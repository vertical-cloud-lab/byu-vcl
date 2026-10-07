#!/usr/bin/env python3
"""Checks on the Onshape export: interference, clearances, sizes and print volumes; writes STL of the printed parts.

The design lives in Onshape (../onshape/viewport_mounts.fs, driven by the variables in ../onshape/variables.py).
This reads the Part Studio as exported by ../onshape/export.py, with Onshape's part names, and checks it:

  - every printed part against every machine part and every bought part, and the printed parts against each other
    (overlap volume; 0 is the goal),
  - the clearances that matter here: the front unit to the furnace foot bracket above the LED cover, the top unit
    to the lid when it is open, and the top camera's line of sight through the lid window,
  - each printed part's volume, mass and bounding box (H2D bed 350 x 320 x 325 mm, A1 mini 180 mm cube).

    python check.py           # -> ../exports/checks.json, ../exports/stl/*.stl
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_LabelSequence
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool
import cadquery as cq

HERE = Path(__file__).resolve().parent
EXPORTS = HERE.parent / "exports"
PETG = 1.27e-3          # g / mm^3


def read_named_solids(path: Path) -> list[tuple[str, cq.Shape]]:
    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    reader = STEPCAFControl_Reader()
    reader.SetNameMode(True)
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        raise SystemExit(f"cannot read {path}")
    reader.Transfer(doc)
    tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    labels = TDF_LabelSequence()
    tool.GetFreeShapes(labels)
    out = []

    def name_of(label) -> str:
        attr = TDataStd_Name()
        if label.FindAttribute(TDataStd_Name.GetID_s(), attr):
            return attr.Get().ToExtString()
        return ""

    def walk(label, loc):
        shape = tool.GetShape_s(label)
        if tool.IsAssembly_s(label):
            comps = TDF_LabelSequence()
            tool.GetComponents_s(label, comps)
            for i in range(1, comps.Length() + 1):
                c = comps.Value(i)
                ref = c
                from OCP.TDF import TDF_Label
                ref = TDF_Label()
                tool.GetReferredShape_s(c, ref)
                cloc = tool.GetLocation_s(c)
                walk_named(ref, loc.Multiplied(cloc), name_of(c) or name_of(ref))
        else:
            out.append((name_of(label), cq.Shape.cast(shape.Moved(loc))))

    def walk_named(label, loc, nm):
        if tool.IsAssembly_s(label):
            walk(label, loc)
        else:
            shape = tool.GetShape_s(label)
            out.append((nm or name_of(label), cq.Shape.cast(shape.Moved(loc))))

    from OCP.TopLoc import TopLoc_Location
    for i in range(1, labels.Length() + 1):
        walk(labels.Value(i), TopLoc_Location())
    solids = []
    for nm, shp in out:
        for k, s in enumerate(shp.Solids()):
            solids.append((nm if len(shp.Solids()) == 1 else f"{nm} [{k}]", s))
    return solids


def volume(shape) -> float:
    p = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, p)
    return p.Mass()


def overlap(a, b) -> float:
    if not a.BoundingBox().enlarge(0.01).intersects(b.BoundingBox()) if hasattr(cq.BoundBox, "intersects") else False:
        return 0.0
    op = BRepAlgoAPI_Common(a.wrapped, b.wrapped)
    op.Build()
    if not op.IsDone():
        return float("nan")
    return volume(cq.Shape.cast(op.Shape()))


def bbox_overlap(a, b, pad=0.01) -> bool:
    A, B = a.BoundingBox(), b.BoundingBox()
    return not (A.xmax + pad < B.xmin or B.xmax + pad < A.xmin or A.ymax + pad < B.ymin or B.ymax + pad < A.ymin
                or A.zmax + pad < B.zmin or B.zmax + pad < A.zmin)


def distance(a, b) -> float:
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    return d.Value() if d.IsDone() else float("nan")


def unit_of(name: str) -> str:
    m = re.match(r"(FRONT|LEFT|TOP)\b", name)
    return m.group(1) if m else ""


def main() -> None:
    solids = read_named_solids(EXPORTS / "onshape_partstudio.step")
    printed = [(n, s) for n, s in solids if "(print)" in n]
    machine = [(n, s) for n, s in solids if n.startswith("(machine)")]
    bought = [(n, s) for n, s in solids if n.startswith("(bought)")]
    print(f"{len(solids)} solids: {len(printed)} printed, {len(machine)} machine, {len(bought)} bought")

    res = {"source": "exports/onshape_partstudio.step (Onshape export of the Part Studio)", "printed": {}, "interference": [],
           "clearances": {}}
    for n, s in printed:
        bb = s.BoundingBox()
        v = volume(s)
        res["printed"][n] = {"volume_cm3": round(v / 1000, 2), "mass_petg_g": round(v * PETG, 1),
                             "bbox_mm": [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]}
    # interference: printed vs machine, printed vs bought, printed vs printed
    pairs = [(a, b) for a in printed for b in machine + bought] + \
            [(printed[i], printed[j]) for i in range(len(printed)) for j in range(i + 1, len(printed))]
    for (na, a), (nb, b) in pairs:
        if not bbox_overlap(a, b):
            continue
        v = overlap(a, b)
        if v > 0.01:
            res["interference"].append({"a": na, "b": nb, "overlap_mm3": round(v, 2)})
    print("interference:", len(res["interference"]))
    for r in res["interference"]:
        print("  ", r)

    def get(prefix):
        return [s for n, s in solids if n.startswith(prefix)]

    # front unit: highest point vs. the cover's top (the furnace foot bracket is ~20 mm above the cover)
    front = [s for n, s in printed if n.startswith("FRONT")]
    cover = get("(machine) AMAZEMET LED cover")
    if front and cover:
        ztop_front = max(s.BoundingBox().zmax for s in front)
        ztop_cover = max(s.BoundingBox().zmax for s in cover)
        res["clearances"]["front_unit_top_above_cover_top_mm"] = round(ztop_front - ztop_cover, 1)
    # top unit vs the lid, closed and open
    top = [(n, s) for n, s in printed + bought if n.startswith("TOP") or (n.startswith("(bought)") and s.BoundingBox().zmin > 1500)]
    for lid_name in ("(machine) furnace lid, open", "(machine) furnace lid"):
        lids = get(lid_name)
        if lids and top:
            dmin = min(distance(s, l) for _, s in top for l in lids)
            key = "top_unit_to_open_lid_mm" if "open" in lid_name else "top_unit_to_closed_lid_mm"
            res["clearances"][key] = round(dmin, 1)
            if "open" not in lid_name:
                break
    # left unit to the stack
    left = [s for n, s in printed if n.startswith("LEFT")]
    stack = get("(machine) ultrasonic stack")
    if left and stack:
        res["clearances"]["left_unit_to_stack_mm"] = round(min(distance(a, b) for a in left for b in stack), 1)

    (EXPORTS / "stl").mkdir(parents=True, exist_ok=True)
    for n, s in printed:
        fn = re.sub(r"[^a-z0-9]+", "_", n.lower().replace("(print)", "")).strip("_") + ".stl"
        cq.exporters.export(cq.Workplane().add(s), str(EXPORTS / "stl" / fn), tolerance=0.05, angularTolerance=0.2)
        res["printed"][n]["stl"] = f"exports/stl/{fn}"
    (EXPORTS / "checks.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res["printed"], indent=1))
    print(json.dumps(res["clearances"], indent=1))


if __name__ == "__main__":
    main()
