#!/usr/bin/env python3
"""Pictures of the under-deck mock-up (build_under_deck.py), next to today's stack on the 4.6 mm spacer.

    python under-deck/render_under_deck.py section     # img/under_deck_section.png (matplotlib)
    python under-deck/render_under_deck.py plan        # img/under_deck_side_by_side_plan.png (matplotlib)
    xvfb-run -a python under-deck/render_under_deck.py views   # img/under_deck_views.png (PyVista)

Run from hardware/vial-stirrer-cubxl. Today's printed parts are the committed STLs (the compact base and
holder, the carrier, the deck keys, Ben's Ø10 x 4.6 mm spacer). Bought parts are build_under_deck.py's
simplified ones. The deck is drawn 9 mm thick in both.
"""
from __future__ import annotations

import functools
import pathlib
import sys
import tempfile

import numpy as np
import trimesh

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import build_under_deck as ud  # noqa: E402
from build_under_deck import C, DZ, DECK_T  # noqa: E402

TMP = pathlib.Path(tempfile.mkdtemp())
SPACER = 4.6
NEW, NEW2 = (0.96, 0.47, 0.05), (0.98, 0.66, 0.20)
COL = {"deck": (0.78, 0.84, 0.90), "base": (0.33, 0.35, 0.39), "holder": (0.10, 0.58, 0.60), "keys": (0.80, 0.80, 0.74),
       "carrier": (0.93, 0.92, 0.88), "mag_n": (0.85, 0.13, 0.13), "mag_s": (0.15, 0.30, 0.85), "fan": (0.16, 0.16, 0.18),
       "hall": (0.05, 0.05, 0.05), "vial": (0.86, 0.93, 0.97), "cap": (0.25, 0.25, 0.28), "bar": (0.97, 0.97, 0.97),
       "spacer": (1.0, 0.80, 0.25), "collar": NEW, "frame": NEW2, "screws": (0.70, 0.71, 0.74), "inserts": (0.80, 0.62, 0.25)}


def tm(wp, name):
    import cadquery as cq
    p = TMP / f"{name}.stl"
    cq.exporters.export(wp, str(p), tolerance=0.03, angularTolerance=0.2)
    return trimesh.load(str(p))


def stl(rel, dz=0.0, dx=0.0):
    m = trimesh.load(str(ROOT / rel))
    m.apply_translation((dx, 0, dz))
    return m


@functools.lru_cache(None)
def scenes():
    """Both assemblies as {name: [trimesh, ...]} in deck coordinates (z 0 = the deck's top face)."""
    b = ud.bought()
    up = -DZ                            # under-deck frame -> the stirrer's own frame
    lift = C["Z_VIAL"] + SPACER         # today's vial bottom
    under = {"deck": [tm(ud.deck(), "deck_u")], "collar": [tm(ud.collar(), "collar")], "frame": [tm(ud.frame(), "frame")],
             "base": [stl("stl/compact/base_compact.stl", DZ)], "carrier": [stl("stl/magnet_carrier.stl", DZ)],
             "fan": [tm(b["fan"], "fan")], "mag_n": [tm(b["magnets"][0], "mn")], "mag_s": [tm(b["magnets"][1], "ms")],
             "hall": [tm(b["hall"], "hall")], "vial": [tm(b["vial"], "vial")], "cap": [tm(b["cap"], "cap")],
             "bar": [tm(b["bar"], "bar")],
             "screws": [tm(s, f"s{i}") for i, s in enumerate(b["screws"] + b["fan_screws"])],
             "inserts": [tm(s, f"i{i}") for i, s in enumerate(b["inserts"])]}
    import cadquery as cq
    deck_t = ud.box(-50, -56, -DECK_T, 50, 56, 0)
    for i in range(-2, 2):
        for j in (-1, 0, 1):
            deck_t = deck_t.cut(ud.pill(ud.COL / 2 + i * ud.COL, j * ud.ROW, ud.SLOT_W, ud.SLOT_L, -DECK_T - 1, 1))
    sh = lambda m, dz: m.copy().apply_translation((0, 0, dz))  # noqa: E731
    today = {"deck": [tm(deck_t, "deck_t")], "keys": [stl("stl/deck_key.stl"), stl("stl/deck_key.stl", dx=25.0)],
             "base": [stl("stl/compact/base_compact.stl")], "carrier": [stl("stl/magnet_carrier.stl")],
             "holder": [stl("stl/compact/vial_holder_compact.stl")],
             "spacer": [stl("stl/spacer/spacer_d10_h4.6.stl", C["Z_VIAL"])],
             "fan": [sh(under["fan"][0], up)], "mag_n": [sh(under["mag_n"][0], up)], "mag_s": [sh(under["mag_s"][0], up)],
             "hall": [sh(under["hall"][0], up)], "vial": [sh(under["vial"][0], lift)], "cap": [sh(under["cap"][0], lift)],
             "bar": [sh(under["bar"][0], lift)]}
    return today, under


def block(offsets, deck_box):
    """Several under-deck modules, one at each (dx, dy), on one patch of deck (half_x, half_y, cx, cy)."""
    _, under = scenes()
    out = {"deck": [tm(ud.deck(*deck_box), f"deck_{len(offsets)}_{deck_box[2]:g}_{deck_box[3]:g}")]}
    for dx, dy in offsets:
        for k, ms in under.items():
            if k == "deck":
                continue
            out.setdefault(k, []).extend(m.copy().apply_translation((dx, dy, 0)) for m in ms)
    return out


def section_polys(mesh, normal, origin, u):
    """Section of a closed mesh by a vertical plane, as shapely geometry in (distance along u, z)."""
    from shapely.geometry import Polygon
    from functools import reduce
    sec = mesh.section(plane_origin=origin, plane_normal=normal)
    if sec is None:
        return None
    u = np.asarray(u, float)
    polys = [Polygon(np.column_stack([d[:, :2] @ u[:2], d[:, 2]])) for d in sec.discrete if len(d) > 3]
    polys = [p.buffer(0) for p in polys if p.area > 1e-4]
    if not polys:
        return None
    return reduce(lambda a, b: a.symmetric_difference(b), polys)


def draw_geom(ax, g, color, alpha=1.0, z=1, lw=0.6, hatch=None):
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path
    from shapely.geometry.polygon import orient
    geoms = getattr(g, "geoms", [g])
    for p in geoms:
        if p.geom_type != "Polygon" or p.is_empty:
            continue
        p = orient(p, 1.0)
        verts, codes = [], []
        for ring in [p.exterior, *p.interiors]:
            xy = np.asarray(ring.coords)
            verts += xy.tolist()
            codes += [Path.MOVETO] + [Path.LINETO] * (len(xy) - 2) + [Path.CLOSEPOLY]
        ax.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor=(0.1, 0.1, 0.1), lw=lw, alpha=alpha,
                               zorder=z, hatch=hatch))


def dim(ax, x, z0, z1, text, side=1, color="#0b0b0b"):
    ax.annotate("", xy=(x, z0), xytext=(x, z1), arrowprops=dict(arrowstyle="<->", lw=1.1, color=color, shrinkA=0, shrinkB=0),
                zorder=20)
    ax.text(x + side * 1.2, (z0 + z1) / 2, text, ha="left" if side > 0 else "right", va="center", fontsize=8.6,
            color=color, zorder=21, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))


def section():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    today, under = scenes()
    r2 = 1 / np.sqrt(2)
    diag = dict(normal=(r2, -r2, 0), origin=(0, 0, 0), u=(r2, r2, 0))
    rot = trimesh.transformations.rotation_matrix(np.pi / 4, (0, 0, 1))

    def turned(sc):
        """The rotor (carrier, magnets) and the bar turned 45 deg, into the diagonal plane. The Hall sensor stays at -X."""
        out = {}
        for k, ms in sc.items():
            if k == "hall":
                continue
            out[k] = [m.copy().apply_transform(rot) if k in ("carrier", "mag_n", "mag_s", "bar") else m for m in ms]
        return out

    fig, axs = plt.subplots(1, 3, figsize=(21, 8.6), gridspec_kw=dict(width_ratios=[1, 1, 1.45]), facecolor="white")
    panels = [(axs[0], turned(today), diag, "along the diagonal",
               "TODAY: compact stirrer on the deck,\nvial on Ben's 4.6 mm spacer"),
              (axs[1], turned(under), diag, "along the diagonal",
               "MOCK-UP: fan under the deck,\nvial standing on the deck"),
              (axs[2], block([(0, 0), (0, ud.PITCH_Y)], (30, 62, 0, ud.PITCH_Y / 2)),
               dict(normal=(1, 0, 0), origin=(ud.COL / 2, 0, 0), u=(0, 1, 0)), "y",
               f"SIDE BY SIDE, through the slot column at x = {ud.COL / 2:g}:\ntwo modules {ud.PITCH_Y:g} mm apart in Y share its slots")]
    order = ["deck", "keys", "base", "fan", "frame", "carrier", "mag_n", "mag_s", "hall", "holder", "collar", "spacer",
             "inserts", "screws", "vial", "cap", "bar"]
    for ax, sc, plane, lab, title in panels:
        for k in order:
            for m in sc.get(k, []):
                g = section_polys(m, **plane)
                if g is None:
                    continue
                draw_geom(ax, g, COL[k], alpha=0.55 if k == "deck" else (0.6 if k == "vial" else 1.0),
                          z=0 if k == "deck" else 2, hatch="///" if k == "deck" else None)
        ax.axhline(0, color="#999", lw=0.5, ls=":", zorder=0)
        ax.axhline(-DECK_T, color="#999", lw=0.5, ls=":", zorder=0)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=11, fontweight="bold", loc="left")
        ax.set_xlabel(f"{lab}, mm")
        ax.grid(color="#eee", lw=0.5, zorder=-1)
        ax.set_ylim(-38, 94)
    axs[0].set_ylabel("height above the deck's top face, mm")
    for ax in axs[:2]:
        ax.set_xlim(-34, 50)
    axs[2].set_xlim(-30, 78)
    zl = C["Z_VIAL"] + SPACER

    def note(ax, x, z0, z1, text, tx, tz):
        ax.annotate("", xy=(x, z0), xytext=(x, z1), arrowprops=dict(arrowstyle="<->", lw=1.1, color="#0b0b0b", shrinkA=0, shrinkB=0), zorder=20)
        ax.annotate(text, xy=(x, (z0 + z1) / 2), xytext=(tx, tz), fontsize=9, va="center", ha="left", zorder=21,
                    arrowprops=dict(arrowstyle="-", lw=0.6, color="#666"),
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#ccc"))
    m0 = 22.645
    note(axs[0], 4.9, m0, zl, f"magnets to vial bottom: {zl - m0:.1f} mm", 22, 12)
    note(axs[0], 19.5, 0, zl, f"vial bottom {zl:.1f} mm up", 22, 44)
    note(axs[0], 17.0, zl, zl + C["VIAL_H"], f"rim {zl + C['VIAL_H']:.0f} mm\nabove the deck", 22, 70)
    note(axs[1], 4.9, m0 + DZ, 0, f"magnets to vial bottom:\n{-(m0 + DZ):.1f} mm (9 mm deck + 1.2)", 18, 12)
    note(axs[1], 17.0, 0, C["VIAL_H"], f"rim {C['VIAL_H']:.0f} mm above the deck,\n{zl:.0f} mm lower than today", 20, 44)
    note(axs[1], -27.0, DZ, -DECK_T, f"hangs {-DZ - DECK_T:.1f} mm\nunder the deck", 18, -30)
    axs[1].text(-33, 84, "Rotor and bar drawn turned 45 deg,\ninto the section plane through the\nfingers; the Hall sensor is at -X,\nout of this plane.", fontsize=8, va="top", color="#444")
    axs[2].text(-28, 86, "Each module uses only the half of a slot nearest its vial.\nHere: the lower module's clamp (M3 x 12 into an insert in\nits frame's boss) and the upper one's key share the slot\nat y 10 to 35, 1 mm apart. Keys go 3 mm into the slot,\nbosses 5 mm, so they miss each other by 1 mm.",
                fontsize=8.4, va="top", ha="left", bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#bbb"))
    for yv, lab in ((0, "vial A"), (ud.PITCH_Y, "vial B")):
        axs[2].annotate(lab, xy=(yv, 30), ha="center", fontsize=9, color="#333")
    handles = [Patch(fc=COL[k], ec="#222", label=l) for k, l in
               [("collar", "NEW: collar (cup, no floor; 4 half keys)"), ("frame", "NEW: frame (replaces the holder; 2 bosses)"),
                ("holder", "today's compact holder"), ("spacer", "Ben's 4.6 mm spacer"), ("base", "compact base (reused)"),
                ("fan", "fan (reused)"), ("carrier", "magnet carrier (reused)"), ("mag_n", "magnets"),
                ("deck", "deck, 9 mm"), ("vial", "20 mL vial"), ("bar", "15 x 6 mm stir bar"),
                ("screws", "screws"), ("inserts", "heat-set inserts")]]
    fig.legend(handles=handles, loc="lower center", ncol=7, fontsize=9, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.suptitle("Stir module with the fan under the deck, so the deck is the spacer, side by side: a mock-up (PR #348)", fontsize=13.5,
                 fontweight="bold", x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.07, 1, 0.97))
    out = ROOT / "img" / "under_deck_section.png"
    fig.savefig(out, dpi=120)
    print("wrote", out)


def views():
    import pyvista as pv
    from PIL import Image, ImageChops
    today, under = scenes()

    def pvm(m):
        return pv.wrap(m)

    W, H = 900, 820
    shots = []
    explode = {"collar": 34, "screws": 34, "vial": 52, "cap": 52, "bar": 52, "deck": 0, "frame": -18, "inserts": -18,
               "hall": -18, "carrier": -30, "mag_n": -30, "mag_s": -30, "fan": -42, "base": -56}
    four = block([(0, 0), (ud.PITCH_X, 0), (0, ud.PITCH_Y), (ud.PITCH_X, ud.PITCH_Y)], (60, 58, ud.PITCH_X / 2, ud.PITCH_Y / 2))
    c4 = (ud.PITCH_X / 2, ud.PITCH_Y / 2)
    for name, sc, cam, exp, deck_op, size, zoom in [
            ("Four side by side, 50 mm apart in X and 45 in Y", four,
             [(c4[0] - 230, c4[1] - 280, 210), (c4[0], c4[1], 14), (0, 0, 1)], False, 1.0, (1000, 900), 1.25),
            ("Under the deck (from below): frames and bases 1 mm apart", four,
             [(c4[0] - 190, c4[1] - 230, -170), (c4[0], c4[1], -16), (0, 0, 1)], False, 1.0, (1000, 900), 1.3),
            ("One module, exploded", under, [(-300, -350, 60), (0, 0, 8), (0, 0, 1)], True, 0.45, (760, 1150), 1.0)]:
        p = pv.Plotter(off_screen=True, window_size=size)
        p.set_background("white")
        for k, ms in sc.items():
            for m in ms:
                mm = pvm(m)
                if exp:
                    dz = explode.get(k, 0)
                    if k == "screws" and m.bounds[0][2] < -15:      # the fan screws go with the frame
                        dz = -18
                    mm = mm.translate((0, 0, dz), inplace=False)
                op = deck_op if k == "deck" else (0.28 if k == "vial" else 1.0)
                p.add_mesh(mm, color=COL[k], opacity=op, smooth_shading=False, specular=0.15, ambient=0.25, diffuse=0.75)
        p.camera_position = cam
        p.camera.zoom(zoom)
        p.enable_anti_aliasing("ssaa")
        f = TMP / f"v{len(shots)}.png"
        p.screenshot(str(f))
        p.close()
        shots.append((name, Image.open(f).convert("RGB")))
    from PIL import ImageDraw, ImageFont
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    crops = []
    for name, im in shots:
        box = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
        im = im.crop((max(box[0] - 20, 0), max(box[1] - 20, 0), min(box[2] + 20, im.width), min(box[3] + 20, im.height)))
        crops.append((name, im))
    h = max(im.height for _, im in crops) + 60
    sheet = Image.new("RGB", (sum(im.width for _, im in crops) + 40 * (len(crops) - 1), h), "white")
    x = 0
    d = ImageDraw.Draw(sheet)
    for name, im in crops:
        sheet.paste(im, (x, 60 + (h - 60 - im.height) // 2))
        d.text((x + 10, 15), name.split(":")[0], fill=(10, 10, 10), font=font)
        x += im.width + 40
    out = ROOT / "img" / "under_deck_views.png"
    sheet.save(out)
    print("wrote", out, sheet.size)


def plan():
    """A block of modules on the slot grid, from above, to scale: which half of each slot each one uses,
    and where the pipette hangs while the capper works a vial."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MPoly
    from shapely.geometry import LineString, Point, box as sbox
    from shapely.ops import unary_union

    INK, INK2, MUTED, SURF, DECK = "#0b0b0b", "#52514e", "#8a8984", "#fcfcfb", "#dcdad4"
    KEY, BOSS, FRAME, BAD, OK = "#eb6834", "#2a78d6", "#9a9890", "#c62828", "#2e7d32"

    def rr(cx, cy, w, d, r):
        return sbox(cx - w / 2 + r, cy - d / 2 + r, cx + w / 2 - r, cy + d / 2 - r).buffer(r, resolution=24)

    def slot(cx, cy):
        return LineString([(cx, cy - ud.SLOT_L / 2 + ud.SLOT_W / 2), (cx, cy + ud.SLOT_L / 2 - ud.SLOT_W / 2)]).buffer(ud.SLOT_W / 2, resolution=24)

    def half(cx, cy, s):
        r = ud.KEY_W / 2
        yc, ye = cy + s * ud.END_C, cy + s * ud.HALF_END
        return Point(cx, yc).buffer(r, resolution=24).union(sbox(cx - r, min(yc, ye), cx + r, max(yc, ye)))

    def poly(ax, g, **kw):
        for gg in getattr(g, "geoms", [g]):
            ax.add_patch(MPoly(list(gg.exterior.coords), closed=True, **kw))
            for ring in gg.interiors:
                ax.add_patch(MPoly(list(ring.coords), closed=True, fc=kw.get("_hole", SURF), ec=kw.get("ec", "none"),
                                   lw=kw.get("lw", 0.5), zorder=kw.get("zorder", 1)))

    fig = plt.figure(figsize=(12.6, 8.4), dpi=110)
    fig.patch.set_facecolor(SURF)
    ax = fig.add_axes((0.01, 0.07, 0.62, 0.80))
    ax.set_facecolor(SURF)
    px, py = ud.PITCH_X, ud.PITCH_Y
    win = (-40, 2 * px + 40, -35, 2 * py + 35)
    ax.add_patch(plt.Rectangle((win[0], win[2]), win[1] - win[0], win[3] - win[2], fc=DECK, ec="none", zorder=0))
    for i in range(-2, 6):
        for j in range(-1, 4):
            poly(ax, slot(ud.COL / 2 + i * ud.COL, ud.ROW / 2 + j * ud.ROW), fc="#f4f3ef", ec="#b9b6ae", lw=0.6, zorder=1)
    modules = [(i * px, j * py) for i in range(2) for j in range(3)]
    for cx, cy in modules:
        poly(ax, rr(cx, cy, ud.CELL_W, ud.CELL_D, 5.0), fc="none", ec=FRAME, lw=1.0, ls=(0, (4, 2)), zorder=2)
        bars = unary_union([rr(cx + sx * ud.COL / 2, cy, ud.BAR_W, ud.CELL_D, 3.0) for sx in (-1, 1)]
                           + [Point(cx, cy).buffer(C["CUP_OD"] / 2, resolution=64)])
        poly(ax, bars, fc="#fdebe2", ec=KEY, lw=1.2, zorder=3)
        for x, y in ud.SLOTS:
            poly(ax, half(cx + x, cy, 1 if y > 0 else -1), fc="none", ec=KEY, lw=1.0, ls=(0, (2, 1.4)), zorder=5)
        for x, y in ud.CLAMP:
            poly(ax, half(cx + x, cy, 1 if y > 0 else -1), fc="none", ec=BOSS, lw=0, hatch="////", zorder=4)
            ax.add_patch(plt.Circle((cx + x, cy + y), 2.75, fc=BOSS, ec=INK, lw=0.6, zorder=7))
        for x, y in ud.FAN_SCREWS:
            ax.add_patch(plt.Circle((cx + x, cy + y), 2.75, fc=SURF, ec=INK2, lw=1.0, ls=(0, (1.5, 1)), zorder=6))
        ax.add_patch(plt.Circle((cx, cy), C["VIAL_OD"] / 2, fc="#e8f2f8", ec=MUTED, lw=0.7, zorder=6))
        ax.add_patch(plt.Circle((cx, cy), 12.6, fc="#4a4a50", ec="none", alpha=0.35, zorder=6))
    # where the pipette hangs while the capper works the lower-left vial, and the capper while the pipette works it
    dx, dy = ud.PIPETTE_FROM_CAPPER
    ax.plot([0, dx], [0, dy], color=BAD, lw=1.2, zorder=8)
    ax.plot(dx, dy, marker="X", ms=12, color=BAD, mec=INK, zorder=9)
    ax.annotate("pipette tip, while the capper works vial A:\n12 mm from vial B's axis, inside its cup",
                (dx, dy), (dx + 8, -27), fontsize=9, color=BAD, ha="left", va="center", zorder=10,
                arrowprops=dict(arrowstyle="-", color=BAD, lw=0.8))
    ax.add_patch(plt.Circle((75, 0), C["CUP_OD"] / 2, fc="none", ec=OK, lw=1.2, ls=(0, (3, 2)), zorder=8))
    ax.annotate("B one column further (75 mm):\nthe tip is 23 mm from its axis,\n6 mm outside its cup", (75 + 12, 12), (96, 30), fontsize=9, color=OK,
                ha="left", va="center", zorder=10, arrowprops=dict(arrowstyle="-", color=OK, lw=0.8))
    ax.text(0, -C["VIAL_OD"] / 2 - 2.5, "A", ha="center", va="top", fontsize=11, fontweight="bold", color=INK, zorder=9)
    ax.text(px, -C["VIAL_OD"] / 2 - 2.5, "B", ha="center", va="top", fontsize=11, fontweight="bold", color=INK, zorder=9)
    ax.set_xlim(win[0], win[1])
    ax.set_ylim(win[2], win[3])
    ax.set_aspect("equal")
    ax.axis("off")
    fig.suptitle("Under-deck stirrers side by side: one per 50 \u00d7 45 mm of the deck", x=0.01, y=0.975, ha="left",
                 fontsize=13.5, fontweight="bold", color=INK)
    fig.text(0.01, 0.925, "Six modules on the CubXL's slot grid, from above, to scale (mm). Each module keeps to its own "
             "49 \u00d7 44 mm and to the half of each slot nearest its vial.", fontsize=10.2, color=INK2)
    notes = [("On the deck", True),
             ("Collar: cup with no floor, two 44 mm bars,\nfour half-length keys (orange, dashed)", False),
             ("Under the deck", True),
             ("Frame and today's compact base, 49 \u00d7 44 mm\n(grey, dashed): 1 mm between neighbours", False),
             ("Frame bosses, 5 mm up into two diagonal\nhalf-slots (blue hatch), with the clamp's\nheat-set inserts", False),
             ("Screws", True),
             ("\u25cf  2 \u00d7 M3 \u00d7 12 clamp, from the top", False),
             ("\u25cb  2 \u00d7 M3 \u00d7 16 fan screws, under the deck. They\n    sit under the other two half-slots, which\n"
              "    is why the clamp can't use those", False),
             ("The head", True),
             ("The pipette is 55 mm +X and 11 mm +Y of the\ncapper. At 50 mm in X it comes down inside\nthe next "
              "vial's cup (red). In Y, 45 mm\napart is clear by 48 mm. So: columns along Y,\nand a free slot "
              "column between them in X", False)]
    y = 0.86
    for text, head in notes:
        fig.text(0.645, y, text, fontsize=10.2 if head else 9.3, color=INK if head else INK2, va="top",
                 fontweight="bold" if head else "normal", linespacing=1.3)
        y -= 0.027 * (text.count("\n") + 1) + (0.008 if head else 0.022)
    fig.text(0.01, 0.025, "Deck: Cubware PandaDeck.step, slots 10 \u00d7 25 mm, 25 mm apart in X and 45 mm in Y. "
             "Vial (blue) and cap (grey) at each module's centre, between four slots.", fontsize=8.8, color=INK2)
    out = ROOT / "img" / "under_deck_side_by_side_plan.png"
    fig.savefig(out, facecolor=SURF)
    print("wrote", out)


if __name__ == "__main__":
    {"section": section, "views": views, "plan": plan}[sys.argv[1]]()
