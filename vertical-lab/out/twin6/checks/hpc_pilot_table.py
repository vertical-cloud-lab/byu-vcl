"""Summarize the HPC pilot: by policy, lab and scale, the seeds that reach each target and their median day (a seed
that doesn't reach it counts as later than the horizon), the best new alloy, and the CPU seconds a run took.

    python out/twin6/checks/hpc_pilot_table.py            # prints markdown; writes hpc_pilot.json and hpc_pilot.md

Reads ``hpc_pilot.jsonl`` (the first job's pilot driver, never committed) if it is there, and the pilot lines of
``timing6.jsonl`` (the second job's: BOFN in the automated lab, 300 days, and the 1x runs of the other policies).
Seconds are CPU seconds where a line has them.
"""
import json
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = []
for name in ("hpc_pilot.jsonl", "timing6.jsonl"):
    p = HERE / name
    if p.exists():
        for l in p.read_text().splitlines():
            if l.strip():
                r = json.loads(l)
                if name == "timing6.jsonl" and not r.get("label", "").startswith("pilot"):
                    continue
                r["seconds"] = r.get("cpu_seconds") or r["seconds"]
                rows.append(r)
G = {}
for r in rows:
    G.setdefault((r["policy"], r["days"], r["lab"], r["scale"]), []).append(r)
out, L = [], []
for (pol, days, lab, sc), rs in sorted(G.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2], kv[0][3])):
    rec = dict(policy=pol, days=days, lab=lab, scale=sc, seeds=sorted(r["seed"] for r in rs),
               seconds_median=round(st.median(r["seconds"] for r in rs), 1), campaigns={})
    for k in ("flaime_al", "onr_cu"):
        c = {}
        for tn in ("T1_day", "T2_day"):
            v = [r["campaigns"][k][tn] for r in rs]
            hit = [x for x in v if x is not None]
            med = st.median([x if x is not None else float('inf') for x in v])
            c[tn] = dict(reached=len(hit), of=len(v), median_day=None if med == float('inf') else round(med, 1))
        c["best_new_median"] = round(st.median(r["campaigns"][k]["best_new"] for r in rs), 4)
        c["tested_median"] = st.median(r["campaigns"][k]["tested"] for r in rs)
        c["visible_median"] = st.median(r["campaigns"][k]["visible"] for r in rs)
        rec["campaigns"][k] = c
    out.append(rec)
(HERE / "hpc_pilot.json").write_text(json.dumps(out, indent=1) + "\n")


def cell(c):
    return f"{c['median_day'] if c['median_day'] is not None else '-'} ({c['reached']}/{c['of']})"


base = {(r["policy"], r["days"], r["lab"]): r for r in out if r["scale"] == 1}
L = ["| Policy | Days | Lab | Scale | Seeds | Al T1 | Al T2 | Al best | Al tested | Cu T1 | Cu T2 | Cu best | Cu tested | "
     "CPU s per run | extra CPU s a day |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in out:
    a, c = r["campaigns"]["flaime_al"], r["campaigns"]["onr_cu"]
    b = base.get((r["policy"], r["days"], r["lab"]))
    extra = "" if b is None or r["scale"] == 1 else f"{(r['seconds_median'] - b['seconds_median']) / r['days']:.2f}"
    L.append(f"| {r['policy']} | {r['days']} | {r['lab']} | {r['scale']}x | {len(r['seeds'])} | {cell(a['T1_day'])} | "
             f"{cell(a['T2_day'])} | {a['best_new_median']} | {a['tested_median']} | {cell(c['T1_day'])} | "
             f"{cell(c['T2_day'])} | {c['best_new_median']} | {c['tested_median']} | {r['seconds_median']} | {extra} |")
L += ["", "Medians over the seeds; a target's cell is the median day (a seed that doesn't reach it counts as later than "
          "the horizon) and the seeds that reached it. 'extra s a day': the run's seconds over the same policy's and "
          "lab's at 1x, per simulated day (CPU seconds). Seeds are paired across scales (the same truths, build-outs and draws), "
          "but a run's path parts as soon as one decision differs, so with a few seeds only large changes show."]
txt = "\n".join(L)
(HERE / "hpc_pilot.md").write_text("# HPC pilot (round 6)\n\nMade by `python out/twin6/checks/hpc_pilot_table.py` "
                                    "from `hpc_pilot.jsonl`. Everything is simulated.\n\n" + txt + "\n")
print(txt)
