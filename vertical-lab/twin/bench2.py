"""Round 2 of the benchmark: both campaigns at once, on the vertical lab with every instrument simulated, against
a conventional lab (the proposals' partners and core facilities), with design-of-experiments baselines, a
metallurgist's heuristic, standard BO, SAASBO and BOFN.

    python3 -m twin.bench2 run [experiment ...]    # -> out/twin2/runs/<experiment>.jsonl (TWIN_WORKERS processes)
    python3 -m twin.bench2 summary                 # -> out/twin2/bench2_summary.json
    python3 -m twin.bench2 one POLICY [FACILITY]   # one run, printed

Every run writes one JSON line: its config, per campaign the best-so-far curve [[days, money, true utility]], what
was demonstrated (true utilities, which the policies never see), money by kind, counts, the facility's utilization,
and the seconds it took. Runs flagged ``events`` also write their whole event log to out/twin2/events/ for the video
and twin/cloud.py.
"""
from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("TWIN_OUT", HERE.parent / "out" / "twin2"))
RUNS = OUT / "runs"
EVENTS = OUT / "events"
OUT.mkdir(parents=True, exist_ok=True)
BUDGET = {"flaime_al": 120_000.0, "onr_cu": 60_000.0}
WIP = {"flaime_al": 24, "onr_cu": 8}

MAIN_POL = ("random", "sobol", "heuristic", "tiered", "cost_aware", "gpbo", "bofn")


def _cfg(policy, seed, facility="vertical_lab", stock="stocked", days=365, years_budget=1.0, crucible=225,
         reuse=True, scenario="historical", events=False, cu_budget=None, **kw):
    return dict(policy=policy, seed=seed, facility=facility, stock=stock, days=days, years_budget=years_budget,
                crucible=crucible, reuse=reuse, scenario=scenario, events=events, cu_budget=cu_budget, **kw)


EXPERIMENTS = {
    # development: every policy, two seeds, stand-in instruments (TWIN_INSTRUMENTS=stub)
    "dev": [_cfg(p, s, events=(s == 0)) for p in MAIN_POL for s in range(2)],
    # the vertical lab, stocked, every instrument: each policy for a year (default GP surrogates)
    "main": [_cfg(p, s, events=(s == 0)) for p in MAIN_POL + ("bofn_blend",) for s in range(12)],
    # a conventional lab: the proposals' partners and BYU's core facilities, day shifts, order-as-needed, three
    # years at three years' money
    "conventional": [_cfg(p, s, facility="proposed", stock="lean", days=1095, years_budget=3.0, events=(s == 0))
                     for p in ("random", "sobol", "heuristic", "tiered", "gpbo", "bofn") for s in range(12)],
    # after the default runs: SAAS priors (MAP; BOFN with SAAS nodes; fully Bayesian SAASBO with NUTS)
    "saas": [_cfg(p, s) for p in ("saasmap", "bofn_saas", "saasbo") for s in range(12)],
    # the vertical lab ordering each charge's metal as it goes (as DAL does now) instead of keeping stock
    "stock": [_cfg(p, s, stock="lean") for p in ("heuristic", "bofn") for s in range(12)],
    # the 400 cm3 crucible against the 225 cm3 one, and powder reuse off
    "crucible": [_cfg(p, s, crucible=400) for p in ("heuristic", "bofn", "bofn_blend") for s in range(12)],
    "reuse": [_cfg(p, s, reuse=False) for p in ("heuristic", "bofn") for s in range(12)],
    # the simulators at 'lite' fidelity (small raw data and the real analysis) against 'fast' (emulated errors)
    "lite": [_cfg(p, s, fidelity="lite") for p in ("heuristic", "bofn") for s in range(3)],
    # copper: the same campaign on a truth with an effect the CALPHAD screen cannot see (gamma-2 above
    # Al = 8.2 + Ni/2), to test whether the tiered funnel's tie with BOFN is the truth being too kind to it
    "cu_hidden": [_cfg(p, s, cu_hidden=1.0) for p in ("random", "heuristic", "tiered", "cost_aware", "gpbo", "bofn",
                                                      "bofn_blend") for s in range(12)],
    # copper: the tiered funnel with a mis-specified proxy (each strengthening coefficient off by a lognormal factor,
    # sigma 0.4), on the plain truth and with the hidden gamma-2 effect: does tiered's copper lead rest on its proxy
    # reading the truth's own coefficients?
    "cu_proxy": [_cfg("tiered_mis", s, cu_hidden=h) for h in (0.0, 1.0) for s in range(12)],
    # ...and the funnel taken apart: its screen with a random ranking, its proxy with no screen
    "cu_ablation": [_cfg(p, s) for p in ("tiered_screen", "tiered_proxy") for s in range(12)],
    # the campaign trace (twin/trace.py, out/twin2/trace/README.md): BOFN, standard BO and random from one common seed
    # set (DAL #275), 12 seeds each; seed 0 of each writes a full trace with the optimizer's state
    "seeded": [_cfg(p, s, seeding="dal275", trace=(s == 0), events=(s == 0)) for p in ("bofn", "gpbo", "random")
               for s in range(12)],
    # the same on DAL's own lab as DAL #256 schedules it (twin/facility.py DAL256: one atomizer run a day Mon-Thu,
    # copper on Fridays, weekly SEM and polishing sessions, two-day Utah sessions on alternate weeks), ordering as it
    # goes; seed 0 of each writes a trace, and BOFN's is out/twin2/trace/campaign_trace.json
    "seeded_dal256": [_cfg(p, s, facility="dal256", stock="lean", seeding="dal275", trace=(s == 0), events=(s == 0))
                      for p in ("bofn", "gpbo", "random") for s in range(12)],
    # copper: what separates the policies when money is not the limit
    "cu": [_cfg(p, s, cu_budget=180_000.0) for p in ("heuristic", "tiered", "gpbo", "bofn", "bofn_blend")
           for s in range(12)],
    # the same for the two copper leaders only: does BOFN with blend screening catch the funnel with three times the
    # copper money (more tested alloys to learn from)?
    "cu_money": [_cfg(p, s, cu_budget=180_000.0) for p in ("tiered", "bofn_blend") for s in range(12)],
}


def run_one(cfg: dict) -> dict:
    import torch
    torch.set_num_threads(1)
    from twin import campaign as C
    from twin.opt import policies2 as P2
    from twin.opt.gp import STATS
    t0 = time.time()
    yb = cfg.get("years_budget", 1.0)
    bud = {"flaime_al": BUDGET["flaime_al"] * yb, "onr_cu": (cfg.get("cu_budget") or BUDGET["onr_cu"]) * yb}
    specs = {k: C.Spec(k, bud[k], WIP[k], cfg["seed"], 1.0, crucible_cm3=cfg.get("crucible", 225),
                       reuse=cfg.get("reuse", True), stock=cfg.get("stock", "stocked"), cu_hidden=cfg.get("cu_hidden", 0.0),
                       fidelity=cfg.get("fidelity", "fast")) for k in bud}
    pols = {k: P2.make(cfg["policy"], k, cfg["seed"], cfg.get("crucible") if cfg.get("crucible") != 225 else None,
                       seeding=cfg.get("seeding"))
            for k in specs}
    tw = C.Twin(specs, pols, scenario=cfg.get("scenario", "historical"), facility=cfg["facility"], seed=cfg["seed"],
                horizon_days=cfg.get("days", 365), trace=bool(cfg.get("trace")))
    s = tw.run()
    out = dict(cfg=cfg, seconds=round(time.time() - t0, 1), gp=dict(STATS), campaigns={})
    from twin import spaces as SP
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
        out["campaigns"][k] = dict(
            spent=round(c["spent"], 2), budget=c["budget"], best=c["best"], curve=c["curve"],
            best_new=best, curve_new=curve_new,
            n_demonstrated=c["n_demonstrated"], n_discoveries=c["n_discoveries"], n_designs=c["n_designs"],
            n_lots=c["n_lots"], n_builds=c["n_builds"], n_sims=c["n_sims"], refused=c["refused"],
            orders=c["orders"], backorders=c["backorders"], spend_by=c["spend_by"], returned_g=c["returned_g"],
            n_results=c["n_results"],
            demonstrated=[{kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in d.items()}
                          for d in sorted(c["demonstrated"], key=lambda d: d["t_h"])])
    f = next(iter(tw.facilities.values()))
    out["utilization"] = f.utilization(tw.h)
    out["busy_h"] = {k: round(r.busy_h, 2) for k, r in f.res.items() if r.busy_h > 0}
    out["units"] = {k: r.st.units for k, r in f.res.items()}
    out["calendar"] = {k: r.st.hours for k, r in f.res.items()}
    out["external"] = {k: bool(r.st.external) for k, r in f.res.items()}
    if cfg.get("events"):
        EVENTS.mkdir(parents=True, exist_ok=True)
        rid = run_id(cfg)
        log = tw.event_log(meta=dict(cfg=cfg, run_id=rid))
        (EVENTS / f"{rid}.json").write_text(json.dumps(log))
        out["events_file"] = f"out/twin2/events/{rid}.json"
    if cfg.get("trace"):
        from twin import trace as TR
        rid = run_id(cfg)
        seeds = {}
        if cfg.get("seeding"):
            from twin import seeding as SD
            for k, pol in pols.items():
                camp = tw.campaigns[k]
                rows = []
                for (lab, comp), d in zip(SD.seeds(cfg["seeding"], k), pol.common_seeds or []):
                    key = tuple(sorted({e: round(d.get(e, 0.0), 3) for e in camp.space.elements}.items()))
                    did = next((i for i, x in camp.designs.items() if x["key"] == key), None)
                    rows.append(dict(label=lab, asked_wt_pct=comp,
                                     run_wt_pct={e: round(d[e], 3) for e in camp.space.elements if d.get(e, 0) > 0},
                                     process={v.name: round(d[v.name], 3) for v in camp.space.process}, design=did))
                seeds[k] = rows
        T = TR.build(tw, cfg, rid, seeds)
        TR.OUT.mkdir(parents=True, exist_ok=True)
        (TR.OUT / f"{rid}.json").write_text(json.dumps(_jsonable(T)))
        out["trace_file"] = f"out/twin2/trace/{rid}.json"
    return out


def _safe(cfg):
    """One run; an exception is recorded with its traceback instead of stopping the experiment."""
    try:
        return run_one(cfg)
    except Exception:
        import traceback
        return dict(cfg=cfg, error=traceback.format_exc()[-3000:])


def run_id(cfg):
    parts = [cfg["facility"], cfg["policy"], f"s{cfg['seed']}"]
    for k, dflt in (("stock", "stocked"), ("crucible", 225), ("reuse", True), ("cu_budget", None),
                    ("fidelity", "fast"), ("cu_hidden", 0.0), ("seeding", None)):
        if cfg.get(k, dflt) != dflt:
            parts.append(f"{k}-{cfg[k]}")
    return "_".join(str(p) for p in parts)


def _jsonable(x):
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x


def run(names, workers=3):
    """Every run of the named experiments in one process pool (so the pool never idles on one experiment's tail),
    in the order the experiments are named, the slow policies first within each; each result is appended to its
    experiment's file as soon as it finishes."""
    from concurrent.futures import as_completed
    RUNS.mkdir(parents=True, exist_ok=True)
    slow = {"saasbo": 0, "bofn_blend": 1, "bofn_saas": 1, "bofn": 2, "gpbo": 3, "saasmap": 3, "cost_aware": 4}
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
                    fh.write(json.dumps(_jsonable(res)) + "\n")
                print(f"  {name} {run_id(c)}: ERROR {res['error'].splitlines()[-1]}", flush=True)
                continue
            with (RUNS / f"{name}.jsonl").open("a") as fh:
                fh.write(json.dumps(_jsonable(res)) + "\n")
            print(f"  {name} {run_id(c)}: FLAIME {res['campaigns']['flaime_al']['best_new']:.3f} "
                  f"ONR {res['campaigns']['onr_cu']['best_new']:.3f} ({res['seconds']} s; "
                  f"{time.time() - t0:.0f} s in)", flush=True)


def load(name):
    p = RUNS / f"{name}.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []


# ---------------------------------------------------------------------------------------------------- summarising
def hit(curve, target, col):
    """(days, money, index) at which a best-so-far curve first reaches target, or None."""
    for i, (d, usd, u) in enumerate(curve):
        if u >= target - 1e-12:
            return d, usd, i
    return None


def targets():
    """Two targets per campaign, from twin/oracle.py: T1, a new alloy that matches or beats the state of the art
    (the best reference alloy's true utility); T2, one halfway from the state of the art to the best the oracle found."""
    p = OUT / "oracle.json"
    if p.exists():
        o = json.loads(p.read_text())
        t1 = {k: o[k]["sota_utility"] for k in ("flaime_al", "onr_cu")}
        t2 = {k: round(o[k]["sota_utility"] + 0.5 * (o[k]["best_found"]["utility"] - o[k]["sota_utility"]), 4)
              for k in ("flaime_al", "onr_cu")}
        return {"T1": t1, "T2": t2}
    return {"T1": {"flaime_al": 0.42, "onr_cu": 0.56}, "T2": {"flaime_al": 0.64, "onr_cu": 0.66}}


def summary():
    T = targets()
    S = dict(targets=T, experiments={})
    for name in EXPERIMENTS:
        rows = load(name)
        if not rows:
            continue
        groups = {}
        for r in rows:
            c = r["cfg"]
            key = run_id(dict(c, seed=0)).replace("_s0", "")
            groups.setdefault(key, []).append(r)
        E = {}
        for key, rs in groups.items():
            g = dict(n=len(rs), policy=rs[0]["cfg"]["policy"], facility=rs[0]["cfg"]["facility"],
                     cfg={k: v for k, v in rs[0]["cfg"].items() if k not in ("seed", "events")},
                     seconds=float(np.mean([r["seconds"] for r in rs])), campaigns={})
            for camp in ("flaime_al", "onr_cu"):
                best = [r["campaigns"][camp].get("best_new", r["campaigns"][camp]["best"]) for r in rs]
                cur = [r["campaigns"][camp].get("curve_new", r["campaigns"][camp]["curve"]) for r in rs]
                tt = {}
                for tn, tv in T.items():
                    hits = [hit(c, tv[camp], 2) for c in cur]
                    tt[tn] = dict(target=tv[camp], hit_frac=sum(1 for h in hits if h) / len(rs),
                                  days=[h[0] if h else None for h in hits], usd=[h[1] if h else None for h in hits],
                                  n=[h[2] + 1 if h else None for h in hits])
                g["campaigns"][camp] = dict(
                    best_mean=float(np.mean(best)), best_se=float(np.std(best, ddof=1) / np.sqrt(len(best))) if len(best) > 1 else 0.0,
                    hit_frac=tt["T1"]["hit_frac"], targets=tt,
                    best_incl_refs=float(np.mean([r["campaigns"][camp]["best"] for r in rs])),
                    spent_mean=float(np.mean([r["campaigns"][camp]["spent"] for r in rs])),
                    n_demonstrated=float(np.mean([r["campaigns"][camp]["n_demonstrated"] for r in rs])),
                    n_discoveries=float(np.mean([r["campaigns"][camp]["n_discoveries"] for r in rs])),
                    n_designs=float(np.mean([r["campaigns"][camp]["n_designs"] for r in rs])),
                    returned_g=float(np.mean([r["campaigns"][camp].get("returned_g", 0) for r in rs])),
                    curves=cur)
            g["utilization"] = {k: float(np.mean([r["utilization"].get(k, 0) for r in rs]))
                                for k in rs[0]["utilization"]}
            E[key] = g
        S["experiments"][name] = E
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "bench2_summary.json").write_text(json.dumps(_jsonable(S)))
    return S


def main(argv):
    if not argv or argv[0] == "summary":
        S = summary()
        for name, E in S["experiments"].items():
            print(f"== {name}")
            for key, g in E.items():
                f, o = g["campaigns"]["flaime_al"], g["campaigns"]["onr_cu"]
                print(f"  {key:45s} n={g['n']:2d} FLAIME {f['best_mean']:.3f}±{f['best_se']:.3f} hit {f['hit_frac']:.0%}"
                      f"  ONR {o['best_mean']:.3f}±{o['best_se']:.3f} hit {o['hit_frac']:.0%}  ({g['seconds']:.0f} s)")
        return
    if argv[0] == "run":
        names = argv[1:] or ["main"]
        run(names, int(os.environ.get("TWIN_WORKERS", "3")))
        summary()
        return
    if argv[0] == "one":
        cfg = _cfg(argv[1], 0, facility=argv[2] if len(argv) > 2 else "vertical_lab")
        r = run_one(cfg)
        print(json.dumps({k: (v["best"], v["n_demonstrated"]) for k, v in r["campaigns"].items()}), r["seconds"])
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
