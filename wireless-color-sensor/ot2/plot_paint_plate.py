#!/usr/bin/env python3
"""Draw the 2026-09-30 paint readings: spectral shape per well, and each paint against the empty well.

    python3 plot_paint_plate.py [paint-plate-2026-09-30.json] [out.png]

Reads the five full-spectrum readings per well from the JSON (A1 yellow, A2
red, A3 blue, A6 empty), all taken with the enclosure sitting on the plate at
nozzle z 86.5 and the rail lights on.
"""
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CHANNELS = ("ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670")
NM = [int(c[2:]) for c in CHANNELS]
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
STYLE = {  # well: (label, colour, marker, linestyle)
    "A1": ("A1 yellow", "#eda100", "o", "-"),
    "A2": ("A2 red", "#e34948", "s", "-"),
    "A3": ("A3 blue", "#2a78d6", "^", "-"),
    "A6": ("A6 empty", INK2, "D", "--"),
}


def mean_channels(readings):
    return np.array([[r["channels"][c] for c in CHANNELS] for r in readings], float).mean(axis=0)


def style_axes(ax, title, ylabel):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", color=INK, fontsize=11, pad=10)
    ax.set_xlabel("AS7341 channel (nm)", color=INK2, fontsize=9)
    ax.set_ylabel(ylabel, color=INK2, fontsize=9)
    ax.set_xticks(NM)
    ax.tick_params(colors=INK2, labelsize=8, length=0)
    ax.grid(True, color=GRID, linewidth=0.8)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xlim(395, 715)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "paint-plate-2026-09-30.json")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "paint-plate-2026-09-30.png")
    data = json.load(open(src))
    means = {w: mean_channels(rs) for w, rs in data["readings"].items()}
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), facecolor=SURFACE)
    ax = axes[0]
    style_axes(ax, "Share of each well's total reading", "% of the 8-channel total")
    for w in ("A6", "A1", "A2", "A3"):
        label, col, mk, ls = STYLE[w]
        share = 100 * means[w] / means[w].sum()
        ax.plot(NM, share, color=col, marker=mk, ms=6, lw=2, ls=ls,
                markeredgecolor=SURFACE, markeredgewidth=1.2)
        ax.annotate(label, (NM[-1], share[-1]), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=8.5, color=INK)
    ax = axes[1]
    style_axes(ax, "Each paint divided by the empty well (A6)", "reading ÷ A6, channel by channel")
    for w in ("A1", "A2", "A3"):
        label, col, mk, ls = STYLE[w]
        ratio = means[w] / means["A6"]
        ax.plot(NM, ratio, color=col, marker=mk, ms=6, lw=2, ls=ls,
                markeredgecolor=SURFACE, markeredgewidth=1.2)
        ax.annotate(label, (NM[-1], ratio[-1]), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=8.5, color=INK)
    fig.text(0.01, 0.01, "Mean of 5 readings per well, enclosure resting on the plate at nozzle "
             "z 86.5, rail lights on. 2026-09-30, 13:25-13:31 MDT.", fontsize=8, color=INK2)
    fig.tight_layout(rect=(0, 0.04, 0.97, 1))
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    print("wrote", out)


if __name__ == "__main__":
    main()
