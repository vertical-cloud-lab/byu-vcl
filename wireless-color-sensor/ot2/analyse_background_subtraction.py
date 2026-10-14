#!/usr/bin/env python3
"""2026-10-14 (evening): read each well empty, add the paint, read it again, subtract.

Asked on PR #202 by @sgbaird (10-10): "testing with an empty well, dispensing,
then measuring again, then subtracting out the first measurement (the
background)". The 10-14 afternoon run read the empty wells but lost the plate
before the paint went in (``results-led-background-2026-10-14.md``). This is
the whole test, with the plate put back and taped down: one enclosure trip
over the empty wells, the paint pipetted in, a second trip over the same wells,
every reading at nozzle z 92 (the foot ~4 mm above the plate, never touching
it), rail lights on, the plate on black paper in slot 7.

    python3 analyse_background_subtraction.py

Reads ``background-subtraction-2026-10-14.json``; writes
``background-subtraction-analysis-2026-10-14.json`` and
``background-subtraction-2026-10-14.png``.

Two ways to turn a painted well's reading into a colour, scored the same way:

    black well (as before)  R = Rb + (Rw - Rb) * (paint - black) / (white - black)
    own empty well (new)    R = Rb + (Rw - Rb) * (paint - empty)  / (white - black)

``paint`` is the well after the paint went in, ``empty`` the same well before,
``black`` and ``white`` the Mars black (H7) and titanium white (H12) wells read
on the same trip as ``paint``. Rw and Rb are the published titanium white and
Mars black per channel (``analyse_white_black.py``). The new way assumes an
empty well over black paper looks like the black paint, which the 10-06 run
found to within 3-8% (``results-black-paper-2026-10-06.md``).

The score is "points off" (``analyse_read_height.py``): how far each paint's
seven channels, 440-670 nm, lie outside the published range of its pigments,
averaged, on a scale where black = 0 and white = 100. Lower is better; 0 is
perfect. 410 nm is left out, as in every score since 09-30.

An empty well (F12) is read on both trips as a control: whatever it changes by
is drift that no subtraction can remove.
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from analyse_paint_accuracy import CHANNELS, NM, OFFSET, load_reference, per_channel  # noqa: E402
from analyse_white_black import BLACKS, WHITES, calibrate, outside  # noqa: E402
from analyse_white_black_correction import KEEP, references  # noqa: E402

DATA = os.path.join(HERE, "background-subtraction-2026-10-14.json")
OUT = os.path.join(HERE, "background-subtraction-analysis-2026-10-14.json")
PNG = os.path.join(HERE, "background-subtraction-2026-10-14.png")
PAINT = {"F3": "yellow", "F6": "red", "F9": "blue"}
CONTROL = "F12"
SURFACE, INK, INK2, MUTED, GRID, BAND = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#d9d7cf"
NEW = "#2a78d6"            # categorical slot 1: the new way
OLD = MUTED                # the way every run since 09-30 has done it


def spectra(data):
    """Mean 8-channel reading per (trip, label), from the ``read`` commands only."""
    g = defaultdict(list)
    for r in data["readings"]:
        if r.get("read_cmd"):
            g[(r["trip"], r["label"])].append([r["channels"][c] for c in CHANNELS])
    return {k: np.array(v, float) for k, v in g.items()}


def mean(g, trip, label):
    return g[(trip, label)].mean(axis=0)


def points(v, ref):
    return round(100 * float(outside(v, ref["lo"], ref["hi"])[KEEP].mean()), 1)


def main():
    data = json.load(open(DATA))
    g = spectra(data)
    s = load_reference()
    ref = references(s)
    rw = np.array([per_channel(s[k]) for k in WHITES]).mean(axis=0)
    rb = np.array([per_channel(s[k]) for k in BLACKS]).mean(axis=0)
    t1, t2 = "trip 1", "trip 2"
    res = {"what": "each well read empty, then painted, at nozzle z 92; the empty reading subtracted",
           "channels": CHANNELS, "scored_nm": NM[KEEP].tolist()}

    # Repeatability: the wells that did not change between the trips
    rep = {}
    for lab in ("black-H7", "white-H12", f"empty-{CONTROL}"):
        if (t1, lab) in g and (t2, lab) in g:
            a, b = mean(g, t1, lab) - OFFSET, mean(g, t2, lab) - OFFSET
            rep[lab] = {"total_trip2_over_trip1": round(float(b.sum() / a.sum()), 4),
                        "largest_channel_change_pct": round(float(100 * np.abs(b / a - 1)[KEEP].max()), 2)}
    res["unchanged_wells"] = rep
    res["repeat_spread_within_a_read_pct"] = {
        f"{k[0]} {k[1]}": round(float(100 * (v.sum(1).max() - v.sum(1).min()) / v.sum(1).mean()), 3)
        for k, v in g.items()}

    # The empty wells, trip 1: how much the background changes from place to place
    B1 = mean(g, t1, "black-H7")
    W1 = mean(g, t1, "white-H12")
    empt = {}
    for w in list(PAINT) + [CONTROL]:
        if (t1, f"empty-{w}") in g:
            e = mean(g, t1, f"empty-{w}")
            empt[w] = {"total": round(float(e.sum()), 1),
                       "over_black": ((e - OFFSET) / (B1 - OFFSET)).round(3).tolist(),
                       "on_white_black_scale": calibrate(e, W1, B1, rw, rb).round(3).tolist(),
                       "on_white_black_scale_mean_440_670": round(float(calibrate(e, W1, B1, rw, rb)[KEEP].mean()), 3)}
    res["empty_wells_trip1"] = {"wells": empt, "black_total": round(float(B1.sum()), 1),
                                "white_total": round(float(W1.sum()), 1)}

    # The painted wells, both ways
    B2, W2 = mean(g, t2, "black-H7"), mean(g, t2, "white-H12")
    paints = {}
    for w, name in PAINT.items():
        lab = f"{name}-{w}"
        if (t2, lab) not in g or (t1, f"empty-{w}") not in g:
            continue
        S, E = mean(g, t2, lab), mean(g, t1, f"empty-{w}")
        old = calibrate(S, W2, B2, rw, rb)
        new = rb + (rw - rb) * (S - E) / (W2 - B2)
        paints[name] = {
            "well": w, "paint_total": round(float(S.sum()), 1), "empty_total": round(float(E.sum()), 1),
            "background_share_of_reading": ((E - OFFSET) / (S - OFFSET)).round(3).tolist(),
            "R_black_well": old.round(3).tolist(), "R_own_empty": new.round(3).tolist(),
            "published_lo": ref[name]["lo"].round(3).tolist(), "published_hi": ref[name]["hi"].round(3).tolist(),
            "points_off_black_well": points(old, ref[name]), "points_off_own_empty": points(new, ref[name]),
            "inside_range_black_well": int((outside(old, ref[name]["lo"], ref[name]["hi"])[KEEP] == 0).sum()),
            "inside_range_own_empty": int((outside(new, ref[name]["lo"], ref[name]["hi"])[KEEP] == 0).sum()),
        }
    res["paints"] = paints
    if paints:
        res["points_off_all"] = {
            "black_well": round(float(np.mean([p["points_off_black_well"] for p in paints.values()])), 1),
            "own_empty": round(float(np.mean([p["points_off_own_empty"] for p in paints.values()])), 1)}
    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=1)
        fh.write("\n")
    chart(res)
    print("unchanged wells:", rep)
    print("empty totals:", {w: e["total"] for w, e in empt.items()}, "black", res["empty_wells_trip1"]["black_total"],
          "white", res["empty_wells_trip1"]["white_total"])
    for name, p in paints.items():
        print(f"{name:6s} points off: black well {p['points_off_black_well']:5.1f}  own empty "
              f"{p['points_off_own_empty']:5.1f}   background share {p['background_share_of_reading']}")
    print("all:", res.get("points_off_all"))


def chart(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    names = list(res["paints"])
    if not names:
        return
    nm = np.array(res["scored_nm"])
    keep = np.isin(NM, nm)
    fig, axes = plt.subplots(1, len(names), figsize=(4.0 * len(names) + 0.4, 4.4), dpi=130, sharey=True,
                             squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    vals = []
    for ax, name in zip(axes[0], names):
        p = res["paints"][name]
        ax.set_facecolor(SURFACE)
        lo, hi = np.array(p["published_lo"])[keep], np.array(p["published_hi"])[keep]
        old, new = np.array(p["R_black_well"])[keep], np.array(p["R_own_empty"])[keep]
        vals += [old, new, lo, hi]
        ax.fill_between(nm, lo, hi, color=BAND, lw=0, label="published range (the target)")
        ax.plot(nm, old, color=OLD, lw=2, ls="--", marker="o", ms=5, label="black well subtracted (as before)")
        ax.plot(nm, new, color=NEW, lw=2, marker="o", ms=5, label="own empty reading subtracted (new)")
        ax.set_title(f"{name} ({p['well']}): points off\n{p['points_off_black_well']:g} black well, "
                     f"{p['points_off_own_empty']:g} own empty", color=INK, fontsize=10, loc="left")
        ax.set_xticks(nm)
        ax.set_xlabel("channel (nm)", color=INK2, fontsize=9)
        ax.axhline(0, color=MUTED, lw=0.8)
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(MUTED)
        ax.tick_params(colors=INK2, labelsize=8)
    v = np.concatenate(vals)
    axes[0][0].set_ylim(min(-0.05, v.min() - 0.05), max(1.0, v.max() + 0.05))
    axes[0][0].set_ylabel("reflectance (black 0, white 1)", color=INK2, fontsize=9)
    h, lab = axes[0][0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=3, frameon=False, fontsize=8.5, labelcolor=INK2)
    fig.suptitle("Each paint read 4 mm above the plate (z 92), two ways. Points off: lower is better, 0 is perfect",
                 color=INK, fontsize=11, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.07, 1, 0.94))
    fig.savefig(PNG, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
