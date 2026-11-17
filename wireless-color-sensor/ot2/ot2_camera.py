#!/usr/bin/env python3
"""Full-resolution (1920x1080) pictures from the OT-2's own camera.

Written for byu-vcl#349 (2026-11-17). The robot server's ``POST /camera/picture`` always asks
ffmpeg for 640x480. The camera itself (``H264 USB Camera``, USB ``32e4:9422``, ``/dev/video0``
on the robot's Raspberry Pi 3) does MJPEG up to 1920x1080, so this runs ffmpeg on the robot
through the robot's own Jupyter Notebook server (port 48888, no password as shipped) and copies
the camera's JPEGs back without re-encoding them. It only reads the camera; nothing moves.

Both ports are reached through an SSH port-forward from the runner, through the Pi that holds
the robot's cable (see CLAUDE.md, "Reaching the OT-2"):

    ssh -f -N -o ExitOnForwardFailure=yes \
        -L 31950:169.254.51.252:31950 -L 48888:169.254.51.252:48888 "$USER@$PI"

    ot2_camera.py shoot NAME [N]     average of N frames -> shots/NAME.png (+ the frames)
    ot2_camera.py shift A B x0,y0,x1,y1 [bx0,by0,bx1,by1]
                                     sub-pixel shift of a box from shot A to shot B, minus the
                                     shift of an optional static background box
    ot2_camera.py done               delete the frames on the robot and the Jupyter kernel

Needs ``requests``, ``websocket-client``, ``numpy`` and ``opencv-python-headless``.
Frames are ~150 kB each; MAX_RATE throttles the copy so a Pi on Wi-Fi is not swamped.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import uuid

import requests
import websocket

JUP = os.environ.get("OT2_JUPYTER", "http://127.0.0.1:48888")
SHOTS = os.environ.get("OT2_SHOTS", "/tmp/ot2cam/shots")
STATE = os.environ.get("OT2_CAM_STATE", "/tmp/ot2cam/state.json")
CAMDIR = "vcl-cam-tmp"                      # under the Jupyter root; removed by `done`
ROOT = "/var/lib/jupyter/notebooks"         # the server's root; the kernel's cwd is "/" (read-only)
SKIP = 60                                   # frames for auto-exposure to settle
MAX_RATE = 1.0e6                            # bytes/s when copying frames off the robot

GRAB = r'''
import subprocess, glob, os, time
d = os.path.join(%(root)r, %(camdir)r)
os.makedirs(d, exist_ok=True)
for f in glob.glob(d + "/*.jpg"):
    os.remove(f)
t = time.time()
r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "video4linux2",
                    "-input_format", "mjpeg", "-video_size", "1920x1080", "-i", "/dev/video0",
                    "-c:v", "copy", "-bsf:v", "mjpeg2jpeg", "-frames:v", "%(total)d", "-f", "image2",
                    d + "/f%%03d.jpg"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                   universal_newlines=True)
fs = sorted(glob.glob(d + "/*.jpg"))
for f in fs[:%(skip)d]:
    os.remove(f)
print(r.stdout[-300:])
print("FILES", " ".join(os.path.basename(f) for f in fs[%(skip)d:]), "took %%.1f" %% (time.time() - t))
'''

CLEAN = r'''
import glob, os
d = os.path.join(%(root)r, %(camdir)r)
for f in glob.glob(d + "/*"):
    os.remove(f)
if os.path.isdir(d):
    os.rmdir(d)
print("cleaned", not os.path.exists(d))
'''


def _state() -> dict:
    try:
        return json.load(open(STATE))
    except FileNotFoundError:
        return {}


def _save(st: dict) -> None:
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(st, open(STATE, "w"))


def _kernel() -> str:
    kid = _state().get("kernel")
    if kid and requests.get(f"{JUP}/api/kernels/{kid}", timeout=20).status_code == 200:
        return kid
    kid = requests.post(f"{JUP}/api/kernels", json={"name": "python3"}, timeout=60).json()["id"]
    st = _state()
    st["kernel"] = kid
    _save(st)
    return kid


def kexec(code: str, timeout: float = 120) -> str:
    """Run code in a kernel on the robot; return its stdout/stderr."""
    kid = _kernel()
    host = JUP.split("://", 1)[1]
    ws = websocket.create_connection(f"ws://{host}/api/kernels/{kid}/channels", timeout=timeout)
    mid = uuid.uuid4().hex
    ws.send(json.dumps({"header": {"msg_id": mid, "username": "vcl", "session": uuid.uuid4().hex,
                                   "msg_type": "execute_request", "version": "5.3"},
                        "parent_header": {}, "metadata": {}, "channel": "shell",
                        "content": {"code": code, "silent": False, "store_history": False,
                                    "user_expressions": {}, "allow_stdin": False,
                                    "stop_on_error": True}}))
    out = []
    while True:
        m = json.loads(ws.recv())
        if m.get("parent_header", {}).get("msg_id") != mid:
            continue
        if m["msg_type"] == "stream":
            out.append(m["content"]["text"])
        elif m["msg_type"] == "error":
            out.append("ERROR: %s %s" % (m["content"]["ename"], m["content"]["evalue"]))
        elif m["msg_type"] == "status" and m["content"]["execution_state"] == "idle":
            break
    ws.close()
    return "".join(out)


def shoot(name: str, n: int = 5, skip: int = SKIP) -> str:
    """Grab n frames after `skip`; save them and their mean under SHOTS. Returns the mean's path."""
    import cv2
    import numpy as np
    os.makedirs(SHOTS, exist_ok=True)
    out = kexec(GRAB % {"root": ROOT, "camdir": CAMDIR, "total": n + skip, "skip": skip})
    m = re.search(r"FILES (.*?) took", out)
    if not m:
        raise RuntimeError("grab failed: " + out[-500:])
    imgs = []
    for i, f in enumerate(m.group(1).split()):
        t0 = time.time()
        r = requests.get(f"{JUP}/files/{CAMDIR}/{f}", timeout=60)
        r.raise_for_status()
        p = f"{SHOTS}/{name}_{i}.jpg"
        open(p, "wb").write(r.content)
        imgs.append(cv2.imread(p).astype(np.float32))
        time.sleep(max(0.0, len(r.content) / MAX_RATE - (time.time() - t0)))
    mean = np.clip(np.mean(imgs, axis=0), 0, 255).astype(np.uint8)
    path = f"{SHOTS}/{name}.png"
    cv2.imwrite(path, mean)
    kexec(CLEAN % {"root": ROOT, "camdir": CAMDIR})
    return path


def done() -> None:
    try:
        print(kexec(CLEAN % {"root": ROOT, "camdir": CAMDIR}).strip())
    finally:
        st = _state()
        kid = st.pop("kernel", None)
        if kid:
            requests.delete(f"{JUP}/api/kernels/{kid}", timeout=30)
        _save(st)
        print("kernel deleted:", kid)


# ------------------------------------------------------------------ measuring
def _gray(name: str):
    import cv2
    import numpy as np
    im = cv2.imread(f"{SHOTS}/{name}.png", cv2.IMREAD_GRAYSCALE)
    if im is None:
        raise FileNotFoundError(name)
    return im.astype(np.float32)


def _match(ref, img, box, search=12, up=4):
    import cv2
    x0, y0, x1, y1 = box
    t = cv2.resize(ref[y0:y1, x0:x1], None, fx=up, fy=up, interpolation=cv2.INTER_CUBIC)
    s = cv2.resize(img[y0 - search:y1 + search, x0 - search:x1 + search], None, fx=up, fy=up,
                   interpolation=cv2.INTER_CUBIC)
    r = cv2.matchTemplate(s, t, cv2.TM_CCOEFF_NORMED)
    _, score, _, (x, y) = cv2.minMaxLoc(r)
    dx = dy = 0.0
    if 0 < x < r.shape[1] - 1:
        a, b, c = r[y, x - 1], r[y, x], r[y, x + 1]
        dx = 0.5 * (a - c) / (a - 2 * b + c) if a - 2 * b + c else 0.0
    if 0 < y < r.shape[0] - 1:
        a, b, c = r[y - 1, x], r[y, x], r[y + 1, x]
        dy = 0.5 * (a - c) / (a - 2 * b + c) if a - 2 * b + c else 0.0
    return (x + dx) / up - search, (y + dy) / up - search, score


def shift(a: str, b: str, box, bg=None):
    """Shift (px) of what's in `box` from shot a to shot b, minus the background's shift.
    Keep the box tight on the moving part: a box that's mostly static background tracks the
    background instead, and reports no motion."""
    ra, rb = _gray(a), _gray(b)
    dx, dy, sc = _match(ra, rb, box)
    bdx = bdy = 0.0
    if bg:
        bdx, bdy, _ = _match(ra, rb, bg, search=6)
    return dx - bdx, dy - bdy, sc


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
    elif a[0] == "shoot":
        print(shoot(a[1], int(a[2]) if len(a) > 2 else 5))
    elif a[0] == "shift":
        box = tuple(int(v) for v in a[3].split(","))
        bg = tuple(int(v) for v in a[4].split(",")) if len(a) > 4 else None
        print("dx %.2f dy %.2f score %.3f" % shift(a[1], a[2], box, bg))
    elif a[0] == "done":
        done()
