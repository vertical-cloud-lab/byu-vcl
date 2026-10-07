#!/usr/bin/env python3
"""Overhangs in the printed parts' STLs, measured on the mesh without the slicer.

    python overhangs.py   # every STL in ../exports -> overhangs.json

For each part, in the print orientation it was exported in, this measures the area of
downward-facing triangles more than 45 degrees from vertical (normal z < -cos 45). It leaves
out the faces on the bed (all three vertices within 0.05 mm of the part's lowest z) and
finds the largest edge-connected patch of what remains. Faces drawn at exactly 45 degrees,
like the carrier's gussets, are reported separately as at_limit_mm2: float32 STL normals
scatter them a few thousandths of a degree either side, so without the 0.1 degree margin
about half of each gusset would count. Horizontal hole tops and short bridges count too, so
read the numbers as where to look, not as a verdict. Bambu's own support check is in
report.json.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

HERE = Path(__file__).resolve().parent
EXPORTS = HERE.parent / "exports"
ANGLE_DEG = 45.0  # from vertical
ANGLE_TOL = 0.1   # degrees; faces within this of ANGLE_DEG are at the limit, not over it
BED_TOL = 0.05    # mm


def patch(mesh: trimesh.Trimesh, faces: np.ndarray) -> dict:
    v = mesh.vertices[mesh.faces[faces]].reshape(-1, 3)
    return {"area_mm2": round(float(mesh.area_faces[faces].sum()), 1), "triangles": len(faces),
            # flattest face in the patch, degrees from vertical (90 = a flat ceiling)
            "max_angle_deg": round(math.degrees(math.asin(min(1.0, -mesh.face_normals[faces, 2].min()))), 1),
            "bbox_mm": [round(float(c), 2) for c in (*v.min(0), *v.max(0))]}


def overhangs(stl: Path) -> dict:
    mesh = trimesh.load(stl, force="mesh")
    zmin = mesh.bounds[0, 2]
    on_bed = mesh.vertices[mesh.faces][:, :, 2].max(axis=1) <= zmin + BED_TOL
    angle = np.degrees(np.arcsin(np.clip(-mesh.face_normals[:, 2], -1, 1)))  # from vertical; 90 = ceiling
    sel = np.flatnonzero((angle > ANGLE_DEG + ANGLE_TOL) & ~on_bed)
    at_limit = (abs(angle - ANGLE_DEG) <= ANGLE_TOL) & ~on_bed
    out = {"stl": stl.name, "sha256": hashlib.sha256(stl.read_bytes()).hexdigest()[:12],
           "bbox_mm": [round(float(c), 2) for c in mesh.bounds.ravel()],
           "overhang_area_mm2": round(float(mesh.area_faces[sel].sum()), 1), "triangles": len(sel),
           "at_limit_mm2": round(float(mesh.area_faces[at_limit].sum()), 1),
           "patches": 0, "largest_patch": None, "next_largest_mm2": []}
    if len(sel):
        index = np.full(len(mesh.faces), -1)
        index[sel] = np.arange(len(sel))
        a, b = index[mesh.face_adjacency].T  # faces that share an edge
        both = (a >= 0) & (b >= 0)
        graph = coo_matrix((np.ones(both.sum()), (a[both], b[both])), shape=(len(sel), len(sel)))
        n, label = connected_components(graph, directed=False)
        areas = np.bincount(label, weights=mesh.area_faces[sel], minlength=n)
        order = np.argsort(areas)[::-1]
        out.update(patches=int(n), largest_patch=patch(mesh, sel[label == order[0]]),
                   next_largest_mm2=[round(float(areas[i]), 1) for i in order[1:3]])
    return out


def main() -> None:
    parts = {stl.stem: overhangs(stl) for stl in sorted(EXPORTS.glob("*.stl"))}
    result = {"criterion": {"angle_from_vertical_deg": ANGLE_DEG, "margin_deg": ANGLE_TOL,
                            "normal_z_below": round(-math.sin(math.radians(ANGLE_DEG + ANGLE_TOL)), 4),
                            "bed_faces_excluded_within_mm": BED_TOL},
              "parts": parts}
    (HERE / "overhangs.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"{'part':10s} {'area mm2':>9s} {'at 45':>7s} {'patches':>7s} {'largest':>8s}  largest patch bbox (x0 y0 z0 x1 y1 z1)")
    for name, r in parts.items():
        lp = r["largest_patch"] or {"area_mm2": 0, "bbox_mm": []}
        print(f"{name:10s} {r['overhang_area_mm2']:9.1f} {r['at_limit_mm2']:7.1f} {r['patches']:7d} "
              f"{lp['area_mm2']:8.1f}  {lp['bbox_mm']}")


if __name__ == "__main__":
    main()
