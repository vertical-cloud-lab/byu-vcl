#!/usr/bin/env python3
"""Convert a closed STL mesh to a STEP solid without remodelling it.

Every STL vertex keeps its exact coordinates, and every edge is a straight line
between two STL vertices, shared by the faces on either side, so the solid is
closed by construction (no sewing). Triangles that lie in one plane, to within
--plane-tol (default 2e-6 mm, the rounding of the STL's 32-bit floats), are merged
into a single planar face. Nothing else is changed, so curved surfaces come out
faceted, exactly as the STL has them.

Written for cadquery-ocp 8.0 (OpenCascade 8.0): pip install cadquery-ocp numpy

Usage: python stl_to_step.py input.stl output.step [--name NAME] [--plane-tol MM]
       [--regions regions.npz]
"""
import argparse
import time

import numpy as np
from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.Geom import Geom_Plane
from OCP.gp import gp_Ax3, gp_Dir, gp_Pnt
from OCP.IFSelect import IFSelect_ReturnStatus
from OCP.Interface import Interface_Static
from OCP.STEPControl import STEPControl_StepModelType, STEPControl_Writer
from OCP.TopoDS import TopoDS_Face, TopoDS_Shell, TopoDS_Solid, TopoDS_Vertex, TopoDS_Wire


def read_stl(path):
    """Return unique vertices (float64, exactly the STL's float32 values) and faces."""
    raw = open(path, "rb").read()
    n = int(np.frombuffer(raw, "<u4", 1, 80)[0])
    if len(raw) != 84 + 50 * n:
        raise SystemExit("only binary STL is supported")
    rec = np.frombuffer(raw, np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]), n, 84)
    uniq, inv = np.unique(rec["v"].reshape(-1, 3), axis=0, return_inverse=True)
    return uniq.astype(np.float64), inv.reshape(-1, 3)


def neighbours(F, nv):
    """nbr[t, k] = triangle across edge k (F[t,k] -> F[t,(k+1)%3]); requires a closed, oriented, manifold mesh."""
    E = np.stack([F, np.roll(F, -1, axis=1)], axis=2)
    key = (E[..., 0].astype(np.int64) * nv + E[..., 1]).ravel()
    twin = (E[..., 1].astype(np.int64) * nv + E[..., 0]).ravel()
    order = np.argsort(key)
    pos = np.clip(np.searchsorted(key[order], twin), 0, len(key) - 1)
    idx = order[pos]
    if not (key[idx] == twin).all() or len(np.unique(key)) != len(key):
        raise SystemExit("mesh is not closed, consistently oriented and manifold")
    return (idx // 3).reshape(F.shape)


def planar_regions(P, F, nbr, tol, cos_tol=np.cos(1e-3)):
    """Grow regions of triangles whose vertices all lie within tol of the seed triangle's plane."""
    a, b, c = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]
    cr = np.cross(b - a, c - a)
    area = 0.5 * np.linalg.norm(cr, axis=1)
    nn = cr / (2 * area[:, None])
    region = np.full(len(F), -1)
    r = 0
    for s in np.argsort(-area):  # largest triangle first: its normal is the most accurate
        if region[s] >= 0:
            continue
        ns, ds = nn[s], nn[s] @ a[s]
        region[s] = r
        stack = [s]
        while stack:
            t = stack.pop()
            for u in nbr[t]:
                if region[u] < 0 and nn[u] @ ns > cos_tol and np.abs(P[F[u]] @ ns - ds).max() <= tol:
                    region[u] = r
                    stack.append(u)
        r += 1
    return region, nn


def fit_plane(Q, seed_n):
    """Plane through points Q: exact axis plane if they share a coordinate, else the best of LSQ and seed."""
    for k in range(3):
        if np.ptp(Q[:, k]) == 0:
            n = np.zeros(3)
            n[k] = np.sign(seed_n[k])
            return Q[0].copy(), n
    c = Q.mean(axis=0)
    cand = [seed_n, np.linalg.svd(Q - c)[2][2]]
    cand = [n if n @ seed_n > 0 else -n for n in cand]
    devs = [np.abs((Q - c) @ n).max() for n in cand]
    return c, cand[int(np.argmin(devs))]


def region_loops(P, F, nbr, region, tris, rid, n):
    """Closed boundary loops of one region, as lists of vertex indices (region on the left)."""
    out = {}
    for t in tris:
        for k in range(3):
            if region[nbr[t, k]] != rid:
                out.setdefault(F[t, k], []).append(F[t, (k + 1) % 3])
    # 2D frame in the plane, for choosing the right turn at vertices where the boundary touches itself
    xd = np.cross(n, [1.0, 0, 0] if abs(n[0]) < 0.9 else [0, 1.0, 0])
    xd /= np.linalg.norm(xd)
    yd = np.cross(n, xd)
    loops = []
    remaining = sum(len(v) for v in out.values())
    while remaining:
        start = next(v for v, w in out.items() if w)
        loop, prev, cur = [start], None, start
        while True:
            cands = out[cur]
            if len(cands) == 1 or prev is None:
                nxt = cands[0]
            else:  # first outgoing edge clockwise from the reversed incoming edge
                back = P[prev] - P[cur]
                ab = np.arctan2(back @ yd, back @ xd)
                best = None
                for w in cands:
                    d = P[w] - P[cur]
                    cw = (ab - np.arctan2(d @ yd, d @ xd)) % (2 * np.pi)
                    if best is None or cw < best[0]:
                        best = (cw, w)
                nxt = best[1]
            cands.remove(nxt)
            remaining -= 1
            if nxt == start:
                break
            loop.append(nxt)
            prev, cur = cur, nxt
        loops.append(loop)
    return loops, xd, yd


def signed_area(P, loop, xd, yd):
    q = P[loop]
    x, y = q @ xd, q @ yd
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stl")
    ap.add_argument("step")
    ap.add_argument("--name", default="Part")
    ap.add_argument("--plane-tol", type=float, default=2e-6)
    ap.add_argument("--regions", help="save the triangle -> face map here (for previews)")
    args = ap.parse_args()
    t0 = time.time()

    P, F = read_stl(args.stl)
    nbr = neighbours(F, len(P))
    region, nn = planar_regions(P, F, nbr, args.plane_tol)
    nreg = region.max() + 1
    members = [[] for _ in range(nreg)]
    for t, r in enumerate(region):
        members[r].append(t)
    print(f"{len(F)} triangles, {len(P)} vertices -> {nreg} faces ({time.time() - t0:.1f} s)")

    # planes, boundary loops and the deviation each vertex needs as tolerance
    dev = np.zeros(len(P))
    faces = []  # (origin, normal, [outer, holes...])
    unmerged = 0
    for rid, tris in enumerate(members):
        if len(tris) == 1:
            t = tris[0]
            faces.append((P[F[t, 0]], nn[t], [list(F[t])], rid))
            continue
        vids = np.unique(F[tris])
        origin, n = fit_plane(P[vids], nn[tris[0]])
        loops, xd, yd = region_loops(P, F, nbr, region, tris, rid, n)
        areas = [signed_area(P, l, xd, yd) for l in loops]
        if sum(a > 0 for a in areas) != 1:  # not a single outer loop: keep the triangles separate
            unmerged += len(tris)
            for t in tris:
                faces.append((P[F[t, 0]], nn[t], [list(F[t])], rid))
            continue
        loops = [loops[int(np.argmax(areas))]] + [l for l, a in zip(loops, areas) if a <= 0]
        bv = np.unique(np.concatenate(loops))
        dev[bv] = np.maximum(dev[bv], np.abs((P[bv] - origin) @ n))
        faces.append((origin, n, loops, rid))
    print(f"max vertex distance from its merged plane: {dev.max():.3g} mm; triangles left unmerged: {unmerged}")

    # topology: shared vertices and straight edges, tolerances covering the deviation above
    B = BRep_Builder()
    edges_needed = {}
    for _, _, loops, _ in faces:
        for l in loops:
            for i, j in zip(l, l[1:] + l[:1]):
                edges_needed[(min(i, j), max(i, j))] = None
    tolE = {e: max(1e-7, 1.5 * max(dev[e[0]], dev[e[1]])) for e in edges_needed}
    tolV = np.full(len(P), 1e-7)
    for (i, j), t in tolE.items():
        tolV[i] = max(tolV[i], t)
        tolV[j] = max(tolV[j], t)
    V = {}
    for i in {v for e in edges_needed for v in e}:
        v = TopoDS_Vertex()
        B.MakeVertex(v, gp_Pnt(*P[i]), tolV[i])
        V[i] = v
    for e in edges_needed:
        edge = BRepBuilderAPI_MakeEdge(V[e[0]], V[e[1]]).Edge()
        B.UpdateEdge(edge, tolE[e])
        edges_needed[e] = edge

    shell = TopoDS_Shell()
    B.MakeShell(shell)
    for origin, n, loops, rid in faces:
        face = TopoDS_Face()
        B.MakeFace(face, Geom_Plane(gp_Ax3(gp_Pnt(*origin), gp_Dir(*n))), 1e-7)
        for l in loops:
            w = TopoDS_Wire()
            B.MakeWire(w)
            for i, j in zip(l, l[1:] + l[:1]):
                e = edges_needed[(min(i, j), max(i, j))]
                B.Add(w, e if i < j else e.Reversed())
            w.Closed(True)
            B.Add(face, w)
        B.Add(shell, face)
    shell.Closed(True)
    solid = TopoDS_Solid()
    B.MakeSolid(solid)
    B.Add(solid, shell)
    print(f"built {len(faces)} faces, {len(edges_needed)} edges, {len(V)} vertices ({time.time() - t0:.1f} s)")

    ok = BRepCheck_Analyzer(solid).IsValid()
    print(f"BRepCheck valid: {ok} ({time.time() - t0:.1f} s)")
    if not ok:
        raise SystemExit("invalid solid, not writing")

    w = STEPControl_Writer()  # the settings below only exist once a writer has been created
    for key, val in [("write.step.schema", "AP214IS"), ("write.step.unit", "MM"),
                     ("write.step.product.name", args.name)]:
        assert Interface_Static.SetCVal_s(key, val), key
    # no 2D copies of every edge (pcurves): on planes they are redundant, and they triple the file size;
    # declare the largest tolerance in the shape as the file's uncertainty
    for key, val in [("write.surfacecurve.mode", 0), ("write.precision.mode", 1)]:
        assert Interface_Static.SetIVal_s(key, val), key
    w.Transfer(solid, STEPControl_StepModelType.STEPControl_AsIs)
    w.CleanDuplicateEntities()  # one CARTESIAN_POINT per vertex, not one per edge and face as well
    if w.Write(args.step) != IFSelect_ReturnStatus.IFSelect_RetDone:
        raise SystemExit("STEP write failed")
    print(f"wrote {args.step} ({time.time() - t0:.1f} s)")

    if args.regions:
        merged = np.array([len(m) > 1 for m in members])
        np.savez_compressed(args.regions, P=P, F=F, region=region, merged=merged)


if __name__ == "__main__":
    main()
