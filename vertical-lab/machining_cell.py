"""The charge cups machined, cleaned, dried, weighed, measured and racked in a floor cell (byu-vcl #367, from PR #318's
review: "We should probably automate machining of the high-purity cups and plugs ... This would also need to include a
cleaning and drying step (IPA for example)").

One cup's path through the recommended cell (notes/machining.md), as a model and a clip:

1. **The lathe** (a compact bar-fed CNC turning centre with a short-bar loader, drawn at the size of the machine named
   in ``machining.LATHE``; the inside is ours) turns the cup from Ø20 mm bar: face, turn the OD to 19.05 mm, drill
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
    MCELL_STILL=lab xvfb-run -a python3 machining_cell.py   # the cell in its place on the floor -> out/machining_lab.png
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
# Body box: the Haas ST-10's installed size with its chip conveyor (3437 x 1596 x 2167 mm, Haas layout drawing 12/2024),
# the conveyor's end at -x; front face at y1. Its Bar Feeder V2 (4 ft bars; 2104 x 1283 mm) behind the headstock (+x).
LATHE = dict(x0=-1937.0, x1=1500.0, y1=-800.0, D=1596.0, H=2167.0, loader_l=2104.0, loader_w=1283.0)
SPIN_Y, SPIN_Z = -1270.0, 1050.0                                    # the spindle's axis, along x
X_COLLET = 198.0                 # the collet's face; the bar comes out towards -x
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
X_INDEX = -80.0                  # where the turret's centre goes along x to index: every tool clear of bar and headstock
BELT_X = (END + CUP_BASE_X) / 2  # 158.25: under the parted cup, and the belt's middle
BELT_Z = 880.0                   # belt top
UP_Y = -700.0                    # the upender's pivot: the lying cup's base against its end plate
BELT_Y = (-1150.0, UP_Y - 33.0)  # inside the machine -> the upender, outside the guard
NEST = np.array([BELT_X, UP_Y + CUP_R, BELT_Z])            # the cup's base centre, stood up on the upender
BLOW = np.array([-720.0, -610.0, 945.0])                   # the cup's base, lowered into the blow-off ring
BASKET = np.array([-800.0, -400.0, 1032.0])                # the basket's feet on its stand (one row along y)
# Two small ultrasonic baths (sized after Elma's Elmasonic P 60 H: 365 x 186 x 271 mm outside, 5.75 L), water in the
# tank, each with ONE closed stainless vessel of IPA hung in it: Elma's manual allows "max. 1 litre" of a flammable
# liquid, and only in a separate vessel standing in water (notes/machining.md). Each vessel holds about 0.6 L.
PANS = {"wash": np.array([-905.0, -20.0]), "rinse": np.array([-705.0, -20.0])}
PAN = dict(ix=46.0, iy=196.0, depth=125.0, rim=1157.0, wall=2.0, ipa=76.0)
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
BASKET_POCKET = 0                                          # its pocket in the basket

CUP_GRASP = 50.0                 # grasp point over a cup's base (chapter 1: 45; here 50, so the pads clear the upender's
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
def lathe_parts() -> dict:
    """{name: (mesh, colour, opacity)} of the turning centre's body, cell frame. Its front (the door) faces +y, the
    headstock is at +x, the short-bar loader behind it; the chip conveyor leaves at the back into one bin per metal."""
    x0, x1, y1, D, H = LATHE["x0"], LATHE["x1"], LATHE["y1"], LATHE["D"], LATHE["H"]
    y0 = y1 - D
    t = 20.0
    door = dict(x0=-620.0, x1=520.0, z0=930.0, z1=1800.0)
    slot = dict(x0=100.0, x1=215.0, z0=855.0, z1=915.0)        # the belt's way out under the door
    body = [
        _box(x0, x1, y0, y0 + t, 0, H),                      # back
        _box(x0, x0 + t, y0, y1, 0, H), _box(x1 - t, x1, y0, y1, 0, H),      # sides
        _box(x0, x1, y0, y1, H - t, H),                      # roof
        _box(x0, door["x0"], y1 - t, y1, 0, H - t), _box(door["x1"], x1, y1 - t, y1, 0, H - t),   # front, beside
        _box(door["x0"], door["x1"], y1 - t, y1, door["z1"], H - t),       # over the door
        _box(door["x0"], slot["x0"], y1 - t, y1, 0, door["z0"]), _box(slot["x1"], door["x1"], y1 - t, y1, 0, door["z0"]),
        _box(slot["x0"], slot["x1"], y1 - t, y1, 0, slot["z0"]), _box(slot["x0"], slot["x1"], y1 - t, y1, slot["z1"],
                                                                      door["z0"]),
    ]
    trim = [_box(x0 - 5, x1 + 5, y0 - 5, y1 + 5, 0, 90),      # plinth
            _box(x0, x1, y1 - t - 2, y1 + 2, H - 140, H - t)]           # the header band
    # the door: frame and window, slid shut; the control pendant on the right; a work light inside
    df = [_box(door["x0"], door["x1"], y1, y1 + 30, door["z0"], door["z0"] + 70),
          _box(door["x0"], door["x1"], y1, y1 + 30, door["z1"] - 60, door["z1"]),
          _box(door["x0"], door["x0"] + 60, y1, y1 + 30, door["z0"], door["z1"]),
          _box(door["x1"] - 60, door["x1"], y1, y1 + 30, door["z0"], door["z1"]),
          _box(door["x1"] - 50, door["x1"] - 30, y1 + 30, y1 + 60, 1150, 1500)]           # the handle
    glass = _box(door["x0"] + 60, door["x1"] - 60, y1 + 10, y1 + 18, door["z0"] + 70, door["z1"] - 60)
    pendant = _merge([_box(820, 1240, y1, y1 + 90, 1150, 1750), _box(850, 1210, y1 + 90, y1 + 92, 1430, 1720)])
    # inside: the chip pan sloping back, the slant bed, the headstock, the collet nose
    pan = _merge([_box(-1000, x1 - t, y0 + t, y1 - t, 640, 660)])
    # the slant bed behind the turret's reach (620-700 mm from the axis along the slant), on a base casting
    n = np.array([0.0, -TURRET_U[2], TURRET_U[1]])
    Mb = np.eye(4)
    Mb[:3, 0], Mb[:3, 1], Mb[:3, 2] = (1, 0, 0), n, -TURRET_U
    Mb[:3, 3] = (0, SPIN_Y, SPIN_Z)
    slant = _box(-800, 700, -330, 330, 620, 700).transform(Mb, inplace=False)
    bed = _box(-800, 700, -2430, -1660, 90, 1240)
    head = _box(260, 760, SPIN_Y - 260, SPIN_Y + 250, 760, 1340)
    nose = _cyl((240, SPIN_Y, SPIN_Z), (262, SPIN_Y, SPIN_Z), 95.0, res=64)
    # the belt: a short narrow conveyor along y, from under the spindle out through the slot to the upender (ours)
    belt = _box(BELT_X - 20, BELT_X + 20, BELT_Y[0], BELT_Y[1], BELT_Z - 22, BELT_Z)
    belt_frame = _merge([_box(BELT_X - 26, BELT_X - 20, BELT_Y[0] - 10, BELT_Y[1] + 2, BELT_Z - 40, BELT_Z + 4),
                         _box(BELT_X + 20, BELT_X + 26, BELT_Y[0] - 10, BELT_Y[1] + 2, BELT_Z - 40, BELT_Z + 4),
                         _box(BELT_X - 20, BELT_X + 20, BELT_Y[1] - 80, BELT_Y[1] - 60, 660, BELT_Z - 40),
                         _box(BELT_X - 20, BELT_X + 20, BELT_Y[0] + 20, BELT_Y[0] + 40, 660, BELT_Z - 40),
                         # the upender's stand and its rotary actuator, beside the pivot
                         _box(BELT_X - 30, BELT_X + 30, UP_Y - 40, UP_Y + 25, 520, BELT_Z - 30),
                         _box(BELT_X + 22, BELT_X + 52, UP_Y - 18, UP_Y + 18, BELT_Z - 40, BELT_Z + 4)])
    # the short-bar loader behind the headstock (sized by machining.LATHE), bars on its sloping magazine
    lx0, lx1, lw = x1, x1 + LATHE["loader_l"], LATHE["loader_w"]
    loader = [_box(lx0, lx1, SPIN_Y - lw / 2, SPIN_Y + lw / 2, 90, 900), _box(lx0 + 60, lx1 - 60, SPIN_Y - 300,
                                                                            SPIN_Y + 300, 900, 1000)]
    bars = []
    for k in range(6):
        y = SPIN_Y - 250 + 42 * k
        bars.append(_cyl((lx0 + 120, y, 1000 + BAR_R + 6 * k / 5), (lx0 + 120 + 1000, y, 1000 + BAR_R + 6 * k / 5),
                         BAR_R, res=24))
    feed = _cyl((x1 - 10, SPIN_Y, SPIN_Z), (lx0 + 120, SPIN_Y, SPIN_Z), 45.0, res=32)
    # the chip conveyor out of the back into the bin of the metal being cut, and the other metal's bin beside it
    # the chip conveyor (inside the body's -x end) lifts the chips into the bin of the metal being cut; the other
    # metal's bin waits beside it, so Al and Cu chips never share a bin
    conv = _box(x0 + 40, -1050, SPIN_Y - 250, SPIN_Y + 250, 700, 1250).rotate_y(0, inplace=False)
    bin_al = _open_box(x0 + 60, x0 + 560, y1 + 60, y1 + 560, 0, 650, 6)
    bin_cu = _open_box(x0 + 620, x0 + 1120, y1 + 60, y1 + 560, 0, 650, 6)
    # the alcohol MQL unit on the body's front left, its line into the work zone (drawn to the panel)
    mql = _merge([_box(-1000, -760, y1, y1 + 160, 1300, 1620), _cyl((-880, y1 + 80, 1620), (-880, y1 + 80, 1720),
                                                                    35.0, res=24)])
    return {
        "lathe/skin": (_merge(body), SHEET, 1.0),
        "lathe/trim": (_merge(trim + [pendant]), TRIM, 1.0),
        "lathe/door": (_merge(df), (0.30, 0.31, 0.34), 1.0),
        "lathe/glass": (glass, GLASS, 0.18),
        "lathe/pan": (pan, (0.45, 0.46, 0.48), 1.0),
        "lathe/bed": (_merge([bed, slant]), (0.36, 0.37, 0.40), 1.0),
        "lathe/head": (_merge([head, nose]), (0.52, 0.53, 0.56), 1.0),
        "lathe/belt": (belt, DARK, 1.0),
        "lathe/beltframe": (belt_frame, STEEL, 1.0),
        "lathe/loader": (_merge(loader + [feed]), SHEET, 1.0),
        "lathe/bars": (_merge(bars), AL, 1.0),
        "lathe/conveyor": (conv, TRIM, 1.0),
        "lathe/bin_al": (bin_al, (0.25, 0.45, 0.85), 1.0),
        "lathe/bin_cu": (bin_cu, (0.85, 0.45, 0.20), 1.0),
        "lathe/mql": (mql, (0.20, 0.36, 0.62), 1.0),
    }


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
    """A frame with z along u (radial), y along n, x along the spindle's axis, at `origin` (turret frame)."""
    M = np.eye(4)
    M[:3, 0] = np.cross(n, u)
    M[:3, 1] = n
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
    tray = _open_box(-40, 34, -22, 22, -3, 6, 3)
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
    fx, fy = 40.0, 190.0
    ys, yp = [-60.0, -20.0, 20.0, 60.0], [-40.0, 0.0, 40.0, 80.0]
    feet = [_box(-fx / 2, fx / 2, -fy / 2, -fy / 2 + 10, 0, 4), _box(-fx / 2, fx / 2, fy / 2 - 10, fy / 2, 0, 4)]
    floor = _box(-fx / 2, fx / 2, -fy / 2, fy / 2, 4, 8)
    rims = [_ring(C.STOCK_D / 2 + 3.0, C.STOCK_D / 2 + 0.8, 8, 13).translate((0, y, 0), inplace=False) for y in ys]
    rims += [_ring(C.CUP_BORE_D / 2 + 2.5, C.CUP_BORE_D / 2 + 0.6, 8, 11).translate((0, y, 0), inplace=False)
             for y in yp]
    posts = [_box(-4, 4, s_ * 99 - 4, s_ * 99 + 4, 8, BASKET_CAP) for s_ in (-1, 1)]
    cap = _box(-33, 33, -108, 108, BASKET_CAP, BASKET_CAP + 4)
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
    hood = _merge([_box(x0 - 70, x0 - 10, -230, 190, BENCH_Z, TANK["top"] + 260),
                   _box(x0 - 70, x0 - 50, -210, 170, TANK["top"] + 40, TANK["top"] + 230),
                   _cyl((x0 - 40, -20, TANK["top"] + 260), (x0 - 40, -20, 2700), 75.0, res=32)])
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
    x, y = DRYER
    disc = C.lathe([(0, 0), (DRYER_R + 14, 0), (DRYER_R + 14, 14), (0, 14)], res=64).translate(
        (DRYER_R + 14, 0, 0), inplace=False)
    knob = _box(2 * DRYER_R + 8, 2 * DRYER_R + 40, -30, 30, 0, 30)
    win = _cyl((DRYER_R + 14, 0, 14), (DRYER_R + 14, 0, 16), 70.0, res=48)
    return _merge([disc, knob, win]), np.array([x - DRYER_R - 14, y, DRYER_RIM])


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
    w = C.RACK_COLS * C.RACK_PITCH + 16
    d, h0, h1, t = 80.0, C.RACK_H, C.RACK_H + 52.0, 3.0
    shell = _merge([_box(-w / 2 - t, w / 2 + t, -d / 2 - t, d / 2 + t, h1 - t, h1),
                    _box(-w / 2 - t, -w / 2, -d / 2 - t, d / 2 + t, h0 - 12, h1), _box(w / 2, w / 2 + t, -d / 2 - t,
                                                                                      d / 2 + t, h0 - 12, h1),
                    _box(-w / 2 - t, w / 2 + t, -d / 2 - t, -d / 2, h0 - 12, h1), _box(-w / 2 - t, w / 2 + t, d / 2,
                                                                                      d / 2 + t, h0 - 12, h1)])
    knob = _box(-10, 10, -18, 18, h1, h1 + 24)
    return _merge([shell, knob]), h1 + 14.0


def bench_parts() -> dict:
    """The three benches round the arm, its pedestal, the fence (the front open over the north bench, behind a light
    curtain, for the MiR's arm), and the floor."""
    tops, legs = [], []
    for (x0, x1, y0, y1) in ((-1150, -600, -700, 760), (550, 1150, -700, 760), (-600, 550, 620, 940)):
        tops.append(_box(x0, x1, y0, y1, BENCH_Z - 30, BENCH_Z))
        for (lx, ly) in ((x0 + 40, y0 + 40), (x1 - 40, y0 + 40), (x0 + 40, y1 - 40), (x1 - 40, y1 - 40)):
            legs.append(_box(lx - 25, lx + 25, ly - 25, ly + 25, 0, BENCH_Z - 30))
    ped = _merge([_box(-130, 130, -130, 130, 0, Z_ARM - 15), _box(-300, 300, -300, 300, 0, 20),
                  _box(-140, 140, -140, 140, Z_ARM - 15, Z_ARM)])
    stand = _box(BASKET[0] - 30, BASKET[0] + 30, BASKET[1] - 105, BASKET[1] + 105, BENCH_Z, BASKET[2])
    riser = _box(RACK_AT[0] - 185, RACK_AT[0] + 185, RACK_AT[1] - 50, RACK_AT[1] + 50, BENCH_Z, RACK_AT[2])
    rest = _box(LID_REST[0] - 50, LID_REST[0] + 50, LID_REST[1] - 185, LID_REST[1] + 185, BENCH_Z, BENCH_Z + 8)
    blow = BLOW
    blow_m = _merge([_box(blow[0] - 70, blow[0] + 70, blow[1] - 45, blow[1] + 45, BENCH_Z, BENCH_Z + 10),
                     _cyl((blow[0] - 60, blow[1], BENCH_Z + 10), (blow[0] - 60, blow[1], blow[2] + 130), 9.0, res=16),
                     _cyl((blow[0] - 60, blow[1], blow[2] + 130), (blow[0] - 12, blow[1], blow[2] + 130), 5.0, res=12),
                     _cyl((blow[0], blow[1], blow[2] + 130), (blow[0], blow[1], blow[2] + 95), 3.0, res=12),
                     _cyl((blow[0] - 12, blow[1], blow[2] + 130), (blow[0], blow[1], blow[2] + 130), 4.0, res=12),
                     _cyl((blow[0] - 60, blow[1], blow[2] + 20), (blow[0] - 30, blow[1], blow[2] + 20), 6.0, res=12)])
    ring = _ring(C.STOCK_D / 2 + 14, C.STOCK_D / 2 + 6, blow[2] + 12, blow[2] + 26).translate(
        (blow[0], blow[1], 0), inplace=False)
    sock = _open_box(blow[0] - 45, blow[0] + 45, blow[1] - 40, blow[1] + 40, BENCH_Z + 10, blow[2] - 4, 3)
    posts, rails, mesh = [], [], []
    fx0, fx1, fy0, fy1, fh = -1250.0, 1250.0, LATHE["y1"] + 10, FRONT_Y, 1400.0
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
            "bench/blow": (_merge([blow_m, sock]), (0.36, 0.37, 0.40), 1.0), "bench/ring": (ring, (0.20, 0.55, 0.85), 1.0),
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


# ------------------------------------------------------------------------------------------------ the clip
def movie():
    metal = os.environ.get("MCELL_METAL", "Al")
    col = AL if metal == "Al" else CU_C
    sc = Scene(NAME, TITLE)
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
    CAM_LATHE = [(430, -470, 1300), (150, -1020, 950), (0, 0, 1)]
    CAM_WORK = [(150, -765, 1120), (162, -1270, 1050), (0, 0, 1)]
    CAM_NEST = [(-560, 200, 1550), (150, -660, 950), (0, 0, 1)]
    CAM_BATH = [(-200, 1350, 2350), (-800, -150, 1050), (0, 0, 1)]
    CAM_EAST = [(1950, -1150, 1800), (700, -80, 1000), (0, 0, 1)]
    CAM_RACK = [(-1500, 1500, 1650), (0, 720, 960), (0, 0, 1)]
    sc.cam = CAM_WIDE

    # 1: the cell
    sc.step("1/6", "The charge-cup cell on the lab floor: a bar-fed CNC lathe, a UR10e on a pedestal, an ultrasonic "
                   "bath with two closed IPA pans, a vacuum dryer, a weigh module, a dimension gauge and the cup rack "
                   "the MiR250 takes to tray J.", 3.0, hold=1.5,
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
            W["turned"] = 65.0 * v
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
        P4 = turret_pose(tool, END - 30.0, r)[0][:3, 3] if tool in (2, 3) else turret_pose(tool, x_tip, r + 50.0)[0][:3, 3]
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
        tur(4, GROOVE_X + 120 * u, CUP_R + 40.0 + 60 * u)
    sc.step("3/6", "The catcher brings it down to the belt, turning it to lie along the belt, base first ...", 2.0,
            to_belt, hold=0.1, cam_to=CAM_LATHE, view_angle_to=30.0)
    Wc = sc.world("cup")
    sc.parent.pop("cup")
    sc.gmat["cup"] = Wc
    on_belt = T((0, 70.0, BELT_Z + CUP_R - Wc[2, 3])) @ Wc

    def tip(u):                          # over the tray's low side wall and down onto the belt
        lift = 9.0 * math.sin(math.pi * min(1.0, u * 1.25))
        sc.gmat["cup"] = T((0, 70.0 * u, (BELT_Z + CUP_R - Wc[2, 3]) * u + lift)) @ Wc
        if u > 0.6:
            sc.gmat["catcher"] = T(CATCH_BELT + (CATCH_PARK - CATCH_BELT) * ((u - 0.6) / 0.4)) @ R(
                (0, 0, 1), 90.0 * (1 - (u - 0.6) / 0.4))
    sc.step("3/6", "... and tips it out onto the belt.", 1.0, tip, hold=0.1)
    sc.gmat["catcher"] = T(CATCH_PARK)
    for name, (m, c, op) in upender_parts().items():
        sc.add(name, m, c, "upender", opacity=op)
    sc.gmat["upender"] = upender_pose(0.0)
    sc.show(["cup/cut"], 0.0)
    sc.show(["cup/whole"], 1.0)
    run = (UP_Y - CUP_L) - (on_belt @ np.array([0, 0, CUP_L, 1.0]))[1]      # the mouth's end to UP_Y - 63.5

    def belt(u):
        sc.gmat["cup"] = T((0, run * u, 0)) @ on_belt
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
    g_blow_hi[2, 3] += 120.0
    sc.step("3/6", "To the blow-off station: ...", 2.0, rb.joint_to(Tw=g_blow_hi), hold=0.0, cam_to=CAM_BATH)
    sc.step("3/6", "... a ring nozzle round its foot and a lance into the bore blow the chips off it.",
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
    g_bk_back_hi[2, 3] += 6.0
    sc.step("4/6", "Into the basket, the fourth cup of the run's set.", 2.0, rb.joint_to(Tw=g_bk_back_hi), hold=0.0)
    sc.step("4/6", "", 1.2, rb.line_to(g_bk @ T((0, 0, 0)) if False else T((0, 0, 6.0)) @ g_bk), hold=0.0)
    sc.step("4/6", "", 0.4, rb.line_to(g_bk), hold=0.1)
    sc.step("4/6", "", 0.5, rb.grip_to(OPEN_CUP), hold=0.1)
    rb.release("basket")
    status(Arm="UR10e", Basket="4 of 4 cups, 4 of 4 plugs", Cup="in the basket")
    sc.step("4/6", "", 1.0, rb.line_to(g_bk_back), hold=0.1)

    # 4: the basket through the two IPA pans and the dryer
    g_h = dwn(BASKET + (0, 0, handle[2]), 0.0)                    # fingers across the bar (along x)
    g_h_hi = g_h.copy()
    g_h_hi[2, 3] = DRYER_RIM + 30.0 + handle[2]

    def hinge_open(group, hinge, deg):
        def up(u):
            sc.gmat[group] = T(hinge) @ R((0, 1, 0), -deg * u)
        return up

    def hinge_close(group, hinge, deg):
        def up(u):
            sc.gmat[group] = T(hinge) @ R((0, 1, 0), -deg * (1 - u))
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
        sc.step("4/6", "", 1.6, rb.line_to(g_over), hold=0.2)
        sc.step("4/6", "The vessel's lid shuts behind it.", 1.0, hinge_close(f"lid_{k}", lids[k], 105.0), hold=0.0)
        return g_over

    into("wash", "first vessel of IPA", "wash vessel: 37 kHz, 5 min", "5 min")
    status(Bath="wash done; to the rinse")
    into("rinse", "second vessel, clean IPA", "rinse vessel: 37 kHz, 2 min", "2 min")
    status(Bath="IPA vessels shut")
    # the dryer
    gx, gy = DRYER
    g_d = dwn((gx, gy, BASKET[2] + handle[2]), 0.0)
    g_d_over = g_d.copy()
    g_d_over[2, 3] = DRYER_RIM + 30.0 + handle[2]
    sc.step("5/6", "Into the vacuum dryer: its lid opens ...", 1.2, hinge_open("dlid", dhinge, 110.0), hold=0.0)
    sc.step("5/6", "", 2.0, rb.joint_to(Tw=g_d_over), hold=0.0)
    sc.step("5/6", "", 1.6, rb.line_to(g_d), hold=0.1)
    sc.step("5/6", "", 0.4, rb.grip_to(OPEN_BAR), hold=0.0)
    rb.release(None)
    sc.step("5/6", "", 1.0, rb.line_to(g_d_over), hold=0.0)
    sc.step("5/6", "", 1.0, hinge_close("dlid", dhinge, 110.0), hold=0.0)

    def pump(u):
        p = 1013.0 * (1 - u) + 2.0 * u if u < 0.8 else 2.0 + 1011.0 * ((u - 0.8) / 0.2)
        status(Dryer=f"45 °C, {p:6.0f} mbar" + ("  (N2 back-fill)" if u >= 0.8 else ""))
    sc.step("5/6", "Pumped down at 45 °C: the IPA in each blind bore boils off, through the condenser to the pump. Then "
                   "back-filled with dry nitrogen (shown sped up: about 10 min).", 3.0, pump, hold=0.3, live=True)
    status(Dryer="vented, dry")
    sc.step("5/6", "", 1.2, hinge_open("dlid", dhinge, 110.0), hold=0.0)
    sc.step("5/6", "", 1.0, rb.line_to(g_d), hold=0.0)
    sc.step("5/6", "", 0.4, rb.grip_to(GRIP_BAR), hold=0.0)
    rb.grasp("basket")
    sc.step("5/6", "", 1.4, rb.line_to(g_d_over), hold=0.0)
    sc.step("5/6", "Back on its stand.", 2.0, RB.both(rb.joint_to(Tw=g_h_hi), hinge_close("dlid", dhinge, 110.0)),
            hold=0.0)
    sc.step("5/6", "", 1.4, rb.line_to(g_h), hold=0.0)
    sc.step("5/6", "", 0.4, rb.grip_to(OPEN_BAR), hold=0.0)
    rb.release(None)
    sc.step("5/6", "", 1.0, rb.line_to(g_h_hi), hold=0.0)

    # 5: weigh and measure
    sc.step("6/6", "The cup, dry, to the weigh module ...", 2.0, RB.both(rb.joint_to(Tw=g_bk_back),
                                                                        rb.grip_to(OPEN_CUP)), hold=0.0,
            cam_to=CAM_EAST)
    sc.step("6/6", "", 1.0, rb.line_to(g_bk), hold=0.0)
    sc.step("6/6", "", 0.5, rb.grip_to(GRIP_CUP), hold=0.0)
    rb.grasp("cup")
    status(Arm="UR10e: the cup", Cup="dry")
    sc.step("6/6", "", 1.0, rb.line_to(T((0, 0, 6.0)) @ g_bk), hold=0.0)
    sc.step("6/6", "", 1.0, rb.line_to(g_bk_back_hi), hold=0.0)
    wd = radial(WEIGH)
    g_w = lvl(WEIGH + (0, 0, CUP_GRASP), wd)
    g_w_back = g_w.copy()
    g_w_back[:3, 3] -= np.r_[wd, 0] * 120.0

    def shield(u):
        sc.gmat["shield"] = T((0, 0, 140.0 * u))
    sc.step("6/6", "", 2.2, RB.both(rb.joint_to(Tw=g_w_back), shield), hold=0.0)
    sc.step("6/6", "", 1.2, rb.line_to(g_w), hold=0.0)
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
    sc.step("6/6", "", 1.0, rb.line_to(g_w_back), hold=0.0)
    vd = radial(VISION)
    g_v = lvl(VISION + (0, 0, CUP_GRASP), vd)
    g_v_back = g_v.copy()
    g_v_back[:3, 3] -= np.r_[vd, 0] * 120.0
    sc.step("6/6", "On to the dimension gauge's stage.", 2.0, RB.both(rb.joint_to(Tw=g_v_back),
                                                                     lambda u: sc.gmat.__setitem__(
                                                                         "shield", T((0, 0, 140.0 * (1 - u))))),
            hold=0.0)
    sc.step("6/6", "", 1.2, rb.line_to(g_v), hold=0.0)
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
    sc.step("6/6", "Racked: into the cassette, chapter 1's charge rack, cups in front and plugs behind.", 2.4,
            rb.joint_to(Tw=g_r_back), hold=0.0, cam_to=CAM_RACK)
    sc.step("6/6", "", 1.2, RB.both(rb.line_to(g_r), rb.grip_to(OPEN_RACK)), hold=0.0)
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
    return sc.save()


if __name__ == "__main__":
    movie()
