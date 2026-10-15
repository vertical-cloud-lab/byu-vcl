#!/usr/bin/env python3
"""How accurate were the 2026-09-30 paint readings? Compare them with what the pigments reflect.

    python3 analyse_paint_accuracy.py [paint-plate-2026-09-30.json]

No hardware. Reads the five full-spectrum readings per well from the paint-plate
JSON (A1 yellow, A2 red, A3 blue, A6 empty) and compares each paint, channel by
channel, with published reflectance spectra of the pigments Liquitex lists for
the three BASICS colours used:

    Primary Yellow            PY74          (arylide yellow)
    Cadmium Red Medium Hue    PR170 + PR9   (naphthol reds)
    Primary Blue              PB15:3        (phthalo blue)

The reference spectra are dried drawdowns, 380-730 nm every 10 nm, from Zsolt
Kovacs-Vajna's Color Mixing Tools database (University of Brescia), as
redistributed in rubenwiersma/painting_tools (CC BY-NC-SA 4.0). They are fetched
from a pinned commit and cached, not copied into this repository. For yellow and
blue the database also has the pigment mixed 1:1 with titanium white; wet
acrylic is milky until it dries, so the wet paint in a well should read
somewhere between the two. For red it has PR170 and PR9 separately, not mixed.

Writes paint-accuracy-2026-09-30.json and paint-accuracy-2026-09-30.png.
"""
import json
import os
import sys
import urllib.request

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CHANNELS = ("ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670")
NM = np.array([int(c[2:]) for c in CHANNELS])
# AS7341 datasheet DS000504 v3-00: centre and FWHM of F1..F8, in nm
CENTRE = np.array([415, 445, 480, 515, 555, 590, 630, 680], float)
FWHM = np.array([26, 30, 36, 39, 39, 40, 50, 52], float)
# Lowest sealed reading of 2026-09-10 per channel: the board's green lamp plus the
# smallest leak seen (results-lights-and-offset-2026-09-10.md). Subtracted from
# paint and empty well alike before dividing.
OFFSET = np.array([4.0, 3.0, 8.0, 160.5, 168.5, 35.0, 16.0, 11.5])

REF_SHA = "72f2ced444c1508dfa13ccf5e5d4e25af83fbc38"
REF_URL = ("https://raw.githubusercontent.com/rubenwiersma/painting_tools/"
           f"{REF_SHA}/painting_tools/measurements/pigments/cmt/pigments.rs")
REF_WL = np.arange(380, 731, 10.0)
PAINTS = {  # well: (label, colour, pure pigment(s), pigment + white or None)
    "A1": ("yellow", "#eda100", ["PY74"], "PY74 50% TiO2"),
    "A2": ("red", "#e34948", ["PR170 F5RK Liquitex H.Body Artist Colors: 292-Naphthol Crimson",
                              "PR9 Chroma Atelier Interactive: 0032-Napthol Red Light"], None),
    "A3": ("blue", "#2a78d6", ["PB15:3"], "PB15:3 50% TiO2"),
}
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"


def load_reference():
    cache = os.path.join(os.path.expanduser("~"), ".cache", "byu-vcl", f"cmt-pigments-{REF_SHA[:7]}.rs")
    if not os.path.exists(cache):
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        urllib.request.urlretrieve(REF_URL, cache)
    spectra = {}
    for line in open(cache, encoding="utf-8", errors="replace"):
        parts = line.rstrip("\n").split("\t")
        vals = [float(v) for v in parts[1:] if v.strip()]
        if len(vals) == len(REF_WL):
            spectra[parts[0].strip().strip('"').strip()] = np.array(vals)
    return spectra


def km_mix(spectra):
    """Equal parts by Kubelka-Munk K/S, the usual single-constant approximation."""
    ks = np.mean([(1 - r) ** 2 / (2 * r) for r in spectra], axis=0)
    return 1 + ks - np.sqrt(ks ** 2 + 2 * ks)


def per_channel(r):
    """Reflectance each AS7341 channel sees, with a Gaussian passband and even light."""
    lam = np.arange(380, 731, 1.0)
    fine = np.interp(lam, REF_WL, r)
    out = []
    for c, f in zip(CENTRE, FWHM):
        w = np.exp(-0.5 * ((lam - c) / (f / 2.3548)) ** 2)
        out.append(float((fine * w).sum() / w.sum()))
    return np.array(out)


def fit_line(x, y):
    a, b = np.linalg.lstsq(np.c_[np.ones_like(x), x], y, rcond=None)[0]
    resid = y - (a + b * x)
    return float(a), float(b), float(1 - (resid ** 2).sum() / ((y - y.mean()) ** 2).sum())


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "paint-plate-2026-09-30.json")
    data = json.load(open(src))
    mean = {w: np.array([[r["channels"][c] for c in CHANNELS] for r in rs], float).mean(axis=0)
            for w, rs in data["readings"].items()}
    blank = mean["A6"] - OFFSET
    spectra = load_reference()

    out = {"source": os.path.basename(src), "channels": CHANNELS,
           "as7341_centre_nm": CENTRE.tolist(), "as7341_fwhm_nm": FWHM.tolist(),
           "offset_subtracted": OFFSET.tolist(),
           "reference": {"what": "Color Mixing Tools database (Zsolt Kovacs-Vajna, University of Brescia), "
                                 "dried drawdowns, via rubenwiersma/painting_tools, CC BY-NC-SA 4.0",
                         "url": REF_URL},
           "paints": {}}
    ratio, lo, hi, pure = {}, {}, {}, {}
    for w, (name, _, pigs, tint) in PAINTS.items():
        ratio[w] = (mean[w] - OFFSET) / blank
        pure[w] = per_channel(km_mix([spectra[p] for p in pigs]))
        bounds = [per_channel(spectra[p]) for p in pigs] + ([per_channel(spectra[tint])] if tint else [])
        lo[w], hi[w] = np.min(bounds, axis=0), np.max(bounds, axis=0)
        out["paints"][w] = {"paint": name, "pigments": pigs, "with_white": tint,
                            "measured_over_empty": ratio[w].round(3).tolist(),
                            "measured_over_empty_no_offset": (mean[w] / mean["A6"]).round(3).tolist(),
                            "reference_pure": pure[w].round(3).tolist(),
                            "reference_low": lo[w].round(3).tolist(),
                            "reference_high": hi[w].round(3).tolist()}

    wells = list(PAINTS)
    floor = np.min([ratio[w] for w in wells], axis=0)
    darkest = [PAINTS[wells[i]][0] for i in np.argmin([ratio[w] for w in wells], axis=0)]
    out["floor"] = {"what": "lowest paint reading at each channel, as a fraction of the empty well",
                    "value": floor.round(3).tolist(), "paint": darkest}
    print("reading / empty well (offset subtracted), and reflectance range of the pigments:")
    print("       " + "".join(f"{n:>13d}" for n in NM))
    for w in wells:
        print(f"{PAINTS[w][0]:>6} " + "".join(f"{v:>13.3f}" for v in ratio[w]))
        print("  ref  " + "".join(f"{a:>6.2f}-{b:<6.2f}" for a, b in zip(lo[w], hi[w])))
    print(" floor " + "".join(f"{v:>13.3f}" for v in floor))

    # One straight line through every paint and channel, 440-670 nm (410 is left out,
    # see the write-up): reading = a + b * reflectance. a is what a black paint would
    # read, a + b what a white one would.
    keep = NM >= 440
    y = np.concatenate([ratio[w][keep] for w in wells])
    fits = {}
    for label, pick in (("pure pigments", lambda w: pure[w]),
                        ("yellow and blue with white", lambda w: hi[w] if PAINTS[w][3] else pure[w])):
        a, b, r2 = fit_line(np.concatenate([pick(w)[keep] for w in wells]), y)
        fits[label] = {"a_black_reads": round(a, 3), "b_slope": round(b, 3),
                       "white_reads": round(a + b, 3), "r2": round(r2, 3)}
        print(f"fit, {label}: black reads {a:.2f}, white reads {a + b:.2f} of the empty well, "
              f"slope {b:.2f}, R^2 {r2:.2f}")
    out["fit_440_670"] = fits

    i440, i620 = list(NM).index(440), list(NM).index(620)
    out["yellow_620_over_440"] = {
        "reference_pure": round(float(pure["A1"][i620] / pure["A1"][i440]), 1),
        "reference_with_white": round(float(hi["A1"][i620] / hi["A1"][i440]), 1),
        "measured": round(float(ratio["A1"][i620] / ratio["A1"][i440]), 2)}
    print("yellow 620/440:", out["yellow_620_over_440"])

    json.dump(out, open(os.path.join(HERE, "paint-accuracy-2026-09-30.json"), "w"), indent=1)
    plot(spectra, ratio, lo, hi, os.path.join(HERE, "paint-accuracy-2026-09-30.png"))


def style(ax, title):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", color=INK, fontsize=10.5, pad=8)
    ax.tick_params(colors=INK2, labelsize=8, length=0)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)


def plot(spectra, ratio, lo, hi, out):
    fig = plt.figure(figsize=(12, 5.8), facecolor=SURFACE)
    ax = fig.add_subplot(fig.add_gridspec(1, 1, left=0.06, right=0.535, top=0.93, bottom=0.12)[0])
    style(ax, "What the three pigments reflect (dried paint, lab-measured)")
    for c, n in zip(CENTRE, NM):
        ax.axvline(c, color="#cfcdc8", lw=0.9, ls=":", zorder=0)
        ax.text(c, 1.02, str(n), ha="center", va="center", fontsize=7.5, color=INK2)
    lam = REF_WL
    for w, (name, col, pigs, tint) in PAINTS.items():
        other = spectra[tint] if tint else spectra[pigs[1]]
        ax.fill_between(lam, spectra[pigs[0]], other, color=col, alpha=0.14, lw=0)
        if tint:
            ax.plot(lam, other, color=col, lw=1.2, ls="--")
        ax.plot(lam, km_mix([spectra[p] for p in pigs]), color=col, lw=2.2)
    arrow = dict(arrowstyle="-", color=INK2, lw=0.8)
    ax.annotate("yellow, PY74: dark below ~500 nm,\nbright from ~550 nm up", (600, 0.81),
                xytext=(412, 0.74), fontsize=8.5, color=INK, arrowprops=arrow)
    ax.annotate("red, PR170 + PR9:\ndark below ~590 nm", (628, 0.55), xytext=(642, 0.36),
                fontsize=8.5, color=INK, arrowprops=arrow)
    ax.annotate("blue, PB15:3: a small peak at\n440-480 nm, dark from ~550 nm up", (462, 0.075),
                xytext=(402, 0.60), fontsize=8.5, color=INK, arrowprops=arrow)
    ax.text(402, 0.93, "solid: pigment alone   dashed: mixed 1:1 with white\n"
            "shaded: in between (red: between PR170 and PR9)", fontsize=7.5, color=INK2, va="center")
    ax.set_xlim(395, 705)
    ax.set_ylim(0, 1.06)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.set_xlabel("wavelength (nm)   ·   dotted lines: the sensor's 8 channels", color=INK2, fontsize=9)
    ax.set_ylabel("fraction of light reflected", color=INK2, fontsize=9)

    right = fig.add_gridspec(3, 1, left=0.595, right=0.985, top=0.835, bottom=0.12, hspace=0.55)
    for i, (w, (name, col, _, _)) in enumerate(PAINTS.items()):
        ax = fig.add_subplot(right[i])
        style(ax, f"{w} {name}")
        ax.fill_between(NM, lo[w], hi[w], color=col, alpha=0.2, lw=0)
        ax.plot(NM, ratio[w], color=col, lw=2, marker="o", ms=5,
                markeredgecolor=SURFACE, markeredgewidth=1.0)
        ax.set_xticks(NM)
        ax.set_xlim(400, 680)
        ax.set_ylim(0, 1.0)
        ax.set_yticks([0, 0.5, 1])
        if i == 1:
            ax.set_ylabel("fraction", color=INK2, fontsize=9)
        if i == 2:
            ax.set_xlabel("AS7341 channel (nm)", color=INK2, fontsize=9)
    fig.text(0.575, 0.975, "What the sensor read (line: paint ÷ empty well)\nagainst the pigment (shaded: range from the left)",
             fontsize=10.5, color=INK, va="top")
    fig.text(0.01, 0.01, "2026-09-30 readings, mean of 5 per well, board lamp offset subtracted. Reference spectra: "
             "Color Mixing Tools database (Z. Kovács-Vajna), via rubenwiersma/painting_tools.",
             fontsize=7.5, color=INK2)
    fig.savefig(out, dpi=150, facecolor=SURFACE)
    print("wrote", out)


if __name__ == "__main__":
    main()
