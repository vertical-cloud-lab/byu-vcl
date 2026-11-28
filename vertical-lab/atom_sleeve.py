"""How much of each arm goes into the powder, clip by clip: the length a cover for the dirty work has to be (#353).

Sterling on #353 (2026-11-19): "what about the arm getting powder on it, especially considering it's meant to do other
workflows across the plant. Should the cleaning tools have a whole sleeve that the arm fits into, sort of like a
shoulder length glove?" The answer starts from how far up the arm the powder actually reaches in the clips, so this
re-walks the clips' own arm paths (the planned joint moves the renders used) and measures, for every link of both
arms, how long it spends inside the chamber, and how long within 100 and 300 mm of the open door's hole, where the
dust comes out and settles (being near the chamber's closed walls doesn't count), and of the open furnace's top. The
answer is in notes/atom_sleeve.md.

    python3 runner_guard.py slot --label sleeve_vac -- xvfb-run -a python3 atom_sleeve.py record atom_vacuum
        runs the clip with ARM_AUDIT=1 (nothing is drawn) but swaps the per-frame collision checks for a recorder of
        each arm's joints, base pose, gripper and held part -> out/atom/sleeve/<clip>.json (VIZ3D_FPS=5 is plenty;
        a clip takes 1-3 min, nearly all of it the joint-move planning). The vacuum clip also rewrites
        out/atom/atom_vacuum_meta.json and out/collisions/atom_vacuum_hose.json at that rate: git checkout them after.
    python3 atom_sleeve.py analyse
        the per-link exposure of every recorded clip -> out/atom/sleeve/exposure.json and out/atom/sleeve_exposure.png

The chamber is the model's (repowder/model.py): the D-shaped housing x -115..350, y -120..120, z 420..1130 in the model
frame, its underside the 45 deg slope z = 650 - x, its right end round; the door's hole is 212 x 340 mm in its left
wall (x = -115). Distances are measured on the arm's own mesh (collide.py's decimated links and the 2F-85 with its
D405): its vertices and 6000 points spread over each link's surface (surface_points). Each frame's "reach" is the
distance back along the arm, from the grasp point, of the farthest such point in the zone (the flange is at 155 mm,
wrist 1 at 391, the elbow at 989, the shoulder at 1601).
"""
from __future__ import annotations

import json
import os
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTD = HERE / "out" / "atom" / "sleeve"
CLIPS = ("atom_container", "atom_vacuum", "atom_plate", "atom_crucible_out", "atom_crucible_in", "atom_bn",
         "atom_latch", "atom_cameras")


# ------------------------------------------------------------------------------------------------ record
class Recorder:
    """Stands in for collide.Auditor: a frame hook that keeps each arm's state, and the clip's save()."""

    def __init__(self, sc):
        self.sc = sc
        self.rows: list[dict] = []
        self.snap_frames: set = set()

    def __call__(self, sc):
        arms = []
        for rb in getattr(sc, "robots", []):
            arms.append(dict(p=rb.prefix, q=[round(float(v), 6) for v in rb.q], c=round(float(rb.close), 4),
                             W=[round(float(v), 3) for v in sc.world(rb.root).ravel()],
                             held=(rb.held[0] if rb.held else None)))
        self.rows.append(dict(n=sc.n, label=sc.label, arms=arms))

    def picture(self, sc):
        pass

    def save(self):
        import atom_base as AB
        from scene import FPS
        OUTD.mkdir(parents=True, exist_ok=True)
        out = dict(clip=self.sc.name, fps=FPS, n_frames=self.sc.n, rp=[float(v) for v in AB.RP],
                   substeps=self.sc.substeps, rows=self.rows)
        (OUTD / f"{self.sc.name}.json").write_text(json.dumps(out, separators=(",", ":")) + "\n")
        print(f"{self.sc.name}: {len(self.rows)} states over {self.sc.n} frames at {FPS} fps", flush=True)


def record(clip: str):
    os.environ["ARM_AUDIT"] = "1"
    os.environ.setdefault("VIZ3D_FPS", "5")
    sys.path.insert(0, str(HERE))
    import collide
    collide.Auditor = Recorder
    script, args = clip, []
    if clip.startswith("atom_crucible_"):          # one script, two clips: atom_crucible.py out | in
        script, args = "atom_crucible", [clip.rsplit("_", 1)[1]]
    sys.argv = [str(HERE / f"{script}.py")] + args
    runpy.run_path(str(HERE / f"{script}.py"), run_name="__main__")


# ------------------------------------------------------------------------------------------------ analyse
def chamber_distance(p):
    """Distance (mm, >= 0; 0 inside) from model-frame points p (N x 3) to the chamber's inside, approximately: the
    flat-sided part as a box cut by the 45 deg underside, the round end as a cylinder. Exact enough at the 10 mm level
    for the margins used here."""
    import numpy as np
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    # box part, x -115..230
    dx = np.maximum(np.maximum(-115.0 - x, x - 230.0), 0.0)
    dy = np.maximum(np.abs(y) - 120.0, 0.0)
    dz = np.maximum(np.maximum(420.0 - z, z - 1130.0), 0.0)
    d_box = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
    # round end: a vertical cylinder of radius 120 about (230, 0), z 420..1130, x >= 230
    r = np.hypot(np.maximum(x - 230.0, 0.0), y)
    d_cyl = np.sqrt(np.maximum(r - 120.0, 0.0) ** 2 + np.maximum(230.0 - x, 0.0) ** 2 + dz ** 2)
    d = np.minimum(d_box, d_cyl)
    # the underside: z >= 650 - x; below it is outside, by its distance to the plane
    d_slope = np.maximum((650.0 - x - z) / np.sqrt(2.0), 0.0)
    return np.maximum(d, d_slope)


def door_distance(p):
    """Distance (mm) from model-frame points to the chamber door's opening: the 212 x 340 mm hole in the left wall
    (x = -115, y -106..106, z 775..1115), where the dust comes out when the door stands open."""
    import numpy as np
    dx = np.abs(p[:, 0] + 115.0)
    dy = np.maximum(np.abs(p[:, 1]) - 106.0, 0.0)
    dz = np.maximum(np.maximum(775.0 - p[:, 2], p[:, 2] - 1115.0), 0.0)
    return np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)


def furnace_distance(p):
    """Distance (mm) from model-frame points to the furnace with its lid open: 0 inside the body (r 135, z 1150 to
    1345), else the distance to its open top (the disc r <= 135 at z 1345), since its sides are closed. The crucible,
    its skull, the graphite and the BN."""
    import numpy as np
    r = np.hypot(p[:, 0], p[:, 1])
    inside = (r <= 135.0) & (p[:, 2] >= 1150.0) & (p[:, 2] <= 1345.0)
    d_top = np.sqrt(np.maximum(r - 135.0, 0.0) ** 2 + (p[:, 2] - 1345.0) ** 2)
    return np.where(inside, 0.0, d_top)


def zone_distance(p):
    """{zone: distance (mm)}: "chamber", 0 inside it; "door", 0 inside the chamber, else the distance to the open
    door's hole, where the powder comes out (the chamber's other walls are closed, so being near them doesn't count);
    "furnace", the bore with the lid open (graphite, BN and the skull, not the powder)."""
    import numpy as np
    ch = chamber_distance(p)
    return dict(chamber=ch, door=np.where(ch <= 0.0, 0.0, door_distance(p)), furnace=furnace_distance(p))


CATS = (("chamber", "chamber", 0.0), ("door100", "door", 100.0), ("door300", "door", 300.0),
        ("furnace100", "furnace", 100.0))
SUSTAINED_S = 2.0          # "sustained" reach: the depth up the arm that is passed for at least this long in a clip


SAMPLES = 6000             # points per link, spread over its surface (seeded)


def surface_points(geom):
    """{link: (points (N x 3), None)} spread evenly over each decimated mesh's surface. The decimated meshes keep
    vertices only where the shape needs them, so a long tube (the forearm, the upper arm) has them at its two ends and
    none along it: measuring on vertices alone missed the tubes' middles."""
    import numpy as np
    import trimesh
    out = {}
    for k, (v, f) in geom.items():
        m = trimesh.Trimesh(np.asarray(v, float), np.asarray(f, int), process=False)
        pts, _ = trimesh.sample.sample_surface(m, SAMPLES, seed=7)
        out[k] = (np.vstack([np.asarray(v, float), np.asarray(pts, float)]), None)
    return out


def chain_coords(links, grip):
    """For every vertex of every link (and of the gripper), its distance back along the arm from the fingertips (mm):
    the vertex projected on its link's axis (from the link's joint to the next joint, at q = 0), plus the lengths of
    the links between it and the TCP. 0 at the grasp point; about 1.85 m at the shoulder joint."""
    import numpy as np
    import ur_arm
    names = ["base", "shoulder", "upper_arm", "forearm", "wrist1", "wrist2", "wrist3"]
    F0 = ur_arm.fk("ur10e", np.zeros(6))
    P = [F0[n][:3, 3] for n in names] + [F0["tool0"][:3, 3]]
    s_at = [0.0] * len(P)
    s_at[-1] = float(ur_arm.TCP_MM)                      # tool0 (the flange): TCP_MM behind the grasp point
    for k in range(len(P) - 2, -1, -1):
        s_at[k] = s_at[k + 1] + float(np.linalg.norm(P[k + 1] - P[k]))
    out = {}
    for k, n in enumerate(names):
        v = links[n][0]
        vb = (F0[n][:3, :3] @ v.T).T + F0[n][:3, 3]
        a, b = P[k], P[k + 1]
        L = float(np.linalg.norm(b - a))
        t = np.clip(((vb - a) @ (b - a)) / (L * L), 0.0, 1.0) if L > 1e-6 else np.zeros(len(vb))
        out[n] = s_at[k + 1] + (1.0 - t) * L
    G = ur_arm.gripper_fk(1.0)
    for k in grip:
        v = grip[k][0]
        z = (G[k][:3, :3] @ v.T).T[:, 2] + G[k][2, 3]          # along the tool axis, from the flange
        out["gripper:" + k] = np.clip(float(ur_arm.TCP_MM) - z, 0.0, None)
    return out, dict(zip(names + ["tool0"], s_at))


def analyse():
    import numpy as np
    sys.path.insert(0, str(HERE))
    import collide
    import ur_arm
    links, grip = collide._arm_geometry("ur10e")
    links, grip = surface_points(links), surface_points(grip)
    names = list(collide.ARM_LINKS)
    S, s_joint = chain_coords(links, grip)
    report = {}
    for clip in CLIPS:
        f = OUTD / f"{clip}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text())
        fps, rp = d["fps"], np.asarray(d["rp"], float)
        rows = d["rows"]
        n_end = d["n_frames"]
        per = {}
        for i, row in enumerate(rows):
            dur = ((rows[i + 1]["n"] if i + 1 < len(rows) else n_end) - row["n"]) / fps
            for arm in row["arms"]:
                F = ur_arm.fk("ur10e", arm["q"])
                Wr = np.asarray(arm["W"], float).reshape(4, 4)
                rec = per.setdefault(arm["p"], dict(links={}, reach={c: [] for c, _, _ in CATS}))
                G = ur_arm.gripper_fk(arm["c"])
                Wt = Wr @ F["tool0"]
                parts = [(nm, Wr @ F[nm], links[nm][0], S[nm]) for nm in names]
                gpts = [((Wt @ G[k])[:3, :3] @ grip[k][0].T + (Wt @ G[k])[:3, 3:4]).T for k in grip]
                parts.append(("gripper", None, np.vstack(gpts), np.concatenate([S["gripper:" + k] for k in grip])))
                deepest = {c: 0.0 for c, _, _ in CATS}
                for nm, Wl, v, s in parts:
                    pts = v if Wl is None else (Wl[:3, :3] @ v.T).T + Wl[:3, 3]
                    dz = zone_distance(pts - rp)
                    r = rec["links"].setdefault(nm, dict(min_door_mm=1e9, min_furnace_mm=1e9,
                                                         **{f"s_{c}": 0.0 for c, _, _ in CATS}))
                    r["min_door_mm"] = min(r["min_door_mm"], float(dz["door"].min()))
                    r["min_furnace_mm"] = min(r["min_furnace_mm"], float(dz["furnace"].min()))
                    for c, key, m in CATS:
                        hit = dz[key] <= m
                        if hit.any():
                            r[f"s_{c}"] += dur
                            deepest[c] = max(deepest[c], float(s[hit].max()))
                for c, _, _ in CATS:
                    rec["reach"][c].append((round(deepest[c], 1), round(dur, 3), row["label"]))
        summary = {}
        for p, rec in per.items():
            for nm, r in rec["links"].items():
                for k in list(r):
                    r[k] = round(r[k], 1)
            rs = {}
            for m, lst in rec["reach"].items():
                arr = np.array([(a, b) for a, b, _ in lst]) if lst else np.zeros((0, 2))
                top = max(lst, key=lambda x: x[0]) if lst else (0.0, 0.0, "")
                order = np.argsort(-arr[:, 0]) if len(arr) else []
                acc, sus = 0.0, 0.0
                for k in order:
                    acc += arr[k, 1]
                    if acc >= SUSTAINED_S:
                        sus = float(arr[k, 0])
                        break
                rs[m] = dict(max_mm=round(float(arr[:, 0].max()), 0) if len(arr) else 0.0, at=top[2],
                             sustained_mm=round(sus, 0),
                             **{f"secs_over_{c}": round(float(arr[arr[:, 0] > c, 1].sum()), 1) if len(arr) else 0.0
                                for c in (300, 600, 900, 1200)})
            summary[p] = dict(links=rec["links"], reach=rs)
        report[clip] = dict(seconds=round(n_end / fps, 1), arms=summary)
    OUTD.mkdir(parents=True, exist_ok=True)
    out = dict(chain_mm={k: round(v, 1) for k, v in s_joint.items()},
               categories={c: f"{key} <= {m:g} mm" for c, key, m in CATS}, clips=report)
    (OUTD / "exposure.json").write_text(json.dumps(out, indent=1) + "\n")
    print("chain (mm back from the grasp point to each joint):", out["chain_mm"])
    for clip, r in report.items():
        print(f"\n{clip} ({r['seconds']} s)")
        for p, rec in r["arms"].items():
            line = "  ".join(f"{nm}:" + "/".join(f"{rec['links'][nm]['s_' + c]:.0f}" for c, _, _ in CATS) + "s"
                             for nm in ["gripper"] + names[::-1])
            print(f"  {p}: {line}")
            print(f"     reach (mm back from the TCP): " + "; ".join(
                f"{c}: max {v['max_mm']:.0f} ({v['at']}), {SUSTAINED_S:g} s {v['sustained_mm']:.0f}, >300 "
                f"{v['secs_over_300']} s, >900 {v['secs_over_900']} s" for c, v in rec["reach"].items()))
    return out

# ------------------------------------------------------------------------------------------------ figure
ROWS = (("atom_container", "ur", "door", "Brushing powder: arm 1, 420 mm brush"),
        ("atom_vacuum", "urB", "door", "Vacuum: arm 2, the EXP wand"),
        ("atom_plate", "urB", "door", "Plate swap: arm 2, at the open door"),
        ("atom_crucible_out", "urB", "door", "Crucible out: arm 2, the nut key"),
        ("atom_crucible_out", "ur", "furnace", "Crucible out: arm 1, open furnace"),
        ("atom_crucible_in", "ur", "furnace", "Rebuild: arm 1, open furnace"))


def figure():
    """out/atom/sleeve_exposure.png: per clip, how far back from the fingertips the arm is within 100 and 300 mm of
    the open door's hole (or inside the chamber), for at least SUSTAINED_S in total; the furnace rows use the open
    furnace's top instead. One hue, two steps (nearer is darker); joints marked."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    d = json.loads((OUTD / "exposure.json").read_text())
    chain = d["chain_mm"]
    surf, ink, ink2, grid = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
    near, far = "#1c5cab", "#86b6ef"
    fig, ax = plt.subplots(figsize=(13.5, 5.6), dpi=150)
    fig.patch.set_facecolor(surf)
    ax.set_facecolor(surf)
    for x in (chain["tool0"], chain["wrist2"], chain["wrist1"], chain["forearm"], chain["shoulder"]):
        ax.axvline(x, color=grid, lw=1.0, zorder=0)
    for name, x in (("gripper", chain["tool0"] / 2), ("wrists 3, 2, 1", (chain["tool0"] + chain["wrist1"]) / 2),
                    ("forearm", (chain["wrist1"] + chain["forearm"]) / 2), ("elbow", chain["forearm"]),
                    ("upper arm", (chain["forearm"] + chain["shoulder"]) / 2), ("shoulder", chain["shoulder"])):
        ax.text(x, len(ROWS) - 0.35, name, ha="center", va="bottom", fontsize=9, color=ink2)
    for i, (clip, arm, zone, title) in enumerate(ROWS):
        y = len(ROWS) - 1 - i
        rec = d["clips"][clip]["arms"][arm]
        k100, k300 = (("door100", "door300") if zone == "door" else ("furnace100", None))
        r100 = rec["reach"][k100]
        r300 = rec["reach"][k300] if k300 else None
        g = rec["links"]["gripper"]
        if r300 is not None and r300["sustained_mm"] > 0:
            ax.barh(y, r300["sustained_mm"], height=0.5, color=far, zorder=2)
        if r100["sustained_mm"] > 0:
            ax.barh(y, r100["sustained_mm"], height=0.5, color=near, zorder=3)
        mx = (r300 or r100)["max_mm"]
        if mx > 0:
            ax.plot([mx, mx], [y - 0.3, y + 0.3], color=ink2, lw=1.6, zorder=4)
        if zone == "door":
            txt = (f"gripper within 100 mm {g['s_door100']:.0f} s, within 300 mm {g['s_door300']:.0f} s"
                   if g["s_door300"] > 0 else "nothing within 300 mm: the key holds it 0.4-0.6 m out")
        else:
            txt = f"gripper within 100 mm of the open top {g['s_furnace100']:.0f} s"
        ax.text(1810, y, txt, va="center", ha="left", fontsize=9, color=ink2)
        ax.text(-30, y, title, va="center", ha="right", fontsize=9.5, color=ink)
    ax.set_xlim(0, 1800)
    ax.set_ylim(-0.6, len(ROWS) - 0.1)
    ax.set_yticks([])
    ax.set_xlabel("distance back along the arm from the grasp point (mm)", color=ink2, fontsize=9.5)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(grid)
    ax.tick_params(colors=ink2, labelsize=9)
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    fig.legend(handles=[Patch(color=near, label=f"within 100 mm of the open door's hole (furnace rows: its open top), "
                                                 f"for {SUSTAINED_S:g} s or more"),
                        Patch(color=far, label=f"within 300 mm of the open door's hole, {SUSTAINED_S:g} s or more"),
                        Line2D([], [], color=ink2, lw=1.6, label="deepest brief pass")],
               loc="lower center", ncol=3, frameon=False, fontsize=8.5, labelcolor=ink2)
    fig.suptitle("How far up the arm the powder reaches in the clips (their planned paths re-walked, nothing drawn)",
                 x=0.015, ha="left", fontsize=12, color=ink)
    fig.subplots_adjust(left=0.22, right=0.72, top=0.86, bottom=0.2)
    out = HERE / "out" / "atom" / "sleeve_exposure.png"
    fig.savefig(out, facecolor=surf)
    print("wrote", out)


# ------------------------------------------------------------------------------------------------ concept still
def concept(clip: str = "atom_plate", arm: str = "urB"):
    """out/atom/sleeve_concept_still.png: the arm at the open door in the clip's frame where its gripper is nearest the
    door's hole, drawn in the proposed sleeve. The sleeve is each covered link's convex hull grown 15 mm, see-through,
    from the changer to 150 mm below the shoulder joint, with the cuff there. A sketch of the idea, not a design: the
    tools the clip has in hand are not drawn."""
    import math
    import numpy as np
    import pyvista as pv
    import trimesh
    sys.path.insert(0, str(HERE))
    import atom_base as AB
    import collide
    import ur_arm
    from scene import R
    d = json.loads((OUTD / f"{clip}.json").read_text())
    rp = np.asarray(d["rp"], float)
    links, grip = collide._arm_geometry("ur10e")
    links, grip = surface_points(links), surface_points(grip)
    S, s_joint = chain_coords(links, grip)
    best, best_d = None, 1e9
    for row in d["rows"]:
        for a in row["arms"]:
            if a["p"] != arm:
                continue
            F = ur_arm.fk("ur10e", a["q"])
            Wt = np.asarray(a["W"], float).reshape(4, 4) @ F["tool0"]
            dd = float(door_distance((Wt[:3, 3] - rp)[None, :])[0])
            if dd < best_d:
                best, best_d = (row, a), dd
    row, a = best
    import scene
    scene.encoder = lambda *args, **kw: None       # a still only: no MP4 (and no ffmpeg needed), no GIF
    sc, ma, mb = AB.build("atom_sleeve_concept", "Vertical cloud lab: the arm in its sleeve for the powder work")
    sc.gif = False
    AB.set_joints(sc, door=1.0)
    for m, pre in ((ma, "ur"), (mb, "urB")):
        rec = next(x for x in row["arms"] if x["p"] == pre)
        W = np.asarray(rec["W"], float).reshape(4, 4)
        yaw = math.degrees(math.atan2(W[1, 0], W[0, 0]))
        Rz = R((0, 0, 1), yaw)[:3, :3]
        local = np.asarray(sc.gmat[m.rb.root], float)[:3, 3]
        off = Rz @ local
        m.set(W[0, 3] - off[0], W[1, 3] - off[1], yaw)
        m.rb.set(np.asarray(rec["q"], float), rec["c"])
        assert np.allclose(sc.world(m.rb.root), W, atol=0.5), "the MiR's pose doesn't reproduce the recorded arm base"
    W = np.asarray(a["W"], float).reshape(4, 4)
    F = ur_arm.fk("ur10e", a["q"])
    cut = s_joint["shoulder"] - 150.0
    fabric = (0.22, 0.27, 0.34)
    AB.mir_at(ma if arm == "urB" else mb, "right")      # the other unit out of the way of the view
    for nm in ("wrist3", "wrist2", "wrist1", "forearm", "upper_arm"):
        v = links[nm][0][S[nm] <= cut]
        Wl = W @ F[nm]
        pts = (Wl[:3, :3] @ v.T).T + Wl[:3, 3]
        h = trimesh.convex.convex_hull(pts)
        h = trimesh.Trimesh(h.vertices + h.vertex_normals * 15.0, h.faces)
        faces = np.hstack([np.full((len(h.faces), 1), 3), h.faces]).ravel()
        sc.add(f"sleeve {nm}", pv.PolyData(np.asarray(h.vertices), faces), fabric, "static", opacity=0.78)
    # the cuff: a ring round the sleeve's end on the upper arm, along the upper arm's axis
    Fu = W @ F["upper_arm"]
    Fe = W @ F["forearm"]
    Fw = W @ F["wrist1"]
    ax_u = Fe[:3, 3] - Fu[:3, 3]
    ax_u /= np.linalg.norm(ax_u)
    vu = links["upper_arm"][0]
    near = vu[np.abs(S["upper_arm"] - cut) < 20.0]
    c = ((Fu[:3, :3] @ near.T).T + Fu[:3, 3]).mean(axis=0) if len(near) else Fu[:3, 3]
    cuff = pv.Disc(center=c, inner=82.0, outer=104.0, normal=ax_u, c_res=48).extrude(ax_u * 40.0, capping=True)
    sc.add("sleeve cuff", cuff, (0.12, 0.12, 0.14), "static")
    Wt = W @ F["tool0"]
    base = W[:3, 3]
    at = (base + Wt[:3, 3]) / 2.0 + np.array([0.0, 0.0, 150.0])
    eye = at + np.array([450.0, -2700.0, 650.0])
    door_c = (sc.world(AB.g("door")) @ np.array([-123.0, 0.0, 945.0, 1.0]))[:3]
    sleeve_c = (Fe[:3, 3] + Fw[:3, 3]) / 2.0
    sc.step("1/1", "The arm in its sleeve at the open door (the plate clip's pose): a dissipative, bonded sleeve from the "
            "tool changer to the upper arm, and the atomizer's own gripper at its end, which never leaves the cell",
            0.2, None, hold=0.2, cam_to=[tuple(eye), tuple(at), (0, 0, 1)],
            labels=[("Sleeve: static-dissipative, bonded at both ends", tuple(sleeve_c), (0.04, 0.16)),
                    ("Cuff on the upper arm, below the shoulder", tuple(c), (0.04, 0.62)),
                    ("Tool changer, then the atomizer's own gripper", tuple(Wt[:3, 3]), (0.56, 0.12)),
                    ("The chamber's door, open", tuple(door_c), (0.62, 0.70))],
            still=True)
    sc.save()
    print("frame", row["n"], row["label"], "gripper to the door's hole", round(best_d), "mm")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "record":
        record(sys.argv[2])
    elif len(sys.argv) >= 2 and sys.argv[1] == "concept":
        concept(*sys.argv[2:4])
    elif len(sys.argv) >= 2 and sys.argv[1] == "analyse":
        analyse()
        figure()
    else:
        print(__doc__)
