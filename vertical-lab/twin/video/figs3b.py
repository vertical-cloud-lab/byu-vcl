"""Round 3b's cards (TWIN_VIDEO_ROUND=3b): round 3's cut with what round 3b changes. Drawn with PIL frame by frame, like
figs3's, and with figs3's own cards wherever round 3b changes nothing.

    changes_frame(t), CHANGES_DURATION       round 3's six changes, and round 3b's: the missing arms, and the reruns
    explain_frame(t), EXPLAIN_DURATION       the two targets; then the lab comparison like for like (both labs ordering
                                             metal as they go), why its factor is a lower bound, and the stock as a
                                             separate effect
    assume_frame(t), ASSUME_DURATION         figs3's (the atomizer's design targets against the lab's record)
    results_frame(t), RESULTS_DURATION       figs3's first three parts: the policies in the stocked automated lab
    labs_frame(t), LABS_DURATION             four parts: like for like; what the stock buys; where the automated lab
                                             doesn't win; the cost as campaign spend, with fixed costs left out
    takeaway_frame(t), TAKEAWAY_DURATION     the takeaway

Every number comes from numbers3b.numbers(): out/twin3b/like3b.json (what out/twin3b/tables.md prints) on top of round
3's committed summaries. The rules round 3's cut took from DAL's audit stand, and round 3b adds its own:

- the lab comparison leads with like for like: both labs ordering metal as they go;
- a factor of round 3's pairing (the automated lab stocked, the conventional lab ordering as it goes) appears only
  labelled as that, beside the like-for-like one;
- what the stock buys is shown as stocking, the automated lab against itself, never as the lab's factor;
- where the automated lab doesn't win is its own card;
- the cost is campaign spend to the target, one basis, and the card says fixed costs are left out.

Each part appears when the narration reaches it: the cue times are the lines' `at` in narration3b.json.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

from . import data as D
from . import figs3 as F3
from . import figs_anim as F
from . import numbers3b as NB
from . import style as St
from .figs3 import (ASSUME_DURATION, CAMP_WORD, H, POL, W, _ink, _new, _para, _title, assume_frame,  # noqa: F401
                    cue)
from .style import px

AL, CU = "flaime_al", "onr_cu"
CHANGES_DURATION = 39.0
EXPLAIN_DURATION = 78.5
RESULTS_DURATION = 81.5
LABS_DURATION = 109.0
TAKEAWAY_DURATION = 58.5
LIGHT = 0.42                                            # a campaign's colour, dimmed: the stocked arm beside the lean


def _n() -> dict:
    return NB.numbers()


def _x(c: dict) -> str:
    return NB.big(c)


def _ci(c: dict) -> str:
    return NB.rng(c["lo"], c["hi"])


def _day(v) -> str:
    return "never" if v is None or not math.isfinite(v) else f"day {v:.0f}"


def _lite(col, bg=St.BG):
    return St.mix(col, bg, LIGHT)


# ================================================================================ what changed, rounds 3 and 3b
def _changes() -> list:
    rr = _n()["reruns"]
    return F3._changes() + [
        ("Round 3b: like for like, and round 3 rerun",
         "New runs: the automated lab ordering metal as it goes, the conventional lab stocked, and BOFN and pKGFN in "
         f"the conventional lab (4 seeds). Round 3's runs rerun under a pinned set-up: {rr['identical']} of "
         f"{rr['rerun']} identical, the other {rr['last_bit']} to the last bit of a utility."),
    ]


def changes_frame(t: float) -> np.ndarray:
    im, d = _new()
    _title(d, "Rounds 3 and 3b: what changed in the twin", "The same two campaigns and the same lab design as round "
           "2's video. Everything is simulated.", t)
    y = px(196)
    items = _changes()
    c2 = cue("chg2", 20.8)
    for i, (head, body) in enumerate(items):
        t0 = 0.6 + 2.6 * i if i < len(items) - 1 else c2 - 0.3
        k = St.ramp(t, t0, t0 + 0.7)
        last = i == len(items) - 1
        d.rounded_rectangle((px(80), y + px(8), px(96), y + px(24)), radius=px(4),
                            fill=St.mix(St.BG, St.INK if last else (St.CAMP[AL] if i % 2 == 0 else St.CAMP[CU]), k))
        d.text((px(116), y), head, font=St.font(27, bold=True), fill=St.mix(St.BG, St.INK, k))
        yy = _para(d, px(116), y + px(40), body, St.font(21), St.mix(St.BG, St.INK2, k), px(1700), px(29))
        y = max(yy + px(18), y + px(106))
    return np.asarray(im)


# ============================================================================================== the explainer
EX_L = (190, 262, 890, 742)
EX_R = (1010, 262, 1840, 742)
_CURVES: dict = {}


def _mean3b(exp: str, facility: str, policy: str, camp: str, grid) -> dict | None:
    """The mean best-new-alloy-so-far curve of one of round 3b's arms on the day grid."""
    key = (exp, facility, policy, camp)
    if key not in _CURVES:
        cv = [np.array(r["campaigns"][camp]["curve_new"], float).reshape(-1, 3)
              for r in sorted(D.rows3b(exp), key=lambda r: r["cfg"]["seed"])
              if r["cfg"]["policy"] == policy and r["cfg"]["facility"] == facility]
        m, se = D.mean_curve(cv, grid, 0) if cv else (None, None)
        _CURVES[key] = dict(n=len(cv), mean=m, se=se) if cv else None
    return _CURVES[key]


def explain_caps() -> list:
    n = _n()
    T1, T2 = n["targets"]["T1"][AL], n["targets"]["T2"][AL]
    like = n["lab"]["like"][AL]["T2"]["pkgfn_thumb"]["days"]
    st = n["stock"]["vertical_lab"]["pkgfn3"][AL]["T2"]["days"]
    r3 = n["lab"]["round3"][AL]["T2"]["pkgfn_thumb"]["days"]
    c2, c3, c4, c5 = (cue(k, v) for k, v in (("fig2", 15.2), ("fig3", 22.4), ("fig4", 34.5), ("fig5", 57.3)))
    return [
        (0.0, c2 - 0.4, f"Best new alloy so far: the highest utility of any new alloy tested yet. First dotted line: "
                        f"the best existing alloy on this synthetic benchmark ({n['targets']['ref'][AL]}, {T1:.2f}). "
                        f"One random design in {n['targets']['one_in']} beats it: a low bar."),
        (c2 - 0.4, c3 - 0.4, f"The halfway target ({T2:.2f}): halfway from the best existing alloy to the best alloy "
                             "the twin's own search found."),
        (c3 - 0.4, c4 - 0.4, "Grey, dashed: a conventional lab run by rule of thumb, through partner and core "
                             "facilities. Like for like: both labs here order their metal as they go."),
        (c4 - 0.4, c5 - 0.4, f"Days to a target: the median over 12 runs. Halfway target: {_day(like['m_new'])} "
                             f"automated ({like['hit_new']} of 12 runs), {_day(like['m_ref'])} conventional "
                             f"({like['hit_ref']} of 12). So the factor is a lower bound: {_x(like)}."),
        (c5 - 0.4, EXPLAIN_DURATION, f"Stocking is a separate effect: with its metal on the shelf from day 0, the same "
                                     f"automated lab gets there on {_day(st['m_new'])}, {_x(st)} sooner. Round 3's "
                                     f"{NB.x1(r3['af'])} set that stocked lab against a conventional lab ordering as "
                                     "it goes."),
    ]


def explain_frame(t: float, captions: bool = True) -> np.ndarray:
    n = _n()
    ctx = F.context()
    camp = AL
    col = St.CAMP[camp]
    T1, T2 = n["targets"]["T1"][camp], n["targets"]["T2"][camp]
    like = n["lab"]["like"][camp]["T2"]["pkgfn_thumb"]["days"]
    st = n["stock"]["vertical_lab"]["pkgfn3"][camp]["T2"]["days"]
    g = ctx.day_grid
    lean = _mean3b("v_lean", "vertical_lab", "pkgfn3", camp, g)             # the automated lab ordering as it goes
    stocked = ctx._curves(ctx.group(ctx.auto, camp, "pkgfn3"))              # round 3's arm: stocked on day 0
    bm = ctx._curves(ctx.group(ctx.conv, camp, "heuristic"))                # the conventional lab, ordering as it goes
    caps = explain_caps()
    c2, c3, c4, c5 = caps[1][0], caps[2][0], caps[3][0], caps[4][0]
    im, d = _new()
    if captions:
        F._header(d, "The figures we track", caps, t, total=EXPLAIN_DURATION)
    else:
        d.text((px(80), px(44)), "The figures we track", font=St.font(44, bold=True), fill=St.INK)
    # ------------------------------------------------------------------------------------ left: the curves
    Hd = 365.0
    ax = F.Ax(F._box(EX_L), (0.0, Hd), (0.0, 0.8), "days", "u")
    ax.frame(d, fs=18, nx=5, ny=4, xlabel="days since the start (the first year of both labs)",
             ylabel="utility of the best new alloy so far", fs_label=20)
    sweep = Hd * St.ease((t - 1.0) / 6.0)
    k1 = St.ramp(t, 5.2, 6.0)                            # the first target
    k2 = St.ramp(t, c2 + 0.3, c2 + 1.1)                  # the halfway target
    kb = St.ramp(t, c3 + 0.3, c3 + 5.0)                  # the conventional lab
    k5 = St.ramp(t, c5 + 0.3, c5 + 3.3)                  # the stocked arm
    if k1 > 0:
        ax.dotted_h(d, T1, St.mix(St.BG, St.TARGET, k1), r=px(2.2), gap=px(10))
    if k2 > 0:
        ax.dotted_h(d, T2, St.mix(St.BG, St.TARGET, k2), r=px(2.2), gap=px(10))
    if stocked is not None and k5 > 0:
        F._mean_line(ax, d, g, stocked["mean"], Hd * k5, _lite(col), px(2))
    if bm is not None and kb > 0:
        F._mean_line(ax, d, g, bm["mean"], Hd * kb, St.BASE, px(3), dashed=True)
    if lean is not None:
        F._mean_line(ax, d, g, lean["mean"], sweep, col, px(3))
        if t < 7.0:
            ax.dot(d, sweep, float(np.interp(sweep, g, lean["mean"])), col, r=6)
    if k1 > 0:
        F.label_box(d, (ax.x1 - px(8), ax.Y(T1) + px(10)), f"the best existing alloy: {T1:.2f}",
                    St.font(18, bold=True), St.mix(St.BG, St.INK, k1), anchor="ra", pad=px(4))
    if k2 > 0:
        F.label_box(d, (ax.x1 - px(8), ax.Y(T2) - px(12)), f"halfway target: {T2:.2f}", St.font(18, bold=True),
                    St.mix(St.BG, St.INK, k2), anchor="rd", pad=px(4))
    ke = St.ramp(t, c4 + 3.0, c4 + 4.0)                  # the read-off at the halfway target
    kse = St.ramp(t, c5 + 5.0, c5 + 6.0)
    marks = [(like["m_new"], col, ke), (like["m_ref"], St.BASE, ke), (st["m_new"], _lite(col), kse)]
    for v, cc, kk in marks:
        if kk > 0 and v is not None and math.isfinite(v) and v <= Hd:
            x, y = ax.X(v), ax.Y(T2)
            d.line([(x, y), (x, ax.y1)], fill=St.mix(St.BG, cc, kk), width=px(2))
            d.ellipse((x - px(7), y - px(7), x + px(7), y + px(7)), fill=St.mix(St.BG, cc, kk),
                      outline=St.mix(St.BG, St.INK, kk), width=px(2))
            F.label_box(d, (x, ax.y1 - px(34)), f"{v:.0f}", St.font(18, bold=True), St.mix(St.BG, St.INK, kk),
                        anchor="ma", pad=px(3))
    # legend, bottom right (the docked networks keep the bottom left)
    lx, ly = px(880), px(898)
    na = lean["n"] if lean else 0
    F.legend_line(d, lx, ly, "solid", col, f"automated lab, pKGFN, ordering metal as it goes (mean of {na} one-year "
                  "runs)", fs=18, w=40)
    if kb > 0 and bm is not None:
        F.legend_line(d, lx, ly + px(33), "dashed", St.BASE, f"conventional lab, rule of thumb, ordering metal as it "
                      f"goes (mean of {bm['n']} three-year runs)", fs=18, w=40)
    if k1 > 0:
        x = F.legend_line(d, lx, ly + px(66), "dotted", St.TARGET, "the two targets", fs=18, w=40)
        if k5 > 0 and stocked is not None:
            d.line([(x, ly + px(66)), (x + px(40), ly + px(66))], fill=_lite(col), width=px(2))
            d.text((x + px(48), ly + px(66)), f"the same automated lab stocked on day 0 (mean of {stocked['n']})",
                   font=St.font(18), fill=St.INK2, anchor="lm")
    # ------------------------------------------------------------------------------------ right: the panel
    kt = min(St.ramp(t, 5.2, 6.0), 1.0 - St.ramp(t, c4 - 0.4, c4 + 0.3))          # the targets, for both campaigns
    ks = St.ramp(t, c4 + 0.3, c4 + 1.1)                                          # each run's day, as marks
    if kt > 0.003:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        F3._targets_table(ImageDraw.Draw(lay), n, k2)
        F._over(im, lay, kt)
    if ks > 0.003:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        _runs_strip(ImageDraw.Draw(lay), t - c4, t - c5, camp, T2)
        F._over(im, lay, ks)
    return np.asarray(im)


def _runs_strip(d, t, t5, camp, tgt):
    """Each run's first day at the halfway target: the two labs like for like (both ordering as they go), then the
    same automated lab stocked, which is the stock's effect and not the lab's."""
    n = _n()
    like = n["lab"]["like"][camp]["T2"]["pkgfn_thumb"]["days"]
    st = n["stock"]["vertical_lab"]["pkgfn3"][camp]["T2"]["days"]
    r3 = n["lab"]["round3"][camp]["T2"]["pkgfn_thumb"]["days"]
    x0, y0, x1, _ = F._box(EX_R)
    d.rounded_rectangle((x0, y0, x1, y0 + px(612)), radius=px(16), fill=St.SURF + (255,), outline=St.RULE,
                        width=px(1))
    d.text((x0 + px(28), y0 + px(18)), f"Each run's first day at the halfway target ({tgt:.2f})",
           font=St.font(24, bold=True), fill=St.INK)
    ax0, ax1 = x0 + px(40), x1 - px(190)
    col = St.CAMP[camp]
    k5 = St.ramp(t5, 0.3, 1.1)
    rows = [("automated lab, pKGFN: 12 one-year runs, ordering metal as it goes", [q["new"] for q in like["per_seed"]],
             col, like["m_new"], "in its year", 1.0, 0.0),
            ("conventional lab, rule of thumb: 12 three-year runs, ordering metal as it goes",
             [q["ref"] for q in like["per_seed"]], St.BASE, like["m_ref"], "in three years", 1.0, 5.6),
            ("the same automated lab stocked on day 0 (round 3's arm): the stock's effect",
             [q["new"] for q in st["per_seed"]], _lite(col, St.SURF), st["m_new"], "in its year", k5, None)]
    for i, (lab_, days, cc, med, never_words, kr, delay) in enumerate(rows):
        if kr <= 0:
            continue
        tt = t - delay if delay is not None else t5
        ink, ink2 = St.mix(St.SURF, St.INK, kr), St.mix(St.SURF, St.INK2, kr)
        y = y0 + px(64) + i * px(134)
        d.text((ax0, y), lab_, font=St.font(17), fill=ink2)
        ya = y + px(82)
        d.line([(ax0, ya), (ax1, ya)], fill=St.mix(St.SURF, St.RULE, kr), width=px(2))
        for v in (0, 100, 200, 300, 365):
            xx = ax0 + (ax1 - ax0) * v / 365.0
            d.line([(xx, ya), (xx, ya + px(6))], fill=St.mix(St.SURF, St.RULE, kr), width=px(1))
            d.text((xx, ya + px(9)), f"{v}", font=St.font(14), fill=ink2, anchor="ma")
        hits = sorted(v for v in days if v is not None)
        shown = len(hits) * St.ease((tt - 1.0) / 2.0)
        for j, v in enumerate(hits):
            if j >= shown or v > 365:
                continue
            xx = ax0 + (ax1 - ax0) * v / 365.0
            d.ellipse((xx - px(8), ya - px(8), xx + px(8), ya + px(8)), fill=St.mix(St.SURF, cc, kr),
                      outline=St.SURF, width=px(2))
        km = St.ramp(tt, 3.4, 4.2) * kr
        if med is not None and math.isfinite(med) and km > 0:
            xx = ax0 + (ax1 - ax0) * med / 365.0
            d.line([(xx, ya - px(28)), (xx, ya + px(4))], fill=St.mix(St.SURF, St.INK, km), width=px(3))
            last = " (its last)" if 2 * len(hits) == len(days) else ""
            lab_m = f"median: day {med:.0f}{last}"
            fm = St.font(17, bold=True)
            xm = min(max(xx, ax0 + St.text_w(fm, lab_m) / 2), ax1 - St.text_w(fm, lab_m) / 2 + px(150))
            d.text((xm, ya - px(31)), lab_m, font=fm, fill=St.mix(St.SURF, St.INK, km), anchor="md")
        never = len(days) - len(hits)
        d.rounded_rectangle((ax1 + px(24), ya - px(32), x1 - px(24), ya + px(32)), radius=px(8),
                            outline=St.mix(St.SURF, St.RULE, kr), width=px(1))
        d.text(((ax1 + px(24) + x1 - px(24)) / 2, ya - px(11)), f"{never} of {len(days)}",
               font=St.font(20, bold=True), fill=ink, anchor="mm")
        d.text(((ax1 + px(24) + x1 - px(24)) / 2, ya + px(13)), f"never, {never_words}", font=St.font(13),
               fill=ink2, anchor="mm")
    kf = St.ramp(t, 15.5, 16.5)
    yy = y0 + px(474)
    d.text((x0 + px(40), yy), f"Like for like: {like['m_ref']:.0f} / {like['m_new']:.0f} days: {_x(like)} sooner",
           font=St.font(25, bold=True), fill=St.mix(St.SURF, St.INK, kf))
    d.text((x0 + px(40), yy + px(36)), "at least: the conventional lab's median is its last run to get there",
           font=St.font(16), fill=St.mix(St.SURF, St.INK2, kf))
    kg = St.ramp(t5, 6.0, 7.0)
    d.text((x0 + px(40), yy + px(66)), f"The stock: {st['m_ref']:.0f} / {st['m_new']:.0f} days: {_x(st)} sooner",
           font=St.font(25, bold=True), fill=St.mix(St.SURF, St.INK, kg))
    d.text((x0 + px(40), yy + px(102)), f"Round 3's pairing (stocked against ordering as it goes): {r3['m_ref']:.0f} / "
           f"{r3['m_new']:.0f} days = {_x(r3)}, the two multiplied", font=St.font(15),
           fill=St.mix(St.SURF, St.INK2, St.ramp(t5, 9.5, 10.5)))


# ============================================================================ results: the policies (figs3's cards)
def res_t() -> tuple:
    """When each of the three parts starts (0.8 s before its narration line)."""
    return (0.0,) + tuple(max(1.0, cue(k, v) - 0.8) for k, v in (("res2", 24.5), ("res3", 57.0))) + \
        (RESULTS_DURATION,)


def results_caps() -> list:
    n = _n()
    M, cm = n["main"], n["cu_money"]
    T = res_t()
    return [
        (T[0], T[1], f"12 simulated one-year runs per policy in the automated lab, stocked on day 0. Aluminium: BOFN "
                     f"and pKGFN finished highest ({M['bofn3'][AL]['best']:.2f} and {M['pkgfn3'][AL]['best']:.2f}). "
                     f"Copper: tiered CALPHAD screening still finished ahead ({M['tiered'][CU]['best']:.2f} against "
                     f"{M['bofn3'][CU]['best']:.2f} and {M['pkgfn3'][CU]['best']:.2f})."),
        (T[1], T[2], "Days to each target, every run a mark. The median is the 6th of 12 runs to get there; no "
                     "median when fewer than half do."),
        (T[2], T[3], "Copper is limited by money, not by capacity: removing the cap did not speed it up. With three "
                     f"times the copper money, BOFN and pKGFN gain {cm['bofn3']['own']['mean']:.2f} and "
                     f"{cm['pkgfn3']['own']['mean']:.2f} ({cm['bofn3']['n']} runs each)."),
    ]


def _parts(d, im, t, T, parts, total, ctx=None):
    for i, fn in enumerate(parts):
        a, b = T[i], T[i + 1]
        k = min(St.ramp(t, a, a + 0.6) if a > 0 else 1.0, 1.0 - St.ramp(t, b - 0.5, b) if b < total else 1.0)
        if k <= 0.003:
            continue
        if k >= 0.997:
            fn(d, im, t - a, ctx)
        else:
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            fn(ImageDraw.Draw(lay), lay, t - a, ctx)
            F._over(im, lay, k)


def results_frame(t: float, captions: bool = True) -> np.ndarray:
    ctx = F.context()
    im, d = _new()
    if captions:
        F._header(d, "Results: the policies in the automated lab", results_caps(), t, total=RESULTS_DURATION)
    else:
        d.text((px(80), px(44)), "Results", font=St.font(44, bold=True), fill=St.INK)
    _parts(d, im, t, res_t(), [F3._res_curves, F3._res_days, F3._res_money], RESULTS_DURATION, ctx)
    return np.asarray(im)


# =========================================================================== the lab comparison, like for like
def labs_t() -> tuple:
    return (0.0,) + tuple(max(1.0, cue(k, v) - 0.8) for k, v in (("stk1", 30.6), ("tie1", 53.6), ("cost1", 79.0))) + \
        (LABS_DURATION,)


def labs_caps() -> list:
    T = labs_t()
    return [
        (T[0], T[1], "Like for like: both labs order their metal as they go. Automated lab: one-year runs at one "
                     "year's money. Conventional lab: three-year runs at three years' money. Simulated."),
        (T[1], T[2], "What the stock buys: the simulated automated lab against itself, stocked on day 0 or ordering "
                     "its metal as it goes. Stocking is its own effect, not the lab's."),
        (T[2], T[3], "Where the automated lab doesn't win: the same optimizer in both labs, both ordering metal as "
                     "they go. 4 seeds; the conventional lab's runs are three simulated years."),
        (T[3], T[4], "Cost on one basis: simulated campaign spend to the target (metal, consumables, outside "
                     "services). Fixed costs are left out: staff, equipment and the building."),
    ]


def labs_frame(t: float, captions: bool = True) -> np.ndarray:
    im, d = _new()
    if captions:
        F._header(d, "The lab comparison, like for like", labs_caps(), t, total=LABS_DURATION)
    else:
        d.text((px(80), px(44)), "The lab comparison, like for like", font=St.font(44, bold=True), fill=St.INK)
    _parts(d, im, t, labs_t(), [_lab_like, _lab_stock, _lab_tie, _lab_cost], LABS_DURATION)
    return np.asarray(im)


def _join(vals: list) -> str:
    vals = list(dict.fromkeys(vals))
    return vals[0] if len(vals) == 1 else " and ".join(vals)


def _cell(d, x0, y0, w, who: list, cells: list, r3: list, k, bg=St.SURF):
    """One comparison to one target: the factor (two policies' side by side when they differ), the median days, the
    interval, the runs that got there, the seeds in which the automated lab was first, and, smaller and labelled,
    round 3's pairing of the same comparison."""
    ink, ink2 = St.mix(bg, St.INK, k), St.mix(bg, St.INK2, k)
    kinds = {c["kind"] for c in cells}
    nn = cells[0]["n"]
    y = y0
    if kinds == {"none"} or kinds <= {"none", "at_most"}:
        slower = all(2 * c["hit_ref"] >= c["n"] for c in cells)
        d.text((x0, y + px(8)), "no speed-up" if slower else "no factor", font=St.font(30), fill=ink2)
        y += px(58)
        y = _para(d, x0, y, "the automated lab got there in fewer runs" if slower else
                  "neither lab got there in half its runs", St.font(16), ink2, w, px(22), max_lines=2)
    else:
        x = x0
        if kinds == {"at_least"}:
            d.text((x, y + px(22)), "at least", font=St.font(22, bold=True), fill=ink)
            x += St.text_w(St.font(22, bold=True), "at least") + px(10)
        big = _join([NB.x1(c["af"]) for c in cells])
        d.text((x, y), big, font=St.font(46 if len(big) < 9 else 38, bold=True), fill=ink)
        y += px(60)
        dn = _join([f"{c['m_new']:.0f}" for c in cells if math.isfinite(c["m_new"])])
        dr = _join([f"{c['m_ref']:.0f}" for c in cells if math.isfinite(c["m_ref"])])
        if dn and dr:
            d.text((x0, y), f"day {dn} against " + ("at least " if kinds == {"at_least"} else "") + f"day {dr}",
                   font=St.font(18), fill=ink)
            y += px(26)
        ci = list(dict.fromkeys(_ci(c) for c in cells))
        if len(ci) > 1 and len({c["hi"] for c in cells}) == 1:      # two intervals with one upper end: said once
            ci = [" and ".join(_ci(c).split(" to ")[0] for c in cells) + " to " + _ci(cells[0]).split(" to ")[1]]
        y = _para(d, x0, y, "95 % interval " + (ci[0] if len(ci) == 1 else " and ".join(ci)), St.font(15), ink2, w,
                  px(21), max_lines=2)
    got = (f"{_join([str(c['hit_new']) for c in cells])} of {nn} against "
           f"{_join([str(c['hit_ref']) for c in cells])} of {nn}")
    y = _para(d, x0, y, f"got there: {got}", St.font(15), ink2, w, px(21), max_lines=2)
    if nn >= 8 and len(cells) == 1:
        d.text((x0, y), f"the automated lab first in {cells[0]['first_new']} of {nn} seeds", font=St.font(15),
               fill=ink2)
        y += px(21)
    if r3:
        rk = {c["kind"] for c in r3}
        if rk <= {"none", "at_most"}:
            txt = "no speed-up" if all(2 * c["hit_ref"] >= c["n"] for c in r3) else "no factor"
        elif rk == {"at_least"}:
            txt = "at least " + _join([NB.x1(c["af"]) for c in r3])
        else:
            txt = _join([_x(c) for c in r3])
        _para(d, x0, y + px(4), f"round 3's pairing (automated lab stocked): {txt}", St.font(14),
              St.mix(bg, St.INK3, k), w, px(19), max_lines=2)


def _lab_like(d, lay, t, ctx=None):
    """Like for like, both labs ordering metal as they go: for each campaign the comparison that leads (BOFN and pKGFN
    against the rule of thumb on aluminium, the funnel in both labs on copper) above the other, to both targets."""
    n = _n()
    like, r3 = n["lab"]["like"], n["lab"]["round3"]
    T = n["targets"]
    rows = {
        AL: [("BOFN and pKGFN against a conventional lab run by rule of thumb", ["BOFN", "pKGFN"],
              ("bofn_thumb", "pkgfn_thumb"), 4.4),
             ("The same policy in both labs: the heuristic (rule of thumb)", ["heuristic"], ("same_heur",), 25.4)],
        CU: [("The same policy in both labs: tiered CALPHAD screening", ["tiered"], ("same_funnel",), 18.4),
             ("BOFN and pKGFN against a conventional lab run by rule of thumb", ["BOFN", "pKGFN"],
              ("bofn_thumb", "pkgfn_thumb"), 25.4)],
    }
    y_top = 196
    for i, camp in enumerate(D.CAMPAIGNS):
        x0 = px(80) + i * px(900)
        x1 = x0 + px(860)
        y0 = px(y_top)
        k = St.ramp(t, 0.3 + 0.5 * i, 1.0 + 0.5 * i)
        if k <= 0:
            continue
        ink, ink2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
        d.rounded_rectangle((x0, y0, x1, y0 + px(610)), radius=px(16), fill=St.SURF + (255,), outline=St.RULE,
                            width=px(1))
        F.swatch(d, x0 + px(24), y0 + px(22), St.mix(St.BG, St.CAMP[camp], k), s=20)
        d.text((x0 + px(56), y0 + px(14)), CAMP_WORD[camp], font=St.font(28, bold=True), fill=ink)
        d.text((x1 - px(24), y0 + px(24)), "both labs ordering metal as they go", font=St.font(17, bold=True),
               fill=ink, anchor="ra")
        cw = px(406)
        for j, tn in enumerate(("T1", "T2")):
            cx = x0 + px(24) + j * cw
            head = "to the best existing alloy's score" if tn == "T1" else "to the halfway target"
            d.text((cx, y0 + px(62)), head, font=St.font(18, bold=True), fill=ink)
            d.text((cx + St.text_w(St.font(18, bold=True), head) + px(10), y0 + px(64)), f"{T[tn][camp]:.2f}",
                   font=St.font(16), fill=ink2)
        for r, (h1, who, keys, t_r) in enumerate(rows[camp]):
            yy = y0 + px(100) + r * px(254)
            kr = St.ramp(t, t_r, t_r + 0.8) * k               # as the voice reaches each row
            inkr = St.mix(St.SURF, St.INK, kr)
            d.line([(x0 + px(24), yy), (x1 - px(24), yy)], fill=St.mix(St.SURF, St.RULE, k), width=px(1))
            d.text((x0 + px(24), yy + px(12)), h1, font=St.font(19, bold=True), fill=inkr)
            for j, tn in enumerate(("T1", "T2")):
                cells = [like[camp][tn][q]["days"] for q in keys if q in like[camp][tn]]
                old = [r3[camp][tn][q]["days"] for q in keys if q in r3[camp][tn]]
                if cells:
                    _cell(d, x0 + px(24) + j * cw, yy + px(48), cw - px(20), who, cells, old, kr)
    kf = St.ramp(t, 3.0, 3.8)
    _para(d, px(80), px(y_top + 626), "Like for like: both labs order metal as each charge needs it. Counts are the "
          "automated lab's 12 one-year runs against the conventional lab's 12 three-year runs. \"At least\": the "
          "conventional lab reached the target in half its runs or fewer, so its median is its last run to get "
          "there. Medians: Kaplan-Meier. Intervals: 95 %, paired bootstrap over seeds. Round 3's pairing set a "
          "stocked automated lab against a conventional lab ordering as it goes: it includes the stock.",
          St.font(17), St.mix(St.BG, St.INK2, kf), px(1760), px(24))


def _dumbbell(d, x0, x1, y, ax_lo, ax_hi, a, b, col, k, bg=St.BG):
    """Two medians on one day axis: stocked (filled) and ordering as it goes (hollow), joined."""
    X = lambda v: x0 + (x1 - x0) * (v - ax_lo) / (ax_hi - ax_lo)
    d.line([(x0, y), (x1, y)], fill=St.mix(bg, St.GRID, k), width=px(1))
    if a is not None and b is not None and math.isfinite(a) and math.isfinite(b):
        d.line([(X(a), y), (X(b), y)], fill=St.mix(bg, col, k), width=px(4))
    ok = [v is not None and math.isfinite(v) for v in (a, b)]
    close = all(ok) and abs(X(a) - X(b)) < px(44)          # the two day labels side by side, not on top of each other
    for v, filled in ((b, False), (a, True)):
        if v is None or not math.isfinite(v):
            continue
        xx = X(v)
        if filled:
            d.ellipse((xx - px(11), y - px(11), xx + px(11), y + px(11)), fill=St.mix(bg, col, k))
        else:
            d.ellipse((xx - px(11), y - px(11), xx + px(11), y + px(11)), fill=bg, outline=St.mix(bg, col, k),
                      width=px(3))
        anchor = "ma" if not close else ("ra" if (v <= min(a, b)) else "la")
        dx = 0 if not close else (px(2) if anchor == "ra" else -px(2))
        d.text((xx + dx, y + px(16)), f"{v:.0f}", font=St.font(15), fill=St.mix(bg, St.INK2, k), anchor=anchor)


def _lab_stock(d, lay, t, ctx=None):
    """What the stock buys: the automated lab against itself, and round 3's pairing as the product of the two."""
    n = _n()
    st = n["stock"]["vertical_lab"]
    like, r3 = n["lab"]["like"], n["lab"]["round3"]
    X0 = px(80)
    d.text((X0, px(196)), "The automated lab against itself: median day to the target", font=St.font(26, bold=True),
           fill=St.INK)
    d.text((X0, px(232)), "filled: stocked on day 0;  hollow: ordering metal as it goes;  12 one-year runs each way, "
           "the same seeds", font=St.font(18), fill=St.INK2)
    rows = [("Aluminium, the halfway target", "BOFN", st["bofn3"][AL]["T2"], AL, True),
            ("", "pKGFN", st["pkgfn3"][AL]["T2"], AL, True),
            ("Aluminium, the best existing alloy", "heuristic", st["heuristic"][AL]["T1"], AL, False),
            ("Copper, the halfway target", "tiered screening", st["tiered"][CU]["T2"], CU, False),
            ("Copper, the best existing alloy", "tiered screening", st["tiered"][CU]["T1"], CU, False)]
    ax0, ax1 = X0 + px(300), X0 + px(640)
    y = px(330)
    for i, (head, pol, rec, camp, lead) in enumerate(rows):
        c = rec["days"]
        k = St.ramp(t, 0.8 + (0.5 * i if lead else 9.0 + 0.5 * i), 1.6 + (0.5 * i if lead else 9.0 + 0.5 * i))
        ink, ink2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
        if head:
            d.text((X0, y - px(34)), head, font=St.font(19, bold=True), fill=ink)
        d.text((X0 + px(16), y), pol, font=St.font(20), fill=ink, anchor="lm")
        _dumbbell(d, ax0, ax1, y, 0.0, 365.0, c["m_new"], c["m_ref"], St.CAMP[camp], k)
        d.text((ax1 + px(30), y - px(4)), _x(c), font=St.font(34 if lead else 26, bold=True), fill=ink, anchor="lm")
        xx = ax1 + px(30) + St.text_w(St.font(34 if lead else 26, bold=True), _x(c)) + px(14)
        d.text((xx, y - px(12)), f"95 % interval {_ci(c)}", font=St.font(15), fill=ink2, anchor="lm")
        d.text((xx, y + px(10)), f"got there: {c['hit_new']} of {c['n']} stocked, {c['hit_ref']} of {c['n']} ordering",
               font=St.font(15), fill=ink2, anchor="lm")
        y += px(80) if not rows[min(i + 1, len(rows) - 1)][0] or i == len(rows) - 1 else px(114)
    for v in (0, 100, 200, 300, 365):
        xx = ax0 + (ax1 - ax0) * v / 365.0
        d.line([(xx, px(272)), (xx, px(278))], fill=St.RULE, width=px(1))
        d.text((xx, px(268)), f"{v}", font=St.font(13), fill=St.INK2, anchor="md")
    d.text((ax0 - px(12), px(268)), "day", font=St.font(13), fill=St.INK2, anchor="rd")
    # ---- right: round 3's pairing is the product of the two
    R0 = px(1290)
    kp = St.ramp(t, 14.2, 15.0)
    ink, ink2 = St.mix(St.BG, St.INK, kp), St.mix(St.BG, St.INK2, kp)
    d.rounded_rectangle((R0, px(196), px(1840), px(780)), radius=px(16), fill=St.mix(St.BG, St.SURF, kp),
                        outline=St.mix(St.BG, St.RULE, kp), width=px(1))
    d.text((R0 + px(24), px(212)), "Round 3's pairing multiplied the two", font=St.font(24, bold=True), fill=ink)
    yy = px(262)
    for camp, pol, lk, s_, old in ((AL, "pKGFN against rule of thumb", like[AL]["T2"]["pkgfn_thumb"]["days"],
                                    st["pkgfn3"][AL]["T2"]["days"], r3[AL]["T2"]["pkgfn_thumb"]["days"]),
                                   (CU, "tiered screening in both labs", like[CU]["T2"]["same_funnel"]["days"],
                                    st["tiered"][CU]["T2"]["days"], r3[CU]["T2"]["same_funnel"]["days"])):
        surf = St.mix(St.BG, St.SURF, kp)
        F.swatch(d, R0 + px(24), yy + px(6), St.mix(surf, St.CAMP[camp], kp), s=16)
        d.text((R0 + px(50), yy), f"{CAMP_WORD[camp]}, the halfway target", font=St.font(19, bold=True), fill=ink)
        d.text((R0 + px(24), yy + px(28)), pol, font=St.font(16), fill=ink2)
        fb = St.font(34, bold=True)
        parts = [(old, "round 3: stocked against", "ordering as it goes"), (None, "=", ""),
                 (lk, "the lab,", "like for like"), (None, "×", ""), (s_, "the stock,", "its own effect")]
        x = R0 + px(24)
        for c, l1, l2 in parts:
            if c is None:
                d.text((x, yy + px(76)), l1, font=fb, fill=ink2)
                x += St.text_w(fb, l1) + px(16)
                continue
            if c["kind"] == "at_least":                          # a lower bound keeps its words
                d.text((x, yy + px(58)), "at least", font=St.font(14, bold=True), fill=ink)
            d.text((x, yy + px(76)), NB.x1(c["af"]), font=fb, fill=ink)
            d.text((x, yy + px(122)), l1, font=St.font(14), fill=ink2)
            d.text((x, yy + px(140)), l2, font=St.font(14), fill=ink2)
            x += max(St.text_w(fb, NB.x1(c["af"])), St.text_w(St.font(14), l1), St.text_w(St.font(14), l2)) + px(16)
        d.text((R0 + px(24), yy + px(168)), f"median days: {old['m_ref']:.0f} / {old['m_new']:.0f} = "
               f"({lk['m_ref']:.0f} / {lk['m_new']:.0f}) × ({s_['m_ref']:.0f} / {s_['m_new']:.0f})",
               font=St.font(15), fill=ink2)
        yy += px(222)
    _para(d, R0 + px(24), yy - px(4), "Aluminium's round-3 factor was mostly the stock. Copper's was mostly the lab.",
          St.font(18, bold=True), ink, px(500), px(26))
    kf = St.ramp(t, 16.0, 16.8)
    b, p = st["bofn3"][AL]["T2"]["best_diff"], st["pkgfn3"][AL]["T2"]["best_diff"]
    _para(d, X0, px(800), "The stock is about a month's metal, bought on day 0 and charged to the campaign. It brings "
          "the first results forward; the final alloy is the same either way (stocked minus ordering as it goes: "
          f"BOFN {b['mean']:+.2f} ± {b['se']:.2f}, pKGFN {p['mean']:+.2f} ± {p['se']:.2f}). It does little for "
          f"copper's tiered screening: {_x(st['tiered'][CU]['T1']['days'])} and "
          f"{_x(st['tiered'][CU]['T2']['days'])} to its two targets.", St.font(18),
          St.mix(St.BG, St.INK2, kf), px(1760), px(26))


def _lab_tie(d, lay, t, ctx=None):
    """Where the automated lab doesn't win, like for like."""
    n = _n()
    like, both = n["lab"]["like"], n["lab"]["stocked"]
    A = n["arms"]
    X0 = px(80)
    # ---- the same optimizer in both labs: aluminium's halfway target
    k = St.ramp(t, 4.4, 5.2)
    surf = St.mix(St.BG, St.SURF, k)
    ink, ink2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
    d.rounded_rectangle((X0, px(196), px(1840), px(520)), radius=px(16), fill=surf, outline=St.mix(St.BG, St.RULE, k),
                        width=px(1))
    F.swatch(d, X0 + px(24), px(218), St.mix(surf, St.CAMP[AL], k), s=20)
    d.text((X0 + px(56), px(210)), "Aluminium's halfway target: the same optimizer in both labs, both ordering metal "
           "as they go", font=St.font(24, bold=True), fill=ink)
    d.text((px(1816), px(262)), "about a tie", font=St.font(40, bold=True), fill=ink, anchor="ra")
    d.text((px(1816), px(312)), "4 seeds; intervals include 1.0", font=St.font(17), fill=ink2, anchor="ra")
    for j, (nm, key, t0) in enumerate((("BOFN, time-aware, in both labs", "bofn_same", 12.4),
                                       ("pKGFN, time-aware, in both labs", "pkgfn_same", 14.4))):
        c = like[AL]["T2"][key]["days"]
        kk = St.ramp(t, t0, t0 + 0.8) * k
        i1, i2 = St.mix(surf, St.INK, kk), St.mix(surf, St.INK2, kk)
        x = X0 + px(40) + j * px(640)
        d.text((x, px(262)), nm, font=St.font(19, bold=True), fill=i1)
        d.text((x, px(296)), NB.x1(c["af"]), font=St.font(64, bold=True), fill=i1)
        xx = x + St.text_w(St.font(64, bold=True), NB.x1(c["af"])) + px(20)
        d.text((xx, px(310)), f"95 % interval {_ci(c)}", font=St.font(17), fill=i2)
        d.text((xx, px(336)), f"{_day(c['m_new'])} against {_day(c['m_ref'])}", font=St.font(17), fill=i1)
        d.text((x, px(388)), f"seeds that got there: {c['hit_new']} of {c['n']} in the automated lab's year, "
               f"{c['hit_ref']} of {c['n']}", font=St.font(16), fill=i2)
        d.text((x, px(410)), f"in the conventional lab's three years; the automated lab first in {c['first_new']} of "
               f"{c['n']}", font=St.font(16), fill=i2)
    bs, ps = both[AL]["T2"]["bofn_same"]["days"], both[AL]["T2"]["pkgfn_same"]["days"]
    d.text((X0 + px(40), px(462)), f"With both labs stocked instead: {NB.x1(bs['af'])} ({_ci(bs)}) for BOFN and "
           f"{NB.x1(ps['af'])} ({_ci(ps)}) for pKGFN: ahead, with intervals that reach below 1.",
           font=St.font(17), fill=St.mix(surf, St.INK2, St.ramp(t, 16.5, 17.3) * k))
    # ---- copper's best existing alloy, the same seeds
    k2 = St.ramp(t, 17.6, 18.4)
    surf = St.mix(St.BG, St.SURF, k2)
    ink, ink2 = St.mix(St.BG, St.INK, k2), St.mix(St.BG, St.INK2, k2)
    d.rounded_rectangle((X0, px(540), px(950), px(820)), radius=px(16), fill=surf, outline=St.mix(St.BG, St.RULE, k2),
                        width=px(1))
    F.swatch(d, X0 + px(24), px(562), St.mix(surf, St.CAMP[CU], k2), s=20)
    d.text((X0 + px(56), px(554)), "Copper's best existing alloy, in those seeds", font=St.font(24, bold=True),
           fill=ink)
    d.text((X0 + px(24), px(592)), "the best existing alloy on this synthetic benchmark; seeds that got there, the "
           "automated lab's", font=St.font(16), fill=ink2)
    d.text((X0 + px(24), px(613)), "year against the conventional lab's three years", font=St.font(16), fill=ink2)
    for j, (nm, key) in enumerate((("BOFN in both labs", "bofn_same"), ("pKGFN in both labs", "pkgfn_same"))):
        c = like[CU]["T1"][key]["days"]
        x = X0 + px(40) + j * px(430)
        d.text((x, px(640)), nm, font=St.font(19, bold=True), fill=ink)
        d.text((x, px(672)), f"{c['hit_new']} of {c['n']}", font=St.font(52, bold=True), fill=ink)
        xx = x + St.text_w(St.font(52, bold=True), f"{c['hit_new']} of {c['n']}") + px(16)
        d.text((xx, px(694)), f"against {c['hit_ref']} of {c['n']}", font=St.font(26, bold=True), fill=ink)
        d.text((x, px(750)), f"the conventional lab first in {c['first_ref']} of {c['n']}", font=St.font(16),
               fill=ink2)
    # ---- aluminium's first target against a stocked conventional lab
    k3 = St.ramp(t, 20.0, 20.8)
    surf = St.mix(St.BG, St.SURF, k3)
    ink, ink2 = St.mix(St.BG, St.INK, k3), St.mix(St.BG, St.INK2, k3)
    d.rounded_rectangle((px(970), px(540), px(1840), px(820)), radius=px(16), fill=surf,
                        outline=St.mix(St.BG, St.RULE, k3), width=px(1))
    F.swatch(d, px(994), px(562), St.mix(surf, St.CAMP[AL], k3), s=20)
    d.text((px(1026), px(554)), "Aluminium's best existing alloy, against a stocked lab", font=St.font(24, bold=True),
           fill=ink)
    ch = A["proposed|stocked|heuristic"][AL]["T1"]
    lean = {p: A[f"vertical_lab|lean|{p}"][AL]["T1"] for p in ("heuristic", "bofn3", "pkgfn3")}
    d.text((px(994), px(604)), _day(ch["day"]), font=St.font(52, bold=True), fill=ink)
    xx = px(994) + St.text_w(St.font(52, bold=True), _day(ch["day"])) + px(18)
    d.text((xx, px(612)), "a stocked conventional lab", font=St.font(18), fill=ink)
    d.text((xx, px(638)), f"run by rule of thumb ({ch['hit']} of {ch['n']} runs)", font=St.font(18), fill=ink)
    _para(d, px(994), px(686), "Sooner than the automated lab ordering metal as it goes with any policy: "
          f"{_day(lean['heuristic']['day'])} for the heuristic, {_day(lean['bofn3']['day'])} for BOFN, "
          f"{_day(lean['pkgfn3']['day'])} for pKGFN. The best existing alloy on this synthetic benchmark is a low "
          f"bar: one random design in {n['targets']['one_in']} beats it.", St.font(17), ink2, px(820), px(25),
          max_lines=4)
    kf = St.ramp(t, 21.5, 22.3)
    _para(d, X0, px(840), "BOFN and pKGFN ran in the conventional lab on 4 seeds, three simulated years each, so these "
          "comparisons rest on 4 pairs. Three years' money also gives the conventional lab a first-day release "
          "three times the automated lab's, which helps it early when metal is ordered as it goes "
          "(notes/twin_round3b.md, 2.6).", St.font(17), St.mix(St.BG, St.INK2, kf), px(1760), px(24))


def _lab_cost(d, lay, t, ctx=None):
    """The cost on one basis, campaign spend to the target, like for like; and what that basis leaves out."""
    n = _n()
    like = n["lab"]["like"]
    X0 = px(80)
    d.text((X0, px(196)), "Campaign spend to the target, both labs ordering metal as they go",
           font=St.font(26, bold=True), fill=St.INK)
    d.text((X0, px(234)), "the conventional lab's median spend over the automated lab's on the day each first got "
           "there; right of 1.0, the automated lab spent less", font=St.font(18), fill=St.INK2)
    rows = [("Aluminium, halfway target", "BOFN against rule of thumb", like[AL]["T2"]["bofn_thumb"]["usd"], AL, 8.6),
            ("", "pKGFN against rule of thumb", like[AL]["T2"]["pkgfn_thumb"]["usd"], AL, 8.6),
            ("Copper, halfway target", "tiered screening in both labs", like[CU]["T2"]["same_funnel"]["usd"], CU,
             13.8),
            ("Aluminium, halfway target (4 seeds)", "BOFN in both labs", like[AL]["T2"]["bofn_same"]["usd"], AL, 17.4),
            ("", "pKGFN in both labs", like[AL]["T2"]["pkgfn_same"]["usd"], AL, 17.4),
            ("Copper, best existing alloy (4 seeds)", "BOFN in both labs", like[CU]["T1"]["bofn_same"]["usd"], CU,
             18.4),
            ("", "pKGFN in both labs", like[CU]["T1"]["pkgfn_same"]["usd"], CU, 18.4)]
    ax = F.Ax((X0 + px(560), px(292), X0 + px(1010), px(800)), (0.0, 5.0), (0, 1), "u", "u")
    for v in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0):
        xx = ax.X(v)
        d.line([(xx, ax.y0), (xx, ax.y1)], fill=St.RULE if v == 1.0 else St.GRID, width=px(2) if v == 1.0 else 1)
        d.text((xx, ax.y1 + px(8)), f"{v:.0f}x", font=St.font(16), fill=St.INK2, anchor="ma")
    y = ax.y0 + px(34)
    for i, (head, pol, c, camp, t0) in enumerate(rows):
        k = St.ramp(t, t0, t0 + 0.8)
        ink, ink2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
        col = St.mix(St.BG, St.CAMP[camp], k)
        if head:
            d.text((X0, y - px(30)), head, font=St.font(18, bold=True), fill=ink)
        d.text((X0 + px(16), y), pol, font=St.font(18), fill=ink, anchor="lm")
        lo = c["lo"] if math.isfinite(c["lo"]) else 0.0
        hi = c["hi"] if math.isfinite(c["hi"]) else None
        xa, xb = ax.X(max(lo, 0.0)), ax.X(min(hi, 5.0)) if hi is not None else ax.x1 + px(14)
        d.line([(xa, y), (xb, y)], fill=col, width=px(4))
        if hi is None or hi > 5.0:                               # the interval runs off the scale: an arrow head
            d.polygon([(xb, y - px(7)), (xb + px(12), y), (xb, y + px(7))], fill=col)
        d.ellipse((ax.X(c["af"]) - px(10), y - px(10), ax.X(c["af"]) + px(10), y + px(10)), fill=col)
        xt = ax.x1 + px(44)
        d.text((xt, y - px(1)), _x(c), font=St.font(24, bold=True), fill=ink, anchor="lm")
        xx = xt + St.text_w(St.font(24, bold=True), _x(c)) + px(12)
        spend = (f"{St.money(c['m_new'])} against {St.money(c['m_ref'])}" if math.isfinite(c["m_new"]) and
                 math.isfinite(c["m_ref"]) else "")
        d.text((xx, y - px(11)), f"95 % interval {_ci(c)}; {NB.counts(c)} runs", font=St.font(14), fill=ink2,
               anchor="lm")
        d.text((xx, y + px(9)), spend, font=St.font(14), fill=ink2, anchor="lm")
        y += px(58) if (i + 1 < len(rows) and not rows[i + 1][0]) else px(92)
    # ---- what this basis leaves out
    ko = St.ramp(t, 20.6, 21.4)
    surf = St.mix(St.BG, St.SURF, ko)
    ink, ink2 = St.mix(St.BG, St.INK, ko), St.mix(St.BG, St.INK2, ko)
    d.rounded_rectangle((X0, px(908), px(1840), px(1026)), radius=px(16), fill=surf,
                        outline=St.mix(St.BG, St.RULE, ko), width=px(1))
    d.text((X0 + px(24), px(920)), "Left out of this basis: fixed costs", font=St.font(24, bold=True), fill=ink)
    fy, K = n["cost"]["fixed_year"], n["cost"]["per_alloy"]
    _para(d, X0 + px(24), px(958), "Staff, equipment and the building. Round 3 put them at "
          f"{St.money(fy['vertical'])} a year for the automated lab against {St.money(fy['conventional'])} for the "
          "conventional lab, and a demonstrated alloy at "
          f"{St.money(K['both|vertical lab, campaigns only, with capex'])} against "
          f"{St.money(K['both|conventional, with capex'])} with the equipment included: on every basis that carries "
          "them, the automated lab costs more per alloy. Round 3b did not redo that model for its new arms.",
          St.font(17), ink2, px(1700), px(25), max_lines=3)
    kf = St.ramp(t, 3.0, 3.8)
    _para(d, X0, px(846), "Campaign spend: the metal, consumables and outside services the campaign had paid for on the "
          "day it first reached the target. \"At least\": the conventional lab got there in half its runs or fewer; "
          "\"at most\": the automated lab did. Much of the saving is time: a campaign spends as it goes.",
          St.font(17), St.mix(St.BG, St.INK2, kf), px(1760), px(24))


# ==================================================================================================== takeaway
def takeaway_frame(t: float) -> np.ndarray:
    n = _n()
    M = n["main"]
    like, st = n["lab"]["like"], n["stock"]["vertical_lab"]
    A = n["arms"]
    c1, c2, c3 = cue("take1", 1.0), cue("take2", 20.6), cue("take3", 45.4)
    im, d = _new()
    d.text((W / 2, px(34)), "In this simulated benchmark", font=St.font(40, bold=True), fill=_ink(t, 0.2), anchor="ma")
    # ---- what the policies found
    for i, camp in enumerate(D.CAMPAIGNS):
        cx = W / 2 + (i - 0.5) * px(900)
        y0 = px(100)
        k = St.ramp(t, c1 + 0.3 + (11.5 if i else 0.0), c1 + 1.1 + (11.5 if i else 0.0))
        ink, ink2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
        d.rounded_rectangle((cx - px(430), y0, cx + px(430), y0 + px(252)), radius=px(18),
                            fill=St.mix(St.BG, St.SURF, k), outline=St.mix(St.BG, St.CAMP[camp], k), width=px(3))
        d.text((cx - px(400), y0 + px(16)), CAMP_WORD[camp], font=St.font(30, bold=True), fill=ink)
        if camp == AL:
            b, p, h = M["bofn3"][AL], M["pkgfn3"][AL], M["heuristic"][AL]
            lb, lp = A["vertical_lab|lean|bofn3"][AL]["T2"], A["vertical_lab|lean|pkgfn3"][AL]["T2"]
            head = "BOFN and pKGFN reached the halfway target in about three months stocked, six ordering as they go"
            both = (f"day {lb['day']:.0f} for both, in {lb['hit']} of 12" if round(lb["day"]) == round(lp["day"])
                    and lb["hit"] == lp["hit"] else f"day {lb['day']:.0f} and day {lp['day']:.0f}, in {lb['hit']} "
                    f"and {lp['hit']} of 12")
            body = (f"Stocked on day 0: day {b['T2']['day']:.0f} and day {p['T2']['day']:.0f}, in {b['T2']['hit']} "
                    f"and {p['T2']['hit']} of 12 runs. Ordering metal as they go: {both}. The heuristic reached the "
                    f"best existing alloy's score first (day {h['T1']['day']:.0f}, stocked) and then stalled.")
        else:
            f_, b, p = M["tiered"][CU], M["bofn3"][CU], M["pkgfn3"][CU]
            head = "Tiered CALPHAD screening still won; money, not capacity, was the limit"
            body = (f"It finished at {f_['best']:.2f} against {b['best']:.2f} and {p['best']:.2f} for BOFN and "
                    f"pKGFN, and reached the halfway target on day {f_['T2']['day']:.0f} in {f_['T2']['hit']} of 12 "
                    "runs (stocked). With three times the money, BOFN and pKGFN drew level on the final alloy.")
        yy = _para(d, cx - px(400), y0 + px(60), head, St.font(22, bold=True), ink, px(800), px(30), max_lines=2)
        _para(d, cx - px(400), yy + px(8), body, St.font(18), ink2, px(800), px(26), max_lines=4)
    # ---- against a conventional lab, like for like; the stock; the tie
    k2 = St.ramp(t, c2 + 0.2, c2 + 1.0)
    surf = St.mix(St.BG, St.SURF, k2)
    ink, ink2 = St.mix(St.BG, St.INK, k2), St.mix(St.BG, St.INK2, k2)
    y0 = px(372)
    d.rounded_rectangle((px(80), y0, px(1840), y0 + px(330)), radius=px(18), fill=surf,
                        outline=St.mix(St.BG, St.RULE, k2), width=px(2))
    d.text((px(110), y0 + px(14)), "Against a conventional lab, like for like: both ordering metal as they go",
           font=St.font(28, bold=True), fill=ink)
    d.text((px(110), y0 + px(54)), "to the halfway target; the automated lab's one-year runs against the "
           "conventional lab's three-year runs", font=St.font(18), fill=ink2)
    al = [like[AL]["T2"][q]["days"] for q in ("bofn_thumb", "pkgfn_thumb")]
    cu = like[CU]["T2"]["same_funnel"]["days"]
    rows = [(AL, "at least " + _join([NB.x1(c["af"]) for c in al]) + " sooner", "",
             f"BOFN and pKGFN against a lab run by rule of thumb: {_join([NB.counts(c) for c in al])} runs got there",
             4.6),
            (CU, f"{NB.x1(cu['af'])} sooner", f"95 % interval {_ci(cu)}",
             f"tiered screening in both labs: {NB.counts(cu)} runs got there", 10.6)]
    for r, (camp, big, ci, small, t0) in enumerate(rows):
        yy = y0 + px(96) + r * px(112)
        kk = St.ramp(t, c2 + t0, c2 + t0 + 0.8) * k2
        d.line([(px(110), yy - px(6)), (px(800), yy - px(6))], fill=St.mix(surf, St.RULE, k2), width=px(1))
        F.swatch(d, px(110), yy + px(14), St.mix(surf, St.CAMP[camp], k2), s=16)
        d.text((px(136), yy + px(8)), CAMP_WORD[camp], font=St.font(21, bold=True), fill=ink)
        fb = St.font(34, bold=True)
        d.text((px(300), yy), big, font=fb, fill=St.mix(surf, St.INK, kk))
        if ci:
            d.text((px(300) + St.text_w(fb, big) + px(14), yy + px(14)), ci, font=St.font(16),
                   fill=St.mix(surf, St.INK2, kk))
        _para(d, px(300), yy + px(50), small, St.font(15), St.mix(surf, St.INK2, kk), px(490), px(21), max_lines=2)
    sb, sp = st["bofn3"][AL]["T2"]["days"], st["pkgfn3"][AL]["T2"]["days"]
    r3 = n["lab"]["round3"][AL]["T2"]["pkgfn_thumb"]["days"]
    ks = St.ramp(t, c2 + 14.4, c2 + 15.2) * k2
    x = px(850)
    d.line([(x - px(26), y0 + px(96)), (x - px(26), y0 + px(310))], fill=St.mix(surf, St.RULE, k2), width=px(1))
    d.text((x, y0 + px(92)), "The stock: its own effect", font=St.font(22, bold=True), fill=St.mix(surf, St.INK, ks))
    d.text((x, y0 + px(130)), f"{NB.x1(sb['af'])} to {NB.x1(sp['af'])}", font=St.font(34, bold=True),
           fill=St.mix(surf, St.INK, ks))
    _para(d, x, y0 + px(182), "sooner to aluminium's halfway target for BOFN and pKGFN in the automated lab, stocked "
          f"against ordering as they go. Round 3's {NB.x1(r3['af'])} was the lab's "
          f"{NB.x1(like[AL]['T2']['pkgfn_thumb']['days']['af'])} times the stock's {NB.x1(sp['af'])}.", St.font(16),
          St.mix(surf, St.INK2, ks), px(440), px(23), max_lines=5)
    bs, ps = like[AL]["T2"]["bofn_same"]["days"], like[AL]["T2"]["pkgfn_same"]["days"]
    kt = St.ramp(t, c2 + 19.0, c2 + 19.8) * k2
    x = px(1360)
    d.line([(x - px(26), y0 + px(96)), (x - px(26), y0 + px(310))], fill=St.mix(surf, St.RULE, k2), width=px(1))
    d.text((x, y0 + px(92)), "Where it doesn't win", font=St.font(22, bold=True), fill=St.mix(surf, St.INK, kt))
    d.text((x, y0 + px(130)), "about a tie", font=St.font(34, bold=True), fill=St.mix(surf, St.INK, kt))
    _para(d, x, y0 + px(182), "against the same optimizer in a conventional lab, both ordering as they go: "
          f"{NB.x1(bs['af'])} (BOFN) and {NB.x1(ps['af'])} (pKGFN) to aluminium's halfway target, on {bs['n']} "
          "seeds.", St.font(16), St.mix(surf, St.INK2, kt), px(450), px(23), max_lines=5)
    # ---- the cost, one basis
    k3 = St.ramp(t, c3 + 0.2, c3 + 1.0)
    ink, ink2 = St.mix(St.BG, St.INK, k3), St.mix(St.BG, St.INK2, k3)
    y0 = px(722)
    d.rounded_rectangle((px(80), y0, px(1840), y0 + px(166)), radius=px(18), fill=St.mix(St.BG, St.SURF, k3),
                        outline=St.mix(St.BG, St.RULE, k3), width=px(2))
    d.text((px(110), y0 + px(14)), "Cost: campaign spend to the halfway target, fixed costs left out",
           font=St.font(28, bold=True), fill=ink)
    d.text((px(110), y0 + px(54)), "both labs ordering metal as they go; the conventional lab's median spend over the "
           "automated lab's", font=St.font(18), fill=ink2)
    ub, uf = like[AL]["T2"]["bofn_thumb"]["usd"], like[CU]["T2"]["same_funnel"]["usd"]
    for j, (camp, c, who) in enumerate(((AL, ub, "BOFN against rule of thumb"), (CU, uf, "tiered screening in both"))):
        x = px(110) + j * px(640)
        fb = St.font(40, bold=True)
        d.text((x, y0 + px(88)), _x(c), font=fb, fill=ink)
        xx = x + St.text_w(fb, _x(c)) + px(14)
        d.text((xx, y0 + px(94)), f"less, {CAMP_WORD[camp].lower()}", font=St.font(19, bold=True), fill=ink)
        d.text((xx, y0 + px(120)), who, font=St.font(15), fill=ink2)
        d.text((xx, y0 + px(140)), f"95 % interval {_ci(c)}", font=St.font(15), fill=ink2)
    fy = n["cost"]["fixed_year"]
    _para(d, px(1290), y0 + px(66), "Left out: staff, equipment and the building, where round 3 found the automated "
          f"lab costs more ({St.money(fy['vertical'])} a year against {St.money(fy['conventional'])}). Against the "
          "same optimizer, the spend was about the same, or more.", St.font(16), ink2, px(520), px(23), max_lines=4)
    # ---- what the target is
    kf = St.ramp(t, 2.0, 2.8)
    T = n["targets"]
    _para(d, W / 2, px(906), f"The first target is the best existing alloy on this synthetic benchmark "
          f"({T['ref'][AL]} {T['T1'][AL]:.2f}, {T['ref'][CU]} {T['T1'][CU]:.2f}): one random design in "
          f"{T['one_in']} beats it. The halfway target ({T['T2'][AL]:.2f}, {T['T2'][CU]:.2f}) is halfway from there "
          "to the best alloy the twin's own search found.", St.font(18), St.mix(St.BG, St.INK2, kf), px(1720),
          px(26), anchor="ma", max_lines=2)
    d.text((W / 2, px(980)), "Simulated campaigns in a digital twin: not lab results. 12 runs per arm; 4 for BOFN and "
           "pKGFN in the conventional lab.", font=St.font(21, bold=True), fill=St.mix(St.BG, St.INK, kf), anchor="ma")
    return np.asarray(im)


# ====================================================================================================== stills
if __name__ == "__main__":                                  # python -m twin.video.figs3b [part ...] -> /tmp/vid/
    import sys
    from pathlib import Path
    out = Path("/tmp/vid")
    out.mkdir(parents=True, exist_ok=True)
    which = sys.argv[1:] or ["changes", "explain", "results", "labs", "takeaway"]
    T, TL = res_t(), labs_t()
    jobs = dict(changes=(changes_frame, (10, CHANGES_DURATION - 2)),
                explain=(explain_frame, (12, cue("fig3", 22.4) + 9, cue("fig4", 34.5) + 20, cue("fig5", 57.3) + 8,
                                         EXPLAIN_DURATION - 1.5)),
                assume=(assume_frame, (ASSUME_DURATION - 2,)),
                results=(results_frame, tuple(T[i + 1] - 1.5 for i in range(3))),
                labs=(labs_frame, tuple(TL[i + 1] - 1.2 for i in range(4)) + (TL[0] + 10.0, TL[1] + 6.0)),
                takeaway=(takeaway_frame, (cue("take2", 20.6) - 1, cue("take3", 45.4) - 1, TAKEAWAY_DURATION - 1.5)))
    for name in which:
        fn, ts = jobs[name]
        for tt in ts:
            Image.fromarray(fn(float(tt))).save(out / f"r3b_{name}_{float(tt):05.1f}.png")
            print(name, tt, flush=True)
