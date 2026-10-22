#!/usr/bin/env python3
"""The deck key's nub against the base's key pocket: sizes in the model, in the STLs and in
the G-code the A1 mini ran on 2026-10-21, and a drawing of the fit (img/key_fit.png).

Both outlines are a rounded equilateral triangle: a sharp triangle of 3.1 mm circumradius,
one corner toward -Y, grown by the corner radius r. The pocket has r = 1.1 (Cubware's). The
key printed on 2026-10-21 had r = 1.0, 0.10 mm clear all round, and came out loose. The
key from 2026-10-22 has r = 1.2, 0.10 mm bigger than the pocket all round.

G-code sizes are the outer-wall toolpaths plus or minus half their line width (a pocket
wall's centreline runs half a line width into the material, a nub's half a line width in
from its edge).

    python analysis/key_fit.py    # prints the table in key_fit_output.txt, writes img/key_fit.png

Needs numpy, trimesh (with networkx), shapely and matplotlib.
"""

from __future__ import annotations

import math
import pathlib
import re
import zipfile
from collections import defaultdict

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent.parent
GCODE_3MF = HERE / "print" / "2026-10-21-a1mini" / "stir_module_parts.gcode.3mf"
TRI_R = 3.1          # sharp triangle's circumradius, mm
POCKET_R = 1.1       # pocket corner radius
OLD_R = 1.0          # key printed 2026-10-21
NEW_R = 1.2          # key from 2026-10-22 (keyPress 0.10)
CORNERS = (-90, 30, 150)   # corner directions, degrees; the flats face the opposite ways


def unit(a: float) -> np.ndarray:
    return np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])


def model(r: float) -> dict:
    """Caliper sizes of the rounded triangle with corner radius r."""
    side = TRI_R * math.sqrt(3)
    return {"corner_to_flat": 1.5 * TRI_R + 2 * r, "across_corners": side + 2 * r, "flat": side,
            "centre_to_flat": TRI_R / 2 + r, "centre_to_corner": TRI_R + r}


def sizes(pts: np.ndarray) -> tuple[list, list]:
    """Corner-to-opposite-flat and across-two-corners spans of a closed outline, three of each."""
    h = lambda a: float((pts @ unit(a)).max())
    return [h(c) + h(c + 180) for c in CORNERS], [h(c + 90) + h(c - 90) for c in CORNERS]


def outline(r: float, n: int = 60) -> np.ndarray:
    """Points round the rounded triangle (corner arcs joined by the flats)."""
    pts = []
    for c in CORNERS:
        v = TRI_R * unit(c)
        for a in np.linspace(c - 60, c + 60, n):
            pts.append(v + r * unit(a))
    pts.append(pts[0])
    return np.array(pts)


def stl_sizes() -> list:
    import trimesh

    rows = []

    def section(path, z):
        s = trimesh.load(path).section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        return s.to_planar(to_2D=np.eye(4))[0].polygons_full

    for pg in section(HERE / "stl" / "base.stl", 1.0):
        for ring in pg.interiors:
            pts = np.array(ring.coords)
            if abs(abs(pts[:, 0].mean()) - 12.5) < 2 and abs(pts[:, 1].mean()) < 3:
                rows.append((f"base.stl pocket at x = {pts[:, 0].mean():+.1f}, z = 1.0", *sizes(pts)))
    for name in ("deck_key.stl", "key_fit_test/deck_key_press_0.05.stl", "key_fit_test/deck_key_press_0.15.stl"):
        for z in (1.0, 1.95):
            pts = np.vstack([np.array(p.exterior.coords) for p in section(HERE / "stl" / name, z)])
            rows.append((f"{name} nub, z = {z}", *sizes(pts)))
    return rows


def gcode_sizes() -> list:
    """Outer-wall loops of the base's pockets and the keys' nubs in the G-code that was printed."""
    num = re.compile(r"([XYZEIJ])(-?\d*\.?\d+)")
    walls = defaultdict(list)          # (object, layer z) -> [(line width, x, y)]
    top = defaultdict(float)
    x = y = 0.0
    lz = obj = feat = lw = None
    with zipfile.ZipFile(GCODE_3MF) as z:
        text = z.read("Metadata/plate_1.gcode").decode()
    for line in text.splitlines():
        if line.startswith(";"):
            if line.startswith("; Z_HEIGHT:"):
                lz = float(line.split(":")[1])
            elif line.startswith("; start printing object, unique label id:"):
                obj = int(line.split(":")[1])
            elif line.startswith("; stop printing object"):
                obj = None
            elif line.startswith("; FEATURE:"):
                feat = line.split(":", 1)[1].strip()
            elif line.startswith("; LINE_WIDTH:"):
                lw = float(line.split(":")[1])
            continue
        s = line.split(";")[0].split()
        if not s or s[0] not in ("G0", "G1", "G2", "G3"):
            continue
        p = {k: float(v) for k, v in num.findall(" ".join(s[1:]))}
        nx, ny = p.get("X", x), p.get("Y", y)
        if obj is not None and p.get("E", 0) > 0 and (nx, ny) != (x, y):   # not a de-retraction on the spot
            top[obj] = max(top[obj], lz)
            if feat == "Outer wall":
                pts = [(nx, ny)]
                if s[0] in ("G2", "G3"):   # arcs: sample them
                    cx, cy = x + p.get("I", 0), y + p.get("J", 0)
                    a0, a1 = math.atan2(y - cy, x - cx), math.atan2(ny - cy, nx - cx)
                    if s[0] == "G2":
                        a1 = a1 - 2 * math.pi if a1 >= a0 else a1
                    else:
                        a1 = a1 + 2 * math.pi if a1 <= a0 else a1
                    rr = math.hypot(x - cx, y - cy)
                    pts = [(cx + rr * math.cos(a), cy + rr * math.sin(a)) for a in np.linspace(a0, a1, 24)]
                walls[(obj, lz)] += [(lw, px, py) for px, py in [(x, y)] + pts]
        x, y = nx, ny
    base = next(o for o, t in top.items() if abs(t - 20.0) < 0.01)
    keys = [o for o, t in top.items() if abs(t - 12.0) < 0.01]
    rows = []

    def loop_sizes(obj, zs, centre, sign):
        out = []
        for lz in zs:
            pts = np.array([(px, py) for (lw, px, py) in walls[(obj, lz)] if math.hypot(px - centre[0], py - centre[1]) < 5.5])
            lw = walls[(obj, lz)][0][0]
            hc, wc = sizes(pts)
            out.append((lz, [v + sign * lw for v in hc], [v + sign * lw for v in wc]))
        return out

    bpts = np.array([(px, py) for (o, lz), v in walls.items() if o == base for (_, px, py) in v])
    bc = (bpts.min(axis=0) + bpts.max(axis=0)) / 2
    zs = sorted(lz for (o, lz) in walls if o == base and lz <= 2.2)
    for sx in (-1, 1):
        res = loop_sizes(base, zs, (bc[0] + sx * 12.5, bc[1]), -1)
        rows.append((f"G-code base pocket {'-+'[sx > 0]}X, layer 1 (z 0.2)", *res[0][1:]))
        rows.append((f"G-code base pocket {'-+'[sx > 0]}X, layers 2-11 (z 0.4-2.2), mean",
                     list(np.mean([r[1] for r in res[1:]], axis=0)), list(np.mean([r[2] for r in res[1:]], axis=0))))
    for k in keys:
        kpts = np.array([(px, py) for (o, lz), v in walls.items() if o == k for (_, px, py) in v])
        kc = (kpts.min(axis=0) + kpts.max(axis=0)) / 2
        res = loop_sizes(k, sorted(lz for (o, lz) in walls if o == k and lz > 10.0), kc, +1)
        rows.append(("G-code key nub (z 10.2-12.0), mean", list(np.mean([r[1] for r in res], axis=0)),
                     list(np.mean([r[2] for r in res], axis=0))))
    return rows


def draw(out: pathlib.Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MPoly, Rectangle

    INK, INK2, MUTED, SURF, BASE = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#dcdad4"
    OLD, NEW = "#2a78d6", "#eb6834"      # categorical slots 1 and 2
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": INK})
    fig = plt.figure(figsize=(11, 6.0), dpi=110)
    fig.patch.set_facecolor(SURF)
    gs = fig.add_gridspec(2, 2, width_ratios=(1.0, 1.0), height_ratios=(1.0, 0.8), left=0.02, right=0.98,
                          top=0.86, bottom=0.10, wspace=0.06, hspace=0.12)
    ax, az, at = fig.add_subplot(gs[:, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 1])
    pocket, old, new = outline(POCKET_R), outline(OLD_R), outline(NEW_R)
    m = {k: model(r) for k, r in (("pocket", POCKET_R), ("old", OLD_R), ("new", NEW_R))}

    # left: the three outlines, to scale, with the two caliper sizes
    ax.set_facecolor(SURF)
    ax.add_patch(Rectangle((-5.6, -5.6), 11.2, 10.4, color=BASE, lw=0, zorder=0))
    ax.add_patch(MPoly(pocket, closed=True, fc=SURF, ec=INK, lw=1.4, zorder=1))
    ax.plot(old[:, 0], old[:, 1], color=OLD, lw=1.6, ls=(0, (4, 2)), zorder=2)
    ax.plot(new[:, 0], new[:, 1], color=NEW, lw=2.0, zorder=3)
    yb, yt = -(TRI_R + NEW_R), TRI_R / 2 + NEW_R
    xa = TRI_R * math.sqrt(3) / 2 + NEW_R
    ax.annotate("", (4.6, yb), (4.6, yt), arrowprops=dict(arrowstyle="<->", color=INK2, lw=1))
    for yy in (yb, yt):
        ax.plot([0.3, 4.8], [yy, yy], color=MUTED, lw=0.6, ls=":")
    ax.text(4.75, (yb + yt) / 2, "A", va="center", fontsize=12, fontweight="bold", color=INK2)
    ax.annotate("", (-xa, 3.9), (xa, 3.9), arrowprops=dict(arrowstyle="<->", color=INK2, lw=1))
    for xx in (-xa, xa):
        ax.plot([xx, xx], [TRI_R / 2, 4.1], color=MUTED, lw=0.6, ls=":")
    ax.text(0, 4.05, "B", ha="center", va="bottom", fontsize=12, fontweight="bold", color=INK2)
    ax.text(-5.4, -5.4, "base (printed)", fontsize=9, color=INK2, va="bottom")
    ax.text(-0.9, -1.0, "pocket", fontsize=9.5, color=INK, ha="center")
    ax.set_xlim(-5.6, 5.6)
    ax.set_ylim(-5.6, 4.8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Seen from above, corner toward \u2212Y, to scale (mm)", fontsize=10.5, color=INK, loc="left")

    # top right: one flat, magnified
    az.set_facecolor(SURF)
    yp, yo, yn = m["pocket"]["centre_to_flat"], m["old"]["centre_to_flat"], m["new"]["centre_to_flat"]
    az.add_patch(Rectangle((-1.5, yp), 3, 0.25, color=BASE, lw=0, zorder=0))
    az.add_patch(Rectangle((-1.5, yp), 3, yn - yp, fc="none", ec=NEW, hatch="////", lw=0, zorder=1))
    az.plot([-1.5, 1.5], [yp, yp], color=INK, lw=1.4)
    az.plot([-1.5, 1.5], [yo, yo], color=OLD, lw=1.6, ls=(0, (4, 2)))
    az.plot([-1.5, 1.5], [yn, yn], color=NEW, lw=2.0)
    az.text(-1.45, yp + 0.19, "base", fontsize=9.5, color=INK2, va="center")
    az.text(1.45, yp - 0.012, "pocket wall", fontsize=9.5, color=INK, ha="right", va="top")
    az.text(1.45, yo - 0.012, "nub printed 10-21", fontsize=9.5, color=OLD, ha="right", va="top")
    az.text(1.45, yn + 0.012, "new nub", fontsize=9.5, color=NEW, ha="right", va="bottom")
    for y0, y1, label, c in ((yo, yp, "0.10 clearance (loose)", OLD), (yp, yn, "0.10 interference (press)", NEW)):
        az.annotate("", (-0.75, y0), (-0.75, y1), arrowprops=dict(arrowstyle="<->", color=c, lw=1, shrinkA=0, shrinkB=0))
        az.text(-0.7, (y0 + y1) / 2, " " + label, fontsize=9.5, color=INK, va="center")
    az.set_xlim(-1.5, 1.5)
    az.set_ylim(yo - 0.12, yp + 0.27)
    az.axis("off")
    az.set_title("One flat, magnified: every flat and corner gets the same", fontsize=10.5, color=INK, loc="left")

    # bottom right: the sizes
    at.axis("off")
    cols = (0.0, 0.50, 0.63, 0.77, 1.0)
    head = ("", "A", "B", "corner R", "fit, a side")
    rows = [("pocket in the base", m["pocket"], "1.1", "", INK),
            ("nub printed 10-21", m["old"], "1.0", "0.10 clear", OLD),
            ("new nub", m["new"], "1.2", "0.10 press", NEW)]
    for j, h in enumerate(head):
        at.text(cols[j], 0.92, h, ha="left" if j == 0 else "right", fontsize=9.5, color=INK2, transform=at.transAxes)
    at.plot([0, 1], [0.84, 0.84], color=MUTED, lw=0.6, transform=at.transAxes)
    for i, (name, d, r, fit, c) in enumerate(rows):
        y = 0.70 - 0.17 * i
        at.plot([0.0, 0.03], [y + 0.025, y + 0.025], color=c, lw=2.2, ls=(0, (4, 2)) if c == OLD else "-", transform=at.transAxes)
        cells = (name, f"{d['corner_to_flat']:.2f}", f"{d['across_corners']:.2f}", r, fit)
        for j, cell in enumerate(cells):
            at.text(cols[j] + (0.045 if j == 0 else 0), y, cell, ha="left" if j == 0 else "right", fontsize=9.5, color=INK,
                    fontweight="bold" if c == NEW and j in (1, 2, 3) else "normal", transform=at.transAxes)
    at.text(0.0, 0.08, "Fit-test keys: 0.05 (A 6.95, B 7.67) and 0.15 (A 7.15, B 7.87), in stl/key_fit_test/.\n"
            "Dimples on the key's top face: one per 0.05 mm of interference.", fontsize=8.8, color=INK2,
            transform=at.transAxes, va="bottom")

    fig.suptitle("Deck key nub in the base's key pocket: from 0.10 mm clearance to a 0.10 mm press fit",
                 x=0.02, y=0.975, ha="left", fontsize=13, fontweight="bold", color=INK)
    fig.text(0.02, 0.025, "Pocket 2.1 mm deep, so the printed base takes the new key. Nub 2.0 mm tall, with a 0.3 mm "
             "lead-in chamfer round its top.\nCalipers: A with one jaw on a flat and the other on the opposite corner; "
             "B with the jaws parallel to a flat.", fontsize=8.8, color=INK2)
    fig.savefig(out, facecolor=SURF)


if __name__ == "__main__":
    print("Model (mm)               corner-to-flat  across-corners  flat  centre-to-flat  centre-to-corner")
    for name, r in (("pocket, R1.1", POCKET_R), ("nub printed 10-21, R1.0", OLD_R), ("new nub, R1.2", NEW_R)):
        d = model(r)
        print(f"  {name:24s} {d['corner_to_flat']:6.3f}         {d['across_corners']:6.3f}       {d['flat']:5.3f}    "
              f"{d['centre_to_flat']:5.3f}          {d['centre_to_corner']:5.3f}")
    print("\nMeasured (mm): corner-to-flat x3, across-corners x3")
    for label, hc, wc in stl_sizes() + gcode_sizes():
        print(f"  {label:58s} " + " ".join(f"{v:6.3f}" for v in hc) + "   " + " ".join(f"{v:6.3f}" for v in wc))
    draw(HERE / "img" / "key_fit.png")
    print("\nwrote img/key_fit.png")
