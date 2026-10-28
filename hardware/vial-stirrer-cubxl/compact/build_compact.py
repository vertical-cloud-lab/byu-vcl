#!/usr/bin/env python3
"""The compact (49 x 44 mm) stirrer's base and vial holder, built in CadQuery from
onshape/vial_stirrer.fs's numbers and the 49 x 44 mm layout in analysis/deck_tiling.py.

The Onshape model (vial_stirrer.fs, rebuilt by build_onshape.py) has only today's 56 x 56 mm
stirrer. This script ports its makeBase and makeHolder to CadQuery with a `compact` switch, so the
compact parts could be printed from a run without the Onshape API keys (2026-10-28). It also builds
today's parts with the same code and compares them with the Onshape STLs, so the port can be
checked part by part before the compact parts are trusted.

    python compact/build_compact.py            # writes stl/compact/*.stl, step/compact/*.step, compact/check_output.txt

Needs cadquery, trimesh and manifold3d.
"""

from __future__ import annotations

import math
import pathlib
import re

import cadquery as cq

ROOT = pathlib.Path(__file__).resolve().parent.parent
FS = ROOT / "onshape" / "vial_stirrer.fs"


def fs_constants(path: pathlib.Path) -> dict:
    """The top-level `const NAME = expr;` lines of the FeatureScript, evaluated in order."""
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

# The compact layout (analysis/deck_tiling.py COMPACT), plus what modelling it settled (see the README)
COMPACT = {
    "W": 49.0, "D": 44.0,     # footprint, X x Y
    "R": 5.0,                 # corner radius, as now
    "WALL": 1.6,              # base walls
    "CBORE_D": 6.5,           # counterbores for the M3 x 20 heads in the flange
    "CBORE_SEAT": C["Z_WALL"] + C["FLANGE_T"] - 3.0,   # 3 mm deep, as deck_tiling.py checked
    "THRU_D": 3.4,            # M3 clearance through the flange, as today's corner holes
    "NOTCH": (-11.0, -3.0),   # cable notch in the -Y wall, between the fan posts
    "BOARD_IN": 0.5,          # junction board's rails and stop move this far toward +X
    "WALL_DROP": 1.0,         # base walls end 1 mm under the flange: the holder sits on the fan, not the walls
    "HOLE_DEPTH": 7.5,        # insert holes 1 mm deeper than today's 6.5, so an M3 x 20 never bottoms out
    # and no vents in the -Y wall, where the cable notch is (make_base)
}


def box(x0, y0, z0, x1, y1, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl(x, y, z0, z1, r):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(r).extrude(z1 - z0)


def cone(z0, z1, r0, r1):
    return cq.Workplane("XY").add(cq.Solid.makeCone(r0, r1, z1 - z0, cq.Vector(0, 0, z0), cq.Vector(0, 0, 1)))


def rbox(w, d, z0, z1, r):
    return cq.Workplane("XY").workplane(offset=z0).rect(w, d).extrude(z1 - z0).edges("|Z").fillet(r)


def nub(cx, cy, z0, z1, r):
    """vial_stirrer.fs mkNub: an equilateral triangle of circumradius TRI_R, one vertex toward -y,
    grown by r all round (straight sides, R = r corners)."""
    t = C["TRI_R"]
    pts = [(cx, cy - t), (cx + t * math.sqrt(3) / 2, cy + t / 2), (cx - t * math.sqrt(3) / 2, cy + t / 2)]
    return (cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().offset2D(r, "arc")
            .extrude(z1 - z0))


def make_base(compact: bool):
    """vial_stirrer.fs makeBase, and the compact base."""
    floor, zf0, fp = C["FLOOR_T"], C["Z_FAN0"], C["FAN_PITCH"] / 2
    if compact:
        W, D, R, wall = COMPACT["W"], COMPACT["D"], COMPACT["R"], COMPACT["WALL"]
        ztop = C["Z_WALL"] - COMPACT["WALL_DROP"]
        cav = rbox(W - 2 * wall, D - 2 * wall, floor, ztop + 1, R - wall)
        dx, depth = COMPACT["BOARD_IN"], COMPACT["HOLE_DEPTH"]
    else:
        W = D = C["FOOT"]
        R, ztop = C["FOOT_R"], C["Z_WALL"]
        cav = rbox(C["CAV"], C["CAV"], floor, ztop + 1, 3.0)
        dx, depth = 0.0, 6.5
    body = rbox(W, D, 0, ztop, R).cut(cav)
    adds = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            adds.append(cyl(sx * fp, sy * fp, floor - 0.01, zf0, 4.0))                    # fan posts
            if not compact:
                adds.append(cyl(sx * C["POST"], sy * C["POST"], floor - 0.01, C["Z_WALL"], 4.0))  # corner posts
    adds += [box(-22.6 + dx, -8.9, floor - 0.01, -2.0 + dx, -7.4, floor + 0.5),        # board rails
             box(-22.6 + dx, 7.4, floor - 0.01, -2.0 + dx, 8.9, floor + 0.5),
             box(-1.6 + dx, -5.0, floor - 0.01, -0.4 + dx, 5.0, floor + 3.0)]           # board stop
    for a in adds:
        body = body.union(a)
    cuts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            cuts.append(cyl(sx * fp, sy * fp, zf0 - depth, zf0 + 1, C["INSERT_HOLE"] / 2))
            if not compact:
                cuts.append(cyl(sx * C["POST"], sy * C["POST"], C["Z_WALL"] - 6.5, C["Z_WALL"] + 1, C["INSERT_HOLE"] / 2))
    if compact:
        n0, n1 = COMPACT["NOTCH"]
        cuts.append(box(n0, -D / 2 - 1, floor - 0.6, n1, -(D / 2 - wall) + 0.5, ztop + 1))   # cable notch, -Y wall
    else:
        cuts.append(box(-W / 2 - 1, -6.5, floor - 0.6, -C["CAV"] / 2 + 0.5, 6.5, ztop + 1))  # USB-C notch, -X wall
    for k in range(3):
        z0 = zf0 + 1.5 + k * 3.0
        # vents, +-Y walls. The compact base's -Y wall has the cable notch, which would leave the
        # bars between that wall's vents attached at one end only, so it has none.
        cuts.append(box(-13, 0 if compact else -D / 2 - 1, z0, 13, D / 2 + 1, z0 + 1.6))
        cuts.append(box(0, -13, z0, W / 2 + 1, 13, z0 + 1.6))               # vents, +X wall
    cuts.append(nub(-C["KEY_X"], 0, -0.01, C["NUB_H"] + 0.1, C["POCKET_R"]))   # key pockets
    cuts.append(nub(C["KEY_X"], 0, -0.01, C["NUB_H"] + 0.1, C["POCKET_R"]))
    for c in cuts:
        body = body.cut(c)
    return body


def make_holder(compact: bool, fillets: bool = True):
    """vial_stirrer.fs makeHolder, and the compact holder."""
    zw, ft, fp = C["Z_WALL"], C["FLANGE_T"], C["FAN_PITCH"] / 2
    if compact:
        W, D, R = COMPACT["W"], COMPACT["D"], COMPACT["R"]
    else:
        W = D = C["FOOT"]
        R = C["FOOT_R"]
    body = rbox(W, D, zw, zw + ft, R).union(cyl(0, 0, zw, C["Z_TOP"], C["CUP_OD"] / 2))
    r1 = C["CUP_R0"] - (C["CUP_H"] + 1) * math.tan(math.radians(C["CUP_DRAFT"]))
    tools = [cyl(0, 0, zw - 1, C["Z_RECESS"], C["RECESS_D"] / 2),                                   # carrier recess
             cone(C["Z_VIAL"], C["Z_TOP"] + 1, C["CUP_R0"], r1),                                     # vial pocket
             box(-C["CUP_OD"], -C["CUP_SLOT"] / 2, C["Z_VIAL"] + C["CUP_RING"], C["CUP_OD"], C["CUP_SLOT"] / 2, C["Z_TOP"] + 1),
             box(-C["CUP_SLOT"] / 2, -C["CUP_OD"], C["Z_VIAL"] + C["CUP_RING"], C["CUP_SLOT"] / 2, C["CUP_OD"], C["Z_TOP"] + 1),
             box(-22.8, -2.6, zw - 1, -C["RECESS_D"] / 2 + 0.5, 2.6, C["Z_RECESS"])]                 # Hall-lead groove
    for sx in (-1, 1):
        for sy in (-1, 1):
            if compact:
                tools.append(cyl(sx * fp, sy * fp, zw - 1, zw + ft + 1, COMPACT["THRU_D"] / 2))
                tools.append(cyl(sx * fp, sy * fp, COMPACT["CBORE_SEAT"], zw + ft + 1, COMPACT["CBORE_D"] / 2))
            else:
                tools.append(cyl(sx * fp, sy * fp, zw - 1, C["Z_FAN1"] + 3.6, 3.6))                # fan-screw heads
                tools.append(cyl(sx * C["POST"], sy * C["POST"], zw - 1, zw + ft + 1, 1.7))          # corner screws
    for t in tools:
        body = body.cut(t)
    if fillets:
        body = cup_fillets(body)
    return body


def cup_fillets(body):
    """As in makeHolder: R1 round the outside of each finger tip, then R0.3 on the floor edge and the
    other finger and slot edges; the inner tip edge stays sharp."""
    zt, zv, ring = C["Z_TOP"], C["Z_VIAL"], C["CUP_RING"]
    ro, r0 = C["CUP_OD"] / 2, C["CUP_R0"]

    def mid(e):
        p = e.positionAt(0.5)
        return p.x, p.y, p.z

    tips = [e for e in body.val().Edges() if abs(mid(e)[2] - zt) < 0.01 and abs(math.hypot(*mid(e)[:2]) - ro) < 0.05]
    solid = body.val().fillet(C["CUP_TIP_R"], tips)
    before = {e.hashCode() for e in body.val().Edges()}
    picked = []
    for e in solid.Edges():
        bb = e.BoundingBox()
        x, y, z = mid(e)
        inner_tip = abs(z - zt) < 0.01 and math.hypot(x, y) < r0
        made_by_tip = abs(bb.zmin - (zt - C["CUP_TIP_R"])) < 0.02 or (abs(z - zt) < 0.01 and abs(math.hypot(x, y) - (ro - C["CUP_TIP_R"])) < 0.05)
        on_tip_round = any(f.geomType() == "TORUS" for f in solid.ancestors(e, "Face")) if hasattr(solid, "ancestors") else False
        if inner_tip or on_tip_round:
            continue
        if bb.zmin > zv + ring - 0.01 or (abs(bb.zmin - zv) < 0.01 and abs(bb.zmax - zv) < 0.01):
            picked.append(e)
    solid = solid.fillet(C["CUP_EDGE_R"], picked)
    return cq.Workplane("XY").add(solid), len(tips), len(picked)




# ---------------------------------------------------------------------------------------------
# Meshes. The holder's cup has edge rounds (R1 round each finger tip, R0.3 on the slot and finger
# edges) that OpenCascade would not fillet here, so the compact holder's STL takes everything within
# r = CUP_KEEP of the axis from the Onshape holder (stl/vial_holder.stl), which the compact layout
# leaves unchanged, and the rest from the CadQuery model. The base needs no such step.

CUP_KEEP = 16.9      # taken from Onshape inside this radius; the cup is CUP_OD / 2 = 16.7, and the compact layout
CUP_CUT = 16.8       # changes nothing inside 19 mm. The CadQuery part is used outside CUP_CUT, so the two overlap


def to_manifold(m):
    import manifold3d
    import numpy as np
    return manifold3d.Manifold(manifold3d.Mesh(vert_properties=np.asarray(m.vertices, dtype="float32"),
                                               tri_verts=np.asarray(m.faces, dtype="uint32")))


def to_trimesh(man):
    import trimesh
    mesh = man.to_mesh()
    m = trimesh.Trimesh(vertices=mesh.vert_properties[:, :3].astype(float), faces=mesh.tri_verts.astype(int), process=False)
    m.merge_vertices(digits_vertex=5)
    return m


def cq_mesh(wp, path):
    cq.exporters.export(wp, str(path), tolerance=0.02, angularTolerance=0.15)
    import trimesh
    return trimesh.load(str(path))


def compact_holder_mesh(tmp: pathlib.Path):
    import manifold3d
    flange = to_manifold(cq_mesh(make_holder(True, fillets=False), tmp / "holder_compact_cq.stl"))
    onshape = to_manifold(__import__("trimesh").load(str(ROOT / "stl" / "vial_holder.stl")))
    keep = manifold3d.Manifold.cylinder(40.0, CUP_KEEP, CUP_KEEP, 256).translate([0, 0, 10.0])
    cut = manifold3d.Manifold.cylinder(40.0, CUP_CUT, CUP_CUT, 256).translate([0, 0, 10.0])
    return to_trimesh((onshape ^ keep) + (flange - cut))


def section_dims(m, z):
    """Outer X and Y extent of a mesh's section at height z."""
    sec = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    lo, hi = sec.bounds
    return float(round(hi[0] - lo[0], 3)), float(round(hi[1] - lo[1], 3))


def main():
    import tempfile
    import trimesh
    out_stl = ROOT / "stl" / "compact"
    out_stl.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp())
    lines = []
    say = lines.append

    # 1. The port, checked: today's parts built by this script against the Onshape STLs
    say("1. This script's today's parts against the Onshape STLs (mm3; differences are tessellation, plus the cup's edge rounds)")
    for name, wp in (("base", make_base(False)), ("vial_holder", make_holder(False, fillets=False))):
        a = cq_mesh(wp, tmp / f"{name}_port.stl")
        ref = trimesh.load(str(ROOT / "stl" / f"{name}.stl"))
        A, R = to_manifold(a), to_manifold(ref)
        say(f"   {name:12s} port {a.volume:9.1f}  Onshape {ref.volume:9.1f}  port-only {(A - R).volume():6.1f}  "
            f"Onshape-only {(R - A).volume():6.1f}  bounds equal: {bool((abs(a.bounds - ref.bounds) < 0.01).all())}")

    # 2. The compact parts
    base = cq_mesh(make_base(True), out_stl / "base_compact.stl")
    holder = compact_holder_mesh(tmp)
    holder.export(str(out_stl / "vial_holder_compact.stl"))
    say("")
    say("2. Compact parts written to stl/compact/")
    for name, m in (("base_compact", base), ("vial_holder_compact", holder)):
        size = (m.bounds[1] - m.bounds[0]).round(3).tolist()
        say(f"   {name:20s} {size[0]} x {size[1]} x {size[2]} mm, z {m.bounds[0][2]:.2f} to {m.bounds[1][2]:.2f}, "
            f"{m.volume:8.1f} mm3, watertight {m.is_watertight}, {len(m.split(only_watertight=False))} body")
    ref_h = to_manifold(trimesh.load(str(ROOT / "stl" / "vial_holder.stl")))
    import manifold3d
    keep = manifold3d.Manifold.cylinder(40.0, CUP_KEEP, CUP_KEEP, 256).translate([0, 0, 10.0])
    say(f"   holder inside r = {CUP_KEEP}: {(to_manifold(holder) ^ keep).volume():.3f} mm3, Onshape's {(ref_h ^ keep).volume():.3f} mm3")

    # 3. The layout's numbers, read back off the meshes
    say("")
    say("3. Read back off the compact meshes (mm)")
    say(f"   base outside at z 10: {section_dims(base, 10.0)}; inside the walls at z 15 (fan pocket): "
        f"{tuple(round(W - 2 * COMPACT['WALL'], 3) for W in (COMPACT['W'], COMPACT['D']))} by construction")
    zt = C["Z_WALL"] - COMPACT["WALL_DROP"]
    say(f"   base wall top z {zt:.2f}, holder flange underside z {holder.bounds[0][2]:.2f}: {C['Z_WALL'] - zt:.2f} mm apart, "
        f"so the holder rests on the fan (z {C['Z_FAN1']:.2f}), through four 0.5 mm M3 washers")
    seat, top = COMPACT["CBORE_SEAT"], C["Z_WALL"] + C["FLANGE_T"]
    hole_floor = C["Z_FAN0"] - COMPACT["HOLE_DEPTH"]
    for washer in (0.5, 0.0):
        s = seat - 0.5 + washer
        say(f"   M3 x 20, {'with' if washer else 'without'} washers: head seat z {s:.2f}, tip z {s - 20:.2f}, "
            f"{s - 20 - hole_floor:.2f} above the insert hole's floor (z {hole_floor:.2f}), "
            f"{C['Z_FAN0'] - (s - 20):.2f} of thread below the insert's top (insert {C['INSERT_L']})")
    say(f"   counterbores Ø{COMPACT['CBORE_D']} x {top - seat:.1f} deep at (+-{C['FAN_PITCH'] / 2:.0f}, +-{C['FAN_PITCH'] / 2:.0f}); "
        f"through holes Ø{COMPACT['THRU_D']}")
    (ROOT / "compact" / "check_output.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
