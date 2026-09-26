"""Renders of the rePowder charge CAD (issue #222).

Tessellates the build123d solids from ``charge_cad.py`` straight into PyVista,
draws the true CAD edges in black and gives cut faces a flat, lighter tint so
sections read clearly.  Callouts and dimension lines are drawn with matplotlib
at the projected 3D anchor points.

Usage (VTK needs an X server; on a headless runner wrap it in xvfb-run):
    xvfb-run -a python render.py
"""

from __future__ import annotations

import math
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv
from build123d import Align, Box, GeomType, Pos, Rot

import charge_cad as cad

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "renders"
SS = 2  # supersampling factor

INK = "#0b0b0b"
INK2 = "#52514e"
EDGE = "#1b1b1b"
ALERT = "#d03b3b"
# white halo so leader lines stay visible over the dark graphite
HALO = [pe.withStroke(linewidth=2.4, foreground="white")]

# Physical materials get realistic tints: (body, cut face)
MAT = {
    "al": ("#c9ced5", "#eef0f3"),
    "graphite": ("#55585d", "#9a9ea4"),
    "rod": ("#dcd6c8", "#f3efe6"),
    "copper": ("#b87333", "#e0a672"),
    "steel": ("#8e9aa8", "#c3ccd7"),
    "insulation": ("#e9e4d8", "#f6f3ec"),
}
# Powders are the categorical data: validated palette (all-pairs CVD pass)
POWDER = {
    "AlSi10Mg": "#2a78d6",
    "Si": "#eb6834",
    "mix": "#1baf7a",
    "Al_UA": "#4a3aa7",
}

BODY = dict(smooth_shading=True, ambient=0.32, diffuse=0.72, specular=0.28, specular_power=18)
CUT = dict(smooth_shading=False, ambient=0.78, diffuse=0.26, specular=0.0)
CUT_POWDER = dict(smooth_shading=False, ambient=0.92, diffuse=0.12, specular=0.0)


# ---------------------------------------------------------------------------
# build123d -> PyVista
# ---------------------------------------------------------------------------
def face_poly(face, tol=0.02, ang=0.15) -> pv.PolyData:
    verts, tris = face.tessellate(tol, ang)
    if not tris:
        return pv.PolyData()
    pts = np.array([[v.X, v.Y, v.Z] for v in verts])
    poly = pv.PolyData(pts, np.hstack([[3, *t] for t in tris]))
    # normals per face, so flat faces stay flat and curved faces stay smooth
    return poly.compute_normals(cell_normals=False, point_normals=True, split_vertices=False)


def merged(polys):
    polys = [p for p in polys if p.n_points]
    if not polys:
        return None
    return pv.merge(polys, merge_points=False) if len(polys) > 1 else polys[0]


def is_cut_face(face, y0=0.0) -> bool:
    if face.geom_type != GeomType.PLANE:
        return False
    bb = face.bounding_box()
    return abs(bb.min.Y - y0) < 1e-6 and abs(bb.max.Y - y0) < 1e-6


def halve(shape):
    """Keep y >= 0; the camera looks from -Y, so the cut faces point at it."""
    return shape - Box(400, 200, 600, align=(Align.CENTER, Align.MAX, Align.CENTER))


def edge_lines(shape, n=72) -> pv.PolyData:
    pieces = []
    for e in shape.edges():
        ts = [0.0, 1.0] if e.geom_type == GeomType.LINE else np.linspace(0, 1, n)
        pts = np.array([[p.X, p.Y, p.Z] for p in (e @ t for t in ts)])
        pieces.append(pv.lines_from_points(pts))
    return pieces[0].merge(pieces[1:]) if pieces else pv.PolyData()


def add_solid(pl, shape, mat, cut=True, edges=True, lw=1.1, tol=0.02, powder=False):
    body_c, cut_c = mat if isinstance(mat, tuple) else (mat, mat)
    solid = halve(shape) if cut else shape
    body, section = [], []
    for f in solid.faces():
        (section if cut and is_cut_face(f) else body).append(f)
    mesh = merged([face_poly(f, tol) for f in body])
    if mesh is not None:
        pl.add_mesh(mesh, color=body_c, **BODY)
    mesh = merged([face_poly(f, tol) for f in section])
    if mesh is not None:
        pl.add_mesh(mesh, color=cut_c, **(CUT_POWDER if powder else CUT))
    if edges:
        pl.add_mesh(edge_lines(solid), color=EDGE, line_width=lw * SS)
    return solid


def new_plotter(w, h) -> pv.Plotter:
    pl = pv.Plotter(off_screen=True, window_size=(w * SS, h * SS), lighting="light_kit")
    pl.set_background("white")
    return pl


def project(pl, pts) -> np.ndarray:
    """World -> image pixel coords (x right, y down) in the supersampled frame."""
    ren = pl.renderer
    h = pl.window_size[1]
    out = []
    for x, y, z in pts:
        ren.SetWorldPoint(x, y, z, 1.0)
        ren.WorldToDisplay()
        dx, dy, _ = ren.GetDisplayPoint()
        out.append((dx, h - dy))
    return np.array(out).reshape(-1, 2)


def finish(pl, path, callouts=(), dims=(), title=None, subtitle=None, fontsize=11, dpi=100):
    """Screenshot, then draw callouts and dimension lines with matplotlib.

    callouts: (text, xyz, (tx, ty) as fractions of the frame, ha)
    dims:     dict(p1=xyz, p2=xyz, text=str, t=0..1 along the line, off=(dx, dy) px,
                   ext=[(xyz_from, xyz_to), ...] extension lines)
    """
    img = pl.screenshot(return_img=True)
    h, w = img.shape[:2]
    anchors = project(pl, [c[1] for c in callouts]) if callouts else []
    dim_px = []
    for d in dims:
        p = project(pl, [d["p1"], d["p2"]])
        ext = [project(pl, e) for e in d.get("ext", [])]
        dim_px.append((p, ext))
    pl.close()

    fig = plt.figure(figsize=(w / (dpi * SS), h / (dpi * SS)), dpi=dpi * SS)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img)
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.axis("off")
    for (text, _, (tx, ty), ha), (x, y) in zip(callouts, anchors):
        ax.annotate(
            text,
            xy=(x, y),
            xytext=(tx * w, ty * h),
            fontsize=fontsize,
            color=INK,
            ha=ha,
            va="center",
            linespacing=1.25,
            arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8, shrinkA=3, shrinkB=0, path_effects=HALO),
        )
        ax.plot([x], [y], "o", ms=3.4, color=INK2, markeredgecolor="white", markeredgewidth=0.7)
    for d, (p, ext) in zip(dims, dim_px):
        for e in ext:
            ax.plot(e[:, 0], e[:, 1], color=INK2, lw=0.7, path_effects=HALO)
        ax.annotate(
            "",
            xy=p[1],
            xytext=p[0],
            arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=0.9, mutation_scale=8 * SS, shrinkA=0, shrinkB=0,
                            path_effects=HALO),
        )
        t = d.get("t", 0.5)
        mx, my = p[0] + t * (p[1] - p[0])
        dx, dy = d.get("off", (0, -14))
        ax.text(mx + dx * SS, my + dy * SS, d["text"], fontsize=fontsize, color=INK, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    if title:
        ax.text(0.02 * w, 0.045 * h, title, fontsize=fontsize + 4, color=INK, weight="bold", va="center")
    if subtitle:
        ax.text(0.02 * w, 0.045 * h + 30 * SS, subtitle, fontsize=fontsize - 0.5, color=INK2, va="center")
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    print("wrote", path.relative_to(HERE))


# ---------------------------------------------------------------------------
# Scene pieces
# ---------------------------------------------------------------------------
def cup_with_fill(pl, parts, powder_key, powder_solid=None, loc=None, cut=True, lw=1.1):
    loc = loc if loc is not None else Pos(0, 0, 0)
    add_solid(pl, loc * parts["std_cup"], MAT["al"], cut=cut, lw=lw)
    add_solid(pl, loc * Pos(0, 0, cad.SLUG_L - cad.PLUG_L) * parts["std_plug"], MAT["al"], cut=cut, lw=lw)
    add_solid(pl, loc * (powder_solid or parts["std_powder"]), POWDER[powder_key], cut=cut, lw=lw * 0.6, powder=True)


def context(pl, parts, lw=1.0):
    add_solid(pl, parts["crucible"], MAT["graphite"], lw=lw)
    add_solid(pl, parts["filling_cone"], MAT["insulation"], lw=lw)
    add_solid(pl, parts["sealing_rod"], MAT["rod"], lw=lw)
    add_solid(pl, parts["rod_holder"], MAT["steel"], lw=lw)
    add_solid(pl, parts["coil"], MAT["copper"], lw=lw * 0.5, tol=0.05)


FOCAL_Z = 60
CAM_3D = [(185, -430, 195 + FOCAL_Z), (0, 0, FOCAL_Z), (0, 0, 1)]
RIM = cad.BORE_STRAIGHT
ADAPTER_Z = RIM + cad.ROD_ADAPTER_ABOVE_RIM


def coil_z_left(k):
    """Height of the k-th coil turn where it crosses the section plane on the left (x < 0)."""
    return cad.COIL_Z0 + cad.COIL_PITCH * (k + 0.5)


def hero(parts):
    pl = new_plotter(1500, 1080)
    context(pl, parts)
    r, zb = cad.SLUG_CIRCLE_R, cad.slug_base_z()
    for ang in (0, 90, 180):  # the 270 deg cup is in the cut-away front half
        cup_with_fill(pl, parts, "AlSi10Mg", loc=Rot(0, 0, ang) * Pos(r, 0, zb), cut=(ang != 90))
    pl.enable_parallel_projection()
    pl.camera_position = CAM_3D
    pl.camera.parallel_scale = 110
    ri, ro = cad.CRUCIBLE_ID / 2, cad.CRUCIBLE_ID / 2 + cad.CRUCIBLE_WALL
    cone_deg = math.degrees(math.atan(cad.FLOOR_CONE_H / ri))
    callouts = [
        ("the rod's adapter and its arm stay\nover the crucible while it is filled",
         (-cad.ROD_ADAPTER_D / 2 + 1.5, 0, ADAPTER_Z + 38), (0.045, 0.115), "left"),
        ("don't fill past here", (-0.8 * cad.CRUCIBLE_ID, 0, cad.CRUCIBLE_MAX_FILL), (0.045, 0.235), "left"),
        (f"graphite crucible: {cad.BORE_STRAIGHT:.0f} mm straight,\nthen a {cone_deg:.0f}° cone to the pour hole",
         (-(ri + ro) / 2, 0, 45), (0.045, 0.45), "left"),
        ("induction coil", (-cad.COIL_RADIUS, 0, coil_z_left(2)), (0.045, 0.66), "left"),
        ("melt pours out here", (0, 0, -cad.FLOOR_CONE_H - cad.CRUCIBLE_BOTTOM), (0.045, 0.92), "left"),
        ("sealing rod: seated before\nloading, lifts to pour", (2.5, 0, RIM - 6), (0.67, 0.28), "left"),
        ("lid, with the air hole", (r + 4.5, 0, 59 + zb), (0.74, 0.41), "left"),
        ("powder", (r + 2.5, 0, 38 + zb), (0.74, 0.55), "left"),
        ("cup: 3/4 in bar, 2.5 in long\ntwo per run; four fit", (r + 8.8, 0, 22 + zb), (0.74, 0.69), "left"),
        ("cups stand on the floor cone", (r + 9.3, 0, zb + 0.3), (0.74, 0.83), "left"),
    ]
    dims = [
        dict(p1=(-ri, 0, 71), p2=(-cad.SEALING_ROD_D / 2, 0, 71), text=f"{(cad.CRUCIBLE_ID - cad.SEALING_ROD_D) / 2:.0f}",
             off=(0, -9)),
        dict(p1=(-ri, 0, ADAPTER_Z + 9), p2=(ri, 0, ADAPTER_Z + 9), text=f"Ø{cad.CRUCIBLE_ID:.0f}", t=0.2, off=(0, -10),
             ext=[((-ri, 0, RIM + 7), (-ri, 0, ADAPTER_Z + 12)), ((ri, 0, RIM + 7), (ri, 0, ADAPTER_Z + 12))]),
    ]
    finish(pl, OUT / "crucible_cutaway.png", callouts, dims,
           title="Where the cups go, cut in half",
           subtitle="The crucible is Indutherm's section drawing scaled to AMAZEMET's 225 cm³ (repowder-reference). "
                    "Measure ours before anything is cut.")


def plan(parts, cups, path, title, callouts, dims=(), holder=False, outlines=()):
    """Plan view looking down into the crucible: cups at the given (x, y) centres,
    and red (x, y, radius) outlines drawn over everything."""
    pl = new_plotter(820, 860)
    add_solid(pl, parts["crucible"], MAT["graphite"], cut=False)  # filling cone left off, for clarity
    add_solid(pl, parts["sealing_rod"], MAT["rod"], cut=False)
    if holder:
        add_solid(pl, parts["rod_holder"], MAT["steel"], cut=False)
    zb = cad.slug_base_z()
    for c in cups:
        loc = Pos(*c, zb)
        add_solid(pl, loc * parts["std_cup"], MAT["al"], cut=False)
        add_solid(pl, loc * Pos(0, 0, cad.SLUG_L - cad.PLUG_L) * parts["std_plug"], MAT["al"], cut=False)
    for x, y, rad in outlines:
        ring = pv.Circle(radius=rad, resolution=120).extract_feature_edges()
        pl.add_mesh(ring.translate((x, y, 200)), color=ALERT, line_width=1.8 * SS)
    pl.enable_parallel_projection()
    pl.camera_position = [(0, 0, 400), (0, 0, 0), (0, 1, 0)]
    pl.camera.parallel_scale = 47
    finish(pl, path, callouts, dims, title=title, fontsize=12)


def polar(r, deg, z):
    return (r * math.cos(math.radians(deg)), r * math.sin(math.radians(deg)), z)


def top_view(parts):
    ri, rr, rs = cad.CRUCIBLE_ID / 2, cad.SEALING_ROD_D / 2, cad.STOCK_D / 2
    ra = cad.ROD_ADAPTER_D / 2
    rc = cad.SLUG_CIRCLE_R
    gap4 = cad.packing(4, hot=True, lean="rod")  # tightest case
    z = 205
    gap = (cad.CRUCIBLE_ID - cad.SEALING_ROD_D) / 2
    c4 = [
        ("the sealing rod", polar(rr * 0.99, -45, z), (0.80, 0.93), "left"),
        (f"3/4 in cups stay ≥{math.floor(gap4 * 10) / 10:.1f} mm apart,\neven hot and however they lean",
         polar(rc * math.cos(math.radians(45)), 45, z), (0.55, 0.10), "left"),
    ]
    dims4 = [
        dict(p1=polar(ri, 225, z), p2=polar(ri, 45, z), text=f"Ø{cad.CRUCIBLE_ID:.0f}", t=0.18, off=(0, 0)),
        dict(p1=polar(rr, 135, z), p2=polar(ri, 135, z), text=f"{gap:.0f}", t=0.5, off=(0, 0)),
    ]
    # One 3/4" cup dropped straight down against the wall, away from the arm
    ang = 225.0
    rw = ri - rs
    cup = polar(rw, ang, 0)[:2]
    fit = cad.loading_margin(cad.STOCK_D, cad.SLUG_L)
    s, t = fit["straight_down_mm"], fit["tipped_in_mm"]
    straight = f"still reaches {-s:.2f} mm under the adapter" if s < 0 else f"clears the adapter by {s:.2f} mm"
    tipped = f"it is {-t:.2f} mm too big" if t < 0 else f"it clears by {t:.2f} mm"
    band = ri - ra
    c5 = [
        ("the rod's adapter hangs over the\nmiddle, and hides the rod from above",
         polar(ra * 0.55, 100, z), (0.04, 0.10), "left"),
        ("its arm", polar(ra + 22, cad.ARM_ANGLE, z), (0.80, 0.10), "left"),
        (f"dropped straight in against the wall, a 3/4 in cup\n{straight}.\nTipped in, {tipped}: too close to call, so try one",
         polar(ri - 2 * rs, ang, z), (0.04, 0.92), "left"),
    ]
    dims5 = [
        dict(p1=polar(ra, 135, z), p2=polar(ri, 135, z), text=f"{band:.1f}", t=0.5, off=(0, 0)),
        dict(p1=polar(ri - 2 * rs, ang, z), p2=polar(ri, ang, z), text=f"{cad.STOCK_D:.2f}", t=0.55, off=(12, 9)),
    ]
    p4, p5 = OUT / "_plan4.png", OUT / "_plan5.png"
    plan(parts, [polar(rc, 90 * k + 90, 0)[:2] for k in range(4)], p4, "Four cups fit around the rod", c4, dims4)
    plan(parts, [cup], p5, "…if they can get past its adapter", c5, dims5, holder=True,
         outlines=[(*cup, rs)])
    a4, a5 = plt.imread(p4), plt.imread(p5)
    fig = plt.figure(figsize=((a4.shape[1] + a5.shape[1]) / 100, a4.shape[0] / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(np.hstack([a4, a5]))
    ax.axis("off")
    fig.savefig(OUT / "crucible_top.png", dpi=100)
    plt.close(fig)
    p4.unlink()
    p5.unlink()
    print("wrote renders/crucible_top.png")


def ring_concept(parts):
    pl = new_plotter(1500, 1080)
    context(pl, parts)
    zr = cad.ring_base_z()
    add_solid(pl, Pos(0, 0, zr) * parts["ring_cup"], MAT["al"])
    add_solid(pl, Pos(0, 0, zr + cad.RING_H - cad.RING_PLUG_L) * parts["ring_plug"], MAT["al"])
    add_solid(pl, Pos(0, 0, zr) * parts["ring_powder"], POWDER["AlSi10Mg"], lw=0.6, powder=True)
    pl.enable_parallel_projection()
    pl.camera_position = CAM_3D
    pl.camera.parallel_scale = 110
    ro = cad.RING_OD / 2
    wall = (cad.CRUCIBLE_ID - cad.RING_OD) / 2
    callouts = [
        (f"Would have to go in before the rod, which is\nseated before loading: the ring's Ø{cad.RING_ID:.0f} hole "
         f"can't\npass the Ø{cad.ROD_ADAPTER_D:.0f} adapter, and the furnace must\nnever run without the rod",
         (-cad.ROD_ADAPTER_D / 2 + 1.5, 0, ADAPTER_Z + 38), (0.045, 0.14), "left"),
        ("Washer plug, vented", ((cad.RING_GROOVE_ID + cad.RING_GROOVE_OD) / 4, 0, zr + cad.RING_H - 3), (0.73, 0.37), "left"),
        ("Annular groove: 37 cm³ of powder\n(~60 g AlSi10Mg), 244 g charge", ((cad.RING_GROOVE_ID + cad.RING_GROOVE_OD) / 4, 0, zr + 30), (0.73, 0.52), "left"),
        (f"Ring Ø{cad.RING_OD:.0f} × Ø{cad.RING_ID:.0f} × {cad.RING_H:.0f} from 2\" bar;\n{wall:.1f} mm/side to the wall",
         (ro - 1, 0, zr + 8), (0.73, 0.70), "left"),
        ("Four thin-wall 3/4\" × 100 mm cups\nwould hold ~2× this powder\n(73 vs 37 cm³)", (-ro + 2, 0, zr + 45), (0.04, 0.47), "left"),
    ]
    finish(pl, OUT / "ring_concept.png", callouts,
           title="Concept only: one annular cup over the sealing rod",
           subtitle="Same crucible, rod and holder as the cutaway. Not in the BOM.")


# ---------------------------------------------------------------------------
# Insets: one common scale, bases aligned, so size differences are real
# ---------------------------------------------------------------------------
INSET_SCALE = 41.0
INSET_DIR = np.array([0.95, -1.0, 0.62])


def inset(name, build, focal_z, scale=INSET_SCALE, px=300):
    pl = new_plotter(px, px)
    build(pl)
    pl.enable_parallel_projection()
    d = INSET_DIR / np.linalg.norm(INSET_DIR)
    fp = np.array([0, 0, focal_z])
    pl.camera_position = [tuple(fp + 500 * d), tuple(fp), (0, 0, 1)]
    pl.camera.parallel_scale = scale
    img = pl.screenshot(return_img=True)
    pl.close()
    fig = plt.figure(figsize=(px / 100, px / 100), dpi=100 * SS)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img)
    ax.axis("off")
    path = OUT / "insets" / f"{name}.png"
    fig.savefig(path, dpi=100)
    plt.close(fig)
    print("wrote", path.relative_to(HERE))


def insets(parts):
    (OUT / "insets").mkdir(parents=True, exist_ok=True)
    L = cad.SLUG_L
    std_floor = cad.SLUG_L - cad.CUP_BORE_DEPTH
    si_only = cad.powder_column(4.64, cad.RHO["Si_tap"], cad.CUP_BORE_D, std_floor, point=True)
    lw = 1.3
    thin_fz = cad.THIN_L / 2 + (L - cad.THIN_L) / 2  # keep bases level with the 2.5" parts

    def exp_cup(key, powder=None):
        return lambda pl: cup_with_fill(pl, parts, key, powder_solid=powder, lw=lw)

    def solid(pl):
        add_solid(pl, parts["solid_slug"], MAT["al"], lw=lw)

    def sleeve(pl):
        cup_with_fill(pl, parts, "AlSi10Mg", lw=lw)
        add_solid(pl, parts["support_sleeve"], MAT["steel"], lw=lw)

    def thin(pl):
        add_solid(pl, parts["thin_cup"], MAT["al"], lw=lw)
        add_solid(pl, Pos(0, 0, cad.THIN_L - cad.THIN_PLUG_L) * parts["thin_plug"], MAT["al"], lw=lw)
        add_solid(pl, parts["thin_powder"], POWDER["AlSi10Mg"], lw=lw * 0.6, powder=True)

    def ring(pl):
        add_solid(pl, parts["ring_cup"], MAT["al"], lw=lw)
        add_solid(pl, Pos(0, 0, cad.RING_H - cad.RING_PLUG_L) * parts["ring_plug"], MAT["al"], lw=lw)
        add_solid(pl, parts["ring_powder"], POWDER["AlSi10Mg"], lw=lw * 0.6, powder=True)

    inset("E1_alsi10mg_cup", exp_cup("AlSi10Mg"), L / 2)
    inset("E2_solid_slug", solid, L / 2)
    inset("E3_mix_cup", exp_cup("mix"), L / 2)
    inset("E4_pressed_in_sleeve", sleeve, L / 2)
    inset("E5_si_cup", exp_cup("Si", si_only), L / 2)
    inset("E6_al_powder_cup", exp_cup("Al_UA"), L / 2)
    inset("E7_thin_cup", thin, thin_fz)

    inset("P_solid_slug", solid, L / 2)
    inset("P_std_cup", lambda pl: add_solid(pl, parts["std_cup"], MAT["al"], lw=lw), L / 2)
    inset("P_thin_cup", lambda pl: add_solid(pl, parts["thin_cup"], MAT["al"], lw=lw), thin_fz)
    # plugs are tiny at the common scale: shown ~3x, sectioned to show vent + lead-in
    inset("P_std_plug", lambda pl: add_solid(pl, parts["std_plug"], MAT["al"], lw=lw), cad.PLUG_L / 2, scale=13)
    inset("P_thin_plug", lambda pl: add_solid(pl, parts["thin_plug"], MAT["al"], lw=lw), cad.THIN_PLUG_L / 2, scale=13)
    inset("F_support_sleeve", lambda pl: add_solid(pl, parts["support_sleeve"], MAT["steel"], lw=lw), L / 2)
    inset("C_ring_cup", ring, cad.RING_H / 2 + (L - cad.RING_H) / 2)


def main():
    OUT.mkdir(exist_ok=True)
    parts = cad.build()
    hero(parts)
    top_view(parts)
    ring_concept(parts)
    insets(parts)


if __name__ == "__main__":
    main()
