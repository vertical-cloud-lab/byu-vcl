"""2-D insets for the doser's outlet (ods_c_gravity, capture_map): a cutaway of the inside, and what the capillary does
to the pulses. Drawn to explain the idea, not simulated; the numbers are the README's estimates.

No taper (Sterling, 2026-10-07): the tube keeps PR 176's storage-auger inside as tested (open 21 mm bore at the cap end,
an 8-turn flight of 10.4 mm pitch on an 8 mm core in the outlet third, and the v4 outlet: a 12 mm funnel to a 3 mm
annular exit round the core's tip). A screw-on capillary keeps that exit's 3 mm bore, smooth, for 35 mm (doser_cad.NOSE_OUT
/ NOSE_IN). Dose per turn: PR 176's DEM gives about 320 mm³ of bulk powder per turn, one pulse per turn (about 380 mg of
1.2 g/cm³ granules, so one pulse every 38 s at 10 mg/s). The capillary holds about 250 mm³ (about 300 mg), close to one
pulse; vibrated and kept full, it discharges at a rate its vibration sets, so the flight only has to keep it topped up.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

import doser_cad as D
from gifkit import font

NAVY, ORANGE, INKC, MUTEDC = (0, 46, 93), (235, 104, 52), (20, 22, 28), (90, 96, 106)
STEEL, STEEL_DK, POWDER = (176, 180, 188), (120, 124, 132), (236, 236, 240)

OLD_DOSE, OLD_PERIOD = 380.0, 38.0       # mg per pulse, s between pulses (PR 176 auger at 10 mg/s)
CAP_HOLD = 300.0                         # mg the full 3 mm x 35 mm capillary holds (1.2 g/cm3 granules)


def _panel(w, h, title):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 10, fill=(250, 251, 253, 238), outline=(170, 176, 186, 255), width=2)
    d.text((10, 6), title, font=font(max(11, int(h * 0.070)), bold=True), fill=INKC)
    return im, d


def nose_inset(w, h):
    """Longitudinal cutaway: the flight's last turns, the v4 outlet as tested, and the same-bore capillary."""
    im, d = _panel(w, h, "Inside the outlet")
    fl = font(max(10, int(h * 0.056)))
    res_l = 30.0                                             # mm of the flight shown, behind the outlet face
    span = res_l + D.NOSE_L + 3.0
    k = (w * 0.92) / span                                    # px per mm
    x0, cy = w * 0.04, h * 0.52

    def X(s):                                                # s: mm along the axis, 0 at the outlet face
        return x0 + (s + res_l) * k

    out = [(-res_l, 12.5)] + D.NOSE_OUT
    inn = [(-res_l, 10.5), (-12.0, 10.5), (0.0, 1.5)] + D.NOSE_IN
    for sgn in (1, -1):                                      # the wall, above and below the axis
        poly = [(X(s), cy - sgn * r * k) for s, r in out] + [(X(s), cy - sgn * r * k) for s, r in reversed(inn)]
        d.polygon(poly, fill=STEEL, outline=STEEL_DK)
    d.line((X(0), cy - 12.5 * k, X(0), cy - 1.5 * k), fill=STEEL_DK, width=1)   # the thread joint
    d.line((X(0), cy + 1.5 * k, X(0), cy + 12.5 * k), fill=STEEL_DK, width=1)
    # the core: 8 mm, with its conical tip in the funnel (to 0.8 mm at the face)
    d.polygon([(X(-res_l), cy - 4 * k), (X(-12.0), cy - 4 * k), (X(0.0), cy - 0.4 * k), (X(0.0), cy + 0.4 * k),
               (X(-12.0), cy + 4 * k), (X(-res_l), cy + 4 * k)], fill=STEEL_DK)
    rng = np.random.default_rng(4)

    def bore(s):
        return float(np.interp(s, [p[0] for p in inn], [p[1] for p in inn]))

    def core(s):
        return float(np.interp(s, [-res_l, -12.0, 0.0], [4.0, 4.0, 0.4]))

    # granules: in the lower part of each flight pocket and the funnel, the capillary full, a thin stream out of the tip
    for _ in range(int(span * 7)):
        s = rng.uniform(-res_l, D.NOSE_L + 3.0)
        if s > D.NOSE_L:
            px, py = X(s), cy + 0.4 * k + (s - D.NOSE_L) ** 1.6 * 0.5 * k + rng.normal(0, 0.25) * k
        elif s > 0:
            px, py = X(s), cy + rng.uniform(-0.8, 0.9) * 1.5 * k
        else:
            lo, hi = core(s), bore(s)
            if hi - lo < 0.3:
                continue
            px, py = X(s), cy + rng.uniform(lo + 0.2, lo + 0.2 + 0.85 * (hi - lo)) * k
        d.ellipse((px - 1.2, py - 1.2, px + 1.2, py + 1.2), fill=POWDER, outline=(140, 140, 146))
    # the flight: PR 176's single start, 10.4 mm pitch, from the core to the wall, following the funnel at the end
    for s in np.arange(-res_l + 1.0, 0.0, 10.416 / 2):
        for sgn in (1, -1):
            d.line((X(s), cy - sgn * bore(s) * k, X(s + 2.6), cy - sgn * core(s + 2.6) * k), fill=NAVY, width=2)
    top, bot = cy - 12.5 * k, cy + 12.5 * k

    def put(text, x, y, anchor="mm"):
        d.text((x, y), text, font=fl, fill=INKC, anchor=anchor)
    put("flight, PR 176:", X(-res_l / 2 - 3), top - fl.size * 2.1)
    put("10.4 mm pitch", X(-res_l / 2 - 3), top - fl.size * 0.9)
    put("v4 outlet, as tested", X(-6.0), bot + fl.size * 0.9)
    put("capillary: v4's own", w - 8, cy - 2.5 * k - fl.size * 3.0, "rm")
    put("3 mm bore, smooth, vibrated", w - 8, cy - 2.5 * k - fl.size * 1.8, "rm")
    d.text((10, h - fl.size - 8), "holds ~300 mg, about one pulse", font=fl, fill=MUTEDC)
    return im


def pulse_inset(w, h):
    """Cumulative dose over a minute at 10 mg/s: PR 176's flight alone, and out of the full, vibrated capillary."""
    im, d = _panel(w, h, "Dose over a minute, 10 mg/s")
    fl = font(max(10, int(h * 0.056)))
    x0, x1, y0, y1 = w * 0.15, w * 0.95, h * 0.17, h * 0.64
    tmax, mmax = 60.0, 800.0
    X = lambda t: x0 + (x1 - x0) * t / tmax
    Y = lambda m: y1 - (y1 - y0) * m / mmax
    d.line((x0, y1, x1, y1), fill=NAVY, width=2)
    d.line((x0, y0, x0, y1), fill=NAVY, width=2)
    for m in (0, 400, 800):
        d.text((x0 - 5, Y(m)), f"{m}", font=fl, fill=MUTEDC, anchor="rm")
    d.text((x1, y1 + 3), "60 s", font=fl, fill=MUTEDC, anchor="ra")
    d.text((x0 + 6, y0 - 2), "mg", font=fl, fill=MUTEDC, anchor="ls")
    for t in np.arange(0, tmax, 2.0):                        # target, dashed
        d.line((X(t), Y(10 * t), X(t + 1.0), Y(10 * (t + 1.0))), fill=(150, 150, 150), width=2)
    pts, m = [(X(0), Y(0))], 0.0                             # the flight alone: one pulse a turn
    for tk in np.arange(19.0, tmax, OLD_PERIOD):
        pts += [(X(tk), Y(m)), (X(tk), Y(m + OLD_DOSE))]
        m += OLD_DOSE
    pts.append((X(tmax), Y(m)))
    d.line(pts, fill=ORANGE, width=3)
    ts = np.linspace(0.0, tmax, 120)                         # out of the capillary: the vibration's rate, a small ripple
    d.line([(X(t), Y(10 * t + 6 * math.sin(2 * math.pi * t / OLD_PERIOD))) for t in ts], fill=NAVY, width=2)
    ly = y1 + fl.size + 6
    for text, c in ((f"flight alone: {OLD_DOSE:.0f} mg every {OLD_PERIOD:.0f} s", ORANGE),
                    ("out of the full capillary:", NAVY),
                    ("   the vibration sets the rate", None),
                    ("target", (150, 150, 150))):
        if c:
            d.rectangle((10, ly + fl.size * 0.4, 22, ly + fl.size * 0.4 + 4), fill=c)
        d.text((28, ly), text, font=fl, fill=INKC)
        ly += fl.size + 3
    return im


if __name__ == "__main__":                      # preview: python nose_insets.py -> /tmp/nose_insets.png
    # (out/nose_insets.png, the README figure, is the same two panels at 690 x 566 each)
    w, h = int(1280 * 0.27), int(1280 * 0.27 * 0.82)       # InsetScene's size at 1280 x 720
    sheet = Image.new("RGBA", (2 * w + 15, h + 10), (40, 44, 52, 255))
    sheet.alpha_composite(nose_inset(w, h), (5, 5))
    sheet.alpha_composite(pulse_inset(w, h), (w + 10, 5))
    sheet.save("/tmp/nose_insets.png")
