#!/usr/bin/env python3
"""Which read height is best, said plainly, and what "points off" means.

    python3 analyse_read_height.py

No hardware. Asked on PR #202 (2026-10-09) by @timothy-commins: is reading above the
well better than resting the enclosure on it, and at exactly what height? And what the
percentages in the 10-09 summary meant.

Sources: the calibrated values the earlier analyses committed, for the three runs that
read a ladder of heights over the same five wells (slot 7, H row):

    10-01      bare deck, paint ~19 h old        white-paper-analysis-2026-10-06.json  '10-01 corrected'
    10-06 pm   white paper under the plate       white-paper-analysis-2026-10-06.json  '10-06 corrected'
    10-06 eve  black paper (the standing backing) black-paper-analysis-2026-10-06.json  'black paper direct'

Resting scores are the ones those analyses used (10-01: the second-landing white, 44.2).

    points off  per colour, the mean distance of its 7 readings (440-670 nm) outside the
                published range of its pigment (pigment alone to 1:1 with titanium white;
                red PR170 to PR9), on a 0-100 scale: black well 0, white well 100. Inside
                the range counts as 0. The 10-09 summary's "error"; its "accuracy" was
                100 minus this.
    contrast    slope b of reading = a + b x (middle of the published range): the share
                of the real differences between colours that the readings keep.
    haze        a, what a black paint would read on the same scale.
    shape       r2 of that line.

Gap above the plate ~ nozzle z - 88: the foot first touched at z 86.5-89 depending on the
well (camera and light, 10-01 and 10-06), so every gap is +-1.5 mm.

The best height is also interpolated: a parabola through the lowest tested point and its
two neighbours.

Writes read-height-2026-10-09.json, read-height-2026-10-09.png and
read-height-spectra-2026-10-09.png.
"""
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from analyse_paint_accuracy import NM, load_reference  # noqa: E402
from analyse_white_black import outside  # noqa: E402
from analyse_white_black_correction import KEEP, NAMES, references  # noqa: E402

LADDER = ("90.0", "92.0", "95.0", "100.0", "110.0", "125.0")
CONTACT_Z = 88.0
RUNS = ("10-06 eve", "10-06 pm", "10-01")       # categorical order: the standing setup first
LABEL = {"10-06 eve": "black paper (10-06, current setup)", "10-06 pm": "white paper (10-06)",
         "10-01": "bare deck (10-01)"}
SERIES = {"10-06 eve": "#2a78d6", "10-06 pm": "#eb6834", "10-01": "#1baf7a"}   # validated, all pairs
SHOW_Z = "92.0"                                  # the height the spectra chart shows
COLOUR_WORD = {440: "violet", 470: "blue", 510: "cyan", 550: "green", 583: "yellow", 620: "orange",
               670: "red"}
SURFACE, INK, INK2, MUTED, GRID, BAND = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#d9d7cf"


def load(name):
    return json.load(open(os.path.join(HERE, name)))


def points_off(values, ref):
    out, allm = {}, []
    for p in NAMES:
        m = outside(np.array(values[p], float), ref[p]["lo"], ref[p]["hi"])[KEEP]
        allm.append(m)
        out[p] = round(100 * float(m.mean()), 1)
    out["all"] = round(100 * float(np.concatenate(allm).mean()), 1)
    return out


def row(entry, ref):
    fit = entry["fit_mid"]
    return {"points_off": points_off(entry["values"], ref), "contrast_b": round(fit["b_slope"], 2),
            "haze_a": round(fit["a_black_reads"], 2), "shape_r2": round(fit["r2"], 2),
            "values": entry["values"]}


def vertex(zs, ys):
    """Lowest point of the parabola through three (z, y) points."""
    a, b, c = np.polyfit(zs, ys, 2)
    z0 = -b / (2 * a)
    return round(float(z0), 1), round(float(np.polyval([a, b, c], z0)), 1)


def chart_heights(result):
    plt.rcParams.update({"font.size": 9, "font.family": "DejaVu Sans", "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK2})
    fig, ax = plt.subplots(figsize=(10, 5.6), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    xs = ["resting"] + list(LADDER)
    pos = {z: i for i, z in enumerate(xs)}
    ax.axvspan(pos[SHOW_Z] - 0.42, pos[SHOW_Z] + 0.42, color="#dbe8f8", zorder=0, lw=0)
    ax.text(pos[SHOW_Z], 57.5, "best over\nblack paper", ha="center", va="top", color=INK, fontsize=8.5)
    for run in reversed(RUNS):
        r = result["runs"][run]
        ys = [r["resting"]["points_off"]["all"]] + [r["heights"][z]["points_off"]["all"] for z in LADDER]
        main = run == RUNS[0]
        ax.plot(range(len(xs)), ys, color=SERIES[run], lw=2.6 if main else 2, marker="o",
                ms=8 if main else 7, mec=SURFACE, mew=2, zorder=3 if main else 2)
        ax.annotate(LABEL[run], (len(xs) - 1, ys[-1]), xytext=(10, {"10-06 eve": -13, "10-06 pm": 4, "10-01": 0}[run]),
                    textcoords="offset points", va="center", color=INK2, fontsize=8.5)
        if main:
            for z in ("resting", SHOW_Z):
                y = ys[pos[z]]
                ax.annotate(f"{y:.0f}", (pos[z], y), xytext=(0, -16 if z == SHOW_Z else 10),
                            textcoords="offset points", ha="center", color=INK, fontsize=9, fontweight="bold")
    ax.annotate("Resting on the plate was the\nworst height in all 3 runs", (0.1, 47), xytext=(1.2, 45),
                va="center", color=INK, fontsize=8.5, arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.8})
    ax.text(pos["100.0"], 9.6, "on white paper or bare deck,\nz 100 was best", ha="center", va="top",
            color=INK2, fontsize=8)
    labels = ["resting on\nthe plate\n(z 86.5)"] + [f"{float(z) - CONTACT_Z:.0f} mm\n(z {float(z):.0f})" for z in LADDER]
    ax.set_xticks(range(len(xs)), labels)
    ax.set_xlim(-0.5, len(xs) + 1.6)
    ax.set_ylim(0, 58)
    ax.set_xlabel("How high the enclosure's bottom is above the plate (nozzle height in brackets)", labelpad=8)
    ax.set_ylabel("Points off  (0 = matches the published paint colour; lower is better)")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.suptitle("Read about 4 mm above the plate (nozzle z 92), not resting on it", x=0.065, y=0.975,
                 ha="left", color=INK, fontsize=12)
    fig.text(0.065, 0.905, "Points off: how far each paint's readings are from lab measurements of the same pigment, "
             "on a 0-100 scale\n(black well = 0, white well = 100), averaged over yellow, red and blue. "
             "Each line is one run over the same five wells.", ha="left", va="top", color=INK2, fontsize=8.5)
    fig.subplots_adjust(left=0.065, right=0.985, top=0.83, bottom=0.16)
    fig.savefig(os.path.join(HERE, "read-height-2026-10-09.png"), dpi=150, facecolor=SURFACE)
    plt.close(fig)


def chart_spectra(result, ref):
    run = result["runs"][RUNS[0]]
    keep = [int(n) for n in NM[KEEP]]
    x = np.arange(len(keep))
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.4), facecolor=SURFACE, sharey=True)
    for ax, p in zip(axes, NAMES):
        ax.set_facecolor(SURFACE)
        lo, hi = 100 * ref[p]["lo"][KEEP], 100 * ref[p]["hi"][KEEP]
        ax.fill_between(x, lo, hi, color=BAND, lw=0, zorder=1)
        best = 100 * np.array(run["heights"][SHOW_Z]["values"][p])[KEEP]
        rest = 100 * np.array(run["resting"]["values"][p])[KEEP]
        ax.plot(x, rest, color=SERIES["10-06 pm"], lw=2, ls=(0, (4, 2)), marker="o", ms=7, mec=SURFACE, mew=2, zorder=2)
        ax.plot(x, best, color=SERIES["10-06 eve"], lw=2.4, marker="o", ms=8, mec=SURFACE, mew=2, zorder=3)
        ax.axhline(100, color=MUTED, lw=0.8, ls=":")
        ax.set_xticks(x, [f"{n}\n{COLOUR_WORD[n]}" for n in keep], fontsize=8)
        ax.set_ylim(-5, 175)
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        off = (run["heights"][SHOW_Z]["points_off"][p], run["resting"]["points_off"][p])
        ax.set_title(f"{p.capitalize()} paint\n{off[0]:.0f} points off at z 92, {off[1]:.0f} resting",
                     loc="left", color=INK, fontsize=9.5)
    axes[0].set_ylabel("Brightness, % of the white well (black well = 0)")
    axes[0].text(0.0, 103, "white paint", color=MUTED, fontsize=7.5, va="bottom")
    handles = [plt.Rectangle((0, 0), 1, 1, color=BAND),
               plt.Line2D([], [], color=SERIES["10-06 eve"], lw=2.4, marker="o"),
               plt.Line2D([], [], color=SERIES["10-06 pm"], lw=2, ls=(0, (4, 2)), marker="o")]
    fig.legend(handles, ["lab measurements of the pigment (alone, up to mixed 1:1 with white)",
                         "read 4 mm above the plate (z 92)", "read resting on the plate (z 86.5)"],
               loc="lower center", ncol=3, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, 0.0))
    fig.suptitle("What the sensor read over black paper (10-06), against the pigments' lab measurements",
                 x=0.06, ha="left", color=INK, fontsize=11.5)
    fig.text(0.06, 0.885, "Points off = how far the blue dots sit outside the grey band, on average. "
             "Resting, the colours read brighter than white paint, which no paint can.",
             ha="left", color=INK2, fontsize=8.5)
    fig.subplots_adjust(left=0.06, right=0.99, top=0.76, bottom=0.2, wspace=0.08)
    fig.savefig(os.path.join(HERE, "read-height-spectra-2026-10-09.png"), dpi=150, facecolor=SURFACE)
    plt.close(fig)


def main():
    ref = references(load_reference())
    wp = load("white-paper-analysis-2026-10-06.json")
    bp = load("black-paper-analysis-2026-10-06.json")
    ladders = {"10-01": lambda z: wp["heights"][z]["10-01 corrected"],
               "10-06 pm": lambda z: wp["heights"][z]["10-06 corrected"],
               "10-06 eve": lambda z: bp["scores"][z]["black paper direct"]}
    resting = {"10-01": {"points_off": {"all": round(100 * wp["bottom_10_01"]["second_landing_white"], 1)},
                         "note": "second-landing white; per-colour values not stored"},
               "10-06 pm": row(bp["bottom"]["white paper"], ref),
               "10-06 eve": row(bp["bottom"]["black paper"], ref)}
    runs = {}
    for run in RUNS:
        heights = {z: row(ladders[run](z), ref) for z in LADDER}
        best = min(LADDER, key=lambda z: heights[z]["points_off"]["all"])
        i = LADDER.index(best)
        near = LADDER[max(0, i - 1):i + 2]
        runs[run] = {"what": LABEL[run], "resting": resting[run], "heights": heights,
                     "best_tested_z": float(best),
                     "best_interpolated": dict(zip(("z", "points_off"),
                                                   vertex([float(z) for z in near],
                                                          [heights[z]["points_off"]["all"] for z in near])))
                     if len(near) == 3 else None}
    mean = {z: round(float(np.mean([runs[r]["heights"][z]["points_off"]["all"] for r in RUNS])), 1) for z in LADDER}
    result = {"what": "read height against colour error, three ladder runs, plain-language scale",
              "contact_z_assumed": CONTACT_Z, "gap_mm": {z: round(float(z) - CONTACT_Z, 1) for z in LADDER},
              "runs": runs, "mean_points_off_over_runs": mean,
              "colour_blind_floor_points_off": load("accuracy-summary-2026-10-09.json").get(
                  "colour_blind", {}).get("all", {}).get("error_pct")}
    for run in RUNS:
        r = runs[run]
        print(f"{run:10s} resting {r['resting']['points_off']['all']:5.1f} | "
              + "  ".join(f"z{float(z):.0f} {r['heights'][z]['points_off']['all']:5.1f}" for z in LADDER)
              + f" | best z {r['best_tested_z']:.0f}, interpolated {r['best_interpolated']}")
    print("mean over runs:", mean)
    with open(os.path.join(HERE, "read-height-2026-10-09.json"), "w") as f:
        json.dump(result, f, indent=1)
        f.write("\n")
    chart_heights(result)
    chart_spectra(result, ref)


if __name__ == "__main__":
    main()
