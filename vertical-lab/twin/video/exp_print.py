"""Printing: one build of nine cubes at nine settings, each cube's density and crack reading going onto a map of
laser power against scan speed as it is measured (twin/video/exp_print.py).

    Print().frame(t)      0 <= t <= Print.DURATION

What is what on screen:

* **The nine readings** are the twin's simulated output for the alloy followed: nine parts made by the twin's build
  model (truth_al.AlTruth.build) from the lot's powder at a 3 x 3 grid of laser power and scan speed
  (exp_data.GRID_P x GRID_V), each reported exactly as the campaign reports a fresh part (Campaign._soundness: the
  lower of the Archimedes density and the polished section's image analysis, and the section's crack density; here
  with the instrument models at full fidelity). The two regimes' labels sit on the cubes where the twin's own
  lack-of-fusion and keyhole indices are highest (read from the data, not placed by hand).
* **The grid is an example grid**, not the settings the campaign's policy chose (the event logs don't hold them).
  In the campaign a build is up to nine density cubes at different settings and tensile blanks at ONE of them, chosen
  before printing; here that is the middle setting (exp_data.BARS_AT).
* **The plate with its nine cubes and blanks is a schematic** (illustrative): drawn without powder, not to scale;
  the cubes grow together, layer by layer, as they do in the machine. The layer count is the density coupon's height
  (twin/instruments/density.py) over the layer thickness.
* **The picture of the printer** is the lab's 3-D model (PR 318's render, out/hd/alloy_print.mp4). That render prints
  four tensile bars from the route's Al-10Si powder: it shows the machine, not this build, and its tag says so.

The segment does not say the alloy passes or fails a gate: its crack reading sits near the lab's gate and a single
section's reading scatters.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image

from . import exp_data as X
from . import exp_draw as G
from . import style as St
from .exp_am import fade_text          # exp_draw.Canvas.text ignores opacity; see exp_am._text_alpha
from .exp_draw import Axes, Canvas, Segment, fmt, lin, ramp
from .style import CAMP, INK, INK2, mix

WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
         10: "ten", 11: "eleven", 12: "twelve"}
# the density scale: denser is lighter (a sequential blue, FLAIME's colour family)
_STOPS = [(0.0, (30, 44, 84)), (0.45, (48, 108, 204)), (1.0, (216, 238, 255))]
_LUT = np.stack([np.interp(np.linspace(0, 1, 256), [s[0] for s in _STOPS], [s[1][i] for s in _STOPS])
                 for i in range(3)], 1).astype(np.uint8)
TOP, SIDE_V, SIDE_U = (150, 158, 174), (110, 118, 136), (82, 90, 108)        # a part's three faces
PLATE_TOP, PLATE_SIDE = (58, 64, 76), (38, 42, 52)
CLIP_T = (250.3, 259.5)          # PR 318's close-up of the laser on the plate, to its last layer (s of alloy_print)
CLIP_CROP = (0.245, 0.370, 0.370, 0.4935)   # x, y, w, h as shares of the frame: clear of its title, table and labels


def word(n: int) -> str:
    return WORDS.get(int(n), str(int(n)))


class Print(Segment):
    key = "print"
    title = "Printing: nine cubes, nine settings"
    campaign = "flaime_al"
    nodes = ("print",)
    done = ("composition", "calphad", "powder")
    DURATION = 27.0
    T_BUILD = (1.0, 9.0)
    T_MEAS0, MEAS_S = 9.6, 1.0       # the first cube's reading, and seconds a cube
    T_BARS = 19.0
    T_NET = 21.6
    # the schematic's projection (design units): the plate's back corner, and units per plate unit along x, y, up
    CX, CY, KX, KY, KH = 478.0, 524.0, 54.0, 27.0, 50.0
    PL, PITCH, FIRST, SIDE = 5.6, 1.7, 1.1, 1.0
    MAP = (1076, 244, 1832, 648)

    def __init__(self):
        super().__init__()
        a = X.alloy("flaime_al")
        self.alloy = a
        self.cubes = a.cubes()
        self.n = len(self.cubes)
        self.best, self.densest = a.best, a.densest
        self.proc = a.proc
        self.f = X.load_facts()["al"]
        self.GP, self.GV = list(X.GRID_P), list(X.GRID_V)
        self.dens = [100.0 * c["measured"]["rel_density"] for c in self.cubes]
        self.crack = [float(c["measured"]["crack_density"]) for c in self.cubes]
        por = [max(100.0 - d, 1e-3) for d in self.dens]
        self.p_hi, self.p_lo = max(por) * 1.15, min(por) * 0.6
        self.i_lof = int(np.argmax([c["lof"] for c in self.cubes]))
        self.i_kh = int(np.argmax([c["kh"] for c in self.cubes]))
        from twin.instruments import density as DN
        side_mm = (DN.COUPON_CM3[self.campaign] * 1000.0) ** (1.0 / 3.0)
        self.side_mm = side_mm
        self.n_layers = int(round(side_mm * 1000.0 / float(self.proc["t_um"])))
        x0, y0, x1, y1 = self.MAP
        span = self.GP[-1] - self.GP[0]
        self.ax = Axes(self.MAP, (self.GV[0] / 1.5, self.GV[-1] * 1.8), (self.GP[0] - 0.45 * span,
                                                                         self.GP[-1] + 0.33 * span),
                       "scan speed, mm/s", "laser power, W", xticks=self.GV, yticks=self.GP, logx=True)
        self._clip = None
        nn = word(self.n)
        self.captions = [
            (0.6, 9.3, "Each powder is printed at several laser settings; every build is checked for density and "
                       "cracks."),
            (self.T_MEAS0, self.T_MEAS0 + self.n * self.MEAS_S + 0.2,
             "Each cube is weighed in air and in water, then sectioned and imaged. Its density and its crack reading "
             "go on the map at its setting."),
            (self.T_BARS, 26.6, f"The tensile blanks are printed at the middle setting. One build gives the network "
                                f"{nn} rows: settings in, density and cracks out."),
        ]
        self.marks = {"print.build": self.T_BUILD[0], "print.readings": self.T_MEAS0, "print.bars": self.T_BARS,
                      "print.net": self.T_NET}
        self.sources = [
            ("sim", "nine cubes' density and crack readings: truth_al.AlTruth.build at exp_data.GRID_P x GRID_V for "
                    "the alloy followed, each measured as Campaign._soundness does (instrument models at full "
                    "fidelity); the regime labels from the twin's lack-of-fusion and keyhole indices"),
            ("illus", "the plate with nine cubes and the tensile blanks: drawn without powder, not to scale"),
            ("render", "the printer: PR 318's render (alloy_print.mp4), which prints four tensile bars from Al-10Si "
                       "powder, not this build"),
        ]

    # ------------------------------------------------------------------------------------------ small things
    def u_dens(self, d_pct: float) -> float:
        """0..1 along the density scale: the logarithm of the porosity, densest at 1."""
        p = max(100.0 - d_pct, 1e-3)
        return float(np.clip((math.log10(self.p_hi) - math.log10(p)) /
                             (math.log10(self.p_hi) - math.log10(self.p_lo)), 0.0, 1.0))

    def colour(self, d_pct: float) -> tuple:
        return tuple(int(v) for v in _LUT[int(round(self.u_dens(d_pct) * 255))])

    def iso(self, u: float, v: float, h: float = 0.0) -> tuple:
        return self.CX + (u - v) * self.KX, self.CY + (u + v) * self.KY - h * self.KH

    def cell(self, i: int) -> tuple:
        """Where cube i stands on the plate (u, v of its centre): speed along u, power towards the back."""
        ip, iv = divmod(i, len(self.GV))
        return self.FIRST + self.PITCH * iv, self.FIRST + self.PITCH * (len(self.GP) - 1 - ip)

    def _reader(self):
        if self._clip is None:
            from . import assets as A
            src = A.src("alloy_print")
            w, h = A.probe(src)[:2]
            cx, cy, cw, ch = CLIP_CROP
            speed = (CLIP_T[1] - CLIP_T[0]) / (self.T_BUILD[1] - self.T_BUILD[0])   # the clip's build in ours
            self._clip = G.Footage(src, CLIP_T[0], CLIP_T[1], 372, 279,
                                   (int(cx * w), int(cy * h), int(cw * w), int(ch * h)), speed)
        return self._clip

    def close(self):
        if self._clip is not None:
            self._clip.close()
            self._clip = None

    def measured(self, t: float) -> tuple:
        """(how many cubes have their reading, the cube being measured or None, 0..1 through it)."""
        k = (t - self.T_MEAS0) / self.MEAS_S
        if k < 0:
            return 0, None, 0.0
        if k >= self.n:
            return self.n, None, 1.0
        return int(k), int(k), k - int(k)

    # ------------------------------------------------------------------------------------------ the schematic
    def _box(self, cv: Canvas, u0, v0, u1, v1, h, top=TOP, sv=SIDE_V, su=SIDE_U, edge=(196, 202, 214), lines=0,
             a=1.0, width=1.5):
        I = self.iso
        cv.poly([I(u0, v1), I(u1, v1), I(u1, v1, h), I(u0, v1, h)], fill=sv, a=a)
        cv.poly([I(u1, v0), I(u1, v1), I(u1, v1, h), I(u1, v0, h)], fill=su, a=a)
        for k in range(1, lines + 1):                                  # the layers, as fine lines on the sides
            hh = h * k / (lines + 1)
            cv.line([I(u0, v1, hh), I(u1, v1, hh), I(u1, v0, hh)], mix(sv, (20, 22, 28), 0.35), 1, a)
        cv.poly([I(u0, v0, h), I(u1, v0, h), I(u1, v1, h), I(u0, v1, h)], fill=top, a=a)
        cv.line([I(u0, v1), I(u0, v1, h), I(u0, v0, h), I(u1, v0, h), I(u1, v0), I(u1, v1), I(u0, v1)], edge, width, a)
        cv.line([I(u0, v1, h), I(u1, v1, h), I(u1, v0, h)], edge, width, a)
        cv.line([I(u1, v1), I(u1, v1, h)], edge, width, a)

    def _plate(self, cv: Canvas):
        """The plate and its two scales (static)."""
        I, PL = self.iso, self.PL
        th = 0.22
        cv.poly([I(0, PL, -th), I(PL, PL, -th), I(PL, PL), I(0, PL)], fill=PLATE_SIDE)
        cv.poly([I(PL, 0, -th), I(PL, PL, -th), I(PL, PL), I(PL, 0)], fill=mix(PLATE_SIDE, (0, 0, 0), 0.25))
        cv.poly([I(0, 0), I(PL, 0), I(PL, PL), I(0, PL)], fill=PLATE_TOP, outline=(120, 128, 142), width=2)
        for j, v_ in enumerate(self.GV):                               # scan speed along the front-left edge
            x, y = I(self.FIRST + self.PITCH * j, PL + 0.55)
            cv.text(x, y - 8, f"{v_:g}", 18, bold=True, fill=INK, anchor="ma")
        x, y = I(self.FIRST + self.PITCH, PL + 1.4)
        cv.text(x, y, "scan speed, mm/s", 17, fill=INK2, anchor="ma", cond=True)
        for i, p_ in enumerate(self.GP):                               # laser power along the front-right edge
            x, y = I(PL + 0.55, self.FIRST + self.PITCH * (len(self.GP) - 1 - i))
            cv.text(x, y - 8, f"{p_:g}", 18, bold=True, fill=INK, anchor="ma")
        x, y = I(PL + 1.4, self.FIRST + self.PITCH)
        cv.text(x, y, "laser power, W", 17, fill=INK2, anchor="ma", cond=True)

    def _blanks(self) -> list:
        """Three thin blanks standing beside the cube at the setting they are printed at."""
        u, v = self.cell(self.best)
        s = self.SIDE / 2
        out = []
        for k in range(3):
            u0 = u + s + 0.13 + k * 0.19
            out.append((u0, v - s, u0 + 0.12, v + s))
        return out

    def _schematic(self, cv: Canvas, t: float):
        I = self.iso
        s = self.SIDE / 2
        ub = lin(t, *self.T_BUILD)
        h = 0.03 + 0.97 * ub
        n_done, cur, uc = self.measured(t)
        building = 0 < ub < 1
        # which part the laser is on: nine cubes, then the blanks, round and round
        dwell = 0.27
        k_scan = int(((t - self.T_BUILD[0]) % (dwell * (self.n + 1))) / dwell)
        f_scan = (((t - self.T_BUILD[0]) % (dwell * (self.n + 1))) / dwell) % 1.0
        parts = []
        for i in range(self.n):
            u, v = self.cell(i)
            parts.append((u + v, "cube", i, (u - s, v - s, u + s, v + s)))
        for k, b in enumerate(self._blanks()):
            parts.append((b[0] + b[2] + b[1] + b[3], "blank", k, b))
        parts.sort(key=lambda p: (p[3][0] + p[3][2]) / 2 + (p[3][1] + p[3][3]) / 2)
        kb = ramp(t, self.T_BARS, self.T_BARS + 0.6)
        spot = None
        for _, kind, i, (u0, v0, u1, v1) in parts:
            top, edge, wd = TOP, (196, 202, 214), 1.5
            active = building and ((kind == "cube" and k_scan == i) or (kind == "blank" and k_scan == self.n))
            if kind == "cube" and i < n_done:
                top = self.colour(self.dens[i])
            if kind == "cube" and cur == i:
                top = mix(TOP, self.colour(self.dens[i]), ramp(uc, 0.45, 0.9))
                edge, wd = G.HOT, 3.5
            if kb > 0 and (kind == "blank" or i == self.best):
                edge, wd = mix(edge, G.HOT, kb), 1.5 + 2.0 * kb
            if active:
                top = mix(top, G.HOT, 0.30)
            self._box(cv, u0, v0, u1, v1, h, top=top, edge=edge, lines=5 if kind == "cube" else 0, width=wd)
            if active:                                                 # the hatch being laid on this layer
                nl = 6 if kind == "cube" else 1
                if kind == "blank" and i != int(f_scan * 3) % 3:
                    continue
                for j in range(nl):
                    fj = f_scan * nl - j
                    if fj <= 0:
                        break
                    vv = v0 + (v1 - v0) * (j + 0.5) / nl
                    ua, ub_ = (u0 + 0.06, u1 - 0.06) if j % 2 == 0 else (u1 - 0.06, u0 + 0.06)
                    ue = ua + (ub_ - ua) * min(1.0, fj)
                    cv.line([I(ua, vv, h), I(ue, vv, h)], G.HOT, 3)
                    if fj < 1.0:
                        spot = I(ue, vv, h)
        if building and spot is not None:
            x, y = spot
            cv.line([(self.CX, 492), (x, y)], G.HOT + (150,), 3)
            cv.circle(x, y, 9, fill=G.HOT + (120,))
            cv.circle(x, y, 4, fill=(255, 255, 255))
        if kb > 0:                                                     # the blanks' label, with a leader to them
            b = self._blanks()[1]
            x, y = I((b[0] + b[2]) / 2, (b[1] + b[3]) / 2, 1.0)
            lx, ly = 742.0, 532.0
            cv.line([(x, y - 4), (lx - 6, ly + 22)], INK, 2, kb)
            c = self.cubes[self.best]
            cv.text(lx, ly - 26, "tensile blanks", 19, bold=True, fill=INK, anchor="ma", a=kb)
            cv.text(lx, ly - 2, f"printed at {c['P_W']:g} W, {c['v_mm_s']:g} mm/s", 17, fill=INK, anchor="ma", a=kb,
                    cond=True)

    # ------------------------------------------------------------------------------------------ the map
    def _map(self, cv: Canvas, t: float):
        ax = self.ax
        x0, y0, x1, y1 = self.MAP
        col = CAMP[self.campaign]
        n_done, cur, uc = self.measured(t)
        kb = ramp(t, self.T_BARS, self.T_BARS + 0.6)
        kn = ramp(t, self.T_NET, self.T_NET + 0.7)
        nP, nV = len(self.GP), len(self.GV)
        for i, c in enumerate(self.cubes):
            X_, Y_ = float(ax.X(c["v_mm_s"])), float(ax.Y(c["P_W"]))
            if i >= n_done and cur != i:
                cv.circle(X_, Y_, 7, outline=(96, 102, 114), width=2)       # a setting still waiting for its reading
                continue
            k = 1.0 if i < n_done else ramp(uc, 0.45, 0.85)
            if cur == i:
                cv.circle(X_, Y_, 30, outline=G.HOT, width=3, a=1 - 0.6 * k)
                if k <= 0:
                    cv.circle(X_, Y_, 7, outline=G.HOT, width=3)
                    continue
            r = 21.0 * (0.6 + 0.4 * k)
            cv.circle(X_, Y_, r + 3, fill=(232, 236, 244), a=k)
            cv.circle(X_, Y_, r, fill=self.colour(self.dens[i]), a=k)
            cv.text(X_ + 32, Y_ - 12, f"{self.dens[i]:.2f} %", 23, bold=True, fill=INK, anchor="lm", a=k)
            cr = self.crack[i]
            cv.text(X_ + 32, Y_ + 14, f"cracks {cr:.2f}" if cr > 0 else "no cracks found", 17, cond=True,
                    fill=INK2, anchor="lm", a=k)
        kw = 1 - ramp(t, self.T_MEAS0 - 0.5, self.T_MEAS0 + 0.3)        # while the build runs: what will come
        cv.text((x0 + x1) / 2, y1 - 34, "one reading for each setting, once the cubes are built and measured", 19,
                fill=INK2, anchor="mm", a=kw)
        # the two regimes, where the twin's own indices are highest
        for i, head, key_, tail in ((self.i_lof, "lack of fusion", "lof", "the twin's lack-of-fusion index peaks here"),
                                    (self.i_kh, "keyholing", "kh", "the twin's keyhole index peaks here")):
            if i >= n_done:
                continue
            k = ramp(t, self.T_MEAS0 + (i + 1) * self.MEAS_S, self.T_MEAS0 + (i + 1) * self.MEAS_S + 0.6)
            c = self.cubes[i]
            ip, iv = divmod(i, nV)
            X_, Y_ = float(ax.X(c["v_mm_s"])), float(ax.Y(c["P_W"]))
            up = ip >= nP / 2                                          # the upper rows carry the label above them
            left = iv < nV / 2
            xa = X_ - 24 if left else min(X_ + 150, x1 - 10)
            anc = "l" if left else "r"
            ya = Y_ - 74 if up else Y_ + 36
            cv.text(xa, ya, head, 19, bold=True, fill=INK, anchor=anc + "a", a=k)
            cv.text(xa, ya + 25, f"{tail}: {c[key_]:.2f}", 17, cond=True, fill=INK2, anchor=anc + "a", a=k)
        # the setting the blanks are printed at, and the densest reading if it is another
        if kb > 0:
            c = self.cubes[self.best]
            X_, Y_ = float(ax.X(c["v_mm_s"])), float(ax.Y(c["P_W"]))
            cv.circle(X_, Y_, 31, outline=G.HOT, width=4, a=kb)
            cv.text(X_ + 10, Y_ - 52, "tensile blanks printed at this setting", 18, bold=True, fill=INK, anchor="mm",
                    a=kb)
            if self.densest != self.best:
                c = self.cubes[self.densest]
                X_, Y_ = float(ax.X(c["v_mm_s"])), float(ax.Y(c["P_W"]))
                cv.text(X_ + 32, Y_ + 36, "the densest reading", 16, cond=True, fill=INK, anchor="lm", a=kb)
        # what the network takes
        if kn > 0:
            for i, c in enumerate(self.cubes):
                X_, Y_ = float(ax.X(c["v_mm_s"])), float(ax.Y(c["P_W"]))
                cv.circle(X_, Y_, 27, outline=col, width=3, a=kn * (0.72 + 0.28 * math.sin(4.0 * (t - self.T_NET))))
        cv.para(x0 - 4, 838, f"→ the print node: {word(self.n)} rows from this one build, each a setting with its "
                             f"density and its crack density", 20, 770, bold=True, fill=INK, a=kn, lh=1.3)
        cv.text(x0 - 4, 900, "An example grid of settings, not the ones the campaign's policy chose.", 17, cond=True,
                fill=INK2)

    # ------------------------------------------------------------------------------------------ the frame
    def static_extra(self, cv: Canvas):
        cv.card((56, 150, 900, 936), "The experiment")
        cv.card((940, 150, 1864, 936), "Its data")
        self._plate(cv)
        cv.tag(78, 892, "illus", "this build: nine cubes and the blanks, drawn without powder, not to scale")
        # the build, in words
        p = self.proc
        x = 474
        cv.text(x, 200, "One build", 21, bold=True, fill=INK)
        y = cv.para(x, 234, f"{word(self.n).capitalize()} density cubes, each at its own laser power and scan speed.",
                    18, 400, fill=INK, lh=1.32)
        y = cv.para(x, y + 6, "Tensile blanks at one of the settings, chosen before printing.", 18, 400, fill=INK,
                    lh=1.32)
        cv.text(x, y + 10, f"hatch {fmt(p['h_um'])} µm, layer {fmt(p['t_um'])} µm, plate at {fmt(p['T0_C'])} °C",
                17, fill=INK2, cond=True)
        self._status_y = y + 46
        # the map's frame and its key
        x0, y0, x1, y1 = self.MAP
        cv.text(x0 - 4, 196, "Density of each cube, at its laser power and scan speed", 23, bold=True, fill=INK)
        self.ax.draw(cv)
        kx0, kx1, ky = x0, x0 + 400.0, 738.0
        grad = np.repeat(_LUT[None, np.linspace(0, 255, int((kx1 - kx0) * St.S)).astype(int), :],
                         max(2, St.px(14)), 0)
        cv.paste(grad, kx0, ky)
        cv.rect((kx0, ky, kx1, ky + 14), outline=G.CARD_EDGE, width=1)
        gate = self.f["gates"]["density_pct"]
        for d in (90.0, 97.0, 99.0, gate, 99.8):
            u = self.u_dens(d)
            if not 0.02 < u < 0.98:
                continue
            xx = kx0 + (kx1 - kx0) * u
            cv.line([(xx, ky - 4), (xx, ky + 18)], INK, 2)
            cv.text(xx, ky + 21, f"{d:g}", 16, fill=INK2, anchor="ma", cond=True)
            if d == gate:
                cv.text(xx, ky - 8, "the lab's gate", 16, fill=INK2, anchor="ms", cond=True)
        cv.text(kx1 + 16, ky - 4, "relative density, %: denser is lighter", 17, fill=INK2, anchor="lm", cond=True)
        cv.text(kx1 + 16, ky + 20, "cracks: mm of crack per mm² of section", 17, fill=INK2, anchor="lm", cond=True)
        cv.tag(x0 - 4, 796, "sim", "the twin's build model, each cube weighed and sectioned by its instrument models")

    def draw(self, cv: Canvas, t: float):
        fade_text(cv)
        # the printer, from the lab's 3-D model
        rd = self._reader()                      # it plays once, with the build, then holds its finished plate
        fr = rd.frame(min(max(t - self.T_BUILD[0], 0.0), rd.span - 2.0 / rd.fps))
        cv.paste(fr, 78, 198)
        G.framed(cv, (78, 198, 450, 477), "the lab's 3-D model of the printer (PR 318)", size=16)
        cv.tag(86, 440, "render", "another build: four tensile bars", size=16)
        # where the build is
        x, y = 474, self._status_y
        ub = lin(t, *self.T_BUILD)
        n_done, cur, uc = self.measured(t)
        if ub < 1:
            layer = max(1, int(round(ub * self.n_layers)))
            cv.text(x, y, f"layer {fmt(layer)} of {fmt(self.n_layers)}" if ub > 0 else "ready to print", 26,
                    bold=True, fill=INK)
            cv.rect((x, y + 40, x + 380, y + 50), fill=(40, 44, 54), radius=5)
            cv.rect((x, y + 40, x + 380 * ub, y + 50), fill=G.HOT, radius=5)
            cv.text(x, y + 60, f"{fmt(self.side_mm)} mm cubes, the cubes and blanks grow together", 17, fill=INK2,
                    cond=True)
        elif cur is not None:
            c = self.cubes[cur]
            cv.text(x, y, f"cube {cur + 1} of {self.n}: {c['P_W']:g} W, {c['v_mm_s']:g} mm/s", 21, bold=True,
                    fill=INK)
            cv.text(x, y + 38, "weighed in air and in water" if uc < 0.45 else "sectioned, polished and imaged", 19,
                    fill=INK)
        elif n_done >= self.n:
            cv.text(x, y, f"{word(self.n).capitalize()} cubes measured", 24, bold=True, fill=INK)
            cv.para(x, y + 38, "The blanks go on to heat treatment and the tensile test.", 18, 400, fill=INK2,
                    cond=True, a=ramp(t, self.T_BARS, self.T_BARS + 0.6))
        else:
            cv.text(x, y, "Built", 26, bold=True, fill=INK)
            cv.text(x, y + 40, "off the plate: to the balance, then the saw", 18, fill=INK2, cond=True)
        self._schematic(cv, t)
        self._map(cv, t)


if __name__ == "__main__":
    import sys
    import time
    from pathlib import Path
    Path("/tmp/vid").mkdir(exist_ok=True)
    seg = Print()
    t0 = time.time()
    ts = [float(v) for v in sys.argv[1:]] or [0.5, 4.0, 8.5, 11.2, 15.3, 18.9, 20.5, 23.5, 27.0]
    for tt in ts:
        Image.fromarray(seg.frame(tt)).save(f"/tmp/vid/exp_print_{tt:05.1f}.png")
        print("wrote", f"/tmp/vid/exp_print_{tt:05.1f}.png")
    print(f"{(time.time() - t0) / len(ts):.2f} s a frame")
    seg.close()
