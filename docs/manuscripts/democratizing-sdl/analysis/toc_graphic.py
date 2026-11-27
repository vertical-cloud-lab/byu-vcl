"""Layout sketch for the table-of-contents graphic. Not for submission.

Digital Discovery wants the TOC graphic at the revision stage, 8 cm x 4 cm at
600 dpi or more, and "original, unpublished artwork created by one of the
co-authors. Preferably, the graphic should not be reused and appear again within
the article." This sketch reuses Figure 1(b) and was drafted with an AI coding
assistant, so it is only a starting point for the co-author who draws the real one.
It draws each project's break-even wage as a dot against the $25-75/h band.

    python toc_graphic.py   # writes ../figures/source/toc-layout-sketch.png

It reads the same PROJECTS as labor_cost_analysis.py.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from labor_cost_analysis import BAND, C_BOM, GRID, INK, INK_2, PROJECTS, SURFACE, median

HERE = Path(__file__).resolve().parent
FIGDIR = HERE.parent / "figures"
DPI = 600


def swarm(values: list[float], min_gap: float) -> list[int]:
    """Stack dots whose values are closer than min_gap: level 0, 1, 2, ... upwards."""
    levels: list[int] = []
    placed: list[tuple[float, int]] = []
    for v in values:
        lv = 0
        while any(abs(v - pv) < min_gap and plv == lv for pv, plv in placed):
            lv += 1
        levels.append(lv)
        placed.append((v, lv))
    return levels


def main() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 6.5,
        "axes.edgecolor": GRID,
        "axes.linewidth": 0.6,
    })
    # 1890 x 945 px is 8.0 x 4.0 cm at 600 dpi exactly (8 cm is 1889.8 px).
    fig = plt.figure(figsize=(1890 / DPI, 945 / DPI), dpi=DPI, facecolor=SURFACE)
    ax = fig.add_axes((0.05, 0.22, 0.90, 0.40))
    ax.set_facecolor(SURFACE)

    wages = sorted(p.breakeven_wage for p in PROJECTS)
    levels = swarm(wages, min_gap=2.6)
    ys = [0.35 + lv * 0.55 for lv in levels]

    ax.axvspan(*BAND, color="#f2f1ee", zorder=0, lw=0)
    ax.text(sum(BAND) / 2, 2.45, "typical loaded labour cost", ha="center", va="top",
            color=INK_2, fontsize=5.6, style="italic")
    ax.scatter(wages, ys, s=26, color=C_BOM, edgecolors=SURFACE, linewidths=0.9, zorder=3)

    med = median(wages)
    top_at_med = max(y for w, y in zip(wages, ys) if abs(w - med) < 1e-9)
    ax.text(med, top_at_med + 0.32, f"median ${med:.0f}/h", ha="center", va="bottom",
            color=INK_2, fontsize=5.6)
    hi = max(wages)
    ax.text(hi, 0.35 + 0.32, f"${hi:.0f}/h", ha="center", va="bottom", color=INK_2, fontsize=5.6)

    ax.set_xlim(-3, 88)
    ax.set_ylim(-0.25, 2.6)
    ax.set_yticks([])
    ax.set_xticks([0, 25, 50, 75])
    ax.set_xticklabels(["$0", "$25", "$50", "$75"])
    ax.tick_params(axis="x", length=0, pad=3, labelcolor=INK_2, labelsize=6)
    for side in ("left", "right", "top"):
        ax.spines[side].set_visible(False)
    ax.set_xlabel("Break-even wage (USD per hour)", color=INK_2, fontsize=6, labelpad=2)

    fig.text(0.05, 0.95, "Labour, not parts, is the bigger bill", ha="left", va="top",
             color=INK, fontsize=8.5, fontweight="bold")
    fig.text(0.05, 0.815, "Each dot is one lab-automation project, at the wage where its build\n"
                          "labour costs as much as its parts. Above that wage, labour costs more.",
             ha="left", va="top", color=INK_2, fontsize=5.8, linespacing=1.3)

    out = FIGDIR / "source" / "toc-layout-sketch.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, facecolor=SURFACE)
    print(f"Wrote {out.relative_to(HERE.parent)} (layout sketch, not for submission)")


if __name__ == "__main__":
    main()
