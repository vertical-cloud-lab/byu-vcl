#!/usr/bin/env python3
"""Check the triangle interface of deck_clip_key_v2_1_tri and vial_rack_9x20mL_v2_tri.

Measures, from the meshes (not from params.json):
  - the nub of deck_clip_key_v2_1_tri.stl, and of the stir module's deck_key.stl;
  - the key pockets of vial_rack_9x20mL_v2_tri.stl, of PANDA-BEAR's 9VialHolder20mL_TightFit.step
    (../../cad/) and of the stir module's base.stl.
Each outline is fitted as a sharp equilateral triangle of circumradius R grown all round by r, and
reported as A (corner to the opposite flat) and B (across two corners, parallel to a flat), the same
caliper sizes as hardware/vial-stirrer-cubxl/analysis/key_fit.py. Then a key is put into each of the
rack's pockets and the overlap is measured: it should be the 0.05 mm press band round the nub and
nothing else. Writes tri_fit_output.txt and ../img/tri_fit.png.

    python cad/check_tri_fit.py

Needs trimesh, manifold3d, shapely and matplotlib, and cadquery for the STEP file.
"""
from __future__ import annotations

import io
import math
import pathlib
import tempfile
import warnings

import numpy as np
import trimesh

warnings.filterwarnings("ignore", category=DeprecationWarning)

V2 = pathlib.Path(__file__).resolve().parent.parent
ROOT = V2.parents[2]
STIR = ROOT / "hardware" / "vial-stirrer-cubxl" / "stl"
KEY = V2 / "stl" / "deck_clip_key_v2_1_tri.stl"
RACK = V2 / "stl" / "vial_rack_9x20mL_v2_tri.stl"
ORIG = V2.parent / "cad" / "9VialHolder20mL_TightFit.step"
KEY_Y = (0.0, -225.0)
DECK_T, SLOT_HALF_W = 10.0, 5.0      # Cubware PandaDeck: 10 mm plate, 10 mm wide slots

out = io.StringIO()


def say(*a):
    print(*a)
    print(*a, file=out)


def section_2d(mesh, z):
    s = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s is None:
        return []
    to2d = getattr(s, "to_2D", None) or s.to_planar
    return to2d(to_2D=np.eye(4))[0].polygons_full


def rings(mesh, z, x0, y0, kind):
    """Outlines near (x0, y0) at height z: holes (kind="hole") or outer outlines ("solid")."""
    found = []
    for pg in section_2d(mesh, z):
        for ring in (pg.interiors if kind == "hole" else [pg.exterior]):
            pts = np.array(ring.coords)[:, :2]
            span = pts.max(axis=0) - pts.min(axis=0)
            c = (pts.max(axis=0) + pts.min(axis=0)) / 2
            if span.max() < 12 and math.hypot(c[0] - x0, c[1] - y0) < 6:
                found.append(pts)
    return found


def fit(pts):
    """Centre, A, B, R, r and corner directions of a rounded equilateral triangle."""
    angs = np.arange(0.0, 360.0, 0.05)
    U = np.c_[np.cos(np.radians(angs)), np.sin(np.radians(angs))]
    c = (pts.min(axis=0) + pts.max(axis=0)) / 2
    for _ in range(6):
        h = ((pts - c) @ U.T).max(axis=0)
        ca = angs[int(np.argmax(h))]
        cs = np.array([ca, ca + 120.0, ca + 240.0])
        Uc = np.c_[np.cos(np.radians(cs)), np.sin(np.radians(cs))]
        hc = ((pts - c) @ Uc.T).max(axis=0)
        d, *_ = np.linalg.lstsq(Uc, hc - hc.mean(), rcond=None)
        c = c + d

    def h1(a):
        return float(((pts - c) @ np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])).max())

    A = float(np.mean([h1(x) + h1(x + 180) for x in cs]))
    B = float(np.mean([h1(x + 90) + h1(x - 90) for x in cs]))
    R = (B - A) / (math.sqrt(3) - 1.5)
    r = (A - 1.5 * R) / 2
    corners = sorted(round(((x + 180) % 360) - 180) for x in cs)
    return {"c": c, "A": A, "B": B, "R": R, "r": r, "corners": corners}


def toward(corners):
    if any(abs(a + 90) <= 3 for a in corners):
        return "-y"
    if any(abs(a - 90) <= 3 for a in corners):
        return "+y"
    return "?"


_DEPTH = {}


def depth(mesh, x0, y0, lo=1.5, hi=2.6):
    """Height of the roof of the hole near (x0, y0), by bisection between lo (hole) and hi (no hole)."""
    key_ = (id(mesh), x0, y0)
    if key_ in _DEPTH:
        return _DEPTH[key_]
    for _ in range(16):
        mid = (lo + hi) / 2
        if rings(mesh, mid, x0, y0, "hole"):
            lo = mid
        else:
            hi = mid
    _DEPTH[key_] = (lo + hi) / 2
    return _DEPTH[key_]


def load_step(path):
    import cadquery as cq

    with tempfile.TemporaryDirectory() as td:
        stl = pathlib.Path(td) / "orig.stl"
        cq.exporters.export(cq.importers.importStep(str(path)), str(stl), tolerance=0.005, angularTolerance=0.05)
        return trimesh.load(stl)


def row(name, d, extra=""):
    say(f"  {name:52s} A {d['A']:6.3f}  B {d['B']:6.3f}  R {d['R']:5.3f}  r {d['r']:5.3f}  "
        f"corner toward {toward(d['corners'])} {d['corners']}  {extra}")


key, rack = trimesh.load(KEY), trimesh.load(RACK)
say("Triangle interface: nub and pockets measured from the meshes (mm)")
say("A = corner to the opposite flat, B = across two corners parallel to a flat; R, r = the sharp")
say("triangle's circumradius and the corner radius it is grown by.\n")

say("Nubs (section at z = 1.0):")
kn = fit(rings(key, 1.0, 0, 0, "solid")[0])
row("deck_clip_key_v2_1_tri.stl", kn, f"height {key.bounds[1][2]:.3f}")
top = fit(rings(key, 1.95, 0, 0, "solid")[0])
say(f"  {'  same, z = 1.95 (in the 0.3 mm lead-in)':52s} A {top['A']:6.3f}  B {top['B']:6.3f}")
sk = trimesh.load(STIR / "deck_key.stl")
sn = fit(np.vstack(rings(sk, 1.0, *((sk.bounds[0][:2] + sk.bounds[1][:2]) / 2), "solid")))
row("stir module deck_key.stl (the 0.05 mm key Ben chose)", sn, f"height {sk.bounds[1][2]:.3f}")

say("\nPockets (section at z = 1.0; depth = highest z with the hole):")
pockets = {}
for ky in KEY_Y:
    pockets[ky] = fit(rings(rack, 1.0, 0, ky, "hole")[0])
    row(f"vial_rack_9x20mL_v2_tri.stl at y = {ky:g}", pockets[ky], f"depth {depth(rack, 0, ky):.3f}")
    mouth = fit(rings(rack, 0.02, 0, ky, "hole")[0])
    say(f"  {'  same, at its mouth (z = 0.02)':52s} A {mouth['A']:6.3f}  B {mouth['B']:6.3f}")
orig = load_step(ORIG)
for ky in KEY_Y:
    row(f"9VialHolder20mL_TightFit.step at y = {ky:g}", fit(rings(orig, 1.0, 0, ky, "hole")[0]),
        f"depth {depth(orig, 0, ky):.3f}")
base = trimesh.load(STIR / "base.stl")
for kx in (-12.5, 12.5):
    row(f"stir module base.stl at x = {kx:g}", fit(rings(base, 1.0, kx, 0, "hole")[0]), f"depth {depth(base, kx, 0):.3f}")

p0 = pockets[0.0]
say(f"\nFit, each side: A {(kn['A'] - p0['A']) / 2:+.3f}, B {(kn['B'] - p0['B']) / 2:+.3f} "
    f"(+ = interference); r {kn['r'] - p0['r']:+.3f}")
say(f"The stir module's key against the same pocket: A {(sn['A'] - p0['A']) / 2:+.3f}, B {(sn['B'] - p0['B']) / 2:+.3f}")

say("\nKey pressed fully home in each of the rack's pockets (key top face on the rack's underside):")
for ky in KEY_Y:
    k = key.copy()
    k.apply_translation([0, ky, 0])
    ov = trimesh.boolean.intersection([rack, k], engine="manifold")
    if ov.is_empty or ov.volume < 1e-6:
        say(f"  y = {ky:g}: no overlap")
        continue
    lo, hi = ov.bounds
    perim = float(np.sum(np.linalg.norm(np.diff(rings(rack, 1.0, 0, ky, "hole")[0], axis=0), axis=1)))
    band = ov.volume / (perim * (hi[2] - lo[2]))
    say(f"  y = {ky:g}: overlap {ov.volume:.2f} mm^3, x {lo[0]:+.2f}..{hi[0]:+.2f}, y {lo[1] - ky:+.2f}..{hi[1] - ky:+.2f} "
        f"(from the key's centre), z {lo[2]:.2f}..{hi[2]:.2f}; spread round the {perim:.1f} mm pocket wall, "
        f"{band:.3f} mm thick")
gap = depth(rack, 0, 0.0) - key.bounds[1][2]
say(f"  gap over the nub: {gap:.3f} mm (pocket depth less nub height)")
say("  The overlap is only the press band round the nub, below its lead-in. The key's top face and the rack's")
say("  underside meet at z = 0 without overlapping, so the rack still sits on the deck.")

# What the joint has to carry. The barbs' 30-degree retention ramps bear on the deck's bottom edge, so on a
# thick enough deck each arm stays flexed inward and its ramp pushes the key down. The rack can't take that
# through the key's top face (it only stops the key going up), so it is carried by the nub's grip.
import json

P = json.loads((V2 / "cad" / "params.json").read_text())
fea = json.loads((V2 / "fea" / "fea_results.json").read_text())["key_v2_1_latch_t1.3_deflect_0.75mm"]
k_arm = fea["F_per_arm_N"] / 0.75                      # N/mm at the barb, linear FEA
tn = math.tan(math.radians(P["ramp_deg"]))
slot_edge_u = SLOT_HALF_W - P["pill_w"] / 2            # the slot edge is 0.10 mm out from the pill flat
say(f"\nLoad on the nub joint from the latch (arm stiffness {k_arm:.1f} N/mm at the barb, from the FEA;")
say(f"ramps {P['ramp_deg']:g} deg from vertical; friction at the deck edge mu = 0.3 gives the range):")
PRELOAD = {}
for T in (9.0, 9.5, 10.0, 10.3):
    # depth of the deck's bottom edge below the ramp's start, times tan(ramp), less the slot's 0.10 mm
    d = min(max(0.0, (T + P["barb_top"]) * tn - slot_edge_u), P["barb_u"] - slot_edge_u)
    f = k_arm * d
    phi = math.atan(0.3)
    lo_, mid, hi_ = (2 * f * math.tan(math.radians(P["ramp_deg"]) + s) for s in (-phi, 0.0, phi))
    PRELOAD[T] = (d, mid, lo_, hi_)
    say(f"  deck {T:4.1f} mm: arm flexed {d:.2f} mm, {f:.1f} N per arm -> key pulled down {mid:.1f} N "
        f"({lo_:.1f}-{hi_:.1f})")
say("  On a 10 mm deck that is about 5 N per key, all the time. The stir module's and tip rack's keys only")
say("  locate, so their 0.05 mm press has never had to carry a steady load.")

(V2 / "cad" / "tri_fit_output.txt").write_text(out.getvalue())


# ---------------------------------------------------------------- figure
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.path import Path
from shapely.geometry.polygon import orient

INK, INK2, MUTED, SURF, GREY = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#dcdad4"
RACK_C, KEY_C = "#2a78d6", "#eb6834"      # categorical slots 1 and 2: the rack and the key
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": INK})


def patch(pg, **kw):
    pg = orient(pg, 1.0)
    verts, codes = [], []
    for ring in [pg.exterior] + list(pg.interiors):
        xy = np.array(ring.coords)[:, :2]
        verts += xy.tolist()
        codes += [Path.MOVETO] + [Path.LINETO] * (len(xy) - 2) + [Path.CLOSEPOLY]
    return PathPatch(Path(verts, codes), **kw)


def xz_section(mesh, y0):
    s = mesh.section(plane_origin=[0, y0, 0], plane_normal=[0, 1, 0])
    T = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, y0], [0, 0, 0, 1]], float)
    to2d = getattr(s, "to_2D", None) or s.to_planar
    return to2d(to_2D=T)[0].polygons_full


fig = plt.figure(figsize=(13.5, 7.4), dpi=110)
fig.patch.set_facecolor(SURF)
gs = fig.add_gridspec(2, 3, width_ratios=(1.05, 1.0, 1.0), height_ratios=(1.0, 0.62), left=0.02, right=0.99,
                      top=0.86, bottom=0.12, wspace=0.10, hspace=0.18)
ax = fig.add_subplot(gs[:, 0])
az = fig.add_subplot(gs[1, 1:])
s0, s1 = fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[0, 2])

# (a) plan view at z = 1.0, to scale
pock = rings(rack, 1.0, 0, 0, "hole")[0]
nub = rings(key, 1.0, 0, 0, "solid")[0]
ax.set_facecolor(SURF)
ax.add_patch(Rectangle((-5.6, -5.8), 11.2, 10.8, color=GREY, lw=0, zorder=0))
ax.fill(pock[:, 0], pock[:, 1], color=SURF, zorder=1)
ax.plot(pock[:, 0], pock[:, 1], color=RACK_C, lw=2.0, zorder=3, label="pocket in the rack (R1.1, 2.1 deep)")
ax.plot(nub[:, 0], nub[:, 1], color=KEY_C, lw=2.0, zorder=4, label="key's nub (R1.15, 2.0 tall)")
yb, yt = -(3.1 + 1.15), 3.1 / 2 + 1.15
xa = 3.1 * math.sqrt(3) / 2 + 1.15
ax.annotate("", (4.75, yb), (4.75, yt), arrowprops=dict(arrowstyle="<->", color=INK2, lw=1))
for yy in (yb, yt):
    ax.plot([0.3, 4.95], [yy, yy], color=MUTED, lw=0.6, ls=":")
ax.text(4.9, (yb + yt) / 2, " A", va="center", fontsize=12, fontweight="bold", color=INK2)
ax.annotate("", (-xa, 4.1), (xa, 4.1), arrowprops=dict(arrowstyle="<->", color=INK2, lw=1))
for xx in (-xa, xa):
    ax.plot([xx, xx], [3.1 / 2, 4.3], color=MUTED, lw=0.6, ls=":")
ax.text(0, 4.25, "B", ha="center", va="bottom", fontsize=12, fontweight="bold", color=INK2)
ax.annotate("−y (toward vial 2)", (0, -5.55), (0, -4.6), ha="center", va="center", fontsize=9, color=INK2,
            arrowprops=dict(arrowstyle="->", color=INK2, lw=1))
ax.text(-5.45, 4.75, "rack underside", fontsize=9, color=INK2, va="top")
ax.legend(loc="lower left", bbox_to_anchor=(0.0, -0.13), frameon=False, fontsize=9.5)
ax.set_xlim(-5.6, 5.9)
ax.set_ylim(-6.0, 5.2)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Pocket and nub at z = 1 mm, seen from above, to scale (mm)", fontsize=10.5, loc="left")

# (b), (c) sections through the assembly: rack, key, and the deck plate with its slot
for axs, y0, title in ((s0, 0.0, "Section through the nub (y = 0)"),
                       (s1, 5.0, "Section through the barbs (y = 5)")):
    axs.set_facecolor(SURF)
    axs.add_patch(Rectangle((-9.5, -DECK_T), 9.5 - SLOT_HALF_W, DECK_T, color=GREY, lw=0, zorder=0))
    axs.add_patch(Rectangle((SLOT_HALF_W, -DECK_T), 9.5 - SLOT_HALF_W, DECK_T, color=GREY, lw=0, zorder=0))
    for pg in xz_section(rack, y0):
        axs.add_patch(patch(pg, fc=RACK_C, ec=RACK_C, alpha=0.30, lw=0, zorder=1))
        axs.add_patch(patch(pg, fc="none", ec=RACK_C, lw=1.2, zorder=3))
    for pg in xz_section(key, y0):
        axs.add_patch(patch(pg, fc=KEY_C, ec=KEY_C, alpha=0.35, lw=0, zorder=2))
        axs.add_patch(patch(pg, fc="none", ec=KEY_C, lw=1.2, zorder=4))
    axs.text(-9.3, -DECK_T / 2, "deck\n10 mm", fontsize=8.5, color=INK2, va="center")
    axs.text(-9.3, 3.2, "rack", fontsize=8.5, color=INK2, va="center")
    axs.set_xlim(-9.5, 9.5)
    axs.set_ylim(-19.0, 6.2)
    axs.set_aspect("equal")
    axs.axis("off")
    axs.set_title(title, fontsize=10.5, loc="left")
s0.annotate("0.1 mm over the nub", (0.0, 2.05), (3.4, 4.7), fontsize=8.5, color=INK2,
            arrowprops=dict(arrowstyle="->", color=INK2, lw=0.8))
s0.annotate("latch arms, joined to the key\nat its \u2212y end", (-4.4, -14.0), (-4.4, -17.4), fontsize=8.5,
            color=INK2, ha="center", va="center", arrowprops=dict(arrowstyle="->", color=INK2, lw=0.8))
d10 = PRELOAD[10.0]
s1.annotate(f"barbs, drawn unflexed: on a 10 mm deck each arm\nstays {d10[0]:.2f} mm in, and its ramp pulls the key "
            f"down ~{d10[1]:.0f} N", (5.25, -9.9), (0.0, -17.4), fontsize=8.5, color=INK2, ha="center", va="center",
            arrowprops=dict(arrowstyle="->", color=INK2, lw=0.8))

# (d) the sizes, and where else this pocket is
az.axis("off")
cols = (0.0, 0.47, 0.57, 0.68, 0.85, 1.0)
head = ("measured from the meshes", "A", "B", "corner R", "depth / height", "fit, a side")
for j, h in enumerate(head):
    az.text(cols[j], 0.94, h, ha="left" if j == 0 else "right", fontsize=9.5, color=INK2, transform=az.transAxes)
az.plot([0, 1], [0.88, 0.88], color=MUTED, lw=0.6, transform=az.transAxes)
tab = [("pocket, this rack (both)", p0, f"{depth(rack, 0, 0.0):.2f}", "", RACK_C),
       ("pocket, PANDA-BEAR 9-vial holder", fit(rings(orig, 1.0, 0, 0, "hole")[0]), f"{depth(orig, 0, 0):.2f}", "", INK2),
       ("pocket, stir module base", fit(rings(base, 1.0, 12.5, 0, "hole")[0]), f"{depth(base, 12.5, 0):.2f}", "", INK2),
       ("nub, this key", kn, f"{key.bounds[1][2]:.2f}", f"{(kn['A'] - p0['A']) / 2:+.3f} press", KEY_C),
       ("nub, stir module key (Ben's 0.05)", sn, f"{sk.bounds[1][2]:.2f}", f"{(sn['A'] - p0['A']) / 2:+.3f} press", INK2)]
for i, (name, d, dz, f, c) in enumerate(tab):
    y = 0.74 - 0.155 * i
    az.plot([0.0, 0.025], [y + 0.03, y + 0.03], color=c, lw=2.4, transform=az.transAxes)
    cells = (name, f"{d['A']:.2f}", f"{d['B']:.2f}", f"{d['r']:.2f}", dz, f)
    for j, cell in enumerate(cells):
        az.text(cols[j] + (0.04 if j == 0 else 0), y, cell, ha="left" if j == 0 else "right", fontsize=9.5,
                color=INK, transform=az.transAxes)

fig.suptitle("Clip-in deck key with the triangle nub: 0.05 mm a side over Cubware's pocket, as on the stir module",
             x=0.02, y=0.975, ha="left", fontsize=13, fontweight="bold", color=INK)
fig.text(0.02, 0.915, "deck_clip_key_v2_1_tri in vial_rack_9x20mL_v2_tri. Below the deck top the key is v2_1 "
         "unchanged; only the stem became the nub.", fontsize=9.5, color=INK2)
fig.text(0.02, 0.02, "A: one caliper jaw on a flat, the other on the opposite corner. B: jaws parallel to a flat. "
         "Sections drawn from the STLs; the deck is Cubware's 10 mm plate with a 10 mm slot.\n"
         "Made by cad/check_tri_fit.py, which also writes cad/tri_fit_output.txt.", fontsize=8.8, color=INK2)
fig.savefig(V2 / "img" / "tri_fit.png", facecolor=SURF)
print("wrote img/tri_fit.png and cad/tri_fit_output.txt")
