"""Screws and nuts for the assembly animation, at nominal ISO sizes, in their assembled places.

Every screw is built along +Z with the underside of its head at Z = 0 and the shank running up
+Z; `along` then turns +Z onto the screw's own axis (the way the shank points) and moves the head
seat into place. Nuts sit on Z = 0 and are placed the same way.
"""
from __future__ import annotations

import math

import cadquery as cq

from piper_mount import Params, cm_holes, hq_holes, hq_place, cm_place, pi_holes, pod_screw_axes, station_vec

ISO4762 = {"M2": (3.8, 2.0, 1.5), "M2.5": (4.5, 2.5, 2.0), "M3": (5.5, 3.0, 2.5)}   # head d, head h, key
ISO4032 = {"M2": (4.0, 1.6), "M2.5": (5.0, 2.0), "M3": (5.5, 2.4)}                   # nut AF, height
MAJOR = {"M2": 2.0, "M2.5": 2.5, "M3": 3.0}


def socket_head(size: str, length: float) -> cq.Workplane:
    dk, k, s = ISO4762[size]
    head = cq.Workplane("XY").circle(dk / 2).extrude(k).translate((0, 0, -k)).faces("<Z").chamfer(0.25)
    head = head.cut(cq.Workplane("XY").polygon(6, s / math.cos(math.pi / 6)).extrude(k * 0.6).translate((0, 0, -k - 0.01)))
    return head.union(cq.Workplane("XY").circle(MAJOR[size] / 2).extrude(length))


def hex_nut(size: str) -> cq.Workplane:
    af, m = ISO4032[size]
    nut = cq.Workplane("XY").polygon(6, af / math.cos(math.pi / 6)).extrude(m)
    return nut.cut(cq.Workplane("XY").circle(MAJOR[size] * 0.42).extrude(m + 1).translate((0, 0, -0.5)))


def along(shape: cq.Workplane, seat: cq.Vector, direction: cq.Vector, spin: float = 0.0) -> cq.Workplane:
    """Turn +Z onto `direction` and put the origin at `seat`."""
    d = direction.normalized()
    z = cq.Vector(0, 0, 1)
    shape = shape.rotate((0, 0, 0), (0, 0, 1), spin)
    axis = z.cross(d)
    ang = math.degrees(math.acos(max(-1.0, min(1.0, z.dot(d)))))
    if axis.Length > 1e-9:
        shape = shape.rotate((0, 0, 0), axis.normalized().toTuple(), ang)
    elif ang > 90:
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 180)
    return shape.translate(seat.toTuple())


def placed(p: Params) -> dict[str, dict]:
    """Every fastener group in its assembled position, with the direction it goes in along
    (for the animation) and a short label. Keys are animation groups."""
    X, Y = cq.Vector(1, 0, 0), cq.Vector(0, 1, 0)
    t = math.radians(p.toe_deg)
    fwd = cq.Vector(math.sin(t), -math.cos(t), 0)            # station -Y: into the pod, from its front
    out: dict[str, dict] = {}
    # Tab: M3 x 12 down the hex-key channels (head on the pad's back face, shank toward -Y).
    y_pad = p.collar_y0 + p.pad_t
    out["tab_screws"] = {"shapes": [along(socket_head("M3", p.tab_screw_len), cq.Vector(x, y_pad, z), -Y)
                                    for x, z in p.tab_holes], "dir": -Y, "label": "2 x M3 x 12"}
    # Collar: heads on the carrier side, shank toward -X into nuts in the bracket's ears.
    seat_x = p.ax_x + p.clamp_head_seat
    clamp = [(y, p.ax_z + sz * p.clamp_r) for sz in (-1, 1) for y in p.clamp_y]
    out["clamp_screws"] = {"shapes": [along(socket_head("M3", p.clamp_screw_len), cq.Vector(seat_x, y, z), -X)
                                      for y, z in clamp], "dir": -X, "label": "4 x M3 x 16"}
    nut_x = p.ax_x - p.ear_w + p.m3_nut_depth - 0.3
    out["clamp_nuts"] = {"shapes": [along(hex_nut("M3"), cq.Vector(nut_x, y, z), -X) for y, z in clamp],
                         "dir": X, "label": "4 x M3 nut"}
    # Pod: M3 x 16 from the pod's back face into nuts slid into the web.
    pod = pod_screw_axes(p)
    out["pod_screws"] = {"shapes": [along(socket_head("M3", p.pod_screw_len), a, d) for a, d in pod],
                         "dir": fwd, "label": "2 x M3 x 16"}
    h = ISO4032["M3"][1]
    out["pod_nuts"] = {"shapes": [along(hex_nut("M3"), a + d * (-p.hq_standoff - p.pod_nut_y + h / 2), -d,
                                        spin=p.toe_deg) for a, d in pod],
                       "dir": cq.Vector(math.cos(t), math.sin(t), 0), "label": "2 x M3 nut"}
    # HQ Camera: M2.5 x 12 from the pod's front counterbores, nuts on the back of the board.
    hq, cm = hq_place(p), cm_place(p)
    back = -fwd
    front_seat = -(p.hq_standoff + p.pod_t) + 2.0                    # station y of the counterbore floor
    out["hq_screws"] = {"shapes": [along(socket_head("M2.5", 12), _hq_pt(p, x, y, front_seat), back)
                                   for x, y in hq_holes(p)], "dir": back, "label": "4 x M2.5 x 12"}
    out["hq_nuts"] = {"shapes": [along(hex_nut("M2.5"), _hq_pt(p, x, y, p.hq_pcb_t), back) for x, y in hq_holes(p)],
                      "dir": fwd, "label": "4 x M2.5 nut"}
    cm_seat = -(p.hq_standoff + p.pod_t) + 2.0
    out["cm_screws"] = {"shapes": [along(socket_head("M2", 10), _cm_pt(p, x, y, cm_seat), back)
                                   for x, y in cm_holes(p)], "dir": back, "label": "4 x M2 x 10"}
    out["cm_nuts"] = {"shapes": [along(hex_nut("M2"), _cm_pt(p, x, y, -(p.hq_standoff - p.cm_standoff) + p.cm_pcb_t),
                                       back) for x, y in cm_holes(p)], "dir": fwd, "label": "4 x M2 nut"}
    # Pi 5: M2.5 x 12 from the top of the board, through the spacers, into nuts in the carrier.
    top = p.pi_x + 1.6
    out["pi_screws"] = {"shapes": [along(socket_head("M2.5", 12), cq.Vector(top, y, z), -X) for y, z in pi_holes(p)],
                        "dir": -X, "label": "4 x M2.5 x 12"}
    out["pi_nuts"] = {"shapes": [along(hex_nut("M2.5"), cq.Vector(p.carrier_x0 - 0.01, y, z), X)
                                 for y, z in pi_holes(p)], "dir": X, "label": "4 x M2.5 nut"}
    return out


def _hq_pt(p: Params, x: float, y: float, y_station: float) -> cq.Vector:
    """A point on an HQ hole's axis (camera-frame x, y), at a given station-frame depth."""
    v = hq_place(p)(cq.Workplane().add(cq.Vertex.makeVertex(x, y, 0))).val()
    o = station_vec(p, 0, 0, 0)
    t = math.radians(p.toe_deg)
    d = cq.Vector(-math.sin(t), math.cos(t), 0)                     # station +Y
    return cq.Vector(v.X, v.Y, v.Z) + d * (y_station - (cq.Vector(v.X, v.Y, v.Z) - o).dot(d))


def _cm_pt(p: Params, x: float, y: float, y_station: float) -> cq.Vector:
    v = cm_place(p)(cq.Workplane().add(cq.Vertex.makeVertex(x, y, 0))).val()
    o = station_vec(p, 0, 0, 0)
    t = math.radians(p.toe_deg)
    d = cq.Vector(-math.sin(t), math.cos(t), 0)
    return cq.Vector(v.X, v.Y, v.Z) + d * (y_station - (cq.Vector(v.X, v.Y, v.Z) - o).dot(d))
