"""CALPHAD: Scheil solidification. The melt cooling beside its curve of temperature against fraction solid, the same
alloy three ways, then the numbers the network reads from the curve (twin/video/exp_scheil.py).

    Scheil().frame(t)      0 <= t <= Scheil.DURATION

What is what on screen:

* **The open-database node's curve** (blue) is the twin's own: its dilute multicomponent Scheil model with the
  parameters pycalphad gives on the open databases (twin/thermo.py ``AlSolidification('open')``, the curve kept by
  ``exp_data.scheil_twin``). It is what every policy in round 3b saw: all of that round's committed runs called this
  node and no other (``facts.json`` ``sim_kinds``). The liquidus, freezing range, cracking index and Q read from it
  are that node's outputs (``AlTruth.sim_open``).
* **The pycalphad + scheil curve** (violet) is an independent Scheil-Gulliver calculation on MatCalc's open aluminium
  database, for the elements that database has (``exp_data.scheil_open``; the elements left out are named on
  screen). Its phases, the temperatures they first appear at and their amounts at the end are that run's output.
* **The hidden truth's curve** (light) is the same model with the assessed diagrams' parameters and its primary
  intermetallics (``AlSolidification('truth')``): what the twin's alloy does, which no policy sees.
* **Nothing here is Thermo-Calc output.** The twin's Thermo-Calc node is a stand-in (the truth with a few percent
  error) that no run of round 3b bought; the segment says so.
* **The picture of the melt is illustrative**: grains growing into a liquid until the share of the picture that is
  solid equals the fraction solid of the curve being drawn; where the run has primary intermetallics they come first.
  The shapes are drawn, not computed.
"""
from __future__ import annotations

import math
import re

import numpy as np
from PIL import Image

from . import exp_data as X
from . import exp_draw as G
from . import style as St
from .exp_draw import Axes, Canvas, Segment, fmt, lin, ramp
from .style import CAMP, INK, INK2, mix

CALC = G.KIND["calc"][0]                 # the pycalphad run's line: the colour of the "computed" tag
TRUTH = (226, 228, 234)                  # the hidden truth's line
PHASE_NAME = {"FCC_A1": "fcc Al", "AL4CR": "Al₄Cr", "AL3TI_H": "Al₃Ti", "AL6MN": "Al₆Mn", "AL3ZR": "Al₃Zr",
              "AL3NI": "Al₃Ni"}
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
TIGHT, WIDE = (612.0, 682.0), (596.0, 806.0)


def phase_name(key: str) -> str:
    """A database's phase name as it is written on screen (AL13CR2 -> Al₁₃Cr₂)."""
    if key in PHASE_NAME:
        return PHASE_NAME[key]
    k = key.split("_")[0]
    return "".join(a.capitalize() + b.translate(SUB) for a, b in re.findall(r"([A-Za-z]+)(\d*)", k))


def formula_name(s: str) -> str:
    """'Al13Cr2' -> 'Al₁₃Cr₂'."""
    return "".join(a + b.translate(SUB) for a, b in re.findall(r"([A-Z][a-z]?)(\d*)", s))


def _formula(s: str) -> dict:
    return {a: int(b or 1) for a, b in re.findall(r"([A-Z][a-z]?)(\d*)", s)}


def _rank(v: np.ndarray) -> np.ndarray:
    """Values -> their rank in 0..1 (so that a threshold u selects a share u of the picture)."""
    flat = v.ravel()
    out = np.empty(flat.size)
    out[np.argsort(flat, kind="stable")] = (np.arange(flat.size) + 0.5) / flat.size
    return out.reshape(v.shape)


def melt_fields(n: int = 300, seed: int = 11) -> dict:
    """The schematic's geometry (illustrative): for each point the order in which it freezes as a grain's arms reach
    it (``order``, 0..1: the last points to freeze lie between the grains), which grain it joins (``grain``), and
    the order in which points turn into intermetallic particles in a run that has them (``part``)."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:n, 0:n] / float(n)
    g = 4
    pts = [((i + 0.5 + rng.uniform(-0.34, 0.34)) / g, (j + 0.5 + rng.uniform(-0.34, 0.34)) / g)
           for i in range(g) for j in range(g)]
    th = rng.uniform(0, math.pi / 2, len(pts))
    m = n // 10 + 3                                           # a smooth random field, for the arms' roughness
    coarse = rng.normal(size=(m, m))
    ix = np.linspace(0, m - 1.001, n)
    i0 = ix.astype(int)
    fx = ix - i0
    rows = coarse[i0] * (1 - fx)[:, None] + coarse[i0 + 1] * fx[:, None]
    noise = rows[:, i0] * (1 - fx)[None, :] + rows[:, i0 + 1] * fx[None, :]
    tmin = np.full((n, n), 1e9)
    grain = np.zeros((n, n), int)
    for k, ((sx, sy), a) in enumerate(zip(pts, th)):
        dx, dy = xx - sx, yy - sy
        r = np.hypot(dx, dy)
        phi = np.arctan2(dy, dx) - a
        v = 1.0 + 0.58 * np.cos(4 * phi)                       # four arms: fastest along them
        tau = r / v * (1.0 + 0.10 * np.sin(2 * math.pi * 34 * r * np.abs(np.cos(2 * phi)) + k))
        better = tau < tmin
        grain[better] = k
        tmin = np.where(better, tau, tmin)
    order = _rank(tmin * (1.0 + 0.16 * noise))
    pv = np.full((n, n), 1e9)                                  # particles: small plates at random places
    for _ in range(46):
        cx, cy, a = rng.uniform(0.04, 0.96), rng.uniform(0.04, 0.96), rng.uniform(0, math.pi)
        la, lb = rng.uniform(0.030, 0.060), rng.uniform(0.008, 0.014)
        u = (xx - cx) * math.cos(a) + (yy - cy) * math.sin(a)
        w = -(xx - cx) * math.sin(a) + (yy - cy) * math.cos(a)
        pv = np.minimum(pv, np.maximum(np.abs(u) / la, np.abs(w) / lb))
    tint = 0.80 + 0.24 * rng.random(len(pts))
    return dict(n=n, order=order, grain=grain, part=_rank(pv), tint=tint[grain])


class Scheil(Segment):
    key = "scheil"
    title = "CALPHAD: Scheil solidification"
    campaign = "flaime_al"
    nodes = ("calphad",)
    done = ("composition",)
    DURATION = 33.5              # the end state holds while the line on round 3b's runs is spoken
    T_OPEN = (0.9, 8.3)          # the node's curve draws as the melt cools
    T_OUT = (8.5, 9.5)           # the plot widens
    T_CALC = (9.6, 15.2)         # the open-database Scheil run, its phases ticked off
    T_TRUTH = (16.0, 19.4)       # the hidden truth
    T_IN = (19.7, 20.7)          # back to the node's curve
    T_LIQ, T_RANGE, T_KOU, T_Q = 20.9, 22.3, 23.7, 25.5
    T_NET = 26.8                 # what the network takes
    BOX = (1052, 246, 1820, 598)
    MELT = (80, 206, 540)        # x, y, side of the picture of the melt

    def __init__(self):
        super().__init__()
        a = X.alloy("flaime_al")
        self.alloy = a
        sc = a.scheil()
        self.op, self.tr = sc["open"], sc["truth"]
        self.calc = X.scheil_open()
        self.sim = a.sims()["open"]
        self.kinds = X.load_facts()["sim_kinds"]
        self.col = CAMP[self.campaign]
        self.F = melt_fields()
        # --- the three trajectories: x = fraction solid (%), y = temperature (degC), and what the picture shows
        o = self.op
        self.cur_open = dict(x=o["fs"] * 100.0, y=o["T_C"], fs=o["fs"], part=0.0)
        t = self.tr
        prim = sorted(t["primary"].items(), key=lambda kv: -kv[1]["T_C"])
        self.prim = [(formula_name(p["phase"]), float(p["T_C"])) for _, p in prim]
        from twin.instruments import micro
        share = 0.0                                            # the truth's primary intermetallics, as a share of the
        for el, p in prim:                                     # picture (their excess solute over the phase's own
            share += p["excess_wt"] / max(micro.stoich_wt(_formula(p["phase"])).get(el, 1.0), 1e-6) / 100.0
        self.part_truth = float(min(share, 0.12))              # content: illustrative)
        Tp = self.prim[0][1] if self.prim else t["T_alpha_liquidus_C"]
        n0 = 40
        lead_T = np.linspace(Tp + 6.0, t["T_alpha_liquidus_C"], n0, endpoint=False)
        lead_p = np.linspace(0.0, 1.0, n0, endpoint=False)
        self.cur_truth = dict(x=np.concatenate([np.zeros(n0), t["fs"] * 100.0]),
                              y=np.concatenate([lead_T, t["T_C"]]),
                              fs=np.concatenate([np.zeros(n0), t["fs"]]),
                              grow=np.concatenate([lead_p, np.ones(len(t["fs"]))]), part=self.part_truth, lead=n0)
        self.has_calc = self.calc is not None
        if self.has_calc:
            c = self.calc
            T, fs = np.asarray(c["T_C"], float), np.asarray(c["fraction_solid"], float)
            i0 = max(0, int(np.argmax(T <= WIDE[1] - 6.0)))
            ifcc = int(np.argmax(c["phases"]["FCC_A1"] > 1e-6)) if "FCC_A1" in c["phases"] else len(T) - 1
            part = float(fs[max(ifcc - 1, 0)])                 # what had frozen before the matrix started
            grow = np.clip(fs / max(part, 1e-9), 0.0, 1.0)
            self.cur_calc = dict(x=fs[i0:] * 100.0, y=T[i0:], fs=fs[i0:], grow=grow[i0:], part=part)
            ph = []
            for key, arr in c["phases"].items():
                i = int(np.argmax(np.asarray(arr) > 1e-6))
                ph.append(dict(key=key, name=phase_name(key), fs=float(fs[i]), T=float(T[i]),
                               end=float(np.asarray(arr)[-1])))
            self.phases = sorted(ph, key=lambda p: -p["T"])
            self.left_out = ", ".join(c["left_out"])
        for cur, lim in ((self.cur_open, TIGHT), (self.cur_truth, WIDE)) + \
                (((self.cur_calc, WIDE),) if self.has_calc else ()):
            cur["arc"] = self._arc(cur["x"], cur["y"], lim)
        self._order = {}
        self.captions = [
            (0.6, 8.4, "CALPHAD runs on the BYU HPC: pycalphad on open databases, Thermo-Calc as an interface. "
                       "This curve is the open-database node's, the one the optimizer sees."),
            (8.6, 19.5, "The same alloy three ways: the node's fast model, a full Scheil run on an open database, "
                        "and the twin's hidden truth. They differ, as a simulator differs from a real alloy."),
            (19.8, 26.6, "From its curve the node reads the liquidus, the freezing range, a hot-cracking index and "
                         "a growth-restriction factor."),
            (26.8, 33.2, "The network's print node takes two of them, the liquidus and the cracking index. The "
                         "atomizer's melt is set from the same liquidus."),
        ]
        self.marks = {"scheil.cool": self.T_OPEN[0], "scheil.phases": self.T_CALC[0], "scheil.truth": self.T_TRUTH[0],
                      "scheil.indicators": self.T_LIQ, "scheil.range": self.T_RANGE, "scheil.crack": self.T_KOU,
                      "scheil.net": self.T_NET}
        self.sources = [
            ("sim", "the open-database node's curve and its four numbers: twin/thermo.py AlSolidification('open') and "
                    "AlTruth.sim_open, for the alloy followed"),
            ("calc", "pycalphad + scheil on MatCalc mc_al (open database), for the elements it has "
                     "(out/twin3b/video/experiments/scheil_open.json)"),
            ("sim", "the hidden truth's curve and primary intermetallics: AlSolidification('truth')"),
            ("illus", "the picture of the melt: grains and particles drawn so that the solid share equals the curve's "
                      "fraction solid"),
        ]

    # ------------------------------------------------------------------------------------------ helpers
    def _arc(self, x, y, ylim) -> np.ndarray:
        """Cumulative length of the curve as it lies in the plot with y limits ylim, 0..1 (the pen's even speed)."""
        x0, y0, x1, y1 = self.BOX
        X_ = x0 + np.asarray(x) / 100.0 * (x1 - x0)
        Y_ = y1 - (np.clip(np.asarray(y), ylim[0], ylim[1]) - ylim[0]) / (ylim[1] - ylim[0]) * (y1 - y0)
        seg = np.hypot(np.diff(X_), np.diff(Y_))
        return np.concatenate([[0.0], np.cumsum(seg)]) / max(float(seg.sum()), 1e-9)

    @staticmethod
    def _at(cur: dict, u: float) -> tuple:
        """(index as a float, T, fraction solid, share of the particles grown) at pen progress u."""
        f = float(np.interp(min(max(u, 0.0), 1.0), cur["arc"], np.arange(len(cur["arc"]))))
        i = min(int(f), len(cur["x"]) - 2)
        w = f - i
        T = cur["y"][i] + (cur["y"][i + 1] - cur["y"][i]) * w
        fs = cur["fs"][i] + (cur["fs"][i + 1] - cur["fs"][i]) * w
        g = 1.0
        if "grow" in cur:
            g = cur["grow"][i] + (cur["grow"][i + 1] - cur["grow"][i]) * w
        return f, float(T), float(fs), float(g)

    def _zoom(self, t: float) -> float:
        return ramp(t, *self.T_OUT) * (1.0 - ramp(t, *self.T_IN))

    def _ylim(self, t: float) -> tuple:
        z = self._zoom(t)
        return TIGHT[0] + (WIDE[0] - TIGHT[0]) * z, TIGHT[1] + (WIDE[1] - TIGHT[1]) * z

    def _curve(self, cv: Canvas, ax: Axes, cur: dict, upto: float, fill, width: float, a: float):
        """The curve up to index ``upto`` (a float), cut at the plot's top and bottom. Returns the pen's place in
        design units, or None when it is outside the plot."""
        if a <= 0.004 or upto <= 0:
            return None
        n = len(cur["x"])
        f = min(upto, n - 1.0)
        i = int(f)
        xs, ys = list(cur["x"][:i + 1]), list(cur["y"][:i + 1])
        if i < n - 1 and f > i:
            w = f - i
            xs.append(cur["x"][i] + (cur["x"][i + 1] - cur["x"][i]) * w)
            ys.append(cur["y"][i] + (cur["y"][i + 1] - cur["y"][i]) * w)
        lo, hi = ax.ylim
        runs, run = [], []
        for j in range(len(xs)):
            inside = lo <= ys[j] <= hi
            if j > 0:
                pin = lo <= ys[j - 1] <= hi
                if inside != pin:                              # the curve crosses an edge between j - 1 and j
                    edge = lo if (ys[j] < lo or ys[j - 1] < lo) else hi
                    w = (edge - ys[j - 1]) / (ys[j] - ys[j - 1])
                    px_ = xs[j - 1] + (xs[j] - xs[j - 1]) * w
                    run.append((float(ax.X(px_)), float(ax.Y(edge))))
                    if pin:
                        runs.append(run)
                        run = []
            if inside:
                run.append((float(ax.X(xs[j])), float(ax.Y(ys[j]))))
        if run:
            runs.append(run)
        for r in runs:
            if len(r) >= 2:
                cv.aaline(G._thin(np.array(r)), fill, width, a)
        if lo <= ys[-1] <= hi:
            return float(ax.X(xs[-1])), float(ax.Y(ys[-1]))
        return None

    # ------------------------------------------------------------------------------------------ the melt
    def _orders(self, part: float) -> tuple:
        """(order of freezing 0..1, is-particle mask) for a run whose first ``part`` of the solid is particles."""
        key = round(part, 4)
        if key not in self._order:
            F = self.F
            if part <= 0:
                self._order[key] = (F["order"], np.zeros_like(F["order"], bool))
            else:
                isp = F["part"] <= part
                o = np.where(isp, F["part"], 0.0)
                rest = _rank(np.where(isp, -1.0, F["order"]))      # the particles' points rank first, then drop out
                o = np.where(isp, o, part + (1.0 - part) * np.clip((rest - part) / (1.0 - part), 0, 1))
                self._order[key] = (o, isp)
        return self._order[key]

    def _melt(self, part: float, grow: float, fs: float, T: float) -> Image.Image:
        """The picture: liquid tinted by temperature, grains (and particles) up to the fraction solid."""
        order, isp = self._orders(part)
        total = part * grow + (1.0 - part) * fs if part > 0 else fs
        if part > 0 and grow < 1.0:
            total = part * grow                                # only the particles are growing yet
        soft = 0.006
        al = np.clip((total * (1.0 + soft) - soft / 2 - order) / soft + 0.5, 0.0, 1.0)[..., None]
        u = min(1.0, max(0.0, (T - 600.0) / 200.0))
        liq = np.array(mix((208, 78, 34), (255, 204, 104), u), float)
        sol = np.array(mix((128, 156, 198), (176, 172, 196), 0.5 * u), float)
        img = np.empty(order.shape + (3,), float)
        img[:] = liq
        solid = self.F["tint"][..., None] * sol[None, None, :]
        solid = np.where(isp[..., None], np.array((240, 242, 248), float)[None, None, :], solid)
        img = img * (1 - al) + solid * al
        _, _, side = self.MELT
        return G.to_image(np.clip(img, 0, 255).astype(np.uint8), side, side, Image.BILINEAR)

    def _state(self, t: float) -> dict:
        """What the picture of the melt shows at t: which run, its temperature and fraction solid."""
        o = self.op
        if t < self.T_OUT[0] + 0.5:
            _, T, fs, _ = self._at(self.cur_open, lin(t, *self.T_OPEN))
            return dict(run="open", part=0.0, grow=1.0, fs=fs, T=T)
        if self.has_calc and t < self.T_TRUTH[0] - 0.3:
            _, T, fs, g = self._at(self.cur_calc, lin(t, *self.T_CALC))
            p = self.cur_calc["part"]
            fm = 0.0 if g < 1.0 else (fs - p) / max(1e-9, 1.0 - p)
            return dict(run="calc", part=p, grow=g, fs=fm, T=T, shown=fs)
        if t < self.T_IN[0] + 0.5:
            _, T, fs, g = self._at(self.cur_truth, lin(t, *self.T_TRUTH))
            return dict(run="truth", part=self.part_truth, grow=g, fs=fs, T=T)
        # the indicators, on the node's curve again
        lo, hi = o["kou_window"]
        if t < self.T_RANGE:
            fs = 0.0
        elif t < self.T_KOU:
            fs = 0.98 * St.ease(lin(t, self.T_RANGE, self.T_KOU - 0.3))
        else:
            fs = lo + (hi - lo) * lin(t, self.T_KOU + 0.2, self.T_Q - 0.2)
        T = float(np.interp(fs, o["fs"], o["T_C"]))
        return dict(run="open", part=0.0, grow=1.0, fs=fs, T=T)

    # ------------------------------------------------------------------------------------------ the frame
    def static_extra(self, cv: Canvas):
        cv.card((56, 150, 900, 936), "The model")
        cv.card((940, 150, 1864, 936), "Its output")
        x, y, s = self.MELT
        cv.tag(x, y + s + 14, "illus", "how a melt freezes; the solid share drawn is the curve's fraction solid")
        cv.text(1052, 198, "Temperature against fraction solid, as the melt cools", 24, bold=True, fill=INK)

    def _left(self, cv: Canvas, t: float):
        st = self._state(t)
        x, y, s = self.MELT
        cv.paste(self._melt(st["part"], st["grow"], st["fs"], st["T"]), x, y)
        G.framed(cv, (x, y, x + s, y + s))
        cx = x + s + 26
        name = {"open": ("the open-database", "node"), "calc": ("pycalphad + scheil", "(open database)"),
                "truth": ("the twin's", "hidden truth")}[st["run"]]
        colr = {"open": self.col, "calc": CALC, "truth": TRUTH}[st["run"]]
        cv.text(cx, 212, "the model running", 17, cond=True, fill=INK2)
        cv.rect((cx, 244, cx + 44, 250), fill=colr, radius=3)
        cv.text(cx, 258, name[0], 21, bold=True, fill=INK)
        cv.text(cx, 286, name[1], 21, bold=True, fill=INK)
        shown = st.get("shown")
        if shown is None:
            shown = st["fs"] if st["grow"] >= 1.0 else 0.0
        cv.value(cx, 346, "temperature", fmt(st["T"]), "°C", size=46, label_size=18)
        cv.value(cx, 462, "fraction solid", fmt(math.floor(100.0 * shown + 1e-6)), "%", size=46, label_size=18)
        yy = 590
        for colr_, lab in (((232, 141, 69), "liquid"), ((128, 156, 198), "aluminium grains (fcc)"),
                           ((240, 242, 248), "intermetallic particles")):
            if lab.startswith("inter") and st["part"] <= 0:
                continue
            cv.rect((cx, yy, cx + 22, yy + 22), fill=colr_, outline=(20, 22, 26), width=1, radius=4)
            cv.text(cx + 32, yy + 11, lab, 17, cond=True, fill=INK2, anchor="lm")
            yy += 34
        # under the picture: what the model assumes, why the last liquid matters, then what round 3b's runs used
        ks = ramp(t, 0.6, 1.4) * (1 - ramp(t, self.T_KOU - 0.6, self.T_KOU - 0.1))
        if ks > 0:
            cv.para(x, 812, "Scheil's model: the liquid stays mixed and the solid, once frozen, keeps the "
                            "composition it froze with. So the remaining liquid grows richer in solute and freezes "
                            "at lower and lower temperatures.", 20, 800, fill=INK, a=ks)
        kk = ramp(t, self.T_KOU, self.T_KOU + 0.6) * (1 - ramp(t, self.T_NET - 0.5, self.T_NET))
        if kk > 0:
            cv.para(x, 812, "Hot cracks open where the last liquid films between the grains are pulled apart. The "
                            "steeper the temperature falls there, the longer the films last (Kou, 2015).", 20, 800,
                    fill=INK, a=kk)
        kn = ramp(t, self.T_NET, self.T_NET + 0.7)
        if kn > 0:
            k = self.kinds
            calls = sum(k["calls"].values())
            only = set(k["calls"]) == {"sim_open"}
            lead = (f"Round 3b: all {fmt(k['logs'])} runs called this open-database node and no other "
                    f"({calls:,} calls)." if only else
                    f"Round 3b: {fmt(k['logs'])} runs, {calls:,} simulation calls.")
            y2 = cv.para(x, 808, lead, 20, 800, fill=INK, a=kn, bold=True)
            cv.para(x, y2 + 4, "The twin also has a Thermo-Calc stand-in: the truth with a few percent error. No "
                               "run bought it, and nothing here is Thermo-Calc output.", 19, 800, fill=INK2, a=kn)

    def _right(self, cv: Canvas, t: float):
        o, col = self.op, self.col
        ax = Axes(self.BOX, (0.0, 100.0), self._ylim(t), "fraction solid, %", "temperature, °C",
                  xticks=[0, 20, 40, 60, 80, 100], yticks=list(range(560, 841, 20)))
        ax.draw(cv)
        z = self._zoom(t)
        late = ramp(t, self.T_IN[0], self.T_IN[1])               # the other two step back for the indicators
        n_open = len(self.cur_open["x"])
        # --- the hidden truth
        ut = lin(t, *self.T_TRUTH)
        if ut > 0:
            ft = self._at(self.cur_truth, ut)[0]
            a_t = 1.0 - 0.62 * late
            cur = self.cur_truth
            body = dict(x=cur["x"][cur["lead"]:], y=cur["y"][cur["lead"]:])
            pen = self._curve(cv, ax, body, ft - cur["lead"], TRUTH, 3.0, a_t)
            Tn = self._at(cur, ut)[1]
            lab_a = (1.0 - late) * z
            lx = float(ax.X(40.0))                               # its primary intermetallics, above the matrix:
            last = None                                          # labels in one column, kept 27 units apart
            for nm, Tp in self.prim:
                k = (ramp(-Tn, -Tp - 3.0, -Tp + 3.0) if ut < 1 else 1.0) * z
                if not (ax.ylim[0] <= Tp <= ax.ylim[1]):
                    continue
                Y_ = float(ax.Y(Tp))
                ly = Y_ if last is None else max(Y_, last + 27.0)
                last = ly
                if k <= 0:
                    continue
                x0 = self.BOX[0]
                cv.poly([(x0, Y_ - 8), (x0 + 8, Y_), (x0, Y_ + 8), (x0 - 8, Y_)], fill=TRUTH, outline=(20, 22, 26),
                        a=k * a_t)
                cv.line([(x0 + 12, Y_), (lx - 40, Y_), (lx - 8, ly)], (130, 134, 144), 1, a=k * lab_a)
                cv.text(lx, ly, f"{nm} first, {fmt(Tp)} °C", 17, fill=INK, anchor="lm", a=k * lab_a)
            if pen and 0 < ut < 1:
                cv.circle(pen[0], pen[1], 7, fill=TRUTH, outline=(20, 22, 26), width=2)
        # --- the open-database Scheil run and its phases
        uc = lin(t, *self.T_CALC) if self.has_calc else 0.0
        if uc > 0:
            fc, Tn, _, _ = self._at(self.cur_calc, uc)
            a_c = 1.0 - 0.62 * late
            pen = self._curve(cv, ax, self.cur_calc, fc, CALC, 3.6, a_c)
            lab_a = (1.0 - ramp(t, self.T_TRUTH[0] - 0.5, self.T_TRUTH[0])) * z
            place = {"AL4CR": (14, 0, "lm"), "AL3TI_H": (14, 0, "lm"), "FCC_A1": (10, -16, "ls"),
                     "AL6MN": (0, 44, "ma"), "AL3ZR": (-70, 44, "ma"), "AL3NI": (-2, -40, "rs")}
            for p in self.phases:
                k = (ramp(-Tn, -p["T"] - 1.5, -p["T"] + 1.5) if uc < 1 else 1.0)
                if p["fs"] > 0.5:
                    k = ramp(self._at(self.cur_calc, uc)[2], p["fs"] - 0.02, p["fs"]) if uc < 1 else 1.0
                if k <= 0 or not (ax.ylim[0] <= p["T"] <= ax.ylim[1]):
                    continue
                X_, Y_ = float(ax.X(100 * p["fs"])), float(ax.Y(p["T"]))
                cv.circle(X_, Y_, 7.5, fill=(20, 22, 26), a=k * a_c)
                cv.circle(X_, Y_, 5.5, fill=CALC, a=k * a_c)
                dx, dy, anc = place.get(p["key"], (14, 0, "lm"))
                if abs(dy) > 20:
                    cv.line([(X_, Y_ + (9 if dy > 0 else -9)), (X_ + dx, Y_ + dy + (-4 if dy > 0 else 4))],
                            (130, 134, 144), 1, a=k * lab_a)
                cv.text(X_ + dx, Y_ + dy, f"{p['name']}, {fmt(p['T'])} °C", 17, fill=INK, anchor=anc, a=k * lab_a)
            if pen and 0 < uc < 1:
                cv.circle(pen[0], pen[1], 7, fill=CALC, outline=INK, width=2)
        # --- the node's curve
        uo = lin(t, *self.T_OPEN)
        fo = self._at(self.cur_open, uo)[0]
        pen = self._curve(cv, ax, self.cur_open, fo if uo < 1 else n_open - 1.0, col, 4.4, 1.0)
        if pen and 0 < uo < 1:
            cv.circle(pen[0], pen[1], 8, fill=G.HOT, outline=INK, width=2)
        # --- the indicators, on the node's curve
        TL, T98 = o["T_alpha_liquidus_C"], o["T_98_C"]
        kl = ramp(t, self.T_LIQ, self.T_LIQ + 0.5)
        if kl > 0:
            X_, Y_ = ax.dot(cv, 0.0, TL, G.HOT, 7, a=kl)
            cv.text(X_ + 18, Y_ - 14, "liquidus: the first solid", 18, fill=INK, anchor="ls", a=kl)
        kr = ramp(t, self.T_RANGE, self.T_RANGE + 0.6)
        if kr > 0:
            xb = float(ax.X(98.0))
            cv.dashed([(float(ax.X(0)), float(ax.Y(TL))), (xb, float(ax.Y(TL)))], INK2, 2, 9, 6, kr)
            yb = float(ax.Y(TL)) + (float(ax.Y(T98)) - float(ax.Y(TL))) * kr
            cv.line([(xb, float(ax.Y(TL))), (xb, yb)], G.HOT, 4, kr)
            for yy in (float(ax.Y(TL)), yb):
                cv.line([(xb - 9, yy), (xb + 9, yy)], G.HOT, 4, kr)
            cv.text(xb - 16, float(ax.Y(TL)) + 24, "freezing range: liquidus to 98 % solid", 18, fill=INK,
                    anchor="rm", a=kr)
        kk = ramp(t, self.T_KOU, self.T_KOU + 0.6)
        if kk > 0:
            lo, hi = o["kou_window"]
            sl, ic = o["kou_fit"]
            fsx = np.linspace(max(0.0, lo - 0.22), min(0.985, hi + 0.09), 40)
            fit = ic + sl * np.sqrt(fsx)
            cv.dashed([(float(ax.X(100 * a_)), float(ax.Y(b_))) for a_, b_ in zip(fsx, fit)
                       if ax.ylim[0] <= b_ <= ax.ylim[1]], INK, 2, 8, 6, kk)
            sel = (o["fs"] >= lo) & (o["fs"] <= hi)
            pts = [(float(ax.X(100 * a_)), float(ax.Y(b_))) for a_, b_ in zip(o["fs"][sel], o["T_C"][sel])]
            if len(pts) >= 2:
                cv.aaline(pts, G.HOT, 8.0, kk)
            xm = float(ax.X(100 * (lo + hi) / 2))
            ym = float(ax.Y(float(np.interp((lo + hi) / 2, o["fs"], o["T_C"]))))
            xr = float(ax.X(100 * hi)) - 4
            cv.line([(xm, ym + 8), (xm, ym + 40)], (130, 134, 144), 1, a=kk)
            cv.text(xr, ym + 44, "cracking index: how steeply the temperature falls", 18, fill=INK, anchor="ra", a=kk)
            cv.text(xr, ym + 68, "against √(fraction solid), fitted over this stretch", 18, fill=INK, anchor="ra",
                    a=kk)
        # --- under the plot: the three curves and where each comes from
        x0 = self.BOX[0]
        rows = [(self.T_OPEN[0], col, "sim", "the open-database node: the twin's fast Scheil model, fitted to "
                                              "pycalphad")]
        if self.has_calc:
            rows.append((self.T_CALC[0], CALC, "calc", f"pycalphad + scheil on MatCalc mc_al (open database); "
                                                       f"{self.left_out} are not in it"))
        rows.append((self.T_TRUTH[0], TRUTH, "sim", "the twin's hidden truth (assessed diagrams); no policy sees it"))
        for j, (t0, colr, kind, words) in enumerate(rows):
            k = ramp(t, t0 - 0.1, t0 + 0.5)
            yy = 666 + j * 36
            cv.rect((x0, yy + 12, x0 + 46, yy + 18), fill=colr, radius=3, a=k)
            cv.tag(x0 + 60, yy, kind, words, a=k)
        # --- the open-database run's phases at the end, then the node's four numbers
        if self.has_calc:
            kp = ramp(t, self.T_CALC[1] - 0.4, self.T_CALC[1] + 0.3) * (1 - ramp(t, self.T_IN[0] - 0.3, self.T_IN[0] + 0.3))
            if kp > 0:
                cv.text(x0, 788, "frozen by the end of the pycalphad + scheil run, mol %", 18, cond=True, fill=INK2,
                        a=kp)
                xx = x0
                for p in sorted(self.phases, key=lambda p: -p["end"]):
                    v = 100.0 * p["end"]
                    s_ = f"{p['name']} {v:.1f}" if v >= 1 else f"{p['name']} {v:.2f}"
                    w = cv.text_w(s_, 17, bold=True) + 18
                    cv.rect((xx, 818, xx + w, 850), fill=(30, 28, 44), outline=mix(G.CARD_EDGE, CALC, 0.6), width=2,
                            radius=8, a=kp)
                    cv.text(xx + w / 2, 834, s_, 17, bold=True, fill=INK, anchor="mm", a=kp)
                    xx += w + 8
        s = self.sim
        outs = (("liquidus", fmt(s["liquidus_C"]), "°C", self.T_LIQ + 0.3, True),
                ("freezing range", fmt(s["freezing_range_K"]), "K", self.T_RANGE + 0.5, False),
                ("cracking index", fmt(s["kou_K"]), "K", self.T_KOU + 0.7, True),
                ("growth restriction, Q", fmt(s["Q_K"]), "K", self.T_Q, False))
        kn = ramp(t, self.T_NET, self.T_NET + 0.6)
        for j, (lab, val, unit, t0, used) in enumerate(outs):
            k = ramp(t, t0, t0 + 0.5)
            if k <= 0:
                continue
            x = x0 + j * 196
            if used and kn > 0:
                cv.rect((x - 12, 778, x + 172, 870), fill=mix(G.CARD_FILL, col, 0.30 * kn),
                        outline=mix(G.CARD_EDGE, col, kn), width=3, radius=10)
            cv.value(x, 788, lab, val, unit, a=k, size=38, label_size=17)
        cv.text(x0, 888, "→ the print node takes two: the liquidus and the cracking index", 20, bold=True, fill=INK,
                a=kn)

    def draw(self, cv: Canvas, t: float):
        self._left(cv, t)
        self._right(cv, t)


if __name__ == "__main__":
    import sys
    import time
    seg = Scheil()
    for tt in [float(v) for v in sys.argv[1:]] or [2.5, 6.5, 9.0, 12.0, 15.6, 18.0, 21.5, 24.5, 26.0, 30.9]:
        t0 = time.time()
        fr = seg.frame(tt)
        Image.fromarray(fr).save(f"/tmp/vid/exp_scheil_{tt:05.1f}.png")
        print("wrote", f"/tmp/vid/exp_scheil_{tt:05.1f}.png", f"{time.time() - t0:.2f} s")
    seg.close()
