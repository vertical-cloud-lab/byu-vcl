"""Round 6: what the HPC pilot measured, put where ``python -m twin.bench6 status`` reads it (``smoke.json``).

    cd vertical-lab && python out/twin6/checks/smoke_merge.py

* **Two-year runs.** The pilot's runs of seed 0 of a lab's stocked arm for the full two years are the same
  configurations as the grid's seed 0 of ``arms`` (``bench6._cfg(lab, plan, policy, "reorder", 0)``, at the scale
  each was run at); they go into ``smoke.json`` as those groups' measured two-year times (``full``). The pilot only
  made them with its own driver, so that the long runs could start while the shortened ones waited for cores.
* **The stream's cost** (``stream_cost``): seconds of runtime per simulated day per unit of HPC scale, by policy
  class (``fast``: the heuristic and the funnel; ``gp``: BOFN and pKGFN) and lab. For each pair of the pilot's runs
  that differ only in scale (the same policy, lab, seed and days), the extra seconds over the extra scale-days; the
  median over the pairs whose larger scale is at least 16x. ``bench6.timings`` moves a run's stream cost from the
  scale it was measured at to another with it.
"""
import json
import os
import statistics as st
import sys
from pathlib import Path

VL = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(VL))
os.environ.setdefault("TWIN_PIN", "portable")
from twin import bench6 as B6  # noqa: E402

HERE = Path(__file__).resolve().parent
ARM = {"vertical": ("vertical", "parallel"), "conventional": ("conventional", "external")}


def stream_cost(rows):
    by = {}
    for r in rows:
        by.setdefault((r["policy"], r["lab"], r["seed"], r["days"]), {})[r["scale"]] = r["seconds"]
    k = {}
    for (pol, lab, seed, days), d in by.items():
        if 1 not in d:
            continue
        for sc, secs in d.items():
            if sc >= 16:
                k.setdefault(("fast" if pol == "fast" else "gp", lab), []).append((secs - d[1]) / ((sc - 1) * days))
    out = {}
    for (cls, lab), v in sorted(k.items()):
        out.setdefault(cls, {})[lab] = round(st.median(v), 5)
    return out, {f"{c}/{l}": len(v) for (c, l), v in k.items()}


def main():
    p = HERE / "smoke.json"
    rec = json.loads(p.read_text()) if p.exists() else dict(groups={})
    rows = [json.loads(l) for l in (HERE / "hpc_pilot.jsonl").read_text().splitlines() if l.strip()]
    n = 0
    for r in rows:
        if r["days"] < B6.DAYS or r["seed"] != 0:
            continue
        lab, plan = ARM[r["lab"]]
        g = B6.group_key(B6._cfg(lab, plan, r["policy"], "reorder", 0, hpc=dict(scale=r["scale"])))
        e = rec["groups"].setdefault(g, dict(experiment="arms" if r["scale"] == B6.HPC_SCALE else "hpc"))
        e["full"] = dict(seconds=r["seconds"], days=r["days"], scale=r["scale"], gp_fits=r.get("gp_fits"),
                         cpu=r.get("cpu"), commit=(r.get("code") or {}).get("commit"),
                         twin_dirty=(r.get("code") or {}).get("twin_dirty"), source="checks/hpc_pilot.jsonl",
                         targets={k: dict(T1=v["T1_day"], T2=v["T2_day"]) for k, v in r["campaigns"].items()},
                         best_new={k: v["best_new"] for k, v in r["campaigns"].items()})
        n += 1
        print(g, r["seconds"], "s")
    k, npairs = stream_cost(rows)
    rec["stream_cost"] = k
    rec["stream_cost_note"] = ("seconds of runtime per simulated day per unit of HPC scale, the median over the HPC "
                               "pilot's pairs of runs that differ only in scale (larger scale at least 16x); pairs: "
                               + json.dumps(npairs))
    rec["groups"] = dict(sorted(rec["groups"].items()))
    p.write_text(json.dumps(rec, indent=1) + "\n")
    print(n, "two-year runs merged into", p.name, "; stream cost", k)


if __name__ == "__main__":
    main()
