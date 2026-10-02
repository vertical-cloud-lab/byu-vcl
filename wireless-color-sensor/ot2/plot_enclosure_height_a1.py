#!/usr/bin/env python3
"""Light lost per 0.25 mm of descent, over well A1 (2026-09-30 run 4) and the plate centre (runs 2-3).

While the enclosure hangs free, every 0.25 mm lower cuts the light by a steady
amount. When its foot lands, the drop falls away. Only fine steps (<= 0.5 mm)
are plotted, scaled to 0.25 mm, and only descents taken while the room light was
steady (A1 descent 2 was not).

    python3 plot_enclosure_height_a1.py   ->  enclosure-height-a1-2026-09-30.png
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
A1 = json.load(open(os.path.join(HERE, "enclosure-height-a1-2026-09-30.json")))
CENTRE = json.load(open(os.path.join(HERE, "enclosure-height-2026-09-30.json")))


def drops(ladder):
    pts = [(s["z"], sum(s["reads"]) / len(s["reads"])) for s in ladder if s.get("z") is not None]
    out = []
    for (z0, r0), (z1, r1) in zip(pts, pts[1:]):
        dz = z0 - z1
        if 0 < dz <= 0.5 + 1e-9:
            out.append((z1, (r0 - r1) * 0.25 / dz))
    return out


SERIES = [  # fixed categorical order
    ("A1, descent 1", A1["descent_1"], "#2a78d6", "o"),
    # descent 3 without its ends: the z 88.25 pair differed by 147 counts and the
    # step to 86.5 coincided with a 240-count drop in the room light
    ("A1, descent 3", A1["descent_3"][1:-1], "#eb6834", "s"),
    ("centre, run 2", CENTRE["run2"]["ladder"], "#1baf7a", "^"),
    ("centre, run 3", CENTRE["run3"]["ladder"], "#eda100", "D"),
]

fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=150)
fig.patch.set_facecolor("#fcfcfb")
ax.set_facecolor("#fcfcfb")
for label, ladder, color, marker in SERIES:
    pts = drops(ladder)
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, lw=2, marker=marker,
            ms=6, mec="#fcfcfb", mew=1.5, label=label)
ax.axvspan(87.75, 88.0, color="#2a78d6", alpha=0.10, lw=0)
ax.axvspan(88.25, 88.5, color="#1baf7a", alpha=0.12, lw=0)
ax.text(87.875, 63, "A1 touches\n87.75-88.0", ha="center", va="top", fontsize=8, color="#52514e")
ax.text(88.375, 63, "centre touches\n88.25-88.5", ha="center", va="top", fontsize=8, color="#52514e")
ax.axhline(0, color="#52514e", lw=0.8)
ax.set_xlim(89.6, 86.6)                     # descending, left to right
ax.set_ylim(-6, 66)
ax.set_xlabel("nozzle z (mm), going down")
ax.set_ylabel("light lost per 0.25 mm (counts)")
ax.set_title("Where the light stops falling: the enclosure's foot is on the plate",
             fontsize=10, color="#0b0b0b", loc="left")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color("#52514e")
ax.tick_params(colors="#52514e", labelsize=8)
ax.grid(axis="y", color="#e6e5e1", lw=0.6)
ax.legend(frameon=False, fontsize=8, loc="center right")
fig.tight_layout()
fig.savefig(os.path.join(HERE, "enclosure-height-a1-2026-09-30.png"), facecolor=fig.get_facecolor())
print("wrote enclosure-height-a1-2026-09-30.png")
