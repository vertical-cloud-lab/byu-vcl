#!/usr/bin/env python3
"""Sort an STL's triangles into faces, each lying on one plane, cylinder, sphere or torus.

A CAD export puts every STL vertex exactly on the original surfaces, so each face of the original
model can be recovered by fitting: a region is accepted only if all its vertices lie within TOL
(default 0.00002 mm) of the fitted surface and every facet faces the surface's way within 8 degrees.

1. Coplanar triangles spanning more than 0.2 mm form the flat faces (facets of curved surfaces are
   narrower than that).
2. The remaining triangles are split into smoothly connected components; a component that fits one
   surface becomes one region.
3. Other components are split by region growing from seed patches, repeated until no new region is
   found; leftover triangles that fit a neighbouring region join it.
4. What is left is mostly long fillet facets whose only vertices are at their ends; for those, a
   cylinder axis is taken from the cross product of two neighbouring facet normals.

Usage: python segment.py input.stl seg.pkl [TOL]
"""
import pickle
import sys
import time
from collections import deque

import numpy as np

sys.path.insert(0, __import__("os").path.dirname(__file__))
from fit import bfs_patch, dist, fit_best, normal_ok, fit_cylinder, sane  # noqa: E402
from stl_to_step import neighbours, planar_regions, read_stl  # noqa: E402

TOL = float(sys.argv[3]) if len(sys.argv) > 3 else 2e-5
t0 = time.time()
P, F = read_stl(sys.argv[1])
nbr = neighbours(F, len(P))
region, nn = planar_regions(P, F, nbr, 2e-6)
a, b, c = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]
area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
cen = (a + b + c) / 3
nreg = region.max() + 1
members = [[] for _ in range(nreg)]
for t, r in enumerate(region):
    members[r].append(t)
width = np.zeros(nreg)
for r, m in enumerate(members):
    Q = P[np.unique(F[m])]
    Q = Q - Q.mean(0)
    width[r] = np.ptp(Q @ np.linalg.svd(Q, full_matrices=False)[2][:2].T, axis=0).min()
flat = width > 0.2
print(f"{len(F)} tris; {nreg} planar groups; flat faces {flat.sum()}; min flat width {width[flat].min():.3f}, "
      f"max strip width {width[~flat].max():.3f} ({time.time()-t0:.1f}s)")

# final labels: flat faces keep their own id
label = np.full(len(F), -1)
models = []
for r in np.nonzero(flat)[0]:
    m = members[r]
    vids = np.unique(F[m])
    Q = P[vids]
    # exact axis plane when a coordinate is shared, else lstsq
    n = nn[m[np.argmax(area[m])]]
    k = None
    for kk in range(3):
        if np.ptp(Q[:, kk]) == 0:
            k = kk
    if k is not None:
        nv = np.zeros(3)
        nv[k] = np.sign(n[k])
        mod = dict(type="plane", o=Q[0].copy(), n=nv)
    else:
        cq = Q.mean(0)
        nv = np.linalg.svd(Q - cq, full_matrices=False)[2][2]
        mod = dict(type="plane", o=cq, n=nv if nv @ n > 0 else -nv)
    label[m] = len(models)
    models.append(mod)

curved = label < 0
cosd = np.cos(np.radians(25))
# connected components of curved triangles over smooth edges
comp = np.full(len(F), -1)
nc = 0
for s in np.nonzero(curved)[0]:
    if comp[s] >= 0:
        continue
    comp[s] = nc
    q = deque([s])
    while q:
        t = q.popleft()
        for u in nbr[t]:
            if curved[u] and comp[u] < 0 and nn[u] @ nn[t] > cosd:
                comp[u] = nc
                q.append(u)
    nc += 1
print(f"{curved.sum()} curved tris in {nc} smooth components ({time.time()-t0:.1f}s)")


def grow(tris_allowed, seed_tris, model):
    """Grow from seed_tris over allowed triangles whose vertices all fit model within TOL."""
    reg = set(seed_tris)
    q = deque(seed_tris)
    while q:
        t = q.popleft()
        for u in nbr[t]:
            if u in reg or not tris_allowed[u]:
                continue
            if np.abs(dist(model, P[F[u]])).max() < TOL and normal_ok(model, nn[u:u + 1], cen[u:u + 1]):
                reg.add(u)
                q.append(u)
    return sorted(reg)


def fit_tris(tris):
    tris = np.asarray(tris)
    Q = P[np.unique(F[tris])]
    return fit_best(Q, nn[tris], cen[tris], TOL)


nsplit = 0
todo = []
for ci in range(nc):
    tris = np.nonzero(comp == ci)[0]
    m, r = fit_tris(tris)
    if m is not None:
        label[tris] = len(models)
        models.append(m)
    else:
        todo.extend(tris.tolist())
        nsplit += 1
allowed = np.zeros(len(F), bool)
allowed[todo] = True
for npass in range(8):
    made = 0
    tried = np.zeros(len(F), bool)
    rem = np.nonzero(allowed)[0]
    for seed in rem[np.argsort(-area[rem])]:
        if not allowed[seed] or tried[seed]:
            continue
        patch = bfs_patch(seed, nbr, allowed, 40)
        m, r = fit_tris(patch)
        if m is None:
            small = bfs_patch(seed, nbr, allowed, 12)
            if len(small) >= 6:
                m, r = fit_tris(small)
                patch = small
        if m is None:
            tried[patch] = True
            continue
        for _ in range(3):
            reg = grow(allowed, patch, m)
            m2, r2 = fit_tris(reg)
            if m2 is None or m2["type"] != m["type"]:
                break
            m, patch = m2, reg
        reg = grow(allowed, patch, m)
        label[reg] = len(models)
        models.append(m)
        allowed[reg] = False
        made += 1
    # let regions absorb leftover neighbours that fit them
    changed = True
    while changed:
        changed = False
        for t in np.nonzero(allowed)[0]:
            for u in nbr[t]:
                L = label[u]
                if L >= 0 and models[L]["type"] != "plane":
                    if np.abs(dist(models[L], P[F[t]])).max() < TOL and normal_ok(models[L], nn[t:t + 1], cen[t:t + 1]):
                        label[t] = L
                        allowed[t] = False
                        changed = True
                        break
    print(f"pass {npass}: {made} new regions, {allowed.sum()} triangles left ({time.time()-t0:.1f}s)", flush=True)
    if made == 0 or not allowed.any():
        break

SIN_AX = np.sin(np.radians(0.2))


def cyl_hypothesis(seed):
    """Cylinder through the seed: axis from the cross product of two neighbouring facet normals."""
    for u in nbr[seed]:
        if not allowed[u]:
            continue
        cr = np.cross(nn[seed], nn[u])
        s = np.linalg.norm(cr)
        if s < np.sin(np.radians(0.3)):
            continue
        ax = cr / s
        seen = {seed}
        q = deque([seed])
        cand = []
        while q and len(cand) < 80:
            t = q.popleft()
            cand.append(t)
            for w in nbr[t]:
                if w not in seen and allowed[w] and abs(nn[w] @ ax) < SIN_AX:
                    seen.add(w)
                    q.append(w)
        if len(cand) < 4:
            continue
        Q = P[np.unique(F[cand])]
        try:
            m = fit_cylinder(Q, nn[cand], ax)
        except Exception:
            continue
        if sane(m) and np.abs(dist(m, Q)).max() < TOL and normal_ok(m, nn[cand], cen[cand]):
            return cand, m
    return None, None


for npass in range(6):
    made = 0
    rem = np.nonzero(allowed)[0]
    for seed in rem[np.argsort(-area[rem])]:
        if not allowed[seed]:
            continue
        cand, m = cyl_hypothesis(seed)
        if m is None:
            continue
        reg = grow(allowed, cand, m)
        m2, _ = fit_tris(reg)
        if m2 is not None and m2["type"] == "cylinder":
            m = m2
            reg = grow(allowed, reg, m)
        label[reg] = len(models)
        models.append(m)
        allowed[reg] = False
        made += 1
    print(f"cylinder pass {npass}: {made} new regions, {allowed.sum()} triangles left ({time.time()-t0:.1f}s)", flush=True)
    if made == 0:
        break

print(f"{len(models)} surfaces ({nsplit} components split) ({time.time()-t0:.1f}s)")
# residual report
from collections import Counter  # noqa: E402

print(Counter(m["type"] for m in models))
worst = 0
for i, m in enumerate(models):
    tris = np.nonzero(label == i)[0]
    if len(tris) == 0:
        continue
    r = np.abs(dist(m, P[np.unique(F[tris])])).max()
    worst = max(worst, r)
print(f"worst vertex residual {worst:.2e} mm; unlabelled tris {(label < 0).sum()}")
pickle.dump(dict(P=P, F=F, label=label, models=models, nn=nn), open(sys.argv[2], "wb"))
