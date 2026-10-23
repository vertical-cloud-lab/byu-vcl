#!/usr/bin/env python3
"""Where a 5 mm C-CS ring goes on the lid camera, on Tim's photo of 2026-10-23 20:06 UTC.

    python c_cs_ring.py

Writes frames/2026-10-23/c_cs_ring_where.jpg from frames/2026-10-23/lens_stack_2006Z_crop.jpg
(a crop of the photo posted on #234, without its EXIF). The knurled back-focus ring is all the
way out there, so about 5 mm of its thread shows below the camera body. A C-CS ring (for example
Amazon B09STVLLVY, two per pack) screws into the knurled ring where the lens is now, and the lens
screws into the ring.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / "frames/2026-10-23"
PHOTO = OUT / "lens_stack_2006Z_crop.jpg"

ORANGE, INK = "#ff7800", "#1e1e20"

# (text, point on the photo in crop pixels, text position in crop pixels)
LABELS = [
    ("camera body", (560, 230), (1260, 150)),
    ("knurled back-focus ring, part of the camera:\n"
     "all the way out, about 5 mm of its thread shows", (360, 430), (1260, 330)),
    ("the C–CS ring goes in here: its threaded end\n"
     "screws into the knurled ring, the lens into it", (700, 518), (1260, 520)),
    ("the lens's silver rim (its flange)", (980, 548), (1260, 700)),
]


def main() -> None:
    photo = Image.open(PHOTO)
    w, h = photo.size
    fig, ax = plt.subplots(figsize=(13.0, 5.6), dpi=110)
    ax.imshow(photo, extent=(0, w, h, 0))
    ax.set_xlim(0, w + 820)
    ax.set_ylim(h, 0)
    ax.axis("off")
    box = dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.95)
    for text, xy, xytext in LABELS:
        ax.annotate(text, xy, xytext, color=INK, fontsize=11, va="center", bbox=box,
                    arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=2.0))
        ax.plot(*xy, "o", ms=7, mfc=ORANGE, mec="white", mew=1.2)
    ax.text(12, h - 16, "Tim's photo, 2026-10-23 20:06 UTC (#234)", color="white", fontsize=9,
            va="bottom")
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(OUT / "c_cs_ring_where.jpg", dpi=110, pil_kwargs={"quality": 88})


if __name__ == "__main__":
    main()
