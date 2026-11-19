"""The tools and fixtures for changing the crucible (PR #353, #303): all ours, drawn from pyvista primitives.

Every tool is held by the 2F-85 by a handle 28 mm thick (pads 28 mm apart: closure GRIP_TOOL), like chapter 2's
loading tong (alloy_atomize.add_tong). Each lives in a holder on a MiR250's cabinet top. Frames: z up the tool's axis,
origin at its working point; the handle's grasp point at HANDLE[name] along z (the key's is off-axis, KEY_GRASP).

    CG  crucible gripper: a top plate over the rim and three soft jaws (4 mm aluminium, 2 mm silicone) that close
        1.5 mm on the crucible's outside, the top 38 mm (the 2F-85's squeeze drives them through a wedge, as the tong's
        jaws). The jaws stay inside r 46, 14 mm off the coil (inner r 60).
    NT  needle tool for the insulation: four needle heads (Schmalz SNG-M 4 0.8, 10.01.29.00001: four 0.8 mm needles,
        3 mm stroke, 30 deg, 4-6 bar) on a hub at r 54.5, so they land on all three pieces' top faces (top ring
        r 50-98, side tube r 38-59, bottom ring r 16-59). The hub and heads stay inside r 59, 1 mm off the coil.
    TW  tweezers for the nozzle: two thin jaws that close 2 mm each when the 2F-85 squeezes the handle's halves.
    KEY nut key for arm 2: a 500 mm bar through the chamber's door, a gear head under the nut, a turning socket with six
        pins for the nut's six notches and a cup (rim 3 mm over the nut) that keeps the nut and the lower seal
        captive. A small gearmotor in the bar turns the socket through a bevel pair (ours: to choose).
    fixtures on MiR 1: the crucible cradle (a soft seat, a well for the holder's shank, a backlight under the nozzle),
        seats for the three insulation pieces, a rod holder, a thermocouple stand, a pin tray, the holder fixture
        (soft jaws on the shank) and a nozzle tray with a backlight.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pyvista as pv

import charge as C
from scene import R, T

ALU = (0.74, 0.76, 0.79)
DARK = (0.22, 0.23, 0.26)
SILICONE = (0.90, 0.48, 0.16)        # orange silicone pads
PEEK = (0.80, 0.72, 0.55)
STEEL = (0.62, 0.64, 0.68)
FIX = (0.30, 0.32, 0.36)             # fixtures: dark grey, as the MiR's container cradle
MARK = (0.98, 0.80, 0.10)            # a yellow stripe, so turning shows
LIGHT = (1.0, 0.98, 0.85)

HANDLE_T = 28.0                      # the handle's thickness across the pads (mm)
GRIP_TOOL = 0.70                     # ur_arm.gripper_fk: pads 28.1 mm apart
CAB_TOP = float(os.environ.get("CRUCIBLE_CAB_TOP", "800"))   # props.mir250: the cabinet spans z 300-800 (its
                                     # 20 mm plate included); the first atom_crucible_in render used 780, 20 mm
                                     # into it, which is what the audit's "in amr 12 mm" hits were: =780 repeats it

# ----------------------------------------------------------------------------------------------- the crucible
CR_R = 37.65                         # the crucible's outside radius (model.py: CRUCIBLE_ID / 2 + CRUCIBLE_WALL)
CG_JAW_OPEN = 1.5                    # mm each jaw opens
CG_JAW_DZ = (-38.0, 6.0)             # the jaws' span, from the rim plane
CG_HANDLE = 82.0
NT_HANDLE = 195.0
TW_HANDLE = 170.0
NT_R = 54.5                          # the needle heads' radius
KEY_GRASP = np.array([500.0, 0.0, 10.0])   # the key's handle centre, key frame (x from the socket to the handle):
                                           # 500 mm out, so arm 2's wrist stays left of the open lid (x -375..-152)


def cyl(c, d, r, h, res=40):
    c = np.asarray(c, float)
    d = np.asarray(d, float) / np.linalg.norm(d)
    return pv.Cylinder(center=tuple(c + d * h / 2), direction=tuple(d), radius=r, height=h, resolution=res).triangulate()


def box(x0, x1, y0, y1, z0, z1):
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1)).triangulate()


def tube(r0, r1, z0, z1, res=64):
    return C.lathe([(r0, z0), (r1, z0), (r1, z1), (r0, z1)], res=res)


def handle(h, w=40.0, t=HANDLE_T, tall=40.0):
    """A handle block centred at height h: t thick along x (the pads' closing line), w wide along y."""
    return box(-t / 2, t / 2, -w / 2, w / 2, h - tall / 2, h + tall / 2)


# ----------------------------------------------------------------------------------------------- tools
def cg_meshes() -> dict:
    """{name: (mesh, colour, part)}; part "body" or "jaw<k>" (each jaw its own group, sliding radially)."""
    out = {"cg plate": (cyl((0, 0, 6), (0, 0, 1), 47.0, 8.0, 64), ALU, "body"),
           "cg mark": (box(30.0, 46.0, -2.0, 2.0, 14.0, 14.8), MARK, "body"),
           "cg stem": (cyl((0, 0, 14), (0, 0, 1), 9.0, CG_HANDLE - 20 - 14), ALU, "body"),
           "cg handle": (handle(CG_HANDLE), DARK, "body")}
    for k in range(3):
        a = 90.0 + 120.0 * k
        jaw = box(CR_R + 2.0, CR_R + 6.0, -13.0, 13.0, CG_JAW_DZ[0], CG_JAW_DZ[1])
        pad = box(CR_R, CR_R + 2.0, -12.0, 12.0, CG_JAW_DZ[0] + 1, CG_JAW_DZ[1] - 6)
        rot = R((0, 0, 1), a)
        out[f"cg jaw{k}"] = (jaw.transform(rot, inplace=False), ALU, f"jaw{k}")
        out[f"cg pad{k}"] = (pad.transform(rot, inplace=False), SILICONE, f"jaw{k}")
    return out


def cg_jaw_dirs():
    return [np.array([math.cos(math.radians(90.0 + 120.0 * k)), math.sin(math.radians(90.0 + 120.0 * k)), 0.0])
            for k in range(3)]


def nt_meshes() -> dict:
    out = {"nt hub": (cyl((0, 0, 10), (0, 0, 1), 58.0, 8.0, 64), ALU, "body"),
           "nt stem": (cyl((0, 0, 18), (0, 0, 1), 8.0, NT_HANDLE - 20 - 18), ALU, "body"),
           "nt handle": (handle(NT_HANDLE), DARK, "body")}
    for k in range(4):
        a = math.radians(45.0 + 90.0 * k)
        c = (NT_R * math.cos(a), NT_R * math.sin(a), 0.0)
        out[f"nt head{k}"] = (cyl(c, (0, 0, 1), 4.5, 10.0, 24), DARK, "body")
        for s in (-1, 1):                                    # two needles per head, out at 30 deg (shown engaged)
            t = np.array([-math.sin(a), math.cos(a), 0.0]) * s
            p0 = np.array(c) + t * 1.5
            d = t * math.sin(math.radians(30)) - np.array([0, 0, 1.0]) * math.cos(math.radians(30))
            out[f"nt needle{k}{'ab'[s > 0]}"] = (cyl(p0, d, 0.45, 4.0, 8), STEEL, "needles")
    return out


def tw_meshes() -> dict:
    out = {"tw bridge": (box(-14.0, 14.0, -4.0, 4.0, 50.0, 56.0), STEEL, "body"),
           "tw stem": (box(-3.0, 3.0, -4.0, 4.0, 56.0, TW_HANDLE - 20), STEEL, "body"),
           "tw handle": (handle(TW_HANDLE), DARK, "body")}
    for s, part in ((-1, "jaw_a"), (1, "jaw_b")):
        out[f"tw {part}"] = (box(s * 8.0 - (1.5 if s < 0 else 0.0), s * 8.0 + (0.0 if s < 0 else 1.5), -3.0, 3.0,
                                 0.0, 52.0), STEEL, part)
        out[f"tw tip {part}"] = (box(s * 8.0 - (0.6 if s < 0 else 0.0), s * 8.0 + (0.0 if s < 0 else 0.6), -2.5, 2.5,
                                     0.5, 6.0), PEEK, part)
    return out


def key_meshes() -> dict:
    """The nut key, key frame: origin on the socket's axis at the cup floor's top (the nut's bottom face), z up, x from
    the socket to the handle. Parts: body (bar, gear head, motor, handle) and sock (floor, cup wall, six pins, mark)."""
    out = {"key head": (cyl((0, 0, -30), (0, 0, 1), 22.0, 25.0, 48), DARK, "body"),
           "key bar": (box(16.0, 514.0, -12.0, 12.0, -28.0, -10.0), ALU, "body"),
           "key motor": (cyl((190, 0, -19), (1, 0, 0), 13.0, 70.0, 32), DARK, "body"),
           "key handle": (box(480.0, 520.0, -HANDLE_T / 2, HANDLE_T / 2, -10.0, 30.0), DARK, "body")}
    floor = C.lathe([(13.0, -5.0), (37.0, -5.0), (37.0, 0.0), (13.0, 0.0)], res=64)
    wall = tube(31.0, 36.0, 0.0, 15.0)
    out["key floor"] = (floor, ALU, "sock")
    out["key cup"] = (wall, ALU, "sock")
    out["key mark"] = (box(35.5, 36.8, -2.0, 2.0, 2.0, 14.0), MARK, "sock")
    for k in range(6):
        a = math.radians(30.0 + 60.0 * k)
        out[f"key pin{k}"] = (cyl((30.0 * math.cos(a), 30.0 * math.sin(a), 0.0), (0, 0, 1), 2.6, 10.0, 16), STEEL,
                              "sock")
    return out


# ----------------------------------------------------------------------------------------------- the pin
PIN_Y = (-16.0, 14.0)                # the safety pin's shaft, along y through the lever's eye (model frame, ours)
PIN_GRIP_Y = -24.0                   # its T-handle's centre


def pin_meshes(z_arm: float) -> dict:
    """The lever's safety pin (ours: the model implies it, T4 2:02-2:08 shows it pulled and pushed): a 3.2 mm shaft
    through the eye and the adapter's stub, an 8 mm T-handle at the front end. Model frame (it rides the lever)."""
    return {"crucible pin shaft": (cyl((0, PIN_Y[0], z_arm), (0, 1, 0), 1.6, PIN_Y[1] - PIN_Y[0], 16), STEEL),
            "crucible pin grip": (cyl((0.0, PIN_GRIP_Y, z_arm), (1, 0, 0), 4.0, 14.0, 24), (0.85, 0.12, 0.10)),
            "crucible pin web": (box(-2.0, 2.0, PIN_GRIP_Y, PIN_Y[0] + 0.5, z_arm - 1.6, z_arm + 1.6), STEEL)}


# ----------------------------------------------------------------------------------------------- fixtures
# MiR-local positions (x, y) on MiR 1's cabinet top (the arm's base is at (0, 130)) and the heights things sit at
LAY1 = dict(rod=(-330.0, 130.0), tc=(-300.0, -45.0), cradle=(-200.0, -155.0), cg=(342.0, 57.0),
            fixture=(73.0, -212.0), nozzle=(185.0, -167.0), nt=(287.0, -71.0), tw=(-60.0, -215.0),
            pin=(345.0, 191.0))
# every fixture on its own bearing from the arm's base, ~350 mm out, so the upper arm reaching one passes no other
# the insulation's seats are on a small parts table beside the machine (model frame), not on the MiR
TABLE = dict(x=(240.0, 800.0), y=(-450.0, -190.0), z=850.0)
SEATS_T = dict(top_ring=(350.0, -320.0), side_tube=(530.0, -320.0), bottom_ring=(690.0, -320.0))
SEAT_Z = TABLE["z"] + 5.0            # the insulation seats' top (on the parts table, model frame)
CRADLE_Z = CAB_TOP + 95.0            # the crucible's base in the cradle
CG_Z = CAB_TOP + 45.0                # the crucible gripper's frame on its stand
NT_Z = CAB_TOP + 25.0
TW_Z = CAB_TOP + 8.0
ROD_Z = CAB_TOP + 10.0               # the rod's ball bottom in its holder
TC_Z = CAB_TOP + 5.0                 # the thermocouple's tip in its stand
FIX_TOP = CAB_TOP + 65.0             # the holder fixture's top: the holder's shoulder sits on it
NOZ_Z = CAB_TOP + 30.0               # the nozzle's bottom in its tray
PIN_Z = CAB_TOP + 110.0              # the pin's axis on its rest
# MiR 2: the key on two posts
KEY_AT2 = (-120.0, -175.0)           # the socket's axis, MiR-local; the bar along local +x
KEY_Z2 = CAB_TOP + 51.0


def fixtures1(lay=LAY1) -> dict:
    """{name: (mesh, colour)} on MiR 1, MiR-local."""
    out = {}

    def at(name, mesh, col, key):
        x, y = lay[key]
        out[name] = (mesh.translate((x, y, 0.0), inplace=False), col)
    # the cradle: a soft ring seat for the crucible's base, a well for the holder and shank, a backlight at the bottom
    at("cradle", C.lathe([(19.0, CAB_TOP + 6.0), (52.0, CAB_TOP + 6.0), (52.0, CRADLE_Z - 3.0), (19.0, CRADLE_Z - 3.0)],
                         res=64).merge(tube(0.0, 52.0, CAB_TOP, CAB_TOP + 6.0)), FIX, "cradle")
    at("cradle pad", tube(20.0, 36.0, CRADLE_Z - 3.0, CRADLE_Z), SILICONE, "cradle")
    at("cradle light", tube(0.0, 10.0, CAB_TOP + 6.0, CAB_TOP + 7.0, res=32), LIGHT, "cradle")
    at("stand cg", tube(0.0, 30.0, CAB_TOP, CG_Z + 6.0), FIX, "cg")
    at("stand nt", tube(36.0, 46.0, CAB_TOP, NT_Z + 10.0), FIX, "nt")
    at("rod holder", C.lathe([(7.6, ROD_Z), (14.0, ROD_Z), (14.0, CAB_TOP + 100.0), (7.6, CAB_TOP + 100.0)], res=40)
       .merge(tube(0.0, 14.0, CAB_TOP, ROD_Z)), FIX, "rod")
    at("tc stand", C.lathe([(2.6, TC_Z), (6.0, TC_Z), (6.0, CAB_TOP + 88.0), (2.6, CAB_TOP + 88.0)], res=24)
       .merge(tube(0.0, 6.0, CAB_TOP, TC_Z)).merge(tube(0.0, 14.0, CAB_TOP, CAB_TOP + 4.0)), FIX, "tc")
    # the pin's rest: a thin fin the shaft lies on, its T-handle out over the end, so the pads can take the handle's
    # two ends from above (as at the lever)
    at("pin tray", box(-3.0, 3.0, -15.0, 15.0, CAB_TOP, PIN_Z - 1.6).merge(box(-20.0, 20.0, -20.0, 20.0, CAB_TOP,
                                                                              CAB_TOP + 6.0)), FIX, "pin")
    # the holder fixture: a block, a bore for the shank, two soft jaws in a slot (their own group: fix_a / fix_b)
    blk = C.lathe([(13.5, CAB_TOP + 8.0), (34.0, CAB_TOP + 8.0), (34.0, FIX_TOP), (13.5, FIX_TOP)], res=48)
    at("fixture", blk.merge(tube(0.0, 34.0, CAB_TOP, CAB_TOP + 8.0)), FIX, "fixture")
    at("nozzle tray", C.lathe([(13.5, NOZ_Z), (22.0, NOZ_Z), (22.0, NOZ_Z + 5.0), (13.5, NOZ_Z + 5.0)], res=48)
       .merge(C.lathe([(3.0, CAB_TOP), (22.0, CAB_TOP), (22.0, NOZ_Z), (3.0, NOZ_Z)], res=48)), FIX, "nozzle")
    at("nozzle light", tube(0.0, 3.0, NOZ_Z - 2.0, NOZ_Z - 0.6, res=24), LIGHT, "nozzle")
    # the tweezers' stand: a slot the jaws hang in (x +-12.5, y +-5.5), its two side walls under the bridge's ends
    ztop = TW_Z + 50.0 - 0.2
    stand = box(-20.0, 20.0, -12.0, 12.0, CAB_TOP, TW_Z - 3.0)
    for x0, x1 in ((-20.0, -12.5), (12.5, 20.0)):
        stand = stand.merge(box(x0, x1, -12.0, 12.0, TW_Z - 3.0, ztop))
    for y0, y1 in ((-12.0, -5.5), (5.5, 12.0)):
        stand = stand.merge(box(-12.5, 12.5, y0, y1, TW_Z - 3.0, ztop - 10.0))
    at("stand tw", stand, FIX, "tw")
    return out


def table_meshes() -> dict:
    """The parts table beside the machine (model frame, ours) with the three insulation seats."""
    (x0, x1), (y0, y1), z = TABLE["x"], TABLE["y"], TABLE["z"]
    top = box(x0, x1, y0, y1, z - 20.0, z)
    legs = None
    for x in (x0 + 25, x1 - 25):
        for y in (y0 + 25, y1 - 25):
            leg = box(x - 15, x + 15, y - 15, y + 15, 0.0, z - 20.0)
            legs = leg if legs is None else legs.merge(leg)
    out = {"table top": (top, (0.55, 0.57, 0.60)), "table legs": (legs, FIX)}
    for name, r in (("top_ring", 103.0), ("side_tube", 64.0), ("bottom_ring", 64.0)):
        sx, sy = SEATS_T[name]
        seat = tube(0.0, r, z, SEAT_Z).merge(tube(r - 3.0, r + 1.0, SEAT_Z, SEAT_Z + 8.0))
        out[f"seat {name}"] = (seat.translate((sx, sy, 0.0), inplace=False), FIX)
    return out


def fixture_jaws(lay=LAY1) -> dict:
    """The holder fixture's two soft jaws (MiR-local, closed on the 24 mm shank): {group: (mesh, colour)}; each slides
    along x by FIX_JAW_OPEN when open."""
    x, y = lay["fixture"]
    out = {}
    for s, grp in ((-1, "fix_a"), (1, "fix_b")):
        jaw = box(s * 12.0 - (10.0 if s < 0 else 0.0), s * 12.0 + (0.0 if s < 0 else 10.0), -9.0, 9.0,
                  FIX_TOP - 40.0, FIX_TOP - 6.0)
        out[grp] = (jaw.translate((x, y, 0.0), inplace=False), SILICONE)
    return out


FIX_JAW_OPEN = 1.4


def key_posts() -> pv.PolyData:
    """Two posts under the key's bar on MiR 2 (MiR-local): the key frame at KEY_AT2, KEY_Z2, bar along local +x."""
    x, y = KEY_AT2
    m = None
    for kx in (60.0, 150.0, 400.0):            # clear of the motor (key x 190-260)
        p = box(x + kx - 12, x + kx + 12, y - 16, y + 16, CAB_TOP, KEY_Z2 - 28.0)
        m = p if m is None else m.merge(p)
    return m


def key_rack_pose() -> np.ndarray:
    """The key's frame on MiR 2, MiR-local."""
    return T((KEY_AT2[0], KEY_AT2[1], KEY_Z2))


def gripper_gap_close(gap: float) -> float:
    """The 2F-85 closure for a pad gap (mm), from ur_arm.gripper_fk (85 mm open, ~1 mm shut)."""
    import ur_arm
    cs = np.linspace(0.0, 1.0, 101)
    gaps = []
    for c in cs:
        G = ur_arm.gripper_fk(c)
        lft = (G["left_finger_tip"] @ np.array([-25.26, 0, 31.9, 1.0]))[0]
        rgt = (G["right_finger_tip"] @ np.array([25.26, 0, 31.9, 1.0]))[0]
        gaps.append(lft - rgt)
    return float(np.interp(-gap, -np.array(gaps), cs))
