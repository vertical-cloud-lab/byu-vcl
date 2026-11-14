"""The alloy route, chapter 4: the powder, checked (#303, round 8).

    xvfb-run -a python3 alloy_powder.py             # -> out/mp4/alloy_powder.mp4, out/alloy_powder.gif, .json, still
    PREVIEW=1 xvfb-run -a python3 alloy_powder.py   # the last frame of each sub-step -> /tmp/preview_alloy_powder.png
    ARM_AUDIT=1 xvfb-run -a python3 alloy_powder.py # no render: every frame collision-checked -> out/collisions/

While the plate prints (chapter 3), a retained sample of the sieved 20-63 um cut goes round the trays, in the whole
lab as the set-up movie leaves it (``setup_lab.build``: both Shuttles, every tray loaded). The MiR250 + UR10e docks at
Shuttle 1; the VLM brings each tray to its opening only when it is needed:

* **Tray D, the prep station and the MiniFlex.** Sterling on PR #318: "for powder XRD, you didn't show anything related
  to the sample prep for it, which is actually kind of an art". The arm sifts the powder through a mesh-capped vial
  onto a zero-background Si holder (A-Lab's way, Szymanski 2024), dusts an SEM stub and fills an XRF cup from the
  same vial; a blade strikes the holder's powder off flush with its reference plane, no pressing; nothing is ground,
  since milling ductile atomized powder cold-welds spheres into flakes (Edison, ``notes/edison_r8.md``). The holder
  goes into the Rigaku MiniFlex, whose door is drawn see-through from the start and whose goniometer stays still
  until the door is shut and the X-rays are on; the pattern is computed, and badged so. The stub goes into the
  TM4000PlusII in a 1.5 in carrier, so the same spring-plunger cup that grounds the mounts grounds it. The SEM images
  are the lab's own atomized Al 4047 (c3k0n5, DAL #157), badged REAL.
* **Tray E, the Mastersizer 3000 + Aero S.** A few grams into the Aero S, then the optical bench in cutaway: the laser,
  the beam converging through the cell, light scattered narrow by large particles and wide by small ones, the
  detector's arcs, and the size distribution (computed from the SEM count, and badged so).
* **Tray M on Shuttle 2, the Bruker S2 PUMA.** The MiR drives to the second Shuttle at the MiR250's 0.3 m/s^2. The cup
  goes in through a hatch in the hood's top onto the chamber's lift ring (Bruker's Automation version takes samples
  "into the sample chamber directly"; the hatch is our assumption), the ring lowers it over the tube and the detector,
  and the spectrum comes up, badged ILLUSTRATIVE.

Every arm move is a straight line of the grasp point or a joint move planned round whatever is in the way
(``robot.py``, ``collide.py``). ``notes/alloy_powder.md`` says what is measured, computed, illustrative and assumed.
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw

import scene
from scene import AUDIT, CLEAN, FPS, OUT, PREVIEW, T, R, S, font  # noqa: E402

import animate as A                   # noqa: E402
import instruments as I               # noqa: E402
import lab                            # noqa: E402
import line                           # noqa: E402
import props as P                     # noqa: E402
import r8_powder as RP                # noqa: E402
import r8_powder_data as DATA         # noqa: E402
import robot as RB                    # noqa: E402
import setup_lab as SL                # noqa: E402
import tour                           # noqa: E402
import vlm as V                       # noqa: E402
import warehouse as W                 # noqa: E402

NAME = "alloy_powder"
TITLE = "Vertical cloud lab: the alloy route 4/7, the powder checked"
HERE = Path(__file__).resolve().parent
X2 = SL.X2
DOCK1 = W.dock_pose("vlm")                       # (0, -1932, 0): Shuttle 1's dock
DOCK2 = (X2 - 450.0, DOCK1[1], 0.0)              # Shuttle 2: 450 mm left of its dock's centre, in front of the XRF
START_X = 2100.0                                 # the MiR comes in from the right, from the Aconity's side
MIR_V = 1500.0                                   # mm/s at most, with the 0.3 m/s^2 ramps (props.ramp_secs)


def grip_for(d: float) -> float:
    """2F-85 closure on a part d mm across (pads 28 mm apart at 0.70; 90 mm per unit, as alloy_characterize)."""
    return 0.70 + (28.0 - d) / 90.0


GRIP_VIAL = A.GRIP_VIAL
GRIP_FIN = grip_for(RP.ZBH["fin_w"])
GRIP_PUCK = grip_for(RP.PREP["puck_d"])
GRIP_CUP = grip_for(RP.PREP["cup_d"])
VIAL_TCP = 50.0                      # the vial held 50 mm up its side (animate's buffer pick): 11 mm under its rim
CAP_OUT = 2.0                        # the mesh cap stands 2 mm proud of the rim
LEVEL0 = 19.0                        # mm of powder in the vial: about 15 g of Al 4047 poured at about 1.6 g/cm3


# ================================================================================================= the overlays
class Overlays:
    """The data panels (r8_powder_data's PNGs) at the top right and an instrument clock, drawn over every frame."""

    def __init__(self, sc):
        self.sc, self.key, self.a, self.clock = sc, None, 0.0, None
        self.cache: dict[str, Image.Image] = {}
        base = sc.overlay

        def ov(img, scale, anchors):
            img = base(img, scale, anchors)
            if CLEAN:
                return img
            if self.key and self.a > 0.02:
                self._panel(img)
            if self.clock:
                self._clock(img)
            return img
        sc.overlay = ov

    def _panel(self, img):
        if self.key not in self.cache:
            self.cache[self.key] = DATA.panel(self.key).convert("RGBA")
        pan = self.cache[self.key]
        W_, H_ = img.size
        w = int(0.46 * W_)
        h = int(w * pan.height / pan.width)
        p = pan.resize((w, h), Image.LANCZOS)
        a = p.getchannel("A").point(lambda v: int(v * min(1.0, self.a) * 0.97))
        p.putalpha(a)
        img.paste(p, (W_ - w - int(0.012 * W_), int(0.068 * H_)), p)

    def _clock(self, img):
        W_, H_ = img.size
        k = W_ / 1280
        s = max(k, 0.8)
        what, txt = self.clock
        d = ImageDraw.Draw(img, "RGBA")
        f1, f2 = font(13 * s), font(24 * s, bold=True, mono=True)
        w = max(d.textlength(what, font=f1), d.textlength(txt, font=f2)) + 24 * k
        x1, y1 = W_ - 14 * k, H_ - 150 * k
        d.rounded_rectangle((x1 - w, y1 - 56 * s, x1, y1), 6 * k, fill=(20, 24, 34, 225))
        d.text((x1 - w + 12 * k, y1 - 52 * s), what, font=f1, fill=(190, 200, 215))
        d.text((x1 - w + 12 * k, y1 - 34 * s), txt, font=f2, fill=(255, 255, 255))


# ================================================================================================= the scene
def _rig(rigs, key):
    return next(r for name, r in rigs.items() if name.split("_", 1)[1] == key)


def _members(sc, group):
    return [n for n, g in sc.group_of.items() if g == group]


def _restore(sc, rig, pieces):
    """Pieces setup_lab.build hid (an instrument's props) back into the rig, so its fade joints show them."""
    for pc in pieces:
        rig.names[pc] = _members(sc, f"{rig.prefix}{pc}")


def _hide(sc, rig, pieces):
    for pc in pieces:
        for n in rig.names.pop(pc, []) or _members(sc, f"{rig.prefix}{pc}"):
            sc.alpha[n] = 0.0
            sc.base_alpha[n] = 0.0


def _add_cq(sc, group, parts: dict, tol=0.25):
    """{name: (cq shape, material)} -> actors in `group`."""
    names = []
    for nm, (shape, mat) in parts.items():
        val = shape.val() if hasattr(shape, "val") else shape
        r, g, b, a, spec = tour.MATS[mat]             # every module's MATERIALS (tour._modules merges them)
        n = f"{group}/{nm}"
        sc.add(n, lab.to_mesh(val, tol, 0.2), (r, g, b), group, opacity=a, specular=spec)
        names.append(n)
    return names


def build():
    data = lab.meshes()
    idata = SL.load_all()
    sc, L, F, items, rigs, units, util, ulabel, vp = SL.build(data, idata, name=NAME, title=TITLE)
    SL.add_bay_cams(sc)
    u = units[0]
    u.set((START_X, DOCK1[1], 0.0))
    L.robot = u.robot
    L.amr_group = f"{u.name}_cab"
    L.units, L.items, L.floor = units, items, F
    # VLAB_ONLY_TRAYS=DEM (setup_lab.build) loads only the trays this chapter presents; the cladding is then opaque, as
    # on a real Kardex, so the trays left empty are never seen. Unset, every tray is loaded and the cladding see-through.
    L.skin(0.0 if os.environ.get("VLAB_ONLY_TRAYS") else 1.0)(1.0)
    L.show_gauges = True
    L.extra_gauges = []
    sc.intro = 0.8
    ov = Overlays(sc)
    R_ = dict(xrd=_rig(rigs, "xrd"), sem=_rig(rigs, "sem"), ms=_rig(rigs, "mastersizer"), xrf=_rig(rigs, "xrf"),
              prep=_rig(rigs, "pxrd_prep"))
    _restore(sc, R_["xrd"], ("ibeam", "dbeam", "glow"))
    _restore(sc, R_["ms"], ("beam", "powder", "arcs_lit", "scat_large", "scat_small"))
    _restore(sc, R_["xrf"], ("beam",))
    for rig, pcs in ((R_["xrd"], ("ibeam", "dbeam", "glow")), (R_["ms"], ("beam", "powder", "arcs_lit", "scat_large",
                                                                           "scat_small")), (R_["xrf"], ("beam",))):
        for pc in pcs:
            rig.v[pc] = 0.0
        rig.apply()
    # the Mastersizer's falling grains (a path joint): shown by hand, only while the powder runs
    ms_grains = _members(sc, f"{R_['ms'].prefix}grains")
    for n in ms_grains:
        sc.alpha[n] = 0.0
    # the prep station's stock as our own groups, so they can move: the holder, the stub carrier, the XRF cup
    prep = R_["prep"]
    _hide(sc, prep, ("zbh", "stub_puck", "xrf_cup"))
    body = f"{prep.prefix}body"
    f = RP.prep_frames()
    _add_cq(sc, "p_zbh", RP.zbh_parts())
    sc.parent["p_zbh"], sc.gmat["p_zbh"] = body, T(f["zbh"])
    _add_cq(sc, "p_puck", RP.stub_puck_parts())
    sc.parent["p_puck"], sc.gmat["p_puck"] = body, T(f["puck"])
    _add_cq(sc, "p_cup", RP.xrf_cup_parts())
    sc.parent["p_cup"], sc.gmat["p_cup"] = body, T(f["cup"])
    # the powder: a mound on the holder while it is sifted on, then the struck-off face; the excess in the trough; the
    # dusting on the stub; the XRF cup's fill
    dome = pv.Sphere(radius=1.0, center=(0, 0, 0), theta_resolution=32, phi_resolution=16, start_phi=0.0,
                     end_phi=90.0).triangulate()
    z = RP.ZBH
    sc.add("p_heap/mound", dome, P.POWDER, "p_heap", specular=0.1)
    sc.parent["p_heap"] = "p_zbh"
    _add_cq(sc, "p_flat", {"face": (RP.zbh_powder(), "powder")})
    sc.parent["p_flat"], sc.gmat["p_flat"] = "p_zbh", np.eye(4)
    sc.add("p_trough/excess", dome.copy(), P.POWDER, "p_trough", specular=0.1)
    sc.parent["p_trough"] = body
    sc.gmat["p_trough"] = T((f["trough_x"], f["zbh"][1], RP.PREP["h"] - 15.0)) @ S((9.0, 20.0, 0.1))
    pp = RP.PREP
    sc.add("p_dust/dust", pv.Cylinder(center=(0, 0, 0.25), direction=(0, 0, 1), radius=5.8, height=0.5,
                                       resolution=32).triangulate(), P.POWDER, "p_dust", specular=0.1)
    sc.parent["p_dust"], sc.gmat["p_dust"] = "p_puck", T((0, 0, pp["puck_h"] + 2.8))
    sc.add("p_fill/fill", pv.Cylinder(center=(0, 0, 0.5), direction=(0, 0, 1), radius=pp["cup_d"] / 2 - 2.0,
                                       height=1.0, resolution=40).triangulate(), P.POWDER, "p_fill", specular=0.1)
    sc.parent["p_fill"] = "p_cup"
    for g in ("p_heap", "p_flat", "p_trough", "p_dust", "p_fill"):
        for n in sc.members(g):
            sc.alpha[n] = 0.0
    set_heap(sc, 0.0)
    set_fill(sc, 0.0)
    # the sample vial with its mesh cap, in the MiR's one-vial block (setup_lab.Unit's), and its powder
    sc.add("p_vial/glass", P.vial_glass(), P.GLASS, "p_vial", opacity=0.55, specular=0.7)
    ring = pv.Cylinder(center=(0, 0, P.VIAL_H - 2.0), direction=(0, 0, 1), radius=P.VIAL_R + 0.8, height=8.0,
                       resolution=40).triangulate()
    sc.add("p_vial/cap ring", ring, (0.86, 0.87, 0.88), "p_vial", specular=0.4)
    mesh = pv.Cylinder(center=(0, 0, P.VIAL_H + CAP_OUT - 0.3), direction=(0, 0, 1), radius=P.VIAL_R - 0.6,
                       height=0.6, resolution=40).triangulate()
    sc.add("p_vial/mesh", mesh, (0.30, 0.31, 0.33), "p_vial", opacity=0.75, specular=0.5)
    sc.add("p_vial/powder", P.fill(1.0), P.POWDER, "p_vial_powder")
    sc.parent["p_vial_powder"] = "p_vial"
    vial_level(sc, LEVEL0)
    cab = L.amr_group
    sc.parent["p_vial"] = cab
    sc.gmat["p_vial"] = T((A.BUFFER_LOCAL[0], A.BUFFER_LOCAL[1], P.AMR_TOP - 20.0 + P.DECK_FLOOR))
    # a one-cup block on the cabinet for the XRF cup's ride to Shuttle 2 (a shallow pocket: the fingers stay over it)
    blk = P.pocket_block(-34.0, 34.0, -34.0, 34.0, [(0.0, 0.0, pp["cup_d"] / 2 + 2.0)], floor=18.0)
    sc.add("p_caddy/block", blk, P.RACK_C, "p_caddy", specular=0.25)
    sc.parent["p_caddy"] = cab
    # round 11: on the arm's 20 mm mounting plate (props.mir250: |x| < 170, its top at P.AMR_TOP), not 20 mm down in it
    # at the cabinet's top: the pocket's floor was 2 mm under the plate's top, so the cup was set down into the plate
    sc.gmat["p_caddy"] = T((CADDY_AT[0], CADDY_AT[1], P.AMR_TOP))
    # the falling powder (points)
    sc.add("p_stream", pv.PolyData(np.zeros((1, 3))), P.POWDER, "p_stream", style="points", point_size=3.0,
           render_points_as_spheres=True)
    sc.alpha["p_stream"] = 0.0
    L.apply_state()
    return sc, L, u, R_, ov, ms_grains


MS_LID = 1.0                          # how far the Aero S cover opens. Round 11: its full swing reaches the iMicro beside
#                                       it (50 mm, 6 frames), but opened 55 % it was in the arm's way (25 frames): open
XRD_DOOR = 0.8                        # the MiniFlex's door, 80 deg. Round 11: it meets camera D1's head (7 frames), and
#                                       still does at 70 deg: open
CADDY_AT = (60.0, -185.0)             # the XRF cup's block on the cabinet top (MiR frame), behind the arm


def fast_collisions(sc, L, u, trays=("D", "E", "M"), reach=2800.0):
    """As alloy_characterize.fast_collisions (round 10): the arm's collision world (collide.World) is what it can
    reach, the trays this chapter presents and whatever stands within `reach` of the arm's base anywhere on its way
    (from START_X to both docks), our parts included. The trays left in their slots inside the Shuttles are left out.
    The planner and the audit see the same world, so the paths are the same; World.refresh otherwise asks VTK about
    every actor in the lab every frame (round 9's audit of this chapter took 30 min). Only this chapter's arm is
    audited: the second unit stays on its charger."""
    import collide as CL
    keep, drop = set(), set()
    for k in L.tray:
        (keep if k in trays else drop).update(CL._subtree(sc, f"tray_{k}"))
    x0, x1 = min(DOCK1[0], DOCK2[0], START_X), max(DOCK1[0], DOCK2[0], START_X)
    xs = np.linspace(x0, x1, 1 + int(math.ceil((x1 - x0) / 250.0))) + A.ARM_LOCAL[0]
    bases = np.c_[xs, np.full_like(xs, DOCK1[1] + A.ARM_LOCAL[1])]
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


def set_heap(sc, k: float):
    """The mound on the holder: k = 0 (none) to 1 (a dome 15 mm across, 4 mm high over the reference plane)."""
    z = RP.ZBH
    top = z["t"]
    on = k > 0.01
    sc.gmat["p_heap"] = T((0, 0, top - 0.3)) @ S((max(0.5, 15.0 * k ** 0.4), max(0.5, 15.0 * k ** 0.4),
                                                  max(0.05, 4.0 * k)))
    for n in sc.members("p_heap"):
        sc.alpha[n] = 1.0 if on else 0.0


def set_fill(sc, mm: float):
    sc.gmat["p_fill"] = T((0, 0, 1.2)) @ S((1.0, 1.0, max(0.05, mm)))
    for n in sc.members("p_fill"):
        sc.alpha[n] = 1.0 if mm > 0.05 else 0.0


def vial_level(sc, mm: float, inverted=False):
    """The powder in the vial: `mm` deep, on the floor, or against the mesh cap when the vial is upside down."""
    z0 = P.VIAL_FLOOR if not inverted else P.VIAL_H - 1.0 - mm
    sc.gmat["p_vial_powder"] = T((0, 0, z0)) @ S((1, 1, max(0.1, mm)))


def branch_q(rb, Tw, Tw_ref):
    """The IK solution for Tw in the branch of a clear solution for Tw_ref (alloy_workflow's way), so the straight line
    that follows stays in a branch that is clear where it ends; of those, the first whose Tw solution is clear too."""
    import collide
    chk = rb.checker()
    Wd = chk.snapshot()
    Tb = np.linalg.inv(rb.sc.world(rb.root)) @ Tw_ref
    first = None
    for q in collide.ik_all(rb.model, Tb, rb.q):
        if not chk.collisions(q, rb.close, Wd, chk.touching(q, rb.close, Wd)):
            qq = rb.solve(Tw, seed=q)
            if first is None:
                first = qq
            if not chk.collisions(qq, rb.close, Wd, chk.touching(qq, rb.close, Wd)):
                return qq
    return first if first is not None else rb.solve(Tw)


# ================================================================================================= the movie
def movie():
    sc, L, u, RG, ov, ms_grains = build()
    rb = u.robot
    fast_collisions(sc, L, u)
    xrd, sem, ms, xrf, prep = RG["xrd"], RG["sem"], RG["ms"], RG["xrf"], RG["prep"]
    # round 11: what isn't solid, for the stricter audit's movers check (collide.py skips sc.fluids): the MiniFlex's and
    # the S2 PUMA's X-ray beams, the Mastersizer's laser, its scattered light and the grains it scatters off, the glow
    light = {f"{xrd.prefix}{k}" for k in ("ibeam", "dbeam", "glow")} | {f"{xrf.prefix}beam"} | {
        f"{ms.prefix}{k}" for k in ("beam", "arcs_lit", "scat_large", "scat_small", "grains", "powder")}
    sc.fluids = set(getattr(sc, "fluids", set())) | {n for n, g in sc.group_of.items() if g in light}
    PARK = np.radians(A.PARK_DEG)
    n = 7
    st = {"lbl": f"1/{n}", "cap": ""}
    rows: dict[str, str] = {}

    def status(**kv):
        rows.update(kv)
        L.extra_gauges = [(k, v) for k, v in rows.items() if v]
        L.gauges()

    # ------------------------------------------------------------------ helpers
    def step(secs, f=None, hold=0.1, cam=None, labels=(), still=False):
        sc.step(st["lbl"], st["cap"], secs, f, hold=hold, cam_to=cam, labels=labels, still=still)

    def go(Tw=None, q=None, secs=1.6, cam=None, labels=(), grip=None, extra=None, hold=0.05):
        fj = rb.joint_to(Tw=Tw) if Tw is not None else rb.joint_to(q)
        step(secs, RB.both(fj, rb.grip_to(grip) if grip is not None else None, extra), hold=hold, cam=cam,
             labels=labels)

    def lin(Tw, secs=0.8, extra=None, hold=0.05, cam=None):
        step(secs, RB.both(rb.line_to(Tw), extra), hold=hold, cam=cam)

    def grip(c, secs=0.4):
        step(secs, rb.grip_to(c), hold=0.05)

    def sh(Tw, d):
        M = Tw.copy()
        M[:3, 3] = M[:3, 3] + np.asarray(d, float)
        return M

    def along(Tw, dist):
        return sh(Tw, Tw[:3, 2] * dist)

    def go_to(Tw, ref, secs=1.6, cam=None, labels=(), grip=None, extra=None, hold=0.05):
        go(q=branch_q(rb, Tw, ref), secs=secs, cam=cam, labels=labels, grip=grip, extra=extra, hold=hold)

    def clear_of(cands):
        """The first candidate [pose, ...] (each a list of tool poses the move needs) whose every pose has an IK
        solution clear of everything, the checker run on the scene as it is now; the first one if none is."""
        import collide
        chk = rb.checker()
        Wd = chk.snapshot()
        Bi = np.linalg.inv(sc.world(rb.root))
        for k, poses in enumerate(cands):
            ok = True
            for Tw in poses:
                qs = collide.ik_all(rb.model, Bi @ Tw, rb.q)
                if not any(not chk.collisions(q, rb.close, Wd, chk.touching(q, rb.close, Wd)) for q in qs):
                    ok = False
                    break
            if ok:
                return k
        print(f"warning: {NAME} {st['lbl']}: no candidate clear of everything", file=sys.stderr, flush=True)
        return 0

    def park(secs=1.4, cam=None, labels=(), extra=None):
        go(q=PARK, secs=secs, cam=cam, labels=labels, extra=extra)

    def clock(what, t0, t1, unit="min"):
        def up(uu):
            t = t0 + (t1 - t0) * uu
            ov.clock = (what, f"{int(t // 60):d}:{int(t % 60):02d}" if unit == "s" else
                        f"{int(t):d} min {int(round((t % 1) * 60)) % 60:02d} s")
        return up

    def panel(key, a0, a1):
        def up(uu):
            ov.key = key
            ov.a = a0 + (a1 - a0) * uu
        return up

    def at(rig, p):
        return (sc.world(f"{rig.prefix}body") @ np.r_[p, 1.0])[:3]

    def wpt(group, p=(0, 0, 0)):
        return (sc.world(group) @ np.r_[p, 1.0])[:3]

    def drive(x0, x1, y=DOCK1[1]):
        dist = x1 - x0

        def up(uu):
            u.set((x0 + dist * P.ramp_frac(P.unease(uu), dist, MIR_V), y, 0.0))
            if rb.held is not None:
                rb.set()
            L.apply_state()
        return up, max(1.2, P.ramp_secs(dist, MIR_V))

    # streams of falling powder from the vial's mouth to a target
    rng = np.random.default_rng(4)
    NPTS = 70
    jit = rng.uniform(-1, 1, (NPTS, 2))
    phase = rng.uniform(0, 1, NPTS)

    def stream(target, spread, on_from=0.25, on_to=0.95, rate=6.0):
        def up(uu):
            on = on_from < uu < on_to
            sc.alpha["p_stream"] = 1.0 if on else 0.0
            if not on:
                return
            mouth = wpt("p_vial", (0, 0, P.VIAL_H + CAP_OUT))
            ph = (phase + uu * rate) % 1.0
            xy0 = mouth[:2] + jit * (P.VIAL_R - 3.0) * 0.8
            xy1 = np.asarray(target[:2]) + jit * spread
            pts = np.c_[xy0 + (xy1 - xy0) * ph[:, None], mouth[2] + (target[2] - mouth[2]) * ph]
            sc.set_mesh("p_stream", pv.PolyData(pts))
        return up

    # ------------------------------------------------------------------ cameras
    CAM_IN = [(4600, -6900, 3000), (1100, -1500, 1150), (0, 0, 1)]
    CAM_OPEN = [(2300, -4300, 2200), (150, -1250, 1150), (0, 0, 1)]

    # ------------------------------------------------------------------ 1. the sample arrives
    st["lbl"] = f"1/{n}"
    st["cap"] = ("While the plate prints, a retained sample of the sieved 20-63 µm cut, about 15 g split off at the "
                 "sieving cell (chapter 3), goes round the trays. The MiR250 brings it to Shuttle 1 in a vial with a "
                 "mesh cap.")
    status(Arm="UR10e on the MiR250, arriving", Sample="Al-10Si, 20-63 um, 15 g", Trays="all in their slots")
    sc.cam = list(CAM_IN)
    f_drive, secs = drive(START_X, DOCK1[0])
    step(secs, f_drive, hold=0.2, cam=CAM_OPEN)
    step(0.6, None, hold=1.2, labels=[("sample vial, mesh cap", tuple(wpt("p_vial", (0, 0, 80))), (0.16, 0.36))])

    # ------------------------------------------------------------------ 2. tray D: the prep
    st["lbl"] = f"2/{n}"
    st["cap"] = ("Tray D, microscopy and diffraction, comes to the opening: the TM4000PlusII SEM, the Rigaku MiniFlex "
                 "and the powder prep station beside it (our design): a zero-background holder, an SEM stub carrier "
                 "and an XRF cup in their nests, and a blade.")
    status(Trays="D to the opening")
    L.fetch("D", st["lbl"], st["cap"], fast=0.55, cam=CAM_OPEN, hold=0.2)
    status(Trays="D at the opening")
    pw = lambda q: at(prep, q)                                # noqa: E731
    fr = RP.prep_frames()
    pz = RP.PREP["h"]
    c_st = pw((-40.0, -40.0, pz))
    CAM_PREP = [tuple(c_st + (520, -820, 420)), tuple(c_st + (-10, 0, 10)), (0, 0, 1)]
    step(1.6, None, hold=0.6, cam=CAM_PREP,
         labels=[("zero-background holder: single-crystal Si", tuple(wpt("p_zbh", (0, 0, 8))), (0.14, 0.30)),
                 ("SEM stub on a 1.5 in carrier", tuple(wpt("p_puck", (0, 0, 30))), (0.52, 0.18)),
                 ("XRF cup, film down", tuple(wpt("p_cup", (0, 0, 28))), (0.86, 0.30)),
                 ("strike-off blade", tuple(pw((RP.PREP["zbh_x"] + RP.PREP["blade_park"], fr["zbh"][1] + 40,
                                                pz + 45))), (0.30, 0.82))])
    # the vial from its block on the cabinet, held level by its side, so a roll of the wrist turns it over
    st["cap"] = ("The arm takes the vial by its side. The powder goes on as it came off the sieves: never ground. "
                 "Milling ductile atomized powder cold-welds the spheres into flakes, which lie flat and skew the "
                 "pattern (literature summarized in notes/edison_r8.md).")
    status(Arm="taking the vial")
    v_base = wpt("p_vial")
    T_v = A.level(v_base + (0, 0, VIAL_TCP), toward=(1.0, 0.0, 0.0), spin=0.0)
    go_to(along(T_v, -110), T_v, secs=1.8, grip=0.55, cam=CAM_OPEN)
    lin(T_v, 0.7)
    grip(GRIP_VIAL)
    rb.grasp("p_vial")
    lin(sh(T_v, (0, 0, 70)), 0.6)

    # sift: over the target, upright and high; then turned over, the mesh 14 mm over it; shaken; turned back
    def sift(target_top, spread, secs_pour, f_more=None, gap=14.0, rate=6.0, roll=-165.0, toward=(0.0, 1.0, 0.0)):
        T_up = A.level(target_top + (0, 0, 95.0), toward=toward, spin=0.0)
        T_dn = A.level(target_top + (0, 0, gap + (P.VIAL_H + CAP_OUT - VIAL_TCP)), toward=toward, spin=0.0) \
            @ R((0, 0, 1), roll)
        go(T_up, secs=1.8, cam=CAM_SIFT)
        step(1.2, RB.both(rb.line_to(T_dn), lambda uu: vial_level(sc, lvl["mm"], inverted=uu > 0.55)), hold=0.05)
        T_a, T_b = T_dn @ R((0, 0, 1), 7.0), T_dn @ R((0, 0, 1), -7.0)

        def shake(uu):
            stream(target_top, spread, rate=rate)(uu)
            if f_more is not None:
                f_more(uu)
        k = 3
        for i in range(k):
            step(secs_pour / (2 * k), RB.both(rb.line_to(T_a if i % 2 == 0 else T_b),
                                              lambda uu, i=i: shake((i + uu) / k)), hold=0.0)
            step(secs_pour / (2 * k), RB.both(rb.line_to(T_dn), lambda uu, i=i: shake((i + 0.5 + uu * 0.5) / k)),
                 hold=0.0)
        sc.alpha["p_stream"] = 0.0
        step(1.0, RB.both(rb.line_to(T_up), lambda uu: vial_level(sc, lvl["mm"], inverted=uu < 0.45)), hold=0.05)

    lvl = {"mm": LEVEL0}
    CAM_SIFT = [tuple(c_st + (600, -380, 640)), tuple(c_st + (-90, 10, 20)), (0, 0, 1)]   # above right: the arm
    #                                                                                         comes in from the left

    def drain(mm0, mm1):
        def up(uu):
            lvl["mm"] = mm0 + (mm1 - mm0) * uu
            vial_level(sc, lvl["mm"], inverted=True)
        return up

    zt = wpt("p_zbh", (0, 0, RP.ZBH["t"]))
    st["cap"] = ("Onto the holder first. Turned over and shaken, the vial sifts the powder through its mesh cap, an even "
                 "layer with no pressing (as A-Lab's UR5e does it), a little more than the 0.5 mm well holds.")
    status(Arm="sifting onto the XRD holder")
    sift(zt, 6.0, 3.0, RB.both(drain(LEVEL0, LEVEL0 - 1.5), lambda uu: set_heap(sc, uu)), gap=60.0)
    st["cap"] = "A dusting on the SEM stub's carbon tab, from the same vial."
    status(Arm="dusting the SEM stub")
    sift(wpt("p_puck", (0, 0, RP.PREP["puck_h"] + 2.8)), 3.0, 1.2, RB.both(
        drain(LEVEL0 - 1.5, LEVEL0 - 1.6), lambda uu: [sc.alpha.__setitem__(nm, min(1.0, uu * 2)) for nm in
                                                        sc.members("p_dust")]), gap=26.0, rate=3.0)
    st["cap"] = "And about 4 g into the XRF cup, onto its film."
    status(Arm="filling the XRF cup")
    sift(wpt("p_cup", (0, 0, 26.5)), 9.0, 3.0, RB.both(drain(LEVEL0 - 1.6, LEVEL0 - 6.5),
                                                       lambda uu: set_fill(sc, 11.0 * uu)), gap=22.0)
    st["cap"] = "The vial goes back to its block on the MiR."
    status(Arm="the vial back")
    go(sh(T_v, (0, 0, 70)), secs=2.0, cam=CAM_OPEN)
    lin(T_v, 0.6)
    grip(0.55)
    rb.release(L.amr_group)
    lin(along(T_v, -110), 0.6)
    # strike off
    blade_x0 = prep.v["blade"]
    st["cap"] = ("The blade strikes the mound off flush with the holder's top, its reference plane, and pushes the excess "
                 "into the trough. The powder's face has to sit on the goniometer's axis: 0.1 mm too high moves the Al "
                 "111 peak by about 0.07 deg.")
    status(Arm="parked", Prep="striking off")
    CAM_ZBH = [tuple(zt + (260, -330, 190)), tuple(zt + (0, 0, 0)), (0, 0, 1)]
    park(1.2, cam=CAM_ZBH)

    def strike(uu):
        prep.move({"blade": (blade_x0, 1.0)})(uu)
        set_heap(sc, max(0.0, 1.0 - uu * 1.6))
        on = uu > 0.25
        for nm in sc.members("p_flat"):
            sc.alpha[nm] = 1.0 if on else 0.0
        kk = min(1.0, max(0.0, (uu - 0.5) / 0.5))
        sc.gmat["p_trough"] = T((fr["trough_x"], fr["zbh"][1], RP.PREP["h"] - 15.0)) @ S((9.0, 20.0, 0.1 + 5.0 * kk))
        for nm in sc.members("p_trough"):
            sc.alpha[nm] = 1.0 if kk > 0.02 else 0.0
    step(2.4, strike, hold=0.2)
    step(1.4, prep.move({"blade": (1.0, 0.0)}), hold=0.6,
         labels=[("struck off flush: on the goniometer's axis", tuple(zt + (0, 0, 2)), (0.30, 0.30))])
    status(Prep="holder, stub and cup ready")

    # ------------------------------------------------------------------ 3. the XRD
    st["lbl"] = f"3/{n}"
    g = I._miniflex(I.XRD)
    xw = lambda q: at(xrd, q)                                 # noqa: E731
    axis = xw((0, g["gy"], g["gz"]))
    CAM_XRD = [tuple(axis + (420, -1050, 330)), tuple(axis + (-10, -60, -40)), (0, 0, 1)]
    # the holder is taken with the door shut: opened, the door stands between the arm and the prep station
    st["cap"] = ("The Rigaku MiniFlex, its door drawn see-through so the goniometer shows: it stands still at its load "
                 "position. The arm takes the holder by its fin first, while the door is still shut.")
    status(XRD="door shut", Prep="", Arm="taking the holder")
    fin = (0.0, RP.ZBH["fin_y"], RP.ZBH["fin_h"] - 4.0)
    stage_g = f"{xrd.prefix}stage"
    H_on = sc.world(stage_g) @ T((0.0, g["gy"], g["gz"] - 3.0)) @ R((0, 0, 1), -25.0)
    rolls = (0.0, 180.0)
    cands = []
    for rl in rolls:
        Tf = sc.world("p_zbh") @ T(fin) @ _level_y() @ R((0, 0, 1), rl)
        To = H_on @ T(fin) @ _level_y() @ R((0, 0, 1), rl)
        cands.append([sh(along(Tf, -110), (0, 0, 30)), Tf, sh(along(To, -230), (0, 0, 30)), sh(To, (0, 0, 30)), To])
    xrd.v["door"] = 0.8                      # judge the placing poses with the door open, as they will be
    xrd.apply()
    roll = rolls[clear_of(cands)]
    xrd.v["door"] = 0.0
    xrd.apply()
    T_fin = sc.world("p_zbh") @ T(fin) @ _level_y() @ R((0, 0, 1), roll)
    T_on = H_on @ T(fin) @ _level_y() @ R((0, 0, 1), roll)
    CAM_XRDL = [tuple(axis + (760, -1350, 620)), tuple(axis + (-40, -170, -80)), (0, 0, 1)]
    go(sh(along(T_fin, -110), (0, 0, 30)), secs=1.8, grip=0.62, cam=CAM_SIFT,
       labels=[("Rigaku MiniFlex", tuple(xw((0, g["yf"], I.XRD["H"] + 30))), (0.22, 0.22))])
    lin(T_fin, 0.8)
    grip(GRIP_FIN)
    rb.grasp("p_zbh")
    lin(sh(T_fin, (0, 0, 30)), 0.6)
    lin(sh(along(T_fin, -90), (0, 0, 30)), 0.6)
    # it waits left of the MiniFlex, outside the door's swing, while the door opens. Round 10: 480 mm back along the
    # way in (was 380, where the holder's far edge was 372 mm from the hinge, inside the door's 398 mm swing, and the
    # opening door met it), and in the IK branch that is clear with the holder on the stage (branch_q, judged with the
    # door open, as it will be). The nearest branch had the shoulder turned 100 deg further round, and the straight
    # line in from there swept the upper arm and forearm through the SEM, the MiniFlex's housing and tray D's camera
    # post (16 frames in round 9's audit, which the notes had put on the way back out)
    T_wait = sh(along(T_on, -480), (0, 0, 60))
    xrd.v["door"] = 0.8
    xrd.apply()
    q_wait = branch_q(rb, T_wait, T_on)
    xrd.v["door"] = 0.0
    xrd.apply()
    go(q=q_wait, secs=2.2, cam=CAM_XRDL)
    st["cap"] = ("An actuator on the hinge opens the door (our addition; Yotsumoto et al. 2024 drove theirs the same "
                 "way), to 80 deg, which clears the tray's camera post; the arm waits outside its swing.")
    status(XRD="door opening", Arm="holding the holder")
    step(1.6, xrd.move({"door": (0.0, XRD_DOOR)}), hold=0.2,
         labels=[("goniometer, at rest", tuple(axis + (0, 0, 60)), (0.62, 0.20))])
    st["cap"] = ("In through the door and onto the stage, turned a little (the spinner takes it any way round). Nothing "
                 "has touched the powder's face since it was struck off.")
    status(Arm="loading the XRD")
    lin(sh(along(T_on, -230), (0, 0, 30)), 1.0)
    lin(sh(T_on, (0, 0, 30)), 1.2)
    lin(T_on, 0.6)
    grip(0.62)
    rb.release(stage_g)
    lin(along(T_on, -230), 1.0)
    go(sh(T_v, (0, 0, 220)), secs=2.2, cam=CAM_XRDL)   # back out of the doorway and up over the MiR, clear of the housings
    park(1.8, cam=CAM_XRD)
    sc.gmat["p_zbh"] = sc.gmat["p_zbh"].copy()
    status(Arm="parked", XRD="loaded")
    st["cap"] = ("Door shut and locked; only then does the interlock let the tube switch on, and the X-ray lamp on top "
                 "lights. The goniometer drives to its start, theta 5 deg and 2theta 10 deg.")
    status(XRD="door locked, X-rays on")
    step(1.4, xrd.move({"door": (XRD_DOOR, 0.0)}), hold=0.1)
    step(1.0, xrd.move({"glow": (0.0, 1.0)}), hold=0.1)
    step(1.4, xrd.move({"stage": (0.0, RP.V_START), "ibeam": (0.0, 1.0), "~hood": (0.0, 1.0), "~door": (0.0, 0.6)}),
         hold=0.1, labels=[("X-ray tube (fixed)", tuple(xw((-I.XRD["gonio_r"] - 50, g["gy"], g["gz"] + 50))),
                            (0.12, 0.26)),
                           ("detector, 2theta", tuple(xw((150, g["gy"], g["gz"] + 40))), (0.86, 0.26))])
    # the scan, with the holder spinning (a spinner: our assumption), which samples more crystallites
    H0 = sc.gmat["p_zbh"].copy()

    def scan(uu):
        xrd.move({"stage": (RP.V_START, 1.0), "detector": (0.0, 1.0), "dbeam": (0.0, 1.0)})(uu)
        sc.gmat["p_zbh"] = H0 @ R((0, 0, 1), 360.0 * 6 * uu)
        clock("MiniFlex, 2theta 10-90 deg", 0.0, 14.0)(uu)
    st["cap"] = ("The scan, the housing drawn see-through: the tube stays put, the sample tilts by theta and the detector "
                 "sweeps 2theta from 10 to 90 deg. The holder spins as it goes (a spinner is assumed), so more "
                 "crystallites diffract: the literature's fix for coarse grains, not grinding.")
    status(XRD="scanning, 10-90 deg 2theta")
    step(5.0, scan, hold=0.1)
    st["cap"] = ("The pattern: aluminium's fcc peaks and silicon's diamond-cubic ones, as Al-10Si should show. COMPUTED, "
                 "not measured: no pattern of this powder exists yet. Bragg's law, structure factors, "
                 "Lorentz-polarization.")
    step(1.2, panel("xrd", 0.0, 1.0), hold=3.6, still=True)
    ov.clock = None
    st["cap"] = ("X-rays off, the lamp out, the goniometer back to its load position; the holder stays in until the "
                 "next sample.")
    status(XRD="done")
    step(1.4, RB.both(panel("xrd", 1.0, 0.0), xrd.move({"stage": (1.0, 0.0), "detector": (1.0, 0.0),
                                                         "ibeam": (1.0, 0.0), "dbeam": (1.0, 0.0), "glow": (1.0, 0.0),
                                                         "~hood": (1.0, 0.0), "~door": (0.6, 0.0)})), hold=0.2)
    ov.key = None

    # ------------------------------------------------------------------ 4. the SEM
    st["lbl"] = f"4/{n}"
    gs = I._tm4000(I.SEM)
    sw = lambda q: at(sem, q)                                 # noqa: E731
    import r8_char as RC
    cup_floor = I.SEM["front_z0"] + 62.0 + RC.SEM_CUP["floor"]
    CAM_SEM = [tuple(sw((0, -300, 200)) + (-850, -1650, 760)), tuple(sw((0, -330, 170))), (0, 0, 1)]
    st["cap"] = ("The SEM next to it, a Hitachi TM4000PlusII: it vents and its door comes out with the stage. The stub "
                 "rides on a 1.5 in aluminium carrier (our design), so the same holder cup that takes the mounts "
                 "(chapter 7) takes it, and its spring plunger is the path to ground.")
    status(SEM="venting, door out", Arm="taking the stub carrier")
    spins = (0.0, 90.0, 180.0, 270.0, 45.0, 135.0, 225.0, 315.0)
    pk_at = wpt("p_puck", (0, 0, RP.PREP["puck_h"] + 8.0))
    k = clear_of([[A.down(pk_at + (0, 0, 90), spin=sp), A.down(pk_at, spin=sp)] for sp in spins])
    T_pk = A.down(pk_at, spin=spins[k])
    go_to(sh(T_pk, (0, 0, 90)), T_pk, secs=1.8, grip=0.5, cam=CAM_SIFT,
          extra=sem.move({"drawer": (0.0, 1.0)}))
    lin(T_pk, 0.7)
    grip(GRIP_PUCK)
    rb.grasp("p_puck")
    lin(sh(T_pk, (0, 0, 90)), 0.7)
    drawer_g = f"{sem.prefix}drawer"
    P_in = (sc.world(drawer_g) @ np.r_[0.0, gs["ys"], cup_floor, 1.0])[:3]
    in_at = P_in + (0, 0, RP.PREP["puck_h"] + 8.0)
    k = clear_of([[A.down(in_at + (0, 0, 90), spin=sp), A.down(in_at, spin=sp)] for sp in spins] +
                 [[P.tcp_frame(in_at + (0, -25, 90), (0, 0.26, -0.966), sp), P.tcp_frame(in_at, (0, 0.26, -0.966), sp)]
                  for sp in spins])
    T_in = (A.down(in_at, spin=spins[k]) if k < len(spins) else
            P.tcp_frame(in_at, (0, 0.26, -0.966), spins[k - len(spins)]))
    go_to(sh(T_in, (0, 0, 90)), T_in, secs=2.0, cam=CAM_SEM,
          labels=[("Hitachi TM4000PlusII", tuple(sw((0, 0, 600))), (0.22, 0.22)),
                  (RC.AZTEC.split(",")[0], tuple(sw((gs["W"] / 2 + 190, -90, 330))), (0.80, 0.16))])
    lin(T_in, 0.8)
    grip(0.5)
    rb.release(drawer_g)
    lin(sh(T_in, (0, 0, 90)), 0.7)
    if k >= len(spins):                       # set in tilted: square it up in the cup (it drops the last mm)
        sc.gmat["p_puck"] = T((0.0, gs["ys"], cup_floor))
    park(1.4)
    status(Arm="parked", SEM="pumping down")
    st["cap"] = "Door in, EVAC: about three minutes to vacuum. Then the powder, imaged."
    step(1.4, RB.both(sem.move({"drawer": (1.0, 0.0)}), clock("TM4000", 0.0, 0.2)), hold=0.1, cam=CAM_SEM)
    step(1.0, clock("TM4000", 0.2, 3.0), hold=0.1)
    st["cap"] = ("REAL DATA: the lab's own atomized Al 4047, run c3k0n5 (rePowder, 22 Oct 2026), on BYU's Apreo, "
                 "26 Oct 2026 (DAL #157). Spheres, a few satellites and some irregular particles; the same powder, "
                 "imaged on a floor SEM rather than this TM4000.")
    status(SEM="imaging")
    step(1.2, RB.both(panel("sem", 0.0, 1.0), clock("TM4000", 3.0, 8.0)), hold=4.2)
    st["cap"] = ("The particles counted in those images (972, inscribed circles): the size by number as imaged, by "
                 "volume, and what laser diffraction of the 20-63 um cut would give, computed from the count.")
    step(1.0, panel("psd", 0.0, 1.0), hold=3.6)
    step(0.8, panel("psd", 1.0, 0.0), hold=0.1)
    ov.key, ov.clock = None, None
    # the XRF cup rides on the MiR to Shuttle 2
    st["cap"] = "The XRF cup goes onto the MiR, into a shallow pocket on its cabinet: the XRF is on Shuttle 2."
    status(Arm="the XRF cup to the MiR")
    T_c = A.down(wpt("p_cup", (0, 0, 30.5)), spin=0.0)
    go_to(sh(T_c, (0, 0, 90)), T_c, secs=1.8, grip=0.45, cam=CAM_OPEN)
    lin(T_c, 0.7)
    grip(GRIP_CUP)
    rb.grasp("p_cup")
    lin(sh(T_c, (0, 0, 90)), 0.7)
    cad = wpt("p_caddy", (0, 0, 18.0 + 30.5))
    T_cd = A.down(cad, spin=0.0)
    go_to(sh(T_cd, (0, 0, 90)), T_cd, secs=2.0)
    lin(T_cd, 0.7)
    grip(0.45)
    rb.release("p_caddy")
    lin(sh(T_cd, (0, 0, 90)), 0.7)
    park(1.4)
    status(Arm="parked")
    st["cap"] = "Tray D goes back to its slot and its power, the samples in the instruments; tray E comes down."
    status(SEM="", XRD="", Trays="D to its slot")
    L.store("D", st["lbl"], st["cap"], fast=0.55, hold=0.1, cam=CAM_OPEN)

    # ------------------------------------------------------------------ 5. laser diffraction
    st["lbl"] = f"5/{n}"
    st["cap"] = ("Tray E, mechanical testing and particle size: the PIP, the KLA iMicro and the Malvern Mastersizer "
                 "3000 with its Aero S dry disperser.")
    status(Trays="E to the opening")
    L.fetch("E", st["lbl"], st["cap"], fast=0.55, hold=0.2, cam=CAM_OPEN)
    status(Trays="E at the opening")
    MP = I.MS3000
    gm = I._ms3000(MP)
    mw = lambda q: at(ms, q)                                  # noqa: E731
    hop = mw((gm["hx"], gm["hy"], MP["hop_z"]))
    CAM_MS = [tuple(hop + (700, -1300, 600)), tuple(hop + (60, 0, -60)), (0, 0, 1)]
    st["cap"] = ("The arm takes the vial again. The Aero S's clear cover lifts off (by hand in Malvern's videos; an "
                 "actuator is assumed here).")
    status(Arm="taking the vial", Malvern="cover off")
    v_base = wpt("p_vial")
    T_v = A.level(v_base + (0, 0, VIAL_TCP), toward=(1.0, 0.0, 0.0), spin=0.0)
    go_to(along(T_v, -110), T_v, secs=1.8, grip=0.55, extra=ms.move({"lid": (0.0, MS_LID)}))
    lin(T_v, 0.7)
    grip(GRIP_VIAL)
    rb.grasp("p_vial")
    lin(sh(T_v, (0, 0, 70)), 0.6)
    st["cap"] = "About 5 g into the hopper, over the vibrating feeder tray."
    status(Arm="pouring the powder")
    toward = np.array([0.0, 1.0, 0.0])
    T_p = A.level(hop + (18.0, 0.0, 52.0), toward=tuple(toward), spin=0.0)
    go(T_p, secs=2.0, cam=CAM_MS, labels=[("Malvern Mastersizer 3000 + Aero S", tuple(hop + (0, 0, 220)),
                                           (0.70, 0.22))])
    T_tip = T_p @ R((0, 0, 1), -125.0)

    def pour(uu):
        stream(hop + (0, 0, -20), 8.0, on_from=0.3, on_to=1.01, rate=7.0)(uu)
        drain(LEVEL0 - 6.5, LEVEL0 - 11.0)(min(1.0, max(0.0, (uu - 0.3) / 0.7)))
        vial_level(sc, lvl["mm"], inverted=uu > 0.5)
    lin(T_tip, 1.4, extra=pour, hold=0.0)
    step(1.2, pour, hold=0.0)
    sc.alpha["p_stream"] = 0.0
    step(1.0, RB.both(rb.line_to(T_p), lambda uu: vial_level(sc, lvl["mm"], inverted=uu < 0.5)), hold=0.05)
    status(Arm="the vial back")
    go(sh(T_v, (0, 0, 70)), secs=2.0, cam=CAM_OPEN)
    lin(T_v, 0.6)
    grip(0.55)
    rb.release(L.amr_group)
    lin(along(T_v, -110), 0.6)
    park(1.4, extra=ms.move({"lid": (MS_LID, 0.0), "powder": (0.0, 1.0)}), cam=CAM_MS)
    status(Arm="parked", Malvern="measuring")
    # the optical bench, in cutaway
    m = RP.ms_geometry()
    bench = mw(m["cell"])
    CAM_BENCH = [tuple(mw((-380.0, m["cy"] - 1000.0, m["bz"] + 1000.0))), tuple(mw((-190.0, m["cy"], m["bz"] - 20.0))),
                 (0, 0, 1)]       # high and in front, from the laser's end: the whole axis, the cell and the detector
    o = RP.MSO
    blabels = [("He-Ne laser 632.8 nm", tuple(mw((-490.0, m["cy"], m["bz"] + 18))), (0.10, 0.22)),
               ("lens", tuple(mw((o["lens_x"], m["cy"], m["bz"] + o["lens_r"]))), (0.26, 0.14)),
               ("cell", tuple(mw((m["cell"][0], m["cy"] - 30, m["bz"] + 40))), (0.44, 0.14)),
               ("focal-plane detector", tuple(mw((o["fpd_x"], m["cy"], m["bz"] + 40))), (0.88, 0.22)),
               ("large-angle detectors", tuple(mw((o["la_x"][0], m["cy"], m["bz"] - 44))), (0.64, 0.84)),
               ("blue LED 470 nm", tuple(mw((-436.0, m["cy"], m["bz"] - 60))), (0.12, 0.84))]
    st["cap"] = ("Cover on, air on. The instrument drawn see-through: the laser's beam is expanded, then focused so it "
                 "converges through the cell onto the focal-plane detector. First the background, with the cell "
                 "empty.")
    step(2.0, RB.both(ms.move({"shell": (1.0, 0.0), "beam": (0.0, 1.0)}), clock("Mastersizer", 0.0, 0.5)), hold=0.4,
         cam=CAM_BENCH, labels=blabels)

    def grains(on):
        for nm in ms_grains:
            sc.alpha[nm] = 1.0 if on else 0.0

    def feed(uu):
        ms.move({"tray": (0.0, 1.0), "powder": (1.0, 0.3), "grains": (0.0, 1.0)})(uu)
        grains(uu > 0.15)
        clock("Mastersizer", 0.5, 1.0)(uu)
    st["cap"] = ("The feeder tray vibrates the powder into the venturi; the air disperses it and carries it through the "
                 "cell. The obscuration, the share of the beam the particles take out, rises.")
    step(3.0, feed, hold=0.2, labels=blabels)

    def scatter(uu):
        ms.move({"scat_large": (0.0, 1.0), "scat_small": (0.0, 1.0), "arcs_lit": (0.0, 1.0),
                 "grains": (0.0, 1.0), "tray": (0.0, 1.0)})(uu)
        clock("Mastersizer", 1.0, 1.8)(uu)
    st["cap"] = ("Large particles scatter light at small angles, onto the inner arcs of the focal-plane detector; small "
                 "ones scatter wide, to the large-angle and back-scatter detectors, where the blue LED's shorter "
                 "wavelength resolves the finest. Each arc's light, ring by ring, is the raw data.")
    step(4.0, scatter, hold=0.6, labels=blabels)
    st["cap"] = ("A Mie-theory fit of that pattern gives the volume-weighted size distribution. COMPUTED here: no "
                 "Mastersizer result for this powder exists, so the curve is the SEM count of c3k0n5 by volume, put "
                 "through the 20-63 um sieve (Dv50 about 58 um).")
    step(1.2, RB.both(panel("psd", 0.0, 1.0), clock("Mastersizer", 1.8, 2.5)), hold=4.0)
    st["cap"] = "Done: the beam off, the extractor draws the powder away, the bench closed."
    status(Malvern="done")

    def done_ms(uu):
        ms.move({"beam": (1.0, 0.0), "scat_large": (1.0, 0.0), "scat_small": (1.0, 0.0), "arcs_lit": (1.0, 0.0),
                 "shell": (0.0, 1.0), "powder": (0.3, 0.0)})(uu)
        panel("psd", 1.0, 0.0)(uu)
        grains(uu < 0.4)
    step(1.4, done_ms, hold=0.2)
    ov.key, ov.clock = None, None
    grains(False)
    st["cap"] = "Tray E goes back up to its slot."
    status(Malvern="", Trays="E to its slot")
    L.store("E", st["lbl"], st["cap"], fast=0.55, hold=0.1, cam=CAM_OPEN)

    # ------------------------------------------------------------------ 6. the XRF on Shuttle 2
    st["lbl"] = f"6/{n}"
    st["cap"] = ("The XRF is on Shuttle 2. The MiR250 drives over, speeding up and slowing down at its published "
                 "0.3 m/s², and stops in front of the second Shuttle's opening, by the XRF's end of the tray.")
    status(Arm="parked, the XRF cup on the cabinet", Trays="D, E in their slots")
    CAM_2 = [(X2 + 2300, -4300, 2200), (X2 - 400, -1250, 1150), (0, 0, 1)]
    f_drive, secs = drive(DOCK1[0], DOCK2[0])
    step(secs, f_drive, hold=0.2, cam=CAM_2)
    st["cap"] = ("Tray M comes down to Shuttle 2's opening: the Bruker S2 PUMA Series 2 benchtop XRF, a ductless fume "
                 "hood and the Carvera.")
    status(Trays="M to the opening")
    L.fetch("M", st["lbl"], st["cap"], fast=0.55, cam=CAM_2, hold=0.2)
    status(Trays="M at the opening")
    gx = RP.xrf_geometry()
    fw = lambda q: at(xrf, q)                                 # noqa: E731
    mx, my = gx["port"]
    dk = gx["deck"]
    port_w = fw((mx, my, dk))
    CAM_XRF = [tuple(port_w + (520, -900, 640)), tuple(port_w + (60, 40, 20)), (0, 0, 1)]
    st["cap"] = ("The S2 PUMA measures from below, so the film-bottomed cup only has to reach the chamber's port. For a "
                 "robot, Bruker's Automation version takes samples \"into the sample chamber directly\": drawn here as a "
                 "hatch in the hood's top (our assumption), which slides back; the port opens and the chamber's lift "
                 "ring rises through it to take the cup.")
    status(XRF="hatch open, port open")
    RING_UP = -60.0 / RP.XRF_G["sink"]          # the ring 60 mm up through the open port, to meet the cup
    # round 9 (Sterling, 27:13): the hood and the body go see-through HERE, before the cup moves, and stay so until the
    # measurement is over, so the whole internal path (hatch, lift ring, down into the chamber) is seen
    step(1.8, RB.both(xrf.move({"hatch": (0.0, 1.0), "port": (0.0, 1.0), "~lid": (0.0, 1.0), "~body": (0.0, 1.0)}),
                      lambda uu: xrf.move({"ring": (0.0, RING_UP)})(max(0.0, uu * 2 - 1))), hold=0.3, cam=CAM_XRF,
         labels=[("Bruker S2 PUMA Series 2", tuple(fw((0, gx["yf"], gx["H"] + 40))), (0.20, 0.22)),
                 ("hatch (assumed)", tuple(fw((0, gx["yf"] + 120, gx["H"] + 10))), (0.56, 0.16)),
                 ("chamber port", tuple(port_w + (0, 0, 6)), (0.30, 0.70))])
    st["cap"] = "The arm takes the cup off the cabinet and lowers it through the hatch onto the chamber's lift ring."
    status(Arm="loading the XRF")
    T_c = A.down(wpt("p_cup", (0, 0, 30.5)), spin=0.0)
    go_to(sh(T_c, (0, 0, 90)), T_c, secs=1.8, grip=0.45, cam=CAM_2)
    lin(T_c, 0.7)
    grip(GRIP_CUP)
    rb.grasp("p_cup")
    lin(sh(T_c, (0, 0, 90)), 0.7)
    ring_g = f"{xrf.prefix}ring"
    on_ring = (sc.world(ring_g) @ np.r_[mx, my, dk + 2.0, 1.0])[:3]        # the ring up: 60 mm over the deck
    hsp = (0.0, 90.0, 180.0, 270.0)
    k = clear_of([[A.down(on_ring + (0, 0, 290.5), spin=sp), A.down(on_ring + (0, 0, 30.5), spin=sp)]
                  for sp in hsp])
    T_r = A.down(on_ring + (0, 0, 30.5), spin=hsp[k])
    CAM_XRFL = [tuple(port_w + (1150, -1450, 950)), tuple(port_w + (0, -120, 60)), (0, 0, 1)]
    go_to(sh(T_r, (0, 0, 260)), T_r, secs=2.2, cam=CAM_XRFL)
    lin(sh(T_r, (0, 0, 40)), 1.4)
    lin(T_r, 0.6)
    grip(0.45)
    rb.release(ring_g)
    lin(sh(T_r, (0, 0, 260)), 1.2)
    park(1.4)
    status(Arm="parked", XRF="loaded")
    step(1.0, None, hold=0.1, cam=CAM_XRF)
    st["cap"] = ("Hatch shut. The ring lowers the cup into the chamber, film down over the tube and the detector, and the "
                 "port shuts; the chamber fills with helium, which keeps loose powder in place and lets the light "
                 "elements' X-rays through.")
    CAM_XRFI = [tuple(port_w + (1150, -850, 230)), tuple(port_w + (0, 0, -110)), (0, 0, 1)]
    step(1.2, xrf.move({"hatch": (1.0, 0.0)}), hold=0.1, cam=CAM_XRFI)
    step(3.6, xrf.move({"ring": (RING_UP, 1.0)}), hold=0.6,
         labels=[("lift ring, taking the cup down", tuple(port_w + (0, 0, -60)), (0.20, 0.30)),
                 ("X-ray tube, detector", tuple(port_w + (0, 0, -230)), (0.62, 0.80))])
    step(0.8, xrf.move({"port": (1.0, 0.0)}), hold=0.8)
    st["cap"] = ("The beam, drawn see-through: up to 50 kV from the tube; each element answers with its own X-ray lines, "
                 "which the silicon drift detector counts.")
    status(XRF="measuring, He")
    step(2.4, RB.both(xrf.move({"beam": (0.0, 1.0)}), clock("S2 PUMA", 0.0, 4.0)), hold=0.2)
    st["cap"] = ("The spectrum and a composition against Al 4047's limits. ILLUSTRATIVE: the line energies are real, the "
                 "heights and the numbers are made up for the picture; no XRF of this powder exists yet.")
    step(1.2, RB.both(panel("xrf", 0.0, 1.0), clock("S2 PUMA", 4.0, 8.0)), hold=4.0)
    step(1.2, RB.both(panel("xrf", 1.0, 0.0), xrf.move({"beam": (1.0, 0.0), "~lid": (1.0, 0.0), "~body": (1.0, 0.0)}),
                      clock("S2 PUMA", 8.0, 10.0)), hold=0.2)
    ov.key, ov.clock = None, None
    status(XRF="done", Trays="M to its slot")
    st["cap"] = "Tray M goes back to its slot; the cup stays in the S2 PUMA until it is unloaded with the next batch."
    L.store("M", st["lbl"], st["cap"], fast=0.55, hold=0.1, cam=CAM_2)

    # ------------------------------------------------------------------ 7. the record
    st["lbl"] = f"7/{n}"
    status(XRF="", Trays="all in their slots", Sample="checked: size, phases, shape, composition")
    st["cap"] = ("The powder checked while its plate printed: its size distribution, its phases, its shape and its "
                 "composition, each tray brought to an opening only when it was needed. Chapter 5 takes the printed "
                 "plate out of the MIDI.")
    step(2.4, None, hold=3.0, cam=[(X2 / 2 + 1500, -5600, 2700), (X2 / 2, -1300, 1150), (0, 0, 1)])
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm", flush=True)
    out = sc.save()
    if not (PREVIEW or AUDIT or CLEAN):
        print(line.mp4_to_gif(OUT / "mp4" / f"{NAME}.mp4", OUT / f"{NAME}.gif", fps=4, width=560, lossy=100),
              flush=True)
    return out


def _level_y() -> np.ndarray:
    """A level tool frame pointing along the part's +y (into the machine), its fingers closing along the part's x and
    its y down: P.tcp_frame's convention for a level approach (spin 0), at the origin."""
    M = P.tcp_frame((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 0.0)
    return M


if __name__ == "__main__":
    print(movie(), flush=True)
