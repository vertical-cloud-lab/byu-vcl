"""Round 6, batched GP predictions: the measured saving put into the seconds the grid plans with (``smoke.json``),
and this runner's speed against the one round 6 was timed on.

    cd vertical-lab && python out/twin6/checks/batch_merge.py          # writes smoke.json and batch.md beside this

* **The saving** (``timing6b_ab.jsonl``, made by ``timing6b.py ab``): the same saved state of the automated lab's BOFN
  or pKGFN (seed 0, 64x, day D of a two-year run) carried on for the same simulated days with 64-point GP calls and
  without, in two fresh processes side by side. Its ratio, ``r``, is CPU seconds with over CPU seconds without.
* **What it changes**: the automated lab's BOFN and pKGFN two-year runs are priced by extrapolating round 6's timing
  runs, made on the engine before the batching (``timing6.md``; ``smoke.json`` records them as ``extrapolated``).
  Their seconds before the cell (day 200 of the timing run's curve, where the GP calls are few and small) are kept and
  the rest is multiplied by 0.92 (the faster trial settings of 74254fe, on which the A/B ran) and by the policy's ``r``
  at the latest day measured: ``new = pre + (old - pre) x 0.92 x r``, for the low and high ends alike. The conventional lab's BOFN and pKGFN keep their measured two-year seconds (small nodes and a
  small share of GP work: the saving there is smaller and wasn't measured), so they are, if anything, high.
* **This runner's speed** (``speed``): the same code on this runner and on the EPYC 9V45 that timed round 6, every vCPU
  busy on both: the unbatched timing runs (``timing6b_progress.jsonl``, the engine before the batching) and the
  heuristic and funnel (``timing6b_calib.jsonl``, no GP at all) against the same runs' curves in
  ``timing6_progress.jsonl``, read at the same simulated days.
"""
import json
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
AB = HERE / "timing6b_ab.jsonl"
OLD = HERE / "timing6_progress.jsonl"
NEW = HERE / "timing6b_progress.jsonl"
CAL = HERE / "timing6b_calib.jsonl"
SMOKE = HERE / "smoke.json"
PRE_D = 200
# the engine at 74254fe (the atomize search's trial settings 28x faster, byte for byte) took 0.92 of the timing runs'
# engine's time late in a run (grid_hours.py ``NEW_ENGINE``, notes section 10); the A/B measures the batching on
# that engine, so the two compound
TRIALS = 0.92
GROUPS = {"r6_vertical_parallel_bofn3_reorder": ("bofn3", "vertical bofn3 64x"),
          "r6_vertical_parallel_pkgfn3_reorder": ("pkgfn3", "vertical pkgfn3 64x"),
          "r6_vertical_parallel_bofn3_reorder_hpc16": ("bofn3", "vertical bofn3 16x"),
          "r6_vertical_parallel_pkgfn3_reorder_hpc16": ("pkgfn3", "vertical pkgfn3 16x")}


def _lines(p):
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def ratios():
    """{policy: [(from_day, days, cpu with, cpu without, r)]}, from the A/B lines (pairs by label and day)."""
    by = {}
    for r in _lines(AB):
        by.setdefault((r["label"], r["from_day"], r["days"]), {})[str(r["chunk"])] = r
    out = {}
    for (label, d, n), v in sorted(by.items(), key=lambda kv: kv[0][1]):
        if "64" in v and "None" in v:
            pol = "pkgfn3" if "pkgfn3" in label else "bofn3"
            a, b = v["64"]["cpu_seconds"], v["None"]["cpu_seconds"]
            out.setdefault(pol, []).append(dict(from_day=d, days=n, cpu_batched=a, cpu_unbatched=b,
                                                ratio=round(a / b, 4)))
    return out


def curves(p):
    c = {}
    for x in _lines(p):
        c.setdefault(x["label"], {})[x["day"]] = x["cpu"]
    return c


def speed():
    """This runner's CPU seconds over the 9V45's for the same code and the same simulated days (every 50 days to
    the last both reached), by pair of runs."""
    old, new = curves(OLD), curves(NEW)
    new.update(curves(CAL))
    pairs = {"vertical bofn3 64x unbatched": "vertical bofn3 64x", "vertical pkgfn3 64x unbatched": "vertical pkgfn3 64x",
             "vertical fast 64x calib": "vertical fast 64x"}
    out = {}
    for a, b in pairs.items():
        if a not in new or b not in old:
            continue
        days = [d for d in sorted(set(new[a]) & set(old[b])) if d and d % 50 == 0]
        out[a] = {d: round(new[a][d] / old[b][d], 3) for d in days}
    return out


def main():
    rs = ratios()
    sp = speed()
    rec = json.loads(SMOKE.read_text())
    old_curve = curves(OLD)
    L = ["# Round 6: batched GP predictions, what they save, and this runner's speed", "",
         "Made by `python out/twin6/checks/batch_merge.py` from `timing6b_ab.jsonl`, `timing6b_progress.jsonl`, "
         "`timing6b_calib.jsonl` and round 6's timing runs (`timing6_progress.jsonl`). Everything is simulated.", "",
         "**The saving on identical work** (the same saved state carried on with 64-point GP calls and without, side "
         "by side on this runner):", "",
         "| Policy | From day | Days | CPU s, 64-point calls | CPU s, one call | Ratio |", "|---|---|---|---|---|---|"]
    for pol, xs in sorted(rs.items()):
        for x in xs:
            L.append(f"| {pol} | {x['from_day']} | {x['days']} | {x['cpu_batched']:,.0f} | {x['cpu_unbatched']:,.0f} | "
                     f"{x['ratio']:.3f} |")
    use = {pol: xs[-1]["ratio"] for pol, xs in rs.items() if xs}
    L += ["", "**The grid's seconds** (`smoke.json`, two-year CPU seconds on the 9V45, which `status` and `plan` "
              "read): `new = pre + (old - pre) x 0.92 x r`: `old` the extrapolation of round 6's timing run on the "
              "engine it used (568ab5f), `pre` its CPU seconds at day 200, 0.92 the faster trial settings (74254fe, "
              "notes section 10), `r` the batching's ratio for the policy at the latest day measured.", "",
          "| Group | r | The timing runs' engine (568ab5f), low-high | Batched, low-high |", "|---|---|---|---|"]
    for g, (pol, label) in GROUPS.items():
        f = (rec["groups"].get(g) or {}).get("full")
        if not f or "extrapolated" not in f or pol not in use:
            continue
        ex = f.get("unbatched") or dict(low=f["extrapolated"]["low"], high=f["extrapolated"]["high"],
                                        cpu_seconds=f["cpu_seconds"], how=f["how"])
        pre = old_curve.get(label, {}).get(PRE_D, 0.0)
        r = use[pol]
        lo, hi = (round(pre + (ex[k] - pre) * TRIALS * r) for k in ("low", "high"))
        f["unbatched"] = ex
        f["batched"] = dict(ratio=r, trials=TRIALS, pre_cell_cpu=pre, low=lo, high=hi,
                            source="checks/timing6b_ab.jsonl")
        f["cpu_seconds"] = hi
        f["how"] = (f"{ex['how'].split(':')[0]} on the timing runs' engine, x {TRIALS} (the faster trial settings) "
                    f"x {r:.3f} (64-point GP calls, measured) after day {PRE_D} (checks/batch.md): {lo:,}-{hi:,} s")
        L.append(f"| `{g}` | {r:.3f} | {ex['low']:,}-{ex['high']:,} | {lo:,}-{hi:,} |")
    SMOKE.write_text(json.dumps(rec, indent=1) + "\n")
    L += ["", "**This runner's speed against the 9V45** (CPU seconds here over CPU seconds there for the same code and "
              "simulated days, every vCPU busy on both; above 1 is slower):", "",
          "| Runs | " + " | ".join(f"day {d}" for d in range(50, 751, 50)) + " |", "|---|" + "---|" * 15]
    allr = []
    for a, by in sp.items():
        L.append(f"| {a} | " + " | ".join(f"{by[d]:.2f}" if d in by else "" for d in range(50, 751, 50)) + " |")
        allr += [v for d, v in by.items() if d >= 100]
    if allr:
        L += ["", f"Median from day 100 on: **{st.median(allr):.2f}**."]
    (HERE / "batch.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    print(json.dumps(dict(ratio=use, speed_median=st.median(allr) if allr else None)))


if __name__ == "__main__":
    main()
