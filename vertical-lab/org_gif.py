"""The org page's GIF, remade in the lab as this branch has it: ``vertical-cloud-lab/.github``'s
``profile/vertical-lab.gif`` ("In a vertical lab, equipment is brought to the operator", PR #318).

Round 4 (PR #329, Sterling, 2026-11-06: "you should have started backed off to see the full overview and then zoomed
in to show what's going on in more detail. It would be better to show the arm interacting with the atomizer (using the
latest modeling of the atomizer ...) instead of interaction with the sieving station, which doesn't really make sense
to do contextually. Wouldn't it be more interesting to show loading up a charge cup with the desired powder doses and
then taking it over to the atomizer to be atomized?"). One Shuttle, loaded as the set-up loads it (``animate.lab_scene``,
Shuttle 1's trays A-F and J), no pallet racking, no second Shuttle and none of its trays (round 2). One loop, which ends
where it starts:

1. the whole lab, wide: the Shuttle, the rePowder atomizer, the sieving cell, the MiR250 + UR10e docked at the
   Shuttle's opening. The camera closes in on the opening while the VLM brings tray B, the powder doser, down;
2. at tray B (chapter 1's tray, ``alloy_charge.Charge``: the charge rack, the vacuum press, the multi-doser v5 on its
   HR-202i), the arm takes an empty 5N Al charge cup out of the rack and stands it on the fork of the doser's vessel
   shuttle, which carries it in onto the pan. The doser doses the run's two powders into it by weight, one module at a
   time: Si (3.92 g, 26.8 mm up the bore), then the AlSi10Mg top-up (3.91 g, to 46.1 mm). The camera goes in to the
   pan, and the cup is drawn cut open while it fills. The shuttle brings it out and the arm stands it in a pocket of the
   cup carrier on the MiR's cabinet (chapter 2's carrier);
3. tray B goes back up while the MiR drives to the rePowder (PR #327's refined model: its lid hinged at the back, the
   draw latch and the pneumatic locking bolt as joints, ``repowder/model.py``);
4. at the rePowder, the bolt goes back, the arm pulls the latch's lever out and lifts the lid by its knob, past its
   balance point to RP_LID_U of its swing. With chapter 2's loading tong it takes the cup off the carrier and carries
   it down #222's path into the crucible (``alloy_atomize.tong_path``: tipped 4.1 deg past the sealing rod's adapter,
   then upright onto the floor cone), puts the tong back, shuts the lid and the latch, and the bolt goes in;
5. the rePowder, cut open, melts the cup and atomizes it (a time-lapse, ``Melt``: the coil, the cup glowing and
   slumping into the pool, the sealing rod up, the stream onto the vibrating plate, droplets, the powder in the
   container), while the MiR drives back to the opening; then the camera pulls back out to the wide view.

The last frame is the first one again: the MiR at the opening with its arm parked, tray B in its slot, the rePowder
shut and cold. What differs is too small to see from there: one cup fewer in tray B's rack, and powder in the rePowder's
container. The GIF plays everything at SPEED x the modelled times and says so; the atomizer's run, half an hour or so,
is compressed much further, and its label says that.

Drawn differently for this shot only (all drawing choices):
- Shuttle 2 is left out with its trays, the pallet racking and the second MiR unit (round 2); the south row's floor
  machines and its overhead utilities too (SOUTH_OUT, Y_CUT), since the wide view looks across where they stand.
- The VLM's camera target stands at the opening's right instead of its left (TARGET_DX, round 2): coming from the
  rePowder, a unit drives in from the left.
- One cup goes into the crucible, where the lab loads four a run (byu-vcl PR #318), and the melt is drawn for one
  cup's 43 g. Its plug isn't fitted or pressed (chapter 1 does both, on the same tray); the cup goes over open.
- The lid opens to RP_LID_U of the model's 105 deg: from where the MiR stops, the arm can't follow the knob further
  (the lid is past its balance point well before that: its centre of mass passes over the hinge at about 66 deg).
- The arm works the latch and the lid on its own (chapter 2 has a second unit hold the lid down while the latch lets
  go).

    VIZ3D_FPS=12 xvfb-run -a python3 org_gif.py views    # the views, as stills -> /tmp/org_gif_views.png
    ORG_STRIDE=24 VIZ3D_FPS=12 xvfb-run -a python3 org_gif.py   # every 24th frame only -> /tmp/org_stride/
    ARM_AUDIT=1 VIZ3D_FPS=12 xvfb-run -a python3 org_gif.py # no render: every frame's arm checked -> out/collisions/
    VIZ3D_FPS=12 xvfb-run -a python3 org_gif.py          # -> out/mp4/<NAME>.mp4, out/<NAME>.json
    ORG_PART=a:b ORG_NAME=<NAME>_p0 ...                  # render frames a..b-1 only (the rest are counted, not drawn)
    python3 org_gif.py join <NAME>_p0 <NAME>_p1 ...      # the parts -> out/mp4/<NAME>.mp4, out/<NAME>.json
    ORG_AUDIT_PART=a:b ARM_AUDIT=1 ...                   # audit frames a..b-1 -> /tmp/org_audit/<a>.json
    python3 org_gif.py audit_join                        # the audited parts -> out/collisions/<NAME>.json
    python3 org_gif.py gif                               # -> out/<NAME>.gif (SPEED x), its still, mp4/<NAME>_readme.mp4
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import tempfile

import numpy as np

NAME = os.environ.get("ORG_NAME", "org_vertical_lab")   # another name renders beside a running pass, without clashing
TITLE = "In a vertical lab, equipment is brought to the operator"
SPEED = 1.5          # the GIF plays the clip at this many times its modelled speed, and says so (12 fps x 1.5: 18 fps,
                     # frame delays of 6 and 5 cs in turn)
GIF_W = 1280         # px; the org README shows it about 830 px wide, so this stays sharp on a 2x display
TEXT = 1.45          # the overlay's text, against the scenes' 720p sizes: the README shows the GIF at about 0.65x
S1_TRAYS = "ABCDEFJ"     # Shuttle 1's trays (setup_lab.TRAYS): the only ones loaded


def _cam(f, az, el, d, va):
    """A view: the camera `d` mm from focal point `f`, `az` degrees right of straight on (from -y) and `el` up."""
    a, e = math.radians(az), math.radians(el)
    return [(f[0] + d * math.sin(a) * math.cos(e), f[1] - d * math.cos(a) * math.cos(e), f[2] + d * math.sin(e)),
            tuple(f), (0, 0, 1), va]


RP_AT = (-3775.0, -1700.0)       # animate.REPOWDER_AT: the rePowder model's origin, the furnace axis on the floor
# the views: camera position, focal point, up (mm; Shuttle 1's centre at the origin, its opening facing -y), view angle
CAMS = {
    "wide": _cam((-1500.0, -1000.0, 1350.0), 2.0, 17.0, 11500.0, 34.0),    # the Shuttle, the rePowder, the cell
    "trayB": _cam((-60.0, -1480.0, 960.0), 8.0, 20.0, 2900.0, 27.0),       # tray B at the opening, the arm, the MiR
    "dose": None,                     # the doser's pan from the front right, set once tray B is at the opening
    "rp": _cam((RP_AT[0] - 40.0, RP_AT[1] - 420.0, 1150.0), 22.0, 16.0, 3100.0, 27.0),   # the arm at the rePowder
    "bore": _cam((RP_AT[0] + 0.0, RP_AT[1] - 30.0, 1300.0), -25.0, 48.0, 1050.0, 27.0),  # down into the crucible
    "cut": _cam((RP_AT[0] + 60.0, RP_AT[1] + 0.0, 860.0), 10.0, 6.0, 2350.0, 27.0),      # the rePowder cut open
}
CAM = "wide"
# The camera stands behind the south row (its fronts at y = -6238), so the row's overhead utilities (its cable tray at
# 3.2 m with its network cable, hangers, drops and junction boxes, the DED's argon run, the fume hood's duct;
# setup_lab.utilities) and its floor machines (SOUTH_OUT) would stand between it and Shuttle 1. For this shot they are
# left out: every utility cell south of Y_CUT, and every FLOOR_PLAN station in row "S". The north row's stay.
Y_CUT = -4000.0
SOUTH_OUT = bool(int(os.environ.get("ORG_SOUTH_OUT", "1")))
TARGET_DX = 2 * 1330.0           # the VLM's camera target, from x = -1330 (setup_lab.TARGET_AT) to +1330
# the cycle
CUP = 3                          # tray B's rack seat of the cup the run takes: the fourth 5N Al cup (alloy_charge.SLOTS)
CUP_AT = 0                       # its place in the crucible: alloy_atomize.CUP_ANGLES[0], 145 deg, at the back, clear
                                 # of the sealing-rod lever (which lies along +x)
CARRIER_K = 0                    # the carrier pocket it rides in
GRASP_DOWN = 48.0                # a cup taken from above, the pads' centre 48 mm up it (its top 63.5 mm up)
OPEN_CUP = 0.66                  # alloy_charge.OPEN_CUP: 31.6 mm between the pads, clear of the next cup in the rack
GRIP_CUP = 0.80                  # on the 19.05 mm cup (ur_arm.gripper_fk: gap = 28 - 90 (c - 0.70))
RP_STOP = (RP_AT[0] - 120.0, -2380.0)   # the MiR at the rePowder, heading 0: from here the arm follows the latch's
                                 # lever and the lid's knob (an IK sweep of MiR stops, 2026-11-06)
RP_LID_U = 0.86                  # the lid opens this share of the model's 105 deg (90 deg): further, the knob leaves the
                                 # arm's reach from RP_STOP
LATCH_U = 0.5                    # the latch's lever swings out this share of its 95 deg: the loop is well off the keeper
LATCH_AT = (24.0, 0.85, 45.0)    # its grasp: the pads' centre 24 mm out from the furnace's face, 0.85 of the lever up
                                 # from its pivot, the tool tipped 45 deg down from level (fingers on the two flanges)
GRIP_LATCH, OPEN_LATCH = 0.59, 0.45   # the lever's 38 mm channel; 50 mm open
GRIP_KNOB = 0.70                 # the lid's 28 mm ball knob
KNOB_OUT = 4.0                   # the knob taken level from the front, the pads' centre 4 mm in front of the ball's
ARM_S = (1.6, 0.9, 0.5, 0.8)     # a pick or a place: joint move, line in, grip, line out (s): the 9:09 clip's
                                 # (animate.pick/place)
HOLD = 0.1
DOSE_F = 0.6                     # the doser's moves at this share of chapter 1's times (its first cup is shown at 0.55)
MIR_V = 1500.0                   # mm/s at most, with the MiR250's 0.3 m/s^2 ramps (props.ramp_secs)
ATOM_SECS = 14.0                 # the atomizer's run, half an hour or so, in this many seconds of the clip (a time-lapse)


def _load_s1() -> dict:
    """setup_lab.load_all without fab_tour's models: they are trays G-I's, all on Shuttle 2."""
    import setup_lab as SL
    idata = SL.tour_load_safe()
    idata.update(SL.load_r7())
    idata.update(SL.r7_stand_ins(idata))
    return idata


class Melt:
    """The rePowder's run as a frame hook (Scene.frame_hooks), ATOM_SECS from start(): the furnace and chamber cut open,
    the coil on, the cup glowing and slumping into the pool, the sealing rod up, the stream onto the vibrating plate,
    droplets flying off it and the powder heap rising in the container; then all off, the cut shut. alloy_atomize's
    effects (its port of #124's training animation), under names of their own, sized for one cup."""

    def __init__(self, sc, cup_group):
        import pyvista as pv

        import alloy_atomize as AT
        import charge as C
        from scene import T
        M = AT.M
        self.sc, self.AT, self.M, self.cg = sc, AT, M, cup_group
        v = M.variant_meshes()
        self.pool_levels, self.pool_meshes = v["pool_levels"], v["pool_half"]
        self.pw_levels, self.pw_meshes = v["powder_levels"], v["powder_half"]
        sc.add("rp pool", self.pool_meshes[0][0], AT.MELT, AT.g("crucible"), ambient=0.75, diffuse=0.45, specular=0.5)
        sc.add("rp pool#cut", self.pool_meshes[0][1], AT.lighter(AT.MELT, 0.3), AT.g("crucible"), ambient=0.85,
               diffuse=0.3, specular=0.0, smooth_shading=False)
        col = C.POWDERS["Al"][0]
        sc.add("rp powder", self.pw_meshes[0][0], col, AT.g("container"), specular=0.05, ambient=0.3)
        sc.add("rp powder#cut", self.pw_meshes[0][1], AT.lighter(col, 0.25), AT.g("container"), smooth_shading=False,
               ambient=0.6, specular=0.0)
        h = AT.STREAM_TOP - M.IMPACT[2]
        sc.add("rp stream", pv.Cylinder(center=(0, 0, M.IMPACT[2] + h / 2), direction=(0, 0, 1), radius=1.4, height=h,
                                        resolution=16), AT.MELT, "rp_stream", ambient=0.85, diffuse=0.4, shown=False)
        sc.parent["rp_stream"] = "rp"
        self.spray = AT.Particles(sc, "rp spray", (0.40, 0.41, 0.46), size=5.5)
        self.drops = AT.Particles(sc, "rp drops", AT.MELT, size=7.0, slowmo=0.35, seed=2)
        # one cup's metal: the pool and the powder heap at the levels its 43 g makes (alloy_atomize.POOL_LEVEL and
        # POWDER_END are for four)
        m = AT.RUN["charge_g"] / 4
        self.pool_top = AT.level_for(AT.pool_volume, m / AT.AL_LIQUID, -14.0, 37.0)
        self.powder_top = AT.level_for(AT.powder_volume, m * 0.912 / AT.POWDER_BULK, 3.0, 70.0)
        self.n0 = self.n1 = None
        self.cup_names = [n for n, g in sc.group_of.items() if g in (cup_group, f"{cup_group}_pw", f"{cup_group}_pw2")]
        self.cup_col = {n: sc.color.get(n) for n in self.cup_names}
        self.T = T
        self.pool(-30.0)
        self.powder(-1.0)

    def pool(self, level, color=None):
        sc, AT = self.sc, self.AT
        color = color or AT.MELT
        on = level > self.pool_levels[0] - 0.5
        i = int(np.argmin(np.abs(self.pool_levels - level)))
        sc.set_mesh("rp pool", self.pool_meshes[i][0])
        sc.set_mesh("rp pool#cut", self.pool_meshes[i][1])
        for n, c in (("rp pool", color), ("rp pool#cut", AT.lighter(color, 0.3))):
            sc.alpha[n] = 1.0 if on else 0.0
            sc.color[n] = c

    def powder(self, level):
        sc = self.sc
        on = level >= self.pw_levels[0]
        i = int(np.argmin(np.abs(self.pw_levels - level)))
        sc.set_mesh("rp powder", self.pw_meshes[i][0])
        sc.set_mesh("rp powder#cut", self.pw_meshes[i][1])
        sc.alpha["rp powder"] = sc.alpha["rp powder#cut"] = 1.0 if on else 0.0

    def start(self, sc):
        self.n0 = sc.n
        self.seat = sc.gmat[self.cg].copy()

    def __call__(self, sc):
        from scene import FPS, S, window
        if self.n0 is None or (self.n1 is not None and sc.n > self.n1 + 1):
            return
        AT, M = self.AT, self.M
        u = min(1.0, max(0.0, (sc.n - self.n0) / (ATOM_SECS * FPS)))
        AT.set_cut(sc, window(u, 0.0, 0.08) * (1.0 - window(u, 0.92, 1.0)), AT.FUR_G + AT.CH_G)
        heat = window(u, 0.08, 0.30)
        glow = heat * (1.0 - window(u, 0.80, 0.90))
        AT.coil_glow(sc, glow)
        temp = 24.0 + (720.0 - 24.0) * heat
        f = 1.0 - 0.95 * window(u, 0.28, 0.42)              # the cup slumps into the pool
        sc.gmat[self.cg] = self.seat @ S((1 + 0.12 * (1 - f), 1 + 0.12 * (1 - f), f))
        for n in self.cup_names:
            sc.alpha[n] = (sc.alpha[n] if f > 0.07 else 0.0) if u < 0.999 else sc.alpha[n]
            if sc.alpha.get(n, 0.0) > 0.0:
                sc.color[n] = AT.temp_color(temp)
                sc.ambient[n] = 0.18 + 0.55 * max(0.0, min(1.0, (temp - 450) / 400))
        drain = window(u, 0.50, 0.80)
        level = (-14.0 + (self.pool_top + 14.0) * window(u, 0.29, 0.42)) * (1.0 - drain) + (-12.0) * drain
        self.pool(level if 0.29 < u < 0.82 else -30.0)
        AT.rod_lift(sc, 12.0 * window(u, 0.44, 0.50) * (1.0 - window(u, 0.80, 0.86)))
        flow = window(u, 0.48, 0.52) * (1.0 - window(u, 0.78, 0.82))
        sc.alpha["rp stream"] = 1.0 if flow > 0.02 else 0.0
        sc.gmat["rp_stream"] = S((1.0, 1.0, max(flow, 0.01)), (0, 0, AT.STREAM_TOP))
        on = 0.50 < u < 0.82
        sc.gmat[AT.g("connector")] = self.T(M.STACK_DIR * (1.2 if (on and (sc.n * 15 // FPS) % 2) else 0.0))
        if 0.52 < u < 0.80:
            self.spray.emit_spray(int(round(30 * AT.PER_FRAME)))
            if sc.n % max(1, 3 * FPS // 15) == 0:
                self.drops.emit_drops(2, M.IMPACT + np.array([0, 0, 3]), M.PLATE_UP * 250 + M.STACK_DIR * 500)
        if u > 0.88:
            self.spray.clear()
            self.drops.clear()
        else:
            self.spray.step()
            self.drops.step()
        self.powder(-1.0 if u < 0.53 else 3.0 + (self.powder_top - 3.0) * window(u, 0.53, 0.86))
        if u >= 1.0 and self.n1 is None:
            self.n1 = sc.n


def build(data):
    """Shuttle 1 in the lab (animate.lab_scene), stripped (strip, floor_edits, clear_view), with chapter 1's charge on
    tray B (alloy_charge.Charge: the rack of cups and plugs, the vacuum press, the MiR's cup carrier), the rePowder by
    its parts (alloy_atomize.load_rp, PR #327's model), chapter 2's loading tong on the MiR and the melt (Melt); and
    the cycle's start: the MiR at the opening, its arm parked, trays A and B in their slots, the extractor at B's.
    -> (scene, lab, charge, melt)."""
    import alloy_atomize as AT
    import alloy_charge as AC
    import animate as A
    import setup_lab as SL
    import vlm as V
    import warehouse as W
    os.environ.setdefault("VLAB_ONLY_TRAYS", S1_TRAYS)
    SL.load_all = _load_s1
    sc, L = A.lab_scene(data, name=NAME, title=TITLE)
    sc.gif = False                                     # gif() makes the GIF from the MP4
    sc.text_scale = TEXT
    L.show_gauges = False
    L.extra_gauges = []
    strip(sc, L)
    floor_edits(sc)
    clear_view(sc, L)
    u = L.units[0]
    u.set(W.dock_pose("vlm"))
    # chapter 1's charge on tray B. Its MiR group "amr" rides on this unit's cabinet; the unit's one-vial holder goes
    sc.parent["amr"] = L.amr_group
    sc.gmat["amr"] = np.eye(4)
    for nm in (f"{u.name}/holder",):
        sc.alpha[nm] = 0.0
        sc.base_alpha[nm] = 0.0
    K = AC.Charge(sc, L)
    for nm in ("vial/glass", f"{L.eq_groups['B'][0]}/rack", f"{L.eq_groups['B'][0]}/vials"):
        sc.base_alpha[nm] = 0.0
    sc.parent["stream"] = K.rig
    L.powder_h = L.liquid_h = 0.0
    L.set_fill()
    # the rePowder by its parts; the merged copy goes
    for nm in list(sc.actors):
        if nm.startswith("repowder:"):
            sc.alpha[nm] = 0.0
            sc.base_alpha[nm] = 0.0
    AT.load_rp(sc, ghost={"stack_cover": 0.35})
    L.tong_home = AT.add_tong(sc, None)
    fx = Melt(sc, f"cup{CUP}")
    # trays A and B in their slots, the extractor at B's (where the cycle leaves it), the shutter shut
    L.use(1)
    for k in ("A", "B"):
        L.tray[k] = [*V.SLOTS[A.HOME[k]]]
        L.where[k] = A.HOME[k]
    L.lift_z = V.SLOTS[A.HOME["B"]][1]
    L.shutter = 0.0
    L.skin(1.0)(1.0)
    L.apply_state()
    return sc, L, K, fx


def strip(sc, L):
    """Leave out Shuttle 2 (its u2_* groups, its bay camera, its trays and everything riding on them), the pallet
    racking and the second unit."""
    import setup_lab as SL
    import vlm as V
    s2 = {f"tray_{k}" for k, (slot, _) in SL.TRAYS.items() if V.SLOT_SHUTTLE.get(slot, 1) == 2}
    other = [u.name for u in L.units[1:]]
    out = set()
    for g in set(sc.group_of.values()):
        h, n = g, 0
        while h is not None and n < 64:
            if h in s2 or h.startswith(("u2_", "baycam2", "baycamrig2")) or h == "racking" or \
                    any(h == o or h.startswith(o + "_") or h.startswith(o + "ur_") for o in other):
                out.add(g)
                break
            h, n = sc.parent.get(h), n + 1
    for nm, g in sc.group_of.items():
        if g in out:
            sc.alpha[nm] = 0.0
            sc.base_alpha[nm] = 0.0


def floor_edits(sc):
    """The floor marks for Shuttle 2 go (its dock tape, its camera target, the tape round its footprint), and the VLM's
    camera target moves from the opening's left to its right (TARGET_DX): the merged meshes warehouse.Floor._tape and
    setup_lab.footprints draw them in, edited in place."""
    import pyvista as pv

    import setup_lab as SL
    import vlm as V
    x2 = V.SHUTTLE_X[2]
    tx, ty = SL.TARGET_AT["vlm"]
    xo, yo = V.UNIT_W / 2 + V.SKIN + 300.0, V.UNIT_D / 2 + V.SKIN + 300.0
    for nm in ("dock tape", "target posts", "target black", "target white", "footprints"):
        if nm not in sc.actors:
            continue
        mesh = pv.wrap(sc.actors[nm].GetMapper().GetInput()).copy()
        c = mesh.cell_centers().points
        if nm == "footprints":            # the tape round Shuttle 2's footprint (setup_lab.footprints)
            keep = np.flatnonzero(~((np.abs(c[:, 0] - x2) < xo) & (np.abs(c[:, 1]) < yo)))
        else:                             # its dock and its camera target
            keep = np.flatnonzero(~((np.abs(c[:, 0] - x2) < 1900) & (c[:, 1] > -2700) & (c[:, 1] < -1400)))
        if len(keep) < mesh.n_cells:
            mesh = mesh.extract_cells(keep).extract_surface(algorithm="dataset_surface")
        p = np.array(mesh.points)
        sel = (np.abs(p[:, 0] - tx) < 200) & (np.abs(p[:, 1] - ty) < 200)
        p[sel, 0] += TARGET_DX
        mesh.points = p
        sc.set_mesh(nm, mesh)


def clear_view(sc, L=None):
    """Leave the south row's overhead utilities out of the shot (Y_CUT), and its floor machines (SOUTH_OUT); and the
    utilities' cells over Shuttle 2's footprint, its cable drops."""
    import pyvista as pv

    import setup_lab as SL
    import vlm as V
    F = getattr(L, "floor", None)
    if SOUTH_OUT and F is not None:
        for key, (_, row, *_r) in SL.FLOOR_PLAN.items():
            if row == "S" or key == "vlm2":
                for nm in F.groups.get(key, []):
                    sc.alpha[nm] = 0.0
    x2, half = V.SHUTTLE_X[2], V.UNIT_W / 2 + V.SKIN
    for nm in [n for n in sc.actors if n.startswith("util/")]:
        mesh = pv.wrap(sc.actors[nm].GetMapper().GetInput())
        if mesh.n_cells == 0:
            continue
        c = mesh.cell_centers().points
        drop = (c[:, 1] <= Y_CUT) | ((np.abs(c[:, 0] - x2) < half) & (c[:, 1] > -V.UNIT_D / 2 - 400) &
                                     (c[:, 2] < 3000.0))
        keep = np.flatnonzero(~drop)
        if len(keep) == mesh.n_cells:
            continue
        if len(keep) == 0:
            sc.alpha[nm] = 0.0
            continue
        sc.set_mesh(nm, mesh.extract_cells(keep).extract_surface(algorithm="dataset_surface"))


def set_cam(sc, key):
    cam = CAMS[key]
    sc.cam = [tuple(float(v) for v in c) for c in cam[:3]]
    sc.view_angle = cam[3] if len(cam) > 3 else 30.0


def views():
    """Stills of the views (ORG_VIEWS=a,b,... picks some), with the scene at the cycle's start."""
    from PIL import Image, ImageDraw

    import lab
    sc, L, K, fx = build(lab.meshes())
    keys = [k for k in CAMS if CAMS[k] and (not os.environ.get("ORG_VIEWS") or k in os.environ["ORG_VIEWS"].split(","))]
    shots = []
    for key in keys:
        set_cam(sc, key)
        shots.append((key, Image.fromarray(sc.render_base())))
    tw, th = 640, 360
    cols = 3
    sheet = Image.new("RGB", (tw * cols, th * ((len(shots) + cols - 1) // cols)), "white")
    d = ImageDraw.Draw(sheet)
    for i, (lbl, im) in enumerate(shots):
        x, y = (i % cols) * tw, (i // cols) * th
        sheet.paste(im.resize((tw, th)), (x, y))
        d.text((x + 6, y + 4), lbl, fill=(200, 0, 0))
        im.save(f"/tmp/org_gif_{lbl}.png")
    sheet.save("/tmp/org_gif_views.png")
    sc.pl.close()
    print("views -> /tmp/org_gif_views.png", flush=True)


# ============================================================================================ running moves side by side
class Track:
    """A generator of (seconds, factory) segments run against a clock. factory() -> update(u) or None is called when
    its segment starts, so each move starts from the state the ones before it left; the generator's own code between
    its yields (a grasp, a tray's lamp) runs as one segment ends and the next starts."""

    def __init__(self, gen):
        self.gen, self.t0, self.dur, self.up, self.done = gen, 0.0, 0.0, None, False
        self._next(0.0)

    def _next(self, t0):
        try:
            dur, fac = next(self.gen)
        except StopIteration:
            self.done, self.up = True, None
            return
        self.t0, self.dur = t0, float(dur)
        self.up = fac() if fac is not None else None

    def end(self):
        return self.t0 + self.dur

    def advance(self, t):
        from scene import ease
        while not self.done:
            if t < self.end() - 1e-9:
                if self.up is not None:
                    self.up(ease((t - self.t0) / self.dur))
                return
            if self.up is not None:
                self.up(1.0)
            self._next(self.end())


def run(sc, main, *background):
    """Run the `main` track step by step (Scene.step: one step a segment, each eased) with the `background` tracks
    advancing on the same clock; then whatever is left of the background ones."""
    import props as P
    from scene import FPS
    bg = [Track(g) for g in background]
    clock = 0.0

    def step(d, up):
        nonlocal clock
        n = max(1, int(round(d * FPS)))
        t0, dd = clock, n / FPS

        def upd(e):
            if up is not None:
                up(e)
            for b in bg:
                b.advance(t0 + P.unease(e) * dd)
        sc.step(sc.label, "", dd, upd, hold=0.0)
        clock += dd
    for dur, fac in main:
        step(dur, fac() if fac is not None else None)
    while any(not b.done for b in bg):
        d = min(b.end() for b in bg if not b.done) - clock
        if d < 0.5 / FPS:            # a segment ending within half a frame: finish it between frames
            for b in bg:
                if not b.done and b.end() - clock < 0.5 / FPS:
                    b.advance(b.end() + 1e-6)
            continue
        step(d, None)


def wait(seconds):
    yield seconds, None


def call(f):
    """A track step that only runs f (a caption, labels, a lamp) between the segments around it."""
    f()
    return
    yield


def both(*fs):
    def up(u):
        for f in fs:
            if f is not None:
                f(u)
    return up


def pick(rb, M_grasp, M_pre, group, grip, opening=0.0, s=ARM_S):
    """animate.pick as a track: joint move to M_pre opening the gripper to `opening`, line to M_grasp, close, take
    `group`, line back."""
    yield s[0], lambda: both(rb.joint_to(Tw=M_pre), rb.grip_to(opening))
    yield HOLD, None
    yield s[1], lambda: rb.line_to(M_grasp)
    yield HOLD, None
    yield s[2], lambda: rb.grip_to(grip)
    rb.grasp(group)
    yield HOLD, None
    yield s[3], lambda: rb.line_to(M_pre)
    yield HOLD, None


def place(rb, M_place, M_pre, new_parent, opening=0.0, s=ARM_S):
    """animate.place as a track; the gripper opens to `opening` to let go."""
    yield s[0], lambda: rb.joint_to(Tw=M_pre)
    yield HOLD, None
    yield s[1], lambda: rb.line_to(M_place)
    yield HOLD, None
    yield s[2], lambda: rb.grip_to(opening)
    rb.release(new_parent)
    yield HOLD, None
    yield s[3], lambda: rb.line_to(M_pre)
    yield HOLD, None


def park(rb, secs=1.2):
    import animate as A
    yield secs, lambda: rb.joint_to(A.PARK_RAD)
    yield HOLD, None


def fetch(L, k):
    """setup_lab.TwoLab.fetch as a track: the same moves and times."""
    import vlm as V
    L.use(L.unit.get(k, 1))
    ys, zs = V.SLOTS[L.where[k]]
    yt, zt = V.SLOTS["open"]
    if abs(L.lift_z - zs) > 1:
        yield max(0.6, abs(L.lift_z - zs) / 1333), lambda: L.lift_to(zs)
        yield 0.1, None
    L.where[k] = None
    L.apply_state()
    yield 2.2, lambda: L.slide(k, 0.0)
    yield 0.1, None
    yield max(0.6, abs(zs - zt) / 1333), lambda: L.lift_to(zt, carry=k)
    yield 0.1, None
    yield 0.7, lambda: L.shut(1.0)
    yield 2.2, lambda: L.slide(k, yt)
    yield 0.7, lambda: L.shut(0.0)
    L.where[k] = "open"
    L.apply_state()
    yield 0.3, None


def store(L, k):
    """setup_lab.TwoLab.store as a track."""
    import animate as A
    import vlm as V
    L.use(L.unit.get(k, 1))
    L.where[k] = None
    L.apply_state()
    ys, zs = V.SLOTS[A.HOME[k]]
    yield 0.7, lambda: L.shut(1.0)
    yield 2.2, lambda: L.slide(k, 0.0)
    yield 0.7, lambda: L.shut(0.0)
    yield 0.1, None
    yield max(0.6, abs(L.lift_z - zs) / 1333), lambda: L.lift_to(zs, carry=k)
    yield 0.1, None
    yield 2.2, lambda: L.slide(k, ys)
    L.where[k] = A.HOME[k]
    L.apply_state()
    yield 0.3, None


def drive(L, to, follow=None, cams=None):
    """The docked unit to `to` (x, y; heading 0) along props.s_curve, from rest to rest at the MiR250's 0.3 m/s^2
    (props.ramp_frac); `follow` is a label's anchor (a list), moved with it. With `cams` (k0, k1), the camera goes from
    view k0 to view k1 at the MiR's own pace: the share of the way it has driven is the share of the way between."""
    import props as P
    u, rb, sc = L.units[0], L.robot, L.sc
    x0, y0, hd = u.pose
    at, ps, s = P.s_curve(x0, y0, to[0], to[1])
    d0 = None if follow is None else [follow[0] - x0, follow[1] - y0]

    def fac():
        def up(e):
            f = P.ramp_frac(P.unease(e), s[-1], MIR_V)
            x, y, h = at(float(np.interp(f * s[-1], s, ps)))
            u.set((x, y, h))
            if d0 is not None:
                follow[0], follow[1] = x + d0[0], y + d0[1]
            if cams is not None:
                cam_between(sc, cams[0], cams[1], f)
            if rb.held is not None:
                rb.set()
        return up
    yield max(1.4, P.ramp_secs(s[-1], MIR_V)), fac
    yield HOLD, None


def cam_between(sc, k0, k1, f):
    """The camera f of the way from view k0 to view k1 (position, focal point and view angle, each in a line)."""
    a, b = CAMS[k0], CAMS[k1]
    sc.cam = [tuple(float(p + (q - p) * f) for p, q in zip(pa, pb)) for pa, pb in zip(a[:3], b[:3])]
    sc.view_angle = float(a[3] + (b[3] - a[3]) * f)


def cam_to(sc, key, secs):
    """A track segment: the camera from wherever it is to view `key`."""
    def fac():
        a = [np.array(v, float) for v in sc.cam]
        va = sc.view_angle
        b = CAMS[key]

        def up(e):
            sc.cam = [tuple(p + (np.array(q, float) - p) * e) for p, q in zip(a, b[:3])]
            sc.view_angle = float(va + (b[3] - va) * e)
        return up
    yield secs, fac


# ============================================================================================ the parts of a long render
def frame_range(env):
    v = os.environ.get(env)
    if not v:
        return None
    a, b = v.split(":")
    return int(a), int(b)


def part_snap(sc, a, b):
    """Draw only frames a..b-1 (ORG_PART): the others are counted, not drawn, so parts rendered side by side join into
    the whole clip."""
    snap = sc.snap

    def f(n=1):
        n0 = sc.n
        k = len(range(max(n0, a), min(n0 + n, b)))
        if k == 0:
            sc.want_still = False
            sc.n = n0 + n
            return None
        sc.n = max(n0, a)
        hi = snap(k)
        sc.n = n0 + n
        return hi
    sc.snap = f


def stride_snap(sc, every, out="/tmp/org_stride"):
    """Draw only every `every`-th frame, to `out` as JPEGs (ORG_STRIDE): the whole loop checked in a few minutes."""
    import time

    from PIL import Image
    os.makedirs(out, exist_ok=True)
    t0 = time.time()

    def f(n=1):
        n0 = sc.n
        hit = [k for k in range(n0, n0 + n) if k % every == 0]
        if hit:
            base = sc.render_base()
            anchors = [sc.project(xyz) for _, xyz, _, _ in sc.labels]
            hi = sc.overlay(Image.fromarray(base), sc.text_scale, anchors)
            hi.convert("RGB").resize((960, 540)).save(f"{out}/{hit[0]:05d}.jpg", quality=82)
            print(f"stride: frame {hit[0]} ({sc.label}), {time.time() - t0:.0f} s", flush=True)
        sc.n = n0 + n
        return None
    sc.snap = f


def cam_up(sc, key):
    """An update(e) taking the camera from where it is now to view `key` (call it as its segment starts)."""
    a = [np.array(v, float) for v in sc.cam]
    va = sc.view_angle
    b = CAMS[key]

    def up(e):
        sc.cam = [tuple(p + (np.array(q, float) - p) * e) for p, q in zip(a, b[:3])]
        sc.view_angle = float(va + (b[3] - va) * e)
    return up


# ============================================================================================ the cycle
def movie():
    """The cycle, rendered real-time. The scene draws only the leader labels: the title, the step captions and the
    speed badge go in the GIF's header band (gif()), from the phases written into out/<NAME>.json."""
    import alloy_atomize as AT
    import alloy_charge as AC
    import alloy_press as AP
    import animate as A
    import carousel as CR
    import charge as C
    import lab
    import props as P
    import pyvista as pv
    import scene as SC
    import vlm as V
    import warehouse as W
    from scene import OUT, T
    M, RP = AT.M, AT.RP
    sc, L, K, fx = build(lab.meshes())
    sc.title = ""
    part, apart = frame_range("ORG_PART"), frame_range("ORG_AUDIT_PART")
    if os.environ.get("ORG_STRIDE") and not (SC.PREVIEW or SC.AUDIT):
        stride_snap(sc, int(os.environ["ORG_STRIDE"]))
    elif part and not (SC.PREVIEW or SC.AUDIT):
        part_snap(sc, *part)
    if apart and SC.AUDIT and sc.auditor is not None:      # this pass checks frames a..b-1 only
        aud = sc.auditor
        sc.frame_hooks[sc.frame_hooks.index(aud)] = lambda s, aud=aud: aud(s) if apart[0] <= s.n < apart[1] else None
    if os.environ.get("ARM_AUDIT_RENDER") and not (SC.PREVIEW or SC.AUDIT):
        import collide                      # ARM_AUDIT=1's audit in the render's own pass: one pass for both
        sc.auditor = collide.Auditor(sc)
        sc.frame_hooks.append(sc.auditor)
    sc.frame_hooks.insert(0, fx)            # the melt, before the audit sees the frame
    rb, car = L.robot, L.carousel
    cg = f"cup{CUP}"
    PR = AP.pressed_recipe()["runs"]["Al-10Si"]
    h_si, h_set = float(PR["column_mm_alloying"]), float(PR["column_mm_set"])
    set_cam(sc, CAM)
    sc.intro = 0.8
    phases = []

    def phase(text):
        phases.append(dict(start_frame=sc.n, text=text))

    def labels(*ls):
        sc.sticky_labels = list(ls)

    # ------------------------------------------------------------------ the labels (box: fractions of the frame; a
    # box left of the middle has its left edge at fx, one right of it its right edge; fy is its middle)
    dock = W.dock_pose("vlm")
    arm_at = [dock[0], dock[1] - 250.0, 1250.0]            # moves with the MiR (drive's `follow`)
    lbl_arm = ("the operator: a MiR250 + UR10e", arm_at, (0.40, 0.93))
    lbl_vlm = ("the VLM, a Kardex Shuttle XP 500:\nits trays come to the opening", (-700.0, -900.0, 2950.0),
               (0.985, 0.08))
    lbl_rp = ("AMAZEMET rePowder atomizer", (RP[0] + 120.0, RP[1] + 250.0, 1750.0), (0.02, 0.08))
    lbl_cell = ("sieving cell", (-1982.5, -1250.0, 1650.0), (0.30, 0.18))
    lbl_B = ("tray B at the opening:\nthe multi-doser v5 on its balance", tuple(K.bal_cup() + (150.0, 80.0, 560.0)),
             (0.985, 0.10))
    lbl_rack = ("charge cups, 5N Al", tuple(K.rack_cup(1) + (0.0, 0.0, 70.0)), (0.02, 0.62))
    lbl_cup = ("the cup, cut open: Si,\nthen the AlSi10Mg top-up", tuple(K.bal_cup() + (0.0, 0.0, 30.0)),
               (0.985, 0.72))
    lbl_latch = ("draw latch", tuple(RP + (M.latch_geom()["x"], -150.0, 1300.0)), (0.985, 0.62))
    lbl_lid = ("the lid, hinged at the back", tuple(RP + (-60.0, 0.0, 1560.0)), (0.02, 0.10))
    lbl_tong = ("loading tong", None, (0.985, 0.30))
    lbl_melt = ("the melt (time-lapse)", tuple(RP + (-10.0, 5.0, M.Z_CR + 10.0)), (0.02, 0.22))
    lbl_plate = ("droplets off the vibrating plate", tuple(RP + tuple(M.IMPACT + np.array([60.0, 0.0, -30.0]))),
                 (0.985, 0.50))
    lbl_pw = ("powder", tuple(RP + (M.CHUTE_X, 0.0, 230.0)), (0.985, 0.82))
    at_start = [lbl_vlm, lbl_rp, lbl_arm]
    labels(*at_start)

    # ------------------------------------------------------------------ 1. the whole lab; in to tray B as it comes down
    def overview():
        yield from call(lambda: phase("A vertical lab: its storage brings each instrument to the operator, a "
                                      "mobile robot arm."))
        yield 1.4, None
        yield from call(lambda: phase("Here it makes a charge for the atomizer. The VLM brings tray B, the powder "
                                      "doser, down."))
        yield from cam_to(sc, "trayB", 4.2)
        yield from call(lambda: labels(lbl_arm, lbl_B, lbl_rack))
    run(sc, overview(), fetch(L, "B"))
    CAMS["dose"] = _cam(tuple(K.bal_cup() + (0.0, 0.0, 60.0)), 38.0, 22.0, 950.0, 27.0)

    # ------------------------------------------------------------------ 2. the cup dosed: Si, then the top-up
    f = DOSE_F
    p_rack = K.rack_cup(CUP) + (0, 0, GRASP_DOWN)
    p_hand = K.hand_cup() + (0, 0, GRASP_DOWN)

    def dose_up(layer, h0, h1):
        spin0 = car.state["spin"]
        stt = car.to(spin=spin0 + 2 * math.pi * 2.0)         # eight quarter turns, a reading after each

        def up(u):
            stt(u)
            on = 1.0 if 0.05 < u < 0.95 else 0.0
            pts = AC.stream_points(L, K, CUP, u * 6.0, on)
            sc.alpha["stream"] = 1.0 if len(pts) else 0.0
            if len(pts):
                sc.set_mesh("stream", pv.PolyData(pts))
            k = min(1.0, max(0.0, (u - 0.12) / 0.83))
            if layer == 0:
                K._point[CUP] = k > 0.02
                K.powder_h[CUP] = h1 * max(0.0, (k - 0.08) / 0.92)
                K.powder_h2[CUP] = K.powder_h[CUP]
            else:
                K.powder_h2[CUP] = h0 + (h1 - h0) * k
            K.apply()
            K.cut(CUP, True, sleeve=None)
        return up

    def at_B():
        yield from call(lambda: phase("The arm stands an empty charge cup on the doser's shuttle, which carries it "
                                      "onto the balance."))
        yield from pick(rb, A.down(p_rack, spin=0.0), A.down(p_rack + (0, 0, 110), spin=0.0), cg, GRIP_CUP, OPEN_CUP)
        yield from place(rb, A.down(p_hand, spin=180.0), A.down(p_hand + (0, 0, 120), spin=180.0), car.fork_group,
                         OPEN_CUP)
        yield 1.2, lambda: both(rb.joint_to(A.PARK_RAD), car.to(side_door=CR.SIDE_OPEN), cam_up(sc, "dose"))
        yield from call(lambda: labels(lbl_cup))
        yield 1.6 * f, lambda: car.to(shuttle=0.0)
        yield 0.4 * f, lambda: car.to(fork=A.SET_U)
        car.reparent(cg, K.rig)
        yield 0.3 * f, lambda: car.to(fork=1.0)
        yield 1.3 * f, lambda: car.to(shuttle=1.0)
        yield 0.5 * f, lambda: car.to(side_door=0.0, fork=0.0)
        for layer, pname, h0, h1, text in (
                (0, "Si", 0.0, h_si, f"The doser weighs in the alloy's powders, one module at a time: "
                                     f"{PR['alloying_g']:.2f} g of Si ..."),
                (1, "AlSi10Mg", h_si, h_set, f"... then {PR['top_up_g']:.2f} g of AlSi10Mg on top, for Al-10Si.")):
            m = AC.MODULE[pname]
            yield from call(lambda text=text: phase(text))
            yield 2.2 * f, lambda m=m: car.to(shift=car.index_to(m), top_door=CR.TOP_OPEN)
            yield 1.2 * f, lambda: both(car.to(ext=CR.DOCK_EXT, magnet_on=True), car.ghost(0.18))
            yield 1.3 * f, lambda: car.to(tilt=CR.TILT)
            K.cut(CUP, True, sleeve=None)
            yield 3.4 * 0.8, lambda layer=layer, h0=h0, h1=h1: dose_up(layer, h0, h1)
            sc.alpha["stream"] = 0.0
            if layer == 0:
                K.powder_h[CUP] = h1
                K._point[CUP] = True
            K.powder_h2[CUP] = h1
            K.apply()
            K.cut(CUP, True, sleeve=None)
            yield 1.0 * f, lambda: car.to(tilt=0.0)
            yield 0.7 * f, lambda: car.to(spin=car.state["spin"] - 2 * math.pi)
            yield 0.9 * f, lambda: both(car.to(ext=0.0, magnet_on=False, top_door=0.0), car.ghost(1.0))
        K.cut(CUP, False, sleeve=None)
        yield from call(lambda: phase("The shuttle brings the charged cup out, and the arm stands it in the carrier "
                                      "on the robot."))
        yield 1.4, lambda: both(car.to(side_door=CR.SIDE_OPEN, fork=1.0), cam_up(sc, "trayB"))
        yield from call(lambda: labels(lbl_arm, lbl_B))
        yield 1.3 * f, lambda: car.to(shuttle=0.0)
        yield 0.3 * f, lambda: car.to(fork=A.SET_U)
        car.reparent(cg, car.fork_group)
        yield 0.4 * f, lambda: car.to(fork=0.0)
        yield 1.5 * f, lambda: car.to(shuttle=1.0)
        yield 0.5 * f, lambda: car.to(side_door=0.0)
        yield from pick(rb, A.down(p_hand, spin=180.0), A.down(p_hand + (0, 0, 120), spin=180.0), cg, GRIP_CUP,
                        OPEN_CUP)
        p_car = K.carrier_seat(CARRIER_K) + (0, 0, GRASP_DOWN)
        yield from place(rb, A.down(p_car, spin=0.0), A.down(p_car + (0, 0, 120), spin=0.0), "amr", OPEN_CUP)
        yield from park(rb)
    run(sc, at_B())

    # ------------------------------------------------------------------ 3. tray B back up; the MiR to the rePowder
    def go():
        yield from call(lambda: (phase("Tray B goes back into storage, and the robot takes the cup to the atomizer."),
                                 labels(lbl_arm)))
        yield from drive(L, RP_STOP, arm_at, ("trayB", "rp"))
    run(sc, go(), store(L, "B"))

    # ------------------------------------------------------------------ 4. at the rePowder: latch, lid, tong, cup in
    gl = M.latch_geom()

    def lid(s):
        sc.gmat[AT.g("hood")] = M.joint_matrix("lid", s * RP_LID_U)

    def latch(s):
        sc.gmat[AT.g("latch_lever")] = M.joint_matrix("latch", s * LATCH_U)

    def bolt(s0, s1):
        def up(e):
            sc.gmat[AT.g("latch_bolt")] = M.joint_matrix("bolt", s0 + (s1 - s0) * e)
        return up

    def latch_grasp(s):
        out, up_, tilt = LATCH_AT
        a = math.radians(tilt)
        Mx = P.tcp_frame(np.array([gl["x"], gl["yface"] - out, gl["zf"] + up_ * gl["length"]]),
                         (0.0, math.cos(a), -math.sin(a)), 0.0)
        return T(RP) @ M.joint_matrix("latch", s * LATCH_U) @ Mx

    kc = M.knob_centre()

    def knob_grasp(s):
        Mx = P.tcp_frame(kc + np.array([0.0, -KNOB_OUT, 0.0]), (0.0, 1.0, 0.0), 0.0)
        return T(RP) @ M.joint_matrix("lid", s * RP_LID_U) @ Mx

    def arc(pose, s0, s1, n):
        return AT.follow(rb, [pose(s0 + (s1 - s0) * x) for x in np.linspace(0.0, 1.0, n)])

    def jaws(f0, f1):
        def up(e):
            AT.tong_jaws(sc, f0 + (f1 - f0) * e)
        return up

    def hold_cup():
        """The tong has shut on the cup: the arm holds the cup now, the tong riding on it (alloy_atomize's
        bookkeeping, for the audit: a held part may touch where it came from and where it goes)."""
        tw, cw = sc.world("tong"), sc.world(cg)
        rb.events.append((sc.n, "release", "tong", None))
        sc.parent.pop(cg, None)
        sc.gmat[cg] = cw
        rb.held = (cg, AT.inv(rb.tcp_world()) @ cw)
        rb.events.append((sc.n, "grasp", cg, "amr"))
        sc.parent["tong"] = cg
        sc.gmat["tong"] = AT.inv(cw) @ tw

    def hold_tong():
        tw, cw = sc.world("tong"), sc.world(cg)
        sc.parent.pop("tong", None)
        sc.gmat["tong"] = tw
        if sc.parent.get(cg) is None:
            sc.parent[cg] = "tong"
            sc.gmat[cg] = AT.inv(tw) @ cw
        rb.events.append((sc.n, "release", cg, None))
        rb.held = ("tong", AT.inv(rb.tcp_world()) @ tw)
        rb.events.append((sc.n, "grasp", "tong", None))

    def cup_down():
        """The jaws open: the cup stays, standing on the floor cone at its place."""
        sc.parent[cg] = AT.g("crucible")
        sc.gmat[cg] = AT.inv(sc.world(AT.g("crucible"))) @ T(RP) @ AT.cup_pose(CUP_AT, AT.CUP_R,
                                                                                AT.cup_seat(CUP_AT)[2], 0.0)
        rb.events.append((sc.n, "release", cg, AT.g("crucible")))
        for chk in [rb._checker] + list(getattr(sc.auditor, "checkers", {}).values()):
            if chk is not None:
                chk.held_group = None

    st = {}

    def to_arc(key, grasp, pose, move, close, skip, back, opening):
        def fac():
            q = AT.arc_branch(rb, sc, grasp, pose, move, close, skip, n=17, back=back)
            st[key] = q
            return both(rb.joint_to(q1=rb.solve(grasp @ T((0, 0, -back)), q)), rb.grip_to(opening))
        return fac

    def at_rp():
        yield from call(lambda: (phase("At the atomizer, the arm pulls the lid's draw latch open and lifts the lid by "
                                       "its knob."), labels(lbl_arm, lbl_latch, lbl_lid)))
        yield 0.8, lambda: bolt(0.0, 1.0)                       # the pneumatic locking bolt goes back
        yield ARM_S[0], to_arc("latch", latch_grasp(0.0), latch_grasp, latch, GRIP_LATCH, ("latch",), 100.0,
                               OPEN_LATCH)
        yield HOLD, None
        yield ARM_S[1], lambda: rb.line_to(latch_grasp(0.0))
        yield ARM_S[2], lambda: rb.grip_to(GRIP_LATCH)
        rb.events.append((sc.n, "grasp", AT.g("latch_lever"), None))
        yield 1.4, lambda: both(arc(latch_grasp, 0.0, 1.0, 9), latch)
        yield ARM_S[2], lambda: rb.grip_to(OPEN_LATCH)
        rb.events.append((sc.n, "release", AT.g("latch_lever"), None))
        yield ARM_S[3], lambda: rb.line_to(latch_grasp(1.0) @ T((0, 0, -100)))
        yield ARM_S[0], to_arc("knob", knob_grasp(0.0), knob_grasp, lid, GRIP_KNOB, ("knob",), 110.0, 0.45)
        yield HOLD, None
        yield ARM_S[1], lambda: rb.line_to(knob_grasp(0.0))
        yield ARM_S[2], lambda: rb.grip_to(GRIP_KNOB)
        rb.events.append((sc.n, "grasp", AT.g("knob"), None))
        yield 2.2, lambda: both(arc(knob_grasp, 0.0, 1.0, 12), lid)
        yield ARM_S[2], lambda: rb.grip_to(0.45)
        rb.events.append((sc.n, "release", AT.g("knob"), None))
        yield ARM_S[3], lambda: rb.line_to(knob_grasp(1.0) @ T((0, 0, -110)))
        # the loading tong out of its holder on the MiR's cabinet (alloy_atomize: chapter 2's moves)
        yield from call(lambda: (phase("With a loading tong, the arm takes the cup and sets it on the crucible's "
                                       "floor, past the sealing rod."), labels(lbl_arm, lbl_tong_at())))
        home = AT.tong_tcp(sc.world("tong"))
        yield 1.6, lambda: both(rb.joint_to(Tw=T((0, 0, 130)) @ home), rb.grip_to(0.0))
        yield 0.8, lambda: rb.line_to(home)
        yield 0.4, lambda: rb.grip_to(AT.GRIP_TONG)
        rb.grasp("tong")
        yield 0.9, lambda: rb.line_to(T((0, 0, 210)) @ rb.tcp_world())
        xm = sc.world(L.amr_group)[:3, 0]
        top = (sc.world(cg) @ np.r_[0.0, 0.0, C.SLUG_L, 1.0])[:3]
        F = np.eye(4)
        F[:3, 0], F[:3, 1], F[:3, 2], F[:3, 3] = xm, np.cross((0, 0, 1.0), xm), (0, 0, 1), top
        g_pick = AT.tong_tcp(F)
        yield 1.4, lambda: both(rb.joint_to(Tw=T((0, 0, 90)) @ g_pick), rb.grip_to(AT.GRIP_TONG_OPEN), jaws(0.0, 1.0))
        yield 0.7, lambda: rb.line_to(g_pick)
        yield 0.4, lambda: both(rb.grip_to(AT.GRIP_TONG), jaws(1.0, 0.0))
        hold_cup()
        yield 0.6, lambda: rb.line_to(T((0, 0, 150)) @ rb.tcp_world())
        path = AT.tong_path(CUP_AT)
        grips = [AT.tong_tcp(T(RP) @ AT.tong_frame_for(CUP_AT, Mx)) for Mx in path]
        stage = grips[0].copy()
        stage[0, 3], stage[1, 3] = RP[0] + 60.0, RP[1] - 200.0
        yield 1.3, lambda: both(rb.joint_to(Tw=stage), cam_up(sc, "bore"))
        yield 0.6, lambda: rb.line_to(grips[0])
        # down the bore in three legs, the arm's "held" part swapping between the cup and the tong (alloy_atomize)
        yield 1.2, lambda: AT.follow(rb, grips[:4])
        hold_tong()
        yield 0.8, lambda: AT.follow(rb, grips[3:5])
        hold_cup()
        yield 1.4, lambda: AT.follow(rb, grips[4:])
        hold_tong()
        yield 0.4, lambda: both(rb.grip_to(AT.GRIP_TONG_OPEN), jaws(0.0, 1.0))
        cup_down()
        yield 0.8, lambda: rb.line_to(T((0, 0, 170)) @ rb.tcp_world())
        home2 = AT.tong_tcp(sc.world("amr") @ L.tong_home)
        yield 1.6, lambda: both(rb.joint_to(Tw=T((0, 0, 220)) @ home2), rb.grip_to(AT.GRIP_TONG), jaws(1.0, 0.0),
                                cam_up(sc, "rp"))
        yield 0.9, lambda: rb.line_to(home2)
        yield 0.4, lambda: rb.grip_to(0.0)
        rb.release("amr")
        yield 0.6, lambda: rb.line_to(T((0, 0, 120)) @ rb.tcp_world())
        # the lid down and the latch shut, the bolt in
        yield from call(lambda: (phase("The arm shuts the lid and the latch, and the locking bolt goes in."),
                                 labels(lbl_arm, lbl_latch, lbl_lid)))
        yield 1.4, to_arc("knob_open", knob_grasp(1.0), lambda s: knob_grasp(1.0 - s), lambda s: lid(1.0 - s),
                          GRIP_KNOB, ("knob",), 110.0, 0.45)
        yield 0.7, lambda: rb.line_to(knob_grasp(1.0))
        yield 0.4, lambda: rb.grip_to(GRIP_KNOB)
        rb.events.append((sc.n, "grasp", AT.g("knob"), None))
        yield 2.0, lambda: both(arc(knob_grasp, 1.0, 0.0, 12), lambda e: lid(1.0 - e))
        yield 0.4, lambda: rb.grip_to(0.45)
        rb.events.append((sc.n, "release", AT.g("knob"), None))
        yield 0.7, lambda: rb.line_to(knob_grasp(0.0) @ T((0, 0, -110)))
        yield 1.4, to_arc("latch_open", latch_grasp(1.0), lambda s: latch_grasp(1.0 - s), lambda s: latch(1.0 - s),
                          GRIP_LATCH, ("latch",), 100.0, OPEN_LATCH)
        yield 0.7, lambda: rb.line_to(latch_grasp(1.0))
        yield 0.4, lambda: rb.grip_to(GRIP_LATCH)
        rb.events.append((sc.n, "grasp", AT.g("latch_lever"), None))
        yield 1.4, lambda: both(arc(latch_grasp, 1.0, 0.0, 9), lambda e: latch(1.0 - e))
        yield 0.4, lambda: rb.grip_to(OPEN_LATCH)
        rb.events.append((sc.n, "release", AT.g("latch_lever"), None))
        yield 0.7, lambda: rb.line_to(latch_grasp(0.0) @ T((0, 0, -100)))
        yield 0.6, lambda: both(bolt(1.0, 0.0), rb.joint_to(A.PARK_RAD))
        yield from park(rb, 0.8)

    def lbl_tong_at():
        return ("loading tong", tuple(sc.world("tong")[:3, 3] + (0.0, 0.0, 200.0)), (0.985, 0.30))
    run(sc, at_rp())

    # ------------------------------------------------------------------ 5. melted and atomized; back to the opening
    def melt():
        yield from call(lambda: (phase("The atomizer melts the cup and sprays the melt into powder (a time-lapse, "
                                       "cut open)."), fx.start(sc), labels(lbl_melt, lbl_plate, lbl_pw)))
        yield 1.6, lambda: cam_up(sc, "cut")
        yield ATOM_SECS - 1.6 - 4.6, None
        yield from call(lambda: (phase("And the robot goes back to the VLM for the next tray."), labels(*at_start)))
        yield from cam_to(sc, "wide", 4.6)
        yield 1.2, None

    def back():
        yield 1.0, None
        yield from drive(L, dock[:2], arm_at)
    run(sc, melt(), back())
    out = sc.save()
    if sc.auditor is not None and not SC.AUDIT:      # ARM_AUDIT_RENDER=1
        sc.auditor.save()
    if apart and SC.AUDIT and sc.auditor is not None:
        os.makedirs("/tmp/org_audit", exist_ok=True)
        with open(f"/tmp/org_audit/{apart[0]:05d}.json", "w") as fh:
            json.dump(dict(frames=sc.auditor.frames, parent=sc.parent,
                           events={r.prefix: [list(e) for e in r.events] for r in sc.robots}), fh)
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm; {sc.n} frames; the melt ran frames {fx.n0}-{fx.n1}",
          flush=True)
    if fx.n1 is None:
        print("warning: the melt had not ended by the last frame, so the loop jumps", file=sys.stderr)
    meta_path = OUT / f"{NAME}.json"
    if meta_path.exists() and not os.environ.get("ARM_AUDIT") and not os.environ.get("PREVIEW"):
        meta = json.loads(meta_path.read_text())
        meta.update(title=TITLE, speed=SPEED, camera=CAM, phases=phases)
        meta_path.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    return out


def join(*names):
    """Parts rendered side by side (ORG_PART, each under its own ORG_NAME) -> out/mp4/<NAME>.mp4 and out/<NAME>.json."""
    from scene import OUT
    names = names or sorted(p.stem for p in (OUT / "mp4").glob(f"{NAME}_p*.mp4"))
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
        for nm in names:
            fh.write(f"file '{(OUT / 'mp4' / f'{nm}.mp4').resolve()}'\n")
        lst = fh.name
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags",
                    "+faststart", str(OUT / "mp4" / f"{NAME}.mp4")], check=True)
    meta = json.loads((OUT / f"{names[0]}.json").read_text())
    meta["name"] = NAME
    (OUT / f"{NAME}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    print(f"joined {len(names)} parts -> {NAME}.mp4", flush=True)


def audit_join():
    """The audited parts (ORG_AUDIT_PART, /tmp/org_audit/) -> one report, out/collisions/<NAME>.json, by
    collide.Auditor's own rules over every frame."""
    import glob
    from types import SimpleNamespace

    import collide
    frames, parent, events = [], {}, {}
    for pth in sorted(glob.glob("/tmp/org_audit/*.json")):
        d = json.load(open(pth))
        frames += d["frames"]
        parent, events = d["parent"], d["events"]
    frames.sort(key=lambda fr: fr["n"])
    aud = collide.Auditor.__new__(collide.Auditor)
    aud.sc = SimpleNamespace(name=NAME, parent=parent,
                             robots=[SimpleNamespace(prefix=p, events=ev) for p, ev in events.items()])
    aud.frames, aud.checkers, aud.snap_frames = frames, {}, set()
    rep = aud.save()
    print(f"{rep['frames_with_collisions']} of {rep['frames_checked']} frames with collisions", flush=True)


BAND = 86            # px at 1280 wide: the white header band over the render that holds the GIF's text


def header(img, caption: str):
    """The frame under a white band: the org page's title, the step's caption and the speed badge."""
    from PIL import Image, ImageDraw

    import scene as SC
    w = img.width
    k = w / 1280
    H = int(round(BAND * k))
    out = Image.new("RGB", (w, img.height + H), "white")
    out.paste(img, (0, H))
    d = ImageDraw.Draw(out)
    d.text((18 * k, 9 * k), TITLE, font=SC.font(29 * k, bold=True), fill=(20, 20, 24))
    d.text((18 * k, 50 * k), caption, font=SC.font(21 * k), fill=(55, 58, 66))
    fb = SC.font(20 * k, bold=True)
    badge = f"{SPEED:g}× speed"
    x1 = w - 18 * k
    x0 = x1 - d.textlength(badge, font=fb) - 26 * k
    d.rounded_rectangle((x0, 12 * k, x1, 46 * k), 6 * k, fill=(30, 60, 140))
    d.text((x0 + 13 * k, 17 * k), badge, font=fb, fill=(255, 255, 255))
    d.line([(0, H - 1), (w, H - 1)], fill=(30, 60, 140), width=max(1, int(round(2 * k))))
    return out


def gif(width=GIF_W, lossy=0, colors=128, sticky=int(os.environ.get("ORG_STICKY", "6"))):
    """out/mp4/<NAME>.mp4 -> out/<NAME>.gif, every frame at SPEED x the MP4's rate, each under the header band; and the
    same frames as out/mp4/<NAME>_readme.mp4 (SPEED x, h264), for anyone who would rather embed a video. One palette
    for the whole clip (the camera holds still), no dithering, gifsicle -O3 and no --lossy: lossy re-encoding drifts
    where things moved, and the loop then flickers where the last frame meets the first. On a first cut of round 1's
    clip, --lossy=40 gave 3.3 MB with 38,771 px of the last frame off the first; lossless, 4.3 MB and 5,819 px, nearly
    all by a shade (the MP4's own noise). Round 2's loop is 702 frames: 192 colours gave 8.7 MB, 128 give 7.7 MB with
    no banding to see at the README's size.
    Round 3's is 962 frames of closer views: 47.5 MB as it was. The MP4's noise flickers pixels in the parts that hold
    still, so each frame stored more than what moved. `sticky` keeps a pixel from the frame before wherever no channel
    has changed by more than that many levels (of 255), so those parts are the same bytes from frame to frame: 40.0 MB
    at 6. Most of what is left is the two pans, which change every pixel for about 115 frames. Motion isn't held back:
    something moving across a pixel changes it by far more than 6 levels."""
    from PIL import Image

    from scene import OUT
    mp4, out = OUT / "mp4" / f"{NAME}.mp4", OUT / f"{NAME}.gif"
    meta = json.loads((OUT / f"{NAME}.json").read_text())
    phases = meta["phases"]
    fps = meta["fps"] * SPEED
    sw, sh = meta["size"]
    w, h = width, int(round(sh * width / sw / 2)) * 2
    def frames():
        dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", str(mp4), "-vf",
                                f"scale={w}:{h}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                               stdout=subprocess.PIPE)
        while True:
            buf = dec.stdout.read(w * h * 3)
            if len(buf) < w * h * 3:
                break
            yield np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        dec.wait()

    def held(a, prev):
        if prev is None or sticky <= 0:
            return a
        keep = (np.abs(a.astype(np.int16) - prev.astype(np.int16)).max(axis=2) <= sticky)[..., None]
        return np.where(keep, prev, a)
    prev = None
    if sticky > 0:     # a first pass to where the held pixels end up, so the first frame starts from there: held
        for a in frames():         # from a fresh first frame instead, the loop's seam differed in 8,375 px by over 16
            prev = held(a, prev)   # levels, against 2,837 with nothing held
    with tempfile.TemporaryDirectory() as tmp:
        n = 0
        for a in frames():
            prev = held(a, prev)
            cap = [p["text"] for p in phases if p["start_frame"] <= n][-1]
            header(Image.fromarray(prev), cap).save(f"{tmp}/{n:05d}.png", compress_level=1)
            n += 1
        seq_ = ["-framerate", f"{fps:g}", "-i", f"{tmp}/%05d.png"]
        pal = f"{tmp}/pal.png"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *seq_, "-vf",
                        f"palettegen=max_colors={colors}:stats_mode=full", pal], check=True)
        raw = f"{tmp}/raw.gif"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *seq_, "-i", pal, "-lavfi",
                        "[0:v][1:v]paletteuse=dither=none:diff_mode=rectangle", "-loop", "0", raw], check=True)
        subprocess.run(["gifsicle", "-O3", f"--lossy={lossy}", "-o", str(out), raw], check=True)
        vid = OUT / "mp4" / f"{NAME}_readme.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *seq_, "-c:v", "libx264", "-crf", "20", "-preset", "slow",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(vid)], check=True)
        Image.open(f"{tmp}/00000.png").save(OUT / f"{NAME}_still.png", optimize=True)   # its first frame
    msg = (f"{out.name}: {out.stat().st_size / 1e6:.2f} MB, {w} x {h + int(round(BAND * w / 1280))}, {n} frames at "
           f"{fps:g} fps ({n / fps:.1f} s); {vid.name}: {vid.stat().st_size / 1e6:.2f} MB")
    print(msg, flush=True)
    return msg


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "movie"
    {"views": views, "movie": movie, "gif": gif, "join": join, "audit_join": audit_join}[arg](*sys.argv[2:])
