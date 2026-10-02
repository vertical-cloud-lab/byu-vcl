#!/usr/bin/env python3
"""Did the enclosure move with the nozzle? Measured from the robot's own camera.

The OT-2 cannot tell whether the enclosure is on its nozzle, so this reads it off
the photos ``enclosure_height_cal.py`` takes after every step. Three patches of
each 640x480 robot-camera frame are phase-correlated against a reference frame
(bare nozzle hovering just above the socket, before any contact):

* the pipette's lower housing -- moves with the nozzle (~1.07 px per mm of Z)
* the enclosure's front face, below the collar -- moves only if the enclosure does
* the base's front edge -- must not move at all; a non-zero shift here means
  the camera or the base moved and the other two numbers mean nothing

Rows are positive downwards, so a lift shows as a negative row shift. It also
reports how dark the seam under the enclosure is: a gap opening under a lifted
enclosure shows as a dark line there.

    python3 grip_shift.py REF.jpg PHOTO.jpg [PHOTO.jpg ...] [--json OUT]

The patches are for the base in slot 10, right-hand socket (A2), as photographed
on 2026-09-29; they need moving if the base or the camera moves.
"""
import argparse
import json
import os

import numpy as np
from PIL import Image

# (row0, row1, col0, col1) in the upright robot-camera frame
PATCHES = {
    "nozzle_housing": (0, 64, 224, 352),
    "enclosure_face": (118, 166, 196, 292),
    "base_static": (170, 230, 90, 330),
}
SEAM = (148, 168, 210, 262)       # the line under the enclosure's front face


def grey(path):
    return np.asarray(Image.open(path).convert("L"), dtype=float)


def shift(ref, img, patch):
    """Sub-pixel (rows, cols) shift of img relative to ref, and the peak height."""
    r0, r1, c0, c1 = patch
    win = np.hanning(r1 - r0)[:, None] * np.hanning(c1 - c0)[None, :]
    a = (ref[r0:r1, c0:c1] - ref[r0:r1, c0:c1].mean()) * win
    b = (img[r0:r1, c0:c1] - img[r0:r1, c0:c1].mean()) * win
    cross = np.fft.fft2(b) * np.conj(np.fft.fft2(a))
    corr = np.fft.ifft2(cross / (np.abs(cross) + 1e-9)).real
    iy, ix = np.unravel_index(np.argmax(corr), corr.shape)
    h, w = corr.shape

    def vertex(m, c, p):
        d = m - 2 * c + p
        return 0.5 * (m - p) / d if d else 0.0

    dy = iy + vertex(corr[(iy - 1) % h, ix], corr[iy, ix], corr[(iy + 1) % h, ix])
    dx = ix + vertex(corr[iy, (ix - 1) % w], corr[iy, ix], corr[iy, (ix + 1) % w])
    dy = dy - h if dy > h / 2 else dy
    dx = dx - w if dx > w / 2 else dx
    return round(float(dy), 2), round(float(dx), 2), round(float(corr.max()), 2)


def seam_darkness(img):
    r0, r1, c0, c1 = SEAM
    rows = img[r0:r1, c0:c1].mean(axis=1)
    return round(float(np.median(rows) - rows.min()), 1)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("ref")
    p.add_argument("photos", nargs="+")
    p.add_argument("--json")
    args = p.parse_args()
    ref = grey(args.ref)
    out = []
    for path in args.photos:
        img = grey(path)
        row = {"photo": os.path.basename(path), "seam_contrast": seam_darkness(img)}
        for name, patch in PATCHES.items():
            dy, dx, peak = shift(ref, img, patch)
            row[name] = {"rows": dy, "cols": dx, "peak": peak}
        out.append(row)
        print(f"{row['photo'][:34]:34s} nozzle {row['nozzle_housing']['rows']:+6.2f}  "
              f"enclosure {row['enclosure_face']['rows']:+6.2f}  "
              f"base {row['base_static']['rows']:+5.2f}  seam {row['seam_contrast']:5.1f}")
    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"reference": os.path.basename(args.ref), "patches": PATCHES,
                       "seam": SEAM, "rows_positive": "down", "photos": out}, fh, indent=1)


if __name__ == "__main__":
    main()
