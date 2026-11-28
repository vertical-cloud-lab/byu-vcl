"""Round 6: what the timing runs measured, put where ``python -m twin.bench6 status`` reads it (``smoke.json``).

    cd vertical-lab && python out/twin6/checks/smoke_merge.py

* **Two-year runs.** The timing runs of seed 0 of a lab's stocked arm for the full two years (``timing6.jsonl``,
  made by ``timing6.py``) are the same configurations as the grid's seed 0 of ``arms`` (at the main scale) or of
  ``hpc`` (at another), ``bench6._cfg(lab, plan, policy, "reorder", 0, hpc=scale)``; they go into ``smoke.json`` as
  those groups' measured two-year times (``full``), in CPU seconds (``bench6._secs``).
* **The stream's cost** (``stream_cost``): CPU seconds per simulated day per unit of HPC scale, by policy class
  (``fast``: the heuristic and the funnel; ``gp``: BOFN and pKGFN) and lab, from pairs of runs that differ only in
  scale (the same policy, lab and seed, the larger at least 16x), read off their cost curves at day 150, before the
  cell: the two-year runs, BOFN's pilot (1x, 4x, 16x, 64x) and the 1x runs of the other policies. The median over a
  class and lab's pairs. ``bench6.timings`` moves a run's stream cost from the scale it was measured
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


PRE_CELL_D = 150    # the earliest the cell is integrated in any seed is day 161 (checks/used_market.md)


def stream_cost(rows, prog):
    """{class: {lab: k}}, and the pairs each came from: two runs that differ only in scale (the same policy, lab and
    seed; the larger scale at least 16x), read off their cost curves (``timing6_progress.jsonl``) at day 150 or the
    last day both reached before it: (CPU at the larger scale - CPU at the smaller) over (the scale difference x the
    days). Before the cell the policies' own work is small and the same at every scale, so the difference is the
    stream's; after it, two runs' paths part and their work differs by more than the stream does."""
    curves, meta = {}, {r["label"]: r for r in rows}
    for p in prog:
        curves.setdefault(p["label"], {})[p["day"]] = p["cpu"]
    info = {lb: (meta.get(lb) or _label_meta(lb)) for lb in curves}
    pairs = {}
    for l1, c1 in curves.items():
        for l2, c2 in curves.items():
            r1, r2 = info[l1], info[l2]
            if r1 is None or r2 is None or not (r1["scale"] < r2["scale"] and r2["scale"] >= 16):
                continue
            key = lambda r: (r["policy"], r["lab"], r["seed"], r.get("plan") or ARM[r["lab"]][1],
                             r.get("stock") or "reorder")
            if key(r1) != key(r2):
                continue
            both = [d for d in set(c1) & set(c2) if 0 < d <= PRE_CELL_D]
            if not both or max(both) < 100:
                continue
            D = max(both)
            k = (c2[D] - c1[D]) / ((r2["scale"] - r1["scale"]) * D)
            pairs.setdefault((_cls(r1["policy"]), r1["lab"]), []).append(
                dict(k=round(k, 5), how=f"{r1['policy']} s{r1['seed']}: day {D} at {r1['scale']:g}x ({l1}) and "
                                         f"{r2['scale']:g}x ({l2})"))
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
