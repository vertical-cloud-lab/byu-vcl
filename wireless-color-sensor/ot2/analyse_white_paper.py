#!/usr/bin/env python3
"""Over white paper, with fresh colours and undiluted white and black: did the accuracy change?

    python3 analyse_white_paper.py

No hardware. Asked on PR #202 (2026-10-06): Tim put a sheet of white paper under the
96-well plate and refilled the black (H7) and white (H12) wells with undiluted paint;
the robot refilled the dried colours (H2 yellow, H4 red, H10 blue, 200 uL each) from
the vials. One pick-up then read the five wells at the 2026-10-01 heights, so the two
runs compare height for height. Same plate, same slot (7), same wells, same blackout.

At every height the three colours are calibrated against that height's white and
black, as analyse_height_series.py does:

    reflectance = R_black + (R_white - R_black) * (paint - black) / (white - black)

and scored as analyse_white_black_correction.py does (440-670 nm, 21 values):

    miss       mean distance outside the pigment's published range (0 when inside)
    black      what a perfectly black paint would read (0 is accurate)
    squeeze    how many times too small colour differences come out (1 is accurate)

Also: black / white per channel with the board lamp subtracted (the stray-light floor,
accuracy-sources-2026-10-02.md); how the light changes near the plate; where each well
was touched, from the robot camera (does the enclosure's front face stop following the
nozzle?); and how far each landing moved the enclosure up the nozzle (landing_shift.py's
method, z 125 photos before and after).

Both runs had a landing push the enclosure up the nozzle after the white was read:
~0.5 mm today (the H12 landing itself), ~0.85 mm on 10-01 (the H10 landing). A wall
that sits higher reads like a lower nozzle, so "corrected" rows compare every well in
the shifted state: the white (and, on 10-01, the blue, read before its shift) is taken
from its own ladder at z + shift, interpolated per channel. Only above contact: in
contact the foot rests on the plate and the ladder no longer maps height to light.

Writes white-paper-analysis-2026-10-06.json and white-paper-2026-10-06.png.
"""
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from skimage.feature import match_template  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import landing_shift as LS  # noqa: E402
from analyse_paint_accuracy import CHANNELS, NM, OFFSET, load_reference, per_channel  # noqa: E402
from analyse_white_black import BLACKS, WHITES, calibrate  # noqa: E402
from analyse_white_black_correction import KEEP, references, score  # noqa: E402

HEIGHTS = [125.0, 110.0, 100.0, 95.0, 92.0, 90.0, 89.0, 88.0, 87.0]
ABOVE = [125.0, 110.0, 100.0, 95.0, 92.0, 90.0]        # foot >= ~2 mm off the plate in both runs
COLOURS = {"H2": "yellow", "H4": "red", "H10": "blue"}
WELLS = {"H12": "white", "H10": "blue", "H7": "black", "H4": "red", "H2": "yellow"}
SHIFT = {"10-06": 0.5, "10-01": 0.85}                   # mm up the nozzle; see the docstring
PHOTOS = os.path.join(HERE, "photos-2026-10-06")
UP = np.array([0.518, -0.666])                          # px per mm of upward Z at H12, measured below
# The z 90 photo and the photos below it, per well (robot camera, this run).
CONTACT = {
    "H12": ["25_z90", "26_z89", "27_z88.5", "28_z88", "32_z87.5", "33_z87"],
    "H10": ["40_z90", "41_z89", "42_z88.5", "43_z88", "44_z87.5", "45_z87", "46_z86.5"],
    "H7": ["53_z90", "54_z89", "55_z88", "56_z87", "57_z86.5"],
    "H4": ["64_z90", "65_z89", "66_z88", "67_z87", "68_z86.5"],
    "H2": ["75_z90", "76_z89", "77_z88", "78_z87", "79_z86.5"],
}
LANDINGS = [("H12", "20_over_plate_z125", "34_z125"), ("H10", "35_xy95.38_192.24", "47_z125"),
            ("H7", "48_xy68.38_192.24", "58_z125"), ("H4", "59_xy41.38_192.24", "69_z125"),
            ("H2", "70_xy23.38_192.24", "80_z125")]
SURFACE, INK, INK2, GRID, BEFORE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#8f8c85"
PAINT_COL = {"yellow": "#eda100", "red": "#e34948", "blue": "#2a78d6"}


def spec(rows):
    return np.array([[r["channels"][c] for c in CHANNELS] for r in rows], float).mean(axis=0)


def today_ladders(data):
    """{well: {z: mean spectrum}} above the bottom, first descent where there were two."""
    out = {w: {} for w in WELLS}
    for w in WELLS:
        rows = [r for r in data["readings"] if r["well"] == w and r["stage"] in ("arrive_z125", "ladder")]
        for z in sorted({r["nozzle"][2] for r in rows}, reverse=True):
            at = [r for r in rows if r["nozzle"][2] == z]
            first = [r for r in at if r["pass"] == 1] or at
            out[w][z] = spec(first)
    return out


def today_bottom(data):
    """The eight readings each well got at the bottom of its ladder (H12's second descent)."""
    out = {}
    for w in WELLS:
        rows = [r for r in data["readings"] if r["well"] == w and r["stage"] == "rest8"]
        rows = [r for r in rows if r["nozzle"][2] == min(x["nozzle"][2] for x in rows)]
        out[w] = {"z": rows[0]["nozzle"][2], "mean": spec(rows),
                  "spread_percent": (100 * (np.ptp([[r["channels"][c] for c in CHANNELS] for r in rows], axis=0))
                                     / spec(rows)).round(2).tolist()}
    return out


def oct1_ladders():
    """The 10-01 height series, grouped exactly as analyse_height_series.py groups it."""
    data = json.load(open(os.path.join(HERE, "height-series-2026-10-01.json")))
    lit = [r for r in data["readings"] if r["well"] and r["rail_lights"] == "on"]
    by = {}
    for r in lit:
        by.setdefault((r["well"], r["visit"], r["nozzle"][2]), []).append(r)
    return {w: {z: spec(by[(w, 1, z)]) for (ww, v, z) in by if ww == w and v == 1}
            for w in ("H12", "H10", "H7", "H5", "H4", "H2")}, by


def at(ladder, z):
    """A well's spectrum at height z, linear in z between the heights it was read at."""
    zs = np.array(sorted(ladder))
    sp = np.array([ladder[k] for k in zs])
    if z <= zs[-1]:
        i = max(1, int(np.searchsorted(zs, z)))
        i = min(i, len(zs) - 1)
    else:                                   # just above the top: extend the top segment
        i = len(zs) - 1
    z0, z1 = zs[i - 1], zs[i]
    return sp[i - 1] + (sp[i] - sp[i - 1]) * (z - z0) / (z1 - z0)


def score_at(L, z, rw, rb, ref, shifted=()):
    """Score one height; wells in `shifted` are read at z + their run's shift instead."""
    s = {w: (at(L[w], z + d) if d else L[w][z]) for w, d in shifted} if shifted else {}
    m = {w: s.get(w, L[w][z]) for w in ("H12", "H7", "H2", "H4", "H10")}
    v = {COLOURS[w]: calibrate(m[w], m["H12"], m["H7"], rw, rb) for w in COLOURS}
    out = score(v, ref)
    bw = (m["H7"] - OFFSET) / (m["H12"] - OFFSET)
    out["black_over_white"] = bw.round(3).tolist()
    out["black_over_white_440_670"] = [round(float(bw[KEEP].min()), 2), round(float(bw[KEEP].max()), 2)]
    out["black_over_white_mean_440_670"] = round(float(bw[KEEP].mean()), 3)
    rel = {WELLS[w]: m[w] / m["H12"] for w in COLOURS}
    out["colour_channels_brighter_than_white"] = int(sum((x[KEEP] > 1.0).sum() for x in rel.values()))
    return out


def grey(name):
    return np.asarray(Image.open(os.path.join(PHOTOS, name + "_robot.jpg")).convert("L"), float)


def contact():
    """Below z 90, how much of each commanded step the enclosure's front face followed.

    Registered against the well's own z 90 photo (landing_shift.register, ~0.01 px). A face
    that follows less than 40% of a step is resting on the plate; the nozzle is measured
    as a check that the scale holds at each pose.
    """
    template = LS.photo("27_z90")[LS.FRONT[1] + 23:LS.FRONT[3] + 23, LS.FRONT[0] - 18:LS.FRONT[2] - 18]
    out = {}
    for well, names in CONTACT.items():
        ref = grey(names[0])
        r = match_template(ref, template)
        exp = LS.EXPECT_DX[well] - 18
        lo = max(0, LS.FRONT[0] + exp - 25)
        sub = r[:, lo:LS.FRONT[0] + exp + 25]
        iy, ix = np.unravel_index(np.argmax(sub), sub.shape)
        dx, dy = ix + lo - LS.FRONT[0], iy - LS.FRONT[1]
        face = LS.box_mask(ref.shape, LS.FRONT, dx, dy)
        noz = LS.box_mask(ref.shape, LS.NOZZLE, dx, dy) & (LS.gaussian_filter(ref, 1) < 70)
        steps, prev_z, prev_f = [], 90.0, 0.0
        for n in names[1:]:
            z = float(n.split("_z")[1])
            img = grey(n)
            f = float(LS.register(ref, img, face) @ UP / (UP @ UP))
            nz = float(LS.register(ref, img, noz) @ UP / (UP @ UP))
            steps.append({"z": z, "face_mm": round(f, 2), "nozzle_mm": round(nz, 2),
                          "face_followed": round((prev_f - f) / (prev_z - z), 2)})
            prev_z, prev_f = z, f
        out[well] = {"match": round(float(sub.max()), 2), "offset_px": [int(dx), int(dy)], "steps": steps}
    return out


def landings():
    ref = LS.photo("22_over_plate_z125")         # 10-01's H12 pose, the template landing_shift uses
    template = ref[LS.TEMPLATE[1]:LS.TEMPLATE[3], LS.TEMPLATE[0]:LS.TEMPLATE[2]]
    out = []
    for well, b, a in LANDINGS:
        before, after = grey(b), grey(a)
        dx, dy, sc = LS.locate(before, template, LS.EXPECT_DX[well])
        p = LS.parts(before, after, dx, dy, UP)
        out.append({"well": well, "photos": [b, a], "match": round(sc, 2),
                    **{k: v["mm_up"] for k, v in p.items()}})
    first = LS.parts(ref, grey("20_over_plate_z125"), 0, 0, UP)
    return out, {k: v["mm_up"] for k, v in first.items()}


def main():
    data = json.load(open(os.path.join(HERE, "white-paper-2026-10-06.json")))
    spectra = load_reference()
    ref = references(spectra)
    rw = np.array([per_channel(spectra[k]) for k in WHITES]).mean(axis=0)
    rb = np.array([per_channel(spectra[k]) for k in BLACKS]).mean(axis=0)

    new = today_ladders(data)
    old, by_old = oct1_ladders()
    out = {"what": "the 2026-10-06 run over white paper scored height for height against 2026-10-01",
           "channels": CHANNELS, "heights": {}}
    for z in HEIGHTS:
        row = {"10-06": score_at(new, z, rw, rb, ref)}
        row["10-01"] = score_at(old, z, rw, rb, ref)
        if z in ABOVE:
            row["10-06 corrected"] = score_at(new, z, rw, rb, ref, shifted=[("H12", SHIFT["10-06"])])
            row["10-01 corrected"] = score_at(old, z, rw, rb, ref, shifted=[("H12", SHIFT["10-01"]),
                                                                           ("H10", SHIFT["10-01"])])
        out["heights"][str(z)] = row

    # The bottom: 8 readings per well, foot resting (or nearly) on the plate.
    bot = today_bottom(data)
    m = {w: bot[w]["mean"] for w in WELLS}
    v = {COLOURS[w]: calibrate(m[w], m["H12"], m["H7"], rw, rb) for w in COLOURS}
    b = score(v, ref)
    b["black_over_white"] = ((m["H7"] - OFFSET) / (m["H12"] - OFFSET)).round(3).tolist()
    b["read_z"] = {w: bot[w]["z"] for w in WELLS}
    b["spread_percent_8_readings"] = {w: bot[w]["spread_percent"] for w in WELLS}
    out["bottom_10_06"] = b
    o = score_at(old, 86.5, rw, rb, ref)
    second = np.array([[r["channels"][c] for c in CHANNELS] for r in by_old[("H12", 2, 86.5)]], float).mean(axis=0)
    mo = {w: old[w][86.5] for w in ("H7", "H2", "H4", "H10")}
    vo = {COLOURS[w]: calibrate(mo[w], second, mo["H7"], rw, rb) for w in COLOURS}
    out["bottom_10_01"] = {"as_measured": {k: o[k] for k in ("miss_mean", "fit_mid", "black_over_white_440_670")},
                           "second_landing_white": score(vo, ref)["miss_mean"]}

    # The light near the plate: each well's reading at the bottom over its reading at z 92.
    near = {}
    for w in WELLS:
        near[WELLS[w]] = {"10-06": round(float(bot[w]["mean"].sum() / new[w][92.0].sum()), 3),
                          "10-01": round(float(old[w][86.5].sum() / old[w][92.0].sum()), 3)}
    out["bottom_over_z92_total"] = near
    out["white_z125_total"] = {"10-06": round(float(new["H12"][125.0].sum())),
                               "10-01": round(float(old["H12"][125.0].sum()))}

    out["contact_camera"] = contact()
    lands, vs_oct1 = landings()
    out["landing_shift_mm"] = lands
    out["h12_z125_today_vs_10_01_mm"] = vs_oct1
    json.dump(out, open(os.path.join(HERE, "white-paper-analysis-2026-10-06.json"), "w"), indent=1)

    print(f"{'z':>6s} | {'10-01 miss':>10s} {'black':>6s} {'sq':>5s} {'b/w':>11s} | "
          f"{'10-06 miss':>10s} {'black':>6s} {'sq':>5s} {'b/w':>11s} | corrected 10-01 / 10-06")
    for z in HEIGHTS:
        r = out["heights"][str(z)]
        a, n = r["10-01"], r["10-06"]
        c = (f"{r['10-01 corrected']['miss_mean']:.3f} / {r['10-06 corrected']['miss_mean']:.3f}"
             if "10-01 corrected" in r else "")
        print(f"{z:6.1f} | {a['miss_mean']:10.3f} {a['fit_mid']['a_black_reads']:6.2f} "
              f"{a['fit_mid']['differences_too_small_by']:5.2f} {str(a['black_over_white_440_670']):>11s} | "
              f"{n['miss_mean']:10.3f} {n['fit_mid']['a_black_reads']:6.2f} "
              f"{n['fit_mid']['differences_too_small_by']:5.2f} {str(n['black_over_white_440_670']):>11s} | {c}")
    print("bottom 10-06:", b["miss_mean"], b["fit_mid"], "read at", b["read_z"])
    print("bottom 10-01 (86.5):", out["bottom_10_01"])
    print("bottom / z92 totals:", near)
    for w, c in out["contact_camera"].items():
        print(w, "match", c["match"], [(s["z"], s["face_followed"]) for s in c["steps"]])
    for L in lands:
        print("landing", L["well"], {k: L[k] for k in ("enclosure front", "enclosure top", "nozzle", "tip rack")})
    plot(out, new, old, ref)


def plot(out, new, old, ref):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "font.family": "DejaVu Sans"})
    fig = plt.figure(figsize=(12.5, 8.4), facecolor=SURFACE)
    gs = fig.add_gridspec(2, 3, height_ratios=[1.05, 1], hspace=0.45, wspace=0.3)
    ax1, ax2, ax3 = (fig.add_subplot(gs[0, i]) for i in range(3))
    small = [fig.add_subplot(gs[1, i]) for i in range(3)]
    for ax in (ax1, ax2, ax3, *small):
        ax.set_facecolor(SURFACE)
        ax.grid(True, color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)

    runs = (("10-01 corrected", BEFORE, "s", "--", "10-01, bare deck"),
            ("10-06 corrected", INK, "o", "-", "10-06, white paper"))
    for cor, col, mk, ls, lab in runs:
        z = ABOVE
        ax1.plot(z, [out["heights"][str(k)][cor]["miss_mean"] for k in z], color=col, ls=ls, lw=2,
                 marker=mk, ms=6, mfc=col, mec=col, zorder=3, label=lab)
        ax2.plot(z, [out["heights"][str(k)][cor]["black_over_white_mean_440_670"] for k in z], color=col,
                 ls=ls, lw=2, marker=mk, ms=6, mfc=col, mec=col, zorder=3, label=lab)
    ax1.set_title("Colour error (0 = matches the pigments)", loc="left", color=INK, fontsize=10.5)
    ax1.set_ylabel("mean miss vs published range")
    ax1.set_ylim(0, 0.33)
    ax2.set_title("Black ÷ white (0 is ideal)", loc="left", color=INK, fontsize=10.5)
    ax2.set_ylabel("mean over 440–670 nm, lamp subtracted")
    ax2.set_ylim(0, 0.95)
    ax1.legend(frameon=False, fontsize=8.5, loc="lower right")

    # Each well's light against 10-01's at the same height: which wells changed.
    look = {"H12": ("white", "#b8b5ae", "o", SURFACE), "H7": ("black", INK, "D", INK),
            "H2": ("yellow", PAINT_COL["yellow"], "o", PAINT_COL["yellow"]),
            "H4": ("red", PAINT_COL["red"], "s", PAINT_COL["red"]),
            "H10": ("blue", PAINT_COL["blue"], "^", PAINT_COL["blue"])}
    ax3.axhline(1.0, color=INK2, lw=0.8)
    for w, (lab, col, mk, mfc) in look.items():
        y = [(new[w][k] - OFFSET).sum() / (old[w][k] - OFFSET).sum() for k in ABOVE]
        ax3.plot(ABOVE, y, color=col, lw=2, marker=mk, ms=6, mfc=mfc, mec=col if w != "H12" else INK2, zorder=3)
        nudge = {"H2": 4, "H7": -4}.get(w, 0)        # yellow and black end ~0.007 apart
        ax3.annotate(lab, (ABOVE[0], y[0]), xytext=(6, nudge), textcoords="offset points", va="center",
                     color=INK2, fontsize=8)
    ax3.set_title("Each well's light vs 10-01", loc="left", color=INK, fontsize=10.5)
    ax3.set_ylabel("10-06 ÷ 10-01, total counts (lamp subtracted)")
    for ax in (ax1, ax2, ax3):
        ax.set_xlabel("nozzle z (mm)")
        ax.set_xlim(88.5, 131 if ax is ax3 else 127)

    nm = NM[KEEP]
    for ax, w in zip(small, ("H2", "H4", "H10")):
        p = COLOURS[w]
        col = PAINT_COL[p]
        ax.fill_between(nm, ref[p]["lo"][KEEP], ref[p]["hi"][KEEP], color=GRID, lw=0, label="published range")
        for run, ls, mk, mfc, lab in (("10-01 corrected", "--", "s", SURFACE, "10-01"),
                                      ("10-06 corrected", "-", "o", col, "10-06")):
            v = np.array(out["heights"]["100.0"][run]["values"][p])[KEEP]
            ax.plot(nm, v, color=col, ls=ls, lw=2, marker=mk, ms=5, mfc=mfc, mec=col, label=lab)
        ax.set_ylim(-0.05, 1.15)
        ax.set_xlabel("channel (nm)")
        ax.set_title(f"{p} at z 100: measured vs published", loc="left", color=INK, fontsize=10)
        if w == "H2":
            ax.legend(frameon=False, fontsize=8, loc="lower right")
    small[0].set_ylabel("reflectance after correction")
    fig.text(0.01, 0.005, "Plate in slot 7, rail lights on, OT-2 blacked out; the foot touches the plate at "
             "nozzle z ~87.5-88. Error and black ÷ white corrected for the enclosure riding up the nozzle "
             "mid-run (0.5 mm on 10-06, 0.85 mm on 10-01).\nData: white-paper-2026-10-06.json, "
             "height-series-2026-10-01.json; analyse_white_paper.py",
             color=INK2, fontsize=7.5)
    fig.savefig(os.path.join(HERE, "white-paper-2026-10-06.png"), dpi=130, facecolor=SURFACE,
                bbox_inches="tight")


if __name__ == "__main__":
    main()
