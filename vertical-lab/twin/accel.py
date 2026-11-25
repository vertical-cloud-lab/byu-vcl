"""Acceleration and enhancement factors, the self-driving-lab benchmarking metrics, for the twin's runs.

    python3 -m twin.accel [runs.jsonl]       # AF and EF of round 1's facility experiment, printed

Definitions follow Rohr et al. (Chem. Sci. 2020, "Benchmarking the acceleration of materials discovery by sequential
learning") and their use across materials domains by Liang et al. (npj Comput. Mater. 2021) and in the survey of
reported values by Adesiji, Wang, Kuo and Brown (2025): see notes/twin_econ.md for the citations and what they found.

* **Acceleration factor** AF(target) = x_ref / x_new, where x is what it takes to first reach the target: the number
  of experiments, the days, or the dollars. Here x is per seed (each twin-year is one campaign), and AF is the ratio
  of the medians over seeds. When some seeds never reach the target within the horizon, their x is censored at what
  they used, and the medians are Kaplan-Meier medians (the smallest x at which the estimated share still short of
  the target falls to one half or below); if fewer than half of an arm's seeds reach it, its median is unbounded and
  AF is reported as a bound. Confidence intervals: percentile bootstrap over seeds, resampled within each arm.
* **Enhancement factor** EF(at) = y_new(at) / y_ref(at): the ratio of the best true utility reached by x = at
  (experiments, days or dollars), mean over seeds, with a bootstrap CI (Rohr et al. ratio the fraction of top
  candidates found; here the analogue is the best demonstrated alloy's utility).
* ``compare``: time to target and cost to target together, for the headline "X times faster at Y of the cost", with
  costs from ``econ.cost_curves`` (cash, operating or full cost).

Curves are lists of [days, spent_usd, best_true_utility] (best-so-far, one point per demonstrated alloy), one per
seed; or dicts with 'curve' and optional 'horizon_days', 'spent' (the year's final spend) and 'n' (demonstrated).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

COL = {"days": 0, "usd": 1}


def _norm(c, horizon_days=365.0):
    if isinstance(c, dict):
        cur = c.get("curve", [])
        return dict(curve=[list(p) for p in cur], horizon=float(c.get("horizon_days", horizon_days)),
                    spent=float(c.get("spent", cur[-1][1] if cur else 0.0)), n=int(c.get("n", len(cur))))
    cur = [list(p) for p in c]
    return dict(curve=cur, horizon=float(horizon_days), spent=float(cur[-1][1] if cur else 0.0), n=len(cur))


def time_to_target(curve, target: float, x: str = "experiments", horizon_days: float = 365.0):
    """(x needed to first reach `target`, reached?) for one seed; censored at what the seed used if never."""
    c = _norm(curve, horizon_days)
    for i, p in enumerate(c["curve"]):
        if p[2] >= target - 1e-12:
            return (float(i + 1) if x == "experiments" else float(p[COL[x]])), True
    if x == "experiments":
        return float(max(c["n"], len(c["curve"]))), False
    if x == "days":
        return c["horizon"], False
    return max(c["spent"], c["curve"][-1][1] if c["curve"] else 0.0), False


def km_median(t, reached) -> float:
    """Kaplan-Meier median of times with right-censoring (reached False = censored). inf if S(t) stays above 0.5."""
    t = np.asarray(t, float)
    e = np.asarray(reached, bool)
    if len(t) == 0:
        return float("nan")
    order = np.lexsort((~e, t))                 # events before censorings at the same time
    t, e = t[order], e[order]
    n = len(t)
    s = 1.0
    at_risk = n
    i = 0
    while i < n:
        tt = t[i]
        d = c = 0
        while i < n and t[i] == tt:
            d += int(e[i])
            c += int(not e[i])
            i += 1
        if d:
            s *= 1.0 - d / at_risk
            if s <= 0.5 + 1e-12:
                return float(tt)
        at_risk -= d + c
    return float("inf")


def _median_x(curves, target, x, horizon_days):
    xs, ok = zip(*[time_to_target(c, target, x, horizon_days) for c in curves]) if curves else ((), ())
    if all(ok):
        return float(np.median(xs)), xs, ok
    return km_median(xs, ok), xs, ok


def median_bound(xs, ok) -> float:
    """When the KM median is unbounded (fewer than half the seeds reached the target), the median is at least the
    largest x observed in the arm (the estimated share short of the target stays above one half through it)."""
    return float(np.max(xs)) if len(xs) else float("nan")


def _q(x, qs):
    """Quantiles that tolerate infinities (nearest rank, no interpolation)."""
    x = np.sort(np.asarray(x, float))
    if len(x) == 0:
        return [float("nan")] * len(qs)
    return [float(x[min(int(round(q * (len(x) - 1))), len(x) - 1)]) for q in qs]


def _ratio(a, b):
    if not np.isfinite(a) and not np.isfinite(b):
        return float("nan")
    if not np.isfinite(b):
        return 0.0
    if not np.isfinite(a):
        return float("inf")
    return a / b if b > 0 else float("inf")


def acceleration_factor(curves_ref, curves_new, target: float, x: str = "experiments", n_boot: int = 2000,
                        seed: int = 0, horizon_days: float = 365.0, ci: float = 0.95) -> dict:
    """AF = median x_ref / median x_new to reach `target` (KM medians when seeds are censored), bootstrap CI."""
    m_ref, xr, er = _median_x(curves_ref, target, x, horizon_days)
    m_new, xn, en = _median_x(curves_new, target, x, horizon_days)
    af = _ratio(m_ref, m_new)
    rng = np.random.default_rng(seed)
    boots = []
    xr, er, xn, en = np.array(xr), np.array(er), np.array(xn), np.array(en)
    for _ in range(n_boot):
        i = rng.integers(len(xr), size=len(xr))
        j = rng.integers(len(xn), size=len(xn))
        a = float(np.median(xr[i])) if er[i].all() else km_median(xr[i], er[i])
        b = float(np.median(xn[j])) if en[j].all() else km_median(xn[j], en[j])
        boots.append(_ratio(a, b))
    boots = np.array(boots, float)
    boots = boots[~np.isnan(boots)]
    lo, hi = _q(boots, [(1 - ci) / 2, 1 - (1 - ci) / 2])
    # bounds when a median is unbounded: AF >= (largest x the reference used) / median_new, or
    # AF <= median_ref / (largest x the new arm used)
    af_bound, bound_kind = None, None
    if not np.isfinite(m_ref) and np.isfinite(m_new):
        af_bound, bound_kind = _ratio(median_bound(xr, er), m_new), "lower"
    elif np.isfinite(m_ref) and not np.isfinite(m_new):
        af_bound, bound_kind = _ratio(m_ref, median_bound(xn, en)), "upper"
    return dict(af=af, lo=float(lo), hi=float(hi), median_ref=m_ref, median_new=m_new, x=x, target=target,
                hit_ref=float(np.mean(er)) if len(er) else 0.0, hit_new=float(np.mean(en)) if len(en) else 0.0,
                n_ref=len(xr), n_new=len(xn), bounded=not (np.isfinite(m_ref) and np.isfinite(m_new)),
                af_bound=af_bound, bound_kind=bound_kind,
                median_ref_bound=median_bound(xr, er) if not np.isfinite(m_ref) else None,
                median_new_bound=median_bound(xn, en) if not np.isfinite(m_new) else None)


def best_at(curve, at: float, x: str = "experiments", horizon_days: float = 365.0) -> float:
    c = _norm(curve, horizon_days)
    best = 0.0
    for i, p in enumerate(c["curve"]):
        v = (i + 1) if x == "experiments" else p[COL[x]]
        if v <= at + 1e-12:
            best = max(best, p[2])
    return best


def enhancement_factor(curves_ref, curves_new, at: float, x: str = "experiments", n_boot: int = 2000, seed: int = 0,
                       horizon_days: float = 365.0, ci: float = 0.95) -> dict:
    """EF = mean best_new(at) / mean best_ref(at) (best true utility reached by x = at), bootstrap CI."""
    yr = np.array([best_at(c, at, x, horizon_days) for c in curves_ref], float)
    yn = np.array([best_at(c, at, x, horizon_days) for c in curves_new], float)
    ef = _ratio(float(yn.mean()), float(yr.mean())) if len(yr) and len(yn) else float("nan")
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        a = yn[rng.integers(len(yn), size=len(yn))].mean()
        b = yr[rng.integers(len(yr), size=len(yr))].mean()
        boots.append(_ratio(a, b))
    boots = np.array(boots, float)
    boots = boots[~np.isnan(boots)]
    lo, hi = _q(boots, [(1 - ci) / 2, 1 - (1 - ci) / 2])
    return dict(ef=ef, lo=float(lo), hi=float(hi), mean_ref=float(yr.mean()) if len(yr) else None,
                mean_new=float(yn.mean()) if len(yn) else None, at=at, x=x)


def af_vs_target(curves_ref, curves_new, targets, x="days", **kw) -> list:
    return [acceleration_factor(curves_ref, curves_new, t, x, **kw) for t in targets]


def compare(curves_ref, curves_new, target: float, costs_ref=None, costs_new=None, n_boot: int = 2000, seed: int = 0,
            horizon_days: float = 365.0, label_ref: str = "reference", label_new: str = "new") -> dict:
    """Time to target and cost to target. ``costs_*``: {basis: curves with spend replaced by that basis' cost}
    (econ.cost_curves); without them, the curves' own (cash) spend is used. X = AF in days (ref / new); Y = the
    cost ratio new / ref (1 / AF in dollars), each with its CI."""
    out = dict(target=target, ref=label_ref, new=label_new)
    out["days"] = acceleration_factor(curves_ref, curves_new, target, "days", n_boot, seed, horizon_days)
    out["experiments"] = acceleration_factor(curves_ref, curves_new, target, "experiments", n_boot, seed,
                                             horizon_days)
    costs_ref = costs_ref or {"cash": curves_ref}
    costs_new = costs_new or {"cash": curves_new}
    out["cost"] = {}
    for basis in costs_ref:
        if basis not in costs_new:
            continue
        a = acceleration_factor(costs_ref[basis], costs_new[basis], target, "usd", n_boot, seed, horizon_days)
        inv = lambda v: float("nan") if (v is None or np.isnan(v)) else (_ratio(1.0, v) if v else float("inf"))
        y = dict(ratio=inv(a["af"]), lo=inv(a["hi"]), hi=inv(a["lo"]),
                 median_ref=a["median_ref"], median_new=a["median_new"], bounded=a["bounded"],
                 hit_ref=a["hit_ref"], hit_new=a["hit_new"],
                 ratio_bound=(_ratio(1.0, a["af_bound"]) if a["af_bound"] else None),
                 bound_kind={"lower": "upper", "upper": "lower"}.get(a["bound_kind"]),
                 median_ref_bound=a["median_ref_bound"], median_new_bound=a["median_new_bound"])
        out["cost"][basis] = y
    return out


def headline(cmp: dict, campaign_label: str = "", basis_order=("operating", "full", "cash")) -> str:
    """One sentence from compare()'s output, with bounds where the reference (or the new arm) reached the target in
    fewer than half its seeds."""
    d = cmp["days"]

    def f(v):
        return "unbounded" if not np.isfinite(v) else (f"{v:.1f}" if v >= 1 else f"{v:.2f}")

    def pct(v):
        return "unbounded" if not np.isfinite(v) else f"{v:.0%}"
    hits = (f" (reached in {d['hit_new']:.0%} of {d['n_new']} seeds against {d['hit_ref']:.0%} of {d['n_ref']})")
    if d["bound_kind"] == "lower":
        speed = (f"at least {f(d['af_bound'])}x faster: the {cmp['ref']} reached it in fewer than half its seeds "
                 f"within the horizon")
    elif d["bound_kind"] == "upper":
        speed = f"at most {f(d['af_bound'])}x as fast (it reached the target in fewer than half its seeds)"
    elif np.isfinite(d["af"]):
        speed = f"{f(d['af'])}x faster (95% CI {f(d['lo'])}-{f(d['hi'])})"
    else:
        speed = "with neither arm reaching it in half its seeds"
    parts = [f"{campaign_label}in this simulated benchmark, the {cmp['new']} reached the target ({cmp['target']:g}) "
             f"{speed}{hits}"]
    for b in basis_order:
        if b not in cmp["cost"]:
            continue
        y = cmp["cost"][b]
        if y.get("bound_kind") == "upper":
            parts.append(f"at most {pct(y['ratio_bound'])} of the {b} cost")
        elif y.get("bound_kind") == "lower":
            parts.append(f"at least {pct(y['ratio_bound'])} of the {b} cost")
        elif np.isfinite(y["ratio"]):
            parts.append(f"at {pct(y['ratio'])} of the {b} cost (95% CI {pct(y['lo'])}-{pct(y['hi'])})")
    return "; ".join(parts) + f"; reference: the {cmp['ref']}."


def curves_of(runs, campaign: str) -> list:
    """Per run: the campaign's best-so-far curve (round 2's new-alloys-only curve when present), its year's spend,
    horizon and number of demonstrated alloys."""
    from twin.econ import curve_of, horizon_days
    out = []
    for r in runs:
        c = r["campaigns"][campaign]
        cur = curve_of(c)
        out.append(dict(curve=cur, spent=c.get("spent", 0.0), horizon_days=horizon_days(r["cfg"]), n=len(cur)))
    return out


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "out" / "twin" / \
        "runs" / "facility.jsonl"
    rows = [json.loads(l) for l in path.read_text().splitlines()]
    grp = {}
    for r in rows:
        grp.setdefault((r["cfg"]["facility"], r["cfg"]["policy"]), []).append(r)
    for camp, tgt in (("flaime_al", 0.6), ("onr_cu", 0.45)):
        ref = curves_of(grp[("proposed", "cost_aware")], camp)
        new = curves_of(grp[("vertical_lab", "cost_aware")], camp)
        print(camp, json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in
                                acceleration_factor(ref, new, tgt, "days").items()}))
