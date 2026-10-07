import sys, site
sys.path.append(site.getusersitepackages())
import cv2, numpy as np
img_path, out_prefix = sys.argv[1], sys.argv[2]
img = cv2.imread(img_path)
g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
H, W = g.shape
scale = W / 2304.0
BLOCK = int(sys.argv[3]) if len(sys.argv) > 3 else 31
# bright rims: adaptive threshold
bw = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, int(BLOCK*scale)|1, -12)
bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))
cnts, hier = cv2.findContours(bw, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
cands = []
for i, c in enumerate(cnts):
    if hier[0][i][3] < 0:  # want holes (children)
        continue
    a = cv2.contourArea(c)
    if a < 150*scale**2 or a > 12000*scale**2: continue
    x, y, w, h = cv2.boundingRect(c)
    ar = h / max(w, 1)
    if not (1.4 < ar < 4.5): continue
    hull = cv2.convexHull(c); sol = a / max(cv2.contourArea(hull), 1)
    if sol < 0.85: continue
    M = cv2.moments(c)
    cands.append((M['m10']/M['m00'], M['m01']/M['m00'], w, h, a))
cands = np.array(cands)
print('candidates', len(cands))
vis = img.copy()
for x, y, w, h, a in cands:
    cv2.circle(vis, (int(x), int(y)), int(6*scale), (0,0,255), -1)
cv2.imwrite(out_prefix + '_det.jpg', cv2.resize(vis, (1536, int(1536*H/W))))
np.save(out_prefix + '_cands.npy', cands)
