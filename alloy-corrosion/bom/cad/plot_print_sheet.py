"""print-sheet.png: every printed part in the BOM, one tile each, drawn from its own STEP or STL,
with its name, how many to print and the material. Reads ../bom.csv for the list.

    xvfb-run -a python plot_print_sheet.py
"""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import cadquery as cq
import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TILE, COLS = 360, 5


def font(size, bold=False):
    from matplotlib import font_manager
    return ImageFont.truetype(font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold" if bold else "normal")), size)


def mesh_for(step_path: Path) -> pv.PolyData:
    stl = step_path.with_suffix(".stl")
    if not stl.exists():  # the capper module ships STEP only: mesh it in a temp dir, leave its folder alone
        tmp = Path(tempfile.mkdtemp()) / (step_path.stem + ".stl")
        cq.exporters.export(cq.importers.importStep(str(step_path)), str(tmp), tolerance=0.05, angularTolerance=0.3)
        stl = tmp
    return pv.read(stl).clean().compute_normals(auto_orient_normals=True, split_vertices=True, feature_angle=35)


def render(mesh, colour):
    pl = pv.Plotter(off_screen=True, window_size=(TILE, TILE - 70))
    pl.set_background("white")
    pl.add_mesh(mesh, color=colour, smooth_shading=True, specular=0.25)
    pl.enable_parallel_projection()
    pl.camera_position = "iso"
    pl.camera.azimuth = 20
    pl.reset_camera()
    pl.camera.zoom(1.25)
    img = pl.screenshot(return_img=True)
    pl.close()
    return Image.fromarray(img)


def main():
    rows = [r for r in csv.DictReader((HERE.parent / "bom.csv").open()) if r["kind"] == "print" and r["step"]]
    n = len(rows)
    nrows = -(-n // COLS)
    sheet = Image.new("RGB", (COLS * TILE, nrows * TILE + 60), "white")
    d = ImageDraw.Draw(sheet)
    d.text((16, 14), "Printed parts for corrosion testing on the CubXL: one tile per STEP file, drawn from the file itself",
           fill="#222", font=font(22, True))
    palette = {"PETG": "#e9a47c", "PLA": "#9cc3d5", "PTFE": "#f2f2f0"}
    for k, r in enumerate(rows):
        cx, cy = (k % COLS) * TILE, (k // COLS) * TILE + 60
        mesh = mesh_for(REPO / r["step"])
        mat = r["material"].split()[0] if r["material"] else "PETG"
        sheet.paste(render(mesh, palette.get(mat, "#cfcfcf")), (cx, cy))
        d.rectangle([cx + 2, cy + 2, cx + TILE - 3, cy + TILE - 3], outline="#d0d0d0")
        d.text((cx + 10, cy + TILE - 66), r["id"] + "  " + Path(r["step"]).stem, fill="#111", font=font(15, True))
        b = mesh.bounds
        dims = f"{b[1]-b[0]:.0f} x {b[3]-b[2]:.0f} x {b[5]-b[4]:.0f} mm"
        d.text((cx + 10, cy + TILE - 44), f"print {r['qty']}  |  {mat}  |  {dims}", fill="#333", font=font(14))
        d.text((cx + 10, cy + TILE - 24), r["status"][:44], fill="#666", font=font(13))
    sheet.save(HERE.parent / "print-sheet.png", optimize=True)
    print("wrote", HERE.parent / "print-sheet.png", n, "tiles")


if __name__ == "__main__":
    main()
