"""ICP-MS (Agilent 8900 triple quadrupole, He/H2 cell modes) after an HF-free acid digest: what the lab's chemistry
reports for a lot or for chips cut from a part.

The lab bans HF, so the digest is aqua regia + H2O2 in a closed microwave vessel (200 degC, assumed), made up to
50 mL, then diluted 1000x for measurement. The simulator follows the sample through that chain:

* **Digestion recovery by phase**, from the latent microstructure (twin/instruments/micro.py): metal in solid
  solution dissolves; elemental Si (the eutectic network of Al-Si alloys) does not dissolve in HCl/HNO3 at all, and
  dissolved silicic acid partly polymerizes and drops out as silica gel, so Si above about 1 wt% is badly
  under-recovered; Al3Zr, Al3Ti, Al3(Sc,Zr), Al45Cr7 and the Cu-side Ni3Nb, Ni3Ti and Cr particles are attacked only
  partly, and Zr, Ti and Nb in solution hydrolyse without fluoride (the reason HF is normally added; e.g. EPA
  Method 3052 and Agilent application notes on Zr/Ti/Nb alloys). The recoveries in ``RECOVERY`` are assumed
  (order of magnitude from those methods' cautions); each digest's recovery varies, more where it is partial.
* **Sample preparation**: 100 mg weighed (+-0.05 mg), 50 mL volumetric (+-0.1 %), 1000x dilution (+-0.3 %).
* **Measurement**: counts = sensitivity x concentration x dwell + background equivalent (BEC; Si's from N2+/CO+ in
  H2 mode, Fe's residual ArO+ in He mode), Poisson, 0.8 % flicker per replicate, internal-standard drift correction
  leaving 0.3 %; three replicates.
* **Analysis**: a five-point external calibration (0, 1, 10, 50, 100 ug/L, each standard +-0.5 %) by weighted
  linear regression; sample concentrations back-calculated to wt% in the solid; 3-sigma LOD from the blank's
  replicates. Results are absolute (not normalized), so what the digest misses reads low.

Li is seen (7Li, the only instrument here that does). Sensitivities and BECs assumed from typical 8900 figures.
Fidelity: 'lite' and 'full' run the chain ('full' adds ``raw``: counts, calibration lines, recoveries); 'fast'
draws from a lognormal around the expected recovery with spreads fitted to the lite chain (calib_micro.json,
'icpms').
"""
from __future__ import annotations

import math

import numpy as np

from twin.instruments import micro

SPEC = dict(station="byu_icpms", hours=0.1, consumables={"digest_vessel": 1, "aqua_regia_mL": 10, "argon_L": 30},
            note="HF-free microwave digest (aqua regia + H2O2), 100 mg, 50 mL, 1000x dilution; 3 replicates")

# sensitivity (cps per ug/L) and background equivalent concentration (ug/L) per element, assumed typical for an
# Agilent 8900 in He (or H2, for Si) mode
SENS = dict(Li=5e3, Mg=2.0e4, Al=2.0e4, Si=5e3, Sc=4e4, Ti=1.5e4, Cr=4e4, Mn=5e4, Fe=4e4, Ni=3e4, Cu=3e4,
            Zn=1.5e4, Zr=8e4, Nb=1.0e5, Sn=6e4, Ce=1.5e5, Er=1.2e5)
BEC = dict(Li=0.005, Mg=0.01, Al=0.05, Si=2.0, Sc=0.01, Ti=0.02, Cr=0.02, Mn=0.005, Fe=0.05, Ni=0.01, Cu=0.01,
           Zn=0.03, Zr=0.002, Nb=0.001, Sn=0.005, Ce=0.001, Er=0.001)
# fraction of an element recovered into solution from each phase (assumed): (phase name or 'matrix') -> element
RECOVERY = {
    "matrix": dict(Si=0.90, Zr=0.85, Ti=0.90, Nb=0.65, Sn=0.95, Cr=0.99),
    "Si": dict(Si=0.03),
    "Mg2Si": dict(Si=0.30),
    "Al3Zr_L12": dict(Zr=0.45), "Al3Zr_D023": dict(Zr=0.35), "Al3(Sc,Zr)": dict(Sc=0.75, Zr=0.45),
    "Al3Sc": dict(Sc=0.85), "Al3Er": dict(Er=0.90), "Al3Ti": dict(Ti=0.50), "Al45Cr7": dict(Cr=0.70),
    "Ni2Si": dict(Si=0.40), "Ni3Nb": dict(Nb=0.35), "Ni3Ti": dict(Ti=0.60), "Cr": dict(Cr=0.60),
}
STDS = np.array([0.0, 1.0, 10.0, 50.0, 100.0])        # ug/L
MASS_G, VOL_L, DIL = 0.100, 0.050, 1000.0


def expected_recovery(pm: dict) -> dict:
    """Mass-weighted recovery of each element over the phases that hold it (the digest's expectation)."""
    base = pm["base"]
    held, rec = {}, {}
    for p in pm["phases"]:
        tab = RECOVERY["matrix"] if p["role"] == "matrix" else RECOVERY.get(p["name"], {})
        for e, x in p["comp"].items():
            if e == base:
                continue
            m = p["wt"] * x
            held[e] = held.get(e, 0.0) + m
            r = tab.get(e, RECOVERY["matrix"].get(e, 1.0) if p["role"] in ("matrix", "martensite") else 0.99)
            rec[e] = rec.get(e, 0.0) + m * r
    out = {e: rec[e] / held[e] for e in held if held[e] > 0}
    # silicic acid above ~60 mg/L Si in the 50 mL digest polymerizes (assumed): the part above it is lost
    c_si = pm["composition"].get("Si", 0.0) * 1e-2 * MASS_G / VOL_L * 1e3     # mg/L if all dissolved
    if c_si > 60.0 and "Si" in out:
        out["Si"] *= 60.0 / c_si + (1 - 60.0 / c_si) * 0.3
    return out


def _truth_comp(sample, campaign):
    kind = micro.kind_of(sample)
    pm = micro.phase_model(sample, campaign, kind)
    comp = {e: v for e, v in pm["composition"].items() if e != pm["base"] and v > 0}
    for e, x in (pm.get("extra") or {}).items():
        comp[e] = comp.get(e, 0.0) + x
    return comp, pm


def _chain(comp, rec, rng, full=False):
    """Weigh, digest, dilute, measure, calibrate. comp in wt%."""
    m = MASS_G + rng.normal(0, 5e-5)
    V = VOL_L * (1 + rng.normal(0, 1e-3))
    D = DIL * (1 + rng.normal(0, 3e-3))
    out, lod, raw = {}, {}, {}
    els = sorted(set(comp) | set(SENS)) if full else sorted(comp)
    for e in els:
        if e not in SENS:
            continue
        r = rec.get(e, 1.0)
        # partial recoveries vary from digest to digest (assumed: sd 15 % of the missing share, + 0.5 %)
        r_eff = min(r * math.exp(rng.normal(0, 0.15 * (1 - r) + 0.005)), 1.0)
        c_sol = comp.get(e, 0.0) * 1e-2 * m * r_eff / V * 1e6 / D            # ug/L in the measured solution
        S, B = SENS[e], BEC[e]
        drift = math.exp(rng.normal(0, 0.003))
        dwell = 0.3 * 3

        def sig(c, n=3):
            mu = S * (c + B) * dwell * drift
            reps = rng.poisson(np.full(n, mu) * np.exp(rng.normal(0, 0.008, n))) / dwell
            return reps
        cal_true = STDS * (1 + rng.normal(0, 0.005, len(STDS)))
        cal_true[0] = 0.0
        ys = np.array([sig(c).mean() for c in cal_true])
        w = 1.0 / (np.maximum(ys, 1.0))                                       # Poisson weights
        X = np.stack([np.ones_like(STDS), STDS], 1)
        G = (X * w[:, None]).T @ X
        b = np.linalg.solve(G, (X * w[:, None]).T @ ys)
        blank = sig(0.0, 10)
        y = sig(c_sol).mean()
        c_meas = (y - b[0]) / b[1]
        wt = c_meas * D * V / m * 1e-6 * 100.0
        l_sol = 3 * blank.std(ddof=1) / b[1] if blank.std() > 0 else 3 * math.sqrt(S * B * dwell) / dwell / b[1]
        lod[e] = float(l_sol * D * V / m * 1e-6 * 100.0)
        if wt > lod[e] and comp.get(e, 0.0) > 0 or (wt > lod[e] and full):
            if comp.get(e, 0.0) > 0 or wt > 3 * lod[e]:
                out[e] = float(wt)
        if full:
            raw[e] = dict(cal_std=cal_true.tolist(), cal_cps=ys.tolist(), slope=float(b[1]), intercept=float(b[0]),
                          sample_cps=float(y), recovery=float(r_eff), c_sol_ugL=float(c_sol))
    return out, lod, raw


def measure(sample, campaign, rng, fidelity="fast", **kw):
    comp, pm = _truth_comp(sample, campaign)
    rec = expected_recovery(pm)
    if fidelity == "fast":
        return _fast(comp, rec, campaign, rng)
    out, lod, raw = _chain(comp, rec, rng, full=(fidelity == "full"))
    res = dict(comp=out)
    if fidelity == "full":
        res["raw"] = dict(per_element=raw, lod=lod, expected_recovery=rec)
    return res


def _fast(comp, rec, campaign, rng):
    cal = micro.calib("icpms").get(campaign, {})
    out = {}
    for e, c in comp.items():
        if e not in SENS:
            continue
        r = rec.get(e, 1.0)
        p = cal.get(e, {})
        s = p.get("s", [-4.3, 0.9, 0.0])
        miss = math.log10(1 - r + 0.005)
        lsd = math.exp(s[0] + s[1] * (miss + 2.3) + s[2] * math.log10(max(c, 1e-4)))
        b = p.get("b", 0.0)
        out[e] = float(c * r * math.exp(b + lsd * rng.normal()))
    return dict(comp=out)


def calibrate(n=40, reps=4, seed=0, verbose=True):
    rng = np.random.default_rng(seed)
    params, table = {}, []
    for camp in ("flaime_al", "onr_cu"):
        pairs = micro.random_samples(camp, n, seed=seed + 5) + list(micro.gallery_samples()[camp].values())
        rows = []
        for lot, part in pairs:
            for s in (lot, part):
                comp, pm = _truth_comp(s, camp)
                rec = expected_recovery(pm)
                for _ in range(reps):
                    r = measure(s, camp, rng, fidelity="lite")["comp"]
                    for e, c in comp.items():
                        if e in r and e in SENS:
                            rows.append((e, c, rec.get(e, 1.0), math.log(r[e] / (c * rec.get(e, 1.0)))))
        cp = {}
        for e in sorted({r[0] for r in rows}):
            R = [r for r in rows if r[0] == e]
            if len(R) < 8:
                continue
            y = np.array([r[3] for r in R])
            b = float(np.median(y))
            X = np.array([[1.0, math.log10(1 - r[2] + 0.005) + 2.3, math.log10(max(r[1], 1e-4))] for r in R])
            ly = np.log(np.abs(y - b) * 1.2533 + 1e-5)
            lam = np.diag([1e-6, 1e-2, 1e-2])
            s = np.linalg.solve(X.T @ X + lam, X.T @ ly)
            cp[e] = dict(b=b, s=[float(v) for v in s], n=len(R), sd=float(np.std(y)))
            table.append((camp, e, len(R), b, float(np.std(y)), float(np.mean([r[2] for r in R]))))
        params[camp] = cp
    if verbose:
        for row in table:
            print("%-9s %-3s n=%4d bias|rec=%+.4f sd=%.4f mean recovery=%.3f" % row)
    params["_table"] = [list(r) for r in table]
    return params


def gallery(outdir, samples):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from pathlib import Path
    outdir = Path(outdir)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    lot, part = samples["flaime_al"]["AlSi10Mg"]
    r = measure(lot, "flaime_al", np.random.default_rng(3), fidelity="full")
    ax = axes[0]
    for e, d in r["raw"]["per_element"].items():
        if e in ("Si", "Mg", "Fe"):
            ax.plot(d["cal_std"], d["cal_cps"], "o-", label=f"{e} calibration")
            ax.plot([d["c_sol_ugL"]], [d["sample_cps"]], "k*", ms=10)
    ax.set_xlabel("standard (ug/L)")
    ax.set_ylabel("counts per second")
    ax.set_xscale("symlog", linthresh=1)
    ax.set_yscale("log")
    ax.set_title("AlSi10Mg lot: external calibration and the sample (stars)", fontsize=9)
    ax.legend(fontsize=7)
    ax = axes[1]
    names, true, meas, err = [], [], [], []
    rng = np.random.default_rng(4)
    for camp, d in samples.items():
        for nm, (lot, part) in d.items():
            comp, pm = _truth_comp(lot, camp)
            reps = [measure(lot, camp, rng, fidelity="lite")["comp"] for _ in range(5)]
            for e, v in sorted(comp.items(), key=lambda t: -t[1]):
                if v < 0.05:
                    continue
                ms = [q.get(e, 0.0) for q in reps]
                names.append(f"{nm}\n{e}")
                true.append(v)
                meas.append(np.mean(ms))
                err.append(np.std(ms))
    x = np.arange(len(names))
    ax.bar(x - 0.2, true, 0.4, color="0.6", label="true (lot)")
    ax.bar(x + 0.2, meas, 0.4, yerr=err, color="C2", label="ICP-MS lite, HF-free digest, mean of 5")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=7)
    ax.set_ylabel("wt%")
    ax.legend(fontsize=8)
    ax.set_title("Si (eutectic network) and intermetallic-bound Zr read low without HF", fontsize=9)
    fig.tight_layout()
    fig.savefig(outdir / "icpms.png", dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    micro.calib_write("icpms", calibrate())
