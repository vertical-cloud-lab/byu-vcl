#!/usr/bin/env python3
"""Calibrate the paint readings against a white well and a black well.

    python3 analyse_white_black.py [paint-white-black-2026-09-30.json]

No hardware. Reads the full-spectrum readings taken on 2026-09-30 with the
enclosure resting on the plate at nozzle z 86.5 over A1 yellow, A2 red, A3 blue,
A4 white (Liquitex BASICS Titanium White, PW6), A5 black (Mars Black, PBk11) and
A6 empty: eight readings a visit, on two trips (pass 1: A1-A5; pass 2: A6-A2).

Per channel, if the sensor is linear and every well gets the same stray light,

    reflectance = R_black + (R_white - R_black) * (paint - black) / (white - black)

where R_white and R_black are what the two pigments reflect. The board lamp's
offset and the stray light cancel in the two differences, so nothing has to be
subtracted first. R_white and R_black are published spectra of dried drawdowns
(Color Mixing Tools database, via rubenwiersma/painting_tools, CC BY-NC-SA 4.0;
see analyse_paint_accuracy.py): the mean of seven PW6 titanium whites and of two
PBk11 Mars blacks. Each colour is then set against its pigments' range, as in
analyse_paint_accuracy.py.

The black can also be checked against two paints that are known to be near-black
in part of the spectrum: the red (PR170 + PR9) reflects 1-3% from 440 to 550 nm,
and the blue (PB15:3) ~3% from 510 to 670 nm. A black well that reads lighter
than those is grey to the sensor.

Writes white-black-2026-09-30.json and white-black-2026-09-30.png.
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
    CHANNELS, NM, PAINTS, km_mix, load_reference, per_channel,
)

WHITES = [
    "PW6 Chroma Atelier Interactive: 1111-Titanium White",
    "PW6 Ferrario PenColor: 01-White",
    "PW6 Gamblin Cons. Colors: Titanium White",
    "PW6 Golden H.Body Acrylic: 1380-Titanium White",
    "PW6 Maimeri Polycolors: 018-Titanium White",
    "PW6 Talens VanGoghH2Oil: 105-Titanium White",
    "PW6 WinsorNewton Art. Acrylic: 644-Titanium White",
]
BLACKS = ["PBk11 Maimeri Acqua: 540-Mars Black", "PBk11 Maimeri Brera: 540-Mars Black"]
KEEP = NM >= 440                  # 410 nm is unreliable under the rail lights
DARK = {"A2": (NM >= 440) & (NM <= 550), "A3": NM >= 510}   # where each pigment is near-black
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
LOOK = {  # well: (label, line colour, marker, linestyle)
    "A1": ("A1 yellow", "#eda100", "o", "-"),
    "A2": ("A2 red", "#e34948", "s", "-"),
    "A3": ("A3 blue", "#2a78d6", "^", "-"),
    "A5": ("A5 black", INK, "D", "-"),
    "A6": ("A6 empty", "#8f8c85", "v", "--"),
}


def spectra_of(readings):
    return np.array([[r["channels"][c] for c in CHANNELS] for r in readings], float)


def calibrate(s, white, black, rw, rb):
    return rb + (rw - rb) * (s - black) / (white - black)


def outside(v, lo, hi):
    """How far v lies outside [lo, hi], per channel; 0 inside."""
    return np.maximum(0, lo - v) + np.maximum(0, v - hi)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "paint-white-black-2026-09-30.json")
    data = json.load(open(src))
    rd = data["readings"]
    wells = sorted({r["well"] for r in rd})
    well = {w: spectra_of([r for r in rd if r["well"] == w]).mean(axis=0) for w in wells}
    visit = {}
    for r in rd:
        visit.setdefault((r["well"], r["pass"]), []).append(r)
    vmean = {k: spectra_of(v).mean(axis=0) for k, v in visit.items()}
    spectra = load_reference()
    rw_all = np.array([per_channel(spectra[k]) for k in WHITES])
    rb_all = np.array([per_channel(spectra[k]) for k in BLACKS])
    rw, rb = rw_all.mean(axis=0), rb_all.mean(axis=0)
    W, B, E = well["A4"], well["A5"], well["A6"]

    out = {"source": os.path.basename(src), "channels": CHANNELS,
           "method": "reflectance = R_black + (R_white - R_black) * (paint - black) / (white - black), "
                     "per channel, on the mean of every reading of each well (both passes)",
           "r_white": {"pigments": WHITES, "mean": rw.round(3).tolist(),
                       "low": rw_all.min(axis=0).round(3).tolist(),
                       "high": rw_all.max(axis=0).round(3).tolist()},
           "r_black": {"pigments": BLACKS, "mean": rb.round(3).tolist(),
                       "low": rb_all.min(axis=0).round(3).tolist(),
                       "high": rb_all.max(axis=0).round(3).tolist()},
           "mean_counts": {w: v.round(1).tolist() for w, v in well.items()},
           "black_over_white": (B / W).round(3).tolist(),
           "white_over_empty": (W / E).round(3).tolist(),
           "black_over_empty": (B / E).round(3).tolist(),
           "paints": {}}
    print("mean counts per well (both passes):")
    print("        " + "".join(f"{n:>8d}" for n in NM))
    for w in wells:
        print(f"  {w}    " + "".join(f"{v:>8.0f}" for v in well[w]) + f"   total {well[w].sum():.0f}")
    print("black / white " + " ".join(f"{v:.3f}" for v in B / W))
    print("white / empty " + " ".join(f"{v:.3f}" for v in W / E))
    print("black / empty " + " ".join(f"{v:.3f}" for v in B / E))

    cal, lo, hi = {}, {}, {}
    for w, (name, _, pigs, tint) in PAINTS.items():
        cal[w] = calibrate(well[w], W, B, rw, rb)
        pure = per_channel(km_mix([spectra[p] for p in pigs]))
        bounds = [per_channel(spectra[p]) for p in pigs] + ([per_channel(spectra[tint])] if tint else [])
        lo[w], hi[w] = np.min(bounds, axis=0), np.max(bounds, axis=0)
        # How much the choice of R_white / R_black moves the answer
        spread = [calibrate(well[w], W, B, a, b) for a in (rw_all.min(0), rw_all.max(0))
                  for b in (rb_all.min(0), rb_all.max(0))]
        # Each pass on its own white and black, where that pass read the paint
        by_pass = {p: calibrate(vmean[(w, p)], vmean[("A4", p)], vmean[("A5", p)], rw, rb)
                   for p in (1, 2) if (w, p) in vmean}
        miss = outside(cal[w], lo[w], hi[w])[KEEP]
        out["paints"][w] = {
            "paint": name, "pigments": pigs, "with_white": tint,
            "fraction_of_white_minus_black": ((well[w] - B) / (W - B)).round(3).tolist(),
            "reflectance": cal[w].round(3).tolist(),
            "reflectance_low": np.min(spread, axis=0).round(3).tolist(),
            "reflectance_high": np.max(spread, axis=0).round(3).tolist(),
            "reflectance_by_pass": {str(p): v.round(3).tolist() for p, v in by_pass.items()},
            "reference_pure": pure.round(3).tolist(),
            "reference_low": lo[w].round(3).tolist(),
            "reference_high": hi[w].round(3).tolist(),
            "outside_reference_440_670_mean": round(float(miss.mean()), 3),
            "outside_reference_440_670_max": round(float(miss.max()), 3),
            "channels_inside_reference_440_670": int((miss == 0).sum()),
        }
    print("\nreflectance, white/black calibrated; pigment range below:")
    for w in PAINTS:
        print(f"  {PAINTS[w][0]:>6} " + " ".join(f"{v:6.2f}" for v in cal[w]))
        print("         " + " ".join(f"{a:4.2f}-{b:<4.2f}"[:9].rjust(6) for a, b in zip(lo[w], hi[w])))
        o = out["paints"][w]
        print(f"         outside the range by {o['outside_reference_440_670_mean']:.2f} on average "
              f"(max {o['outside_reference_440_670_max']:.2f}) at 440-670 nm; "
              f"{o['channels_inside_reference_440_670']}/7 inside")
    lo_all = min(float(cal[w][KEEP].min()) for w in PAINTS)
    hi_all = max(float(cal[w][KEEP].max()) for w in PAINTS)
    out["calibrated_range_440_670"] = [round(lo_all, 2), round(hi_all, 2)]

    # Is the black black? Where the red and the blue are near-black, how far do
    # they read below the black well, and what reflectance would the black need
    # for them to land on their pigments?
    check = {}
    for w, mask in DARK.items():
        below = (B - well[w]) / B
        q = (well[w] - B) / (W - B)
        target = np.array(out["paints"][w]["reference_pure"])
        rb_needed = (target - rw * q) / (1 - q)
        check[w] = {"nm": NM[mask].tolist(),
                    "paint_below_black_fraction": below[mask].round(3).tolist(),
                    "reference_pure": target[mask].round(3).tolist(),
                    "r_black_that_would_fit": rb_needed[mask].round(3).tolist()}
        print(f"{PAINTS[w][0]} reads below the black by {np.round(100 * below[mask], 1).tolist()} % "
              f"at {NM[mask].tolist()}; the black would need R = {rb_needed[mask].round(2).tolist()}")
    out["black_check"] = check
    for w in ("A1", "A2"):
        above = (well[w] - W) / W
        print(f"{PAINTS[w][0]} reads above the white by {np.round(100 * above, 1).tolist()} %")
        out.setdefault("paint_above_white_fraction", {})[w] = above.round(3).tolist()

    i440, i620 = list(NM).index(440), list(NM).index(620)
    out["yellow_620_over_440"] = {
        "calibrated": round(float(cal["A1"][i620] / cal["A1"][i440]), 1),
        "reference_pure": round(float(out["paints"]["A1"]["reference_pure"][i620]
                                      / out["paints"]["A1"]["reference_pure"][i440]), 1),
        "reference_with_white": round(float(hi["A1"][i620] / hi["A1"][i440]), 1)}
    print("yellow 620/440:", out["yellow_620_over_440"])

    # Repeatability. Within a visit: the 8 readings. Between passes: the same
    # well on the two trips (different pick-ups, ~32 min apart).
    within = {f"{w}-p{p}": round(float((spectra_of(v).std(axis=0, ddof=1) / spectra_of(v).mean(axis=0)).max()), 4)
              for (w, p), v in sorted(visit.items())}
    between = {w: (vmean[(w, 2)] / vmean[(w, 1)] - 1).round(4).tolist()
               for w in wells if (w, 1) in vmean and (w, 2) in vmean}
    out["within_visit_max_cv"] = within
    out["pass2_over_pass1_minus_1"] = between
    print("within-visit max CV:", within)
    for w, v in between.items():
        print(f"  {w} pass 2 / pass 1 - 1: " + " ".join(f"{x:+.3f}" for x in v))
    qdiff = {w: (np.array(out["paints"][w]["reflectance_by_pass"]["2"])
                 - np.array(out["paints"][w]["reflectance_by_pass"]["1"])).round(3).tolist()
             for w in PAINTS if len(out["paints"][w]["reflectance_by_pass"]) == 2}
    out["calibrated_pass2_minus_pass1"] = qdiff
    for w, v in qdiff.items():
        print(f"  {w} calibrated, pass 2 - pass 1: " + " ".join(f"{x:+.2f}" for x in v))

    earlier = data.get("earlier_means")
    if earlier:
        out["change_since_13_25"] = {w: (well[w] / np.array(v) - 1).round(3).tolist()
                                     for w, v in earlier.items() if w in well}
        print("change since the 13:25-13:31 readings (A4 and A5 were empty then):")
        for w, v in out["change_since_13_25"].items():
            print(f"  {w} " + " ".join(f"{x:+.3f}" for x in v))

    json.dump(out, open(os.path.join(HERE, "white-black-2026-09-30.json"), "w"), indent=1)
    plot(well, cal, lo, hi, os.path.join(HERE, "white-black-2026-09-30.png"))


def style(ax, title):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", color=INK, fontsize=10.5, pad=8)
    ax.tick_params(colors=INK2, labelsize=8, length=0)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)


def plot(well, cal, lo, hi, out):
    fig = plt.figure(figsize=(12, 6.2), facecolor=SURFACE)
    ax = fig.add_subplot(fig.add_gridspec(1, 1, left=0.06, right=0.44, top=0.82, bottom=0.14)[0])
    style(ax, "Each well ÷ the white well (A4)")
    W = well["A4"]
    ends = []
    for w in ("A6", "A1", "A2", "A3", "A5"):
        label, col, mk, ls = LOOK[w]
        y = well[w] / W
        ax.plot(NM, y, color=col, marker=mk, ms=6, lw=2, ls=ls,
                markeredgecolor=SURFACE, markeredgewidth=1.0)
        ends.append([float(y[-1]), label])
    ends.sort()
    for i in range(1, len(ends)):          # keep the end labels apart
        ends[i][0] = max(ends[i][0], ends[i - 1][0] + 0.03)
    for y, label in ends:
        ax.annotate(label, (NM[-1], y), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=8.5, color=INK)
    ax.axhline(1.0, color=INK2, lw=1.0)
    ax.text(404, 1.005, "A4 white", fontsize=8, color=INK2, va="bottom")
    ax.set_xticks(NM)
    ax.set_xlim(400, 720)
    ax.set_ylim(0.6, 1.25)
    ax.set_xlabel("AS7341 channel (nm)", color=INK2, fontsize=9)
    ax.set_ylabel("reading ÷ white well", color=INK2, fontsize=9)
    ax.annotate("the black reads lighter than\nthe blue (510-670 nm)\nand the red (440-550 nm)",
                (583, float(well["A5"][5] / W[5])), xytext=(545, 0.625), fontsize=8, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))

    right = fig.add_gridspec(3, 1, left=0.555, right=0.985, top=0.82, bottom=0.14, hspace=0.6)
    for i, (w, (name, col, _, _)) in enumerate(PAINTS.items()):
        ax = fig.add_subplot(right[i])
        style(ax, f"{w} {name}")
        ax.axhspan(-0.6, 0, color="#efeeeb", lw=0)
        ax.axhspan(1, 1.8, color="#efeeeb", lw=0)
        ax.fill_between(NM, lo[w], hi[w], color=col, alpha=0.22, lw=0)
        ax.plot(NM, cal[w], color=col, lw=2, marker="o", ms=5,
                markeredgecolor=SURFACE, markeredgewidth=1.0)
        ax.set_xticks(NM)
        ax.set_xlim(400, 680)
        ax.set_ylim(-0.5, 1.6)
        ax.set_yticks([0, 0.5, 1, 1.5])
        if i == 1:
            ax.set_ylabel("fraction reflected", color=INK2, fontsize=9)
        if i == 2:
            ax.set_xlabel("AS7341 channel (nm)", color=INK2, fontsize=9)
    fig.text(0.545, 0.975, "Calibrated with the white and black wells (line)\n"
             "against the pigment (shaded). Grey: below 0 or above 1,\nwhich no paint can reflect",
             fontsize=10.5, color=INK, va="top")
    fig.text(0.01, 0.975, "What the sensor read\n(mean of 8-16 readings per well)", fontsize=10.5,
             color=INK, va="top")
    fig.text(0.01, 0.012, "2026-09-30, 15:47-16:28 MDT, enclosure resting on the plate at nozzle z 86.5, "
             "rail lights on; 410 nm is unreliable under the rail lights.\nPigment spectra: Color Mixing "
             "Tools database (Z. Kovács-Vajna), via rubenwiersma/painting_tools.",
             fontsize=7.5, color=INK2)
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    print("wrote", out)


if __name__ == "__main__":
    main()
