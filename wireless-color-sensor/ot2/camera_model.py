#!/usr/bin/env python3
"""Measure where the nozzle really is, from the two cameras that watch the OT-2.

Neither camera looks along a deck axis. Both look back and down from the front
left, so a millimetre in X, in Y and in Z each moves the nozzle's image in a
different direction. This fits those three directions (a 2x3 image Jacobian
per camera) from photos of the bare nozzle at known poses, then uses them for
two things on 2026-09-25:

``fit``    solve the Jacobians from ``*_align_x<X>_y<Y>_z<Z>_{live,robot}.jpg``
           photos, as written by ``enclosure_height_cal.py``'s ``align``;
``press``  read how far the nozzle actually went on each ``press_z<Z>`` photo,
           from the row of its shoulder (the step from the wide section to the
           narrow tip), which stays visible above the enclosure while the tip
           is inside it. A press that jams shows up as a shoulder that stops
           moving: the Z motor loses steps without reporting anything, which
           is how the first press into the right-hand socket went unnoticed
           until the photo after the lift.

    python3 camera_model.py fit   PHOTO_DIR [PHOTO_DIR ...] [--out model.json]
    python3 camera_model.py press PHOTO_DIR --x 92.8 --y 316.5 [--model model.json]

The pixel windows below are for the camera poses of 2026-09-25 and the
right-hand socket of the base in slot 10. Move either camera and they, and the
fitted numbers, have to be redone.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re

import numpy as np
from PIL import Image

REF = np.array([92.5, 315.5, 102.0])     # pose the linear model is centred on
LIVE_WINDOW = (470, 580, 0, 120)         # x0, x1, y0, y1 around the socket
ROBOT_WINDOW = (150, 320, 0, 140)
# The nozzle's shoulder in the livestream, at REF's X/Y: row = A + B * (120 - z).
# Fitted on 2026-09-25 from z = 120, 108, 105, 102, 101 (residuals < 0.25 px).
SHOULDER_A, SHOULDER_B = 37.12, 1.726


def pose_from_name(path):
    m = re.search(r"align_x([\d.]+)_y([\d.]+)_z([\d.]+)_", os.path.basename(path))
    return tuple(float(v) for v in m.groups()) if m else None


def tip_live(path):
    """Tip of the nozzle in the livestream: its lowest dark row, centred."""
    x0, x1, y0, y1 = LIVE_WINDOW
    a = np.asarray(Image.open(path).convert("L")).astype(float)[y0:y1, x0:x1]
    dark = a < 70
    rows = np.where(dark.sum(axis=1) >= 3)[0]
    r = rows.max()
    cols = np.where(dark[r - 2:r + 1].any(axis=0))[0]
    return x0 + cols.mean(), y0 + r + 0.5


def tip_robot(path):
    """Tip in the robot camera: the far end of the pipette's dark blob.

    The pipette is the largest dark region touching the top of the window; it
    runs up and to the right in this camera, so its tip is its extreme point
    along (-0.45, 0.9). Taking any dark pixel instead picks up the shadowed
    edge of the base's tower whenever the nozzle is high.
    """
    from scipy import ndimage

    x0, x1, y0, y1 = ROBOT_WINDOW
    a = np.asarray(Image.open(path).convert("L")).astype(float)[y0:y1, x0:x1]
    lab, n = ndimage.label(a < 55)
    best, size = None, 0
    for k in range(1, n + 1):
        m = lab == k
        if m[0].any() and m.sum() > size:
            best, size = m, m.sum()
    ys, xs = np.nonzero(best)
    d = np.array([-0.45, 0.9]) / np.hypot(0.45, 0.9)
    proj = xs * d[0] + ys * d[1]
    k = proj >= proj.max() - 1.5
    return x0 + xs[k].mean(), y0 + ys[k].mean()


def shoulder_row(path, x0=495, x1=555, y0=20, y1=100):
    """Sub-pixel row where the dark band narrows from ~15 px to ~8 px."""
    a = np.asarray(Image.open(path).convert("L")).astype(float)[y0:y1, x0:x1]
    w = np.clip((110 - a) / 70.0, 0, 1).sum(axis=1)
    idx = None
    for r in range(len(w) - 1):
        if w[r] >= 11.0 > w[r + 1]:
            idx = r
    if idx is None:
        return None
    return y0 + idx + (w[idx] - 11.0) / (w[idx] - w[idx + 1])


def fit(dirs):
    rows = []
    for d in dirs:
        for live in sorted(glob.glob(os.path.join(d, "*_align_x*_live.jpg"))):
            pose = pose_from_name(live)
            robot = live.replace("_live.jpg", "_robot.jpg")
            if pose and os.path.exists(robot):
                rows.append((pose, tip_live(live), tip_robot(robot)))
    P = np.array([r[0] for r in rows])
    A = np.hstack([np.ones((len(P), 1)), P - REF])
    model = {"ref_pose": REF.tolist(), "n_poses": len(rows), "poses": P.tolist()}
    for name, k in (("live", 1), ("robot", 2)):
        Y = np.array([r[k] for r in rows])
        coef, *_ = np.linalg.lstsq(A, Y, rcond=None)
        rms = np.sqrt(((A @ coef - Y) ** 2).mean(axis=0))
        model[name] = {
            "image_at_ref": coef[0].round(2).tolist(),
            "px_per_mm": {"x": coef[1].round(3).tolist(), "y": coef[2].round(3).tolist(),
                          "z": coef[3].round(3).tolist()},
            "fit_rms_px": rms.round(2).tolist(),
            "tips_px": Y.round(1).tolist(),
        }
    return model


def press(d, x, y, model):
    """How far above its commanded Z the nozzle really was at each press step."""
    jl = model["live"]["px_per_mm"]
    dv = jl["x"][1] * (x - REF[0]) + jl["y"][1] * (y - REF[1])
    out = []
    for f in sorted(glob.glob(os.path.join(d, "*_z*_live.jpg"))):
        m = re.search(r"_z([\d.]+)_live", os.path.basename(f))
        s = shoulder_row(f)
        if not m or s is None:
            continue
        z = float(m.group(1))
        expected = SHOULDER_A + SHOULDER_B * (120 - z) + dv
        out.append({"photo": os.path.basename(f), "z_sent": z, "shoulder_row": round(s, 2),
                    "expected_row": round(expected, 2),
                    "nozzle_above_sent_mm": round(-(s - expected) / SHOULDER_B, 2)})
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fit")
    f.add_argument("dirs", nargs="+")
    f.add_argument("--out", default="camera-model.json")
    q = sub.add_parser("press")
    q.add_argument("dir")
    q.add_argument("--x", type=float, required=True)
    q.add_argument("--y", type=float, required=True)
    q.add_argument("--model", default="camera-model.json")
    a = p.parse_args()
    if a.cmd == "fit":
        model = fit(a.dirs)
        with open(a.out, "w") as fh:
            json.dump(model, fh, indent=1)
        for name in ("live", "robot"):
            m = model[name]
            print(f"{name:5s} px/mm  x {m['px_per_mm']['x']}  y {m['px_per_mm']['y']}  "
                  f"z {m['px_per_mm']['z']}  rms {m['fit_rms_px']}")
    else:
        with open(a.model) as fh:
            model = json.load(fh)
        for r in press(a.dir, a.x, a.y, model):
            print(f"{r['photo']:34s} sent z {r['z_sent']:6.2f}  nozzle "
                  f"{r['nozzle_above_sent_mm']:+.2f} mm above that")


if __name__ == "__main__":
    main()
