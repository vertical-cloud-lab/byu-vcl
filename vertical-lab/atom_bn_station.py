"""The crucible's cleaning bench, the fume hood's spray station, the tools and the crucible's BN coat (PR #353, #303).

Everything here is drawn in the rePowder's model frame (repowder/model.py: x right, y back, z up from the floor, mm)
and hung on the scene group "rp", so a point written here is where it is on the floor beside the machine. The
station stands to the right of the atomizer's taped area (atom_base.py: the tape runs to x = 1500).

What is ours and what is bought (notes/atom_bn.md has the sources):
  * the bench, the two-axis positioner (a soft-jawed three-jaw chuck on a trunnion: spin and a 180 deg flip, with a
    small knocker), the dark tray, the tool holsters, the side light: ours (a positioner like this is a small
    welding-positioner layout; sizes are ours).
  * the brush, the scraper and the seat plug: ours (a bought nylon bore brush and an acetal blade on our handles).
  * the vacuum: the lab's Nilfisk CFM 118EXP (atom_nilfisk.py's model when it exists, else a stand-in drawn here),
    its conductive hose and cuff and the 11 in aluminium crevice tool 01768900 (vacuum SOP; bought), on our grip clamp.
  * the fume hood: the Labconco Protector XStream 4 ft as instruments_r7.py draws it (bought; its etch beakers and
    the coupon are left out here). In it: the open-topped box with a turntable on a short lift, the plug's
    holster, the spray tool's cradle and the drying rack: ours.
  * the spray: Momentive Boron Nitride Spray II, 13 oz aerosol, McMaster 10515K35 (bought); the clamp and the valve
    pusher that hold and fire it: ours. The can's size (68 x 230 mm with its actuator) is assumed: a standard 211
    can, the size most 12-16 oz aerosols come in.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import charge as C                       # noqa: E402  lathe()
from scene import R, T                   # noqa: E402

try:
    import repowder.model as M           # noqa: E402
except Exception:                        # noqa: BLE001
    import alloy_atomize as _AA          # noqa: E402
    M = _AA.M

# ------------------------------------------------------------------------------------------------ the crucible
CR_H = M.BORE_STRAIGHT + M.FLOOR_CONE_H + M.CRUCIBLE_BOTTOM      # 115.3 mm, base to rim
CR_RO = M.CRUCIBLE_ID / 2 + M.CRUCIBLE_WALL                     # 37.65
CR_RI = M.CRUCIBLE_ID / 2                                       # 28.55
Z_FLOOR = M.FLOOR_CONE_H + M.CRUCIBLE_BOTTOM                    # 34.2: where the bore meets the floor cone, over the base
HOLE_R = M.POUR_HOLE_D / 2                                       # 3.45
SEAT_R = 12.0                     # the seat ring round the hole that the sealing rod seals on: never scraped, masked
CR_GRIP = close = None            # set in atom_bn (ur_arm.close_for)

# colours
GRAPHITE = M.GRAPHITE
OLD_COAT = (0.80, 0.80, 0.77)     # fired BN, a little grey after a run
DAMAGED = (0.47, 0.45, 0.42)      # cracked and lifted coat, metal stuck to it
SCRAPED = (0.36, 0.36, 0.38)      # the thin grey bonded layer left after scraping (bronze plan)
WET = (0.66, 0.74, 0.82)          # a wet coat: darker, with a shine
MATTE = (0.95, 0.95, 0.92)        # dry BN: matte white
SKULL_C = (0.62, 0.45, 0.30)      # 630 bronze skull
SEAT_C = (0.30, 0.30, 0.32)

# which zones the run left damaged (and the cleaning scrapes back): the floor and the floor-wall corner, where the
# Oct 30 coat and the Nov 2 touch-up cracked (bronze plan), and three wall patches (ours: an example)
N_SEC = 12
DAMAGE = {("floor", k) for k in range(N_SEC)} | {("low", k) for k in (1, 2, 3, 7, 8)} | {("up", k) for k in (2, 8)}


def crucible_mesh(sc) -> pv.PolyData:
    """The model's own crucible (repowder/model.py furnace_parts: the 'crucible' part), as the rePowder's loader drew
    it, moved so its base centre is the origin."""
    import alloy_atomize as AA
    for name in sc.members(AA.g("crucible")):
        if "crucible" in name and not name.endswith("#cut") and sc.cutrole.get(name) != "half":
            mesh = pv.wrap(sc.actors[name].GetMapper().GetInput()).copy()
            return mesh.translate((0.0, 0.0, -M.CRUCIBLE_BASE), inplace=False)
    raise KeyError("no crucible mesh in the scene")


def _patch(fn, nu, nv) -> pv.PolyData:
    """A surface patch from fn(u, v) -> xyz on a grid, triangulated."""
    us, vs = np.linspace(0, 1, nu), np.linspace(0, 1, nv)
    pts = np.array([fn(u, v) for v in vs for u in us], float)
    faces = []
    for j in range(nv - 1):
        for i in range(nu - 1):
            a = j * nu + i
            faces += [3, a, a + 1, a + nu + 1, 3, a, a + nu + 1, a + nu]
    return pv.PolyData(pts, faces=np.array(faces)).compute_normals(auto_orient_normals=False)


def coat_zones() -> dict:
    """The inside of the crucible as zones (in its base frame): 12 sectors of the upper wall ('up'), the lower wall
    ('low') and the floor cone outside the seat ('floor'); then the seat ring round the hole ('seat'). Each is a thin
    skin 0.25 mm inside the surface, so its colour is the coat's."""
    out = {}
    ri = CR_RI - 0.25
    z0, zm, z1 = Z_FLOOR, Z_FLOOR + 40.0, CR_H - 1.2
    for k in range(N_SEC):
        a0, a1 = 2 * math.pi * k / N_SEC, 2 * math.pi * (k + 1) / N_SEC

        def wall(za, zb):
            return lambda u, v: (ri * math.cos(a0 + (a1 - a0) * u), ri * math.sin(a0 + (a1 - a0) * u),
                                 za + (zb - za) * v)
        out[("low", k)] = _patch(wall(z0, zm), 6, 5)
        out[("up", k)] = _patch(wall(zm, z1), 6, 5)

        def floor(u, v):
            r = SEAT_R + (CR_RI - 0.3 - SEAT_R) * v
            a = a0 + (a1 - a0) * u
            return (r * math.cos(a), r * math.sin(a), Z_FLOOR + M.floor_z(r) + 0.25)
        out[("floor", k)] = _patch(floor, 6, 4)

    def seat(u, v):
        r = HOLE_R + 0.2 + (SEAT_R - HOLE_R - 0.2) * v
        a = 2 * math.pi * u
        return (r * math.cos(a), r * math.sin(a), Z_FLOOR + M.floor_z(r) + 0.25)
    out[("seat", 0)] = _patch(seat, 37, 3)
    return out


def skull_mesh() -> pv.PolyData:
    """What stays in the crucible after a pour: a skull of metal and slag on the floor (178 SOP: "slag always remains
    at the bottom"). A lens 44 mm across, 9 mm at its thickest, on the floor cone (ours, a typical size)."""
    rs = np.linspace(0.0, 22.0, 12)
    base = [float(M.floor_z(max(r, HOLE_R)) - M.floor_z(HOLE_R)) + 0.6 for r in rs]
    prof = [(float(r), b) for r, b in zip(rs, base)]
    prof += [(float(r), b + 9.0 * (1 - (r / 22.0) ** 2) + 0.3) for r, b in zip(rs[::-1], base[::-1])][1:]
    m = C.lathe(prof, res=48)
    return m.translate((0, 0, Z_FLOOR + M.floor_z(HOLE_R)), inplace=False)


def plug_meshes() -> dict:
    """The seat plug (ours): a PTFE cone that sits on the seat ring and a spigot in the 6.9 mm hole, so no spray gets
    on the seat or down the bore; a 5 mm stem and a round 20 mm handle for the 2F-85 (round, so the turntable's turn doesn't matter), 12 mm over the rim. Its
    frame: the crucible's base centre (where it is when it is in)."""
    zh = Z_FLOOR + M.floor_z(HOLE_R)
    prof = [(0.0, zh - 9.0), (HOLE_R - 0.25, zh - 9.0), (HOLE_R - 0.25, zh), (SEAT_R + 0.8, Z_FLOOR + M.floor_z(SEAT_R + 0.8) + 0.3)]
    prof += [(SEAT_R + 0.8, Z_FLOOR + M.floor_z(SEAT_R + 0.8) + 2.5), (2.5, zh + 9.0), (0.0, zh + 9.0)]
    cone = C.lathe(prof, res=40)
    stem = pv.Cylinder(center=(0, 0, (zh + 9.0 + CR_H + 12.0) / 2), direction=(0, 0, 1), radius=2.5,
                       height=CR_H + 12.0 - zh - 9.0, resolution=16).triangulate()
    handle = pv.Cylinder(center=(0, 0, CR_H + 23.0), direction=(0, 0, 1), radius=GRIP_W / 2, height=22.0,
                         resolution=32).triangulate()
    return {"plug cone": (cone, (0.93, 0.93, 0.90)), "plug stem": (stem.merge(handle), (0.86, 0.87, 0.88))}


PLUG_GRIP_Z = CR_H + 23.0         # the handle's centre over the crucible's base


# ------------------------------------------------------------------------------------------------ the layout
BENCH = dict(x0=1700.0, x1=2380.0, y0=-229.0, y1=371.0, top=900.0, t=30.0)
POS = dict(x=2030.0, y=-60.0, axis=1070.0, face=20.0, body_r=55.0, ux=100.0)   # the positioner's trunnion
TRAY = dict(x=2030.0, y=-60.0, w=170.0, d=170.0, h=15.0)                       # the dark tray under it
HOLSTERS = {"brush": (2205.0, -110.0), "scraper": (2280.0, -110.0), "vac": (2240.0, 30.0)}
LIGHT = (1890.0, 40.0)            # the side light's post, behind the chuck's left upright
HOOD_AT = (3000.0, 250.0)         # the hood's footprint centre (instruments_r7.FH: 1219 x 958; front at y = -229)
HOOD_Z0 = 932.0                   # its work surface
SASH_Y = (HOOD_AT[1] - 479.0 + 26.0, HOOD_AT[1] - 479.0 + 44.0)     # the sash and its handle: y -203 .. -185
SASH_BOTTOM = 960.0 + 457.0       # the sash raised to its 18 in (457 mm) working stop: its bottom edge at 1417
BOX = dict(x=2760.0, y=105.0, inner=130.0, deep=150.0, wall=2.0, plinth=60.0, floor=3.0, h=193.0)   # inside: 130 x 150 x 193
CRU_IN_BOX = (2760.0, 115.0)     # the crucible stands 10 mm behind the box centre: 47 mm in front of it for the spray
TT = dict(r=45.0, t=8.0, stroke=152.0)  # turntable on a lift (ours): up 152 mm for the hand-over
RACK = (2945.0, 115.0)             # the drying rack, the crucible upside down on it
PLUG_HOLSTER = (2610.0, 60.0)
CAN_CRADLE = (3180.0, -95.0)      # where the spray tool rests (the can inside, its handle at the sash)
NILFISK_AT = (1560.0, 560.0)      # the vacuum stands behind the bench's left end, out of the arm's way

BOX_FLOOR = HOOD_Z0 + BOX["plinth"] + BOX["floor"]       # 995
BOX_RIM = BOX_FLOOR + BOX["h"]                            # 1188: 70 mm (2.75 in) over the crucible's rim
TT_LOW = BOX_FLOOR + TT["t"]                              # the turntable's top, spraying: 1003
TT_HIGH = TT_LOW + TT["stroke"]                           # and at the hand-over: the crucible's top 82 mm over the rim
RACK_TOP = HOOD_Z0 + 120.0                                # the inverted crucible's rim rests here


def _box(x0, x1, y0, y1, z0, z1):
    return pv.Box(bounds=(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))).triangulate()


def _cyl(c, d, r, h, res=32):
    return pv.Cylinder(center=c, direction=d, radius=r, height=h, resolution=res).triangulate()


def _ring(x, y, z0, h, ro, ri, res=40):
    return C.lathe([(ri, 0.0), (ro, 0.0), (ro, h), (ri, h)], res=res).translate((x, y, z0), inplace=False)


def bench_meshes() -> dict:
    b = BENCH
    top = _box(b["x0"], b["x1"], b["y0"], b["y1"], b["top"] - b["t"], b["top"])
    legs = None
    for x in (b["x0"] + 30, b["x1"] - 30):
        for y in (b["y0"] + 30, b["y1"] - 30):
            leg = _box(x - 25, x + 25, y - 25, y + 25, 0.0, b["top"] - b["t"])
            legs = leg if legs is None else legs.merge(leg)
    shelf = _box(b["x0"] + 10, b["x1"] - 10, b["y0"] + 40, b["y1"] - 10, 150.0, 170.0)
    return {"bench top": (top, (0.30, 0.31, 0.33)), "bench frame": (legs.merge(shelf), (0.66, 0.67, 0.70))}


def positioner_static() -> dict:
    """The positioner's base plate and its two uprights (ours)."""
    p = POS
    base = _box(p["x"] - 130, p["x"] + 130, p["y"] - 45, p["y"] + 45, BENCH["top"], BENCH["top"] + 12)
    ups = None
    for s in (-1, 1):
        x = p["x"] + s * p["ux"]
        u = _box(x - 10, x + 10, p["y"] - 30, p["y"] + 30, BENCH["top"] + 12, p["axis"] + 28).merge(
            _cyl((x - s * 0.0, p["y"], p["axis"]), (1, 0, 0), 26, 20))
        ups = u if ups is None else ups.merge(u)
    motor = _cyl((p["x"] + p["ux"] + 32, p["y"], p["axis"]), (1, 0, 0), 28, 44)    # the flip motor and gearbox
    return {"positioner base": (base.merge(ups), (0.30, 0.45, 0.70)), "positioner motor": (motor, (0.20, 0.21, 0.23))}


def trunnion_meshes() -> dict:
    """In the trunnion's frame (origin on the flip axis, z along the chuck's axis when upright): the shaft, the
    chuck's body with its spin motor, and the face the crucible stands on."""
    p = POS
    shaft = _cyl((0, 0, 0), (1, 0, 0), 10.0, 2 * (p["ux"] - 10.0) - 1.0)
    body = _cyl((0, 0, (p["face"] - 30.0) / 2 - 10.0), (0, 0, 1), p["body_r"], p["face"] + 30.0 - 10.0, 48)
    hub = _cyl((0, 0, -26.0), (0, 0, 1), 30.0, 22.0)
    return {"chuck body": (body.merge(hub), (0.62, 0.63, 0.66)), "trunnion shaft": (shaft, (0.55, 0.56, 0.60))}


JAW_H, JAW_T, JAW_W = 35.0, 12.0, 18.0
JAW_OPEN = 5.0


def jaw_mesh(k: int) -> pv.PolyData:
    """Jaw k of three (acetal soft jaws, ours), its inner face on the crucible's outside (closed), in the trunnion's
    frame; opened it moves out along its radius (jaw_open())."""
    a = math.radians(90 + 120 * k)
    r0 = CR_RO + 0.4
    m = _box(r0, r0 + JAW_T, -JAW_W / 2, JAW_W / 2, POS["face"], POS["face"] + JAW_H)
    m = m.merge(_box(r0 + JAW_T - 2, POS["body_r"] - 2, -JAW_W / 2 - 3, JAW_W / 2 + 3, POS["face"] - 6, POS["face"]))
    return m.rotate_z(math.degrees(a), inplace=False)


def jaw_dir(k: int) -> np.ndarray:
    a = math.radians(90 + 120 * k)
    return np.array([math.cos(a), math.sin(a), 0.0])


def tray_meshes() -> dict:
    t = TRAY
    z0 = BENCH["top"]
    pan = _box(t["x"] - t["w"] / 2, t["x"] + t["w"] / 2, t["y"] - t["d"] / 2, t["y"] + t["d"] / 2, z0, z0 + 3)
    for s in (-1, 1):
        pan = pan.merge(_box(t["x"] + s * t["w"] / 2 - 2 * (s > 0), t["x"] + s * t["w"] / 2 + 2 * (s < 0),
                             t["y"] - t["d"] / 2, t["y"] + t["d"] / 2, z0, z0 + t["h"]))
        pan = pan.merge(_box(t["x"] - t["w"] / 2, t["x"] + t["w"] / 2, t["y"] + s * t["d"] / 2 - 2 * (s > 0),
                             t["y"] + s * t["d"] / 2 + 2 * (s < 0), z0, z0 + t["h"]))
    return {"dark tray": (pan, (0.10, 0.10, 0.11))}


def light_meshes() -> dict:
    """The side light (ours): a 10 W LED spot on a post behind the chuck, aimed low across the crucible's mouth."""
    x, y = LIGHT
    post = _cyl((x, y, BENCH["top"] + 180), (0, 0, 1), 8, 360)
    head = _cyl((x + 14, y - 14, BENCH["top"] + 352), (0.5, -0.5, -0.7), 22, 46)
    return {"side light post": (post, (0.25, 0.26, 0.28)), "side light": (head, (0.22, 0.23, 0.25))}


def light_beam() -> pv.PolyData:
    """The light's cone, drawn faint, onto the crucible's mouth when the light is on."""
    x, y = LIGHT
    tip = np.array([x + 20, y - 20, BENCH["top"] + 340.0])
    to = np.array([POS["x"], POS["y"], POS["axis"] + POS["face"] + CR_H - 20.0])
    d = to - tip
    L = float(np.linalg.norm(d))
    return pv.Cone(center=tuple(tip + d / 2), direction=tuple(-d / L), height=L, radius=34.0, resolution=32).triangulate()


# ------------------------------------------------------------------------------------------------ the tools
GRIP_W = 20.0                     # every tool's handle is 20 mm across the fingers (ours)


def _handle(z0=-20.0, z1=20.0):
    """A tool's handle block round its grip point (the tool frame's origin), 20 x 30 mm: the fingers close along x."""
    return _box(-GRIP_W / 2, GRIP_W / 2, -15.0, 15.0, z0, z1)


def brush_meshes() -> dict:
    """The bore brush (ours, from a bought one): a 50 mm round brush of soft nylon on an 8 mm stem, on our handle.
    Tool frame: the grip point at the origin, z down along the stem (the gripper's approach)."""
    stem = _cyl((0, 0, 85.0), (0, 0, 1), 4.0, 130.0, 16)
    head = _cyl((0, 0, 168.0), (0, 0, 1), 25.0, 40.0, 32)
    return {"brush handle": (_handle().merge(stem), (0.20, 0.36, 0.70)), "brush head": (head, (0.92, 0.86, 0.62))}


BRUSH_TIP = 188.0


def scraper_meshes() -> dict:
    """The scraper (ours): an acetal blade 30 mm wide on a 10 mm stem, its edge rounded to the 57.1 mm bore and set
    at 20 deg to the wall; plastic, as the bronze plan asks (a plastic or wooden edge)."""
    stem = _cyl((0, 0, 90.0), (0, 0, 1), 5.0, 140.0, 16)
    blade = _box(-15.0, 15.0, 0.0, 3.0, 150.0, 185.0)
    blade = blade.rotate_x(-20.0, point=(0, 0, 150.0), inplace=False).translate((0, 6.0, 0), inplace=False)
    return {"scraper handle": (_handle().merge(stem), (0.20, 0.36, 0.70)), "scraper blade": (blade, (0.95, 0.95, 0.90))}


SCRAPER_TIP = 183.0
SCRAPER_EDGE = (0.0, 19.0, 182.0)      # the blade's edge, tool frame: 19 mm out from the stem


VAC_OFF = 75.0                    # the crevice tool's axis from the grip point, tool +y: clear of the gripper's body
VAC_TIP = 130.0                   # grip point to the crevice tool's tip: the clamp sits on the tool, 130 mm from its tip
VAC_HOSE_AT = (0.0, VAC_OFF, -239.0)     # where the hose leaves the cuff, tool frame


def vac_meshes() -> dict:
    """The vacuum's tool (bought: the 11 in, 279 mm aluminium crevice tool 01768900 and the hose cuff 4072000343) with
    our aluminium clamp on the crevice tool, 130 mm from its tip, and a 20 mm handle 75 mm off its axis, so the cuff
    runs beside the gripper, not into it. Bonded (vacuum SOP: every metal joint <= 0.1 ohm). Tool frame: the grip
    point at the origin, z down (the approach), the crevice tool's axis at y = +75."""
    y0 = VAC_OFF
    clamp = _handle(-20.0, 20.0).merge(_box(-8.0, 8.0, 10.0, y0 - 18.0, -12.0, 12.0)).merge(
        _ring(0.0, y0, -14.0, 28.0, 24.0, 18.5, 32))
    cuff = _cyl((0, y0, -194.0), (0, 0, 1), 22.0, 90.0)
    lo = np.array([[-18, y0 - 18, -149], [18, y0 - 18, -149], [18, y0 + 18, -149], [-18, y0 + 18, -149],
                   [-15, y0 - 5, VAC_TIP], [15, y0 - 5, VAC_TIP], [15, y0 + 5, VAC_TIP], [-15, y0 + 5, VAC_TIP]], float)
    faces = np.hstack([[4, 0, 1, 2, 3], [4, 4, 7, 6, 5], [4, 0, 4, 5, 1], [4, 1, 5, 6, 2], [4, 2, 6, 7, 3],
                       [4, 3, 7, 4, 0]])
    crev = pv.PolyData(lo, faces=faces).triangulate()
    return {"vac clamp": (clamp, (0.70, 0.71, 0.73)), "vac cuff": (cuff, (0.20, 0.20, 0.22)),
            "crevice tool": (crev, (0.78, 0.79, 0.81))}


# The spray tool (ours): an aluminium cradle with two clamp bands holding the 13 oz can, tilted 50 deg from upright
# (its spray 40 deg off vertical, aimed down into the crucible), a 10 mm bore air cylinder that presses the actuator
# (no motor or spark source near a flammable aerosol: its valve is outside the hood), and the 20 mm handle the 2F-85
# holds. Tool frame: the grip point at the origin, z the gripper's approach (level, into
# the hood), y down (props.tcp_frame).
CAN_D, CAN_L = 68.0, 230.0
CAN_TILT = 50.0                   # deg from upright
CAN_BASE = np.array([0.0, 0.0, 70.0])          # the can's bottom centre in the tool frame, 70 mm ahead of the grip


def can_axis_tool() -> np.ndarray:
    """The can's axis in the tool frame: up (tool -y) tilted CAN_TILT toward the approach (tool z)."""
    t = math.radians(CAN_TILT)
    return np.array([0.0, -math.cos(t), math.sin(t)])


def spray_dir_tool() -> np.ndarray:
    """The actuator's spray, square to the can's axis and pointing down-forward (40 deg off vertical when level)."""
    t = math.radians(CAN_TILT)
    return np.array([0.0, math.sin(t), math.cos(t)])


def nozzle_tool() -> np.ndarray:
    """The actuator's orifice: at the can's top, 12 mm below the actuator's top and 11 mm off the axis."""
    a = can_axis_tool()
    return CAN_BASE + a * (CAN_L - 12.0) + spray_dir_tool() * 11.0


def can_tool_meshes() -> dict:
    a = can_axis_tool()
    s = spray_dir_tool()
    body_c = CAN_BASE + a * 95.0
    can = pv.Cylinder(center=tuple(body_c), direction=tuple(a), radius=CAN_D / 2, height=190.0, resolution=40).triangulate()
    dome = pv.Cone(center=tuple(CAN_BASE + a * 200.0), direction=tuple(a), height=20.0, radius=CAN_D / 2 - 2,
                   resolution=40).triangulate()
    act = pv.Cylinder(center=tuple(CAN_BASE + a * 220.0), direction=tuple(a), radius=11.0, height=20.0,
                      resolution=24).triangulate()
    # the cradle: a plate under the can from the handle forward, two bands round it
    x = np.array([1.0, 0.0, 0.0])
    under = -np.cross(a, x)
    under = under if under @ np.array([0, 1, 0]) > 0 else -under       # the side of the can toward tool +y (down)
    plate_pts = []
    bands = None
    for f in (0.12, 0.62):
        c = CAN_BASE + a * (190.0 * f)
        band = pv.Cylinder(center=tuple(c), direction=tuple(a), radius=CAN_D / 2 + 3.0, height=12.0,
                           resolution=40).triangulate()
        bands = band if bands is None else bands.merge(band)
        plate_pts.append(c + under * (CAN_D / 2 + 3.0))
    p0, p1 = plate_pts
    spine = pv.Line(tuple(p0 - a * 20), tuple(p1 + a * 20)).tube(radius=5.0, n_sides=12).triangulate()
    arm = pv.Line((0.0, 0.0, 18.0), tuple(p0)).tube(radius=6.0, n_sides=12).triangulate()
    # the pusher (ours): a 10 mm bore air cylinder on a yoke over the actuator, its rod on the button
    yoke = pv.Line(tuple(p1), tuple(CAN_BASE + a * 236.0 - s * 4.0)).tube(radius=3.5, n_sides=10).triangulate()
    servo = pv.Box(bounds=(-10, 10, -6, 6, -12, 12)).triangulate()
    Rm = np.eye(4)
    Rm[:3, 2] = a
    Rm[:3, 0] = x
    Rm[:3, 1] = np.cross(a, x)
    Rm[:3, 3] = CAN_BASE + a * 240.0 - s * 2.0
    servo = servo.transform(Rm, inplace=False)
    return {"bn can": (can.merge(dome), (0.86, 0.88, 0.90)), "bn can cap": (act, (0.92, 0.92, 0.94)),
            "can label": (pv.Cylinder(center=tuple(CAN_BASE + a * 100.0), direction=tuple(a), radius=CAN_D / 2 + 0.4,
                                      height=90.0, resolution=40).triangulate(), (0.10, 0.30, 0.62)),
            "can cradle": (_handle(-20.0, 20.0).merge(arm).merge(spine).merge(bands).merge(yoke),
                           (0.70, 0.71, 0.73)),
            "can pusher": (servo, (0.15, 0.15, 0.17))}


def mist_mesh(L=180.0, half_deg=11.0) -> pv.PolyData:
    """One burst's spray cone in the tool frame, from the orifice along the spray (drawn see-through)."""
    s = spray_dir_tool()
    n = nozzle_tool()
    r = L * math.tan(math.radians(half_deg))
    return pv.Cone(center=tuple(n + s * L / 2), direction=tuple(-s), height=L, radius=r, resolution=28).triangulate()


# ------------------------------------------------------------------------------------------------ the hood's insides
def box_meshes() -> dict:
    """The open-topped box (ours): aluminium sheet, 130 mm square inside and 193 mm tall, 70 mm (2.75 in) over the
    crucible's rim (150 mm deep, the crucible 47 mm behind its front wall, so a 40 deg spray clears the wall), on a 60 mm plinth that holds the turntable's lift and motor. Drawn see-through so its inside
    shows; it is opaque. Its front is 8.4 in (213 mm) behind the sash (bronze plan: at least 6 in)."""
    b = BOX
    x, y, h, d = b["x"], b["y"], b["inner"] / 2, b["deep"] / 2
    w = b["wall"]
    walls = None
    for (x0, x1, y0, y1) in ((x - h - w, x + h + w, y - d - w, y - d), (x - h - w, x + h + w, y + d, y + d + w),
                             (x - h - w, x - h, y - d, y + d), (x + h, x + h + w, y - d, y + d)):
        m = _box(x0, x1, y0, y1, BOX_FLOOR - b["floor"], BOX_RIM)
        walls = m if walls is None else walls.merge(m)
    cx, cy = CRU_IN_BOX
    floor = _box(x - h, x + h, y - d, y + d, BOX_FLOOR - b["floor"], BOX_FLOOR)
    floor = floor.clip_box((cx - 16, cx + 16, cy - 16, cy + 16, BOX_FLOOR - 10, BOX_FLOOR + 10), invert=True).triangulate()
    plinth = _box(x - h - w - 10, x + h + w + 10, y - d - w - 10, y + d + w + 10, HOOD_Z0, BOX_FLOOR - b["floor"])
    return {"spray box": (walls.merge(floor), (0.78, 0.80, 0.83)), "box plinth": (plinth, (0.30, 0.31, 0.33))}


def lift_meshes() -> dict:
    """The turntable on its column (moves up and down, and spins): in its own frame, its top at z = 0. Both air-driven
    (ours: an air cylinder with a mid stop, and an air indexer): the propellant and solvents pool at the bottom of the
    box (bronze plan), right where a motor would be, so nothing under it may spark. Valves outside the hood."""
    disc = _cyl((0, 0, -TT["t"] / 2), (0, 0, 1), TT["r"], TT["t"], 48)
    col = _cyl((0, 0, -TT["t"] - 100.0), (0, 0, 1), 12.0, 200.0, 20)
    mark = _box(TT["r"] - 10, TT["r"] - 1, -3, 3, -0.6, 0.4)          # a mark, so the turning shows
    return {"turntable": (disc.merge(col), (0.55, 0.56, 0.60)), "turntable mark": (mark, (0.95, 0.70, 0.10))}


def rack_meshes() -> dict:
    """The drying rack (ours): three stainless pins on a plate; the crucible stands upside down on them, its mouth
    open below, so nothing pools on the floor and the draft can't reach inside (bronze plan)."""
    x, y = RACK
    plate = _box(x - 60, x + 60, y - 60, y + 60, HOOD_Z0, HOOD_Z0 + 6)
    pins = None
    for k in range(3):
        a = math.radians(90 + 120 * k)
        px, py = x + 33.0 * math.cos(a), y + 33.0 * math.sin(a)
        p = _cyl((px, py, (HOOD_Z0 + 6 + RACK_TOP) / 2), (0, 0, 1), 4.0, RACK_TOP - HOOD_Z0 - 6, 16)
        pins = p if pins is None else pins.merge(p)
    return {"drying rack": (plate.merge(pins), (0.72, 0.73, 0.76))}


def holster_meshes() -> dict:
    """Holsters (ours): cups the tools stand in, their handles up. On the bench for the brush, the scraper and the
    vacuum's tool; in the hood for the seat plug."""
    out = {}
    top = BENCH["top"]
    for name, (x, y) in HOLSTERS.items():
        r, h = {"brush": (31.0, 70.0), "scraper": (30.0, 60.0), "vac": (24.0, 80.0)}[name]
        cup = _ring(x, y, top, h, r + 3.0, r).merge(_cyl((x, y, top + 1.5), (0, 0, 1), r + 3.0, 3.0))
        out[f"holster {name}"] = (cup, (0.30, 0.31, 0.33))
    x, y = PLUG_HOLSTER
    out["holster plug"] = (_ring(x, y, HOOD_Z0, 95.0, 17.0, 14.0).merge(_cyl((x, y, HOOD_Z0 + 1.5), (0, 0, 1), 17.0, 3.0)),
                           (0.30, 0.31, 0.33))
    x, y = CAN_CRADLE
    out["can cradle stand"] = (_box(x - 45, x + 45, y + 60, y + 200, HOOD_Z0, HOOD_Z0 + 14), (0.30, 0.31, 0.33))
    return out


HOLSTER_SEAT = {"brush": BENCH["top"] + 3.0, "scraper": BENCH["top"] + 3.0, "vac": BENCH["top"] + 3.0}


def nilfisk_standin() -> dict:
    """A stand-in for the Nilfisk CFM 118EXP (drum and motor head), used only if atom_nilfisk.py isn't there yet."""
    x, y = NILFISK_AT
    drum = _cyl((x, y, 330.0), (0, 0, 1), 230.0, 560.0, 48)
    head = _cyl((x, y, 700.0), (0, 0, 1), 215.0, 180.0, 48)
    inlet = _cyl((x + 200, y - 120, 560.0), (1, -0.6, 0), 24.0, 80.0)
    wheels = _box(x - 260, x + 260, y - 260, y + 260, 0.0, 50.0)
    return {"nilfisk drum": (drum.merge(wheels), (0.88, 0.88, 0.86)), "nilfisk head": (head, (0.20, 0.42, 0.75)),
            "nilfisk inlet": (inlet, (0.20, 0.20, 0.22))}


NILFISK_INLET = np.array([NILFISK_AT[0] + 235.0, NILFISK_AT[1] - 140.0, 560.0])


def hose_mesh(p0, p1, sag=180.0) -> pv.PolyData:
    """The conductive 1.5 in hose (38 mm) from the vacuum's inlet to the tool's cuff: a sagging curve."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    mid = (p0 + p1) / 2 + np.array([0.0, 0.0, -sag])
    mid[2] = max(mid[2], BENCH["top"] + 40.0) if p1[2] > BENCH["top"] else mid[2]
    a = p0 + np.array([60.0, -40.0, 0.0])
    b = p1 + np.array([0.0, 0.0, 90.0])
    pts = np.array([p0, a, mid, b, p1])
    return pv.Spline(pts, 60).tube(radius=19.0, n_sides=14).triangulate()


# ------------------------------------------------------------------------------------------------ the hood itself
def add_hood(sc, parent="rp"):
    """instruments_r7's Labconco XStream 4 ft in the scene, its sash raised to the 18 in stop. The etch beakers, the
    reagent bottle, the coupon and the air puffs of its own tour are left out. Returns the tour.Rig."""
    import instruments_r7 as R7
    import tour
    tour.MATS.update(R7.MATERIALS)
    inst = R7.fumehood()
    drop = ("etch beaker", "rinse beaker", "reagent")
    for piece in list(inst.pieces):
        if piece not in ("body", "sash"):
            del inst.pieces[piece]
    inst.pieces["body"].parts = [p for p in inst.pieces["body"].parts if not p.name.startswith(drop)]
    for k in list(inst.joints):
        if k != "sash":
            del inst.joints[k]
    ents = tour.piece_entries(inst)
    rig = tour.Rig(sc, inst, ents, "hood:", at=T((HOOD_AT[0], HOOD_AT[1], 0.0)), parent=parent)
    rig.v["sash"] = 1.0
    rig.apply()
    return rig
