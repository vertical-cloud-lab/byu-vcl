#!/usr/bin/env python3
"""Check the mount against Opentrons' own OT-2 model, slot by slot, and render it in place.

Opentrons publishes a STEP model of the OT-2 at github.com/Opentrons/ot2. It has
no licence file, so it is downloaded into .cache/ at run time rather than
committed here. From it this script

  * confirms the lid geometry the design depends on (window thickness, deck to
    window height, pipette-head clearance under the window),
  * places the mount over every deck slot and checks it against the robot's frame,
  * works out where to mark the lid for each slot, and the camera's field of view,
  * renders the mount on the robot and a simulated camera view of a plate.

    xvfb-run -a -s "-screen 0 1920x1080x24" python ot2_context.py [--slot 5] [--focal 25]

Coordinates: the Opentrons deck frame has x to the right, y toward the back and z
up, with the origin at the front-left corner of slot 1. The reference STEP is Y-up
with +Z toward the front:
    x_deck = X + 196.5,   y_deck = 214.525 - Z,   z_deck = Y - 53.55
"""
from __future__ import annotations

import argparse
import json
import math
import urllib.request
from pathlib import Path

import cadquery as cq
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer

from lid_mount import ASSEMBLY, EXPORTS, Params, box, build, overlap

HERE = Path(__file__).resolve().parent
RENDERS = HERE.parent / "renders"
URL = ("https://raw.githubusercontent.com/Opentrons/ot2/master/reference-model/STEP/"
       "OT-2%20Reference%20Model%20Detailed.STEP")
CACHE = HERE / ".cache" / "OT-2 Reference Model Detailed.STEP"

DECK_Y = 53.55            # deck surface in the STEP (largest upward face of REMOVABLE DECK)
X0, Z0 = 196.5, 214.525   # STEP origin in deck coordinates
SENSOR = (6.287, 4.712)   # IMX477 active area, mm
PLATE = (127.76, 85.48, 14.35)   # SBS 96-well footprint and height
PUPIL_IN_LENS = 20.0      # estimate: entrance pupil behind the lens front; shifts the FOV ~3 %

# Slot centres in deck coordinates: 3 across (132.5 mm pitch), 4 deep (90.5 mm).
SLOTS = {n: (((n - 1) % 3) * 132.5 + 64.0, ((n - 1) // 3) * 90.5 + 43.0) for n in range(1, 12)}
CONTEXT = ("TOP WINDOW", "OT-2 FRAME", "REMOVABLE DECK", "LEFT WINDOW", "RIGHT WINDOW",
           "REAR WINDOW", "WINDOW FRAME LEFT", "WINDOW FRAME RIGHT", "DOOR TOP", "DOOR BOTTOM")


def fetch() -> Path:
    if not CACHE.exists():
        CACHE.parent.mkdir(exist_ok=True)
        print("downloading the OT-2 reference model from github.com/Opentrons/ot2 ...")
        urllib.request.urlretrieve(URL, CACHE)
    return CACHE


def load_solids(path: Path) -> dict[str, cq.Solid]:
    reader = STEPControl_Reader()
    reader.ReadFile(str(path))
    reader.TransferRoots()
    names = reader.WS().TransferReader()
    out = {}
    exp = TopExp_Explorer(reader.OneShape(), TopAbs_SOLID)
    while exp.More():
        shape = exp.Current()
        out[names.EntityFromShapeResult(shape, 1).Name().ToCString()] = cq.Solid(shape)
        exp.Next()
    return out


def placed(solid: cq.Shape, slot_xy: tuple[float, float], window_top_y: float) -> cq.Shape:
    """Move a STEP solid into the mount's frame, with the mount over slot_xy."""
    xc, yc = slot_xy
    return solid.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90).translate(
        cq.Vector(X0 - xc, Z0 - yc, -window_top_y))


def plate_at_deck(z_deck_surface: float) -> cq.Workplane:
    """A 96-well plate centred on the optical axis, standing on the deck."""
    w, d, h = PLATE
    plate = box(w, d, h, z0=z_deck_surface)
    wells = [(-49.5 + 9 * i, 31.5 - 9 * j) for i in range(12) for j in range(8)]
    return plate.cut(cq.Workplane("XY").pushPoints(wells).circle(6.86 / 2).extrude(11)
                     .translate((0, 0, z_deck_surface + h - 10.9)))


def fov(p: Params, z_target: float, focal: float) -> tuple[float, float, float]:
    """Field of view (w, h) at z_target and the pinhole height, for a pinhole
    PUPIL_IN_LENS behind the lens front."""
    z_pin = p.z_lens_front + PUPIL_IN_LENS
    dist = z_pin - z_target
    return SENSOR[0] * dist / focal, SENSOR[1] * dist / focal, z_pin


def fov_pyramid(p: Params, z_target: float, focal: float) -> cq.Workplane:
    w, h, z_pin = fov(p, z_target, focal)
    s = 1e-3
    small = cq.Wire.makePolygon([cq.Vector(sx * s, sy * s, p.z_lens_front)
                                 for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], close=True)
    k = (p.z_lens_front - z_target) / (z_pin - z_target)
    big = cq.Wire.makePolygon([cq.Vector(sx * w / 2 * k, sy * h / 2 * k, z_target)
                               for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], close=True)
    return cq.Workplane("XY").add(cq.Solid.makeLoft([small, big]))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slot", type=int, default=5, help="slot to render (default 5)")
    ap.add_argument("--focal", type=float, default=25.0, help="zoom setting for the FOV, mm")
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()

    p = Params()
    parts = build(p)
    solids = load_solids(fetch())
    win = solids["TOP WINDOW"].BoundingBox()
    window_top_y, window_t = win.ymax, win.ymax - win.ymin
    gantry_top_y = solids["Z-GANTRY TOP COVER"].BoundingBox().ymax
    z_deck = DECK_Y - window_top_y                     # deck surface in the mount frame
    z_plate = z_deck + PLATE[2]
    geometry = {
        "window thickness (mm)": round(window_t, 2),
        "window outline (mm)": [round(win.xlen, 2), round(win.zlen, 2)],
        "deck surface to window underside (mm)": round(win.ymin - DECK_Y, 2),
        "pipette-head top cover below window underside (mm)": round(win.ymin - gantry_top_y, 2),
        "lens front to plate top (mm)": round(p.z_lens_front - z_plate, 1),
    }

    # Frame solids around the lid, to check the mount against, per slot.
    frame = solids["OT-2 FRAME"]
    slots = {}
    for n, xy in SLOTS.items():
        fr = cq.Workplane("XY").add(placed(frame, xy, window_top_y))
        clash = overlap(parts["base"], fr)
        slots[n] = {
            "centre (deck mm)": [xy[0], xy[1]],
            "mark on lid from window front-left corner (mm)": [round(xy[0] + 85.95, 1), round(xy[1] + 13.03, 1)],
            "base overlaps the frame (mm3)": round(clash, 1),
            "fits": clash < 1e-3,
        }
    w, h, _ = fov(p, z_plate, args.focal)
    f_fill = SENSOR[0] * (p.z_lens_front + PUPIL_IN_LENS - z_plate) / (PLATE[0] + 10.0)
    optics = {
        "focal length used (mm)": args.focal,
        f"field of view at the plate top, f = {args.focal:g} (mm)": [round(w, 1), round(h, 1)],
        "resolution at the plate (px/mm)": round(4056 / w, 1),
        "pixels across one 6.86 mm well": round(4056 / w * 6.86),
        "longest focal length leaving 5 mm round the plate (mm)": round(f_fill, 1),
    }
    report = {"ot2_geometry": geometry, "optics": optics, "slots": slots,
              "source": "Opentrons OT-2 Reference Model Detailed.STEP, github.com/Opentrons/ot2 (2018)"}
    (EXPORTS / "ot2_fit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

    if not args.no_render:
        render(p, parts, solids, SLOTS[args.slot], window_top_y, z_deck, z_plate, args)


def render(p, parts, solids, slot_xy, window_top_y, z_deck, z_plate, args) -> None:
    import pyvista as pv

    from render import add

    ctx = {n: cq.Workplane("XY").add(placed(solids[n], slot_xy, window_top_y)) for n in CONTEXT}
    plate = plate_at_deck(z_deck)
    pyr = fov_pyramid(p, z_plate, args.focal)

    pl = pv.Plotter(off_screen=True, window_size=(1600, 1400))
    pl.set_background("white")
    pl.enable_anti_aliasing("ssaa")
    for n, wp in ctx.items():
        if n == "REMOVABLE DECK":
            add(pl, wp, n, color=(0.78, 0.80, 0.82))
        elif "WINDOW" in n or "DOOR" in n:
            add(pl, wp, n, opacity=0.12, color=(0.7, 0.85, 1.0))
        else:
            add(pl, wp, n, opacity=0.18, color=(0.85, 0.85, 0.85))
    add(pl, plate, "plate", color=(0.95, 0.95, 0.97))
    add(pl, pyr, "fov", opacity=0.22, color=(1.0, 0.8, 0.2))
    for name in ASSEMBLY[1:]:
        add(pl, parts[name], name)
    pl.camera_position = [(900, -1350, 450), (0, 0, -280), (0, 0, 1)]
    pl.add_text(f"Mount over slot {args.slot}, view to a 96-well plate at f = {args.focal:g} mm "
                f"(OT-2 model: Opentrons; gantry hidden)", font_size=11, color="black")
    pl.screenshot(RENDERS / "ot2_context.png")
    pl.close()

    # What the camera sees: a pinhole camera at the entrance pupil, looking down.
    w, h, z_pin = fov(p, z_plate, args.focal)
    pl = pv.Plotter(off_screen=True, window_size=(1014, 760), lighting="none")
    pl.set_background("black")
    for n in ("REMOVABLE DECK", "OT-2 FRAME"):
        add(pl, ctx[n], n, color=(0.50, 0.52, 0.55) if n == "REMOVABLE DECK" else (0.35, 0.35, 0.37))
    add(pl, plate, "plate", color=(0.80, 0.82, 0.86))
    pl.add_light(pv.Light(position=(-150, 250, z_pin), focal_point=(0, 0, z_deck), intensity=0.9))
    pl.add_light(pv.Light(position=(200, -200, z_pin), focal_point=(0, 0, z_deck), intensity=0.35))
    pl.camera.position = (0, 0, z_pin)
    pl.camera.focal_point = (0, 0, z_deck)
    pl.camera.up = (0, 1, 0)
    pl.camera.view_angle = math.degrees(2 * math.atan(SENSOR[1] / 2 / args.focal))
    pl.camera.clipping_range = (1.0, 2000.0)
    pl.add_text(f"simulated camera view, f = {args.focal:g} mm, slot {args.slot}", position="lower_left",
                font_size=10, color="yellow")
    pl.screenshot(RENDERS / "camera_view_sim.png")
    pl.close()
    print("rendered ot2_context.png and camera_view_sim.png")


if __name__ == "__main__":
    main()
