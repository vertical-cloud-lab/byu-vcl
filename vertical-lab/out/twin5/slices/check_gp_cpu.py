"""Round 5, a check made when the slices were folded in (not rows): do committed BOFN rows reproduce on another CPU?

    cd vertical-lab && mkdir -p /tmp/twin5cpu && TWIN_PIN=avx2 PYTHONHASHSEED=0 TWIN5_OUT=/tmp/twin5cpu \
        python out/twin5/slices/check_gp_cpu.py > out/twin5/slices/check_gp_cpu.json

The slices' requested check reruns a heuristic-and-funnel row, which fits no GP. Slice 6 found that two committed BOFN
and pKGFN rows made on an AMD EPYC 9V45 don't reproduce on its Intel Xeon under the same pin. The six slices ran on four
CPU models, so this reruns four committed BOFN rows of ``plans_net``, one made on each model, on the runner that folds
them in, with the engine at b410477 and the same pin, each in a fresh worker. Outputs go under TWIN5_OUT (outside the
repository); the committed rows and event logs are only read. A row is compared apart from timing and provenance
(``seconds``, ``gp``, ``env``, ``code``, ``events_file``), and its event log as decompressed JSON.
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

RUNS = [("plans_net", "r5_vertical_wait_bofn3_reorder_s1"),        # made on an AMD EPYC 9V45 (slice 1)
        ("plans_net", "r5_vertical_external_bofn3_reorder_s10"),   # an AMD EPYC 9V74 (slice 2)
        ("plans_net", "r5_vertical_wait_bofn3_reorder_s2"),        # an AMD EPYC 7763 (slice 3)
        ("plans_net", "r5_vertical_wait_bofn3_reorder_s3")]        # an Intel Xeon 6975P-C (slice 5)
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


def days(row, T):
    from twin import bench2 as B2
    out = {}
    for camp in ("flaime_al", "onr_cu"):
        for tn in ("T1", "T2"):
            h = B2.hit(row["campaigns"][camp]["curve_new"], T[tn][camp], 2)
            out[f"{camp}|{tn}"] = round(float(h[0]), 1) if h else None
    return out


if __name__ == "__main__":
    from twin import bench2 as B2
    T = B2.targets()
    refs = {rid: committed(name, rid) for name, rid in RUNS}
    cfgs = {rid: [c for c in B5.EXPERIMENTS[name] if B5.run_id(c) == rid][0] for name, rid in RUNS}
    for rid in refs:
        assert cfgs[rid] == refs[rid]["cfg"], rid
    with ProcessPoolExecutor(len(RUNS), max_tasks_per_child=1) as ex:
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
        out.append(dict(
            experiment=name, run_id=rid, committed_on=ref["env"]["cpu"], rerun_on=new["env"]["cpu"],
            row_identical=not d, n_differences=len(d), event_log_identical=ev_new == ev_ref,
            first_differences=[["/".join(map(str, p)), str(x)[:60], str(y)[:60]] for p, x, y in d[:4]],
            env_same_apart_from_cpu={k: v for k, v in new["env"].items() if k not in ("cpu", "avx512")}
            == {k: v for k, v in ref["env"].items() if k not in ("cpu", "avx512")},
            code=dict(rerun=new["code"], committed=ref["code"]), seconds=dict(rerun=new["seconds"], committed=ref["seconds"]),
            gp_fits_rerun=new["gp"]["fits"],
            best_new=dict(rerun={k: round(v["best_new"], 4) for k, v in new["campaigns"].items()},
                          committed={k: round(v["best_new"], 4) for k, v in ref["campaigns"].items()}),
            days_to_target=dict(rerun=days(new, T), committed=days(ref, T))))
    print(json.dumps(dict(
        what="four committed BOFN rows (plans_net), one made on each CPU model the slices ran on, rerun on the runner "
             "that folded the slices in; [rerun, committed] are compared apart from timing and provenance",
        runner_cpu=out[0].get("rerun_on") if out else None, pin=os.environ["TWIN_PIN"], reruns=out), indent=1))
