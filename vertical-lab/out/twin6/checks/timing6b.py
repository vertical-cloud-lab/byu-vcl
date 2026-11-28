"""Round 6, batched GP predictions (twin/opt/gp.py ``Node.chunk``, 64 points a call): the automated lab's BOFN and
pKGFN re-timed, and the batching's saving measured on identical states. Checks, not rows of the grid.

    cd vertical-lab && TWIN_PIN=portable PYTHONHASHSEED=0 TWIN6_OUT=/tmp/twin6b \
        python out/twin6/checks/timing6b.py runs              # the two timing runs, side by side, until stopped
    python out/twin6/checks/timing6b.py ab LABEL DAY DAYS     # from the timing run's checkpoint at DAY: DAYS more
                                                              # simulated days with 64-point calls and without, in
                                                              # two fresh processes side by side
    python out/twin6/checks/timing6b.py calib DAYS            # the automated lab's heuristic and funnel at 64x for
                                                              # DAYS days: engine-identical (no GP), so its CPU
                                                              # seconds against timing6_progress.jsonl's give this
                                                              # runner's speed against the runner that timed round 6

**The timing runs** are seed 0 of the grid's ``r6_vertical_parallel_bofn3_reorder`` and ``..._pkgfn3_reorder`` (two
years, 64x), run by ``bench6.simulate`` as a slice runs them, with every vCPU of this runner busy. Every 10 simulated
days each appends its CPU seconds so far to ``timing6b_progress.jsonl``. From day 200 on, every 50 days, each is
stopped, saved (twin/ckpt6.py) and carried on from the file, which gives the same run as an unbroken one
(``python -m twin.gpcheck6 resume``); the files under /tmp/twin6b/ckpt are what ``ab`` starts from.

**The A/B** (``ab``): the same saved state carried on with every node's ``chunk`` at 64 (round 6's default) and at
None (the engine before it, twin/ 701dea1: one posterior call for all the points), each in its own process; their
CPU seconds over the same simulated days give the batching's saving on identical work, whatever this runner's speed.
Appends to ``timing6b_ab.jsonl``. Everything is simulated.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

VL = Path.cwd()
sys.path.insert(0, str(VL))
HERE = Path(__file__).resolve().parent
PROG = HERE / "timing6b_progress.jsonl"
SEGS = HERE / "timing6b_segments.jsonl"
AB = HERE / "timing6b_ab.jsonl"
CAL = HERE / "timing6b_calib.jsonl"
CK = Path("/tmp/twin6b/ckpt")
RUNS = {"vertical bofn3 64x batched": ("vertical", "parallel", "bofn3", "reorder", 0, 64),
        "vertical pkgfn3 64x batched": ("vertical", "parallel", "pkgfn3", "reorder", 0, 64)}
# the same runs on the engine before the batching (every node's chunk None: twin/ 701dea1's computation), side by
# side with the batched ones: they keep all four vCPUs busy, as a slice does, and give the batching's saving over
# whole runs on this runner (the paths part once a decision turns on a last bit)
UNBATCHED = {"vertical bofn3 64x unbatched": RUNS["vertical bofn3 64x batched"],
             "vertical pkgfn3 64x unbatched": RUNS["vertical pkgfn3 64x batched"]}
CK_UNB = Path("/tmp/twin6b/ckpt_unbatched")
CALIB = {"vertical fast 64x calib": ("vertical", "parallel", "fast", "reorder", 0, 64)}
EVERY, FROM = 50, 200


def _hook(label, path):
    from twin import round6 as R6
    t0, c0 = time.time(), time.process_time()
    tick, state = R6.Twin6._stream_tick, dict(day=-1)

    def _tick(self, g):
        d = int(g // 24.0)
        if d != state["day"] and d % 10 == 0:
            state["day"] = d
            with path.open("a") as fh:
                fh.write(json.dumps(dict(label=label, day=d, wall=round(time.time() - t0, 1),
                                         cpu=round(time.process_time() - c0, 1),
                                         load1=round(os.getloadavg()[0], 2))) + "\n")
        return tick(self, g)

    R6.Twin6._stream_tick = _tick
    return t0, c0


def one_run(label):
    from twin import bench6 as B6
    from twin.opt import net6
    lab, plan, pol, stock, seed, scale = RUNS.get(label) or UNBATCHED[label]
    ck = CK
    if label in UNBATCHED:
        net6._Six.PREDICT_CHUNK = None
        ck = CK_UNB
    cfg = B6._cfg(lab, plan, pol, stock, seed, hpc=dict(scale=scale))
    t0, c0 = _hook(label, PROG)
    ck.mkdir(parents=True, exist_ok=True)
    work = ck / f"{B6.run_id(cfg)}.ckpt.xz"
    work.unlink(missing_ok=True)
    day = FROM
    while True:
        out, info = B6.simulate(cfg, ckpt=work, stop_day=day if day < B6.DAYS else None)
        if out is not None:
            rec = dict(label=label, day=B6.DAYS, cpu=round(time.process_time() - c0, 1), finished=True,
                       best_new={k: c["best_new"] for k, c in out["campaigns"].items()}, code=out["code"],
                       cpu_model=out["env"]["cpu"], segments=out["timing"].get("segments"))
            with SEGS.open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            return rec
        keep = ck / f"{B6.run_id(cfg)}_d{int(info['day'])}.ckpt.xz"
        shutil.copyfile(work, keep)
        with SEGS.open("a") as fh:
            fh.write(json.dumps(dict(label=label, day=info["day"], cpu=round(time.process_time() - c0, 1),
                                     wall=round(time.time() - t0, 1), ckpt_bytes=info["bytes"],
                                     segment=info["segments"][-1])) + "\n")
        day += EVERY


def ab_child(label, day, days, chunk, src):
    """One arm of the A/B in this process: the saved state at ``day`` with ``chunk`` on every node, ``days`` on."""
    from twin import bench6 as B6
    from twin import ckpt6
    lab, plan, pol, stock, seed, scale = RUNS[label]
    cfg = B6._cfg(lab, plan, pol, stock, seed, hpc=dict(scale=scale))
    st = ckpt6.load(src)
    n = 0
    for c in st["tw"].campaigns.values():
        for nodes in (getattr(c.policy, "nodes", None) or {}).values():
            for nd in nodes:
                nd.chunk = chunk
                n += 1
    tmp = Path(f"/tmp/twin6b/ab_{os.getpid()}.ckpt.xz")
    ckpt6.save(tmp, st)
    del st
    out, info = B6.simulate(cfg, ckpt=tmp, stop_day=day + days)
    tmp.unlink(missing_ok=True)
    seg = info["segments"][-1] if out is None else out["timing"]["segments"][-1]
    return dict(label=label, from_day=day, days=days, chunk=chunk, nodes=n, cpu_seconds=seg["cpu_seconds"],
                wall_seconds=seg["wall_seconds"], to_day=seg["to_day"], cpu_model=seg["cpu"],
                load1=round(os.getloadavg()[0], 2))


def calib(days):
    from twin import bench6 as B6
    os.environ["TWIN6_DAYS"] = str(days)
    (label, (lab, plan, pol, stock, seed, scale)), = CALIB.items()
    cfg = B6._cfg(lab, plan, pol, stock, seed, hpc=dict(scale=scale))
    _hook(label, CAL)
    out, _ = B6.simulate(cfg)
    return dict(label=label, days=days, cpu_seconds=out["timing"]["cpu_seconds"], cpu_model=out["env"]["cpu"])


if __name__ == "__main__":
    assert os.environ.get("TWIN_PIN") == "portable" and os.environ.get("PYTHONHASHSEED") == "0"
    assert os.environ.get("TWIN6_OUT", "").startswith("/tmp/")
    cmd = sys.argv[1]
    if cmd == "runs":
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(len(RUNS), max_tasks_per_child=1) as ex:
            for r in ex.map(one_run, list(RUNS)):
                print(json.dumps(r), flush=True)
    elif cmd == "unbatched":
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(len(UNBATCHED), max_tasks_per_child=1) as ex:
            for r in ex.map(one_run, list(UNBATCHED)):
                print(json.dumps(r), flush=True)
    elif cmd == "_one":
        print(json.dumps(one_run(sys.argv[2])), flush=True)
    elif cmd == "ab":
        label, day, days = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
        from twin import bench6 as B6
        lab, plan, pol, stock, seed, scale = RUNS[label]
        src = CK / f"{B6.run_id(B6._cfg(lab, plan, pol, stock, seed, hpc=dict(scale=scale)))}_d{day}.ckpt.xz"
        procs = {c: subprocess.Popen([sys.executable, __file__, "_ab", label, str(day), str(days), str(c), str(src)],
                                     stdout=subprocess.PIPE, text=True) for c in (64, None)}
        for c, p in procs.items():
            line = [l for l in p.communicate()[0].splitlines() if l.startswith("{")][-1]
            with AB.open("a") as fh:
                fh.write(line + "\n")
            print(line, flush=True)
    elif cmd == "_ab":
        label, day, days, c, src = sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6]
        print(json.dumps(ab_child(label, day, days, None if c == "None" else int(c), src)), flush=True)
    elif cmd == "calib":
        r = calib(int(sys.argv[2]))
        with CAL.open("a") as fh:
            fh.write(json.dumps(dict(r, final=True)) + "\n")
        print(json.dumps(r), flush=True)
