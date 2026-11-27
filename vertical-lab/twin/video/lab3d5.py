"""The animated lab for the two-year replay (rounds 5 and later): lab3d's scene and moves, plus the build-out.

    cd vertical-lab
    TWIN_VIDEO_ROUND=5 VIZ3D_SIZE=1920x1080 xvfb-run -a python -m twin.video.lab3d5 parts        # the scene's parts
    TWIN_VIDEO_ROUND=5 VIZ3D_SIZE=1920x1080 xvfb-run -a python -m twin.video.lab3d5 test 30 90 170 300
    TWIN_VIDEO_ROUND=5 python -m twin.video.lab3d5 run                                            # every 3-D job

Round 5's replay starts on the day the money arrives, before there is a lab. So each part of PR 318's scene is drawn
as a ghost (see-through) until the twin has it online, and solid from then on (replay5.part_online: the space, each
Shuttle and its trays, each floor machine, the mobile units). A part of the lab's design that the twin's build-out
does not list stays a ghost for the whole replay. The trays and units move only from the day the cell is integrated
(replay5.moves_view): before that, people run each station as it comes online.

A render is reused while neither the moves' state (lab3d_sched.Plan.key) nor the set of parts online changes, so the
months before the space is ready and the months after the lab stops cost a handful of renders.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from . import lab3d as L3

HERE = L3.HERE
VLM_GROUPS = ("base", "posts", "col_front", "col_rear", "lift_rails", "drive", "lift", "belts", "bay", "console",
              "shutter", "skin_L", "skin_R", "skin_back", "skin_front", "skin_top")      # setup_lab.movie's
# cameras: lab3d's, with the whole-lab views turned a little east, so the floor clears the replay's right-hand column
VIEWS = dict(L3.VIEWS)


class Lab3D5(L3.Lab3D):
    """lab3d.Lab3D with each part of the scene solid or a ghost."""

    def __init__(self):
        super().__init__()
        self.parts = self._parts()
        self._alpha0 = {n: float(self.sc.alpha.get(n, 1.0)) for n in self.sc.actors}
        self._bkey = None

    def _root(self, g: str) -> str:
        sc = self.sc
        seen = 0
        while g in sc.parent and seen < 64:
            g = sc.parent[g]
            seen += 1
        return g

    def _parts(self) -> dict:
        """{part: [actor names]}: 'm:<machine>' the floor machines (setup_lab's floor groups), 't:<tray>' each tray
        with what stands on it, 'shuttle1', 'shuttle2', 'units' (the MiR250 + UR12e units), 'chargers', and 'room' for
        everything else (the floor's markings, docks, services, safety equipment, cameras)."""
        sc, F = self.sc, self.F
        machine = {}
        for key, names in F.groups.items():
            if key in ("tape", "docks", "racking", "vlm", "vlm2") or not names:
                continue
            for n in names:
                machine.setdefault(n, key)
        unit_names = set()
        for u in self.units:
            try:
                unit_names |= set(u.all_names())
            except Exception:                               # noqa: BLE001
                pass
        u3 = getattr(F, "unit3", None)
        if u3 is not None:
            try:
                unit_names |= set(u3.all_names())
            except Exception:                               # noqa: BLE001
                pass
        parts: dict = {}
        self.roots: dict = {}
        for name, g in sc.group_of.items():
            if name not in sc.actors:
                continue
            r = self._root(g)
            chain, gg = [g], g
            while gg in sc.parent and len(chain) < 64:
                gg = sc.parent[gg]
                chain.append(gg)
            tray = next((c for c in chain if c.startswith("tray_")), None)
            if name in machine:
                key = "m:" + machine[name]
            elif name in unit_names:
                key = "units"
            elif tray is not None:
                key = "t:" + tray[5:]
            elif any(c.startswith("u2_") for c in chain):
                key = "shuttle2"
            elif any(c in VLM_GROUPS for c in chain):
                key = "shuttle1"
            elif any(c.startswith("charger") for c in chain):
                key = "chargers"
            else:
                key = "room"
                self.roots[r] = self.roots.get(r, 0) + 1
            parts.setdefault(key, []).append(name)
        return parts

    def apply_build(self, alpha: dict, ghost: float):
        """Each part at its alpha (replay5.build_alpha); a part the build-out doesn't list is a ghost."""
        key = tuple(sorted((k, round(float(alpha.get(k, ghost)), 3)) for k in self.parts))
        if key == self._bkey:
            return
        self._bkey = key
        sc = self.sc
        for part, names in self.parts.items():
            a = float(alpha.get(part, ghost))
            for n in names:
                sc.alpha[n] = self._alpha0.get(n, 1.0) * a

    def view(self, name: str):
        cam, va = VIEWS[name]
        self.sc.cam = [tuple(v) for v in cam]
        self.sc.view_angle = va
        self.sc._clip_n = 0


# ============================================================================================ jobs
def render_job(job: dict, lab: Lab3D5, shared: dict):
    """One job's frames: <out>.mp4 (the renders at its fps, x264 crf 12, 4:4:4) and <out>.json (the job, its counts
    and, per frame, its video time, view and whether the render was reused)."""
    from . import lab3d_sched as LS
    from . import replay5 as R5
    t_start = time.time()
    lab.kin = lab.kin or LS.load_kin()
    if "plan" not in shared:
        shared["plan"] = R5.plan()
        shared["tl"] = R5.tl()
    p, T = shared["plan"], shared["tl"]
    fps = float(job["fps"])
    v0, v1 = float(job["v0"]), float(job["v1"])
    n = int(round((v1 - v0) * fps))
    out = Path(job["out"])
    out.parent.mkdir(parents=True, exist_ok=True)
    W_, H_ = (int(v) for v in lab.sc.size)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W_}x{H_}",
                            "-framerate", f"{fps:g}", "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast",
                            "-crf", "12", "-pix_fmt", "yuv444p", "-threads", "1", str(out.with_suffix(".mp4"))],
                           stdin=subprocess.PIPE)
    rec, last_key, last_img, cur_view, renders = [], None, None, None, 0
    cpu0 = time.process_time()
    for i in range(n):
        v = v0 + i / fps
        name = L3.view_at(job, v)
        if name != cur_view:
            lab.view(name)
            cur_view, last_key = name, None
        t_h = T.lab(v)[0]
        key = (p.key(v), R5.build_key(t_h))
        if key != last_key or last_img is None:
            lab.apply_build(R5.build_alpha(t_h), R5.GHOST)
            lab.apply(p.state(v))
            last_img = np.ascontiguousarray(lab.render())
            last_key = key
            renders += 1
            reused = False
        else:
            reused = True
        enc.stdin.write(last_img.tobytes())
        rec.append(dict(v=round(v, 4), view=name, reused=reused))
        if (i + 1) % 100 == 0:
            print(f"{out.name}: {i + 1}/{n} frames, {renders} renders, {time.time() - t_start:.0f} s", flush=True)
    enc.stdin.close()
    enc.wait()
    info = dict(job=job, frames=n, renders=renders, build_s=round(lab.build_s, 1),
                wall_s=round(time.time() - t_start, 1), cpu_s=round(time.process_time() - cpu0, 1),
                counts=LS.summary(p), frames_rec=rec)
    out.with_suffix(".json").write_text(json.dumps(info) + "\n")
    print(json.dumps({k: v for k, v in info.items() if k not in ("frames_rec", "job")} | dict(out=out.name)),
          flush=True)


def render_batch(jobs: list):
    lab = Lab3D5()
    shared: dict = {}
    for j in jobs:
        render_job(j, lab, shared)


def _done(j: dict) -> bool:
    rec = Path(j["out"]).with_suffix(".json")
    if not (rec.exists() and Path(j["out"]).with_suffix(".mp4").exists()):
        return False
    try:
        return json.loads(rec.read_text()).get("job") == j
    except Exception:                                      # noqa: BLE001
        return False


def run_jobs(jobs: list, workers: int):
    """The jobs not already done, in `workers` processes, each rendering a batch of one frame size with one scene
    build (about 3 GB each). Batches are balanced by the renders each job is likely to need, not by its frames: a
    stretch in which nothing in the lab changes costs one render."""
    from . import replay5 as R5
    todo = [j for j in jobs if not _done(j)]
    if not todo:
        print("3-D: every job is done", flush=True)
        return
    p, T = R5.plan(), R5.tl()

    def cost(j):
        keys, last = 0, None
        n = int(round((j["v1"] - j["v0"]) * j["fps"]))
        for i in range(n):
            v = j["v0"] + i / j["fps"]
            k = (p.key(v), R5.build_key(T.lab(v)[0]))
            if k != last:
                keys, last = keys + 1, k
        return (keys + 3) * (j["size"][0] * j["size"][1]) / (1920 * 1080)
    costs = {j["out"]: cost(j) for j in todo}
    by_size: dict = {}
    for j in todo:
        by_size.setdefault(tuple(j["size"]), []).append(j)
    tot = sum(costs.values()) or 1.0
    ks = {s: max(1, min(len(js), round(workers * sum(costs[j["out"]] for j in js) / tot))) for s, js in by_size.items()}
    while sum(ks.values()) > max(workers, len(ks)):
        big = max(ks, key=lambda s: ks[s])
        ks[big] -= 1
    batches = []
    for s, js in by_size.items():
        per = [[] for _ in range(ks[s])]
        load = [0.0] * ks[s]
        for j in sorted(js, key=lambda j: -costs[j["out"]]):
            i = int(np.argmin(load))
            per[i].append(j)
            load[i] += costs[j["out"]]
        batches += [(s, sorted(b, key=lambda j: j["v0"])) for b in per if b]
    print(f"3-D: {len(todo)} jobs, about {sum(costs.values()):.0f} full-size renders, {len(batches)} processes",
          flush=True)
    t0 = time.time()
    procs = []
    tmp = Path(todo[0]["out"]).parent
    tmp.mkdir(parents=True, exist_ok=True)
    for n, (size, batch) in enumerate(batches):
        bp = tmp / f"r5_batch_{n}_{size[0]}x{size[1]}.json"
        bp.write_text(json.dumps(batch))
        env = dict(os.environ, VIZ3D_SIZE=f"{size[0]}x{size[1]}",
                   LP_NUM_THREADS=os.environ.get("TWIN_VIDEO_LP_THREADS", "2"))
        log = open(bp.with_suffix(".log"), "w")
        pr = subprocess.Popen(["xvfb-run", "-a", "-s", f"-screen 0 {max(size[0], 1280)}x{max(size[1], 720)}x24",
                               sys.executable, "-m", "twin.video.lab3d5", "render", str(bp)], cwd=HERE, env=env,
                              stdout=log, stderr=subprocess.STDOUT)
        procs.append((pr, bp, log))
        print(f"  3-D batch {n}: {len(batch)} jobs at {size[0]}x{size[1]}", flush=True)
    for pr, bp, log in procs:
        pr.wait()
        log.close()
        print(f"  3-D {bp.name}: rc {pr.returncode}, {time.time() - t0:.0f} s", flush=True)
        if pr.returncode != 0:
            raise SystemExit(f"3-D batch {bp} failed: see {bp.with_suffix('.log')}")
    bad = [j["out"] for j in jobs if not _done(j)]
    if bad:
        raise SystemExit(f"3-D jobs missing after the run: {bad}")


def test_main(days: list):
    from PIL import Image
    from . import lab3d_sched as LS
    from . import replay5 as R5
    Path("/tmp/vid").mkdir(exist_ok=True)
    lab = Lab3D5()
    lab.kin = LS.load_kin()
    print(f"built in {lab.build_s:.0f} s; parts: " + ", ".join(f"{k} {len(v)}" for k, v in sorted(lab.parts.items())),
          flush=True)
    p, T = R5.plan(), R5.tl()
    for d in days:
        v = T.video(d * 24.0)
        t_h = T.lab(v)[0]
        for name in (os.environ.get("TEST_VIEWS", "high").split(",")):
            lab.view(name)
            lab.apply_build(R5.build_alpha(t_h), R5.GHOST)
            lab.apply(p.state(v))
            t0 = time.time()
            img = lab.render()
            print(f"day {d:g} ({v:.1f} s) {name}: {time.time() - t0:.2f} s", flush=True)
            Image.fromarray(img).save(f"/tmp/vid/lab3d5_{name}_d{int(d):03d}.png")


if __name__ == "__main__":
    cmd = sys.argv[1] if sys.argv[1:] else "run"
    if cmd == "parts":
        lab = Lab3D5()
        print(f"built in {lab.build_s:.0f} s")
        for k, v in sorted(lab.parts.items()):
            print(f"  {k:18s} {len(v):5d} actors")
        print("  room's root groups:", dict(sorted(lab.roots.items(), key=lambda kv: -kv[1])[:60]))
    elif cmd == "test":
        test_main([float(x) for x in sys.argv[2:]] or [30.0, 90.0, 170.0, 300.0])
    elif cmd == "render":
        js = json.loads(Path(sys.argv[2]).read_text())
        render_batch(js if isinstance(js, list) else [js])
    elif cmd == "run":
        from . import replay5 as R5
        run_jobs(R5.jobs(), int(os.environ.get("TWIN_VIDEO_WORKERS", "3")))
    else:
        raise SystemExit(__doc__)
