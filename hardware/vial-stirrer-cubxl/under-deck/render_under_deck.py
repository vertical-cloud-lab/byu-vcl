#!/usr/bin/env python3
"""Pictures of the under-deck mock-up (build_under_deck.py), next to today's stack on the 4.6 mm spacer.

    python under-deck/render_under_deck.py section     # img/under_deck_section.png (matplotlib)
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

    fig, axs = plt.subplots(1, 3, figsize=(19, 8.6), gridspec_kw=dict(width_ratios=[1, 1, 1.05]), facecolor="white")
    panels = [(axs[0], turned(today), diag, "along the diagonal",
               "TODAY: compact stirrer on the deck,\nvial on Ben's 4.6 mm spacer"),
              (axs[1], turned(under), diag, "along the diagonal",
               "MOCK-UP: fan under the deck,\nvial standing on the deck"),
              (axs[2], under, dict(normal=(1, 0, 0), origin=(ud.COL / 2, 0, 0), u=(0, 1, 0)), "y",
               f"MOCK-UP, through the slot column at x = {ud.COL / 2:g}:\nkeys, bosses and the clamp screws")]
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
    axs[2].set_xlim(-40, 56)
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
    axs[2].text(30, 30, "M3 x 12 from the top into heat-set\ninserts. The collar's keys (3 mm into\nthe slot) and the frame's bosses\n(5 mm in) share each slot, 1 mm\napart, so the screws clamp the deck\nand line the magnets up with the vial.",
                fontsize=8.6, va="center", ha="left", bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#bbb"))
    handles = [Patch(fc=COL[k], ec="#222", label=l) for k, l in
               [("collar", "NEW: collar (cup, no floor; 4 keys)"), ("frame", "NEW: frame (replaces the holder)"),
                ("holder", "today's compact holder"), ("spacer", "Ben's 4.6 mm spacer"), ("base", "compact base (reused)"),
                ("fan", "fan (reused)"), ("carrier", "magnet carrier (reused)"), ("mag_n", "magnets"),
                ("deck", "deck, 9 mm"), ("vial", "20 mL vial"), ("bar", "15 x 6 mm stir bar"),
                ("screws", "screws"), ("inserts", "heat-set inserts")]]
    fig.legend(handles=handles, loc="lower center", ncol=7, fontsize=9, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.suptitle("Stir module with the fan under the deck, so the deck is the spacer: a mock-up (PR #348)", fontsize=13.5,
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
    for name, cam, exp, deck_op, size, zoom in [
            ("On the deck: the collar holds the vial from the side only", [(-190, -230, 170), (0, 0, 18), (0, 0, 1)], False, 1.0, (900, 900), 1.15),
            ("Under the deck (seen from below): the frame and today's compact base", [(-150, -185, -130), (0, 0, -14), (0, 0, 1)], False, 1.0, (900, 900), 1.2),
            ("Exploded: what goes above and below the deck", [(-300, -350, 60), (0, 0, 8), (0, 0, 1)], True, 0.45, (760, 1150), 1.0)]:
        p = pv.Plotter(off_screen=True, window_size=size)
        p.set_background("white")
        for k, ms in under.items():
            for m in ms:
                mm = pvm(m)
                if exp:
                    dz = explode.get(k, 0)
                    if k == "screws" and m.bounds[0][2] < -20:      # the fan screws go with the frame
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


if __name__ == "__main__":
    {"section": section, "views": views}[sys.argv[1]]()
