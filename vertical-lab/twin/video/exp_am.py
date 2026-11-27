"""The AM module: one laser track over a powder bed, the melt pool's shape and temperature field, the thermal history
of a point under the track, and the numbers the twin takes from the model (twin/video/exp_am.py).

    AMModule().frame(t)      0 <= t <= AMModule.DURATION

What is what on screen:

* **The temperature field, the melt pool's outline and the thermal history** are the twin's own melt-pool model for
  the alloy followed, at the settings of the cube the tensile blanks are printed beside (exp_data.melt_pool:
  truth_al.AlTruth.melt_pool, i.e. Rosenthal's moving point source of twin/physics.py with this alloy's conductivity,
  density, liquidus and absorptivity). The field is steady in the frame moving with the laser, so the picture from
  above is that one field carried along the track; the colour scale stops at the boiling point because a point
  source is singular at its origin.
* **This is the twin's stand-in for Thermo-Calc's AM Module, not Thermo-Calc output**, and the segment says so the
  whole time it is on screen. No run of round 3b bought the node (exp_data.sim_kinds: every simulation call in its
  committed event logs is the open-database CALPHAD node); the same model sits inside the twin's truth, where
  ``build`` turns its width, depth and cooling rate into a build's porosity and cell size.
* **The powder bed, the scanned tracks, the powder layer and the bead in the section** are drawn to explain
  (illustrative): particle sizes are the lot's sieved cut, the tracks lie at the hatch spacing, nothing else about
  them is computed.
* **The settings are example settings** (the middle of the print segment's grid), not the campaign's.

The laser's 0.1 ms is one second of video (``K``): the clock on screen says how much slower that is.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

from . import exp_data as X
from . import exp_draw as G
from . import style as St
from .exp_draw import Axes, Canvas, Segment, fmt, ramp
from .style import CAMP, INK, INK2, mix, px

S = St.S
METAL = (104, 116, 138)          # consolidated metal in the two views
METAL_DARK = (58, 66, 82)        # solid metal under the surface (the section)
BED_BG = (22, 25, 31)            # between the powder particles
WHITE = (255, 255, 255)


# ------------------------------------------------------------------------------------------------- text that fades
def fade_text(cv: Canvas) -> Canvas:
    """Kept for its callers: exp_draw.Canvas.text now fades a text itself (through a mask of its glyphs), which this
    module first had to do on its own."""
    return cv


# ------------------------------------------------------------------------------------------------- layers
def _particles(w: float, h: float, dmin: float, dmax: float, seed: int, tries: int = 5200) -> list:
    """Circles (x, y, r) that do not overlap, sizes between dmin and dmax (random sequential placement; the late
    tries are small ones that fill the gaps). Illustrative: a picture of a powder bed, not a packing model."""
    rng = np.random.default_rng(seed)
    xs, ys, rs = [], [], []
    for k in range(tries):
        d = float(np.clip(rng.lognormal(math.log(0.5 * (dmin + dmax) * 0.9), 0.3), dmin, dmax))
        if k > tries * 0.55:
            d = dmin * (1.0 + 0.3 * rng.random())
        r = d / 2.0
        x, y = rng.uniform(-r, w + r), rng.uniform(-r, h + r)
        if xs:
            ax, ay, ar = np.asarray(xs), np.asarray(ys), np.asarray(rs)
            if np.any((ax - x) ** 2 + (ay - y) ** 2 < (ar + r - 1.0) ** 2):
                continue
        xs.append(x)
        ys.append(y)
        rs.append(r)
    return list(zip(xs, ys, rs))


def _spheres(parts: list, w: float, h: float, k: int = 2, bg=BED_BG) -> Image.Image:
    """The particles as shaded spheres on a w x h (design units) picture."""
    W_, H_ = max(1, int(round(w * S))), max(1, int(round(h * S)))
    im = Image.new("RGB", (W_ * k, H_ * k), bg)
    d = ImageDraw.Draw(im)
    f = S * k
    for x, y, r in sorted(parts, key=lambda p: -p[2]):
        d.ellipse(((x - r) * f, (y - r) * f, (x + r) * f, (y + r) * f), fill=(96, 102, 114), outline=(58, 62, 72),
                  width=max(1, int(f)))
        d.ellipse(((x - 0.80 * r) * f, (y - 0.84 * r) * f, (x + 0.60 * r) * f, (y + 0.56 * r) * f),
                  fill=(128, 134, 146))
        d.ellipse(((x - 0.58 * r) * f, (y - 0.64 * r) * f, (x + 0.16 * r) * f, (y + 0.10 * r) * f),
                  fill=(160, 166, 178))
        d.ellipse(((x - 0.42 * r) * f, (y - 0.48 * r) * f, (x - 0.12 * r) * f, (y - 0.18 * r) * f),
                  fill=(204, 208, 218))
    return im.resize((W_, H_), Image.LANCZOS)


def _band(w: float, half: float, direction: int, k: int = 2) -> Image.Image:
    """A consolidated track seen from above, w long and 2 x half wide (design units): a bead lighter along its
    centreline, with the ripples a melt pool leaves behind it (open towards the direction of travel)."""
    W_, H_ = max(1, int(round(w * S))) * k, max(1, int(round(2 * half * S))) * k
    f = S * k
    yy = (np.arange(H_) + 0.5) / H_ * 2 - 1
    shade = 0.74 + 0.30 * np.cos(yy * math.pi / 2) ** 1.5
    col = np.clip(np.outer(shade, np.array(METAL, float)), 0, 255).astype(np.uint8)
    im = Image.fromarray(np.repeat(col[:, None, :], W_, 1))
    d = ImageDraw.Draw(im)
    dys = np.linspace(-half, half, 25)
    bow = 0.62 * half
    step = 21.0
    n = int(w / step) + 6
    for i in range(-3, n):
        x0 = i * step
        pts = [((x0 + direction * bow * (dy / half) ** 2) * f, (dy + half) * f) for dy in dys]
        d.line(pts, fill=(70, 80, 98), width=max(1, int(1.2 * f)))
        d.line([(x + 1.6 * f * direction, y) for x, y in pts], fill=(142, 154, 176), width=max(1, int(0.9 * f)))
    d.line([(0, 0), (W_, 0)], fill=(52, 60, 74), width=max(2, int(2 * f)))
    d.line([(0, H_ - 1), (W_, H_ - 1)], fill=(52, 60, 74), width=max(2, int(2 * f)))
    return im.resize((W_ // k, H_ // k), Image.LANCZOS)


class _Scale:
    """Temperature to colour and opacity: the square root of the way from the plate's temperature to the boiling
    point (so the cool tail reads apart from nothing); clear near the plate's temperature, opaque from the liquidus,
    so the bed shows through the cooling tail."""

    def __init__(self, T0: float, Tb: float, Tl: float):
        self.T0, self.Tb = float(T0), float(Tb)
        self.a_lo, self.a_hi = self.T0 + 90.0, float(Tl)

    def u(self, T):
        return np.sqrt(np.clip((np.asarray(T, float) - self.T0) / (self.Tb - self.T0), 0.0, 1.0))

    def rgb(self, T) -> tuple:
        return tuple(int(v) for v in G.LUT_HEAT[int(round(float(self.u(T)) * 255))])

    def rgba(self, T: np.ndarray) -> np.ndarray:
        al = np.clip((T - self.a_lo) / (self.a_hi - self.a_lo), 0.0, 1.0)
        al = 0.94 * al * al * (3 - 2 * al)
        return np.dstack([G.LUT_HEAT[(self.u(T) * 255).astype(np.uint8)], (al * 255).astype(np.uint8)])


def _contour(field: np.ndarray, level: float, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
    """The longest iso-line of a field at ``level`` as (x, y) in the units of its axes."""
    from skimage import measure
    cs = measure.find_contours(np.minimum(field, level * 4.0), level)
    if not cs:
        return np.zeros((0, 2))
    c = max(cs, key=len)
    r, q = c[:, 0], c[:, 1]
    return np.stack([np.interp(q, np.arange(len(xs)), xs), np.interp(r, np.arange(len(ys)), ys)], 1)


def _paste_rgba(dst: Image.Image, src: Image.Image, X_: int, Y_: int):
    """An RGBA picture onto dst with its top left at (X_, Y_) in pixels, only the part that lands on dst."""
    x0, y0 = max(0, X_), max(0, Y_)
    x1, y1 = min(dst.width, X_ + src.width), min(dst.height, Y_ + src.height)
    if x1 <= x0 or y1 <= y0:
        return
    part = src.crop((x0 - X_, y0 - Y_, x1 - X_, y1 - Y_))
    dst.paste(part, (x0, y0), part)


def _pill(cv: Canvas, x: float, y: float, s: str, size: float = 17, anchor: str = "l", a: float = 1.0,
          bold: bool = False):
    """A label on a dark pill (legible over the field and the bed). (x, y) is its left or right end, mid-height."""
    w = cv.text_w(s, size, bold=bold, cond=True) + 18
    h = size * 1.62
    if anchor == "r":
        x -= w
    elif anchor == "m":
        x -= w / 2
    cv.rect((x, y - h / 2, x + w, y + h / 2), fill=(10, 12, 16, 226), radius=h / 2, a=a)
    cv.text(x + 9, y, s, size, bold=bold, cond=True, fill=INK, anchor="lm", a=a)
    return w


def _dim(cv: Canvas, p0: tuple, p1: tuple, a: float = 1.0, fill=WHITE, tick: float = 7.0):
    """A dimension line between two points with a tick across each end."""
    if a <= 0.004:
        return
    cv.line([p0, p1], fill, 2, a)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]) + math.pi / 2
    dx, dy = tick * math.cos(ang), tick * math.sin(ang)
    for p in (p0, p1):
        cv.line([(p[0] - dx, p[1] - dy), (p[0] + dx, p[1] + dy)], fill, 2, a)


# ------------------------------------------------------------------------------------------------- the segment
class AMModule(Segment):
    key = "am"
    title = "The AM module: one laser track"
    campaign = "flaime_al"
    nodes = ("calphad",)
    done = ("composition",)
    DURATION = 28.0
    VIEW = (78, 200, 878, 620)        # the bed from above; UM design units per micrometre
    UM = 1.0
    Y1V, XPV = 140.0, 330.0           # in the view: the first track's centreline, and the probe on it
    K = 0.1                           # milliseconds of the laser's time per second of video
    T_PROBE = 4.9                     # the laser is over the probe
    T_PASS2 = 14.2                    # the next track starts, one hatch spacing over, the other way
    SEC = (962, 204, 1842, 426)       # the centre plane; US design units per micrometre, AIR units above the surface
    US, AIR, XA = 1.25, 44.0, -520.0
    HIST = (1066, 522, 1816, 686)
    T_END_MS = 0.9                    # the history is drawn to here
    T_TAKES = 14.6
    T_NOT_TC = 20.5

    def __init__(self):
        super().__init__()
        a = X.alloy("flaime_al")
        self.alloy = a
        mp = a.melt_pool()
        self.mp = mp
        self.tw, self.proc = mp["twin"], mp["proc"]
        self.f = X.load_facts()
        self.v = float(self.proc["v_mm_s"])                       # mm/s = micrometres per millisecond
        self.vs = self.v * self.K * self.UM                       # design units per second of video
        self.slow = 1000.0 / self.K                               # how many times slower than life
        self.half = 0.5 * self.tw["W_um"] * self.UM
        self.hatch = float(self.proc["h_um"]) * self.UM
        self.scale = _Scale(mp["T0_C"], mp["boil_C"], mp["liquidus_C"])
        self.layers = mp["probe_um"] / float(self.proc["t_um"])
        t, h = mp["t_ms"], mp["hist_C"]
        keep = t <= self.T_END_MS + 1e-9
        self.ht, self.hh = t[keep], h[keep]
        self.i_peak = int(np.argmax(self.hh))
        self.i_liq = mp["i_liquidus"] if mp["i_liquidus"] is not None and mp["i_liquidus"] < len(self.ht) else None
        up = np.nonzero(self.hh[:self.i_peak + 1] >= mp["liquidus_C"])[0]
        self.i_up = int(up[0]) if len(up) else None
        self.molten_ms = None if self.i_up is None or self.i_liq is None else float(self.ht[self.i_liq] -
                                                                                    self.ht[self.i_up])
        self.axH = Axes(self.HIST, (float(self.ht[0]), self.T_END_MS),
                        (0.0, math.ceil(mp["hist_peak_C"] * 1.12 / 200.0) * 200.0), "", "temperature, °C",
                        xticks=[v for v in (-0.2, 0.0, 0.2, 0.4, 0.6, 0.8) if self.ht[0] <= v <= self.T_END_MS],
                        yticks=St.nice_ticks(0.0, math.ceil(mp["hist_peak_C"] * 1.12 / 200.0) * 200.0, 4))
        self._ready = False
        n_l = self.layers
        lay = f"{n_l:.0f} layers" if abs(n_l - round(n_l)) < 1e-6 and round(n_l) != 1 else f"{mp['probe_um']:.0f} µm"
        self.lay_words = lay
        cool_probe = mp["hist_cool_K_s"]
        self.captions = [
            (0.5, 4.6, f"One laser track over the powder bed, shown {fmt(self.slow)} times slower. The colours are "
                       f"the temperature field of the twin's melt-pool model for this alloy."),
            (self.T_PROBE, 13.9, f"A point {lay} down melts again as the track passes over it, then cools through "
                                 f"the liquidus at {cool_probe / 1e6:.1f} million kelvin a second."),
            (self.T_TAKES, 20.2, "The twin takes five numbers from this model: the pool's width and depth, a "
                                 "lack-of-fusion index, a keyhole index and the cooling rate."),
            (self.T_NOT_TC, 27.6, "This is the twin's stand-in for Thermo-Calc's AM Module, not Thermo-Calc output. "
                                  "No run in round 3b bought this node."),
        ]
        self.marks = {"am.track": self.T_PROBE - (self.XPV + 40.0) / self.vs, "am.section": 3.0,
                      "am.history": self.T_PROBE, "am.takes": self.T_TAKES, "am.not_tc": self.T_NOT_TC}
        self.sources = [
            ("sim", "temperature field, melt-pool outline, thermal history, width, depth, indices, cooling rate: the "
                    "twin's melt-pool model (Rosenthal's point source, twin/physics.py and truth_al.AlTruth.melt_pool) "
                    "for the alloy followed, at the middle setting of the print grid"),
            ("illus", "the powder bed, the scanned tracks and their ripples, the powder layer and the bead in the "
                      "section"),
        ]

    # ------------------------------------------------------------------------------------------ where things are
    def th(self, t: float) -> float:
        """The laser's time relative to its pass over the probe, ms."""
        return (t - self.T_PROBE) * self.K

    def x1(self, t: float) -> float:
        """The first pass's laser, in the view (design units from its left edge)."""
        return self.XPV + self.vs * (t - self.T_PROBE)

    def x2(self, t: float) -> float:
        """The second pass's, travelling the other way."""
        vw = self.VIEW[2] - self.VIEW[0]
        return vw + 40.0 - self.vs * (t - self.T_PASS2)

    # ------------------------------------------------------------------------------------------ the layers
    def _prep(self):
        if self._ready:
            return
        mp, sc = self.mp, self.scale
        vw, vh = self.VIEW[2] - self.VIEW[0], self.VIEW[3] - self.VIEW[1]
        cut = self.f["al"]["powder"]["cut"]
        bed = _spheres(_particles(vw / self.UM, vh / self.UM, cut[0], cut[1], 7), vw, vh)
        self.band = {+1: _band(vw + 2, self.half, +1), -1: _band(vw + 2, self.half, -1)}
        self.band_h = self.band[+1].height
        base = bed.copy()
        k = 1
        while self.Y1V - k * self.hatch + self.half > 0:              # the tracks scanned before, oldest first
            k += 1
        for j in range(k - 1, 0, -1):
            yc = self.Y1V - j * self.hatch
            base.paste(self.band[+1 if j % 2 == 0 else -1], (0, int(round((yc - self.half) * S))))
        self.base = base
        # the field, carried with the laser: one picture for each direction of travel
        xi, yy = mp["xi_um"], mp["y_um"]
        fw, fh = int(round((xi[-1] - xi[0]) * self.UM * S)), int(round((yy[-1] - yy[0]) * self.UM * S))
        fld = Image.fromarray(sc.rgba(mp["top_C"]), "RGBA").resize((fw, fh), Image.BICUBIC)
        self.field = {+1: fld, -1: fld.transpose(Image.FLIP_LEFT_RIGHT)}
        self.f_ox = {+1: -xi[0] * self.UM * S, -1: xi[-1] * self.UM * S}      # the laser's column in each picture
        self.f_oy = -yy[0] * self.UM * S
        self.pool = _contour(mp["top_C"], mp["liquidus_C"], xi, yy) * self.UM      # the liquidus isotherm, (xi, y)
        i_w = int(np.argmax(np.abs(self.pool[:, 1]))) if len(self.pool) else 0
        self.xi_wide = float(self.pool[i_w, 0]) if len(self.pool) else 0.0
        self.xi_front = float(self.pool[:, 0].max()) if len(self.pool) else 0.0
        self.xi_rear = float(self.pool[:, 0].min()) if len(self.pool) else 0.0
        self._section_prep()
        self._ready = True

    def _section_prep(self):
        mp, sc = self.mp, self.scale
        x0, y0, x1, y1 = self.SEC
        w, h = x1 - x0, y1 - y0
        US, air, XA = self.US, self.AIR, self.XA
        XB = XA + w / US
        zmax = (h - air) / US
        xi, zz = mp["xi_um"], mp["z_um"]
        ci = np.nonzero((xi >= XA - 6) & (xi <= XB + 6))[0]
        ri = np.nonzero(zz <= zmax + 6)[0]
        sub = mp["side_C"][np.ix_(ri, ci)]
        cvs = Canvas(Image.new("RGB", (px(w), px(h)), (15, 17, 22)))
        cvs.rect((0, air, w, h), fill=METAL_DARK)
        t_um = float(self.proc["t_um"])
        kk = 1
        while kk * t_um < zmax:                                        # the layers under the surface
            y = air + kk * t_um * US
            cvs.dashed([(0, y), (w, y)], (92, 102, 122), 1, 5, 7)
            kk += 1
        X_ = lambda v: (v - XA) * US                                   # noqa: E731  (xi in um -> units in the picture)
        Y_ = lambda z: air + z * US                                    # noqa: E731
        fld = Image.fromarray(sc.rgba(sub), "RGBA").resize(
            (int(round((xi[ci[-1]] - xi[ci[0]]) * US * S)), int(round((zz[ri[-1]] - zz[ri[0]]) * US * S))),
            Image.BICUBIC)
        _paste_rgba(cvs.im, fld, int(round(X_(xi[ci[0]]) * S)), int(round(Y_(zz[ri[0]]) * S)))
        cvs.d = ImageDraw.Draw(cvs.im, "RGBA")
        iso = _contour(sub, mp["liquidus_C"], xi[ci], zz[ri])
        self.sec_iso = iso
        if len(iso):
            cvs.aaline([(X_(a), Y_(b)) for a, b in iso], WHITE, 2.6)
        self.sec_front = float(iso[:, 0].max()) if len(iso) else 0.0
        self.sec_rear = float(iso[:, 0].min()) if len(iso) else 0.0
        i_deep = int(np.argmax(iso[:, 1])) if len(iso) else 0
        xi_deep = float(iso[i_deep, 0]) if len(iso) else 0.0
        # the bead behind the pool and the surface (illustrative)
        cvs.rect((0, air - 9, X_(self.sec_rear) + 6, air), fill=METAL)
        cvs.line([(0, air), (w, air)], (196, 202, 214), 2)
        # the laser
        xl = X_(0.0)
        for wd, al in ((26, 34), (14, 70), (6, 255)):
            cvs.rect((xl - wd / 2, 0, xl + wd / 2, air), fill=G.HOT + (al,))
        # the depth: the twin's, a little under the isotherm's (its keyhole term)
        D, iso_d = self.tw["D_um"], 0.5 * self.tw["W_um"]
        xd = X_(xi_deep)
        cvs.dashed([(xd - 150, Y_(D)), (xd + 150, Y_(D))], WHITE, 2, 8, 6)
        _dim(cvs, (xd, Y_(0.0) + 2), (xd, Y_(D)), fill=WHITE)
        wd = _pill(cvs, xd, Y_(D) + 22, f"depth {fmt(D)} µm", 18, anchor="m", bold=True)
        if abs(D - iso_d) > 0.5:
            _pill(cvs, xd - wd / 2 - 10, Y_(D) + 22, f"the isotherm's {fmt(iso_d)} µm and the twin's keyhole term",
                  16, anchor="r")
        _pill(cvs, X_(self.sec_rear) - 12, air + 18, "liquidus isotherm: the melt pool", 16, anchor="r")
        self.sec_base = cvs.im
        self.sec_w, self.sec_h, self.sec_X, self.sec_Y, self.sec_XB = w, h, X_, Y_, XB
        # the powder layer ahead of the laser: a strip that scrolls towards the pool (illustrative)
        period = 420.0
        parts = _particles(period, air - 8, 15.0, min(30.0, air - 10), 11, 1500)
        strip = _spheres(parts, period, air - 8, bg=(15, 17, 22))
        self.strip, self.strip_period = strip, period

    # ------------------------------------------------------------------------------------------ the pictures
    def _top(self, cv: Canvas, t: float):
        mp = self.mp
        vx0, vy0, vx1, vy1 = self.VIEW
        vw, vh = vx1 - vx0, vy1 - vy0
        im = self.base.copy()
        xa, xb = self.x1(t), self.x2(t)
        y2 = self.Y1V + self.hatch
        # what each pass has consolidated so far
        if xa > 0:
            wpx = int(round(min(vw, xa) * S))
            im.paste(self.band[+1].crop((0, 0, wpx, self.band_h)), (0, int(round((self.Y1V - self.half) * S))))
        if xb < vw:
            x_from = int(round(max(0.0, xb) * S))
            im.paste(self.band[-1].crop((x_from, 0, self.band[-1].width, self.band_h)),
                     (x_from, int(round((y2 - self.half) * S))))
        # the field round each laser (the first pass's cooling tail is still there when the second starts)
        for d_, xl, yc in ((+1, xa, self.Y1V), (-1, xb, y2)):
            _paste_rgba(im, self.field[d_], int(round(xl * S - self.f_ox[d_])), int(round(yc * S - self.f_oy)))
        sub = fade_text(Canvas(im))
        for d_, xl, yc in ((+1, xa, self.Y1V), (-1, xb, y2)):
            if -260 < xl < vw + 260 and len(self.pool):
                sub.aaline([(xl + d_ * a_, yc + b_) for a_, b_ in self.pool], WHITE, 2.6)
            if -30 < xl < vw + 30:
                for r_, al in ((30, 40), (19, 80), (10, 170)):
                    sub.circle(xl, yc, r_, fill=G.HOT + (al,))
                sub.circle(xl, yc, 4.5, fill=WHITE)
            # the width, carried with the pool
            xw = xl + d_ * self.xi_wide
            aw = (min(ramp(xw, 160, 210), 1 - ramp(xw, vw - 70, vw - 20)) if d_ > 0 else
                  min(ramp(xw, 20, 70), 1 - ramp(xw, vw - 210, vw - 160)))
            if aw > 0:
                _dim(sub, (xw, yc - self.half), (xw, yc + self.half), aw)
                _pill(sub, xw - d_ * 12, yc + self.half + 22, f"width {fmt(self.tw['W_um'])} µm", 18,
                      anchor="r" if d_ > 0 else "l", a=aw, bold=True)
            if 40 < xl < vw - 150 and d_ > 0:
                _pill(sub, xl + 44, yc - 46, "laser", 17, a=min(ramp(xl, 40, 90), 1 - ramp(xl, vw - 200, vw - 150)))
            if 330 < xl < vw - 40 and d_ < 0:
                _pill(sub, xl - 44, yc - 46, "laser, the next track", 17, anchor="r",
                      a=min(ramp(xl, 330, 390), 1 - ramp(xl, vw - 90, vw - 40)))
        # the probe: a point under the first track's centreline
        xp, yp = self.XPV, self.Y1V
        sub.circle(xp, yp, 11, outline=WHITE, width=3)
        sub.line([(xp - 18, yp), (xp + 18, yp)], WHITE, 2)
        sub.line([(xp, yp - 18), (xp, yp + 18)], WHITE, 2)
        _pill(sub, xp + 20, yp + 32, f"probe: {fmt(mp['probe_um'])} µm under this point", 17)
        # the hatch spacing, once the next track is on its way
        ah = ramp(t, self.T_PASS2 + 1.2, self.T_PASS2 + 2.0)
        if ah > 0:
            xh = 64.0
            _dim(sub, (xh, self.Y1V), (xh, y2), ah)
            _pill(sub, xh + 12, (self.Y1V + y2) / 2, f"hatch {fmt(self.proc['h_um'])} µm", 18, a=ah, bold=True)
        _pill(sub, vw - 12, 20, f"shown {fmt(self.slow)} times slower", 16, anchor="r")
        G.scale_bar(sub, vw - 14, vh - 12, 1.0 / self.UM)
        cv.paste(sub.im, vx0, vy0)
        G.framed(cv, self.VIEW, "from above: the powder bed and the track")

    def _section(self, cv: Canvas, t: float, a: float):
        if a <= 0.004:
            return
        mp = self.mp
        x0, y0, x1, y1 = self.SEC
        w, air = self.sec_w, self.AIR
        im = self.sec_base.copy()
        # the powder layer flows in from ahead (the frame moves with the laser)
        xf = self.sec_X(self.sec_front) + 4
        off = (self.vs / self.UM * self.US * t) % self.strip_period
        sp, sw_ = self.strip, self.strip.width
        Xf = int(round(xf * S))
        k = -int(round(off * S))
        while k < im.width:
            if k + sw_ > Xf:
                lo = max(Xf, k)
                im.paste(sp.crop((lo - k, 0, min(sw_, im.width - k), sp.height)), (lo, int(round(4 * S))))
            k += sw_
        sub = Canvas(im)
        sub.rect((xf - 3, 0, xf + 22, air), fill=G.HOT + (60,))
        _pill(sub, w - 12, 20, f"powder layer, {fmt(self.proc['t_um'])} µm", 16, anchor="r")
        _pill(sub, self.sec_X(0.0) - 22, 20, "laser →", 16, anchor="r")
        # the probe's depth, and the probe itself as the bed carries it under the laser
        yp = self.sec_Y(mp["probe_um"])
        sub.dashed([(0, yp), (w, yp)], WHITE, 2, 3, 6, 0.85)
        _pill(sub, 12, yp + 20, f"probe depth, {fmt(mp['probe_um'])} µm: {self.lay_words} down", 16)
        xi_p = -self.v * self.th(t)                                       # where the probe is, seen from the laser
        if self.XA <= xi_p <= self.sec_XB:
            T_now = float(np.interp(self.th(t), mp["t_ms"], mp["hist_C"]))
            xpp = self.sec_X(xi_p)
            sub.circle(xpp, yp, 12, fill=WHITE)
            sub.circle(xpp, yp, 8.5, fill=self.scale.rgb(T_now))
            _pill(sub, xpp, yp - 26, "probe", 16, anchor="m")
        cv.paste(sub.im, x0, y0, a=a)
        G.framed(cv, self.SEC, "the centre plane under the laser", a=a)
        cv.tag(x0, y1 + 8, "sim", "the model's field, in the frame moving with the laser", a=a)
        cv.tag(x1, y1 + 8, "illus", "powder layer, bead", a=a, anchor="r")

    def _history(self, cv: Canvas, t: float, a: float):
        if a <= 0.004:
            return
        mp, ax = self.mp, self.axH
        x0, y0, x1, y1 = self.HIST
        cv.text(x0, y0 - 40, "Temperature at the probe as the first track passes", 22, bold=True, fill=INK, a=a)
        ax.draw(cv, a, size=16)
        cv.text((x0 + x1) / 2, y1 + 34, "time, ms: the laser is over the probe at 0", 18, fill=INK, anchor="ma", a=a)
        liq = mp["liquidus_C"]
        ax.hline(cv, liq, INK2, a)
        cv.text(x0 + 10, float(ax.Y(liq)) - 7, f"liquidus, {fmt(liq)} °C", 17, fill=INK, anchor="ls", a=a)
        th = self.th(t)
        u = (th - self.ht[0]) / (self.ht[-1] - self.ht[0])
        pen = ax.line(cv, self.ht, self.hh, G.HOT, 4.0, u, a)
        if pen and 0 < u < 1:
            cv.circle(pen[0], pen[1], 8, fill=G.HOT, outline=INK, width=2, a=a)
        tp = float(self.ht[self.i_peak])
        kp = ramp(th, tp + 0.01, tp + 0.05)
        if kp > 0:
            ax.dot(cv, tp, self.hh[self.i_peak], G.HOT, 6, a=a * kp)
            cv.text(float(ax.X(tp)) + 16, float(ax.Y(self.hh[self.i_peak])) + 2,
                    f"peak {fmt(mp['hist_peak_C'])} °C", 18, bold=True, fill=INK, anchor="lm", a=a * kp)
        if self.i_liq is not None:
            tl = float(self.ht[self.i_liq])
            kl = ramp(th, tl + 0.01, tl + 0.06)
            if kl > 0:
                rate = mp["hist_cool_K_s"] * 1e-3                         # K per ms
                dt = 0.085
                cv.aaline([(float(ax.X(tl - dt)), float(ax.Y(liq + rate * dt))),
                           (float(ax.X(tl + dt)), float(ax.Y(liq - rate * dt)))], WHITE, 3.0, a * kl)
                ax.dot(cv, tl, liq, WHITE, 5, ring=(20, 22, 28), a=a * kl)
                cv.text(float(ax.X(tl)) + 30, float(ax.Y(liq)) - 12,
                        f"cooling through the liquidus: {mp['hist_cool_K_s'] / 1e6:.1f} × 10⁶ K/s", 18, bold=True,
                        fill=INK, anchor="ls", a=a * kl)
                if self.molten_ms is not None and self.i_up is not None:
                    tu = float(self.ht[self.i_up])
                    yb = float(ax.Y(liq)) + 12
                    _dim(cv, (float(ax.X(tu)), yb), (float(ax.X(tl)), yb), a * kl, fill=INK2, tick=5)
                    cv.text(float(ax.X(tu)) + 6, yb + 9, f"molten for {self.molten_ms:.2f} ms", 16, fill=INK,
                            anchor="la", a=a * kl)
        cv.tag(x1 - 8, y0 + 8, "sim", "the model, at the probe", a=a, anchor="r")

    def _takes(self, cv: Canvas, t: float):
        """What the twin takes from the model, and what its truth does with each."""
        tw = self.tw
        col = CAMP[self.campaign]
        items = [
            ("melt-pool width", fmt(tw["W_um"]), "µm", "against the hatch spacing"),
            ("melt-pool depth", fmt(tw["D_um"]), "µm", "against the layer thickness"),
            ("lack-of-fusion index", fmt(tw["lof"], 2), "", "→ porosity: gaps left unmelted"),
            ("keyhole index", fmt(tw["kh"], 2), "", "→ porosity: keyhole pores"),
            ("cooling rate, surface", f"{tw['cool_K_s'] / 1e6:.1f}", "× 10⁶ K/s", "→ cell size, so strength"),
        ]
        x0, wcol = 962.0, 177.0
        lit = ramp(t, self.T_TAKES - 0.4, self.T_TAKES + 0.2)
        cv.text(x0 - 8, 748, "What the twin takes from this model", 19, bold=True, fill=mix(INK2, INK, lit))
        for i, (lab, val, unit, note) in enumerate(items):
            k = ramp(t, self.T_TAKES + 0.75 * i, self.T_TAKES + 0.75 * i + 0.5)
            x = x0 + i * wcol
            cv.rect((x - 8, 778, x + wcol - 12, 888), fill=mix(G.PLOT_FILL, mix(G.CARD_FILL, col, 0.24), k),
                    outline=mix(G.CARD_EDGE, mix(G.CARD_EDGE, col, 0.85), k), width=2, radius=10)
            cv.text(x, 785, lab, 16, cond=True, fill=mix(INK2, INK, 0.5 * k))
            if k <= 0:
                continue
            cv.text(x, 806, val, 31, bold=True, fill=INK, a=k)
            if unit:
                cv.text(x + cv.text_w(val, 31, bold=True) + 6, 818, unit, 17, fill=INK2, a=k)
            cv.para(x, 846, note, 16, wcol - 22, fill=INK, cond=True, a=k, lh=1.2, max_lines=2)
        ke = ramp(t, self.T_TAKES + 3.9, self.T_TAKES + 4.5)
        cv.text(x0 - 8, 898, f"A sixth, the energy density ({fmt(tw['Ev_J_mm3'])} J/mm³), sets how much Mg, Zn and Li "
                             f"boil off under the laser.", 17, cond=True, fill=INK2, a=ke)

    def _statement(self, cv: Canvas, t: float):
        """The stand-in statement: on screen for the whole segment, lit when the narration reaches it."""
        sk = self.f["sim_kinds"]
        calls = sk["calls"]
        total = sum(calls.values())
        k = ramp(t, self.T_NOT_TC, self.T_NOT_TC + 0.7)
        box = (78, 758, 878, 924)
        cv.rect(box, fill=mix((14, 16, 21), (58, 44, 12), k), outline=mix((84, 88, 98), St.WARN, k),
                width=3 if k > 0.5 else 2, radius=10)
        head = "A stand-in for Thermo-Calc's AM Module. Not Thermo-Calc output."
        size = 21.0
        while size > 16 and cv.text_w(head, size, bold=True) > 764:
            size -= 0.5
        cv.text(96, 768, head, size, bold=True, fill=INK)
        y = cv.para(96, 800, "Rosenthal's moving point source (1946), with this alloy's conductivity, density, "
                             "liquidus and absorptivity.", 18, 764, fill=INK, lh=1.3)
        if calls.get("sim_am", 0) == 0 and set(calls) == {"sim_open"}:
            s2 = (f"No run in round 3b bought this node: all {fmt(total)} simulation calls in its {fmt(sk['logs'])} "
                  f"runs were the open-database CALPHAD node. The same model sits inside the twin's truth, where it "
                  f"sets every simulated build's porosity and cell size.")
        else:
            s2 = (f"In round 3b's {fmt(sk['logs'])} runs this node was called {fmt(calls.get('sim_am', 0))} times, of "
                  f"{fmt(total)} simulation calls. The same model sits inside the twin's truth, where it sets every "
                  f"simulated build's porosity and cell size.")
        cv.para(96, y + 4, s2, 18, 764, fill=INK, lh=1.3)

    # ------------------------------------------------------------------------------------------ the frame
    def static_extra(self, cv: Canvas):
        cv.card((56, 150, 900, 936), "The model")
        cv.card((940, 150, 1864, 936), "Its output")
        mp, sc = self.mp, self.scale
        # the colour key under the view
        x0, x1, y = 78.0, 470.0, 634.0
        grad = np.repeat(G.LUT_HEAT[None, np.linspace(0, 255, int((x1 - x0) * S)).astype(int), :],
                         max(2, px(12)), 0)
        cv.paste(grad, x0, y)
        cv.rect((x0, y, x1, y + 12), outline=G.CARD_EDGE, width=1)
        for T_, lab, anc in ((mp["T0_C"], f"{fmt(mp['T0_C'])}", "la"),
                             (mp["liquidus_C"], f"{fmt(mp['liquidus_C'])}, liquidus", "ma"),
                             (1500.0, "1500", "ma"), (mp["boil_C"], f"{fmt(mp['boil_C'])} °C", "ra")):
            xx = x0 + (x1 - x0) * float(sc.u(T_))
            cv.line([(xx, y - 3), (xx, y + 15)], INK, 2)
            cv.text(xx, y + 18, lab, 16, fill=INK2, anchor=anc, cond=True)
        cv.text(x1 + 16, y - 4, "temperature; the scale stops at boiling,", 16, fill=INK2, cond=True)
        cv.text(x1 + 16, y + 16, "where a point source runs away", 16, fill=INK2, cond=True)
        w = cv.tag(78, 678, "sim", "the twin's melt-pool model for this alloy")
        cv.tag(78 + w + 10, 678, "illus", "powder bed, scanned tracks")
        p = self.proc
        cv.text(78, 718, f"Example settings: {fmt(p['P_W'])} W, {fmt(p['v_mm_s'])} mm/s, hatch {fmt(p['h_um'])} µm, "
                         f"layer {fmt(p['t_um'])} µm, plate at {fmt(p['T0_C'])} °C.", 17, fill=INK2, cond=True)

    def draw(self, cv: Canvas, t: float):
        self._prep()
        fade_text(cv)
        self._top(cv, t)
        self._statement(cv, t)
        self._section(cv, t, ramp(t, 2.2, 3.0))
        self._history(cv, t, ramp(t, 1.4, 2.2))
        self._takes(cv, t)


if __name__ == "__main__":
    import sys
    import time
    from pathlib import Path
    Path("/tmp/vid").mkdir(exist_ok=True)
    seg = AMModule()
    t0 = time.time()
    ts = [float(v) for v in sys.argv[1:]] or [0.8, 3.4, 5.2, 7.5, 11.0, 15.5, 19.5, 24.0, 28.0]
    for tt in ts:
        Image.fromarray(seg.frame(tt)).save(f"/tmp/vid/exp_am_{tt:05.1f}.png")
        print("wrote", f"/tmp/vid/exp_am_{tt:05.1f}.png")
    print(f"{(time.time() - t0) / len(ts):.2f} s a frame (the first builds the layers)")
    seg.close()
