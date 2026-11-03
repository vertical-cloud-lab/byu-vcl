"""The vertical cloud lab with its characterization instruments, and the backup layout: the alloy equipment in a line
with the VLM, all facing the same way, along a floor rail for the arm (#303).

    xvfb-run -a python3 line.py            # -> out/vlm_line.gif, out/mp4/vlm_line.mp4, out/vlm_line_still.png

What fits through the opening (727.5 mm of product height, Kardex's order sheet) goes on three more trays, D, E and F,
in the three storage slots round 2 left free. What doesn't stands in the line: the floor Instron, the tabletop
Instron, the wire EDM and the glovebox, with the rePowder atomizer and the Aconity MIDI. The rail is the backup to the
mobile base: a Vention rack-and-pinion seventh axis along the fronts, the UR10e on a pedestal on its carriage, parked
where the MiR250 parks. It is not used by any workflow yet.

Builds on ``animate.Lab`` (round 2's scene: the VLM, trays A-C and their equipment, the rePowder) and ``tour.Rig``
(the instruments and their moving pieces).
"""
from __future__ import annotations

import sys

import numpy as np
import pyvista as pv

import animate as A
import instruments as I
import lab
import tour
import vlm as V
from scene import FPS, Scene, T, R

TITLE = "Vertical cloud lab: the characterization trays and the alloy line"
Y_FACE = -V.UNIT_D / 2 - V.SKIN                 # the VLM's front face; every machine in the line has its front here
EXTRA = {"D": ("R1", "microscopy and diffraction"), "E": ("R4", "mechanical testing"),
         "F": ("F2", "sample prep, heat treatment, particle size")}
# what goes on each new tray, in the tray's frame (centre of its floor, y to the back): (instrument key, x, y, rz)
TRAY_LOADS = {
    "D": [("sem", -820.0, 0.0, 0.0), ("xrd", -170.0, 0.0, 0.0), ("openflexure_v7", 380.0, -200.0, 0.0),
          ("openflexure_delta", 700.0, -200.0, 0.0)],
    "E": [("pip", -650.0, 0.0, 0.0), ("nanoindenter", 350.0, 0.0, 0.0)],
    "F": [("polisher", -780.0, 0.0, 0.0), ("furnace", -150.0, 0.0, 0.0), ("mastersizer", 650.0, 0.0, 0.0)],
}
# along the line, x of each machine's centre; fronts at Y_FACE (the rePowder stays where round 2 put it)
LINE = {"glovebox": -6300.0, "instron_small": 2350.0, "instron_floor": 3550.0, "wire_edm": 5400.0}
RAIL_Y = A.AMR_XY[1] + A.ARM_LOCAL[1]          # the arm's base over the same spot as on the MiR250
RAIL_X = (-7600.0, 7000.0)


def add_tray(sc: Scene, L: A.Lab, k: str):
    slot, role = EXTRA[k]
    V.TRAYS[k] = dict(kind="extra", role=role)
    A.HOME[k] = slot
    A.ROLE[k] = role
    for name, (shape, mat, group) in {**V.tray(k), **V.lamp(k)}.items():
        e = lab._entry(lab.to_mesh(shape.val() if hasattr(shape, "val") else shape, 2.0), mat, group)
        sc.add(name, e["mesh"], e["color"], group, opacity=e["opacity"])
    L.tray[k] = [*V.SLOTS[slot]]
    L.where[k] = slot
    L.eq_groups[k] = []


def build(name: str, data: dict, idata: dict) -> tuple[Scene, A.Lab, dict]:
    sc = Scene(name, TITLE)
    sc.cam = list(A.CAM_WIDE)
    L = A.Lab(sc, data, robot=False)
    rigs = {}
    for k, loads in TRAY_LOADS.items():
        add_tray(sc, L, k)
        for key, x, y, rz in loads:
            if key not in idata:
                continue
            inst, ents = idata[key]
            x0, x1, y0, y1, z0, _ = inst.bbox()
            at = T((x, y, V.T_FLOOR)) @ R((0, 0, 1), rz) @ T((-(x0 + x1) / 2, -(y0 + y1) / 2, -z0))
            rigs[key] = tour.Rig(sc, inst, ents, f"{k}_{key}:", at=at, parent=f"tray_{k}")
            L.eq_groups[k].append(f"{k}_{key}:body")
    for key, x in LINE.items():
        if key not in idata:
            continue
        inst, ents = idata[key]
        x0, x1, y0, y1, z0, _ = inst.bbox()
        at = T((x, Y_FACE - y0 - (y1 - y0), 0)) @ T((-(x0 + x1) / 2, -(y0 + y1) / 2 + (y1 - y0) / 2, -z0))
        rigs[key] = tour.Rig(sc, inst, ents, f"line_{key}:", at=at)
    if "rail" in idata:
        inst, ents = idata["rail"]
        rigs["rail"] = tour.Rig(sc, inst, ents, "rail:", at=T(((RAIL_X[0] + RAIL_X[1]) / 2, RAIL_Y, 0)))
    L.apply_state()
    return sc, L, rigs


if __name__ == "__main__":
    data = lab.meshes()
    idata = tour.load()
    sc, L, rigs = build("vlm_line", data, idata)
    sc.cam = list(A.CAM_WIDE)
    img = sc.render_base()
    from PIL import Image
    Image.fromarray(img).save("/tmp/line_test.png")
    print("ok")
