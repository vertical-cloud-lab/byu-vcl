"""Round 6: does each of the grid's sensitivities do what it says? One shortened run of each (a check, not rows).

    cd vertical-lab && TWIN_PIN=portable PYTHONHASHSEED=0 TWIN6_OUT=/tmp/twin6paths TWIN_WORKERS=2 \
        python out/twin6/checks/paths.py            # appends to paths.jsonl beside this file
    python out/twin6/checks/paths.py table          # the summary (paths.md)

Seed 0 of the automated lab, stocked, the heuristic and the funnel (and BOFN for late crucibles), at 1x round 5's
candidates (the stream's scale changes none of these code paths, only their cost), for long enough that what each
sensitivity changes has happened: the cell (day 161-248) and, for late crucibles, the pool (day 260-380). Records
what each sensitivity is meant to change, read off the run's own record.
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

VL = Path.cwd()
sys.path.insert(0, str(VL))
HERE = Path(__file__).resolve().parent
OUT = HERE / "paths.jsonl"
H = 24.0
# (label, lab, plan, policy, stock, days, options)
CASES = [
    ("main", "vertical", "parallel", "fast", "reorder", 330, {}),
    ("lean", "vertical", "parallel", "fast", "lean", 330, {}),
    ("plan: wait for the cell", "vertical", "wait", "fast", "reorder", 330, {}),
    ("plan: external routes only", "vertical", "external", "fast", "reorder", 330, {}),
    ("decisions: none", "vertical", "parallel", "fast", "reorder", 330, dict(decisions="none")),
    ("decisions: slow", "vertical", "parallel", "fast", "reorder", 330, dict(decisions="slow")),
    ("atomizer: 3 h", "vertical", "parallel", "fast", "reorder", 330, dict(atom="3h")),
    ("atomizer: slow", "vertical", "parallel", "fast", "reorder", 330, dict(atom="slow")),
    ("crucibles: late", "vertical", "parallel", "fast", "reorder", 400, dict(late=240)),
    ("crucibles: late, BOFN", "vertical", "parallel", "bofn3", "reorder", 400, dict(late=240)),
    ("all-new equipment", "vertical", "parallel", "fast", "reorder", 330, dict(used=False)),
    ("conventional lab", "conventional", "external", "fast", "reorder", 330, {}),
]


def one(case):
    from twin import bench6 as B6
    label, lab, plan, pol, stock, days, opts = case
    os.environ["TWIN6_DAYS"] = str(days)
    cfg = B6._cfg(lab, plan, pol, stock, 0, hpc=dict(scale=1), **opts)
    out, tw = B6.simulate(cfg)
    r6, F = out["r6"], tw.fac4
    sp = r6["spend"]["totals"]
    atom = F.res["atomizer"]
    jobs = [j for j in atom.jobs if j[3] == "atomize"]
    sw = F.atom_switch_h
    after = [j for j in jobs if sw is not None and j[0] >= sw]
    per_day_after = None
    if after:
        span = (min(tw.h, max(j[0] for j in after)) - sw) / H
        per_day_after = round(len(after) / max(span, 1.0), 2)
    cr = r6["crucibles"]
    held = r6["decisions"]["held"]
    T = B6.B2.targets()
    tg = {k: {tn: (lambda h: None if h is None else round(h[0], 1))(B6.B2.hit(c["curve_new"], T[tn][k], 2))
              for tn in ("T1", "T2")} for k, c in out["campaigns"].items()}
    return dict(label=label, run=B6.run_id(cfg), days=days, seconds=out["seconds"], code=out["code"],
                pin=out["env"]["pin"], start_d=round(F.start_h / H, 1), room_d=round((F.sched.get("room_h") or 0) / H, 1),
                cell_d=None if sw is None else round(sw / H, 1), atom_cycle=F.atom_cycle,
                atom_runs=len(jobs), atom_runs_per_day_after_cell=per_day_after,
                derived_cycle_start_d=cr["derived_cycle_start_d"],
                crucibles={f: dict(arrive_d=v["arrive_d"], melts=v["melts"], runs_waited=v["runs_waited"],
                                   wait_h_total=v["wait_h_total"], most_in_use=v["most_in_use"], n=v["n"])
                           for f, v in cr["families"].items()},
                used=sorted(r6["used"]["items"]), used_source=r6["used"]["source"],
                capital_new=sp["lab"]["capital_new"], capital_used=sp["lab"]["capital_used"],
                held={k: v for k, v in held.items()}, decisions=r6["decisions"]["level"],
                spent={k: c["spent"] for k, c in out["campaigns"].items()}, targets=tg,
                tested={k: c["n_new_alloys"] for k, c in out["campaigns"].items()})


def table():
    rows = [json.loads(l) for l in OUT.read_text().splitlines() if l.strip()]
    order = {c[0]: i for i, c in enumerate(CASES)}
    rows.sort(key=lambda r: order.get(r["label"], 99))
    L = ["# Round 6: each sensitivity's code path, checked", "",
         "Made by `python out/twin6/checks/paths.py table` from `paths.jsonl`: seed 0, the automated lab stocked unless "
         "named, the heuristic and the funnel unless named, at 1x round 5's candidates, shortened. Days are from t = 0. "
         "Everything is simulated.", "",
         "| Case | Days run | Work starts | Cell | Atomizer cycle | Atomizer runs a day after the cell | Derived cycle "
         "starts | Runs that waited for a crucible (Al / Cu) | Bought used | Capital new / used ($M) | Results held "
         "for a person (Al / Cu) | Al T1 / T2 | Cu T1 / T2 | s |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        c = r["crucibles"]
        h = r["held"]
        hn = lambda k: sum(v.get("n", 0) for v in (h.get(k) or {}).values())
        t = r["targets"]
        L.append(f"| {r['label']} | {r['days']} | {r['start_d']} | {r['cell_d']} | {r['atom_cycle']} | "
                 f"{r['atom_runs_per_day_after_cell']} | {r['derived_cycle_start_d']} | "
                 f"{c['flaime_al']['runs_waited']} / {c['onr_cu']['runs_waited']} | {len(r['used'])} | "
                 f"{r['capital_new'] / 1e6:.2f} / {r['capital_used'] / 1e6:.2f} | {hn('flaime_al')} / {hn('onr_cu')} | "
                 f"{t['flaime_al']['T1']} / {t['flaime_al']['T2']} | {t['onr_cu']['T1']} / {t['onr_cu']['T2']} | "
                 f"{r['seconds']} |")
    (HERE / "paths.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    if sys.argv[1:2] == ["table"]:
        table()
        sys.exit(0)
    assert os.environ.get("TWIN_PIN") == "portable" and os.environ.get("PYTHONHASHSEED") == "0"
    assert os.environ.get("TWIN6_OUT", "").startswith("/tmp/")
    from twin import bench6 as B6                  # noqa: E402  (the twin package applies the pin first)
    done = {json.loads(l)["label"] for l in OUT.read_text().splitlines()} if OUT.exists() else set()
    todo = [c for c in CASES if c[0] not in done]
    with ProcessPoolExecutor(int(os.environ.get("TWIN_WORKERS", "1")), max_tasks_per_child=1) as ex:
        futs = {ex.submit(one, c): c for c in sorted(todo, key=lambda c: c[3] == "fast")}
        for f in as_completed(futs):
            c = futs[f]
            try:
                r = f.result()
            except Exception as e:                  # a sensitivity that breaks is the finding
                r = dict(label=c[0], error=repr(e)[:2000])
            with OUT.open("a") as fh:
                fh.write(json.dumps(B6.B2._jsonable(r)) + "\n")
            print(c[0], r.get("seconds"), r.get("error", ""), flush=True)
