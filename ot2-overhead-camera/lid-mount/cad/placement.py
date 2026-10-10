#!/usr/bin/env python3
"""Top view of the OT-2's top window, dimensioned for setting the mount over slot 5.

Writes ../renders/lid_placement.png. Everything is measured on the window, from its
centre: +x to the right and +y toward the back, looking down with the door at the bottom.
The numbers come from Opentrons' 2018 CAD (github.com/Opentrons/ot2), measured on 2026-10-02:

  * window outline, 564.9 x 455.1 mm, centred at deck (196.5, 214.525): the reference
    STEP, the same model ot2_context.py checks against;
  * the four corner screw slots, centred at (+-255.7, +-221.9): TOP_WINDOW_RevA2.DXF;
  * slot rectangles, 128 x 86 mm on a 132.5 x 90.5 mm pitch: Opentrons' OT-2 deck
    definition (shared-data/deck/definitions/5/ot2_standard.json).

The outline is drawn as a plain rectangle; the real one has shallow steps in its side
edges, which sit under the frame's lips anyway.

    python placement.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

from lid_mount import Params
from ot2_context import SLOTS

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "renders" / "lid_placement.png"

WINDOW = (564.9, 455.1)
WINDOW_CENTRE_DECK = (196.5, 214.525)
SCREWS = [(sx * 255.7, sy * 221.9) for sx in (-1, 1) for sy in (-1, 1)]
SLOT_SIZE = (128.0, 86.0)
FOV_25 = (152.7, 114.5)          # at the plate top, f = 25 mm (exports/ot2_fit.json)
PLATE = (127.76, 85.48)

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#a3a29c"
MOUNT = "#2a78d6"


def on_window(slot: int) -> tuple[float, float]:
    x, y = SLOTS[slot] if slot in SLOTS else (265.0 + 64.0, 271.5 + 43.0)
    return x - WINDOW_CENTRE_DECK[0], y - WINDOW_CENTRE_DECK[1]


def vdim(ax, x, y0, y1, text, side=1):
    """A vertical dimension at x from y0 to y1, labelled beside its middle."""
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<|-|>", color=INK2, lw=1.0,
                                                       shrinkA=0, shrinkB=0, mutation_scale=9))
    ax.text(x + side * 6, (y0 + y1) / 2, text, ha="left" if side > 0 else "right", va="center",
            fontsize=10, color=INK, bbox=dict(fc="#f1f1ee", ec="none", pad=1.5))


def mount_outline(ax, cx, cy, p: Params) -> None:
    half, tip = p.base_size / 2, p.base_size / 2 + p.tab_len
    ax.add_patch(FancyBboxPatch((cx - half + p.corner_r, cy - half + p.corner_r),
                                p.base_size - 2 * p.corner_r, p.base_size - 2 * p.corner_r,
                                boxstyle=f"round,pad={p.corner_r}", fc=MOUNT, alpha=0.16, ec="none"))
    ax.add_patch(FancyBboxPatch((cx - half + p.corner_r, cy - half + p.corner_r),
                                p.base_size - 2 * p.corner_r, p.base_size - 2 * p.corner_r,
                                boxstyle=f"round,pad={p.corner_r}", fc="none", ec=MOUNT, lw=1.6))
    w = p.tab_w / 2
    for ux, uy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        # Tab with its V-notch on the optical-axis line, in the tab's own frame (u along the axis line).
        local = [(-w, half), (-w, tip), (-3, tip), (0, tip - 4), (3, tip), (w, tip), (w, half)]
        pts = [(cx + a * uy + b * ux, cy + b * uy - a * ux) for a, b in local]
        ax.add_patch(Polygon(pts, closed=False, fc=MOUNT, alpha=0.16, ec="none"))
        ax.add_patch(Polygon(pts, closed=False, fc="none", ec=MOUNT, lw=1.6))
    ax.add_patch(Circle((cx, cy), p.aperture_d / 2 + p.collar_wall, fc="white", ec=MOUNT, lw=1.6))
    ax.add_patch(Circle((cx, cy), p.aperture_d / 2, fc="none", ec=MOUNT, lw=1.0))
    for x, y in [(cx + sx * p.post_c, cy + sy * p.post_c) for sx in (-1, 1) for sy in (-1, 1)]:
        ax.add_patch(Rectangle((x - p.post_w / 2, y - p.post_w / 2), p.post_w, p.post_w, fc=MOUNT, ec="none"))
    # The engraved arrow points -Y, at the door.
    ax.add_patch(Polygon([(cx - 5, cy - 34), (cx + 5, cy - 34), (cx, cy - 44)], fc=MOUNT, ec="none"))
    # Optical-axis lines through the tab notches.
    for (x0, y0), (x1, y1) in (((cx - tip - 8, cy), (cx + tip + 8, cy)), ((cx, cy - tip - 8), (cx, cy + tip + 8))):
        ax.plot([x0, x1], [y0, y1], color=MOUNT, lw=0.9, ls=(0, (6, 3)))


def main() -> None:
    p = Params()
    W, D = WINDOW
    ax_c = on_window(5)
    fig, ax = plt.subplots(figsize=(11.5, 10.2), dpi=140)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    ax.add_patch(FancyBboxPatch((-W / 2 + 3, -D / 2 + 3), W - 6, D - 6, boxstyle="round,pad=3",
                                fc="#f1f1ee", ec=INK2, lw=1.4))
    for n in range(1, 13):
        x, y = on_window(n)
        sw, sd = SLOT_SIZE
        ax.add_patch(Rectangle((x - sw / 2, y - sd / 2), sw, sd, fc="none", ec=MUTED, lw=0.8, ls=(0, (4, 3))))
        label = f"slot {n}" + (" (trash)" if n == 12 else "")
        ax.text(x - sw / 2 + 3, y + sd / 2 - 3, label, ha="left", va="top", fontsize=9,
                color=INK if n == 5 else INK2, fontweight="bold" if n == 5 else "normal")
    for x, y in SCREWS:
        ax.add_patch(Circle((x, y), 4.0, fc=INK2, ec="none"))
    ax.plot([SCREWS[0][0], SCREWS[2][0]], [SCREWS[0][1], SCREWS[2][1]], color=INK2, lw=0.6, ls=(0, (2, 2)))
    ax.text(SCREWS[2][0] - 7, SCREWS[2][1] + 3, "corner screw", ha="right", va="bottom", fontsize=9, color=INK2)
    ax.plot([0, 0], [-D / 2, D / 2], color=INK2, lw=0.6, ls=(0, (8, 3, 2, 3)))
    ax.text(3, D / 2 - 6, "window centreline:\nhalfway between the left\nand right screws", ha="left", va="top",
            fontsize=9, color=INK2)
    ax.plot([-6, 6], [0, 0], color=INK, lw=1.0)
    ax.plot([0, 0], [-6, 6], color=INK, lw=1.0)
    ax.text(-8, 4, "window centre", ha="right", va="bottom", fontsize=9, color=INK2)

    mount_outline(ax, *ax_c, p)

    vdim(ax, -100, -D / 2, ax_c[1], "146.5 mm from the\nwindow's front edge", side=-1)
    vdim(ax, 100, SCREWS[0][1], ax_c[1], "140.9 mm from the line\nthrough the front screws", side=1)
    vdim(ax, 100, ax_c[1], 0, "81.0 mm to the\nwindow centre", side=1)
    ax.plot([-100 - 4, ax_c[0] - 72], [ax_c[1], ax_c[1]], color=INK2, lw=0.6)
    ax.plot([100 + 4, ax_c[0] + 72], [ax_c[1], ax_c[1]], color=INK2, lw=0.6)
    ax.plot([8, 100 + 4], [0, 0], color=INK2, lw=0.6)
    ax.annotate("lens axis\n(centre of the aperture)", (ax_c[0] - 1, ax_c[1] + 1), (-165, 15),
                fontsize=10, color=INK, ha="center", va="center", bbox=dict(fc=SURFACE, ec="none", pad=1.5),
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8, connectionstyle="arc3,rad=0.15"))
    ax.annotate("arrow on the base\npoints at the door", (ax_c[0] + 1, ax_c[1] - 41), (-200, -205),
                fontsize=9, color=INK2, ha="center", va="center", bbox=dict(fc=SURFACE, ec="none", pad=1.5),
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    ax.text(W / 2 - 8, D / 2 - 108, "gantry parks at\nthe back right\nwhen homed", ha="right", va="top",
            fontsize=9, color=INK2, style="italic", bbox=dict(fc="#f1f1ee", ec="none", pad=1.5))

    ax.text(0, -D / 2 - 14, "FRONT (door)", ha="center", va="top", fontsize=11, color=INK, fontweight="bold")
    ax.text(0, D / 2 + 10, "BACK", ha="center", va="bottom", fontsize=11, color=INK, fontweight="bold")
    ax.set_title("OT-2 top window from above: where the mount goes (default: over slot 5)",
                 fontsize=13, color=INK, loc="left", pad=26)
    fx, fy = FOV_25
    fig.text(0.035, 0.014,
             "Mount in blue: the 112 mm base, with the V-notches in its four tabs on the lens-axis lines. "
             "Dashed outlines: the deck slots under the window.\n"
             f"At 25 mm zoom the camera sees {fx:.0f} x {fy:.0f} mm at the plate, so the whole plate stays in the "
             f"image if the axis is within ~{(fx - PLATE[0]) / 2:.0f} mm (left-right) and "
             f"~{(fy - PLATE[1]) / 2:.0f} mm (front-back) of this mark.\n"
             "Source: Opentrons' 2018 CAD (reference STEP, TOP_WINDOW_RevA2.DXF, OT-2 deck definition).\n"
             "Confirm with the live preview (README section 4). Other slots are in README section 3.",
             fontsize=8.5, color=INK2, ha="left", va="bottom", linespacing=1.5)

    ax.set_xlim(-W / 2 - 40, W / 2 + 40)
    ax.set_ylim(-D / 2 - 40, D / 2 + 30)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.105)
    fig.savefig(OUT, facecolor=SURFACE)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
