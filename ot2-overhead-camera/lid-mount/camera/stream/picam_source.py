#!/usr/bin/env python3
"""One camera, two uses: frames for the live stream, and full-resolution stills while it runs.

Option A of borysgroup/streamingLambda#9, which ran 8 h live to YouTube on a Pi Zero 2 W stream
cam with 0 restarts and 95/95 stills (borysgroup/streamingLambda PR #10), adapted to the OT-2 lid
camera's Pi 5 and HQ Camera. A camera belongs to one process at a time, so `rpicam-still` can't
run beside `rpicam-vid`; one picamera2 process can serve both, because the ISP makes two outputs
from every sensor readout:

    main   4056 x 3040 YUV420, the whole sensor at full resolution, kept for stills
    lores  the stream's size (1920 x 1440), written to stdout for ffmpeg, every frame

A Pi 5 has no hardware H.264 encoder, so where option A used picamera2's H264Encoder, this
writes raw YUV420 frames, tightly packed: what `rpicam-vid --codec yuv420` gives device.py,
minus the row padding. ffmpeg does the one encode, as before.

Stills and the camera's state are served over HTTP on 127.0.0.1 only (the tailnet grant to this
Pi is tcp:22), so from another machine go through SSH:

    ssh <pi> 'curl -s localhost:8081/still' > still.jpg     # 4056 x 3040 JPEG, with EXIF
    ssh <pi> 'curl -s localhost:8081/status'                # frame rate, exposure, focus scores

The focus score is the mean gradient over a patch of the full-resolution picture, relative to
its brightness, so it hardly moves with exposure; it peaks when the patch is sharpest. It is
worked out for every frame on a 3 x 3 grid of patches, and with --overlay-file the centre
patch's score is written once a frame for ffmpeg's drawtext to show on the stream.

device.py runs this in place of rpicam-vid when my_secrets.py has CAMERA_SOURCE = "picamera2",
under the system python3, which has picamera2 (device.py's venv doesn't). By hand, off-air:

    python3 picam_source.py --size 1920x1440 --framerate 3 > /dev/null
"""
from __future__ import annotations

import argparse
import io
import json
import os
import queue
import signal
import sys
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import numpy as np
from libcamera import ColorSpace, Transform
from picamera2 import MappedArray, Picamera2

# Metadata worth keeping with a still (the rest is ISP detail).
META_KEYS = ("SensorTimestamp", "ExposureTime", "AnalogueGain", "DigitalGain", "ColourGains",
             "ColourTemperature", "Lux", "FrameDuration", "ScalerCrop", "SensorTemperature")
GRID = 3            # focus patches per side
PATCH = (512, 384)  # focus patch, full-resolution pixels (w, h)
BEST_WINDOW = 120   # s over which the overlay's "best" runs


def size(text: str, sep: str = "x") -> tuple[int, int]:
    w, h = (int(v) for v in text.lower().split(sep))
    return w, h


def packed_yuv420(buf: np.ndarray, w: int, h: int, stride: int) -> np.ndarray:
    """I420 with no row padding, from a buffer whose luma rows are `stride` bytes."""
    if stride == w:
        return buf[: w * h * 3 // 2]
    cs, ch = stride // 2, h // 2
    y = buf[: stride * h].reshape(h, stride)[:, :w]
    u = buf[stride * h: stride * h + cs * ch].reshape(ch, cs)[:, : w // 2]
    v = buf[stride * h + cs * ch: stride * h + 2 * cs * ch].reshape(ch, cs)[:, : w // 2]
    return np.concatenate([y.ravel(), u.ravel(), v.ravel()])


def focus_grid(y: np.ndarray) -> list[list[float]]:
    """Focus score of a PATCH-sized area at the centre of each GRID x GRID cell of the luma plane:
    1000 x RMS gradient between neighbouring pixels / mean level."""
    h, w = y.shape
    pw, ph = PATCH
    out = []
    for r in range(GRID):
        row = []
        for c in range(GRID):
            cx, cy = (2 * c + 1) * w // (2 * GRID), (2 * r + 1) * h // (2 * GRID)
            p = y[cy - ph // 2: cy + ph // 2, cx - pw // 2: cx + pw // 2].astype(np.float32)
            gx, gy = np.diff(p, axis=1), np.diff(p, axis=0)
            g = np.sqrt((np.mean(gx * gx) + np.mean(gy * gy)) / 2)
            row.append(round(float(1000 * g / max(float(p.mean()), 1.0)), 1))
        out.append(row)
    return out


def slim(meta: dict) -> dict:
    return {k: meta[k] for k in META_KEYS if k in meta}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--size", default="1920x1440", help="stream frames, WIDTHxHEIGHT")
    ap.add_argument("--still-size", default=None, help="stills, WIDTHxHEIGHT; default the sensor mode's")
    ap.add_argument("--sensor-mode", default="4056:3040", help="WIDTH:HEIGHT, as rpicam-vid --mode")
    ap.add_argument("--framerate", type=float, default=3)
    ap.add_argument("--hflip", action="store_true")
    ap.add_argument("--vflip", action="store_true")
    ap.add_argument("--port", type=int, default=8081)
    ap.add_argument("--quality", type=int, default=93, help="JPEG quality of stills")
    ap.add_argument("--overlay-file", help="write the centre focus score here once a frame")
    args = ap.parse_args()

    # Frames go to the original stdout and nothing else does: our prints, picamera2's warnings
    # and libcamera's log all go to stderr (the journal). One stray line in the pipe would shift
    # every raw frame after it (see README, "What changed in device.py").
    frames_out = os.fdopen(os.dup(1), "wb")
    os.dup2(2, 1)
    sys.stdout = sys.stderr

    w, h = size(args.size)
    sensor = size(args.sensor_mode, ":")
    still = size(args.still_size) if args.still_size else sensor

    stop = threading.Event()

    def on_term(signum, frame):
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, on_term)

    picam2 = Picamera2()
    picam2.options["quality"] = args.quality
    config = picam2.create_video_configuration(
        main={"size": still, "format": "YUV420"},
        lores={"size": (w, h), "format": "YUV420"},
        sensor={"output_size": sensor},
        transform=Transform(hflip=args.hflip, vflip=args.vflip),
        # rpicam-vid's YUV420 is full-range sYCC, which device.py converts for the stream; the
        # same here. (picamera2's video default would be limited-range Rec.709.) JPEG wants sYCC too.
        colour_space=ColorSpace.Sycc(),
        controls={"FrameRate": args.framerate},
        buffer_count=4,
    )
    picam2.configure(config)
    actual = picam2.camera_configuration()
    stride = actual["lores"]["stride"]
    print(f"picam_source: main {actual['main']['size']}, lores {actual['lores']['size']} "
          f"(stride {stride}), sensor {actual['sensor']}, {args.framerate} fps", flush=True)

    state = {"started": time.time(), "frames": 0, "dropped": 0, "stills": 0, "last_still": None,
             "focus": None, "meta": {}}
    stamps: deque[float] = deque(maxlen=30)
    best: deque[tuple[float, float]] = deque()
    lock = threading.Lock()

    # Frames are handed to a writer thread, so that a stalled upload (ffmpeg blocked on the
    # network) holds up only the stream, never the camera or the stills. If it falls more than
    # three frames behind, the oldest are dropped.
    frames: queue.Queue = queue.Queue(maxsize=3)

    def writer():
        while True:
            frame = frames.get()
            if frame is None:
                return
            try:
                frames_out.write(memoryview(frame))
                frames_out.flush()
            except (BrokenPipeError, ValueError, OSError):
                print("picam_source: the frame pipe closed; stopping", flush=True)
                stop.set()
                return

    stills: queue.Queue = queue.Queue()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *a):
            pass

        def reply(self, code, body: bytes, ctype: str, headers: dict | None = None):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            for k, v in (headers or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlparse(self.path).path
            if path in ("/still", "/still.jpg"):
                job = {"done": threading.Event()}
                stills.put(job)
                if not job["done"].wait(15):
                    self.reply(504, b"no frame within 15 s\n", "text/plain")
                    return
                self.reply(200, job["jpeg"], "image/jpeg",
                           {"X-Still-Metadata": json.dumps(job["meta"], default=str)})
            elif path == "/status":
                with lock:
                    s = dict(state)
                    fps = (len(stamps) - 1) / (stamps[-1] - stamps[0]) if len(stamps) > 1 else 0.0
                    s["fps"] = round(fps, 2)
                    s["last_frame_age_s"] = round(time.time() - stamps[-1], 2) if stamps else None
                s.update(size=[w, h], still_size=list(still), sensor_mode=list(sensor),
                         focus_grid=f"{GRID}x{GRID} patches of {PATCH[0]}x{PATCH[1]} full-resolution px")
                self.reply(200, (json.dumps(s, default=str, indent=1) + "\n").encode(), "application/json")
            else:
                self.reply(404, b"try /still or /status\n", "text/plain")

    def serve():
        for attempt in range(10):
            try:
                server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
                break
            except OSError as e:  # the previous run's socket, still closing
                print(f"picam_source: port {args.port}: {e}; retrying", flush=True)
                time.sleep(2)
        else:
            print("picam_source: no stills this run; the stream carries on", flush=True)
            return
        server.daemon_threads = True
        server.serve_forever()

    threading.Thread(target=writer, daemon=True).start()
    threading.Thread(target=serve, daemon=True).start()

    picam2.start()
    try:
        while not stop.is_set():
            try:
                request = picam2.capture_request(wait=10)
            except TimeoutError:
                print("picam_source: no frame from the camera for 10 s; exiting", flush=True)
                return 1
            try:
                frame = packed_yuv420(request.make_buffer("lores"), w, h, stride)
                try:
                    frames.put_nowait(frame)
                except queue.Full:
                    frames.get_nowait()
                    frames.put_nowait(frame)
                    with lock:
                        state["dropped"] += 1
                meta = request.get_metadata()
                with MappedArray(request, "main") as m:
                    grid = focus_grid(m.array[: still[1], : still[0]])
                if not stills.empty():
                    buf = io.BytesIO()
                    request.save("main", buf, format="jpeg")  # simplejpeg from YUV420, with EXIF
                    jpeg = buf.getvalue()
                    while not stills.empty():
                        job = stills.get_nowait()
                        job.update(jpeg=jpeg, meta=slim(meta))
                        job["done"].set()
                    with lock:
                        state["stills"] += 1
                        state["last_still"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            finally:
                request.release()

            now = time.time()
            centre = grid[GRID // 2][GRID // 2]
            best.append((now, centre))
            while best and best[0][0] < now - BEST_WINDOW:
                best.popleft()
            with lock:
                state["frames"] += 1
                state["focus"] = {"centre": centre, "best_2min": max(v for _, v in best), "grid": grid}
                state["meta"] = slim(meta)
                stamps.append(now)
            if args.overlay_file:
                tmp = args.overlay_file + ".tmp"
                with open(tmp, "w") as f:
                    f.write(f"focus {centre:.0f}  (best {state['focus']['best_2min']:.0f} in 2 min)")
                os.replace(tmp, args.overlay_file)
        return 1  # the pipe closed
    finally:
        try:
            frames.put_nowait(None)
        except queue.Full:  # the writer is stuck on the pipe; it's a daemon thread, so let it go
            pass
        picam2.stop()
        picam2.close()


if __name__ == "__main__":
    sys.exit(main())
