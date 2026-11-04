"""The pieces the alloy workflow (``alloy_workflow.py``) adds to the line: the Aconity MIDI opened up, the build plate
with its printed tensile bars, the wire EDM's fixture and wire head, and the holders on the MiR250.

The Aconity MIDI is #199's model (``lab_models.equipment.aconity_midi()``), with its process chamber split so it can
open: the chamber's walls, a door with the model's viewport and handle, and inside, a build cylinder and a powder
supply cylinder of 170 mm, with a build piston and a recoater. #199's model is a closed block there; Aconity publishes
no drawing of the inside, so the layout inside is drawn from DAL PR #169's figures only (170 mm build platform and
powder supply; the beam tube's axis is the build cylinder's) and is otherwise a layout choice.

Frames are each model's own, in millimetres, z up; the Aconity's is the centred frame of ``equipment.py``.
"""
from __future__ import annotations

import hashlib
import math
import pickle
import sys
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
import lab                                    # noqa: E402
import instruments as I                       # noqa: E402

MATS = dict(lab.MATS)
MATS.update(I.MATERIALS)

# ---------------------------------------------------------------------------------------------- the specimen
# ASTM E8/E8M sheet-type subsize specimen, mm: overall length L, reduced section A long and W wide, grips C wide and B
# long, fillet R, gauge length G. DAL PR #169 (from issue #47's drawing) gives the bars printed for the Utah build:
# 100 mm long, 10 mm ends, 32 mm reduced section 6 mm wide, printed 6 mm thick, flat on the plate. That is this
# specimen. T is DAL's print height.
E8_SUB = dict(L=100.0, A=32.0, W=6.0, C=10.0, B=30.0, R=6.0, G=25.0, T=6.0)
# the build plate: 170 mm, the Aconity MIDI's build platform (DAL PR #169); Al 6061, as Utah's (DAL PR #169). Its
# thickness and the zero-point stud under it are assumptions (see the notes)
PLATE = dict(r=85.0, t=15.0, stud_r=20.0, stud_h=20.0)
BAR_X = (-35.0, -10.0, 15.0, 40.0)            # the four bars across the plate (x of each centre line), 25 mm apart
LUG = (-84.0, -72.0, -15.0, 15.0, 0.0, 30.0)   # a handling lug printed with the bars, at the plate's left rim
AS_BUILT = (0.60, 0.61, 0.62)                 # as-built LPBF AlSi10Mg: matte grey
AL6061 = (0.78, 0.79, 0.81)
POWDER = (0.50, 0.51, 0.53)


def _half_outline(n_arc: int = 8) -> list:
    """The E8 subsize outline's y >= 0 half in the xy plane (long axis along y), counter-clockwise from (W/2, 0) to
    (-W/2, 0)."""
    p = E8_SUB
    hl, ha, hw, hc, r = p["L"] / 2, p["A"] / 2, p["W"] / 2, p["C"] / 2, p["R"]
    # the fillet: an arc of radius R tangent to the reduced section's edge at y = A/2, out to the grip's width
    cx, cy = hw + r, ha                       # arc centre (x, y), quarter on the +x, +y side
    t1 = math.acos((cx - hc) / r)             # angle swept until x reaches the grip's edge
    arc = [(cx - r * math.cos(t), cy + r * math.sin(t)) for t in np.linspace(0.0, t1, n_arc)]
    q1 = [(hw, 0.0)] + arc + [(hc, hl)]       # +x, +y quarter from the centre line up to the end
    return q1 + [(-x, y) for x, y in reversed(q1)]


def bar_outline() -> np.ndarray:
    """The whole outline, counter-clockwise."""
    top = _half_outline()
    pts = top[:-1] + [(x, -y) for x, y in reversed(top)][:-1]
    return np.array(pts)


def bar_mesh(half: str | None = None) -> pv.PolyData:
    """The printed bar in the plate's frame: centred on its own axis, long axis along y, z 0..T (on the plate).
    half = 'lo' (y < 0) or 'hi' (y > 0) for the two pieces after fracture."""
    if half is None:
        pts = bar_outline()
    else:
        top = _half_outline()
        pts = np.array(top if half == "hi" else [(x, -y) for x, y in reversed(top)])
    poly = pv.PolyData(np.c_[pts, np.zeros(len(pts))], faces=np.r_[len(pts), np.arange(len(pts))])
    solid = poly.triangulate().extrude((0, 0, E8_SUB["T"]), capping=True).triangulate().clean()
    return solid.compute_normals(auto_orient_normals=True, split_vertices=True)


def plate_parts() -> dict:
    """{name: (mesh, colour, specular)}: the plate, its stud, the lug; in the plate's frame (top face centre, z up)."""
    p = PLATE
    plate = pv.Cylinder(center=(0, 0, -p["t"] / 2), direction=(0, 0, 1), radius=p["r"], height=p["t"],
                        resolution=72).triangulate()
    stud = pv.Cylinder(center=(0, 0, -p["t"] - p["stud_h"] / 2), direction=(0, 0, 1), radius=p["stud_r"],
                       height=p["stud_h"], resolution=32).triangulate()
    x0, x1, y0, y1, z0, z1 = LUG
    lug = pv.Box(bounds=(x0, x1, y0, y1, z0, z1)).triangulate()
    return {"plate": (plate, AL6061, 0.35), "stud": (stud, (0.55, 0.56, 0.58), 0.6), "lug": (lug, AS_BUILT, 0.2)}


# ------------------------------------------------------------------------------------------------ Aconity
ACO = dict(bx=935.0, by=600.0, sy=790.0, bore=170.0, floor=1005.0, wall=15.0, cyl_bot=760.0)


def _aco_frame():
    import equipment
    p = equipment.ACONITY
    W, D = p["W"], p["D"]

    def B(x0, x1, y0, y1, z0, z1):
        from common import box
        return box(x0 - W / 2, y0 - D / 2, z0, x1 - W / 2, y1 - D / 2, z1)

    def C(d, x, y, z0, z1):
        from common import cyl
        return cyl(d, z1 - z0, x=x - W / 2, y=y - D / 2, z=z0)

    def P(x, y, z):
        return (x - W / 2, y - D / 2, z)
    return B, C, P


def build_point(z: float | None = None) -> np.ndarray:
    """The build cylinder's axis in the Aconity's frame, at the chamber floor (or at z)."""
    _, _, P = _aco_frame()
    return np.array(P(ACO["bx"], ACO["by"], ACO["floor"] if z is None else z))


DOOR_PIVOT = None    # set by aconity_pieces(): the door's hinge axis point in the model frame


def _aconity_build() -> dict:
    """{piece: [entry]} with one merged mesh per material: body, cabinet (the base cabinet, faded for the cutaway),
    shell (the process chamber's walls), door, bore (cylinders and floor details), piston, recoater, supply powder."""
    import equipment
    from common import Model
    B, C, P = _aco_frame()
    m = equipment.aconity_midi()
    out_parts = {"body": [], "cabinet": [], "shell": [], "door": [], "bore": [], "piston": [], "recoater": [],
                 "supply": []}
    drop = {"process chamber", "chamber viewport", "chamber handle"}
    for prt in m.parts:
        if prt.name in drop:
            continue
        key = "cabinet" if prt.name.startswith("base ") else "body"
        out_parts[key].append((prt.shape, prt.material))
    w, fl = ACO["wall"], ACO["floor"]
    x0, x1, y0, y1, z0, z1 = 634.0, 1243.0, 250.0, 950.0, 990.0, 1300.0
    outer = B(x0, x1, y0, y1, z0, z1).edges("|Y").fillet(10)
    inner = B(x0 + w, x1 - w, y0 - 1, y1 - w, fl, z1 - w)
    shell = outer.cut(inner)
    for d, (x, y) in ((ACO["bore"], (ACO["bx"], ACO["by"])), (ACO["bore"], (ACO["bx"], ACO["sy"]))):
        shell = shell.cut(C(d, x, y, z0 - 1, fl + 1))
    out_parts["shell"].append((shell, "anthracite"))
    # the door: the chamber's front, inside the shell's 15 mm frame, with #199's viewport and handle on it
    door = B(x0 + w + 1, x1 - w - 1, y0, y0 + w, fl + 1, z1 - w - 1)
    out_parts["door"] += [(door, "anthracite"), (B(855, 1000, 244, 250.01, 1120, 1180), "tinted")]
    from common import hose
    out_parts["door"].append((hose([P(870, 250, 1017), P(870, 225, 1017), P(1030, 225, 1017), P(1030, 250, 1017)], 16),
                              "printer_black"))
    # the two cylinders under the floor, down into the base cabinet
    for (x, y) in ((ACO["bx"], ACO["by"]), (ACO["bx"], ACO["sy"])):
        tube = C(ACO["bore"] + 24, x, y, ACO["cyl_bot"], z0).cut(C(ACO["bore"], x, y, ACO["cyl_bot"] - 1, z0 + 1))
        out_parts["bore"].append((tube, "steel"))
    # the supply's powder, level with the floor; its piston is below
    out_parts["supply"].append((C(ACO["bore"] - 0.5, ACO["bx"], ACO["sy"], fl - 25, fl - 0.5), "powder"))
    # the build piston, top at z = 0 in its own frame (moved by the animation): the platform and its rod
    from common import cyl
    out_parts["piston"] += [(cyl(ACO["bore"] - 1, 25, z=-25), "steel"), (cyl(60, 280, z=-305), "steel")]
    # the recoater: a blade on a carriage across the cylinders, parked at the back
    out_parts["recoater"] += [(B(760, 1110, 893, 917, fl + 2, fl + 40), "aluminium"),
                              (B(780, 1090, 893, 899, fl, fl + 8), "steel")]
    ents = {}
    for piece, lst in out_parts.items():
        by = {}
        for shape, mat in lst:
            if hasattr(shape, "vals"):
                shape = shape.val() if len(shape.vals()) == 1 else I.cq.Compound.makeCompound(shape.vals())
            by.setdefault(mat, []).append(lab.to_mesh(shape, 1.0))
        ents[piece] = []
        for mat, ms in by.items():
            r, g, b, a, spec = MATS[mat]
            ents[piece].append(dict(mesh=lab._merge(ms), color=(r, g, b), opacity=a, specular=spec, material=mat))
    return ents


def aconity_pieces() -> dict:
    """``_aconity_build()``, cached in .cache on this file and #199's equipment.py."""
    src = (HERE / "lab_models" / "equipment.py").read_bytes() + Path(__file__).read_bytes() + \
        (HERE / "lab.py").read_bytes()
    path = lab.CACHE / f"alloy_aconity_{hashlib.sha256(src).hexdigest()[:12]}.pkl"
    if path.exists():
        return pickle.loads(path.read_bytes())
    lab.CACHE.mkdir(exist_ok=True)
    print("tessellating the Aconity MIDI, opened", flush=True)
    ents = _aconity_build()
    path.write_bytes(pickle.dumps(ents))
    return ents


def door_pivot() -> tuple:
    """The door's hinge: its left edge, at the front of the chamber (model frame)."""
    _, _, P = _aco_frame()
    return P(634.0 + ACO["wall"] + 1, 250.0, 0.0)


# ------------------------------------------------------------------------------------------------- wire EDM
def edm_fixture(pc: np.ndarray) -> dict:
    """The fixture in the EDM's frame for a plate standing on edge, its bar face towards the front, face centre pc:
    an angle plate across the table's window with a zero-point receiver, and a catch shelf for the cut bars."""
    p = PLATE
    x, yf, z = pc
    yb = yf + p["t"]                                  # the plate's back face
    tz = I.EDM["table_z"]
    out = {}
    out["receiver"] = (pv.Cylinder(center=(x, yb + 15, z), direction=(0, 1, 0), radius=48, height=30,
                                   resolution=48).triangulate(), (0.30, 0.32, 0.36))
    ang = pv.Box(bounds=(x - 140, x + 140, yb + 30, yb + 60, tz + 20, z + 120)).triangulate()
    foot = pv.Box(bounds=(-740.0, -120.0, yb + 30, yb + 90, tz, tz + 20)).triangulate()
    out["angle plate"] = (ang.merge(foot), (0.42, 0.44, 0.47))
    zs = z - E8_SUB["L"] / 2 - 14.0                   # the shelf the cut bars drop onto
    arm = pv.Box(bounds=(x - 112, x - 98, yf - 14, yb + 30, zs - 4, zs)).triangulate()
    shelf = pv.Box(bounds=(x - 112, x + 60, yf - 14, yf - 1.2, zs - 4, zs)).triangulate()
    out["catch shelf"] = (arm.merge(shelf), (0.30, 0.31, 0.33))
    return out


def wire_head(z_lo: float, z_hi: float) -> dict:
    """The upper and lower guides and the wire, at x = y = 0, wire from z_lo to z_hi (moved by the animation).
    The wire is 0.25 mm; it is drawn 1.6 mm so it shows."""
    up = pv.Cylinder(center=(0, 0, z_hi + 20), direction=(0, 0, 1), radius=20, height=40, resolution=32).triangulate()
    upb = pv.Box(bounds=(-55, 55, -55, 55, z_hi + 40, z_hi + 260)).triangulate()
    lo = pv.Cylinder(center=(0, 0, z_lo - 20), direction=(0, 0, 1), radius=20, height=40, resolution=32).triangulate()
    lob = pv.Box(bounds=(-35, 35, -35, 35, z_lo - 140, z_lo - 40)).triangulate()
    wire = pv.Cylinder(center=(0, 0, (z_lo + z_hi) / 2), direction=(0, 0, 1), radius=0.8, height=z_hi - z_lo,
                       resolution=12).triangulate()
    return {"upper guide": (up.merge(upb), (0.86, 0.87, 0.86)), "lower guide": (lo.merge(lob), (0.72, 0.73, 0.75)),
            "wire": (wire, (0.86, 0.68, 0.28))}


# ------------------------------------------------------------------------------------------------- MiR250
CARRIER_LOCAL = (250.0, -95.0)                 # plate carrier on the cabinet top (MiR frame, x, y)
HOLDER_LOCAL = (-280.0, -120.0)                # bar holder on the cabinet top
CARRIER_H = 120.0                              # post: the plate's back face 120 mm over the cabinet's top
HOLDER_H = 230.0


def mir_fixtures(top: float) -> dict:
    """The plate carrier (a receiver on a post) and the bar holder (a slotted block on a post) on the MiR's cabinet,
    `top` = the cabinet's top. MiR frame."""
    cx, cy = CARRIER_LOCAL
    post = pv.Cylinder(center=(cx, cy, top + CARRIER_H / 2), direction=(0, 0, 1), radius=30,
                       height=CARRIER_H).triangulate()
    puck = pv.Cylinder(center=(cx, cy, top + CARRIER_H - 15), direction=(0, 0, 1), radius=60, height=30,
                       resolution=48).triangulate()
    foot = pv.Box(bounds=(cx - 70, cx + 70, cy - 70, cy + 70, top, top + 10)).triangulate()
    hx, hy = HOLDER_LOCAL
    hpost = pv.Cylinder(center=(hx, hy, top + HOLDER_H / 2), direction=(0, 0, 1), radius=16,
                        height=HOLDER_H).triangulate()
    block = pv.Box(bounds=(hx - 30, hx + 30, hy - 25, hy + 25, top + HOLDER_H, top + HOLDER_H + 30)).triangulate()
    hfoot = pv.Box(bounds=(hx - 45, hx + 45, hy - 45, hy + 45, top, top + 8)).triangulate()
    return {"carrier": (post.merge(puck).merge(foot), (0.30, 0.32, 0.36)),
            "bar holder": (hpost.merge(block).merge(hfoot), (0.94, 0.94, 0.92))}


def carrier_top(top: float) -> np.ndarray:
    """Where the plate's back face sits on the carrier, MiR frame."""
    return np.array([CARRIER_LOCAL[0], CARRIER_LOCAL[1], top + CARRIER_H])


def holder_seat(top: float) -> np.ndarray:
    """Where a bar's lower end rests in the holder's slot (25 mm deep), MiR frame."""
    return np.array([HOLDER_LOCAL[0], HOLDER_LOCAL[1], top + HOLDER_H + 30 - 25])


# ------------------------------------------------------------------------------------------------- depowdering
# A compact depowdering box in the line, between the Aconity MIDI and the Instron 68FM-100, where the line leaves 544 mm.
# Our design, on the principle of Solukon's SFM-AT200: the plate clamped on a table that turns about one axis on a
# programmed path, shaken at a variable frequency, in nitrogen or argon (TCT Magazine: parts up to 300 x 300 x 230 mm,
# 60 kg). Solukon publishes no outer size for it, and 3devaluate lists its installation space as 2 x 2 x 2 m, so the
# commercial unit would need the line opened up by about a metre; this box is 420 mm wide. Frame: the front face's
# centre on the floor, +y into the box, z up. The plate's zero-point stud goes into the chuck, as on the EDM's receiver.
DBOX = dict(W=420.0, D=620.0, H=1540.0, base=700.0, chuck_x=30.0, axis_y=300.0, chuck_top=990.0,
            door_x=(-120.0, 196.0), door_z=(745.0, 1480.0), lift=760.0)
DBOX["axis_z"] = DBOX["chuck_top"] - 45.0
LANCE = dict(L=300.0, r=14.0, grip=23.0)        # suction lance: tube length and radius, handle half-length (y)
# the lance hangs on a post in front of the Aconity, right of its chamber, where the arm reaches it from the MiR's spot
# at the printer; a pipe along the floor takes the powder to the box's separator. Post frame: like the box's.
HOLSTER = (0.0, -60.0, 1300.0)                  # the lance's grasp point when it hangs in its forks (post frame)
STAND_PORT = (75.0, -60.0, 70.0)                # where the hose joins the floor pipe (post frame)
HOSE_INLET = (-168.0, -22.0, 740.0)             # the floor pipe's end on the box's front, low (box frame)


def _box(x0, x1, y0, y1, z0, z1):
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1)).triangulate()


def _cyl(r, p0, p1, res=40):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    return pv.Cylinder(center=(p0 + p1) / 2, direction=d, radius=r, height=float(np.linalg.norm(d)),
                       resolution=res).triangulate()


def depowder_box() -> dict:
    """{piece: {name: (mesh, colour, specular, opacity)}}: 'body' (cabinet, frame, hopper, bottle, holster, hose port),
    'walls' (the enclosure, drawn see-through while it works), 'door' (slides up) and 'rotor' (the shaft, the zero-point
    chuck and the vibrator, turning about x through (axis_y, axis_z))."""
    import charge
    p = DBOX
    hw, D, H, zb = p["W"] / 2, p["D"], p["H"], p["base"]
    cx, ay, az, ct = p["chuck_x"], p["axis_y"], p["axis_z"], p["chuck_top"]
    grey, dark, steel = (0.86, 0.87, 0.88), (0.24, 0.25, 0.27), (0.62, 0.63, 0.66)
    frame = _box(-hw, hw, 0, 30, zb, zb + 40).merge(_box(-hw, -hw + 30, 0, 30, zb, H)) \
        .merge(_box(hw - 30, hw, 0, 30, zb, H)).merge(_box(-hw, hw, 0, 30, H - 50, H))
    body = {"cabinet": (_box(-hw, hw, 0, D, 40, zb), grey, 0.15, 1.0),
            "plinth": (_box(-hw + 10, hw - 10, 10, D - 10, 0, 40), dark, 0.1, 1.0),
            "frame": (frame, dark, 0.2, 1.0),
            "window": (_box(-60, 120, -1.0, 0.5, 330, 600), (0.20, 0.22, 0.25), 0.5, 1.0),
            "panel": (_box(hw - 120, hw - 34, -2.0, 0.5, 1180, 1420), (0.16, 0.17, 0.18), 0.3, 1.0),
            "screen": (_box(hw - 112, hw - 42, -3.0, -1.5, 1330, 1405), (0.30, 0.62, 0.86), 0.4, 1.0),
            "start": (_cyl(9, (hw - 77, -2, 1250), (hw - 77, -10, 1250), 24), (0.10, 0.62, 0.30), 0.3, 1.0)}
    hop = charge.lathe([(28, zb - 20), (36, zb - 20), (180, zb + 150), (186, zb + 150), (186, zb + 158),
                        (172, zb + 158), (28, zb - 12)], res=64).translate((cx, ay, 0), inplace=False)
    body["hopper"] = (hop, steel, 0.45, 1.0)
    bottle = charge.lathe([(0, 330), (62, 330), (66, 336), (66, 600), (40, 640), (40, zb - 10), (0, zb - 10)], res=48)
    body["bottle"] = (bottle.translate((cx, ay, 0), inplace=False), (0.80, 0.81, 0.83), 0.5, 1.0)
    for sx in (-1, 1):                                    # the trunnion's bearing blocks on the side walls
        body[f"bearing {sx}"] = (_box(min(sx * hw, sx * (hw - 36)), max(sx * hw, sx * (hw - 36)),
                                      ay - 40, ay + 40, az - 40, az + 40), dark, 0.2, 1.0)
    ix, iy, iz = HOSE_INLET
    body["hose port"] = (_cyl(20, (ix, 0.5, iz), (ix, iy, iz), 32), steel, 0.5, 1.0)
    body["argon"] = (_cyl(6, (hw - 60, D - 30, H - 50), (hw - 60, D - 30, H + 120), 16), (0.20, 0.45, 0.80), 0.4, 1.0)
    walls = _box(-hw, hw, D - 8, D, zb + 40, H).merge(_box(-hw, -hw + 8, 30, D, zb + 40, H)) \
        .merge(_box(hw - 8, hw, 30, D, zb + 40, H)).merge(_box(-hw, hw, 30, D, H - 8, H))
    x0, x1 = p["door_x"]
    z0, z1 = p["door_z"]
    door = {"door": (_box(x0, x1, -14, -6, z0, z1), (0.30, 0.31, 0.33), 0.3, 1.0),
            "door window": (_box(x0 + 30, x1 - 30, -16, -14.9, z0 + 70, z1 - 70), (0.62, 0.74, 0.82), 0.6, 0.55),
            "door handle": (_box(x0 + 110, x1 - 110, -40, -16, z0 + 30, z0 + 44), dark, 0.3, 1.0)}
    chuck = _cyl(52, (cx, ay, az - 20), (cx, ay, ct), 48).merge(_box(cx - 40, cx + 40, ay - 22, ay + 22, az - 22,
                                                                       az + 10))
    rotor = {"shaft": (_cyl(16, (-hw + 36, ay, az), (hw - 36, ay, az), 32), steel, 0.6, 1.0),
             "chuck": (chuck, (0.30, 0.32, 0.36), 0.4, 1.0),
             "vibrator": (_cyl(22, (cx + 95, ay, az), (cx + 150, ay, az), 32), (0.85, 0.42, 0.10), 0.3, 1.0)}
    return {"body": body, "walls": {"walls": (walls, (0.80, 0.82, 0.84), 0.2, 1.0)}, "door": door, "rotor": rotor}


def lance_stand() -> dict:
    """The lance's post: a floor plate, a post behind the lance and two forks open to the front, so the arm lifts the
    lance 14 mm and draws it straight out. Post frame. {name: (mesh, colour, specular, opacity)}."""
    hx, hy, hz = HOLSTER
    dark = (0.24, 0.25, 0.27)
    post = _box(-15, 15, hy + 32, hy + 52, 0, hz + 40).merge(_box(-80, 80, hy - 30, -4, 0, 10))
    forks = None
    for zf in (hz - 330.0, hz - 170.0):
        fork = _box(hx - 26, hx + 26, hy + 18, hy + 34, zf - 12, zf + 12).merge(
            _box(hx - 26, hx - 17, hy - 24, hy + 18, zf - 6, zf + 6)).merge(
            _box(hx + 17, hx + 26, hy - 24, hy + 18, zf - 6, zf + 6))
        forks = fork if forks is None else forks.merge(fork)
    px, py, pz = STAND_PORT
    port = _cyl(22, (px, py, pz - 40), (px, py, pz + 20), 32)
    return {"post": (post, dark, 0.2, 1.0), "forks": (forks, (0.12, 0.40, 0.75), 0.3, 1.0),
            "port": (port, (0.62, 0.63, 0.66), 0.5, 1.0)}


BARB = (0.0, 6.0, -15.0, -45.0)                 # the hose barb: on the handle's -z face at y = 6, out to z = -45


def lance() -> dict:
    """The suction lance in its own frame: the grasp point at the origin, the tube along +y, the handle block 12 mm
    thick in x (gripped like the plate's lug), the hose barb on its side (-z). The gripper takes the handle end-on,
    its fingers along x and its body behind (-y), so a barb on the end would put the hose through the gripper: on
    the -z face it leaves past the fingers, which are 28 mm across in z. {name: (mesh, colour, specular)}."""
    import charge
    L, r, g = LANCE["L"], LANCE["r"], LANCE["grip"]
    tube = _cyl(r, (0, g, 0), (0, g + L, 0), 32)
    noz = charge.lathe([(r - 2, 0), (r, 0), (r + 8, 26), (r + 6, 26)], res=32)
    noz.rotate_x(-90, inplace=True)                  # its axis from +z to +y
    noz.translate((0, g + L, 0), inplace=True)
    return {"tube": (tube.merge(noz), (0.75, 0.76, 0.78), 0.5),
            "handle": (_box(-6, 6, -g, g, -15, 15), (0.12, 0.40, 0.75), 0.2),
            "barb": (_cyl(9, (BARB[0], BARB[1], BARB[2] + 1), (BARB[0], BARB[1], BARB[3]), 24), (0.25, 0.26, 0.28),
                     0.3)}


def hose_mesh(p0, d0, p1, d1, sag=180.0, r=13.0) -> pv.PolyData:
    """A hose from p0 (leaving along d0) to p1 (arriving along -d1), a cubic Bezier sagging `sag` mm, as a tube."""
    p0, p1, d0, d1 = (np.asarray(v, float) for v in (p0, p1, d0, d1))
    span = float(np.linalg.norm(p1 - p0))
    k = 0.35 * span + 80.0
    c0, c1 = p0 + d0 * k, p1 + d1 * k
    c0[2] -= sag
    c1[2] -= sag
    s = np.linspace(0, 1, 40)[:, None]
    pts = (1 - s) ** 3 * p0 + 3 * (1 - s) ** 2 * s * c0 + 3 * (1 - s) * s ** 2 * c1 + s ** 3 * p1
    return pv.Spline(pts, 60).tube(radius=r, n_sides=14).triangulate()


# ------------------------------------------------------------------------------------------------- rinse and dry
# A dip-and-blow cup on a stand in front of the EDM: isopropanol in the lower part, an annular air knife on the rim
# that blows the bar dry as it is pulled out. Our design (assumed): wire-cut parts come out wet with deionised water.
RINSE = dict(r=46.0, z0=900.0, z1=1062.0, liquid=1045.0)


def rinse_cup() -> dict:
    import charge
    p = RINSE
    stand = _cyl(18, (0, 0, 0), (0, 0, p["z0"]), 24).merge(_box(-110, 110, -90, 90, 0, 12))
    cup = charge.lathe([(0, p["z0"]), (p["r"], p["z0"]), (p["r"], p["z1"]), (p["r"] - 3, p["z1"]),
                        (p["r"] - 3, p["z0"] + 3), (0, p["z0"] + 3)], res=48)
    liquid = _cyl(p["r"] - 3.5, (0, 0, p["z0"] + 3), (0, 0, p["liquid"]), 48)
    # the air knife sits on the rim, its slot facing in: the gripper's fingertips pass inside it, into the cup
    ring = charge.lathe([(p["r"] - 1, p["z1"]), (p["r"] + 10, p["z1"]), (p["r"] + 10, p["z1"] + 16),
                         (p["r"] - 1, p["z1"] + 16)], res=48)
    line_ = _cyl(4, (p["r"] + 10, 0, p["z1"] + 8), (p["r"] + 60, 0, p["z1"] + 8), 12).merge(
        _cyl(4, (p["r"] + 60, 0, p["z1"] + 8), (p["r"] + 60, 0, 12), 12))
    return {"stand": (stand, (0.24, 0.25, 0.27), 0.2, 1.0), "cup": (cup, (0.86, 0.90, 0.94), 0.5, 0.45),
            "liquid": (liquid, (0.55, 0.72, 0.92), 0.3, 0.55), "air knife": (ring, (0.62, 0.63, 0.66), 0.5, 1.0),
            "air line": (line_, (0.20, 0.45, 0.80), 0.3, 1.0)}
