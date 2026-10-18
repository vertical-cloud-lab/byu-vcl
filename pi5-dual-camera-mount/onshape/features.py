#!/usr/bin/env python3
"""The mount and the C-mount collar as Onshape features: sketches on the Top, Front and Right
planes, each followed by an extrude. onshape_api.py sends this list to Onshape as native
features, so the model stays editable there.

build_cq() replays the same list in CadQuery with Onshape's own plane and extrude conventions
(from the FeatureScript standard library: defaultFeatures.fs and extrude.fs). check() compares
the result with mount.py, so the list is known to be right before any API call is spent:

    python features.py        # prints the volumes and the symmetric difference, which should be 0
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cad"))
import mount as m  # noqa: E402

# Onshape's default planes, as defaultFeatures.fs makes them: (normal, sketch x direction).
# The sketch y direction is normal x (sketch x), so the Front plane's sketch y is world +Z.
PLANES = {
    "Top": ((0, 0, 1), (1, 0, 0)),
    "Front": ((0, -1, 0), (1, 0, 0)),
    "Right": ((1, 0, 0), (0, 1, 0)),
}
THROUGH = 1000.0          # "through all", for the CadQuery replay


# --- sketch entities (millimetres, in the sketch plane's own x, y) -----------------------------

@dataclass
class Line:
    x0: float
    y0: float
    x1: float
    y1: float


@dataclass
class Arc:
    """Counter-clockwise from angle a0 to a1 (radians, from the sketch's x direction)."""
    cx: float
    cy: float
    r: float
    a0: float
    a1: float


@dataclass
class Circle:
    cx: float
    cy: float
    r: float


@dataclass
class Sketch:
    name: str
    plane: str
    loops: list[list]          # closed loops that neither overlap nor nest


@dataclass
class Extrude:
    name: str
    sketch: str                # name of the sketch whose regions it extrudes
    op: str                    # NEW, ADD or REMOVE
    depth: float | None        # None: through all
    opposite: bool = False     # against the plane's normal
    symmetric: bool = False    # depth is the full depth, half each way
    start_offset: float = 0.0  # the profile moves this far along the plane's normal first...
    start_opposite: bool = False  # ...or against it
    note: str = field(default="")


# --- profiles -------------------------------------------------------------------------------

def circle(cx, cy, d) -> list:
    return [Circle(cx, cy, d / 2)]


def polygon(pts) -> list:
    return [Line(*pts[i], *pts[(i + 1) % len(pts)]) for i in range(len(pts))]


def hexagon(cx, cy, af, vertex_up) -> list:
    return polygon([(cx + x, cy + y) for x, y in m.hex_pts(af, vertex_up)])


def rounded_polygon(pts, radii) -> list:
    """A closed counter-clockwise polygon with a fillet of radii[i] at each vertex, convex or
    concave (as CadQuery's fillet of the vertical edges gives)."""
    n = len(pts)
    ends = []                  # (tangent point into the corner, tangent point out of it, arc or None)
    for i in range(n):
        (px, py), r = pts[i], radii[i]
        ax, ay = pts[i - 1]
        bx, by = pts[(i + 1) % n]
        din = ((px - ax) / math.hypot(px - ax, py - ay), (py - ay) / math.hypot(px - ax, py - ay))
        dout = ((bx - px) / math.hypot(bx - px, by - py), (by - py) / math.hypot(bx - px, by - py))
        if r == 0:
            ends.append(((px, py), (px, py), None))
            continue
        turn = din[0] * dout[1] - din[1] * dout[0]           # > 0: convex, < 0: concave
        half = math.acos(max(-1.0, min(1.0, din[0] * dout[0] + din[1] * dout[1]))) / 2
        t = r * math.tan(half)
        t0 = (px - din[0] * t, py - din[1] * t)
        t1 = (px + dout[0] * t, py + dout[1] * t)
        side = 1 if turn > 0 else -1
        c = (t0[0] - side * din[1] * r, t0[1] + side * din[0] * r)
        a0 = math.atan2(t0[1] - c[1], t0[0] - c[0])
        a1 = math.atan2(t1[1] - c[1], t1[0] - c[0])
        if side < 0:
            a0, a1 = a1, a0                                   # keep every arc counter-clockwise
        while a1 <= a0:
            a1 += 2 * math.pi
        ends.append((t0, t1, Arc(c[0], c[1], r, a0, a1)))
    out = []
    for i in range(n):
        if ends[i][2] is not None:
            out.append(ends[i][2])
        a, b = ends[i][1], ends[(i + 1) % n][0]
        if math.hypot(b[0] - a[0], b[1] - a[1]) > 1e-9:
            out.append(Line(*a, *b))
    return out


def rounded_rect(cx, cy, w, h, r) -> list:
    return rounded_polygon([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2),
                            (cx - w / 2, cy + h / 2)], [r] * 4)


def teardrop(cx, cy, r) -> list:
    """A circle whose underside runs to a 45 degree point (mount.y_teardrop)."""
    k = r / math.sqrt(2)
    bottom = (cx, cy - r * math.sqrt(2))
    return [Arc(cx, cy, r, -math.pi / 4, 5 * math.pi / 4), Line(cx - k, cy - k, *bottom),
            Line(*bottom, cx + k, cy - k)]


def slot(cx, cy, length, width) -> list:
    a, r = (length - width) / 2, width / 2
    return [Arc(cx + a, cy, r, -math.pi / 2, math.pi / 2), Line(cx + a, cy + r, cx - a, cy + r),
            Arc(cx - a, cy, r, math.pi / 2, 3 * math.pi / 2), Line(cx - a, cy - r, cx + a, cy - r)]


# --- the two part studios -------------------------------------------------------------------

def mount_features(p: m.Params) -> list:
    """The printed L-bracket, in mount coordinates (see mount.py): X right, Y back, Z up."""
    hw, z = p.upright_half_w, p.axis_z
    sx0, sx1 = p.pi_x_edge - 56.0 - p.pi_margin, p.pi_x_edge + p.pi_margin
    y_end = p.pi_y0 + 85.0 + 1.0
    base = [(-hw, 0), (hw, 0), (hw, p.apron_depth), (sx1, p.apron_depth), (sx1, y_end), (sx0, y_end),
            (sx0, p.apron_depth), (-hw, p.apron_depth)]
    sx, sy = p.stand_xy
    r_out = p.stand_nut_af / m.COS30 / 2 + p.stand_collar_wall
    pis = p.pi_holes()
    xs, ys = [x for x, _ in pis], sorted({y for _, y in pis})
    top = p.upright_top
    upright = rounded_polygon([(-hw, 0), (hw, 0), (hw, top), (-hw, top)], [0, 0, p.top_r, p.top_r])
    hq = [(xc + u, z + v) for xc in p.stations for u, v in m.hq_holes(p)]
    cm3 = [(xc + u, z + v) for xc in p.stations for u, v in m.cm3_holes(p)]
    t = p.upright_t
    gusset = polygon([(t - 0.5, p.base_t - 0.5), (t + p.gusset_len, p.base_t - 0.5), (t - 0.5, p.base_t + p.gusset_h)])
    return [
        Sketch("Base outline", "Top", [rounded_polygon(base, [p.base_corner_r] * len(base))]),
        Extrude("Base plate", "Base outline", "NEW", p.base_t),
        Sketch("Pi 5 bosses", "Top", [circle(x, y, p.pi_boss_d) for x, y in pis]),
        Extrude("Pi 5 bosses", "Pi 5 bosses", "ADD", p.base_t + p.pi_boss_h),
        Sketch("Stand nut collar", "Top", [circle(sx, sy, 2 * r_out)]),
        Extrude("Stand nut collar", "Stand nut collar", "ADD", p.base_t + p.stand_collar_h),
        Sketch("Holes through the base", "Top",
               [circle(x, y, p.m25_clear_d) for x, y in pis] + [circle(sx, sy, p.stud_clear_d)]
               + [rounded_rect((min(xs) + max(xs)) / 2, (ys[0] + ys[1]) / 2, p.vent_w, p.vent_l, 4.0)]),
        Extrude("Pi 5 screw holes, stand stud hole, vent", "Holes through the base", "REMOVE", None),
        Sketch("Pi 5 nut traps", "Top", [hexagon(x, y, p.m25_nut_af, False) for x, y in pis]),
        Extrude("Pi 5 nut traps", "Pi 5 nut traps", "REMOVE", p.m25_nut_depth - 0.01),
        Sketch("Stand nut pocket", "Top", [hexagon(sx, sy, p.stand_nut_af, False)]),
        Extrude("Stand nut pocket", "Stand nut pocket", "REMOVE", p.stand_collar_h + 1, start_offset=p.base_t),
        Sketch("Upright", "Front", [upright]),
        Extrude("Upright", "Upright", "ADD", t, opposite=True),
        Sketch("HQ Camera bosses", "Front", [teardrop(x, y, p.hq_boss_d / 2) for x, y in hq]),
        Extrude("HQ Camera bosses", "HQ Camera bosses", "ADD", p.hq_boss_h),
        Sketch("Module 3 bosses", "Front", [teardrop(x, y, p.cm3_boss_d / 2) for x, y in cm3]),
        Extrude("Module 3 bosses", "Module 3 bosses", "ADD", p.cm3_boss_h),
        Sketch("Camera screw holes and ribbon slots", "Front",
               [circle(x, y, p.m25_clear_d) for x, y in hq] + [circle(x, y, p.m2_clear_d) for x, y in cm3]
               + [slot(xc, z + p.slot_v, p.slot_w, p.slot_h) for xc in p.stations]),
        Extrude("Camera screw holes and ribbon slots", "Camera screw holes and ribbon slots", "REMOVE", 20.0,
                symmetric=True),
        Sketch("HQ Camera nut pockets", "Front", [hexagon(x, y, p.m25_nut_af, True) for x, y in hq]),
        Extrude("HQ Camera nut pockets", "HQ Camera nut pockets", "REMOVE", p.m25_nut_depth + 0.01, opposite=True,
                start_offset=t - p.m25_nut_depth, start_opposite=True),
        Sketch("Module 3 nut pockets", "Front", [hexagon(x, y, p.m2_nut_af, True) for x, y in cm3]),
        Extrude("Module 3 nut pockets", "Module 3 nut pockets", "REMOVE", p.m2_nut_depth + 0.01, opposite=True,
                start_offset=t - p.m2_nut_depth, start_opposite=True),
        Sketch("Gusset", "Right", [gusset]),
        Extrude("Gusset, right", "Gusset", "ADD", p.gusset_t, start_offset=hw - p.gusset_t),
        Extrude("Gusset, left", "Gusset", "ADD", p.gusset_t, opposite=True, start_offset=hw - p.gusset_t,
                start_opposite=True),
    ]


def collar_features(p: m.Params) -> list:
    """The collar as printed (mount.collar_print): front face on the Top plane, legs up +Z."""
    a = p.hq_pitch / 2
    holes = [(su * a, sv * a) for su in (-1, 1) for sv in (-1, 1)]
    return [
        Sketch("Collar plate", "Top", [rounded_rect(0, 0, 2 * p.collar_half, 2 * p.collar_half, p.collar_corner_r)]),
        Extrude("Collar plate", "Collar plate", "NEW", p.collar_t),
        Sketch("Legs", "Top", [circle(x, y, p.collar_leg_d) for x, y in holes]),
        Extrude("Legs, down to the HQ board", "Legs", "ADD", p.collar_front),
        Sketch("Bore and screw holes", "Top", [circle(0, 0, p.collar_bore_d)]
               + [circle(x, y, p.m25_clear_d) for x, y in holes]),
        Extrude("Bore and screw holes", "Bore and screw holes", "REMOVE", None),
        Sketch("Crush ribs", "Top", [circle(u, -v, p.collar_rib_d) for u, v in m.collar_ribs(p)]),
        Extrude("Crush ribs", "Crush ribs", "ADD", p.collar_t),
        Sketch("Counterbores", "Top", [circle(x, y, p.collar_cbore_d) for x, y in holes]),
        Extrude("Counterbores for M2.5 socket heads", "Counterbores", "REMOVE", p.collar_cbore_h),
    ]


# --- CadQuery replay ------------------------------------------------------------------------

def _frame(plane: str):
    n, xd = (cq.Vector(*v) for v in PLANES[plane])
    return n, xd, n.cross(xd)


def _loop_face(loop, plane) -> cq.Face:
    n, xd, yd = _frame(plane)
    pt = lambda u, v: xd * u + yd * v  # noqa: E731
    edges = []
    for e in loop:
        if isinstance(e, Circle):
            edges.append(cq.Edge.makeCircle(e.r, pt(e.cx, e.cy), n))
        elif isinstance(e, Line):
            edges.append(cq.Edge.makeLine(pt(e.x0, e.y0), pt(e.x1, e.y1)))
        else:
            am = (e.a0 + e.a1) / 2
            edges.append(cq.Edge.makeThreePointArc(
                *(pt(e.cx + e.r * math.cos(a), e.cy + e.r * math.sin(a)) for a in (e.a0, am, e.a1))))
    return cq.Face.makeFromWires(cq.Wire.assembleEdges(edges))


def build_cq(features: list) -> cq.Solid:
    sketches, body = {}, None
    for f in features:
        if isinstance(f, Sketch):
            sketches[f.name] = f
            continue
        sk = sketches[f.sketch]
        n, _, _ = _frame(sk.plane)
        off = n * (-f.start_offset if f.start_opposite else f.start_offset)
        depth = THROUGH if f.depth is None else f.depth
        d = n * (-depth if f.opposite else depth)
        tools = []
        for loop in sk.loops:
            face = _loop_face(loop, sk.plane).translate(off)
            if f.symmetric:
                face = face.translate(d * -0.5)
            tools.append(cq.Solid.extrudeLinear(face, d))
        tool = tools[0].fuse(*tools[1:]).clean() if len(tools) > 1 else tools[0]
        if f.op == "NEW":
            body = tool
        elif f.op == "ADD":
            body = body.fuse(tool).clean()
        else:
            body = body.cut(tool).clean()
    return body


def compare(a: cq.Shape, b: cq.Shape) -> dict:
    return {"volume_features_mm3": round(a.Volume(), 3), "volume_mount_py_mm3": round(b.Volume(), 3),
            "features_minus_mount_py_mm3": round(a.cut(b).Volume(), 4),
            "mount_py_minus_features_mm3": round(b.cut(a).Volume(), 4)}


def check(p: m.Params | None = None) -> dict:
    p = p or m.Params()
    return {"mount": compare(build_cq(mount_features(p)), m.make_mount(p).val()),
            "collar": compare(build_cq(collar_features(p)), m.collar_print(p).val())}


if __name__ == "__main__":
    import json
    print(json.dumps(check(), indent=2))
