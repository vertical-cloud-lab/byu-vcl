#!/usr/bin/env python3
"""Score the paint readings with the AS7341's measured response curves, not Gaussians.

    python3 analyse_response_curves.py          # needs colour-science (pip install colour-science)

No hardware. Asked on PR #202 (2026-10-10): every accuracy score so far compared the
readings with published pigment spectra seen through a Gaussian per channel, at the
datasheet's typical centre and FWHM, under even light (analyse_paint_accuracy.per_channel).
DS000504 v3-00 Figure 19 is the measured response of F1-F8 (diffuser on the package, 256x,
relative to F8's peak), leakage outside each band included: up to 17% of a channel's area
lies in the visible outside +-1 FWHM, and 8-42% above 730 nm. extract_as7341_response.py
reads it out of the PDF's vector paths into as7341-response-fig19.csv (350-1050 nm, 2 nm).

The channel model, on that grid:

    R_k = sum E(l) r_k(l) R(l) / sum E(l) r_k(l)

    r_k   Fig. 19 curve of channel k (Gaussian model: exp(-(l-c)^2 / 2s^2), 380-730 nm)
    E     the light. even: 1 everywhere (what the Gaussian model assumed). LED-B1..B5: the
          CIE 015:2018 phosphor-white LEDs (colour-science), 380-780 nm, 0 outside
    R     a pigment's published reflectance (Color Mixing Tools, 380-730 nm every 10 nm,
          load_reference), held at its end values outside that range (np.interp). Beyond
          730 nm two alternatives say whether the guess matters: R = 0.5, and R = 0.8 x R(730)

Fig. 19 was measured at 256x; our readings are at 128x. The channels' relative
sensitivities are taken as the same at both gains.

Which light: the OT-2's rail lights are white LEDs of unknown spectrum. Each candidate
predicts the white well's counts, sum E r_k R_TiO2 (R_TiO2: the mean of analyse_white_black
.WHITES), up to one overall scale. That is compared with the white H12, board lamp OFFSET
subtracted, in the 10-06 evening black-paper run (its second visit, the white the 'direct'
scores use) at z 92 and z 100; the 10-06 evening first visit, 10-06 afternoon and 10-01 at
the same heights are checks. The scale is fitted in log at 440-670 nm, so 410 nm is a
prediction, not a fit. The light that fits best is "Fig. 19 + LED" below.

Then the published references (lo/hi/mid per paint and channel) and R_white / R_black are
recomputed with each model, and the raw readings re-calibrated exactly as before:

    09-30 runs   as analyse_white_black_correction.main() (before: / empty A6; 1st and
                 2nd try: white/black)
    ladders      10-01 corrected and 10-06 pm corrected (analyse_white_paper.score_at, white
                 at z + landing shift), 10-06 eve direct (analyse_black_paper.scores, the
                 white's second visit), resting (analyse_black_paper.bottom; 10-01: the
                 second-landing white, as analyse_white_paper.main)

and scored as analyse_read_height.row: points off = 100 x the mean distance outside the
published range at 440-670 nm (21 values; black well 0, white well 100), and the fit
reading = a + b x mid. Before any new number is trusted, the Gaussian model is run through
the same code and must reproduce the committed values (read-height-2026-10-09.json,
white-black-correction-2026-10-01.json); the script stops if it does not.

410 nm (F1), left out of every score because yellow read 0.73 there against 0.47 at 440
nm: what each model predicts there against what each run measured, and how much of F1's
signal over the white well comes from outside 390-440 nm. An 8-channel score is reported
as an extra, not in place of the 7-channel one.

Writes response-curves-2026-10-10.json and response-curves-2026-10-10.png.
"""
import json
import os
import sys
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_black_paper as ABP  # noqa: E402
import analyse_white_paper as AWP  # noqa: E402
from analyse_paint_accuracy import (  # noqa: E402
    CENTRE, CHANNELS, FWHM, NM, OFFSET, PAINTS, REF_WL, km_mix, load_reference, per_channel,
)
from analyse_read_height import LADDER, RUNS, row  # noqa: E402
from analyse_white_black import BLACKS, WHITES, calibrate, outside  # noqa: E402
from analyse_white_black_correction import KEEP, NAMES, references, score, spectra_of  # noqa: E402

CSV = "as7341-response-fig19.csv"
LEDS = ("LED-B1", "LED-B2", "LED-B3", "LED-B4", "LED-B5")
LED_CCT = {"LED-B1": 2733, "LED-B2": 2998, "LED-B3": 4103, "LED-B4": 5109, "LED-B5": 6598}  # K, CIE 015:2018
NIR = {"hold": "held at R(730)", "half": "R = 0.5 beyond 730 nm", "dim": "R = 0.8 x R(730) beyond 730 nm"}
F1_BAND = (390.0, 440.0)
PICK = ("10-06 eve z 92", "10-06 eve z 100")      # the white readings the light is picked on
FIG_Z = "92.0"                                     # the height the 410 nm panel shows for the ladders
RUN_COL = {"10-06 eve": "#2a78d6", "10-06 pm": "#eb6834", "10-01": "#1baf7a"}  # analyse_read_height.SERIES
RUN_LABEL = {"10-06 eve": "black paper, 10-06 evening", "10-06 pm": "white paper, 10-06 afternoon",
             "10-01": "bare deck, 10-01"}
PAINT_COL = {"yellow": "#eda100", "red": "#e34948", "blue": "#2a78d6"}
SURFACE, INK, INK2, MUTED, GRID, BAND = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#d9d7cf"


def load(name):
    return json.load(open(os.path.join(HERE, name)))


def fig19():
    d = np.genfromtxt(os.path.join(HERE, CSV), delimiter=",", names=True)
    return d["nm"], np.array([d[f"F{i}"] for i in range(1, 9)])


LAM, RESP = fig19()


def illuminants():
    """{name: E on LAM}, each scaled to a peak of 1; the CIE LEDs are 0 outside 380-780 nm."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import colour
    out = {"even": np.ones_like(LAM)}
    for k in LEDS:
        sd = colour.SDS_ILLUMINANTS[k]
        out[k] = np.interp(LAM, sd.wavelengths, sd.values / sd.values.max(), left=0.0, right=0.0)
    return out


def with_tail(e):
    """An LED continued past 780 nm with the exponential fall of its 730-780 nm stretch."""
    i730, i780 = np.searchsorted(LAM, [730, 780])
    tau = (LAM[i780] - LAM[i730]) / np.log(e[i730] / e[i780])
    out = e.copy()
    out[i780 + 1:] = e[i780] * np.exp(-(LAM[i780 + 1:] - LAM[i780]) / tau)
    return out, float(tau)


def extend(r, nir="hold"):
    """A 380-730 nm spectrum on LAM: end values held, or one of the alternatives beyond 730."""
    fine = np.interp(LAM, REF_WL, r)
    beyond = LAM > REF_WL[-1]
    if nir == "half":
        fine[beyond] = 0.5
    elif nir == "dim":
        fine[beyond] = 0.8 * r[-1]
    return fine


def weighted_model(w, nir="hold"):
    """per_channel() with any 8 x LAM weights (response x light) in place of Gaussians and even light."""
    norm = w.sum(axis=1)
    return lambda r: (w @ extend(r, nir)) / norm


def fig19_model(e, nir="hold"):
    return weighted_model(RESP * e, nir)


def f1_bounds(e, r_white, excess):
    """F1 weights with the white-well light the model misses (excess, a fraction) added inside
    390-440 nm only, or outside it only: the two ends of where that light could be."""
    w = RESP * e
    inside = (LAM >= F1_BAND[0]) & (LAM <= F1_BAND[1])
    t = float(w[0] @ r_white)
    out = {}
    for name, mask in (("extra_inside_390_440", inside), ("extra_outside_390_440", ~inside)):
        ww = w.copy()
        ww[0] = w[0] + excess * t / float((w[0] * mask) @ r_white) * w[0] * mask
        out[name] = ww
    return out


def published(spectra, f):
    """analyse_white_black_correction.references(), R_white and R_black, for any channel model f."""
    ref = {}
    for name, _, pigs, tint in PAINTS.values():
        bounds = [f(spectra[p]) for p in pigs] + ([f(spectra[tint])] if tint else [])
        lo, hi = np.min(bounds, axis=0), np.max(bounds, axis=0)
        pure = f(km_mix([spectra[p] for p in pigs]))
        ref[name] = {"pure": pure, "tinted": f(spectra[tint]) if tint else pure,
                     "lo": lo, "hi": hi, "mid": (lo + hi) / 2}
    rw = np.array([f(spectra[k]) for k in WHITES]).mean(axis=0)
    rb = np.array([f(spectra[k]) for k in BLACKS]).mean(axis=0)
    return ref, rw, rb


def raw_data():
    """Every raw reading the scores start from, grouped as the earlier analyses group them."""
    d0 = load("paint-plate-2026-09-30.json")
    d1 = load("paint-white-black-2026-09-30.json")
    d2 = load("paint-spaced-2026-09-30.json")
    eve_d, pm_d = load("black-paper-2026-10-06.json"), load("white-paper-2026-10-06.json")
    oct1, by_oct1 = AWP.oct1_ladders()
    return {
        "m0": {w: spectra_of(rs).mean(axis=0) for w, rs in d0["readings"].items()},
        "m1": {w: spectra_of([r for r in d1["readings"] if r["well"] == w]).mean(axis=0)
               for w in sorted({r["well"] for r in d1["readings"]})},
        "m2": {p: spectra_of([r for r in d2["readings"] if r["paint"] == p]).mean(axis=0)
               for p in NAMES + ("black", "white")},
        "eve_d": eve_d, "pm_d": pm_d, "eve": ABP.ladders(eve_d, 1), "eve2": ABP.ladders(eve_d, 2),
        "pm": AWP.today_ladders(pm_d), "oct1": oct1,
        "oct1_white2": spectra_of(by_oct1[("H12", 2, 86.5)]).mean(axis=0),
    }


def white_readings(raw):
    """The white H12, board lamp subtracted: the two the light is picked on, then the checks."""
    out = {}
    for z in (92.0, 100.0):
        out[f"10-06 eve z {z:.0f}"] = raw["eve2"]["H12"][z] - OFFSET
    for z in (92.0, 100.0):
        out[f"10-06 eve z {z:.0f}, 1st visit"] = raw["eve"]["H12"][z] - OFFSET
        out[f"10-06 pm z {z:.0f}"] = raw["pm"]["H12"][z] - OFFSET
        out[f"10-01 z {z:.0f}"] = raw["oct1"]["H12"][z] - OFFSET
    return out


def fit_white(measured, predicted):
    """One overall scale, fitted in log at 440-670 nm. Residual per channel (%) and its rms there."""
    k = np.exp(np.mean(np.log(measured[KEEP] / predicted[KEEP])))
    res = 100 * (measured / (k * predicted) - 1)
    return res, float(np.sqrt(np.mean(res[KEEP] ** 2)))


def runs_0930(raw, rw, rb):
    """The three 2026-09-30 runs, calibrated exactly as analyse_white_black_correction.main()."""
    m0, m1, m2 = raw["m0"], raw["m1"], raw["m2"]
    well = {PAINTS[w][0]: w for w in PAINTS}
    return {"before": {p: (m0[well[p]] - OFFSET) / (m0["A6"] - OFFSET) for p in NAMES},
            "first_try": {p: calibrate(m1[well[p]], m1["A4"], m1["A5"], rw, rb) for p in NAMES},
            "second_try": {p: calibrate(m2[p], m2["white"], m2["black"], rw, rb) for p in NAMES}}


def ladder_entries(raw, rw, rb, ref):
    """{run: {"resting": score entry, z: score entry}}, exactly as analyse_read_height's sources."""
    sc = ABP.scores(raw["eve"], raw["eve2"], raw["pm"], rw, rb, ref)
    shift = [("H12", AWP.SHIFT["10-01"]), ("H10", AWP.SHIFT["10-01"])]
    oct1 = raw["oct1"]
    mo = {w: oct1[w][86.5] for w in ("H7", "H2", "H4", "H10")}
    vo = {AWP.COLOURS[w]: calibrate(mo[w], raw["oct1_white2"], mo["H7"], rw, rb) for w in AWP.COLOURS}
    out = {"10-06 eve": {z: sc[z]["black paper direct"] for z in LADDER},
           "10-06 pm": {z: sc[z]["white paper corrected"] for z in LADDER},
           "10-01": {z: AWP.score_at(oct1, float(z), rw, rb, ref, shifted=shift) for z in LADDER}}
    out["10-06 eve"]["resting"] = ABP.bottom(raw["eve_d"], rw, rb, ref)[0]
    out["10-06 pm"]["resting"] = ABP.bottom(raw["pm_d"], rw, rb, ref)[0]
    out["10-01"]["resting"] = score(vo, ref)
    return out


def eight(values, ref):
    """The extra score: points off and fit over all 8 channels (24 values), 410 nm included."""
    v = np.concatenate([np.array(values[p], float) for p in NAMES])
    x = np.concatenate([ref[p]["mid"] for p in NAMES])
    m = np.concatenate([outside(np.array(values[p], float), ref[p]["lo"], ref[p]["hi"]) for p in NAMES])
    a, b = np.linalg.lstsq(np.c_[np.ones_like(x), x], v, rcond=None)[0]
    return {"points_off": round(100 * float(m.mean()), 1), "haze_a": round(float(a), 2),
            "contrast_b": round(float(b), 2)}


def evaluate(spectra, raw, f):
    """Everything one channel model gives: references, the 09-30 runs and the three ladders."""
    ref, rw, rb = published(spectra, f)
    runs = {k: score(v, ref) for k, v in runs_0930(raw, rw, rb).items()}
    lad = ladder_entries(raw, rw, rb, ref)
    rows = {run: {z: row(e, ref) for z, e in lad[run].items()} for run in lad}
    for k, s in runs.items():
        rows.setdefault("09-30", {})[k] = row(s, ref)
    extra = {run: {z: eight(e["values"], ref) for z, e in lad[run].items()} for run in lad}
    extra["09-30"] = {k: eight(s["values"], ref) for k, s in runs.items()}
    entries = {**lad, "09-30": runs}
    line = {run: {z: on_line(e, ref) for z, e in ents.items()} for run, ents in entries.items()}
    return {"ref": ref, "rw": rw, "rb": rb, "rows": rows, "eight": extra, "line410": line, "entries": entries}


def on_line(entry, ref):
    """Does 410 nm sit on the run's own 440-670 nm line (reading = a + b x mid), like the others?"""
    a, b = entry["fit_mid"]["a_black_reads"], entry["fit_mid"]["b_slope"]
    res = {p: np.array(entry["values"][p], float) - (a + b * ref[p]["mid"]) for p in NAMES}
    rms = float(np.sqrt(np.mean(np.concatenate([res[p][KEEP] for p in NAMES]) ** 2)))
    r410 = float(np.sqrt(np.mean([res[p][0] ** 2 for p in NAMES])))
    return {"residual_410": {p: round(float(res[p][0]), 3) for p in NAMES}, "rms_410": round(r410, 3),
            "rms_440_670": round(rms, 3)}


def r3(a):
    return np.round(np.asarray(a, float), 3).tolist()


def check_gaussian(spectra, g):
    """The Gaussian model through this code must give the committed numbers, or nothing here holds."""
    old, _, _ = published(spectra, per_channel)
    same = all(np.array_equal(old[p][k], references(spectra)[p][k]) for p in NAMES for k in old[p])
    rh, wb = load("read-height-2026-10-09.json"), load("white-black-correction-2026-10-01.json")
    diffs = []
    for run in RUNS:
        for z in ("resting",) + LADDER:
            c = rh["runs"][run]["resting"] if z == "resting" else rh["runs"][run]["heights"][z]
            diffs.append(abs(g["rows"][run][z]["points_off"]["all"] - c["points_off"]["all"]))
            if z != "resting" or run != "10-01":
                for p in NAMES:
                    diffs.append(abs(g["rows"][run][z]["points_off"][p] - c["points_off"][p]))
                for k in ("contrast_b", "haze_a", "shape_r2"):
                    diffs.append(abs(g["rows"][run][z][k] - c[k]))
    for k in ("before", "first_try", "second_try"):
        diffs.append(abs(g["rows"]["09-30"][k]["points_off"]["all"] / 100 - wb["runs"][k]["miss_mean"]))
    out = {"references_identical": bool(same), "values_compared": len(diffs),
           "largest_difference": round(float(max(diffs)), 4),
           "black_paper_z92": g["rows"]["10-06 eve"]["92.0"]["points_off"]["all"],
           "black_paper_resting": g["rows"]["10-06 eve"]["resting"]["points_off"]["all"],
           "09_30_miss": [round(g["rows"]["09-30"][k]["points_off"]["all"] / 100, 3)
                          for k in ("before", "first_try", "second_try")]}
    # Points off are re-derived from 3-decimal values, so a committed 0.1 can differ by one rounding step.
    if not same or max(diffs) > 0.051:
        raise SystemExit(f"Gaussian model does not reproduce the committed values: {out}")
    return out


def summary(m):
    """The JSON for one model: what it says each channel sees, and every score."""
    return {"r_white": r3(m["rw"]), "r_black": r3(m["rb"]),
            "reference": {p: {k: r3(m["ref"][p][k]) for k in ("lo", "hi", "mid")} for p in NAMES},
            "points_off_440_670": {run: {z: {"points_off": r["points_off"], "contrast_b": r["contrast_b"],
                                             "haze_a": r["haze_a"], "shape_r2": r["shape_r2"]}
                                         for z, r in rows.items()} for run, rows in m["rows"].items()},
            "eight_channel_extra": m["eight"]}


def share(e, r_white, lo, hi):
    """Share of F1's white-well signal from outside lo-hi nm, from 380-730 nm outside it, above 730."""
    s = RESP[0] * e * r_white
    out_band = (LAM < lo) | (LAM > hi)
    return {"outside": round(float(s[out_band].sum() / s.sum()), 3),
            "visible_outside": round(float(s[out_band & (LAM <= 730)].sum() / s.sum()), 3),
            "above_730": round(float(s[LAM > 730].sum() / s.sum()), 3)}


def band_shares(e, r_white):
    """Per channel, the white well's signal: inside +-1 FWHM, 350-730 nm outside it, above 730 nm."""
    out = {}
    for i, n in enumerate(NM):
        s = RESP[i] * e * r_white
        band = np.abs(LAM - CENTRE[i]) <= FWHM[i]
        out[str(n)] = {"in_band": round(float(s[band].sum() / s.sum()), 3),
                       "visible_outside": round(float(s[~band & (LAM <= 730)].sum() / s.sum()), 3),
                       "above_730": round(float(s[LAM > 730].sum() / s.sum()), 3)}
    return out


def main():
    spectra = load_reference()
    raw = raw_data()
    light = illuminants()

    # 1. Which light: predicted white-well ratios against the counts, one overall scale.
    r_white = np.mean([extend(spectra[k]) for k in WHITES], axis=0)
    whites = white_readings(raw)
    fit = {}
    for name, e in light.items():
        pred = RESP @ (e * r_white)
        per = {k: fit_white(m, pred) for k, m in whites.items()}
        fit[name] = {"rms_pct_440_670_pick": round(float(np.mean([per[k][1] for k in PICK])), 1),
                     "rms_pct_440_670_checks": round(float(np.mean([v[1] for k, v in per.items() if k not in PICK])), 1),
                     "residual_pct": {k: np.round(v[0], 1).tolist() for k, v in per.items()}}
    best = min(LEDS, key=lambda k: fit[k]["rms_pct_440_670_pick"])
    best_checks = min(LEDS, key=lambda k: fit[k]["rms_pct_440_670_checks"])
    print("white well: measured / predicted - 1 (%), scale fitted at 440-670 nm; rms there (pick | checks)")
    print(f"{'':10s}" + "".join(f"{n:>7d}" for n in NM))
    for name in light:
        r = fit[name]["residual_pct"][PICK[0]]
        print(f"{name:10s}" + "".join(f"{v:7.1f}" for v in r)
              + f"   rms {fit[name]['rms_pct_440_670_pick']:5.1f} | {fit[name]['rms_pct_440_670_checks']:5.1f}")
    print(f"best LED on the pick readings: {best}; on the checks: {best_checks}")

    # 2. Every score, three models side by side; the Gaussian one must match what is committed.
    models = {"gaussian": evaluate(spectra, raw, per_channel),
              "fig19_even": evaluate(spectra, raw, fig19_model(light["even"])),
              "fig19_led": evaluate(spectra, raw, fig19_model(light[best]))}
    check = check_gaussian(spectra, models["gaussian"])
    print("Gaussian model reproduces the committed values:", check)
    others = {k: evaluate(spectra, raw, fig19_model(light[k])) for k in LEDS if k != best}

    print("\npoints off (440-670 nm, 0 = inside the published range; black well 0, white well 100)")
    for run in RUNS:
        for key in models:
            rr = models[key]["rows"][run]
            print(f"{run:10s} {key:11s} rest {rr['resting']['points_off']['all']:5.1f} | "
                  + "  ".join(f"z{float(z):.0f} {rr[z]['points_off']['all']:5.1f}" for z in LADDER)
                  + f" | z92 a {rr['92.0']['haze_a']:.2f} b {rr['92.0']['contrast_b']:.2f}")
    for k in ("before", "first_try", "second_try"):
        print(f"09-30 {k:11s} " + "  ".join(
            f"{key} {models[key]['rows']['09-30'][k]['points_off']['all']:5.1f} "
            f"(a {models[key]['rows']['09-30'][k]['haze_a']:.2f}, b {models[key]['rows']['09-30'][k]['contrast_b']:.2f})"
            for key in models))
    for k, m in others.items():
        print(f"{k} (not picked): black paper z92 {m['rows']['10-06 eve']['92.0']['points_off']['all']}, "
              f"resting {m['rows']['10-06 eve']['resting']['points_off']['all']}, "
              f"09-30 2nd try {m['rows']['09-30']['second_try']['points_off']['all']}")

    # How much the guess beyond 730 nm moves things, and an LED tail past 780 nm.
    nir = {}
    tail_e, tau = with_tail(light[best])
    variants = {("fig19_even", v): fig19_model(light["even"], v) for v in ("half", "dim")}
    variants.update({("fig19_led", v): fig19_model(light[best], v) for v in ("half", "dim")})
    variants[("fig19_led", "led_tail")] = fig19_model(tail_e)
    for (key, v), f in variants.items():
        m = evaluate(spectra, raw, f)
        base = models[key]
        dref = max(float(np.abs(m["ref"][p][k] - base["ref"][p][k]).max()) for p in NAMES for k in ("lo", "hi"))
        dpts = {run: max(abs(m["rows"][run][z]["points_off"]["all"] - base["rows"][run][z]["points_off"]["all"])
                         for z in m["rows"][run]) for run in m["rows"]}
        nir.setdefault(key, {})[v] = {
            "what": NIR.get(v, f"LED continued past 780 nm, exponential fall {tau:.0f} nm"),
            "reference_moves_by_up_to": round(dref, 3),
            "r_white_moves_by_up_to": round(float(np.abs(m["rw"] - base["rw"]).max()), 3),
            "r_black_moves_by_up_to": round(float(np.abs(m["rb"] - base["rb"]).max()), 3),
            "points_off_moves_by_up_to": {k: round(x, 1) for k, x in dpts.items()},
            "reference_410_mid_moves_by_up_to": round(float(max(
                abs(m["ref"][p]["mid"][0] - base["ref"][p]["mid"][0]) for p in NAMES)), 3)}
        print(f"{key} {v:8s}: refs move <= {dref:.3f}; points off move <= {max(dpts.values()):.1f} "
              f"({ {k: round(x, 1) for k, x in dpts.items()} })")

    # 3. 410 nm: what each model predicts there, what each run measured, and where F1's light comes from.
    f1 = {"share_of_f1_white_signal_outside_390_440": {
        name: share(e, r_white, *F1_BAND) for name, e in light.items()}}
    f1["share_of_f1_white_signal_outside_390_440"][f"{best} + tail"] = share(tail_e, r_white, *F1_BAND)
    f1["band_shares_white_well"] = {"even": band_shares(light["even"], r_white),
                                    best: band_shares(light[best], r_white)}
    # The white well's F1 reads more than the model predicts; put that light in band or out of it.
    excess = float(np.mean([fit[best]["residual_pct"][k][0] for k in PICK])) / 100
    bounds = {k: evaluate(spectra, raw, weighted_model(w)) for k, w in f1_bounds(light[best], r_white, excess).items()}
    f1["unexplained_f1_light"] = {
        "what": f"the white well's 410 nm reads {100 * excess:.0f}% above {best} x Fig. 19 (scale fitted at "
                "440-670 nm); that light added to F1 inside 390-440 nm only, or outside it only",
        "excess_fraction": round(excess, 3),
        "outside_share_if_inside": round(float(share(light[best], r_white, *F1_BAND)["outside"] / (1 + excess)), 3),
        "outside_share_if_outside": round(float((share(light[best], r_white, *F1_BAND)["outside"] + excess)
                                                / (1 + excess)), 3)}
    picks = {"09-30 before (/ empty)": ("09-30", "before"), "09-30 1st try": ("09-30", "first_try"),
             "09-30 2nd try": ("09-30", "second_try"), "10-06 eve z 92": ("10-06 eve", "92.0"),
             "10-06 eve z 100": ("10-06 eve", "100.0"), "10-06 pm z 100": ("10-06 pm", "100.0"),
             "10-01 z 100": ("10-01", "100.0")}
    measured = {}
    for key, m in {**models, **{f"fig19_led_{k}": v for k, v in bounds.items()}}.items():
        ent = {k: m["entries"][run][z] for k, (run, z) in picks.items()}
        measured[key] = {
            "reference_410": {p: [round(float(m["ref"][p]["lo"][0]), 3), round(float(m["ref"][p]["hi"][0]), 3)]
                              for p in NAMES},
            "reference_440": {p: [round(float(m["ref"][p]["lo"][1]), 3), round(float(m["ref"][p]["hi"][1]), 3)]
                              for p in NAMES},
            "r_white_410": round(float(m["rw"][0]), 3), "r_black_410": round(float(m["rb"][0]), 3),
            "measured_410": {k: {p: round(float(e["values"][p][0]), 3) for p in NAMES} for k, e in ent.items()},
            "measured_410_off_range": {k: {p: round(float(outside(np.array(e["values"][p][:1], float),
                                                                  m["ref"][p]["lo"][:1], m["ref"][p]["hi"][:1])[0]), 3)
                                           for p in NAMES} for k, e in ent.items()},
            "on_the_runs_own_line": {k: m["line410"][run][z] for k, (run, z) in picks.items()},
            "rms_410_over_rms_440_670_all_rows": round(float(np.mean(
                [r["rms_410"] / r["rms_440_670"] for rr in m["line410"].values() for r in rr.values()])), 2)}
    f1["by_model"] = measured
    print("\n410 nm: published range per model, then what the runs read (white/black calibrated; 'before' / empty)")
    for key, mm in measured.items():
        print(f"  {key:38s} R_white {mm['r_white_410']:.3f} ref "
              + "  ".join(f"{p} {lo:.2f}-{hi:.2f}" for p, (lo, hi) in mm["reference_410"].items())
              + f" | 410 off its run's line / others: {mm['rms_410_over_rms_440_670_all_rows']:.2f}")
        for k, v in mm["measured_410"].items():
            ln = mm["on_the_runs_own_line"][k]
            print(f"      {k:22s} " + "  ".join(f"{p} {x:5.2f} (off {mm['measured_410_off_range'][k][p]:.2f})"
                                                for p, x in v.items())
                  + f" | line: 410 rms {ln['rms_410']:.2f}, 440-670 rms {ln['rms_440_670']:.2f}")
    for name, sh in f1["share_of_f1_white_signal_outside_390_440"].items():
        print(f"  F1 over the white well, {name:14s}: {sh['outside']:.0%} from outside 390-440 nm "
              f"({sh['visible_outside']:.0%} visible, {sh['above_730']:.0%} above 730 nm)")
    print("  unexplained F1 light:", f1["unexplained_f1_light"])
    diff8 = {key: [m["eight"][run][z]["points_off"] - m["rows"][run][z]["points_off"]["all"]
                   for run in m["eight"] for z in m["eight"][run]] for key, m in models.items()}
    f1["eight_minus_seven_points_off"] = {
        key: {"mean": round(float(np.mean(d)), 1), "min": round(float(min(d)), 1), "max": round(float(max(d)), 1)}
        for key, d in diff8.items()}
    print("  8-channel minus 7-channel points off, every run and height:", f1["eight_minus_seven_points_off"])

    out = {"what": "the paint scores recomputed with the AS7341's measured response (DS000504 v3-00 Fig. 19) "
                   "instead of Gaussian passbands, under even light and under a CIE white LED",
           "response_curves": {"source": "DS000504 v3-00 Figure 19, diffuser on package, F1-F8 at 256x, relative "
                                         "to F8's peak; extracted by extract_as7341_response.py", "csv": CSV,
                               "peak_relative_to_f8": r3(RESP.max(axis=1)),
                               "peak_nm": LAM[RESP.argmax(axis=1)].round(0).tolist()},
           "assumptions": {
               "gain": "Fig. 19 is at 256x, the readings at 128x; relative channel sensitivities taken as "
                       "gain-independent",
               "pigments_outside_380_730": "held at the end values; alternatives beyond 730 nm in nir_extrapolation",
               "leds": "CIE 015:2018 LED-B1..B5 from colour-science SDS_ILLUMINANTS, 380-780 nm, 0 outside",
               "units": "E and Fig. 19 both taken as per unit energy, so no wavelength weighting"},
           "illuminant_fit": {"what": "white H12 counts minus the board lamp offset against sum E r_k R_TiO2, one "
                                      "overall scale fitted in log at 440-670 nm; residual = measured / predicted - 1, "
                                      "%, all 8 channels (410 predicted, not fitted)",
                              "picked_on": list(PICK), "cct_k": LED_CCT,
                              "white_counts_minus_offset": {k: np.round(v, 1).tolist() for k, v in whites.items()},
                              "by_illuminant": fit, "best": best, "best_on_checks": best_checks},
           "gaussian_reproduces_committed": check,
           "models": {"gaussian": {"what": "Gaussian at the typical centre and FWHM, even light, 380-730 nm "
                                           "(analyse_paint_accuracy.per_channel)", **summary(models["gaussian"])},
                      "fig19_even": {"what": "Fig. 19 curves, even light 350-1050 nm", **summary(models["fig19_even"])},
                      "fig19_led": {"what": f"Fig. 19 curves, CIE {best}", "illuminant": best,
                                    **summary(models["fig19_led"])}},
           "other_leds": {k: {"points_off_all": {run: {z: r["points_off"]["all"] for z, r in rows.items()}
                                                 for run, rows in m["rows"].items()}} for k, m in others.items()},
           "nir_extrapolation": nir, "f1_410": f1}
    with open(os.path.join(HERE, "response-curves-2026-10-10.json"), "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    chart(out, models, light[best], best)


def tidy(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def chart(out, models, e_best, best):
    plt.rcParams.update({"font.size": 9, "font.family": "DejaVu Sans", "axes.edgecolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK2})
    fig = plt.figure(figsize=(12.5, 9.2), facecolor=SURFACE)
    top = fig.add_gridspec(1, 2, left=0.065, right=0.985, top=0.885, bottom=0.555, wspace=0.2,
                           width_ratios=[1.75, 1])
    bot = fig.add_gridspec(1, 3, left=0.065, right=0.985, top=0.39, bottom=0.105, wspace=0.08)

    # (a) The curves: measured response, log scale so the leakage shows, against the Gaussians.
    ax = fig.add_subplot(top[0])
    tidy(ax)
    ax.fill_between(LAM, 1e-4, np.maximum(e_best, 1e-4), color="#efe6cf", lw=0, zorder=0)
    ax.text(1040, 0.3, f"shaded: white LED, CIE {best}, standing in\nfor the rail lights (peak scaled to 1)",
            color=INK2, fontsize=8, ha="right", va="bottom")
    lam_g = np.arange(380, 731, 1.0)
    for i in range(8):
        f1 = i == 0
        g = RESP[i].max() * np.exp(-0.5 * ((lam_g - CENTRE[i]) / (FWHM[i] / 2.3548)) ** 2)
        ax.plot(lam_g, np.where(g > 1e-3, g, np.nan), color=INK if f1 else MUTED, lw=1.3 if f1 else 0.9,
                ls=(0, (3, 2)), zorder=2)
        r = np.where(RESP[i] > 0, RESP[i], np.nan)
        ax.plot(LAM, r, color=INK if f1 else "#b3b1ab", lw=2.2 if f1 else 1.0, zorder=4 if f1 else 3)
        ax.text(LAM[RESP[i].argmax()], RESP[i].max() * 1.18, str(NM[i]), ha="center", va="bottom",
                fontsize=7.5, color=INK if f1 else INK2, fontweight="bold" if f1 else "normal")
    sh = out["f1_410"]["share_of_f1_white_signal_outside_390_440"][best]["outside"]
    ax.annotate(f"410 nm channel, outside its band: {sh:.0%} of what\nit reads over the white well comes from here",
                (690, 0.0125), xytext=(1040, 0.0017), fontsize=8, color=INK, va="center", ha="right",
                arrowprops={"arrowstyle": "-", "color": INK2, "lw": 0.8})
    ax.text(900, 0.05, "above 730 nm: 8-42% of each channel's area,\nbut the LED gives almost no light there",
            ha="center", va="bottom", fontsize=8, color=INK2)
    ax.set_yscale("log")
    ax.set_ylim(1e-3, 2.6)
    ax.set_xlim(350, 1050)
    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("response, relative to the 680 nm channel's peak (log scale)")
    ax.set_title("The sensor's measured channels (solid, datasheet Fig. 19) leak outside their bands;\n"
                 "the Gaussians every earlier score assumed (dashed) do not", loc="left", color=INK, fontsize=10)

    # (c) 410 nm: the published range each model predicts, and what the calibrated runs read.
    ax = fig.add_subplot(top[1])
    tidy(ax)
    f1 = out["f1_410"]["by_model"]
    runs = [k for k in f1["fig19_led"]["measured_410"] if k != "09-30 before (/ empty)"]
    for j, p in enumerate(NAMES):
        for dx, key, col in ((-0.17, "gaussian", BAND), (0.17, "fig19_led", PAINT_COL[p])):
            lo, hi = f1[key]["reference_410"][p]
            ax.bar(j + dx, max(hi - lo, 0.012), bottom=lo - (0.006 if hi - lo < 0.012 else 0), width=0.26,
                   color=col, alpha=1 if key == "gaussian" else 0.45, lw=0, zorder=2)
            ys = [f1[key]["measured_410"][k][p] for k in runs]
            ax.plot(np.full(len(ys), j + dx), ys, ls="none", marker="o", ms=5.5, mfc=SURFACE if key == "gaussian"
                    else INK, mec=INK2 if key == "gaussian" else SURFACE, mew=1.2, zorder=4)
        lo_b = f1["fig19_led_extra_inside_390_440"]["reference_410"][p][0]
        hi_b = f1["fig19_led_extra_outside_390_440"]["reference_410"][p][1]
        ax.plot([j + 0.33, j + 0.33], [lo_b, hi_b], color=INK2, lw=1.2, zorder=3)
        ax.plot([j + 0.30, j + 0.36], [lo_b, lo_b], color=INK2, lw=1.2)
        ax.plot([j + 0.30, j + 0.36], [hi_b, hi_b], color=INK2, lw=1.2)
    ax.set_xticks(range(3), [f"{p}\nold | new" for p in NAMES])
    ax.set_xlim(-0.5, 2.6)
    ax.set_ylim(-0.08, 0.85)
    ax.set_ylabel("410 nm reading, black well 0, white well 1")
    ax.set_title("410 nm: what each model says the paint\nshould read (bars) and what 6 runs read (dots)",
                 loc="left", color=INK, fontsize=10)
    ax.text(0.98, 0.98, "grey bar, hollow dots: Gaussians\ncoloured bar, filled dots: Fig. 19 + LED\n"
            "thin line: Fig. 19 + LED if the 410 nm light\nthe model misses is all in band / all out",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.5, color=INK2)

    # (b) Points off by height, one panel per run: Gaussian against Fig. 19 + LED.
    xs = ("resting",) + LADDER
    labels = ["rest"] + [f"z {float(z):.0f}" for z in LADDER]
    axes = [fig.add_subplot(bot[i]) for i in range(3)]
    for i, (ax, run) in enumerate(zip(axes, RUNS)):
        tidy(ax)
        pts = {key: [out["models"][key]["points_off_440_670"][run][z]["points_off"]["all"] for z in xs]
               for key in ("gaussian", "fig19_led")}
        ax.plot(range(len(xs)), pts["gaussian"], color=MUTED, lw=1.6, ls=(0, (4, 2)), marker="o", ms=7,
                mfc=SURFACE, mec=MUTED, mew=1.4, zorder=2)
        ax.plot(range(len(xs)), pts["fig19_led"], color=RUN_COL[run], lw=2.2, marker="o", ms=7, mec=SURFACE,
                mew=1.5, zorder=3)
        j = int(np.argmin(pts["fig19_led"][1:])) + 1
        for key, dy in (("gaussian", 11), ("fig19_led", -15)):
            ax.annotate(f"{pts[key][j]:.1f}", (j, pts[key][j]), xytext=(0, dy), textcoords="offset points",
                        ha="center", color=INK, fontsize=8.5, fontweight="bold" if key == "fig19_led" else "normal")
        ax.annotate(f"{pts['gaussian'][0]:.1f} → {pts['fig19_led'][0]:.1f}", (0, pts["fig19_led"][0]),
                    xytext=(10, -2), textcoords="offset points", va="top", color=INK, fontsize=8.5)
        ax.set_xticks(range(len(xs)), labels, fontsize=8)
        ax.set_ylim(0, 56)
        ax.set_title(RUN_LABEL[run], loc="left", color=INK, fontsize=10)
        ax.set_xlabel("read height (nozzle z, mm); the foot touches at ~88")
        if i == 0:
            ax.set_ylabel("points off: 0 = matches the pigment\n(black well 0, white well 100)")
            handles = [plt.Line2D([], [], color=MUTED, lw=1.6, ls=(0, (4, 2)), marker="o", ms=7, mfc=SURFACE,
                                  mec=MUTED, mew=1.4),
                       plt.Line2D([], [], color=INK2, lw=2.2, marker="o", ms=7, mec=SURFACE, mew=1.5)]
            ax.legend(handles, ["Gaussian channels, even light (every earlier score)",
                                f"measured channels + {best} (colour: the run)"],
                      loc="center right", bbox_to_anchor=(1.0, 0.62), frameon=False, fontsize=8, labelcolor=INK)
        else:
            ax.tick_params(labelleft=False)
    fig.text(0.065, 0.465, "Points off by read height, all three paints (440-670 nm): the measured curves move "
             "every score by about a point and change no conclusion", color=INK, fontsize=11)
    fig.suptitle("Measured channel curves instead of Gaussians: scores move by about a point, and leakage explains "
                 "yellow's bright 410 nm",
                 x=0.065, y=0.975, ha="left", color=INK, fontsize=12)
    fig.text(0.065, 0.01, "Channel curves: AS7341 datasheet DS000504 v3-00 Fig. 19 (as7341-response-fig19.csv). "
             f"Light: CIE 015:2018 {best}, the white LED that best fits the white well's counts.\nPigments: Color "
             "Mixing Tools database, via rubenwiersma/painting_tools. Scores and calibration as analyse_read_height.py; "
             "analyse_response_curves.py, response-curves-2026-10-10.json.", color=INK2, fontsize=7.5)
    fig.savefig(os.path.join(HERE, "response-curves-2026-10-10.png"), dpi=150, facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main()
