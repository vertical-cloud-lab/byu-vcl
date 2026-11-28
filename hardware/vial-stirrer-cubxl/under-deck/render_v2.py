#!/usr/bin/env python3
"""The under-deck frame, v1 (printed 2026-11-20) against v2 (2026-11-24), and where the cable leaves a column of modules.

    python under-deck/render_v2.py      # img/under_deck_v2.png

Run from hardware/vial-stirrer-cubxl. The frames, the Hall sensor, the fan and the magnets come from build_under_deck.py;
the base and the carrier are the committed STLs (stl/compact/base_compact.stl, stl/magnet_carrier.stl).
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import trimesh

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import build_under_deck as ud  # noqa: E402
from render_under_deck import COL, draw_geom, section_polys, stl, tm  # noqa: E402


def plan_polys(mesh, z):
    """Horizontal section of a closed mesh at height z, as shapely geometry in (x, y)."""
    from functools import reduce
    from shapely.geometry import Polygon
    sec = mesh.section(plane_origin=(0, 0, z), plane_normal=(0, 0, 1))
    if sec is None:
        return None
    polys = [Polygon(d[:, :2]).buffer(0) for d in sec.discrete if len(d) > 3]
    polys = [p for p in polys if p.area > 1e-4]
    return reduce(lambda a, b: a.symmetric_difference(b), polys) if polys else None


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Patch, Rectangle

    b = ud.bought()
    frames = {1: tm(ud.frame(1), "frame_v1"), 2: tm(ud.frame(2), "frame_v2")}
    halls = {v: tm(ud.hall_body(v), f"hall_v{v}") for v in (1, 2)}
    common = {"deck": tm(ud.deck(40, 30), "deck"), "base": stl("stl/compact/base_compact.stl", ud.DZ),
              "carrier": stl("stl/magnet_carrier.stl", ud.DZ), "fan": tm(b["fan"], "fan"),
              "mag_n": tm(b["magnets"][0], "mn"), "mag_s": tm(b["magnets"][1], "ms")}
    z1 = ud.Z_PLATE1

    fig = plt.figure(figsize=(20, 12.6), facecolor="white")
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 0.78], height_ratios=[1, 0.86])
    titles = {1: "v1, printed 2026-11-20", 2: "v2, 2026-11-24"}
    v2 = ud.V2
    for col, v in enumerate((1, 2)):
        # --- top view of the frame -------------------------------------------------------------------------------
        ax = fig.add_subplot(gs[0, col])
        top = plan_polys(frames[v], z1 - 0.05)
        through = plan_polys(frames[v], ud.Z_PLATE0 + 0.2)
        draw_geom(ax, top, (1.0, 0.86, 0.62), z=1)            # the top face, with the pocket, groove and hole
        draw_geom(ax, through, COL["frame"], z=2, alpha=0.9)  # what is left right through the plate
        hb = halls[v].bounds
        ax.add_patch(Rectangle((hb[0][0], hb[0][1]), hb[1][0] - hb[0][0], hb[1][1] - hb[0][1], fc="#111", ec="#111", zorder=5))
        ax.add_patch(Circle((0, 0), ud.C["CAR_D"] / 2, fc="none", ec="#c00", lw=1.6, ls="--", zorder=6))
        for s in (1, -1):
            ax.add_patch(Circle((s * ud.C["MAG_CC"] / 2, 0), ud.C["MAG_D"] / 2, fc=COL["mag_n" if s > 0 else "mag_s"],
                                ec="none", alpha=0.35, zorder=4))
        bore = ud.C["CAR_D"] + 1.6 if v == 1 else v2["BORE_D"]
        gap = (bore - ud.C["CAR_D"]) / 2
        ax.annotate(f"bore Ø{bore:g}: {gap:.1f} mm round\nthe Ø{ud.C['CAR_D']:g} carrier (red)", xy=(bore / 2 * 0.707, -bore / 2 * 0.707),
                    xytext=(8, -19.5), fontsize=10.5, arrowprops=dict(arrowstyle="->", lw=1.0),
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#bbb"), zorder=9)
        if v == 1:
            ax.annotate("lead slot 2.0 x 2.6 mm:\nthe sensor (4.06 x 1.52) can't pass,\nso it is threaded and soldered\nwith the frame in the way",
                        xy=(-21.6, 0), xytext=(-24, 13.5), fontsize=10.5, arrowprops=dict(arrowstyle="->", lw=1.0),
                        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#bbb"), zorder=9)
        else:
            hx0, hx1 = v2["HOLE_X"]
            ax.annotate(f"hole {hx1 - hx0:.1f} x {v2['HOLE_W']:.1f} mm, through:\nthe whole sensor passes, so it is\nsoldered first and pushed up\nthrough the frame afterwards",
                        xy=((hx0 + hx1) / 2, 1.0), xytext=(-24, 13.5), fontsize=10.5, arrowprops=dict(arrowstyle="->", lw=1.0),
                        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#bbb"), zorder=9)
            ax.annotate(f"groove {v2['GROOVE_W']:g} wide, its floor {v2['GROOVE_STEP']:g} mm above\nthe pocket's: the body can't slide out",
                        xy=(-17.0, -1.2), xytext=(-24, -15.5), fontsize=9.5, arrowprops=dict(arrowstyle="->", lw=0.8),
                        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#bbb"), zorder=9)
        ax.set_xlim(-26, 26)
        ax.set_ylim(-23.5, 23.5)
        ax.set_aspect("equal")
        ax.grid(color="#eee", lw=0.5, zorder=-1)
        ax.set_title(f"Frame {titles[v]}: from above", fontsize=12, fontweight="bold", loc="left")
        ax.set_xlabel("x, mm (cable notch and Hall leads at -X)")
        if col == 0:
            ax.set_ylabel("y, mm")

        # --- section through the sensor, y = 0 ---------------------------------------------------------------------
        ax = fig.add_subplot(gs[1, col])
        plane = dict(normal=(0, 1, 0), origin=(0, 0, 0), u=(1, 0, 0))
        parts = [("deck", common["deck"]), ("base", common["base"]), ("fan", common["fan"]), ("frame", frames[v]),
                 ("carrier", common["carrier"]), ("mag_n", common["mag_n"]), ("mag_s", common["mag_s"]), ("hall", halls[v])]
        for k, m in parts:
            g = section_polys(m, **plane)
            if g is not None:
                draw_geom(ax, g, COL[k], alpha=0.55 if k == "deck" else 1.0, z=0 if k == "deck" else 2,
                          hatch="///" if k == "deck" else None)
        ax.axhline(-ud.DECK_T, color="#999", lw=0.5, ls=":")
        hb = halls[v].bounds
        if v == 1:
            txt = "sensor's top edge at r 10.30, 0.8 mm\nfrom the carrier; Hall signal 15.7 mT\n(worst case, bar following)"
        else:
            txt = ("sensor's top edge at r 11.05, 1.55 mm from\nthe carrier, and 0.83 mm lower: its element\n"
                   "is at the magnets' mid-height. Hall signal\n11.9 mT worst case (trips by 9.5)")
        ax.annotate(txt, xy=(hb[0][0] + 1.5, hb[1][2] - 0.3), xytext=(-43.5, -0.8), fontsize=9.5, va="top",
                    arrowprops=dict(arrowstyle="->", lw=0.9), bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#bbb"), zorder=9)
        ax.text(4.0, -2.5, "deck, 9 mm", fontsize=9, color="#345", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"))
        ax.annotate("base's -X wall: open\nhere (the cable notch)", xy=(-23.7, -29.6), xytext=(-43.5, -25.5), fontsize=9,
                    arrowprops=dict(arrowstyle="->", lw=0.8), bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#ddd"), zorder=9)
        hole_txt = "lead slot 2.0 mm" if v == 1 else "hole 3.3 mm: the sensor\ncomes up through it"
        ax.annotate(hole_txt, xy=(-21.6 if v == 1 else -21.25, -12.2), xytext=(-43.5, -16.5), fontsize=9,
                    arrowprops=dict(arrowstyle="->", lw=0.8), bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#ddd"), zorder=9)
        ax.set_xlim(-44, 14)
        ax.set_ylim(-34, 1)
        ax.set_aspect("equal")
        ax.grid(color="#eee", lw=0.5, zorder=-1)
        ax.set_title(f"{titles[v]}: section at y = 0", fontsize=12, fontweight="bold", loc="left")
        ax.set_xlabel("x, mm")
        if col == 0:
            ax.set_ylabel("z, mm (0 = the deck's top face)")

    # --- the cable: a column along Y ------------------------------------------------------------------------------
    ax = fig.add_subplot(gs[:, 2])
    w, d = ud.CELL_W, ud.CELL_D
    for k in range(3):
        for xc, bad in ((0.0, True), (82.0, False)):
            y = k * ud.PITCH_Y
            ax.add_patch(Rectangle((xc - w / 2, y - d / 2), w, d, fc=COL["base"], ec="#111", alpha=0.85, zorder=2))
            ax.add_patch(Circle((xc, y), 13.75, fc=COL["vial"], ec="#557", zorder=3, alpha=0.9))
            if bad:   # 10-28 / 10-30 base: notch in the -Y wall, x -11 to -3
                ax.add_patch(Rectangle((xc - 11, y - d / 2 - 0.3), 8, 1.9, fc="white", ec="none", zorder=4))
                ax.plot([xc - 7, xc - 7], [y - d / 2, y - d / 2 - 9], color="#d22", lw=3.2, zorder=5, solid_capstyle="round")
            else:     # 11-04 base: notch in the -X wall, y -6.5 to 6.5
                ax.add_patch(Rectangle((xc - w / 2 - 0.3, y - 6.5), 1.9, 13, fc="white", ec="none", zorder=4))
                ax.plot([xc - w / 2, xc - w / 2 - 14], [y, y], color="#1a7f37", lw=3.2, zorder=5, solid_capstyle="round")
    ax.text(0, 2 * ud.PITCH_Y + 29, "printed so far\n(10-28, 10-30):\nnotch in -Y", ha="center",
            fontsize=10.5, color="#a00", fontweight="bold")
    ax.text(82, 2 * ud.PITCH_Y + 29, "CAD since 11-04\n(not printed yet):\nnotch in -X", ha="center",
            fontsize=10.5, color="#1a7f37", fontweight="bold")
    ax.text(0, -36, "the cable runs into\nthe next module,\n1 mm away", ha="center", va="top", fontsize=10, color="#a00")
    ax.text(82, -36, "every cable leaves\nsideways, clear of\nits neighbours", ha="center", va="top", fontsize=10, color="#1a7f37")
    ax.set_xlim(-42, 118)
    ax.set_ylim(-55, 2 * ud.PITCH_Y + 50)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("The cable, modules in a column along Y,\n45 mm apart (from above, bases only)", fontsize=12, fontweight="bold", loc="left")

    handles = [Patch(fc=(1.0, 0.86, 0.62), ec="#222", label="frame: recessed from the top face (pocket, groove)"),
               Patch(fc=COL["frame"], ec="#222", label="frame: full thickness"), Patch(fc="#111", label="US1881 Hall sensor"),
               Patch(fc=COL["carrier"], ec="#222", label="magnet carrier"), Patch(fc=COL["mag_n"], label="magnets"),
               Patch(fc=COL["fan"], label="fan"), Patch(fc=COL["base"], label="compact base"),
               Patch(fc=COL["deck"], ec="#222", hatch="///", label="deck")]
    fig.legend(handles=handles, loc="lower center", ncol=8, fontsize=9.5, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.suptitle("Under-deck stir module, v2 (PR #348, 2026-11-24): a hole the Hall sensor passes through, a wider bore, "
                 "and the base with its cable notch on -X", fontsize=13.5, fontweight="bold", x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.035, 1, 0.965))
    out = ROOT / "img" / "under_deck_v2.png"
    fig.savefig(out, dpi=110)
    print("wrote", out)


if __name__ == "__main__":
    main()
