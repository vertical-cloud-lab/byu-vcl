"""Round 5, compute slice 4 of 6 (issue 415, for PR 405): this slice's runs, with the round-5 engine as committed
at b410477 and under its pin. Nothing in twin/ is changed; every row records whether twin/ was clean (``code``).

    cd vertical-lab
    python -m out.twin5.slices.run_slice_4 check    # rerun arms' r5_conventional_external_fast_lean_s0, compare
    python -m out.twin5.slices.run_slice_4 run      # this slice's runs not yet in runs/<experiment>.slice-4.jsonl
    python -m out.twin5.slices.run_slice_4 status   # done, failed and left

It starts itself exactly as ``python -m twin.bench5`` does (``bench5.main``): with ``TWIN_PIN`` unset it sets
``TWIN_PIN=avx2`` and ``PYTHONHASHSEED=0`` and re-executes, then calls ``twin.repro.reexec_pinned``. Each run is the
config in ``twin.bench5.EXPERIMENTS[<experiment>]`` whose ``run_id`` matches, run by ``twin.bench5._safe``
(``run_one``, an exception caught as ``bench5.run`` catches it), 4 at a time (``TWIN_WORKERS``) in a
ProcessPoolExecutor, in ``bench5.plan``'s order. A row is appended to ``runs/<experiment>.slice-4.jsonl``, an error to
``runs/<experiment>.slice-4.errors.jsonl``; ``run_one`` writes the event log to ``events/<run id>.json.xz``.

``check`` reruns one committed row and compares it with the row in ``runs/arms.jsonl.xz`` field by field, all but
timing and provenance (``seconds``; ``gp``, whose fit counts and times add up over a worker's runs; ``env``, the
machine; ``code``, the commit; ``events_file``), and its event log with the committed one. It appends the row
nowhere and writes only ``slices/slice-4.check.json``; restore the event file afterwards
(``git checkout -- out/twin5/events/``).
"""
from __future__ import annotations

import json
import os
import sys
import time

MODULE = "out.twin5.slices.run_slice_4"
SLICE = "slice-4"
RUNS = {
    "net": ["r5_vertical_parallel_bofn3_lean_s11", "r5_vertical_parallel_bofn3_lean_s8",
            "r5_vertical_parallel_bofn3_reorder_s6", "r5_vertical_parallel_pkgfn3_reorder_s11",
            "r5_vertical_parallel_pkgfn3_reorder_s5", "r5_vertical_parallel_pkgfn3_reorder_s8"],
    "net_more": ["r5_vertical_parallel_bofn3_lean_s14", "r5_vertical_parallel_pkgfn3_reorder_s14"],
    "plans_net": ["r5_vertical_external_bofn3_reorder_s11", "r5_vertical_external_bofn3_reorder_s2",
                  "r5_vertical_external_bofn3_reorder_s5", "r5_vertical_external_bofn3_reorder_s8"],
}
CHECK = ("arms", "r5_conventional_external_fast_lean_s0")
IGNORE = ("seconds", "gp", "env", "code", "events_file")
# environment variables that would change what bench5 runs (a shorter horizon, other output, other seed counts)
FORBIDDEN = ("TWIN5_DAYS", "TWIN5_OUT", "TWIN5_SEEDS", "TWIN5_NET_SEEDS")


def _configs():
    """(experiment, config) for each of this slice's runs, from bench5's own EXPERIMENTS."""
    from twin import bench5 as B5
    out = []
    for name, rids in RUNS.items():
        by_id = {B5.run_id(c): c for c in B5.EXPERIMENTS[name]}
        missing = [r for r in rids if r not in by_id]
        if missing:
            raise SystemExit(f"{name}: not in twin.bench5.EXPERIMENTS: {missing}")
        out += [(name, by_id[r]) for r in rids]
    return out


def _order(t):
    """bench5.plan's key for these runs (all the automated lab's): net, then plans_net, then net_more; by seed."""
    from twin import bench5 as B5
    name, c = t
    return ({"net": 2, "plans_net": 3}.get(name, 4), c["seed"], B5.run_id(c))


def _rows(name, kind=""):
    from twin import bench5 as B5
    p = B5.RUNS / f"{name}.{SLICE}{kind}.jsonl"
    out = []
    if p.exists():
        for line in p.read_text().splitlines():
            try:
                out.append(json.loads(line))
            except Exception:                          # a row being written while this reads
                pass
    return out


def _done(name):
    from twin import bench5 as B5
    return {B5.run_id(r["cfg"]) for r in _rows(name)}


def run(workers):
    from concurrent.futures import ProcessPoolExecutor, as_completed

    from twin import bench2 as B2
    from twin import bench5 as B5
    B5.RUNS.mkdir(parents=True, exist_ok=True)
    todo = [t for t in sorted(_configs(), key=_order) if B5.run_id(t[1]) not in _done(t[0])]
    print(f"{len(todo)} runs to do, {workers} at a time: " + ", ".join(B5.run_id(c) for _, c in todo), flush=True)
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        futs = {ex.submit(B5._safe, c): (name, c) for name, c in todo}
        for fut in as_completed(futs):
            name, c = futs[fut]
            res = fut.result()
            if "error" in res:
                with (B5.RUNS / f"{name}.{SLICE}.errors.jsonl").open("a") as fh:
                    fh.write(json.dumps(B2._jsonable(res)) + "\n")
                print(f"  {name} {B5.run_id(c)}: ERROR {res['error'].splitlines()[-1]}", flush=True)
                continue
            with (B5.RUNS / f"{name}.{SLICE}.jsonl").open("a") as fh:
                fh.write(json.dumps(res) + "\n")
            print(f"  {name} {B5.run_id(c)}: Al {res['campaigns']['flaime_al']['best_new']:.3f} "
                  f"Cu {res['campaigns']['onr_cu']['best_new']:.3f} ({res['seconds']} s; "
                  f"{time.time() - t0:.0f} s in; code {res['code']})", flush=True)


def status():
    from twin import bench5 as B5
    left = 0
    for name, rids in RUNS.items():
        done = _done(name)
        failed = {B5.run_id(r["cfg"]) for r in _rows(name, ".errors")} - done
        for r in rids:
            st = "done" if r in done else "FAILED" if r in failed else "left"
            left += st != "done"
            print(f"{name:10s} {r:45s} {st}")
    print(f"left: {left} of {sum(map(len, RUNS.values()))}")
    return left


def _diffs(a, b, path=""):
    """Every place two JSON values differ: (path, a, b). Leaves compare as JSON text (exact floats, NaN, int/float)."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in list(a) + [k for k in b if k not in a]:
            if k not in a or k not in b:
                yield (f"{path}/{k}", a.get(k, "<missing>"), b.get(k, "<missing>"))
            else:
                yield from _diffs(a[k], b[k], f"{path}/{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            yield (f"{path} (length)", len(a), len(b))
        for i, (x, y) in enumerate(zip(a, b)):
            yield from _diffs(x, y, f"{path}[{i}]")
    elif json.dumps(a) != json.dumps(b):
        yield (path, a, b)


def check():
    import lzma
    import subprocess
    from concurrent.futures import ProcessPoolExecutor

    from twin import bench5 as B5
    from twin import repro as R
    name, rid = CHECK
    ref = next(r for r in B5.load(name) if B5.run_id(r["cfg"]) == rid)
    cfg = next(c for c in B5.EXPERIMENTS[name] if B5.run_id(c) == rid)
    if json.dumps(cfg) != json.dumps(ref["cfg"]):
        raise SystemExit(f"bench5's config for {rid} is not the committed row's: {cfg} vs {ref['cfg']}")
    with ProcessPoolExecutor(1) as ex:                 # in a worker, as the committed row was made
        out = ex.submit(B5._safe, cfg).result()
    if "error" in out:
        print(out["error"])
        return 1
    diffs = list(_diffs(out, ref))
    top = lambda p: p.split("/")[1].split("[")[0].split(" ")[0]
    kept = [d for d in diffs if top(d[0]) not in IGNORE]
    same_rest = (json.dumps({k: v for k, v in out.items() if k not in IGNORE})
                 == json.dumps({k: v for k, v in ref.items() if k not in IGNORE}))
    ev = B5.EVENTS / f"{rid}.json.xz"
    git = subprocess.run(["git", "show", f"HEAD:./out/twin5/events/{rid}.json.xz"], cwd=B5.HERE.parent,
                         capture_output=True)
    ev_new, ev_ref = ev.read_bytes(), git.stdout
    ev_diffs = list(_diffs(json.loads(lzma.decompress(ev_new)), json.loads(lzma.decompress(ev_ref))))
    res = dict(
        run_id=rid, experiment=name, identical=not kept and same_rest and not ev_diffs,
        row_identical_but=sorted({top(d[0]) for d in diffs}), row_fields_differing=len(kept),
        row_first_diffs=[[p, str(x)[:200], str(y)[:200]] for p, x, y in kept[:10]],
        row_serialized_identical_but_ignored=same_rest, events_identical=not ev_diffs,
        events_xz_bytes_identical=ev_new == ev_ref, events_first_diffs=[[p, str(x)[:200], str(y)[:200]]
                                                                         for p, x, y in ev_diffs[:10]],
        ignored=list(IGNORE), torch_rng_used=[out["torch_rng_used"], ref["torch_rng_used"]],
        seconds=[out["seconds"], ref["seconds"]], cpu=[out["env"]["cpu"], ref["env"]["cpu"]],
        code=[out["code"], ref["code"]],
        env_differing={k: [out["env"].get(k), ref["env"].get(k)] for k in sorted(set(out["env"]) | set(ref["env"]))
                       if json.dumps(out["env"].get(k)) != json.dumps(ref["env"].get(k))},
        fingerprint=R.fingerprint())
    (B5.OUT / "slices" / f"{SLICE}.check.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0 if res["identical"] else 1


def main(argv):
    if os.environ.get("TWIN_PIN") is None:            # as bench5.main starts itself
        os.environ["TWIN_PIN"] = "avx2"
        os.environ["PYTHONHASHSEED"] = "0"
        sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, "-m", MODULE] + argv)
    from twin import repro as R
    R.reexec_pinned(MODULE)
    bad = [k for k in FORBIDDEN if os.environ.get(k)]
    if bad:
        raise SystemExit(f"unset {bad}: they change what bench5 runs")
    if os.environ["TWIN_PIN"] != "avx2" or not R.hash_pinned():
        raise SystemExit(f"not pinned as bench5 pins itself: TWIN_PIN={os.environ['TWIN_PIN']}, "
                         f"hash pinned {R.hash_pinned()}")
    if not argv or argv[0] == "status":
        status()
        return 0
    if argv[0] == "check":
        return check()
    if argv[0] == "run":
        run(int(os.environ.get("TWIN_WORKERS", "4")))
        return 1 if status() else 0
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
