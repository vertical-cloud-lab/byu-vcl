#!/usr/bin/env python3
"""How much bigger does the mount make the gripper? For reaching into tight spaces.

Compares three wrists: the bare gripper, the first version of this mount (commit f99bd07,
cameras flat on the tab), and the current one (camera pod set back and turned in). For each it
works out, as a function of depth behind the fingertips, how far the wrist reaches out from the
gripper axis on each side. The gripper's fingers are set 40 mm apart.

    python envelope.py      # -> ../renders/tight_spaces.png, ../exports/envelope.json

The first version's geometry comes from its own exported assembly in git history, so git must
be able to see commit f99bd07.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import cadquery as cq
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

import reference
from piper_mount import ASSEMBLY, FINGERTIP_Y, Params, build, place_tag_wedges

HERE = Path(__file__).resolve().parent
RENDERS = HERE.parent / "renders"
EXPORTS = HERE.parent / "exports"
OPENING = 40.0
FIRST_VERSION = "f99bd07"

INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
NEW, OLD, BARE = "#2a78d6", "#eb6834", "#b9b8b2"      # categorical slots 1 and 2; the bare gripper as context


def points(shapes, tol=0.3) -> list[np.ndarray]:
    """Triangles (n x 3 x 3) of each shape."""
    out = []
    for s in shapes:
        verts, tris = s.tessellate(tol, 0.3)
        v = np.array([(p.x, p.y, p.z) for p in verts])
        out.append(v[np.array(tris)])
    return out


def silhouette(tris: list[np.ndarray], axes=(0, 1)) -> Polygon:
    polys = []
    for t in tris:
        for tri in t:
            p = Polygon(tri[:, axes])
            if p.area > 1e-6:
                polys.append(p)
    return unary_union(polys).buffer(0.05).buffer(-0.05)


def profile(tris: list[np.ndarray], p: Params, depths: np.ndarray) -> dict[str, list[float]]:
    """For each depth d behind the fingertips: how far anything in front of that depth reaches
    from the gripper axis toward -X (the camera side), +X (the Pi side), and along Z."""
    v = np.concatenate([t.reshape(-1, 3) for t in tris])
    d = v[:, 1] - FINGERTIP_Y
    order = np.argsort(d)
    d, v = d[order], v[order]
    mx = np.maximum.accumulate(p.ax_x - v[:, 0])
    px = np.maximum.accumulate(v[:, 0] - p.ax_x)
    z = np.maximum.accumulate(np.abs(v[:, 2] - p.ax_z))
    idx = np.searchsorted(d, depths, side="right") - 1
    ok = idx >= 0
    res = {"camera side (-X)": [], "Pi side (+X)": [], "along the finger travel (Z)": []}
    for k, (i, good) in enumerate(zip(idx, ok)):
        res["camera side (-X)"].append(float(mx[i]) if good else 0.0)
        res["Pi side (+X)"].append(float(px[i]) if good else 0.0)
        res["along the finger travel (Z)"].append(float(z[i]) if good else 0.0)
    return res


def gripper_shapes() -> list:
    g = reference.gripper(OPENING, for_checks=False)
    return list(g["body"].val().Solids()) + list(g["fingers"].val().Solids())


def first_version_shapes() -> list:
    step = subprocess.run(["git", "show", f"{FIRST_VERSION}:piper-camera-mount/exports/assembly.step"],
                          capture_output=True, check=True, cwd=HERE).stdout
    with tempfile.NamedTemporaryFile(suffix=".step") as fh:
        fh.write(step)
        fh.flush()
        return list(cq.importers.importStep(fh.name).solids().vals())


def main() -> None:
    p = Params()
    parts = build(p)
    new = [s for n in ASSEMBLY for s in parts[n].val().Solids()]
    wedges = list(place_tag_wedges(p, OPENING).val().Solids())
    wrists = {"bare gripper": gripper_shapes(), "first version": first_version_shapes(), "this version": new}
    tris = {k: points(v) for k, v in wrists.items()}
    tris["first version"] += tris["bare gripper"]
    tris["this version, no tag wedges"] = tris["this version"] + tris["bare gripper"]
    tris["this version"] = tris["this version, no tag wedges"] + points(wedges)
    depths = np.arange(0.0, 145.5, 0.5)
    prof = {k: profile(t, p, depths) for k, t in tris.items()}

    def first_growth(name, side, over=1.0):
        a, b = np.array(prof[name][side]), np.array(prof["bare gripper"][side])
        i = np.argmax(a > b + over)
        return float(depths[i]) if (a > b + over).any() else None

    summary = {
        "fingers set to (mm)": OPENING,
        "depth behind the fingertips before the mount makes the wrist wider (mm)": {
            k: {side: first_growth(k, side) for side in ("camera side (-X)", "Pi side (+X)")}
            for k in ("first version", "this version, no tag wedges", "this version")},
        "furthest reach from the gripper axis (mm)": {
            k: {side: round(max(prof[k][side]), 1) for side in ("camera side (-X)", "Pi side (+X)",
                                                                 "along the finger travel (Z)")}
            for k in (*wrists, "this version, no tag wedges")},
    }
    wedge = np.array(prof["this version"]["camera side (-X)"]) - np.array(prof["bare gripper"]["camera side (-X)"])
    near = depths < 60
    summary["finger tag wedges: extra reach on the camera side within 60 mm of the fingertips (mm)"] = round(
        float(wedge[near].max()), 1)
    for k in ("first version", "this version"):
        summary["furthest reach from the gripper axis (mm)"][k]["overall width in X (mm)"] = round(
            max(prof[k]["camera side (-X)"]) + max(prof[k]["Pi side (+X)"]), 1)
    summary["furthest reach from the gripper axis (mm)"]["bare gripper"]["overall width in X (mm)"] = round(
        max(prof["bare gripper"]["camera side (-X)"]) + max(prof["bare gripper"]["Pi side (+X)"]), 1)
    (EXPORTS / "envelope.json").write_text(json.dumps({"summary": summary, "depth_mm": depths.tolist(),
                                                       "profiles": prof}, indent=1) + "\n")
    print(json.dumps(summary, indent=2))
    plot(p, tris, prof, depths, summary)


def plot(p, tris, prof, depths, summary) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                         "ytick.color": INK2, "text.color": INK, "axes.titlesize": 11, "axes.titleweight": "bold",
                         "axes.titlelocation": "left"})
    fig = plt.figure(figsize=(13, 6.4), dpi=150)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.0, 1.25], wspace=0.28)

    # (a) top view, fingertips at the bottom
    ax = fig.add_subplot(gs[0])
    sil = {k: silhouette(t, (0, 1)) for k, t in tris.items()}
    for geom, style in ((sil["bare gripper"], dict(fc=BARE, ec="none", zorder=1)),):
        for poly in getattr(geom, "geoms", [geom]):
            ax.fill(*np.array(poly.exterior.coords).T, **style)
    for k, col in (("first version", OLD), ("this version", NEW)):
        for poly in getattr(sil[k], "geoms", [sil[k]]):
            ax.plot(*np.array(poly.exterior.coords).T, color=col, lw=2, solid_joinstyle="round")
    ax.axhline(FINGERTIP_Y, color=INK2, lw=1)
    ax.text(p.ax_x + 70, FINGERTIP_Y + 2, "fingertips", color=INK2, fontsize=9, va="bottom", ha="right")
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm), camera side on the left")
    ax.set_ylabel("y (mm), toward the arm")
    ax.set_title("Seen from above")
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)

    # (b) looking back along the approach axis
    ax = fig.add_subplot(gs[1])
    sil = {k: silhouette(t, (0, 2)) for k, t in tris.items()}
    for poly in getattr(sil["bare gripper"], "geoms", [sil["bare gripper"]]):
        ax.fill(*np.array(poly.exterior.coords).T, fc=BARE, ec="none", zorder=1)
    for k, col in (("first version", OLD), ("this version", NEW)):
        for poly in getattr(sil[k], "geoms", [sil[k]]):
            ax.plot(*np.array(poly.exterior.coords).T, color=col, lw=2, solid_joinstyle="round")
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("z (mm), finger travel")
    ax.set_title("Looking along the approach")
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)

    # (c) reach toward the camera side vs depth
    ax = fig.add_subplot(gs[2])
    side = "camera side (-X)"
    ax.plot(depths, prof["bare gripper"][side], color=BARE, lw=2, label="bare gripper")
    ax.plot(depths, prof["first version"][side], color=OLD, lw=2, label="first version")
    ax.plot(depths, prof["this version"][side], color=NEW, lw=2, label="this version")
    for k, col in (("first version", OLD), ("this version, no tag wedges", NEW)):
        d0 = summary["depth behind the fingertips before the mount makes the wrist wider (mm)"][k][side]
        if d0 is not None:
            ax.axvline(d0, color=col, lw=1, ymax=0.08)
            ax.annotate(f"{d0:.0f} mm", (d0, 4), xytext=(4, 0), textcoords="offset points", fontsize=9,
                        color=INK2, va="bottom")
    ax.set_xlabel("depth behind the fingertips (mm)")
    ax.set_ylabel("reach from the gripper axis, camera side (mm)")
    ax.set_title("How deep before it gets wider")
    ax.set_xlim(0, depths[-1])
    ax.set_ylim(0, None)
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, loc="upper left")
    fig.suptitle("PiPER gripper with fingers 40 mm apart: bare (grey fill), first mount (orange), this mount (blue)",
                 x=0.01, ha="left", fontsize=12, color=INK)
    RENDERS.mkdir(exist_ok=True)
    fig.savefig(RENDERS / "tight_spaces.png", bbox_inches="tight", facecolor="#fcfcfb")
    plt.close(fig)


if __name__ == "__main__":
    main()
