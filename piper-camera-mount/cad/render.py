#!/usr/bin/env python3
"""Render PNGs of the PiPER camera mount into ../renders.

Needs a display; on a headless machine run it under Xvfb:

    xvfb-run -a -s "-screen 0 1920x1080x24" python render.py
"""
from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq
import numpy as np
import pyvista as pv

import reference
from piper_mount import (ASSEMBLY, CM3W_FOV, COLORS, Params, build, hq_fov, optical_axes,
                         print_orientation, view_pyramid)

RENDERS = Path(__file__).resolve().parent.parent / "renders"
ALU, DARK, PAD = (0.78, 0.79, 0.81), (0.20, 0.20, 0.22), (0.35, 0.35, 0.37)


def mesh(shape, tol=0.08) -> pv.PolyData:
    shape = shape.val() if isinstance(shape, cq.Workplane) else shape
    verts, tris = shape.tessellate(tol, 0.2)
    pts = np.array([(v.x, v.y, v.z) for v in verts])
    return pv.PolyData(pts, np.hstack([[3, *t] for t in tris]))


def plotter(size=(1600, 1200)) -> pv.Plotter:
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background("white")
    pl.enable_anti_aliasing("ssaa")
    return pl


def add_gripper(pl, opening=60.0, opacity=1.0):
    sol = reference.gripper_solids()
    shift = (opening - reference.OPENING_AS_MODELLED) / 2
    for i, s in enumerate(sol):
        if i in reference.UPPER_FINGER:
            s = s.translate(cq.Vector(0, 0, shift))
        elif i in reference.LOWER_FINGER:
            s = s.translate(cq.Vector(0, 0, -shift))
        color = PAD if i in (6, 10) else (DARK if i in (1, 5, 8, 9, 12) else ALU)
        pl.add_mesh(mesh(s, 0.15), color=color, opacity=opacity, smooth_shading=False, specular=0.2)


def add_parts(pl, parts, names=ASSEMBLY, offset=None):
    for name in names:
        wp = parts[name]
        if offset and name in offset:
            wp = wp.translate(offset[name])
        pl.add_mesh(mesh(wp), color=COLORS[name], smooth_shading=False, specular=0.15)


def add_cones(pl, p, depth=160.0):
    axes = optical_axes(p)
    hf, vf = hq_fov(p)
    pl.add_mesh(mesh(view_pyramid(*axes["hq"], hf, vf, depth, aperture=6.0)), color=(1.0, 0.8, 0.2), opacity=0.22)
    pl.add_mesh(mesh(view_pyramid(*axes["cm3w"], *CM3W_FOV, depth * 0.6, aperture=1.5)),
                color=(0.3, 0.6, 1.0), opacity=0.15)


def render_assembly(p, parts, out):
    for tag, cam in (("assembly", [(-420, -330, 260), (-20, 0, 5), (0, 0, 1)]),
                     ("assembly_pi_side", [(420, 260, 230), (0, 20, 5), (0, 0, 1)])):
        pl = plotter()
        add_gripper(pl)
        add_parts(pl, parts)
        if tag == "assembly":
            add_cones(pl, p)
        pl.camera_position = cam
        pl.add_text("AgileX PiPER gripper (AgileX STEP) + Pi 5, HQ Camera with 6 mm lens, Camera Module 3 Wide"
                    + ("\nyellow: HQ field of view; blue: Wide field of view" if tag == "assembly" else ""),
                    font_size=11, color="black")
        pl.screenshot(out / f"{tag}.png")
        pl.close()


def render_front(p, parts, out):
    """From in front of the fingertips, looking back up the approach axis."""
    pl = plotter((1400, 1100))
    add_gripper(pl, opening=100.0)
    add_parts(pl, parts)
    pl.camera_position = [(p.ax_x, -600, p.ax_z), (p.ax_x - 15, 0, p.ax_z + 5), (0, 0, 1)]
    pl.enable_parallel_projection()
    pl.add_text("Looking back from the fingertips (fingers fully open, 100 mm)", font_size=12, color="black")
    pl.screenshot(out / "front.png")
    pl.close()


def render_exploded(p, parts, out):
    off = {"bracket": (-40, 0, 0), "hq_pcb": (-40, -35, 0), "hq_mount": (-40, -35, 0), "hq_lens": (-40, -70, 0),
           "cm_pcb": (-40, -35, 0), "cm_module": (-40, -35, 0), "carrier": (40, 0, 0), "pi_spacers": (60, 0, 0),
           "pi5": (85, 0, 0)}
    pl = plotter((1700, 1100))
    add_gripper(pl, opacity=0.35)
    add_parts(pl, parts, offset=off)
    pl.camera_position = [(-250, -520, 420), (0, 0, 0), (0, 0, 1)]
    pl.add_text("Exploded: bracket and cameras (-X), carrier, spacers and Pi 5 (+X)", font_size=12, color="black")
    pl.screenshot(out / "exploded.png")
    pl.close()


def render_camera_view(p, parts, out, which: str, depth_to_target=120.0):
    """What each camera sees: the gripper, a vial between the fingers, and a 10 mm grid
    `depth_to_target` past the fingertips (square to the approach axis)."""
    o, d = optical_axes(p)[which]
    if which == "hq":
        hf, vf = hq_fov(p)
        size = (1600, int(1600 * 3040 / 4056))
    else:
        hf, vf = CM3W_FOV
        size = (1600, 900)
    pl = plotter(size)
    add_gripper(pl, opening=40.0)
    y_t = -77.52 - depth_to_target
    grid = pv.Plane(center=(p.ax_x, y_t, p.ax_z), direction=(0, 1, 0), i_size=1000, j_size=1000,
                    i_resolution=100, j_resolution=100)
    pl.add_mesh(grid, color=(0.97, 0.97, 0.95), show_edges=True, edge_color=(0.6, 0.6, 0.6))
    pl.add_mesh(pv.Cylinder(center=(p.ax_x, -62.0, p.ax_z), direction=(0, 1, 0), radius=6.0, height=40),
                color=(0.55, 0.75, 0.95), opacity=0.8)      # a 12 mm vial held by the fingertips
    pl.add_mesh(pv.Sphere(radius=3.0, center=(p.ax_x, y_t + 0.5, p.ax_z)), color="red")
    pl.camera.position = tuple(o)
    pl.camera.focal_point = tuple(o + d * 200)
    pl.camera.up = (0, 0, 1)   # the HQ hangs connector-down, so rotate its image 180 deg in software
    pl.camera.view_angle = vf
    pl.camera.clipping_range = (1.0, 2000.0)
    label = ("HQ Camera + 6 mm lens" if which == "hq" else "Camera Module 3 Wide")
    pl.add_text(f"{label}: simulated view ({hf:.0f} x {vf:.0f} deg). Grid: 10 mm squares, "
                f"{depth_to_target:.0f} mm past the fingertips; red dot on the gripper axis", font_size=10,
                color="black")
    pl.screenshot(out / f"view_{which}.png")
    pl.close()


def render_print_layout(p, parts, out):
    pl = plotter((1700, 900))
    for name, dx in (("bracket", -70.0), ("carrier", 60.0), ("spacers", 150.0)):
        wp = print_orientation(name, parts[name]).translate((dx, 0, 0))
        pl.add_mesh(mesh(wp), color=(0.93, 0.45, 0.13), smooth_shading=False, specular=0.15)
    pl.add_mesh(pv.Plane(center=(20, 0, -0.2), direction=(0, 0, 1), i_size=330, j_size=180), color=(0.25, 0.25, 0.27))
    pl.camera_position = [(20, -420, 330), (20, 0, 20), (0, 0, 1)]
    pl.add_text("Printed parts as they sit on the bed: bracket camera-plate down, carrier Pi-plate down",
                font_size=12, color="black")
    pl.screenshot(out / "print_layout.png")
    pl.close()


def main() -> None:
    RENDERS.mkdir(parents=True, exist_ok=True)
    p = Params()
    parts = build(p)
    render_assembly(p, parts, RENDERS)
    render_front(p, parts, RENDERS)
    render_exploded(p, parts, RENDERS)
    render_camera_view(p, parts, RENDERS, "hq")
    render_camera_view(p, parts, RENDERS, "cm3w")
    render_print_layout(p, parts, RENDERS)
    print(f"renders written to {RENDERS}")


if __name__ == "__main__":
    main()
