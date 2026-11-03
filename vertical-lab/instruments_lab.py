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
from dataclasses import dataclass, field
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
# The CubXL as DAL PR #180 (alloy-corrosion/, branch claude/issue-213-20261013-2132) proposes it for corrosion spots,
# in the CubOS deck frame of Ben's 2026-10-02 calibration (cubxl-setup.md): origin front left, x right, y away, mm.
# Every deck coordinate below is DAL's proposal, not a measurement. Nothing in it has been printed, wired or run.
#  - Coupon tray, stations S1-S4 at x 185/210/235/260, y 240; tray 170-275 x 220-260; coupon face at z 20, lid top
#    26, 42 with the electrode cap on. Each piece sits face up on a pogo pin (the working-electrode contact to its
#    bare back), under a lid that presses an FKM O-ring (AS568-006, 3 mm well, 0.071 cm2) onto its face; an 8 mm
#    bore above holds about 150 uL.
#  - The electrode cap: 20 mm across, 16 mm tall; a leak-free 2 mm Ag/AgCl reference down the middle inside five
#    turns of 0.25 mm Pt wire (the counter), protruding 4.5 mm; a steel disc on top for the capper's 50 N magnet; two
#    pogo pins at +-11 mm that land on RE and CE pads beside each station. About 15 g of PETG.
#  - Stocks: 0.6, 0.06, 0.006 M NaCl and DI water in capped 20 mL vials at (318, 101/134/167/200), caps at 71.
#  - Rinse cup (60, 245) and park cup (90, 245), 4 mL vials, top 45 (61 with the cap on).
#  - Tube rack, 2 x 8 open 0.5 mL PP tubes at x 176 + 12k, y 28/46, top 32: each spot's liquid, for ICP.
#  - Tip racks: Ben's, A1 (291.3, 89), unmoved; a printed 2 x 15 rack, A1 (108, 89), A2 (99.5, 89). Tip waste
#    (335, 40), 30 mm across, top 50.
#  - The head: capper (0, 0), lowest point 16 below the carriage, 36.5 carrying the cap; P20 single Gen2 at
#    (+55, +11), 35 below with a tip on; camera_3 at (-40, +10). Travel height: carriage at z 122. Setting the cap:
#    carriage at 58; the pipette in a well, likewise.
#  - One spot (protocol.md): fill 150 uL; OCP 30 min; LPR -10 to +10 mV about OCP at 0.167 mV/s; rest 5 min;
#    cyclic polarization from 50 mV below OCP, up at 0.167 mV/s (G61's 0.6 V/h) or 1 mV/s for screening, reversing
#    at 1 mA/cm2, back to E_corr; collect the liquid plus one 150 uL rinse into a tube; image the spot. 44 min a spot
#    at 1 mV/s, 107 at the G61 rate.
# The potentiostat is the one the lab has now: NuVant's EZstat Pro, lent by Dr. Porter (byu-vcl #231, DAL #221),
# 10 x 9.625 x 4 in (255 x 245 x 102 mm), 2.8 kg, +-1 A, +-25 V compliance, a 5-lead cell cable (nuvant.com, EZstat
# Pro page). It runs from NuVant's EZware on a Windows 7 PC, which is cabled to the CubXL's Pi (CLAUDE.md, #231).
# DAL's plan sized the bus for an EmStat Pico in a small box behind the deck; the EZstat stands beside the frame.
CORR = dict(deck_z=80.0, x0=-180.0, y0=-232.5, travel_z=122.0,
            stations=((185.0, 240.0), (210.0, 240.0), (235.0, 240.0), (260.0, 240.0)),
            tray=(170.0, 275.0, 220.0, 260.0), face=20.0, lid=26.0,
            stocks=((318.0, 101.0, "0.6 M"), (318.0, 134.0, "0.06 M"), (318.0, 167.0, "0.006 M"),
                    (318.0, 200.0, "water")),
            rinse=(60.0, 245.0), park=(90.0, 245.0), cup_top=45.0,
            tubes_x0=176.0, tubes_dx=12.0, tubes_y=(28.0, 46.0), tube_top=32.0,
            rack1=(291.3, 89.0), rack2=(108.0, 89.0), rack_dx=8.5, rack_dy=10.0, rack_top=66.0, tip_top=71.0,
            tip_len=35.0, waste=(335.0, 40.0), waste_top=50.0,
            pip=(55.0, 11.0), cam=(-40.0, 10.0), cap_d=20.0, cap_h=16.0, cap_el=4.5,
            ez=(255.0, 245.0, 102.0), ez_x=530.0)


def _cx(x):
    return CORR["x0"] + x


def _cy(y):
    return CORR["y0"] + y


def _cz(z):
    return CORR["deck_z"] + z


# The curve: illustrative, not measured. Nobody in the lab has run a corrosion spot yet (the EZstat Pro passed its
# first dummy-cell check, C1, on 2026-10-26: byu-vcl #291 via DAL #221). E_corr and i_corr are the published values
# DAL's README quotes for as-built LPBF AlSi10Mg in aerated 3.5 wt% NaCl against SCE, Wu et al. 2022
# (doi:10.3390/ma15248786): E_corr -0.81 V, i_corr 3.39e-7 A/cm2. The passive current, the pitting and repassivation
# potentials and the Tafel slopes are made up for the drawing.
CURVE = dict(E_corr=-0.81, i_corr=3.39e-7, i_pass=1.5e-6, E_pit=-0.705, E_rp=-0.775, i_rev=1e-3, ba=0.05, bc=0.12)


def _polarization():
    c = CURVE
    E0, i0 = c["E_corr"], c["i_corr"]

    def passive(E):
        ia = i0 * 10 ** ((E - E0) / c["ba"])
        return 1.0 / (1.0 / ia + 1.0 / c["i_pass"])

    def cath(E):
        return i0 * 10 ** (-(E - E0) / c["bc"])

    fwd_E = np.linspace(E0 - 0.05, c["E_pit"] + 0.04, 400)
    fwd_i = np.array([passive(E) + 1e-6 * 10 ** max(0.0, (E - c["E_pit"]) / 0.004) - cath(E) - 1e-6 * (E > c["E_pit"])
                      for E in fwd_E])
    # stop where the anodic current reaches the reversal, 1 mA/cm2
    k = int(np.argmax(fwd_i >= c["i_rev"])) or len(fwd_i) - 1
    fwd_E, fwd_i = fwd_E[:k + 1], fwd_i[:k + 1]
    E_rev = fwd_E[-1]
    b_back = (E_rev - c["E_rp"]) / 2.0            # falls two decades, to 10 uA/cm2, at E_rp
    back_E = np.linspace(E_rev, E0 + 0.012, 300)
    back_i = np.array([c["i_rev"] * 10 ** ((E - E_rev) / b_back) + passive(E) - cath(E) for E in back_E])
    E = np.concatenate([fwd_E, back_E])
    i = np.concatenate([fwd_i, back_i])
    return E, np.abs(i), len(fwd_E), E_rev


def _ocp():
    t = np.linspace(0, 30, 240)
    rng = np.random.default_rng(7)
    E = CURVE["E_corr"] + 0.055 * np.exp(-t / 5.0) + 0.0015 * np.convolve(rng.standard_normal(240), np.ones(5) / 5,
                                                                          mode="same")
    return t, E


_PE, _PI, _NFWD, _EREV = _polarization()
_OT, _OE = _ocp()


def _draw_corrosion_plot(sc, img, s):
    from PIL import ImageDraw
    from scene import font
    key = "cubxl_corrosion:"
    a = min(1.0, _gv(sc, key + "plot"))
    if a <= 0.02:
        return
    p_ocp, p_scan = _gv(sc, key + "ocp"), _gv(sc, key + "scan")
    W, H = img.size
    d = ImageDraw.Draw(img, "RGBA")
    al = int(255 * a)
    x0, y0, x1, y1 = W * 0.585, 46 * s, W - 10 * s, 46 * s + H * 0.47
    d.rounded_rectangle((x0, y0, x1, y1), 6 * s, fill=(255, 255, 255, int(236 * a)), outline=(150, 156, 164, al))
    ft, fs = font(13.5 * s, bold=True), font(11.5 * s)
    d.text((x0 + 10 * s, y0 + 6 * s), "EZstat Pro on S1: OCP, then cyclic polarization", font=ft, fill=(20, 20, 24, al))
    d.text((x0 + 10 * s, y1 - 33 * s), "ILLUSTRATIVE, not measured. E_corr, i_corr: Wu et al. 2022, as-built LPBF",
           font=fs, fill=(150, 40, 30, al))
    d.text((x0 + 10 * s, y1 - 18 * s), "AlSi10Mg, 3.5 wt% NaCl. E_pit, E_rp and slopes drawn for the example.",
           font=fs, fill=(150, 40, 30, al))
    # two panels sharing the potential axis: OCP against time, then E against log |i|
    py0, py1 = y0 + 42 * s, y1 - 58 * s
    ax0 = x0 + 52 * s
    split = ax0 + (x1 - ax0) * 0.30
    bx0, bx1 = split + 12 * s, x1 - 12 * s
    Emin, Emax = -0.89, -0.66

    def ey(E):
        return py1 - (E - Emin) / (Emax - Emin) * (py1 - py0)
    grid = (205, 210, 216, al)
    for E in (-0.85, -0.80, -0.75, -0.70):
        d.line([(ax0, ey(E)), (split, ey(E))], fill=grid, width=1)
        d.line([(bx0, ey(E)), (bx1, ey(E))], fill=grid, width=1)
        d.text((x0 + 8 * s, ey(E) - 7 * s), f"{E:.2f}", font=fs, fill=(80, 84, 90, al))
    d.text((x0 + 8 * s, py0 - 17 * s), "E, V vs SCE", font=fs, fill=(80, 84, 90, al))
    for xa, xb in ((ax0, split), (bx0, bx1)):
        d.rectangle((xa, py0, xb, py1), outline=(120, 124, 130, al))
    d.text((ax0 + 4 * s, py1 + 3 * s), "OCP, 0-30 min", font=fs, fill=(80, 84, 90, al))
    lmin, lmax = -8.0, -2.0

    def ix(i):
        return bx0 + (math.log10(max(i, 1e-12)) - lmin) / (lmax - lmin) * (bx1 - bx0)
    for L in (-8, -6, -4, -2):
        xx = ix(10.0 ** L)
        d.line([(xx, py0), (xx, py1)], fill=grid, width=1)
        if L > -8:
            d.text((xx - 12 * s, py1 + 3 * s), f"1e{L}", font=fs, fill=(80, 84, 90, al))
    d.text((bx0 + 2 * s, py0 - 17 * s), "|i|, A/cm2, log scale", font=fs, fill=(80, 84, 90, al))
    # OCP trace
    n = int(round(p_ocp * (len(_OT) - 1)))
    if n >= 1:
        pts = [(ax0 + t / 30.0 * (split - ax0), ey(E)) for t, E in zip(_OT[:n + 1], _OE[:n + 1])]
        d.line(pts, fill=(30, 60, 140, al), width=max(1, int(round(2 * s))))
    # polarization: forward up to the reversal, then back
    m = int(round(p_scan * (len(_PE) - 1)))
    if m >= 1:
        fwd = [(ix(i), ey(E)) for E, i in zip(_PE[:min(m, _NFWD - 1) + 1], _PI[:min(m, _NFWD - 1) + 1])]
        d.line(fwd, fill=(30, 60, 140, al), width=max(1, int(round(2 * s))))
        if m > _NFWD - 1:
            back = [(ix(i), ey(E)) for E, i in zip(_PE[_NFWD - 1:m + 1], _PI[_NFWD - 1:m + 1])]
            d.line(back, fill=(220, 110, 30, al), width=max(1, int(round(2 * s))))
        E_now, i_now = _PE[m], _PI[m]
        r = 3.5 * s
        d.ellipse((ix(i_now) - r, ey(E_now) - r, ix(i_now) + r, ey(E_now) + r), fill=(20, 20, 24, al))
    if p_scan >= 0.999:
        for E, lab, col in ((CURVE["E_pit"], "E_pit", (30, 60, 140)), (CURVE["E_rp"], "E_rp", (220, 110, 30)),
                            (CURVE["E_corr"], "E_corr", (60, 60, 66))):
            d.line([(bx0, ey(E)), (bx1, ey(E))], fill=(*col, int(150 * a)), width=1)
            d.text((bx1 - 50 * s, ey(E) - 15 * s), lab, font=fs, fill=(*col, al))


def cubxl_corrosion() -> Instrument:
    import equipment
    p = CORR
    W, D = equipment.CUBXL["W"], equipment.CUBXL["D"]
    inst = Instrument(
        "cubxl_corrosion", "Corrosion spots on the CubXL, with a potentiostat", "CubXL + NuVant EZstat Pro",
        (W + 70 + 30 + p["ez"][0], D, equipment.CUBXL["H"] + 50),
        "The CubXL from lab_models.equipment.cubxl() (#199); the corrosion deck, electrode cap and head as DAL PR #180 "
        "proposes them (alloy-corrosion/cubxl-setup.md, CubOS deck frame of Ben's 2026-10-02 calibration); NuVant's "
        "EZstat Pro (255 x 245 x 102 mm, nuvant.com) beside it, as in byu-vcl #231 / DAL #221",
        props=("cap", "tip", "tip2", "well", "tubefill", "led", "plot", "ocp", "scan"))
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
    dz = p["deck_z"]
    # ---- the deck: coupon tray with four stations
    tx0, tx1, ty0, ty1 = (_cx(p["tray"][0]), _cx(p["tray"][1]), _cy(p["tray"][2]), _cy(p["tray"][3]))
    face, lid = _cz(p["face"]), _cz(p["lid"])
    body.add("coupon tray", box(tx0, ty0, dz, tx1, ty1, face - 6), "pla_grey")
    lid_s = box(tx0, ty0, face, tx1, ty1, lid)
    for i, (sx, sy) in enumerate(p["stations"]):
        x, y = _cx(sx), _cy(sy)
        lid_s = lid_s.cut(cyl(8, 10, x=x, y=y, z=face - 1))
        body.add(f"coupon S{i + 1}", box(x - 8, y - 8, face - 6, x + 8, y + 8, face), "sample")
        body.add(f"O-ring S{i + 1}", tube(5.6, 3.0, 1.4, x=x, y=y, z=face), "pp_black")
        for sgn in (-1, 1):
            body.add(f"pad S{i + 1} {sgn:+d}", box(x + sgn * 11 - 1.5, y - 3, lid, x + sgn * 11 + 1.5, y + 3, lid + 0.6),
                     "brass")
    body.add("lids", lid_s, "pla_white")
    body.add("bus connector", box(tx0 + 40, ty1, dz + 6, tx0 + 80, ty1 + 6, face), "printer_black")
    # ---- stocks, cups, tubes, tip racks, tip waste
    hx = _cx(p["stocks"][0][0])
    body.add("stock holder", box(hx - 20, _cy(p["stocks"][0][1]) - 20, dz, hx + 20, _cy(p["stocks"][-1][1]) + 20, dz + 14),
             "pla_white")
    for i, (sx, sy, _) in enumerate(p["stocks"]):
        x, y = _cx(sx), _cy(sy)
        body.add(f"stock {i + 1}", tube(28, 25, 57, x=x, y=y, z=dz + 5).union(cyl(28, 2, x=x, y=y, z=dz + 5)), "glass")
        body.add(f"stock {i + 1} liquid", cyl(24.5, 36, x=x, y=y, z=dz + 7), "lab_nacl")
        if i > 0:                                   # the 0.6 M stock is open: the capper has its cap
            body.add(f"stock {i + 1} cap", cyl(28, 9, x=x, y=y, z=_cz(62)), "pp_black")
            body.add(f"stock {i + 1} disc", cyl(16, 1, x=x, y=y, z=_cz(71)), "steel")
    for name, (sx, sy) in (("rinse cup", p["rinse"]), ("park cup", p["park"])):
        x, y = _cx(sx), _cy(sy)
        body.add(name, tube(15, 12.6, _cz(p["cup_top"]) - dz - 2, x=x, y=y, z=dz + 2).union(cyl(15, 2, x=x, y=y, z=dz + 2)),
                 "glass")
        body.add(f"{name} liquid", cyl(12.4, 38, x=x, y=y, z=dz + 4), "lab_nacl")
    body.add("cup holder", box(_cx(p["rinse"][0]) - 14, _cy(p["rinse"][1]) - 12, dz, _cx(p["park"][0]) + 14,
                               _cy(p["park"][1]) + 12, dz + 8), "pla_white")
    xs = [p["tubes_x0"] + p["tubes_dx"] * k for k in range(8)]
    rx0, rx1 = _cx(xs[0]) - 6, _cx(xs[-1]) + 6
    ry0, ry1 = _cy(p["tubes_y"][0]) - 8, _cy(p["tubes_y"][1]) + 8
    plate = box(rx0, ry0, _cz(18), rx1, ry1, _cz(21))
    for x in xs:
        for y in p["tubes_y"]:
            plate = plate.cut(cyl(8.4, 6, x=_cx(x), y=_cy(y), z=_cz(17)))
            body.add(f"tube {x:.0f},{y:.0f}", tube(8, 6.6, 30, x=_cx(x), y=_cy(y), z=_cz(2)), "lab_tube")
    body.add("tube rack", box(rx0, ry0, dz, rx1, ry1, dz + 4).union(plate).union(
        box(rx0, ry0, dz, rx0 + 4, ry1, _cz(21))).union(box(rx1 - 4, ry0, dz, rx1, ry1, _cz(21))), "pla_white")
    tips = None
    for rk, (ax, ay) in (("rack 1", p["rack1"]), ("rack 2", p["rack2"])):
        xa, xb = _cx(ax - p["rack_dx"]), _cx(ax)
        y0r, y1r = _cy(ay), _cy(ay + 14 * p["rack_dy"])
        body.add(f"tip {rk}", box(xa - 6, y0r - 6, dz, xb + 6, y1r + 6, _cz(p["rack_top"])),
                 "printer_black" if rk == "rack 1" else "pla_white")
        for j in range(15):
            for xx in (xa, xb):
                if rk == "rack 1" and j == 0:      # A1 and A2 of Ben's rack: the two the clip uses
                    continue
                t = _cone(5.2, 1.0, p["tip_len"], x=xx, y=_cy(ay + j * p["rack_dy"]), z=_cz(p["tip_top"] - p["tip_len"]))
                tips = t if tips is None else tips.union(t)
    body.add("tips", tips, "lab_tip")
    wx, wy = _cx(p["waste"][0]), _cy(p["waste"][1])
    body.add("tip waste", tube(30, 27, p["waste_top"], x=wx, y=wy, z=dz).union(cyl(30, 2, x=wx, y=wy, z=dz)),
             "printer_grey")
    # ---- the potentiostat beside the frame, and its cell cable to the tray's back edge
    ew, ed, eh = p["ez"]
    ex = p["ez_x"]
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
    led = _piece(inst, "led")
    led.add("cell-on LED", _ycyl(7, 3, x=ex + ew / 2 - 30, y=60 - ed / 2 - 3, z=eh - 25), "glow")
    # ---- the head, as DAL plans it, modelled at CubOS x 0, y 0, carriage at travel height
    tools = _piece(inst, "tools")
    zr = _cz(p["travel_z"])                      # the carriage's reference height, CubOS z 122
    hx0, hy0 = _cx(0), _cy(0)
    tools.add("capper", cyl(40, 110, x=hx0, y=hy0, z=zr - 8), "printer_grey")
    tools.add("capper magnet", cyl(30, 8, x=hx0, y=hy0, z=zr - 16), "graphite")
    tools.add("capper bracket", box(hx0 - 15, hy0 + 18, zr + 50, hx0 + 15, hy0 + 26, zr + 95), "printer_black")
    px, py = hx0 + p["pip"][0], hy0 + p["pip"][1]
    tools.add("P20 pipette", cyl(34, 170, x=px, y=py, z=zr + 40), "printer_black")
    tools.add("P20 nozzle", _cone(8, 5, 40, x=px, y=py, z=zr), "printer_grey")
    cxm, cym = hx0 + p["cam"][0], hy0 + p["cam"][1]
    tools.add("camera_3", box(cxm - 12, cym - 12, zr + 20, cxm + 12, cym + 12, zr + 52), "printer_black")
    tools.add("camera lens", cyl(10, 6, x=cxm, y=cym, z=zr + 14), "glass")
    # ---- the electrode cap, modelled on the park cup
    cap = _piece(inst, "cap")
    kx, ky, kz = _cx(p["park"][0]), _cy(p["park"][1]), _cz(p["cup_top"])
    cap.add("cap body", cyl(p["cap_d"], p["cap_h"] - 1.5, x=kx, y=ky, z=kz), "pla_white")
    cap.add("steel disc", cyl(18, 1.5, x=kx, y=ky, z=kz + p["cap_h"] - 1.5), "steel")
    cap.add("Ag/AgCl reference", cyl(2, p["cap_h"] + p["cap_el"] - 2, x=kx, y=ky, z=kz - p["cap_el"]), "lab_agcl")
    coil = None
    for k in range(5):
        c = tube(5.2, 4.4, 0.45, x=kx, y=ky, z=kz - p["cap_el"] + 0.3 + k * 0.85)
        coil = c if coil is None else coil.union(c)
    cap.add("Pt coil", coil, "chrome")
    for sgn in (-1, 1):
        cap.add(f"pogo {sgn:+d}", cyl(1.4, 4, x=kx + sgn * 11, y=ky, z=kz - 3.5), "brass")
    # ---- tips the clip uses, the liquid in well S1 and in tube 1
    t1 = _piece(inst, "tip")
    a1x, a1y = _cx(p["rack1"][0]), _cy(p["rack1"][1])
    t1.add("tip A1", _cone(5.2, 1.0, p["tip_len"], x=a1x, y=a1y, z=_cz(p["tip_top"] - p["tip_len"])), "lab_tip")
    t2 = _piece(inst, "tip2")
    a2x = _cx(p["rack1"][0] - p["rack_dx"])
    t2.add("tip A2", _cone(5.2, 1.0, p["tip_len"], x=a2x, y=a1y, z=_cz(p["tip_top"] - p["tip_len"])), "lab_tip")
    s1x, s1y = _cx(p["stations"][0][0]), _cy(p["stations"][0][1])
    _piece(inst, "well").add("electrolyte in S1", cyl(7.6, 3.0, x=s1x, y=s1y, z=face + 0.05), "lab_nacl")
    _piece(inst, "tubefill").add("tube 1 liquid", cyl(6.2, 13, x=_cx(xs[0]), y=_cy(p["tubes_y"][0]), z=_cz(4)),
                                 "lab_nacl")

    # ---- the choreography: one timeline for the head and everything it carries
    def head_at(x, y):           # capper over (x, y); "pip" puts the pipette there instead
        return dict(x=x, y=y)

    def pip_at(x, y):
        return dict(x=x - p["pip"][0], y=y - p["pip"][1])
    TZ = p["travel_z"]
    tl = Timeline(dict(x=150.0, y=60.0, z=TZ, cap="park", tip="rack", tip2="rack", well=0.0, tube=0.0))
    xy = lambda a, b: max(0.35, math.hypot(b["x"] - a["x"], b["y"] - a["y"]) / 170.0)   # noqa: E731

    def move(**kw):
        s = tl.states[-1]
        tl.go(xy(s, kw), **kw)

    def z(zc, secs=None, **kw):
        tl.go(secs or max(0.25, abs(tl.states[-1]["z"] - zc) / 90.0), z=zc, **kw)
    s1, s2 = p["stations"][0], p["stations"][1]
    # 0: a tip
    move(**pip_at(*p["rack1"])); z(p["tip_top"]); z(TZ, tip="head"); tl.mark("tip")
    # 1: 150 uL of 0.6 M NaCl into S1
    move(**pip_at(p["stocks"][0][0], p["stocks"][0][1])); z(70); tl.go(0.35); z(TZ)
    move(**pip_at(*s1)); z(p["face"] + 3 + p["tip_len"]); tl.go(0.6, well=1.0); tl.mark("filled")
    # 2: tip off, cap from the park cup
    z(TZ); move(**pip_at(*p["waste"])); tl.go(0.35, tip="waste")
    move(**head_at(*p["park"])); z(p["cup_top"] + p["cap_h"] + 16); z(TZ, cap="head"); tl.mark("capped up")
    # 3: cap onto S1, head away
    move(**head_at(*s1)); z(p["lid"] + p["cap_h"] + 16); z(TZ, cap="S1"); move(x=340.0, y=290.0); tl.mark("cap on")
    # 6: cap off, rinsed, parked
    move(**head_at(*s1)); z(p["lid"] + p["cap_h"] + 16); z(TZ, cap="head")
    on_cup = p["cup_top"] + p["cap_h"] + 16          # the cap seated on a cup, its electrodes in the liquid
    move(**head_at(*p["rinse"])); z(on_cup); z(on_cup + 25, 0.3); z(on_cup, 0.3); z(TZ)
    move(**head_at(*p["park"])); z(p["cup_top"] + p["cap_h"] + 16); z(TZ, cap="park"); tl.mark("parked")
    # 7: a fresh tip; S1's liquid into tube 1, for ICP; tip off
    move(**pip_at(p["rack1"][0] - p["rack_dx"], p["rack1"][1])); z(p["tip_top"]); z(TZ, tip2="head")
    move(**pip_at(*s1)); z(p["face"] + 1 + p["tip_len"]); tl.go(0.6, well=0.0); z(TZ)
    move(**pip_at(xs[0], p["tubes_y"][0])); z(20 + p["tip_len"]); tl.go(0.5, tube=1.0); z(TZ)
    move(**pip_at(*p["waste"])); tl.go(0.35, tip2="waste"); tl.mark("collected")
    # 8: on to S2
    move(**pip_at(*s2)); tl.mark("next")

    cap_rest = {"park": (p["park"][0], p["park"][1], p["cup_top"]), "S1": (s1[0], s1[1], p["lid"])}

    def cap_off(s):              # where the cap is, as an offset from where it is modelled (on the park cup)
        if s["cap"] == "head":
            at = (s["x"], s["y"], s["z"] - 16 - p["cap_h"])
        else:
            at = cap_rest[s["cap"]]
        return (at[0] - p["park"][0], at[1] - p["park"][1], at[2] - p["cup_top"])

    def tip_off(s, key, home):
        if s[key] == "head":
            at = (s["x"] + p["pip"][0], s["y"] + p["pip"][1], s["z"] - p["tip_len"])
        elif s[key] == "waste":
            at = (p["waste"][0], p["waste"][1], 8.0)
        else:
            at = (home[0], home[1], p["tip_top"] - p["tip_len"])
        return (at[0] - home[0], at[1] - home[1], at[2] - (p["tip_top"] - p["tip_len"]))
    a2 = (p["rack1"][0] - p["rack_dx"], p["rack1"][1])
    inst.joints = {
        "gantry": Track(knots=tl.knots(lambda s: (0, s["y"], 0))),
        "carriage": Track(parent="gantry", knots=tl.knots(lambda s: (s["x"], 0, 0))),
        "tools": Track(parent="carriage", knots=tl.knots(lambda s: (0, 0, s["z"] - TZ))),
        "cap": Track(knots=tl.knots(cap_off)),
        "tip": Track(knots=tl.knots(lambda s: tip_off(s, "tip", p["rack1"]))),
        "tip2": Track(knots=tl.knots(lambda s: tip_off(s, "tip2", a2))),
        "well": Track(knots=tl.knots(lambda s: (0, 0, -4.0 * (1 - s["well"])))),
        "tubefill": Track(knots=tl.knots(lambda s: (0, 0, -14.0 * (1 - s["tube"])))),
        "led": Joint("fade"),
        "plot": Joint("slide", vec=(1, 0, 0)),
        "ocp": Joint("slide", vec=(1, 0, 0)),
        "scan": Joint("slide", vec=(1, 0, 0)),
    }
    head = ("gantry", "carriage", "tools", "cap", "tip", "tip2", "well", "tubefill")

    def seg(a, b, **extra):
        out = {k: (tl.v(a), tl.v(b)) for k in head}
        out.update(extra)
        return out
    inst.actions = [
        ("Four polished coupons under O-ring lids, face up on pogo pins (DAL PR #180's plan). The P20 on the CubXL's "
         "head takes a tip.", 2.6, seg("start", "tip")),
        ("It fills well S1 with 150 uL of 0.6 M NaCl (3.5 wt%) from the stocks, which the capper uncaps. The O-ring "
         "leaves 3 mm of the coupon wet: 0.071 cm2.", 3.4, seg("tip", "filled")),
        ("Tip off. The capper's magnet picks up the electrode cap: a leak-free 2 mm Ag/AgCl reference inside a coil "
         "of Pt wire, the counter.", 3.0, seg("filled", "capped up")),
        ("The cap goes on S1. Its pogo pins land on the RE and CE pads; the coupon's back is on the WE pin. The head "
         "is free.", 2.6, seg("capped up", "cap on")),
        ("The EZstat Pro beside the deck holds the cell at open circuit for 30 min: OCP settles to E_corr.", 3.2,
         {"led": (0.0, 1.0), "plot": (0.0, 1.0), "ocp": (0.0, 1.0)}),
        ("LPR, then a cyclic polarization at 1 mV/s: up from 50 mV below OCP, reversing at 1 mA/cm2, back to E_corr. "
         "44 min a spot at 1 mV/s.", 4.4, {"scan": (0.0, 1.0)}),
        ("The capper lifts the cap off, dips it in the rinse cup and parks it.", 3.4,
         {**seg("cap on", "parked"), "led": (1.0, 0.0)}),
        ("A fresh tip takes the well's liquid to tube 1, for ICP: dissolved Al and Mg, element by element.", 4.2,
         seg("parked", "collected")),
        ("On to S2. At 44 min a spot, a 12 h night screens 16 spots; at the G61 rate, 6.", 2.4,
         seg("collected", "next")),
    ]
    inst.labels = [("electrode cap,\nparked", (kx, ky, kz + 18), (0.10, 0.30)),
                   ("coupon tray S1-S4", (_cx(222), ty0, lid), (0.12, 0.55)),
                   ("NaCl stocks", (hx, _cy(150), _cz(60)), (0.40, 0.80)),
                   ("NuVant EZstat Pro", (ex - 40, 60 - ed / 2, eh), (0.86, 0.70))]
    inst.cam = (0.55, -1.5, 1.25)
    inst.framing = (0.80, 0.30)
    inst.notes = ["Deck, cap and head: DAL PR #180's plan, not yet built", "Curve: illustrative"]
    return inst


# deck close-ups for the clip (absolute, model frame); index = action number
_DECK = ((330.0, -560.0, 780.0), (20.0, -70.0, 90.0))
_CELL = ((300.0, -1025.0, 865.0), (300.0, 40.0, 120.0))
_OVER = ((560.0, -1450.0, 1250.0), (60.0, 0.0, 180.0))
CAMS["instruments/cubxl_corrosion"] = {0: _DECK, 4: _CELL, 6: _DECK, 8: _OVER}
PLOTS["instruments/cubxl_corrosion"] = _draw_corrosion_plot


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
    foam = box(bx_ - b["W"] / 2 + 5, yf + 5, 5, bx_ + b["W"] / 2 - 5, yf + b["D"] - 5, b["H"] - 40).cut(
        box(bx_ - 95, by_ - 40, 12, bx_ + 95, by_ + 40, b["H"]))
    body.add("foam insert", foam, "lab_foam")
    lid = _piece(inst, "lid")
    lid.add("box lid", box(bx_ - b["W"] / 2, yf, b["H"] - 5, bx_ + b["W"] / 2, yf + b["D"], b["H"]), "lab_kraft")
    lid.add("lid sides", box(bx_ - b["W"] / 2, yf, b["H"] - 40, bx_ + b["W"] / 2, yf + b["D"], b["H"] - 5).cut(
        box(bx_ - b["W"] / 2 + 5, yf + 5, b["H"] - 41, bx_ + b["W"] / 2 - 5, yf + b["D"] - 5, b["H"] - 4)), "lab_kraft")
    lid.add("lid foam", box(bx_ - b["W"] / 2 + 6, yf + 6, b["H"] - 35, bx_ + b["W"] / 2 - 6, yf + b["D"] - 6,
                            b["H"] - 5), "lab_foam")
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
    bag = _piece(inst, "bag")
    bag.add("liner bag", box(jx - 42, jy - 42, jz - 3, jx + 42, jy + 42, jz + j["h"] + 30).cut(
        box(jx - 40, jy - 40, jz - 1, jx + 40, jy + 40, jz + j["h"] + 31)), "lab_bag")
    bag.add("bag mouth", box(jx - 42, jy - 3, jz + j["h"] + 30, jx + 42, jy + 3, jz + j["h"] + 52), "lab_bag")
    lw, ll = P["label"]
    ship = _piece(inst, "shiplabel")
    ship.add("4 x 6 label", box(bx_ - lw / 2, by_ - ll / 2, b["H"], bx_ + lw / 2, by_ + ll / 2, b["H"] + 0.6),
             "lab_label")
    ship.add("label barcode", box(bx_ - 35, by_ - 60, b["H"] + 0.6, bx_ + 35, by_ - 30, b["H"] + 0.9), "inst_black")
    ship.add("label text", box(bx_ - 40, by_ + 10, b["H"] + 0.6, bx_ + 20, by_ + 60, b["H"] + 0.8), "inst_grey")

    # ---- choreography on one timeline
    mid = jz + j["h"] / 2                                  # the jar's tilt pivot: the middle of its axis
    ap_c = (ax, cy0, 95 + 12.5 + j["d"] / 2)               # the jar's axis, lying in the AP380's cradle
    bag_at = (sx_, yf - 80, 4.0)                           # standing on the bag stand, the bag's mouth over the jaw
    pocket = (bx_, by_, 12 + 2 + j["d"] / 2)               # the jar's axis, lying in the foam pocket
    tl = Timeline(dict(p=(jx - 260, jy - 80, jz + 220), tilt=0.0, spin=0.0, ship=0.0))

    def to(secs, x, y, z, **kw):
        tl.go(secs, p=(x, y, z), **kw)
    lie = lambda c: c[2] - (mid - jz)                      # noqa: E731  the jar's base z when its axis is at c lying
    to(1.0, jx, jy, jz + 80); to(0.6, jx, jy, jz); tl.mark("nested")
    to(0.5, jx, jy, jz + 160); to(1.0, ap_c[0], ap_c[1], lie(ap_c) + 160, tilt=90.0)
    to(0.6, ap_c[0], ap_c[1], lie(ap_c)); tl.mark("in AP380")
    tl.go(2.0, spin=360.0); tl.mark("labelled")
    to(0.6, ap_c[0], ap_c[1], lie(ap_c) + 160); to(1.0, bag_at[0], bag_at[1], bag_at[2] + 160, tilt=0.0)
    to(0.6, *bag_at); tl.mark("at sealer")
    tl.go(1.6); tl.mark("sealed")
    to(0.5, bag_at[0], bag_at[1], bag_at[2] + 200); to(1.0, pocket[0], pocket[1], lie(pocket) + 150, tilt=90.0)
    to(0.6, pocket[0], pocket[1], lie(pocket)); tl.mark("boxed")
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
        "bag": Joint("fade", parent="jartilt"),
        "stripslide": Joint("slide", vec=(0, -60, 0)),
        "strip": Joint("fade", parent="stripslide"),
        "press": Joint("hinge", axis=(1, 0, 0), pivot=(ax, yf + a["D"] - 200, pz), deg=-14.0, v0=1.0),
        "arm": Joint("hinge", axis=(1, 0, 0), pivot=(sx_, yf + se["D"], 126), deg=-35.0, v0=1.0),
        "lid": Joint("hinge", axis=(1, 0, 0), pivot=(bx_, yf + b["D"], b["H"] - 40), deg=105.0, v0=1.0),
        "shiplabel": Track(knots=tl.knots(ship_off)),
        "inset_jar": Joint("slide", vec=(1, 0, 0)),
        "inset_ship": Joint("slide", vec=(1, 0, 0)),
    }
    track = ("jarpos", "jartilt", "jar", "shiplabel")

    def seg(a_, b_, **extra):
        out = {k: (tl.v(a_), tl.v(b_)) for k in track}
        out.update(extra)
        return out
    inst.actions = [
        ("A 250 mL jar of powder goes into the printed nest.", 1.8, seg("start", "nested")),
        ("The LX500c prints its label: sample ID, alloy, mass, date and a QR code. The AP380 takes such labels "
         "die-cut on a roll.", 2.4, {"stripslide": (0.0, 1.0), "strip": (0.0, 1.0), "inset_jar": (0.0, 1.0)}),
        ("The jar goes into the AP380, lying down on its rollers; the pressure arm comes down.", 2.6,
         {**seg("nested", "in AP380"), "strip": (1.0, 0.0), "press": (1.0, 0.0)}),
        ("One press of the foot switch: the rollers turn the jar once and the label wraps on.", 2.2,
         {**seg("in AP380", "labelled"), "jarlabel": (0.0, 1.0)}),
        ("Out, and into a clear liner bag, its mouth across the H-190's jaw.", 2.4,
         {**seg("labelled", "at sealer"), "press": (0.0, 1.0), "bag": (0.0, 1.0), "inset_jar": (1.0, 0.0)}),
        ("The impulse sealer closes the bag: a 12 in seal.", 1.8, {**seg("at sealer", "sealed"), "arm": (1.0, 0.0)}),
        ("Into the foam insert's cut-out, lying down.", 2.2, {**seg("sealed", "boxed"), "arm": (0.0, 1.0)}),
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
        "load": Joint("path", path=((bw / 2 + 160, 0.0, bh - 30), (bw / 2 + 160, 0.0, bh + 120),
                                    (tcx + 60, yf - 260, tz + 80), (tcx, yf - 120, tz + 40), (tcx, tcy, tz + 25),
                                    (tcx, tcy, tz))),
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
        ("A steel substrate goes from the shelf onto the 175 x 175 mm worktable.", 2.2, {"load": (0.0, 1.0)}),
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
    # ---- the O2-Dr.HIP, centred on the tray: drum housing on the left, cabinet on the right, plinth, red band
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
    over = _piece(inst, "over")
    e = 14.0                                             # proud of the HIP's faces, so they don't fight
    over.add("too tall", box(-W / 2 - e, -D / 2 - 40, h["h_max"], W / 2 + e, D / 2 + e, H + e), "lab_over")
    over.add("too deep, front", box(-W / 2 - e, -D / 2 - 40, 0, W / 2 + e, -td / 2, h["h_max"]), "lab_over")
    over.add("too deep, back", box(-W / 2 - e, td / 2, 0, W / 2 + e, D / 2 + e, h["h_max"]), "lab_over")
    inst.joints = {
        "env": Joint("fade"),
        "hipdrop": Joint("path", path=((0, 0, 1500.0), (0, 0, 300.0), (0, 0, 0)), v0=1.0),
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
