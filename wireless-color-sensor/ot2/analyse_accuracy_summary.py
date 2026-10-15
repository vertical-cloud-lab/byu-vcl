#!/usr/bin/env python3
"""Every accuracy attempt on one scale, and where each colour stands now.

    python3 analyse_accuracy_summary.py

No hardware. Asked on PR #202 (2026-10-09): the factors that affect accuracy, every
attempt made and how much each helped as a percentage, the current accuracy per colour,
and what is half-tested or untried. This script supplies the numbers;
accuracy-summary-2026-10-09.md has the lists.

The paint runs are re-scored from the calibrated values their own analyses committed,
on the scale used since 2026-09-30 (analyse_white_black_correction.score): 440-670 nm,
each colour's 7 values against its pigments' published range (pigment alone to 1:1 with
titanium white; red PR170 to PR9).

    error     mean distance outside that range, in reflectance (white = 1), as a %
    accuracy  100% - error
    in range  how many of a colour's 7 values fall inside its range; recounted from the
              stored 3-decimal values, so a value on a range's edge can count differently
              from its own analysis (10-06 evening z 95: 7 here, 8 there)

For scale, the same score for a sensor that sees no colour at all: one grey for every
channel of every paint, the grey picked to score best. Picking it with the answers in
hand makes it a floor for a colour-blind sensor, not a typical one.

    09-30 13:25  first paint read, paint / empty A6           white-black-correction-2026-10-01.json
    09-30 15:47  + white A4 and black A5 beside the paints     (runs: before, first_try, second_try)
    09-30 19:15  + empty wells between the paints, slot 1
    10-01        plate in slot 7, cardboard, paint ~19 h old   white-paper-analysis-2026-10-06.json
    10-06 pm     fresh colours, undiluted white/black, white paper   ('10-01/10-06 corrected')
    10-06 eve    black paper                                   black-paper-analysis-2026-10-06.json

All three 09-30 runs read resting on the plate. From 10-01 each run read a ladder of
heights; "above" is the best of z 92, 95 and 100 (foot ~4-12 mm up), and "resting" is
the foot on the plate (z 86.5-87). Where a landing pushed the enclosure up the nozzle,
the scores are the ones those analyses corrected for it (10-01: the second-landing white
when resting; 10-06 evening: the white's second visit, 'direct').

The attempts before paint was in a plate (09-09 and 09-10) were measured in share points
on empty wells; they are quoted from accuracy-provenance.md section 4 and put against the
largest colour signal of the time (2.61 share points). The blackout numbers are quoted
from blackout-2026-10-02.json.

Writes accuracy-summary-2026-10-09.json and accuracy-summary-2026-10-09.png.
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

ABOVE = ("100.0", "95.0", "92.0")              # foot ~4-12 mm above the plate
BRIGHT = {"yellow": (550, 583, 620, 670), "red": (620, 670), "blue": (440, 470)}
SIGNAL_0910 = 2.61                             # largest colour signal before 09-30, share points
SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
ACCENT = "#2a78d6"


def load(name):
    return json.load(open(os.path.join(HERE, name)))


def per_colour(values, ref):
    """Error (%), accuracy (%) and values in range, per colour and overall."""
    out, allm = {}, []
    for p in NAMES:
        m = outside(np.array(values[p], float), ref[p]["lo"], ref[p]["hi"])[KEEP]
        allm.append(m)
        out[p] = {"error_pct": round(100 * float(m.mean()), 1), "accuracy_pct": round(100 - 100 * float(m.mean()), 1),
                  "in_range_of_7": int((m == 0).sum())}
    m = np.concatenate(allm)
    out["all"] = {"error_pct": round(100 * float(m.mean()), 1), "accuracy_pct": round(100 - 100 * float(m.mean()), 1),
                  "in_range_of_21": int((m == 0).sum())}
    return out


def colour_blind(ref):
    """One grey for every channel of every paint, chosen to score best."""
    best = None
    for c in np.round(np.arange(0, 1.0005, 0.001), 3):
        v = {p: np.full(len(NM), c) for p in NAMES}
        e = per_colour(v, ref)
        if best is None or e["all"]["error_pct"] < best[1]["all"]["error_pct"]:
            best = (float(c), e)
    return {"grey": best[0], **best[1]}


def bright_fraction(values, ref):
    """Each colour's own bright channels, as a fraction of the middle of its published range."""
    out = {}
    for p, band in BRIGHT.items():
        i = [list(NM).index(n) for n in band]
        out[p] = {"nm": list(band), "fraction_of_published": np.round(np.array(values[p])[i] / ref[p]["mid"][i], 2).tolist()}
    return out


def change(before, after):
    return round(100 * (after - before) / before, 1)


def main():
    ref = references(load_reference())
    corr = load("white-black-correction-2026-10-01.json")
    wp = load("white-paper-analysis-2026-10-06.json")
    bp = load("black-paper-analysis-2026-10-06.json")
    bo = load("blackout-2026-10-02.json")

    # Every paint run: resting on the plate, and the best of z 92-100 where a ladder was read.
    ladders = {"10-01": lambda z: wp["heights"][z]["10-01 corrected"],
               "10-06 pm": lambda z: wp["heights"][z]["10-06 corrected"],
               "10-06 eve": lambda z: bp["scores"][z]["black paper direct"]}
    resting = {"09-30 13:25": per_colour(corr["runs"]["before"]["values"], ref),
               "09-30 15:47": per_colour(corr["runs"]["first_try"]["values"], ref),
               "09-30 19:15": per_colour(corr["runs"]["second_try"]["values"], ref),
               "10-01": {"all": {"error_pct": round(100 * wp["bottom_10_01"]["second_landing_white"], 1)}},
               "10-06 pm": per_colour(bp["bottom"]["white paper"]["values"], ref),
               "10-06 eve": per_colour(bp["bottom"]["black paper"]["values"], ref)}
    above = {}
    for run, get in ladders.items():
        by_z = {z: per_colour(get(z)["values"], ref) for z in ABOVE}
        z = min(by_z, key=lambda k: by_z[k]["all"]["error_pct"])
        above[run] = {"best_z": float(z), **by_z[z], "by_z": by_z}
    labels = {"09-30 13:25": "first paint reading (paint ÷ empty well)",
              "09-30 15:47": "+ white and black wells beside the paints",
              "09-30 19:15": "+ empty wells between the paints",
              "10-01": "plate moved to slot 7, cardboard, paint dried",
              "10-06 pm": "fresh colours, undiluted white/black, white paper",
              "10-06 eve": "black paper instead of white"}
    runs = [{"run": r, "what": labels[r], "resting": resting[r],
             "above": {k: v for k, v in above[r].items() if k != "by_z"} if r in above else None,
             "above_by_z": above[r]["by_z"] if r in above else None} for r in labels]

    err = lambda r, w="resting": (resting[r] if w == "resting" else above[r])["all"]["error_pct"]  # noqa: E731
    at = lambda r, z: above[r]["by_z"][z]["all"]["error_pct"]  # noqa: E731
    bw = {"10-01": wp["heights"]["100.0"]["10-01 corrected"]["black_over_white_mean_440_670"],
          "10-06 pm": wp["heights"]["100.0"]["10-06 corrected"]["black_over_white_mean_440_670"],
          "10-06 eve": bp["scores"]["100.0"]["black paper direct"]["black_over_white_mean_440_670"]}
    room = bo["outside_light_at_fixed_spots"]["by_stage"]
    sides = [change(room[s]["outside_light_counts"]["none"], room[s]["outside_light_counts"]["sides"])
             for s in ("z93", "z110", "z190")]
    card = [change(room[s]["outside_light_counts"]["sides"], room[s]["outside_light_counts"]["cardboard"])
            for s in ("z93", "z110", "z190")]
    jumps = {row["stage"]: row["max_percent"] for row in bo["two_readings_in_a_row"]}
    steady = {s: max(r["max_percent"] for r in bo["two_readings_in_a_row"] if r["stage"] == s)
              for s in set(jumps)}
    cbe = bo["colour_error_same_wells_same_heights"]

    attempts = [
        # Before paint was in a plate: empty wells, share points, against the 2.61-point signal.
        {"when": "09-09", "what": "read at z 120, not z 128",
         "result": "colour disagreement between stops 55.7% -> 0.8%", "change_pct": change(55.7, 0.8)},
        {"when": "09-10", "what": "rail lights on",
         "result": "5.6x the signal; noise floor 0.338 -> 0.018 share points", "change_pct": change(0.338, 0.018)},
        {"when": "09-10", "what": "reference read at the same spot, height and lights as the sample",
         "result": "avoids errors of 0.30 / 3.12-9.67 / 2.55-2.80 share points (spot / height / lights)",
         "avoided_pct_of_colour_signal": [round(100 * x / SIGNAL_0910) for x in (0.295, 3.12, 9.67, 2.55, 2.80)]},
        {"when": "09-10", "what": "subtract the board's green glow before dividing",
         "result": "residual 0.00 share points: all of it removed", "change_pct": -100.0},
        {"when": "09-10", "what": "nobody near the robot during a reading",
         "result": "avoids 1.40 share points (a forearm moved the total 31.7%)",
         "avoided_pct_of_colour_signal": round(100 * 1.40 / SIGNAL_0910)},
        # With paint in the plate.
        {"when": "09-30", "what": "paint in a 96-well plate instead of vials",
         "result": "largest colour signal 2.61 -> 4.16 share points", "change_pct": change(2.61, 4.16)},
        {"when": "09-30", "what": "robot's sides blacked out",
         "result": "outside light at three fixed spots", "change_pct": [min(sides), max(sides)]},
        {"when": "09-30", "what": "white and black wells beside the paints",
         "result": f"error {err('09-30 13:25')} -> {err('09-30 15:47')}",
         "change_pct": change(err("09-30 13:25"), err("09-30 15:47"))},
        {"when": "09-30", "what": "empty wells between the paints (also new white/black, vials stirred)",
         "result": f"error {err('09-30 15:47')} -> {err('09-30 19:15')}",
         "change_pct": change(err("09-30 15:47"), err("09-30 19:15"))},
        {"when": "10-01", "what": "cardboard and wood over the robot",
         "result": (f"outside light a further {-max(card)}-{-min(card)}% less; biggest jump between two readings "
                    f"{steady['sides']}% -> {steady['cardboard']}%; colour error at z 125 "
                    f"{100 * cbe['125.0']['sides_red_visit_1']['miss']:.0f} -> {100 * cbe['125.0']['cardboard']['miss']:.0f}, "
                    f"resting {100 * cbe['86.5']['sides_red_visit_1']['miss']:.0f} -> "
                    f"{100 * cbe['86.5']['cardboard_rescored_second_white']:.0f}: confounded (slot 1 -> 7, paint aged)"),
         "change_pct": {"outside_light": [min(card), max(card)],
                        "biggest_jump": change(steady["sides"], steady["cardboard"])}},
        {"when": "10-01", "what": "read 4-12 mm above the plate instead of resting on it",
         "result": "; ".join(f"{r}: {err(r)} -> {err(r, 'above')} (z {above[r]['best_z']:.0f})" for r in above),
         "change_pct": [change(err(r), err(r, "above")) for r in above]},
        {"when": "10-01", "what": "more readings per landing",
         "result": "16 readings at one landing agreed within 0.1%", "change_pct": 0.0},
        {"when": "10-02", "what": "board's green LED (checked, left on)",
         "result": "a fixed offset that cancels in the white/black correction", "change_pct": 0.0},
        {"when": "10-06", "what": "fresh colours, undiluted white and black, white paper (all at once)",
         "result": (f"black / white at z 100 {bw['10-01']} -> {bw['10-06 pm']}; error z 100 "
                    f"{at('10-01', '100.0')} -> {at('10-06 pm', '100.0')}, z 92 {at('10-01', '92.0')} -> "
                    f"{at('10-06 pm', '92.0')}, resting {err('10-01')} -> {err('10-06 pm')}"),
         "change_pct": {"black_over_white_z100": change(bw["10-01"], bw["10-06 pm"]),
                        "z100": change(at("10-01", "100.0"), at("10-06 pm", "100.0")),
                        "z92": change(at("10-01", "92.0"), at("10-06 pm", "92.0")),
                        "resting": change(err("10-01"), err("10-06 pm"))}},
        {"when": "10-06", "what": "black paper instead of white",
         "result": (f"black / white at z 100 {bw['10-06 pm']} -> {bw['10-06 eve']}; error z 100 "
                    f"{at('10-06 pm', '100.0')} -> {at('10-06 eve', '100.0')}, z 92 {at('10-06 pm', '92.0')} -> "
                    f"{at('10-06 eve', '92.0')}, resting {err('10-06 pm')} -> {err('10-06 eve')}"),
         "change_pct": {"black_over_white_z100": change(bw["10-06 pm"], bw["10-06 eve"]),
                        "z100": change(at("10-06 pm", "100.0"), at("10-06 eve", "100.0")),
                        "z92": change(at("10-06 pm", "92.0"), at("10-06 eve", "92.0")),
                        "resting": change(err("10-06 pm"), err("10-06 eve"))}},
    ]

    blind = colour_blind(ref)
    now = above["10-06 eve"]["by_z"]
    out = {"what": "every accuracy attempt on one scale, and the current accuracy per colour (2026-10-09)",
           "scale": "error = mean distance outside the published pigment range over 440-670 nm, % of white; "
                    "accuracy = 100% - error",
           "published_range": {p: {"lo": ref[p]["lo"][KEEP].round(3).tolist(), "hi": ref[p]["hi"][KEEP].round(3).tolist(),
                                   "mean_width": round(float((ref[p]["hi"] - ref[p]["lo"])[KEEP].mean()), 3)}
                               for p in NAMES},
           "colour_blind": blind,
           "runs": runs,
           "attempts": attempts,
           "current": {"setup": "10-06 evening: black paper, plate in slot 7, undiluted white H12 and black H7",
                       "resting_on_plate": resting["10-06 eve"],
                       "above_z92_95_100": now,
                       "bright_channels": {z: bright_fraction(bp["scores"][z]["black paper direct"]["values"], ref)
                                           for z in ABOVE},
                       "differences_too_small_by": {z: bp["scores"][z]["black paper direct"]["fit_mid"]
                                                    ["differences_too_small_by"] for z in ABOVE},
                       "shape_matches": bp["scores"]["100.0"]["black paper direct"]["shape_matches"]},
           "first_to_best": {"from": err("09-30 13:25"), "to": err("10-06 eve", "above"),
                             "change_pct": change(err("09-30 13:25"), err("10-06 eve", "above"))}}
    with open(os.path.join(HERE, "accuracy-summary-2026-10-09.json"), "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")

    print(f"colour-blind floor: grey {blind['grey']}, error {blind['all']['error_pct']}% "
          f"(yellow {blind['yellow']['error_pct']}, red {blind['red']['error_pct']}, blue {blind['blue']['error_pct']})")
    for r in runs:
        a = r["above"]
        print(f"{r['run']:12s} resting {r['resting']['all']['error_pct']:5.1f}   "
              + (f"above {a['all']['error_pct']:5.1f} at z {a['best_z']:.0f}" if a else ""))
    print("current, black paper:")
    for p in (*NAMES, "all"):
        cells = "  ".join(f"z{float(z):.0f} {now[z][p]['error_pct']:5.1f}" for z in ABOVE)
        print(f"  {p:6s} resting {resting['10-06 eve'][p]['error_pct']:5.1f}  {cells}")
    for a in attempts:
        print(f"{a['when']}  {a['what']}: {a['result']}  {a.get('change_pct', a.get('avoided_pct_of_colour_signal'))}")
    plot(runs, blind)


def plot(runs, blind):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "font.family": "DejaVu Sans"})
    fig, ax = plt.subplots(figsize=(10, 4.6), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.grid(True, axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)

    y = np.arange(len(runs))[::-1]
    for yi, r in zip(y, runs):
        rest, up = r["resting"]["all"]["error_pct"], r["above"]
        if up:
            ax.plot([up["all"]["error_pct"], rest], [yi, yi], color=GRID, lw=2, zorder=1)
            ax.plot(up["all"]["error_pct"], yi, "o", ms=10, color=ACCENT, mec=SURFACE, mew=1.5, zorder=3)
            ax.annotate(f"{up['all']['error_pct']:.0f}% (z {up['best_z']:.0f})", (up["all"]["error_pct"], yi),
                        xytext=(0, 9), textcoords="offset points", ha="center", color=INK, fontsize=8.5)
        ax.plot(rest, yi, "o", ms=9, mfc=SURFACE, mec=MUTED, mew=2, zorder=3)
        ax.annotate(f"{rest:.0f}%", (rest, yi), xytext=(0, 9), textcoords="offset points", ha="center",
                    color=INK2, fontsize=8.5)

    cb = blind["all"]["error_pct"]
    ax.axvline(cb, color=INK2, lw=1, ls=(0, (4, 3)), zorder=2)
    ax.text(cb - 0.6, y[0] + 0.45, f"colour-blind sensor: {cb:.0f}%\n(the same grey for every paint)",
            color=INK2, fontsize=8, va="center", ha="right")
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r['run']}  {r['what']}" for r in runs], fontsize=8.5, color=INK)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 56)
    ax.set_ylim(-0.6, len(runs) - 0.1)
    ax.set_xlabel("average colour error, % of white (0 = matches the published paint; lower is better)")
    ax.set_title("Colour error in every paint run", loc="left", color=INK, fontsize=11)
    handles = [plt.Line2D([], [], ls="", marker="o", ms=8, mfc=SURFACE, mec=MUTED, mew=2,
                          label="resting on the plate (z 86.5–87)"),
               plt.Line2D([], [], ls="", marker="o", ms=8, color=ACCENT, label="4–12 mm above it (best of z 92, 95, 100)")]
    ax.legend(handles=handles, loc="upper right", bbox_to_anchor=(1.0, 0.78), frameon=False, fontsize=8.5,
              labelcolor=INK2)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "accuracy-summary-2026-10-09.png"), dpi=150, facecolor=SURFACE)


if __name__ == "__main__":
    main()
