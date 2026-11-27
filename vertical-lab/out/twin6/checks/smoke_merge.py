"""Round 6: put the two-year runs of the HPC pilot (``hpc_pilot.jsonl``: seed 0 of a lab's stocked arm at the grid's
main scale, run for the full two years) into ``smoke.json`` as those arms' measured two-year times, beside the
shortened smoke runs that ``python -m twin.bench6 smoke`` writes. Then ``python -m twin.bench6 status``.

    cd vertical-lab && python out/twin6/checks/smoke_merge.py

The pilot's runs are the same configurations as the grid's seed 0 of ``arms`` (``bench6._cfg(lab, plan, policy,
"reorder", 0)`` at ``bench6.HPC_SCALE``); the pilot only made them with its own driver, so that the two-year runs could
start while the shortened ones waited for cores.
"""
import json
import os
import sys
from pathlib import Path

VL = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(VL))
os.environ.setdefault("TWIN_PIN", "portable")
from twin import bench6 as B6  # noqa: E402

HERE = Path(__file__).resolve().parent
ARM = {"vertical": ("vertical", "parallel"), "conventional": ("conventional", "external")}


def main():
    p = HERE / "smoke.json"
    rec = json.loads(p.read_text()) if p.exists() else dict(groups={})
    n = 0
    for line in (HERE / "hpc_pilot.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["days"] < B6.DAYS or r["seed"] != 0 or r["scale"] != B6.HPC_SCALE:
            continue
        lab, plan = ARM[r["lab"]]
        g = B6.group_key(B6._cfg(lab, plan, r["policy"], "reorder", 0))
        e = rec["groups"].setdefault(g, dict(experiment="arms"))
        e["full"] = dict(seconds=r["seconds"], days=r["days"], gp_fits=r.get("gp_fits"), cpu=r.get("cpu"),
                         concurrent=r.get("concurrent"), commit=(r.get("code") or {}).get("commit"),
                         twin_dirty=(r.get("code") or {}).get("twin_dirty"), source="checks/hpc_pilot.jsonl",
                         targets={k: dict(T1=v["T1_day"], T2=v["T2_day"]) for k, v in r["campaigns"].items()},
                         best_new={k: v["best_new"] for k, v in r["campaigns"].items()})
        n += 1
        print(g, r["seconds"], "s")
    rec["groups"] = dict(sorted(rec["groups"].items()))
    p.write_text(json.dumps(rec, indent=1) + "\n")
    print(n, "two-year runs merged into", p.name)


if __name__ == "__main__":
    main()
