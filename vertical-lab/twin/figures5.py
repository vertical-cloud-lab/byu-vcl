"""Round 5's figures (simulated), from out/twin5/like5.json and the rows in out/twin5/runs.

    python3 -m twin.figures5      # -> out/twin5/fig/twin5_four_ways.png, twin5_money.png, twin5_decisions.png

* ``twin5_four_ways``: days from the money to each target for every arm of comparison 1. Small multiples, one panel
  per campaign and target; each row a policy; each marker an arm's Kaplan-Meier median: blue the automated lab,
  orange the conventional lab, filled stocked, hollow ordering metal as it goes; a right arrow at day 730 where
  fewer than half the seeds got there. A thin line joins each lab's two stock levels. Labels: seeds there.
* ``twin5_money``: each campaign's money spent against the day (median over seeds), the four arms of the cheap
  policies, with the two-year budget.
* ``twin5_decisions``: the same medians as the first figure for the cheap policies, with no decision delay, the
  nominal windows and slow windows.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from twin import bench5 as B5  # noqa: E402
from twin import like5 as L5  # noqa: E402

OUT = B5.OUT
FIG = OUT / "fig"
BLUE, ORANGE = "#257de0", "#f47230"            # the reference palette's slots 1-2 (validated, light mode)
INK, INK2, GRID = "#191919", "#666666", "#e6e6e6"
CAMPS = [("flaime_al", "Aluminium"), ("onr_cu", "Copper")]
TS = [("T1", "best existing alloy (T1)"), ("T2", "halfway target (T2)")]
POLS = [("fast", {"flaime_al": "Heuristic", "onr_cu": "Funnel"}), ("bofn3", "BOFN"), ("pkgfn3", "pKGFN")]
ARMS = [("vertical", "parallel", "reorder", BLUE, True), ("vertical", "parallel", "lean", BLUE, False),
        ("conventional", "external", "reorder", ORANGE, True), ("conventional", "external", "lean", ORANGE, False)]
HOR = 730.0


def _style(ax):
    ax.set_xlim(0, HOR + 60)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8)


def four_ways(S):
    A = S["arms"]
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 6.6), sharex=True)
    for i, (camp, cname) in enumerate(CAMPS):
        for j, (tn, tname) in enumerate(TS):
            ax = axes[i][j]
            labels = []
            for r, (pol, pname) in enumerate(POLS):
                y = len(POLS) - 1 - r
                labels.append((y, pname[camp] if isinstance(pname, dict) else pname))
                pts = {}
                for k, (lab, plan, st, col, filled) in enumerate(ARMS):
                    a = A.get(L5.gk(lab, plan, pol, st))
                    if not a:
                        continue
                    x_ = a["stats"][f"{camp}|{tn}"]
                    m = x_["median"]
                    unb = m is None or not math.isfinite(float(m))
                    x = HOR if unb else float(m)
                    dy = (0.3, 0.1, -0.1, -0.3)[k]
                    pts[(lab, st)] = (x, y + dy)
                    ax.plot([x], [y + dy], marker=">" if unb else "o", ms=7, mew=1.5,
                            mfc=col if filled else "white", mec=col, ls="none", zorder=3)
                    ax.annotate(f"{x_['hit']}/{x_['n']}", (x, y + dy), textcoords="offset points", xytext=(6, -2.5),
                                fontsize=6.5, color=INK2)
                for lab in ("vertical", "conventional"):
                    if (lab, "reorder") in pts and (lab, "lean") in pts:
                        (x1, y1), (x2, y2) = pts[(lab, "reorder")], pts[(lab, "lean")]
                        ax.plot([x1, x2], [y1, y2], color=BLUE if lab == "vertical" else ORANGE, lw=0.8, alpha=0.5,
                                zorder=2)
            ax.set_yticks([y for y, _ in labels])
            ax.set_yticklabels([n for _, n in labels], fontsize=8.5, color=INK)
            ax.set_ylim(-0.6, len(POLS) - 0.4)
            _style(ax)
            ax.set_title(f"{cname}: {tname}", fontsize=10, color=INK, loc="left")
            if i == 1:
                ax.set_xlabel("days from the day the money arrives (Kaplan-Meier median)", fontsize=8.5, color=INK2)
    hand = [Line2D([], [], marker="o", ls="none", mfc=BLUE, mec=BLUE, label="automated lab, stocked"),
            Line2D([], [], marker="o", ls="none", mfc="white", mec=BLUE, mew=1.5, label="automated lab, ordering as it goes"),
            Line2D([], [], marker="o", ls="none", mfc=ORANGE, mec=ORANGE, label="conventional lab, stocked"),
            Line2D([], [], marker="o", ls="none", mfc="white", mec=ORANGE, mew=1.5,
                   label="conventional lab, ordering as it goes"),
            Line2D([], [], marker=">", ls="none", mfc=INK2, mec=INK2, label="fewer than half got there in 2 years")]
    fig.legend(handles=hand, loc="lower center", ncol=3, fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Round 5 (simulated): days to each target, like with like (labels: seeds that got there)",
                 fontsize=11, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.07, 1, 0.97))
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "twin5_four_ways.png", dpi=150)
    plt.close(fig)


def money(Arows):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.0))
    for i, (camp, cname) in enumerate(CAMPS):
        ax = axes[i]
        bud = None
        ends = []
        for lab, plan, st, col, filled in ARMS:
            arm = Arows.get(L5.gk(lab, plan, "fast", st), {})
            if not arm:
                continue
            curves = [r["campaigns"][camp]["spend_curve"] for r in arm.values()]
            bud = next(iter(arm.values()))["campaigns"][camp]["budget"]
            n = min(len(c) for c in curves)
            days = [c[k][0] for k in range(n) for c in curves[:1]]
            med = np.median(np.array([[c[k][1] for k in range(n)] for c in curves]), axis=0) / 1000.0
            ax.plot(days, med, color=col, lw=2, ls="-" if filled else "--")
            ends.append([float(med[-1]), days[-1], f"{'automated' if lab == 'vertical' else 'conventional'}, "
                                                    f"{'stocked' if st == 'reorder' else 'lean'}", col])
        if ends and bud:
            gap = bud / 1000.0 * 0.06                       # labels at least 6 % of the budget apart
            ends.sort(key=lambda e: e[0])
            ys = [e[0] for e in ends]
            for k in range(1, len(ys)):
                ys[k] = max(ys[k], ys[k - 1] + gap)
            top = bud / 1000.0 * 1.1
            if ys[-1] > top:
                shift = ys[-1] - top
                ys = [y - shift for y in ys]
            for (y0, x0, txt, col), y in zip(ends, ys):
                ax.annotate(txt, (x0, y0), xytext=(x0 + 25, y), textcoords="data", fontsize=7, color=INK2,
                            va="center", arrowprops=dict(arrowstyle="-", color=col, lw=0.6))
        if bud:
            ax.axhline(bud / 1000.0, color=INK2, lw=0.8, ls=":")
            ax.annotate("two-year budget", (5, bud / 1000.0), textcoords="offset points", xytext=(0, 3), fontsize=7,
                        color=INK2)
        ax.set_xlim(0, HOR + 230)
        ax.set_ylim(0, (bud or 1) / 1000.0 * 1.12)
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(colors=INK2, labelsize=8)
        ax.set_title(f"{cname}: money spent (median over seeds; heuristic / funnel)", fontsize=10, color=INK,
                     loc="left")
        ax.set_xlabel("days from the day the money arrives", fontsize=8.5, color=INK2)
        ax.set_ylabel("$k spent", fontsize=8.5, color=INK2)
    fig.tight_layout()
    fig.savefig(FIG / "twin5_money.png", dpi=150)
    plt.close(fig)


def decisions(S):
    A = S["arms"]
    lev = [("none", {"decisions": "none"}, "s", "no delay"), ("nominal", {}, "o", "nominal windows"),
           ("slow", {"decisions": "slow"}, "^", "slow windows")]
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 6.0), sharex=True)
    for i, (camp, cname) in enumerate(CAMPS):
        for j, (tn, tname) in enumerate(TS):
            ax = axes[i][j]
            ticks = []
            for r, (lab, plan, st, col, filled) in enumerate(ARMS):
                y = len(ARMS) - 1 - r
                ticks.append((y, f"{'automated' if lab == 'vertical' else 'conventional'}, "
                                 f"{'stocked' if st == 'reorder' else 'lean'}"))
                for k, (ln, o, mk, _) in enumerate(lev):
                    a = A.get(L5.gk(lab, plan, "fast", st, **o))
                    if not a:
                        continue
                    x_ = a["stats"][f"{camp}|{tn}"]
                    m = x_["median"]
                    unb = m is None or not math.isfinite(float(m))
                    x = HOR if unb else float(m)
                    ax.plot([x], [y + (0.22, 0.0, -0.22)[k]], marker=">" if unb else mk, ms=6.5, mew=1.4,
                            mfc=col if filled else "white", mec=col, ls="none", zorder=3)
            ax.set_yticks([y for y, _ in ticks])
            ax.set_yticklabels([n for _, n in ticks], fontsize=8, color=INK)
            ax.set_ylim(-0.6, len(ARMS) - 0.4)
            _style(ax)
            ax.set_title(f"{cname}: {tname}", fontsize=10, color=INK, loc="left")
            if i == 1:
                ax.set_xlabel("days from the day the money arrives (Kaplan-Meier median)", fontsize=8.5, color=INK2)
    hand = [Line2D([], [], marker=mk, ls="none", mfc=INK2, mec=INK2, label=lab_) for _, _, mk, lab_ in lev]
    hand.append(Line2D([], [], marker=">", ls="none", mfc="white", mec=INK2, label="fewer than half got there"))
    fig.legend(handles=hand, loc="lower center", ncol=4, fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Round 5 (simulated): decision time, heuristic (Al) and funnel (Cu); blue automated, orange "
                 "conventional, filled stocked", fontsize=10.5, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.06, 1, 0.96))
    fig.savefig(FIG / "twin5_decisions.png", dpi=150)
    plt.close(fig)


def main():
    S = json.loads((OUT / "like5.json").read_text())
    four_ways(S)
    money(L5.load_all())
    decisions(S)


if __name__ == "__main__":
    main()
