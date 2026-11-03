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
