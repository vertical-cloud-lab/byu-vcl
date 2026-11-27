"""Round 5, compute slice 6 of 6 (issue #417, stacked on PR #405): 11 runs of the round-5 engine as committed at b410477.

    cd vertical-lab
    python -m out.twin5.slices.run_slice_6 check    # rerun a committed row (arms, r5_conventional_external_fast_lean_s0)
                                                    # and compare it apart from timing and provenance; appends no row
    python -m out.twin5.slices.run_slice_6 run      # this slice's runs, 4 at a time (TWIN_WORKERS); skips any made
    python -m out.twin5.slices.run_slice_6 status   # made and left

Nothing in twin/ is changed or patched. Each run is ``twin.bench5.run_one`` for the config in
``twin.bench5.EXPERIMENTS[<experiment>]`` whose ``run_id`` matches, called through ``bench5._safe`` (which catches an
exception, as ``bench5.run`` does) in a pool of 4 processes. The driver starts itself pinned exactly as
``python -m twin.bench5`` does (``main()``: ``TWIN_PIN=avx2`` and ``PYTHONHASHSEED=0`` if ``TWIN_PIN`` is unset, then
``twin.repro.reexec_pinned``), so it has to be started with ``-m`` from vertical-lab/.

* a row is appended to ``out/twin5/runs/<experiment>.slice-6.jsonl``, and a run that raises to
  ``out/twin5/runs/<experiment>.slice-6.errors.jsonl``, as ``bench5.run`` writes its own (``runs/*.jsonl`` are in
  out/twin5/.gitignore, so add them with ``git add -f``);
* ``run_one`` writes the event log to ``out/twin5/events/<run id>.json.xz``;
* the longest runs go first (by the committed rows' median time for the arm), so 11 runs end about together;
* each worker reads its commit and whether twin/ is clean (``bench5._code``, which caches them) when it starts, not at
  the end of its first run, so a commit that only adds rows while the runs go on isn't recorded as the rows' code.

``check`` overwrites the committed event log of the run it repeats, compares it too, then restores it with
``git checkout`` so the slices don't collide. It writes its comparison (not the row) to
``out/twin5/slices/check.slice-6.json``.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

SLICE = 6
MODULE = "out.twin5.slices.run_slice_6"
VL = Path(__file__).resolve().parents[3]          # vertical-lab/
RUNS = {
    "net": ["r5_vertical_parallel_bofn3_lean_s9", "r5_vertical_parallel_bofn3_reorder_s7",
            "r5_vertical_parallel_pkgfn3_reorder_s6", "r5_vertical_parallel_pkgfn3_reorder_s9"],
    "net_more": ["r5_vertical_parallel_bofn3_lean_s12", "r5_vertical_parallel_bofn3_lean_s15",
                 "r5_vertical_parallel_pkgfn3_reorder_s12", "r5_vertical_parallel_pkgfn3_reorder_s15"],
    "plans_net": ["r5_vertical_external_bofn3_reorder_s3", "r5_vertical_external_bofn3_reorder_s6",
                  "r5_vertical_external_bofn3_reorder_s9"],
}
CHECK = ("arms", "r5_conventional_external_fast_lean_s0")
# timing (the run's wall time, the GP's fit and NUTS times) and provenance (the machine and the commit)
TIMING_PROVENANCE = {"/seconds", "/gp/fit_s", "/gp/nuts_s", "/env", "/code"}


def _cfg(B5, name, rid):
    m = [c for c in B5.EXPERIMENTS[name] if B5.run_id(c) == rid]
    if len(m) != 1:
        raise SystemExit(f"{name}: {len(m)} configs have run id {rid}")
    return m[0]


def _path(B5, name, kind=""):
    return B5.RUNS / f"{name}.slice-{SLICE}{kind}.jsonl"


def _mine(B5, name):
    """Run ids in this slice's file for ``name``."""
    p, out = _path(B5, name), set()
    if p.exists():
        for line in p.read_text().splitlines():
            try:
                out.add(B5.run_id(json.loads(line)["cfg"]))
            except Exception:                          # a row being written while this reads
                pass
    return out


def _warm():
    from twin import bench5 as B5
    B5._code()


def _expected_s(B5):
    """The committed rows' median wall time for each arm (net_more's arms are net's, with later seeds)."""
    secs = {}
    for name in RUNS:
        for r in B5.load(name):
            secs.setdefault(B5.group_key(r["cfg"]), []).append(r["seconds"])
    return {g: sorted(v)[len(v) // 2] for g, v in secs.items()}


def diffs(a, b, path="", out=None, cap=20):
    """Every place two JSON values differ (up to ``cap``), skipping timing and provenance."""
    out = [] if out is None else out
    if path in TIMING_PROVENANCE or len(out) >= cap:
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append((f"{path}/{k}", a.get(k, "<missing>"), b.get(k, "<missing>")))
            else:
                diffs(a[k], b[k], f"{path}/{k}", out, cap)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((f"{path} (length)", len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            diffs(x, y, f"{path}[{i}]", out, cap)
    elif isinstance(a, float) and isinstance(b, float) and a != a and b != b:     # NaN in both
        pass
    elif a != b or type(a) is not type(b):
        out.append((path, a, b))
    return out


def check():
    import lzma

    from twin import bench5 as B5
    name, rid = CHECK
    cfg = _cfg(B5, name, rid)
    ref = [r for r in B5.load(name) if B5.run_id(r["cfg"]) == rid]
    if len(ref) != 1:
        raise SystemExit(f"{name}: {len(ref)} committed rows for {rid}")
    ref = ref[0]
    ev = B5.EVENTS / f"{rid}.json.xz"
    rel = ev.relative_to(VL)
    if subprocess.run(["git", "status", "--porcelain", "--", str(rel)], cwd=VL, capture_output=True,
                      text=True).stdout.strip():
        raise SystemExit(f"{rel} differs from the commit; restore it first (git checkout -- {rel})")
    ref_ev = ev.read_bytes()
    with ProcessPoolExecutor(1, initializer=_warm) as ex:
        res = ex.submit(B5._safe, cfg).result()
    new_ev = ev.read_bytes()
    subprocess.run(["git", "checkout", "--", str(rel)], cwd=VL, check=True)   # restore the committed event log
    if "error" in res:
        print(res["error"])
        return 1
    res = json.loads(json.dumps(res))
    d_row = diffs(res, ref)
    d_ev = diffs(json.loads(lzma.decompress(new_ev)), json.loads(lzma.decompress(ref_ev)))
    env_d = {k: [res["env"].get(k), ref["env"].get(k)] for k in sorted(set(res["env"]) | set(ref["env"]))
             if res["env"].get(k) != ref["env"].get(k)}
    rep = dict(experiment=name, run_id=rid, row_identical=not d_row, row_diffs=[list(map(str, d)) for d in d_row],
               events_identical=not d_ev, events_diffs=[list(map(str, d)) for d in d_ev],
               events_xz_bytes_identical=new_ev == ref_ev,
               not_compared=sorted(TIMING_PROVENANCE),
               timing=dict(seconds=[res["seconds"], ref["seconds"]], gp=[res["gp"], ref["gp"]]),
               provenance=dict(code=[res["code"], ref["code"]], env_differs=env_d),
               pin=dict(pin=res["env"]["pin"], pin_late=res["env"]["pin_late"],
                        hash_pinned=res["env"]["hash_pinned"], torch_cpu=res["env"].get("torch_cpu"),
                        blas=[(b["api"], b["arch"], b["threads"]) for b in res["env"]["blas"] or []]),
               note="[this rerun, the committed row]; the rerun's row is not appended anywhere and the committed "
                    "event log was restored with git checkout")
    out = Path(__file__).resolve().parent / f"check.slice-{SLICE}.json"
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep, indent=1))
    return 0 if rep["row_identical"] and rep["events_identical"] else 1


def run(workers):
    from twin import bench2 as B2
    from twin import bench5 as B5
    B5.RUNS.mkdir(parents=True, exist_ok=True)
    todo = []
    for name, rids in RUNS.items():
        made = _mine(B5, name) | B5._done(name)
        todo += [(name, _cfg(B5, name, rid)) for rid in rids if rid not in made]
    exp = _expected_s(B5)
    todo.sort(key=lambda t: (-exp.get(B5.group_key(t[1]), 0.0), t[0], t[1]["seed"]))
    n = sum(map(len, RUNS.values()))
    print(f"slice {SLICE}: {len(todo)} of {n} runs to do, {workers} at a time:", flush=True)
    for name, c in todo:
        print(f"  {name} {B5.run_id(c)} (about {exp.get(B5.group_key(c), 0.0) / 60:.0f} min)", flush=True)
    t0 = time.time()
    with ProcessPoolExecutor(workers, initializer=_warm) as ex:
        futs = {ex.submit(B5._safe, c): (name, c) for name, c in todo}
        for fut in as_completed(futs):
            name, c = futs[fut]
            res = fut.result()
            if "error" in res:
                with _path(B5, name, ".errors").open("a") as fh:
                    fh.write(json.dumps(B2._jsonable(res)) + "\n")
                print(f"  {name} {B5.run_id(c)}: ERROR {res['error'].splitlines()[-1]}", flush=True)
                continue
            with _path(B5, name).open("a") as fh:
                fh.write(json.dumps(res) + "\n")
            print(f"  {name} {B5.run_id(c)}: Al {res['campaigns']['flaime_al']['best_new']:.3f} "
                  f"Cu {res['campaigns']['onr_cu']['best_new']:.3f} ({res['seconds']} s; "
                  f"{time.time() - t0:.0f} s in)", flush=True)
    return status()


def status():
    from twin import bench5 as B5
    left = 0
    for name, rids in RUNS.items():
        mine, errs = _mine(B5, name), set()
        pe = _path(B5, name, ".errors")
        if pe.exists():
            errs = {B5.run_id(json.loads(line)["cfg"]) for line in pe.read_text().splitlines() if line.strip()}
        for rid in rids:
            st = "made" if rid in mine else "error" if rid in errs else "left"
            left += st != "made"
            print(f"{name:10s} {rid:45s} {st}")
    print(f"left: {left}")
    return 0 if left == 0 else 1


def main(argv):
    if os.environ.get("TWIN_PIN") is None:                 # as twin.bench5.main starts itself
        os.environ["TWIN_PIN"] = "avx2"
        os.environ["PYTHONHASHSEED"] = "0"
        sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, "-m", MODULE] + argv)
    from twin import repro as R
    R.reexec_pinned(MODULE)
    cmd = argv[0] if argv else "status"
    if cmd == "check":
        return check()
    if cmd == "run":
        return run(int(os.environ.get("TWIN_WORKERS", "4")))
    if cmd == "status":
        return status()
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
