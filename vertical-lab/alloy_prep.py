"""The alloy route, chapter 6: sample prep. Chapter 5's AlSi10Mg build is sectioned and two specimens are made for
chapter 7 (#303, PR #318, round 8).

    VIZ3D_FPS=6 xvfb-run --server-num=11 -a python3 alloy_prep.py      # -> out/alloy_prep.{gif,json}, out/mp4/alloy_prep.mp4,
                                                                        #    out/alloy_prep_still.png
    PREVIEW=1 xvfb-run --server-num=11 -a python3 alloy_prep.py         # the last frame of each step -> /tmp
    ARM_AUDIT=1 xvfb-run --server-num=11 -a python3 alloy_prep.py       # every frame collision-checked -> out/collisions/

The lab is the two-Shuttle floor of ``setup_lab.py`` (every tray loaded, the floor machines, the utilities). The
UR10e on its MiR250 does every transfer; nothing moves on its own except what a machine moves itself:

1. **Sectioning, on the wire EDM** (the floor's FANUC, chapter 5's): a coupon (14 x 10 x 6 mm) and a slice
   (10 x 10 x 6 mm) ride the MiR's caddy (ours) with the steel puck and the press's stopper.
2. **The steel mount**, on the caddy: the slice into the puck's pocket, released in its mouth and pressed home by the
   closed fingers; a ball plunger in the pocket wall holds it (``r8_specimens.steel_mount``).
3. **The Carvera** (tray M, Shuttle 2) faces the slice flush with the puck, parallel to its base: the arm loads the
   puck into the vise. Then into the PX500's 6-position holder, face up, and the holder turned over on its rest.
4. **The LECO MX400** (tray F, Shuttle 1), the lab's video step by step: the coupon on the ram face down, compound
   from a doser (ours), the stopper set in the mold's mouth and pressed down by the closed fingers, the cycle, then
   the stopper off and the mount into the holder.
5. **The PX500** (tray F): the holder onto the head; the arm changes whole pre-loaded discs (each with its paper or
   cloth and its retaining ring) between the magazine and the magnetic platen, 320 to 1200 grit SiC, then the cloth
   with 1 um alumina, at the lab's SOP's settings (PR #258), with a rinse between grits.
6. The holder back on its rest, turned face up; what the SOP does next (ethanol, ultrasonic, the VibroMet 2) and what
   is hard to automate.

Sources and what is assumed: notes/alloy_prep.md.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pyvista as pv

import scene
scene.GIF_FPS = 2                      # a ~5-minute GIF under 4.9 MB (the MP4 keeps every frame)
scene.GIF_SIZE = (480, 270)
from scene import PREVIEW, T, R  # noqa: E402

import animate as A                    # noqa: E402
import lab                             # noqa: E402
import props as P                      # noqa: E402
import r8_prep as RP                   # noqa: E402
import r8_specimens as SP              # noqa: E402
import robot as RB                     # noqa: E402

NAME = "alloy_prep"
TITLE = "Vertical cloud lab, the alloy route 6/7: sample prep"
FAST = 0.30                            # the later disc changes: a time-lapse
CAM_LAB = [(9800, -12500, 6900), (1700, -1800, 1300), (0, 0, 1)]

# where the MiR stops on the dock line in front of the two Shuttles (x of its centre; heading 0, the arm's side to
# the VLM): at Shuttle 2 with the Carvera (tray M's right end) in reach, at Shuttle 1 with the MX400 (tray F's left
# end) in reach, and at Shuttle 1's dock for the PX500 and its disc magazine. Chosen with PREP_PROBE=1 (below): at
# -800 every gripper spin over the mold has a clear arm, at -720 a quarter of them collide with camera F0's head
X_CNC = None                           # set from setup_lab.X2 in movie()
X_PRESS = -800.0
X_POL = 0.0
MIR_V = 900.0                          # mm/s, the MiR's top speed along the line here (at 0.3 m/s^2, props.ramp_secs)

# ours on the MiR's cabinet top (MiR frame, x along the MiR, +y towards the VLM; the arm's base at animate.ARM_LOCAL)
CAB_TOP = P.MIR["H"] + P.CAB_H
CADDY = dict(x0=-130.0, x1=95.0, y=-200.0, w=70.0, h=30.0)
SEAT = {"stopper": -92.0, "puck": -36.0, "coupon": 14.0, "slice": 56.0}     # x along the caddy's centre line
REST_AT = (-245.0, -165.0)             # the holder's rest (as alloy_characterize, round 7)
REST = dict(d=190.0, base=4.0, pin_d=12.0, pin_h=16.0, pin_r=66.0, pins=(30.0, 150.0, 330.0))
HOLDER = dict(d=150.0, t=12.0, r=52.0, tab_w=24.0, tab_l=55.0, below=13.0)
POCKET_STEEL, POCKET_HOT = 90.0, 210.0     # the two pockets we use (deg, holder frame); the tab is at 270
STOP = dict(d=RP.MX["bore"] - 0.6, h=RP.MX["stopper_h"])
DOWN_TIP = 20.1                        # the grasp point this far over a part's foot: the pads' tips 1 mm over it


def g_open(gap):
    """2F-85 closure for a gap (mm): gap = 28 - 90 (c - 0.70)."""
    return 0.70 + (28.0 - gap) / 90.0


GRIP_SLICE, GRIP_COUPON, GRIP_MOUNT = g_open(10.0), g_open(10.0), g_open(SP.MOUNT_D)
GRIP_STOP = g_open(STOP["d"])
OPEN_SMALL, OPEN_MOUNT = g_open(30.0), g_open(52.0)


# ================================================================================================= our parts
def _cq(shape, tol=0.25):
    return lab.to_mesh(shape.val() if hasattr(shape, "val") else shape, tol, 0.15)


def caddy_mesh():
    import cadquery as cq
    p = CADDY
    blk = cq.Workplane("XY").box(p["x1"] - p["x0"], p["w"], p["h"]).edges("|Z").fillet(6).translate(
        ((p["x0"] + p["x1"]) / 2, p["y"], p["h"] / 2))
    marks = None
    for k, x in SEAT.items():                  # a painted outline at each seat (0.3 mm high)
        if k in ("stopper", "puck"):
            m = cq.Workplane("XY").circle(21.5).circle(20.5).extrude(0.3)
        else:
            m = cq.Workplane("XY").rect(16, 12).rect(14, 10).extrude(0.3)
        m = m.translate((x, p["y"], p["h"]))
        marks = m if marks is None else marks.union(m)
    return _cq(blk), _cq(marks)


def rest_mesh():
    import cadquery as cq
    p = REST
    blk = cq.Workplane("XY").circle(p["d"] / 2).extrude(p["base"])
    for a in p["pins"]:
        r = math.radians(a)
        blk = blk.union(cq.Workplane("XY").circle(p["pin_d"] / 2).extrude(p["pin_h"]).translate(
            (p["pin_r"] * math.cos(r), p["pin_r"] * math.sin(r), p["base"])))
    return _cq(blk)


def holder_mesh():
    """The PX500's 6-position holder as we use it: LECO's disc, plus a handling tab and, at our two pockets, slots
    for the fingertips along the radius (our additions). Frame: centre of the face side, z to its back."""
    import cadquery as cq
    p = HOLDER
    disc = cq.Workplane("XY").circle(p["d"] / 2).extrude(p["t"])
    for i in range(6):
        a = math.radians(30 + 60 * i)
        # stepped bore: the mount's diameter up to the mount's back (7 mm in), then a 5 mm ledge with the piston's
        # aperture. A mount rests on that ledge when the holder is carried face up; nothing clamps it (no set screw)
        c = (p["r"] * math.cos(a), p["r"] * math.sin(a))
        disc = disc.cut(cq.Workplane("XY").circle(SP.MOUNT_D / 2 + 0.4).extrude(p["t"] - 5.0 + 1)
                        .translate((c[0], c[1], -1)))
        disc = disc.cut(cq.Workplane("XY").circle(RP.PIST_D / 2 + 2).extrude(p["t"] + 2).translate((c[0], c[1], -1)))
    for ang in (POCKET_STEEL, POCKET_HOT):
        a = math.radians(ang)
        for r0, r1 in ((p["r"] - 32.0, p["r"] - 12.0), (p["r"] + 12.0, p["r"] + 34.0)):
            rc = (r0 + r1) / 2
            slot = cq.Workplane("XY").box(r1 - r0, 30.0, p["t"] + 4).rotate((0, 0, 0), (0, 0, 1), ang) \
                .translate((rc * math.cos(a), rc * math.sin(a), p["t"] / 2))
            disc = disc.cut(slot)
    tab = cq.Workplane("XY").box(p["tab_w"], p["tab_l"] + 10, p["t"]).translate(
        (0, -(p["d"] / 2 + p["tab_l"] / 2 - 5), p["t"] / 2))
    return _cq(disc.union(tab))


def stopper_meshes():
    """The MX400's stopper, as the lab's: steel, its green marble end up. Frame: its foot."""
    body = pv.Cylinder(center=(0, 0, (STOP["h"] - 2) / 2), direction=(0, 0, 1), radius=STOP["d"] / 2,
                       height=STOP["h"] - 2, resolution=64).triangulate()
    top = pv.Cylinder(center=(0, 0, STOP["h"] - 1), direction=(0, 0, 1), radius=STOP["d"] / 2, height=2,
                      resolution=64).triangulate()
    return {"steel": (body, (0.74, 0.75, 0.78), 0.6), "green end": (top, (0.16, 0.55, 0.32), 0.4)}


def box_mesh(sx, sy, sz):
    return pv.Box(bounds=(-sx / 2, sx / 2, -sy / 2, sy / 2, 0, sz)).triangulate()


def mount_in_holder(ang: float) -> np.ndarray:
    """A 1.5 in mount (r8_specimens frame: foot at z = 0, face at FACE_Z) seated in the holder's pocket at `ang`, its
    face HOLDER['below'] proud of the face side (towards the platen), the holder's frame."""
    a = math.radians(ang)
    return T((HOLDER["r"] * math.cos(a), HOLDER["r"] * math.sin(a), SP.FACE_Z - HOLDER["below"])) @ \
        R((1, 0, 0), 180.0)


def rest_matrix(face_up: bool) -> np.ndarray:
    """The holder on its rest (rest frame): face down, its face side on the pins; or face up, its back on them. The
    tab points along the rest's -y (the MiR's back), as in round 7."""
    z = REST["base"] + REST["pin_h"]
    if face_up:
        return T((0, 0, z + HOLDER["t"])) @ R((0, 1, 0), 180.0)
    return T((0, 0, z))


def tab_grasp() -> np.ndarray:
    """The grasp point on the holder's tab, the holder's frame: level, pointing at the disc's centre (+y), the fingers
    across the tab (along x)."""
    M = np.eye(4)
    M[:3, 0] = (1, 0, 0)
    M[:3, 2] = (0, 1, 0)
    M[:3, 1] = np.cross(M[:3, 2], M[:3, 0])
    M[:3, 3] = (0, -(HOLDER["d"] / 2 + HOLDER["tab_l"] - 22.0), HOLDER["t"] / 2)
    return M


GRIP_TAB = g_open(HOLDER["tab_w"])


# ================================================================================================= the scene
def status(sc, **kv):
    rows = dict(getattr(sc, "_rows", {}))
    rows.update(kv)
    sc._rows = rows
    sc.gauges = [(k, v) for k, v in rows.items() if v]


def rig_of(rigs, key):
    for k, r in rigs.items():
        if k.split("_", 1)[1] == key:
            return r
    raise KeyError(key)


def show_props(sc, rig, pieces):
    """setup_lab hides an instrument's props; the chapter runs them: put them back under the rig's control."""
    for pc in pieces:
        names = sc.members(f"{rig.prefix}{pc}")
        rig.names[pc] = names
        for n in names:
            sc.alpha[n] = 1.0
    rig.apply()


def hide_props(sc, rig, pieces):
    for pc in pieces:
        for n in list(rig.names.get(pc, [])) + sc.members(f"{rig.prefix}{pc}"):
            sc.alpha[n] = 0.0
        rig.names[pc] = []


def add_group(sc, g, parts, parent=None, M=None):
    for nm, (mesh, col, spec) in parts.items():
        sc.add(f"{g}/{nm}", mesh, col, g, specular=spec)
    if parent is not None:
        sc.parent[g] = parent
    sc.gmat[g] = np.eye(4) if M is None else M
    return g


def set_alpha(sc, g, a):
    for n in sc.members(g):
        sc.alpha[n] = a


def cam_at(target, off, look=(0.0, 0.0, 0.0)):
    t = np.asarray(target, float)
    return [tuple(t + np.asarray(off, float)), tuple(t + np.asarray(look, float)), (0, 0, 1)]


def build():
    import setup_lab as SL
    data = lab.meshes()
    idata = SL.load_all()
    sc, L, F, items, rigs, units, util, ulabel, vp = SL.build(data, idata, name=NAME, title=TITLE)
    sc.gif = not (PREVIEW or scene.AUDIT)
    SL.add_bay_cams(sc)
    u = units[0]
    L.robot = u.robot
    L.unit = getattr(L, "unit", {})
    L.skin(1.0)(1.0)
    L.show_gauges = False
    L.apply_state()
    return sc, L, F, rigs, u


def movie():
    import setup_lab as SL
    import warehouse as W
    global X_CNC
    X_CNC = SL.X2 + 560.0
    sc, L, F, rigs, u = build()
    rb = u.robot
    cab = f"{u.name}_cab"
    DOCK_Y = W.DOCK_N
    PARK = np.radians(A.PARK_DEG)
    pol, press, mag, cnc = (rig_of(rigs, k) for k in ("polisher", "mount_press", "disc_magazine", "cnc"))
    # the machines' own props that we run, and the ones the arm replaces with ours
    hide_props(sc, pol, ("holder",))
    show_props(sc, pol, ("water", "powder", "pistons"))
    pol.v.update(water=0.0, powder=0.0, pistons=0.0)
    pol.apply()
    hide_props(sc, press, ("specimen", "stopper"))
    show_props(sc, press, ("charge", "mount", "glow", "pour"))
    for pc, v in (("charge", 0.0), ("mount", 0.0), ("glow", 0.0), ("pour", 0.0)):
        press.v[pc] = v
    press.apply()
    hide_props(sc, cnc, ("carrier", "part", "stock"))
    for n in sc.members(f"{u.name}") + sc.members(cab):
        if n.endswith("/holder"):
            sc.alpha[n] = 0.0                  # the MiR's own buffer block: the caddy and the rest are there now
    # the discs: our own groups (the arm carries them), at home in the magazine
    G = RP.px_geometry()
    m_off = np.array([G["mag"][0], G["mag"][1], 0.0])
    discs = {}
    for kind in RP.GRITS:
        g = f"pd_{kind}"
        for nm, (solid, mat) in RP.disc_solids(kind).items():
            r_, g_, b_, op, spec = RP.MATERIALS.get(mat) or lab.MATS.get(mat) or RP.I.MATERIALS[mat]
            sc.add(f"{g}/{nm}", _cq(solid, 0.3), (r_, g_, b_), g, opacity=op, specular=spec)
        sc.parent[g] = f"{mag.prefix}body"
        sc.gmat[g] = T(RP.disc_home(RP.GRITS.index(kind))[:3, 3] - m_off)
        discs[kind] = g
    # ours on the MiR: the caddy and the holder's rest; on them the parts
    cm, marks = caddy_mesh()
    add_group(sc, "p_caddy", {"caddy": (cm, (0.94, 0.94, 0.92), 0.25), "seats": (marks, (0.30, 0.32, 0.36), 0.2)},
              cab, T((0, 0, CAB_TOP)))
    add_group(sc, "p_rest", {"rest": (rest_mesh(), (0.94, 0.94, 0.92), 0.25)}, cab,
              T((REST_AT[0], REST_AT[1], CAB_TOP)))
    add_group(sc, "p_holder", {"holder": (holder_mesh(), (0.72, 0.73, 0.75), 0.75)}, "p_rest", rest_matrix(True))
    seat_z = CADDY["h"]

    def seat(k):
        return T((SEAT[k], CADDY["y"], seat_z))
    add_group(sc, "p_stopper", stopper_meshes(), "p_caddy", seat("stopper"))
    stl = SP.steel_mount("seated")
    add_group(sc, "p_steel", {"puck": stl["puck"], "screw": stl["screw"]}, "p_caddy", seat("puck"))
    add_group(sc, "p_slice", {"slice": (box_mesh(10.0, 10.0, SP.STEEL["as_cut"]), (0.47, 0.48, 0.50), 0.1)},
              "p_caddy", seat("slice"))
    add_group(sc, "p_coupon", {"coupon": (box_mesh(*SP.HOT["coupon"]), (0.47, 0.48, 0.50), 0.1)}, "p_caddy",
              seat("coupon") @ R((0, 0, 1), 90.0))
    # the steel mount after the CNC (the slice faced flush) and after polishing; the hot mount pressed and polished
    add_group(sc, "p_steel_faced", {"slice": SP.steel_mount("ground")["slice"]}, "p_steel")
    add_group(sc, "p_steel_pol", {"slice": SP.steel_mount("polished")["slice"]}, "p_steel")
    set_alpha(sc, "p_steel_faced", 0.0)
    set_alpha(sc, "p_steel_pol", 0.0)
    add_group(sc, "p_hot", SP.hot_mount("pressed"))
    add_group(sc, "p_hot_pol", SP.hot_mount("polished"), "p_hot")
    set_alpha(sc, "p_hot", 0.0)
    set_alpha(sc, "p_hot_pol", 0.0)

    def mir_at(x):
        u.set((x, DOCK_Y, 0.0))
        if rb.held is not None:
            rb.set()

    def drive(x1):
        x0 = u.pose[0]

        def up(e):
            mir_at(x0 + (x1 - x0) * P.ramp_frac(P.unease(e), x1 - x0, MIR_V))
        return up, max(1.4, P.ramp_secs(x1 - x0, MIR_V))
    mir_at(X_CNC)
    rb.set(PARK)
    sc.apply()
    if os.environ.get("PREP_PROBE"):
        return probe(sc, L, rigs, u, rb, discs, mir_at)

    # ------------------------------------------------------------------ the arm's moves
    st = {"lbl": "6/7", "cap": ""}

    def go(Tw=None, q=None, secs=1.5, cam=None, grip=None, extra=None, hold=0.05, labels=()):
        f = rb.joint_to(Tw=Tw) if Tw is not None else rb.joint_to(q)
        sc.step(st["lbl"], st["cap"], secs, RB.both(f, rb.grip_to(grip) if grip is not None else None, extra),
                hold=hold, cam_to=cam, labels=labels)

    def lin(Tw, secs=0.7, extra=None, hold=0.05, cam=None):
        sc.step(st["lbl"], st["cap"], secs, RB.both(rb.line_to(Tw), extra), hold=hold, cam_to=cam)

    def grip(c, secs=0.4):
        sc.step(st["lbl"], st["cap"], secs, rb.grip_to(c), hold=0.05)

    def park(secs=1.4, cam=None, extra=None):
        go(q=PARK, secs=secs, cam=cam, extra=extra)

    def sh(Tw, d):
        M = Tw.copy()
        M[:3, 3] = M[:3, 3] + np.asarray(d, float)
        return M

    def along(Tw, dist):
        return sh(Tw, Tw[:3, 2] * dist)

    def foot(g):
        return sc.world(g)[:3, 3]

    def pick(g, z_foot, c, spin=0.0, f=1.0, above=70.0, cam=None, at=None):
        """Down onto part g (its foot at world z_foot), the pads' tips 1 mm over it; grasp; up."""
        p = np.array(foot(g) if at is None else at, float)
        Tg = A.down((p[0], p[1], z_foot + DOWN_TIP), spin=spin)
        go(sh(Tg, (0, 0, above)), secs=1.5 * f, grip=min(c, OPEN_SMALL) if c > 0.75 else OPEN_MOUNT, cam=cam)
        lin(Tg, 0.7 * f)
        grip(c, 0.4 * f)
        rb.grasp(g)
        lin(sh(Tg, (0, 0, above)), 0.6 * f)

    def place(g, at, z_foot, parent, spin=0.0, f=1.0, above=70.0, cam=None, open_to=None, secs=1.6):
        """Part g down with its foot at world z_foot over `at` (x, y); let go to `parent`; up."""
        Tg = A.down((at[0], at[1], z_foot + DOWN_TIP), spin=spin)
        go(sh(Tg, (0, 0, above)), secs=secs * f, cam=cam)
        lin(Tg, 0.8 * f)
        grip(open_to if open_to is not None else max(0.0, rb.close - 0.2), 0.4 * f)
        rb.release(parent)
        lin(sh(Tg, (0, 0, above)), 0.6 * f)

    def push(g, dz, f=1.0, spin=0.0):
        """Close the fingers over part g and press it dz mm down (into a pocket or a mold's bore)."""
        top = sc.world(g) @ np.r_[0, 0, 0, 1.0]
        pts = sc.world(g)[:3, 3]
        Tt = A.down((pts[0], pts[1], top[2] + ztop[g] + 19.6), spin=spin)
        go(sh(Tt, (0, 0, 40)), secs=1.0 * f, grip=1.0)
        lin(Tt, 0.5 * f)
        rb.grasp(g)
        lin(sh(Tt, (0, 0, -dz)), 0.9 * f)
        return Tt

    ztop = {"p_slice": SP.STEEL["as_cut"], "p_stopper": STOP["h"]}

    # ------------------------------------------------------------------ 0. the plan, the sectioning
    sc.cam = list(CAM_LAB)
    status(sc, Build="AlSi10Mg, chapter 5's", Coupon="to cut", Slice="to cut")
    st["cap"] = ("Chapter 6, sample prep. Chapter 5's AlSi10Mg build gives chapter 7 two specimens: a coupon "
                 "hot-mounted in conductive phenolic (SEM/EDS, micro-Vickers), and a slice set in a steel mount "
                 "(nanoindentation and PIP: nothing soft under the sample).")
    sc.step(st["lbl"], st["cap"], 4.5, None, hold=1.0)
    edm = F.where.get("wire_edm") if hasattr(F, "where") else None
    ex = 6600.0 if edm is None else float(edm[0])
    ey = W.Y_FACE_S
    cam_edm = [(ex + 2600, ey + 3300, 2600), (ex, ey - 900, 1100), (0, 0, 1)]
    st["lbl"] = "Section"
    st["cap"] = ("Sectioning, on the wire EDM on the floor (chapter 5's machine): a 14 x 10 x 6 mm coupon and a "
                 "10 x 10 x 6 mm slice, cut from the build with no cutting force, so no saw burr, only a thin "
                 "recast layer. The lab's SOP cuts with a diamond saw instead (step 1).")
    sc.step(st["lbl"], st["cap"], 3.5, None, cam_to=cam_edm, hold=2.0)
    status(sc, Coupon="cut, 14 x 10 x 6 mm", Slice="cut, 10 x 10 x 6 mm")

    # ------------------------------------------------------------------ 1. the steel mount, on the MiR
    def cam_caddy():
        c = (sc.world("p_caddy") @ np.r_[(CADDY["x0"] + CADDY["x1"]) / 2, CADDY["y"], CADDY["h"], 1.0])[:3]
        return cam_at(c, (420, -760, 560), (0, 40, 0)), c

    def cam_rest():
        """From the MiR's back left, so the arm, reaching from its base, stays behind the rest."""
        return cam_at(sc.world("p_rest")[:3, 3], (-640, -560, 560), (40, 30, 20))
    cam_cad, cad = cam_caddy()
    st["lbl"] = "Steel mount"
    st["cap"] = ("At Shuttle 2, the pieces on the MiR's caddy (ours): the slice, the coupon, a 1.5 in steel puck "
                 "and the press's stopper. Behind them, the polisher's 6-position holder on its rest.")
    sc.step(st["lbl"], st["cap"], 3.0, None, cam_to=cam_cad, hold=1.2,
            labels=[("slice", tuple(foot("p_slice") + (0, 0, 10)), (0.86, 0.30)),
                    ("coupon", tuple(foot("p_coupon") + (0, 0, 10)), (0.70, 0.18)),
                    ("steel puck", tuple(foot("p_steel") + (0, 0, 24)), (0.42, 0.16)),
                    ("stopper", tuple(foot("p_stopper") + (0, 0, 28)), (0.20, 0.22)),
                    ("6-position holder", tuple(sc.world("p_holder")[:3, 3]), (0.10, 0.50))])
    st["cap"] = ("The slice into the puck's pocket, a 10.1 mm square, 5.6 deep: the fingers let go in its mouth, then "
                 "press it home closed. A ball plunger in the wall holds it; it stands 0.4 mm proud.")
    status(sc, Arm="the slice into the steel puck")
    pick("p_slice", CAB_TOP + seat_z, GRIP_SLICE)
    pk = sc.world("p_steel") @ np.r_[0, 0, SP.FACE_Z, 1.0]
    place("p_slice", pk[:2], pk[2], "p_steel", open_to=OPEN_SMALL)
    Tt = push("p_slice", SP.STEEL["slice"][2])
    rb.release("p_steel")
    lin(sh(Tt, (0, 0, 40)), 0.5)
    park(1.4)
    status(sc, Slice="in the steel puck, 0.4 mm proud", Arm="parked")

    # ------------------------------------------------------------------ 2. faced on the Carvera (tray M, Shuttle 2)
    st["lbl"] = "CNC"
    st["cap"] = "Tray M comes to Shuttle 2's opening: the Makera Carvera desktop CNC."
    L.fetch("M", st["lbl"], st["cap"], fast=0.45, cam=cam_at(cad, (900, -2300, 1500), (300, 600, 300)), hold=0.2)
    G2 = RP.cnc_puck_geometry()
    cw = sc.world(f"{cnc.prefix}body")
    vise = (cw @ np.r_[G2["x"], G2["y"], G2["z_base"], 1.0])[:3]
    cam_cnc = cam_at(vise, (430, -900, 560), (0, 40, 40))
    acts = cnc.inst.actions
    st["cap"] = "The Carvera's lid opens (its actuator is ours)."
    sc.step(st["lbl"], st["cap"], 1.6, cnc.move(acts[0][2]), cam_to=cam_cnc, hold=0.2)
    st["cap"] = ("The arm sets the steel mount on the parallels of the vise (ours); the fingers close along x, the "
                 "jaws along y.")
    status(sc, Arm="the steel mount into the vise")
    pick("p_steel", CAB_TOP + seat_z, GRIP_MOUNT, cam=cam_cad)
    place("p_steel", vise[:2], vise[2], f"{cnc.prefix}body", open_to=OPEN_MOUNT, cam=cam_cnc, secs=2.2)
    park(1.6, cam=cam_cnc)
    status(sc, Arm="parked")
    st["cap"] = "Clamped, the lid shut, a 6 mm end mill from the tool changer."
    sc.step(st["lbl"], st["cap"], 2.6, cnc.move(acts[2][2]), hold=0.2)
    st["cap"] = ("The slice faced flush with the puck: its 0.4 mm and the EDM's recast layer off, the face parallel "
                 "to the puck's base, as nanoindentation and PIP need. The CNC's job in this route: the printed "
                 "build's own slice.")

    def face_skin(e):
        cnc.move(acts[3][2])(e)
        set_alpha(sc, "p_steel_faced", min(1.0, e * 1.5))
        a = max(0.0, 1.0 - e * 1.5)
        for n in sc.members("p_slice"):
            sc.alpha[n] = a
    sc.step(st["lbl"], st["cap"], 4.6, face_skin, hold=0.4)
    st["cap"] = "The end mill back in the rack; the lid opens and the vise lets go."
    sc.step(st["lbl"], st["cap"], 2.4, cnc.move(acts[4][2]), hold=0.2)
    status(sc, Slice="faced flush, in the steel mount")

    # ------------------------------------------------------------------ 3. into the holder, face up; the holder over
    st["lbl"] = "Holder"
    hw = sc.world("p_holder")
    st["cap"] = ("Into the holder, face up: its pocket has slots for the fingertips (ours). The holder's six pockets "
                 "take 1.5 in mounts, which just sit in them: no set screw, nothing clamps them. A ledge at the back of each "
                 "bore stops the mount.")
    status(sc, Arm="the steel mount into the holder")
    pick("p_steel", vise[2], GRIP_MOUNT, cam=cam_cnc)
    Mh = hw @ R((0, 0, 1), 0.0) @ mount_in_holder(POCKET_STEEL)
    # the holder lies face up: the mount's foot is its lowest point, the face up
    fz = min((Mh @ np.r_[0, 0, 0, 1.0])[2], (Mh @ np.r_[0, 0, SP.FACE_Z, 1.0])[2])
    ctr = Mh[:3, 3]
    ang = math.degrees(math.atan2(ctr[1] - hw[1, 3], ctr[0] - hw[0, 3]))
    place("p_steel", ctr[:2], fz, "p_holder", spin=-ang, open_to=OPEN_MOUNT, cam=cam_rest(), secs=2.4)
    park(1.4)
    status(sc, Arm="parked", Holder="face up, the steel mount in it")
    L.store("M", st["lbl"], "Tray M goes back to its slot.", fast=0.45, hold=0.1)
    st["cap"] = ("The arm turns the holder over, by a tab (ours): the steel mount face down now, as the polisher needs "
                 "it. Free in its hole, it is kept from dropping by a light O-ring grip in the bore (assumed: LECO "
                 "publishes none), and the holder stays level.")
    Tg = sc.world("p_holder") @ tab_grasp()
    go(along(Tg, -110), secs=1.6, grip=g_open(44.0), cam=cam_rest())
    lin(Tg, 0.7)
    grip(GRIP_TAB)
    rb.grasp("p_holder")
    lift = sh(Tg, (0, 0, 110))
    lin(lift, 0.8)
    q_up = rb.q.copy()
    q_flip = q_up.copy()
    q_flip[5] += math.pi if q_up[5] < 0 else -math.pi
    go(q=q_flip, secs=1.6)
    Tdown = sc.world("p_rest") @ rest_matrix(False) @ tab_grasp()
    lin(sh(Tdown, (0, 0, 110)), 0.5)
    lin(Tdown, 0.8)
    grip(g_open(44.0))
    rb.release("p_rest")
    lin(along(Tdown, -110), 0.6)
    park(1.4)
    status(sc, Arm="parked", Holder="face down, the steel mount in it")

    # ------------------------------------------------------------------ 4. to Shuttle 1: the MX400 (tray F)
    st["lbl"] = "Mount"
    st["cap"] = "The MiR drives to Shuttle 1, stopping in front of tray F's left end."
    upd, secs = drive(X_PRESS)
    sc.step(st["lbl"], st["cap"], secs, upd, cam_to=[(-2600, -6900, 3100), (-300, -1400, 1000), (0, 0, 1)],
            hold=0.1)
    st["cap"] = "Tray F comes to Shuttle 1's opening: the LECO MX400 press, the PX500 and its disc magazine."
    L.fetch("F", st["lbl"], st["cap"], fast=0.45, hold=0.3)
    pw = sc.world(f"{press.prefix}body")
    gm = RP.mx_geometry()
    mold = (pw @ np.r_[gm["mx"], gm["my"], gm["top"], 1.0])[:3]
    cam_mx = cam_at(mold, (-150, -1300, 450), (40, 0, -30))     # from the front left: the arm comes from the right
    pr = press.inst.actions
    st["cap"] = "Hot mounting, as in the lab's own MX400 video: the closure swings off the 1.5 in mold; ram up."
    sc.step(st["lbl"], st["cap"], 1.6, press.move({"closure": (0.0, 1.0)}), cam_to=cam_mx, hold=0.1)
    sc.step(st["lbl"], st["cap"], 1.2, press.move({"ram": (0.0, 1.0)}), hold=0.2)
    st["cap"] = "The coupon goes on the ram, face down: the face to be polished."
    status(sc, Arm="the coupon onto the ram")
    pick("p_coupon", CAB_TOP + seat_z, GRIP_COUPON, cam=cam_caddy()[0])
    place("p_coupon", mold[:2], mold[2], f"{press.prefix}ram", open_to=OPEN_SMALL, cam=cam_mx, secs=2.2)
    go(sh(A.down(tuple(mold), 0.0), (0, 0, 200)), secs=1.0)
    st["cap"] = "Ram down, into the mold."
    sc.step(st["lbl"], st["cap"], 1.2, press.move({"ram": (1.0, 0.0)}), hold=0.1)
    st["cap"] = ("Conductive phenolic (carbon-filled: the SEM's path to ground), the SOP's 3/4 scoop, from a doser "
                 "(ours) where the video pours it by hand.")
    sc.step(st["lbl"], st["cap"], 2.2, press.move(pr[5][2]), hold=0.1)
    sc.step(st["lbl"], st["cap"], 0.9, press.move(pr[6][2]), hold=0.1)
    st["cap"] = ("The stopper, green end up as the press's label says: set in the mold's mouth, then pressed down "
                 "onto the compound by the closed fingers (the SOP: an airtight fit).")
    status(sc, Arm="the stopper into the mold")
    pick("p_stopper", CAB_TOP + seat_z, GRIP_STOP, cam=cam_caddy()[0])
    place("p_stopper", mold[:2], mold[2], f"{press.prefix}body", open_to=OPEN_MOUNT, cam=cam_mx, secs=2.2)
    Tt = push("p_stopper", gm["top"] - gm["stopper_z"])
    rb.release(f"{press.prefix}body")
    lin(sh(Tt, (0, 0, 60)), 0.5)
    park(1.4)
    status(sc, Arm="parked")
    st["cap"] = "The closure swung back and locked."
    sc.step(st["lbl"], st["cap"], 1.2, press.move({"closure": (1.0, 0.0)}), hold=0.1)
    st["cap"] = ("Heating under pressure at the lab's settings on the screen: 300, 4.2, 100, 10:00 (300 F is 149 C, "
                 "4.2 thousand psi is 29 MPa: our reading of the units). The ram presses the loose compound solid.")
    sc.step(st["lbl"], st["cap"], 3.0, press.move(pr[8][2]), hold=0.1)
    st["cap"] = "Cooling, then Complete."
    sc.step(st["lbl"], st["cap"], 1.4, press.move(pr[9][2]), hold=0.1)
    # out: the stopper rides up on the mount
    rb.reparent("p_stopper", f"{press.prefix}ram")
    st["cap"] = "Closure off; the ram pushes the mount up out of the mold, the stopper on top."
    sc.step(st["lbl"], st["cap"], 2.2, press.move({"closure": (0.0, 1.0), "ram": (RP.RAM_PRESSED, 1.0)}), hold=0.2)
    # the press's mount and our coupon become one part, the pressed hot mount (r8_specimens), face down on the ram
    ram_w = sc.world(f"{press.prefix}ram")
    Mhot = np.linalg.inv(ram_w) @ T(tuple(mold + (0, 0, SP.FACE_Z + SP.HOT["skin"]))) @ R((1, 0, 0), 180.0)
    sc.parent["p_hot"] = f"{press.prefix}ram"
    sc.gmat["p_hot"] = Mhot
    set_alpha(sc, "p_hot", 1.0)
    set_alpha(sc, "p_hot_pol", 0.0)
    hide_props(sc, press, ("mount",))
    set_alpha(sc, "p_coupon", 0.0)
    st["cap"] = "The stopper back on the caddy."
    status(sc, Coupon="hot-mounted, 1.5 in conductive phenolic", Arm="the stopper off")
    pick("p_stopper", mold[2] + SP.FACE_Z + SP.HOT["skin"], GRIP_STOP, cam=cam_mx)
    sp_ = (sc.world("p_caddy") @ seat("stopper"))[:3, 3]
    place("p_stopper", sp_[:2], sp_[2], "p_caddy", open_to=OPEN_MOUNT, cam=cam_mx)
    st["cap"] = ("The mount into the holder, face down, beside the steel mount. The SOP takes the compound's skin "
                 "off on a belt sander (step 3); here the 320 paper does it.")
    status(sc, Arm="the hot mount into the holder")
    pick("p_hot", mold[2], GRIP_MOUNT, cam=cam_mx)
    hw = sc.world("p_holder")
    Mh = hw @ mount_in_holder(POCKET_HOT)
    fz = min((Mh @ np.r_[0, 0, 0, 1.0])[2], (Mh @ np.r_[0, 0, SP.FACE_Z, 1.0])[2])
    ctr = Mh[:3, 3]
    ang = math.degrees(math.atan2(ctr[1] - hw[1, 3], ctr[0] - hw[0, 3]))
    place("p_hot", ctr[:2], fz, "p_holder", spin=-ang, open_to=OPEN_MOUNT, cam=cam_rest(), secs=2.4)
    park(1.4)
    status(sc, Arm="parked", Holder="face down, both mounts in it")
    st["cap"] = "The press tidied: closure back, ram down."
    sc.step(st["lbl"], st["cap"], 1.2, press.move({"closure": (1.0, 0.0), "ram": (1.0, 0.0)}), cam_to=cam_mx,
            hold=0.1)

    # ------------------------------------------------------------------ 5. the PX500
    st["lbl"] = "Polish"
    upd, secs = drive(X_POL)
    st["cap"] = "To the PX500: the MiR moves along to Shuttle 1's dock."
    pw2 = sc.world(f"{pol.prefix}body")
    plat = (pw2 @ np.r_[G["bx"], G["by"], G["disc_z"], 1.0])[:3]
    mw = sc.world(f"{mag.prefix}body")
    mid = (plat + mw[:3, 3]) / 2
    cam_pol = cam_at(mid + (0, -200, 300), (300, -2600, 1300))
    sc.step(st["lbl"], st["cap"], secs, upd, cam_to=cam_pol, hold=0.1)
    up_ = -RP.LIFT / (pol.inst.joints["head"].vec[2] * -1.0)
    st["cap"] = ("Grinding and polishing on the lab's PX500. First the holder: the head lifts clear (our extra "
                 "lift), and the arm fits the holder onto the spindle's coupling (assumed), level, from under it.")
    sc.step(st["lbl"], st["cap"], 1.2, pol.move({"head": (0.0, up_)}), hold=0.2)
    p5 = RP.P5
    hz = p5["deck"] + p5["head_up"]
    head_hold = f"{pol.prefix}holder"
    Tg = sc.world("p_holder") @ tab_grasp()
    go(along(Tg, -110), secs=1.6, grip=g_open(44.0))
    lin(Tg, 0.7)
    grip(GRIP_TAB)
    rb.grasp("p_holder")
    lin(sh(Tg, (0, 0, 40)), 0.6)
    lin(sh(along(Tg, -90), (0, 0, 60)), 0.7)
    H_on = sc.world(head_hold) @ T((G["hx"], G["hy"], hz - 120.0))
    T_on = H_on @ tab_grasp()
    go(sh(along(T_on, -260), (0, 0, -4)), secs=2.0, cam=cam_pol)
    lin(sh(T_on, (0, 0, -4)), 1.2)
    lin(T_on, 0.3)
    grip(g_open(44.0))
    rb.release(head_hold)
    lin(along(T_on, -240), 0.9)
    status(sc, Holder="on the PX500's head")
    drop_ = -pol.inst.joints["head"].vec[2]
    hold_dn = H_on[:3, 3] - (0.0, 0.0, drop_ + RP.LIFT)       # the holder's face side, the head down on the disc
    cam_pist = cam_at(hold_dn + (0, 0, 40), (60, -430, 70), look=(0, 0, 0))

    pre_back = 140.0

    def handle_world(group):
        return sc.world(group) @ RP.handle_tcp()
    on_platen = f"{pol.prefix}platen"
    out_pol, out_mag, lift_pol = 470.0, 360.0, 62.0

    def to_platen(kind, f=1.0, cap_=""):
        g_ = discs[kind]
        Hh = handle_world(g_)
        st["cap"] = cap_
        go(sh(Hh, (0, -pre_back, 0)), secs=1.6 * f, grip=0.0)
        lin(Hh, 0.7 * f)
        grip(RP.GRIP_HANDLE, 0.4 * f)
        rb.grasp(g_)
        lin(sh(Hh, (0, 0, 8)), 0.4 * f)
        lin(sh(Hh, (0, -out_mag, 8)), 1.0 * f)
        Hp = T(plat) @ RP.handle_tcp()
        lin(sh(Hp, (0, -out_pol, lift_pol)), 2.0 * f)
        lin(sh(Hp, (0, 0, lift_pol)), 1.2 * f)
        lin(Hp, 0.6 * f)
        grip(0.0, 0.4 * f)
        rb.release(on_platen)
        lin(sh(Hp, (0, -pre_back, 0)), 0.6 * f)

    def to_magazine(kind, f=1.0, cap_=""):
        g_ = discs[kind]
        Hh = handle_world(g_)
        i = RP.GRITS.index(kind)
        Hm = mw @ T(RP.disc_home(i)[:3, 3] - m_off) @ RP.handle_tcp()
        st["cap"] = cap_
        go(sh(Hh, (0, -pre_back, 0)), secs=1.2 * f, grip=0.0)
        lin(Hh, 0.6 * f)
        grip(RP.GRIP_HANDLE, 0.4 * f)
        rb.grasp(g_)
        lin(sh(Hh, (0, 0, lift_pol)), 0.6 * f)
        lin(sh(Hh, (0, -out_pol, lift_pol)), 1.2 * f)
        lin(sh(Hm, (0, -out_mag, 8)), 2.0 * f)
        lin(sh(Hm, (0, 0, 8)), 1.0 * f)
        lin(Hm, 0.4 * f)
        grip(0.0, 0.4 * f)
        rb.release(f"{mag.prefix}body")
        lin(sh(Hm, (0, -pre_back, 0)), 0.6 * f)

    plat_v = [0.0, 0.0]
    H_TURN = 360.0 / abs(pol.inst.joints["holder"].deg)     # the holder's joint value for one whole turn: each grind
    #                                                         ends with its tab to the front again, for the arm

    def grind(cap_, secs_, cloth=False, f=1.0, rinse=True):
        st["cap"] = cap_
        a, b = plat_v[0], plat_v[0] + 1.0
        ha, hb = plat_v[1], plat_v[1] + H_TURN
        sc.step(st["lbl"], cap_, 0.8 * f, pol.move({"head": (up_, 1.0)}), hold=0.0)
        ws = {"powder": (0.0, 1.0)} if cloth else {"water": (0.0, 1.0)}
        sc.step(st["lbl"], cap_ + " The pistons come down onto the mounts' backs.", 0.7 * f,
                pol.move({"pistons": (0.0, 1.0)}), hold=0.0, cam_to=cam_pist)
        sc.step(st["lbl"], cap_, secs_ * f, pol.move({"platen": (a, b), "holder": (ha, hb), "pistons": (1.0, 1.0),
                                                      **ws}), hold=0.0)
        we = {"powder": (1.0, 0.0)} if cloth else {"water": (1.0, 0.0)}
        sc.step(st["lbl"], "Pistons up: the mounts just stand in their holes.", 0.5 * f,
                pol.move({"pistons": (1.0, 0.0)}), hold=0.0)
        sc.step(st["lbl"], cap_, 0.8 * f, pol.move({"head": (1.0, up_), **we}), hold=0.1, cam_to=cam_pol)
        if rinse and not cloth:
            sc.step(st["lbl"], "Head up: the mounts, the holder and the disc rinsed under the spigot before the next "
                    "grit (the SOP, step 4).", 0.9 * f, pol.move({"water": (0.0, 1.0)}), hold=0.1)
            sc.step(st["lbl"], st["cap"], 0.3 * f, pol.move({"water": (1.0, 0.0)}), hold=0.0)
        plat_v[0], plat_v[1] = b, hb

    st["cap"] = ("Why whole discs: changing a SiC paper means prying off its retaining ring, peeling the paper, laying "
                 "a new one flat and pressing the ring back on (the SOP, step 4). No robot has been shown doing that.")
    sc.step(st["lbl"], st["cap"], 1.0, None, hold=3.0)
    st["cap"] = ("The documented automatic route changes whole pre-loaded discs (BAM's RASI cell: a QATM QPOL 250 Bot "
                 "with 16). So each steel disc here carries its own paper or cloth and its own ring; the magnetic "
                 "platen holds it, and the arm moves it by the handle on the ring.")
    sc.step(st["lbl"], st["cap"], 1.0, None, hold=3.4)
    to_platen("320", 1.0, "The 320-grit disc from the bottom shelf of the magazine onto the magnetic platen.")
    status(sc, Disc="320 SiC")
    grind("320 grit with water at the SOP's gentle settings, 35, 30, 150, 30 s; first it takes the compound's skin "
          "off the coupon.", 3.2)
    for prev, nxt in (("320", "400"), ("400", "600"), ("600", "800"), ("800", "1200"), ("1200", "cloth")):
        f = 0.75 if prev == "320" else FAST
        cap_ = (f"Change: the {prev} disc back to its shelf, paper, ring and all; the {nxt} out and onto the platen."
                if prev == "320" else f"{prev} back, {nxt} on (a time-lapse).")
        to_magazine(prev, f, cap_)
        to_platen(nxt, f, cap_)
        status(sc, Disc=f"{nxt} SiC" if nxt != "cloth" else "cloth, 1 um alumina")
        if nxt != "cloth":
            grind(f"{nxt} grit, 30 s, the same settings.", 2.0, f=0.8 if nxt == "400" else 0.6)
    st["cap"] = ("The final polish: 1 um alumina from the PX500's dispenser onto the cloth, no water, 3 min (the SOP, "
                 "step 5).")

    def polished(e):
        on = e > 0.5
        set_alpha(sc, "p_steel_pol", 1.0 if on else 0.0)
        set_alpha(sc, "p_steel_faced", 0.0 if on else 1.0)
        set_alpha(sc, "p_hot_pol", 1.0 if on else 0.0)
        set_alpha(sc, "p_hot", 0.0 if on else 1.0)
    a, b = plat_v[0], plat_v[0] + 1.0
    ha, hb = plat_v[1], plat_v[1] + H_TURN
    sc.step(st["lbl"], st["cap"], 0.8, pol.move({"head": (up_, 1.0)}), hold=0.0)
    sc.step(st["lbl"], st["cap"], 0.7, pol.move({"pistons": (0.0, 1.0)}), hold=0.0)
    sc.step(st["lbl"], st["cap"], 3.6, RB.both(pol.move({"platen": (a, b), "holder": (ha, hb),
                                                         "powder": (0.0, 1.0)}), polished), hold=0.0)
    sc.step(st["lbl"], st["cap"], 0.5, pol.move({"pistons": (1.0, 0.0)}), hold=0.0)
    sc.step(st["lbl"], st["cap"], 0.8, pol.move({"head": (1.0, up_), "powder": (1.0, 0.0)}), hold=0.1)
    status(sc, Coupon="polished, in its hot mount", Slice="polished flush, in the steel mount")

    # ------------------------------------------------------------------ 6. the holder back, face up; what is left
    st["lbl"] = "Done"
    st["cap"] = "The holder off the head and back on the MiR's rest, turned face up on the way."
    status(sc, Arm="the holder back to its rest")
    T_on = sc.world("p_holder") @ tab_grasp()
    go(along(T_on, -240), secs=1.6, grip=g_open(44.0))
    lin(T_on, 0.9)
    grip(GRIP_TAB)
    rb.grasp("p_holder")
    lin(sh(T_on, (0, 0, -4)), 0.3)
    lin(sh(along(T_on, -260), (0, 0, -4)), 1.2)
    T_up = sc.world("p_rest") @ rest_matrix(True) @ tab_grasp()
    go(sh(along(T_up, -90), (0, 0, 60)), secs=2.2)
    lin(sh(T_up, (0, 0, 40)), 0.7)
    lin(T_up, 0.5)
    grip(g_open(44.0))
    rb.release("p_rest")
    lin(along(T_up, -110), 0.7)
    park(1.4)
    status(sc, Arm="parked", Holder="face up on the MiR, both mounts polished")
    rw = sc.world("p_holder")[:3, 3]
    st["cap"] = ("Both specimens polished, face up: the coupon in conductive phenolic, the slice flush in its steel "
                 "puck. The SOP's step 6 follows: ethanol, then an ultrasonic bath (not modelled).")
    sc.step(st["lbl"], st["cap"], 2.4, None, cam_to=cam_at(rw, (260, -330, 300), (0, 20, 0)), hold=2.4, still=True)
    st["cap"] = ("The SOP's step 7 is a final 0.1 um diamond polish on a Buehler VibroMet 2, 1 to 2 hours, checked "
                 "every 30 min: a vibratory bowl, not on a tray here yet. For EDS on Al, 0.1 um is the finish to reach.")
    sc.step(st["lbl"], st["cap"], 1.0, None, hold=4.0)
    st["cap"] = ("Where automating this is hard: re-papering discs, judging the polish (by eye in the SOP), and the "
                 "holder. Buehler's AutoMet heads automate force, speed and time, and its Burst module doses "
                 "suspension, but a person changes the papers.")
    L.store("F", st["lbl"], st["cap"], fast=0.6, hold=1.2)
    st["cap"] = ("UES's Robo-Met.3D (now sold by AV) moves one mounted specimen between polishing, ultrasonic "
                 "cleaning and an inverted microscope, for serial sectioning; it does not cut or mount. Sectioning and "
                 "mounting are what this chapter adds. Next, chapter 7: the MiR takes the holder to the trays.")
    sc.step(st["lbl"], st["cap"], 1.0, None, cam_to=CAM_LAB, hold=4.2)
    return sc.save()


# ================================================================================================= pose probe
def feasible(rb, Tw, close=0.5):
    """(clear IK branches, all IK branches, the fewest hits of any branch) for the arm's grasp point at Tw."""
    import collide
    chk = rb.checker()
    world = chk.snapshot()
    Tb = np.linalg.inv(rb.sc.world(rb.root)) @ Tw
    try:
        qs = collide.ik_all(rb.model, Tb, rb.q)
    except Exception:                       # noqa: BLE001
        qs = []
    res = [chk.collisions(q, close, world, chk.touching(q, close, world)) for q in qs]
    best = min(res, key=len) if res else ["no IK"]
    return sum(1 for h in res if not h), len(qs), [(h[0], h[1], h[2][-28:]) if isinstance(h, tuple) else h
                                                   for h in best[:2]]


def probe(sc, L, rigs, u, rb, discs, mir_at):
    """PREP_PROBE=1: which MiR stops and gripper spins give the chapter's grasps a clear arm. No movie."""
    import setup_lab as SL
    import vlm as V
    pol, press, mag, cnc = (rig_of(rigs, k) for k in ("polisher", "mount_press", "disc_magazine", "cnc"))

    def present(k):
        L.use(L.unit.get(k, 1))
        L.tray[k] = [*V.SLOTS["open"]]
        L.where[k] = "open"
        L.apply_state()
        sc.apply()

    def report(tag, Tw, close=0.5):
        n, m, worst = feasible(rb, Tw, close)
        print(f"PROBE {tag}: {n}/{m} clear" + ("" if n else f"  {worst}"), flush=True)
        return n
    # 1. the caddy and the rest, relative to the MiR (the MiR at X_CNC, nothing presented)
    for k in ("slice", "coupon", "puck", "stopper"):
        for spin in (0.0, 90.0, 180.0, -90.0):
            w = (sc.world("p_caddy") @ np.r_[SEAT[k], CADDY["y"], CADDY["h"] + DOWN_TIP, 1.0])[:3]
            Tg = A.down(tuple(w), spin=spin)
            report(f"caddy {k} spin {spin:.0f} grasp", Tg)
            M = Tg.copy()
            M[2, 3] += 70
            report(f"caddy {k} spin {spin:.0f} above", M)
    for face_up, ang in ((True, POCKET_STEEL), (False, POCKET_HOT)):
        sc.gmat["p_holder"] = rest_matrix(face_up)
        sc.apply()
        hw = sc.world("p_holder")
        Mh = hw @ mount_in_holder(ang)
        fz = min((Mh @ np.r_[0, 0, 0, 1.0])[2], (Mh @ np.r_[0, 0, SP.FACE_Z, 1.0])[2])
        ctr = Mh[:3, 3]
        a = math.degrees(math.atan2(ctr[1] - hw[1, 3], ctr[0] - hw[0, 3]))
        for spin in (-a, 180 - a):
            Tg = A.down((ctr[0], ctr[1], fz + DOWN_TIP), spin=spin)
            report(f"holder face_up={face_up} pocket {ang:.0f} spin {spin:.0f} seat", Tg)
            M = Tg.copy()
            M[2, 3] += 70
            report(f"holder face_up={face_up} pocket {ang:.0f} spin {spin:.0f} above", M)
        Tt = hw @ tab_grasp()
        report(f"holder face_up={face_up} tab", Tt, GRIP_TAB)
        M = Tt.copy()
        M[:3, 3] -= Tt[:3, 2] * 110
        report(f"holder face_up={face_up} tab back 110", M, 0.4)
    sc.gmat["p_holder"] = rest_matrix(True)
    # 2. the Carvera's vise, tray M at Shuttle 2
    present("M")
    G2 = RP.cnc_puck_geometry()
    for lid in (-40.0, -65.0, -80.0):
        cnc.inst.joints["lid"].deg = lid
        cnc.v["lid"] = 1.0
        cnc.apply()
        for dx in (420.0, 560.0, 700.0):
            mir_at(SL.X2 + dx)
            sc.apply()
            vise = (sc.world(f"{cnc.prefix}body") @ np.r_[G2["x"], G2["y"], G2["z_base"] + DOWN_TIP, 1.0])[:3]
            for spin in (0.0, 180.0):
                Tg = A.down(tuple(vise), spin=spin)
                report(f"cnc lid {lid:.0f} mir +{dx:.0f} spin {spin:.0f} seat", Tg)
                M = Tg.copy()
                M[2, 3] += 70
                report(f"cnc lid {lid:.0f} mir +{dx:.0f} spin {spin:.0f} above", M)
    # 3. the MX400, tray F at Shuttle 1: closure off, ram up
    present("F")
    press.v["closure"] = 1.0
    press.v["ram"] = 1.0
    press.apply()
    gm = RP.mx_geometry()
    for x in (-720.0, -800.0, -860.0):
        mir_at(x)
        sc.apply()
        mold = (sc.world(f"{press.prefix}body") @ np.r_[gm["mx"], gm["my"], gm["top"], 1.0])[:3]
        for spin in (0.0, 45.0, 90.0, 135.0, 180.0, -45.0, -90.0, -135.0):
            Tg = A.down((mold[0], mold[1], mold[2] + DOWN_TIP), spin=spin)
            report(f"press mir {x:.0f} spin {spin:.0f} mold", Tg)
            M = Tg.copy()
            M[2, 3] += 70
            report(f"press mir {x:.0f} spin {spin:.0f} above", M)
    # 4. the PX500 and its magazine: head lifted, the disc handles
    up_ = -RP.LIFT / (pol.inst.joints["head"].vec[2] * -1.0)
    pol.v["head"] = up_
    pol.apply()
    G = RP.px_geometry()
    m_off = np.array([G["mag"][0], G["mag"][1], 0.0])
    for x in (0.0, 150.0, 300.0, 450.0):
        mir_at(x)
        sc.apply()
        pw2 = sc.world(f"{pol.prefix}body")
        plat = (pw2 @ np.r_[G["bx"], G["by"], G["disc_z"], 1.0])[:3]
        Hp = T(plat) @ RP.handle_tcp()
        report(f"px mir {x:.0f} platen handle", Hp, RP.GRIP_HANDLE)
        M = Hp.copy()
        M[1, 3] -= 140
        report(f"px mir {x:.0f} platen pre", M, 0.0)
        M = Hp.copy()
        M[1, 3] -= 470
        M[2, 3] += 62
        report(f"px mir {x:.0f} platen out", M, RP.GRIP_HANDLE)
        mw = sc.world(f"{mag.prefix}body")
        for i in range(len(RP.GRITS)):
            Hm = mw @ T(RP.disc_home(i)[:3, 3] - m_off) @ RP.handle_tcp()
            report(f"px mir {x:.0f} magazine shelf {i} handle", Hm, RP.GRIP_HANDLE)
            M = Hm.copy()
            M[1, 3] -= 140
            report(f"px mir {x:.0f} magazine shelf {i} pre", M, 0.0)
            M = Hm.copy()
            M[1, 3] -= 360
            M[2, 3] += 8
            report(f"px mir {x:.0f} magazine shelf {i} out", M, RP.GRIP_HANDLE)
        p5 = RP.P5
        hz = p5["deck"] + p5["head_up"]
        H_on = sc.world(f"{pol.prefix}holder") @ T((G["hx"], G["hy"], hz - 120.0))
        T_on = H_on @ tab_grasp()
        report(f"px mir {x:.0f} holder on head tab", T_on, GRIP_TAB)
        M = T_on.copy()
        M[:3, 3] -= T_on[:3, 2] * 260
        M[2, 3] -= 4
        report(f"px mir {x:.0f} holder on head back 260", M, GRIP_TAB)
    print("PROBE done", flush=True)


if __name__ == "__main__":
    print(movie())
