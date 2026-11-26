"""Round 3b: the missing arms of round 3's lab comparison, and round 3's runs again for their event logs.

    python3 -m twin.bench3b run [experiment ...]   # -> out/twin3b/runs/<experiment>.jsonl, events/<run>.json.xz
    python3 -m twin.bench3b status                 # what is done, and which reruns match their committed rows

Round 3's engine and policies, unchanged (twin/bench3.py), under the pinned numerical set-up (twin/repro.py).
Every run here writes its event log, compressed with xz (``out/twin3b/events/<run id>.json.xz``; read it with
``read_events``).

* The missing arms. Round 3 compared a stocked vertical lab (one year at one year's money) with a conventional lab
  ordering metal as it goes (three years at three years' money), so the stock's share of every factor was not
  measured (DAL audit of the round-2 video, digital-alloy-lab PR 293). ``v_lean``: the vertical lab ordering as it
  goes. ``c_stocked``: the conventional lab stocked. ``c_lean_net``: BOFN and pKGFN in the conventional lab ordering
  as it goes (round 3's ``conventional_net``, defined but never run). Each for the policies the comparisons use:
  the heuristic and the funnel on 12 seeds, time-aware BOFN and pKGFN on 12 in the vertical lab and on
  ``TWIN3B_CONV_NET`` seeds (4) in the conventional lab, where a run simulates three years.
* The reruns. ``re_main``, ``re_main_more`` and ``re_conventional`` run round 3's committed configurations again with
  the event log on, so that every seed has one (round 3 kept seed 0's). Each row records whether it matches its
  committed row (``committed_match``: True, or the first difference); a run that matches has the committed run's
  log.
"""
from __future__ import annotations

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
OUT = Path(os.environ.get("TWIN3B_OUT", HERE.parent / "out" / "twin3b"))
RUNS = OUT / "runs"
EVENTS = OUT / "events"
R3_RUNS = HERE.parent / "out" / "twin3" / "runs"

CHEAP = ("heuristic", "tiered")
NET = ("bofn3", "pkgfn3")
N_CONV_NET = int(os.environ.get("TWIN3B_CONV_NET", "4"))


def _c(policy, seed, facility, stock):
    """A lab-comparison arm: the vertical lab runs one year at one year's money, the conventional lab three years at
    three years' money, as in round 3."""
    if facility == "proposed":
        return B3._cfg(policy, seed, facility="proposed", stock=stock, days=1095, years_budget=3.0, events=True)
    return B3._cfg(policy, seed, facility="vertical_lab", stock=stock, events=True)


def _re(name):
    """Round 3's committed configurations of an experiment, event log on."""
    return [dict(c, events=True) for c in B3.EXPERIMENTS[name]]


EXPERIMENTS = {
    "v_lean": [_c(p, s, "vertical_lab", "lean") for p in CHEAP + NET for s in range(12)],
    "c_stocked": ([_c(p, s, "proposed", "stocked") for p in CHEAP for s in range(12)]
                  + [_c(p, s, "proposed", "stocked") for p in NET for s in range(N_CONV_NET)]),
    "c_lean_net": [_c(p, s, "proposed", "lean") for p in NET for s in range(N_CONV_NET)],
    "re_main": _re("main"),
    "re_main_more": _re("main_more"),
    "re_conventional": _re("conventional"),
    # round 3's copper tests, the cheap policies only (a check that they reproduce too; BOFN and pKGFN there are
    # 16 runs of 10-18 minutes and were not rerun)
    "re_cu": [c for nm in ("cu_hidden", "cu_proxy", "cu_ablation", "cu_money") for c in _re(nm)
              if c["policy"] not in NET],
}
RERUN_OF = {"re_main": "main", "re_main_more": "main_more", "re_conventional": "conventional", "re_cu": "cu"}


def run_id(cfg):
    return B3.run_id(cfg)


# --------------------------------------------------------------------------------------------- comparing reruns
IGNORE = {"seconds", "gp", "events_file", "env", "torch_rng_used", "committed_match", "rerun_of"}


def first_diff(a, b, path=""):
    """The first place two JSON values differ: (path, a, b), or None if they are identical."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if path == "" and k in IGNORE:
                continue
            if path == "/cfg" and k == "events":
                continue
            if k not in a or k not in b:
                return (f"{path}/{k}", a.get(k, "<missing>"), b.get(k, "<missing>"))
            d = first_diff(a[k], b[k], f"{path}/{k}")
            if d:
                return d
        return None
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return (f"{path} (length)", len(a), len(b))
        for i, (x, y) in enumerate(zip(a, b)):
            d = first_diff(x, y, f"{path}[{i}]")
            if d:
                return d
        return None
    return None if a == b else (path, a, b)


def committed_rows(name):
    out = {}
    names = {"cu": ["cu_hidden", "cu_proxy", "cu_ablation", "cu_money"]}.get(name, [name])
    for nm in names + {"conventional": ["conventional_net"]}.get(name, []):
        p = R3_RUNS / f"{nm}.jsonl"
        if p.exists():
            for line in p.read_text().splitlines():
                if line.strip():
                    r = json.loads(line)
                    out[run_id(r["cfg"])] = r
    return out


# ------------------------------------------------------------------------------------------------------ running
def run_one(cfg: dict, rerun_of: str | None = None) -> dict:
    out, tw = B3.simulate(cfg)
    rid = run_id(cfg)
    if cfg.get("events"):
        EVENTS.mkdir(parents=True, exist_ok=True)
        log = tw.event_log(meta=dict(cfg=cfg, run_id=rid))
        data = json.dumps(B2._jsonable(log)).encode()
        (EVENTS / f"{rid}.json.xz").write_bytes(lzma.compress(data, preset=9 | lzma.PRESET_EXTREME))
        out["events_file"] = f"out/twin3b/events/{rid}.json.xz"
    out = json.loads(json.dumps(B2._jsonable(out)))
    if rerun_of:
        ref = committed_rows(rerun_of).get(rid)
        out["rerun_of"] = rerun_of
        if ref is None:
            out["committed_match"] = None
        else:
            d = first_diff(out, ref)
            out["committed_match"] = True if d is None else [d[0], str(d[1])[:200], str(d[2])[:200]]
    return out


def _safe(cfg, rerun_of):
    try:
        return run_one(cfg, rerun_of)
    except Exception:
        import traceback
        return dict(cfg=cfg, error=traceback.format_exc()[-3000:])


def read_events(path) -> dict:
    """An event log written here (``.json.xz``) or by round 3 (``.json``)."""
    p = Path(path)
    b = p.read_bytes()
    return json.loads(lzma.decompress(b) if p.suffix == ".xz" else b)


def _done(name):
    path = RUNS / f"{name}.jsonl"
    done = set()
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                done.add(run_id(json.loads(line)["cfg"]))
            except Exception:
                pass
    return done


def plan(names):
    """The queue, in the order that leaves a usable result at any point: the cheap policies' runs first (the new arms,
    then the reruns), then the expensive ones by seed, so that every arm has the same seeds when the job stops; within
    a seed the three-year conventional runs first (they take about three times as long), then the vertical lab's, then
    the reruns of round 3's BOFN and pKGFN (time-aware BOFN, pKGFN, then BOFN per dollar)."""
    todo = []
    for name in names:
        done = _done(name)
        mine = [c for c in EXPERIMENTS[name] if run_id(c) not in done]
        print(f"{name}: {len(mine)} runs to do ({len(done)} done)", flush=True)
        todo += [(name, c) for c in mine]
    exp_rank = {"v_lean": 0, "c_stocked": 1, "c_lean_net": 1, "re_main": 2, "re_main_more": 3, "re_conventional": 4,
                "re_cu": 5}
    pol_rank = {"bofn3": 0, "pkgfn3": 1, "bofn3_usd": 2}

    def key(t):
        name, c = t
        if c["policy"] not in NET + ("bofn3_usd",):
            return (0, exp_rank.get(name, 9), c["policy"], c["seed"])
        if name.startswith("re_"):
            return (2 + pol_rank[c["policy"]], c["seed"], 0, "")
        conv = c["facility"] == "proposed"
        return (1, c["seed"], 0 if conv else 1, f"{c['policy']}_{c['stock']}")
    todo.sort(key=key)
    return todo


def run(names, workers=4):
    RUNS.mkdir(parents=True, exist_ok=True)
    todo = plan(names)
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        futs = {ex.submit(_safe, c, RERUN_OF.get(name)): (name, c) for name, c in todo}
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
            m = res.get("committed_match", "-")
            print(f"  {name} {run_id(c)}: Al {res['campaigns']['flaime_al']['best_new']:.3f} "
                  f"Cu {res['campaigns']['onr_cu']['best_new']:.3f} match={m if m in (True, None, '-') else 'NO'} "
                  f"({res['seconds']} s; {time.time() - t0:.0f} s in)", flush=True)


def load(name):
    p = RUNS / f"{name}.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def status():
    for name in EXPERIMENTS:
        rows = load(name)
        line = f"{name}: {len(rows)} of {len(EXPERIMENTS[name])} runs"
        if name in RERUN_OF:
            ok = sum(1 for r in rows if r.get("committed_match") is True)
            bad = [run_id(r["cfg"]) for r in rows if r.get("committed_match") not in (True, None)]
            line += f"; {ok} match their committed rows, {len(bad)} don't" + (f": {bad}" if bad else "")
        used = sum(1 for r in rows if r.get("torch_rng_used"))
        line += f"; {used} drew from torch's global generator"
        print(line)


def main(argv):
    from twin import repro as R
    R.reexec_pinned("twin.bench3b")
    if not argv or argv[0] == "status":
        status()
        return
    if argv[0] == "run":
        run(argv[1:] or list(EXPERIMENTS), int(os.environ.get("TWIN_WORKERS", "4")))
        status()
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])


def match_kind(new, ref, rel=4e-16):
    """How a rerun compares with its committed row: 'exact'; 'last bit' (every difference a float within a few units
    in the last place, everything else in the row identical: counts, days, dollars); or the first real difference."""
    d = first_diff(new, ref)
    if d is None:
        return "exact", None
    worst = [0.0]

    def walk(a, b, path=""):
        if isinstance(a, dict) and isinstance(b, dict):
            for k in set(a) | set(b):
                if path == "" and k in IGNORE or path == "/cfg" and k == "events":
                    continue
                if k not in a or k not in b:
                    return (f"{path}/{k}", a.get(k), b.get(k))
                r = walk(a[k], b[k], f"{path}/{k}")
                if r:
                    return r
            return None
        if isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                return (f"{path} (length)", len(a), len(b))
            for i, (x, y) in enumerate(zip(a, b)):
                r = walk(x, y, f"{path}[{i}]")
                if r:
                    return r
            return None
        if a == b:
            return None
        if isinstance(a, float) and isinstance(b, float) and abs(a - b) <= rel * max(abs(a), abs(b), 1e-300) * 8:
            worst[0] = max(worst[0], abs(a - b))
            return None
        return (path, a, b)
    r = walk(new, ref)
    if r is None:
        return "last bit", worst[0]
    return "different", [r[0], str(r[1])[:120], str(r[2])[:120]]


def rerun_report():
    """Every rerun against its committed row: {experiment: {kind: [run ids]}} and the first real differences."""
    out = {}
    for name, src in RERUN_OF.items():
        refs = committed_rows(src)
        K = {}
        for r in load(name):
            rid = run_id(r["cfg"])
            ref = refs.get(rid)
            kind, info = match_kind(r, ref) if ref is not None else ("no committed row", None)
            K.setdefault(kind, []).append(rid if info is None or kind == "last bit" else [rid, info])
        out[name] = K
    return out
