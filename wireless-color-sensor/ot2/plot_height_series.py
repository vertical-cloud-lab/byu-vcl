#!/usr/bin/env python3
"""Plot the slot-7 read-height series: z 120 vs 125 vs 128.

Three runs, identical in every respect but the nozzle Z at the read positions.
Reads the committed run JSONs and writes ``xscan-height-series-2026-09-09.png``.
"""

import json
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

CH = ["ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670"]
NM = [410, 440, 470, 510, 550, 583, 620, 670]
POS = ["pos1-dx-30", "pos2-dx+0", "pos3-dx+30"]
PLBL = ["x −30", "centre", "x +30"]

RUNS = [
    (120, 29.5, "xscan-slot7-z120-2026-09-09.json"),
    (125, 34.5, "xscan-slot7-2026-09-09.json"),
    (128, 37.5, "xscan-slot7-z128-2026-09-09.json"),
]

# ordinal blue ramp, light->dark with increasing height (validated --ordinal)
ZC = {120: "#86b6ef", 125: "#2a78d6", 128: "#104281"}
# categorical slots 1-3 for the three X positions
PC = ["#2a78d6", "#eb6834", "#1baf7a"]

SURFACE, INK, INK2, INK3 = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8985"


def load():
    out = {}
    for z, ap, f in RUNS:
        d = json.load(open(f))
        per = {}
        for p in POS:
            rs = [r for r in d["readings"] if r["stage"] == p]
            per[p] = {
                "totals": [r["total"] for r in rs],
                "chan": [st.mean([r["channels"][c] for r in rs]) for c in CH],
            }
        out[z] = {"aperture": ap, "pos": per}
    return out


def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#dcdbd6")
    ax.tick_params(colors=INK2, labelsize=9, length=0)
    ax.grid(axis="y", color="#eceae5", lw=0.8)
    ax.set_axisbelow(True)


def main():
    d = load()
    fig = plt.figure(figsize=(13.2, 8.4), facecolor=SURFACE)
    gs = GridSpec(2, 3, figure=fig, height_ratios=[1.15, 1.0],
                  hspace=0.42, wspace=0.26, left=0.06, right=0.975,
                  top=0.865, bottom=0.085)

    # --- A: signal ---------------------------------------------------------
    axA = fig.add_subplot(gs[0, :2])
    style(axA)
    x = [0, 1, 2]
    for z, _, _ in RUNS:
        means = [st.mean(d[z]["pos"][p]["totals"]) for p in POS]
        lo = [means[i] - min(d[z]["pos"][p]["totals"]) for i, p in enumerate(POS)]
        hi = [max(d[z]["pos"][p]["totals"]) - means[i] for i, p in enumerate(POS)]
        axA.errorbar(x, means, yerr=[lo, hi], color=ZC[z], lw=2, marker="o",
                     ms=8, capsize=4, elinewidth=1.6, zorder=3,
                     markeredgecolor=SURFACE, markeredgewidth=2)
        axA.annotate(f"z {z}", (x[-1], means[-1]), xytext=(10, 0),
                     textcoords="offset points", color=ZC[z], fontsize=10,
                     fontweight="bold", va="center")
    axA.set_xticks(x); axA.set_xticklabels(PLBL)
    axA.set_xlim(-0.25, 2.42)
    axA.set_ylim(0, 8200)
    axA.set_ylabel("total counts", color=INK2, fontsize=9.5)
    axA.set_title("Signal — bars show the spread of the 3 reads at each stop",
                  loc="left", color=INK, fontsize=11.5, fontweight="bold", pad=8)

    # --- B: repeatability --------------------------------------------------
    axB = fig.add_subplot(gs[0, 2])
    style(axB)
    w = 0.26
    for i, (z, _, _) in enumerate(RUNS):
        vals = []
        for p in POS:
            t = d[z]["pos"][p]["totals"]
            vals.append((max(t) - min(t)) / st.mean(t) * 100)
        xs = [j + (i - 1) * w for j in range(3)]
        for xx, v in zip(xs, vals):
            axB.vlines(xx, 0.02, v, color=ZC[z], lw=1.6, zorder=2)
            axB.annotate(f"{v:.2f}", (xx, v), xytext=(0, 9),
                         textcoords="offset points", ha="center", va="bottom",
                         fontsize=8, color=INK2)
        axB.plot(xs, vals, ls="none", marker="o", ms=9, color=ZC[z], zorder=3,
                 markeredgecolor=SURFACE, markeredgewidth=1.6, label=f"z {z}")
    axB.set_yscale("log")
    axB.set_ylim(0.02, 200)
    axB.set_xlim(-0.5, 2.5)
    axB.set_xticks(range(3)); axB.set_xticklabels(PLBL)
    axB.set_ylabel("read-to-read spread (% of mean)", color=INK2, fontsize=9.5)
    axB.set_title("Repeatability — lower is better, log scale",
                  loc="left", color=INK, fontsize=11.5, fontweight="bold", pad=8)
    axB.legend(frameon=False, fontsize=8.5, labelcolor=INK2, ncol=3,
               loc="upper left", handlelength=0.8, columnspacing=1.2,
               handletextpad=0.4)

    # --- C: spectral shape agreement ---------------------------------------
    for k, (z, ap, _) in enumerate(RUNS):
        ax = fig.add_subplot(gs[1, k])
        style(ax)
        fr = []
        for p in POS:
            c = d[z]["pos"][p]["chan"]
            fr.append([v / sum(c) * 100 for v in c])
        worst = max((max(f[i] for f in fr) - min(f[i] for f in fr))
                    / st.mean([f[i] for f in fr]) * 100 for i in range(len(CH)))
        for j, (p, f) in enumerate(zip(POS, fr)):
            ax.plot(NM, f, color=PC[j], lw=2, marker="o", ms=5,
                    markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=3,
                    label=PLBL[j])
        ax.set_ylim(0, 33)
        ax.set_xlim(398, 685)
        ax.set_xticks([410, 470, 550, 620, 670])
        ax.set_xlabel("channel (nm)", color=INK2, fontsize=9)
        if k == 0:
            ax.set_ylabel("share of total counts (%)", color=INK2, fontsize=9.5)
        ax.set_title(f"z {z}  ·  aperture {ap} mm off deck", loc="left",
                     color=INK, fontsize=11, fontweight="bold", pad=6)
        ax.annotate(f"the three stops disagree by {worst:.1f}%",
                    (0.5, 0.975), xycoords="axes fraction", ha="center",
                    va="top", fontsize=9.5, color=INK, fontweight="bold")
        if k == 0:
            ax.annotate("all three curves coincide", (0.5, 0.885),
                        xycoords="axes fraction", ha="center", va="top",
                        fontsize=8.5, color=INK2, style="italic")
            ax.legend(frameon=False, fontsize=8.5, labelcolor=INK2, ncol=3,
                      loc="lower right", handlelength=0.9, columnspacing=1.0,
                      handletextpad=0.4, bbox_to_anchor=(1.02, -0.02))

    fig.text(0.06, 0.955,
             "Read height in slot 7: 120 mm is right, and every millimetre up makes it worse",
             color=INK, fontsize=15.5, fontweight="bold")
    fig.text(0.06, 0.915,
             "Three runs of run_xscan_test.py, slot 7, empty slot, module LEDs off. "
             "Identical X and Y; only the nozzle Z at the read positions differs.",
             color=INK2, fontsize=10)
    fig.text(0.06, 0.022,
             "Bottom row is the one that matters for a colour test: at z 120 the three "
             "stops agree on the colour of an empty slot to 0.8%; at z 128 they disagree by 56%.",
             color=INK3, fontsize=9, style="italic")

    fig.savefig("xscan-height-series-2026-09-09.png", dpi=145,
                facecolor=SURFACE)
    print("wrote xscan-height-series-2026-09-09.png")


if __name__ == "__main__":
    main()
