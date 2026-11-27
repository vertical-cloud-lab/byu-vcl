"""The figures the video tracks, drawn with PIL frame by frame: the replay's live plot panel, the explainer that builds
those figures up step by step, the results and the takeaway card.

    PlotPanel(replay, bench).draw(t_h)   -> RGBA 600 x 420: best so far vs days and vs money, both campaigns, live
    explain_frame(t), EXPLAIN_DURATION   -> the explainer (t in seconds from its start), EXPLAIN_CAPTIONS
    results_frame(t), RESULTS_DURATION   -> the results, RESULTS_CAPTIONS
    takeaway_frame(t), TAKEAWAY_DURATION -> the takeaway card

Every number on screen comes from twin/video/data.py (the replayed run, bench(), headline(), econ(), target()); a value
that is missing is shown as "pending". Encoding (style.py): a campaign's colour, solid, is the automated lab; grey
dashed is the conventional baseline; white dotted is the state-of-the-art target. Text stays in the text inks. The
bottom-left box (24, 860, 820, 200) of the full-screen frames is left empty for the docked DAG overlay.
"""
from __future__ import annotations

import math
import os

import numpy as np
from PIL import Image, ImageDraw

from . import data as D
from . import style as St
from .style import px

HPD = 24.0
EXPLAIN_DURATION = 62.0
RESULTS_DURATION = 90.0
# the narrated cut (compose.NARRATE): the takeaway's three lines take 50 s, and the captions say what the voice says
NARRATED = os.environ.get("TWIN_VIDEO_NARRATION", "0") == "1"
TAKEAWAY_DURATION = 73.0 if NARRATED else 15.0       # narrated: four lines, the card built up as they're said


# ------------------------------------------------------------------ the narrated cut's numbers (DAL audit, PR 293 §4)
_AUD: dict = {}


def audit_numbers() -> dict:
    """What the narrated cut adds on screen, after DAL's audit of the video (digital-alloy-lab PR 293): aluminium's
    factor with both labs ordering metal as they go (bench2_summary.json's stock runs against the conventional lab,
    twin.accel as econ_summary.json computes the headline), copper over all 24 automated seeds, and the share of random
    designs that beat the target (oracle.json)."""
    if _AUD:
        return _AUD
    import json
    try:
        from twin import accel as AC
        E = json.loads((D.OUT2 / "bench2_summary.json").read_text())["experiments"]
        T = D.target()

        def cur(exp, key, c):
            g = E[exp][key]
            hz = float(g["cfg"].get("days") or g["cfg"].get("horizon_days") or 365)
            return [dict(curve=x, horizon_days=hz) for x in g["campaigns"][c]["curves"]]
        a = AC.acceleration_factor(cur("conventional", "proposed_bofn_stock-lean", "flaime_al"),
                                   cur("stock", "vertical_lab_bofn_stock-lean", "flaime_al"), T["flaime_al"], "days",
                                   n_boot=2000, seed=0)
        _AUD["lean_af"] = dict(af=a["af"], lo=a["lo"], hi=a["hi"], days_new=a["median_new"], days_ref=a["median_ref"])

        def fin(key):
            v = []
            for exp in ("main", "cu_seeds"):
                v += [x[-1][2] if x else 0.0 for x in E[exp][key]["campaigns"]["onr_cu"]["curves"]]
            return float(np.mean(v)), len(v)
        _AUD["cu24"] = dict(tiered=fin("vertical_lab_tiered"), blend=fin("vertical_lab_bofn_blend"),
                            bofn=E["main"]["vertical_lab_bofn"]["campaigns"]["onr_cu"]["best_mean"],
                            random=E["main"]["vertical_lab_random"]["campaigns"]["onr_cu"]["best_mean"])
        O = json.loads((D.OUT2 / "oracle.json").read_text())
        _AUD["frac_random"] = min(O[c]["random_default_process"]["frac_above_sota"] for c in D.CAMPAIGNS)
    except Exception as e:                              # noqa: BLE001
        print("audit_numbers:", e)
    return _AUD


DAG_BOX = (24, 860, 820, 200)            # x, y, w, h at 1920 x 1080: the docked DAG overlay's corner, kept empty

STATION_SHORT = {
    "hpc": "HPC (CALPHAD)", "atomizer": "atomizer", "doser": "doser + press", "sieve": "sieving", "psd": "PSD + XRF",
    "byu_sem": "SEM + EDS", "byu_icpms": "ICP-MS", "density": "density", "edm": "wire EDM", "furnace": "furnace",
    "tensile": "tensile", "tensile_hot": "hot tensile", "utah_midi": "LPBF (MIDI)", "utah_mxlab": "DED (MX-Lab)",
    "mines_x2": "DED (Mines X2)", "nsl": "NSL Analytical", "cubxl": "corrosion (CubXL)", "immersion": "immersion",
    "xrd": "XRD", "xrf": "XRF", "prep": "metallography", "hardness": "Vickers", "nanoindent": "nanoindenter",
    "pip": "PIP", "shop": "shop", "valimet": "Valimet", "ames": "Ames"}


# ===================================================================================================== the data
class Ctx:
    """What every figure reads, loaded once: the replay, the benchmark groups, the headline and the economics."""

    def __init__(self, replay=None, bench_dict=None):
        self.R = replay if replay is not None else D.Replay()
        self.B = bench_dict if bench_dict is not None else D.bench([self.R])
        self.T = dict(self.B.get("target") or D.target())
        self.E = D.econ()
        self.Hd = D.headline(self.R)
        facs = {f for f, _ in self.B["groups"]}
        self.auto, self.conv = D.facility_keys(facs | {self.R.facility})
        self.pol = self.R.policy
        self.horizon = float(self.R.horizon_days)
        self.placeholder = bool(self.B.get("placeholder") or self.R.placeholder or self.E.get("placeholder"))
        longest = max([float(c[-1, 0]) for g in self.B["groups"].values() for cs in g.values() for c in cs
                       if len(c)] + [self.horizon])
        self.day_max = max(self.horizon, min(longest, 4 * self.horizon))
        self.day_grid = np.linspace(0.0, self.day_max, int(self.day_max * 2) + 1)
        # the explainer and the ratios draw the comparison econ_summary.json quotes (automated lab running A against
        # the conventional lab running B); the replay's corner draws the conventional lab running the replayed policy
        self.cmp_a, self.cmp_b = D.comparison_pair(self.E.get("comparison")) if self.E.get("comparison") else \
            (None, None)
        if self.cmp_a is None:
            self.cmp_a = self.cmp_b = self.pol
        self.base, self.auto_mean, self.base_replay = {}, {}, {}
        for camp in D.CAMPAIGNS:
            self.base[camp] = self._curves(self.group(self.conv, camp, self.cmp_b))
            self.auto_mean[camp] = self._curves(self.group(self.auto, camp, self.cmp_a))
            self.base_replay[camp] = self._curves(self.group(self.conv, camp, self.pol))
            if D.R3B:
                # round 3b: the replayed runs are the stocked automated lab's, so the live plots' reference is like
                # for like: the same policy in the conventional lab, stocked too (out/twin3b/runs/c_stocked.jsonl)
                cv = [np.array(r["campaigns"][camp]["curve_new"], float).reshape(-1, 3)
                      for r in sorted(D.rows3b("c_stocked"), key=lambda r: r["cfg"]["seed"])
                      if r["cfg"]["policy"] == self.pol and r["cfg"]["facility"] == self.conv]
                self.base_replay[camp] = self._curves(cv) if cv else None
        try:
            from twin import spaces as SP
            self.refs = {c: list(SP.REFERENCE.get(c, {}).keys()) for c in D.CAMPAIGNS}
        except Exception:                               # noqa: BLE001
            self.refs = {c: [] for c in D.CAMPAIGNS}
        self.util_auto = utilization(self.R)
        self.R_conv = None
        for p in sorted(D.EVENTS_DIR.glob("*.json")) + sorted(D.VID.glob("placeholder_*.json")):
            try:
                import json
                m = json.loads(p.read_text()).get("meta", {})
            except Exception:                           # noqa: BLE001
                continue
            if str(m.get("facility")) == self.conv:
                try:
                    self.R_conv = D.Replay(p)
                    break
                except Exception:                       # noqa: BLE001
                    pass
        self.util_conv = utilization(self.R_conv) if self.R_conv is not None else None

    def group(self, fac, camp, pol=None) -> list:
        """The per-seed curves of a facility for a policy: that policy, else its base (bofn for bofn_blend), else the
        comparison's conventional policy, else cost_aware, else any."""
        G = self.B["groups"]
        pol = pol or self.pol
        base = str(pol).split("_blend")[0]
        for p in (pol, base, getattr(self, "cmp_b", None), "cost_aware"):
            if p and (fac, p) in G:
                return G[(fac, p)].get(camp, [])
        for (f, p), g in G.items():
            if f == fac:
                return g.get(camp, [])
        return []

    def _curves(self, curves: list) -> dict | None:
        """Mean and SE on the day grid, the mean spend at each day, and the mean and SE against money."""
        if not curves:
            return None
        g = self.day_grid
        m, se = D.mean_curve(curves, g, 0)
        spend = []
        for c in curves:
            d = np.concatenate([[0.0], c[:, 0]]) if len(c) else np.array([0.0, 1.0])
            s = np.concatenate([[0.0], c[:, 1]]) if len(c) else np.array([0.0, 0.0])
            spend.append(np.interp(g, d, s))
        spend = np.mean(spend, 0)
        top = max([float(c[:, 1].max()) for c in curves if len(c)] + [1000.0])
        mg = np.linspace(0.0, top * 1.02, 600)
        mm, mse = D.mean_curve(curves, mg, 1)
        return dict(n=len(curves), mean=m, se=se, spend=spend, money_grid=mg, money_mean=mm, money_se=mse)


_CTX: Ctx | None = None


def context(replay=None, bench_dict=None, refresh: bool = False) -> Ctx:
    """The shared context; compose passes its own Replay and bench so the video reads them once."""
    global _CTX
    if _CTX is None or refresh or (replay is not None and _CTX.R is not replay):
        _CTX = Ctx(replay, bench_dict)
    return _CTX


def utilization(R) -> dict:
    """{station: share of the horizon it was busy}, event hours clipped to the horizon over units x horizon."""
    if R is None:
        return {}
    out = {}
    hz = R.horizon_h
    t0 = np.clip(R.t0, 0, hz)
    t1 = np.clip(R.t1, 0, hz)
    for st in set(R.station.tolist()):
        if not st:
            continue
        m = R.station == st
        units = max(1, int((R.stations.get(st) or {}).get(D.KEYS["st_units"], 1) or 1))
        out[st] = float((t1[m] - t0[m]).sum() / (units * hz))
    return out


def util_by_campaign(R) -> dict:
    """{station: {campaign: share}} for the stacked bars."""
    out = {}
    if R is None:
        return out
    hz = R.horizon_h
    t0 = np.clip(R.t0, 0, hz)
    t1 = np.clip(R.t1, 0, hz)
    for st in set(R.station.tolist()):
        if not st:
            continue
        units = max(1, int((R.stations.get(st) or {}).get(D.KEYS["st_units"], 1) or 1))
        out[st] = {}
        for c in D.CAMPAIGNS:
            m = (R.station == st) & (R.camp == c)
            out[st][c] = float((t1[m] - t0[m]).sum() / (units * hz))
    return out


# ================================================================================================= small helpers
def fmt_days(v) -> str:
    return "pending" if v is None else f"{v:.0f} d"


def fmt_x(v) -> str:
    return "pending" if v is None else f"{v:.1f}x"


def fmt_pct(v) -> str:
    return "pending" if v is None else f"{100 * v:.0f} %"


def fmt_money(v) -> str:
    return "pending" if v is None else St.money(v)


def ticks(lo: float, hi: float, n: int, kind: str) -> list:
    """Round tick values: 1-2-5 steps for utility and shares (no 0.25), style.nice_ticks otherwise."""
    if kind not in ("u", "pct"):
        return St.nice_ticks(lo, hi, n)
    span = max(hi - lo, 1e-9)
    mag = 10 ** math.floor(math.log10(span / max(1, n)))
    for m in (1, 2, 5, 10):
        step = m * mag
        if span / step <= n:
            break
    a = math.ceil(lo / step - 1e-9) * step
    return [round(a + i * step, 10) for i in range(int((hi - a) / step + 1e-9) + 1)]


def _tick_label(v: float, kind: str, step: float) -> str:
    if kind == "usd":
        if v == 0:
            return "$0"
        if v >= 1e6:
            return f"${v / 1e6:g}M"
        return f"${v / 1e3:g}k" if v >= 1e3 else f"${v:g}"
    if kind == "u":
        return f"{v:.1f}" if step >= 0.1 - 1e-9 else f"{v:.2f}"
    if kind == "pct":
        return f"{100 * v:.0f} %" if step >= 0.01 - 1e-12 else f"{100 * v:.1f} %"
    return f"{v:g}"


def _simplify(pts: list) -> list:
    """Drop points in the middle of horizontal runs (a step curve on a grid)."""
    if len(pts) <= 2:
        return pts
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        if abs(pts[i][1] - out[-1][1]) < 1e-9 and abs(pts[i + 1][1] - pts[i][1]) < 1e-9:
            continue
        out.append(pts[i])
    out.append(pts[-1])
    return out


def step_points(xs, ys, x_end: float, x0: float = 0.0, y0: float = 0.0) -> list:
    """A best-so-far step curve: flat at y0 from x0, up at each improvement, flat to x_end."""
    pts = [(x0, y0)]
    cur = y0
    for x, y in zip(xs, ys):
        if y > cur + 1e-12:
            pts += [(x, cur), (x, y)]
            cur = y
    if x_end > pts[-1][0]:
        pts.append((x_end, cur))
    return pts


class Ax:
    """A plot area in pixels with linear data ranges, and the marks drawn into it."""

    def __init__(self, box, xr, yr, xkind="days", ykind="u"):
        self.x0, self.y0, self.x1, self.y1 = box
        self.xr, self.yr = xr, yr
        self.xkind, self.ykind = xkind, ykind

    def X(self, v):
        a, b = self.xr
        return self.x0 + (v - a) / max(1e-12, b - a) * (self.x1 - self.x0)

    def Y(self, v):
        a, b = self.yr
        return self.y1 - (v - a) / max(1e-12, b - a) * (self.y1 - self.y0)

    def P(self, pts):
        return [(self.X(x), self.Y(y)) for x, y in pts]

    def frame(self, d, fs=13, nx=4, ny=4, xlabel=None, ylabel=None, fs_label=None, xticks=True, pad_r=None):
        f = St.font(fs)
        xt = ticks(self.xr[0], self.xr[1], nx, self.xkind)
        yt = ticks(self.yr[0], self.yr[1], ny, self.ykind)
        pad_r = px(10) if pad_r is None else pad_r
        xs = xt[1] - xt[0] if len(xt) > 1 else 1.0
        ys = yt[1] - yt[0] if len(yt) > 1 else 1.0
        for v in yt:
            y = self.Y(v)
            d.line([(self.x0, y), (self.x1, y)], fill=St.GRID, width=1)
            d.text((self.x0 - px(6), y), _tick_label(v, self.ykind, ys), font=f, fill=St.INK2, anchor="rm")
        d.line([(self.x0, self.y1), (self.x1, self.y1)], fill=St.RULE, width=max(1, px(1)))
        if xticks:
            for v in xt:
                x = self.X(v)
                if x > self.x1 + 1:
                    continue
                d.line([(x, self.y1), (x, self.y1 + px(4))], fill=St.RULE, width=1)
                lab = _tick_label(v, self.xkind, xs)
                w2 = St.text_w(f, lab) / 2
                xl = min(x, self.x1 + pad_r - w2)              # the last label kept inside the panel
                d.text((xl, self.y1 + px(6)), lab, font=f, fill=St.INK2, anchor="ma")
        fl = St.font(fs_label or fs)
        if xlabel:
            d.text(((self.x0 + self.x1) / 2, self.y1 + px(8) + fs * St.S + px(6)), xlabel, font=fl, fill=St.INK2,
                   anchor="ma")
        if ylabel:
            d.text((self.x0, self.y0 - px(10)), ylabel, font=fl, fill=St.INK2, anchor="ld")

    def line(self, d, pts, fill, width, dashed=False, dash=10, gap=7):
        if len(pts) < 2:
            return
        P = self.P(_simplify(pts))
        if dashed:
            St.dashed_line(d, P, fill, width=width, dash=px(dash), gap=px(gap))
        else:
            d.line(P, fill=fill, width=width, joint="curve")

    def dotted_h(self, d, y_val, fill, x_from=None, x_to=None, r=None, gap=None):
        y = self.Y(y_val)
        r = px(2.0) if r is None else r
        gap = px(8) if gap is None else gap
        xa = self.x0 if x_from is None else self.X(x_from)
        xb = self.x1 if x_to is None else self.X(x_to)
        x = xa
        while x <= xb:
            d.ellipse((x - r, y - r, x + r, y + r), fill=fill)
            x += gap

    def dot(self, d, x, y, fill, r=5):
        cx, cy = self.X(x), self.Y(y)
        rr = px(r)
        ring = px(2)
        d.ellipse((cx - rr - ring, cy - rr - ring, cx + rr + ring, cy + rr + ring), fill=St.SURF)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=fill)

    def band(self, layer_d, xs, lo, hi, fill, alpha=0.22):
        if len(xs) < 2:
            return
        top = [(self.X(x), self.Y(v)) for x, v in zip(xs, hi)]
        bot = [(self.X(x), self.Y(v)) for x, v in zip(xs[::-1], lo[::-1])]
        layer_d.polygon(top + bot, fill=tuple(fill[:3]) + (int(255 * alpha),))


def label_box(d, xy, text, f, fill, anchor="ma", bg=None, pad=None):
    """Text on a box of the background colour, so curves under it do not cross the letters."""
    pad = px(6) if pad is None else pad
    x0, y0, x1, y1 = d.textbbox(xy, text, font=f, anchor=anchor)
    d.rounded_rectangle((x0 - pad, y0 - pad, x1 + pad, y1 + pad), radius=px(6), fill=St.BG if bg is None else bg)
    d.text(xy, text, font=f, fill=fill, anchor=anchor)


def _over(img: Image.Image, lay: Image.Image, k: float = 1.0):
    """Composite an RGBA layer onto an RGB or RGBA image, at opacity k."""
    if k < 0.997:
        lay = _fade(lay, k)
    if img.mode == "RGBA":
        img.alpha_composite(lay)
    else:
        img.paste(lay, (0, 0), lay)


def legend_line(d, x, y, kind, color, text, fs=14, w=34):
    """One legend entry: a line sample (solid, dashed or dotted) and its text in INK2; returns the x after it."""
    yy = y
    if kind == "solid":
        d.line([(x, yy), (x + px(w), yy)], fill=color, width=px(3))
    elif kind == "dashed":
        St.dashed_line(d, [(x, yy), (x + px(w), yy)], color, width=px(3), dash=px(8), gap=px(5))
    elif kind == "dotted":
        xx = x
        while xx <= x + px(w):
            d.ellipse((xx - px(1.6), yy - px(1.6), xx + px(1.6), yy + px(1.6)), fill=color)
            xx += px(7)
    elif kind == "solid2":                         # both campaign colours: the automated lab
        d.line([(x, yy - px(3)), (x + px(w), yy - px(3))], fill=St.CAMP["flaime_al"], width=px(3))
        d.line([(x, yy + px(3)), (x + px(w), yy + px(3))], fill=St.CAMP["onr_cu"], width=px(3))
    f = St.font(fs)
    d.text((x + px(w + 8), yy), text, font=f, fill=St.INK2, anchor="lm")
    return x + px(w + 8) + St.text_w(f, text) + px(22)


def swatch(d, x, y, color, s=12):
    d.rounded_rectangle((x, y, x + px(s), y + px(s)), radius=px(3), fill=color)


def ymax_for(camp: str, ctx: Ctx, best: float) -> float:
    if D.ROUND == 3:                                    # both targets stay on the plot
        return max(1.12 * D.targets2()[camp], 1.1 * best, 0.1)
    return max(1.2 * ctx.T[camp], 1.1 * best, 0.1)


def xmax_days(t_days: float, horizon: float, lo: float = 7.0) -> float:
    return min(max(lo, 1.15 * t_days), horizon * 1.03)


# ================================================================================================ the live panel
class PlotPanel:
    """Best so far against days and against money, FLAIME and ONR, for the replay's corner: the run itself (the
    campaign's colour), the conventional baseline's mean up to the same day (grey dashed) and the target (dotted)."""

    SIZE = (600, 420)

    def __init__(self, replay=None, bench_dict=None):
        self.ctx = context(replay, bench_dict)
        self.R = self.ctx.R
        self.w, self.h = px(self.SIZE[0]), px(self.SIZE[1])
        self.bg = St.rounded((self.w, self.h), px(14), St.SURF, alpha=0.88)

    def draw(self, t_h: float) -> Image.Image:
        ctx, R = self.ctx, self.R
        im = self.bg.copy()
        d = ImageDraw.Draw(im)
        t_h = float(min(max(t_h, 0.0), R.horizon_h))
        td = t_h / HPD
        f13, f14 = St.font(13), St.font(14)
        fb = St.font(15, bold=True)
        # column titles
        cols = [(px(58), px(282)), (px(352), px(584))]
        r3 = D.ROUND == 3
        T2 = D.targets2() if r3 else {}
        d.text((cols[0][0], px(10)), "best new alloy so far vs days" if r3 else "best so far vs days", font=f14,
               fill=St.INK2)
        d.text((cols[1][0], px(10)), "vs the campaign's spending" if r3 else "vs money spent", font=f14,
               fill=St.INK2)
        rows = [(px(34), px(196)), (px(214), px(376))]
        labelled_target = False
        for ri, camp in enumerate(D.CAMPAIGNS):
            ry0, ry1 = rows[ri]
            col = St.CAMP[camp]
            best = R.best_at(camp, t_h)
            tgt = ctx.T[camp]
            # row label: swatch, name, the run's best so far and the target
            swatch(d, px(12), ry0 + px(3), col)
            d.text((px(30), ry0), St.CAMP_NAME[camp], font=fb, fill=St.INK)
            xname = px(30) + St.text_w(fb, St.CAMP_NAME[camp]) + px(8)
            d.text((xname, ry0 + px(2)), St.CAMP_SHORT[camp], font=f13, fill=St.INK2)
            d.text((self.w - px(14), ry0 + px(1)), f"best {best:.2f} · targets {tgt:.2f}, {T2[camp]:.2f}" if r3
                   else f"best {best:.2f} · target {tgt:.2f}", font=f13, fill=St.INK2, anchor="ra")
            ymax = ymax_for(camp, ctx, best)
            py0, py1 = ry0 + px(30), ry1 - px(22)
            base = ctx.base_replay.get(camp)
            # ---- days
            xm = xmax_days(td, ctx.horizon)
            ax = Ax((cols[0][0], py0, cols[0][1], py1), (0.0, xm), (0.0, ymax), "days", "u")
            ax.frame(d, fs=13, nx=4, ny=4)
            ax.dotted_h(d, tgt, St.TARGET)
            if r3:
                ax.dotted_h(d, T2[camp], St.TARGET)
            if base is not None:
                k = int(np.searchsorted(ctx.day_grid, td, side="right"))
                if k >= 2:
                    pts = list(zip(ctx.day_grid[:k], base["mean"][:k]))
                    ax.line(d, pts, St.BASE, px(3), dashed=True)
            cur = R.curve_upto(camp, t_h, "days")
            pts = step_points(cur[:, 0], cur[:, 1], td) if len(cur) else [(0.0, 0.0), (td, 0.0)]
            ax.line(d, pts, col, px(3))
            ax.dot(d, td, best, col, r=5)
            if not labelled_target:                     # once, over the curves
                label_box(d, (ax.x0 + px(6), ax.Y(tgt) - px(5)), "best existing alloy" if r3 else "state of the art",
                          f13, St.INK2, anchor="ld", bg=St.SURF + (235,), pad=px(2))
                if r3:
                    label_box(d, (ax.x0 + px(6), ax.Y(T2[camp]) - px(5)), "halfway target", f13, St.INK2,
                              anchor="ld", bg=St.SURF + (235,), pad=px(2))
                labelled_target = True
            # ---- money
            spent = R.spent_at(camp, t_h)
            b_spent = float(np.interp(td, ctx.day_grid, base["spend"])) if base is not None else 0.0
            xm2 = max(1000.0, 1.15 * max(spent, b_spent))
            ax2 = Ax((cols[1][0], py0, cols[1][1], py1), (0.0, xm2), (0.0, ymax), "usd", "u")
            ax2.frame(d, fs=13, nx=3, ny=4, pad_r=px(12))
            ax2.dotted_h(d, tgt, St.TARGET)
            if r3:
                ax2.dotted_h(d, T2[camp], St.TARGET)
            if base is not None and b_spent > 0:
                mg = base["money_grid"]
                k = int(np.searchsorted(mg, b_spent, side="right"))
                if k >= 2:
                    ax2.line(d, list(zip(mg[:k], base["money_mean"][:k])), St.BASE, px(3), dashed=True)
            cm = R.curve_upto(camp, t_h, "money")
            pts = step_points(cm[:, 0], cm[:, 1], spent) if len(cm) else [(0.0, 0.0), (spent, 0.0)]
            ax2.line(d, pts, col, px(3))
            ax2.dot(d, spent, best, col, r=5)
        # legend
        y = self.h - px(20)
        x = px(14)
        nb = (ctx.base_replay.get("flaime_al") or {}).get("n")
        if D.ROUND != 3:
            x = legend_line(d, x, y, "solid2", None, "automated lab (this run)", fs=13, w=26)
        if r3:                                          # BOFN was not run in the conventional lab: rule of thumb
            x = legend_line(d, px(14), y, "solid2", None, "this run", fs=13, w=26)
            x = legend_line(d, x, y, "dashed", St.BASE, f"conventional, stocked, same policy (mean of {nb})" if D.R3B
                            else f"conventional, rule of thumb (mean of {nb})", fs=13, w=26)
            legend_line(d, x, y, "dotted", St.TARGET, "targets", fs=13, w=20)
            return im
        x = legend_line(d, x, y, "dashed", St.BASE, "conventional" + (f" (mean of {nb})" if nb else ""), fs=13, w=26)
        legend_line(d, x, y, "dotted", St.TARGET, "target", fs=13, w=20)
        return im


# ================================================================================================= the explainer
EXPLAIN_CAPTIONS = [
    (0.0, 11.0, "Best so far: the highest utility of any alloy tested yet, here FLAIME's automated lab over the year."),
    (11.0, 19.0, "The target: the state of the art, the best of the reference alloys." if not NARRATED else
     "The target: the best reference alloy's score on the twin's synthetic alloy model. One random design in "
     f"{round(1 / max(1e-6, audit_numbers().get('frac_random', 1 / 12)))} beats it."),
    (19.0, 28.0, "The same curve against the money spent: powder, builds, tests and machine time."),
    (28.0, 36.0, "Grey, dashed: the conventional lab, the same policy with partner and core facilities" +
     (", ordering metal as it goes (the automated lab starts stocked)." if NARRATED else ".")),
    (36.0, 50.0, "Read off where each first reaches the target: X = days conventional / days automated, "
                 "Y = cost automated / cost conventional."),
    (50.0, EXPLAIN_DURATION, "Instrument utilization: the share of the year each station was busy, both campaigns."),
]
EX_CAMP = "flaime_al"
EX_L = (190, 250, 890, 730)              # plot areas: days (left) and money (right)
EX_R = (1100, 250, 1800, 730)


def _caption_at(caps, t):
    for a, b, s in caps:
        if a <= t < b:
            return s, a, b
    return caps[-1][2], caps[-1][0], caps[-1][1]


def _header(d, title, caps, t, sub_y=112, total=None):
    d.text((px(80), px(44)), title, font=St.font(44, bold=True), fill=St.INK)
    s, a, b = _caption_at(caps, t)
    total = caps[-1][1] if total is None else total
    k = min(St.ramp(t, a, a + 0.6) if a > 0 else 1.0, 1.0 - St.ramp(t, b - 0.4, b) if b < total else 1.0)
    col = St.mix(St.BG, St.INK, k)
    size = 28
    while size > 22 and len(St.wrap(s, St.font(size), px(1760))) > 2:     # a long caption: smaller, never cut
        size -= 1
    f = St.font(size)
    for i, ln in enumerate(St.wrap(s, f, px(1760))[:2]):
        d.text((px(80), px(sub_y) + i * px(size * 38 / 28)), ln, font=f, fill=col)


def _box(b):
    return tuple(px(v) for v in b)


def _mean_line(ax, d, xs, ys, upto, color, width, dashed=False):
    k = int(np.searchsorted(xs, upto, side="right"))
    if k >= 2:
        pts = list(zip(xs[:k], ys[:k]))
        if upto > xs[k - 1]:
            pts.append((upto, ys[k - 1]))
        ax.line(d, pts, color, width, dashed=dashed)


def arrow_h(d, x0, x1, y, color, width=3, head=12):
    """A horizontal double-headed arrow from x0 to x1 at y."""
    if abs(x1 - x0) < 2 * head:
        d.line([(x0, y), (x1, y)], fill=color, width=width)
        return
    a, b = (x0, x1) if x0 < x1 else (x1, x0)
    d.line([(a + head, y), (b - head, y)], fill=color, width=width)
    d.polygon([(a, y), (a + head, y - head * 0.55), (a + head, y + head * 0.55)], fill=color)
    d.polygon([(b, y), (b - head, y - head * 0.55), (b - head, y + head * 0.55)], fill=color)


def explain_frame(t: float, captions: bool = True) -> np.ndarray:
    ctx = context()
    camp = EX_CAMP
    col = St.CAMP[camp]
    tgt = ctx.T[camp]
    am, bm = ctx.auto_mean.get(camp), ctx.base.get(camp)
    hd = ctx.Hd.get(camp, {})
    im = Image.new("RGB", (St.W, St.H), St.BG)
    d = ImageDraw.Draw(im)
    if captions:
        _header(d, "The figures we track", EXPLAIN_CAPTIONS, t)
    else:
        d.text((px(80), px(44)), "The figures we track", font=St.font(44, bold=True), fill=St.INK)
    charts = 1.0 - St.ramp(t, 48.9, 49.7)
    if charts >= 0.997:
        _explain_charts(d, t, ctx, camp, col, tgt, am, bm, hd)
    elif charts > 0.01:
        layer = Image.new("RGBA", (St.W, St.H), (0, 0, 0, 0))
        _explain_charts(ImageDraw.Draw(layer), t, ctx, camp, col, tgt, am, bm, hd)
        _over(im, layer, charts)
    ku = St.ramp(t, 49.8, 50.6)
    if ku >= 0.997:
        _explain_util(d, t, ctx)
    elif ku > 0.003:
        layer = Image.new("RGBA", (St.W, St.H), (0, 0, 0, 0))
        _explain_util(ImageDraw.Draw(layer), max(t, 50.6), ctx)
        _over(im, layer, ku)
    return np.asarray(im)


def _explain_charts(d, t, ctx, camp, col, tgt, am, bm, hd):
    H = ctx.horizon
    best_all = max([float(np.max(x["mean"])) for x in (am, bm) if x is not None] + [tgt])
    ymax = max(1.2 * tgt, 1.1 * best_all)
    n_a = am["n"] if am else 0
    n_b = bm["n"] if bm else 0
    # (a) days: the x-axis grows as the curve is drawn
    sweep = H * St.ease((t - 1.5) / 8.0) if t < 9.5 else H
    xm = xmax_days(sweep, H, lo=14.0)
    dc0 = hd.get("days_conv")
    H_ax = H if not dc0 or dc0 <= H else min(ctx.day_max, 1.08 * dc0)
    if H_ax > H:                                  # grows with the baseline, 28.5-34 s
        xm = xm + (H_ax * 1.03 - xm) * St.ramp(t, 28.5, 34.0)
    ax = Ax(_box(EX_L), (0.0, xm), (0.0, ymax), "days", "u")
    ax.frame(d, fs=18, nx=5, ny=4, xlabel="days since the start", ylabel="utility, best so far", fs_label=20)
    # (b) target
    kt = St.ramp(t, 11.0, 12.0)
    if kt > 0:
        ax.dotted_h(d, tgt, St.mix(St.BG, St.TARGET, kt), r=px(2.2), gap=px(10))
    # (d) the baseline, drawn in over 28.5-34 s
    kb = St.ramp(t, 28.5, 34.0)
    if bm is not None and kb > 0:
        _mean_line(ax, d, ctx.day_grid, bm["mean"], H_ax * kb, St.BASE, px(3), dashed=True)
    if am is not None:
        _mean_line(ax, d, ctx.day_grid, am["mean"], sweep, col, px(3))
        if t < 9.5:
            ax.dot(d, sweep, float(np.interp(sweep, ctx.day_grid, am["mean"])), col, r=6)
    if kt > 0:                                   # the target's labels, over the curves
        sota = D.target_refs().get(camp)
        names = (f"{sota}, the best of " if sota else "the best of ") + (", ".join(ctx.refs.get(camp, [])) or
                                                                         "the reference alloys")
        label_box(d, (ax.x0 + px(10), ax.Y(tgt) - px(12)), f"state of the art: {tgt:.2f}",
                  St.font(18, bold=True), St.mix(St.BG, St.INK, kt), anchor="ld", pad=px(4))
        label_box(d, (ax.x0 + px(10), ax.Y(tgt) + px(14)), names, St.font(17),
                  St.mix(St.BG, St.INK2, kt), anchor="la", pad=px(4))
    # (c) money, from 19 s
    km = St.ramp(t, 19.0, 19.8)
    if km > 0:
        top = max([float(x["money_grid"][-1]) for x in (am, bm) if x is not None] + [1000.0])
        m_sweep_d = H * St.ease((t - 19.5) / 7.0) if t < 26.5 else H
        # the money axis grows with the automated lab's spending at the swept day
        spent = float(np.interp(m_sweep_d, ctx.day_grid, am["spend"])) if am is not None else 0.0
        b_spent = float(np.interp(H_ax * kb, ctx.day_grid, bm["spend"])) if (bm is not None and kb > 0) else 0.0
        xm2 = max(2000.0, 1.15 * max(spent, b_spent)) if t < 26.5 or kb > 0 else max(2000.0, 1.15 * spent)
        xm2 = min(xm2, top * 1.05)
        ax2 = Ax(_box(EX_R), (0.0, xm2), (0.0, ymax), "usd", "u")
        lay = Image.new("RGBA", (St.W, St.H), (0, 0, 0, 0)) if km < 0.999 else None
        dd = ImageDraw.Draw(lay) if lay is not None else d
        ax2.frame(dd, fs=18, nx=4, ny=4, xlabel="money spent", ylabel="utility, best so far", fs_label=20)
        if kt > 0:
            ax2.dotted_h(dd, tgt, St.mix(St.BG, St.TARGET, kt), r=px(2.2), gap=px(10))
        if bm is not None and kb > 0:
            _mean_line(ax2, dd, bm["money_grid"], bm["money_mean"], b_spent, St.BASE, px(3), dashed=True)
        if am is not None:
            _mean_line(ax2, dd, am["money_grid"], am["money_mean"], spent, col, px(3))
        if lay is not None:
            _over(d._image, lay, km)
    # legend, bottom right (clear of the DAG box)
    lx, ly = px(900), px(905)
    x = legend_line(d, lx, ly, "solid", col, f"automated lab (mean of {n_a} runs)" if n_a != 1 else
                    "automated lab (one run)", fs=20, w=44)
    if kb > 0 and bm is not None:
        legend_line(d, x, ly, "dashed", St.BASE, f"conventional (mean of {n_b} runs)" if n_b != 1 else
                    "conventional (one run)", fs=20, w=44)
    if kt > 0:
        legend_line(d, lx, ly + px(40), "dotted", St.TARGET, "state of the art (target)", fs=20, w=44)
    # (e) the read-off
    ke = St.ramp(t, 36.0, 37.0)
    if ke > 0:
        da, dc = hd.get("days_auto"), hd.get("days_conv")
        y = ax.Y(tgt)
        ink = St.mix(St.BG, St.INK, ke)
        for v, c in ((da, col), (dc, St.BASE)):
            if v is not None and v <= ax.xr[1]:
                x = ax.X(v)
                d.line([(x, y), (x, ax.y1)], fill=St.mix(St.BG, c, ke), width=px(2))
                d.ellipse((x - px(7), y - px(7), x + px(7), y + px(7)), fill=St.mix(St.BG, c, ke),
                          outline=St.mix(St.BG, St.INK, ke), width=px(2))
        ya = y + px(46)
        if da is not None and dc is not None:
            arrow_h(d, ax.X(da), ax.X(dc), ya, ink, width=px(3), head=px(14))
            txt = f"X = {dc:.0f} d / {da:.0f} d = {fmt_x(hd.get('accel') if hd.get('accel') else dc / da)}"
        else:
            txt = "X: pending (a lab did not reach the target in these runs)"
        label_box(d, ((ax.x0 + ax.x1) / 2, ya + px(18)), txt, St.font(24, bold=True), ink, anchor="ma")
        label_box(d, ((ax.x0 + ax.x1) / 2, ya + px(56)), "first day at the target, median over runs",
                  St.font(18), St.mix(St.BG, St.INK2, ke), anchor="ma", pad=px(4))
    kc = St.ramp(t, 43.0, 44.0)
    if kc > 0 and km > 0:
        sa, sc = hd.get("usd_auto"), hd.get("usd_conv")
        y = ax2.Y(tgt)
        ink = St.mix(St.BG, St.INK, kc)
        for v, c in ((sa, col), (sc, St.BASE)):
            if v is not None and v <= ax2.xr[1]:
                x = ax2.X(v)
                d.line([(x, y), (x, ax2.y1)], fill=St.mix(St.BG, c, kc), width=px(2))
                d.ellipse((x - px(7), y - px(7), x + px(7), y + px(7)), fill=St.mix(St.BG, c, kc),
                          outline=St.mix(St.BG, St.INK, kc), width=px(2))
        ya = y + px(46)
        if sa is not None and sc is not None:
            arrow_h(d, ax2.X(sa), ax2.X(sc), ya, ink, width=px(3), head=px(14))
            txt = f"Y = {St.money(sa)} / {St.money(sc)} = {sa / sc:.2f}"
        else:
            txt = "Y: pending (a lab did not reach the target in these runs)"
        label_box(d, ((ax2.x0 + ax2.x1) / 2, ya + px(18)), txt, St.font(24, bold=True), ink, anchor="ma")
        label_box(d, ((ax2.x0 + ax2.x1) / 2, ya + px(56)), "the campaigns' own spending by then, median over runs",
                  St.font(18), St.mix(St.BG, St.INK2, kc), anchor="ma", pad=px(4))


def _fade(lay: Image.Image, k: float) -> Image.Image:
    a = np.asarray(lay).copy()
    a[:, :, 3] = (a[:, :, 3].astype(np.uint16) * int(255 * k) // 255).astype(np.uint8)
    return Image.fromarray(a)


def _util_rows(ctx, n=14):
    ua, uc = ctx.util_auto, ctx.util_conv or {}
    by = util_by_campaign(ctx.R)
    keys = sorted(set(ua) | set(uc), key=lambda k: -max(ua.get(k, 0.0), uc.get(k, 0.0)))
    keys = [k for k in keys if max(ua.get(k, 0.0), uc.get(k, 0.0)) > 0.0005][:n]
    return keys, ua, uc, by


def _util_bars(d, t, t0, ctx, box, fs=20, n=14):
    """Stacked bars of the automated run's busy share per station (campaign colours) and a grey bar for the
    conventional run's, growing in from t0."""
    keys, ua, uc, by = _util_rows(ctx, n)
    x0, y0, x1, y1 = box
    if not keys:
        d.text((x0, y0), "utilization: pending", font=St.font(fs), fill=St.INK2)
        return
    k = St.ease((t - t0) / 2.5)
    top = max([ua.get(s, 0.0) for s in keys] + [uc.get(s, 0.0) for s in keys] + [0.05])
    vmax = min(1.0, max(0.1, math.ceil(top * 10 + 1e-9) / 10))
    lab_w = px(250)
    ax = Ax((x0 + lab_w, y0 + px(30), x1 - px(90), y1), (0.0, vmax), (0, 1), "pct", "u")
    f = St.font(fs)
    fsm = St.font(fs - 3)
    xt = St.nice_ticks(0.0, vmax, 5)
    for v in xt:
        x = ax.X(v)
        d.line([(x, ax.y0), (x, ax.y1)], fill=St.GRID, width=1)
        d.text((x, ax.y0 - px(6)), f"{100 * v:.0f} %", font=fsm, fill=St.INK2, anchor="md")
    row_h = (ax.y1 - ax.y0) / len(keys)
    has_conv = bool(uc)
    bh = row_h * (0.34 if has_conv else 0.6)

    def pct(v):
        return f"{100 * v:.1f} %" if v < 0.0095 else f"{100 * v:.0f} %"
    for i, s in enumerate(keys):
        yc = ax.y0 + row_h * (i + 0.5)
        name = STATION_SHORT.get(s) or (ctx.R.stations.get(s) or {}).get("name", s)[:24]
        d.text((ax.x0 - px(12), yc), name, font=f, fill=St.INK, anchor="rm")
        yb = yc - (bh + px(2) if has_conv else bh / 2)
        xcur = ax.X(0)
        for c in D.CAMPAIGNS:
            v = by.get(s, {}).get(c, 0.0) * k
            if v <= 0:
                continue
            xe = ax.X(v) + (xcur - ax.X(0))
            if xe - xcur >= 1:
                d.rounded_rectangle((xcur, yb, max(xcur + 1, xe - px(2)), yb + bh), radius=px(3), fill=St.CAMP[c])
            xcur = xe
        d.text((xcur + px(8), yb + bh / 2), pct(ua.get(s, 0.0)), font=fsm, fill=St.INK2, anchor="lm")
        if has_conv:
            v = uc.get(s, 0.0) * k
            ybb = yc + px(2)
            if v > 0:
                d.rounded_rectangle((ax.X(0), ybb, max(ax.X(0) + 1, ax.X(v)), ybb + bh), radius=px(3),
                                    fill=St.BASE)
            d.text((ax.X(v) + px(8), ybb + bh / 2), pct(uc.get(s, 0.0)), font=fsm, fill=St.INK2, anchor="lm")


def _explain_util(d, t, ctx):
    _util_bars(d, t, 50.4, ctx, _box((80, 200, 1840, 830)), fs=20, n=13)
    lx, ly = px(900), px(905)
    x = lx
    for c in D.CAMPAIGNS:
        swatch(d, x, ly - px(9), St.CAMP[c], s=18)
        lab = f"automated lab, {St.CAMP_NAME[c]}"
        d.text((x + px(28), ly), lab, font=St.font(20), fill=St.INK2, anchor="lm")
        x += px(28) + St.text_w(St.font(20), lab) + px(30)
    if ctx.util_conv:
        swatch(d, x, ly - px(9), St.BASE, s=18)
        d.text((x + px(28), ly), "conventional lab, both", font=St.font(20), fill=St.INK2, anchor="lm")
    d.text((lx, ly + px(40)), f"event hours over units x {ctx.horizon:.0f} days, from the replayed run" +
           (" and a conventional run" if ctx.util_conv else ""), font=St.font(18), fill=St.INK2, anchor="lm")


# =================================================================================================== results
def _leaders() -> str:
    """Who finished highest in the automated lab, as the narration says it (bench2_summary.json, main): BOFN on
    aluminium; on copper, tiered CALPHAD screening ahead of BOFN with blend screening."""
    try:
        import json
        E = json.loads((D.OUT2 / "bench2_summary.json").read_text())["experiments"]["main"]
        g = lambda k, c: E[k]["campaigns"][c]["best_mean"]
        al = max(E, key=lambda k: g(k, "flaime_al"))
        cu = max(E, key=lambda k: g(k, "onr_cu"))
        if not (al.endswith(("_bofn", "_bofn_blend")) and cu.endswith("_tiered")):
            return ""
        return (f" In the automated lab, BOFN finished highest on aluminium; on copper, tiered CALPHAD screening "
                f"finished ahead of BOFN with blend screening ({g(cu, 'onr_cu'):.2f} against "
                f"{g('vertical_lab_bofn_blend', 'onr_cu'):.2f}).")
    except Exception:                                   # noqa: BLE001
        return ""


def _results_lead() -> str:
    """The narrated cut's first results caption: the run counts and the leaders, as the voice says them (DAL audit,
    PR 293 §4: "12 one-year automated runs and 12 three-year conventional runs"; copper over 24 seeds)."""
    a = audit_numbers().get("cu24")
    if not a or not _leaders():
        return ("One twin-year per run, both campaigns at once: the automated lab against the conventional lab, "
                "for each policy.")
    return ("12 one-year automated and 12 three-year conventional runs per policy. BOFN finished highest on aluminium; "
            f"on copper, tiered CALPHAD screening finished ahead of BOFN with blend screening ({a['tiered'][0]:.2f} "
            f"against {a['blend'][0]:.2f} over {a['tiered'][1]} seeds), and plain BOFN did no better than random "
            f"({a['bofn']:.2f} against {a['random']:.2f}).")


# the parts' times: the narrated cut gives the ratios 24 s (its line takes 22) and the cost per experiment 16
RES_T = (0.0, 26.0, 50.0, 66.0, RESULTS_DURATION) if NARRATED else (0.0, 26.0, 46.0, 66.0, RESULTS_DURATION)
RESULTS_CAPTIONS = [
    (RES_T[0], RES_T[1], _results_lead() if NARRATED else
     "One twin-year per run, both campaigns at once: the automated lab against the conventional lab, for each policy."),
    (RES_T[1], RES_T[2], "How much sooner, and for how much less, each campaign reached the state of the art."),
    (RES_T[2], RES_T[3], "Cost per experiment."),
    (RES_T[3], RES_T[4], "Utilization, and the capacity left over for outside users (a cloud user facility)."),
]
POLICY_ORDER = ["cost_aware", "tiered", "random", "cost_aware_tc", "tiered_tc", "cost_aware_scaleup", "bofn", "pkgfn"]


def results_frame(t: float, captions: bool = True) -> np.ndarray:
    ctx = context()
    im = Image.new("RGB", (St.W, St.H), St.BG)
    d = ImageDraw.Draw(im)
    if captions:
        _header(d, "Results", RESULTS_CAPTIONS, t)
    else:
        d.text((px(80), px(44)), "Results", font=St.font(44, bold=True), fill=St.INK)
    parts = [(RES_T[0], RES_T[1], _res_curves), (RES_T[1], RES_T[2], _res_ratios), (RES_T[2], RES_T[3], _res_cost),
             (RES_T[3], RES_T[4], _res_util)]
    for a, b, fn in parts:
        k = min(St.ramp(t, a, a + 0.6) if a > 0 else 1.0,
                1.0 - St.ramp(t, b - 0.5, b) if b < RESULTS_DURATION else 1.0)
        if k <= 0.003:
            continue
        if k >= 0.997:
            fn(d, im, t - a, ctx)
        else:
            lay = Image.new("RGBA", (St.W, St.H), (0, 0, 0, 0))
            fn(ImageDraw.Draw(lay), lay, t - a, ctx)
            _over(im, lay, k)
    return np.asarray(im)


POLICY_SHORT = {"cost_aware": "cost-aware surrogate", "tiered": "tiered CALPHAD", "random": "random",
                "bofn": "BOFN", "bofn_blend": "BOFN + Cu blends", "gpbo": "GP-BO", "sobol": "Sobol",
                "heuristic": "heuristic", "cost_aware_tc": "cost-aware, Thermo-Calc", "tiered_tc": "tiered, Thermo-Calc"}


def _policies(ctx) -> list:
    """Up to four policies, those both labs ran first: the replayed policy's base, then the comparison's, then the
    rest in POLICY_ORDER."""
    G = ctx.B["groups"]
    pols = {p for _, p in G}
    both = {p for p in pols if (ctx.auto, p) in G and (ctx.conv, p) in G}
    first = [str(ctx.pol).split("_blend")[0], ctx.pol, getattr(ctx, "cmp_a", None), getattr(ctx, "cmp_b", None)]
    order = POLICY_ORDER + ["gpbo", "sobol", "heuristic", "bofn_blend"]

    def rank(p):
        return (0 if p in both else 1, first.index(p) if p in first else 9,
                order.index(p) if p in order else 99, p)
    return sorted(pols, key=rank)[:4]


def _res_curves(d, lay, t, ctx):
    pols = _policies(ctx)
    if not pols:
        d.text((px(80), px(220)), "benchmark curves: pending", font=St.font(28), fill=St.INK2)
        return
    H = ctx.horizon
    g = ctx.day_grid
    X0, X1, Y0 = px(150), px(1840), px(200)
    gapx = px(46)
    pw = (X1 - X0 - gapx * (len(pols) - 1)) / len(pols)
    sweep = H * St.ease((t - 0.8) / 5.0)
    k = int(np.searchsorted(g, sweep, side="right"))
    bands = {False: Image.new("RGBA", lay.size, (0, 0, 0, 0)), True: Image.new("RGBA", lay.size, (0, 0, 0, 0))}
    todo = []
    for ri, camp in enumerate(D.CAMPAIGNS):
        ry = Y0 + ri * px(330)
        col = St.CAMP[camp]
        tgt = ctx.T[camp]
        fb = St.font(24, bold=True)
        swatch(d, px(80), ry + px(6), col, s=18)
        d.text((px(108), ry), St.CAMP_NAME[camp], font=fb, fill=St.INK)
        d.text((px(108) + St.text_w(fb, St.CAMP_NAME[camp]) + px(12), ry + px(4)),
               St.CAMP_LONG[camp].split(": ", 1)[-1], font=St.font(20), fill=St.INK2)
        curves = {}
        top = tgt
        for p in pols:
            for fac in (ctx.auto, ctx.conv):
                cv = ctx.B["groups"].get((fac, p), {}).get(camp, [])
                if cv:
                    key = ("res_mean", fac, p, camp)
                    if key not in ctx.__dict__.setdefault("_cache", {}):
                        ctx._cache[key] = D.mean_curve(cv, g, 0)
                    m, se = ctx._cache[key]
                    curves[(fac, p)] = (m, se, len(cv))
                    top = max(top, float((m + se).max()))
        ymax = max(1.2 * tgt, 1.08 * top)
        for ci, p in enumerate(pols):
            x0 = X0 + ci * (pw + gapx)
            ax = Ax((x0, ry + px(76), x0 + pw, ry + px(276)), (0.0, H), (0.0, ymax), "days", "u")
            na = curves.get((ctx.auto, p), (None, None, 0))[2]
            nc = curves.get((ctx.conv, p), (None, None, 0))[2]
            d.text((x0, ry + px(40)), POLICY_SHORT.get(p, D.POLICY_LABEL.get(p, p)), font=St.font(19, bold=True),
                   fill=St.INK)
            d.text((x0 + pw, ry + px(44)), f"n = {na} / {nc}", font=St.font(16), fill=St.INK2, anchor="ra")
            ax.frame(d, fs=16, nx=4, ny=3)
            for fac, c, dashed in ((ctx.conv, St.BASE, True), (ctx.auto, col, False)):
                if (fac, p) not in curves or k < 2:
                    continue
                m, se, n = curves[(fac, p)]
                if n > 1:
                    ax.band(ImageDraw.Draw(bands[dashed]), g[:k], np.maximum(m[:k] - se[:k], 0), m[:k] + se[:k], c,
                            alpha=0.18 if dashed else 0.25)
                todo.append((ax, list(zip(g[:k], m[:k])), c, dashed))
            todo.append((ax, tgt, None, None))
    _over(lay, bands[True])
    _over(lay, bands[False])
    for ax, pts, c, dashed in todo:
        if c is None:
            ax.dotted_h(d, pts, St.TARGET)
        else:
            ax.line(d, pts, c, px(3), dashed=dashed)
    lx, ly = px(900), px(905)
    x = legend_line(d, lx, ly, "solid2", None, "automated lab, mean ± SE", fs=20, w=44)
    legend_line(d, x, ly, "dashed", St.BASE, "conventional, mean ± SE", fs=20, w=44)
    legend_line(d, lx, ly + px(40), "dotted", St.TARGET, "state of the art (target); x: days; n = runs "
                "automated / conventional", fs=20, w=44)


def _ratio_txt(r, at_least=False) -> str:
    if not r or r.get("ratio") is None:
        if r and r.get("ratio_bound") is not None:
            return f"{'at most ' if r.get('bounded') else ''}{fmt_pct(r['ratio_bound'])}"
        return "pending"
    return fmt_pct(r["ratio"])


def _ci(lo, hi, pct=False) -> str:
    def f(v):
        if v is None:
            return "?"
        if v == float("inf"):
            return "unbounded"
        return f"{100 * v:.0f} %" if pct else f"{v:.2g}"
    return "" if lo is None and hi is None else f"95% CI {f(lo)} to {f(hi)}"


def _res_ratios(d, lay, t, ctx):
    for i, camp in enumerate(D.CAMPAIGNS):
        h = ctx.Hd.get(camp, {})
        costs = h.get("costs") or {}
        x0 = px(80) + i * px(900)
        x1 = x0 + px(840)
        y0 = px(190)
        k = St.ramp(t, 0.3 + 0.4 * i, 1.0 + 0.4 * i)
        if k <= 0:
            continue
        ink, ink2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
        d.rounded_rectangle((x0, y0, x1, px(968)), radius=px(16), fill=St.SURF + (255,), outline=St.RULE,
                            width=px(1))
        swatch(d, x0 + px(28), y0 + px(30), St.mix(St.BG, St.CAMP[camp], k), s=20)
        d.text((x0 + px(60), y0 + px(24)), St.CAMP_NAME[camp], font=St.font(30, bold=True), fill=ink)
        d.text((x0 + px(60), y0 + px(64)), St.CAMP_LONG[camp].split(": ", 1)[-1], font=St.font(20), fill=ink2)
        rows = [("time to the target, X", f"{fmt_days(h.get('days_auto'))} automated, "
                 f"{fmt_days(h.get('days_conv'))} conventional; {_ci(h.get('accel_lo'), h.get('accel_hi'))}",
                 (("at least " if h.get("accel_at_least") else "") + fmt_x(h.get("accel"))) if h.get("accel")
                 else "pending", "times faster")]
        if NARRATED and h.get("accel"):
            # DAL audit (PR 293 §4): the conventional lab's copper median is its last hit (6 of 12 runs), so a lower
            # bound; aluminium's factor is mostly the automated lab's stock on the shelf
            n_c, hc = h.get("n_conv", 0), h.get("hit_conv") or 0.0
            lean = audit_numbers().get("lean_af")
            if hc < 1.0:
                rows[0] = ("time to the target, X", f"{fmt_days(h.get('days_auto'))} automated, at least "
                           f"{fmt_days(h.get('days_conv'))} conventional ({round(hc * n_c)} of {n_c} runs got there); "
                           f"{_ci(h.get('accel_lo'), h.get('accel_hi'))}", "≥ " + fmt_x(h.get("accel")), "times faster")
            elif lean:
                rows[0] = ("time to the target, X", f"{fmt_days(h.get('days_auto'))} automated, "
                           f"{fmt_days(h.get('days_conv'))} conventional; {_ci(h.get('accel_lo'), h.get('accel_hi'))}; "
                           f"both labs ordering metal as they go: {lean['af']:.1f}x ({lean['lo']:.1f} to "
                           f"{lean['hi']:.1f})", fmt_x(h.get("accel")), "times faster")
        for key, lab in D.COST_BASES:
            r = costs.get(key)
            det = (f"{fmt_money(r.get('median_new'))} automated, {fmt_money(r.get('median_ref'))} conventional; "
                   f"{_ci(r.get('lo'), r.get('hi'), pct=True)}") if r else "needs econ_summary.json"
            rows.append((f"cost, {lab}", det, _ratio_txt(r), "of the conventional lab's"))
        y = y0 + px(116)
        for j, (lab, detail, big, big_lab) in enumerate(rows):
            d.text((x0 + px(28), y), lab, font=St.font(21, bold=True), fill=ink)
            for jj, ln in enumerate(St.wrap(detail, St.font(17), px(560))[:2]):
                d.text((x0 + px(28), y + px(30) + jj * px(22)), ln, font=St.font(17), fill=ink2)
            if big == "pending":
                d.text((x1 - px(28), y + px(6)), big, font=St.font(28), fill=ink2, anchor="ra")
            else:
                d.text((x1 - px(28), y - px(6)), big, font=St.font(44 if j == 0 else 36, bold=True), fill=ink,
                       anchor="ra")
            d.text((x1 - px(28), y + px(48)), big_lab, font=St.font(15), fill=ink2, anchor="ra")
            y += px(110 if j == 0 else 88)
        n_a, n_c = h.get("n_auto", 0), h.get("n_conv", 0)
        ha, hc = h.get("hit_auto"), h.get("hit_conv")
        foot = (f"reached the target in {round((ha or 0) * 100)} % of {n_a} automated and {round((hc or 0) * 100)} % "
                f"of {n_c} conventional twin-years; target utility {ctx.T[camp]:.2f}")
        if NARRATED:
            foot = (f"reached the target in {round((ha or 0) * n_a)} of {n_a} one-year automated runs and "
                    f"{round((hc or 0) * n_c)} of {n_c} three-year conventional runs; target utility {ctx.T[camp]:.2f}")
        for jj, ln in enumerate(St.wrap(foot, St.font(16), px(790))[:2]):
            d.text((x0 + px(28), px(904) + jj * px(22)), ln, font=St.font(16), fill=ink2)
    cmp_ = ctx.E.get("comparison") or "benchmark curves"
    src = f"source: econ_summary.json, {cmp_}"
    if NARRATED:
        src += ("; the automated lab stocked, the conventional lab ordering as it goes; both ordering as they go: "
                "bench2_summary.json's stock runs")
    d.text((px(80), px(990)), src, font=St.font(17), fill=St.INK2)


CPE_COLORS = {"capex": St.hexrgb("#9887ef"), "service": St.hexrgb("#00a888"), "utilities": St.hexrgb("#d28e05"),
              "labour": St.hexrgb("#e24d8b"), "consumables": St.hexrgb("#c9a26b"),
              "outside_fees": St.hexrgb("#eb6263")}
CPE_LABEL = {"capex": "capex", "service": "service contracts", "utilities": "utilities and space", "labour": "labour",
             "consumables": "consumables", "outside_fees": "outside fees"}


def _res_cost(d, lay, t, ctx):
    pe = ctx.E.get("per_experiment") or {}
    if not any(pe.get(c) for c in D.CAMPAIGNS):
        d.text((px(80), px(200)), "cost per experiment: pending (econ_summary.json)", font=St.font(26, bold=True),
               fill=St.INK2)
        return
    unit = ctx.E.get("cpe_unit", "experiment")
    d.text((px(80), px(196)), f"Cost per {unit}, by what it pays for", font=St.font(26, bold=True), fill=St.INK)
    vmax = max(tot for c in D.CAMPAIGNS for _, _, tot, _ in pe.get(c, [])) or 1.0
    k = St.ease(t / 2.0)
    lab_w, x_ax0, x_ax1 = px(330), px(80) + px(330) + px(140), px(1700)
    y = px(250)
    rh = px(46)
    for camp in D.CAMPAIGNS:
        rows = pe.get(camp, [])
        if not rows:
            continue
        swatch(d, px(80), y + px(6), St.CAMP[camp], s=18)
        d.text((px(108), y), St.CAMP_LONG[camp], font=St.font(21, bold=True), fill=St.INK)
        y += px(38)
        for lab, parts, tot, n in rows:
            yc = y + rh / 2
            d.text((x_ax0 - px(14), yc), lab, font=St.font(19), fill=St.INK, anchor="rm")
            x = x_ax0
            for part in D.CPE_PARTS:
                v = parts.get(part, 0.0) * k
                w = (x_ax1 - x_ax0) * v / vmax
                if w >= 1:
                    d.rectangle((x, yc - px(14), x + w, yc + px(14)), fill=CPE_COLORS[part])
                    x += w + (px(2) if w > px(3) else 0)
            d.text((x + px(10), yc), St.money(tot * k) + (f"  (n = {n})" if n else ""), font=St.font(18),
                   fill=St.INK2, anchor="lm")
            y += rh
        y += px(18)
    lx, ly = px(80), max(y + px(10), px(800))
    for part in D.CPE_PARTS:
        swatch(d, lx, ly - px(9), CPE_COLORS[part], s=18)
        d.text((lx + px(26), ly), CPE_LABEL[part], font=St.font(19), fill=St.INK2, anchor="lm")
        lx += px(26) + St.text_w(St.font(19), CPE_LABEL[part]) + px(30)


def _res_util(d, lay, t, ctx):
    U = ctx.E.get("utilization") or {}
    byc = ctx.E.get("util_by_campaign") or {}
    d.text((px(80), px(196)), "Utilization of the automated lab, both campaigns", font=St.font(26, bold=True),
           fill=St.INK)
    if U:
        keys = [k for k in sorted(U, key=lambda k: -U[k]) if U[k] > 0.0005][:13]
        vmax = max(0.1, math.ceil(max(U[k] for k in keys) * 10 + 1e-9) / 10) if keys else 1.0
        x_ax0, x_ax1 = px(80) + px(260), px(1060)
        y = px(250)
        rh = min(px(44), (px(820) - y) / max(1, len(keys)))
        kk = St.ease(t / 2.0)
        for st in keys:
            yc = y + rh / 2
            d.text((x_ax0 - px(12), yc), STATION_SHORT.get(st, st), font=St.font(19), fill=St.INK, anchor="rm")
            tot_h = sum((byc.get(st) or {}).values()) or 1.0
            x = x_ax0
            for c in D.CAMPAIGNS:
                share = U[st] * ((byc.get(st) or {}).get(c, 0.0) / tot_h if byc.get(st) else 0.5)
                w = (x_ax1 - x_ax0) * share * kk / vmax
                if w >= 1:
                    d.rectangle((x, yc - rh * 0.3, x + w, yc + rh * 0.3), fill=St.CAMP[c])
                    x += w
            d.text((x + px(10), yc), f"{100 * U[st]:.1f} %", font=St.font(17), fill=St.INK2, anchor="lm")
            y += rh
        cw = ctx.E.get("util_capex_weighted")
        if cw is not None:
            d.text((px(80), px(850)), f"capex-weighted mean: {100 * cw:.1f} % of the lab's hours (econ_summary.json)",
                   font=St.font(19), fill=St.INK2)
    else:
        _util_bars(d, t, 0.2, ctx, _box((80, 250, 1100, 830)), fs=18, n=12)
    O = ctx.E.get("outside") or {}
    x0 = px(1180)
    d.text((x0, px(196)), "The spare hours, offered to outside users", font=St.font(26, bold=True), fill=St.INK)
    if not O or O.get("jobs") is None:
        d.text((x0, px(250)), "pending (econ_summary.json)", font=St.font(30), fill=St.INK2)
        return
    cap = O.get("cap")
    d.text((x0, px(236)), f"as a cloud user facility, each station filled to {100 * (cap or 0):.0f} % at most",
           font=St.font(19), fill=St.INK2)
    tiles = [("at capacity", O.get("jobs"), O.get("revenue"), O.get("net"), O.get("net_x_depreciation")),
             (f"demand-limited ({O.get('demand_h_week') or 0:.0f} h a week each)", O.get("dl_jobs"),
              O.get("dl_revenue"), O.get("dl_net"), O.get("dl_net_x_depreciation"))]
    y = px(290)
    kk = St.ease(t / 2.0)
    for lab, jobs, rev, net, xd in tiles:
        d.rounded_rectangle((x0, y, px(1840), y + px(250)), radius=px(14), fill=St.SURF, outline=St.RULE, width=px(1))
        d.text((x0 + px(24), y + px(18)), lab, font=St.font(22, bold=True), fill=St.INK)
        cells = [("outside jobs a year", f"{(jobs or 0) * kk:,.0f}"), ("revenue a year", St.money((rev or 0) * kk)),
                 ("net of handling", St.money((net or 0) * kk)),
                 ("net over the lab's depreciation", f"{(xd or 0) * kk:.1f}x")]
        for j, (cl, cv) in enumerate(cells):
            cx = x0 + px(24) + (j % 2) * px(320)
            cy = y + px(64) + (j // 2) * px(90)
            d.text((cx, cy), cv, font=St.font(36, bold=True), fill=St.INK)
            d.text((cx, cy + px(46)), cl, font=St.font(17), fill=St.INK2)
        y += px(280)


def _cmp_words(c) -> str:
    """'cost_aware on the partners -> bofn in the vertical lab' in words."""
    pb, pa = D.comparison_pair(c) if c else (None, None)
    if pa is None:
        return "the benchmark curves"
    return (f"the automated lab running {D.POLICY_LABEL.get(pb, pb)} against the conventional lab running "
            f"{D.POLICY_LABEL.get(pa, pa)}")


# =================================================================================================== takeaway
def _take_at() -> dict:
    """When each takeaway line starts (s into the segment), from twin/video/narration.json: the narrated card shows
    each part as the voice reaches it."""
    import json
    out = dict(take1=1.0, take1b=21.2, take2=33.2, take3=58.2)
    try:
        for ln in json.loads((D.HERE / "twin" / "video" / "narration.json").read_text())["lines"]:
            if ln.get("seg") == "takeaway" and ln["id"] in out:
                out[ln["id"]] = float(ln.get("at", out[ln["id"]]))
    except Exception:                                   # noqa: BLE001
        pass
    return out


def _x1(v) -> str:
    return "pending" if v is None or not math.isfinite(v) else f"{v:.1f}x"


def _x2(v) -> str:
    """A multiple with the second decimal only where it changes the number: 2.0x, 1.15x (as the narration says them)."""
    if v is None or not math.isfinite(v):
        return "pending"
    return f"{v:.1f}x" if abs(round(v, 2) - round(v, 1)) < 1e-9 else f"{v:.2f}x"


def _rng(lo, hi) -> str:
    f = (lambda v: "unbounded" if v is None or not math.isfinite(v) else (f"{v:.0f}" if v == 0 else f"{v:.1f}"))
    return f"{f(lo)} to {f(hi)}"


def _takeaway_narrated(t: float) -> np.ndarray:
    """The narrated cut's takeaway, reworded as DAL's audit suggests (digital-alloy-lab PR 293 §4): what was compared
    (a stocked automated lab against a conventional lab that orders metal as it goes), aluminium's factor with both
    ordering as they go, copper's as the lower bound it is, the cost on one basis with the equipment included, the
    heuristic comparison and what the target means; each part appears as the narration reaches it."""
    ctx = context()
    E = ctx.E
    acc = (E.get("raw") or {}).get("acceleration") or {}
    nm_h = next((n for n in acc if n.startswith(f"vertical lab + {ctx.pol} vs") and n.endswith("+ heuristic")), None)
    heur = {c: ((acc.get(nm_h) or {}).get(c) or {}).get("compare") or {} for c in D.CAMPAIGNS} if nm_h else {}
    aud = audit_numbers()
    ta = _take_at()
    im = Image.new("RGB", (St.W, St.H), St.BG)
    d = ImageDraw.Draw(im)

    def ink_at(t0, col=St.INK, dur=0.8, bg=St.BG):
        return St.mix(bg, col, St.ramp(t, t0, t0 + dur))
    head = ("In this simulated benchmark, a stocked automated lab reached an alloy better than the reference alloy "
            "sooner than a conventional lab that orders metal as it goes")
    f_head = St.font(32, bold=True)
    for i, ln in enumerate(St.wrap(head, f_head, px(1720))[:2]):
        d.text((St.W / 2, px(52) + i * px(44)), ln, font=f_head, fill=ink_at(0.2), anchor="ma")
    for i, camp in enumerate(D.CAMPAIGNS):
        h = ctx.Hd.get(camp, {})
        costs = h.get("costs") or {}
        cx = St.W / 2 + (i - 0.5) * px(860)
        cy = px(170)
        k = St.ramp(t, 0.6 + 0.5 * i, 1.4 + 0.5 * i)
        ik, ik2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
        d.rounded_rectangle((cx - px(400), cy, cx + px(400), cy + px(500)), radius=px(18),
                            fill=St.mix(St.BG, St.SURF, k), outline=St.mix(St.BG, St.CAMP[camp], k), width=px(3))
        d.text((cx, cy + px(20)), St.CAMP_NAME[camp], font=St.font(32, bold=True), fill=ik, anchor="ma")
        d.text((cx, cy + px(62)), St.CAMP_LONG[camp].split(": ", 1)[-1], font=St.font(21), fill=ik2, anchor="ma")
        lower = (h.get("hit_conv") or 0.0) < 1.0
        big = ("≥ " if lower else "") + _x1(h.get("accel"))
        d.text((cx, cy + px(96)), big, font=St.font(80, bold=True), fill=ik, anchor="ma")
        d.text((cx, cy + px(186)), "sooner", font=St.font(24), fill=ik2, anchor="ma")
        n_c, hc = h.get("n_conv", 0), h.get("hit_conv") or 0.0
        if lower:
            det = (f"{fmt_days(h.get('days_auto'))} against at least {fmt_days(h.get('days_conv'))}: the conventional "
                   f"lab got there in {round(hc * n_c)} of {n_c} three-year runs")
        else:
            det = (f"{fmt_days(h.get('days_auto'))} against {fmt_days(h.get('days_conv'))}; 95 % CI "
                   f"{_rng(h.get('accel_lo'), h.get('accel_hi'))}")
        for jj, ln in enumerate(St.wrap(det, St.font(19), px(740))[:2]):
            d.text((cx, cy + px(222) + jj * px(25)), ln, font=St.font(19), fill=ik2, anchor="ma")
        lean = aud.get("lean_af")
        if camp == "flaime_al" and lean:
            note = f"Both labs ordering metal as they go: {lean['af']:.1f}x ({_rng(lean['lo'], lean['hi'])})"
        else:
            note = "The automated lab also screens powder blends first (BOFN with blend screening)"
        for jj, ln in enumerate(St.wrap(note, St.font(20, bold=True), px(740))[:2]):
            d.text((cx, cy + px(280) + jj * px(26)), ln, font=St.font(20, bold=True),
                   fill=ink_at(ta["take1b"], bg=St.SURF), anchor="ma")
        d.line((cx - px(360), cy + px(338), cx + px(360), cy + px(338)), fill=St.mix(St.BG, St.RULE, k), width=px(1))
        full, cash = costs.get("full_alone") or {}, costs.get("cash") or {}
        kc = ta["take2"]
        d.text((cx, cy + px(352)), _x2(full.get("ratio")), font=St.font(56, bold=True), fill=ink_at(kc, bg=St.SURF),
               anchor="ma")
        d.text((cx, cy + px(420)), "the cost, equipment included", font=St.font(22),
               fill=ink_at(kc, St.INK2, bg=St.SURF), anchor="ma")
        d.text((cx, cy + px(454)), f"95 % CI {_rng(full.get('lo'), full.get('hi'))}  ·  counting only the campaigns' "
               f"spending: {_x1(cash.get('ratio'))}", font=St.font(18), fill=ink_at(kc, St.INK2, bg=St.SURF),
               anchor="ma")
    fs = [ctx.Hd.get(c, {}).get("costs", {}).get("full_shared") or {} for c in D.CAMPAIGNS]
    shared = " and ".join(fmt_pct(x.get("ratio")) for x in fs)
    cost_note = ("With the equipment included, it costs less than the conventional lab only for copper, and only if "
                 "outside users rent its idle hours, which this model assumes and does not show "
                 f"(full cost with outside users: {shared}).")
    for i, ln in enumerate(St.wrap(cost_note, St.font(21), px(1720))[:2]):
        d.text((St.W / 2, px(690) + i * px(29)), ln, font=St.font(21), fill=ink_at(ta["take2"] + 8.0, St.INK2),
               anchor="ma")
    if heur:
        fa, fc = heur.get("flaime_al", {}), heur.get("onr_cu", {})
        da, dc = fa.get("days") or {}, fc.get("days") or {}
        opa = ((fa.get("cost") or {}).get("operating, alone") or {}).get("ratio")
        hl = ("Against a conventional lab run by a metallurgist's rules of thumb: no faster on aluminium "
              f"({da.get('af', float('nan')):.2f}x, {_rng(da.get('lo'), da.get('hi'))}) at {_x1(opa)} the operating "
              f"cost; {_x1(dc.get('af'))} faster on copper ({_rng(dc.get('lo'), dc.get('hi'))}).")
        for i, ln in enumerate(St.wrap(hl, St.font(22, bold=True), px(1720))[:2]):
            d.text((St.W / 2, px(768) + i * px(30)), ln, font=St.font(22, bold=True), fill=ink_at(ta["take3"]),
                   anchor="ma")
    fr_ = aud.get("frac_random")
    refs = D.target_refs() if hasattr(D, "target_refs") else {}
    tgt = (f"The target is the reference alloy's score on the twin's synthetic alloy model ({ctx.T['flaime_al']:.2f}, "
           f"{ctx.T['onr_cu']:.2f}). One random design in {round(1 / fr_) if fr_ else 12} beats it, so reaching it "
           "shows how fast a lab tests its first alloys, not a discovery.")
    for i, ln in enumerate(St.wrap(tgt, St.font(19), px(1720))[:2]):
        d.text((St.W / 2, px(852) + i * px(26)), ln, font=St.font(19), fill=ink_at(2.0, St.INK2), anchor="ma")
    foot = ("A synthetic benchmark: simulated campaigns in a digital twin, not lab results. 12 one-year automated and "
            "12 three-year conventional runs per policy.")
    for i, ln in enumerate(St.wrap(foot, St.font(22, bold=True), px(1720))[:2]):
        d.text((St.W / 2, px(930) + i * px(30)), ln, font=St.font(22, bold=True), fill=ink_at(2.5), anchor="ma")
    return np.asarray(im)


def takeaway_frame(t: float) -> np.ndarray:
    """The takeaway card; everything above y = 860 so the docked DAG's corner stays clear."""
    if NARRATED:
        return _takeaway_narrated(t)
    ctx = context()
    im = Image.new("RGB", (St.W, St.H), St.BG)
    d = ImageDraw.Draw(im)
    k0 = St.ramp(t, 0.2, 1.0)
    ink = St.mix(St.BG, St.INK, k0)
    f_head = St.font(36, bold=True)
    head = "In this simulated benchmark, the automated lab reached state-of-the-art alloys"
    for i, ln in enumerate(St.wrap(head, f_head, px(1700))):
        d.text((St.W / 2, px(110) + i * px(50)), ln, font=f_head, fill=ink, anchor="ma")
    for i, camp in enumerate(D.CAMPAIGNS):
        h = ctx.Hd.get(camp, {})
        k = St.ramp(t, 1.0 + 0.6 * i, 2.0 + 0.6 * i)
        cx = St.W / 2 + (i - 0.5) * px(860)
        cy = px(250)
        col = St.mix(St.BG, St.CAMP[camp], k)
        ik, ik2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
        d.rounded_rectangle((cx - px(400), cy, cx + px(400), cy + px(450)), radius=px(18),
                            fill=St.mix(St.BG, St.SURF, k), outline=col, width=px(3))
        d.text((cx, cy + px(26)), St.CAMP_NAME[camp], font=St.font(34, bold=True), fill=ik, anchor="ma")
        d.text((cx, cy + px(72)), St.CAMP_LONG[camp].split(": ", 1)[-1], font=St.font(22), fill=ik2, anchor="ma")
        x_txt = fmt_x(h.get("accel"))
        if h.get("accel_at_least") and x_txt != "pending":
            x_txt = "≥ " + x_txt
        y_txt = fmt_pct(h.get("y"))
        if x_txt == "pending":
            d.text((cx, cy + px(150)), x_txt, font=St.font(44), fill=ik2, anchor="ma")
        else:
            d.text((cx, cy + px(112)), x_txt, font=St.font(96, bold=True), fill=ik, anchor="ma")
        d.text((cx, cy + px(226)), "faster", font=St.font(28), fill=ik2, anchor="ma")
        if y_txt == "pending":
            d.text((cx, cy + px(290)), y_txt, font=St.font(44), fill=ik2, anchor="ma")
        else:
            d.text((cx, cy + px(272)), y_txt, font=St.font(72, bold=True), fill=ik, anchor="ma")
        words = h.get("y_words") or "cost: pending"
        for jj, ln in enumerate(St.wrap(words, St.font(21), px(740))[:2]):
            d.text((cx, cy + px(352) + jj * px(28)), ln, font=St.font(21), fill=ik2, anchor="ma")
        d.text((cx, cy + px(412)), f"operating (no capex): {fmt_pct(h.get('cost_ratio'))}  ·  full, with capex: "
               f"{fmt_pct(h.get('cost_ratio_capex'))}", font=St.font(17), fill=ik2, anchor="ma")
    k2 = St.ramp(t, 2.5, 3.5)
    small = St.mix(St.BG, St.INK2, k2)
    pol = D.POLICY_LABEL.get(ctx.pol, ctx.pol)
    na = [ctx.Hd.get(c, {}).get("n_auto", 0) for c in D.CAMPAIGNS]
    nc = [ctx.Hd.get(c, {}).get("n_conv", 0) for c in D.CAMPAIGNS]
    cond = (f"Runs: {na[0]} automated and {nc[0]} conventional twin-years. "
            f"Target utility: {ctx.T['flaime_al']:.2f} (FLAIME), {ctx.T['onr_cu']:.2f} (ONR). "
            "X: median days to the target, conventional over automated. Y: the cost of getting there, automated "
            "over conventional" + ("; operating cost is materials, outside fees, labour, service contracts, "
                                   "utilities and space, without the equipment's capital cost" if NARRATED else "") +
            f". Compared: {_cmp_words(ctx.E.get('comparison'))}.")
    f = St.font(21)
    for i, ln in enumerate(St.wrap(cond, f, px(1700))[:3]):
        d.text((St.W / 2, px(724) + i * px(30)), ln, font=f, fill=small, anchor="ma")
    d.text((St.W / 2, px(830)), "A synthetic benchmark: simulated campaigns in a digital twin, not lab results.",
           font=St.font(24, bold=True), fill=St.mix(St.BG, St.INK, k2), anchor="ma")
    # the same automated lab against the conventional lab run the usual way (a metallurgist's heuristic), so the card
    # is not read as the only comparison; its costs are in the results
    try:
        acc = (ctx.E.get("raw") or {}).get("acceleration") or {}
        nm = next((n for n in acc if n.startswith(f"vertical lab + {ctx.pol} vs") and n.endswith("+ heuristic")),
                  None)
        bits = []
        for c, lab in (("flaime_al", "FLAIME"), ("onr_cu", "ONR")):
            af = ((acc.get(nm) or {}).get(c) or {}).get("compare", {}).get("days", {}).get("af") if nm else None
            if af is not None and math.isfinite(af):
                bits.append(f"{lab} {af:.1f}x")
        if bits:
            d.text((St.W / 2, px(884)), "Against the conventional lab run with a metallurgist's heuristic instead: "
                   + ", ".join(bits) + " faster (costs for every comparison: notes/twin_econ.md).",
                   font=St.font(21), fill=small, anchor="ma")
    except Exception:                                   # noqa: BLE001
        pass
    return np.asarray(im)


# ====================================================================================================== stills
if __name__ == "__main__":                                  # python -m twin.video.figs_anim  -> /tmp/vid/figs_*.png
    import subprocess
    import sys
    import time
    from pathlib import Path
    out = Path("/tmp/vid")
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    R = D.Replay()
    B = D.bench([R])
    ctx = context(R, B)
    print(f"context {time.time() - t0:.2f} s; groups {list(B['groups'])}; placeholder {ctx.placeholder}")
    bg = out / "figs_bg.png"
    if not bg.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "100", "-i", str(D.HERE / "out/hd/setup_lab.mp4"),
                        "-vframes", "1", str(bg)], check=True)
    base = np.asarray(Image.open(bg).convert("RGB").resize((St.W, St.H)))
    pp = PlotPanel(R, B)
    which = sys.argv[1:] or ["panel", "explain", "results", "takeaway"]
    if "panel" in which:
        ts = []
        for day in (2, 30, 200, 365):
            a = time.time()
            im = pp.draw(day * HPD)
            ts.append(time.time() - a)
            fr = base.copy()
            St.paste(fr, im, px(1296), px(640))
            Image.fromarray(fr).save(out / f"figs_panel_{day:03d}.png")
        for _ in range(20):
            a = time.process_time()
            pp.draw(150 * HPD)
            ts.append(time.process_time() - a)
        print("panel ms", [round(1000 * x, 1) for x in ts[:4]], "mean", round(1000 * np.mean(ts[4:]), 1))
    if "explain" in which:
        for tt in (5, 10.5, 15, 24, 33, 40, 47, 56):
            a = time.process_time()
            Image.fromarray(explain_frame(tt)).save(out / f"figs_explain_{tt:04.1f}.png")
            print("explain", tt, round(1000 * (time.process_time() - a), 1), "ms cpu")
    if "results" in which:
        for tt in (3, 12, 30, 40, 55, 75):
            a = time.process_time()
            Image.fromarray(results_frame(tt)).save(out / f"figs_results_{tt:02d}.png")
            print("results", tt, round(1000 * (time.process_time() - a), 1), "ms cpu")
    if "takeaway" in which:
        a = time.time()
        Image.fromarray(takeaway_frame(8)).save(out / "figs_takeaway.png")
        print("takeaway", round(1000 * (time.time() - a), 1), "ms")
