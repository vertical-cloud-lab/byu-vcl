"""Round 6, item 6 (a check, not rows of the grid): do copper's stretches with free capacity and nothing started,
which round 5 found with BOFN and pKGFN, go away without the optimizers' cap on blend screens?

    cd vertical-lab && TWIN_PIN=<pin> PYTHONHASHSEED=0 TWIN6_OUT=/tmp/twin6idle \
        python out/twin6/checks/copper_idle.py > /dev/null      # appends to copper_idle.jsonl beside this file

Reruns, on round 6's engine, arms and seeds in which round 5 flagged a copper stretch (out/twin5/runs/net*.jsonl.xz),
for the days that cover the flagged stretches, and records copper's stretches by round 6's rule (the policy waiting
while the campaign could have started a job: twin/round6.py ``idle_report6``), with what the policy did in them and
why it offered no new design when it didn't (twin/opt/net6.py's counters).
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

VL = Path.cwd()
sys.path.insert(0, str(VL))
assert os.environ.get("TWIN_PIN") and os.environ.get("PYTHONHASHSEED") == "0"
assert os.environ.get("TWIN6_OUT", "").startswith("/tmp/")
from twin import bench5 as B5                      # noqa: E402
from twin import bench6 as B6                      # noqa: E402

OUT = Path(__file__).resolve().parent / "copper_idle.jsonl"
# (lab, plan, policy, stock, seed, days): round 5 flagged copper's first fabrication step in each of these
CASES = [("conventional", "external", "bofn3", "lean", s, 260) for s in (0, 4, 6, 7)] + \
        [("conventional", "external", "bofn3", "reorder", s, 260) for s in (0, 2, 4, 5)] + \
        [("conventional", "external", "pkgfn3", "reorder", s, 260) for s in (0, 2)] + \
        [("vertical", "parallel", "bofn3", "reorder", s, 170) for s in (0, 1, 7)] + \
        [("vertical", "parallel", "pkgfn3", "reorder", s, 170) for s in (0, 1)]


def round5_flags():
    out = {}
    for r in B5.load("net") + B5.load("net_more"):
        c = r["cfg"]
        key = (c["lab"], c["plan"], c["policy"], c["stock"], c["seed"])
        out[key] = {g: [(x["start_d"], x["days"]) for x in v if x["flag"]]
                    for g, v in r["r5"]["idle"]["stretches"]["onr_cu"].items()}
    return out


def one(case):
    lab, plan, pol, stock, seed, days = case
    os.environ["TWIN6_DAYS"] = str(days)
    cfg = B6._cfg(lab, plan, pol, stock, seed)
    out, tw = B6.simulate(cfg)
    st = out["r6"]["idle"]["stretches"]["onr_cu"]
    keep = ("start_d", "days", "cause", "could_start", "flag", "days_asked", "days_nothing_proposed", "pending_median")
    return dict(run=B6.run_id(cfg), days=days, seconds=out["seconds"], code=out["code"], pin=out["env"]["pin"],
                stretches={g: [{k: x[k] for k in keep} for x in v if x["days"] >= 14] for g, v in st.items()},
                flagged={g: [(x["start_d"], x["days"]) for x in v if x["flag"]] for g, v in st.items()},
                policy_counts=out["campaigns"]["onr_cu"]["policy_counts"], status=out["campaigns"]["onr_cu"]["status"],
                counters=out["r6"]["counters"]["onr_cu"],
                blend_screens=sum(1 for D in tw.campaigns["onr_cu"].deposits.values() if D["mode"] == "blend"))


if __name__ == "__main__":
    r5 = round5_flags()
    done = {json.loads(l)["run"] for l in OUT.read_text().splitlines()} if OUT.exists() else set()
    todo = [c for c in CASES if B6.run_id(B6._cfg(*c[:5])) not in done]
    with ProcessPoolExecutor(int(os.environ.get("TWIN_WORKERS", "1")), max_tasks_per_child=1) as ex:
        futs = {ex.submit(one, c): c for c in todo}
        for f in as_completed(futs):
            c = futs[f]
            r = f.result()
            r["round5_flagged"] = {g: [x for x in v if x[0] < c[5]] for g, v in r5.get(tuple(c[:5]), {}).items()}
            with OUT.open("a") as fh:
                fh.write(json.dumps(B6.B2._jsonable(r)) + "\n")
            print(r["run"], r["seconds"], "s; round 5 flagged", r["round5_flagged"], "; round 6 flags", r["flagged"],
                  file=sys.stderr, flush=True)
