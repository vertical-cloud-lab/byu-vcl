"""Build and render the Provenance Eyes headset in Blender.

    blender -b --factory-startup -P build_headset.py -- [--layout v2|v1] [--quick] [--views a,b] [--no-stl]

Geometry, positions and masses come from layout.py, which mass_budget.py also
reads, so the renders and the balance numbers always describe the same layout.
Writes PNGs to ../img/ and the device (no head) as ../stl/headset-assembly.stl.

The scene also has context that is not part of the device: a generic full-face
respirator (facepiece, two filters, exhalation valve, four-strap harness and pad),
a lab coat collar and shoulders, and a bench for the camera's-eye view. The script
checks the device against them and writes the numbers to respirator_check.md.
"""

import math
import os
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as L  # noqa: E402

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
QUICK = "--quick" in ARGS
EXPORT_STL = "--no-stl" not in ARGS
VIEWS = None
if "--views" in ARGS:
    VIEWS = ARGS[ARGS.index("--views") + 1].split(",")
LAYOUT = ARGS[ARGS.index("--layout") + 1] if "--layout" in ARGS else "v2"
L.use(LAYOUT)
IMG = os.path.normpath(os.path.join(HERE, "..", "img"))
STL = os.path.normpath(os.path.join(HERE, "..", "stl"))
os.makedirs(IMG, exist_ok=True)
os.makedirs(STL, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

DEVICE = []      # objects exported to STL
SHELLS = []      # pod shells that go see-through in the x-ray views
MARKERS = []     # centre-of-mass markers, side view only
RESP = []        # full-face respirator (context)
COAT = []        # lab coat shoulders and collar (context)
BENCH = []       # bench, arms and glassware for the camera's-eye view (context)


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
    rubber=material("respirator-rubber", (0.045, 0.047, 0.05), rough=0.6),
    strap=material("harness-strap", (0.03, 0.03, 0.032), rough=0.7),
    filt=material("P100-filter", (0.78, 0.10, 0.45), rough=0.5),
    coat=material("lab-coat", (0.90, 0.91, 0.92), rough=0.85),
    bench=material("benchtop", (0.09, 0.09, 0.10), rough=0.35),
    glove=material("nitrile", (0.18, 0.36, 0.85), rough=0.55),
    paper=material("paper", (0.93, 0.92, 0.88), rough=0.9),
    liquid_a=material("liquid-a", (0.85, 0.35, 0.05), rough=0.1),
    liquid_b=material("liquid-b", (0.05, 0.45, 0.70), rough=0.1),
)


def clear_material(name, color, alpha=1.0):
    m = material(name, color, rough=0.03, coat=0.5)
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    for key in ("Transmission Weight", "Transmission"):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = 1.0
            break
    bsdf.inputs["IOR"].default_value = 1.50
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
    return m


MAT["visor"] = clear_material("visor-polycarbonate", (0.92, 0.95, 0.97), alpha=0.35)
MAT["beaker"] = clear_material("beaker-glass", (0.95, 0.97, 0.98), alpha=0.5)


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
    f = L.front_pod_frames()
    w = Vector(f["w"])
    d0 = Vector(f["d0"])
    tg = Vector(f["tg"])
    bx, by, bz = L.FRONT_POD["base"]
    base_c = Vector(f["base"])
    SHELLS.append(box("pi-enclosure", base_c, (bx, by, bz), (d0, tg, w), MAT["pod"], round_=0.004))
    for k in range(6):  # vents on top, over the heatsink
        box(f"front-vent-{k}", base_c + w * (bz / 2 + 0.0001) + tg * (-0.015 + 0.006 * k) + d0 * 0.001,
            (0.007, 0.0028, 0.0012), (d0, tg, w), MAT["lens"], round_=0.0005)
    # Camera head, hinged and tilted down. In v2 a printed brim carries the hinge forward.
    ax, ay, az = Vector(f["ax"]), Vector(f["ay"]), Vector(f["az"])
    hx, hy, hz = L.FRONT_POD["head"]
    root, hinge, head_c = Vector(f["root"]), Vector(f["hinge"]), Vector(f["head"])
    brim = L.FRONT_POD["brim"]
    if brim:
        fwd = Vector((1.0, 0.0, 0.0))
        side = Vector((0.0, 1.0, 0.0))
        for s in (-1, 1):
            arm = root + fwd * (brim / 2) + side * s * (hy / 2 + 0.003)
            box(f"brim-arm-{s}", arm, (brim + 0.010, 0.005, 0.009), (fwd, side, fwd.cross(side)),
                MAT["pod"], round_=0.0015)
        cylinder("brim-root-pin", root, 0.0035, hy + 0.012, ay, MAT["pod"], round_=0.0008)
    SHELLS.append(box("camera-head", head_c, (hx, hy, hz), (ax, ay, az), MAT["pod"], round_=0.0045))
    for side in (-1, 1):  # hinge knuckles, pin through the head
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


# ----------------------------------------------------------------------------- context: respirator, coat, bench
# A generic elastomeric full-face respirator, sized like a medium facepiece: the seal
# runs across the mid-forehead, down the temples in front of the ears and under the
# chin; a polycarbonate visor stands about 3 cm off the eyes; two P100 filters sit on
# the cheeks; four straps run to a pad high on the back of the head. Not any one model.
FACE = dict(axis_x=0.020, z_top=0.075, z_bot=-0.128, phi_max=math.radians(62.0), p=4.0,
            rim=0.004, shell=0.003, dome_c=(0.030, 0.0, -0.030), dome_r=(0.105, 0.088, 0.128),
            pad_elev_deg=30.0)
FACE_ZC = 0.5 * (FACE["z_top"] + FACE["z_bot"])
FACE_HZ = 0.5 * (FACE["z_top"] - FACE["z_bot"])


def world_tree(objs):
    """One BVH of the world-space triangles of objs (evaluated, modifiers applied)."""
    dg = bpy.context.evaluated_depsgraph_get()
    verts, polys = [], []
    for ob in objs:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        M = ob.matrix_world
        base = len(verts)
        verts += [M @ v.co for v in me.vertices]
        polys += [[base + i for i in p.vertices] for p in me.polygons]
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys), verts


def smax(a, b, k=0.008):
    h = max(k - abs(a - b), 0.0) / k
    return max(a, b) + h * h * k * 0.25


def smoothstep(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def face_norm(phi, z):
    p = FACE["p"]
    return (abs(phi / FACE["phi_max"]) ** p + abs((z - FACE_ZC) / FACE_HZ) ** p) ** (1.0 / p)


def face_outer(tree, phi, z, r=None):
    """Outer surface of the facepiece along a horizontal ray from the axis at height z."""
    o = Vector((FACE["axis_x"], 0.0, z))
    d = Vector((math.cos(phi), math.sin(phi), 0.0))
    hit = tree.ray_cast(o, d, 0.5)
    t_head = hit[3] if hit[0] is not None else 0.08
    t_dome = L.ray_ellipsoid(tuple(o), tuple(d), FACE["dome_c"], FACE["dome_r"])
    r = face_norm(phi, z) if r is None else r
    seal = t_head + FACE["rim"]
    s = smoothstep(0.78, 1.0, r)
    t = smax(seal, t_dome) * (1 - s) + seal * s
    return o + d * t, d


def build_respirator(head):
    tree, _ = world_tree([head])
    p, NR, NA = FACE["p"], 44, 192
    verts, rr, ss = [], [], []
    c, _ = face_outer(tree, 0.0, FACE_ZC, 0.0)
    verts.append(c); rr.append(0.0); ss.append(1.0)
    for k in range(1, NR + 1):
        r = 1.0 - (1.0 - k / NR) ** 1.35
        for j in range(NA):
            a = 2 * math.pi * j / NA
            R = (abs(math.cos(a)) ** p + abs(math.sin(a)) ** p) ** (-1.0 / p)
            phi = FACE["phi_max"] * R * r * math.cos(a)
            z = FACE_ZC + FACE_HZ * R * r * math.sin(a)
            P, _ = face_outer(tree, phi, z, r)
            verts.append(P); rr.append(r); ss.append(math.sin(a))
    faces = [(0, 1 + j, 1 + (j + 1) % NA) for j in range(NA)]
    for k in range(NR - 1):
        a0, b0 = 1 + k * NA, 1 + (k + 1) * NA
        for j in range(NA):
            j2 = (j + 1) % NA
            faces.append((a0 + j, b0 + j, b0 + j2, a0 + j2))
    ob = make_mesh("facepiece", verts, faces, MAT["rubber"], device=False)
    ob.data.materials.append(MAT["visor"])
    # Visor: everything inside r = 0.8 above two lines running out and down from the nose,
    # so its edges follow the mesh instead of cutting across it in steps.
    for poly in ob.data.polygons:
        if max(rr[i] for i in poly.vertices) <= 0.80 + 1e-6 and min(ss[i] for i in poly.vertices) > -0.27:
            poly.material_index = 1
    sol = ob.modifiers.new("shell", "SOLIDIFY")
    sol.thickness = FACE["shell"]
    sol.offset = 0.0
    smooth(ob)
    RESP.append(ob)
    # Filters on the cheeks, exhalation valve cover at the front.
    for s in (1, -1):
        P, d = face_outer(tree, s * math.radians(42), -0.070)
        axis = Vector((math.cos(math.radians(60)), s * math.sin(math.radians(60)), -0.25)).normalized()
        RESP.append(cylinder(f"filter-mount-{s}", P + axis * 0.004, 0.020, 0.014, axis, MAT["rubber"], device=False))
        RESP.append(cylinder(f"filter-{s}", P + axis * 0.019, 0.033, 0.020, axis, MAT["filt"], round_=0.004, device=False))
    P, d = face_outer(tree, 0.0, -0.092)
    vd = Vector((math.cos(math.radians(18)), 0.0, -math.sin(math.radians(18))))
    RESP.append(box("exhalation-valve", P + vd * 0.010, (0.020, 0.044, 0.036),
                    (vd, Vector((0, 1, 0)), vd.cross(Vector((0, 1, 0)))), MAT["rubber"], round_=0.006, device=False))
    # Harness: pad high on the back of the head, two upper and two lower straps.
    C = Vector(L.HEAD_CENTER)

    def surf(direction, off):
        dd = Vector(direction).normalized()
        hit = tree.ray_cast(C, dd, 0.5)
        return hit[0] + hit[1] * off, hit[1]

    e = math.radians(FACE["pad_elev_deg"])
    pad_c, pad_n = surf((-math.cos(e), 0.0, math.sin(e)), 0.004)
    yv = Vector((0.0, 1.0, 0.0))
    up = pad_n.cross(yv).normalized()
    if up.z < 0:
        up = -up
    rot = Matrix((tuple(pad_n), tuple(yv), tuple(up))).transposed()
    pad = ellipsoid("harness-pad", pad_c, (0.004, 0.045, 0.036), MAT["strap"], rot=rot)
    RESP.append(pad)

    def edge_point(s, z):
        lo, hi = 0.0, FACE["phi_max"] * 1.2
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if face_norm(mid, z) < 0.985 else (lo, mid)
        P, _ = face_outer(tree, s * lo, z)
        return P

    def strap(name, pts, n_each=24):
        path = []
        for a, b in zip(pts[:-1], pts[1:]):
            da, db = (a - C).normalized(), (b - C).normalized()
            ang = da.angle(db)
            for i in range(n_each):
                t = i / n_each
                dd = (da * math.sin((1 - t) * ang) + db * math.sin(t * ang)) / max(math.sin(ang), 1e-6)
                path.append(surf(dd, 0.0035))
        path.append(surf((pts[-1] - C), 0.0035))
        frames = []
        for i, (q, n) in enumerate(path):
            q2 = path[min(i + 1, len(path) - 1)][0]
            q1 = path[max(i - 1, 0)][0]
            tan = (q2 - q1).normalized()
            u = n.cross(tan).normalized()
            frames.append((q, n, u))
        RESP.append(sweep(name, frames, 0.0022, 0.016, False, MAT["strap"], device=False))

    for s in (1, -1):
        a = edge_point(s, 0.040)
        strap(f"strap-upper-{s}", [a, C + Vector((-0.010, s * 0.08, 0.050)), pad_c + yv * s * 0.030 + up * 0.016])
        b = edge_point(s, -0.088)
        strap(f"strap-lower-{s}", [b, C + Vector((-0.020, s * 0.065, -0.075)),
                                   C + Vector((-0.080, s * 0.035, -0.055)), pad_c + yv * s * 0.026 - up * 0.022])
    return tree


def build_coat():
    COAT.append(ellipsoid("coat-shoulders", (-0.015, 0.0, -0.40), (0.125, 0.215, 0.225), MAT["coat"]))
    frames = []
    for k in range(97):
        beta = 0.42 + (2 * math.pi - 0.84) * k / 96
        q = Vector((-0.012 + 0.068 * math.cos(beta), 0.065 * math.sin(beta), -0.168 - 0.022 * math.cos(beta)))
        d = Vector((math.cos(beta), math.sin(beta), 0.0)).normalized()
        u = (Vector((0.0, 0.0, 1.0)) + d * 0.30).normalized()
        frames.append((q, d, u))
    COAT.append(sweep("coat-collar", frames, 0.005, 0.050, False, MAT["coat"], round_=0.0015, device=False))


def build_bench():
    z0 = -0.72  # bench top, 72 cm below the ear line: standing at a 90 cm bench
    BENCH.append(box("bench", (0.50, 0.0, z0 - 0.015), (0.9, 1.6, 0.03), ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                     MAT["bench"], round_=0.002, device=False))
    for i, (x, y, liq) in enumerate(((0.50, 0.15, "liquid_a"), (0.58, 0.07, "liquid_b"))):
        BENCH.append(cylinder(f"beaker-{i}", (x, y, z0 + 0.045), 0.032, 0.09, (0, 0, 1), MAT["beaker"], device=False))
        BENCH.append(cylinder(f"liquid-{i}", (x, y, z0 + 0.026), 0.029, 0.050, (0, 0, 1), MAT[liq], device=False))
    BENCH.append(box("tube-rack", (0.47, -0.06, z0 + 0.022), (0.05, 0.17, 0.044), ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                     MAT["pod"], round_=0.002, device=False))
    for k in range(6):
        BENCH.append(cylinder(f"tube-{k}", (0.47, -0.135 + 0.03 * k, z0 + 0.05), 0.0075, 0.10, (0, 0, 1),
                              MAT["beaker"], device=False))
    nb = Matrix.Rotation(math.radians(12), 3, "Z")
    BENCH.append(box("notebook", (0.36, -0.26, z0 + 0.004), (0.21, 0.15, 0.008),
                     (nb @ Vector((1, 0, 0)), nb @ Vector((0, 1, 0)), Vector((0, 0, 1))), MAT["paper"], round_=0.001, device=False))
    # Arms in lab-coat sleeves and nitrile gloves; the right hand holds a pipette over the rack.
    for s, wrist, hand in ((1, (0.36, 0.10, -0.64), (0.42, 0.085, -0.665)), (-1, (0.38, -0.02, -0.56), (0.43, -0.04, -0.585))):
        BENCH.append(tube(f"sleeve-{s}", [(-0.02, s * 0.17, -0.25), (0.05, s * 0.21, -0.50), wrist], 0.040, MAT["coat"], device=False))
        BENCH.append(ellipsoid(f"glove-{s}", hand, (0.050, 0.030, 0.017), MAT["glove"],
                               rot=Matrix.Rotation(math.radians(-25 * s), 3, "Z")))
    BENCH.append(cylinder("pipette", (0.46, -0.055, -0.60), 0.011, 0.15, (0.30, 0.10, -1.0), MAT["pod"], device=False))
    BENCH.append(cylinder("pipette-tip", (0.483, -0.047, -0.678), 0.0035, 0.05, (0.30, 0.10, -1.0), MAT["beaker"], device=False))


# ----------------------------------------------------------------------------- checks
def camera_dirs(f, nu=96, nv=54, hfov=102.0):
    tx = math.tan(math.radians(hfov / 2))
    ty = tx * 9 / 16
    ax, ay, az = Vector(f["ax"]), Vector(f["ay"]), Vector(f["az"])
    for i in range(nu):
        for j in range(nv):
            u = -1 + (2 * i + 1) / nu
            v = -1 + (2 * j + 1) / nv
            yield (ax - ay * (u * tx) + az * (v * ty)).normalized()


def blocked_share(tree, f):
    o = Vector(f["lens"]) + Vector(f["ax"]) * 0.003
    dirs = list(camera_dirs(f))
    hits = sum(1 for d in dirs if tree.ray_cast(o, d, 1.0)[0] is not None)
    return hits / len(dirs)


TILTS = (20, 30, 40, 50, 60, 70)


def respirator_checks():
    """Clearances and view checks, written to respirator_check.md."""
    out = [f"# Respirator and lab-coat checks, layout {LAYOUT}", "",
           "Generated by `build_headset.py`; distances in mm. Context geometry is a generic medium",
           "full-face respirator and lab coat, not any one product.", ""]
    face_tree, _ = world_tree([o for o in RESP if o.type == "MESH" and o.name == "facepiece"])
    resp_tree, _ = world_tree([o for o in RESP if o.type == "MESH"])
    dg = bpy.context.evaluated_depsgraph_get()
    rows = []
    for ob in DEVICE:
        if ob.type != "MESH":
            continue
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        dmin = min((face_tree.find_nearest(ob.matrix_world @ v.co)[3] for v in me.vertices), default=9.0)
        ev.to_mesh_clear()
        rows.append((dmin, ob.name))
    rows.sort()
    out += ["## Closest device parts to the facepiece", "", "| Part | Gap to facepiece (mm) |", "| --- | ---: |"]
    out += [f"| {n} | {1000 * d:.1f} |" for d, n in rows[:6]]
    # Lab coat: lowest device point behind the ear line vs. the top of the collar at the back.
    _, cverts = world_tree([o for o in COAT if o.name == "coat-collar"])
    collar_top = max(v.z for v in cverts if v.x < -0.03)
    low = 9.0
    for ob in DEVICE:
        if ob.type != "MESH":
            continue
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        zs = [(ob.matrix_world @ v.co) for v in me.vertices]
        low = min([low] + [p.z for p in zs if p.x < 0.0])
        ev.to_mesh_clear()
    out += ["", f"- Lowest device point behind the ear line: z = {1000 * low:.0f} mm; top of the coat collar at the "
            f"back: z = {1000 * collar_top:.0f} mm; gap **{1000 * (low - collar_top):.0f} mm**.", ""]
    # How much of the camera's frame the respirator blocks, for brim length and tilt.
    keep = dict(L.FRONT_POD)
    out += ["## Share of the camera frame (102° × 70°, 16:9) blocked by the respirator", "",
            "| Brim (mm) | " + " | ".join(f"tilt {t}°" for t in TILTS) + " |",
            "| ---: | " + " | ".join("---:" for _ in TILTS) + " |"]
    for brim in (0.0, 0.030):
        cells = []
        for tilt in TILTS:
            L.FRONT_POD.update(brim=brim, tilt_deg=float(tilt))
            cells.append(f"{100 * blocked_share(resp_tree, L.front_pod_frames()):.1f}%")
        out.append(f"| {1000 * brim:.0f} | " + " | ".join(cells) + " |")
    L.FRONT_POD.update(keep)
    f = L.front_pod_frames()
    out += ["", f"This build: brim {1000 * L.FRONT_POD['brim']:.0f} mm, tilt {L.FRONT_POD['tilt_deg']:.0f}°, "
            f"blocked {100 * blocked_share(resp_tree, f):.1f}%. Lens at x = {1000 * f['lens'][0]:.0f} mm "
            f"(forward of the ear line), z = {1000 * f['lens'][2]:.0f} mm (above it).", ""]
    # Sanity check that the ray test can see the respirator at all: aim at the visor and a filter.
    o = Vector(f["lens"]) + Vector(f["ax"]) * 0.003
    visor = Vector((0.12, 0.0, 0.02))
    filt = next(ob for ob in RESP if ob.name == "filter-1").matrix_world.translation
    seen = [resp_tree.ray_cast(o, (t - o).normalized(), 1.0)[0] is not None for t in (visor, filt)]
    out += [f"Sanity check: rays from the lens aimed at the visor and at a filter hit the respirator: "
            f"{'yes' if all(seen) else 'NO - check the ray test'} ({seen}). The respirator is simply below "
            f"and behind the camera's view.", ""]
    path = os.path.join(HERE, f"respirator_check{'' if LAYOUT == 'v2' else '_' + LAYOUT}.md")
    open(path, "w").write("\n".join(out))
    print("\n".join(out))


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
    scene.cycles.samples = 16 if QUICK else 64
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
print("layout:", LAYOUT)
print("device centre of mass (m):", tuple(round(c, 4) for c in dev))
print("device + headgear centre of mass (m):", tuple(round(c, 4) for c in tot))
build_respirator(head)
build_coat()
build_bench()
respirator_checks()

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

# Everything on the head pitches together for the camera's-eye view.
rig = link(bpy.data.objects.new("head-rig", None))
_context = set(MARKERS) | set(COAT) | set(BENCH)
for ob in list(scene.objects):
    if ob is rig or ob.type in ("LIGHT", "CAMERA") or ob in _context:
        continue
    ob.parent = rig

cam = setup_world()
F = L.front_pod_frames()
PITCH = 25.0  # head bowed 25 degrees, a usual working posture at a bench
if LAYOUT == "v2":
    views = {
        "headset-front-left": dict(direction=(0.80, 0.62, 0.30), dist=1.05),
        "headset-side-balance": dict(direction=(0.0, 1.0, 0.02), dist=1.10, lens=70, markers=True),
        "headset-rear-right": dict(direction=(-0.78, -0.60, 0.40), dist=1.05),
        "headset-xray-rear": dict(direction=(-0.70, 0.55, 0.45), dist=0.62, target=(-0.07, 0.0, 0.05), xray=True),
        "headset-xray-front": dict(direction=(0.80, -0.50, 0.25), dist=0.55, target=(0.08, 0.0, 0.06), xray=True),
        "respirator-front-left": dict(direction=(0.80, 0.62, 0.22), dist=1.25, target=(0.0, 0.0, -0.06), resp=True, coat=True),
        "respirator-side": dict(direction=(0.0, 1.0, 0.0), dist=1.45, target=(0.0, 0.0, -0.08), resp=True, coat=True),
        "respirator-rear-left": dict(direction=(-0.75, 0.62, 0.35), dist=1.20, target=(0.0, 0.0, -0.05), resp=True, coat=True),
        "camera-view": dict(camview=True, resp=True, coat=True, bench=True),
    }
else:
    views = {
        "v1-respirator-conflict": dict(direction=(0.0, 1.0, 0.0), dist=1.45, target=(0.0, 0.0, -0.08), resp=True, coat=True),
    }


def place_camview(cam_obj):
    R = Matrix.Rotation(math.radians(PITCH), 4, "Y")
    R3 = R.to_3x3()
    ax, az = R3 @ Vector(F["ax"]), R3 @ Vector(F["az"])
    pos = R @ (Vector(F["lens"]) + Vector(F["ax"]) * 0.004)
    zc = -ax
    yc = az
    xc = yc.cross(zc)
    M = Matrix((tuple(xc), tuple(yc), tuple(zc))).transposed().to_4x4()
    M.translation = pos
    cam_obj.matrix_world = M
    cam_obj.data.sensor_fit = "HORIZONTAL"
    cam_obj.data.angle = math.radians(102.0)
    cam_obj.data.clip_start = 0.003


for name, v in views.items():
    if VIEWS and name not in VIEWS:
        continue
    for m in MARKERS:
        m.hide_render = not v.get("markers", False)
    for ob in RESP:
        ob.hide_render = not v.get("resp", False)
    for ob in COAT:
        ob.hide_render = not v.get("coat", False)
    for ob in BENCH:
        ob.hide_render = not v.get("bench", False)
    set_xray(v.get("xray", False))
    rx, ry = scene.render.resolution_x, scene.render.resolution_y
    if v.get("camview"):
        rig.rotation_euler = (0.0, math.radians(PITCH), 0.0)
        bpy.context.view_layer.update()
        place_camview(cam)
        scene.render.resolution_x, scene.render.resolution_y = (640, 360) if QUICK else (1280, 720)
    else:
        rig.rotation_euler = (0.0, 0.0, 0.0)
        cam.data.sensor_fit = "AUTO"
        cam.data.clip_start = 0.1
        look(cam, v["direction"], v["dist"], v.get("target", (0.0, 0.0, -0.005)), v.get("lens", 70))
    render(name)
    scene.render.resolution_x, scene.render.resolution_y = rx, ry
rig.rotation_euler = (0.0, 0.0, 0.0)
bpy.context.view_layer.update()
set_xray(False)

if EXPORT_STL and LAYOUT == "v2":
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
