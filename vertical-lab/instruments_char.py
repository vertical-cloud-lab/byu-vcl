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
            if lx < ux1 + 3 and lx + tw > ux0 - 3 and ly > uy - 14 * s:
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
    # the plate as a mesh with its sharp edges split, so the big flat faces shade flat
    import lab
    r, g, b, _, _ = MATERIALS["char_plate"]
    pm = lab.to_mesh(slab.val(), 0.5).compute_normals(split_vertices=True, feature_angle=30.0)
    inst.meshes["plate"] = [(pm, (r, g, b), 1.0)]
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


# ===================================================================================================== Instrument + aside
class CharInstrument(Instrument):
    """An Instrument whose `aside` pieces (things that are not the machine, such as the powder container, but that
    should stay where they are in the hero still) are left out of its size, like the props."""
    aside: tuple = ()

    def bbox(self, all_pieces=False) -> tuple:
        if all_pieces or not self.aside:
            return super().bbox(all_pieces)
        keep_p, keep_m = self.pieces, self.meshes
        try:
            self.pieces = {k: v for k, v in keep_p.items() if k not in self.aside}
            self.meshes = {k: v for k, v in keep_m.items() if k not in self.aside}
            return super().bbox(all_pieces)
        finally:
            self.pieces, self.meshes = keep_p, keep_m


def _dummy(at=(0.0, 0.0, 0.0)):
    """An invisible speck, so a joint-only piece (a carrier) gets a group with the right parent in tour.Rig."""
    return [(pv.Sphere(radius=0.5, center=at, theta_resolution=4, phi_resolution=4), (1.0, 1.0, 1.0), 0.0)]


def _lathe(pts) -> cq.Shape:
    """Revolve a closed (r, z) half-profile about z (DAL's sieving/viz3d/model.py)."""
    return cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0)).val()


def _shell(line, t) -> cq.Shape:
    """DAL's sieving/viz3d/model.py `shell`: a centre line in (r, z), thickened by t each side, revolved about z."""
    out = None
    pts = [np.asarray(p, float) for p in line]
    for a, b in zip(pts[:-1], pts[1:]):
        d = (b - a) / np.linalg.norm(b - a)
        nrm = np.array([-d[1], d[0]])
        a2, b2 = a - d * t, b + d * t
        quad = [a2 + nrm * t, b2 + nrm * t, b2 - nrm * t, a2 - nrm * t]
        quad = [(max(0.0, float(q[0])), float(q[1])) for q in quad]
        s = _lathe(quad)
        out = s if out is None else out.fuse(s)
    return out.clean()


def _cluster(rng, n, r_bed, z0, rad, heap=8.0) -> pv.PolyData:
    """n spheres of radius `rad` lying in a low heap of radius r_bed on z = z0."""
    out = []
    for _ in range(n):
        rr = r_bed * math.sqrt(rng.random())
        a = rng.random() * 2 * math.pi
        z = z0 + rad + heap * max(0.0, 1 - (rr / r_bed) ** 2) * rng.random()
        out.append(pv.Sphere(radius=rad * (0.85 + 0.3 * rng.random()), center=(rr * math.cos(a), rr * math.sin(a), z),
                             theta_resolution=8, phi_resolution=6))
    return _merge(out)


# ===================================================================================================== sieve shaker
# Retsch AS 200 control, the vibratory sieve shaker. Published (Retsch's AS 200 control page): 417 W x 212 H x 384 D mm,
# about 35 kg; 3-D throwing motion with angular momentum; amplitude 0.20-3.00 mm (digital); acceleration 1.0-15.1 g;
# 20 um to 25 mm; up to 3 kg feed and 6 kg stack; up to 11 full-height or 22 half-height fractions; sieves 100, 200 and
# 203 mm (8 in); stack up to 620 mm; clamping lids "standard" or "comfort", for wet or dry sieving.
# Why it and not the Ro-Tap DAL's sieve note plans to buy used (RX-29: 71 x 54 x 64 cm, 180 lb, about 85 dB, a tapping
# arm over the stack): the AS 200's base is 212 mm tall, so a seven-piece 8 in stack and its lid stay under Kardex's
# 727.5 mm, and nothing swings over the stack. None of Retsch, Fritsch, Haver or Gilson sells a shaker for robot loading.
# The nearest are Fritsch's ANALYSETTE 3 PRO with its electric "TorqueMaster" stack tensioning, which would take the
# hand-tightened clamp out of the job, and SIEBTECHNIK TEMA's ASM with quick-release fasteners. So the animation shows
# what an arm would do with the AS 200: pour, lower the lid, turn the two knobs.
# The look (a light grey housing, a sloped dark control panel with the display at the front, the round sieve plate
# with two threaded rods) is from Retsch's photos; the housing's proportions are approximate.
#
# The stack is the one DAL bought and ordered (DAL PR #175, docs/sieve-order.md: ME Order 13553, McMaster 304
# stainless, 8 x 2 in: cover, No. 60, No. 230 and pan bought; No. 100, No. 140 and No. 325 on order). Its profiles
# are DAL's sieving/viz3d/model.py (8 in = 203.2 mm frames, 2 in deep, which is also what each sieve adds to the
# stack; the 5/8 in skirt, 1.2 mm sheet and rolled rim are assumed there). The AS 200's own clamping lid closes the top,
# so McMaster's cover stays off.
SIEVE_SPECS = dict(W=417.0, H=212.0, D=384.0, mass_kg=35.0, amp_mm=(0.2, 3.0), stack_max=620.0,
                   source="Retsch AS 200 control product page (retsch.com/products/sieving/sieve-shakers/as-200-control)")
T_SHEET, SIEVE_OD, DEPTH, SKIRT_H, LIP = 0.6, 203.2, 50.8, 15.9, 1.8       # DAL sieving/viz3d/model.py
RW = SIEVE_OD / 2 - T_SHEET
RS = RW - 2 * T_SHEET - 0.5
SIEVE_LINE = [(RS, 0.0), (RS, SKIRT_H), (RW, SKIRT_H), (RW, SKIRT_H + DEPTH - 2 * T_SHEET),
              (RW + LIP, SKIRT_H + DEPTH - 2 * T_SHEET)]
PAN_LINE = [(0.0, T_SHEET), (RW, T_SHEET), (RW, DEPTH - T_SHEET), (RW + LIP, DEPTH - T_SHEET)]
MESH_R = RW - T_SHEET - 0.1
MESH_DZ = SKIRT_H + T_SHEET + 0.25
CONT_LINE = [(0.0, 1.0), (54.0, 1.0), (64.0, 11.0), (64.0, 190.0), (44.0, 200.0), (44.0, 228.0)]   # DAL, assumed size
# bottom to top: (key, ASTM E11 number, opening um, what stays on it, material of that fraction)
STACK = [("pan", None, None, "< 45 um", "powder_fine"),
         ("s325", 325, 45, "45-63 um", "powder_f2"),
         ("s230", 230, 63, "63-106 um", "powder_f3"),
         ("s140", 140, 106, "106-150 um", "powder_f4"),
         ("s100", 100, 150, "150-250 um", "powder_mid"),
         ("s60", 60, 250, "> 250 um", "powder_coarse")]
MATERIALS.update({"powder_f2": (0.30, 0.68, 0.80, 1.0, 0.05), "powder_f3": (0.45, 0.72, 0.35, 1.0, 0.05),
                  "powder_f4": (0.95, 0.78, 0.22, 1.0, 0.05), "sieve_cloth": (0.45, 0.47, 0.51, 0.55, 0.4)})


def sieve() -> Instrument:
    p = SIEVE_SPECS
    W, H, D = p["W"], p["H"], p["D"]
    inst = CharInstrument("sieve", "Sieve shaker for atomized powder", "Retsch AS 200 control", (W, D, H),
                          "Retsch AS 200 control product page (417 W x 212 H x 384 D mm, about 35 kg, 3-D throwing "
                          "motion, amplitude 0.2-3 mm); the 8 in stack from DAL PR #175 and DAL's sieving/viz3d model; "
                          "look from Retsch's photos")
    zp = H                                       # the sieve plate's top: the pan stands here
    body = _piece(inst, "body")
    housing = rbox(W, D, H - 28, 40, z=6).edges(">Z").fillet(18)
    body.add("housing", housing, "inst_offwhite")
    body.add("feet", rbox(W - 60, D - 60, 6, 20), "inst_black")
    yf = -D / 2
    panel = I._wedge(W - 80, 70, 30, 120, y0=yf - 8, z=30)
    body.add("control panel", panel, "inst_dark")
    body.add("display", box(-70, yf + 19, 112, 70, yf + 30, 140), "screen_on")
    for i, x in enumerate((-130, -100, 100, 130)):
        body.add(f"key {i}", _ycyl(16, 10, x=x, y=yf + 6, z=90), "inst_light")
    body.add("start key", _ycyl(22, 10, x=0, y=yf - 1, z=70), "inst_green")
    body.add("drive collar", cyl(250, 10, z=H - 22), "inst_dark")
    # the stack and everything that vibrates with it: the sieve plate, the two threaded rods, the sieves
    stack = _piece(inst, "stack")
    rod_x, rod_top = 132.0, zp + 6 * DEPTH + 50.0
    stack.add("sieve plate", cyl(236, 12, z=H - 12), "inst_grey")
    stack.add("rubber mat", cyl(214, 2, z=zp - 2), "inst_black")
    for sx in (-1, 1):
        stack.add(f"rod {sx}", cyl(14, rod_top - zp, x=sx * rod_x, z=zp), "steel")
        stack.add(f"rod foot {sx}", cyl(30, 14, x=sx * rod_x, z=zp - 2), "inst_dark")
        stack.add(f"rod arm {sx}", box(min(sx * 100, sx * rod_x), -12, zp - 12, max(sx * 100, sx * rod_x), 12, zp - 2),
                  "inst_dark")
    levels = {}
    z_rim = zp
    for k, (key, num, op, _, _) in enumerate(STACK):
        if key == "pan":
            stack.add("pan", _shell(PAN_LINE, T_SHEET).translate(cq.Vector(0, 0, zp)), "stainless")
            levels[key] = zp + 2 * T_SHEET
        else:
            z_sk = zp + k * DEPTH - (SKIRT_H - T_SHEET)
            stack.add(f"No. {num} frame", _shell(SIEVE_LINE, T_SHEET).translate(cq.Vector(0, 0, z_sk)), "stainless")
            stack.add(f"No. {num} cloth", cyl(2 * MESH_R, 0.5, z=z_sk + MESH_DZ - 0.25), "sieve_cloth")
            stack.add(f"No. {num} tag", box(-18, -RW - LIP - 1.2, z_sk + SKIRT_H + 14, 18, -RW - LIP + 0.2,
                                             z_sk + SKIRT_H + 26), "brass")
            levels[key] = z_sk + MESH_DZ + 0.25
        z_rim = zp + (k + 1) * DEPTH
    # the clamping lid, modelled clamped on the top rim; it starts parked on the bench to the right, comes in over the
    # rods and down them, and the knobs turn on the rods
    zl = z_rim - 8
    lid = _piece(inst, "lid")
    lid.add("lid", _shell([(RS, 0.0), (RS, 8.0), (RW + LIP + 4, 8.0)], 1.0).translate(cq.Vector(0, 0, zl)), "inst_grey")
    lid.add("lid plate", cyl(2 * RS, 2.0, z=zl + 7), "inst_grey")
    lid.add("crossbar", box(-rod_x - 20, -18, zl + 9, rod_x + 20, 18, zl + 25).cut(
        cyl(16, 40, x=-rod_x, z=zl).union(cyl(16, 40, x=rod_x, z=zl))), "inst_dark")
    for sx in (-1, 1):
        kn = _piece(inst, f"knob{'LR'[sx > 0]}")
        kn.add("knob", cyl(54, 22, x=sx * rod_x, z=zl + 25).cut(cyl(16, 30, x=sx * rod_x, z=zl + 20)), "inst_black")
        for j in range(5):
            a = j * 72
            kn.add(f"grip {j}", cyl(12, 22, x=sx * rod_x + 27 * math.cos(math.radians(a)),
                                    y=27 * math.sin(math.radians(a)), z=zl + 25), "inst_black")
    # the powder: one cluster per fraction, all in a heap on the No. 60 at first, then each on the sieve that keeps it
    rng = np.random.default_rng(7)
    z60 = levels["s60"]
    rad = {"pan": 2.2, "s325": 2.4, "s230": 2.6, "s140": 2.9, "s100": 3.2, "s60": 3.8}
    n_by = {"pan": 26, "s325": 34, "s230": 40, "s140": 34, "s100": 30, "s60": 14}      # an example split, not data
    for key, num, op, rng_txt, mat in STACK:
        r_, g_, b_, _, _ = MATERIALS[mat]
        cl = _cluster(rng, n_by[key], 70.0 if key != "s60" else 55.0, z60, rad[key], heap=10.0)
        inst.meshes[f"frac_{key}"] = [(cl, (r_, g_, b_), 1.0)]
        inst.meshes[f"fall_{key}"] = _dummy((0, 0, z60))
        dz = levels[key] - z60
        inst.joints[f"fall_{key}"] = Joint("path", parent="stack", path=((0, 0, 0), (0, 0, 0.35 * dz), (0, 0, dz)))
        inst.joints[f"frac_{key}"] = Joint("fade", parent=f"fall_{key}")
    # the rePowder's powder container: at rest on the left, then up, over and tipped onto the No. 60
    cx, cy = -W / 2 - 150.0, -40.0
    inst.meshes["carrier"] = _dummy((cx, cy, 0))
    cont = _piece(inst, "container")
    can = _shell(CONT_LINE, 1.0).translate(cq.Vector(cx, cy, 0.45))
    cont.add("container", can, "stainless")
    cont.add("handle", box(cx - 8, cy - 88, 233, cx + 8, cy - 44.5, 249).union(box(cx - 4, cy - 100, 235, cx + 85, cy - 88,
                                                                                 247)), "inst_red")
    cont.add("powder", cyl(120, 40, x=cx, y=cy, z=2), "powder")
    pv_ = (cx + 44, cy, 228.0)                            # the lip it tips over
    pour = (-20.0 - pv_[0], -pv_[1], z_rim + 60 - pv_[2])  # the carrier's offset: the lip just over the No. 60's rim
    inst.joints["carrier"] = Joint("path", path=((0, 0, 0), (0, 0, pour[2] + 60), (pour[0], pour[1], pour[2] + 60),
                                                 pour))
    inst.joints["container"] = Joint("hinge", parent="carrier", axis=(0, 1, 0), pivot=pv_, deg=125.0)
    falls = []
    for j in range(22):
        falls.append(pv.Sphere(radius=2.1, center=(-12 + 6 * math.sin(j * 1.7), 3 * math.cos(j * 2.3),
                                                    z60 + 12 + j * (z_rim + 55 - z60) / 21),
                               theta_resolution=8, phi_resolution=6))
    inst.meshes["stream"] = [(_merge(falls), I.MATERIALS["powder"][:3], 1.0)]
    inst.joints["stream"] = Joint("fade")
    inst.meshes["readout"] = _dummy((0, 0, zp))
    inst.joints["readout"] = Joint("fade")
    inst.joints["stack"] = Joint("path", path=tuple((0.0, 0.0, (1.5 if i % 2 else -1.5) if 0 < i < 24 else 0.0)
                                                    for i in range(25)))
    over = rod_top - zl + 25.0
    inst.joints["lid"] = Joint("path", parent="stack", path=((375.0, -40.0, -zl), (375.0, -40.0, over), (0, 0, over),
                                                            (0, 0, 0)))
    for s in ("L", "R"):
        sx = -1 if s == "L" else 1
        inst.joints[f"knob{s}"] = Joint("spin", parent="lid", axis=(0, 0, 1), pivot=(sx * rod_x, 0, 0), deg=-720.0 * sx)
    fades = {f"frac_{k}": (0.0, 0.0) for k, *_ in STACK}
    inst.aside = ("container", "carrier", "stream", "readout") + tuple(f"frac_{k}" for k, *_ in STACK) + \
        tuple(f"fall_{k}" for k, *_ in STACK)
    inst.props = tuple(f"frac_{k}" for k, *_ in STACK) + tuple(f"fall_{k}" for k, *_ in STACK) + \
        ("lid", "knobL", "knobR")
    inst.actions = [
        ("The powder from the atomizer's container goes onto the top sieve. The stack is the 8 in, 304 stainless one "
         "DAL bought and ordered: No. 60, 100, 140, 230, 325 and a pan.", 2.8,
         {"carrier": (0.0, 1.0), "container": (0.0, 1.0), **fades}),
        ("", 2.0, {"stream": (0.0, 1.0), **{f"frac_{k}": (0.0, 1.0) for k, *_ in STACK}}),
        ("The container goes back. The clamping lid goes over the two rods and down onto the stack ...", 2.6,
         {"stream": (1.0, 0.0), "carrier": (1.0, 0.0), "container": (1.0, 0.0), "lid": (0.0, 1.0)}),
        ("... and its knobs clamp it: what an arm would do, since no shaker found is sold for robot loading.", 1.4,
         {"knobL": (0.0, 1.0), "knobR": (0.0, 1.0)}),
        ("Sieving, drawn see-through: 3-D throwing motion, amplitude 0.2-3 mm. Each size class falls until a cloth "
         "stops it.", 5.6, {"stack": (0.0, 1.0), "~stack": (0.0, 1.0), "~lid": (0.0, 1.0),
                            **{f"fall_{k}": (0.0, 1.0) for k, *_ in STACK}}),
        ("The fractions, by the sieve that keeps each. The LPBF cut (20-63 um) is the No. 325 and the pan; DED's "
         "45-105 um is the No. 230 and No. 325; its 100-200 um is close to the No. 140 and No. 100.", 4.6,
         {"readout": (0.0, 1.0)}),
    ]
    inst.labels = [(f"No. {num} ({op} um)" if num else "pan", (RW + LIP, 0, levels[key] + 10),
                    (0.80, 0.80 - 0.105 * i)) for i, (key, num, op, _, _) in enumerate(STACK)]
    inst.labels.append(("rePowder powder container", (cx, cy - 64, 150), (0.10, 0.62)))
    inst.cam = (0.5, -1.8, 0.62)
    inst.framing = (1.25, 0.66)
    inst.notes = [f"stack top rim {z_rim:.1f} mm, lid closed about {z_rim + 30:.0f} mm, rods {rod_top:.0f} mm"]
    return inst


def _sieve_panel(img, scale, alpha):
    from PIL import ImageDraw
    from scene import font
    W, H = img.size
    d = ImageDraw.Draw(img, "RGBA")
    s = max(scale, 0.8)
    a = int(255 * alpha)
    rows = [(f"No. {num}  ({op} um)" if num else "pan", txt, MATERIALS[mat][:3]) for _, num, op, txt, mat in
            reversed(STACK)]
    x0, y0 = 0.035 * W, 0.12 * H
    lh = 24 * s
    w = 300 * s
    h = (len(rows) + 2) * lh + 34 * s
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 8 * scale, fill=(255, 255, 255, int(236 * alpha)),
                        outline=(120, 124, 130, a))
    d.text((x0 + 10 * s, y0 + 6 * s), "What stays on each sieve", font=font(14.5 * s, bold=True), fill=(20, 20, 24, a))
    f = font(13 * s)
    for i, (name, txt, col) in enumerate(rows):
        yy = y0 + 32 * s + i * lh
        c = tuple(int(255 * v) for v in col)
        d.ellipse((x0 + 12 * s, yy + 3 * s, x0 + 26 * s, yy + 17 * s), fill=c + (a,))
        d.text((x0 + 34 * s, yy), name, font=f, fill=(20, 20, 24, a))
        d.text((x0 + 180 * s, yy), txt, font=font(13 * s, bold=True), fill=(20, 20, 24, a))
    yy = y0 + 32 * s + len(rows) * lh + 4 * s
    d.text((x0 + 12 * s, yy), "LPBF 20-63 um: No. 325 + pan", font=font(12 * s), fill=(30, 60, 140, a))
    d.text((x0 + 12 * s, yy + 17 * s), "Amounts drawn are an example, not data", font=font(11.5 * s),
           fill=(150, 30, 30, a))


# ===================================================================================================== Keyence VHX
# Keyence VHX-7000 digital microscope with the EA-300 laser-based elemental analyzer, on the VHX-S750E free-angle
# observation system. Published (Keyence's VHX-7000N brochure KA1-1099, pp. 34-38; the EA-300 model page):
# * EA-300 "Observation and elemental analysis unit": 280 W x 210 D x 375 H mm with its lens stored, about 7.2 kg; a
#   355 nm Nd:YAG laser, Class 1; 10 um spot (typ.); elements H to U; its own 3.19 MP camera at 300-1000x through a
#   reflective objective with 25 mm working distance; powered from the VHX controller's camera port, no box of its own.
# * The brochure's configuration diagram marks the VHX-S750E, S770E and S700 stands "EA-compatible", and the VH-ZST
#   (20-2000x) and VH-Z00R/Z00T lenses; the VH-ZST hangs off the EA-300 through its lens joint (OP-88660).
# * VHX-S750E: XYZ motorized stage, XY +-20 mm, theta rotation +-90 deg, stage top 171 x 168 mm (centre disk 100 mm),
#   focus Z 49 mm and stage Z 50 mm motorized, 23.8 kg, 5 kg load. Keyence publishes no outer size for the stand
#   (only a drawing), so the base and column here are scaled from Keyence's photos: estimates.
# * VHX-7000 controller: 625 W x 460 H x 180 D mm stored, about 12 kg; the 27 in 4K screen (596.7 x 335.7 mm) is in the
#   controller's own spec table, so it is drawn built in (an inference).
# * The head's tilt: Keyence's text gives no range; Georgia Tech's facility page gives -60 to +90 deg for the VHX-7000.
# The VHX-7000 is discontinued; Keyence offers the VHX-X1 in its place. The EA-300 is how DAL's proposal could add
# elemental mapping to the "Keyence VHX-7000 Optical Microscope (BYU)" it lists.
VHX_SPECS = dict(ea_W=280.0, ea_D=210.0, ea_H=375.0, ea_kg=7.2, laser_nm=355, spot_um=10, wd=25.0,
                 ctrl_W=625.0, ctrl_H=460.0, ctrl_D=180.0, screen=(596.7, 335.7), stage=(171.0, 168.0), disk=100.0,
                 xy=20.0, focus_z=49.0, stand_kg=23.8,
                 base=(330.0, 430.0, 95.0), column=(150.0, 120.0, 560.0))     # base and column: estimates from photos


def vhx() -> Instrument:
    p = VHX_SPECS
    inst = CharInstrument("vhx", "Digital microscope with laser elemental analysis (LIBS)",
                          "Keyence VHX-7000 + EA-300", (0.0, 0.0, 0.0),
                          "Keyence VHX-7000N brochure KA1-1099 pp. 34-38 (EA-300 280 x 210 x 375 mm, 7.2 kg, 355 nm "
                          "Nd:YAG, 10 um spot, H-U; VHX-S750E stage 171 x 168 mm, XY +-20 mm; controller 625 x 460 x "
                          "180 mm); EA-300 model page; stand base and column scaled from Keyence's photos")
    bw, bd, bh = p["base"]
    cw, cd, ch = p["column"]
    sx0 = 0.0                                     # the stand's centre; the controller stands to its right
    body = _piece(inst, "body")
    body.add("stand base", rbox(bw, bd, bh, 30, x=sx0).edges(">Z").fillet(10), "char_keyence")
    body.add("base trim", box(sx0 - bw / 2 + 20, -bd / 2 - 1, 20, sx0 + bw / 2 - 20, -bd / 2, 40), "char_keyence_dk")
    yc = bd / 2 - cd / 2 - 15
    body.add("column", rbox(cw, cd, ch, 20, x=sx0, y=yc, z=bh), "char_keyence")
    body.add("column face", box(sx0 - cw / 2 + 15, yc - cd / 2 - 1, bh + 40, sx0 + cw / 2 - 15, yc - cd / 2, bh + ch - 40),
             "char_keyence_dk")
    zs = bh + 40.0                                 # the stage top
    body.add("XY stage", rbox(p["stage"][0], p["stage"][1], 40, 8, x=sx0, y=-40, z=bh), "char_keyence_dk")
    body.add("stage disk", cyl(p["disk"], 2, x=sx0, y=-40, z=zs - 1), "inst_grey")
    # the free-angle arm: a pivot on the column at the head's focal height, so the view stays centred as it tilts
    zf = zs + 1.0 + 12.6                           # the sample surface: a 12.6 mm mounted coupon on the stage disk
    pivot = (sx0, -40.0, zf)
    head = _piece(inst, "head")
    eh = p["ea_H"]
    z_ea = zf + p["wd"] + 40.0                     # the EA-300's underside: objective nose + working distance
    # the EA-300's back stands 4 mm clear of the tilt guide on the column face, the arm bridging the gap
    ey = yc - cd / 2 - 14 - 4 - p["ea_D"] / 2
    ly = ey - 110.0                                # the zoom lens, half sunk in the EA-300's front as before
    head.add("arm", box(sx0 - 40, -40 + 60, z_ea + 120, sx0 + 40, yc - cd / 2, z_ea + 200), "char_keyence_dk")
    head.add("EA-300", rbox(p["ea_W"], p["ea_D"], eh, 18, x=sx0, y=ey, z=z_ea).edges(">Z").fillet(10),
             "char_keyence")
    head.add("EA-300 band", box(sx0 - p["ea_W"] / 2 - 0.5, ey - p["ea_D"] / 2 - 0.5, z_ea + 150,
                                sx0 + p["ea_W"] / 2 + 0.5, ey + p["ea_D"] / 2 + 0.5, z_ea + 175), "char_keyence_dk")
    head.add("objective", cyl(46, 40, x=sx0, y=-40, z=z_ea - 40), "inst_dark")
    head.add("objective ring", cyl(52, 6, x=sx0, y=-40, z=z_ea - 12), "chrome")
    head.add("VH-ZST zoom lens", cyl(58, 150, x=sx0 + 95, y=ly, z=z_ea + 60), "char_keyence_dk")
    head.add("camera", rbox(60, 60, 50, 6, x=sx0 + 95, y=ly, z=z_ea + 210), "char_keyence")
    head.add("lens joint", box(sx0 + 60, ly - 15, z_ea + 150, sx0 + 140, ly + 20, z_ea + 180), "inst_grey")
    # the free-angle guide: an arc on the column face about the focal point, which the arm rides as the head tilts
    R_arm = z_ea + 160 - zf
    for k in range(-6, 7):
        seg = box(sx0 - R_arm * math.sin(math.radians(5.5)), yc - cd / 2 - 14, zf + R_arm - 12,
                  sx0 + R_arm * math.sin(math.radians(5.5)), yc - cd / 2, zf + R_arm + 12)
        body.add(f"tilt guide {k}", seg.rotate((sx0, 0, zf), (sx0, 1, zf), 10.0 * k), "char_keyence_dk")
    body.add("cable", hose([(sx0 + cw / 2 - 20, yc + cd / 2, bh + ch - 80), (sx0 + cw / 2 - 20, yc + cd / 2 + 40, bh + ch - 80),
                            (sx0 + 200, yc + cd / 2 + 40, 60), (390.0, yc + cd / 2 + 40, 60)], 10), "char_cable")
    # the controller with its 27 in screen
    cx = 540.0                                     # drawn, but left out of the framing and the size (aside)
    ctrl = _piece(inst, "controller")
    ctrl.add("controller", rbox(p["ctrl_W"], p["ctrl_D"], 110, 10, x=cx, y=60), "char_keyence")
    ctrl.add("screen frame", box(cx - p["ctrl_W"] / 2, 60 - 20, 110, cx + p["ctrl_W"] / 2, 60 + 20, p["ctrl_H"]),
             "inst_black")
    sw, sh = p["screen"]
    ctrl.add("screen", box(cx - sw / 2, 60 - 21, 110 + (p["ctrl_H"] - 110 - sh) / 2, cx + sw / 2, 60 - 20,
                           110 + (p["ctrl_H"] - 110 + sh) / 2), "screen_on")
    body.add("handheld controller", rbox(110, 70, 30, 12, x=sx0 + 260, y=-120, z=0), "char_keyence_dk")
    # the sample, the laser and the plasma
    smp = _piece(inst, "sample")
    smp.add("mount", cyl(30, 12, z=0), "mount")
    smp.add("polished face", cyl(22, 0.6, z=12), "sample")
    inst.joints = {
        # in under the objective's nose, then down onto the stage disk (its top at zs + 1)
        "sample": Joint("path", path=((sx0, -320, zs + 150), (sx0, -160, zs + 14), (sx0, -40, zs + 6), (sx0, -40, zs + 1))),
        "head": Joint("hinge", axis=(0, 1, 0), pivot=pivot, deg=-35.0, parent="focus"),
        "laser": Joint("fade"),
        "plasma": Joint("fade"),
        "readout": Joint("fade"),
    }
    inst.meshes["focus"] = _dummy((sx0, -40, zf))
    inst.joints["focus"] = Joint("path", path=((0, 0, 0), (0, 0, -6), (0, 0, 6), (0, 0, 0)))
    las = _piece(inst, "laser")
    las.add("beam", cyl(6.0, z_ea - 40 - zf, x=sx0, y=-40, z=zf), "laser")
    pl = _piece(inst, "plasma")
    pl.add("plasma core", cq.Workplane("XY").sphere(2.4).translate((sx0, -40, zf + 1.5)), "plasma")
    pl.add("plasma glow", cq.Workplane("XY").sphere(14.0).translate((sx0, -40, zf + 3.0)), "plasma_halo")
    inst.meshes["readout"] = _dummy((cx, 60, 300))
    inst.aside = ("readout", "controller")
    inst.props = ("sample",)
    inst.actions = [
        ("A polished, mounted coupon goes onto the VHX-S750E's motorized XY stage (+-20 mm).", 2.4,
         {"sample": (0.0, 1.0), "laser": (0.0, 0.0), "plasma": (0.0, 0.0), "readout": (0.0, 0.0)}),
        ("The free-angle head tilts to look at the surface from the side; the view stays centred on the coupon.", 2.6,
         {"head": (0.0, 1.0)}),
        ("Upright again. Depth composition: the motorized Z focus sweeps through the relief and the controller keeps "
         "the sharp part of each frame (VH-ZST zoom: 20-2000x).", 3.6, {"head": (1.0, 0.0), "focus": (0.0, 1.0)}),
        ("The EA-300 fires: a 355 nm Nd:YAG pulse (drawn red, and far wider than its 10 um spot) turns a speck of the "
         "surface into a plasma.", 2.4, {"laser": (0.0, 1.0), "plasma": (0.0, 1.0)}),
        ("Its spectrometer reads the plasma's light: elements from H to U, in seconds, at the spot the camera is "
         "looking at.", 4.2, {"laser": (1.0, 0.0), "plasma": (1.0, 0.3), "readout": (0.0, 1.0)}),
        ("The EA-300 adds 7.2 kg and 375 mm to the stand. Stand and head are 655 mm tall: under Kardex's 727.5 mm.",
         2.4, {"plasma": (0.3, 0.0), "readout": (1.0, 0.0)}),
    ]
    inst.labels = [("EA-300 LIBS head", (sx0 - p["ea_W"] / 2, -40, z_ea + 250), (0.10, 0.25)),
                   ("VH-ZST zoom lens", (sx0 + 95 + 29, ly, z_ea + 120), (0.42, 0.14)),
                   ("motorized XY stage", (sx0 - p["stage"][0] / 2, -40 - p["stage"][1] / 2, zs), (0.08, 0.72)),
                   ("controller, 27 in 4K screen", (cx - 250, 40, p["ctrl_H"] - 60), (0.84, 0.80)),
                   ("laser spot", (sx0, -40 - 15, zf + 2), (0.12, 0.50))]
    inst.cam = (0.55, -1.7, 0.62)
    inst.framing = (0.95, 0.46)
    bb = inst.bbox()
    inst.size = (round(bb[1] - bb[0]), round(bb[3] - bb[2]), round(bb[5] - bb[4]))
    return inst


MATERIALS["plasma_halo"] = (0.85, 0.80, 1.00, 0.35, 0.0)


def _libs_panel(img, scale, alpha):
    x = np.linspace(250, 420, 900)
    lines = [(279.55, 0.55, "Mg II"), (280.27, 0.40, ""), (285.21, 0.45, ""), (288.16, 1.0, "Si I"),
             (324.75, 0.30, "Cu I"), (327.40, 0.22, ""), (371.99, 0.25, "Fe I"), (373.49, 0.18, ""),
             (394.40, 1.6, ""), (396.15, 2.0, "")]
    y = 0.06 + 0.02 * np.sin(x / 7.0) ** 2
    for mu, h, _ in lines:
        y = y + _gauss(x, mu, 0.35, h)
    peaks = [(mu, lab) for mu, _, lab in lines if lab] + [(396.15, "Al I 394/396")]
    _spectrum_panel(img, scale, alpha, title="EA-300: LIBS spectrum at the spot (illustrative)",
                    xlabel="wavelength (nm)", x=x, y=y, peaks=peaks, xticks=(250, 300, 350, 400),
                    note="Illustrative: NIST line positions, made-up intensities. Not a measurement.")


# ===================================================================================================== desktop XRF
# Bruker S2 PUMA Series 2, with the XY Autochanger. Published (Bruker's S2 PUMA Series 2 data, via its distributor
# DKSH): single-sample 67 x 71 x 37 cm, 87 kg; XY Autochanger 67 x 71 x 61 cm (W x D x H), 108 kg; Carousel and
# Automation 67 x 71 x 57 cm, 130-132 kg (the Automation version has an "interface to conveyor belt or robot arm
# link-up"); Pd or Ag anode, 50 W, 50 kV max; HighSense silicon drift detector, Na to Am; air, vacuum, helium or
# nitrogen, and a "Helium mode with reduced pressure" for loose powder samples; the XY tray has 20 removable positions,
# cups up to 40 mm across and 38 mm tall. Fits a tray: 610 mm against Kardex's 727.5 mm, closed. The lid's open height
# isn't published; open, it needs the opening, not a slot. The look (a white body with a sloped front, the sample tray
# under a large dark lid hinged at the back, the touch screen on the right) is from Bruker's photos: approximate.
# Like most benchtop EDXRF, it measures from below: the cup sits film-side down over the tube and detector.
# Alternatives checked: Rigaku NEX DE VS (356 x 351 x 260 mm, 27 kg, 1, 3 and 10 mm spots), Thermo ARL QUANT'X
# (lid opens to 915 mm), Hitachi EA1000VX (520 x 600 x 445 mm), Bruker M4 TORNADO (a micro-XRF mapper, 815 x 680 x 580
# mm, 130 kg).
XRF_LID_DEG = 35.0         # how far the lid is drawn opening: not published
XRF_SPECS = dict(W=670.0, D=710.0, H=610.0, kg=108, positions=20, cup_d=40.0, cup_h=38.0, kv=50, watts=50,
                 source="Bruker S2 PUMA Series 2 specifications, DKSH (technology-products.dksh.com/?p=1219)")


def xrf() -> Instrument:
    p = XRF_SPECS
    W, D, H = p["W"], p["D"], p["H"]
    inst = CharInstrument("xrf", "Benchtop EDXRF for powders and coupons", "Bruker S2 PUMA Series 2, XY Autochanger",
                          (W, D, H), "Bruker S2 PUMA Series 2 specifications via DKSH (XY Autochanger 67 x 71 x 61 cm, "
                          "108 kg; 20-position tray; 50 W Pd/Ag tube; HighSense SDD; reduced-pressure He for loose "
                          "powders); look from Bruker's photos")
    yf, yb = -D / 2, D / 2
    deck = 420.0                                  # the sample deck under the lid (estimate from photos)
    body = _piece(inst, "body")
    body.add("feet", rbox(W - 80, D - 80, 15, 20), "inst_black")
    shell = I._wedge(W, D, D - 140, deck - 15, y0=yf, z=15).edges("|Y").fillet(25)
    body.add("housing", shell, "inst_white")
    lean = math.degrees(math.atan2(140.0, deck - 15.0))   # the front leans back 140 mm over its 405 mm height

    def on_front(x0, x1, z0, z1, t=1.0):
        """A thin plate lying on the sloped front, from z0 to z1 (as measured up the face's height)."""
        zc = (z0 + z1) / 2
        yc = yf + 140.0 * (zc - 15.0) / (deck - 15.0)
        return box(x0, -t, z0 - zc, x1, 0.0, z1 - zc).rotate((0, 0, 0), (1, 0, 0), -lean).translate((0, yc, zc))
    body.add("front band", on_front(-W / 2 + 30, W / 2 - 30, 40, 70), "inst_navy")
    body.add("logo", on_front(-W / 2 + 40, -W / 2 + 180, deck - 80, deck - 60, 1.5), "inst_blue")
    body.add("touch screen", box(W / 2 - 190, yf + 140 - 30, deck - 15, W / 2 - 40, yf + 140, deck + 75).rotate(
        (0, yf + 140, deck - 15), (1, yf + 140, deck - 15), -25), "screen_on")
    deck_plate = box(-W / 2 + 20, yf + 150, deck - 15, W / 2 - 230, yb - 40, deck + 1)
    # the XY sample tray: 4 x 5 = 20 cups' seats, removable
    tx, ty = -W / 2 + 20 + (W - 250) / 2, (yf + 150 + yb - 40) / 2
    tray = box(tx - 150, ty - 190, deck, tx + 150, ty + 190, deck + 12)
    seats = []
    for i in range(4):
        for j in range(5):
            sx_, sy_ = tx - 105 + 70 * i, ty - 150 + 75 * j
            seats.append((sx_, sy_))
            tray = tray.cut(cyl(p["cup_d"] + 4, 20, x=sx_, y=sy_, z=deck + 2))
    body.add("XY tray", tray, "aluminium")
    # the measuring position: the window over the tube, front left of the tray
    mx, my = tx - 105, ty - 150 - 75                   # in front of the tray's first row
    body.add("deck", deck_plate.cut(cyl(46, 20, x=mx, y=my, z=deck - 18)), "inst_grey")   # open under the window
    body.add("measuring window", tube(70, 46, 3, x=mx, y=my, z=deck - 1), "steel")
    lid = _piece(inst, "lid")
    lw, ld = W - 230, D - 190
    lid.add("lid", rbox(lw, ld, H - deck - 10, 30, x=-W / 2 + 20 + lw / 2, y=yf + 150 + ld / 2 - 5, z=deck)
            .edges(">Z").fillet(20).cut(rbox(lw - 16, ld - 16, H - deck - 18, 24, x=-W / 2 + 20 + lw / 2,
                                             y=yf + 150 + ld / 2 - 5, z=deck - 1)), "inst_dark")
    lid.add("lid window", box(-W / 2 + 80, yf + 170, H - 11, -W / 2 + lw - 40, yf + 300, H - 9), "polycarb")
    lid.add("lid grip", box(-W / 2 + 120, yf + 140, deck + 40, -W / 2 + lw - 80, yf + 150, deck + 60), "chrome")
    # inside, under the window: the tube and the detector, seen when the body goes see-through
    inner = _piece(inst, "inner")
    spot = np.array([mx, my, deck + 2.0])
    tube_end, det_end = spot + (-40.0, 0.0, -80.0), spot + (40.0, 0.0, -80.0)
    for name, a, L, dia, mat in (("X-ray tube", tube_end, 120.0, 60.0, "inst_black"),
                                 ("detector", det_end, 140.0, 30.0, "steel")):
        dvec = (a - spot) / np.linalg.norm(a - spot)
        inner.add(name, cq.Workplane("XY").add(cq.Solid.makeCylinder(dia / 2, L, cq.Vector(*a), cq.Vector(*dvec))), mat)
    cup = _piece(inst, "sample")
    cup.add("cup", tube(p["cup_d"], p["cup_d"] - 3, 25, z=1.5), "pp_white")
    cup.add("film", cyl(p["cup_d"] - 1, 0.4, z=0.6), "prolene")
    cup.add("powder", cyl(p["cup_d"] - 4, 12, z=1.2), "powder")
    cup.add("ring", tube(p["cup_d"] + 2, p["cup_d"] - 1, 6, z=0.0), "pp_white")
    beam = _piece(inst, "beam")
    beam.add("primary", _cone(tube_end, spot, 3.0, 12.0), "xray")
    beam.add("fluorescence", _cone(spot, det_end, 12.0, 8.0), "fluor")
    inst.meshes["readout"] = _dummy((0, 0, H))
    hinge_y = yb - 40
    s0 = seats[2]
    path = ((s0[0] - 60, yf - 260, H + 220), (s0[0], s0[1] - 30, H + 120), (s0[0], s0[1], deck + 40),
            (s0[0], s0[1], deck + 3), (s0[0], s0[1], deck + 40), (mx, my, deck + 40), (mx, my, deck + 2))
    seg = np.linalg.norm(np.diff(np.asarray(path), axis=0), axis=1)
    v_seat = float(seg[:3].sum() / seg.sum())
    inst.joints = {
        "lid": Joint("hinge", axis=(1, 0, 0), pivot=(0, hinge_y, H - 10), deg=-XRF_LID_DEG),
        "sample": Joint("path", path=path),
        "beam": Joint("fade"),
        "readout": Joint("fade"),
    }
    inst.aside = ("readout",)
    inst.props = ("sample", "beam")
    inst.actions = [
        ("The lid lifts on its rear hinge, uncovering the XY Autochanger's 20-position tray.", 2.2,
         {"lid": (0.0, 1.0), "sample": (0.0, 0.0), "beam": (0.0, 0.0), "readout": (0.0, 0.0)}),
        ("A cup of atomized powder, closed underneath by a thin prolene film, goes into a free seat.", 2.6,
         {"sample": (0.0, v_seat)}),
        ("Lid down; drawn see-through.", 1.6, {"lid": (1.0, 0.0), "~body": (0.0, 1.0), "~lid": (0.0, 1.0)}),
        ("The changer takes the cup to the measuring position, film side down over the window: the tube and the "
         "detector are underneath. Helium at reduced pressure keeps loose powder in place.", 2.8,
         {"sample": (v_seat, 1.0)}),
        ("The beam, drawn see-through: up to 50 kV and 50 W from the tube; each element in the powder answers with "
         "its own X-ray lines, which the silicon drift detector counts.", 3.0, {"beam": (0.0, 1.0)}),
        ("The spectrum: peaks at each element's lines give the composition, Na to Am, in minutes.", 4.8,
         {"readout": (0.0, 1.0)}),
    ]
    inst.labels = [("lid", (-W / 2 + 60, yf + 300, H - 5), (0.10, 0.22)),
                   ("20-position XY tray", (tx - 140, ty, deck + 12), (0.10, 0.52)),
                   ("touch screen", (W / 2 - 115, yf + 150, deck + 40), (0.86, 0.74))]
    inst.cam = (0.75, -1.75, 0.9)
    inst.framing = (0.95, 0.50)
    # how tall the lid stands open, against the ~844 mm between a presented tray's floor and the opening's header
    lb = lid.bbox()
    corners = np.array([[x, y, z] for x in (lb.xmin, lb.xmax) for y in (lb.ymin, lb.ymax) for z in (lb.zmin, lb.zmax)])
    m = I._R((1, 0, 0), -XRF_LID_DEG, (0, hinge_y, H - 10))
    top = float((corners @ m[:3, :3].T + m[:3, 3])[:, 2].max())
    inst.notes = [f"lid drawn opening {XRF_LID_DEG:.0f} deg: its front edge rises to {top:.0f} mm (estimate)"]
    return inst


def _cone(a, b, ra, rb):
    """A truncated cone from point a (radius ra) to point b (radius rb)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    L = float(np.linalg.norm(b - a))
    d = (b - a) / L
    return cq.Workplane("XY").add(cq.Solid.makeCone(ra, rb, L, cq.Vector(*a), cq.Vector(*d)))


def _xrf_panel(img, scale, alpha):
    x = np.linspace(0.5, 10.0, 900)
    lines = [(1.254, 0.10, "Mg Ka"), (1.487, 1.0, "Al Ka"), (1.740, 0.85, "Si Ka"), (5.899, 0.05, "Mn Ka"),
             (6.404, 0.32, "Fe Ka"), (7.058, 0.06, ""), (8.048, 0.12, "Cu Ka"), (8.639, 0.07, "Zn Ka"),
             (2.984, 0.18, "Ag La (tube)")]
    y = 0.035 + 0.05 * np.exp(-((x - 6.5) / 3.0) ** 2)
    for mu, h, _ in lines:
        sig = 0.045 + 0.012 * mu                      # an SDD's peak width grows with energy
        y = y + _gauss(x, mu, sig, h)
    peaks = [(mu, lab) for mu, _, lab in lines if lab]
    _spectrum_panel(img, scale, alpha, title="EDXRF spectrum of an Al-Si powder (illustrative)",
                    xlabel="energy (keV)", x=x, y=y, peaks=peaks, xticks=(1, 2, 4, 6, 8, 10),
                    note="Illustrative: real line energies, made-up intensities. Not a measurement.")


# ===================================================================================================== registry
REGISTRY = {
    "openflexure_array": openflexure_array,
    "vhx": vhx,
    "xrf": xrf,
    "sieve": sieve,
}
# at module level, not in the builders: tour.load() may take the instruments from its cache without calling them
OVERLAYS.update(vhx=_libs_panel, xrf=_xrf_panel, sieve=_sieve_panel)
