"""cad_preview.png: station S1 in section with the electrode cap seated, and the cap's parts
exploded above its lid. Reads the STLs that cad_cu_cell.py writes.

    xvfb-run -a python plot_cad_preview.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
META = json.loads((HERE / "cad_parts.json").read_text())
LID_TOP = META["heights"]["lid_top_W"]

COL = {"well_lid": "#e9a47c", "electrode_cap": "#efe9e2", "electrode_carrier": "#9c9b97", "steel_disc": "#8d9196",
       "ag_agcl_ref": "#e9e6df", "pt_coil": "#c7c9cc", "cap_pogo_pins": "#c9a64a", "cap_hold_steel": "#6f7276",
       "face_oring_006": "#1d1d1d", "coupon_20x20x6": "#b89a8a", "lid_pads": "#c77a3a", "lid_eyelets": "#c9a64a",
       "lid_hold_magnets": "#7a7f86", "tray_station": "#f4efe6"}
CAP_PARTS = ("electrode_cap", "electrode_carrier", "steel_disc", "ag_agcl_ref", "pt_coil", "cap_pogo_pins", "cap_hold_steel")
LID_PARTS = ("well_lid", "face_oring_006", "coupon_20x20x6", "lid_pads", "lid_eyelets", "lid_hold_magnets")


def load(name, section):
    f = HERE / (f"{name}_section.stl" if section else f"{name}.stl")
    return pv.read(f).clean().compute_normals(auto_orient_normals=True, split_vertices=True, feature_angle=35)


def font(size, bold=False):
    from matplotlib import font_manager
    return ImageFont.truetype(font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold" if bold else "normal")), size)


def scene_section(pl):
    for name in LID_PARTS + ("tray_station",):
        pl.add_mesh(load(name, True), color=COL[name], smooth_shading=True, specular=0.2)
    for name in CAP_PARTS:
        pl.add_mesh(load(name, True).translate((0, 0, LID_TOP), inplace=False), color=COL[name], smooth_shading=True, specular=0.3)
    pl.camera.position = (34, -150, 52)
    pl.camera.focal_point = (0, 0, 5)
    pl.camera.up = (0, 0, 1)
    pl.camera.view_angle = 20


def scene_exploded(pl):
    lift = {"electrode_cap": 26, "electrode_carrier": 14, "steel_disc": 36, "ag_agcl_ref": 14, "pt_coil": 14,
            "cap_pogo_pins": 26, "cap_hold_steel": 26}
    for name in LID_PARTS:
        dz = {"face_oring_006": -8, "coupon_20x20x6": -20, "lid_hold_magnets": 0}.get(name, 0)
        pl.add_mesh(load(name, False).translate((0, 0, dz), inplace=False), color=COL[name], smooth_shading=True, specular=0.2)
    for name in CAP_PARTS:
        pl.add_mesh(load(name, False).translate((0, 0, LID_TOP + lift[name]), inplace=False), color=COL[name], smooth_shading=True, specular=0.3)
    pl.camera.position = (135, -170, 100)
    pl.camera.focal_point = (0, 0, 20)
    pl.camera.up = (0, 0, 1)
    pl.camera.view_angle = 24


def main():
    w, h = 800, 900
    imgs = []
    for build in (scene_section, scene_exploded):
        pl = pv.Plotter(off_screen=True, window_size=(w, h), lighting="light_kit")
        pl.set_background("#fcfcfb")
        pl.enable_anti_aliasing("ssaa")
        build(pl)
        imgs.append(Image.fromarray(pl.screenshot(return_img=True)))
        pl.close()
    out = Image.new("RGB", (2 * w, h), "#fcfcfb")
    out.paste(imgs[0], (0, 0))
    out.paste(imgs[1], (w, 0))
    d = ImageDraw.Draw(out)
    d.text((18, 14), "A  Station S1 in section, electrode cap seated", font=font(22, True), fill="#0b0b0b")
    d.text((w + 18, 14), "B  The same parts, exploded", font=font(22, True), fill="#0b0b0b")
    notes = ["recommended cap: 0.12 mm clearance skirt over the 16 mm boss, no O-ring,",
             "held down by two 4 x 2 mm magnets in the lid; disc top = magnet contact",
             "AS568-006 face seal squeezed to 1.40 mm; reference tip 3.0 mm above the metal"]
    d.rectangle([0, h - 92, w, h], fill="#fcfcfb")
    for i, t in enumerate(notes):
        d.text((18, h - 82 + 24 * i), t, font=font(16), fill="#52514e")
    d.rectangle([w, h - 44, 2 * w, h], fill="#fcfcfb")
    d.text((w + 18, h - 34), "cap, carrier + electrodes, steel disc; lid + pads, face O-ring, 20 x 20 mm piece",
           font=font(16), fill="#52514e")
    out.save(HERE / "cad_preview.png", optimize=True)
    print("cad_preview.png", out.size)


if __name__ == "__main__":
    main()
