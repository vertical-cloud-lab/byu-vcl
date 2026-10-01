#!/usr/bin/env python3
"""Live view of the CubXL's overhead deck camera, in a browser, over SSH.

Serves an MJPEG stream from the Pi's ribbon-cable camera on 127.0.0.1 only, so
the way to watch it is the same SSH tunnel as the CubOS Operator UI::

    # on the Pi (or let deckcam.service run it)
    python3 deckcam.py

    # on your laptop, then open http://localhost:8743
    ssh -N -L 8743:127.0.0.1:8743 <pi-user>@<pi-host>

Endpoints: ``/`` viewer page (crosshair and grid overlay, for aiming the camera),
``/stream.mjpg`` the raw stream, ``/snapshot.jpg`` one frame, ``/status`` JSON.

``rpicam-vid`` runs only while someone is watching, and stops ``--idle`` seconds
after the last viewer leaves. Only one process can hold the camera at a time,
so this keeps it free for ``rpicam-still`` and other captures the rest of the
time. Equally, while the stream is up, those captures fail with "pipeline
handler in use"; close the page (or ``systemctl stop deckcam``) first.

The sensor mode is pinned with ``--mode`` on purpose. Asked for 1280x720 with no
mode, rpicam-vid picks the IMX708's 1536x864 mode, which is a centre crop of
the sensor: the stream then shows only the middle two thirds of what the
camera actually sees, which is exactly wrong for deciding where to put it.
2304:1296 is the full field of view, 2x2 binned (checked 2026-10-01).

Standard library only, plus ``rpicam-vid`` from rpicam-apps, which Raspberry
Pi OS already ships.
"""

from __future__ import annotations

import argparse
import http.server
import json
import logging
import os
import select
import signal
import subprocess
import threading
import time
from collections import deque

log = logging.getLogger("deckcam")

SOI = b"\xff\xd8"
EOI = b"\xff\xd9"
BOUNDARY = "deckcamframe"

PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>CubXL deck camera</title>
<style>
  html, body { margin: 0; height: 100%; background: #111; color: #ddd;
               font: 13px system-ui, sans-serif; }
  #bar { padding: 6px 10px; display: flex; gap: 14px; align-items: center; }
  #bar a { color: #9cf; }
  #wrap { position: relative; height: calc(100% - 34px); }
  #view, #overlay { position: absolute; inset: 0; width: 100%; height: 100%; }
  #view { object-fit: contain; }
  .flip { transform: rotate(180deg); }
</style></head>
<body>
<div id="bar">
  <b>CubXL deck camera</b>
  <label><input type="checkbox" id="cross" checked> crosshair (c)</label>
  <label><input type="checkbox" id="grid" checked> thirds grid (g)</label>
  <label><input type="checkbox" id="rot"> rotate 180&deg; (r)</label>
  <a href="/snapshot.jpg" target="_blank">snapshot</a>
  <span id="status">connecting&hellip;</span>
</div>
<div id="wrap">
  <img id="view" src="/stream.mjpg" alt="deck camera">
  <svg id="overlay" preserveAspectRatio="none"></svg>
</div>
<script>
const img = document.getElementById("view"), svg = document.getElementById("overlay");
const boxes = { c: "cross", g: "grid", r: "rot" };
function draw() {
  // Draw over the image itself, not the letterbox around it.
  const W = svg.clientWidth, H = svg.clientHeight;
  const iw = img.naturalWidth || 16, ih = img.naturalHeight || 9;
  const s = Math.min(W / iw, H / ih), w = iw * s, h = ih * s;
  const x0 = (W - w) / 2, y0 = (H - h) / 2;
  const line = (x1, y1, x2, y2, c) =>
    `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${c}" stroke-width="1.5"/>`;
  let out = "";
  if (document.getElementById("grid").checked)
    for (const f of [1 / 3, 2 / 3])
      out += line(x0 + w * f, y0, x0 + w * f, y0 + h, "#ff0a") +
             line(x0, y0 + h * f, x0 + w, y0 + h * f, "#ff0a");
  if (document.getElementById("cross").checked)
    out += line(x0 + w / 2, y0, x0 + w / 2, y0 + h, "#f33") +
           line(x0, y0 + h / 2, x0 + w, y0 + h / 2, "#f33");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.innerHTML = out;
  const flip = document.getElementById("rot").checked;
  img.classList.toggle("flip", flip);
  svg.classList.toggle("flip", flip);
}
for (const id of Object.values(boxes)) document.getElementById(id).onchange = draw;
document.onkeydown = e => {
  const id = boxes[e.key];
  if (id) { const b = document.getElementById(id); b.checked = !b.checked; draw(); }
};
img.onload = draw;
window.onresize = draw;
let orphaned = 0;
async function poll() {
  try {
    const s = await (await fetch("/status")).json();
    document.getElementById("status").textContent = s.last_error
      ? "camera error: " + s.last_error
      : `${s.width}x${s.height}, ${s.fps.toFixed(1)} fps, ${s.viewers} viewer(s)`;
    // The server ends a stream that has gone 10 s without frames; reopen it.
    orphaned = s.viewers === 0 ? orphaned + 1 : 0;
    if (orphaned >= 2 && document.visibilityState === "visible") {
      img.src = "/stream.mjpg?" + Date.now();
      orphaned = 0;
    }
  } catch (e) {
    document.getElementById("status").textContent = "server unreachable (is the SSH tunnel still open?)";
  }
}
setInterval(poll, 2000);
poll();
draw();
</script>
</body></html>
"""


class Camera:
    """Owns the rpicam-vid process: started for the first viewer, stopped after the last."""

    def __init__(self, cmd, idle_s=10.0, warmup_s=2.0):
        self.cmd = cmd
        self.idle_s = idle_s
        self.warmup_s = warmup_s
        self.cond = threading.Condition()
        self.frame = None
        self.frame_time = 0.0
        self.seq = 0
        self.viewers = 0
        self.wanted_until = 0.0
        self.started_at = float("inf")
        self.running = False
        self.closing = False
        self.proc = None
        self.last_error = None
        self.frame_times = deque(maxlen=30)
        threading.Thread(target=self._supervise, name="camera", daemon=True).start()

    # -- demand ---------------------------------------------------------------

    def _wanted(self):
        if self.closing:
            return False
        return self.viewers > 0 or time.monotonic() < self.wanted_until

    def acquire(self):
        """Register a viewer; returns the ``seq`` to pass to ``next_frame``.

        A frame left over from an earlier session is not served as live: a new
        viewer waits for a fresh one unless the camera is already running.
        """
        with self.cond:
            self.viewers += 1
            self.cond.notify_all()
            return self.seq - 1 if self.running and self.frame is not None else self.seq

    def release(self):
        with self.cond:
            self.viewers -= 1
            self.wanted_until = time.monotonic() + self.idle_s

    def next_frame(self, after_seq, timeout=10.0):
        """Block until a frame newer than ``after_seq`` arrives; (None, seq) on timeout."""
        deadline = time.monotonic() + timeout
        with self.cond:
            while self.seq == after_seq:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return None, after_seq
                self.cond.wait(remaining)
            return self.frame, self.seq

    def snapshot(self, timeout=15.0):
        """A current frame, starting the camera and letting exposure settle if needed."""
        deadline = time.monotonic() + timeout
        with self.cond:
            asked = time.monotonic()
            self.wanted_until = max(self.wanted_until, asked + self.idle_s)
            self.cond.notify_all()
            while not (self.frame is not None
                       and self.frame_time >= asked - 0.5
                       and self.frame_time >= self.started_at + self.warmup_s):
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return None
                self.cond.wait(remaining)
            return self.frame

    def status(self):
        with self.cond:
            t = list(self.frame_times)
            fps = (len(t) - 1) / (t[-1] - t[0]) if len(t) > 1 and t[-1] > t[0] else 0.0
            if not self.running or time.monotonic() - self.frame_time > 3:
                fps = 0.0
            return {"running": self.running, "viewers": self.viewers,
                    "fps": round(fps, 1), "last_error": self.last_error}

    def close(self):
        """Stop the camera for good (server shutdown)."""
        with self.cond:
            self.closing = True
            proc = self.proc
            self.cond.notify_all()
        if proc is not None:
            _stop(proc)

    # -- process --------------------------------------------------------------

    def _supervise(self):
        while True:
            with self.cond:
                while not self._wanted():
                    self.cond.wait(1.0)
            ok = self._run_once()
            if not ok:
                time.sleep(3)  # e.g. camera busy: back off instead of spinning

    def _run_once(self):
        log.info("starting: %s", " ".join(self.cmd))
        env = dict(os.environ, LIBCAMERA_LOG_LEVELS="*:ERROR")
        proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env=env)
        errors = deque(maxlen=5)
        reader = threading.Thread(target=self._drain_stderr, args=(proc, errors),
                                  daemon=True)
        reader.start()
        with self.cond:
            self.proc = proc
            self.running = True
            self.started_at = time.monotonic()
            self.frame_times.clear()
        fd = proc.stdout.fileno()
        buf = bytearray()
        got_frame = False
        try:
            while True:
                with self.cond:
                    if not self._wanted():
                        log.info("no viewers for %.0f s, stopping camera", self.idle_s)
                        return True
                ready, _, _ = select.select([fd], [], [], 1.0)
                if not ready:
                    continue
                chunk = os.read(fd, 1 << 16)
                if not chunk:
                    break  # rpicam-vid exited
                buf += chunk
                for jpeg in _split_frames(buf):
                    got_frame = True
                    self._publish(jpeg)
                if len(buf) > 8 << 20:  # no frame boundary in 8 MB: resynchronise
                    buf.clear()
        finally:
            _stop(proc)
            with self.cond:
                self.proc = None
                self.running = False
                self.started_at = float("inf")
                self.cond.notify_all()
        reader.join(2)
        if self.closing:
            return True
        message = "; ".join(errors) or f"rpicam-vid exited with status {proc.returncode}"
        if "failed to acquire camera" in message:
            message = ("camera busy: another program has it open "
                       "(rpicam-still, rpicam-hello, a second deckcam?)")
        log.warning("camera stopped unexpectedly: %s", message)
        with self.cond:
            self.last_error = message
        return got_frame

    def _drain_stderr(self, proc, errors):
        for raw in proc.stderr:
            line = raw.decode(errors="replace").strip()
            if line:
                errors.append(line)
                log.debug("rpicam-vid: %s", line)

    def _publish(self, jpeg):
        with self.cond:
            self.frame = jpeg
            self.frame_time = time.monotonic()
            self.frame_times.append(self.frame_time)
            self.seq += 1
            self.last_error = None
            self.cond.notify_all()


def _stop(proc):
    """SIGINT lets rpicam-vid release the camera cleanly; kill it if it will not go."""
    if proc.poll() is None:
        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


def _split_frames(buf):
    """Yield every complete JPEG in ``buf`` and drop the bytes consumed.

    Entropy-coded JPEG data byte-stuffs 0xFF, so FFD9 only ever appears as the
    end-of-image marker, and rpicam-vid's MJPEG frames carry no embedded
    thumbnail that could contain a second one.
    """
    while True:
        start = buf.find(SOI)
        if start < 0:
            # Keep a trailing 0xFF: it may be the first half of the next SOI.
            del buf[:-1 if buf.endswith(b"\xff") else len(buf)]
            return
        end = buf.find(EOI, start + 2)
        if end < 0:
            del buf[:start]
            return
        yield bytes(buf[start:end + 2])
        del buf[:end + 2]


def make_handler(camera, info):
    class Handler(http.server.BaseHTTPRequestHandler):
        server_version = "deckcam"

        def log_message(self, fmt, *args):
            log.debug("%s %s", self.address_string(), fmt % args)

        def _send(self, code, body, ctype):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path == "/":
                self._send(200, PAGE.encode(), "text/html; charset=utf-8")
            elif path == "/status":
                body = json.dumps({**info, **camera.status()}).encode()
                self._send(200, body, "application/json")
            elif path == "/snapshot.jpg":
                jpeg = camera.snapshot()
                if jpeg is None:
                    msg = camera.status()["last_error"] or "no frame from the camera"
                    self._send(503, msg.encode(), "text/plain; charset=utf-8")
                else:
                    self._send(200, jpeg, "image/jpeg")
            elif path == "/stream.mjpg":
                self._stream()
            else:
                self._send(404, b"not found", "text/plain")

        def _stream(self):
            seq = camera.acquire()
            try:
                self.send_response(200)
                self.send_header("Content-Type",
                                 f"multipart/x-mixed-replace; boundary={BOUNDARY}")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                while True:
                    jpeg, seq = camera.next_frame(seq)
                    if jpeg is None:
                        # Nothing written means a closed tab goes unnoticed and
                        # keeps the camera claimed, so end the response; the
                        # page reconnects by itself.
                        return
                    self.wfile.write(
                        f"--{BOUNDARY}\r\nContent-Type: image/jpeg\r\n"
                        f"Content-Length: {len(jpeg)}\r\n\r\n".encode())
                    self.wfile.write(jpeg)
                    self.wfile.write(b"\r\n")
            except (BrokenPipeError, ConnectionResetError, TimeoutError):
                pass
            finally:
                camera.release()

    return Handler


def build_command(args):
    cmd = ["rpicam-vid", "-t", "0", "-n", "--verbose", "0", "--flush",
           "--codec", "mjpeg", "--mode", args.mode,
           "--width", str(args.width), "--height", str(args.height),
           "--framerate", str(args.fps), "-q", str(args.quality)]
    if args.lens_position is None:
        cmd += ["--autofocus-mode", "continuous"]
    else:
        cmd += ["--autofocus-mode", "manual", "--lens-position", str(args.lens_position)]
    if args.rotate180:
        cmd += ["--rotation", "180"]
    return cmd + ["-o", "-"]


def main(argv=None):
    env = os.environ.get
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--host", default=env("DECKCAM_HOST", "127.0.0.1"),
                   help="bind address; keep it loopback and use an SSH tunnel")
    p.add_argument("--port", type=int, default=int(env("DECKCAM_PORT", "8743")))
    p.add_argument("--width", type=int, default=int(env("DECKCAM_WIDTH", "1280")))
    p.add_argument("--height", type=int, default=int(env("DECKCAM_HEIGHT", "720")))
    p.add_argument("--fps", type=float, default=float(env("DECKCAM_FPS", "10")))
    p.add_argument("--quality", type=int, default=int(env("DECKCAM_QUALITY", "60")),
                   help="JPEG quality; lower it if the Wi-Fi struggles")
    p.add_argument("--mode", default=env("DECKCAM_MODE", "2304:1296:10:P"),
                   help="sensor mode; the default is the IMX708's full field of view")
    p.add_argument("--lens-position", type=float,
                   default=float(env("DECKCAM_LENS_POSITION")) if env("DECKCAM_LENS_POSITION") else None,
                   help="fix focus at this many dioptres (1 / distance in m) "
                        "instead of continuous autofocus")
    p.add_argument("--rotate180", action="store_true",
                   default=env("DECKCAM_ROTATE180", "") not in ("", "0", "false"))
    p.add_argument("--idle", type=float, default=float(env("DECKCAM_IDLE_S", "10")),
                   help="seconds to keep the camera running after the last viewer leaves")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(message)s")
    camera = Camera(build_command(args), idle_s=args.idle)
    info = {"width": args.width, "height": args.height, "mode": args.mode}
    server = http.server.ThreadingHTTPServer((args.host, args.port),
                                             make_handler(camera, info))
    server.daemon_threads = True
    log.info("serving on http://%s:%d", args.host, args.port)
    signal.signal(signal.SIGTERM, lambda *_: threading.Thread(target=server.shutdown).start())
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        camera.close()


if __name__ == "__main__":
    main()
