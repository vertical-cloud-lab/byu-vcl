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
# round 11: the build cylinder 171 mm across, not 170: the 170 mm plate rose through a 170 mm hole in the chamber's
# floor, which the strict audit's movers check read as the plate 12 mm into the shell (a build cylinder runs a
# fraction of a mm round its platform, with a seal)
ACO = dict(bx=935.0, by=600.0, sy=790.0, bore=171.0, floor=1005.0, wall=15.0, cyl_bot=760.0)


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
        shape = prt.shape
        if key == "cabinet":            # round 11: the build cylinder and the piston's rod run down through it
            try:
                shape = shape.cut(C(ACO["bore"] + 24.0, ACO["bx"], ACO["by"], 300.0, 1310.0).val())
            except Exception:           # noqa: BLE001  (a part the cut can't take stays whole)
                pass
        out_parts[key].append((shape, prt.material))
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
    # round 11: a bore in the platform for the plate's zero-point stud (20 mm under the plate, 0.5 mm round it);
    # round 10's solid platform had the stud 20 mm inside it, which the strict audit read as the plate through it
    sb = cyl(2 * (PLATE["stud_r"] + 0.5), PLATE["stud_h"] + 2.5, z=-(PLATE["stud_h"] + 2.0))
    out_parts["piston"] += [(cyl(ACO["bore"] - 1, 25, z=-25).cut(sb), "steel"), (cyl(60, 280, z=-305), "steel")]
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


# Round 9 (Sterling, PR #318, 2026-11-05: "Aconity MIDI door swings the wrong way"). Rounds 4-8 hinged the door on
# its left edge and turned it +100 deg about z, which swings its free edge back into the machine, through the
# chamber's left wall. Aconity's chamber door lifts: on the MIDI the bar handle sits centred on the door's lower edge
# (Amazemet's photo of their MIDI, https://www.amazemet.com/aconity-midi-lpbf-system-in-amazemets-rd-facility), and
# Aconity's photo of the MIDI+ shows the chamber open with its front flap raised, standing up over the chamber on two
# struts, the handle at its top (3Dnatives, https://www.3dnatives.com/3d-materials/en/3d-printers/aconity-midi-plus/).
# So the door hinges along its top edge, at the chamber's front face, and swings out and up. DOOR_OPEN = 165 deg
# leaves it leaning 15 deg forward of upright, as in that photo; the struts and the angle are our reading of it.
DOOR_OPEN = 165.0


def door_pivot() -> tuple:
    """The door's hinge line (along x): its top edge, at the chamber's front face (model frame). Its y is the
    chamber's front, which is what alloy_print.py takes from it."""
    _, _, P = _aco_frame()
    return P(634.0 + ACO["wall"] + 1, 250.0, 1300.0 - ACO["wall"])


def door_T(f: float) -> np.ndarray:
    """The door's 4x4 (model frame) at f open (0 shut, 1 open): a turn about the hinge line (x) that takes its lower
    edge out (-y) and up, never into the chamber."""
    _, py, pz = door_pivot()
    t = -math.radians(DOOR_OPEN * float(f))
    c, s = math.cos(t), math.sin(t)
    m = np.eye(4)
    m[1, 1], m[1, 2], m[2, 1], m[2, 2] = c, -s, s, c
    m[1, 3] = py - (c * py - s * pz)
    m[2, 3] = pz - (s * py + c * pz)
    return m


# ------------------------------------------------------------------------------------------------- wire EDM
def edm_fixture(pc: np.ndarray) -> dict:
    """The fixture in the EDM's frame for a plate standing on edge, its bar face towards the front, face centre pc:
    an angle plate across the table's window with a zero-point receiver, and a catch shelf for the cut bars."""
    p = PLATE
    x, yf, z = pc
    yb = yf + p["t"]                                  # the plate's back face
    tz = I.EDM["table_z"]
    out = {}
    import charge                     # round 11: the receiver bored for the plate's stud (0.5 mm round it)
    rs, hs = p["stud_r"] + 0.5, p["stud_h"] + 2.0
    rec = charge.lathe([(rs, 0.0), (48.0, 0.0), (48.0, 30.0), (0.0, 30.0), (0.0, hs), (rs, hs)], res=48)
    out["receiver"] = (rec.rotate_x(-90.0, inplace=False).translate((x, yb, z), inplace=False), (0.30, 0.32, 0.36))
    ang = pv.Box(bounds=(x - 175, x + 175, yb + 30, yb + 60, tz + 20, z + 120)).triangulate()   # round 11: 350 wide
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
    lob = pv.Box(bounds=(-35, 35, -35, 35, z_lo - 105, z_lo - 40)).triangulate()     # round 11: over the tank floor
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
# suction lance: tube length and radius, handle half-length (y). Round 9: 400 mm (300 until round 8), so the nozzle
# reaches the build cylinder, 350 mm behind the chamber's front, with the gripper outside the chamber
LANCE = dict(L=400.0, r=14.0, grip=23.0)
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
    import charge                     # round 11: the chuck bored for the plate's stud (0.5 mm round it)
    rs, hs = PLATE["stud_r"] + 0.5, PLATE["stud_h"] + 2.0
    chuck = charge.lathe([(0.0, az - 20), (52.0, az - 20), (52.0, ct), (rs, ct), (rs, ct - hs), (0.0, ct - hs)],
                         res=48).translate((cx, ay, 0.0), inplace=False)
    chuck = chuck.merge(_box(cx - 40, cx + 40, ay - 22, ay + 22, az - 22, az + 10))
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


# =========================================================================================== round 8 (chapter 5)
# Sterling (PR #318, 2026-11-05): "The bars dropping onto the catch shelf.. it totally looks like they'd just bounce and
# fall straight off ... If there's going to be a catch shelf, it should actually be capable of catching it in terms of
# distance and a taller lip and such." The plate stands on edge, so each cut bar stands on end. Each gets a slot of its
# own in a comb under it, whose floor is 0.5 mm under the bar's lower end before the cut: the bar settles 0.5 mm onto a
# urethane pad instead of falling 14 mm. The slot is walled in front (75 mm), on both sides (the comb's teeth) and, behind,
# by the plate's own face. An ejector pin in each slot's floor lifts its bar 65 mm, so the gripper can take it by its
# upper end clear of the other three and of the plate's rim (round 6's suggestion), its lower 10 mm still in the slot. Our design, sizes
# assumed. Frame: the EDM's, like edm_fixture().
# round 11: the arms 165 mm out, not 112: the wire starts 150 mm left of the plate's centre and crossed the left arm
# (the movers check: 12 mm); the angle plate is 350 mm wide to take them, and the head parks 125 mm right of centre
COMB = dict(gap=0.5, wall_h=75.0, wall_t=5.0, slot_w=13.0, slot_d=7.0, floor_t=8.0, pad_t=2.0, lift=65.0, pin_r=2.5,
            arm_dx=165.0, back_gap=1.4, pin_y=-4.0)


def comb_floor_z(pc) -> float:
    """The top of the slots' pads: 0.5 mm under the bars' lower ends (the plate's centre, less half a bar)."""
    return float(pc[2]) - E8_SUB["L"] / 2 - COMB["gap"]


def _box_holes(x0, x1, y0, y1, z0, z1, holes) -> pv.PolyData:
    """Round 11: a box with square holes through it along z, holes = [(hx0, hx1, hy0, hy1)], as boxes."""
    xs = sorted({x0, x1, *[min(max(h[i], x0), x1) for h in holes for i in (0, 1)]})
    out = None
    for a, b in zip(xs[:-1], xs[1:]):
        if b - a < 1e-6:
            continue
        cuts = sorted((h[2], h[3]) for h in holes if h[0] < b - 1e-6 and h[1] > a + 1e-6)
        ys, y = [], y0
        for c0, c1 in cuts:
            if c0 > y:
                ys.append((y, min(c0, y1)))
            y = max(y, c1)
        if y < y1:
            ys.append((y, y1))
        for ya, yb in ys:
            if yb - ya > 1e-6:
                m = pv.Box(bounds=(a, b, ya, yb, z0, z1)).triangulate()
                out = m if out is None else out.merge(m)
    return out


def pin_holes(pc, bar_xs, r=3.5) -> list:
    """Round 11: the square holes the ejector pins (r 2.5) rise through, 1 mm round them."""
    y = pc[1] + COMB["pin_y"]
    return [(float(b) - r, float(b) + r, y - r, y + r) for b in bar_xs]


def catch_comb(pc, bar_xs) -> dict:
    """{name: (mesh, colour)}: the comb for bars at EDM x = bar_xs, the plate's bar face centre at pc. Its teeth and
    floor stop COMB['back_gap'] in front of the plate's face, clear of the wire, which runs 0.15 mm off it."""
    c = COMB
    x, yf, _ = pc
    yb = yf + PLATE["t"]
    z_pad = comb_floor_z(pc)
    z0 = z_pad - c["pad_t"] - c["floor_t"]
    y_back = yf - c["back_gap"]                         # the comb's back, 1.4 mm in front of the plate's face
    y_front = yf - E8_SUB["T"] - c["slot_d"] + E8_SUB["T"]   # the slot's front face (bars are 6 mm, slot 7 mm)
    y_front = min(y_front, yf - c["slot_d"])
    xs = sorted(float(b) for b in bar_xs)
    xa, xb = xs[0] - c["slot_w"] / 2 - 12.0, xs[-1] + c["slot_w"] / 2 + 12.0
    holes = pin_holes(pc, xs)                           # round 11: the pins rise through these, not through solid floor
    parts = [_box_holes(xa, xb, y_front - c["wall_t"], y_back, z0, z_pad - c["pad_t"], holes)]            # the floor
    wall = pv.Box(bounds=(xa, xb, y_front - c["wall_t"], y_front, z_pad - c["pad_t"], z_pad + c["wall_h"])).triangulate()
    edges = [xa] + [xs[0] - c["slot_w"] / 2]
    for i in range(len(xs) - 1):
        edges += [xs[i] + c["slot_w"] / 2, xs[i + 1] - c["slot_w"] / 2]
    edges += [xs[-1] + c["slot_w"] / 2, xb]
    for a, b in zip(edges[0::2], edges[1::2]):                                                        # the teeth
        parts.append(pv.Box(bounds=(a, b, y_front, y_back, z_pad - c["pad_t"], z_pad + c["wall_h"])))
    # two arms round the plate's sides to the angle plate behind it (outside the wire's travel)
    for xx in (x - c["arm_dx"], x + c["arm_dx"]):
        lo, hi = min(xx, xa - 4 if xx < x else xb), max(xx, xa if xx < x else xb + 4)
        parts.append(pv.Box(bounds=(lo - 7, hi + 7, y_front - c["wall_t"], yf - 2.0, z0, z0 + 12)))
        parts.append(pv.Box(bounds=(xx - 7, xx + 7, yf - 2.0, yb + 30, z0, z0 + 12)))
    body = parts[0]
    for m in parts[1:]:
        body = body.merge(m.triangulate())
    pads = None
    for b in xs:
        pad = _box_holes(b - c["slot_w"] / 2 + 0.5, b + c["slot_w"] / 2 - 0.5, y_front + 0.3, y_back - 0.3,
                         z_pad - c["pad_t"], z_pad, holes)
        pads = pad if pads is None else pads.merge(pad)
    return {"catch comb": (body.triangulate(), (0.30, 0.31, 0.33)), "comb wall": (wall, (0.30, 0.31, 0.33)),
            "comb pads": (pads, (0.86, 0.55, 0.18))}


def ejector_pin(pc, bx) -> pv.PolyData:
    """One slot's ejector pin and its cylinder under the comb, EDM frame, at rest (its tip flush with the pad)."""
    c = COMB
    z_pad = comb_floor_z(pc)
    y = pc[1] + c["pin_y"]
    pin = pv.Cylinder(center=(bx, y, z_pad - 14.0), direction=(0, 0, 1), radius=c["pin_r"], height=28.0,
                      resolution=16).triangulate()
    return pin


def ejector_body(pc, bar_xs) -> pv.PolyData:
    """The pins' cylinders, one block under the comb's floor (they don't move)."""
    c = COMB
    z0 = comb_floor_z(pc) - c["pad_t"] - c["floor_t"]
    xs = sorted(float(b) for b in bar_xs)
    y = pc[1] + c["pin_y"]
    return _box_holes(xs[0] - 8, xs[-1] + 8, y - 7, pc[1] - 2.0, z0 - 34, z0, pin_holes(pc, xs))    # bored for the pins


# ------------------------------------------------------------------------------------------------ MiR250, low
# PR #318, round 7: "There's no insertion gap for the intermediary storage on the MiR250. They would just fall off.
# Also, it's positioned rather high". Round 4's plate carrier and bar holder stood on posts 120 and 230 mm tall; these
# are low pockets on the cabinet's top plate instead, each with a 3 mm lead-in: the plate in a 30 mm block bored to
# take it and its stud, the specimen rack in a frame, and a rest for the tongs. MiR frame (z from the cabinet's top).
POCKETS = dict(plate=(255.0, -110.0), rack=(-255.0, -120.0), tongs=(-90.0, 255.0), block_h=40.0, rack_h=20.0,
               pocket=12.0, cradle=(250.0, 150.0), cradle_h=30.0, channel=(12.0, 5.0), channel_dx=15.0)


def mir_pockets(top: float) -> dict:
    """{name: (mesh, colour)} on the cabinet top `top`: the plate block, the rack frame, the tongs' rest."""
    import charge
    px, py = POCKETS["plate"]
    hb, dp = POCKETS["block_h"], POCKETS["pocket"]
    p = PLATE
    blk = charge.lathe([(0, top), (p["r"] + 14, top), (p["r"] + 14, top + hb), (p["r"] + 3.5, top + hb),
                        (p["r"] + 0.5, top + hb - 3), (p["r"] + 0.5, top + hb - dp), (p["stud_r"] + 1.0, top + hb - dp),
                        (p["stud_r"] + 1.0, top + hb - dp - p["stud_h"] - 2), (0, top + hb - dp - p["stud_h"] - 2)],
                       res=72)
    blk = blk.translate((px, py, 0), inplace=False)
    rx, ry = POCKETS["rack"]
    import r8_test as RT
    t = RT.TRAY
    fw, fd, fh = t["W"] + 2.0, t["D"] + 2.0, POCKETS["rack_h"]
    frame = pv.Box(bounds=(rx - fw / 2 - 12, rx + fw / 2 + 12, ry - fd / 2 - 12, ry + fd / 2 + 12, top, top + 4))
    walls = [pv.Box(bounds=(rx - fw / 2 - 12, rx + fw / 2 + 12, ry + fd / 2, ry + fd / 2 + 12, top, top + fh)),
             pv.Box(bounds=(rx - fw / 2 - 12, rx - fw / 2, ry - fd / 2 - 12, ry + fd / 2 + 12, top, top + fh)),
             pv.Box(bounds=(rx + fw / 2, rx + fw / 2 + 12, ry - fd / 2 - 12, ry + fd / 2 + 12, top, top + fh)),
             # the front wall stops either side of the fin
             pv.Box(bounds=(rx - fw / 2 - 12, rx - t["fin_t"] / 2 - 4, ry - fd / 2 - 12, ry - fd / 2, top, top + fh)),
             pv.Box(bounds=(rx + t["fin_t"] / 2 + 4, rx + fw / 2 + 12, ry - fd / 2 - 12, ry - fd / 2, top, top + fh))]
    rack = frame.triangulate()
    for w_ in walls:
        rack = rack.merge(w_.triangulate())
    tx, ty = POCKETS["tongs"]
    rest = None
    # two V-blocks under the shaft (round 11: 95 mm either side, the left one 6 mm clear of the sleeve at the handle,
    # which is 4 mm fatter than the shaft and sat 4 mm into it)
    for dx in (-95.0, 95.0):
        v = pv.Box(bounds=(tx + dx - 14, tx + dx + 14, ty - 20, ty + 20, top, top + 36)).triangulate()
        rest = v if rest is None else rest.merge(v)
    # a cradle for the room-temperature halves, kept for fractography: two channels along y, each half lying flat in
    # one with its fracture surface touching nothing
    cx_, cy_ = POCKETS["cradle"]
    ch_w, ch_d = POCKETS["channel"]
    hc = POCKETS["cradle_h"]
    # round 11: the specimen fingers (ur_arm.SPEC_FINGER) lay each half in its channel pointing down, their blades
    # either side of it 10 mm past the grasp point: a relief across each channel takes them (RELIEF, under the grasp)
    rx_, ry_, rz_ = RELIEF
    dx_ = POCKETS["channel_dx"]
    z_floor = top + hc - ch_d
    boxes = [(cx_ - 30, cx_ + 30, cy_ - 60, cy_ + 60, top, z_floor - rz_)]                    # the slab under it all
    for y0, y1 in ((cy_ - 60, cy_ - ry_), (cy_ + ry_, cy_ + 60)):                            # the floor, either side
        boxes.append((cx_ - 30, cx_ + 30, y0, y1, z_floor - rz_, z_floor))
    xs_r = [cx_ - 30, cx_ - dx_ - rx_, cx_ - dx_ + rx_, cx_ + dx_ - rx_, cx_ + dx_ + rx_, cx_ + 30]
    for a_, b_ in zip(xs_r[0::2], xs_r[1::2]):                                               # ... and between the reliefs
        boxes.append((a_, b_, cy_ - ry_, cy_ + ry_, z_floor - rz_, z_floor))
    xs_ = [cx_ - 30, cx_ - dx_ - ch_w / 2, cx_ - dx_ + ch_w / 2, cx_ + dx_ - ch_w / 2, cx_ + dx_ + ch_w / 2, cx_ + 30]
    for a_, b_ in zip(xs_[0::2], xs_[1::2]):                                                 # the channels' walls
        for y0, y1 in ((cy_ - 60, cy_ - ry_), (cy_ + ry_, cy_ + 60)):
            boxes.append((a_, b_, y0, y1, z_floor, top + hc))
        for c0, c1 in ((a_, b_),):
            segs = [(c0, c1)]
            for rc in (cx_ - dx_, cx_ + dx_):
                segs = [s for a2, b2 in segs for s in ((a2, min(b2, rc - rx_)), (max(a2, rc + rx_), b2)) if s[1] - s[0] > 0.1]
            for a2, b2 in segs:
                boxes.append((a2, b2, cy_ - ry_, cy_ + ry_, z_floor, top + hc))
    cradle = None
    for b_ in boxes:
        m_ = pv.Box(bounds=b_).triangulate()
        cradle = m_ if cradle is None else cradle.merge(m_)
    return {"plate block": (blk, (0.30, 0.32, 0.36)), "rack pocket": (rack, (0.94, 0.94, 0.92)),
            "tongs rest": (rest, (0.30, 0.32, 0.36)), "halves cradle": (cradle, (0.20, 0.36, 0.62)),
            "finger stand": (finger_stand(top), (0.30, 0.32, 0.36))}


# Round 11: the reliefs across the halves cradle's channels, half-sizes (x, y) and depth under the channel's floor: the
# specimen fingers' blades are 4 mm thick either side of a 6 mm section (outer faces 7 mm off its axis, 8.5 once
# opened to let go) and 8 mm along it, and reach 10 mm past the grasp point, which sits 3.5 mm over the floor (their
# tips 6.5 mm under it)
RELIEF = (11.0, 6.5, 10.0)
# The specimen fingers' stand (ur_arm.SPEC_FINGER), MiR frame: on the cabinet top behind the rack, the pair standing
# blades down in two slots, the caps' end plates on its top, at the spacing of the 2F-85 opened to a 30 mm gap between
# the blades and closing along the MiR's x. A spring clip in each slot holds its blade while the fingertip draws out
# of the cap against the cap's plunger (our design).
FINGER_STAND = dict(at=(-300.0, 40.0), w=80.0, d=44.0, h=72.0, gap=30.0, slot=(6.0, 12.0), depth=66.0)


def finger_stand(top: float) -> pv.PolyData:
    import ur_arm
    s = FINGER_STAND
    x0, y0 = s["at"]
    sw, sd = s["slot"]
    z1 = top + s["h"]
    xc = s["gap"] / 2 + ur_arm.SPEC_FINGER["blade_t"] / 2          # each blade's centre, either side
    zs = z1 - s["depth"]
    boxes = [(x0 - s["w"] / 2, x0 + s["w"] / 2, y0 - s["d"] / 2, y0 + s["d"] / 2, top, zs)]
    xs = [x0 - s["w"] / 2, x0 - xc - sw / 2, x0 - xc + sw / 2, x0 + xc - sw / 2, x0 + xc + sw / 2, x0 + s["w"] / 2]
    for a_, b_ in zip(xs[0::2], xs[1::2]):
        boxes.append((a_, b_, y0 - s["d"] / 2, y0 + s["d"] / 2, zs, z1))
    for a_, b_ in zip(xs[1::2], xs[2::2]):
        for ya, yb in ((y0 - s["d"] / 2, y0 - sd / 2), (y0 + sd / 2, y0 + s["d"] / 2)):
            boxes.append((a_, b_, ya, yb, zs, z1))
    out = None
    for b_ in boxes:
        m_ = pv.Box(bounds=b_).triangulate()
        out = m_ if out is None else out.merge(m_)
    return out


def finger_stand_grasp(top: float) -> np.ndarray:
    """Where the blades' grasp point is with the pair in its stand, MiR frame: 52 mm under the caps' end plates, which
    rest on the stand's top (ur_arm.SPEC_FINGER: the end plate at z 53.5 of the fingertip frame, the grasp at 105.5)."""
    import ur_arm
    s = FINGER_STAND
    sf = ur_arm.SPEC_FINGER
    return np.array([s["at"][0], s["at"][1], top + s["h"] - (sf["grasp_z"] - sf["cap_z"][1])])


def cradle_seat(top: float, i: int) -> np.ndarray:
    """Channel i's floor centre (i = 0, 1), MiR frame."""
    cx_, cy_ = POCKETS["cradle"]
    return np.array([cx_ + POCKETS["channel_dx"] * (2 * i - 1), cy_, top + POCKETS["cradle_h"] - POCKETS["channel"][1]])


def plate_seat(top: float) -> np.ndarray:
    """The plate's top face centre in its block (3 mm proud of it), MiR frame."""
    px, py = POCKETS["plate"]
    return np.array([px, py, top + POCKETS["block_h"] - POCKETS["pocket"] + PLATE["t"]])


def rack_seat(top: float) -> np.ndarray:
    """The rack's floor centre in its pocket, MiR frame."""
    rx, ry = POCKETS["rack"]
    return np.array([rx, ry, top + 4.0])


# ------------------------------------------------------------------------------------------------ the tongs
# For the hot rack (the T6's solution treatment ends at 530 C), the gripper holds a pair of tongs rather than the rack's
# fin: 300 mm of stainless shaft between the 2F-85 and the jaws, so the gripper stays out of the furnace's mouth. The
# gripper squeezes the handle's two plates, which closes the jaws on the fin through the shaft (a linkage of our design,
# assumed); the jaws are drawn fixed. Frame: the handle's grasp point at the origin, the shaft along +y.
# Round 11: the jaws 42 mm tall, not 50: at 50 they reached 3 mm into the rack's top beside the fin every time the
# tongs took it or let it go (the audit's depth limit). And the handle 90 mm further out on the cabinet (x -300, its
# rest with it): at x -210, 233 mm off the arm's axis, the arm folded so far to reach it pointing down that its
# shoulder met its forearm.
TONGS = dict(L=300.0, shaft_r=7.0, handle=(12.0, 50.0, 40.0), jaw=(30.0, 40.0, 42.0), jaw_gap=12.4)
TONGS_HANDLE = (-300.0, 255.0)    # on the MiR: the handle 325 mm off the arm's axis, the shaft along +x past the
#                                   arm's base, all on the cabinet top


def tongs() -> dict:
    t = TONGS
    hx, hl, hh = t["handle"]
    handle = pv.Box(bounds=(-hx / 2, hx / 2, -hl / 2, hl / 2, -hh / 2, hh / 2)).triangulate()
    shaft = pv.Cylinder(center=(0, hl / 2 + t["L"] / 2, 0), direction=(0, 1, 0), radius=t["shaft_r"],
                        height=t["L"], resolution=20).triangulate()
    jx, jl, jh = t["jaw"]
    y0 = hl / 2 + t["L"]
    g = t["jaw_gap"] / 2
    jaws = pv.Box(bounds=(-jx / 2, -g, y0 - 4, y0 + jl, -jh / 2, jh / 2)).triangulate().merge(
        pv.Box(bounds=(g, jx / 2, y0 - 4, y0 + jl, -jh / 2, jh / 2)).triangulate())
    sleeve = pv.Cylinder(center=(0, hl / 2 + 40, 0), direction=(0, 1, 0), radius=t["shaft_r"] + 4, height=60,
                         resolution=20).triangulate()
    return {"handle": (handle, (0.20, 0.21, 0.23)), "shaft": (shaft.merge(sleeve), (0.72, 0.73, 0.75)),
            "jaws": (jaws, (0.55, 0.56, 0.58))}


def tongs_bite() -> np.ndarray:
    """Where the fin's grasp point sits between the jaws, tongs frame."""
    t = TONGS
    return np.array([0.0, t["handle"][1] / 2 + t["L"] + t["jaw"][1] / 2, 0.0])


# ------------------------------------------------------------------------------------------------ the IPA jar's lid
# PR #318: "The IPA rinse after wire EDM should probably be capped starting out and then uncapped". The cup gets a lid
# with a knob that the gripper lifts off onto a rest beside the stand, and puts back afterwards.
LID = dict(r=34.0, t=8.0, knob_r=10.0, knob_h=26.0)
# The jar is slim (32 mm across) so the bar, held level by its upper end, goes in up to the fingers: the arm carries
# every specimen that way from the comb to the grips, and round 5's 92 mm cup with its rim knife only let a gripper
# pointing down reach in. IPA to 6 mm under the rim; an air knife ring on the rim dries the bar on the way out.
JAR = dict(r=16.0, wall=2.0, z0=880.0, z1=1000.0, liquid=994.0, ring_r=25.0, ring_h=10.0)


def ipa_jar() -> dict:
    """{name: (mesh, colour, specular, opacity)} on its stand, stand frame (z from the floor)."""
    import charge
    j = JAR
    stand = _cyl(18, (0, 0, 0), (0, 0, j["z0"]), 24).merge(_box(-90, 90, -90, 90, 0, 12))
    jar = charge.lathe([(0, j["z0"]), (j["r"], j["z0"]), (j["r"], j["z1"]), (j["r"] - j["wall"], j["z1"]),
                        (j["r"] - j["wall"], j["z0"] + 3), (0, j["z0"] + 3)], res=40)
    liquid = _cyl(j["r"] - j["wall"] - 0.4, (0, 0, j["z0"] + 3), (0, 0, j["liquid"]), 40)
    ring = charge.lathe([(j["r"] - 1, j["z1"]), (j["ring_r"], j["z1"]), (j["ring_r"], j["z1"] + j["ring_h"]),
                         (j["r"] - 1, j["z1"] + j["ring_h"])], res=40)
    line_ = _cyl(4, (j["ring_r"], 0, j["z1"] + 5), (j["ring_r"] + 50, 0, j["z1"] + 5), 12).merge(
        _cyl(4, (j["ring_r"] + 50, 0, j["z1"] + 5), (j["ring_r"] + 50, 0, 12), 12))
    import props                                     # round 9: the lab-wide jar, clear glass with a matte black cap
    js = props.jar_style()
    return {"stand": (stand, (0.24, 0.25, 0.27), 0.2, 1.0), "jar": (jar, js["glass"], 0.5, js["glass_opacity"]),
            "liquid": (liquid, (0.55, 0.72, 0.92), 0.3, 0.55), "air knife": (ring, (0.62, 0.63, 0.66), 0.5, 1.0),
            "air line": (line_, (0.20, 0.45, 0.80), 0.3, 1.0)}


def rinse_lid() -> dict:
    """{name: (mesh, colour)}: the lid, its knob; frame: the lid's underside centre."""
    l = LID
    disc = pv.Cylinder(center=(0, 0, l["t"] / 2), direction=(0, 0, 1), radius=l["r"], height=l["t"],
                       resolution=48).triangulate()
    knob = pv.Cylinder(center=(0, 0, l["t"] + l["knob_h"] / 2), direction=(0, 0, 1), radius=l["knob_r"],
                       height=l["knob_h"], resolution=24).triangulate()
    import props                                     # round 9: the lab-wide jar's matte black cap, knob and all
    return {"lid": (disc, props.jar_style()["lid"]), "knob": (knob, props.jar_style()["lid"])}


def lid_rest() -> pv.PolyData:
    """A post with a shallow cup on top for the lid, beside the jar's stand (its own frame, set by the chapter)."""
    import charge
    l = LID
    top = JAR["z1"] + JAR["ring_h"]
    post = _cyl(14, (0, 0, 0), (0, 0, top - 10), 20).merge(_box(-70, 70, -70, 70, 0, 12))
    cup = charge.lathe([(0, top - 10), (l["r"] + 6, top - 10), (l["r"] + 6, top + 4), (l["r"] + 2, top + 4),
                        (l["r"] + 2, top), (0, top)], res=48)
    return post.merge(cup)


# =========================================================================================== round 9 (chapter 5)
# ------------------------------------------------------------------------------------------- build orientations
# Sterling (PR #318, 2026-11-05 22:56): "sometimes we're going to be doing tensile bars at different orientations. How
# is that going to work with the automated EDM process?" The chapter's plate now carries two bars printed vertical (Z;
# ZXY in ISO/ASTM 52921's notation) beside its four flat ones (XY; XYZ), at the plate's right, clear of the lug. Wire
# EDM cuts in a plane that holds the wire, so a part comes off a plate that stands on edge, the wire parallel to its
# face (Calignano & Mercurio 2024; GF's CUT AM 500 turns the plate upside down instead): that one set-up cuts both kinds,
# the flat bars along their length (about 800 mm^2 each) and the vertical ones across their 10 x 6 mm foot (60 mm^2).
# On edge the vertical bars stand out of the plate's face, level, towards the front; each settles 0.5 mm into a trough
# under it as the wire frees it. notes/edm_orientations.md (its own PR) has the 45 deg bars and the limits.
ZBARS = ((68.0, -22.0), (68.0, 22.0))   # plate (x, y) of each vertical bar's foot centre: 10 mm across x, 6 mm along y


def zbar_mesh(half: str | None = None) -> pv.PolyData:
    """A bar printed vertical, in its own frame: the foot's centre at the origin, its long axis along +z (0..L), its
    10 mm grip width along x, its 6 mm thickness along y. half = 'lo' (the foot's half) or 'hi', as bar_mesh."""
    m = bar_mesh(half).translate((0.0, 0.0, -E8_SUB["T"] / 2), inplace=False)
    m.rotate_x(90.0, inplace=True)                 # long axis y -> z, thickness z -> y
    m.translate((0.0, 0.0, E8_SUB["L"] / 2), inplace=True)
    return m


def zbar_edm(pc, k: int) -> tuple:
    """(x, z) in the EDM's frame of vertical bar k's axis when the plate stands on edge (plate x -> EDM -x, plate
    y -> EDM -z, plate z -> EDM -y), the plate's bar face centre at pc."""
    zx, zy = ZBARS[k]
    return float(pc[0]) - zx, float(pc[2]) - zy


# round 11: the lower trough stops 72 mm out, not 2 mm past the bar's end: the specimen fingers take each vertical bar
# 13 mm from its free end with blades either side of it, where the trough's walls stood
TROUGH = dict(gap=0.5, clear=1.0, wall=2.0, wall_h=4.0, floor_t=4.0, y0=6.0, reach=(60.0, 72.0), post=(-90.0, -78.0),
              post_y=(-32.0, -20.0))


def zbar_troughs(pc) -> dict:
    """{name: (mesh, colour)}: a U trough under each vertical bar (EDM frame), its floor 0.5 mm under the bar, 1 mm
    each side of it, from 6 mm off the plate's face (clear of the wire, 0.15 mm off it) to 72 mm out (round 11: short
    of the specimen fingers' blades at the free end); both hang off one post that stands on the comb's left arm, left of the bars, so the gripper reaches each
    free end from the front. The upper trough stops 60 mm out (the bar's centre of mass is 50 mm out), so the lower
    bar's free end is open from the front once the upper bar is gone. Our design; sizes assumed."""
    c, t = COMB, TROUGH
    x, yf, _ = pc
    z_arm = comb_floor_z(pc) - c["pad_t"] - c["floor_t"]           # the comb's floor and arms start here
    hw = 5.0 + t["clear"]
    parts, tops = [], []
    for k in range(len(ZBARS)):
        bx, bz = zbar_edm(pc, k)
        top = bz - E8_SUB["T"] / 2 - t["gap"]                      # the trough's floor, 0.5 mm under the bar
        tops.append(top)
        y1 = yf - t["y0"]
        y0 = yf - t["reach"][1 if k == 1 else 0] if bz < float(pc[2]) else yf - t["reach"][0]
        parts += [pv.Box(bounds=(bx - hw - t["wall"], bx + hw + t["wall"], y0, y1, top - t["floor_t"], top)),
                  pv.Box(bounds=(bx - hw - t["wall"], bx - hw, y0, y1, top, top + t["wall_h"])),
                  pv.Box(bounds=(bx + hw, bx + hw + t["wall"], y0, y1, top, top + t["wall_h"])),
                  # its web to the post
                  pv.Box(bounds=(x + t["post"][0], bx - hw - t["wall"] + 0.5, yf + t["post_y"][0], yf + t["post_y"][1],
                                 top - t["floor_t"], top))]
    parts.append(pv.Box(bounds=(x + t["post"][0], x + t["post"][1], yf + t["post_y"][0], yf + t["post_y"][1], z_arm,
                                max(tops))))
    # its foot, forward along the arm to it
    parts.append(pv.Box(bounds=(x + t["post"][0], x + t["post"][1], yf + t["post_y"][0], yf - 2.0 - 10.0 + 0.5, z_arm,
                                z_arm + 12.0)))
    body = parts[0].triangulate()
    for m in parts[1:]:
        body = body.merge(m.triangulate())
    return {"zbar troughs": (body, (0.30, 0.31, 0.33))}


def zbar_grasp_local() -> tuple:
    """Where the gripper takes a vertical bar (its own frame): 13 mm in from its free end, on its axis."""
    return (0.0, 0.0, E8_SUB["L"] - 13.0)


# ------------------------------------------------------------------------------------ the depowdering box's clamps
# Sterling (PR #318, 2026-11-05 22:56): "It's not clear how that depowdering box actually gets the plate to stay on it.
# Is it clamped somehow?" It is, twice over. The plate's stud is pulled into the zero-point chuck (rounds 4-8 said so
# only in a caption), and three swing clamps on the rotor, 120 deg apart round the plate, rise, swing their arms over
# its rim and pull down on it before the shaft turns, and let go after. Solukon's units clamp the build plate to the
# rotary table or to an adapter plate for each machine's plates (its SFM-AT200 page lists the part envelope, 300 x 300 x
# 230 mm, 60 kg with the plate, a horizontal axis that swivels about 350 deg and a vibrator, but not the clamping, which
# its datasheet, sent on request, would have); swing clamps of this kind are a catalogue part (e.g. ROEMHELD's). The
# three clamps are our design. Arms open, they sit below the chuck's top, out of the plate's way as it is set down.
CLAMPS = dict(r=100.0, angles=(60.0, -60.0, 140.0), body_r=14.0, rod_r=5.0, arm=(29.0, 10.0, 8.0), rise=34.0)


def clamp_body(top: float) -> pv.PolyData:
    """The clamps' fixed parts on the rotor (DBOX frame): three cylinder bodies under the plate's rim, each on an arm
    from the chuck; `top` = the chuck's top (the plate's underside)."""
    p, c = DBOX, CLAMPS
    out = None
    for a in c["angles"]:
        u = np.array([math.cos(math.radians(a)), math.sin(math.radians(a)), 0.0])
        cx_, cy_ = p["chuck_x"] + c["r"] * u[0], p["axis_y"] + c["r"] * u[1]
        body = _cyl(c["body_r"], (cx_, cy_, top - 50.0), (cx_, cy_, top - 8.0), 24)
        arm_p0 = np.array([p["chuck_x"], p["axis_y"], top - 44.0]) + 40.0 * u
        arm = _cyl(7.0, arm_p0, (cx_, cy_, top - 44.0), 16)
        out = body.merge(arm) if out is None else out.merge(body).merge(arm)
    return out


def clamp_arm() -> pv.PolyData:
    """One clamp's moving part in its own frame: the rod on the clamp's axis (z), its top at z 0, and the arm along
    +x from it, its underside at z 0. Closed, the frame sits at the plate's top face over the clamp's axis, the arm
    pointing at the plate's centre."""
    c = CLAMPS
    L, w, h = c["arm"]
    rod = _cyl(c["rod_r"], (0, 0, -60.0), (0, 0, h), 16)
    arm = pv.Box(bounds=(-8.0, L, -w / 2, w / 2, 0.0, h)).triangulate()
    pad = _cyl(4.0, (L - 5.0, 0, -1.5), (L - 5.0, 0, 0.0), 12)
    return rod.merge(arm).merge(pad)


def clamp_pose(i: int, top: float, f: float) -> np.ndarray:
    """Clamp i's arm (DBOX frame) at f closed: 0 open (down, under the chuck's top, turned 90 deg off the plate),
    0.5 risen and still turned away, 1 swung in over the rim and pulled down onto the plate's top face."""
    c = CLAMPS
    a = c["angles"][i]
    u = (math.cos(math.radians(a)), math.sin(math.radians(a)))
    lift = min(1.0, 2.0 * f)
    swing = max(0.0, 2.0 * f - 1.0)
    # round 11: the pad (1.5 mm under the arm) closes 0.1 mm over the plate's top face, and swings in 3 mm higher;
    # round 10 closed it 1.5 mm into the plate and swung it in 2 mm lower still (the movers check: 3 mm deep)
    z = top + PLATE["t"] + 1.6 - c["rise"] * (1.0 - lift) + 3.0 * (1.0 - swing) * (lift >= 1.0)
    yaw = a + 180.0 + 90.0 * (1.0 - swing)            # closed: pointing at the plate's centre
    t_, ca, sa = math.radians(yaw), 0.0, 0.0
    ca, sa = math.cos(t_), math.sin(t_)
    m = np.eye(4)
    m[:2, :2] = [[ca, -sa], [sa, ca]]
    m[:3, 3] = (DBOX["chuck_x"] + c["r"] * u[0], DBOX["axis_y"] + c["r"] * u[1], z)
    return m
