"""Round 6, item 6 (a check, not rows of the grid): do copper's stretches with free capacity and nothing started,
which round 5 found with BOFN and pKGFN, go away without the optimizers' cap on blend screens?

    cd vertical-lab && TWIN_PIN=portable PYTHONHASHSEED=0 TWIN6_OUT=/tmp/twin6idle TWIN_WORKERS=4 \
        python out/twin6/checks/copper_idle.py          # appends to copper_idle.jsonl beside this file
    python out/twin6/checks/copper_idle.py table        # the summary (copper_idle.md)

Reruns, on round 6's engine, arms and seeds in which round 5 flagged a copper stretch (out/twin5/runs/net*.jsonl.xz),
for days that cover the flagged stretches, twice: with round 6's policies (no cap) and with the cap put back
(``bofn3cap``, ``pkgfn3cap`` in twin/opt/net6.py; the rest of round 6 unchanged), so that what the cap does is told
apart from what the rest of round 6 does. Records copper's stretches by round 6's rule (the policy waiting while the
campaign could have started a job: twin/round6.py ``idle_report6``), what the policy did in them, why it offered no
new design when it didn't (twin/opt/net6.py's counters), and how many blend screens it ran.
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

VL = Path.cwd()
sys.path.insert(0, str(VL))
HERE = Path(__file__).resolve().parent
OUT = HERE / "copper_idle.jsonl"
# (lab, plan, policy, stock, seed, days): round 5 flagged copper's first fabrication step in each of these
CASES = [("conventional", "external", "bofn3", "lean", s, 260) for s in (0, 4)] + \
        [("conventional", "external", "bofn3", "reorder", s, 260) for s in (0, 2)] + \
        [("conventional", "external", "pkgfn3", "reorder", s, 260) for s in (0, 2)] + \
        [("vertical", "parallel", "bofn3", "reorder", s, 170) for s in (0, 1)] + \
        [("vertical", "parallel", "pkgfn3", "reorder", s, 170) for s in (0, 1)]


def round5_flags():
    from twin import bench5 as B5
    out = {}
    for r in B5.load("net") + B5.load("net_more"):
        c = r["cfg"]
        key = (c["lab"], c["plan"], c["policy"], c["stock"], c["seed"])
        out[key] = {g: [(x["start_d"], x["days"]) for x in v if x["flag"]]
                    for g, v in r["r5"]["idle"]["stretches"]["onr_cu"].items()}
    return out


def flag5(x):
    return x["station_busy_frac"] < 0.5 and x["cause"].startswith("policy waiting") and x["days"] >= 14


def one(case):
    from twin import bench6 as B6
    lab, plan, pol, stock, seed, days = case
    os.environ["TWIN6_DAYS"] = str(days)
    cfg = B6._cfg(lab, plan, pol, stock, seed)
    out, tw = B6.simulate(cfg)
    st = out["r6"]["idle"]["stretches"]["onr_cu"]
    keep = ("start_d", "days", "cause", "could_start", "flag", "days_asked", "days_nothing_proposed", "pending_median",
            "causes", "station_busy_frac")
    cu = tw.campaigns["onr_cu"]
    return dict(run=B6.run_id(cfg), case=list(case), days=days, seconds=out["seconds"], code=out["code"],
                pin=out["env"]["pin"], cpu=out["env"]["cpu"],
                stretches={g: [{k: x[k] for k in keep} for x in v if x["days"] >= 14] for g, v in st.items()},
                flagged={g: [(x["start_d"], x["days"]) for x in v if x["flag"]] for g, v in st.items()},
                # round 5's rule on the same stretches: the station busy under half of every hour of the stretch, the
                # policy waiting, two weeks or more (money never runs out in round 6)
                flagged_r5_rule={g: [(x["start_d"], x["days"]) for x in v if flag5(x)] for g, v in st.items()},
                policy_counts=out["campaigns"]["onr_cu"]["policy_counts"], status=out["campaigns"]["onr_cu"]["status"],
                counters=out["r6"]["counters"]["onr_cu"],
                blend_screens=sum(1 for D in cu.deposits.values() if D.get("mode") == "blend"),
                lots=len(cu.lots), deposits=len(cu.deposits), spent=round(cu.spent, 2),
                best_new=out["campaigns"]["onr_cu"]["best_new"])


def table():
    rows = [json.loads(l) for l in OUT.read_text().splitlines() if l.strip()]
    by = {}
    for r in rows:
        lab, plan, pol, stock, seed, days = r["case"]
        base = pol.replace("cap", "")
        by.setdefault((lab, base, stock, seed, days), {})["cap" if pol.endswith("cap") else "nocap"] = r
    L = ["# Copper's idle stretches with and without the cap on blend screens (round 6's engine)", "",
         "Made by `python out/twin6/checks/copper_idle.py table` from `copper_idle.jsonl`. A stretch is flagged when "
         "copper's first fabrication step (or the atomizer) started nothing for two weeks or more while the policy "
         "was waiting and the campaign could have started a job (twin/round6.py `idle_report6`). Everything is "
         "simulated.", "",
         "Round 5's rule (the station busy under half of every hour of the stretch) is applied to the same stretches "
         "beside round 6's (a partner's session offered and not used, or an in-house station free half its open "
         "hours), so that a change of rule is not mistaken for a change of policy. Counts are of copper's first "
         "fabrication step, where round 5 found its stretches.", "",
         "| Lab | Policy | Stock | Seed | Days | Round 5 flagged | Flagged, cap (r6 rule / r5 rule) | "
         "Flagged, no cap (r6 rule / r5 rule) | Blend screens, cap / no cap | Lots, cap / no cap |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    tot = {(k, rule): 0 for k in ("cap", "nocap") for rule in ("flagged", "flagged_r5_rule")}
    n = lambda r, f: sum(len(v) for g, v in r[f].items() if g == "fab")
    for (lab, pol, stock, seed, days), d in sorted(by.items()):
        for k, r in d.items():
            for rule in ("flagged", "flagged_r5_rule"):
                tot[(k, rule)] += n(r, rule)
        cell = lambda k, fn: str(fn(d[k])) if k in d else "-"
        r5f = next(iter(d.values()))["round5_flagged"].get("fab", [])
        L.append(f"| {lab} | {pol} | {stock} | {seed} | {days} | {len(r5f)} | "
                 f"{cell('cap', lambda r: n(r, 'flagged'))} / {cell('cap', lambda r: n(r, 'flagged_r5_rule'))} | "
                 f"{cell('nocap', lambda r: n(r, 'flagged'))} / {cell('nocap', lambda r: n(r, 'flagged_r5_rule'))} | "
                 f"{cell('cap', lambda r: r['blend_screens'])} / {cell('nocap', lambda r: r['blend_screens'])} | "
                 f"{cell('cap', lambda r: r['lots'])} / {cell('nocap', lambda r: r['lots'])} |")
    L += ["", "Copper's first fabrication step, flagged stretches in all: with the cap put back "
              f"{tot[('cap', 'flagged')]} by round 6's rule and {tot[('cap', 'flagged_r5_rule')]} by round 5's; "
              f"without it {tot[('nocap', 'flagged')]} and {tot[('nocap', 'flagged_r5_rule')]}."]
    (HERE / "copper_idle.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    if sys.argv[1:2] == ["table"]:
        table()
        sys.exit(0)
    assert os.environ.get("TWIN_PIN") == "portable" and os.environ.get("PYTHONHASHSEED") == "0"
    assert os.environ.get("TWIN6_OUT", "").startswith("/tmp/")
    from twin import bench6 as B6                  # noqa: E402  (the twin package applies the pin first)
    r5 = round5_flags()
    done = {json.loads(l)["run"] for l in OUT.read_text().splitlines()} if OUT.exists() else set()
    both = [v for c in CASES for v in (c, (c[0], c[1], c[2] + "cap") + c[3:])]
    todo = [c for c in both if B6.run_id(B6._cfg(*c[:5])) not in done]
    with ProcessPoolExecutor(int(os.environ.get("TWIN_WORKERS", "1")), max_tasks_per_child=1) as ex:
        futs = {ex.submit(one, c): c for c in todo}
        for f in as_completed(futs):
            c = futs[f]
            r = f.result()
            key = (c[0], c[1], c[2].replace("cap", ""), c[3], c[4])
            r["round5_flagged"] = {g: [x for x in v if x[0] < c[5]] for g, v in r5.get(key, {}).items()}
            with OUT.open("a") as fh:
                fh.write(json.dumps(B6.B2._jsonable(r)) + "\n")
            print(r["run"], r["seconds"], "s; round 5 flagged", r["round5_flagged"], "; round 6 flags", r["flagged"],
                  file=sys.stderr, flush=True)
