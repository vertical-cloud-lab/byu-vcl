#!/usr/bin/env python3
"""Shaded renders of deck_clip_key_v2_1_tri and of vial_rack_9x20mL_v2_tri's key pocket.

    python cad/render_tri.py      # writes ../img/deck_clip_key_tri.png

A small z-buffer rasterizer (orthographic, flat-shaded), so faces hide each other properly, which
matplotlib's 3D axes don't do. Needs trimesh, numpy and matplotlib.
"""
import math
import pathlib

import numpy as np
import trimesh
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

V2 = pathlib.Path(__file__).resolve().parent.parent
INK, INK2, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
KEY_RGB, RACK_RGB = np.array([0.92, 0.41, 0.20]), np.array([0.16, 0.47, 0.84])   # palette slots 2 and 1
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": INK})


def view_matrix(elev, azim):
    """Rows: screen x, screen y, toward the viewer (matplotlib's elev/azim convention)."""
    e, a = math.radians(elev), math.radians(azim)
    fwd = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])   # toward the viewer
    up = np.array([0.0, 0.0, 1.0])
    right = np.cross(up, fwd)
    if np.linalg.norm(right) < 1e-9:
        right = np.array([1.0, 0.0, 0.0])
    right /= np.linalg.norm(right)
    upv = np.cross(fwd, right)
    return np.vstack([right, upv, fwd])


def render(mesh, elev, azim, rgb, px=560, pad=0.06):
    M = view_matrix(elev, azim)
    v = mesh.vertices @ M.T
    lo, hi = v[:, :2].min(axis=0), v[:, :2].max(axis=0)
    span = (hi - lo).max() * (1 + 2 * pad)
    c = (lo + hi) / 2
    s = px / span
    sx = (v[:, 0] - c[0]) * s + px / 2
    sy = px / 2 - (v[:, 1] - c[1]) * s
    sz = v[:, 2]
    n = mesh.face_normals @ M.T
    light = np.array([-0.35, 0.55, 0.76])
    light /= np.linalg.norm(light)
    shade = 0.30 + 0.70 * np.clip(n @ light, 0, 1) + 0.12 * np.clip(n[:, 2], 0, 1)
    zbuf = np.full((px, px), -np.inf)
    img = np.ones((px, px, 3)) * np.array([0.988, 0.988, 0.984])
    F = mesh.faces
    for f, sh in zip(F, shade):
        x, y, z = sx[f], sy[f], sz[f]
        x0, x1 = max(int(math.floor(x.min())), 0), min(int(math.ceil(x.max())), px - 1)
        y0, y1 = max(int(math.floor(y.min())), 0), min(int(math.ceil(y.max())), px - 1)
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        d = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
        if abs(d) < 1e-12:
            continue
        w0 = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / d
        w1 = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / d
        w2 = 1 - w0 - w1
        inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not inside.any():
            continue
        zz = w0 * z[0] + w1 * z[1] + w2 * z[2]
        sub = zbuf[y0:y1 + 1, x0:x1 + 1]
        upd = inside & (zz > sub)
        sub[upd] = zz[upd]
        img[y0:y1 + 1, x0:x1 + 1][upd] = np.clip(rgb * sh, 0, 1)
    # dark outline where depth jumps, so edges read
    edge = np.zeros((px, px), bool)
    fin = np.isfinite(zbuf)
    zb = np.where(fin, zbuf, zbuf[fin].min() - 50 if fin.any() else 0)
    edge[1:, :] |= np.abs(np.diff(zb, axis=0)) > 0.6
    edge[:, 1:] |= np.abs(np.diff(zb, axis=1)) > 0.6
    img[edge] = img[edge] * 0.45
    return img


key = trimesh.load(V2 / "stl" / "deck_clip_key_v2_1_tri.stl")
rack = trimesh.load(V2 / "stl" / "vial_rack_9x20mL_v2_tri.stl")
end = rack.slice_plane([0, -16.5, 0], [0, 1, 0], cap=True).slice_plane([0, 0, 8.0], [0, 0, -1], cap=True)

views = ((key, 50, -90, KEY_RGB, "Key from above, −y end nearest: the nub points\nat you; the dimple (0.05 mm press) is at the far end"),
         (key, -30, -60, KEY_RGB, "Key from below: the two barbed latch arms,\nunchanged from v2_1"),
         (key, 0, 0, KEY_RGB, "Key from the side (+x): the 2.0 mm nub over\nthe pill; z = 0 is the deck top"),
         (end, -55, -70, RACK_RGB, "Rack from below, at vial 1: the 2.1 mm\ntriangular pocket (vial 7 has the other)"))
fig, axs = plt.subplots(1, 4, figsize=(15.5, 5.0), dpi=110)
fig.patch.set_facecolor(SURF)
for ax, (m, e, a, rgb, title) in zip(axs, views):
    ax.imshow(render(m, e, a, rgb), interpolation="lanczos")
    ax.set_axis_off()
    ax.set_title(title, fontsize=10, color=INK, loc="left")
fig.suptitle("deck_clip_key_v2_1_tri and vial_rack_9x20mL_v2_tri", x=0.01, y=0.985, ha="left", fontsize=13,
             fontweight="bold", color=INK)
fig.text(0.01, 0.025, "Rendered from the STLs by cad/render_tri.py. The key prints as drawn, nub up; the rack prints "
         "bottom down, so its pockets open onto the bed.", fontsize=9, color=INK2)
fig.subplots_adjust(left=0.01, right=0.99, top=0.83, bottom=0.07, wspace=0.04)
fig.savefig(V2 / "img" / "deck_clip_key_tri.png", facecolor=SURF)
print("wrote img/deck_clip_key_tri.png")
