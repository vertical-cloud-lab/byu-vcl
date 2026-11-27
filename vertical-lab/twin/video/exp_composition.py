"""Composition: one design on the periodic table, its fractions filling in, and where it sits in its search space; for
the aluminium alloy followed, then for the copper one (twin/video/exp_composition.py).

    Composition().frame(t)      0 <= t <= Composition.DURATION     (aluminium, then copper)

What is what on screen:

* **The design** (its elements and their wt%) and **the run's other designs** are read from the committed event log of
  the run the video replays (``exp_data.Alloy.run_designs``): every design the campaign's policy simulated, which of
  them it made into powder or deposited, and which it demonstrated (tested to the end).
* **The search space** (which elements, each element's upper bound, how many may be in one design) is the proposals'
  (twin/spaces.py). A tile fills to the design's share of that element's upper bound; so does its bar.
* **The map** is a projection, and says so: the first two principal components of the run's designs, each composition
  axis scaled by its bound. Its axes have no units, and it carries only part of the spread (the share is on screen).

Nothing here is measured or modelled: it is the input of the network.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

from . import exp_data as X
from . import exp_draw as G
from . import ptable as PT
from . import style as St
from .exp_draw import Axes, Canvas, Segment, fmt, ramp
from .style import CAMP, INK, INK2, mix

TARGET_WORDS = {"T1": "the best existing alloy on this synthetic benchmark", "T2": "the halfway target"}
TARGET_SHORT = {"T1": ("past the best existing alloy", "on this synthetic benchmark"), "T2": ("past the halfway target",)}
NAME = {"flaime_al": "aluminium", "onr_cu": "copper"}
LEAD = {"flaime_al": "FLAIME: aluminium alloys for laser powder bed fusion.",
        "onr_cu": "ONR: copper alloys designed as powders for blown-powder DED."}
EMPTY_EDGE, EMPTY_INK = (58, 61, 68), (98, 101, 108)
ZERO_FILL, ZERO_INK, ZERO_EDGE = (36, 39, 46), (176, 179, 186), (150, 154, 164)
BAL_FILL = (84, 88, 98)
SIM_DOT, MADE_DOT = (104, 108, 118), (176, 180, 190)


def _wt(v: float) -> str:
    return f"{v:.2f}" if v < 9.995 else f"{v:.1f}"


def pca2(designs: dict, bounds: dict) -> tuple:
    """The run's designs on their first two principal components: each composition axis divided by its upper bound,
    centred, then numpy's SVD. Returns ({id: (x, y)}, share of the spread the two carry). Signs are fixed so that
    each component's largest loading is positive (an SVD's signs are arbitrary)."""
    els = list(bounds)
    ids = sorted(designs)
    M = np.array([[float(designs[i].get(e, 0.0)) / float(bounds[e][1]) for e in els] for i in ids])
    M = M - M.mean(0)
    _, s, Vt = np.linalg.svd(M, full_matrices=False)
    V = Vt[:2].copy()
    for k in range(2):
        if V[k][int(np.argmax(np.abs(V[k])))] < 0:
            V[k] = -V[k]
    P = M @ V.T
    share = float((s[:2] ** 2).sum() / (s ** 2).sum())
    return {i: (float(P[j, 0]), float(P[j, 1])) for j, i in enumerate(ids)}, share


class _Half(Segment):
    """One alloy: its table, its fractions, its place among the run's designs."""
    key = "composition"
    title = "Composition: one design in its search space"
    nodes = ("composition",)
    done = ()
    # the left card and the table in it
    CARD_L = (56, 150, 1150, 936)
    CARD_R = (1186, 150, 1864, 936)
    TX0, TY0 = 79.0, 208.0
    PITCH = (1094 - 46) / 18.0
    PLOT = (1262, 226, 1836, 606)
    LEG_Y = 684                   # the first legend row under the map

    def __init__(self, campaign: str, duration: float, t_space: tuple, t_light: float, step: float, t_map: tuple):
        super().__init__()
        self.campaign = campaign
        self.DURATION = duration
        self.T_SPACE, self.T_LIGHT, self.STEP, self.T_MAP = t_space, t_light, step, t_map
        a = X.alloy(campaign)
        self.alloy = a
        self.f = X.follow()[campaign]
        self.base = a.base
        self.bounds = {e: (float(lo), float(hi)) for e, (lo, hi) in a.space.bounds.items()}
        self.kmax = int(a.space.k_range[1])
        self.order = sorted(a.design, key=lambda e: -a.design[e])          # the design's elements, largest first
        self.t_on = {e: t_light + i * step for i, e in enumerate(self.order)}
        self.T_LIT = t_light + len(self.order) * step                       # every element is in
        self.T_RING = t_map[1]
        rd = a.run_designs()
        self.rd = rd
        ids = set(rd["designs"])
        shown = set(rd["shown"]) & ids
        worked = ((set(rd["made"]) | set(rd["built"])) & ids) - shown
        self.groups = dict(sim=sorted(ids - worked - shown), made=sorted(worked), shown=sorted(shown))
        self.counts = {k: len(v) for k, v in self.groups.items()}
        self.xy, self.share = pca2(rd["designs"], self.bounds)
        xs = np.array([p[0] for p in self.xy.values()])
        ys = np.array([p[1] for p in self.xy.values()])
        px_, py_ = 0.06 * (xs.max() - xs.min()), 0.07 * (ys.max() - ys.min())
        self.ax = Axes(self.PLOT, (xs.min() - px_, xs.max() + px_), (ys.min() - py_, ys.max() + py_),
                       "principal component 1 of composition", "principal component 2 of composition",
                       xticks=[], yticks=[])
        self._layers = None
        col = CAMP[campaign]
        self.col = col
        n_space, n_in = len(self.bounds), len(self.order)
        self.n_space, self.n_in = n_space, n_in
        day = fmt(self.f["day"])
        ts = TARGET_SHORT[self.f["target"]]                  # the label on the map: a bold line, then one or two more
        self.words = (f"design {a.design_id} · seed {a.seed}", f"day {day}: {ts[0]}") + tuple(ts[1:])
        self.captions = [
            (0.4, t_map[0] - 0.2, f"{LEAD[campaign]} A design is {NAME[campaign]} plus up to {self.kmax} of "
                                  f"{n_space} {'alloying ' if campaign == 'flaime_al' else ''}elements."),
            (t_map[0], duration - 0.3, f"This is design {a.design_id} of the replayed run, seed {a.seed}: the alloy "
                                       f"that took it past {TARGET_WORDS[self.f['target']]}, on day {day}."),
        ]
        self.sources = [
            ("sim", f"the design and the run's other designs: the committed event log of seed {a.seed} "
                    f"({self.f['run']})"),
            ("sim", "the search space, its bounds and how many elements a design may have: twin/spaces.py (the "
                    "proposals')"),
            ("illus", "the map: a projection (two principal components of composition scaled by the bounds)"),
        ]

    # ------------------------------------------------------------------------------------------ the table
    def _cell(self, el: str) -> tuple:
        c, r = PT._cell_xy(el)
        return self.TX0 + c * self.PITCH, self.TY0 + r * self.PITCH, self.PITCH * (1 - PT.GAP)

    def _tile_empty(self, cv: Canvas, el: str):
        x, y, s = self._cell(el)
        cv.rect((x, y, x + s, y + s), outline=EMPTY_EDGE, width=1)
        cv.text(x + s / 2, y + s / 2, el, 17, fill=EMPTY_INK, anchor="mm")

    def _tile_space(self, cv: Canvas, el: str, k: float):
        """An element of the search space, not (yet) in the design: k = 0 as any other tile, 1 outlined."""
        x, y, s = self._cell(el)
        cv.rect((x, y, x + s, y + s), fill=mix(G.CARD_FILL, ZERO_FILL, k), outline=mix(EMPTY_EDGE, ZERO_EDGE, k),
                width=2 if k > 0.5 else 1)
        cv.text(x + s / 2, y + s / 2, el, 17 + 4 * k, bold=k > 0.5, fill=mix(EMPTY_INK, ZERO_INK, k), anchor="mm")

    def _tile_balance(self, cv: Canvas, k: float, a: float = 1.0):
        el = self.base
        x, y, s = self._cell(el)
        cv.rect((x, y, x + s, y + s), fill=mix(G.CARD_FILL, BAL_FILL, k), outline=mix(EMPTY_EDGE, INK, k), width=2)
        if k > 0.02:
            for i in range(1, 8):                          # hatched: the balance element
                d = s * i / 4.0
                p0 = (x + min(d, s), y + max(0.0, d - s))
                p1 = (x + max(0.0, d - s), y + min(d, s))
                cv.line([p0, p1], (118, 122, 132), 1, a=k * 0.9)
        cv.text(x + s / 2, y + s * 0.36, el, 21, bold=True, fill=INK, anchor="mm", stroke=1.5)
        cv.text(x + s / 2, y + s * 0.76, _wt(self.alloy.comp[el]), 16, fill=INK, anchor="mm", a=k * a, stroke=1.5)

    def _tile_design(self, cv: Canvas, el: str, u: float):
        """An element of the design lighting up: u in 0..1; its tile fills from the bottom to the design's share
        of the element's upper bound."""
        x, y, s = self._cell(el)
        v = self.alloy.design[el]
        share = min(1.0, v / self.bounds[el][1])
        on = St.ease_out(min(1.0, u / 0.35))
        cv.rect((x, y, x + s, y + s), fill=ZERO_FILL, outline=mix(ZERO_EDGE, INK, on), width=2)
        h = (s - 4) * share * St.ease(min(1.0, max(0.0, (u - 0.1) / 0.75)))
        if h > 0.5:
            cv.rect((x + 2, y + s - 2 - h, x + s - 2, y + s - 2), fill=self.col)
        if u < 1.0:                                        # a ring of light as it comes on
            g = (1 - u) ** 2
            cv.rect((x - 5 * g - 1, y - 5 * g - 1, x + s + 5 * g + 1, y + s + 5 * g + 1), outline=G.HOT, width=3,
                    a=g)
        cv.text(x + s / 2, y + s * 0.36, el, 21, bold=True, fill=INK, anchor="mm", stroke=1.5)
        cv.text(x + s / 2, y + s * 0.76, _wt(v), 16, fill=INK, anchor="mm", a=ramp(u, 0.25, 0.7), stroke=1.5)

    def static_extra(self, cv: Canvas):
        a = self.alloy
        cv.card(self.CARD_L, f"The design: {NAME[self.campaign]} plus {self.n_in} of the search space's "
                             f"{self.n_space} elements")
        cv.card(self.CARD_R, f"Where it sits among this run's {len(a.run_designs()['designs'])} designs")
        for el in PT.PTABLE_RC:
            if el != self.base and el not in self.bounds:
                self._tile_empty(cv, el)
        # the table's empty top middle: which design, and how to read a tile
        x0 = self.TX0 + 2 * self.PITCH + 14
        y0 = self.TY0 + 4
        cv.text(x0, y0, self.words[0], 26, bold=True, fill=INK)
        cv.text(x0, y0 + 40, f"of the replayed run ({self.f['run']})", 17, cond=True, fill=INK2)
        sw = 26
        yy = y0 + 76
        cv.rect((x0, yy, x0 + sw, yy + sw), fill=ZERO_FILL, outline=ZERO_EDGE, width=2)
        cv.text(x0 + sw + 12, yy + sw / 2, f"in the search space: {self.n_space} elements with upper bounds", 18,
                fill=INK2, anchor="lm")
        yy += 40
        cv.rect((x0, yy, x0 + sw, yy + sw), fill=ZERO_FILL, outline=INK, width=2)
        cv.rect((x0 + 2, yy + sw * 0.45, x0 + sw - 2, yy + sw - 2), fill=self.col)
        cv.text(x0 + sw + 12, yy + sw / 2 - 1, "in this design: its wt%, and the tile filled to", 18, fill=INK2,
                anchor="lm")
        cv.text(x0 + sw + 12, yy + sw / 2 + 23, "that share of the element's upper bound", 18, fill=INK2,
                anchor="lm")
        # the fractions' frame
        cv.text(79, 652, "Its fractions, wt%", 22, bold=True, fill=INK)
        cv.text(79 + cv.text_w("Its fractions, wt%", 22, bold=True) + 14, 656,
                "each track runs from 0 to that element's upper bound", 18, cond=True, fill=INK2)
        for i, el in enumerate(self.order):
            x, y, tw = self._bar_xy(i)
            cv.text(x, y, el, 24, bold=True, fill=INK, anchor="lm")
            cv.rect((x + 54, y - 10, x + 54 + tw, y + 10), fill=(34, 38, 46), outline=(74, 78, 88), width=1, radius=4)
            cv.text(x + 54 + tw + 100, y, f"of {self.bounds[el][1]:g}", 17, cond=True, fill=INK2, anchor="lm")
        cv.tag(79, 896, "sim", f"the design: the committed event log of seed {a.seed}; the bounds: the proposals' "
                               f"search space (twin/spaces.py)")
        # the map's frame
        self.ax.draw(cv, grid=False, size=17)
        x0, y0, x1, y1 = self.PLOT
        cv.para(1210, 812, f"A projection: the {self.n_space} composition axes, each scaled by its bound, on their "
                           f"first two principal components. The two carry {100 * self.share:.0f} % of the spread, "
                           f"so near on the map is only roughly near in composition.", 17, 630, fill=INK2,
                cond=True)
        cv.tag(1210, 896, "sim", f"every design in the log of seed {a.seed}")

    def _bar_xy(self, i: int) -> tuple:
        """(x of the symbol, y of the row's middle, the track's width) of row i of the fractions."""
        n = len(self.order)
        if n > 4:                                           # two columns of four
            col_, row = divmod(i, 4)
            return 96 + col_ * 520, 706 + row * 48, 300
        return 96, 712 + i * 56, 720

    # ------------------------------------------------------------------------------------------ the map
    def _point_layers(self) -> dict:
        """Each class of designs as an RGBA layer over the plot (drawn once)."""
        if self._layers is None:
            x0, y0, x1, y1 = self.PLOT
            S = G.S
            size = (int(round((x1 - x0) * S)), int(round((y1 - y0) * S)))
            out = {}
            for key, colr, r, edge in (("sim", SIM_DOT, 4.0, None), ("made", MADE_DOT, 5.0, None),
                                       ("shown", self.col, 8.0, INK)):
                cv = Canvas(Image.new("RGB", (G.W, G.H), G.PLOT_FILL))
                lay = Image.new("RGBA", (G.W, G.H), (0, 0, 0, 0))
                cv.im, cv.d = lay, ImageDraw.Draw(lay, "RGBA")
                for i in self.groups[key]:
                    if i == self.alloy.design_id:
                        continue
                    px_, py_ = self.xy[i]
                    X_, Y_ = float(self.ax.X(px_)), float(self.ax.Y(py_))
                    if edge is not None:
                        cv.circle(X_, Y_, r + 2, fill=edge)
                    cv.circle(X_, Y_, r, fill=colr)
                out[key] = lay.crop((int(round(x0 * S)), int(round(y0 * S)), int(round(x0 * S)) + size[0],
                                     int(round(y0 * S)) + size[1]))
            self._layers = out
        return self._layers

    def _map(self, cv: Canvas, t: float):
        m0, m1 = self.T_MAP
        x0, y0, x1, y1 = self.PLOT
        lay = self._point_layers()
        when = (self.T_SPACE[0] + 0.8, self.T_LIGHT + 0.5 * (self.T_LIT - self.T_LIGHT), m0)
        keys = (("sim", "simulated only (the CALPHAD node)"),
                ("made", "made into powder" if self.campaign == "flaime_al" else "made into powder or deposited"),
                ("shown", "demonstrated: tested to the end of the chain"))
        for j, (key, lab) in enumerate(keys):
            k = ramp(t, when[j], when[j] + 0.9)
            cv.paste(lay[key], x0, y0, a=k)
            yy = self.LEG_Y + j * 30
            colr, r = ((SIM_DOT, 4.5), (MADE_DOT, 5.5), (self.col, 8.0))[j]
            if j == 2:
                cv.circle(1222, yy, r + 2, fill=INK, a=k)
            cv.circle(1222, yy, r, fill=colr, a=k)
            cv.text(1244, yy, lab, 19, fill=INK, anchor="lm", a=k)
            cv.text(1838, yy, f"{fmt(self.counts[key])}", 19, bold=True, fill=INK, anchor="rm", a=k)
        # this design
        kr = ramp(t, self.T_RING, self.T_RING + 0.7)
        if kr > 0:
            px_, py_ = self.xy[self.alloy.design_id]
            X_, Y_ = float(self.ax.X(px_)), float(self.ax.Y(py_))
            pulse = 1.0 + 0.9 * (1 - St.ease_out(min(1.0, (t - self.T_RING) / 1.1)))
            cv.circle(X_, Y_, 19 * pulse, outline=G.HOT, width=4, a=kr)
            cv.circle(X_, Y_, 10.5, fill=INK, a=kr)
            cv.circle(X_, Y_, 8.5, fill=self.col, a=kr)
            bx, by, w = self._label_box(cv)
            cx = min(max(X_, bx), bx + w)
            bh = self._label_h()
            cy = min(max(Y_, by), by + bh)
            cv.line([(X_ + (cx - X_) * 0.16, Y_ + (cy - Y_) * 0.16), (cx, cy)], G.HOT, 2, a=kr)
            cv.rect((bx, by, bx + w, by + bh), fill=(12, 14, 18, 240), outline=G.HOT, width=2, radius=9, a=kr)
            cv.text(bx + 14, by + 9, self.words[0], 20, bold=True, fill=INK, a=kr)
            for j, ln in enumerate(self.words[1:]):
                cv.text(bx + 14, by + 38 + 26 * j, ln, 18, fill=INK, a=kr)
            yy = self.LEG_Y + 3 * 30
            cv.circle(1222, yy, 11, outline=G.HOT, width=3, a=kr)
            cv.circle(1222, yy, 5.5, fill=self.col, a=kr)
            cv.text(1244, yy, "this design", 19, bold=True, fill=INK, anchor="lm", a=kr)

    def _label_h(self) -> float:
        return 42.0 + 26.0 * (len(self.words) - 1)

    def _label_box(self, cv: Canvas) -> tuple:
        """(x, y, w) of the design's label: the corner of the plot with the fewest designs under it."""
        if getattr(self, "_lbox", None) is None:
            x0, y0, x1, y1 = self.PLOT
            w = max([cv.text_w(self.words[0], 20, bold=True)] + [cv.text_w(ln, 18) for ln in self.words[1:]]) + 28
            bh = self._label_h()
            P = np.array([[float(self.ax.X(x)), float(self.ax.Y(y))] for x, y in self.xy.values()])
            me = self.xy[self.alloy.design_id]
            mx, my = float(self.ax.X(me[0])), float(self.ax.Y(me[1]))
            best = None
            for bx, by in ((x1 - w - 10, y0 + 10), (x0 + 10, y0 + 10), (x1 - w - 10, y1 - bh - 10),
                           (x0 + 10, y1 - bh - 10)):
                n = int(((P[:, 0] > bx - 8) & (P[:, 0] < bx + w + 8) & (P[:, 1] > by - 8)
                         & (P[:, 1] < by + bh + 8)).sum())
                if bx - 30 < mx < bx + w + 30 and by - 30 < my < by + bh + 30:
                    n += 1000                              # never on the design itself
                if best is None or n < best[0]:
                    best = (n, bx, by)
            self._lbox = (best[1], best[2], w)
        return self._lbox

    # ------------------------------------------------------------------------------------------ the frame
    def draw(self, cv: Canvas, t: float):
        s0, s1 = self.T_SPACE
        n = len(self.bounds)
        order_all = list(self.bounds)
        for el in order_all:                               # the search space outlines itself, element by element
            j = order_all.index(el)
            k = ramp(t, s0 + (s1 - s0) * 0.75 * j / max(1, n - 1), s0 + (s1 - s0) * (0.75 * j / max(1, n - 1) + 0.25))
            if el in self.alloy.design:
                u = (t - self.t_on[el]) / max(0.2, self.STEP * 1.15)
                if u <= 0:
                    self._tile_space(cv, el, k)
                else:
                    self._tile_design(cv, el, min(1.0, u))
            else:
                self._tile_space(cv, el, k)
        self._tile_balance(cv, ramp(t, s0, s0 + 0.6), ramp(t, self.T_LIGHT - 0.4, self.T_LIGHT + 0.2))
        # the fractions
        for i, el in enumerate(self.order):
            x, y, tw = self._bar_xy(i)
            u = (t - self.t_on[el]) / max(0.2, self.STEP * 1.15)
            if u <= 0:
                continue
            v = self.alloy.design[el]
            share = min(1.0, v / self.bounds[el][1])
            g = St.ease(min(1.0, max(0.0, (u - 0.1) / 0.75)))
            w = max(3.0, tw * share * g)
            cv.rect((x + 54, y - 10, x + 54 + w, y + 10), fill=self.col, radius=4)
            cv.text(x + 54 + tw + 12, y, _wt(v * g) if g < 1 else _wt(v), 22, bold=True, fill=INK, anchor="lm")
        kb = ramp(t, self.T_LIGHT - 0.4, self.T_LIGHT + 0.2)
        if kb > 0:
            xb = 79 + cv.text_w("Its fractions, wt%", 22, bold=True) + 14
            wb = cv.text_w("each track runs from 0 to that element's upper bound", 18, cond=True)
            cv.text(xb + wb + 26, 656, f"balance: {self.base} {_wt(self.alloy.comp[self.base])}", 18, bold=True,
                    cond=True, fill=INK, a=kb)
        self._map(cv, t)


class Composition(Segment):
    """Aluminium, then copper: two halves, each with its own header (the campaign's own network strip)."""
    key = "composition"
    title = "Composition: one design in its search space"
    campaign = "flaime_al"
    nodes = ("composition",)
    done = ()
    T_AL, T_CU = 16.0, 12.5
    DURATION = T_AL + T_CU
    DIP = 0.35                    # seconds each half fades at the change of alloy

    def __init__(self):
        super().__init__()
        self.al = _Half("flaime_al", self.T_AL, (0.5, 2.3), 2.5, 0.74, (9.0, 10.4))
        self.cu = _Half("onr_cu", self.T_CU, (0.5, 1.9), 2.1, 0.85, (5.2, 6.6))
        off = self.T_AL
        self.captions = list(self.al.captions) + [(a + off, b + off, s) for a, b, s in self.cu.captions]
        self.marks = {"composition.al": self.al.T_SPACE[0], "composition.al.light": self.al.T_LIGHT,
                      "composition.al.space": self.al.T_MAP[0], "composition.al.ring": self.al.T_RING,
                      "composition.cu": off + self.cu.T_SPACE[0], "composition.cu.light": off + self.cu.T_LIGHT,
                      "composition.cu.space": off + self.cu.T_MAP[0], "composition.cu.ring": off + self.cu.T_RING}
        self.sources = self.al.sources + [s for s in self.cu.sources if s not in self.al.sources]

    def frame(self, t: float) -> np.ndarray:
        t = max(0.0, min(float(t), self.DURATION))
        if t < self.T_AL:
            fr = self.al.frame(t)
            k = min(1.0, (self.T_AL - t) / self.DIP)
        else:
            fr = self.cu.frame(t - self.T_AL)
            k = min(1.0, (t - self.T_AL) / self.DIP)
        if k < 1.0:
            fr = St.dim(fr, max(0.0, k))
        return fr

    def draw(self, cv: Canvas, t: float):                  # the halves draw; frame() dispatches
        raise NotImplementedError

    def close(self):
        self.al.close()
        self.cu.close()


if __name__ == "__main__":
    import sys
    import time
    seg = Composition()
    for tt in [float(v) for v in sys.argv[1:]] or [1.5, 4.0, 8.5, 11.0, 16.0, 18.5, 21.5, 25.0, 29.5]:
        t0 = time.time()
        fr = seg.frame(tt)
        Image.fromarray(fr).save(f"/tmp/vid/exp_composition_{tt:05.1f}.png")
        print("wrote", f"/tmp/vid/exp_composition_{tt:05.1f}.png", f"{time.time() - t0:.2f} s")
    seg.close()
