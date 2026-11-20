"""Start the stirrer from rest with the vial on a spacer, filmed by camera 1 (2026-11-05, PR #269).

usage: stir_spacer.py <label> [--roi x,y,w,h] <rpm> <seconds> [<rpm> <seconds> ...]

11-04's stir_video.py with two changes: a step with rpm 0 stops the fan (30,0) and keeps
reading 31 for <seconds>, so one sequence can start the fan from rest several times; and
camera 1's crop is set for where it looks today (from above, at the compact stirrer);
--roi overrides it, since the camera rides on the gantry head and was moved by hand
between runs.

Runs on the CubXL Pi, with the CubOS venv (for PawduinoLink). It starts rpicam-vid on
camera 1 (30 fps MJPEG, with a timestamp per frame), films 4 s with the fan at rest, then
runs the steps on one connection (opening the port resets the Uno). A step with rpm > 0
sends 30,<rpm>,<seconds + 15> and reads 31 every second for <seconds>; the extra 15 s is a
safety timer, so that if this script dies the fan still stops by itself. At the end: 30,0,
8 s of coasting on camera, and the camera stops.

A file named STOP in the working directory ends the sequence early (30,0 at once).
Writes <label>.mjpeg, <label>_pts.txt (ms per frame, from rpicam-vid), <label>.jsonl
(every status reply, with UTC), and <label>_camera.json (UTC of the first frame).
"""
import json, signal, subprocess, sys, threading, time
from datetime import datetime, timezone
from pathlib import Path
from cubos.instruments.controllers.pawduino import PawduinoLink

PORT = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00"
CAMERA = ["rpicam-vid", "--camera", "1", "-t", "0", "-n", "--verbose", "0",
          "--mode", "2304:1296:10:P", "--roi", "0.5425,0.494,0.3255,0.3935",
          "--width", "864", "--height", "592", "--framerate", "30",
          "--shutter", "20000", "--codec", "mjpeg", "-q", "75",
          "--autofocus-mode", "manual", "--lens-position", "1.16"]

label, args = sys.argv[1], sys.argv[2:]
if args[:1] == ["--roi"]:
    CAMERA[CAMERA.index("--roi") + 1] = args[1]
    args = args[2:]
rest = [int(a) for a in args]
steps = list(zip(rest[0::2], rest[1::2]))
utc = lambda: datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-4] + "Z"
out = open(f"{label}.jsonl", "a")
video = Path(f"{label}.mjpeg")
stop_file = Path("STOP")


def log(rec):
    rec = {"utc": utc(), **rec}
    out.write(json.dumps(rec) + "\n")
    out.flush()


def first_frame_time(cam):
    """UTC at which the first bytes of video reach the file, about frame 0's time."""
    while cam.poll() is None:
        if video.exists() and video.stat().st_size > 0:
            t = utc()
            Path(f"{label}_camera.json").write_text(json.dumps(
                {"first_bytes_utc": t, "cmd": CAMERA + ["--save-pts", f"{label}_pts.txt"]}))
            print(t, "camera: first frame", flush=True)
            return
        time.sleep(0.01)


def status(rpm_cmd, t0):
    s = link.send_command(31, timeout=5)
    t = time.monotonic() - t0
    rec = {"t": round(t, 2), "rpm_cmd": rpm_cmd, "reply": s}
    try:
        rec.update(json.loads(s.split(":", 1)[1]))
    except Exception:
        pass
    log(rec)
    print(f"{utc()} {t:6.1f} s  {s}", flush=True)


cam = subprocess.Popen(CAMERA + ["--save-pts", f"{label}_pts.txt", "-o", str(video)],
                       stdout=subprocess.DEVNULL, stderr=open(f"{label}_camera.err", "w"))
threading.Thread(target=first_frame_time, args=(cam,), daemon=True).start()
print(utc(), "camera started, filming the fan at rest", flush=True)
time.sleep(4.0)

link = PawduinoLink.acquire(PORT, 115200)
link.connect()
print(utc(), "connected (the Uno reset)", flush=True)
t_start = time.monotonic()
try:
    log({"event": "before", "reply": link.send_command(31, timeout=5)})
    for rpm, secs in steps:
        if stop_file.exists():
            break
        if rpm > 0:
            cmd = (30, rpm, secs + 15)
            r = link.send_command(*cmd, timeout=5)
        else:
            cmd = (30, 0)
            r = link.send_command(*cmd, timeout=5)
        t0 = time.monotonic()
        c = ",".join(str(x) for x in cmd)
        print(f"{utc()} step: {c} -> {r}", flush=True)
        log({"event": "step" if rpm > 0 else "coast", "cmd": c, "reply": r,
             "t_seq": round(t0 - t_start, 2)})
        while time.monotonic() - t0 < secs - 0.5 and not stop_file.exists():
            time.sleep(1.0)
            status(rpm, t0)
    if stop_file.exists():
        print(utc(), "STOP file found, stopping early", flush=True)
        log({"event": "stop_file"})
finally:
    r = link.send_command(30, 0, timeout=5)
    t0 = time.monotonic()
    print(utc(), "stop: 30,0 ->", r, flush=True)
    log({"event": "stop", "reply": r})
    try:
        while time.monotonic() - t0 < 8.0:
            time.sleep(1.0)
            status(0, t0)
    finally:
        link.disconnect()
        cam.send_signal(signal.SIGINT)
        try:
            cam.wait(10)
        except subprocess.TimeoutExpired:
            cam.kill()
        print(utc(), f"camera stopped, {video.stat().st_size / 1e6:.1f} MB", flush=True)
