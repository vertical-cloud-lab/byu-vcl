#!/usr/bin/env python3
"""Read the STEP back and compare it with the STL. Optionally render a preview.

Usage: python check.py part.step part.stl [preview.png]
"""
import sys
import time
from collections import Counter

import numpy as np
import trimesh
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.Bnd import Bnd_Box
from OCP.GeomAbs import GeomAbs_CurveType, GeomAbs_SurfaceType
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_ReturnStatus
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_REVERSED, TopAbs_SOLID, TopAbs_VERTEX
from OCP.TopExp import TopExp
from OCP.TopLoc import TopLoc_Location
from OCP.OCP.collections import IndexedMap_TopoDS_Shape_TopTools_ShapeMapHasher as TopTools_IndexedMapOfShape
from OCP.TopoDS import TopoDS

t0 = time.time()
rd = STEPControl_Reader()
assert rd.ReadFile(sys.argv[1]) == IFSelect_ReturnStatus.IFSelect_RetDone
rd.TransferRoots()
shape = rd.OneShape()
print(f"read {sys.argv[1]} in {time.time() - t0:.1f} s")


def unique(kind):
    m = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, kind, m)
    return [m.FindKey(i) for i in range(1, m.Extent() + 1)]


faces, edges = unique(TopAbs_FACE), unique(TopAbs_EDGE)
print(f"topology: {len(unique(TopAbs_SOLID))} solid, {len(faces)} faces, {len(edges)} edges, "
      f"{len(unique(TopAbs_VERTEX))} vertices")
print("valid (BRepCheck):", BRepCheck_Analyzer(shape).IsValid())
SNAME = {GeomAbs_SurfaceType.GeomAbs_Plane: "plane", GeomAbs_SurfaceType.GeomAbs_Cylinder: "cylinder",
         GeomAbs_SurfaceType.GeomAbs_Sphere: "sphere", GeomAbs_SurfaceType.GeomAbs_Torus: "torus",
         GeomAbs_SurfaceType.GeomAbs_Cone: "cone"}
ftype = [SNAME.get(BRepAdaptor_Surface(TopoDS.Face(f)).GetType(), "other") for f in faces]
print("faces by surface type:", dict(Counter(ftype)))
radii = Counter()
for f, t in zip(faces, ftype):
    s = BRepAdaptor_Surface(TopoDS.Face(f))
    if t == "cylinder":
        radii[f"cylinder r={s.Cylinder().Radius():.3f}"] += 1
    elif t == "sphere":
        radii[f"sphere r={s.Sphere().Radius():.3f}"] += 1
    elif t == "torus":
        radii[f"torus R={s.Torus().MajorRadius():.3f} r={s.Torus().MinorRadius():.3f}"] += 1
for k in sorted(radii):
    print(f"  {k}: {radii[k]} faces")
CNAME = {GeomAbs_CurveType.GeomAbs_Line: "line", GeomAbs_CurveType.GeomAbs_Circle: "circle", GeomAbs_CurveType.GeomAbs_Ellipse: "ellipse",
         GeomAbs_CurveType.GeomAbs_BSplineCurve: "bspline"}
print("edges by curve type:", dict(Counter(CNAME.get(BRepAdaptor_Curve(TopoDS.Edge(e)).GetType(), "other")
                                         for e in edges)))
tol = max(BRep_Tool.Tolerance_s(TopoDS.Edge(e)) for e in edges)
print(f"largest edge tolerance: {tol:.2e} mm")

stl = trimesh.load(sys.argv[2])
g = GProp_GProps()
BRepGProp.VolumeProperties_s(shape, g)
vol = g.Mass()
g2 = GProp_GProps()
BRepGProp.SurfaceProperties_s(shape, g2)
print(f"volume: STL {stl.volume:.3f} mm3, STEP {vol:.3f} mm3 (difference {vol - stl.volume:+.3f})")
print(f"area:   STL {stl.area:.3f} mm2, STEP {g2.Mass():.3f} mm2 (difference {g2.Mass() - stl.area:+.3f})")
bb = Bnd_Box()
BRepBndLib.AddOptimal_s(shape, bb, False, False)
print("bbox STL ", np.round(stl.bounds, 4).tolist())
print("bbox STEP", np.round([[*bb.CornerMin().Coord()], [*bb.CornerMax().Coord()]], 4).tolist())

# tessellate the STEP finely and compare with the STL in both directions
BRepMesh_IncrementalMesh(shape, 0.0005, False, 0.05, True)
V, T, FT, FI = [], [], [], []
off = 0
for fi, (f, t) in enumerate(zip(faces, ftype)):
    face = TopoDS.Face(f)
    loc = TopLoc_Location()
    tri = BRep_Tool.Triangulation_s(face, loc)
    if tri is None:
        continue
    tr = loc.Transformation()
    pts = np.array([[*tri.Node(i).Transformed(tr).Coord()] for i in range(1, tri.NbNodes() + 1)])
    tt = np.array([tri.Triangle(i).Get() for i in range(1, tri.NbTriangles() + 1)]) - 1
    if face.Orientation() == TopAbs_REVERSED:
        tt = tt[:, ::-1]
    V.append(pts)
    T.append(tt + off)
    FT += [t] * len(tt)
    FI += [fi] * len(tt)
    off += len(pts)
V, T = np.vstack(V), np.vstack(T)
step_mesh = trimesh.Trimesh(V, T, process=False)
d1 = np.abs(trimesh.proximity.closest_point(stl, V)[1])
d2 = np.abs(trimesh.proximity.closest_point(step_mesh, stl.vertices)[1])
print(f"STEP surface -> STL facets: max {d1.max():.4f} mm, mean {d1.mean():.5f} mm ({len(V)} points)")
print(f"STL vertices -> STEP surface: max {d2.max():.5f} mm (STEP tessellated to 0.0005 mm)")
print(f"done in {time.time() - t0:.1f} s")

if len(sys.argv) > 3:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    SURF, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
    COL = {"plane": np.array([0x2a, 0x78, 0xd6]) / 255, "cylinder": np.array([0xc3, 0xc2, 0xb7]) / 255,
           "torus": np.array([0xe0, 0xa4, 0x58]) / 255, "sphere": np.array([0x6c, 0xb8, 0x7a]) / 255}
    EDGE = np.array([0.13, 0.13, 0.12])
    FT = np.array(FT)
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    nn = np.cross(b - a, c - a)
    nl = np.linalg.norm(nn, axis=1, keepdims=True)
    nn = nn / np.where(nl == 0, 1, nl)
    # B-rep edges as polylines
    polys = []
    for e in edges:
        cv = BRepAdaptor_Curve(TopoDS.Edge(e))
        us = np.linspace(cv.FirstParameter(), cv.LastParameter(), 60)
        polys.append(np.array([[*cv.Value(u).Coord()] for u in us]))

    def render(az, el, S=1400, pad=0.06):
        az, el = np.radians(az), np.radians(el)
        cdir = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
        r = np.cross(-cdir, [0, 0, 1.0])
        r /= np.linalg.norm(r)
        u = np.cross(r, -cdir)
        ctr = (V.max(0) + V.min(0)) / 2

        def proj(Q):
            Q = Q - ctr
            return Q @ r, Q @ u, Q @ cdir
        sx, sy, sz = proj(V)
        span = max(np.ptp(sx), np.ptp(sy)) * (1 + 2 * pad)
        X, Y = (sx / span + 0.5) * S, (0.5 - sy / span) * S
        img = np.tile(np.array([int(SURF[i:i + 2], 16) for i in (1, 3, 5)]) / 255, (S, S, 1))
        zb = np.full((S, S), -np.inf)
        L = cdir + 0.6 * u - 0.35 * r
        L /= np.linalg.norm(L)
        shade = 0.42 + 0.58 * np.clip(nn @ L, 0, 1)
        for t in np.nonzero(nn @ cdir > 0)[0]:
            i = T[t]
            xs, ys, zs = X[i], Y[i], sz[i]
            x0, x1 = max(int(xs.min()), 0), min(int(np.ceil(xs.max())), S - 1)
            y0, y1 = max(int(ys.min()), 0), min(int(np.ceil(ys.max())), S - 1)
            det = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
            if abs(det) < 1e-12 or x1 < x0 or y1 < y0:
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
            img[y0:y1 + 1, x0:x1 + 1][upd] = COL[FT[t]] * shade[t]
        for pl in polys:
            px_, py_, pz_ = proj(pl)
            xs, ys = (px_ / span + 0.5) * S, (0.5 - py_ / span) * S
            for k in range(len(pl) - 1):
                n = int(max(abs(xs[k + 1] - xs[k]), abs(ys[k + 1] - ys[k])) * 1.5) + 2
                s = np.linspace(0, 1, n)
                qx, qy = xs[k] + s * (xs[k + 1] - xs[k]), ys[k] + s * (ys[k + 1] - ys[k])
                qz = pz_[k] + s * (pz_[k + 1] - pz_[k])
                ix, iy = np.clip(qx.astype(int), 0, S - 2), np.clip(qy.astype(int), 0, S - 2)
                vis = qz >= zb[iy, ix] - 0.04
                for dx in (0, 1):
                    for dy in (0, 1):
                        img[iy[vis] + dy, ix[vis] + dx] = EDGE
        k = 2
        return img.reshape(S // k, k, S // k, k, 3).mean(axis=(1, 3))

    views = [(-55, 28, "From above"), (125, -28, "From below, opposite side")]
    fig, axes = plt.subplots(1, 2, figsize=(11, 6.2), facecolor=SURF)
    for ax, (az, el, title) in zip(axes, views):
        ax.imshow(render(az, el))
        ax.set_title(title, color=INK2, fontsize=11)
        ax.axis("off")
    cnt = Counter(ftype)
    fig.suptitle("RaspberryPiCameraMount.step: flat faces and true curved surfaces", color=INK, fontsize=13,
                 x=0.02, y=0.955, ha="left", va="center")
    labels = [("plane", "Flat"), ("cylinder", "Cylinder"), ("torus", "Torus (bend)"), ("sphere", "Sphere (corner)")]
    fig.legend(handles=[Patch(color=COL[k], label=f"{lab}: {cnt[k]} faces") for k, lab in labels],
               loc="lower left", ncol=4, frameon=False, fontsize=10, labelcolor=INK)
    fig.text(0.98, 0.955, f"{len(faces)} faces, every face outlined", color=INK2, fontsize=10, ha="right",
             va="center")
    plt.subplots_adjust(left=0.01, right=0.99, top=0.88, bottom=0.08, wspace=0.02)
    fig.savefig(sys.argv[3], dpi=110, facecolor=SURF)
    print("wrote", sys.argv[3])
