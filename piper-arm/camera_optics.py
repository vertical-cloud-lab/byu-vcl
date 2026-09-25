#!/usr/bin/env python3
"""Field of view and depth of field for the PiPER eye-in-hand camera candidates.

Rows are the four Raspberry Pi cameras from issue #233 (Camera Module 3 in both
lens variants, the Global Shutter with both the official 6 mm lens and a
generic ~3 mm one) plus the two honorable mentions, the Intel RealSense D405 and
Orbbec Gemini 305. Writes ``camera-fov-dof.png`` next to this script and prints
the numbers the report quotes.

Sensor width is pixel count x pixel pitch. Horizontal FoV is Raspberry Pi's
published figure (for the 6 mm CS lens: 45 deg on the GS sensor, 55 deg on the
HQ sensor); 2*atan(w / 2f) agrees with all of them to within 3 deg, so it is
used for the 3 mm lens, which has no official figure.

"Sharp" means a blur spot no larger than one pixel of a 640-px-wide frame, the
resolution a detector or policy network actually consumes (YOLO 640, ACT
480x640). Thin-lens depth of field with hyperfocal H = f^2 / (N c) + f.
"""

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_PX = 640          # frame width the vision model sees
VIEW_AT_MM = 100      # lens-to-object distance for the view-width panel
FOCUS_AT_MM = 200     # focus distance locked for the sharpness panel
SBS_PLATE_MM = 127.76 # ANSI/SLAS microplate length, for scale

# name, sensor px width, pitch um, focal mm, f-number, HFOV deg (None = compute),
# closest focus mm (None = unknown), colour role. The 6 mm lens is F1.2 wide
# open; f/2.8 is the kinder assumption.
CAMS = [
    ("Camera Module 3 Wide", 4608, 1.40, 2.75, 2.2, 102.0, 50, "pick"),
    ("Camera Module 3", 4608, 1.40, 4.74, 1.8, 66.0, 100, "rest"),
    ("Global Shutter + 6 mm, f/2.8", 1456, 3.45, 6.0, 2.8, 45.0, 200, "rest"),
    ("Global Shutter + ~3 mm, f/2.8", 1456, 3.45, 3.0, 2.8, None, None, "rest"),
    ("AI Camera", 4056, 1.55, 4.74, 1.79, 66.3, 200, "rest"),
    ("HQ Camera + 6 mm, f/2.8", 4056, 1.55, 6.0, 2.8, 55.0, 200, "rest"),
]
# Depth cameras: only datasheet numbers, never the thin-lens model.
# D405 87x58 deg; Gemini 305 RGB 94x68 deg, range 4-100 cm, ideal 7-50 cm.
DEPTH = [
    dict(name="RealSense D405", hfov=87.0, depth_mm=(70, 500),
         note="7–50 cm ideal depth range (datasheet)"),
    dict(name="Orbbec Gemini 305", hfov=94.0, depth_mm=(70, 500),
         note="7–50 cm ideal depth range (4–100 cm usable)"),
]

SURFACE, INK, INK2, INK3 = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
PICK, ALT, REST = "#2a78d6", "#eb6834", "#b5b4ad"   # emphasis: slot 1, slot 2, gray
BAND = "#f0efec"


def hfov(cam):
    _, px, pitch, f, _, fov, _, _ = cam
    if fov is not None:
        return fov
    return math.degrees(2 * math.atan(px * pitch / 1000 / (2 * f)))


def view_width(fov_deg, d_mm):
    return 2 * d_mm * math.tan(math.radians(fov_deg) / 2)


def sharp_range(cam, s_mm):
    _, px, pitch, f, n, _, closest, _ = cam
    s_mm = max(s_mm, closest or 0)       # cannot focus nearer than the lens allows
    c = px * pitch / 1000 / OUT_PX       # one output pixel, in mm on the sensor
    h = f * f / (n * c) + f
    near = s_mm * (h - f) / (h + s_mm - 2 * f)
    far = s_mm * (h - f) / (h - s_mm) if s_mm < h else math.inf
    return near, far, h


def bar(ax, y, x0, x1, colour, h=0.46):
    ax.barh(y, x1 - x0, left=x0, height=h, color=colour, lw=0, zorder=3)


def main():
    rows = [c[0] for c in CAMS] + [d["name"] for d in DEPTH]
    ys = list(range(len(rows)))[::-1]

    print(f"{'camera':34s} {'HFOV':>6s} {'w@10cm':>7s} {'w@20cm':>7s} "
          f"{'px/mm@20cm(640)':>15s} {'H mm':>6s} {'sharp @ focus 20 cm':>22s}")
    table = []
    for cam in CAMS:
        fov = hfov(cam)
        near, far, h = sharp_range(cam, FOCUS_AT_MM)
        w10, w20 = view_width(fov, 100), view_width(fov, 200)
        table.append((cam, fov, near, far))
        far_s = "inf" if math.isinf(far) else f"{far / 10:.1f}"
        print(f"{cam[0]:34s} {fov:6.1f} {w10:7.0f} {w20:7.0f} {OUT_PX / w20:15.2f} "
              f"{h:6.0f} {near / 10:9.1f} - {far_s:>5s} cm")
    for d in DEPTH:
        print(f"{d['name']:34s} {d['hfov']:6.1f} {view_width(d['hfov'], 100):7.0f} "
              f"{view_width(d['hfov'], 200):7.0f} {OUT_PX / view_width(d['hfov'], 200):15.2f}")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 5.2), dpi=200, sharey=True,
                                 gridspec_kw=dict(width_ratios=[1, 1.15], wspace=0.08))
    fig.patch.set_facecolor(SURFACE)
    top = len(rows) - 0.05
    label_y, ref_top = top - 0.38, top - 0.62   # reference labels sit above the bars
    for ax in (a1, a2):
        ax.set_facecolor(SURFACE)
        ax.set_ylim(-0.6, top)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(AXIS)
        ax.tick_params(axis="x", colors=INK3, length=0)
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", color=GRID, lw=0.8, zorder=0)
        ax.set_axisbelow(True)

    # panel 1: how wide a strip of bench each camera sees at VIEW_AT_MM
    a1.set_xlim(0, 300)
    a1.vlines(SBS_PLATE_MM, -0.6, ref_top, color=INK2, lw=1, zorder=2)
    a1.text(SBS_PLATE_MM, label_y, "96-well plate, 127.8 mm", ha="center",
            va="center", color=INK2, fontsize=8)
    widths = [view_width(hfov(c), VIEW_AT_MM) for c in CAMS] + \
             [view_width(d["hfov"], VIEW_AT_MM) for d in DEPTH]
    colours = [PICK if c[7] == "pick" else REST for c in CAMS] + [ALT] * len(DEPTH)
    for y, w, col in zip(ys, widths, colours):
        bar(a1, y, 0, w, col)
        a1.text(w + 5, y, f"{w:.0f} mm", va="center", color=INK, fontsize=8.5,
                zorder=4, bbox=dict(fc=SURFACE, ec="none", pad=1.5))
    labels = rows[:len(CAMS)] + [f"{d['name']}\n(honorable mention)" for d in DEPTH]
    a1.set_yticks(ys, labels, color=INK)
    a1.set_xlabel(f"Width of view {VIEW_AT_MM / 10:.0f} cm from the lens (mm)",
                  color=INK2)
    a1.set_title("What fits in the frame", loc="left", color=INK, fontsize=10.5,
                 fontweight="bold")

    # panel 2: what stays sharp with focus locked at FOCUS_AT_MM
    xmax = 60
    a2.set_xlim(0, xmax)
    a2.fill_betweenx([-0.6, ref_top], 10, 20, color=BAND, zorder=1, lw=0)
    a2.text(15, label_y, "grasp zone", ha="center", va="center",
            color=INK2, fontsize=8)
    for y, (cam, fov, near, far) in zip(ys, table):
        col = PICK if cam[7] == "pick" else REST
        far_c = min(far / 10, xmax)
        bar(a2, y, near / 10, far_c, col)
        if cam[6]:
            a2.plot([cam[6] / 10], [y - 0.36], marker="^", ms=5, color=INK2,
                    zorder=4, clip_on=False)
        far_s = "∞" if math.isinf(far) else f"{far / 10:.0f}"
        a2.text(far_c + 0.8, y, f"{near / 10:.0f}–{far_s} cm", va="center",
                color=INK, fontsize=8.5)
    for y, d in zip(ys[len(CAMS):], DEPTH):
        lo, hi = d["depth_mm"]
        bar(a2, y, lo / 10, hi / 10, ALT)
        a2.text((lo + hi) / 20, y, d["note"], ha="center", va="center", color=INK,
                fontsize=8)
    a2.set_xlabel("Lens-to-object distance (cm)", color=INK2)
    a2.set_title(f"What stays sharp with focus locked at {FOCUS_AT_MM / 10:.0f} cm",
                 loc="left", color=INK, fontsize=10.5, fontweight="bold")

    fig.text(0.01, 0.012,
             f"Sharp = blur spot ≤ 1 pixel of a {OUT_PX}-px-wide frame (thin-lens model). "
             "▲ = closest focus the lens allows (AI Camera and the 6 mm lens: 20 cm).\n"
             "Official Raspberry Pi FoV figures, except the generic ~3 mm lens (from sensor size). "
             "The 6 mm CS lens is F1.2 wide open, so f/2.8 flatters GS and HQ.\n"
             "Grasp zone assumes the lens sits ~10 cm behind the fingertips. "
             "Script: piper-arm/camera_optics.py",
             color=INK3, fontsize=7, linespacing=1.5)
    fig.subplots_adjust(left=0.185, right=0.975, top=0.92, bottom=0.195)
    fig.savefig(Path(__file__).with_name("camera-fov-dof.png"), facecolor=SURFACE)
    print("wrote camera-fov-dof.png")


if __name__ == "__main__":
    main()
