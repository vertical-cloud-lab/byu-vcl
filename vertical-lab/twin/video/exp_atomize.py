"""Atomizing: the alloy becomes powder. The lab's own atomizer melting and pouring beside the powder's size
distribution building up, then the mass balance of the charge (twin/video/exp_atomize.py).

    Atomize().frame(t)      0 <= t <= Atomize.DURATION

What is what on screen:

* **The size distribution and the mass balance** are the twin's simulated measurements of the alloy followed
  (twin/instruments/psd.py: laser diffraction of the lot, three aliquots; twin/instruments/atomize_yield.py: each
  run's charge weighed, the usable powder weighed, the lot sieved into the campaign's cut), at full fidelity. The thin
  dashed line is the lot's true distribution, which only the twin knows. The bars filling in is the picture's way
  of showing the powder arriving: laser diffraction measures an aliquot at once.
* **The footage is real, and of another alloy**: the lab's own ultrasonic atomizer melting and pouring 630 bronze
  on 27 October 2026 (run k7m2q9, DAL #219; out/footage/manifest.json), and that run's powder after sieving. The
  frame over the footage says so. No footage of the alloy followed exists: it is a simulated alloy.
* **The crucible and the plate with its droplets** are the lab's 3-D model (PR 318's render of the atomizer).
* **The settings** are example settings (twin/instruments/micro.py ``AL_PROC``), not the ones the campaign's policy
  chose; the atomizer's throughput and failure rate in the twin are design targets, not the lab's record.
"""
from __future__ import annotations

import datetime as dt
import json
import math

import numpy as np
from PIL import Image

from . import data as D
from . import exp_data as X
from . import exp_draw as G
from . import style as St
from .exp_draw import Axes, Canvas, Segment, fmt, lin, ramp
from .style import CAMP, INK, INK2, mix

FOOT = D.HERE / "out" / "footage"
MELT = ("nab_melt2.mp4", 0.2, 6.8)                 # the rods slumping into a pool, through the furnace port
POUR = ("nab_pour1.mp4", 0.3, 7.3)                 # the jet landing on the plate and atomizing, through the view port
POUR_CROP = (48, 70, 310, 550)                     # the view port, a little closer (the clip is 406 x 720)
JARS = ("nab_k7m2q9_sieved_three_jars.jpg", (60, 190, 1530, 765))   # the three jars, clear of the room behind them
RENDER = "alloy_atomize"                           # PR 318's chapter 2 (out/mp4, 1280 x 720); its model half only
MODEL_MELT = (211.6, 219.6, (96, 150, 560, 316))   # the crucible in its coil, cut open
MODEL_POUR = (236.7, 243.3, (110, 104, 572, 322))  # the jet, the plate and the droplets
LOSS = (112, 118, 130)                             # what did not become powder: a neutral tone


def _alpha_text(cv: Canvas):
    """exp_draw.Canvas.text passes its alpha to PIL in the fill, and PIL draws text opaque on an RGB image whatever
    the fill's alpha is (shapes do blend), so text popped in while its panel was still fading. Until Canvas.text
    does this itself, give the frame's canvas a text() that fades: the glyphs drawn on a mask and pasted through it.
    Everything that writes (para, value, tag, Axes.draw, the segment's caption) goes through cv.text."""
    from PIL import ImageDraw

    def text(x, y, s, size=24, bold=False, fill=INK, anchor="la", cond=False, mono=False, a=1.0, stroke=0):
        if a >= 0.996 or stroke:
            return Canvas.text(cv, x, y, s, size, bold, fill, anchor, cond, mono, a, stroke)
        if a <= 0.004 or not s:
            return None
        f = St.font(size, bold=bold, cond=cond, mono=mono)
        X, Y = x * G.S, y * G.S
        l, t_, r, b = cv.d.textbbox((X, Y), str(s), font=f, anchor=anchor)
        x0, y0, x1, y1 = int(math.floor(l)) - 1, int(math.floor(t_)) - 1, int(math.ceil(r)) + 1, int(math.ceil(b)) + 1
        if x1 <= x0 or y1 <= y0:
            return None
        m = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(m).text((X - x0, Y - y0), str(s), font=f, fill=int(round(255 * a)), anchor=anchor)
        cv.im.paste(Image.new("RGB", m.size, tuple(int(v) for v in fill[:3])), (x0, y0), m)
        return None

    cv.text = text


def _manifest(name: str) -> dict:
    m = json.loads((FOOT / "manifest.json").read_text())
    return next(f for f in m["files"] if f["file"] == name)


def _issue(run: str) -> str:
    """The DAL issue a run's files are credited to (the first 'DAL #n' in an entry that names the run)."""
    import re
    m = json.loads((FOOT / "manifest.json").read_text())
    for f in m["files"]:
        if run in f.get("run", "") or run in f["file"]:
            hit = re.search(r"DAL #\d+", f.get("run", "") + " " + f.get("source", ""))
            if hit:
                return hit.group(0)
    return "DAL"


def _day(iso: str) -> str:
    d = dt.date.fromisoformat(iso)
    return f"{d.day} {d:%B} {d.year}"


def run_days(alloy) -> dict:
    """The day each kind of step first started for this design in the replayed run's own log ({what: day})."""
    ev = X._events(alloy.events)
    out = {}
    for e in ev["events"]:
        if e["campaign"] == alloy.campaign and e.get("design") == alloy.design_id:
            d = e["t0_h"] / D.HPD
            out[e["what"]] = min(out.get(e["what"], d), d)
    return out


class Atomize(Segment):
    key = "atomize"
    title = "Atomizing: the alloy becomes powder"
    campaign = "flaime_al"
    nodes = ("powder",)
    done = ("composition", "calphad")
    DURATION = 24.0
    T_MELT = (0.5, 5.4)          # the charge melts (real footage)
    T_POUR = 5.4                 # the pour: the jet atomizes on the plate
    T_PSD = (6.0, 12.6)          # the size distribution fills in
    T_MARK = (12.9, 15.3)        # the true distribution, d10, d50, d90, the cut's share
    T_JARS = 13.2                # the real powder of that run, sieved
    T_CHARGE = 1.3               # the mass balance's first row: what was charged
    T_YIELD = (15.7, 19.2)       # its other two rows: the usable powder, then the powder in the cut
    T_NET = 20.2                 # what the network takes

    def __init__(self):
        super().__init__()
        a = X.alloy("flaime_al")
        self.alloy = a
        F = X.load_facts()["al"]["powder"]
        self.F = F
        ps, yl = a.measure("psd"), a.measure("yield")
        r = ps["raw"]
        self.edges = np.asarray(r["edges_um"], float)
        self.d = np.asarray(r["d_um"], float)
        self.v = np.asarray(r["v_meas"], float) * 100.0            # % of the volume in each size class
        self.v_true = np.asarray(r["v_true"], float) * 100.0
        self.cut = tuple(float(c) for c in r["cut"])
        self.n_aliquots = int(np.asarray(r["v_meas_all"]).shape[0])
        ymax = float(math.ceil(self.v.max() + 0.6))
        self.ax = Axes((1068, 250, 1816, 512), (10.0, 1000.0), (0.0, ymax), "particle size, µm (log scale)",
                       "volume in each size class, %", xticks=[10, 20, 50, 100, 200, 500, 1000],
                       yticks=list(range(0, int(ymax) + 1, 2)), logx=True)
        self.inside = [i for i in range(len(self.d)) if self.edges[i] >= 10.0 and self.edges[i + 1] <= 1000.0]
        runs = yl["raw"]["runs"]
        self.runs = [dict(charge=float(c), usable=float(u), failed=bool(f))
                     for c, u, f in zip(runs["charge_g"], runs["usable_g"], runs["failed"])]
        self.yl = yl
        self.proc = a.proc
        self.T_melt = float(np.mean([rr["T_melt_C"] for rr in a.lot["runs"]]))
        self.days = run_days(a)
        mf, pf, jf = _manifest(MELT[0]), _manifest(POUR[0]), _manifest(JARS[0])
        run = pf["run"].split(" ")[0]
        self.foot = dict(alloy=pf["alloy"].split(" (")[0], day=_day(pf["date"]), run=run, issue=_issue(run),
                         jars_day=_day(jf["date"]), melt_day=_day(mf["date"]))
        self._readers: dict = {}
        self._jars = None
        nf, nr = F["failed"], F["runs"]
        words = {1: "One", 2: "Two", 3: "Three"}
        self.captions = [
            (0.6, 5.9, "The lab makes its own powder: it doses and presses the charge, atomizes it and checks the "
                       "powder."),
            (6.2, 15.4, "Laser diffraction sizes the powder. This distribution is the twin's simulated measurement "
                        "of this alloy's lot."),
            (15.7, 23.6, f"{words.get(nf, str(nf))} of {words.get(nr, str(nr)).lower()} runs failed here. "
                         f"{fmt(F['cut_yield_pct'])} % of the charge ends up in the cut the printer takes: the "
                         f"atomize node's output."),
        ]
        self.marks = {"atomize.melt": self.T_MELT[0], "atomize.charge": self.T_CHARGE, "atomize.pour": self.T_POUR,
                      "atomize.psd": self.T_PSD[0], "atomize.marks": self.T_MARK[0], "atomize.jars": self.T_JARS,
                      "atomize.yield": self.T_YIELD[0], "atomize.net": self.T_NET}
        self.sources = [
            ("sim", "size distribution: twin/instruments/psd.py (laser diffraction, three aliquots, full fidelity) "
                    "on the alloy followed; the dashed line is the lot's true distribution"),
            ("sim", "mass balance and in-cut yield: twin/instruments/atomize_yield.py (full fidelity)"),
            ("real", f"melt, pour and sieved powder: the lab's own atomizer, {self.foot['alloy']}, "
                     f"{self.foot['day']} (run {self.foot['run']}, {self.foot['issue']}): another alloy"),
            ("render", "the crucible and the plate with its droplets: PR 318's render (out/mp4/alloy_atomize.mp4)"),
            ("illus", "the bars filling in as the powder arrives (laser diffraction measures an aliquot at once)"),
        ]

    # ------------------------------------------------------------------------------------------ footage
    def _reader(self, which: str):
        if which not in self._readers:
            from . import assets as A
            if which == "melt":
                self._readers[which] = G.Footage(FOOT / MELT[0], MELT[1], MELT[2], 316, 560, None, 1.35)
            elif which == "pour":
                self._readers[which] = G.Footage(FOOT / POUR[0], POUR[1], POUR[2], 316, 560, POUR_CROP, 1.0)
            elif which == "model_melt":
                self._readers[which] = G.Footage(A.src(RENDER), MODEL_MELT[0], MODEL_MELT[1], 466, 262,
                                                 MODEL_MELT[2], 1.6)
            else:
                self._readers[which] = G.Footage(A.src(RENDER), MODEL_POUR[0], MODEL_POUR[1], 466, 262,
                                                 MODEL_POUR[2], 1.0)
        return self._readers[which]

    def _jar_photo(self) -> Image.Image:
        if self._jars is None:
            x, y, w, h = JARS[1]
            im = Image.open(FOOT / JARS[0]).convert("RGB").crop((x, y, x + w, y + h))
            self._jars = im.resize((max(2, int(round(466 * G.S))), max(2, int(round(233 * G.S)))), Image.LANCZOS)
        return self._jars

    def close(self):
        for r in self._readers.values():
            r.close()
        self._readers.clear()

    # ------------------------------------------------------------------------------------------ the frame
    def static_extra(self, cv: Canvas):
        cv.card((56, 150, 900, 936), "The experiment")
        cv.card((940, 150, 1864, 936), "Its data")
        self.ax.draw(cv)
        cv.text(1068, 204, "Particle size of the powder (laser diffraction)", 24, bold=True, fill=INK)
        x0, x1 = float(self.ax.X(self.cut[0])), float(self.ax.X(self.cut[1]))
        _, y0, _, y1 = self.ax.box
        cv.rect((x0, y0, x1, y1), fill=G.HOT + (30,))
        for x in (x0, x1):
            cv.line([(x, y0), (x, y1)], G.HOT, 2, 0.75)
        cv.text((x0 + x1) / 2, y0 + 8, f"the cut for the printer", 17, cond=True, fill=INK, anchor="ma")
        cv.text((x0 + x1) / 2, y0 + 30, f"{self.cut[0]:g} to {self.cut[1]:g} µm", 17, bold=True, cond=True,
                fill=INK, anchor="ma")
        # under the footage: what it is
        ft = self.foot
        cv.tag(78, 768, "real", f"the lab's own atomizer, {ft['day']} (run {ft['run']}, {ft['issue']})")
        cv.text(78, 808, f"{ft['alloy'].capitalize()}: a different alloy from the one followed.", 20, bold=True,
                fill=INK)
        nf, nr = self.F["failed"], self.F["runs"]
        cv.para(78, 846, "In the twin, the atomizer's throughput and failure rate are design targets, not the "
                         f"lab's record. This lot is the twin's model: {nf} of its {nr} runs failed.", 18, 800,
                fill=INK2, cond=True)

    def _left(self, cv: Canvas, t: float):
        ft = self.foot
        # ---- the real footage: the melt, then the pour (looped, with a dip at each wrap)
        box = (78, 196, 394, 756)
        kp = ramp(t, self.T_POUR - 0.25, self.T_POUR + 0.25)
        if kp < 1.0:
            cv.paste(self._reader("melt").frame(max(0.0, t - 0.1)), box[0], box[1])
        if kp > 0.0:
            rd = self._reader("pour")
            tl = max(0.0, t - self.T_POUR)
            fr = rd.frame(tl)
            ph = tl % rd.span
            dip = 1.0 if tl < rd.span * 0.5 else min(1.0, ph / 0.3, (rd.span - ph) / 0.3)
            if tl >= rd.span and ph < 0.3:
                dip = ph / 0.3
            if dip < 1.0:
                fr = (fr.astype(np.float32) * (0.25 + 0.75 * max(0.0, dip))).astype(np.uint8)
            cv.paste(fr, box[0], box[1], a=kp)
        lab = "the charge melts" if kp < 0.5 else "the pour: jet onto the plate"
        G.framed(cv, box, lab)
        cv.rect((box[0], box[3] - 40, box[2], box[3]), fill=(10, 12, 16, 225))
        cv.text((box[0] + box[2]) / 2, box[3] - 20, f"{ft['alloy']}, not this alloy", 19, bold=True, cond=True,
                fill=INK, anchor="mm")
        # ---- the lab's 3-D model: the crucible while it melts, the plate while it pours
        mb = (412, 196, 878, 458)
        if kp < 1.0:
            cv.paste(self._reader("model_melt").frame(max(0.0, t - 0.1)), mb[0], mb[1])
        if kp > 0.0:
            cv.paste(self._reader("model_pour").frame(max(0.0, t - self.T_POUR)), mb[0], mb[1], a=kp)
        G.framed(cv, mb, "the crucible in its coil, cut open" if kp < 0.5 else "the plate, the jet and the droplets")
        cv.tag(mb[0] + 10, mb[3] - 40, "render", "the lab's 3-D model (PR 318)")
        # ---- below it: the example settings, then the powder that run made
        jb = (412, 478, 878, 711)
        kj = ramp(t, self.T_JARS, self.T_JARS + 0.7)
        if kj < 1.0:
            a = 1.0 - kj
            cv.rect(jb, fill=G.PLOT_FILL, outline=G.CARD_EDGE, width=2, radius=10, a=a)
            cv.text(jb[0] + 18, jb[1] + 14, "Example settings", 19, bold=True, fill=INK, a=a)
            cv.text(jb[2] - 18, jb[1] + 16, "not the campaign's own", 17, cond=True, fill=INK2, anchor="ra", a=a)
            p = self.proc
            rows = [("melt", f"{fmt(p['superheat_K'])} K above the liquidus ({fmt(self.T_melt)} °C)"),
                    ("pour pressure", f"{fmt(p['pour_mbar'])} mbar of argon"),
                    ("plate amplitude", f"{p['amplitude']:g} of the maximum")]
            for i, (k, v) in enumerate(rows):
                y = jb[1] + 52 + i * 34
                cv.text(jb[0] + 18, y, k, 18, cond=True, fill=INK2, a=a)
                cv.text(jb[0] + 168, y, v, 18, cond=True, fill=INK, a=a)
            dd = self.days
            if "charge" in dd and "atomize" in dd:
                cv.para(jb[0] + 18, jb[1] + 162, f"In the replayed run (seed {self.alloy.seed}) this alloy's charge "
                        f"was made on day {fmt(dd['charge'])} and atomized on day {fmt(dd['atomize'])}.", 17,
                        jb[2] - jb[0] - 36, fill=INK2, cond=True, a=a)
        if kj > 0.0:
            cv.paste(self._jar_photo(), jb[0], jb[1], a=kj)
            G.framed(cv, jb, "that run's powder, sieved", a=kj)
            cv.rect((jb[0], jb[3] - 36, jb[2], jb[3]), fill=(10, 12, 16, 225), a=kj)
            cv.text((jb[0] + jb[2]) / 2, jb[3] - 18, "under 63 µm  ·  63 to 250 µm  ·  over 250 µm", 17, bold=True,
                    cond=True, fill=INK, anchor="mm", a=kj)
            cv.tag(jb[0], jb[3] + 10, "real", f"{ft['alloy']}, {ft['jars_day']} ({ft['issue']})", a=kj)

    def _psd(self, cv: Canvas, t: float):
        ax = self.ax
        col = CAMP[self.campaign]
        u = lin(t, *self.T_PSD)
        y_base = float(ax.Y(0.0))
        if u > 0:
            for i in self.inside:
                ph = (i * 2.399963) % (2 * math.pi)
                g = min(1.0, max(0.0, u + 0.72 * math.sin(ph + 7.0 * u) * u * (1.0 - u)))
                v = self.v[i] * g
                if v <= 0.004:
                    continue
                xa, xb = float(ax.X(self.edges[i])) + 1.2, float(ax.X(self.edges[i + 1])) - 1.2
                incut = self.cut[0] <= self.d[i] <= self.cut[1]
                cv.rect((xa, float(ax.Y(v)), xb, y_base), fill=col if incut else mix(G.PLOT_FILL, col, 0.62))
        m0, m1 = self.T_MARK
        kt = lin(t, m0, m0 + 0.9)
        if kt > 0:
            sel = [i for i in self.inside if self.v_true[i] > 0.01]
            ax.line(cv, self.d[sel], self.v_true[sel], INK, 2.2, kt, 0.9, dashed=True)
            ka = ramp(t, m0 + 0.6, m0 + 1.0)
            ip = max(sel, key=lambda i: self.v_true[i])
            cv.text(float(ax.X(self.d[ip])) + 150, float(ax.Y(self.v_true[ip])) + 2, "dashed: the lot's true", 17,
                    cond=True, fill=INK, anchor="la", a=ka)
            cv.text(float(ax.X(self.d[ip])) + 150, float(ax.Y(self.v_true[ip])) + 24, "distribution (the twin "
                    "knows it)", 17, cond=True, fill=INK, anchor="la", a=ka)
        F = self.F
        for j, (key, lab) in enumerate((("d10_um", "d10"), ("d50_um", "d50"), ("d90_um", "d90"))):
            kd = ramp(t, m0 + 0.9 + 0.35 * j, m0 + 1.3 + 0.35 * j)
            if kd <= 0:
                continue
            xv = float(ax.X(F[key]))
            cv.dashed([(xv, y_base), (xv, y_base - 46)], INK, 2, 7, 5, kd)
            cv.circle(xv, y_base, 6, fill=G.HOT, outline=INK, width=2, a=kd)
        kd = ramp(t, m0 + 1.2, m0 + 1.9)
        cv.tag(1068, 588, "sim", f"the twin's laser diffraction of this alloy's lot ({self.n_aliquots} aliquots)",
               a=ramp(t, self.T_PSD[0], self.T_PSD[0] + 0.6))
        cv.text(1068, 626, f"d10 {fmt(F['d10_um'])}  ·  d50 {fmt(F['d50_um'])}  ·  d90 {fmt(F['d90_um'])} µm", 20,
                bold=True, fill=INK, a=kd)
        kc = ramp(t, m0 + 1.9, m0 + 2.4)
        cv.text(1816, 627, f"{fmt(F['cut_frac_pct'])} % of its volume is in the cut", 19, fill=INK, anchor="ra", a=kc)

    def _balance(self, cv: Canvas, t: float):
        """The charge, the usable powder and the powder in the cut, as three bars on one scale (grams)."""
        y0_ = self.T_YIELD[0] - 1.1                      # rows 2 and 3 keep their offsets from here
        c0 = self.T_CHARGE
        col = CAMP[self.campaign]
        F, yl = self.F, self.yl
        x0, wmax = 1068.0, 470.0
        total = sum(r["charge"] for r in self.runs)
        sc = wmax / total
        rows_y = (702, 757, 812)
        # row 1: the charge, run by run
        k1 = ramp(t, c0, c0 + 0.6)
        cv.text(x0, rows_y[0] - 24, f"charged: {len(self.runs)} runs of {fmt(self.runs[0]['charge'])} g", 18,
                cond=True, fill=INK2, a=k1)
        x = x0
        slots = []
        for i, r in enumerate(self.runs):
            w = r["charge"] * sc
            g = lin(t, c0 + 0.3 * i, c0 + 0.7 + 0.3 * i)
            slots.append((x, w))
            if g > 0:
                cv.rect((x, rows_y[0], x + (w - 4) * g, rows_y[0] + 24), fill=mix(G.PLOT_FILL, (200, 206, 218), 0.7),
                        a=k1)
                if g >= 1.0:
                    cv.text(x + (w - 4) / 2, rows_y[0] + 12, f"run {i + 1}" + (": failed" if r["failed"] else ""),
                            16, bold=r["failed"], cond=True, fill=(18, 20, 24), anchor="mm", a=k1)
            x += w
        cv.text(x0 + wmax + 14, rows_y[0] + 12, f"{fmt(yl['charge_g'])} g", 20, bold=True, fill=INK, anchor="lm",
                a=k1)
        # row 2: what came out as usable powder
        k2 = ramp(t, y0_ + 1.1, y0_ + 1.7)
        cv.text(x0, rows_y[1] - 24, "usable powder (through the 250 µm sieve)", 18, cond=True, fill=INK2, a=k2)
        for i, (r, (xs, w)) in enumerate(zip(self.runs, slots)):
            g = lin(t, y0_ + 1.2 + 0.15 * i, y0_ + 1.8 + 0.15 * i)
            if g <= 0:
                continue
            if r["failed"]:
                cv.rect((xs, rows_y[1], xs + w - 4, rows_y[1] + 24), outline=LOSS, width=2, a=k2 * g)
                cv.text(xs + (w - 4) / 2, rows_y[1] + 12, "a skull, no powder", 16, cond=True, fill=INK2,
                        anchor="mm", a=k2 * g)
            else:
                wu = r["usable"] * sc
                cv.rect((xs, rows_y[1], xs + wu * g, rows_y[1] + 24), fill=mix(G.PLOT_FILL, col, 0.62), a=k2)
        cv.text(x0 + wmax + 14, rows_y[1] + 12, f"{fmt(yl['collected_g'])} g", 20, bold=True, fill=INK,
                anchor="lm", a=k2)
        cv.text(x0 + wmax + 96, rows_y[1] + 12, f"{fmt(F['yield_pct'])} % of the charge", 18, cond=True, fill=INK2,
                anchor="lm", a=k2)
        # row 3: what is in the cut
        k3 = ramp(t, y0_ + 2.3, y0_ + 2.9)
        g3 = lin(t, y0_ + 2.4, y0_ + 3.2)
        lo, hi = self.cut
        cv.text(x0, rows_y[2] - 24, f"in the {lo:g} to {hi:g} µm cut, after sieving", 18, cond=True, fill=INK2, a=k3)
        kn = ramp(t, self.T_NET, self.T_NET + 0.6)
        if kn > 0:
            cv.rect((x0 + wmax + 4, rows_y[2] - 12, 1836, rows_y[2] + 36), fill=mix(G.CARD_FILL, col, 0.30 * kn),
                    outline=mix(G.CARD_EDGE, col, kn), width=3, radius=10)
        if g3 > 0:
            cv.rect((x0, rows_y[2], x0 + yl["cut_g"] * sc * g3, rows_y[2] + 24), fill=col, a=k3)
        cv.text(x0 + wmax + 14, rows_y[2] + 12, f"{fmt(yl['cut_g'])} g", 20, bold=True, fill=INK, anchor="lm", a=k3)
        cv.text(x0 + wmax + 96, rows_y[2] + 12, f"{fmt(F['cut_yield_pct'])} % of the charge", 18, bold=kn > 0.5,
                cond=True, fill=INK if kn > 0.5 else INK2, anchor="lm", a=k3)
        cv.tag(1836, rows_y[0] - 38, "sim", "the twin's weighing and sieving of this lot", a=k1, anchor="r")
        cv.text(x0, 848, "→ the atomize node's output: the in-cut yield per charge", 20, bold=True, fill=INK, a=kn)
        cv.para(x0, 879, "Its inputs: composition, the liquidus CALPHAD gave, and the three settings. The powder's "
                         "oxygen and satellites go on to the print node.", 17, 756, fill=INK2, cond=True, a=kn,
                max_lines=2)

    def draw(self, cv: Canvas, t: float):
        _alpha_text(cv)
        self._left(cv, t)
        self._psd(cv, t)
        if t >= self.T_CHARGE:
            self._balance(cv, t)


if __name__ == "__main__":
    import sys
    seg = Atomize()
    for tt in [float(v) for v in sys.argv[1:]] or [2.0, 7.0, 10.0, 14.5, 18.0, 21.0, 24.0]:
        Image.fromarray(seg.frame(tt)).save(f"/tmp/vid/exp_atomize_{tt:05.1f}.png")
        print("wrote", f"/tmp/vid/exp_atomize_{tt:05.1f}.png")
    seg.close()
