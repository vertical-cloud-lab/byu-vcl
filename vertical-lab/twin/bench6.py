"""Round 6 of the benchmark: money tracked instead of limited (twin/round6.py). The grid, and the tools a compute
slice needs to run part of it.

    python -m twin.bench6 status                    # runs and seeds per arm, done and left, estimated hours (left.md)
    python -m twin.bench6 ids FILE|ID ... [--slice K] [--workers N]   # run a list of run ids (a compute slice)
    python -m twin.bench6 slices N [GROUP ...]      # split the runs left into N lists of about equal run time
    python -m twin.bench6 run [experiment ...]      # run whole experiments here (not meant for one job: see status)
    python -m twin.bench6 smoke [DAYS] [GROUP ...]  # seed 0 of each group for DAYS simulated days, timed, rows not kept
    python -m twin.bench6 fold                      # append the slices' rows to their experiments, then pack
    python -m twin.bench6 pack | snapshot           # merge appended rows into runs/<experiment>.jsonl.xz
    python -m twin.bench6 one LAB PLAN POLICY STOCK [SEED] [opt=value ...]   # one run, printed (TWIN6_DAYS shortens)

Every row is made under round 6's pin (``PIN``; twin/repro.py), set here if ``TWIN_PIN`` is unset, and records the CPU,
the kernels and package versions (``env``), the commit, the tree hash of ``twin/`` at that commit and whether
``twin/`` differed from it (``code``), the notes applied (``r6.notes``) and the sha256 of its event log.

The arms are round 5's: ``lab`` is ``vertical`` (the automated lab, built from day 0 while experiments run on every
route) or ``conventional`` (existing equipment, core facilities and partners, run by people); ``stock`` is ``reorder``
(the reorder-point heuristic) or ``lean`` (each charge's metal ordered when it is needed). ``fast`` runs the
heuristic on aluminium and the funnel on copper; ``bofn3`` and ``pkgfn3`` run time-aware BOFN or pKGFN on both
campaigns (twin/opt/net6.py). Every sensitivity is run with all three.
"""
from __future__ import annotations

import hashlib
import json
import lzma
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from twin import bench2 as B2
from twin import bench3 as B3

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("TWIN6_OUT", HERE.parent / "out" / "twin6"))
RUNS = OUT / "runs"
EVENTS = OUT / "events"
CHECKS = HERE.parent / "out" / "twin6" / "checks"
SLICES = HERE.parent / "out" / "twin6" / "slices"
DAYS = 730
PIN = "portable"                       # round 6's pin (twin/repro.py); bench5's rows were made under "avx2"
ALIAS = {"fast": "heuristic+tiered"}
POLICIES = ("fast", "bofn3", "pkgfn3")
ARMS = (("vertical", "parallel", "reorder"), ("vertical", "parallel", "lean"),
        ("conventional", "external", "reorder"), ("conventional", "external", "lean"))
N_SEEDS = int(os.environ.get("TWIN6_SEEDS", "16"))
FLOOR = 12                             # an arm is reported from 12 seeds
# The simulated candidates the policies see, as a multiple of round 5's (64 new a day, 128 kept): the main arms'
# scale, chosen from the pilot (out/twin6/checks/hpc_pilot.json; notes/twin_round6.md, section 4).
HPC_SCALE = 1
HPC_SCALES = (1, 4, 16, 64, 256)
LATE_D = 240.0                         # "late crucibles": the pool arrives 240 days later than its lead time


def _cfg(lab, plan, policy, stock, seed, days=DAYS, **opts):
    o = dict(lab=lab, decisions="nominal", atom="derived", used=True, hpc=dict(scale=HPC_SCALE))
    for k, v in opts.items():
        if k == "hpc" and not isinstance(v, dict):
            v = dict(scale=int(v) if float(v) == int(float(v)) else float(v))
        if k == "late":
            k, v = "crucibles", dict(late_d=float(v))
        if k == "used" and isinstance(v, str):
            v = v.lower() in ("1", "true", "yes")
        o[k] = v
    return dict(lab=lab, plan=plan, policy=policy, stock=stock, seed=int(seed), days=days, opts=o)


def _arms(seeds, arms=ARMS, **opts):
    return [_cfg(lab, plan, p, stock, s, **opts) for s in seeds for p in POLICIES for lab, plan, stock in arms]


_S = range(N_SEEDS)
_V = ARMS[:2]
EXPERIMENTS = {
    # comparison 1, like with like four ways: the same policy and the same stock rule in both labs
    "arms": _arms(_S),
    # comparison 2: round 4's three plans (parallel is "arms"), stocked
    "plans": [_cfg("vertical", pl, p, "reorder", s) for s in _S for p in POLICIES for pl in ("wait", "external")],
    # decision time: no delay and slow windows (nominal is "arms"), the four arms
    "dec_none": _arms(_S, decisions="none"),
    "dec_slow": _arms(_S, decisions="slow"),
    # the automated atomizer's cycle: 3 h and slow (derived is "arms"), the automated lab both ways
    "atom": [c for a in ("3h", "slow") for c in _arms(_S, _V, atom=a)],
    # late crucibles: the pool arrives after the cell is integrated; the automated lab both ways
    "crucibles_late": _arms(_S, _V, crucibles=dict(late_d=LATE_D)),
    # what used equipment buys: the automated lab with every station bought new, stocked
    "noused": _arms(_S, _V[:1], used=False),
    # the HPC stream's scale (the main arms run at HPC_SCALE), both labs stocked
    "hpc": [c for sc in HPC_SCALES if sc != HPC_SCALE for c in _arms(_S, ARMS[::2], hpc=dict(scale=sc))],
}
# the order of work: the comparison first, then what it rests on, then the sensitivities
TIERS = {"arms": 1, "plans": 2, "hpc": 2, "noused": 3, "crucibles_late": 3, "atom": 4, "dec_none": 4, "dec_slow": 4}


def run_id(cfg):
    o = cfg.get("opts") or {}
    parts = ["r6", cfg["lab"], cfg["plan"], cfg["policy"], cfg["stock"], f"s{cfg['seed']}"]
    if o.get("decisions", "nominal") != "nominal":
        parts.append(f"dec-{o['decisions']}")
    if o.get("atom", "derived") != "derived":
        parts.append(f"atom-{o['atom']}")
    if not o.get("used", True):
        parts.append("noused")
    sc = (o.get("hpc") or {}).get("scale", 1)
    if sc != HPC_SCALE:
        parts.append(f"hpc{sc:g}")
    late = (o.get("crucibles") or {}).get("late_d")
    if late:
        parts.append(f"late{late:g}")
    for k in sorted(o):
        if k in ("lab", "decisions", "atom", "used", "hpc", "crucibles"):
            continue
        parts.append(f"{k}-{o[k]}")
    if cfg.get("days", DAYS) != DAYS:
        parts.append(f"d{cfg['days']}")
    return "_".join(str(p) for p in parts)


def group_key(cfg):
    return run_id(dict(cfg, seed=0)).replace("_s0", "")


def by_id() -> dict:
    out = {}
    for name, cfgs in EXPERIMENTS.items():
        for c in cfgs:
            rid = run_id(c)
            assert rid not in out, rid
            out[rid] = (name, c)
    return out


def pol_names(name):
    name = ALIAS.get(name, name)
    al, cu = (name.split("+") + [name])[:2] if "+" in name else (name, name)
    return {"flaime_al": al, "onr_cu": cu}


def make_policies(name, seed):
    from twin.opt import net6
    return {k: net6.make6(v, k, seed) for k, v in pol_names(name).items()}


def simulate(cfg: dict):
    import torch
    torch.set_num_threads(1)
    from twin import repro as R
    R.seed_globals(cfg["seed"])
    rng0 = R.torch_rng_state()
    from twin import campaign as C
    from twin import round6 as R6
    from twin import spaces as SP
    from twin.opt.gp import STATS
    t0 = time.time()
    fits0 = dict(STATS)
    days = int(os.environ.get("TWIN6_DAYS", cfg.get("days", DAYS)))
    specs = {k: C.Spec(k, R6.REFERENCE_USD[k], B2.WIP[k], cfg["seed"], 1.0, stock=cfg["stock"])
             for k in ("flaime_al", "onr_cu")}
    pols = make_policies(cfg["policy"], cfg["seed"])
    tw = R6.Twin6(specs, pols, plan=cfg["plan"], seed=cfg["seed"], horizon_days=days, opts=cfg.get("opts"),
                  pol_names=pol_names(cfg["policy"]))
    s = tw.run()
    out = dict(cfg=cfg, days_run=days, seconds=round(time.time() - t0, 1),
               gp={k: round(STATS[k] - fits0.get(k, 0), 3) for k in STATS}, campaigns={})
    T = B2.targets()
    r6 = tw.report6()
    sp = r6["spend"]
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
        n_new = len({d["design"] for d in new})
        # money: to each target, and per new alloy tested, without and with the lab's fixed costs (capital,
        # facility and labour, shared between the campaigns 2 : 1 as round 5's budgets were)
        share = sp["fixed_share"][k]
        direct = sum(sp["totals"]["campaigns"][k][cat] for cat in ("stock", "consumables", "partners_services"))
        fixed = share * sum(sp["totals"]["lab"].values())
        to_t = {}
        for tn in ("T1", "T2"):
            h = B2.hit(curve_new, T[tn][k], 2)
            if h is None:
                to_t[tn] = None
                continue
            at = tw.spend_at(h[0] * 24.0)
            dct = sum(at["campaigns"][k][cat] for cat in ("stock", "consumables", "partners_services"))
            to_t[tn] = dict(day=h[0], direct_usd=round(dct, 2), by=at["campaigns"][k],
                            with_fixed_usd=round(dct + share * sum(at["lab"].values()), 2),
                            lab={kk: round(vv, 2) for kk, vv in at["lab"].items()})
        out["campaigns"][k] = dict(
            spent=round(c["spent"], 2), reference_usd=R6.REFERENCE_USD[k], best=c["best"], best_new=best,
            curve_new=curve_new, n_demonstrated=c["n_demonstrated"], n_new_demonstrated=len(new), n_new_alloys=n_new,
            n_designs=r6["counters"][k]["designed"], n_lots=c["n_lots"], n_builds=c["n_builds"], refused=c["refused"],
            spend_by=c["spend_by"], done=c["done"], stops=c["stops"], status=c["status"],
            n_alloys_made=c["n_alloys_made"], prov_usd=round(camp.prov_usd, 2),
            policy_counts=dict(getattr(pol, "counts", {}) or {}), spend_curve=B3._spend_curve(camp),
            spend_to_target=to_t,
            per_alloy=dict(n_new_alloys=n_new,
                           direct_usd=round(direct / n_new, 2) if n_new else None,
                           with_fixed_usd=round((direct + fixed) / n_new, 2) if n_new else None,
                           direct_total_usd=round(direct, 2), fixed_share_usd=round(fixed, 2),
                           stock_left_usd=sp["stock_left_usd"][k]),
            demonstrated=[{kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in d.items()}
                          for d in sorted(c["demonstrated"], key=lambda d: d["t_h"])])
    out["r4"] = tw.report()
    out["r6"] = r6
    out["torch_rng_used"] = R.torch_rng_used(rng0)
    out["env"] = R.fingerprint()
    out["code"] = _code()
    return out, tw


def _code():
    """The commit the row was made from, the tree hash of twin/ at that commit (the same for two commits whose
    twin/ is identical), and whether twin/ differed from it when the row was made."""
    import subprocess
    try:
        g = lambda *a: subprocess.run(["git", *a], cwd=HERE, capture_output=True, text=True).stdout
        c = g("rev-parse", "HEAD").strip()
        tree = g("rev-parse", "HEAD:vertical-lab/twin").strip()
        d = g("status", "--porcelain", "--", ".")
        return dict(commit=c, twin_tree=tree, twin_dirty=any(l[3:].strip().endswith(".py") for l in d.splitlines()))
    except Exception:
        return dict(commit=None, twin_tree=None, twin_dirty=None)


def events_kept(name, cfg) -> bool:
    """Event logs that go into the repository: the comparison's (``arms``) and seeds 0-1 of everything else. Every
    row carries its log's sha256, so a rerun can be checked against a log that was not kept."""
    return name == "arms" or cfg["seed"] < 2


def event_log(tw, cfg) -> dict:
    rid = run_id(cfg)
    log = tw.event_log(meta=dict(cfg=cfg, run_id=rid))
    cash = {}
    for k, c in tw.campaigns.items():
        agg = {}
        for t, u, cat, _ in c.cash:
            key = (int(t // 24), cat)
            agg[key] = agg.get(key, 0.0) + u
        cash[k] = sorted((d, cat, round(u, 2)) for (d, cat), u in agg.items())
    log["round6"] = dict(stock={k: dict(use=c.use_log, orders=c.stock_orders, stockouts=c.stockouts)
                                for k, c in tw.campaigns.items()},
                         held=tw.held_log, daily={k: v for k, v in tw.daily.items()}, cash_daily=cash,
                         crucibles={f: p.uses for f, p in tw.fac4.pools.items()})
    return B2._jsonable(log)


def run_one(cfg: dict, name: str | None = None) -> dict:
    out, tw = simulate(cfg)
    rid = run_id(cfg)
    data = json.dumps(event_log(tw, cfg)).encode()
    out["events_sha256"] = hashlib.sha256(data).hexdigest()
    EVENTS.mkdir(parents=True, exist_ok=True)
    (EVENTS / f"{rid}.json.xz").write_bytes(lzma.compress(data, preset=6))
    out["events_file"] = f"out/twin6/events/{rid}.json.xz"
    out["events_kept"] = events_kept(name or by_id().get(rid, ("", None))[0], cfg)
    return json.loads(json.dumps(B2._jsonable(out)))


def _safe(args):
    name, cfg = args
    try:
        return run_one(cfg, name)
    except Exception:
        import traceback
        return dict(cfg=cfg, error=traceback.format_exc()[-4000:])


def read_events(path) -> dict:
    p = Path(path)
    b = p.read_bytes()
    return json.loads(lzma.decompress(b) if p.suffix == ".xz" else b)


# ------------------------------------------------------------------------------------------------- rows on disk
def _lines(name):
    """An experiment's rows: the packed file, rows appended since, and any slice's rows not yet folded in."""
    out = []
    px = RUNS / f"{name}.jsonl.xz"
    if px.exists():
        out += lzma.decompress(px.read_bytes()).decode().splitlines()
    for p in [RUNS / f"{name}.jsonl"] + sorted(RUNS.glob(f"{name}.slice-*.jsonl")):
        if p.exists():
            out += p.read_text().splitlines()
    return [l for l in out if l.strip()]


def _done(name):
    done = set()
    for line in _lines(name):
        try:
            done.add(run_id(json.loads(line)["cfg"]))
        except Exception:
            pass
    return done


def load(name):
    return [json.loads(l) for l in _lines(name)]


def pack(keep_appended=False):
    for name in EXPERIMENTS:
        p = RUNS / f"{name}.jsonl"
        if not p.exists():
            continue
        seen, keep = set(), []
        for line in _lines(name):
            try:
                rid = run_id(json.loads(line)["cfg"])
            except Exception:
                continue
            if rid not in seen:
                seen.add(rid)
                keep.append(line)
        (RUNS / f"{name}.jsonl.xz").write_bytes(lzma.compress(("\n".join(keep) + "\n").encode(),
                                                              preset=9 | lzma.PRESET_EXTREME))
        if not keep_appended:
            p.unlink()
        print(f"{name}: {len(keep)} rows packed")


def fold():
    """Append every slice's rows to its experiment's appended file (one row per run id, the first kept), remove the
    slice files, and pack. Prints what each slice brought and anything that came twice."""
    for name in EXPERIMENTS:
        have = _done_no_slices(name)
        for p in sorted(RUNS.glob(f"{name}.slice-*.jsonl")):
            new, twice = [], []
            for line in p.read_text().splitlines():
                if not line.strip():
                    continue
                rid = run_id(json.loads(line)["cfg"])
                (twice if rid in have else new).append((rid, line))
                have.add(rid)
            with (RUNS / f"{name}.jsonl").open("a") as fh:
                for _, line in new:
                    fh.write(line + "\n")
            p.unlink()
            print(f"{p.name}: {len(new)} rows folded in" + (f"; already there: {[r for r, _ in twice]}" if twice else ""))
    pack()


def _done_no_slices(name):
    done = set()
    px = RUNS / f"{name}.jsonl.xz"
    lines = lzma.decompress(px.read_bytes()).decode().splitlines() if px.exists() else []
    p = RUNS / f"{name}.jsonl"
    lines += p.read_text().splitlines() if p.exists() else []
    for line in lines:
        if line.strip():
            done.add(run_id(json.loads(line)["cfg"]))
    return done


# ------------------------------------------------------------------------------------------------- timing
def timings() -> dict:
    """Seconds a two-year run of each group takes: measured in full where a full run was timed, otherwise scaled
    from a shortened smoke run (``checks/smoke.json``; each entry says which)."""
    p = CHECKS / "smoke.json"
    return json.loads(p.read_text()).get("groups", {}) if p.exists() else {}


def est_seconds(cfg, tm=None) -> float | None:
    tm = timings() if tm is None else tm
    t = tm.get(group_key(cfg))
    return None if t is None else float(t["seconds_2y"])


def _left():
    out = []
    for name, cfgs in EXPERIMENTS.items():
        done = _done(name)
        out += [(name, c) for c in cfgs if run_id(c) not in done]
    return out


def order(todo):
    """The order of work: by tier, the first 12 seeds of an arm before its last 4, seed by seed across arms."""
    return sorted(todo, key=lambda t: (TIERS.get(t[0], 9), t[1]["seed"] >= FLOOR, t[1]["seed"], t[0], run_id(t[1])))


# ------------------------------------------------------------------------------------------------- running
def _run(todo, workers, suffix=""):
    RUNS.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    n_err = 0
    with ProcessPoolExecutor(workers, max_tasks_per_child=1) as ex:      # a fresh interpreter for every run
        futs = {ex.submit(_safe, (name, c)): (name, c) for name, c in todo}
        for fut in as_completed(futs):
            name, c = futs[fut]
            res = fut.result()
            if "error" in res:
                n_err += 1
                with (RUNS / f"{name}{suffix}.errors.jsonl").open("a") as fh:
                    fh.write(json.dumps(B2._jsonable(res)) + "\n")
                print(f"  {name} {run_id(c)}: ERROR {res['error'].splitlines()[-1]}", flush=True)
                continue
            with (RUNS / f"{name}{suffix}.jsonl").open("a") as fh:
                fh.write(json.dumps(res) + "\n")
            print(f"  {name} {run_id(c)}: Al {res['campaigns']['flaime_al']['best_new']:.3f} "
                  f"Cu {res['campaigns']['onr_cu']['best_new']:.3f} ({res['seconds']} s; "
                  f"{time.time() - t0:.0f} s in)", flush=True)
    return n_err


def run(names, workers=4):
    todo = order([(n, c) for n, c in _left() if n in names])
    print(f"{len(todo)} runs to do", flush=True)
    return _run(todo, workers)


def run_ids(ids, workers=4, slice_k=None):
    """Run the given run ids (a compute slice's list), skipping those already done. Rows go to
    ``runs/<experiment>.slice-<K>.jsonl`` with ``--slice K`` (so slices never write the same file), else to
    ``runs/<experiment>.jsonl``."""
    table = by_id()
    unknown = [i for i in ids if i not in table]
    if unknown:
        raise SystemExit(f"unknown run ids: {unknown[:5]}{' ...' if len(unknown) > 5 else ''}")
    done = {n: _done(n) for n in EXPERIMENTS}
    todo = [table[i] for i in ids if i not in done[table[i][0]]]
    print(f"{len(ids)} ids, {len(ids) - len(todo)} already done, {len(todo)} to run", flush=True)
    tm = timings()
    todo.sort(key=lambda t: -(est_seconds(t[1], tm) or 0.0))             # the long ones first
    return _run(todo, workers, f".slice-{slice_k}" if slice_k is not None else "")


def slices(n: int, groups=None):
    """Split the runs left (optionally only some experiments or tiers: ``arms``, ``tier1`` ...) into ``n`` lists of
    about equal estimated run time, written to ``out/twin6/slices/slice-<k>.txt``."""
    tm = timings()
    todo = order(_left())
    if groups:
        want = set(groups)
        todo = [t for t in todo if t[0] in want or f"tier{TIERS.get(t[0], 9)}" in want]
    est = [(est_seconds(c, tm) or 600.0, name, c) for name, c in todo]
    bins = [[0.0, []] for _ in range(n)]
    for sec, name, c in sorted(est, key=lambda x: -x[0]):
        b = min(bins, key=lambda b: b[0])
        b[0] += sec
        b[1].append(run_id(c))
    SLICES.mkdir(parents=True, exist_ok=True)
    for k, (sec, ids) in enumerate(bins, 1):
        (SLICES / f"slice-{k}.txt").write_text("\n".join(ids) + "\n")
        print(f"slice-{k}.txt: {len(ids)} runs, about {sec / 3600:.1f} core-hours "
              f"({sec / 3600 / 4:.1f} h on 4 cores)")


def smoke(days=None, groups=None, workers=3, seed=0):
    """Seed 0 of each group, run for ``days`` simulated days (None: the full two years), timed. Rows are not kept:
    outputs go under /tmp. Writes ``checks/smoke.json``; a shortened run's two-year time is its seconds scaled by
    days (a lower bound for the policies that fit GPs, whose cost grows with the data)."""
    from twin import repro as R
    seen, todo = set(), []
    for name, cfgs in EXPERIMENTS.items():
        for c in cfgs:
            g = group_key(c)
            if c["seed"] == seed and g not in seen and (not groups or g in groups or name in groups):
                seen.add(g)
                todo.append((name, c))
    if days is not None:
        os.environ["TWIN6_DAYS"] = str(int(days))
    p = CHECKS / "smoke.json"
    rec = json.loads(p.read_text()) if p.exists() else dict(groups={})
    rec.update(cpu=R.cpu_model(), pin=os.environ.get("TWIN_PIN"), workers=workers)
    t0 = time.time()
    with ProcessPoolExecutor(workers, max_tasks_per_child=1) as ex:
        futs = {ex.submit(_smoke_one, c): (name, c) for name, c in todo}
        for fut in as_completed(futs):
            name, c = futs[fut]
            r = fut.result()
            g = group_key(c)
            if "error" in r:
                print(f"  {g}: ERROR {r['error'].splitlines()[-1]}", flush=True)
                rec["groups"][g] = dict(error=r["error"][-600:])
                continue
            full = r["days_run"] >= DAYS
            old = rec["groups"].get(g) or {}
            if old.get("full") and not full:
                continue                             # keep a full run's timing over a shortened one's
            rec["groups"][g] = dict(experiment=name, seconds=r["seconds"], days=r["days_run"], full=full,
                                    seconds_2y=round(r["seconds"] * DAYS / r["days_run"], 1), gp_fits=r["gp"]["fits"],
                                    cpu=R.cpu_model(), concurrent=workers)
            print(f"  {g}: {r['seconds']} s for {r['days_run']} days ({time.time() - t0:.0f} s in)", flush=True)
            CHECKS.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    return rec


def _smoke_one(cfg):
    try:
        out, tw = simulate(cfg)
        json.dumps(event_log(tw, cfg))                # the event log must serialize too
        return json.loads(json.dumps(B2._jsonable(dict(seconds=out["seconds"], days_run=out["days_run"],
                                                       gp=out["gp"]))))
    except Exception:
        import traceback
        return dict(error=traceback.format_exc()[-3000:])


def status(write=True):
    tm = timings()
    L = ["# Round 6: runs done and left", "",
         "Made by `python -m twin.bench6 status`. An arm is reported from 12 seeds; the grid has 16 for every arm. "
         "Hours are core-hours for the runs left, from `checks/smoke.json` (a group timed in full is marked; the "
         "others are scaled from a shortened run and are a lower bound for BOFN and pKGFN).", "",
         "| Tier | Experiment | Arm | Seeds done | Seeds left | s per run | Core-hours left |", "|---|---|---|---|---|---|---|"]
    tot_left, tot_runs, hours, unknown = 0, 0, {}, 0
    for name in sorted(EXPERIMENTS, key=lambda n: (TIERS.get(n, 9), n)):
        cfgs = EXPERIMENTS[name]
        done = _done(name)
        arms = {}
        for c in cfgs:
            a = arms.setdefault(group_key(c), [[], [], c])
            a[0 if run_id(c) in done else 1].append(c["seed"])
        for g, (d, l, c0) in arms.items():
            tot_left += len(l)
            tot_runs += len(d) + len(l)
            t = tm.get(g)
            sec = None if t is None or "seconds_2y" not in t else t["seconds_2y"]
            h = None if sec is None else sec * len(l) / 3600.0
            if h is None:
                unknown += len(l)
            else:
                hours[TIERS.get(name, 9)] = hours.get(TIERS.get(name, 9), 0.0) + h
            L.append(f"| {TIERS.get(name, 9)} | {name} | `{g}` | {len(d)} | {len(l)} | "
                     + ("?" if sec is None else f"{sec:,.0f}" + ("" if t.get("full") else " (scaled)")) + " | "
                     + ("?" if h is None else f"{h:.1f}") + " |")
    L += ["", f"Runs: {tot_runs} in the grid, {tot_left} left."]
    if hours:
        L.append("Core-hours left by tier: " + "; ".join(f"tier {k}: {v:,.0f}" for k, v in sorted(hours.items()))
                 + f"; all: {sum(hours.values()):,.0f}" + (f" ({unknown} runs not timed)" if unknown else "") + ".")
    txt = "\n".join(L) + "\n"
    if write:
        (HERE.parent / "out" / "twin6").mkdir(parents=True, exist_ok=True)
        (HERE.parent / "out" / "twin6" / "left.md").write_text(txt)
    print(txt)


def main(argv):
    if os.environ.get("TWIN_PIN") is None:
        os.environ["TWIN_PIN"] = PIN
        os.environ["PYTHONHASHSEED"] = "0"
        sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, "-m", "twin.bench6"] + argv)
    from twin import repro as R
    R.reexec_pinned("twin.bench6")
    workers = int(os.environ.get("TWIN_WORKERS", "4"))
    if "--workers" in argv:
        i = argv.index("--workers")
        workers = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    if not argv or argv[0] == "status":
        status()
        return 0
    if argv[0] in ("pack", "snapshot"):
        pack(keep_appended=argv[0] == "snapshot")
        status()
        return 0
    if argv[0] == "fold":
        fold()
        status()
        return 0
    if argv[0] == "run":
        n = run(argv[1:] or list(EXPERIMENTS), workers)
        status()
        return 1 if n else 0
    if argv[0] == "ids":
        args = argv[1:]
        k = None
        if "--slice" in args:
            i = args.index("--slice")
            k = args[i + 1]
            args = args[:i] + args[i + 2:]
        ids = []
        for a in args:
            ids += [l.strip() for l in Path(a).read_text().splitlines() if l.strip()] if Path(a).exists() else [a]
        return 1 if run_ids(ids, workers, k) else 0
    if argv[0] == "slices":
        slices(int(argv[1]), argv[2:])
        return 0
    if argv[0] == "smoke":
        days = None if len(argv) < 2 or argv[1] in ("full", "730") else int(argv[1])
        smoke(days, argv[2:], workers)
        return 0
    if argv[0] == "one":
        lab, pl, pol, stock = argv[1:5]
        seed = int(argv[5]) if len(argv) > 5 else 0
        extra = dict(a.split("=", 1) for a in argv[6:])
        cfg = _cfg(lab, pl, pol, stock, seed, **extra)
        out, tw = simulate(cfg)
        r6 = out["r6"]
        print(run_id(cfg), out["seconds"], "s for", out["days_run"], "days; GP fits", out["gp"]["fits"])
        for k, c in out["campaigns"].items():
            print(k, "best_new", c["best_new"], "tested", c["n_new_alloys"], "spent", round(c["spent"]),
                  "to target", {t: (v and (v["day"], round(v["direct_usd"]))) for t, v in c["spend_to_target"].items()},
                  "per alloy", c["per_alloy"]["direct_usd"], c["per_alloy"]["with_fixed_usd"])
            print("   status", c["status"], "counts", c["policy_counts"])
        print("spend, campaigns", json.dumps(r6["spend"]["totals"]["campaigns"]))
        print("spend, lab", json.dumps(r6["spend"]["totals"]["lab"]))
        print("crucibles", json.dumps({f: {kk: v[kk] for kk in ("arrive_d", "melts", "runs_waited", "wait_h_total",
                                                               "derived_cycle_start_d")}
                                       for f, v in r6["crucibles"]["families"].items()}))
        print("atom", r6["atom"]["runs"], r6["atom"]["runs_by"], "used", r6["used"]["source"],
              sorted(r6["used"]["items"]))
        print("counters", json.dumps(r6["counters"]))
        print("hpc", json.dumps({k: {kk: v[kk] for kk in ("materialized", "evicted", "designs_in_memory")}
                                 for k, v in r6["hpc"]["campaigns"].items()}))
        print("stock", {k: {kk: v[kk] for kk in ("mode", "n_charges", "n_stockouts", "days_waited", "stock_usd",
                                                    "left_usd")} for k, v in r6["stock"].items()})
        print("idle", json.dumps({k: {g: [(x["start_d"], x["days"], x["cause"], x["flag"]) for x in v[:8]]
                                      for g, v in d.items()} for k, d in r6["idle"]["stretches"].items()}))
        return 0
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
