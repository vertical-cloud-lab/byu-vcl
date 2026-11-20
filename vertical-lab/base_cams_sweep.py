#!/usr/bin/env python3
"""Where do the arms go, in their own MiR250's frame? The check behind the base cameras' places (notes/base_cameras.md).

Sterling (PR #318, 2026-11-20) asked for two or three cameras on each mobile base: one on either side and one higher
up on a rod or extrusion. Anything fixed to the base is inside the UR10e's reach (1300 mm, on an 800 x 580 mm base),
so the question is not whether the arm *could* hit a camera but whether it does in the work the clips show. This
runs a clip as ``ARM_AUDIT=1`` would (nothing drawn, every frame's update run), records every arm's joints and its
base's pose relative to the MiR it rides on, frame by frame, and then sweeps the arm's drawn meshes (links, 2F-85,
D405 and whatever it holds is left out: held parts are checked by the audit) through those frames in the MiR's own
frame:

    python3 base_cams_sweep.py record atom_latch.py [args]     # -> out/base_cams/sweep/<clip>.npz (no audit JSON)
    python3 base_cams_sweep.py analyse                         # -> out/base_cams/sweep.json and sweep.png

``analyse`` reports, for every camera part ``props.base_camera_parts()`` draws and for each clip, the arm's closest
approach (mm) over all frames, from a 10 mm voxel sweep of points sampled every 6 mm over the arm's surfaces. Run it
through ``runner_guard.py slot`` like any other scene. The joint moves are planned against the scene as it is drawn
(robot.py), so a camera the arm never comes near leaves every planned path as it was; ``ARM_AUDIT=1`` on the clip
with the cameras in place is the check that settles it.
"""
from __future__ import annotations

import json
import os
import runpy
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "base_cams"
SWEEP = OUT / "sweep"
VOX = 10.0                                   # mm
BOUNDS = np.array([[-1700.0, 1700.0], [-1600.0, 1900.0], [-50.0, 2600.0]])   # MiR frame: x, y, z


def _mir_group(sc, rb) -> str | None:
    """The group of the MiR an arm rides on: the arm's root's parent (alloy_atomize.Mir, animate.Lab._amr, ...)."""
    return sc.parent.get(rb.root)


def record(argv: list[str]) -> None:
    os.environ["ARM_AUDIT"] = "1"
    os.environ.setdefault("ARM_AUDIT_TAG", "sweep")
    script, args = argv[0], argv[1:]
    import collide
    import scene as S
    collide.Auditor.__call__ = lambda self, sc: None          # the sweep only; the clip's audit stays as committed
    collide.Auditor.save = lambda self: {}
    collide.Auditor.picture = lambda self, sc: None
    rows: dict[str, list] = {}
    meta: dict[str, dict] = {}
    names = {}

    def hook(sc):
        for rb in getattr(sc, "robots", ()):
            g = _mir_group(sc, rb)
            if g is None:
                continue
            Wm = sc.world(g)
            Wr = sc.world(rb.root)
            Rl = np.linalg.solve(Wm, Wr)               # the arm's base in the MiR's frame (fixed, but checked)
            key = f"{sc.name}:{rb.prefix}"
            names[key] = sc.name
            meta.setdefault(key, dict(scene=sc.name, prefix=rb.prefix, model=rb.model, mir_group=g))
            rows.setdefault(key, []).append(np.r_[sc.n, rb.q, rb.close, Rl[:3, :4].ravel()])

    orig_init = S.Scene.__init__

    def init(self, *a, **kw):
        orig_init(self, *a, **kw)
        self.frame_hooks.append(hook)
    S.Scene.__init__ = init
    t0 = time.time()
    sys.argv = [script] + args
    try:
        runpy.run_path(str(HERE / script), run_name="__main__")
    except SystemExit:
        pass
    SWEEP.mkdir(parents=True, exist_ok=True)
    tag = Path(script).stem + ("_" + "_".join(args) if args else "")
    arrs = {k.replace(":", "__"): np.array(v, float) for k, v in rows.items()}
    np.savez_compressed(SWEEP / f"{tag}.npz", **arrs)
    (SWEEP / f"{tag}.json").write_text(json.dumps(dict(script=script, args=args, seconds=round(time.time() - t0, 1),
                                                       arms=meta, frames={k: len(v) for k, v in rows.items()}),
                                                  indent=1) + "\n")
    print(f"sweep {tag}: {sum(len(v) for v in rows.values())} arm-frames, {len(rows)} arms, "
          f"{time.time() - t0:.0f} s -> {SWEEP / (tag + '.npz')}", flush=True)


# ------------------------------------------------------------------------------------------------ analysis
def _surface_points(mesh, step: float = 6.0) -> np.ndarray:
    """Points over a mesh's triangles, about `step` mm apart (vertices included)."""
    import pyvista as pv
    m = pv.wrap(mesh).triangulate()
    v = np.asarray(m.points, float)
    f = np.asarray(m.faces).reshape(-1, 4)[:, 1:]
    out = [v]
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    n = np.ceil(area / (step * step * 0.5)).astype(int)
    big = n > 1
    if big.any():
        rng = np.random.default_rng(0)
        idx = np.repeat(np.nonzero(big)[0], n[big])
        r1, r2 = rng.random(len(idx)), rng.random(len(idx))
        s = np.sqrt(r1)
        out.append(a[idx] * (1 - s)[:, None] + b[idx] * (s * (1 - r2))[:, None] + c[idx] * (s * r2)[:, None])
    return np.vstack(out)


def _arm_points(model: str) -> dict:
    """{body: points in that body's frame}: the seven links and the gripper (2F-85 parts and the D405) on tool0."""
    import ur_arm
    pts = {}
    for link, lst in ur_arm.arm_meshes(model).items():
        pts[link] = np.vstack([_surface_points(m) for m, _, _ in lst])
    return pts


def _gripper_points(close: float) -> np.ndarray:
    import ur_arm
    G = ur_arm.gripper_fk(close)
    out = []
    for part, lst in ur_arm.gripper_meshes().items():
        for m, _, _ in lst:
            p = _surface_points(m)
            out.append(p @ G[part][:3, :3].T + G[part][:3, 3])
    return np.vstack(out)


def _dedup(p: np.ndarray, step: float) -> np.ndarray:
    """One point per `step` mm voxel."""
    k = np.floor(p / step).astype(np.int64)
    _, idx = np.unique(k, axis=0, return_index=True)
    return p[np.sort(idx)]


def _frames(data, key):
    """(frame numbers, q (N x 6), close (N,), the arm base in its MiR's frame (N x 4 x 4)) for one arm's rows."""
    r = data[key]
    Rl = np.tile(np.eye(4), (len(r), 1, 1))
    Rl[:, :3, :4] = r[:, 8:20].reshape(-1, 3, 4)
    return r[:, 0].astype(int), r[:, 1:7], r[:, 7], Rl


def sweep_grid(npz: Path, every: int = 1, step: float = 6.0, chunk: int = 150) -> tuple[np.ndarray, dict]:
    """A boolean voxel grid (MiR frame, VOX mm) of everything the arm's surfaces passed through in a clip (points one
    per `step` mm voxel of the links, the 2F-85 and the D405), and {arm: frames}."""
    import ur_arm
    data = np.load(npz)
    shape = tuple(int(np.ceil((hi - lo) / VOX)) for lo, hi in BOUNDS)
    grid = np.zeros(shape, bool)
    info = {}
    arm = {k: _dedup(v, step) for k, v in _arm_points("ur10e").items()}
    grip = _dedup(_gripper_points(0.5), step)
    for key in data.files:
        fr, Q, _, Rl = _frames(data, key)
        Q, Rl = Q[::every], Rl[::every]
        for a in range(0, len(Q), chunk):
            fks = [ur_arm.fk("ur10e", q) for q in Q[a:a + chunk]]
            Rc = Rl[a:a + chunk]
            for l, pts in list(arm.items()) + [("tool0", grip)]:
                Ms = np.stack([Rc[i] @ fks[i][l] for i in range(len(fks))])
                W = (np.einsum("tij,nj->tni", Ms[:, :3, :3], pts) + Ms[:, None, :3, 3]).reshape(-1, 3)
                ijk = np.floor((W - BOUNDS[:, 0]) / VOX).astype(int)
                ok = np.all((ijk >= 0) & (ijk < np.array(shape)), axis=1)
                ijk = ijk[ok]
                grid[ijk[:, 0], ijk[:, 1], ijk[:, 2]] = True
        info[key] = len(Q)
    return grid, info


def clearance(grid: np.ndarray, pts: np.ndarray) -> float:
    """The smallest distance (mm) from any of `pts` (MiR frame) to a swept voxel's centre, less half a voxel."""
    from scipy.ndimage import distance_transform_edt
    if not grid.any():
        return float("inf")
    dist = distance_transform_edt(~grid, sampling=VOX)
    ijk = np.floor((pts - BOUNDS[:, 0]) / VOX).astype(int)
    ijk = np.clip(ijk, 0, np.array(grid.shape) - 1)
    return float(max(0.0, dist[ijk[:, 0], ijk[:, 1], ijk[:, 2]].min() - VOX / 2))


def analyse() -> dict:
    import props as P
    parts = P.base_camera_parts()
    ppts = {name: _surface_points(mesh, 5.0) for name, (mesh, _) in parts.items()}
    rep = dict(method=f"every frame of each clip run as ARM_AUDIT=1 (base_cams_sweep.py record); the UR10e's links "
                      f"and its gripper (2F-85 and D405) as points every 6 mm over their drawn surfaces, put in the "
                      f"MiR's frame and voxelised at {VOX:g} mm; clearance = distance from each camera part's surface "
                      f"to the nearest swept voxel's centre, less half a voxel (so a part at 0 may touch)",
               clips={}, parts=list(parts))
    total = None
    for npz in sorted(SWEEP.glob("*.npz")):
        meta = json.loads(npz.with_suffix(".json").read_text())
        grid, info = sweep_grid(npz)
        total = grid if total is None else total | grid
        rep["clips"][npz.stem] = dict(arms=meta["arms"], frames=info, seconds_to_record=meta["seconds"],
                                      clearance_mm={k: round(clearance(grid, p), 0) for k, p in ppts.items()})
        print(npz.stem, rep["clips"][npz.stem]["clearance_mm"], flush=True)
    if total is not None:
        rep["all_clips_clearance_mm"] = {k: round(clearance(total, p), 0) for k, p in ppts.items()}
        np.savez_compressed(OUT / "sweep_union.npz", grid=total, bounds=BOUNDS, vox=VOX)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "sweep.json").write_text(json.dumps(rep, indent=1) + "\n")
    return rep


def _part_masks(margins=(0.0, 25.0), vox: float = 4.0) -> dict:
    """For each camera part, a fine voxel mask (MiR frame, `vox` mm) of everything within each margin of its surface:
    {part: (origin, shape, {margin: bool grid})}."""
    from scipy.ndimage import distance_transform_edt
    import props as P
    out = {}
    for name, (mesh, _) in P.base_camera_parts().items():
        pts = _surface_points(mesh, 2.0)
        m = max(margins) + 2 * vox
        lo = pts.min(0) - m
        shape = tuple(int(v) for v in np.ceil((pts.max(0) + m - lo) / vox) + 1)
        occ = np.zeros(shape, bool)
        ijk = np.floor((pts - lo) / vox).astype(int)
        occ[ijk[:, 0], ijk[:, 1], ijk[:, 2]] = True
        dist = distance_transform_edt(~occ, sampling=vox)
        out[name] = (lo, shape, {mg: dist <= mg + vox * 0.87 for mg in margins})
    return out


def conflicts(sweep_dir: Path | None = None, margins=(0.0, 25.0), step: float = 6.0, chunk: int = 150) -> dict:
    """Per clip and per camera part: the frames in which any point of an arm's surface (the arm on the same MiR)
    comes within each margin of the part. Margin 0 counts touching, to the 4 mm voxels and the 6 mm point spacing."""
    import ur_arm
    sweep_dir = sweep_dir or SWEEP
    masks = _part_masks(margins)
    arm = {k: _dedup(v, step) for k, v in _arm_points("ur10e").items()}
    grip = {c: _dedup(_gripper_points(c), step) for c in (0.0, 0.5, 1.0)}
    rep = dict(method=f"frames in which a point of the arm's drawn surface (links, 2F-85 and D405, one point per "
                      f"{step:g} mm voxel) falls within the margin of a camera part's surface (4 mm voxels), in the "
                      f"frame of the MiR the arm rides on; per clip and part. Held parts are not included",
               margins_mm=list(margins), clips={})
    for npz in sorted(Path(sweep_dir).glob("*.npz")):
        data = np.load(npz)
        res, first, nfr = {}, {}, 0
        for key in data.files:
            fr, Q, C, Rl = _frames(data, key)
            for a in range(0, len(fr), chunk):
                sl = slice(a, a + chunk)
                fks = [ur_arm.fk("ur10e", q) for q in Q[sl]]
                hit = {}
                bodies = [(np.stack([Rl[sl][i] @ fks[i][l] for i in range(len(fks))]), pts) for l, pts in arm.items()]
                for c, pts in grip.items():
                    sel = np.abs(C[sl] - c) == np.min([np.abs(C[sl] - cc) for cc in grip], axis=0)
                    Ms = np.stack([Rl[sl][i] @ fks[i]["tool0"] for i in range(len(fks))])
                    bodies.append((Ms, pts, sel))
                for b in bodies:
                    Ms, pts = b[0], b[1]
                    sel = b[2] if len(b) > 2 else np.ones(len(Ms), bool)
                    W = np.einsum("tij,nj->tni", Ms[:, :3, :3], pts) + Ms[:, None, :3, 3]
                    for p, (lo, shape, grids) in masks.items():
                        ijk = np.floor((W - lo) / 4.0).astype(int)
                        ok = np.all((ijk >= 0) & (ijk < np.array(shape)), axis=2)
                        if not ok.any():
                            continue
                        ii = np.where(ok, ijk[..., 0], 0)
                        jj = np.where(ok, ijk[..., 1], 0)
                        kk = np.where(ok, ijk[..., 2], 0)
                        for mg, gm in grids.items():
                            h = (gm[ii, jj, kk] & ok).any(axis=1) & sel
                            k = f"{p} <= {mg:g} mm"
                            hit[k] = hit.get(k, np.zeros(len(Ms), bool)) | h
                for k, h in hit.items():
                    res[k] = res.get(k, 0) + int(h.sum())
                    if h.any() and k not in first:
                        first[k] = (key.split("__")[-1], int(fr[sl][np.argmax(h)]))
            nfr += len(fr)
        rep["clips"][npz.stem] = dict(arm_frames=nfr, hits={k: v for k, v in res.items() if v}, first=first)
        print(npz.stem, nfr, {k: v for k, v in res.items() if v}, flush=True)
    tot = {}
    for c in rep["clips"].values():
        for k, v in c["hits"].items():
            tot[k] = tot.get(k, 0) + v
    rep["total"] = tot
    return rep


def figure(sweep_dir: Path | None = None) -> Path:
    """out/base_cams/sweep.png: seen from above, the lowest height over the cabinet top at which any clip's arm passed
    each spot of the base (blank: never below 1.9 m), the cabinet, the arm's base and the cameras' parts drawn on it;
    and the same seen from the back. From every recorded clip, 10 mm voxels."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    import props as P
    sweep_dir = Path(sweep_dir or SWEEP)
    union, names = None, []
    for npz in sorted(sweep_dir.glob("*.npz")):
        g, _ = sweep_grid(npz)
        union = g if union is None else union | g
        names.append(npz.stem)
    zc = BOUNDS[2, 0] + (np.arange(union.shape[2]) + 0.5) * VOX
    over = union & (zc > P.CAB_TOP + 5)[None, None, :]
    low = np.where(over.any(2), zc[np.argmax(over, axis=2)], np.nan)
    low[low > 1900] = np.nan
    x = BOUNDS[0, 0] + (np.arange(union.shape[0]) + 0.5) * VOX
    y = BOUNDS[1, 0] + (np.arange(union.shape[1]) + 0.5) * VOX
    fig, axs = plt.subplots(1, 2, figsize=(14.5, 6.4), gridspec_kw=dict(width_ratios=[1.25, 1]))
    ax = axs[0]
    im = ax.pcolormesh(x, y, low.T, cmap="viridis_r", vmin=P.CAB_TOP, vmax=1900, shading="auto")
    fig.colorbar(im, ax=ax, label="lowest height (mm) any clip's arm passed, over the cabinet top")
    L, Wd = P.MIR["L"], P.MIR["W"]
    ax.add_patch(Rectangle((-L / 2, -Wd / 2), L, Wd, fill=False, ec="k", lw=1.6, label="MiR250 footprint"))
    ax.add_patch(Rectangle((-P.CAB_X, -P.CAB_Y), 2 * P.CAB_X, 2 * P.CAB_Y, fill=False, ec="0.35", lw=1.0, ls="--",
                           label="cabinet"))
    import animate as A
    ax.add_patch(plt.Circle(A.ARM_LOCAL, 95, fill=False, ec="w", lw=1.4))
    ax.text(A.ARM_LOCAL[0], A.ARM_LOCAL[1] - 140, "arm base", color="w", ha="center", fontsize=9)
    colours = {"L": "#2a73d9", "R": "#ee8019", "M": "#279e4d"}
    for k in P.BASE_CAMS:
        g = P.base_camera_geometry(k)
        for part in ("post", "box"):
            b = g[part].bounds
            ax.add_patch(Rectangle((b[0], b[2]), b[1] - b[0], b[3] - b[2], fill=part == "post", fc=colours[k],
                                   ec=colours[k], lw=1.6, alpha=0.95))
        ax.text(g["box_centre"][0], g["box_centre"][1] + (60 if k != "M" else -95), f"{k}, {g['top']:.0f}",
                color=colours[k], ha="center", fontsize=10, weight="bold",
                bbox=dict(fc="w", ec="none", alpha=0.75, pad=1.5))
    ax.set_xlim(-560, 560)
    ax.set_ylim(-420, 900)
    ax.set_aspect("equal")
    ax.set_xlabel("x along the base (mm)")
    ax.set_ylabel("y across it (mm): +y is the station side")
    ax.set_title("From above: where the arms pass low over the base", fontsize=11)
    ax.legend(loc="upper left", fontsize=8)
    ax = axs[1]
    side = union[:, :, :].any(1)                       # seen along y: x against z
    ax.pcolormesh(x, zc, side.T, cmap="Greys", vmin=0, vmax=1.6, shading="auto")
    ax.add_patch(Rectangle((-L / 2, 0), L, P.MIR["H"], fill=True, fc="0.25", ec="k"))
    ax.add_patch(Rectangle((-P.CAB_X, P.MIR["H"]), 2 * P.CAB_X, P.CAB_H, fill=True, fc="0.8", ec="k"))
    for k in P.BASE_CAMS:
        g = P.base_camera_geometry(k)
        for part in ("post", "box"):
            b = g[part].bounds
            ax.add_patch(Rectangle((b[0], b[4]), b[1] - b[0], b[5] - b[4], fill=True, fc=colours[k], ec=colours[k]))
    ax.axhline(1800, color="#279e4d", lw=0.8, ls=":")
    ax.text(-1150, 1825, "1.8 m: the MiR250's 3D cameras see obstacles up to here", fontsize=8, color="#279e4d")
    ax.set_xlim(-1200, 1200)
    ax.set_ylim(0, 2400)
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("z (mm)")
    ax.set_title("Seen from the side: everywhere any arm went (grey)", fontsize=11)
    fig.suptitle(f"The arms' sweep over their own MiR250 in {len(names)} clips, and the base cameras", fontsize=12)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "sweep.png"
    fig.savefig(out, dpi=110)
    return out


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    if len(sys.argv) > 1 and sys.argv[1] == "figure":
        print(figure(Path(sys.argv[2]) if len(sys.argv) > 2 else None))
        raise SystemExit
    if len(sys.argv) > 2 and sys.argv[1] == "record":
        record(sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1] == "analyse":
        analyse()
    elif len(sys.argv) > 1 and sys.argv[1] == "conflicts":
        rep = conflicts(Path(sys.argv[2]) if len(sys.argv) > 2 else None)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "conflicts.json").write_text(json.dumps(rep, indent=1) + "\n")
    else:
        print(__doc__)
