#!/usr/bin/env python3
"""Build every model: STEP (and STL for the printable holders) into ../exports, an index in
../exports/models.json, and with --render the PNGs in ../renders.

    python vendor.py                                                  # optional: warm the vendor cache
    python build.py                                                   # exports only
    xvfb-run -a -s "-screen 0 1920x1080x24" python build.py --render  # exports and renders
"""
from __future__ import annotations

import argparse
import json
import time

import cadquery as cq

import equipment
import labware
import room
import sandbox
import vendor
from common import EXPORTS, RENDERS, Model, export, write_json

GROUPS = ("tier1", "tier2", "extra", "station")


def lineup(cat: dict[str, Model], gap: float = 25.0, row_width: float = 1400.0) -> Model:
    """Every sandbox object on one grid, grouped as in docs/sandbox-object-set.md (Tier 1 at
    the back), part names prefixed with the object's key."""
    m = Model("labware_lineup", "Sandbox objects, all together", source="see the per-object rows")
    y = 0.0
    for group in GROUPS:
        models = [mm for mm in cat.values() if mm.notes.get("group") == group]
        rows, row, width = [], [], 0.0
        for mm in models:
            w = mm.bbox().xlen
            if row and width + w > row_width:
                rows.append(row)
                row, width = [], 0.0
            row.append(mm)
            width += w + gap
        rows.append(row)
        for row in rows:
            depth = max(mm.bbox().ylen for mm in row)
            x = 0.0
            for mm in row:
                bb = mm.bbox()
                for p in mm.moved(x - bb.xmin, y - bb.center.y).parts:
                    m.add(f"{mm.key} - {p.name}", p.shape, p.material)
                x += bb.xlen + gap
            y -= depth + gap
        y -= gap * 3
    return m


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--onshape", action="store_true",
                    help="also write exports/onshape/, the scene STEPs with AgileX's and Opentrons' geometry in them")
    ap.add_argument("--only", nargs="*", help="labware, equipment, sandbox, room")
    args = ap.parse_args()
    groups = args.only or ["labware", "equipment", "sandbox", "room"]
    t0 = time.time()
    index: dict = {}
    cat = labware.catalog()
    if "labware" in groups:
        for key, m in cat.items():
            index[key] = export(m, EXPORTS / "labware", stl=m.notes.get("group") == "station" and "our design" in m.source)
        lu = lineup(cat)
        index[lu.key] = export(lu, stl=False)
    eq = {}
    if {"equipment", "sandbox", "room"} & set(groups):
        eq = {m.key: m for m in [equipment.a1_mini(), equipment.h2d(), equipment.cubxl(), equipment.drop_tower(),
                                 equipment.atomizer()]}
    if "equipment" in groups:
        for key, m in eq.items():
            index[key] = export(m, stl=False)
        for f in (vendor.ot2, vendor.piper):      # not exported: vendor geometry stays in .cache
            m = f()
            index[m.key] = {"title": m.title, "source": m.source, "parts": len(m.parts), **m.notes}
    if "sandbox" in groups:
        sb = sandbox.layout(cat, with_vendor=False)
        index[sb.key] = export(sb, stl=False)
    rm = None
    if "room" in groups:
        rm = room.cb154(eq)
        index[rm.key] = export(rm, stl=False)
    if args.onshape:                 # vendor geometry: uploaded to Onshape, never committed
        # The room gets Opentrons' OT-2. AgileX's arm stays an envelope there: re-exported, its
        # 42 MB STEP grows to ~100 MB, so in Onshape it goes into the sandbox as an assembly instead.
        export(room.cb154(eq, {"opentrons_ot2": vendor.ot2()}), EXPORTS / "onshape")
    old = EXPORTS / "models.json"               # --only rebuilds merge into the existing index
    if args.only and old.exists():
        index = {**json.loads(old.read_text()), **index}
    write_json(old, index)
    print(f"exported {len(index)} models in {time.time() - t0:.0f} s")
    if args.render:
        import renders
        renders.all_renders(cat, eq, rm)
        print(f"rendered in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
