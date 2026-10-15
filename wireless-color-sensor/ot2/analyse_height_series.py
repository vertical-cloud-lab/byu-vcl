#!/usr/bin/env python3
"""Which read height gives the most accurate colours? The 2026-10-01 height series.

    python3 analyse_height_series.py

No hardware. Asked on PR #202: try reading the colours at different heights. One
pick-up, one carry: the enclosure was lowered over six wells of the slot-7 plate
(H2 yellow, H4 red, H5 empty, H7 black, H10 blue, H12 white) from nozzle z 125 to
86.5, two readings at each stop, eight more at z 86.5, and H12 was landed on a
second time at the end. Rail lights on, OT-2 blacked out with cardboard.

At every height the three colours are calibrated against that same height's white
and black wells, exactly as analyse_white_black.py does at z 86.5:

    reflectance = R_black + (R_white - R_black) * (paint - black) / (white - black)

and scored as analyse_white_black_correction.py scores the 2026-09-30 runs
(440-670 nm, 21 values, against each pigment's published range):

    miss       mean distance outside the range (0 when inside)
    black      what a perfectly black paint would read (a of reading = a + b * reference)
    squeeze    1/b, how many times too small colour differences come out

Also reported: how much one landing repeats (16 readings at H12), how much a
second landing on the same well differs, and the rail-lights-off reading (the
blackout check).

Writes height-series-analysis-2026-10-01.json and height-series-2026-10-01.png.
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
from analyse_paint_accuracy import CHANNELS, NM, load_reference, per_channel  # noqa: E402
from analyse_white_black import BLACKS, WHITES, calibrate  # noqa: E402
from analyse_white_black_correction import KEEP, references, score  # noqa: E402

HEIGHTS = [125.0, 110.0, 100.0, 95.0, 92.0, 90.0, 89.0, 88.0, 87.0, 86.5]
COLOURS = {"H2": "yellow", "H4": "red", "H10": "blue"}
READ_Z = 86.5            # the height Tim picked on 2026-09-30
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
# Colour is the paint's own colour; every well also has its own marker and a
# direct label, so nothing depends on colour alone.
LOOK = {  # well: (label, colour, marker, filled)
    "H12": ("white", "#b8b5ae", "o", False),
    "H5": ("empty", "#8f8c85", "v", True),
    "H2": ("yellow", "#eda100", "o", True),
    "H4": ("red", "#e34948", "s", True),
    "H10": ("blue", "#2a78d6", "^", True),
    "H7": ("black", INK, "D", True),
}


def mean_spectrum(rows):
    return np.array([[r["channels"][c] for c in CHANNELS] for r in rows], float).mean(axis=0)


def main():
    data = json.load(open(os.path.join(HERE, "height-series-2026-10-01.json")))
    lit = [r for r in data["readings"] if r["well"] and r["rail_lights"] == "on"]
    by = {}
    for r in lit:
        by.setdefault((r["well"], r["visit"], r["nozzle"][2]), []).append(r)

    spectra = load_reference()
    ref = references(spectra)
    rw = np.array([per_channel(spectra[k]) for k in WHITES]).mean(axis=0)
    rb = np.array([per_channel(spectra[k]) for k in BLACKS]).mean(axis=0)

    out = {"what": "white/black-calibrated colours scored at each read height, 2026-10-01",
           "channels": CHANNELS, "heights": {}}
    for z in HEIGHTS:
        m = {w: mean_spectrum(by[(w, 1, z)]) for w in LOOK}
        v = {COLOURS[w]: calibrate(m[w], m["H12"], m["H7"], rw, rb) for w in COLOURS}
        s = score(v, ref)
        rel = {LOOK[w][0]: (m[w] / m["H12"]).round(3).tolist() for w in LOOK if w != "H12"}
        out["heights"][str(z)] = {
            "totals": {LOOK[w][0]: round(float(m[w].sum()), 1) for w in LOOK},
            "relative_to_white": rel,
            "brighter_than_white": {k: int((np.array(x)[KEEP] > 1.0).sum()) for k, x in rel.items()},
            **s}

    # How well one landing repeats, and how much a second landing differs.
    h12 = [r for r in lit if r["well"] == "H12" and r["label"] == "H12-white-z86.5"]
    sp = np.array([[r["channels"][c] for c in CHANNELS] for r in h12], float)
    first = mean_spectrum(by[("H12", 1, READ_Z)])
    second = mean_spectrum(by[("H12", 2, READ_Z)])
    land = {str(z): round(float(mean_spectrum(by[("H12", 2, z)]).sum()
                                / mean_spectrum(by[("H12", 1, z)]).sum() - 1), 4)
            for z in (125.0, 90.0, 89.0, 88.0, 87.0, 86.5)}
    dark = [r for r in data["readings"] if r["rail_lights"] == "off"]
    out["repeatability"] = {
        "one_landing_16_readings": {"totals_min_max": [int(sp.sum(1).min()), int(sp.sum(1).max())],
                                    "per_channel_sd_counts": sp.std(axis=0, ddof=1).round(2).tolist(),
                                    "per_channel_sd_percent": (100 * sp.std(axis=0, ddof=1)
                                                               / sp.mean(axis=0)).round(2).tolist()},
        "second_landing_h12_minus_first_fraction_of_total": land,
        "second_over_first_per_channel_at_86.5": (second / first).round(3).tolist(),
        "free_hanging_drift_z125_h12": [12056, 11978, 11942],
        "free_hanging_drift_note": "13:49, 13:53, 14:06 MDT: -0.95% over 17 min",
    }
    out["rail_lights_off_on_white_86.5"] = {
        "channels": mean_spectrum(dark).round(1).tolist(),
        "total": round(float(mean_spectrum(dark).sum()), 1),
        "sealed_lamp_2026_09_10": [4.0, 3.0, 8.0, 160.5, 168.5, 35.0, 16.0, 11.5],
        "note": "equal to the board's own lamp in a closed box: no measurable room light"}
    best = min(HEIGHTS, key=lambda z: out["heights"][str(z)]["miss_mean"])
    out["best_height_by_miss"] = best
    json.dump(out, open(os.path.join(HERE, "height-series-analysis-2026-10-01.json"), "w"), indent=1)

    print(f"{'z':>6s} {'miss':>6s} {'black':>6s} {'squeeze':>7s} {'R2':>5s} {'inside':>6s}  "
          f"{'colours brighter than white (of 21)':>36s}")
    for z in HEIGHTS:
        h = out["heights"][str(z)]
        f = h["fit_mid"]
        nb = sum(h["brighter_than_white"][k] for k in ("yellow", "red", "blue"))
        print(f"{z:6.1f} {h['miss_mean']:6.3f} {f['a_black_reads']:6.2f} "
              f"{f['differences_too_small_by']:7.2f} {f['r2']:5.2f} {h['inside_range']:6d}  {nb:36d}")
    print("second landing on H12, change in total:", land)
    print("one landing, per-channel sd %:", out["repeatability"]["one_landing_16_readings"]["per_channel_sd_percent"])
    print("lights off on white:", out["rail_lights_off_on_white_86.5"]["channels"])
    print("best height by miss:", best)

    plot(by, out, ref)


def plot(by, out, ref):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "font.family": "DejaVu Sans"})
    fig = plt.figure(figsize=(12.5, 8.2), facecolor=SURFACE)
    gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1], hspace=0.42, wspace=0.28)
    ax1 = fig.add_subplot(gs[0, :2])
    ax2 = fig.add_subplot(gs[0, 2])
    small = [fig.add_subplot(gs[1, i]) for i in range(3)]
    for ax in [ax1, ax2] + small:
        ax.set_facecolor(SURFACE)
        ax.grid(True, color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)

    # 1. Light reaching the sensor against height, every well.
    zs = sorted({k[2] for k in by if k[1] == 1 and k[0] == "H12"})
    for w, (label, col, mk, filled) in LOOK.items():
        pts = sorted((z, mean_spectrum(by[(w, 1, z)]).sum()) for z in zs if (w, 1, z) in by)
        x, y = zip(*pts)
        ax1.plot(x, y, color=col, lw=2, marker=mk, ms=6, mfc=col if filled else SURFACE,
                 mec=col if filled else INK2, zorder=3, label=f"{w} {label}")
    pts = sorted((z, mean_spectrum(by[("H12", 2, z)]).sum()) for z in zs if ("H12", 2, z) in by)
    x, y = zip(*pts)
    ax1.plot(x, y, color=INK2, lw=1.5, ls="--", marker="o", ms=5, mfc=SURFACE, mec=INK2, zorder=3,
             label="H12 white, landed again at the end")
    ax1.axvspan(86.3, 87.6, color=GRID, alpha=0.7, lw=0, zorder=1)
    ax1.annotate("foot resting\non the plate", (86.95, 11900), ha="center", va="top",
                 color=INK2, fontsize=8)
    ax1.legend(frameon=False, fontsize=8, loc="lower right", ncol=2)
    ax1.set_xlim(85.5, 126)
    ax1.set_xlabel("nozzle z (mm)  -  the foot first touches the plate at about 87.5")
    ax1.set_ylabel("total counts, 8 channels")
    ax1.set_title("Light reaching the sensor as the enclosure comes down onto each well",
                  loc="left", color=INK, fontsize=10.5)

    # 2. Accuracy against height.
    miss = [out["heights"][str(z)]["miss_mean"] for z in HEIGHTS]
    ax2.plot(HEIGHTS, miss, color=INK, lw=2, marker="o", ms=6, zorder=3)
    best = out["best_height_by_miss"]
    for z, lab, off in ((best, f"best: z {best:g}", (4, 14)), (READ_Z, f"z {READ_Z:g}, in use", (12, -4))):
        v = out["heights"][str(z)]["miss_mean"]
        ax2.annotate(f"{lab}\nmiss {v:.2f}", (z, v), xytext=off, textcoords="offset points",
                     color=INK2, fontsize=8.5, va="center")
    ax2.set_xlim(85.5, 127)
    ax2.set_ylim(0, max(miss) * 1.15)
    ax2.set_xlabel("nozzle z (mm)")
    ax2.set_ylabel("mean miss vs published pigments (0 = inside)")
    ax2.set_title("Colour error after white/black correction", loc="left", color=INK, fontsize=10.5)

    # 3. The calibrated colours at the best height and at the height in use.
    nm = NM[KEEP]
    for ax, p in zip(small, ("yellow", "red", "blue")):
        col = {"yellow": "#eda100", "red": "#e34948", "blue": "#2a78d6"}[p]
        ax.fill_between(nm, ref[p]["lo"][KEEP], ref[p]["hi"][KEEP], color=GRID, lw=0,
                        label="published range")
        for z, ls, mk in ((best, "-", "o"), (READ_Z, "--", "s")):
            v = np.array(out["heights"][str(z)]["values"][p])[KEEP]
            ax.plot(nm, v, color=col, ls=ls, lw=2, marker=mk, ms=5,
                    mfc=col if ls == "-" else SURFACE, mec=col, label=f"z {z:g}")
        ax.set_ylim(-0.1, 2.5)
        ax.set_xlabel("channel (nm)")
        ax.set_title(f"{p}: measured vs published", loc="left", color=INK, fontsize=10)
        if p == "yellow":     # same line styles in all three; one legend
            ax.legend(frameon=False, fontsize=8, loc="upper left")
    small[0].set_ylabel("reflectance after correction")
    fig.text(0.01, 0.005, "2026-10-01, plate in slot 7, rail lights on, OT-2 blacked out. "
             "Two readings per stop; 8 more at z 86.5. Data: height-series-2026-10-01.json",
             color=INK2, fontsize=7.5)
    fig.savefig(os.path.join(HERE, "height-series-2026-10-01.png"), dpi=130,
                facecolor=SURFACE, bbox_inches="tight")


if __name__ == "__main__":
    main()
