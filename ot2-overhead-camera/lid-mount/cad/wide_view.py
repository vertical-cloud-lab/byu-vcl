#!/usr/bin/env python3
"""The 8 mm whole-deck view, with the mount over the middle of the deck: pixels per slot and per well.

Writes ../renders/wide_view_8mm.png and ../exports/wide_view_8mm.json.

Uses coverage.py's pinhole camera. The mount sits halfway between slots 5 and 8, the lens at its
8 mm end and the IMX477's long side along X. Pixels are for a full-resolution still (4056 x 3040,
what capture_still.py and rpicam-still take). For each slot it reports the steepest look into a
well of a 96-well plate there, how much of that well's floor the near wall hides, and how much of
the floor is left in view: the overlap of the well's top and bottom circles, offset by the shadow.

It also draws what PR #84's preview_server.py shows of the same view. Its 1536 x 864 stream makes
libcamera pick the IMX477's 16:9 mode, ScalerCrop (108, 440, 3840, 2160): 95 % of the sensor's width
and 71 % of its height (checked on the lid camera's Pi 5 on 2026-10-15). ../camera/preview_server.py
keeps the whole 4:3 field.

    python wide_view.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

from coverage import (INK, INK2, MUTED, POSITIONS, PX, SLOT_SIZE, SURFACE, WELL_D, WELL_DEPTH, WINDOW_TOP,
                      slot_rect, view, wells)
from lid_mount import EXPORTS, Params
from ot2_context import PLATE, PUPIL_IN_LENS, SENSOR, SLOTS

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "renders" / "wide_view_8mm.png"

FOCAL = 8.0
AXIS = POSITIONS["deck centre"][1]
CROP_16x9 = (108, 440, 3840, 2160)      # ScalerCrop of preview_server.py's 1536 x 864 stream (x, y, w, h)
FIELD_C, CROP_C = "#1c5cab", "#d4622a"


def floor_in_view(shadow: float) -> float:
    """Fraction of a well's floor in view: two circles of the well's diameter, offset by the shadow."""
    r = WELL_D / 2
    if shadow >= 2 * r:
        return 0.0
    lens = 2 * r * r * math.acos(shadow / (2 * r)) - shadow / 2 * math.sqrt(4 * r * r - shadow * shadow)
    return lens / (math.pi * r * r)


def main() -> None:
    p = Params()
    r = view(p, AXIS, FOCAL)
    x0, y0, x1, y1 = r["field (deck mm)"]
    w, h = r["field at the plate top (mm)"]
    pxmm = PX[0] / w
    dist = WINDOW_TOP + p.z_lens_front + PUPIL_IN_LENS - PLATE[2]

    slots = {}
    for n in range(1, 12):
        pts = wells(n)
        rad = np.hypot(pts[:, 0] - AXIS[0], pts[:, 1] - AXIS[1]).max()
        ang = math.degrees(math.atan(rad / dist))
        shadow = WELL_DEPTH * math.tan(math.radians(ang))
        slots[n] = {"steepest look into a well (deg)": round(ang, 1),
                    "near-wall shadow on that well's floor (mm)": round(shadow, 1),
                    "floor of that well in view": round(floor_in_view(shadow), 2)}

    # The wells of plates in every slot, and the slot outlines, against the field.
    allw = np.vstack([wells(n) for n in range(1, 12)])
    wx = (allw[:, 0].min() - WELL_D / 2, allw[:, 0].max() + WELL_D / 2)
    wy = (allw[:, 1].min() - WELL_D / 2, allw[:, 1].max() + WELL_D / 2)
    deck = (slot_rect(1)[0], slot_rect(1)[1], slot_rect(12)[2], slot_rect(12)[3])
    f_wells = SENSOR[1] * dist / (wy[1] - wy[0])
    f_slots = SENSOR[1] * dist / (deck[3] - deck[1])

    cx, cy, cw, ch = CROP_16x9
    crop = (x0 + cx / PX[0] * w, y1 - (cy + ch) / PX[1] * h, x0 + (cx + cw) / PX[0] * w, y1 - cy / PX[1] * h)
    crop_cut = {n: round(1 - max(0.0, min(crop[3], slot_rect(n)[3]) - max(crop[1], slot_rect(n)[1])) / SLOT_SIZE[1], 2)
                for n in range(1, 13)}

    report = {
        "mount": "lens axis halfway between slots 5 and 8: x 0, y -35.8 mm from the window's centre",
        "focal length (mm)": FOCAL,
        "field at the plate top (mm)": [w, h],
        "field (deck mm)": [x0, y0, x1, y1],
        "resolution, full-resolution still (px/mm)": round(pxmm, 2),
        "one slot, 128 x 86 mm (px)": [round(SLOT_SIZE[0] * pxmm), round(SLOT_SIZE[1] * pxmm)],
        "one 96-well plate, 127.76 x 85.48 mm (px)": [round(PLATE[0] * pxmm), round(PLATE[1] * pxmm)],
        "pixels across one well (6.86 mm)": round(WELL_D * pxmm, 1),
        "pixels inside one well's opening": round(math.pi / 4 * (WELL_D * pxmm) ** 2),
        "margin beyond the outermost wells, left/right and front/back (mm)":
            [round(min(wx[0] - x0, x1 - wx[1]), 1), round(min(wy[0] - y0, y1 - wy[1]), 1)],
        "margin beyond the slot outlines, left/right and front/back (mm)":
            [round(min(deck[0] - x0, x1 - deck[2]), 1), round(min(deck[1] - y0, y1 - deck[3]), 1)],
        "longest focal length that still fits every well front to back (mm)": round(f_wells, 2),
        "longest focal length that still fits every slot outline front to back (mm)": round(f_slots, 2),
        "per slot (plate of 96 wells in it)": slots,
        "preview_server.py as in PR #84 (16:9 crop)": {
            "ScalerCrop (x, y, w, h)": list(CROP_16x9),
            "field shown (deck mm)": [round(v, 1) for v in crop],
            "fraction of each slot's depth it hides": crop_cut,
        },
        "1352 x 1014 live view of camera/preview_server.py (px/mm)": round(pxmm * 1352 / PX[0], 2),
    }
    (EXPORTS / "wide_view_8mm.json").write_text(json.dumps(report, indent=2) + "\n")

    # --- figure ---
    fig, ax = plt.subplots(figsize=(11.5, 10.6), dpi=130)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for n in range(1, 13):
        sx0, sy0, sx1, sy1 = slot_rect(n)
        ax.add_patch(Rectangle((sx0, sy0), sx1 - sx0, sy1 - sy0, fc="none", ec=MUTED, lw=0.8, ls=(0, (4, 3))))
        ax.text(sx0 + 3, sy1 - 3, f"{n}" + (" (trash)" if n == 12 else ""), ha="left", va="top",
                fontsize=10, color=INK, fontweight="bold")
        if n == 12:
            continue
        scx, scy = SLOTS[n]
        ax.add_patch(FancyBboxPatch((scx - PLATE[0] / 2 + 3, scy - PLATE[1] / 2 + 3), PLATE[0] - 6, PLATE[1] - 6,
                                    boxstyle="round,pad=3", fc="#f1f1ee", ec=MUTED, lw=0.6))
        for x, y in wells(n):
            ax.add_patch(Circle((x, y), WELL_D / 2, fc="none", ec=MUTED, lw=0.35))
        s = slots[n]
        ax.text(scx, scy, f"{s['steepest look into a well (deg)']:.0f}°\n"
                f"{s['floor of that well in view'] * 100:.0f} % of floor",
                ha="center", va="center", fontsize=8.5, color=INK, linespacing=1.3,
                bbox=dict(fc=SURFACE, ec="none", pad=1.5, alpha=0.9))

    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="none", ec=FIELD_C, lw=2.6))
    ax.text(x0 + 2, y1 + 3, f"Full-resolution still at 8 mm: {w:.0f} × {h:.0f} mm, 4056 × 3040 px",
            ha="left", va="bottom", fontsize=9.5, color=INK, fontweight="bold")
    ax.add_patch(Rectangle((crop[0], crop[1]), crop[2] - crop[0], crop[3] - crop[1], fc="none", ec=CROP_C,
                           lw=1.8, ls=(0, (6, 3))))
    ax.text(crop[2] - 3, crop[3] + 3, "What PR #84's preview_server.py\nshows: a 16:9 crop",
            ha="right", va="bottom", fontsize=9, color=INK, linespacing=1.3,
            bbox=dict(fc=SURFACE, ec="none", pad=1.0))
    ax.plot([AXIS[0] - 8, AXIS[0] + 8], [AXIS[1], AXIS[1]], color=INK, lw=1.2)
    ax.plot([AXIS[0], AXIS[0]], [AXIS[1] - 8, AXIS[1] + 8], color=INK, lw=1.2)

    ax.text(196.5, -26, "FRONT (door)", ha="center", va="top", fontsize=10, color=INK, fontweight="bold")
    ax.text(196.5, 384, "BACK", ha="center", va="bottom", fontsize=10, color=INK, fontweight="bold")
    ax.set_xlim(-50, 445)
    ax.set_ylim(-40, 400)
    ax.set_aspect("equal")
    ax.axis("off")

    sl = report["one slot, 128 x 86 mm (px)"]
    mw, mh = report["margin beyond the outermost wells, left/right and front/back (mm)"]
    fig.suptitle("The 8 mm view with the mount over the middle of the deck (seen from above)",
                 x=0.03, y=0.975, ha="left", fontsize=13, color=INK)
    fig.text(0.03, 0.935,
             f"Every slot: {sl[0]:,} × {sl[1]:,} px ({pxmm:.1f} px/mm).  Every well: "
             f"{report['pixels across one well (6.86 mm)']:.0f} px across, about "
             f"{report['pixels inside one well\'s opening']:,} px inside its opening.",
             ha="left", va="top", fontsize=10.5, color=INK)
    fig.text(0.03, 0.012,
             "+ is the lens axis: halfway between slots 5 and 8, x 0, y −35.8 mm from the window's centre. "
             "In each slot: the steepest look into a well of a 96-well plate there,\nand how much of that "
             f"well's floor the near wall leaves in view. Margins beyond the outermost wells: {mw:.0f} mm "
             f"left and right, {mh:.0f} mm front and back; every well fits up to f = {f_wells:.2f} mm.\n"
             "Pinhole model at the top of the plate (about ±3 % on the field); lens distortion is not "
             "modelled. Numbers in exports/wide_view_8mm.json, from cad/wide_view.py.",
             fontsize=8.5, color=INK2, ha="left", va="bottom", linespacing=1.5)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.91, bottom=0.08)
    fig.savefig(OUT, facecolor=SURFACE)
    print(f"wrote {OUT}")
    print(json.dumps({k: v for k, v in report.items() if k != "per slot (plate of 96 wells in it)"}, indent=1))
    print(json.dumps(slots, indent=1))


if __name__ == "__main__":
    main()
