"""burst.py: a still from both ribbon cameras every 10 s for 1 minute.

Runs on the CubXL Pi: ssh <pi> 'python3 -I -' < burst.py
Seven ticks, at 0, 10, ... 60 s. At each tick both cameras capture in
parallel with rpicam-still, so each pair is taken within about a second of
each other. Camera 0 is CAM/DISP 0, camera 1 is CAM/DISP 1. If camera 0 is
busy because someone has the deckcam live view open (deckcam uses camera 0),
its picture comes from deckcam's /snapshot.jpg instead, so the viewer is not
interrupted.
"""
import datetime
import os
import subprocess
import time
import urllib.request

OUT = "/tmp/burst_20261007"
TICKS, PERIOD = 7, 10.0
ENV = dict(os.environ, LIBCAMERA_LOG_LEVELS="*:ERROR")


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S.%f")[:-4] + "Z"


def log(msg):
    print(msg, flush=True)
    with open(f"{OUT}/burst.log", "a") as fh:
        fh.write(msg + "\n")


os.makedirs(OUT, exist_ok=True)
busy = subprocess.run(["pgrep", "-a", "rpicam"], capture_output=True, text=True).stdout.strip()
log(f"rpicam processes before start: {busy or 'none'}")
start = time.time() + 1
for k in range(TICKS):
    while time.time() < start + PERIOD * k:
        time.sleep(0.02)
    log(f"tick {k} start {stamp()}")
    pending = {}
    for idx in (0, 1):
        f = f"{OUT}/{k:02d}_t{int(PERIOD * k):02d}s__cam{idx}_csi{idx}.jpg"
        pending[idx] = (f, subprocess.Popen(
            ["timeout", "9", "rpicam-still", "--camera", str(idx), "-n", "-t", "2500",
             "--width", "2304", "--height", "1296", "--metadata", f[:-4] + ".json", "-o", f],
            stdout=subprocess.DEVNULL, stderr=open(f[:-4] + ".err", "w"), env=ENV))
    while pending:
        for idx, (f, p) in list(pending.items()):
            rc = p.poll()
            if rc is None:
                continue
            del pending[idx]
            if rc == 0:
                log(f"tick {k} cam{idx} ok {stamp()} {os.path.getsize(f)} bytes")
                continue
            err = open(f[:-4] + ".err").read().strip().splitlines()[-2:]
            log(f"tick {k} cam{idx} FAILED rc={rc} {stamp()}: {' | '.join(err)}")
            if idx == 0:
                try:
                    with urllib.request.urlopen("http://127.0.0.1:8743/snapshot.jpg", timeout=5) as r:
                        data = r.read()
                    with open(f, "wb") as fh:
                        fh.write(data)
                    log(f"tick {k} cam0 via deckcam snapshot {stamp()} {len(data)} bytes")
                except Exception as e:
                    log(f"tick {k} cam0 deckcam snapshot failed: {e}")
        time.sleep(0.02)
log(f"done {stamp()}")
