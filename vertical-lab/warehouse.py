"""The warehouse version (#303, round 4): the VLM and the floor machines on an open warehouse floor, served by MiR250
mobile bases carrying UR10e arms that drive between docking spots, instead of a rail along a line.

    xvfb-run -a python3 warehouse.py            # -> out/warehouse.gif, out/mp4/warehouse.mp4, out/warehouse_still.png
    PREVIEW=1 xvfb-run -a python3 warehouse.py  # the last frame of each sub-step -> /tmp/preview_warehouse.png
    python3 warehouse.py sway                   # low rail + pedestal, beam rail, MiR250 -> out/rail_vs_amr.json
    xvfb-run -a python3 warehouse.py compare    # the three side by side -> out/rail_vs_amr.png

The floor plan is data (``STATIONS``, ``CHARGERS``, ``RACKS``) so ``setup_lab.py`` builds the same floor. A model that
another module adds later (the DED machine and the packaging station, keys ``ded`` and ``packaging``; a HIP, ``hip``)
takes its reserved spot when ``tour.load()`` returns it; until then the DED and packaging spots are labelled footprints.

Every MiR figure is from MiR's own specification sheet, "MiR250 Specifications", dated 2023-06-28, as hosted by the
MiR distributor Hartfiel (https://www.hartfiel.com/wp-content/uploads/2024/04/MiR250-Specs.pdf). Every UR10e figure is
from UR's UR10e data sheet (October 2026) and the UR10e user manual for software 5.26, section 6.2, "Dimensioning the
Stand":
https://www.universal-robots.com/manuals/EN/PDF/SW5_26/user-manual-UR10e-PDF_online/711-039-00_UR10e_User_Manual_en_Global.pdf
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np
import pyvista as pv

import animate as A
import lab
import line
import props as P
import tour
import vlm as V
from scene import FPS, OUT, PREVIEW, Scene, T, R

TITLE = "Vertical cloud lab, warehouse version: MiR250 + UR10e on an open floor"

# ============================================================================================ sourced figures
MIR250 = dict(                    # MiR250 Specifications, 2023-06-28 (see the module docstring)
    size_mm=(800, 580, 300), mass_kg=97, payload_kg=250, max_speed_m_s=2.0,
    corridor_mm=1450,             # operational corridor width, default footprint and SICK safety configuration
    corridor_two_mm=3000,         # two robots passing, default setup (2100-2450 with the dynamic setups)
    turn90_mm=1500, uturn_mm=1600, pivot_mm=1800,
    dock_L_mm_deg=(6, 3, 1.0),    # docking to an L-marker: +-6 mm along x, +-3 mm along y, +-1 deg yaw
    dock_VL_mm=(3, 3),            # docking to a VL-marker: +-3 mm, +-3 mm
    dock_V_mm_deg=(9, 17, 3.0),
    position_mm_deg=(60, 85, 4.0),  # "moving to position", no marker: +-60 mm, +-85 mm, +-4 deg
    charger_gap_mm=450, charger_front_mm=2800, charger_side_mm=550, charge_10_90_min=52,
)
CHARGER = dict(W=622.0, D=237.0, H=287.0, D_plate=487.0)   # MiR Charge 48V, W x D x H, and the depth with its
# charging plate: Konica Minolta's and IDEC's (MiR distributors) listings; 20 kg
UR10E = dict(payload_kg=12.5, reach_mm=1300, mass_kg=33.3, repeat_mm=0.05,            # UR10e data sheet, Oct 2026
             # UR10e manual 6.2: worst-case loads on the stand x a safety factor of 2.5: Mz [Nm], Fz [N], Mxy [Nm],
             # Fxy [N]
             stand_stop=(990, 1700, 1460, 1160), stand_run=(830, 1450, 860, 860), safety=2.5, stand_min_hz=45)
VENTION_REPEAT_MM = 0.3           # Vention rack and pinion actuator, repeatability including backlash, +-0.3 mm
# (docs.vention.com/docs/rack-and-pinon-actuator; 0.25 mm backlash; 4000 mm/s without gearbox)

# ============================================================================================ the floor plan
# x along the main aisle, y away from it; the VLM at the origin, its front face on line.Y_FACE (as in every scene)
Y_FACE_N = line.Y_FACE                         # -1562: the north row's fronts
DOCK_N = A.AMR_XY[1]                           # -1932: a MiR250 docked at a north-row station, as at the VLM before
AISLE = (DOCK_N - 468.0, DOCK_N - 468.0 - MIR250["corridor_two_mm"])   # (-2400, -5400): 3.0 m, two MiR250s pass
Y_FACE_S = AISLE[1] - 468.0 - (Y_FACE_N - DOCK_N)                      # -6238: the south row's fronts, facing north
DOCK_S = Y_FACE_S + (Y_FACE_N - DOCK_N)                                # -5868
X_END = (-10200.0, 10200.0)                    # the ends of the marked aisle

# station key: (x of its centre, row, turn of the machine about z in degrees, dock x). SETBACK moves a machine back
# from its row's front line (the glovebox, so the arm has room to reach level into its antechamber). The north row faces
# south
# (towards -y), the south row north. The glovebox is turned so its automatic antechamber faces the aisle and the arm;
# its glove ports face west, where people work.
STATIONS = {
    "glovebox": (-7300.0, "N", -90.0, -7300.0),
    "repowder": (None, "N", 0.0, -3640.0),       # placed by animate.Lab at REPOWDER_AT
    "vlm": (0.0, "N", 0.0, 0.0),
    "aconity": (3700.0, "N", 0.0, 3400.0),
    "wire_edm": (7400.0, "N", 0.0, 7400.0),
    "instron_floor": (-6400.0, "S", 0.0, -6600.0),
    "instron_small": (-4300.0, "S", 0.0, -4300.0),
    "ded": (3500.0, "S", 0.0, 3500.0),
    "packaging": (7300.0, "S", 0.0, 7300.0),
    "hip": (10000.0, "N", 0.0, 10000.0),         # a hot isostatic press, if a module adds one (key "hip")
}
SETBACK = {"glovebox": 400.0}
BENCH = {"packaging": 900.0}      # benchtop stations on the floor plan stand on a bench this tall (mm, a choice)
RESERVED = {"ded": ("space for a DED machine", 3000.0, 2400.0),           # footprints drawn until a model exists
            "packaging": ("space for a packaging station", 2400.0, 1500.0)}   # (estimates: room, not a machine)
NAMES = {"glovebox": "glovebox: antechamber to the aisle", "repowder": "rePowder atomizer", "vlm": "Kardex VLM",
         "aconity": "Aconity MIDI", "wire_edm": "FANUC wire EDM", "instron_floor": "Instron 68FM-100",
         "instron_small": "Instron 68SC-2", "ded": "DED machine", "packaging": "packaging station",
         "hip": "hot isostatic press"}
CHARGERS = [-1500.0, -300.0]                   # x of each MiR Charge 48V, south side of the aisle (1.2 m apart)
RACK = dict(bay=2743.0, depth=1067.0, height=4877.0, levels=(0.0, 1626.0, 3251.0), upright=76.0, beam_h=127.0)
# typical selective pallet racking, not a quote: 108 in beams, 42 in deep frames, 16 ft uprights; GMA pallets
# 48 x 40 in (1219 x 1016 mm, one of ISO 6780's sizes)
PALLET = (1219.0, 1016.0, 140.0)
RACKS = [  # (x0, y0, bays, along): the racking round the edge, its back to the wall
    (-12900.0, -9200.0, 5, "y"), (12900.0 - RACK["depth"], -9200.0, 5, "y"), (-11000.0, 2800.0, 8, "x"),
]
FLOOR_C = (0.80, 0.80, 0.78)                   # sealed concrete
TAPE_Y, TAPE_W = (0.98, 0.80, 0.10), (0.97, 0.97, 0.95)
R1_C, R2_C = (0.15, 0.45, 0.85), (0.10, 0.65, 0.45)

CAM_ALL = [(5200, -20500, 17500), (-300, -2900, 0), (0, 0, 1)]
CAM_AISLE = [(6200, -12500, 4600), (-1200, -3600, 700), (0, 0, 1)]
CAM_VLM = [(2900, -6600, 2700), (-100, -1900, 1000), (0, 0, 1)]
CAM_WEST = [(-2400, -9600, 4300), (-6800, -3200, 900), (0, 0, 1)]
CAM_GB = [(-4300, -5600, 2600), (-7300, -2100, 1000), (0, 0, 1)]


# ============================================================================================ geometry helpers
def _box(x0, y0, z0, x1, y1, z1):
    return pv.Box(bounds=(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))).triangulate()


def _merge(ms):
    ms = [m for m in ms if m is not None and m.n_points]
    return ms[0].merge(ms[1:]) if len(ms) > 1 else (ms[0] if ms else None)


def tape_rect(cx, cy, w, d, t=60.0, ang=0.0):
    """A rectangle of floor tape, w x d (outer), centred on (cx, cy), turned by ang about z."""
    parts = [_box(-w / 2, -d / 2, 0, w / 2, -d / 2 + t, 1.5), _box(-w / 2, d / 2 - t, 0, w / 2, d / 2, 1.5),
             _box(-w / 2, -d / 2, 0, -w / 2 + t, d / 2, 1.5), _box(w / 2 - t, -d / 2, 0, w / 2, d / 2, 1.5)]
    m = _merge(parts)
    return m.rotate_z(ang, inplace=False).translate((cx, cy, 0), inplace=False)


def tag(size=110.0):
    """A camera target: a square fiducial, black with a white pattern (drawn like an AprilTag; schematic), facing up,
    origin at its centre. Returns (black, white)."""
    s = size / 2
    black = _box(-s, -s, 0, s, s, 4)
    c = size / 8
    cells = [(1, 1), (1, 4), (2, 2), (3, 1), (4, 3), (4, 5), (5, 2), (2, 5), (5, 5), (3, 3)]
    white = _merge([_box(-s + c * i, -s + c * j, 4, -s + c * (i + 1), -s + c * (j + 1), 5) for i, j in cells])
    return black, white


def racking():
    """The pallet racking round the edge: uprights, beams, pallets and boxes, one mesh each."""
    up, beams, pal, boxes, boxes2 = [], [], [], [], []
    rng = np.random.default_rng(303)
    b, d, h, u = RACK["bay"], RACK["depth"], RACK["height"], RACK["upright"]
    for x0, y0, n, along in RACKS:
        for i in range(n + 1):
            for j in (0, 1):
                if along == "x":
                    px, py = x0 + i * b, y0 + j * (d - u)
                else:
                    px, py = x0 + j * (d - u), y0 + i * b
                up.append(_box(px, py, 0, px + u, py + u, h))
        for i in range(n):
            for lv in RACK["levels"]:
                z = lv + (RACK["beam_h"] if lv == 0 else 0.0)
                for j in (0, 1):
                    if lv == 0:
                        continue
                    if along == "x":
                        beams.append(_box(x0 + i * b + u, y0 + j * (d - u), z, x0 + (i + 1) * b, y0 + j * (d - u) + u,
                                          z + RACK["beam_h"]))
                    else:
                        beams.append(_box(x0 + j * (d - u), y0 + i * b + u, z, x0 + j * (d - u) + u, y0 + (i + 1) * b,
                                          z + RACK["beam_h"]))
                for k in range(2):                       # two pallets a bay, 40 in faces out
                    if rng.random() < 0.18:
                        continue
                    zb = z + (RACK["beam_h"] if lv > 0 else 0.0)
                    if along == "x":
                        cx, cy = x0 + i * b + u + 120 + PALLET[1] / 2 + k * (PALLET[1] + 200), y0 + d / 2
                        pw, pd = PALLET[1], PALLET[0]
                    else:
                        cx, cy = x0 + d / 2, y0 + i * b + u + 120 + PALLET[1] / 2 + k * (PALLET[1] + 200)
                        pw, pd = PALLET[0], PALLET[1]
                    pal.append(_box(cx - pw / 2, cy - pd / 2, zb, cx + pw / 2, cy + pd / 2, zb + PALLET[2]))
                    hh = rng.uniform(700, 1250)
                    (boxes if rng.random() < 0.6 else boxes2).append(
                        _box(cx - pw / 2 + 30, cy - pd / 2 + 30, zb + PALLET[2], cx + pw / 2 - 30, cy + pd / 2 - 30,
                             zb + PALLET[2] + hh))
    return {"rack uprights": (_merge(up), (0.13, 0.30, 0.62)), "rack beams": (_merge(beams), (0.95, 0.45, 0.08)),
            "rack pallets": (_merge(pal), (0.72, 0.58, 0.38)), "rack boxes": (_merge(boxes), (0.80, 0.66, 0.45)),
            "rack boxes 2": (_merge(boxes2), (0.90, 0.88, 0.84))}


def charger_mesh():
    """MiR Charge 48V: the body against the south row and its charging plate on the floor, origin at the plate's front
    edge, facing +y (north). The plate's thickness and the contacts are drawn, not sourced."""
    W, D, H, Dp = CHARGER["W"], CHARGER["D"], CHARGER["H"], CHARGER["D_plate"]
    body = _box(-W / 2, -Dp, 0, W / 2, -Dp + D, H)
    plate = _box(-W / 2 + 40, -Dp + D, 0, W / 2 - 40, 0, 8)
    contacts = _box(-120, -Dp + D, 8, 120, -Dp + D + 80, 30)
    led = _box(-W / 2 + 60, -Dp + D, H - 50, W / 2 - 60, -Dp + D + 2, H - 30)
    return {"charger body": (body, (0.30, 0.31, 0.33)), "charger plate": (plate, (0.55, 0.56, 0.58)),
            "charger contacts": (contacts, (0.85, 0.65, 0.20)), "charger led": (led, (0.40, 0.85, 1.0))}


def place(bbox, cx, front, row, turn=0.0) -> np.ndarray:
    """A machine's own frame (x right, front at ymin) -> the floor: its footprint's centre on x = cx, its outermost
    face towards the aisle on y = front, standing on the floor. row "N" faces -y, "S" faces +y; turn is about z."""
    x0, x1, y0, y1, z0, _ = bbox
    Rz = R((0, 0, 1), turn + (180.0 if row == "S" else 0.0))
    corners = np.array([[x, y, 0, 1] for x in (x0, x1) for y in (y0, y1)]) @ Rz.T
    lo, hi = corners[:, :2].min(0), corners[:, :2].max(0)
    if row == "N":
        return T((cx - (lo[0] + hi[0]) / 2, front - lo[1], -z0)) @ Rz
    return T((cx - (lo[0] + hi[0]) / 2, front - hi[1], -z0)) @ Rz


def dock_pose(key: str) -> tuple[float, float, float]:
    """(x, y, heading) of a MiR250 docked at a station: alongside its front, the arm's side (the MiR's left) towards
    it."""
    _, row, _, dx = STATIONS[key]
    return (dx, DOCK_N, 0.0) if row == "N" else (dx, DOCK_S, 180.0)


def charger_pose(i: int) -> tuple[float, float, float]:
    return (CHARGERS[i], Y_FACE_S + 20.0 + P.MIR["L"] / 2, -90.0)


def target_xy(key: str) -> np.ndarray:
    """Where the camera target stands at a dock: beyond the docked MiR's front end, 150 mm off the station's face."""
    x, y, hd = dock_pose(key)
    fwd = np.array([math.cos(math.radians(hd)), math.sin(math.radians(hd))])
    side = np.array([-fwd[1], fwd[0]])
    return np.array([x, y]) + fwd * 650.0 + side * ((Y_FACE_N - DOCK_N) - 150.0)


TARGET_Z = 900.0
SPEED = 1500.0                                 # mm/s as drawn; the MiR250 does up to 2.0 m/s (MiR)
GIF = dict(fps=5, width=640, lossy=90)         # line.mp4_to_gif settings: these movies are long, so a smaller GIF


def upright(p, toward):
    """Gripper level, pointing along `toward`, its frame's y up, so a vial held this way stays upright whichever way the
    gripper points (props.tcp_frame's spin picked to suit)."""
    M = P.tcp_frame(p, toward, 0.0)
    return M if M[2, 1] > 0 else P.tcp_frame(p, toward, 180.0)


# ============================================================================================ the mobile manipulators
class Amr:
    """A MiR250 with its cabinet, the vial holder and a UR10e with a Robotiq 2F-85: props.mir250() and robot.Robot, as
    in animate.Lab._amr, but free to drive. pose = (x, y, heading in degrees); it drives along its own x."""

    def __init__(self, sc: Scene, name: str, pose, band=None):
        import robot as RB
        self.sc, self.name = sc, name
        for nm, (mesh, col) in P.mir250().items():
            kw = dict(ambient=0.8) if "light" in nm else {}
            if "light" in nm and band is not None:
                col = band
            sc.add(f"{name}/{nm}", mesh, col, name, **kw)
        holder, seat = P.buffer_holder()
        sc.add(f"{name}/holder", holder.translate((*A.BUFFER_LOCAL, P.AMR_TOP - 20), inplace=False), P.RACK_C, name)
        self.buffer_seat = (A.BUFFER_LOCAL[0], A.BUFFER_LOCAL[1], P.AMR_TOP - 20 + seat[2])
        self.pose = list(pose)
        self.set()
        self.robot = RB.Robot(sc, A.ROBOT, name, T((*A.ARM_LOCAL, P.AMR_TOP)), q0=A.PARK_DEG, prefix=f"{name}ur")

    def set(self, pose=None):
        if pose is not None:
            self.pose = list(pose)
        x, y, hd = self.pose
        self.sc.gmat[self.name] = T((x, y, 0)) @ R((0, 0, 1), hd)
        rb = getattr(self, "robot", None)
        if rb is not None and rb.held is not None:
            rb.set()

    def names(self):
        return [n for n, g in self.sc.group_of.items() if g == self.name or g.startswith(f"{self.name}ur")]

    def route(self, pts, end_heading=None, reverse_first=False, reverse_last=False):
        """Timeline of a drive through the (x, y) points: pivot to face each leg (MiR250s turn on the spot), drive it
        straight; then pivot to end_heading. reverse_first backs the first leg out (off a charger), reverse_last backs
        into the dock. Returns (update(u), seconds at SPEED mm/s and 60 deg/s)."""
        segs, (x, y, hd) = [], self.pose
        for i, (px, py) in enumerate(pts):
            dx, dy = px - x, py - y
            dist = math.hypot(dx, dy)
            if dist < 1:
                continue
            want = math.degrees(math.atan2(dy, dx))
            if (i == 0 and reverse_first) or (i == len(pts) - 1 and reverse_last):
                want += 180.0
            turn = (want - hd + 180.0) % 360.0 - 180.0
            if abs(turn) > 0.5:
                segs.append(("turn", (x, y, hd), (x, y, hd + turn), abs(turn) / 60.0))
                hd += turn
            segs.append(("drive", (x, y, hd), (px, py, hd), dist / SPEED))
            x, y = px, py
        if end_heading is not None:
            turn = (end_heading - hd + 180.0) % 360.0 - 180.0
            if abs(turn) > 0.5:
                segs.append(("turn", (x, y, hd), (x, y, hd + turn), abs(turn) / 60.0))
        total = sum(s[3] for s in segs) or 1.0
        bounds = np.cumsum([0.0] + [s[3] / total for s in segs])

        def up(u):
            for k, s in enumerate(segs):
                if u <= bounds[k + 1] + 1e-9 or k == len(segs) - 1:
                    f = min(1.0, max(0.0, (u - bounds[k]) / max(bounds[k + 1] - bounds[k], 1e-9)))
                    a, b = np.array(s[1]), np.array(s[2])
                    self.set(a + (b - a) * f)
                    return
        return up, total


def path_ribbon(start, pts, width=45.0):
    """The planned route drawn on the floor: a ribbon through start and the points."""
    pts = [tuple(start[:2])] + [tuple(p) for p in pts]
    out = []
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1:
            continue
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        seg = _box(0, -width / 2, 2.0, L, width / 2, 3.5).rotate_z(ang, inplace=False).translate((x0, y0, 0),
                                                                                                    inplace=False)
        out.append(seg)
        out.append(pv.Cylinder(center=(x1, y1, 2.75), direction=(0, 0, 1), radius=width * 0.9, height=1.5,
                               resolution=24).triangulate())
    return _merge(out)


# ============================================================================================ the floor
class Floor:
    """The warehouse floor plan in a scene: every station, the chargers, the tape, the targets and the racking. Each
    item is its own group (``self.groups[key]``), so setup_lab.py can bring them in one at a time."""

    def __init__(self, sc: Scene, L: A.Lab, idata: dict, racks=True):
        self.sc, self.L, self.idata = sc, L, idata
        self.groups: dict[str, list[str]] = {}
        self.rigs: dict[str, tour.Rig] = {}
        self.where: dict[str, np.ndarray] = {}        # a label point for each station
        sc.alpha["floor"] = 0.0
        sc.alpha["floor shadow"] = 0.0
        sc.add("warehouse floor", pv.Plane(center=(0, -3500, -2), direction=(0, 0, 1), i_size=30000, j_size=21000),
               FLOOR_C, "wfloor", ambient=0.9, diffuse=0.15, specular=0.0, smooth_shading=False)
        self._stations()
        self._tape()
        self._chargers()
        if racks:
            for nm, (mesh, col) in racking().items():
                sc.add(nm, mesh, col, "racking", specular=0.1)
            self.groups["racking"] = sc.members("racking")

    # ----------------------------------------------------------------------------------- stations
    def _stations(self):
        sc = self.sc
        for key, (cx, row, turn, _) in STATIONS.items():
            if key == "vlm":
                self.where[key] = np.array([0.0, Y_FACE_N, V.UNIT_H])
                continue
            if key == "repowder":
                self.where[key] = np.array([A.REPOWDER_AT[0] + 140, A.REPOWDER_AT[1] + 300, 1600])
                self.groups[key] = sc.members("repowder")
                continue
            front = Y_FACE_N if row == "N" else Y_FACE_S
            front += SETBACK.get(key, 0.0) * (1 if row == "N" else -1)
            if key == "aconity":
                ents = line.aconity_entries()
                pts = np.vstack([e["mesh"].points for e in ents.values() if e["mesh"].n_points])
                lo, hi = pts.min(0), pts.max(0)
                for n, e in ents.items():
                    sc.add(n, e["mesh"], e["color"], "aconity", opacity=e["opacity"])
                sc.gmat["aconity"] = place((lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]), cx, front, row, turn)
                self.groups[key] = sc.members("aconity")
                self.where[key] = np.array([cx, front + (300 if row == "N" else -300), hi[2]])
                continue
            if key in self.idata:
                inst, ents = self.idata[key]
                bb = inst.bbox()
                M = place(bb, cx, front, row, turn)
                bench = []
                if key in BENCH:                      # a benchtop station stands on a plain bench (a layout choice)
                    h = BENCH[key]
                    w, d = bb[1] - bb[0] + 100.0, bb[3] - bb[2] + 100.0
                    yc = front + (bb[3] - bb[2]) / 2 if row == "N" else front - (bb[3] - bb[2]) / 2
                    g = f"bench_{key}"
                    sc.add(f"{g}/top", _box(cx - w / 2, yc - d / 2, h - 40, cx + w / 2, yc + d / 2, h),
                           (0.62, 0.64, 0.67), g, specular=0.1)
                    legs = _merge([_box(x - 25, y - 25, 0, x + 25, y + 25, h - 40)
                                   for x in (cx - w / 2 + 40, cx + w / 2 - 40) for y in (yc - d / 2 + 40, yc + d / 2 - 40)])
                    sc.add(f"{g}/legs", legs, (0.35, 0.36, 0.38), g)
                    bench = sc.members(g)
                    M = T((0, 0, h)) @ M
                rig = tour.Rig(sc, inst, ents, f"wh_{key}:", at=M)
                self.rigs[key] = rig
                for piece in [pc for pc in rig.names if pc in inst.props]:
                    for nm in rig.names.pop(piece):
                        sc.alpha[nm] = 0.0
                self.groups[key] = rig.all_names() + bench
                self.where[key] = np.array([cx, front + (300 if row == "N" else -300), bb[5] + BENCH.get(key, 0.0)])
                continue
            if key in RESERVED:                       # a labelled footprint until the model exists
                txt, w, d = RESERVED[key]
                yc = front + d / 2 if row == "N" else front - d / 2
                g = f"reserved_{key}"
                sc.add(f"{g}/tape", tape_rect(cx, yc, w, d, t=70.0), (0.90, 0.35, 0.10), g, specular=0.0)
                hatch = _merge([_box(cx - w / 2 + 70 + i * 300, yc - d / 2 + 70, 0, cx - w / 2 + 70 + i * 300 + 40,
                                     yc + d / 2 - 70, 1.2) for i in range(int((w - 140) // 300) + 1)])
                sc.add(f"{g}/hatch", hatch, (0.93, 0.72, 0.55), g, specular=0.0)
                sc.add(f"{g}/volume", _box(cx - w / 2, yc - d / 2, 0, cx + w / 2, yc + d / 2, 1800),
                       (0.95, 0.55, 0.25), g, opacity=0.10, specular=0.0)
                self.groups[key] = sc.members(g)
                self.where[key] = np.array([cx, yc, 1800])

    # ----------------------------------------------------------------------------------- tape and targets
    def _tape(self):
        sc = self.sc
        lines = []
        for y in AISLE:
            lines.append(_box(X_END[0], y - 37.5, 0, X_END[1], y + 37.5, 1.5))    # 3 in tape on the aisle's edges
        sc.add("aisle tape", _merge(lines), TAPE_Y, "tape", specular=0.0, ambient=0.5)
        # dashed centre line: two lanes
        dashes = [_box(x, (AISLE[0] + AISLE[1]) / 2 - 25, 0, x + 600, (AISLE[0] + AISLE[1]) / 2 + 25, 1.5)
                  for x in np.arange(X_END[0] + 300, X_END[1] - 600, 1200)]
        sc.add("aisle dashes", _merge(dashes), TAPE_W, "tape", specular=0.0, ambient=0.5)
        self.groups["tape"] = ["aisle tape", "aisle dashes"]
        docks, blacks, whites, posts = [], [], [], []
        for key in STATIONS:
            if key not in ("vlm", "repowder") and key not in self.groups:      # nothing stands there: no dock
                continue
            x, y, hd = dock_pose(key)
            docks.append(tape_rect(x, y, P.MIR["L"] + 140, P.MIR["W"] + 140, t=50.0, ang=hd))
            tx, ty = target_xy(key)
            posts.append(pv.Cylinder(center=(tx, ty, TARGET_Z / 2), direction=(0, 0, 1), radius=25,
                                     height=TARGET_Z, resolution=20).triangulate())
            posts.append(_box(tx - 150, ty - 150, 0, tx + 150, ty + 150, 12))
            b, w = tag()
            blacks.append(b.translate((tx, ty, TARGET_Z), inplace=False))
            whites.append(w.translate((tx, ty, TARGET_Z), inplace=False))
        sc.add("dock tape", _merge(docks), TAPE_W, "docks", specular=0.0, ambient=0.5)
        sc.add("target posts", _merge(posts), (0.45, 0.46, 0.48), "docks")
        sc.add("target black", _merge(blacks), (0.05, 0.05, 0.06), "docks", specular=0.0)
        sc.add("target white", _merge(whites), (0.98, 0.98, 0.98), "docks", specular=0.0, ambient=0.6)
        self.groups["docks"] = ["dock tape", "target posts", "target black", "target white"]

    def _chargers(self):
        sc = self.sc
        names = []
        for i, x in enumerate(CHARGERS):
            g = f"charger{i}"
            for nm, (mesh, col) in charger_mesh().items():
                kw = dict(ambient=0.8) if "led" in nm else {}
                sc.add(f"{g}/{nm}", mesh, col, g, **kw)
                names.append(f"{g}/{nm}")
            sc.gmat[g] = T((x, Y_FACE_S + (CHARGER["D_plate"] - CHARGER["D"]), 0))
            bay = tape_rect(x, Y_FACE_S + 20.0 + P.MIR["L"] / 2, P.MIR["W"] + 140, P.MIR["L"] + 140, t=50.0)
            sc.add(f"{g}/bay tape", bay, TAPE_W, f"{g}_tape", specular=0.0, ambient=0.5)
            names.append(f"{g}/bay tape")
        self.groups["chargers"] = names


def lbl(F: Floor, key, at, text=None):
    return (text or NAMES[key], tuple(F.where[key]), at)


def auto(sc: Scene, cam, items, dy=0.10):
    """Leader labels over their anchors as seen from `cam`: [(text, xyz)] -> [(text, xyz, (fx, fy))], staggered so
    neighbours don't overlap."""
    sc.pl.camera_position = cam
    sc.pl.camera.view_angle = sc.view_angle
    pts = sorted(((t, tuple(xyz), sc.project(xyz)) for t, xyz in items), key=lambda p: p[2][0])
    out = []
    for i, (t, xyz, (px, py)) in enumerate(pts):
        fy = py - dy - 0.055 * (i % 2)
        fx = px + (0.015 if px < 0.5 else -0.015)
        out.append((t, xyz, (min(max(fx, 0.03), 0.97), min(max(fy, 0.08), 0.84))))
    return out


def floor_labels(F, keys, have):
    out = []
    for k in keys:
        if k not in F.where:                     # a spot with nothing on it yet (e.g. "hip" before its module exists)
            continue
        t = NAMES[k] if k not in RESERVED or k in have else RESERVED[k][0]
        out.append((t, F.where[k]))
    return out


# ============================================================================================ the movie
def movie(data, idata):
    sc = Scene("warehouse", TITLE, gif=False)
    sc.cam = list(CAM_ALL)
    L = A.Lab(sc, data, robot=False)
    F = Floor(sc, L, idata)
    L.skin(0.0)(1.0)
    L.show_gauges = False
    L.apply_state()
    r1 = Amr(sc, "amr1", charger_pose(0), band=(0.45, 0.75, 1.0))
    r2 = Amr(sc, "amr2", charger_pose(1), band=(0.45, 1.0, 0.70))
    n = 7

    # ------------------------------------------------------------------ 1. the floor
    have = [k for k in ("ded", "packaging") if k in idata]
    cap = ("The warehouse version: the VLM and the alloy line's floor machines on an open floor, pallet racking round "
           "the edge, served by MiR250 mobile bases each carrying a UR10e. The machines face one aisle from both "
           "sides instead of standing along a rail: a MiR250 can dock at any front that faces an aisle.")
    sc.step(f"1/{n}", cap, 3.0, None, hold=2.0, labels=auto(sc, CAM_ALL, floor_labels(F, STATIONS, have)))
    # ------------------------------------------------------------------ 2. aisles, docks, chargers
    gap = CHARGERS[1] - CHARGERS[0] - CHARGER["W"]
    cap = (f"The main aisle is {MIR250['corridor_two_mm'] / 1000:.1f} m wide, MiR's figure for two MiR250s passing "
           f"with the default safety setup; one needs {MIR250['corridor_mm'] / 1000:.2f} m and pivots in "
           f"{MIR250['pivot_mm'] / 1000:.1f} m. The docks sit between the aisle and the machines, each taped with a "
           f"camera target on a post, so a docked unit blocks nothing. The two chargers stand {gap / 1000:.2f} m apart "
           f"(MiR: at least {MIR250['charger_side_mm'] / 1000:.2f} m to the side of each).")
    mid = (AISLE[0] + AISLE[1]) / 2
    sc.step(f"2/{n}", cap, 3.0, None, hold=2.4, cam_to=CAM_AISLE,
            labels=[("main aisle, 3.0 m", (-4800, mid, 0), (0.16, 0.42)),
                    ("dock: tape and a camera target", (*target_xy("instron_small"), TARGET_Z), (0.12, 0.62)),
                    ("MiR Charge 48V x 2", (CHARGERS[0], Y_FACE_S, 300), (0.62, 0.70)),
                    ("UR10e on a MiR250, charging", (CHARGERS[1], Y_FACE_S + 450, 1300), (0.80, 0.46))])
    # ------------------------------------------------------------------ 3. out to the VLM and the Instron
    xv, yv, hv = dock_pose("vlm")
    p1 = [(CHARGERS[0], mid + 400), (-1800, mid + 400), (-1800, yv), (xv, yv)]
    xi, yi, hi = dock_pose("instron_floor")
    p2 = [(CHARGERS[1], mid - 400), (xi + 1500, mid - 400), (xi + 1500, yi), (xi, yi)]
    rib1 = path_ribbon(r1.pose, p1)
    rib2 = path_ribbon(r2.pose, p2)
    sc.add("route1", rib1, R1_C, "routes", specular=0.0, ambient=0.6)
    sc.add("route2", rib2, R2_C, "routes", specular=0.0, ambient=0.6)
    sc.alpha["route1"] = sc.alpha["route2"] = 0.0
    u1, t1 = r1.route(p1, end_heading=hv, reverse_first=True)
    u2, t2 = r2.route(p2, end_heading=hi, reverse_first=True)

    def show_routes(u):
        sc.alpha["route1"] = sc.alpha["route2"] = min(1.0, u * 2)
    sc.step(f"3/{n}", "Two units leave their chargers on the routes they are given: unit 1 to the VLM's opening, unit "
            "2 to the 100 kN Instron. Drawn at 1.5 m/s; the MiR250 does up to 2.0 m/s.", 1.0, show_routes, hold=0.2,
            cam_to=CAM_ALL)
    sc.step(f"3/{n}", "Two units leave their chargers on the routes they are given: unit 1 to the VLM's opening, unit "
            "2 to the 100 kN Instron. Drawn at 1.5 m/s; the MiR250 does up to 2.0 m/s.", max(t1, t2),
            A.both(u1, u2), hold=0.3, labels=auto(sc, CAM_ALL, [("unit 1: to the VLM", (xv, yv, 1500)),
                                                               ("unit 2: to the Instron", (xi, yi, 1500))]))
    # ------------------------------------------------------------------ 4. dock, camera check, the vial
    rb = r1.robot
    tx, ty = target_xy("vlm")
    look = A.down(np.array([tx, ty, TARGET_Z + 330.0]), spin=0.0)
    cap = (f"Docked. MiR's figures for docking to an L-marker: ±{MIR250['dock_L_mm_deg'][0]} mm along, "
           f"±{MIR250['dock_L_mm_deg'][1]} mm across, ±{MIR250['dock_L_mm_deg'][2]:.0f}° of yaw. One degree is 23 mm "
           "at the arm's 1.3 m reach, so the wrist camera reads the target and shifts the taught frame before the arm "
           "works.")
    sc.step(f"4/{n}", cap, 2.2, rb.joint_to(Tw=look), hold=1.6,
            cam_to=CAM_VLM, labels=[("camera target", (tx, ty, TARGET_Z), (0.80, 0.40))])
    L.fetch("B", f"4/{n}", "The VLM brings tray B (powder dosing) to the opening.", fast=0.45, hold=0.1)
    rack_xy = A.LOADS["B"][0][1:]
    seat = np.array(L.rack_seats[A.RACK_SEAT]) + (*rack_xy, V.T_FLOOR)
    p_rack = A.tray_world("B", seat + (0, 0, 50.0))
    cap = "The arm takes a vial from tray B's rack and stands it in the holder on its own cabinet."
    A.pick(L, rb, f"4/{n}", cap, A.down(p_rack), A.down(p_rack + (0, 0, 110)), "vial", seconds=(1.3, 0.7, 0.4, 0.6))
    buf = np.array(r1.buffer_seat)
    p_buf = (sc.world("amr1") @ np.r_[buf + (0, 0, 50.0), 1.0])[:3]
    A.place(L, rb, f"4/{n}", cap, A.down(p_buf), A.down(p_buf + (0, 0, 120)), "amr1", seconds=(1.3, 0.7, 0.4, 0.6))
    sc.step(f"4/{n}", cap, 1.0, rb.joint_to(A.PARK_RAD), hold=0.1)
    L.store("B", f"4/{n}", "Tray B goes back to its slot.", fast=0.4, hold=0.1)
    # ------------------------------------------------------------------ 5. to the glovebox; unit 2 checks in
    xg, yg, hg = dock_pose("glovebox")
    p3 = [(xv - 1200, yv), (xv - 1200, mid + 400), (xg + 1600, mid + 400), (xg + 1600, yg), (xg, yg)]
    rib3 = path_ribbon(r1.pose, p3)
    sc.add("route3", rib3, R1_C, "routes", specular=0.0, ambient=0.6)
    sc.alpha["route1"] = sc.alpha["route2"] = 0.0
    sc.alpha["route3"] = 0.0
    u3, t3 = r1.route(p3, end_heading=hg, reverse_first=True, reverse_last=True)
    rb2 = r2.robot
    tx2, ty2 = target_xy("instron_floor")
    look2 = A.down(np.array([tx2, ty2, TARGET_Z + 330.0]), spin=0.0)
    j2 = rb2.joint_to(Tw=look2)

    def go(u):
        sc.alpha["route3"] = min(1.0, u * 8)
        u3(u)
        j2(min(1.0, u * 2.5))
    sc.step(f"5/{n}", "Unit 1 carries the vial to the glovebox's antechamber, along the aisle. At the Instron, unit "
            "2's camera finds that dock's target.", t3, go, hold=0.3, cam_to=CAM_WEST,
            labels=[("unit 1, a vial on board", (xg + 1600, mid, 1500), (0.70, 0.22)),
                    ("unit 2: camera check", (tx2, ty2, TARGET_Z), (0.24, 0.70))])
    # ------------------------------------------------------------------ 6. the antechamber
    gb = F.rigs.get("glovebox")
    txg, tyg = target_xy("glovebox")
    lookg = A.down(np.array([txg, tyg, TARGET_Z + 330.0]), spin=0.0)
    cap = "At the glovebox: camera check, then the automatic antechamber's outer door opens to the aisle."
    sc.step(f"6/{n}", cap, 1.8, A.both(rb.joint_to(Tw=lookg), rb2.joint_to(A.PARK_RAD)), hold=0.3, cam_to=CAM_GB)
    if gb is not None:
        sc.step(f"6/{n}", cap, 1.6, gb.move({"door": (None, 1.0)}), hold=0.2)
    done = _antechamber(sc, L, F, r1, f"6/{n}")
    if gb is not None:
        sc.step(f"6/{n}", "Door shut: the PLC evacuates and refills the antechamber before the vial goes inside."
                if done else cap, 1.4, gb.move({"door": (None, 0.0)}), hold=0.4)
    # ------------------------------------------------------------------ 7. home
    p4 = [(xg + 1600, yg), (xg + 1600, mid + 400), (CHARGERS[0], mid + 400), (CHARGERS[0], charger_pose(0)[1])]
    p5 = [(xi + 1500, yi), (xi + 1500, mid - 400), (CHARGERS[1], mid - 400), (CHARGERS[1], charger_pose(1)[1])]
    u4, t4 = r1.route(p4, end_heading=-90.0)
    u5, t5 = r2.route(p5, end_heading=-90.0)
    sc.alpha["route3"] = 0.0
    sc.step(f"7/{n}", "Both units go back to charge: 10 to 90 % takes 52 min on a MiR Charge 48V (MiR).", max(t4, t5),
            A.both(u4, u5), hold=0.3, cam_to=CAM_ALL)
    sc.step(f"7/{n}", "The trade against the rail: every front on the floor is reachable and the floor stays free, but "
            "a dock comes back to within millimetres, not the rail's ±0.3 mm, so every station needs a target the "
            "arm checks before it works.", 1.6, None, hold=3.0, still=True,
            labels=auto(sc, CAM_ALL, floor_labels(F, ("glovebox", "vlm", "wire_edm", "instron_floor", "ded"), have)))
    return sc.save()


def _antechamber(sc, L, F, r1, step) -> bool:
    """The arm takes the vial from its holder and puts it in the antechamber, gripper level, through the door. Returns
    False (and leaves the vial on the robot) if the inverse kinematics can't do it without a flip."""
    gb = F.rigs.get("glovebox")
    if gb is None:
        return False
    import instruments as I
    p = I.GLOVEBOX
    xb1 = -p["W"] / 2 + p["box_w"]
    az = p["stand_h"] + p["ante_d"] / 2 + 80
    seat_local = np.array([xb1 + p["ante_l"] - 160, 0.0, az - p["ante_d"] / 2 + 40, 1.0])
    seat = (sc.world("wh_glovebox:body") @ seat_local)[:3]
    rb = r1.robot
    buf = np.array(r1.buffer_seat)
    p_buf = (sc.world("amr1") @ np.r_[buf + (0, 0, 50.0), 1.0])[:3]
    east = sc.world("amr1")[:3, :3] @ np.array([1.0, 0, 0])          # along the MiR, towards its front
    inward = sc.world("wh_glovebox:body")[:3, :3] @ np.array([-1.0, 0, 0])
    p_in = seat + (0, 0, 32.0)
    back = 300.0
    try:
        q0 = rb.q.copy()
        for M in (upright(p_buf - east * 160, east), upright(p_buf, east), upright(p_in - inward * back, inward),
                  upright(p_in, inward)):
            rb.solve(M)
        rb.q = q0
        cap = "The arm takes the vial from its holder, gripper level, ..."
        sc.step(step, cap, 1.4, A.both(rb.joint_to(Tw=upright(p_buf - east * 160 + (0, 0, 40), east)),
                                       rb.grip_to(0.0)), hold=0.05)
        sc.step(step, cap, 0.5, rb.line_to(upright(p_buf - east * 160, east)), hold=0.0)
        sc.step(step, cap, 0.7, rb.line_to(upright(p_buf, east)), hold=0.05)
        sc.step(step, cap, 0.4, rb.grip_to(A.GRIP_VIAL), hold=0.05)
        rb.grasp("vial")
        sc.step(step, cap, 0.5, rb.line_to(upright(p_buf + (0, 0, 60), east)), hold=0.0)
        sc.step(step, cap, 0.6, rb.line_to(upright(p_buf - east * 160 + (0, 0, 60), east)), hold=0.05)
        cap = "... and puts it into the antechamber through the open door."
        sc.step(step, cap, 1.5, rb.joint_to(Tw=upright(p_in - inward * back, inward)), hold=0.05)
        sc.step(step, cap, 1.0, rb.line_to(upright(p_in, inward)), hold=0.05)
        sc.step(step, cap, 0.4, rb.grip_to(0.0), hold=0.05)
        rb.release("wh_glovebox:body")
        sc.step(step, cap, 0.9, rb.line_to(upright(p_in - inward * back, inward)), hold=0.05)
        sc.step(step, cap, 1.2, rb.joint_to(A.PARK_RAD), hold=0.1)
        return True
    except Exception as e:                       # noqa: BLE001
        print("antechamber move skipped:", e, flush=True)
        sc.step(step, "The arm parks; the antechamber stays for the gloves.", 1.0, rb.joint_to(A.PARK_RAD), hold=0.2)
        return False


# ============================================================================================ rail vs mobile base
def sway() -> dict:
    """First-order numbers for the three ways of carrying the arm: a low rail with a steel pedestal, the beam-height
    Vention rail, and a MiR250. Cantilever pedestal, steel E = 200 GPa, loads from UR's stand table without its 2.5
    factor. Estimates are labelled; see notes/warehouse.md."""
    E = 200e3                                       # N/mm^2, structural steel
    stop, run = UR10E["stand_stop"], UR10E["stand_run"]
    sf = UR10E["safety"]
    cases = {"run": (run[2] / sf * 1e3, run[3] / sf), "stop": (stop[2] / sf * 1e3, stop[3] / sf)}   # (Nmm, N)
    sections = {   # I in mm^4; a round tube and two square ones (square corners: slightly high)
        "CHS 219.1 x 8.0": math.pi / 64 * (219.1 ** 4 - 203.1 ** 4),
        "SHS 150 x 150 x 6.3": (150 ** 4 - 137.4 ** 4) / 12,
        "SHS 200 x 200 x 10": (200 ** 4 - 180 ** 4) / 12,
    }
    beam_top = 800.0 - 86.0 - 30.0                  # 684 mm: the beam's top under the carriage (instruments.rail)
    heights = {"Vention beam laid on the floor (carriage top 363.5 mm)": 800.0 - 363.5,
               "flush floor track (carriage top about 150 mm, estimate)": 650.0}
    mass = UR10E["mass_kg"] + UR10E["payload_kg"] + 0.925 + 5.0     # arm, payload, 2F-85 (0.925 kg), top plate (est.)
    e_com = 400.0                                   # height of that mass over the flange, mm (estimate, mid-reach pose)
    out = {"inputs": dict(E_N_mm2=E, loads_nominal=dict(run_Mxy_Nm=run[2] / sf, run_Fxy_N=run[3] / sf,
                                                         stop_Mxy_Nm=stop[2] / sf, stop_Fxy_N=stop[3] / sf),
                          lever_mm=UR10E["reach_mm"], mass_on_top_kg=mass, com_above_flange_mm=e_com,
                          sources=["UR10e user manual SW5.26, 6.2 Dimensioning the Stand (loads x 2.5; >= 45 Hz)",
                                   "UR10e data sheet Oct 2026 (12.5 kg, 1300 mm, 33.3 kg, +-0.05 mm)",
                                   "Robotiq 2F-85: about 0.9 kg (Robotiq; 0.89-0.925 kg in listings)"]),
           "pedestal": []}
    for hname, Lp in heights.items():
        for sname, Ii in sections.items():
            EI = E * Ii
            row = dict(pedestal=hname, height_mm=round(Lp, 1), section=sname, I_cm4=round(Ii / 1e4))
            for cname, (M, Fh) in cases.items():
                th = Fh * Lp ** 2 / (2 * EI) + M * Lp / EI
                de = Fh * Lp ** 3 / (3 * EI) + M * Lp ** 2 / (2 * EI)
                row[f"{cname}_tilt_mdeg"] = round(math.degrees(th) * 1e3, 2)
                row[f"{cname}_tool_mm"] = round(de + th * UR10E["reach_mm"], 3)
            k = EI / (Lp ** 3 / 3 + e_com * Lp ** 2 + e_com ** 2 * Lp)       # N/mm at the mass
            row["first_mode_hz"] = round(math.sqrt(k * 1e3 / mass) / (2 * math.pi), 1)
            out["pedestal"].append(row)
    lever = {"beam-height rail": 800.0 - beam_top, "low rail, 436.5 mm pedestal": 800.0 - 363.5,
             "flush track, 650 mm pedestal": 800.0 - 150.0}
    out["moment_at_carriage_Nm"] = {k: dict(run=round(cases["run"][0] / 1e3 + cases["run"][1] * v / 1e3),
                                            stop=round(cases["stop"][0] / 1e3 + cases["stop"][1] * v / 1e3),
                                            lever_mm=round(v, 1)) for k, v in lever.items()}
    out["tool_mm_per_mdeg_tilt_at_reach"] = round(math.radians(1e-3) * UR10E["reach_mm"], 4)
    # the MiR250: docking error at the tool, and the tipping check
    yaw = MIR250["dock_L_mm_deg"][2]
    out["mir250"] = dict(dock_L=MIR250["dock_L_mm_deg"], dock_VL=MIR250["dock_VL_mm"],
                         position=MIR250["position_mm_deg"],
                         tool_error_from_1deg_yaw_mm=round(math.radians(yaw) * UR10E["reach_mm"], 1),
                         touch_off_mm=0.12, touch_off_deg=0.005,
                         touch_off_source="Burger et al., Nature 583, 237 (2020), SI 1.3: six touches on a 100 x 100 x "
                                          "50 mm cube; KUKA KMR iiwa, 100 trials from up to +-15 mm, +-2.5 deg")
    m_tot = MIR250["mass_kg"] + UR10E["mass_kg"] + 12.0 + UR10E["payload_kg"] + 40.0   # + control box, payload, cabinet
    restore = m_tot * 9.81 * (MIR250["size_mm"][1] / 2) / 1e3                           # Nm, about the long edge
    h = P.AMR_TOP / 1e3
    out["mir250"]["tipping"] = dict(
        mass_kg=round(m_tot, 1), note="MiR250 97 kg (MiR), UR10e 33.3 kg, control box 12 kg, payload 12.5 kg (UR), "
        "cabinet 40 kg (estimate); restoring moment about the body's long edge, an upper bound (the wheels sit inside)",
        restoring_Nm=round(restore), arm_base_m=h,
        overturn_run_Nm=round(cases["run"][0] / 1e3 + cases["run"][1] * h),
        overturn_stop_Nm=round(cases["stop"][0] / 1e3 + cases["stop"][1] * h))
    out["rail"] = dict(vention_repeat_mm=VENTION_REPEAT_MM, ur10e_repeat_mm=UR10E["repeat_mm"])
    return out


def compare():
    """out/rail_vs_amr.png: the three ways of carrying the UR10e at 800 mm, side by side, the arm in the same pose, with
    the numbers from sway() under each."""
    import instruments as I
    import robot as RB
    from PIL import Image, ImageDraw
    from scene import font
    res = sway()
    sc = Scene("rail_vs_amr", "", gif=False, mp4=False)
    sc.add("floor", pv.Plane(center=(3000, 0, -1), direction=(0, 0, 1), i_size=16000, j_size=10000), FLOOR_C, "wfloor",
           ambient=0.9, diffuse=0.15, specular=0.0, smooth_shading=False)
    xa, xb, xc = 0.0, 3500.0, 7000.0
    blue, steel = I.MATERIALS["vention_blue"][:3], (0.70, 0.71, 0.73)
    # A: Vention's beam laid on the floor (carriage top 363.5 mm) and a round steel tube, 219.1 x 8 mm, up to 800 mm
    car_top = 800.0 - (800.0 - 363.5)
    sc.add("A beam", _box(xa - 1250, -123.75, 0, xa + 1250, 123.75, 247.5), blue, "A")
    sc.add("A guides", _merge([_box(xa - 1230, y - 10, 247.5, xa + 1230, y + 10, 262.5) for y in (-93.75, 93.75)]),
           steel, "A")
    sc.add("A carriage", _box(xa - 213, -179, car_top - 86, xa + 213, 179, car_top), blue, "A")
    sc.add("A pedestal", pv.Cylinder(center=(xa, 0, (car_top + 20 + 780) / 2), direction=(0, 0, 1), radius=109.55,
                                     height=780 - car_top - 20, resolution=48).triangulate(), (0.35, 0.36, 0.38), "A")
    sc.add("A plates", _merge([_box(xa - 160, -160, car_top, xa + 160, 160, car_top + 20),
                               _box(xa - 130, -130, 780, xa + 130, 130, 800)]), (0.35, 0.36, 0.38), "A")
    # B: the beam-height rail of round 3
    rail = I.rail(length=2500.0, travel=1.0)
    tour.Rig(sc, rail, tour.piece_entries(rail), "B:", at=T((xb, 0, 0)))
    # C: a MiR250 with its cabinet
    amr = Amr(sc, "C", (xc, -A.ARM_LOCAL[1], 0.0))
    robots = [RB.Robot(sc, A.ROBOT, "A", T((xa, 0, 800.0)), q0=A.PARK_DEG, prefix="Aur"),
              RB.Robot(sc, A.ROBOT, "B:carriage", T((0, 0, I.RAIL["top"])), q0=A.PARK_DEG, prefix="Bur"), amr.robot]
    for rb in robots:                               # the same pose for all three: reaching out 1 m, gripper down
        base = sc.world(rb.root)[:3, 3]
        rb.set(rb.solve(A.down(base + np.array([800.0, -300.0, 50.0]))))
    sc.cam = [(3700, -10400, 3300), (3700, 0, 500), (0, 0, 1)]
    img = Image.fromarray(sc.render_base())
    pts = [sc.project((x, -900, 0)) for x in (xa, xb, xc)]
    sc.pl.close()
    p = res["pedestal"]
    ped = next(r for r in p if r["section"].startswith("CHS") and r["height_mm"] < 500)
    mom = res["moment_at_carriage_Nm"]
    mir = res["mir250"]
    texts = [
        ("A. Low rail, steel pedestal", [f"round tube 219.1 x 8 mm, {ped['height_mm']:.0f} mm tall",
                                         f"sway at the tool: {ped['run_tool_mm']:.2f}-{ped['stop_tool_mm']:.2f} mm",
                                         f"first mode about {ped['first_mode_hz']:.0f} Hz (UR: ≥ 45)",
                                         f"rail: ±{VENTION_REPEAT_MM} mm (Vention)",
                                         f"carriage moment {mom['low rail, 436.5 mm pedestal']['run']} Nm"]),
        ("B. Beam-height rail (round 3)", [f"rail: ±{VENTION_REPEAT_MM} mm (Vention)",
                                           f"carriage moment {mom['beam-height rail']['run']} Nm",
                                           "beam at 440-690 mm, 120 mm in front", "of the machines' fronts"]),
        ("C. MiR250 + cabinet", [f"dock: ±{mir['dock_L'][0]} / ±{mir['dock_L'][1]} mm, ±{mir['dock_L'][2]:.0f}° "
                                 "(L-marker)", f"1° of yaw = {mir['tool_error_from_1deg_yaw_mm']:.0f} mm at 1.3 m",
                                 f"touch-off: ±{mir['touch_off_mm']} mm (Burger 2020)",
                                 f"worst-case tipping moment {mir['tipping']['overturn_run_Nm']} Nm",
                                 f"vs ≤ {mir['tipping']['restoring_Nm']} Nm holding it: slow the arm"]),
    ]
    d = ImageDraw.Draw(img, "RGBA")
    f1, f2 = font(17, bold=True), font(14)
    for (title, lines), (fx, fy) in zip(texts, pts):
        x0 = min(max(fx * img.width - 170, 12), img.width - 330)
        y0 = min(fy * img.height + 10, img.height - 30 - 20 * len(lines))
        w = max([d.textlength(title, font=f1)] + [d.textlength(t, font=f2) for t in lines]) + 20
        d.rounded_rectangle((x0 - 10, y0 - 6, x0 + w, y0 + 26 + 20 * len(lines)), 6, fill=(255, 255, 255, 225),
                            outline=(150, 154, 160, 255))
        d.text((x0, y0), title, font=f1, fill=(20, 20, 24))
        for i, t in enumerate(lines):
            d.text((x0, y0 + 26 + 20 * i), t, font=f2, fill=(40, 42, 46))
    d.text((14, 10), "Carrying a UR10e at 800 mm, three ways (UR's worst-case loads, without its 2.5 factor)",
           font=font(19, bold=True), fill=(20, 20, 24))
    path = OUT / "rail_vs_amr.png"
    img.convert("RGB").save(path, optimize=True)
    return path


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "sway":
        res = sway()
        OUT.mkdir(exist_ok=True)
        (OUT / "rail_vs_amr.json").write_text(json.dumps(res, indent=1) + "\n")
        print(json.dumps(res, indent=1))
    elif args and args[0] == "compare":
        print(compare(), flush=True)
    else:
        data = lab.meshes()
        idata = tour.load()
        print(movie(data, idata), flush=True)
        if not PREVIEW:
            print(line.mp4_to_gif(OUT / "mp4" / "warehouse.mp4", OUT / "warehouse.gif", **GIF), flush=True)
