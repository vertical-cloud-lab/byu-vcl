"""Where every part goes: the chain solution, the 13 carriages, the frame,
the station and the assembly steps (v4: v3 with the augers outside the loop, Sam's item 7 of 2026-10-29: each module on
its carriage's outer face, the electronics carriage reaching round the auger to dock, an auger-only swap at the side hatch).

Each chain is solved exactly for 104 links on four 32T sprockets on a
114.3 x 228.6 mm rectangle of centres: with 32 teeth a 90-degree wrap is
exactly 8 links, so the pins at every tangent point sit in a tooth gap and
the straights are whole pitches (bottom 12, sides 24, top 12). The two chains
are identical, 305 mm apart in x, and every carriage bolts to the same link
number on both, so a carriage only ever moves in the y-z plane.

A positive shift moves the loop counter-clockwise seen from the back (+x
looking toward -x): along the bottom toward +y, up the +y side, back along
the top, down the -y side. The machine runs the other way (RUN_DIRECTION = -1,
the auger-leakage study), so its moves are negative shifts. Carriage 1 sits at
the station on the bottom straight at home.

``placements(state)`` places the whole rig for a machine state (chain
travel with the exact polygonal kinematics of kinematics.py, which
carriages and modules are on, the station's actuator extension and tilt,
the auger's turn, a carriage half-way through a swap). Everything is in the
frame's own coordinates; ``world()`` applies the frame pitch for the renders.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import cadquery as cq
import numpy as np

from params import *  # noqa: F401,F403
import parts as PT
import parts3 as P3
import parts4 as P4
import parts5 as P5
import kinematics as K

HERE = Path(__file__).resolve().parent
REF = HERE.parent / "chain-carousel-v4" / "reference"   # Sam's Onshape export, the lab auger (v4's copy; v5 adds none)

ALPHA = K.ALPHA
CORNERS = K.CORNERS
DRIVE = "B+"                         # NEMA 34 on this shaft, at the back
CARRIAGE_LINK0 = 6                   # carriage 1's A-1 link at home: on the bottom straight (links 0-11)
LOAD_SLOT = CARRIAGE_LINK0 + 3 * MODULE_LINKS   # 30: the +y side, mid-height, where carriages go on and off
chain_pins = K.home_pins


def T(R3=None, t=(0.0, 0.0, 0.0)) -> np.ndarray:
    M = np.eye(4)
    if R3 is not None:
        M[:3, :3] = R3
    M[:3, 3] = t
    return M


def Rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def cols(*vs) -> np.ndarray:
    return np.array(vs, float).T


def _frame_from_pins(a, b) -> np.ndarray:
    ty, tz = (b - a) / P
    u, w = (0.0, ty, tz), (0.0, -tz, ty)
    return T(cols(u, w, (1.0, 0.0, 0.0)), (0.0, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2))


def carriage_frame(i: int, shift: float = 0.0) -> np.ndarray:
    """Carriage frame on link i after `shift` links of travel: u along the travel, w inward (into the loop),
    x front -> back; origin on the front chain's pitch line mid-way between the link's pins."""
    p = K.pins_at(shift) if shift else chain_pins()
    return _frame_from_pins(p[i % N_LINKS], p[(i + 1) % N_LINKS])


def link_frame(i: int, back: bool, shift: float = 0.0) -> np.ndarray:
    """Frame of link i in parts.py's link coordinates (x along the chain, y radially outward, z along the pins).
    The A-1 tab is on +z, so z points from each chain toward the modules: +x on the front chain, -x on the back."""
    C = carriage_frame(i, shift)
    u, w = C[:3, 0], C[:3, 1]
    if back:
        return T(cols(u, -w, (-1.0, 0.0, 0.0)), C[:3, 3] + (CHAIN_L, 0.0, 0.0))
    return T(cols(-u, -w, (1.0, 0.0, 0.0)), C[:3, 3])


def carriage_links() -> list[int]:
    return [(CARRIAGE_LINK0 + MODULE_LINKS * k) % N_LINKS for k in range(N_MODULES)]


def station_frame() -> np.ndarray:
    """The dispense station: carriage 1's frame at home."""
    return carriage_frame(CARRIAGE_LINK0)


def load_frame() -> np.ndarray:
    """The loading position on the +y side (carriage 4 at home)."""
    return carriage_frame(LOAD_SLOT)


def to_world(M: np.ndarray, xyz) -> np.ndarray:
    return (M @ np.r_[np.asarray(xyz, float), 1.0])[:3]


def slot_of(k: int, shift: float) -> float:
    """Loop slot (home link number, fractional) that carriage k's link occupies after `shift` links."""
    return (CARRIAGE_LINK0 + MODULE_LINKS * k + shift) % N_LINKS


def carriage_at(slot: int, shift: float, tol: float = 0.02) -> int:
    """Carriage whose link sits on home slot `slot` at this shift (or -1)."""
    for k in range(N_MODULES):
        d = (slot_of(k, shift) - slot + N_LINKS / 2) % N_LINKS - N_LINKS / 2
        if abs(d) < tol:
            return k
    return -1


def shift_to(k: int, slot: int, forward: bool = True) -> float:
    """Chain travel (links) that brings carriage k from home onto `slot`, running forward (or backward)."""
    d = (slot - (CARRIAGE_LINK0 + MODULE_LINKS * k)) % N_LINKS
    return float(d if forward else d - N_LINKS)


STATION_Y = float(station_frame()[1, 3])                 # 4.76: carriage 1's centre on the bottom run
HINGE_STATION = to_world(station_frame(), (0.0, HINGE_W, HINGE_X))   # station hinge axis point, frame coordinates


# ---------------------------------------------------------------- side plates
def side_holes(back: bool) -> list[tuple]:
    """(kind, (y, z), size) for every opening in a side plate, world y/z.
    kinds: circle (d), slot (d, length; vertical), tap (M5 tapped)."""
    out = []
    j = BRG["J"] / 2
    lo, hi = TENSION_TRAVEL
    for name, (y, z) in CORNERS.items():
        if name.startswith("B"):
            out.append(("circle", (y, z), (BRG["HOLE"],)))                          # the bearing's rear dome
            for dy in (-j, j):                                                      # bolt line horizontal
                out.append(("circle", (y + dy, z), (BRG["BOLT_D"] + 0.8,)))
        else:                                                                       # top: vertical slots to tension
            zm = z + (lo + hi) / 2
            out.append(("slot", (y, zm), (BRG["HOLE"], BRG["HOLE"] + hi - lo)))
            for dy in (-j, j):
                out.append(("slot", (y + dy, zm), (BRG["BOLT_D"] + 0.8, BRG["BOLT_D"] + 0.8 + hi - lo)))
            for dy in (-10.0, 10.0):                                                # tensioner block screws
                out.append(("tap", (y + dy, z - BRG["DOME_D"] / 2 - 6.0 - 12.0), (5.0,)))
    zb0 = SIDE_Z_BACK[0] if back else SIDE_Z[0]
    zs = [zb0 + 20.0 + k * (SIDE_Z[1] - 15.0 - zb0 - 20.0) / (5 if back else 3) for k in range(6 if back else 4)]
    zl = float(load_frame()[2, 3])                                                  # keep the post screws' heads off the side tabs
    zs = [zl - 34.0 if zl - 34.0 < z < zl + 8.0 else z for z in zs]
    for sy in (-1, 1):                                                              # to the posts' slots
        for z in zs:
            out.append(("circle", (sy * POST_Y, z), (5.5,)))
    for dy in (-12.0, 12.0):                                                        # hold-down, into its inserts:
        out.append(("slot", (STATION_Y + dy, Z_RUN + CAR_W0 - CAR_T - HOLD_DOWN_FOOT_GAP - 11.0), (5.5, 9.5)))   # +-2 mm to set the lip gap
    Lf = load_frame()                                                               # side tabs at the loading position (5a)
    for (du, dw) in P3.SIDE_TAB_INSERTS:
        du = -du if back else du
        uu = Lf[:3, 0] * (-1 if back else 1)
        p = Lf[:3, 3] + uu * du + Lf[:3, 1] * dw
        out.append(("tap", (float(p[1]), float(p[2])), (5.0,)))
    if back:                                                                        # NEMA 34, slotted to tension the drive chain
        out.append(("slot", (LOOP_Y, Z_MOTOR), (M34_PILOT_D + 0.5, M34_PILOT_D + 0.5 + 2 * DRIVE_TRAVEL)))
        for dy in (-1, 1):
            for dz in (-1, 1):
                out.append(("slot", (LOOP_Y + dy * M34_BOLT_SQ / 2, Z_MOTOR + dz * M34_BOLT_SQ / 2),
                            (M34_HOLE_D, M34_HOLE_D + 2 * DRIVE_TRAVEL)))
    return out


@lru_cache(None)
def side_plate_part(back: bool) -> cq.Workplane:
    """Side plate in its own frame: x = world y, y = world z, z = world x measured from the plate's inner face
    (front plate: z in [-6.35, 0]; back plate: z in [0, 6.35])."""
    t = PLATE_T_SIDE
    z0 = 0.0 if back else -t
    p = PT.side_plate(back).translate((0, 0, z0))
    for kind, (y, z), size in side_holes(back):
        if kind in ("circle", "tap"):
            d = size[0] if kind == "circle" else 4.2
            p = p.cut(cq.Workplane("XY").center(y, z).circle(d / 2).extrude(t + 2).translate((0, 0, z0 - 1)))
        elif kind == "slot":
            p = p.cut(cq.Workplane("XY").center(y, z).slot2D(size[1], size[0], angle=90).extrude(t + 2)
                      .translate((0, 0, z0 - 1)))
    return p


# ---------------------------------------------------------------- reference parts
def _read_step_parts(path: Path) -> dict[str, cq.Shape]:
    """Named solids of a STEP assembly, in its world frame."""
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPCAFControl import STEPCAFControl_Reader
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.TDataStd import TDataStd_Name
    from OCP.TDF import TDF_Label, TDF_LabelSequence
    from OCP.TDocStd import TDocStd_Document
    from OCP.TopLoc import TopLoc_Location
    from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool

    doc = TDocStd_Document(TCollection_ExtendedString("d"))
    rd = STEPCAFControl_Reader()
    rd.SetNameMode(True)
    assert rd.ReadFile(str(path)) == IFSelect_RetDone, path
    rd.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    out: dict[str, cq.Shape] = {}

    def name(lab):
        n = TDataStd_Name()
        return n.Get().ToExtString() if lab.FindAttribute(TDataStd_Name.GetID_s(), n) else "part"

    def walk(lab, loc):
        if XCAFDoc_ShapeTool.IsAssembly_s(lab):
            comps = TDF_LabelSequence()
            XCAFDoc_ShapeTool.GetComponents_s(lab, comps)
            for i in range(1, comps.Length() + 1):
                c, ref = comps.Value(i), TDF_Label()
                XCAFDoc_ShapeTool.GetReferredShape_s(c, ref)
                walk(ref, loc.Multiplied(XCAFDoc_ShapeTool.GetLocation_s(c)))
        else:
            out[name(lab)] = cq.Shape.cast(XCAFDoc_ShapeTool.GetShape_s(lab).Moved(loc))

    roots = TDF_LabelSequence()
    st.GetFreeShapes(roots)
    for i in range(1, roots.Length() + 1):
        walk(roots.Value(i), TopLoc_Location())
    return out


@lru_cache(None)
def reference_parts() -> dict[str, cq.Workplane]:
    """v3's mounting plate and electronics carriage (Sam's Oct 13 Part Studio with parts3's additions and cuts) and the
    lab's threaded-storage auger + cap (PR #170). Sam's parts are in his studio frame (hinge axis = his y axis at
    x = z = 0); the auger runs along +z from its outlet end."""
    out = {}
    sam = _read_step_parts(REF / "sam-oct13-mounting-plate-and-carriage.step")
    a, c = P4.plate_additions_v4()                      # v4 plate: dock balls and pad on the auger side, pin-latch keeper
    out["sam_mounting_plate"] = cq.Workplane("XY").add(sam["Mounting Plate"]).union(a).cut(c)
    a, c = P5.ec_additions_v5()                         # EC v5: EC v4 with saddles on the lift bar instead of its clevis
    out["sam_electronics_carriage"] = cq.Workplane("XY").add(sam["Carriage"]).mirror("XY").union(a).cut(c)
    aug = _read_step_parts(REF / "auger-threaded-storage.step")
    out["auger"] = cq.Workplane("XY").add(next(iter(aug.values())))
    cap = _read_step_parts(REF / "auger-cap-threaded.step")
    out["auger_cap"] = cq.Workplane("XY").add(next(iter(cap.values())))
    return out


SAM_IN_CARRIAGE = T(cols((0, 0, 1), (-1, 0, 0), (0, -1, 0)), (0.0, HINGE_W, HINGE_X))   # v4: his x -> x, y -> -u, z -> -w (outward)
AUGER_IN_SAM = T(Ry(math.pi / 2), (AUGER_Z0_XS, 0, 0))


def sam_frame(carriage_M: np.ndarray, tilt_deg: float = 0.0) -> np.ndarray:
    """Sam's studio frame on a carriage (v4: his z points out of the loop). Positive tilt lifts the cap end into the loop
    (outlet down), about the hinge: through the carriage's opening."""
    return carriage_M @ SAM_IN_CARRIAGE @ T(Ry(math.radians(tilt_deg)))


# ---------------------------------------------------------------- frame pitch
X_FRONT_OUT = -SIDE_GAP - PLATE_T_SIDE          # front plate's outer face
X_BACK_OUT = CHAIN_L + SIDE_GAP + PLATE_T_SIDE  # back plate's outer face
X_POST = (X_FRONT_OUT - EXT / 2, X_BACK_OUT + EXT / 2)
RAIL_X0, RAIL_X1 = X_FRONT_OUT - EXT, X_BACK_OUT + EXT
FOOT_X = (RAIL_X0 + 15.0, RAIL_X1 - 15.0)       # leveling feet, front and back
RISER_H = (FOOT_X[1] - FOOT_X[0]) * math.tan(math.radians(FRAME_PITCH_DEG))   # front feet sit this much lower (frame z)


def world_matrix(pitch_deg: float = FRAME_PITCH_DEG) -> np.ndarray:
    """Frame -> bench: the frame pitched outlet (front, -x) end up, about the back feet's contact line."""
    xb = FOOT_X[1]
    return T(None, (xb, 0, 0)) @ T(Ry(math.radians(pitch_deg))) @ T(None, (-xb, 0, 0))


def world(pl: list, pitch_deg: float = FRAME_PITCH_DEG) -> list:
    W = world_matrix(pitch_deg)
    return [Placement(p.key, p.name, W @ p.M, p.step, p.color, p.group, p.explode, p.module) for p in pl]


def frame_dose_tilt(world_tilt: float = TILT_DOSE_WORLD, pitch_deg: float = FRAME_PITCH_DEG) -> float:
    """Hinge angle in the frame for a dose tilt measured from the bench's horizontal."""
    return world_tilt + pitch_deg


# ---------------------------------------------------------------- station geometry (frame coordinates)
def electronics_frame(tilt_frame: float, ext: float) -> np.ndarray:
    """EC v4's as-drawn frame (Sam's carriage mirrored through the auger's axis plane), in the station module's Sam frame:
    docked (its three contacts on the plate's auger side) and tilting with the module, or PARK_DROP - ext further out (down
    at the station) on the approach (ext 0: parked on the cradle's seat)."""
    if tilt_frame > 0 or ext >= PARK_DROP:
        return sam_frame(station_frame(), tilt_frame) @ T(None, (0, 0, DOCK_RISE_V4))
    return sam_frame(station_frame(), 0.0) @ T(None, (0, 0, DOCK_RISE_V4 + (PARK_DROP - ext)))


def actuator_pins(tilt_frame: float, ext: float) -> tuple[np.ndarray, np.ndarray]:
    """(base pin B, rod-end pin P) of the P16, frame coordinates. B is directly under the parked EC's clevis pin, so the
    approach is vertical. The pin rides in the EC's 2 mm slots: fully retracted it floats mid-slot under the parked EC,
    and the LAC targets +1 mm to lift, mid-slot again at the dock (the magnets hold it), +1 mm while tilting. The CAD
    draws it mid-slot."""
    pin = (EC_PIN[0], 0.0, -EC_PIN[1])                  # v4: the clevis is on the far side of the auger (EC mirrored)
    B = to_world(electronics_frame(0.0, 0.0), pin) - np.array([0.0, 0.0, ACT_RETRACTED])
    return B, to_world(electronics_frame(tilt_frame, ext), pin)


def p16_pins(tilt_frame: float, ext: float, side: int) -> tuple[np.ndarray, np.ndarray]:
    """v5: (base pin, rod-end pin) of the P16 on side -1 / +1: v4's single P16 moved along y to +-P16_Y. Both pins are on
    the lift bar's axis line (along y), which is v4's EC clevis-pin axis, so the two P16s and the EC move exactly as v4's
    one did."""
    B, Pp = actuator_pins(tilt_frame, ext)
    d = np.array([0.0, side * P16_Y - Pp[1], 0.0])
    return B + d, Pp + d


STATION_RAIL_X = HINGE_X + EC_PIN[0]               # v5: the station posts' x (v4: the 2020 cross rail under the actuator)
_B0 = actuator_pins(0.0, 0.0)[0]
CLEVIS_PIN_Z = float(_B0[2])
CLEVIS_RISE = 20.2                                 # v5: v4's base clevis as drawn (pin 20.2 mm over its foot), on a shelf
SHELF_TOP_Z = CLEVIS_PIN_Z - CLEVIS_RISE           # the P16 shelves' top faces
BAR_PARK_Z = float(actuator_pins(0.0, 0.0)[1][2])          # lift bar's axis, parked
BAR_DOCK_Z = float(actuator_pins(0.0, PARK_DROP)[1][2])    # ... docked
GUIDE_TOP_Z = BAR_DOCK_Z - SHOE[2] / 2             # the shoe's bottom when docked: it leaves its slot as the EC seats
GUIDE_FLOOR_Z = BAR_PARK_Z - SHOE[2] / 2 - 4.0     # 4 mm under the parked shoe
STATION_POST_TOP = GUIDE_TOP_Z                     # station posts end level with their guides
CRADLE_M = electronics_frame(0.0, 0.0)             # the cradle is drawn in the parked EC's frame
_ZB0 = EC_BASE_Z - EC_BASE_T
CRADLE_FLOOR = -(_ZB0 + 2.6 - KC_BALL_D / 2 - 1.0 - 6.0)   # cradle floor's outer face (its frame, v4: mirrored)
CRADLE_FLOOR_Z = float(to_world(CRADLE_M, (0, 0, CRADLE_FLOOR))[2]) - 6.0   # under the cradle's arm (6 mm, on the post's top)
CRADLE_POST = (STATION_RAIL_X, STATION_Y + 32.0)  # 2020 post on the station rail beside the P16 (v4: world +y = Sam's -y)
LATCH_RAIL_M = None                                # set below: the station carriage's Sam frame at tilt 0
LATCH_RAIL_POST = (HINGE_X + LATCH_FOLLOW_X + 11.0, STATION_Y - LATCH_Y)   # on the second station rail under the rail (also the tube rest)


def world_to_station_sam(xw: float, yw: float) -> tuple[float, float]:
    """A world (x, y) in the station module's Sam frame at tilt 0 (v4: his y is the world's -y there)."""
    S = np.linalg.inv(sam_frame(station_frame(), 0.0))
    v = S @ np.array([xw, yw, HINGE_STATION[2], 1.0])
    return float(v[0]), float(v[1])
LATCH_RAIL_X = LATCH_RAIL_POST[0]                  # v5: the latch post's and the latch beam's x
LATCH_BEAM_ZC = float(HINGE_STATION[2]) - P4.STATION_RAILS_OUTER - EXT / 2   # v5: the beam's top where v4's latch post ended
LATCH_BEAM_L = LATCH_RAIL_POST[1] + EXT / 2 - (-POST_Y + EXT / 2)            # from the latch post's inner face to under the rail's pad


def exit_point(tilt_frame: float) -> np.ndarray:
    """Auger exit (the 3 mm hole on the axis at the outlet plane), frame coordinates: on the hinge axis, so it doesn't
    move with the tilt."""
    return to_world(sam_frame(station_frame(), tilt_frame), (AUGER_Z0_XS, 0.0, 0.0))


DOSE_POINT = exit_point(0.0)                       # where the dose leaves the module, at every tilt
CARR_FRONT_X = float(HINGE_STATION[0] + 2.33)      # docked/approaching EC's front face (Sam x 2.33)
CRADLE_POST_S = world_to_station_sam(*CRADLE_POST)
LATCH_POST_S = world_to_station_sam(*LATCH_RAIL_POST)


def scale_pan_target() -> np.ndarray:
    """Where the HR-100A's pan centre has to be: under the dose point (world x, y; the bench at z = 0)."""
    return np.array([DOSE_POINT[0], DOSE_POINT[1], 0.0])


# ---------------------------------------------------------------- placements
@dataclass
class Placement:
    key: str
    name: str
    M: np.ndarray
    step: int
    color: tuple = (0.6, 0.6, 0.6)
    group: str = ""
    explode: tuple = (0.0, 0.0, 0.0)      # world offset used by the step renders
    module: int = -1                      # carriage slot this instance moves with (-1: fixed or chain)


@dataclass
class State:
    shift: float = 0.0                    # chain travel, links (forward = bottom run toward +y)
    carriages: tuple = tuple(range(N_MODULES))    # carriages on the chain
    modules: tuple = tuple(range(N_MODULES))      # carriages that carry a module (plate, auger, cap)
    tilt: float = 0.0                     # station module's hinge angle in the frame, deg (cap end up)
    ext: float = PARK_DROP                # actuator extension at tilt 0 (0 parked on the cradle, PARK_DROP docked)
    station: bool = True
    spin: float = 0.0                     # auger turn at the station, rad (pinion turns -spin * 44/20)
    tap: float = 0.0                      # solenoid plunger travel, mm
    magnet_on: bool = False
    out_carriage: int = -1                # carriage coming off/going on at the loading position
    out_auger: int = -1                   # v4: module whose auger is coming off its plate at the loading position
    auger_out: float = 0.0                # v4: how far (mm, out of the loop, Sam's +z)
    out_slide: float = 0.0                # mm along +u (frees the hooks from the tabs)
    out_lift: float = 0.0                 # mm outward, away from the loop
    screws_out: float = 0.0               # its two tab screws backed out by (mm)
    tension: float = 0.0                  # top shafts' offset, mm
    door: float = -1.0                    # station module's outlet door opening, mm (-1: set by the EC's position)
    hatch_front: float = 0.0              # front hatch opening angle, deg
    hatch_side: float = 0.0               # side hatch opening angle, deg
    enclosure: bool = True                # acrylic panels, hatches, standoffs
    scale: bool = True                    # v5: the HR-202i (or the HR-100A), its pan centre at the dose point + scale_offset
    scale_model: str = "hr202i"           # v5: "hr202i" or "hr100a"
    top_door: float = 0.0                 # v5: the HR-202i's top door slid back, mm (P5.HR2_TOP_OPEN open)
    side_door: float = 0.0                # v5: its -y side door slid back, mm
    beaker_dx: float = 0.0                # v5: the beaker moved off its seat (x, y: out through the -y side door; z: lifted out of the cup)
    beaker_dy: float = 0.0
    beaker_dz: float = 0.0
    scale_offset: tuple = (0.0, 0.0)      # (x, y) mm, for the scale-fit study
    beaker: bool = True
    side_tabs: bool = True
    extra: list = field(default_factory=list)     # extra placements (animation props)


STEEL = (0.62, 0.64, 0.67)
DARK = (0.18, 0.18, 0.2)
ALU = (0.80, 0.82, 0.85)
PLATE_ALU = (0.70, 0.72, 0.76)
PETG = (0.16, 0.36, 0.78)
ORANGE = (0.95, 0.55, 0.12)
SAM = (0.10, 0.25, 0.85)
WHITE = (0.97, 0.97, 0.97)
BLANK = (0.88, 0.88, 0.84)
BRASS = (0.80, 0.65, 0.25)
GREEN = (0.10, 0.50, 0.25)
RED = (0.85, 0.12, 0.10)
CAST = (0.42, 0.44, 0.47)
GLASS = (0.75, 0.88, 0.95)
ELEC = (0.20, 0.45, 0.95)
MAGNET_RED = (0.75, 0.15, 0.12)

STEPS = {
    1: "Base frame: rails, two station rails, corner brackets, leveling feet",
    2: "Posts and top frame",
    3: "Side plates onto the posts",
    4: "Flange bearings and top-shaft tensioners on the side plates",
    5: "Corner shafts with their sprockets (back set screws loose)",
    6: "NEMA 34 on the back plate, 15T sprockets, drive chain",
    7: "Chains: 13 A-1 links per chain, close both loops",
    8: "Station: hold-downs, hall switches, the P16, the guide cradle on its post, the electronics carriage v4 (arms round the auger, dock seats, magnets, balls), the latch rail and tube rest, the side tabs",
    9: "Modules on the bench: auger into the v4 plate, auger-side dock balls and steel washer, outlet door; plate pinned onto a carriage's outer face, latch pin in",
    10: "Carriages onto the chain at the loading position, one index at a time; phase and tension",
    11: "Electronics board: supply, driver, Pi, interface board, LAC, e-stop",
    12: "Enclosure: acrylic panels on standoffs, the front hatch (scale) and the side hatch (swaps); the HR-100A",
}
SCALE_GHOST = (0.93, 0.93, 0.95)
ACRYL = (0.80, 0.90, 0.98)

X_DRV = X_BACK_OUT + BRG["OUT"] + 7.5            # drive chain's centre plane, 2 mm clear of the bearing
SHAFT_X0 = X_FRONT_OUT - BRG["OUT"]
SHAFT_L = X_BACK_OUT + BRG["OUT"] - SHAFT_X0      # flush with both bearings' inserts
DRIVE_EXTRA = X_DRV + LTB15 - TOOTH_W / 2 - (X_BACK_OUT + BRG["OUT"])   # B+ shaft's stub for the 15T


@lru_cache(None)
def drive_chain_pins() -> np.ndarray:
    """44 pin centres (y, z) of the drive chain: two equal 15T sprockets, C = 14.5 pitches, solved like v1's loop
    (14-link spans, 8 links on each sprocket). The stub sprocket (B+ shaft) is at the top."""
    r = PD15 / 2
    al = 2 * math.pi / N15
    ha = al / 2
    xd, xi = C_DRIVE / 2, -C_DRIVE / 2           # local x: motor (-) -> stub (+)
    A = np.array([xd, r])
    B = np.array([xi + P / 2, r * math.cos(ha)])
    D = np.array([xi, -r])
    E = np.array([xd - P / 2, -r * math.cos(ha)])
    span = (DRIVE_LINKS - 16) // 2
    pts = [A + (B - A) * i / span for i in range(span)]
    pts += [np.array([xi + r * math.cos(math.pi / 2 - ha + k * al), r * math.sin(math.pi / 2 - ha + k * al)]) for k in range(8)]
    pts += [D + (E - D) * i / span for i in range(span)]
    pts += [np.array([xd + r * math.cos(-math.pi / 2 - ha + k * al), r * math.sin(-math.pi / 2 - ha + k * al)]) for k in range(8)]
    pts = np.array(pts)
    gaps = np.linalg.norm(np.roll(pts, -1, axis=0) - pts, axis=1)
    assert len(pts) == DRIVE_LINKS and np.allclose(gaps, P, atol=2e-3), (len(pts), gaps.min(), gaps.max())
    zc = (Z_BOT + Z_MOTOR) / 2
    return np.column_stack([LOOP_Y + pts[:, 1], zc + pts[:, 0]])


def drive_chain_pins_at(shift: float) -> np.ndarray:
    """Drive chain advanced with the B+ shaft: 15/32 of a drive link per link of the main chain, moved along
    the pins' polygon (within 0.5 mm of the exact path on the 15T arcs; it only matters for the renders)."""
    pins = drive_chain_pins()
    s_mm = (shift * N15 / N_TEETH) * P
    n = len(pins)
    seg = np.linalg.norm(np.roll(pins, -1, axis=0) - pins, axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    total = cum[-1]
    out = np.zeros_like(pins)
    for j in range(n):
        d = (cum[j] + s_mm) % total
        k = int(np.searchsorted(cum, d, side="right") - 1) % n
        f = (d - cum[k]) / seg[k]
        out[j] = pins[k] + f * (pins[(k + 1) % n] - pins[k])
    return out


def bracket(corner, n1, n2) -> np.ndarray:
    """Corner bracket: leg on the surface with outward normal n1, the other leg against the surface with outward
    normal n2, at the corner point."""
    n1, n2 = np.asarray(n1, float), np.asarray(n2, float)
    return T(cols(n2, np.cross(n1, n2), n1), corner)


def _carriage_M(k: int, st: State) -> np.ndarray:
    li = carriage_links()[k]
    C = carriage_frame(li, st.shift)
    if k == st.out_carriage:
        C = C @ T(None, (st.out_slide, -st.out_lift, 0.0))
    return C


def placements(state: State | float | None = None) -> list[Placement]:
    """Every instance for a machine state (a float is taken as the station module's hinge angle, as before)."""
    if state is None:
        st = State()
    elif isinstance(state, (int, float)):
        st = State(tilt=float(state))
    else:
        st = state
    out: list[Placement] = []
    add = out.append
    zr0, zr1 = Z_BASE, Z_BASE + EXT                       # base rails
    zt0, zt1 = Z_TOP_RAIL, Z_TOP_RAIL + EXT               # top rails
    L_x, L_y = RAIL_X1 - RAIL_X0, 2 * POST_Y - EXT        # rails along x run full length; along y fit between

    # 1. base frame, station rail, feet (+ risers under the front feet for the pitch)
    for sy in (-1, 1):
        add(Placement("ext_x", f"Base rail {'-y' if sy < 0 else '+y'}", T(Ry(math.pi / 2), (RAIL_X0, sy * POST_Y, (zr0 + zr1) / 2)),
                      1, ALU, "frame", (0, sy * 40, -40)))
    # v5: only the back base cross rail. The HR-202i stands where v4's front cross rail and both station rails were; the
    # front posts are tied by the front side plate and the top cross rail.
    add(Placement("ext_y", "Base cross rail back", T(Rx(-math.pi / 2), (X_POST[1], -L_y / 2, (zr0 + zr1) / 2)), 1, ALU, "frame", (0, 0, -60)))
    # v5: the station posts (P16 shelves and the bar guides) and the latch post, on the side base rails; the latch beam
    for sy in (-1, 1):
        add(Placement("ext_station_post", f"Station post {'-y' if sy < 0 else '+y'} (2020)", T(None, (STATION_RAIL_X, sy * POST_Y, zr1)), 1, ALU,
                      "frame", (0, sy * 40, 0)))
        for sx in (-1, 1):
            add(Placement("corner_bracket", "Corner bracket (station post)",
                          bracket((STATION_RAIL_X + sx * EXT / 2, sy * POST_Y, zr1), (0, 0, 1), (sx, 0, 0)), 1, ALU, "frame", (0, 0, 40)))
    add(Placement("ext_latch_post5", "Latch post -y (2020)", T(None, (LATCH_RAIL_X, -POST_Y, zr1)), 1, ALU, "frame", (0, -40, 0)))
    for sx in (-1, 1):
        add(Placement("corner_bracket", "Corner bracket (latch post)",
                      bracket((LATCH_RAIL_X + sx * EXT / 2, -POST_Y, zr1), (0, 0, 1), (sx, 0, 0)), 1, ALU, "frame", (0, 0, 40)))
    add(Placement("ext_latch_beam", "Latch beam (2020, along y off the latch post)", T(Rx(-math.pi / 2), (LATCH_RAIL_X, -POST_Y + EXT / 2, LATCH_BEAM_ZC)),
                  1, ALU, "frame", (0, -40, 0)))
    add(Placement("corner_bracket", "Corner bracket (latch beam)",
                  bracket((LATCH_RAIL_X, -POST_Y + EXT / 2, LATCH_BEAM_ZC - EXT / 2), (0, 0, -1), (0, 1, 0)), 1, ALU, "frame", (0, 0, 40)))
    for xf in FOOT_X:
        front = xf < 0
        for sy in (-1, 1):
            zf = -RISER_H if front else 0.0
            if front and RISER_H > 0.5:
                add(Placement("riser", "Front riser (2020 stub)", T(None, (xf, sy * POST_Y, zr0 - RISER_H)), 1, ALU, "frame", (0, 0, -80)))
            add(Placement("foot", "Leveling foot (swivel)", T(None, (xf, sy * POST_Y, zf)), 1, DARK, "frame", (0, 0, -80)))
            add(Placement("tnut_m5", "T-nut (foot)", T(Rx(math.pi), (xf, sy * POST_Y, zr0 + 2.2)), 1, STEEL, "frame", (0, 0, -80)))
    # 2. posts and top frame
    for xp in X_POST:
        for sy in (-1, 1):
            add(Placement("ext_post", "Post", T(None, (xp, sy * POST_Y, zr1)), 2, ALU, "frame", (0, sy * 30, 0)))
            sx = 1 if xp < 0 else -1
            add(Placement("corner_bracket", "Corner bracket (post foot)",
                          bracket((xp + sx * EXT / 2, sy * POST_Y, zr1), (0, 0, 1), (sx, 0, 0)), 2, ALU, "frame", (0, 0, 40)))
            add(Placement("corner_bracket", "Corner bracket (post foot)",
                          bracket((xp, sy * (POST_Y - EXT / 2), zr1), (0, 0, 1), (0, -sy, 0)), 2, ALU, "frame", (0, 0, 40)))
            add(Placement("corner_bracket", "Corner bracket (post head)",
                          bracket((xp + sx * EXT / 2, sy * POST_Y, zt0), (0, 0, -1), (sx, 0, 0)), 2, ALU, "frame", (0, 0, 60)))
            add(Placement("corner_bracket", "Corner bracket (post head)",
                          bracket((xp, sy * (POST_Y - EXT / 2), zt0), (0, 0, -1), (0, -sy, 0)), 2, ALU, "frame", (0, 0, 60)))
    for sy in (-1, 1):
        add(Placement("ext_x", f"Top rail {'-y' if sy < 0 else '+y'}", T(Ry(math.pi / 2), (RAIL_X0, sy * POST_Y, (zt0 + zt1) / 2)),
                      2, ALU, "frame", (0, sy * 30, 80)))
    for xp in X_POST:
        add(Placement("ext_y", f"Top cross rail {'front' if xp < 0 else 'back'}",
                      T(Rx(-math.pi / 2), (xp, -L_y / 2, (zt0 + zt1) / 2)), 2, ALU, "frame", (0, 0, 80)))
    # 3. side plates
    Rside = cols((0, 1, 0), (0, 0, 1), (1, 0, 0))          # plate x -> world y, y -> z, z -> x
    add(Placement("side_plate_front", "Side plate, front (1/4in 6061)", T(Rside, (-SIDE_GAP, 0, 0)), 3, PLATE_ALU, "plates", (-70, 0, 0)))
    add(Placement("side_plate_back", "Side plate, back (1/4in 6061)", T(Rside, (CHAIN_L + SIDE_GAP, 0, 0)), 3, PLATE_ALU, "plates", (70, 0, 0)))
    for back in (False, True):
        xi = CHAIN_L + SIDE_GAP if back else -SIDE_GAP
        sgn = 1 if back else -1
        for kind, (y, z), size in side_holes(back):
            if kind == "circle" and abs(abs(y) - POST_Y) < 0.1:
                add(Placement("m5x12_bhcs", "Side plate screw M5x12", T(Ry(-sgn * math.pi / 2), (xi, y, z)), 3, DARK, "plates", (sgn * 90, 0, 0)))
                add(Placement("tnut_m5", "T-nut (side plate)", T(Ry(sgn * math.pi / 2), (xi + sgn * (PLATE_T_SIDE + 2.2), y, z)),
                              3, STEEL, "plates", (sgn * 110, 0, 0)))
    # 4. bearings and tensioners
    for back in (False, True):
        xo = X_BACK_OUT if back else X_FRONT_OUT
        Rb = cols((0, 0, -1), (0, 1, 0), (1, 0, 0)) if back else cols((0, 0, 1), (0, 1, 0), (-1, 0, 0))
        sgn = 1 if back else -1
        for name, (y, z) in CORNERS.items():
            zz = z + (st.tension if name.startswith("T") else 0.0)
            add(Placement("flange_bearing", f"Flange bearing {name} {'back' if back else 'front'}", T(Rb, (xo, y, zz)), 4, CAST,
                          "bearings", (sgn * 60, 0, 0)))
            for dy in (-BRG["J"] / 2, BRG["J"] / 2):
                add(Placement("bolt_m6x25", "Bearing bolt 1/4-20 x 1in", T(Ry(sgn * math.pi / 2), (xo + sgn * BRG["T"], y + dy, zz)), 4,
                              DARK, "bearings", (sgn * 90, 0, 0)))
                add(Placement("nut_m6", "Bearing locknut 1/4-20 (nylon insert)", T(Ry(-sgn * math.pi / 2), (xo - sgn * PLATE_T_SIDE, y + dy, zz)),
                              4, STEEL, "bearings", (-sgn * 40, 0, 0)))
            if name.startswith("T"):
                Rt = cols((0, 1, 0), (0, 0, 1), (1, 0, 0)) if back else cols((0, -1, 0), (0, 0, 1), (-1, 0, 0))
                zb = z - BRG["DOME_D"] / 2 - 6.0
                add(Placement("tensioner_block", f"Tensioner block {name} {'back' if back else 'front'} (printed)",
                              T(Rt, (xo, y, zb)), 4, ORANGE, "bearings", (sgn * 40, 0, -20)))
                for dy in (-10.0, 10.0):
                    add(Placement("m5x10_shcs", "Tensioner block screw M5x10", T(Ry(sgn * math.pi / 2), (xo + sgn * 4.0, y + dy, zb - 12)),
                                  4, DARK, "bearings", (sgn * 70, 0, -20)))
                xs = xo + sgn * 7.0
                add(Placement("m5x30_shcs", "Jack screw M5x30", T(cols((0, 1, 0), (1, 0, 0), (0, 0, -1)), (xs, y, z - BRG["DOME_D"] / 2 - 30.0)),
                              4, DARK, "bearings", (sgn * 40, 0, -50)))
                add(Placement("nut_m5", "Jack screw locknut M5 (trapped, nylon insert)", T(None, (xs, y, zb - 8.65)), 4, STEEL, "bearings", (sgn * 40, 0, -20)))
    # 5. shafts and sprockets (all four turn together with the chain)
    phi = K.sprocket_angle(st.shift)
    for name, (y, z) in CORNERS.items():
        zz = z + (st.tension if name.startswith("T") else 0.0)
        key = "shaft_drive" if name == DRIVE else "shaft"
        add(Placement(key, f"Shaft {name} (5/8in keyed)", T(Ry(math.pi / 2), (SHAFT_X0, y, zz)) @ T(Rz(-phi)), 5, STEEL, "shafts", (-120, 0, 0)))
        add(Placement("sprocket_32", f"Sprocket 35BS32 {name} front", T(cols((0, 1, 0), (0, 0, 1), (1, 0, 0)), (0.0, y, zz)) @ T(Rz(phi)), 5, STEEL,
                      "sprockets", (60, 0, 0)))
        add(Placement("sprocket_32", f"Sprocket 35BS32 {name} back", T(cols((0, 1, 0), (0, 0, -1), (-1, 0, 0)), (CHAIN_L, y, zz)) @ T(Rz(-phi)), 5,
                      STEEL, "sprockets", (-60, 0, 0)))
    # 6. NEMA 34 inside the frame on the back plate's inner face; #35 drive chain up to the B+ shaft's stub
    Rm = cols((0, 1, 0), (0, 0, 1), (1, 0, 0))
    xi_b = CHAIN_L + SIDE_GAP
    add(Placement("nema34", "NEMA 34 34HS59-6004D-E1000", T(Rm, (xi_b, LOOP_Y, Z_MOTOR)), 6, DARK, "drive", (-170, 0, 0)))
    for dy in (-1, 1):
        for dz in (-1, 1):
            pp = (LOOP_Y + dy * M34_BOLT_SQ / 2, Z_MOTOR + dz * M34_BOLT_SQ / 2)
            add(Placement("m5x25_shcs", "Motor bolt M5x25", T(Ry(math.pi / 2), (X_BACK_OUT, *pp)), 6, DARK, "drive", (80, 0, 0)))
            add(Placement("nut_m5", "Motor locknut M5 (nylon insert)", T(Ry(-math.pi / 2), (xi_b - 12.0, *pp)), 6, STEEL, "drive", (-120, 0, 0)))
    Rs15 = cols((0, 1, 0), (0, 0, -1), (-1, 0, 0))
    add(Placement("sprocket_15_motor", "Drive sprocket 15T on the motor (35BS15H-1/2 bored 14 mm)",
                  T(Rs15 @ Rz(-math.pi / N15), (X_DRV, LOOP_Y, Z_MOTOR)) @ T(Rz(-phi)), 6, STEEL, "drive", (60, 0, 0)))
    add(Placement("sprocket_15_shaft", "Drive sprocket 15T on the B+ shaft (35BS15H-5/8)", T(Rs15, (X_DRV, LOOP_Y, Z_BOT)) @ T(Rz(-phi)), 6, STEEL,
                  "drive", (80, 0, 0)))
    dp = drive_chain_pins_at(st.shift) if st.shift else drive_chain_pins()
    for i in range(DRIVE_LINKS):
        a_, b_ = dp[i], dp[(i + 1) % DRIVE_LINKS]
        d = (b_ - a_) / max(np.linalg.norm(b_ - a_), 1e-9)
        ty, tz = d
        Ml = T(cols((0, -ty, -tz), (0, tz, -ty), (1, 0, 0)), (X_DRV, (a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2))
        add(Placement("chain_outer" if i % 2 == 0 else "chain_inner", "Drive chain link", Ml, 6, STEEL, "drive", (80, 0, 0)))
    # 7. chains: every 8th link an A-1 attachment connecting link, same links on both chains
    cl = set(carriage_links())
    for back in (False, True):
        for i in range(N_LINKS):
            M = link_frame(i, back, st.shift)
            ex = (60 if not back else -60, 0, 0)
            key = "chain_a1" if i in cl else ("chain_outer" if i % 2 == 0 else "chain_inner")
            nm = f"A-1 attachment connecting link ({'back' if back else 'front'})" if i in cl else ("Outer link" if i % 2 == 0 else "Inner link")
            add(Placement(key, nm, M, 7, STEEL, "chain", ex))

    # 8. station
    if st.station:
        _station(st, add)

    # 9-10. carriages and their modules
    k_st = carriage_at(CARRIAGE_LINK0, st.shift)
    for k in st.carriages:
        C = _carriage_M(k, st)
        out_dir = tuple(-C[:3, 1] * 60)
        add(Placement("carriage", f"Carriage {k + 1}", C, 10, PETG, "carriages", out_dir, k))
        for xa in (A1_HOLE_C, CHAIN_L - A1_HOLE_C):
            so = st.screws_out if k == st.out_carriage else 0.0
            add(Placement("m3x12_bhcs", f"Tab screw M3x12 button head {k + 1}", C @ T(Rx(math.pi / 2), (0, CAR_W0 - CAR_T + TAB_SCREW_CB - so, xa)), 10, DARK,
                          "carriages", out_dir, k))
            add(Placement("nut_m3", f"Tab locknut M3 (in the hook) {k + 1}", C @ T(Rx(-math.pi / 2), (0, CAR_W0 + PLATE_T + 0.28, xa)), 10, STEEL,
                          "carriages", out_dir, k))
        mz = CAR_W0 - 0.3 - MAGNET_H
        add(Placement("magnet", f"Index magnet {k + 1}", C @ T(Rx(-math.pi / 2), (0, mz, CAR_X0 + 7.0)), 10, STEEL, "carriages", out_dir, k))
        if k == 0:
            add(Placement("magnet", "Home magnet", C @ T(Rx(-math.pi / 2), (0, mz, CAR_X1 - 7.0)), 10, STEEL, "carriages", out_dir, k))
        # 4a. the plate latch (v4: a pin in the keeper's hole) rides on the carriage; the station's rail draws it back
        lo = latch_open(k, st)
        Ml = sam_frame(C, 0.0)
        add(Placement("latch_bolt", f"Latch bolt: 4 mm pin in a printed carrier {k + 1}", Ml @ T(None, (lo, 0, 0)), 10, ORANGE, "carriages", out_dir, k))
        add(Placement("latch_follower", f"Latch follower, dowel 3 x 40 {k + 1}", Ml @ T(None, (LATCH_FOLLOW_X + lo, LATCH_Y, 0)), 10, STEEL,
                      "carriages", out_dir, k))
        add(Placement("latch_spring", f"Latch spring {k + 1}", Ml @ T(Ry(math.pi / 2), (P4.LATCH4_TAIL[1] + lo, LATCH_Y, LATCH4_PIN[1])), 10, STEEL,
                      "carriages", out_dir, k))
        if k not in st.modules:
            continue
        on_station = (k == k_st and st.station)
        tilt = st.tilt if on_station else 0.0
        Ms = sam_frame(C, tilt)
        add(Placement("sam_mounting_plate", f"Mounting plate v4 (Sam's Oct 13 + auger-side dock, pin keeper) {k + 1}", Ms, 9, SAM, "modules", out_dir, k))
        for (x, y) in (KC4_A, KC4_B):
            add(Placement("kc_ball", f"Dock ball 1/4in chrome steel (plate) {k + 1}", Ms @ T(None, (x, y, KC4_BALL_Z)), 9, STEEL, "modules", out_dir, k))
        add(Placement("flat_pad_v4", f"Dock flat: M5 steel washer (plate) {k + 1}", Ms @ T(None, (KC4_C[0], KC4_C[1], -13.0)), 9, STEEL, "modules", out_dir, k))
        dz = door_open(st) if on_station else 0.0
        add(Placement("door_housing", f"Outlet door housing (printed) {k + 1}", Ms, 9, ORANGE, "modules", out_dir, k))
        add(Placement("door_shutter", f"Outlet door shutter (printed) {k + 1}", Ms @ T(None, (0, 0, -dz)), 9, DARK, "modules", out_dir, k))
        sk = "door_spring_open" if dz > 0.5 else "door_spring"
        add(Placement(sk, f"Outlet door spring {k + 1}", Ms @ T(None, (P3.DOOR_SPRING_X, 0.0, -DOOR_SPRING_SEAT)), 9, STEEL, "modules", out_dir, k))
        for sy in (-1, 1):
            add(Placement("m2x8_shcs", f"Door housing screw M2x8 {k + 1}", Ms @ T(None, (18.5, sy * 13.7, -8.0)), 9, DARK, "modules", out_dir, k))
        spin = st.spin if on_station else 0.0
        Ma = Ms @ AUGER_IN_SAM @ T(Rz(spin))
        if k == st.out_auger:
            Ma = Ms @ T(None, (0, 0, st.auger_out)) @ AUGER_IN_SAM
        add(Placement("auger", f"Auger, threaded storage {k + 1}", Ma, 9, WHITE, "modules", out_dir, k))
        add(Placement("auger_cap", f"Auger cap {k + 1}", Ma @ T(None, (0, 0, AUGER_LEN)), 9, WHITE, "modules", out_dir, k))
        for su in (-1, 1):
            u_head = su * (LUG_U4 + LUG_T - PIN_CBORE[1])
            Rp = Ry(su * math.pi / 2)                        # head (+z) outward, shank toward the carriage centre
            add(Placement("clevis_pin", f"Hinge pin 5 mm, grooved {k + 1}", C @ T(Rp, (u_head, HINGE_W, HINGE_X)), 9, STEEL, "modules", out_dir, k))
            add(Placement("eclip", f"E-clip DIN 6799-4 {k + 1}", C @ T(Rp, (su * PIN_GROOVE_U, HINGE_W, HINGE_X)), 9, DARK, "modules", out_dir, k))

    # 11. electronics board beside the rig (on the bench, behind it on the +y side)
    bx, by = CHAIN_L + 330.0, 260.0
    add(Placement("board_panel", "Electronics board (1/4in plywood)", T(None, (bx, by, 0.0)), 11, (0.80, 0.68, 0.48), "elec", (0, 80, 0)))
    add(Placement("lrs350", "Mean Well LRS-350-48", T(None, (bx - 90, by + 70, 6.35)), 11, ALU, "elec", (0, 80, 60)))
    add(Placement("cl86t", "CL86T closed-loop driver", T(None, (bx + 105, by + 55, 6.35)), 11, DARK, "elec", (0, 80, 60)))
    add(Placement("raspberry_pi", "Raspberry Pi", T(None, (bx - 120, by - 85, 6.35 + 6)), 11, GREEN, "elec", (0, 80, 60)))
    add(Placement("perfboard", "Interface board (74AHCT125, pull-ups)", T(None, (bx - 20, by - 85, 6.35 + 6)), 11, GREEN, "elec", (0, 80, 60)))
    add(Placement("lac", "Actuonix LAC board", T(None, (bx + 60, by - 85, 6.35)), 11, GREEN, "elec", (0, 80, 60)))
    add(Placement("estop", "E-stop", T(None, (bx + 150, by - 90, 6.35)), 11, RED, "elec", (0, 80, 60)))
    # 12. enclosure and the scale
    if st.enclosure:
        _enclosure(st, add)
    if st.scale:
        _scale(st, add)
    out += st.extra
    return out


def latch_open(k: int, st: State) -> float:
    """How far carriage k's latch bolt is drawn back (mm): the station's rail has a flat +-22 mm about the station and
    25 deg ramps at both ends, and only bottom-run carriages near the station reach it."""
    d = ((slot_of(k, st.shift) - CARRIAGE_LINK0 + N_LINKS / 2) % N_LINKS - N_LINKS / 2) * P
    flat, ramp = LATCH_RAIL_FLAT, LATCH_TRAVEL / math.tan(math.radians(25.0))
    if abs(d) >= flat + ramp:
        return 0.0
    return LATCH_TRAVEL * min(1.0, (flat + ramp - abs(d)) / ramp)


def door_open(st: State) -> float:
    """The station module's door opening (mm): the EC's finger lifts the push strip in the last DOOR_TRAVEL of the dock."""
    if st.door >= 0:
        return st.door
    if not st.station:
        return 0.0
    if st.tilt > 0 or st.ext >= PARK_DROP:
        return DOOR_TRAVEL
    return max(0.0, DOOR_TRAVEL - (PARK_DROP - st.ext))


def _hold_downs(add, frame_y, frame_z, u_axis, w_axis, label, key="hold_down", key_m=None, step=8, switches=True, inserts=None):
    """A pair of tongue tabs (front and back side plates) for a carriage frame on a straight: v2's hold-downs at the
    station, v3's side tabs at the loading position. `inserts`: (u, w) of the screws in the front tab's frame (the back
    tab, mirrored in u when key_m is given, gets (-u, w))."""
    u, w = np.asarray(u_axis, float), np.asarray(w_axis, float)
    ins = inserts or [(dy, CAR_W0 - CAR_T - HOLD_DOWN_FOOT_GAP - 11.0) for dy in (-12.0, 12.0)]
    HDf = T(cols(u, w, (1, 0, 0)), (-SIDE_GAP, frame_y, frame_z))
    HDb = T(cols(-u, w, (-1, 0, 0)), (CHAIN_L + SIDE_GAP, frame_y, frame_z))
    tz = CAR_W0 + HOLD_DOWN_GAP
    zc = SIDE_GAP + CAR_X0 + 7.0
    Rsw = cols((1, 0, 0), (0, 0, -1), (0, 1, 0))
    for HD, nm, sgn, kk in ((HDf, "front, INDEX", -1, key), (HDb, "back, HOME", 1, key_m or key)):
        add(Placement(kk, f"{label} ({nm.split(',')[0]}, printed)", HD, step, ORANGE, "station", (0, 0, 60)))
        if switches:
            add(Placement("hall_switch", f"Hall switch US5881 ({nm.split(', ')[1]})", HD @ T(Rsw, (0, tz + 0.8, zc)), step, DARK, "station", (0, 0, 90)))
        for (du, dw) in ins:
            du = -du if (sgn > 0 and key_m) else du
            if inserts is None:                     # hold-downs: M5 x 16 from outside the side plate into inserts in the foot
                p = to_world(HD, (du, dw, 0.0))
                xo = X_BACK_OUT if sgn > 0 else X_FRONT_OUT
                add(Placement("m5x16_shcs", f"{label} screw M5x16", T(Ry(sgn * math.pi / 2), (xo, p[1], p[2])), step, DARK, "station", (sgn * 60, 0, 0)))
                add(Placement("insert_m5", f"M5 heat-set insert ({label.lower()})", HD @ T(None, (du, dw, 0.0)), step, BRASS, "station", (0, 0, 60)))
            else:                                   # side tabs: M5 x 10 from the tab's counterbore into the plate's tapped hole
                add(Placement("m5x8_shcs", f"{label} screw M5x8 (into the tapped plate)", HD @ T(None, (du, dw, P3.SIDE_TAB_CB_Z)), step, DARK,
                              "station", (0, 0, 60)))


def _station(st: State, add) -> None:
    """v3 station: hold-downs and hall switches (v2's), the P16 pinned at both ends, the guide cradle on its post with its
    Kelvin seat, EC v3 (Sam's carriage + the dock: cone and vee seats with magnets, the flat ball, the dock electromagnet;
    the base balls and the slotted clevis), the NEMA 11, pinion and solenoid, the latch rail on its post; the side tabs at
    the loading position. No fork, no funnel, no load cell: the HR-100A is placed by _scale."""
    S = station_frame()
    _hold_downs(add, STATION_Y, Z_RUN, (0, 1, 0), (0, 0, 1), "Hold-down")
    if st.side_tabs:                                    # 5a: the loading position's tabs (+y side, the run goes up there)
        Lf = load_frame()
        _hold_downs(add, float(Lf[1, 3]), float(Lf[2, 3]), Lf[:3, 0], Lf[:3, 1], "Side tab", key="side_tab", key_m="side_tab_m",
                    switches=False, inserts=list(P3.SIDE_TAB_INSERTS))
    # v5: two P16s beside the balance, pinned at both ends; their rod ends' adapters carry the lift bar, which the EC's
    # saddles clamp; the bar's end shoes run in the station posts' guides until the EC seats
    for side in (-1, 1):
        B, Pp = p16_pins(st.tilt, st.ext, side)
        zdir = (Pp - B) / np.linalg.norm(Pp - B)
        ydir = np.array([0.0, 1.0, 0.0])
        xdir = np.cross(ydir, zdir)
        Ract = cols(xdir, ydir, zdir)
        Lact = float(np.linalg.norm(Pp - B))
        nm = "-y" if side < 0 else "+y"
        Rg = cols((1, 0, 0), (0, 1, 0), (0, 0, 1)) if side < 0 else cols((-1, 0, 0), (0, -1, 0), (0, 0, 1))
        add(Placement("p16_shelf", f"P16 shelf {nm} (printed, on the station post)", T(Rg, (STATION_RAIL_X, side * (POST_Y - EXT / 2), 0.0)), 8,
                      ORANGE, "station", (0, side * 40, -40)))
        add(Placement("clevis_bracket", f"P16 base clevis {nm} (printed, v4's)", T(None, B), 8, ORANGE, "station", (0, side * 40, -40)))
        y_head = -(SHOULDER_CLEVIS_L - 0.2) / 2
        add(Placement("clevis_screw", f"Shoulder screw 4 x 16 mm, M3 (P16 base pin {nm})", T(Rx(math.pi / 2), B + np.array([0, y_head, 0])), 8, STEEL,
                      "station", (0, side * 40, -40)))
        add(Placement("nut_m3_clevis", f"M3 locknut (P16 base pin {nm})", T(Rx(-math.pi / 2), B + np.array([0, y_head + SHOULDER_CLEVIS_L, 0])), 8,
                      STEEL, "station", (0, side * 40, -40)))
        add(Placement("actuator_body", f"Actuonix P16-150-22-12-P (pot feedback) {nm}", T(Ract, B), 8, (0.25, 0.25, 0.28), "station_act",
                      (0, side * 40, -40)))
        add(Placement("actuator_rod", f"Actuonix rod {nm}", T(Ract, B + zdir * (Lact - ACT_RETRACTED)), 8, (0.7, 0.7, 0.72), "station_act",
                      (0, side * 40, -40)))
        Rb = cols((1, 0, 0), (0, 1, 0), (0, 0, 1)) if side > 0 else cols((-1, 0, 0), (0, -1, 0), (0, 0, 1))
        C = electronics_frame(st.tilt, st.ext)
        Rc = C[:3, :3] @ cols((1, 0, 0), (0, -1, 0), (0, 0, -1))     # the EC's turn (tilt), with y and z back to the world's
        add(Placement("bar_end", f"Bar end block {nm} (printed: clamp, cheeks, guide shoe)", T(Rc @ Rb, Pp), 8, ORANGE, "station_ec",
                      (0, side * 40, -60)))
        # its shoulder screw from outside (head in the shoe's counterbore), its nylock between the inner cheek and the bar
        yh = side * (3.1 + 5.0)
        add(Placement("clevis_screw", f"Shoulder screw 4 x 16 mm, M3 (P16 rod end {nm})",
                      T(Rc, Pp + Rc @ np.array([0.0, yh, 0.0])) @ T(Rx(-side * math.pi / 2)), 8, STEEL, "station_ec", (0, side * 40, -60)))
        add(Placement("nut_m3_clevis", f"M3 locknut (P16 rod end {nm})",
                      T(Rc, Pp + Rc @ np.array([0.0, yh - side * SHOULDER_CLEVIS_L, 0.0])) @ T(Rx(side * math.pi / 2)), 8, STEEL, "station_ec",
                      (0, side * 40, -60)))
        Rg = cols((1, 0, 0), (0, 1, 0), (0, 0, 1)) if side < 0 else cols((-1, 0, 0), (0, -1, 0), (0, 0, 1))
        add(Placement("guide_block", f"Bar guide {nm} (printed, on the station post)", T(Rg, (STATION_RAIL_X, side * (POST_Y - EXT / 2), 0.0)), 8,
                      ORANGE, "station", (0, side * 40, 0)))
    C = electronics_frame(st.tilt, st.ext)
    _, Pp0 = actuator_pins(st.tilt, st.ext)
    add(Placement("lift_bar", "Lift bar, 8 mm precision steel shaft x 264 mm", T(C[:3, :3], (Pp0[0], 0.0, Pp0[2])), 8, STEEL, "station_ec",
                  (0, 0, -60)))
    add(Placement("sam_electronics_carriage", "Electronics carriage v5 (EC v4: Sam's Oct 13 turned over + arms round the auger, dock, door finger; saddles on the lift bar; printed)", C, 8, ELEC,
                  "station_ec", (0, 0, -60)))
    add(Placement("nema11", "NEMA 11 11HS18-0674S (auger drive)", C @ T(Ry(math.pi / 2), (NEMA11_X, 0, -NEMA11_Z)), 8, DARK, "station_ec", (0, 0, -60)))
    pin_ang = st.spin * 44.0 / 20.0
    add(Placement("pinion", "20T steel pinion (KHK SS1-20A, hub faced off)", C @ T(Ry(math.pi / 2), (PINION_X0, 0, -NEMA11_Z)) @ T(Rz(pin_ang)), 8,
                  ORANGE, "station_ec", (0, 0, -60)))
    add(Placement("solenoid", "Solenoid (Adafruit 412)", C @ T(Rx(math.pi), (SOL_X, 0, -SOL_Z)), 8, DARK, "station_ec", (0, 0, -60)))
    for nm_, c in P4.ec_ball_centres_v4().items():
        if nm_.startswith("base"):
            continue                                   # v5: no seat balls under the base (no cradle)
        add(Placement("kc_ball", f"Ball 1/4in chrome steel (EC, {nm_})", C @ T(None, c), 8, STEEL, "station_ec", (0, 0, -60)))
    for c in P4.vee_dowel_centres_v4():
        add(Placement("vee_dowel", "Dowel 1/8 x 5/16in (EC dock vee)", C @ T(None, c), 8, STEEL, "station_ec", (0, 0, -60)))
    for (x, y, zf) in P4.kc_magnet_faces_v4():
        add(Placement("kc_magnet", "Magnet D44-N52 (behind an EC dock contact)", C @ T(Rx(math.pi), (x, y, zf)), 8, MAGNET_RED, "station_ec", (0, 0, -60)))
    # 4a. the latch rail on its post
    LR = sam_frame(S, 0.0)
    add(Placement("latch_rail", "Latch rail and tube rest with their arm (printed)", LR, 8, ORANGE, "station", (0, 0, -40)))
    # v5: the rail's pad sits on the latch beam's end (frame), where v4's latch post ended


def _enclosure(st: State, add) -> None:
    """5. Clear acrylic on nylon standoffs outside the 2020 frame: both sides, front, back (deeper standoffs: the drive
    sprockets stand past the back posts) and top. The front hatch (under the station, for the scale) and the side hatch
    (+y, at the loading position) are hinged acrylic doors with magnetic catches."""
    x0, x1 = RAIL_X0, RAIL_X1
    yo = POST_Y + EXT / 2
    zt = Z_TOP_RAIL + EXT
    so = PANEL_STANDOFF
    back_so = X_DRV + LTB15 + 3.0 - x1            # past the drive sprocket's hub
    yp = yo + so + ACRYLIC_T                      # side panels' outer faces
    zl = load_frame()[2, 3]
    hs_w, hs_h = HATCH_SIDE
    hf_w, hf_h = HATCH_FRONT
    side_cut = (CHAIN_L / 2 - x0 - hs_w / 2, zl - hs_h / 2 - 1.0, CHAIN_L / 2 - x0 + hs_w / 2, zl + hs_h / 2 - 1.0)
    front_cut = front_hatch_cut()
    add(Placement("panel_side_hatch", "Side panel +y with the swap hatch (3 mm acrylic)", T(cols((1, 0, 0), (0, 0, 1), (0, -1, 0)), (x0, yp, 1.0)), 12,
                  ACRYL, "enclosure", (0, 120, 0)))
    add(Placement("panel_side", "Side panel -y (3 mm acrylic)", T(cols((1, 0, 0), (0, 0, 1), (0, -1, 0)), (x0, -yo - so, 1.0)), 12, ACRYL, "enclosure",
                  (0, -120, 0)))
    xf = x0 - so - ACRYLIC_T
    add(Placement("panel_front_hatch", "Front panel with the scale hatch (3 mm acrylic)", T(cols((0, 1, 0), (0, 0, 1), (1, 0, 0)), (xf, -yp, 1.0)), 12,
                  ACRYL, "enclosure", (-120, 0, 0)))
    xb = x1 + back_so
    add(Placement("panel_back", "Back panel (3 mm acrylic)", T(cols((0, 1, 0), (0, 0, 1), (1, 0, 0)), (xb, -yp, 1.0)), 12, ACRYL, "enclosure", (120, 0, 0)))
    add(Placement("panel_top", "Top panel (3 mm acrylic)", T(None, (xf, -yp, zt + so)), 12, ACRYL, "enclosure", (0, 0, 120)))
    # standoffs: along the posts and rails, every face
    for (xs, ys) in ((X_POST[0], -1), (X_POST[1], -1), (X_POST[0], 1), (X_POST[1], 1)):
        for z in (40.0, zt - 40.0, (zt) / 2):
            add(Placement("standoff", "Panel standoff, nylon 10 x 6", T(Rx(-ys * math.pi / 2), (xs, ys * yo, z)), 12, WHITE, "enclosure", (0, ys * 100, 0)))
    for ys in (-1, 1):
        for z in (40.0, zt - 40.0, zt / 2):
            add(Placement("standoff", "Panel standoff, nylon 10 x 6", T(Ry(-math.pi / 2), (x0, ys * POST_Y, z)), 12, WHITE, "enclosure", (-100, 0, 0)))
            add(Placement("standoff_back", "Panel standoff, nylon 10 x 30", T(Ry(math.pi / 2), (x1, ys * POST_Y, z)), 12, WHITE, "enclosure", (100, 0, 0)))
    # hatches: doors 4 mm over their openings, hinged on one edge, opening outward
    hf = T(cols((0, -1, 0), (0, 0, 1), (-1, 0, 0)), (xf, STATION_Y + hf_w / 2 + 4.0, HATCH_DOOR_Z0)) @ T(Ry(-math.radians(st.hatch_front)))
    add(Placement("hatch_front", "Front hatch door (3 mm acrylic, knob)", hf, 12, ACRYL, "enclosure", (-160, 0, 0)))
    hs = T(cols((0, 0, -1), (-1, 0, 0), (0, 1, 0)), (CHAIN_L / 2 + hs_w / 2 + 4.0, yp, zl + hs_h / 2 + 4.0)) @ T(Ry(-math.radians(st.hatch_side)))
    add(Placement("hatch_side", "Side hatch door (3 mm acrylic, knob)", hs, 12, ACRYL, "enclosure", (0, 160, 0)))
    for M, L_, nm in ((hf, HATCH_DOOR_H, "front"), (hs, hs_w + 8.0, "side")):
        for f in (0.2, 0.8):
            add(Placement("hinge_leaf", f"Hinge leaf (door, {nm} hatch)", M @ T(None, (0.0, f * L_, ACRYLIC_T)), 12, STEEL, "enclosure", (0, 0, 0)))
    for f in (0.2, 0.8):
        add(Placement("hinge_leaf", "Hinge leaf (panel, front hatch)", T(cols((0, 1, 0), (0, 0, 1), (-1, 0, 0)), (xf, STATION_Y + hf_w / 2 + 4.0, HATCH_DOOR_Z0 + f * HATCH_DOOR_H)),
                      12, STEEL, "enclosure", (-160, 0, 0)))
        add(Placement("hinge_leaf", "Hinge leaf (panel, side hatch)",
                      T(cols((0, 0, 1), (1, 0, 0), (0, 1, 0)), (CHAIN_L / 2 + hs_w / 2 + 4.0 - f * (hs_w + 8.0), yp, zl + hs_h / 2 + 4.0)), 12, STEEL,
                      "enclosure", (0, 160, 0)))
    add(Placement("catch", "Turn button (front hatch)", T(cols((0, 1, 0), (0, 0, 1), (-1, 0, 0)), (xf, STATION_Y - hf_w / 2 - 4.0 - 7.0, HATCH_DOOR_Z0 + HATCH_DOOR_H / 2)),
                  12, DARK, "enclosure", (-160, 0, 0)))
    add(Placement("catch", "Turn button (side hatch)", T(cols((1, 0, 0), (0, 0, -1), (0, 1, 0)), (CHAIN_L / 2, yp, zl - hs_h / 2 - 4.0 - 7.0)), 12,
                  DARK, "enclosure", (0, 160, 0)))


def _scale(st: State, add) -> None:
    """6, v5: the A&D HR-202i with its pan centre at the dose point (+ st.scale_offset), the display toward the front (-x),
    standing on the bench and touching nothing of the doser; on its pan the printed riser and the 25 mL beaker, rim 288 mm
    up. st.scale_model "hr100a" draws v4's HR-100A there instead (the lab's 102 g balance), for the fit check. The top
    door slides back (st.top_door, mm) while the station doses; the left side door (st.side_door) opens for the beaker."""
    px, py, _ = scale_pan_target()
    ox, oy = st.scale_offset
    M = T(None, (px + ox, py + oy, 0.0))
    if st.scale_model == "hr100a":
        add(Placement("hr100a_body", "A&D HR-100A balance (body)", M, 12, SCALE_GHOST, "scale", (-200, 0, 0)))
        add(Placement("hr100a_glass", "A&D HR-100A breeze break (glass)", M, 12, GLASS, "scale", (-200, 0, 0)))
        add(Placement("hr100a_pan", "A&D HR-100A pan", M, 12, STEEL, "scale", (-200, 0, 0)))
        z_pan = HR_PAN_Z
    else:
        add(Placement("hr202i_body", "A&D HR-202i balance (body, 220 g x 0.1 mg)", M, 12, WHITE, "scale", (-200, 0, 0)))
        add(Placement("hr202i_display", "A&D HR-202i display", M, 12, DARK, "scale", (-200, 0, 0)))
        add(Placement("hr202i_front_glass", "A&D HR-202i front glass", M, 12, GLASS, "scale", (-200, 0, 0)))
        add(Placement("hr202i_pan", "A&D HR-202i pan", M, 12, STEEL, "scale", (-200, 0, 0)))
        add(Placement("hr202i_door_left", "A&D HR-202i side door -y", M @ T(None, (st.side_door, 0, 0)), 12, GLASS, "scale", (-200, 0, 0)))
        add(Placement("hr202i_door_right", "A&D HR-202i side door +y", M, 12, GLASS, "scale", (-200, 0, 0)))
        add(Placement("hr202i_top_door", "A&D HR-202i top door", M @ T(None, (st.top_door, 0, 0)), 12, GLASS, "scale", (-200, 0, 0)))
        z_pan = HR2_PAN_TOP
    if st.beaker:
        zr = z_pan
        if st.scale_model != "hr100a":
            add(Placement("beaker_riser", "Beaker riser (printed PETG, on the pan)", M @ T(None, (0, 0, z_pan)), 12, ORANGE, "scale", (-200, 0, 60)))
            zr = z_pan + BEAKER_RISER_H - 5.0
        add(Placement("beaker", "Beaker, 25 mL low form", M @ T(None, (st.beaker_dx, st.beaker_dy, zr + st.beaker_dz)), 12, GLASS, "scale",
                      (-200, 0, 60)))


BUILDERS = {
    "ext_x": lambda: PT.extrusion_2020(RAIL_X1 - RAIL_X0),
    "ext_y": lambda: PT.extrusion_2020(2 * POST_Y - EXT),
    "ext_post": lambda: PT.extrusion_2020(Z_TOP_RAIL - Z_BASE - EXT),
    "riser": lambda: PT.extrusion_2020(RISER_H),
    "corner_bracket": PT.corner_bracket,
    "foot": PT.leveling_foot,
    "side_plate_front": lambda: side_plate_part(False),
    "side_plate_back": lambda: side_plate_part(True),
    "flange_bearing": PT.flange_bearing,
    "shaft": lambda: PT.shaft(SHAFT_L),
    "shaft_drive": lambda: PT.shaft(SHAFT_L + DRIVE_EXTRA),
    "tensioner_block": PT.tensioner_block,
    "sprocket_32": PT.sprocket_32,
    "sprocket_15_shaft": PT.sprocket_15_shaft,
    "sprocket_15_motor": PT.sprocket_15_motor,
    "nema34": PT.nema34,
    "chain_a1": PT.chain_a1_link,
    "chain_outer": PT.chain_outer_link,
    "chain_inner": PT.chain_inner_link,
    "carriage": P4.carriage_v4,
    "insert_m3": PT.heat_insert_m3,
    "insert_m5": lambda: cq.Workplane("XY").circle(3.5).circle(2.5).extrude(7.0),
    "magnet": PT.magnet,
    "hold_down": PT.hold_down,
    "hall_switch": PT.hall_switch,
    "m3x12_bhcs": lambda: PT.shcs(3, TAB_SCREW_L, "button"),
    "m3x6_fhcs": lambda: PT.shcs(3, 6, "flat"),
    "nut_m3": lambda: PT.locknut(3.0),
    "clevis_pin": PT.clevis_pin,
    "eclip": PT.eclip,
    "m5x12_bhcs": lambda: PT.shcs(5, 12, "button"),
    "m5x16_shcs": lambda: PT.shcs(5, 16),
    "m5x30_shcs": lambda: PT.shcs(5, 30),
    "bolt_m6x25": lambda: PT.shcs(6, 25),
    "nut_m6": lambda: PT.locknut(6.35),
    "m5x25_shcs": lambda: PT.shcs(5, 25),
    "m5x10_shcs": lambda: PT.shcs(5, 10),
    "m5x8_shcs": lambda: PT.shcs(5, 8),
    "ec_pin_screw": lambda: P3.shoulder_screw_4x20(),
    "ptfe_washer": lambda: cq.Workplane("XY").circle(4.5).circle(2.15).extrude(0.8),
    "nut_m5": lambda: PT.locknut(5.0),
    "tnut_m5": PT.tnut_m5,
    "board_panel": PT.board_panel,
    "lrs350": PT.lrs350,
    "cl86t": PT.cl86t,
    "raspberry_pi": PT.raspberry_pi,
    "perfboard": PT.perfboard,
    "lac": lambda: PT.box(50, 40, 12, 1),
    "estop": PT.estop,
    "sam_mounting_plate": lambda: reference_parts()["sam_mounting_plate"],
    "sam_electronics_carriage": lambda: reference_parts()["sam_electronics_carriage"],
    "auger": lambda: reference_parts()["auger"],
    "auger_cap": lambda: reference_parts()["auger_cap"],
    "clevis_bracket": lambda: PT.clevis_bracket(CLEVIS_RISE),
    "clevis_screw": PT.clevis_shoulder_screw,
    "nut_m3_clevis": lambda: PT.locknut(3.0),          # its own key: "nut_m3" moves with the chain in --sweep
    "actuator_body": lambda: PT.actuator_p16()[0],
    "actuator_rod": lambda: PT.actuator_p16()[1],
    "nema11": PT.nema11_envelope,
    "pinion": PT.pinion_20t,
    "solenoid": PT.solenoid_412,
    "dock_magnet": PT.dock_magnet,
    # ---- v3
    "armature_v3": P3.armature_v3,
    "kc_ball": P3.kc_ball,
    "vee_dowel": lambda: P3.dowel(L=7.94),
    "kc_magnet": P3.disc_magnet,
    "flat_pad": P3.steel_washer_flat,
    "cradle": lambda: P4.cradle_v4(*CRADLE_POST_S),
    "ext_cradle_post": lambda: PT.extrusion_2020(CRADLE_FLOOR_Z - (Z_BASE + EXT)),
    "latch_rail": lambda: P4.station_rails_v4(*LATCH_POST_S),
    "ext_latch_post": lambda: PT.extrusion_2020(HINGE_STATION[2] - P4.STATION_RAILS_OUTER - (Z_BASE + EXT)),
    "latch_bolt": P4.latch_bolt_v4,
    "latch_follower": P4.latch_follower_v4,
    "flat_pad_v4": P4.flat_pad_v4,
    "latch_spring": lambda: P3.spring(LATCH_SPRING[0], LATCH_SPRING[1] - 2.7, 0.3, 6),
    "door_housing": P4.door_housing_v4,
    "door_shutter": P4.door_shutter_v4,
    "door_spring": lambda: P3.spring(DOOR_SPRING[0], DOOR_SPRING_SHUT, 0.3, 7),
    "door_spring_open": lambda: P3.spring(DOOR_SPRING[0], DOOR_SPRING_SHUT - DOOR_TRAVEL, 0.25, 7),
    "m2x8_shcs": lambda: PT.shcs(2, 8),
    "side_tab": P3.side_tab,
    "side_tab_m": lambda: P3.side_tab().mirror("YZ"),
    "panel_side": lambda: P3.acrylic_panel(RAIL_X1 - RAIL_X0, Z_TOP_RAIL + EXT - 1.0),
    "panel_side_hatch": lambda: P3.acrylic_panel(RAIL_X1 - RAIL_X0, Z_TOP_RAIL + EXT - 1.0, cut=side_hatch_cut()),
    "panel_front_hatch": lambda: P3.acrylic_panel(2 * ENC_YP, Z_TOP_RAIL + EXT - 1.0, cut=front_hatch_cut()),
    "panel_back": lambda: P3.acrylic_panel(2 * ENC_YP, Z_TOP_RAIL + EXT - 1.0),
    "panel_top": lambda: P3.acrylic_panel(ENC_XB + ACRYLIC_T - ENC_XF, 2 * ENC_YP),
    "standoff": lambda: P3.standoff(PANEL_STANDOFF),
    "standoff_back": lambda: P3.standoff(ENC_BACK_SO),
    "hatch_front": lambda: P3.hatch_door(HATCH_FRONT[0] + 8.0, HATCH_DOOR_H),
    "hatch_side": lambda: P3.hatch_door(HATCH_SIDE[1] + 8.0, HATCH_SIDE[0] + 8.0),
    "hinge_leaf": P3.hinge_leaf,
    "catch": P3.turn_button,
    # ---- v5
    "ext_station_post": lambda: PT.extrusion_2020(STATION_POST_TOP - (Z_BASE + EXT)),
    "ext_latch_post5": lambda: PT.extrusion_2020(LATCH_BEAM_ZC + EXT / 2 - (Z_BASE + EXT)),
    "ext_latch_beam": lambda: PT.extrusion_2020(LATCH_BEAM_L),
    "p16_shelf": lambda: P5.p16_shelf(SHELF_TOP_Z),
    "guide_block": lambda: P5.guide_block(GUIDE_FLOOR_Z, GUIDE_TOP_Z),
    "bar_end": P5.bar_end,
    "lift_bar": P5.lift_bar,
    "hr202i_body": lambda: P5.hr202i()["hr202i_body"],
    "hr202i_display": lambda: P5.hr202i()["hr202i_display"],
    "hr202i_front_glass": lambda: P5.hr202i()["hr202i_front_glass"],
    "hr202i_pan": lambda: P5.hr202i()["hr202i_pan"],
    "hr202i_door_left": lambda: P5.hr202i()["hr202i_door_left"],
    "hr202i_door_right": lambda: P5.hr202i()["hr202i_door_right"],
    "hr202i_top_door": lambda: P5.hr202i()["hr202i_top_door"],
    "beaker_riser": P5.beaker_riser,
    "hr100a_body": lambda: P3.hr100a()[0],
    "hr100a_glass": lambda: P3.hr100a()[1],
    "hr100a_pan": lambda: P3.hr100a()[2],
    "beaker": P3.beaker,
}


# enclosure geometry shared by _enclosure and the panel builders
ENC_YP = POST_Y + EXT / 2 + PANEL_STANDOFF + ACRYLIC_T          # side panels' outer faces
ENC_XF = RAIL_X0 - PANEL_STANDOFF - ACRYLIC_T                   # front panel's outer face
ENC_BACK_SO = X_DRV + LTB15 + 3.0 - RAIL_X1                     # back standoffs: past the drive sprocket's hub
ENC_XB = RAIL_X1 + ENC_BACK_SO                                  # back panel's inner face


def side_hatch_cut() -> tuple:
    """The +y panel's swap opening, panel coordinates (x from RAIL_X0, y from z = 1)."""
    zl = load_frame()[2, 3]
    w, h = HATCH_SIDE
    return (CHAIN_L / 2 - RAIL_X0 - w / 2, zl - h / 2 - 1.0, CHAIN_L / 2 - RAIL_X0 + w / 2, zl + h / 2 - 1.0)


def front_hatch_cut() -> tuple:
    """v5: the front panel's opening, panel coordinates (x from y = -ENC_YP, y from z = 1): from the bench up, so the
    HR-202i's display unit pokes out under the hatch door (a brush strip closes the gap round it)."""
    w, h = HATCH_FRONT
    return (STATION_Y + ENC_YP - w / 2, -2.0, STATION_Y + ENC_YP + w / 2, h - 1.0)


HATCH_DOOR_Z0 = HR2_NOSE[1] + 12.0                # v5: the front hatch door's bottom edge, over the balance's display unit
HATCH_DOOR_H = HATCH_FRONT[1] - HATCH_DOOR_Z0 + 4.0


# The vendors' own STEP files (McMaster screws and nuts, Actuonix's P16, StepperOnline's NEMA 34) are git-ignored
# (cad/vendor/files/, no licence to redistribute); v2's committed per-part STEPs carry the same geometry in the same
# builder frames, so v3 reads those when cad/vendor/files/ isn't on disk.
V2_COMPONENTS = HERE.parent / "chain-carousel-v2" / "step" / "components"
VENDOR_KEYS = ("actuator_body", "actuator_rod", "nema34", "m3x12_bhcs", "m3x6_fhcs", "m5x10_shcs", "m5x12_bhcs", "m5x16_shcs", "m5x25_shcs",
               "nut_m3", "nut_m5", "nut_m6", "clevis_screw")
VENDOR_FILES = HERE.parent / "vendor" / "files"


@lru_cache(None)
def shape(key: str) -> cq.Shape:
    if key in VENDOR_KEYS or key == "nut_m3_clevis":
        src = V2_COMPONENTS / f"{'nut_m3' if key == 'nut_m3_clevis' else key}.step"
        if not VENDOR_FILES.exists() and src.exists():
            s = cq.importers.importStep(str(src))
            vals = s.vals()
            return vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals)
    w = BUILDERS[key]()
    vals = w.vals()
    return vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals)


def moved(key: str, M: np.ndarray) -> cq.Shape:
    from OCP.gp import gp_Trsf
    from OCP.TopLoc import TopLoc_Location
    tr = gp_Trsf()
    tr.SetValues(*[float(v) for v in M[:3, :].ravel()])
    return cq.Shape.cast(shape(key).wrapped.Moved(TopLoc_Location(tr)))


if __name__ == "__main__":
    p = chain_pins()
    print("pins:", len(p), "; carriage links:", carriage_links(), "; station y =", round(STATION_Y, 2), "; load slot", LOAD_SLOT)
    print("loop pitch-line box: y +-%.1f, z %.1f-%.1f" % (LOOP_Y + R, Z_BOT - R, Z_TOP + R))
    print("shaft clearance to the gear: %.2f mm" % SHAFT_CLEAR)
    print("station hinge", np.round(HINGE_STATION, 2), "base clevis pin z %.2f (rise above rail %.2f)" % (CLEVIS_PIN_Z, CLEVIS_RISE))
    print("cradle floor z %.1f; dose point %s; scale pan target %s" % (CRADLE_FLOOR_Z, np.round(DOSE_POINT, 2), np.round(scale_pan_target(), 2)))
    pl = placements()
    from collections import Counter
    print(len(pl), "placements;", Counter(x.key for x in pl).most_common(16))
