"""The two OpenFlexure microscopes, both set up for reflection (epi-) illumination, from OpenFlexure's own CAD (#303).

* **OpenFlexure Microscope v7** (gitlab.com/openflexure/openflexure-microscope, tag ``v7.0.0-beta5``, commit
  ``4828ffa5``; CERN-OHL-S-2.0): the high-resolution build with the beamsplitter optics module, the filter cube and
  the reflection illuminator; stand, motors, Raspberry Pi and Sangaboard.
* **OpenFlexure Delta Stage** (gitlab.com/openflexure/openflexure-delta-stage, tag ``v1.2.3``, commit ``d882d18b``;
  CERN-OHL-1.2): the same reflection optics under the delta stage, on its electronics base.

Every part was exported from OpenFlexure's OpenSCAD source with OpenSCAD's manifold backend, in assembled positions:
the v7 through the repo's own assembly-rendering modules, the delta stage with its ``build.sh`` options and the
transforms in ``openflexure/manifest.json``. Neither repo renders the reflection set-up assembled, so the filter cube,
illuminator and LED are placed from the .scad sources (see the manifest's notes). The scripts are in
``openflexure/``; the meshes (about 60 MB of STL) are not committed, like the other vendor CAD: they live in
``.cache/openflexure/{v7,delta}/`` and are regenerated with those scripts.

Reflection mode is what metallography needs: the LED sits beside the optics module under the stage, the beamsplitter
turns its light up through the objective onto an opaque, polished sample, and the camera looks down through it.
"""
from __future__ import annotations

import json
from pathlib import Path

import cadquery as cq
import numpy as np
import pyvista as pv

import instruments as I
from common import box, cyl  # noqa: F401  (lab_models helpers, on the path via instruments)

HERE = Path(__file__).resolve().parent
SRC = HERE / ".cache" / "openflexure"
MANIFEST = json.loads((HERE / "openflexure" / "manifest.json").read_text())
MAX_TRIS = 25000            # per part, for the scene; the main bodies keep their detail


def _hex(c: str) -> tuple:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _load(key: str) -> dict:
    """{part: (PolyData, rgb)} for one microscope, decimated to MAX_TRIS."""
    parts = MANIFEST["instruments"][key]["parts"]
    out = {}
    for name, p in parts.items():
        if p.get("placeholder") and "slide" in name:          # the sample is ours (below)
            continue
        path = SRC / p["file"]
        if not path.exists():
            raise FileNotFoundError(f"{path}: build the OpenFlexure meshes first (openflexure/README.md)")
        m = pv.read(str(path)).triangulate().clean()
        if m.n_cells > MAX_TRIS:
            m = m.decimate(1.0 - MAX_TRIS / m.n_cells)
        m = m.compute_normals(split_vertices=True, feature_angle=35.0, auto_orient_normals=False)
        col = _hex(p["colour"])
        if name == "led_star_placeholder":
            col = (1.0, 0.85, 0.2)
        out[name] = (m, col, p.get("moves_with_stage", []))
    return out


def _sample(z: float) -> I.Model:
    """A glass slide with a small polished metal coupon on it: what reflection mode is for."""
    m = I.Model("ofm_sample", "slide and coupon")
    m.add("slide", box(-37.5, -12.5, 0, 37.5, 12.5, 1.0), "window")
    m.add("coupon", box(-6, -6, 1.0, 6, 6, 4.0), "sample")
    return m


# ===================================================================================================== the mechanisms
# The flexure legs, levers and actuator columns move with the stage. Each moves as a linkage driven by the stage's
# displacement d (Joint "follow"), to first order, as the flexures bend by no more than flex_a. Every number below is
# from OpenFlexure's .scad parameters, in the assembly frame (main-body frame + z0).
#
# Microscope v7 (openscad/libs/microscope_parameters.scad, default_params(); main_body_structure.scad). Four legs at
# leg_r = 30 hold the stage, each a parallelogram: two bars between a top and a bottom block, on flexures, so the top
# shifts sideways (tangentially) and stays level. A flexure under the bottom block (xy_flexures, at z = lower_xy_flex_z
# + 0.5 + flex_t/2) hinges the leg to the inner wall, and the top flexure ring (z = upper_xy_flex_z + 0.5 + flex_t/2)
# hinges it to the stage, both across a flex_l gap, at radius leg_r - flex_l/2; the leg is upper_xy_flex_z -
# lower_xy_flex_z = 60 mm between the two. So a leg leans on its bottom flexure by (d . radial)/60 and shears by
# (d . tangent)/60. The front two are actuator_leg()s: an arm runs out from the foot to the actuator column at
# actuating_nut_r = 60 * xy_lever_ratio (4/7) = 34.3 mm, so leg and arm pivot together like a bell crank, and the
# column drops by (34.3 + flex_l/2)/60 of the stage's travel along that leg.
V7_MECH = dict(z0=75.0, leg_r=30.0, flex_l=1.5, flex_t=0.75, z_low=0.0, z_up=60.0, nut_r=60.0 * 4 / 7, flex_a=0.15,
               travel=60.0 * 4 / 7 * 0.15)
# piece: (the leg's outward direction, degrees; it has an arm and a column), as in the wrapper's in_leg_frame()
V7_LEGS = {"leg_x": (45.0, True), "leg_y": (135.0, True), "leg_back_left": (-135.0, False),
           "leg_back_right": (-45.0, False)}
V7_STAGE = (6.0, 4.0, 0.0)          # the tour's scan: 7.1 mm along the X leg, which leans 0.12 rad (flex_a 0.15)
# Delta Stage (openscad/parameters.scad; delta_stage_parts.scad). Three levers at 120 degrees, each hinged on its
# lever_flexures at the casing (radius stage_r + zflex[1]/2, z = dz + zflex[2]/2) and lifted at its far end by the
# actuator column at nut_y. A parallelogram leg stands on each lever, on flexures at lever_l = 35, and carries the stage
# on the stage flexures at z = flex_z2 + dz + zflex[2]/2, back at radius stage_r + zflex[1]/2: it leans in 35 mm over
# 70. When the stage moves by d, the lever turns by theta = (L . d)/(L . (x × (B - P))), which keeps the leg's length
# L; the leg turns about its foot B in its own plane and shears along the tangent x. In the assembly the body is turned
# 120 degrees and raised 79 mm (the manifest's transform_applied).
DELTA_MECH = dict(zb=79.0, rot=120.0, stage_r=25.0, lever_l=35.0, nut_y=47.0, flex_z2=70.0, zflex=(6.0, 1.5, 0.75),
                  dz=0.5, flex_a=0.1)
DELTA_STAGE = (5.0, -4.0, 1.2)      # x/y and focus together: the levers turn at most 0.091 rad (flex_a 0.1)


def _skew(a) -> np.ndarray:
    x, y, z = a
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])


def _unit(a) -> np.ndarray:
    a = np.asarray(a, float)
    return a / np.linalg.norm(a)


def _jac(rot=(), shear=(), move=(), offset=(0.0, 0.0, 0.0)) -> np.ndarray:
    """jac (3 x 3 x 4) for a Joint "follow": the motion of a piece per mm of the stage's displacement d, to first order.
    rot [(axis, pivot, g)]: turn about axis through pivot by g . d radians; shear [(e, pivot, n, u)]: shift along e
    by (u . d) * ((p - pivot) . n); move [(f, w)]: shift along f by w . d. offset: where the microscope stands."""
    A, b = np.zeros((3, 3, 3)), np.zeros((3, 3))
    o = np.asarray(offset, float)
    for axis, pivot, g in rot:
        K = _skew(_unit(axis))
        c = np.asarray(pivot, float) + o
        for k in range(3):
            A[k] += g[k] * K
            b[k] -= g[k] * K @ c
    for e, pivot, n, u in shear:
        S = np.outer(e, n)
        c = np.asarray(pivot, float) + o
        for k in range(3):
            A[k] += u[k] * S
            b[k] -= u[k] * S @ c
    for f, w in move:
        for k in range(3):
            b[k] += w[k] * np.asarray(f, float)
    return np.concatenate([A, b[:, :, None]], axis=2)


def _v7_terms() -> dict:
    """{piece: (parts, rot, shear, move, top)}: each leg's and column's motion; top is a leg's top flexure."""
    p = V7_MECH
    L = p["z_up"] - p["z_low"]
    zh = p["z0"] + p["z_low"] + 0.5 + p["flex_t"] / 2          # the bottom flexures (xy_flexures)
    out = {}
    for piece, (deg, arm) in V7_LEGS.items():
        r = np.array([np.cos(np.radians(deg)), np.sin(np.radians(deg)), 0.0])
        t = np.cross((0.0, 0.0, 1.0), r)
        hinge = (p["leg_r"] - p["flex_l"] / 2) * r + np.array((0.0, 0.0, zh))
        out[piece] = ([piece], [(t, hinge, r / L)], [(t, hinge, np.array((0.0, 0.0, 1 / L)), t)], [],
                      hinge + (0.0, 0.0, L))
        if arm:                                                   # the column on the arm's end
            rho = p["nut_r"] + p["flex_l"] / 2
            out[piece.replace("leg_", "column_")] = ([piece.replace("leg_", "actuator_column_")], [], [],
                                                     [((0.0, 0.0, 1.0), -rho * r / L)], None)
    return out


def _delta_terms() -> dict:
    """{piece: (parts, rot, shear, move, top)} for the three legs, levers and columns."""
    p = DELTA_MECH
    zf = p["zb"] + p["dz"] + p["zflex"][2] / 2                  # the lever flexures, at both ends of the lever
    zt = p["zb"] + p["flex_z2"] + p["dz"] + p["zflex"][2] / 2    # the stage flexures
    out = {}
    for i in range(3):
        a = np.radians(p["rot"] + 120 * i)
        y = np.array([-np.sin(a), np.cos(a), 0.0])               # out along the lever
        x = np.cross(y, (0.0, 0.0, 1.0))
        P = (p["stage_r"] + p["zflex"][1] / 2) * y + (0.0, 0.0, zf)    # lever pivot (lever_flexures)
        B = P + p["lever_l"] * y                                       # the lever-to-leg flexures
        T = (p["stage_r"] + p["zflex"][1] / 2) * y + (0.0, 0.0, zt)    # the leg-to-stage flexures
        L = T - B
        arm = np.cross(x, B - P)                                 # how B moves per radian of the lever
        g = L / (L @ arm)                                        # theta = g . d keeps |L|
        h = (np.cross(x, L) - (np.cross(x, L) @ arm) * g) / (L @ L)   # the leg's own turn about B
        out[f"lever{i}"] = ([f"lever{i}"], [(x, P, g)], [], [], None)
        out[f"leg{i}"] = ([f"leg{i}"], [(x, B, h)], [(x, B, np.array((0.0, 0.0, 1 / L[2])), x)], [(arm, g)], T)
        out[f"column{i}"] = ([f"column{i}"], [], [], [((0.0, 0.0, 1.0), (p["nut_y"] - p["zflex"][1] / 2) * g)],
                             None)
    return out


def _check(key: str, ds) -> None:
    """Every displacement in ds keeps each flexure within flex_a, each leg's top on the stage and each v7 column
    within its travel."""
    terms = _v7_terms() if key == "v7" else _delta_terms()
    lim = (V7_MECH if key == "v7" else DELTA_MECH)["flex_a"]
    for d in np.atleast_2d(np.asarray(ds, float)):
        for piece, (_, rot, shear, move, top) in terms.items():
            for _, _, g in rot:
                assert abs(g @ d) <= lim + 1e-9, f"{key} {piece}: turns {g @ d:.3f} rad at d = {d}, past flex_a"
            for _, _, n, u in shear:
                assert abs((u @ d) * n[2]) <= lim + 1e-9, f"{key} {piece}: shears {(u @ d) * n[2]:.3f} at d = {d}"
            for f, w in move:
                if key == "v7":
                    assert abs(w @ d) <= V7_MECH["travel"], f"v7 {piece}: moves {w @ d:.2f} mm, past its travel"
            if top is not None:                                   # the leg's top flexure goes where the stage goes
                moved = np.tensordot(d, _jac(rot, shear, move), axes=1) @ np.r_[top, 1.0]
                assert np.allclose(moved, d, atol=1e-6), f"{key} {piece}: top moves {moved}, the stage {d}"


def mechanism(key: str, vec=None, path=(), offset=(0.0, 0.0, 0.0), parent=None) -> dict:
    """{piece: (parts, Joint)}: the legs, levers and columns of one microscope standing at offset, following a stage
    that slides by v * vec or goes along path (offsets, as Joint "path" takes them)."""
    _check(key, path if path else [vec])
    terms = _v7_terms() if key == "v7" else _delta_terms()
    out = {}
    for piece, (parts, rot, shear, move, _) in terms.items():
        jac = _jac(rot, shear, move, offset).round(9).tolist()
        out[piece] = (parts, I.Joint("follow", vec=tuple(vec) if vec is not None else (0.0, 0.0, 0.0),
                                     path=tuple(path), parent=parent, jac=tuple(tuple(map(tuple, m)) for m in jac)))
    return out


def _build(key: str, title: str, model: str, source: str, stage_parts: tuple, optics_parts: tuple, z_stage: float,
           cam, stage_vec) -> I.Instrument:
    d = MANIFEST["instruments"][key]
    (x0, y0, z0), (x1, y1, z1) = d["overall_bbox_mm"]
    inst = I.Instrument(f"openflexure_{key}", title, model, (round(x1 - x0), round(y1 - y0), round(z1 - z0)), source)
    mech = mechanism(key, vec=stage_vec)
    piece_of = {part: piece for piece, (parts, _) in mech.items() for part in parts}
    for name, (mesh, col, moves) in _load(key).items():
        piece = "stage" if name in stage_parts else "optics" if name in optics_parts else \
            "led" if name == "led_star_placeholder" else piece_of.get(name, "body")
        inst.meshes.setdefault(piece, []).append((mesh, col, 1.0))
    inst.pieces["sample"] = _sample(z_stage)
    inst.meshes.setdefault("stage", [])
    inst.joints.update({piece: j for piece, (_, j) in mech.items()})
    return inst


def v7() -> I.Instrument:
    d = MANIFEST["instruments"]["v7"]
    zs = d["stage_top_surface_z"]
    inst = _build("v7", "Microscope, reflection", "OpenFlexure Microscope v7",
                  "OpenFlexure Microscope v7.0.0-beta5's OpenSCAD (commit 4828ffa5, CERN-OHL-S-2.0), exported "
                  "assembled with its own rendering modules; reflection optics placed from the .scad sources",
                  ("xy_stage", "sample_clips"),
                  ("optics_module_beamsplitter", "objective", "tube_lens", "picamera2_with_cover", "camera_ribbon_cable",
                   "fl_cube", "reflection_illuminator_holder", "reflection_led_condenser"), zs, None, V7_STAGE)
    mech = list(inst.joints)
    inst.joints.update({
        "sample": I.Joint("path", parent="stage", path=((0, -170, zs + 90), (0, -60, zs + 30), (0, 0, zs + 6),
                                                         (0, 0, zs))),
        "stage": I.Joint("slide", vec=V7_STAGE),
        "optics": I.Joint("slide", vec=(0, 0, 2.0)),
        "led": I.Joint("fade", v0=1.0),
    })
    scan = ["stage", "optics", *mech]
    inst.actions = [
        ("A polished coupon on a slide goes under the clips: reflection mode, for opaque metal samples.", 2.2,
         {"sample": (0.0, 1.0), "led": (1.0, 1.0)}),
        ("The LED beside the optics module lights the sample through the objective via the beamsplitter; the camera "
         "looks down through it. The stage scans x/y on four flexure legs that lean and shear with it; the X and Y "
         "actuators pull the front two as levers. The optics focus.", 3.4, {k: (0.0, 1.0) for k in scan}),
        ("Back to centre. Printed in PLA, about 170 mm across; several fit on one tray.", 1.8,
         {k: (1.0, 0.0) for k in scan}),
    ]
    inst.labels = [("beamsplitter optics and reflection illuminator", (0, -20, 60), (0.12, 0.70)),
                   ("flexure XY stage", (20, -20, zs), (0.84, 0.25))]
    inst.cam = (0.9, -1.6, 0.9)
    inst.zoom = {1: ((20.0, -24.0, 120.0), 200.0), 2: "out"}     # in on the front-right leg while the stage scans
    return inst


def delta() -> I.Instrument:
    d = MANIFEST["instruments"]["delta"]
    zs = d["stage_top_surface_z"]
    inst = _build("delta", "Microscope, reflection", "OpenFlexure Delta Stage",
                  "OpenFlexure Delta Stage v1.2.3's OpenSCAD (commit d882d18b, CERN-OHL-1.2), exported with its "
                  "build.sh options for reflection illumination; assembled from the .scad sources",
                  ("moving_stage", "sample_clips"), (), zs, None, DELTA_STAGE)
    mech = list(inst.joints)
    inst.joints.update({
        "sample": I.Joint("path", parent="stage", path=((0, -170, zs + 90), (0, -60, zs + 30), (0, 0, zs + 6),
                                                         (0, 0, zs))),
        "stage": I.Joint("slide", vec=DELTA_STAGE),
        "led": I.Joint("fade", v0=1.0),
    })
    scan = ["stage", *mech]
    inst.actions = [
        ("The delta stage: three flexure legs move the stage in x, y and z. A polished coupon goes on.", 2.2,
         {"sample": (0.0, 1.0), "led": (1.0, 1.0)}),
        ("Same reflection optics underneath, fixed; the stage does the moving, focus included. Each actuator tips a "
         "lever, and the leg standing on it pushes the stage.", 3.4, {k: (0.0, 1.0) for k in scan}),
        ("Back to centre.", 1.4, {k: (1.0, 0.0) for k in scan}),
    ]
    inst.labels = [("moving stage", (0, 30, zs), (0.84, 0.25)),
                   ("electronics base (Pi, Sangaboard)", (60, -40, 40), (0.84, 0.72))]
    inst.cam = (0.9, -1.6, 0.9)
    inst.zoom = {1: ((28.0, -22.0, 120.0), 235.0), 2: "out"}     # in on the front-right leg and its lever
    return inst
