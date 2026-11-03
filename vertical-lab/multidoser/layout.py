"""Where every part goes: the chain solution, the 13 carriages, the frame,
the station and the assembly steps (v2, vertical twin-chain loop).

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
import kinematics as K

HERE = Path(__file__).resolve().parent
REF = HERE / "reference"            # Sam's Onshape export, the lab auger

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
    for sy in (-1, 1):                                                              # to the posts' slots
        for z in zs:
            out.append(("circle", (sy * POST_Y, z), (5.5,)))
    for dy in (-12.0, 12.0):                                                        # hold-down, into its inserts:
        out.append(("slot", (STATION_Y + dy, Z_RUN + CAR_W0 - CAR_T - HOLD_DOWN_FOOT_GAP - 11.0), (5.5, 9.5)))   # +-2 mm to set the lip gap
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
    """Sam's Oct 13 mounting plate and electronics carriage (his Onshape Part Studio, the latest), and the lab's
    threaded-storage auger + cap (PR #170). Sam's parts are in his studio frame (hinge axis = his y axis at
    x = z = 0); the auger runs along +z from its outlet end. The plate gets the two M3 insert holes for the
    dock magnet's steel armature in its back strip."""
    out = {}
    sam = _read_step_parts(REF / "sam-oct13-mounting-plate-and-carriage.step")
    plate = cq.Workplane("XY").add(sam["Mounting Plate"])
    for x, y in ARMATURE_SCREWS:
        plate = plate.cut(cq.Workplane("XY").center(x, y).circle(2.0).extrude(4.5).translate((0, 0, -18.01)))
    (hx, hy), (sx, sy) = LOCPIN_XY                     # locating-pin hole and slot (along x) in the underside
    plate = plate.cut(cq.Workplane("XY").center(hx, hy).circle(LOCPIN_HOLE / 2).extrude(3.5).translate((0, 0, -18.01)))
    plate = plate.cut(cq.Workplane("XY").center(sx, sy).slot2D(LOCPIN_SLOT, LOCPIN_HOLE, 0).extrude(3.5).translate((0, 0, -18.01)))
    out["sam_mounting_plate"] = plate
    out["sam_electronics_carriage"] = cq.Workplane("XY").add(sam["Carriage"])
    aug = _read_step_parts(REF / "auger-threaded-storage.step")
    out["auger"] = cq.Workplane("XY").add(next(iter(aug.values())))
    cap = _read_step_parts(REF / "auger-cap-threaded.step")
    out["auger_cap"] = cq.Workplane("XY").add(next(iter(cap.values())))
    return out


SAM_IN_CARRIAGE = T(cols((0, 0, 1), (1, 0, 0), (0, 1, 0)), (0.0, HINGE_W, HINGE_X))   # his x -> x, y -> u, z -> w
AUGER_IN_SAM = T(Ry(math.pi / 2), (AUGER_Z0_XS, 0, 0))


def sam_frame(carriage_M: np.ndarray, tilt_deg: float = 0.0) -> np.ndarray:
    """Sam's studio frame on a carriage. Positive tilt lifts the cap end into the loop (outlet down), about the hinge."""
    return carriage_M @ SAM_IN_CARRIAGE @ T(Ry(-math.radians(tilt_deg)))


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
    """Sam's frame of the electronics carriage: docked (rim on the plate) and tilting with the module, or lowered
    by DOCK_EXT - ext on the approach."""
    H = T(None, HINGE_STATION)
    if tilt_frame > 0 or ext >= DOCK_EXT:
        return H @ T(Ry(-math.radians(tilt_frame))) @ T(None, (0, 0, DOCK_RISE))
    return H @ T(None, (0, 0, DOCK_RISE - (DOCK_EXT - ext)))


def actuator_pins(tilt_frame: float, ext: float) -> tuple[np.ndarray, np.ndarray]:
    """(base pin B, carriage pin P) of the P16 and its U-yoke, frame coordinates. The P16's rod-end hole is UFORK_L
    short of P on the same axis; B sits directly under the docked carriage pin, so the approach is vertical."""
    pin_dock = to_world(electronics_frame(0.0, DOCK_EXT), (YOKE_X, 0.0, YOKE_Z))
    B = pin_dock - np.array([0.0, 0.0, ACT_RETRACTED + DOCK_EXT + UFORK_L])
    Pp = to_world(electronics_frame(tilt_frame, ext), (YOKE_X, 0.0, YOKE_Z))
    return B, Pp


STATION_RAIL_X = HINGE_X + YOKE_X                  # 2020 cross rail under the actuator (along y)
_B0 = actuator_pins(0.0, DOCK_EXT)[0]
CLEVIS_PIN_Z = float(_B0[2])
CLEVIS_RISE = CLEVIS_PIN_Z - (Z_BASE + EXT)        # base clevis pin above the station rail's top
FORK_POST_Y = STATION_Y + 40.0
TONGUE_Z0 = YOKE_Z - UFORK_L - 6.0 - 25.0          # tongue's bottom (Sam's frame, docked actuator vertical)
FORK_TOP = float(to_world(electronics_frame(0.0, DOCK_EXT), (TONGUE_X, 0, TONGUE_Z0))[2]) - 1.0   # 1 mm under the docked tongue
FORK_Z = FORK_TOP - FORK_H


def exit_point(tilt_frame: float) -> np.ndarray:
    """Auger exit (the Ø3 hole on the axis at the outlet plane), frame coordinates."""
    return to_world(sam_frame(station_frame(), tilt_frame), (AUGER_Z0_XS, 0.0, 0.0))


def stream_point(z: float, tilt_frame: float, pitch_deg: float = FRAME_PITCH_DEG) -> np.ndarray:
    """Where the falling powder crosses frame height z: it falls along the bench's vertical, which in the
    pitched frame leans toward +x by tan(pitch)."""
    e = exit_point(tilt_frame)
    a = math.radians(pitch_deg)
    return np.array([e[0] + (e[2] - z) * math.tan(a), e[1], z])


CARR_FRONT_X = float(HINGE_STATION[0] + 2.33)      # docked/approaching electronics carriage's front face (Sam x 2.33)
FUNNEL_TOP = Z_RUN + CAR_W0 - CAR_T - 1.5          # under every passing carriage plate
FUNNEL_CUT_X = CARR_FRONT_X - 1.0                  # D-cut mouth, 1 mm ahead of the docked electronics carriage
VIAL_XY = (FUNNEL_CUT_X - 16.0, STATION_Y)
FUNNEL_SPOUT_Z = FUNNEL_TOP - FUNNEL["h"]
VIAL_Z = FUNNEL_SPOUT_Z + 5.0 - VIAL_H             # spout 5 mm into the vial's mouth
CUP_Z = VIAL_Z - 3.0
LC_TOP = CUP_Z
VIAL_POST_Y = -POST_Y + 2.0                        # post on the -y base rail
LC_Y0 = VIAL_XY[1] - (30.0 + VIAL_D / 2 + 1) - LC_L   # load cell's fixed end (y), cup arm toward +y
WEDGE_Z = LC_TOP - 12.7 - 6.0 - 40.0 * math.tan(math.radians(FRAME_PITCH_DEG)) / 2   # top of the vial post
VIAL_PIVOT = np.array([VIAL_XY[0], VIAL_POST_Y, WEDGE_Z])   # the gravity-referenced group turns about the wedge


def stream_check(pitch_deg: float = FRAME_PITCH_DEG, world_tilt: float = TILT_DOSE_WORLD) -> dict:
    """Does the dose stream land inside the funnel's D-cut mouth? (frame coordinates)"""
    tf = frame_dose_tilt(world_tilt, pitch_deg)
    s = stream_point(FUNNEL_TOP, tf, pitch_deg)
    r = FUNNEL["top_d"] / 2
    inside = (s[0] <= FUNNEL_CUT_X - 0.5) and math.hypot(s[0] - VIAL_XY[0], s[1] - VIAL_XY[1]) < r - 1.0
    return dict(pitch=pitch_deg, frame_tilt=tf, stream_x=round(float(s[0]), 2), cut_x=round(FUNNEL_CUT_X, 2),
                margin_mm=round(FUNNEL_CUT_X - 0.5 - float(s[0]), 2), inside=bool(inside))


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
    ext: float = DOCK_EXT                 # actuator extension at tilt 0 (0 retracted, DOCK_EXT docked)
    station: bool = True
    spin: float = 0.0                     # auger turn at the station, rad (pinion turns -spin * 44/20)
    tap: float = 0.0                      # solenoid plunger travel, mm
    magnet_on: bool = False
    out_carriage: int = -1                # carriage coming off/going on at the loading position
    out_slide: float = 0.0                # mm along +u (frees the hooks from the tabs)
    out_lift: float = 0.0                 # mm outward, away from the loop
    screws_out: float = 0.0               # its two tab screws backed out by (mm)
    tension: float = 0.0                  # top shafts' offset, mm
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
    1: "Base frame: rails, station rail, corner brackets, leveling feet and front risers",
    2: "Posts and top frame",
    3: "Side plates onto the posts",
    4: "Flange bearings and top-shaft tensioners on the side plates",
    5: "Corner shafts with their sprockets (back set screws loose)",
    6: "NEMA 34 on the back plate, 15T sprockets, drive chain",
    7: "Chains: 13 A-1 links per chain, close both loops",
    8: "Station: hold-downs, hall switches, actuator, electronics carriage with dock magnet, approach fork, vial on the load cell",
    9: "Modules on the bench: auger into Sam's plate (the carrier), steel armature tab, plate pinned onto a carriage",
    10: "Carriages onto the chain at the loading position, one index at a time; phase and tension",
    11: "Electronics board: supply, driver, Pi, interface board, LAC, e-stop",
}

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
    for xp in X_POST:
        add(Placement("ext_y", f"Base cross rail {'front' if xp < 0 else 'back'}",
                      T(Rx(-math.pi / 2), (xp, -L_y / 2, (zr0 + zr1) / 2)), 1, ALU, "frame", (0, 0, -60)))
    add(Placement("ext_y", "Station rail (actuator)", T(Rx(-math.pi / 2), (STATION_RAIL_X, -L_y / 2, (zr0 + zr1) / 2)), 1, ALU, "frame",
                  (0, 0, -60)))
    for sy in (-1, 1):
        add(Placement("corner_bracket", "Corner bracket (station rail)",
                      bracket((STATION_RAIL_X + EXT / 2, sy * (POST_Y - EXT / 2), zr1), (0, 0, 1), (0, -sy, 0)), 1, ALU, "frame", (0, 0, 40)))
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
        if k not in st.modules:
            continue
        tilt = st.tilt if (k == k_st and st.station) else 0.0
        Ms = sam_frame(C, tilt)
        add(Placement("sam_mounting_plate", f"Mounting plate (Sam, Oct 13) {k + 1}", Ms, 9, SAM, "modules", out_dir, k))
        add(Placement("armature_tab", f"Armature tab, 2 mm steel {k + 1}", Ms, 9, STEEL, "modules", out_dir, k))
        for x, y in ARMATURE_SCREWS:
            add(Placement("m3x6_fhcs", f"Armature screw M3x6 flat head {k + 1}", Ms @ T(Rx(math.pi), (x, y, -18.0 - ARMATURE_T)), 9, DARK,
                          "modules", out_dir, k))
            add(Placement("insert_m3", f"M3 heat-set insert (plate) {k + 1}", Ms @ T(None, (x, y, -18.0)), 9, BRASS, "modules", out_dir, k))
        spin = st.spin if (k == k_st and st.station) else 0.0
        Ma = Ms @ AUGER_IN_SAM @ T(Rz(spin))
        add(Placement("auger", f"Auger, threaded storage {k + 1}", Ma, 9, WHITE, "modules", out_dir, k))
        add(Placement("auger_cap", f"Auger cap {k + 1}", Ma @ T(None, (0, 0, AUGER_LEN)), 9, WHITE, "modules", out_dir, k))
        for su in (-1, 1):
            u_head = su * (LUG_U + LUG_T - PIN_CBORE[1])
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
    out += st.extra
    return out


def _station(st: State, add) -> None:
    """Hold-downs and hall switches at the station tongues, the P16 on its clevis, Sam's electronics carriage on
    the yoke with the NEMA 11, pinion, solenoid and dock magnet, the approach fork, and the vial on its load cell
    (the vial group stays plumb: it is turned back by the frame pitch about the wedge on the post)."""
    S = station_frame()
    HDf = T(cols((0, 1, 0), (0, 0, 1), (1, 0, 0)), (-SIDE_GAP, STATION_Y, Z_RUN))
    HDb = T(cols((0, -1, 0), (0, 0, 1), (-1, 0, 0)), (CHAIN_L + SIDE_GAP, STATION_Y, Z_RUN))
    tz = CAR_W0 + HOLD_DOWN_GAP
    zc = SIDE_GAP + CAR_X0 + 7.0
    Rsw = cols((1, 0, 0), (0, 0, -1), (0, 1, 0))
    for HD, nm, sgn in ((HDf, "front, INDEX", -1), (HDb, "back, HOME", 1)):
        add(Placement("hold_down", f"Hold-down ({nm.split(',')[0]}, printed)", HD, 8, ORANGE, "station", (0, 0, 60)))
        add(Placement("hall_switch", f"Hall switch US5881 ({nm.split(', ')[1]})", HD @ T(Rsw, (0, tz + 0.8, zc)), 8, DARK, "station", (0, 0, 90)))
        for dy in (-12.0, 12.0):
            p = to_world(HD, (dy, CAR_W0 - CAR_T - HOLD_DOWN_FOOT_GAP - 11.0, 0.0))
            xo = X_BACK_OUT if sgn > 0 else X_FRONT_OUT
            add(Placement("m5x16_shcs", "Hold-down screw M5x16", T(Ry(sgn * math.pi / 2), (xo, p[1], p[2])), 8, DARK, "station", (sgn * 60, 0, 0)))
            add(Placement("insert_m5", "M5 heat-set insert (hold-down)", HD @ T(None, (dy, CAR_W0 - CAR_T - HOLD_DOWN_FOOT_GAP - 11.0, 0.0)), 8, BRASS,
                          "station", (0, 0, 60)))
    # actuator, pinned at both ends
    B, Pp = actuator_pins(st.tilt, st.ext)
    zdir = (Pp - B) / np.linalg.norm(Pp - B)
    ydir = np.array([0.0, 1.0, 0.0])
    xdir = np.cross(ydir, zdir)
    Ract = cols(xdir, ydir, zdir)
    Lact = float(np.linalg.norm(Pp - B))
    add(Placement("clevis_bracket", "Actuator base clevis (printed)", T(None, B), 8, ORANGE, "station", (0, 0, -40)))
    add(Placement("actuator_body", "Actuonix P16-150-22-12-P (pot feedback)", T(Ract, B), 8, (0.25, 0.25, 0.28), "station", (0, 0, -40)))
    add(Placement("actuator_rod", "Actuonix rod", T(Ract, B + zdir * (Lact - UFORK_L - ACT_RETRACTED)), 8, (0.7, 0.7, 0.72), "station", (0, 0, -40)))
    Y = T(Ract, Pp)                                     # yoke frame: on the carriage pins' axis, along the actuator
    add(Placement("uyoke_base", "U-yoke crossbar with guide tongue (printed)", Y, 8, ORANGE, "station", (0, 0, -60)))
    for sy in (-1, 1):
        Rm = T(None) if sy > 0 else T(Rz(math.pi))           # part's +y outward
        add(Placement("uyoke_arm", "U-yoke arm, 2 mm steel (laser cut)", Y @ T(None, (0, sy * UFORK_Y[0], 0)) @ Rm, 8, STEEL, "station", (0, 0, -60)))
        add(Placement("yoke_stop" if sy > 0 else "yoke_stop_m", f"Yoke stop block {'+' if sy > 0 else '-'}y (printed, on the arm)",
                      Y @ T(None, (0, sy * UFORK_Y[0], 0)), 8, ORANGE, "station", (0, 0, -60)))
    C = electronics_frame(st.tilt, st.ext)
    add(Placement("sam_electronics_carriage", "Electronics carriage (Sam, Oct 13)", C, 8, ELEC, "station", (0, 0, -60)))
    for sy in (-1, 1):
        Rq = T(Rz(math.pi)) if sy < 0 else T(None)          # part's +y outward
        add(Placement("pin_boss" if sy > 0 else "pin_boss_m", f"Stub-pin plate with tail {'+' if sy > 0 else '-'}y (printed, bonded to the side post)",
                      C @ T(None, (YOKE_X, sy * 18.0, YOKE_Z)), 8, ORANGE, "station", (0, 0, -60)))
        add(Placement("stub_pin", "Stub pin 4 mm, steel, e-clip groove", C @ T(None, (YOKE_X, sy * 15.3, YOKE_Z)) @ Rq, 8, STEEL, "station", (0, 0, -60)))
        add(Placement("eclip_stub", "E-clip DIN 6799-3.2 (stub pin)", C @ T(None, (YOKE_X, sy * 22.3, YOKE_Z)) @ T(Rx(-sy * math.pi / 2)), 8, DARK,
                      "station", (0, 0, -60)))
    add(Placement("nema11", "NEMA 11 11HS18-0674S (auger drive)", C @ T(Ry(math.pi / 2), (NEMA11_X, 0, NEMA11_Z)), 8, DARK, "station", (0, 0, -60)))
    pin_ang = -st.spin * 44.0 / 20.0
    add(Placement("pinion", "20T steel pinion (KHK SS1-20A, hub faced off)", C @ T(Ry(math.pi / 2), (PINION_X0, 0, NEMA11_Z)) @ T(Rz(pin_ang)), 8, ORANGE,
                  "station", (0, 0, -60)))
    add(Placement("solenoid", "Solenoid (Adafruit 412)", C @ T(None, (SOL_X, 0, SOL_Z + st.tap * 0.0)), 8, DARK, "station", (0, 0, -60)))
    add(Placement("magnet_bracket", "Dock magnet bracket (printed)", C, 8, ORANGE, "station", (0, 0, -60)))
    for (x, y) in LOCPIN_XY:
        add(Placement("loc_pin", "Locating pin 4 mm, conical tip (carriage rim)", C @ T(None, (x, y, -18.9 - 5.0)), 8, STEEL, "station", (0, 0, -60)))
    add(Placement("dock_magnet", "Dock electromagnet Adafruit 3872 (P20/15)", C @ T(None, (DOCK_MAG_XY[0], DOCK_MAG_XY[1], DOCK_MAG_FACE_Z)), 8,
                  MAGNET_RED if st.magnet_on else DARK, "station", (0, 0, -60)))
    # approach fork on its post
    add(Placement("fork", "Approach fork (printed)", T(None, (HINGE_STATION[0] + TONGUE_X, STATION_Y + TONGUE_Y, FORK_Z)), 8, ORANGE, "station", (0, 0, -40)))
    add(Placement("ext_fork_post", "Fork post (2020)", T(None, (STATION_RAIL_X, FORK_POST_Y, Z_BASE + EXT)), 8, ALU, "station", (0, 0, -40)))
    add(Placement("fork_arm", "Fork arm (printed)", T(None, (HINGE_STATION[0] + TONGUE_X, STATION_Y + TONGUE_Y, FORK_Z)), 8, ORANGE, "station", (0, 0, -40)))
    # vial, funnel, cup and load cell: plumb on the bench, so turned back by the pitch about the wedge on the post
    G = T(None, VIAL_PIVOT) @ T(Ry(-math.radians(FRAME_PITCH_DEG))) @ T(None, -VIAL_PIVOT)
    add(Placement("ext_vial_post", "Vial post (2020)", T(None, (VIAL_XY[0], VIAL_POST_Y, Z_BASE + EXT)), 8, ALU, "dispense", (0, 0, -40)))
    add(Placement("level_wedge", "Level wedge on the vial post (printed)", T(None, VIAL_PIVOT), 8, ORANGE, "dispense", (0, 0, -40)))
    add(Placement("load_cell", "Load cell 100 g (TAL221)", G @ T(Rz(math.pi / 2), (VIAL_XY[0], LC_Y0, LC_TOP - 12.7)), 8, (0.7, 0.7, 0.75), "dispense", (0, -30, 0)))
    add(Placement("vial_cup", "Vial cup on the load cell (printed)", G @ T(Rz(math.pi / 2), (VIAL_XY[0], VIAL_XY[1], CUP_Z)), 8, ORANGE, "dispense", (0, 0, 40)))
    add(Placement("vial", "Vial, 20 mL", G @ T(None, (VIAL_XY[0], VIAL_XY[1], VIAL_Z)), 8, GLASS, "dispense", (0, 0, 60)))
    add(Placement("vial_funnel", "Catch funnel, D-cut (printed)", G @ T(None, (VIAL_XY[0], VIAL_XY[1], FUNNEL_SPOUT_Z)), 8, ORANGE, "dispense", (0, 0, 60)))


BUILDERS = {
    "ext_x": lambda: PT.extrusion_2020(RAIL_X1 - RAIL_X0),
    "ext_y": lambda: PT.extrusion_2020(2 * POST_Y - EXT),
    "ext_post": lambda: PT.extrusion_2020(Z_TOP_RAIL - Z_BASE - EXT),
    "ext_fork_post": lambda: PT.extrusion_2020(FORK_Z - 6.0 - (Z_BASE + EXT)),
    "ext_vial_post": lambda: PT.extrusion_2020(WEDGE_Z - (Z_BASE + EXT)),
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
    "carriage": PT.carriage,
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
    "eclip_stub": PT.eclip_stub,
    "m5x12_bhcs": lambda: PT.shcs(5, 12, "button"),
    "m5x16_shcs": lambda: PT.shcs(5, 16),
    "m5x30_shcs": lambda: PT.shcs(5, 30),
    "bolt_m6x25": lambda: PT.shcs(6, 25),
    "nut_m6": lambda: PT.locknut(6.35),
    "m5x25_shcs": lambda: PT.shcs(5, 25),
    "m5x10_shcs": lambda: PT.shcs(5, 10),
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
    "armature_tab": PT.armature_tab,
    "clevis_bracket": lambda: PT.clevis_bracket(CLEVIS_RISE),
    "actuator_body": lambda: PT.actuator_p16()[0],
    "actuator_rod": lambda: PT.actuator_p16()[1],
    "uyoke_base": PT.uyoke_base,
    "uyoke_arm": PT.uyoke_arm,
    "stub_pin": PT.stub_pin,
    "yoke_stop": PT.yoke_stop,
    "yoke_stop_m": PT.yoke_stop_m,
    "pin_boss": PT.pin_boss,
    "pin_boss_m": PT.pin_boss_m,
    "nema11": PT.nema11_envelope,
    "pinion": PT.pinion_20t,
    "solenoid": PT.solenoid_412,
    "magnet_bracket": PT.magnet_bracket,
    "loc_pin": PT.loc_pin,
    "dock_magnet": PT.dock_magnet,
    "fork": PT.approach_fork,
    "fork_arm": lambda: _fork_arm(),
    "vial": PT.vial,
    "vial_cup": PT.vial_cup,
    "vial_funnel": lambda: PT.vial_funnel(FUNNEL_CUT_X - VIAL_XY[0]),
    "load_cell": PT.load_cell,
    "level_wedge": PT.level_wedge,
}


def _fork_arm() -> cq.Workplane:
    """Printed arm from the fork post (x = STATION_RAIL_X, y = FORK_POST_Y) to the fork (frame at the fork's slot centre)."""
    y0, y1 = 14.5, FORK_POST_Y - (STATION_Y + TONGUE_Y) - 10.0
    x0 = STATION_RAIL_X - (HINGE_STATION[0] + TONGUE_X) - 10.0
    return cq.Workplane("XY").box(20.0, y1 - y0, 12.0, centered=False).translate((x0, y0, -6.0))


@lru_cache(None)
def shape(key: str) -> cq.Shape:
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
    print("fork z %.1f-%.1f; funnel top %.2f cut x %.2f; vial base z %.2f; riser %.1f mm" % (FORK_Z, FORK_TOP, FUNNEL_TOP, FUNNEL_CUT_X, VIAL_Z, RISER_H))
    for pd in (0.0, 2.0, 2.5, 5.0, 8.0):
        print("stream", stream_check(pd))
    pl = placements()
    from collections import Counter
    print(len(pl), "placements;", Counter(x.key for x in pl).most_common(16))
