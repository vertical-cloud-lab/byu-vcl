#!/usr/bin/env python3
"""How much of the squeeze did the white/black correction take out? All three 2026-09-30 runs on one scale.

    python3 analyse_white_black_correction.py

No hardware. Asked on PR #202: the white and black wells were meant to fix the
distortion found in the first paint readings (results-paint-accuracy-2026-09-30.md);
to what degree did they? Three runs, each read with the enclosure resting on the
plate at nozzle z 86.5, rail lights on:

    before     13:25  A1 yellow, A2 red, A3 blue, A6 empty           paint-plate-2026-09-30.json
    1st try    15:47  + white in A4, black in A5, next to the paints paint-white-black-2026-09-30.json
    2nd try    19:15  H2 yellow, H4 red, H7 black, H10 blue, H12 white,
                      empty wells between them                       paint-spaced-2026-09-30.json

"Before" is paint / empty well with the board lamp's sealed offset subtracted,
exactly as analyse_paint_accuracy.py. The two tries are calibrated exactly as
analyse_white_black.py:

    reflectance = R_black + (R_white - R_black) * (paint - black) / (white - black)

Each is scored the same way, at 440-670 nm (21 values: 3 paints x 7 channels),
against the published range of each paint's pigments (pigment alone to 1:1 with
titanium white; red: PR170 to PR9):

    fit        reading = a + b * reference, with the reference at the middle of the
               range. a is what a perfectly black paint would read; 1/b is how many
               times too small colour differences come out. Accurate is a 0, b 1.
    miss       mean distance outside the range (0 when inside)
    shape      correlation of each paint's 7 values with each pigment's; the
               pigment it correlates best with is the one its shape matches

Controls on the same readings separate the white's part from the black's: the
15:47 run read the old way (/ empty A6), and both tries divided by their white
alone (no black subtracted).

Writes white-black-correction-2026-10-01.json and white-black-correction-2026-10-01.png.
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
from analyse_paint_accuracy import (  # noqa: E402
    CHANNELS, NM, OFFSET, PAINTS, fit_line, km_mix, load_reference, per_channel,
)
from analyse_white_black import BLACKS, WHITES, calibrate, outside  # noqa: E402

KEEP = NM >= 440                  # 410 nm is unreliable under the rail lights
NAMES = ("yellow", "red", "blue")
LOOK = {"yellow": ("#eda100", "o"), "red": ("#e34948", "s"), "blue": ("#2a78d6", "^")}
DARK = {"yellow": (NM >= 440) & (NM <= 470), "red": (NM >= 440) & (NM <= 550), "blue": NM >= 550}
SURFACE, INK, INK2, GRID, BEFORE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#8f8c85"


def spectra_of(readings):
    return np.array([[r["channels"][c] for c in CHANNELS] for r in readings], float)


def references(spectra):
    ref = {}
    for name, _, pigs, tint in PAINTS.values():
        bounds = [per_channel(spectra[p]) for p in pigs] + ([per_channel(spectra[tint])] if tint else [])
        lo, hi = np.min(bounds, axis=0), np.max(bounds, axis=0)
        ref[name] = {"pure": per_channel(km_mix([spectra[p] for p in pigs])),
                     "tinted": per_channel(spectra[tint]) if tint else per_channel(km_mix([spectra[p] for p in pigs])),
                     "lo": lo, "hi": hi, "mid": (lo + hi) / 2}
    return ref


def score(v, ref):
    """The same scorecard for any set of three calibrated spectra."""
    out = {"values": {p: v[p].round(3).tolist() for p in NAMES}}
    y = np.concatenate([v[p][KEEP] for p in NAMES])
    for which in ("mid", "pure", "tinted"):
        a, b, r2 = fit_line(np.concatenate([ref[p][which][KEEP] for p in NAMES]), y)
        out[f"fit_{which}"] = {"a_black_reads": round(a, 3), "b_slope": round(b, 3),
                               "differences_too_small_by": round(1 / b, 2), "r2": round(r2, 3)}
    miss = {p: outside(v[p], ref[p]["lo"], ref[p]["hi"])[KEEP] for p in NAMES}
    out["miss_mean"] = round(float(np.concatenate(list(miss.values())).mean()), 3)
    out["miss_by_paint"] = {p: round(float(m.mean()), 3) for p, m in miss.items()}
    out["inside_range"] = int(sum((m == 0).sum() for m in miss.values()))
    out["dark_floor"] = {p: [round(float(v[p][DARK[p]].min()), 2), round(float(v[p][DARK[p]].max()), 2)]
                         for p in NAMES}
    corr = {p: {q: round(float(np.corrcoef(v[p][KEEP], ref[q]["mid"][KEEP])[0, 1]), 2) for q in NAMES}
            for p in NAMES}
    out["shape_correlation"] = corr
    out["shape_matches"] = {p: max(corr[p], key=corr[p].get) for p in NAMES}
    i440, i620 = list(NM).index(440), list(NM).index(620)
    out["yellow_620_over_440"] = round(float(v["yellow"][i620] / v["yellow"][i440]), 2)
    return out


def main():
    spectra = load_reference()
    ref = references(spectra)
    rw = np.array([per_channel(spectra[k]) for k in WHITES]).mean(axis=0)
    rb = np.array([per_channel(spectra[k]) for k in BLACKS]).mean(axis=0)

    d0 = json.load(open(os.path.join(HERE, "paint-plate-2026-09-30.json")))
    m0 = {w: spectra_of(rs).mean(axis=0) for w, rs in d0["readings"].items()}
    d1 = json.load(open(os.path.join(HERE, "paint-white-black-2026-09-30.json")))
    m1 = {w: spectra_of([r for r in d1["readings"] if r["well"] == w]).mean(axis=0)
          for w in sorted({r["well"] for r in d1["readings"]})}
    d2 = json.load(open(os.path.join(HERE, "paint-spaced-2026-09-30.json")))
    m2 = {p: spectra_of([r for r in d2["readings"] if r["paint"] == p]).mean(axis=0)
          for p in NAMES + ("black", "white")}
    well = {PAINTS[w][0]: w for w in PAINTS}          # yellow -> A1 ...

    runs = {
        "before": ("13:25, paint / empty A6", {p: (m0[well[p]] - OFFSET) / (m0["A6"] - OFFSET) for p in NAMES}),
        "first_try": ("15:47, white A4 and black A5 next to the paints",
                      {p: calibrate(m1[well[p]], m1["A4"], m1["A5"], rw, rb) for p in NAMES}),
        "second_try": ("19:15, white H12 and black H7, empty wells between the paints",
                       {p: calibrate(m2[p], m2["white"], m2["black"], rw, rb) for p in NAMES}),
    }
    controls = {
        "first_try_old_way": ("15:47 readings / empty A6, as before",
                              {p: (m1[well[p]] - OFFSET) / (m1["A6"] - OFFSET) for p in NAMES}),
        "first_try_white_only": ("15:47 readings / white A4 x R_white, no black subtracted",
                                 {p: rw * (m1[well[p]] - OFFSET) / (m1["A4"] - OFFSET) for p in NAMES}),
        "second_try_white_only": ("19:15 readings / white H12 x R_white, no black subtracted",
                                  {p: rw * (m2[p] - OFFSET) / (m2["white"] - OFFSET) for p in NAMES}),
    }
    out = {"what": "the three 2026-09-30 paint runs scored on one scale, 440-670 nm",
           "reference": "pigment alone to 1:1 with titanium white (red: PR170 to PR9); fits use the middle",
           "channels": CHANNELS, "runs": {}, "controls": {}}
    for group, items in (("runs", runs), ("controls", controls)):
        for key, (label, v) in items.items():
            out[group][key] = {"label": label, **score(v, ref)}

    print(f"{'':24s} {'black reads':>11s} {'too small':>9s} {'R2':>5s} {'miss':>6s} {'inside':>6s} "
          f"{'y620/440':>8s}  shape matches")
    for group in ("runs", "controls"):
        for key, s in out[group].items():
            f = s["fit_mid"]
            print(f"{key:24s} {f['a_black_reads']:>11.2f} {f['differences_too_small_by']:>8.2f}x "
                  f"{f['r2']:>5.2f} {s['miss_mean']:>6.3f} {s['inside_range']:>4d}/21 "
                  f"{s['yellow_620_over_440']:>8.2f}  {s['shape_matches']}")
    for key in ("before", "second_try"):
        s = out["runs"][key]
        print(f"{key}: miss by paint {s['miss_by_paint']}, dark floor {s['dark_floor']}")
        print(f"{'':{len(key)}s}  blue's shape correlation {s['shape_correlation']['blue']}")
    b0, b2 = out["runs"]["before"]["fit_mid"], out["runs"]["second_try"]["fit_mid"]
    out["second_try_vs_before"] = {
        "floor_removed_fraction": round(1 - b2["a_black_reads"] / b0["a_black_reads"], 2),
        "squeeze_removed_fraction": round((b2["b_slope"] - b0["b_slope"]) / (1 - b0["b_slope"]), 2),
        "miss_removed_fraction": round(1 - out["runs"]["second_try"]["miss_mean"]
                                       / out["runs"]["before"]["miss_mean"], 2)}
    print("2nd try against before:", out["second_try_vs_before"])

    # The floor can't be the black or the white being off. With R_black too low for
    # this black (a grey black), near-black paints calibrate *below* R_black; with
    # R_white too high for this white (a dim white), the error scales with
    # (paint - black) and vanishes at the black. Here near-black paints read high.
    # One parameter for what's left: the colour wells read as if a fraction f of
    # the view were empty plate, which pulls every value towards the empty plate's
    # calibrated level R_E. That predicts b = 1 - f and a = f * R_E. This run read
    # no empty well, so the 15:47 run's empty / white ratio stands in.
    x = np.concatenate([ref[p]["mid"][KEEP] for p in NAMES])
    y = np.concatenate([runs["second_try"][1][p][KEEP] for p in NAMES])
    empty = (m1["A6"] / m1["A4"]) * m2["white"]
    r_e = calibrate(empty, m2["white"], m2["black"], rw, rb)
    re = np.concatenate([r_e[KEEP]] * len(NAMES))
    f = float((y - x) @ (re - x) / ((re - x) @ (re - x)))
    rms1 = float(np.sqrt(((y - ((1 - f) * x + f * re)) ** 2).mean()))
    rms2 = float(np.sqrt(((y - (b2["a_black_reads"] + b2["b_slope"] * x)) ** 2).mean()))
    out["second_try_view_fraction"] = {
        "f": round(f, 3), "rms_one_parameter": round(rms1, 3), "rms_free_line": round(rms2, 3),
        "r_empty_440_670": r_e[KEEP].round(2).tolist(),
        "empty_plate": "15:47 run's A6 / A4 ratio applied to the 19:15 white; this run read no empty well"}
    print(f"view fraction f {f:.3f}: rms {rms1:.3f} (free line {rms2:.3f})")

    # Red read twice in the 2nd try, five minutes apart: how far does the landing alone move it?
    vis = {k: calibrate(spectra_of([r for r in d2["readings"] if r["paint"] == "red" and r["visit"] == k])
                        .mean(axis=0), m2["white"], m2["black"], rw, rb) for k in (1, 2)}
    out["second_try_red_by_visit"] = {str(k): v.round(3).tolist() for k, v in vis.items()}
    print("red, 2nd try, visit 1:", vis[1].round(2).tolist(), "visit 2:", vis[2].round(2).tolist())

    json.dump(out, open(os.path.join(HERE, "white-black-correction-2026-10-01.json"), "w"), indent=1)
    plot(runs, out, ref, os.path.join(HERE, "white-black-correction-2026-10-01.png"))


def style(ax, title):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", color=INK, fontsize=10.5, pad=8)
    ax.tick_params(colors=INK2, labelsize=8, length=0)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)


def plot(runs, out, ref, path):
    fig = plt.figure(figsize=(12, 9.4), facecolor=SURFACE)
    top = fig.add_gridspec(1, 3, left=0.06, right=0.985, top=0.885, bottom=0.555, wspace=0.16)
    titles = {"before": "Before: ÷ the empty well (13:25)",
              "first_try": "1st try: white A4, black A5 (15:47)",
              "second_try": "2nd try: wells spaced apart (19:15)"}
    for i, key in enumerate(("before", "first_try", "second_try")):
        ax = fig.add_subplot(top[i])
        style(ax, titles[key])
        ax.axhspan(-0.6, 0, color="#efeeeb", lw=0)
        ax.axhspan(1, 1.8, color="#efeeeb", lw=0)
        ax.plot([0, 1], [0, 1], color=INK, lw=1.2)
        f = out["runs"][key]["fit_mid"]
        ax.plot([0, 1], [f["a_black_reads"], f["a_black_reads"] + f["b_slope"]], color=BEFORE, lw=1.6)
        for p in NAMES:
            col, mk = LOOK[p]
            v = runs[key][1][p][KEEP]
            r = ref[p]
            ax.errorbar(r["mid"][KEEP], v, xerr=[(r["mid"] - r["lo"])[KEEP], (r["hi"] - r["mid"])[KEEP]],
                        fmt="none", ecolor=col, elinewidth=1.4, alpha=0.45, capsize=0)
            ax.plot(r["mid"][KEEP], v, ls="none", marker=mk, ms=7, color=col,
                    markeredgecolor=SURFACE, markeredgewidth=1.2, label=p)
        ax.set_xlim(-0.05, 1.02)
        ax.set_ylim(-0.45, 1.45)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
        ax.set_yticks([0, 0.5, 1])
        ax.set_xlabel("what the pigment reflects (published)", color=INK2, fontsize=9)
        if i == 0:
            ax.set_ylabel("what the sensor gave", color=INK2, fontsize=9)
            ax.text(0.74, 0.63, "accurate", rotation=37, fontsize=8, color=INK, ha="center", va="center")
            ax.legend(loc="upper left", fontsize=8, frameon=False, labelcolor=INK, handletextpad=0.2,
                      borderaxespad=0.3)
        s = out["runs"][key]
        k = f["differences_too_small_by"]
        diff = f"{k:.1f}× too small" if k > 1 else f"{1 / k:.1f}× too big"
        black = f"{f['a_black_reads']:.2f}".replace("-", "−")
        ax.text(0.98, -0.40, f"a black paint reads {black}\ndifferences come out {diff}\n"
                f"average miss {s['miss_mean']:.2f}", ha="right", va="bottom", fontsize=8.5, color=INK)
    fig.text(0.01, 0.975, "Each dot is one paint at one channel (440–670 nm). On the black line the reading is "
             "accurate; the grey line is the best straight-line fit.\nA bar spans the published range: pigment alone "
             "to mixed 1:1 with white (red: PR170 to PR9). Grey bands: below 0 or above 1, which no paint can read.",
             fontsize=10, color=INK, va="top")

    bottom = fig.add_gridspec(1, 3, left=0.06, right=0.985, top=0.405, bottom=0.085, wspace=0.16)
    for i, p in enumerate(NAMES):
        col, mk = LOOK[p]
        ax = fig.add_subplot(bottom[i])
        style(ax, f"{p}: before (grey) and 2nd try ({p})")
        ax.axhspan(-0.6, 0, color="#efeeeb", lw=0)
        ax.axhspan(1, 1.8, color="#efeeeb", lw=0)
        ax.fill_between(NM[KEEP], ref[p]["lo"][KEEP], ref[p]["hi"][KEEP], color=col, alpha=0.22, lw=0)
        ax.plot(NM[KEEP], runs["before"][1][p][KEEP], color=BEFORE, lw=1.6, marker=mk, ms=5,
                markerfacecolor=SURFACE, markeredgecolor=BEFORE, markeredgewidth=1.2)
        ax.plot(NM[KEEP], runs["second_try"][1][p][KEEP], color=col, lw=2, marker=mk, ms=6,
                markeredgecolor=SURFACE, markeredgewidth=1.0)
        ax.set_xticks(NM[KEEP])
        ax.set_xlim(430, 680)
        ax.set_ylim(-0.05, 1.08)
        ax.set_yticks([0, 0.5, 1])
        ax.set_xlabel("AS7341 channel (nm)", color=INK2, fontsize=9)
        if i == 0:
            ax.set_ylabel("fraction reflected", color=INK2, fontsize=9)
        m = out["runs"]["before"]["shape_matches"][p], out["runs"]["second_try"]["shape_matches"][p]
        ax.text(0.98, 0.02, f"shape matches: {m[0]} → {m[1]}", transform=ax.transAxes, ha="right",
                va="bottom", fontsize=8.5, color=INK)
    fig.text(0.01, 0.475, "The same three paints as spectra. Shaded: the published range. Before, the blue had a "
             "red paint's shape; with the black subtracted, each paint\nhas its own pigment's shape. Where a pigment "
             "is near-black, the 2nd try still reads 0.24–0.36.", fontsize=10, color=INK, va="top")
    fig.text(0.01, 0.012, "2026-09-30, enclosure resting on the plate at nozzle z 86.5, rail lights on; 410 nm left "
             "out (unreliable under the rail lights). Before: board-lamp offset subtracted, ÷ the empty well.\n"
             "Tries: R_black + (R_white − R_black) × (paint − black) ÷ (white − black). Pigment spectra: Color Mixing "
             "Tools database (Z. Kovács-Vajna), via rubenwiersma/painting_tools.", fontsize=7.5, color=INK2)
    fig.savefig(path, dpi=150, facecolor=SURFACE)
    print("wrote", path)


if __name__ == "__main__":
    main()
