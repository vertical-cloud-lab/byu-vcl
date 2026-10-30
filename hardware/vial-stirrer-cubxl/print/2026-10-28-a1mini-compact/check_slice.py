#!/usr/bin/env python3
"""Check the compact stirrer's plate in the sent .gcode.3mf against the model.

For each object (named from the file's own plate_1.json, matched by layer-1 footprint): its
footprint on layer 1, its outline at a few heights from the outer-wall toolpaths (span + one
line width), and for the deck keys the nub's caliper sizes and dimple count as in
../2026-10-22-a1mini-keys/check_slice.py. Writes a top view of every extrusion move, shaded
by height, to OUT_PNG.

    python check_slice.py compact_stirrer_parts.gcode.3mf plate_layout.png
"""
import json, math, re, sys, zipfile
from collections import defaultdict
import numpy as np

src, out_png = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(src) as z:
    text = z.read("Metadata/plate_1.gcode").decode()
    plate = json.loads(z.read("Metadata/plate_1.json"))

CORNERS = (-90, 30, 150)          # nub corner directions, one corner toward -Y
unit = lambda a: np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
num = re.compile(r"([XYZEIJ])(-?\d*\.?\d+)")
walls = defaultdict(list)          # (object, z) -> [(line width, x, y)]
arcs = defaultdict(set)
moves, first = [], defaultdict(list)
x = y = 0.0
lz = obj = feat = lw = None
for line in text.splitlines():
    if line.startswith(";"):
        if line.startswith("; Z_HEIGHT:"):
            lz = round(float(line.split(":")[1]), 3)
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
    if obj is not None and p.get("E", 0) > 0 and (nx, ny) != (x, y):
        pts = [(nx, ny)]
        if s[0] in ("G2", "G3"):
            cx, cy = x + p.get("I", 0), y + p.get("J", 0)
            a0, a1 = math.atan2(y - cy, x - cx), math.atan2(ny - cy, nx - cx)
            if s[0] == "G2":
                a1 = a1 - 2 * math.pi if a1 >= a0 else a1
            else:
                a1 = a1 + 2 * math.pi if a1 <= a0 else a1
            rr = math.hypot(x - cx, y - cy)
            pts = [(cx + rr * math.cos(a), cy + rr * math.sin(a)) for a in np.linspace(a0, a1, 24)]
        prev = (x, y)
        for q in pts:
            moves.append((lz, prev[0], prev[1], q[0], q[1]))
            prev = q
        if abs(lz - 0.2) < 1e-6:
            first[obj] += [(x, y)] + pts
        if feat == "Outer wall":
            walls[(obj, lz)] += [(lw, px, py) for px, py in [(x, y)] + pts]
            if s[0] in ("G2", "G3"):
                arcs[(obj, lz)].add((round((x + p.get("I", 0)) * 20) / 20, round((y + p.get("J", 0)) * 20) / 20))
    x, y = nx, ny

# name each G-code object by the nearest plate_1.json bounding-box centre
boxes = {o["name"]: o["bbox"] for o in plate["bbox_objects"]}
def name_of(lo, hi):
    c = (lo + hi) / 2
    return min(boxes, key=lambda n: math.hypot((boxes[n][0] + boxes[n][2]) / 2 - c[0], (boxes[n][1] + boxes[n][3]) / 2 - c[1]))

def outline(o, z):
    """Outer extent in X and Y of the object's outer-wall toolpaths on the layer at z, plus one line width."""
    k = min((k for k in walls if k[0] == o), key=lambda k: abs(k[1] - z))
    pts = np.array([(px, py) for (_, px, py) in walls[k]])
    w = walls[k][0][0]
    return k[1], [round(float(pts[:, 0].max() - pts[:, 0].min() + w), 3), round(float(pts[:, 1].max() - pts[:, 1].min() + w), 3)]

rows = []
for o in sorted(first):
    f = np.array(first[o])
    lo, hi = f.min(axis=0), f.max(axis=0)
    c = (lo + hi) / 2
    n = name_of(lo, hi)
    zmax = max(k[1] for k in walls if k[0] == o)
    r = {"label_id": o, "name": n, "footprint_layer1_mm": [round(float(v), 2) for v in (*lo, *hi)],
         "top_layer_z": zmax}
    if n.startswith("base"):
        r["outline_mm"] = dict(outline(o, z) for z in (5.0, 10.0, 18.0))
    elif n.startswith("vial_holder"):
        r["flange_outline_mm"] = dict(outline(o, z) for z in (1.0, 5.0))
        # the cup: outer-wall points more than 12 mm from the axis, at mid-height of the fingers
        for z in (12.0, 18.0):
            k = min((k for k in walls if k[0] == o), key=lambda k: abs(k[1] - z))
            pts = np.array([(px, py) for (_, px, py) in walls[k]]) - c
            rad = np.hypot(pts[:, 0], pts[:, 1])
            r.setdefault("cup_outer_diameter_mm", {})[k[1]] = round(float(2 * rad.max() + walls[k][0][0]), 3)
    elif n.startswith("deck_key"):
        nub = []
        for z in sorted(k[1] for k in walls if k[0] == o and 10.1 < k[1] < 11.7):
            pts = np.array([(px, py) for (_, px, py) in walls[(o, z)] if math.hypot(px - c[0], py - c[1]) < 5.5])
            w = walls[(o, z)][0][0]
            h = lambda a: float((pts @ unit(a)).max())
            nub.append(([h(a) + h(a + 180) + w for a in CORNERS], [h(a + 90) + h(a - 90) + w for a in CORNERS]))
        r["nub_A_mm"] = round(float(np.mean([v[0] for v in nub])), 3)
        r["nub_B_mm"] = round(float(np.mean([v[1] for v in nub])), 3)
        r["nub_layers"] = len(nub)
        found = set()
        for z in (9.8, 10.0):
            for sgn in (1, -1):
                found |= {(sgn, round(float(ax - c[0]), 1)) for ax, ay in arcs.get((o, z), ())
                          if abs(ay - (c[1] + sgn * 8.5)) < 0.5 and abs(ax - c[0]) < 3.3}
        r["dimples"] = len({v for v in found})
    elif n.startswith("magnet"):
        r["outline_mm"] = dict(outline(o, z) for z in (1.0, 2.6))
    rows.append(r)
for r in rows:
    print(json.dumps(r))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
mv = np.array(moves)
mv = mv[np.argsort(mv[:, 0])]
fig, ax = plt.subplots(figsize=(7, 7), dpi=130)
lc = LineCollection(mv[:, 1:].reshape(-1, 2, 2), array=mv[:, 0], cmap="viridis", linewidths=0.6)
ax.add_collection(lc)
ax.plot([0, 180, 180, 0, 0], [0, 0, 180, 180, 0], color="0.6", lw=1)
for r in rows:
    x0, y0, x1, y1 = r["footprint_layer1_mm"]
    ax.annotate(r["name"].replace(".stl", ""), ((x0 + x1) / 2, y0 - 2), ha="center", va="top", fontsize=8)
ax.set_xlim(-5, 185); ax.set_ylim(-5, 185); ax.set_aspect("equal")
ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)")
fig.colorbar(lc, ax=ax, shrink=0.7, label="Z (mm)")
ax.set_title("Extrusion moves, top view (A1 mini bed, 180 x 180 mm)", fontsize=10)
fig.tight_layout(); fig.savefig(out_png)
print("wrote", out_png)
