"""Build a B-rep solid from the segmented mesh: one face per region on its fitted surface.
Usage: build.py seg.pkl out.step"""
import pickle
import sys
import time
from collections import defaultdict

import numpy as np

sys.path.insert(0, __import__("os").path.dirname(__file__))
from fit import dist, normal  # noqa: E402
from stl_to_step import neighbours  # noqa: E402

from OCP.BRep import BRep_Builder  # noqa: E402
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge  # noqa: E402
from OCP.BRepCheck import BRepCheck_Analyzer  # noqa: E402
from OCP.BRepGProp import BRepGProp  # noqa: E402
from OCP.GProp import GProp_GProps  # noqa: E402
from OCP.Geom import (Geom_CylindricalSurface, Geom_Plane, Geom_SphericalSurface,  # noqa: E402
                      Geom_ToroidalSurface, Geom_ConicalSurface, Geom_Circle, Geom_Line)
from OCP.GeomAPI import GeomAPI_Interpolate  # noqa: E402
from OCP.ShapeFix import ShapeFix_Shape  # noqa: E402
from OCP.OCP.collections import HArray1_gp_Pnt as TColgp_HArray1OfPnt  # noqa: E402
from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX  # noqa: E402
from OCP.TopExp import TopExp_Explorer  # noqa: E402
from OCP.TopoDS import TopoDS_Face, TopoDS_Shell, TopoDS_Solid, TopoDS_Vertex, TopoDS_Wire  # noqa: E402
from OCP.gp import gp_Ax2, gp_Ax3, gp_Circ, gp_Dir, gp_Pnt  # noqa: E402

TOL_FIT = 5e-5
t0 = time.time()
d = pickle.load(open(sys.argv[1], "rb"))
P, F, label, models, nn = d["P"], d["F"], d["label"].copy(), d["models"], d["nn"]
nbr = neighbours(F, len(P))
a_, b_, c_ = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]
cen = (a_ + b_ + c_) / 3

# ---- merge adjacent regions that lie on the same surface
parent = list(range(len(models)))


def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


pairs = set()
for t in range(len(F)):
    for u in nbr[t]:
        if label[t] < label[u]:
            pairs.add((label[t], label[u]))
verts_of = defaultdict(set)
for t in range(len(F)):
    verts_of[label[t]].update(F[t].tolist())
tris_of = defaultdict(list)
for t in range(len(F)):
    tris_of[label[t]].append(t)
for i, j in sorted(pairs):
    if models[i]["type"] != models[j]["type"]:
        continue
    vj = P[list(verts_of[j])]
    vi = P[list(verts_of[i])]
    tj, ti = tris_of[j], tris_of[i]
    if (np.abs(dist(models[i], vj)).max() < TOL_FIT and np.abs(dist(models[j], vi)).max() < TOL_FIT
            and (np.abs(np.sum(normal(models[i], cen[tj]) * nn[tj], 1)) > 0.99).all()):
        parent[find(j)] = find(i)
roots = sorted({find(i) for i in range(len(models)) if len(tris_of[i])})
newid = {r: k for k, r in enumerate(roots)}
label = np.array([newid[find(l)] for l in label])
models = [models[r] for r in roots]
nreg = len(models)
print(f"{nreg} faces after merging ({time.time()-t0:.1f}s)")

# ---- boundary half-edges and loops per region
out = defaultdict(list)  # (region, v) -> list of (w, other_region)
for t in range(len(F)):
    for k in range(3):
        u = nbr[t, k]
        if label[u] != label[t]:
            out[(label[t], F[t, k])].append((F[t, (k + 1) % 3], label[u]))
vreg = defaultdict(set)
for t in range(len(F)):
    for v in F[t]:
        vreg[v].add(label[t])
vnorm = defaultdict(lambda: np.zeros(3))
for t in range(len(F)):
    for v in F[t]:
        vnorm[(label[t], v)] = vnorm[(label[t], v)] + nn[t]

loops = defaultdict(list)  # region -> list of loops; loop = list of (v, w, other)
by_region = defaultdict(list)
for (r, v), lst in out.items():
    by_region[r].append(v)
for r in range(nreg):
    pending = {v: list(out[(r, v)]) for v in by_region[r]}
    while any(pending.values()):
        start = next(v for v, l in pending.items() if l)
        loop = []
        prev, cur = None, start
        while True:
            cands = pending[cur]
            if len(cands) == 1 or prev is None:
                pick = cands[0]
            else:
                n = vnorm[(r, cur)]
                n = n / np.linalg.norm(n)
                xd = P[prev] - P[cur]
                xd = xd - (xd @ n) * n
                xd /= np.linalg.norm(xd)
                yd = np.cross(n, xd)
                best = None
                for cnd in cands:
                    dv = P[cnd[0]] - P[cur]
                    ang = (-np.arctan2(dv @ yd, dv @ xd)) % (2 * np.pi)
                    if best is None or ang < best[0]:
                        best = (ang, cnd)
                pick = best[1]
            cands.remove(pick)
            loop.append((cur, pick[0], pick[1]))
            prev, cur = cur, pick[0]
            if cur == start and not pending[start]:
                break
            if cur == start:
                break
        loops[r].append(loop)
print(f"loops traced ({time.time()-t0:.1f}s)")

# ---- split loops into chains at junction vertices / neighbour changes
chains = {}  # key -> dict(verts=[...], closed=bool)


def canon(vs, closed):
    if not closed:
        return tuple(vs) if (vs[0], vs[1]) < (vs[-1], vs[-2]) else tuple(vs[::-1])
    body = vs[:-1]
    i = int(np.argmin(body))
    rot = body[i:] + body[:i]
    if rot[1] > rot[-1]:
        rot = [rot[0]] + rot[1:][::-1]
    return tuple(rot) + (rot[0],)


face_loops = defaultdict(list)  # region -> list of [(key, forward)]
for r in range(nreg):
    for loop in loops[r]:
        n = len(loop)
        brk = [i for i in range(n) if len(vreg[loop[i][0]]) >= 3 or loop[i][2] != loop[i - 1][2]]
        segs = []
        if not brk:
            vs = [e[0] for e in loop] + [loop[0][0]]
            segs.append((vs, True))
        else:
            for bi, s in enumerate(brk):
                e_ = brk[(bi + 1) % len(brk)]
                idx = list(range(s, e_)) if e_ > s else list(range(s, n)) + list(range(0, e_))
                vs = [loop[i][0] for i in idx] + [loop[idx[-1]][1]]
                segs.append((vs, False))
        wl = []
        for vs, closed in segs:
            key = canon(vs, closed)
            if key not in chains:
                chains[key] = dict(closed=closed)
            if closed:
                # orientation: does vs run the same way as key?
                k0 = list(key[:-1])
                pos = k0.index(vs[0])
                fwd = k0[(pos + 1) % len(k0)] == vs[1]
            else:
                fwd = tuple(vs) == key
            wl.append((key, fwd))
        face_loops[r].append(wl)
print(f"{len(chains)} edges ({time.time()-t0:.1f}s)")

# ---- vertices and edge curves
B = BRep_Builder()
V = {}


def vertex(i):
    if i not in V:
        v = TopoDS_Vertex()
        B.MakeVertex(v, gp_Pnt(*P[i]), 1e-4)
        V[i] = v
    return V[i]


ntype = defaultdict(int)
E = {}
for key, ch in chains.items():
    vs = list(key)
    X = P[vs]
    closed = ch["closed"]
    p0, p1 = X[0], X[-1]
    edge = None
    if not closed:
        dvec = p1 - p0
        L = np.linalg.norm(dvec)
        if L > 0:
            u = dvec / L
            off = (X - p0) - np.outer((X - p0) @ u, u)
            if np.linalg.norm(off, axis=1).max() < 2e-5:
                edge = BRepBuilderAPI_MakeEdge(vertex(vs[0]), vertex(vs[-1])).Edge()
                ntype["line"] += 1
    if edge is None and len(vs) >= (4 if closed else 3):
        Y = X[:-1] if closed else X
        cY = Y.mean(0)
        nrm = np.linalg.svd(Y - cY, full_matrices=False)[2][2]
        if np.abs((Y - cY) @ nrm).max() < 2e-5:
            e1 = np.cross(nrm, [1.0, 0, 0] if abs(nrm[0]) < 0.9 else [0, 1.0, 0])
            e1 /= np.linalg.norm(e1)
            e2 = np.cross(nrm, e1)
            x, y = (Y - cY) @ e1, (Y - cY) @ e2
            A = np.c_[x, y, np.ones_like(x)]
            D_, E_, F_ = np.linalg.lstsq(A, -(x * x + y * y), rcond=None)[0]
            cx, cy = -D_ / 2, -E_ / 2
            rad = np.sqrt(cx * cx + cy * cy - F_)
            if np.abs(np.hypot(x - cx, y - cy) - rad).max() < 2e-5 and rad < 100:
                C = cY + cx * e1 + cy * e2
                # orient the circle so the chain runs counterclockwise
                ang = np.unwrap(np.arctan2(y - cy, x - cx))
                if ang[-1] < ang[0]:
                    nrm = -nrm
                circ = gp_Circ(gp_Ax2(gp_Pnt(*C), gp_Dir(*nrm)), rad)
                if closed:
                    edge = BRepBuilderAPI_MakeEdge(circ, vertex(vs[0]), vertex(vs[0])).Edge()
                else:
                    edge = BRepBuilderAPI_MakeEdge(circ, vertex(vs[0]), vertex(vs[-1])).Edge()
                ntype["circle"] += 1
    if edge is None:
        pts = X[:-1] if closed else X
        arr = TColgp_HArray1OfPnt(1, len(pts))
        for i, p in enumerate(pts):
            arr.SetValue(i + 1, gp_Pnt(*p))
        itp = GeomAPI_Interpolate(arr, closed, 1e-9)
        itp.Perform()
        crv = itp.Curve()
        edge = BRepBuilderAPI_MakeEdge(crv, vertex(vs[0]), vertex(vs[-1])).Edge()
        ntype["bspline"] += 1
    B.UpdateEdge(edge, 5e-5)
    E[key] = edge
print("edge curves:", dict(ntype), f"({time.time()-t0:.1f}s)")


# ---- faces
def surface(m, sign):
    t = m["type"]
    if t == "plane":
        return Geom_Plane(gp_Ax3(gp_Pnt(*m["o"]), gp_Dir(*(m["n"] * sign))))
    ax = m.get("a", np.array([0, 0, 1.0]))
    ax3 = gp_Ax3(gp_Pnt(*m["c"]), gp_Dir(*ax))
    if sign < 0:
        ax3.YReverse()
    if t == "cylinder":
        return Geom_CylindricalSurface(ax3, m["r"])
    if t == "sphere":
        return Geom_SphericalSurface(ax3, m["r"])
    if t == "torus":
        return Geom_ToroidalSurface(ax3, m["R"], m["r"])
    raise ValueError(t)


shell = TopoDS_Shell()
B.MakeShell(shell)
ftype = defaultdict(int)
for r in range(nreg):
    m = models[r]
    tr = tris_of_r = np.nonzero(label == r)[0]
    sgn = np.sign(np.sum(np.sum(normal(m, cen[tr]) * nn[tr], 1)))
    face = TopoDS_Face()
    B.MakeFace(face, surface(m, sgn), 5e-5)
    for wl in face_loops[r]:
        w = TopoDS_Wire()
        B.MakeWire(w)
        for key, fwd in wl:
            e = E[key]
            B.Add(w, e if fwd else e.Reversed())
        w.Closed(True)
        B.Add(face, w)
    B.Add(shell, face)
    ftype[m["type"]] += 1
shell.Closed(True)
solid = TopoDS_Solid()
B.MakeSolid(solid)
B.Add(solid, shell)
print("faces:", dict(ftype), f"({time.time()-t0:.1f}s)")

fix = ShapeFix_Shape(solid)
fix.SetPrecision(5e-5)
fix.SetMaxTolerance(1e-3)
fix.Perform()
shape = fix.Shape()
ok = BRepCheck_Analyzer(shape).IsValid()
props = GProp_GProps()
BRepGProp.VolumeProperties_s(shape, props)
vol = props.Mass()
props2 = GProp_GProps()
BRepGProp.SurfaceProperties_s(shape, props2)


def count(s, kind):
    ex = TopExp_Explorer(s, kind)
    n = 0
    while ex.More():
        n += 1
        ex.Next()
    return n


print(f"valid {ok}; volume {vol:.4f}; area {props2.Mass():.4f}; faces {count(shape, TopAbs_FACE)} "
      f"edges {count(shape, TopAbs_EDGE)} vertices {count(shape, TopAbs_VERTEX)} ({time.time()-t0:.1f}s)")
pickle.dump(dict(label=label, models=models), open(sys.argv[1] + ".merged", "wb"))
from OCP.BRepTools import BRepTools  # noqa: E402
BRepTools.Write_s(shape, sys.argv[2] + ".brep")

# ---- STEP
from OCP.IFSelect import IFSelect_ReturnStatus  # noqa: E402
from OCP.Interface import Interface_Static  # noqa: E402
from OCP.STEPControl import STEPControl_StepModelType, STEPControl_Writer  # noqa: E402

if not ok:
    raise SystemExit("invalid solid, not writing STEP")
name = sys.argv[3] if len(sys.argv) > 3 else "Part"
w = STEPControl_Writer()
for k, v in [("write.step.schema", "AP214IS"), ("write.step.unit", "MM"), ("write.step.product.name", name)]:
    assert Interface_Static.SetCVal_s(k, v), k
w.Transfer(shape, STEPControl_StepModelType.STEPControl_AsIs)
if w.Write(sys.argv[2]) != IFSelect_ReturnStatus.IFSelect_RetDone:
    raise SystemExit("STEP write failed")
print("wrote", sys.argv[2], f"({time.time()-t0:.1f}s)")
