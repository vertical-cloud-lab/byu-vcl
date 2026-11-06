#!/usr/bin/env python3
"""Which thread is which: the knurled back-focus ring came off the camera on the lens (2026-10-30).

    python which_thread.py

Writes frames/2026-10-30/which_thread.jpg, two crops of @mcwilliams03's photos posted on #234
(frames/2026-10-30/camera_body_2026-10-30.jpg and lens_with_knurled_ring_2026-10-30.jpg, without
their EXIF) with numbered parts, and frames/2026-10-30/thread_stack.jpg, an exploded section of
the stack drawn to scale.

The camera's knurled back-focus ring unscrewed from the camera body together with the lens, so
it looked like part of the lens. His caliper readings then line up with the parts:

- 0.965 in (24.5 mm) inside the "lens": the knurled ring's own C-mount thread, 1"-32 UN, whose
  basic minor (crest) diameter is 0.966 in. The printed spacer's threaded end fits it.
- 1.0965 in (27.9 mm) outside the "lens": the knurled ring's outer thread, which screws into the
  camera body. Not a lens standard.
- 1.085 in (27.6 mm) inside the "Pi lens adapter": the camera body's thread for the knurled ring.

The lens's own 1"-32 thread (1.000 in across the crests) was out of sight inside the knurled ring.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / "frames/2026-10-30"
CAMERA = OUT / "camera_body_2026-10-30.jpg"
LENS = OUT / "lens_with_knurled_ring_2026-10-30.jpg"

ORANGE, INK = "#ff7800", "#1e1e20"
CAMERA_GREY, RING_BLUE, LENS_GREY, SILVER = "#3a3a3e", "#4a6fa5", "#2b2b2e", "#b9bcc2"
P = 25.4 / 32   # 1"-32 UN pitch, mm

# (point on the photo in crop pixels, key text); the markers are numbered in order
CAMERA_LABELS = [
    ((235, 680), "The camera body's own thread, about 28 mm across: your \"Pi lens\n"
                 "adapter\", 1.085 in. The knurled ring screws in here."),
    ((700, 805), "The lock-screw clamp, which holds the knurled ring."),
]
LENS_LABELS = [
    ((538, 262), "The C-mount 1\"-32 thread inside the knurled ring: your 0.965 in.\n"
                 "The spacer's threaded end fits it, and that's where it goes."),
    ((585, 385), "The knurled ring's outer thread, about 28 mm: your 1.0965 in.\n"
                 "It screws into the camera body (photo 1, mark 1)."),
    ((210, 520), "The knurled back-focus ring: part of the camera, not the lens."),
    ((345, 551), "The lens's silver rim. The lens's own C-mount thread, 1.000 in\n"
                 "across, is hidden inside the knurled ring."),
]


def zig(z0, z1, r_lo, r_hi, pitch=P):
    """Points up a threaded surface, from z0 to z1, the radius zigzagging between r_lo and r_hi."""
    z = np.arange(z0, z1 + 1e-9, pitch / 2)
    r = np.where(np.arange(len(z)) % 2 == 0, r_lo, r_hi)
    return list(zip(r, z))


def part(ax, pts, color, **kw):
    """Fill a half-section and its mirror image."""
    r, z = np.array(pts).T
    ax.fill(r, z, color=color, lw=0, **kw)
    ax.fill(-r, z, color=color, lw=0, **kw)


def label_photo(ax, path, labels, title, first=1, key_h=330):
    """The photo with numbered orange marks, and the key underneath it."""
    photo = Image.open(path)
    w, h = photo.size
    ax.imshow(photo, extent=(0, w, h, 0))
    ax.set_xlim(0, w)
    ax.set_ylim(h + key_h, 0)
    ax.axis("off")
    ax.set_title(title, fontsize=12.5, color=INK, loc="left")
    key = []
    for n, (xy, text) in enumerate(labels, first):
        ax.plot(*xy, "o", ms=19, mfc=ORANGE, mec="white", mew=1.5)
        ax.text(*xy, str(n), ha="center", va="center", fontsize=11, color="white", weight="bold")
        key.append(f"{n}  " + text.replace("\n", "\n    "))
    ax.text(0, h + 25, "\n".join(key), fontsize=10.5, color=INK, va="top", linespacing=1.45)


def stack(ax):
    """Exploded half-sections, to scale, camera at the top as it hangs under the deck."""
    # lens: barrel, silver rim and its 5 mm C-mount thread
    part(ax, [(10.5, 0), (20.0, 0), (20.0, 10.0), (12.7, 10.0), *zig(10.0, 15.0, 12.7, 12.25),
              (10.5, 15.0)], LENS_GREY)
    part(ax, [(12.7, 10.0), (18.3, 10.0), (18.3, 11.4), (12.7, 11.4)], SILVER)
    ax.fill([-10.5, 10.5, 10.5, -10.5], [7.5, 7.5, 10.0, 10.0], color="#9ec5e8", lw=0)
    # printed spacer: 5 mm flange with the female bore, a 4 mm threaded end
    part(ax, [(15.0, 20.0), (15.0, 25.0), (12.95, 25.0), *zig(25.0, 29.0, 12.7, 12.25),
              (11.05, 29.0), (11.05, 24.6), *zig(20.0, 24.6, 12.95, 12.5)[::-1]], ORANGE)
    # knurled back-focus ring: knurled flange, outer thread into the body, 1"-32 inside
    part(ax, [(17.5, 34.0), (17.5, 36.5), (13.9, 36.5), *zig(36.5, 44.0, 13.9, 13.45),
              *zig(34.0, 44.0, 12.75, 12.3)[::-1]], RING_BLUE)
    # camera body with its thread for the ring, then the board and sensor
    part(ax, [(18.5, 49.0), (18.5, 57.0), *zig(49.0, 57.0, 14.4, 13.95)[::-1]], CAMERA_GREY)
    ax.fill([-20, 20, 20, -20], [57.0, 57.0, 58.6, 58.6], color="#2e7d32", lw=0)
    ax.fill([-4, 4, 4, -4], [56.4, 56.4, 57.0, 57.0], color="#14524a", lw=0)

    arrow = dict(arrowstyle="-|>", color=ORANGE, lw=2.2, mutation_scale=16)
    for r, z0, z1 in [(12.5, 15.6, 19.6), (12.5, 29.6, 33.6), (13.7, 44.6, 48.6)]:
        for s in (1, -1):
            ax.annotate("", (s * r, z1), (s * r, z0), arrowprops=arrow)
    ax.text(0, 17.6, "screws in", ha="center", va="center", fontsize=10, color=ORANGE)
    ax.text(0, 31.6, "screws in", ha="center", va="center", fontsize=10, color=ORANGE)
    ax.text(0, 46.6, "screws in", ha="center", va="center", fontsize=10, color=ORANGE)

    notes = [
        (53.0, "Camera body, on the board. Its thread is about\n28 mm across: your \"Pi lens adapter\", 1.085 in."),
        (39.5, "Knurled back-focus ring, part of the camera.\nOutside: about 28 mm (your 1.0965 in), into the\n"
               "camera body. Inside: C-mount 1\"-32 (your 0.965 in).\nIn your photo it is still on the lens."),
        (24.5, "Printed C–CS spacer: adds 5 mm.\nThreaded end: 1\"-32, into the knurled ring (the fit\n"
               "you found). Bore: 1\"-32, for the lens's thread."),
        (8.5, "Lens. Its own C-mount thread, 1.000 in across\nthe crests and 5 mm long, was hidden inside\n"
              "the knurled ring."),
    ]
    for z, text in notes:
        ax.text(22.5, z, text, fontsize=11, va="center", color=INK)
    ax.set_xlim(-21, 63)
    ax.set_ylim(-1.5, 60.5)
    ax.set_aspect("equal")
    ax.axis("off")


def main() -> None:
    fig = plt.figure(figsize=(13.0, 9.4), dpi=100)
    gs = fig.add_gridspec(1, 2, width_ratios=[979, 694 * 1.43], wspace=0.03,
                          left=0.01, right=0.99, top=0.91, bottom=0.01)
    label_photo(fig.add_subplot(gs[0]), CAMERA, CAMERA_LABELS,
                "Photo 1: the camera, without its knurled ring", key_h=300)
    ax = fig.add_subplot(gs[1])
    label_photo(ax, LENS, LENS_LABELS, "Photo 3: the knurled ring is still on the lens",
                first=len(CAMERA_LABELS) + 1, key_h=300)
    ax.set_xlim(0, 694 * 1.43)
    fig.suptitle("The camera's knurled back-focus ring came off with the lens", fontsize=15,
                 color=INK, x=0.01, ha="left")
    fig.savefig(OUT / "which_thread.jpg", dpi=100, pil_kwargs={"quality": 88})

    fig, ax = plt.subplots(figsize=(12.0, 8.4), dpi=100)
    stack(ax)
    ax.set_title("How they go together: the printed spacer goes between the knurled ring and the "
                 "lens\n(exploded section, to scale; the camera is at the top, as it hangs under "
                 "the deck)", fontsize=13, color=INK, loc="left")
    fig.subplots_adjust(0.01, 0.01, 0.99, 0.9)
    fig.savefig(OUT / "thread_stack.jpg", dpi=100, pil_kwargs={"quality": 88})


if __name__ == "__main__":
    main()
