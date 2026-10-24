#!/usr/bin/env python3
"""Why the lid camera can't reach focus with its focus thumbscrew at NEAR, and the fix.

    python back_focus_fix.py

Writes frames/2026-10-23/back_focus_fix.png. Left: Tim's photo of the lens stack (2026-10-09),
labelled with what to turn. Middle and right: a section through the camera and the top of the
lens, now and fixed. Heights come from Raspberry Pi's HQ Camera drawing (ring face 14.43 mm in
front of the camera board, the 12.5 mm CS flange distance) and the 3.3 mm camera bosses as
printed; widths are only roughly to scale. The camera looks down, so "behind the sensor" is up.

Focusing nearer moves the picture further back behind the lens. With the knurled back-focus ring
screwed fully in and no C-CS adapter, the lens sits 5 mm closer to the sensor than a C-mount lens
is built for, and at NEAR the focus mechanism can't make that up: the picture still forms a few
millimetres behind the sensor. The 3 mm drawn is the middle of the 1-4 mm estimated from the
2026-10-22 21:47 UTC still (frames/2026-10-22/focus_end_2147Z.json).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / "frames/2026-10-23"
PHOTO = OUT / "lens_stack_2026-10-09_crop.jpg"

ORANGE, AMBER = "#ff7800", "#f0aa14"
INK, GREY, RED = "#1e1e20", "#6b6b70", "#d62728"
DARK, BODY, LENS, PCB = "#2b2b2b", "#45454a", "#161616", "#1f7a3a"

# Heights in mm below the deck plate's underside (y = 0, up is positive).
BOSS = 3.3              # camera bosses as sliced on the H2D deck
BOARD = 2.0             # camera PCB, measured 2026-10-08
RING_FACE = 14.43       # PCB front to the knurled ring's face, screwed fully in (drawing: 18.58 - 2.75 - 1.4)
RING_H = 5.8
CS_FFD, C_FFD = 12.5, 17.526
ADAPTER = 5.03

Y_PCB_FRONT = -(BOSS + BOARD)
Y_SEAT = Y_PCB_FRONT - RING_FACE                  # face of the knurled ring = CS seat
Y_SENSOR = Y_SEAT + CS_FFD                        # image plane of a CS lens
BEHIND_NOW = 3.0                                  # where the picture forms now, behind the sensor


def wall(ax, x0, x1, y0, y1, colour, **kw):
    """One wall of a part, drawn on both sides of the axis."""
    for s in (1, -1):
        ax.add_patch(Rectangle((s * x0 if s > 0 else -x1, y0), x1 - x0, y1 - y0, color=colour, **kw))


def stack(ax, fixed: bool) -> None:
    flange = Y_SEAT - (ADAPTER if fixed else 0.0)
    ax.add_patch(Rectangle((-24, 0), 48, 5, color=DARK))                        # deck
    for x in (-17, 13):
        ax.add_patch(Rectangle((x, -BOSS), 4, BOSS, color=DARK))                # bosses
    ax.add_patch(Rectangle((-19, Y_PCB_FRONT), 38, BOARD, color=PCB))           # camera board
    ax.add_patch(Rectangle((-5, Y_SENSOR), 10, Y_PCB_FRONT - Y_SENSOR, color="#20304f"))
    ax.plot([-5, 5], [Y_SENSOR, Y_SENSOR], color="#8fb3ff", lw=2.5)             # sensor surface
    wall(ax, 11.2, 15.4, Y_SEAT + RING_H, Y_PCB_FRONT, BODY)                    # mount body
    wall(ax, 12.7, 18.0, Y_SEAT, Y_SEAT + RING_H, ORANGE)                       # knurled ring
    for y in [Y_SEAT + 0.6 + i * 0.9 for i in range(6)]:                       # its knurls
        for s in (1, -1):
            ax.plot([s * 18.0, s * 18.6], [y, y], color=ORANGE, lw=1.2)
    ax.add_patch(Rectangle((-21.5, Y_SEAT + RING_H - 0.2), 3.5, 4.2, color=BODY))   # lock-screw clamp
    ax.add_patch(Rectangle((-23.0, Y_SEAT + RING_H + 1.0), 1.6, 1.8, color="#b9b9bd"))
    if fixed:
        wall(ax, 12.7, 15.6, flange, Y_SEAT, AMBER)                             # C-CS adapter
    wall(ax, 10.6, 12.7, flange, flange + 4.5, LENS)                            # lens thread
    wall(ax, 10.6, 19.0, -44, flange, LENS)                                     # lens barrel
    for s in (1, -1):
        ax.plot([s * 12.7, s * 19.0], [flange, flange], color="#d9d9dc", lw=3)  # silver rim
    ax.text(15, flange - 12, "FAR–NEAR", color="white", ha="center", fontsize=8, rotation=90)

    # Light from the plate, leaving the lens's rear glass and converging on its picture.
    y_img = Y_SENSOR + (0.0 if fixed else BEHIND_NOW)
    y_glass = flange - 2.0
    ax.add_patch(Polygon([(-8.5, y_glass), (8.5, y_glass), (0, y_img)], closed=True,
                         color="#ffe066", alpha=0.55, lw=0, zorder=3))
    if not fixed:
        half = 8.5 * BEHIND_NOW / (y_img - y_glass)
        ax.plot([-half, half], [Y_SENSOR - 0.05, Y_SENSOR - 0.05], color=RED, lw=5, zorder=5)
        ax.plot(0, y_img, "o", color=RED, ms=5, zorder=6)
        ax.annotate("the picture forms here,\nabout 3 mm behind the sensor", (0, y_img),
                    (27, 10.5), color=RED, fontsize=10, ha="left", va="center",
                    arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
        ax.annotate("so the sensor sees a blur", (half, Y_SENSOR), (27, 3.5), color=RED,
                    fontsize=10, ha="left", va="center",
                    arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
        ax.annotate("knurled ring\nscrewed fully in,\nno adapter", (18.6, Y_SEAT + 3), (27, -16),
                    color=ORANGE, fontsize=10, ha="left", va="center", fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.2))
        ax.annotate("focus thumbscrew\nalready at NEAR", (19.0, Y_SEAT - 8), (27, -31),
                    color=INK, fontsize=10, ha="left", va="center",
                    arrowprops=dict(arrowstyle="->", color=INK, lw=1.0))
    else:
        ax.plot(0, y_img, "o", color="#2ca02c", ms=6, zorder=6)
        ax.annotate("the picture forms on\nthe sensor: sharp", (0, y_img), (27, 10.5),
                    color="#2ca02c", fontsize=10, ha="left", va="center", fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=1.2))
        ax.annotate("5 mm C–CS adapter\n(or the knurled ring\nturned 5 mm down)",
                    (15.6, Y_SEAT - ADAPTER / 2), (27, -17), color="#b07800", fontsize=10,
                    ha="left", va="center", fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color="#b07800", lw=1.2))
        ax.plot([-21, 21], [Y_SEAT, Y_SEAT], ls=":", color=GREY, lw=1)
        ax.add_patch(FancyArrowPatch((-25, Y_SEAT), (-25, flange), arrowstyle="<->",
                                     mutation_scale=10, color=INK, lw=1.2))
        ax.text(-26, (Y_SEAT + flange) / 2, "+5 mm", ha="right", va="center", fontsize=11,
                color=INK, fontweight="bold")
        ax.annotate("lens and its silver rim\n5 mm further down", (19.0, flange - 1.5), (27, -31),
                    color=INK, fontsize=10, ha="left", va="center",
                    arrowprops=dict(arrowstyle="->", color=INK, lw=1.0))
    ax.text(-23.5, 2.5, "deck", color="white", va="center", fontsize=9)
    ax.text(-18.5, Y_PCB_FRONT + 1.0, "camera board", color="white", va="center", fontsize=8)
    if not fixed:
        ax.annotate("sensor", (-5, Y_SENSOR), (-33, Y_SENSOR - 3.5), fontsize=9, color=INK,
                    arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
        ax.annotate("lock screw", (-23.0, Y_SEAT + RING_H + 1.9), (-33, Y_SEAT - 2),
                    fontsize=9, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
    ax.text(0, -43, "lens\n(continues down)", color=INK, ha="center", fontsize=9)
    ax.set_xlim(-34, 66)
    ax.set_ylim(-46, 14)
    ax.set_aspect("equal")
    ax.axis("off")


def photo(ax) -> None:
    im = Image.open(PHOTO)
    ax.imshow(im, extent=(0, im.width, im.height, 0))
    ax.set_xlim(0, 1060)
    ax.set_ylim(im.height, 0)
    ax.axis("off")
    box = dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.9)
    ax.annotate("focus thumbscrew\n(now at NEAR)", (150, 280), (8, 205), color=INK, bbox=box,
                arrowprops=dict(arrowstyle="->", color="white", lw=2), fontsize=10, va="center")
    ax.text(5, 392, "Tim's photo, 2026-10-09", color="white", fontsize=9, va="bottom")
    kw = dict(fontsize=11.5, va="center", ha="left")
    ax.annotate("1  Loosen the small lock screw 1\u20132 turns\n    (small flat screwdriver).",
                (265, 142), (625, 40), color=INK, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=INK, lw=1.5), **kw)
    ax.annotate("2  Grip the knurled ring itself, not the lens, and\n"
                "    turn it so it moves DOWN, away from the deck,\n"
                "    about 5 mm: your 16 mm becomes about 21 mm.\n"
                "    For a normal thread that's counter-clockwise\n"
                "    looking up; if the gap shrinks, go the other way.",
                (350, 175), (625, 150), color=ORANGE, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=ORANGE, lw=2.5), **kw)
    ax.text(625, 262, "3  Retighten the lock screw, then refocus:\n"
            "    iris open, focus thumbscrew from FAR toward NEAR.", color=INK,
            fontweight="bold", **kw)
    ax.annotate("Or instead: screw a 5 mm C\u2013CS adapter in between\n"
                "the knurled ring and the lens's silver rim, and\n"
                "leave the ring screwed fully in and locked.",
                (300, 196), (625, 352), color="#b07800", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=AMBER, lw=2), **kw)


def main() -> None:
    fig = plt.figure(figsize=(15, 11.0), dpi=100, facecolor="white")
    gs = fig.add_gridspec(2, 2, height_ratios=[5.66, 4.45], hspace=0.12, wspace=0.03)
    a = fig.add_subplot(gs[0, :])
    b, c = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])
    photo(a)
    stack(b, fixed=False)
    stack(c, fixed=True)
    a.set_title("The focus ring ran out at NEAR: give the lens 5 mm more room", fontsize=16,
                fontweight="bold", loc="left")
    b.set_title("Now: the lens sits 5 mm too close to the sensor", fontsize=13,
                fontweight="bold", loc="left")
    c.set_title("Fixed: 5 mm more between lens and sensor", fontsize=13, fontweight="bold",
                loc="left")
    fig.text(0.5, 0.075, "Sections through the camera and the top of the lens: heights from Raspberry "
             "Pi's HQ Camera drawing, widths roughly to scale.\nThe camera looks down, so 'behind "
             "the sensor' is up. Focusing nearer moves the picture further behind the lens, so a\n"
             "focus ring that runs out at NEAR means the lens needs more distance from the sensor, "
             "not less.", ha="center", va="top", fontsize=10.5, color=GREY)
    out = OUT / "back_focus_fix.png"
    fig.savefig(out, bbox_inches="tight", pad_inches=0.15)
    print(out)


if __name__ == "__main__":
    main()
