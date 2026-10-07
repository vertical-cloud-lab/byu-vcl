"""Assign detected slot centres to PandaDeck grid indices and solve the camera pose.
usage: gridfit.py <image> <cands.npy> <seed_px_x> <seed_px_y> <seed_i> <seed_j> <out_prefix>
Plate frame (mm): origin front-left corner, x right (image right), y toward the back
(image up). Slot centres: x = 27.5 + 25 i (i = 0..17), y = 40 + 45 r where r counts
rows from the FRONT (r = 0..9). j = 9 - r counts rows from the back.
"""
import sys, site, json
sys.path.append(site.getusersitepackages())
import cv2, numpy as np
img_path, cands_path = sys.argv[1], sys.argv[2]
sx, sy, si, sj = float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
out = sys.argv[7]
img = cv2.imread(img_path); H, W = img.shape[:2]
c = np.load(cands_path)[:, :2]
def plate_xy(i, j):
    return 27.5 + 25.0 * i, 40.0 + 45.0 * (9 - j)
# nearest-neighbour lattice vectors around the seed
d = c - np.array([sx, sy])
k = np.argmin((d**2).sum(1)); seed = c[k] if np.sqrt((d[k]**2).sum()) < 20 * W / 2304 else np.array([sx, sy])
nn = []
for p in c:
    dd = c - p; r = np.hypot(*dd.T); r[r == 0] = 1e9
    for q in np.argsort(r)[:4]:
        nn.append(dd[q])
nn = np.array(nn)
# column step: mostly horizontal, row step: mostly vertical
hz = nn[(np.abs(nn[:, 0]) > 2 * np.abs(nn[:, 1]))]; hz = hz * np.sign(hz[:, :1])
vt = nn[(np.abs(nn[:, 1]) > 2 * np.abs(nn[:, 0]))]; vt = vt * np.sign(vt[:, 1:])
u = np.median(hz, 0); v = np.median(vt, 0)
if len(sys.argv) > 8:
    u = np.array([float(sys.argv[8]), float(sys.argv[9])]); v = np.array([float(sys.argv[10]), float(sys.argv[11])])
print('u', u, 'v', v)
# iterative assignment with a homography from (i,j) -> pixel
A = np.array([[u[0], v[0], seed[0] - u[0]*si - v[0]*sj], [u[1], v[1], seed[1] - u[1]*si - v[1]*sj], [0, 0, 1.0]])
Hm = A
for it in range(6):
    grid = np.array([[i, j] for i in range(18) for j in range(10)], float)
    pred = cv2.perspectiveTransform(grid[None], Hm)[0]
    tol = 0.3 * np.hypot(*u)
    pairs = []
    for g, p in zip(grid, pred):
        r = np.hypot(*(c - p).T); q = np.argmin(r)
        if r[q] < tol: pairs.append((g, c[q]))
    G = np.array([p[0] for p in pairs]); P = np.array([p[1] for p in pairs])
    Hm, mask = cv2.findHomography(G, P, cv2.RANSAC, 3.0 * W / 2304)
    print('iter', it, 'matched', len(pairs), 'inliers', int(mask.sum()))
mask = mask.ravel().astype(bool)
G, P = G[mask], P[mask]
obj = np.array([[*plate_xy(i, j), 0.0] for i, j in G])
np.savez(out + '_matches.npz', G=G, P=P, obj=obj)
vis = img.copy()
grid = np.array([[i, j] for i in range(18) for j in range(10)], float)
pred = cv2.perspectiveTransform(grid[None], Hm)[0]
s = W / 2304
for (i, j), p in zip(grid, pred):
    cv2.circle(vis, tuple(int(t) for t in p), int(5*s), (0, 255, 255), 1)
for p in P:
    cv2.circle(vis, tuple(int(t) for t in p), int(4*s), (0, 0, 255), -1)
for (i, j), p in zip(grid, pred):
    if (i in (0, 17)) and (j in (0, 9)):
        cv2.putText(vis, f'{int(i)},{int(j)}', (int(p[0]) + 8, int(p[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.8*s, (0, 255, 0), 2)
cv2.imwrite(out + '_grid.jpg', cv2.resize(vis, (1536, int(1536 * H / W))))
