#!/usr/bin/env python3
"""Toolpaths over the magnet slots' skin, from slice_v3.py's builds.

    python skin_toolpaths.py <out.png> <out.json> <label>=<build dir> [<label>=<build dir>]

Print frame (slice_v3.py): X' = Onshape x + 25, Y' = 45 - Onshape z (the back face is Y' = 45),
Z' = Onshape y + 45. Upright slots: Z' 28..70; cross slot: Z' 5..15.5.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from shapely.geometry import LineString, Point  # noqa: E402

LAYERS = {"upright slot (layer at 50.0 mm)": 50.0, "cross slot (layer at 10.0 mm)": 10.0}
WINDOW = {50.0: (0.0, 16.0), 10.0: (-0.6, 15.4)}  # X' range; Y' 39..45.6
COLOURS = {"Outer wall": "#2a78d6", "Inner wall": "#eb6834", "Gap infill": "#1baf7a"}
OTHER = "#b9b8b3"
SURFACE, INK, MUTED = "#fcfcfb", "#0b0b0b", "#52514e"


def parse(gcode: Path, zs: set[float]) -> dict[float, list[dict]]:
    out = {z: [] for z in zs}
    z = feat = None
    width = 0.42
    x = y = 0.0
    for line in gcode.read_text().splitlines():
        if line.startswith("; Z_HEIGHT:"):
            z = round(float(line.split(":")[1]), 3)
        elif line.startswith("; FEATURE:"):
            feat = line.split(":", 1)[1].strip()
        elif line.startswith("; LINE_WIDTH:"):
            width = float(line.split(":")[1])
        elif line[:3] in ("G0 ", "G1 ", "G2 ", "G3 "):
            body = line.split(";")[0]
            nx = re.search(r"X(-?[\d.]+)", body)
            ny = re.search(r"Y(-?[\d.]+)", body)
            e = re.search(r"E(-?[\d.]+)", body)
            px, py = x, y
            x = float(nx.group(1)) if nx else x
            y = float(ny.group(1)) if ny else y
            if z in out and e and float(e.group(1)) > 0 and (x, y) != (px, py):
                out[z].append({"feat": feat, "w": width, "p": [(px, py), (x, y)]})
    return out


def coverage(segs: list[dict], ys: float, x0: float, x1: float) -> dict:
    """Which features cover points along the skin's mid-line, Y' = ys, from X' x0 to x1."""
    xs = np.arange(x0 + 0.05, x1, 0.1)
    lines = [(s["feat"], s["w"], LineString(s["p"])) for s in segs]
    hits = {}
    for xv in xs:
        pt = Point(xv, ys)
        feats = sorted({f for f, w, ln in lines if ln.distance(pt) <= w / 2})
        key = "+".join(feats) if feats else "nothing"
        hits[key] = hits.get(key, 0) + 1
    return {k: round(100 * v / len(xs), 1) for k, v in sorted(hits.items(), key=lambda kv: -kv[1])}


def skin_lines(segs: list[dict], x0: float, x1: float) -> list[dict]:
    """Extrusions that run along the back face over the slot: feature, Y' of the centre line, width."""
    rows = {}
    for s in segs:
        (ax_, ay), (bx, by) = s["p"]
        if abs(ay - by) < 1e-3 and ay > 43.5 and min(ax_, bx) < x1 and max(ax_, bx) > x0:
            key = (s["feat"], round(ay, 3), s["w"])
            rows[key] = rows.get(key, 0.0) + abs(bx - ax_)
    return [{"feature": f, "y_mm": y, "width_mm": w, "length_mm": round(n, 1)}
            for (f, y, w), n in sorted(rows.items(), key=lambda kv: -kv[0][1])]


def main() -> None:
    png, js = Path(sys.argv[1]), Path(sys.argv[2])
    builds = [a.split("=", 1) for a in sys.argv[3:]]
    fig, axes = plt.subplots(len(LAYERS), len(builds), figsize=(6.2 * len(builds), 3.4 * len(LAYERS)),
                             squeeze=False, facecolor=SURFACE)
    report = {}
    for c, (label, build) in enumerate(builds):
        build = Path(build)
        pos = json.loads((build / "placement.json").read_text())["stl_origin_on_bed"]
        mesh = trimesh.load(build / "atomizer_holder_v3_print.stl")
        layers = parse(build / "plate_1.gcode", set(LAYERS.values()))
        report[label] = {}
        for r, (title, z) in enumerate(LAYERS.items()):
            ax = axes[r][c]
            x0, x1 = WINDOW[z]
            segs = [{**s, "p": [(px - pos[0], py - pos[1]) for px, py in s["p"]]} for s in layers[z]]
            allp = np.array([p for s in segs for p in s["p"]])
            sec = mesh.section(plane_origin=[0, 0, z - 0.1], plane_normal=[0, 0, 1])
            outline = sec.to_2D(to_2D=np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, -(z - 0.1)], [0, 0, 0, 1]], float))[0]
            xs0, xs1 = (2.75, 13.25) if z == 50.0 else (0.0, 45.0)
            # skin thickness: the stretch of the section, at the slot's middle, that touches the back face
            poly = max(outline.polygons_full, key=lambda q: q.area)
            xm = (xs0 + xs1) / 2
            cut = poly.intersection(LineString([(xm, 45.5), (xm, 38.0)]))
            pieces = list(getattr(cut, "geoms", [cut]))
            skin_t = round(max(pc.length for pc in pieces if max(q[1] for q in pc.coords) > 44.99), 3)
            cov = coverage(segs, 45 - skin_t / 2, xs0, xs1)
            report[label][title] = {"segments": len(segs),
                                    "toolpath_bounds_mm": np.round([allp.min(0), allp.max(0)], 2).tolist(),
                                    "skin_mm": skin_t, "skin_midline_coverage_pct": cov,
                                    "lines_along_skin": skin_lines(segs, xs0 + 0.75, xs1 - 0.75)}
            ax.set_facecolor(SURFACE)
            for feat_group in ("other", "Inner wall", "Outer wall", "Gap infill"):
                polys, cols = [], []
                for s in segs:
                    f = s["feat"] if s["feat"] in COLOURS else "other"
                    if f != feat_group:
                        continue
                    g = LineString(s["p"]).buffer(s["w"] / 2, cap_style=2)
                    for geom in getattr(g, "geoms", [g]):
                        polys.append(np.asarray(geom.exterior.coords))
                        cols.append(COLOURS.get(f, OTHER))
                if polys:
                    ax.add_collection(PolyCollection(polys, facecolors=cols, edgecolors=SURFACE,
                                                     linewidths=0.25, alpha=0.9))
            gap = [q for q in report[label][title]["lines_along_skin"] if q["feature"] == "Gap infill"]
            if gap:
                ax.annotate("gap fill", xy=((max(x0, xs0) + min(x1, xs1)) / 2, gap[0]["y_mm"]),
                            xytext=((max(x0, xs0) + min(x1, xs1)) / 2, 45 - skin_t - 0.75), ha="center", va="center",
                            fontsize=8, color=INK, arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.6})
            walls = [q for q in report[label][title]["lines_along_skin"] if q["feature"] == "Outer wall"]
            if len(walls) == 2 and abs(walls[0]["y_mm"] - walls[1]["y_mm"]) < walls[0]["width_mm"]:
                gap_mm = abs(walls[0]["y_mm"] - walls[1]["y_mm"])
                ax.annotate(f"two outer walls, {gap_mm:.2f} mm apart", xy=((max(x0, xs0) + min(x1, xs1)) / 2, 45 - skin_t / 2),
                            xytext=((max(x0, xs0) + min(x1, xs1)) / 2, 45 - skin_t - 0.75), ha="center", va="center",
                            fontsize=8, color=INK, arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.6})
            for ent in outline.discrete:
                ax.plot(ent[:, 0], ent[:, 1], color=INK, lw=0.9)
            ax.set_xlim(x0, x1)
            ax.set_ylim(39.0, 45.6)
            ax.set_aspect("equal")
            ax.set_title(f"{label}: {title}, skin {skin_t:g} mm", fontsize=9.5, color=INK, loc="left")
            ax.tick_params(colors=MUTED, labelsize=8)
            for sp in ax.spines.values():
                sp.set_color("#d6d5d0")
            ax.set_xlabel("mm along the back face", fontsize=8, color=MUTED)
            ax.set_ylabel("mm (back face at 45)", fontsize=8, color=MUTED)
            ax.annotate("back face", xy=(x1 - 0.2, 45.05), ha="right", va="bottom", fontsize=8, color=MUTED)
            ax.annotate("slot", xy=((max(x0, xs0) + min(x1, xs1)) / 2, 45 - skin_t - 1.75),
                        ha="center", va="center", fontsize=8.5, color=MUTED)
    handles = [Patch(facecolor=COLOURS[k], label=k.lower()) for k in COLOURS] + \
              [Patch(facecolor=OTHER, label="infill and other"), Line2D([], [], color=INK, lw=0.9, label="designed outline")]
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False, fontsize=8.5)
    fig.suptitle("Atomizer Holder V3 magnet slots: Bambu Studio CLI slice, stock A1 mini 0.20 mm Standard (Classic walls)",
                 fontsize=10.5, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    fig.savefig(png, dpi=170, facecolor=SURFACE)
    js.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
