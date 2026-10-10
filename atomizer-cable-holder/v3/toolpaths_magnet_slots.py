"""Draw the sliced toolpaths over the magnet slots' 1 mm skins, from the plate G-code that was sent.

    python toolpaths_magnet_slots.py   # writes evidence/2026-10-08/skin_toolpaths.png

Reads Metadata/plate_1.gcode from atomizer_holder_v3_magnet_slots_A1mini_blackPLA.gcode.3mf.
Each extrusion is drawn as a strip of its own width, from the E per mm:
cross-section = E * pi * (1.75 / 2)^2 / length, and width = section / h + h * (1 - pi / 4)
for a line of height h with rounded sides. Bed coordinates: the part's back face is y = 112.5.
"""
import math
import re
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
SLICE = HERE / "atomizer_holder_v3_magnet_slots_A1mini_blackPLA.gcode.3mf"
OUT = HERE / "evidence" / "2026-10-08" / "skin_toolpaths.png"
FILAMENT_AREA = math.pi * (1.75 / 2) ** 2
BACK_FACE_Y = 112.5

# Three categorical slots (validated all-pairs), everything else folded into a neutral "other".
COLOURS = {"Outer wall": "#2a78d6", "Gap infill": "#eb6834", "Bridge": "#1baf7a"}
OTHER = "#b4b2ab"
PANELS = [  # (z, x window, y window, title)
    (40.0, (66.0, 80.0), (105.5, 113.5), "z = 40 mm, through an upright slot"),
    (10.0, (64.0, 78.0), (105.5, 113.5), "z = 10 mm, through the cross slot"),
    (15.8, (64.0, 78.0), (105.5, 113.5), "z = 15.8 mm, the cross slot's roof"),
]


def layers(gcode, wanted):
    """Extrusion segments (x0, y0, x1, y1, feature, width) on the wanted layers."""
    out = {z: [] for z in wanted}
    x = y = 0.0
    z = h = None
    feature = None
    for line in gcode.splitlines():
        if line.startswith("; Z_HEIGHT:"):
            z = float(line.split(":")[1])
            continue
        if line.startswith("; LAYER_HEIGHT:"):
            h = float(line.split(":")[1])
            continue
        if line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
            continue
        if not line.startswith(("G1 ", "G0 ")):
            continue
        words = dict((k, float(v)) for k, v in re.findall(r"([XYE])([-\d.]+)", line))
        nx, ny = words.get("X", x), words.get("Y", y)
        layer = next((w for w in wanted if z is not None and abs(w - z) < 1e-3), None)
        length = math.hypot(nx - x, ny - y)
        if layer is not None and words.get("E", 0) > 0 and length > 1e-6:
            section = words["E"] * FILAMENT_AREA / length
            out[layer].append((x, y, nx, ny, feature, section / h + h * (1 - math.pi / 4)))
        x, y = nx, ny
    return out


def strip(x0, y0, x1, y1, w):
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy)
    ox, oy = -dy / n * w / 2, dx / n * w / 2
    return [(x0 + ox, y0 + oy), (x1 + ox, y1 + oy), (x1 - ox, y1 - oy), (x0 - ox, y0 - oy)]


def main():
    gcode = zipfile.ZipFile(SLICE).read("Metadata/plate_1.gcode").decode()
    segs = layers(gcode, [p[0] for p in PANELS])
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.3), facecolor="#fcfcfb")
    for ax, (z, (xa, xb), (ya, yb), title) in zip(axes, PANELS):
        ax.set_facecolor("#fcfcfb")
        polys = [strip(*s[:4], s[5]) for s in segs[z]]
        colours = [COLOURS.get(s[4], OTHER) for s in segs[z]]
        ax.add_collection(PolyCollection(polys, facecolors=colours, edgecolors="none"))
        ax.axhline(BACK_FACE_Y, color="#0b0b0b", lw=1)
        ax.axhline(BACK_FACE_Y - 1.0, color="#0b0b0b", lw=1, ls=(0, (3, 3)))
        ax.annotate("", xy=(xb - 0.6, BACK_FACE_Y), xytext=(xb - 0.6, BACK_FACE_Y - 1.0),
                    arrowprops=dict(arrowstyle="<->", color="#0b0b0b", lw=1, shrinkA=0, shrinkB=0))
        ax.text(xb - 0.8, BACK_FACE_Y - 1.45, "1.0 mm skin", ha="right", va="center", fontsize=10,
                color="#0b0b0b", bbox=dict(fc="#fcfcfb", ec="none", pad=1))
        ax.text(xa + 0.3, BACK_FACE_Y + 0.35, "back face (against the panel)", fontsize=9,
                color="#52514e", va="bottom")
        ax.set_xlim(xa, xb)
        ax.set_ylim(ya, yb + 0.6)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=11, color="#0b0b0b", loc="left")
        ax.set_xlabel("bed x (mm)", color="#52514e")
        ax.tick_params(colors="#52514e", labelsize=8)
        for spine in ax.spines.values():
            spine.set_color("#d6d4cd")
    axes[0].set_ylabel("bed y (mm)", color="#52514e")
    axes[0].text(72.5, 109.8, "magnet slot", ha="center", fontsize=10, color="#52514e")
    axes[1].text(71.0, 109.8, "magnet slot (cross)", ha="center", fontsize=10, color="#52514e")
    axes[2].text(71.0, 109.75, "bridged roof, 3.5 mm span", ha="center", fontsize=10, color="#0b0b0b",
                 bbox=dict(fc="#fcfcfb", ec="none", pad=1.5))
    handles = [Patch(color=c, label=k) for k, c in COLOURS.items()] + [Patch(color=OTHER, label="Other (inner wall, infill)")]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=10)
    fig.suptitle("Atomizer Holder V3 with magnet slots: the sent slice over the 1 mm skins (A1 mini, 0.20mm Standard)",
                 fontsize=12, color="#0b0b0b", x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.1, 1, 0.94))
    fig.savefig(OUT, dpi=110, facecolor=fig.get_facecolor())
    print(OUT)


if __name__ == "__main__":
    main()
