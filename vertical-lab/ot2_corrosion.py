"""The Opentrons OT-2 on tray A as the CubXL's liquid station for the copper corrosion screen (#303): before a night
it makes up the CubXL's 0.1 mg/L sulfide stock in seawater, so tray A's two machines read as one corrosion station.

    xvfb-run --server-num=82 python3 ot2_corrosion.py   # -> out/instruments/ot2_corrosion_prep.{gif,png,json}, out/mp4/
    PREVIEW=1 xvfb-run --server-num=82 python3 ot2_corrosion.py     # the end of each action only, a contact sheet

Round 15 (PR #318): no acid on this deck. Sterling, 2026-11-20: "an OT-2 probably doesn't have great compatibility
with many of the solvents that would be required for ICP-MS and ICP-OES. And it would be very risky to try to put
high-hazard chemicals on a tray." Round 14 moved the ICP-MS work to a station on the floor (icpms.py, notes/icpms.md),
but this clip still diluted the tubes here: 100 uL of each into 900 uL of 2 % HNO3 from a reservoir trough, and a
matrix-matched standard. Both are gone, with the acid trough, the blank matrix, the standard and the tube block's nine
tube seats; the station's acid-rated dilutor makes the dilution and the standards in its own hood.

What it does, and where each number comes from (DAL = digital-alloy-lab alloy-corrosion/copper/protocol.md at
aeda51a, PR #180's head):
* The electrolyte. DAL's copper wells are mixed on the CubXL from seawater (ASTM D1141 without the heavy-metal stock)
  and two sulfide stocks, 10 and 0.1 mg/L S, fresh each night, "the 0.1 mg/L stock from the 10 mg/L one, not from
  solid" (DAL section 3). Here the OT-2 makes that 1:100 dilution: 1980 uL of seawater (P300: 6 x 300 + 180 uL) and
  then 20 uL of the 10 mg/L stock (P20), sulfide last, 2.0 mL in a deep well, a night's worth (the CubXL draws at most
  150 uL of it a well). This is digital-wetlab PR #83's direction 5 for the OT-2, "the electrolyte matrix"
  (grants/ot2-new-directions/README.md at aff0623, section 5); its other half, "the matrix-matched ICP-OES dilutions",
  is the station's now. DAL keeps the sulfide stocks deaerated with little headspace; an open deep well and a 20 mL
  deck vial holding 2 mL don't, which is the open question this step leaves.
* The tubes don't come here. Each corrosion well on the CubXL ends as one pre-weighed 0.5 mL PP tube: the well's
  150 uL, one 150 uL DI rinse and 20 uL of 1 M trace-metal HNO3, which the CubXL adds itself at once, from a capped
  vial (DAL section 4, steps 11-12): 320 uL at 62 mM. DAL section 9: "Only 1 M trace-metal HNO3 goes on the deck, in a
  capped vial. Dilute it from the concentrated acid in the fume hood only", and "Label them, cap them in the morning,
  and store them for ICP." The capped tubes go to the ICP-MS station (notes/icpms.md).
* The pipettes are the two in the OT-2's STEP: a P300 single (30-300 uL, Opentrons 300 uL tips) on the right mount
  for the seawater; a P20 single (1-20 uL, 20 uL tips) on the left for the 20 uL of sulfide.
* Every liquid is drawn at the height its volume gives in its own vessel, so the 3.4 mm the seawater trough drops is
  to scale too. The panel at the top right reads the volumes out as they change.

The OT-2 is Opentrons' reference STEP split into the pieces that move exactly as PR #320 does it
(instruments_round2.py at 5a39245): OT2_SOLIDS, OT2, the _ot2_* helpers, grow, trace and half are copied from there,
because #320 isn't merged into this branch. If it is merged, these should import from it instead.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np

from instruments import Instrument, Joint, _piece

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
from common import box, cyl, rbox  # noqa: E402

KEY = "ot2_corrosion_prep"          # longform.py reads out/mp4/instruments/<KEY>.mp4
NAME = f"instruments/{KEY}"

# name: (r, g, b, opacity, specular), merged into tour.MATS
MATERIALS = {   # round 15: the acid diluent, the blank matrix, the samples and the standard went with the dilution
    "oc_asw": (0.66, 0.84, 0.93, 0.80, 0.6),            # seawater, ASTM D1141 (and the 0.1 mg/L S made in it)
    "oc_asw_cut": (0.54, 0.76, 0.88, 1.0, 0.4),
    "oc_sulf": (0.92, 0.82, 0.42, 0.90, 0.5),           # the 10 mg/L sulfide stock
    "oc_tip": (0.90, 0.91, 0.88, 0.62, 0.4),            # a polypropylene pipette tip
    "oc_tube": (0.92, 0.92, 0.88, 0.55, 0.4),           # the stock's 1.5 mL PP tube
}


# ===================================================================================================== from PR #320
# grow, trace, half and the OT-2 split below are PR #320's (vertical-lab/instruments_round2.py at 5a39245), unchanged
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
    with a "path" joint on the same waypoints."""
    jac = [[[0.0] * 4 for _ in range(3)] for _ in range(3)]
    jac[axis][axis][3] = float(sign)
    return Joint("follow", path=tuple(tuple(map(float, p)) for p in path),
                 jac=tuple(tuple(map(tuple, j)) for j in jac), parent=parent)


def half(shape, y: float = 0.0, keep_back: bool = True):
    """The back half (y >= `y`) of a CadQuery shape, so a camera in front sees its section."""
    big = 5000.0
    cutter = box(-big, y - big if keep_back else y, -big, big, y if keep_back else y + big, big)
    return shape.cut(cutter)


# Opentrons' reference STEP ("OT-2 Reference Model Detailed", lab_models/vendor.py) is 26 solids. What each one is
# (PR #320): 1 the deck plate; 2-9 the acrylic; 14 the frame, with the fixed trash and the gantry's X beam fused into
# it; 10-13 the head (lid, back plate, U-shaped cover, the C-shaped carriage on the beam); 15-26 the pipettes, every
# variant drawn on both mounts (centres x -17 and +17; y -78.7): a P20 single (ending at z 301.1; 15 left, 19 right),
# a P300 (314.1; 23, 20), a P1000 (24, 21) and an 8-channel (25, 22), plus each mount's slide, up (16, 26) and down
# (18, 17).
OT2_SOLIDS = dict(deck=(1,), panels=(2, 3, 4, 5, 6, 7, 8, 9), frame=14, cover=(10, 12), carriage=(11, 13),
                  left=(15, 16), right=(20, 26), drop=(17, 18, 19, 21, 22, 23, 24, 25))
# The deck, from Opentrons' deck definition (shared-data/deck/definitions/3/ot2_standard.json): 12 slots of
# 128 x 86 mm at a pitch of 132.5 x 90.5 mm, slot 1 front left, slot 12 the fixed trash; slot 1's front-left corner
# lands at (-196.5, -213.47) here, the deck's surface 68.55 mm above the bench (PR #320).
OT2 = dict(x0=-196.5, y0=-213.47, pitch=(132.5, 90.5), deck_z=68.55,
           nozzle=(17.0, -78.74, 314.1),      # the P300's nozzle end (solid 20), mount fully up
           beam=(-274.4, -44.0, 499.0, 274.4, 32.0, 582.0),   # the X beam, inside the frame's side walls
           trash=(70.0, 55.0, 68.6, 250.0, 232.0, 160.0),   # the fixed trash's block (above the deck), in solid 14
           overlap=7.47,                      # how far a 300 uL tip seats onto the P300's nozzle (Opentrons)
           travel_z=240.0)                    # the nozzle's height between moves
P20 = dict(nozzle=(-17.0, -78.74, 301.1),     # the P20's nozzle end (solid 15), mount fully up
           overlap=8.25)                      # how far a 20 uL tip seats onto a P20 GEN2 (Opentrons' definition)


def _ot2_slot(n: int) -> tuple:
    """The front-left corner (x, y) of deck slot n (1-12)."""
    c, r = (n - 1) % 3, (n - 1) // 3
    return OT2["x0"] + OT2["pitch"][0] * c, OT2["y0"] + OT2["pitch"][1] * r


def _ot2_well(n: int, a1x: float, a1y: float, row: int, col: int, pitch: float = 9.0) -> tuple:
    """A well's centre (x, y) in an SBS labware seated in slot n, A1 a1x from its left and a1y from its back edge."""
    import labware
    x, y = _ot2_slot(n)
    return x + a1x + col * pitch, y + labware.SBS_D - a1y - row * pitch


def _ot2_seat(model, n: int):
    """A lab_models labware (centred, on z = 0) seated in slot n, as Opentrons places it: corner on the slot's."""
    import labware
    x, y = _ot2_slot(n)
    return model.moved(x + labware.SBS_W / 2, y + labware.SBS_D / 2, OT2["deck_z"])


def _ot2_path(states, taus, comps, dwell) -> tuple:
    """A follow joint's waypoints that play one channel through the actions with any timing: states[a] holds the
    channel at the start of action a and at the end of each of its segments, taus[a] each segment's share of the
    action. A path joint moves evenly by arc length, so each segment is made as long as its share of the action; where
    the channel moves less than that, the rest of the length goes along `dwell`, an axis the joint's jac ignores.
    Returns (waypoints, v at the end of every action)."""
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


# ===================================================================================================== the labware
TIP300 = dict(total=64.49, length=59.3, top_d=7.3)          # labware.tiprack("300ul")
TIP20 = dict(total=64.69, length=39.2, top_d=5.6)           # labware.tiprack("20ul")
COLLAR = 9.0                                                # labware.tiprack's collar above the rack's deck
# The stock block, printed, on an SBS footprint (ours): one seat for a 1.5 mL tube, the 10 mg/L sulfide stock, at its
# middle. Round 15: its nine 0.5 mL seats (the night's ICP-MS tubes, for the dilution) and the standard's seat are gone.
BLOCK = dict(H=28.0, hole_std=11.0)
# NEST 12-well reservoir, 15 mL (360102; Opentrons nest_12_reservoir_15ml): 127.76 x 85.48 x 31.4, troughs 8.2 x 71.2
# at a 9 mm pitch, 26.85 deep, A1 14.38 from the left. Trough 1: seawater (ASTM D1141 without the heavy metals, DAL
# protocol section 3); the rest empty (round 15: the 2 % HNO3 and the blank matrix went with the dilution).
RES = dict(H=31.4, w=8.2, l=71.2, depth=26.85, a1x=14.38, pitch=9.0, ml=12.0)
TUBE15_UL = 1000.0                                         # in the 1.5 mL tube
WELL_UL = dict(asw=1980.0, sulf=20.0)


def _revolve(pts, x=0.0, y=0.0, z=0.0) -> cq.Workplane:
    return cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0)).translate((x, y, z))


def _frustum_h(v_ul: float, r0: float, slope: float) -> float:
    """The height of liquid holding v_ul in a cone of radius r0 at its tip widening by `slope` per mm."""
    lo, hi = 0.0, 200.0
    for _ in range(60):
        h = (lo + hi) / 2
        r1 = r0 + slope * h
        v = math.pi * h / 3 * (r0 * r0 + r0 * r1 + r1 * r1)
        lo, hi = (h, hi) if v < v_ul else (lo, h)
    return (lo + hi) / 2


def _tube15_liquid(x, y, z, v_ul):
    """v_ul in an open 1.5 mL tube (labware.microtube: its bore 1.8 -> 4.35 mm in radius over 1-18.9, then ~4.42)."""
    vc = math.pi * 17.85 / 3 * (1.75 ** 2 + 1.75 * 4.30 + 4.30 ** 2)
    top = 18.9 + (v_ul - vc) / (math.pi * 4.42 ** 2)
    return _revolve([(0, 1.05), (1.75, 1.05), (4.30, 18.9), (4.42, top), (0, top)], x, y, z)


def _block(cx, cy, z):
    """The printed stock block: one seat, for the 10 mg/L sulfide stock's 1.5 mL tube. -> (the block, the seat's x, y)"""
    import labware
    blk = rbox(labware.SBS_W, labware.SBS_D, BLOCK["H"], labware.SBS_R, x=cx, y=cy, z=z)
    return blk.cut(cyl(BLOCK["hole_std"], BLOCK["H"], x=cx, y=cy, z=z + 1.0)), (cx, cy)


def _reservoir(cx, cy, z):
    import labware
    r = RES
    blk = rbox(labware.SBS_W, labware.SBS_D, r["H"], labware.SBS_R, x=cx, y=cy, z=z)
    x0 = cx - labware.SBS_W / 2 + r["a1x"]
    for i in range(12):
        blk = blk.cut(box(x0 + i * r["pitch"] - r["w"] / 2, cy - r["l"] / 2, z + r["H"] - r["depth"],
                          x0 + i * r["pitch"] + r["w"] / 2, cy + r["l"] / 2, z + r["H"] + 1))
    return blk, [(x0 + i * r["pitch"], cy) for i in range(12)], z + r["H"] - r["depth"]


# ===================================================================================================== the clip
def _move(axis):
    m = [[0.0] * 4 for _ in range(3)]
    m[axis][3] = 1.0
    return m


ZERO = [[0.0] * 4 for _ in range(3)]
SINK = [[0.0] * 4, [0.0] * 4, [0.0, 0.0, 0.0, -1000.0]]   # d[0] = 1 drops an empty vessel's liquid out of sight


def _scale_z(z0: float):
    """d[2] stretches a piece modelled from z0 by (1 + d) about z0: a liquid level."""
    return [[0.0] * 4, [0.0] * 4, [0.0, 0.0, 1.0, -z0]]


P300_TIPS = {"tipA": (0, "A1")}                    # row of column 1 (Opentrons' pick order starts at A1)
P20_TIPS = {"tipP": (0, "A1")}
TIP_LIQ = {   # piece: (its tip, uL, material)
    "tlA": ("tipA", 300.0, "oc_asw"), "tlA2": ("tipA", 180.0, "oc_asw"), "tlP": ("tipP", 20.0, "oc_sulf")}
LEVELS = ("h6", "res1")     # liquids that rise and fall, and hide while their vessel is empty


def ot2_corrosion() -> Instrument:
    import labware
    import vendor
    p = OT2
    sols = vendor._solids("ot2")
    S = lambda n: sols[n - 1]                                       # noqa: E731  the STEP's "solid n"
    ox, oy, oz = p["nozzle"]
    lx, ly, lz = P20["nozzle"]
    inst = Instrument(
        KEY, "The sulfide stock for the CubXL's corrosion screen", "Opentrons OT-2",
        (624.3, 567.4, 662.0),
        "Opentrons' reference STEP (github.com/Opentrons/ot2), split as PR #320 does it; deck slots from Opentrons' "
        "ot2_standard.json; the stocks and volumes from DAL alloy-corrosion/copper/protocol.md at aeda51a "
        "(sections 3, 4 and 9); the role from digital-wetlab PR #83, direction 5",
        props=(*P300_TIPS, *P20_TIPS, *(f"{k}_xy" for k in (*P300_TIPS, *P20_TIPS)), *TIP_LIQ, *LEVELS,
               *(q for q, _, _ in ROWS)))
    body, frame, panels = _piece(inst, "body"), _piece(inst, "frame"), _piece(inst, "panels")
    # ---- the frame solid, split (PR #320): the X beam (gantry), the fixed trash (a bin cut into its block), the rest
    beam, rest = _ot2_split(S(OT2_SOLIDS["frame"]), p["beam"])
    trash, rest = _ot2_split(rest, p["trash"])
    tb = trash.BoundingBox()
    tcx, tcy, ttop = (tb.xmin + tb.xmax) / 2, (tb.ymin + tb.ymax) / 2, tb.zmax
    walls = trash.intersect(box(-1e3, -1e3, 99.5, 1e3, 1e3, 100.5).val()).BoundingBox()
    bin_floor = 82.0
    trash = trash.cut(rbox(walls.xlen - 12, walls.ylen - 12, ttop - bin_floor + 1, 6.0, x=(walls.xmin + walls.xmax) / 2,
                           y=(walls.ymin + walls.ymax) / 2, z=bin_floor).val())
    frame.add("frame", rest, "printer_white")
    body.add("fixed trash", trash, "inst_offwhite")
    body.add("deck", S(OT2_SOLIDS["deck"][0]), "aluminium")
    for n in OT2_SOLIDS["panels"]:
        panels.add(f"acrylic {n}", S(n), "acrylic")
    _piece(inst, "gantry").add("X beam", beam, "inst_dark")
    car, cover = _piece(inst, "carriage"), _piece(inst, "cover")
    back, hook = OT2_SOLIDS["carriage"]
    car.add("back plate", S(back), "printer_white")
    car.add("carriage", S(hook), "inst_grey")
    lid, shell = OT2_SOLIDS["cover"]
    cover.add("head lid", S(lid), "printer_white")
    cover.add("head cover", S(shell), "printer_white")
    # both pipettes move in z: the P300 on the right mount, the P20 on the left
    for piece, (n, slide), what in ((_piece(inst, "p20"), OT2_SOLIDS["left"], "P20 (left mount)"),
                                    (_piece(inst, "pipette"), OT2_SOLIDS["right"], "P300 (right mount)")):
        for nm, shp, mat in _ot2_pipette(S(n), what):
            piece.add(nm, shp, mat)
        piece.add(f"{what} slide", S(slide), "inst_dark")

    # ---- labware
    dz = p["deck_z"]
    top300, top20 = dz + TIP300["total"], dz + TIP20["total"]
    tip_xy, tip_z0 = {}, {}
    for slot, kind, tips, top, length in ((1, "300ul", P300_TIPS, top300, TIP300["length"]),
                                          (4, "20ul", P20_TIPS, top20, TIP20["length"])):
        rack = _ot2_seat(labware.tiprack(kind), slot)
        sol = rack.parts[1].shape.Solids()                     # labware._grid order: A1, A2, ... B1 is index 12
        used = {12 * row: name for name, (row, _) in tips.items()}
        body.add(f"{kind} tip rack", rack.parts[0].shape, "pp_black")
        body.add(f"{kind} tips", cq.Compound.makeCompound([t for i, t in enumerate(sol) if i not in used]), "oc_tip")
        for i, name in used.items():
            _piece(inst, name).add(f"tip {tips[name][1]} ({kind})", sol[i], "oc_tip")
            _piece(inst, f"{name}_xy")                         # no parts: carries its tip in x and y
            tip_xy[name] = _ot2_well(slot, 14.38, 11.24, tips[name][0], 0)
            tip_z0[name] = top - length
    # the stock block in slot 2: the 10 mg/L sulfide stock, an open 1.5 mL tube (its lid left off)
    s2x, s2y = _ot2_slot(2)
    blk, (sfx, sfy) = _block(s2x + labware.SBS_W / 2, s2y + labware.SBS_D / 2, dz)
    body.add("stock block", blk, "pla_white")
    tz = dz + 1.0                                              # the tube's outer bottom, on its seat's floor
    mt = labware.microtube().parts[0].shape
    body.add("sulfide stock tube", mt.moved(cq.Location(cq.Vector(sfx, sfy, tz))), "oc_tube")
    body.add("10 mg/L sulfide stock", _tube15_liquid(sfx, sfy, tz, TUBE15_UL), "oc_sulf")
    # the 2 mL deep-well plate in slot 3, cut through row H: H6 takes the 0.1 mg/L S working stock
    deep = labware.PLATES["96_deep"]
    wx6 = _ot2_well(3, deep["a1x"], deep["a1y"], 7, 5)
    wx1 = _ot2_well(3, deep["a1x"], deep["a1y"], 7, 0)
    plate = _ot2_seat(labware.plate("96_deep"), 3)
    body.add("deep-well plate", half(cq.Workplane().add(plate.parts[0].shape), wx6[1]), "polystyrene")
    w_bot = dz + deep["H"] - deep["depth"]
    w_area = (deep["well"] - 0.1) ** 2
    lvl = lambda ul: ul / w_area                                # noqa: E731  height of ul in a deep well
    wl = deep["well"] / 2 - 0.05
    ref = {"h6": 2000.0}
    x6, y6 = wx6
    _piece(inst, "h6").add("H6: 0.1 mg/L S", half(box(x6 - wl, y6 - wl, w_bot, x6 + wl, y6 + wl,
                                                      w_bot + lvl(ref["h6"])), y6), "oc_asw_cut")
    # the reservoir in slot 5: seawater in trough 1, the other troughs empty
    s5x, s5y = _ot2_slot(5)
    res, troughs, r_bot = _reservoir(s5x + labware.SBS_W / 2, s5y + labware.SBS_D / 2, dz)
    body.add("12-well reservoir", res, "polypropylene")
    r_area = (RES["w"] - 0.1) * (RES["l"] - 0.1)
    r_h = RES["ml"] * 1000.0 / r_area
    sea = troughs[0]
    _piece(inst, "res1").add("seawater", box(sea[0] - RES["w"] / 2 + 0.05, sea[1] - RES["l"] / 2 + 0.05, r_bot + 0.05,
                                             sea[0] + RES["w"] / 2 - 0.05, sea[1] + RES["l"] / 2 - 0.05, r_bot + r_h),
                             "oc_asw")
    # liquid in the tips, each modelled full in its tip in the rack: a cone from the tip's end up the bore
    slope = {300: (TIP300["top_d"] / 2 - 1.7) / (TIP300["length"] - COLLAR - 2.0),
             20: (TIP20["top_d"] / 2 - 1.7) / (TIP20["length"] - COLLAR - 2.0)}
    for key, (tip, ul, mat) in TIP_LIQ.items():
        x, y = tip_xy[tip]
        k = 300 if tip in P300_TIPS else 20
        r_end = 0.30 if k == 300 else 0.25
        h = _frustum_h(ul, r_end, slope[k])
        _piece(inst, key).add(f"{ul:.0f} uL in {tip}", cq.Workplane().add(cq.Solid.makeCone(
            r_end, r_end + slope[k] * h, h, cq.Vector(x, y, tip_z0[tip] + 0.3), cq.Vector(0, 0, 1))), mat)

    # ---- the script: the head, the P20, the tips, the liquids and the read-outs, segment by segment
    o300, o20 = TIP300["length"] - p["overlap"], TIP20["length"] - P20["overlap"]   # tip end below its nozzle
    zt = p["travel_z"]

    def head(x, y, z):                               # the P300's nozzle at (x, y, z) -> the head's offset
        return (x - ox, y - oy, z - oz)

    def head20(x, y):                                # the P20's nozzle over (x, y); the P300 stays up
        return (x - lx, y - ly, 0.0)
    pick = {t: head(*tip_xy[t], top300 - p["overlap"]) for t in P300_TIPS}
    pick.update({t: (*head20(*tip_xy[t])[:2], top20 - P20["overlap"] - lz) for t in P20_TIPS})

    def a3(tip, xy, z):                              # the P300 (and its tip) with its nozzle at (x, y, z)
        h = head(*xy, z)
        return {"head": h, tip: tuple(a - b for a, b in zip(h, pick[tip]))}

    def a2(tip, xy, z):                              # the P20 (and its tip) with its nozzle at (x, y, z)
        h, z20 = head20(*xy), z - lz
        return {"head": h, "p20": z20, tip: (h[0] - pick[tip][0], h[1] - pick[tip][1], z20 - pick[tip][2])}

    def fall(tip, jx):                               # a tip pushed off over the trash, landing on the bin's floor
        x, y = tip_xy[tip]
        return {tip: (tcx - x + jx, tcy - y - 4.0, bin_floor + 0.4 - tip_z0[tip])}
    # hidden: sunk out of sight and flattened, not to zero (round 15: a zero scale is a singular matrix, which stopped
    # ARM_AUDIT's movers check, collide.Movers, on the first frame)
    hide, full, shown0 = (1.0, -0.999), (0.0, 0.0), (0.0, -0.999)

    def level(key, ul):                              # a level channel: (hidden, stretch)
        if ul <= 0:
            return hide
        if key in ref:
            return (0.0, lvl(ul) / lvl(ref[key]) - 1.0)
        return (0.0, ul / r_area / r_h - 1.0)        # the seawater trough

    asp_res = r_bot + 2.0 + o300                     # the P300's nozzle with its tip end 2 mm off the trough's floor
    dsp_top = dz + deep["H"] - 3.0 + o300            # tip end 3 mm into the well: dispensing from above the liquid
    asp_15 = tz + 1.0 + 2.0 + o20                    # 2 mm off a 1.5 mL tube's floor
    vol = dict(h6=0.0, res1=RES["ml"] * 1000.0)

    def xfer(tip, tl, src_key, src_xy, z_src, dst_key, dst_xy, z_dst, ul, f=1.0):
        """One P300 transfer from travel height and back: down, draw, up, across, down, dispense, up."""
        vol[src_key] -= ul
        first = vol[dst_key] <= 0
        vol[dst_key] += ul
        q = {"h6": "qh6", "res1": "qres1"}
        return [(0.16 * f, a3(tip, src_xy, zt)), (0.10 * f, a3(tip, src_xy, z_src)), (0.003, {tl: shown0}),
                (0.14 * f, {tl: full, "q300": ul, q[src_key]: vol[src_key], src_key: level(src_key, vol[src_key])}),
                (0.08 * f, a3(tip, src_xy, zt)), (0.15 * f, a3(tip, dst_xy, zt)), (0.07 * f, a3(tip, dst_xy, z_dst)),
                (0.003, {dst_key: shown0} if first else {}),
                (0.13 * f, {tl: shown0, "q300": 0.0, q[dst_key]: vol[dst_key], dst_key: level(dst_key, vol[dst_key])}),
                (0.003, {tl: hide}), (0.06 * f, a3(tip, dst_xy, zt))]
    asw = []
    for k in range(1, 8):                                       # 6 x 300 + 180 = 1980 uL
        ul = 300.0 if k < 7 else 180.0
        asw += xfer("tipA", "tlA" if k < 7 else "tlA2", "res1", sea, asp_res, "h6", wx6, dsp_top, ul, f=0.6)
    sulf_in = w_bot + lvl(WELL_UL["asw"]) - 3.0 + o20          # the P20's tip end 3 mm under H6's surface
    script = [
        ("The OT-2 beside the CubXL on tray A makes the CubXL's sulfide stock in seawater. Its door, windows and "
         "frame fade: a P300 on the right mount, a P20 on the left.", 2.4,
         {"~panels": (0.0, 1.0), "~frame": (0.0, 0.55), "~cover": (0.0, 0.8)}, [(1.0, {})]),
        ("Before a night: the CubXL's 0.1 mg/L sulfide stock, made from its 10 mg/L stock, not from solid (DAL "
         "protocol §3). The P300 takes a tip and puts 300 µL of seawater (ASTM D1141) from trough 1 into deep well H6.",
         4.6, {}, [(0.62, {"head": head(*tip_xy["tipA"], zt)}), (0.38, {"head": pick["tipA"]}),
                   (0.12, a3("tipA", tip_xy["tipA"], zt))] + asw[:11]),
        ("Six more transfers, five of 300 µL and one of 180: 1980 µL, all from above the liquid. The tip goes into "
         "the trash.", 5.4, {},
         asw[11:] + [(0.30, a3("tipA", (tcx, tcy), zt)), (0.003, {}), (0.22, fall("tipA", -24.0))]),
        ("Sulfide last: the P20 adds 20 µL of the 10 mg/L stock below the surface: 2.0 mL at 0.1 mg/L S, a night's "
         "worth, for the CubXL's 0.1 mg/L vial.", 5.0, {},
         [(0.10, {"head": (*head(tcx, tcy, zt)[:2], 0.0)}), (0.14, {"head": head20(*tip_xy["tipP"]), "p20": zt - lz}),
          (0.08, {"p20": pick["tipP"][2]}), (0.07, a2("tipP", tip_xy["tipP"], zt)), (0.12, a2("tipP", (sfx, sfy), zt)),
          (0.08, a2("tipP", (sfx, sfy), asp_15)), (0.003, dict(tlP=shown0)), (0.08, dict(tlP=full, q20=20.0)),
          (0.06, a2("tipP", (sfx, sfy), zt)), (0.14, a2("tipP", wx6, zt)), (0.07, a2("tipP", wx6, sulf_in)),
          (0.08, dict(tlP=shown0, q20=0.0, qh6=2000.0, h6=level("h6", 2000.0))), (0.003, dict(tlP=hide)),
          (0.06, a2("tipP", wx6, zt)), (0.20, a2("tipP", (tcx, tcy), zt)), (0.003, {}),
          (0.18, fall("tipP", 24.0))]),
        # round 15 (PR #318, Sterling 2026-11-20: acids off the trays): the ICP-MS dilution and standard that followed
        # here moved to the floor's ICP-MS station (icpms.py); the clip ends with where the tubes go instead
        ("The head parks. No acid on this deck: the CubXL adds 20 µL of 1 M HNO3 to each of its tubes itself, and "
         "the capped tubes go to the ICP-MS station on the floor, whose dilutor in a metal-free fume hood makes the "
         "10x dilution.", 6.0, {}, [(0.35, {"head": (0.0, 0.0, 0.0), "p20": 0.0}), (0.65, {})]),
    ]
    state = dict(head=(0.0, 0.0, 0.0), p20=0.0, q300=0.0, q20=0.0, qh6=0.0, qres1=RES["ml"] * 1000.0,
                 h6=hide, res1=level("res1", RES["ml"] * 1000.0),
                 **{t: (0.0, 0.0, 0.0) for t in (*P300_TIPS, *P20_TIPS)}, **{k: hide for k in TIP_LIQ})
    states, taus = [], []
    for _, _, _, segs in script:
        st = [dict(state)]
        for _, chg in segs:
            state = {**state, **chg}
            st.append(dict(state))
        states.append(st)
        tot = sum(t for t, _ in segs)
        taus.append([t / tot for t, _ in segs])        # each action's shares sum to 1, as _ot2_path assumes
    sc1 = lambda k: (lambda s: (s[k],))              # noqa: E731
    sv = lambda k: (lambda s: s[k])                  # noqa: E731
    tips = (*P300_TIPS, *P20_TIPS)
    channels = {   # joint: (value of the state, comps of the path the value fills, the dwell comp)
        "gantry": (lambda s: (s["head"][1],), (1,), 0),
        "carriage": (lambda s: (s["head"][0],), (0,), 1),
        "pipette": (lambda s: (s["head"][2],), (2,), 0),
        "p20": (sc1("p20"), (2,), 0),
        **{f"{t}_xy": ((lambda tt: lambda s: s[tt][:2])(t), (0, 1), 2) for t in tips},
        **{t: ((lambda tt: lambda s: (s[tt][2],))(t), (2,), 0) for t in tips},
        **{k: (sv(k), (0, 2), 1) for k in (*TIP_LIQ, *LEVELS)},
        **{q: (sc1(q), (0,), 1) for q, _, _ in ROWS},
    }
    z0s = {**{k: tip_z0[t] + 0.3 for k, (t, _, _) in TIP_LIQ.items()}, "h6": w_bot, "res1": r_bot + 0.05}
    parents = {"carriage": "gantry", "pipette": "carriage", "p20": "carriage", **{t: f"{t}_xy" for t in tips},
               **{k: t for k, (t, _, _) in TIP_LIQ.items()}}
    ends = {}
    for name, (get, comps, dwell) in channels.items():
        path, vs = _ot2_path([[get(s) for s in st] for st in states], taus, comps, dwell)
        ends[name] = vs
        par = parents.get(name)
        if name in ("gantry", "carriage", "pipette", "p20") or name in tips:
            j = trace(path, {"gantry": 1, "carriage": 0}.get(name, 2), parent=par)
        elif name.endswith("_xy"):
            j = Joint("follow", path=path, jac=(_move(0), _move(1), ZERO))
        elif comps == (0, 2):
            j = Joint("follow", path=path, jac=(SINK, ZERO, _scale_z(z0s[name])), parent=par)
        else:                                      # a read-out: the value is the group's x translation
            j = Joint("follow", path=path, jac=(_move(0), ZERO, ZERO))
        inst.joints[name] = j
    inst.joints["cover"] = Joint("slide", vec=(0.0, 0.0, 0.0), parent="carriage")
    for i, (cap, secs, extra, _) in enumerate(script):
        tg = {k: (ends[k][i - 1] if i else 0.0, ends[k][i]) for k in channels}
        tg.update(extra)
        inst.actions.append((cap, secs, tg))

    # ---- labels, camera (what is ours is marked so; the OT-2, its pipettes, tips, plate and reservoir are bought)
    blk_lbl = ("stock block (ours):\n10 mg/L S, 1.5 mL tube", (sfx, sfy, tz + 40.0), (0.16, 0.62))
    plate_lbl = ("2 mL deep-well plate,\ncut through row H", (wx1[0] + 30.0, wx1[1] + 4.0, dz + deep["H"]), (0.86, 0.60))
    asw_lbl = ("trough 1: seawater", (sea[0], sea[1] + 20.0, r_bot + r_h), (0.16, 0.40))
    h6_lbl = ("deep well H6", (x6, y6 + 4.0, w_bot + 25.0), (0.84, 0.62))
    trash_lbl = ("fixed trash", (tcx - 50.0, tcy - 70.0, ttop), (0.80, 0.42))
    inst.labels = [("P300, right mount", (ox, oy - 25.0, 360.0), (0.78, 0.40)),
                   ("P20, left mount", (lx, ly - 25.0, 350.0), (0.20, 0.30)), blk_lbl, plate_lbl]
    inst.step_labels = {
        1: [asw_lbl, h6_lbl], 2: [asw_lbl, h6_lbl, trash_lbl],
        3: [("10 mg/L S stock", (sfx, sfy, tz + 40.0), (0.20, 0.62)), h6_lbl],
        4: [("deep well H6: 2.0 mL\nat 0.1 mg/L S, for the CubXL", (x6, y6 + 4.0, w_bot + 25.0), (0.84, 0.62)),
            ("NEST 12-well reservoir:\nseawater only, no acid", (sea[0], sea[1] + 20.0, r_bot + r_h), (0.16, 0.40)),
            blk_lbl],
    }
    mid = lambda r, w: ((r[0] + w[0]) / 2, (r[1] + w[1]) / 2, dz + 30.0)   # noqa: E731
    inst.zoom = {1: (mid(sea, wx6), 620.0), 3: ((0.0, -100.0, dz + 30.0), 800.0), 4: "out"}
    inst.cam = (0.75, -1.6, 1.25)
    inst.notes = ["Opentrons' reference STEP; the head split out of it by bounding box as in PR #320",
                  "P300 single (right) and P20 single (left), the STEP's own; tips from Opentrons' labware sizes",
                  "stocks and volumes from DAL alloy-corrosion/copper/protocol.md at aeda51a; round 15: no acid on the "
                  "deck, the ICP-MS dilution is the floor station's (icpms.py)"]
    return inst


# ===================================================================================================== the read-out
def _gv(sc, key) -> float:
    m = sc.gmat.get(key)
    return 0.0 if m is None else float(m[0, 3])


ROWS = (("q300", "P300 tip", "{:.0f} µL"), ("q20", "P20 tip", "{:.0f} µL"),
        ("qres1", "seawater, trough 1", "{:.2f} mL"), ("qh6", "H6: 0.1 mg/L S", "{:.0f} µL"))


def draw_volumes(sc, img, s):
    """The volumes, live, at the top right: the two tips, the seawater and H6."""
    from PIL import ImageDraw
    from scene import font
    k = f"{KEY}:"
    if k + "q300" not in sc.gmat:
        return
    rows = ROWS
    vals = {c: _gv(sc, k + c) / (1000.0 if "mL" in fmt else 1.0) for c, _, fmt in rows}
    prev = getattr(sc, "_oc_prev", {}).get(img.size)
    sc.__dict__.setdefault("_oc_prev", {})[img.size] = dict(vals)
    W, H = img.size
    d = ImageDraw.Draw(img, "RGBA")
    fh, fr, fb = font(13.5 * s, bold=True), font(13 * s), font(13 * s, bold=True)
    x1, y0 = W - 10 * s, 46 * s
    x0 = x1 - 236 * s
    lh = 19 * s
    d.rounded_rectangle((x0, y0, x1, y0 + 30 * s + lh * len(rows)), 6 * s, fill=(255, 255, 255, 232),
                        outline=(150, 156, 164, 255))
    d.text((x0 + 10 * s, y0 + 6 * s), "Volumes, drawn to scale", font=fh, fill=(20, 20, 24))
    for i, (c, name, fmt) in enumerate(rows):
        y = y0 + 27 * s + i * lh
        moving = prev is not None and c in prev and abs(vals[c] - prev[c]) > 1e-6
        col = (200, 80, 20) if moving else (40, 42, 48)
        d.text((x0 + 10 * s, y), name, font=fb if moving else fr, fill=col)
        txt = fmt.format(max(vals[c], 0.0))
        d.text((x1 - 10 * s - d.textlength(txt, font=fb), y), txt, font=fb if moving else fr, fill=col)


def _install_plot():
    """Draw the read-out through instruments_lab's per-scene overlay hook; if that module can't be imported, wrap
    Scene.overlay here the same way, for this scene only."""
    try:
        import instruments_lab as IL
        IL.PLOTS[NAME] = draw_volumes
        return
    except Exception as e:                       # noqa: BLE001  the hook is all this needs from it
        print(f"  instruments_lab not importable ({e}); drawing the read-out with a hook of its own", flush=True)
    import scene as S
    orig = S.Scene.overlay

    def overlay(self, img, scale, anchors):
        img = orig(self, img, scale, anchors)
        if self.name == NAME and not S.CLEAN:
            draw_volumes(self, img, max(scale, 0.80))
        return img
    S.Scene.overlay = overlay


def _install_fluids():
    """The liquids are not obstacles for ARM_AUDIT's movers check (collide.py skips sc.fluids), as in the chapters: a
    tip dips into the seawater and H6, and each tip's liquid is drawn inside it (round 15)."""
    import scene as S
    if getattr(S.Scene.step, "_ot2_fluids", False):
        return
    orig = S.Scene.step

    def step(self, *a, **kw):
        if self.name == NAME:
            wet = {f"{KEY}:{k}" for k in (*TIP_LIQ, *LEVELS)}
            self.fluids = set(getattr(self, "fluids", set())) | {n for n, g in self.group_of.items() if g in wet}
        return orig(self, *a, **kw)
    step._ot2_fluids = True
    S.Scene.step = step


_install_plot()
_install_fluids()
REGISTRY = {KEY: ot2_corrosion}

if __name__ == "__main__":
    import tour
    tour.MATS.update(MATERIALS)
    inst = ot2_corrosion()
    print(tour.fit_report(inst), flush=True)
    print(tour.tour_one(inst, tour.piece_entries(inst)), flush=True)
