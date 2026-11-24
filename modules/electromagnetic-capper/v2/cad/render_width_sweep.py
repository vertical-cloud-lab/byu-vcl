#!/usr/bin/env python3
"""Renders and sections of the deck key width sweep (stl/width_sweep/).

    python cad/render_width_sweep.py      # writes ../img/deck_key_width_sweep.png

Top row: each stem key from above, -y end nearest, so its dimples face you.  Bottom left: the
widest key cut at y = 5 mm (through the stem, the pill, both latch arms and their barbs) in a
10 mm deck with a 10.5 mm slot.  Bottom right: the pill's +x flat for all four widths against
the slot wall, stretched sideways so the tenths of a millimetre show.  The rasterizer is
render_tri.py's.  Needs trimesh, shapely, numpy and matplotlib.
"""
import json
import math
import pathlib

import numpy as np
import trimesh
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon, Rectangle
from shapely.geometry import box

V2 = pathlib.Path(__file__).resolve().parent.parent
P = json.load(open(V2 / "cad" / "params.json"))
SLOT = P["slot_w_meas"]
INK, INK2, MUTED, SURF, DECK = "#0b0b0b", "#52514e", "#898781", "#fcfcfb", "#d6d5ce"
KEY_RGB = np.array([0.92, 0.41, 0.20])                     # categorical slot 2 (orange)
SEQ = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]           # blue ramp 250/400/550/700: wider = darker
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": INK,
                     "axes.edgecolor": MUTED, "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK2})


def view_matrix(elev, azim):
    e, a = math.radians(elev), math.radians(azim)
    fwd = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    right = np.cross([0.0, 0.0, 1.0], fwd)
    right /= np.linalg.norm(right)
    return np.vstack([right, np.cross(fwd, right), fwd])


def render(mesh, elev, azim, rgb, px=520, pad=0.06):
    """Orthographic, flat-shaded z-buffer render (as render_tri.py)."""
    M = view_matrix(elev, azim)
    v = mesh.vertices @ M.T
    lo, hi = v[:, :2].min(axis=0), v[:, :2].max(axis=0)
    span = (hi - lo).max() * (1 + 2 * pad)
    c = (lo + hi) / 2
    s = px / span
    sx, sy, sz = (v[:, 0] - c[0]) * s + px / 2, px / 2 - (v[:, 1] - c[1]) * s, v[:, 2]
    n = mesh.face_normals @ M.T
    light = np.array([-0.35, 0.55, 0.76]) / np.linalg.norm([-0.35, 0.55, 0.76])
    shade = 0.30 + 0.70 * np.clip(n @ light, 0, 1) + 0.12 * np.clip(n[:, 2], 0, 1)
    zbuf = np.full((px, px), -np.inf)
    img = np.ones((px, px, 3)) * np.array([0.988, 0.988, 0.984])
    for f, sh in zip(mesh.faces, shade):
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
    edge = np.zeros((px, px), bool)
    fin = np.isfinite(zbuf)
    zb = np.where(fin, zbuf, zbuf[fin].min() - 50)
    edge[1:, :] |= np.abs(np.diff(zb, axis=0)) > 0.3
    edge[:, 1:] |= np.abs(np.diff(zb, axis=1)) > 0.3
    img[edge] = img[edge] * 0.45
    return img


def xz_section(mesh, y):
    """Shapely polygons of the cut at this y, in (x, z)."""
    s = mesh.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0])
    T = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, y], [0, 0, 0, 1]], float)   # (x, y, z) -> (x, z, y0 - y)
    to2d = getattr(s, "to_2D", None) or s.to_planar
    return to2d(to_2D=T)[0].polygons_full


def draw_polys(ax, polys, **kw):
    for pg in polys:
        ax.add_patch(MplPolygon(np.array(pg.exterior.coords), closed=True, **kw))
        for r in pg.interiors:
            ax.add_patch(MplPolygon(np.array(r.coords), closed=True, facecolor=SURF, edgecolor=kw.get("edgecolor", "none"), lw=kw.get("lw", 0)))


keys = []
for i, c in enumerate(P["sweep_clear"]):
    w = round(SLOT - c, 3)
    keys.append((c, w, i + 1, trimesh.load(V2 / "stl" / "width_sweep" / f"deck_clip_key_v2_1_w{w:.1f}_c{c:.1f}.stl")))
base = trimesh.load(V2 / "stl" / "deck_clip_key_v2_1.stl")

fig = plt.figure(figsize=(15.5, 10.4), dpi=110)
fig.patch.set_facecolor(SURF)
gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 1.25], left=0.04, right=0.985, top=0.90, bottom=0.07, hspace=0.22, wspace=0.12)
for j, (c, w, n, m) in enumerate(keys):
    ax = fig.add_subplot(gs[0, j])
    ax.imshow(render(m, 52, -90, KEY_RGB), interpolation="lanczos")
    ax.set_axis_off()
    ax.set_title(f"{c:.1f} mm clearance\n{w:.1f} mm wide, {n} dimple{'s' * (n > 1)}", fontsize=11, color=INK, loc="left")

# bottom left: the widest key in the deck, cut through a barb
ax = fig.add_subplot(gs[1, 0:2])
yc = 5.0
DT = 10.0
for sgn in (1, -1):
    x0 = SLOT / 2 if sgn > 0 else -9.5
    ax.add_patch(Rectangle((x0, -DT), 9.5 - SLOT / 2, DT, facecolor=DECK, edgecolor=MUTED, lw=0.8, zorder=1))
draw_polys(ax, xz_section(keys[-1][3], yc), facecolor=KEY_RGB, edgecolor=INK, lw=0.6, alpha=0.95, zorder=2)
for pg in xz_section(base, yc):
    ax.plot(*np.array(pg.exterior.coords).T, color=INK2, lw=1.0, ls=(0, (3, 2)), zorder=3)
ax.set_xlim(-9.5, 9.5)
ax.set_ylim(-16.0, 6.0)
ax.set_aspect("equal")
ax.set_xlabel("x (mm), across the slot")
ax.set_ylabel("z (mm), 0 = deck top")
ax.set_title(f"The {keys[-1][1]:.1f} mm key (0 clearance) cut at y = {yc:.0f} mm, through a barb,\n"
             f"in a {SLOT} mm slot in a {DT:.0f} mm deck (Cubware's CAD; ours isn't\nmeasured). "
             "Dashed: v2_1, the 9.8 mm key", fontsize=10.5, color=INK, loc="left")
note = dict(fontsize=9, color=INK2)
ax.annotate("pill: the only part that changed,\nfull width for the top 5.65 mm", xy=(5.25, -2.5), xytext=(6.2, 3.4), arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8), **note)
ax.annotate("45° flare back to\nv2_1 at z = −6", xy=(5.05, -5.85), xytext=(6.2, -7.0), arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8), **note)
ax.annotate("latch arm and barb:\nv2_1's, unchanged", xy=(5.6, -10.6), xytext=(6.2, -14.2), arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8), **note)
ax.text(-9.2, -1.2, "deck", **note)
ax.text(-1.0, 3.2, "stem", **note)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)

# bottom right: the +x flat of each pill against the slot wall
ax = fig.add_subplot(gs[1, 2:4])
X0, X1 = 4.70, 5.80
win = box(X0, -7.2, X1, 0.6)
ax.add_patch(Rectangle((SLOT / 2, -DT), X1 - SLOT / 2, DT, facecolor=DECK, edgecolor=MUTED, lw=0.8, zorder=1))
ax.text(SLOT / 2 + 0.02, -6.95, "slot wall (deck)", **note)


def flat(m):
    parts = []
    for pg in xz_section(m, yc):
        g = pg.exterior.intersection(win)
        parts += list(getattr(g, "geoms", [g]))
    return [np.array(p.coords) for p in parts if p.length > 0]


for seg in flat(base):
    ax.plot(seg[:, 0], seg[:, 1], color=INK2, lw=1.4, ls=(0, (3, 2)), zorder=3)
ax.plot([], [], color=INK2, lw=1.4, ls=(0, (3, 2)), label="v2_1, 9.8 mm: 0.35 mm a side (what you have)")
for (c, w, n, m), col in zip(keys, SEQ):
    for seg in flat(m):
        ax.plot(seg[:, 0], seg[:, 1], color=col, lw=2.0, zorder=4)
    ax.plot([], [], color=col, lw=2.0, label=f"{w:.1f} mm: {c / 2:.2f} mm a side ({c:.1f} total), {n} dimple{'s' * (n > 1)}")
    ax.text(w / 2, 0.15, f"{w:.1f}", ha="center", va="bottom", fontsize=9, color=INK)
ax.text(4.9, 0.15, "9.8", ha="center", va="bottom", fontsize=9, color=INK2)
ax.set_xlim(X0, X1)
ax.set_ylim(-7.2, 0.9)
ax.set_xlabel("x (mm) from the key's centre line: half the width")
ax.set_ylabel("z (mm), 0 = deck top")
fig.canvas.draw()
bb = ax.get_window_extent()
stretch = (bb.width / (X1 - X0)) / (bb.height / (0.9 + 7.2))
ax.set_title(f"The pill's +x flat against the slot wall, at the same cut,\nstretched sideways ×{stretch:.0f} "
             "(so the 45° flare at z = −6 looks flat)", fontsize=10.5, color=INK, loc="left")
ax.grid(axis="x", color="#e1e0d9", lw=0.6)
ax.legend(loc="upper right", fontsize=8.6, frameon=True, facecolor=SURF, edgecolor="#e1e0d9", bbox_to_anchor=(1.0, 0.86))
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)

fig.suptitle("Deck key width sweep: 10.0, 10.2, 10.4 and 10.5 mm wide, all 24.8 mm long (stem tops shown; the _tri keys are "
             "the same below the top)", x=0.01, y=0.985, ha="left", fontsize=13, fontweight="bold", color=INK)
fig.text(0.01, 0.945, f"Slot taken as {SLOT} mm wide: Ben measured 0.7 mm of clearance on the 9.8 mm pill. Keys print as drawn, top up, so "
         "the pill is 9 mm above the bed and clear of elephant's foot. Rendered from the STLs by cad/render_width_sweep.py.",
         fontsize=9, color=INK2)
fig.savefig(V2 / "img" / "deck_key_width_sweep.png", facecolor=SURF)
print("wrote img/deck_key_width_sweep.png")
