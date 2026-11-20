"""The Opentrons OT-2 on tray A as the CubXL's liquid station for the copper corrosion screen (#303): before a night
it makes up one of the CubXL's electrolyte stocks, and after the night it dilutes each ICP-MS tube 10x in dilute nitric
acid and makes a matrix-matched standard, so tray A's two machines read as one corrosion station.

    xvfb-run --server-num=82 python3 ot2_corrosion.py   # -> out/instruments/ot2_corrosion_prep.{gif,png,json}, out/mp4/
    PREVIEW=1 xvfb-run --server-num=82 python3 ot2_corrosion.py     # the end of each action only, a contact sheet

What it does, and where each number comes from (DAL = digital-alloy-lab alloy-corrosion/copper/protocol.md at
aeda51a, PR #180's head):
* The electrolyte. DAL's copper wells are mixed on the CubXL from seawater (ASTM D1141 without the heavy-metal stock)
  and two sulfide stocks, 10 and 0.1 mg/L S, fresh each night, "the 0.1 mg/L stock from the 10 mg/L one, not from
  solid" (DAL section 3). Here the OT-2 makes that 1:100 dilution: 1980 uL of seawater (P300: 6 x 300 + 180 uL) and
  then 20 uL of the 10 mg/L stock (P20), sulfide last, 2.0 mL in a deep well, a night's worth (the CubXL draws at most
  150 uL of it a well). DAL keeps the sulfide stocks deaerated with little headspace; an open deep well and a 20 mL deck
  vial holding 2 mL don't, which is the open question this step leaves.
* The tubes. Each corrosion well on the CubXL ends as one pre-weighed 0.5 mL PP tube: the well's 150 uL plus one
  150 uL DI rinse, then 20 uL of 1 M trace-metal HNO3, 320 uL (DAL section 4, steps 11-12). A night is eight wells plus
  the stock blank: nine tubes.
* The dilution. "ICP-MS with a collision cell, after a 10x dilution in dilute HNO3" (DAL section 6): here 100 uL of the
  tube into 900 uL of 2 % HNO3, 1.0 mL in a 2 mL deep well, which leaves 220 uL in the tube for a re-run.
* The standard. 10 uL of a 1 mg/L multi-element standard (Cu, Ni, Fe, Mn, Al) into 990 uL of blank matrix (seawater
  diluted as the samples are, in 2 % HNO3): 10 ug/L, matrix-matched. This one is our example of what digital-wetlab
  PR #83's direction 5 asks the OT-2 for ("the electrolyte matrix ... the matrix-matched ICP-OES dilutions",
  grants/ot2-new-directions/README.md at aff0623, section 5); DAL's protocol names no standards.
* The pipettes are the two in the OT-2's STEP: a P300 single (30-300 uL, Opentrons 300 uL tips) on the right mount
  for the seawater, the diluent, the sample and the mixing; a P20 single (1-20 uL, 20 uL tips) on the left for the
  20 and 10 uL.
* Every liquid is drawn at the height its volume gives in its own vessel, so the 10 uL and the 1.5 mm the acid trough
  drops are to scale too. The panel at the top right reads the volumes out as they change.

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
MATERIALS = {
    "oc_diluent": (0.55, 0.76, 0.96, 0.80, 0.6),        # 2 % HNO3, the samples' diluent
    "oc_diluent_cut": (0.42, 0.66, 0.92, 1.0, 0.4),
    "oc_blank": (0.50, 0.80, 0.78, 0.85, 0.5),          # the matrix-matched blank
    "oc_blank_cut": (0.38, 0.70, 0.68, 1.0, 0.4),
    "oc_sample": (0.18, 0.58, 0.60, 0.85, 0.5),         # a tube from the CubXL: seawater, metal, HNO3
    "oc_sample_cut": (0.14, 0.50, 0.52, 1.0, 0.4),
    "oc_std": (0.95, 0.55, 0.15, 0.90, 0.5),            # the 1 mg/L multi-element standard
    "oc_asw": (0.66, 0.84, 0.93, 0.80, 0.6),            # seawater, ASTM D1141 (and the 0.1 mg/L S made in it)
    "oc_asw_cut": (0.54, 0.76, 0.88, 1.0, 0.4),
    "oc_sulf": (0.92, 0.82, 0.42, 0.90, 0.5),           # the 10 mg/L sulfide stock
    "oc_tip": (0.90, 0.91, 0.88, 0.62, 0.4),            # a polypropylene pipette tip
    "oc_tube": (0.92, 0.92, 0.88, 0.55, 0.4),           # a 0.5 mL PP tube, cut
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
# The tube block, printed, on an SBS footprint (ours): the night's 0.5 mL PP tubes on DAL's 2 x 8 rack pitch (12 mm
# in x, 18 mm between rows; plot_deck_layout.py TUBE_X, TUBE_Y), tubes 1-8 (the eight wells) in the front row, tube 9
# (the stock blank) behind, and two 1.5 mL tubes: the 10 mg/L sulfide stock and the ICP-MS standard. The block is cut
# through the front row, so tube 1 shows.
BLOCK = dict(H=28.0, dx=12.0, dy=18.0, hole=8.4, hole_std=11.0, std_x=30.0, sulf_x=4.0)
TUBE05 = dict(L=30.5, rim_z=29.0, rim_r=4.6, floor=0.8, r0=0.7, cone_z=13.0, r1=3.0, r_top=3.25, ul=320.0)
# NEST 12-well reservoir, 15 mL (360102; Opentrons nest_12_reservoir_15ml): 127.76 x 85.48 x 31.4, troughs 8.2 x 71.2
# at a 9 mm pitch, 26.85 deep, A1 14.38 from the left. Trough 1: 2 % HNO3; trough 2: seawater (ASTM D1141 without
# the heavy metals, DAL protocol section 3); trough 3: the blank matrix.
RES = dict(H=31.4, w=8.2, l=71.2, depth=26.85, a1x=14.38, pitch=9.0, ml=12.0, ml3=10.0)
TUBE15_UL = 1000.0                                         # in each 1.5 mL tube
WELL_UL = dict(asw=1980.0, sulf=20.0, diluent=900.0, sample=100.0, mix=250.0, blank=990.0, std=10.0)


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


def _tube05_level(v_ul: float) -> float:
    """Height above the tube's outer bottom of v_ul in a 0.5 mL tube (TUBE05: a cone, then a near-cylinder)."""
    t = TUBE05
    hc = t["cone_z"] - t["floor"]
    slope = (t["r1"] - t["r0"]) / hc
    vc = math.pi * hc / 3 * (t["r0"] ** 2 + t["r0"] * t["r1"] + t["r1"] ** 2)
    if v_ul <= vc:
        return t["floor"] + _frustum_h(v_ul, t["r0"], slope)
    return t["cone_z"] + (v_ul - vc) / (math.pi * t["r1"] ** 2)


def _tube05(x, y, z):
    """A 0.5 mL PP tube standing at (x, y, z): its wall, open at the top."""
    t = TUBE05
    outer = _revolve([(0, 0), (1.5, 0), (3.6, t["cone_z"]), (3.95, t["rim_z"]), (t["rim_r"], t["rim_z"]),
                      (t["rim_r"], t["L"]), (0, t["L"])], x, y, z)
    inner = _revolve([(0, t["floor"]), (t["r0"], t["floor"]), (t["r1"], t["cone_z"]), (t["r_top"], t["L"] + 1),
                      (0, t["L"] + 1)], x, y, z)
    return outer.cut(inner)


def _tube05_liquid(x, y, z, v_ul):
    """(the cone of liquid, a cylinder on it up to v_ul's level, its height) in a 0.5 mL tube at (x, y, z)."""
    t = TUBE05
    r0, r1 = t["r0"] - 0.03, t["r1"] - 0.03
    cone = _revolve([(0, t["floor"] + 0.05), (r0, t["floor"] + 0.05), (r1, t["cone_z"]), (0, t["cone_z"])], x, y, z)
    h = _tube05_level(v_ul) - t["cone_z"]
    return cone, cyl(2 * r1, h, x=x, y=y, z=z + t["cone_z"]), h


def _tube15_liquid(x, y, z, v_ul):
    """v_ul in an open 1.5 mL tube (labware.microtube: its bore 1.8 -> 4.35 mm in radius over 1-18.9, then ~4.42)."""
    vc = math.pi * 17.85 / 3 * (1.75 ** 2 + 1.75 * 4.30 + 4.30 ** 2)
    top = 18.9 + (v_ul - vc) / (math.pi * 4.42 ** 2)
    return _revolve([(0, 1.05), (1.75, 1.05), (4.30, 18.9), (4.42, top), (0, top)], x, y, z)


def _block(cx, cy, z):
    """The printed tube block: nine 0.5 mL tube holes, and two for 1.5 mL tubes (the sulfide stock, the standard)."""
    import labware
    b = BLOCK
    blk = rbox(labware.SBS_W, labware.SBS_D, b["H"], labware.SBS_R, x=cx, y=cy, z=z)
    holes = [(cx - 3.5 * b["dx"] + b["dx"] * k, cy - b["dy"] / 2) for k in range(8)] + \
        [(cx - 3.5 * b["dx"], cy + b["dy"] / 2)]
    for hx, hy in holes:
        blk = blk.cut(cyl(b["hole"], b["H"], x=hx, y=hy, z=z + 1.0))
    big = [(cx + b["sulf_x"], cy + b["dy"] / 2), (cx + b["std_x"], cy + b["dy"] / 2)]
    for hx, hy in big:
        blk = blk.cut(cyl(b["hole_std"], b["H"], x=hx, y=hy, z=z + 1.0))
    return blk, holes, big


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


P300_TIPS = {"tipA": (0, "A1"), "tipB": (1, "B1"), "tipC": (2, "C1")}     # rows of column 1, Opentrons' pick order
P20_TIPS = {"tipP": (0, "A1"), "tipQ": (1, "B1")}
TIP_LIQ = {   # piece: (its tip, uL, material)
    "tlA": ("tipA", 300.0, "oc_asw"), "tlA2": ("tipA", 180.0, "oc_asw"), "tlB": ("tipB", 300.0, "oc_diluent"),
    "tlC1": ("tipC", 100.0, "oc_sample"), "tlC2": ("tipC", 250.0, "oc_diluent"), "tlP": ("tipP", 20.0, "oc_sulf"),
    "tlQ": ("tipQ", 10.0, "oc_std")}
LEVELS = ("h6", "h1", "h12", "t1", "res1", "res2")     # liquids that rise and fall, and hide while their vessel is empty


def ot2_corrosion() -> Instrument:
    import labware
    import vendor
    p = OT2
    sols = vendor._solids("ot2")
    S = lambda n: sols[n - 1]                                       # noqa: E731  the STEP's "solid n"
    ox, oy, oz = p["nozzle"]
    lx, ly, lz = P20["nozzle"]
    inst = Instrument(
        KEY, "Electrolyte and ICP-MS sample prep for the CubXL's corrosion screen", "Opentrons OT-2",
        (624.3, 567.4, 662.0),
        "Opentrons' reference STEP (github.com/Opentrons/ot2), split as PR #320 does it; deck slots from Opentrons' "
        "ot2_standard.json; the stocks, tubes and volumes from DAL alloy-corrosion/copper/protocol.md at aeda51a "
        "(sections 3, 4 and 6); the role from digital-wetlab PR #83, direction 5",
        props=(*P300_TIPS, *P20_TIPS, *(f"{k}_xy" for k in (*P300_TIPS, *P20_TIPS)), *TIP_LIQ, *LEVELS, "night",
               "before", *(q for q, _, _, _ in ROWS), "qphase"))
    body, frame, panels = _piece(inst, "body"), _piece(inst, "frame"), _piece(inst, "panels")
    night, before = _piece(inst, "night"), _piece(inst, "before")       # what is on the deck only after / before
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
    # the tube block in slot 2, cut through its front row; the night's tubes appear after the night
    s2x, s2y = _ot2_slot(2)
    blk, holes, ((sfx, sfy), (stx, sty)) = _block(s2x + labware.SBS_W / 2, s2y + labware.SBS_D / 2, dz)
    cut_y = holes[0][1]
    body.add("tube block", half(blk, cut_y), "pla_white")
    tz = dz + 1.0                                              # the tubes' outer bottoms, on the holes' floors
    for i, (hx, hy) in enumerate(holes):
        front = i < 8
        shell_ = _tube05(hx, hy, tz)
        night.add(f"tube {i + 1}", half(shell_, cut_y) if front else shell_, "oc_tube")
        cone, cylp, h320 = _tube05_liquid(hx, hy, tz, TUBE05["ul"])
        if front:
            cone, cylp = half(cone, cut_y), half(cylp, cut_y)
        night.add(f"tube {i + 1} liquid cone", cone, "oc_sample_cut" if front else "oc_sample")
        if i == 0:
            _piece(inst, "t1").add("tube 1 liquid", cylp, "oc_sample_cut")
        else:
            night.add(f"tube {i + 1} liquid", cylp, "oc_sample_cut" if front else "oc_sample")
    t1x, t1y = holes[0]
    h220 = _tube05_level(TUBE05["ul"] - WELL_UL["sample"]) - TUBE05["cone_z"]
    mt = labware.microtube().parts[0].shape                    # an open 1.5 mL tube, its lid left off
    before.add("sulfide stock tube", mt.moved(cq.Location(cq.Vector(sfx, sfy, tz))), "oc_tube")
    before.add("10 mg/L sulfide stock", _tube15_liquid(sfx, sfy, tz, TUBE15_UL), "oc_sulf")
    night.add("standard's tube", mt.moved(cq.Location(cq.Vector(stx, sty, tz))), "oc_tube")
    night.add("1 mg/L standard", _tube15_liquid(stx, sty, tz, TUBE15_UL), "oc_std")
    # the 2 mL deep-well plate in slot 3, cut through row H: H6 the sulfide working stock, H1 sample 1, H12 a standard
    deep = labware.PLATES["96_deep"]
    wx = {c: _ot2_well(3, deep["a1x"], deep["a1y"], 7, c - 1) for c in (1, 6, 12)}
    plate = _ot2_seat(labware.plate("96_deep"), 3)
    body.add("deep-well plate", half(cq.Workplane().add(plate.parts[0].shape), wx[1][1]), "polystyrene")
    w_bot = dz + deep["H"] - deep["depth"]
    w_area = (deep["well"] - 0.1) ** 2
    lvl = lambda ul: ul / w_area                                # noqa: E731  height of ul in a deep well
    wl = deep["well"] / 2 - 0.05
    ref = {"h6": 2000.0, "h1": 1000.0, "h12": 1000.0}
    for key, col, mat, what in (("h6", 6, "oc_asw_cut", "0.1 mg/L S"), ("h1", 1, "oc_diluent_cut", "sample 1, 10x"),
                                ("h12", 12, "oc_blank_cut", "standard")):
        x, y = wx[col]
        _piece(inst, key).add(f"H{col}: {what}", half(box(x - wl, y - wl, w_bot, x + wl, y + wl,
                                                          w_bot + lvl(ref[key])), y), mat)
    # the reservoir in slot 5
    s5x, s5y = _ot2_slot(5)
    res, troughs, r_bot = _reservoir(s5x + labware.SBS_W / 2, s5y + labware.SBS_D / 2, dz)
    body.add("12-well reservoir", res, "polypropylene")
    r_area = (RES["w"] - 0.1) * (RES["l"] - 0.1)
    r_h = RES["ml"] * 1000.0 / r_area

    def trough(i, h):
        x, y = troughs[i]
        return box(x - RES["w"] / 2 + 0.05, y - RES["l"] / 2 + 0.05, r_bot + 0.05, x + RES["w"] / 2 - 0.05,
                   y + RES["l"] / 2 - 0.05, r_bot + h)
    _piece(inst, "res1").add("2% HNO3", trough(0, r_h), "oc_diluent")
    _piece(inst, "res2").add("seawater", trough(1, r_h), "oc_asw")
    night.add("blank matrix", trough(2, RES["ml3"] * 1000.0 / r_area), "oc_blank")
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
    hide, full, shown0 = (1.0, -1.0), (0.0, 0.0), (0.0, -0.999)

    def level(key, ul):                              # a level channel: (hidden, stretch)
        if ul <= 0:
            return hide
        if key in ref:
            return (0.0, lvl(ul) / lvl(ref[key]) - 1.0)
        if key == "t1":
            return (0.0, (_tube05_level(ul) - TUBE05["cone_z"]) / h320 - 1.0)
        return (0.0, ul / r_area / r_h - 1.0)        # a reservoir trough

    res = {0: troughs[0], 1: troughs[1]}
    asp_res = r_bot + 2.0 + o300                     # the P300's nozzle with its tip end 2 mm off the trough's floor
    dsp_top = dz + deep["H"] - 3.0 + o300            # tip end 3 mm into the well: dispensing from above the liquid
    in_well = w_bot + 2.0 + o300                     # tip end 2 mm off the well's floor
    asp_t1 = tz + TUBE05["floor"] + 1.5 + o300       # 1.5 mm off the tube's floor
    asp_15 = tz + 1.0 + 2.0 + o20                    # 2 mm off a 1.5 mL tube's floor
    vol = dict(h6=0.0, h1=0.0, h12=WELL_UL["blank"], t1=TUBE05["ul"], res1=RES["ml"] * 1000.0,
               res2=RES["ml"] * 1000.0)

    def xfer(tip, tl, src_key, src_xy, z_src, dst_key, dst_xy, z_dst, ul, f=1.0):
        """One P300 transfer from travel height and back: down, draw, up, across, down, dispense, up."""
        vol[src_key] -= ul
        first = vol[dst_key] <= 0
        vol[dst_key] += ul
        q = {"h6": "qh6", "h1": "qh1", "res1": "qres1", "res2": "qres2", "t1": "qt1"}
        return [(0.16 * f, a3(tip, src_xy, zt)), (0.10 * f, a3(tip, src_xy, z_src)), (0.003, {tl: shown0}),
                (0.14 * f, {tl: full, "q300": ul, q[src_key]: vol[src_key], src_key: level(src_key, vol[src_key])}),
                (0.08 * f, a3(tip, src_xy, zt)), (0.15 * f, a3(tip, dst_xy, zt)), (0.07 * f, a3(tip, dst_xy, z_dst)),
                (0.003, {dst_key: shown0} if first else {}),
                (0.13 * f, {tl: shown0, "q300": 0.0, q[dst_key]: vol[dst_key], dst_key: level(dst_key, vol[dst_key])}),
                (0.003, {tl: hide}), (0.06 * f, a3(tip, dst_xy, zt))]
    asw = []
    for k in range(1, 8):                                       # 6 x 300 + 180 = 1980 uL
        ul = 300.0 if k < 7 else 180.0
        asw += xfer("tipA", "tlA" if k < 7 else "tlA2", "res2", res[1], asp_res, "h6", wx[6], dsp_top, ul, f=0.6)
    dil = [xfer("tipB", "tlB", "res1", res[0], asp_res, "h1", wx[1], dsp_top, 300.0, f=1.0 if k == 0 else 0.65)
           for k in range(3)]
    mix = []
    for _ in range(3):
        mix += [(0.003, dict(tlC2=shown0)),
                (0.14, dict(tlC2=full, q300=WELL_UL["mix"], qh1=1000.0 - WELL_UL["mix"],
                            h1=level("h1", 1000.0 - WELL_UL["mix"]))),
                (0.14, dict(tlC2=shown0, q300=0.0, qh1=1000.0, h1=level("h1", 1000.0))), (0.003, dict(tlC2=hide))]
    sulf_in = w_bot + lvl(WELL_UL["asw"]) - 3.0 + o20          # the P20's tip end 3 mm under H6's surface
    std_in = w_bot + lvl(WELL_UL["blank"]) - 3.0 + o20
    script = [
        ("The OT-2 beside the CubXL on tray A makes the corrosion screen's liquids. Its door, windows and frame "
         "fade: a P300 on the right mount, a P20 on the left.", 2.4,
         {"~panels": (0.0, 1.0), "~frame": (0.0, 0.55), "~cover": (0.0, 0.8)}, [(1.0, {})]),
        ("Before a night: the CubXL's 0.1 mg/L sulfide stock, made from its 10 mg/L stock, not from solid (DAL "
         "protocol §3). The P300 takes a tip and puts 300 µL of seawater (ASTM D1141) from trough 2 into deep well H6.",
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
          (0.06, a2("tipP", (sfx, sfy), zt)), (0.14, a2("tipP", wx[6], zt)), (0.07, a2("tipP", wx[6], sulf_in)),
          (0.08, dict(tlP=shown0, q20=0.0, qh6=2000.0, h6=level("h6", 2000.0))), (0.003, dict(tlP=hide)),
          (0.06, a2("tipP", wx[6], zt)), (0.20, a2("tipP", (tcx, tcy), zt)), (0.003, {}),
          (0.18, fall("tipP", 24.0))]),
        ("After the night: H6's stock has gone to the CubXL's vial, and the night's nine 0.5 mL tubes are in slot 2, "
         "320 µL each: a well's 150 µL, a 150 µL DI rinse and 20 µL of 1 M HNO3 (DAL protocol §4).", 3.6,
         {"night": (0.0, 1.0), "before": (1.0, 0.0)},
         [(0.30, {"head": (0.0, 0.0, 0.0), "p20": 0.0}), (0.003, dict(h6=hide, qh6=0.0, t1=level("t1", 320.0),
                                                                      res1=level("res1", 12000.0), qphase=1.0,
                                                                      h12=level("h12", WELL_UL["blank"]),
                                                                      res2=hide)),
          (0.40, {}), (0.62 * 0.5, {"head": head(*tip_xy["tipB"], zt)}), (0.38 * 0.5, {"head": pick["tipB"]})]),
        ("A fresh tip draws 300 µL of 2% HNO3 from trough 1 and dispenses it into deep well H1 from above the liquid, "
         "so it touches nothing but the acid.", 4.6, {}, [(0.12, a3("tipB", tip_xy["tipB"], zt))] + dil[0]),
        ("Twice more: 900 µL in H1. The same tip would give each of the nine samples' wells its 900 µL.", 3.8, {},
         dil[1] + dil[2]),
        ("That tip goes into the trash, and the P300 takes a fresh one for the sample.", 3.4, {},
         [(0.32, a3("tipB", (tcx, tcy), zt)), (0.003, {}), (0.25, fall("tipB", -8.0)),
          (0.28, {"head": head(*tip_xy["tipC"], zt)}), (0.15, {"head": pick["tipC"]})]),
        ("100 µL of tube 1 into H1's 900 µL: 1.0 mL, the 10x dilution in dilute HNO3 that DAL's protocol asks for "
         "before ICP-MS (§6). 220 µL stay in the tube for a re-run.", 4.8, {},
         [(0.10, a3("tipC", tip_xy["tipC"], zt)), (0.16, a3("tipC", (t1x, t1y), zt)),
          (0.12, a3("tipC", (t1x, t1y), asp_t1)), (0.003, dict(tlC1=shown0)),
          (0.12, dict(tlC1=full, q300=WELL_UL["sample"], qt1=220.0, t1=level("t1", 220.0))),
          (0.08, a3("tipC", (t1x, t1y), zt)), (0.16, a3("tipC", wx[1], zt)), (0.10, a3("tipC", wx[1], in_well)),
          (0.12, dict(tlC1=shown0, q300=0.0, qh1=1000.0, h1=level("h1", 1000.0))), (0.003, dict(tlC1=hide))]),
        ("It mixes in the well: three times 250 µL up and back.", 2.8, {}, mix),
        ("The tip goes into the trash. Tubes 2 to 9 get the same, a fresh tip each.", 2.6, {},
         [(0.20, a3("tipC", wx[1], zt)), (0.45, a3("tipC", (tcx, tcy), zt)), (0.003, {}),
          (0.35, fall("tipC", 8.0))]),
        ("A matrix-matched standard (our example; DAL names none): the P20 adds 10 µL of a 1 mg/L Cu, Ni, Fe, Mn, Al "
         "standard to 990 µL of blank matrix in H12 (seawater diluted as the samples are): 10 µg/L.", 5.6, {},
         [(0.10, {"head": (*head(tcx, tcy, zt)[:2], 0.0)}), (0.16, {"head": head20(*tip_xy["tipQ"]), "p20": zt - lz}),
          (0.08, {"p20": pick["tipQ"][2]}), (0.07, a2("tipQ", tip_xy["tipQ"], zt)), (0.14, a2("tipQ", (stx, sty), zt)),
          (0.08, a2("tipQ", (stx, sty), asp_15)), (0.003, dict(tlQ=shown0)), (0.08, dict(tlQ=full, q20=10.0)),
          (0.06, a2("tipQ", (stx, sty), zt)), (0.14, a2("tipQ", wx[12], zt)), (0.06, a2("tipQ", wx[12], std_in)),
          (0.08, dict(tlQ=shown0, q20=0.0, qh12=1000.0, h12=level("h12", 1000.0))), (0.003, dict(tlQ=hide))]),
        ("Its tip goes into the trash and the head parks. The plate goes to the ICP-MS: a collision cell, Cu, Ni, Fe "
         "and Mn in every sample, Al on NAB.", 3.4, {},
         [(0.08, a2("tipQ", wx[12], zt)), (0.36, a2("tipQ", (tcx, tcy), zt)), (0.003, {}),
          (0.30, fall("tipQ", 0.0)), (0.30, {"head": (0.0, 0.0, 0.0), "p20": 0.0})]),
    ]
    state = dict(head=(0.0, 0.0, 0.0), p20=0.0, qphase=0.0, q300=0.0, q20=0.0, qh6=0.0, qt1=TUBE05["ul"], qh1=0.0,
                 qh12=WELL_UL["blank"], qres1=RES["ml"] * 1000.0, qres2=RES["ml"] * 1000.0,
                 h6=hide, h1=hide, h12=hide, t1=hide, res1=hide, res2=level("res2", RES["ml"] * 1000.0),
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
        **{k: (sc1(k), (0,), 1) for k in (*(q for q, _, _, _ in ROWS), "qphase")},
    }
    z0s = {**{k: tip_z0[t] + 0.3 for k, (t, _, _) in TIP_LIQ.items()}, "h6": w_bot, "h1": w_bot, "h12": w_bot,
           "t1": tz + TUBE05["cone_z"], "res1": r_bot + 0.05, "res2": r_bot + 0.05}
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
    inst.joints["night"] = Joint("fade", v0=0.0)
    inst.joints["before"] = Joint("fade", v0=1.0)
    for i, (cap, secs, extra, _) in enumerate(script):
        tg = {k: (ends[k][i - 1] if i else 0.0, ends[k][i]) for k in channels}
        tg.update(extra)
        inst.actions.append((cap, secs, tg))

    # ---- labels, camera
    h1x, h1y = wx[1]
    blk_lbl = ("tube block, cut through\nits front row", (t1x, t1y + 4.0, tz + 30.0), (0.14, 0.62))
    tubes_lbl = ("the night's nine ICP-MS tubes,\n0.5 mL, 320 µL each", (t1x, t1y + 4.0, tz + 30.0), (0.14, 0.62))
    plate_lbl = ("2 mL deep-well plate,\ncut through row H", (h1x + 30.0, h1y + 4.0, dz + deep["H"]), (0.86, 0.60))
    asw_lbl = ("trough 2: seawater", (res[1][0], res[1][1] + 20.0, r_bot + r_h), (0.16, 0.40))
    acid_lbl = ("trough 1: 2% HNO3", (res[0][0], res[0][1] + 20.0, r_bot + r_h), (0.16, 0.40))
    h6_lbl = ("deep well H6", (wx[6][0], wx[6][1] + 4.0, w_bot + 25.0), (0.84, 0.62))
    h1_lbl = ("deep well H1", (h1x, h1y + 4.0, w_bot + 15.0), (0.84, 0.62))
    trash_lbl = ("fixed trash", (tcx - 50.0, tcy - 70.0, ttop), (0.80, 0.42))
    inst.labels = [("P300, right mount", (ox, oy - 25.0, 360.0), (0.78, 0.40)),
                   ("P20, left mount", (lx, ly - 25.0, 350.0), (0.20, 0.30)), blk_lbl, plate_lbl]
    inst.step_labels = {
        1: [asw_lbl, h6_lbl], 2: [asw_lbl, h6_lbl, trash_lbl],
        3: [("10 mg/L S stock", (sfx, sfy, tz + 40.0), (0.20, 0.62)), h6_lbl],
        4: [tubes_lbl, ("300 µL tips", (tip_xy["tipB"][0] + 40.0, tip_xy["tipB"][1] - 30.0, top300), (0.12, 0.36))],
        5: [acid_lbl, h1_lbl], 6: [acid_lbl, h1_lbl], 7: [trash_lbl],
        8: [("tube 1", (t1x, t1y + 2.0, tz + 18.0), (0.14, 0.62)), h1_lbl], 9: [h1_lbl], 10: [trash_lbl],
        11: [("1 mg/L standard", (stx, sty, tz + 40.0), (0.20, 0.62)),
             ("deep well H12:\n990 µL of blank matrix", (wx[12][0], wx[12][1] + 4.0, w_bot + 15.0), (0.84, 0.62))],
        12: [trash_lbl, plate_lbl],
    }
    mid_res = lambda r, w: ((r[0] + w[0]) / 2, (r[1] + w[1]) / 2, dz + 30.0)   # noqa: E731
    inst.zoom = {1: (mid_res(res[1], wx[6]), 620.0), 3: ((0.0, -100.0, dz + 30.0), 800.0), 4: "out",
                 5: (mid_res(res[0], wx[1]), 560.0), 8: (((t1x + h1x) / 2, (t1y + h1y) / 2, dz + 25.0), 480.0),
                 9: ((h1x, h1y, w_bot + 20.0), 300.0), 10: "out", 11: ((20.0, -120.0, dz + 30.0), 760.0), 12: "out"}
    inst.cam = (0.75, -1.6, 1.25)
    inst.notes = ["Opentrons' reference STEP; the head split out of it by bounding box as in PR #320",
                  "P300 single (right) and P20 single (left), the STEP's own; tips from Opentrons' labware sizes",
                  "stocks and volumes from DAL alloy-corrosion/copper/protocol.md at aeda51a; the standard is ours"]
    return inst


# ===================================================================================================== the read-out
def _gv(sc, key) -> float:
    m = sc.gmat.get(key)
    return 0.0 if m is None else float(m[0, 3])


ROWS = (("q300", "P300 tip", "{:.0f} µL", None), ("q20", "P20 tip", "{:.0f} µL", None),
        ("qres2", "seawater, trough 2", "{:.2f} mL", 0), ("qh6", "H6: 0.1 mg/L S", "{:.0f} µL", 0),
        ("qt1", "tube 1", "{:.0f} µL", 1), ("qh1", "deep well H1", "{:.0f} µL", 1),
        ("qh12", "deep well H12", "{:.0f} µL", 1), ("qres1", "2% HNO3, trough 1", "{:.2f} mL", 1))


def draw_volumes(sc, img, s):
    """The volumes, live, at the top right: the two tips, then the vessels of the step in hand."""
    from PIL import ImageDraw
    from scene import font
    k = f"{KEY}:"
    if k + "q300" not in sc.gmat:
        return
    phase = 1 if _gv(sc, k + "qphase") > 0.5 else 0
    rows = [r for r in ROWS if r[3] is None or r[3] == phase]
    vals = {c: _gv(sc, k + c) / (1000.0 if "mL" in fmt else 1.0) for c, _, fmt, _ in rows}
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
    for i, (c, name, fmt, _) in enumerate(rows):
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


_install_plot()
REGISTRY = {KEY: ot2_corrosion}

if __name__ == "__main__":
    import tour
    tour.MATS.update(MATERIALS)
    inst = ot2_corrosion()
    print(tour.fit_report(inst), flush=True)
    print(tour.tour_one(inst, tour.piece_entries(inst)), flush=True)
