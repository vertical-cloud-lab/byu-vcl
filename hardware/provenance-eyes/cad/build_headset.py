"""Build and render the Provenance Eyes headset in Blender.

    blender -b --factory-startup -P build_headset.py -- [--quick] [--views a,b] [--no-stl]

Geometry, positions and masses come from layout.py, which mass_budget.py also
reads, so the renders and the balance numbers always describe the same layout.
Writes PNGs to ../img/ and the device (no head) as ../stl/headset-assembly.stl.
"""

import math
import os
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as L  # noqa: E402

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
QUICK = "--quick" in ARGS
EXPORT_STL = "--no-stl" not in ARGS
VIEWS = None
if "--views" in ARGS:
    VIEWS = ARGS[ARGS.index("--views") + 1].split(",")
IMG = os.path.normpath(os.path.join(HERE, "..", "img"))
STL = os.path.normpath(os.path.join(HERE, "..", "stl"))
os.makedirs(IMG, exist_ok=True)
os.makedirs(STL, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

DEVICE = []      # objects exported to STL
SHELLS = []      # pod shells that go see-through in the x-ray views
MARKERS = []     # centre-of-mass markers, side view only


# ----------------------------------------------------------------------------- materials
def material(name, color, rough=0.5, metal=0.0, emit=None, strength=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit is not None:
        bsdf.inputs["Emission Color"].default_value = (*emit, 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    if coat:
        bsdf.inputs["Coat Weight"].default_value = coat
    m.diffuse_color = (*color, 1.0)
    return m


MAT = dict(
    skin=material("mannequin", (0.80, 0.74, 0.68), rough=0.65),
    band=material("headband", (0.035, 0.037, 0.04), rough=0.55),
    pad=material("sweatband", (0.10, 0.10, 0.11), rough=0.9),
    ratchet=material("ratchet", (0.02, 0.02, 0.022), rough=0.4),
    knob=material("knob", (0.85, 0.32, 0.05), rough=0.45),
    pod=material("pod-PETG", (0.10, 0.33, 0.62), rough=0.35, coat=0.3),
    lens=material("lens-barrel", (0.01, 0.01, 0.012), rough=0.25),
    glass=material("lens-glass", (0.02, 0.05, 0.10), rough=0.02, metal=0.6, coat=1.0),
    led=material("rec-LED", (0.9, 0.02, 0.02), rough=0.2, emit=(1.0, 0.05, 0.03), strength=25.0),
    button=material("button", (0.95, 0.42, 0.05), rough=0.4),
    ribbon=material("camera-ribbon", (0.82, 0.83, 0.85), rough=0.5),
    wire=material("wire", (0.03, 0.03, 0.03), rough=0.45),
    pcb=material("pcb-green", (0.03, 0.30, 0.10), rough=0.4),
    pcb_dark=material("pcb-black", (0.03, 0.03, 0.035), rough=0.4),
    chip=material("chip", (0.55, 0.56, 0.58), rough=0.3, metal=0.8),
    cell=material("lipo", (0.62, 0.66, 0.72), rough=0.35, metal=0.5),
    marker_com=material("marker-com", (0.85, 0.05, 0.55), rough=0.3, emit=(0.85, 0.05, 0.55), strength=2.0),
    marker_ear=material("marker-ear", (0.25, 0.25, 0.28), rough=0.5),
    marker_tot=material("marker-total", (0.35, 0.10, 0.75), rough=0.3, emit=(0.35, 0.10, 0.75), strength=1.5),
)


# ----------------------------------------------------------------------------- mesh helpers
def link(ob):
    scene.collection.objects.link(ob)
    return ob


def smooth(ob):
    try:
        ob.data.shade_smooth()
    except Exception:
        for p in ob.data.polygons:
            p.use_smooth = True


def make_mesh(name, verts, faces, mat, device=True, recalc=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.validate()
    if recalc:
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()
    me.update()
    ob = link(bpy.data.objects.new(name, me))
    ob.data.materials.append(mat)
    if device:
        DEVICE.append(ob)
    return ob


def bevel(ob, width, segments=3, angle=None):
    mod = ob.modifiers.new("bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    if angle is not None:
        mod.limit_method = "ANGLE"
        mod.angle_limit = math.radians(angle)
    else:
        mod.limit_method = "NONE"
    try:
        mod.harden_normals = True
    except Exception:
        pass
    smooth(ob)
    return ob


def frame_matrix(center, ax, ay, az):
    R = Matrix((tuple(ax), tuple(ay), tuple(az))).transposed()
    return Matrix.Translation(Vector(center)) @ R.to_4x4()


def box(name, center, size, axes, mat, round_=0.0015, device=True):
    hx, hy, hz = (s / 2 for s in size)
    v = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
         (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    ob = make_mesh(name, v, f, mat, device)
    ob.matrix_world = frame_matrix(center, *axes)
    if round_:
        bevel(ob, round_, 3)
    return ob


def cylinder(name, center, radius, length, axis, mat, n=48, round_=0.0, device=True):
    v = []
    for z in (-length / 2, length / 2):
        for i in range(n):
            a = 2 * math.pi * i / n
            v.append((radius * math.cos(a), radius * math.sin(a), z))
    f = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    f += [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    ob = make_mesh(name, v, f, mat, device)
    az = Vector(axis).normalized()
    helper = Vector((0, 0, 1)) if abs(az.z) < 0.9 else Vector((1, 0, 0))
    ax = helper.cross(az).normalized()
    ay = az.cross(ax)
    ob.matrix_world = frame_matrix(center, ax, ay, az)
    if round_:
        bevel(ob, round_, 2, angle=40)
    else:
        smooth(ob)
    return ob


def sweep(name, frames, out, height, closed, mat, round_=0.0, device=True):
    """Rectangular section swept along frames [(inner point, outward dir, up dir)]."""
    v = []
    for p, d, u in frames:
        p, d, u = Vector(p), Vector(d), Vector(u)
        v += [p - u * height / 2, p + d * out - u * height / 2, p + d * out + u * height / 2, p + u * height / 2]
    n = len(frames)
    f = []
    for i in range(n if closed else n - 1):
        a, b = 4 * i, 4 * ((i + 1) % n)
        for k in range(4):
            k2 = (k + 1) % 4
            f.append((a + k, b + k, b + k2, a + k2))
    if not closed:
        f.append((3, 2, 1, 0))
        e = 4 * (n - 1)
        f.append((e, e + 1, e + 2, e + 3))
    ob = make_mesh(name, v, f, mat, device)
    if round_:
        bevel(ob, round_, 3, angle=50)
    else:
        smooth(ob)
    return ob


def tube(name, points, radius, mat, device=True):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (*p, 1.0)
    ob = link(bpy.data.objects.new(name, cu))
    ob.data.materials.append(mat)
    if device:
        DEVICE.append(ob)
    return ob


def ellipsoid(name, center, semi, mat, rot=None, seg=64, rings=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=1.0)
    ob = bpy.context.active_object
    ob.name = name
    M = Matrix.Diagonal((*semi, 1.0))
    if rot is not None:
        M = rot.to_4x4() @ M
    ob.data.transform(M)
    ob.location = center
    ob.data.materials.append(mat)
    return ob


# ----------------------------------------------------------------------------- head form
def build_head():
    parts = [
        ellipsoid("cranium", L.HEAD_CENTER, L.HEAD_SEMI_AXES, MAT["skin"]),
        ellipsoid("face", (0.040, 0.0, -0.048), (0.060, 0.056, 0.076), MAT["skin"]),
        ellipsoid("nose", (0.099, 0.0, -0.020), (0.017, 0.012, 0.028), MAT["skin"],
                  rot=Matrix.Rotation(math.radians(-12), 3, "Y")),
        ellipsoid("brow", (0.085, 0.0, 0.012), (0.020, 0.058, 0.014), MAT["skin"]),
        ellipsoid("ear_l", (-0.004, 0.074, -0.002), (0.015, 0.009, 0.030), MAT["skin"]),
        ellipsoid("ear_r", (-0.004, -0.074, -0.002), (0.015, 0.009, 0.030), MAT["skin"]),
    ]
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1.0, depth=0.13, location=(-0.012, 0.0, -0.125))
    neck = bpy.context.active_object
    neck.data.transform(Matrix.Diagonal((0.058, 0.055, 1.0, 1.0)))
    neck.data.materials.append(MAT["skin"])
    parts.append(neck)
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    head = bpy.context.active_object
    head.name = "head-form"
    rm = head.modifiers.new("remesh", "REMESH")
    rm.mode = "VOXEL"
    rm.voxel_size = 0.0025 if not QUICK else 0.004
    try:
        rm.use_smooth_shade = True
    except Exception:
        pass
    sm = head.modifiers.new("smooth", "SMOOTH")
    sm.factor = 0.8
    sm.iterations = 12
    smooth(head)
    return head


# ----------------------------------------------------------------------------- headband
def build_headband():
    t = L.BAND["thickness"]
    h = L.BAND["height"]
    _, _, _, w = L.band_frame()
    N = 240
    frames = [(L.band_point(2 * math.pi * i / N), L.band_dir(2 * math.pi * i / N), w) for i in range(N)]
    sweep("band", frames, t, h, True, MAT["band"], round_=0.0012)
    # Sweatband on the forehead: a softer strip on the inside, front half only.
    pad = [(L.band_point(a, 0.0, -0.0015), L.band_dir(a), w)
           for a in [math.radians(x) for x in range(-60, 61, 2)]]
    sweep("sweatband", pad, 0.0018, h * 0.9, False, MAT["pad"], round_=0.0006)
    # Crown strap, ear to ear over the top.
    _, _, _, n = L.crown_frame()
    cf = []
    for i in range(121):
        a = math.radians(-86 + 172 * i / 120)
        p, d = L.crown_point(a)
        cf.append((p, d, n))
    sweep("crown-strap", cf, L.CROWN["thickness"], L.CROWN["width"], False, MAT["band"], round_=0.0008)
    top, d = L.crown_point(0.0, out=L.CROWN["thickness"])
    box("crown-buckle", Vector(top) + Vector(d) * 0.002, (0.004, 0.030, 0.026),
        (d, (0, 1, 0), n), MAT["ratchet"], round_=0.0015)
    # Ratchet housing and knob at the back.
    th = math.pi
    d = Vector(L.band_dir(th))
    tg = Vector(L.band_tangent(th))
    c = Vector(L.band_point(th, 0.0, t + 0.005))
    box("ratchet-housing", c, (0.010, 0.064, 0.032), (d, tg, w), MAT["ratchet"], round_=0.004)
    cylinder("ratchet-knob", c + d * 0.011, 0.017, 0.012, d, MAT["knob"], round_=0.002)
    for k in range(16):  # grip ridges
        a = 2 * math.pi * k / 16
        off = tg * math.cos(a) * 0.017 + Vector(w) * math.sin(a) * 0.017
        box(f"knob-ridge-{k}", c + d * 0.011 + off, (0.011, 0.003, 0.003), (d, tg, w), MAT["knob"], round_=0.0008)


# ----------------------------------------------------------------------------- pods
def build_front_pod():
    t = L.BAND["thickness"]
    _, u, _, w = L.band_frame()
    w = Vector(w)
    d0 = Vector(L.band_dir(0.0))
    tg = Vector(L.band_tangent(0.0))
    bx, by, bz = L.FRONT_POD["base"]
    base_c = Vector(L.band_point(0.0, 0.0, t + bx / 2))
    SHELLS.append(box("pi-enclosure", base_c, (bx, by, bz), (d0, tg, w), MAT["pod"], round_=0.004))
    for k in range(6):  # vents on top, over the heatsink
        box(f"front-vent-{k}", base_c + w * (bz / 2 + 0.0001) + tg * (-0.015 + 0.006 * k) + d0 * 0.001,
            (0.007, 0.0028, 0.0012), (d0, tg, w), MAT["lens"], round_=0.0005)
    # Camera head, hinged on the enclosure and tilted down.
    tilt = math.radians(L.FRONT_POD["tilt_deg"])
    ax = Vector((math.cos(tilt), 0.0, -math.sin(tilt)))
    ay = Vector((0.0, 1.0, 0.0))
    az = ax.cross(ay)
    hx, hy, hz = L.FRONT_POD["head"]
    hinge = base_c + d0 * (bx / 2 + 0.003) - w * (bz / 2 - 0.007)
    head_c = hinge + ax * (hx / 2 + 0.001) + az * (hz / 2 - 0.007)
    SHELLS.append(box("camera-head", head_c, (hx, hy, hz), (ax, ay, az), MAT["pod"], round_=0.0045))
    for side in (-1, 1):  # hinge knuckles on the enclosure, pin through the head
        cylinder(f"knuckle-{side}", hinge + ay * side * (hy / 2 + 0.003), 0.0045, 0.005, ay, MAT["pod"], round_=0.001)
        cylinder(f"hinge-screw-{side}", hinge + ay * side * (hy / 2 + 0.0058), 0.0028, 0.0012, ay, MAT["chip"])
    front = head_c + ax * (hx / 2)
    lens_c = front + az * 0.002
    cylinder("lens-barrel", lens_c + ax * 0.002, 0.0062, 0.005, ax, MAT["lens"], round_=0.0008)
    cylinder("lens-glass", lens_c + ax * 0.0047, 0.0036, 0.0008, ax, MAT["glass"])
    cylinder("rec-led", front + ax * 0.0006 - ay * 0.011 + az * 0.009, 0.0019, 0.0016, ax, MAT["led"])
    # Inside (x-ray views): Pi Zero 2 W, its heatsink, the camera board.
    box("pi-zero-2w", base_c - d0 * 0.002, (0.0014, 0.065, 0.030), (d0, tg, w), MAT["pcb"], 0, device=False)
    box("rp3a0", base_c - d0 * 0.0006 + tg * 0.004, (0.0013, 0.014, 0.014), (d0, tg, w), MAT["chip"], 0, device=False)
    box("heatsink", base_c + d0 * 0.0028 + tg * 0.004, (0.006, 0.014, 0.014), (d0, tg, w), MAT["lens"], 0, device=False)
    box("microsd", base_c - d0 * 0.002 + tg * 0.031, (0.0012, 0.011, 0.008), (d0, tg, w), MAT["chip"], 0, device=False)
    box("cam-pcb", head_c + ax * 0.001 + az * 0.002, (0.0012, 0.024, 0.025), (ax, ay, az), MAT["pcb"], 0, device=False)
    box("cam-holder", head_c + ax * 0.0045 + az * 0.002, (0.005, 0.0085, 0.0085), (ax, ay, az), MAT["lens"], 0, device=False)
    return head_c, ax


def build_temple_pods():
    t = L.BAND["thickness"]
    _, _, _, w = L.band_frame()
    th = math.radians(L.TEMPLE_POD_THETA_DEG)
    out = {}
    for side, ang, spec in (("left", th, L.TEMPLE_POD), ("right", -th, L.TEMPLE_POD_RIGHT)):
        sx, sy, sz = spec["size"]
        d = Vector(L.band_dir(ang))
        tg = Vector(L.band_tangent(ang))
        fwd = tg if tg.x > 0 else -tg
        c = Vector(L.band_point(ang, 0.0, t + sx / 2))
        SHELLS.append(box(f"temple-pod-{side}", c, (sx, sy, sz), (d, tg, Vector(w)), MAT["pod"], round_=0.0035))
        port = c + d * (sx / 2) + fwd * (sy / 2 - 0.006)
        cylinder(f"mic-port-{side}", port, 0.0013, 0.0012, d, MAT["lens"])
        box(f"mic-pcb-{side}", c + fwd * (sy / 2 - 0.009), (0.0016, 0.0127, 0.0120), (d, tg, Vector(w)),
            MAT["pcb_dark"], 0, device=False)
        if side == "right":
            cylinder("record-button", c + d * (sx / 2 + 0.0014) - fwd * 0.004, 0.0062, 0.0030, d, MAT["button"], round_=0.0009)
            cylinder("haptic-motor", c - fwd * 0.012, 0.005, 0.0027, d, MAT["chip"], device=False)
        out[side] = c
    return out


def rear_pod_mesh(spec):
    """Curved shell (annular sector) in a local frame: inner face centre at origin, outward = -x."""
    r_in, depth, width, height = spec["r_in"], spec["depth"], spec["width"], spec["height"]
    span = width / (r_in + depth / 2)
    n = 36
    v = []
    for i in range(n + 1):
        phi = math.pi - span / 2 + span * i / n
        for r, z in ((r_in, -height / 2), (r_in + depth, -height / 2), (r_in + depth, height / 2), (r_in, height / 2)):
            v.append((r_in + r * math.cos(phi), r * math.sin(phi), z))
    f = []
    for i in range(n):
        a, b = 4 * i, 4 * (i + 1)
        for k in range(4):
            k2 = (k + 1) % 4
            f.append((a + k, b + k, b + k2, a + k2))
    f.append((3, 2, 1, 0))
    e = 4 * n
    f.append((e, e + 1, e + 2, e + 3))
    return v, f


def build_rear_pod(battery="pisugar3"):
    spec = L.REAR_POD
    inner, lean = L.rear_pod_frame()
    M = Matrix.Translation(Vector(inner)) @ Matrix.Rotation(lean, 4, "Y")
    v, f = rear_pod_mesh(spec)
    pod = make_mesh("rear-pod", v, f, MAT["pod"])
    pod.matrix_world = M
    bevel(pod, 0.004, 4, angle=40)
    SHELLS.append(pod)

    def at(x, y, z):
        return M @ Vector((x, y, z))

    ax = (M.to_3x3() @ Vector((-1, 0, 0))).normalized()   # outward
    ay = (M.to_3x3() @ Vector((0, 1, 0))).normalized()
    az = (M.to_3x3() @ Vector((0, 0, 1))).normalized()
    depth, height = spec["depth"], spec["height"]
    # USB-C charge port and PiSugar button on the underside.
    box("usb-c", at(-depth * 0.55, 0.012, -height / 2 - 0.0002), (0.0035, 0.009, 0.0012), (ax, ay, az), MAT["lens"], round_=0.0005)
    cylinder("power-button", at(-depth * 0.55, -0.014, -height / 2 - 0.0008), 0.0025, 0.0015, -az, MAT["button"])
    # Bracket legs down to the band's top edge, either side of the ratchet.
    t = L.BAND["thickness"]
    _, _, _, w = L.band_frame()
    for side in (-1, 1):
        ang = math.pi - side * 0.32
        top = Vector(L.band_point(ang, L.BAND["height"] / 2 - 0.004, t / 2))
        foot = at(-0.006, side * 0.028, -height / 2 + 0.004)
        mid = (top + foot) / 2
        up = (foot - top).normalized()
        dvec = Vector(L.band_dir(ang))
        sidev = up.cross(dvec).normalized()
        box(f"bracket-{'l' if side > 0 else 'r'}", mid, (0.005, 0.010, (foot - top).length + 0.010),
            (dvec, sidev, up), MAT["pod"], round_=0.0015)
    # Inside (x-ray): the LiPo cell against the head side, the PiSugar 3 board outside it.
    b = L.BATTERY_OPTIONS[battery]
    if b["cell"]:
        cx, cy, cz = b["cell"]
        box("lipo-cell", at(-0.0005 - cx / 2, 0.0, 0.0), (cx, cy, cz), (ax, ay, az), MAT["cell"], round_=0.0015, device=False)
        box("pisugar-pcb", at(-0.0088, 0.0, 0.0), (0.0016, 0.065, 0.030), (ax, ay, az), MAT["pcb_dark"], 0, device=False)
    return at(-depth / 2, 0, 0)


# ----------------------------------------------------------------------------- cables
def build_cables():
    t = L.BAND["thickness"]
    _, _, _, w = L.band_frame()
    th = int(L.TEMPLE_POD_THETA_DEG)

    def run(name, degs, s_, r, mat):
        pts = [L.band_point(math.radians(x), s_, t + r + 0.0002) for x in degs]
        tube(name, pts, r, mat)

    run("cable-power-i2c", range(24, 157, 2), -0.0065, 0.0016, MAT["wire"])        # front pod to battery, left side
    run("wire-left-mic", range(th - 9, 23, -2), 0.0065, 0.0010, MAT["wire"])        # left temple to front pod
    run("wire-right-bundle", range(-(th - 11), -23, 2), 0.0, 0.0014, MAT["wire"])   # right temple to front pod
    for deg in (45, 110, 140, -45):  # cable clips
        a = math.radians(deg)
        d = Vector(L.band_dir(a))
        tg = Vector(L.band_tangent(a))
        box(f"clip-{deg}", Vector(L.band_point(a, 0.0, t + 0.0018)), (0.0036, 0.006, L.BAND["height"] + 0.003),
            (d, tg, Vector(w)), MAT["ratchet"], round_=0.001)


# ----------------------------------------------------------------------------- markers
def build_markers(battery="pisugar3"):
    _, dev = L.centre_of_mass(L.components(battery, with_headgear=False))
    _, tot = L.centre_of_mass(L.components(battery, with_headgear=True))
    y = 0.098  # drawn just outside the left side of the head, as projections

    def line_and_ball(name, x, z, mat, r, dy):
        MARKERS.append(cylinder(name + "-line", (x, y + dy, 0.055), 0.0009, 0.23, (0, 0, 1), mat, device=False))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y + dy, z))
        s = bpy.context.active_object
        s.data.materials.append(mat)
        MARKERS.append(s)

    line_and_ball("ear", 0.0, 0.0, MAT["marker_ear"], 0.0045, 0.0)
    line_and_ball("com-device", dev[0], dev[2], MAT["marker_com"], 0.0062, 0.002)
    line_and_ball("com-total", tot[0], tot[2], MAT["marker_tot"], 0.0055, 0.004)
    return dev, tot


# ----------------------------------------------------------------------------- scene
def setup_world():
    world = bpy.data.worlds.new("world")
    scene.world = world
    try:
        world.use_nodes = True
    except Exception:
        pass
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.94, 0.95, 0.97, 1.0)
    bg.inputs[1].default_value = 0.75

    def area(name, loc, size, energy):
        ld = bpy.data.lights.new(name, "AREA")
        ld.size = size
        ld.energy = energy
        ob = link(bpy.data.objects.new(name, ld))
        ob.location = loc
        ob.rotation_euler = (Vector((0, 0, 0.02)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()

    area("key", (1.0, 0.9, 1.1), 0.9, 38)
    area("fill", (0.6, -1.1, 0.3), 1.2, 14)
    area("rim", (-1.1, 0.2, 0.9), 0.8, 28)
    area("rim2", (-0.8, -0.9, 0.6), 0.8, 16)

    r = scene.render
    r.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24 if QUICK else 96
    try:
        scene.cycles.use_denoising = True
    except Exception:
        pass
    r.resolution_x = 800 if QUICK else 1500
    r.resolution_y = 600 if QUICK else 1125
    r.film_transparent = False
    try:
        scene.view_settings.view_transform = "AgX"
    except Exception:
        pass

    cam = link(bpy.data.objects.new("camera", bpy.data.cameras.new("camera")))
    cam.data.lens = 70
    scene.camera = cam
    return cam


def look(cam, direction, dist, target=(0.0, 0.0, -0.005), lens=70):
    tgt = Vector(target)
    loc = tgt + Vector(direction).normalized() * dist
    cam.location = loc
    cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens


def set_xray(on):
    for ob in SHELLS:
        ob.hide_render = False
        if on:
            m = ob.data.materials[0]
            ob.data.materials[0] = XRAY
        else:
            ob.data.materials[0] = MAT["pod"]


def render(name):
    path = os.path.join(IMG, f"{name}.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("wrote", path)


# ----------------------------------------------------------------------------- build
head = build_head()
build_headband()
build_front_pod()
build_temple_pods()
build_rear_pod()
build_cables()
dev, tot = build_markers()
print("device centre of mass (m):", tuple(round(c, 4) for c in dev))
print("device + headgear centre of mass (m):", tuple(round(c, 4) for c in tot))

XRAY = bpy.data.materials.new("pod-xray")
try:
    XRAY.use_nodes = True
except Exception:
    pass
_nodes = XRAY.node_tree.nodes
_bsdf = next(n for n in _nodes if n.type == "BSDF_PRINCIPLED")
_bsdf.inputs["Base Color"].default_value = (0.25, 0.55, 0.95, 1.0)
_bsdf.inputs["Roughness"].default_value = 0.2
_bsdf.inputs["Alpha"].default_value = 0.22

cam = setup_world()
views = {
    "headset-front-left": dict(direction=(0.80, 0.62, 0.30), dist=1.05),
    "headset-side-balance": dict(direction=(0.0, 1.0, 0.02), dist=1.10, lens=70, markers=True),
    "headset-rear-right": dict(direction=(-0.78, -0.60, 0.40), dist=1.05),
    "headset-xray-rear": dict(direction=(-0.70, 0.55, 0.45), dist=0.62, target=(-0.07, 0.0, 0.03), xray=True),
    "headset-xray-front": dict(direction=(0.80, -0.50, 0.25), dist=0.55, target=(0.07, 0.0, 0.03), xray=True),
}
for name, v in views.items():
    if VIEWS and name not in VIEWS:
        continue
    for m in MARKERS:
        m.hide_render = not v.get("markers", False)
    set_xray(v.get("xray", False))
    look(cam, v["direction"], v["dist"], v.get("target", (0.0, 0.0, -0.005)), v.get("lens", 70))
    render(name)
set_xray(False)

if EXPORT_STL:
    for m in MARKERS:
        m.hide_set(True)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in DEVICE:
        if ob.type == "CURVE":
            bpy.context.view_layer.objects.active = ob
            ob.select_set(True)
            bpy.ops.object.convert(target="MESH")
            ob.select_set(False)
    for ob in DEVICE:
        if ob.name in bpy.context.view_layer.objects:
            ob.select_set(True)
    path = os.path.join(STL, "headset-assembly.stl")
    try:
        bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True, global_scale=1000.0, apply_modifiers=True)
    except Exception as exc:  # older Blender
        print("wm.stl_export failed:", exc)
        bpy.ops.export_mesh.stl(filepath=path, use_selection=True, global_scale=1000.0)
    print("wrote", path)
