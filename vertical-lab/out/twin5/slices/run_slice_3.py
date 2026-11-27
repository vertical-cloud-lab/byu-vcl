"""Round 5, compute slice 3 of 6 (issue #414, for PR #405): twelve of the automated lab's BOFN and pKGFN runs.

    cd vertical-lab
    python -m out.twin5.slices.run_slice_3 check    # rerun arms' r5_conventional_external_fast_lean_s0 and compare
    python -m out.twin5.slices.run_slice_3 run      # this slice's runs not made yet, 4 at a time (TWIN_WORKERS)
    python -m out.twin5.slices.run_slice_3 status   # this slice's runs done, failed and left

``python out/twin5/slices/run_slice_3.py ...`` does the same (it re-executes itself as the module, from vertical-lab/).

Nothing in twin/ changes, and this file is outside it, so each row's ``code.twin_dirty`` still says whether twin/
matched the commit the row records. It starts pinned exactly as ``python -m twin.bench5`` starts itself
(``bench5.main``): with ``TWIN_PIN`` unset it sets ``TWIN_PIN=avx2`` and ``PYTHONHASHSEED=0`` and re-executes, then
calls ``twin.repro.reexec_pinned``. It imports nothing but the standard library before the ``twin`` package, so the
package's pin (twin/repro.py) is set before numpy or torch load, here and in the workers.

``run`` takes each run's config from ``twin.bench5.EXPERIMENTS[<experiment>]`` (the one whose run id matches) and
calls ``twin.bench5.run_one``, through ``bench5._safe``, in a pool of worker processes, as ``bench5.run`` does. A row is
appended to ``out/twin5/runs/<experiment>.slice-3.jsonl``, a run that raises to
``out/twin5/runs/<experiment>.slice-3.errors.jsonl``, and ``run_one`` writes the event log to
``out/twin5/events/<run id>.json.xz``. Runs already in this slice's rows are skipped, so running it again does
what's left. The longest runs go first (pKGFN, then BOFN in the parallel plan, then BOFN in the waiting plan, which
takes about a third as long), so the four workers finish close together. The order changes no row.

``check`` reruns one committed row the same way (in a worker process) and compares it with ``arms``' committed row,
apart from timing (``seconds``, ``gp.fit_s``, ``gp.nuts_s``) and provenance (``env``, ``code``), and compares the event
log it writes with the committed one. It appends no row. It does overwrite that run's committed event log, so restore
it afterwards (``git checkout -- out/twin5/events/``).
"""
from __future__ import annotations

import json
import lzma
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

MODULE = "out.twin5.slices.run_slice_3"
LAB = Path(__file__).resolve().parents[3]                    # vertical-lab/
SLICE = "slice-3"
RUN_IDS = {
    "net": ["r5_vertical_parallel_bofn3_lean_s5", "r5_vertical_parallel_bofn3_reorder_s11",
            "r5_vertical_parallel_bofn3_reorder_s8", "r5_vertical_parallel_pkgfn3_lean_s10",
            "r5_vertical_parallel_pkgfn3_lean_s4", "r5_vertical_parallel_pkgfn3_lean_s7"],
    "net_more": ["r5_vertical_parallel_bofn3_reorder_s14", "r5_vertical_parallel_pkgfn3_lean_s13"],
    "plans_net": ["r5_vertical_wait_bofn3_reorder_s11", "r5_vertical_wait_bofn3_reorder_s2",
                  "r5_vertical_wait_bofn3_reorder_s5", "r5_vertical_wait_bofn3_reorder_s8"],
}
CHECK = ("arms", "r5_conventional_external_fast_lean_s0")
IGNORED = {("seconds",): "timing", ("gp", "fit_s"): "timing", ("gp", "nuts_s"): "timing",
           ("env",): "provenance", ("code",): "provenance"}


def start_pinned(argv):
    """``bench5.main``'s start, for this module."""
    if os.environ.get("TWIN_PIN") is None:
        os.environ["TWIN_PIN"] = "avx2"
        os.environ["PYTHONHASHSEED"] = "0"
        sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, "-m", MODULE] + argv)
    from twin import repro as R
    R.reexec_pinned(MODULE)


def configs(B5):
    out = []
    for name, rids in RUN_IDS.items():
        for rid in rids:
            hits = [c for c in B5.EXPERIMENTS[name] if B5.run_id(c) == rid]
            if len(hits) != 1:
                raise SystemExit(f"{name}: {len(hits)} configs have run id {rid}")
            out.append((name, hits[0]))
    return out


def _ids(path, B5):
    out = set()
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                out.add(B5.run_id(json.loads(line)["cfg"]))
            except Exception:                              # a row being written while this reads
                pass
    return out


def done(B5, name):
    return _ids(B5.RUNS / f"{name}.{SLICE}.jsonl", B5)


def failed(B5, name):
    return _ids(B5.RUNS / f"{name}.{SLICE}.errors.jsonl", B5)


def order(B5, todo):
    """Longest first: on round 5's runner pKGFN took 29-37 min a run, BOFN 21-30, BOFN in the waiting plan 10."""
    rank = {"pkgfn3": 0, "bofn3": 1}
    return sorted(todo, key=lambda t: (t[1]["plan"] == "wait", rank.get(t[1]["policy"], 2), t[1]["seed"],
                                       B5.run_id(t[1])))


def run(B5, workers=4):
    B5.RUNS.mkdir(parents=True, exist_ok=True)
    todo = order(B5, [(n, c) for n, c in configs(B5) if B5.run_id(c) not in done(B5, n)])
    print(f"{SLICE}: {len(todo)} runs to do, {workers} at a time: " + ", ".join(B5.run_id(c) for _, c in todo),
          flush=True)
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        futs = {ex.submit(B5._safe, c): (name, c) for name, c in todo}
        for fut in as_completed(futs):
            name, c = futs[fut]
            res = fut.result()
            if "error" in res:
                with (B5.RUNS / f"{name}.{SLICE}.errors.jsonl").open("a") as fh:
                    fh.write(json.dumps(B5.B2._jsonable(res)) + "\n")
                print(f"  {name} {B5.run_id(c)}: ERROR {res['error'].splitlines()[-1]}", flush=True)
                continue
            with (B5.RUNS / f"{name}.{SLICE}.jsonl").open("a") as fh:
                fh.write(json.dumps(res) + "\n")
            print(f"  {name} {B5.run_id(c)}: Al {res['campaigns']['flaime_al']['best_new']:.3f} "
                  f"Cu {res['campaigns']['onr_cu']['best_new']:.3f} ({res['seconds']} s; "
                  f"{time.time() - t0:.0f} s in)", flush=True)


def status(B5):
    n = {"done": 0, "failed": 0, "left": 0}
    for name, rids in RUN_IDS.items():
        d, f = done(B5, name), failed(B5, name)
        for rid in rids:
            s = "done" if rid in d else "failed" if rid in f else "left"
            n[s] += 1
            print(f"{name:9s} {rid}: {s}")
    print(f"{SLICE}: {n['done']} done, {n['failed']} failed (not done), {n['left']} left", flush=True)


def diff(a, b, path=()):
    """Every path at which two parsed JSON values differ, with both values."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                yield path + (k,), a.get(k, "<missing>"), b.get(k, "<missing>")
            else:
                yield from diff(a[k], b[k], path + (k,))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            yield path + ("<len>",), len(a), len(b)
        for i, (x, y) in enumerate(zip(a, b)):
            yield from diff(x, y, path + (i,))
    elif type(a) is not type(b) or a != b:
        yield path, a, b


def check(B5):
    name, rid = CHECK
    ref = next(r for r in B5.load(name) if B5.run_id(r["cfg"]) == rid)
    cfg = next(c for c in B5.EXPERIMENTS[name] if B5.run_id(c) == rid)
    print(f"check: rerunning {name} {rid} (config as committed: {cfg == ref['cfg']})", flush=True)
    with ProcessPoolExecutor(1) as ex:
        res = ex.submit(B5._safe, cfg).result()
    if "error" in res:
        print(f"check: the rerun raised\n{res['error']}", flush=True)
        return 1
    ignored, real = [], []
    for p, x, y in diff(ref, res):
        why = next((w for k, w in IGNORED.items() if p[:len(k)] == k), None)
        (ignored if why else real).append((p, x, y, why))
    for p, x, y, why in ignored:
        print(f"  ignored ({why}) {'.'.join(map(str, p))}: {str(x)[:100]} -> {str(y)[:100]}")
    for p, x, y, _ in real[:40]:
        print(f"  DIFFERS {'.'.join(map(str, p))}: {str(x)[:100]} -> {str(y)[:100]}")
    ev = B5.EVENTS / f"{rid}.json.xz"
    git = subprocess.run(["git", "show", f"HEAD:./{ev.relative_to(LAB)}"], cwd=LAB, capture_output=True)
    if git.returncode:
        print(f"check: no committed event log for {rid}", flush=True)
        ev_same = False
    else:
        ev_same = ev.read_bytes() == git.stdout
        if not ev_same:
            evd = list(diff(json.loads(lzma.decompress(git.stdout)), B5.read_events(ev)))
            for p, x, y in evd[:40]:
                print(f"  EVENT LOG DIFFERS {'.'.join(map(str, p))}: {str(x)[:100]} -> {str(y)[:100]}")
            ev_same = not evd
    print(json.dumps(dict(run_id=rid, row_identical=not real, n_differences=len(real), event_log_identical=ev_same,
                          seconds=[ref.get("seconds"), res.get("seconds")], cpu=[ref["env"]["cpu"], res["env"]["cpu"]],
                          pin=res["env"]["pin"], hash_pinned=res["env"]["hash_pinned"],
                          pin_late=res["env"]["pin_late"], torch_cpu=res["env"].get("torch_cpu"),
                          blas=[d.get("arch") for d in res["env"].get("blas") or []], code=res["code"])), flush=True)
    return 0 if not real and ev_same else 1


def main(argv):
    start_pinned(argv)
    from twin import bench5 as B5
    if not argv or argv[0] == "status":
        status(B5)
        return 0
    if argv[0] == "check":
        return check(B5)
    if argv[0] == "run":
        run(B5, int(os.environ.get("TWIN_WORKERS", "4")))
        status(B5)
        return 0
    raise SystemExit(__doc__)


if __name__ == "__main__":
    if __spec__ is None:                                     # run as a file: re-execute as the module
        os.chdir(LAB)
        sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, "-m", MODULE] + sys.argv[1:])
    sys.exit(main(sys.argv[1:]))
