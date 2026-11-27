"""Round 6: what the grid costs, by lab and policy class, at both ends of the extrapolated two-year runs.

    cd vertical-lab && python out/twin6/checks/grid_hours.py        # writes grid_hours.md beside this file

Reads ``smoke.json`` as ``python -m twin.bench6 status`` does (``bench6.timings``). A two-year run that didn't reach
day 730 in the job that timed it carries its extrapolation (``full.extrapolated``: ``low`` at its latest rate, ``high``
with that rate still rising); ````status`` plans with ``high``; this script prices the grid both ways.
"""
import copy
import json
import os
import sys
from pathlib import Path

VL = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(VL))
os.environ.setdefault("TWIN_PIN", "portable")
from twin import bench6 as B6  # noqa: E402

HERE = Path(__file__).resolve().parent


def totals(rec):
    tm = B6.timings(rec["groups"], B6.stream_cost(rec))
    out = {}
    for name, cfgs in B6.EXPERIMENTS.items():
        for c in cfgs:
            key = (c["lab"], "BOFN and pKGFN" if c["policy"] != "fast" else "heuristic and funnel")
            t = tm.get(B6.group_key(c))
            o = out.setdefault(key, dict(runs=0, sec=0.0, unknown=0, longest=0.0))
            o["runs"] += 1
            if t is None:
                o["unknown"] += 1
            else:
                o["sec"] += t["seconds_2y"]
                o["longest"] = max(o["longest"], t["seconds_2y"])
    return out


def main():
    rec = json.loads((HERE / "smoke.json").read_text())
    low = copy.deepcopy(rec)
    ext = []
    for g, e in low["groups"].items():
        x = (e.get("full") or {}).get("extrapolated")
        if x:
            e["full"]["cpu_seconds"] = x["low"]
            ext.append((g, x))
    hi, lo = totals(rec), totals(low)
    L = ["# Round 6: what the grid costs", "",
         "Made by `python out/twin6/checks/grid_hours.py` from `smoke.json`. CPU-hours of two-year runs on the runner "
         "that timed them (an AMD EPYC 9V45, every vCPU busy, as in a slice); a runner runs four at a time. "
         "**High** prices each extrapolated run with its cost a day still rising as it was (what `status` and `slices` "
         "use), **low** with its latest cost a day held. The cost a day has risen in every stretch measured so far, and "
         "copper's GP nodes were still filling at day ~400 (checks/profile/profile.md), so low is more likely to be "
         "short than high is to be long. Everything is simulated.", "",
         "| Lab | Policies | Runs | CPU-hours a run, low-high (mean) | Longest run, high (h) | Core-hours, low | "
         "Core-hours, high |", "|---|---|---|---|---|---|---|"]
    S = dict(runs=0, lo=0.0, hi=0.0)
    for key in sorted(hi):
        h, l = hi[key], lo[key]
        n = h["runs"] - h["unknown"]
        L.append(f"| {'automated' if key[0] == 'vertical' else 'conventional'} | {key[1]} | {h['runs']} | "
                 f"{l['sec'] / max(n, 1) / 3600:.1f}-{h['sec'] / max(n, 1) / 3600:.1f} | {h['longest'] / 3600:.1f} | "
                 f"{l['sec'] / 3600:,.0f} | {h['sec'] / 3600:,.0f} |")
        S["runs"] += h["runs"]
        S["lo"] += l["sec"] / 3600
        S["hi"] += h["sec"] / 3600
    L.append(f"| all | | {S['runs']:,} | | | {S['lo']:,.0f} | {S['hi']:,.0f} |")
    L += ["", f"**Runner-hours at four runs a runner: {S['lo'] / 4:,.0f} (low) to {S['hi'] / 4:,.0f} (high).**",
          "", "Extrapolated two-year runs:", ""]
    for g, x in ext:
        L.append(f"* `{g}`: day {x['from_day']} reached at {x['cpu_at_day']:,.0f} CPU s, {x['rate']} CPU s a day "
                 f"over the last 50 days, rising {x['slope']} a day: two years {x['low']:,}-{x['high']:,} CPU s "
                 f"({x['low'] / 3600:.1f}-{x['high'] / 3600:.1f} h)")
    (HERE / "grid_hours.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
