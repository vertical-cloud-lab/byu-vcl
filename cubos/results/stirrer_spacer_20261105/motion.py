"""Did the stirrer move anything? Frame-to-frame change in camera 1's video, per frame.

usage: motion.py <label>     (reads <label>.mjpeg and <label>_pts.txt; writes <label>_motion.csv)

Camera 1 rides on the gantry head and looks down at the compact stirrer. For each frame,
the mean absolute difference (0-255 grey levels) from the frame before, inside STIR (the
stirrer: in spacer_1105 the cup with the open vial and the water in it, in washers_1105 the
flange and the vial's cap, which went on as that run started) and inside STILL (bare deck
or a part that doesn't move, for the camera's own noise). The regions are in the 864 x 592
frame; the crop differs between the two runs because the head was moved by hand in between.
"""
import csv, sys
import cv2
import numpy as np

REGIONS = {  # x0, y0, x1, y1
    "spacer_1105": {"STIR": (40, 330, 480, 592), "STILL": (80, 60, 170, 240)},
    "washers_1105": {"STIR": (220, 140, 760, 400), "STILL": (20, 400, 200, 540)},
}
label = sys.argv[1]
reg = REGIONS[label]
data = open(f"{label}.mjpeg", "rb").read()
offs, i = [], 0
while True:
    a = data.find(b"\xff\xd8", i)
    b = data.find(b"\xff\xd9", a + 2) if a >= 0 else -1
    if b < 0:
        break
    offs.append((a, b + 2))
    i = b + 2
pts = [float(l) / 1000 for l in open(f"{label}_pts.txt") if l.strip() and not l.startswith("#")]


def grey(k):
    a, b = offs[k]
    return cv2.imdecode(np.frombuffer(data[a:b], np.uint8), cv2.IMREAD_GRAYSCALE).astype(np.float32)


def change(g, prev, r):
    x0, y0, x1, y1 = r
    return float(np.abs(g[y0:y1, x0:x1] - prev[y0:y1, x0:x1]).mean())


prev = grey(0)
with open(f"{label}_motion.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["t_video_s", "stirrer", "still"])
    for k in range(1, min(len(offs), len(pts))):
        g = grey(k)
        w.writerow([f"{pts[k]:.3f}", f"{change(g, prev, reg['STIR']):.3f}",
                    f"{change(g, prev, reg['STILL']):.3f}"])
        prev = g
print(label, len(offs), "frames")
