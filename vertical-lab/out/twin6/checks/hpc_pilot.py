"""Round 6, a pilot for the HPC stream's scale (not rows of the grid): where do outcomes stop changing?

    cd vertical-lab && TWIN_PIN=<pin> PYTHONHASHSEED=0 TWIN6_OUT=/tmp/twin6pilot \
        python out/twin6/checks/hpc_pilot.py POLICY DAYS SEEDS SCALE [SCALE ...] [--labs vertical,conventional]

Runs the stocked arm of each lab named, for DAYS simulated days, seeds 0..SEEDS-1, at each scale (the simulated
candidates the policies see, as a multiple of round 5's 64 new a day and 128 kept), and appends one line per run to
``hpc_pilot.jsonl`` beside this file: the day each target is reached, the best new alloy, the alloys tested, the
candidates made visible, and the run's seconds. Nothing is written to out/twin6/runs.
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
from twin import bench6 as B6                      # noqa: E402  (the twin package applies the pin first)

OUT = Path(__file__).resolve().parent / "hpc_pilot.jsonl"
ARM = {"vertical": ("vertical", "parallel", "reorder"), "conventional": ("conventional", "external", "reorder")}


def one(args):
    lab, policy, seed, scale, days = args
    from twin import bench2 as B2
    os.environ["TWIN6_DAYS"] = str(days)
    cfg = B6._cfg(*ARM[lab][:2], policy, ARM[lab][2], seed, hpc=dict(scale=scale))
    out, tw = B6.simulate(cfg)
    T = B2.targets()
    rec = dict(lab=lab, policy=policy, seed=seed, scale=scale, days=days, seconds=out["seconds"],
               gp_fits=out["gp"]["fits"], code=out["code"], cpu=out["env"]["cpu"], pin=out["env"]["pin"], campaigns={})
    for k, c in out["campaigns"].items():
        hit = {tn: (lambda h: None if h is None else h[0])(B2.hit(c["curve_new"], T[tn][k], 2)) for tn in ("T1", "T2")}
        rec["campaigns"][k] = dict(T1_day=hit["T1"], T2_day=hit["T2"], best_new=round(c["best_new"], 4),
                                   tested=c["n_new_alloys"], spent=c["spent"],
                                   visible=out["r6"]["hpc"]["campaigns"][k]["materialized"],
                                   prescreened=c["policy_counts"].get("prescreened"))
    return rec


if __name__ == "__main__":
    a = sys.argv[1:]
    labs = ("vertical", "conventional")
    if "--labs" in a:
        i = a.index("--labs")
        labs = tuple(a[i + 1].split(","))
        a = a[:i] + a[i + 2:]
    policy, days, seeds = a[0], int(a[1]), int(a[2])
    scales = [float(x) if "." in x else int(x) for x in a[3:]]
    done = set()
    if OUT.exists():
        for l in OUT.read_text().splitlines():
            r = json.loads(l)
            done.add((r["lab"], r["policy"], r["seed"], r["scale"], r["days"]))
    todo = [(lab, policy, s, sc, days) for sc in scales for s in range(seeds) for lab in labs
            if (lab, policy, s, sc, days) not in done]
    print(len(todo), "runs", flush=True)
    with ProcessPoolExecutor(int(os.environ.get("TWIN_WORKERS", "2")), max_tasks_per_child=1) as ex:
        futs = {ex.submit(one, t): t for t in todo}
        for f in as_completed(futs):
            r = f.result()
            with OUT.open("a") as fh:
                fh.write(json.dumps(r) + "\n")
            print(r["lab"], r["policy"], "seed", r["seed"], "scale", r["scale"], r["seconds"], "s",
                  {k: (v["T1_day"], v["T2_day"]) for k, v in r["campaigns"].items()}, flush=True)
