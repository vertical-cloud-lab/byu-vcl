#!/usr/bin/env python3
"""Calibrate the 2026-09-30 evening readings: five paints, each with empty wells all round.

    python3 analyse_spaced_wells.py [paint-spaced-2026-09-30.json]

No hardware. Reads the full-spectrum readings taken at 19:15-19:27 MDT with the
enclosure resting on the plate at nozzle z 86.5 over the plate's front row:

    H2 yellow   H4 red   H7 black   H10 blue   H12 white

with every other well empty, so each paint has the same kind of neighbours. That
was the fix proposed after the 15:36-16:40 run (white in A4, black in A5, next to
the colours), where a well's reading changed with its neighbours and the black
read lighter than the red and the blue (results-white-black-2026-09-30.md). The
white and the black are also new: Timothy made them less watery, since the
earlier black looked grey.

The calibration is analyse_white_black.py's, unchanged:

    reflectance = R_black + (R_white - R_black) * (paint - black) / (white - black)

per channel, with R_white and R_black the mean published PW6 and PBk11 spectra.
Each colour is then set against its pigments' range (analyse_paint_accuracy.py),
and against what the 15:36-16:40 run gave (white-black-2026-09-30.json).

Red was read twice, at 19:22 and again at 19:27 on the way back. The two visits
agree at 620-670 nm and differ by up to 12.5% at 440 nm; the result uses their
mean and reports both. The change fits the sensor seeing 13% empty plate in
place of red paint (R^2 0.91, with the 15:36 run's empty A6 as the empty plate),
so where the enclosure sits over a well moves a reading at this level.

Writes spaced-wells-2026-09-30.json and spaced-wells-2026-09-30.png.
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
from analyse_paint_accuracy import CHANNELS, NM, km_mix, load_reference, per_channel  # noqa: E402
from analyse_white_black import BLACKS, WHITES, calibrate, outside  # noqa: E402

KEEP = NM >= 440                  # 410 nm is unreliable under the rail lights
# paint: (well, pigments, pigment + white or None, line colour, marker, earlier run's well)
PAINTS = {
    "yellow": ("H2", ["PY74"], "PY74 50% TiO2", "#eda100", "o", "A1"),
    "red": ("H4", ["PR170 F5RK Liquitex H.Body Artist Colors: 292-Naphthol Crimson",
                   "PR9 Chroma Atelier Interactive: 0032-Napthol Red Light"], None, "#e34948", "s", "A2"),
    "blue": ("H10", ["PB15:3"], "PB15:3 50% TiO2", "#2a78d6", "^", "A3"),
}
# Where each pigment is near-black, and where it is bright, in the AS7341's channels
DARK = {"yellow": (NM >= 440) & (NM <= 470), "red": (NM >= 440) & (NM <= 550), "blue": NM >= 550}
BRIGHT = {"yellow": (NM >= 550) & (NM <= 670), "red": (NM >= 620), "blue": (NM >= 440) & (NM <= 470)}
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
EARLIER = "#8f8c85"


def spectra_of(readings):
    return np.array([[r["channels"][c] for c in CHANNELS] for r in readings], float)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "paint-spaced-2026-09-30.json")
    data = json.load(open(src))
    rd = data["readings"]
    visit = {}
    for r in rd:
        visit.setdefault((r["paint"], r["visit"]), []).append(r)
    vmean = {k: spectra_of(v).mean(axis=0) for k, v in visit.items()}
    well = {p: spectra_of([r for r in rd if r["paint"] == p]).mean(axis=0)
            for p in ("yellow", "red", "blue", "black", "white")}
    W, B = well["white"], well["black"]

    spectra = load_reference()
    rw_all = np.array([per_channel(spectra[k]) for k in WHITES])
    rb_all = np.array([per_channel(spectra[k]) for k in BLACKS])
    rw, rb = rw_all.mean(axis=0), rb_all.mean(axis=0)
    earlier = json.load(open(os.path.join(HERE, "white-black-2026-09-30.json")))

    out = {"source": os.path.basename(src), "channels": CHANNELS,
           "method": "reflectance = R_black + (R_white - R_black) * (paint - black) / (white - black), "
                     "per channel, on the mean of every reading of each well (red: both visits)",
           "r_white_mean": rw.round(3).tolist(), "r_black_mean": rb.round(3).tolist(),
           "mean_counts": {p: v.round(1).tolist() for p, v in well.items()},
           "red_visits": {str(k[1]): vmean[k].round(1).tolist() for k in sorted(vmean) if k[0] == "red"},
           "black_over_white": (B / W).round(3).tolist(),
           "black_over_white_earlier": earlier["black_over_white"],
           "paints": {}}
    print("mean counts per well:")
    print("          " + "".join(f"{n:>8d}" for n in NM))
    for p, v in well.items():
        print(f"  {p:7s} " + "".join(f"{x:>8.0f}" for x in v) + f"   total {v.sum():.0f}")
    print("black / white now     " + " ".join(f"{v:.3f}" for v in B / W))
    print("black / white earlier " + " ".join(f"{v:.3f}" for v in earlier["black_over_white"]))

    # The two checks proposed after the 15:36 run: the black must read below every
    # colour, and the white above every colour, at every channel from 440 to 670 nm.
    above_black = {p: ((well[p] - B) / B) for p in PAINTS}
    vs_white = {p: ((well[p] - W) / W) for p in PAINTS}
    out["paint_above_black_fraction"] = {p: v.round(3).tolist() for p, v in above_black.items()}
    out["paint_minus_white_fraction"] = {p: v.round(3).tolist() for p, v in vs_white.items()}
    out["black_below_every_colour_440_670"] = bool(all((v[KEEP] > 0).all() for v in above_black.values()))
    out["white_above_every_colour_440_670"] = bool(all((v[KEEP] < 0).all() for v in vs_white.values()))
    for p in PAINTS:
        print(f"{p:6s} above the black by {np.round(100 * above_black[p], 1).tolist()} %")
        print(f"{'':6s} vs the white       {np.round(100 * vs_white[p], 1).tolist()} %")
    print("black below every colour at 440-670:", out["black_below_every_colour_440_670"],
          "| white above every colour:", out["white_above_every_colour_440_670"])

    cal, lo, hi = {}, {}, {}
    for p, (w, pigs, tint, _, _, old) in PAINTS.items():
        cal[p] = calibrate(well[p], W, B, rw, rb)
        pure = per_channel(km_mix([spectra[s] for s in pigs]))
        bounds = [per_channel(spectra[s]) for s in pigs] + ([per_channel(spectra[tint])] if tint else [])
        lo[p], hi[p] = np.min(bounds, axis=0), np.max(bounds, axis=0)
        spread = [calibrate(well[p], W, B, a, b) for a in (rw_all.min(0), rw_all.max(0))
                  for b in (rb_all.min(0), rb_all.max(0))]
        miss = outside(cal[p], lo[p], hi[p])[KEEP]
        prev = earlier["paints"][old]
        out["paints"][p] = {
            "well": w, "pigments": pigs, "with_white": tint,
            "reflectance": cal[p].round(3).tolist(),
            "reflectance_low": np.min(spread, axis=0).round(3).tolist(),
            "reflectance_high": np.max(spread, axis=0).round(3).tolist(),
            "reference_pure": pure.round(3).tolist(),
            "reference_low": lo[p].round(3).tolist(),
            "reference_high": hi[p].round(3).tolist(),
            "outside_reference_440_670_mean": round(float(miss.mean()), 3),
            "outside_reference_440_670_max": round(float(miss.max()), 3),
            "channels_inside_reference_440_670": int((miss == 0).sum()),
            "floor_where_pigment_is_dark": round(float(cal[p][DARK[p]].mean()), 3),
            "reference_where_pigment_is_dark": round(float(hi[p][DARK[p]].mean()), 3),
            "excess_where_pigment_is_bright": round(float((cal[p] - hi[p])[BRIGHT[p]].mean()), 3),
            "earlier": {"well": old, "reflectance": prev["reflectance"],
                        "outside_reference_440_670_mean": prev["outside_reference_440_670_mean"],
                        "channels_inside_reference_440_670": prev["channels_inside_reference_440_670"]},
        }
    print("\nreflectance, white/black calibrated; pigment range below:")
    for p in PAINTS:
        o = out["paints"][p]
        print(f"  {p:>6} " + " ".join(f"{v:6.2f}" for v in cal[p]))
        print("         " + " ".join(f"{a:4.2f}-{b:<4.2f}"[:9].rjust(6) for a, b in zip(lo[p], hi[p])))
        print(f"         outside by {o['outside_reference_440_670_mean']:.2f} on average (max "
              f"{o['outside_reference_440_670_max']:.2f}); earlier run "
              f"{o['earlier']['outside_reference_440_670_mean']:.2f}. Floor where the pigment is dark "
              f"{o['floor_where_pigment_is_dark']:.2f} (pigment <= {o['reference_where_pigment_is_dark']:.2f}); "
              f"too bright where it reflects by {o['excess_where_pigment_is_bright']:+.2f}")
    keep_all = np.concatenate([cal[p][KEEP] for p in PAINTS])
    out["calibrated_range_440_670"] = [round(float(keep_all.min()), 2), round(float(keep_all.max()), 2)]
    out["calibrated_range_440_670_earlier"] = earlier["calibrated_range_440_670"]
    print("calibrated range now", out["calibrated_range_440_670"], "earlier",
          out["calibrated_range_440_670_earlier"])

    i440, i620 = list(NM).index(440), list(NM).index(620)
    out["yellow_620_over_440"] = {
        "calibrated": round(float(cal["yellow"][i620] / cal["yellow"][i440]), 1),
        "reference_pure": round(float(out["paints"]["yellow"]["reference_pure"][i620]
                                      / out["paints"]["yellow"]["reference_pure"][i440]), 1),
        "reference_with_white": round(float(hi["yellow"][i620] / hi["yellow"][i440]), 1),
        "earlier_calibrated": earlier["yellow_620_over_440"]["calibrated"]}
    print("yellow 620/440:", out["yellow_620_over_440"])

    # Red's two visits, calibrated separately on the same white and black
    r1, r2 = (calibrate(vmean[("red", k)], W, B, rw, rb) for k in (1, 2))
    out["red_visit2_over_visit1_minus_1"] = (vmean[("red", 2)] / vmean[("red", 1)] - 1).round(3).tolist()
    out["red_calibrated_by_visit"] = {"1": r1.round(3).tolist(), "2": r2.round(3).tolist()}
    print("red visit 2 / visit 1 - 1: " + " ".join(f"{x:+.3f}" for x in out["red_visit2_over_visit1_minus_1"]))

    # Does that change look like the sensor seeing some empty plate in place of
    # red paint? This run read no empty well, so the 15:36 run's A6 stands in.
    empty = np.array(earlier["mean_counts"]["A6"])
    change = (vmean[("red", 2)] - vmean[("red", 1)])[KEEP]
    basis = (empty - vmean[("red", 1)])[KEEP]
    frac = float(change @ basis / (basis @ basis))
    resid = change - frac * basis
    r_sq = 1 - float(resid @ resid) / float(((change - change.mean()) ** 2).sum())
    out["red_change_as_empty_plate"] = {
        "fraction_of_view": round(frac, 3), "r2_440_670": round(r_sq, 3),
        "observed_440_670": change.round(1).tolist(), "fitted_440_670": (frac * basis).round(1).tolist(),
        "empty_plate": "A6 of the 15:36-16:40 run (white-black-2026-09-30.json); this run read no empty well"}
    print(f"red's change = {frac:.2f} of the view traded for empty plate (R^2 {r_sq:.2f}): fitted "
          f"{np.round(frac * basis).tolist()}, observed {np.round(change).tolist()}")

    within = {f"{p}-v{k}": round(float((spectra_of(v).std(axis=0, ddof=1)
                                        / spectra_of(v).mean(axis=0)).max()), 4)
              for (p, k), v in sorted(visit.items())}
    drift = {f"{p}-v{k}": round(float(np.ptp(spectra_of(v).sum(axis=1)) / spectra_of(v).sum(axis=1).mean()), 4)
             for (p, k), v in sorted(visit.items())}
    out["within_visit_max_cv"] = within
    out["within_visit_total_range_fraction"] = drift
    print("within-visit max CV:", within)

    # The ladder at each well: total counts at each step down, and the drop per step
    steps = {}
    for r in data["ladder"]:
        z = r["nozzle"][2] if r.get("nozzle") else None
        if r["label"].startswith("z") and z is not None and z <= 90.0:
            key = f"{r['nozzle'][0]:g}"
            steps.setdefault(key, {}).setdefault(z, []).append(r["total"])
    xs = {"68.38": "H7", "113.38": "H12", "95.38": "H10", "41.38": "H4", "23.38": "H2"}
    out["ladder_totals"] = {}
    for x, zz in steps.items():
        out["ladder_totals"][xs.get(x, x)] = {f"{z:g}": v for z, v in sorted(zz.items(), reverse=True)}
    json.dump(out, open(os.path.join(HERE, "spaced-wells-2026-09-30.json"), "w"), indent=1)
    plot(well, cal, lo, hi, earlier, os.path.join(HERE, "spaced-wells-2026-09-30.png"))


def style(ax, title):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", color=INK, fontsize=10.5, pad=8)
    ax.tick_params(colors=INK2, labelsize=8, length=0)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)


def plot(well, cal, lo, hi, earlier, out):
    fig = plt.figure(figsize=(12, 6.4), facecolor=SURFACE)
    ax = fig.add_subplot(fig.add_gridspec(1, 1, left=0.06, right=0.43, top=0.80, bottom=0.15)[0])
    style(ax, "Each well ÷ the white well (H12)")
    W = well["white"]
    ends = []
    for p, (w, _, _, col, mk, _) in PAINTS.items():
        y = well[p] / W
        ax.plot(NM, y, color=col, marker=mk, ms=6, lw=2, markeredgecolor=SURFACE, markeredgewidth=1.0)
        ends.append([float(y[-1]), f"{w} {p}"])
    y = well["black"] / W
    ax.plot(NM, y, color=INK, marker="D", ms=5.5, lw=2, markeredgecolor=SURFACE, markeredgewidth=1.0)
    ends.append([float(y[-1]), "H7 black"])
    yb = np.array(earlier["black_over_white"])
    ax.plot(NM, yb, color=EARLIER, lw=1.5, ls="--", marker="D", ms=4, markeredgecolor=SURFACE)
    ends.append([float(yb[-1]), "black, 15:47 run\n(A5 ÷ A4)"])
    ends.sort()
    for i in range(1, len(ends)):          # keep the end labels apart
        ends[i][0] = max(ends[i][0], ends[i - 1][0] + 0.045)
    for y_end, label in ends:
        ax.annotate(label, (NM[-1], y_end), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=8.5, color=INK)
    ax.axhline(1.0, color=INK2, lw=1.0)
    ax.text(404, 1.008, "H12 white", fontsize=8, color=INK2, va="bottom")
    ax.set_xticks(NM)
    ax.set_xlim(400, 735)
    ax.set_ylim(0.45, 1.08)
    ax.set_xlabel("AS7341 channel (nm)", color=INK2, fontsize=9)
    ax.set_ylabel("reading ÷ white well", color=INK2, fontsize=9)

    right = fig.add_gridspec(3, 1, left=0.56, right=0.985, top=0.80, bottom=0.15, hspace=0.62)
    for i, (p, (w, _, _, col, mk, old)) in enumerate(PAINTS.items()):
        ax = fig.add_subplot(right[i])
        style(ax, f"{w} {p}")
        ax.axhspan(-0.6, 0, color="#efeeeb", lw=0)
        ax.axhspan(1, 1.8, color="#efeeeb", lw=0)
        ax.fill_between(NM, lo[p], hi[p], color=col, alpha=0.22, lw=0)
        ax.plot(NM, earlier["paints"][old]["reflectance"], color=EARLIER, lw=1.3, ls="--",
                marker=mk, ms=3.5, markeredgecolor=SURFACE)
        ax.plot(NM, cal[p], color=col, lw=2, marker=mk, ms=5.5,
                markeredgecolor=SURFACE, markeredgewidth=1.0)
        ax.set_xticks(NM)
        ax.set_xlim(400, 680)
        ax.set_ylim(-0.5, 1.6)
        ax.set_yticks([0, 0.5, 1, 1.5])
        if i == 0:
            ax.annotate("now", (NM[3], cal[p][3]), xytext=(-34, 14), textcoords="offset points",
                        fontsize=8, color=INK, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
            ax.annotate(f"15:47 run ({old})", (NM[6], earlier["paints"][old]["reflectance"][6]),
                        xytext=(-118, 4), textcoords="offset points", fontsize=8, color=INK2,
                        va="center", arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
        if i == 1:
            ax.set_ylabel("fraction reflected", color=INK2, fontsize=9)
        if i == 2:
            ax.set_xlabel("AS7341 channel (nm)", color=INK2, fontsize=9)
    fig.text(0.548, 0.975, "Calibrated with the white and black wells: now (solid)\n"
             "and in the 15:47 run (dashed), against the pigment\n(shaded). Grey: below 0 or above 1",
             fontsize=10.5, color=INK, va="top")
    fig.text(0.01, 0.975, "What the sensor read (mean of 8 readings per well;\nred 16, over two visits). "
             "The black now reads below\nevery colour; at 15:47 it read lighter than the red and the blue", fontsize=10.5,
             color=INK, va="top")
    fig.text(0.01, 0.012, "2026-09-30, 19:15-19:27 MDT, front row of a fresh plate with empty wells between "
             "the paints; enclosure resting on the plate at nozzle z 86.5, rail lights on. 410 nm is "
             "unreliable under the rail lights.\nPigment spectra: Color Mixing Tools database "
             "(Z. Kovács-Vajna), via rubenwiersma/painting_tools.", fontsize=7.5, color=INK2)
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    print("wrote", out)


if __name__ == "__main__":
    main()
