#!/usr/bin/env python3
"""The chemical waste station: the ducted fume hood's base as a vented solvent cabinet and a vented acid cabinet, an
intake tray on the hood's work surface, and a MiR250 + UR10e bringing a capped bottle (#303, PR #318; notes/waste.md).

    xvfb-run -a python3 waste_station.py          # -> out/waste_station_still.png (one frame, about a minute)

Our design throughout. The hood is instruments_r7's Labconco Protector XStream 4 ft (``FH``: 1219 x 958 x 1499 mm,
the work surface at 932 mm, the sash raised to its 18 in, 457 mm, stop), drawn here as boxes so that this file needs no
cadquery. Its base is split into two cabinets the size of the base: a solvent cabinet (left) and an acid cabinet
(right), each vented to the hood, with their doors drawn see-through. Container sizes are typical (a 2.5 gal safety
can, 4 L and 10 L bottles, 1 L bottles), not a supplier's drawing. Where things go and why: notes/waste.md, "The waste
station".
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import props as P            # noqa: E402
from scene import OUT, R, Scene, T      # noqa: E402

# instruments_r7.FH, copied (that module needs cadquery)
FH = dict(W=1219.0, D=958.0, Hh=1499.0, cab=900.0, top=32.0, post=100.0, sash=(960.0, 1750.0), stop=457.0,
          collar=325.0)
W, D = FH["W"], FH["D"]
XW, YF, YB = W / 2, -D / 2, D / 2          # the hood's half width, front and back (front at -y, the aisle side)
Z0 = FH["cab"] + FH["top"]                 # 932: the work surface
ZT = Z0 + FH["Hh"]                         # 2431: the hood's top
XI = XW - FH["post"]
SASH_LIFT = FH["stop"]                     # raised to the 18 in stop

WHITE = (0.93, 0.93, 0.91)
LINER = (0.80, 0.81, 0.80)
EPOXY = (0.12, 0.12, 0.13)
STEEL = (0.62, 0.64, 0.67)
YELLOW = (0.96, 0.78, 0.10)                # the solvent cabinet: flammable-storage yellow
RED = (0.80, 0.12, 0.10)
ACIDBLUE = (0.30, 0.45, 0.70)              # the acid cabinet's doors
TRAY = (0.94, 0.94, 0.90)                  # polyethylene trays
GLASS = (0.80, 0.90, 0.95)
HDPE = (0.92, 0.92, 0.88)
AMBER = (0.55, 0.30, 0.08)
IPA_C = (0.70, 0.85, 1.00)
ACID_C = (0.85, 0.93, 0.85)
WECK_C = (0.45, 0.10, 0.45)
CAP = (0.10, 0.10, 0.11)
LABEL = (1.0, 1.0, 1.0)
GREEN_YEL = (0.30, 0.65, 0.20)
FLOOR_C = (0.86, 0.86, 0.84)
TAPE = (0.98, 0.80, 0.10)


def box(x0, y0, z0, x1, y1, z1) -> pv.PolyData:
    return pv.Box(bounds=(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1),
                          max(z0, z1))).triangulate()


def cyl(r, h, x=0.0, y=0.0, z=0.0, res=40) -> pv.PolyData:
    return pv.Cylinder(center=(x, y, z + h / 2), direction=(0, 0, 1), radius=r, height=h, resolution=res).triangulate()


def bottle(x, y, z, r, h, liquid, fill=0.6, cap_r=None, glass=GLASS) -> list:
    """A capped bottle: body, shoulder, cap, label and its liquid, standing at (x, y, z)."""
    cap_r = cap_r or r * 0.45
    body = cyl(r, h * 0.78, x, y, z)
    sh = pv.Cone(center=(x, y, z + h * 0.78 + h * 0.06), direction=(0, 0, 1), height=h * 0.12, radius=r,
                 resolution=40).triangulate()
    neck = cyl(cap_r * 0.9, h * 0.06, x, y, z + h * 0.84)
    cap = cyl(cap_r, h * 0.1, x, y, z + h * 0.9)
    lab = cyl(r + 0.6, h * 0.3, x, y, z + h * 0.22)
    liq = cyl(r - 2.0, h * 0.78 * fill, x, y, z + 2.0)
    return [("body", body.merge(sh).merge(neck), glass, 0.35), ("liquid", liq, liquid, 0.85),
            ("cap", cap, CAP, 1.0), ("label", lab.clip_box((x - r - 2, x + r + 2, y - r - 2, y, z, z + h), invert=False),
                                     LABEL, 1.0)]


def safety_can(x, y, z, r=120.0, h=300.0) -> list:
    """A red steel safety can (Type I style) with its spring lid and a green-yellow bond wire."""
    body = cyl(r, h, x, y, z)
    top = pv.Cone(center=(x, y, z + h + 25), direction=(0, 0, 1), height=50, radius=r, resolution=40).triangulate()
    lid = cyl(28, 18, x + r * 0.45, y, z + h + 40)
    handle = box(x - 15, y - r * 0.8, z + h + 50, x + 15, y + r * 0.8, z + h + 62)
    band = cyl(r + 1, 70, x, y, z + h * 0.35)
    wire = pv.Spline(np.array([[x - r, y, z + 60], [x - r - 40, y + 20, z + 20], [x - r - 60, y + 60, 2.0]]), 20) \
        .tube(radius=3.0, n_sides=10).triangulate()
    return [("can", body.merge(top).merge(lid).merge(handle), RED, 1.0), ("can label", band, YELLOW, 1.0),
            ("bond wire", wire, GREEN_YEL, 1.0)]


def hood() -> list:
    out = []
    a = out.append
    # the base: two cabinets the base's size, each with its own doors (see-through, so the containers show)
    gap = 10.0
    for side, (x0, x1), door_c, name in ((-1, (-XW, -gap / 2), YELLOW, "solvent"), (1, (gap / 2, XW), ACIDBLUE, "acid")):
        a((f"{name} cabinet shell", box(x0, YF + 40, 0, x1, YB, 40).merge(box(x0, YF + 40, FH["cab"] - 30, x1, YB,
                                                                         FH["cab"]))
           .merge(box(x0, YB - 20, 40, x1, YB, FH["cab"] - 30))
           .merge(box(x0, YF + 40, 40, x0 + 20, YB, FH["cab"] - 30))
           .merge(box(x1 - 20, YF + 40, 40, x1, YB, FH["cab"] - 30)), door_c if name == "solvent" else WHITE, 1.0))
        a((f"{name} cabinet shelf", box(x0 + 20, YF + 60, 440, x1 - 20, YB - 20, 460), door_c if name == "solvent"
           else WHITE, 1.0))
        a((f"{name} cabinet doors", box(x0 + 8, YF + 38, 50, x1 - 8, YF + 42, FH["cab"] - 40), door_c, 0.22))
        # door frames and the warning band, opaque, so the doors read as doors
        a((f"{name} door frame", box(x0 + 8, YF + 36, 50, x1 - 8, YF + 42, 70)
           .merge(box(x0 + 8, YF + 36, FH["cab"] - 60, x1 - 8, YF + 42, FH["cab"] - 40))
           .merge(box(x0 + 8, YF + 36, 50, x0 + 28, YF + 42, FH["cab"] - 40))
           .merge(box(x1 - 28, YF + 36, 50, x1 - 8, YF + 42, FH["cab"] - 40))
           .merge(box((x0 + x1) / 2 - 6, YF + 36, 50, (x0 + x1) / 2 + 6, YF + 42, FH["cab"] - 40)), door_c, 1.0))
        a((f"{name} warning band", box(x0 + 60, YF + 34, FH["cab"] - 160, x1 - 60, YF + 36, FH["cab"] - 100),
           RED if name == "solvent" else (0.95, 0.95, 0.95), 1.0))
        # the cabinet's vent: a tube from its back up into the hood's duct space
        vx = (x0 + x1) / 2
        a((f"{name} vent", pv.Spline(np.array([[vx, YB - 60, FH["cab"] - 40], [vx, YB + 40, FH["cab"] + 80],
                                                [vx * 0.4, YB + 60, ZT - 300], [0, YB - 160, ZT + 20]]), 40)
           .tube(radius=22, n_sides=16).triangulate(), STEEL, 1.0))
    a(("work surface", box(-XW, YF, FH["cab"], XW, YB, Z0), EPOXY, 1.0))
    for sx in (-1, 1):
        x0 = XI if sx > 0 else -XW
        a((f"post {sx}", box(x0, YF, Z0, x0 + FH["post"], YB, ZT - 200), WHITE, 1.0))
    a(("hood top", box(-XW, YF, ZT - 200, XW, YB, ZT), WHITE, 1.0))
    a(("back", box(-XI, YB - 30, Z0, XI, YB, ZT - 200), WHITE, 1.0))
    a(("fascia", box(-XI, YF, FH["sash"][1] + SASH_LIFT * 0 + 0, XI, YF + 20, ZT - 200), WHITE, 1.0))
    a(("airfoil", box(-XI, YF, Z0, XI, YF + 39, Z0 + 28), STEEL, 1.0))
    a(("baffle", box(-XI, YB - 78, Z0 + 28, XI, YB - 66, ZT - 240), LINER, 1.0))
    s0, s1 = FH["sash"]
    a(("sash glass", box(-XI + 5, YF + 30, s0 + SASH_LIFT + 30, XI - 5, YF + 40, min(s1 + SASH_LIFT, ZT - 210)),
       GLASS, 0.25))
    a(("sash handle", box(-XI + 5, YF + 26, s0 + SASH_LIFT, XI - 5, YF + 44, s0 + SASH_LIFT + 30), STEEL, 1.0))
    a(("collar", cyl(FH["collar"] / 2, 150, 0, 200, ZT), STEEL, 1.0))
    a(("duct", cyl(FH["collar"] / 2 - 5, 900, 0, 200, ZT + 150), STEEL, 1.0))
    a(("airflow monitor", box(XI + 20, YF - 1, 1600, XI + 80, YF, 1660), (0.3, 0.75, 0.4), 1.0))
    return out


def cabinet_contents() -> list:
    out = []
    # solvent cabinet (left half, x -609..-5): lower shelf, the grounded safety can of sieve-wash IPA (with Al fines)
    # and a 10 L can of rinse IPA; upper shelf, the Form Wash IPA (with resin) in an amber 4 L bottle and the used BN cans
    for nm, m, c, op in safety_can(-430.0, 60.0, 40.0):
        out.append((f"sieve IPA {nm}", m, c, op))
    for nm, m, c, op in safety_can(-180.0, 60.0, 40.0, r=110.0, h=280.0):
        out.append((f"rinse IPA {nm}", m, c, op))
    for nm, m, c, op in bottle(-450.0, 60.0, 460.0, 80.0, 330.0, (0.75, 0.55, 0.20), fill=0.5, glass=AMBER):
        out.append((f"form wash IPA {nm}", m, c, op))
    bin_ = box(-300, -60, 460, -60, 180, 470).merge(box(-300, -60, 460, -60, -50, 560))
    out.append(("aerosol bin", bin_, (0.55, 0.57, 0.60), 1.0))
    for i, (cx, cy) in enumerate(((-250, 20), (-185, 70), (-120, 20))):
        out.append((f"used BN can {i}", cyl(34, 200, cx, cy, 470).merge(
            pv.Cone(center=(cx, cy, 685), direction=(0, 0, 1), height=30, radius=34).triangulate()),
            (0.85, 0.85, 0.88), 1.0))
    # acid cabinet (right half, x 5..609): upper shelf tray, the Acid Aqueous carboy; lower shelf, its own tray, the
    # Weck's bottle (base, oxidizer) a shelf apart from the acid
    out.append(("acid tray", box(60, -300, 460, 560, 380, 520).merge(box(70, -290, 470, 550, 370, 520)).extract_surface(algorithm=None)
                .triangulate(), TRAY, 1.0))
    for nm, m, c, op in bottle(300.0, 40.0, 470.0, 115.0, 380.0, ACID_C, fill=0.35, glass=HDPE):
        out.append((f"acid carboy {nm}", m, c, op))
    out.append(("base tray", box(60, -300, 40, 560, 380, 100), TRAY, 1.0))
    for nm, m, c, op in bottle(220.0, 60.0, 100.0, 50.0, 200.0, WECK_C, fill=0.4, glass=HDPE):
        out.append((f"weck bottle {nm}", m, c, op))
    return out


INTAKE = dict(x=150.0, y=YF + 230.0, w=420.0, d=300.0, h=60.0)     # inside the sash, 230 mm behind the hood's front
MIR_X = 760.0           # the unit stands right of the hood's centre (the still's choice, so the cabinets show)


def work_surface() -> tuple[list, list]:
    """The intake tray (right) and the etch (left), on the work surface. Returns the parts and the nests' (x, y, z)."""
    p = INTAKE
    x0, x1 = p["x"] - p["w"] / 2, p["x"] + p["w"] / 2
    y0, y1 = p["y"] - p["d"] / 2, p["y"] + p["d"] / 2
    out = []
    tray = box(x0, y0, Z0, x1, y1, Z0 + 8)
    for (a0, a1, b0, b1) in ((x0, x1, y0, y0 + 6), (x0, x1, y1 - 6, y1), (x0, x0 + 6, y0, y1), (x1 - 6, x1, y0, y1),
                             (p["x"] - 3, p["x"] + 3, y0, y1)):
        tray = tray.merge(box(a0, b0, Z0, a1, b1, Z0 + p["h"]))
    out.append(("intake tray", tray, TRAY, 1.0))
    nests = []
    for i, nx in enumerate((x0 + p["w"] / 4, x0 + 3 * p["w"] / 4)):
        ring = pv.Disc(center=(nx, p["y"], Z0 + 9), inner=48, outer=56, normal=(0, 0, 1), c_res=48).triangulate()
        out.append((f"nest {i}", ring.extrude((0, 0, 16), capping=True).triangulate(), (0.35, 0.37, 0.40), 1.0))
        nests.append((nx, p["y"], Z0 + 8))
    # one bottle already delivered (rinse acid, left nest), the other nest waiting for the arm's
    for nm, m, c, op in bottle(nests[0][0], nests[0][1], Z0 + 8, 45.0, 190.0, ACID_C, fill=0.55, glass=HDPE):
        out.append((f"delivered {nm}", m, c, op))
    # the rack of empties beside it, and the etch at the other end (25 mL of Weck's in a beaker, and a rinse)
    rack = box(x1 + 15, y0 + 40, Z0, x1 + 75, y1 - 40, Z0 + 30)
    out.append(("empties rack", rack, (0.35, 0.37, 0.40), 1.0))
    for k, ry in enumerate((p["y"] - 50, p["y"] + 50)):
        for nm, m, c, op in bottle(x1 + 45, ry, Z0 + 30, 26.0, 120.0, (1, 1, 1), fill=0.0, glass=HDPE):
            out.append((f"empty {k} {nm}", m, c, op))
    for k, (bx, liq) in enumerate(((-380.0, WECK_C), (-280.0, (0.75, 0.88, 1.0)))):
        beaker = cyl(32, 70, bx, YF + 260, Z0).boolean_difference(cyl(29, 70, bx, YF + 260, Z0 + 3)) \
            if False else cyl(32, 70, bx, YF + 260, Z0)
        out.append((f"etch beaker {k}", beaker, GLASS, 0.35))
        out.append((f"etch liquid {k}", cyl(29, 22, bx, YF + 260, Z0 + 3), liq, 0.9))
    return out, nests


def floor() -> list:
    return [("floor", box(-2600, -2600, -10, 2600, 900, 0), FLOOR_C, 1.0),
            ("aisle tape", box(-2600, -479 - 838 - 25, 0, 2600, -479 - 838 + 25, 1.5), TAPE, 1.0)]


SOLIDS = {   # the hood's parts the arm must keep 10 mm off (posts, sash and its handle, fascia, work surface), mm
    "right post": (XI - 10, XW + 10, YF - 10, YB, Z0, ZT - 200),
    "left post": (-XW - 10, -XI + 10, YF - 10, YB, Z0, ZT - 200),
    "sash": (-XI, XI, YF + 16, YF + 54, FH["sash"][0] + SASH_LIFT - 10, ZT - 200),
    "fascia": (-XI, XI, YF - 10, YF + 30, FH["sash"][1] - 10, ZT - 200),
    "work surface": (-XW - 10, XW + 10, YF - 10, YB, 0, Z0 + 10),
}


def _hits(base, q, arm_pts, grip_pts) -> int:
    """How many of the arm's and gripper's mesh points (the held bottle aside) fall inside SOLIDS at joint angles q."""
    import ur_arm
    fk = ur_arm.fk("ur10e", q)
    gfk = ur_arm.gripper_fk(0.55)
    Tb = T(base)
    n = 0
    clouds = [(Tb @ fk[l], pts) for l, pts in arm_pts.items()]
    clouds += [(Tb @ fk["tool0"] @ gfk[g], pts) for g, pts in grip_pts.items()]
    for M, pts in clouds:
        Wp = (M[:3, :3] @ pts.T).T + M[:3, 3]
        for x0, x1, y0, y1, z0, z1 in SOLIDS.values():
            n += int(np.count_nonzero((Wp[:, 0] > x0) & (Wp[:, 0] < x1) & (Wp[:, 1] > y0) & (Wp[:, 1] < y1)
                                      & (Wp[:, 2] > z0) & (Wp[:, 2] < z1)))
    return n


def build() -> tuple[Scene, dict]:
    sc = Scene("waste_station", "The chemical waste station: the fume hood's base as solvent and acid cabinets",
               size=(1920, 1080), gif=False, mp4=False)
    for group, parts in (("floor", floor()), ("hood", hood()), ("contents", cabinet_contents())):
        for nm, m, c, op in parts:
            sc.add(f"{group}/{nm}", m, c, group, opacity=op)
    ws, nests = work_surface()
    for nm, m, c, op in ws:
        sc.add(f"surface/{nm}", m, c, "surface", opacity=op)

    # the unit: a MiR250 + UR10e parked in front of the hood, the arm setting a capped 1 L bottle of sieve-wash IPA in
    # the intake tray's empty nest through the raised sash. The spot is searched: the dock line (the MiR's side 80 mm off
    # the row) and further back, the first where the arm finds a level-ish approach with its forearm outside the sash
    import robot as RB
    import ur_arm
    target = np.array([nests[1][0], nests[1][1], nests[1][2] + 120.0])     # grasp the bottle at its shoulder
    arm_pts = {l: np.vstack([m.points for m, _, _ in lst]) for l, lst in ur_arm.arm_meshes("ur10e").items()}
    grip_pts = {g: np.vstack([m.points for m, _, _ in lst]) for g, lst in ur_arm.gripper_meshes().items()}
    best, tried = None, []
    for mir_x in (MIR_X, MIR_X - 110.0, MIR_X - 220.0, MIR_X - 330.0, MIR_X - 440.0):
        for back in (0.0, 120.0, 240.0, 360.0):
            for pitch in (0.0, 15.0, 30.0, 45.0):
                mir_y = YF - 80.0 - P.MIR["W"] / 2 - back
                base = np.array([mir_x, mir_y + 130.0, P.AMR_TOP])
                app = np.array([0.0, math.cos(math.radians(pitch)), -math.sin(math.radians(pitch))])
                Tb = np.linalg.inv(T(base)) @ P.tcp_frame(target, app, 0.0)
                try:
                    q = ur_arm.ik("ur10e", Tb, np.radians([-90.0, -120.0, 110.0, -80.0, -90.0, 0.0]))
                except ValueError:
                    continue
                h = _hits(base, q, arm_pts, grip_pts)
                tried.append((h, mir_x, back, pitch))
                if h == 0:
                    best = (back, pitch, base, q)
                    break
            if best:
                break
        if best:
            break
    if best is None:
        raise SystemExit(f"no clear arm pose found for the intake tray; fewest points inside: {sorted(tried)[:5]}")
    back, pitch, base, q = best
    mir_y = base[1] - 130.0
    mir_x = base[0]
    for nm, (mesh, col) in P.mir250().items():
        sc.add(f"amr/{nm}", mesh, col, "amr", **(dict(ambient=0.8) if "light" in nm else {}))
    sc.gmat["amr"] = T((mir_x, mir_y, 0.0))
    # the waste carrier on the MiR's deck: a PE spill tray with one nest per class (ours)
    carrier = box(-380, -250, 0, -160, -60, 6)
    for (a0, a1, b0, b1) in ((-380, -160, -250, -244), (-380, -160, -66, -60), (-380, -374, -250, -60),
                             (-166, -160, -250, -60)):
        carrier = carrier.merge(box(a0, b0, 0, a1, b1, 50))
    sc.add("amr/waste carrier", carrier.translate((0, 0, P.AMR_TOP - 20), inplace=False), TRAY, "amr")
    rb = RB.Robot(sc, "ur10e", "amr", T((0.0, 130.0, P.AMR_TOP)), q0=np.degrees(q), prefix="amrur")
    rb.set(q=q, close=0.55)
    # the held bottle, in the gripper
    held = bottle(0, 0, -120.0, 45.0, 190.0, IPA_C, fill=0.75, glass=HDPE)
    held.append(("band", cyl(46.5, 40, 0, 0, -120.0 + 190 * 0.5), RED, 1.0))
    tcp = rb.tcp_world()
    for nm, m, c, op in held:
        sc.add(f"held/{nm}", m, c, "held", opacity=op)
    sc.gmat["held"] = T(target - np.array([0, 0, 0])) @ T((0, 0, 0))
    sc.gmat["held"] = T((target[0], target[1], target[2]))
    return sc, dict(mir_x=round(float(mir_x)), back=back, pitch=pitch, tcp=np.round(tcp[:3, 3], 1).tolist(),
                    target=target.tolist(), hood_points_hit=_hits(base, q, arm_pts, grip_pts))


LABELS = [
    ("Solvent cabinet, vented: IPA with Al fines (grounded can),\nrinse IPA, Form Wash IPA with resin, used BN cans",
     (-330.0, YF + 40.0, 650.0), (0.03, 0.70)),
    ("Acid cabinet, vented: Acid Aqueous on one shelf,\nWeck's (base, oxidizer) on the other, each in its own tray",
     (330.0, YF + 40.0, 250.0), (0.03, 0.85)),
    ("Intake tray in the hood's airflow:\nclosed bottles only, one nest per class", (80.0, YF + 230.0, Z0 + 60.0),
     (0.80, 0.22)),
    ("The etch, kept apart: 25 mL of Weck's", (-330.0, YF + 260.0, Z0 + 40.0), (0.03, 0.42)),
    ("MiR250 + UR10e: one class a trip, in the\ndeck's spill tray; it never opens or pours", (None, -1000.0, 830.0),
     (0.80, 0.78)),
]


def main() -> None:
    sc, info = build()
    sc.cam = [(-1500.0, -4700.0, 2350.0), (150.0, -300.0, 1050.0), (0, 0, 1)]
    sc.view_angle = 38.0
    sc.title = "Waste station: the hood's base as solvent and acid cabinets, an intake tray, a unit bringing a bottle"
    sc.caption = ("Our design (notes/waste.md): the arm sets a capped bottle of sieve-wash IPA in the intake tray under "
                  "the raised sash; a person moves bottles into the cabinets each day shift.")
    sc.labels = [(t, (info["mir_x"] - 270.0 if xyz[0] is None else xyz[0], xyz[1], xyz[2]), f, 1.0)
                 for t, xyz, f in LABELS]
    base = sc.render_base()
    anchors = [sc.project(xyz) for _, xyz, _, _ in sc.labels]
    img = sc.overlay(Image.fromarray(base), 1.5, anchors)
    OUT.mkdir(exist_ok=True)
    path = OUT / "waste_station_still.png"
    img.convert("RGB").save(path)
    print(path, info, flush=True)


if __name__ == "__main__":
    main()
