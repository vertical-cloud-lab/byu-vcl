"""Part models for the spot D enclosure (#229), built from the makers' published dimensions.

Every part is a trimesh in metres, in its own local frame. Nothing here is a vendor CAD file:
each shape is rebuilt from the few numbers the maker publishes, which are listed next to it.
"""

from dataclasses import dataclass

import numpy as np
import trimesh
from shapely.geometry import Polygon
from trimesh.creation import box, cylinder, extrude_polygon, icosphere

IN = 0.0254


@dataclass
class Part:
    name: str
    mesh: trimesh.Trimesh
    color: str
    source: str


def _union(*meshes):
    return trimesh.boolean.union(meshes, engine="manifold")


def _minus(a, *cutters):
    return trimesh.boolean.difference([a, *cutters], engine="manifold")


def _cyl(r, z0, z1, sections=48):
    """Cylinder on the z axis from z0 to z1."""
    c = cylinder(radius=r, height=z1 - z0, sections=sections)
    c.apply_translation((0, 0, (z0 + z1) / 2))
    return c


def _along(axis):
    """Rotation taking +z onto a coordinate axis (0, 1 or 2)."""
    return {0: trimesh.transformations.rotation_matrix(np.pi / 2, (0, 1, 0)),
            1: trimesh.transformations.rotation_matrix(-np.pi / 2, (1, 0, 0)),
            2: np.eye(4)}[axis]


# ------------------------------------------------------------------ pipe
# Charlotte Pipe 3/4 in Sch 40 PVC, ASTM D1785: OD 1.050 in, minimum wall 0.113 in.
PIPE_OD = 1.050 * IN
PIPE_WALL = 0.113 * IN


def pvc_pipe(length):
    """A cut length of pipe on the z axis, from z = 0 to z = length."""
    outer = _cyl(PIPE_OD / 2, 0, length, 40)
    inner = _cyl(PIPE_OD / 2 - PIPE_WALL, -0.001, length + 0.001, 40)
    return Part(f"pipe-{length * 1000:.0f}mm", _minus(outer, inner), "#f1f1ee",
                "Charlotte 3/4 in Sch 40 PVC (ASTM D1785): 1.050 in OD, 0.113 in wall")


# ------------------------------------------------------------------ 3-way elbow
# FORMUFIT F0343WE, technical spec sheet TSD F0343WE (2022-01-27):
# 2.250 in overall on each axis, 1.050 in socket ID, 1.001 in insertion depth, 1.293 in OD.
ELBOW_OVERALL = 2.250 * IN
ELBOW_OD = 1.293 * IN
ELBOW_SOCKET_ID = 1.050 * IN
ELBOW_INSERTION = 1.001 * IN
# From the corner (where the three pipe axes meet) to the socket mouth, and to the socket bottom.
ELBOW_MOUTH = ELBOW_OVERALL - ELBOW_OD / 2          # 1.604 in
ELBOW_STOP = ELBOW_MOUTH - ELBOW_INSERTION           # 0.603 in = 15.3 mm: the cut allowance per pipe end


def formufit_elbow():
    """Legs along +x, +y and +z from the corner; the outer corner is a sphere of the fitting OD."""
    body = [icosphere(subdivisions=3, radius=ELBOW_OD / 2)]
    bores = []
    for ax in range(3):
        R = _along(ax)
        body.append(_cyl(ELBOW_OD / 2, 0, ELBOW_MOUTH).apply_transform(R))
        bores.append(_cyl(ELBOW_SOCKET_ID / 2, ELBOW_STOP, ELBOW_MOUTH + 0.001).apply_transform(R))
    return Part("elbow-formufit-f0343we", _minus(_union(*body), *bores), "#fbfbf9",
                "FORMUFIT F0343WE spec sheet: 2.250 in overall, 1.293 in OD, 1.001 in insertion")


# ------------------------------------------------------------------ snap clamp
# Johnny's Selected Seeds #7036, snap clamp for 3/4 in PVC or 1 in EMT: ABS, 4 in long,
# 0.90 in ID relaxed. Fitted over pipe and cloth it opens to the pipe OD; the wall and the
# 120 degree gap are estimated from photos.
CLAMP_LEN = 4.0 * IN
CLAMP_WALL = 0.0025
CLOTH_T = 0.0006  # 8 oz canvas


def snap_clamp():
    """C-section on the z axis, centred at z = 0, with its gap facing +x."""
    r0 = PIPE_OD / 2 + CLOTH_T
    r1 = r0 + CLAMP_WALL
    t = np.radians(np.linspace(60, 300, 49))
    ring = np.vstack([np.c_[r1 * np.cos(t), r1 * np.sin(t)], np.c_[r0 * np.cos(t[::-1]), r0 * np.sin(t[::-1])]])
    m = extrude_polygon(Polygon(ring), CLAMP_LEN)
    m.apply_translation((0, 0, -CLAMP_LEN / 2))
    return Part("snap-clamp-3-4in-pvc", m, "#dfe3e6",
                "Johnny's #7036: ABS, 4 in long, 0.90 in ID, fits 3/4 in PVC")


# ------------------------------------------------------------------ M5 x 25 socket cap
# ISO 4762 M5: head 8.5 mm dia x 5 mm, 4 mm hex socket 2.5 mm deep. 25 mm under the head.
def m5_socket_cap(length=0.025):
    """Head at z <= 0, shank up the +z axis (installed pointing up through the plywood)."""
    head = _cyl(0.00425, -0.005, 0, 36)
    shank = _cyl(0.0025, -0.0001, length, 24)
    hexs = cylinder(radius=0.004 / np.sqrt(3), height=0.005, sections=6)
    hexs.apply_translation((0, 0, -0.005))
    return Part("m5x25-socket-cap", _minus(_union(head, shank), hexs), "#b9bdc2",
                "ISO 4762 M5 x 25: 8.5 mm head, 5 mm tall, 4 mm hex socket")


# ------------------------------------------------------------------ plywood base
# Columbia Forest Products PureBond birch project panel, 3/4 in nominal: 24 x 48 in, 0.703 in actual.
PLY = dict(w=24 * IN, l=48 * IN, t=0.703 * IN)
HOLE_SQ = 0.070          # PiPER base: 4 x M5 on a 70 mm square (user manual)
HOLE_D, CBORE_D, CBORE_H = 0.0055, 0.010, 0.006


def hole_xy():
    h = HOLE_SQ / 2
    return [(sx * h, sy * h) for sx in (-1, 1) for sy in (-1, 1)]


def plywood_base():
    """Long side on y, top face at z = 0, centred on the arm; counterbores open downwards."""
    t = PLY["t"]
    slab = box((PLY["w"], PLY["l"], t))
    slab.apply_translation((0, 0, -t / 2))
    cuts = []
    for x, y in hole_xy():
        cuts.append(_cyl(HOLE_D / 2, -t - 0.001, 0.001, 24).apply_translation((x, y, 0)))
        cuts.append(_cyl(CBORE_D / 2, -t - 0.001, -t + CBORE_H, 32).apply_translation((x, y, 0)))
    return Part("plywood-base-24x48in", _minus(slab, *cuts), "#e3d2ad",
                "PureBond birch 3/4 in project panel: 24 x 48 in, 0.703 in actual")


# ------------------------------------------------------------------ canvas
# Everbilt 8 oz canvas drop cloth, sold as 9 x 12 ft; the finished size is 8 ft 9 in x 11 ft 9 in.
CLOTH_SHEET = (105 * IN, 141 * IN)


def canvas_panel(w, h, sag=0.0):
    """A w x h sheet in the x-y plane, centred at the origin; `sag` dips the middle (m)."""
    nx, ny = 24, 24
    x, y = np.meshgrid(np.linspace(-w / 2, w / 2, nx), np.linspace(-h / 2, h / 2, ny), indexing="ij")
    z = -sag * np.cos(np.pi * x / w) * np.cos(np.pi * y / h)
    v = np.c_[x.ravel(), y.ravel(), z.ravel()]
    f = []
    for i in range(nx - 1):
        for j in range(ny - 1):
            a, b, c, d = i * ny + j, (i + 1) * ny + j, (i + 1) * ny + j + 1, i * ny + j + 1
            f += [(a, b, c), (a, c, d)]
    top = trimesh.Trimesh(v, f)
    under = trimesh.Trimesh(v - (0, 0, CLOTH_T), np.array(f)[:, ::-1])
    return Part("canvas", trimesh.util.concatenate([top, under]), "#e8dfcb",
                "Everbilt 8 oz canvas drop cloth, 8 ft 9 in x 11 ft 9 in finished")
