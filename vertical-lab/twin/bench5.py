"""Round 5 of the benchmark: two years from the day the money arrives (twin/round5.py).

    python3 -m twin.bench5 run [experiment ...]    # -> out/twin5/runs/<experiment>.jsonl, events/<run id>.json.xz
    python3 -m twin.bench5 status                  # what is done, what is left (out/twin5/left.md)
    python3 -m twin.bench5 pack                    # merge appended rows into runs/<experiment>.jsonl.xz
    python3 -m twin.bench5 snapshot                # the same, keeping the appended file (while runs go on)
    python3 -m twin.bench5 one LAB PLAN POLICY STOCK [SEED]   # one run, printed (TWIN5_DAYS shortens it)

Every row is made under round 3b's pin (twin/repro.py) with ``TWIN_PIN=avx2`` (set here if unset: the AVX2 kernels
run on any x86-64 runner). Under it a heuristic or funnel row reproduces bit for bit on every CPU tried; a BOFN or
pKGFN row is deterministic on one CPU model but doesn't reproduce on every other (notes/twin_round5.md,
"Reproducibility"). Every row records the CPU, the kernels and the package versions (``env``), the notes it includes
(``r5.notes``), and writes its event log, compressed with xz.

The arms. ``lab`` is ``vertical`` (round 4's parallel plan with round 5's set-up: the in-house stations from the
facility window, the partners and BYU's equipment from day 0) or ``conventional`` (BYU's existing equipment and
core facilities and the partners, run by people, at most 8 atomizations a week). ``stock`` is ``reorder`` (stocked:
the reorder-point heuristic) or ``lean`` (each charge's metal ordered when it is needed). A policy ``A+B`` runs A on
aluminium and B on copper: ``fast`` is the heuristic and the funnel; ``bofn3`` and ``pkgfn3`` run time-aware BOFN or
pKGFN on both campaigns.
"""
from __future__ import annotations

import json
import lzma
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from twin import bench2 as B2
from twin import bench3 as B3

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("TWIN5_OUT", HERE.parent / "out" / "twin5"))
RUNS = OUT / "runs"
EVENTS = OUT / "events"
DAYS = 730
ALIAS = {"fast": "heuristic+tiered"}
ARMS = (("vertical", "parallel", "reorder"), ("vertical", "parallel", "lean"),
        ("conventional", "external", "reorder"), ("conventional", "external", "lean"))
N_CHEAP = int(os.environ.get("TWIN5_SEEDS", "16"))
N_NET = int(os.environ.get("TWIN5_NET_SEEDS", "12"))


def _cfg(lab, plan, policy, stock, seed, days=DAYS, money=1.0, **opts):
    o = dict(lab=lab, decisions="nominal", atom="derived", used=True)
    o.update(opts)
    return dict(lab=lab, plan=plan, policy=policy, stock=stock, seed=seed, days=days, money=money, opts=o)


def _arms(policy, seeds, **opts):
    return [_cfg(lab, plan, policy, stock, s, **opts) for s in seeds for lab, plan, stock in ARMS]


EXPERIMENTS = {
    # comparison 1, the cheap policies (the heuristic on aluminium, the funnel on copper): the four arms, 16 seeds
    "arms": _arms("fast", range(N_CHEAP)),
    # comparison 1, time-aware BOFN and pKGFN on both campaigns, in the four arms: 12 seeds, then 4 more
    "net": [c for s in range(N_NET) for p in ("bofn3", "pkgfn3") for c in _arms(p, [s])],
    "net_more": [c for s in range(N_NET, 16) for p in ("bofn3", "pkgfn3") for c in _arms(p, [s])],
    # decision time: no delay and slow windows (nominal is "arms"), the four arms, the cheap policies
    "dec_none": _arms("fast", range(N_CHEAP), decisions="none"),
    "dec_slow": _arms("fast", range(N_CHEAP), decisions="slow"),
    # note 2: the automated atomizer's cycle, 3 h and slow (derived is "arms"), the automated lab both ways
    "atom": [_cfg("vertical", "parallel", "fast", st, s, atom=a) for s in range(N_CHEAP) for a in ("3h", "slow")
             for st in ("reorder", "lean")],
    # comparison 2: round 4's three plans under the facility window and advance ordering (parallel is "arms")
    "plans": [_cfg("vertical", p, "fast", "reorder", s) for s in range(N_CHEAP) for p in ("wait", "external")],
    # what used equipment buys: the automated lab with every station bought new
    "noused": [_cfg("vertical", "parallel", "fast", "reorder", s, used=False) for s in range(N_CHEAP)],
    # note 4: four times the simulated candidates the policies see (512 kept, 256 new a day), both labs stocked
    "hpc_more": [_cfg(lab, plan, "fast", "reorder", s, hpc=dict(keep=512, add_per_day=256))
                 for s in range(N_CHEAP) for lab, plan, _ in ARMS[::2]],
    # comparison 2 with BOFN (on both campaigns): wait and external, 12 seeds (parallel is "net")
    "plans_net": [_cfg("vertical", p, "bofn3", "reorder", s) for s in range(N_NET) for p in ("wait", "external")],
}
CHEAP_FIRST = ("arms", "plans", "dec_none", "dec_slow", "atom", "noused", "hpc_more")


def run_id(cfg):
    o = cfg.get("opts") or {}
    parts = ["r5", cfg["lab"], cfg["plan"], cfg["policy"], cfg["stock"], f"s{cfg['seed']}"]
    if o.get("decisions", "nominal") != "nominal":
        parts.append(f"dec-{o['decisions']}")
    if o.get("atom", "derived") != "derived":
        parts.append(f"atom-{o['atom']}")
    if not o.get("used", True):
        parts.append("noused")
    for k in sorted(o):
        if k in ("lab", "decisions", "atom", "used"):
            continue
        v = o[k]
        if isinstance(v, dict):
            parts.append(f"{k}-" + "-".join(f"{kk}{vv}" for kk, vv in sorted(v.items())))
            continue
        parts.append(f"{k}-{'.'.join(map(str, v)) if isinstance(v, (list, tuple)) else v}")
    if cfg.get("days", DAYS) != DAYS:
        parts.append(f"d{cfg['days']}")
    if cfg.get("money", 1.0) != 1.0:
        parts.append(f"money{cfg['money']:g}")
    return "_".join(str(p) for p in parts)


def group_key(cfg):
    return run_id(dict(cfg, seed=0)).replace("_s0", "")


def pol_names(name):
    name = ALIAS.get(name, name)
    al, cu = (name.split("+") + [name])[:2] if "+" in name else (name, name)
    return {"flaime_al": al, "onr_cu": cu}


def make_policies(name, seed):
    from twin.opt import policies3 as P3
    n = pol_names(name)
    return {k: P3.make3(v, k, seed) for k, v in n.items()}


def simulate(cfg: dict):
    import torch
    torch.set_num_threads(1)
    from twin import repro as R
    R.seed_globals(cfg["seed"])
    rng0 = R.torch_rng_state()
    from twin import campaign as C
    from twin import round5 as R5
    from twin import spaces as SP
    from twin.opt.gp import STATS
    t0 = time.time()
    days = int(os.environ.get("TWIN5_DAYS", cfg.get("days", DAYS)))
    yb = cfg.get("days", DAYS) / 365.0
    bud = {k: B2.BUDGET[k] * yb * cfg.get("money", 1.0) for k in ("flaime_al", "onr_cu")}
    specs = {k: C.Spec(k, bud[k], B2.WIP[k], cfg["seed"], 1.0, stock=cfg["stock"]) for k in bud}
    pols = make_policies(cfg["policy"], cfg["seed"])
    tw = R5.Twin5(specs, pols, plan=cfg["plan"], seed=cfg["seed"], horizon_days=days, opts=cfg.get("opts"),
                  pol_names=pol_names(cfg["policy"]))
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
    out["r5"] = tw.report5()
    out["torch_rng_used"] = R.torch_rng_used(rng0)
    out["env"] = R.fingerprint()
    out["code"] = _code()
    return out, tw


_CODE = {}


def _code():
    """The commit the row was made from, and whether twin/ differed from it."""
    if not _CODE:
        import subprocess
        try:
            c = subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE, capture_output=True, text=True).stdout.strip()
            d = subprocess.run(["git", "status", "--porcelain", "--", "."], cwd=HERE, capture_output=True,
                               text=True).stdout
            _CODE.update(commit=c, twin_dirty=any(l[3:].endswith(".py") for l in d.splitlines()))
        except Exception:
            _CODE.update(commit=None, twin_dirty=None)
    return dict(_CODE)


def run_one(cfg: dict) -> dict:
    out, tw = simulate(cfg)
    rid = run_id(cfg)
    EVENTS.mkdir(parents=True, exist_ok=True)
    log = tw.event_log(meta=dict(cfg=cfg, run_id=rid))
    log["round5"] = dict(stock={k: dict(use=c.use_log, orders=c.stock_orders, stockouts=c.stockouts)
                                for k, c in tw.campaigns.items()},
                         held=tw.held_log, daily={k: v for k, v in tw.daily.items()})
    data = json.dumps(B2._jsonable(log)).encode()
    (EVENTS / f"{rid}.json.xz").write_bytes(lzma.compress(data, preset=9 | lzma.PRESET_EXTREME))
    out["events_file"] = f"out/twin5/events/{rid}.json.xz"
    return json.loads(json.dumps(B2._jsonable(out)))


def _safe(cfg):
    try:
        return run_one(cfg)
    except Exception:
        import traceback
        return dict(cfg=cfg, error=traceback.format_exc()[-4000:])


def read_events(path) -> dict:
    p = Path(path)
    b = p.read_bytes()
    return json.loads(lzma.decompress(b) if p.suffix == ".xz" else b)


def _lines(name):
    """An experiment's rows as text lines: the packed file (``<name>.jsonl.xz``, committed) and any rows appended
    since (``<name>.jsonl``)."""
    out = []
    px = RUNS / f"{name}.jsonl.xz"
    if px.exists():
        out += lzma.decompress(px.read_bytes()).decode().splitlines()
    p = RUNS / f"{name}.jsonl"
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


def pack(keep_appended=False):
    """Merge each experiment's appended rows into its packed file (one row per run id, the first kept). With
    ``keep_appended`` the appended file stays (a checkpoint while runs are still being added to it)."""
    for name in EXPERIMENTS:
        p = RUNS / f"{name}.jsonl"
        if not p.exists():
            continue
        seen, keep = set(), []
        for line in _lines(name):
            try:
                rid = run_id(json.loads(line)["cfg"])
            except Exception:                          # a row being written while this reads
                continue
            if rid not in seen:
                seen.add(rid)
                keep.append(line)
        (RUNS / f"{name}.jsonl.xz").write_bytes(lzma.compress(("\n".join(keep) + "\n").encode(),
                                                              preset=9 | lzma.PRESET_EXTREME))
        if not keep_appended:
            p.unlink()
        print(f"{name}: {len(keep)} rows packed")


def plan(names):
    """The queue, in an order that leaves usable, balanced results at any point: the cheap policies first (each
    experiment seed by seed across its arms), then BOFN and pKGFN: the conventional lab's seed by seed, then the
    automated lab's (net), the plans with BOFN, and the automated lab's last four seeds (net_more)."""
    todo = []
    for name in names:
        done = _done(name)
        mine = [c for c in EXPERIMENTS[name] if run_id(c) not in done]
        print(f"{name}: {len(mine)} runs to do ({len(done)} done)", flush=True)
        todo += [(name, c) for c in mine]
    rank = {n: i for i, n in enumerate(CHEAP_FIRST)}

    def key(t):
        name, c = t
        if name in rank:
            return (0, rank[name], c["seed"], run_id(c))
        # BOFN and pKGFN: a two-year run takes 3-5 minutes in the conventional lab (people decide at their meetings)
        # and 25-35 minutes in the automated lab (hourly decisions on a 24/7 lab: many more results and refits). The
        # conventional lab's first (all its seeds), then the automated lab's 12 seeds, the plans with BOFN, its 4 more
        if c["lab"] == "conventional":
            return (1, c["seed"], run_id(c))
        if name == "net":
            return (2, c["seed"], run_id(c))
        if name == "plans_net":
            return (3, c["seed"], run_id(c))
        return (4, c["seed"], run_id(c))
    todo.sort(key=key)
    return todo


def run(names, workers=4):
    RUNS.mkdir(parents=True, exist_ok=True)
    todo = plan(names)
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        futs = {ex.submit(_safe, c): (name, c) for name, c in todo}
        for fut in as_completed(futs):
            name, c = futs[fut]
            res = fut.result()
            if "error" in res:
                with (RUNS / f"{name}.errors.jsonl").open("a") as fh:
                    fh.write(json.dumps(B2._jsonable(res)) + "\n")
                print(f"  {name} {run_id(c)}: ERROR {res['error'].splitlines()[-1]}", flush=True)
                continue
            with (RUNS / f"{name}.jsonl").open("a") as fh:
                fh.write(json.dumps(res) + "\n")
            print(f"  {name} {run_id(c)}: Al {res['campaigns']['flaime_al']['best_new']:.3f} "
                  f"Cu {res['campaigns']['onr_cu']['best_new']:.3f} ({res['seconds']} s; "
                  f"{time.time() - t0:.0f} s in)", flush=True)


def load(name):
    return [json.loads(l) for l in _lines(name)]


def status(write=True):
    lines = ["# Round 5: runs done and left", "",
             "Made by `python -m twin.bench5 status`. Each arm needs at least 12 seeds before the tables report it "
             "(16 for the cheap policies).", "", "| Experiment | Arm | Seeds done | Seeds left |", "|---|---|---|---|"]
    left_total = 0
    for name, cfgs in EXPERIMENTS.items():
        done = _done(name)
        arms = {}
        for c in cfgs:
            a = arms.setdefault(group_key(c), [[], []])
            a[0 if run_id(c) in done else 1].append(c["seed"])
        for g, (d, l) in arms.items():
            left_total += len(l)
            lines.append(f"| {name} | `{g}` | {len(d)} | {len(l)}" + (f" ({min(l)}-{max(l)})" if l else "") + " |")
    lines += ["", f"Runs left: {left_total}."]
    txt = "\n".join(lines) + "\n"
    if write:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "left.md").write_text(txt)
    print(txt)


def main(argv):
    if os.environ.get("TWIN_PIN") is None:
        os.environ["TWIN_PIN"] = "avx2"
        os.environ["PYTHONHASHSEED"] = "0"
        sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, "-m", "twin.bench5"] + argv)
    from twin import repro as R
    R.reexec_pinned("twin.bench5")
    if not argv or argv[0] == "status":
        status()
        return
    if argv[0] in ("pack", "snapshot"):
        pack(keep_appended=argv[0] == "snapshot")
        status()
        return
    if argv[0] == "run":
        run(argv[1:] or list(CHEAP_FIRST), int(os.environ.get("TWIN_WORKERS", "4")))
        status()
        return
    if argv[0] == "one":
        lab, pl, pol, stock = argv[1:5]
        seed = int(argv[5]) if len(argv) > 5 else 0
        extra = dict(a.split("=", 1) for a in argv[6:])
        cfg = _cfg(lab, pl, pol, stock, seed, **extra)
        out, tw = simulate(cfg)
        print(json.dumps({k: (v["best_new"], v["n_demonstrated"], round(v["spent"])) for k, v in
                          out["campaigns"].items()}), out["seconds"], "s")
        r5 = out["r5"]
        print("room day", round((r5["room_h"] or 0) / 24, 1), "cell day", round((out["r4"]["cell_h"] or 0) / 24, 1),
              "atom runs", r5["atom"]["runs"], r5["atom"]["runs_by"])
        print("used", {k: (v["fault"], v["days_bought"]) for k, v in r5["used"].items()})
        print("counters", json.dumps(r5["counters"]))
        print("stock", {k: {kk: v[kk] for kk in ("mode", "n_charges", "n_stockouts", "days_waited", "stock_usd",
                                                    "left_usd")} for k, v in r5["stock"].items()})
        print("held", json.dumps(r5["decisions"]["held"]))
        print("status", {k: v["status"] for k, v in out["campaigns"].items()})
        for k, c in out["campaigns"].items():
            print(k, "T curve", c["curve_new"][:3], "...", c["curve_new"][-1:] if c["curve_new"] else None)
        print("idle", json.dumps({k: {g: [(x["start_d"], x["days"], x["cause"]) for x in v[:6]]
                                      for g, v in d.items()} for k, d in r5["idle"]["stretches"].items()}))
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
