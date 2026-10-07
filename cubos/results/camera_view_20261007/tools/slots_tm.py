"""Slot centres by template matching one clear slot. usage: slots_tm.py <img> <cx> <cy> <hw> <hh> <thr> <out_prefix>"""
import sys, site
sys.path.append(site.getusersitepackages())
import cv2, numpy as np
img = cv2.imread(sys.argv[1]); g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cx, cy, hw, hh, thr = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), float(sys.argv[6])
out = sys.argv[7]
t = g[cy - hh:cy + hh, cx - hw:cx + hw]
pts = []
for sc in (0.85, 1.0, 1.15):
    ts = cv2.resize(t, None, fx=sc, fy=sc)
    r = cv2.matchTemplate(g, ts, cv2.TM_CCOEFF_NORMED)
    dil = cv2.dilate(r, np.ones((41, 41), np.uint8))
    ys, xs = np.where((r == dil) & (r > thr))
    for x, y in zip(xs, ys):
        pts.append((x + ts.shape[1] / 2, y + ts.shape[0] / 2, r[y, x]))
pts = np.array(sorted(pts, key=lambda p: -p[2]))
keep = []
for p in pts:
    if all(np.hypot(p[0] - q[0], p[1] - q[1]) > 35 for q in keep):
        keep.append(p)
keep = np.array(keep)
print('matches', len(keep))
np.save(out + '_cands.npy', keep)
vis = img.copy()
for p in keep: cv2.circle(vis, (int(p[0]), int(p[1])), 7, (0, 0, 255), -1)
cv2.imwrite(out + '_det.jpg', cv2.resize(vis, (1152, 648)))
