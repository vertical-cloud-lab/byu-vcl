"""Small things the workflow handles, and the robot's mobile base. PyVista primitives, millimetres, z up.

* The vial is the multi-doser's own: a 20 mL vial, 28 mm across and 61 mm tall (powder-doser
  ``cad/chain-carousel-v2/params.py``), with a powder fill and a liquid fill that the animation sets.
* The vial rack is a printed block like the CubXL's six-vial rack (``lab_models/equipment.py``), sized for 28 mm vials.
* The mobile base is a **MiR250** (Mobile Industrial Robots, the AMR sold with UR arms): 800 x 580 x 300 mm
  (MiR250 data sheet), with a top cabinet that holds the UR control box (e-Series control box 460 x 449 x 254 mm,
  UR data sheet), so the arm's base sits at ``AMR_TOP``. The cabinet's height is a layout choice: it puts the
  arm's base 80 mm under the opening's counter, so the arm reaches over the counter and down onto the tray.
"""
from __future__ import annotations

import numpy as np
import pyvista as pv

VIAL_R, VIAL_H = 14.0, 61.0                  # 20 mL vial (powder-doser chain-carousel-v2 params: 28 x 61 mm)
VIAL_WALL, VIAL_FLOOR = 1.2, 2.5
GLASS = (0.62, 0.78, 0.90)
POWDER = (0.33, 0.33, 0.36)                  # a grey metal powder (Al 4047, Si: the alloy lab's powders)
LIQUID = (0.25, 0.50, 0.85)
RACK_C = (0.94, 0.94, 0.92)

MIR = dict(L=800.0, W=580.0, H=300.0)        # MiR250: 800 x 580 x 300 mm
CAB_H = 480.0                                # top cabinet with the UR control box (layout choice, see above)
AMR_TOP = MIR["H"] + CAB_H + 20.0            # arm base height above the floor (20 mm mounting plate)


def _cyl(r, h, z0=0.0, x=0.0, y=0.0, res=40):
    return pv.Cylinder(center=(x, y, z0 + h / 2), direction=(0, 0, 1), radius=r, height=h, resolution=res).triangulate()


def vial_glass() -> pv.PolyData:
    """Open 20 mL vial, base centre at the origin: a thin wall and floor, the neck's thread band."""
    outer = _cyl(VIAL_R, VIAL_H)
    neck = pv.Cylinder(center=(0, 0, VIAL_H - 5), direction=(0, 0, 1), radius=VIAL_R + 0.6, height=8,
                       resolution=40).triangulate()
    return outer.merge(neck)


def fill(level_mm: float, r: float = VIAL_R - VIAL_WALL) -> pv.PolyData:
    """A fill of unit height (the animation scales z), from the vial's floor."""
    return _cyl(r, 1.0, 0.0, res=32)


def vial_rack(n: int = 6, pitch: float = 34.0) -> tuple[pv.PolyData, list[tuple[float, float, float]]]:
    """A printed rack: n holes in a row along x, 32 mm deep. Returns the mesh and the vial seats (base centres)."""
    w = n * pitch + 16
    block = pv.Box(bounds=(-w / 2, w / 2, -26, 26, 0, 40)).triangulate()
    seats = [(-w / 2 + 8 + pitch * (i + 0.5), 0.0, 8.0) for i in range(n)]
    return block, seats


def mir250() -> dict[str, tuple[pv.PolyData, tuple]]:
    """MiR250 body, its status-light band, the top cabinet and the arm's mounting plate; origin on the floor at the
    centre of the footprint, long side along x, the arm mounted over the front (-y) half."""
    L, W, H = MIR["L"], MIR["W"], MIR["H"]
    body = pv.Box(bounds=(-L / 2, L / 2, -W / 2, W / 2, 30, H - 20)).triangulate()
    cover = pv.Box(bounds=(-L / 2 + 10, L / 2 - 10, -W / 2 + 10, W / 2 - 10, H - 20, H)).triangulate()
    band = pv.Box(bounds=(-L / 2 - 2, L / 2 + 2, -W / 2 - 2, W / 2 + 2, 60, 78)).triangulate()
    skirt = pv.Box(bounds=(-L / 2 + 20, L / 2 - 20, -W / 2 + 20, W / 2 - 20, 0, 30)).triangulate()
    cab = pv.Box(bounds=(-L / 2 + 40, L / 2 - 40, -W / 2 + 30, W / 2 - 30, H, H + CAB_H)).triangulate()
    plate = pv.Box(bounds=(-170, 170, -W / 2 + 30, W / 2 - 30, H + CAB_H, AMR_TOP)).triangulate()
    door = pv.Box(bounds=(-L / 2 + 70, L / 2 - 70, -W / 2 + 28, -W / 2 + 30, H + 40, H + CAB_H - 40)).triangulate()
    estop = pv.Cylinder(center=(L / 2 - 90, -W / 2 + 60, AMR_TOP + 15), direction=(0, 0, 1), radius=20,
                        height=30).triangulate()
    return {
        "amr body": (body.merge(skirt), (0.22, 0.23, 0.25)),
        "amr cover": (cover, (0.80, 0.81, 0.83)),
        "amr light band": (band, (0.55, 0.85, 1.00)),
        "amr cabinet": (cab.merge(plate), (0.86, 0.87, 0.88)),
        "amr cabinet door": (door, (0.70, 0.72, 0.75)),
        "amr e-stop": (estop, (0.85, 0.12, 0.10)),
    }


HOLDER_H = 260.0                             # the vial holder's post on the cabinet top (layout choice)


def buffer_holder() -> tuple[pv.PolyData, tuple[float, float, float]]:
    """A one-vial holder on a post on the cabinet top, beside the arm: where the vial waits while the VLM swaps
    trays. The post keeps the arm's wrist well clear of the cabinet when it reaches down there."""
    post = pv.Cylinder(center=(0, 0, HOLDER_H / 2), direction=(0, 0, 1), radius=16, height=HOLDER_H).triangulate()
    foot = pv.Box(bounds=(-45, 45, -45, 45, 0, 8)).triangulate()
    cup = pv.Box(bounds=(-30, 30, -30, 30, HOLDER_H, HOLDER_H + 36)).triangulate()
    return post.merge(foot).merge(cup), (0.0, 0.0, HOLDER_H + 6.0)


def tcp_frame(p, approach=(0, 0, -1), spin_deg: float = 0.0) -> np.ndarray:
    """A 4x4 tool pose at point p with the tool's z along `approach` (unit vector) and its x picked by `spin_deg`."""
    z = np.asarray(approach, float)
    z /= np.linalg.norm(z)
    ref = np.array([1.0, 0.0, 0.0]) if abs(z[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    x = ref - z * (ref @ z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    a = np.radians(spin_deg)
    x, y = x * np.cos(a) + y * np.sin(a), -x * np.sin(a) + y * np.cos(a)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, p
    return M
