#!/usr/bin/env python3
"""Check the deck key width sweep (stl/width_sweep/) against deck_clip_key_v2_1 and the deck slot.

Measures, from the meshes (not from params.json):
  - each key's pill: width and length at three heights, and how tall the full-width band is;
  - that below the pill (z < -6) each key is v2_1's, section by section, including the latch
    arms, the barbs and the 0.7 mm gap at each arm's free end;
  - the dimples in the top face;
  - the clearance to a 10.5 mm wide deck slot (Ben's 0.7 mm on the 9.8 mm pill), in width and,
    for two guesses at the slot's length, at the round ends.
Then works out the latch in that slot, which is the same for every key.  Writes
width_sweep_output.txt.

    python cad/check_width_sweep.py

Needs trimesh, shapely and numpy.
"""
from __future__ import annotations

import io
import json
import math
import pathlib

import numpy as np
import trimesh
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

V2 = pathlib.Path(__file__).resolve().parent.parent
P = json.load(open(V2 / "cad" / "params.json"))
SWEEP = V2 / "stl" / "width_sweep"
BASE = {"stem": V2 / "stl" / "deck_clip_key_v2_1.stl", "tri": V2 / "stl" / "deck_clip_key_v2_1_tri.stl"}
SLOT_W = P["slot_w_meas"]

out = io.StringIO()


def say(*a):
    print(*a)
    print(*a, file=out)


def section(mesh, z):
    s = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s is None:
        return Polygon()
    to2d = getattr(s, "to_2D", None) or s.to_planar
    return unary_union(to2d(to_2D=np.eye(4))[0].polygons_full)


def stadium(w, l, n=720):
    """Pill outline, w wide (x) and l long (y), round ends of radius w/2."""
    r, c = w / 2, l / 2 - w / 2
    t = np.linspace(0, math.pi, n // 2)
    top = np.c_[r * np.cos(t), c + r * np.sin(t)]
    bot = np.c_[-r * np.cos(t), -c - r * np.sin(t)]
    return Polygon(np.r_[top, bot])


def name_parts(path):
    stem = path.stem                      # deck_clip_key_v2_1[_tri]_w10.2_c0.3
    top = "tri" if "_tri_" in stem else "stem"
    w = float(stem.split("_w")[1].split("_c")[0])
    c = float(stem.split("_c")[-1])
    return top, w, c


say("Deck key width sweep, measured from the STLs")
say(f"Deck slot taken as {SLOT_W:.2f} mm wide: the 9.80 mm pill + the 0.70 mm Ben measured (total, not a side).")
say("")

files = sorted(SWEEP.glob("*.stl"), key=lambda p: (name_parts(p)[0], name_parts(p)[1]))
base = {k: trimesh.load(v) for k, v in BASE.items()}
rows = []
say(f"{'key':40s} {'W@-0.2':>7s} {'W@-3':>6s} {'W@-5.9':>7s} {'L@-3':>6s} {'band':>5s} {'below z=-6 vs v2_1':>19s} {'dimples':>8s}")
for f in files:
    top, w, c = name_parts(f)
    m = trimesh.load(f)
    assert m.is_watertight, f
    widths = {}
    for z in (-0.2, -3.0, -5.9):
        b = section(m, z).bounds
        widths[z] = b[2] - b[0]
    b3 = section(m, -3.0).bounds
    length = b3[3] - b3[1]
    # full-width band: highest z below which the width drops under w - 0.01
    zs = np.arange(-6.0, 0.0, 0.01)
    full = [z for z in zs if (lambda bb: bb[2] - bb[0])(section(m, z).bounds) >= w - 0.01]
    band = -min(full) if full else 0.0
    # below the pill: section-by-section against v2_1
    worst = 0.0
    for z in (-6.2, -7.0, -8.0, -8.95, -9.5, -10.3, -11.0, -12.5, -14.5):
        a, b = section(m, z), section(base[top], z)
        worst = max(worst, a.symmetric_difference(b).area)
    # dimples: holes in the top face's section near the -y end (and the tri key's nub-press dimple at +y)
    s0 = section(m, -0.2)
    holes = [Polygon(r) for g in getattr(s0, "geoms", [s0]) for r in g.interiors]
    n_w = sum(1 for h in holes if h.centroid.y < -6)
    n_p = sum(1 for h in holes if h.centroid.y > 6)
    rows.append(dict(name=f.stem, top=top, w=w, c=c, W=widths, L=length, band=band, diff=worst, dimples=n_w, press=n_p, mesh=m))
    say(f"{f.stem:40s} {widths[-0.2]:7.3f} {widths[-3.0]:6.3f} {widths[-5.9]:7.3f} {length:6.3f} {band:5.2f} "
        f"{worst:15.4f} mm² {n_w:4d}" + (f" (+{n_p} at +y)" if n_p else ""))
for k, m in base.items():
    b = section(m, -3.0).bounds
    say(f"{BASE[k].stem + ' (for comparison)':40s} {'':7s} {b[2] - b[0]:6.3f} {'':7s} {b[3] - b[1]:6.3f}")

say("")
say("W = pill width (x) at that height, L = length (y), band = how far down from the top the pill is")
say("at its full width (below that, the 45-degree flare steps it back to v2_1's 9.8 mm at z = -6).")
say("'below z=-6 vs v2_1' is the largest area by which any section from z = -6.2 to -14.5 differs from")
say("v2_1's: zero means the transition, latch arms, barbs and ends are v2_1's.")

# arm free-end gap and barb reach, from the 10.5 mm key (the most changed)
m = [r for r in rows if r["top"] == "stem" and abs(r["c"]) < 1e-9][0]["mesh"]
strip = section(m, -12.5).intersection(box(3.7, 0.0, 4.8, 12.5))      # through the +x arm, toward +y
parts = sorted(getattr(strip, "geoms", [strip]), key=lambda g: g.bounds[1])
v = m.vertices
say("")
say(f"10.5 mm key, below the pill: barb tips at x = ±{np.abs(v[v[:, 2] < -8.0][:, 0]).max():.3f} mm, arm outer faces at "
    f"x = ±{section(m, -12.5).intersection(box(0, -7, 6, 2.5)).bounds[2]:.3f} mm, and {parts[1].bounds[1] - parts[0].bounds[3]:.3f} mm "
    f"from each arm's free end to the +y end block (v2_1: 0.700)")

# clearance to the slot
say("")
say("Clearance to the slot, key centred in it (mm). The slot's length is unknown: Cubware's drawing says 25.0,")
say("and if it is as oversize in length as in width it is 25.5. 'a side' is (slot - key) / 2.")
say(f"{'key':10s} {'width, total':>13s} {'a side':>7s} {'nearest at the ends, L 25.0':>28s} {'L 25.5':>7s}")
for r in [r for r in rows if r["top"] == "stem"]:
    key = section(r["mesh"], -3.0)
    ends = []
    for L in (25.0, 25.5):
        slot = stadium(SLOT_W, L)
        bd = slot.exterior
        pts = np.array(key.exterior.coords)
        far = pts[np.abs(pts[:, 1]) > (24.8 - r["w"]) / 2 + 0.5]          # points on the round ends
        ends.append(min(bd.distance(Point(p)) for p in far))
        assert slot.buffer(1e-6).contains(key), (r["name"], L)
    say(f"{r['w']:6.1f} mm  {SLOT_W - r['W'][-3.0]:10.3f}   {(SLOT_W - r['W'][-3.0]) / 2:7.3f} {ends[0]:24.3f} {ends[1]:11.3f}")

# the latch, in this slot: unchanged from v2_1, so the same for every sweep key
hx, u, tn = P["pill_w"] / 2, P["barb_u"], math.tan(math.radians(P["ramp_deg"]))
reach = hx + u - SLOT_W / 2                    # barb past the slot edge, key centred
k_arm, d_fea, eps_fea = 5.55 / 0.75, 0.75, 1.35       # FEA (fea_results.json): N/mm at the barb, its travel, peak strain %
z_catch = P["barb_top"] - (SLOT_W / 2 - hx) / tn
say("")
say(f"Latch in a {SLOT_W} mm slot (v2_1's, so the same for all eight keys and for the keys printed on 2026-11-19 bar the")
say("chamfer fix):")
say(f"  barbs reach {reach:.2f} mm past the slot edge (they reach 0.75 in the 10.0 mm slot they were drawn for)")
say(f"  to clip in, each arm moves {reach:.2f} mm: {k_arm * reach:.1f} N, {eps_fea * reach / d_fea:.2f} % peak strain "
    f"(FEA, linear: {k_arm * d_fea:.1f} N and {eps_fea:.2f} % at {d_fea} mm)")
say(f"  the ramps meet the slot's bottom edge at z = {z_catch:.2f}: no vertical play on a deck {-z_catch:.2f} mm or thicker")
for t in (9.0, 9.5, 10.0):
    if t >= -z_catch:
        dfl = (t + z_catch) * tn
        say(f"    {t:4.1f} mm deck: arms held {dfl:.2f} mm in, key pulled down {2 * k_arm * dfl * tn:.1f} N")
    else:
        say(f"    {t:4.1f} mm deck: {(-z_catch - t):.2f} mm of vertical play")

say("")
say("Lateral play of the rack at each key = the clearance in width, so 0.5 -> 0.3 -> 0.1 -> 0 mm. The keys are")
say("225 mm apart, so the rack can also turn by up to clearance / 225 rad: 0.13, 0.08, 0.03 and 0 degrees.")
(V2 / "cad" / "width_sweep_output.txt").write_text(out.getvalue())
print("wrote cad/width_sweep_output.txt")
