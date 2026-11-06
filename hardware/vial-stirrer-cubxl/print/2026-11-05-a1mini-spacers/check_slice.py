#!/usr/bin/env python3
"""check_slice.py FILE.gcode.3mf|FILE.gcode: where the two Ø15 × 4.6 mm spacers print, and how big.

Reads the plate's G-code (from Metadata/plate_1.gcode in a .gcode.3mf), takes the outer wall's
extrusion moves on layers 1, 2, 12 and the last, splits them into the two discs at the widest gap,
and prints each disc's centre and its wall's centreline span. Add one line width to the span for the
outside diameter: 0.42 mm from layer 2, 0.5 mm on layer 1.
"""
import collections, io, re, sys, zipfile
path = sys.argv[1]
if path.endswith(".3mf"):
    text = zipfile.ZipFile(path).read("Metadata/plate_1.gcode").decode("utf-8", "replace")
else:
    text = open(path, errors="replace").read()
z = None; layer = 0; feat = None; x = y = None
walls = collections.defaultdict(list)   # layer -> [(x,y)] outer-wall extrusion points
allext = collections.defaultdict(list)
for line in io.StringIO(text):
    if line.startswith("; CHANGE_LAYER"):
        layer += 1
    m = re.match(r"; Z_HEIGHT: ([\d.]+)", line)
    if m: z = float(m.group(1))
    m = re.match(r"; FEATURE: (.+)", line)
    if m: feat = m.group(1).strip()
    if line.startswith(("G1 ", "G0 ", "G2 ", "G3 ")):
        mx = re.search(r"X(-?[\d.]+)", line); my = re.search(r"Y(-?[\d.]+)", line); me = re.search(r"E(-?[\d.]+)", line)
        nx = float(mx.group(1)) if mx else x; ny = float(my.group(1)) if my else y
        if me and float(me.group(1)) > 0 and nx is not None and layer > 0 and feat not in (None, "Custom"):
            allext[layer].append((nx, ny))
            if feat == "Outer wall":
                walls[layer].append((nx, ny))
        x, y = nx, ny
def split(pts):
    # two discs side by side: split on the largest gap in x or y
    best = None
    for ax in (0, 1):
        s = sorted(p[ax] for p in pts)
        gaps = [(s[i+1]-s[i], (s[i+1]+s[i])/2) for i in range(len(s)-1)]
        g = max(gaps)
        if best is None or g[0] > best[0]: best = (g[0], ax, g[1])
    _, ax, cut = best
    return [p for p in pts if p[ax] < cut], [p for p in pts if p[ax] >= cut], ax
print(f"layers with extrusion: {len(allext)}")
for L in sorted(walls):
    if L not in (1, 2, 12, len(allext)): continue
    a, b, ax = split(walls[L])
    out = []
    for grp in (a, b):
        xs = [p[0] for p in grp]; ys = [p[1] for p in grp]
        cx, cy = (max(xs)+min(xs))/2, (max(ys)+min(ys))/2
        out.append(f"centre ({cx:6.2f},{cy:6.2f}) X span {max(xs)-min(xs):5.2f} Y span {max(ys)-min(ys):5.2f}")
    print(f"layer {L:2d}: " + " | ".join(out))
a, b, ax = split(allext[1])
for name, grp in (("A", a), ("B", b)):
    xs = [p[0] for p in grp]; ys = [p[1] for p in grp]
    print(f"layer 1 all extrusion, disc {name}: X {min(xs):.2f}-{max(xs):.2f}, Y {min(ys):.2f}-{max(ys):.2f}")
