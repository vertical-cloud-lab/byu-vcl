"""Round 5, compute slice 5 of 6 (issue 416, for PR 405): eleven of round 5's runs, made with the engine as committed
at b410477 (nothing in twin/ changed) under bench5's own pin.

    cd vertical-lab
    python out/twin5/slices/run_slice_5.py check              # rerun arms' r5_conventional_external_fast_lean_s0 and
                                                              # compare it with the committed row (appends nothing)
    python out/twin5/slices/run_slice_5.py run [RUN_ID ...]   # this slice's runs not yet in its files (all, or the
                                                              # ones named), 4 at a time (TWIN_WORKERS)

It starts itself pinned exactly as ``python -m twin.bench5`` does (``twin.bench5.main``: ``TWIN_PIN=avx2`` and
``PYTHONHASHSEED=0`` if ``TWIN_PIN`` is unset, then the re-execution ``twin.repro.reexec_pinned`` makes, of this
script instead of ``-m twin.bench5``), and refuses to run under any other pin. Each run's config is the one in
``twin.bench5.EXPERIMENTS[<experiment>]`` with that run id, run with ``twin.bench5._safe`` (``run_one``, catching
what it raises) in a pool of worker processes, in the queue order of ``twin.bench5.plan``, as ``twin.bench5.run``
does. A row is appended to ``out/twin5/runs/<experiment>.slice-5.jsonl``, a run that raises to
``out/twin5/runs/<experiment>.slice-5.errors.jsonl``, and ``run_one`` writes the event log to
``out/twin5/events/<run id>.json.xz``. ``TWIN5_OUT`` moves ``out/twin5``, as it does for bench5.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]                    # vertical-lab/, where python -m twin.bench5 runs
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SLICE = 5
RUNS = {
    "net": ("r5_vertical_parallel_bofn3_lean_s6", "r5_vertical_parallel_bofn3_reorder_s9",
            "r5_vertical_parallel_pkgfn3_lean_s11", "r5_vertical_parallel_pkgfn3_lean_s5",
            "r5_vertical_parallel_pkgfn3_lean_s8"),
    "net_more": ("r5_vertical_parallel_bofn3_reorder_s12", "r5_vertical_parallel_bofn3_reorder_s15",
                 "r5_vertical_parallel_pkgfn3_lean_s14"),
    "plans_net": ("r5_vertical_wait_bofn3_reorder_s3", "r5_vertical_wait_bofn3_reorder_s6",
                  "r5_vertical_wait_bofn3_reorder_s9"),
}
CHECK = ("arms", "r5_conventional_external_fast_lean_s0")      # a committed row, rerun first and compared
NOT_COMPARED = ("seconds", "gp", "env", "code")                # timing (gp counts fits and their seconds) and provenance


def _pinned(argv):
    """Pin this process exactly as ``python -m twin.bench5`` pins itself (``twin.bench5.main``)."""
    me = [sys.executable, str(Path(__file__).resolve())]
    if os.environ.get("TWIN_PIN") is None:
        os.environ["TWIN_PIN"] = "avx2"
        os.environ["PYTHONHASHSEED"] = "0"
        sys.stdout.flush()
        os.execv(sys.executable, me + argv)
    from twin import repro as R                                 # twin/__init__.py applies the pin before numpy loads
    if not (R.hash_pinned() or os.environ.get("TWIN_PIN", "avx512").lower() == "off"):   # R.reexec_pinned's test
        os.environ["PYTHONHASHSEED"] = "0"
        sys.stdout.flush()
        os.execv(sys.executable, me + sys.argv[1:])
    if R.STATE["pin"] != "avx2" or not R.hash_pinned() or R.STATE["late"]:
        raise SystemExit(f"not bench5's pin (avx2, hashing pinned, applied before numpy): {R.STATE}, "
                         f"hash pinned {R.hash_pinned()}")
    return R


def _slice_file(B5, name, errors=False):
    return B5.RUNS / f"{name}.slice-{SLICE}{'.errors' if errors else ''}.jsonl"


def _done(B5, name):
    """Run ids with a row in this slice's file, or among the experiment's committed and appended rows."""
    done = set(B5._done(name))
    p = _slice_file(B5, name)
    if p.exists():
        for line in p.read_text().splitlines():
            try:
                done.add(B5.run_id(json.loads(line)["cfg"]))
            except Exception:
                pass
    return done


def _todo(B5, only=()):
    """This slice's runs not done yet, with their configs from bench5.EXPERIMENTS, in bench5.plan's queue order."""
    todo, mine = [], set()
    for name, rids in RUNS.items():
        by_id = {B5.run_id(c): c for c in B5.EXPERIMENTS[name]}
        done = _done(B5, name)
        for rid in rids:
            if rid not in by_id:
                raise SystemExit(f"{rid} is not a run of twin.bench5.EXPERIMENTS[{name!r}]")
            mine.add(rid)
            if only and rid not in only:
                continue
            if rid in done:
                print(f"{name} {rid}: done already", flush=True)
                continue
            todo.append((name, by_id[rid]))
    if set(only) - mine:
        raise SystemExit(f"not runs of slice {SLICE}: {sorted(set(only) - mine)}")
    # bench5.plan's key for the automated lab's BOFN and pKGFN: net seed by seed, the plans with BOFN, net_more
    rank = {"net": 2, "plans_net": 3, "net_more": 4}
    todo.sort(key=lambda t: (rank[t[0]], t[1]["seed"], B5.run_id(t[1])))
    return todo


def run(B5, todo, workers=4):
    """bench5.run's loop, writing this slice's files."""
    from concurrent.futures import ProcessPoolExecutor, as_completed
    B5.RUNS.mkdir(parents=True, exist_ok=True)
    print(f"slice {SLICE}: {len(todo)} runs, {workers} at a time: " + ", ".join(B5.run_id(c) for _, c in todo),
          flush=True)
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        futs = {ex.submit(B5._safe, c): (name, c) for name, c in todo}
        for fut in as_completed(futs):
            name, c = futs[fut]
            res = fut.result()
            if "error" in res:
                with _slice_file(B5, name, errors=True).open("a") as fh:
                    fh.write(json.dumps(B5.B2._jsonable(res)) + "\n")
                print(f"  {name} {B5.run_id(c)}: ERROR {res['error'].splitlines()[-1]}", flush=True)
                continue
            with _slice_file(B5, name).open("a") as fh:
                fh.write(json.dumps(res) + "\n")
            print(f"  {name} {B5.run_id(c)}: Al {res['campaigns']['flaime_al']['best_new']:.3f} "
                  f"Cu {res['campaigns']['onr_cu']['best_new']:.3f} ({res['seconds']} s; "
                  f"{time.time() - t0:.0f} s in)", flush=True)


def _diff(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                yield f"{path}/{k}", a.get(k, "<missing>"), b.get(k, "<missing>")
            else:
                yield from _diff(a[k], b[k], f"{path}/{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            yield f"{path} (length)", len(a), len(b)
        for i, (x, y) in enumerate(zip(a, b)):
            yield from _diff(x, y, f"{path}/{i}")
    elif isinstance(a, float) and isinstance(b, float) and a != a and b != b:
        return                                                  # NaN on both sides
    elif type(a) is not type(b) or a != b:
        yield path, a, b


def check(B5):
    """Rerun the committed row CHECK in a worker, as bench5.run makes a row, and compare everything but timing and
    provenance. Appends nothing; its event log overwrites the committed one (restore it with git checkout)."""
    import lzma
    from concurrent.futures import ProcessPoolExecutor
    name, rid = CHECK
    refs = [r for r in B5.load(name) if B5.run_id(r["cfg"]) == rid]
    cfgs = [c for c in B5.EXPERIMENTS[name] if B5.run_id(c) == rid]
    if len(refs) != 1 or len(cfgs) != 1:
        raise SystemExit(f"{name} {rid}: {len(refs)} committed rows, {len(cfgs)} configs")
    ref, cfg = refs[0], cfgs[0]
    ev = B5.EVENTS / f"{rid}.json.xz"
    ev_ref = ev.read_bytes() if ev.exists() else None
    with ProcessPoolExecutor(1) as ex:
        res = ex.submit(B5._safe, cfg).result()
    if "error" in res:
        print(res["error"])
        return 1
    a = {k: v for k, v in res.items() if k not in NOT_COMPARED}
    b = {k: v for k, v in ref.items() if k not in NOT_COMPARED}
    diffs = [(p, str(x)[:200], str(y)[:200]) for p, x, y in _diff(a, b)]
    ev_new = ev.read_bytes()
    ev_same_bytes = ev_ref == ev_new
    ev_same = ev_same_bytes or (ev_ref is not None and json.loads(lzma.decompress(ev_ref)) ==
                                json.loads(lzma.decompress(ev_new)))
    out = dict(experiment=name, run_id=rid, config_as_committed=cfg == ref["cfg"],
               identical=not diffs and json.dumps(a) == json.dumps(b), n_differences=len(diffs),
               differences=diffs[:20], not_compared=list(NOT_COMPARED),
               event_log_identical=ev_same, event_log_identical_bytes=ev_same_bytes,
               rerun=dict(seconds=res["seconds"], code=res["code"], env=res["env"]),
               committed=dict(seconds=ref["seconds"], code=ref["code"], env=ref["env"]))
    print(json.dumps(out, indent=1))
    (B5.OUT / "slices").mkdir(parents=True, exist_ok=True)
    (B5.OUT / "slices" / f"check_slice_{SLICE}.json").write_text(json.dumps(out, indent=1) + "\n")
    return 0 if out["identical"] and out["config_as_committed"] and ev_same else 1


def main(argv):
    _pinned(argv)
    from twin import bench5 as B5
    if argv[:1] == ["check"]:
        return check(B5)
    if argv[:1] == ["run"]:
        run(B5, _todo(B5, argv[1:]), int(os.environ.get("TWIN_WORKERS", "4")))
        return 0
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
