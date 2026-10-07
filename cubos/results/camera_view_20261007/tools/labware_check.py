"""Check the camera model against known labware spacings in ben_2vials_tiprack.yaml.
usage: labware_check.py <image> <pose.json> <out.json>
"""
import sys, site, json
sys.path.append(site.getusersitepackages())
import cv2, numpy as np
from scipy.optimize import brentq
img = cv2.imread(sys.argv[1]); pose = json.load(open(sys.argv[2]))['k1k2']
K = np.array(pose['K']); dist = np.array(pose['dist']); R, _ = cv2.Rodrigues(np.array(pose['rvec'])); C = np.array(pose['C'])
def rays(px):
    n = cv2.undistortPoints(np.array(px, np.float64).reshape(-1, 1, 2), K, dist).reshape(-1, 2)
    d = np.c_[n, np.ones(len(n))] @ R  # camera -> plate frame (R^T d)
    return d
def on_plane(px, h):
    d = rays(px); s = (h - C[2]) / d[:, 2]
    return C[:2] + d[:, :2] * s[:, None]
# --- tip rack holes: dark blobs inside the bright white block
x0, y0, x1, y1 = 1150, 650, 1290, 1030
roi = img[y0:y1, x0:x1]; g = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
white = (g > 170).astype(np.uint8)
white = cv2.morphologyEx(white, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
cnt = max(cv2.findContours(white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0], key=cv2.contourArea)
mask = np.zeros_like(white); cv2.drawContours(mask, [cnt], -1, 1, -1)
mask = cv2.erode(mask, np.ones((5, 5), np.uint8))
dark = ((g < np.percentile(g[mask > 0], 35)) & (mask > 0)).astype(np.uint8)
n, lab, stats, cent = cv2.connectedComponentsWithStats(dark)
holes = np.array([cent[i] + [x0, y0] for i in range(1, n) if 4 <= stats[i, cv2.CC_STAT_AREA] <= 80])
print('tip-rack hole blobs', len(holes))
# split into two columns along the rack's long axis
mean = holes.mean(0); u, s_, vt = np.linalg.svd(holes - mean); ax = vt[0]; perp = vt[1]
side = (holes - mean) @ perp
cols = [holes[side < 0], holes[side >= 0]]
res = {}
def pitch_err(h):
    ps = []
    for col in cols:
        q = on_plane(col, h); order = np.argsort(q[:, 1]); q = q[order]
        dd = np.hypot(*np.diff(q, axis=0).T); dd = dd[(dd > 5) & (dd < 12)]
        ps.extend(dd)
    return np.median(ps) - 8.5
h_r = brentq(pitch_err, 0, 200)
qa = on_plane(cols[0], h_r); qb = on_plane(cols[1], h_r)
colx = sorted([qa[:, 0].mean(), qb[:, 0].mean()])
rows_y = np.sort(np.r_[qa[:, 1], qb[:, 1]])
res['tip_rack'] = dict(n_holes=int(len(holes)), top_height_mm_from_8p5_pitch=float(h_r),
                       column_x_plate=colx, column_spacing_mm=float(colx[1] - colx[0]),
                       hole_y_span_plate=[float(rows_y.min()), float(rows_y.max())])
print('tip rack: top height %.1f mm (from 8.5 mm pitch); column spacing %.2f mm (file 8.5); columns at plate x %s; holes y %.1f..%.1f'
      % (h_r, colx[1] - colx[0], np.round(colx, 1), rows_y.min(), rows_y.max()))
# --- vial tops: three bright disks
x0, y0, x1, y1 = 800, 880, 960, 1160
roi = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
circ = cv2.HoughCircles(cv2.GaussianBlur(roi, (5, 5), 1.5), cv2.HOUGH_GRADIENT, dp=1, minDist=50, param1=80, param2=25, minRadius=22, maxRadius=45)
circ = circ[0][np.argsort(circ[0][:, 1])] if circ is not None else np.zeros((0, 3))
vt_px = circ[:, :2] + [x0, y0]
print('vial-top circles', np.round(circ, 1).tolist())
def vpitch(h):
    q = on_plane(vt_px, h); return np.median(np.hypot(*np.diff(q, axis=0).T)) - 33.0
h_v = brentq(vpitch, 0, 300)
qv = on_plane(vt_px, h_v)
res['vials'] = dict(top_height_mm_from_33_pitch=float(h_v), plate_xy=qv.tolist())
print('vials: top height %.1f mm (from 33 mm pitch); plate xy %s' % (h_v, np.round(qv, 1).tolist()))
# --- deck <-> plate offset from labware, and the vial-to-rack distance check
rack_cx = np.mean(colx); vial_x = qv[:, 0].mean()
res['vial_to_rack_x_mm'] = dict(measured=float(rack_cx - vial_x), file=float((282.832 + 291.332) / 2 - 136.668))
print('vial column -> tip-rack centre line, X: measured %.1f mm, deck file %.1f mm' % (rack_cx - vial_x, (282.832 + 291.332) / 2 - 136.668))
off_x_rack = rack_cx - (282.832 + 291.332) / 2; off_x_vial = vial_x - 136.668
# rows: A (y = 89) is the front end, O (y = 208) the back; the plate y increases toward the back
off_y_rack = rows_y.min() - 89.0
vy = np.sort(qv[:, 1])  # front-most first
res['offset_plate_minus_deck'] = dict(x_from_rack=float(off_x_rack), x_from_vials=float(off_x_vial), y_from_rack=float(off_y_rack),
                                      y_vials_if_front_is_vial_1=[float(vy[0] - 45), float(vy[1] - 78)])
print('plate - deck offset: x %.1f (rack) / %.1f (vials); y %.1f (rack) / %s (vials, front two = vial_1, vial_2)'
      % (off_x_rack, off_x_vial, off_y_rack, np.round([vy[0] - 45, vy[1] - 78], 1).tolist()))
json.dump(res, open(sys.argv[3], 'w'), indent=1)
vis = img.copy()
for p in holes: cv2.circle(vis, tuple(int(t) for t in p), 3, (0, 0, 255), -1)
for x, y, r in circ: cv2.circle(vis, (int(x + 800), int(y + 880)), int(r), (0, 255, 0), 2)
cv2.imwrite(sys.argv[3].replace('.json', '.jpg'), vis[600:1200, 750:1350])
