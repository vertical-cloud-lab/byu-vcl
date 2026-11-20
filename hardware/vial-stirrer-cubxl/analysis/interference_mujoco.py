#!/usr/bin/env python3
"""Interference check of the compact stirrer in MuJoCo (PR #269, 2026-11-04).

On 2026-11-03 the compact stirrer's fan spun with the vial holder off and would not turn with it
on. This builds the compact stirrer as BUILD.md stage 6 assembles it, as a MuJoCo model, and checks
it for interference:

  1. Every pair of fixed parts: interference, contact or clearance. The deck keys' 0.05 mm press
     fit is a known interference, so it calibrates the check.
  2. The fan's rotor (hub, blades) with the magnet carrier and magnets, turned through 360 degrees
     on a hinge, with the holder on: the closest approach to every fixed part.
  3. The same with the as-built deviations that could close a gap: no washers, the blades level
     with the frame's face, the carrier off-centre, the Hall sensor pushed in along the groove.
  4. A plan map of the free height between the rotor's swept top (or the fan frame) and the
     holder's underside, from MuJoCo ray casts, so it shows where a sensor and its leads fit.

Where the geometry comes from:
  - printed parts: stl/compact/base_compact.stl, stl/compact/vial_holder_compact.stl,
    stl/magnet_carrier.stl and stl/deck_key.stl, the files that were printed. The base was then
    the one printed on 2026-10-28 and 2026-10-30 (commit b9f57f5). Later on 2026-11-04 the base
    lost its board stop and its cable notch moved to the -X wall; neither is near the rotor, but
    a rerun reads the new base and still lays the cable's cores on the old route under the fan;
  - bought parts (fan, washers, screws, inserts, Hall sensor and leads, junction board, MOSFET,
    vial): onshape/vial_stirrer.fs's numbers (makeFan, makeHall, makeScrew, makeInsert,
    makeDriver), BUILD.md's and wiring_diagram.py's for the compact build.

MuJoCo collides a mesh as its convex hull, so a part with a pocket or a hole would collide as if it
were filled. Every printed part is therefore cut into convex prisms first: the STL is sliced
between the heights of its horizontal faces, each slice's section is triangulated (ear cutting)
and the triangles merged into convex pieces (Hertel-Mehlhorn). Where a part's walls are vertical
this is exact, to the STL's own 0.02 mm tessellation. Where they are not (the cup's 3 degree pocket
and edge rounds, the nub's lead-in chamfer) the slices are at most 0.5 mm thick and take the union
of the sections in them, so they can only add material.

    python analysis/interference_mujoco.py      # writes analysis/interference_mujoco_output.txt
                                                # and img/interference_mujoco.png

Needs mujoco (written against 3.17.0), trimesh, shapely, mapbox_earcut, scipy and matplotlib.
"""

from __future__ import annotations

import math
import pathlib
import re
import sys
import tempfile
import time

import mujoco
import numpy as np
import shapely
import trimesh
from scipy.spatial import ConvexHull, HalfspaceIntersection
from shapely.geometry import MultiPolygon, Point, Polygon

ROOT = pathlib.Path(__file__).resolve().parent.parent
FS = ROOT / "onshape" / "vial_stirrer.fs"
OUT_TXT = ROOT / "analysis" / "interference_mujoco_output.txt"
OUT_PNG = ROOT / "img" / "interference_mujoco.png"


def fs_constants(path: pathlib.Path) -> dict:
    """The top-level `const NAME = expr;` lines of the FeatureScript, evaluated in order
    (as in compact/build_compact.py)."""
    env: dict = {"tan": lambda d: math.tan(math.radians(d)), "sqrt": math.sqrt}
    out: dict = {}
    for m in re.finditer(r"^const\s+([A-Z_0-9]+)\s*=\s*([^;]+);", path.read_text(), re.M):
        expr = m.group(2).replace("* degree", "")
        try:
            out[m.group(1)] = env[m.group(1)] = float(eval(expr, {"__builtins__": {}}, env))
        except Exception:
            pass
    return out


C = fs_constants(FS)
Z_FAN0, Z_FAN1, Z_WALL, Z_RECESS, Z_VIAL = C["Z_FAN0"], C["Z_FAN1"], C["Z_WALL"], C["Z_RECESS"], C["Z_VIAL"]
FP = C["FAN_PITCH"] / 2                       # fan holes, posts, washers and screws at (+-16, +-16)
WASHER_OD, WASHER_ID, WASHER_T = 7.0, 3.2, 0.5   # ISO 7089 M3, as compact/README.md
CBORE_SEAT = Z_WALL + C["FLANGE_T"] - 3.0        # build_compact.py COMPACT["CBORE_SEAT"], 23.0
SCREW_L, SCREW_HEAD_D, SCREW_HEAD_H, SCREW_D = 20.0, 5.5, 3.0, 3.0
KEY_DX = 2 * C["KEY_X"]                          # deck_key.stl is the key at x = -12.5; the other is at +12.5

MARGIN = 2.0          # contacts are reported between geoms closer than this (mm)
TOUCH = 0.005         # |distance| under this is contact: parts resting on each other
NEAR = 1.0            # clearances under this are listed


# ------------------------------------------------------------------------------------------------
# Convex pieces


def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _convex(v, idx):
    n = len(idx)
    for i in range(n):
        o, a, b = v[idx[i - 1]], v[idx[i]], v[idx[(i + 1) % n]]
        e1, e2 = np.subtract(a, o), np.subtract(b, a)
        if _cross(o, a, b) < -1e-9 * (np.hypot(*e1) * np.hypot(*e2) + 1e-30):
            return False
    return True


def convex_pieces(poly) -> list[np.ndarray]:
    """Exact convex decomposition of a polygon with holes: ear-cut triangles, merged across their
    shared edges while the result stays convex (Hertel-Mehlhorn)."""
    if poly.is_empty:
        return []
    polys = list(poly.geoms) if isinstance(poly, MultiPolygon) else [poly]
    out = []
    for p in polys:
        p = p.simplify(1e-5)
        if p.is_empty or p.area < 1e-6:
            continue
        v, f = trimesh.creation.triangulate_polygon(p, engine="earcut")
        v = np.asarray(v, float)
        pieces = {}
        for k, t in enumerate(f):
            t = list(map(int, t))
            if _cross(v[t[0]], v[t[1]], v[t[2]]) < 0:
                t.reverse()
            if abs(_cross(v[t[0]], v[t[1]], v[t[2]])) < 1e-12:
                continue
            pieces[k] = t
        owner = {}
        for k, t in pieces.items():
            for i in range(len(t)):
                owner[(t[i], t[(i + 1) % len(t)])] = k
        changed = True
        while changed:
            changed = False
            for (a, b), k in list(owner.items()):
                if owner.get((a, b)) != k:
                    continue
                j = owner.get((b, a))
                if j is None or j == k:
                    continue
                P, Q = pieces[k], pieces[j]
                ip, iq = P.index(a), Q.index(b)
                Pr = P[ip + 1:] + P[:ip + 1]          # b ... a
                Qr = Q[iq + 1:] + Q[:iq + 1]          # a ... b
                merged = Pr + Qr[1:-1]
                if len(set(merged)) != len(merged) or not _convex(v, merged):
                    continue
                for t in (P, Q):
                    for i in range(len(t)):
                        owner.pop((t[i], t[(i + 1) % len(t)]), None)
                pieces[k] = merged
                del pieces[j]
                for i in range(len(merged)):
                    owner[(merged[i], merged[(i + 1) % len(merged)])] = k
                changed = True
        out += [v[t] for t in pieces.values()]
    return out


def section(mesh: trimesh.Trimesh, z: float):
    sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        return Polygon()
    T = np.eye(4)
    T[2, 3] = -z
    p2, _ = sec.to_2D(to_2D=T)
    return shapely.union_all(list(p2.polygons_full)).buffer(0)


def stl_layers(mesh: trimesh.Trimesh, dz_max: float = 0.5, thin: float = 0.05):
    """(z0, z1, section) slabs whose union contains the mesh: exact where its walls are vertical."""
    z = np.unique(np.round(mesh.vertices[:, 2], 4))
    n = mesh.face_normals
    tz = mesh.vertices[mesh.faces][:, :, 2]
    sl = (np.abs(n[:, 2]) > 1e-4) & (np.abs(n[:, 2]) < 1 - 1e-4)
    lo, hi = tz[sl].min(1), tz[sl].max(1)

    def plain(a, b):
        return b - a >= thin and not np.any((lo < b - 1e-6) & (hi > a + 1e-6))

    layers, i = [], 0
    while i < len(z) - 1:
        if plain(z[i], z[i + 1]):
            layers.append((z[i], z[i + 1], section(mesh, 0.5 * (z[i] + z[i + 1]))))
            i += 1
            continue
        j = i + 1
        while j < len(z) - 1 and z[j + 1] - z[i] <= dz_max and not plain(z[j], z[j + 1]):
            j += 1
        eps = min(1e-4, 0.25 * (z[j] - z[i]))
        samples = sorted({min(max(s, z[i] + eps), z[j] - eps) for s in z[i:j + 1]})
        layers.append((z[i], z[j], shapely.union_all([section(mesh, s) for s in samples]).buffer(0)))
        i = j
    return layers


def prism(v2, z0, z1):
    v2 = np.asarray(v2, float)
    return np.vstack([np.c_[v2, np.full(len(v2), z0)], np.c_[v2, np.full(len(v2), z1)]])


_STL_CACHE: dict = {}


def stl_part(path):
    """A printed part's STL as convex prisms (cached: the variants only move parts)."""
    key = str(path)
    if key not in _STL_CACHE:
        mesh = trimesh.load(key)
        pieces = []
        for z0, z1, sec in stl_layers(mesh):
            for v2 in convex_pieces(sec):
                pieces.append(("mesh", prism(v2, z0, z1)))
        _STL_CACHE[key] = (pieces, mesh)
    return _STL_CACHE[key]


def poly_part(poly, z0, z1):
    return [("mesh", prism(v2, z0, z1)) for v2 in convex_pieces(poly)]


def circle(x, y, r, n=256):
    return Point(x, y).buffer(r, quad_segs=n // 4)


def rrect(w, d, r):
    return shapely.box(-w / 2 + r, -d / 2 + r, w / 2 - r, d / 2 - r).buffer(r, quad_segs=32)


def cyl(x, y, z0, z1, r):
    return ("cyl", (x, y, 0.5 * (z0 + z1)), (r, 0.5 * (z1 - z0)))


def box(x0, y0, z0, x1, y1, z1):
    return ("box", (0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (z0 + z1)), (0.5 * (x1 - x0), 0.5 * (y1 - y0), 0.5 * (z1 - z0)))


# ------------------------------------------------------------------------------------------------
# The parts


def fan_blades(lift=0.0):
    """vial_stirrer.fs makeFan's seven blades: a 1 mm box from r 10 to 18.4, tilted 38 degrees about
    x, trimmed to the frame's faces. `lift` raises them (to test blades level with the frame face)."""
    x0, x1 = C["HUB_D"] / 2 - 1.0, C["FAN_BORE"] / 2 - 0.6
    z0, z1 = Z_FAN0 + 2.8, Z_FAN1 - 0.8
    zc, a = (Z_FAN0 + Z_FAN1) / 2 + 0.6, math.radians(38)
    corners = np.array([[x, y, z] for x in (x0, x1) for y in (-0.5, 0.5) for z in (z0, z1)])
    y, zz = corners[:, 1], corners[:, 2] - zc
    corners = np.c_[corners[:, 0], y * math.cos(a) - zz * math.sin(a), y * math.sin(a) + zz * math.cos(a) + zc + lift]
    hull = ConvexHull(corners)
    hs = np.vstack([hull.equations, [0, 0, -1, Z_FAN0], [0, 0, 1, -Z_FAN1]])
    v = HalfspaceIntersection(hs, corners.mean(0)).intersections
    out = []
    for k in range(7):
        t = 2 * math.pi * k / 7
        R = np.array([[math.cos(t), -math.sin(t), 0], [math.sin(t), math.cos(t), 0], [0, 0, 1]])
        out.append(("mesh", v @ R.T))
    return out


def hall_parts(dx=0.0, dz=0.0):
    """vial_stirrer.fs makeHall: the US1881 (TO-92UA, 4.1 x 3.0 x 1.6 mm) on the recess ceiling at the
    groove's mouth, and its leads, in the groove then down the -X wall. dx moves the body and the
    leads' horizontal run toward the axis (+X) along the groove, dz moves them down."""
    z1 = Z_RECESS - dz
    body = [box(-13.3 + dx, -2.05, z1 - 1.6, -10.3 + dx, 2.05, z1)]
    leads = []
    for k in range(3):
        y = (k - 1) * 1.27
        leads.append(box(-21.9, y - 0.25, z1 - 1.0, -13.3 + dx, y + 0.25, z1 - 0.5))
        leads.append(box(-22.2, y - 0.3, C["FLOOR_T"] + 3.0, -21.6, y + 0.3, z1 - 0.5))
    return body, leads


def build_parts(v: dict):
    """Every part as (name, group, rgba, moving, pieces). v holds the deviations from BUILD.md."""
    hz = v.get("holder_dz", 0.0)                      # holder, Hall sensor and screws move with it
    parts = []

    def add(name, group, rgba, pieces, moving=False, shift=(0, 0, 0)):
        sh = np.asarray(shift, float)
        out = []
        for p in pieces:
            if p[0] == "mesh":
                out.append(("mesh", p[1] + sh))
            else:
                out.append((p[0], tuple(np.add(p[1], sh)), p[2]))
        parts.append((name, group, rgba, moving, out))

    base, _ = stl_part(ROOT / "stl" / "compact" / "base_compact.stl")
    add("base", 4, "0.45 0.47 0.52 1", base)
    k1, _ = stl_part(ROOT / "stl" / "deck_key.stl")
    add("deck key -X", 4, "0.9 0.9 0.9 1", k1)
    add("deck key +X", 4, "0.9 0.9 0.9 1", k1, shift=(KEY_DX, 0, 0))
    inserts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            ring = circle(sx * FP, sy * FP, C["INSERT_OD"] / 2).difference(circle(sx * FP, sy * FP, 1.5))
            inserts += poly_part(ring, Z_FAN0 - C["INSERT_L"], Z_FAN0)
    add("inserts", 4, "0.80 0.62 0.25 1", inserts)

    # fan: frame (rounded square, bore, four holes), motor mount and struts (vial_stirrer.fs makeFan)
    frame = rrect(C["FAN_W"], C["FAN_W"], 3.0).difference(circle(0, 0, C["FAN_BORE"] / 2))
    for sx in (-1, 1):
        for sy in (-1, 1):
            frame = frame.difference(circle(sx * FP, sy * FP, C["FAN_HOLE"] / 2))
    add("fan frame", 3, "0.12 0.12 0.13 1", poly_part(frame, Z_FAN0, Z_FAN1))
    stator = [cyl(0, 0, Z_FAN0, Z_FAN0 + 2.0, 10.5)]
    for k in range(4):
        t = k * math.pi / 2
        pts = np.array([[9.0, -0.9], [C["FAN_BORE"] / 2 + 0.3, -0.9], [C["FAN_BORE"] / 2 + 0.3, 0.9], [9.0, 0.9]])
        R = np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])
        stator.append(("mesh", prism(pts @ R.T, Z_FAN0, Z_FAN0 + 2.0)))
    add("fan stator", 3, "0.12 0.12 0.13 1", stator)

    # washers on the fan's corners, the holder on them
    washers = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            if (sx, sy) in v.get("no_washer_at", ()):
                continue
            ring = circle(sx * FP, sy * FP, WASHER_OD / 2).difference(circle(sx * FP, sy * FP, WASHER_ID / 2))
            washers += poly_part(ring, Z_FAN1, Z_FAN1 + WASHER_T)
    if not v.get("no_washers"):
        add("washers", 1, "0.75 0.75 0.78 1", washers)
    holder, _ = stl_part(ROOT / "stl" / "compact" / "vial_holder_compact.stl")
    add("holder", 1, "0.10 0.58 0.60 1", holder, shift=(0, 0, hz))
    screws = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            s = CBORE_SEAT
            screws += [cyl(sx * FP, sy * FP, s, s + SCREW_HEAD_H, SCREW_HEAD_D / 2),
                       cyl(sx * FP, sy * FP, s - SCREW_L, s, SCREW_D / 2)]
    add("screws", 1, "0.70 0.70 0.72 1", screws, shift=(0, 0, hz))
    body, leads = hall_parts(v.get("hall_dx", 0.0), v.get("hall_dz", 0.0))
    add("Hall sensor", 5, "0.05 0.05 0.05 1", body, shift=(0, 0, hz))
    add("Hall leads", 5, "0.85 0.85 0.88 1", leads, shift=(0, 0, hz))

    # under the fan (BUILD.md stage 5 and compact stage 6): the junction board on its rails against
    # the stop, the tallest parts on it (resistors and diode lie flat, under 3 mm), the cable's cores
    # as a 2 x 2 bundle along its -Y edge, and the MOSFET flat on the floor at +X
    zb = C["FLOOR_T"] + 0.5
    under = [box(-21.4, -10.0, zb, -1.1, 10.0, zb + 1.6), box(-19.0, -6.0, zb + 1.6, -3.0, 6.0, zb + 1.6 + 2.6)]
    add("junction board", 4, "0.10 0.45 0.20 1", under)
    cores = []
    for iy in range(2):
        for iz in range(2):
            y, zc = -9.2 + 0.8 + iy * 1.6, zb + 1.6 + 0.8 + iz * 1.6
            cores.append(("capx", (-11.0, y, zc), (0.8, 9.6)))
    add("cable cores", 4, "0.2 0.2 0.8 1", cores)
    zf = C["FLOOR_T"]
    add("MOSFET", 4, "0.10 0.10 0.10 1", [box(6.0, -5.0, zf, 15.2, 5.0, zf + 4.5), box(15.2, -5.0, zf, 21.6, 5.0, zf + 1.3)])

    # the vial, sitting on the holder's floor (its outside only)
    add("vial", 0, "0.8 0.9 1.0 0.3", [cyl(0, 0, Z_VIAL + hz, Z_VIAL + hz + 22.0, C["VIAL_OD"] / 2)])

    # the rotor: hub, blades, carrier and magnets, on one hinge
    rz = v.get("rotor_dz", 0.0)
    add("fan hub", 2, "0.20 0.20 0.22 1", [cyl(0, 0, Z_FAN0 + 2.0, Z_FAN1, C["HUB_D"] / 2)], moving=True, shift=(0, 0, rz))
    add("fan blades", 2, "0.25 0.25 0.28 1", fan_blades(v.get("blade_lift", 0.0)), moving=True, shift=(0, 0, rz))
    car, _ = stl_part(ROOT / "stl" / "magnet_carrier.stl")
    ex, cz = v.get("carrier_dx", 0.0), v.get("carrier_dz", 0.0)
    add("magnet carrier", 2, "0.96 0.55 0.10 1", car, moving=True, shift=(ex, 0, rz + cz))
    zm = Z_FAN1 + C["CAR_T"] - C["POCKET_T"]
    mags = [cyl(sx * C["MAG_CC"] / 2, 0, zm, zm + C["MAG_T"], C["MAG_D"] / 2) for sx in (-1, 1)]
    add("magnets", 2, "0.85 0.13 0.13 1", mags, moving=True, shift=(ex, 0, rz + cz))
    return parts


# ------------------------------------------------------------------------------------------------
# The MuJoCo model


def mjcf(parts) -> tuple[str, list]:
    assets, world, rotor, labels = [], [], [], []
    for name, group, rgba, moving, pieces in parts:
        for p in pieces:
            gid = len(labels)
            labels.append(name)
            attrs = f'name="g{gid}" group="{group}" rgba="{rgba}" margin="{MARGIN}" contype="1" conaffinity="1"'
            if p[0] == "mesh":
                assets.append(f'<mesh name="m{gid}" vertex="{" ".join(f"{c:.5f}" for c in np.asarray(p[1]).ravel())}"/>')
                g = f'<geom type="mesh" mesh="m{gid}" {attrs}/>'
            elif p[0] == "cyl":
                g = f'<geom type="cylinder" pos="{p[1][0]:.5f} {p[1][1]:.5f} {p[1][2]:.5f}" size="{p[2][0]:.5f} {p[2][1]:.5f}" {attrs}/>'
            elif p[0] == "capx":
                g = (f'<geom type="capsule" pos="{p[1][0]:.5f} {p[1][1]:.5f} {p[1][2]:.5f}" size="{p[2][0]:.5f} {p[2][1]:.5f}" '
                     f'zaxis="1 0 0" {attrs}/>')
            else:
                g = f'<geom type="box" pos="{p[1][0]:.5f} {p[1][1]:.5f} {p[1][2]:.5f}" size="{p[2][0]:.5f} {p[2][1]:.5f} {p[2][2]:.5f}" {attrs}/>'
            if moving:
                rotor.append(g)
            elif name == "fan stator":
                world.append(("stator", g))
            else:
                world.append(("world", g))
    xml = ['<mujoco model="compact vial stirrer, interference check">',
           '<compiler angle="degree" boundmass="1e-6" boundinertia="1e-9"/>',
           '<option gravity="0 0 0" ccd_iterations="200" ccd_tolerance="1e-10"/>',
           '<size memory="400M"/>', "<asset>", *assets, "</asset>", "<worldbody>",
           *[g for k, g in world if k == "world"],
           '<body name="fan_stator">', *[g for k, g in world if k == "stator"], "</body>",
           '<body name="rotor"><joint name="spin" type="hinge" axis="0 0 1" pos="0 0 0"/>', *rotor, "</body>",
           "</worldbody>",
           # the hub turns on the stator's bearing: the fan's own clearance, not ours to check
           '<contact><exclude body1="rotor" body2="fan_stator"/></contact>', "</mujoco>"]
    return "\n".join(xml), labels


def compile_model(parts):
    xml, labels = mjcf(parts)
    m = mujoco.MjModel.from_xml_string(xml)
    # MuJoCo numbers geoms body by body, so map each back to its part by name
    by_id = [labels[int(m.geom(i).name[1:])] for i in range(m.ngeom)]
    return m, mujoco.MjData(m), by_id, xml


def world_aabb(m, d):
    c = d.geom_xpos + np.einsum("nij,nj->ni", d.geom_xmat.reshape(-1, 3, 3), m.geom_aabb[:, :3])
    h = np.einsum("nij,nj->ni", np.abs(d.geom_xmat.reshape(-1, 3, 3)), m.geom_aabb[:, 3:])
    return c - h, c + h


def pair_min(m, d, ga, gb, distmax=NEAR):
    """Smallest signed distance between two sets of geoms (mj_geomDistance on AABB-near pairs)."""
    lo, hi = world_aabb(m, d)
    ga, gb = np.asarray(ga), np.asarray(gb)
    best, where = distmax, None
    ft = np.zeros(6)
    for s in range(0, len(ga), 256):
        g = ga[s:s + 256]
        near = np.all((lo[g][:, None, :] <= hi[gb][None, :, :] + distmax) & (lo[gb][None, :, :] <= hi[g][:, None, :] + distmax), axis=2)
        for i, j in zip(*np.nonzero(near)):
            dist = mujoco.mj_geomDistance(m, d, int(g[i]), int(gb[j]), distmax, ft)
            if dist < best:
                best, where = dist, ft.copy()
    return best, where


def sweep(m, d, labels, step_deg=1.0):
    """Turn the rotor through 360 degrees; the closest approach of each moving part to each fixed one."""
    best = {}
    for t in np.arange(0.0, 360.0, step_deg):
        d.qpos[0] = math.radians(t)
        mujoco.mj_fwdPosition(m, d)
        for c in d.contact[:d.ncon]:
            a, b = labels[c.geom1], labels[c.geom2]
            if m.geom_bodyid[c.geom1] != m.body("rotor").id:
                a, b = b, a
            key = (a, b)
            if key not in best or c.dist < best[key][0]:
                best[key] = (float(c.dist), float(t), c.pos.copy())
    d.qpos[0] = 0.0
    mujoco.mj_fwdPosition(m, d)
    return best


def classify(dist):
    if dist < -TOUCH:
        return "INTERFERENCE"
    if dist <= TOUCH:
        return "contact"
    return "clear"


# ------------------------------------------------------------------------------------------------


INTENDED = {
    ("base", "deck key -X"): "press fit, 0.05 mm a side (BUILD.md stage 2)",
    ("base", "deck key +X"): "press fit, 0.05 mm a side (BUILD.md stage 2)",
    ("base", "inserts"): "heat-set: Ø4.6 insert melted into a Ø4.0 hole",
    ("holder", "vial"): "the cup's four fingers flex out round the vial (spring fit)",
    ("inserts", "screws"): "the screw's thread in the insert",
    ("fan frame", "fan stator"): "one moulding: the model runs the struts 0.3 mm into the frame",
}
RESTING = {("deck key -X", "base"), ("base", "fan frame"), ("fan frame", "washers"), ("holder", "washers"),
           ("holder", "Hall sensor"), ("holder", "screws"), ("Hall leads", "Hall sensor"), ("base", "junction board"),
           ("cable cores", "junction board"), ("base", "MOSFET"), ("base", "fan stator"), ("fan frame", "fan stator"),
           ("holder", "vial"), ("base", "deck key +X"), ("inserts", "fan frame")}

VARIANTS = [
    ("as BUILD.md has it (0.5 mm washers, sensor on the recess ceiling)", {}),
    ("no washers: the holder sits on the fan, 0.5 mm lower", {"holder_dz": -WASHER_T}),
    ("blades level with the frame's face (the model has them 1.3 mm below it)", {"blade_lift": "level"}),
    ("both: blades level with the face and no washers", {"blade_lift": "level", "holder_dz": -WASHER_T}),
    ("carrier glued 0.3 mm off-centre, toward the sensor at 0 deg", {"carrier_dx": -0.3}),
    ("carrier standing 1.2 mm higher (a proud hub, a thick glue line)", {"carrier_dz": 1.2}),
    ("fan's middle pushed up 1.2 mm (by something under it), rotor with it", {"rotor_dz": 1.2}),
    ("sensor slid 1.0 mm in along the groove", {"hall_dx": 1.0}),
    ("sensor resting on the fan's top face beside the carrier, not on the ceiling", {"hall_dz": Z_RECESS - (Z_FAN1 + 1.6)}),
]


def main():
    t0 = time.time()
    lines = []

    def say(s=""):
        lines.append(s)
        print(s, flush=True)

    say("Interference check of the compact stirrer in MuJoCo " + mujoco.__version__)
    say("(hardware/vial-stirrer-cubxl/analysis/interference_mujoco.py; all lengths mm, z = 0 is the deck's top face)")
    say("")

    # the blades' highest point in the model, for the 'level with the face' variants
    top = max(p[1][:, 2].max() for p in fan_blades())
    level = Z_FAN1 - top

    results = []
    for vi, (vname, v) in enumerate(VARIANTS):
        v = dict(v)
        if v.get("blade_lift") == "level":
            v["blade_lift"] = level
        parts = build_parts(v)
        m, d, labels, xml = compile_model(parts)
        mujoco.mj_fwdPosition(m, d)
        names = list(dict.fromkeys(labels))
        gid = {n: [i for i, lab in enumerate(labels) if lab == n] for n in names}
        moving = [p[0] for p in parts if p[3]]
        if vi == 0:
            say(f"Model: {m.ngeom} geoms ({m.nmesh} convex meshes) in {len(names)} parts; the rotor turns on one hinge.")
            for p in parts:
                say(f"   {p[0]:16s} {len(p[4]):5d} {'piece ' if len(p[4]) == 1 else 'pieces'}{'  (moving)' if p[3] else ''}")
            say(f"   fan blades' top edge in vial_stirrer.fs's fan: z {top:.2f}, {level:.2f} below the frame's face (z {Z_FAN1:.2f})")
            pathlib.Path(tempfile.gettempdir(), "stirrer_interference.xml").write_text(xml)

            # 1. fixed parts against each other
            say("")
            say("1. Fixed parts against each other, holder on (smallest signed distance; negative = overlap)")
            fixed = [n for n in names if n not in moving]
            rows = []
            for i, a in enumerate(fixed):
                for b in fixed[i + 1:]:
                    dist, ft = pair_min(m, d, gid[a], gid[b])
                    if dist < NEAR:
                        rows.append((dist, a, b, ft))
            for dist, a, b, ft in sorted(rows, key=lambda r: r[0]):
                note = INTENDED.get((a, b)) or INTENDED.get((b, a)) or ""
                kind = classify(dist)
                if kind == "INTERFERENCE" and note:
                    kind = "interference, intended"
                elif kind == "contact" and ((a, b) in RESTING or (b, a) in RESTING):
                    kind = "contact (rests on / glued to)"
                at = "" if ft is None else f"  at ({ft[0]:.1f}, {ft[1]:.1f}, {ft[2]:.2f})"
                say(f"   {a:16s} / {b:16s} {dist:+8.3f}  {kind}{at}{'  -- ' + note if note else ''}")
            say("   (pairs not listed are more than 1 mm apart)")
            for key in ("deck key -X", "deck key +X"):
                dist, _ = pair_min(m, d, gid["base"], gid[key])
                say(f"   calibration: {key} nub in its pocket overlaps by {-dist:.3f} mm; the model's press fit is {0.05:.3f}")

        # 2./3. the rotor turned through 360 degrees
        best = sweep(m, d, labels)
        results.append((vname, best))
        say("")
        say(f"{'2' if vi == 0 else '3'}.{vi} Rotor turned through 360 deg in 1 deg steps: {vname}")
        rows = sorted(best.items(), key=lambda kv: kv[1][0])
        shown = 0
        for (a, b), (dist, t, pos) in rows:
            if dist >= NEAR and shown >= 6:
                continue
            own = "  (the fan's own blade-tip clearance, as modelled)" if b == "fan frame" else ""
            say(f"   {a:15s} -> {b:15s} {dist:+8.3f}  {classify(dist):12s} closest at {t:5.1f} deg, "
                f"({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.2f}){own}")
            shown += 1
        far = sorted({b for b in names if b not in moving} - {b for (_, b) in best} - {"fan stator"})
        say(f"   more than {MARGIN:.0f} mm from every moving part: {', '.join(far)}"
            "  (the fan's stator is excluded: the hub turns on its bearing)")

        if vi == 0:
            free_map = free_height(m, d, labels)
    say("")
    say(f"({time.time() - t0:.0f} s)")
    OUT_TXT.write_text("\n".join(lines) + "\n")
    figure(results, free_map, level)


def free_height(m, d, labels, step=0.25):
    """Plan map of the room between the rotor's swept top (or any fixed part below z 20) and the
    holder's underside, from MuJoCo ray casts: up from z 19.4 hitting only the holder, Hall sensor and
    washers (groups 1 and 5), and down from z 30 hitting only the rotor (group 2) at 48 angles, or the
    fan frame, base and what lies under the fan (groups 3 and 4)."""
    xs = np.arange(-23.0, 21.01, step)
    ys = np.arange(-21.0, 21.01, step)
    X, Y = np.meshgrid(xs, ys)
    pts = np.c_[X.ravel(), Y.ravel()] + [0.00137, 0.00173]    # off the convex pieces' shared edges
    n = len(pts)
    geomid = np.zeros(n, np.int32)

    def cast(z0, direction, groups):
        gg = np.zeros(6, np.uint8)
        gg[list(groups)] = 1
        vec = np.array([0.0, 0.0, direction])
        out = np.empty(n)
        for k in range(n):
            out[k] = mujoco.mj_ray(m, d, np.array([pts[k, 0], pts[k, 1], z0]), vec, gg, 1, -1, geomid[k:k + 1])
        return out

    up = cast(Z_FAN1 - 0.1, 1.0, (1, 5))
    ceiling = np.where(up >= 0, Z_FAN1 - 0.1 + up, np.nan)
    floor = np.full(n, -np.inf)
    fixed = cast(30.0, -1.0, (3, 4))          # fan frame, base, and what lies under the fan
    floor = np.maximum(floor, np.where(fixed >= 0, 30.0 - fixed, -np.inf))
    for t in np.arange(0.0, 180.0, 3.75):        # the rotor repeats every 180 deg (magnets) and 51.4 deg (blades)
        d.qpos[0] = math.radians(t)
        mujoco.mj_fwdPosition(m, d)
        r = cast(30.0, -1.0, (2,))
        floor = np.maximum(floor, np.where(r >= 0, 30.0 - r, -np.inf))
    d.qpos[0] = 0.0
    mujoco.mj_fwdPosition(m, d)
    floor = np.where(np.isfinite(floor), floor, np.nan)
    gap = ceiling - floor
    for sx in (-1, 1):
        for sy in (-1, 1):                     # the screws and washers themselves
            gap[np.hypot(pts[:, 0] - sx * FP, pts[:, 1] - sy * FP) < WASHER_OD / 2] = np.nan
    return xs, ys, gap.reshape(X.shape), ceiling.reshape(X.shape), floor.reshape(X.shape)


def figure(results, free_map, level):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle

    xs, ys, gap, ceil, floor = free_map
    fig, ax = plt.subplots(1, 2, figsize=(15, 6.6), gridspec_kw={"width_ratios": [1.05, 1]})
    a = ax[0]
    g = np.where(np.isnan(gap), np.nan, np.clip(gap, 0, 4.5))
    im = a.imshow(g, origin="lower", extent=(xs[0], xs[-1], ys[0], ys[-1]), cmap="viridis", vmin=0, vmax=4.5)
    cb = fig.colorbar(im, ax=a, fraction=0.04, pad=0.02)
    cb.set_label("free height under the holder, mm")
    for r, ls in ((C["RECESS_D"] / 2, "--"), (C["CAR_D"] / 2, "-"), (C["FAN_BORE"] / 2, ":")):
        a.add_patch(Circle((0, 0), r, fill=False, ec="white", ls=ls, lw=1))
    a.add_patch(Rectangle((-13.3, -2.05), 3.0, 4.1, fill=False, ec="red", lw=1.8))
    a.add_patch(Rectangle((-22.8, -2.6), 22.8 - C["RECESS_D"] / 2 + 0.5, 5.2, fill=False, ec="white", lw=0.8, ls="--"))
    a.annotate("Hall sensor as\nBUILD.md has it", (-11.8, 2.1), (-22.5, 7.0), color="red", fontsize=9,
               arrowprops=dict(arrowstyle="->", color="red"), bbox=dict(fc="white", ec="none", alpha=0.8))
    a.text(0, 0, "1.1 over\nthe carrier", ha="center", va="center", color="white", fontsize=9)
    a.text(-18.0, -4.0, "groove", color="white", fontsize=8.5, ha="center")
    a.text(-21.6, -11.5, "fan / wall\ngap", color="white", fontsize=7.5, ha="center", rotation=90)
    a.text(0, 19.6, "0.5: the washers' gap over the frame", color="white", fontsize=8.5, ha="center", va="center")
    a.text(0, -16.4, f"over the blades: 1.8, the washers' 0.5 + the\nblades' {level:.1f} below the face (not measured)", color="black", fontsize=8.5, ha="center",
           bbox=dict(fc="white", ec="none", alpha=0.7))
    a.text(0, 11.4, "recess, 4.3", color="black", fontsize=8.5, ha="center")
    a.set_title("Room between the rotor's swept top and the holder's underside\n"
                "holder on, as BUILD.md assembles it (MuJoCo ray casts, 0.25 mm grid)", fontsize=10)
    a.set_xlim(xs[0], xs[-1])
    a.set_ylim(ys[0], ys[-1])
    a.set_xlabel("x, mm (-X wall, groove and sensor on the left)")
    a.set_ylabel("y, mm (cable notch at -Y)")
    a.set_aspect("equal")

    b = ax[1]
    b.axis("off")
    rows = []
    for vname, best in results:
        worst = [kv for kv in sorted(best.items(), key=lambda kv: kv[1][0]) if kv[0][1] != "fan frame"][:2]
        cells = [f"{w[0][0]} -> {w[0][1]}: {w[1][0]:+.2f}" for w in worst]
        rows.append((vname, cells))
    y = 0.98
    b.text(0, y, "Closest approach of the turning rotor to a fixed part, holder on\n(mm, MuJoCo, 1 deg steps; negative = overlap)", fontsize=10.5, weight="bold", va="top")
    y -= 0.03
    y -= 0.07
    for vname, cells in rows:
        b.text(0, y, vname, fontsize=9, va="top", wrap=True)
        y -= 0.04
        for c in cells[:1]:
            col = "#b00020" if "-" in c.split(":")[1] and float(c.split(":")[1]) < -TOUCH else ("#a06000" if abs(float(c.split(":")[1])) <= TOUCH else "#205020")
            b.text(0.03, y, c, fontsize=9, va="top", color=col, family="monospace")
            y -= 0.04
        y -= 0.012
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=110)
    print("wrote", OUT_PNG)


if __name__ == "__main__":
    sys.exit(main())
