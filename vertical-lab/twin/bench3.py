"""Round 3 of the benchmark: the same two campaigns on the asynchronous engine (``Twin(mode="async")``: no cap on work
in flight, physical capacity, a spending plan, interim immersion readings), every policy with the same capacity and
the same freedom to fill it, BOFN and pKGFN on every node with a per-dollar and a time-aware denominator.

    python3 -m twin.bench3 run [experiment ...]    # -> out/twin3/runs/<experiment>.jsonl (TWIN_WORKERS processes)
    python3 -m twin.bench3 summary                 # -> out/twin3/bench3_summary.json
    python3 -m twin.bench3 one POLICY [FACILITY]   # one run, printed

Each run writes one JSON line like round 2's (twin/bench2.py), plus what round 3 adds: completed evaluations by kind
(``done``), stopped coupons, the engine's admission outcomes (``status``) and the alloys made.
"""
from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from twin import bench2 as B2

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("TWIN3_OUT", HERE.parent / "out" / "twin3"))
RUNS = OUT / "runs"
EVENTS = OUT / "events"
BUDGET = dict(B2.BUDGET)

BASE = ("random", "sobol", "heuristic", "tiered", "gpbo")
NET = ("bofn3", "pkgfn3", "bofn3_usd", "pkgfn3_usd")
MAIN3 = BASE + NET


def _cfg(policy, seed, facility="vertical_lab", stock="stocked", days=365, years_budget=1.0, crucible=225,
         reuse=True, scenario="historical", events=False, cu_budget=None, **kw):
    return dict(policy=policy, seed=seed, facility=facility, stock=stock, days=days, years_budget=years_budget,
                crucible=crucible, reuse=reuse, scenario=scenario, events=events, cu_budget=cu_budget, engine="async",
                **kw)


EXPERIMENTS = {
    "dev": [_cfg(p, 0) for p in MAIN3],
    # the vertical lab, stocked, one year, both campaigns; seed 0 of each policy writes its event log. pKGFN runs
    # time-aware only (its comparison is with round 2's EI per dollar, BOFN per dollar here); a run of it costs
    # about twice a BOFN run
    "main": [_cfg(p, s, events=(s == 0)) for p in BASE + ("bofn3", "bofn3_usd", "pkgfn3") for s in range(12)],
    # 12 more seeds (24 in all) for copper's comparisons: the time-aware BOFN and the baselines
    "main_more": [_cfg(p, s) for p in BASE + ("bofn3",) for s in range(12, 24)],
    # copper's tests from round 2 (section 5.3): the hidden gamma-2 effect, a mis-specified proxy, the funnel taken
    # apart, three times the copper money; BOFN and pKGFN on 4 seeds (the cheap policies on 12)
    "cu_hidden": [_cfg(p, s, cu_hidden=1.0) for p in ("random", "heuristic", "tiered", "gpbo", "bofn3", "pkgfn3")
                  for s in range(4 if p in NET else 12)],
    "cu_proxy": [_cfg("tiered_mis", s, cu_hidden=h) for h in (0.0, 1.0) for s in range(12)],
    "cu_ablation": [_cfg(p, s) for p in ("tiered_screen", "tiered_proxy") for s in range(12)],
    "cu_money": [_cfg(p, s, cu_budget=180_000.0) for p in ("tiered", "heuristic", "gpbo", "bofn3", "pkgfn3")
                 for s in range(4 if p in NET else 12)],
    # the conventional lab with the same asynchronous freedom inside its own facilities and booking rules: three years
    # at three years' money, metal ordered as each charge needs it. Its cheap policies (the references of the
    # acceleration factors) are one experiment; BOFN and pKGFN another, on 3 and 2 seeds (three simulated years each
    # cost about three times a vertical-lab year), run last
    "conventional": [_cfg(p, s, facility="proposed", stock="lean", days=1095, years_budget=3.0, events=(s == 0))
                     for p in BASE for s in range(12)],
    "conventional_net": [_cfg(p, s, facility="proposed", stock="lean", days=1095, years_budget=3.0, events=(s == 0))
                         for p, n in (("bofn3", 3), ("pkgfn3", 2)) for s in range(n)],
}


def run_id(cfg):
    return "r3_" + B2.run_id(cfg)


def run_one(cfg: dict) -> dict:
    import torch
    torch.set_num_threads(1)
    from twin import campaign as C
    from twin import spaces as SP
    from twin.opt import policies3 as P3
    from twin.opt.gp import STATS
    t0 = time.time()
    yb = cfg.get("years_budget", 1.0)
    bud = {"flaime_al": BUDGET["flaime_al"] * yb, "onr_cu": (cfg.get("cu_budget") or BUDGET["onr_cu"]) * yb}
    specs = {k: C.Spec(k, bud[k], B2.WIP[k], cfg["seed"], 1.0, crucible_cm3=cfg.get("crucible", 225),
                       reuse=cfg.get("reuse", True), stock=cfg.get("stock", "stocked"),
                       cu_hidden=cfg.get("cu_hidden", 0.0), fidelity=cfg.get("fidelity", "fast")) for k in bud}
    pols = {k: P3.make3(cfg["policy"], k, cfg["seed"], cfg.get("crucible") if cfg.get("crucible") != 225 else None)
            for k in specs}
    tw = C.Twin(specs, pols, scenario=cfg.get("scenario", "historical"), facility=cfg["facility"], seed=cfg["seed"],
                horizon_days=cfg.get("days", 365), mode="async")
    s = tw.run()
    out = dict(cfg=cfg, seconds=round(time.time() - t0, 1), gp=dict(STATS), campaigns={})
    for k in specs:
        c = s[k]
        camp = tw.campaigns[k]
        refs = [{e: w.get(e, 0.0) for e in SP.SPACES[k].elements} for w in SP.REFERENCE[k].values()]
        for d in c["demonstrated"]:
            comp = camp.designs[d["design"]]["composition"]
            d["ref"] = any(all(abs(comp.get(e, 0.0) - r[e]) < 0.06 for e in r) for r in refs)
        new = sorted([d for d in c["demonstrated"] if not d["ref"]], key=lambda d: d["t_h"])
        best, curve_new = 0.0, []
        for d in new:
            best = max(best, d["u"])
            curve_new.append((round(d["t_h"] / 24.0, 3), round(d["spent"], 2), round(best, 4)))
        pol = pols[k]
        out["campaigns"][k] = dict(
            spent=round(c["spent"], 2), budget=c["budget"], best=c["best"], curve=c["curve"], best_new=best,
            curve_new=curve_new, n_demonstrated=c["n_demonstrated"], n_new_demonstrated=len(new),
            n_new_alloys=len({d["design"] for d in new}), n_discoveries=c["n_discoveries"],
            n_designs=c["n_designs"], n_lots=c["n_lots"], n_builds=c["n_builds"], n_sims=c["n_sims"],
            refused=c["refused"], orders=c["orders"], backorders=c["backorders"], spend_by=c["spend_by"],
            returned_g=c["returned_g"], n_results=c["n_results"], done=c["done"], stops=c["stops"],
            status=c["status"], n_inflight_end=c["n_inflight_end"], n_alloys_made=c["n_alloys_made"],
            policy_counts=dict(getattr(pol, "counts", {}) or {}),
            spend_curve=_spend_curve(camp),
            demonstrated=[{kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in d.items()}
                          for d in sorted(c["demonstrated"], key=lambda d: d["t_h"])])
    f = next(iter(tw.facilities.values()))
    out["utilization"] = f.utilization(tw.h)
    out["busy_h"] = {k: round(r.busy_h, 2) for k, r in f.res.items() if r.busy_h > 0}
    out["units"] = {k: r.st.units for k, r in f.res.items()}
    out["calendar"] = {k: r.st.hours for k, r in f.res.items()}
    out["external"] = {k: bool(r.st.external) for k, r in f.res.items()}
    out["helper_misses"] = f.helper_misses
    if cfg.get("events"):
        EVENTS.mkdir(parents=True, exist_ok=True)
        rid = run_id(cfg)
        log = tw.event_log(meta=dict(cfg=cfg, run_id=rid))
        (EVENTS / f"{rid}.json").write_text(json.dumps(B2._jsonable(log)))
        out["events_file"] = f"out/twin3/events/{rid}.json"
    return out


def _spend_curve(camp):
    """Money spent by day (cumulative, at 7-day steps), for the cost-alongside plots."""
    led = sorted(camp.ledger, key=lambda r: r[0])
    out, tot, i = [], 0.0, 0
    for day in range(0, int(camp.horizon_h / 24) + 8, 7):
        while i < len(led) and led[i][0] <= day * 24.0:
            tot += led[i][1]
            i += 1
        out.append((day, round(tot, 2)))
    return out


def _safe(cfg):
    try:
        return run_one(cfg)
    except Exception:
        import traceback
        return dict(cfg=cfg, error=traceback.format_exc()[-3000:])


def run(names, workers=3):
    # one BLAS thread per worker: numpy's OpenBLAS otherwise starts a thread per core in every worker, and four
    # workers on four cores ran about three times slower than one alone
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(k, "1")
    RUNS.mkdir(parents=True, exist_ok=True)
    slow = {"pkgfn3": 0, "pkgfn3_usd": 0, "bofn3": 1, "bofn3_usd": 1, "gpbo": 2}
    todo = []
    for rank, name in enumerate(names):
        path = RUNS / f"{name}.jsonl"
        done = set()
        if path.exists():
            for line in path.read_text().splitlines():
                try:
                    done.add(run_id(json.loads(line)["cfg"]))
                except Exception:
                    pass
        mine = [c for c in EXPERIMENTS[name] if run_id(c) not in done]
        print(f"{name}: {len(mine)} runs ({len(done)} already done)", flush=True)
        todo += [(rank, name, c) for c in mine]
    todo.sort(key=lambda t: (t[0], slow.get(t[2]["policy"], 9), t[2]["seed"]))
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        futs = {ex.submit(_safe, c): (name, c) for _, name, c in todo}
        for fut in as_completed(futs):
            name, c = futs[fut]
            res = fut.result()
            if "error" in res:
                with (RUNS / f"{name}.errors.jsonl").open("a") as fh:
                    fh.write(json.dumps(B2._jsonable(res)) + "\n")
                print(f"  {name} {run_id(c)}: ERROR {res['error'].splitlines()[-1]}", flush=True)
                continue
            with (RUNS / f"{name}.jsonl").open("a") as fh:
                fh.write(json.dumps(B2._jsonable(res)) + "\n")
            print(f"  {name} {run_id(c)}: FLAIME {res['campaigns']['flaime_al']['best_new']:.3f} "
                  f"ONR {res['campaigns']['onr_cu']['best_new']:.3f} ({res['seconds']} s; "
                  f"{time.time() - t0:.0f} s in)", flush=True)


def load(name):
    """An experiment's runs (the conventional lab's two experiments read as one)."""
    names = [name] + (["conventional_net"] if name == "conventional" else [])
    out = []
    for nm in names:
        p = RUNS / f"{nm}.jsonl"
        if p.exists():
            out += [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    return out


# ------------------------------------------------------------------------------------------------- summarising
def km_median(times, horizon):
    """Kaplan-Meier median of first-hit times with censoring at the horizon (None: not reached in the run)."""
    ev = sorted((t if t is not None else horizon + 1e-6, t is not None) for t in times)
    n, s = len(ev), 1.0
    for i, (t, hit) in enumerate(ev):
        if hit:
            s *= 1.0 - 1.0 / (n - i)
            if s <= 0.5:
                return t
    return None


def summary():
    T = B2.targets()
    S = dict(targets=T, experiments={})
    for name in EXPERIMENTS:
        rows = load(name)
        if not rows:
            continue
        groups = {}
        for r in rows:
            key = run_id(dict(r["cfg"], seed=0)).replace("_s0", "")
            groups.setdefault(key, []).append(r)
        E = {}
        for key, rs in groups.items():
            rs.sort(key=lambda r: r["cfg"]["seed"])
            days = rs[0]["cfg"].get("days", 365)
            g = dict(n=len(rs), policy=rs[0]["cfg"]["policy"], facility=rs[0]["cfg"]["facility"],
                     seeds=[r["cfg"]["seed"] for r in rs],
                     cfg={k: v for k, v in rs[0]["cfg"].items() if k not in ("seed", "events")},
                     seconds=float(np.mean([r["seconds"] for r in rs])), campaigns={})
            for camp in ("flaime_al", "onr_cu"):
                cc = [r["campaigns"][camp] for r in rs]
                best = [c["best_new"] for c in cc]
                tt = {}
                for tn, tv in T.items():
                    hits = [B2.hit(c["curve_new"], tv[camp], 2) for c in cc]
                    dl = [h[0] if h else None for h in hits]
                    tt[tn] = dict(target=tv[camp], hit_frac=sum(1 for h in hits if h) / len(rs), days=dl,
                                  usd=[h[1] if h else None for h in hits], km_median_days=km_median(dl, days))
                done = {}
                for c in cc:
                    for k, x in (c.get("done") or {}).items():
                        done[k] = done.get(k, 0) + x / len(cc) / (days / 365.0)
                g["campaigns"][camp] = dict(
                    best=best, best_mean=float(np.mean(best)),
                    best_se=float(np.std(best, ddof=1) / np.sqrt(len(best))) if len(best) > 1 else 0.0,
                    targets=tt, spent_mean=float(np.mean([c["spent"] for c in cc])),
                    n_new_alloys=float(np.mean([c.get("n_new_alloys", 0) for c in cc])) / (days / 365.0),
                    n_alloys_made=float(np.mean([c.get("n_alloys_made", 0) for c in cc])) / (days / 365.0),
                    n_stops=float(np.mean([len(c.get("stops") or []) for c in cc])) / (days / 365.0),
                    done_per_year={k: round(x, 2) for k, x in sorted(done.items())},
                    curves=[c["curve_new"] for c in cc], spend_curves=[c.get("spend_curve") for c in cc])
            g["utilization"] = {k: float(np.mean([r["utilization"].get(k, 0) for r in rs])) for k in rs[0]["utilization"]}
            E[key] = g
        S["experiments"][name] = E
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "bench3_summary.json").write_text(json.dumps(B2._jsonable(S)))
    return S


def main(argv):
    if not argv or argv[0] == "summary":
        S = summary()
        for name, E in S["experiments"].items():
            print(f"== {name}")
            for key, g in E.items():
                f, o = g["campaigns"]["flaime_al"], g["campaigns"]["onr_cu"]
                ft1, ot1 = f["targets"]["T1"]["km_median_days"], o["targets"]["T1"]["km_median_days"]
                print(f"  {key:52s} n={g['n']:2d} FLAIME {f['best_mean']:.3f}±{f['best_se']:.3f} T1 "
                      f"{f['targets']['T1']['hit_frac']:.0%} d{ft1}  ONR {o['best_mean']:.3f}±{o['best_se']:.3f} T1 "
                      f"{o['targets']['T1']['hit_frac']:.0%} d{ot1} ({g['seconds']:.0f} s)")
        return
    if argv[0] == "run":
        run(argv[1:] or ["main"], int(os.environ.get("TWIN_WORKERS", "3")))
        summary()
        return
    if argv[0] == "one":
        cfg = _cfg(argv[1], 0, facility=argv[2] if len(argv) > 2 else "vertical_lab")
        r = run_one(cfg)
        print(json.dumps({k: (v["best_new"], v["n_demonstrated"]) for k, v in r["campaigns"].items()}), r["seconds"])
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
