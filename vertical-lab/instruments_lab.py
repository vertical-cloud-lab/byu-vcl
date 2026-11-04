"""Round 4, lab equipment (#303): the CubXL set up for corrosion spots, a freestanding DED machine, an automated
packaging station for sending powders out, and the question of whether a hot isostatic press could ride on a tray.

Each model is an ``instruments.Instrument`` (pieces, joints, actions), as in ``instruments.py``; ``tour.py`` loads
``REGISTRY`` and plays each one. Frame as in ``instruments.py``: x to the right, y away from you facing the front, z up,
origin at the footprint centre, millimetres.

Two things here go beyond what ``instruments.Joint`` does, so they live in this module rather than in shared code:

* ``Track``, a joint moved by a shared timeline. The CubXL's gantry, carriage and head, the electrode cap, the
  pipette tips and the liquid levels each get a track with the same knots, so one action can carry the head
  through several waypoints and pick up or set down the cap on the way, and everything stays in step.
* Two wrappers on ``scene.Scene``, installed on import and keyed on the scene's name, so they touch only these
  instruments' clips: ``step`` takes a camera move per action from ``CAMS``, and ``overlay`` draws a live plot
  from ``PLOTS`` (the potentiostat's curve). The change I'd want in ``tour.py`` instead: an ``Instrument.cams``
  list and an ``Instrument.overlay(sc, img, s)`` hook that ``tour_one`` passes to its Scene.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq
import numpy as np

import instruments as I
from instruments import Instrument, Joint, _piece, _ycyl, _xcyl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
from common import box, cyl, rbox, tube, hose  # noqa: E402

# name: (r, g, b, opacity, specular); merged into tour.MATS
MATERIALS = {
    "lab_tip": (0.90, 0.91, 0.88, 0.55, 0.4),           # natural polypropylene pipette tips
    "lab_tube": (0.88, 0.90, 0.92, 0.45, 0.6),          # 0.5 mL polypropylene tubes
    "lab_agcl": (0.36, 0.30, 0.26, 1.0, 0.4),           # an Ag/AgCl reference element
    "lab_nacl": (0.55, 0.75, 0.95, 0.70, 0.7),          # NaCl solution
    "lab_cable": (0.10, 0.10, 0.11, 1.0, 0.3),
    "lab_smoked": (0.10, 0.10, 0.11, 0.65, 0.9),       # a printer's smoked lid
    "lab_lightblue": (0.55, 0.68, 0.82, 1.0, 0.35),     # Uline's light-blue hammertone
    "lab_ptfe": (0.55, 0.38, 0.22, 1.0, 0.3),           # PTFE tape over a sealer's element
    "lab_kraft": (0.74, 0.58, 0.40, 1.0, 0.1),          # corrugated board
    "lab_foam": (0.22, 0.23, 0.24, 1.0, 0.05),          # charcoal polyurethane foam
    "lab_hdpe": (0.93, 0.93, 0.90, 0.80, 0.3),          # a milky HDPE jar
    "lab_label": (0.98, 0.98, 0.97, 1.0, 0.2),
    "lab_bag": (0.86, 0.89, 0.92, 0.38, 0.7),           # a clear polyethylene liner bag
    "lab_over": (0.92, 0.16, 0.12, 0.42, 0.2),          # what doesn't fit, highlighted
}


# ===================================================================================================== joints, hooks
@dataclass
class Track(Joint):
    """A translation that follows knots ((v, (dx, dy, dz)), ...) piecewise linearly in v, not by arc length, so
    several tracks with the same knots move in step: the gantry's y, the carriage's x, the head's z, and whatever the
    head carries."""
    knots: tuple = ()
    kind: str = "track"

    def matrix(self, v: float) -> np.ndarray:
        vs = np.array([k[0] for k in self.knots], float)
        ps = np.array([k[1] for k in self.knots], float)
        p = np.array([np.interp(v, vs, ps[:, i]) for i in range(3)])
        return I._T(p)


@dataclass
class Turn(Joint):
    """A rotation about ``axis`` through ``pivot`` whose angle follows knots ((v, deg), ...) piecewise linearly."""
    knots: tuple = ()
    kind: str = "turn"

    def matrix(self, v: float) -> np.ndarray:
        vs = np.array([k[0] for k in self.knots], float)
        ds = np.array([k[1] for k in self.knots], float)
        return I._R(self.axis, float(np.interp(v, vs, ds)), self.pivot)


class Timeline:
    """Waypoints of everything that moves with the CubXL's head, each with a duration; ``mark`` names a point for the
    actions. ``tracks()`` turns it into one ``Track`` per piece, all on the same knots."""

    def __init__(self, start: dict):
        self.t = [0.0]
        self.states = [dict(start)]
        self.marks = {"start": 0}

    def go(self, secs: float, **changes):
        s = dict(self.states[-1])
        s.update(changes)
        self.t.append(self.t[-1] + secs)
        self.states.append(s)
        return self

    def mark(self, name: str):
        self.marks[name] = len(self.t) - 1
        return self

    def v(self, name: str) -> float:
        return self.t[self.marks[name]] / self.t[-1]

    def knots(self, fn) -> tuple:
        T = self.t[-1]
        return tuple((t / T, tuple(float(c) for c in fn(s))) for t, s in zip(self.t, self.states))


PLOTS: dict = {}            # scene name -> draw(sc, img, s)
CAMS: dict = {}             # scene name -> {action index: (eye, focus)}
LABELS: dict = {}           # scene name -> {action index: [(text, xyz, (fx, fy))]}, for clips whose camera moves


def _install_hooks():
    import scene as S
    if getattr(S.Scene, "_lab_hooks", False):
        return
    orig_overlay, orig_step = S.Scene.overlay, S.Scene.step

    def overlay(self, img, scale, anchors):
        img = orig_overlay(self, img, scale, anchors)
        fn = PLOTS.get(self.name)
        if fn is not None and not S.CLEAN:
            fn(self, img, max(scale, 0.80))
        return img

    def step(self, label, caption, seconds, update=None, hold=1.2, cam_to=None, *a, **kw):
        labs = LABELS.get(self.name)
        if labs:
            idx = max((k for k in labs if k <= len(self.substeps)), default=None)
            if idx is not None:
                kw["labels"] = labs[idx]
        cams = CAMS.get(self.name)
        if cam_to is None and cams and len(self.substeps) in cams:
            eye, focus = cams[len(self.substeps)]
            cam_to = [tuple(eye), tuple(focus), (0, 0, 1)]
        return orig_step(self, label, caption, seconds, update, hold, cam_to, *a, **kw)

    S.Scene.overlay, S.Scene.step = overlay, step
    S.Scene._lab_hooks = True


_install_hooks()


def _gv(sc, key) -> float:
    """A virtual joint's value: a slide of (1, 0, 0) puts v in its group's x translation."""
    m = sc.gmat.get(key)
    return 0.0 if m is None else float(m[0, 3])


def _cone(d_top, d_bot, h, x=0.0, y=0.0, z=0.0) -> cq.Workplane:
    """A cone standing on z with its narrow end down (a pipette tip)."""
    s = cq.Solid.makeCone(d_bot / 2, d_top / 2, h, cq.Vector(x, y, z), cq.Vector(0, 0, 1))
    return cq.Workplane().add(s)


# ===================================================================================================== CubXL corrosion
# The CubXL set up for the lab's copper corrosion screen, as digital-alloy-lab PR #180 proposes it (branch
# claude/issue-213-20261013-2132, head aeda51a; folder alloy-corrosion/):
#   copper/deck_cu.py and ../plot_deck_layout.py   the deck and the head (every position below);
#   copper/protocol.md section 4                     the sequence of one spot;
#   copper/render_cubxl_cu.py                        DAL's own animation of it (cameras, the capper's STEP placement);
#   copper/copper_numbers.json                       volumes, times, the EIS and LPR numbers.
# Positions are in the CubOS deck frame of Ben's 2026-10-02 calibration: origin front left, x right, y away, z up, mm.
# They are DAL's proposal, to be re-jogged; nothing has been printed, wired or run. One change from DAL's deck, and why,
# is under CORR. The capper's mount, the 9-vial holder and the vial caps are Ben's STEP files
# (modules/electromagnetic-capper/cad/ in this repo), placed as render_cubxl_cu.py places them.
#
# The pipette is the CubXL's own, a P20 single-channel Gen2 (1-20 uL; cubxl-setup.md section 3), with 20 uL tips. So
# every liquid move here is at most 20 uL, as DAL counts them (copper_numbers.json "sulfide_mixing", cubxl-setup.md
# section 5): the 150 uL well is 7 transfers of 19.3 uL of seawater and one of 15 uL of sulfide stock; collecting it is
# 8 transfers of 18.75 uL and the 150 uL DI rinse 8 more; the acid is one 20 uL transfer. Levels are drawn from the
# volumes: 150 uL stands 4.4 mm in the well (DAL's well_level: a 2.9 mm throat 1.6 mm deep under an 8 mm bore);
# 320 uL stands 17 mm in a 0.5 mL tube; 135 uL lowers a 20 mL stock 0.27 mm.
CAPPER_CAD = HERE.parent / "modules" / "electromagnetic-capper" / "cad"
DAL_AT = "digital-alloy-lab PR #180 at aeda51a"

CORR = dict(
    deck_z=80.0, x0=-180.0, y0=-232.5, travel_z=122.0, park=(236.0, 25.0),
    # the coupon tray (plot_deck_layout.TRAY): S1-S3 hold the specimens, S4 a PTFE blank (protocol.md section 2)
    tray=(170.0, 275.0, 220.0, 260.0), stations=(185.0, 210.0, 235.0, 260.0), station_y=240.0, face=20.0, lid=26.0,
    specimens=(("C71500 Cu-Ni", "lab_cuni"), ("C95800 NAB", "lab_nab"), ("DED pad", "lab_ded"),
               ("PTFE blank", "lab_ptfe")),
    # the well (protocol.md section 2, render_cubxl_cu.py): AS568-006 in a 7.30 x 1.40 mm counterbore, a 2.9 mm throat
    # 1.6 mm deep, an 8 mm bore above it; the cap's reference tip 3.0 mm above the metal
    a_spot=1.45, z_step=1.6, r_bore=4.0, ref_tip=3.0,
    # Ben's 9-position 20 mL holder at x 318, positions y 35 + 33k (deck_cu.py); 20 mL vials, rim 56, cap top 71
    holder_x=318.0, holder_y0=35.0, holder_dy=33.0, holder_top=35.0, vial_rim=56.0, vial_cap=71.0,
    stocks=(("spare (FeSO4 nights only)", 0, "lab_feso4"), ("1 M HNO3, trace metal", 1, "lab_acid"),
            ("ASW (D1141, no heavy metals)", 2, "lab_asw"), ("ASW + 10 mg/L S", 3, "lab_sulf"),
            ("ASW + 0.1 mg/L S", 4, "lab_sulf2"), ("DI water", 5, "lab_di")),          # positions 6 and 7 stay empty
    stock_ml=18.0,
    # rinse 2 (ASW), rinse 1 (DI), the park cup (the reference's storage solution): 4 mL vials, rim 45
    cups=(("rinse 2 (ASW)", 30.0, "lab_asw"), ("rinse 1 (DI)", 60.0, "lab_di"), ("park cup", 90.0, "lab_store")),
    cup_y=245.0, cup_rim=45.0,
    # 2 x 8 open 0.5 mL PP tubes, x 176 + 12k, y 28 / 46, top 32; rack 170-266 x 20-54
    tubes_x0=176.0, tubes_dx=12.0, tubes_y=(28.0, 46.0), tube_top=32.0, tube_rack=(170.0, 266.0, 20.0, 54.0),
    # tip racks, 2 x 15 at 8.5 mm (plot_deck_layout): rack 1 is Ben's, unmoved, A1 (291.332, 89), A2 8.5 mm to its left;
    # rack 2, DAL's printed one, A1 (108, 89). Tips 39 mm, top 66; the nozzle seats 4 mm in, so the end is 35 below it
    rack1=(291.332, 89.0), rack2=(108.0, 89.0), rack_pitch=8.5, rack_rows=15, rack_top=55.0, tip_top=66.0,
    tip_len=39.0, tip_hang=35.0,
    # the tip waste, moved by the copper deck to (385, 150) because the full holder covers (335, 40)
    waste=(385.0, 150.0), waste_d=30.0, waste_top=50.0,
    # the head (cubxl-setup.md section 3): capper (0, 0), magnet face 16 below the carriage; P20 (+55, +11), its bare
    # nozzle at the carriage's reference; camera (-40, +10)
    pip=(55.0, 11.0), cam=(-40.0, 10.0), magnet=16.0,
    # the electrode cap (copper version, deck_cu.py): 16 mm body on a 26 mm flange, its electrodes 3 mm below the skirt,
    # so the reference tip sits 3.0 mm above the metal; carried, it hangs 16 + 16 + 3 mm below the carriage
    cap_d=26.0, cap_h=16.0, cap_el=3.0,
    # the potentiostat the lab has now: NuVant's EZstat Pro, lent by Dr. Porter (byu-vcl #231, DAL #221), 255 x 245 x 102
    # mm. It has no EIS: until the requested potentiostat comes, DAL skips the EIS step and runs OCP for 30 min
    ez=(255.0, 245.0, 102.0), ez_x=530.0)
# Everything is where DAL puts it. One thing to raise with DAL: its deck check is in plan, with the capper as a 10 mm-
# radius disc (plot_deck_layout.RADIUS). Ben's real mount, the PAW-V2 STEP placed as render_cubxl_cu.py places it, is
# 41 x 31 mm in its lowest 16 mm (x -25.2 to +15.7, y -16.7 to +14.5 about the capper's axis). Every waypoint of this
# clip, checked against the deck with CadQuery booleans: it clears everything but one. Drawing from the ASW and the
# 10 mg/L S stocks (carriage at 70), the mount's lower edge is 1.6 mm into Ben's rack 1 over 12 mm, 1 mm below the
# rack's top, if that rack is DAL's tips +- 5.75 mm wide and 55 mm tall (render_cubxl_cu.py draws it so).
CORR["rack2_drawn"] = CORR["rack2"]
MATERIALS.update({
    "lab_cuni": (0.72, 0.60, 0.54, 1.0, 0.8),          # C71500 70/30 Cu-Ni, polished (render_cubxl_cu.py colours)
    "lab_nab": (0.76, 0.61, 0.33, 1.0, 0.8),           # C95800 nickel-aluminium bronze
    "lab_ded": (0.75, 0.54, 0.38, 1.0, 0.8),           # a DED Cu-Ni pad
    "lab_ptfe": (0.97, 0.97, 0.96, 1.0, 0.1),
    "lab_lid": (0.91, 0.64, 0.49, 1.0, 0.25),          # the printed well lids
    "lab_tray": (0.96, 0.94, 0.90, 1.0, 0.15),
    "lab_petg": (0.87, 0.86, 0.82, 1.0, 0.15),
    "lab_petg_dark": (0.78, 0.76, 0.71, 1.0, 0.15),
    "lab_asw": (0.61, 0.78, 0.91, 0.80, 0.6),          # ASTM D1141 substitute ocean water
    "lab_sulf": (0.90, 0.84, 0.54, 0.80, 0.6),         # ASW + 10 mg/L S
    "lab_sulf2": (0.93, 0.89, 0.71, 0.80, 0.6),        # ASW + 0.1 mg/L S
    "lab_acid": (0.95, 0.94, 0.90, 0.75, 0.6),         # 1 M trace-metal HNO3
    "lab_di": (0.85, 0.93, 0.97, 0.70, 0.6),
    "lab_feso4": (0.81, 0.88, 0.78, 0.80, 0.6),
    "lab_store": (0.85, 0.82, 0.92, 0.80, 0.6),        # the reference's storage solution
    "lab_well": (0.36, 0.62, 0.92, 0.90, 0.6),         # the liquid in a well, a tip or a tube, drawn darker to show
    "lab_mount": (0.61, 0.61, 0.59, 1.0, 0.3),
    "lab_pip": (0.11, 0.11, 0.11, 1.0, 0.3),
    "lab_pip_shaft": (0.91, 0.91, 0.89, 1.0, 0.3),
})


def _cx(x):
    return CORR["x0"] + x


def _cy(y):
    return CORR["y0"] + y


def _cz(z):
    return CORR["deck_z"] + z


def _corr_w(x, y, z):
    """CubOS deck coordinates -> the model's frame."""
    return (_cx(x), _cy(y), _cz(z))


def well_level(ul: float, capped: bool = False) -> float:
    """Height of `ul` microlitres above the metal in a -006 well (render_cubxl_cu.well_level): the 2.9 mm throat to
    1.6 mm, then the 8 mm bore; with the cap on, its 2 mm capillary displaces the liquid above its tip."""
    p = CORR
    a2 = math.pi * p["a_spot"] ** 2
    throat = a2 * p["z_step"]
    lvl = ul / a2 if ul <= throat else p["z_step"] + (ul - throat) / (math.pi * p["r_bore"] ** 2)
    if capped and lvl > p["ref_tip"]:
        lvl = p["ref_tip"] + (lvl - p["ref_tip"]) * p["r_bore"] ** 2 / (p["r_bore"] ** 2 - 1.0)
    return lvl


# a 0.5 mL tube's inside, (z, r) from its floor: a cone to 12.4 mm, then 6.5 mm across to the rim
_TUBE_IN = ((0.8, 0.6), (12.4, 3.1), (31.2, 3.25))


def _tube_r(z):
    zs, rs = zip(*_TUBE_IN)
    return float(np.interp(z, zs, rs)) if z >= zs[0] else 0.0


def tube_level(ul: float) -> float:
    """Height above the tube's outside bottom of `ul` microlitres, from _TUBE_IN."""
    if ul <= 0:
        return 0.0
    z, v, dz = _TUBE_IN[0][0], 0.0, 0.02
    while v < ul and z < _TUBE_IN[-1][0]:
        v += math.pi * _tube_r(z + dz / 2) ** 2 * dz
        z += dz
    return z


def tip_level(ul: float) -> float:
    """Height above a 20 uL tip's end of `ul` microlitres: its bore widens from 0.6 mm at the end at 0.072 mm/mm."""
    if ul <= 0:
        return 0.0
    z, v, dz = 0.0, 0.0, 0.02
    while v < ul and z < 30:
        r = 0.3 + 0.072 * (z + dz / 2)
        v += math.pi * r * r * dz
        z += dz
    return z


@dataclass
class Level(Joint):
    """A liquid's height, following knots ((v, h mm), ...) piecewise linearly: the piece, modelled from z0 to z0 + h0,
    is stretched in z about z0 to height h. Empty, it is flattened and dropped 2 mm, into what holds it."""
    knots: tuple = ()
    z0: float = 0.0
    h0: float = 1.0
    kind: str = "level"

    def matrix(self, v: float) -> np.ndarray:
        vs = np.array([k[0] for k in self.knots], float)
        hs = np.array([k[1] for k in self.knots], float)
        h = float(np.interp(v, vs, hs))
        s = h / self.h0 if h > 0.02 else 1e-3
        m = np.eye(4)
        m[2, 2] = s
        m[2, 3] = self.z0 * (1.0 - s) - (2.0 if h <= 0.02 else 0.0)
        return m


# ----------------------------------------------------------------------------------------------- one spot, as a timeline
TIP_UL = 135.0 / 7               # one seawater transfer: 135 µL in 7 (protocol.md section 3)
PACE = 0.85                      # video seconds per second of the timeline


class Head:
    """Writes the CubXL head's moves into a Timeline, as render_cubxl_cu.py's Story does: every XY move at travel
    height (CubOS's multi_tool_safe_travel_z), the tool lowered over its target. Positions are CubOS deck mm; the state's
    x, y, z are the capper's axis and the carriage's reference (the bare P20 nozzle's end)."""

    def __init__(self, tl: Timeline):
        self.tl, self.speed = tl, 1.0
        self.p = CORR

    def go(self, secs, **kw):
        self.tl.go(secs * self.speed, **kw)

    def travel(self, x, y):
        TZ = self.p["travel_z"]
        s = self.tl.states[-1]
        if s["z"] < TZ - 1e-6:
            self.go(max(0.25, (TZ - s["z"]) / 110.0), z=TZ)
        s = self.tl.states[-1]
        d = math.hypot(x - s["x"], y - s["y"])
        if d > 0.01:
            self.go(max(0.3, d / 190.0), x=x, y=y)

    def down(self, z, **kw):
        self.go(max(0.25, abs(self.tl.states[-1]["z"] - z) / 110.0), z=z, **kw)

    def up(self, secs=0.3):
        self.go(secs, z=self.p["travel_z"])

    def pip_to(self, x, y, tip_end):        # the P20 with a tip, its end at deck z tip_end
        self.travel(x - self.p["pip"][0], y - self.p["pip"][1])
        self.down(tip_end + self.p["tip_hang"])

    def bare_to(self, x, y, nozzle):        # the bare P20 nozzle at deck z `nozzle`
        self.travel(x - self.p["pip"][0], y - self.p["pip"][1])
        self.down(nozzle)

    def capper_to(self, x, y, face):        # the capper's magnet face at deck z `face`
        self.travel(x, y)
        self.down(face + self.p["magnet"])

    def camera_to(self, x, y):
        self.travel(x - self.p["cam"][0], y - self.p["cam"][1])


def _corr_start(**kw) -> dict:
    p = CORR
    s = dict(x=p["park"][0], y=p["park"][1], z=p["travel_z"], cap="park", vcap="", tip="rack", tip2="rack",
             tip3="rack", tip_ul=0.0, liq="", well=0.0, tube=0.0, capped=0, meas=0.0, xfer="", panel=0,
             asw=p["stock_ml"], s10=p["stock_ml"], acid=p["stock_ml"], what="", lapse=0, end=0.0, vial=0.0)
    s.update(kw)
    return s


def _corr_spot() -> Timeline:
    """The head and everything that changes on the deck through one spot (protocol.md section 4, render_cubxl_cu.py's
    build_story). Numbers interpolate between waypoints; text (what the tip holds, which transfer) holds from the
    waypoint where it is set."""
    p = CORR
    TZ = p["travel_z"]
    tl = Timeline(_corr_start())
    h = Head(tl)
    speed = h
    go, travel, down, pip_to, bare_to, capper_to, camera_to = (h.go, h.travel, h.down, h.pip_to, h.bare_to,
                                                               h.capper_to, h.camera_to)
    st = p["stations"]
    S1 = (st[0], p["station_y"])
    hy = lambda k: p["holder_y0"] + k * p["holder_dy"]     # noqa: E731
    acid, asw, s10, di = (p["holder_x"], hy(1)), (p["holder_x"], hy(2)), (p["holder_x"], hy(3)), (p["holder_x"], hy(5))
    tube1 = (p["tubes_x0"], p["tubes_y"][0])
    r1a1, r1a2 = p["rack1"], (p["rack1"][0] - p["rack_pitch"], p["rack1"][1])
    r2a1 = CORR["rack2_drawn"]
    lid, face, cup = p["lid"], p["face"], p["cup_rim"]
    cap_face = p["cap_h"]              # the magnet face sits on the cap's disc, cap_h above where the cap rests
    over = lid + 1.0                   # dispense with the tip end 1 mm over the lid: above the meniscus (4.4 mm max)
    # 0. the deck, the head parked
    go(2.6)
    tl.mark("start")
    # 1. a 20 µL tip from Ben's rack
    bare_to(*r1a1, p["tip_top"] - 4.0)
    go(0.2, tip="head", panel=1, what="takes a 20 µL tip from Ben's rack 1")
    go(0.3, z=TZ)
    tl.mark("tip")
    # 2. the capper lifts the seawater cap; 135 µL of ASW in 7 transfers of 19.3 µL, from above the meniscus
    capper_to(*asw, p["vial_cap"])
    go(0.2, vcap="asw", what="the capper lifts the ASW cap")
    go(0.25, z=TZ)
    for k in range(1, 8):
        speed.speed = 1.0 if k == 1 else 0.18
        lapse = 0 if k == 1 else 1
        pip_to(*asw, 35.0)
        go(0.35, tip_ul=TIP_UL, liq="ASW", asw=p["stock_ml"] - k * TIP_UL / 1000, xfer=f"ASW transfer {k} of 7",
           what=f"draws {TIP_UL:.1f} µL of ASW", lapse=lapse)
        pip_to(*S1, over)
        go(0.35, tip_ul=0.0, well=k * TIP_UL, what=f"dispenses it into S1, above the meniscus")
    speed.speed = 1.0
    capper_to(*asw, p["vial_cap"])
    go(0.2, vcap="", lapse=0, what="the ASW cap goes back")
    go(0.25, z=TZ)
    tl.mark("asw")
    # 3. sulfide last: 15 µL of the 10 mg/L S stock with the same tip -> 150 µL at 1 mg/L S; the tip to the waste
    capper_to(*s10, p["vial_cap"])
    go(0.2, vcap="s10", what="the capper lifts the 10 mg/L S cap")
    go(0.25, z=TZ)
    pip_to(*s10, 35.0)
    go(0.35, tip_ul=15.0, liq="10 mg/L S", s10=p["stock_ml"] - 0.015, xfer="sulfide, 1 transfer",
       what="draws 15 µL of the 10 mg/L S stock")
    pip_to(*S1, over)
    go(0.35, tip_ul=0.0, well=150.0, what="adds it to S1: 150 µL at 1 mg/L S")
    capper_to(*s10, p["vial_cap"])
    go(0.2, vcap="", what="the sulfide cap goes back")
    pip_to(*p["waste"], 60.0)
    go(0.3, tip="waste", xfer="", liq="", what="the tip drops into the waste")
    tl.mark("filled")
    # 4. leak check with the head camera, 2 min
    camera_to(*S1)
    go(1.6, what="head camera: no liquid outside the O-ring after 2 min")
    tl.mark("leak")
    # 5. the electrode cap from the park cup onto S1's boss (tipless)
    capper_to(p["cups"][2][1], p["cup_y"], cup + cap_face)
    go(0.25, cap="head", what="the capper picks up the electrode cap")
    go(0.3, z=TZ)
    capper_to(*S1, lid + cap_face)
    go(0.25, cap="S1", capped=1, what="it sets the cap over S1's boss")
    go(0.3, z=TZ)
    travel(*p["park"])
    tl.mark("capped")
    # 6. the measurement; the head is free
    go(9.0, meas=1.0, what="")
    tl.mark("measured")
    # 7. the cap off, dipped in DI water, then in seawater, parked
    capper_to(*S1, lid + cap_face)
    go(0.25, cap="head", capped=0, what="the magnet lifts the cap off S1")
    for (_, cx_, _), what in ((p["cups"][1], "dipped in DI water"), (p["cups"][0], "dipped in seawater")):
        capper_to(cx_, p["cup_y"], cup + cap_face)
        go(0.35, what=what)
        go(0.25, z=TZ)
    capper_to(p["cups"][2][1], p["cup_y"], cup + cap_face)
    go(0.25, cap="park", what="parked")
    go(0.25, z=TZ)
    tl.mark("parked")
    # 8. a new tip; the well's 150 µL to tube 1 in 8 transfers of 18.75 µL; the 150 µL DI rinse the same way
    bare_to(*r1a2, p["tip_top"] - 4.0)
    go(0.2, tip2="head", what="a new tip")
    go(0.3, z=TZ)
    for k in range(1, 9):
        speed.speed = 1.0 if k == 1 else 0.15
        pip_to(*S1, face + 0.5)
        go(0.35, tip_ul=18.75, liq="the well's liquid", well=150.0 - k * 18.75, xfer=f"collect: transfer {k} of 8",
           what="draws 18.75 µL from S1", lapse=0 if k == 1 else 1)
        pip_to(*tube1, 40.0)
        go(0.35, tip_ul=0.0, tube=k * 18.75, what="dispenses it into tube 1, above the rim")
    speed.speed = 1.0
    go(0.6, well=150.0, xfer="DI rinse: 150 µL into S1", liq="", lapse=1, what="the 150 µL DI rinse")
    for k in range(1, 9):
        speed.speed = 0.10
        pip_to(*S1, face + 0.5)
        go(0.35, tip_ul=18.75, liq="the rinse", well=150.0 - k * 18.75, xfer=f"rinse: transfer {k} of 8", lapse=1)
        pip_to(*tube1, 40.0)
        go(0.35, tip_ul=0.0, tube=150.0 + k * 18.75)
    speed.speed = 1.0
    pip_to(*p["waste"], 60.0)
    go(0.3, tip2="waste", xfer="", liq="", lapse=0, what="the tip drops into the waste")
    tl.mark("collected")
    # 9. acidify at once: the acid cap off, the night's one acid tip (rack 2), 20 µL of 1 M HNO3 from above the rim,
    # the acid tip back to its rack, the cap back
    capper_to(*acid, p["vial_cap"])
    go(0.2, vcap="acid", what="the capper lifts the acid cap")
    go(0.25, z=TZ)
    bare_to(*r2a1, p["tip_top"] - 4.0)
    go(0.2, tip3="head", what="the night's one acid tip, from rack 2")
    go(0.3, z=TZ)
    pip_to(*acid, 35.0)
    go(0.35, tip_ul=20.0, liq="1 M HNO3", acid=p["stock_ml"] - 0.020, xfer="acid, 1 transfer",
       what="draws 20 µL of 1 M HNO3")
    pip_to(*tube1, 37.0)
    go(0.35, tip_ul=0.0, tube=320.0, what="adds it from above the rim: 320 µL, 62 mM HNO3")
    bare_to(*r2a1, p["tip_top"] - 1.0)
    go(0.25, tip3="rack", xfer="", liq="", what="the acid tip goes back to rack 2")
    go(0.3, z=TZ)
    capper_to(*acid, p["vial_cap"])
    go(0.2, vcap="", what="the acid cap goes back")
    go(0.25, z=TZ)
    tl.mark("acid")
    # 10. image the spot; park
    camera_to(*S1)
    go(1.0, what="head camera: the spot after the test")
    travel(*p["park"])
    tl.mark("imaged")
    # 11. the sequence, in one card
    go(4.0, end=1.0, panel=0, what="")
    tl.mark("end")
    return tl


_CORR_TL = _corr_spot()

# DAL's powder reactivity test (cubxl-setup.md section 8, "Where it could matter"): "Dose a weighed 10-50 mg of each
# run's powder into a tube, add 0.6 M NaCl ..., hold for a fixed time, and send the liquid to ICP with the corrosion
# tubes. Dissolved Al and Mg per gram of powder would track the oxide and surface condition the atomizer program is
# trying to control." DAL places it after the corrosion baseline and outside the BOM. Here (round 2's workflow) the
# multi-doser doses 25 mg of an atomized powder into its own 20 mL vial, the arm stands the vial in the holder's spare
# seat (y 35, free except on FeSO4 nights), and the P20 adds 200 uL of the deck's chloride electrolyte, the ASW, in 10
# transfers of 20 uL. The copper deck carries ASW rather than DAL's 0.6 M NaCl (the aluminium plan's top stock).
POWDER_TEST = dict(seat=(318.0, 35.0), mg=25.0, ul=200.0, n=10, park=(0.0, 278.0), vial_top=61.0)


def powder_test() -> Timeline:
    """The CubXL's moves for the powder test, from the head parked at the back left (clear of the arm) and back."""
    p, q = CORR, POWDER_TEST
    tl = Timeline(_corr_start(x=q["park"][0], y=q["park"][1]))
    h = Head(tl)
    asw = (p["holder_x"], p["holder_y0"] + 2 * p["holder_dy"])
    h.go(0.3)
    tl.mark("start")
    h.bare_to(*TIP_HOME["tip"], p["tip_top"] - 4.0)
    h.go(0.2, tip="head", panel=1)
    h.up()
    h.capper_to(*asw, p["vial_cap"])
    h.go(0.2, vcap="asw")
    h.up(0.25)
    tl.mark("open")
    each = q["ul"] / q["n"]
    for k in range(1, q["n"] + 1):
        h.speed = 1.0 if k == 1 else 0.16
        h.pip_to(*asw, 35.0)
        h.go(0.35, tip_ul=each, liq="ASW", asw=p["stock_ml"] - k * each / 1000, xfer=f"ASW transfer {k} of {q['n']}",
             lapse=0 if k == 1 else 1)
        h.pip_to(*q["seat"], q["vial_top"] + 5.0)
        h.go(0.35, tip_ul=0.0, vial=k * each)
        if k == 1:
            tl.mark("first")
    h.speed = 1.0
    h.capper_to(*asw, p["vial_cap"])
    h.go(0.2, vcap="", xfer="", liq="", lapse=0)
    h.up(0.25)
    h.pip_to(*p["waste"], 60.0)
    h.go(0.3, tip="waste")
    h.travel(*q["park"])
    tl.mark("end")
    return tl


_CORR_SEGS = (("start", "Copper corrosion on the CubXL, as DAL's copper screen lays it out (PR #180): four stations, S1 "
                        "C71500 Cu-Ni, S2 C95800 NAB, S3 a DED pad, S4 a PTFE blank; Ben's 9-vial holder of stocks; three "
                        "cups; 2 x 8 ICP-MS tubes; two tip racks. On the head: the capper, a P20 and a camera."),
              ("tip", "1  The CubXL's P20 (1-20 µL) takes a 20 µL tip from Ben's rack."),
              ("asw", "2  The capper lifts the seawater cap (ASTM D1141, no heavy metals). The P20 builds S1's well from "
                      "135 µL of it: 7 transfers of 19.3 µL, each dispensed from above the meniscus."),
              ("filled", "3  Sulfide last: 15 µL of the 10 mg/L S stock, with the same tip, makes 150 µL at 1 mg/L S. "
                         "The tip goes to the waste."),
              ("leak", "4  The head camera checks for liquid outside the O-ring (2 min)."),
              ("capped", "5  The capper carries the electrode cap (leak-free Ag/AgCl reference, Pt coil counter) from "
                         "its park cup and sets it over S1's boss: no O-ring, two small lid magnets hold it. No tip on."),
              ("measured", "6  Cap on, head free: OCP 20 min, EIS at OCP 10 min, LPR ±10 mV, rest 5 min, a +50 mV hold "
                           "for 10 min, OCP 5 min. EIS needs the requested potentiostat: the EZstat Pro has none, so "
                           "until then OCP runs 30 min."),
              ("parked", "7  The magnet lifts the cap off S1. It is dipped in DI water, then seawater, and parked."),
              ("collected", "8  A new tip moves the well's 150 µL to tube 1 for ICP-MS, 8 transfers of 18.75 µL, then "
                            "a 150 µL DI rinse the same way: 16 transfers."),
              ("acid", "9  Acidify at once: the capper opens the acid vial and the night's one acid tip adds 20 µL of "
                       "1 M HNO3 from above the rim: 320 µL at 62 mM HNO3. The acid tip goes back to rack 2."),
              ("imaged", "10  The head camera images the spot. Next: S2. A spot is 67 min of deck time: eight wells "
                         "(three pieces, two wells each, and S4's two blanks) take about 9 h of a 12 h night."),
              ("end", "Cyclic polarization runs only on selected spots, and last on each: fill to EIS, then the scan, "
                      "then its own tube. On every spot it would swamp the tube's copper (3.4 mC against the "
                      "hold's 0.2-2.8 mC)."))


def _corr_state(v: float) -> dict:
    """The timeline's state at v: numbers interpolated, the rest held from the last waypoint at or before v."""
    tl = _CORR_TL
    T_ = tl.t[-1]
    ts = np.array(tl.t) / T_
    i = int(np.clip(np.searchsorted(ts, v, side="right") - 1, 0, len(ts) - 2))
    f = 0.0 if ts[i + 1] <= ts[i] else min(1.0, max(0.0, (v - ts[i]) / (ts[i + 1] - ts[i])))
    a, b = tl.states[i], tl.states[i + 1]
    out = {}
    for k, va in a.items():
        vb = b[k]
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)) and not isinstance(va, bool):
            out[k] = va + (vb - va) * f
        else:
            out[k] = vb if f >= 0.999 else va
    return out


# ----------------------------------------------------------------------------------------------- the overlay
# The measurement, drawn as E - E_corr against time with each phase marked, and the EIS as a Nyquist plot that builds as
# the frequency sweeps down. ILLUSTRATIVE: nobody has run a spot. The Nyquist arc is the Randles circuit DAL's video
# draws (render_cubxl_cu.py): R_u 60 ohm and R_p 48.8 kohm from its well simulation (C71500), with the simulation's
# assumed 30 uF/cm2 double layer on 0.0661 cm2. The OCP drift, the LPR step and the hold are drawn to the protocol's
# settings; their sizes in mV are the protocol's (±10 mV, +50 mV), the drift is made up.
PHASES = ((0.0, 20.0, "OCP"), (20.0, 30.0, "EIS at OCP"), (30.0, 32.0, "LPR"), (32.0, 37.0, "rest"),
          (37.0, 47.0, "+50 mV hold"), (47.0, 52.0, "OCP"))
RANDLES = dict(R_u=60.0, R_p=48.8e3, C=30e-6 * 0.0661)


def _e_rel(t):
    """E - E_corr in mV at t minutes (illustrative)."""
    if t < 20.0:
        return 24.0 * math.exp(-t / 4.0) + 0.6 * math.sin(t * 2.1)
    if t < 30.0:
        return 0.4 * math.sin(t * 9.0)
    if t < 32.0:
        return -10.0 + 10.0 * (t - 30.0)
    if t < 37.0:
        return 10.0 * math.exp(-(t - 32.0) / 0.8)
    if t < 47.0:
        return 50.0
    return 8.0 + 42.0 * math.exp(-(t - 47.0) / 0.9)


def _nyquist(n):
    f = np.array([1e5 * 10 ** (-k / 10) for k in range(71)])[:n]
    w = 2 * math.pi * f
    z = RANDLES["R_u"] + RANDLES["R_p"] / (1 + 1j * w * RANDLES["R_p"] * RANDLES["C"])
    return z.real / 1e3, -z.imag / 1e3, f


def _draw_corr_overlay(sc, img, s):
    from PIL import ImageDraw
    from scene import font
    v = _gv(sc, "cubxl_corrosion:clock")
    st = _corr_state(v)
    W, H = img.size
    d = ImageDraw.Draw(img, "RGBA")
    ft, fs, fm = font(13.5 * s, bold=True), font(12 * s), font(12 * s, mono=True)
    ink, mute, warn = (20, 20, 24, 255), (80, 84, 90, 255), (150, 40, 30, 255)
    measuring = 0.0005 < st["meas"] < 0.9999 or (st["meas"] >= 0.9999 and st["cap"] == "S1")
    if st["panel"] > 0.5 and not measuring:
        # the liquid panel: what the P20 holds and where the liquid is, in µL, to scale
        x0, y0 = W - 330 * s, 46 * s
        rows = [("P20, 20 µL tips", ""),
                ("tip", f"{st['tip_ul']:5.1f} µL {st['liq']}" if st["tip_ul"] > 0.05 else "  0.0 µL"),
                ("well S1", f"{st['well']:5.1f} µL, {well_level(st['well'], st['capped'] > 0.5):.1f} mm deep"),
                ("tube 1", f"{st['tube']:5.1f} µL, {tube_level(st['tube']):4.1f} mm"),
                ("ASW vial", f"{st['asw']:.3f} mL")]
        if st["acid"] < CORR["stock_ml"] - 1e-6:
            rows.append(("acid vial", f"{st['acid']:.3f} mL"))
        h = (26 + 19 * len(rows) + (20 if st["xfer"] else 0)) * s
        d.rounded_rectangle((x0, y0, W - 10 * s, y0 + h), 6 * s, fill=(255, 255, 255, 232), outline=(150, 156, 164, 255))
        d.text((x0 + 10 * s, y0 + 6 * s), "The CubXL's own P20 (1-20 µL)", font=ft, fill=ink)
        for i, (k, val) in enumerate(rows[1:]):
            yy = y0 + (28 + 19 * i) * s
            d.text((x0 + 10 * s, yy), k, font=fs, fill=mute)
            d.text((x0 + 92 * s, yy), val, font=fm, fill=ink)
        if st["xfer"]:
            yy = y0 + (28 + 19 * (len(rows) - 1)) * s
            d.text((x0 + 10 * s, yy), st["xfer"] + ("  (sped up)" if st["lapse"] > 0.5 else ""), font=ft,
                   fill=(30, 60, 140, 255))
    if measuring:
        _draw_corr_measure(d, W, H, s, st["meas"])
    if st["end"] > 0.02:
        a = min(1.0, st["end"] * 4)
        x0, y0, x1 = W * 0.18, 70 * s, W * 0.82
        d.rounded_rectangle((x0, y0, x1, y0 + 250 * s), 8 * s, fill=(255, 255, 255, int(238 * a)),
                            outline=(150, 156, 164, int(255 * a)))
        al = int(255 * a)
        lines = [("One spot (DAL protocol.md section 4), about 67 min of deck time", True),
                 ("fill 150 µL (8 P20 transfers)  >  leak check  >  cap on", False),
                 ("OCP 20 min  >  EIS at OCP 10 min  >  LPR ±10 mV  >  rest 5 min", False),
                 ("+50 mV hold 10 min  >  OCP 5 min  >  cap off, rinsed", False),
                 ("well + DI rinse to its tube (16 transfers)  >  20 µL 1 M HNO3  >  image", False),
                 ("Each piece's second well: the same, OCP only (the companion)", False),
                 ("Selected spots only, last: fill to EIS, then cyclic polarization", True),
                 ("from 50 mV below OCP at 1 mV/s, reversing at 1 mA/cm2, back to E_corr; its own tube", False),
                 ("Nobody has run a spot yet: DAL's plan, PR #180 (aeda51a)", False)]
        for i, (t, b) in enumerate(lines):
            d.text((x0 + 16 * s, y0 + (14 + 25 * i) * s), t, font=ft if b else fs,
                   fill=(20, 20, 24, al) if i < 8 else (150, 40, 30, al))


def _draw_corr_measure(d, W, H, s, m):
    from scene import font
    ft, fs = font(13.5 * s, bold=True), font(11.5 * s)
    x0, y0, x1, y1 = W * 0.50, 46 * s, W - 10 * s, 46 * s + H * 0.50
    d.rounded_rectangle((x0, y0, x1, y1), 6 * s, fill=(255, 255, 255, 236), outline=(150, 156, 164, 255))
    t_now = 52.0 * m
    ph = next((p for p in PHASES if p[0] <= t_now < p[1]), PHASES[-1])
    d.text((x0 + 10 * s, y0 + 6 * s), f"S1, cap on: {ph[2]}, minute {t_now:4.1f} of 52", font=ft, fill=(20, 20, 24))
    d.text((x0 + 10 * s, y1 - 33 * s), "ILLUSTRATIVE, not measured: the protocol's steps and sizes; the drift and the",
           font=fs, fill=(150, 40, 30))
    d.text((x0 + 10 * s, y1 - 18 * s), "arc (DAL's Randles circuit, R_u 60 ohm, R_p 48.8 kohm) are drawn for the example.",
           font=fs, fill=(150, 40, 30))
    # E - E_corr against time, phases shaded
    ax0, ax1 = x0 + 50 * s, x0 + (x1 - x0) * 0.60
    py0, py1 = y0 + 44 * s, y1 - 62 * s
    lo, hi = -20.0, 60.0

    def ey(e):
        return py1 - (e - lo) / (hi - lo) * (py1 - py0)

    def tx(t):
        return ax0 + t / 52.0 * (ax1 - ax0)
    cols = {"OCP": (232, 236, 242), "EIS at OCP": (226, 238, 228), "LPR": (246, 236, 220), "rest": (238, 238, 238),
            "+50 mV hold": (248, 226, 222)}
    for a, b, name in PHASES:
        d.rectangle((tx(a), py0, tx(b), py1), fill=cols[name])
        if b - a >= 5:
            d.text((tx(a) + 2 * s, py0 + 2 * s), name.replace(" at OCP", ""), font=fs, fill=(80, 84, 90))
    for e in (-10, 0, 10, 50):
        d.line([(ax0, ey(e)), (ax1, ey(e))], fill=(205, 210, 216), width=1)
        d.text((x0 + 8 * s, ey(e) - 7 * s), f"{e:+d}", font=fs, fill=(80, 84, 90))
    d.text((x0 + 8 * s, py0 - 17 * s), "E - E_corr, mV", font=fs, fill=(80, 84, 90))
    d.rectangle((ax0, py0, ax1, py1), outline=(120, 124, 130))
    d.text((ax0, py1 + 3 * s), "0", font=fs, fill=(80, 84, 90))
    d.text((ax1 - 30 * s, py1 + 3 * s), "52 min", font=fs, fill=(80, 84, 90))
    ts = np.linspace(0.0, max(t_now, 0.01), max(2, int(240 * m)))
    d.line([(tx(t), ey(_e_rel(t))) for t in ts], fill=(30, 60, 140), width=max(1, int(round(2 * s))))
    r = 3.5 * s
    d.ellipse((tx(t_now) - r, ey(_e_rel(t_now)) - r, tx(t_now) + r, ey(_e_rel(t_now)) + r), fill=(20, 20, 24))
    # Nyquist, building through the EIS window (minutes 20-30), 100 kHz first
    bx0, bx1 = ax1 + 30 * s, x1 - 14 * s
    by1 = py1
    by0 = by1 - (bx1 - bx0)
    d.rectangle((bx0, by0, bx1, by1), outline=(120, 124, 130))
    d.text((bx0, by0 - 30 * s), "EIS at OCP, Nyquist", font=fs, fill=(80, 84, 90))
    d.text((bx0, by0 - 16 * s), "-Z'' against Z', 0-50 kohm", font=fs, fill=(80, 84, 90))
    frac = min(1.0, max(0.0, (t_now - 20.0) / 10.0))
    n = int(round(frac * 71))
    if n >= 2:
        zr, zi, f = _nyquist(n)
        k = (bx1 - bx0) / 50.0
        d.line([(bx0 + a * k, by1 - b * k) for a, b in zip(zr, zi)], fill=(30, 120, 60), width=max(1, int(round(2 * s))))
        if frac < 1.0:
            hz = f[-1]
            lab = f"{hz / 1e3:.0f} kHz" if hz >= 1e3 else f"{hz:.2g} Hz"
            d.text((bx0 + 4 * s, by1 - 16 * s), lab, font=fs, fill=(30, 120, 60))
    if t_now >= 37.0:
        q = min(10.0, t_now - 37.0) / 10.0
        d.text((ax0, py1 + 18 * s), f"hold: {q * 10:.0f} of 10 min; DAL expects 0.2-2.8 mC (cap 3 mC)", font=fs,
               fill=(80, 84, 90))


def _corr_parts(inst: Instrument):
    """Every deck item, the head's tools and the electrode cap, in the model's frame (CubOS -> _corr_w)."""
    p = CORR
    body = _piece(inst, "body")
    dz = p["deck_z"]
    face, lid = _cz(p["face"]), _cz(p["lid"])
    # ---- the coupon tray: four stations under printed lids, each with an O-ring well, RE and CE pads
    tx0, tx1, ty0, ty1 = _cx(p["tray"][0]), _cx(p["tray"][1]), _cy(p["tray"][2]), _cy(p["tray"][3])
    body.add("coupon tray", box(tx0, ty0, dz, tx1, ty1, face - 6), "lab_tray")
    sy = _cy(p["station_y"])
    lids = None
    for i, sx_ in enumerate(p["stations"]):
        x = _cx(sx_)
        name, mat = p["specimens"][i]
        spec = box(x - 10, sy - 10, face - 6, x + 10, sy + 10, face) if i < 3 else cyl(20, 6, x=x, y=sy, z=face - 6)
        body.add(f"S{i + 1} {name}", spec, mat)
        plate = box(x - 11.5, sy - 17, face, x + 11.5, sy + 17, face + 3.0).union(cyl(16, 6, x=x, y=sy, z=face))
        plate = plate.cut(cyl(7.3, 1.42, x=x, y=sy, z=face - 0.01)).cut(cyl(2 * p["a_spot"], 2, x=x, y=sy, z=face)) \
            .cut(cyl(2 * p["r_bore"], 10, x=x, y=sy, z=face + p["z_step"]))
        lids = plate if lids is None else lids.union(plate)
        body.add(f"S{i + 1} O-ring", tube(6.46, 2.9, 1.42, x=x, y=sy, z=face), "pp_black")
        for sgn in (-1, 1):
            body.add(f"pad S{i + 1} {sgn:+d}", box(x + sgn * 11 - 1.5, sy - 3, face + 3.0, x + sgn * 11 + 1.5, sy + 3,
                                                   face + 3.6), "brass")
    body.add("lids", lids, "lab_lid")
    body.add("bus connector", box(tx0 + 40, ty1, dz + 6, tx0 + 80, ty1 + 6, face - 6), "printer_black")
    # ---- Ben's 9-position holder (STEP) and its six vials, caps from Ben's VialCap16mm STEP
    hx = _cx(p["holder_x"])
    hy = [_cy(p["holder_y0"] + k * p["holder_dy"]) for k in range(9)]
    try:
        holder = cq.importers.importStep(str(CAPPER_CAD / "9VialHolder20mL_TightFit.step"))
        holder = holder.rotate((0, 0, 0), (0, 0, 1), 180).translate((hx, hy[0], dz))
    except Exception:                              # no STEP: its envelope (33.4 x 297.4 x 35 mm)
        holder = box(hx - 16.7, hy[0] - 16.7, dz, hx + 16.7, hy[-1] + 16.7, dz + p["holder_top"])
    body.add("9-vial holder", holder, "lab_petg_dark")
    try:
        vcap = cq.importers.importStep(str(CAPPER_CAD / "VialCap16mm.step"))
    except Exception:
        vcap = cyl(28, 18.5, z=-18.0)
    movable = {"1 M HNO3, trace metal": "vcap_acid", "ASW (D1141, no heavy metals)": "vcap_asw",
               "ASW + 10 mg/L S": "vcap_s10"}
    for name, k, mat in p["stocks"]:
        x, y = hx, hy[k]
        body.add(f"vial {name}", tube(27.5, 25.2, p["vial_rim"], x=x, y=y, z=dz).union(cyl(27.5, 1.5, x=x, y=y, z=dz)),
                 "glass")
        body.add(f"{name} liquid", cyl(25.0, 36.0, x=x, y=y, z=dz + 1.5), mat)
        tgt = _piece(inst, movable[name]) if name in movable else body
        tgt.add(f"{name} cap", vcap.translate((x, y, _cz(p["vial_cap"] - 0.5))), "pp_white")
        if k == 0:                # the spare seat's vial (FeSO4 nights only): a piece, so round 2's workflow can drop it
            spare = _piece(inst, "spare")
            for part in [pt for pt in body.parts if pt.name in (f"vial {name}", f"{name} liquid", f"{name} cap")]:
                body.parts.remove(part)
                spare.parts.append(part)
    # ---- the three cups (4 mL vials) on their block
    cy_ = _cy(p["cup_y"])
    body.add("cup block", box(_cx(16), cy_ - 12, dz, _cx(104), cy_ + 12, dz + 8), "lab_petg")
    for name, x_, mat in p["cups"]:
        x = _cx(x_)
        body.add(name, tube(15, 13.2, p["cup_rim"], x=x, y=cy_, z=dz).union(cyl(15, 1.5, x=x, y=cy_, z=dz)), "glass")
        body.add(f"{name} liquid", cyl(13.0, 40.0, x=x, y=cy_, z=dz + 1.5), mat)
    # ---- the tube rack, 2 x 8 open 0.5 mL tubes
    rx0, rx1, ry0, ry1 = (_cx(p["tube_rack"][0]), _cx(p["tube_rack"][1]), _cy(p["tube_rack"][2]),
                          _cy(p["tube_rack"][3]))
    xs = [p["tubes_x0"] + p["tubes_dx"] * k for k in range(8)]
    rack = box(rx0, ry0, dz, rx1, ry1, dz + 20)
    for x_ in xs:
        for y_ in p["tubes_y"]:
            rack = rack.cut(cyl(8.4, 25, x=_cx(x_), y=_cy(y_), z=dz + 1))
    body.add("tube rack", rack, "lab_petg")
    prof_out = [(0, 0), (1.3, 0), (3.6, 12.4), (3.85, 30.5), (4.6, 30.5), (4.6, p["tube_top"]), (0, p["tube_top"])]
    prof_in = [(0, _TUBE_IN[0][0])] + [(r, z) for z, r in _TUBE_IN] + [(0, _TUBE_IN[-1][0] + 1)]
    tshape = _revolve_rz(prof_out).cut(_revolve_rz(prof_in))
    tubes = [tshape.translate((_cx(x_), _cy(y_), dz + 1)).val() for x_ in xs for y_ in p["tubes_y"]]
    body.add("0.5 mL tubes", cq.Workplane().add(cq.Compound.makeCompound(tubes)), "lab_tube")
    # tube 1's liquid, modelled to the 320 uL level and scaled by its Level joint
    h320 = tube_level(320.0)
    liq = _revolve_rz([(0, _TUBE_IN[0][0])] + [(r - 0.05, z) for z, r in _TUBE_IN if z < h320] +
                      [(_tube_r(h320) - 0.05, h320), (0, h320)])
    _piece(inst, "tubeliq").add("tube 1 liquid", liq.translate((_cx(xs[0]), _cy(p["tubes_y"][0]), dz + 1)), "lab_well")
    # ---- tip racks: Ben's (rack 1) and DAL's printed rack 2, 2 x 15 tips each; the three tips the spot uses move
    tip = _revolve_rz([(0, 0), (0.45, 0), (2.6, 30), (2.9, 37), (3.3, p["tip_len"]), (0, p["tip_len"])])
    used = {}
    tips = []
    for rk, (ax, ay) in (("rack 1", p["rack1"]), ("rack 2", CORR["rack2_drawn"])):
        cols = (ax, ax - p["rack_pitch"])
        x0r, x1r = _cx(min(cols) - 5.75), _cx(max(cols) + 5.75)
        y0r, y1r = _cy(ay - 4.0), _cy(ay + (p["rack_rows"] - 1) * p["rack_pitch"] + 4.0)
        body.add(f"tip {rk}", box(x0r, y0r, dz, x1r, y1r, _cz(p["rack_top"])),
                 "lab_petg_dark" if rk == "rack 1" else "lab_petg")
        for r in range(p["rack_rows"]):
            for c, cx_ in enumerate(cols):
                at = (_cx(cx_), _cy(ay + r * p["rack_pitch"]), _cz(p["tip_top"] - p["tip_len"]))
                key = {("rack 1", 0, 0): "tip", ("rack 1", 0, 1): "tip2", ("rack 2", 0, 0): "tip3"}.get((rk, r, c))
                if key:
                    used[key] = (cx_, ay)
                    _piece(inst, key).add(f"{key} ({rk})", tip.translate(at), "lab_tip")
                    continue
                tips.append(tip.translate(at).val())
    body.add("tips", cq.Workplane().add(cq.Compound.makeCompound(tips)), "lab_tip")
    wx, wy = _cx(p["waste"][0]), _cy(p["waste"][1])
    body.add("tip waste", tube(p["waste_d"], p["waste_d"] - 3, p["waste_top"], x=wx, y=wy, z=dz)
             .union(cyl(p["waste_d"], 2, x=wx, y=wy, z=dz)), "printer_grey")
    return body, used, xs


def _revolve_rz(prof):
    """A solid of revolution about z from (r, z) points."""
    return cq.Workplane("XZ").polyline([(r, z) for r, z in prof]).close().revolve(360, (0, 0, 0), (0, 1, 0))


# where the three tips the spot uses sit in their racks, and where each liquid is modelled: (z0, h0, parent)
TIP_HOME = {"tip": CORR["rack1"], "tip2": (CORR["rack1"][0] - CORR["rack_pitch"], CORR["rack1"][1]),
            "tip3": CORR["rack2_drawn"]}
_ZR = _cz(CORR["travel_z"])
LEVEL_AT = {"tipliq": (_ZR - CORR["tip_hang"] + 0.15, None, "tools"),
            "wellliq": (_cz(CORR["face"]) + 0.02, 3.0, None),
            "tubeliq": (_cz(1.0) + _TUBE_IN[0][0], None, None)}


def corr_offsets(s: dict) -> dict:
    """{piece: (dx, dy, dz)} of everything that moves, for a timeline state: the gantry (y), the carriage (x), the
    tools (z, from travel height), the electrode cap, the three vial caps and the three tips, each from where it is
    modelled."""
    p = CORR
    out = {"gantry": (0.0, s["y"], 0.0), "carriage": (s["x"], 0.0, 0.0), "tools": (0.0, 0.0, s["z"] - p["travel_z"])}
    park = (p["cups"][2][1], p["cup_y"], p["cup_rim"])
    if s["cap"] == "head":       # the cap's skirt underside: the magnet face, less the cap's height
        at = (s["x"], s["y"], s["z"] - p["magnet"] - p["cap_h"])
    elif s["cap"] == "S1":
        at = (p["stations"][0], p["station_y"], p["lid"])
    else:
        at = park
    out["cap"] = tuple(a - b for a, b in zip(at, park))
    for name, k in (("asw", 2), ("s10", 3), ("acid", 1)):     # a vial cap on the magnet: its top at the magnet face
        hx, hy = p["holder_x"], p["holder_y0"] + k * p["holder_dy"]
        out[f"vcap_{name}"] = ((s["x"] - hx, s["y"] - hy, s["z"] - p["magnet"] - p["vial_cap"])
                               if s["vcap"] == name else (0.0, 0.0, 0.0))
    jitter = {"tip": (-5.0, -4.0), "tip2": (5.0, 3.0), "tip3": (0.0, 5.0)}
    for key, home in TIP_HOME.items():
        if s[key] == "head":         # its top 4 mm above the nozzle, its end 35 mm below
            at = (s["x"] + p["pip"][0], s["y"] + p["pip"][1], s["z"] + 4.0 - p["tip_len"])
        elif s[key] == "waste":      # lying in the waste, side by side (collide.py found two in one spot before)
            at = (p["waste"][0] + jitter[key][0], p["waste"][1] + jitter[key][1], 2.0)
        else:
            at = (home[0], home[1], p["tip_top"] - p["tip_len"])
        out[key] = (at[0] - home[0], at[1] - home[1], at[2] - (p["tip_top"] - p["tip_len"]))
    return out


def corr_levels(s: dict) -> dict:
    """Liquid heights, mm, for a timeline state: in the tip on the P20, in well S1, in tube 1 (above its floor)."""
    return {"tipliq": tip_level(s["tip_ul"]), "wellliq": well_level(s["well"], s["capped"] > 0.5),
            "tubeliq": max(0.0, tube_level(s["tube"]) - _TUBE_IN[0][0])}


LEVEL_AT["tipliq"] = (LEVEL_AT["tipliq"][0], tip_level(20.0), "tools")
LEVEL_AT["tubeliq"] = (LEVEL_AT["tubeliq"][0], tube_level(320.0) - _TUBE_IN[0][0], None)


def cubxl_corrosion() -> Instrument:
    import equipment
    p = CORR
    W, D = equipment.CUBXL["W"], equipment.CUBXL["D"]
    inst = Instrument(
        "cubxl_corrosion", "Copper corrosion spots on the CubXL", "CubXL + NuVant EZstat Pro",
        (W + 70 + 30 + p["ez"][0], D, equipment.CUBXL["H"] + 50),
        "The CubXL from lab_models.equipment.cubxl() (#199); the deck, the head and one spot as digital-alloy-lab PR "
        "#180 lays them out for copper (alloy-corrosion/copper/deck_cu.py, protocol.md, render_cubxl_cu.py at aeda51a); "
        "Ben's capper mount, 9-vial holder and vial cap STEPs (modules/electromagnetic-capper/cad); NuVant's EZstat Pro "
        "(255 x 245 x 102 mm, nuvant.com) beside it, as in byu-vcl #231 / DAL #221",
        props=("cap", "vcap_asw", "vcap_s10", "vcap_acid", "tip", "tip2", "tip3", "tipliq", "wellliq", "tubeliq", "led",
               "clock"))
    cub = equipment.cubxl(0.05, 0.0, 0.5)          # carriage at CubOS x 0, gantry at y 0
    gantry_names = ("gantry upright L", "gantry upright R", "gantry beam", "cable chain")
    carriage_names = ("z carriage", "tool plate", "controller")
    dropped = ("pipette", "capper", "vial rack", "tip rack") + tuple(f"vial {i}" for i in range(1, 7)) + \
        tuple(f"vial {i} cap" for i in range(1, 7))
    body, gantry, carriage = _piece(inst, "body"), _piece(inst, "gantry"), _piece(inst, "carriage")
    for part in cub.parts:
        if part.name in dropped:
            continue
        target = gantry if part.name in gantry_names else carriage if part.name in carriage_names else body
        target.parts.append(part)
    body, used, xs = _corr_parts(inst)
    dz = p["deck_z"]
    # ---- the potentiostat beside the frame, and its cell cable to the tray's back edge
    ew, ed, eh = p["ez"]
    ex = p["ez_x"]
    tx0, ty1 = _cx(p["tray"][0]), _cy(p["tray"][3])
    body.add("EZstat Pro", rbox(ew, ed, eh - 8, 6, x=ex, y=60, z=8), "paint_grey")
    body.add("EZstat front", box(ex - ew / 2 + 6, 60 - ed / 2 - 1, 14, ex + ew / 2 - 6, 60 - ed / 2, eh - 6), "inst_dark")
    for sxx in (-1, 1):
        for syy in (-1, 1):
            body.add(f"EZstat foot {sxx}{syy}", cyl(14, 8, x=ex + sxx * (ew / 2 - 25), y=60 + syy * (ed / 2 - 25)),
                     "pp_black")
    body.add("cell connector", _xcyl(16, 12, x=ex - ew / 2 - 12, y=110, z=50), "steel")
    body.add("cell cable", hose([(ex - ew / 2 - 12, 110, 50), (ex - ew / 2 - 40, 200, 45), (360, 268, 70),
                                 (300, 268, 70), (200, 150, 92), (tx0 + 60, ty1 + 25, dz + 6),
                                 (tx0 + 60, ty1 + 6, dz + 10)], 6), "lab_cable")
    _piece(inst, "led").add("cell-on LED", _ycyl(7, 3, x=ex + ew / 2 - 30, y=60 - ed / 2 - 3, z=eh - 25), "glow")
    # ---- the head, at CubOS x 0, y 0, carriage at travel height: Ben's PAW-V2 mount and magnet, the P20, the camera
    tools = _piece(inst, "tools")
    zr = _cz(p["travel_z"])                      # the carriage's reference: the bare P20 nozzle's end
    hx0, hy0 = _cx(0), _cy(0)
    try:
        mount = cq.importers.importStep(str(CAPPER_CAD / "PAW-V2-ElectromagnetMount.step"))
        mount = mount.rotate((0, 0, 0), (1, 0, 0), 180)
        zmin = mount.val().BoundingBox().zmin
        mount = mount.translate((hx0 - 63.17, hy0 + 6.53, zr - p["magnet"] - zmin))   # its bore axis on (0, 0)
    except Exception:
        mount = cyl(30, 43, x=hx0, y=hy0, z=zr - p["magnet"])
    tools.add("capper mount (PAW-V2)", mount, "lab_mount")
    tools.add("capper magnet", cyl(25, 20, x=hx0, y=hy0, z=zr - p["magnet"] + 0.5), "steel")
    tools.add("capper arm", box(hx0 - 8, hy0 + 10, zr, hx0 + 8, hy0 + 25, zr + 26), "lab_mount")
    px, py = hx0 + p["pip"][0], hy0 + p["pip"][1]
    tools.add("P20 shaft", cyl(8, 44, x=px, y=py, z=zr), "lab_pip_shaft")
    tools.add("P20 body", box(px - 17, py - 13, zr + 44, px + 17, py + 13, zr + 150), "lab_pip")
    tools.add("P20 top", box(px - 17, py - 13, zr + 150, px + 17, py + 13, zr + 162), "inst_grey")
    cxm, cym = hx0 + p["cam"][0], hy0 + p["cam"][1]
    tools.add("camera_3", box(cxm - 11, cym - 11, zr + 8, cxm + 11, cym + 11, zr + 34), "printer_black")
    tools.add("camera lens", cyl(10, 3, x=cxm, y=cym, z=zr + 5), "glass")
    tools.add("camera arm", box(cxm - 5, cym + 11, zr + 20, cxm + 5, hy0 + 25, zr + 34), "printer_black")
    # the liquid in whichever tip is on the P20: a cone up the tip's bore from its end, modelled 11.4 mm (20 uL) tall
    hang = p["tip_hang"]
    h20 = tip_level(20.0)
    tl_shape = cq.Workplane().add(cq.Solid.makeCone(0.3, 0.3 + 0.072 * h20, h20, cq.Vector(px, py, zr - hang + 0.15),
                                                    cq.Vector(0, 0, 1)))
    _piece(inst, "tipliq").add("liquid in the tip", tl_shape, "lab_well")
    # ---- the electrode cap, modelled on the park cup: 26 mm flange, 16 mm body, steel disc, the Ag/AgCl capillary in a
    # Pt coil 3 mm below the skirt, two pogo pins at +-11 mm
    cap = _piece(inst, "cap")
    kx, ky, kz = _cx(p["cups"][2][1]), _cy(p["cup_y"]), _cz(p["cup_rim"])
    cap.add("cap flange", cyl(p["cap_d"], 4.0, x=kx, y=ky, z=kz), "pla_white")
    cap.add("cap body", cyl(18, p["cap_h"] - 5.2, x=kx, y=ky, z=kz + 4.0), "pla_white")
    cap.add("steel disc", cyl(12, 1.2, x=kx, y=ky, z=kz + p["cap_h"] - 1.2), "steel")
    cap.add("Ag/AgCl reference", cyl(2, p["cap_h"] + p["cap_el"] - 1.5, x=kx, y=ky, z=kz - p["cap_el"]), "lab_agcl")
    coil = None
    for k in range(4):
        c = tube(5.2, 4.4, 0.45, x=kx, y=ky, z=kz - p["cap_el"] + 0.3 + k * 0.7)
        coil = c if coil is None else coil.union(c)
    cap.add("Pt coil", coil, "chrome")
    for sgn in (-1, 1):
        cap.add(f"pogo {sgn:+d}", cyl(1.4, 2.6, x=kx + sgn * 11, y=ky, z=kz - 2.4), "brass")
    # ---- the liquid in well S1, modelled 3 mm deep and scaled by its Level joint
    s1x, s1y = _cx(p["stations"][0]), _cy(p["station_y"])
    _piece(inst, "wellliq").add("liquid in S1", cyl(2 * p["r_bore"] - 0.1, 3.0, x=s1x, y=s1y, z=_cz(p["face"]) + 0.02),
                                "lab_well")

    # ---- the joints: one timeline for the head, what it carries, and the liquid levels
    tl = _CORR_TL
    off = [corr_offsets(st) for st in tl.states]
    lev = [corr_levels(st) for st in tl.states]

    def knots(key):
        return tuple((t / tl.t[-1], tuple(float(c) for c in o[key])) for t, o in zip(tl.t, off))

    def lknots(key):
        return tuple((t / tl.t[-1], float(lv[key])) for t, lv in zip(tl.t, lev))
    inst.joints = {
        "gantry": Track(knots=knots("gantry")),
        "carriage": Track(parent="gantry", knots=knots("carriage")),
        "tools": Track(parent="carriage", knots=knots("tools")),
        **{k: Track(knots=knots(k)) for k in ("cap", "vcap_asw", "vcap_s10", "vcap_acid", "tip", "tip2", "tip3")},
        **{k: Level(parent=LEVEL_AT[k][2], knots=lknots(k), z0=LEVEL_AT[k][0], h0=LEVEL_AT[k][1])
           for k in ("tipliq", "wellliq", "tubeliq")},
        "led": Joint("fade"),
        "clock": Track(knots=((0.0, (0.0, 0.0, 0.0)), (1.0, (1.0, 0.0, 0.0)))),
    }
    moving = [k for k in inst.joints if k != "led"]

    def seg(a, b, **extra):
        out = {k: (tl.v(a), tl.v(b)) for k in moving}
        out.update(extra)
        return out
    marks = [m for m, _ in _CORR_SEGS]
    inst.actions = []
    prev = None
    for i, (m, cap_txt) in enumerate(_CORR_SEGS):
        if prev is None:
            # the carriage's 220 x 290 mm tool plate (#199's model) stands behind the head: drawn see-through
            inst.actions.append((cap_txt, tl.t[tl.marks[m]] * PACE,
                                 seg("start", "start") | {"clock": (0.0, tl.v(m)), "~carriage": (0.0, 0.7)}))
        else:
            extra = {"led": (0.0, 1.0)} if m == "measured" else {"led": (1.0, 0.0)} if m == "parked" else {}
            secs = (tl.t[tl.marks[m]] - tl.t[tl.marks[prev]]) * PACE
            inst.actions.append((cap_txt, secs, seg(prev, m, **extra)))
        prev = m
    del marks
    hxw = _cx(p["holder_x"])
    inst.labels = [("electrode cap,\nparked", (kx, ky, kz + 18), (0.10, 0.30)),
                   ("S1-S4: Cu-Ni, NAB,\nDED pad, PTFE blank", (_cx(222), _cy(p["tray"][2]), _cz(p["lid"])), (0.10, 0.58)),
                   ("Ben's 9-vial holder:\nASW, sulfide, acid, DI", (hxw, _cy(130), _cz(60)), (0.62, 0.86)),
                   ("ICP-MS tubes", (_cx(220), _cy(37), _cz(32)), (0.36, 0.88)),
                   ("NuVant EZstat Pro", (ex - 40, 60 - ed / 2, eh), (0.88, 0.62))]
    inst.cam = (0.55, -1.5, 1.25)
    inst.framing = (0.80, 0.30)
    inst.notes = ["Deck, head and spot: DAL PR #180's copper plan (aeda51a), not yet built",
                  "P20 volumes and levels to scale; the measurement plot is illustrative"]
    return inst


# cameras (model frame), by action index. DAL's own run view (render_cubxl_cu.RUN_WIDE, CubOS (700, -520, 540) looking at
# (225, 150, 30)) for the deck; closer in for the fill and the cell.
_C_WIDE = (_corr_w(700.0, -560.0, 640.0), _corr_w(205.0, 150.0, 30.0))
_C_FILL = (_corr_w(540.0, -330.0, 430.0), _corr_w(250.0, 170.0, 30.0))
_C_CELL = (_corr_w(400.0, 360.0, 230.0), _corr_w(150.0, 225.0, 25.0))     # from behind, right: the parked head is in front
_C_WELL = (_corr_w(120.0, 60.0, 170.0), _corr_w(200.0, 235.0, 22.0))
_C_TUBE = (_corr_w(400.0, -340.0, 400.0), _corr_w(210.0, 100.0, 30.0))
_C_OVER = ((560.0, -1450.0, 1250.0), (60.0, 0.0, 180.0))
CAMS["instruments/cubxl_corrosion"] = {0: _C_WIDE, 2: _C_FILL, 3: _C_WELL, 4: _C_FILL, 5: _C_CELL, 6: _C_CELL,
                                       7: _C_FILL, 8: _C_TUBE, 10: _C_WIDE, 11: _C_OVER}
PLOTS["instruments/cubxl_corrosion"] = _draw_corr_overlay


# ===================================================================================================== packaging
# An automated packaging station for sending powders out: the jar into a nest, a label printed and wrapped on, the jar
# bagged and sealed, into a foam insert, the lid on, a shipping label printed and applied. Every piece is a real
# benchtop product at its published size:
#  - Primera AP380 wrap-around label applicator: 340 W x 508 D x 226 H mm, 9.07 kg; containers 15-170 mm across;
#    labels 19-210 mm wide; one press of the foot switch (primera.com, AP380 page). The bottle lies on its side in a
#    cradle of chrome rollers under a spring-loaded pressure arm; the label roll sits high at the back; grey control
#    box on the right end.
#  - Primera LX500c colour label printer: 264 W x 389 D x 180 H mm closed, 3.2 kg; print width 19-108 mm
#    (primera.com, LX500c page). Off-white body, smoked lid at the top rear, labels out of a slot low on the front.
#    The AP380 takes die-cut labels with the waste removed, on a roll: in practice the LX500c prints the batch's labels
#    and the roll is rewound onto the AP380. Primera sells no print-and-apply bundle.
#  - Zebra ZD621t, 4 in thermal-transfer desktop printer: 202 W x 267 D x 192 H mm, 2.5 kg; 104 mm print width at
#    203 dpi (Zebra spec sheet, via midcomdata.com). Standard 4 x 6 in shipping labels (Uline S-6802).
#  - Uline H-190 12 in tabletop impulse sealer: 17.8 x 3.3 x 7.4 in (452 x 84 x 188 mm), 4.2 kg; seals up to 8 mil
#    poly (uline.com). Light-blue hammertone.
#  - Nalgene 2104-0008 250 mL wide-mouth HDPE jar: 61 mm across, 131 mm tall, 43 mm cap (thermofisher.com).
#  - Uline S-23611 pick-and-pack foam shipper: 12 x 12 x 4 in inside, 324 x 311 x 108 mm outside, charcoal foam.
# The nest and the bag stand are printed fixtures drawn here; their sizes are layout choices.
PACK = dict(front=-254.0,
            ap=dict(W=340.0, D=508.0, H=226.0, x=-250.0), lx=dict(W=264.0, D=389.0, H=180.0, x=-610.0),
            zd=dict(W=202.0, D=267.0, H=192.0, x=900.0), seal=dict(W=452.0, D=84.0, H=188.0, x=150.0),
            box=dict(W=324.0, D=311.0, H=108.0, x=580.0), jar=dict(d=61.0, h=131.0, cap_d=52.0, cap_h=14.0),
            nest_x=-900.0, label=(102.0, 152.0))


def _qr(rng_seed=3, n=21):
    """A QR-like module grid for the drawing: three finder squares and seeded noise. Not a real, scannable code."""
    rng = np.random.default_rng(rng_seed)
    g = rng.random((n, n)) < 0.45
    for (r, c) in ((0, 0), (0, n - 7), (n - 7, 0)):
        g[r:r + 7, c:c + 7] = False
        g[r:r + 7, c] = True
        g[r:r + 7, c + 6] = True
        g[r, c:c + 7] = True
        g[r + 6, c:c + 7] = True
        g[r + 2:r + 5, c + 2:c + 5] = True
    return g


_QR = _qr()


def _draw_packaging_insets(sc, img, s):
    from PIL import ImageDraw
    from scene import font
    key = "packaging:"
    aj, asl = min(1.0, _gv(sc, key + "inset_jar")), min(1.0, _gv(sc, key + "inset_ship"))
    W, H = img.size
    d = ImageDraw.Draw(img, "RGBA")
    fb, fs, fm = font(13 * s, bold=True), font(11.5 * s), font(12 * s, mono=True)
    if aj > 0.02:
        al = int(255 * aj)
        x0, y0 = W * 0.60, 46 * s
        x1, y1 = W - 10 * s, y0 + 150 * s
        d.rounded_rectangle((x0, y0, x1, y1), 6 * s, fill=(255, 255, 255, int(240 * aj)), outline=(120, 124, 130, al))
        d.text((x0 + 10 * s, y0 + 6 * s), "The jar label, from the LX500c (an example layout)", font=fb,
               fill=(20, 20, 24, al))
        q = 4.2 * s
        qx, qy = x0 + 12 * s, y0 + 30 * s
        for r in range(_QR.shape[0]):
            for c in range(_QR.shape[1]):
                if _QR[r, c]:
                    d.rectangle((qx + c * q, qy + r * q, qx + (c + 1) * q - 1, qy + (r + 1) * q - 1),
                                fill=(10, 10, 12, al))
        tx = qx + _QR.shape[1] * q + 14 * s
        for i, line in enumerate(["SAMPLE ID  <run ID>-P01", "AlSi10Mg, 15-45 um", "net 212.4 g", "2026-11-03",
                                  "BYU Vertical Cloud Lab"]):
            d.text((tx, qy + i * 17 * s), line, font=fm, fill=(20, 20, 24, al))
        d.text((x0 + 10 * s, y1 - 18 * s), "QR: a placeholder pattern, not a real code. Values are examples.",
               font=fs, fill=(150, 40, 30, al))
    if asl > 0.02:
        al = int(255 * asl)
        x0, y0 = W * 0.50, 46 * s
        x1, y1 = W - 10 * s, y0 + 300 * s
        d.rounded_rectangle((x0, y0, x1, y1), 6 * s, fill=(255, 255, 255, int(242 * asl)), outline=(120, 124, 130, al))
        d.text((x0 + 10 * s, y0 + 6 * s), "What the 4 x 6 in label and the papers must carry", font=fb,
               fill=(20, 20, 24, al))
        lw = 150 * s
        lx0, ly0 = x0 + 12 * s, y0 + 30 * s
        d.rectangle((lx0, ly0, lx0 + lw, ly0 + lw * 1.5), fill=(255, 255, 255, al), outline=(20, 20, 24, al), width=2)
        for i, line in enumerate(["FROM", "BYU Vertical Cloud Lab", "Provo, UT, USA", "", "TO", "<consignee>",
                                  "<address>"]):
            d.text((lx0 + 8 * s, ly0 + 6 * s + i * 14 * s), line, font=fb if line in ("FROM", "TO") else fs,
                   fill=(20, 20, 24, al))
        rng = np.random.default_rng(11)
        bx = lx0 + 10 * s
        while bx < lx0 + lw - 12 * s:
            w_ = (1 + int(rng.integers(0, 3))) * s
            d.rectangle((bx, ly0 + lw * 1.5 - 70 * s, bx + w_, ly0 + lw * 1.5 - 22 * s), fill=(10, 10, 12, al))
            bx += w_ + (1 + int(rng.integers(0, 3))) * s
        d.text((lx0 + 8 * s, ly0 + lw * 1.5 - 18 * s), "carrier's barcode", font=fs, fill=(90, 94, 100, al))
        rx = lx0 + lw + 14 * s
        rows = [("b", "Tested, not dangerous goods"),
                ("", "(MSE Supplies confirmed our AlSi10Mg"),
                ("", " shipment to Amazemet non-hazardous"),
                ("", " per IATA): no DG marks or labels;"),
                ("", " 'Not Restricted' on the air waybill."),
                ("", ""),
                ("b", "Untested aluminium powder, coated:"),
                ("", "UN1309, Aluminium powder, coated;"),
                ("", "the Class 4.1 FLAMMABLE SOLID label;"),
                ("", "shipper and consignee addresses."),
                ("", "Uncoated: UN1396, Class 4.3."),
                ("", "USPS takes no flammable solid abroad."),
                ("", ""),
                ("b", "Bronze, copper, steel: no UN entry;"),
                ("", "regulated only if a UN test says so.")]
        for i, (st, line) in enumerate(rows):
            d.text((rx, ly0 + i * 15.5 * s), line, font=fb if st else fs, fill=(20, 20, 24, al))
        d.text((x0 + 10 * s, y1 - 18 * s), "Sources: 49 CFR 172.101, 173.124-125; IATA DGR 8.2.6; USPS Pub. 52 344.2; "
               "DAL alloy-workflow-review.md", font=font(10 * s), fill=(90, 94, 100, al))


def _pack_labels() -> dict:
    """The leader labels for each part of the clip (the camera moves, so each view gets its own)."""
    P = PACK
    yf = P["front"]
    a, se, b = P["ap"], P["seal"], P["box"]
    L_lx = ("Primera LX500c\ncolour label printer", (P["lx"]["x"] - 60, yf, 150), (0.08, 0.22))
    L_ap = ("Primera AP380\nwrap-around applicator", (a["x"] - 60, yf + a["D"] - 110, a["H"] - 25), (0.30, 0.13))
    L_nest = ("jar nest", (P["nest_x"], yf + 80, 25), (0.06, 0.62))
    L_se = ("Uline H-190\nimpulse sealer", (se["x"] - 150, yf, 100), (0.10, 0.60))
    L_bag = ("liner bag", (se["x"] - 42, yf - 122, 120), (0.30, 0.80))
    L_box = ("foam shipper", (b["x"] - b["W"] / 2, yf, 60), (0.12, 0.70))
    L_zd = ("Zebra ZD621t", (P["zd"]["x"] + 60, yf, 160), (0.90, 0.75))
    return {0: [L_lx, L_ap, L_nest], 4: [L_se, L_bag], 6: [L_box, L_zd], 9: [L_lx, L_ap, L_se, L_box, L_zd]}


def packaging() -> Instrument:
    P = PACK
    yf = P["front"]
    inst = Instrument(
        "packaging", "Automated packaging station for powders", "Primera AP380 + LX500c, Zebra ZD621t, Uline H-190",
        (2000.0, 508.0, 226.0),
        "Primera AP380 (340 x 508 x 226 mm) and LX500c (264 x 389 x 180 mm) pages; Zebra ZD621 spec sheet (ZD621t "
        "202 x 267 x 192 mm); Uline H-190 (452 x 84 x 188 mm), S-23611 foam shipper, S-6802 4 x 6 in labels; "
        "Nalgene 2104-0008 250 mL jar (61 x 131 mm). Looks from the makers' photos; fixtures drawn here",
        props=("jarpos", "jartilt", "jar", "jarlabel", "bag", "inset_jar", "inset_ship"))
    body = _piece(inst, "body")
    # ---- AP380: black side plates on splayed feet, a cradle of chrome rollers, a pressure arm, the label roll at the
    # back, the grey control box on the right end
    a = P["ap"]
    ax, ay = a["x"], yf + a["D"] / 2
    for sx in (-1, 1):
        x = ax + sx * (a["W"] / 2 - 60)
        body.add(f"AP380 side plate {sx:+d}", box(x - 5, yf + 20, 25, x + 5, yf + a["D"] - 20, 205), "inst_black")
        for sy in (-1, 1):
            body.add(f"AP380 foot {sx:+d}{sy:+d}", box(x - 18 + sx * 12, ay + sy * (a["D"] / 2 - 30) - 15, 0,
                                                        x + 18 + sx * 12, ay + sy * (a["D"] / 2 - 30) + 15, 25),
                     "inst_black")
    body.add("AP380 base", box(ax - a["W"] / 2 + 55, yf + 30, 25, ax + a["W"] / 2 - 55, yf + a["D"] - 30, 45),
             "inst_black")
    cy0 = yf + 150                                       # the cradle's centre line, along x
    for sy in (-1, 1):
        body.add(f"AP380 roller {sy:+d}", _xcyl(25, a["W"] - 140, x=ax - (a["W"] - 140) / 2, y=cy0 + sy * 30, z=95),
                 "chrome")
    body.add("AP380 control box", box(ax + a["W"] / 2 - 60, yf + 40, 45, ax + a["W"] / 2, yf + 260, a["H"] - 20),
             "inst_grey")
    for i in range(4):
        body.add(f"AP380 button {i}", _ycyl(10, 3, x=ax + a["W"] / 2 - 30, y=yf + 40, z=80 + 22 * i), "inst_white")
    body.add("AP380 counter", box(ax + a["W"] / 2 - 50, yf + 37, 175, ax + a["W"] / 2 - 10, yf + 40, 195), "inst_red")
    ry, rz = yf + a["D"] - 110, a["H"] - 85
    body.add("AP380 roll", _xcyl(160, 110, x=ax - 55, y=ry, z=rz).cut(_xcyl(76, 120, x=ax - 60, y=ry, z=rz)),
             "lab_label")
    for sx in (-1, 1):
        body.add(f"AP380 roll guide {sx:+d}", _xcyl(175, 4, x=ax + sx * 59 - 2, y=ry, z=rz), "inst_black")
    body.add("AP380 spindle", _xcyl(20, a["W"] - 140, x=ax - (a["W"] - 140) / 2, y=ry, z=rz), "chrome")
    body.add("foot switch", box(ax - 60, yf - 160, 0, ax + 30, yf - 60, 35), "inst_dark")
    press = _piece(inst, "press")
    pz = 200.0
    press.add("pressure arm", box(ax - 15, cy0 + 10, pz - 8, ax + 15, yf + a["D"] - 200, pz + 8), "inst_black")
    press.add("pressure roller", _xcyl(26, 70, x=ax - 35, y=cy0 + 10, z=pz - 10), "pp_black")
    # ---- LX500c
    l_ = P["lx"]
    lx_, ly_ = l_["x"], yf + l_["D"] / 2
    body.add("LX500c body", rbox(l_["W"], l_["D"], l_["H"] - 30, 10, x=lx_, y=ly_), "inst_offwhite")
    body.add("LX500c lid", box(lx_ - l_["W"] / 2 + 12, ly_ - 20, l_["H"] - 30, lx_ + l_["W"] / 2 - 12,
                               ly_ + l_["D"] / 2 - 10, l_["H"]), "lab_smoked")
    body.add("LX500c panel", box(lx_ - l_["W"] / 2 + 30, yf + 30, l_["H"] - 30, lx_ + l_["W"] / 2 - 30, yf + 80,
                                 l_["H"] - 26), "inst_light")
    for i in range(3):
        body.add(f"LX500c button {i}", cyl(10, 3, x=lx_ - 40 + 40 * i, y=yf + 55, z=l_["H"] - 26), "inst_dark")
    body.add("LX500c slot", box(lx_ - 60, yf - 1, 22, lx_ + 60, yf + 3, 30), "inst_black")
    _piece(inst, "stripslide")                          # an empty parent: the printed strip's slide
    _piece(inst, "strip").add("printed label", box(lx_ - 50, yf + 5, 25, lx_ + 50, yf + 70, 25.6), "lab_label")
    # ---- Zebra ZD621t
    zd = P["zd"]
    zx, zy = zd["x"], yf + zd["D"] / 2
    body.add("ZD621 base", rbox(zd["W"], zd["D"], 80, 14, x=zx, y=zy), "inst_dark")
    body.add("ZD621 top", rbox(zd["W"] - 6, zd["D"] - 10, zd["H"] - 80, 30, x=zx, y=zy + 4, z=80), "inst_light")
    body.add("ZD621 screen", box(zx - zd["W"] / 2 + 20, yf - 1, 95, zx - 10, yf + 2, 140), "screen_on")
    body.add("ZD621 latch", box(zx + zd["W"] / 2 - 2, zy - 30, 70, zx + zd["W"] / 2 + 3, zy + 30, 85), "inst_yellow")
    body.add("ZD621 exit", box(zx - 55, yf - 1, 66, zx + 55, yf + 2, 72), "inst_black")
    # ---- Uline H-190 impulse sealer, and the bag stand in front of it
    se = P["seal"]
    sx_, sy_ = se["x"], yf + se["D"] / 2
    body.add("H-190 base", box(sx_ - se["W"] / 2, yf, 0, sx_ + se["W"] / 2, yf + se["D"], 120), "lab_lightblue")
    body.add("H-190 jaw", box(sx_ - se["W"] / 2 + 70, yf + 8, 120, sx_ + se["W"] / 2 - 30, yf + 30, 126), "lab_ptfe")
    body.add("H-190 dial", _xcyl(34, 10, x=sx_ + se["W"] / 2, y=sy_ - 5, z=70), "inst_black")
    body.add("H-190 lamp", _xcyl(10, 6, x=sx_ + se["W"] / 2, y=sy_ - 5, z=100), "inst_red")
    arm = _piece(inst, "arm")
    arm.add("H-190 arm", box(sx_ - se["W"] / 2 + 60, yf + 4, 126, sx_ + se["W"] / 2 - 20, yf + se["D"], 168),
            "lab_lightblue")
    arm.add("H-190 upper jaw", box(sx_ - se["W"] / 2 + 70, yf + 8, 125, sx_ + se["W"] / 2 - 30, yf + 30, 127),
            "pp_black")
    arm.add("H-190 knob", box(sx_ + se["W"] / 2 - 60, yf - 30, 150, sx_ + se["W"] / 2 - 30, yf + 10, 175), "inst_black")
    body.add("bag stand", box(sx_ - 60, yf - 140, 0, sx_ + 60, yf - 20, 4), "pla_white")
    # ---- the foam shipper: kraft box, charcoal foam with a pocket for the jar lying down, the lid hinged at the back
    b = P["box"]
    bx_, by_ = b["x"], yf + b["D"] / 2
    shell = box(bx_ - b["W"] / 2, yf, 0, bx_ + b["W"] / 2, yf + b["D"], b["H"] - 40).cut(
        box(bx_ - b["W"] / 2 + 5, yf + 5, 5, bx_ + b["W"] / 2 - 5, yf + b["D"] - 5, b["H"]))
    body.add("box", shell, "lab_kraft")
    # the pocket, plucked from the pick-and-pack foam: 190 x 108 mm, room for the bagged jar lying down with its sealed
    # mouth flat; the lid's foam has the same cut-out, 8 mm deep, over the bag's top
    pocket_cut = box(bx_ - 95, by_ - 54, 12, bx_ + 95, by_ + 54, b["H"] - 27)
    foam = box(bx_ - b["W"] / 2 + 5, yf + 5, 5, bx_ + b["W"] / 2 - 5, yf + b["D"] - 5, b["H"] - 40).cut(pocket_cut)
    body.add("foam insert", foam, "lab_foam")
    lid = _piece(inst, "lid")
    lid.add("box lid", box(bx_ - b["W"] / 2, yf, b["H"] - 5, bx_ + b["W"] / 2, yf + b["D"], b["H"]), "lab_kraft")
    lid.add("lid sides", box(bx_ - b["W"] / 2, yf, b["H"] - 40, bx_ + b["W"] / 2, yf + b["D"], b["H"] - 5).cut(
        box(bx_ - b["W"] / 2 + 5, yf + 5, b["H"] - 41, bx_ + b["W"] / 2 - 5, yf + b["D"] - 5, b["H"] - 4)), "lab_kraft")
    lid.add("lid foam", box(bx_ - b["W"] / 2 + 6, yf + 6, b["H"] - 35, bx_ + b["W"] / 2 - 6, yf + b["D"] - 6,
                            b["H"] - 5).cut(pocket_cut), "lab_foam")
    # ---- the jar nest, with the next jar waiting in its left seat
    nx = P["nest_x"]
    body.add("jar nest", box(nx - 85, yf + 80, 0, nx + 85, yf + 200, 30).cut(
        cyl(64, 30, x=nx - 40, y=yf + 140, z=10)).cut(cyl(64, 30, x=nx + 40, y=yf + 140, z=10)), "pla_white")
    j = P["jar"]
    jx, jy, jz = nx + 40, yf + 140, 10.0                  # the jar is modelled standing in the nest's right seat
    body.add("next jar", cyl(j["d"], j["h"] - j["cap_h"], x=nx - 40, y=jy, z=jz), "lab_hdpe")
    body.add("next jar cap", cyl(j["cap_d"], j["cap_h"], x=nx - 40, y=jy, z=jz + j["h"] - j["cap_h"]), "pla_white")
    body.add("next jar powder", cyl(j["d"] - 4, 70, x=nx - 40, y=jy, z=jz + 3), "powder")
    _piece(inst, "jarpos")
    _piece(inst, "jartilt")
    jar = _piece(inst, "jar")
    jar.add("jar", cyl(j["d"], j["h"] - j["cap_h"], x=jx, y=jy, z=jz).cut(
        cyl(j["d"] - 4, j["h"], x=jx, y=jy, z=jz + 2)), "lab_hdpe")
    jar.add("jar cap", cyl(j["cap_d"], j["cap_h"], x=jx, y=jy, z=jz + j["h"] - j["cap_h"]), "pla_white")
    jar.add("powder", cyl(j["d"] - 4.5, 70, x=jx, y=jy, z=jz + 2.5), "powder")
    lab = _piece(inst, "jarlabel")
    lab.add("jar label", tube(j["d"] + 1.2, j["d"] - 0.5, 60, x=jx, y=jy, z=jz + 25), "lab_label")
    lab.add("QR patch", box(jx - 9, jy - j["d"] / 2 - 0.9, jz + 45, jx + 9, jy - j["d"] / 2 + 2, jz + 63), "inst_black")
    # the liner bag as film: a 0.5 mm sleeve close round the jar (66 mm, over the 62 mm label), the jar standing on its
    # 0.6 mm bottom, and its mouth flattened to a 100 mm strip (half the sleeve's girth) for the seal. Drawn as a rigid
    # 84 mm box, it went 2.5-6 mm into the foam pocket, the lid's foam, the box's floor and the bag stand
    bag = _piece(inst, "bag")
    bag_d, bag_up, mouth_w = 66.0, 20.0, 100.0
    bag.add("liner bag", tube(bag_d, bag_d - 1.0, j["h"] + bag_up + 0.6, x=jx, y=jy, z=jz - 0.6).union(
        cyl(bag_d, 0.6, x=jx, y=jy, z=jz - 0.6)), "lab_bag")
    bag.add("bag mouth", box(jx - mouth_w / 2, jy - 3, jz + j["h"] + bag_up, jx + mouth_w / 2, jy + 3,
                             jz + j["h"] + bag_up + 22), "lab_bag")
    # the bag's open neck, laid back over the H-190's front and across its jaw for the seal: drawn where it lies with
    # the jar on the bag stand (bag_at, below), then carried into the jar's frame; shown only at the sealer
    bag_at = (sx_, yf - 80, 4.6)                           # the jar in its bag on the bag stand, in front of the sealer
    top = bag_at[2] + j["h"] + bag_up + 22                 # the top of the bag's mouth there
    neck = None
    for p0, p1 in (((bag_at[1], top), (yf - 4, 128.0)), ((yf - 4, 128.0), (yf + 36, 127.0))):
        d = np.subtract(p1, p0) / np.linalg.norm(np.subtract(p1, p0))
        n = np.array([-d[1], d[0]]) * 1.5
        quad = [tuple(p0), tuple(p1), tuple(np.add(p1, n)), tuple(np.add(p0, n))]
        s = cq.Workplane("YZ").polyline(quad).close().extrude(mouth_w).translate((bag_at[0] - mouth_w / 2, 0, 0))
        neck = s if neck is None else neck.union(s)
    _piece(inst, "neck").add("bag neck", neck.translate((jx - bag_at[0], jy - bag_at[1], jz - bag_at[2])), "lab_bag")
    lw, ll = P["label"]
    ship = _piece(inst, "shiplabel")
    ship.add("4 x 6 label", box(bx_ - lw / 2, by_ - ll / 2, b["H"], bx_ + lw / 2, by_ + ll / 2, b["H"] + 0.6),
             "lab_label")
    ship.add("label barcode", box(bx_ - 35, by_ - 60, b["H"] + 0.6, bx_ + 35, by_ - 30, b["H"] + 0.9), "inst_black")
    ship.add("label text", box(bx_ - 40, by_ + 10, b["H"] + 0.6, bx_ + 20, by_ + 60, b["H"] + 0.8), "inst_grey")

    # ---- choreography on one timeline
    mid = jz + j["h"] / 2                                  # the jar's tilt pivot: the middle of its axis
    # the jar's axis, lying in the AP380's cradle: on both rollers (30 mm either side of it), the label just touching
    ap_c = (ax, cy0, 95 + math.sqrt((12.5 + j["d"] / 2 + 0.6) ** 2 - 30.0 ** 2) + 0.1)
    # the pressure arm, hinged at the back: down, its roller rests on the jar's label (0.3 mm off); up, 50 deg, its
    # roller is clear of the jar as it comes down into the cradle and goes out again (raised only 14 deg, the roller
    # and the arm's end were in the jar's way, 3.6 mm: interference.py)
    press_pivot, press_up = (ax, yf + a["D"] - 200, pz), -50.0
    r_dy, r_dz = (cy0 + 10) - press_pivot[1], (pz - 10) - pz       # the pressure roller's axis from the hinge

    def roller_gap(deg):
        t = math.radians(deg)
        y_, z_ = r_dy * math.cos(t) - r_dz * math.sin(t), r_dy * math.sin(t) + r_dz * math.cos(t)
        return math.hypot(press_pivot[1] + y_ - cy0, pz + z_ - ap_c[2]) - (13.0 + j["d"] / 2 + 0.6) - 0.3
    lo_, hi_ = -20.0, 40.0
    for _ in range(50):                                            # the angle at which the roller meets the label
        lo_, hi_ = ((lo_ + hi_) / 2, hi_) if roller_gap((lo_ + hi_) / 2) > 0 else (lo_, (lo_ + hi_) / 2)
    press_down = lo_
    # the jar's axis, lying in the foam pocket: set left so the jar and its bag's sealed mouth (174 mm) fit the 190,
    # the bag 0.6 mm over the pocket's floor
    pocket = (bx_ - 24.5, by_, 12 + 0.6 + bag_d / 2)
    # press: the AP380's pressure arm, arm: the H-190's (1 up, 0 down); they ride the timeline, so each is up before
    # the jar comes in or goes out under it
    tl = Timeline(dict(p=(jx - 260, jy - 80, jz + 220), tilt=0.0, spin=0.0, ship=0.0, press=1.0, arm=1.0))

    def to(secs, x, y, z, **kw):
        tl.go(secs, p=(x, y, z), **kw)
    lie = lambda c: c[2] - (mid - jz)                      # noqa: E731  the jar's base z when its axis is at c lying
    # in over the next jar, clear of its cap (lower, it went through it: collide.py), then down into the seat
    to(1.0, jx, jy, jz + j["h"] + 30); to(0.6, jx, jy, jz); tl.mark("nested")
    to(0.5, jx, jy, jz + 160); to(1.0, ap_c[0], ap_c[1], lie(ap_c) + 160, tilt=90.0)
    to(0.6, ap_c[0], ap_c[1], lie(ap_c)); tl.go(0.4, press=0.0); tl.mark("in AP380")
    tl.go(2.0, spin=360.0); tl.mark("labelled")
    # out once the pressure arm is up; forward, clear of the H-190's raised arm; along its front; down on the stand
    tl.go(0.4, press=1.0); to(0.5, ap_c[0], ap_c[1], lie(ap_c) + 160); to(0.5, ap_c[0], bag_at[1], lie(ap_c) + 160)
    to(0.9, bag_at[0], bag_at[1], bag_at[2] + 160, tilt=0.0)
    to(0.6, *bag_at); tl.mark("at sealer")
    tl.go(0.5); tl.go(0.5, arm=0.0); tl.go(0.8); tl.mark("sealed")
    # arm up, the neck drawn forward out of the jaw, then up, over the sealer and down into the foam
    tl.go(0.5, arm=1.0); to(0.4, bag_at[0], bag_at[1] - 60, bag_at[2] + 4)
    # turned a quarter on its axis as it goes over, so that the bag's flat seal lies flat in the pocket
    to(0.5, bag_at[0], bag_at[1] - 60, bag_at[2] + 300)
    to(1.0, pocket[0], pocket[1], lie(pocket) + 260, tilt=90.0, spin=450.0)
    to(0.7, pocket[0], pocket[1], lie(pocket)); tl.mark("boxed")
    tl.go(1.0); tl.mark("lid on")
    tl.go(0.8, ship=1.0); tl.go(0.9, ship=2.0); tl.go(0.6, ship=3.0); tl.mark("shipped")
    # the label's track: inside the ZD621, out of its front, over the lid, onto it
    ship_pts = [(zx - bx_, (yf + 80) - by_, 69 - b["H"]), (zx - bx_, (yf - 70) - by_, 69 - b["H"]),
                (0.0, 0.0, 140.0), (0.0, 0.0, 0.0)]

    def ship_off(st):
        k = st["ship"]
        i = min(int(k), 2)
        f = k - i
        return tuple(ship_pts[i][c] + (ship_pts[i + 1][c] - ship_pts[i][c]) * f for c in range(3))
    inst.joints = {
        "jarpos": Track(knots=tl.knots(lambda st: (st["p"][0] - jx, st["p"][1] - jy, st["p"][2] - jz))),
        "jartilt": Turn(parent="jarpos", axis=(0, 1, 0), pivot=(jx, jy, mid),
                        knots=tuple((v, c[0]) for v, c in tl.knots(lambda st: (st["tilt"], 0, 0)))),
        "jar": Turn(parent="jartilt", axis=(0, 0, 1), pivot=(jx, jy, 0),
                    knots=tuple((v, c[0]) for v, c in tl.knots(lambda st: (st["spin"], 0, 0)))),
        "jarlabel": Joint("fade", parent="jar"),
        "bag": Joint("fade", parent="jar"),                # it turns with the jar on the way to the foam
        "neck": Joint("fade", parent="jartilt"),
        "stripslide": Joint("slide", vec=(0, -60, 0)),
        "strip": Joint("fade", parent="stripslide"),
        "press": Turn(axis=(1, 0, 0), pivot=press_pivot,
                      knots=tuple((v, c[0]) for v, c in tl.knots(
                          lambda st: (press_down + (press_up - press_down) * st["press"], 0, 0)))),
        "arm": Turn(axis=(1, 0, 0), pivot=(sx_, yf + se["D"], 126),
                    knots=tuple((v, c[0]) for v, c in tl.knots(lambda st: (-35.0 * st["arm"], 0, 0)))),
        "lid": Joint("hinge", axis=(1, 0, 0), pivot=(bx_, yf + b["D"], b["H"] - 40), deg=-105.0, v0=1.0),
        "shiplabel": Track(knots=tl.knots(ship_off)),
        "inset_jar": Joint("slide", vec=(1, 0, 0)),
        "inset_ship": Joint("slide", vec=(1, 0, 0)),
    }
    track = ("jarpos", "jartilt", "jar", "shiplabel", "press", "arm")

    def seg(a_, b_, **extra):
        out = {k: (tl.v(a_), tl.v(b_)) for k in track}
        out.update(extra)
        return out
    inst.actions = [
        ("A 250 mL jar of powder goes into the printed nest.", 1.8, seg("start", "nested")),
        ("The LX500c prints its label: sample ID, alloy, mass, date and a QR code. The AP380 takes such labels "
         "die-cut on a roll.", 2.4, {"stripslide": (0.0, 1.0), "strip": (0.0, 1.0), "inset_jar": (0.0, 1.0)}),
        ("The jar goes into the AP380, lying down on its rollers; the pressure arm comes down.", 2.8,
         {**seg("nested", "in AP380"), "strip": (1.0, 0.0)}),
        ("One press of the foot switch: the rollers turn the jar once and the label wraps on.", 2.2,
         {**seg("in AP380", "labelled"), "jarlabel": (0.0, 1.0)}),
        ("The pressure arm lifts. Out, and into a clear liner bag, standing in front of the H-190 impulse sealer.", 2.8,
         {**seg("labelled", "at sealer"), "bag": (0.0, 1.0), "inset_jar": (1.0, 0.0), "neck": (0.0, 0.0)}),
        ("The bag's mouth goes across the jaw, and the sealer closes on it: a 12 in seal.", 1.9,
         {**seg("at sealer", "sealed"), "neck": (0.0, 1.0)}),
        ("Into the foam insert's cut-out, lying down.", 2.8, {**seg("sealed", "boxed"), "neck": (1.0, -1.0)}),
        ("The lid goes on.", 1.4, {**seg("boxed", "lid on"), "lid": (1.0, 0.0)}),
        ("The ZD621 prints the 4 x 6 in shipping label, and it goes on the lid. Whether the box needs dangerous-goods "
         "marks depends on a test, not on the alloy's name.", 3.4,
         {**seg("lid on", "shipped"), "inset_ship": (0.0, 1.0)}),
        ("", 2.0, {}),
    ]
    inst.labels = _pack_labels()[9]
    inst.cam = (0.25, -1.6, 0.85)
    inst.framing = (0.62, 0.30)
    return inst


_PK_OVER = ((0.0, -2300.0, 1450.0), (0.0, 0.0, 120.0))
_PK_LEFT = ((-780.0, -1250.0, 760.0), (-560.0, -60.0, 110.0))
_PK_SEAL = ((260.0, -950.0, 560.0), (260.0, -150.0, 110.0))
_PK_BOX = ((700.0, -1050.0, 760.0), (650.0, -80.0, 90.0))
CAMS["instruments/packaging"] = {0: _PK_LEFT, 4: _PK_SEAL, 6: _PK_BOX, 9: _PK_OVER}
PLOTS["instruments/packaging"] = _draw_packaging_insets
LABELS["instruments/packaging"] = _pack_labels()


# ===================================================================================================== DED
# InssTek MX-Lab, a laser powder DED machine for alloy development, freestanding on its base cabinet. Chosen over the
# FormAlloy X2 and L2 because it is the only one of the three with a published size and mass, and because it is the
# first step in DAL's own plan (PR #117: machine time on the MX-Lab in Prof. Zak Fang's lab at the University of Utah,
# about 0.5 kg of powder a deposit; then the FormAlloy X2 at Mines, 1 kW, four feeders, 250 x 250 x 300 mm, at least
# 2 kg a powder).
#  - 680 x 684 x 835 mm "(without accessories)", 250 kg; 1-phase 220 V, 15(20) A (InssTek MX-Lab Technical Data
#    Rev.3, 2020-12; that sheet is for the 300 W version, and the 2024 brochure gives no dimensions).
#  - 150 x 150 x 150 mm stroke; 175 x 175 mm worktable; up to six hoppers, about 0.42 L each, fed at the same time
#    to mix in the melt pool; 0.03-2 g/min (Ti-6Al-4V); Yb fibre laser, 400 um beam, up to 500 W (2024 brochure).
#  - Option: argon (> 99.999 %) with O2 <= 50 ppm in the chamber; leak rate class 1 (2024 brochure; Phillips).
#  - Look (InssTek's and Chalmers' photos): matte black; a seam a little above mid-height; above it a small
#    touchscreen, an E-stop, key switch and buttons, vent slots; the lower band is the door, hinged on the left, with
#    a large dark laser-filter window and an orange gasket. Inside, the deposition head with orange powder lines and a
#    perforated build plate.
#  - The base cabinet on casters is not in the published figures: about 900 mm wide and 1000 mm tall, scaled from
#    the Chalmers photo against the published 680 mm width. An estimate.
DED = dict(W=680.0, D=684.0, H=835.0, base_w=900.0, base_d=760.0, base_h=1000.0, seam=0.55, table=175.0, plate=100.0,
           plate_t=10.0, spokes=6, layers=3, segs=4, r0=8.0, r1=45.0, bead_w=3.2, bead_h=1.1)
SPOKE_C = ((0.80, 0.45, 0.25), (0.82, 0.52, 0.28), (0.84, 0.60, 0.32), (0.80, 0.66, 0.40), (0.74, 0.70, 0.52),
           (0.70, 0.71, 0.70))      # copper to a pale alloy grey: one colour a blend, illustrative
for _i, _c in enumerate(SPOKE_C):
    MATERIALS[f"ded_spoke{_i}"] = (*_c, 1.0, 0.6)
MATERIALS["ded_orange"] = (0.95, 0.45, 0.08, 1.0, 0.3)
MATERIALS["ded_window"] = (0.30, 0.22, 0.10, 0.55, 0.9)      # a laser-filter window: dark amber


def _draw_ded_overlay(sc, img, s):
    from PIL import ImageDraw
    from scene import font
    key = "ded:"
    a = min(1.0, _gv(sc, key + "gauge"))
    if a <= 0.02:
        return
    pu = _gv(sc, key + "purge")
    W, H = img.size
    d = ImageDraw.Draw(img, "RGBA")
    al = int(255 * a)
    x0, y0, x1, y1 = W - 330 * s, 46 * s, W - 10 * s, 46 * s + 96 * s
    d.rounded_rectangle((x0, y0, x1, y1), 6 * s, fill=(255, 255, 255, int(236 * a)), outline=(150, 156, 164, al))
    lo, hi = math.log10(50.0), math.log10(209000.0)
    ppm = 10 ** (hi + (lo - hi) * pu)
    txt = f"{ppm / 1e4:.1f} %" if ppm >= 1e4 else f"{ppm:,.0f} ppm"
    d.text((x0 + 10 * s, y0 + 6 * s), "Chamber O2 during the argon purge", font=font(13 * s, bold=True),
           fill=(20, 20, 24, al))
    d.text((x0 + 10 * s, y0 + 26 * s), txt, font=font(20 * s, bold=True), fill=(30, 60, 140, al))
    bx0, bx1, by = x0 + 140 * s, x1 - 12 * s, y0 + 38 * s
    d.rectangle((bx0, by - 6 * s, bx1, by + 6 * s), outline=(120, 124, 130, al))
    d.rectangle((bx0, by - 6 * s, bx0 + (bx1 - bx0) * (1 - pu), by + 6 * s), fill=(30, 60, 140, int(200 * a)))
    d.text((x0 + 10 * s, y0 + 56 * s), "air, 20.9 %, to <= 50 ppm: InssTek's inert option.",
           font=font(11 * s), fill=(80, 84, 90, al))
    d.text((x0 + 10 * s, y0 + 72 * s), "Log scale; the time it takes is not published.", font=font(11 * s),
           fill=(150, 40, 30, al))


def ded() -> Instrument:
    p = DED
    W, D, H = p["W"], p["D"], p["H"]
    bw, bd, bh = p["base_w"], p["base_d"], p["base_h"]
    inst = Instrument(
        "ded", "Directed energy deposition, powder-fed laser", "InssTek MX-Lab", (W, D, H),
        "InssTek MX-Lab Technical Data Rev.3 (680 x 684 x 835 mm, 250 kg, 1-phase 220 V), InssTek's 2024 brochure "
        "(150 mm stroke, 175 mm table, six hoppers, <= 500 W, Ar with <= 50 ppm O2); look from InssTek's and Chalmers' "
        "photos. The base cabinet's size is an estimate", floor=True,
        props=("load", "glow", "purge", "gauge") + tuple(f"bead{k}_{l}_{g}" for k in range(p["spokes"])
                                                        for l in range(p["layers"]) for g in range(p["segs"])))
    body = _piece(inst, "body")
    yb = -bd / 2
    # ---- base cabinet (estimated), casters, the fold-out shelf, the exhaust duct
    body.add("base cabinet", box(-bw / 2, yb, 90, bw / 2, bd / 2, bh), "inst_black")
    for sx in (-1, 1):
        for sy in (-1, 1):
            body.add(f"caster {sx}{sy}", cyl(70, 60, x=sx * (bw / 2 - 70), y=sy * (bd / 2 - 70), z=10), "pp_black")
            body.add(f"levelling foot {sx}{sy}", cyl(40, 90, x=sx * (bw / 2 - 140), y=sy * (bd / 2 - 70)), "stainless")
    for i in range(10):
        body.add(f"base vent {i}", box(bw / 2 - 300 + i * 26, yb - 1, 160, bw / 2 - 288 + i * 26, yb, 420), "inst_dark")
    body.add("base panel", box(-bw / 2 + 60, yb - 1, bh - 200, -bw / 2 + 220, yb, bh - 90), "screen_on")
    body.add("base power", _ycyl(30, 8, x=-bw / 2 + 280, y=yb - 8, z=bh - 145), "inst_green")
    body.add("shelf", box(bw / 2, -150, bh - 120, bw / 2 + 300, 150, bh - 100), "stainless")
    body.add("balance", box(bw / 2 + 60, -110, bh - 100, bw / 2 + 260, 110, bh - 30), "inst_offwhite")
    body.add("exhaust duct", cyl(110, bh + H - 60, x=-bw / 2 - 60, y=bd / 2 - 120, z=60), "stainless")
    body.add("duct bellows", cyl(126, 180, x=-bw / 2 - 60, y=bd / 2 - 120, z=bh + H - 400), "inst_grey")
    # ---- the MX-Lab: a matte black near-cube, the front-left edge rounded
    z0 = bh
    yf = -D / 2
    zseam = z0 + p["seam"] * H
    dx0, dx1, dz0, dz1 = -W / 2 + 40, W / 2 - 90, z0 + 40, zseam - 20          # the door
    cav = box(dx0 + 10, yf - 1, dz0 + 10, dx1 - 10, D / 2 - 60, dz1 - 10)
    shell = box(-W / 2, yf, z0, W / 2, D / 2, z0 + H).edges("|Z").edges("<X and <Y").fillet(110)
    body.add("cabinet", shell.cut(cav), "inst_black")
    body.add("seam", box(-W / 2 + 20, yf - 1, zseam - 3, W / 2 - 4, yf, zseam + 3), "inst_dark")
    body.add("screen", box(40, yf - 2, zseam + 110, 210, yf, zseam + 210), "screen_on")
    for i, c in enumerate(("inst_orange", "inst_red", "inst_orange")):
        body.add(f"screen tile {i}", box(55 + 52 * i, yf - 3, zseam + 125, 95 + 52 * i, yf - 2, zseam + 150), c)
    body.add("e-stop ring", _ycyl(70, 6, x=W / 2 - 70, y=yf - 6, z=zseam + 165), "inst_yellow")
    body.add("e-stop", _ycyl(48, 22, x=W / 2 - 70, y=yf - 26, z=zseam + 165), "inst_red")
    body.add("key switch", _ycyl(26, 8, x=W / 2 - 70, y=yf - 8, z=zseam + 90), "chrome")
    for i, z in enumerate((zseam + 40, zseam + 60)):
        body.add(f"button {i}", _ycyl(20, 8, x=W / 2 - 140 + 40 * i, y=yf - 8, z=zseam + 50), "inst_white")
    for i in range(6):
        body.add(f"vent slot {i}", box(80 + i * 34, yf - 1, z0 + H - 150, 96 + i * 34, yf, z0 + H - 30), "inst_dark")
    body.add("safety labels", box(-W / 2 + 120, yf - 1, zseam + 150, -W / 2 + 280, yf, zseam + 260), "inst_yellow")
    for sz in (z0 + H - 170, z0 + H - 330):
        body.add(f"fan grille {sz:.0f}", box(W / 2, -60, sz - 120, W / 2 + 4, 120, sz), "inst_dark")
    # ---- the chamber: worktable, perforated plate, the head's Z column
    tz = dz0 + 85                                       # the worktable's top
    tcx, tcy = (dx0 + dx1) / 2, -40.0
    body.add("chamber floor", box(dx0 + 10, yf + 30, dz0 + 10, dx1 - 10, D / 2 - 60, dz0 + 14), "inst_dark")
    body.add("table pedestal", box(tcx - 60, tcy - 60, dz0 + 14, tcx + 60, tcy + 60, tz - 20), "inst_dark")
    tbl = box(tcx - p["table"] / 2, tcy - p["table"] / 2, tz - 20, tcx + p["table"] / 2, tcy + p["table"] / 2, tz)
    holes = cq.Workplane("XY").pushPoints([(tcx - 70 + 20 * i, tcy - 70 + 20 * j) for i in range(8) for j in range(8)]
                                          ).circle(3).extrude(12).translate((0, 0, tz - 6))
    body.add("worktable", tbl.cut(holes), "steel")
    body.add("chamber light", box(dx0 + 20, D / 2 - 64, dz1 - 40, dx1 - 20, D / 2 - 60, dz1 - 20), "vlm_led")
    # ---- the door: hinged on its left edge, a dark laser-filter window, an orange gasket, two clamp latches
    door = _piece(inst, "door")
    dw = dx1 - dx0
    wx0, wx1 = dx0 + 0.15 * dw, dx1 - 0.15 * dw
    door.add("door", box(dx0, yf - 30, dz0, dx1, yf, dz1).cut(box(wx0, yf - 31, dz0 + 60, wx1, yf + 1, dz1 - 60)),
             "inst_black")
    door.add("window", box(wx0, yf - 22, dz0 + 60, wx1, yf - 8, dz1 - 60), "ded_window")
    door.add("gasket", box(dx0 + 4, yf - 2, dz0 + 4, dx1 - 4, yf + 2, dz1 - 4).cut(
        box(dx0 + 14, yf - 3, dz0 + 14, dx1 - 14, yf + 3, dz1 - 14)), "ded_orange")
    for zz in (dz0 + 90, dz1 - 90):
        door.add(f"latch {zz:.0f}", box(dx1 - 40, yf - 55, zz - 20, dx1 - 10, yf - 30, zz + 20), "chrome")
    # ---- the head: a coaxial nozzle with six orange powder lines, on a carriage from the chamber's ceiling
    plate_top = tz + p["plate_t"]
    stand = 9.0                                         # nozzle standoff over the surface being built
    hz = plate_top + stand + 60                         # the head is modelled 60 mm up, over the plate's centre
    head = _piece(inst, "head")
    head.add("nozzle", _cone(44, 10, 50, x=tcx, y=tcy, z=hz - 60 + 2), "copper")
    head.add("head body", cyl(70, 150, x=tcx, y=tcy, z=hz - 8), "aluminium")
    head.add("Z carriage", box(tcx - 40, tcy + 35, hz + 40, tcx + 40, tcy + 55, dz1 - 12), "inst_dark")
    for i in range(6):
        ang = math.radians(60 * i + 30)
        x1, y1 = tcx + 26 * math.cos(ang), tcy + 26 * math.sin(ang)
        head.add(f"powder line {i}", hose([(x1, y1, hz + 20), (tcx + 50 * math.cos(ang), tcy + 50 * math.sin(ang),
                                                                hz + 90), (tcx + 30 * math.cos(ang), tcy + 60,
                                                                           dz1 - 12)], 6), "ded_orange")
    glow = _piece(inst, "glow")
    glow.add("melt pool", cq.Workplane().add(cq.Solid.makeSphere(4.2, cq.Vector(tcx, tcy, plate_top + 0.6),
                                                                  angleDegrees1=-90, angleDegrees2=90)), "glow")
    # ---- the substrate, and the wagon wheel's beads in segments that rise as the nozzle passes
    load = _piece(inst, "load")
    pl = p["plate"]
    load.add("substrate", box(tcx - pl / 2, tcy - pl / 2, tz, tcx + pl / 2, tcy + pl / 2, plate_top), "steel")
    seg_len = (p["r1"] - p["r0"]) / p["segs"]
    for k in range(p["spokes"]):
        ang = 2 * math.pi * k / p["spokes"]
        for l_ in range(p["layers"]):
            for g in range(p["segs"]):
                r_a = p["r0"] + g * seg_len
                b = box(r_a, -p["bead_w"] / 2, 0, r_a + seg_len + 0.4, p["bead_w"] / 2, p["bead_h"])
                b = b.edges("|X").fillet(p["bead_h"] * 0.45)
                b = b.rotate((0, 0, 0), (0, 0, 1), math.degrees(ang)).translate(
                    (tcx, tcy, plate_top + l_ * p["bead_h"]))
                _piece(inst, f"bead{k}_{l_}_{g}").add("bead", b, f"ded_spoke{k}")
    # ---- the build on one timeline: head xyz, the melt pool, each bead segment
    tl = Timeline(dict(h=(0.0, 0.0, 60.0), pool=0.0, built=frozenset()))
    for l_ in range(p["layers"]):
        zl = l_ * p["bead_h"]
        for k in range(p["spokes"]):
            ang = 2 * math.pi * k / p["spokes"]
            c, s_ = math.cos(ang), math.sin(ang)
            tl.go(0.10, h=(p["r0"] * c, p["r0"] * s_, zl + 3), pool=0.0)
            tl.go(0.04, pool=1.0)
            for g in range(p["segs"]):
                r_b = p["r0"] + (g + 1) * seg_len
                built = set(tl.states[-1]["built"]) | {(k, l_, g)}
                tl.go(0.07, h=(r_b * c, r_b * s_, zl), built=frozenset(built))
            tl.go(0.04, pool=0.0)
    tl.go(0.25, h=(0.0, 0.0, 60.0))
    joints = {
        "door": Joint("hinge", axis=(0, 0, 1), pivot=(dx0, yf - 30, 0), deg=-105.0),
        # off the balance, forward past the cabinet's right side, across in front of it, in through the door
        "load": Joint("path", path=((bw / 2 + 160, 0.0, bh - 30), (bw / 2 + 160, 0.0, bh + 120),
                                    (bw / 2 + 160, yf - 260, tz + 80), (tcx + 60, yf - 260, tz + 80),
                                    (tcx, yf - 120, tz + 40), (tcx, tcy, tz + 25), (tcx, tcy, tz))),
        "head": Track(knots=tl.knots(lambda st: st["h"])),
        "glow": Track(parent="head", knots=tl.knots(lambda st: (0, 0, (1 - st["pool"]) * 30.0))),
        "purge": Joint("slide", vec=(1, 0, 0)),
        "gauge": Joint("slide", vec=(1, 0, 0)),
    }
    # the substrate is modelled on the table, so the path's last point is the origin of its offsets
    jl = joints["load"]
    joints["load"] = Joint("path", path=tuple((x - tcx, y - tcy, z - tz) for x, y, z in jl.path))
    for k in range(p["spokes"]):
        for l_ in range(p["layers"]):
            for g in range(p["segs"]):
                hide = -(l_ + 1) * p["bead_h"] - 2.0
                joints[f"bead{k}_{l_}_{g}"] = Track(knots=tl.knots(
                    lambda st, key=(k, l_, g), h_=hide: (0, 0, 0.0 if key in st["built"] else h_)))
    inst.joints = joints
    beads = [k for k in joints if k.startswith("bead")]
    build = {k: (0.0, 1.0) for k in ["head", "glow"] + beads}
    inst.actions = [
        ("The MX-Lab stands on the floor beside the VLM: 680 x 684 x 835 mm and 250 kg without its base, taller "
         "than the 727.5 mm a tray takes. Up to six powder hoppers feed one nozzle.", 2.6, {"load": (0.0, 0.0)}),
        ("The door swings open on its left hinge.", 1.6, {"door": (0.0, 1.0)}),
        ("A steel substrate goes from the shelf onto the 175 x 175 mm worktable.", 2.6, {"load": (0.0, 1.0)}),
        ("Door shut. Argon purges the chamber: InssTek's inert option holds O2 at or below 50 ppm.", 2.8,
         {"door": (1.0, 0.0), "gauge": (0.0, 1.0), "purge": (0.0, 1.0), "~door": (0.0, 1.0)}),
        ("The laser and the powder streams meet at the melt pool. Spoke by spoke, layer by layer: a wagon wheel, each "
         "spoke a different blend from the six hoppers (colours illustrative).", 7.5,
         {**build, "~door": (1.0, 1.0), "gauge": (1.0, 0.0)}),
        ("Laser off; the door opens on six compositions in one build.", 2.0,
         {"~door": (1.0, 0.0), "door": (0.0, 1.0)}),
        ("", 1.2, {}),
    ]
    inst.labels = [("six-hopper\ncoaxial nozzle", (tcx, tcy - 35, hz + 40), (0.14, 0.30)),
                   ("175 mm worktable", (tcx - 80, tcy - 80, tz), (0.14, 0.70)),
                   ("door with laser-\nfilter window", (dx1 - 20, yf - 30, dz1 - 120), (0.84, 0.66))]
    inst.cam = (0.9, -1.9, 0.75)
    return inst


_DED_OVER = ((1900.0, -3300.0, 2300.0), (0.0, 0.0, 950.0))
_DED_DOOR = ((900.0, -1650.0, 1650.0), (-30.0, -200.0, 1250.0))
_DED_IN = ((260.0, -620.0, 1420.0), (-65.0, -40.0, 1145.0))
CAMS["instruments/ded"] = {1: _DED_DOOR, 3: _DED_IN, 6: _DED_OVER}
PLOTS["instruments/ded"] = _draw_ded_overlay


# ===================================================================================================== HIP
# "Could a hot isostatic press fit on the VLM?" The smallest 200 MPa laboratory HIP with a published envelope is
# Kobelco's O2-Dr.HIP: 1315 W x 1100 D x 1300 H mm, 1100 kg, 200 MPa; 1500 C (Pt-Rh), 2000 C (graphite) or 1500 C
# (Mo) heaters; hot zones 50 x 60, 50 x 75 or 75 x 100 mm (kobelco.co.jp, Dr. HIP page). Against a Kardex tray
# (#53, the order sheet): 2450 x 864 mm, about 2426 x 840 inside the rim; 727.5 mm of product height through the
# opening; 228 / 360 / 490 kg for light / medium / strong trays; power in a slot and at the opening, not in transit,
# and no gas or water. Others, for the record: AIP6-30H (30,000 psi, 75 x 125 mm hot zone) publishes no size or mass;
# EPSI's lab HIPs and Hiperbaric's HIP 10 likewise; Quintus' smallest current compact unit, the QIH 15L, is
# 4.2 x 3.0 x 3.4 m and 8 t; MTI's CM-HIP-2 (1200 x 630 x 1425 mm, 250 kg) is a 20 MPa furnace, a tenth of HIP
# pressure, and still too tall. A "QIH 3" was not found.
# Look (Kobelco's photo and cutaway): one off-white enclosure; on the left a tall housing with a rounded, drum-like
# front around the vessel; on the right a cabinet with the HMI screen and keypad on its upper face and a full-height
# door; a broad red band at about three-quarter height with KOBELCO in white; a plinth. Inside, a vertical vessel held
# by a frame across its closures. The vessel's and the frame's sizes are not published: drawn schematically.
HIP = dict(W=1315.0, D=1100.0, H=1300.0, mass=1100.0, p_mpa=200.0, hot=(75.0, 100.0),
           tray=(2450.0, 864.0), inside=(2426.0, 840.0), h_max=727.5, payload=(228.0, 360.0, 490.0),
           header=844.0, opening_w=2500.0)


def hip_numbers() -> dict:
    """The comparison, and the stored energy of the gas by NIST NCNR's method for isentropic expansion,
    W = P1 V1 / (k - 1) [1 - (P2 / P1)^((k - 1) / k)], ideal-gas argon (k = 5/3): a rough figure at 200 MPa."""
    h = HIP
    k, p1, p2 = 5.0 / 3.0, h["p_mpa"] * 1e6, 0.101e6
    per_l = p1 * 1e-3 / (k - 1) * (1 - (p2 / p1) ** ((k - 1) / k))
    hot_l = math.pi / 4 * (h["hot"][0] / 10) ** 2 * (h["hot"][1] / 10) / 1000
    return dict(height_over_mm=h["H"] - h["h_max"], height_ratio=round(h["H"] / h["h_max"], 2),
                depth_over_inside_mm=h["D"] - h["inside"][1], depth_over_tray_mm=h["D"] - h["tray"][1],
                mass_ratio={n: round(h["mass"] / m, 1) for n, m in zip(("light", "medium", "strong"), h["payload"])},
                energy_MJ_per_L=round(per_l / 1e6, 3), hot_zone_L=round(hot_l, 3),
                energy_hot_zone_MJ=round(per_l * hot_l / 1e6, 3), header_over_mm=h["H"] - h["header"])


def _draw_hip_overlay(sc, img, s):
    from PIL import ImageDraw
    from scene import font
    a = min(1.0, _gv(sc, "hip:table"))
    if a <= 0.02:
        return
    n = hip_numbers()
    h = HIP
    W, H = img.size
    d = ImageDraw.Draw(img, "RGBA")
    al = int(255 * a)
    x0, y0, x1 = W - 470 * s, 46 * s, W - 10 * s
    rows = [("", "O2-Dr.HIP", "tray limit"),
            ("height", f"{h['H']:.0f} mm", f"{h['h_max']} mm"),
            ("depth", f"{h['D']:.0f} mm", f"{h['tray'][1]:.0f} mm tray"),
            ("mass", f"{h['mass']:.0f} kg", "228 / 360 / 490 kg"),
            ("services", "Ar, water, air", "power, not in transit"),
            ("gas", f"{h['p_mpa']:.0f} MPa argon", "none")]
    y1 = y0 + (len(rows) * 20 + 66) * s
    d.rounded_rectangle((x0, y0, x1, y1), 6 * s, fill=(255, 255, 255, int(238 * a)), outline=(150, 156, 164, al))
    d.text((x0 + 10 * s, y0 + 6 * s), "On a tray? No.", font=font(15 * s, bold=True), fill=(170, 30, 30, al))
    for i, (k, v1, v2) in enumerate(rows):
        yy = y0 + (30 + i * 20) * s
        f = font(12.5 * s, bold=(i == 0))
        d.text((x0 + 10 * s, yy), k, font=f, fill=(80, 84, 90, al))
        d.text((x0 + 100 * s, yy), v1, font=f, fill=(170, 30, 30, al) if i else (20, 20, 24, al))
        d.text((x0 + 265 * s, yy), v2, font=f, fill=(20, 20, 24, al))
    d.text((x0 + 10 * s, y1 - 32 * s), f"Gas energy, ideal argon at 200 MPa: about {n['energy_MJ_per_L']:.2f} MJ per "
           f"litre (NIST", font=font(11 * s), fill=(80, 84, 90, al))
    d.text((x0 + 10 * s, y1 - 18 * s), f"NCNR's method); the 75 x 100 mm hot zone alone, {n['energy_hot_zone_MJ']:.2f} MJ."
           , font=font(11 * s), fill=(80, 84, 90, al))


def hip() -> Instrument:
    h = HIP
    W, D, H = h["W"], h["D"], h["H"]
    inst = Instrument(
        "hip", "Hot isostatic press against a VLM tray", "Kobelco O2-Dr.HIP", (W, D, H),
        "Kobelco's Dr. HIP page (O2-Dr.HIP: 1315 x 1100 x 1300 mm, 1100 kg, 200 MPa, up to 2000 C) and photo; the "
        "tray, product height and payloads from #53 and Kardex's order sheet. Vessel and frame inside drawn "
        "schematically (not published)", floor=True, props=("hip", "vessel", "over", "env", "table"))
    body = _piece(inst, "body")
    tw, td = h["tray"]
    # ---- the tray, the product height it takes, and the opening's posts and header
    body.add("tray", box(-tw / 2, -td / 2, -22, tw / 2, td / 2, 0).cut(
        box(-tw / 2 + 12, -td / 2 + 12, -10, tw / 2 - 12, td / 2 - 12, 1)), "inst_light")
    body.add("tray floor", box(-tw / 2 + 12, -td / 2 + 12, -12, tw / 2 - 12, td / 2 - 12, -10), "inst_grey")
    ow = h["opening_w"]
    for sx in (-1, 1):
        body.add(f"opening post {sx:+d}", box(sx * ow / 2 - (0 if sx > 0 else 60), -td / 2 - 80, -22,
                                              sx * ow / 2 + (60 if sx > 0 else 0), -td / 2 - 20, h["header"]),
                 "anthracite")
    body.add("opening header", box(-ow / 2 - 60, -td / 2 - 80, h["header"], ow / 2 + 60, -td / 2 - 20,
                                   h["header"] + 160), "paint_white")
    env = _piece(inst, "env")
    iw, idp = h["inside"]
    env.add("product height", box(-iw / 2, -idp / 2, 0, iw / 2, idp / 2, h["h_max"]), "window")
    env.add("height line", box(-iw / 2, -idp / 2 - 1, h["h_max"] - 2, iw / 2, -idp / 2 + 1, h["h_max"] + 2), "inst_blue")
    # ---- the O2-Dr.HIP, modelled centred on the tray (hipdrop sets it back): drum housing on the left, cabinet on the
    # right, plinth, red band
    _piece(inst, "hipdrop")                              # an empty parent: lowers the HIP onto the tray
    hp = _piece(inst, "hip")
    xd = -W / 2 + 350                                    # the drum's axis
    hp.add("plinth", box(-W / 2 + 10, -D / 2 + 10, 0, W / 2 - 10, D / 2 - 10, 60), "inst_grey")
    drum = box(-W / 2, -D / 2 + 350, 60, xd + 350, D / 2, H).union(cyl(700, H - 60, x=xd, y=-D / 2 + 350, z=60))
    hp.add("drum housing", drum, "inst_white")
    hp.add("cabinet", box(xd + 350, -D / 2, 60, W / 2, D / 2, H), "inst_offwhite")
    hp.add("cabinet door", box(xd + 380, -D / 2 - 4, 90, W / 2 - 30, -D / 2, 900), "inst_white")
    hp.add("door handle", box(W / 2 - 80, -D / 2 - 30, 420, W / 2 - 60, -D / 2 - 4, 600), "inst_grey")
    hp.add("HMI", box(xd + 420, -D / 2 - 3, 1060, xd + 640, -D / 2, 1220), "screen_on")
    hp.add("keypad", box(W / 2 - 160, -D / 2 - 3, 1080, W / 2 - 60, -D / 2, 1200), "inst_dark")
    band = box(-W / 2 - 3, -D / 2 + 350, 940, W / 2 + 3, D / 2 + 3, 1020).union(
        cyl(706, 80, x=xd, y=-D / 2 + 350, z=940)).union(box(xd + 350, -D / 2 - 3, 940, W / 2 + 3, D / 2 + 3, 1020))
    hp.add("red band", band.cut(box(xd + 400, -D / 2 - 10, 930, xd + 660, -D / 2 + 5, 1030)), "inst_red")
    import pyvista as pv
    t = pv.Text3D("KOBELCO", depth=0.04)
    b = t.bounds
    t = t.translate((-b[0], -b[2], -b[4]), inplace=False).scale(50.0 / (b[3] - b[2]), inplace=False)
    t = t.rotate_x(90, inplace=False).translate((xd - 160, -D / 2 - 4, 955), inplace=False)
    inst.meshes["hip"] = [(t, (1.0, 1.0, 1.0), 1.0)]
    vessel = _piece(inst, "vessel")                      # schematic: sizes not published
    vessel.add("vessel", cyl(360, 640, x=xd, y=-D / 2 + 350, z=180), "stainless")
    vessel.add("frame", box(xd - 300, -D / 2 + 320, 120, xd + 300, -D / 2 + 380, 900).cut(
        box(xd - 240, -D / 2 + 300, 180, xd + 240, -D / 2 + 400, 840)), "inst_dark")
    vessel.add("hot zone", cyl(75, 100, x=xd, y=-D / 2 + 350, z=450), "glow")
    # Centred, the HIP's front would stand 118 mm over the tray's front edge, through the opening's header, which is
    # 20-80 mm in front of the tray. So it is set back on the tray until its door handle clears the header, and the
    # whole 236 mm it is deeper than the tray overhangs the back.
    back = -td / 2 - 20 + 2 - (-D / 2 - 30)              # 130 mm: the handle 2 mm behind the header's back face
    over = _piece(inst, "over")
    e = 14.0                                             # proud of the HIP's faces, so they don't fight
    over.add("too tall", box(-W / 2 - e, -td / 2 - 19, h["h_max"], W / 2 + e, back + D / 2 + e, H + e), "lab_over")
    over.add("too deep, back", box(-W / 2 - e, td / 2, 0, W / 2 + e, back + D / 2 + e, h["h_max"]), "lab_over")
    inst.joints = {
        "env": Joint("fade"),
        "hipdrop": Joint("path", path=((0, back, 1500.0), (0, back, 300.0), (0, back, 0)), v0=1.0),
        "hip": Joint("fade", parent="hipdrop"),
        "vessel": Joint("fade", parent="hip"),
        "over": Joint("fade"),
        "table": Joint("slide", vec=(1, 0, 0)),
    }
    n = hip_numbers()
    inst.actions = [
        ("A Kardex tray, 2450 x 864 mm, and the room above it: 727.5 mm of product height through the opening.", 2.6,
         {"env": (0.0, 1.0), "hip": (0.0, 0.0), "vessel": (0.0, 0.0), "over": (0.0, 0.0), "hipdrop": (0.0, 0.0)}),
        ("The smallest 200 MPa lab HIP with a published size: Kobelco's O2-Dr.HIP, 1315 x 1100 x 1300 mm, 1100 kg.",
         2.8, {"hip": (1.0, 1.0), "hipdrop": (0.0, 1.0)}),
        (f"{n['height_over_mm']:.0f} mm too tall and {n['depth_over_tray_mm']:.0f} mm deeper than the tray; "
         f"{n['mass_ratio']['strong']} times what a strong tray carries.", 3.0,
         {"over": (0.0, 1.0), "table": (0.0, 1.0)}),
        ("Inside, a vessel in a frame (drawn schematically): argon at 200 MPa, up to 2000 C. A HIP needs argon, "
         "cooling water and air, and its cooling must not stop. A tray has power only, and not in transit.", 3.8,
         {"over": (1.0, 0.0), "~hip": (0.0, 1.0), "vessel": (0.0, 1.0)}),
        ("So no. A HIP stands on the floor with its gas and water, like the wire EDM, and the arm brings it work.", 2.4,
         {"~hip": (1.0, 0.0), "vessel": (1.0, 0.0)}),
    ]
    inst.labels = [("727.5 mm product height", (-iw / 2 + 200, -idp / 2, h["h_max"]), (0.10, 0.22)),
                   ("tray, 2450 x 864 mm", (-tw / 2 + 150, -td / 2, 0), (0.10, 0.80)),
                   ("opening header", (ow / 2 - 200, -td / 2 - 80, h["header"] + 80), (0.86, 0.80))]
    inst.cam = (0.55, -1.7, 0.75)
    inst.framing = (0.80, 0.45)
    inst.notes = [f"{k}: {v}" for k, v in n.items()]
    return inst


PLOTS["instruments/hip"] = _draw_hip_overlay


# ===================================================================================================== registry
REGISTRY = {"cubxl_corrosion": cubxl_corrosion, "ded": ded, "packaging": packaging, "hip": hip}
