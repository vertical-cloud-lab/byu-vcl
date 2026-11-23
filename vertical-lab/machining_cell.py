"""The charge cups machined, cleaned, dried, weighed, measured and racked in a floor cell (byu-vcl #367, from PR #318's
review: "We should probably automate machining of the high-purity cups and plugs ... This would also need to include a
cleaning and drying step (IPA for example)").

One cup's path through the recommended cell (notes/machining.md), as a model and a clip:

1. **The lathe** (a Haas ST-10 with its Bar Feeder V2: the outside from Haas's machine layout drawing, ``ST10``, checked
   against footage by machining_fit.py; the inside is ours) turns the cup from Ø20 mm bar: face, turn the OD to 19.05 mm, drill
   12.5 mm with a 118 deg point, finish-bore 12.70 mm, chamfer, part off. Dry but for a minimum-quantity mist of
   alcohol at the tool (as DESY, CERN and Thermo Fisher machine high-purity Al and Cu). The bar and the cup are drawn
   in half section while they are in the machine.
2. **The parts catcher** takes the cup as it is parted off and a short belt carries it out through the guard to a
   nest, so the door stays shut and the arm never reaches into the machine.
3. **The arm** (a UR10e on a pedestal, Robotiq 2F-85, wrist camera) picks the cup off the nest, stands it upright,
   blows the chips off it (a ring nozzle and a lance into the bore) and sets it in the cleaning basket, whose other
   three cups and four plugs are already in.
4. **Cleaning, indirect** (DAL #234's rule, as notes/alloy_print.md applies it): the basket goes into a closed
   stainless pan of IPA standing in the water of an ultrasonic bath, then into a second pan of clean IPA, each pan's
   lid shut over it, a slot hood behind drawing off the vapour.
5. **Drying under vacuum**: into a heated top-loading chamber pumped by a chemistry diaphragm pump through a
   condenser: the IPA in each blind bore boils off without being blown about.
6. **Weighed and measured**: on a weigh module whose glass shield lifts for the arm; then on the glass stage of an
   image-dimension gauge (OD and bore at the mouth).
7. **Racked**: into chapter 1's eight-cup charge rack (``charge.rack``), which is the cassette the MiR250 carries to
   tray J; its lid goes on once the run's four cups and plugs are in.

Cell frame: x east, y north (towards the aisle), z up, mm; the origin is the arm's pedestal on the floor. On the lab's
floor plan the cell stands in the south row (``machining.FLOOR``).

    python3 runner_guard.py slot --label mcell -- xvfb-run -a python3 machining_cell.py     # render (VIZ3D_FPS=12)
    PREVIEW=1 xvfb-run -a python3 machining_cell.py      # the last frame of each sub-step -> /tmp/preview_*.png
    ARM_AUDIT=1 xvfb-run -a python3 machining_cell.py    # nothing drawn, every frame checked -> out/collisions/
    MCELL_STILL=lab xvfb-run -a python3 machining_cell.py   # the cell on the floor -> out/machining_lab.png
    MCELL_GIF=1 python3 machining_cell.py                  # out/machining_cell.gif, cut from the MP4
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
import pyvista as pv

import charge as C
import props as P
import robot as RB
from scene import R, Scene, T

HERE = Path(__file__).resolve().parent
NAME = "machining_cell"
TITLE = "Vertical cloud lab: a charge cup machined, cleaned, dried and racked"

# ------------------------------------------------------------------------------------------------ layout (cell frame)
Z_ARM = 760.0                    # the UR10e's base plate on its pedestal
BENCH_Z = 860.0                  # bench tops
FRONT_Y = 950.0                  # the cell's front (the fence), on the south row's face line
X_COLLET = 198.0                 # the collet's face; the bar comes out towards -x

# The Haas ST-10's outside, in its own frame: x along the spindle from the enclosure's headstock end towards the chip
# conveyor (the operator's left to right), y from the enclosure's front face into the machine, z up from the floor; mm.
# From Haas's machine layout drawing (ST-10/15 MLD, 12/20/2024): the front elevation's height and width breakdown (read
# at 3.176 mm a pixel at 200 dpi, checked against its own dimensions to 1 %), the plan's depths and the bar feeder page.
# Footage of the machine (refs/st10/, machining_fit.py) checks it and fits what the drawing doesn't dimension. Until
# round 14 of #367 the lathe was a 3437 x 1596 x 2167 mm box: the installed envelope, conveyor and all, as one block.
ST10 = dict(
    W=2160.0, D=1021.0, H=1795.0,                # enclosure: 680 px of the elevation; 40.2 in deep (plan); its roof
                                                 # (72.5 in, 1842 mm, is the top of a small box on the roof)
    t=20.0,                                      # its sheet metal, drawn thick enough to read
    base_h=676.0, base_x0=40.0, base_x1=2087.0, base_y0=35.0, base_y1=985.0, feet=76.0,   # the dark base; 3.0 in pads
    door_x0=794.0, door_x1=1382.0, door_z0=680.0, door_z1=1636.0,   # the opening: 23.3 in wide, its sill 26.8 in up
    panel_x0=767.0, panel_w=642.0,               # the sliding door, shut (it slides to the left, over the white panel)
    win_x0=235.0, win_w=238.0, win_z0=1143.0, win_z1=1486.0,        # its window, from the door's left edge
    surround_x0=740.0, surround_x1=1430.0,       # the dark grey surround of the door on the front
    pend_x0=1492.0, pend_x1=1969.0, pend_z0=1032.0, pend_z1=1667.0, pend_d=205.0,   # the pendant, 8.1 in proud
    scr_x0=1620.0, scr_x1=1937.0, scr_z0=1376.0, scr_z1=1604.0,     # its screen
    lcov_w=130.0, lcov_y0=20.0, lcov_y1=470.0, lcov_z0=800.0, lcov_z1=1290.0,   # the spindle's cover at the left end
                                                 # (as seen in footage; the drawing shows a larger outline, 285 mm)
    cab_x0=950.0, cab_x1=1900.0, cab_d=270.0, cab_h=1842.0,          # the electrical cabinet on the back (to 49.8 in)
    conv_x1=3138.0, conv_y0=130.0, conv_y1=510.0, conv_low=300.0, conv_top=1576.0, conv_dis=1064.0,
    conv_head=343.0,                             # the conveyor's head, 62.1 in to its top; it drops chips at 41.9 in
    spin_y=307.0, spin_z=991.0,                  # the spindle's axis: 12.1 in behind the front face, 39 in up
    nose_x=860.0,                                # the spindle nose (collet face) from the enclosure's left end (est.)
    feed_l=2104.0, feed_y1=1283.0,               # Bar Feeder V2: 82.9 in long, 50.5 in deep (bar feeder page)
    feed_y0=0.0, feed_z0=700.0, feed_z1=1150.0, feed_lid=100.0, feed_body_y1=860.0,
)
X_HEAD = X_COLLET + ST10["nose_x"]   # the enclosure's headstock end in the cell (the operator's left)
Y_FRONT = -800.0                     # its front face in the cell
SPIN_Y, SPIN_Z = Y_FRONT - ST10["spin_y"], ST10["spin_z"]           # the spindle's axis, along x
M_ST10 = np.array([[-1.0, 0, 0, X_HEAD], [0, -1.0, 0, Y_FRONT], [0, 0, 1.0, 0], [0, 0, 0, 1.0]])   # machine -> cell
# The envelope for machining.py's floor plan: the conveyor's end (-x) to the motor cover (+x), the pendant to the
# cabinet; the bar feeder beyond the motor cover. Overall 3423 mm against Haas's 3437 (their 1/2 in tolerance).
LATHE = dict(x0=X_HEAD - ST10["conv_x1"], x1=X_HEAD + ST10["lcov_w"], y1=Y_FRONT + ST10["pend_d"],
             D=ST10["pend_d"] + ST10["D"] + ST10["cab_d"], H=ST10["cab_h"], loader_l=ST10["feed_l"],
             loader_w=ST10["feed_y1"])
BAR_R = 10.0                     # Ø20 mm bar (5N Al, DAL #152; OFE Cu bought at 20 mm too, so both are turned)
CUP_R = C.STOCK_D / 2            # 9.525: the cup's OD, turned
DRILL_R = 6.25                   # 12.5 mm drill, 118 deg point
BORE_R = C.CUP_BORE_D / 2        # 6.35: finish-bored
CUP_L = C.SLUG_L                 # 63.5
GROOVE_W = 3.0                   # the parting blade
END0 = 125.5                     # the raw bar's end after a feed (72.5 mm out of the collet)
END = 126.5                      # faced
GROOVE_X = END + CUP_L + GROOVE_W / 2       # 191.5: the parting groove's centre
CUP_BASE_X = END + CUP_L         # 190: the cup's base, when parted
TURRET_U = np.array([0.0, math.cos(math.radians(-45)), math.sin(math.radians(-45))])  # turret -> axis, along the slant
TURRET_R = 283.0                 # turret centre to the working tool's tip (on the axis at X = 0)
X_INDEX = -80.0                  # the turret's centre along x when it indexes: every tool clear of bar and headstock
BELT_X = (END + CUP_BASE_X) / 2  # 158.25: under the parted cup, and the belt's middle
BELT_Z = 880.0                   # belt top
UP_Y = -700.0                    # the upender's pivot: the lying cup's base against its end plate
BELT_Y = (-1150.0, UP_Y - 33.0)  # inside the machine -> the upender, outside the guard
NEST = np.array([BELT_X, UP_Y + CUP_R, BELT_Z])            # the cup's base centre, stood up on the upender
BLOW = np.array([-660.0, -560.0, 1040.0])                  # the cup's base at the blow-off station, on its riser
BASKET = np.array([-800.0, -400.0, 1032.0])                # the basket's feet on its stand (one row along y)
# Two small ultrasonic baths (sized after Elma's Elmasonic P 60 H: 365 x 186 x 271 mm outside, 5.75 L), water in the
# tank, each with ONE closed stainless vessel of IPA hung in it: Elma's manual allows "max. 1 litre" of a flammable
# liquid, and only in a separate vessel standing in water (notes/machining.md). Each vessel holds about 0.6 L.
PANS = {"wash": np.array([-875.0, -20.0]), "rinse": np.array([-680.0, -20.0])}
PAN = dict(ix=46.0, iy=220.0, depth=125.0, rim=1157.0, wall=2.0, ipa=76.0)
TANK = dict(x=186.0, y=365.0, top=BENCH_Z + 271.0, water=1100.0)
DRYER = np.array([-860.0, 420.0])
DRYER_R = 140.0
DRYER_RIM = BASKET[2] + 171.0          # the basket's handle (top at 159) 12 mm under the rim, so the lid shuts
WEIGH = np.array([720.0, -420.0, 952.0])                   # the cup's base on the weigh module's seat
VISION = np.array([760.0, 160.0, 965.0])                   # the cup's base on the gauge's glass stage
RACK_AT = np.array([0.0, 780.0, 920.0])                    # charge.rack()'s frame on the north bench
LID_REST = np.array([760.0, 560.0, BENCH_Z])               # the cassette's lid, its long side along y
HERO = 3                                                   # the rack pocket the clip's cup goes to
PARK = [-90.0, -110.0, 120.0, -100.0, -90.0, 0.0]          # the arm's joints, parked (deg)
BASKET_POCKET = 1                                          # its pocket in the basket (no post beside it)

CUP_GRASP = 50.0                 # grasp point over a cup's base (chapter 1: 45; 50 here, so the pads clear the
                                 # 30 mm trough when the cup stands on it)
GRIP_CUP, OPEN_CUP, OPEN_RACK = 0.80, 0.66, 0.75           # alloy_charge's closures on the 19.05 mm cup
GRIP_BAR, OPEN_BAR = 0.86, 0.66                            # on the basket's 14 mm handle bar

# ------------------------------------------------------------------------------------------------ colours
AL, CU_C = C.AL_5N, C.CU
SHEET = (0.88, 0.89, 0.90)       # machine sheet metal
TRIM = (0.24, 0.25, 0.27)
STEEL = (0.70, 0.71, 0.73)
SS = (0.78, 0.79, 0.81)          # stainless
DARK = (0.16, 0.17, 0.18)
BENCH_C = (0.55, 0.57, 0.60)
TOP_C = (0.86, 0.85, 0.82)       # phenolic bench top
GLASS = (0.80, 0.88, 0.94)
WATER = (0.62, 0.80, 0.93)
IPA = (0.82, 0.91, 0.98)
FENCE = (0.95, 0.80, 0.15)
PRINTED = C.PRINT
TOOL = (0.85, 0.66, 0.20)        # carbide/PCD inserts, gold for legibility
CHIP = (0.74, 0.75, 0.78)
FLOOR_C = (0.80, 0.80, 0.78)


def _box(x0, x1, y0, y1, z0, z1):
    return pv.Box(bounds=(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))).triangulate()


def _cyl(p0, p1, r, res=40, capping=True):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    h = float(np.linalg.norm(d))
    return pv.Cylinder(center=(p0 + p1) / 2, direction=d / h, radius=r, height=h, resolution=res,
                       capping=capping).triangulate()


def _merge(ms):
    ms = [m for m in ms if m is not None and m.n_points]
    out = ms[0].copy()
    for m in ms[1:]:
        out = out.merge(m)
    return out


def _open_box(x0, x1, y0, y1, z0, z1, t):
    """A box open at the top, walls t thick (a tank, a pan, a bin)."""
    return _merge([_box(x0, x1, y0, y1, z0, z0 + t), _box(x0, x0 + t, y0, y1, z0, z1), _box(x1 - t, x1, y0, y1, z0, z1),
                   _box(x0, x1, y0, y0 + t, z0, z1), _box(x0, x1, y1 - t, y1, z0, z1)])


def _holed(x0, x1, y0, y1, z0, z1, holes) -> pv.PolyData:
    """A plate with rectangular holes [(hx0, hx1, hy0, hy1)] through it (manifold3d, as charge._pocketed)."""
    import manifold3d as m3d
    body = m3d.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])
    for hx0, hx1, hy0, hy1 in holes:
        body = body - m3d.Manifold.cube([hx1 - hx0, hy1 - hy0, z1 - z0 + 2]).translate([hx0, hy0, z0 - 1])
    mg = body.to_mesh()
    v = np.asarray(mg.vert_properties, float)[:, :3]
    f = np.asarray(mg.tri_verts, np.int64)
    return pv.PolyData(v, np.c_[np.full(len(f), 3), f].ravel()).clean()


def _ring(ro, ri, z0, z1, res=48):
    return C.lathe([(ri, z0), (ro, z0), (ro, z1), (ri, z1)], res=res)


def lvl(p, toward):
    """A level gripper at p pointing along `toward` (horizontal), fingers closing sideways (props.tcp_frame)."""
    t = np.array([toward[0], toward[1], 0.0], float)
    return P.tcp_frame(np.asarray(p, float), t / np.linalg.norm(t), 0.0)


def dwn(p, spin=0.0):
    """A gripper pointing straight down, its fingers closing along world x (spin 0) or y (spin 90)."""
    return P.tcp_frame(np.asarray(p, float), (0, 0, -1), spin)


def about_y(M, deg):
    """M turned about the world y axis through its own origin."""
    Rm = R((0, 1, 0), deg)
    out = np.eye(4)
    out[:3, :3] = Rm[:3, :3] @ M[:3, :3]
    out[:3, 3] = M[:3, 3]
    return out


def radial(p, base=(0.0, 0.0)):
    v = np.asarray(p[:2], float) - np.asarray(base, float)
    return v / np.linalg.norm(v)


# ------------------------------------------------------------------------------------------------ the workpiece
# The bar's frame: z from the collet's face (0) towards the free end, which points to -x in the cell. M_BAR maps it:
# local x -> -z, y -> -y, z -> -x (a proper rotation), so charge.lathe(cut=True)'s kept half (local y >= 0) is the
# half behind the spindle's axis, and a camera in front of the machine sees the section.
M_BAR = np.array([[0, 0, -1, X_COLLET], [0, -1, 0, SPIN_Y], [-1, 0, 0, SPIN_Z], [0, 0, 0, 1]], float)


def work_profile(end_x: float, turned: float = 0.0, hole_r: float = 0.0, hole_d: float = 0.0, groove: float = 0.0):
    """(r, z) profile of the bar out of the collet: the free end at cell x = end_x; `turned` mm turned to the cup's OD
    back from the end; a hole hole_d deep (radius hole_r, 118 deg point); the parting groove `groove` deep."""
    end = X_COLLET - end_x
    pts = [(0.0, 0.0), (BAR_R, 0.0)]
    r_out = BAR_R
    if turned > 0.05:
        zt = max(0.5, end - turned)
        pts += [(BAR_R, zt), (CUP_R, zt)]
        r_out = CUP_R
    if groove > 0.05:
        zg = X_COLLET - GROOVE_X
        pts += [(r_out, zg - GROOVE_W / 2), (r_out - groove, zg - GROOVE_W / 2), (r_out - groove, zg + GROOVE_W / 2),
                (r_out, zg + GROOVE_W / 2)]
    pts += [(r_out, end)]
    if hole_d > 0.05:
        tip = hole_r / math.tan(math.radians(59.0))
        pts += [(hole_r, end), (hole_r, end - hole_d), (0.0, end - hole_d - tip)]
    else:
        pts += [(0.0, end)]
    return pts


def work_mesh(cut=True, **kw) -> pv.PolyData:
    return C.lathe(work_profile(**kw), cut=cut, res=64).transform(M_BAR, inplace=False)


def stub_mesh(cut=True) -> pv.PolyData:
    """What is left of the bar when the cup is parted off: the collet's face to the groove's far side."""
    zg = X_COLLET - GROOVE_X - GROOVE_W / 2
    return C.lathe([(0, 0), (BAR_R, 0), (BAR_R, zg), (0, zg)], cut=cut, res=64).transform(M_BAR, inplace=False)


def cup_in_bar() -> np.ndarray:
    """The cup's own frame (charge.cup: base at z = 0, rim at 63.5) where it is in the bar, parted."""
    return M_BAR @ T((0, 0, X_COLLET - CUP_BASE_X))


# ------------------------------------------------------------------------------------------------ the lathe
def _slab(p0, p1, half_w, y0, y1):
    """A box between two points in the machine's xz plane, half_w either side of the line (an inclined conveyor)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    L = float(np.hypot(*d))
    a = math.degrees(math.atan2(d[1], d[0]))
    b = _box(0, L, y0, y1, -half_w, half_w)
    return b.rotate_y(-a, inplace=False).translate((p0[0], 0, p0[1]), inplace=False)


ST10_GREY = (0.33, 0.35, 0.37)       # the base, the door's surround, the conveyor (Haas's dark grey)
ST10_WHITE = (0.90, 0.91, 0.92)      # the enclosure's panels
ST10_DOOR = (0.25, 0.26, 0.28)


def st10_parts(p=None, inside=True) -> dict:
    """{name: (mesh, colour, opacity)} of the ST-10 and its bar feeder in the machine's frame (see ST10). inside=False
    leaves the enclosure closed and solid (machining_fit.py's silhouettes)."""
    p = dict(ST10, **(p or {}))
    W, D, H, t, bh = p["W"], p["D"], p["H"], p["t"], p["base_h"]
    dx0, dx1, dz0, dz1 = p["door_x0"], p["door_x1"], p["door_z0"], p["door_z1"]
    out = {}
    if inside:          # walls, and the front round the door's opening, so the clip can look in
        enc = [_box(0, W, D - t, D, bh, H), _box(0, t, 0, D, bh, H), _box(W - t, W, 0, D, bh, H),
               _box(0, W, 0, D, H - t, H), _box(0, dx0, 0, t, bh, H - t), _box(dx1, W, 0, t, bh, H - t),
               _box(dx0, dx1, 0, t, dz1, H - t), _box(dx0, dx1, 0, t, bh, dz0)]
    else:
        enc = [_box(0, W, 0, D, bh, H)]
    out["skin"] = (_merge(enc), ST10_WHITE, 1.0)
    sx0, sx1 = p["surround_x0"], p["surround_x1"]
    out["surround"] = (_merge([_box(sx0, dx0, -4, 0, bh, H - 60), _box(dx1, sx1, -4, 0, bh, H - 60),
                               _box(dx0, dx1, -4, 0, dz1, H - 60), _box(sx0, sx1, -4, 0, bh, dz0)]), ST10_GREY, 1.0)
    out["base"] = (_merge([_box(p["base_x0"], p["base_x1"], p["base_y0"], p["base_y1"], p["feet"], bh),
                           _box(-5, W + 5, -12, p["base_y1"], bh - 28, bh)]), ST10_GREY, 1.0)
    feet = [_cyl((x, y, 0), (x, y, p["feet"]), 45.0, res=16) for x in (p["base_x0"] + 110, p["base_x1"] - 150)
            for y in (p["base_y0"] + 90, p["base_y1"] - 90)]
    out["feet"] = (_merge(feet), DARK, 1.0)
    out["lcov"] = (_box(-p["lcov_w"], 0, p["lcov_y0"], p["lcov_y1"], p["lcov_z0"], p["lcov_z1"]), ST10_WHITE, 1.0)
    out["cabinet"] = (_box(p["cab_x0"], p["cab_x1"], D, D + p["cab_d"], p["feet"], p["cab_h"]), ST10_WHITE, 1.0)
    pd = p["pend_d"]
    out["pendant"] = (_merge([_box(p["pend_x0"], p["pend_x1"], -pd, -pd + 95, p["pend_z0"], p["pend_z1"]),
                              _box(p["pend_x1"] - 90, p["pend_x1"] - 20, -pd + 95, 0, p["pend_z1"] - 160,
                                   p["pend_z1"] - 60)]), ST10_WHITE, 1.0)
    out["screen"] = (_box(p["scr_x0"], p["scr_x1"], -pd - 2, -pd, p["scr_z0"], p["scr_z1"]), DARK, 1.0)
    # the chip conveyor out of the base's right end: a low run, the incline, the head over its bin
    xh0 = p["conv_x1"] - p["conv_head"]
    cy0, cy1, lo = p["conv_y0"], p["conv_y1"], p["conv_low"]
    conv = [_box(p["base_x1"] - 200, p["base_x1"] + 280, cy0, cy1, lo, lo + 210),
            _slab((p["base_x1"] + 120, lo + 105), (xh0 + 60, p["conv_top"] - 120), 115.0, cy0, cy1),
            _box(xh0, p["conv_x1"], cy0, cy1, p["conv_top"] - 330, p["conv_top"]),
            _box(xh0 + 60, p["conv_x1"] - 60, cy0 + 20, cy1 - 20, p["conv_dis"], p["conv_top"] - 330)]
    out["conveyor"] = (_merge(conv), ST10_GREY, 1.0)
    # the door, shut, with its window and handle (it slides left over the white panel; machining_cell fades it)
    x0d = p["panel_x0"]
    df = [_box(x0d, x0d + p["panel_w"], -30, -6, dz0 - 20, p["win_z0"]),
          _box(x0d, x0d + p["panel_w"], -30, -6, p["win_z1"], dz1 + 30),
          _box(x0d, x0d + p["win_x0"], -30, -6, p["win_z0"], p["win_z1"]),
          _box(x0d + p["win_x0"] + p["win_w"], x0d + p["panel_w"], -30, -6, p["win_z0"], p["win_z1"]),
          _box(x0d + p["panel_w"] - 75, x0d + p["panel_w"] - 55, -70, -30, 1150, 1450)]
    out["door"] = (_merge(df), ST10_DOOR, 1.0)
    out["glass"] = (_box(x0d + p["win_x0"], x0d + p["win_x0"] + p["win_w"], -22, -14, p["win_z0"], p["win_z1"]),
                    GLASS, 0.25)
    # the bar feeder beyond the motor cover: its stand and feet, the body, the dark lid over the magazine
    fx1 = -p["lcov_w"]
    fx0 = fx1 - p["feed_l"]
    fy0, fyb, fy1 = p["feed_y0"], p["feed_body_y1"], p["feed_y1"]
    stand = [_box(fx0 + 120, fx1 - 120, fy0 + 120, fyb - 160, p["feet"], p["feed_z0"])]
    for x in (fx0 + 120, fx1 - 200):
        stand.append(_box(x, x + 80, fy0, fy1, 0, 70))
    out["feeder_stand"] = (_merge(stand), ST10_GREY, 1.0)
    out["feeder"] = (_box(fx0, fx1, fy0, fyb, p["feed_z0"], p["feed_z1"]), ST10_WHITE, 1.0)
    out["feeder_lid"] = (_box(fx0 + 30, fx1 - 30, fy0 + 30, fyb - 30, p["feed_z1"], p["feed_z1"] + p["feed_lid"]),
                         ST10_GREY, 1.0)
    return out


def st10_anchors(p=None, pose=None) -> dict:
    """Named points of the ST-10 in its frame, for picks in footage (machining_fit.py; register.py's convention)."""
    p = dict(ST10, **(p or {}))
    W, H, bh, pd = p["W"], p["H"], p["base_h"], p["pend_d"]
    x0d, wx0, wx1 = p["panel_x0"], p["panel_x0"] + p["win_x0"], p["panel_x0"] + p["win_x0"] + p["win_w"]
    xh0 = p["conv_x1"] - p["conv_head"]
    fx1 = -p["lcov_w"]
    fx0 = fx1 - p["feed_l"]
    return {"enc tl": (0, 0, H), "enc tr": (W, 0, H), "enc bl": (0, 0, bh), "enc br": (W, 0, bh),
            "base bl": (p["base_x0"], p["base_y0"], p["feet"]), "base br": (p["base_x1"], p["base_y0"], p["feet"]),
            "win tl": (wx0, -30, p["win_z1"]), "win tr": (wx1, -30, p["win_z1"]),
            "win bl": (wx0, -30, p["win_z0"]), "win br": (wx1, -30, p["win_z0"]),
            "door tl": (x0d, -30, p["door_z1"] + 30), "door tr": (x0d + p["panel_w"], -30, p["door_z1"] + 30),
            "scr tl": (p["scr_x0"], -pd, p["scr_z1"]), "scr tr": (p["scr_x1"], -pd, p["scr_z1"]),
            "scr bl": (p["scr_x0"], -pd, p["scr_z0"]), "scr br": (p["scr_x1"], -pd, p["scr_z0"]),
            "pend tl": (p["pend_x0"], -pd, p["pend_z1"]), "pend tr": (p["pend_x1"], -pd, p["pend_z1"]),
            "pend bl": (p["pend_x0"], -pd, p["pend_z0"]), "pend br": (p["pend_x1"], -pd, p["pend_z0"]),
            "lcov tl": (-p["lcov_w"], p["lcov_y0"], p["lcov_z1"]), "lcov bl": (-p["lcov_w"], p["lcov_y0"], p["lcov_z0"]),
            "conv head tl": (xh0, p["conv_y0"], p["conv_top"]), "conv head tr": (p["conv_x1"], p["conv_y0"], p["conv_top"]),
            "feed tl": (fx0, p["feed_y0"], p["feed_z1"]), "feed tr": (fx1, p["feed_y0"], p["feed_z1"]),
            "feed bl": (fx0, p["feed_y0"], p["feed_z0"]), "feed br": (fx1, p["feed_y0"], p["feed_z0"]),
            "lid tl": (fx0 + 30, p["feed_y0"] + 30, p["feed_z1"] + p["feed_lid"]),
            "lid tr": (fx1 - 30, p["feed_y0"] + 30, p["feed_z1"] + p["feed_lid"])}


def _to_cell(m: pv.PolyData) -> pv.PolyData:
    return m.transform(M_ST10, inplace=False)


SLOT = dict(x0=100.0, x1=215.0, z0=855.0, z1=915.0)    # the belt's way out through the door's lower panel (ours), cell
# In the cell the pendant is swung back against the enclosure (it hangs on a swinging arm, R17.4 in on Haas's plan), its
# face 110 mm proud instead of 205, clear of the blow-off station's post; footage and the fit keep it where Haas draws it
CELL_ST10 = dict(pend_d=110.0)


def lathe_parts() -> dict:
    """{name: (mesh, colour, opacity)} of the turning centre, cell frame. Its front (the door) faces +y, the headstock
    is at +x with the bar feeder beyond it, the chip conveyor climbs out of the -x end into one bin per metal. The
    outside is the measured ST-10 (``st10_parts``, placed by ``M_ST10``); the inside, the belt and the bins are ours."""
    out = {}
    sx0, sx1 = X_HEAD - SLOT["x1"], X_HEAD - SLOT["x0"]       # the slot in the machine's frame
    for name, (m, col, op) in st10_parts(CELL_ST10, inside=True).items():
        if name == "door":                                     # cut the belt's slot out of the door's lower panel
            p = ST10
            x0d, x1d = p["panel_x0"], p["panel_x0"] + p["panel_w"]
            parts = [_box(x0d, x1d, -30, -6, SLOT["z1"], p["win_z0"]),
                     _box(x0d, sx0, -30, -6, p["door_z0"] - 20, SLOT["z1"]),
                     _box(sx1, x1d, -30, -6, p["door_z0"] - 20, SLOT["z1"]),
                     _box(sx0, sx1, -30, -6, p["door_z0"] - 20, SLOT["z0"]),
                     _box(x0d, x1d, -30, -6, p["win_z1"], p["door_z1"] + 30),
                     _box(x0d, x0d + p["win_x0"], -30, -6, p["win_z0"], p["win_z1"]),
                     _box(x0d + p["win_x0"] + p["win_w"], x1d, -30, -6, p["win_z0"], p["win_z1"]),
                     _box(x1d - 75, x1d - 55, -70, -30, 1150, 1450)]
            m = _merge(parts)
        out[f"lathe/{name}"] = (_to_cell(m), col, op)
    p = ST10
    xe0, xe1 = X_HEAD - p["W"], X_HEAD                         # the enclosure in the cell
    ye1, ye0 = Y_FRONT, Y_FRONT - p["D"]
    t, bh = p["t"], p["base_h"]
    # inside: the chip pan on the base, the slant bed beyond the turret's reach (760-840 mm from the axis along the
    # slant, as before; the far side's tools reach 648 mm), narrowed to fit the real 1021 mm depth, its base casting
    # against the back wall behind the tools' sweep, the headstock, the spindle nose
    pan = _box(xe0 + t, xe1 - t, ye0 + t, ye1 - t, bh, bh + 12)
    n = np.array([0.0, -TURRET_U[2], TURRET_U[1]])
    Mb = np.eye(4)
    Mb[:3, 0], Mb[:3, 1], Mb[:3, 2] = (1, 0, 0), n, -TURRET_U
    Mb[:3, 3] = (0, SPIN_Y, SPIN_Z)
    slant = _box(-800, 700, -140, 140, 760, 840).transform(Mb, inplace=False)
    bed = _box(-800, 700, ye0 + t, ye0 + 140, bh, 1450)
    head = _box(260, min(760, xe1 - t - 10), SPIN_Y - 260, SPIN_Y + 250, 760, 1340)
    nose = _cyl((240, SPIN_Y, SPIN_Z), (262, SPIN_Y, SPIN_Z), 95.0, res=64)
    # the belt: a short narrow conveyor along y, from under the spindle out through the door's slot to the upender
    belt = _box(BELT_X - 20, BELT_X + 20, BELT_Y[0], BELT_Y[1], BELT_Z - 22, BELT_Z)
    belt_frame = _merge([_box(BELT_X - 26, BELT_X - 20, BELT_Y[0] - 10, BELT_Y[1] + 2, BELT_Z - 40, BELT_Z + 4),
                         _box(BELT_X + 20, BELT_X + 26, BELT_Y[0] - 10, BELT_Y[1] + 2, BELT_Z - 40, BELT_Z + 4),
                         _box(BELT_X - 20, BELT_X + 20, BELT_Y[1] - 80, BELT_Y[1] - 60, 520, BELT_Z - 40),
                         _box(BELT_X - 20, BELT_X + 20, BELT_Y[0] + 20, BELT_Y[0] + 40, bh + 12, BELT_Z - 40),
                         # the upender's stand and its rotary actuator, beside the pivot
                         _box(BELT_X - 30, BELT_X + 30, UP_Y - 40, UP_Y + 25, 520, BELT_Z - 30),
                         _box(BELT_X + 22, BELT_X + 52, UP_Y - 18, UP_Y + 18, BELT_Z - 40, BELT_Z + 4)])
    # the bar being fed: the feeder's channel and the spindle liner through the motor cover into the headstock; the
    # magazine's bars on the feeder's top
    fx1 = X_HEAD + p["lcov_w"]
    feed = _cyl((xe1 - 200, SPIN_Y, SPIN_Z), (fx1 + 40, SPIN_Y, SPIN_Z), 45.0, res=32)
    bars = []
    ztop = p["feed_z1"] + p["feed_lid"]
    for k in range(6):
        y = Y_FRONT - 180 - 42 * k
        bars.append(_cyl((fx1 + 300, y, ztop + BAR_R), (fx1 + 1500, y, ztop + BAR_R), BAR_R, res=24))
    # the conveyor's head drops into the bin of the metal being cut; the other metal's bin waits behind it
    xd0, xd1 = X_HEAD - p["conv_x1"] - 40, X_HEAD - p["conv_x1"] + p["conv_head"] + 40
    bin_al = _open_box(xd0, xd1, Y_FRONT - 560, Y_FRONT - 80, 0, 650, 6)
    bin_cu = _open_box(xd0, xd1, Y_FRONT - 1120, Y_FRONT - 640, 0, 650, 6)
    # the alcohol MQL unit on the enclosure's -x end, behind the conveyor, its line into the work zone
    mql = _merge([_box(xe0 - 160, xe0, ye0 + 120, ye0 + 380, 1100, 1420),
                  _cyl((xe0 - 80, ye0 + 250, 1420), (xe0 - 80, ye0 + 250, 1520), 35.0, res=24)])
    out.update({
        "lathe/pan": (pan, (0.45, 0.46, 0.48), 1.0),
        "lathe/bed": (_merge([bed, slant]), (0.36, 0.37, 0.40), 1.0),
        "lathe/head": (_merge([head, nose]), (0.52, 0.53, 0.56), 1.0),
        "lathe/belt": (belt, DARK, 1.0),
        "lathe/beltframe": (belt_frame, STEEL, 1.0),
        "lathe/loader": (feed, SHEET, 1.0),
        "lathe/bars": (_merge(bars), AL, 1.0),
        "lathe/bin_al": (bin_al, (0.25, 0.45, 0.85), 1.0),
        "lathe/bin_cu": (bin_cu, (0.85, 0.45, 0.20), 1.0),
        "lathe/mql": (mql, (0.20, 0.36, 0.62), 1.0),
    })
    return out


def collet_parts() -> dict:
    """The collet chuck's nose, which turns: a ring with three slots, so the spin shows (group "spindle")."""
    ring = C.lathe([(14.0, 0), (34.0, 0), (34.0, 36.0), (14.0, 36.0)], res=64)
    ring = ring.rotate_y(-90.0, inplace=False).translate((X_COLLET + 36.0, SPIN_Y, SPIN_Z), inplace=False)
    slots = []
    for k in range(3):
        a = math.radians(120 * k)
        y, z = SPIN_Y + 28 * math.cos(a), SPIN_Z + 28 * math.sin(a)
        slots.append(_box(X_COLLET - 0.5, X_COLLET + 30, y - 2.5, y + 2.5, z - 2.5, z + 2.5).rotate_x(
            0.0, inplace=False))
    return {"spindle/collet": (ring, STEEL, 1.0), "spindle/slots": (_merge(slots), DARK, 1.0)}


# The turret's own frame: origin at its centre, x along the spindle's axis, the working station along TURRET_U. Tools
# are mounted every 90 deg: T1 the turning and facing tool (radial), T2 the 12.5 mm drill, T3 the boring bar (both
# axial, along +x), T4 the parting blade (radial). Turning the turret by -90 * (k - 1) brings tool k to work.
TOOL_ANG = {1: 0.0, 2: 90.0, 3: 180.0, 4: 270.0}        # from the working station, about +x


def _station(ang: float):
    """(unit radial vector, unit normal in the y-z plane) of a station `ang` deg round from the working one."""
    a = math.atan2(TURRET_U[2], TURRET_U[1]) + math.radians(ang)
    u = np.array([0.0, math.cos(a), math.sin(a)])
    n = np.array([0.0, -math.sin(a), math.cos(a)])
    return u, n


def turret_parts() -> dict:
    """{name: (mesh, colour, opacity)} in the turret's frame (group "turret_rot")."""
    disc = _cyl((-45, 0, 0), (45, 0, 0), 165.0, res=8)                       # an octagonal drum
    hub = _cyl((-45, 0, 0), (-120, 0, 0), 90.0, res=32)
    holders, shanks, tips = [], [], []
    for k, ang in TOOL_ANG.items():
        u, n = _station(ang)
        c = u * 190.0
        holders.append(_box(-30, 40, -28, 28, -28, 28).translate((0, 0, 0), inplace=False)
                       .transform(_frame(u, n, c), inplace=False))
        if k in (1, 4):                                         # radial: a shank to the axis, the insert at its tip
            w = 2.6 if k == 4 else 12.0
            sh = _box(-w / 2 if k == 4 else -12, w / 2 if k == 4 else 0, -6, 6, 0, TURRET_R - 205.0 - 8.0)
            shanks.append(sh.transform(_frame(u, n, u * 205.0), inplace=False))
            if k == 4:
                tip = _box(-1.3, 1.3, -5, 5, TURRET_R - 205.0 - 8.0, TURRET_R - 205.0 - 0.3)
            else:                                               # the cutting edge at the tip's +x face
                tip = _box(-10, 0, -5, 5, TURRET_R - 205.0 - 8.0, TURRET_R - 205.0 - 0.3)
            tips.append(tip.transform(_frame(u, n, u * 205.0), inplace=False))
        else:                                                   # axial: a holder at the axis, the tool along +x
            ctr = u * TURRET_R
            blk = _box(40, 110, -26, 26, -26, 26).translate(ctr, inplace=False)
            holders.append(blk)
            if k == 2:
                body = _cyl(ctr + (110, 0, 0), ctr + (TOOL_L - 7.0, 0, 0), DRILL_R - 0.15, res=24)
                point = C.lathe([(0, 0), (DRILL_R - 0.15, 0), (0, (DRILL_R - 0.15) / math.tan(math.radians(59)))],
                                res=24).rotate_y(90.0, inplace=False).translate(ctr + (TOOL_L - 7.0, 0, 0),
                                                                                 inplace=False)
                shanks.append(body)
                tips.append(point)
            else:
                body = _cyl(ctr + (110, 0, 0), ctr + (TOOL_L - 6.0, 0, 0), 4.5, res=20)
                ins = _cyl(ctr + (TOOL_L - 6.0, 0, 0), ctr + (TOOL_L, 0, 0), BORE_R - 0.05, res=24)
                shanks.append(body)
                tips.append(ins)
    return {"turret/drum": (_merge([disc, hub]), (0.55, 0.56, 0.60), 1.0),
            "turret/holders": (_merge(holders), (0.40, 0.41, 0.44), 1.0),
            "turret/shanks": (_merge(shanks), (0.30, 0.30, 0.32), 1.0),
            "turret/tips": (_merge(tips), TOOL, 1.0)}


TOOL_L = 175.0                   # the axial tools' tips, along +x from the turret's centre


def _frame(u, n, origin):
    """A right-handed frame with x along the spindle's axis (+x), z along u (radial), y = z x x, at `origin` (turret
    frame). (`n` is kept for the callers; until 2026-11-20 x was n x u, which is -x, so every insert pointed into the
    work.)"""
    M = np.eye(4)
    M[:3, 0] = (1.0, 0.0, 0.0)
    M[:3, 1] = (0.0, u[2], -u[1])
    M[:3, 2] = u
    M[:3, 3] = origin
    return M


def turret_pose(tool: int, x_tip: float, r: float, index_deg: float | None = None) -> tuple[np.ndarray, np.ndarray]:
    """(the turret's matrix "turret", the drum's index turn "turret_rot") with tool `tool` at work: a radial tool's tip
    at cell x = x_tip, r from the spindle's axis on the turret's side; an axial tool's tip at x = x_tip on the axis
    (r = 0), or r further back along the slant (to clear the bar)."""
    if tool in (1, 4):
        org = np.array([x_tip, SPIN_Y, SPIN_Z]) - TURRET_U * (TURRET_R + r)
    else:
        org = np.array([x_tip - TOOL_L, SPIN_Y, SPIN_Z]) - TURRET_U * (TURRET_R + r)
    ang = -TOOL_ANG[tool] if index_deg is None else index_deg
    return T(org), R((1, 0, 0), ang)


# ------------------------------------------------------------------------------------------------ the catcher
# A tray on the parts catcher's arm (ours), its frame at the middle of its floor's top. Under the spindle its long side
# runs along x, under the cup being parted; it then turns 90 deg as it comes down to the belt, so the cup lies along
# the belt, base first, and is tipped out over the tray's low side wall onto the belt.
CATCH_PARK = np.array([BELT_X - 150.0, -985.0, 985.0])
CATCH_UNDER = np.array([BELT_X, SPIN_Y, SPIN_Z - CUP_R - 2.0])
CATCH_BELT = np.array([BELT_X, BELT_Y[0] + 55.0, BELT_Z + 6.0])


def catcher_parts() -> dict:
    tray = _merge([_box(-40, 34, -22, 22, -3, 0), _box(-40, 34, -22, -19, -3, 6), _box(-40, 34, 19, 22, -3, 6)])
    arm = _box(-56, -40, -6, 6, -3, 4)
    return {"catcher/tray": (_merge([tray, arm]), (0.62, 0.63, 0.66), 1.0)}


def upender_parts() -> dict:
    """The upender at the belt's end (ours), in its own frame at the pivot: a 30 mm trough the lying cup slides onto
    base first, against an end plate. Turned -90 deg about x it stands the cup up, mouth up, on the end plate, with the
    trough a low wall on its south side, below the gripper's pads."""
    r = CUP_R
    floor = _box(-14, 14, -30, 0, -6, 0)
    walls = _merge([_box(-r - 4.5, -r - 1.5, -30, 0, -6, 7), _box(r + 1.5, r + 4.5, -30, 0, -6, 7),
                    _box(-r - 4.5, r + 4.5, -30, 0, -6, -3)])
    end = _box(-14, 14, 0, 6, -6, 2 * r + 4)
    hinge = _cyl((-r - 6, 3, -3), (r + 22, 3, -3), 5.0, res=16)
    return {"upender/body": (_merge([floor, walls, end]), STEEL, 1.0), "upender/hinge": (hinge, DARK, 1.0)}


def upender_pose(u: float) -> np.ndarray:
    return T((BELT_X, UP_Y, BELT_Z)) @ R((1, 0, 0), -90.0 * u)


# ------------------------------------------------------------------------------------------------ the cell's stations
BASKET_CAP = 125.0               # the cap's underside over the basket's feet: shuts a vessel 125 mm deep
BASKET_HANDLE = 152.0            # the handle bar's centre


def basket_parts() -> tuple[dict, list, list, np.ndarray]:
    """The cleaning basket (ours, 316 stainless): one row along y of the run's four cups with its four plugs between
    them, under a cap plate that shuts the IPA vessel it is lowered into, a handle bar on the cap. Frame: the middle
    of its feet's underside. A level gripper sets each cup in from +x; the pads pass over the 9.5 mm plugs. Returns its
    parts, the cup and plug seats and the handle's centre."""
    fx, fy = 40.0, 214.0
    ys, yp = [-66.0, -22.0, 22.0, 66.0], [-44.0, 0.0, 44.0, 88.0]
    feet = [_box(-fx / 2, fx / 2, -fy / 2, -fy / 2 + 10, 0, 4), _box(-fx / 2, fx / 2, fy / 2 - 10, fy / 2, 0, 4)]
    floor = _box(-fx / 2, fx / 2, -fy / 2, fy / 2, 4, 8)
    rims = [_ring(C.STOCK_D / 2 + 3.0, C.STOCK_D / 2 + 0.8, 8, 13).translate((0, y, 0), inplace=False) for y in ys]
    rims += [_ring(C.CUP_BORE_D / 2 + 2.5, C.CUP_BORE_D / 2 + 0.6, 8, 11).translate((0, y, 0), inplace=False)
             for y in yp]
    posts = [_box(sx * 16 - 4, sx * 16 + 4, sy * 102 - 4, sy * 102 + 4, 4, BASKET_CAP) for sx in (-1, 1)
             for sy in (-1, 1)]
    cap = _box(-33, 33, -118, 118, BASKET_CAP, BASKET_CAP + 4)
    hposts = [_box(-4, 4, s_ * 50 - 4, s_ * 50 + 4, BASKET_CAP + 4, BASKET_HANDLE - 7) for s_ in (-1, 1)]
    bar = _box(-7, 7, -60, 60, BASKET_HANDLE - 7, BASKET_HANDLE + 7)
    parts = {"basket/frame": (_merge(feet + [floor] + posts + hposts + [bar]), SS, 1.0),
             "basket/cap": (cap, (0.70, 0.71, 0.74), 1.0), "basket/rims": (_merge(rims), SS, 1.0)}
    return parts, [np.array([0, y, 8.0]) for y in ys], [np.array([0, y, 8.0]) for y in yp], np.array(
        [0, 0, BASKET_HANDLE])


def bath_parts() -> dict:
    """Two bench ultrasonic baths (sized after Elma's Elmasonic P 60 H: 186 x 365 x 271 mm outside), water in each
    tank, and in each ONE closed stainless vessel of IPA hung from a cover plate (ours: 46 x 196 mm inside, 125 deep,
    76 mm of IPA, about 0.6 L): Elma allows "max. 1 litre" of a flammable liquid, in a separate vessel standing in
    water. A slot hood behind draws off the vapour (the same duct as the dryer's pump)."""
    tanks, plates, water, vessels, ipa = [], [], [], [], []
    for k, (px, py) in PANS.items():
        hx, hy = TANK["x"] / 2, TANK["y"] / 2
        tanks.append(_open_box(px - hx, px + hx, py - hy, py + hy, BENCH_Z, TANK["top"], 4))
        tanks.append(_box(px + hx, px + hx + 6, py - 120, py + 40, BENCH_Z + 30, BENCH_Z + 120))      # its panel
        ix, iy, w = PAN["ix"], PAN["iy"], PAN["wall"]
        z1, z0 = PAN["rim"], PAN["rim"] - PAN["depth"]
        plates.append(_holed(px - hx, px + hx, py - hy, py + hy, TANK["top"], TANK["top"] + 3,
                             [(px - ix / 2 - w, px + ix / 2 + w, py - iy / 2 - w, py + iy / 2 + w)]))
        vessels.append(_open_box(px - ix / 2 - w, px + ix / 2 + w, py - iy / 2 - w, py + iy / 2 + w, z0 - w, z1, w))
        vessels.append(_holed(px - ix / 2 - 10, px + ix / 2 + 10, py - iy / 2 - 10, py + iy / 2 + 10, z1 - 3, z1,
                              [(px - ix / 2, px + ix / 2, py - iy / 2, py + iy / 2)]))
        water.append(_box(px - hx + 4, px + hx - 4, py - hy + 4, py + hy - 4, BENCH_Z + 24, TANK["water"]))
        ipa.append(_box(px - ix / 2, px + ix / 2, py - iy / 2, py + iy / 2, z0, z0 + PAN["ipa"]))
    x0 = min(p[0] for p in PANS.values()) - TANK["x"] / 2
    hood = _merge([_box(x0 - 110, x0 - 50, -230, 190, BENCH_Z, TANK["top"] + 260),
                   _box(x0 - 110, x0 - 90, -210, 170, TANK["top"] + 40, TANK["top"] + 230),
                   _cyl((x0 - 80, -20, TANK["top"] + 260), (x0 - 80, -20, 2700), 60.0, res=32)])
    return {"bath/tank": (_merge(tanks), (0.72, 0.73, 0.75), 1.0),
            "bath/plate": (_merge(plates), (0.66, 0.67, 0.70), 1.0),
            "bath/water": (_merge(water), WATER, 0.40),
            "bath/vessel": (_merge(vessels), SS, 1.0),
            "bath/ipa": (_merge(ipa), IPA, 0.55),
            "bath/hood": (hood, (0.62, 0.64, 0.68), 1.0)}


def pan_lid(k: str) -> tuple[pv.PolyData, np.ndarray]:
    """A vessel's lid (hinged at its -x edge), in its own frame at the hinge; and where the hinge is. It shuts the
    vessel whenever the basket isn't in it (the basket's own cap shuts it while it is)."""
    ix, iy = PAN["ix"], PAN["iy"]
    lid = _merge([_box(0, ix + 74, -iy / 2 - 12, iy / 2 + 12, 0, 5), _box(ix + 60, ix + 74, -30, 30, 5, 20)])
    px, py = PANS[k]
    return lid, np.array([px - ix / 2 - 37, py, PAN["rim"]])


def dryer_parts() -> dict:
    """The vacuum dryer (ours): a heated stainless pot with a hinged lid, a chemistry diaphragm pump and a condenser
    under the bench, its exhaust to the bath's duct."""
    x, y = DRYER
    rim, fl = DRYER_RIM, BASKET[2]
    pot = C.lathe([(DRYER_R - 8, BENCH_Z + 12), (DRYER_R, BENCH_Z + 12), (DRYER_R, rim), (DRYER_R - 8, rim),
                   (DRYER_R - 8, BENCH_Z + 20)], res=64).translate((x, y, 0), inplace=False)
    floor = C.lathe([(0, fl - 8), (DRYER_R - 8, fl - 8), (DRYER_R - 8, fl), (0, fl)], res=64).translate(
        (x, y, 0), inplace=False)
    flange = _ring(DRYER_R + 14, DRYER_R - 8, rim - 8, rim).translate((x, y, 0), inplace=False)
    base = _box(x - DRYER_R - 20, x + DRYER_R + 20, y - DRYER_R - 20, y + DRYER_R + 20, BENCH_Z, BENCH_Z + 12)
    pump = _box(-1080, -800, y - 130, y + 130, 120, 400)
    cond = _merge([_cyl((-1000, y + 230, 120), (-1000, y + 230, 560), 55.0, res=24),
                   _cyl((x - DRYER_R - 5, y, BENCH_Z - 60), (-1000, y, BENCH_Z - 60), 12.0, res=16)])
    return {"dryer/pot": (_merge([pot, flange, base]), SS, 1.0), "dryer/floor": (floor, (0.50, 0.51, 0.53), 1.0),
            "dryer/pump": (_merge([pump, cond]), (0.20, 0.36, 0.62), 1.0)}


def dryer_lid() -> tuple[pv.PolyData, np.ndarray]:
    """The dryer's lid, hinged on its north (+y) edge so it opens away from the arm and inside the fence; its own
    frame at the hinge."""
    x, y = DRYER
    disc = C.lathe([(0, 0), (DRYER_R + 14, 0), (DRYER_R + 14, 14), (0, 14)], res=64).translate(
        (0, -(DRYER_R + 14), 0), inplace=False)
    knob = _box(-30, 30, -(2 * DRYER_R + 40), -(2 * DRYER_R + 8), 0, 30)
    win = _cyl((0, -(DRYER_R + 14), 14), (0, -(DRYER_R + 14), 16), 70.0, res=48)
    return _merge([disc, knob, win]), np.array([x, y + DRYER_R + 14, DRYER_RIM])


def weigh_parts() -> dict:
    """A weigh module made for automation (sized after a Mettler Toledo WXS/WMS class unit: an estimate), a seat for
    the cup on its pan, and a glass draft shield that lifts on two rods."""
    x, y, z = WEIGH
    base = _box(x - 90, x + 110, y - 130, y + 130, BENCH_Z, z - 25)
    seat = _merge([_cyl((x, y, z - 25), (x, y, z - 6), 20.0, res=32), _ring(C.STOCK_D / 2 + 3, C.STOCK_D / 2 + 0.6,
                                                                          z - 6, z + 3).translate((x, y, 0),
                                                                                                  inplace=False)])
    rods = _merge([_cyl((x + 100, y + s * 60, z - 25), (x + 100, y + s * 60, z + 260), 6.0, res=16) for s in (-1, 1)])
    disp = _box(x + 110, x + 118, y - 60, y + 60, BENCH_Z + 10, BENCH_Z + 70)
    return {"weigh/base": (_merge([base, disp]), (0.88, 0.88, 0.86), 1.0), "weigh/seat": (seat, STEEL, 1.0),
            "weigh/rods": (rods, STEEL, 1.0)}


def weigh_shield() -> dict:
    x, y, z = WEIGH
    tube = C.lathe([(66, 0), (70, 0), (70, 110), (66, 110)], res=64).translate((x, y, z - 18), inplace=False)
    top = C.lathe([(0, 106), (70, 106), (70, 110), (0, 110)], res=64).translate((x, y, z - 18), inplace=False)
    collar = _merge([_box(x + 60, x + 106, y + s * 60 - 9, y + s * 60 + 9, z + 70, z + 92) for s in (-1, 1)])
    return {"shield/glass": (_merge([tube, top]), GLASS, 0.30), "shield/collar": (collar, STEEL, 1.0)}


def vision_parts() -> dict:
    """An image-dimension gauge (sized after Keyence's IM-8000 class: estimates): a lit glass stage, a column at the
    back and the camera head over the stage."""
    x, y, z = VISION
    base = _box(x - 130, x + 150, y - 150, y + 150, BENCH_Z, z - 3)
    stage = _cyl((x, y, z - 3), (x, y, z), 62.0, res=48)
    col = _box(x + 150, x + 200, y - 30, y + 30, BENCH_Z, z + 470)
    arm = _box(x - 70, x + 200, y - 55, y + 55, z + 420, z + 470)
    lens = _merge([_cyl((x, y, z + 420), (x, y, z + 300), 48.0, res=32),
                   _ring(70.0, 52.0, z + 290, z + 304).translate((x, y, 0), inplace=False)])
    return {"vision/body": (_merge([base, col, arm]), (0.93, 0.93, 0.92), 1.0), "vision/stage": (stage, GLASS, 0.55),
            "vision/lens": (lens, DARK, 1.0)}


def rack_lid_mesh() -> tuple[pv.PolyData, float]:
    """The cassette's lid (ours, printed PETG): a cover over charge.rack(), open below, a knob on top. Frame: the
    rack's frame, the lid seated. Returns it and the knob's grasp height in that frame."""
    w = C.RACK_COLS * C.RACK_PITCH + 16 + 2.0          # 1 mm clear of the rack all round
    d, h0, h1, t = 80.0 + 2.0, C.RACK_H, C.RACK_H + 52.0, 3.0
    shell = _merge([_box(-w / 2 - t, w / 2 + t, -d / 2 - t, d / 2 + t, h1 - t, h1),
                    _box(-w / 2 - t, -w / 2, -d / 2 - t, d / 2 + t, h0 - 12, h1), _box(w / 2, w / 2 + t, -d / 2 - t,
                                                                                      d / 2 + t, h0 - 12, h1),
                    _box(-w / 2 - t, w / 2 + t, -d / 2 - t, -d / 2, h0 - 12, h1), _box(-w / 2 - t, w / 2 + t, d / 2,
                                                                                      d / 2 + t, h0 - 12, h1)])
    knob = _box(-10, 10, -18, 18, h1, h1 + 38)
    return _merge([shell, knob]), h1 + 28.0


def bench_parts() -> dict:
    """The three benches round the arm, its pedestal, the fence (the front open over the north bench, behind a light
    curtain, for the MiR's arm), and the floor."""
    tops, legs = [], []
    for (x0, x1, y0, y1) in ((-1080, -590, -700, 760), (550, 1080, -700, 760), (-590, 550, 620, 940)):
        tops.append(_box(x0, x1, y0, y1, BENCH_Z - 30, BENCH_Z))
        for (lx, ly) in ((x0 + 40, y0 + 40), (x1 - 40, y0 + 40), (x0 + 40, y1 - 40), (x1 - 40, y1 - 40)):
            legs.append(_box(lx - 25, lx + 25, ly - 25, ly + 25, 0, BENCH_Z - 30))
    ped = _merge([_box(-130, 130, -130, 130, 0, Z_ARM - 15), _box(-300, 300, -300, 300, 0, 20),
                  _box(-140, 140, -140, 140, Z_ARM - 15, Z_ARM)])
    stand = _box(BASKET[0] - 30, BASKET[0] + 30, BASKET[1] - 112, BASKET[1] + 112, BENCH_Z, BASKET[2])
    riser = _box(RACK_AT[0] - 185, RACK_AT[0] + 185, RACK_AT[1] - 50, RACK_AT[1] + 50, BENCH_Z, RACK_AT[2])
    rest = _box(LID_REST[0] - 50, LID_REST[0] + 50, LID_REST[1] - 185, LID_REST[1] + 185, BENCH_Z, BENCH_Z + 8)
    blow = BLOW
    bd = radial(BLOW)
    side = np.array([-bd[1], bd[0], 0.0])
    far = np.r_[bd, 0.0]
    post = blow + far * 70.0
    blow_m = _merge([_box(blow[0] - 70, blow[0] + 70, blow[1] - 45, blow[1] + 45, BENCH_Z, BENCH_Z + 10),
                     _cyl((post[0], post[1], BENCH_Z + 10), (post[0], post[1], blow[2] + 130), 9.0, res=16),
                     _cyl(post + (0, 0, 130), blow + (0, 0, 130), 5.0, res=12),
                     _cyl(blow + (0, 0, 130), blow + (0, 0, 95), 3.0, res=12)])
    ring = _merge([_cyl(blow + side * 52 + (0, 0, 12), blow + side * 22 + (0, 0, 12), 4.0, res=12),
                   _cyl(blow - side * 52 + (0, 0, 12), blow - side * 22 + (0, 0, 12), 4.0, res=12),
                   _cyl(post + (0, 0, 12), blow + side * 52 + (0, 0, 12), 4.0, res=12),
                   _cyl(post + (0, 0, 12), blow - side * 52 + (0, 0, 12), 4.0, res=12)])
    sock = _merge([_box(blow[0] - 70, blow[0] + 70, blow[1] - 45, blow[1] + 45, BENCH_Z, blow[2] - 90),
                   _open_box(blow[0] - 45, blow[0] + 45, blow[1] - 40, blow[1] + 40, blow[2] - 90, blow[2] - 4, 3)])
    posts, rails, mesh = [], [], []
    fx0, fx1, fy0, fy1, fh = -1100.0, 1100.0, Y_FRONT + 10, FRONT_Y, 1400.0
    for (x, y) in ((fx0, fy0), (fx0, fy1), (fx1, fy0), (fx1, fy1), (fx0, 80), (fx1, 80), (-420, fy1), (420, fy1)):
        posts.append(_box(x - 20, x + 20, y - 20, y + 20, 0, fh))
    for (xa, xb, ya, yb) in ((fx0, fx0, fy0, fy1), (fx1, fx1, fy0, fy1), (fx0, -420, fy1, fy1), (420, fx1, fy1, fy1)):
        rails.append(_box(xa - 15, xb + 15, ya - 15, yb + 15, fh - 30, fh))
        rails.append(_box(xa - 15, xb + 15, ya - 15, yb + 15, 100, 130))
        mesh.append(_box(xa - 2, xb + 2, ya - 2, yb + 2, 130, fh - 30))
    curtain = _merge([_box(-420 - 25, -420 + 25, fy1 - 25, fy1 + 25, BENCH_Z, 1400),
                      _box(420 - 25, 420 + 25, fy1 - 25, fy1 + 25, BENCH_Z, 1400)])
    floor = _box(-1700, 2700, -3900, 1600, -20, 0)
    tape = _merge([_box(fx0 - 60, fx1 + 60, fy1 + 20, fy1 + 80, 0, 1.5)])
    return {"bench/tops": (_merge(tops), TOP_C, 1.0), "bench/legs": (_merge(legs + [stand, riser, rest]), BENCH_C, 1.0),
            "bench/ped": (ped, (0.30, 0.31, 0.33), 1.0),
            "bench/blow": (_merge([blow_m, sock]), (0.36, 0.37, 0.40), 1.0),
            "bench/ring": (ring, (0.20, 0.55, 0.85), 1.0),
            "fence/posts": (_merge(posts + rails), FENCE, 1.0), "fence/mesh": (_merge(mesh), (0.25, 0.25, 0.26), 0.12),
            "fence/curtain": (curtain, (0.95, 0.55, 0.10), 1.0),
            "floor": (floor, FLOOR_C, 1.0), "floor_tape": (tape, (0.98, 0.80, 0.10), 1.0)}


def chips(n=60, seed=3) -> pv.PolyData:
    """Swarf on the chip pan under the work: short curls (fluids for the collision checks)."""
    rng = np.random.default_rng(seed)
    ms = []
    for _ in range(n):
        t = np.linspace(0, 2.5 * math.pi, 18)
        r = rng.uniform(2.0, 4.0)
        pts = np.c_[r * np.cos(t), r * np.sin(t), np.linspace(0, rng.uniform(4, 10), len(t))]
        line = pv.lines_from_points(pts)
        tube = line.tube(radius=0.7, n_sides=5)
        ang = rng.uniform(0, 360, 3)
        tube = tube.rotate_x(ang[0], inplace=False).rotate_y(ang[1], inplace=False).rotate_z(ang[2], inplace=False)
        tube = tube.translate((rng.uniform(-60, 200), rng.uniform(SPIN_Y - 60, SPIN_Y + 260), 664 + rng.uniform(0, 8)),
                              inplace=False)
        ms.append(tube.triangulate())
    return _merge(ms)


# ------------------------------------------------------------------------------------------------ in the lab
CTX_H = {"instron_floor": 2000.0, "instron_small": 1500.0, "fumehood": 2581.0, "charger0": 287.0, "charger1": 287.0,
         "ded": 2000.0, "wire_edm": 2200.0, "eos_m400": 2700.0, "repowder": 2000.0, "sieve_cell": 1150.0,
         "vlm": 6000.0, "vlm2": 6000.0, "glovebox": 1900.0, "aconity": 2200.0, "packaging": 1200.0}
CTX_NAME = {"instron_floor": "Instron 68FM-100", "instron_small": "Instron 68SC-2", "fumehood": "fume hood",
            "charger0": "MiR charger 0", "charger1": "MiR charger 1", "vlm": "Kardex VLM 1", "vlm2": "Kardex VLM 2",
            "repowder": "rePowder atomizer", "sieve_cell": "sieving cell", "ded": "DED"}


def lab_context(sc) -> list:
    """The cell's neighbours on the lab floor (out/tray_plan.json's footprints, heights estimated), the aisle's tape
    and a MiR250 docked at the cell's front, in the cell's frame (machining.FLOOR is where the cell stands). Returns
    leader labels for them."""
    import json
    import machining as MA
    fl = json.loads((HERE / "out" / "tray_plan.json").read_text())["floor"]
    X, Y = MA.FLOOR["x"], MA.FLOOR["y"]
    labels = []
    boxes = []
    for k, (x0, x1, y0, y1) in fl["machines"].items():
        if k not in CTX_H or abs((x0 + x1) / 2 - X) > 9000:
            continue
        boxes.append(_box(x0 - X, x1 - X, y0 - Y, y1 - Y, 0, CTX_H[k]))
        if k in CTX_NAME:
            labels.append((CTX_NAME[k], ((x0 + x1) / 2 - X, (y0 + y1) / 2 - Y, CTX_H[k])))
    sc.add("ctx/machines", _merge(boxes), (0.82, 0.84, 0.87), "ctx", opacity=1.0, specular=0.1)
    a = fl["aisle_mm"]
    tape = _merge([_box(a[0] - X, a[1] - X, yy - Y - 30, yy - Y + 30, 0, 2) for yy in (a[2], a[3])])
    sc.add("ctx/tape", tape, (0.98, 0.80, 0.10), "ctx")
    sc.add("ctx/floor", _box(-9500, 9500, -4500, 9000, -25, -1), FLOOR_C, "ctx", specular=0.05)
    dx, dy, _ = MA.FLOOR["dock"]
    mir = _merge([_box(dx - X - 445, dx - X + 445, dy - Y - 290, dy - Y + 290, 0, 350),
                  _box(dx - X - 200, dx - X + 200, dy - Y - 200, dy - Y + 200, 350, 750)])
    sc.add("ctx/mir", mir, (0.30, 0.31, 0.33), "ctx", specular=0.2)
    labels.append(("MiR250 docked at the cell", (dx - X, dy - Y, 750)))
    return labels


def still_lab(sc, path):
    """One frame: the cell in its place on the floor, from over the aisle (MCELL_STILL=lab)."""
    from PIL import Image
    labs = lab_context(sc)
    sc.cam = [(3600, 4300, 4300), (-700, -900, 600), (0, 0, 1)]
    sc.view_angle = 40.0
    keep = {"Instron 68SC-2", "MiR charger 0", "Instron 68FM-100", "MiR250 docked at the cell"}
    sc.caption = ("The cup-and-plug cell on the south row, seen from over the aisle: its front between the Instron "
                  "68SC-2 and MiR charger 0, where a MiR250 docks; the lathe and its bar feeder behind the row.")
    sc.title = "Vertical cloud lab: the charge-cup machining cell in the lab"
    labs = [(t, xyz) for t, xyz in labs if t in keep]
    labs += [("the machining cell: bar-fed lathe, UR10e, IPA baths, vacuum dryer, weigh, gauge, cassette",
              (0.0, 300.0, 1450.0)), ("Haas ST-10 lathe (as measured)", (-200.0, -1500.0, 1842.0)),
             ("4 ft bar feeder", (2300.0, -1200.0, 1250.0))]
    sc.labels = []
    sc.render_base()                                    # sets the camera, so the anchors can be projected
    placed = []
    for t, xyz in labs:
        px, py = sc.project(xyz)
        fx = max(0.02, px - 0.10) if px < 0.5 else min(0.98, px + 0.10)
        fy = min(0.86, max(0.08, py - 0.08))
        while any(abs(fy - q) < 0.045 and (fx < 0.5) == (r < 0.5) for r, q in placed):
            fy = min(0.86, fy + 0.05)
        placed.append((fx, fy))
        sc.labels.append((t, xyz, (fx, fy), 1.0))
    base = sc.render_base()
    anchors = [sc.project(xyz) for _, xyz, _, _ in sc.labels]
    img = sc.overlay(Image.fromarray(base), SC_size_scale(sc), anchors)
    img.convert("RGB").save(path, optimize=True)
    print("wrote", path)


def SC_size_scale(sc) -> float:
    import scene
    return scene.size_scale(sc.size)


# ------------------------------------------------------------------------------------------------ the clip
def movie():
    metal = os.environ.get("MCELL_METAL", "Al")
    col = AL if metal == "Al" else CU_C
    lab = os.environ.get("MCELL_STILL") == "lab"
    # the still writes no video: a Scene opens its MP4 encoder on out/mp4/<name>.mp4 at once, and on 2026-11-20 a
    # still run beside the render truncated the render's MP4 under it. The GIF is cut from the MP4 afterwards (gif())
    sc = Scene(NAME, TITLE, gif=False, mp4=not lab)
    sc.fluids = set()
    sc.soft = set()
    # --- static parts
    for name, (m, c, op) in {**bench_parts(), **lathe_parts(), **bath_parts(), **dryer_parts(), **weigh_parts(),
                             **vision_parts()}.items():
        grp = "static" if name == "bench/ped" else name.split("/")[0]     # the arm stands on "static": its pedestal
        sc.add(name, m, c, grp, opacity=op, specular=0.2)                  # one group per station, for the audit
    for nm in ("bath/water", "bath/ipa"):
        sc.fluids.add(nm)
    # --- moving parts
    for name, (m, c, op) in collet_parts().items():
        sc.add(name, m, c, "spindle", opacity=op)
    for name, (m, c, op) in turret_parts().items():
        sc.add(name, m, c, "turret_rot", opacity=op, specular=0.5)
    sc.parent["turret_rot"] = "turret"
    for name, (m, c, op) in catcher_parts().items():
        sc.add(name, m, c, "catcher", opacity=op)
    sc.gmat["catcher"] = T(CATCH_PARK)
    for name, (m, c, op) in upender_parts().items():
        sc.add(name, m, c, "upender", opacity=op)
    sc.gmat["upender"] = upender_pose(0.0)
    sc.add("work", work_mesh(end_x=END0), col, "work", specular=0.6)
    sc.add("chips", chips(), CHIP, "chips", specular=0.6, shown=False)
    sc.fluids.add("chips")
    # the cup: whole and in half section
    sc.add("cup/whole", C.cup(), col, "cup", specular=0.6, shown=False)
    sc.add("cup/cut", C.cup(cut=True), col, "cup", specular=0.6, shown=False)
    sc.gmat["cup"] = cup_in_bar()
    # the basket with the run's other three cups and four plugs
    bparts, cup_seats, plug_seats, handle = basket_parts()
    for name, (m, c, op) in bparts.items():
        sc.add(name, m, c, "basket", opacity=op, specular=0.5)
    sc.gmat["basket"] = T(BASKET)
    for i, s in enumerate(cup_seats):
        if i != BASKET_POCKET:
            sc.add(f"bcup{i}", C.cup(), col, f"bcup{i}", specular=0.6)
            sc.gmat[f"bcup{i}"] = T(s)
            sc.parent[f"bcup{i}"] = "basket"
    for i, s in enumerate(plug_seats):
        sc.add(f"bplug{i}", C.plug(), col, f"bplug{i}", specular=0.6)
        sc.gmat[f"bplug{i}"] = T(s)
        sc.parent[f"bplug{i}"] = "basket"
    # pan lids and the dryer's lid, on their hinges
    lids = {}
    for k in PANS:
        m, hinge = pan_lid(k)
        sc.add(f"lid_{k}/plate", m, (0.66, 0.67, 0.70), f"lid_{k}", specular=0.5)
        lids[k] = hinge
        sc.gmat[f"lid_{k}"] = T(hinge)
    m, dhinge = dryer_lid()
    sc.add("dlid/plate", m, SS, "dlid", specular=0.5)
    sc.gmat["dlid"] = T(dhinge)
    # the weigh module's shield, the cassette (charge rack) and its lid on the rest
    for name, (m, c, op) in weigh_shield().items():
        sc.add(name, m, c, "shield", opacity=op)
    rk_body, rk_rims, rk_seats = C.rack()
    sc.add("rack/body", rk_body, PRINTED, "rack", specular=0.2)
    sc.add("rack/rims", rk_rims, PRINTED, "rack", specular=0.2)
    sc.gmat["rack"] = T(RACK_AT)
    lid_m, lid_grasp = rack_lid_mesh()
    sc.add("rlid/body", lid_m, (0.93, 0.93, 0.95), "rlid", opacity=1.0, specular=0.2)
    sc.gmat["rlid"] = T(LID_REST + (0, 0, 8.0 - C.RACK_H + 12.0)) @ R((0, 0, 1), 90.0)
    for i in range(4):                                   # the run's set lands in pockets 0-3; 4-7 stay for the next run
        if i != HERO:
            sc.add(f"rcup{i}", C.cup(), col, f"rcup{i}", specular=0.6, shown=False)
            sc.gmat[f"rcup{i}"] = T(RACK_AT + np.array(rk_seats["cup"][i]))
        sc.add(f"rplug{i}", C.plug(), col, f"rplug{i}", specular=0.6, shown=False)
        sc.gmat[f"rplug{i}"] = T(RACK_AT + np.array(rk_seats["plug"][i]))
    # --- the arm
    rb = RB.Robot(sc, "ur10e", "static", T((0, 0, Z_ARM)), q0=PARK)
    sc.apply()
    if os.environ.get("MCELL_STILL") == "lab":
        sc.show(["floor"], 0.0)
        return still_lab(sc, HERE / "out" / "machining_lab.png")

    # --- helpers
    def status(**kv):
        g = dict(sc.gauges)
        g.update(kv)
        sc.gauges = list(g.items())

    status(Lathe="bar in: 5N Al, Ø20 mm" if metal == "Al" else "bar in: OFE Cu (C10100), Ø20 mm",
           Cup="-", Basket="3 of 4 cups, 4 of 4 plugs", Bath="IPA vessels shut", Dryer="vented, lid shut",
           Arm="UR10e, parked")

    def spin(u, n0=[0.0], rate=4.0):
        sc.gmat["spindle"] = (T((0, SPIN_Y, SPIN_Z)) @ R((1, 0, 0), (n0[0] + u * 360 * rate) % 360)
                              @ T((0, -SPIN_Y, -SPIN_Z)))

    TS = {"tool": 1, "x": END0 - 60.0, "r": 40.0}       # the tool at work, its tip's x and r

    def tur(tool, x_tip, r, idx=None):
        Mt, Mr = turret_pose(tool, x_tip, r, idx)
        sc.gmat["turret"], sc.gmat["turret_rot"] = Mt, Mr
        TS.update(tool=tool, x=x_tip, r=r)

    tur(1, END0 - 60.0, 40.0)
    W = {"end": END0, "turned": 0.0, "hole_r": 0.0, "hole_d": 0.0, "groove": 0.0}

    def rework():
        sc.set_mesh("work", work_mesh(end_x=W["end"], turned=W["turned"], hole_r=W["hole_r"], hole_d=W["hole_d"],
                                      groove=W["groove"]))

    def door_fade(u):
        sc.show(["lathe/door"], 1.0 - 0.85 * u)
        sc.show(["lathe/glass"], 1.0 - u)

    sc.title = TITLE
    CAM_WIDE = [(3700, 3500, 3700), (-100, -550, 900), (0, 0, 1)]
    dS = np.array([0.0, SPIN_Y + 1270.0, SPIN_Z - 1050.0])    # the spindle's move from round 13's (y -1270, z 1050)
    CAM_LATHE = [tuple(np.array((430, -470, 1300)) + dS), tuple(np.array((150, -1020, 950)) + dS), (0, 0, 1)]
    CAM_WORK = [tuple(np.array((150, -765, 1120)) + dS), (162, SPIN_Y, SPIN_Z), (0, 0, 1)]
    CAM_NEST = [(620, -130, 1380), (140, -690, 950), (0, 0, 1)]
    CAM_BATH = [(-200, 1350, 2350), (-800, -150, 1050), (0, 0, 1)]
    CAM_EAST = [(1010, -120, 1650), (700, -420, 1000), (0, 0, 1)]
    CAM_GAUGE = [(1020, -260, 1380), (740, 150, 1010), (0, 0, 1)]
    CAM_RACK = [(-250, 1180, 1450), (60, 740, 960), (0, 0, 1)]
    sc.cam = CAM_WIDE

    # 1: the cell
    sc.step("1/6", "The charge-cup cell on the lab floor: a bar-fed CNC lathe, a UR10e on a pedestal, two ultrasonic "
                   "baths each holding one closed vessel of IPA, a vacuum dryer, a weigh module, a dimension gauge and "
                   "the cup rack the MiR250 takes to tray J.", 3.0, hold=1.5,
            labels=[("bar-fed CNC lathe (Haas ST-10 size) + 4 ft bar feeder", (300, -1300, 2167), (0.62, 0.10)),
                    ("UR10e on a pedestal", (0, 0, 1300), (0.42, 0.22)),
                    ("2 ultrasonic baths, each with 1 closed IPA vessel", (-805, -20, 1160), (0.06, 0.40)),
                    ("vacuum dryer", (-860, 420, 1210), (0.08, 0.58)),
                    ("weigh module", tuple(WEIGH + (0, 0, 100)), (0.86, 0.36)),
                    ("dimension gauge", tuple(VISION + (0, 0, 330)), (0.87, 0.52)),
                    ("cup rack (cassette) for tray J", tuple(RACK_AT + (0, 0, 60)), (0.55, 0.82))])

    # 2: in the lathe
    def feed(u):
        W["end"] = END0 + 75.0 * (1 - u)
        W["end"] = min(W["end"], X_COLLET - 4.0)
        rework()
        tur(1, END0 - 60.0 + 60.0 * u, 40.0 - 28.0 * u)
    W["end"] = X_COLLET - 4.0
    rework()
    sc.step("2/6", "The bar loader pushes the Ø20 mm bar 72.5 mm out of the collet. Bar and cup are drawn in half "
                   "section, the door see-through.", 2.5, RB.both(feed, door_fade), cam_to=CAM_WORK, view_angle_to=19.0,
            hold=0.4)

    def face_turn(u):
        spin(u, rate=10)
        if u < 0.25:                                     # face: across the end, from the OD to the centre
            v = u / 0.25
            W["end"] = END0 + (END - END0) * v
            tur(1, W["end"], BAR_R + 1.0 - (BAR_R + 1.0) * v)
        else:                                            # turn the OD to 19.05 mm over 68 mm
            v = (u - 0.25) / 0.75
            W["end"] = END
            W["turned"] = 68.0 * v                      # past the parting groove (x 190-193)
            tur(1, END + W["turned"], CUP_R)
        rework()
    sc.step("2/6", "Turning tool: face the end, then turn the OD to 19.05 mm. Dry but for an alcohol MQL mist "
                   "at the insert (PCD or sharp uncoated carbide, kept for this metal only).", 4.0, face_turn, hold=0.3,
            labels=[("PCD turning insert", (END + 30, SPIN_Y - 20, SPIN_Z + 30), (0.18, 0.25))])
    sc.show(["chips"], 0.4)

    def index(tool, x_tip, r):
        """Retract the tool at work (an axial one out of its hole along -x first), take the turret to the index
        position (X_INDEX: every tool clear of the bar and the headstock), turn the drum, then bring the new tool to
        its start, (x_tip, r)."""
        t0, x0, r0 = TS["tool"], TS["x"], TS["r"]
        P0 = turret_pose(t0, x0, r0)[0][:3, 3]
        P1 = turret_pose(t0, END - 30.0, r0)[0][:3, 3] if t0 in (2, 3) else turret_pose(t0, x0, r0 + 50.0)[0][:3, 3]
        P2 = np.r_[X_INDEX, P1[1:] - TURRET_U[1:] * 60.0]
        P4 = (turret_pose(tool, END - 30.0, r) if tool in (2, 3) else turret_pose(tool, x_tip, r + 50.0))[0][:3, 3]
        P5 = turret_pose(tool, x_tip, r)[0][:3, 3]
        a0, a1 = -TOOL_ANG[t0], -TOOL_ANG[tool]
        da = (a1 - a0 + 180) % 360 - 180
        legs = [(P0, P1), (P1, P2), None, (P2, P4), (P4, P5)]

        def up(u):
            k = min(4, int(u * 5))
            v = u * 5 - k
            if legs[k] is None:
                sc.gmat["turret"] = T(P2)
                sc.gmat["turret_rot"] = R((1, 0, 0), a0 + da * v)
            else:
                pa, pb = legs[k]
                sc.gmat["turret"] = T(pa + (pb - pa) * v)
                sc.gmat["turret_rot"] = R((1, 0, 0), a0 if k < 2 else a1)
            if u >= 1.0:
                tur(tool, x_tip, r)
        return up
    # retract the turning tool off the bar first
    sc.step("2/6", "Index to the 12.5 mm drill.", 2.0, index(2, END - 20.0, 0.0), hold=0.1)

    def drill(u):
        spin(u, rate=10)
        d = 47.6 * u
        W["hole_r"], W["hole_d"] = DRILL_R, d
        tip = DRILL_R / math.tan(math.radians(59))
        tur(2, END + d + tip, 0.0)
        rework()
    sc.show(["chips"], 0.7)
    sc.step("2/6", "Drill 12.5 mm, 47.6 mm deep with a 118° point, pecking to break the chips (drawn as one pass).",
            3.5, drill, hold=0.3)
    sc.step("2/6", "Index to the boring bar.", 2.0, index(3, END - 20.0, 0.0), hold=0.1)

    def bore(u):
        spin(u, rate=10)
        W["hole_r"] = BORE_R
        tur(3, END - 20.0 + (47.6 + 20.0) * math.sin(math.pi * u), 0.0)
        rework()
    sc.step("2/6", "Finish-bore to 12.70 mm, the press fit's size for the plug, and break the rim's edge.", 3.0, bore,
            hold=0.2)
    def catch_in(u):
        """The tray from where it waits, along under the bar's level, then up under the cup."""
        mid = np.array([CATCH_UNDER[0], CATCH_UNDER[1] + 30.0, CATCH_UNDER[2] - 25.0])
        if u < 0.7:
            p = CATCH_PARK + (mid - CATCH_PARK) * (u / 0.7)
        else:
            p = mid + (CATCH_UNDER - mid) * ((u - 0.7) / 0.3)
        sc.gmat["catcher"] = T(p)
    sc.step("2/6", "Index to the parting blade; the parts catcher comes in under the cup.", 2.0,
            RB.both(index(4, GROOVE_X, CUP_R + 2.0), catch_in), hold=0.1)

    def part(u):
        spin(u, rate=10)
        W["groove"] = (CUP_R - 0.6) * u
        tur(4, GROOVE_X, CUP_R - W["groove"])
        rework()
    sc.show(["chips"], 1.0)
    sc.step("2/6", "Part off at 63.5 mm, the blade chamfering the cup's base on the way in.", 2.5, part, hold=0.1)
    # the cup comes free: the bar's stub stays in the collet, the cup drops 2 mm into the tray
    sc.set_mesh("work", stub_mesh())
    sc.show(["cup/cut"], 1.0)
    sc.gmat["cup"] = cup_in_bar()
    status(Cup="parted: Ø19.05 x 63.5 mm, bore 12.70 x 47.6 mm")
    M_drop = T((0, 0, -2.0)) @ cup_in_bar()

    def drop(u):
        sc.gmat["cup"] = T((0, 0, -2.0 * u)) @ cup_in_bar()
        tur(4, GROOVE_X, CUP_R + 40.0 * u)
    sc.step("2/6", "The cup drops into the catcher's tray.", 0.6, drop, hold=0.2)
    sc.parent["cup"] = "catcher"
    sc.gmat["cup"] = np.linalg.inv(sc.world("catcher")) @ M_drop

    def to_belt(u):
        sc.gmat["catcher"] = T(CATCH_UNDER + (CATCH_BELT - CATCH_UNDER) * u) @ R((0, 0, 1), 90.0 * u)
        tur(4, GROOVE_X + (X_INDEX - GROOVE_X) * u, CUP_R + 40.0 + 60 * u)
    sc.step("3/6", "The catcher brings it down to the belt, turning it to lie along the belt, base first ...", 2.0,
            to_belt, hold=0.1, cam_to=CAM_LATHE, view_angle_to=30.0)
    Wc = sc.world("cup")
    sc.parent.pop("cup")
    sc.gmat["cup"] = Wc
    on_belt = T((0, 70.0, BELT_Z + CUP_R - Wc[2, 3])) @ Wc

    def tip(u):                          # lifted clear of the tray, slid off its open end, set down on the belt
        dz = BELT_Z + CUP_R - Wc[2, 3]
        if u < 0.2:
            off = (0.0, 4.0 * u / 0.2)
        elif u < 0.75:
            off = (70.0 * (u - 0.2) / 0.55, 4.0)
        else:
            off = (70.0, 4.0 + (dz - 4.0) * (u - 0.75) / 0.25)
        sc.gmat["cup"] = T((0, off[0], off[1])) @ Wc
    sc.step("3/6", "... and tips it out onto the belt.", 1.0, tip, hold=0.1)

    def catcher_home(u):
        sc.gmat["catcher"] = T(CATCH_BELT + (CATCH_PARK - CATCH_BELT) * u) @ R((0, 0, 1), 90.0 * (1 - u))
    for name, (m, c, op) in upender_parts().items():
        sc.add(name, m, c, "upender", opacity=op)
    sc.gmat["upender"] = upender_pose(0.0)
    sc.show(["cup/cut"], 0.0)
    sc.show(["cup/whole"], 1.0)
    run = (UP_Y - CUP_L) - (on_belt @ np.array([0, 0, CUP_L, 1.0]))[1]      # the mouth's end to UP_Y - 63.5

    def belt(u):
        sc.gmat["cup"] = T((0, run * u, 0)) @ on_belt
        catcher_home(min(1.0, u * 2.0))
    sc.step("3/6", "The belt carries it out through the guard: the door stays shut and the arm never reaches into "
                   "the machine.", 3.0, belt, hold=0.2, cam_to=CAM_NEST)
    sc.parent["cup"] = "upender"
    sc.gmat["cup"] = np.linalg.inv(sc.world("upender")) @ (T((0, run, 0)) @ on_belt)
    sc.step("3/6", "The upender stands it up, mouth up.", 1.4,
            lambda u: sc.gmat.__setitem__("upender", upender_pose(u)), hold=0.2)
    status(Cup="stood up at the guard")

    # 3: the arm takes it, blows it off, into the basket
    nd = radial(NEST)
    g_n = lvl(NEST + (0, 0, CUP_GRASP), nd)
    g_n_back = g_n.copy()
    g_n_back[:3, 3] -= np.r_[nd, 0] * 120.0
    g_n_up = g_n.copy()
    g_n_up[2, 3] += 60.0
    sc.step("3/6", "The arm comes to the upender ...", 2.0, RB.both(rb.joint_to(Tw=g_n_back), rb.grip_to(OPEN_CUP)),
            hold=0.1, view_angle_to=30.0)
    sc.step("3/6", "", 1.2, rb.line_to(g_n), hold=0.1)
    sc.step("3/6", "... grips the cup ...", 0.5, rb.grip_to(GRIP_CUP), hold=0.1)
    rb.grasp("cup")
    status(Arm="UR10e: the cup", Cup="gripped")
    sc.show(["lathe/door", "lathe/glass"], 1.0)
    sc.step("3/6", "", 1.0, rb.line_to(g_n_up), hold=0.0)
    sc.step("3/6", "", 0.8, lambda u: sc.gmat.__setitem__("upender", upender_pose(1 - u)), hold=0.0)
    # blow-off: lower its foot into the ring, a lance over the bore
    bd = radial(BLOW)
    g_blow = lvl(BLOW + (0, 0, CUP_GRASP), bd)
    g_blow_hi = g_blow.copy()
    g_blow_hi[:3, 3] -= np.r_[bd, 0] * 130.0
    sc.step("3/6", "To the blow-off station: ...", 2.0, rb.joint_to(Tw=g_blow_hi), hold=0.0, cam_to=CAM_BATH)
    sc.step("3/6", "... two nozzles at its foot and a lance over the bore blow the chips off it.",
            1.5, rb.line_to(g_blow), hold=0.8)
    sc.step("3/6", "", 1.0, rb.line_to(g_blow_hi), hold=0.0)
    # into the basket's front row
    pocket = BASKET + cup_seats[BASKET_POCKET]
    g_bk = lvl(pocket + (0, 0, CUP_GRASP), (-1.0, 0.0))           # from the arm's side, square to the row
    g_bk_hi = g_bk.copy()
    g_bk_hi[2, 3] += 90.0
    g_bk_back = g_bk.copy()
    g_bk_back[0, 3] += 120.0
    g_bk_back_hi = g_bk_back.copy()
    g_bk_back_hi[2, 3] += 8.0
    sc.step("4/6", "Into the basket, the fourth cup of the run's set.", 2.0, rb.joint_to(Tw=g_bk_back_hi), hold=0.0)
    sc.step("4/6", "", 1.2, rb.line_to(T((0, 0, 8.0)) @ g_bk), hold=0.0)
    sc.step("4/6", "", 0.5, rb.line_to(g_bk), hold=0.1)
    sc.step("4/6", "", 0.5, rb.grip_to(OPEN_RACK), hold=0.1)
    rb.release("basket")
    status(Arm="UR10e", Basket="4 of 4 cups, 4 of 4 plugs", Cup="in the basket")
    sc.step("4/6", "", 1.0, rb.line_to(g_bk_back), hold=0.1)

    # 4: the basket through the two IPA pans and the dryer
    g_h = dwn(BASKET + (0, 0, handle[2]), 0.0)                    # fingers across the bar (along x)
    g_h_hi = g_h.copy()
    g_h_hi[2, 3] = DRYER_RIM + 30.0 + handle[2]

    def hinge_open(group, hinge, deg, axis=(0, 1, 0)):
        def up(u):
            sc.gmat[group] = T(hinge) @ R(axis, -deg * u)
        return up

    def hinge_close(group, hinge, deg, axis=(0, 1, 0)):
        def up(u):
            sc.gmat[group] = T(hinge) @ R(axis, -deg * (1 - u))
        return up

    sc.step("4/6", "The arm takes the basket by its handle.", 2.0, RB.both(rb.joint_to(Tw=g_h_hi),
                                                                         rb.grip_to(OPEN_BAR)), hold=0.0)
    sc.step("4/6", "", 1.0, rb.line_to(g_h), hold=0.0)
    sc.step("4/6", "", 0.5, rb.grip_to(GRIP_BAR), hold=0.1)
    rb.grasp("basket")
    status(Arm="UR10e: the basket")

    def into(k, secs_note, son_label, son_secs):
        px, py = PANS[k]
        g_in = dwn((px, py, PAN["rim"] - PAN["depth"] + handle[2]), 0.0)
        g_over = g_in.copy()
        g_over[2, 3] = PAN["rim"] + 30.0 + handle[2]
        sc.step("4/6", f"The {k} vessel's lid opens ...", 1.2, RB.both(rb.line_to(g_h_hi) if k == "wash" else None,
                                                                       hinge_open(f"lid_{k}", lids[k], 105.0)),
                hold=0.0)
        sc.step("4/6", f"... the basket goes into the {secs_note}, and its own cap shuts the vessel.", 2.0,
                rb.joint_to(Tw=g_over), hold=0.0)
        sc.step("4/6", "", 1.6, rb.line_to(g_in), hold=0.1)
        sc.step("4/6", "", 0.4, rb.grip_to(OPEN_BAR), hold=0.0)
        rb.release(None)
        sc.step("4/6", "", 1.0, rb.line_to(g_over), hold=0.0)
        status(Bath=son_label)
        ipa = "bath/ipa"

        def son(u):
            f = 0.5 + 0.5 * math.sin(u * 60.0)
            sc.color[ipa] = tuple(c * (0.92 + 0.08 * f) for c in IPA)
            sc.color["bath/water"] = tuple(c * (0.92 + 0.08 * f) for c in WATER)
        sc.step("4/6", f"Ultrasound, {son_secs}, through the bath's water into the shut vessel (shown sped up).", 2.5,
                son, hold=0.0, live=True)
        sc.color.pop(ipa, None)
        sc.color.pop("bath/water", None)
        sc.step("4/6", "", 1.0, rb.line_to(g_in), hold=0.0)
        sc.step("4/6", "", 0.4, rb.grip_to(GRIP_BAR), hold=0.0)
        rb.grasp("basket")
        sc.step("4/6", "", 1.6, rb.line_to(g_over), hold=0.0)
        g_off = g_over.copy()
        g_off[0, 3] += 170.0
        g_off[2, 3] += 150.0
        sc.step("4/6", "The vessel's lid shuts behind it.", 1.2, RB.both(rb.line_to(g_off),
                                                                        hinge_close(f"lid_{k}", lids[k], 105.0)),
                hold=0.0)
        return g_off

    into("wash", "first vessel of IPA", "wash vessel: 37 kHz, 5 min", "5 min")
    status(Bath="wash done; to the rinse")
    into("rinse", "second vessel, clean IPA", "rinse vessel: 37 kHz, 2 min", "2 min")
    status(Bath="IPA vessels shut")
    # the dryer
    gx, gy = DRYER
    g_d = dwn((gx, gy, BASKET[2] + handle[2]), 0.0)
    g_d_over = g_d.copy()
    g_d_over[2, 3] = DRYER_RIM + 30.0 + handle[2]
    sc.step("5/6", "Into the vacuum dryer: its lid opens ...", 1.2, hinge_open("dlid", dhinge, 105.0, (1, 0, 0)),
            hold=0.0)
    sc.step("5/6", "", 2.0, rb.joint_to(Tw=g_d_over), hold=0.0)
    sc.step("5/6", "", 1.6, rb.line_to(g_d), hold=0.1)
    sc.step("5/6", "", 0.4, rb.grip_to(OPEN_BAR), hold=0.0)
    rb.release(None)
    sc.step("5/6", "", 1.0, rb.line_to(g_d_over), hold=0.0)
    g_d_away = g_d_over.copy()
    g_d_away[:3, 3] += (380.0, 0.0, 60.0)
    sc.step("5/6", "", 1.2, rb.line_to(g_d_away), hold=0.0)
    sc.step("5/6", "", 1.0, hinge_close("dlid", dhinge, 105.0, (1, 0, 0)), hold=0.0)

    def pump(u):
        p = 1013.0 * (1 - u) + 2.0 * u if u < 0.8 else 2.0 + 1011.0 * ((u - 0.8) / 0.2)
        status(Dryer=f"45 °C, {p:6.0f} mbar" + ("  (N2 back-fill)" if u >= 0.8 else ""))
    sc.step("5/6", "Pumped down at 45 °C: the IPA in each blind bore boils off, through the condenser to the pump. "
                   "Then "
                   "back-filled with dry nitrogen (shown sped up: about 10 min).", 3.0, pump, hold=0.3, live=True)
    status(Dryer="vented, dry")
    sc.step("5/6", "", 1.2, hinge_open("dlid", dhinge, 105.0, (1, 0, 0)), hold=0.0)
    sc.step("5/6", "", 1.2, rb.line_to(g_d_over), hold=0.0)
    sc.step("5/6", "", 1.0, rb.line_to(g_d), hold=0.0)
    sc.step("5/6", "", 0.4, rb.grip_to(GRIP_BAR), hold=0.0)
    rb.grasp("basket")
    sc.step("5/6", "", 1.4, rb.line_to(g_d_over), hold=0.0)
    sc.step("5/6", "Back on its stand.", 2.0, rb.joint_to(Tw=g_h_hi), hold=0.0)
    sc.step("5/6", "", 1.4, RB.both(rb.line_to(g_h), hinge_close("dlid", dhinge, 105.0, (1, 0, 0))), hold=0.0)
    sc.step("5/6", "", 0.4, rb.grip_to(OPEN_BAR), hold=0.0)
    rb.release(None)
    sc.step("5/6", "", 1.0, rb.line_to(g_h_hi), hold=0.0)

    # 5: weigh and measure
    sc.step("6/6", "The cup, dry, to the weigh module ...", 2.0, RB.both(rb.joint_to(Tw=g_bk_back),
                                                                        rb.grip_to(OPEN_RACK)), hold=0.0,
            cam_to=CAM_EAST)
    sc.step("6/6", "", 1.0, rb.line_to(g_bk), hold=0.0)
    sc.step("6/6", "", 0.5, rb.grip_to(GRIP_CUP), hold=0.0)
    rb.grasp("cup")
    status(Arm="UR10e: the cup", Cup="dry")
    sc.step("6/6", "", 0.6, rb.line_to(T((0, 0, 8.0)) @ g_bk), hold=0.0)
    sc.step("6/6", "", 1.0, rb.line_to(g_bk_back_hi), hold=0.0)
    wd = radial(WEIGH)
    g_w = lvl(WEIGH + (0, 0, CUP_GRASP), wd)
    g_w_back = g_w.copy()
    g_w_back[:3, 3] -= np.r_[wd, 0] * 120.0

    def shield(u):
        sc.gmat["shield"] = T((0, 0, 140.0 * u))
    g_w_back_hi = T((0, 0, 8.0)) @ g_w_back
    sc.step("6/6", "", 2.2, RB.both(rb.joint_to(Tw=g_w_back_hi), shield), hold=0.0)
    sc.step("6/6", "", 1.2, rb.line_to(T((0, 0, 8.0)) @ g_w), hold=0.0)
    sc.step("6/6", "", 0.5, rb.line_to(g_w), hold=0.0)
    sc.step("6/6", "", 0.5, rb.grip_to(OPEN_CUP), hold=0.0)
    rb.release(None)
    sc.step("6/6", "", 1.0, rb.line_to(g_w_back), hold=0.0)
    cup_g = round(C.volumes()["cup"] * C.RHO[metal], 3)
    reading = f"{cup_g + 0.0007:.4f} g"

    def weigh(u):
        sc.gmat["shield"] = T((0, 0, 140.0 * (1 - u)))
        status(Weigh=("settling" if u < 0.9 else reading))
    sc.step("6/6", f"Weighed with the shield down: the empty cup's own mass ({cup_g:.2f} g by CAD for 5N Al), recorded "
                   "against its place in the rack, so the charge station doses against what the cup really weighs.",
            2.5, weigh, hold=0.8)
    status(Cup=f"{reading}")
    sc.step("6/6", "", 1.0, shield, hold=0.0)
    sc.step("6/6", "", 1.0, rb.line_to(g_w), hold=0.0)
    sc.step("6/6", "", 0.5, rb.grip_to(GRIP_CUP), hold=0.0)
    rb.grasp("cup")
    sc.step("6/6", "", 0.5, rb.line_to(T((0, 0, 8.0)) @ g_w), hold=0.0)
    sc.step("6/6", "", 1.0, rb.line_to(g_w_back_hi), hold=0.0)
    vd = radial(VISION)
    g_v = lvl(VISION + (0, 0, CUP_GRASP), vd)
    g_v_back = g_v.copy()
    g_v_back[:3, 3] -= np.r_[vd, 0] * 120.0
    sc.step("6/6", "On to the dimension gauge's stage.", 2.0, RB.both(rb.joint_to(Tw=g_v_back),
                                                                     lambda u: sc.gmat.__setitem__(
                                                                         "shield", T((0, 0, 140.0 * (1 - u))))),
            hold=0.0, cam_to=CAM_GAUGE)
    sc.step("6/6", "", 1.2, rb.line_to(T((0, 0, 2.0)) @ g_v), hold=0.0)
    sc.step("6/6", "", 0.3, rb.line_to(g_v), hold=0.0)
    sc.step("6/6", "", 0.5, rb.grip_to(OPEN_CUP), hold=0.0)
    rb.release(None)
    sc.step("6/6", "", 1.0, rb.line_to(g_v_back), hold=0.0)

    def measure(u):
        status(Gauge="measuring" if u < 0.7 else "OD 19.049  bore 12.703  rim chamfer ok")
    sc.step("6/6", "Lit from below and above, it reads the OD and the bore at the mouth: the press fit's two numbers.",
            2.0, measure, hold=0.8)
    sc.step("6/6", "", 1.0, rb.line_to(g_v), hold=0.0)
    sc.step("6/6", "", 0.5, rb.grip_to(GRIP_CUP), hold=0.0)
    rb.grasp("cup")
    sc.step("6/6", "", 1.0, rb.line_to(g_v_back), hold=0.0)
    # into the rack's front row, level from the front (as chapter 1 takes them)
    seat = RACK_AT + np.array(rk_seats["cup"][HERO])
    g_r = lvl(seat + (0, 0, CUP_GRASP), (0.0, 1.0))
    g_r_back = g_r.copy()
    g_r_back[1, 3] -= 130.0
    lift_r = C.CUP_POCKET + 6.0                                    # over the rack's top, then down into the pocket
    sc.step("6/6", "Racked: into the cassette, chapter 1's charge rack, cups in front and plugs behind.", 2.4,
            rb.joint_to(Tw=T((0, 0, lift_r)) @ g_r_back), hold=0.0, cam_to=CAM_RACK)
    sc.step("6/6", "", 1.2, rb.line_to(T((0, 0, lift_r)) @ g_r), hold=0.0)
    sc.step("6/6", "", 1.0, rb.line_to(g_r), hold=0.0)
    sc.step("6/6", "", 0.4, rb.grip_to(OPEN_RACK), hold=0.0)
    rb.release("rack")
    status(Arm="UR10e")
    sc.step("6/6", "", 1.0, rb.line_to(g_r_back), hold=0.0)
    others = [f"rcup{i}" for i in range(4) if i != HERO] + [f"rplug{i}" for i in range(4)]
    bk_others = [f"bcup{i}" for i in range(4) if i != BASKET_POCKET] + [f"bplug{i}" for i in range(4)]

    def others_go(u):
        for g in others:
            sc.show(sc.members(g), u)
        for g in bk_others:
            sc.show(sc.members(g), 1 - u)
    sc.step("6/6", "The run's other three cups and four plugs go the same way (not shown).", 1.5, others_go, hold=0.3)
    status(Basket="empty", Cup="racked: pocket 4 of 8")
    # the lid on
    lid_w = sc.world("rlid")
    g_l = dwn(lid_w[:3, 3] + (0, 0, lid_grasp), 90.0)          # the knob's 20 mm side is along y on the rest
    g_l_hi = g_l.copy()
    g_l_hi[2, 3] += 120.0
    g_on = dwn(RACK_AT + (0, 0, lid_grasp), 0.0)
    g_on_hi = g_on.copy()
    g_on_hi[2, 3] += 120.0
    sc.step("6/6", "The lid goes on.", 2.0, RB.both(rb.joint_to(Tw=g_l_hi), rb.grip_to(0.55)), hold=0.0)
    sc.step("6/6", "", 1.0, rb.line_to(g_l), hold=0.0)
    sc.step("6/6", "", 0.4, rb.grip_to(0.79), hold=0.0)
    rb.grasp("rlid")
    status(Arm="UR10e: the lid")
    sc.step("6/6", "", 1.0, rb.line_to(g_l_hi), hold=0.0)
    sc.step("6/6", "", 2.0, rb.joint_to(Tw=g_on_hi), hold=0.0)
    sc.step("6/6", "", 1.2, rb.line_to(g_on), hold=0.0)
    sc.step("6/6", "", 0.4, rb.grip_to(0.55), hold=0.0)
    rb.release("rack")
    sc.step("6/6", "", 1.0, rb.line_to(g_on_hi), hold=0.0)
    status(Arm="UR10e, parked", Cup="racked, lidded: ready for the MiR250 and tray J")
    sc.step("6/6", "One run's set, cleaned, dried, weighed, measured and racked. The MiR250's arm takes the cassette "
                   "through the front window, over the light curtain, to tray J.", 2.5,
            rb.joint_to(q1=np.radians(PARK)), hold=2.0, cam_to=CAM_WIDE, still=True)
    if os.environ.get("MCELL_STEPS"):
        for st in sc.substeps:
            print(f"{st['start_frame']:5d}-{st['end_frame']:5d} {st['label']} {st['caption'][:60]}")
    return sc.save()


def gif(fps: int = 4, width: int = 520, lossy: int = 130, colors: int = 48):
    """out/machining_cell.gif from the MP4: 4 fps, 520 px, 48 colours, gifsicle --lossy=130 (under 4.9 MB)."""
    import subprocess
    mp4, out = HERE / "out" / "mp4" / f"{NAME}.mp4", HERE / "out" / f"{NAME}.gif"
    tmp = Path("/tmp") / f"{NAME}_raw.gif"
    th = os.environ.get("FFMPEG_THREADS", "2")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", th, "-i", str(mp4), "-vf",
                    f"fps={fps},scale={width}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors={colors}[p];"
                    "[b][p]paletteuse=dither=bayer:bayer_scale=4", "-threads", th, str(tmp)], check=True)
    subprocess.run(["gifsicle", "-O3", f"--lossy={lossy}", str(tmp), "-o", str(out)], check=True)
    print(f"{out.name}: {out.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    if os.environ.get("MCELL_GIF"):
        gif()
    else:
        movie()
