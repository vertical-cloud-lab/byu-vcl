#!/usr/bin/env python3
"""Render PNGs of the Pi 5 dual-camera mount into ../renders.

Uses Raspberry Pi's own Pi 5 and Camera Module 3 models when fetch_models.py has put them
in .cache/, and the simplified models in mount.py otherwise. Needs a display; on a headless
machine run it under Xvfb:

    xvfb-run -a -s "-screen 0 1920x1080x24" python render.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pyvista as pv

from mount import (COLORS, Params, build_config, color_for, make_active_cooler, make_cm3, make_mount,
                   make_pi5, view_frustum)

HERE = Path(__file__).resolve().parent
RENDERS = HERE.parent / "renders"
CACHE = HERE / ".cache"
CABLE = (0.93, 0.93, 0.90)


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


def add(pl, wp_or_mesh, color, opacity=1.0):
    m = wp_or_mesh if isinstance(wp_or_mesh, pv.DataSet) else mesh(wp_or_mesh)
    pl.add_mesh(m, color=color, opacity=opacity, smooth_shading=False, specular=0.15)


# --- Raspberry Pi's own models, placed in mount coordinates -----------------------------------

def real_pi5(p: Params) -> pv.PolyData | None:
    f = CACHE / "pi5.stl"
    if not f.exists():
        return None
    m = pv.read(f)
    pts = m.points.copy()
    x, y, z = pts[:, 0].copy(), pts[:, 1].copy(), pts[:, 2].copy()
    pts[:, 0] = p.pi_x_edge - y          # board Y (up from the port edge) runs along -X
    pts[:, 1] = p.pi_y0 + x              # board X runs backwards from the microSD edge
    pts[:, 2] = p.pi_z + z - 0.03        # the STEP's PCB underside is at Z = 0.03
    m.points = pts
    return m


def real_cm3(p: Params, xc: float) -> pv.PolyData | None:
    f = CACHE / "cm3_standard.stl"
    if not f.exists():
        return None
    m = pv.read(f)
    pts = m.points.copy()
    x, y, z = pts[:, 0].copy(), pts[:, 1].copy(), pts[:, 2].copy()
    pts[:, 0] = xc + y - 12.5            # across the board
    pts[:, 1] = -p.cm3_boss_h + z - 0.013  # the STEP's lens looks along -Z; PCB back at Z = 0.013
    pts[:, 2] = p.axis_z + x - 14.4      # the lens axis is 14.4 mm from the far edge
    m.points = pts
    return m


# --- ribbon cables ----------------------------------------------------------------------------

def bezier(p0, p1, p2, p3, n=40):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def ribbon(path: np.ndarray, w0: float, w1: float) -> pv.PolyData:
    """A flat cable along `path` whose width stays as close to X as the path allows."""
    tang = np.gradient(path, axis=0)
    tang /= np.linalg.norm(tang, axis=1)[:, None]
    ex = np.array([1.0, 0, 0])
    wdir = ex - (tang @ ex)[:, None] * tang
    wdir /= np.linalg.norm(wdir, axis=1)[:, None]
    s = np.linspace(0, 1, len(path))
    width = np.where(s < 0.75, w0, w0 + (w1 - w0) * (s - 0.75) / 0.25)[:, None]
    left, right = path - wdir * width / 2, path + wdir * width / 2
    pts = np.vstack([left, right])
    n = len(path)
    faces = np.hstack([[4, i, i + 1, n + i + 1, n + i] for i in range(n - 1)])
    return pv.PolyData(pts, faces)


def cable_paths(p: Params, cams: list[str]) -> list[np.ndarray]:
    """From the top of each camera's connector, up through its slot, then down into one of the
    Pi 5's two camera connectors from above."""
    conn_x = p.pi_x_edge - 8.5
    conn_ys = [p.pi_y0 + 55.0 - 0.1, p.pi_y0 + 48.6]      # right camera to the rear connector
    z_conn = p.pi_z + 5.3
    zs = p.axis_z + p.slot_v
    out = []
    for i, (kind, xc) in enumerate(zip(cams, p.stations)):
        top = p.hq_board / 2 if kind == "hq" else p.cm3_lens_to_top
        yb = (-p.hq_boss_h if kind == "hq" else -p.cm3_boss_h) + 1.4
        front = np.array([[xc, yb, p.axis_z + top], [xc, yb, zs - 2.0], [xc, yb * 0.5, zs - 0.3],
                          [xc, 0.0, zs], [xc, p.upright_t, zs]])
        yc = conn_ys[1 - i]
        rear = bezier(np.array([xc, p.upright_t, zs]), np.array([xc, 40.0, zs + 4]),
                      np.array([conn_x, yc, z_conn + 40]), np.array([conn_x, yc, z_conn + 0.5]))
        out.append(np.vstack([front[:-1], rear]))
    return out


# --- scenes -----------------------------------------------------------------------------------

def add_scene(pl, p: Params, cams: list[str], mount_mesh, cables=True, lens="16mm_C"):
    add(pl, mount_mesh, COLORS["mount"])
    pi = real_pi5(p)
    add(pl, pi if pi is not None else make_pi5(p), COLORS["pi5"])
    add(pl, make_active_cooler(p), COLORS["cooler"])
    cfg = build_config(p, cams, lens=lens)
    for k, wp in cfg["parts"].items():
        if k.startswith("cm3_"):
            xc = p.stations[0 if k.endswith("_L") else 1]
            real = real_cm3(p, xc)
            if real is not None:
                if k.startswith("cm3_pcb"):
                    add(pl, real, (0.16, 0.45, 0.28))
                continue
        add(pl, wp, color_for(k))
    if cables:
        for path in cable_paths(p, cams):
            pl.add_mesh(ribbon(path, 16.0, 11.5), color=CABLE, smooth_shading=True, specular=0.2)


def render_hq_cm3(p: Params, mount_mesh, out: Path) -> None:
    pl = plotter()
    add_scene(pl, p, ["hq", "cm3"], mount_mesh)
    c = make_cm3(p, p.stations[1])
    fr = view_frustum(p, p.stations[1], c["lens_front_y"], c["hfov"], c["vfov"], 95.0)
    add(pl, fr, (1.0, 0.8, 0.2), opacity=0.18)
    pl.camera_position = [(-200, -250, 150), (8, -10, 26), (0, 0, 1)]
    pl.add_text("HQ Camera + 16 mm lens (left) and Camera Module 3 (right) on a Pi 5\n"
                "yellow: the Module 3's field of view, clear of the HQ lens", font_size=12, color="black")
    pl.screenshot(out / "hq_cm3.png")
    pl.close()


def render_rear(p: Params, mount_mesh, out: Path) -> None:
    pl = plotter()
    add_scene(pl, p, ["hq", "cm3"], mount_mesh)
    pl.camera_position = [(170, 250, 175), (0, 40, 24), (0, 0, 1)]
    pl.add_text("From behind: ribbons through the slots, down into the Pi 5's camera connectors", font_size=12,
                color="black")
    pl.screenshot(out / "rear.png")
    pl.close()


def render_two_cm3(p: Params, mount_mesh, out: Path) -> None:
    pl = plotter((1600, 1000))
    add_scene(pl, p, ["cm3", "cm3"], mount_mesh)
    pl.camera_position = [(60, -190, 80), (0, 20, 28), (0, 0, 1)]
    pl.add_text(f"Two Camera Module 3s, {p.station_pitch:.0f} mm apart", font_size=12, color="black")
    pl.screenshot(out / "two_cm3.png")
    pl.close()


def render_mount(p: Params, mount_mesh, out: Path) -> None:
    pl = pv.Plotter(off_screen=True, window_size=(1800, 800), shape=(1, 2))
    pl.set_background("white")
    pl.enable_anti_aliasing("ssaa")
    for i, (pos, title) in enumerate((((-150, -190, 120), "Front: HQ bosses (tall) and Module 3 bosses (short)"),
                                      ((160, 230, 160), "Back: nut pockets, cable slots, Pi 5 bosses, stand nut"))):
        pl.subplot(0, i)
        pl.add_mesh(mount_mesh, color=(0.2, 0.2, 0.22), smooth_shading=False, specular=0.2)
        pl.camera_position = [pos, (0, 45, 18), (0, 0, 1)]
        pl.add_text(title, font_size=11, color="black")
    pl.screenshot(out / "mount.png")
    pl.close()


def render_station(p: Params, mount_mesh, out: Path) -> None:
    """Close-up of one station, bare and with each camera, from the front left."""
    from mount import make_hq_camera
    xc = p.stations[0]
    pl = pv.Plotter(off_screen=True, window_size=(2100, 800), shape=(1, 3))
    pl.set_background("white")
    pl.enable_anti_aliasing("ssaa")
    a = p.hq_pitch / 2
    for i, what in enumerate(("bare", "hq", "cm3")):
        pl.subplot(0, i)
        pl.add_mesh(mount_mesh, color=(0.45, 0.5, 0.56), smooth_shading=False, specular=0.2)
        if what == "bare":
            labels = {
                f"HQ: M2.5 on {p.hq_pitch:.0f} x {p.hq_pitch:.0f}, {p.hq_boss_h} mm": (xc + a, -p.hq_boss_h, p.axis_z + a),
                f"Module 3: M2 on 21 x 12.5, {p.cm3_boss_h:.1f} mm": (xc + p.cm3_hole_du / 2, -p.cm3_boss_h,
                                                                  p.axis_z + p.cm3_hole_v[0]),
                "ribbon slot": (xc, -0.5, p.axis_z + p.slot_v),
            }
            pl.add_point_labels(np.array(list(labels.values()), dtype=float), list(labels.keys()), font_size=16,
                                point_size=10, point_color="red", shape_opacity=0.85, always_visible=True)
            title = "Bare station"
        elif what == "hq":
            hq = make_hq_camera(p, xc)
            for k in ("pcb", "conn", "mount"):
                add(pl, hq[k], color_for(f"hq_{k}"))
            title = "HQ Camera on the tall bosses"
        else:
            real = real_cm3(p, xc)
            if real is not None:
                add(pl, real, (0.16, 0.45, 0.28))
            else:
                c = make_cm3(p, xc)
                for k in ("pcb", "conn", "lens"):
                    add(pl, c[k], (0.16, 0.45, 0.28))
            title = "Module 3 on the short bosses"
        pl.camera_position = [(xc - 70, -120, p.axis_z + 45), (xc, 0, p.axis_z + 2), (0, 0, 1)]
        pl.add_text(title, font_size=12, color="black")
    pl.screenshot(out / "station.png")
    pl.close()


def main() -> None:
    RENDERS.mkdir(parents=True, exist_ok=True)
    p = Params()
    mm = mesh(make_mount(p), tol=0.03)
    render_hq_cm3(p, mm, RENDERS)
    render_rear(p, mm, RENDERS)
    render_two_cm3(p, mm, RENDERS)
    render_mount(p, mm, RENDERS)
    render_station(p, mm, RENDERS)
    print(f"renders written to {RENDERS}")


if __name__ == "__main__":
    main()
