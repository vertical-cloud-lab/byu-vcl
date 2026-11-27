"""The figure for notes/vertical_lab_worth_it.md (issue #407): out/worth_it/worth_it.png.

    python -m twin.worth_it_figure

Two dot plots from out/worth_it/results.json.xz, each a median over the 24 event logs with its 10th-90th percentile
range: how long an outside job takes from request to its sample back on the rack, and how much later an internal step
ends than in the twin. Rows are the two timings at 30 % and 60 % outside load; dots are the issue's three layouts.
"""
from __future__ import annotations

from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from twin import worth_it as W  # noqa: E402
from twin import worth_it_report as R  # noqa: E402

# the reference categorical palette's first three slots (validated all-pairs: CVD dE 12.6, normal 23.0)
SERIES = [(("vlm", 1), "VLM + 1 unit", "#257de0", "o"), (("flat", 2), "flat + 2 units", "#f47230", "s"),
          (("vlm", 2), "VLM + 2 units", "#00b894", "D")]
TEXT, MUTED, GRID = "#1f1f1f", "#6b6b6b", "#e6e6e6"
ROWS = [("none", 0.3, "twin's timing, 30 %"), ("none", 0.6, "twin's timing, 60 %"),
        ("cells", 0.3, "attended time, 30 %"), ("cells", 0.6, "attended time, 60 %")]
PANELS = [("ext_turn_h", "Outside job: request to sample back (h)"),
          ("int_end_h", "Internal step ends later than in the twin (h)")]


def main():
    rows = W._load(W.OUT / "results.json.xz")["rows"]
    g = defaultdict(list)
    for r in rows:
        g[((r.get("params") or {}).get("attend", "none"), r["ext_load"], r["layout"], r["n_mm"])].append(R.metrics(r))
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), sharey=True)
    fig.patch.set_facecolor("white")
    for ax, (key, title) in zip(axes, PANELS):
        for yi, (mode, ext, _) in enumerate(ROWS):
            for si, (lay, name, col, mk) in enumerate(SERIES):
                v = [m[key] for m in g.get((mode, ext, *lay), []) if m[key] is not None]
                if not v:
                    continue
                y = yi + (si - 1) * 0.22
                med, lo, hi = R._med(v), R._pct(v, 0.1), R._pct(v, 0.9)
                ax.plot([max(lo, 0.05), max(hi, 0.05)], [y, y], color=col, lw=2, solid_capstyle="round", zorder=2)
                ax.plot([max(med, 0.05)], [y], marker=mk, ms=8, color=col, mec="white", mew=2, zorder=3,
                        label=name if yi == 0 else None, ls="none")
                if yi == 0:
                    ax.annotate(name, (max(med, 0.05), y), xytext=(8, 0), textcoords="offset points", va="center",
                                fontsize=8.5, color=TEXT)
        ax.set_xscale("log")
        ax.set_title(title, fontsize=11, color=TEXT, loc="left")
        ax.grid(axis="x", color=GRID, lw=1, which="both")
        ax.set_axisbelow(True)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(MUTED)
        ax.tick_params(colors=MUTED, labelsize=9, length=0)
        ax.set_xlabel("hours, log scale (dot: median of 24 logs; bar: 10th-90th percentile)", fontsize=8.5,
                      color=MUTED)
    axes[0].set_yticks(range(len(ROWS)))
    axes[0].set_yticklabels([r[2] for r in ROWS], fontsize=9.5, color=TEXT)
    axes[0].invert_yaxis()
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="upper center", ncol=3, frameon=False, fontsize=9.5, bbox_to_anchor=(0.5, 1.0))
    fig.suptitle("Simulated replay of the twin's year: outside load by timing and layout", fontsize=12, color=TEXT,
                 x=0.01, ha="left", y=1.06)
    fig.tight_layout()
    out = W.OUT / "worth_it.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(out)


if __name__ == "__main__":
    main()
