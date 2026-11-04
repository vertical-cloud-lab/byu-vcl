"""The alloy route, chapter 5: the printed AlSi10Mg build through the characterization trays (#303).

    xvfb-run -a python3 alloy_characterize.py             # -> out/alloy_characterize.gif, out/mp4/alloy_characterize.mp4
    PREVIEW=1 xvfb-run -a python3 alloy_characterize.py   # the last frame of each sub-step -> /tmp/preview_*.png
    ARM_AUDIT=1 xvfb-run -a python3 alloy_characterize.py # no render: every frame collision-checked -> out/collisions/

Chapter 4 (``alloy_workflow.py``) ends with one of the printed bars broken in the Instron 68FM-100. This chapter takes
samples of the same build through trays D, E and F at the VLM's opening, the way the trays would be used: the VLM
brings a tray, the UR10e on its MiR250 loads an instrument, the instrument does its job (its own joints in
``instruments.py``, sped up, with a clock), the arm unloads it, and the tray goes back for the next one.

* **Tray F, the LECO PX500:** a coupon of the build, hot-mounted in a 1.25 in Bakelite mount, is ground and polished.
* **Tray D, the Hitachi TM4000PlusII:** the polished mount is imaged (BSE) and mapped with EDS.
* **Tray E, the KLA iMicro and the Mastersizer 3000:** a grid of nanoindents in the polished face; then a vial of the
  sieved powder the plate was printed from through the Aero S.

Every arm move is a straight line of the grasp point (IK every frame) or a joint move planned round whatever is in the
way (``robot.py``, ``collide.py``). What is assumed (the holders, the slotted pocket, the head's lift for loading) is in
``notes/alloy_characterize.md``.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw

import scene
scene.GIF_FPS = 5                     # a 2-3 minute GIF under 4.9 MB: 5 fps at 640 x 360 (the MP4 keeps every frame)
scene.GIF_SIZE = (640, 360)
from scene import CLEAN, FPS, OUT, PREVIEW, Scene, T, R, S, font  # noqa: E402

import animate as A                   # noqa: E402
import instruments as I               # noqa: E402
import lab                            # noqa: E402
import line                           # noqa: E402
import props as P                     # noqa: E402
import robot as RB                    # noqa: E402
import tour                           # noqa: E402
import vlm as V                       # noqa: E402

NAME = "alloy_characterize"
TITLE = "Vertical cloud lab: the alloy route 5/5, characterization"
HERE = Path(__file__).resolve().parent
SEM_LOCAL = HERE / "out" / "alloy_sem_AlSi10Mg_carbon_adhesive.png"      # chapter 4's real image (DAL figures/sem)
SEM_CREDIT = ["Real data: the lab's AlSi10Mg powder, the powder this",
              "plate was printed from. SEM, 500x, 5 kV, BYU's Apreo,",
              "Gage Erickson, 2 Apr 2026 (byu-vcl#48). Not the TM4000."]

MOUNT_D, MOUNT_H = I.MOUNT_D, 22.0    # the lab's 1.25 in (31.75 mm) Bakelite mounts ("Making Bakelite Polishing Puck")
GRIP_MOUNT = 0.70 + (28.0 - MOUNT_D) / 90.0       # 2F-85 closure on the mount (gap = 28 - 90 (c - 0.70))
GRIP_VIAL = A.GRIP_VIAL
OPEN_NEAR = 0.40                      # opened only to 50 mm, to reach in beside a mount
STUB = dict(d=40.0, h=24.0)           # the SEM's mount holder: a cup for a 1.25 in mount, left in the stage's socket


# ================================================================================================= the scene
class ChScene(Scene):
    """Scene with the result insets drawn over every frame: the SEM image, the indent map, the size distribution,
    and the instrument's clock."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.inset = None             # "sem", "nano", "psd" or None
        self.inset_a = 0.0
        self.clock = None             # (instrument, text) or None
        self._sem = None

    def overlay(self, img, scale, anchors):
        img = super().overlay(img, scale, anchors)
        if CLEAN:
            return img
        if self.inset and self.inset_a > 0.02:
            getattr(self, f"_draw_{self.inset}")(img)
        if self.clock:
            self._draw_clock(img)
        return img

    def _box(self, img, w, h):
        W, H = img.size
        k = W / 1280
        x0, y0 = W - w - int(14 * k), int(52 * k)
        return k, x0, y0

    def _draw_clock(self, img):
        W, H = img.size
        k = W / 1280
        s = max(k, 0.8)
        what, txt = self.clock
        d = ImageDraw.Draw(img, "RGBA")
        f1, f2 = font(13 * s), font(26 * s, bold=True, mono=True)
        w = max(d.textlength(what, font=f1), d.textlength(txt, font=f2)) + 24 * k
        x1, y1 = W - 14 * k, H - 150 * k
        d.rounded_rectangle((x1 - w, y1 - 58 * s, x1, y1), 6 * k, fill=(20, 24, 34, 225))
        d.text((x1 - w + 12 * k, y1 - 54 * s), what, font=f1, fill=(190, 200, 215))
        d.text((x1 - w + 12 * k, y1 - 36 * s), txt, font=f2, fill=(255, 255, 255))

    def _draw_sem(self, img):
        W, H = img.size
        k = W / 1280
        if self._sem is None:
            self._sem = Image.open(SEM_LOCAL).convert("RGB")
        w = int(380 * k)
        h = int(w * self._sem.height / self._sem.width)
        pic = self._sem.resize((w, h), Image.LANCZOS)
        x0, y0 = W - w - int(14 * k), int(52 * k)
        s = max(k, 0.8)
        fc = font(12 * s)
        lh = 15 * s
        box = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(box)
        d.rounded_rectangle((x0 - 6 * k, y0 - 6 * k, x0 + w + 6 * k, y0 + h + 8 * k + len(SEM_CREDIT) * lh),
                            6 * k, fill=(255, 255, 255, 235), outline=(150, 154, 160, 255))
        box.paste(pic, (x0, y0))
        for i, t in enumerate(SEM_CREDIT):
            d.text((x0, y0 + h + 4 * k + i * lh), t, font=fc, fill=(20, 20, 24, 255))
        a = int(255 * self.inset_a)
        box.putalpha(box.getchannel("A").point(lambda v: v * a // 255))
        img.paste(box, (0, 0), box)


def status(sc, **kv):
    rows = dict(sc._rows) if hasattr(sc, "_rows") else {}
    rows.update(kv)
    sc._rows = rows
    sc.gauges = [(k, v) for k, v in rows.items() if v]


def build():
    data = lab.meshes()
    keys = [key for k in ("D", "E", "F") for key, _, _ in line.TRAY_LOADS[k]]
    idata = tour.load(keys)
    sc = ChScene(NAME, TITLE)
    sc.intro = 0.8
    L = A.Lab(sc, data, robot=True)
    L.show_gauges = False
    L.skin(0.0)(1.0)
    rigs = {}
    for k in ("D", "E", "F"):
        line.add_tray(sc, L, k)
        for key, x, y in line.TRAY_LOADS[k]:
            if key not in idata:
                print(f"warning: {key} not built (its meshes are missing); tray {k} without it", file=sys.stderr)
                continue
            inst, ents = idata[key]
            x0, x1, y0, y1, z0, _ = inst.bbox()
            at = T((x - (x0 + x1) / 2, y - (y0 + y1) / 2, V.T_FLOOR - z0))
            rigs[key] = tour.Rig(sc, inst, ents, f"{k}_{key}:", at=at, parent=f"tray_{k}")
            L.eq_groups[k].append(f"{k}_{key}:body")
    # the props the tours move in and out of each instrument (a stub, a sample, a tray of coupons) wait in mid-air
    # in front of it at their start: here the arm brings the samples, so they go, and so do the polisher's holder and
    # the Mastersizer's vial, which are ours
    for key, rig in rigs.items():
        drop = [pc for pc in rig.inst.props if pc in rig.names and rig.inst.joints.get(pc) is not None
                and rig.inst.joints[pc].kind != "fade"]
        drop += [pc for pc in {"polisher": ["holder"], "mastersizer": ["vial"]}.get(key, []) if pc in rig.names]
        for piece in drop:
            for n in rig.names[piece]:
                sc.alpha[n] = 0.0
            rig.names[piece] = []
    for n in L.groups("vial", "vial_powder", "vial_liquid"):       # round 2's vial on tray B
        sc.alpha[n] = 0.0
    sc.alpha["amr/holder"] = 0.0
    L.apply_state()
    return sc, L, rigs, idata


def tray_of(key):
    return next(k for k in ("D", "E", "F") for kk, _, _ in line.TRAY_LOADS[k] if kk == key)


def inst_world(sc, rig, p):
    return (sc.world(f"{rig.prefix}body") @ np.r_[p, 1.0])[:3]


# ================================================================================================= our parts
def _cq_mesh(shape, tol=0.4):
    return lab.to_mesh(shape.val() if hasattr(shape, "val") else shape, tol, 0.15)


HOLDER = dict(d=150.0, t=12.0, r=52.0, tab_w=24.0, tab_l=55.0, below=13.0, above=0.0)
POCKET = 90.0                         # our coupon's pocket in the 6-position holder (deg, holder frame)
MOUNT_H = HOLDER["below"] + HOLDER["t"] + HOLDER["above"]      # 25 mm: 13 proud of the face side, flush at the back
TCP_OUT = 5.0                         # the grasp point 5 mm out from the polished face: the pads hold its top 13 mm
REST = dict(d=160.0, h=20.0, ledge=16.0)             # the holder's rest: a block 20 mm tall, the rim on a ledge 16 up
CADDY = dict(w=124.0, d=56.0, h=P.DECK_H, mount_bore=10.0, vial_bore=P.DECK_DEPTH)
CUP = dict(d=44.0, h=18.0, bore=8.0, dy=-30.0)  # the SEM's mount cup on the stage, 30 mm ahead of its socket, so the
                                                 # wrist clears the SEM's front with the door out
ARM_CADDY = (40.0, -180.0)            # the caddy on the MiR's cabinet (MiR frame), behind the arm, clear of the e-stop
ARM_REST = (-245.0, -165.0)           # the holder rest's post, behind the arm on the left


def holder_parts():
    """The PX500's 6-position holder as we use it: LECO's disc, plus a handling tab and a pocket slotted for the
    fingertips (our additions). Frame: centre of the disc's face side (the side towards the platen), z to its back.
    Returns {name: (mesh, colour, specular)} for the disc and the five other mounts; ours is separate."""
    import cadquery as cq
    p = HOLDER
    disc = cq.Workplane("XY").circle(p["d"] / 2).extrude(p["t"])
    for i in range(6):
        a = math.radians(30 + 60 * i)
        disc = disc.cut(cq.Workplane("XY").circle(MOUNT_D / 2 + 0.5).extrude(p["t"] + 2)
                        .translate((p["r"] * math.cos(a), p["r"] * math.sin(a), -1)))
    # the slots for the fingertips at our pocket, along the radius (the fingers close radially there)
    a = math.radians(POCKET)
    for r0, r1 in ((p["r"] - 30.0, p["r"] - 14.0), (p["r"] + 14.0, p["r"] + 32.0)):
        rc = (r0 + r1) / 2
        slot = cq.Workplane("XY").box(r1 - r0, 30.0, p["t"] + 4).rotate((0, 0, 0), (0, 0, 1), POCKET) \
            .translate((rc * math.cos(a), rc * math.sin(a), p["t"] / 2))
        disc = disc.cut(slot)
    tab = cq.Workplane("XY").box(p["tab_w"], p["tab_l"] + 10, p["t"]).translate(
        (0, -(p["d"] / 2 + p["tab_l"] / 2 - 5), p["t"] / 2))
    disc = disc.union(tab)
    out = {"disc": (_cq_mesh(disc), (0.72, 0.73, 0.75), 0.75)}
    others = None
    for i in range(6):
        ang = 30 + 60 * i
        if abs(ang - POCKET) < 1:
            continue
        a = math.radians(ang)
        m = pv.Cylinder(center=(p["r"] * math.cos(a), p["r"] * math.sin(a), (p["t"] + p["above"] - p["below"]) / 2),
                        direction=(0, 0, 1), radius=MOUNT_D / 2, height=MOUNT_H, resolution=40).triangulate()
        others = m if others is None else others.merge(m)
    out["mounts"] = (others, (0.46, 0.09, 0.11), 0.35)
    return out


def mount_parts():
    """Our coupon in its 1.25 in Bakelite mount. Frame: the centre of the polished face, z out of the face."""
    body = pv.Cylinder(center=(0, 0, -MOUNT_H / 2), direction=(0, 0, 1), radius=MOUNT_D / 2, height=MOUNT_H,
                       resolution=48).triangulate()
    coupon = pv.Box(bounds=(-7, 7, -5, 5, -6.0, 0.25)).triangulate()
    return {"bakelite": (body, (0.46, 0.09, 0.11), 0.35), "coupon": (coupon, (0.80, 0.81, 0.83), 0.85)}


def rest_parts():
    """The holder's rest on the MiR: a low block on the cabinet top, like the MiR's other storage (props.pocket_block,
    no post). The holder's rim sits on a ledge in a 152 mm recess, 4 mm of wall round it; a deeper middle takes the
    mounts' faces when it lies face down; a notch lets the tab out. Frame: the block's foot on the cabinet top."""
    import cadquery as cq
    p = REST
    blk = cq.Workplane("XY").circle(p["d"] / 2).extrude(p["h"])
    blk = blk.cut(cq.Workplane("XY").circle(HOLDER["d"] / 2 + 1.0).extrude(p["h"]).translate((0, 0, p["ledge"])))
    blk = blk.cut(cq.Workplane("XY").circle(HOLDER["r"] + MOUNT_D / 2 + 2.0).extrude(p["h"])
                  .translate((0, 0, P.DECK_FLOOR)))
    blk = blk.cut(cq.Workplane("XY").box(HOLDER["tab_w"] + 8.0, p["d"], p["h"]).translate(
        (0, -p["d"] / 2, p["ledge"] + p["h"] / 2)))
    return {"rest": (_cq_mesh(blk), (0.94, 0.94, 0.92), 0.25)}


CADDY_VIAL, CADDY_MOUNT = 32.0, -32.0     # the pockets along the caddy's x, which points away from the arm's base


def caddy_parts():
    """A low two-pocket block on the cabinet top: the mount (a 10 mm pocket) nearer the arm, the powder vial (26 mm,
    as props.buffer_holder's) beyond it, where the gripper takes it from outside, pointing back at the arm. 1 mm
    clearance and a lead-in at each mouth, as on the MiR's other storage."""
    import cadquery as cq
    p = CADDY
    blk = cq.Workplane("XY").box(p["w"], p["d"], p["h"]).translate((0, 0, p["h"] / 2))
    for x, r, depth in ((CADDY_MOUNT, MOUNT_D / 2 + P.POCKET_CLEAR, p["mount_bore"]),
                        (CADDY_VIAL, P.VIAL_R + P.POCKET_CLEAR, p["vial_bore"])):
        blk = blk.cut(cq.Workplane("XY").circle(r).extrude(depth + 1.0).translate((x, 0, p["h"] - depth)))
        cone = cq.Solid.makeCone(r, r + P.POCKET_LEAD + 0.5, P.POCKET_LEAD + 0.5,
                                 pnt=cq.Vector(x, 0, p["h"] - P.POCKET_LEAD), dir=cq.Vector(0, 0, 1))
        blk = blk.cut(cq.Workplane("XY").add(cone))
    return {"caddy": (_cq_mesh(blk), (0.94, 0.94, 0.92), 0.25)}


def caddy_angle() -> float:
    """The caddy's turn on the cabinet (deg): its x along the line from the arm's base out through the caddy."""
    return math.degrees(math.atan2(ARM_CADDY[1] - A.ARM_LOCAL[1], ARM_CADDY[0] - A.ARM_LOCAL[0]))


def cup_parts():
    """The SEM's mount cup: a pin into the stage's socket, a cup with an 8 mm bore and a set screw. Frame: its foot."""
    import cadquery as cq
    p = CUP
    cup = cq.Workplane("XY").circle(p["d"] / 2).extrude(p["h"]).cut(
        cq.Workplane("XY").circle(MOUNT_D / 2 + 0.6).extrude(p["bore"] + 1).translate((0, 0, p["h"] - p["bore"])))
    screw = cq.Workplane("YZ").circle(3.0).extrude(8).translate((p["d"] / 2 - 2, 0, p["h"] - 4))
    return {"cup": (_cq_mesh(cup.union(screw)), (0.72, 0.73, 0.75), 0.7)}


def add_parts(sc, rigs):
    """Our parts in the scene. Groups: c_rest/c_caddy on the MiR, c_holder (the 6-position holder), c_mount (the
    coupon), c_vial (the powder), c_cup (in the SEM's stage)."""
    top = P.MIR["H"] + P.CAB_H
    for grp, parts, at in (("c_rest", rest_parts(), ARM_REST), ("c_caddy", caddy_parts(), ARM_CADDY)):
        for name, (mesh, col, spec) in parts.items():
            sc.add(f"{grp}/{name}", mesh, col, grp, specular=spec)
        sc.parent[grp] = "amr"
        sc.gmat[grp] = T((at[0], at[1], top)) @ (R((0, 0, 1), caddy_angle()) if grp == "c_caddy" else np.eye(4))
    for name, (mesh, col, spec) in holder_parts().items():
        sc.add(f"c_holder/{name}", mesh, col, "c_holder", specular=spec)
    for name, (mesh, col, spec) in mount_parts().items():
        sc.add(f"c_mount/{name}", mesh, col, "c_mount", specular=spec)
    sc.add("c_vial/glass", P.vial_glass(), P.GLASS, "c_vial", opacity=0.55, specular=0.7)
    sc.add("c_vial/powder", P.fill(1.0), P.POWDER, "c_vial_powder")
    sc.parent["c_vial_powder"] = "c_vial"
    sc.gmat["c_vial_powder"] = T((0, 0, P.VIAL_FLOOR)) @ S((1, 1, 26.0))
    if "sem" in rigs:
        for name, (mesh, col, spec) in cup_parts().items():
            sc.add(f"c_cup/{name}", mesh, col, "c_cup", specular=spec)
        g = I._tm4000(I.SEM)
        sc.parent["c_cup"] = f"{rigs['sem'].prefix}drawer"
        sc.gmat["c_cup"] = T((0.0, g["ys"] + CUP["dy"], I.SEM["front_z0"] + 62.0))
    # the powder stream (points), hidden until the pour
    sc.add("c_stream", pv.PolyData(np.zeros((1, 3))), P.POWDER, "c_stream", style="points", point_size=4.0,
           render_points_as_spheres=True)
    sc.alpha["c_stream"] = 0.0
    # where they start: the holder face-down on its rest, the coupon in its pocket, the vial in the caddy
    holder_on_rest(sc, face_up=False)
    sc.parent["c_mount"] = "c_holder"
    sc.gmat["c_mount"] = mount_in_holder()
    sc.parent["c_vial"] = "c_caddy"
    sc.gmat["c_vial"] = T((CADDY_VIAL, 0.0, CADDY["h"] - CADDY["vial_bore"]))


def rest_dir():
    """Unit xy the holder's tab points along on the rest (MiR frame): to the back, so the arm takes it from behind
    the MiR, its wrist clear of everything on the cabinet, pointing the way it points at the polisher."""
    return np.array([0.0, -1.0])


def rest_matrix(face_up: bool) -> np.ndarray:
    """The holder on its rest (rest frame), its tab towards the arm; face up (the polished faces up) or down."""
    d = rest_dir()
    th = math.degrees(math.atan2(d[0], -d[1]))            # holder -y (the tab) along d
    M = R((0, 0, 1), th) @ T((0, 0, REST["ledge"]))
    if face_up:
        M = M @ T((0, 0, HOLDER["t"])) @ R((0, 1, 0), 180.0)
    return M


def holder_on_rest(sc, face_up: bool) -> np.ndarray:
    M = rest_matrix(face_up)
    sc.parent["c_holder"] = "c_rest"
    sc.gmat["c_holder"] = M
    return M


def mount_in_holder() -> np.ndarray:
    """Our mount in its pocket: its polished face HOLDER["below"] proud of the holder's face side."""
    a = math.radians(POCKET)
    return T((HOLDER["r"] * math.cos(a), HOLDER["r"] * math.sin(a), -HOLDER["below"])) @ R((1, 0, 0), 180.0)


def tab_grasp() -> np.ndarray:
    """The TCP on the holder's tab, in the holder's frame: pointing at the disc's centre (+y), the fingers on the
    tab's sides (along x), so the gripper is only its 75 mm thickness tall where it passes over the bowl's lip."""
    M = np.eye(4)
    M[:3, 0] = (1, 0, 0)            # tool x: the fingers close across the tab
    M[:3, 2] = (0, 1, 0)            # tool z: towards the centre
    M[:3, 1] = np.cross(M[:3, 2], M[:3, 0])
    M[:3, 3] = (0, -(HOLDER["d"] / 2 + HOLDER["tab_l"] - 22.0), HOLDER["t"] / 2)
    return M


GRIP_TAB = 0.70 + (28.0 - HOLDER["tab_w"]) / 90.0


def mount_grasp(spin=0.0) -> np.ndarray:
    """The TCP on the mount, in the mount's frame (z out of the face): pointing at the face, 4 mm into the mount."""
    M = np.eye(4)
    M[:3, 2] = (0, 0, -1)
    c, s = math.cos(math.radians(spin)), math.sin(math.radians(spin))
    M[:3, 0] = (c, s, 0)
    M[:3, 1] = np.cross(M[:3, 2], M[:3, 0])
    M[:3, 3] = (0, 0, -4.0)
    return M


def branch_q(rb, Tw, Tw_ref):
    """The IK solution for Tw in the branch of the first clear solution for Tw_ref (as alloy_workflow.py does), so a
    straight line from one to the other stays in a branch that is clear where it ends."""
    import collide
    chk = rb.checker()
    Wd = chk.snapshot()
    Tb = np.linalg.inv(rb.sc.world(rb.root)) @ Tw_ref
    for q in collide.ik_all(rb.model, Tb, rb.q):
        if not chk.collisions(q, rb.close, Wd, chk.touching(q, rb.close, Wd)):
            return rb.solve(Tw, seed=q)
    return rb.solve(Tw)


# ================================================================================================= the movie
def movie():
    sc, L, rigs, idata = build()
    rb = L.robot
    add_parts(sc, rigs)
    PARK = np.radians(A.PARK_DEG)
    pol, sem, nano, ms = rigs["polisher"], rigs["sem"], rigs["nanoindenter"], rigs["mastersizer"]
    n = 5
    amr_x0 = 3300.0

    def amr_at(x):
        sc.gmat["amr"] = T((x, A.AMR_XY[1], 0))
        if rb.held is not None:
            rb.set()

    def drive(x1):
        x0 = sc.gmat["amr"][0, 3]

        def up(u):
            amr_at(x0 + (x1 - x0) * u)
        return up
    amr_at(amr_x0)
    CAM_IN = [(4200, -6400, 2700), (900, -1500, 1150), (0, 0, 1)]
    CAM_OPEN = [(2400, -4300, 2100), (-150, -1250, 1100), (0, 0, 1)]
    sc.cam = list(CAM_IN)
    status(sc, Arm="UR10e on MiR250, arriving", Coupon="mounted, in the PX500's holder", Powder="vial, 5 g",
           Trays="D, E, F in their slots")

    # ------------------------------------------------------------------ 0. the samples arrive
    cap = "Chapter 4 broke one bar from the AlSi10Mg plate in the Instron. Now samples of the same build go through " \
          "the characterization trays: a coupon cut from the plate and hot-mounted in a 1.25 in Bakelite mount, in " \
          "the polisher's 6-position holder, and a vial of the sieved powder it was printed from."
    sc.step(f"1/{n}", cap, 3.2, drive(0.0), hold=0.2, cam_to=CAM_OPEN)
    sc.step(f"1/{n}", cap, 0.6, None, hold=1.6,
            labels=[("6-position holder, the coupon's mount in it", tuple(sc.world("c_holder")[:3, 3] + (0, 0, 40)),
                     (0.16, 0.34)),
                    ("powder vial", tuple(sc.world("c_vial")[:3, 3] + (0, 0, 70)), (0.80, 0.34))])

    # ------------------------------------------------------------------ helpers
    st = {"lbl": f"1/{n}", "cap": cap}

    def go(Tw=None, q=None, secs=1.6, cam=None, labels=(), grip=None, extra=None, hold=0.05):
        f = rb.joint_to(Tw=Tw) if Tw is not None else rb.joint_to(q)
        sc.step(st["lbl"], st["cap"], secs, RB.both(f, rb.grip_to(grip) if grip is not None else None, extra),
                hold=hold, cam_to=cam, labels=labels)

    def lin(Tw, secs=0.8, extra=None, hold=0.05, cam=None):
        sc.step(st["lbl"], st["cap"], secs, RB.both(rb.line_to(Tw), extra), hold=hold, cam_to=cam)

    def grip(c, secs=0.4):
        sc.step(st["lbl"], st["cap"], secs, rb.grip_to(c), hold=0.05)

    def sh(Tw, d):
        M = Tw.copy()
        M[:3, 3] = M[:3, 3] + np.asarray(d, float)
        return M

    def along(Tw, dist):
        """Tw moved `dist` mm along its own approach (tool z)."""
        return sh(Tw, Tw[:3, 2] * dist)

    def clock(what, t0, t1, fmt="min"):
        """An update for the on-screen clock: the instrument's own time from t0 to t1 minutes."""
        def up(u):
            t = t0 + (t1 - t0) * u
            sc.clock = (what, f"{int(t // 60):d} h {int(t % 60):02d} min" if fmt == "h" else
                        f"{int(t):d}:{int(round((t % 1) * 60)) % 60:02d}")
        return up

    def park(secs=1.4, cam=None, labels=(), extra=None):
        go(q=PARK, secs=secs, cam=cam, labels=labels, extra=extra)

    def face():
        """The grasp point on the mount: on its axis, TCP_OUT out from the polished face (the mount's z is out of it),
        so the pads hold the mount's top 13 mm and stop short of a cup's rim or the holder's face."""
        M = sc.world("c_mount")
        return M[:3, 3] + M[:3, 2] * TCP_OUT

    def go_to(Tw, ref, secs=1.6, cam=None, labels=(), grip=None, extra=None, hold=0.05):
        """A joint move to Tw in the IK branch that is clear at `ref`, where the straight line that follows ends."""
        q = branch_q(rb, Tw, ref)
        go(q=q, secs=secs, cam=cam, labels=labels, grip=grip, extra=extra, hold=hold)

    # ------------------------------------------------------------------ 1. tray F: grind and polish
    p = I.POLISHER
    g = I._px500(p)
    hz = p["deck"] + p["head_up"]
    RAISE = -70.0 / (hz - 120.0 - 13.0 - (p["deck"] + p["platen_z"]))     # the head 70 mm over its working height
    st["lbl"] = f"2/{n}"
    st["cap"] = "Tray F (sample prep) comes to the opening: the LECO PX500 grinder-polisher, the lab's own, and the " \
                "Nabertherm furnace."
    status(sc, Arm="parked", Trays="F to the opening")
    L.fetch("F", st["lbl"], st["cap"], fast=0.55, cam=CAM_OPEN, hold=0.2)
    status(sc, Trays="F at the opening")
    head_g = f"{pol.prefix}head"
    pw = lambda q: inst_world(sc, pol, q)                         # noqa: E731
    CAM_POL = [tuple(pw((g["hx"], g["hy"], 300)) + (-950, -1650, 800)), tuple(pw((g["hx"], g["hy"], 330))),
               (0, 0, 1)]
    st["cap"] = "The PX500's head lifts 70 mm for a holder change (assumed: LECO doesn't publish its stroke), and the " \
                "arm takes the 6-position holder off its rest by a tab, our addition, with the coupon's mount in it."
    status(sc, Polisher="head up for a holder change", Arm="taking the holder")
    sc.step(st["lbl"], st["cap"], 1.0, pol.move({"head": (0.0, RAISE)}), hold=0.1, cam_to=CAM_POL,
            labels=[("LECO PX500", tuple(pw((g["hx"] - 140, g["hy"], 600))), (0.20, 0.24))])
    G = tab_grasp()
    T_tab = sc.world("c_holder") @ G
    go_to(along(T_tab, -110), T_tab, secs=1.6, grip=0.55, cam=CAM_OPEN)
    lin(T_tab, 0.7)
    grip(GRIP_TAB)
    rb.grasp("c_holder")
    lin(sh(T_tab, (0, 0, 40)), 0.6)
    lin(sh(along(T_tab, -90), (0, 0, 60)), 0.7)
    # under the raised head, level and 4 mm low, then up onto the spindle's quick-change coupling (assumed)
    W_head = sc.world(head_g)
    H_on = W_head @ T((g["hx"], g["hy"], hz - 120.0))
    T_on = H_on @ G
    st["cap"] = "In under the head, level, and up onto the spindle's quick-change coupling. The holder's other five " \
                "pockets hold mounts from the same build."
    status(sc, Arm="fitting the holder")
    go_to(sh(along(T_on, -260), (0, 0, -4)), sh(T_on, (0, 0, -4)), secs=2.0, cam=CAM_POL)
    lin(sh(T_on, (0, 0, -4)), 1.2)
    lin(T_on, 0.3)
    grip(0.55)
    rb.release(head_g)
    lin(along(T_on, -240), 0.9)
    park(1.4)
    status(sc, Arm="parked", Polisher="holder on")

    # the cycle: the lab's SOP (README): SiC 320 to 1200 grit with water, then 1 um alumina on a white cloth
    sc.gmat["c_holder"] = sc.gmat["c_holder"].copy()
    hold0 = sc.gmat["c_holder"].copy()
    spin = {"deg": 0.0}

    def turn(d0, d1):
        def up(u):
            spin["deg"] = d0 + (d1 - d0) * u
            sc.gmat["c_holder"] = hold0 @ T((0, 0, 0))
            sc.gmat["c_holder"] = T((g["hx"], g["hy"], 0)) @ R((0, 0, 1), spin["deg"]) @ T((-g["hx"], -g["hy"], 0)) \
                @ hold0
        return up
    st["cap"] = "Grinding, as in the lab's SOP: the head comes down, water on, platen 150 rpm and head 35 rpm, 30 s " \
                "each on 320, 400, 600, 800 and 1200 grit SiC paper (the papers are changed between steps, not shown)."
    status(sc, Polisher="grinding, SiC 320 grit")
    sc.step(st["lbl"], st["cap"], 1.2, RB.both(pol.move({"head": (RAISE, 1.0), "paper": (0.0, 1.0)}),
                                               clock("PX500, the SOP's time", 0.0, 0.1)), hold=0.0, cam_to=CAM_POL)

    def grind(u):
        pol.move({"platen": (0.0, 1.0), "glow": (0.0, 1.0)})(u)
        turn(0.0, -720.0)(u)
        clock("PX500, the SOP's time", 0.1, 4.5)(u)
        grits = (320, 400, 600, 800, 1200)
        status(sc, Polisher=f"grinding, SiC {grits[min(4, int(u * 5))]} grit, water")
    sc.step(st["lbl"], st["cap"], 4.0, grind, hold=0.1)
    st["cap"] = "Then the final polish: a white cloth with 1 µm alumina suspension from a dispenser, force 3-5, " \
                "150 rpm, 3 min. Then rinse."
    status(sc, Polisher="cloth, 1 um alumina")
    sc.step(st["lbl"], st["cap"], 1.0, RB.both(pol.move({"paper": (1.0, 0.0), "cloth": (0.0, 1.0), "glow": (1.0, 0.0)}),
                                               clock("PX500, the SOP's time", 4.5, 5.0)), hold=0.0)

    def polish(u):
        pol.move({"platen": (1.0, 2.0), "powder": (0.0, 1.0), "alumina": (0.0, 1.0)})(u)
        turn(-720.0, -1440.0)(u)
        clock("PX500, the SOP's time", 5.0, 8.5)(u)
    sc.step(st["lbl"], st["cap"], 3.6, polish, hold=0.1)
    sc.step(st["lbl"], st["cap"], 1.0, RB.both(pol.move({"head": (1.0, RAISE), "powder": (1.0, 0.0)}),
                                               clock("PX500, the SOP's time", 8.5, 9.0)), hold=0.2)
    sc.clock = None
    status(sc, Polisher="done, head up")
    # the holder off, turned face up on its way back to the rest
    st["cap"] = "The arm takes the holder off and turns it face up on its way back to the rest, so the polished face " \
                "comes up with the mount."
    status(sc, Arm="taking the holder off")
    T_on = sc.world("c_holder") @ G
    go_to(along(T_on, -240), T_on, secs=1.6, grip=0.55)
    lin(T_on, 0.9)
    grip(GRIP_TAB)
    rb.grasp("c_holder")
    lin(sh(T_on, (0, 0, -4)), 0.3)
    lin(sh(along(T_on, -260), (0, 0, -4)), 1.2)
    W_rest = sc.world("c_rest")
    T_up = W_rest @ rest_matrix(True) @ G
    go_to(sh(along(T_up, -90), (0, 0, 60)), sh(T_up, (0, 0, 40)), secs=2.2, cam=CAM_OPEN)
    lin(sh(T_up, (0, 0, 40)), 0.7)
    lin(T_up, 0.5)
    grip(0.55)
    rb.release("c_rest")
    lin(along(T_up, -110), 0.7)
    # the mount out of the face-up holder, by its polished end (the pocket is slotted for the fingertips)
    st["cap"] = "Tray F goes back to its slot. The arm lifts the mount out of the holder by its polished end; the " \
                "pocket is slotted for the fingertips (our design)."
    status(sc, Arm="taking the mount", Coupon="polished")
    T_m = A.down(face(), spin=90.0)             # the fingers along the holder's radius there: world y on the rest
    go_to(sh(T_m, (0, 0, 70)), T_m, secs=1.6, grip=OPEN_NEAR)
    lin(T_m, 0.7)
    grip(GRIP_MOUNT)
    rb.grasp("c_mount")
    lin(sh(T_m, (0, 0, 70)), 0.7)
    park(1.4)
    status(sc, Arm="parked, holding the mount")
    L.store("F", st["lbl"], st["cap"], fast=0.55, hold=0.1, cam=CAM_OPEN)
    status(sc, Trays="F stored", Polisher="")

    # ------------------------------------------------------------------ 2. tray D: the SEM
    st["lbl"] = f"3/{n}"
    st["cap"] = "Tray D (microscopy and diffraction) comes down: the Hitachi TM4000PlusII SEM, the MiniFlex XRD and " \
                "six OpenFlexure microscopes. The arm holds the mount meanwhile."
    status(sc, Trays="D to the opening")
    L.fetch("D", st["lbl"], st["cap"], fast=0.55, cam=CAM_OPEN, hold=0.2)
    status(sc, Trays="D at the opening")
    ys = I._tm4000(I.SEM)["ys"]
    sw = lambda q: inst_world(sc, sem, q)                         # noqa: E731
    CAM_SEM = [tuple(sw((0, -300, 200)) + (-950, -1750, 850)), tuple(sw((0, -330, 180))), (0, 0, 1)]
    st["cap"] = "The SEM vents and its door comes out with the stage on it. A cup for 1.25 in mounts stays in the " \
                "stage's socket (our fixture); the arm sets the mount in it, polished face up."
    status(sc, SEM="venting, door out", Arm="loading the SEM")
    sc.step(st["lbl"], st["cap"], 1.4, sem.move({"drawer": (0.0, 1.0)}), hold=0.1, cam_to=CAM_SEM,
            labels=[("Hitachi TM4000PlusII", tuple(sw((0, 0, 600))), (0.22, 0.22))])
    cup_top = sc.world("c_cup") @ np.r_[0, 0, CUP["h"] - CUP["bore"] + MOUNT_H + TCP_OUT, 1.0]
    T_cup = A.down(cup_top[:3], spin=180.0)    # the wrist camera on the side away from the SEM
    go_to(sh(T_cup, (0, 0, 90)), T_cup, secs=1.8)
    lin(T_cup, 0.8)
    grip(OPEN_NEAR)
    rb.release("c_cup")
    lin(sh(T_cup, (0, 0, 90)), 0.7)
    park(1.4)
    status(sc, Arm="parked")
    st["cap"] = "Door in, EVAC: about three minutes to vacuum. Then backscattered-electron images of the polished " \
                "section (the Si network round the melt pools, any porosity) and an EDS map of Al, Si and Mg."
    status(sc, SEM="pumping down")
    sc.step(st["lbl"], st["cap"], 1.4, RB.both(sem.move({"drawer": (1.0, 0.0)}), clock("TM4000", 0.0, 0.2)),
            hold=0.1)
    sc.step(st["lbl"], st["cap"], 1.4, clock("TM4000", 0.2, 3.0), hold=0.1)
    status(sc, SEM="BSE imaging, EDS map")
    sc.inset = "sem"

    def sem_on(u):
        sc.inset_a = u
        clock("TM4000", 3.0, 18.0)(u)
    sc.step(st["lbl"], "No image of this section exists yet. The inset is real data from the lab, of the powder this "
                       "plate was printed from (chapter 4's), not of the section, and not from the TM4000.",
            4.2, sem_on, hold=0.6, still=True)     # the still: the chapter at work (alloy_route.py)

    def sem_off(u):
        sc.inset_a = 1.0 - u
        clock("TM4000", 18.0, 20.0)(u)
        sem.move({"drawer": (0.0, 1.0)})(u)
    st["cap"] = "Vented, door out; the arm takes the mount back."
    status(sc, SEM="vented, door out", Arm="unloading the SEM")
    sc.step(st["lbl"], st["cap"], 1.4, sem_off, hold=0.1)
    sc.inset, sc.clock = None, None
    T_cup = A.down(face(), spin=180.0)
    go_to(sh(T_cup, (0, 0, 90)), T_cup, secs=1.6, grip=OPEN_NEAR)
    lin(T_cup, 0.8)
    grip(GRIP_MOUNT)
    rb.grasp("c_mount")
    lin(sh(T_cup, (0, 0, 90)), 0.7)
    park(1.4, extra=sem.move({"drawer": (1.0, 0.0)}))
    status(sc, Arm="parked, holding the mount", SEM="")
    st["cap"] = "Tray D goes back up; tray E comes down."
    L.store("D", st["lbl"], st["cap"], fast=0.55, hold=0.1, cam=CAM_OPEN)

    # ------------------------------------------------------------------ 3. tray E: nanoindentation
    st["lbl"] = f"4/{n}"
    st["cap"] = "Tray E (mechanical testing and particle size): the Plastometrex PIP, the KLA iMicro nanoindenter " \
                "and the Malvern Mastersizer 3000."
    status(sc, Trays="E to the opening")
    L.fetch("E", st["lbl"], st["cap"], fast=0.55, hold=0.2, cam=CAM_OPEN)
    status(sc, Trays="E at the opening")
    NP = I.NANO
    sz = NP["feet"] + 70 + NP["stage_z"] - 60
    nw = lambda q: inst_world(sc, nano, q)                        # noqa: E731
    CAM_NANO = [tuple(nw((0, -200, 250)) + (-900, -1650, 850)), tuple(nw((60, -60, 230))), (0, 0, 1)]
    # the stage's load position: 60 mm out in x and 60 mm forward of the objective. Further in, every IK solution
    # for a gripper pointing down puts the forearm or the wrist into the cabinet (ARM_AUDIT; /tmp probe of 8 branches x
    # 4 spins x 7 stage positions)
    LOAD, NDY = -0.6, -60.0
    st["cap"] = "The iMicro's hood lifts and its XY stage runs out to a load position, clear of the objective. The " \
                "arm sets the mount on the stage."
    status(sc, iMicro="hood up, stage to load", Arm="loading the nanoindenter")
    sc.step(st["lbl"], st["cap"], 1.6, nano.move({"lid": (0.0, 1.0), "stage": (0.0, LOAD)}), hold=0.1,
            cam_to=CAM_NANO, labels=[("KLA iMicro nanoindenter", tuple(nw((0, 0, 560))), (0.22, 0.22))])
    spot = sc.world(f"{nano.prefix}stage") @ np.r_[NP["scope_x"], NDY, sz + MOUNT_H + TCP_OUT, 1.0]
    T_n = A.down(spot[:3], spin=180.0)   # the fingers along x, the camera to the open front
    go_to(sh(T_n, (0, 0, 100)), T_n, secs=1.8)
    lin(T_n, 0.8)
    grip(OPEN_NEAR)
    rb.release(f"{nano.prefix}stage")
    m_on = sc.gmat["c_mount"].copy()

    def stage_y(a, b):
        """The stage's y travel, drawn as the mount's (the model's stage moves in x only)."""
        def up(u):
            sc.gmat["c_mount"] = T((0, a + (b - a) * u, 0)) @ m_on
        return up
    lin(sh(T_n, (0, 0, 100)), 0.7)
    park(1.4)
    status(sc, Arm="parked")
    st["cap"] = "Hood down, shutting out air currents and noise. The stage carries the mount under the microscope, " \
                "then under the indenter, for a 5 × 5 grid of indents to 500 nm (hardness and modulus), and back to " \
                "image them."
    status(sc, iMicro="indenting, 25 indents")
    sc.step(st["lbl"], st["cap"], 1.6, RB.both(nano.move({"lid": (1.0, 0.0), "stage": (LOAD, 0.0)}),
                                               stage_y(0.0, -NDY), clock("iMicro", 0.0, 2.0)), hold=0.1)
    sc.step(st["lbl"], st["cap"], 3.0, RB.both(nano.move({"stage": (0.0, 1.0), "~lid": (0.0, 1.0)}),
                                               clock("iMicro", 2.0, 40.0)), hold=0.1)
    sc.step(st["lbl"], st["cap"], 1.4, RB.both(nano.move({"stage": (1.0, 0.0)}), clock("iMicro", 40.0, 45.0)),
            hold=0.2)
    st["cap"] = "Hood up, stage out; the mount goes back to the caddy on the MiR."
    status(sc, iMicro="done", Arm="unloading the nanoindenter")
    sc.step(st["lbl"], st["cap"], 1.4, RB.both(nano.move({"lid": (0.0, 1.0), "stage": (0.0, LOAD), "~lid": (1.0, 0.0)}),
                                               stage_y(-NDY, 0.0)), hold=0.1)
    sc.clock = None
    T_n = A.down(face(), spin=180.0)
    go_to(sh(T_n, (0, 0, 100)), T_n, secs=1.6, grip=OPEN_NEAR)
    lin(T_n, 0.8)
    grip(GRIP_MOUNT)
    rb.grasp("c_mount")
    lin(sh(T_n, (0, 0, 100)), 0.7)
    caddy_m = sc.world("c_caddy") @ np.r_[CADDY_MOUNT, 0.0,
                                          CADDY["h"] - CADDY["mount_bore"] + MOUNT_H + TCP_OUT, 1.0]
    T_c = A.down(caddy_m[:3], spin=90.0 - caddy_angle())      # the fingers across the caddy, clear of the vial
    go_to(sh(T_c, (0, 0, 90)), T_c, secs=2.0, cam=CAM_OPEN)
    lin(T_c, 0.7, extra=nano.move({"lid": (1.0, 0.0), "stage": (LOAD, 0.0)}))
    grip(OPEN_NEAR)
    rb.release("c_caddy")
    lin(sh(T_c, (0, 0, 90)), 0.6)
    status(sc, iMicro="", Coupon="polished, imaged, indented; in the caddy")

    # ------------------------------------------------------------------ 4. tray E: the powder through the Mastersizer
    MP = I.MS3000
    gm = I._ms3000(MP)
    mw = lambda q: inst_world(sc, ms, q)                          # noqa: E731
    hop = mw((gm["hx"], gm["hy"], MP["hop_z"]))
    CAM_MS = [tuple(hop + (700, -1300, 600)), tuple(hop + (60, 0, -60)), (0, 0, 1)]
    st["cap"] = "Then the powder: the arm takes the vial from the caddy by its side. The Aero S's clear cover lifts " \
                "off (by hand in Malvern's videos; an actuator is assumed here)."
    status(sc, Arm="taking the vial", Malvern="cover off")
    v_at = sc.world("c_vial")[:3, 3] + (0, 0, 45.0)
    d = -sc.world("c_caddy")[:3, 0]                  # from outside the caddy, pointing back at the arm's base
    d = np.r_[d[:2] / np.linalg.norm(d[:2]), 0.0]
    T_v = A.level(v_at, toward=tuple(d), spin=0.0)
    go(along(T_v, -100), secs=1.6, grip=0.55, extra=ms.move({"lid": (0.0, 1.0)}))
    lin(T_v, 0.6)
    grip(GRIP_VIAL)
    rb.grasp("c_vial")
    lin(sh(T_v, (0, 0, 60)), 0.6)
    # over the hopper, then a roll of the wrist pours it
    toward = np.array([0.0, 1.0, 0.0])
    p_pour = hop + (18.0, 0.0, 52.0)            # rolled 120 deg, the vial's mouth ends 40 mm over the hopper's middle
    T_p = A.level(p_pour, toward=tuple(toward), spin=0.0)
    st["cap"] = "A few grams into the hopper, over the vibrating tray: the wrist rolls the vial over."
    status(sc, Arm="pouring the powder")
    go(T_p, secs=2.0, cam=CAM_MS, labels=[("Malvern Mastersizer 3000 + Aero S", tuple(hop + (0, 0, 220)),
                                           (0.70, 0.22))])
    T_tip = T_p @ R((0, 0, 1), -120.0)

    def pour_fx(u):
        on = 0.35 < u
        sc.alpha["c_stream"] = 1.0 if on else 0.0
        if on:
            mouth = (sc.world("c_vial") @ np.r_[0, 0, P.VIAL_H, 1.0])[:3]
            k = np.arange(24) / 24.0
            ph = (k + u * 7.0) % 1.0
            pts = np.c_[np.full(24, mouth[0]) + np.sin(k * 40) * 2, np.full(24, mouth[1]) + np.cos(k * 31) * 2,
                        mouth[2] - (mouth[2] - (hop[2] - 20)) * ph]
            sc.set_mesh("c_stream", pv.PolyData(pts))
    lin(T_tip, 1.4, extra=pour_fx, hold=0.0)
    sc.step(st["lbl"], st["cap"], 1.2, pour_fx, hold=0.0)
    sc.alpha["c_stream"] = 0.0
    sc.gmat["c_vial_powder"] = T((0, 0, P.VIAL_FLOOR)) @ S((1, 1, 14.0))
    status(sc, Powder="about 3 g in the Aero S's hopper")
    lin(T_p, 1.0)
    status(sc, Arm="the vial back to the caddy")
    go(sh(T_v, (0, 0, 60)), secs=2.0, cam=CAM_OPEN)
    lin(T_v, 0.6)
    grip(0.55)
    rb.release("c_caddy")
    lin(along(T_v, -100), 0.6)
    st["cap"] = "Cover on, air on and the background measured; the tray vibrates the powder into the venturi and the " \
                "air carries it to the cell, across the laser (drawn see-through). Three measurements, under a " \
                "minute each."
    status(sc, Arm="parked", Malvern="measuring")
    park(1.4, extra=ms.move({"lid": (1.0, 0.0), "powder": (0.0, 1.0)}), cam=CAM_MS)

    def measure(u):
        ms.move({"tray": (0.0, 1.0), "beam": (0.0, 1.0), "~body": (0.0, 1.0), "powder": (1.0, 0.0)})(u)
        clock("Mastersizer", 0.0, 3.0)(u)
    sc.step(st["lbl"], st["cap"], 3.4, measure, hold=0.2)
    sc.step(st["lbl"], st["cap"], 1.0, RB.both(ms.move({"beam": (1.0, 0.0), "~body": (1.0, 0.0)}),
                                               clock("Mastersizer", 3.0, 3.5)), hold=0.2)
    sc.clock = None
    status(sc, Malvern="done", Powder="measured: the size distribution")
    st["cap"] = "Tray E goes back up to its slot and its power."
    L.store("E", st["lbl"], st["cap"], fast=0.55, hold=0.1, cam=CAM_IN)
    status(sc, Trays="D, E, F in their slots", Malvern="")
    return finish(sc, L, rb)


def finish(sc, L, rb):
    sc.step("5/5", "Done: the build's coupon ground and polished on tray F, imaged in the SEM on tray D and indented on "
            "tray E, and its powder sized on tray E, every tray brought to the opening only when it was needed, and "
            "every arm move checked against everything in the scene.", 1.4, None, hold=3.0)
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm", flush=True)
    return sc.save()


def probe():
    """Print where things are with each tray at the opening, and draw a still of each."""
    sc, L, rigs, idata = build()
    rb = L.robot
    print("arm base", sc.world(rb.root)[:3, 3])
    for k in ("F", "D", "E"):
        L.tray[k] = [*V.SLOTS["open"]]
        L.where[k] = "open"
        L.apply_state()
        for key, x, y in line.TRAY_LOADS[k]:
            if key not in rigs:
                continue
            bb = idata[key][0].bbox()
            lo = inst_world(sc, rigs[key], (bb[0], bb[2], bb[4]))
            hi = inst_world(sc, rigs[key], (bb[1], bb[3], bb[5]))
            print(k, key, "world box", lo.round(0), hi.round(0))
        sc.cam = [(2600, -5200, 2300), (0, -1100, 1250), (0, 0, 1)]
        Image.fromarray(sc.render_base()).save(f"/tmp/ch5_probe_{k}.png")
        L.tray[k] = [*V.SLOTS[A.HOME[k]]]
        L.where[k] = A.HOME[k]
        L.apply_state()
    sc.pl.close()


if __name__ == "__main__":
    if sys.argv[1:] == ["probe"]:
        probe()
    else:
        print(movie(), flush=True)
