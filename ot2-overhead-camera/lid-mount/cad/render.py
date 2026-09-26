#!/usr/bin/env python3
"""Render PNGs of the lid mount into ../renders.

Needs a display; on a headless machine run it under Xvfb:

    xvfb-run -a -s "-screen 0 1920x1080x24" python render.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pyvista as pv

import hardware
from lid_mount import ASSEMBLY, COLORS, Params, box, build, make_view_cone, print_orientation

RENDERS = Path(__file__).resolve().parent.parent / "renders"
PRINTED = ("base", "deck", "drill_template", "spacers")
STEEL, NYLON = (0.74, 0.75, 0.78), (0.96, 0.95, 0.90)


def mesh(wp, tol=0.05) -> pv.PolyData:
    verts, tris = wp.val().tessellate(tol, 0.15)
    pts = np.array([(v.x, v.y, v.z) for v in verts])
    faces = np.hstack([[3, *t] for t in tris])
    return pv.PolyData(pts, faces)


def plotter(size=(1600, 1200)) -> pv.Plotter:
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background("white")
    pl.enable_anti_aliasing("ssaa")
    return pl


def add(pl, wp, name, opacity=1.0, color=None):
    pl.add_mesh(mesh(wp), color=color or COLORS.get(name, (0.6, 0.6, 0.6)), opacity=opacity,
                smooth_shading=False, specular=0.15)


def add_fasteners(pl, p: Params, lift: dict | None = None) -> None:
    """McMaster-Carr screws, nuts and washers (see hardware.py), optionally lifted per group."""
    shapes, _ = hardware.placed(p)
    for name, group in shapes.items():
        dz = (lift or {}).get(name, 0.0)
        for s in group:
            pl.add_mesh(mesh(s.translate((0, 0, dz))), color=NYLON if name == "m4_washers" else STEEL,
                        smooth_shading=False, specular=0.3)


def clip_lid(p, parts, size=180.0):
    return parts["lid"].intersect(box(size, size, 40, z0=-20))


def render_assembly(p: Params, parts: dict, out: Path) -> None:
    pl = plotter()
    add(pl, clip_lid(p, parts), "lid", opacity=0.35)
    for name in ASSEMBLY[1:]:
        add(pl, parts[name], name)
    add_fasteners(pl, p)
    add(pl, make_view_cone(p, 25.0, 90.0), "cone", opacity=0.25, color=(1.0, 0.8, 0.2))
    pl.camera_position = [(330, -420, 260), (0, 0, 45), (0, 0, 1)]
    pl.add_text("OT-2 lid camera mount: HQ Camera + 8-50 mm zoom + Pi 5", font_size=12, color="black")
    pl.screenshot(out / "assembly.png")
    pl.close()


def render_exploded(p: Params, parts: dict, out: Path) -> None:
    lift = {"lid": -40, "base": 0, "lens": 35, "adapter": 55, "camera_mount": 75, "camera_pcb": 75,
            "deck": 110, "pi_spacers": 135, "pi5": 160}
    pl = plotter((1400, 1600))
    for name, dz in lift.items():
        wp = clip_lid(p, parts) if name == "lid" else parts[name]
        add(pl, wp.translate((0, 0, dz)), name, opacity=0.35 if name == "lid" else 1.0)
    add_fasteners(pl, p, {"m4_screws": -75, "m4_washers": -58, "m4_nuts": 14, "cam_screws": 60, "cam_nuts": 124,
                          "m3_screws": 132, "pi_nuts": 96, "pi_screws": 178})
    pl.camera_position = [(500, -620, 400), (0, 0, 100), (0, 0, 1)]
    pl.add_text("Exploded: lid, base, lens, C-CS adapter, camera, deck, Pi 5,\n"
                "and the McMaster-Carr screws, nuts and washers", font_size=11, color="black")
    pl.screenshot(out / "exploded.png")
    pl.close()


def render_section(p: Params, parts: dict, out: Path) -> None:
    """Half section through the optical axis, seen from +X."""
    keep = box(400, 400, 400, cx=-200, z0=-100)
    pl = plotter((1300, 1500))
    for name in ASSEMBLY:
        wp = clip_lid(p, parts) if name == "lid" else parts[name]
        add(pl, wp.intersect(keep), name, opacity=0.6 if name == "lid" else 1.0)
    add(pl, make_view_cone(p, 25.0, 40.0).intersect(keep), "cone", opacity=0.3, color=(1.0, 0.8, 0.2))
    labels = {
        "lid top  Z = 0": (0, -95, 0),
        f"lens front  Z = {p.z_lens_front:.1f}": (0, -95, p.z_lens_front),
        f"collar top  Z = {p.base_t + p.collar_h:.1f}": (0, -95, p.base_t + p.collar_h),
        f"lens flange  Z = {p.z_lens_flange:.1f}": (0, -95, p.z_lens_flange),
        f"camera PCB  Z = {p.z_pcb_back:.1f}": (0, -95, p.z_pcb_back),
        f"deck  Z = {p.z_deck:.1f}": (0, -95, p.z_deck),
    }
    pl.add_point_labels(np.array(list(labels.values()), dtype=float), list(labels.keys()), font_size=18,
                        point_size=8, point_color="red", shape_opacity=0.8, always_visible=True)
    pl.camera_position = [(600, 0, 60), (0, -20, 60), (0, 0, 1)]
    pl.enable_parallel_projection()
    pl.add_text("Section through the optical axis (mm)", font_size=12, color="black")
    pl.screenshot(out / "section.png")
    pl.close()


def render_print_layout(p: Params, parts: dict, out: Path) -> None:
    pl = plotter((1800, 1000))
    offsets = {"base": (-150, 0), "deck": (-10, 0), "drill_template": (140, 0), "spacers": (250, -20)}
    for name, (dx, dy) in offsets.items():
        wp = print_orientation(name, parts[name], p).translate((dx, dy, 0))
        add(pl, wp, name, color=(0.2, 0.2, 0.22))
        pl.add_point_labels(np.array([[dx, dy - 95, 0]], dtype=float), [name.replace("_", " ")], font_size=20,
                            point_size=1, shape_opacity=0.0, always_visible=True)
    pl.camera_position = [(40, -480, 380), (40, 0, 20), (0, 0, 1)]
    pl.add_text("Printed parts, as they sit on the bed (no supports needed)", font_size=12, color="black")
    pl.screenshot(out / "print_layout.png")
    pl.close()


def main() -> None:
    RENDERS.mkdir(parents=True, exist_ok=True)
    p = Params()
    parts = build(p)
    render_assembly(p, parts, RENDERS)
    render_exploded(p, parts, RENDERS)
    render_section(p, parts, RENDERS)
    render_print_layout(p, parts, RENDERS)
    print(f"renders written to {RENDERS}")


if __name__ == "__main__":
    main()
