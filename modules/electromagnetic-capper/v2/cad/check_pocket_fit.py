#!/usr/bin/env python3
"""Check the pocket-fit keys (2026-11-23) against the original tip rack's and 9-vial holder's pockets.

The 0.05 mm triangle-nub keys printed on 2026-11-20 didn't go into the original tip rack or the
original 9-vial holder (@benwhitney5463 on #354). This measures, from the meshes:
  - the key pockets of Cubware's TipRack.stl and 9VialHolder.step (fetched at a pinned commit and
    checked by sha256), of the stir module's base.stl and of the v2 tri rack;
  - the nubs of the stir module's deck_key.stl, of the 2026-11-20 3-dot key and of the two new keys;
then gives each key's fit a side in each pocket, presses each new key into its own part's pocket
(mesh boolean) to see where they overlap, and checks that below the top face the new keys are the
3-dot key unchanged. Each outline is fitted as a sharp equilateral triangle of circumradius R grown
all round by r, and reported as A (corner to the opposite flat) and B (across two corners), the
caliper sizes used in hardware/vial-stirrer-cubxl/analysis/key_fit.py and check_tri_fit.py.

    python cad/check_pocket_fit.py [cache_dir]

Writes cad/pocket_fit_output.txt and img/pocket_fit.png. Needs trimesh, manifold3d, shapely,
networkx, matplotlib and cadquery (for the STEP file).
"""
from __future__ import annotations

import hashlib
import io
import math
import pathlib
import sys
import tempfile
import urllib.parse
import urllib.request
import warnings

import numpy as np
import trimesh

warnings.filterwarnings("ignore", category=DeprecationWarning)

V2 = pathlib.Path(__file__).resolve().parent.parent
ROOT = V2.parents[2]
STIR = ROOT / "hardware" / "vial-stirrer-cubxl" / "stl"
OLD = V2 / "stl" / "width_sweep" / "deck_clip_key_v2_1_tri_w10.4_c0.1.stl"
NEW = {"tiprack": V2 / "stl" / "pocket_fit" / "deck_clip_key_v2_1_tri_w10.4_tiprack.stl",
       "vialholder": V2 / "stl" / "pocket_fit" / "deck_clip_key_v2_1_tri_w10.4_vialholder.stl"}
CUBWARE = "0d9e2db638fa7eec6f5097e1e85c195a9205a3a8"     # Ursa-Laboratories/Cubware, 2026-11-23
FILES = {"TipRack.stl": ("cubxl_plus/labware/tip_rack_holder/TipRack.stl",
                         "4a7e64a91d1cf57d"),   # sha256 prefix; same file as hardware/cubxl/ursa_tip_rack_20ul (#151)
         "9VialHolder.step": ("cubxl_plus/labware/vial_holder/9VialHolder.step", "cbc3cc531f3efd05"),
         "9VialHolder-key.step": ("cubxl_plus/labware/vial_holder/9VialHolder-key.step", "48f537baa256339f")}

out = io.StringIO()


def say(*a):
    print(*a)
    print(*a, file=out)


def fetch(cache):
    cache.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, (path, sha) in FILES.items():
        f = cache / name
        if not f.exists():
            url = f"https://raw.githubusercontent.com/Ursa-Laboratories/Cubware/{CUBWARE}/" + urllib.parse.quote(path)
            urllib.request.urlretrieve(url, f)
        got = hashlib.sha256(f.read_bytes()).hexdigest()
        if not got.startswith(sha):
            sys.exit(f"{name}: sha256 {got[:16]} is not the pinned {sha}")
        paths[name] = f
    return paths


def load_step(path):
    """Mesh a STEP file finely (0.005 mm), keeping the mesh next to it so a rerun is quick."""
    stl = path.with_suffix(".meshed.stl")
    if not stl.exists():
        import cadquery as cq

        cq.exporters.export(cq.importers.importStep(str(path)), str(stl), tolerance=0.005, angularTolerance=0.05)
    return trimesh.load(stl)


def section_2d(mesh, z):
    s = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if s is None:
        return []
    to2d = getattr(s, "to_2D", None) or s.to_planar
    return to2d(to_2D=np.eye(4))[0].polygons_full


def rings(mesh, z, x0, y0, kind):
    """Outlines up to 12 mm across within 6 mm of (x0, y0) at height z: holes or outer outlines."""
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
    """Centre, A, B, R, r and corner directions of a rounded equilateral triangle (check_tri_fit.py)."""
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
    return {"c": c, "A": A, "B": B, "R": R, "r": r, "corners": corners, "pts": pts}


def depth(mesh, x0, y0, lo=1.0, hi=3.0):
    """Height of the roof of the hole near (x0, y0), by bisection between lo (hole) and hi (none)."""
    for _ in range(18):
        mid = (lo + hi) / 2
        if rings(mesh, mid, x0, y0, "hole"):
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def nub_height(mesh):
    return float(mesh.bounds[1][2])


def row(name, d, extra=""):
    say(f"  {name:46s} A {d['A']:6.3f}  B {d['B']:6.3f}  R {d['R']:5.3f}  r {d['r']:5.3f}  corners {d['corners']}  {extra}")


cache = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(tempfile.gettempdir()) / "cubware-0d9e2db"
src = fetch(cache)

# ---- the parts, each with its key pockets' centres, bottom face at z = 0 -------------------
tip = trimesh.load(src["TipRack.stl"])                 # 21 x 66 x 138, +y up (top plate at y = 0)
tip.apply_transform(np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float))   # y -> z
tip.apply_translation([0, 0, -tip.bounds[0][2]])
vh = load_step(src["9VialHolder.step"])                 # z = 0 is its bottom, pockets at y = 0 and -225
pill = load_step(src["9VialHolder-key.step"])           # Cubware's own key, glued in per its README
base = trimesh.load(STIR / "base.stl")
rack_tri = trimesh.load(V2 / "stl" / "vial_rack_9x20mL_v2_tri.stl")


def pockets_of(mesh):
    """Every triangle-sized hole 0.5 mm above the bottom face."""
    found = []
    for pg in section_2d(mesh, 0.5):
        for ring in pg.interiors:
            pts = np.array(ring.coords)[:, :2]
            span = pts.max(axis=0) - pts.min(axis=0)
            if 5 < span.max() < 9:
                found.append((pts.max(axis=0) + pts.min(axis=0)) / 2)
    return sorted(found, key=lambda c: (round(c[0], 1), round(c[1], 1)))


say("Triangle key pockets and nubs, measured from the meshes (mm)")
say("A = corner to the opposite flat, B = across two corners parallel to a flat; R, r = the sharp")
say("triangle's circumradius and the corner radius it is grown by. Sections at z = 1.0 unless noted.")
say(f"Cubware files at Ursa-Laboratories/Cubware@{CUBWARE[:7]}, sha256 checked.\n")

say("Pockets (depth = roof of the hole above the part's bottom face):")
P = {}
for label, mesh in (("tip rack, TipRack.stl", tip), ("9-vial holder, 9VialHolder.step", vh),
                    ("stir module, base.stl", base), ("v2 tri rack (not printed)", rack_tri)):
    cs = pockets_of(mesh)
    for c in cs:
        d = fit(rings(mesh, 1.0, *c, "hole")[0])
        d["depth"] = depth(mesh, *c)
        mouth = fit(rings(mesh, 0.05, *c, "hole")[0])
        row(f"{label} @ ({c[0]:.1f}, {c[1]:.1f})", d, f"depth {d['depth']:.2f}  (mouth A {mouth['A']:.3f})")
        P.setdefault(label.split(",")[0], d)
say("  The 9-vial holder in Cubware is byte for byte PANDA-BEAR's 9VialHolder20mL_TightFit.step "
    "(same size), so")
say("  check_tri_fit.py's measurement of that file (A 6.850, B 7.569, 2.1 deep) is the same part.")

say("\nNubs (height = top of the nub above the key's top face):")
N = {}
pn = fit(rings(pill, 1.0, 0, 0, "solid")[0]); pn["h"] = nub_height(pill)
row("Cubware's 9VialHolder-key (glued, per README)", pn, f"height {pn['h']:.2f}")
sk = trimesh.load(STIR / "deck_key.stl")
skc = (sk.bounds[0][:2] + sk.bounds[1][:2]) / 2
sn = fit(np.vstack(rings(sk, 1.0, *skc, "solid"))); sn["h"] = nub_height(sk)
row("stir module deck_key.stl (0.05 press, PETG)", sn, f"height {sn['h']:.2f}")
old = trimesh.load(OLD)
on = fit(rings(old, 1.0, 0, 0, "solid")[0]); on["h"] = nub_height(old)
row("3-dot key of 11-20, w10.4_c0.1 (didn't fit)", on, f"height {on['h']:.2f}")
N["old"] = on
keys = {k: trimesh.load(v) for k, v in NEW.items()}
for k, m in keys.items():
    d = fit(rings(m, 1.0, 0, 0, "solid")[0]); d["h"] = nub_height(m)
    top = fit(rings(m, d["h"] - 0.05, 0, 0, "solid")[0])
    row(f"NEW {NEW[k].stem}", d, f"height {d['h']:.2f}  (A {top['A']:.3f} at the lead-in's top)")
    N[k] = d

say("\nFit, each side (+ = interference, - = clearance), A and B:")
cols = [("tip rack", "tip rack"), ("9-vial holder", "9-vial holder"), ("stir module", "stir module")]
say(f"  {'key':40s}" + "".join(f"{c[0]:>24s}" for c in cols))
for name, d in (("Cubware 9VialHolder-key (glued)", pn), ("stir module deck_key (PETG, best fit)", sn),
                ("3-dot key of 11-20 (didn't fit)", on), ("NEW tiprack key (T)", N["tiprack"]),
                ("NEW vialholder key (V)", N["vialholder"])):
    cells = []
    for _, lab in cols:
        p = P[lab]
        cells.append(f"{(d['A'] - p['A']) / 2:+.3f} {(d['B'] - p['B']) / 2:+.3f}  ")
    say(f"  {name:40s}" + "".join(f"{c:>24s}" for c in cells))
for lab, k in (("tip rack", "tiprack"), ("9-vial holder", "vialholder")):
    say(f"  {lab}: nub {N[k]['h']:.2f} tall in a {P[lab]['depth']:.2f} deep pocket, "
        f"{P[lab]['depth'] - N[k]['h']:.2f} mm under its roof")

say("\nEach new key pressed home in its own part's pocket (key top face on the part's underside;")
say("the key turned to the pocket's corner direction and centred on it):")
OV = {}
for lab, k, mesh in (("tip rack", "tiprack", tip), ("9-vial holder", "vialholder", vh)):
    p, kn = P[lab], N[k]
    key = keys[k].copy()
    # the key's corners are at -90/30/150; turn so one lines up with the pocket's
    best = min(((p["corners"][j] - (-90)) % 360 for j in range(3)), key=lambda a: min(a % 180, 180 - a % 180))
    key.apply_transform(trimesh.transformations.rotation_matrix(math.radians(best), [0, 0, 1]))
    kc = fit(rings(key, 1.0, 0, 0, "solid")[0])["c"]
    key.apply_translation([p["c"][0] - kc[0], p["c"][1] - kc[1], 0])
    window = trimesh.creation.box(extents=[30, 40, 6])
    window.apply_translation([p["c"][0], p["c"][1], 3.0])
    if not mesh.is_volume:
        mesh = mesh.copy()
        mesh.merge_vertices()
        trimesh.repair.fill_holes(mesh)
        trimesh.repair.fix_normals(mesh)
    if not mesh.is_volume:
        say(f"  {lab}: skipped, the part's mesh is not a closed volume (Cubware's TipRack.stl is open); "
            f"the sections above are the check")
        OV[lab] = None
        continue
    part = trimesh.boolean.intersection([mesh, window], engine="manifold")
    ov = trimesh.boolean.intersection([part, key], engine="manifold")
    if ov.is_empty or ov.volume < 1e-6:
        say(f"  {lab}: key turned {best:.0f} deg, no overlap (a slip fit)")
        OV[lab] = None
        continue
    lo, hi = ov.bounds
    perim = float(np.sum(np.linalg.norm(np.diff(p["pts"], axis=0), axis=1)))
    say(f"  {lab}: key turned {best:.0f} deg; overlap {ov.volume:.2f} mm^3 at z {lo[2]:.2f}..{hi[2]:.2f}, "
        f"spread round the {perim:.1f} mm pocket wall: {ov.volume / (perim * (hi[2] - lo[2])):.3f} mm thick")
    OV[lab] = ov

say("\nBelow the engraved letter (z < -0.6), each new key against the 11-20 3-dot key (sections every 0.25 mm):")
for k, m in keys.items():
    worst = 0.0
    for z in np.arange(-14.9, -0.65, 0.25):
        a = section_2d(old, z)
        b = section_2d(m, z)
        if not a and not b:
            continue
        sa = sum(pg.area for pg in a)
        sb = sum(pg.area for pg in b)
        ea = np.vstack([np.array(pg.exterior.coords)[:, :2] for pg in a])
        eb = np.vstack([np.array(pg.exterior.coords)[:, :2] for pg in b])
        worst = max(worst, abs(sa - sb), float(np.abs(ea.min(0) - eb.min(0)).max()), float(np.abs(ea.max(0) - eb.max(0)).max()))
    say(f"  {NEW[k].stem}: largest difference in section area (mm^2) or outline extent (mm), z -14.9 to -0.65: {worst:.4f}")
    marks = [pg for pg in section_2d(m, -0.3)]
    holes = [np.array(r.coords)[:, :2] for pg in marks for r in pg.interiors]
    say(f"    top-face marks at z = -0.3: {len(holes)} recesses, centres "
        + ", ".join(f"({h[:, 0].mean():+.1f}, {h[:, 1].mean():+.1f})" for h in sorted(holes, key=lambda h: (h[:, 1].mean(), h[:, 0].mean()))))
    say(f"    volume {m.volume:.1f} mm^3 (11-20 key {old.volume:.1f}); watertight {m.is_watertight}")

(V2 / "cad" / "pocket_fit_output.txt").write_text(out.getvalue())

# ---------------------------------------------------------------- figure
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK, INK2, MUTED, SURF, GREY = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#dcdad4"
POCK, OLDC, NEWC = "#2a78d6", "#8a8984", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": INK})
fig, axes = plt.subplots(1, 2, figsize=(12.5, 6.6), dpi=110)
fig.patch.set_facecolor(SURF)
for ax, (lab, k, title) in zip(axes, (("tip rack", "tiprack", "Original tip rack (TipRack.stl)"),
                                      ("9-vial holder", "vialholder", "Original 9-vial holder (9VialHolder.step)"))):
    p = P[lab]
    pc = p["pts"] - p["c"]
    # turn the pocket so its corner points to -y, like the keys
    a0 = math.radians(-90 - p["corners"][[abs(((c + 90 + 180) % 360) - 180) for c in p["corners"]].index(
        min(abs(((c + 90 + 180) % 360) - 180) for c in p["corners"]))])
    Rm = np.array([[math.cos(a0), -math.sin(a0)], [math.sin(a0), math.cos(a0)]])
    pc = pc @ Rm.T
    ax.set_facecolor(SURF)
    ax.fill(pc[:, 0], pc[:, 1], color=GREY, lw=0, zorder=0)
    ax.plot(pc[:, 0], pc[:, 1], color=POCK, lw=2.2, zorder=3, label=f"pocket: A {p['A']:.2f}, B {p['B']:.2f}, {p['depth']:.1f} deep")
    o = N["old"]["pts"] - N["old"]["c"]
    ax.plot(o[:, 0], o[:, 1], color=OLDC, lw=1.4, ls="--", zorder=4,
            label=f"11-20 nub (didn't fit): A {N['old']['A']:.2f}, {(N['old']['A'] - p['A']) / 2:+.3f} a side")
    n = N[k]["pts"] - N[k]["c"]
    ax.plot(n[:, 0], n[:, 1], color=NEWC, lw=2.0, zorder=5,
            label=f"new '{'T' if k == 'tiprack' else 'V'}' nub: A {N[k]['A']:.2f}, {(N[k]['A'] - p['A']) / 2:+.3f} a side, "
                  f"{N[k]['h']:.1f} tall")
    ax.set_xlim(-5.2, 5.2)
    ax.set_ylim(-5.6, 4.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=11, loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.01), frameon=False, fontsize=9.5)
fig.suptitle("Pocket-fit keys: each nub sized to its own part's pocket (plan view at z = 1 mm, to scale, mm)",
             x=0.02, ha="left", fontsize=12.5, fontweight="bold")
fig.text(0.02, 0.905, "The differences are a few hundredths of a millimetre, so the lines nearly coincide; "
         "the table in pocket_fit_output.txt has the numbers.", fontsize=9.5, color=INK2)
fig.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.2, wspace=0.08)
fig.savefig(V2 / "img" / "pocket_fit.png", facecolor=SURF)
print("wrote", V2 / "img" / "pocket_fit.png")
