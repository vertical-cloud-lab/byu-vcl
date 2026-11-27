"""Summarize hpc_pilot.jsonl: by policy, lab and scale, the seeds that reach each target and their median day (a seed
that doesn't reach it counts as later than the horizon), the best new alloy, and the seconds a run took.

    python out/twin6/checks/hpc_pilot_table.py            # prints markdown; writes hpc_pilot.json
"""
import json
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = [json.loads(l) for l in (HERE / "hpc_pilot.jsonl").read_text().splitlines() if l.strip()]
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


print("| Policy | Days | Lab | Scale | Seeds | Al T1 | Al T2 | Al best | Cu T1 | Cu T2 | Cu best | s per run |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in out:
    a, c = r["campaigns"]["flaime_al"], r["campaigns"]["onr_cu"]
    print(f"| {r['policy']} | {r['days']} | {r['lab']} | {r['scale']}x | {len(r['seeds'])} | {cell(a['T1_day'])} | "
          f"{cell(a['T2_day'])} | {a['best_new_median']} | {cell(c['T1_day'])} | {cell(c['T2_day'])} | "
          f"{c['best_new_median']} | {r['seconds_median']} |")
