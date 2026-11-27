"""Diagnostic (not rows): is a GP-based run deterministic on this machine, and independent of the worker's history?
A, B: r5_conventional_external_bofn3_lean_s0 in two fresh workers. C: the same run in a worker that first ran
r5_conventional_external_bofn3_reorder_s0. Compare A-B and A-C apart from timing, provenance and the GP counters (which
bench5 accumulates per worker). Restores the committed event logs afterwards.

    cd vertical-lab && TWIN_PIN=avx2 PYTHONHASHSEED=0 python out/twin5/slices/check_det_slice_6.py
"""
import json, subprocess, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

VL = Path.cwd()
sys.path.insert(0, str(VL))


def main():
    from twin import bench5 as B5
    import importlib
    d = importlib.import_module("out.twin5.slices.run_slice_6")
    d.TIMING_PROVENANCE.update({"/gp/fits", "/gp/nuts"})
    rid, pre = "r5_conventional_external_bofn3_lean_s0", "r5_conventional_external_bofn3_reorder_s0"
    evs = [B5.EVENTS / f"{r}.json.xz" for r in (rid, pre)]
    cfg, cfg_pre = d._cfg(B5, "net", rid), d._cfg(B5, "net", pre)
    ea = ProcessPoolExecutor(1, initializer=d._warm, max_tasks_per_child=1)
    eb = ProcessPoolExecutor(1, initializer=d._warm, max_tasks_per_child=1)
    ec = ProcessPoolExecutor(1, initializer=d._warm)
    fa, fb = ea.submit(B5._safe, cfg), eb.submit(B5._safe, cfg)
    fp = ec.submit(B5._safe, cfg_pre)
    fc = ec.submit(B5._safe, cfg)
    a, b, p, c = fa.result(), fb.result(), fp.result(), fc.result()
    for e in (ea, eb, ec):
        e.shutdown()
    for ev in evs:
        subprocess.run(["git", "checkout", "--", str(ev.relative_to(VL))], cwd=VL, check=True)
    ref = {B5.run_id(r["cfg"]): r for r in B5.load("net")}
    rep = {}
    for name, x in (("A", a), ("B", b), ("C", c)):
        if "error" in x:
            rep[name] = x["error"][-400:]
            continue
        rep[name] = dict(best_al=x["campaigns"]["flaime_al"]["best"], n_al=len(x["campaigns"]["flaime_al"]["curve_new"]),
                         gp=x["gp"], seconds=x["seconds"])
    rep["A_vs_B"] = [list(map(str, t)) for t in d.diffs(a, b)]
    rep["A_vs_C"] = [list(map(str, t)) for t in d.diffs(a, c)]
    rep["pre_vs_committed"] = [list(map(str, t)) for t in d.diffs(p, ref[pre])][:5]
    rep["committed"] = dict(best_al=ref[rid]["campaigns"]["flaime_al"]["best"],
                            n_al=len(ref[rid]["campaigns"]["flaime_al"]["curve_new"]), gp=ref[rid]["gp"])
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
