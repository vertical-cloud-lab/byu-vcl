"""The animated lab for the campaign video's replay: PR 318's set-up movie scene, moved by the event log.

    cd vertical-lab
    VIZ3D_SIZE=1920x1080 xvfb-run -a python -m twin.video.lab3d kin           # out/twin2/video/lab3d/kin.json
    VIZ3D_SIZE=1920x1080 xvfb-run -a python -m twin.video.lab3d test          # a few test frames -> /tmp/vid/lab3d_*
    VIZ3D_SIZE=1920x1080 xvfb-run -a python -m twin.video.lab3d render JOB    # one job's frames (see render())

The scene is the one birdseye_render.py renders its stills from: setup_lab.build's lab as the set-up movie (PR 318)
builds it, both Shuttles see-through with every tray loaded, the floor machines, and the two MiR250 + UR12e units.
Nothing in it is rebuilt here. A frame's state comes from lab3d_sched's plan (the event log's bookings, turned into
tray presentations and unit visits) and is put on the scene with the scene's own code:

* trays: setup_lab.TwoLab, the tower's coupling as the set-up movie moves it: each tray's [y, z] (L.tray), its lamp
  (L.where: lit in its slot or at the opening, dark in transit), each Shuttle's extractor (L.lift_z) and shutter
  (L.shutter), switched with L.use(shuttle), then L.apply_state();
* units: setup_lab.Unit.set((x, y, heading)) for the MiR250, robot.Robot.set(q) for the UR12e. The arm's work at a dock
  passes through the poses timelapse.Movie.work aims at: over the presented tray's front at a Shuttle's opening, or
  half a metre in front of a floor machine, solved by the arm's own IK (ur_arm.ik) once, in kin().

Render cost (2026-11-26, this runner: 4 cores, llvmpipe): building the scene takes 115 s with the tessellation cached
(983 s the first time), peak RSS 3.0 GB; a 1920 x 1080 frame of the whole lab takes 0.9 s of wall time with depth
peeling (1.7 CPU-s) and 0.6 s without (1.1-1.2 CPU-s), with no visible difference from above, so peeling is off.
Renders are made at RENDER_FPS (15) and held for two frames of the 30 fps cut, and a render is reused whenever the
plan's state hasn't changed since the last one (Plan.key): an idle lab costs nothing to show.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[2]            # vertical-lab/
sys.path.insert(0, str(HERE))
OUTD = HERE / "out" / "twin2" / "video" / "lab3d"
RENDER_FPS = 15

# cameras (position, focal point, view up; mm) and view angles. "high", "sw" and "se" are the stills' (birdseye_render
# VIEWS) with a narrower angle, so trays and units read at 1920 x 1080; "towers" is close on both Shuttles and the
# aisle in front of them, "west" on the atomizer end of the floor.
VIEWS = {
    "high": ([(1400.0, -25500.0, 23500.0), (1400.0, -3700.0, 700.0), (0.0, 0.0, 1.0)], 30.0 / 1.25),
    "sw": ([(-7200.0, -24000.0, 17500.0), (1300.0, -3700.0, 600.0), (0.0, 0.0, 1.0)], 30.0 / 1.1),
    "se": ([(10200.0, -24000.0, 17500.0), (1500.0, -3700.0, 600.0), (0.0, 0.0, 1.0)], 30.0 / 1.1),
    "towers": ([(9800.0, -13800.0, 7400.0), (1500.0, -2600.0, 1900.0), (0.0, 0.0, 1.0)], 30.0),
    "west": ([(-1400.0, -15500.0, 8600.0), (-3600.0, -3600.0, 700.0), (0.0, 0.0, 1.0)], 30.0),
}


# ============================================================================================ the scene
class Lab3D:
    """The set-up movie's lab, its trays, Shuttles and units moved to a lab3d_sched state each frame."""

    def __init__(self):
        from . import birdseye_render as BR
        t0 = time.time()
        sc, L, F, V, W, SL, A = BR.build()
        self.sc, self.L, self.F, self.V, self.W, self.SL, self.A = sc, L, F, V, W, SL, A
        self.units = list(sc.units)
        self.home = {k: [*V.SLOTS[A.HOME[k]]] for k in L.tray}
        self.q_park = np.radians(A.PARK_DEG)
        self.q_ready = np.radians((-90.0, -100.0, 110.0, -100.0, -90.0, 0.0))     # timelapse.Movie's
        sc.pl.renderer.SetUseDepthPeeling(False)
        os.environ["VIZ3D_PEEL"] = "off"
        self.pts, self.bnds = BR.anchors_world(sc, L, F, V, W, SL, A)
        self.kin = None
        self.build_s = time.time() - t0

    # ------------------------------------------------------------------------------------------------ kinematics
    def kinematics(self) -> dict:
        """kin.json: what lab3d_sched needs about the lab (trays' slots, docks, chargers, the aisle, the arm's work
        poses at every dock), taken from the built scene's own modules."""
        from scene import R, T
        V, A, W, SL, L = self.V, self.A, self.W, self.SL, self.L
        trays = {}
        for k in sorted(L.tray):
            y, z = V.SLOTS[A.HOME[k]]
            trays[k] = dict(slot=A.HOME[k], shuttle=int(L.unit.get(k, 1)), y=float(y), z=float(z))
        docks = {}
        for key in W.STATIONS:
            try:
                docks[key] = [float(v) for v in W.dock_pose(key)]
            except Exception:                                # noqa: BLE001  (no dock)
                pass
        for key in SL.NO_DOCK:
            docks.pop(key, None)
        yo, zo = V.SLOTS["open"]
        work = {}
        uu = self.units[0]
        pose0 = list(uu.pose)
        q0 = np.array(uu.robot.q, float)
        for key, (x, y, hd) in docks.items():
            uu.set((x, y, hd))
            M = T((x, y, 0)) @ R((0, 0, 1), hd)
            qs = []
            for dx in (-260.0, 0.0, 260.0):
                if key in ("vlm", "vlm2"):
                    arm = M @ np.array([*A.ARM_LOCAL, 0.0, 1.0])
                    p = (arm[0] + dx, yo - V.TRAY_D / 2 + 230.0, zo + V.T_FLOOR + 260.0)
                else:
                    q = M @ np.array([A.ARM_LOCAL[0] + dx, A.ARM_LOCAL[1] + 520.0, 0.0, 1.0])
                    p = (q[0], q[1], 980.0)
                try:
                    qq = uu.robot.solve(A.down(p), seed=self.q_ready)
                    ok = qq is not None and np.all(np.isfinite(qq))
                except Exception:                            # noqa: BLE001
                    ok = False
                qs.append([float(v) for v in (qq if ok else self.q_ready)])
            work[key] = qs
        uu.set(pose0)
        uu.robot.set(q0)
        kin = dict(
            note="written by twin/video/lab3d.py kin from setup_lab.build's lab; read by lab3d_sched",
            open=[float(yo), float(zo)], lift_home=float(A.LIFT_HOME), shuttle_x={str(k): float(v) for k, v in
                                                                                 V.SHUTTLE_X.items()},
            trays=trays, docks=docks, back_in=sorted(W.BACK_IN),
            chargers=[[float(v) for v in W.charger_pose(i)] for i in range(len(self.units))],
            aisle=[float(v) for v in W.AISLE], q_park=[float(v) for v in self.q_park],
            q_ready=[float(v) for v in self.q_ready], work_q=work,
            world={k: [round(float(v), 1) for v in p] for k, p in self.pts.items()})
        self.kin = kin
        return kin

    # ------------------------------------------------------------------------------------------------ state
    def arm_q(self, arm) -> np.ndarray:
        """Joint angles for a unit's arm state: ('park',) or ('work', dock, u)."""
        from .lab3d_sched import WORK_KEYS, ease
        if arm[0] != "work":
            return self.q_park
        kin = self.kin
        qs = [np.array(q, float) for q in kin["work_q"].get(arm[1], [kin["q_ready"]] * 3)]
        named = {"park": self.q_park, "ready": np.array(kin["q_ready"], float)}
        u = float(arm[2])
        for (u0, k0), (u1, k1) in zip(WORK_KEYS[:-1], WORK_KEYS[1:]):
            if u <= u1:
                a = named[k0] if isinstance(k0, str) else qs[k0]
                b = named[k1] if isinstance(k1, str) else qs[k1]
                f = ease((u - u0) / max(u1 - u0, 1e-9))
                return a + (b - a) * f
        return self.q_park

    def apply(self, st: dict):
        """Put a lab3d_sched state on the scene."""
        L, A = self.L, self.A
        for k in L.tray:
            L.tray[k] = list(self.home[k])
            L.where[k] = A.HOME[k]
        for s in (1, 2):
            ts = st["towers"].get(s)
            if ts is None:
                continue
            L.use(s)
            L.lift_z = float(ts["lift"])
            L.shutter = float(ts["shutter"])
            for k, (y, z) in ts["trays"].items():
                if k in L.tray:
                    L.tray[k] = [float(y), float(z)]
                    L.where[k] = "open" if ts["out"] == k else None
        L.use(1)
        L.apply_state()
        for u, us in enumerate(st["units"]):
            if u >= len(self.units):
                break
            self.units[u].set(tuple(float(v) for v in us["pose"]))
            self.units[u].robot.set(self.arm_q(us["arm"]))

    # ------------------------------------------------------------------------------------------------ cameras
    def view(self, name: str):
        cam, va = VIEWS[name]
        self.sc.cam = [tuple(v) for v in cam]
        self.sc.view_angle = va
        self.sc._clip_n = 0

    def render(self) -> np.ndarray:
        return self.sc.render_base()[:, :, :3]

    def projection(self, name: str) -> dict:
        """The current view's world -> pixel map: the 4x4 world -> clip matrix and every world anchor in pixels."""
        sc = self.sc
        size = tuple(int(v) for v in sc.size)
        self.view(name)
        sc.render_base()                                   # the camera is applied by a render
        ren = sc.pl.renderer
        cam = ren.GetActiveCamera()
        M = cam.GetCompositeProjectionTransformMatrix(size[0] / size[1], -1.0, 1.0)
        mat = [[M.GetElement(i, j) for j in range(4)] for i in range(4)]
        anc = {}
        for key, p in self.pts.items():
            ren.SetWorldPoint(float(p[0]), float(p[1]), float(p[2]), 1.0)
            ren.WorldToDisplay()
            dx, dy, dz = ren.GetDisplayPoint()
            anc[key] = [round(dx, 1), round(size[1] - dy, 1), round(dz, 5)]
        return dict(view=name, size=list(size), camera=[list(v) for v in VIEWS[name][0]], view_angle=VIEWS[name][1],
                    matrix=mat, anchors=anc)


def project(mat, size, xyz) -> tuple:
    """World point -> pixel (x, y) with a projection() matrix."""
    M = np.asarray(mat, float)
    p = M @ np.array([xyz[0], xyz[1], xyz[2], 1.0])
    if abs(p[3]) < 1e-9:
        return None
    x, y = p[0] / p[3], p[1] / p[3]
    return (x + 1.0) * 0.5 * size[0], (1.0 - (y + 1.0) * 0.5) * size[1]


# ============================================================================================ jobs
def kin_main():
    lab = Lab3D()
    kin = lab.kinematics()
    OUTD.mkdir(parents=True, exist_ok=True)
    views = {}
    for nm in VIEWS:
        views[nm] = lab.projection(nm)
    kin["views"] = views
    (OUTD / "kin.json").write_text(json.dumps(kin, indent=1) + "\n")
    print(f"kin.json written; build {lab.build_s:.0f} s", flush=True)


def render_job(job: dict):
    """job: {"clock": "week" | "replay", ..., "view": [(v0, v1, view name)], "v0", "v1", "fps", "out": path stem}.
    Writes <out>.mp4 (the renders at `fps`, x264 crf 12) and <out>.json (per render: its video time, view and whether
    it was a reuse)."""
    import subprocess
    from . import data as D
    from . import lab3d_sched as LS
    t_start = time.time()
    lab = Lab3D()
    lab.kin = LS.load_kin()
    clock = clock_of(job)
    R = D.Replay()
    p = LS.plan(R, lab.kin, clock)
    fps = float(job.get("fps", RENDER_FPS))
    v0, v1 = float(job["v0"]), float(job["v1"])
    n = int(round((v1 - v0) * fps))
    out = Path(job["out"])
    out.parent.mkdir(parents=True, exist_ok=True)
    W_, H_ = (int(v) for v in lab.sc.size)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W_}x{H_}",
                            "-framerate", f"{fps:g}", "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast",
                            "-crf", "12", "-pix_fmt", "yuv444p", "-threads", "1", str(out.with_suffix(".mp4"))],
                           stdin=subprocess.PIPE)
    rec = []
    last_key, last_img, cur_view = None, None, None
    cpu0 = time.process_time()
    renders = 0
    for i in range(n):
        v = v0 + i / fps
        name = view_at(job, v)
        if name != cur_view:
            lab.view(name)
            cur_view = name
            last_key = None
        key = p.key(v)
        if key != last_key or last_img is None:
            lab.apply(p.state(v))
            last_img = np.ascontiguousarray(lab.render())
            last_key = key
            renders += 1
            reused = False
        else:
            reused = True
        enc.stdin.write(last_img.tobytes())
        rec.append(dict(v=round(v, 4), view=name, reused=reused))
        if (i + 1) % 150 == 0:
            print(f"{out.name}: {i + 1}/{n} frames, {renders} renders, {time.time() - t_start:.0f} s", flush=True)
    enc.stdin.close()
    enc.wait()
    info = dict(job=job, frames=n, renders=renders, build_s=round(lab.build_s, 1),
                wall_s=round(time.time() - t_start, 1), cpu_s=round(time.process_time() - cpu0, 1),
                counts=LS.summary(p), frames_rec=rec)
    out.with_suffix(".json").write_text(json.dumps(info) + "\n")
    print(json.dumps({k: v for k, v in info.items() if k != "frames_rec"}), flush=True)


def clock_of(job: dict):
    from . import lab3d_sched as LS
    c = job["clock"]
    if c == "week":
        return LS.Clock.linear(float(job["lab_h0"]), float(job["hours_per_s"]), float(job["seconds"]))
    if c == "replay":
        from . import compose as C
        tl = C.S("tl")
        return LS.Clock.from_timeline(tl, float(job["clock_v0"]), float(job["clock_v1"]))
    raise ValueError(c)


def view_at(job: dict, v: float) -> str:
    for a, b, name in job["views"]:
        if a <= v < b:
            return name
    return job["views"][-1][2]


def test_main():
    from . import data as D
    from . import lab3d_sched as LS
    Path("/tmp/vid").mkdir(exist_ok=True)
    lab = Lab3D()
    lab.kin = LS.load_kin() if (OUTD / "kin.json").exists() else lab.kinematics()
    clock = LS.Clock.linear(24 * 119, 2.8, 60.0)
    p = LS.plan(D.Replay(), lab.kin, clock)
    print(LS.summary(p), flush=True)
    from PIL import Image
    for name in sys.argv[2:] or ["high"]:
        lab.view(name)
        for v in (5.0, 12.0, 20.0):
            lab.apply(p.state(v))
            t0 = time.time()
            img = lab.render()
            print(f"{name} v={v}: {time.time() - t0:.2f} s", flush=True)
            Image.fromarray(img).save(f"/tmp/vid/lab3d_{name}_{v:04.1f}.png")


if __name__ == "__main__":
    cmd = sys.argv[1] if sys.argv[1:] else "test"
    if cmd == "kin":
        kin_main()
    elif cmd == "test":
        test_main()
    elif cmd == "render":
        render_job(json.loads(Path(sys.argv[2]).read_text()))
    else:
        raise SystemExit(__doc__)
