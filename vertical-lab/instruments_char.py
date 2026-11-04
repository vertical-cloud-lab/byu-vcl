"""Characterization instruments for round 4 of #303: an array of six OpenFlexure microscopes on one sub-tray, a Keyence
digital microscope with its laser-induced breakdown spectroscopy (LIBS) head, a desktop XRF, and a sieve shaker for the
powder that comes out of the rePowder atomizer.

Each is an ``instruments.Instrument`` with pieces, joints and an ``actions`` script, the same pattern as
``instruments.py``; ``tour.py`` finds them through ``REGISTRY``:

    xvfb-run -a python3 tour.py openflexure_array vhx xrf sieve

Frame and units as in ``instruments.py``: mm, x to the right, y away from you facing the front, z up, origin at the
centre of the footprint. Every published figure is in a ``*_SPECS`` dict with its source; anything read off photos is
marked as an estimate there.

Spectra. The VHX, the XRF and the sieve shaker each draw a 2-D panel (a spectrum, the fractions) through their
``Instrument.overlay``, which ``tour.tour_one`` draws over every frame. The panel's opacity follows the opacity of that
instrument's ``readout`` piece, a fade joint, so the actions script decides when it shows. The spectra are
illustrative, and say so on screen.
"""
from __future__ import annotations

import functools
import math

import cadquery as cq
import numpy as np
import pyvista as pv

import instruments as I
from common import box, cyl, hose, rbox, tube  # noqa: F401  (lab_models helpers, on the path via instruments)
from instruments import Instrument, Joint, _piece, _xcyl, _ycyl

# name: (r, g, b, opacity, specular), merged into tour's MATS
# register.py's view of these models (see its docstring), filled in after each build function
ANCHORS: dict = {}
FREE: dict = {}
CHECKS: dict = {}

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

def _readout_overlay(key, draw, sc, img, scale):
    """An Instrument.overlay: draw(img, scale, alpha), a 2-D panel, at the opacity of the instrument's `readout`
    piece. Set as functools.partial(_readout_overlay, key, draw), which pickles with the instrument."""
    pre = f"{key}:readout/"                     # tour.Rig's actor names: <key>:<piece>/<material><i>
    a = max((v for n, v in sc.alpha.items() if n.startswith(pre)), default=0.0)
    if a > 0.02:
        draw(img, scale, min(1.0, a))


def _spectrum_panel(img, scale, alpha, *, title, xlabel, x, y, peaks, note, box_frac=(0.585, 0.105, 0.985, 0.60),
                    xticks=(), log=False):
    """A spectrum plot drawn with PIL: the curve, a label over each named peak, an axis and a note. `peaks` is
    [(x, label)], `box_frac` the panel (x0, y0, x1, y1) as fractions of the frame."""
    from PIL import ImageDraw
    from scene import font
    W, H = img.size
    d = ImageDraw.Draw(img, "RGBA")
    a = int(255 * alpha)
    bx0, by0, bx1, by1 = box_frac[0] * W, box_frac[1] * H, box_frac[2] * W, box_frac[3] * H
    # text is kept larger than a straight downscale in the small GIFs, but no larger than the panel holds: the title
    # has to fit across it, and the note gets smaller still if it must
    s = max(scale, min(max(scale, 0.8), (bx1 - bx0) / (d.textlength(title, font=font(14.5, bold=True)) + 20)))
    s_note = max(scale, min(s, (bx1 - bx0) / (d.textlength(note, font=font(11.5)) + 20)))
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
    d.text((bx0 + 10 * s, by1 - 17 * s), note, font=font(11.5 * s_note), fill=(150, 30, 30, a))


def _gauss(x, mu, sig, h):
    return h * np.exp(-0.5 * ((x - mu) / sig) ** 2)



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
    """{role: {rgb: PolyData}} for one microscope, in its own frame; roles body / stage / optics, and one per flexure
    leg, lever and actuator column (openflexure.mechanism's pieces)."""
    import openflexure as O
    stage = {"v7": ("xy_stage", "sample_clips"), "delta": ("moving_stage", "sample_clips")}[key]
    optics = ("optics_module_beamsplitter", "objective", "tube_lens", "picamera2_with_cover", "camera_ribbon_cable",
              "fl_cube", "reflection_illuminator_holder", "reflection_led_condenser") if key == "v7" else ()
    mech = {part: piece for piece, (parts, _) in O.mechanism(key, vec=(0.0, 0.0, 0.0)).items() for part in parts}
    out = {"body": {}, "stage": {}, "optics": {}, **{piece: {} for piece in mech.values()}}
    for name, (mesh, col, _) in O._load(key).items():
        role = "stage" if name in stage else "optics" if name in optics else mech.get(name, "body")
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
    # ---- the six microscopes: static parts, stages and (v7) optics, merged across the array by colour; each one's
    # flexure legs, levers and columns are pieces of their own, as each pivots about its own microscope's flexures
    meshes = {k: _ofm_meshes(k) for k in ("v7", "delta")}
    # the stages' rasters, within each design's flexure range (openflexure.mechanism checks them): the Delta's levers
    # allow less x/y with focus than the v7's legs, at most 0.1 rad
    scan = {"v7": ((0, 0, 0), (-6, -4, 0), (6, -4, 0), (6, 0, 0), (-6, 0, 0), (-6, 4, 0), (6, 4, 0), (0, 0, 0)),
            "delta": ((0, 0, 0), (-4, -3, 0.5), (4, -3, 0.5), (4, 0, 1.0), (-4, 0, 1.0), (-4, 3, 0.5), (4, 3, 0.5),
                      (0, 0, 0))}
    groups = {"scopes": {}, "stages_v7": {}, "stages_delta": {}, "optics_v7": {}}
    mech_joints = {}
    for i, (kind, cx, cy) in enumerate(sites):
        hull, c = hulls[kind]
        dx, dy = cx - c[0], cy - c[1]
        mech = O.mechanism(kind, path=scan[kind], offset=(dx, dy, z0), parent="plate")
        for role, cols in meshes[kind].items():
            if role in mech:
                g = f"{role}_{i}"
                mech_joints[g] = mech[role][1]
                for col, m in cols.items():
                    inst.meshes.setdefault(g, []).append((_moved(m, dx, dy, z0), col, 1.0))
                continue
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
        "stages_v7": Joint("path", parent="plate", path=scan["v7"]),
        "stages_delta": Joint("path", parent="plate", path=scan["delta"]),
        "optics_v7": Joint("path", parent="plate", path=((0, 0, 0), (0, 0, 2), (0, 0, 0.5), (0, 0, 1.5), (0, 0, 0))),
        **mech_joints,
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
        ("All six scan at once: each flexure stage rasters its coupon under the reflection optics, its legs leaning "
         "with it (+-6 mm on the v7s, +-4 mm on the Deltas). The v7s focus by moving the optics, the Deltas by "
         "moving the stage.", 4.2,
         {"stages_v7": (0.0, 1.0), "stages_delta": (0.0, 1.0), "optics_v7": (0.0, 1.0),
          **{g: (0.0, 1.0) for g in mech_joints}}),
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
    inst.overlay = functools.partial(_readout_overlay, inst.key, _sieve_panel)
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
                 xy=20.0, focus_z=49.0, stand_kg=23.8)
# The look follows Keyence's own footage, fitted with register.py (refs/vhx/, notes/refine_vhx.md): "Versatile
# User-Friendly Digital Microscope | VHX-7000N Series" (youtu.be/C4IBBj20OpE), 0:19 (front, the plain stand beside
# the monitor) and 1:25 (the EA-300 configuration, from the front right). Dark grey and black with silver flanks,
# not white: a flared pedestal base (silver skirt, dark top, VHX badge, the focus knob on its right), a dark stage
# column carrying the motorized XY stage at mid-height, a column rising at the back whose silver arch runs forward
# over the head, the EA-300 as a dark box under that arch with the VH-ZST zoom lens down its front right, and the
# controller as a monitor: a black bezel round the 27 in screen over a silver "VHX" bar on a narrower silver foot,
# with the console (jog dial, keys, joystick) in front. Sizes below are fitted or estimated; the published ones are
# in VHX_SPECS. The stand's outer size is not published, so the stage top (171 x 168 mm) and the monitor
# (625 x 460 mm, screen 596.7 x 335.7 mm) set the scale.
VHX_LOOK = dict(base_w=290.7, base_d=435.0, base_h=115.0, base_y=60.0, logo_z=73.7, knob_y=60.0,
                stage_w=213.4, stage_d=200.0, stage_h=53.4, stage_z=225.0, plate_t=6.0,
                col_w=150.0, col_d=110.0, ea_w=210.0, ea_d=280.0, ea_z=345.0, ea_h=250.0, ea_x=-30.0, arch_rise=50.0,
                mon_x=470.0, mon_y=40.0, scr_top=12.2, bez0=84.9, foot_h=33.0, foot_w=430.0)
VHX_STAGE_Y = -40.0               # the stage's centre, and the laser's axis, in front of the stand's centre
VHX_COL_Y = 225.0                 # the back column's centre


def _vhx_ea_y(p) -> float:
    """The EA-300's centre: its back against the column's front face."""
    return VHX_COL_Y - p["col_d"] / 2 - p["ea_d"] / 2 + 20.0


def vhx_anchors(p, pose=None) -> dict:
    """Points of the stand and of the monitor, from the same parameters vhx() builds them with."""
    s = VHX_SPECS
    ys = VHX_STAGE_Y
    sf = ys - p["stage_d"] / 2                      # the stage body's front face
    pw, pd = s["stage"]
    zt = p["stage_z"] + p["plate_t"]
    a = {"stage top front left": (-p["stage_w"] / 2, sf, p["stage_z"]),
         "stage top front right": (p["stage_w"] / 2, sf, p["stage_z"]),
         "stage bottom front left": (-p["stage_w"] / 2, sf, p["stage_z"] - p["stage_h"]),
         "stage bottom front right": (p["stage_w"] / 2, sf, p["stage_z"] - p["stage_h"]),
         "plate front left": (-pw / 2, ys - pd / 2, zt), "plate front right": (pw / 2, ys - pd / 2, zt),
         "base logo": (0.0, p["base_y"] - p["base_d"] / 2, p["logo_z"])}
    ey = _vhx_ea_y(p)
    ez1 = p["ea_z"] + p["ea_h"]
    for nm, (fx, fy) in {"EA top front left": (-1, -1), "EA top front right": (1, -1),
                         "EA top back right": (1, 1)}.items():
        a[nm] = (p["ea_x"] + fx * p["ea_w"] / 2, ey + fy * p["ea_d"] / 2, ez1)
    a["EA bottom front right"] = (p["ea_x"] + p["ea_w"] / 2, ey - p["ea_d"] / 2, p["ea_z"])
    a["knob end"] = (p["base_w"] / 2 + 35.0, p["base_y"] - p["base_d"] / 2 + p["knob_y"], 0.62 * p["base_h"])
    a["base front bottom"] = (0.0, p["base_y"] - (p["base_d"] + 30.0) / 2, 8.0)
    # the monitor, in its own place: each frame's view of it has its own camera pose, so where it stands doesn't matter
    mx, yf, H, W = p["mon_x"], p["mon_y"] - 15.0, s["ctrl_H"], s["ctrl_W"]
    sw, sh = s["screen"]
    a.update({"bezel top left": (mx - W / 2, yf, H), "bezel top right": (mx + W / 2, yf, H),
              "bezel bottom left": (mx - W / 2, yf, p["bez0"]), "bezel bottom right": (mx + W / 2, yf, p["bez0"]),
              "screen tl": (mx - sw / 2, yf, H - p["scr_top"]), "screen tr": (mx + sw / 2, yf, H - p["scr_top"]),
              "screen bl": (mx - sw / 2, yf, H - p["scr_top"] - sh),
              "screen br": (mx + sw / 2, yf, H - p["scr_top"] - sh)})
    return a


def _arch(y0, y1, z0, rise, w, t, x=0.0, n=28):
    """A flat bar (w across, t thick) bent into a half-ellipse in the y-z plane, from (y0, z0) up over to (y1, z0)."""
    yc, ry = (y0 + y1) / 2, abs(y1 - y0) / 2
    pts = [(yc + ry * math.cos(math.pi * k / n), z0 + rise * math.sin(math.pi * k / n)) for k in range(n + 1)]
    out = None
    for (ya, za), (yb, zb) in zip(pts[:-1], pts[1:]):
        L = math.hypot(yb - ya, zb - za) + t * 0.6
        seg = box(x - w / 2, -L / 2, -t / 2, x + w / 2, L / 2, t / 2)
        seg = seg.rotate((0, 0, 0), (1, 0, 0), math.degrees(math.atan2(zb - za, yb - ya)))
        seg = seg.translate((0, (ya + yb) / 2, (za + zb) / 2))
        out = seg if out is None else out.union(seg)
    return out


def vhx() -> Instrument:
    p = VHX_SPECS
    q = VHX_LOOK
    inst = CharInstrument("vhx", "Digital microscope with laser elemental analysis (LIBS)",
                          "Keyence VHX-7000 + EA-300", (0.0, 0.0, 0.0),
                          "Keyence VHX-7000N brochure KA1-1099 pp. 34-38 (EA-300 280 x 210 x 375 mm, 7.2 kg, 355 nm "
                          "Nd:YAG, 10 um spot, H-U; VHX-S750E stage 171 x 168 mm, XY +-20 mm; controller 625 x 460 x "
                          "180 mm); EA-300 model page; the look from Keyence's VHX-7000N video, fitted with register.py")
    sx0, ys = 0.0, VHX_STAGE_Y
    bw, bd, bh = q["base_w"], q["base_d"], q["base_h"]
    body = _piece(inst, "body")
    # the pedestal: a silver skirt flaring out at the floor, a dark top, the badge and the focus knob on its right
    by = q["base_y"]
    yb0 = by - bd / 2                                # the base's front face
    skirt = (cq.Workplane("XY").sketch().rect(bw + 40, bd + 30).vertices().fillet(60).finalize()
             .extrude(0.5 * bh, taper=math.degrees(math.atan2(20.0, 0.5 * bh))))
    body.add("base skirt", skirt.translate((sx0, by, 8)), "char_vhx_silver")
    lean = math.atan2(20.0, 0.5 * bh)                # the skirt's front leans back as it tapers: dark between the flanks
    panel = box(-0.3 * bw, 0, 0, 0.3 * bw, 3, math.hypot(20.0, 0.5 * bh)).rotate((0, 0, 0), (1, 0, 0), -math.degrees(lean))
    body.add("base front", panel.translate((sx0, by - (bd + 30) / 2 - 1.5, 8)), "char_vhx_dark")
    body.add("base top", rbox(bw - 10, bd - 10, bh - 0.5 * bh - 8, 40, x=sx0, y=by, z=0.5 * bh + 8)
             .edges(">Z").fillet(12), "char_vhx_dark")
    for fx in (-1, 1):
        for fy in (-1, 1):
            body.add(f"foot {fx} {fy}", cyl(50, 8, x=sx0 + fx * (bw / 2 - 10), y=by + fy * (bd / 2 - 25)),
                     "char_vhx_dark")
    body.add("base badge", box(sx0 - 30, yb0 + 4, q["logo_z"] - 6, sx0 + 30, yb0 + 5, q["logo_z"] + 6), "inst_light")
    body.add("base light", box(sx0 - 22, yb0 + 4, q["logo_z"] + 16, sx0 + 22, yb0 + 5, q["logo_z"] + 20),
             "char_vhx_blue")
    body.add("focus knob", _xcyl(46, 40, x=sx0 + bw / 2 - 5, y=yb0 + q["knob_y"], z=0.62 * bh), "char_vhx_dark")
    body.add("knob ring", _xcyl(52, 8, x=sx0 + bw / 2 - 8, y=yb0 + q["knob_y"], z=0.62 * bh), "char_vhx_silver")
    # the stage column and the motorized XY stage at mid-height (stage top 171 x 168 mm, its theta disk 100 mm)
    sz, sh_ = q["stage_z"], q["stage_h"]
    body.add("stage column", cyl(130, sz - sh_ - bh + 2, x=sx0, y=ys + 10, z=bh - 1), "char_vhx_dark")
    body.add("stage column band", cyl(134, 14, x=sx0, y=ys + 10, z=sz - sh_ - 40), "char_vhx_grey")
    body.add("XY stage", rbox(q["stage_w"], q["stage_d"], sh_, 6, x=sx0, y=ys, z=sz - sh_).edges(">Z").fillet(4),
             "char_vhx_dark")
    body.add("stage badge", box(sx0 - 55, ys - q["stage_d"] / 2 - 0.6, sz - sh_ / 2 - 4, sx0 - 5,
                                ys - q["stage_d"] / 2, sz - sh_ / 2 + 4), "inst_light")
    zs = sz + q["plate_t"]                           # the top of the stage plate
    body.add("stage plate", rbox(p["stage"][0], p["stage"][1], q["plate_t"], 4, x=sx0, y=ys, z=sz), "char_vhx_grey")
    body.add("stage disk", cyl(p["disk"], 1.0, x=sx0, y=ys, z=zs), "inst_grey")
    # the back column, and its silver arch running forward over the head
    cw, cd = q["col_w"], q["col_d"]
    ez0, ez1 = q["ea_z"], q["ea_z"] + q["ea_h"]
    ctop = ez1 - 30.0
    body.add("column", rbox(cw, cd, ctop - bh + 5, 30, x=sx0, y=VHX_COL_Y, z=bh - 5), "char_vhx_dark")
    for fx in (-1, 1):
        body.add(f"column flank {fx}", box(sx0 + fx * cw / 2 - 6, VHX_COL_Y - cd / 2 + 15, bh + 20,
                                           sx0 + fx * cw / 2 + 6, VHX_COL_Y + cd / 2 - 15, ctop - 20),
                 "char_vhx_silver")
    # the free-angle head: the EA-300 under the arch, the VH-ZST zoom lens down its front right, the reflective
    # objective under its centre; it all tilts about the focal point
    zf = zs + 1.0 + 12.6                             # the sample surface: a 12.6 mm mounted coupon on the stage disk
    pivot = (sx0, ys, zf)
    head = _piece(inst, "head")
    ex, ey = sx0 + q["ea_x"], _vhx_ea_y(q)
    eW, eD = q["ea_w"], q["ea_d"]                    # narrow side to the front, as the footage shows it
    head.add("EA-300", rbox(eW, eD, q["ea_h"], 22, x=ex, y=ey, z=ez0).edges(">Z").fillet(14), "char_vhx_dark")
    head.add("EA-300 side panel", box(ex + eW / 2 - 1, ey - eD / 2 + 30, ez0 + 30, ex + eW / 2 + 1.5, ey + eD / 2 - 20,
                                      ez1 - 25), "char_vhx_grey")
    head.add("EA-300 badge", box(ex - 30, ey - eD / 2 - 0.6, ez1 - 70, ex + 30, ey - eD / 2, ez1 - 62), "inst_light")
    body.add("arch", _arch(VHX_COL_Y + cd / 2 - 10, ey - eD / 2 + 25, ctop - 10, q["arch_rise"] + 40, 46, 22, x=sx0),
             "char_vhx_silver")                     # the column's, so it stays put as the head tilts under it
    head.add("objective", cyl(44, ez0 - (zf + p["wd"]), x=sx0, y=ys, z=zf + p["wd"]), "char_vhx_dark")
    head.add("objective ring", cyl(50, 6, x=sx0, y=ys, z=zf + p["wd"] + 4), "chrome")
    lx, ly = ex + eW / 2 - 35, ey - eD / 2 - 32      # the VH-ZST, on the EA-300's front right
    head.add("VH-ZST zoom lens", cyl(54, ez1 - 60 - (ez0 - 40), x=lx, y=ly, z=ez0 - 40), "char_vhx_silver")
    head.add("zoom lens grip", cyl(58, 90, x=lx, y=ly, z=ez0 + 40), "char_vhx_dark")
    head.add("lens nose", cyl(46, 40, x=lx, y=ly, z=ez0 - 80), "char_vhx_dark")
    head.add("lens joint", box(lx - 20, ly, ez0 + 140, lx + 20, ey - eD / 2 + 2, ez0 + 175), "char_vhx_grey")
    body.add("cable", hose([(sx0 - cw / 2 + 20, VHX_COL_Y + cd / 2, ctop - 60),
                            (sx0 - cw / 2 + 20, VHX_COL_Y + cd / 2 + 40, ctop - 60),
                            (sx0 + 200, VHX_COL_Y + cd / 2 + 40, 40), (q["mon_x"], VHX_COL_Y + cd / 2 + 40, 40)], 10),
             "char_cable")
    # the controller: a 27 in monitor on a silver "VHX" bar and foot, and its console in front
    cx, cy = q["mon_x"], q["mon_y"]
    W, H, sw, sh = p["ctrl_W"], p["ctrl_H"], p["screen"][0], p["screen"][1]
    ctrl = _piece(inst, "controller")
    ctrl.add("controller foot", rbox(q["foot_w"], p["ctrl_D"], q["foot_h"], 30, x=cx, y=cy + 10).edges(">Z").fillet(8),
             "char_vhx_silver")
    ctrl.add("VHX bar", rbox(W, 60, q["bez0"] - q["foot_h"] + 6, 12, x=cx, y=cy, z=q["foot_h"] - 4)
             .edges("<Z and |X").fillet(16), "char_vhx_silver")
    yf = cy - 15.0
    ctrl.add("bezel", rbox(W, 30, H - q["bez0"], 8, x=cx, y=cy, z=q["bez0"]), "inst_black")
    ctrl.add("back", rbox(W - 60, 70, H - q["bez0"] - 60, 30, x=cx, y=cy + 45, z=q["bez0"] + 10), "char_vhx_dark")
    ctrl.add("screen", box(cx - sw / 2, yf - 0.8, H - q["scr_top"] - sh, cx + sw / 2, yf, H - q["scr_top"]),
             "screen_on")
    ctrl.add("VHX badge", box(cx - 25, cy - 30.6, q["bez0"] - 22, cx + 25, cy - 30, q["bez0"] - 12), "inst_dark")
    kx, ky = cx - 20, cy - 200                       # the console: jog dial, keys and joystick
    ctrl.add("console", rbox(215, 100, 34, 20, x=kx, y=ky).edges(">Z").fillet(6), "char_vhx_silver")
    ctrl.add("console keys", rbox(130, 66, 4, 6, x=kx - 5, y=ky - 5, z=34), "char_vhx_dark")
    ctrl.add("jog dial", _xcyl(44, 30, x=kx - 107.5 - 28, y=ky - 10, z=26), "char_vhx_dark")
    ctrl.add("joystick", cyl(14, 50, x=kx + 85, y=ky + 15, z=34).union(
        cq.Workplane("XY").sphere(11).translate((kx + 85, ky + 15, 88))), "char_vhx_dark")
    # the sample, the laser and the plasma
    smp = _piece(inst, "sample")
    smp.add("mount", cyl(30, 12, z=0), "mount")
    smp.add("polished face", cyl(22, 0.6, z=12), "sample")
    inst.joints = {
        # in under the objective's nose, then down onto the stage disk (its top at zs + 1)
        "sample": Joint("path", path=((sx0, ys - 280, zs + 150), (sx0, ys - 120, zs + 14), (sx0, ys, zs + 6),
                                      (sx0, ys, zs + 1))),
        "head": Joint("hinge", axis=(0, 1, 0), pivot=pivot, deg=-35.0, parent="focus"),
        "laser": Joint("fade"),
        "plasma": Joint("fade"),
        "readout": Joint("fade"),
    }
    inst.meshes["focus"] = _dummy((sx0, ys, zf))
    inst.joints["focus"] = Joint("path", path=((0, 0, 0), (0, 0, -6), (0, 0, 6), (0, 0, 0)))
    las = _piece(inst, "laser")
    las.add("beam", cyl(6.0, p["wd"], x=sx0, y=ys, z=zf), "laser")
    pl = _piece(inst, "plasma")
    pl.add("plasma core", cq.Workplane("XY").sphere(2.4).translate((sx0, ys, zf + 1.5)), "plasma")
    pl.add("plasma glow", cq.Workplane("XY").sphere(14.0).translate((sx0, ys, zf + 3.0)), "plasma_halo")
    inst.meshes["readout"] = _dummy((cx, cy, 300))
    inst.aside = ("readout", "controller")
    inst.props = ("sample",)
    top = ctop - 10 + q["arch_rise"] + 40 + 11      # the arch's crown
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
        (f"The EA-300 adds 7.2 kg to the stand. Stand and head are about {top:.0f} mm tall: under Kardex's 727.5 mm.",
         2.4, {"plasma": (0.3, 0.0), "readout": (1.0, 0.0)}),
    ]
    inst.labels = [("EA-300 LIBS head", (ex - eW / 2, ey - eD / 2, ez1 - 60), (0.10, 0.25)),
                   ("VH-ZST zoom lens", (lx + 27, ly, ez0 + 80), (0.42, 0.14)),
                   ("motorized XY stage", (sx0 - q["stage_w"] / 2, ys - q["stage_d"] / 2, sz - 20), (0.08, 0.72)),
                   ("controller, 27 in 4K screen", (cx - 250, yf, H - 60), (0.84, 0.80)),
                   ("laser spot", (sx0, ys - 15, zf + 2), (0.12, 0.50))]
    inst.anchors = vhx_anchors(q)
    inst.cam = (0.55, -1.7, 0.62)
    inst.framing = (0.95, 0.46)
    bb = inst.bbox()
    inst.size = (round(bb[1] - bb[0]), round(bb[3] - bb[2]), round(bb[5] - bb[4]))
    inst.overlay = functools.partial(_readout_overlay, inst.key, _libs_panel)
    return inst


# register.py: the stand's and the monitor's anchors, fitted to Keyence's video (refs/vhx/)
ANCHORS["vhx"] = (VHX_LOOK, vhx_anchors)
FREE["vhx"] = ["base_w", "logo_z", "stage_w", "stage_h", "stage_z", "scr_top", "bez0"]   # depths aren't seen: not fitted
CHECKS["vhx"] = lambda q: [q["stage_z"] - q["stage_h"] - q["base_h"] - 20, q["ea_z"] - q["stage_z"] - 70,
                           727.5 - (q["ea_z"] + q["ea_h"] + q["arch_rise"] + 21), q["bez0"] - q["foot_h"] - 15,
                           VHX_SPECS["ctrl_H"] - q["scr_top"] - VHX_SPECS["screen"][1] - q["bez0"] - 10]
MATERIALS["char_vhx_dark"] = (0.14, 0.145, 0.16, 1.0, 0.45)      # the VHX stand's near-black
MATERIALS["char_vhx_grey"] = (0.36, 0.37, 0.40, 1.0, 0.45)
MATERIALS["char_vhx_silver"] = (0.74, 0.75, 0.77, 1.0, 0.70)     # its brushed-silver flanks, arch and bars
MATERIALS["char_vhx_blue"] = (0.30, 0.55, 1.00, 1.0, 0.2)        # the blue status light


MATERIALS["plasma_halo"] = (0.85, 0.80, 1.00, 0.35, 0.0)
MATERIALS["xrf_window"] = (0.20, 0.22, 0.26, 0.80, 0.6)        # the S2 PUMA hood's dark window


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


# The exterior follows Bruker's own "S2 PUMA Overview" video (youtu.be/ogSg0j6j2Gw, 0:08-0:16, the XY Autochanger),
# fitted with register.py (refs/xrf/): a full-width white hood over the top 44 % with a dark window in its top and
# BRUKER at its front right, hinged at the back; under it a white body whose vertical front holds the touch screen,
# left of centre, with "S2 PUMA" up its right edge; navy side panels; dark feet. (It was a small dark lid on a sloped
# white body, with the screen on top.)
XRF_LOOK = dict(deck=322.0, side_t=45.0, scr_w=253.0, scr_h=184.0, scr_x=-17.0, scr_z=172.0, win_w=300.0,
                win_y0=40.0, win_d=150.0)


def xrf_anchors(p, pose=None) -> dict:
    W, D, H = XRF_SPECS["W"], XRF_SPECS["D"], XRF_SPECS["H"]
    yf, dk = -D / 2, p["deck"]
    a = {"lid top front left": (-W / 2 + 5, yf + 5, H), "lid top front right": (W / 2 - 5, yf + 5, H),
         "lid bottom front left": (-W / 2 + 5, yf + 5, dk + 4), "lid bottom front right": (W / 2 - 5, yf + 5, dk + 4),
         "lid top back right": (W / 2 - 5, D / 2 - 5, H), "foot front left": (-W / 2, yf, 15.0),
         "foot front right": (W / 2, yf, 15.0),
         "window front left": (-p["win_w"] / 2, yf + p["win_y0"], H), "window front right": (p["win_w"] / 2, yf + p["win_y0"], H),
         "window back left": (-p["win_w"] / 2, yf + p["win_y0"] + p["win_d"], H),
         "window back right": (p["win_w"] / 2, yf + p["win_y0"] + p["win_d"], H)}
    for nm, (fx, fz) in {"screen tl": (-1, 1), "screen tr": (1, 1), "screen bl": (-1, -1), "screen br": (1, -1)}.items():
        a[nm] = (p["scr_x"] + fx * p["scr_w"] / 2, yf, p["scr_z"] + fz * p["scr_h"] / 2)
    return a


def xrf() -> Instrument:
    p = XRF_SPECS
    q = XRF_LOOK
    W, D, H = p["W"], p["D"], p["H"]
    inst = CharInstrument("xrf", "Benchtop EDXRF for powders and coupons", "Bruker S2 PUMA Series 2, XY Autochanger",
                          (W, D, H), "Bruker S2 PUMA Series 2 specifications via DKSH (XY Autochanger 67 x 71 x 61 cm, "
                          "108 kg; 20-position tray; 50 W Pd/Ag tube; HighSense SDD; reduced-pressure He for loose "
                          "powders); the look from Bruker's S2 PUMA Overview video, fitted with register.py")
    yf, yb = -D / 2, D / 2
    deck = q["deck"]                              # the top of the body: the sample deck under the hood
    st = q["side_t"]
    body = _piece(inst, "body")
    feet = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            f_ = cyl(40, 15, x=sx * (W / 2 - 60), y=sy * (D / 2 - 60))
            feet = f_ if feet is None else feet.union(f_)
    body.add("feet", feet, "inst_black")
    body.add("housing", box(-W / 2 + st, yf, 15, W / 2 - st, yb - 5, deck).edges("|Y").fillet(4), "inst_white")
    body.add("side panels", box(-W / 2, yf + 8, 15, -W / 2 + st, yb, deck - 2).edges("|Y").fillet(8).union(
        box(W / 2 - st, yf + 8, 15, W / 2, yb, deck - 2).edges("|Y").fillet(8)), "inst_navy")
    sx0, sx1 = q["scr_x"] - q["scr_w"] / 2, q["scr_x"] + q["scr_w"] / 2
    sz0, sz1 = q["scr_z"] - q["scr_h"] / 2, q["scr_z"] + q["scr_h"] / 2
    body.add("screen bezel", box(sx0 - 8, yf - 1.5, sz0 - 8, sx1 + 8, yf, sz1 + 8), "inst_dark")
    body.add("touch screen", box(sx0, yf - 2.2, sz0, sx1, yf - 1.5, sz1), "nat_screen")
    body.add("S2 PUMA label", box(W / 2 - st - 50, yf - 0.8, sz0 + 10, W / 2 - st - 30, yf, sz1), "inst_light")
    body.add("status light", box(-W / 2 + st + 10, yf - 1, deck - 14, -W / 2 + st + 70, yf, deck - 10), "inst_orange")
    deck_plate = box(-W / 2 + st + 10, yf + 30, deck - 15, W / 2 - st - 10, yb - 60, deck + 1)
    # the XY sample tray: 4 x 5 = 20 cups' seats, removable
    tx, ty = 40.0, (yf + 30 + yb - 60) / 2 + 30
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
    hood = rbox(W - 10, D - 10, H - deck - 4, 10, z=deck + 4).edges(">Z").fillet(8)
    hood = hood.cut(rbox(W - 26, D - 26, H - deck - 12, 6, z=deck + 3))
    hood = hood.cut(box(-q["win_w"] / 2, yf + q["win_y0"], H - 20, q["win_w"] / 2, yf + q["win_y0"] + q["win_d"], H + 1))
    lid.add("hood", hood, "inst_white")
    lid.add("hood window", box(-q["win_w"] / 2, yf + q["win_y0"], H - 9, q["win_w"] / 2, yf + q["win_y0"] + q["win_d"],
                               H - 7), "xrf_window")
    lid.add("BRUKER badge", box(W / 2 - 150, yf + 4, deck + 120, W / 2 - 50, yf + 5, deck + 150), "inst_navy")
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
    hinge_y = yb - 5
    s0 = seats[2]
    # down in front of the lid, in under its front edge (the lid opens only 35 degrees: coming in from above, the cup
    # clipped that edge, collide.py), then down into the seat
    path = ((s0[0] - 60, yf - 260, H + 220), (s0[0], yf - 40, H + 90), (s0[0], s0[1] - 30, H + 90),
            (s0[0], s0[1], deck + 40),
            (s0[0], s0[1], deck + 3), (s0[0], s0[1], deck + 40), (mx, my, deck + 40), (mx, my, deck + 2))
    seg = np.linalg.norm(np.diff(np.asarray(path), axis=0), axis=1)
    v_seat = float(seg[:4].sum() / seg.sum())          # the cup down in its seat, at deck + 3
    inst.joints = {
        "lid": Joint("hinge", axis=(1, 0, 0), pivot=(0, hinge_y, H - 10), deg=-XRF_LID_DEG),
        "sample": Joint("path", path=path),
        "beam": Joint("fade"),
        "readout": Joint("fade"),
    }
    inst.aside = ("readout",)
    inst.props = ("sample", "beam")
    inst.actions = [
        ("The hood lifts on its rear hinge, uncovering the XY Autochanger's 20-position tray.", 2.2,
         {"lid": (0.0, 1.0), "sample": (0.0, 0.0), "beam": (0.0, 0.0), "readout": (0.0, 0.0)}),
        ("A cup of atomized powder, closed underneath by a thin prolene film, goes into a free seat.", 2.6,
         {"sample": (0.0, v_seat)}),
        ("Hood down; drawn see-through.", 1.6, {"lid": (1.0, 0.0), "~body": (0.0, 1.0), "~lid": (0.0, 1.0)}),
        ("The changer takes the cup to the measuring position, film side down over the window: the tube and the "
         "detector are underneath. Helium at reduced pressure keeps loose powder in place.", 2.8,
         {"sample": (v_seat, 1.0)}),
        ("The beam, drawn see-through: up to 50 kV and 50 W from the tube; each element in the powder answers with "
         "its own X-ray lines, which the silicon drift detector counts.", 3.0, {"beam": (0.0, 1.0)}),
        ("The spectrum: peaks at each element's lines give the composition, Na to Am, in minutes.", 4.8,
         {"readout": (0.0, 1.0)}),
    ]
    inst.labels = [("hood, hinged at the back", (-W / 2 + 60, yf + 200, H - 5), (0.10, 0.22)),
                   ("20-position XY tray", (tx - 140, ty, deck + 12), (0.10, 0.52)),
                   ("touch screen", (sx1, yf - 2, q["scr_z"]), (0.86, 0.74))]
    inst.anchors = xrf_anchors(q)
    inst.cam = (0.75, -1.75, 0.9)
    inst.framing = (0.95, 0.50)
    # how tall the lid stands open, against the ~844 mm between a presented tray's floor and the opening's header
    lb = lid.bbox()
    corners = np.array([[x, y, z] for x in (lb.xmin, lb.xmax) for y in (lb.ymin, lb.ymax) for z in (lb.zmin, lb.zmax)])
    m = I._R((1, 0, 0), -XRF_LID_DEG, (0, hinge_y, H - 10))
    top = float((corners @ m[:3, :3].T + m[:3, 3])[:, 2].max())
    inst.notes = [f"lid drawn opening {XRF_LID_DEG:.0f} deg: its front edge rises to {top:.0f} mm (estimate)"]
    inst.overlay = functools.partial(_readout_overlay, inst.key, _xrf_panel)
    return inst



# register.py: the S2 PUMA's anchors and the parts of its look fitted to Bruker's video (refs/xrf/)
ANCHORS["xrf"] = (XRF_LOOK, xrf_anchors)
FREE["xrf"] = ["deck", "scr_w", "scr_h", "scr_x", "scr_z"]     # the window isn't picked: it isn't fitted
CHECKS["xrf"] = lambda q: [q["deck"] - q["scr_z"] - q["scr_h"] / 2 - 30, q["scr_z"] - q["scr_h"] / 2 - 40,
                           XRF_SPECS["H"] - q["deck"] - 150]

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
