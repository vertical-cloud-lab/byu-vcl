"""Bambu Lab A2L, in the style of lab_models/equipment.py (#199): a parametric model from the published figures.

Bambu publishes no CAD for its printers. Published: envelope 544 x 529 x 505 mm, 12.8 kg net, build volume
330 x 320 x 325 mm (Bambu's A2L media kit, as quoted by 3D Printing Industry, 2 June 2026, and retailers). Layout:
reviews describe it as an open-frame bed slinger in the A1's design language, "an A1 that has been fed a steady diet
of protein shakes", with a "pretty beefy triangular" gantry that the base is assembled into, and a spool holder on
the gantry (Tom's Hardware, 2026). So, as on the A1: a T-shaped base with the bed sliding along y on it, a gantry
arch across the base with an upright of triangular profile at each end, the X beam and toolhead riding up and down
between them, the screen on the front of the base. Every proportion inside the envelope is read from that
description, not measured.

Frame: x to the right and y away from the viewer when facing the printer's front; z up from the bench; origin at the
centre of the footprint.
"""
from __future__ import annotations

import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent / "lab_models"))
from common import Model, box, cyl, rbox  # noqa: E402

A2L = dict(W=544.0, D=529.0, H=505.0, bed_w=330.0, bed_d=320.0, build_h=325.0, mass_kg=12.8)
SOURCE = ("Bambu's published envelope (544 x 529 x 505 mm) and build volume (330 x 320 x 325 mm); the layout is the "
          "A1's, per reviews (no CAD published)")


def a2l(gantry_z: float = 260.0, bed_y: float = 0.0) -> Model:
    p = A2L
    W, D, H = p["W"], p["D"], p["H"]
    m = Model("bambu_a2l", "Bambu Lab A2L", source=SOURCE)
    base_h = 62.0
    # base: the Y beam under the bed (front to back) and the cross base the gantry stands on
    m.add("y beam", rbox(150, D - 10, base_h, 10, y=0), "printer_grey")
    gy = 40.0                                              # gantry plane, a little behind the middle (as on the A1)
    m.add("cross base", rbox(W, 150, base_h - 6, 12, y=gy), "printer_grey")
    m.add("base trim", rbox(W - 20, 140, 6, 10, y=gy, z=base_h - 6), "printer_white")
    m.add("screen", box(W / 2 - 150, gy - 76, 12, W / 2 - 60, gy - 74.5, 52).rotate((0, gy - 75, 30), (1, gy - 75, 30), -12),
          "screen")
    # bed: carriage on the Y beam, heatbed, textured PEI plate (330 x 320 build area)
    m.add("bed carriage", box(-60, bed_y - 120, base_h, 60, bed_y + 120, base_h + 14), "printer_black")
    m.add("heatbed", rbox(p["bed_w"] + 20, p["bed_d"] + 20, 7, 8, y=bed_y, z=base_h + 14), "aluminium")
    m.add("build plate", rbox(p["bed_w"] + 8, p["bed_d"] + 8, 1.2, 6, y=bed_y, z=base_h + 21), "pei")
    # gantry arch: two uprights of triangular profile (wide at the foot, narrow at the top) and a top beam
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (W / 2 - 4), sx * (W / 2 - 56)))
        prof = (cq.Workplane("YZ").polyline([(gy - 75, base_h - 6), (gy + 75, base_h - 6), (gy + 24, H - 30),
                                              (gy - 24, H - 30)]).close().extrude(x1 - x0).translate((x0, 0, 0)))
        m.add(f"upright {'LR'[sx > 0]}", prof, "printer_white")
        m.add(f"z screw {'LR'[sx > 0]}", cyl(10, H - base_h - 60, x=sx * (W / 2 - 64), y=gy + 6, z=base_h + 10), "steel")
    m.add("top beam", box(-W / 2 + 4, gy - 24, H - 34, W / 2 - 4, gy + 24, H), "printer_white")
    m.add("top cap", box(-W / 2 + 4, gy - 26, H - 6, W / 2 - 4, gy + 26, H), "printer_grey")
    # X beam with the toolhead in front of it, at gantry_z (nozzle about 75 mm under the beam's top)
    m.add("x beam", box(-W / 2 + 56, gy - 22, gantry_z, W / 2 - 56, gy + 6, gantry_z + 34), "aluminium")
    for sx in (-1, 1):
        m.add(f"z carriage {'LR'[sx > 0]}", box(sx * (W / 2 - 92) - 36, gy - 30, gantry_z - 18, sx * (W / 2 - 92) + 36,
                                                 gy + 22, gantry_z + 52), "printer_grey")
    th = 30.0
    m.add("toolhead", rbox(70, 58, 112, 8, x=th, y=gy - 52, z=gantry_z - 72), "printer_white")
    m.add("toolhead front", box(th - 30, gy - 82, gantry_z - 50, th + 30, gy - 80.5, gantry_z + 26), "printer_grey")
    m.add("hotend", cyl(12, 14, x=th, y=gy - 52, z=gantry_z - 86), "brass")
    # spool holder stub on the top beam's right end, as on the A1 (the spool itself is left off: it isn't in the
    # published envelope)
    m.add("spool holder", box(W / 2 - 90, gy - 8, H - 30, W / 2 - 74, gy + 70, H - 16), "printer_grey")
    m.notes = {"envelope_mm": [W, D, H], "build_volume_mm": [p["bed_w"], p["bed_d"], p["build_h"]],
               "mass_kg": p["mass_kg"]}
    return m


if __name__ == "__main__":
    mod = a2l()
    bb = cq.Compound.makeCompound([pt.shape for pt in mod.parts]).BoundingBox()
    print(len(mod.parts), "parts; bbox", round(bb.xlen), round(bb.ylen), round(bb.zlen))
