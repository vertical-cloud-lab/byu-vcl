#!/usr/bin/env python3
"""Preview of the converted part: flat faces (one STEP face each) in blue, outlined;
curved surfaces, which stay faceted, in gray. Z-buffered software render, two views.

Usage: python preview.py regions.npz out.png   (regions.npz from stl_to_step.py --regions)
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

d = np.load(sys.argv[1])
P, F, region = d["P"], d["F"], d["region"]
# width of each face: its smaller extent in its own plane. Facets of the fillets, holes and bosses
# are all under 0.2 mm wide; the part's real flat faces are all over 0.5 mm wide.
width = np.zeros(region.max() + 1)
for r, tris in enumerate(np.split(np.argsort(region, kind="stable"), np.cumsum(np.bincount(region))[:-1])):
    Q = P[np.unique(F[tris])]
    Q = Q - Q.mean(0)
    width[r] = np.ptp(Q @ np.linalg.svd(Q, full_matrices=False)[2][:2].T, axis=0).min()
flat_face = width > 0.2
SURF, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
BLUE, GRAY, EDGE = np.array([0x2a, 0x78, 0xd6]) / 255, np.array([0xc3, 0xc2, 0xb7]) / 255, np.array([0.13, 0.13, 0.12])

a, b, c = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]
nn = np.cross(b - a, c - a)
nn /= np.linalg.norm(nn, axis=1, keepdims=True)
# edges between different faces where at least one side is a flat face: the flat faces' outlines
E = np.stack([F, np.roll(F, -1, axis=1)], axis=2).reshape(-1, 2)
T = np.repeat(np.arange(len(F)), 3)
key = np.minimum(E[:, 0], E[:, 1]).astype(np.int64) * len(P) + np.maximum(E[:, 0], E[:, 1])
o = np.argsort(key, kind="stable")
t1, t2, ed = T[o][0::2], T[o][1::2], E[o][0::2]
outline = (region[t1] != region[t2]) & (flat_face[region[t1]] | flat_face[region[t2]])
ed, et1, et2 = ed[outline], t1[outline], t2[outline]


def render(az, el, S=1400, pad=0.06):
    az, el = np.radians(az), np.radians(el)
    cdir = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    r = np.cross(-cdir, [0, 0, 1.0]); r /= np.linalg.norm(r)
    u = np.cross(r, -cdir)
    ctr = (P.max(0) + P.min(0)) / 2
    Q = P - ctr
    sx, sy, sz = Q @ r, Q @ u, Q @ cdir
    span = max(np.ptp(sx), np.ptp(sy)) * (1 + 2 * pad)
    X = (sx / span + 0.5) * S
    Y = (0.5 - sy / span) * S
    img = np.tile(np.array([int(SURF[i:i + 2], 16) for i in (1, 3, 5)]) / 255, (S, S, 1))
    zb = np.full((S, S), -np.inf)
    L = cdir + 0.6 * u - 0.35 * r
    L /= np.linalg.norm(L)
    shade = 0.42 + 0.58 * np.clip(nn @ L, 0, 1)
    front = nn @ cdir > 0
    for t in np.nonzero(front)[0]:
        i = F[t]
        xs, ys, zs = X[i], Y[i], sz[i]
        x0, x1 = max(int(xs.min()), 0), min(int(np.ceil(xs.max())), S - 1)
        y0, y1 = max(int(ys.min()), 0), min(int(np.ceil(ys.max())), S - 1)
        det = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if abs(det) < 1e-12:
            continue
        px, py = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        l1 = ((ys[1] - ys[2]) * (px - xs[2]) + (xs[2] - xs[1]) * (py - ys[2])) / det
        l2 = ((ys[2] - ys[0]) * (px - xs[2]) + (xs[0] - xs[2]) * (py - ys[2])) / det
        l3 = 1 - l1 - l2
        m = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        zz = l1 * zs[0] + l2 * zs[1] + l3 * zs[2]
        sub = zb[y0:y1 + 1, x0:x1 + 1]
        upd = m & (zz > sub)
        sub[upd] = zz[upd]
        img[y0:y1 + 1, x0:x1 + 1][upd] = (BLUE if flat_face[region[t]] else GRAY) * shade[t]
    eps = 0.04  # mm of depth slack, so edges lying on the visible surface pass the depth test
    for (i, j), ta, tb in zip(ed, et1, et2):
        if not (front[ta] or front[tb]):
            continue
        n = int(max(abs(X[j] - X[i]), abs(Y[j] - Y[i])) * 1.5) + 2
        s = np.linspace(0, 1, n)
        xs, ys, zs = X[i] + s * (X[j] - X[i]), Y[i] + s * (Y[j] - Y[i]), sz[i] + s * (sz[j] - sz[i])
        ix, iy = np.clip(xs.astype(int), 0, S - 2), np.clip(ys.astype(int), 0, S - 2)
        vis = zs >= zb[iy, ix] - eps
        for dx in (0, 1):
            for dy in (0, 1):
                img[iy[vis] + dy, ix[vis] + dx] = EDGE
    k = 2  # 2x supersampling -> average down
    return img.reshape(S // k, k, S // k, k, 3).mean(axis=(1, 3))


views = [(-55, 28, "From above"), (125, -28, "From below, opposite side")]
fig, axes = plt.subplots(1, 2, figsize=(11, 6.2), facecolor=SURF)
for ax, (az, el, title) in zip(axes, views):
    ax.imshow(render(az, el))
    ax.set_title(title, color=INK2, fontsize=11)
    ax.axis("off")
nflat = int(flat_face.sum())
fig.suptitle("RaspberryPiCameraMount.step: exact conversion of the Cubware STL", color=INK, fontsize=13, x=0.02, y=0.955, ha="left", va="center")
fig.legend(handles=[Patch(color=BLUE, label=f"Flat face, one STEP face each ({nflat} faces, outlined)"),
                    Patch(color=GRAY, label=f"Curved surface, faceted as in the STL ({len(width) - nflat:,} faces)")],
           loc="lower left", ncol=2, frameon=False, fontsize=10, labelcolor=INK)
fig.text(0.98, 0.955, "28.8 × 31.04 × 34.0 mm, 8,760.9 mm³", color=INK2, fontsize=10, ha="right", va="center")
plt.subplots_adjust(left=0.01, right=0.99, top=0.88, bottom=0.08, wspace=0.02)
fig.savefig(sys.argv[2], dpi=110, facecolor=SURF)
print("wrote", sys.argv[2], "-", int(flat_face.sum()), "flat faces")
