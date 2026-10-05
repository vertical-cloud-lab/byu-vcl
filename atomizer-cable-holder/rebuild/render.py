#!/usr/bin/env python3
"""Draw the rebuilt profile over Onshape's sketch, and a shaded view of the STL, to render.png."""
from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import rebuild_from_features as R

SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
PART, SKETCH = "#2a78d6", "#eb6834"


def profile_faces():
    doc = json.loads(R.FEATURES.read_text())
    feats = {f["name"]: f for f in doc["features"]}
    curves = R.sketch_curves(feats["Sketch 1"])
    corners = {}
    for name, pairs in R.FILLETS.items():
        for a, b in pairs:
            v = next(p for p in (curves[a].p0, curves[a].p1) if R.close(p, curves[b].p0) or R.close(p, curves[b].p1))
            corners[v] = R.param(feats[name], "radius")
    faces = [R.face(R.fillet(R.loop(curves, names), corners)) for regions in R.REGIONS.values() for names in regions]
    return curves, faces


def main():
    curves, faces = profile_faces()
    summary = json.loads((R.HERE / "rebuild_summary.json").read_text())
    fig = plt.figure(figsize=(12, 5.6), facecolor=SURFACE)

    ax = fig.add_subplot(1, 2, 1, facecolor=SURFACE)
    for f in faces:
        pts = np.array([(v.x, v.z) for v in f.outerWire().positions(np.linspace(0, 1, 600))])
        ax.fill(pts[:, 0], pts[:, 1], color=PART, alpha=0.25, lw=0)
        ax.plot(pts[:, 0], pts[:, 1], color=PART, lw=1.6)
    for c in curves.values():
        pts = np.array(c.samples(48) + [c.p1])
        ax.plot(pts[:, 0], pts[:, 1], color=SKETCH, lw=1.0, ls=(0, (3, 2)))
    ax.plot([], [], color=PART, lw=1.6, label="rebuilt profile (fillets applied)")
    ax.plot([], [], color=SKETCH, lw=1.0, ls=(0, (3, 2)), label="Onshape sketch, as solved")
    op = summary["clip_opening_mm"]
    notes = [
        (0, 0, "strip 50 × 10 mm, 15 mm deep\n1 mm corner fillets", "center"),
        (-12.5, -10.5, "Ø11 mm\n1.6 mm wall\n10 mm deep", "center"),
        (12.5, -8.5, "Ø7\n1.0 wall\n5 deep", "center"),
    ]
    for x, y, text, ha in notes:
        ax.text(x, y, text, ha=ha, va="center", fontsize=8.5, color=INK, linespacing=1.25)
    ax.annotate(f"opening {op['11 mm clip']:.2f} mm", xy=(-12.5, -16.0), xytext=(-24, -24.5),
                fontsize=8.5, color=INK2, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    ax.annotate(f"opening {op['7 mm clip']:.2f} mm", xy=(12.5, -11.9), xytext=(16, -21),
                fontsize=8.5, color=INK2, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    ax.set_aspect("equal")
    ax.set_xlim(-27, 27)
    ax.set_ylim(-27, 7)
    ax.set_xlabel("X (mm)", color=INK2, fontsize=9)
    ax.set_ylabel("Z (mm)", color=INK2, fontsize=9)
    ax.tick_params(colors=INK2, labelsize=8)
    for s in ax.spines.values():
        s.set_color("#d6d5d0")
    ax.grid(color="#ebeae6", lw=0.6)
    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.12), ncol=2, frameon=False, fontsize=8.5, labelcolor=INK)
    ax.set_title("Front view: profile in the sketch plane", color=INK, fontsize=10.5, loc="left")

    mesh = trimesh.load(R.OUT.with_suffix(".stl"))
    ax3 = fig.add_subplot(1, 2, 2, projection="3d", facecolor=SURFACE)
    tris = mesh.vertices[mesh.faces]
    light = np.array([0.35, -0.75, 0.55])
    shade = 0.30 + 0.65 * np.clip(mesh.face_normals @ (light / np.linalg.norm(light)), 0, 1)
    base = np.array(matplotlib.colors.to_rgb(PART))
    colors = np.clip(base[None, :] * shade[:, None] + (1 - shade[:, None]) * 0.12, 0, 1)
    ax3.add_collection3d(Poly3DCollection(tris, facecolors=colors, edgecolors="none", linewidths=0))
    lo, hi = mesh.bounds
    mid, half = (lo + hi) / 2, (hi - lo).max() / 2
    ax3.set_xlim(mid[0] - half, mid[0] + half)
    ax3.set_ylim(mid[1] - half, mid[1] + half)
    ax3.set_zlim(mid[2] - half, mid[2] + half)
    ax3.set_box_aspect((1, 1, 1))
    ax3.view_init(elev=-28, azim=-58)
    ax3.set_axis_off()
    bb = summary["bbox_mm"]
    size = " × ".join(f"{hi - lo:.1f}" for lo, hi in bb.values())
    ax3.set_title(f"STL, from below: {size} mm, {summary['volume_mm3'] / 1000:.2f} cm³",
                  color=INK, fontsize=10.5, loc="left")

    fig.suptitle("Atomizer transducer cable holder, rebuilt from the Onshape feature list",
                 color=INK, fontsize=12, x=0.02, ha="left")
    fig.tight_layout()
    fig.savefig(R.HERE / "render.png", dpi=150, facecolor=SURFACE)


if __name__ == "__main__":
    main()
