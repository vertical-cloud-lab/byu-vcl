"""Round 5, compute slice 2 of 6 (issue #413, stacked on PR 405): this slice's runs with the round-5 engine as
committed at b410477. Nothing in twin/ is changed; every row records whether twin/ was clean (``code.twin_dirty``).

    cd vertical-lab
    python -m out.twin5.slices.run_slice_2 check    # rerun r5_conventional_external_fast_lean_s0 (arms) and compare
                                                    # it with its committed row and event log; exit 1 if they differ
    python -m out.twin5.slices.run_slice_2 run      # this slice's runs not yet done, 4 at a time (TWIN_WORKERS)
    python -m out.twin5.slices.run_slice_2 status   # this slice's runs: done, failed, left

Each run's config is the one in ``twin.bench5.EXPERIMENTS[<experiment>]`` whose ``run_id`` matches, and each run goes
through ``twin.bench5._safe`` (``run_one``, with an exception caught and recorded) in a ``ProcessPoolExecutor`` of 4
workers, as ``bench5.run`` does, in ``bench5.plan``'s order. The driver starts itself pinned exactly as
``python -m twin.bench5`` does (``main()``: ``TWIN_PIN=avx2`` and ``PYTHONHASHSEED=0`` if ``TWIN_PIN`` is unset, then
``twin.repro.reexec_pinned``), and loads nothing that imports numpy or torch before the ``twin`` package has applied
its pin.

Rows are appended to ``out/twin5/runs/<experiment>.slice-2.jsonl`` and failures to
``out/twin5/runs/<experiment>.slice-2.errors.jsonl``, as ``bench5.run`` appends to ``<experiment>.jsonl`` and
``<experiment>.errors.jsonl``; ``run_one`` writes each event log to ``out/twin5/events/<run id>.json.xz``. A run
already in its slice file or in the packed ``<experiment>.jsonl.xz`` is skipped, so the same command finishes an
interrupted slice. (``out/twin5/.gitignore`` ignores ``runs/*.jsonl``, so the slice files are committed with
``git add -f``.)
"""
from __future__ import annotations

import json
import lzma
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

MODULE = "out.twin5.slices.run_slice_2"
SLICE = 2
RUN_IDS = {
    "net": ["r5_vertical_parallel_bofn3_lean_s10", "r5_vertical_parallel_bofn3_lean_s7",
            "r5_vertical_parallel_bofn3_reorder_s5", "r5_vertical_parallel_pkgfn3_reorder_s10",
            "r5_vertical_parallel_pkgfn3_reorder_s4", "r5_vertical_parallel_pkgfn3_reorder_s7"],
    "net_more": ["r5_vertical_parallel_bofn3_lean_s13", "r5_vertical_parallel_pkgfn3_reorder_s13"],
    "plans_net": ["r5_vertical_external_bofn3_reorder_s1", "r5_vertical_external_bofn3_reorder_s10",
                  "r5_vertical_external_bofn3_reorder_s4", "r5_vertical_external_bofn3_reorder_s7"],
}
# bench5.plan's order for the automated lab's BOFN and pKGFN runs: net, then the plans with BOFN, then net_more,
# each seed by seed
ORDER = {"net": 2, "plans_net": 3, "net_more": 4}
# the committed row the check reruns, and the fields a rerun may change: timing and provenance
CHECK = ("arms", "r5_conventional_external_fast_lean_s0")
TIMING = (("seconds",), ("gp", "fit_s"), ("gp", "nuts_s"))
PROVENANCE = (("env",), ("code",))


def _b5():
    from twin import bench5 as B5      # the twin package applies the pin before bench5 loads numpy and torch
    return B5


def slice_file(B5, name, errors=False):
    return B5.RUNS / f"{name}.slice-{SLICE}{'.errors' if errors else ''}.jsonl"


def _ids(B5, path):
    out = set()
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                out.add(B5.run_id(json.loads(line)["cfg"]))
            except Exception:                          # a row being written while this reads
                pass
    return out


def cfg_for(B5, name, rid):
    found = [c for c in B5.EXPERIMENTS[name] if B5.run_id(c) == rid]
    if len(found) != 1:
        raise SystemExit(f"{name}: {len(found)} configs have run id {rid}, not 1")
    return found[0]


def todo(B5):
    jobs = []
    for name, rids in RUN_IDS.items():
        done = B5._done(name) | _ids(B5, slice_file(B5, name))
        for rid in rids:
            c = cfg_for(B5, name, rid)
            if rid in done:
                print(f"  {name} {rid}: done already, skipped", flush=True)
                continue
            jobs.append((name, c))
    jobs.sort(key=lambda t: (ORDER[t[0]], t[1]["seed"], B5.run_id(t[1])))
    return jobs


def run(B5, workers):
    from twin import bench2 as B2
    B5.RUNS.mkdir(parents=True, exist_ok=True)
    jobs = todo(B5)
    print(f"slice {SLICE}: {len(jobs)} runs to do, {workers} at a time: "
          + ", ".join(B5.run_id(c) for _, c in jobs), flush=True)
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        futs = {ex.submit(B5._safe, c): (name, c) for name, c in jobs}
        for fut in as_completed(futs):
            name, c = futs[fut]
            try:
                res = fut.result()
            except Exception:                          # the worker itself died (bench5.run would stop here)
                import traceback
                res = dict(cfg=c, error=traceback.format_exc()[-4000:])
            if "error" in res:
                with slice_file(B5, name, errors=True).open("a") as fh:
                    fh.write(json.dumps(B2._jsonable(res)) + "\n")
                print(f"  {name} {B5.run_id(c)}: ERROR {res['error'].splitlines()[-1]}", flush=True)
                continue
            with slice_file(B5, name).open("a") as fh:
                fh.write(json.dumps(res) + "\n")
            print(f"  {name} {B5.run_id(c)}: Al {res['campaigns']['flaime_al']['best_new']:.3f} "
                  f"Cu {res['campaigns']['onr_cu']['best_new']:.3f} ({res['seconds']} s; "
                  f"{time.time() - t0:.0f} s in; {time.strftime('%H:%M:%S', time.gmtime())} UTC)", flush=True)
    status(B5)


def _same(a, b):
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return type(a) is type(b) and a == b


def diff(a, b, path=()):
    """Every path at which two JSON values differ: (path, a's value, b's value)."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                yield path + (k,), a.get(k, "<missing>"), b.get(k, "<missing>")
            else:
                yield from diff(a[k], b[k], path + (k,))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            yield path + ("<length>",), len(a), len(b)
        for i, (x, y) in enumerate(zip(a, b)):
            yield from diff(x, y, path + (i,))
    elif not _same(a, b):
        yield path, a, b


def _allowed(path):
    return any(path[:len(p)] == p for p in TIMING + PROVENANCE)


def _show(v, n=160):
    s = json.dumps(v)
    return s if len(s) <= n else s[:n] + "..."


def check(B5):
    """Rerun the committed row CHECK in a pool worker, as bench5.run made it, and compare. The row is not appended
    anywhere; run_one overwrites its event log, which the caller restores (git checkout -- out/twin5/events/)."""
    name, rid = CHECK
    cfg = cfg_for(B5, name, rid)
    committed = [r for r in map(json.loads, B5._lines(name)) if B5.run_id(r["cfg"]) == rid]
    if len(committed) != 1:
        raise SystemExit(f"{name}: {len(committed)} committed rows with run id {rid}, not 1")
    committed = committed[0]
    ev_path = B5.EVENTS / f"{rid}.json.xz"
    ev_old = ev_path.read_bytes()
    print(f"check: rerunning {name} {rid} (committed from {committed['code']}, {committed['seconds']} s)", flush=True)
    with ProcessPoolExecutor(1) as ex:
        res = ex.submit(B5._safe, cfg).result()
    if "error" in res:
        print(f"check: the rerun raised\n{res['error']}", flush=True)
        return 1
    rows = list(diff(res, committed))
    other = [d for d in rows if not _allowed(d[0])]
    print(f"check: the row differs at {len(rows)} paths; {len(rows) - len(other)} are timing or provenance:")
    for p, x, y in rows:
        print(f"  {'ok  ' if _allowed(p) else 'DIFF'} {'.'.join(map(str, p))}: rerun {_show(x)} | committed {_show(y)}")
    ev_new = ev_path.read_bytes()
    ev_rows = list(diff(json.loads(lzma.decompress(ev_new)), json.loads(lzma.decompress(ev_old))))
    print(f"check: event log {'identical bytes' if ev_new == ev_old else 'different bytes'}; "
          f"its JSON differs at {len(ev_rows)} paths")
    for p, x, y in ev_rows[:40]:
        print(f"  DIFF events.{'.'.join(map(str, p))}: rerun {_show(x)} | committed {_show(y)}")
    print(f"check: rerun took {res['seconds']} s on {res['env']['cpu']}, pin {res['env']['pin']}, "
          f"torch {res['env']['torch_cpu']}, hash pinned {res['env']['hash_pinned']}, pin late {res['env']['pin_late']}, "
          f"code {res['code']}")
    ok = not other and not ev_rows
    print("check: MATCH (apart from timing and provenance)" if ok else "check: MISMATCH", flush=True)
    return 0 if ok else 1


def status(B5):
    left = []
    print(f"slice {SLICE}:")
    for name, rids in RUN_IDS.items():
        done = B5._done(name) | _ids(B5, slice_file(B5, name))
        failed = _ids(B5, slice_file(B5, name, errors=True))
        for rid in rids:
            state = "done" if rid in done else ("failed" if rid in failed else "left")
            print(f"  {name} {rid}: {state}")
            if state != "done":
                left.append(rid)
    print(f"{len(left)} left" + (f"; to finish them: cd vertical-lab && python -m {MODULE} run" if left else ""),
          flush=True)
    return left


def main(argv):
    if os.environ.get("TWIN_PIN") is None:            # exactly as twin.bench5.main starts itself
        os.environ["TWIN_PIN"] = "avx2"
        os.environ["PYTHONHASHSEED"] = "0"
        sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, "-m", MODULE] + argv)
    from twin import repro as R
    R.reexec_pinned(MODULE)
    B5 = _b5()
    workers = int(os.environ.get("TWIN_WORKERS", "4"))
    cmd = argv[0] if argv else "status"
    if cmd == "check":
        sys.exit(check(B5))
    if cmd == "run":
        run(B5, workers)
        return
    if cmd == "status":
        status(B5)
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
