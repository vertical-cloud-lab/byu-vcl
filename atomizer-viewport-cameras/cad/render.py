#!/usr/bin/env python3
"""Renders of the Onshape export (../exports/onshape_partstudio.step), coloured by part name.

    xvfb-run -a -s "-screen 0 1920x1080x24" python render.py      # -> ../renders/*.png
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pyvista as pv

from check import EXPORTS, read_named_solids

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "renders"


def colour(name: str) -> tuple[tuple[float, float, float], float]:
    n = name.lower()
    if "open" in n and n.startswith("(machine)"):
        return (0.95, 0.75, 0.45), 0.22
    if "glass" in n or "window" in n:
        return (0.55, 0.80, 0.95), 0.45
    if "blue frame" in n:
        return (0.10, 0.25, 0.62), 1.0
    if "amazemet" in n:
        return (0.33, 0.34, 0.37), 1.0
    if n.startswith("(machine)"):
        return (0.76, 0.77, 0.79), 1.0
    if "face plate" in n or "detent collar" in n:
        return (0.93, 0.47, 0.10), 1.0
    if "(print)" in n:
        return (0.16, 0.16, 0.18), 1.0
    if "screen" in n:
        return (0.12, 0.30, 0.62), 1.0
    if "lens" in n or "connector" in n or "display" in n or "magnetic" in n:
        return (0.06, 0.06, 0.07), 1.0
    if "camera" in n or "raspberry pi 5" in n:
        return (0.07, 0.45, 0.22), 1.0
    return (0.80, 0.81, 0.83), 1.0


def mesh(shape) -> pv.PolyData:
    v, t = shape.tessellate(0.2, 0.25)
    pts = np.array([[p.x, p.y, p.z] for p in v])
    faces = np.hstack([[3, *tri] for tri in t])
    return pv.PolyData(pts, faces)


def scene(solids, clip=None, skip=()):
    pl = pv.Plotter(off_screen=True, window_size=(1600, 1100))
    pl.set_background("white")
    for name, s in solids:
        if any(k in name for k in skip):
            continue
        m = mesh(s)
        if clip is not None:
            m = m.clip(normal=clip[0], origin=clip[1], invert=False)
            if m.n_points == 0:
                continue
        c, op = colour(name)
        pl.add_mesh(m, color=c, opacity=op, smooth_shading=False, specular=0.2)
    pl.enable_anti_aliasing("ssaa")
    return pl


def shot(pl, name, pos, focal, up=(0, 0, 1), zoom=1.0, label=None):
    pl.camera_position = [pos, focal, up]
    pl.camera.zoom(zoom)
    if label:
        pl.add_text(label, position="upper_left", font_size=12, color="black")
    OUT.mkdir(exist_ok=True)
    pl.screenshot(str(OUT / f"{name}.png"))
    pl.close()
    print("wrote", name)


def main() -> None:
    solids = read_named_solids(EXPORTS / "onshape_partstudio.step")
    # overall, from the operator's front left
    shot(scene(solids), "overall", (-1700, -2300, 2300), (60, 0, 1250), zoom=1.25,
         label="rePowder viewport cameras: front (HQ + wide), left (door), top (lid window)\nmachine approximate; every size is an Onshape variable")
    # front unit
    shot(scene(solids, skip=("blue frame",)), "front_unit", (-350, -800, 1350), (-15, -200, 1040), zoom=1.6,
         label="Front port: socket over AMAZEMET's LED cover, keyed by its cable pod;\nHQ (M12) + Camera Module 3 Wide, Pi 5, 5 in HDMI display")
    # section through the front port axis (vertical plane through it, perpendicular to x)
    shot(scene(solids, clip=((1, 0, 0), (-15 - 15, 0, 0)), skip=("blue frame",)), "front_section",
         (-700, -330, 1090), (-30, -190, 1050), zoom=1.5,
         label="Section through the HQ Camera's axis: the cameras sit at the cover's\nfront opening and look through it and the port glass at the plate")
    # left unit
    shot(scene(solids, skip=("blue frame",)), "left_unit", (-900, -350, 1250), (-180, 20, 980), zoom=1.5,
         label="Left port: clamp collar on the door's sight-glass ring;\nCamera Module 3 Wide, Pi 5, 5 in Touch Display 2 (rides on the door)")
    # top unit with the line of sight
    pl = scene(solids)
    w = np.array([0.0, -93.9, 1455.0])
    aim = np.array([0.0, 0.0, 1240.0])
    u = (w - aim) / np.linalg.norm(w - aim)
    pl.add_mesh(pv.Line(aim, w + u * 250), color=(0.85, 0.1, 0.1), line_width=4)
    shot(pl, "top_unit", (-1100, -1200, 2000), (-40, -40, 1600), zoom=1.3,
         label="Top: HQ + 16 mm lens aimed through the lid window at the melt (red line),\non a 2020 arm that swings clear on a ball-plunger detent; lid shown open (ghost)")


if __name__ == "__main__":
    main()
