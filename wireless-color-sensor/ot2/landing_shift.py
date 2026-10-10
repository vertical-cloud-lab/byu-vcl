#!/usr/bin/env python3
"""Why did landing on the same well twice read 12% apart? The 2026-10-01 photos.

    python3 landing_shift.py

No hardware. Asked on PR #202: in the 10-01 height series the white well (H12) was
landed on twice in one pick-up, at the same commanded pose, and the second landing
read 12% more light. The write-up guessed the enclosure sat differently on the
nozzle, but its camera check compared whole pixels and called the two landings
identical. This one measures to a hundredth of a pixel.

Every landing in that run starts and ends with a robot-camera photo at nozzle z 125
over the same well, so the photo before and the photo after bracket one landing and
nothing else. For each pair this registers four parts of the scene separately
(high-passed least squares with cubic interpolation):

    enclosure front    the label face, the side the camera sees
    enclosure top      the top face, nozzle pixels left out
    nozzle             the dark pixels of the nozzle above the collar
    tip rack, deck     controls; nothing there moves

and converts each shift to millimetres of upward travel, using the direction and
scale a real Z move has in this camera (the run's own z 125 -> 90 step).

It also checks the light: the second landing's spectrum against the first visit's
at each height, and the near-plate heights re-scored with the second landing's
white, which was read in the same state as the black and the colours.

Photos: photos-2026-10-01/, copied from ~/color-read-1001/enc/ on the Pi.
Writes landing-shift-2026-10-01.json and landing-shift-2026-10-01.png.
"""
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from scipy.ndimage import gaussian_filter, map_coordinates  # noqa: E402
from scipy.optimize import minimize  # noqa: E402
from skimage.feature import match_template  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from analyse_paint_accuracy import CHANNELS, NM, load_reference, per_channel  # noqa: E402
from analyse_white_black import BLACKS, WHITES, calibrate  # noqa: E402
from analyse_white_black_correction import KEEP, references, score  # noqa: E402

PHOTOS = os.path.join(HERE, "photos-2026-10-01")
# In run order. (well, paint, photo at z 125 before the landing, photo at z 125 after it)
LANDINGS = [
    ("H12", "white", "22_over_plate_z125", "34_z125"),
    ("H10", "blue", "35_xy95.38_192.24", "47_z125"),
    ("H7", "black", "48_xy68.38_192.24", "58_z125"),
    ("H5", "empty", "59_xy50.38_192.24", "69_z125"),
    ("H4", "red", "70_xy41.38_192.24", "80_z125"),
    ("H2", "yellow", "81_xy23.38_192.24", "91_z125"),
]
SECOND_H12 = "92_xy113.38_192.24"   # z 125 over H12 again, just before the second landing
# Pixel boxes (x0, y0, x1, y1) on the H12 z 125 photo; moved with the enclosure elsewhere.
TEMPLATE = (255, 145, 355, 250)      # the whole enclosure, to find it over other wells
FRONT = (262, 200, 350, 248)
TOP = (262, 148, 352, 200)
NOZZLE = (300, 120, 360, 172)
CONTROLS = {"tip rack": (382, 242, 528, 338), "deck": (130, 282, 420, 372)}
EXPECT_DX = {"H12": 0, "H10": -20, "H7": -53, "H5": -77, "H4": -89, "H2": -110}
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
RAMP = {88.0: "#86b6ef", 89.0: "#2a78d6", 90.0: "#104281"}   # ordinal blue, light -> dark
SECOND = "#eb6834"


def photo(name):
    return np.asarray(Image.open(os.path.join(PHOTOS, name + "_robot.jpg")).convert("L"), float)


def box_mask(shape, box, dx=0, dy=0):
    x0, y0, x1, y1 = box
    m = np.zeros(shape, bool)
    m[max(0, y0 + dy):max(0, y1 + dy), max(0, x0 + dx):max(0, x1 + dx)] = True
    return m


def register(a, b, mask, guess=(0, 0)):
    """(dx, dy): how far the masked content of photo a sits in photo b, to ~0.01 px."""
    hp = [g - gaussian_filter(g, 6) for g in (gaussian_filter(a, 0.7), gaussian_filter(b, 0.7))]
    ys, xs = np.nonzero(mask)
    ref = hp[0][ys, xs]

    def cost(p):
        return np.mean((ref - map_coordinates(hp[1], [ys + p[1], xs + p[0]], order=3, mode="nearest")) ** 2)

    best = min((minimize(cost, [guess[0] + gx, guess[1] + gy], method="Nelder-Mead",
                         options={"xatol": 1e-3, "fatol": 1e-4})
                for gx in (-1, 0, 1) for gy in (-1, 0, 1)), key=lambda r: r.fun)
    return best.x


def locate(img, template, expect_dx):
    """Offset of the enclosure in img from where it is in the H12 photo, near the expected x."""
    r = match_template(img, template)
    lo = max(0, TEMPLATE[0] + expect_dx - 25)
    sub = r[:, lo:TEMPLATE[0] + expect_dx + 25]
    iy, ix = np.unravel_index(np.argmax(sub), sub.shape)
    return ix + lo - TEMPLATE[0], iy - TEMPLATE[1], float(sub.max())


def parts(before, after, dx, dy, up):
    dark = gaussian_filter(before, 1) < 70
    masks = {"enclosure front": box_mask(before.shape, FRONT, dx, dy),
             "enclosure top": box_mask(before.shape, TOP, dx, dy) & (gaussian_filter(before, 1) >= 90),
             "nozzle": box_mask(before.shape, NOZZLE, dx, dy) & dark}
    masks.update({k: box_mask(before.shape, b) for k, b in CONTROLS.items()})
    out = {}
    for k, m in masks.items():
        s = register(before, after, m)
        mm = float(s @ up / (up @ up))
        out[k] = {"shift_px": [round(float(s[0]), 3), round(float(s[1]), 3)],
                  "mm_up": round(mm, 2), "off_axis_px": round(float(np.hypot(*(s - mm * up))), 2)}
    return out


def main():
    if "--plot" in sys.argv:            # redraw from the saved JSON only
        plot(json.load(open(os.path.join(HERE, "landing-shift-2026-10-01.json"))))
        return
    ref = photo("22_over_plate_z125")
    template = ref[TEMPLATE[1]:TEMPLATE[3], TEMPLATE[0]:TEMPLATE[2]]

    # What 1 mm of upward Z looks like: the label face from z 125 down to z 90, same well.
    z90 = photo("27_z90")
    r = match_template(z90, ref[FRONT[1]:FRONT[3], FRONT[0]:FRONT[2]])
    iy, ix = np.unravel_index(np.argmax(r), r.shape)
    moved = register(ref, z90, box_mask(ref.shape, FRONT), guess=(ix - FRONT[0], iy - FRONT[1]))
    up = -moved / 35.0                 # px per mm of upward travel, at this pose

    out = {"what": "enclosure shift on the nozzle at each landing of the 2026-10-01 height series, "
                   "from robot-camera photos at z 125 before and after; and the light at the two H12 landings",
           "px_per_mm_up": [round(float(v), 3) for v in up], "landings": []}
    for well, paint, b, a in LANDINGS:
        before, after = photo(b), photo(a)
        dx, dy, score_ = locate(before, template, EXPECT_DX[well])
        out["landings"].append({"well": well, "paint": paint, "photos": [b, a],
                                "enclosure_offset_px": [int(dx), int(dy)], "match": round(score_, 2),
                                "parts": parts(before, after, dx, dy, up)})
    out["h12_first_to_second_visit_z125"] = parts(ref, photo(SECOND_H12), 0, 0, up)

    out["light"] = light()
    json.dump(out, open(os.path.join(HERE, "landing-shift-2026-10-01.json"), "w"), indent=1)

    print("1 mm up moves the enclosure (%+.2f, %+.2f) px" % tuple(up))
    print("%-4s %-7s %8s %8s %8s %8s   (mm of upward travel during that landing)"
          % ("well", "paint", "front", "top", "nozzle", "tiprack"))
    for L in out["landings"]:
        p = L["parts"]
        print("%-4s %-7s %8.2f %8.2f %8.2f %8.2f" % (L["well"], L["paint"], p["enclosure front"]["mm_up"],
                                                     p["enclosure top"]["mm_up"], p["nozzle"]["mm_up"],
                                                     p["tip rack"]["mm_up"]))
    p = out["h12_first_to_second_visit_z125"]
    print("H12 first -> second visit: front %.2f top %.2f nozzle %.2f tip rack %.2f mm" % (
        p["enclosure front"]["mm_up"], p["enclosure top"]["mm_up"], p["nozzle"]["mm_up"], p["tip rack"]["mm_up"]))
    lt = out["light"]
    print("second landing at z 86.5 matches the first visit at z %.2f; per channel vs z 89: %s"
          % (lt["second_landing_equals_first_visit_at_z"], lt["second_86.5_over_first_89_per_channel"]))
    for z, v in lt["rescored"].items():
        print("z %-5s miss %.3f (white from 1st landing) -> %.3f (2nd landing)" % (z, v["first"]["miss"], v["second"]["miss"]))
    plot(out)


def light():
    data = json.load(open(os.path.join(HERE, "height-series-2026-10-01.json")))
    by = {}
    for r in data["readings"]:
        if r["well"] and r["rail_lights"] == "on":
            by.setdefault((r["well"], r["visit"], r["nozzle"][2]), []).append([r["channels"][c] for c in CHANNELS])
    mean = {k: np.mean(v, axis=0) for k, v in by.items()}
    v1 = {z: s for (w, v, z), s in mean.items() if w == "H12" and v == 1}
    v2 = {z: s for (w, v, z), s in mean.items() if w == "H12" and v == 2}
    zs = sorted(v1)
    tot = np.array([v1[z].sum() for z in zs])
    equiv = {str(z): round(float(np.interp(v2[z].sum(), tot, zs)), 2) for z in sorted(v2)}
    first = v1[86.5]
    rel = {"second landing, z 86.5": (100 * (v2[86.5] / first - 1)).round(1).tolist()}
    for z in (88.0, 89.0, 90.0):
        rel["first visit, z %g" % z] = (100 * (v1[z] / first - 1)).round(1).tolist()

    spectra = load_reference()
    refs = references(spectra)
    rw = np.array([per_channel(spectra[k]) for k in WHITES]).mean(axis=0)
    rb = np.array([per_channel(spectra[k]) for k in BLACKS]).mean(axis=0)
    colours = {"H2": "yellow", "H4": "red", "H10": "blue"}
    rescored = {}
    for z in (90.0, 89.0, 88.0, 87.0, 86.5):
        rescored[str(z)] = {}
        for name, white in (("first", v1[z]), ("second", v2[z])):
            black = mean[("H7", 1, z)]
            v = {colours[w]: calibrate(mean[(w, 1, z)], white, black, rw, rb) for w in colours}
            s = score(v, refs)
            rescored[str(z)][name] = {
                "miss": round(float(s["miss_mean"]), 3),
                "black_reads": round(float(s["fit_mid"]["a_black_reads"]), 2),
                "brighter_than_white_of_21": int(sum((mean[(w, 1, z)][KEEP] > white[KEEP]).sum() for w in colours))}
    return {"first_landing_total_86.5": round(float(first.sum())), "second_landing_total_86.5": round(float(v2[86.5].sum())),
            "second_landing_equals_first_visit_at_z": equiv["86.5"],
            "second_visit_equivalent_first_visit_z": equiv,
            "second_86.5_over_first_89_per_channel": (v2[86.5] / v1[89.0]).round(3).tolist(),
            "percent_more_light_than_first_landing": rel,
            "rescored": rescored,
            "order_note": "white H12 1st landing 13:51 (before the shift); blue H10 13:55 (during the landing that "
                          "shifted it); black H7, empty H5, red H4, yellow H2 13:58-14:04 and white H12 again 14:06 "
                          "(after)"}


def plot(out):
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "font.family": "DejaVu Sans"})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.3), facecolor=SURFACE,
                                   gridspec_kw={"width_ratios": [1, 1.35], "wspace": 0.28})
    for ax in (ax1, ax2):
        ax.set_facecolor(SURFACE)
        ax.grid(True, axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)

    # 1. How far each landing moved the enclosure's front face, relative to before it.
    L = out["landings"]
    x = np.arange(len(L))
    y = [l["parts"]["enclosure front"]["mm_up"] - l["parts"]["nozzle"]["mm_up"] for l in L]
    ax1.vlines(x, 0, y, color=RAMP[89.0], lw=2, zorder=2)
    ax1.plot(x, y, "o", color=RAMP[89.0], ms=8, mec=SURFACE, mew=1.5, zorder=3)
    ax1.axhline(0, color="#c3c2b7", lw=1, zorder=1)
    k = int(np.argmax(y))
    ax1.annotate(f"{y[k]:.1f} mm", (x[k], y[k]), xytext=(9, -2), textcoords="offset points",
                 color=INK, fontsize=9, va="center")
    ax1.set_xticks(x, [f"{i + 1}. {l['well']}\n{l['paint']}" for i, l in enumerate(L)], fontsize=8)
    ax1.set_ylim(-0.3, 1.0)
    ax1.set_ylabel("enclosure front, up the nozzle (mm)")
    ax1.set_xlabel("landing, in run order (photos at z 125 before and after each)")
    ax1.set_title("Only the landing on H10 moved the enclosure", loc="left", color=INK, fontsize=10.5)

    # 2. The second landing's light, against the first visit hovering at three heights.
    rel = out["light"]["percent_more_light_than_first_landing"]
    for z, col in RAMP.items():
        v = rel["first visit, z %g" % z]
        lab = f"first visit, {z - 87.5:.1f} mm above the plate"
        ax2.plot(NM, v, color=col, lw=2, marker="o", ms=5, zorder=2, label=lab)
        ax2.annotate(lab, (NM[-1], v[-1]), xytext=(7, 0),
                     textcoords="offset points", color=INK2, fontsize=8, va="center")
    v = rel["second landing, z 86.5"]
    ax2.plot(NM, v, color=SECOND, lw=0, marker="D", ms=8, mec=SURFACE, mew=1.5, zorder=3,
             label="second landing, resting on the plate")
    ax2.annotate("second landing,\nresting on the plate", (NM[4], v[4]), xytext=(NM[3] - 12, 5.5),
                 color=INK, fontsize=8.5, arrowprops={"arrowstyle": "-", "color": INK2, "lw": 0.8})
    h, l = ax2.get_legend_handles_labels()
    ax2.legend(h[::-1], l[::-1], frameon=False, fontsize=7.5, loc="upper right")
    ax2.axhline(0, color="#c3c2b7", lw=1, zorder=1)
    ax2.set_xlim(395, 760)
    ax2.set_xticks(NM, [str(int(n)) for n in NM])
    ax2.set_xlabel("channel (nm)")
    ax2.set_ylabel("% more light than the first landing")
    ax2.set_title("After it moved, resting on the white let in as much light as\n"
                  "hovering 1.5 mm above it had", loc="left", color=INK, fontsize=10.5)
    fig.text(0.01, -0.04, "2026-10-01, white well H12, one pick-up, rail lights on. "
             "Data: landing-shift-2026-10-01.json, height-series-2026-10-01.json", color=INK2, fontsize=7.5)
    fig.savefig(os.path.join(HERE, "landing-shift-2026-10-01.png"), dpi=130, facecolor=SURFACE,
                bbox_inches="tight")


if __name__ == "__main__":
    main()
