"""The birds-eye stills of the whole lab for the campaign video, rendered once (they hold no data), with every station's
anchor projected to the picture. twin/video/birdseye.py lights the stations over them from the event log in 2-D.

    cd vertical-lab
    /tmp/venv/bin/python runner_guard.py slot --mem 7500 --label birdseye -- \
        env VIZ3D_SIZE=2880x1620 xvfb-run -a /tmp/cqenv/bin/python -m twin.video.birdseye_render [view ...]

/tmp/cqenv is /tmp/venv plus cadquery 2.8.0 (lab_models needs it to tessellate): a venv of the same Python with a .pth
pointing at /tmp/venv's site-packages and `pip install cadquery` on top, because installing cadquery into /tmp/venv
itself would take its vtk from 9.7.2 down to 9.6.2 under every other render on the runner. First run 2026-11-25: 17 min
in one slot (983 s building the scene, nearly all of it the first tessellation, now cached in .cache/), 7-14 s a view,
peak RSS 3.7 GB.

-> out/twin2/video/birdseye/<view>.png (the still, no text) and <view>.json: {"size", "camera", "view_angle",
   "matrix" (world -> clip, 4x4, so anchors can be re-projected without a render), "anchors": {key: [x, y, depth]},
   "boxes": {key: [x0, y0, x1, y1]} (each machine's projected bounds), "world": {key: [x, y, z]}}.

The scene is the set-up movie's lab as timelapse.Movie builds it (setup_lab.build: both Shuttles see-through with every
tray loaded and home, the floor machines, the two MiR250 + UR12e units folded on their chargers), with no people, no
beacons and no overlay. Rendered at 2880 x 1620 so the video's pull-back from 1.5x to 1x is a crop, never an upscale.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[2]            # vertical-lab/
sys.path.insert(0, str(HERE))
OUTD = HERE / "out" / "twin2" / "video" / "birdseye"

# (position, focal point, view up), mm; the lab's floor machines span x -7300 (glovebox) .. 10050 (packaging), the north
# row's fronts at y -1562 and the south row's at -6238; the Shuttles are 9.15 m tall at x 0 and 3630.
VIEWS = {
    "high": [(1400.0, -25500.0, 23500.0), (1400.0, -3700.0, 700.0), (0.0, 0.0, 1.0)],
    "sw": [(-7200.0, -24000.0, 17500.0), (1300.0, -3700.0, 600.0), (0.0, 0.0, 1.0)],
    "se": [(10200.0, -24000.0, 17500.0), (1500.0, -3700.0, 600.0), (0.0, 0.0, 1.0)],
    "plan": [(1400.0, -9800.0, 34000.0), (1400.0, -3600.0, 0.0), (0.0, 0.0, 1.0)],
}
VIEW_ANGLE = 30.0


def build():
    import animate as A
    import lab
    import setup_lab as SL
    import vlm as V
    import warehouse as W
    data = lab.meshes()
    idata = SL.load_all()
    il = getattr(SL, "item_label", None)                # as timelapse.Movie: never let a mid-edit label stop the build
    if il is not None:
        def safe_label(inst, il=il):
            try:
                return il(inst)
            except Exception:                           # noqa: BLE001
                return getattr(inst, "model", "")
        SL.item_label = safe_label
    sc, L, F, items, rigs, units, util, _, vp = SL.build(data, idata, mp4=False, name="birdseye", title="")
    SL.add_bay_cams(sc)
    L.show_gauges = False
    L.skin(1.0)(1.0)                                    # see-through Shuttles, every tray showing, as in the set-up
    home = {k: [*V.SLOTS[A.HOME[k]]] for k in L.tray}
    for k in L.tray:
        L.tray[k] = list(home[k])
        L.where[k] = A.HOME[k]
    for sh in (1, 2):
        L.use(sh)
        L.lift_z = A.LIFT_HOME
    L.use(1)
    L.apply_state()
    q_park = np.radians(A.PARK_DEG)
    for i, uu in enumerate(units):
        uu.set(W.charger_pose(i))
        uu.robot.set(q_park)
    sc.title, sc.caption, sc.label, sc.labels = "", "", "", []
    return sc, L, F, V, W, SL, A


def anchors_world(sc, L, F, V, W, SL, A) -> tuple[dict, dict]:
    """{key: (x, y, z) world anchor} and {key: bounds (x0, x1, y0, y1, z0, z1)} for every floor machine group, each
    Shuttle's opening, the chargers and each tray at home and at its Shuttle's opening."""
    import timelapse as TL
    pts, bnds = {}, {}
    for key, names in F.groups.items():
        if not names or key in ("tape", "docks", "racking"):
            continue
        try:
            b = SL._bounds_of(sc, names)
        except Exception:                               # noqa: BLE001
            b = None
        if b is None or not np.isfinite(np.array(b, float)).all():
            continue
        b = tuple(float(v) for v in b)
        bnds[key] = b
        pts[key] = ((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, b[5])
    for sh in (1, 2):
        x0 = float(V.SHUTTLE_X[sh])
        yo, zo = V.SLOTS["open"]
        pts[f"open{sh}"] = (x0, float(yo) - 300.0, float(zo) + 500.0)
        pts[f"top{sh}"] = (x0, 0.0, float(V.UNIT_H))
    for i in range(len(W.CHARGERS)):
        cx, cy, _ = W.charger_pose(i)
        pts[f"charger{i + 1}"] = (float(cx), float(cy), 700.0)
    shut = TL._shuttles()
    by_sh: dict = {}
    for k in sorted(L.tray):
        by_sh.setdefault(shut.get(k, 1), []).append(k)
    for sh, ks in by_sh.items():
        x0 = float(V.SHUTTLE_X[sh])
        yo, zo = V.SLOTS["open"]
        n = len(ks)
        for j, k in enumerate(ks):                       # spread along the opening's width (2.45 m tray)
            dx = (j - (n - 1) / 2) * min(260.0, 2200.0 / max(1, n))
            pts[f"tray_{k}"] = (x0 + dx, float(yo) - 300.0, float(zo) + 500.0)
    for k in sorted(L.tray):                             # each tray where it stands, at home in its slot
        names = sc.members(f"tray_{k}")
        b = SL._bounds_of(sc, names) if names else None
        if b is not None and np.isfinite(np.array(b, float)).all():
            b = tuple(float(v) for v in b)
            bnds[f"slot_{k}"] = b
            pts[f"slot_{k}"] = ((b[0] + b[1]) / 2, b[2] + 120.0, (b[4] + b[5]) / 2)
    return pts, bnds


def project_all(sc, size, pts: dict, bnds: dict) -> tuple[dict, dict, list]:
    ren = sc.pl.renderer
    cam = ren.GetActiveCamera()
    aspect = size[0] / size[1]
    M = cam.GetCompositeProjectionTransformMatrix(aspect, -1.0, 1.0)
    mat = [[M.GetElement(i, j) for j in range(4)] for i in range(4)]
    out, boxes = {}, {}
    for key, p in pts.items():
        ren.SetWorldPoint(float(p[0]), float(p[1]), float(p[2]), 1.0)
        ren.WorldToDisplay()
        dx, dy, dz = ren.GetDisplayPoint()
        out[key] = [round(dx, 1), round(size[1] - dy, 1), round(dz, 5)]
    for key, b in bnds.items():
        xs, ys = [], []
        for x in b[:2]:
            for y in b[2:4]:
                for z in b[4:]:
                    ren.SetWorldPoint(x, y, z, 1.0)
                    ren.WorldToDisplay()
                    dx, dy, _ = ren.GetDisplayPoint()
                    xs.append(dx)
                    ys.append(size[1] - dy)
        boxes[key] = [round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1)]
    return out, boxes, mat


def main(views=None):
    from PIL import Image
    t0 = time.time()
    OUTD.mkdir(parents=True, exist_ok=True)
    sc, L, F, V, W, SL, A = build()
    print(f"built in {time.time() - t0:.0f} s; floor groups: {sorted(k for k, v in F.groups.items() if v)}",
          flush=True)
    pts, bnds = anchors_world(sc, L, F, V, W, SL, A)
    size = tuple(int(v) for v in sc.size)
    for name in views or list(VIEWS):
        t1 = time.time()
        sc.cam = [tuple(v) for v in VIEWS[name]]
        sc.view_angle = VIEW_ANGLE
        sc._clip_n = 0                                   # the first frame of a view goes through pyvista's setter
        img = sc.render_base()
        Image.fromarray(img[:, :, :3]).save(OUTD / f"{name}.png", optimize=False)
        anc, boxes, mat = project_all(sc, size, pts, bnds)
        (OUTD / f"{name}.json").write_text(json.dumps(dict(
            size=list(size), camera=[list(v) for v in VIEWS[name]], view_angle=VIEW_ANGLE, matrix=mat,
            anchors=anc, boxes=boxes, world={k: [round(v, 1) for v in p] for k, p in pts.items()},
            bounds={k: [round(v, 1) for v in b] for k, b in bnds.items()}), indent=1) + "\n")
        print(f"{name}: {time.time() - t1:.1f} s", flush=True)
    try:
        import resource
        print(f"peak RSS {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.0f} MB", flush=True)
    except Exception:                                   # noqa: BLE001
        pass
    print(f"done in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
