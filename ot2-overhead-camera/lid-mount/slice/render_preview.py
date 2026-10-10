#!/usr/bin/env python3
"""Preview images for lid_mount_A1mini_PLA.3mf.

    python render_preview.py    # after slice_a1mini.py -> preview/*.png

toolpaths.png      every extrusion move of each plate's G-code, read straight out of
                   the 3MF, in Bambu Studio's Preview colours; plus each first layer
                   on the 180 x 180 mm bed. Travel and retraction are left out, and
                   arcs (G2/G3) are expanded into short chords.
bambu_plates.png   Bambu Studio's own plate renders (--export-png), if
                   slice_a1mini.py could open an OpenGL context for them.
"""
from __future__ import annotations

import json
import math
import re
import zipfile
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Line3DCollection  # noqa: E402

HERE = Path(__file__).resolve().parent
THREE_MF = HERE / "lid_mount_A1mini_PLA.3mf"
OUT = HERE / "preview"
BED = 180.0

# Bambu Studio's Preview legend (GCodeRenderer/BaseRenderer.cpp), so the two compare by eye.
FEATURES = {
    "Outer wall": "#FF7D38",
    "Inner wall": "#FFE64D",
    "Overhang wall": "#1F1FFF",
    "Top surface": "#F04040",
    "Bridge": "#4D80BA",
    "Sparse infill": "#B03029",
    "Internal solid infill": "#9654CC",
    "Bottom surface": "#665CC7",
}
OTHER = "#A0A0A0"          # gap infill and anything else
SURFACE, INK, MUTED = "#26282B", "#E8E8E8", "#9A9FA6"
WORD = re.compile(r"([XYEIJ])(-?\d*\.?\d+)")


def arc(x0, y0, x1, y1, i, j, cw):
    cx, cy, r = x0 + i, y0 + j, math.hypot(i, j)
    a0 = math.atan2(y0 - cy, x0 - cx)
    sweep = math.atan2(y1 - cy, x1 - cx) - a0
    if cw and sweep >= 0:
        sweep -= 2 * math.pi
    elif not cw and sweep <= 0:
        sweep += 2 * math.pi
    t = np.linspace(a0, a0 + sweep, max(2, int(abs(sweep) * r / 0.5) + 1))
    return np.column_stack([cx + r * np.cos(t), cy + r * np.sin(t)])


def parse(gcode: str) -> tuple[np.ndarray, list[str], np.ndarray]:
    """Extrusion segments (N x 2 x 3), their feature names, and a first-layer mask.

    Only moves after the first layer change count, which leaves out the start
    G-code's purge and its prime line in front of the printable area (Y < 0)."""
    x = y = z = 0.0
    feature, layer = None, 0
    segs, feats, first = [], [], []
    for line in gcode.splitlines():
        if line.startswith(";"):
            if line.startswith("; FEATURE: "):
                feature = line[11:].strip()
            elif line.startswith("; Z_HEIGHT: "):
                z, layer = float(line[12:]), layer + 1
            continue
        cmd = line[:3]
        if cmd not in ("G1 ", "G2 ", "G3 "):
            continue
        w = dict(WORD.findall(line.split(";", 1)[0]))
        nx, ny = float(w.get("X", x)), float(w.get("Y", y))
        if float(w.get("E", 0)) > 0 and (nx, ny) != (x, y):
            if cmd != "G1 " and ("I" in w or "J" in w):
                pts = arc(x, y, nx, ny, float(w.get("I", 0)), float(w.get("J", 0)), cmd == "G2 ")
            else:
                pts = np.array([[x, y], [nx, ny]])
            for a, b in zip(pts[:-1], pts[1:]) if layer else ():
                segs.append(((a[0], a[1], z), (b[0], b[1], z)))
                feats.append(feature)
                first.append(layer == 1)
        x, y = nx, ny
    return np.array(segs), feats, np.array(first)


def fmt_time(s: float) -> str:
    h, m = divmod(round(s / 60), 60)
    return f"{h} h {m:02d} min" if h else f"{m} min"


def toolpaths(plates: list[dict]) -> Path:
    n = len(plates)
    fig = plt.figure(figsize=(16 * n / 3, 10.4), facecolor=SURFACE)
    with zipfile.ZipFile(THREE_MF) as z:
        for k, plate in enumerate(plates):
            segs, feats, first = parse(z.read(f"Metadata/plate_{plate['plate']}.gcode").decode())
            cols = np.array([FEATURES.get(f, OTHER) for f in feats])
            zmax = float(segs[:, :, 2].max())

            ax = fig.add_subplot(2, n, k + 1, projection="3d", facecolor=SURFACE)
            ax.add_collection3d(Line3DCollection(segs, colors=cols, linewidths=0.5))
            ax.plot([0, BED, BED, 0, 0], [0, 0, BED, BED, 0], [0] * 5, color=MUTED, lw=0.8)
            ax.set(xlim=(0, BED), ylim=(0, BED), zlim=(0, zmax))
            ax.set_box_aspect((BED, BED, zmax), zoom=1.25)
            ax.set_proj_type("ortho")
            ax.view_init(elev=30, azim=-60)
            ax.set_axis_off()
            ax.set_title(f"Plate {plate['plate']} · {plate['name']}\n"
                         f"{fmt_time(plate['print_time_s'])} · {plate['filament_g']:.0f} g · "
                         f"{zmax:.1f} mm tall", color=INK, fontsize=12)

            ax2 = fig.add_subplot(2, n, k + 1 + n, facecolor=SURFACE)
            s2 = segs[first][:, :, :2]
            ax2.add_collection(LineCollection(s2, colors=cols[first], linewidths=0.35))
            ax2.plot([0, BED, BED, 0, 0], [0, 0, BED, BED, 0], color=MUTED, lw=0.8)
            ax2.set(xlim=(-5, BED + 5), ylim=(-5, BED + 5), aspect="equal")
            ax2.set_title("first layer on the 180 × 180 mm bed", color=MUTED, fontsize=10)
            ax2.tick_params(colors=MUTED, labelsize=8)
            for s in ax2.spines.values():
                s.set_visible(False)
            ax2.set_xticks([0, 90, 180])
            ax2.set_yticks([0, 90, 180])

    handles = [Line2D([], [], color=c, lw=3, label=n) for n, c in FEATURES.items()]
    handles.append(Line2D([], [], color=OTHER, lw=3, label="Gap infill / other"))
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False, labelcolor=INK, fontsize=10)
    fig.suptitle("lid mount · Bambu Lab A1 mini · 0.20 mm Standard, 3 walls, 25 % infill · Bambu PLA Basic",
                 color=INK, fontsize=13)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.1, hspace=0.12, wspace=0.05)
    out = OUT / "toolpaths.png"
    fig.savefig(out, dpi=110, facecolor=SURFACE)
    plt.close(fig)
    return out


def bambu_plates(plates: list[dict], png_dir: Path) -> Path | None:
    files = [png_dir / f"plate_{p['plate']}_0.png" for p in plates]
    if not all(f.exists() for f in files):
        return None
    fig, axs = plt.subplots(1, len(files), figsize=(5 * len(files), 5.2), facecolor="#F2F2F2")
    for ax, f, plate in zip(axs, files, plates):
        im = mpimg.imread(f)
        ys, xs = np.nonzero(im[..., 3] > 0)
        pad = 12
        ax.imshow(im[max(ys.min() - pad, 0):ys.max() + pad, max(xs.min() - pad, 0):xs.max() + pad])
        ax.set_title(f"Plate {plate['plate']} · {plate['name']}", fontsize=12)
        ax.axis("off")
    fig.suptitle("Bambu Studio's own plate renders (bambu-studio --export-png), black PLA", fontsize=12)
    fig.tight_layout()
    out = OUT / "bambu_plates.png"
    fig.savefig(out, dpi=100, facecolor="#F2F2F2")
    plt.close(fig)
    return out


def main() -> None:
    OUT.mkdir(exist_ok=True)
    plates = json.loads((HERE / "report.json").read_text())["plates"]
    print(toolpaths(plates))
    print(bambu_plates(plates, HERE / "build" / "png"))


if __name__ == "__main__":
    main()
