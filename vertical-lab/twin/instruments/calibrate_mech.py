"""Calibrate the ``fast`` fidelity of the mechanical, powder and corrosion instruments on their own ``lite`` chain.

Run from ``vertical-lab``::

    nice -n 10 /tmp/venv/bin/python -m twin.instruments.calibrate_mech [--n 60] [--reps 4]

It builds representative lots and parts through the truths the way ``twin/campaign.py`` does (``_do_powder``,
``_do_print``, ``_ded``: designs drawn from ``twin/spaces.py``'s samplers plus the reference alloys, a few atomizer
runs per lot, the campaign's ``charge_g``), runs each instrument's lite chain several times per sample, and asks
each module's ``calibrate(samples_by_campaign, rng)`` to fit the parameters its fast mode samples from (biases that
depend on the sample's state, and the spread). The result goes to ``calib_mech.json`` next to this file; every fast
mode falls back to built-in defaults when its section is missing, so the twin runs before calibration too.

The sample builders here (``make_lot``, ``make_part``, ``representative``, ``reference_samples``) are also what the
tests and ``gallery_mech.py`` use.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CALIB_PATH = HERE / "calib_mech.json"

AL_PROC = dict(superheat_K=150, pour_mbar=200, amplitude=0.8, P_W=300, v_mm_s=1000, h_um=110, t_um=30, T0_C=150)
CU_PROC = dict(superheat_K=120, pour_mbar=220, amplitude=0.8, P_W=600, v_mm_min=600, feed_g_min=6)
CHARGE_KG = {"flaime_al": 0.30, "onr_cu": 0.80}         # twin/campaign.py AL_CHARGE_KG, CU_CHARGE_KG
_TRUTHS: dict = {}


def truth(campaign: str, seed: int = 0):
    key = (campaign, seed)
    if key not in _TRUTHS:
        if campaign == "flaime_al":
            from twin.truth_al import AlTruth
            _TRUTHS[key] = AlTruth(seed)
        else:
            from twin.truth_cu import CuTruth
            _TRUTHS[key] = CuTruth(seed)
    return _TRUTHS[key]


def _liquidus(campaign, t, comp):
    th = t.thermo(comp)
    return th["T_liquidus_C"] if campaign == "flaime_al" else th["liquidus_C"]


def make_lot(campaign: str, comp: dict, proc: dict, rng, runs: int = 3, seed: int = 0, tries: int = 6) -> dict:
    """A powder lot as ``Campaign._do_powder`` makes it (runs re-drawn if every one failed)."""
    t = truth(campaign, seed)
    TL = _liquidus(campaign, t, comp)
    kg = CHARGE_KG[campaign]
    for _ in range(tries):
        rs = []
        for _i in range(runs):
            r = t.atomize(comp, proc, TL, rng)
            r["charge_g"] = kg * 1000.0
            rs.append(r)
        good = [r for r in rs if not r["failed"]]
        if good:
            break
    w = np.array([r["usable_frac"] * r["cut_frac"] for r in good])
    w = w / w.sum()
    true = {e: float(sum(wi * r["composition"].get(e, 0.0) for wi, r in zip(w, good)))
            for e in set().union(*[r["composition"] for r in good])}
    return dict(composition=true, oxygen_ppm=float(sum(wi * r["oxygen_ppm"] for wi, r in zip(w, good))),
                satellite_frac=float(sum(wi * r["satellite_frac"] for wi, r in zip(w, good))),
                carbon_ppm=float(sum(wi * r.get("carbon_ppm", 0.0) for wi, r in zip(w, good))), runs=rs,
                campaign=campaign, design=dict(comp), d50_um=float(sum(wi * r["d50_um"] for wi, r in zip(w, good))),
                reuse=0)


def make_part(campaign: str, lot: dict, proc: dict, rng, mode: str = "blown_large", seed: int = 0) -> dict:
    """A part as ``Campaign._do_print`` / ``_ded`` makes it, with what the campaign adds."""
    t = truth(campaign, seed)
    if campaign == "flaime_al":
        part = t.build(lot, proc, rng)
        part.update(strength=t.strength(part), strength_hot=t.strength(part, 250.0))
    else:
        part = t.deposit(lot, proc, mode, rng)
        part.update(strength=t.strength(part), corrosion=t.corrosion(part))
    part.update(campaign=campaign, design=dict(lot.get("design", lot["composition"])), reuse=lot.get("reuse", 0))
    return part


def reference_samples(seed: int = 0, rng=None) -> dict:
    """{label: (lot, part)} for the gallery and tests: the reference alloys at the reference tables' sound process
    points, plus a porous and cracked Al case (7075 without inoculant at a lack-of-fusion setting)."""
    from twin.spaces import REFERENCE
    rng = np.random.default_rng(seed) if rng is None else rng
    out = {}
    for campaign, refs in REFERENCE.items():
        bal = "Al" if campaign == "flaime_al" else "Cu"
        proc = AL_PROC if campaign == "flaime_al" else CU_PROC
        for name, wt in refs.items():
            comp = dict(wt)
            comp[bal] = 100.0 - sum(wt.values())
            lot = make_lot(campaign, comp, proc, rng, seed=seed)
            out[name] = (lot, make_part(campaign, lot, proc, rng, seed=seed))
    comp = {"Zn": 5.6, "Mg": 2.5, "Cu": 1.6, "Cr": 0.23}
    comp["Al"] = 100.0 - sum(comp.values())
    bad = dict(AL_PROC, P_W=180, v_mm_s=1400, h_um=150, t_um=50)
    lot = make_lot("flaime_al", comp, AL_PROC, rng, seed=seed)
    out["7075 porous, cracked"] = (lot, make_part("flaime_al", lot, bad, rng, seed=seed))
    return out


def representative(campaign: str, n: int, seed: int = 0, runs: int = 2) -> list:
    """[(lot, part)] over the campaign's design space (designs and process settings from ``spaces.sample``), plus
    the reference alloys, so the calibration covers sound, porous and cracked parts."""
    from twin.spaces import SPACES
    sp = SPACES[campaign]
    rng = np.random.default_rng(seed + 17)
    out = []
    for d in sp.sample(n, seed=seed):
        comp = sp.composition(d)
        proc = {k: d[k] for k in d if k not in sp.elements}
        lot = make_lot(campaign, comp, proc, rng, runs=runs, seed=0)
        mode = ["blown_large", "blown_small", "preplaced"][int(rng.integers(0, 3))] if campaign == "onr_cu" else None
        out.append((lot, make_part(campaign, lot, proc, rng, mode=mode or "blown_large")))
    for lab, (lot, part) in reference_samples(seed).items():
        if part["campaign"] == campaign:
            out.append((lot, part))
    return out


# --------------------------------------------------------------------------------------------- the calibration run
MODULES = ("tensile", "pip", "hardness", "density", "psd", "atomize_yield", "corrosion")


def run(n: int = 60, seed: int = 0, only=None) -> dict:
    import importlib
    t0 = time.time()
    samples = {c: representative(c, n, seed) for c in ("flaime_al", "onr_cu")}
    print(f"built {sum(len(v) for v in samples.values())} samples in {time.time() - t0:.1f} s", flush=True)
    old = json.loads(CALIB_PATH.read_text()) if CALIB_PATH.exists() else {}
    out = dict(old)
    for m in MODULES:
        if only and m not in only:
            continue
        try:
            mod = importlib.import_module(f"twin.instruments.{m}")
        except ImportError as e:
            print(f"{m}: not importable ({e})")
            continue
        if not hasattr(mod, "calibrate"):
            print(f"{m}: no calibrate()")
            continue
        t1 = time.time()
        res = mod.calibrate(samples, np.random.default_rng(seed + 101))
        out.update(res)
        print(f"{m}: {sorted(res)} in {time.time() - t1:.1f} s", flush=True)
    out["_meta"] = dict(n_designs_per_campaign=n, seed=seed, n_samples={c: len(v) for c, v in samples.items()},
                        written=time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()))
    CALIB_PATH.write_text(json.dumps(out, indent=1, sort_keys=True, default=float))
    print(f"wrote {CALIB_PATH} in {time.time() - t0:.1f} s")
    return out


def fit_linear(X, y, w=None):
    """Least squares y ~ [1, X] -> (coef list, residual sd). A tiny helper the modules' calibrate() functions use."""
    X = np.atleast_2d(np.asarray(X, float))
    if X.shape[0] != len(y):
        X = X.T
    A = np.column_stack([np.ones(len(y)), X])
    y = np.asarray(y, float)
    if w is not None:
        sw = np.sqrt(np.asarray(w, float))
        coef = np.linalg.lstsq(A * sw[:, None], y * sw, rcond=None)[0]
    else:
        coef = np.linalg.lstsq(A, y, rcond=None)[0]
    res = y - A @ coef
    return [float(c) for c in coef], float(np.sqrt(np.mean(res ** 2)))


def fit_mean_sd(X, y, ridge=1e-2):
    """Heteroscedastic normal y ~ N(mu(x), sd(x)): ridge least squares on standardized features for the mean, and
    for log sd a regression of log|residual| (+0.635, the mean of log|z| for a standard normal is -0.635), so the
    spread is positive and grows or shrinks with the state. Returns what ``mech.ln_draw`` reads."""
    X = np.atleast_2d(np.asarray(X, float))
    y = np.asarray(y, float)
    xm, xs = X.mean(0), X.std(0)
    xs = np.where(xs > 1e-12, xs, 1.0)
    Z = (X - xm) / xs
    A = np.column_stack([np.ones(len(y)), Z])
    R = ridge * len(y) * np.eye(A.shape[1])
    R[0, 0] = 0.0
    mu = np.linalg.solve(A.T @ A + R, A.T @ y)
    res = y - A @ mu
    ly = np.log(np.abs(res) + 1e-6) + 0.635
    lsd = np.linalg.solve(A.T @ A + 10 * R, A.T @ ly)
    # rescale so the mean predicted variance matches the residual variance
    pred = np.exp(A @ lsd)
    k = math.sqrt(np.mean(res ** 2) / max(np.mean(pred ** 2), 1e-30))
    lsd[0] += math.log(k)
    return dict(mu=[float(v) for v in mu], lsd=[float(v) for v in lsd], xm=[float(v) for v in xm],
                xs=[float(v) for v in xs], rmse=float(np.sqrt(np.mean(res ** 2))), n=int(len(y)))


def fit_two_level(X, y, g, ridge=1e-2):
    """Two-level calibration of a fast mode on lite-chain repeats: y (a log ratio of measured to the truth's value)
    for observations X grouped by sample g. The between-sample part is a ridge-linear mean in the standardized
    features plus a kernel-smoothed table of each calibration sample's own residual (so a state the features do not
    linearize, such as how a Voce shape biases the PIP inversion, is interpolated from its neighbours); the
    within-sample spread (repeat to repeat) is likewise a log-linear model plus a smoothed table. ``mech.two_level``
    evaluates it."""
    X = np.atleast_2d(np.asarray(X, float))
    y = np.asarray(y, float)
    g = np.asarray(g)
    ug, first = np.unique(g, return_index=True)
    Xg = X[first]
    ym = np.array([y[g == u].mean() for u in ug])
    from scipy.special import digamma
    ng = np.array([(g == u).sum() for u in ug])
    sw = np.array([y[g == u].std(ddof=1) if n > 1 else np.nan for u, n in zip(ug, ng)])
    if np.all(~np.isfinite(sw)):
        sw = np.full(len(ug), float(np.std(y)) + 1e-6)
    sw = np.where(np.isfinite(sw), sw, np.nanmedian(sw))
    sw = np.maximum(sw, 1e-5)
    # E[ln s] = ln sigma + (digamma((n-1)/2) - ln((n-1)/2)) / 2 for a normal sample of n: undo it
    k = np.maximum(ng - 1, 1) / 2.0
    sw = sw * np.exp(-(digamma(k) - np.log(k)) / 2)
    lin = fit_mean_sd(Xg, ym, ridge)
    Z = (Xg - np.array(lin["xm"])) / np.array(lin["xs"])
    A = np.column_stack([np.ones(len(ug)), Z])
    eg = ym - A @ np.array(lin["mu"])
    R = 10 * ridge * len(ug) * np.eye(A.shape[1])
    R[0, 0] = 0.0
    lsw = np.linalg.solve(A.T @ A + R, A.T @ np.log(sw))
    esw = np.log(sw) - A @ lsw
    return dict(mu=lin["mu"], xm=lin["xm"], xs=lin["xs"], lsw=[float(v) for v in lsw],
                Z=np.round(Z, 4).tolist(), eg=np.round(eg, 5).tolist(), esw=np.round(esw, 4).tolist(),
                rmse_between=float(np.sqrt(np.mean(eg ** 2))), sd_within_median=float(np.median(sw)),
                n_samples=int(len(ug)), n=int(len(y)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    run(a.n, a.seed, a.only)
