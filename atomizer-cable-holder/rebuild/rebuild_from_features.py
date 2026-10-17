#!/usr/bin/env python3
"""Rebuild the atomizer transducer cable holder from its Onshape feature list.

The Onshape document (issue #256) is shared by link as view-only, so the API
refuses every geometry, mass-property and export request, but it does return the
feature list. That list carries the solved sketch, so the part can be rebuilt
from it:

    Sketch 1   on the Front plane (sketch x = world X, sketch y = world Z)
    Extrude 1  15 mm, symmetric, new     the 50 x 10 mm strip
    Extrude 2  10 mm, symmetric, add     both arms of the 11 mm clip
    Fillet 1   1 mm                       strip corners, 11 mm clip lips and tips
    Extrude 3   5 mm, symmetric, add     both arms of the 7 mm clip
    Fillet 2   0.7 mm                     7 mm clip tips

Every number (coordinates, radii, depths, fillet radii) is read from
onshape/features.json. Only the topology is written down here: which sketch
entities bound each extruded region and which pairs of entities meet at each
filleted edge, as decoded from the features' queries. The script checks each of
those names against the query text and each fillet pair against the geometry.

Every filleted edge is a straight edge swept along Y, through the full depth of
its own extrude, and touches no other extrude. So rounding the corner in the 2D
profile and then extruding gives the same solid as a 3D fillet. The fillets are
computed here as rolling-ball arcs rather than with OCCT's 2D fillet, because the
clip tips are narrower than two fillets: 1.6 mm against 2 x 1 mm, and 1.0 mm
against 2 x 0.7 mm. Onshape accepted that (both fillets report OK), so it must
have let the two blends meet. Here they are trimmed where they cross, which
leaves a ridge 0.02-0.03 mm short of the original tip face.

    python rebuild_from_features.py     # writes the STL, STEP and rebuild_summary.json
"""
from __future__ import annotations

import base64
import json
import math
import re
import zlib
from pathlib import Path

import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

HERE = Path(__file__).resolve().parent
FEATURES = HERE / "onshape" / "features.json"
OUT = HERE / "transducer_cable_holder"
M = 1000.0  # Onshape stores lengths in metres
TOL = 1e-3  # mm

# Regions of each extrude: the sketch entities bounding them, from the
# "entities" query of each feature. The strip's bottom line closes each arm.
REGIONS = {
    "Extrude 1": [["aKihO2aJETPw.bottom", "aKihO2aJETPw.left", "aKihO2aJETPw.top", "aKihO2aJETPw.right"]],
    "Extrude 2": [
        ["WhlkgmXsXaYM", "LTb9wVHzNvQz.2", "KNvQ3vkQSjVG", "LTb9wVHzNvQz.3", "s4qqPcMQ7sLE"],
        ["lLjdItcHwoXN", "LTb9wVHzNvQz.1", "6iuAaWpwqLFj0.MirrorCS", "LTb9wVHzNvQz.0", "pUUDbhWkUr87"],
    ],
    "Extrude 3": [
        ["FErnh2wuGgi8", "i5ELe0lwy9TE.2", "twg05FiZ6HoB", "i5ELe0lwy9TE.3", "4ltZ142El1J4"],
        ["V5Sx6TMcAORY", "i5ELe0lwy9TE.1", "rtSOOJ6sqQ9b0.MirrorCS", "i5ELe0lwy9TE.0", "5QNkv2wEuXfj"],
    ],
}
# Filleted edges: each is swept from the sketch vertex where two entities meet.
FILLETS = {
    "Fillet 1": [
        ("lLjdItcHwoXN", "6iuAaWpwqLFj0.MirrorCS"), ("KNvQ3vkQSjVG", "WhlkgmXsXaYM"),
        ("aKihO2aJETPw.bottom", "aKihO2aJETPw.left"), ("aKihO2aJETPw.top", "aKihO2aJETPw.left"),
        ("aKihO2aJETPw.top", "aKihO2aJETPw.right"), ("aKihO2aJETPw.bottom", "aKihO2aJETPw.right"),
        ("KNvQ3vkQSjVG", "s4qqPcMQ7sLE"), ("6iuAaWpwqLFj0.MirrorCS", "pUUDbhWkUr87"),
        ("LTb9wVHzNvQz.3", "s4qqPcMQ7sLE"), ("LTb9wVHzNvQz.0", "pUUDbhWkUr87"),
    ],
    "Fillet 2": [
        ("twg05FiZ6HoB", "4ltZ142El1J4"), ("i5ELe0lwy9TE.3", "4ltZ142El1J4"),
        ("rtSOOJ6sqQ9b0.MirrorCS", "5QNkv2wEuXfj"), ("i5ELe0lwy9TE.0", "5QNkv2wEuXfj"),
    ],
}


# --- reading the feature list -----------------------------------------------------------

def query_text(feature: dict, pid: str) -> str:
    """The decoded text of a feature's query parameter (zlib+base64 when it starts with '&')."""
    out = []
    for p in feature["parameters"]:
        if p["parameterId"] != pid:
            continue
        for q in p["queries"]:
            s = re.search(r'qCompressed\(1\.0,"(.*)",id\)', q["queryString"]).group(1)
            if s.startswith("&"):
                body = s.split("$", 1)[1].replace("\\", "")
                s = zlib.decompress(base64.b64decode(body + "=" * (-len(body) % 4))).decode()
            out.append(s)
    return "\n".join(out)


def param(feature: dict, pid: str):
    for p in feature["parameters"]:
        if p["parameterId"] == pid:
            if "expression" in p:
                value, unit = p["expression"].split()
                assert unit == "mm", p["expression"]
                return float(value)
            return p["value"]
    raise KeyError(pid)


def sketch_curves(sketch: dict) -> dict:
    """Non-construction lines and arcs of the sketch, in mm."""
    curves = {}
    for e in sketch["entities"]:
        g = e.get("geometry") or {}
        if e.get("isConstruction"):
            continue
        if g.get("btType") == "BTCurveGeometryLine-117":
            x0, y0, a, b = g["pntX"] * M, g["pntY"] * M, e["startParam"] * M, e["endParam"] * M
            dx, dy = g["dirX"], g["dirY"]
            curves[e["entityId"]] = Seg("line", (x0 + a * dx, y0 + a * dy), (x0 + b * dx, y0 + b * dy))
        elif g.get("btType") == "BTCurveGeometryCircle-115" and e["btType"] == "BTMSketchCurveSegment-155":
            cx, cy, r = g["xCenter"] * M, g["yCenter"] * M, g["radius"] * M
            base, sign = math.atan2(g["yDir"], g["xDir"]), (-1 if g["clockwise"] else 1)
            pt = lambda t: (cx + r * math.cos(base + sign * t), cy + r * math.sin(base + sign * t))
            curves[e["entityId"]] = Seg("arc", pt(e["startParam"]), pt(e["endParam"]), (cx, cy), r,
                                        ccw=not g["clockwise"])
    return curves


# --- 2D geometry ------------------------------------------------------------------------

def sub(p, q): return (p[0] - q[0], p[1] - q[1])
def add(p, q): return (p[0] + q[0], p[1] + q[1])
def mul(p, k): return (p[0] * k, p[1] * k)
def dot(p, q): return p[0] * q[0] + p[1] * q[1]
def cross(p, q): return p[0] * q[1] - p[1] * q[0]
def unit(p): return mul(p, 1 / math.hypot(*p))
def close(p, q): return math.dist(p, q) < TOL


class Seg:
    """A directed line or circular arc from p0 to p1."""

    def __init__(self, kind, p0, p1, c=None, r=None, ccw=None):
        self.kind, self.p0, self.p1, self.c, self.r, self.ccw = kind, p0, p1, c, r, ccw

    def reversed(self) -> "Seg":
        return Seg(self.kind, self.p1, self.p0, self.c, self.r, None if self.ccw is None else not self.ccw)

    def sweep(self, a=None, b=None) -> float:
        """Signed angle swept from a to b (default p0 to p1) along this arc's direction."""
        ta = math.atan2(*reversed(sub(a or self.p0, self.c)))
        tb = math.atan2(*reversed(sub(b or self.p1, self.c)))
        return (tb - ta) % (2 * math.pi) if self.ccw else -((ta - tb) % (2 * math.pi))

    def mid(self):
        if self.kind == "line":
            return mul(add(self.p0, self.p1), 0.5)
        t = math.atan2(*reversed(sub(self.p0, self.c))) + self.sweep() / 2
        return add(self.c, (self.r * math.cos(t), self.r * math.sin(t)))

    def samples(self, n=16):
        if self.kind == "line":
            return [self.p0]
        t0, s = math.atan2(*reversed(sub(self.p0, self.c))), self.sweep()
        return [add(self.c, (self.r * math.cos(t0 + s * i / n), self.r * math.sin(t0 + s * i / n))) for i in range(n)]

    def offset(self, d):
        """This curve moved d to its left: (point, direction) for a line, (centre, radius) for an arc."""
        if self.kind == "line":
            u = unit(sub(self.p1, self.p0))
            return ("line", add(self.p0, mul((-u[1], u[0]), d)), u)
        return ("circle", self.c, self.r - d if self.ccw else self.r + d)

    def foot(self, o):
        """The point of this curve's line or circle nearest o."""
        if self.kind == "line":
            u = unit(sub(self.p1, self.p0))
            return add(self.p0, mul(u, dot(sub(o, self.p0), u)))
        return add(self.c, mul(unit(sub(o, self.c)), self.r))

    def param(self, p) -> float:
        if self.kind == "line":
            return dot(sub(p, self.p0), unit(sub(self.p1, self.p0)))
        return abs(self.sweep(self.p0, p)) if not close(p, self.p0) else 0.0

    def edge(self) -> cq.Edge:
        if self.kind == "line":
            return cq.Edge.makeLine(vec(self.p0), vec(self.p1))
        return cq.Edge.makeThreePointArc(vec(self.p0), vec(self.mid()), vec(self.p1))


def vec(p) -> cq.Vector:
    return cq.Vector(p[0], 0.0, p[1])  # Front plane: sketch (x, y) -> world (x, 0, y)


def intersect(a, b) -> list:
    """Intersections of two offset curves, each ("line", point, dir) or ("circle", centre, radius)."""
    if a[0] == "circle" and b[0] == "line":
        a, b = b, a
    if a[0] == "line" and b[0] == "line":
        (_, p, u), (_, q, v) = a, b
        t = cross(sub(q, p), v) / cross(u, v)
        return [add(p, mul(u, t))]
    if a[0] == "line":
        (_, p, u), (_, c, r) = a, b
        f = dot(sub(c, p), u)
        h2 = r * r - (dot(sub(c, p), sub(c, p)) - f * f)
        return [add(p, mul(u, f + s * math.sqrt(max(h2, 0)))) for s in (-1, 1)]
    (_, c1, r1), (_, c2, r2) = a, b
    d = math.dist(c1, c2)
    x = (d * d + r1 * r1 - r2 * r2) / (2 * d)
    h = math.sqrt(max(r1 * r1 - x * x, 0))
    u = unit(sub(c2, c1))
    m = add(c1, mul(u, x))
    return [add(m, mul((-u[1], u[0]), s * h)) for s in (-1, 1)]


# --- profile ----------------------------------------------------------------------------

def loop(curves: dict, names: list[str]) -> list[Seg]:
    """Chain the named curves into a closed, counter-clockwise loop, closing an open chain with a
    line (the strip's bottom edge, which the arms share with the strip)."""
    segs = [curves[n] for n in names]
    pts = [p for s in segs for p in (s.p0, s.p1)]
    free = [p for p in pts if sum(close(p, q) for q in pts) == 1]
    end, chain, todo = (free[0] if free else segs[0].p0), [], list(segs)
    while todo:
        s = next(s for s in todo if close(s.p0, end) or close(s.p1, end))
        todo.remove(s)
        chain.append(s if close(s.p0, end) else s.reversed())
        end = chain[-1].p1
    if not close(end, chain[0].p0):
        assert abs(end[1] - chain[0].p0[1]) < TOL, "an open chain must close along the strip's bottom edge"
        chain.append(Seg("line", end, chain[0].p0))
    poly = [p for s in chain for p in s.samples()]
    area = sum(cross(poly[i - 1], poly[i]) for i in range(len(poly))) / 2
    return chain if area > 0 else [s.reversed() for s in reversed(chain)]


def fillet(chain: list[Seg], corners: dict) -> list[Seg]:
    """Round the corners (vertex -> radius) of a counter-clockwise loop with rolling-ball arcs.
    Where two fillets overlap across a short segment, the segment goes and the arcs meet."""
    n = len(chain)
    fil = {}  # index of the segment that starts at the vertex -> (centre, radius, foot on prev, foot on next)
    for i, s in enumerate(chain):
        r = next((rr for v, rr in corners.items() if close(v, s.p0)), None)
        if r is None:
            continue
        prev = chain[i - 1]
        o = min(intersect(prev.offset(r), s.offset(r)), key=lambda q: math.dist(q, s.p0))
        fil[i] = [o, r, prev.foot(o), s.foot(o)]
    for i, s in enumerate(chain):  # overlapping fillets: meet where the two circles cross
        a, b = fil.get(i), fil.get((i + 1) % n)
        if a and b and s.param(a[3]) >= s.param(b[2]) - TOL:
            x = min(intersect(("circle", a[0], a[1]), ("circle", b[0], b[1])), key=lambda q: math.dist(q, s.mid()))
            a[3] = b[2] = x
    out = []
    for i, s in enumerate(chain):
        a, b = fil.get(i), fil.get((i + 1) % n)
        if a:
            o, r, p, q = a
            arc_mid = add(o, mul(unit(add(unit(sub(p, o)), unit(sub(q, o)))), r))
            out.append(Seg("arc3", p, q, arc_mid))
        start, end = (a[3] if a else s.p0), (b[2] if b else s.p1)
        if close(start, end) or (a and b and s.param(start) > s.param(end)):
            continue  # consumed by the fillets on either side
        out.append(Seg(s.kind, start, end, s.c, s.r, s.ccw))
    return out


def face(segs: list[Seg]) -> cq.Face:
    edges = []
    for s in segs:
        if s.kind == "arc3":  # fillet arc, given by three points
            edges.append(cq.Edge.makeThreePointArc(vec(s.p0), vec(s.c), vec(s.p1)))
        else:
            edges.append(s.edge())
    f = cq.Face.makeFromWires(cq.Wire.assembleEdges(edges))
    assert f.isValid()
    return f


def extrude_symmetric(f: cq.Face, depth: float) -> cq.Solid:
    return cq.Solid.extrudeLinear(f.translate(cq.Vector(0, -depth / 2, 0)), cq.Vector(0, depth, 0))


def gap(a: cq.Shape, b: cq.Shape) -> float:
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    return d.Value()


def main() -> dict:
    doc = json.loads(FEATURES.read_text())
    feats = {f["name"]: f for f in doc["features"]}
    states = {k: v["featureStatus"] for k, v in doc["featureStates"].items()}
    assert set(states.values()) == {"OK"}, states
    curves = sketch_curves(feats["Sketch 1"])

    # The decoded queries must name every entity this script assumes.
    for name, regions in REGIONS.items():
        text = query_text(feats[name], "entities")
        for ent in sum(regions, []):
            assert ent.split(".")[0] in text, (name, ent)
    for name, pairs in FILLETS.items():
        text = query_text(feats[name], "entities")
        assert text.count("SWEPT_EDGE") == len(pairs), name
        for a, b in pairs:
            assert a.split(".")[0] in text and b.split(".")[0] in text, (name, a, b)

    corners = {}
    for name, pairs in FILLETS.items():
        for a, b in pairs:
            v = next(p for p in (curves[a].p0, curves[a].p1) if close(p, curves[b].p0) or close(p, curves[b].p1))
            corners[v] = param(feats[name], "radius")

    solids, faces, report = [], {}, {"extrudes": {}, "fillets": {}}
    for name, regions in REGIONS.items():
        f = feats[name]
        assert f["featureType"] == "extrude" and param(f, "symmetric") is True
        depth = param(f, "depth")
        faces[name] = [face(fillet(loop(curves, names), corners)) for names in regions]
        solids += [extrude_symmetric(fc, depth) for fc in faces[name]]
        report["extrudes"][name] = {"depth_mm": depth, "regions": len(regions),
                                    "profile_area_mm2": round(sum(fc.Area() for fc in faces[name]), 4)}
    for name, pairs in FILLETS.items():
        report["fillets"][name] = {"radius_mm": param(feats[name], "radius"), "edges": len(pairs)}

    part = solids[0].fuse(*solids[1:]).clean()
    assert part.isValid() and len(part.Solids()) == 1

    bb = part.BoundingBox()
    report["volume_mm3"] = round(part.Volume(), 3)
    report["surface_mm2"] = round(part.Area(), 3)
    report["bbox_mm"] = {k: [round(lo, 4), round(hi, 4)] for k, lo, hi in
                         (("x", bb.xmin, bb.xmax), ("y", bb.ymin, bb.ymax), ("z", bb.zmin, bb.zmax))}
    # Narrowest opening of each clip, after fillets: the gap between its two arms, below the
    # hole's centre (the arms touch at the top, where the hole is tangent to the strip).
    report["clip_opening_mm"] = {}
    for label, name in (("11 mm clip", "Extrude 2"), ("7 mm clip", "Extrude 3")):
        z = curves[REGIONS[name][0][0]].c[1]
        below = cq.Solid.makeBox(100, 100, 100, cq.Vector(-50, -50, z - 100))
        report["clip_opening_mm"][label] = round(gap(*(f.intersect(below) for f in faces[name])), 4)
    report["source"] = {"document": "3094e1d7fbb4c4351dcd0e1a", "workspace": "d3134413115bb70af771d24a",
                        "element": "ef669eb623cfc76bb11527a4", "microversion": doc["sourceMicroversion"]}

    cq.exporters.export(part, str(OUT.with_suffix(".step")))
    cq.exporters.export(part, str(OUT.with_suffix(".stl")), tolerance=0.005, angularTolerance=0.05)
    (HERE / "rebuild_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
