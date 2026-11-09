#!/usr/bin/env python3
"""Check the three fit-test deck keys in a sliced A1 mini G-code (or a .gcode.3mf).

For each object: its footprint on layer 1, its nub's caliper sizes from the outer-wall
toolpaths (z 10.2-11.6, below the 0.3 mm lead-in; toolpath span + one line width), and how
many dimples have a wall loop round them in the pill's top layers (z 9.8 and 10.0).
Writes a top view of every extrusion move, shaded by height, to OUT_PNG.

    python check_slice.py FILE.gcode|FILE.gcode.3mf OUT_PNG [ID=NAME,...]

The optional ID=NAME list names the objects by their G-code label ids.
"""
import json, math, re, sys, zipfile
from collections import defaultdict
import numpy as np

src, out_png = sys.argv[1], sys.argv[2]
names = dict(kv.split("=") for kv in sys.argv[3].split(",")) if len(sys.argv) > 3 else {}
if src.endswith(".3mf"):
    with zipfile.ZipFile(src) as z:
        text = z.read("Metadata/plate_1.gcode").decode()
else:
    text = open(src).read()

CORNERS = (-90, 30, 150)          # nub corner directions, one corner toward -Y
unit = lambda a: np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
num = re.compile(r"([XYZEIJ])(-?\d*\.?\d+)")
walls = defaultdict(list)          # (object, z) -> [(line width, x, y)]
arcs = defaultdict(set)            # (object, z) -> outer-wall arc centres, rounded to 0.05 mm
moves = []                          # (z, x0, y0, x1, y1) for the drawing
first = defaultdict(list)
x = y = 0.0
lz = obj = feat = lw = None
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

rows = []
for o in sorted(first):
    f = np.array(first[o])
    lo, hi = f.min(axis=0), f.max(axis=0)
    c = (lo + hi) / 2
    nub = []
    for z in sorted(k[1] for k in walls if k[0] == o and 10.1 < k[1] < 11.7):
        pts = np.array([(px, py) for (_, px, py) in walls[(o, z)] if math.hypot(px - c[0], py - c[1]) < 5.5])
        w = walls[(o, z)][0][0]
        h = lambda a: float((pts @ unit(a)).max())
        nub.append(([h(a) + h(a + 180) + w for a in CORNERS], [h(a + 90) + h(a - 90) + w for a in CORNERS]))
    A = float(np.mean([n[0] for n in nub]))
    B = float(np.mean([n[1] for n in nub]))
    # dimples: 0.4 mm deep, so in the layers at z 9.8 and 10.0. Each is a hole in the top
    # layers ringed by an outer-wall loop drawn as G2/G3 arcs about its centre. List the
    # arc centres within 0.5 mm of y = cy +/- 8.5, as x offsets from the key's centre.
    found = {}
    for z in (9.8, 10.0):
        for sgn in (1, -1):
            xs = sorted({round(float(ax - c[0]), 1) for ax, ay in arcs.get((o, z), ())
                         if abs(ay - (c[1] + sgn * 8.5)) < 0.5 and abs(ax - c[0]) < 3.3})
            if xs:
                found[f"z {z}, y {'+-'[sgn < 0]}8.5"] = xs
    rows.append({"label_id": o, "name": names.get(str(o), ""), "footprint_layer1_mm": [round(float(v), 2) for v in (*lo, *hi)],
                 "footprint_size_mm": [round(float(v), 2) for v in hi - lo], "nub_A_mm": round(A, 3),
                 "nub_B_mm": round(B, 3), "nub_layers": len(nub),
                 "dimples": found, "dimple_count": max((len(v) for v in found.values()), default=0)})
for r in rows:
    print(json.dumps(r))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
mv = np.array(moves)
order = np.argsort(mv[:, 0])
mv = mv[order]
fig, ax = plt.subplots(figsize=(7, 7), dpi=130)
lc = LineCollection(mv[:, 1:].reshape(-1, 2, 2), array=mv[:, 0], cmap="viridis", linewidths=0.6)
ax.add_collection(lc)
ax.plot([0, 180, 180, 0, 0], [0, 0, 180, 180, 0], color="0.6", lw=1)
for r in rows:
    x0, y0, x1, y1 = r["footprint_layer1_mm"]
    n = r["dimple_count"]
    ax.annotate(f"{r['name'] or r['label_id']}\nA {r['nub_A_mm']:.2f}\n{n} dimple{'s' * (n != 1)}", ((x0 + x1) / 2, y0 - 2),
                ha="center", va="top", fontsize=8)
ax.set_xlim(-5, 185); ax.set_ylim(-5, 185); ax.set_aspect("equal")
ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)")
fig.colorbar(lc, ax=ax, shrink=0.7, label="Z (mm)")
ax.set_title("Extrusion moves, top view (A1 mini bed, 180 x 180 mm)", fontsize=10)
fig.tight_layout(); fig.savefig(out_png)
print("wrote", out_png)
