"""Round 6: what the timing runs measured, put where ``python -m twin.bench6 status`` reads it (``smoke.json``).

    cd vertical-lab && python out/twin6/checks/smoke_merge.py

* **Two-year runs.** The timing runs of seed 0 of a lab's stocked arm for the full two years (``timing6.jsonl``,
  made by ``timing6.py``) are the same configurations as the grid's seed 0 of ``arms`` (at the main scale) or of
  ``hpc`` (at another), ``bench6._cfg(lab, plan, policy, "reorder", 0, hpc=scale)``; they go into ``smoke.json`` as
  those groups' measured two-year times (``full``), in CPU seconds (``bench6._secs``).
* **The stream's cost** (``stream_cost``): CPU seconds per simulated day per unit of HPC scale, by policy class
  (``fast``: the heuristic and the funnel; ``gp``: BOFN and pKGFN) and lab, from pairs of runs that differ only in
  scale (the same policy, lab and seed), the larger scale at least 16x: (CPU at the larger scale - CPU at 1x) over
  (the scale difference x the days). Two kinds of pair, both read at the same simulated day:

  - the pilot's runs of the same length (``pilot ...`` lines of ``timing6.jsonl``: BOFN in the automated lab, 300
    days, at 1x, 4x, 16x and 64x);
  - a 300-day run at 1x (``pilot ... 1x``) against the same seed's two-year run at 16x or 64x, both read off their
    cost curves (``timing6_progress.jsonl``) at the last day both reached.

  The median over a class and lab's pairs. ``bench6.timings`` moves a run's stream cost from the scale it was measured
  at to another with it.
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


def _rows(name):
    p = HERE / name
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def _cls(policy):
    return "fast" if policy == "fast" else "gp"


def stream_cost(rows, prog):
    """{class: {lab: k}}, and the pairs each came from."""
    pairs = {}
    # pairs of runs of the same length
    by = {}
    for r in rows:
        by.setdefault((r["policy"], r["lab"], r["seed"], r["days"]), {})[r["scale"]] = r
    for (pol, lab, seed, days), d in by.items():
        if 1 not in d:
            continue
        for sc, r in d.items():
            if sc >= 16:
                k = (B6._secs(r) - B6._secs(d[1])) / ((sc - 1) * days)
                pairs.setdefault((_cls(pol), lab), []).append(
                    dict(k=round(k, 5), how=f"{pol} s{seed}: {days} days at 1x and {sc:g}x"))
    # a 1x run against a longer run's cost curve, at the last day both reached
    curves = {}
    for p in prog:
        curves.setdefault(p["label"], {})[p["day"]] = p["cpu"]
    meta = {r["label"]: r for r in rows}
    for lab1, c1 in curves.items():
        r1 = meta.get(lab1)
        if r1 is None or r1["scale"] != 1:
            continue
        for lab2, c2 in curves.items():
            r2 = meta.get(lab2) or _label_meta(lab2)
            if (r2 is None or r2["scale"] < 16 or r2["days"] <= r1["days"] or
                    (r2["policy"], r2["lab"], r2["seed"]) != (r1["policy"], r1["lab"], r1["seed"])):
                continue
            both = sorted(set(c1) & set(c2))
            if not both or both[-1] < 100:
                continue
            D = both[-1]
            k = (c2[D] - c1[D]) / ((r2["scale"] - 1) * D)
            pairs.setdefault((_cls(r1["policy"]), r1["lab"]), []).append(
                dict(k=round(k, 5), how=f"{r1['policy']} s{r1['seed']}: day {D} of the 1x run and of the "
                                         f"{r2['scale']:g}x two-year run"))
    out = {}
    for (cls, lab), v in sorted(pairs.items()):
        out.setdefault(cls, {})[lab] = round(st.median(x["k"] for x in v), 5)
    return out, {f"{c}/{l}": v for (c, l), v in sorted(pairs.items())}


def _label_meta(label):
    """A run still going has no line in timing6.jsonl: its configuration from its label ("<lab> <policy> <scale>x")."""
    from importlib.util import module_from_spec, spec_from_file_location
    spec = spec_from_file_location("timing6", HERE / "timing6.py")
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    for jobs in m.SETS.values():
        for j in jobs:
            if j[0] == label:
                lb, lab, pol, seed, sc, days = j[:6]
                out = dict(label=lb, lab=lab, policy=pol, seed=seed, scale=sc, days=days)
                if len(j) > 6:
                    out.update(plan=j[6], stock=j[7])
                return out
    return None


def main():
    p = HERE / "smoke.json"
    rec = json.loads(p.read_text()) if p.exists() else dict(groups={})
    rows = _rows("timing6.jsonl")
    prog = _rows("timing6_progress.jsonl")
    n = 0
    for r in rows:
        if r["days"] < B6.DAYS or r["seed"] != 0:
            continue
        lab, plan = ARM[r["lab"]]
        plan, stock = r.get("plan", plan), r.get("stock", "reorder")
        g = B6.group_key(B6._cfg(r["lab"], plan, r["policy"], stock, 0, hpc=dict(scale=r["scale"])))
        name = next((n for n, cs in B6.EXPERIMENTS.items() for c in cs if c["seed"] == 0 and B6.group_key(c) == g),
                    None)
        e = rec["groups"].setdefault(g, dict(experiment=name))
        e["full"] = dict(seconds=r["seconds"], cpu_seconds=r["cpu_seconds"], loadavg_end=r["timing"]["loadavg_end"],
                         days=r["days"], scale=r["scale"], gp_fits=r.get("gp_fits"), cpu=r.get("cpu"),
                         commit=(r.get("code") or {}).get("commit"), twin_dirty=(r.get("code") or {}).get("twin_dirty"),
                         source="checks/timing6.jsonl",
                         targets={k: dict(T1=v["T1_day"], T2=v["T2_day"]) for k, v in r["campaigns"].items()},
                         best_new={k: v["best_new"] for k, v in r["campaigns"].items()})
        n += 1
        print(g, r["cpu_seconds"], "CPU s")
    # two-year runs stopped before day 730 (``timing6.py``'s ``gp_auto`` and ``other`` sets): their two years
    # extrapolated from the cost curve, the cautious end (``timing6.extrapolate`` ``high``), marked as such
    from importlib.util import module_from_spec, spec_from_file_location
    spec = spec_from_file_location("timing6", HERE / "timing6.py")
    T6 = module_from_spec(spec)
    spec.loader.exec_module(T6)
    done = {r["label"] for r in rows}
    curves = {}
    for q in prog:
        curves.setdefault(q["label"], []).append(q)
    for lb, ps in curves.items():
        meta = _label_meta(lb)
        if lb in done or meta is None or meta["days"] < B6.DAYS or meta["seed"] != 0:
            continue
        x = T6.extrapolate(ps)
        if x is None or x["day"] < 300:
            continue
        lab, plan = ARM[meta["lab"]]
        plan, stock = meta.get("plan", plan), meta.get("stock", "reorder")
        g = B6.group_key(B6._cfg(meta["lab"], plan, meta["policy"], stock, 0, hpc=dict(scale=meta["scale"])))
        name = next((n for n, cs in B6.EXPERIMENTS.items() for c in cs if c["seed"] == 0 and B6.group_key(c) == g),
                    None)
        e = rec["groups"].setdefault(g, dict(experiment=name))
        e["full"] = dict(seconds=None, cpu_seconds=x["high"], days=B6.DAYS, scale=meta["scale"],
                         source="checks/timing6_progress.jsonl",
                         extrapolated=dict(from_day=x["day"], cpu_at_day=x["cpu"], rate=x["rate"], slope=x["slope"],
                                           low=x["low"], high=x["high"]),
                         how=f"extrapolated from day {x['day']} of a two-year run (seed 0): the cautious end, "
                             f"{x['low']:,}-{x['high']:,} s")
        n += 1
        print(g, "extrapolated from day", x["day"], x["low"], "-", x["high"], "CPU s")
    k, pairs = stream_cost(rows, prog)
    rec["stream_cost"] = k
    rec["stream_cost_pairs"] = pairs
    rec["stream_cost_note"] = ("CPU seconds per simulated day per unit of HPC scale, the median over pairs of runs that "
                               "differ only in scale (the larger at least 16x), from checks/timing6.jsonl and "
                               "timing6_progress.jsonl (out/twin6/checks/smoke_merge.py)")
    rec["groups"] = dict(sorted(rec["groups"].items()))
    p.write_text(json.dumps(rec, indent=1) + "\n")
    print(n, "two-year runs merged into", p.name, "; stream cost", k)


if __name__ == "__main__":
    main()
