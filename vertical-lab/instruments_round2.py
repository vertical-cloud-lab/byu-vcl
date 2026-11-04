"""Round 2's equipment doing its job, with the insides showing (#303, PR #320): the Opentrons OT-2's gantry and pipette
over its deck, the Bambu Lab H2D and A1 mini printing a part, the CubXL's pipette over its rack, and the multi-doser
dosing into a vial drawn in half section. ``tour.py`` plays each one, like the round-3 and round-4 instruments:

    xvfb-run -a python3 tour.py ot2 h2d a1_mini cubxl_lh multidoser   # -> out/instruments/<key>.gif, .png; out/mp4/...
    python3 tour.py still h2d                                            # the end of every action -> /tmp/still_h2d.png

Each is an ``instruments.Instrument``: named pieces (``body`` stays put), a ``Joint`` per moving piece and an
``actions`` script. What is around each process is drawn see-through while it runs (a piece's ``~`` value in the
actions, as ``alloy_workflow.py`` ghosts the depowdering box and the MIDI's shell), and liquid, powder and printed
parts grow with ``grow()``, a ``follow`` joint that stretches a piece upward from its base. A machine whose motion
isn't rigid pieces (the doser's chain) can name its own clip function in ``TOURS``; tour.py calls it instead of
``tour_one``.

The models are round 2's (``lab_models/equipment.py``, ``lab_models/vendor.py``, ``carousel.py``), split into the
pieces that move; nothing here changes how round 2's scenes draw them. Frame, as in ``instruments.py``: x to the
right and y away from you when you face the front, z up from the bench, origin at the centre of the footprint, mm.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np

from instruments import Instrument, Joint, _piece, _xcyl, _ycyl  # noqa: F401

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
from common import Model, box, cyl, hose, rbox, tube  # noqa: E402,F401

# files the builds read besides this one and tour.py's common sources: tour.load() re-tessellates when they change
SOURCES = ["lab_models/equipment.py", "lab_models/vendor.py", "lab_models/labware.py", "carousel.py",
           "multidoser/layout.py", "multidoser/parts.py", "multidoser/params.py", "multidoser/kinematics.py"]

# name: (r, g, b, opacity, specular), merged into tour.MATS
MATERIALS = {
    "r2_petg_blue": (0.16, 0.42, 0.80, 1.0, 0.35),      # the part printing on the H2D
    "r2_pla_orange": (0.95, 0.50, 0.12, 1.0, 0.30),     # the part printing on the A1 mini
    "r2_pla_green": (0.20, 0.62, 0.32, 1.0, 0.30),
    "r2_liquid": (0.30, 0.58, 0.92, 0.80, 0.6),         # the liquid in a half-section vial
    "r2_liquid_cut": (0.22, 0.48, 0.85, 1.0, 0.4),
    "r2_powder": (0.66, 0.66, 0.70, 1.0, 0.1),          # a grey metal powder
    "r2_glass_cut": (0.80, 0.90, 0.95, 0.45, 0.9),      # a vial's glass, cut in half
    "r2_tip": (0.90, 0.91, 0.88, 0.70, 0.4),            # a polypropylene pipette tip
    "r2_hot": (1.00, 0.42, 0.08, 1.0, 0.1),             # a hot nozzle tip
}


# ===================================================================================================== helpers
def split(model: Model, inst: Instrument, groups: dict, drop=()) -> None:
    """Hand a lab_models Model's parts to the instrument's pieces: groups = {piece: (part names)}; every other part
    goes to "body", and parts named in `drop` are left out."""
    owner = {n: piece for piece, names in groups.items() for n in names}
    for part in model.parts:
        if part.name in drop:
            continue
        _piece(inst, owner.get(part.name, "body")).parts.append(part)


def grow(z0: float, h0: float, h1: float, parent: str | None = None, v0: float = 0.0) -> Joint:
    """A follow joint that stretches a piece modelled from z0 to z0 + h0 so it reaches z0 + h1 at v = 1: a liquid
    level, a powder heap or a printed part (a prism, so stretching it is the same as adding layers). Below v = 0 it
    shrinks back, to zero height at v = -h0 / (h1 - h0)."""
    k = h1 / h0 - 1.0
    zero = [[0.0] * 4 for _ in range(3)]
    jz = [[0.0] * 4, [0.0] * 4, [0.0, 0.0, k, -k * z0]]
    return Joint("follow", vec=(0.0, 0.0, 1.0), jac=(zero, zero, jz), parent=parent, v0=v0)


def trace(path, axis: int, parent: str | None = None, sign: float = 1.0) -> Joint:
    """A follow joint that moves a piece along one axis (0 x, 1 y, 2 z) of a path's offsets (times `sign`), in step
    with a "path" joint on the same waypoints: a CoreXY gantry following its toolhead in y, a bed slinger's bed
    moving against the nozzle's y."""
    jac = [[[0.0] * 4 for _ in range(3)] for _ in range(3)]
    jac[axis][axis][3] = float(sign)
    return Joint("follow", path=tuple(tuple(map(float, p)) for p in path),
                 jac=tuple(tuple(map(tuple, j)) for j in jac), parent=parent)


def loops(x0, x1, y0, y1, n: int, start=(0.0, 0.0), z=0.0) -> tuple:
    """Waypoints from `start` to the corner (x0, y0), n times round the rectangle, and back to `start`."""
    pts = [(start[0], start[1], z)]
    for _ in range(n):
        pts += [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
    pts += [(x0, y0, z), (start[0], start[1], z)]
    return tuple(pts)


def half(shape, y: float = 0.0, keep_back: bool = True):
    """The back half (y >= `y`) of a CadQuery shape, so a camera in front sees its section."""
    big = 5000.0
    cutter = box(-big, y - big if keep_back else y, -big, big, y if keep_back else y + big, big)
    return shape.cut(cutter)


# ===================================================================================================== Opentrons OT-2
def ot2() -> Instrument:
    """The OT-2 from Opentrons' reference STEP (lab_models/vendor.py), its gantry and pipette split out by bounding
    box so they move over the deck."""
    raise FileNotFoundError("ot2: not built yet")


# ===================================================================================================== the printed parts
def _rack_part(w: float, d: float, h: float, holes: int, hole_d: float, x=0.0, y=0.0, z=0.0) -> cq.Workplane:
    """A vial rack as it prints: a rounded block with a row of through-holes, a prism, so ``grow`` adds its layers."""
    blk = rbox(w, d, h, 6, x=x, y=y, z=z)
    pitch = w / holes
    for i in range(holes):
        blk = blk.cut(cyl(hole_d, h + 2, x=x - w / 2 + pitch * (i + 0.5), y=y, z=z - 1))
    return blk


# ===================================================================================================== Bambu Lab H2D
# Round 2's model (lab_models.equipment.h2d): the enclosure, a CoreXY gantry at the top (the x beam rides the two y
# rails; the dual-nozzle toolhead hangs in front of it) and the bed on two Z screws, moving down a layer at a time.
# Bambu: 325 x 320 x 325 mm build volume with one nozzle. The part is a six-vial rack, 120 x 34 x 40 mm, in PETG,
# printed by the left nozzle; the head's path is its outline, a few loops standing for the layers.
H2D_PART = dict(w=120.0, d=34.0, h=40.0, holes=5, hole_d=21.0, x=0.0, y=5.0)
H2D_DROP = 250.0                     # the bed's park, below the nozzles


def h2d() -> Instrument:
    import equipment
    p = equipment.H2D
    W, D, H = p["W"], p["D"], p["H"]
    gz = H - 110.0
    tip_z = gz - 80.0                                    # the nozzles' tips (equipment.h2d)
    bed_z = tip_z - 9.0                                  # the build plate's top at the tips: the first layer
    inst = Instrument("h2d", "FDM printer, enclosed, CoreXY, two nozzles", "Bambu Lab H2D", (W, D, H),
                      "round 2's model (lab_models/equipment.py) from Bambu's spec: 492 x 514 x 626 mm",
                      props=("part",))
    m = equipment.h2d(bed_z=bed_z)
    split(m, inst, {"shell": ("frame", "lid glass", "screen", "front strip"), "door": ("door glass",),
                    "bed": ("bed",), "plate": ("build plate",), "gantry": ("x gantry",),
                    "head": ("toolhead", "nozzles")})
    q = H2D_PART
    plate_top = bed_z + 9.0
    _piece(inst, "part").add("vial rack (PETG)", _rack_part(q["w"], q["d"], 1.0, q["holes"], q["hole_d"], x=q["x"],
                                                            y=q["y"], z=plate_top - 0.5), "r2_petg_blue")
    _piece(inst, "head").add("hot tip", cq.Workplane("XY").circle(0.6).workplane(offset=3.0).circle(3.4).loft()
                             .translate((-10.0, -50.0, tip_z - 0.2)), "r2_hot")
    # the left nozzle (x -10, y -50) traces the rack's outline: offsets from where the head is modelled
    nx, ny = -10.0, -50.0
    x0, x1 = q["x"] - q["w"] / 2 - nx, q["x"] + q["w"] / 2 - nx
    y0, y1 = q["y"] - q["d"] / 2 - ny, q["y"] + q["d"] / 2 - ny
    path = loops(x0, x1, y0, y1, 6)
    hv = -1.0 / (q["h"] + 0.5 - 1.0)                     # the part's v with no height (grow)
    door_x = -W / 2 + 22.0
    inst.joints = {
        "door": Joint("hinge", axis=(0, 0, 1), pivot=(door_x, -D / 2 + 2.0, 0.0), deg=-105.0),
        "bed": Joint("slide", vec=(0.0, 0.0, -1.0), v0=H2D_DROP),          # mm below the first layer
        "plate": Joint("path", parent="bed", path=((0, 0, 0), (0, 0, 12.0), (0, -D + 40.0, 12.0))),
        "part": grow(plate_top - 0.5, 1.0, q["h"] + 0.5, parent="plate", v0=hv),
        "head": Joint("path", path=path),
        "gantry": trace(path, 1),
    }
    inst.actions = [
        ("The enclosure drawn see-through: a CoreXY gantry at the top carries the two-nozzle toolhead, and the bed "
         "below it moves only in Z.", 2.2, {"~shell": (0.0, 1.0), "~door": (0.0, 1.0)}),
        ("The bed rises on its Z screws until the build plate is a first layer below the nozzles.", 1.8,
         {"bed": (H2D_DROP, 0.0)}),
        ("Printing a vial rack in PETG: the toolhead traces each layer, and the bed steps down a layer at a time "
         "as the part grows.", 6.5, {"head": (0.0, 1.0), "gantry": (0.0, 1.0), "bed": (0.0, q["h"]),
                                     "part": (hv, 1.0)}),
        ("Done. The head parks and the bed drops, so the arm can reach in.", 1.8, {"bed": (q["h"], H2D_DROP)}),
        ("The door opens and the flexible plate comes out with the rack on it, for the arm to take.", 2.6,
         {"door": (0.0, 1.0), "plate": (0.0, 1.0), "~door": (1.0, 0.0)}),
    ]
    inst.labels = [("CoreXY gantry", (0.0, 0.0, gz + 30.0), (0.82, 0.16)),
                   ("toolhead, two nozzles", (15.0, -50.0, gz - 40.0), (0.16, 0.22)),
                   ("bed, moving in Z", (-p["bed_w"] / 2, -p["bed_d"] / 2, bed_z - 120.0), (0.14, 0.72))]
    inst.zoom = {2: ((0.0, -40.0, tip_z - 30.0), 900.0), 3: "out"}
    inst.cam = (0.9, -1.7, 0.8)
    inst.notes = ["The part is a five-hole vial rack, 40 mm tall, standing for whatever the tray prints. The head's "
                  "path is the rack's outline, six loops for the layers; the bed's step per layer is drawn as a "
                  "steady fall."]
    return inst


# ===================================================================================================== Bambu Lab A1 mini
# Round 2's model (lab_models.equipment.a1_mini): a bed slinger. The bed moves in y on the base rail, the toolhead in
# x along the cantilevered arm, and the arm in z up the column. The part is a small vial rack in PLA, 80 x 30 x 30 mm.
A1_PART = dict(w=84.0, d=30.0, h=30.0, holes=4, hole_d=17.0)
A1_LIFT = 70.0                       # the arm parked this far above the first layer


def a1_mini() -> Instrument:
    import equipment
    p = equipment.A1
    tip_dz = 84.0                                        # the hotend's tip, below the arm's z (equipment.a1_mini)
    az = p["bed_top"] + tip_dz                           # the arm with the tip at the plate: the first layer
    inst = Instrument("a1_mini", "FDM printer, open bed slinger", "Bambu Lab A1 mini", (p["W"], p["D"], p["H"]),
                      "round 2's model (lab_models/equipment.py) from Bambu's spec and outline drawing: "
                      "347 x 315 x 365 mm", props=("part",))
    m = equipment.a1_mini(gantry_z=az, bed_y=0.0)
    split(m, inst, {"bed": ("bed carriage", "heatbed"), "plate": ("build plate",),
                    "arm": ("x arm", "z carriage", "x motor box", "arm end cap"),
                    "head": ("toolhead", "hotend", "extruder")}, drop=("ptfe tube",))
    x0 = -p["W"] / 2
    th_x, th_y = x0 + 155.0, (45.0 - p["col_d"] / 2 - 26.0) - 26.0       # the hotend's x, y (equipment.a1_mini)
    bx = x0 + 153.5                                      # the bed's centre in x
    q = A1_PART
    px, py = bx, 0.0
    _piece(inst, "part").add("vial rack (PLA)", _rack_part(q["w"], q["d"], 1.0, q["holes"], q["hole_d"], x=px, y=py,
                                                           z=p["bed_top"] - 0.5), "r2_pla_orange")
    _piece(inst, "head").add("hot tip", cq.Workplane("XY").circle(0.5).workplane(offset=2.5).circle(3.0).loft()
                             .translate((th_x, th_y, p["bed_top"] - 0.2)), "r2_hot")
    # the nozzle's offsets relative to the part: x by the head, y by the bed moving the other way
    ex0, ex1 = px - q["w"] / 2 - th_x, px + q["w"] / 2 - th_x
    ey0, ey1 = py - q["d"] / 2 - th_y, py + q["d"] / 2 - th_y
    path = loops(ex0, ex1, ey0, ey1, 5)
    hv = -1.0 / (q["h"] + 0.5 - 1.0)
    inst.joints = {
        "arm": Joint("slide", vec=(0.0, 0.0, 1.0), v0=A1_LIFT),            # mm above the first layer
        "head": trace(path, 0, parent="arm"),
        "bed": trace(path, 1, sign=-1.0),
        "plate": Joint("path", parent="bed", path=((0, 0, 0), (0, 0, 30.0), (0, -170.0, 110.0))),
        "part": grow(p["bed_top"] - 0.5, 1.0, q["h"] + 0.5, parent="plate", v0=hv),
    }
    inst.actions = [
        ("A bed slinger: the bed moves front to back, the toolhead left to right along the arm, and the arm up "
         "and down the column.", 1.8, {"arm": (A1_LIFT, 0.0)}),
        ("Printing a small vial rack in PLA: the head and the bed trace each layer between them, and the arm "
         "climbs a layer at a time as the part grows.", 6.0, {"head": (0.0, 1.0), "bed": (0.0, 1.0),
                                                                "arm": (0.0, q["h"]), "part": (hv, 1.0)}),
        ("Done. The arm lifts clear.", 1.4, {"arm": (q["h"], q["h"] + A1_LIFT)}),
        ("The magnetic PEI plate lifts off with the rack on it: the arm takes the plate, not the part.", 2.4,
         {"plate": (0.0, 1.0)}),
        ("The arm parks, ready for a fresh plate.", 1.6, {"arm": (q["h"] + A1_LIFT, A1_LIFT)}),
    ]
    inst.labels = [("toolhead (x, on the arm)", (th_x, th_y, p["bed_top"] + 60.0), (0.16, 0.20)),
                   ("arm (z, on the column)", (x0 + 279.0, 0.0, p["H"] - 40.0), (0.80, 0.16)),
                   ("bed (y)", (bx, -90.0, p["bed_top"]), (0.20, 0.78))]
    inst.zoom = {1: ((px, -20.0, p["bed_top"] + 25.0), 620.0), 2: "out"}
    inst.cam = (0.8, -1.7, 0.75)
    inst.notes = ["The PTFE feed tube from the spool holder is left out: in round 2's model it is a fixed sweep, which "
                  "would leave the moving head. The part is a four-hole vial rack, 30 mm tall."]
    return inst


# ===================================================================================================== CubXL, liquid handling
# Round 2's model (lab_models.equipment.cubxl): the gantry (y) on the frame, the carriage (x) on the gantry and the
# tool plate with the pipette and the capper/decapper (z). The deck as round 2 sets it: the six-vial rack and a tip
# rack. Here the stock is vial 1, uncapped, and vial 6 is the vial the arm brought from the multi-doser with its
# powder (round 2's workflow, step 6); both are drawn in half section, so the liquid shows. The pipette takes a tip,
# draws from the stock, adds it to the powder, mixes and puts the tip back. Volumes are for the picture: the pipette
# here is round 2's generic one, not a named model.
CUB_TIP = dict(len=35.0, top_d=5.6, end_d=0.9, collar=8.0)       # a 20 uL tip; the nozzle goes 8 mm into it
CUB_RACK = dict(x=150.0, y=20.0, top=125.0, proud=4.0, pitch=9.0)  # our tip rack (SBS 127.76 x 85.48), in reach
CUB_STOCK = dict(level0=40.0, level1=26.0)                       # stock vial's liquid, mm above its floor
CUB_DOSE = dict(powder=6.0, level=16.0)                          # vial 6: the powder, then the liquid over it


def _cub_vial_half(x, y, z, od=28.0, idia=25.0, h=55.0) -> cq.Workplane:
    glass = tube(od, idia, h, x=x, y=y, z=z).union(cyl(od, 1.5, x=x, y=y, z=z))
    return half(glass, y=y)


def cubxl_lh() -> Instrument:
    import equipment
    p = equipment.CUBXL
    W, D, H = p["W"], p["D"], p["H"]
    tr = p["travel"]
    fx, fy, fz = 0.5, 0.5, 1.0                           # the carriage as modelled: centre, middle, top of z
    inst = Instrument("cubxl_lh", "Liquid-handling gantry: pipette over the vial rack",
                      "CubXL (Genmitsu PROVerXL 4030 V2 frame)", (W, D, H),
                      "round 2's model (lab_models/equipment.py) from the frame's spec and lab photos (#133, #200)",
                      props=("tip", "stock", "dose", "powder"))
    m = equipment.cubxl(fx, fy, fz)
    vials = {1: "vial 1", 6: "vial 6"}
    split(m, inst, {"gantry": ("gantry upright L", "gantry upright R", "gantry beam", "cable chain"),
                    "carriage": ("z carriage", "tool plate", "controller"), "tools": ("pipette", "capper")},
          drop=(*vials.values(), "vial 1 cap", "vial 6 cap", "vial rack", "tip rack"))
    gy = -D / 2 + 150 + fy * tr[1]
    cx = -tr[0] / 2 + fx * tr[0]
    zt = 100 + fz * tr[2]
    noz = np.array([cx - 50.0, gy - 80.0, zt - 40.0])     # the pipette's nozzle end, as modelled
    vz = 80.0                                             # the vials' and racks' floor (equipment.cubxl)
    vx = {i: -60.0 + (i - 1) * 32.0 for i in vials}
    vy = -60.0
    body = _piece(inst, "body")
    for i, n in vials.items():
        body.add(f"{n} (half section)", _cub_vial_half(vx[i], vy, vz), "r2_glass_cut")
    _piece(inst, "stock").add("stock liquid", half(cyl(24.6, 1.0, x=vx[1], y=vy, z=vz + 1.5), y=vy), "r2_liquid")
    _piece(inst, "powder").add("dosed powder", half(cyl(24.6, CUB_DOSE["powder"], x=vx[6], y=vy, z=vz + 1.5), y=vy),
                               "r2_powder")
    _piece(inst, "dose").add("added liquid", half(cyl(24.6, 1.0, x=vx[6], y=vy, z=vz + 1.5 + CUB_DOSE["powder"]),
                                                  y=vy), "r2_liquid")
    # the vial rack (round 2's block, 210 x 50 x 30) with its pockets, cut in half with the two vials
    rack = box(-85.0, -85.0, vz, 125.0, -35.0, vz + 30.0)
    for k in range(6):
        rack = rack.cut(cyl(28.6, 31.0, x=-60.0 + 32.0 * k, y=vy, z=vz + 1.0))
    body.add("vial rack (half section)", half(rack, y=vy), "pla_white")
    # a tip rack of 20 uL tips where the pipette reaches every row (round 2's stood behind its reach); A1 is ours
    t, r = CUB_TIP, CUB_RACK
    rk = rbox(127.76, 85.48, r["top"] - vz, 3, x=r["x"], y=r["y"], z=vz)
    body.add("tip rack", rk, "pp_black")
    tip_top = r["top"] + r["proud"]

    def tip_at(x, y):
        return cq.Workplane("XY").circle(t["end_d"] / 2).workplane(offset=t["len"]).circle(t["top_d"] / 2).loft() \
            .translate((x, y, tip_top - t["len"])).val()
    grid = [(r["x"] - 5.5 * r["pitch"] + c * r["pitch"], r["y"] + 3.5 * r["pitch"] - k * r["pitch"])
            for k in range(8) for c in range(12)]
    body.add("tips", cq.Compound.makeCompound([tip_at(x, y) for x, y in grid[1:]]), "r2_tip")
    tip0 = np.array([grid[0][0], grid[0][1], tip_top])                # A1's top
    _piece(inst, "tip").add("tip A1", tip_at(*grid[0]), "r2_tip")
    # the head's moves: nozzle positions, and the tip riding on it from the moment it is picked up
    travel_z = noz[2]                                    # the modelled height clears every vial and the rack
    on = tip0 - (0.0, 0.0, t["collar"])                  # the nozzle home in the tip's collar
    def at(x, y, z):                                     # noqa: E306
        return np.array([x, y, z], float)
    stock_in = at(vx[1], vy, vz + 1.5 + CUB_STOCK["level1"] - 4.0 + t["len"] - t["collar"])
    dose_in = at(vx[6], vy, vz + 1.5 + CUB_DOSE["powder"] + 3.0 + t["len"] - t["collar"])
    mix_up = dose_in + (0, 0, 9.0)
    seq = [at(on[0], on[1], travel_z), on, at(on[0], on[1], travel_z), at(vx[1], vy, travel_z), stock_in,
           at(vx[1], vy, travel_z), at(vx[6], vy, travel_z), dose_in, mix_up, dose_in, mix_up, dose_in,
           at(vx[6], vy, travel_z), at(on[0], on[1], travel_z), on, at(on[0], on[1], travel_z)]
    off = [tuple(s - noz) for s in seq]                  # the head's offsets from where it is modelled
    # the tip: still until it is picked up (seq[1]), then with the nozzle until it is back in the rack (seq[14])
    tip_pts = [tuple(np.array(o) - np.array(off[1])) for o in off[1:15]]
    seg = np.linalg.norm(np.diff(np.array(tip_pts), axis=0), axis=1)
    tv = np.concatenate([[0.0], np.cumsum(seg)]) / seg.sum()
    inst.joints = {
        "gantry": Joint("slide", vec=(0.0, 1.0, 0.0), v0=off[0][1]),
        "carriage": Joint("slide", vec=(1.0, 0.0, 0.0), parent="gantry", v0=off[0][0]),
        "tools": Joint("slide", vec=(0.0, 0.0, 1.0), parent="carriage", v0=off[0][2]),
        "tip": Joint("path", path=tuple(tip_pts)),
        "stock": grow(vz + 1.5, 1.0, CUB_STOCK["level0"], v0=1.0),
        "dose": grow(vz + 1.5 + CUB_DOSE["powder"], 1.0, CUB_DOSE["level"], v0=-1.0 / (CUB_DOSE["level"] - 1.0)),
        "powder": Joint("slide", vec=(0.0, 0.0, 0.0)),
    }
    lv1 = (CUB_STOCK["level1"] - 1.0) / (CUB_STOCK["level0"] - 1.0)     # the stock's v after one draw
    dv0 = -1.0 / (CUB_DOSE["level"] - 1.0)

    def go(i, j, **extra):                               # the head from seq[i] to seq[j]; the tip with it after 1
        d = {"gantry": (off[i][1], off[j][1]), "carriage": (off[i][0], off[j][0]), "tools": (off[i][2], off[j][2])}
        if 1 <= i <= 14 and 1 <= j <= 14:
            d["tip"] = (tv[i - 1], tv[j - 1])
        d.update(extra)
        return d

    c1 = ("The CubXL's gantry carries a pipette and a capper over its deck: a six-vial rack and a tip rack. The "
          "stock (vial 1) and the vial dosed by the multi-doser (vial 6) are drawn in half section.")
    c2 = "The pipette goes down onto a tip in the rack and lifts it."
    c3 = "Over the stock, down into the liquid, and it draws."
    c4 = "Up, over to vial 6, down to just above the powder, and it dispenses onto it."
    c5 = "It mixes: two draws and dispenses in the vial."
    c6 = "The tip goes back in its rack, and the gantry parks."
    legs = [(c2, 1.4, 0, 1), (c2, 1.0, 1, 2), (c3, 1.4, 2, 3), (c3, 1.2, 3, 4), (c3, 1.2, 4, 4),
            (c4, 1.0, 4, 5), (c4, 1.4, 5, 6), (c4, 1.2, 6, 7), (c4, 1.2, 7, 7),
            (c5, 0.5, 7, 8), (c5, 0.5, 8, 9), (c5, 0.5, 9, 10), (c5, 0.5, 10, 11),
            (c6, 1.0, 11, 12), (c6, 1.6, 12, 13), (c6, 1.0, 13, 14), (c6, 1.0, 14, 15)]
    draw = {(c3, 4, 4): {"stock": (1.0, lv1)}, (c4, 7, 7): {"dose": (dv0, 1.0)}}
    draw[(c2, 0, 1)] = {"~carriage": (0.0, 1.0)}                      # the tool plate see-through: the pipette shows
    draw[(c6, 14, 15)] = {"~carriage": (1.0, 0.0)}
    inst.actions = [(c1, 2.6, {})] + [(c, secs, go(i, j, **draw.get((c, i, j), {}))) for c, secs, i, j in legs]
    deck = [("vial 6: powder from the multi-doser", (vx[6], vy, vz + 40.0), (0.80, 0.80)),
            ("stock (vial 1)", (vx[1], vy, vz + 40.0), (0.16, 0.80)),
            ("tip rack", (r["x"], r["y"], tip_top), (0.84, 0.30))]
    inst.labels = [("pipette", tuple(noz + off[0] + (0, 0, 120.0)), (0.16, 0.18))] + deck
    inst.step_labels = {i: deck for i in range(1, len(inst.actions) - 2)}     # the close-ups: the deck only
    inst.zoom = {1: ((tip0[0], tip0[1], tip0[2] + 10.0), 520.0), 3: ((vx[1], vy, vz + 50.0), 430.0),
                 7: ((vx[6], vy, vz + 45.0), 430.0), 14: "out"}
    inst.cam = (0.75, -1.7, 1.0)
    inst.framing = (0.62, 0.30)
    inst.notes = ["The six-vial rack is round 2's; the tip rack (moved forward, into the pipette's reach), the tips, the "
                  "half-section vials, the liquid and the powder are added here. The pipette's moves are straight lines between the stops."]
    return inst


# ===================================================================================================== the multi-doser
def multidoser() -> Instrument:
    """The chain carousel v2 (carousel.py): its own layout.placements(State(...)), the dose in half section."""
    raise FileNotFoundError("multidoser: not built yet")


# {key: name of a function here, (inst, entries) -> str}: a clip tour.tour_one can't play; tour.py calls it instead
TOURS: dict[str, str] = {}

REGISTRY = {"ot2": ot2, "h2d": h2d, "a1_mini": a1_mini, "cubxl_lh": cubxl_lh, "multidoser": multidoser}
