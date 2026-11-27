"""Round 3b's figure: days to each target for every arm of the lab comparison (simulated).

    python3 -m twin.figures3b          # -> out/twin3b/fig/twin3b_four_ways.png (needs out/twin3b/like3b.json)

Small multiples, one panel per campaign and target. Each row is a policy; each marker an arm's Kaplan-Meier median
day: blue the vertical lab, orange the conventional lab, filled stocked and hollow ordering metal as it goes. A thin
line joins each lab's two stock levels, so its length is what the stock does in that lab. An arm whose seeds mostly
never got there sits at its horizon with a right arrow (365 days for the vertical lab, 1,095 for the conventional
lab). The numbers are in out/twin3b/tables.md.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "out" / "twin3b"
BLUE, ORANGE = "#257de0", "#f47230"            # the reference palette's slots 1-2 (validated, light mode)
INK, INK2, GRID = "#191919", "#666666", "#e6e6e6"
POLS = [("heuristic", "Heuristic"), ("tiered", "Funnel"), ("bofn3", "BOFN"), ("pkgfn3", "pKGFN")]
CAMPS = [("flaime_al", "Aluminium"), ("onr_cu", "Copper")]
TS = [("T1", "best existing alloy (T1)"), ("T2", "halfway target (T2)")]
ARMS = [("vertical_lab", "stocked", BLUE, True), ("vertical_lab", "lean", BLUE, False),
        ("proposed", "stocked", ORANGE, True), ("proposed", "lean", ORANGE, False)]
HOR = {"vertical_lab": 365.0, "proposed": 1095.0}


def main():
    S = json.loads((OUT / "like3b.json").read_text())
    A = S["arms"]
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 7.4), sharex=True)
    for i, (camp, cname) in enumerate(CAMPS):
        for j, (tn, tname) in enumerate(TS):
            ax = axes[i][j]
            for r, (pol, pname) in enumerate(POLS):
                y = len(POLS) - 1 - r
                pts = {}
                for k, (fac, stock, col, filled) in enumerate(ARMS):
                    a = A.get(f"{fac}|{stock}|{pol}")
                    if not a:
                        continue
                    st = a["campaigns"][camp][tn]
                    m = st["median"]
                    unb = m is None or (isinstance(m, float) and not math.isfinite(m)) or m == "inf"
                    x = HOR[fac] if unb else float(m)
                    dy = (0.3, 0.1, -0.1, -0.3)[k]
                    pts[(fac, stock)] = (x, y + dy)
                    ax.plot([x], [y + dy], marker=">" if unb else "o", ms=7, mew=1.5,
                            mfc=col if filled else "white", mec=col, ls="none", zorder=3)
                    ax.annotate(f"{st['hit']}/{st['n']}", (x, y + dy), textcoords="offset points",
                                xytext=(6, -2.5), fontsize=6.5, color=INK2)
                for fac in ("vertical_lab", "proposed"):
                    if (fac, "stocked") in pts and (fac, "lean") in pts:
                        (x0, y0), (x1, y1) = pts[(fac, "stocked")], pts[(fac, "lean")]
                        ax.plot([x0, x1], [y0, y1], color=BLUE if fac == "vertical_lab" else ORANGE, lw=1.0,
                                alpha=0.55, zorder=2)
            ax.set_xscale("log")
            ax.set_xlim(12, 1600)
            ax.set_xticks([15, 30, 60, 120, 240, 365, 730, 1095])
            ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}"))
            ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
            ax.set_yticks(range(len(POLS)))
            ax.set_yticklabels([p for _, p in POLS][::-1], color=INK, fontsize=9)
            ax.set_ylim(-0.6, len(POLS) - 0.4)
            ax.grid(axis="x", color=GRID, lw=0.8)
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            for s in ("left", "bottom"):
                ax.spines[s].set_color("#bbbbbb")
            ax.tick_params(colors=INK2, labelsize=8)
            ax.set_title(f"{cname}: {tname}", fontsize=10, color=INK, loc="left")
            if i == 1:
                ax.set_xlabel("Days from the start to the target (Kaplan-Meier median over seeds; log scale)",
                              fontsize=8.5, color=INK2)
    handles = [Line2D([], [], marker="o", ls="none", mfc=BLUE, mec=BLUE, ms=8, label="vertical lab, stocked"),
               Line2D([], [], marker="o", ls="none", mfc="white", mec=BLUE, mew=1.6, ms=8,
                      label="vertical lab, ordering metal as it goes"),
               Line2D([], [], marker="o", ls="none", mfc=ORANGE, mec=ORANGE, ms=8, label="conventional lab, stocked"),
               Line2D([], [], marker="o", ls="none", mfc="white", mec=ORANGE, mew=1.6, ms=8,
                      label="conventional lab, ordering metal as it goes"),
               Line2D([], [], marker=">", ls="none", mfc="white", mec=INK2, ms=8,
                      label="fewer than half the seeds got there (at the horizon)")]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=8, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("Simulated: days to each target, each lab stocked and ordering as it goes "
                 "(labels: seeds that got there)", fontsize=11, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.07, 1, 0.96))
    (OUT / "fig").mkdir(parents=True, exist_ok=True)
    p = OUT / "fig" / "twin3b_four_ways.png"
    fig.savefig(p, dpi=150)
    print(p)


if __name__ == "__main__":
    main()
