#!/usr/bin/env python3
"""2026-10-20: does using the black well AND each well's own empty reading beat either alone?

@sgbaird on PR #202 (10-18), on the 10-14 result (black well subtracted 17.8
points off, the well's own empty reading subtracted 28.1): "Technically, we
could probably leverage both." No new readings: this re-scores the 10-14 ones
(``background-subtraction-2026-10-14.json``), the only run with every paint
well read both empty and painted.

The simplest way to use both is a mix of the two subtractions:

    R(a) = Rb + (Rw - Rb) * (paint - [(1 - a) * black + a * empty]) / (white - black)

a = 0 is the black well alone, as every run since 09-30; a = 1 is the well's
own empty reading alone, as on 10-14. ``paint - black - a * (empty - black)``
reads a as the share of this spot's extra light (its empty reading above the
black well's) that is still there once the paint is in: light reaching the
sensor without touching the paint (glare, the neighbours) stays, light coming
up through the clear plate is blocked. So 0 <= a <= 1 is the physical range;
a < 0 is scanned too, to see which way the scores lean.

Scored as ``analyse_background_subtraction.py`` scores: points off, 440-670 nm,
lower is better, 0 is perfect. One a picked to suit the same three paints it
is then scored on flatters itself, so the pick is also checked leave-one-out:
a chosen on two paints, scored on the third. The trips were 1.5 h apart and the
unchanged wells read 1-2% lower on the second, so every result is repeated
with the empty readings scaled by that drift.

    python3 analyse_background_blend.py

Writes ``background-blend-2026-10-20.json`` and ``background-blend-2026-10-20.png``.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_background_subtraction as abs_  # noqa: E402
from analyse_paint_accuracy import load_reference, per_channel  # noqa: E402
from analyse_white_black import BLACKS, WHITES, outside  # noqa: E402
from analyse_white_black_correction import KEEP, references  # noqa: E402

OUT = os.path.join(HERE, "background-blend-2026-10-20.json")
PNG = os.path.join(HERE, "background-blend-2026-10-20.png")
ALPHAS = np.round(np.arange(-0.5, 1.0 + 1e-9, 0.05), 2) + 0.0     # + 0.0: no -0.0
SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
PAINT_COL = {"yellow": "#eda100", "red": "#e34948", "blue": "#2a78d6"}   # as analyse_white_paper.py


def blend(S, E, B, W, rw, rb, a):
    return rb + (rw - rb) * (S - ((1 - a) * B + a * E)) / (W - B)


def score(R, ref):
    return 100 * float(outside(R, ref["lo"], ref["hi"])[KEEP].mean())


def scan(paints, B, W, rw, rb, ref):
    return {name: [round(score(blend(S, E, B, W, rw, rb, a), ref[name]), 2) for a in ALPHAS]
            for name, (S, E) in paints.items()}


def summary(tab):
    names = list(tab)
    mean = np.mean([tab[n] for n in names], axis=0)
    i0, i1 = list(ALPHAS).index(0.0), list(ALPHAS).index(1.0)
    best = int(np.argmin(mean))
    inside = [i for i, a in enumerate(ALPHAS) if 0.0 <= a <= 1.0]
    best_in = inside[int(np.argmin(mean[inside]))]
    loo = {}
    for held in names:
        rest = np.mean([tab[n] for n in names if n != held], axis=0)
        j = int(np.argmin(rest))
        loo[held] = {"a_from_the_other_two": float(ALPHAS[j]), "points_off": tab[held][j],
                     "points_off_at_a0": tab[held][i0]}
    return {
        "mean_points_off": [round(float(m), 2) for m in mean],
        "a0_black_well": round(float(mean[i0]), 1),
        "a1_own_empty": round(float(mean[i1]), 1),
        "best_a_scanned": float(ALPHAS[best]), "best_points_off": round(float(mean[best]), 1),
        "best_a_within_0_1": float(ALPHAS[best_in]), "best_within_0_1_points_off": round(float(mean[best_in]), 1),
        "per_paint_best_a": {n: float(ALPHAS[int(np.argmin(tab[n]))]) for n in names},
        "leave_one_out": loo,
        "leave_one_out_mean": round(float(np.mean([v["points_off"] for v in loo.values()])), 1),
    }


def main():
    data = json.load(open(abs_.DATA))
    g = abs_.spectra(data)
    s = load_reference()
    ref = references(s)
    rw = np.array([per_channel(s[k]) for k in WHITES]).mean(axis=0)
    rb = np.array([per_channel(s[k]) for k in BLACKS]).mean(axis=0)
    t1, t2 = "trip 1", "trip 2"
    B1, W1 = abs_.mean(g, t1, "black-H7"), abs_.mean(g, t1, "white-H12")
    B2, W2 = abs_.mean(g, t2, "black-H7"), abs_.mean(g, t2, "white-H12")
    paints = {name: (abs_.mean(g, t2, f"{name}-{w}"), abs_.mean(g, t1, f"empty-{w}"))
              for w, name in abs_.PAINT.items()}
    # Drift between the trips, per channel, from the two wells that stayed as they were
    drift = (B2 + W2) / (B1 + W1)
    drifted = {name: (S, E * drift) for name, (S, E) in paints.items()}

    tab = scan(paints, B2, W2, rw, rb, ref)
    tab_d = scan(drifted, B2, W2, rw, rb, ref)
    res = {
        "what": "points off for paint - [(1 - a) black + a own-empty], 10-14 readings at nozzle z 92",
        "data": os.path.basename(abs_.DATA), "scored_nm": [440, 470, 510, 550, 583, 620, 670],
        "a": ALPHAS.tolist(), "wells": abs_.PAINT,
        "points_off": tab, "summary": summary(tab),
        "drift_trip2_over_trip1": drift.round(4).tolist(),
        "points_off_drift_corrected": tab_d, "summary_drift_corrected": summary(tab_d),
    }
    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=1)
        fh.write("\n")
    chart(res)
    for key in ("summary", "summary_drift_corrected"):
        sm = res[key]
        print(f"{key}: a=0 {sm['a0_black_well']}  a=1 {sm['a1_own_empty']}  best a "
              f"{sm['best_a_scanned']} -> {sm['best_points_off']}  best in [0,1] "
              f"{sm['best_a_within_0_1']} -> {sm['best_within_0_1_points_off']}  "
              f"leave-one-out {sm['leave_one_out_mean']}  per paint {sm['per_paint_best_a']}")


def chart(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    a = np.array(res["a"])
    sm = res["summary"]
    fig, ax = plt.subplots(figsize=(7.4, 4.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.axvspan(a.min(), 0, color="#eeede8", lw=0, zorder=0)
    for x in (0.0, 1.0):
        ax.axvline(x, color=MUTED, lw=0.8, ls=":", zorder=1)
    for name, col in PAINT_COL.items():
        y = np.array(res["points_off"][name])
        ax.plot(a, y, color=col, lw=2, zorder=3, label=name)
        ax.text(a[-1] + 0.03, y[-1], f"{name} {y[-1]:.1f}", color=INK2, fontsize=8.5, va="center")
    m = np.array(sm["mean_points_off"])
    ax.plot(a, m, color=INK, lw=2.4, zorder=4, label="all three")
    ax.text(a[-1] + 0.03, m[-1], f"all three {m[-1]:.1f}", color=INK, fontsize=8.5, va="center",
            fontweight="bold")
    ib = list(a).index(sm["best_a_scanned"])
    ax.plot([a[ib]], [m[ib]], "o", ms=8, color=INK, mec=SURFACE, mew=2, zorder=5)
    ax.annotate(f"lowest: a = {sm['best_a_scanned']:g}, {sm['best_points_off']:.1f}\n"
                f"(a = 0: {sm['a0_black_well']:.1f})", (a[ib], m[ib]), xytext=(a[ib] - 0.17, m[ib] + 6.5),
                color=INK, fontsize=8.5, ha="left",
                arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.8})
    ax.text(-0.25, 36.6, "a < 0: no physical reading", color=INK2, fontsize=8, ha="center", va="top")
    ax.set_xlim(a.min(), a.max() + 0.42)
    ax.set_ylim(0, 38)
    ticks = np.arange(-0.5, 1.01, 0.25)
    ax.set_xticks(ticks)
    ax.set_xticklabels([{0.0: "0\nblack well\n(as now)", 1.0: "1\nown empty\n(10-14)"}.get(round(t, 2) + 0.0, f"{t:g}")
                        for t in ticks])
    ax.set_xlabel("a: share of the well's own empty reading subtracted (the rest: the black well)",
                  color=INK2, fontsize=9)
    ax.set_ylabel("points off (lower is better)", color=INK2, fontsize=9)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.legend(loc="upper left", bbox_to_anchor=(0.33, 0.81), frameon=False, fontsize=8.5, labelcolor=INK2)
    ax.set_title("Mixing in the well's own empty reading: every share of it makes the colours worse\n"
                 "10-14 readings, nozzle z 92, black paper, clear plate", color=INK, fontsize=10, loc="left")
    fig.tight_layout()
    fig.savefig(PNG, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
