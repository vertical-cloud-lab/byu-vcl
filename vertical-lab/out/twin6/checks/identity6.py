"""Round 6: is a run on one engine byte for byte the same run on another, and how long does each take?

    cd <a checkout's vertical-lab> && TWIN_PIN=portable PYTHONHASHSEED=0 TWIN6_OUT=/tmp/... \
        python <this file> LAB POLICY SCALE DAYS [SEED]        # one JSON line: hashes, CPU seconds, the engine

Runs ``bench6.simulate`` on the engine of the checkout it is started from (the current directory's ``twin/``) and
hashes the row (apart from timing and provenance), the event log and the GP state the way ``twin/gpcheck6.py`` does.
Run it from two checkouts (or worktrees) with the same arguments and compare: the same three hashes mean the same
run; the CPU seconds compare the engines' speed on identical work. Appends its line to ``identity6.jsonl`` beside it.
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import twin  # noqa: E402,F401  (the pin)
from twin import bench2 as B2  # noqa: E402
from twin import bench6 as B6  # noqa: E402
from twin import gpcheck6 as G  # noqa: E402

ARM = {"vertical": ("parallel", "reorder"), "conventional": ("external", "reorder")}

if __name__ == "__main__":
    lab, pol, scale, days = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    os.environ["TWIN6_DAYS"] = str(days)
    cfg = B6._cfg(lab, ARM[lab][0], pol, ARM[lab][1], seed, hpc=dict(scale=scale))
    c0 = time.process_time()
    out, tw = B6.simulate(cfg)
    cpu = round(time.process_time() - c0, 1)
    row = json.loads(json.dumps(B2._jsonable(out)))
    log = json.loads(json.dumps(B2._jsonable(B6.event_log(tw, cfg))))
    rec = dict(run_id=B6.run_id(cfg), days=days, row=G._sha({k: v for k, v in row.items() if k not in G.NOT_IN_ROW}),
               log=G._sha(log), gp=G._sha(G.gp_state(tw)), cpu_seconds=cpu, sim_cpu_seconds=out["timing"]["cpu_seconds"],
               loadavg_end=out["timing"]["loadavg_end"], gp_fits=row.get("gp", {}).get("fits"),
               engine=dict(commit=(out["code"].get("commit") or "")[:7], twin_tree=(out["code"].get("twin_tree") or "")[:7],
                           twin_dirty=out["code"].get("twin_dirty")), cpu=out["env"]["cpu"])
    line = json.dumps(rec)
    with (Path(__file__).resolve().parent / "identity6.jsonl").open("a") as fh:
        fh.write(line + "\n")
    print(line)
