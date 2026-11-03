"""Scaling up: the same Kardex Shuttle XP 500, 15.15 m tall (just under 50 ft), eight of them in two rows facing an
aisle, served by a UR10e on a floor rail.

    xvfb-run -a python3 animate.py scale       # -> out/vlm_scale.gif, out/mp4/vlm_scale.mp4

Kardex builds the Shuttle up to 30 m tall (kardex.com, Kardex Shuttle), with heights in 100 mm steps, so 15 150 mm is
the tallest under 50 ft (15 240 mm). The module's footprint, trays, opening and speeds are the ones in ``vlm.py``.
Every tray holds one of the five instrument loads of the main animation (``animate.LOADS``: three OT-2s, three
CubXLs, three H2Ds, three A2Ls or three A1 minis), its slot sized to its equipment as in ``vlm.SLOTS``. The meshes are
the main scene's, decimated so a thousand instruments render; the rest of the tall unit (cladding, opening, trays,
extractor) is drawn here as boxes from ``vlm.py``'s figures. Layout choices, not from a source: the two rows, the
1100 mm aisle between the covers, the rail down its middle and the arm on a 800 mm carriage riser.
"""
from __future__ import annotations

import math

import numpy as np
import pyvista as pv

import vlm as V
from scene import T, R

H_TALL = 15150.0                 # Shuttle heights step 100 mm; the tallest under 50 ft (15 240 mm). Kardex: up to 30 m
N_ROW = 4                        # units per row; two rows
AISLE = 1100.0                   # between the two rows' tray covers (the rail runs down the middle)
PITCH_X = V.UNIT_W + 2 * V.SKIN + 150.0
LIP = 50.0                       # the blue cover's lip in front of the front panel (vlm.opening)
Y_UNIT = AISLE / 2 + LIP + V.SKIN + V.UNIT_D / 2      # unit centre, from the aisle's centre line
RAIL_Z = 800.0                   # the arm's base on its carriage, as on the MiR250
TYPES = ("A", "D", "C", "E", "F", "A", "E", "D", "C", "F")   # the instrument loads, in the order they stack
KIND_H = {"A": 662.0, "C": 488.0, "D": 626.0, "E": 505.0, "F": 482.5}  # tallest item on each (lab.py's bboxes)
MAX_TRIS = 1500                  # per mesh, after decimation
GREY = (0.80, 0.81, 0.80)


def unit_xform(row: int, i: int) -> np.ndarray:
    """Unit (row, i) in the world: row 1 north of the aisle facing -y, row 0 south of it, turned to face +y."""
    x = (i - (N_ROW - 1) / 2) * PITCH_X
    if row == 1:
        return T((x, Y_UNIT, 0.0))
    return T((x, -Y_UNIT, 0.0)) @ R((0, 0, 1), 180.0)


def slots(H: float = H_TALL) -> list[tuple[float, float, str]]:
    """[(y, z, kind)] of every tray in a unit of height H, in its own frame (vlm.py's): both columns filled from the
    bottom, each slot its load's height plus about 50 mm on the 25 mm pitch, the front column with the opening's gap."""
    top = H - 260.0 - 10.0
    out = []
    k = 0
    zones = {V.Y_REAR: [(300.0, top)], V.Y_FRONT: [(300.0, V.Z_SILL - 40.0), (V.Z_OPEN_TOP + 120.0, top)]}
    for y, zs in zones.items():
        for z0, z1 in zs:
            z = z0
            while True:
                kind = TYPES[k % len(TYPES)]
                h = KIND_H[kind]
                if z + V.T_FLOOR + h > z1:
                    if z1 - z < 600:          # nothing fits: the next zone
                        break
                    kind = "F"                # the shortest load, if it fits
                    h = KIND_H[kind]
                    if z + V.T_FLOOR + h > z1:
                        break
                out.append((y, z, kind))
                k += 1
                z += math.ceil((h + 50.0) / V.PITCH) * V.PITCH
    return out


def _decimate(m: pv.PolyData) -> pv.PolyData:
    if m.n_cells <= MAX_TRIS:
        return m
    m = m.triangulate()
    try:
        d = m.decimate(1.0 - MAX_TRIS / m.n_cells)
        return d if d.n_cells else m
    except Exception:
        return m


def tray_templates(data: dict, loads: dict) -> dict:
    """{kind: {(colour, opacity): mesh}}: a tray pan with its three instruments, in the tray's frame (centre of the
    floor's underside), decimated and merged by material."""
    eq = data["equipment"]
    dec = {}
    for key, (entries, _) in eq.items():
        dec[key] = {n: (_decimate(e["mesh"]), e["color"], e["opacity"]) for n, e in entries.items()}
    w, d = V.TRAY_W, V.TRAY_D
    pan = pv.merge([pv.Box(bounds=(-w / 2, w / 2, -d / 2, d / 2, 0, V.T_FLOOR)),
                    pv.Box(bounds=(-w / 2, w / 2, d / 2 - 12, d / 2, 0, V.T_FLOOR + V.T_RIM)),
                    pv.Box(bounds=(-w / 2, -w / 2 + 12, -d / 2, d / 2, 0, V.T_FLOOR + V.T_RIM)),
                    pv.Box(bounds=(w / 2 - 12, w / 2, -d / 2, d / 2, 0, V.T_FLOOR + V.T_RIM))]).triangulate()
    out = {}
    for kind in KIND_H:
        by: dict = {}
        by.setdefault((tuple(V.MATERIALS["vlm_tray"][:3]), 1.0), []).append(pan)
        for key, x, y in loads[kind]:
            pieces = [f"cubxl_{p}" for p in ("frame", "gantry", "carriage", "tools")] if key == "cubxl" else [key]
            bb = eq[pieces[0]][1]
            M = T((x, y, V.T_FLOOR)) @ T((-(bb[0] + bb[1]) / 2, -(bb[2] + bb[3]) / 2, -bb[4]))
            for p in pieces:
                for mesh, col, op in dec[p].values():
                    if mesh.n_points:
                        by.setdefault((tuple(round(c, 3) for c in col), round(op, 2)), []).append(
                            mesh.transform(M, inplace=False))
        out[kind] = {k: pv.merge(v, merge_points=False) for k, v in by.items()}
    return out


def unit_shell(H: float = H_TALL) -> dict:
    """{name: (mesh, colour, ghost opacity or None, grow)} for one tall unit in its own frame. `grow` is the pivot height
    for parts that stretch with the unit as it grows (None: fixed; "roof": moves with the top)."""
    W, D, sk = V.UNIT_W, V.UNIT_D, V.SKIN
    xo, yo = W / 2, D / 2
    ow = V.OPEN_W / 2 + V.POST_W
    zb, zt = V.Z_SILL - 120.0, V.Z_OPEN_TOP + V.HEADER_H
    yf = -yo - sk                                       # outer face of the front panel
    box = lambda *b: pv.Box(bounds=b).triangulate()     # noqa: E731
    p = {}
    p["skin side L"] = (box(-xo - sk, -xo, -yo, yo, 140, H), V.RAL7035, 0.10, 140.0)
    p["skin side R"] = (box(xo, xo + sk, -yo, yo, 140, H), V.RAL7035, 0.10, 140.0)
    p["skin back"] = (box(-xo, xo, yo, yo + sk, 140, H), V.RAL7035, 0.10, 140.0)
    p["skin front high"] = (box(-xo, xo, yf, -yo, zt, H), V.RAL7035, 0.10, zt)
    p["skin front low"] = (pv.merge([box(-xo, xo, yf, -yo, 140, zb), box(-xo, -ow, yf, -yo, zb, zt),
                                     box(ow, xo, yf, -yo, zb, zt)]), V.RAL7035, 0.10, None)
    p["skin roof"] = (box(-xo - sk, xo + sk, -yo - sk, yo + sk, H, H + sk), V.RAL7035, 0.10, "roof")
    p["base"] = (box(-xo, xo, -yo, yo, 40, 140), (0.23, 0.24, 0.26), None, None)
    posts = pv.merge([box(sx * xo - 35 - sx * 35, sx * xo + 35 - sx * 35, y - 35, y + 35, 140, H)
                      for sx in (-1, 1) for y in (-yo + 35, -515.0, 515.0, yo - 35)])
    p["posts"] = (posts, (0.23, 0.24, 0.26), None, 140.0)
    o = V.OPEN_W / 2
    p["opening posts"] = (pv.merge([box(-o - V.POST_W, -o, yf - 30, yf + 40, zb, zt), box(o, o + V.POST_W, yf - 30,
                                    yf + 40, zb, zt)]), (56 / 255, 62 / 255, 66 / 255), None, None)
    p["opening header"] = (box(-o, o, yf - 20, yf + 40, V.Z_OPEN_TOP, zt), (0.90, 0.91, 0.91), None, None)
    p["tray cover"] = (box(-o, o, yf - LIP, yf + 30, zb, V.Z_SILL), V.FIR_BLUE, None, None)
    p["LED light"] = (box(-o + 20, o - 20, yf - 10, yf + 160, V.Z_OPEN_TOP - 12, V.Z_OPEN_TOP), (0.98, 0.97, 0.88),
                      None, None)
    p["shutter"] = (box(-o, o, V.Y_SHUTTER - 6, V.Y_SHUTTER + 6, V.Z_OPEN - 10, V.Z_OPEN_TOP + 40), V.FIR_BLUE, 0.35,
                    None)
    return p


def extractor_mesh() -> pv.PolyData:
    w = V.TRAY_W + 110
    plat = pv.Box(bounds=(-w / 2, w / 2, -V.TRAY_D / 2 - 20, V.TRAY_D / 2 + 20, -90, -10))
    cars = [pv.Box(bounds=(sx * (V.UNIT_W / 2 - 115) - 45, sx * (V.UNIT_W / 2 - 115) + 45, -V.TRAY_D / 2 - 60,
                           V.TRAY_D / 2 + 60, -160, 40)) for sx in (-1, 1)]
    return pv.merge([plat, *cars]).triangulate()


def rail_meshes(length: float) -> dict:
    """The floor rail down the aisle: a base beam, two steel rails, end stops; and the carriage with its riser."""
    box = lambda *b: pv.Box(bounds=b).triangulate()     # noqa: E731
    L = length / 2
    rail = {"rail beam": (box(-L, L, -220, 220, 0, 90), (0.23, 0.24, 0.26)),
            "rails": (pv.merge([box(-L, L, y - 20, y + 20, 90, 125) for y in (-160, 160)]), (0.70, 0.71, 0.73)),
            "end stops": (pv.merge([box(x - 40, x + 40, -230, 230, 90, 220) for x in (-L + 40, L - 40)]),
                          (0.95, 0.75, 0.15))}
    car = {"carriage": (box(-330, 330, -260, 260, 125, 245), (0.23, 0.24, 0.26)),
           "riser": (box(-170, 170, -170, 170, 245, RAIL_Z - 20), (0.85, 0.86, 0.85)),
           "riser plate": (box(-190, 190, -190, 190, RAIL_Z - 20, RAIL_Z), (0.62, 0.63, 0.66)),
           "carriage light": (box(-332, 332, -262, 262, 200, 214), (0.25, 0.85, 0.85))}
    return {"rail": rail, "carriage": car}
