"""Characterization instruments for round 4 of #303: an array of six OpenFlexure microscopes on one sub-tray, a Keyence
digital microscope with its laser-induced breakdown spectroscopy (LIBS) head, a desktop XRF, and a sieve shaker for the
powder that comes out of the rePowder atomizer.

Each is an ``instruments.Instrument`` with pieces, joints and an ``actions`` script, the same pattern as
``instruments.py``; ``tour.py`` finds them through ``REGISTRY``:

    xvfb-run -a python3 tour.py openflexure_array vhx xrf sieve

Frame and units as in ``instruments.py``: mm, x to the right, y away from you facing the front, z up, origin at the
centre of the footprint. Every published figure is in a ``*_SPECS`` dict with its source; anything read off photos is
marked as an estimate there.

Spectra. ``tour.tour_one`` has no hook for 2-D overlays, so this module wraps ``scene.Scene.overlay`` (once, on import)
to draw a spectrum panel in the scenes named ``instruments/<key>`` for the keys in ``OVERLAYS``. The panel's opacity
follows the opacity of that instrument's ``readout`` piece, a fade joint, so the actions script decides when it shows.
Nothing changes for any other scene. The spectra are illustrative, and say so on screen.
"""
from __future__ import annotations

import math

import cadquery as cq
import numpy as np
import pyvista as pv

import instruments as I
from common import box, cyl, hose, rbox, tube  # noqa: F401  (lab_models helpers, on the path via instruments)
from instruments import Instrument, Joint, _piece, _xcyl, _ycyl

# name: (r, g, b, opacity, specular), merged into tour's MATS
MATERIALS = {
    "char_plate": (0.80, 0.81, 0.83, 1.0, 0.55),        # cast aluminium tooling plate, milled
    "char_duct": (0.36, 0.37, 0.40, 1.0, 0.25),         # cable duct
    "char_cable": (0.08, 0.08, 0.09, 1.0, 0.2),
    "char_keyence": (0.93, 0.93, 0.92, 1.0, 0.30),      # Keyence's white
    "char_keyence_dk": (0.16, 0.17, 0.19, 1.0, 0.35),
    "plasma": (0.80, 0.85, 1.00, 0.95, 0.0),            # the LIBS plasma flash
    "xray": (0.55, 0.85, 0.35, 0.30, 0.0),              # an X-ray beam drawn see-through
    "fluor": (0.95, 0.75, 0.25, 0.30, 0.0),             # fluorescence back to the detector
    "prolene": (0.90, 0.93, 0.95, 0.45, 0.9),           # the sample cup's film
    "powder_fine": (0.42, 0.55, 0.85, 1.0, 0.05),       # sieve fractions, coloured as DAL's sieving model does
    "powder_mid": (0.92, 0.55, 0.20, 1.0, 0.05),
    "powder_coarse": (0.30, 0.31, 0.33, 1.0, 0.05),
}

# key -> function(image, scale, alpha) drawing the 2-D panel; see the docstring
OVERLAYS: dict = {}


def _install_overlay_hook():
    """Wrap Scene.overlay so a scene called instruments/<key> also draws OVERLAYS[key], at the opacity of that
    instrument's `readout` piece. Every other scene is untouched."""
    import scene
    if getattr(scene.Scene, "_char_overlay", False):
        return
    orig = scene.Scene.overlay

    def overlay(self, img, scale, anchors):
        img = orig(self, img, scale, anchors)
        key = self.name.split("/", 1)[1] if self.name.startswith("instruments/") else None
        draw = OVERLAYS.get(key)
        if draw is not None and not scene.CLEAN:
            pre = f"{key}:readout/"
            a = max((v for n, v in self.alpha.items() if n.startswith(pre)), default=0.0)
            if a > 0.02:
                draw(img, scale, min(1.0, a))
        return img

    scene.Scene.overlay = overlay
    scene.Scene._char_overlay = True


def _spectrum_panel(img, scale, alpha, *, title, xlabel, x, y, peaks, note, box_frac=(0.585, 0.105, 0.985, 0.60),
                    xticks=(), log=False):
    """A spectrum plot drawn with PIL: the curve, a label over each named peak, an axis and a note. `peaks` is
    [(x, label)], `box_frac` the panel (x0, y0, x1, y1) as fractions of the frame."""
    from PIL import ImageDraw
    from scene import font
    W, H = img.size
    d = ImageDraw.Draw(img, "RGBA")
    s = max(scale, 0.8)
    a = int(255 * alpha)
    bx0, by0, bx1, by1 = box_frac[0] * W, box_frac[1] * H, box_frac[2] * W, box_frac[3] * H
    d.rounded_rectangle((bx0, by0, bx1, by1), 8 * scale, fill=(255, 255, 255, int(236 * alpha)),
                        outline=(120, 124, 130, a), width=max(1, int(round(1.2 * scale))))
    ft, fs, fn = font(14.5 * s, bold=True), font(12 * s), font(11.5 * s)
    d.text((bx0 + 10 * s, by0 + 6 * s), title, font=ft, fill=(20, 20, 24, a))
    # plot area
    px0, px1 = bx0 + 34 * s, bx1 - 14 * s
    py0, py1 = by0 + 34 * s, by1 - 46 * s
    yv = np.log10(np.maximum(y, 1e-3)) if log else np.asarray(y, float)
    y0, y1 = (yv.min(), yv.max() * 1.12) if not log else (yv.min(), yv.max() + 0.25)
    xs = px0 + (np.asarray(x) - x[0]) / (x[-1] - x[0]) * (px1 - px0)
    ys = py1 - (yv - y0) / max(y1 - y0, 1e-9) * (py1 - py0)
    d.line([(px0, py1), (px1, py1)], fill=(60, 62, 68, a), width=max(1, int(round(scale))))
    d.line([(px0, py0), (px0, py1)], fill=(60, 62, 68, a), width=max(1, int(round(scale))))
    pts = list(zip(xs.tolist(), ys.tolist()))
    poly = [(px0, py1)] + pts + [(px1, py1)]
    d.polygon(poly, fill=(30, 60, 140, int(50 * alpha)))
    d.line(pts, fill=(30, 60, 140, a), width=max(1, int(round(1.6 * scale))))
    for xv in xticks:
        tx = px0 + (xv - x[0]) / (x[-1] - x[0]) * (px1 - px0)
        d.line([(tx, py1), (tx, py1 + 4 * s)], fill=(60, 62, 68, a))
        lab = f"{xv:g}"
        d.text((tx - d.textlength(lab, font=fn) / 2, py1 + 5 * s), lab, font=fn, fill=(60, 62, 68, a))
    d.text(((px0 + px1) / 2 - d.textlength(xlabel, font=fn) / 2, py1 + 19 * s), xlabel, font=fn,
           fill=(60, 62, 68, a))
    used = []
    for xv, lab in peaks:
        i = int(np.argmin(np.abs(np.asarray(x) - xv)))
        tx, ty = xs[i], ys[i]
        tw = d.textlength(lab, font=fs)
        lx, ly = tx - tw / 2, ty - 18 * s
        for ux0, ux1, uy in used:                       # step labels up where they would overlap
            if lx < ux1 + 3 and lx + tw > ux0 - 3 and abs(ly - uy) < 14 * s:
                ly = uy - 14 * s
        ly = max(ly, py0 - 12 * s)
        used.append((lx, lx + tw, ly))
        d.line([(tx, ty - 2 * s), (tx, ly + 14 * s)], fill=(120, 124, 130, int(160 * alpha)))
        d.text((lx, ly), lab, font=fs, fill=(150, 30, 30, a))
    d.text((bx0 + 10 * s, by1 - 17 * s), note, font=fn, fill=(150, 30, 30, a))


def _gauss(x, mu, sig, h):
    return h * np.exp(-0.5 * ((x - mu) / sig) ** 2)


_install_overlay_hook()


# ===================================================================================================== helpers
def _merge(meshes) -> pv.PolyData:
    meshes = [m for m in meshes if m.n_points]
    if not meshes:
        return pv.PolyData()
    out = meshes[0].copy()
    for m in meshes[1:]:
        out = out.merge(m)
    return out


def _moved(mesh: pv.PolyData, dx=0.0, dy=0.0, dz=0.0) -> pv.PolyData:
    m = mesh.copy()
    m.points = m.points + np.array([dx, dy, dz])
    return m


# ===================================================================================================== OpenFlexure array
# Six OpenFlexure microscopes on one aluminium sub-tray, in place of the two freestanding ones on tray D.
#
# The mix is four v7 and two Delta Stages. The v7 is OpenFlexure's current microscope. The Delta Stage keeps its optics
# still and moves the sample in x, y and z, which its makers say makes it "particularly suited to more complex imaging
# (phase, reflection, fluorescence microscopy)" (openflexure-delta-stage docs/index.md). Both run the same reflection
# optics and the same OpenFlexure software; the Delta needs only the "SangaStage (Delta)" stage geometry setting. Two
# Deltas let the lab compare the two on the same coupons; six of one kind is the choice once that is settled.
#
# The plate is 1/4 in (6.35 mm) cast aluminium tooling plate, a stock thickness. Each microscope stands in a 2 mm
# pocket cut to its own footprint (the convex hull of the stand's or base's underside in OpenFlexure's mesh, plus
# 1 mm clearance), so it goes back in the same place every time. The ducts, the hub box and the handles are stand-ins,
# sized here: OpenFlexure publishes nothing for an array.
OFA = dict(plate_t=6.35, pocket=2.0, clear=1.0, W=700.0, D=510.0, r=20.0,
           cols=(-250.0, -45.0, 160.0), rows=(-135.0, 115.0),        # footprint centres, front row first
           duct_w=30.0, duct_h=20.0, hub=(300.0, 97.5, 60.0, 285.0, 45.0), handle_d=14.0, handle_l=150.0,
           handle_out=35.0, lift=140.0, carry=260.0)
OFA_KINDS = ("v7", "v7", "delta", "v7", "v7", "delta")   # front row left to right, then the back row


def _footprint(key: str):
    """The microscope's footprint at the floor: convex hull (x, y) of its lowest vertices, and the hull's centre."""
    import trimesh
    from scipy.spatial import ConvexHull
    import openflexure as O
    part = "stand" if key == "v7" else "base_raspi_sangaboard"
    p = O.MANIFEST["instruments"][key]["parts"][part]
    path = O.SRC / p["file"]
    if not path.exists():
        raise FileNotFoundError(f"{path}: build the OpenFlexure meshes first (openflexure/README.md)")
    v = trimesh.load(str(path), force="mesh").vertices
    low = v[v[:, 2] < 0.5][:, :2]
    hull = low[ConvexHull(low).vertices]
    c = (hull.min(0) + hull.max(0)) / 2
    return hull, c


def _ofm_meshes(key: str, max_tris=6000) -> dict:
    """{role: {rgb: PolyData}} for one microscope, in its own frame; roles body / stage / optics."""
    import openflexure as O
    stage = {"v7": ("xy_stage", "sample_clips"), "delta": ("moving_stage", "sample_clips")}[key]
    optics = ("optics_module_beamsplitter", "objective", "tube_lens", "picamera2_with_cover", "camera_ribbon_cable",
              "fl_cube", "reflection_illuminator_holder", "reflection_led_condenser") if key == "v7" else ()
    out = {"body": {}, "stage": {}, "optics": {}}
    for name, (mesh, col, _) in O._load(key).items():
        role = "stage" if name in stage else "optics" if name in optics else "body"
        m = mesh
        if m.n_cells > max_tris:
            m = m.decimate(1.0 - max_tris / m.n_cells).compute_normals(split_vertices=True, feature_angle=35.0)
        col = tuple(round(c, 3) for c in col)
        out[role].setdefault(col, []).append(m)
    return {r: {c: _merge(ms) for c, ms in d.items()} for r, d in out.items()}


def openflexure_array() -> Instrument:
    import openflexure as O
    p = OFA
    inst = Instrument("openflexure_array", "Six reflection microscopes on one sub-tray",
                      "OpenFlexure array: 4 x v7 + 2 x Delta Stage", (p["W"], p["D"], 0.0),
                      "OpenFlexure Microscope v7.0.0-beta5 and Delta Stage v1.2.3, exported from OpenFlexure's own "
                      "OpenSCAD (openflexure/README.md); the sub-tray, ducts, hub and handles are designed here")
    t, pk = p["plate_t"], p["pocket"]
    z0 = t - pk                                     # the microscopes stand on the pocket floors
    x0, x1, y0, y1 = -p["W"] / 2, p["W"] / 2, -p["D"] / 2, p["D"] / 2
    sites = []
    for i, kind in enumerate(OFA_KINDS):
        sites.append((kind, p["cols"][i % 3], p["rows"][i // 3]))
    hulls = {k: _footprint(k) for k in ("v7", "delta")}
    # ---- the plate: pockets, the handles, the ducts and the hub
    plate = _piece(inst, "plate")
    slab = rbox(p["W"], p["D"], t, p["r"])
    for kind, cx, cy in sites:
        hull, c = hulls[kind]
        pts = [(float(x - c[0] + cx), float(y - c[1] + cy)) for x, y in hull]
        pocket = cq.Workplane("XY").polyline(pts).close().offset2D(p["clear"]).extrude(pk + 1).translate((0, 0, z0))
        slab = slab.cut(pocket)
    plate.add("tooling plate", slab, "char_plate")
    hx, hy, hw, hd, hh = p["hub"]
    plate.add("hub", rbox(hw, hd, hh, 6, x=hx, y=hy, z=t), "inst_dark")
    plate.add("hub label", box(hx - hw / 2 + 8, hy - hd / 2 - 1, t + 10, hx + hw / 2 - 8, hy - hd / 2, t + 22),
              "inst_light")
    for k in range(6):
        plate.add(f"hub port {k}", box(hx - hw / 2 - 1, hy - 100 + 38 * k, t + 15, hx - hw / 2, hy - 86 + 38 * k,
                                         t + 27), "inst_black")
    plate.add("hub light", box(hx - 8, hy - hd / 2 - 1.5, t + 30, hx + 8, hy - hd / 2, t + 35), "screen_on")
    plate.add("power lead", hose([(hx, hy + hd / 2, t + 20), (hx, y1 + 10, t + 20), (hx, y1 + 10, 4)], 8),
              "char_cable")
    dw, dh = p["duct_w"], p["duct_h"]
    yd_mid = -30.0                                  # between the rows
    yd_back = y1 - 20 - dw / 2                      # along the back edge
    xd0 = x0 + 25
    for y in (yd_mid, yd_back):
        plate.add(f"duct {y:.0f}", box(xd0, y - dw / 2, t, hx - hw / 2, y + dw / 2, t + dh), "char_duct")
        plate.add(f"duct lid {y:.0f}", box(xd0 - 1, y - dw / 2 - 1, t + dh, hx - hw / 2, y + dw / 2 + 1, t + dh + 2),
                  "inst_grey")
    # each microscope's cable from the back of its electronics to the nearest duct
    for i, (kind, cx, cy) in enumerate(sites):
        hull, c = hulls[kind]
        yb = cy - c[1] + hull[:, 1].max()           # the back of its footprint
        xc = cx + (40.0 if kind == "v7" else 0.0)
        yd = yd_mid if i < 3 else yd_back
        if i < 3:
            plate.add(f"cable {i}", hose([(xc, yb - 6, t + 14), (xc, yb + 8, t + 14), (xc, yd, t + dh)], 6),
                      "char_cable")
        else:
            plate.add(f"cable {i}", hose([(xc, yb - 6, t + 14), (xc, yd, t + 14), (xc, yd, t + dh)], 6), "char_cable")
    # two handles, one on each end, a person's or the arm's lift points
    hdl = p["handle_d"]
    for sx in (-1, 1):
        xe = sx * p["W"] / 2
        xo = xe + sx * p["handle_out"]
        hl = p["handle_l"] / 2
        plate.add(f"handle {'LR'[sx > 0]}", hose([(xe, -hl, t / 2 + 20), (xo, -hl, t / 2 + 20), (xo, hl, t / 2 + 20),
                                                   (xe, hl, t / 2 + 20)], hdl), "steel")
        for sy in (-1, 1):
            plate.add(f"handle block {'LR'[sx > 0]}{sy}", box(min(xe, xe + sx * 14), sy * hl - 12, 0,
                                                              max(xe, xe + sx * 14), sy * hl + 12, t / 2 + 30),
                      "char_plate")
    # ---- the six microscopes: static parts, stages and (v7) optics, merged across the array by colour
    meshes = {k: _ofm_meshes(k) for k in ("v7", "delta")}
    groups = {"scopes": {}, "stages_v7": {}, "stages_delta": {}, "optics_v7": {}}
    for kind, cx, cy in sites:
        hull, c = hulls[kind]
        dx, dy = cx - c[0], cy - c[1]
        for role, cols in meshes[kind].items():
            g = "scopes" if role == "body" else f"{'stages' if role == 'stage' else 'optics'}_{kind}"
            for col, m in cols.items():
                groups[g].setdefault(col, []).append(_moved(m, dx, dy, z0))
    for g, cols in groups.items():
        for col, ms in cols.items():
            inst.meshes.setdefault(g, []).append((_merge(ms), col, 1.0))
    # ---- a slide with a polished coupon for each
    zs = {k: O.MANIFEST["instruments"][k]["stage_top_surface_z"] + z0 for k in ("v7", "delta")}
    inst.joints = {
        "plate": Joint("path", path=((0, 0, 0), (0, 0, p["lift"]), (0, -p["carry"], p["lift"] + 60))),
        "scopes": Joint("slide", parent="plate"),
        "stages_v7": Joint("path", parent="plate", path=((0, 0, 0), (-6, -4, 0), (6, -4, 0), (6, 0, 0), (-6, 0, 0),
                                                            (-6, 4, 0), (6, 4, 0), (0, 0, 0))),
        "stages_delta": Joint("path", parent="plate", path=((0, 0, 0), (-5, -4, 1), (5, -4, 1), (5, 0, 2), (-5, 0, 2),
                                                               (-5, 4, 3), (5, 4, 3), (0, 0, 0))),
        "optics_v7": Joint("path", parent="plate", path=((0, 0, 0), (0, 0, 2), (0, 0, 0.5), (0, 0, 1.5), (0, 0, 0))),
    }
    for i, (kind, cx, cy) in enumerate(sites):
        hull, c = hulls[kind]
        ax, ay = cx - c[0], cy - c[1]                # its optical axis on the plate
        name = f"slide{i}"
        inst.pieces[name] = O._sample(0.0)
        z = zs[kind]
        inst.joints[name] = Joint("path", parent=f"stages_{kind}", path=(
            (ax, -620.0, z + 160), (ax, ay - 60, z + 30), (ax, ay, z + 6), (ax, ay, z)))
    inst.props = tuple(f"slide{i}" for i in range(6))
    front = {f"slide{i}": (0.0, 1.0) for i in range(3)}
    back = {f"slide{i}": (0.0, 1.0) for i in range(3, 6)}
    inst.actions = [
        ("Six OpenFlexure microscopes on one aluminium sub-tray: four v7 and two Delta Stages, each standing in a "
         "2 mm pocket cut to its own footprint, so it goes back in the same place.", 2.8,
         {f"slide{i}": (0.0, 0.0) for i in range(6)}),
        ("A polished coupon on a slide goes under the clips of each microscope in the front row...", 2.0, front),
        ("...and the back row.", 1.8, back),
        ("All six scan at once: each flexure stage rasters its coupon (+-6 mm) under the reflection optics. The v7s "
         "focus by moving the optics, the Deltas by moving the stage.", 4.2,
         {"stages_v7": (0.0, 1.0), "stages_delta": (0.0, 1.0), "optics_v7": (0.0, 1.0)}),
        ("One hub supplies power and a network switch to all six through the cable ducts; the tray's own power "
         "feeds the hub.", 2.2, {}),
        ("The sub-tray lifts out as one unit by its two end handles: microscopes, slides and cables together.", 2.6,
         {"plate": (0.0, 1.0)}),
        ("And goes back into its place on tray D.", 2.0, {"plate": (1.0, 0.0)}),
    ]
    hub_top = (hx, hy - 60, t + hh)
    inst.labels = [("4 x OpenFlexure v7", (p["cols"][1], p["rows"][0] - 30, 175), (0.16, 0.20)),
                   ("2 x OpenFlexure Delta Stage", (p["cols"][2] - 10, p["rows"][1] - 20, 180), (0.70, 0.14)),
                   ("power and network hub (stand-in)", hub_top, (0.86, 0.42)),
                   ("cable duct", (p["cols"][0] + 60, yd_mid, t + dh + 2), (0.12, 0.55)),
                   ("lift handle", (x1 + p["handle_out"], 0, t / 2 + 20), (0.88, 0.70))]
    inst.cam = (0.5, -1.55, 0.95)
    inst.framing = (0.66, 0.22)
    vol = slab.val().Volume()
    inst.notes = [f"plate {p['W']:.0f} x {p['D']:.0f} x {t} mm aluminium, {vol / 1e6 * 2.70:.1f} kg after the pockets"]
    bb = inst.bbox()
    inst.size = (round(bb[1] - bb[0]), round(bb[3] - bb[2]), round(bb[5] - bb[4]))
    return inst


# ===================================================================================================== registry
REGISTRY = {
    "openflexure_array": openflexure_array,
}
