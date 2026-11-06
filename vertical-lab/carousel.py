"""The lab's latest multi-doser, the **chain carousel v5** (powder-doser PR #185, issue #128), as animated meshes.

Thirteen powder modules (Sam's mounting plate with the lab's threaded auger) ride two vertical #35 chains, their augers
outside the loop (v4). v5 rebuilds the station round an **A&D HR-202i** (220 g x 0.1 mg) that stands on the bench under
the dose point, inside the U-shaped base and touching nothing of the doser: the electronics carriage (EC) rides an
8 mm lift bar carried by two Actuonix P16s, one each side of the balance, with guided shoes in slots on two station
posts; it rises, docks under the station module and tilts it to 30° (40° at most), and the dose falls 154 mm through
the balance's open top door into the vessel on its pan, dosed by weight. No funnel, no load cell.

Nothing of the rig is re-modelled: ``multidoser/chain-carousel-v5/`` holds byte-for-byte copies of powder-doser's
``cad/chain-carousel-v5/`` at ``353dae7`` (PR #185's head, 2026-11-05) and ``multidoser/vendor/`` the vendor helpers they
import (``cad/vendor/``, same commit), and ``layout.placements(State(...))`` gives every one of the rig's part instances
for a chain shift, an EC lift and tilt, an auger turn, a solenoid tap and the balance's doors, so the carousel indexes,
docks, tilts and doses with its own kinematics. The vendors' own STEPs (McMaster, Actuonix, StepperOnline) are not
redistributable and are not fetched: the copies fall back to their own parametric stand-ins, as powder-doser does
without ``cad/vendor/files/``. Sam's plate and electronics carriage, the auger and its cap are fetched from v4's
``reference/`` at that commit and hash-checked.

Ours, not powder-doser's (drawn in the lab's PETG teal, and in notes/multidoser.md):
* a **pedestal riser** on the pan in place of v5's beaker riser: the vial or a charge cup stands on an 11 mm neck, its
  rim at 280-282.5 mm, so the 154 mm fall carries over and a cup's 12.7 mm bore sits under the 8 mm stream;
* a **vessel shuttle**: v5 leaves the beaker to a hand through its front hatch, and a 2F-85 can't follow (below), so a
  fork on a belt slide carries the vessel between the arm, outside a port in the -y acrylic panel, and the pedestal,
  through the balance's -y side door;
* a **top-door pusher** and a **side-door pusher** (v5's doors are opened by hand; a robot-served station needs
  actuators), slides on the bench inside the base whose fingers take a door's grip only while they move it.
On tray B the top panel lies on the top rails (``lowered``), so the rig is 854 mm tall, not 860.

Frame of the rig (its own): x along the augers (outlet end, display of the balance, at -x), y along the loop, z up
from the bench. Millimetres.
"""
from __future__ import annotations

import hashlib
import math
import pickle
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
MD = HERE / "multidoser"
V5 = MD / "chain-carousel-v5"
VENDOR = MD / "vendor"
REF = MD / "chain-carousel-v4" / "reference"     # v5's layout.py reads v4's reference/ (v5 adds none)

SHA = "353dae78829ef8fffaa1bd584876a157145a0b76"       # powder-doser PR #185 head (claude/issue-128-20261013-2050)
REF_URL = "https://raw.githubusercontent.com/vertical-cloud-lab/powder-doser/{sha}/cad/chain-carousel-v4/reference/{name}"
REFERENCE = {
    "sam-oct13-mounting-plate-and-carriage.step": "dae4b71975c2fb5f2442df2ee457c811909d9ae343cb31b6850e905f8256b81a",
    "auger-threaded-storage.step": "3008ccbea47bae590934fcef5106a5a904a1ab069ed188480a760ff2e13ce6ff",
    "auger-cap-threaded.step": "2a2e8eda516330268003ad40faeb1b4339300c8f2d00e928ec4c8550259e6b82",
}
SKIP = {"beaker", "beaker_riser"}   # the animation's own vessel and its seat (ours, below) stand in for v5's beaker
HIGHLIGHT = (0.10, 0.65, 0.35)   # powder-doser's render.py marks a module this green
HL_KEYS = {"carriage", "sam_mounting_plate", "auger_cap", "armature_tab"}
FINE = ("sprocket", "pinion")
COARSE = ("chain", "clevis", "stub", "loc_pin", "magnet", "insert", "eclip", "hall", "m2", "m3", "m5", "nut", "tnut",
          "bolt", "standoff", "kc_", "vee", "door_spring")
BUDGET = {"auger": 4000, "auger_cap": 1500, "chain_outer": 240, "chain_inner": 200, "chain_a1": 400,
          "actuator_body": 3000, "nema34": 3000}   # triangles per part
GLASSY = {"hr202i_front_glass", "hr202i_door_left", "hr202i_door_right", "hr202i_top_door", "panel_side_hatch",
          "panel_side", "panel_front_hatch", "panel_back", "panel_top", "hatch_front", "hatch_side"}
GLASS_ALPHA = {"hr202i": 0.30, "panel": 0.10, "hatch": 0.10}
OURS = (0.10, 0.55, 0.55)        # our printed parts and fittings on the rig, in the lab's PETG teal (charge.PRINT)
OURS_DARK = (0.25, 0.27, 0.30)


def _T(t) -> np.ndarray:
    M = np.eye(4)
    M[:3, 3] = t
    return M


def fetch_reference() -> None:
    REF.mkdir(parents=True, exist_ok=True)
    for name, digest in REFERENCE.items():
        path = REF / name
        if not path.exists():
            req = urllib.request.Request(REF_URL.format(sha=SHA, name=name), headers={"User-Agent": "Mozilla/5.0"})
            path.write_bytes(urllib.request.urlopen(req, timeout=300).read())
        d = hashlib.sha256(path.read_bytes()).hexdigest()
        if d != digest:
            raise RuntimeError(f"{name}: sha256 {d}, expected {digest} (powder-doser {SHA[:7]})")


def _import_v5():
    """Import the verbatim copies. Their vendor helpers do ``from common import step_or_none``, and the lab's own
    ``lab_models/common.py`` is imported as ``common`` too (vlm.py, instruments.py): swap it out for the import, put it
    back after, and take the vendor folder off sys.path again so neither shadows the other."""
    saved = sys.modules.pop("common", None)
    sys.path.insert(0, str(VENDOR))
    sys.path.insert(0, str(V5))
    try:
        import actuonix  # noqa: F401
        import mcmaster  # noqa: F401
        import vendor_other  # noqa: F401
        import layout
        import params
    finally:
        sys.modules.pop("common", None)
        if saved is not None:
            sys.modules["common"] = saved
        while str(VENDOR) in sys.path:
            sys.path.remove(str(VENDOR))
    return layout, params


fetch_reference()
CL, CP = _import_v5()          # the carousel's own layout and dimension table, verbatim
P5 = CL.P5

N_MODULES = CP.N_MODULES
MODULE_LINKS = CP.MODULE_LINKS
DIRN = CP.RUN_DIRECTION
DOCK_EXT = CP.PARK_DROP                            # v5's State.ext: 0 parked on its guides, PARK_DROP docked
TILT = CL.frame_dose_tilt(CP.TILT_DOSE_WORLD)      # 30°
TILT_MAX = CP.TILT_MAX_V5                          # 40°: past about 41° the lift bar rises into the next modules
TOP_OPEN = P5.HR2_TOP_OPEN                         # 205 mm: the top door slid back over the tower
SIDE_OPEN = P5.HR2_DOOR_OPEN                       # 205 mm: the -y side door slid back
PAN_XY = np.array(CL.scale_pan_target()[:2], float)   # the pan's centre, under the dose point
PAN_TOP = float(CP.HR2_PAN_TOP)                    # 50 mm over the bench
RIM_Z = float(CP.BEAKER_RIM_Z)                     # 282 mm: v5's beaker rim, 154 mm under the exit
DOOR_TOP_Z = 291.0                                 # the side doors' opening's top (A&D's DXF, params.BEAKER_RIM_Z note)
DOOR_SILL_Z = float(CP.HR2_FLOOR)                  # 40 mm: the chamber floor and the side doors' sills
DOOR_PLANE_Y = float(PAN_XY[1] - CP.HR2_CH[0] / 2)   # the chamber's -y inner face (the side door's opening)
DOOR_X = (float(PAN_XY[0] - CP.HR2_PAN_Y + CP.HR2_CH_Y), float(PAN_XY[0] - CP.HR2_PAN_Y + CP.HR2_CH_Y + CP.HR2_DOOR[0]))

# ---------------------------------------------------------------------------------------- ours: the vessel shuttle
# A robot can't do what v5's front hatch leaves to a hand. The 2F-85's knuckles span 127-138 mm whatever it grips
# (ur_arm.gripper_fk), and the way to the balance's -y side door passes between the frame's front post (x <= -36.4) and
# the -y station post that carries the P16 (x >= 81): 117 mm. So a gripper never reaches the pan. Instead a vessel
# shuttle (ours) carries it: a fork on a belt slide along y, under a port in the -y acrylic panel, takes the vessel
# from the arm 71 mm outside the panel, carries it in through the open side door 6 mm over our pedestal riser on the
# pan, and lowers 10 mm, which sets the vessel down and drops the fork 4 mm clear under it, so only the vessel's foot
# touches the riser and nothing else touches the balance; then the fork backs out round the pedestal through its slot.
VIAL_H, VIAL_R = 61.0, 14.0                        # the 20 mL vial (28 x 61 mm), as props.vial_glass
CUP_D, CUP_L = 19.05, 63.5                         # a charge cup (charge.py: 3/4 in bar, 2.5 in long)
VESSEL_H = {"vial": VIAL_H, "cup": CUP_L}
SEAT_Z = 219.0               # the vessel's foot on our pedestal: a cup's rim at 282.5 mm, the vial's at 280 (v5's beaker
#                              rim is 282): falls of 153-156 mm, as v5's 154; lifted 6 mm on the fork, the cup's rim
#                              (288.5) still passes under the side door opening's 291 mm top (A&D's DXF)
SEAT_LIFT = 6.0                                    # the fork carries the vessel this far over the pedestal
FORK_DROP = 10.0                                   # the fork's lift: 6 mm to set the vessel down, 4 mm clear under it
PED_D, PED_H = 11.0, 20.0                          # the pedestal's neck (the fork's slot is 13 mm), on v5's riser tube
SEAT_FOOT_D, SEAT_TUBE_D = CP.BRISER_FOOT_D, CP.BRISER_TUBE_D   # v5 riser's 80 mm foot and 44 mm tube
Y_HAND = -270.0              # where the arm sets the vessel on the fork: 71 mm outside the -y panel (y -199)
TRAVEL = float(PAN_XY[1] - Y_HAND)                 # 254.8 mm of shuttle travel
FORK_L, FORK_W, FORK_T, SLOT_W, SLOT_L = 180.0, 36.0, 4.0, 13.0, 30.0
RAIL_Y = (-110.0, -470.0)                          # the slide's rail, under the fork's path
RAIL_Z = (110.0, 130.0)
CARR_Z = (130.0, 150.0)
PORT = (0.0, 67.0, 100.0, 300.0)                   # the port cut in the -y acrylic panel (x0, x1, z0, z1)


def seat_base_z(kind: str = "vial") -> float:
    """The vessel's foot on our pedestal, rig frame (one pedestal height for the vial and the cups)."""
    return SEAT_Z


def vessel_at(kind: str = "vial", shuttle: float = 0.0, fork: float = 0.0) -> np.ndarray:
    """Base centre of a vessel riding the fork, rig frame: shuttle 0 over the pan, 1 at the hand-over outside the -y
    panel; fork 0 carrying (SEAT_LIFT over the pedestal), 1 dropped (the vessel on the pedestal, if over the pan)."""
    z = SEAT_Z + SEAT_LIFT - FORK_DROP * fork
    if shuttle < 1e-6:
        z = max(z, SEAT_Z)
    return np.array([PAN_XY[0], PAN_XY[1] - TRAVEL * shuttle, z])


def seat_mesh(kind: str = "vial") -> pv.PolyData:
    """Ours: the pedestal riser on the pan, v5's riser (80 mm foot, 44 mm tube) with an 11 mm neck PED_H tall on top,
    chamfered, that the vessel stands on and the fork's 13 mm slot passes round. Rig frame."""
    z1 = SEAT_Z
    z0 = z1 - PED_H
    prof = np.array([[0.0, PAN_TOP], [SEAT_FOOT_D / 2, PAN_TOP], [SEAT_FOOT_D / 2, PAN_TOP + 3.0],
                     [SEAT_TUBE_D / 2, PAN_TOP + 3.0], [SEAT_TUBE_D / 2, z0 - 3.0], [SEAT_TUBE_D / 2 - 3.0, z0],
                     [PED_D / 2, z0], [PED_D / 2, z1 - 0.8], [PED_D / 2 - 0.8, z1], [0.0, z1]])
    line = pv.PolyData(np.c_[prof[:, 0], np.zeros(len(prof)), prof[:, 1]],
                       lines=np.r_[len(prof), np.arange(len(prof))])
    m = line.extrude_rotate(resolution=56, capping=False).triangulate().clean()
    return m.translate((*PAN_XY, 0.0), inplace=False)


def shuttle_meshes() -> dict[str, pv.PolyData]:
    """Ours: the shuttle's fixed parts (its rail, a bracket on the -y base rail, a leg outside the frame) and its
    moving parts (carriage, column and fork) drawn with the shuttle in (over the pan) and the fork carrying."""
    x = float(PAN_XY[0])
    yc = float(PAN_XY[1]) + SLOT_L / 2 - FORK_L           # the carriage's centre with the slot over the pan
    zf = SEAT_Z + SEAT_LIFT                                # the fork's top, carrying
    box = lambda *b: pv.Box(bounds=b).triangulate()       # noqa: E731
    rail = box(x - 10, x + 10, RAIL_Y[1], RAIL_Y[0], *RAIL_Z)
    bracket = box(x - 10, x + 10, -186.0, -174.0, 35.0, RAIL_Z[0])          # on the -y base rail (z 15-35)
    leg = box(x - 10, x + 10, RAIL_Y[1] + 5, RAIL_Y[1] + 25, 0.0, RAIL_Z[0])
    carriage = box(x - 20, x + 20, yc - 25, yc + 25, *CARR_Z)
    column = box(x - 5, x + 5, yc - 5, yc + 5, CARR_Z[1], zf - FORK_T)
    y0, y1 = yc - 5, yc - 5 + FORK_L
    fork = box(x - FORK_W / 2, x + FORK_W / 2, y0, y1 - SLOT_L, zf - FORK_T, zf)
    for sx in (-1, 1):                                     # the two tines round the slot
        a, b = sorted((x + sx * SLOT_W / 2, x + sx * FORK_W / 2))
        fork = fork.merge(box(a, b, y1 - SLOT_L, y1, zf - FORK_T, zf))
    return {"fixed": rail.merge(bracket).merge(leg), "moving": carriage.merge(column).merge(fork)}


def pusher_meshes() -> dict[str, pv.PolyData]:
    """Ours, not powder-doser's: the actuators a robot-served station needs for the balance's doors (v5 opens them by
    hand). Each is a slim belt slide on the bench inside the U-shaped base, clear of the balance, whose finger takes the
    door's grip only while it moves the door: the side-door slide along the balance's -y face, its finger rising to
    the -y door's grip; the top-door slide along the +y face, its finger reaching over to the top door's front grip.
    Rig frame, doors shut (the fingers move with the doors)."""
    x0 = float(PAN_XY[0] - CP.HR2_PAN_Y)                 # the balance's front (display nose)
    xd0, xd1 = DOOR_X
    yb = float(PAN_XY[1])
    hw = CP.HR2_W / 2
    out = {}
    for name, side in (("side", -1), ("top", 1)):
        yr = yb + side * (hw + 14.0)                    # the slide's centre line, 14 mm off the balance's side
        rail = pv.Box(bounds=(x0 + 70.0, x0 + 420.0, yr - 8.0, yr + 8.0, 0.0, 16.0))
        out[f"{name}_rail"] = rail.triangulate()
    # fingers, at their doors' shut positions
    ys = yb - hw - 14.0
    xg = xd1 + 2.0                                       # the -y door's back edge
    f_side = pv.Box(bounds=(xg, xg + 10.0, ys - 6.0, ys + 6.0, 16.0, 150.0)).merge(
        pv.Box(bounds=(xg, xg + 10.0, ys, yb - hw - 2.0, 140.0, 150.0))).merge(
        pv.Box(bounds=(xg - 12.0, xg + 22.0, ys - 10.0, ys + 10.0, 16.0, 36.0)))
    yt = yb + hw + 14.0
    xt = xd0 + 8.0                                       # the top door's front grip
    f_top = pv.Box(bounds=(xt - 5.0, xt + 5.0, yt - 6.0, yt + 6.0, 16.0, 322.0)).merge(
        pv.Box(bounds=(xt - 5.0, xt + 5.0, 26.0, yt + 6.0, 316.0, 322.0))).merge(
        pv.Box(bounds=(xt - 12.0, xt + 12.0, yt - 10.0, yt + 10.0, 16.0, 36.0)))
    out["side_finger"] = f_side.triangulate()
    out["top_finger"] = f_top.triangulate()
    return out


def _sources_hash() -> str:
    h = hashlib.sha256()
    for f in sorted(V5.glob("*.py")) + sorted(VENDOR.glob("*.py")) + [Path(__file__)]:
        h.update(f.read_bytes())
    return h.hexdigest()[:12]


def _tess(shape, tol: float) -> pv.PolyData:
    verts, tris = shape.tessellate(tol, 0.35)
    if not tris:
        return pv.PolyData()
    pts = np.array([(v.x, v.y, v.z) for v in verts], float)
    faces = np.hstack([[3, *t] for t in tris])
    return pv.PolyData(pts, faces).clean()


def _keys(pl) -> list[str]:
    return sorted({p.key for p in pl} - SKIP)


def part_meshes() -> dict[str, pv.PolyData]:
    """Every unique part, tessellated once in its own frame and cached."""
    cache = HERE / ".cache" / f"carousel5_{_sources_hash()}.pkl"
    if cache.exists():
        return pickle.loads(cache.read_bytes())
    cache.parent.mkdir(exist_ok=True)
    out = {}
    keys = set(_keys(CL.placements(CL.State(ext=0.0)))) | set(_keys(CL.placements(CL.State(tilt=TILT))))
    for key in sorted(keys):
        tol = 0.15 if key.startswith(FINE) else 0.8 if key.startswith(COARSE) else 0.4
        m = _tess(CL.shape(key), tol)
        n = BUDGET.get(key)
        if n and m.n_cells > n:              # threads and chain links: far more triangles than show at this scale
            m = m.triangulate().decimate_pro(1 - n / m.n_cells, preserve_topology=False).clean()
        if key == "panel_side":           # ours: the port the arm reaches the -y side door through
            m = _cut_port(m)
        out[key] = m
    cache.write_bytes(pickle.dumps(out))
    return out


def _cut_port(m: pv.PolyData) -> pv.PolyData:
    """The -y panel with PORT cut out of it, in the panel's own frame."""
    M = next(p.M for p in CL.placements(CL.State(ext=0.0, beaker=False)) if p.key == "panel_side")
    x0, x1, z0, z1 = PORT
    corners = np.array([[x, y, z, 1.0] for x in (x0, x1) for y in (-400.0, 0.0) for z in (z0, z1)])
    loc = (np.linalg.inv(M) @ corners.T).T[:, :3]
    lo, hi = loc.min(0), loc.max(0)
    return m.clip_box((lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]), invert=True).extract_surface().triangulate().clean()


BOARD_AT = (-530.0, -360.0)     # the electronics board's corner (min x, min y), rig frame: on tray B, left of the
#                                 rig, behind the vial rack


def board_move(pl, parts) -> np.ndarray:
    """The rig's electronics board stands on the bench beside the frame in powder-doser; on tray B it lies left of
    the rig, turned 90° (its long side along the tray's depth), its corner at BOARD_AT."""
    Rz = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]], float)
    pts = np.vstack([parts[p.key].points @ p.M[:3, :3].T + p.M[:3, 3] for p in pl if p.group == "elec"]) @ Rz.T
    M = np.eye(4)
    M[:3, :3] = Rz
    M[:3, 3] = np.array([BOARD_AT[0] - pts[:, 0].min(), BOARD_AT[1] - pts[:, 1].min(), 0.0])
    return M


def _alpha(key: str) -> float:
    if key in GLASSY:
        return next(a for k, a in GLASS_ALPHA.items() if key.startswith(k))
    return 1.0


TOP_Z = float(CP.Z_TOP_RAIL + CP.EXT)               # 851: the top rails' top face


def lowered(pl, top=True):
    """Ours, for tray B: the top acrylic panel laid on the top rails instead of on its 6 mm standoffs (which go into
    the rails), so the rig stands 854 mm tall, under the Shuttle's 856.5 mm product height (vlm.MAX_GOODS_H, an
    estimate); powder-doser's 860 mm would not pass the opening. No other part moves."""
    if not top:
        return pl
    out = []
    for p in pl:
        if p.key == "panel_top" or (p.key == "standoff" and p.M[2, 3] > TOP_Z - 1.0):
            M = p.M.copy()
            M[2, 3] -= CP.PANEL_STANDOFF
            p = CL.Placement(p.key, p.name, M, p.step, p.color, p.group, p.explode, p.module)
        out.append(p)
    return out


class Carousel:
    """The rig as a handful of actors (one per colour) in Scene group `group`; ``set(**state)`` re-poses every
    instance from ``layout.placements`` and rewrites the actors' points. The State's keyword names are v5's own:
    shift (links), ext (mm, 0 parked .. DOCK_EXT docked), tilt (deg), spin (rad), tap, magnet_on, top_door and
    side_door (mm slid back), hatch_front / hatch_side (deg)."""

    def __init__(self, sc, group: str, prefix: str = "md", highlight: int | None = None, **state):
        """`highlight`: a module (0-based) whose plate and cap are drawn green, as powder-doser's own movie marks one."""
        self.sc, self.group = sc, group
        self.parts = part_meshes()
        self.state = dict(shift=0.0, ext=0.0, tilt=0.0, spin=0.0, tap=0.0, magnet_on=False, top_door=0.0,
                          side_door=0.0, shuttle=1.0, fork=0.0)
        self.state.update(state)
        pl = self._pl()
        self.keys = [p.key for p in pl]
        self.board = board_move(pl, self.parts)
        # one actor per (colour, glass or not, the highlighted module or not, riding a carriage or fixed): the
        # others' modules and carriages can then be ghosted to show the docked one, which rides inside the loop
        groups: dict[tuple, list[int]] = {}
        for i, p in enumerate(pl):
            if p.key in SKIP:
                continue
            hl = highlight is not None and p.module == highlight
            col = HIGHLIGHT if (hl and p.key in HL_KEYS) else p.color
            groups.setdefault((tuple(round(c, 3) for c in col), _alpha(p.key), hl, p.module >= 0), []).append(i)
        self.actors = []
        self.others = []                 # actors of the modules and carriages other than the highlighted one
        self.glass = []
        for j, ((col, a, hl, rides), idx) in enumerate(sorted(groups.items())):
            name = f"{prefix}/c{j}"
            if rides and not hl and highlight is not None:
                self.others.append(name)
            polys, n0, slices = [], 0, []
            for i in idx:
                m = self.parts[pl[i].key]
                slices.append((i, n0, n0 + m.n_points))
                polys.append(m)
                n0 += m.n_points
            mesh = pv.merge(polys, merge_points=False) if len(polys) > 1 else polys[0].copy()
            spec = 0.6 if col in ((0.62, 0.64, 0.67), (0.8, 0.82, 0.85)) or a < 1 else 0.3
            sc.add(name, mesh, col, group, specular=spec, opacity=a)
            if a < 1:
                self.glass.append(name)
            self.actors.append((name, mesh, slices))
        # ours: the door pushers (their fingers in child groups that slide with the doors), the pedestal riser on the
        # pan and the vessel shuttle (its carriage and fork in a child group, self.fork_group)
        pm = pusher_meshes()
        for k in ("side_rail", "top_rail"):
            sc.add(f"{prefix}/ours_{k}", pm[k], OURS_DARK, group, specular=0.4)
        for k in ("side", "top"):
            g = f"{group}_{k}finger"
            sc.add(f"{prefix}/ours_{k}_finger", pm[f"{k}_finger"], OURS, g, specular=0.3)
            sc.parent[g] = group
        sc.add(f"{prefix}/ours_seat", seat_mesh(), OURS, group, specular=0.3)
        sm = shuttle_meshes()
        sc.add(f"{prefix}/ours_shuttle_rail", sm["fixed"], OURS_DARK, group, specular=0.4)
        self.fork_group = f"{group}_fork"
        sc.add(f"{prefix}/ours_shuttle_fork", sm["moving"], OURS, self.fork_group, specular=0.3)
        sc.parent[self.fork_group] = group
        self.prefix = prefix
        self._last: list | None = None
        self.set()

    def reparent(self, group: str, parent: str) -> None:
        """Move Scene group `group` under `parent`, keeping where it is in the world (a vessel set down by the fork,
        or taken up by it)."""
        sc = self.sc
        M = sc.world(group)
        sc.parent[group] = parent
        sc.gmat[group] = np.linalg.inv(sc.world(parent)) @ M

    def vessel_world(self, shuttle: float | None = None, fork: float | None = None) -> np.ndarray:
        """World position of a vessel's base on the fork (now, or at the given shuttle and fork states)."""
        s = self.state["shuttle"] if shuttle is None else shuttle
        f = self.state["fork"] if fork is None else fork
        return (self.sc.world(self.group) @ np.r_[vessel_at("vial", s, f), 1.0])[:3]

    def _pl(self):
        s = self.state
        st = CL.State(shift=s["shift"], ext=s["ext"], tilt=s["tilt"], spin=s["spin"], tap=s["tap"],
                      magnet_on=s["magnet_on"], top_door=s["top_door"], side_door=s["side_door"], beaker=False)
        return lowered(CL.placements(st))

    def set(self, **kw):
        self.state.update(kw)
        pl = self._pl()
        assert [p.key for p in pl] == self.keys, "the rig's instance list changed with its state"
        Ms = [p.M if p.group != "elec" else self.board @ p.M for p in pl]
        last, self._last = self._last, Ms
        self.sc.gmat[f"{self.group}_sidefinger"] = _T((self.state["side_door"], 0.0, 0.0))
        self.sc.gmat[f"{self.group}_topfinger"] = _T((self.state["top_door"], 0.0, 0.0))
        self.sc.gmat[f"{self.group}_fork"] = _T((0.0, -TRAVEL * self.state["shuttle"], -FORK_DROP * self.state["fork"]))
        for name, mesh, slices in self.actors:
            if last is not None and all(np.array_equal(Ms[i], last[i]) for i, _, _ in slices):
                continue                     # nothing of this actor moved: keep its mesh (and its BVH in collide.py)
            pts = np.empty((mesh.n_points, 3))
            for i, a, b in slices:
                M = Ms[i]
                local = self.parts[pl[i].key].points
                pts[a:b] = local @ M[:3, :3].T + M[:3, 3]
            mesh.points = pts
            self.sc.set_mesh(name, mesh)

    # --------------------------------------------------------------------------------------- moves
    def ghost(self, a1: float):
        """An update(u) that fades the other modules and their carriages to opacity a1 (1: solid)."""
        a0 = {n: self.sc.base_alpha[n] for n in self.others}

        def up(u):
            for n in self.others:
                self.sc.base_alpha[n] = a0[n] + (a1 - a0[n]) * u
        return up

    def to(self, **target):
        """An update(u) that eases the state from now to `target` (numbers only; flags switch at the start)."""
        start = {k: self.state[k] for k in target}

        def up(u):
            kw = {}
            for k, v in target.items():
                kw[k] = v if isinstance(v, bool) else start[k] + (v - start[k]) * u
            self.set(**kw)
        return up

    def index_to(self, module: int):
        """Chain shift that brings `module` (0-based) to the station, the way the rig runs, from the current shift."""
        cur, n_links = self.state["shift"], CP.N_LINKS
        # carriage k sits at the station when MODULE_LINKS * k + shift = 0 (mod N_LINKS): shift 0 has carriage 1 there
        if DIRN < 0:
            return cur - (MODULE_LINKS * module + cur) % n_links
        return cur + (-MODULE_LINKS * module - cur) % n_links

    def exit_point(self) -> np.ndarray:
        """Auger outlet at the station, rig frame, at the current tilt (on the hinge axis: it doesn't move)."""
        return np.asarray(CL.exit_point(self.state["tilt"]), float)


def vial_seat(kind: str = "vial") -> np.ndarray:
    """Base centre of the vessel (the vial, or a charge cup) on our pedestal on the pan, rig frame."""
    return np.array([PAN_XY[0], PAN_XY[1], seat_base_z(kind)])


if __name__ == "__main__":
    import time
    t0 = time.time()
    m = part_meshes()
    print(len(m), "parts,", sum(x.n_cells for x in m.values()), "triangles, %.1f s" % (time.time() - t0))
    pl = CL.placements(CL.State(ext=0.0, beaker=False))
    print(len(pl), "instances,", sum(m[p.key].n_cells for p in pl if p.key not in SKIP), "triangles placed")
    t0 = time.time()
    for _ in range(5):
        CL.placements(CL.State(ext=10.0, tilt=12.0, beaker=False))
    print("placements: %.3f s each" % ((time.time() - t0) / 5))
    print("pan", PAN_XY, "exit", np.round(CL.exit_point(TILT), 1), "door plane y %.1f, x %.1f..%.1f" % (DOOR_PLANE_Y, *DOOR_X))
    pts = np.array([p.M[:3, 3] for p in pl])
    print("instance origins: x %.0f..%.0f, y %.0f..%.0f, z %.0f..%.0f" % (*pts[:, 0].min(0).ravel()[:1], pts[:, 0].max(),
                                                                         pts[:, 1].min(), pts[:, 1].max(), pts[:, 2].min(),
                                                                         pts[:, 2].max()))
