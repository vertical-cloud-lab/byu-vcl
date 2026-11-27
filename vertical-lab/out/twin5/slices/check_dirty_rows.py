"""Round 5, a check made when the slices were folded in (not rows): do this PR's own rows that carry
``twin_dirty: true`` reproduce from the committed engine?

    git worktree add --detach /tmp/twin5clean b410477a          # a clean checkout of the engine of record
    cd /tmp/twin5clean/vertical-lab && mkdir -p /tmp/twin5dirty && \
        TWIN_PIN=avx2 PYTHONHASHSEED=0 TWIN5_OUT=/tmp/twin5dirty \
        python <this checkout>/vertical-lab/out/twin5/slices/check_dirty_rows.py > check_dirty_rows.json

72 BOFN and pKGFN rows (recorded commit 3de9012) and the 32 hpc_more rows (f2b40fd) were made while files in twin/
were edited and not yet committed, so their flag is true and can't say which files differed. This reruns five of them
with the engine at b410477 from a detached worktree (so each rerun records b410477 and twin_dirty false), on the same
CPU model they were made on (an AMD EPYC 9V45), each in a fresh worker, with outputs under TWIN5_OUT (outside the
repository). The engine and the committed rows and event logs are read from the working directory. A row is compared
apart from timing and provenance (``seconds``, ``gp``, ``env``, ``code``, ``events_file``), and its event log as
decompressed JSON.
"""
import json
import lzma
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

VL = Path.cwd()
sys.path.insert(0, str(VL))
assert os.environ.get("TWIN_PIN") == "avx2" and os.environ.get("PYTHONHASHSEED") == "0"
assert os.environ.get("TWIN5_OUT", "").startswith("/tmp/")
from twin import bench5 as B5                    # the twin package applies the pin before numpy and torch load

RUNS = [("hpc_more", "r5_conventional_external_fast_reorder_s0_hpc-add_per_day256-keep512"),
        ("hpc_more", "r5_vertical_parallel_fast_reorder_s0_hpc-add_per_day256-keep512"),
        ("net", "r5_conventional_external_bofn3_reorder_s1"),
        ("net", "r5_conventional_external_pkgfn3_lean_s5"),
        ("net", "r5_vertical_parallel_bofn3_reorder_s1")]
NOT = {("seconds",), ("gp",), ("env",), ("code",), ("events_file",)}


def diff(a, b, path=()):
    if path in NOT:
        return []
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                if path + (k,) not in NOT:
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
    return [] if (type(a) is type(b) and a == b) else [(path, a, b)]


def committed(name, rid):
    lines = lzma.decompress((VL / "out/twin5/runs" / f"{name}.jsonl.xz").read_bytes()).decode().splitlines()
    return [r for r in map(json.loads, (l for l in lines if l.strip())) if B5.run_id(r["cfg"]) == rid][0]


if __name__ == "__main__":
    refs = {rid: committed(name, rid) for name, rid in RUNS}
    cfgs = {rid: [c for c in B5.EXPERIMENTS[name] if B5.run_id(c) == rid][0] for name, rid in RUNS}
    for rid in refs:
        assert cfgs[rid] == refs[rid]["cfg"], rid
        assert refs[rid]["code"]["twin_dirty"] is True, rid
    with ProcessPoolExecutor(4, max_tasks_per_child=1) as ex:
        futs = {rid: ex.submit(B5._safe, cfgs[rid]) for _, rid in RUNS}
        res = {rid: f.result() for rid, f in futs.items()}
    out = []
    for name, rid in RUNS:
        new, ref = res[rid], refs[rid]
        if "error" in new:
            out.append(dict(run_id=rid, error=new["error"][-600:]))
            continue
        d = diff(new, ref)
        ev_new = B5.read_events(Path(os.environ["TWIN5_OUT"]) / "events" / f"{rid}.json.xz")
        ev_ref = B5.read_events(VL / "out/twin5/events" / f"{rid}.json.xz")
        out.append(dict(experiment=name, run_id=rid, committed_on=ref["env"]["cpu"], rerun_on=new["env"]["cpu"],
                        row_identical=not d, n_differences=len(d), event_log_identical=ev_new == ev_ref,
                        first_differences=[["/".join(map(str, p)), str(x)[:60], str(y)[:60]] for p, x, y in d[:4]],
                        code=dict(rerun=new["code"], committed=ref["code"]),
                        seconds=dict(rerun=new["seconds"], committed=ref["seconds"])))
    print(json.dumps(dict(
        what="five of this PR's rows that carry twin_dirty: true, rerun with the engine at b410477 (a detached worktree) on "
             "the CPU model they were made on; [rerun, committed] are compared apart from timing and provenance",
        pin=os.environ["TWIN_PIN"], reruns=out), indent=1))
