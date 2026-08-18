"""Headless multi-view PNG renders of the exported STLs.

Usage: python render_views.py   (after running cad_model.py)

Uses trimesh + matplotlib so it runs on CI without OpenGL/X.
"""

from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = pathlib.Path(__file__).resolve().parent
STL_DIR = HERE / "stl"
RENDER_DIR = HERE / "renders"

VIEWS = {
    "iso": (30, -60),
    "front": (0, -90),
    "top": (90, -90),
}

COLOR = (0.35, 0.55, 0.80)


def render(stl_path: pathlib.Path) -> None:
    mesh = trimesh.load_mesh(stl_path)
    tris = mesh.vertices[mesh.faces]
    # simple lambertian shading from face normals
    light = np.array([0.4, -0.5, 0.75])
    light = light / np.linalg.norm(light)
    shade = np.clip(mesh.face_normals @ light, 0.15, 1.0)[:, None]
    colors = np.clip(shade * np.array(COLOR) + 0.18, 0, 1)

    lo, hi = mesh.bounds
    center = (lo + hi) / 2
    half = (hi - lo).max() / 2 * 1.05

    for view, (elev, azim) in VIEWS.items():
        fig = plt.figure(figsize=(8, 6), dpi=150)
        ax = fig.add_subplot(projection="3d")
        pc = Poly3DCollection(tris, facecolors=colors, edgecolor="none")
        ax.add_collection3d(pc)
        for setter, c in zip((ax.set_xlim, ax.set_ylim, ax.set_zlim), center):
            setter(c - half, c + half)
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()
        ax.set_box_aspect((1, 1, 1))
        fig.tight_layout(pad=0)
        out = RENDER_DIR / f"{stl_path.stem}_{view}.png"
        fig.savefig(out, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print("wrote", out.relative_to(HERE))


if __name__ == "__main__":
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for stl in sorted(STL_DIR.glob("*.stl")):
        render(stl)
