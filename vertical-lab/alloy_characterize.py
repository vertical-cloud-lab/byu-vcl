"""The alloy route, chapter 7: characterizing the build (#303, PR #318, round 8).

    VLAB_ONLY_TRAYS=DEKL VIZ3D_FPS=6 xvfb-run -a python3 alloy_characterize.py   # -> out/alloy_characterize.gif, .mp4
    VLAB_ONLY_TRAYS=DEKL PREVIEW=1 xvfb-run -a python3 alloy_characterize.py     # the last frame of each sub-step
    VLAB_ONLY_TRAYS=DEKL ARM_AUDIT=1 xvfb-run -a python3 alloy_characterize.py   # every frame collision-checked

(``VLAB_ONLY_TRAYS``: setup_lab populates only the trays this chapter presents; the cladding is opaque, so the
others, empty, aren't seen.)

Chapter 6 (``alloy_prep.py``) made two specimens from the AlSi10Mg build, and chapter 5 (``alloy_workflow.py``) broke a
tensile bar. They ride a caddy on the MiR250's cabinet (``r8_specimens``: the conductive hot mount and the steel
mount, 1.5 in), with the bar's upper half. The lab is the two-Shuttle floor of ``setup_lab.py`` with every tray loaded,
as the set-up movie leaves it. The trays come to the opening one at a time and the UR10e loads each instrument:

* **Tray D, Shuttle 1: the Hitachi TM4000PlusII.** The hot mount into the stage's holder cup, where a spring plunger
  presses it against the cup's wall: coupon -> carbon-filled phenolic -> cup -> stage, the path to ground. BSE, then
  EDS (the box beside the SEM is its analyser, Oxford's AZtecOne).
* **Tray E, Shuttle 1: the KLA iMicro, then the Plastometrex PIP**, on the steel mount (the slice on steel: nothing
  soft under it). The iMicro's hood is drawn see-through while it works; the stage carries the slice from the
  microscope to the indenter. The PIP's bay is too low for a gripper, so a loading slide (ours) carries the mount out.
* The MiR250 drives to Shuttle 2 at its 0.3 m/s^2 (props.ramp_frac).
* **Tray L: the Mitutoyo HM-220 micro-Vickers**, on the hot mount, by its own loading slide (ours).
* **Tray K: the Keyence VHX-7000** with the bar's upper half on a carrier (ours): the free-angle head tilts round it,
  the arm turns it over, and a second series covers the underside: the whole bar in 3-D.

Each instrument's data follows its step (``data_panels.py``), labelled real, computed or illustrative. The models are
``r8_char.py``'s. Every arm move is a straight line of the grasp point (IK every frame) or a joint move planned round
whatever is in the way (``robot.py``, ``collide.py``). What is assumed is in ``notes/alloy_characterize.md``.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw

import scene
scene.GIF_FPS = 3                     # a ~4-minute GIF under 4.9 MB (the MP4 keeps every frame)
scene.GIF_SIZE = (512, 288)
from scene import CLEAN, PREVIEW, Scene, T, R, font  # noqa: E402

import animate as A                   # noqa: E402
import lab                            # noqa: E402
import props as P                     # noqa: E402
import r8_char as RC                  # noqa: E402
import r8_specimens as SP             # noqa: E402
import robot as RB                    # noqa: E402

NAME = "alloy_characterize"
TITLE = "Vertical cloud lab, the alloy route 7/7: characterizing the build"
HERE = Path(__file__).resolve().parent

MOUNT_D, FACE = SP.MOUNT_D, SP.FACE_Z          # 38.1 mm, 20 mm
GRIP_MOUNT = 0.588                    # 2F-85 closure on a 38.1 mm mount (pads 38.0 mm apart: ur_arm.gripper_fk)
GRIP_BAR = 0.90                       # on the bar's 10 mm grip section
OPEN = 0.30                           # opened to 62 mm, to reach in beside a mount or the bar
TCP_UP = 13.0                         # the grasp point 13 mm over a mount's face: the pads (+-19 mm) hold its top 6 mm,
#                                       clear of a holder cup's rim
BAR_UP = 14.0                         # and 14 mm over the bar's top: the pads end level with its underside
MIR_SPEED = 1500.0                    # mm/s at most, at 0.3 m/s^2 (props.ramp_secs), as the other chapters
HM_DOCK = 300.0                       # at Shuttle 2 the MiR stops this far short of its dock for the HM-220 (IK: 8
#                                       solutions there against 4 at the dock, 1033 mm out)

# the caddy (ours) on the MiR's cabinet top, where chapter 6 left the mounts (alloy_prep.HOT_AT, ST_AT): a low block
# with two pockets 6 mm deep and a ridge for the bar, narrower than the bar so the pads reach down either side of it
CADDY = dict(w=230.0, d=100.0, h=14.0, pocket=6.0, ridge_w=8.0, ridge_l=40.0, ridge_h=6.0)
CADDY_AT = (250.0, -190.0)            # MiR frame
SLOT_AT = {"hot": (-70.0, 0.0), "steel": (0.0, 0.0), "bar": (75.0, 0.0)}      # caddy frame
CAB_TOP = P.MIR["H"] + P.CAB_H        # 780 mm: the cabinet's top

CAM_LAB = [(9400, -11800, 6400), (1800, -1600, 1300), (0, 0, 1)]
PANEL_W = 0.44                        # a data panel's width, as a share of the frame


# ================================================================================================= the scene
class ChScene(Scene):
    """setup_lab.build's Scene, with a data panel (data_panels.py) and an instrument clock drawn over every frame."""

    def setup_overlays(self):
        self.panel = None             # data_panels key, or "grid" for all six
        self.panel_a = 0.0
        self.clock = None             # (instrument, text) or None
        self._pcache = {}

    def overlay(self, img, scale, anchors):
        img = super().overlay(img, scale, anchors)
        if CLEAN:
            return img
        if self.panel and self.panel_a > 0.02:
            if self.panel == "grid":
                self._draw_grid(img)
            else:
                self._draw_panel(img, self.panel)
        if self.clock:
            self._draw_clock(img)
        return img

    def _pan(self, key, w):
        import data_panels as D
        k = (key, w)
        if k not in self._pcache:
            pan = D.panel(key)
            h = int(w * pan.height / pan.width)
            self._pcache[k] = pan.resize((w, h), Image.LANCZOS).convert("RGBA")
        return self._pcache[k]

    def _draw_panel(self, img, key):
        W, H = img.size
        pnl = self._pan(key, int(PANEL_W * W)).copy()
        pnl.putalpha(int(255 * min(1.0, self.panel_a) * 0.97))
        img.paste(pnl, (W - pnl.width - int(0.012 * W), int(0.075 * H)), pnl)

    def _draw_grid(self, img):
        W, H = img.size
        keys = ("sem", "eds", "hv", "nano", "pip", "vhx")
        w = int(0.315 * W)
        x0, y0 = int(0.02 * W), int(0.085 * H)
        for i, k in enumerate(keys):
            pnl = self._pan(k, w).copy()
            pnl.putalpha(int(255 * min(1.0, self.panel_a) * 0.97))
            img.paste(pnl, (x0 + (i % 3) * (w + int(0.012 * W)), y0 + (i // 3) * (pnl.height + int(0.012 * H))), pnl)

    def _draw_clock(self, img):
        W, H = img.size
        k = W / 1280
        s = max(k, 0.8)
        what, txt = self.clock
        d = ImageDraw.Draw(img, "RGBA")
        f1, f2 = font(13 * s), font(26 * s, bold=True, mono=True)
        w = max(d.textlength(what, font=f1), d.textlength(txt, font=f2)) + 24 * k
        x0, y1 = 14 * k, H - 150 * k
        d.rounded_rectangle((x0, y1 - 58 * s, x0 + w, y1), 6 * k, fill=(20, 24, 34, 225))
        d.text((x0 + 12 * k, y1 - 54 * s), what, font=f1, fill=(190, 200, 215))
        d.text((x0 + 12 * k, y1 - 36 * s), txt, font=f2, fill=(255, 255, 255))


def build():
    import setup_lab as SL
    import warehouse as W
    if hasattr(SL, "item_label"):           # setup_lab's in-progress item_label reads inst.name, which Instrument lacks
        def item_label(inst):
            m = inst.model.strip()
            return f"{inst.title} (our design)" if m.lower() in ("our design", "ours", "(ours)") else m
        SL.item_label = item_label
    data = lab.meshes()
    idata = SL.load_all()
    sc, L, F, items, rigs, units, util, ulabel, vp = SL.build(data, idata, name=NAME, title=TITLE)
    sc.__class__ = ChScene
    sc.setup_overlays()
    sc.gif = not (PREVIEW or scene.AUDIT)
    SL.add_bay_cams(sc)
    u = units[0]
    u.set(W.dock_pose("vlm"))
    L.robot = u.robot
    # opaque cladding: with VLAB_ONLY_TRAYS=DEKL (runner_guard: 1.5 GB instead of 5) the other trays stand empty
    # inside the Shuttles, so they are not shown through a see-through skin
    L.skin(0.0)(1.0)
    L.show_gauges = True
    L.extra_gauges = []
    L.apply_state()
    return sc, L, F, rigs, u


def fast_collisions(sc, L, u, trays=("D", "E", "K", "L"), reach=2800.0):
    """Keep the arm's collision world (collide.World) to what it can reach: the trays this chapter presents and
    whatever stands within `reach` of the arm's base at its three stops (both openings, and short of Shuttle 2's
    dock), our parts included. The other trays (inside the Shuttles) and the far floor are left out. A whole-lab
    scene has tens of thousands of actors, and World.refresh asks VTK about every one of them every frame: the
    audit ran at ~10 frames a minute. Only this chapter's arm is audited (the second unit stays on its charger)."""
    import collide as CL
    import setup_lab as SL
    keep, drop = set(), set()
    for k in L.tray:
        (keep if k in trays else drop).update(CL._subtree(sc, f"tray_{k}"))
    y0 = u.pose[1] + A.ARM_LOCAL[1]
    bases = np.array([[u.pose[0] + A.ARM_LOCAL[0], y0], [SL.X2 - HM_DOCK, y0], [SL.X2, y0]])
    only, known = {}, set(sc.actors)

    def near(name, actor):
        g = sc.group_of.get(name)
        if g in drop:
            return False
        if g in keep:
            return True
        inp = actor.GetMapper().GetInput()
        if inp is None or inp.GetNumberOfPoints() == 0:
            return False
        b = np.array(inp.GetBounds()).reshape(3, 2)
        c = np.array([[b[0, i], b[1, j], b[2, k]] for i in (0, 1) for j in (0, 1) for k in (0, 1)])
        w = (sc.world(g) @ np.c_[c, np.ones(8)].T).T[:, :3]
        lo, hi = w.min(axis=0), w.max(axis=0)
        d = np.linalg.norm(np.maximum(np.maximum(lo[:2] - bases, bases - hi[:2]), 0.0), axis=1).min()
        return d < reach and lo[2] < reach + P.AMR_TOP

    for name, actor in sc.actors.items():
        if near(name, actor):
            only[name] = actor

    class FastWorld(CL.World):
        def refresh(self):
            full = self.sc.actors
            if len(full) != len(known):                     # actors added since: keep those near too
                for name in set(full) - known:
                    known.add(name)
                    if near(name, full[name]):
                        only[name] = full[name]
            self.sc.actors = only
            try:
                CL.World.refresh(self)
            finally:
                self.sc.actors = full

    sc._collide_world = FastWorld(sc)
    sc.robots = [r for r in getattr(sc, "robots", []) if r is u.robot]
    print(f"collision world: {len(only)} of {len(sc.actors)} actors", flush=True)


def rig_of(rigs, key):
    for k, r in rigs.items():
        if k.split("_", 1)[1] == key:
            return r
    raise KeyError(key)


def status(L, **kv):
    rows = dict(L.extra_gauges)
    rows.update(kv)
    L.extra_gauges = [(k, v) for k, v in rows.items() if v]
    L.gauges()


# ================================================================================================= our parts
def _cq_mesh(shape, tol=0.3):
    return lab.to_mesh(shape.val() if hasattr(shape, "val") else shape, tol, 0.15)


def caddy_parts():
    """The caddy: a block, two pockets for the 1.5 in mounts (1 mm clearance, a lead-in), and a ridge for the bar.
    Frame: its foot's centre on the cabinet top."""
    import cadquery as cq
    p = CADDY
    blk = cq.Workplane("XY").box(p["w"], p["d"], p["h"]).translate((0, 0, p["h"] / 2))
    blk = blk.edges("|Z").fillet(6)
    for key in ("hot", "steel"):
        x, y = SLOT_AT[key]
        r = MOUNT_D / 2 + 1.0
        blk = blk.cut(cq.Workplane("XY").circle(r).extrude(p["pocket"] + 1).translate((x, y, p["h"] - p["pocket"])))
        cone = cq.Solid.makeCone(r, r + 2.0, 2.0, pnt=cq.Vector(x, y, p["h"] - 2.0), dir=cq.Vector(0, 0, 1))
        blk = blk.cut(cq.Workplane("XY").add(cone))
    x, y = SLOT_AT["bar"]
    ridge = cq.Workplane("XY").box(p["ridge_w"], p["ridge_l"], p["ridge_h"]).translate(
        (x, y - 5.0, p["h"] + p["ridge_h"] / 2))
    return {"caddy": (_cq_mesh(blk), (0.94, 0.94, 0.92), 0.25), "ridge": (_cq_mesh(ridge), (0.62, 0.63, 0.66), 0.6)}


def bar_mesh() -> pv.PolyData:
    """The broken bar's upper half in its own frame: centred, its underside at z = 0, fracture to +y, grip end to -y
    (as on the VHX's carrier, r8_char.vhx)."""
    return RC.bar_half_mesh().rotate_z(180.0, inplace=False).translate((0, 25.0, 0), inplace=False)


def add_specimens(sc, u):
    """The caddy on the MiR's cabinet, and the three specimens in it: groups c_caddy, c_hot, c_steel, c_bar."""
    cab = f"{u.name}_cab"
    for name, (mesh, col, spec) in caddy_parts().items():
        sc.add(f"c_caddy/{name}", mesh, col, "c_caddy", specular=spec)
    sc.parent["c_caddy"] = cab
    sc.gmat["c_caddy"] = T((CADDY_AT[0], CADDY_AT[1], CAB_TOP))
    for grp, parts in (("c_hot", SP.hot_mount("polished")), ("c_steel", SP.steel_mount("polished"))):
        for name, (mesh, col, spec) in parts.items():
            sc.add(f"{grp}/{name}", mesh, col, grp, specular=spec)
    sc.add("c_bar/bar", bar_mesh(), RC.MATERIALS["r8c_bar"][:3], "c_bar", specular=0.3)
    for key in ("hot", "steel", "bar"):
        home(sc, key)


def home_matrix(key) -> np.ndarray:
    """A specimen's place in the caddy (caddy frame)."""
    x, y = SLOT_AT[key]
    if key == "bar":
        return T((x, y, CADDY["h"] + CADDY["ridge_h"])) @ R((0, 0, 1), 0.0)
    return T((x, y, CADDY["h"] - CADDY["pocket"]))


def home(sc, key):
    sc.parent[f"c_{key}"] = "c_caddy"
    sc.gmat[f"c_{key}"] = home_matrix(key)


def top_of(sc, grp, h) -> np.ndarray:
    """The world point on a specimen's axis, h over its base (mounts: FACE is the face)."""
    return (sc.world(grp) @ np.r_[0.0, 0.0, h, 1.0])[:3]


def cam_at(target, off, look=(0.0, 0.0, 0.0)):
    t = np.asarray(target, float)
    return [tuple(t + np.asarray(off, float)), tuple(t + np.asarray(look, float)), (0, 0, 1)]


def inst_world(sc, rig, p):
    return (sc.world(f"{rig.prefix}body") @ np.r_[p, 1.0])[:3]


def branch_q(rb, Tw, Tw_ref):
    """The IK solution for Tw in the branch of the first clear solution for Tw_ref, so a straight line from one to the
    other stays in a branch that is clear where it ends."""
    import collide
    chk = rb.checker()
    Wd = chk.snapshot()
    Tb = np.linalg.inv(rb.sc.world(rb.root)) @ Tw_ref
    for q in collide.ik_all(rb.model, Tb, rb.q):
        if not chk.collisions(q, rb.close, Wd, chk.touching(q, rb.close, Wd)):
            return rb.solve(Tw, seed=q)
    return rb.solve(Tw)


def sh(Tw, d):
    M = Tw.copy()
    M[:3, 3] = M[:3, 3] + np.asarray(d, float)
    return M


# ================================================================================================= the movie
def movie():
    import setup_lab as SL
    sc, L, F, rigs, u = build()
    rb = u.robot
    add_specimens(sc, u)
    fast_collisions(sc, L, u)
    sem, nano, pip = rig_of(rigs, "sem"), rig_of(rigs, "nanoindenter"), rig_of(rigs, "pip")
    hv, vhx = rig_of(rigs, "hardness"), rig_of(rigs, "vhx")
    PARK = np.radians(A.PARK_DEG)
    sc.apply()
    st = {"lbl": "7/7", "cap": ""}

    # ------------------------------------------------------------------ helpers
    def say(label, cap):
        st["lbl"], st["cap"] = label, cap

    def go(Tw=None, q=None, secs=1.6, cam=None, labels=(), grip=None, extra=None, hold=0.05):
        f = rb.joint_to(Tw=Tw) if Tw is not None else rb.joint_to(q)
        sc.step(st["lbl"], st["cap"], secs, RB.both(f, rb.grip_to(grip) if grip is not None else None, extra),
                hold=hold, cam_to=cam, labels=labels)

    def go_to(Tw, ref, secs=1.6, cam=None, labels=(), grip=None, extra=None, hold=0.05):
        go(q=branch_q(rb, Tw, ref), secs=secs, cam=cam, labels=labels, grip=grip, extra=extra, hold=hold)

    def lin(Tw, secs=0.8, extra=None, hold=0.05, cam=None):
        sc.step(st["lbl"], st["cap"], secs, RB.both(rb.line_to(Tw), extra), hold=hold, cam_to=cam)

    def grip(c, secs=0.4):
        sc.step(st["lbl"], st["cap"], secs, rb.grip_to(c), hold=0.05)

    def wait(secs, update=None, hold=0.1, cam=None, labels=(), still=False):
        sc.step(st["lbl"], st["cap"], secs, update, hold=hold, cam_to=cam, labels=labels, still=still)

    def park(secs=1.4, cam=None, labels=(), extra=None):
        go(q=PARK, secs=secs, cam=cam, labels=labels, extra=extra)

    def clock(what, t0, t1, unit="min"):
        def up(u):
            t = t0 + (t1 - t0) * u
            if unit == "h":
                sc.clock = (what, f"{int(t // 60):d} h {int(t % 60):02d} min")
            else:
                sc.clock = (what, f"{int(t):d}:{int(round((t % 1) * 60)) % 60:02d}")
        return up

    def show_panel(key, secs=4.5, cap=None, hold=1.2, still=False):
        """Fade a data panel in, hold it, and fade it out."""
        sc.panel = key

        def fade_in(u):
            sc.panel_a = u
        wait(0.6, fade_in, hold=0.0)
        wait(secs, None, hold=hold, still=still)

        def fade_out(u):
            sc.panel_a = 1.0 - u
        wait(0.5, fade_out, hold=0.0)
        sc.panel = None

    def pick_mount(grp, spin, cam=None, labels=(), secs=1.8):
        """Take a mount (c_hot or c_steel) from wherever it is, top-down."""
        Tg = A.down(top_of(sc, grp, FACE + TCP_UP), spin=spin)
        go_to(sh(Tg, (0, 0, 90)), Tg, secs=secs, grip=OPEN, cam=cam, labels=labels)
        lin(Tg, 0.7)
        grip(GRIP_MOUNT)
        rb.grasp(grp)
        lin(sh(Tg, (0, 0, 90)), 0.7)

    def place_mount(target_base, parent, spin, cam=None, labels=(), secs=2.0, approach=90.0):
        """Set the held mount down with its base at target_base (world) and leave it with `parent`."""
        Tg = A.down(np.asarray(target_base, float) + (0, 0, FACE + TCP_UP), spin=spin)
        go_to(sh(Tg, (0, 0, approach)), Tg, secs=secs, cam=cam, labels=labels)
        lin(Tg, 0.8)
        grip(OPEN)
        rb.release(parent)
        lin(sh(Tg, (0, 0, approach)), 0.7)

    def drive_to(x1, label, cap, cam=None, hold=0.2):
        """The MiR250 along the dock line from rest to rest at 0.3 m/s^2 (props.ramp_frac)."""
        x0, y0, hd = u.pose
        dist = abs(x1 - x0)

        def up(v):
            f = P.ramp_frac(P.unease(v), dist, MIR_SPEED)
            u.set((x0 + (x1 - x0) * f, y0, hd))
            if rb.held is not None:
                rb.set()
        sc.step(label, cap, max(1.2, P.ramp_secs(dist, MIR_SPEED)), up, hold=hold, cam_to=cam)

    def world_of(rig, piece, p):
        """A point given in the instrument's frame, on one of its moving pieces (as the piece is now)."""
        return (sc.world(f"{rig.prefix}{piece}") @ np.r_[p, 1.0])[:3]

    # ------------------------------------------------------------------ 0. the lab, the specimens
    sc.cam = list(CAM_LAB)
    status(L, Arm="UR10e on MiR250, at Shuttle 1", Caddy="hot mount, steel mount, bar half")
    say("7/7", "Chapter 7: characterizing the build. The MiR250 brings what chapters 5 and 6 made from the sample store "
               "on tray J, in a caddy on its cabinet: the coupon hot-mounted in conductive phenolic, the slice in a "
               "steel mount, and half of a broken tensile bar.")
    wait(4.2, None, hold=0.6)
    hot_w = top_of(sc, "c_hot", FACE)
    CAM_CADDY = cam_at(hot_w, (330, -620, 420), (60, 0, -10))
    say("Specimens", "Two specimens, two mounts. The conductive hot mount (carbon-filled phenolic): the SEM's path to "
                     "ground, and micro-Vickers. The steel mount: the slice on steel, nothing soft under it, for "
                     "nanoindentation and PIP.")
    wait(1.6, None, hold=3.0, cam=CAM_CADDY,
         labels=[("conductive hot mount, 1.5 in", tuple(top_of(sc, "c_hot", FACE + 10)), (0.20, 0.30)),
                 ("steel mount, the slice on steel", tuple(top_of(sc, "c_steel", FACE + 10)), (0.48, 0.20)),
                 ("bar half, chapter 5's", tuple(top_of(sc, "c_bar", 8)), (0.80, 0.34))])

    # ------------------------------------------------------------------ 1. tray D: the SEM
    sem.v.update(drawer=0.0)
    sem.apply()
    say("SEM", "Tray D comes down to Shuttle 1's opening: the Hitachi TM4000PlusII SEM, with the AZtecOne EDS "
               "analyser beside it, and the MiniFlex.")
    status(L, Arm="parked")
    L.fetch("D", st["lbl"], st["cap"], fast=0.5, cam=CAM_LAB, hold=0.2)
    gS = __import__("instruments")._tm4000(__import__("instruments").SEM)
    st_z = __import__("instruments").SEM["front_z0"] + 62.0
    cup_base = (0.0, gS["ys"] + RC.SEM_CUP["dy"], st_z + RC.SEM_CUP["lift"] + RC.SEM_CUP["floor"])
    sw = lambda q: inst_world(sc, sem, q)                          # noqa: E731
    CAM_SEM = cam_at(sw((0, -330, 200)), (-900, -1500, 650))
    say("SEM", "EVAC/AIR vents the chamber and the door comes out with the stage on it. In the stage's socket: a "
               "holder cup for 1.5 in mounts with a spring plunger through its side (ours).")
    status(L, SEM="venting, door out")
    wait(1.6, sem.move({"drawer": (0.0, 1.0)}), cam=CAM_SEM,
         labels=[("Hitachi TM4000PlusII", tuple(sw((0, 0, 600))), (0.22, 0.20)),
                 (RC.AZTEC.split(",")[0] + ": EDS analyser", tuple(sw((RC.I.SEM["W"] / 2 + 190, -90, 330))),
                  (0.78, 0.20))])
    say("SEM", "The arm sets the hot mount in the cup. The plunger presses it against the wall: coupon -> "
               "carbon-filled phenolic -> cup -> stage, the path to ground (Sterling's point: a bare puck has none).")
    status(L, Arm="loading the SEM")
    pick_mount("c_hot", spin=180.0)
    place_mount(world_of(sem, "drawer", cup_base), f"{sem.prefix}drawer", spin=180.0,
                labels=[("holder cup + spring plunger", tuple(world_of(sem, "drawer", cup_base) + (0, 0, 15)),
                         (0.30, 0.78))])
    park(1.4)
    status(L, Arm="parked", SEM="pumping down")
    say("SEM", "Door in, EVAC: about three minutes to vacuum. Then backscattered-electron images of the polished "
               "section: the melt pools, any porosity.")
    wait(1.4, RB.both(sem.move({"drawer": (1.0, 0.0)}), clock("TM4000", 0.0, 0.2)), cam=CAM_SEM)
    wait(1.4, clock("TM4000", 0.2, 3.0))
    status(L, SEM="BSE imaging")
    wait(1.2, clock("TM4000", 3.0, 9.0))
    show_panel("sem", 4.2)
    say("SEM", "EDS: the built-in detector and its AZtecOne analyser map Al, Si and Mg across the section.")
    status(L, SEM="EDS mapping")
    wait(1.0, clock("TM4000", 9.0, 24.0))
    show_panel("eds", 4.0)
    sc.clock = None
    say("SEM", "Vented, door out; the mount goes back to the caddy. Tray D goes back up.")
    status(L, SEM="vented, door out", Arm="unloading the SEM")
    wait(1.4, sem.move({"drawer": (0.0, 1.0)}))
    pick_mount("c_hot", spin=180.0)
    caddy_hot = (sc.world("c_caddy") @ np.r_[SLOT_AT["hot"][0], SLOT_AT["hot"][1], CADDY["h"] - CADDY["pocket"], 1.0])
    place_mount(caddy_hot[:3], "c_caddy", spin=180.0, cam=CAM_LAB)
    park(1.4, extra=sem.move({"drawer": (1.0, 0.0)}))
    status(L, Arm="parked", SEM="")
    L.store("D", st["lbl"], st["cap"], fast=0.5, hold=0.1, cam=CAM_LAB)

    # ------------------------------------------------------------------ 2. tray E: the iMicro
    NP = __import__("instruments").NANO
    sz = NP["feet"] + 70 + NP["stage_z"] - 60
    ox = NP["scope_x"]
    nano_base = (ox, 0.0, sz - 6 + RC.NANO_HOLD["floor"])
    nw = lambda q: inst_world(sc, nano, q)                         # noqa: E731
    CAM_NANO = cam_at(nw((0, -150, 250)), (-850, -1500, 760))
    say("iMicro", "Tray E comes down: the Plastometrex PIP, the KLA iMicro nanoindenter and the Mastersizer.")
    L.fetch("E", st["lbl"], st["cap"], fast=0.5, cam=CAM_LAB, hold=0.2)
    say("iMicro", "The iMicro's hood lifts and its XY stage runs out to the load position, clear of the objective.")
    status(L, iMicro="hood up, stage out")
    wait(1.6, nano.move({"lid": (0.0, 1.0), "carriage": (0.0, 1.0)}), cam=CAM_NANO,
         labels=[("KLA iMicro nanoindenter", tuple(nw((0, 0, 560))), (0.22, 0.20))])
    say("iMicro", "The steel mount into the stage's steel cup, clamped by a spring plunger: steel on steel.")
    status(L, Arm="loading the iMicro")
    pick_mount("c_steel", spin=180.0)
    place_mount(world_of(nano, "stage", nano_base), f"{nano.prefix}stage", spin=180.0)
    park(1.4)
    status(L, Arm="parked", iMicro="indenting")
    say("iMicro", "Hood down (drawn see-through). The stage carries the slice under the microscope objective, which "
                  "finds the polished face, then 100 mm across under the indenter head.")
    wait(1.6, RB.both(nano.move({"lid": (1.0, 0.0), "carriage": (1.0, 0.0), "~cabinet": (0.0, 1.0),
                                 "~lid": (0.0, 1.0)}), clock("iMicro", 0.0, 2.0)))
    wait(1.4, RB.both(nano.move({"stage": (0.0, 1.0)}), clock("iMicro", 2.0, 4.0)))
    say("iMicro", "The Berkovich tip comes down onto the surface and is driven in to 500 nm: 25 indents in a 5 x 5 "
                  "grid, 20 um apart, hardness and modulus from each unloading curve (Oliver-Pharr).")
    wait(1.4, RB.both(nano.move({"tip": (0.0, 1.0)}), clock("iMicro", 4.0, 6.0)))
    wait(1.6, RB.both(nano.move({"tip": (1.0, 0.0)}), clock("iMicro", 6.0, 42.0)))
    wait(1.2, RB.both(nano.move({"stage": (1.0, 0.0)}), clock("iMicro", 42.0, 45.0)))
    show_panel("nano", 4.4)
    sc.clock = None
    say("iMicro", "Hood up, stage out; the arm takes the steel mount on to the PIP.")
    status(L, iMicro="done", Arm="unloading the iMicro")
    wait(1.4, nano.move({"lid": (0.0, 1.0), "carriage": (0.0, 1.0), "~cabinet": (1.0, 0.0), "~lid": (1.0, 0.0)}))
    pick_mount("c_steel", spin=180.0)

    # ------------------------------------------------------------------ 3. tray E: the PIP
    gP = __import__("instruments")._plx(__import__("instruments").PIP)
    pip_base = (0.0, gP["yc"], gP["stz"] + RC.PIP_SLIDE["t"])
    pw = lambda q: inst_world(sc, pip, q)                          # noqa: E731
    CAM_PIP = cam_at(pw((0, -250, 160)), (-700, -1300, 600))
    say("PIP", "The PIP's working bay is about 130 mm tall, with the indenter 7 mm over the sample: too tight for a "
               "gripper. Its loading slide (ours) runs a steel plate out to the front.")
    status(L, PIP="slide out")
    go(q=PARK, secs=1.4, cam=CAM_PIP, extra=RB.both(pip.move({"slide": (0.0, 1.0)}),
                                                      nano.move({"lid": (1.0, 0.0), "carriage": (1.0, 0.0)})),
       labels=[("Plastometrex PLX-Benchtop (PIP)", tuple(pw((0, 0, 720))), (0.30, 0.18))])
    place_mount(world_of(pip, "slide", pip_base), f"{pip.prefix}slide", spin=180.0,
                labels=[("loading slide (ours)", tuple(world_of(pip, "slide", (0, gP["yc"], gP["stz"]))),
                         (0.20, 0.80))])
    park(1.4)
    say("PIP", "Slide in: the plate sits on the platen, metal from the slice down to the load cell. The 1 mm ball is "
               "pressed in; the profilometer maps the indent's shape.")
    status(L, Arm="parked", PIP="indenting")
    wait(1.6, RB.both(pip.move({"slide": (1.0, 0.0)}), clock("PIP", 0.0, 0.5)))
    wait(1.4, RB.both(pip.move({"head": (0.0, 1.0)}), clock("PIP", 0.5, 1.0)))
    wait(1.4, RB.both(pip.move({"head": (1.0, -0.3), "stylus": (0.0, 0.33)}), clock("PIP", 1.0, 1.5)))
    wait(1.8, RB.both(pip.move({"stylus": (0.33, 0.67)}), clock("PIP", 1.5, 3.0)))
    wait(1.2, RB.both(pip.move({"stylus": (0.67, 1.0), "head": (-0.3, 0.0)}), clock("PIP", 3.0, 3.5)))
    say("PIP", "CORSICA fits a stress-strain curve to the indent's profile by finite elements, in minutes.")
    status(L, PIP="fitting the curve")
    wait(0.8, clock("PIP", 3.5, 6.0))
    show_panel("pip", 4.4)
    sc.clock = None
    say("PIP", "Slide out; the steel mount goes back to the caddy. Tray E goes back up.")
    status(L, PIP="done", Arm="unloading the PIP")
    wait(1.4, pip.move({"slide": (0.0, 1.0)}))
    pick_mount("c_steel", spin=180.0)
    caddy_st = (sc.world("c_caddy") @ np.r_[SLOT_AT["steel"][0], SLOT_AT["steel"][1], CADDY["h"] - CADDY["pocket"],
                                             1.0])
    place_mount(caddy_st[:3], "c_caddy", spin=180.0, cam=CAM_LAB)
    park(1.4, extra=pip.move({"slide": (1.0, 0.0)}))
    status(L, Arm="parked", PIP="", iMicro="")
    L.store("E", st["lbl"], st["cap"], fast=0.5, hold=0.1, cam=CAM_LAB)

    # ------------------------------------------------------------------ 4. to Shuttle 2
    x2 = SL.X2
    say("Shuttle 2", "The MiR250 drives along to Shuttle 2's opening, at its 0.3 m/s^2, and stops 300 mm short of "
                     "its usual dock, nearer the HM-220 at the tray's left end.")
    status(L, Arm="UR10e on MiR250, to Shuttle 2")
    drive_to(x2 - HM_DOCK, st["lbl"], st["cap"], cam=[(x2 + 6800, -9800, 5200), (x2 - 600, -1500, 1100), (0, 0, 1)])
    status(L, Arm="UR10e on MiR250, at Shuttle 2")

    # ------------------------------------------------------------------ 5. tray L: micro-Vickers
    import instruments_r7 as R7
    pH = R7.HM
    ax, ay = pH["ax"]
    hv_base = (ax, ay, 252.0 + RC.HM_HOLD["plate"])
    hw = lambda q: inst_world(sc, hv, q)                           # noqa: E731
    CAM_HV = cam_at(hw((0, -260, 300)), (-700, -1250, 560))
    say("Vickers", "Tray L comes down at Shuttle 2: the Mitutoyo HM-220 micro-Vickers tester, and the zwickiLine.")
    L.fetch("L", st["lbl"], st["cap"], fast=0.5, cam=CAM_LAB, hold=0.2)
    say("Vickers", "Its loading slide (ours) runs the mount holder out from under the turret; the arm sets the hot "
                   "mount on it, against the V-block.")
    status(L, **{"HM-220": "slide out", "Arm": "loading the HM-220"})
    wait(1.4, hv.move({"slide": (0.0, 1.0)}), cam=CAM_HV,
         labels=[("Mitutoyo HM-220 micro-Vickers", tuple(hw((0, 0, 620))), (0.24, 0.18))])
    pick_mount("c_hot", spin=180.0)
    place_mount(world_of(hv, "slide", hv_base), f"{hv.prefix}slide", spin=180.0)
    park(1.4)
    say("Vickers", "Slide in. The turret swings the Vickers indenter over the coupon and presses, HV0.1; the 50x "
                   "objective comes back and the camera measures both diagonals. A row across the coupon, unattended.")
    status(L, **{"Arm": "parked", "HM-220": "indenting, HV0.1"})
    tl_keys = [k for k in hv.inst.joints if k in ("stage_x", "turret", "indenter") or k.startswith("dent")]
    wait(1.4, RB.both(hv.move({"slide": (1.0, 0.0)}), clock("HM-220", 0.0, 0.5)))
    wait(6.0, RB.both(hv.move({k: (0.0, 1.0) for k in tl_keys}), clock("HM-220", 0.5, 12.0)))
    show_panel("hv", 4.4)
    sc.clock = None
    say("Vickers", "Slide out; the mount goes back to the caddy. Tray L goes back up.")
    status(L, **{"HM-220": "done", "Arm": "unloading the HM-220"})
    wait(1.4, hv.move({"slide": (0.0, 1.0)}))
    pick_mount("c_hot", spin=180.0)
    place_mount(caddy_hot_now(sc), "c_caddy", spin=180.0, cam=CAM_LAB)
    park(1.4, extra=hv.move({"slide": (1.0, 0.0)}))
    status(L, **{"Arm": "parked", "HM-220": ""})
    L.store("L", st["lbl"], st["cap"], fast=0.5, hold=0.1, cam=CAM_LAB)

    # ------------------------------------------------------------------ 6. tray K: the VHX, the bar in 3-D
    import instruments_char as IC
    q = IC.VHX_LOOK
    ys = IC.VHX_STAGE_Y
    zs = q["stage_z"] + q["plate_t"]
    c = RC.VHX_CARRIER
    bar_base = (0.0, ys, zs + 1.0 + c["t"] + c["ped_h"])
    vw = lambda p_: inst_world(sc, vhx, p_)                        # noqa: E731
    CAM_VHX = cam_at(vw((0, -120, 260)), (-640, -1150, 520))
    say("VHX", "Tray K comes down: the glovebox and the Keyence VHX-7000, remoted in through a PiKVM. The MiR250 moves "
               "back to its dock.")
    status(L, Arm="UR10e on MiR250, at Shuttle 2")
    drive_to(x2, st["lbl"], st["cap"], hold=0.0)
    L.fetch("K", st["lbl"], st["cap"], fast=0.5, cam=CAM_LAB, hold=0.2)
    say("VHX", "The ring light is 25 mm over the focal point, too close for a gripper: the stage's loading slide "
               "(ours) runs its carrier out to the front, and the arm sets the bar on its narrow pedestal.")
    status(L, VHX="carrier out", Arm="loading the VHX")
    wait(1.4, vhx.move({"carrier": (0.0, 1.0)}), cam=CAM_VHX,
         labels=[("Keyence VHX-7000, free-angle head", tuple(vw((0, -40, 700))), (0.26, 0.18))])
    Tb = A.down(top_of(sc, "c_bar", RC.BAR_T + BAR_UP), spin=180.0)
    go_to(sh(Tb, (0, 0, 90)), Tb, secs=1.8, grip=OPEN, cam=CAM_LAB)
    lin(Tb, 0.7)
    grip(GRIP_BAR)
    rb.grasp("c_bar")
    lin(sh(Tb, (0, 0, 90)), 0.7)
    target = world_of(vhx, "carrier", bar_base)
    Tp = A.down(target + (0, 0, RC.BAR_T + BAR_UP), spin=180.0)
    go_to(sh(Tp, (0, 0, 90)), Tp, secs=2.0, cam=CAM_VHX)
    lin(Tp, 0.8)
    grip(OPEN)
    rb.release(f"{vhx.prefix}carrier")
    lin(sh(Tp, (0, 0, 90)), 0.7)
    park(1.4)
    say("VHX", "Carrier in. The free-angle head tilts about the focal point (eucentric: the view stays on the bar) "
               "while the stage turns; depth composition at every view.")
    status(L, Arm="parked", VHX="tilt series, top side")
    wait(1.4, vhx.move({"carrier": (1.0, 0.0)}))
    wait(3.4, RB.both(vhx.move({"head": (0.0, 1.0), "turntable": (0.0, 0.5)}), clock("VHX", 0.0, 6.0)))
    wait(3.0, RB.both(vhx.move({"head": (1.0, -0.45), "turntable": (0.5, 0.0)}), clock("VHX", 6.0, 12.0)))
    wait(1.6, RB.both(vhx.move({"head": (-0.45, 0.0), "focus": (0.0, 1.0)}), clock("VHX", 12.0, 14.0)))
    sc.clock = None
    flip_bar(sc, rb, vhx, st, go_to, lin, grip, park, wait, status, L, CAM_VHX)
    say("VHX", "The series again, on the underside: with one turn-over, every face of the bar and its fracture "
               "surface, as one 3-D model.")
    status(L, Arm="parked", VHX="tilt series, underside")
    wait(1.4, vhx.move({"carrier": (1.0, 0.0)}))
    wait(3.0, RB.both(vhx.move({"head": (0.0, -0.8), "turntable": (0.0, -0.5)}), clock("VHX", 14.0, 20.0)))
    wait(2.2, RB.both(vhx.move({"head": (-0.8, 0.0), "turntable": (-0.5, 0.0)}), clock("VHX", 20.0, 25.0)))
    show_panel("vhx", 4.4)
    sc.clock = None
    say("VHX", "Carrier out; the bar goes back to the caddy. Tray K goes back up.")
    status(L, VHX="done", Arm="unloading the VHX")
    wait(1.4, vhx.move({"carrier": (0.0, 1.0)}))
    Tb = A.down(top_of(sc, "c_bar", RC.BAR_T + BAR_UP), spin=180.0)
    go_to(sh(Tb, (0, 0, 90)), Tb, secs=1.8, grip=OPEN)
    lin(Tb, 0.7)
    grip(GRIP_BAR)
    rb.grasp("c_bar")
    lin(sh(Tb, (0, 0, 90)), 0.7)
    bar_home = sc.world("c_caddy") @ home_matrix("bar")
    Tp = A.down(bar_home[:3, 3] + (0, 0, RC.BAR_T + BAR_UP), spin=180.0)
    go_to(sh(Tp, (0, 0, 90)), Tp, secs=2.0, cam=CAM_LAB)
    lin(Tp, 0.8)
    grip(OPEN)
    rb.release("c_caddy")
    lin(sh(Tp, (0, 0, 90)), 0.7)
    park(1.4, extra=vhx.move({"carrier": (1.0, 0.0)}))
    status(L, Arm="parked", VHX="")
    L.store("K", st["lbl"], st["cap"], fast=0.5, hold=0.1, cam=CAM_LAB)

    # ------------------------------------------------------------------ 7. the data
    say("Data", "What the chapter measured, and what is real: the SEM inset is the lab's own atomized powder; the "
                "section, the EDS, the hardness and the VHX map are illustrative, the nanoindentation computed. No "
                "section of the lab's prints has been imaged yet.")
    status(L, Arm="parked", Caddy="the specimens, to the sample store")
    sc.panel = "grid"

    def grid_in(v):
        sc.panel_a = v
    wait(0.8, grid_in, hold=0.0)
    wait(1.0, None, hold=6.0, still=True)
    return finish(sc, rb)


def caddy_hot_now(sc) -> np.ndarray:
    """The hot mount's pocket in the caddy, in the world, where the caddy is now."""
    return (sc.world("c_caddy") @ np.r_[SLOT_AT["hot"][0], SLOT_AT["hot"][1], CADDY["h"] - CADDY["pocket"], 1.0])[:3]


def flip_bar(sc, rb, vhx, st, go_to, lin, grip, park, wait, status, L, cam):
    """The arm turns the bar over on the carrier: the carrier out, a level grasp on the grip end from the front, up
    25 mm, a 180 deg roll of the wrist about the bar's axis, down, let go."""
    status(L, VHX="carrier out", Arm="turning the bar over")
    st["lbl"], st["cap"] = "VHX", ("Carrier out. The arm takes the bar by its grip end, lifts it clear of the "
                                   "pedestal, rolls it over about its long axis and sets it back down.")
    wait(1.4, vhx.move({"carrier": (0.0, 1.0)}), cam=cam)
    bw = sc.world("c_bar")
    end = (bw @ np.r_[0.0, -25.0 + 10.0, RC.BAR_T / 2, 1.0])[:3]         # 10 mm in from the grip end, mid-height
    along = bw[:3, :3] @ np.array([0.0, 1.0, 0.0])                        # towards the fracture
    Tl = A.level(end, toward=tuple(along), spin=0.0)
    back = sh(Tl, -along * 80.0)
    go_to(back, Tl, secs=2.0)
    lin(Tl, 0.8)
    grip(GRIP_BAR)
    rb.grasp("c_bar")
    up = sh(Tl, (0, 0, 25.0))
    lin(up, 0.6)
    lin(A.level(up[:3, 3], toward=tuple(along), spin=180.0), 1.4)
    lin(A.level(Tl[:3, 3], toward=tuple(along), spin=180.0), 0.6)
    grip(0.55)
    rb.release(f"{vhx.prefix}carrier")
    lin(sh(A.level(Tl[:3, 3], toward=tuple(along), spin=180.0), -along * 80.0), 0.7)
    park(1.4)


def finish(sc, rb):
    sc.panel = None
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm", flush=True)
    return sc.save()


if __name__ == "__main__":
    print(movie(), flush=True)
