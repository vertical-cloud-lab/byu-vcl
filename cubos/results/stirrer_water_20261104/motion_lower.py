"""The 23:32 run (fan started with the vial out, vial lowered in): did the water move?

usage: motion_lower.py   (reads lower_1104.mjpeg, _pts.txt, _camera.json; writes
                          lower_1104_motion.csv and prints a line per stretch)

Camera 1 had been moved between the runs, so the vial sits elsewhere in the frame than in
motion.py. Frame-to-frame mean |difference| over the vial (VIAL) and over bare deck
(STILL), by stretches picked from the frames: hands in the picture are left out.
"""
import json
import cv2
import numpy as np

secs = lambda u: sum(float(x) * m for x, m in zip(u.rstrip("Z").split(":"), (3600, 60, 1)))
T0 = secs(json.load(open("lower_1104_camera.json"))["first_bytes_utc"])
STEP = secs("23:32:13.80")     # 30,300,105 sent
pts = [float(l) for l in open("lower_1104_pts.txt") if l.strip() and not l.startswith("#")]
data = open("lower_1104.mjpeg", "rb").read()
VIAL, STILL = (200, 200, 420, 360), (600, 30, 700, 100)
crop = lambda g, r: g[r[1]:r[3], r[0]:r[2]]
prev, out, i, k = None, [], 0, 0
while True:
    a = data.find(b"\xff\xd8", i)
    b = data.find(b"\xff\xd9", a + 2) if a >= 0 else -1
    if b < 0:
        break
    i = b + 2
    g = cv2.imdecode(np.frombuffer(data[a:i], np.uint8), cv2.IMREAD_GRAYSCALE).astype(np.float32)
    if prev is not None:
        out.append((T0 + pts[k] / 1000 - STEP, np.abs(crop(g, VIAL) - crop(prev, VIAL)).mean(),
                    np.abs(crop(g, STILL) - crop(prev, STILL)).mean()))
    prev, k = g, k + 1
out = np.array(out)
np.savetxt("lower_1104_motion.csv", out, delimiter=",", fmt="%.3f", comments="",
           header="t_after_step_s,vial_vs_prev,still_vs_prev")
for lo, hi, what in ((-6, -3, "vial out, hand in view"), (22, 33, "vial in, hands off, Hall 300-360"),
                     (62, 73, "vial in, hands off, Hall erratic"), (75, 89, "vial in, Hall 60-810"),
                     (91, 97, "after 30,0")):
    s = out[(out[:, 0] >= lo) & (out[:, 0] <= hi)]
    print(f"{what:34s} {lo:+d}..{hi:+d} s: vial median {np.median(s[:, 1]):.2f}, p90 "
          f"{np.percentile(s[:, 1], 90):.2f} | bare deck median {np.median(s[:, 2]):.2f}")
