"""Round 4 of the benchmark: from the day the funding arrives, three plans for the same two campaigns.

* ``wait``: build the cell, then start the campaigns in it (round 3's vertical lab, from its completion);
* ``parallel``: start on day 0 on the existing atomizer, BYU's own equipment and every partner route, and move work
  in house as each station comes online;
* ``external``: never build; BYU's equipment and the partners only.

    python3 -m twin.bench4 run [experiment ...]    # -> out/twin4/runs/<experiment>.jsonl (TWIN_WORKERS processes)
    python3 -m twin.bench4 summary                 # -> out/twin4/bench4_summary.json
    python3 -m twin.bench4 one PLAN [POLICY]       # one run, printed

A policy name ``A+B`` runs A on aluminium and B on copper: ``fast`` is the heuristic and the funnel (round 3's cheap
policies, the funnel being copper's best), ``best`` is time-aware BOFN and the funnel (each campaign's best in round 3).
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
from twin import bench3 as B3

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("TWIN4_OUT", HERE.parent / "out" / "twin4"))
RUNS = OUT / "runs"
EVENTS = OUT / "events"
DAYS = 730
YEARS = DAYS / 365.0
ALIAS = {"fast": "heuristic+tiered", "best": "bofn3+tiered", "pk": "pkgfn3+tiered"}
PLANS = ("wait", "parallel", "external")


def _cfg(plan, policy, seed, days=DAYS, events=False, money=1.0, **opts):
    return dict(plan=plan, policy=policy, seed=seed, days=days, years_budget=days / 365.0, stock="stocked",
                events=events, money=money, opts=opts)


EXPERIMENTS = {
    # the three plans, round 3's cheap policies (the heuristic on aluminium, the funnel on copper), 12 seeds
    "plans": [_cfg(p, "fast", s) for p in PLANS for s in range(12)],
    # 12 more seeds of the same (read together with "plans": 24 in all)
    "plans_more": [_cfg(p, "fast", s) for p in PLANS for s in range(12, 24)],
    # the same with three times the money (every route can run at its capacity; round 3's copper test)
    "plans_3x": [_cfg(p, "fast", s, money=3.0) for p in PLANS for s in range(12)],
    # each campaign's best policy of round 3 (time-aware BOFN on aluminium, the funnel on copper)
    "plans_best": [_cfg(p, "best", s) for p in PLANS for s in range(6)],
    # the parallel plan without one partner route at a time (where adding a route doesn't help)
    "routes": [_cfg("parallel", "fast", s, drop_routes=[r]) for r in
               ("lpbf_3dpt", "utah_midi", "tensile_ext", "utah_mxlab", "mines_x2", "edm", "pip") for s in range(8)],
    # provenance: someone on site at each partner's first job, at the stand-in offsets and at twice them
    "provenance": [_cfg("parallel", "fast", s, provenance=pv, offset_mult=m) for m in (1.0, 2.0, 3.0)
                   for pv in ((), "all") for s in range(8)],
    # no learning curve (every station at full rate the day it is commissioned), to size the ramp-up's cost
    "nolearn": [_cfg(p, "fast", s, learn=False) for p in ("wait", "parallel") for s in range(8)],
}


def run_id(cfg):
    parts = ["r4", cfg["plan"], cfg["policy"], f"s{cfg['seed']}"]
    for k, v in sorted((cfg.get("opts") or {}).items()):
        if v in ((), None, False) and k != "learn":
            continue
        if k == "learn" and v:
            continue
        parts.append(f"{k}-{'.'.join(v) if isinstance(v, (list, tuple)) else v}")
    if cfg.get("days", DAYS) != DAYS:
        parts.append(f"d{cfg['days']}")
    if cfg.get("money", 1.0) != 1.0:
        parts.append(f"money{cfg['money']:g}")
    return "_".join(str(p) for p in parts)


def make_policies(name, seed):
    from twin.opt import policies3 as P3
    name = ALIAS.get(name, name)
    al, cu = (name.split("+") + [name])[:2] if "+" in name else (name, name)
    return {"flaime_al": P3.make3(al, "flaime_al", seed), "onr_cu": P3.make3(cu, "onr_cu", seed)}


def run_one(cfg: dict) -> dict:
    try:
        import torch
        torch.set_num_threads(1)
    except Exception:
        pass
    from twin import campaign as C
    from twin import round4 as R4
    from twin import spaces as SP
    from twin.opt.gp import STATS
    t0 = time.time()
    yb = cfg.get("years_budget", YEARS)
    bud = {k: B2.BUDGET[k] * yb * cfg.get("money", 1.0) for k in ("flaime_al", "onr_cu")}
    specs = {k: C.Spec(k, bud[k], B2.WIP[k], cfg["seed"], 1.0, stock=cfg.get("stock", "stocked")) for k in bud}
    pols = make_policies(cfg["policy"], cfg["seed"])
    tw = R4.Twin4(specs, pols, plan=cfg["plan"], seed=cfg["seed"], horizon_days=cfg.get("days", DAYS),
                  opts=cfg.get("opts"))
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
            spent=round(c["spent"], 2), budget=c["budget"], best=c["best"], best_new=best, curve_new=curve_new,
            n_demonstrated=c["n_demonstrated"], n_new_demonstrated=len(new),
            n_new_alloys=len({d["design"] for d in new}), n_designs=c["n_designs"], n_lots=c["n_lots"],
            n_builds=c["n_builds"], refused=c["refused"], spend_by=c["spend_by"], done=c["done"], stops=c["stops"],
            status=c["status"], n_alloys_made=c["n_alloys_made"], prov_usd=round(camp.prov_usd, 2),
            policy_counts=dict(getattr(pol, "counts", {}) or {}), spend_curve=B3._spend_curve(camp),
            demonstrated=[{kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in d.items()}
                          for d in sorted(c["demonstrated"], key=lambda d: d["t_h"])])
    out["r4"] = tw.report()
    if cfg.get("events"):
        EVENTS.mkdir(parents=True, exist_ok=True)
        rid = run_id(cfg)
        log = tw.event_log(meta=dict(cfg=cfg, run_id=rid))
        (EVENTS / f"{rid}.json").write_text(json.dumps(B2._jsonable(log)))
        out["events_file"] = f"out/twin4/events/{rid}.json"
    return out


def _safe(cfg):
    try:
        return run_one(cfg)
    except Exception:
        import traceback
        return dict(cfg=cfg, error=traceback.format_exc()[-3000:])


def run(names, workers=3):
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(k, "1")
    RUNS.mkdir(parents=True, exist_ok=True)
    slow = {"best": 0, "pk": 0, "fast": 9}
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
    todo.sort(key=lambda t: (t[0], slow.get(t[2]["policy"], 5), t[2]["seed"]))
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
            print(f"  {name} {run_id(c)}: Al {res['campaigns']['flaime_al']['best_new']:.3f} "
                  f"Cu {res['campaigns']['onr_cu']['best_new']:.3f} ({res['seconds']} s; "
                  f"{time.time() - t0:.0f} s in)", flush=True)


def load(name):
    """An experiment's runs; "plans24" is "plans" and "plans_more" together (24 seeds)."""
    out = []
    for nm in {"plans24": ["plans", "plans_more"]}.get(name, [name]):
        p = RUNS / f"{nm}.jsonl"
        if p.exists():
            out += [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    return out


def group_key(cfg):
    return run_id(dict(cfg, seed=0)).replace("_s0", "")


def summary():
    T = B2.targets()
    S = dict(targets=T, experiments={})
    for name in EXPERIMENTS:
        rows = load(name)
        if not rows:
            continue
        groups = {}
        for r in rows:
            groups.setdefault(group_key(r["cfg"]), []).append(r)
        E = {}
        for key, rs in groups.items():
            rs.sort(key=lambda r: r["cfg"]["seed"])
            days = rs[0]["cfg"].get("days", DAYS)
            g = dict(n=len(rs), plan=rs[0]["cfg"]["plan"], policy=rs[0]["cfg"]["policy"],
                     opts=rs[0]["cfg"].get("opts"), seeds=[r["cfg"]["seed"] for r in rs],
                     seconds=float(np.mean([r["seconds"] for r in rs])),
                     start_days=[r["r4"]["start_h"] / 24.0 for r in rs],
                     cell_days=[(r["r4"]["cell_h"] or 0) / 24.0 for r in rs], campaigns={})
            for camp in ("flaime_al", "onr_cu"):
                cc = [r["campaigns"][camp] for r in rs]
                best = [c["best_new"] for c in cc]
                tt = {}
                for tn, tv in T.items():
                    hits = [B2.hit(c["curve_new"], tv[camp], 2) for c in cc]
                    dl = [h[0] if h else None for h in hits]
                    tt[tn] = dict(target=tv[camp], hit_frac=sum(1 for h in hits if h) / len(rs), days=dl,
                                  usd=[h[1] if h else None for h in hits],
                                  km_median_days=B3.km_median(dl, days))
                g["campaigns"][camp] = dict(
                    best=best, best_mean=float(np.mean(best)),
                    best_se=float(np.std(best, ddof=1) / np.sqrt(len(best))) if len(best) > 1 else 0.0,
                    targets=tt, spent_mean=float(np.mean([c["spent"] for c in cc])),
                    prov_usd=float(np.mean([c.get("prov_usd", 0.0) for c in cc])),
                    n_new_alloys=float(np.mean([c.get("n_new_alloys", 0) for c in cc])),
                    curves=[c["curve_new"] for c in cc], spend_curves=[c.get("spend_curve") for c in cc])
            E[key] = g
        S["experiments"][name] = E
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "bench4_summary.json").write_text(json.dumps(B2._jsonable(S)))
    return S


def main(argv):
    if not argv or argv[0] == "summary":
        S = summary()
        for name, E in S["experiments"].items():
            print(f"== {name}")
            for key, g in E.items():
                f, o = g["campaigns"]["flaime_al"], g["campaigns"]["onr_cu"]
                fmt = lambda c, t: f"{c['targets'][t]['hit_frac']:.0%} d{c['targets'][t]['km_median_days']}"
                print(f"  {key:60s} n={g['n']:2d} Al {f['best_mean']:.3f}±{f['best_se']:.3f} T1 {fmt(f, 'T1')} "
                      f"T2 {fmt(f, 'T2')} | Cu {o['best_mean']:.3f}±{o['best_se']:.3f} T1 {fmt(o, 'T1')} "
                      f"T2 {fmt(o, 'T2')} ({g['seconds']:.0f} s)")
        return
    if argv[0] == "run":
        run(argv[1:] or ["plans"], int(os.environ.get("TWIN_WORKERS", "3")))
        summary()
        return
    if argv[0] == "one":
        cfg = _cfg(argv[1], argv[2] if len(argv) > 2 else "fast", int(argv[3]) if len(argv) > 3 else 0,
                   days=int(os.environ.get("TWIN4_DAYS", DAYS)))
        r = run_one(cfg)
        print(json.dumps({k: (v["best_new"], v["n_demonstrated"], v["spent"]) for k, v in r["campaigns"].items()}),
              r["seconds"], "start", round(r["r4"]["start_h"] / 24, 1), "cell", round((r["r4"]["cell_h"] or 0) / 24, 1))
        print(json.dumps(r["r4"]["routes"]))
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
