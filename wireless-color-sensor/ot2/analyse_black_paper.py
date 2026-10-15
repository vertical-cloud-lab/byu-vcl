#!/usr/bin/env python3
"""Over black paper instead of white: the same wells at the same heights. Which paints are see-through?

    python3 analyse_black_paper.py

No hardware. Asked on PR #202 (2026-10-06, evening): Tim swapped the white paper under
the 96-well plate for black paper. One pick-up then re-read the afternoon's five wells
(H2 yellow, H4 red, H7 black, H10 blue, H12 white) with the afternoon's arguments and
ladder, and no new paint. Then two visits the afternoon skipped, above the plate only:
the empty H5, and the white H12 a second time.

This is the backing test of ISO 13655 (accuracy-sources-2026-10-02.md): a layer that
hides its backing reads the same over black and over white. Here every well reads less
over the black paper, the opaque white and black included, because the sensor also sees
the clear plate around the well and the paper through it. So the test is per channel,
on the counts each well lost:

    drop(well)   = reading over white paper - reading over black paper
    surround     = mean(drop(white H12), drop(black H7))   both opaque: never through paint
    excess(well) = drop(well) - surround                   light that went through the paint
    share        = excess / (reading over white paper - lamp)

A colour with a share of 0 hid the paper; the larger the share, the more of its reading
over white paper was the paper. Only above the plate (z 125-90). H12 is compared visit 1
with visit 1, before its landing in both runs.

A common surround cancels in the white/black calibration, (paint - black) / (white -
black); the see-through part does not. The scores are computed exactly as
analyse_white_paper.py computes them (440-670 nm, 21 values, published pigment ranges):

    as measured  every well's own reading at that height
    corrected    the white taken from its own ladder at z + the landing shift, because
                 the H12 landing pushed the enclosure up the nozzle before every other
                 well was read: 0.5 mm in the afternoon, 0.85 mm this evening (front face,
                 measured here as in landing_shift.py)
    direct       this evening only: the white from H12's second visit, read in the same
                 state as the other wells, so no shift has to be assumed

Also: the empty H5 over black paper against the black paint; H12's second visit against
its first; where each well was touched (robot camera, as in analyse_white_paper.py);
how far each landing moved the enclosure; and three fixed spots over the base that both
runs read on the way out, to show the light itself had not changed.

Writes black-paper-analysis-2026-10-06.json and black-paper-2026-10-06.png.
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
import analyse_white_paper as AWP  # noqa: E402
import landing_shift as LS  # noqa: E402
from analyse_paint_accuracy import CHANNELS, NM, OFFSET, load_reference, per_channel  # noqa: E402
from analyse_white_black import BLACKS, WHITES, calibrate  # noqa: E402
from analyse_white_black_correction import KEEP, references, score  # noqa: E402

ABOVE = AWP.ABOVE                                   # 125, 110, 100, 95, 92, 90
COLOURS = AWP.COLOURS                               # H2 yellow, H4 red, H10 blue
WELLS = AWP.WELLS                                   # the five paint wells
SHIFT = {"white paper": 0.5, "black paper": 0.85}   # mm up the nozzle at the H12 landing
PHOTOS = os.path.join(HERE, "photos-2026-10-06-black")
UP = AWP.UP
CONTACT = {
    "H12": ["25_z90", "26_z89", "27_z88.5", "28_z88", "29_z87.5", "30_z87"],
    "H10": ["37_z90", "38_z89", "39_z88.5", "40_z88", "41_z87.5", "42_z87", "43_z86.5"],
    "H7": ["50_z90", "51_z89", "52_z88", "53_z87", "54_z86.5"],
    "H4": ["61_z90", "62_z89", "63_z88", "64_z87", "65_z86.5"],
    "H2": ["72_z90", "73_z89", "74_z88", "75_z87", "76_z86.5"],
}
LANDINGS = [("H12", "20_over_plate_z125", "31_z125"), ("H10", "32_xy95.38_192.24", "44_z125"),
            ("H7", "45_xy68.38_192.24", "55_z125"), ("H4", "56_xy41.38_192.24", "66_z125"),
            ("H2", "67_xy23.38_192.24", "77_z125")]
# H12 at z 125 just after its landing, then at the start and end of its second visit.
H12_LATER = ("31_z125", "85_xy113.38_192.24", "91_z125")
FIXED = ("lifted_z93", "up_z110", "carry_start_z190")   # over the base, read by both runs
SURFACE, INK, INK2, GRID = AWP.SURFACE, AWP.INK, AWP.INK2, AWP.GRID
PAINT_COL = AWP.PAINT_COL
WHITE_RUN, BLACK_RUN = "#1baf7a", "#4a3aa7"         # the afternoon, this evening (categorical slots 3, 7)


def spec(rows):
    return AWP.spec(rows)


def ladders(data, visit=1):
    """{well: {z: mean spectrum}} for one visit, over the plate and above the bottom readings."""
    out = {}
    for w in ("H12", "H10", "H7", "H5", "H4", "H2"):
        rows = [r for r in data["readings"] if r["well"] == w and r["stage"] in ("arrive_z125", "ladder")
                and r["pass"] == visit]
        if rows:
            out[w] = {z: spec([r for r in rows if r["nozzle"][2] == z])
                      for z in sorted({r["nozzle"][2] for r in rows}, reverse=True)}
    return out


def fixed_spots(data):
    return {s: round(float(np.mean([r["total"] for r in data["readings"] if r["stage"] == s])), 1)
            for s in FIXED}


def grey(name):
    return np.asarray(Image.open(os.path.join(PHOTOS, name + "_robot.jpg")).convert("L"), float)


def contact():
    """Below z 90, how much of each commanded step the enclosure's front face followed.

    The same method as analyse_white_paper.contact(): registered against the well's own
    z 90 photo; a face that follows less than 40% of a step is resting on the plate.
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
        steps, prev_z, prev_f = [], 90.0, 0.0
        for n in names[1:]:
            z = float(n.split("_z")[1])
            f = float(LS.register(ref, grey(n), face) @ UP / (UP @ UP))
            steps.append({"z": z, "face_mm": round(f, 2),
                          "face_followed": round((prev_f - f) / (prev_z - z), 2)})
            prev_z, prev_f = z, f
        out[well] = {"match": round(float(sub.max()), 2), "steps": steps}
    return out


def landings():
    ref = LS.photo("22_over_plate_z125")          # 10-01's H12 pose, the template landing_shift uses
    template = ref[LS.TEMPLATE[1]:LS.TEMPLATE[3], LS.TEMPLATE[0]:LS.TEMPLATE[2]]
    keep = ("enclosure front", "enclosure top", "nozzle", "tip rack", "deck")
    out = []
    for well, b, a in LANDINGS:
        before, after = grey(b), grey(a)
        dx, dy, sc = LS.locate(before, template, LS.EXPECT_DX[well])
        p = LS.parts(before, after, dx, dy, UP)
        out.append({"well": well, "photos": [b, a], "match": round(sc, 2), **{k: p[k]["mm_up"] for k in keep}})
    # H12 after its landing against its second visit: did anything move in between?
    first = grey(H12_LATER[0])
    dx, dy, _ = LS.locate(first, template, 0)
    later = {}
    for n in H12_LATER[1:]:
        p = LS.parts(first, grey(n), dx, dy, UP)
        later[n] = {k: p[k]["mm_up"] for k in keep}
    afternoon = np.asarray(Image.open(os.path.join(HERE, "photos-2026-10-06", "20_over_plate_z125_robot.jpg"))
                           .convert("L"), float)
    p = LS.parts(afternoon, grey(LANDINGS[0][1]), dx, dy, UP)
    return out, later, {k: p[k]["mm_up"] for k in keep}


def backing(new, old):
    """Per channel, at each height above the plate: what each well lost over black paper."""
    out = {}
    for z in ABOVE:
        drop = {w: old[w][z] - new[w][z] for w in WELLS}
        surround = (drop["H12"] + drop["H7"]) / 2
        row = {"surround_counts": surround.round(0).tolist(),
               "white_drop_minus_black_drop_counts": (drop["H12"] - drop["H7"]).round(0).tolist(),
               "total_ratio": {WELLS[w]: round(float((new[w][z] - OFFSET).sum() / (old[w][z] - OFFSET).sum()), 3)
                               for w in WELLS}}
        for w in COLOURS:
            ex = drop[w] - surround
            share = ex / (old[w][z] - OFFSET)
            row[COLOURS[w]] = {"excess_counts": ex.round(0).tolist(), "share": share.round(3).tolist(),
                               "share_440_670_mean": round(float(share[KEEP].mean()), 3)}
        out[str(z)] = row
    return out


def scores(new, new2, old, rw, rb, ref):
    """Every height, both runs: as measured, corrected for the landing shift, and (tonight) direct."""
    out = {}
    for z in ABOVE:
        direct = {w: dict(v) for w, v in new.items()}
        direct["H12"] = new2["H12"]
        out[str(z)] = {
            "white paper": AWP.score_at(old, z, rw, rb, ref),
            "white paper corrected": AWP.score_at(old, z, rw, rb, ref, shifted=[("H12", SHIFT["white paper"])]),
            "black paper": AWP.score_at(new, z, rw, rb, ref),
            "black paper corrected": AWP.score_at(new, z, rw, rb, ref, shifted=[("H12", SHIFT["black paper"])]),
            "black paper direct": AWP.score_at(direct, z, rw, rb, ref),
        }
    return out


def bottom(data, rw, rb, ref):
    bot = AWP.today_bottom(data)
    m = {w: bot[w]["mean"] for w in WELLS}
    v = {COLOURS[w]: calibrate(m[w], m["H12"], m["H7"], rw, rb) for w in COLOURS}
    b = score(v, ref)
    bw = (m["H7"] - OFFSET) / (m["H12"] - OFFSET)
    b["black_over_white"] = bw.round(3).tolist()
    b["black_over_white_mean_440_670"] = round(float(bw[KEEP].mean()), 3)
    b["read_z"] = {w: bot[w]["z"] for w in WELLS}
    b["colour_channels_brighter_than_white"] = int(sum((m[w][KEEP] > m["H12"][KEEP]).sum() for w in COLOURS))
    return b, m


def main():
    new_d = json.load(open(os.path.join(HERE, "black-paper-2026-10-06.json")))
    old_d = json.load(open(os.path.join(HERE, "white-paper-2026-10-06.json")))
    spectra = load_reference()
    ref = references(spectra)
    rw = np.array([per_channel(spectra[k]) for k in WHITES]).mean(axis=0)
    rb = np.array([per_channel(spectra[k]) for k in BLACKS]).mean(axis=0)

    new, new2 = ladders(new_d, 1), ladders(new_d, 2)
    old = AWP.today_ladders(old_d)
    out = {"what": "the 2026-10-06 evening run over black paper against the same afternoon's run over white paper",
           "channels": CHANNELS,
           "fixed_spots_total": {"white paper": fixed_spots(old_d), "black paper": fixed_spots(new_d)}}
    out["backing"] = backing(new, old)
    out["scores"] = scores(new, new2, old, rw, rb, ref)
    bn, mn = bottom(new_d, rw, rb, ref)
    bo, mo = bottom(old_d, rw, rb, ref)
    out["bottom"] = {"black paper": bn, "white paper": bo,
                     "total_ratio": {WELLS[w]: round(float((mn[w] - OFFSET).sum() / (mo[w] - OFFSET).sum()), 3)
                                     for w in WELLS}}
    # The empty well: what the black paper looks like through the plate, against the black paint.
    out["empty_H5_over_black_paint_H7"] = {str(z): ((new["H5"][z] - OFFSET) / (new["H7"][z] - OFFSET)).round(3).tolist()
                                           for z in ABOVE}
    out["empty_H5_over_white_H12"] = {str(z): ((new["H5"][z] - OFFSET) / (new["H12"][z] - OFFSET)).round(3).tolist()
                                      for z in ABOVE}
    out["H12_second_visit_over_first_total"] = {str(z): round(float((new2["H12"][z] - OFFSET).sum()
                                                                    / (new["H12"][z] - OFFSET).sum()), 3)
                                                for z in ABOVE}
    out["contact_camera"] = contact()
    lands, later, vs_afternoon = landings()
    out["landing_shift_mm"] = lands
    out["H12_after_landing_vs_second_visit_mm"] = later
    out["H12_arrival_vs_afternoon_arrival_mm"] = vs_afternoon
    json.dump(out, open(os.path.join(HERE, "black-paper-analysis-2026-10-06.json"), "w"), indent=1)

    print("fixed spots:", out["fixed_spots_total"])
    print(f"{'z':>6s} | {'white paper':>11s} {'corr':>6s} {'b/w':>6s} | {'black paper':>11s} {'corr':>6s} "
          f"{'direct':>6s} {'b/w':>6s} | by paint (corrected): white paper -> black paper")
    for z in ABOVE:
        s = out["scores"][str(z)]
        w, wc, b, bc, bd = (s[k] for k in ("white paper", "white paper corrected", "black paper",
                                          "black paper corrected", "black paper direct"))
        print(f"{z:6.1f} | {w['miss_mean']:11.3f} {wc['miss_mean']:6.3f} {wc['black_over_white_mean_440_670']:6.3f} | "
              f"{b['miss_mean']:11.3f} {bc['miss_mean']:6.3f} {bd['miss_mean']:6.3f} "
              f"{bd['black_over_white_mean_440_670']:6.3f} | {wc['miss_by_paint']} -> {bd['miss_by_paint']}")
        print(f"{'':6s}   dark floor {wc['dark_floor']} -> {bd['dark_floor']};  black reads "
              f"{wc['fit_mid']['a_black_reads']} -> {bd['fit_mid']['a_black_reads']}")
    print("bottom white paper:", bo["miss_mean"], bo["miss_by_paint"], "b/w", bo["black_over_white_mean_440_670"])
    print("bottom black paper:", bn["miss_mean"], bn["miss_by_paint"], "b/w", bn["black_over_white_mean_440_670"],
          "brighter than white:", bn["colour_channels_brighter_than_white"], "(white paper",
          bo["colour_channels_brighter_than_white"], ")")
    print("bottom total ratio:", out["bottom"]["total_ratio"])
    for z in ("100.0", "92.0"):
        bk = out["backing"][z]
        print(f"z {z}: total ratio {bk['total_ratio']}")
        print("   surround", bk["surround_counts"], " white-black drop", bk["white_drop_minus_black_drop_counts"])
        for p in ("yellow", "red", "blue"):
            print(f"   {p:6s} share {bk[p]['share']}  mean {bk[p]['share_440_670_mean']}")
    print("H5 / H7 at z 100:", out["empty_H5_over_black_paint_H7"]["100.0"])
    print("H12 second / first:", out["H12_second_visit_over_first_total"])
    for w, c in out["contact_camera"].items():
        print(w, "match", c["match"], [(s["z"], s["face_followed"]) for s in c["steps"]])
    for L in lands:
        print("landing", L["well"], {k: L[k] for k in ("enclosure front", "enclosure top", "nozzle", "tip rack")})
    print("H12 after landing -> later:", later)
    print("H12 arrival vs afternoon:", vs_afternoon)
    plot(out, new, new2, old, ref)


def plot(out, new, new2, old, ref):
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

    # Two runs, one per backing: colour plus line style plus marker, and a direct label.
    runs = (("white paper corrected", WHITE_RUN, "s", "--", SURFACE, "white paper\n(afternoon)", 9),
            ("black paper direct", BLACK_RUN, "o", "-", BLACK_RUN, "black paper\n(evening)", -9))
    for key, col, mk, ls, mfc, lab, nudge in runs:
        for ax, metric in ((ax1, "miss_mean"), (ax2, "black_over_white_mean_440_670")):
            y = [out["scores"][str(z)][key][metric] for z in ABOVE]
            ax.plot(ABOVE, y, color=col, ls=ls, lw=2, marker=mk, ms=7, mfc=mfc, mec=col, mew=1.6, zorder=3)
            ax.annotate(lab, (ABOVE[0], y[0]), xytext=(7, nudge), textcoords="offset points", va="center",
                        color=INK2, fontsize=8)
    rest = out["bottom"]
    ax1.text(0.97, 0.96, f"resting on the plate: {rest['white paper']['miss_mean']:.2f} → "
             f"{rest['black paper']['miss_mean']:.2f}", transform=ax1.transAxes, va="top", ha="right", color=INK2,
             fontsize=8)
    ax1.set_title("Colour error (0 = matches the pigments)", loc="left", color=INK, fontsize=10.5)
    ax1.set_ylabel("mean miss vs published range")
    ax1.set_ylim(0, 0.33)
    ax2.set_title("Black ÷ white (0 is ideal)", loc="left", color=INK, fontsize=10.5)
    ax2.set_ylabel("mean over 440–670 nm, lamp subtracted")
    ax2.set_ylim(0, 0.95)
    for ax in (ax1, ax2):
        ax.set_xlabel("nozzle z (mm); the foot touches at ~87.5–88")
        ax.set_xlim(88.5, 137)
        ax.set_xticks([90, 95, 100, 110, 125])

    # The backing test: the share of each colour's reading over white paper that the paper gave.
    nm = NM[KEEP]
    bk = out["backing"]["100.0"]
    ax3.axhline(0, color=INK2, lw=0.8)
    for w in ("H2", "H4", "H10"):
        p = COLOURS[w]
        y = 100 * np.array(bk[p]["share"])[KEEP]
        ax3.plot(nm, y, color=PAINT_COL[p], lw=2, marker="o", ms=6, mfc=PAINT_COL[p], mec=PAINT_COL[p], zorder=3)
        ax3.annotate(f"{p} {100 * bk[p]['share_440_670_mean']:.0f}%", (nm[-1], y[-1]),
                     xytext=(6, {"red": 4, "blue": -4}.get(p, 0)),
                     textcoords="offset points", va="center", color=INK2, fontsize=8)
    ax3.set_title("The paper seen through each paint, z 100", loc="left", color=INK, fontsize=10.5)
    ax3.set_ylabel("% of the colour's reading over white paper")
    ax3.set_xlabel("channel (nm)")
    ax3.set_xlim(425, 735)
    ax3.set_xticks([450, 500, 550, 600, 650])
    ax3.set_ylim(-2, 18)

    for ax, w in zip(small, ("H2", "H4", "H10")):
        p = COLOURS[w]
        col = PAINT_COL[p]
        ax.fill_between(nm, ref[p]["lo"][KEEP], ref[p]["hi"][KEEP], color=GRID, lw=0, label="published range")
        for key, ls, mk, mfc, lab in (("white paper corrected", "--", "s", SURFACE, "white paper"),
                                      ("black paper direct", "-", "o", col, "black paper")):
            v = np.array(out["scores"]["100.0"][key]["values"][p])[KEEP]
            ax.plot(nm, v, color=col, ls=ls, lw=2, marker=mk, ms=5, mfc=mfc, mec=col, label=lab, zorder=3)
        ax.set_ylim(-0.05, 1.15)
        ax.set_xlabel("channel (nm)")
        ax.set_title(f"{p} at z 100: measured vs published", loc="left", color=INK, fontsize=10)
        ax.legend(frameon=False, fontsize=8, loc="upper right" if p != "yellow" else "upper left")
    small[0].set_ylabel("reflectance after white/black correction")
    fig.text(0.01, 0.005, "Plate in slot 7, rail lights on, OT-2 blacked out; same wells, paint and arguments in both "
             "runs. Error and black ÷ white use the white read after the H12 landing pushed the enclosure up the "
             "nozzle (evening: H12's second visit; afternoon: its ladder at z + 0.5 mm).\nData: "
             "black-paper-2026-10-06.json, white-paper-2026-10-06.json; analyse_black_paper.py",
             color=INK2, fontsize=7.5)
    fig.savefig(os.path.join(HERE, "black-paper-2026-10-06.png"), dpi=130, facecolor=SURFACE,
                bbox_inches="tight")


if __name__ == "__main__":
    main()
