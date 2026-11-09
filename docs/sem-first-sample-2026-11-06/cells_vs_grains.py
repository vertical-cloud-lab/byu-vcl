"""Sketch of cells vs grains in LPBF AlSi10Mg, next to Ronnie's 35,000x image
of the first diamond-polished sample (Apreo, ETD, 5 kV, 2026-11-06), for PR 258.

    pip install pillow numpy scipy scikit-image matplotlib
    python docs/sem-first-sample-2026-11-06/cells_vs_grains.py

The original (6144 x 4376 JPEG, data bar included) is fetched from the PR
comment's attachment into /tmp/sem-dl/ if it is not already there.
(a)-(c) are schematic and not to scale.
"""
import os
import urllib.request

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patheffects as pe
from matplotlib.patches import Polygon

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
AID, HFW_UM = "98e04b8f-0dbe-491b-9067-528b064a5bf0", 11.8  # 35,000x image

W, H = 10.0, 7.0          # schematic panel, arbitrary units (1 unit ~ 0.5 um)
CELL = 1.05               # cell width
HW = 0.075                # half-width of a Si-rich wall
BETA = np.radians(20)     # grain 2: cells and atom rows turned 20 degrees
S = 0.17                  # atom spacing (hugely enlarged)
YS = np.linspace(0, H, 400)


def x_gb(y):
    return 5.25 - 0.10 * y + 0.12 * np.sin(0.9 * y)


# grain 1: near-vertical wavy walls
G1_X0 = [0.95, 2.0, 3.05, 4.1]
G1_PH = [0.0, 1.7, 3.1, 4.6]


def g1_wall(i, y):
    return G1_X0[i] + 0.10 * np.sin(2 * np.pi * y / 2.6 + G1_PH[i])


# grain 2: walls along d = (sin b, cos b), normal n = (cos b, -sin b)
D = np.array([np.sin(BETA), np.cos(BETA)])
N = np.array([np.cos(BETA), -np.sin(BETA)])
G2_C = np.arange(2.45, 10.0, CELL)


def g2_offset(i, t):
    return G2_C[i] + 0.10 * np.sin(2 * np.pi * t / 2.6 + 0.9 * i)


def grain_polys():
    left = np.vstack([[0, 0], np.c_[x_gb(YS), YS], [0, H]])
    right = np.vstack([np.c_[x_gb(YS), YS], [W, H], [W, 0]])
    return left, right


def wall_polys():
    """Polygons for every Si-rich wall, tagged by grain (1, 2) or 'gb'."""
    out = []
    for i in range(len(G1_X0)):
        x = g1_wall(i, YS)
        out.append((1, np.vstack([np.c_[x - HW, YS], np.c_[x + HW, YS][::-1]])))
    t = np.linspace(-3, 12, 500)
    for i in range(len(G2_C)):
        o = g2_offset(i, t)
        c = np.outer(o, N) + np.outer(t, D)
        out.append((2, np.vstack([c - HW * N, (c + HW * N)[::-1]])))
    x = x_gb(YS)
    out.append(("gb", np.vstack([np.c_[x - HW * 1.1, YS], np.c_[x + HW * 1.1, YS][::-1]])))
    return out


def atoms():
    m = 0.05
    ii, jj = np.meshgrid(np.arange(-20, 90), np.arange(-60, 90))
    # grain 1: square lattice, rows along x and y
    p1 = np.c_[ii.ravel() * S + 0.04, jj.ravel() * S + 0.06]
    keep = (p1[:, 0] > 0.05) & (p1[:, 1] > 0.05) & (p1[:, 1] < H - 0.05)
    keep &= p1[:, 0] < x_gb(p1[:, 1]) - HW * 1.1 - m
    for i in range(len(G1_X0)):
        keep &= np.abs(p1[:, 0] - g1_wall(i, p1[:, 1])) > HW + m
    p1 = p1[keep]
    # grain 2: same lattice turned by BETA, rows along D and N
    p2 = np.outer(ii.ravel() * S, N) + np.outer(jj.ravel() * S, D) + [0.02, 0.03]
    keep = (p2[:, 0] < W - 0.05) & (p2[:, 1] > 0.05) & (p2[:, 1] < H - 0.05)
    keep &= p2[:, 0] > x_gb(p2[:, 1]) + HW * 1.1 + m
    for i in range(len(G2_C)):
        keep &= np.abs(p2 @ N - g2_offset(i, p2 @ D)) > HW + m
    return p1, p2[keep]


def label(ax, xy, xytext, s, color="black", fs=10.5, **kw):
    ax.annotate(s, xy, xytext=xytext, fontsize=fs, color=color, ha=kw.pop("ha", "left"),
                va=kw.pop("va", "center"),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.3, shrinkA=2, shrinkB=1),
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.92), zorder=7, **kw)


def schematic(ax, mode):
    left, right = grain_polys()
    if mode == "real":
        fills, wall_c = ("#dceaf7", "#fde5cc"), "#3b3b3b"
    elif mode == "sem":
        fills, wall_c = ("#6b6b6b", "#6b6b6b"), "#ececec"
    else:  # ebsd
        fills, wall_c = ("#4e79a7", "#f28e2b"), None
    gp = []
    for poly, fc in zip((left, right), fills):
        p = Polygon(poly, closed=True, fc=fc, ec="none")
        ax.add_patch(p)
        gp.append(p)
    if wall_c:
        for tag, poly in wall_polys():
            w = Polygon(poly, closed=True, fc=wall_c, ec="none", zorder=3)
            ax.add_patch(w)
            if tag in (1, 2):
                w.set_clip_path(gp[tag - 1])
    if mode == "real":
        p1, p2 = atoms()
        ax.scatter(p1[:, 0], p1[:, 1], s=3.4, c="#1f4e79", lw=0, zorder=4)
        ax.scatter(p2[:, 0], p2[:, 1], s=3.4, c="#8a4b08", lw=0, zorder=4)
    if mode == "ebsd":
        ax.plot(x_gb(YS), YS, color="black", lw=2.2, zorder=4)
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])


def load35():
    path = f"/tmp/sem-dl/{AID}.jpg"
    if not os.path.exists(path):
        os.makedirs("/tmp/sem-dl", exist_ok=True)
        urllib.request.urlretrieve(f"https://github.com/user-attachments/assets/{AID}", path)
    a = np.asarray(Image.open(path).convert("L")).astype(float)[:4096]  # drop the data bar
    return a, HFW_UM / a.shape[1]


def main():
    fig, axs = plt.subplots(2, 2, figsize=(13.2, 9.6), dpi=110)

    ax = axs[0, 0]
    schematic(ax, "real")
    ax.set_title("(a) Inside the metal: two grains, each made of many cells", fontsize=11.5)
    ax.text(2.4, 6.55, "grain 1", ha="center", fontsize=12, weight="bold", color="#1f4e79",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85), zorder=6)
    ax.text(7.6, 6.55, "grain 2", ha="center", fontsize=12, weight="bold", color="#8a4b08",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85), zorder=6)
    y = 4.6
    label(ax, (g1_wall(1, y) + HW, y), (0.25, 5.65), "cell wall: Si-rich, but the atom\nrows line up on both sides of it")
    y = 1.3
    label(ax, (x_gb(y) + 0.1, y), (5.9, 0.55), "grain boundary: Si-rich too,\nbut the atom rows turn here")
    yb = 2.75
    xa, xb = g1_wall(1, yb) + HW, g1_wall(2, yb) - HW
    ax.annotate("", (xa, yb), (xb, yb), arrowprops=dict(arrowstyle="<->", color="black", lw=1.3), zorder=6)
    ax.text((xa + xb) / 2, yb - 0.32, "one cell\n~0.5 µm", ha="center", va="top", fontsize=9.5,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.88), zorder=6)

    ax = axs[0, 1]
    schematic(ax, "sem")
    ax.set_title("(b) What an SE or BSE image shows: just the Si-rich walls", fontsize=11.5)
    y = 3.9
    label(ax, (x_gb(y), y), (5.75, 6.3), "the grain boundary looks like any\nother wall. The only clue is that\nthe cells change direction, and\noften they barely do")

    ax = axs[1, 0]
    schematic(ax, "ebsd")
    ax.set_title("(c) What an EBSD map shows: one color per grain, no cells", fontsize=11.5)
    for x, s in ((2.4, "grain 1"), (7.6, "grain 2")):
        ax.text(x, 3.5, s, ha="center", va="center", fontsize=13, weight="bold", color="white")
    ax.text(5.0, 0.5, "EBSD maps which way the atom rows run.\nEvery cell in a grain shares that, so the cells vanish",
            ha="center", va="center", fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none"), zorder=6)

    ax = axs[1, 1]
    a, um = load35()
    x0, y0, x1, y1 = 300, 1500, 2600, 3100
    c = a[y0:y1, x0:x1]
    d = ndi.gaussian_filter(c, 2) - ndi.gaussian_filter(c, 150)
    lo, hi = np.percentile(d, [1, 99.7])
    e = np.clip((d - lo) / (hi - lo), 0, 1)
    ext = [0, c.shape[1] * um, c.shape[0] * um, 0]
    ax.imshow(e, cmap="gray", extent=ext)
    # label positions in um, picked on the stretched crop: a bright wall, and one
    # cell measured between the two walls either side of it, perpendicular to them
    # (the walls run at ~35 deg here; this cell is ~0.43 um across)
    wall_xy = (1.49, 0.63)
    c0, c1 = (1.675, 2.437), (1.920, 2.084)
    stroke = [pe.withStroke(linewidth=3, foreground="black")]
    ax.annotate("bright lines: the Si-rich walls in (b)", wall_xy, xytext=(wall_xy[0] - 0.9, 0.25),
                fontsize=10.5, color="#ffd166", va="center", path_effects=stroke,
                arrowprops=dict(arrowstyle="->", color="#ffd166", lw=1.6, shrinkB=2))
    ax.annotate("", c0, c1, arrowprops=dict(arrowstyle="<->", color="#ffd166", lw=2.0, shrinkA=0, shrinkB=0))
    ax.text(c0[0] - 0.06, c0[1] + 0.12, "one cell", fontsize=10.5, color="#ffd166", ha="right", va="center",
            path_effects=stroke)
    X, Y = ext[1] - 1.25, ext[2] - 0.22
    ax.plot([X, X + 1.0], [Y, Y], color="white", lw=4, solid_capstyle="butt",
            path_effects=[pe.Stroke(linewidth=6, foreground="black"), pe.Normal()])
    ax.text(X + 0.5, Y - 0.08, "1 µm", color="white", ha="center", va="bottom", fontsize=11,
            path_effects=[pe.withStroke(linewidth=3, foreground="black")])
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("(d) Your 35,000x image (ETD, 5 kV), a 4.4 µm crop, contrast stretched", fontsize=11.5)

    fig.text(0.5, 0.005, "(a)-(c) are sketches, not to scale: a real grain here is ~10 µm wide, about 20 cells across, "
             "and the atoms are drawn a few hundred times too big.", ha="center", fontsize=10, style="italic")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    out = os.path.join(HERE, "cells-vs-grains.png")
    fig.savefig(out, dpi=110)
    print("wrote", out)


if __name__ == "__main__":
    main()
