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
        ("On to S2. Four coupons, two wells each, make eight spots a tray load: one night at the screening rate.", 2.4,
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


# ===================================================================================================== registry
REGISTRY = {"cubxl_corrosion": cubxl_corrosion}
