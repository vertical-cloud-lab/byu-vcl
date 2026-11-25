"""Calibrate the fast mode of the microscopy, diffraction and chemistry simulators on their lite chains, and print
the fast-vs-lite comparison.

    python -m twin.instruments.calibrate_micro                 # every module (about 2-4 min on one core)
    python -m twin.instruments.calibrate_micro xrd ebsd        # some of them
    python -m twin.instruments.calibrate_micro --table [n]     # fast vs lite on the gallery alloys (n draws each)

Each module's ``calibrate()`` runs its own lite chain many times over representative samples (random feasible
designs and process settings from ``twin.spaces``, a quarter of the atomizer melts set 60 K below the true liquidus,
the three DED modes, plus the gallery alloys), fits its error model (bias and spread as functions of the sample's
state) and the parameters go to ``twin/instruments/calib_micro.json`` (keys: eds, xrf, icpms, sem_powder,
sem_section, ebsd, xrd_powder, xrd_part). The fast mode of each instrument samples from those parameters.

``--table`` writes ``out/twin2/instruments/calib_micro_table.{json,md}``: for every instrument, gallery alloy and
output, the truth (where the sample has it), lite mean and sd, fast mean and sd, over n draws of each.
"""
from __future__ import annotations

import importlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

from twin.instruments import OUTPUTS, micro

MODULES = ["xrd", "eds", "xrf", "icpms", "sem", "ebsd"]
OUT = Path(__file__).resolve().parents[2] / "out" / "twin2" / "instruments"
# instrument -> (module, function, sample kind)
MICRO = {"sem_powder": ("sem", "measure_powder", "powder"), "eds": ("eds", "measure", "powder"),
         "xrf": ("xrf", "measure", "powder"), "icpms": ("icpms", "measure", "powder"),
         "xrd_powder": ("xrd", "measure_powder", "powder"), "sem_section": ("sem", "measure_section", "part"),
         "ebsd": ("ebsd", "measure", "part"), "xrd_part": ("xrd", "measure_part", "part")}


def run(mods):
    for m in mods:
        t0 = time.time()
        mod = importlib.import_module(f"twin.instruments.{m}")
        cal = mod.calibrate()
        if m in ("eds", "xrf", "icpms", "ebsd"):
            cal = {m: cal}
        for k, v in cal.items():
            micro.calib_write(k, v)
        print(f"{m}: calibrated {sorted(cal)} in {time.time() - t0:.0f} s", flush=True)


def truth_of(inst, key, sample, campaign, pm):
    """The true value of an output, where the sample carries it (None otherwise)."""
    base = micro.base_of(campaign)
    if key == "a_fcc_A":
        return pm["matrix"]["a_A"]
    if key == "porosity":
        return sample.get("porosity")
    if key == "crack_density":
        return sample.get("crack_density")
    if key == "grain_um":
        return sample.get("grain_um")
    if key == "beta_prime_frac":
        return sample.get("beta_prime") if campaign == "onr_cu" else None
    if key == "equiaxed_frac":
        return pm.get("grains", {}).get("equiaxed_frac")
    if key == "satellite_frac":
        return sample.get("satellite_frac")
    if key == "lof_frac":
        p = sample.get("pores") or {}
        tot = sum(p.get(k, 0.0) for k in ("lof", "keyhole", "gas"))
        return p.get("lof", 0.0) / tot if tot > 0 else None
    if key.startswith("comp."):
        return sample["composition"].get(key[5:])
    return None


def table(n=40, seed=7):
    rows = []
    G = micro.gallery_samples()
    for inst, (mod, fn, kind) in MICRO.items():
        f = getattr(importlib.import_module(f"twin.instruments.{mod}"), fn)
        for camp, alloys in G.items():
            for alloy, (lot, part) in alloys.items():
                s = lot if kind == "powder" else part
                pm = micro.phase_model(s, camp, kind)
                vals = {"lite": {}, "fast": {}}
                tms = {"lite": [], "fast": []}
                for fid in ("lite", "fast"):
                    rng = np.random.default_rng(seed)
                    for _ in range(n):
                        t = time.process_time()
                        r = f(s, camp, rng, fidelity=fid)
                        tms[fid].append(time.process_time() - t)
                        for k, v in _flatten(r, camp).items():
                            vals[fid].setdefault(k, []).append(v)
                for k in sorted(set(vals["lite"]) | set(vals["fast"])):
                    L, F = vals["lite"].get(k, []), vals["fast"].get(k, [])
                    tr = truth_of(inst, k, s, camp, pm)
                    rows.append(dict(instrument=inst, campaign=camp, alloy=alloy, output=k,
                                     true=None if tr is None else float(tr),
                                     lite_mean=_m(L), lite_sd=_s(L), lite_n=len(L), fast_mean=_m(F), fast_sd=_s(F),
                                     fast_n=len(F)))
                rows.append(dict(instrument=inst, campaign=camp, alloy=alloy, output="_ms_per_call",
                                 lite_mean=1e3 * float(np.median(tms["lite"])), fast_mean=1e3 * float(np.median(tms["fast"]))))
                print(inst, alloy, "lite %.2f ms fast %.3f ms" % (1e3 * np.median(tms["lite"]), 1e3 * np.median(tms["fast"])),
                      flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "calib_micro_table.json").write_text(json.dumps(rows, indent=1))
    md = ["| instrument | alloy | output | true | lite mean ± sd | fast mean ± sd | (fast−lite)/se |",
          "|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["output"] == "_ms_per_call":
            continue
        if r["lite_mean"] is None and r["fast_mean"] is None:
            continue
        se = math.sqrt(((r["lite_sd"] or 0) ** 2) / max(r["lite_n"], 1) + ((r["fast_sd"] or 0) ** 2) / max(r["fast_n"], 1))
        z = ((r["fast_mean"] - r["lite_mean"]) / se) if (se > 0 and r["fast_mean"] is not None and r["lite_mean"] is not None) else float("nan")
        md.append(f"| {r['instrument']} | {r['alloy']} | {r['output']} | {_f(r['true'])} | {_f(r['lite_mean'])} ± {_f(r['lite_sd'])}"
                  f" ({r['lite_n']}) | {_f(r['fast_mean'])} ± {_f(r['fast_sd'])} ({r['fast_n']}) | {z:+.1f} |")
    (OUT / "calib_micro_table.md").write_text("\n".join(md) + "\n")
    print("wrote", OUT / "calib_micro_table.md")
    return rows


def _flatten(r, camp):
    out = {}
    for k, v in r.items():
        if k in ("raw",):
            continue
        if isinstance(v, dict):
            if k in ("comp",):
                for e, x in v.items():
                    out[f"comp.{e}"] = float(x)
            elif k == "phases":
                base = micro.base_of(camp)
                for e, x in v.items():
                    out[f"phase.{e}"] = float(x)
            continue
        if isinstance(v, (int, float)) and v is not None and np.isfinite(v):
            out[k] = float(v)
    return out


def _m(v):
    return float(np.mean(v)) if len(v) else None


def _s(v):
    return float(np.std(v)) if len(v) > 1 else None


def _f(x):
    if x is None:
        return "–"
    ax = abs(x)
    if ax == 0:
        return "0"
    if ax >= 100:
        return f"{x:.0f}"
    if ax >= 1:
        return f"{x:.3g}" if ax < 10 else f"{x:.1f}"
    return f"{x:.3g}" if ax >= 1e-3 else f"{x:.2e}"


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--table":
        table(int(args[1]) if len(args) > 1 else 40)
    else:
        run(args or MODULES)
