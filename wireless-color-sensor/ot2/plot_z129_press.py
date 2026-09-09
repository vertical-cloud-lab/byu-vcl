#!/usr/bin/env python3
"""Spectral shape at each read position, for the empty slot and the two paint runs.

Shares rather than raw counts: the three runs sit at different aperture heights,
so their levels are not comparable, but the *shape* is what a colour measurement
is made of. Regenerates ``xscan-z129-press90-2026-09-09.png`` from the committed
JSONs.
"""
import json
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CH = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]
NM = [410, 440, 470, 510, 550, 583, 620, 670]

SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#d9d8d4"
SERIES = [
    ("empty slot, z 128", "xscan-slot7-z128-2026-09-09.json", "#2a78d6", "o"),
    ("vials, z 128", "xscan-slot7-paint-2026-09-09.json", "#eb6834", "s"),
    ("vials, z 129 + deeper press", "xscan-slot7-z129-press90-2026-09-09.json",
     "#1baf7a", "^"),
]


def load(path):
    grouped = {}
    for r in json.load(open(path))["readings"]:
        if not r["label"].startswith("pos"):
            continue
        grouped.setdefault(r["label"].rsplit("-", 1)[0], []).append(r)
    out = {}
    for reads in grouped.values():
        x = round(reads[0]["position"]["x"], 2)
        total = st.mean(r["total"] for r in reads)
        out[x] = ([100 * st.mean(r["channels"][c] for r in reads) / total
                   for c in CH], total)
    return out


def main():
    runs = [(label, load(path), colour, marker)
            for label, path, colour, marker in SERIES]
    xs = sorted(runs[0][1])

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.9), sharey=True,
                             facecolor=SURFACE)
    titles = {xs[0]: "x = 33.88 mm  (dx −30)", xs[1]: "x = 63.88 mm  (slot centre)",
              xs[2]: "x = 93.88 mm  (dx +30)"}

    for ax, x in zip(axes, xs):
        ax.set_facecolor(SURFACE)
        for label, data, colour, marker in runs:
            shares, total = data[x]
            ax.plot(NM, shares, color=colour, lw=2.0, marker=marker,
                    ms=6.5, mew=1.6, mfc=SURFACE, label=f"{label}  ({total:.0f} counts)",
                    zorder=3, clip_on=False)
        ax.set_title(titles[x], color=INK, fontsize=11.5, pad=10, loc="left")
        ax.grid(True, color=GRID, lw=0.8, zorder=0)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GRID)
        ax.tick_params(colors=INK_2, labelsize=9.5, length=0)
        ax.set_xlabel("channel centre (nm)", color=INK_2, fontsize=10)
        ax.set_xticks(NM)
        ax.set_xticklabels(NM, rotation=45, ha="right")

    axes[0].set_ylabel("share of the position's own total  (%)", color=INK_2,
                       fontsize=10)

    # the finding: 440/470 nm collapse at x = 33.88 only, in both paint runs
    axes[0].annotate("yellow absorbs here\n440 & 470 nm drop,\n550/583 nm rise",
                     xy=(440, 2.6), xytext=(516, 6.4), fontsize=9.5, color=INK,
                     ha="left", va="center",
                     arrowprops=dict(arrowstyle="->", color=INK_2, lw=1.3,
                                     connectionstyle="arc3,rad=-0.25"))
    axes[2].annotate("all three runs agree\n= bare deck, no vial",
                     xy=(620, 28.3), xytext=(432, 21.5), fontsize=9.5, color=INK,
                     ha="left", va="center",
                     arrowprops=dict(arrowstyle="->", color=INK_2, lw=1.3,
                                     connectionstyle="arc3,rad=-0.18"))

    fig.tight_layout(rect=(0, 0, 1, 0.80))

    fig.text(0.012, 0.965, "Spectral shape at the three read positions, slot 7",
             ha="left", va="top", color=INK, fontsize=13.5)
    fig.text(0.012, 0.895,
             "Shares, not counts \u2014 the runs sit at different aperture heights, "
             "so only the shape is comparable.",
             ha="left", va="top", color=INK_2, fontsize=9.5)
    handles, labels = axes[0].get_legend_handles_labels()
    leg = fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.008, 0.855),
                     ncol=3, frameon=False, fontsize=10, handlelength=2.4,
                     columnspacing=2.4)
    for text in leg.get_texts():
        text.set_color(INK_2)
    fig.savefig("xscan-z129-press90-2026-09-09.png", dpi=170,
                facecolor=SURFACE, bbox_inches="tight")
    print("wrote xscan-z129-press90-2026-09-09.png")


if __name__ == "__main__":
    main()
