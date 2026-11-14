"""Maintenance in the workflow (#303, PR #318, round 10): a clip of about 90 s.

    VIZ3D_FPS=6 xvfb-run -a python3 upkeep_clip.py            # -> out/mp4/upkeep_clip.mp4, out/upkeep_clip.gif, .json
    PREVIEW=1 xvfb-run -a python3 upkeep_clip.py               # the last frame of each sub-step -> /tmp/preview_*.png
    ARM_AUDIT=1 xvfb-run -a python3 upkeep_clip.py             # every frame collision-checked -> out/collisions/

(``VLAB_ONLY_TRAYS=BE`` is the default here: setup_lab populates only trays B and E, the two this clip presents; the
cladding is opaque, so the others, empty, aren't seen.)

Sterling on PR #318 (2026-11-07): "Something that's been on my mind is maintenance over long-term and how that gets
handled in workflows." Three parts, in the whole lab as the set-up movie leaves it, each task as ``upkeep.py`` (the
upkeep-model stream's) books it:

1. **The week's schedule, maintenance included** (``out/upkeep_week.png``; a placeholder is drawn until it exists):
   maintenance booked like any job, by who does it.
2. **A check the arm runs between jobs** (upkeep.py ``bal_weights``: daily, the arm, 0.15 h). The A&D HR-202i under
   the multi-doser's dose point: a 100 g OIML class E2 weight, kept in tray J's store and carried on the MiR's deck,
   is set on the doser's pedestal by our vessel shuttle (``carousel.py``, as round 9's 8:37 clip sets the vial), read,
   and taken back. The reading goes on a control chart against the lab's limits; out of them, the doser is flagged
   (no doses booked on it) and a person's task is booked.
3. **A person's task, with Kardex's full tray extraction** (upkeep.py ``nano_tip``: every 600 runs, a person, the tray
   pulled out, 2 h). Tray E comes to Shuttle 1's opening; the MiR250 + UR10e drives off to Shuttle 2, which carries
   on working. A person rolls an extraction table to the opening, the tray comes out onto it ("With the full tray
   extraction device, a tray is placed in front of the access opening": Kardex Shuttle XP brochure,
   notes/maintenance.md), the iMicro's hood lifts and the person changes its Berkovich tip. The tray goes back in, the
   table goes away, the MiR docks again and runs the fused-silica check on the new tip (upkeep.py ``nano_fs``).
   upkeep.py books the PX500's and the furnace's jobs at the opening (both stand at the tray's front); the tray comes
   out for what is out of reach there.

Kardex publishes no size for its extraction device or its cart: the table here is assumed (``TABLE``). What is
assumed is in ``notes/upkeep_clip.md``.

Round 11 (Sterling: "That's kind of a cringy looking human ... Also, maintenance step shows a collision. There are
probably other collisions and interferences that I didn't catch from this"):

* **The person** is ``people.Person``: MakeHuman's CC0 base mesh skinned to its default skeleton, posed each frame
  (walk, lean, both arms solved to their targets, head turned, fingers curled) and dressed by region. Round 10's
  capsule figure was drawn here.
* **What the arm audit can't see** is checked too (``PeopleCheck``, with ``ARM_AUDIT=1``): every part of the person
  as posed, the extraction table, and tray E with everything on it while it is off its dock, against everything
  visible near them; -> ``out/collisions/upkeep_clip_movers.json``. ``UPKEEP_FROM=3`` starts at part 3.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw

import scene
from scene import CLEAN, OUT, PREVIEW, Scene, T, R, font  # noqa: E402

import animate as A                   # noqa: E402
import lab                            # noqa: E402
import props as P                     # noqa: E402
import robot as RB                    # noqa: E402
import vlm as V                       # noqa: E402

NAME = "upkeep_clip"
TITLE = "Vertical cloud lab: maintenance in the workflow"
HERE = Path(__file__).resolve().parent
STOP = os.environ.get("UPKEEP_STOP", "")      # "1" or "2": end after that part (for a quick look while writing it)
FROM = os.environ.get("UPKEEP_FROM", "")      # "3": start at part 3 (the person's task), for a quick look

# ------------------------------------------------------------------------------------------------ the check weight
# OIML R 111-1's cylindrical form with a knob, sized from the mass at 8.0 g/cm3 (stainless steel): estimates, not a
# maker's drawing. 100 g sits in the HR-202i's 220 g x 0.1 mg range, and its 24 mm foot rides our shuttle's fork, whose
# tines straddle a 13 mm slot (a 20 g weight, 14 mm across, would fall through it).
WEIGHT = dict(g=100.0, d=24.0, body_h=25.0, neck_d=10.0, neck_h=3.0, knob_d=14.0, knob_h=9.5)
WEIGHT_H = WEIGHT["body_h"] + WEIGHT["neck_h"] + WEIGHT["knob_h"]          # 37.5 mm
GRIP_UP = 31.0                        # the grasp point over the weight's foot: the pads (+-19 mm) hold the body's top
#                                       13 mm and end 12 mm over the fork's top
STAND = dict(w=64.0, h=12.0, pocket=3.0)      # ours: a low block on the MiR's cabinet top with a shallow seat
STAND_AT = (-300.0, 55.0)                     # cabinet frame: beside the vial holder (animate.BUFFER_LOCAL)
CAB_TOP = P.MIR["H"] + P.CAB_H                # 780 mm
E2_MPE_MG = 0.16                              # OIML R 111-1, Table 1: class E2, 100 g
LIMIT_MG = 0.3                                # the lab's action limit (assumed): HR-202i linearity +-0.2 mg + E2 MPE
WARN_MG = 0.2                                 # warning limit (assumed)
TODAY_MG, WHATIF_MG = 0.1, 0.4               # today's reading (illustrative), and the what-if

# ------------------------------------------------------------------------------------------------ the extraction
FACE = -V.UNIT_D / 2 - V.SKIN                 # -1562: the cladding's front face
LIP = FACE - 50.0                             # -1612: the front of the blue cover under the opening (vlm.opening)
EXTRACT = V.TRAY_D + ((V.Y_FRONT - V.TRAY_D / 2) - FACE)       # 964 mm: the tray's back edge out to the face
# the extraction table (assumed: Kardex publishes no size): a frame on four castors that docks against the cover's
# lip, its two roller rails at the tray's running height, as long as the tray is deep and a little narrower than it
# (its left legs stay clear of the AprilTag post's foot plate, setup_lab.TARGET_AT)
TABLE = dict(d=900.0, half_w=1180.0, rail_x=1150.0, rail_w=60.0, leg_x=1110.0, z_top=V.Z_OPEN, castor=110.0)
TABLE_GAP = 4.0                               # docked 4 mm off the cover: the LED-Navigator strip stands 2 mm proud of it
TABLE_Y = LIP - TABLE_GAP - TABLE["d"] / 2    # its centre, docked
TABLE_FRONT = LIP - TABLE_GAP - TABLE["d"]    # -2516
MIR_SPEED = 1500.0                            # mm/s at most, at 0.3 m/s^2 (props.ramp_secs), as the other chapters
WALK = 900.0                                  # the person's pace, mm/s (a slow walk, pushing a table)

CAM_LAB = [(9400, -11800, 6400), (1800, -1600, 1300), (0, 0, 1)]
CAM_OPEN = [(3600, -6200, 3000), (0, -1300, 1250), (0, 0, 1)]
CAM_EXTRACT = [(3000, -5200, 2600), (-200, -2100, 900), (0, 0, 1)]      # in the aisle, north of the south row
PANEL_W = 0.46                                # the control chart's width, as a share of the frame

# the palette (dataviz skill's reference instance): one series, its limits, status colours with a word beside them
INK, INK2, MUTED, GRID, AXIS, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e1e0d9", "#c3c2b7", "#fcfcfb"
SERIES, GOOD, CRITICAL, WARNING = "#2a78d6", "#0ca30c", "#d03b3b", "#fab219"


# ================================================================================================= the scene
class UpScene(Scene):
    """setup_lab.build's Scene, with full-frame and side panels and an instrument clock drawn over every frame."""

    def setup_overlays(self):
        self.panels = {}              # key -> [PIL image, alpha, where ("full" or "right")]
        self.clock = None
        self._pc = {}

    def overlay(self, img, scale, anchors):
        img = super().overlay(img, scale, anchors)
        if CLEAN:
            return img
        for key, (im, a, where) in list(self.panels.items()):
            if a > 0.02:
                self._draw_panel(img, key, im, a, where)
        if self.clock:
            self._draw_clock(img)
        return img

    def _draw_panel(self, img, key, im, a, where):
        W, H = img.size
        if where == "full":
            bw, bh = int(0.96 * W), int(0.76 * H)
        else:
            bw, bh = int(PANEL_W * W), int(0.62 * H)
        k = min(bw / im.width, bh / im.height)
        size = (max(1, int(im.width * k)), max(1, int(im.height * k)))
        ck = (key, size)
        if ck not in self._pc:
            self._pc[ck] = im.resize(size, Image.LANCZOS).convert("RGBA")
        pnl = self._pc[ck].copy()
        pnl.putalpha(int(255 * min(1.0, a) * 0.97))
        if where == "full":
            x, y = (W - pnl.width) // 2, int(0.075 * H)
        else:
            x, y = W - pnl.width - int(0.012 * W), int(0.075 * H)
        img.paste(pnl, (x, y), pnl)

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
    # set here, not at import: timelapse.py imports this module for its Person and must keep every tray and its GIF
    os.environ.setdefault("VLAB_ONLY_TRAYS", "BE")
    scene.GIF_FPS = 3                 # a 1.5-minute GIF well under 4.9 MB (the MP4 keeps every frame)
    scene.GIF_SIZE = (512, 288)
    import setup_lab as SL
    import warehouse as W
    data = lab.meshes()
    idata = SL.load_all()
    sc, L, F, items, rigs, units, util, ulabel, vp = SL.build(data, idata, name=NAME, title=TITLE)
    sc.__class__ = UpScene
    sc.setup_overlays()
    sc.gif = not (PREVIEW or scene.AUDIT)
    SL.add_bay_cams(sc)
    u = units[0]
    u.set(W.dock_pose("vlm"))
    L.robot = u.robot
    L.skin(0.0)(1.0)                   # opaque: with VLAB_ONLY_TRAYS=BF the other trays stand empty in the Shuttles
    L.show_gauges = True
    L.extra_gauges = []
    L.apply_state()
    return sc, L, rigs, u


def fast_collisions(sc, L, u, trays=("B", "E"), reach=2800.0):
    """As alloy_characterize.fast_collisions: the arm's collision world is what it can reach from its dock at Shuttle
    1 (trays B and F, and whatever stands within `reach`); only this unit's arm is audited."""
    import collide as CL
    keep, drop = set(), set()
    for k in L.tray:
        (keep if k in trays else drop).update(CL._subtree(sc, f"tray_{k}"))
    y0 = u.pose[1] + A.ARM_LOCAL[1]
    bases = np.array([[u.pose[0] + A.ARM_LOCAL[0], y0]])
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
            if len(full) != len(known):
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


class PeopleCheck:
    """Round 11 (Sterling: "maintenance step shows a collision. There are probably other collisions and interferences
    that I didn't catch"): what collide.Auditor can't see, checked every audited frame (ARM_AUDIT=1).

    * the person, as posed (every part of the skinned body), against everything visible near them;
    * the extraction table, whenever it is shown;
    * tray E and everything on it while it is off its dock (sliding out, on the table, sliding back).

    The movers check (collide.Movers) sees a group's world matrix change; a body that bends in place (a lean, a reach)
    doesn't change it, so the person needs this one. FCL on the drawn meshes; a contact counts if collide.depth puts
    it deeper than 1.5 mm. Allowed, by rule: the shoes on the floor (to 12 mm: the skinned soles roll), the table's
    castors on the floor, the tray on the table's rollers and in the carrier it left (to 3 mm), and what `allow` names
    for the moment (the gloves on the bar they push, on the tip they hold). Writes out/collisions/upkeep_clip_movers.json."""

    DEPTH = 1.5

    def __init__(self, sc, person, table_group="xtable", tray="E", L=None,
                 region=((-2900.0, 2900.0), (-6400.0, -700.0), (-60.0, 2800.0))):
        import collide as CL
        self.CL, self.sc, self.p, self.L, self.tray = CL, sc, person, L, tray
        self.table = table_group
        self.tray_groups = CL._subtree(sc, f"tray_{tray}")
        self.allow: set[tuple[str, str]] = set()          # (person part or "*", other group) allowed now
        self.frames: list[dict] = []
        self.y_dock = None
        (x0, x1), (y0, y1), (z0, z1) = region
        mine = set(person.groups) | {table_group} | self.tray_groups
        only, known = {}, set()

        def near(name, actor):
            g = sc.group_of.get(name)
            if g in mine:
                return True
            if g in person.groups:
                return False
            inp = actor.GetMapper().GetInput()
            if inp is None or inp.GetNumberOfPoints() == 0:
                return False
            b = np.array(inp.GetBounds()).reshape(3, 2)
            c = np.array([[b[0, i], b[1, j], b[2, k]] for i in (0, 1) for j in (0, 1) for k in (0, 1)])
            w = (sc.world(g) @ np.c_[c, np.ones(8)].T).T[:, :3]
            lo, hi = w.min(axis=0), w.max(axis=0)
            return hi[0] > x0 and lo[0] < x1 and hi[1] > y0 and lo[1] < y1 and hi[2] > z0 and lo[2] < z1

        person_names = set(person.names())

        class W(CL.World):
            def refresh(self):
                full = self.sc.actors
                for name in set(full) - known:
                    known.add(name)
                    if name not in person_names and near(name, full[name]):
                        only[name] = full[name]
                self.sc.actors = only
                try:
                    CL.World.refresh(self)
                finally:
                    self.sc.actors = full
        self.world = W(sc)
        self.depth = getattr(CL, "depth", None)
        print(f"people check: {len(only)} actors", flush=True)

    def _d(self, a, b) -> float:
        if self.depth is not None:
            return self.depth(a, b, upto=12.0)
        return 99.0 if self.CL._hit(a.obj, b.obj) else 0.0

    @staticmethod
    def _is_floor(name: str) -> bool:
        n = name.lower()
        return "floor" in n or "ground" in n

    def __call__(self, sc):
        CL, p = self.CL, self.p
        hits = []
        self.world.refresh()
        held = {g for g, _ in p.held.values()}
        snap = self.world.current(set(p.groups) | held)
        if not snap.items:
            self.frames.append(dict(n=sc.n, label=sc.label, hits=hits))
            return
        groups = [b.group for b in snap.bodies]
        shown = any(sc.alpha.get(n, 0.0) > 0.02 for n in p.names())
        # 1. the person
        if shown:
            for part, (P, F) in p.posed().items():
                lo, hi = P.min(0) - 1.0, P.max(0) + 1.0
                cand = np.nonzero(~((snap.lo > hi) | (snap.hi < lo)).any(1))[0]
                if not len(cand):
                    continue
                body = CL.Body(f"{p.n}/{part}", p.group, P, np.asarray(F, np.int32))
                body.place(np.eye(4))
                for i in cand:
                    b, g = snap.bodies[i], groups[i]
                    if (part, g) in self.allow or ("*", g) in self.allow or g in held:
                        continue
                    b.ensure()
                    b.place(snap.M[i])
                    if not CL._hit(body.obj, b.obj):
                        continue
                    d = self._d(body, b)
                    tol = 12.0 if (part == "shoes" and self._is_floor(b.name)) else self.DEPTH
                    if d > tol:
                        hits.append(dict(a=f"{p.n}/{part}", b=b.name, group=g, depth=d))
        # 2. the table and 3. tray E off its dock: rigid, against what isn't them
        movers = []
        if any(sc.alpha.get(n, 0.0) > 0.02 for n in sc.members(self.table)):
            movers.append(("table", {self.table}))
        if self.L is not None:
            y = self.L.tray[self.tray][0]
            if self.y_dock is None:
                self.y_dock = y
            if self.L.where.get(self.tray) is None:
                movers.append(("tray", self.tray_groups))
        for kind, gs in movers:
            mine = [(b, M) for b, M in zip(snap.bodies, snap.M) if b.group in gs]
            for a, Ma in mine:
                a.ensure()
                a.place(Ma)
                lo, hi = a.box(Ma)
                cand = np.nonzero(~((snap.lo > hi + 1.0) | (snap.hi < lo - 1.0)).any(1))[0]
                for i in cand:
                    b, g = snap.bodies[i], groups[i]
                    if g in gs or (kind == "tray" and g == self.table) or (kind == "table" and g in self.tray_groups):
                        if not (kind == "tray" and g == self.table):
                            continue
                    if ("*", g) in self.allow or (kind, g) in self.allow:
                        continue
                    b.ensure()
                    b.place(snap.M[i])
                    if not CL._hit(a.obj, b.obj):
                        continue
                    d = self._d(a, b)
                    floor = self._is_floor(b.name)
                    tol = 12.0 if (kind == "table" and floor) else (3.0 if (kind == "tray" and g == self.table) else
                                                                    self.DEPTH)
                    if d > tol:
                        hits.append(dict(a=a.name, b=b.name, group=g, depth=d))
        self.frames.append(dict(n=sc.n, label=sc.label, hits=hits))

    def report(self) -> dict:
        bad = [f for f in self.frames if f["hits"]]
        pairs = {}
        for f in bad:
            for h in f["hits"]:
                k = (h["a"], h["b"])
                r = pairs.setdefault(k, dict(a=h["a"], b=h["b"], frames=0, first=f["n"], last=f["n"], depth=0.0,
                                             label=f["label"]))
                r["frames"] += 1
                r["last"] = f["n"]
                r["depth"] = max(r["depth"], h["depth"])
        return dict(frames_checked=len(self.frames), frames_in_collision=len(bad),
                    pairs=sorted(pairs.values(), key=lambda r: r["first"]))

    def save(self, name):
        out = HERE / "out" / "collisions" / f"{name}_movers.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        rep = self.report()
        out.write_text(json.dumps(rep, indent=1) + "\n")
        print(f"people/table/tray check: {rep['frames_in_collision']} of {rep['frames_checked']} frames in "
              f"collision -> {out}", flush=True)
        for r in rep["pairs"][:40]:
            print(f"  {r['a']} x {r['b']}: frames {r['first']}-{r['last']} ({r['frames']}), depth {r['depth']}, "
                  f"{r['label']}", flush=True)
        return rep


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


# ================================================================================================= meshes
def revolve(profile, res=40) -> pv.PolyData:
    """A closed surface of revolution about z from a profile [(r, z)] that starts and ends on the axis."""
    pts = np.array([[r, 0.0, z] for r, z in profile], float)
    line = pv.PolyData(pts, lines=np.r_[len(pts), np.arange(len(pts))])
    m = line.extrude_rotate(resolution=res, capping=False).triangulate().clean()
    return m.compute_normals(auto_orient_normals=True, split_vertices=False)


def weight_mesh() -> pv.PolyData:
    """The 100 g weight, its foot's centre at the origin (OIML R 111-1's knob form, sizes estimated)."""
    w = WEIGHT
    r, b, n_r, n_h, k_r, k_h = w["d"] / 2, w["body_h"], w["neck_d"] / 2, w["neck_h"], w["knob_d"] / 2, w["knob_h"]
    prof = [(0.0, b + n_h + k_h), (k_r - 3.0, b + n_h + k_h), (k_r - 0.6, b + n_h + k_h - 0.8), (k_r, b + n_h + k_h - 3.0),
            (k_r, b + n_h + 2.0), (k_r - 2.0, b + n_h), (n_r, b + n_h), (n_r, b + 0.2), (r - 1.5, b), (r - 0.2, b - 0.6),
            (r, b - 2.0), (r, 1.2), (r - 1.0, 0.0), (0.0, 0.0)]
    return revolve(prof[::1], 48)


def stand_mesh() -> pv.PolyData:
    """Ours: the weight's seat on the MiR's cabinet top, a 64 mm block 12 mm tall with a 25 mm pocket 3 mm deep."""
    s = STAND
    return P.pocket_block(-s["w"] / 2, s["w"] / 2, -s["w"] / 2, s["w"] / 2, [(0.0, 0.0, WEIGHT["d"] / 2 + 0.5)],
                          h=s["h"], floor=s["h"] - s["pocket"], lead=1.0)


def table_parts() -> dict:
    """The extraction table (assumed), its frame: x across the opening, y towards the VLM, z up, the origin on the
    floor under its centre. {name: (mesh, rgb, specular)}"""
    t = TABLE
    d2, hw, rx, rw, lx, zt = t["d"] / 2, t["half_w"], t["rail_x"], t["rail_w"], t["leg_x"], t["z_top"]
    box = lambda *b: pv.Box(bounds=b).triangulate()               # noqa: E731
    frame = None
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (rx - rw / 2), sx * (rx + rw / 2)))
        rail = box(x0, x1, -d2, d2, zt - 70, zt - 30)               # the rail carrier
        frame = rail if frame is None else frame.merge(rail)
    for y in (-d2 + 25, d2 - 25):                                    # cross beams under the rails
        frame = frame.merge(box(-hw, hw, y - 25, y + 25, zt - 110, zt - 70))
    frame = frame.merge(box(-hw, hw, -25, 25, zt - 110, zt - 70))
    frame = frame.merge(box(-hw, hw, -d2, -d2 + 30, zt - 60, zt - 30))   # the push bar along the front edge
    legs = None
    for sx in (-1, 1):
        for y in (-d2 + 35, d2 - 35):
            leg = box(sx * lx - 25, sx * lx + 25, y - 25, y + 25, t["castor"], zt - 70)
            legs = leg if legs is None else legs.merge(leg)
    rollers = None
    for sx in (-1, 1):
        for y in np.arange(-d2 + 40, d2 - 30, 80.0):
            rl = pv.Cylinder(center=(sx * rx, y, zt - 13), direction=(1, 0, 0), radius=13.0, height=rw - 6,
                             resolution=16).triangulate()
            rollers = rl if rollers is None else rollers.merge(rl)
    stops = None                                                     # a stop at the front end of each rail
    for sx in (-1, 1):
        st = box(sx * rx - 22, sx * rx + 22, -d2 + 4, -d2 + 30, zt - 30, zt + 22)
        stops = st if stops is None else stops.merge(st)
    castors = None
    for sx in (-1, 1):
        for y in (-d2 + 35, d2 - 35):
            fk = box(sx * lx - 22, sx * lx + 22, y - 30, y + 30, 70, t["castor"])
            wh = pv.Cylinder(center=(sx * lx, y, 50), direction=(1, 0, 0), radius=48, height=32,      # 2 mm over the
                             resolution=24).triangulate()                       # floor: its tape is 1.5 mm thick
            c = fk.merge(wh)
            castors = c if castors is None else castors.merge(c)
    latch = None                                                     # two hooks resting on the cover's lip
    for sx in (-1, 1):                                               # (round 10's sat inside it: under its top)
        lt = box(sx * 900 - 40, sx * 900 + 40, d2 - 5, d2 + 35, V.Z_SILL + 0.5, V.Z_SILL + 12.0)
        lt = lt.merge(box(sx * 900 - 40, sx * 900 + 40, d2 - 22, d2 - 5, zt - 40, V.Z_SILL + 12.0))
        latch = lt if latch is None else latch.merge(lt)
    out = {"frame": (frame.merge(stops), V.RAL7035, 0.2), "legs": (legs, (0.55, 0.57, 0.60), 0.3),
           "rollers": (rollers, (0.72, 0.73, 0.75), 0.6), "castors": (castors, (0.12, 0.12, 0.13), 0.2),
           "latch": (latch, (0.30, 0.32, 0.35), 0.3)}
    for m, _, _ in out.values():
        m.clear_data()
    return out


# ================================================================================================= the person
from people import Person              # noqa: E402  (round 11: MakeHuman's CC0 body, skinned; was drawn here)

STRIDE = Person.STRIDE                 # mm per gait cycle


# ================================================================================================= the panels
def _fig_to_image(fig) -> Image.Image:
    import io
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=fig.dpi, facecolor=fig.get_facecolor())
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def chart_data():
    """30 working days of the daily check (illustrative): reading less the weight's certified mass, in mg, read to the
    HR-202i's 0.1 mg."""
    rng = np.random.default_rng(303)
    past = np.round(rng.normal(0.02, 0.07, 29) / 0.1) * 0.1
    return [float(v) for v in past] + [TODAY_MG]


def control_chart(whatif: bool) -> Image.Image:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    vals = chart_data()
    n = len(vals)
    fig, ax = plt.subplots(figsize=(6.2, 4.0), dpi=110)
    fig.patch.set_facecolor(SURF)
    ax.set_facecolor(SURF)
    x = np.arange(1, n + 1)
    ax.axhspan(-LIMIT_MG, LIMIT_MG, color="#eaf4ea", zorder=0)
    for lim, col, ls, lw in ((LIMIT_MG, CRITICAL, (0, (5, 3)), 1.4), (WARN_MG, INK2, (0, (2, 3)), 1.0)):
        for sg in (-1, 1):
            ax.axhline(sg * lim, color=col, lw=lw, ls=ls, zorder=1)
    ax.axhline(0.0, color=AXIS, lw=1.0, zorder=1)
    ax.plot(x, vals, color=SERIES, lw=2.0, zorder=3)
    ax.scatter(x[:-1], vals[:-1], s=34, color=SERIES, edgecolor=SURF, linewidth=1.5, zorder=4)
    ax.scatter([n], [vals[-1]], s=120, color=GOOD, edgecolor=SURF, linewidth=2.0, zorder=5)
    ax.annotate(f"today {vals[-1]:+.1f} mg\n✓ within limits: online", (n, vals[-1]), xytext=(n - 12.0, -0.47),
                fontsize=9.5, color=INK, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    if whatif:
        ax.scatter([n + 1], [WHATIF_MG], s=120, color=CRITICAL, edgecolor=SURF, linewidth=2.0, zorder=5)
        ax.annotate(f"what if {WHATIF_MG:+.1f} mg\n✗ out: repeat once, then\nflag the doser, book a person",
                    (n + 1, WHATIF_MG), xytext=(n - 17.0, 0.375), fontsize=9.5, color=INK,
                    arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    ax.text(0.6, LIMIT_MG + 0.015, f"action limit ±{LIMIT_MG:.1f} mg (ours, assumed)", fontsize=8.5,
            color=INK2, va="bottom")
    ax.text(0.6, -WARN_MG - 0.015, f"warning ±{WARN_MG:.1f} mg", fontsize=8.5, color=INK2, va="top")
    ax.set_xlim(0, n + 2.5)
    ax.set_ylim(-0.62, 0.62)
    ax.set_xlabel("daily check, working days", fontsize=9.5, color=INK2)
    ax.set_ylabel("reading − certified mass, mg", fontsize=9.5, color=INK2)
    ax.tick_params(colors=INK2, labelsize=8.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(AXIS)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    fig.suptitle("A&D HR-202i daily check: 100 g OIML E2 weight", x=0.02, ha="left", fontsize=11.5, color=INK,
                 fontweight="bold")
    fig.text(0.02, 0.905, f"E2 tolerance ±{E2_MPE_MG:.2f} mg (OIML R 111-1); readability 0.1 mg. "
             "Readings illustrative.", fontsize=8.5, color=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.89))
    im = _fig_to_image(fig)
    plt.close(fig)
    return im


def week_panel() -> tuple[Image.Image, bool]:
    """upkeep.py's week (out/upkeep_week.png, the upkeep-model stream's), or a placeholder until it exists."""
    path = OUT / "upkeep_week.png"
    if path.exists():
        return Image.open(path).convert("RGB"), True
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(12.0, 6.0), dpi=100)
    fig.patch.set_facecolor(SURF)
    ax.set_facecolor(SURF)
    rows = ["experiments", "the arm's checks", "people's tasks"]
    cols = [SERIES, "#1baf7a", "#eb6834"]
    for i, (row, c) in enumerate(zip(rows, cols)):
        for d in range(7):
            if i == 0:
                ax.barh(i, 18, left=d * 24 + 3, height=0.5, color=c)
            elif i == 1:
                ax.barh(i, 0.6, left=d * 24 + 6, height=0.5, color=c)
            elif d in (1, 3):
                ax.barh(i, 2, left=d * 24 + 9, height=0.5, color=c)
    ax.set_yticks(range(3), rows)
    ax.set_xticks([d * 24 + 12 for d in range(7)], ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    ax.invert_yaxis()
    ax.text(84, 1.0, "PLACEHOLDER: upkeep.py's week goes here", ha="center", va="center", fontsize=20, color=MUTED)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    im = _fig_to_image(fig)
    plt.close(fig)
    return im, False


# ================================================================================================= the movie
def movie():
    import carousel as C
    import setup_lab as SL
    sc, L, rigs, u = build()
    rb = u.robot
    car = L.carousel
    cab = f"{u.name}_cab"
    PARK = np.radians(A.PARK_DEG)
    nano = rig_of(rigs, "nanoindenter")
    week, week_real = week_panel()
    chart_ok, chart_out = control_chart(False), control_chart(True)
    try:
        chart_ok.save(OUT / "upkeep_clip_chart.png")
        chart_out.save(OUT / "upkeep_clip_chart_whatif.png")
    except OSError:
        pass

    # ------------------------------------------------------------------ our parts: the weight, its stand
    sc.add("w_stand/stand", stand_mesh(), (0.08, 0.08, 0.09), "w_stand", specular=0.2)
    sc.parent["w_stand"] = cab
    sc.gmat["w_stand"] = T((STAND_AT[0], STAND_AT[1], CAB_TOP))
    sc.add("w_weight/weight", weight_mesh(), (0.80, 0.81, 0.83), "w_weight", specular=0.75)
    sc.parent["w_weight"] = "w_stand"
    sc.gmat["w_weight"] = T((0, 0, STAND["h"] - STAND["pocket"]))
    # the extraction table and the person, out of sight until part 3
    for nm, (mesh, col, spec) in table_parts().items():
        sc.add(f"xtable/{nm}", mesh, col, "xtable", specular=spec)
    T_FAR = -4400.0                    # the table's start, in the aisle, out of CAM_EXTRACT's view (round 11: 200 mm nearer,
    #                                    so the person behind it starts clear of unit 2 on its charger, front at y -5418)
    sc.gmat["xtable"] = T((0.0, T_FAR, 0.0))
    table_names = [n for n, g in sc.group_of.items() if g == "xtable"]
    person = Person(sc)
    fast_collisions(sc, L, u)
    pcheck = None
    if scene.AUDIT:
        pcheck = PeopleCheck(sc, person, L=L)
        sc.frame_hooks.append(pcheck)
    sc._pcheck = pcheck
    for n in table_names + person.names():
        sc.alpha[n] = 0.0

    rig = L.eq_groups["B"][1]
    car_xy = A.LOADS["B"][1][1:]

    def rig_w(xyz):
        return A.tray_world("B", np.asarray(xyz, float) + (*car_xy, V.T_FLOOR))
    pan = C.vial_seat()
    st = {"lbl": "", "cap": ""}

    # ------------------------------------------------------------------ helpers
    def say(label, cap):
        st["lbl"], st["cap"] = label, cap

    def step(secs, update=None, hold=0.05, cam=None, labels=(), still=False):
        sc.step(st["lbl"], st["cap"], secs, update, hold=hold, cam_to=cam, labels=labels, still=still)

    def go(Tw=None, q=None, secs=1.6, cam=None, labels=(), grip=None, hold=0.05):
        f = rb.joint_to(Tw=Tw) if Tw is not None else rb.joint_to(q)
        step(secs, RB.both(f, rb.grip_to(grip) if grip is not None else None), hold=hold, cam=cam, labels=labels)

    def lin(Tw, secs=0.8, hold=0.05, cam=None):
        step(secs, rb.line_to(Tw), hold=hold, cam=cam)

    def panel(key, im, a0, a1, where="right"):
        def up(v):
            sc.panels[key] = [im, a0 + (a1 - a0) * v, where]
        return up

    def gripper_for(width):
        """2F-85 closure with its pads `width` mm apart (ur_arm.gripper_fk; bisection)."""
        import ur_arm
        lo, hi = 0.0, 1.0

        def gap(c):
            G = ur_arm.gripper_fk(c)
            xl = (G["left_finger_tip"] @ np.array([-25.26, 0, 31.9, 1.0]))[0]
            xr = (G["right_finger_tip"] @ np.array([25.26, 0, 31.9, 1.0]))[0]
            return abs(xr - xl)
        for _ in range(40):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if gap(mid) > width else (lo, mid)
        return (lo + hi) / 2
    GRIP_W = gripper_for(WEIGHT["d"] - 0.6)

    if FROM != "3":
        # ================================================================== 1. the week
        sc.cam = list(A.CAM_LAB_VLM)
        status(L, Arm="UR10e on MiR250, at Shuttle 1", Deck="100 g E2 weight, from tray J's store")
        say("1/3 The week", "Maintenance in the workflow. A lab that runs round the clock still needs looking after: "
                            "balances checked, bowls cleaned, filters changed, thermocouples verified. Each task is booked "
                            "like a job, with who does it: the arm between jobs, or a person on a weekday shift.")
        step(2.6, None, hold=0.8)
        cap_week = ("The week's schedule from upkeep.py: experiments, the arm's own checks between them, and people's tasks "
                    "on weekday shifts, so nothing is due at once and a station is out of service only while it is worked "
                    "on.") if week_real else ("The week's schedule, maintenance booked like any job (placeholder: upkeep.py's "
                                               "week replaces it).")
        say("1/3 The week", cap_week)
        step(0.8, panel("week", week, 0.0, 1.0, "full"), hold=0.0)
        step(1.0, None, hold=6.2)
        step(0.6, panel("week", week, 1.0, 0.0, "full"), hold=0.0)
        sc.panels.pop("week", None)
        if STOP == "0":
            return finish(sc, rb)

        # ================================================================== 2. the arm's check: the HR-202i
        say("2/3 A check between jobs", "Between two dosing runs at night, the HR-202i's daily check. The arm brought the 100 g "
                                       "class E2 weight up from tray J's store with the night's first job; it rides "
                                       "on the MiR's deck, in a low seat of its own (ours). Tray B, the doser, comes down.")
        status(L, Arm="UR10e, parked", Doser="idle between runs")
        w_top = (sc.world("w_weight") @ np.r_[0, 0, WEIGHT_H, 1.0])[:3]
        CAM_DECK = [tuple(w_top + (620, -780, 520)), tuple(w_top + (-60, 120, -60)), (0, 0, 1)]
        step(2.0, None, hold=1.6, cam=CAM_DECK,
             labels=[("100 g OIML E2 weight", tuple(w_top + (0, 0, 10)), (0.30, 0.30)),
                     ("its seat on the MiR's deck (ours)", tuple(w_top + (0, -20, -40)), (0.62, 0.62))])
        L.fetch("B", st["lbl"], st["cap"], fast=0.5, cam=A.CAM_WORK, hold=0.1)
        p_hand = rig_w(C.vessel_at("vial", 1.0, 0.0) + (0, 0, GRIP_UP))
        cam_close = [tuple(rig_w(pan + (-430.0, -520.0, 190.0))), tuple(rig_w(pan + (0.0, 0.0, 60.0))), (0, 0, 1)]
        say("2/3 A check between jobs", "The arm takes the weight by its body, as weight tongs would (no skin, no oil), "
                                       "and stands it on our vessel shuttle's fork outside the doser, where it sets the "
                                       "vials down.")
        status(L, Arm="the weight: deck to the shuttle")
        Tg = A.down(w_top + (0, 0, GRIP_UP - WEIGHT_H), spin=180.0)
        go(Tw=A.down(w_top + (0, 0, GRIP_UP - WEIGHT_H + 110), spin=180.0), secs=1.6, grip=0.0, cam=A.CAM_WORK)
        lin(Tg, 0.8)
        step(0.4, rb.grip_to(GRIP_W))
        rb.grasp("w_weight")
        lin(A.down(w_top + (0, 0, GRIP_UP - WEIGHT_H + 110), spin=180.0), 0.7)
        go(Tw=A.down(p_hand + (0, 0, 120), spin=180.0), secs=1.6,
           labels=[("our vessel shuttle", tuple(p_hand + (0, 0, 60)), (0.60, 0.30))])
        lin(A.down(p_hand, spin=180.0), 0.8)
        step(0.4, rb.grip_to(0.0))
        rb.release(car.fork_group)
        lin(A.down(p_hand + (0, 0, 120), spin=180.0), 0.7)
        say("2/3 A check between jobs", "The arm parks. The side door opens, the shuttle carries the weight in, sets it "
                                       "on the pedestal on the pan and backs out; the door shuts. The HR-202i has no "
                                       "internal mass (A&D's HR-i manual: calibrate 'using a weight that you have'), so "
                                       "this weight is its check, and once a month its calibration.")
        status(L, Arm="parked", Doser="shuttle in", **{"HR-202i": "0.0000 g  tared"})
        step(1.2, RB.both(rb.joint_to(PARK), car.to(side_door=C.SIDE_OPEN)), cam=cam_close)
        step(1.8, car.to(shuttle=0.0),
             labels=[("A&D HR-202i, side door open", tuple(rig_w(pan + (-80, -120, 120))), (0.24, 0.24)),
                     ("the pedestal on the pan", tuple(rig_w(pan + (0, 0, -60))), (0.70, 0.66))])
        step(0.5, car.to(fork=A.SET_U), hold=0.0)
        car.reparent("w_weight", rig)
        step(0.3, car.to(fork=1.0))
        step(1.4, car.to(shuttle=1.0))
        step(0.7, car.to(side_door=0.0, fork=0.0))
        reading = WEIGHT["g"] + TODAY_MG / 1000.0

        def settle(v):
            r = WEIGHT["g"] * min(1.0, v * 1.15) + (TODAY_MG / 1000.0 if v > 0.85 else 0.0)
            sc.clock = ("HR-202i, 220 g x 0.1 mg", f"{r:9.4f} g" + ("  stable" if v > 0.85 else ""))
        say("2/3 A check between jobs", "Doors shut, the reading settles: 100.0001 g against the weight's certificate. "
                                       "The shuttle lifts it off and back ten times (USP <41>'s repeatability; one is "
                                       "shown), and the mean goes on the control chart against the lab's limits.")
        status(L, Doser="the check weight on the pan", **{"HR-202i": "settling"})
        # the reading's view: along cam_close's line of sight to the weight (clear of the doser's frame), 55 % closer,
        # the weight a third of the way across, so the control chart (the right 46 %) leaves it in view
        w_pan = (sc.world("w_weight") @ np.r_[0, 0, WEIGHT_H / 2, 1.0])[:3]
        e0 = np.asarray(cam_close[0], float)
        eye = e0 + 0.55 * (w_pan - e0)
        dv = w_pan - eye
        right = np.cross(dv, (0.0, 0.0, 1.0))
        right /= max(np.linalg.norm(right), 1e-9)
        cam_read = [tuple(eye), tuple(w_pan + 0.19 * np.linalg.norm(dv) * right), (0, 0, 1)]
        step(1.6, settle, hold=0.2, cam=cam_read)
        status(L, **{"HR-202i": f"{reading:.4f} g: +{TODAY_MG:.1f} mg, pass"})
        step(0.6, panel("chart", chart_ok, 0.0, 1.0), hold=0.0)
        step(1.0, None, hold=3.4)
        say("2/3 A check between jobs", "Had it read outside the limits, the arm repeats it once; still out, the scheduler "
                                       "flags the doser, so no doses are booked on it, and books a person's task for "
                                       "the next shift: clean the chamber, level, calibrate with the E2 set.")
        sc.panels["chart_out"] = [chart_out, 0.0, "right"]

        def whatif(v):
            sc.panels["chart"][1] = 1.0 - v
            sc.panels["chart_out"][1] = v
        step(0.6, whatif, hold=0.0)
        status(L, Doser="FLAGGED (what if): jobs held", Booked="person, next shift: HR-202i service")
        step(1.0, None, hold=3.6)
        status(L, Doser="online (today's check passed)", Booked="")

        def chart_off(v):
            sc.panels["chart_out"][1] = 1.0 - v
        step(0.5, chart_off, hold=0.0)
        sc.panels.clear()
        sc.clock = None
        say("2/3 A check between jobs", "Today it passed. The shuttle brings the weight back out, the arm returns it to "
                                       "its seat on the deck (it goes back to tray J with the next run's samples), and "
                                       "tray B goes back up. About twelve minutes (upkeep.py books 0.2 h), between two "
                                       "night-time jobs.")
        status(L, Doser="shuttle out", **{"HR-202i": ""})
        step(0.7, car.to(side_door=C.SIDE_OPEN, fork=1.0), cam=cam_close)
        step(1.4, car.to(shuttle=0.0), hold=0.0)
        step(0.3, car.to(fork=A.SET_U), hold=0.0)
        car.reparent("w_weight", car.fork_group)
        step(0.4, car.to(fork=0.0), hold=0.0)
        step(1.4, car.to(shuttle=1.0), hold=0.0)
        step(0.5, car.to(side_door=0.0))
        status(L, Arm="the weight: shuttle to the deck", Doser="")
        go(Tw=A.down(p_hand + (0, 0, 120), spin=180.0), secs=1.4, grip=0.0, cam=A.CAM_WORK)
        lin(A.down(p_hand, spin=180.0), 0.7)
        step(0.4, rb.grip_to(GRIP_W))
        rb.grasp("w_weight")
        lin(A.down(p_hand + (0, 0, 120), spin=180.0), 0.6)
        seat_w = (sc.world("w_stand") @ np.r_[0, 0, STAND["h"] - STAND["pocket"], 1.0])[:3]
        go(Tw=A.down(seat_w + (0, 0, GRIP_UP + 110), spin=180.0), secs=1.4)
        lin(A.down(seat_w + (0, 0, GRIP_UP), spin=180.0), 0.7)
        step(0.4, rb.grip_to(0.0))
        rb.release("w_stand")
        lin(A.down(seat_w + (0, 0, GRIP_UP + 110), spin=180.0), 0.6)
        status(L, Arm="parked")
        step(1.2, rb.joint_to(PARK))
        L.store("B", st["lbl"], st["cap"], fast=0.45, cam=CAM_OPEN, hold=0.1)
        if STOP == "2":
            return finish(sc, rb)

    # ================================================================== 3. a person's task: tray E out
    x2 = SL.X2
    dock = list(u.pose)
    NP = __import__("instruments").NANO
    sz = NP["feet"] + 70 + NP["stage_z"] - 60          # the stage's top in the iMicro's frame (r8_char.nanoindenter)
    nw = lambda q: (sc.world(f"{nano.prefix}body") @ np.r_[q, 1.0])[:3]          # noqa: E731
    say("3/3 A person's task", "A person's task, counted rather than dated: after 600 runs the iMicro's Berkovich tip "
                               "is due (upkeep.py: two hours, the tray pulled out). Tray E comes to the opening; the "
                               "tip sits 0.8 m from where a person stands there.")
    status(L, Arm="parked", Deck="", iMicro="tip due: 600 runs; booked, a person")
    L.fetch("E", st["lbl"], st["cap"], fast=0.5, cam=CAM_OPEN, hold=0.2,
            )
    sc.step(st["lbl"], st["cap"], 0.8, None, hold=0.6,
            labels=[("KLA iMicro nanoindenter", tuple(nw((0, 0, NP["H"] + 40))), (0.36, 0.20))])
    # the MiR drives off to Shuttle 2, where it carries on; the person rolls the table in behind it
    tip0 = nw((NP["head_x"], 0.0, sz + 60.0))
    # round 11: where the person stands, from people.Person's reach (people.py) and the check (PeopleCheck)
    xp = float(tip0[0]) - 150.0                      # the right shoulder in line with the indenter head
    y_push, lean_push = 215.0, 24.0                  # pushing: 215 mm behind the table's front edge, a 24 deg stoop
    y_work, lean_work = TABLE_FRONT - 195.0, 42.0    # by the table; the tip change: a deep bend into the iMicro
    y_start = T_FAR - TABLE["d"] / 2 - y_push
    BAR_TOP = V.Z_OPEN - 30.0                        # the push bar's top (table_parts)
    hand_z = {"l": 900.0, "r": 900.0}                # the palms' targets, settled each frame onto the bar

    def hands_on_table():
        yb = sc.gmat["xtable"][1, 3] - TABLE["d"] / 2
        return {"l": (xp - 215.0, yb + 15.0, hand_z["l"]), "r": (xp + 215.0, yb + 15.0, hand_z["r"])}

    def settle_hands(n=2):
        """The fingers resting on the push bar: each palm's target is raised or lowered until the glove's lowest point
        over the bar is 0.5 mm above its top (the movers check counts a contact deeper than 1.5 mm)."""
        yb = sc.gmat["xtable"][1, 3] - TABLE["d"] / 2
        for _ in range(n):
            G = person.posed()["glove"][0]
            for sd in ("l", "r"):
                hp = person.hand_point(sd)
                near = G[(np.linalg.norm(G - hp, axis=1) < 160.0) & (G[:, 1] >= yb - 2.0) & (G[:, 1] <= yb + 32.0)]
                if len(near):
                    hand_z[sd] += BAR_TOP + 0.5 - float(near[:, 2].min())
            person.set(hands=hands_on_table())

    def keep(tag):
        """PREVIEW: the step's last frame at full size, for a close look at the person."""
        if PREVIEW and sc.preview:
            sc.preview[-1].convert("RGB").save(f"/tmp/upkeep_{tag}.png")

    def reach_err(tag):
        if PREVIEW or scene.AUDIT:
            for sd in ("l", "r"):
                t = person.st["hands"][sd]
                if t is not None:
                    e = float(np.linalg.norm(person.hand_point(sd) - np.asarray(t, float)))
                    if e > 15.0:
                        print(f"reach {tag} {sd}: palm {e:.0f} mm from its target", flush=True)

    def allow(*pairs):
        if pcheck is not None:
            pcheck.allow = set(pairs)
    if os.environ.get("UPKEEP_NOCAMS"):              # a diagnostic: tray E's camera units out of the check and the view
        for n, g in sc.group_of.items():
            if g.startswith(("cam_E0", "cam_E1")):
                sc.alpha[n] = 0.0
    for n in table_names + person.names():
        sc.alpha[n] = 1.0
    person.set(x=xp, y=y_start, hd=0.0, lean=lean_push, amp=0.0, phase=0.0, look=None, grip={"l": 0.35, "r": 0.35})
    print(f"tip {np.round(tip0)}, xp {xp:.0f}, table front {TABLE_FRONT:.0f}, tray E y {L.tray['E'][0]:.0f}", flush=True)
    person.set(hands=hands_on_table())
    settle_hands(3)
    say("3/3 A person's task", "The MiR250 + UR10e drives off to Shuttle 2, which carries on working: only Shuttle 1's "
                               "opening is taken. A person rolls the extraction table (ours: Kardex publishes no size "
                               "for its device or its cart) to the opening and docks it against the cover.")
    status(L, Arm="UR10e on MiR250: to Shuttle 2")
    x0d, y0d, hd0 = dock
    dist = x2 - x0d
    t_drive = max(1.2, P.ramp_secs(dist, MIR_SPEED))
    walk_d = TABLE_Y - T_FAR

    def drive_and_roll(v):
        f = P.ramp_frac(P.unease(v), dist, MIR_SPEED)
        u.set((x0d + dist * f, y0d, hd0))
        w = min(1.0, max(0.0, (v - 0.30) / 0.70))
        ws = 0.5 - 0.5 * math.cos(math.pi * w)
        sc.gmat["xtable"] = T((0.0, T_FAR + walk_d * ws, 0.0))
        s = walk_d * ws
        person.set(y=y_start + s, amp=min(1.0, 4.0 * min(w, 1.0 - w)), phase=2 * math.pi * s / STRIDE,
                   hands=hands_on_table())
        settle_hands()
        if v >= 1.0:
            reach_err("push")
    step(t_drive, drive_and_roll, hold=0.1, cam=CAM_EXTRACT,
         labels=[("extraction table (assumed size)", (900.0, TABLE_Y - 300, V.Z_OPEN + 40), (0.74, 0.32))])
    keep("push")
    person.set(amp=0.0, phase=0.0)
    status(L, Arm="UR10e on MiR250, at Shuttle 2 (working)")
    say("3/3 A person's task", "Kardex's full tray extraction: \"a tray is placed in front of the access opening\". The "
                               "tray leaves its dock in the bay, so it runs on nothing while it is out (the iMicro shut "
                               "down first). It rolls out onto the table's rails.")
    L.focus = None
    L.where["E"] = None
    status(L, **{"Tray E": "out on the table, off its dock"}, iMicro="shut down for the tip change")
    y_in = L.tray["E"][0]
    allow()
    bar = hands_on_table()

    def to_rest(hands, v, over=0.0):
        """Hands from `hands` towards where they hang now, v from 0 to 1; `over` mm higher on the way (over a bar)."""
        return {sd: tuple(np.asarray(hands[sd], float) * (1.0 - v) + np.asarray(person.rest_hand(sd)) * v +
                          (0.0, 0.0, over * math.sin(math.pi * v))) for sd in ("l", "r")}

    def back_off(v):
        person.set(y=TABLE_FRONT - y_push + (y_work - 90.0 - (TABLE_FRONT - y_push)) * v, lean=lean_push * (1.0 - v))
        person.set(hands=to_rest(bar, v, over=90.0), grip={"l": 0.35 - 0.05 * v, "r": 0.35 - 0.05 * v})
    step(0.8, back_off, hold=0.0)
    person.set(hands={"l": None, "r": None})
    step(3.2, L.slide("E", y_in - EXTRACT), hold=0.2,
         labels=[("tray E, on the table's rails", (-1000.0, y_in - EXTRACT - 330, V.Z_OPEN + 80), (0.18, 0.34))])

    # the tip change (round 11). The iMicro's front panel is the cabinet's and only its lid lifts (r8_char, 180c0f4),
    # and the tip sits 235 mm under the panel's top edge and 260 mm behind it: no one reaches it over the panel. So the
    # panel is a removable service panel (assumed: KLA publishes no service drawing; r8_char's "panel" piece) that
    # lifts straight up and off. Tray E's cameras E0 and E1 stand 80 mm in front of the iMicro (services.TRAY_CAMS["E"]):
    # the person works from between their masts and keeps their body in front of them; only the arms go through.
    tip = nw((NP["head_x"], 0.0, sz + 60.0))
    front_y = nw((0.0, -NP["D"] / 2, 0.0))[1]        # the cabinet's front face
    panel_top = nw((0.0, 0.0, NP["H"] - NP["lid_t"]))[2]
    # tray E's camera masts where they are now (the tray out on the table): those standing in front of the iMicro,
    # within its width, are what the person works round (services.TRAY_CAMS["E"]; the scene's own groups, so a mast
    # moved by the lab stream is picked up)
    ix0, ix1 = nw((-NP["W"] / 2, 0.0, 0.0))[0], nw((NP["W"] / 2, 0.0, 0.0))[0]
    masts = [sc.world(g)[:3, 3] for g in sorted(sc.gmat) if g.startswith("cam_E") and g[5:].isdigit()]
    masts = [m for m in masts if m[1] < front_y and ix0 - 120.0 < m[0] < ix1 + 120.0]
    x_gap = float(nw((0.0, 0.0, 0.0))[0])            # the panel's middle
    y_mast = float(min(m[1] for m in masts)) if masts else front_y - 80.0
    for n in nano.names.get("sample", []):          # the tour's prop (a mount in the cup) stays hidden
        sc.alpha[n] = 0.0
    have_panel = "panel" in nano.inst.joints
    panel_g = f"{nano.prefix}panel"
    f_tip = tip + (-60.0, -200.0, -80.0)            # along CAM_EXTRACT's line of sight (the person stands left of it)
    CAM_TIP = [tuple(f_tip + 0.5 * (np.asarray(CAM_EXTRACT[0], float) - f_tip)), tuple(f_tip), (0, 0, 1)]
    say("3/3 A person's task", "The lid lifts and the stage runs out from under the indenter head.")
    status(L, iMicro="lid up: tip change")
    lid_moves = {"lid": (0.0, 1.0)}
    if "carriage" in nano.inst.joints:
        lid_moves["carriage"] = (0.0, 1.25)          # past its load position: clear behind the hand under the head
    if "stage" in nano.inst.joints:
        lid_moves["stage"] = (0.0, -1.0)             # the x stage 100 mm the other way: nothing under the tip
    step(1.4, nano.move(lid_moves), hold=0.1, cam=CAM_TIP,
         labels=[("indenter head, Berkovich tip", tuple(tip + (0, 0, 60)), (0.66, 0.22))])
    print(f"masts {[tuple(np.round(m[:2])) for m in masts]}, gap x {x_gap:.0f}, front {front_y:.0f}, panel top "
          f"{panel_top:.0f}, panel joint {have_panel}", flush=True)

    def side_to(x1, secs, **kw):
        x0 = person.st["x"]

        def up(v):
            s_ = (x1 - x0) * v
            person.set(x=x0 + s_, amp=min(0.35, 2.0 * min(v, 1.0 - v)), phase=2 * math.pi * abs(s_) / STRIDE, **kw)
        step(secs, up, hold=0.0)
        person.set(amp=0.0, phase=0.0)
    if have_panel:
        say("3/3 A person's task", "The front panel comes off: a removable service panel (assumed: KLA publishes no "
                                   "service drawing), lifted straight up its guides, clear of the head, from between "
                                   "the camera masts.")
        status(L, iMicro="front panel off")
        side_to(x_gap, 0.8)
        # the hands on the panel's top edge from the front, the arms between the masts: the body 455 mm in front of
        # them (people.py's skeleton, solved off-line: every part 20 mm short of the masts)
        grip_pts = {"l": np.array([x_gap - 70.0, front_y - 30.0, panel_top - 6.0]),
                    "r": np.array([x_gap + 70.0, front_y - 30.0, panel_top - 6.0])}
        PANEL_UP = 1.55                               # of its 420 mm guides' travel: 650 mm, its lower edge over the head
        y_panel = y_mast - 455.0

        def to_panel(v):
            person.set(y=y_work - 90.0 + (y_panel - (y_work - 90.0)) * v, lean=10.0 * v, look=tuple(grip_pts["r"]),
                       grip={"l": 0.1, "r": 0.1})
            person.set(hands=to_rest({k: tuple(g) for k, g in grip_pts.items()}, 1.0 - v))
        step(1.0, to_panel, hold=0.1)
        allow(("glove", panel_g))
        lift = nano.move({"panel": (0.0, PANEL_UP)})
        rise = float(nano.inst.joints["panel"].vec[2]) if hasattr(nano.inst.joints["panel"], "vec") else 420.0
        u_let = 310.0 / (rise * PANEL_UP)            # the hands follow it up 310 mm, then it slides on by itself

        def lift_off(v):
            lift(v)
            dz = rise * PANEL_UP * min(v, u_let)
            hands = {sd: tuple(grip_pts[sd] + (0.0, 0.0, dz)) for sd in ("l", "r")}
            w = max(0.0, (v - u_let) / (1.0 - u_let))
            person.set(hands=to_rest(hands, w) if v > u_let else hands, lean=10.0 * (1.0 - w))
        step(2.2, lift_off, hold=0.2)
        allow()
        person.set(hands={"l": None, "r": None}, grip={"l": 0.3, "r": 0.3})
        # people.py's skeleton, solved off-line: the body's centre 51 mm to the left of the tip, 411 mm in front of
        # the masts, bent 42 deg; the head goes into the gap between the masts, the chest stays 20 mm short of them,
        # the right palm reaches the shaft
        x_tip = float(tip[0]) - 51.0
        side_to(x_tip, 0.8)
        y_reach = y_mast - 411.0
    else:
        say("3/3 A person's task", "The tip sits 26 cm inside the cabinet, behind its fixed front panel: not shown here, "
                                   "the person takes the panel off, reaches in and changes the tip by hand.")
        x_tip, y_reach = person.st["x"], y_work - 90.0
    r_at = tip + (-45.0, 10.0, -12.0)                # the right hand beside the tip's shaft, under the head, fingers round it
    l_at = np.array([x_tip - 60.0, y_mast - 120.0, tip[2] + 60.0])   # the left hand holds the new tip, ready

    def lean_in(v):
        person.set(y=person_y0 + (y_reach - person_y0) * v, lean=lean_work * v, look=tuple(tip),
                   grip={"l": 0.55 * v, "r": 0.5 * v},
                   hands={"l": tuple(np.asarray(person.rest_hand("l")) * (1 - v) + l_at * v),
                          "r": tuple(np.asarray(person.rest_hand("r")) * (1 - v) + r_at * v)})
    person_y0 = person.st["y"]
    if have_panel:
        step(1.6, lean_in, hold=0.1)
        keep("lean_in")
        reach_err("lean in")
        tip_g = f"{nano.prefix}tip"
        tip_parent, tip_M = sc.parent.get(tip_g), sc.gmat[tip_g].copy()
        person.hold("r", tip_g)

        def unscrew(v):
            # turned loose, drawn straight down out of the head's bore (its shaft is 60 mm up it), held up to the light;
            # then the new one the same way up and turned in. It never moves sideways while it is in the head.
            u = v if v < 0.5 else 1.0 - v
            down = float(np.clip((u - 0.25) / 0.18, 0.0, 1.0))
            wob = 5.0 * math.sin(2 * math.pi * 6 * v) * (1.0 - down)
            person.set(hands={"r": tuple(r_at + (0.0, wob, -58.0 * down))})
        step(4.2, unscrew, hold=0.2, still=True)
        keep("unscrew")
        person.held.pop("r", None)
        if tip_parent is not None:
            sc.parent[tip_g] = tip_parent
        sc.gmat[tip_g] = tip_M

    def lean_out(v):
        person.set(y=y_reach + (y_work - 90.0 - y_reach) * v, lean=lean_work * (1.0 - v), grip={"l": 0.3, "r": 0.3},
                   hands={"l": tuple(l_at * (1 - v) + np.asarray(person.rest_hand("l")) * v),
                          "r": tuple(r_at * (1 - v) + np.asarray(person.rest_hand("r")) * v)})
    if have_panel:
        step(1.2, lean_out, hold=0.1)
        person.set(hands={"l": None, "r": None}, look=None)
        say("3/3 A person's task", "The panel goes back on, the lid comes down and the stage runs back.")
        side_to(x_gap, 0.8)
        low_pts = {"l": np.array([x_gap - 70.0, front_y - 30.0, panel_top - 385.0 + rise * PANEL_UP + 6.0]),
                   "r": np.array([x_gap + 70.0, front_y - 30.0, panel_top - 385.0 + rise * PANEL_UP + 6.0])}
        down = nano.move({"panel": (PANEL_UP, 0.0)})

        def to_low(v):
            person.set(y=y_work - 90.0 + (y_panel - (y_work - 90.0)) * v, lean=10.0 * v,
                       look=tuple(low_pts["r"]), grip={"l": 0.1, "r": 0.1})
            person.set(hands=to_rest({k: tuple(g) for k, g in low_pts.items()}, 1.0 - v))
        step(0.9, to_low, hold=0.0)
        allow(("glove", panel_g))

        def panel_down(v):
            down(v)
            dz = -rise * PANEL_UP * min(v, u_let)
            hands = {sd: tuple(low_pts[sd] + (0.0, 0.0, dz)) for sd in ("l", "r")}
            person.set(hands=to_rest(hands, max(0.0, (v - u_let) / (1.0 - u_let))) if v > u_let else hands)
        step(2.0, panel_down, hold=0.1)
        allow()

        def step_back(v):
            person.set(y=y_panel + (y_work - 90.0 - y_panel) * v, lean=10.0 * (1.0 - v), grip={"l": 0.3, "r": 0.3})
        step(0.6, step_back, hold=0.0)
    person.set(hands={"l": None, "r": None}, look=None)
    say("3/3 A person's task", "Hood down, the tray rolls back into the bay and onto its dock: power back. The person "
                               "takes the table away. The new tip's area function is the arm's job, booked as its next "
                               "one on tray E: indents in the fused-silica reference (upkeep.py's weekly check).")
    status(L, iMicro="new tip; fused-silica check booked, the arm", **{"Tray E": "back in the bay"})
    back_moves = {k: (None, 0.0) for k in lid_moves}
    step(1.2, nano.move(back_moves), hold=0.0)
    step(3.0, L.slide("E", y_in), hold=0.1, cam=CAM_EXTRACT)
    L.where["E"] = "open"
    L.focus = "E"
    status(L, **{"Tray E": ""})
    # the table goes, the MiR comes back
    y_away = T_FAR

    def table_off(v):
        s = (y_away - TABLE_Y) * v
        sc.gmat["xtable"] = T((0.0, TABLE_Y + s, 0.0))
        person.set(y=TABLE_FRONT - y_push + s, hd=0.0, lean=lean_push, amp=min(1.0, 4.0 * min(v, 1.0 - v)),
                   phase=2 * math.pi * s / STRIDE, hands=hands_on_table())
        settle_hands()

    def grip_again(v):
        person.set(y=y_work - 90.0 + (TABLE_FRONT - y_push - (y_work - 90.0)) * v, lean=lean_push * v,
                   grip={"l": 0.3 + 0.05 * v, "r": 0.3 + 0.05 * v})
        person.set(hands=to_rest(hands_on_table(), 1.0 - v, over=90.0))
    step(0.8, grip_again, hold=0.0)
    person.set(hands=hands_on_table())
    settle_hands(3)
    step(4.0, table_off, hold=0.0)
    for n in table_names + person.names():
        sc.alpha[n] = 0.0
    say("3/3 A person's task", "The MiR250 + UR10e docks at Shuttle 1 again; tray E goes back up until the arm's "
                               "fused-silica check on the new tip, before any sample. The iMicro's run count starts "
                               "again from zero.")
    status(L, Arm="UR10e on MiR250: back to Shuttle 1")

    def drive_back(v):
        f = P.ramp_frac(P.unease(v), dist, MIR_SPEED)
        u.set((x2 - dist * f, y0d, hd0))
    step(t_drive, drive_back, hold=0.1, cam=CAM_OPEN)
    status(L, Arm="UR10e on MiR250, at Shuttle 1", iMicro="new tip, 0 of 600 runs: fused-silica check next")
    L.store("E", st["lbl"], st["cap"], fast=0.5, cam=A.CAM_LAB_VLM, hold=0.2)
    step(1.0, None, hold=2.6)
    return finish(sc, rb)


def finish(sc, rb):
    sc.panels.clear()
    if getattr(sc, "_pcheck", None) is not None:
        sc._pcheck.save(NAME)
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm", flush=True)
    out = sc.save()
    if not (PREVIEW or scene.AUDIT):
        meta_p = OUT / f"{NAME}.json"
        try:
            meta = json.loads(meta_p.read_text())
            parts = {}
            for s in meta["substeps"]:
                k = s["label"].split(" ", 1)[0]
                p = parts.setdefault(k, dict(part=s["label"], start_frame=s["start_frame"], end_frame=s["end_frame"]))
                p["end_frame"] = s["end_frame"]
            meta["parts"] = list(parts.values())
            meta["assumed"] = {
                "extraction_table": f"{2 * TABLE['half_w']:.0f} x {TABLE['d']:.0f} mm, rails at {TABLE['z_top']:.0f} mm "
                                    "(Kardex publishes no size for its extraction device or cart)",
                "check_weight": f"{WEIGHT['g']:.0f} g OIML E2, {WEIGHT['d']:.0f} mm across, {WEIGHT_H:.1f} mm tall "
                                "(OIML R 111-1's knob form, sized from the mass)",
                "limits_mg": dict(action=LIMIT_MG, warning=WARN_MG, e2_mpe=E2_MPE_MG),
                "readings": "illustrative",
                "person": "drawn here, 1.75 m; no figure existed in the codebase"}
            meta_p.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
        except (OSError, ValueError, KeyError) as e:
            print(f"warning: {meta_p.name}: parts not added ({e})", flush=True)
    return out


if __name__ == "__main__":
    print(movie(), flush=True)
