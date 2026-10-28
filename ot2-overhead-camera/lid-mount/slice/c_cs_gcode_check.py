#!/usr/bin/env python3
"""Check the threads of printed C-CS spacer rings against the model, from the plate G-code.

    python c_cs_gcode_check.py PLATE.gcode A B           # the 2026-10-23 print: rings A and B
    python c_cs_gcode_check.py PLATE.gcode C D E F G H   # the 2026-10-28 print
    python c_cs_gcode_check.py PLATE.gcode A B --json out.json

For each ring on the plate it rebuilds the outer-wall paths (G1 lines and the G2/G3 arcs that
arc fitting writes), finds the ring's centre from the plain bore of its threaded end, and takes
the nozzle path's radius round that centre on every layer. At any one height a thread's surface
passes once through its whole profile in one turn, so the spread of those radii is the profile:
crest, flanks and root. The model's radius function from ../cad/c_cs_spacer.py, sampled on the
slicing plane (mid-layer) and offset by half the line width (out of the material, so outwards
for the bore and inwards for the threaded end), gives the same spread for the design.

It reports, per ring and per thread, the as-sliced minus the modelled radius at the 5th, 50th
and 95th percentile, averaged over the threaded layers. Within a few hundredths of a millimetre
means the slicer drew the thread as modelled, so any misfit comes from printing, not slicing.

Rings are matched to names by their rim notches (one per letter, A = 1) where the plate has
more than one ring; the bore of the threaded end gives the centre.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cad"))
import c_cs_spacer as cs  # noqa: E402

NUM = re.compile(r"([XYZEIJ])(-?\d*\.?\d+)")


def outer_walls(path):
    """Outer-wall extrusion points, sampled every 0.05 mm: (object id, z, x, y, line width)."""
    rows = []
    x = y = z = 0.0
    feat, width, obj = None, 0.42, None
    for line in open(path):
        if line.startswith(";"):
            if line.startswith("; FEATURE:"):
                feat = line.split(":", 1)[1].strip()
            elif line.startswith("; LINE_WIDTH:"):
                width = float(line.split(":")[1])
            elif line.startswith("; OBJECT_ID:"):
                obj = int(line.split(":")[1])
            continue
        code = line.split(";")[0]
        g = code.split()[:1]
        if not g or g[0] not in ("G0", "G1", "G2", "G3"):
            continue
        d = {k: float(v) for k, v in NUM.findall(code)}
        nx, ny, nz = d.get("X", x), d.get("Y", y), d.get("Z", z)
        if d.get("E", 0.0) > 0 and feat == "Outer wall" and nz == z:
            if g[0] in ("G2", "G3") and ("I" in d or "J" in d):
                cx, cy = x + d.get("I", 0.0), y + d.get("J", 0.0)
                a0, a1 = math.atan2(y - cy, x - cx), math.atan2(ny - cy, nx - cx)
                r = math.hypot(x - cx, y - cy)
                if g[0] == "G2" and a1 >= a0:
                    a1 -= 2 * math.pi
                if g[0] == "G3" and a1 <= a0:
                    a1 += 2 * math.pi
                a = np.linspace(a0, a1, max(2, int(abs(a1 - a0) * r / 0.05)) + 1)
                px, py = cx + r * np.cos(a), cy + r * np.sin(a)
            else:
                n = max(1, int(math.hypot(nx - x, ny - y) / 0.05))
                t = np.linspace(0, 1, n + 1)
                px, py = x + (nx - x) * t, y + (ny - y) * t
            rows.append(np.column_stack([np.full(len(px), obj), np.full(len(px), z), px, py,
                                         np.full(len(px), width)]))
        x, y, z = nx, ny, nz
    return np.vstack(rows)


def centre(P):
    """Least-squares circle through the plain bore of the threaded end (the inner loop, z 6-8.4)."""
    c0 = P.mean(0)
    r0 = np.hypot(*(P - c0).T)
    inner = P[r0 < r0.min() + 0.35]         # the bore loop; the thread's root is 0.6 mm further out
    A = np.column_stack([2 * inner[:, 0], 2 * inner[:, 1], np.ones(len(inner))])
    cx, cy, k = np.linalg.lstsq(A, (inner ** 2).sum(1), rcond=None)[0]
    return cx, cy, math.sqrt(k + cx * cx + cy * cy)


def notches(z_rows, cx, cy):
    """Count the V-notches on the rim at mid-flange: clusters of the flange path dipping 0.45 mm in
    (the notches are 0.8 mm deep, the grip flutes 0.25 mm), separated by more than 5 degrees."""
    zz = min(z_rows, key=lambda z: abs(z - 2.5))
    P = z_rows[zz]
    r = np.hypot(P[:, 0] - cx, P[:, 1] - cy)
    th = np.degrees(np.arctan2(P[:, 1] - cy, P[:, 0] - cx))
    rim = r > 14.0
    deep = np.sort(th[rim & (r < r[rim].max() - 0.45)])
    if not len(deep):
        return 0
    gaps = np.diff(np.concatenate([deep, [deep[0] + 360]]))
    return int(max(1, np.sum(gaps > 5)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gcode")
    ap.add_argument("names", nargs="+", help="ring letters on the plate, e.g. C D E F G H")
    ap.add_argument("--json")
    a = ap.parse_args()
    spec = {s.name: s for s in cs.VARIANTS + cs.SIZES}
    W = outer_walls(a.gcode)
    th = np.linspace(0, 2 * np.pi, 3600, endpoint=False)
    report = {"gcode": Path(a.gcode).name, "rings": {}}
    for o in sorted(set(W[:, 0].astype(int))):
        S = W[W[:, 0] == o]
        m = (S[:, 1] > 6.0) & (S[:, 1] < 8.4)
        cx, cy, rb = centre(S[m][:, 2:4])
        z_rows = {z: S[S[:, 1] == z][:, 2:5] for z in sorted(set(S[:, 1]))}
        n = notches(z_rows, cx, cy)
        name = next((k for k in a.names if spec[k].notches == n), None)
        rec = {"object_id": int(o), "centre_xy": [round(cx, 3), round(cy, 3)], "notches_seen": n,
               "ring": name, "end_bore_path_r": round(rb, 3),
               "end_bore_path_r_model": round(spec[a.names[0]].bore / 2 + 0.21, 3)}
        if name is None:
            report["rings"][str(o)] = rec
            print(f"object {o}: {n} notches, no ring of that count among {a.names}")
            continue
        s = spec[name]
        diffs = {"female": [], "male": []}
        for z, P in z_rows.items():
            r = np.hypot(P[:, 0] - cx, P[:, 1] - cy)
            w2 = float(np.median(P[:, 2])) / 2
            zs = z - 0.04                                   # slicing plane: mid-layer of a 0.08 layer
            if 1.0 < z < s.spacing - s.roof - 0.2:          # female thread, clear of the entry and roof
                rr = r[(r > 12.0) & (r < 14.0 - 0.3)]
                if not len(rr):
                    continue
                des = cs.female_r(s, th, zs) + w2
                diffs["female"].append(np.percentile(rr, [5, 50, 95]) - np.percentile(des, [5, 50, 95]))
            elif s.spacing + s.relief + 0.4 < z < s.spacing + s.spigot - 0.5:   # male thread
                rr = r[r > s.bore / 2 + 0.5]
                if not len(rr):
                    continue
                des = cs.male_r(s, th, zs) - w2
                diffs["male"].append(np.percentile(rr, [5, 50, 95]) - np.percentile(des, [5, 50, 95]))
        for k, v in diffs.items():
            v = np.array(v)
            rec[k] = {"layers": len(v), "sliced_minus_model_mm_p5_p50_p95": v.mean(0).round(3).tolist(),
                      "worst_abs_mm": round(float(np.abs(v).max()), 3)}
        report["rings"][name] = rec
        print(f"ring {name} (object {o}, {n} notches, centre {cx:.2f}, {cy:.2f}): "
              f"female {rec['female']['sliced_minus_model_mm_p5_p50_p95']} over {rec['female']['layers']} layers, "
              f"male {rec['male']['sliced_minus_model_mm_p5_p50_p95']} over {rec['male']['layers']} layers")
    if a.json:
        Path(a.json).write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
