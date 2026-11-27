"""Round 6: the grid's timing runs and BOFN's scale pilot, timed carefully (checks, not rows of the grid).

    cd vertical-lab && TWIN_PIN=portable PYTHONHASHSEED=0 TWIN6_OUT=/tmp/twin6timing TWIN_WORKERS=4 \
        python out/twin6/checks/timing6.py SET [SET ...]        # appends to timing6.jsonl beside this file
    python out/twin6/checks/timing6.py table                    # the summary (timing6.md)

Sets: ``gp_auto`` (the automated lab's BOFN and pKGFN, stocked, two years at 64x and 16x: the grid's main cost),
``other`` (the other arms groups' two-year runs at 64x: the automated lab's heuristic and funnel, the conventional
lab's three policies), ``pilot`` (BOFN's scale pilot: the automated lab stocked, 300 days, seeds 0-1 at 1x, 16x and
64x and seed 0 at 4x, as the first attempt's pilot ran it), ``pilot1x`` (the conventional lab's BOFN and both labs'
heuristic and funnel at 1x for 300 days, against the same seed's two-year run at 64x read at day 300: the stream's
cost for those).

Each run is seed ``s`` of a grid configuration (``bench6._cfg``), run by ``bench6.simulate`` in a fresh process. Its
line records the wall seconds, **the process's CPU seconds** (what it costs a slice that runs one run per vCPU,
whatever else this runner was doing alongside: the cost to plan with), the load averages, the GP fits, the targets
reached and the provenance. Every 10 simulated days each run also appends its CPU and wall seconds so far to
``timing6_progress.jsonl``, so a run that is stopped still gives its cost curve. Nothing is written to out/twin6/runs.
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

VL = Path.cwd()
sys.path.insert(0, str(VL))
HERE = Path(__file__).resolve().parent
OUT = HERE / "timing6.jsonl"
PROG = HERE / "timing6_progress.jsonl"
ARM = {"vertical": ("vertical", "parallel", "reorder"), "conventional": ("conventional", "external", "reorder")}

# (label, lab, policy, seed, scale, days), longest first within a set
SETS = {
    "gp_auto": [("vertical pkgfn3 64x", "vertical", "pkgfn3", 0, 64, 730),
                ("vertical bofn3 64x", "vertical", "bofn3", 0, 64, 730),
                ("vertical pkgfn3 16x", "vertical", "pkgfn3", 0, 16, 730),
                ("vertical bofn3 16x", "vertical", "bofn3", 0, 16, 730)],
    "other": [("conventional pkgfn3 64x", "conventional", "pkgfn3", 0, 64, 730),
              ("conventional bofn3 64x", "conventional", "bofn3", 0, 64, 730),
              ("vertical fast 64x", "vertical", "fast", 0, 64, 730),
              ("conventional fast 64x", "conventional", "fast", 0, 64, 730)],
    "pilot": [("pilot vertical bofn3 s0 64x", "vertical", "bofn3", 0, 64, 300),
              ("pilot vertical bofn3 s1 64x", "vertical", "bofn3", 1, 64, 300),
              ("pilot vertical bofn3 s0 16x", "vertical", "bofn3", 0, 16, 300),
              ("pilot vertical bofn3 s1 16x", "vertical", "bofn3", 1, 16, 300),
              ("pilot vertical bofn3 s0 4x", "vertical", "bofn3", 0, 4, 300),
              ("pilot vertical bofn3 s0 1x", "vertical", "bofn3", 0, 1, 300),
              ("pilot vertical bofn3 s1 1x", "vertical", "bofn3", 1, 1, 300)],
    # the other policy classes and the conventional lab at 1x for 300 days: against the same seed's two-year run at
    # 64x read at day 300 (timing6_progress.jsonl), the stream's cost per unit of scale for each
    "pilot1x": [("pilot conventional bofn3 s0 1x", "conventional", "bofn3", 0, 1, 300),
                ("pilot vertical fast s0 1x", "vertical", "fast", 0, 1, 300),
                ("pilot conventional fast s0 1x", "conventional", "fast", 0, 1, 300)],
}


def one(job):
    label, lab, policy, seed, scale, days = job
    from twin import bench2 as B2
    from twin import bench6 as B6
    from twin import round6 as R6
    os.environ["TWIN6_DAYS"] = str(days)
    t0, c0 = time.time(), time.process_time()
    tick, state = R6.Twin6._stream_tick, dict(day=-1)

    def _tick(self, g):                         # every 10 simulated days: the cost so far
        d = int(g // 24.0)
        if d != state["day"] and d % 10 == 0:
            state["day"] = d
            with PROG.open("a") as fh:
                fh.write(json.dumps(dict(label=label, day=d, wall=round(time.time() - t0, 1),
                                         cpu=round(time.process_time() - c0, 1),
                                         load1=round(os.getloadavg()[0], 2))) + "\n")
        return tick(self, g)

    R6.Twin6._stream_tick = _tick
    cfg = B6._cfg(*ARM[lab][:2], policy, ARM[lab][2], seed, hpc=dict(scale=scale))
    out, tw = B6.simulate(cfg)
    T = B2.targets()
    rec = dict(label=label, lab=lab, policy=policy, seed=seed, scale=scale, days=days, run_id=B6.run_id(cfg),
               group=B6.group_key(dict(cfg, days=B6.DAYS)), seconds=out["seconds"],
               cpu_seconds=out["timing"]["cpu_seconds"], timing=out["timing"], gp_fits=out["gp"].get("fits"),
               gp=out["gp"], code=out["code"], cpu=out["env"]["cpu"], pin=out["env"]["pin"],
               used=sorted(out["r6"]["used"]["items"]), used_file_sha256=out["r6"]["used"]["file_sha256"],
               campaigns={})
    for k, c in out["campaigns"].items():
        hit = {tn: (lambda h: None if h is None else h[0])(B2.hit(c["curve_new"], T[tn][k], 2)) for tn in ("T1", "T2")}
        rec["campaigns"][k] = dict(T1_day=hit["T1"], T2_day=hit["T2"], best_new=round(c["best_new"], 4),
                                   tested=c["n_new_alloys"], spent=c["spent"],
                                   visible=out["r6"]["hpc"]["campaigns"][k]["materialized"],
                                   prescreened=c["policy_counts"].get("prescreened"))
    return B2._jsonable(rec)


def table():
    rows = [json.loads(l) for l in OUT.read_text().splitlines() if l.strip()]
    prog = {}
    if PROG.exists():
        for l in PROG.read_text().splitlines():
            if l.strip():
                p = json.loads(l)
                prog.setdefault(p["label"], []).append(p)
    done = {r["label"] for r in rows}
    L = ["# Round 6: timing runs and BOFN's scale pilot", "",
         "Made by `python out/twin6/checks/timing6.py table` from `timing6.jsonl` and `timing6_progress.jsonl`. Seed s "
         "of the stocked arm of each lab (the automated lab's parallel plan), at the scale named. **CPU seconds** are "
         "the run's own process time, what it costs a slice that runs one run per vCPU; wall seconds stretch when "
         "this runner ran more than four things at once (the load average at the end says how busy it was). "
         "Everything is simulated.", "",
         "| Run | Days | CPU s | Wall s | Load at end | GP fits | Al T1 / T2 day | Cu T1 / T2 day | Al / Cu tested | "
         "Al / Cu best new | Bought used | twin/ dirty |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["label"].startswith("pilot"), r["lab"], r["policy"], -r["scale"],
                                         r["seed"])):
        a, c = r["campaigns"]["flaime_al"], r["campaigns"]["onr_cu"]
        L.append(f"| {r['label']} | {r['days']} | {r['cpu_seconds']:,.0f} | {r['seconds']:,.0f} | "
                 f"{r['timing']['loadavg_end'][0]} | {r['gp_fits']} | {a['T1_day']} / {a['T2_day']} | "
                 f"{c['T1_day']} / {c['T2_day']} | {a['tested']} / {c['tested']} | {a['best_new']} / {c['best_new']} | "
                 f"{', '.join(r['used']) or '-'} | {r['code'].get('twin_dirty')} |")
    run = [k for k in prog if k not in done]
    if run:
        L += ["", "**Not finished** (the cost so far, from the progress file):", "",
              "| Run | Last day reached | CPU s so far | Wall s so far | CPU s a simulated day, last 50 days |",
              "|---|---|---|---|---|"]
        for k in sorted(run):
            ps = sorted(prog[k], key=lambda p: p["day"])
            last = ps[-1]
            back = [p for p in ps if p["day"] <= last["day"] - 50]
            rate = None if not back else (last["cpu"] - back[-1]["cpu"]) / max(last["day"] - back[-1]["day"], 1)
            L.append(f"| {k} | {last['day']} | {last['cpu']:,.0f} | {last['wall']:,.0f} | "
                     + ("-" if rate is None else f"{rate:.1f}") + " |")
    if prog:
        L += ["", "CPU seconds by simulated day (every 100 days), all runs:", "",
              "| Run | " + " | ".join(f"day {d}" for d in range(100, 800, 100)) + " |",
              "|---|" + "---|" * 7]
        for k in sorted(prog):
            by = {p["day"]: p["cpu"] for p in prog[k]}
            L.append(f"| {k} | " + " | ".join(f"{by[d]:,.0f}" if d in by else "" for d in range(100, 800, 100)) + " |")
    (HERE / "timing6.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    if sys.argv[1:2] == ["table"]:
        table()
        sys.exit(0)
    assert os.environ.get("TWIN_PIN") == "portable" and os.environ.get("PYTHONHASHSEED") == "0"
    assert os.environ.get("TWIN6_OUT", "").startswith("/tmp/")
    from twin import bench6 as B6                      # noqa: E402  (the twin package applies the pin first)
    done = {json.loads(l)["label"] for l in OUT.read_text().splitlines() if l.strip()} if OUT.exists() else set()
    todo = [j for s in sys.argv[1:] for j in SETS[s] if j[0] not in done]
    print(len(todo), "runs", flush=True)
    with ProcessPoolExecutor(int(os.environ.get("TWIN_WORKERS", "4")), max_tasks_per_child=1) as ex:
        futs = {ex.submit(one, j): j for j in todo}
        for f in as_completed(futs):
            j = futs[f]
            try:
                r = f.result()
            except Exception as e:
                import traceback
                r = dict(label=j[0], error=traceback.format_exc()[-3000:])
                print(j[0], "ERROR", repr(e), flush=True)
                with (HERE / "timing6.errors.jsonl").open("a") as fh:
                    fh.write(json.dumps(r) + "\n")
                continue
            with OUT.open("a") as fh:
                fh.write(json.dumps(r) + "\n")
            print(r["label"], r["cpu_seconds"], "cpu s", r["seconds"], "wall s", flush=True)
