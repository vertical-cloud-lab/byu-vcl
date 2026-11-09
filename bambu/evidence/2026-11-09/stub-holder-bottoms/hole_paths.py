"""Wall loops around each pin hole in a plate G-code. Arcs (G2/G3) are sampled along the arc,
then each continuous extrusion run of a wall feature is a loop; loops under 3 mm in radius
are the pin holes. Reports the loop touching the hole (outer wall) and the next one out
(inner wall), per part, at a few heights."""
import json, math, re, sys, zipfile
import numpy as np
path = sys.argv[1]
g = zipfile.ZipFile(path).read("Metadata/plate_1.gcode").decode().splitlines()
targets = [3.2, 6.0, 10.0, 14.8, 17.8]
x = y = None; layer_z = None; feat = None
runs = []  # (z, feat, [points])
cur = None
def flush():
    global cur
    if cur and len(cur[2]) > 3: runs.append(cur)
    cur = None
for line in g:
    if line.startswith("; Z_HEIGHT:"):
        flush(); layer_z = round(float(line.split(":")[1]), 2)
    elif line.startswith("; FEATURE:"):
        flush(); feat = line.split(":", 1)[1].strip()
    elif line[:3] in ("G1 ", "G0 ", "G2 ", "G3 "):
        code = line[:2]
        m = dict(re.findall(r"([XYZEIJ])(-?[\d.]+)", line.split(";")[0]))
        nx = float(m["X"]) if "X" in m else x
        ny = float(m["Y"]) if "Y" in m else y
        extr = "E" in m and float(m["E"]) > 0
        if extr and x is not None and (nx, ny) != (x, y) and feat in ("Outer wall", "Inner wall") and layer_z is not None:
            if cur is None or cur[0] != layer_z or cur[1] != feat:
                flush(); cur = (layer_z, feat, [(x, y)])
            if code in ("G2", "G3"):
                cx, cy = x + float(m.get("I", 0)), y + float(m.get("J", 0))
                r = math.hypot(x - cx, y - cy)
                a0 = math.atan2(y - cy, x - cx); a1 = math.atan2(ny - cy, nx - cx)
                if code == "G2":   # clockwise
                    while a1 >= a0: a1 -= 2 * math.pi
                else:
                    while a1 <= a0: a1 += 2 * math.pi
                for t in np.linspace(0, 1, 16)[1:]:
                    a = a0 + (a1 - a0) * t
                    cur[2].append((cx + r * math.cos(a), cy + r * math.sin(a)))
            else:
                for t in np.linspace(0, 1, 6)[1:]:
                    cur[2].append((x + (nx - x) * t, y + (ny - y) * t))
        elif not extr and cur is not None and (nx, ny) != (x, y):
            flush()
        x, y = nx, ny
flush()
layers = sorted({r[0] for r in runs})
out = {}
for t in targets:
    lz = min(layers, key=lambda L: abs(L - t))
    row = {}
    for z, f, pts in runs:
        if z != lz: continue
        P = np.array(pts)
        if np.ptp(P[:, 0]) > 7 or np.ptp(P[:, 1]) > 7: continue      # bigger than a hole loop
        A = np.c_[2 * P, np.ones(len(P))]; b = (P ** 2).sum(1)
        (cx, cy, k), *_ = np.linalg.lstsq(A, b, rcond=None)
        c = np.array([cx, cy]); d = np.hypot(*(P - c).T)
        if d.std() > 0.05: continue                                  # not round
        part = "3.3" if c[1] < 90 else "3.4"
        row.setdefault(f"{part} {f}", []).append((round(float(c[0]), 2), round(float(c[1]), 2), float(d.mean())))
    out[f"z={lz}"] = {k: {"n_loops": len(v), "mean_r": round(float(np.mean([r for *_, r in v])), 3),
                          "min_r": round(min(r for *_, r in v), 3), "max_r": round(max(r for *_, r in v), 3),
                          "centres": [(a, b) for a, b, _ in v]} for k, v in sorted(row.items())}
json.dump(out, sys.stdout, indent=1)
