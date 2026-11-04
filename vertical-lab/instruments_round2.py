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
# Opentrons' reference STEP ("OT-2 Reference Model Detailed", lab_models/vendor.py) is 26 solids, in vendor.ot2()'s
# order "solid 1" ... "solid 26". What each one is, from its bounding box, sections and quick renders:
#   1 the deck plate (slots 68.55 above the bench, 3.5 mm ridges round them); 2-9 the acrylic: side windows (2, 3, and
#   the outer skins 8, 9), top (4), back (5), the door's lower and upper panes (6, 7); 14 the frame, one solid with
#   the fixed trash and the gantry's X beam fused into it; 10-13 the head: lid, back plate, U-shaped cover, and the
#   C-shaped carriage hooked over the beam; 15-26 the pipettes, every variant drawn on both mounts at once (centres
#   x -17 and +17, Opentrons' 34 mm between mounts; y -78.7): a P20 single (3.75 mm nozzle, ending at z 301.1; 15
#   left, 19 right), a P300 (4.9 mm, 314.1; 23, 20), a P1000 (7.7 mm, 334.1; 24, 21) and an 8-channel (25, 22),
#   plus each mount's 18 x 37.5 x 177 mm slide, drawn up (16, 26) and 219 mm down (18, 17): the Z travel.
OT2_SOLIDS = dict(deck=(1,), panels=(2, 3, 4, 5, 6, 7, 8, 9), frame=14, cover=(10, 12), carriage=(11, 13),
                  left=(15, 16), right=(20, 26), drop=(17, 18, 19, 21, 22, 23, 24, 25))
# The deck, from Opentrons' deck definition (github.com/Opentrons/opentrons, shared-data/deck/definitions/3/
# ot2_standard.json): 12 slots of 128 x 86 mm at a pitch of 132.5 x 90.5 mm, slot 1 front left, slot 12 the fixed
# trash; the deck's origin, slot 1's front-left corner, 115.65 x 68.03 mm in from the front-left corner of the
# robot's 624.3 x 565.2 mm footprint. That footprint is the STEP frame's (solid 14) to the 0.1 mm, so the origin
# lands at (-196.5, -213.47) here, and the STEP's slot ridges fall in the 4.5 mm gaps between the slots. The deck's
# surface, 68.55 mm above the bench, is measured off the STEP's deck plate.
OT2 = dict(x0=-196.5, y0=-213.47, pitch=(132.5, 90.5), deck_z=68.55,
           nozzle=(17.0, -78.74, 314.1),      # the P300's nozzle end (solid 20), mount fully up
           beam=(-274.4, -44.0, 499.0, 274.4, 32.0, 582.0),   # the X beam, inside the frame's side walls (x +-274.45)
           trash=(70.0, 55.0, 68.6, 250.0, 232.0, 160.0),   # the fixed trash's block (above the deck), in solid 14
           overlap=7.47,                      # how far a 300 uL tip seats onto the P300's nozzle (Opentrons)
           travel_z=240.0,                    # the nozzle's height between moves
           src_ul=1500.0, ul=300.0)


def _ot2_slot(n: int) -> tuple:
    """The front-left corner (x, y) of deck slot n (1-12)."""
    c, r = (n - 1) % 3, (n - 1) // 3
    return OT2["x0"] + OT2["pitch"][0] * c, OT2["y0"] + OT2["pitch"][1] * r


def _ot2_well(n: int, a1x: float, a1y: float, row: int, col: int, pitch: float = 9.0) -> tuple:
    """A well's centre (x, y) in an SBS labware seated in slot n, A1 a1x from its left and a1y from its back edge."""
    import labware
    x, y = _ot2_slot(n)
    return x + a1x + col * pitch, y + labware.SBS_D - a1y - row * pitch


def _ot2_seat(model: Model, n: int) -> Model:
    """A lab_models labware (centred, on z = 0) seated in slot n, as Opentrons places it: corner on the slot's."""
    import labware
    x, y = _ot2_slot(n)
    return model.moved(x + labware.SBS_W / 2, y + labware.SBS_D / 2, OT2["deck_z"])


def _ot2_path(states, taus, comps, dwell) -> tuple:
    """A follow joint's waypoints that play one channel (a tuple of values: an offset, a liquid level) through the
    actions with any timing: states[a] holds the channel at the start of action a and at the end of each of its
    segments, taus[a] each segment's share of the action. A path joint moves evenly by arc length, so each segment
    is made as long as its share of the action; where the channel moves less than that, the rest of the length goes
    along `dwell`, an axis the joint's jac ignores (a pause, then a move, within one action). Returns (waypoints,
    v at the end of every action)."""
    p = np.zeros(3)
    p[list(comps)] = states[0][0]
    pts, ends, s = [tuple(map(float, p))], [], 0.0
    for vals, tau in zip(states, taus):
        steps = [np.subtract(b, a) for a, b in zip(vals[:-1], vals[1:])]
        c = max(float(np.linalg.norm(d)) / t for d, t in zip(steps, tau))
        for d, t in zip(steps, tau):
            q = np.zeros(3)
            q[list(comps)] = d
            q[dwell] = math.sqrt(max((c * t) ** 2 - float(np.dot(d, d)), 0.0))
            p = p + q
            pts.append(tuple(map(float, p)))
        s += c
        ends.append(s)
    return tuple(pts), [e / s if s > 0 else 0.0 for e in ends]


def _ot2_split(solid, box_: tuple) -> tuple:
    """(the part of a solid inside an axis-aligned box, the rest)."""
    b = box(*box_).val()
    return solid.intersect(b), solid.cut(b)


def _ot2_pipette(solid, name: str) -> list:
    """A STEP pipette as (name, shape, material): the body light grey, the shaft and nozzle below it darker."""
    bb = solid.BoundingBox()
    shaft, body = _ot2_split(solid, (bb.xmin - 1, bb.ymin - 1, bb.zmin - 1, bb.xmax + 1, bb.ymax + 1, 388.0))
    return [(f"{name} body", body, "inst_light"), (f"{name} shaft", shaft, "inst_grey")]


def ot2() -> Instrument:
    """The OT-2 from Opentrons' reference STEP (lab_models/vendor.py), its moving head split out of the STEP's solids
    (see OT2_SOLIDS): the X beam cut out of the frame solid by its bounding box, OT2["beam"], is the gantry, sliding
    in y between the frame's side walls; the head's lid, cover, back plate and carriage ride it in x; the P300 on
    the right mount with its slide moves in z. The STEP draws every pipette on both mounts, so this keeps one each,
    a P20 on the left (parked up) and the P300 on the right, Opentrons' own shapes. On the deck, in Opentrons' slot
    positions (OT2): a 300 uL tip rack in slot 1, a 2 mL deep-well plate in slot 2 and a 96-well plate in slot 3,
    both cut through row H so the liquid in H1 shows, and the fixed trash in slot 12, the STEP's block with a bin cut
    into it. The P300 picks tip A1, draws 300 uL from the deep well, dispenses it into the plate's H1 and drops the
    tip in the trash."""
    import labware
    import vendor
    p = OT2
    sols = vendor._solids("ot2")
    S = lambda n: sols[n - 1]                                       # noqa: E731  the STEP's "solid n"
    ox, oy, oz = p["nozzle"]
    inst = Instrument("ot2", "Liquid-handling robot", "Opentrons OT-2", (624.3, 567.4, 662.0),
                      "Opentrons' reference STEP (github.com/Opentrons/ot2), its envelope as the size; deck slots from "
                      "Opentrons' ot2_standard.json deck definition; labware from lab_models/labware.py")
    body, frame, panels = _piece(inst, "body"), _piece(inst, "frame"), _piece(inst, "panels")
    # ---- the frame solid, split: the X beam (gantry), the fixed trash (a bin cut into its block), the rest
    beam, rest = _ot2_split(S(OT2_SOLIDS["frame"]), p["beam"])
    trash, rest = _ot2_split(rest, p["trash"])
    tb = trash.BoundingBox()
    tcx, tcy, ttop = (tb.xmin + tb.xmax) / 2, (tb.ymin + tb.ymax) / 2, tb.zmax
    walls = trash.intersect(box(-1e3, -1e3, 99.5, 1e3, 1e3, 100.5).val()).BoundingBox()   # its sides, under the rim
    bin_floor = 82.0
    trash = trash.cut(rbox(walls.xlen - 12, walls.ylen - 12, ttop - bin_floor + 1, 6.0, x=(walls.xmin + walls.xmax) / 2,
                           y=(walls.ymin + walls.ymax) / 2, z=bin_floor).val())
    frame.add("frame", rest, "printer_white")
    body.add("fixed trash", trash, "inst_offwhite")
    body.add("deck", S(OT2_SOLIDS["deck"][0]), "aluminium")
    for n in OT2_SOLIDS["panels"]:
        panels.add(f"acrylic {n}", S(n), "acrylic")
    _piece(inst, "gantry").add("X beam", beam, "inst_dark")
    car, cover, pip = _piece(inst, "carriage"), _piece(inst, "cover"), _piece(inst, "pipette")
    back, hook = OT2_SOLIDS["carriage"]
    car.add("back plate", S(back), "printer_white")
    car.add("carriage", S(hook), "inst_grey")
    lid, shell = OT2_SOLIDS["cover"]
    cover.add("head lid", S(lid), "printer_white")
    cover.add("head cover", S(shell), "printer_white")
    # the P20 rides with the carriage, parked up; the P300 is the piece that moves in z
    for piece, (n, slide), what in ((car, OT2_SOLIDS["left"], "P20 (left mount)"),
                                    (pip, OT2_SOLIDS["right"], "P300 (right mount)")):
        for nm, shp, mat in _ot2_pipette(S(n), what):
            piece.add(nm, shp, mat)
        piece.add(f"{what} slide", S(slide), "inst_dark")
    # ---- labware: tips in slot 1, the deep-well source in slot 2, the 96-well plate in slot 3
    dz = p["deck_z"]
    rack = _ot2_seat(labware.tiprack("300ul"), 1)
    tips = rack.parts[1].shape.Solids()                        # in _grid order: A1 first
    body.add("tip rack", rack.parts[0].shape, "pp_black")
    body.add("tips", cq.Compound.makeCompound(tips[1:]), "r2_tip")
    tipm = _piece(inst, "tip")
    tipm.add("tip A1", tips[0], "r2_tip")
    _piece(inst, "tipxy")                                      # no parts: carries the tip in x and y
    deep, nest = labware.PLATES["96_deep"], labware.PLATES["96_nest"]
    sx, sy = _ot2_well(2, deep["a1x"], deep["a1y"], 7, 0)      # H1 of the deep-well plate
    dx, dy = _ot2_well(3, nest["a1x"], nest["a1y"], 7, 0)      # H1 of the 96-well plate
    src_plate = _ot2_seat(labware.plate("96_deep"), 2)
    dst_plate = _ot2_seat(labware.plate("96_nest"), 3)
    body.add("deep-well plate", half(cq.Workplane().add(src_plate.parts[0].shape), sy), "polystyrene")
    body.add("96-well plate", half(cq.Workplane().add(dst_plate.parts[0].shape), dy), "polystyrene")
    s_bot = dz + deep["H"] - deep["depth"]
    w = deep["well"] - 0.1
    s_h = p["src_ul"] / w ** 2                                 # 1.5 mL in an 8.2 mm square well
    s_after = s_h - p["ul"] / w ** 2
    _piece(inst, "source").add("liquid in H1", half(box(sx - w / 2, sy - w / 2, s_bot, sx + w / 2, sy + w / 2,
                                                        s_bot + s_h), sy), "r2_liquid_cut")
    d_bot = dz + nest["H"] - nest["depth"]
    d_h = p["ul"] / (math.pi * (nest["well"] / 2 - 0.05) ** 2)   # 300 uL in a 6.96 mm well
    _piece(inst, "well").add("liquid in H1", half(cyl(nest["well"] - 0.1, d_h, x=dx, y=dy, z=d_bot), dy),
                             "r2_liquid_cut")

    # ---- the script: the head (P300 nozzle) and tip offsets, the liquids, segment by segment
    tip_top = dz + 64.49                                       # the 300 uL rack's height (labware.tiprack)
    tip_len = 59.3
    tx, ty = _ot2_well(1, 14.38, 11.24, 0, 0)                  # tip A1
    tl_z, tl_h = tip_top - tip_len + 0.6, 40.0                 # the liquid drawn up into it
    _piece(inst, "tipliquid").add("liquid in the tip", cq.Solid.makeCone(
        0.2, 0.2 + 1.95 / 48.3 * tl_h * 0.85, tl_h, cq.Vector(tx, ty, tl_z), cq.Vector(0, 0, 1)), "r2_liquid")
    z_pick = tip_top - p["overlap"]                            # the nozzle seated in the tip
    z_asp = s_bot + 1.0 + tip_len - p["overlap"]               # the tip 1 mm off the well's bottom
    z_dsp = d_bot + 1.0 + tip_len - p["overlap"]
    z_trav = p["travel_z"]

    def head(x, y, z):                                         # where the nozzle is -> the head's offset
        return (x - ox, y - oy, z - oz)
    h_pick = head(tx, ty, z_pick)

    def carried(h):                                            # the tip on the nozzle: it moves as the head does
        return tuple(a - b for a, b in zip(h, h_pick))
    tip_fall = (tcx - tx + 6.0, tcy - ty - 4.0, bin_floor + 0.4 - (tip_top - tip_len))   # drifting a little
    hide = 1.0                                                 # an empty well's or tip's liquid, out of sight
    script = [
        ("Opentrons' own CAD of the OT-2. Its door, windows and frame fade, and the head's cover too, to show the "
         "P300 pipette on the right mount and a P20 on the left.", 2.6,
         {"~panels": (0.0, 1.0), "~frame": (0.0, 0.55), "~cover": (0.0, 0.8)}, [(1.0, {})]),
        ("The gantry slides forward and the head along it, to the tip rack in slot 1. The pipette comes down and "
         "presses its nozzle into tip A1.", 3.4, {},
         [(0.62, dict(head=head(tx, ty, z_trav))), (0.38, dict(head=h_pick))]),
        ("It lifts the tip out, crosses to the deep-well plate in slot 2 and draws up 300 uL from well H1. The plate "
         "is cut through row H, so the level can be seen dropping.", 4.4, {},
         [(0.2, dict(head=head(tx, ty, z_trav), tip=carried(head(tx, ty, z_trav)))),
          (0.25, dict(head=head(sx, sy, z_trav), tip=carried(head(sx, sy, z_trav)))),
          (0.25, dict(head=head(sx, sy, z_asp), tip=carried(head(sx, sy, z_asp)))),
          (0.003, dict(tl=(0.0, -1.0))), (0.297, dict(src=s_after / s_h - 1.0, tl=(0.0, 0.0)))]),
        ("Over the 96-well plate in slot 3 it dispenses the 300 uL into well H1.", 4.4, {},
         [(0.2, dict(head=head(sx, sy, z_trav), tip=carried(head(sx, sy, z_trav)))),
          (0.22, dict(head=head(dx, dy, z_trav), tip=carried(head(dx, dy, z_trav)))),
          (0.25, dict(head=head(dx, dy, z_dsp), tip=carried(head(dx, dy, z_dsp)))),
          (0.003, dict(dst=(0.0, -1.0))), (0.324, dict(dst=(0.0, 0.0), tl=(0.0, -1.0))),
          (0.003, dict(tl=(hide, -1.0)))]),
        ("Then over the fixed trash in slot 12, the pipette pushes the used tip off, and it drops into the bin.",
         3.8, {},
         [(0.18, dict(head=head(dx, dy, z_trav), tip=carried(head(dx, dy, z_trav)))),
          (0.47, dict(head=head(tcx, tcy, z_trav), tip=carried(head(tcx, tcy, z_trav)))),
          (0.35, dict(tip=tip_fall))]),
        ("The head goes back to where it started, ready for the next tip.", 2.0, {},
         [(1.0, dict(head=(0.0, 0.0, 0.0)))]),
    ]
    state = dict(head=(0.0, 0.0, 0.0), tip=(0.0, 0.0, 0.0), src=0.0, dst=(hide, -1.0), tl=(hide, -1.0))
    states, taus = [], []
    for _, _, _, segs in script:
        st = [dict(state)]
        for _, chg in segs:
            state = {**state, **chg}
            st.append(dict(state))
        states.append(st)
        taus.append([t for t, _ in segs])
    zero = [[0.0] * 4 for _ in range(3)]

    def move(axis):                                            # the 3x4 matrix of a translation along axis per unit d
        m = [[0.0] * 4 for _ in range(3)]
        m[axis][3] = 1.0
        return m
    channels = {   # joint: (value of the state, comps of the path the value fills, the dwell comp)
        "gantry": (lambda s: (s["head"][1],), (1,), 0),
        "carriage": (lambda s: (s["head"][0],), (0,), 1),
        "pipette": (lambda s: (s["head"][2],), (2,), 0),
        "tipxy": (lambda s: s["tip"][:2], (0, 1), 2),
        "tip": (lambda s: (s["tip"][2],), (2,), 0),
        "source": (lambda s: (s["src"],), (2,), 0),
        "well": (lambda s: s["dst"], (0, 2), 1),
        "tipliquid": (lambda s: s["tl"], (0, 2), 1),
    }
    ends = {}
    for name, (get, comps, dwell) in channels.items():
        path, vs = _ot2_path([[get(s) for s in st] for st in states], taus, comps, dwell)
        ends[name] = vs
        if name == "gantry":
            j = trace(path, 1)
        elif name == "carriage":
            j = trace(path, 0, parent="gantry")
        elif name == "pipette":
            j = trace(path, 2, parent="carriage")
        elif name == "tipxy":
            j = Joint("follow", path=path, jac=(move(0), move(1), zero))
        elif name == "tip":
            j = trace(path, 2, parent="tipxy")
        elif name == "source":
            j = grow(s_bot, s_h, 2 * s_h)
            j.path = path
        else:     # the well, the tip's liquid: d[0] sinks an empty one 1 m (under the studio floor), d[2] grows it
            g = grow(d_bot, d_h, 2 * d_h) if name == "well" else grow(tl_z, tl_h, 2 * tl_h)
            sink = [[0.0] * 4 for _ in range(3)]
            sink[2][3] = -1000.0
            j = Joint("follow", path=path, jac=(sink, zero, g.jac[2]), parent="tip" if name == "tipliquid" else None)
        inst.joints[name] = j
    inst.joints["cover"] = Joint("slide", vec=(0.0, 0.0, 0.0), parent="carriage")
    for i, (cap, secs, extra, _) in enumerate(script):
        tg = {k: (ends[k][i - 1] if i else 0.0, ends[k][i]) for k in channels}
        tg.update(extra)
        inst.actions.append((cap, secs, tg))
    # ---- labels, camera
    sw = (sx, sy, s_bot + s_h)
    dw = (dx, dy, d_bot + d_h)
    inst.labels = [("gantry (X beam)", (-150.0, -40.0, 560.0), (0.16, 0.13)),
                   ("P300 pipette", (ox, oy - 25.0, 360.0), (0.80, 0.16)),
                   ("tip rack", (tx + 40.0, ty - 30.0, tip_top), (0.10, 0.80)),
                   ("96-well plate", (dx + 40.0, dy + 30.0, d_bot + 11.0), (0.86, 0.84))]
    fixed = [lab for lab in inst.labels if lab[0] in ("tip rack", "96-well plate")]
    inst.step_labels = {1: fixed, 2: [("deep-well plate, cut through row H", sw, (0.22, 0.85))],
                        3: [("96-well plate, cut through row H", dw, (0.78, 0.85))],
                        4: fixed + [("fixed trash", (tcx, tcy - 60.0, ttop), (0.86, 0.60))], 5: fixed}
    inst.zoom = {2: ((sx, sy + 10.0, s_bot + 30.0), 330.0), 3: ((dx, dy + 10.0, d_bot + 30.0), 330.0), 4: "out"}
    inst.cam = (1.0, -1.7, 1.05)
    inst.notes = ["Opentrons' reference STEP; the head split out of it by bounding box (OT2_SOLIDS, OT2['beam'])",
                  "one pipette per mount kept of the STEP's four variants: P20 left, P300 right",
                  "deck slots from Opentrons' ot2_standard.json, the deck surface measured off the STEP"]
    return inst


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
