"""Run the two campaigns at once, many times: policies x supply scenarios x facilities x seeds.

    python3 -m twin.bench run [experiment ...]   # -> out/twin/runs/<experiment>.jsonl   (3 worker processes)
    python3 -m twin.bench summary                # -> out/twin/bench_summary.json
    python3 -m twin.bench one                    # one run, printed

Experiments (``EXPERIMENTS``): ``main`` (the three policies, the proposals' facility, the historical market, 20
seeds); ``supply`` (five market scenarios); ``facility`` (the proposals' partners against PR 318's lab); ``sharing``
(the two campaigns on one lab against a lab each); ``kappa`` (how much of the nucleant effect the CALPHAD nodes miss,
as in DAL's prelim). Every run is one twin-year, both campaigns from day 0, FLAIME with $120k and ONR with $60k of
non-personnel money (``BUDGET``: assumed; see notes/twin.md).
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
OUT = HERE.parent / "out" / "twin"
RUNS = OUT / "runs"
BUDGET = {"flaime_al": 120_000.0, "onr_cu": 60_000.0}
WIP = {"flaime_al": 24, "onr_cu": 8}
HORIZON_DAYS = 365

EXPERIMENTS = {
    "main": [dict(facility="proposed", scenario="historical", policy=p, seed=s, kappa=1.0, isolated=False)
             for p in ("random", "tiered", "cost_aware") for s in range(20)],
    "supply": [dict(facility="proposed", scenario=sc, policy=p, seed=s, kappa=1.0, isolated=False)
               for sc in ("calm", "historical", "tariffs", "export_controls", "inflation")
               for p in ("random", "cost_aware") for s in range(10)],
    "facility": [dict(facility=f, scenario="historical", policy=p, seed=s, kappa=1.0, isolated=False)
                 for f in ("proposed", "vertical_lab") for p in ("random", "cost_aware") for s in range(10)],
    "sharing": [dict(facility="proposed", scenario="historical", policy="cost_aware", seed=s, kappa=1.0, isolated=i)
                for i in (False, True) for s in range(10)],
    "kappa": [dict(facility="proposed", scenario="historical", policy=p, seed=s, kappa=k, isolated=False)
              for k in (0.0, 0.5, 1.0) for p in ("tiered", "cost_aware") for s in range(10)],
    "calphad": [dict(facility="proposed", scenario="historical", policy=p, seed=s, kappa=1.0, isolated=False)
                for p in ("tiered_tc", "cost_aware_tc") for s in range(20)],
    # the proposals' scale-up: a gas-atomized lot of the first good alloy, and (FLAIME) an E8 plate from it
    "scaleup": [dict(facility="proposed", scenario="historical", policy="cost_aware_scaleup", seed=s, kappa=1.0,
                     isolated=False) for s in range(20)],
    # the ONR proposal's H4: choosing new experiments while others are pending, against one at a time
    "wip": [dict(facility="proposed", scenario="historical", policy="cost_aware", seed=s, kappa=1.0, isolated=False,
                 wip=w) for w in ((1, 1), (6, 3), (24, 8)) for s in range(10)],
}


def run_one(cfg: dict) -> dict:
    from twin import campaign as C, policies as P
    t0 = time.time()
    wip = cfg.get("wip") or (WIP["flaime_al"], WIP["onr_cu"])
    specs = {"flaime_al": C.Spec("flaime_al", BUDGET["flaime_al"], wip[0], cfg["seed"], cfg["kappa"]),
             "onr_cu": C.Spec("onr_cu", BUDGET["onr_cu"], wip[1], cfg["seed"], 1.0)}
    pols = {k: P.POLICIES[cfg["policy"]](k, cfg["seed"]) for k in specs}
    tw = C.Twin(specs, pols, scenario=cfg["scenario"], facility=cfg["facility"], seed=cfg["seed"],
                horizon_days=HORIZON_DAYS, isolated=cfg["isolated"])
    out = tw.run()
    res = dict(cfg=cfg, seconds=round(time.time() - t0, 2), campaigns={})
    for k in specs:
        o = out[k]
        c = tw.campaigns[k]
        res["campaigns"][k] = dict(
            spent=round(o["spent"], 2), best=o["best"], curve=[(round(a, 3), round(b, 2), round(u, 4))
                                                                for a, b, u in o["curve"]],
            n_demonstrated=o["n_demonstrated"], n_discoveries=o["n_discoveries"], n_designs=o["n_designs"],
            n_lots=o["n_lots"], n_builds=o["n_builds"], n_sims=o["n_sims"], refused=o["refused"],
            orders=o["orders"], backorders=o["backorders"], spend_by=o["spend_by"],
            order_cost=round(sum(x.cost for x in c.stores.orders), 2),
            wait_days=round(float(np.mean([x.arrival_day - x.placed_day for x in c.stores.orders
                                           if x.placed_day >= 0] or [0.0])), 2),
            best_alloy=_best(o["demonstrated"]),
            vectors=_vectors(k, o["demonstrated"]))
    res["utilization"] = out["utilization"]["shared"]
    res["market_events"] = out["market_events"]
    return res


def _vectors(camp, dem):
    """Each demonstrated alloy's objective desirabilities (the multi-objective view; 0 if infeasible)."""
    from twin.campaign import _desir
    out = []
    ref_c = 0.02897
    for d in dem:
        if camp == "flaime_al":
            v = [_desir(d["ys"], 150, 400), _desir(d["el"], 2, 15), _desir(1.5 * ref_c - d["cmdri"], 0, 1.5 * ref_c)]
        else:
            v = [_desir(d["ys"], 100, 400), _desir(d["el"], 5, 35), _desir(3 * 6.65 - d["rate"], 0, 2.5 * 6.65),
                 _desir(30 - d["ni"], 0, 30)]
        out.append([round(x, 4) for x in v] + [1 if d["feasible"] else 0, round(d["t_h"] / 24, 2)])
    return out


def hypervolume(vecs, n=20000, seed=0):
    """Monte Carlo hypervolume of the feasible desirability vectors, in the unit cube (reference point 0)."""
    pts = np.array([v[:-2] for v in vecs if v[-2] == 1], float)
    if len(pts) == 0:
        return 0.0
    rng = np.random.default_rng(seed)
    u = rng.random((n, pts.shape[1]))
    dom = np.zeros(n, bool)
    for p in pts:
        dom |= np.all(u <= p, axis=1)
    return float(dom.mean())


def _best(dem):
    if not dem:
        return None
    d = max(dem, key=lambda x: x["u"])
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()
            if k not in ("t_h",) and not isinstance(v, dict)}


def _jsonable(x):
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def run(names, workers=3):
    RUNS.mkdir(parents=True, exist_ok=True)
    for name in names:
        cfgs = EXPERIMENTS[name]
        path = RUNS / f"{name}.jsonl"
        done = set()
        if path.exists():
            for line in path.read_text().splitlines():
                c = json.loads(line)["cfg"]
                done.add(json.dumps(c, sort_keys=True))
        todo = [c for c in cfgs if json.dumps(c, sort_keys=True) not in done]
        t0 = time.time()
        with ProcessPoolExecutor(max_workers=workers) as ex, open(path, "a") as f:
            for i, r in enumerate(ex.map(run_one, todo)):
                f.write(json.dumps(_jsonable(r)) + "\n")
                f.flush()
                if i % 10 == 9 or i == len(todo) - 1:
                    print(f"{name}: {i + 1}/{len(todo)} in {time.time() - t0:.0f} s", flush=True)


def load(name):
    p = RUNS / f"{name}.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []


def step_at(curve, xs, col):
    """A best-so-far step curve sampled at xs (col 0: days, 1: spend)."""
    out = np.zeros(len(xs))
    for c in curve:
        out[np.asarray(xs) >= c[col]] = np.maximum(out[np.asarray(xs) >= c[col]], c[2])
    return out


TARGET = {"flaime_al": 0.6, "onr_cu": 0.45}


def summary():
    out = {}
    for name in EXPERIMENTS:
        rows = load(name)
        if not rows:
            continue
        groups = {}
        for r in rows:
            c = r["cfg"]
            key = "|".join(f"{k}={c[k]}" for k in ("facility", "scenario", "policy", "kappa", "isolated"))
            if c.get("wip"):
                key += f"|wip={c['wip'][0]}/{c['wip'][1]}"
            groups.setdefault(key, []).append(r)
        g_out = {}
        for key, rs in groups.items():
            g = dict(n=len(rs))
            for camp in ("flaime_al", "onr_cu"):
                b = np.array([r["campaigns"][camp]["best"] for r in rs])
                spend_hit, day_hit = [], []
                for r in rs:
                    hit = [c for c in r["campaigns"][camp]["curve"] if c[2] >= TARGET[camp]]
                    spend_hit.append(hit[0][1] if hit else np.nan)
                    day_hit.append(hit[0][0] if hit else np.nan)
                g[camp] = dict(
                    best_mean=float(b.mean()), best_se=float(b.std(ddof=1) / np.sqrt(len(b))) if len(b) > 1 else 0.0,
                    hit_frac=float(np.mean(np.isfinite(spend_hit))),
                    spend_to_target_median=float(np.nanmedian(spend_hit)) if np.isfinite(spend_hit).any() else None,
                    days_to_target_median=float(np.nanmedian(day_hit)) if np.isfinite(day_hit).any() else None,
                    demonstrated_mean=float(np.mean([r["campaigns"][camp]["n_demonstrated"] for r in rs])),
                    discoveries_mean=float(np.mean([r["campaigns"][camp]["n_discoveries"] for r in rs])),
                    spent_mean=float(np.mean([r["campaigns"][camp]["spent"] for r in rs])),
                    order_cost_mean=float(np.mean([r["campaigns"][camp]["order_cost"] for r in rs])),
                    wait_days_mean=float(np.mean([r["campaigns"][camp]["wait_days"] for r in rs])),
                    backorders_mean=float(np.mean([r["campaigns"][camp]["backorders"] for r in rs])),
                    lots_mean=float(np.mean([r["campaigns"][camp]["n_lots"] for r in rs])),
                    hv_mean=float(np.mean([hypervolume(r["campaigns"][camp].get("vectors", [])) for r in rs]))
                    if all("vectors" in r["campaigns"][camp] for r in rs) else None)
            g["seconds_mean"] = float(np.mean([r["seconds"] for r in rs]))
            g_out[key] = g
        out[name] = g_out
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "bench_summary.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


LABELS = {"random": "random, full chain", "tiered": "tiered (open CALPHAD)", "cost_aware": "cost-aware (open CALPHAD)",
          "cost_aware_scaleup": "cost-aware + gas atomization and E8 plate",
          "tiered_tc": "tiered (Thermo-Calc)", "cost_aware_tc": "cost-aware (Thermo-Calc)"}


def markdown(S=None) -> str:
    """The summary as markdown tables, one per experiment (for notes/twin.md)."""
    S = S or json.loads((OUT / "bench_summary.json").read_text())
    out = []
    for name, groups in S.items():
        out.append(f"**{name}**\n")
        out.append("| setting | n | FLAIME best (± SE) | hit 0.6 | $ to 0.6 | days to 0.6 | discoveries | ONR best (± SE) "
                   "| hit 0.45 | $ to 0.45 | days to 0.45 |")
        out.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for key, g in groups.items():
            kv = dict(x.split("=", 1) for x in key.split("|"))
            lab = LABELS.get(kv["policy"], kv["policy"])
            extra = []
            if name in ("supply",):
                extra.append(kv["scenario"])
            if name == "facility":
                extra.append(kv["facility"])
            if name == "sharing":
                extra.append("a lab each" if kv["isolated"] == "True" else "one shared lab")
            if name == "kappa":
                extra.append("kappa " + kv["kappa"])
            if name == "wip":
                extra.append("in flight at once: " + kv["wip"] + " (FLAIME/ONR)")
            lab = ", ".join(extra + [lab])
            f, c = g["flaime_al"], g["onr_cu"]
            k = lambda v: "-" if v is None else f"${v / 1000:.0f}k"
            d = lambda v: "-" if v is None else f"{v:.0f}"
            out.append(f"| {lab} | {g['n']} | {f['best_mean']:.2f} ± {f['best_se']:.2f} | {f['hit_frac']:.0%} | "
                       f"{k(f['spend_to_target_median'])} | {d(f['days_to_target_median'])} | {f['discoveries_mean']:.1f} | "
                       f"{c['best_mean']:.2f} ± {c['best_se']:.2f} | {c['hit_frac']:.0%} | "
                       f"{k(c['spend_to_target_median'])} | {d(c['days_to_target_median'])} |")
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "one"
    if cmd == "run":
        run(sys.argv[2:] or list(EXPERIMENTS), workers=int(os.environ.get("TWIN_WORKERS", "3")))
    elif cmd == "summary":
        print(json.dumps(summary(), indent=1)[:4000])
    elif cmd == "markdown":
        print(markdown(summary()))
    else:
        r = run_one(dict(facility="proposed", scenario="historical", policy="cost_aware", seed=0, kappa=1.0,
                         isolated=False))
        print(json.dumps(_jsonable({k: v for k, v in r.items() if k != "market_events"}), indent=1)[:3000])
