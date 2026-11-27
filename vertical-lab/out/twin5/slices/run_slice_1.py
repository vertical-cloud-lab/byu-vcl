"""Round 5, compute slice 1 of 6 (issue 412, stacked on PR 405): this slice's runs with the round-5 engine as committed
at b410477, under the same pin. Nothing in twin/ changes; every row records the commit and whether twin/ was clean
(``code``).

    cd vertical-lab
    python -m out.twin5.slices.run_slice_1 verify   # rerun arms' r5_conventional_external_fast_lean_s0 and compare it
                                                    # with the committed row, apart from timing and provenance (nothing
                                                    # is appended; restore its event file afterwards with
                                                    # git checkout -- out/twin5/events/)
    python -m out.twin5.slices.run_slice_1 run      # this slice's runs not yet in runs/<experiment>.slice-1.jsonl
    python -m out.twin5.slices.run_slice_1 status   # done and left

It starts itself pinned exactly as ``python -m twin.bench5`` does (``bench5.main``): ``TWIN_PIN=avx2`` and
``PYTHONHASHSEED=0`` (re-executing itself if ``TWIN_PIN`` was unset), then ``twin.repro.reexec_pinned``. Each run's config
is the one in ``twin.bench5.EXPERIMENTS[<experiment>]`` whose ``run_id`` matches; it runs as ``bench5._safe``
(``bench5.run_one``, an exception caught as ``bench5.run`` catches it) in a pool of 4 processes (``TWIN_WORKERS``), queued
in ``bench5.plan``'s order. A finished row is appended to ``out/twin5/runs/<experiment>.slice-1.jsonl``, a run that raised
to ``<experiment>.slice-1.errors.jsonl``, and ``run_one`` writes the event log to ``out/twin5/events/<run id>.json.xz``.
"""
from __future__ import annotations

import json
import lzma
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from twin import bench2 as B2                     # the twin package first: it pins the kernels before numpy loads
from twin import bench5 as B5

MODULE = "out.twin5.slices.run_slice_1"
SLICE = "slice-1"
RUN_IDS = {
    "net": ["r5_vertical_parallel_bofn3_reorder_s10", "r5_vertical_parallel_pkgfn3_lean_s6",
            "r5_vertical_parallel_pkgfn3_lean_s9", "r5_vertical_parallel_pkgfn3_reorder_s3"],
    "net_more": ["r5_vertical_parallel_bofn3_reorder_s13", "r5_vertical_parallel_pkgfn3_lean_s12",
                 "r5_vertical_parallel_pkgfn3_lean_s15"],
    "plans_net": ["r5_vertical_wait_bofn3_reorder_s1", "r5_vertical_wait_bofn3_reorder_s10",
                  "r5_vertical_wait_bofn3_reorder_s4", "r5_vertical_wait_bofn3_reorder_s7"],
}
CHECK = ("arms", "r5_conventional_external_fast_lean_s0")
# a row's timing and provenance: everything else has to match the committed row exactly
NOT_COMPARED = {("seconds",), ("gp", "fit_s"), ("gp", "nuts_s"), ("env",), ("code",)}


def rows_file(name):
    return B5.RUNS / f"{name}.{SLICE}.jsonl"


def errors_file(name):
    return B5.RUNS / f"{name}.{SLICE}.errors.jsonl"


def done_here(name):
    p = rows_file(name)
    done = set()
    if p.exists():
        for line in p.read_text().splitlines():
            try:
                done.add(B5.run_id(json.loads(line)["cfg"]))
            except Exception:                          # a row being written while this reads
                pass
    return done


def config(name, rid):
    hits = [c for c in B5.EXPERIMENTS[name] if B5.run_id(c) == rid]
    if len(hits) != 1:
        raise SystemExit(f"{name}: {len(hits)} configs with run id {rid}")
    return hits[0]


def plan_key(t):
    """bench5.plan's order for the automated lab's BOFN and pKGFN: net, then the plans with BOFN, then net_more."""
    name, c = t
    if c["lab"] == "conventional":
        return (1, c["seed"], B5.run_id(c))
    return ({"net": 2, "plans_net": 3}.get(name, 4), c["seed"], B5.run_id(c))


def todo():
    out = []
    for name, rids in RUN_IDS.items():
        done, committed = done_here(name), B5._done(name)
        for rid in rids:
            if rid in committed:
                print(f"  note: {name} {rid} is already in the committed rows", flush=True)
            if rid not in done:
                out.append((name, config(name, rid)))
    return sorted(out, key=plan_key)


def run(workers):
    B5.RUNS.mkdir(parents=True, exist_ok=True)
    queue = todo()
    print(f"{len(queue)} runs to do, {workers} at a time:", flush=True)
    for name, c in queue:
        print(f"  {name} {B5.run_id(c)}", flush=True)
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        futs = {ex.submit(B5._safe, c): (name, c) for name, c in queue}
        for fut in as_completed(futs):
            name, c = futs[fut]
            res = fut.result()
            if "error" in res:
                with errors_file(name).open("a") as fh:
                    fh.write(json.dumps(B2._jsonable(res)) + "\n")
                print(f"  {name} {B5.run_id(c)}: ERROR {res['error'].splitlines()[-1]}", flush=True)
                continue
            with rows_file(name).open("a") as fh:
                fh.write(json.dumps(res) + "\n")
            print(f"  {name} {B5.run_id(c)}: Al {res['campaigns']['flaime_al']['best_new']:.3f} "
                  f"Cu {res['campaigns']['onr_cu']['best_new']:.3f} ({res['seconds']} s; "
                  f"{time.time() - t0:.0f} s in; twin_dirty {res['code']['twin_dirty']})", flush=True)


def diff(a, b, path=()):
    """The paths at which two rows differ, skipping NOT_COMPARED."""
    if path in NOT_COMPARED:
        return []
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                if path + (k,) not in NOT_COMPARED:
                    out.append((path + (k,), a.get(k, "<missing>"), b.get(k, "<missing>")))
                continue
            out += diff(a[k], b[k], path + (k,))
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [(path + ("len",), len(a), len(b))]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, path + (i,))
        return out
    if type(a) is not type(b) or a != b:
        return [(path, a, b)]
    return []


def verify():
    name, rid = CHECK
    ref = [r for r in B5.load(name) if B5.run_id(r["cfg"]) == rid]
    if len(ref) != 1:
        raise SystemExit(f"{name}: {len(ref)} committed rows with run id {rid}")
    ref = ref[0]
    cfg = config(name, rid)
    if cfg != ref["cfg"]:
        print(f"the config in EXPERIMENTS differs from the committed row's: {diff(cfg, ref['cfg'])}")
    events = B5.EVENTS / f"{rid}.json.xz"
    ref_events = B5.read_events(events)                # the committed event log, before the rerun overwrites it
    with ProcessPoolExecutor(1) as ex:                  # in a worker, as bench5.run makes a row
        out = ex.submit(B5._safe, cfg).result()
    if "error" in out:
        print(out["error"])
        return 1
    d = diff(out, ref)
    new_events = B5.read_events(events)
    ev_same = new_events == ref_events
    report = dict(experiment=name, run_id=rid, identical_apart_from_timing_and_provenance=not d,
                  n_differences=len(d), differences=[[list(p), str(x)[:200], str(y)[:200]] for p, x, y in d[:40]],
                  event_log_identical=ev_same, not_compared=[list(p) for p in sorted(NOT_COMPARED)],
                  seconds=dict(rerun=out["seconds"], committed=ref["seconds"]),
                  code=dict(rerun=out["code"], committed=ref["code"]),
                  env_rerun=out["env"], env_committed=ref["env"],
                  gp=dict(rerun=out["gp"], committed=ref["gp"]))
    print(json.dumps(report, indent=1))
    return 0 if (not d and ev_same) else 1


def status():
    left = 0
    for name, rids in RUN_IDS.items():
        done, err = done_here(name), set()
        if errors_file(name).exists():
            for line in errors_file(name).read_text().splitlines():
                try:
                    err.add(B5.run_id(json.loads(line)["cfg"]))
                except Exception:
                    pass
        for rid in rids:
            state = "done" if rid in done else ("raised" if rid in err else "left")
            left += state != "done"
            print(f"{name:10s} {rid:45s} {state}")
    print(f"runs left: {left}")


def main(argv):
    if os.environ.get("TWIN_PIN") is None:              # as bench5.main starts itself
        os.environ["TWIN_PIN"] = "avx2"
        os.environ["PYTHONHASHSEED"] = "0"
        sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, "-m", MODULE] + argv)
    from twin import repro as R
    R.reexec_pinned(MODULE)
    for k in ("TWIN5_DAYS", "TWIN5_OUT", "TWIN5_SEEDS", "TWIN5_NET_SEEDS"):
        if k in os.environ:
            raise SystemExit(f"{k} is set; this slice runs bench5's defaults")
    if not argv or argv[0] == "status":
        status()
        return 0
    if argv[0] == "verify":
        return verify()
    if argv[0] == "run":
        run(int(os.environ.get("TWIN_WORKERS", "4")))
        status()
        return 0
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
