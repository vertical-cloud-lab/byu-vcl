#!/usr/bin/env python3
"""Two checks behind accuracy-sources-2026-10-02.md, from runs on file (no hardware).

    python3 analyse_source_checks.py

1. Channel tolerance. Every accuracy score on PR #202 (the "miss") compares
   white/black-calibrated readings with published pigment spectra seen through
   Gaussian passbands at the *typical* centre wavelengths of DS000504 v3-00. The
   same datasheet (Figs. 8-15) only guarantees each visible channel's centre to
   typ +/- 10 nm, and our unit's centres have never been measured. So the best
   calibrated runs are re-scored with the passbands moved within those limits:
   all eight channels together (-10 to +10 nm), and each channel on its own
   (uniform in +/- 10 nm, 2,000 draws). The white's and black's published values
   move with the passbands too.

2. Black / white. A zero reference should read near zero: published dried Mars
   black reflects ~2% of what titanium white does. The black well's reading over
   the white well's, board lamp subtracted, says how much of what the sensor sees
   is not the paint in the well. If every well read s + k*R (s: light that
   doesn't depend on the paint; R: the paint's reflectance), then
   black/white = (s + k*Rb) / (s + k*Rw), and s / (s + k*Rw) is the share of the
   white well's reading that is not the white paint. Rb is taken both as the
   published 0.02 and as 0.15, for a watered-down black that looks grey.

Writes source-checks-2026-10-02.json.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from analyse_paint_accuracy import (  # noqa: E402
    CENTRE, FWHM, NM, OFFSET, PAINTS, REF_WL, fit_line, load_reference,
)
from analyse_white_black import BLACKS, WHITES, calibrate, outside  # noqa: E402
from analyse_white_black_correction import KEEP, NAMES, spectra_of  # noqa: E402

TOL = 10.0               # DS000504 Figs. 8-15: centre wavelength min/max = typ -/+ 10 nm
DRAWS = 2000
SHIFTS = (-10, -5, 0, 5, 10)
LAM = np.arange(380, 731, 1.0)
GREY_BLACK = 0.15        # a watered-down black that looks grey, for the second estimate


def per_channel_at(r, centre):
    """Reflectance each channel sees, Gaussian passband at `centre`, even light."""
    fine = np.interp(LAM, REF_WL, r)
    out = []
    for c, f in zip(centre, FWHM):
        w = np.exp(-0.5 * ((LAM - c) / (f / 2.3548)) ** 2)
        out.append(float((fine * w).sum() / w.sum()))
    return np.array(out)


def published_at(spectra, centre):
    ref = {}
    for name, _, pigs, tint in PAINTS.values():
        bounds = [per_channel_at(spectra[p], centre) for p in pigs]
        if tint:
            bounds.append(per_channel_at(spectra[tint], centre))
        lo, hi = np.min(bounds, axis=0), np.max(bounds, axis=0)
        ref[name] = {"lo": lo, "hi": hi, "mid": (lo + hi) / 2}
    rw = np.array([per_channel_at(spectra[k], centre) for k in WHITES]).mean(axis=0)
    rb = np.array([per_channel_at(spectra[k], centre) for k in BLACKS]).mean(axis=0)
    return ref, rw, rb


def score(raw, spectra, centre):
    """Calibrate the raw well means against white and black, then the usual miss and fit."""
    ref, rw, rb = published_at(spectra, centre)
    v = {p: calibrate(raw[p], raw["white"], raw["black"], rw, rb) for p in NAMES}
    miss = np.concatenate([outside(v[p], ref[p]["lo"], ref[p]["hi"])[KEEP] for p in NAMES])
    a, b, _ = fit_line(np.concatenate([ref[p]["mid"][KEEP] for p in NAMES]),
                       np.concatenate([v[p][KEEP] for p in NAMES]))
    return float(miss.mean()), a, 1 / b


def runs():
    """Raw well means (counts) of the calibrated runs on file, by paint."""
    d1 = json.load(open(os.path.join(HERE, "paint-white-black-2026-09-30.json")))
    first = {p: spectra_of([r for r in d1["readings"] if r["well"] == w and r["pass"] == 1]).mean(axis=0)
             for w, p in (("A1", "yellow"), ("A2", "red"), ("A3", "blue"), ("A4", "white"), ("A5", "black"))}
    d2 = json.load(open(os.path.join(HERE, "paint-spaced-2026-09-30.json")))
    spaced = {p: spectra_of([r for r in d2["readings"] if r["paint"] == p]).mean(axis=0)
              for p in NAMES + ("black", "white")}
    h = json.load(open(os.path.join(HERE, "height-series-2026-10-01.json")))
    paint = {"H2": "yellow", "H4": "red", "H10": "blue", "H7": "black", "H12": "white"}

    def at(z):
        rows = [r for r in h["readings"] if r["well"] in paint and r["rail_lights"] == "on"
                and r["visit"] == 1 and r["nozzle"][2] == z]
        return {paint[w]: spectra_of([r for r in rows if r["well"] == w]).mean(axis=0) for w in paint}

    return {
        "2026-09-30 15:47, white and black next to the colours, resting on the plate": (first, False),
        "2026-09-30 19:15, spaced wells, resting on the plate": (spaced, True),
        "2026-10-01, z 125 (foot ~37 mm up)": (at(125.0), True),
        "2026-10-01, z 100 (foot ~12 mm up; best of ten heights)": (at(100.0), True),
        "2026-10-01, z 92 (foot ~4.5 mm up)": (at(92.0), True),
        "2026-10-01, z 86.5 (pressed ~1 mm onto the plate)": (at(86.5), True),
    }


def not_paint_share(ratio, rb, rw):
    """s / (s + k*Rw) from black/white = (s + k*Rb) / (s + k*Rw)."""
    s_over_k = (rb - ratio * rw) / (ratio - 1)
    return s_over_k / (s_over_k + rw)


def main():
    spectra = load_reference()
    rng = np.random.default_rng(20261002)
    draws = rng.uniform(-TOL, TOL, size=(DRAWS, len(CENTRE)))
    nominal, rw0, rb0 = published_at(spectra, CENTRE)

    # 1. How far the published values themselves move within the tolerance.
    move = {}
    for p in NAMES:
        ends = [published_at(spectra, CENTRE + s)[0][p]["mid"] for s in (-TOL, TOL)]
        move[p] = {f"{n} nm": round(float(max(abs(x[i] - nominal[p]["mid"][i]) for x in ends)), 3)
                   for i, n in enumerate(NM)}

    out = {"channels_nm": NM.tolist(), "typical_centres_nm": CENTRE.tolist(), "fwhm_nm": FWHM.tolist(),
           "scored_channels": "440-670 nm, as in every score since 2026-09-30",
           "channel_tolerance": {
               "what": "accuracy scores re-computed with the AS7341 passbands moved within the datasheet's "
                       "centre-wavelength limits (DS000504 v3-00 Figs. 8-15: typ +/- 10 nm)",
               "published_mid_moves_by_up_to": move, "runs": {}},
           "black_over_white": {
               "what": "black well / white well, board lamp subtracted, 440-670 nm; and the share of the "
                       "white well's reading that is not the white paint, if every well reads s + k*R",
               "published_black_over_white": (rb0 / rw0)[KEEP].round(3).tolist(),
               "grey_black_reflectance_assumed": GREY_BLACK, "runs": {}}}

    print("largest move of a published value for a 10 nm shift:")
    for p in NAMES:
        worst = max(move[p], key=move[p].get)
        print(f"  {p:6s} {move[p][worst]:.3f} at {worst}")
    print(f"published black / white, 440-670 nm: {(rb0 / rw0)[KEEP].round(3).tolist()}")

    for name, (raw, scored) in runs().items():
        ratio = ((raw["black"] - OFFSET) / (raw["white"] - OFFSET))[KEEP]
        share_pub = not_paint_share(ratio, rb0[KEEP], rw0[KEEP])
        share_grey = not_paint_share(ratio, np.full_like(ratio, GREY_BLACK), rw0[KEEP])
        out["black_over_white"]["runs"][name] = {
            "black_over_white": ratio.round(2).tolist(),
            "not_paint_share_black_as_published": [round(float(share_pub.min()), 2), round(float(share_pub.max()), 2)],
            "not_paint_share_black_grey": [round(float(share_grey.min()), 2), round(float(share_grey.max()), 2)]}
        b = out["black_over_white"]["runs"][name]
        print(f"{name}\n  black/white {ratio.min():.2f}-{ratio.max():.2f}; not the paint: "
              f"{b['not_paint_share_black_as_published'][0]:.0%}-{b['not_paint_share_black_as_published'][1]:.0%} "
              f"(black grey: {b['not_paint_share_black_grey'][0]:.0%}-{b['not_paint_share_black_grey'][1]:.0%})")
        if not scored:
            continue
        miss0, a0, sq0 = score(raw, spectra, CENTRE)
        common = {f"{s:+d} nm": round(score(raw, spectra, CENTRE + s)[0], 3) for s in SHIFTS}
        mc = np.array([score(raw, spectra, CENTRE + d)[0] for d in draws])
        out["channel_tolerance"]["runs"][name] = {
            "miss_at_typical_centres": round(miss0, 3),
            "black_reads": round(a0, 2), "differences_too_small_by": round(sq0, 2),
            "miss_all_channels_shifted": common,
            "miss_independent_shifts": {"p5": round(float(np.percentile(mc, 5)), 3),
                                        "median": round(float(np.median(mc)), 3),
                                        "p95": round(float(np.percentile(mc, 95)), 3),
                                        "min": round(float(mc.min()), 3), "max": round(float(mc.max()), 3)}}
        r = out["channel_tolerance"]["runs"][name]["miss_independent_shifts"]
        print(f"  miss {miss0:.3f} at typical centres; all shifted {common}; "
              f"independent p5-p95 {r['p5']:.3f}-{r['p95']:.3f} (min {r['min']:.3f}, max {r['max']:.3f})")

    json.dump(out, open(os.path.join(HERE, "source-checks-2026-10-02.json"), "w"), indent=1)
    print("wrote source-checks-2026-10-02.json")


if __name__ == "__main__":
    main()
