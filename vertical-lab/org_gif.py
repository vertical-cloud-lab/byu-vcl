"""The org page's GIF, remade in the lab as this branch has it: ``vertical-cloud-lab/.github``'s
``profile/vertical-lab.gif`` ("In a vertical lab, equipment is brought to the operator", PR #318).

Round 2 (PR #329, Sterling, 2026-11-06: "that gif is way over-simplified. At the very least, it should show interaction
with multiple trays and an interaction with at least one module sitting outside the VLM. Remove the warehouse stuff,
remove the 2nd VLM."). One Shuttle, loaded as the set-up loads it (``animate.lab_scene``, Shuttle 1's trays A-F and J);
no pallet racking, no second Shuttle and none of its trays. One loop of the lab in steady state, which ends where it
starts:

1. at the sieving cell, on its bench beside the Shuttle (a module outside the VLM), the MiR250 + UR10e takes the run's
   sample, a vial of the sieved powder, out of a pocket on the bench and stands it in a pocket on its own base;
   meanwhile the VLM brings tray A, the CubXL laid out for DAL's corrosion screen, to its opening;
2. the MiR drives along the dock line to the opening;
3. at tray A, the arm swaps the vials: the last sample, its test done, comes out of the CubXL's free seat into the
   MiR's second pocket, and the new one goes in;
4. tray A goes back to its slot (R2), where its dock keeps it powered and the CubXL runs the new test, DAL's powder
   reactivity test (``instruments_lab.powder_test``: ten 20 uL transfers of seawater onto the powder); the VLM brings
   tray B, powder dosing, down;
5. at tray B, the arm takes an empty 20 mL vial out of the rack and stands the tested one in its seat;
6. tray B goes back up while the MiR drives back to the cell, and the arm leaves the empty vial in the cell's pocket
   for the next sample.

Round 3 (PR #329, Sterling, 2026-11-06: "the GIF can be larger ... more like 50 MB, so you don't have to restrict
yourself so much in terms of time. Also, you should probably zoom in to see what the robot's doing, while still in view
of the CubXL in the background that's still doing things"). The same loop, closer and slower:
- the camera stands about 3-4 m from the arm instead of 8 m, and follows the MiR: one framing at the cell ("cell"),
  with the VLM's bay at its right, and one at the opening ("open"), panned between them as the MiR drives, at the
  MiR's own pace (drive's `cams`). From the opening, tray A's CubXL stays in view after it goes back to R2: over and
  between tray B's instruments, and through the empty bay once tray B has gone back up;
- the CubXL's test runs for TEST_SECS of the clip (TestClock) instead of 5 s, from tray A's return to its slot through
  tray B's visit and the drive back, so it is still running behind the arm; it ends before the loop does;
- the arm's moves take the 9:09 clip's times again (ARM_S), and the GIF plays at 1.5x instead of 2.5x.

The last frame is the first one again: the MiR at the cell with its arm parked, a vial in the cell's pocket, trays A and
B in their slots, a tested vial in the CubXL, the extractor at tray B's slot. What differs is too small to see: the vial
in the cell's pocket is empty at the end and holds the 25 mg sample at the start, and the rack's vial on tray B holds
the tested sample at the end. The GIF plays everything at SPEED x the modelled times and says so; the CubXL's test,
minutes long, is compressed much further, and its label says that.

Drawn differently for this shot only (all drawing choices):
- Shuttle 2 is left out: its frame, extractor and cladding (setup_lab.TwoLab's u2_* groups), its bay camera, its trays
  G-M with their instruments, UPSs and cameras, its dock tape and its camera target. Its trays' instruments aren't
  loaded at all (VLAB_ONLY_TRAYS, and no fab_tour.load), which also makes the scene much lighter.
- So is the pallet racking round the room's edge (warehouse.racking), and the second MiR unit on its charger.
- The camera stands where the south row is, so that row's floor machines and its overhead utilities are left out, as
  in round 1 (SOUTH_OUT, Y_CUT).
- A MiR250 can't turn on a dock line 80 mm off the fronts, and the VLM's camera target stands on that line at the
  opening's left (setup_lab.TARGET_AT, for a unit that backs in from the right). Coming from the cell, a unit drives in
  from the left, so the target stands at the opening's right instead (TARGET_DX), its mirror image.
- The MiR stops at the cell on the VLM's dock line (W.DOCK_N), CELL_X, so it drives to the opening along the line,
  straight; the set-up's own spot for the cell is 300 mm further out, for the arm's level reach to the sieves' tabs.
- The cell's vial pocket (CELL_SEAT) and the MiR's second pocket (M2_LOCAL) are props.buffer_holder blocks, as the
  MiR's own pocket is.
- The bay's back shutter is drawn at 12 % opacity instead of the usual 35 %, so tray A's slot shows through the empty
  bay while its test starts there.

    VIZ3D_FPS=12 xvfb-run -a python3 org_gif.py views    # the candidate views, as stills -> /tmp/org_gif_views.png
    PREVIEW=1 VIZ3D_FPS=12 xvfb-run -a python3 org_gif.py   # the last frame of each step -> /tmp/preview_<NAME>.png
    ARM_AUDIT=1 VIZ3D_FPS=12 xvfb-run -a python3 org_gif.py # no render: every frame's arm checked -> out/collisions/
    VIZ3D_FPS=12 xvfb-run -a python3 org_gif.py          # -> out/mp4/<NAME>.mp4, out/<NAME>.json
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


# the views: camera position, focal point, up (mm; Shuttle 1's centre at the origin, its opening facing -y), view angle.
# Round 3's two: "cell", the MiR at the cell with the bay at the frame's right (tray A at the opening, or its slot R2
# through the empty bay), about 3.6 m across at the arm; "open", the MiR at the opening, about 3 m across, tray A's
# slot over and between tray B's instruments. Rounds 1 and 2 used "f2" and "c4", 8-9 m across.
CAMS = {
    "cell": _cam((-1150.0, -1500.0, 1080.0), 0.0, 18.0, 4000.0, 27.0),
    "open": _cam((-120.0, -1460.0, 1010.0), 11.0, 19.0, 3300.0, 27.0),
    "c4": [(1300, -8600, 3400), (-650, -900, 1750), (0, 0, 1), 34.0],
    "c1": [(1300, -8600, 3200), (-650, -900, 1500), (0, 0, 1), 34.0],       # the VLM's roof cut off
    "c2": [(600, -8200, 2900), (-700, -900, 1450), (0, 0, 1), 36.0],
    "c3": [(2000, -8400, 3500), (-500, -800, 1500), (0, 0, 1), 34.0],
    "f2": [(2200, -8000, 3000), (100, -700, 1700), (0, 0, 1), 33.0],       # round 1's: Shuttle 1 alone
}
CAM = "cell"
# leader-label boxes, as fractions of the frame (the overlay draws a line from each to its point in the lab)
# (a box left of the middle has its left edge at fx, one right of it its right edge; fy is its middle)
LBL = {"arm": (0.03, 0.93), "cell": (0.02, 0.08), "vlm": (0.985, 0.07), "A": (0.985, 0.09), "run": (0.985, 0.09),
       "B": (0.985, 0.70)}
# The camera stands behind the south row (its fronts at y = -6238), so the row's overhead utilities (its cable tray at
# 3.2 m with its network cable, hangers, drops and junction boxes, the DED's argon run, the fume hood's duct;
# setup_lab.utilities) and its floor machines (SOUTH_OUT) would stand between it and Shuttle 1. For this shot they are
# left out: every utility cell south of Y_CUT, and every FLOOR_PLAN station in row "S". The north row's stay.
Y_CUT = -4000.0
SHUTTER_GHOST = 0.12
SOUTH_OUT = bool(int(os.environ.get("ORG_SOUTH_OUT", "1")))
# the cycle's places
CELL_X = -1750.0                 # the MiR's centre at the sieving cell, on the VLM's dock line: its arm's base in
                                 # front of the bench's free right end, so the arm reaches in through the cell's open
                                 # front (from further right, its forearm went through the enclosure's side panel and
                                 # the Shuttle's corner); 50 mm short of the cell's camera target's floor plate
CELL_SEAT = (-1560.0, -1442.0)   # the cell's vial pocket: on its bench, 120 mm in from the front, 200 mm right of the
                                 # shaker's body and 110 mm left of the enclosure's side panel; right of the parked arm,
                                 # so the camera sees it
M2_LOCAL = (300.0, -150.0)       # the MiR's second pocket (cabinet frame): BUFFER_LOCAL's mirror image across the arm
TARGET_DX = 2 * 1330.0           # the VLM's camera target, from x = -1330 (setup_lab.TARGET_AT) to +1330
GRASP_Z = 50.0                   # the gripper takes a vial 50 mm up (animate.workflow)
ARM_S = (1.6, 0.9, 0.5, 0.8)     # a pick or a place: joint move, line in, grip, line out (s): the 9:09 clip's
                                 # (animate.pick/place); round 2 ran them at 1.2/0.7/0.4/0.6
HOLD = 0.1
MIR_V = 1500.0                   # mm/s at most, with the MiR250's 0.3 m/s^2 ramps (props.ramp_secs)
TEST_SECS = 34.0                 # the CubXL's test, minutes long, in this many seconds of the clip (a time-lapse): from
                                 # tray A's return to R2 to the arm at the cell again, before its last park


def _load_s1() -> dict:
    """setup_lab.load_all without fab_tour's models: they are trays G-I's, all on Shuttle 2."""
    import setup_lab as SL
    idata = SL.tour_load_safe()
    idata.update(SL.load_r7())
    idata.update(SL.r7_stand_ins(idata))
    return idata


class Vial:
    """A 20 mL vial (props.vial_glass) with its powder, a heap on its floor at its angle of repose, to scale
    (animate.workflow), and the liquid over it. Group `g`, under `parent` at `at`."""

    REPOSE = math.radians(34.0)

    def __init__(self, sc, g, parent, at, mg=0.0, ul=0.0):
        import pyvista as pv

        import props as P
        from scene import T
        self.sc, self.g = sc, g
        sc.add(f"{g}/glass", P.vial_glass(), P.GLASS, g, opacity=0.55, specular=0.7)
        heap = pv.Cone(center=(0, 0, 0.5), direction=(0, 0, -1), height=1.0, radius=1.0, resolution=40).triangulate()
        sc.add(f"{g}/heap", heap, P.POWDER, f"{g}_heap")
        sc.add(f"{g}/liquid", P.fill(1.0), P.LIQUID, f"{g}_liq", opacity=0.85)
        sc.parent[f"{g}_heap"] = g
        sc.parent[f"{g}_liq"] = g
        sc.parent[g] = parent
        sc.gmat[g] = T(at)
        self.set(mg, ul)

    def set(self, mg=None, ul=None):
        import props as P
        from scene import S, T
        sc, g = self.sc, self.g
        if mg is not None:
            r = (3 * (max(mg, 1e-3) / 1.4) / (math.pi * math.tan(self.REPOSE))) ** (1 / 3)
            sc.gmat[f"{g}_heap"] = T((0, 0, P.VIAL_FLOOR)) @ S((r, r, r * math.tan(self.REPOSE)))
            sc.alpha[f"{g}/heap"] = 1.0 if mg > 0.05 else 0.0
        if ul is not None:
            h = ul / (math.pi * (P.VIAL_R - P.VIAL_WALL) ** 2)
            sc.gmat[f"{g}_liq"] = T((0, 0, P.VIAL_FLOOR)) @ S((1, 1, max(h, 0.01)))
            sc.alpha[f"{g}/liquid"] = 1.0 if h > 0.05 else 0.0


def build(data):
    """Shuttle 1 in the lab (animate.lab_scene), stripped (strip, floor_edits, clear_view), with the corrosion CubXL
    that moves (cubxl_rig) on tray A and the cycle's start: the MiR at the cell, its arm parked, the sample in the
    cell's pocket, a tested vial in the CubXL, an empty one in tray B's rack, trays A and B in their slots and the
    extractor at B's. -> (scene, lab, cub, test, vials)."""
    import animate as A
    import cubxl_rig
    import instruments_lab as IL
    import props as P
    import setup_lab as SL
    import vlm as V
    import warehouse as W
    from scene import T
    os.environ.setdefault("VLAB_ONLY_TRAYS", S1_TRAYS)
    SL.load_all = _load_s1
    sc, L = A.lab_scene(data, name=NAME, title=TITLE)
    sc.text_scale = TEXT
    L.show_gauges = False
    L.extra_gauges = []
    strip(sc, L)
    floor_edits(sc)
    clear_view(sc, L)
    cub = cubxl_rig.CubRig(L)
    for key, g, names, _ in L.items.get("A", []):      # as animate.workflow: CubRig draws the set-up's CubXL, moving
        if key == "cubxl_corrosion":
            for nm in names:
                sc.alpha[nm] = 0.0
                sc.base_alpha[nm] = 0.0
    test = IL.powder_test()
    cub.pose(cubxl_rig.state_at(test, 1.0))             # the last sample's test, done
    q = IL.POWDER_TEST
    # the unit at the cell, on the dock line; the MiR's second pocket
    u = L.units[0]
    u.set((CELL_X, W.DOCK_N, 0.0))
    holder, seat = P.buffer_holder()
    sc.add(f"{u.name}/holder2", holder.translate((*M2_LOCAL, P.AMR_TOP - 20), inplace=False), P.RACK_C, L.amr_group)
    L.m2_seat = (M2_LOCAL[0], M2_LOCAL[1], P.AMR_TOP - 20 + seat[2])
    # the cell's pocket, on its bench
    bench_h = SL.SIEVE_BENCH["h"]
    sc.add("cell pocket", holder.translate((*CELL_SEAT, bench_h), inplace=False), P.RACK_C, "cell_pocket")
    L.cell_seat = (CELL_SEAT[0], CELL_SEAT[1], bench_h + seat[2])
    # the vials: the set-up's own ("vial", in tray B's rack) is the empty one; the tested one in the CubXL's free seat;
    # the sample, 25 mg of the sieved cut (DAL's test takes 10-50 mg of each run's powder), in the cell's pocket
    L.powder_h = L.liquid_h = 0.0
    L.set_fill()
    seat_cub = (IL._cx(q["seat"][0]), IL._cy(q["seat"][1]), IL._cz(0.0))
    vials = {"tested": Vial(sc, "vial_t", cub.body, seat_cub, mg=q["mg"], ul=q["ul"]),
             "sample": Vial(sc, "vial_s", "cell_pocket", L.cell_seat, mg=q["mg"], ul=0.0)}
    # trays A and B in their slots, the extractor at B's (where the cycle leaves it), the shutter shut
    L.use(1)
    for k in ("A", "B"):
        L.tray[k] = [*V.SLOTS[A.HOME[k]]]
        L.where[k] = A.HOME[k]
    L.lift_z = V.SLOTS[A.HOME["B"]][1]
    L.shutter = 0.0
    for nm in list(L.ghost):
        if sc.group_of.get(nm, "").endswith("shutter"):
            L.ghost[nm] = SHUTTER_GHOST
    L.skin(1.0)(1.0)
    L.apply_state()
    return sc, L, cub, test, vials


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
    """Stills of the candidate views (ORG_VIEWS=a,b,... picks some): the cycle's start, and tray A at the opening with
    the MiR docked there."""
    from PIL import Image, ImageDraw

    import lab
    import vlm as V
    import warehouse as W
    sc, L, cub, test, vials = build(lab.meshes())
    keys = [k for k in CAMS if not os.environ.get("ORG_VIEWS") or k in os.environ["ORG_VIEWS"].split(",")]
    shots = []
    for state in ("start", "docked"):
        if state == "docked":
            L.tray["A"] = [*V.SLOTS["open"]]
            L.where["A"] = "open"
            L.lift_z = V.SLOTS["open"][1]
            L.units[0].set(W.dock_pose("vlm"))
            L.apply_state()
        for key in keys:
            set_cam(sc, key)
            shots.append((f"{key} / {state}", Image.fromarray(sc.render_base())))
    tw, th = 640, 360
    sheet = Image.new("RGB", (tw * len(keys), th * 2), "white")
    d = ImageDraw.Draw(sheet)
    for i, (lbl, im) in enumerate(shots):
        x, y = (i % len(keys)) * tw, (i // len(keys)) * th
        sheet.paste(im.resize((tw, th)), (x, y))
        d.text((x + 6, y + 4), lbl, fill=(200, 0, 0))
        im.save(f"/tmp/org_gif_{lbl.replace(' / ', '_').replace(' ', '_')}.png")
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
        sc.step("", "", dd, upd, hold=0.0)
        clock += dd
    for dur, fac in main:
        step(dur, fac() if fac is not None else None)
    while any(not b.done for b in bg):
        d = min(b.end() for b in bg if not b.done) - clock
        if d < 0.5 / FPS:
            for b in bg:
                b.advance(clock)
            continue
        step(d, None)


def seq(*gens):
    for g in gens:
        yield from g


def wait(seconds):
    yield seconds, None


def call(f):
    """A track step that only runs f (a caption, labels, a lamp) between the segments around it."""
    f()
    return
    yield


def pick(rb, M_grasp, M_pre, group, grip):
    """animate.pick as a track: joint move to M_pre opening the gripper, line to M_grasp, close, take `group`, line back."""
    import animate as A
    s = ARM_S
    yield s[0], lambda: A.both(rb.joint_to(Tw=M_pre), rb.grip_to(0.0))
    yield HOLD, None
    yield s[1], lambda: rb.line_to(M_grasp)
    yield HOLD, None
    yield s[2], lambda: rb.grip_to(grip)
    rb.grasp(group)
    yield HOLD, None
    yield s[3], lambda: rb.line_to(M_pre)
    yield HOLD, None


def place(rb, M_place, M_pre, new_parent):
    """animate.place as a track."""
    s = ARM_S
    yield s[0], lambda: rb.joint_to(Tw=M_pre)
    yield HOLD, None
    yield s[1], lambda: rb.line_to(M_place)
    yield HOLD, None
    yield s[2], lambda: rb.grip_to(0.0)
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


def drive(L, x1, follow, cams=None):
    """The docked unit along its own x to x1, from rest to rest at the MiR250's 0.3 m/s^2 (props.ramp_frac);
    `follow` is a label's anchor (a list), moved with it. With `cams` (k0, k1), the camera goes from view k0 to view k1
    at the MiR's own pace: the share of the way it has driven is the share of the way between the two views."""
    import props as P
    u, rb, sc = L.units[0], L.robot, L.sc
    x0, y0, hd = u.pose
    at, ps, s = P.s_curve(x0, y0, x1, y0)
    d0 = [follow[0] - x0, follow[1] - y0]

    def fac():
        def up(e):
            f = P.ramp_frac(P.unease(e), s[-1], MIR_V)
            x, y, h = at(float(np.interp(f * s[-1], s, ps)))
            u.set((x, y, h))
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


class TestClock:
    """The CubXL's test as a frame hook (Scene.frame_hooks): from start() on it runs with the frames, TEST_SECS for the
    whole test, whatever the tracks are doing, so it carries on behind the arm across steps; then it stays done."""

    def __init__(self, cub, test, on_state):
        self.cub, self.test, self.on_state = cub, test, on_state
        self.va, self.vb = test.v("start"), test.v("end")
        self.n0 = None
        self.n1 = None             # the frame it ends on, for the log

    def start(self, sc):
        self.n0 = sc.n

    def __call__(self, sc):
        import cubxl_rig
        from scene import FPS
        if self.n0 is None:
            return
        u = min(1.0, max(0.0, (sc.n - self.n0) / (TEST_SECS * FPS)))
        if u >= 1.0 and self.n1 is not None:
            return
        if u >= 1.0:
            self.n1 = sc.n
        s = cubxl_rig.state_at(self.test, self.va + (self.vb - self.va) * u)
        self.cub.pose(s)
        self.on_state(s)


def movie():
    """The cycle, rendered real-time. The scene draws only the leader labels: the title, the step captions and the
    speed badge go in the GIF's header band (gif()), from the phases written into out/<NAME>.json."""
    import animate as A
    import cubxl_rig
    import instruments_lab as IL
    import lab
    import props as P
    import vlm as V
    import warehouse as W
    import scene as SC
    from scene import OUT
    sc, L, cub, test, vials = build(lab.meshes())
    sc.title = ""
    if os.environ.get("ARM_AUDIT_RENDER") and not (SC.PREVIEW or SC.AUDIT):
        import collide                      # ARM_AUDIT=1's audit in the render's own pass: one pass for both
        sc.auditor = collide.Auditor(sc)
        sc.frame_hooks.append(sc.auditor)   # after the TestClock (inserted at 0 below), so it sees the CubXL posed
    live = os.environ.get("ORG_LIVE")       # a directory: every 60th frame as a JPEG while it renders, to check it
    if live and not (SC.PREVIEW or SC.AUDIT):
        import time
        os.makedirs(live, exist_ok=True)
        snap, t_start = sc.snap, time.time()

        def snap_live(n=1):
            hi = snap(n)
            if hi is not None and sc.n // 60 != (sc.n - n) // 60:
                hi.convert("RGB").save(f"{live}/{sc.n:05d}.jpg", quality=85)
                print(f"frame {sc.n}, {time.time() - t_start:.0f} s", flush=True)
            return hi
        sc.snap = snap_live
    rb, cab = L.robot, L.amr_group
    q = IL.POWDER_TEST
    set_cam(sc, os.environ.get("ORG_CAM", CAM))
    cams = ("cell", "open") if os.environ.get("ORG_CAM", CAM) == "cell" else None   # a still camera if ORG_CAM is set
    sc.intro = 0.6
    rack = L.eq_groups["B"][0]
    rack_xy = A.LOADS["B"][0][1:]
    phases = []

    def phase(text):
        phases.append(dict(start_frame=sc.n, text=text))

    def on_cab(seat):
        """A pocket on the MiR's cabinet, in the world, where the MiR is now, at the grasp height."""
        return (sc.world(cab) @ np.r_[np.asarray(seat, float) + (0, 0, GRASP_Z), 1.0])[:3]

    def cub_seat():
        return cub.deck_world(*q["seat"], 0.0) + (0, 0, GRASP_Z)

    def rack_seat():
        return A.tray_world("B", np.array(L.rack_seats[A.RACK_SEAT]) + (*rack_xy, V.T_FLOOR) + (0, 0, GRASP_Z))

    p_cell = np.array(L.cell_seat) + (0, 0, GRASP_Z)
    # the labels: the MiR's anchor moves with it (drive's `follow`: a list, read when each frame is drawn)
    arm_at = [CELL_X, W.DOCK_N - 300.0, 650.0]
    lbl_arm = ("the operator: a MiR250 + UR10e", arm_at, LBL["arm"])
    b = __import__("setup_lab").SIEVE_BENCH
    lbl_cell = ("outside the VLM: the sieving cell", (b["x"] - 250.0, -1562.0, b["h"] + b["encl_h"] - 250.0),
                LBL["cell"])
    # the VLM's label points at its opening's header, by the logo: the roof is out of these close views. Only the cell's
    # view shows it; the header is above the opening's view, so the drive over labels tray A instead (lbl_A, whose
    # anchor stays in frame all the way). At the header's middle, its first anchor was under its own box
    lbl_vlm = ("Kardex Shuttle XP 500:\nevery tray docked to power", (-900.0, -1590.0, V.Z_OPEN_TOP + 45.0),
               LBL["vlm"])
    at_cell = [lbl_arm, lbl_cell, lbl_vlm]

    def lbl_at(k, text, xyz_tray, box):
        return (text, tuple((sc.world(f"tray_{k}") @ np.r_[np.asarray(xyz_tray, float), 1.0])[:3]), box)
    lbl_A = []                            # set as the MiR leaves the cell, with tray A at the opening

    def on_state(s):
        vials["sample"].set(ul=s["vial"])
    clock = TestClock(cub, test, on_state)
    sc.frame_hooks.insert(0, clock)

    def labels(*ls):
        sc.sticky_labels = list(ls)

    # ------------------------------------------------------------------ 1. the sample, at the cell; tray A comes down
    def cell_pick():
        yield from call(lambda: (phase("The operator, here a mobile robot arm, takes a sample from an instrument "
                                       "outside the VLM."), labels(*at_cell)))
        yield from pick(rb, A.down(p_cell), A.down(p_cell + (0, 0, 120)), "vial_s", A.GRIP_VIAL)
        yield from place(rb, A.down(on_cab(L.buffer_seat)), A.down(on_cab(L.buffer_seat) + (0, 0, 120)), cab)
        yield from park(rb)
        yield from call(leave_cell)
        yield from drive(L, 0.0, arm_at, cams)

    def leave_cell():
        if L.where["A"] != "open":
            print("warning: tray A wasn't at the opening yet when its label was placed", file=sys.stderr)
        lbl_A.append(lbl_at("A", "tray A at the opening:\nthe CubXL, a corrosion test", (31.0, -49.0, 455.0),
                            LBL["A"]))
        phase("It drives over. The VLM has already brought the tray it needs to the opening.")
        labels(lbl_arm, lbl_A[0])
    run(sc, cell_pick(), fetch(L, "A"))
    # ------------------------------------------------------------------ 2. tray A: the vials swapped

    def at_A():
        yield from call(lambda: (phase("Tray A: the new sample goes in, and the one whose test is done comes out."),
                                 labels(lbl_arm, lbl_A[0])))
        yield from pick(rb, A.down(cub_seat(), spin=0.0), A.down(cub_seat() + (0, 0, 130), spin=0.0), "vial_t",
                        A.GRIP_VIAL)
        yield from place(rb, A.down(on_cab(L.m2_seat), spin=0.0), A.down(on_cab(L.m2_seat) + (0, 0, 120), spin=0.0),
                         cab)
        yield from pick(rb, A.down(on_cab(L.buffer_seat)), A.down(on_cab(L.buffer_seat) + (0, 0, 120)), "vial_s",
                        A.GRIP_VIAL)
        yield from place(rb, A.down(cub_seat(), spin=0.0), A.down(cub_seat() + (0, 0, 130), spin=0.0), cub.body)
        yield from park(rb)
    run(sc, at_A())
    # ------------------------------------------------------------------ 3. tray A back, its test running; tray B down
    phase("Tray A goes back into storage, still powered, and runs the test there. Tray B comes down.")
    labels(lbl_arm)
    run(sc, store(L, "A"))
    lbl_run = ("tray A in its slot: the test\nruns there (time-lapse)", tuple(cub.deck_world(200.0, 150.0, 200.0)),
               LBL["run"])
    labels(lbl_arm, lbl_run)
    vials["sample"].set(ul=0.0)
    clock.start(sc)                       # the test runs from here, behind everything else, for TEST_SECS
    run(sc, fetch(L, "B"))
    # ------------------------------------------------------------------ 4. tray B: the tested vial in, an empty one out
    lbl_B = lbl_at("B", "tray B at the opening:\npowder dosing, its vial rack",
                   np.array(L.rack_seats[A.RACK_SEAT]) + (*rack_xy, V.T_FLOOR + 90.0), LBL["B"])

    def at_B():
        yield from call(lambda: (phase("Tray B: the tested sample goes into storage, and an empty vial comes out, "
                                       "while tray A's test runs behind it."), labels(lbl_arm, lbl_B, lbl_run)))
        yield from pick(rb, A.down(rack_seat()), A.down(rack_seat() + (0, 0, 110)), "vial", A.GRIP_VIAL)
        yield from place(rb, A.down(on_cab(L.buffer_seat)), A.down(on_cab(L.buffer_seat) + (0, 0, 120)), cab)
        yield from pick(rb, A.down(on_cab(L.m2_seat), spin=0.0), A.down(on_cab(L.m2_seat) + (0, 0, 120), spin=0.0),
                        "vial_t", A.GRIP_VIAL)
        yield from place(rb, A.down(rack_seat()), A.down(rack_seat() + (0, 0, 110)), rack)
        yield from park(rb)
    run(sc, at_B())
    # ------------------------------------------------------------------ 5. back to the cell; tray B back up

    def back():
        yield from call(lambda: (phase("The arm takes the empty vial back to the instrument for its next sample."),
                                 labels(lbl_arm, lbl_run)))
        yield from drive(L, CELL_X, arm_at, cams[::-1] if cams else None)
        yield from call(lambda: labels(lbl_arm, lbl_cell, lbl_run))
        yield from pick(rb, A.down(on_cab(L.buffer_seat)), A.down(on_cab(L.buffer_seat) + (0, 0, 120)), "vial",
                        A.GRIP_VIAL)
        yield from place(rb, A.down(p_cell), A.down(p_cell + (0, 0, 120)), "cell_pocket")
        yield from call(lambda: (labels(*at_cell), print(f"test: frames {clock.n0}-{clock.n1}, last park from "
                                                         f"{sc.n}", flush=True)))
        yield from park(rb)
        yield 0.4, None
    run(sc, back(), store(L, "B"))
    out = sc.save()
    if sc.auditor is not None and not SC.AUDIT:      # ARM_AUDIT_RENDER=1
        sc.auditor.save()
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm; {sc.n} frames; the test ran frames {clock.n0}-"
          f"{clock.n1}", flush=True)
    if clock.n1 is None:
        print("warning: the CubXL's test had not ended by the last frame, so the loop jumps", file=sys.stderr)
    meta_path = OUT / f"{NAME}.json"
    if meta_path.exists() and not os.environ.get("ARM_AUDIT") and not os.environ.get("PREVIEW"):
        meta = json.loads(meta_path.read_text())
        meta.update(title=TITLE, speed=SPEED, camera=os.environ.get("ORG_CAM", CAM), phases=phases)
        meta_path.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    return out


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


def gif(width=GIF_W, lossy=0, colors=128):
    """out/mp4/<NAME>.mp4 -> out/<NAME>.gif, every frame at SPEED x the MP4's rate, each under the header band; and the
    same frames as out/mp4/<NAME>_readme.mp4 (SPEED x, h264), for anyone who would rather embed a video. One palette
    for the whole clip (the camera holds still), no dithering, gifsicle -O3 and no --lossy: lossy re-encoding drifts
    where things moved, and the loop then flickers where the last frame meets the first. On a first cut of round 1's
    clip, --lossy=40 gave 3.3 MB with 38,771 px of the last frame off the first; lossless, 4.3 MB and 5,819 px, nearly
    all by a shade (the MP4's own noise). Round 2's loop is 702 frames: 192 colours gave 8.7 MB, 128 give 7.7 MB with
    no banding to see at the README's size."""
    from PIL import Image

    from scene import OUT
    mp4, out = OUT / "mp4" / f"{NAME}.mp4", OUT / f"{NAME}.gif"
    meta = json.loads((OUT / f"{NAME}.json").read_text())
    phases = meta["phases"]
    fps = meta["fps"] * SPEED
    sw, sh = meta["size"]
    w, h = width, int(round(sh * width / sw / 2)) * 2
    with tempfile.TemporaryDirectory() as tmp:
        dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", str(mp4), "-vf",
                                f"scale={w}:{h}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                               stdout=subprocess.PIPE)
        n = 0
        while True:
            buf = dec.stdout.read(w * h * 3)
            if len(buf) < w * h * 3:
                break
            cap = [p["text"] for p in phases if p["start_frame"] <= n][-1]
            header(Image.frombytes("RGB", (w, h), buf), cap).save(f"{tmp}/{n:05d}.png", compress_level=1)
            n += 1
        dec.wait()
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
    {"views": views, "movie": movie, "gif": gif}[arg]()
