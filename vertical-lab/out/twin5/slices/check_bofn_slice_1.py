"""Extra check, not a slice run (its output: verify_slice_1_bofn.json). Made with

    cd vertical-lab && mkdir -p /tmp/twin5check && TWIN_PIN=avx2 PYTHONHASHSEED=0 TWIN5_OUT=/tmp/twin5check \
        python out/twin5/slices/check_bofn_slice_1.py

It reruns the committed net row r5_conventional_external_bofn3_lean_s0 (made at 9ecef6f,
twin clean; the engine is unchanged to b410477) with outputs under TWIN5_OUT=/tmp/twin5check, compare with the
committed row and event log in the repo. Exercises BOFN's GP fits under the pin."""
import json, lzma, os, sys
sys.path.insert(0, os.getcwd())
assert os.environ.get("TWIN_PIN") == "avx2" and os.environ.get("PYTHONHASHSEED") == "0"
assert os.environ.get("TWIN5_OUT") == "/tmp/twin5check"
from twin import bench5 as B5
from concurrent.futures import ProcessPoolExecutor
NOT = {("seconds",), ("gp", "fit_s"), ("gp", "nuts_s"), ("env",), ("code",), ("events_file",)}
def diff(a, b, path=()):
    if path in NOT: return []
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                out.append((path + (k,), a.get(k, "<missing>"), b.get(k, "<missing>"))); continue
            out += diff(a[k], b[k], path + (k,))
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b): return [(path + ("len",), len(a), len(b))]
        out = []
        for i, (x, y) in enumerate(zip(a, b)): out += diff(x, y, path + (i,))
        return out
    return [] if (type(a) is type(b) and a == b) else [(path, a, b)]
if __name__ == "__main__":
    rid = "r5_conventional_external_bofn3_lean_s0"
    rows = [json.loads(l) for l in lzma.decompress(open("out/twin5/runs/net.jsonl.xz", "rb").read()).decode().splitlines() if l.strip()]
    ref = [r for r in rows if B5.run_id(r["cfg"]) == rid][0]
    cfg = [c for c in B5.EXPERIMENTS["net"] if B5.run_id(c) == rid][0]
    assert cfg == ref["cfg"]
    with ProcessPoolExecutor(1) as ex:
        out = ex.submit(B5._safe, cfg).result()
    assert "error" not in out, out.get("error")
    d = diff(out, ref)
    ev_new = B5.read_events(f"/tmp/twin5check/events/{rid}.json.xz")
    ev_ref = B5.read_events(f"out/twin5/events/{rid}.json.xz")
    print(json.dumps(dict(run_id=rid, identical_apart_from_timing_and_provenance=not d, n_differences=len(d),
                          differences=[[list(p), str(x)[:150], str(y)[:150]] for p, x, y in d[:20]],
                          event_log_identical=ev_new == ev_ref, gp=dict(rerun=out["gp"], committed=ref["gp"]),
                          torch_rng_used=dict(rerun=out["torch_rng_used"], committed=ref["torch_rng_used"]),
                          seconds=dict(rerun=out["seconds"], committed=ref["seconds"]),
                          code=dict(rerun=out["code"], committed=ref["code"]),
                          env_same=out["env"] == ref["env"]), indent=1))
