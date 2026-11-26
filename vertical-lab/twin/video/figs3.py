"""Round 3's cards (TWIN_VIDEO_ROUND=3): what changed in the twin, how to read the figures, the atomizer's assumptions
against the lab's record, the results and the takeaway, drawn with PIL frame by frame like figs_anim's.

    changes_frame(t), CHANGES_DURATION       what round 3 changed in the twin
    explain_frame(t), EXPLAIN_DURATION       best new alloy so far, the two targets, the conventional lab's curve, and
                                             how a lab-against-lab factor is read off (and when it is a lower bound)
    assume_frame(t), ASSUME_DURATION         the twin's atomizer against the lab's own record: design targets
    results_frame(t), RESULTS_DURATION       five parts: the curves, days to both targets, copper and money, the lab
                                             against a conventional lab, the cost on one basis
    takeaway_frame(t), TAKEAWAY_DURATION     the takeaway

Every number comes from numbers3.numbers() (round 3's committed summaries); nothing is typed in here. The cards follow
DAL's audit of round 2's video (digital-alloy-lab PR 293, audits/twin-round2-video/README.md): a lab-against-lab
factor is never the headline, each says which lab is stocked and which orders as it goes, a factor whose conventional
arm reached the target in half its runs or fewer is "at least", every factor carries its run counts, the same-policy
comparison sits beside the one against a conventional lab run by rule of thumb, the cost has one stated basis per
card, and the first target is called what it is, with the halfway target shown beside it.

Each part appears when the narration reaches it: the cue times are the lines' `at` in narration3.json.
"""
from __future__ import annotations

import json
import math

import numpy as np
from PIL import Image, ImageDraw

from . import data as D
from . import figs_anim as F
from . import numbers3 as N3
from . import style as St
from .style import px

W, H = St.W, St.H
SCRIPT = D.HERE / "twin" / "video" / "narration3.json"
CHANGES_DURATION = 22.0
EXPLAIN_DURATION = 68.0
ASSUME_DURATION = 24.5
RESULTS_DURATION = 141.0
TAKEAWAY_DURATION = 58.0
POLS = ["bofn3", "pkgfn3", "bofn3_usd", "tiered", "heuristic", "gpbo", "sobol", "random"]      # the tables' order
POL = {"bofn3": "BOFN, time-aware", "pkgfn3": "pKGFN, time-aware", "bofn3_usd": "BOFN, per dollar",
       "tiered": "tiered CALPHAD screening", "heuristic": "heuristic (rule of thumb)", "gpbo": "GP-BO",
       "sobol": "Sobol", "random": "random"}
CAMP_WORD = {"flaime_al": "Aluminium", "onr_cu": "Copper"}
_CUE: dict = {}


def cue(line_id: str, default: float = 0.0) -> float:
    """Seconds into its segment at which a narration line starts (narration3.json), so a card's parts follow the
    voice."""
    if not _CUE:
        try:
            for ln in json.loads(SCRIPT.read_text())["lines"]:
                if "at" in ln:
                    _CUE[ln["id"]] = float(ln["at"])
        except Exception:                               # noqa: BLE001
            _CUE["_"] = 0.0
    return _CUE.get(line_id, default)


def _n() -> dict:
    return N3.numbers()


def _ink(t, t0, col=St.INK, bg=St.BG, dur=0.7):
    return St.mix(bg, col, St.ramp(t, t0, t0 + dur))


def _para(d, x, y, text, f, fill, width, lh, anchor="la", max_lines=None) -> float:
    """Wrapped text from (x, y); returns the y under it."""
    lines = St.wrap(text, f, width)
    if max_lines:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=f, fill=fill, anchor=anchor)
    return y + len(lines) * lh


def _d(v) -> str:
    return f"day {v:.0f}"


def _new() -> tuple:
    im = Image.new("RGB", (W, H), St.BG)
    return im, ImageDraw.Draw(im)


def _title(d, text, sub=None, t=99.0):
    d.text((px(80), px(44)), text, font=St.font(44, bold=True), fill=St.INK)
    if sub:
        _para(d, px(80), px(112), sub, St.font(26), _ink(t, 0.2, St.INK2), px(1760), px(36), max_lines=2)


# ===================================================================================== what changed in round 3
def _changes() -> list:
    return [
        ("No cap on work in flight",
         "Round 2 capped each campaign's actions in flight (24 for aluminium, 8 for copper). Round 3 books what is "
         "physical: each station, the two mobile robots, the technician, furnace and immersion positions."),
        ("Decisions every simulated hour",
         "A ranked list of actions across every step of every part, with a model of the work already running."),
        ("One spending plan for every policy",
         "The stocked lab's day-0 inventory first, then the rest of the money paced over the year."),
        ("Interim readings on the 30-day immersion",
         "On days 1, 3, 7 and 14, and a stop action: a coupon that can't pay gives its position back."),
        ("pKGFN, and a time-aware rule",
         "The knowledge gradient of the next step for its cost; BOFN and pKGFN can count bottleneck hours in "
         "place of dollars."),
        ("A scoring bug fixed",
         "Round 2 scored some copper alloys before their 30-day immersion had finished. Round 3 waits for both "
         "results."),
    ]


def changes_frame(t: float) -> np.ndarray:
    im, d = _new()
    _title(d, "Round 3: what changed in the twin", "The same two campaigns and the same lab design as round 2's "
           "video. Everything is simulated.", t)
    y = px(206)
    for i, (head, body) in enumerate(_changes()):
        t0 = 0.6 + 2.6 * i
        k = St.ramp(t, t0, t0 + 0.7)
        d.rounded_rectangle((px(80), y + px(8), px(96), y + px(24)), radius=px(4),
                            fill=St.mix(St.BG, St.CAMP["flaime_al"] if i % 2 == 0 else St.CAMP["onr_cu"], k))
        d.text((px(116), y), head, font=St.font(30, bold=True), fill=St.mix(St.BG, St.INK, k))
        yy = _para(d, px(116), y + px(44), body, St.font(23), St.mix(St.BG, St.INK2, k), px(1700), px(32))
        y = max(yy + px(26), y + px(132))
    return np.asarray(im)


# ============================================================================================== the explainer
EX_L = (190, 262, 890, 742)
EX_R = (1010, 262, 1840, 742)


def explain_caps() -> list:
    n = _n()
    c = "flaime_al"
    T1, T2 = n["targets"]["T1"][c], n["targets"]["T2"][c]
    cell = n["labs"][c]["thumb"]["T2"]
    c2, c3, c4, c5 = (cue(k, v) for k, v in (("fig2", 15.2), ("fig3", 22.4), ("fig4", 34.5), ("fig5", 57.5)))
    big, _ = N3.cell_words(cell)
    return [
        (0.0, c2 - 0.4, f"Best new alloy so far: the highest utility of any new alloy tested yet. First dotted line: "
                        f"the best existing alloy on this synthetic benchmark ({n['targets']['ref'][c]}, {T1:.2f}). "
                        f"One random design in {n['targets']['one_in']} beats it: a low bar."),
        (c2 - 0.4, c3 - 0.4, f"The halfway target ({T2:.2f}): halfway from the best existing alloy to the best alloy "
                             "the twin's own search found."),
        (c3 - 0.4, c4 - 0.4, "Grey, dashed: a conventional lab run by rule of thumb, through partner and core "
                             "facilities, ordering its metal as it goes. The automated lab starts stocked."),
        (c4 - 0.4, c5 - 0.4, f"Days to a target: the median over 12 runs. Halfway target: {_d(cell['day_new'])} "
                             f"automated ({cell['hit_new']} of 12 runs), {_d(cell['day_ref'])} conventional "
                             f"({cell['hit_ref']} of 12). So the factor is a lower bound: {big}."),
        (c5 - 0.4, EXPLAIN_DURATION, "Both labs ordering metal as they go was not run in round 3, so how much of a "
                                     "factor is the stock on the shelf is not known."),
    ]


def explain_frame(t: float, captions: bool = True) -> np.ndarray:
    n = _n()
    ctx = F.context()
    camp = "flaime_al"
    col = St.CAMP[camp]
    T1, T2 = n["targets"]["T1"][camp], n["targets"]["T2"][camp]
    lab = n["labs"][camp]["thumb"]
    cell = lab["T2"]
    am, bm = ctx.auto_mean.get(camp), ctx.base.get(camp)
    caps = explain_caps()
    c2, c3, c4, c5 = caps[1][0], caps[2][0], caps[3][0], caps[4][0]
    im, d = _new()
    if captions:
        F._header(d, "The figures we track", caps, t, total=EXPLAIN_DURATION)
    else:
        d.text((px(80), px(44)), "The figures we track", font=St.font(44, bold=True), fill=St.INK)
    # ------------------------------------------------------------------------------------ left: the curves
    Hd = 365.0
    ymax = 0.8
    ax = F.Ax(F._box(EX_L), (0.0, Hd), (0.0, ymax), "days", "u")
    ax.frame(d, fs=18, nx=5, ny=4, xlabel="days since the start (the first year of both labs)",
             ylabel="utility of the best new alloy so far", fs_label=20)
    sweep = Hd * St.ease((t - 1.0) / 6.0)
    k1 = St.ramp(t, 5.2, 6.0)                            # the first target
    k2 = St.ramp(t, c2 + 0.3, c2 + 1.1)                  # the halfway target
    kb = St.ramp(t, c3 + 0.3, c3 + 5.0)                  # the conventional lab
    if k1 > 0:
        ax.dotted_h(d, T1, St.mix(St.BG, St.TARGET, k1), r=px(2.2), gap=px(10))
    if k2 > 0:
        ax.dotted_h(d, T2, St.mix(St.BG, St.TARGET, k2), r=px(2.2), gap=px(10))
    if bm is not None and kb > 0:
        F._mean_line(ax, d, ctx.day_grid, bm["mean"], Hd * kb, St.BASE, px(3), dashed=True)
    if am is not None:
        F._mean_line(ax, d, ctx.day_grid, am["mean"], sweep, col, px(3))
        if t < 7.0:
            ax.dot(d, sweep, float(np.interp(sweep, ctx.day_grid, am["mean"])), col, r=6)
    if k1 > 0:
        F.label_box(d, (ax.x1 - px(8), ax.Y(T1) + px(10)), f"the best existing alloy: {T1:.2f}",
                    St.font(18, bold=True), St.mix(St.BG, St.INK, k1), anchor="ra", pad=px(4))
    if k2 > 0:
        F.label_box(d, (ax.x1 - px(8), ax.Y(T2) - px(12)), f"halfway target: {T2:.2f}", St.font(18, bold=True),
                    St.mix(St.BG, St.INK, k2), anchor="rd", pad=px(4))
    ke = St.ramp(t, c4 + 3.0, c4 + 4.0)                  # the read-off at the halfway target
    if ke > 0:
        y = ax.Y(T2)
        for v, cc in ((cell["day_new"], col), (cell["day_ref"], St.BASE)):
            if v is not None and math.isfinite(v) and v <= Hd:
                x = ax.X(v)
                d.line([(x, y), (x, ax.y1)], fill=St.mix(St.BG, cc, ke), width=px(2))
                d.ellipse((x - px(7), y - px(7), x + px(7), y + px(7)), fill=St.mix(St.BG, cc, ke),
                          outline=St.mix(St.BG, St.INK, ke), width=px(2))
                F.label_box(d, (x, ax.y1 - px(34)), f"{v:.0f}", St.font(18, bold=True), St.mix(St.BG, St.INK, ke),
                            anchor="ma", pad=px(3))
    # legend, bottom right (the docked networks keep the bottom left)
    lx, ly = px(900), px(905)
    na = am["n"] if am else 0
    x = F.legend_line(d, lx, ly, "solid", col, f"automated lab, pKGFN (mean of {na} one-year runs)", fs=19, w=40)
    if kb > 0 and bm is not None:
        F.legend_line(d, lx, ly + px(36), "dashed", St.BASE, f"conventional lab, rule of thumb (mean of {bm['n']} "
                      "three-year runs)", fs=19, w=40)
    if k1 > 0:
        F.legend_line(d, lx, ly + px(72), "dotted", St.TARGET, "the two targets", fs=19, w=40)
    # ------------------------------------------------------------------------------------ right: the panel
    kt = min(St.ramp(t, 5.2, 6.0), 1.0 - St.ramp(t, c4 - 0.4, c4 + 0.3))          # the targets, for both campaigns
    ks = St.ramp(t, c4 + 0.3, c4 + 1.1)                                          # each run's day, as marks
    if kt > 0.003:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        _targets_table(ImageDraw.Draw(lay), n, k2)
        F._over(im, lay, kt)
    if ks > 0.003:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        _runs_strip(ImageDraw.Draw(lay), t - c4, camp, lab, T2, St.ramp(t, c5, c5 + 0.8))
        F._over(im, lay, ks)
    return np.asarray(im)


def _targets_table(d, n, k2):
    x0, y0, x1, _ = F._box(EX_R)
    d.rounded_rectangle((x0, y0, x1, y0 + px(400)), radius=px(16), fill=St.SURF + (255,), outline=St.RULE,
                        width=px(1))
    d.text((x0 + px(28), y0 + px(22)), "The two targets", font=St.font(28, bold=True), fill=St.INK)
    d.text((x0 + px(28), y0 + px(64)), "true utility on the twin's synthetic alloy model, 0 to 1",
           font=St.font(19), fill=St.INK2)
    cx = [x0 + px(440), x0 + px(660)]
    for j, c in enumerate(D.CAMPAIGNS):
        F.swatch(d, cx[j] - px(26), y0 + px(128), St.CAMP[c], s=16)
        d.text((cx[j], y0 + px(122)), CAMP_WORD[c].lower(), font=St.font(22, bold=True), fill=St.INK)
    rows = [("the best existing alloy", [f"{n['targets']['T1'][c]:.2f}" for c in D.CAMPAIGNS],
             [n["targets"]["ref"][c] for c in D.CAMPAIGNS], 1.0),
            ("random designs that beat it", [f"{100 * n['targets']['frac_random'][c]:.0f} %" for c in D.CAMPAIGNS],
             ["", ""], 1.0),
            ("the halfway target", [f"{n['targets']['T2'][c]:.2f}" for c in D.CAMPAIGNS], ["", ""], k2)]
    y = y0 + px(176)
    for lab, vals, subs, k in rows:
        ink = St.mix(St.SURF, St.INK, k)
        d.text((x0 + px(28), y + px(4)), lab, font=St.font(22), fill=ink)
        for j in range(2):
            d.text((cx[j], y), vals[j], font=St.font(30, bold=True), fill=ink)
            if subs[j]:
                d.text((cx[j], y + px(40)), subs[j], font=St.font(17), fill=St.mix(St.SURF, St.INK2, k))
        y += px(74)


def _runs_strip(d, t, camp, lab, tgt, k_note):
    """Each run's first day at the halfway target, both labs: the marks behind a median and a count."""
    x0, y0, x1, _ = F._box(EX_R)
    cell = lab["T2"]
    d.rounded_rectangle((x0, y0, x1, y0 + px(480)), radius=px(16), fill=St.SURF + (255,), outline=St.RULE,
                        width=px(1))
    d.text((x0 + px(28), y0 + px(20)), f"Each run's first day at the halfway target ({tgt:.2f})",
           font=St.font(24, bold=True), fill=St.INK)
    a_new = D.arm3("main", "vertical_lab", lab["new"], camp)["T2"]["days"]
    a_ref = D.arm3("conventional", "proposed", lab["ref"], camp)["T2"]["days"]
    ax0, ax1 = x0 + px(40), x1 - px(190)
    rows = [("automated lab, pKGFN: 12 one-year runs, stocked", a_new, St.CAMP[camp], cell["day_new"], "in its year"),
            ("conventional lab, rule of thumb: 12 three-year runs, ordering as it goes", a_ref, St.BASE,
             cell["day_ref"], "in three years")]
    for i, (lab_, days, col, med, never_words) in enumerate(rows):
        y = y0 + px(78) + i * px(156)
        d.text((ax0, y), lab_, font=St.font(18), fill=St.INK2)
        ya = y + px(92)
        d.line([(ax0, ya), (ax1, ya)], fill=St.RULE, width=px(2))
        for v in (0, 100, 200, 300, 365):
            xx = ax0 + (ax1 - ax0) * v / 365.0
            d.line([(xx, ya), (xx, ya + px(6))], fill=St.RULE, width=px(1))
            d.text((xx, ya + px(10)), f"{v}", font=St.font(15), fill=St.INK2, anchor="ma")
        hits = sorted(v for v in days if v is not None)
        shown = len(hits) * St.ease((t - 1.0 - 5.0 * i) / 2.0)
        for j, v in enumerate(hits):
            if j >= shown or v > 365:
                continue
            xx = ax0 + (ax1 - ax0) * v / 365.0
            d.ellipse((xx - px(8), ya - px(8), xx + px(8), ya + px(8)), fill=col, outline=St.SURF, width=px(2))
        km = St.ramp(t, 3.4 + 5.6 * i, 4.2 + 5.6 * i)
        if med is not None and math.isfinite(med) and km > 0:
            xx = ax0 + (ax1 - ax0) * med / 365.0
            d.line([(xx, ya - px(30)), (xx, ya + px(4))], fill=St.mix(St.SURF, St.INK, km), width=px(3))
            last = " (its last)" if 2 * len(hits) == len(days) else ""
            lab_m = f"median: day {med:.0f}{last}"
            xm = min(max(xx, ax0 + St.text_w(St.font(18, bold=True), lab_m) / 2), ax1 - St.text_w(
                St.font(18, bold=True), lab_m) / 2 + px(150))
            d.text((xm, ya - px(34)), lab_m, font=St.font(18, bold=True), fill=St.mix(St.SURF, St.INK, km),
                   anchor="md")
        never = len(days) - len(hits)
        d.rounded_rectangle((ax1 + px(24), ya - px(34), x1 - px(24), ya + px(34)), radius=px(8), outline=St.RULE,
                            width=px(1))
        d.text(((ax1 + px(24) + x1 - px(24)) / 2, ya - px(12)), f"{never} of {len(days)}",
               font=St.font(20, bold=True), fill=St.INK, anchor="mm")
        d.text(((ax1 + px(24) + x1 - px(24)) / 2, ya + px(14)), f"never, {never_words}", font=St.font(13),
               fill=St.INK2, anchor="mm")
    big, _ = N3.cell_words(cell)
    kf = St.ramp(t, 15.5, 16.5)
    yy = y0 + px(398)
    d.text((x0 + px(40), yy), f"{cell['day_ref']:.0f} / {cell['day_new']:.0f} days: {big} sooner",
           font=St.font(28, bold=True), fill=St.mix(St.SURF, St.INK, kf))
    d.text((x0 + px(40), yy + px(42)), "at least: the conventional lab's median is its last run to get there",
           font=St.font(17), fill=St.mix(St.SURF, St.INK2, kf))


# ===================================================================== the atomizer: design targets and the record
def assume_frame(t: float) -> np.ndarray:
    n = _n()
    tw, lab = n["atomizer"]["twin"], n["atomizer"]["lab"]
    rep = n["replay"]
    im, d = _new()
    _title(d, "The atomizer in this twin runs at design targets",
           "Not at rates the lab has demonstrated. Every result in this video rests on them.", t)
    X = [px(80), px(560), px(1220)]
    y0 = px(230)
    k0 = St.ramp(t, 0.5, 1.2)
    d.text((X[1], y0), "In the twin: a design target", font=St.font(26, bold=True), fill=St.mix(St.BG, St.INK, k0))
    d.text((X[2], y0), "The lab's record so far", font=St.font(26, bold=True), fill=St.mix(St.BG, St.INK, k0))
    d.text((X[2], y0 + px(38)), f"{lab['runs']} runs, 2 October to 13 November 2026", font=St.font(19),
           fill=St.mix(St.BG, St.INK2, k0))
    d.text((X[1], y0 + px(38)), "as coded for the simulated atomizer", font=St.font(19),
           fill=St.mix(St.BG, St.INK2, k0))
    used = rep.get("atomizer_runs_week")
    rows = [
        ("Runs a week", f"{tw['slots_week']} start slots",
         f"about {used:.0f} used in the replayed year" if used else "",
         f"{lab['runs_week']:.1f}", f"{lab['runs']} runs in {lab['weeks']} weeks"),
        ("Runs that fail", f"{100 * tw['p_fail_base']:.0f} %",
         "the base chance; more for a cold melt",
         f"{lab['runs'] - lab['good']} of {lab['runs']}", "had problems: little or no powder in most"),
        ("Usable powder, good run", f"{100 * tw['usable_good']:.0f} %", "of the charge",
         f"{100 * lab['best_yield']:.0f} %", "on the best run; about 75 % on the other good one (estimated)"),
    ]
    y = y0 + px(110)
    for i, (head, a, a2, b, b2) in enumerate(rows):
        k = St.ramp(t, 1.4 + 2.2 * i, 2.1 + 2.2 * i)
        ink, ink2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
        d.line([(X[0], y - px(18)), (px(1840), y - px(18))], fill=St.mix(St.BG, St.RULE, k), width=px(1))
        d.text((X[0], y + px(18)), head, font=St.font(26, bold=True), fill=ink)
        d.text((X[1], y), a, font=St.font(54, bold=True), fill=ink)
        d.text((X[1], y + px(72)), a2, font=St.font(21), fill=ink2)
        d.text((X[2], y), b, font=St.font(54, bold=True), fill=ink)
        d.text((X[2], y + px(72)), b2, font=St.font(21), fill=ink2)
        y += px(150)
    kf = St.ramp(t, 8.5, 9.5)
    _para(d, X[0], px(820), "The lab is still commissioning its atomizer: its five aluminium runs made little "
          "powder, and its two good runs were bronze. Sources: twin/physics.py and twin/facility.py; the lab's "
          "atomizer log (digital-alloy-lab, atomizer-runs/runs.csv), as DAL's audit of round 2's video reads it.",
          St.font(21),
          St.mix(St.BG, St.INK2, kf), px(1760), px(31))
    return np.asarray(im)


# ===================================================================================================== results
def res_t() -> tuple:
    """When each of the results' five parts starts (0.8 s before its narration line)."""
    return (0.0,) + tuple(max(1.0, cue(k, v) - 0.8) for k, v in (("res2", 24.5), ("res3", 57.0), ("res4", 81.2),
                                                                 ("res5", 120.3))) + (RESULTS_DURATION,)


def results_caps() -> list:
    n = _n()
    M = n["main"]
    T = res_t()
    al, cu = "flaime_al", "onr_cu"
    cm = n["cu_money"]
    same, thumb = n["labs"][cu]["same"]["T2"], n["labs"][al]["thumb"]["T2"]
    K = n["cost"]["per_alloy"]
    return [
        (T[0], T[1], f"12 simulated one-year runs per policy in the automated lab. Aluminium: BOFN and pKGFN finished "
                     f"highest ({M['bofn3'][al]['best']:.2f} and {M['pkgfn3'][al]['best']:.2f}). Copper: tiered "
                     f"CALPHAD screening still finished ahead ({M['tiered'][cu]['best']:.2f} against "
                     f"{M['bofn3'][cu]['best']:.2f} and {M['pkgfn3'][cu]['best']:.2f})."),
        (T[1], T[2], "Days to each target, every run a mark. The median is the 6th of 12 runs to get there; no "
                     "median when fewer than half do."),
        (T[2], T[3], "Copper is limited by money, not by capacity: removing the cap did not speed it up. With three "
                     f"times the copper money, BOFN and pKGFN gain {cm['bofn3']['own']['mean']:.2f} and "
                     f"{cm['pkgfn3']['own']['mean']:.2f} ({cm['bofn3']['n']} runs each)."),
        (T[3], T[4], "Against a conventional lab. Every factor: a stocked automated lab (one-year runs) against a "
                     "conventional lab ordering metal as it goes (three-year runs)."),
        (T[4], T[5], "Cost on one basis for both campaigns: equipment included. A demonstrated alloy: "
                     f"{St.money(K['both|vertical lab, campaigns only, with capex'])} automated against "
                     f"{St.money(K['both|conventional, with capex'])} conventional."),
    ]


def results_frame(t: float, captions: bool = True) -> np.ndarray:
    ctx = F.context()
    im, d = _new()
    caps = results_caps()
    if captions:
        F._header(d, "Results", caps, t, total=RESULTS_DURATION)
    else:
        d.text((px(80), px(44)), "Results", font=St.font(44, bold=True), fill=St.INK)
    T = res_t()
    parts = [_res_curves, _res_days, _res_money, _res_labs, _res_cost]
    for i, fn in enumerate(parts):
        a, b = T[i], T[i + 1]
        k = min(St.ramp(t, a, a + 0.6) if a > 0 else 1.0, 1.0 - St.ramp(t, b - 0.5, b) if b < RESULTS_DURATION
                else 1.0)
        if k <= 0.003:
            continue
        if k >= 0.997:
            fn(d, im, t - a, ctx)
        else:
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            fn(ImageDraw.Draw(lay), lay, t - a, ctx)
            F._over(im, lay, k)
    return np.asarray(im)


def _res_curves(d, lay, t, ctx):
    """Best new alloy so far against days, four policies, both campaigns: the automated lab's 12 one-year runs (mean
    and SE), the conventional lab's first year where it ran the same policy, and both targets."""
    n = _n()
    pols = ["bofn3", "pkgfn3", "tiered", "heuristic"]
    Hd = 365.0
    g = ctx.day_grid
    X0, X1, Y0 = px(150), px(1840), px(196)
    gapx = px(46)
    pw = (X1 - X0 - gapx * (len(pols) - 1)) / len(pols)
    sweep = Hd * St.ease((t - 0.8) / 5.0)
    k = int(np.searchsorted(g, sweep, side="right"))
    bands = {False: Image.new("RGBA", lay.size, (0, 0, 0, 0)), True: Image.new("RGBA", lay.size, (0, 0, 0, 0))}
    todo = []
    for ri, camp in enumerate(D.CAMPAIGNS):
        ry = Y0 + ri * px(334)
        col = St.CAMP[camp]
        T1, T2 = n["targets"]["T1"][camp], n["targets"]["T2"][camp]
        fb = St.font(24, bold=True)
        F.swatch(d, px(80), ry + px(6), col, s=18)
        d.text((px(108), ry), St.CAMP_NAME[camp], font=fb, fill=St.INK)
        d.text((px(108) + St.text_w(fb, St.CAMP_NAME[camp]) + px(12), ry + px(4)),
               St.CAMP_LONG[camp].split(": ", 1)[-1], font=St.font(20), fill=St.INK2)
        for ci, p in enumerate(pols):
            x0 = X0 + ci * (pw + gapx)
            ax = F.Ax((x0, ry + px(78), x0 + pw, ry + px(278)), (0.0, Hd), (0.0, 0.8), "days", "u")
            a = n["main"][p][camp]
            d.text((x0, ry + px(42)), POL[p].replace(" (rule of thumb)", "").replace(" CALPHAD", ""),
                   font=St.font(19, bold=True), fill=St.INK)
            d.text((x0 + pw, ry + px(46)), f"{a['best']:.2f} ± {a['se']:.2f}", font=St.font(17), fill=St.INK2,
                   anchor="ra")
            ax.frame(d, fs=15, nx=4, ny=4)
            for fac, c, dashed in ((ctx.conv, St.BASE, True), (ctx.auto, col, False)):
                cv = ctx.B["groups"].get((fac, p), {}).get(camp, [])
                if not cv or k < 2:
                    continue
                key = ("res3_mean", fac, p, camp)
                cache = ctx.__dict__.setdefault("_cache", {})
                if key not in cache:
                    cache[key] = D.mean_curve(cv, g, 0)
                m, se = cache[key]
                F.Ax.band(ax, ImageDraw.Draw(bands[dashed]), g[:k], np.maximum(m[:k] - se[:k], 0), m[:k] + se[:k],
                          c, alpha=0.16 if dashed else 0.25)
                todo.append((ax, list(zip(g[:k], m[:k])), c, dashed))
            todo.append((ax, (T1, T2), None, None))
    F._over(lay, bands[True])
    F._over(lay, bands[False])
    for ax, pts, c, dashed in todo:
        if c is None:
            ax.dotted_h(d, pts[0], St.TARGET)
            ax.dotted_h(d, pts[1], St.TARGET)
        else:
            ax.line(d, pts, c, px(3), dashed=dashed)
    lx, ly = px(80), px(880)
    x = F.legend_line(d, lx, ly, "solid2", None, "automated lab, mean ± SE of 12 one-year runs", fs=19, w=44)
    x = F.legend_line(d, x, ly, "dashed", St.BASE, "conventional lab, the first year of 12 three-year runs "
                      "(BOFN and pKGFN were not run there)", fs=19, w=44)
    F.legend_line(d, lx, ly + px(38), "dotted", St.TARGET, "the two targets: the best existing alloy on this "
                  "synthetic benchmark (lower) and the halfway target; right of each title: the final best new "
                  "alloy, mean ± SE", fs=19, w=44)


def _res_days(d, lay, t, ctx):
    """Days to both targets, every policy, both campaigns: each run a mark, the Kaplan-Meier median, the count."""
    n = _n()
    Hd = 365.0
    x_lab = px(80)
    cols = []                                             # (campaign, target, x0, x1)
    xa = px(420)
    wa = px(250)
    for camp in D.CAMPAIGNS:
        for tn in ("T1", "T2"):
            cols.append((camp, tn, xa, xa + wa))
            xa += wa + px(118)
        xa += px(8)
    y0 = px(250)
    rh = px(68)
    for camp, tn, x0, x1 in cols:
        tv = n["targets"][tn][camp]
        d.text((x0, y0 - px(62)), f"{CAMP_WORD[camp]}: " + ("the best existing alloy" if tn == "T1" else
                                                           "the halfway target"), font=St.font(18, bold=True),
               fill=St.INK)
        d.text((x0, y0 - px(36)), f"utility {tv:.2f}", font=St.font(16), fill=St.INK2)
    for ri, p in enumerate(POLS):
        y = y0 + ri * rh
        k = St.ramp(t, 0.4 + 0.25 * ri, 1.0 + 0.25 * ri)
        ink, ink2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
        d.text((x_lab, y + px(14)), POL[p], font=St.font(20, bold=p in ("bofn3", "pkgfn3", "tiered")), fill=ink)
        for camp, tn, x0, x1 in cols:
            a3 = D.arm3("main", "vertical_lab", p, camp)[tn]
            a = n["main"][p][camp][tn]
            ya = y + px(26)
            d.line([(x0, ya), (x1, ya)], fill=St.mix(St.BG, St.RULE, k), width=px(1))
            col = St.mix(St.BG, St.CAMP[camp], k)
            for v in a3["days"]:
                if v is None:
                    continue
                xx = x0 + (x1 - x0) * v / Hd
                d.line([(xx, ya - px(9)), (xx, ya + px(9))], fill=col, width=px(3))
            if a["day"] is not None:
                xx = x0 + (x1 - x0) * a["day"] / Hd
                d.polygon([(xx, ya - px(15)), (xx + px(9), ya), (xx, ya + px(15)), (xx - px(9), ya)], fill=ink,
                          outline=St.BG)
                txt = f"day {a['day']:.0f}"
            else:
                txt = "no median"
            d.text((x1 + px(10), ya - px(12)), txt, font=St.font(17, bold=a["day"] is not None), fill=ink)
            d.text((x1 + px(10), ya + px(10)), f"{a['hit']} of {n['main'][p][camp]['n']} runs", font=St.font(14),
                   fill=ink2)
    ya = y0 + len(POLS) * rh + px(4)
    for camp, tn, x0, x1 in cols:
        for v in (0, 180, 365):
            xx = x0 + (x1 - x0) * v / Hd
            d.text((xx, ya), f"{v}", font=St.font(14), fill=St.INK2, anchor="ma")
    d.text((x_lab, ya), "day of the simulated year", font=St.font(16), fill=St.INK2)
    kk = St.ramp(t, 3.0, 3.8)
    _para(d, px(80), px(868), "Each mark: one run's first day at the target. Diamond: the median (Kaplan-Meier; a run "
          "that never gets there counts as later than the year). Automated lab, stocked, 12 one-year runs per "
          "policy. The heuristic is first to aluminium's low bar and then stalls: the halfway target in 1 of 12 "
          "runs.", St.font(19), St.mix(St.BG, St.INK2, kk),
          px(1760), px(28))


def _res_money(d, lay, t, ctx):
    """Copper and money: where the money goes, and what three times the copper money buys."""
    n = _n()
    cm = n["cu_money"]
    sh = n["orders_share"]
    cu = "onr_cu"
    # left: where the money went
    x0 = px(80)
    d.text((x0, px(196)), "Where the money goes", font=St.font(26, bold=True), fill=St.INK)
    d.text((x0, px(234)), "share of each campaign's spending, mean of all 96 runs", font=St.font(19), fill=St.INK2)
    y = px(300)
    kk = St.ease(t / 2.0)
    for c in D.CAMPAIGNS:
        d.text((x0, y), CAMP_WORD[c], font=St.font(22, bold=True), fill=St.INK)
        bx0, bx1 = x0, x0 + px(620)
        w = (bx1 - bx0) * sh[c] * kk
        d.rounded_rectangle((bx0, y + px(40), bx1, y + px(84)), radius=px(6), fill=St.SURF, outline=St.RULE,
                            width=px(1))
        d.rounded_rectangle((bx0, y + px(40), bx0 + max(px(8), w), y + px(84)), radius=px(6), fill=St.CAMP[c])
        d.text((bx0 + px(14), y + px(62)), f"orders of metal and consumables: {100 * sh[c] * kk:.0f} %",
               font=St.font(20, bold=True), fill=St.INK, anchor="lm")
        d.text((bx1 + px(12), y + px(62)), "builds, tests", font=St.font(17), fill=St.INK2, anchor="lm")
        y += px(130)
    lots, imm = n["cu_year"]["lots"], n["cu_year"]["immersions"]
    _para(d, x0, y + px(6), f"Whatever the policy, copper's $60k a year buys {lots[0]:.0f} to {lots[1]:.0f} powder "
          f"lots and {imm[0]:.0f} to {imm[1]:.0f} finished 30-day immersions (means of 12 runs). The lab is not "
          "what runs out.", St.font(20), St.INK2, px(700), px(29))
    # right: three times the money
    X0 = px(940)
    d.text((X0, px(196)), "Three times the copper money ($180k a year)", font=St.font(26, bold=True), fill=St.INK)
    d.text((X0, px(234)), "the final best new copper alloy, mean ± SE, against the same seeds at $60k",
           font=St.font(19), fill=St.INK2)
    ax = F.Ax((X0 + px(330), px(300), px(1700), px(700)), (0.40, 0.76), (0, 1), "u", "u")
    for v in (0.4, 0.5, 0.6, 0.7):
        xx = ax.X(v)
        d.line([(xx, ax.y0), (xx, ax.y1)], fill=St.GRID, width=1)
        d.text((xx, ax.y1 + px(8)), f"{v:.1f}", font=St.font(17), fill=St.INK2, anchor="ma")
    d.text(((ax.x0 + ax.x1) / 2, ax.y1 + px(38)), "utility of the best new alloy at the end of the year",
           font=St.font(17), fill=St.INK2, anchor="ma")
    T2 = n["targets"]["T2"][cu]
    xx = ax.X(T2)
    St.dashed_line(d, [(xx, ax.y0), (xx, ax.y1)], St.TARGET, width=px(2), dash=px(3), gap=px(7))
    d.text((xx + px(8), ax.y0 - px(4)), "halfway target", font=St.font(15), fill=St.INK2, anchor="ld")
    rows = [("tiered", "tiered CALPHAD screening"), ("bofn3", "BOFN, time-aware"), ("pkgfn3", "pKGFN, time-aware")]
    rh = (ax.y1 - ax.y0) / len(rows)
    for i, (p, lab) in enumerate(rows):
        g = cm[p]
        yc = ax.y0 + rh * (i + 0.5)
        k = St.ramp(t, 1.0 + 0.9 * i, 1.8 + 0.9 * i)
        ink, ink2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
        d.text((X0, yc - px(22)), lab, font=St.font(21, bold=True), fill=ink)
        d.text((X0, yc + px(8)), f"{g['n']} runs at each budget", font=St.font(17), fill=ink2)
        b, a, se = g["base"], g["best"], g["se"]
        yb, ya = yc - px(18), yc + px(18)
        # $60k (hollow) then $180k (filled), an arrow between
        d.line([(ax.X(b), yb), (ax.X(a), ya)], fill=St.mix(St.BG, St.RULE, k), width=px(2))
        d.ellipse((ax.X(b) - px(9), yb - px(9), ax.X(b) + px(9), yb + px(9)), outline=St.mix(St.BG, St.CAMP[cu], k),
                  width=px(3))
        d.line([(ax.X(a - se), ya), (ax.X(a + se), ya)], fill=St.mix(St.BG, St.CAMP[cu], k), width=px(3))
        d.ellipse((ax.X(a) - px(10), ya - px(10), ax.X(a) + px(10), ya + px(10)), fill=St.mix(St.BG, St.CAMP[cu], k))
        d.text((ax.X(b) - px(16), yb), f"$60k: {b:.2f}", font=St.font(16), fill=ink2, anchor="rm")
        d.text((ax.x1 + px(20), yc - px(14)), f"{a:.2f} ± {se:.2f}", font=St.font(22, bold=True), fill=ink,
               anchor="lm")
        o = g["own"]
        d.text((ax.x1 + px(20), yc + px(14)), f"{o['mean']:+.2f} ± {o['se']:.2f}", font=St.font(17), fill=ink2,
               anchor="lm")
    kf = St.ramp(t, 4.4, 5.2)
    f_, b_, p_ = cm["tiered"], cm["bofn3"], cm["pkgfn3"]
    _para(d, X0, px(770), f"Hollow: $60k. Filled: $180k. BOFN and pKGFN draw level with tiered screening on the final "
          f"alloy; tiered screening is still first to both targets (day {f_['T1']['day']:.0f} and "
          f"{f_['T2']['day']:.0f}, against day {min(b_['T1']['day'], p_['T1']['day']):.0f} to "
          f"{max(b_['T1']['day'], p_['T1']['day']):.0f} for the first). BOFN and pKGFN have "
          f"{b_['n']} runs each here: a small sample.", St.font(19), St.mix(St.BG, St.INK2, kf), px(880), px(28))


def _lab_cell(d, x0, y0, w, cell, k, bg=St.SURF):
    """One factor: the number (with "at least" where it is a bound), the days where the summaries agree on them, the
    interval, the runs that got there, and the same count inside the first year of both labs."""
    big, _ = N3.cell_words(cell)
    ink, ink2 = St.mix(bg, St.INK, k), St.mix(bg, St.INK2, k)
    n = cell["n"]
    if cell["kind"] == "none":
        slower = 2 * cell["hit_ref"] >= n                # the conventional lab has a median, the automated lab none
        d.text((x0, y0 + px(8)), "no speed-up" if slower else "no factor", font=St.font(30), fill=ink2)
        y = y0 + px(58)
        y = _para(d, x0, y, "the automated lab got there in fewer runs" if slower else
                  "neither lab got there in half its runs", St.font(16), ink2, w, px(22), max_lines=2)
    else:
        x = x0
        if cell["kind"] == "at_least":
            d.text((x, y0 + px(22)), "at least", font=St.font(22, bold=True), fill=ink)
            x += St.text_w(St.font(22, bold=True), "at least") + px(10)
        d.text((x, y0), N3.x1(cell["af"]), font=St.font(46, bold=True), fill=ink)
        y = y0 + px(60)
        if cell.get("days_ok"):
            d.text((x0, y), f"day {cell['day_new']:.0f} against " + ("at least " if cell["kind"] == "at_least"
                                                                    else "") + f"day {cell['day_ref']:.0f}",
                   font=St.font(18), fill=ink)
            y += px(26)
        if cell["kind"] == "factor":
            d.text((x0, y), f"95 % interval {N3.rng(cell['lo'], cell['hi'])}", font=St.font(16), fill=ink2)
            y += px(22)
    d.text((x0, y), f"runs that got there: {cell['hit_new']} of {n} against {cell['hit_ref']} of {n}",
           font=St.font(16), fill=ink2)
    d.text((x0, y + px(22)), f"inside the first year: {cell['hit_new']} against {cell['hit_ref_365']}",
           font=St.font(16), fill=ink2)


def _res_labs(d, lay, t, ctx, y_top=196):
    """The lab against a conventional lab, like for like: the same policy in both labs above the comparison against
    the conventional lab run by rule of thumb, to both targets, with the run counts."""
    n = _n()
    for i, camp in enumerate(D.CAMPAIGNS):
        L = n["labs"][camp]
        x0 = px(80) + i * px(900)
        x1 = x0 + px(860)
        y0 = px(y_top)
        k = St.ramp(t, 0.3 + 0.5 * i, 1.0 + 0.5 * i)
        if k <= 0:
            continue
        ink, ink2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
        d.rounded_rectangle((x0, y0, x1, y0 + px(604)), radius=px(16), fill=St.SURF + (255,), outline=St.RULE,
                            width=px(1))
        F.swatch(d, x0 + px(24), y0 + px(22), St.mix(St.BG, St.CAMP[camp], k), s=20)
        d.text((x0 + px(56), y0 + px(14)), CAMP_WORD[camp], font=St.font(28, bold=True), fill=ink)
        d.text((x1 - px(24), y0 + px(24)), "counts: automated lab against conventional lab", font=St.font(16),
               fill=ink2, anchor="ra")
        T = n["targets"]
        cw = px(406)
        for j, tn in enumerate(("T1", "T2")):
            cx = x0 + px(24) + j * cw
            d.text((cx, y0 + px(62)), "to the best existing alloy's score" if tn == "T1" else "to the halfway target",
                   font=St.font(18, bold=True), fill=ink)
            d.text((cx + St.text_w(St.font(18, bold=True), "to the best existing alloy's score" if tn == "T1" else
                                   "to the halfway target") + px(10), y0 + px(64)), f"{T[tn][camp]:.2f}",
                   font=St.font(16), fill=ink2)
        rows = [("same", "The same policy in both labs", POL[L["same"]["new"]].replace(" (rule of thumb)", "") +
                 " in both"),
                ("thumb", "Against the conventional lab run by rule of thumb", POL[L["thumb"]["new"]].split(",")[0] +
                 " in the automated lab")]
        for r, (key, h1, h2) in enumerate(rows):
            yy = y0 + px(100) + r * px(250)
            kr = St.ramp(t, 0.5 * i + (10.0 if key == "same" else 22.0), 0.8 + 0.5 * i +
                         (10.0 if key == "same" else 22.0)) * k        # as the voice reaches each row
            inkr, inkr2 = St.mix(St.SURF, St.INK, kr), St.mix(St.SURF, St.INK2, kr)
            d.line([(x0 + px(24), yy), (x1 - px(24), yy)], fill=St.mix(St.SURF, St.RULE, k), width=px(1))
            d.text((x0 + px(24), yy + px(12)), h1, font=St.font(20, bold=True), fill=inkr)
            d.text((x0 + px(24) + St.text_w(St.font(20, bold=True), h1) + px(12), yy + px(15)), h2,
                   font=St.font(16), fill=inkr2)
            for j, tn in enumerate(("T1", "T2")):
                _lab_cell(d, x0 + px(24) + j * cw, yy + px(52), cw - px(20), L[key][tn], kr)
    kf = St.ramp(t, 4.0, 4.8)
    _para(d, px(80), px(y_top + 620), "Every factor: the automated lab stocked on day 0 (one-year runs), the "
          "conventional lab ordering metal as it goes (three-year runs). Both labs ordering as they go, or both "
          "stocked: not run in round 3, so the stock's share of a factor is not known. BOFN and pKGFN were not run "
          "in the conventional lab. \"At least\": the conventional lab reached the target in half its runs or "
          "fewer. Intervals: 95 %, bootstrap over runs.", St.font(18), St.mix(St.BG, St.INK2, kf), px(1760), px(26))


def _res_cost(d, lay, t, ctx):
    """The cost, on one basis for both campaigns: equipment included."""
    n = _n()
    K = n["cost"]["per_alloy"]
    cst = n["cost"]["to_T1"]
    x0 = px(80)
    d.text((x0, px(196)), "Cost per demonstrated alloy, equipment included", font=St.font(26, bold=True),
           fill=St.INK)
    d.text((x0, px(234)), "materials, fees, labour, service, utilities and space, plus the equipment's depreciation",
           font=St.font(18), fill=St.INK2)
    rows = [("both campaigns", "both"), ("aluminium", "flaime_al"), ("copper", "onr_cu")]
    cases = [("conventional lab", "conventional, with capex", St.BASE),
             ("automated lab, the two campaigns alone", "vertical lab, campaigns only, with capex", None),
             ("automated lab if outside users filled it to 60 % (assumed, not shown)",
              "vertical lab, 60% utilized, with capex", "hollow")]
    vmax = max(K[f"{c}|{case}"] for _, c in rows for _, case, _ in cases)
    bx0, bx1 = x0 + px(10), x0 + px(700)
    y = px(292)
    kk = St.ease(t / 2.0)
    for lab, c in rows:
        col = St.CAMP.get(c, St.INK)
        d.text((x0, y), lab, font=St.font(21, bold=True), fill=St.INK)
        y += px(34)
        for name, case, style in cases:
            v = K[f"{c}|{case}"]
            w = (bx1 - bx0) * v / vmax * kk
            if style == "hollow":
                d.rounded_rectangle((bx0, y, bx0 + max(px(4), w), y + px(22)), radius=px(4), outline=col,
                                    width=px(2))
            else:
                d.rounded_rectangle((bx0, y, bx0 + max(px(4), w), y + px(22)), radius=px(4),
                                    fill=style if style else col)
            d.text((bx0 + max(px(4), w) + px(10), y + px(11)), St.money(v * kk), font=St.font(18, bold=True),
                   fill=St.INK, anchor="lm")
            y += px(30)
        y += px(20)
    lx, ly = x0, px(770)
    d.rounded_rectangle((lx, ly, lx + px(26), ly + px(16)), radius=px(3), fill=St.BASE)
    d.text((lx + px(36), ly + px(8)), "conventional lab", font=St.font(17), fill=St.INK2, anchor="lm")
    for j, cc in enumerate((St.INK, St.CAMP["flaime_al"], St.CAMP["onr_cu"])):
        d.rounded_rectangle((lx + px(230) + j * px(30), ly, lx + px(254) + j * px(30), ly + px(16)), radius=px(3),
                            fill=cc)
    d.text((lx + px(330), ly + px(8)), "automated lab, the two campaigns carrying it alone", font=St.font(17),
           fill=St.INK2, anchor="lm")
    d.rounded_rectangle((lx, ly + px(30), lx + px(26), ly + px(46)), radius=px(3), outline=St.INK2, width=px(2))
    d.text((lx + px(36), ly + px(38)), "automated lab if outside users filled it to 60 %: assumed, not shown by any "
           "data", font=St.font(17), fill=St.INK2, anchor="lm")
    # right: the cost of reaching the first target
    X0 = px(1000)
    d.text((X0, px(196)), "Cost of reaching the first target, equipment included", font=St.font(26, bold=True),
           fill=St.INK)
    d.text((X0, px(234)), "automated (pKGFN) over conventional (rule of thumb); 1.0 = the same cost",
           font=St.font(18), fill=St.INK2)
    ax = F.Ax((X0 + px(170), px(300), px(1800), px(560)), (0.0, 2.4), (0, 1), "u", "u")
    for v in (0.0, 0.5, 1.0, 1.5, 2.0):
        xx = ax.X(v)
        d.line([(xx, ax.y0), (xx, ax.y1)], fill=St.RULE if v == 1.0 else St.GRID, width=px(2) if v == 1.0 else 1)
        d.text((xx, ax.y1 + px(8)), f"{v:.1f}x", font=St.font(17), fill=St.INK2, anchor="ma")
    for i, c in enumerate(D.CAMPAIGNS):
        g = cst[c]["full_alone"]
        yc = ax.y0 + (ax.y1 - ax.y0) * (i + 0.5) / 2
        k = St.ramp(t, 1.5 + 0.8 * i, 2.3 + 0.8 * i)
        col = St.mix(St.BG, St.CAMP[c], k)
        d.text((X0, yc), CAMP_WORD[c], font=St.font(22, bold=True), fill=St.mix(St.BG, St.INK, k), anchor="lm")
        d.line([(ax.X(g["lo"]), yc), (ax.X(min(g["hi"], 2.4)), yc)], fill=col, width=px(4))
        d.ellipse((ax.X(g["ratio"]) - px(11), yc - px(11), ax.X(g["ratio"]) + px(11), yc + px(11)), fill=col)
        d.text((ax.X(g["ratio"]), yc - px(20)), f"{g['ratio']:.1f}x", font=St.font(24, bold=True),
               fill=St.mix(St.BG, St.INK, k), anchor="md")
        d.text((ax.X(min(g["hi"], 2.4)) + px(10), yc + px(22)), f"95 % interval {N3.rng(g['lo'], g['hi'])}",
               font=St.font(15), fill=St.mix(St.BG, St.INK2, k), anchor="ra")
    kf = St.ramp(t, 4.0, 4.8)
    u = n["util"]["capex_weighted"]
    cap = n["cost"]["capex"]
    _para(d, X0, px(640), f"The equipment: {St.money(cap['vertical'])} for the automated lab, "
          f"{St.money(cap['conventional'])} for the conventional one. The two campaigns use {100 * u:.0f} % of the "
          "automated lab's capacity, weighted by capital cost: it is mostly idle, because money, not capacity, "
          "limits them. Both intervals include 1.0.", St.font(20), St.mix(St.BG, St.INK2, kf), px(820), px(30))


# ==================================================================================================== takeaway
def takeaway_frame(t: float) -> np.ndarray:
    n = _n()
    M = n["main"]
    al, cu = "flaime_al", "onr_cu"
    c1, c2, c3 = cue("take1", 1.0), cue("take2", 16.8), cue("take3", 42.8)
    im, d = _new()
    d.text((W / 2, px(40)), "In this simulated benchmark", font=St.font(40, bold=True), fill=_ink(t, 0.2),
           anchor="ma")
    # ---- what the policies found
    for i, camp in enumerate(D.CAMPAIGNS):
        cx = W / 2 + (i - 0.5) * px(900)
        y0 = px(112)
        k = St.ramp(t, c1 + 0.3 + (8.0 if i else 0.0), c1 + 1.1 + (8.0 if i else 0.0))
        ink, ink2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
        d.rounded_rectangle((cx - px(430), y0, cx + px(430), y0 + px(250)), radius=px(18),
                            fill=St.mix(St.BG, St.SURF, k), outline=St.mix(St.BG, St.CAMP[camp], k), width=px(3))
        d.text((cx - px(400), y0 + px(18)), CAMP_WORD[camp], font=St.font(30, bold=True), fill=ink)
        if camp == al:
            b, p, h = M["bofn3"][al], M["pkgfn3"][al], M["heuristic"][al]
            head = "BOFN and pKGFN reached the halfway target in about three months"
            body = (f"Day {b['T2']['day']:.0f} and day {p['T2']['day']:.0f}, in {b['T2']['hit']} and "
                    f"{p['T2']['hit']} of 12 runs (time-aware); BOFN per dollar in "
                    f"{M['bofn3_usd'][al]['T2']['hit']}; no other policy in more than {n['al_T2_others_max']}. The "
                    f"heuristic reached the best existing alloy's score first (day {h['T1']['day']:.0f}) and then "
                    "stalled.")
        else:
            f_, b, p = M["tiered"][cu], M["bofn3"][cu], M["pkgfn3"][cu]
            head = "Tiered CALPHAD screening still won; money, not capacity, was the limit"
            body = (f"It finished at {f_['best']:.2f} against {b['best']:.2f} and {p['best']:.2f} for BOFN and "
                    f"pKGFN, and reached the halfway target on day {f_['T2']['day']:.0f} in {f_['T2']['hit']} of 12 "
                    "runs. With three times the money, BOFN and pKGFN drew level on the final alloy.")
        yy = _para(d, cx - px(400), y0 + px(64), head, St.font(23, bold=True), ink, px(800), px(31), max_lines=2)
        _para(d, cx - px(400), yy + px(8), body, St.font(19), ink2, px(800), px(27), max_lines=4)
    # ---- against a conventional lab: both campaigns' halfway targets, the same policy beside rule of thumb
    k2 = St.ramp(t, c2 + 0.2, c2 + 1.0)
    surf = St.mix(St.BG, St.SURF, k2)
    ink, ink2 = St.mix(St.BG, St.INK, k2), St.mix(St.BG, St.INK2, k2)
    y0 = px(386)
    d.rounded_rectangle((px(80), y0, px(1840), y0 + px(300)), radius=px(18), fill=surf,
                        outline=St.mix(St.BG, St.RULE, k2), width=px(2))
    d.text((px(110), y0 + px(14)), "Against a conventional lab, to the halfway target", font=St.font(28, bold=True),
           fill=ink)
    d.text((px(110), y0 + px(54)), "a stocked automated lab (one-year runs) against a conventional lab ordering metal "
           "as it goes (three-year runs)", font=St.font(19), fill=ink2)
    X = [px(110), px(330), px(860)]
    d.text((X[1], y0 + px(92)), "The same policy in both labs", font=St.font(18, bold=True), fill=ink)
    d.text((X[2], y0 + px(92)), "Against a lab run by rule of thumb", font=St.font(18, bold=True), fill=ink)

    def words(cell, who):
        nn = cell["n"]
        cnt = f"{who}: {cell['hit_new']} of {nn} runs against {cell['hit_ref']} of {nn}"
        if cell["kind"] == "none":
            return ("no speed-up" if 2 * cell["hit_ref"] >= nn else "no factor"), cnt, False, ""
        if cell["kind"] == "at_least":
            return f"at least {N3.x1(cell['af'])} sooner", cnt, True, ""
        return f"{N3.x1(cell['af'])} sooner", cnt, True, f"95 % interval {N3.rng(cell['lo'], cell['hi'])}"
    for r, camp in enumerate(D.CAMPAIGNS):
        yy = y0 + px(128) + r * px(84)
        L = n["labs"][camp]
        d.line([(X[0], yy - px(6)), (px(1330), yy - px(6))], fill=St.mix(surf, St.RULE, k2), width=px(1))
        F.swatch(d, X[0], yy + px(12), St.mix(surf, St.CAMP[camp], k2), s=16)
        d.text((X[0] + px(26), yy + px(6)), CAMP_WORD[camp], font=St.font(22, bold=True), fill=ink)
        for j, key in enumerate(("same", "thumb")):
            who = (POL[L[key]["new"]].replace(" (rule of thumb)", "").replace(" CALPHAD", "") + " in both"
                   if key == "same" else POL[L[key]["new"]].split(",")[0] + " in the automated lab")
            big, small, strong, ci = words(L[key]["T2"], who)
            t_c = c2 + ((10.3, 12.8), (16.6, 19.3))[j][r]             # as the voice reaches each cell
            kk = St.ramp(t, t_c, t_c + 0.8) * k2
            fb = St.font(30, bold=strong)
            d.text((X[1 + j], yy), big, font=fb, fill=St.mix(surf, St.INK if strong else St.INK2, kk))
            if ci:
                d.text((X[1 + j] + St.text_w(fb, big) + px(14), yy + px(12)), ci, font=St.font(16),
                       fill=St.mix(surf, St.INK2, kk))
            d.text((X[1 + j], yy + px(42)), small, font=St.font(15), fill=St.mix(surf, St.INK2, kk))
    kn = St.ramp(t, c2 + 20.6, c2 + 21.4) * k2
    x = px(1380)
    d.line([(x - px(28), y0 + px(96)), (x - px(28), y0 + px(280))], fill=St.mix(surf, St.RULE, k2), width=px(1))
    d.text((x, y0 + px(92)), "Not measured", font=St.font(30, bold=True), fill=St.mix(surf, St.INK, kn))
    _para(d, x, y0 + px(140), "How much of a factor is the stock on the shelf: round 3 did not run both labs "
          "ordering metal as they go. BOFN and pKGFN were not run in the conventional lab.", St.font(18),
          St.mix(surf, St.INK2, kn), px(430), px(25), max_lines=6)
    # ---- the cost, one basis
    k3 = St.ramp(t, c3 + 0.2, c3 + 1.0)
    ink, ink2 = St.mix(St.BG, St.INK, k3), St.mix(St.BG, St.INK2, k3)
    y0 = px(710)
    d.rounded_rectangle((px(80), y0, px(1840), y0 + px(168)), radius=px(18), fill=St.mix(St.BG, St.SURF, k3),
                        outline=St.mix(St.BG, St.RULE, k3), width=px(2))
    d.text((px(110), y0 + px(16)), "Cost, equipment included", font=St.font(28, bold=True), fill=ink)
    d.text((px(110), y0 + px(56)), "to reach the first target: automated (pKGFN) over conventional (rule of thumb)",
           font=St.font(19), fill=ink2)
    cst = n["cost"]["to_T1"]
    for j, c in enumerate(D.CAMPAIGNS):
        g = cst[c]["full_alone"]
        x = px(110) + j * px(420)
        d.text((x, y0 + px(90)), f"{g['ratio']:.1f}x", font=St.font(44, bold=True), fill=ink)
        xx = x + St.text_w(St.font(44, bold=True), f"{g['ratio']:.1f}x") + px(14)
        d.text((xx, y0 + px(98)), CAMP_WORD[c].lower(), font=St.font(20, bold=True), fill=ink)
        d.text((xx, y0 + px(126)), f"95 % interval {N3.rng(g['lo'], g['hi'])}", font=St.font(16), fill=ink2)
    K = n["cost"]["per_alloy"]
    _para(d, px(110) + 2 * px(420) + px(40), y0 + px(92), "Per demonstrated alloy, both campaigns: "
          f"{St.money(K['both|vertical lab, campaigns only, with capex'])} automated against "
          f"{St.money(K['both|conventional, with capex'])} conventional, while the two campaigns carry the lab "
          "alone.", St.font(19), ink2, px(820), px(27), max_lines=3)
    # ---- what the target is
    kf = St.ramp(t, 2.0, 2.8)
    T = n["targets"]
    _para(d, W / 2, px(900), f"The first target is the best existing alloy on this synthetic benchmark "
          f"({T['ref'][al]} {T['T1'][al]:.2f}, {T['ref'][cu]} {T['T1'][cu]:.2f}): one random design in "
          f"{T['one_in']} beats it. The halfway target ({T['T2'][al]:.2f}, {T['T2'][cu]:.2f}) is halfway from there "
          "to the best alloy the twin's own search found.", St.font(19), St.mix(St.BG, St.INK2, kf), px(1720),
          px(27), anchor="ma", max_lines=2)
    d.text((W / 2, px(976)), "Simulated campaigns in a digital twin: not lab results. 12 runs per policy in each lab.",
           font=St.font(22, bold=True), fill=St.mix(St.BG, St.INK, kf), anchor="ma")
    return np.asarray(im)


# ====================================================================================================== stills
if __name__ == "__main__":                                  # python -m twin.video.figs3 [part ...] -> /tmp/vid/
    import sys
    from pathlib import Path
    out = Path("/tmp/vid")
    out.mkdir(parents=True, exist_ok=True)
    which = sys.argv[1:] or ["changes", "explain", "assume", "results", "takeaway"]
    T = res_t()
    jobs = dict(changes=(changes_frame, (4, 14, 25)),
                explain=(explain_frame, (5, 12, cue("fig2", 18) + 4, cue("fig3", 27) + 8, cue("fig4", 40) + 6,
                                         cue("fig4", 40) + 16, EXPLAIN_DURATION - 2)),
                assume=(assume_frame, (4, 12, 26)),
                results=(results_frame, tuple(T[i] + x for i in range(5) for x in (3.0, 14.0))),
                takeaway=(takeaway_frame, (5, cue("take2", 17) + 6, cue("take2", 17) + 18, TAKEAWAY_DURATION - 2)))
    for name in which:
        fn, ts = jobs[name]
        for tt in ts:
            Image.fromarray(fn(float(tt))).save(out / f"r3_{name}_{float(tt):05.1f}.png")
            print(name, tt, flush=True)
