"""One-off extra check (not a row): rerun committed conventional-lab BOFN and pKGFN rows of `net` (seed 0, lean),
which fit GPs, and compare them with the committed rows apart from timing and provenance, as run_slice_6 check does.

    cd vertical-lab && TWIN_PIN=avx2 PYTHONHASHSEED=0 python out/twin5/slices/check_gp_slice_6.py

TWIN_PIN and PYTHONHASHSEED are set when the interpreter starts: the driver's pinned state."""
import json, lzma, subprocess, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

VL = Path.cwd()
sys.path.insert(0, str(VL))


def main():
    from twin import bench5 as B5               # twin/__init__ applies the pin before numpy and torch load
    import importlib
    d = importlib.import_module("out.twin5.slices.run_slice_6")
    rids = ["r5_conventional_external_bofn3_lean_s0", "r5_conventional_external_pkgfn3_lean_s0"]
    cfgs = {r: d._cfg(B5, "net", r) for r in rids}
    refs = {B5.run_id(r["cfg"]): r for r in B5.load("net") if B5.run_id(r["cfg"]) in rids}
    evs = {r: B5.EVENTS / f"{r}.json.xz" for r in rids}
    for r, ev in evs.items():
        assert not subprocess.run(["git", "status", "--porcelain", "--", str(ev.relative_to(VL))], cwd=VL,
                                  capture_output=True, text=True).stdout.strip(), ev
    ref_ev = {r: ev.read_bytes() for r, ev in evs.items()}
    with ProcessPoolExecutor(2, initializer=d._warm, max_tasks_per_child=1) as ex:
        futs = {r: ex.submit(B5._safe, cfgs[r]) for r in rids}
        res = {r: f.result() for r, f in futs.items()}
    new_ev = {r: ev.read_bytes() for r, ev in evs.items()}
    for ev in evs.values():
        subprocess.run(["git", "checkout", "--", str(ev.relative_to(VL))], cwd=VL, check=True)
    out = []
    for r in rids:
        if "error" in res[r]:
            out.append(dict(run_id=r, error=res[r]["error"][-500:]))
            continue
        dr = d.diffs(res[r], refs[r])
        de = d.diffs(json.loads(lzma.decompress(new_ev[r])), json.loads(lzma.decompress(ref_ev[r])))
        out.append(dict(experiment="net", run_id=r, row_identical=not dr, row_diffs=[list(map(str, x)) for x in dr],
                        events_identical=not de, events_diffs=[list(map(str, x)) for x in de],
                        events_xz_bytes_identical=new_ev[r] == ref_ev[r],
                        seconds=[res[r]["seconds"], refs[r]["seconds"]], gp=[res[r]["gp"], refs[r]["gp"]],
                        cpu=[res[r]["env"]["cpu"], refs[r]["env"]["cpu"]],
                        code=[res[r]["code"], refs[r]["code"]]))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
