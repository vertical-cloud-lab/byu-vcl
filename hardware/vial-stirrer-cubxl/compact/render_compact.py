#!/usr/bin/env python3
"""Exploded render of the compact stirrer's printed parts: img/compact_parts.png.

    python compact/render_compact.py img/compact_parts.png

Run from hardware/vial-stirrer-cubxl. Needs pyvista, and a display for VTK (Xvfb will do).
"""
import sys

import pyvista as pv
from PIL import Image, ImageChops
parts = [  # path, colour, (dx, dz)
    ("stl/deck_key.stl", (0.92, 0.92, 0.88), (0.0, -16)),
    ("stl/deck_key.stl", (0.92, 0.92, 0.88), (25.0, -16)),
    ("stl/compact/base_compact.stl", (0.27, 0.29, 0.33), (0, 0)),
    ("stl/magnet_carrier.stl", (0.96, 0.55, 0.10), (0, 14)),
    ("stl/compact/vial_holder_compact.stl", (0.10, 0.58, 0.60), (0, 30)),
]
p = pv.Plotter(off_screen=True, window_size=(1100, 1200))
p.set_background("white")
for path, col, (dx, dz) in parts:
    m = pv.read(path).translate((dx, 0, dz), inplace=False)
    p.add_mesh(m, color=col, smooth_shading=False, specular=0.15, ambient=0.25, diffuse=0.75)
p.camera_position = [(105, -160, 130), (0, 0, 20), (0, 0, 1)]
p.camera.zoom(0.78)
p.enable_anti_aliasing("ssaa")
p.screenshot(sys.argv[1])
im = Image.open(sys.argv[1]).convert("RGB")
box = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()   # trim the white margin
im.crop((max(box[0] - 30, 0), max(box[1] - 30, 0), min(box[2] + 30, im.width), min(box[3] + 30, im.height))).save(sys.argv[1])
print("wrote", sys.argv[1])
