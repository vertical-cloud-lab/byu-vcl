#!/usr/bin/env python3
"""Read a STEP file back and compare it with the STL it was made from.

Usage: python check_step.py part.step part.stl   (cadquery-ocp 8.0)
"""
import sys
import time

import numpy as np
from OCP.BRep import BRep_Tool
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_ReturnStatus
from OCP.ShapeAnalysis import ShapeAnalysis_ShapeTolerance
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_ShapeEnum as T
from OCP.TopExp import TopExp
from OCP.TopoDS import TopoDS
from OCP.OCP.collections import IndexedDataMap_TopoDS_Shape_List_TopoDS_Shape_TopTools_ShapeMapHasher as TopTools_IndexedDataMapOfShapeListOfShape
from OCP.OCP.collections import IndexedMap_TopoDS_Shape_TopTools_ShapeMapHasher as TopTools_IndexedMapOfShape

t0 = time.time()
step, stl = sys.argv[1], sys.argv[2]
r = STEPControl_Reader()
assert r.ReadFile(step) == IFSelect_ReturnStatus.IFSelect_RetDone
r.TransferRoots()
shape = r.OneShape()
print(f"read in {time.time() - t0:.1f} s")


def count(kind):
    m = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, kind, m)
    return m


counts = {k: count(getattr(T, f"TopAbs_{k}")).Extent() for k in ["SOLID", "SHELL", "FACE", "EDGE", "VERTEX"]}
print("topology:", counts)
print("valid (BRepCheck):", BRepCheck_Analyzer(shape).IsValid())
ef = TopTools_IndexedDataMapOfShapeListOfShape()
TopExp.MapShapesAndAncestors_s(shape, T.TopAbs_EDGE, T.TopAbs_FACE, ef)
uses = [ef.FindFromIndex(i).Extent() for i in range(1, ef.Extent() + 1)]
print("edges not shared by exactly 2 faces:", sum(u != 2 for u in uses))
print("max tolerance (mm):", ShapeAnalysis_ShapeTolerance().Tolerance(shape, 1))
g = GProp_GProps()
BRepGProp.VolumeProperties_s(shape, g)
vol = g.Mass()
g2 = GProp_GProps()
BRepGProp.SurfaceProperties_s(shape, g2)
area = g2.Mass()
vm = count(T.TopAbs_VERTEX)
SV = np.array([[c for c in (lambda p: (p.X(), p.Y(), p.Z()))(BRep_Tool.Pnt_s(TopoDS.Vertex(vm.FindKey(i))))]
               for i in range(1, vm.Extent() + 1)])

raw = open(stl, "rb").read()
n = int(np.frombuffer(raw, "<u4", 1, 80)[0])
v = np.frombuffer(raw, np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]), n, 84)["v"]
P = np.unique(v.reshape(-1, 3), axis=0).astype(np.float64)
a, b, c = (v[:, k].astype(np.float64) for k in range(3))
svol = np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6
sarea = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1).sum()

# match every STEP vertex to its nearest STL vertex (grid hash on 0.01 mm cells)
cell = {}
for i, p in enumerate(P):
    cell.setdefault(tuple(np.floor(p / 0.01).astype(int)), []).append(i)
dmax, matched = 0.0, set()
for p in SV:
    k = np.floor(p / 0.01).astype(int)
    cand = [i for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)
            for i in cell.get((k[0] + dx, k[1] + dy, k[2] + dz), [])]
    d = np.linalg.norm(P[cand] - p, axis=1)
    dmax = max(dmax, d.min())
    matched.add(cand[int(d.argmin())])
print(f"STL: {len(P)} vertices, volume {svol:.6f} mm3, area {sarea:.6f} mm2")
print(f"STEP: {len(SV)} vertices, volume {vol:.6f} mm3, area {area:.6f} mm2")
print(f"volume difference {vol - svol:.3e} mm3, area difference {area - sarea:.3e} mm2")
print(f"STEP vertices matching an STL vertex: {len(matched)} of {len(SV)}; largest distance {dmax:.3e} mm")
print("bbox STL ", P.min(0), P.max(0))
print("bbox STEP", SV.min(0), SV.max(0))
print(f"done in {time.time() - t0:.1f} s")
