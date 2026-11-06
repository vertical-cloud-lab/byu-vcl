"""Round 8, the powder stream (#303, PR #318): the XRD, the laser-diffraction sizer and the XRF, refitted for the
powder chapter (``alloy_powder.py``) and their tour clips. ``tour.load()`` lets this module's REGISTRY replace the
older builders' keys, so these are the models in every scene that loads them.

    xvfb-run --server-num=13 -a python3 tour.py xrd mastersizer xrf

* **xrd, the Rigaku MiniFlex.** ``instruments.xrd()`` with: the door's panel drawn see-through from the first frame (a
  tinted window in a navy frame); the goniometer still until the door is shut and the X-ray lamp is lit; the scan a
  true theta-2theta (theta 5 to 45 deg as 2theta runs 10 to 90 deg), the incident and diffracted beams drawn; a
  camera from the front that shows the sample and both arms; a zero-background holder (a single-crystal Si plate with
  a shallow well) on the stage instead of the plain glass slide; and the computed pattern as the readout.
* **mastersizer, the Mastersizer 3000 + Aero S.** ``instruments.mastersizer()`` with the optical bench inside drawn
  for a cutaway: the red laser and the blue LED, the beam expander, the focusing lens (Malvern's reverse-Fourier
  design: the beam converges through the cell onto the focal-plane detector), the cell, the back-scatter and
  large-angle detectors, the focal-plane detector's log-spaced arcs; the light scattered by large particles (narrow,
  onto the inner arcs) and by small ones (wide, to the large-angle detectors); the particles in the cell; the PSD as
  the readout.
* **xrf, the Bruker S2 PUMA Series 2.** See ``xrf()``.

The data panels the readouts show are ``r8_powder_data.py``'s.
"""
from __future__ import annotations

import math

import cadquery as cq
import numpy as np
import pyvista as pv

import instruments as I
from common import box, cyl, rbox, tube  # noqa: F401  (lab_models helpers, on the path via instruments)
from instruments import Joint, _piece, _xcyl, _ycyl

MATERIALS = {
    "r8_door_glass": (0.20, 0.22, 0.34, 0.16, 0.9),     # the MiniFlex door's panel, drawn see-through
    "r8_si_wafer": (0.27, 0.28, 0.36, 1.0, 0.95),       # single-crystal Si, polished: a dark violet-grey mirror
    "r8_xray": (0.55, 0.85, 0.35, 0.35, 0.0),           # an X-ray beam drawn see-through
    "r8_xray_d": (0.30, 0.65, 0.95, 0.35, 0.0),         # the diffracted beam
    "r8_scat_large": (1.00, 0.55, 0.10, 0.30, 0.0),     # light scattered by large particles (narrow angles)
    "r8_scat_small": (0.30, 0.45, 1.00, 0.22, 0.0),     # by small particles (wide angles)
    "r8_blue": (0.25, 0.45, 1.00, 1.0, 0.1),            # the blue LED
    "r8_det": (0.10, 0.12, 0.16, 1.0, 0.6),             # detector silicon
    "r8_arc": (0.55, 0.57, 0.62, 1.0, 0.5),             # a detector arc, dark
    "r8_arc_lit": (1.00, 0.45, 0.15, 1.0, 0.1),         # an arc receiving light
    "r8_lens": (0.80, 0.90, 0.97, 0.40, 0.9),
    "r8_ptfe": (0.97, 0.97, 0.95, 1.0, 0.15),
    "r8_film": (0.90, 0.93, 0.95, 0.45, 0.9),
}


def _dummy(at=(0.0, 0.0, 0.0)):
    """An invisible speck, so a fade-only piece (the readout) has a group in tour.Rig."""
    return [(pv.Sphere(radius=0.5, center=at, theta_resolution=4, phi_resolution=4), (1.0, 1.0, 1.0), 0.0)]


def _cone(a, b, ra, rb):
    """A truncated cone from point a (radius ra) to point b (radius rb)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    L = float(np.linalg.norm(b - a))
    d = (b - a) / L
    return cq.Workplane("XY").add(cq.Solid.makeCone(ra, rb, L, cq.Vector(*a), cq.Vector(*d)))


# ===================================================================================================== XRD
# The zero-background holder: a single-crystal Si plate cut off a low-index plane (Si(510) is the usual), so it
# diffracts nothing into the scan, in an aluminium carrier the size of the MiniFlex's standard holder (estimate). The
# well is 20 mm across and 0.5 mm deep: enough powder to be "infinitely thick" for Al-12Si (0.2 mm gives 99 % at
# 2theta = 90 deg, r8_powder_data.thick_enough) and a flat, level face to strike off flush with the carrier's top,
# which is the goniometer's reference plane. Our choice; plain plates and other wells are sold.
ZBH = dict(w=44.0, l=52.0, t=2.5, si_d=32.0, si_t=2.0, well_d=20.0, well=0.5,
           fin_w=14.0, fin_d=8.0, fin_h=30.0, fin_y=-36.0)
# Round 8, continuation (alloy_powder.py): the arm carries the holder by an upright fin on a tab at its front edge, 30 mm
# in front of the well, so the gripper's fingers close across the fin (14 mm) and never reach under the carrier, and
# nothing of the gripper is near the beam's plane. Our design, as is the rest of the holder's carrier.
SCAN = (10.0, 90.0)                 # 2theta, deg
DET_REST = 10.0                     # the detector's 2theta as modelled (instruments.xrd)
V_START = (SCAN[0] / 2) / 45.0      # the stage's joint value at theta = 5 deg (its joint runs to 45 deg)


def zbh_parts() -> dict:
    """{name: (shape, material)} of the zero-background holder, in its own frame: the carrier's underside centre."""
    p = ZBH
    carrier = box(-p["w"] / 2, -p["l"] / 2, 0, p["w"] / 2, p["l"] / 2, p["t"]).edges("|Z").fillet(3).cut(
        cyl(p["si_d"] + 0.4, p["si_t"] + 1, z=p["t"] - p["si_t"]))
    fy0 = p["fin_y"] - p["fin_d"] / 2
    tab = box(-p["fin_w"] / 2, fy0, 0, p["fin_w"] / 2, -p["l"] / 2 + 1, p["t"])      # a tab to hold it by,
    fin = box(-p["fin_w"] / 2, fy0, 0, p["fin_w"] / 2, fy0 + p["fin_d"], p["fin_h"])  # with a fin the gripper holds
    si = cyl(p["si_d"], p["si_t"], z=p["t"] - p["si_t"]).cut(cyl(p["well_d"], p["well"] + 0.1, z=p["t"] - p["well"]))
    return {"carrier": (carrier.union(tab).union(fin), "aluminium"), "Si plate": (si, "r8_si_wafer")}


def zbh_powder() -> cq.Workplane:
    p = ZBH
    return cyl(p["well_d"] - 0.1, p["well"], z=p["t"] - p["well"])


def xrd() -> I.Instrument:
    inst = I.xrd()
    p = I.XRD
    g = I._miniflex(p)
    yf, gy, gz = g["yf"], g["gy"], g["gz"]
    px, seam, dt = p["panel_x"], p["seam_z"], p["door_t"]
    # the door: a navy frame round a see-through panel, the handle and the label as before
    door = I.Model("xrd_door", "MiniFlex: door")
    dz0, dz1 = seam + 1, p["door_top"] - 1
    wx0, wx1, wz0, wz1 = -px + 42, px - 30, seam + 48, p["door_top"] - 26
    frame = box(-px + 1, yf - 3, dz0, px - 1, yf + 6, dz1).cut(box(wx0, yf - 4, wz0, wx1, yf + 7, wz1))
    door.add("door frame", frame, "rigaku_navy")
    door.add("door window", box(wx0, yf - 1, wz0, wx1, yf + 3, wz1), "r8_door_glass")
    door.add("MiniFlex label", box(-58, yf - 4, seam + 14, 58, yf - 3, seam + 34), "inst_light")
    hx, hz0, hz1 = p["handle_x"], p["handle_z0"], p["handle_z1"]
    door.add("door handle", box(hx - 5, yf - 29, hz0, hx + 5, yf - 23, hz1).union(
        box(hx - 5, yf - 29, hz0, hx + 5, yf - 3, hz0 + 10)).union(box(hx - 5, yf - 29, hz1 - 10, hx + 5, yf - 3, hz1)),
        "chrome")
    inst.pieces["door"] = door
    # the zero-background holder, in place of the glass slide (its frame: the carrier's underside centre)
    holder = I.Model("xrd_holder", "MiniFlex: zero-background holder")
    for nm, (shape, mat) in zbh_parts().items():
        holder.add(nm, shape, mat)
    holder.add("powder", zbh_powder(), "powder")
    inst.pieces["holder"] = holder
    # the beams: incident from the tube's window to the sample; diffracted from the sample to the detector, riding on
    # the detector's arm (modelled at 2theta = 10 deg)
    tube_x0 = -p["gonio_r"]
    ib = _piece(inst, "ibeam")
    ib.add("incident beam", _cone((tube_x0 + 40, gy, gz), (0, gy, gz), 2.0, 7.0), "r8_xray")
    db = _piece(inst, "dbeam")
    t = math.radians(DET_REST)
    r = p["gonio_r"]
    db.add("diffracted beam", _cone((0, gy, gz), (r * math.cos(t) - 12, gy, gz + (r - 12) * math.sin(t)), 7.0, 2.5),
           "r8_xray_d")
    inst.meshes["readout"] = _dummy((0, 0, p["H"]))
    j = inst.joints
    j["stage"] = Joint("hinge", axis=(0, 1, 0), pivot=(0, gy, gz), deg=-45.0)          # theta, to 45 deg
    j["detector"] = Joint("hinge", axis=(0, 1, 0), pivot=(0, gy, gz), deg=-(SCAN[1] - DET_REST))   # 2theta to 90
    j["ibeam"] = Joint("fade")
    j["dbeam"] = Joint("fade", parent="detector")
    j["readout"] = Joint("fade")
    # the holder by hand in the tour, as before; in the chapter the arm carries it (alloy_powder.py)
    j["holder"] = Joint("path", parent="stage", path=((-200, -520, gz + 60), (0, yf - 40, gz + 40),
                                                      (0, gy - 60, gz - 3 + 40), (0, gy, gz - 3)))
    inst.props = ("holder", "glow", "ibeam", "dbeam")
    inst.aside = ("readout",)
    off = {"stage": (0.0, 0.0), "detector": (0.0, 0.0), "glow": (0.0, 0.0), "ibeam": (0.0, 0.0),
           "dbeam": (0.0, 0.0), "readout": (0.0, 0.0)}
    inst.actions = [
        ("The door, drawn see-through, swings open on its right-hand hinge. The goniometer stands still at its load "
         "position: nothing moves inside until the door is locked and the X-rays are on.", 1.8,
         {"door": (0.0, 1.0), "holder": (0.0, 0.0), **off}),
        ("The prepared holder goes onto the stage by hand: a zero-background plate, single-crystal Si, with the "
         "powder struck off flush in its well, so the powder's face is on the goniometer's axis.", 2.2,
         {"holder": (0.0, 1.0)}),
        ("Door shut and DOOR LOCK pressed.", 1.4, {"door": (1.0, 0.0)}),
        ("Only then does the interlock let the 600 W tube switch on: the X-ray lamp on top lights.", 1.2,
         {"glow": (0.0, 1.0)}),
        ("The goniometer drives to its start, theta 5 deg and 2theta 10 deg, and the shutter opens: the incident "
         "beam from the tube on the left.", 1.6, {"stage": (0.0, V_START), "ibeam": (0.0, 1.0), "~hood": (0.0, 1.0)}),
        ("The scan, the housing drawn see-through: the tube stays put, the sample tilts by theta and the detector on "
         "the right sweeps 2theta from 10 to 90 deg, counting the diffracted beam.", 4.6,
         {"stage": (V_START, 1.0), "detector": (0.0, 1.0), "dbeam": (0.0, 1.0), "readout": (0.0, 1.0)}),
        ("Shutter shut and X-rays off, the lamp out; the goniometer goes back to its load position. The door stays "
         "locked until then.", 1.8, {"stage": (1.0, 0.0), "detector": (1.0, 0.0), "ibeam": (1.0, 0.0),
                                     "dbeam": (1.0, 0.0), "glow": (1.0, 0.0), "~hood": (1.0, 0.0)}),
        ("Door open, the holder out.", 2.0, {"door": (0.0, 1.0), "holder": (1.0, 0.0)}),
        ("Door shut. At 722 mm tall the MiniFlex just fits a tray: Kardex allows 727.5 mm.", 1.4,
         {"door": (1.0, 0.0), "readout": (1.0, 0.0)}),
    ]
    inst.labels = [("X-ray tube (fixed)", (tube_x0 - 50, gy, gz + 50), (0.10, 0.30)),
                   ("detector on the 2theta arm", (150, gy, gz + 40), (0.90, 0.30)),
                   ("zero-background holder", (0, gy - 20, gz), (0.16, 0.70))]
    inst.cam = (0.32, -1.7, 0.42)
    inst.framing = (0.80, 0.55)
    inst.zoom = {4: ((0, gy, gz + 10), 820.0), 6: "out"}
    inst.step_labels = {5: [("X-ray tube (fixed)", (tube_x0 - 50, gy, gz + 50), (0.12, 0.26)),
                            ("detector, 2theta", (150, gy, gz + 40), (0.88, 0.26)),
                            ("sample, theta", (0, gy - 25, gz), (0.20, 0.74))]}
    return inst


# ===================================================================================================== laser diffraction
# The optical bench inside, after Malvern's description of the Mastersizer 3000 (a red He-Ne laser at 632.8 nm and a
# blue LED at 470 nm; "reverse Fourier" optics, the beam focused before the cell so it converges through it onto the
# focal-plane detector; log-spaced arcs on that detector for the forward angles, large-angle and back-scatter
# detectors for the wide ones). Its layout here is schematic: Malvern publishes no drawing of the bench's insides, and
# the real one folds its path. The cell is the model's (in the bay), the beam along x at the cell's windows.
MSO = dict(laser=(-530.0, -445.0), r_laser=16.0, exp=(-428.0, -404.0), lens_x=-372.0, lens_r=24.0, bs_x=-352.0,
           la_x=(-258.0, -236.0), fpd_x=96.0, fpd_r=40.0, narrow=14.0, wide=46.0, arcs=10)


def ms_geometry() -> dict:
    """Where the bench's optics are (instrument frame): the axis (y, z), the cell's centre, the focal point."""
    p = I.MS3000
    g = I._ms3000(p)
    cy, bz = g["yf"] + 120.0, p["fit_z"] - 15.0
    return dict(cy=cy, bz=bz, cell=(g["fx"], cy, bz), focus=(MSO["fpd_x"] - 4.0, cy, bz), g=g)


def mastersizer() -> I.Instrument:
    inst = I.mastersizer()
    m = ms_geometry()
    cy, bz = m["cy"], m["bz"]
    cx = m["cell"][0]
    o = MSO
    opt = _piece(inst, "optics")                     # no joint: shown whenever the bench is see-through
    opt.add("He-Ne laser", _xcyl(2 * o["r_laser"], o["laser"][1] - o["laser"][0], x=o["laser"][0], y=cy, z=bz),
            "inst_dark")
    opt.add("laser head", _xcyl(14, 8, x=o["laser"][1], y=cy, z=bz), "inst_red")
    opt.add("blue LED", _ycyl(16, 14, x=-436.0, y=cy - 7, z=bz - 46).union(
        box(-444, cy - 10, bz - 62, -428, cy + 10, bz - 52)), "r8_blue")
    opt.add("dichroic", box(-439, cy - 12, bz - 12, -433, cy + 12, bz + 12).rotate((-436, cy, bz), (-436, cy + 1, bz),
                                                                                   45.0), "r8_lens")
    opt.add("beam expander", _xcyl(22, o["exp"][1] - o["exp"][0], x=o["exp"][0], y=cy, z=bz).cut(
        _xcyl(14, 40, x=o["exp"][0] - 5, y=cy, z=bz)), "steel")
    opt.add("focusing lens", _xcyl(2 * o["lens_r"], 6, x=o["lens_x"] - 3, y=cy, z=bz), "r8_lens")
    opt.add("lens mount", _xcyl(2 * o["lens_r"] + 10, 8, x=o["lens_x"] - 4, y=cy, z=bz).cut(
        _xcyl(2 * o["lens_r"] - 2, 12, x=o["lens_x"] - 6, y=cy, z=bz)), "inst_dark")
    for k, (dy, dz) in enumerate(((0, 34), (0, -34), (30, 0), (-30, 0))):
        opt.add(f"back-scatter detector {k}", box(o["bs_x"] - 2, cy + dy - 6, bz + dz - 6, o["bs_x"] + 2,
                                                  cy + dy + 6, bz + dz + 6), "r8_det")
    for k in range(6):
        a = math.radians(30 + 60 * k)
        rr = o["wide"] - 4
        dy, dz = rr * math.cos(a), rr * math.sin(a)
        opt.add(f"large-angle detector {k}", box(o["la_x"][0], cy + dy - 7, bz + dz - 7, o["la_x"][0] + 4,
                                                 cy + dy + 7, bz + dz + 7), "r8_det")
    fx = o["fpd_x"]
    opt.add("focal-plane detector", _xcyl(2 * o["fpd_r"], 6, x=fx, y=cy, z=bz), "inst_dark")
    radii = [3.0 * (o["fpd_r"] / 3.6) ** (i / (o["arcs"] - 1)) for i in range(o["arcs"])]
    arcs = None
    for r_ in radii:
        ring = _xcyl(2 * r_ + 1.6, 1.2, x=fx - 1.0, y=cy, z=bz).cut(_xcyl(2 * r_ - 1.6, 4, x=fx - 2, y=cy, z=bz))
        ring = ring.intersect(box(fx - 4, cy - 60, bz, fx + 4, cy + 60, bz + 60))          # the upper half: a fan
        arcs = ring if arcs is None else arcs.union(ring)
    opt.add("arcs", arcs, "r8_arc")
    lit = _piece(inst, "arcs_lit")
    lit.add("arcs lit", arcs.translate((-0.4, 0, 0)), "r8_arc_lit")
    # the beam: from the laser, expanded, then converging from the lens through the cell to the focal point
    beam = I.Model("mastersizer_beam", "Mastersizer: beam")
    beam.add("laser out", _xcyl(3, o["exp"][0] - o["laser"][1], x=o["laser"][1], y=cy, z=bz), "laser")
    beam.add("expanded", _xcyl(18, o["lens_x"] - o["exp"][1], x=o["exp"][1], y=cy, z=bz), "laser")
    beam.add("converging", _cone((o["lens_x"], cy, bz), m["focus"], 9.0, 0.6), "laser")
    inst.pieces["beam"] = beam
    sl = _piece(inst, "scat_large")
    sl.add("narrow cone", _cone((cx, cy, bz), (fx - 2, cy, bz), 1.0, o["narrow"]).cut(
        _cone((cx + 1, cy, bz), (fx - 1, cy, bz), 0.5, 3.0)), "r8_scat_large")
    ss = _piece(inst, "scat_small")
    ss.add("wide cone", _cone((cx + 8, cy, bz), (o["la_x"][0], cy, bz), 2.0, o["wide"]), "r8_scat_small")
    ss.add("back cone", _cone((cx - 8, cy, bz), (o["bs_x"] + 3, cy, bz), 2.0, 40.0), "r8_scat_small")
    # the particles in the cell, a slow fall for the tour (the chapter draws its own stream)
    gr = _piece(inst, "grains")
    rng = np.random.default_rng(7)
    for k in range(26):
        d = float(rng.uniform(2.2, 4.4))
        q = (cx + rng.uniform(-6, 6), cy + rng.uniform(-14, 14), bz + rng.uniform(-30, 30))
        gr.add(f"grain {k}", cq.Workplane("XY").sphere(d).translate(q), "powder")
    inst.meshes["readout"] = _dummy((0, 0, I.MS3000["H"]))
    # Round 9 (Sterling: "lots of overlapping transparency that obscures the laser"): no ghosted body. The bench's outer
    # covers (shell, end cap, deck, lids) are their own piece "shell" that fades OUT, leaving the optics bare on a base
    # plate; the cell cassette is cut in half along the beam so its pocket and windows show.
    body = inst.pieces["body"]
    cover_names = {"bench", "end cap", "deck", "plinth", "bay joints", "cassette plate", "AERO lettering", "green LED",
                   "cassette fitting", "bay LED", "MASTERSIZER lettering", "lid ring", "cell lid", "lid handle",
                   "swoosh", "status light"}
    shell = _piece(inst, "shell")
    keep = []
    for pt in body.parts:
        (shell.parts if pt.name in cover_names else keep).append(pt)
    body.parts = keep
    for pt in body.parts:
        if pt.name == "cell":
            pt.shape = pt.shape.cut(box(g["xl"], g["yf"], 0, g["xp"], cy, I.MS3000["H"]).val())
    body.add("bench floor", box(g["xl"] + 8, g["yf"] + 30, I.MS3000["feet"], g["xp"], g["yb"] - 8,
                                I.MS3000["feet"] + 10), "inst_dark")
    j = inst.joints
    j["shell"] = Joint("fade", v0=1.0)
    fall = tuple((0.0, 0.0, -6.0 * (i % 2)) for i in range(17))
    j.update({"arcs_lit": Joint("fade"), "scat_large": Joint("fade"), "scat_small": Joint("fade"),
              "grains": Joint("path", path=fall), "readout": Joint("fade")})
    inst.props = ("vial", "beam", "powder", "arcs_lit", "scat_large", "scat_small", "grains")
    inst.aside = ("readout",)
    hz = I.MS3000["hop_z"]
    g = m["g"]
    off = {"arcs_lit": (0.0, 0.0), "scat_large": (0.0, 0.0), "scat_small": (0.0, 0.0), "readout": (0.0, 0.0)}
    acts = list(inst.actions)
    acts[0] = (acts[0][0], acts[0][1], {**acts[0][2], **off})
    inst.actions = acts[:4] + [
        ("Air on; the bench drawn see-through. The background is measured with the cell empty: the laser's beam "
         "expanded, then focused by the lens so it converges through the cell onto the focal-plane detector.", 2.6,
         {"shell": (1.0, 0.0), "beam": (0.0, 1.0)}),
        ("The tray vibrates the powder into the venturi; the air disperses it and carries it through the cell. The "
         "obscuration, the share of the beam the particles take out, rises.", 2.6,
         {"tray": (0.0, 1.0), "powder": (1.0, 0.0), "grains": (0.0, 1.0)}),
        ("Large particles scatter light at small angles, onto the inner arcs; small ones scatter wide, to the large-"
         "angle and back-scatter detectors, where the blue LED's shorter wavelength resolves the finest.", 3.6,
         {"scat_large": (0.0, 1.0), "scat_small": (0.0, 1.0), "arcs_lit": (0.0, 1.0), "grains": (0.0, 1.0)}),
        ("The scattering pattern, fitted with Mie theory, gives the volume-weighted size distribution, 0.01 um to "
         "3.5 mm, in seconds; the extractor draws the powder away.", 3.4, {"readout": (0.0, 1.0)}),
        ("Done: the beam off, the bench closed.", 1.4,
         {"beam": (1.0, 0.0), "scat_large": (1.0, 0.0), "scat_small": (1.0, 0.0), "arcs_lit": (1.0, 0.0),
          "shell": (0.0, 1.0), "readout": (1.0, 0.0)}),
    ]
    inst.labels = [("Aero S dry disperser", (g["ax"] - I.MS3000["aero_l"] / 2, g["ay"], I.MS3000["aero_h"] - 80),
                    (0.12, 0.30)), ("cell cassette", (g["fx"], g["yf"], I.MS3000["deck"] - 60), (0.42, 0.10)),
                   ("optical bench", (g["xp"] - 150, g["yf"], 300), (0.62, 0.80))]
    inst.step_labels = {k: [("He-Ne laser 632.8 nm", (-490.0, cy, bz + 18), (0.10, 0.22)),
                            ("lens", (o["lens_x"], cy, bz + o["lens_r"]), (0.26, 0.14)),
                            ("cell", (cx, cy - 30, bz + 40), (0.42, 0.14)),
                            ("focal-plane detector", (fx, cy, bz + 40), (0.90, 0.22)),
                            ("large-angle detectors", (o["la_x"][0], cy, bz - 44), (0.64, 0.84)),
                            ("blue LED 470 nm", (-436.0, cy, bz - 60), (0.12, 0.84))] for k in (4, 5, 6)}
    inst.zoom = {0: ((g["hx"] + 60, g["hy"], I.MS3000["cover_z"] + 40), 1700.0), 4: ((-230.0, cy, bz), 760.0),
                 7: "out"}
    inst.cam = (0.38, -1.7, 0.75)
    return inst




# ===================================================================================================== XRF
# Bruker S2 PUMA Series 2, XY Autochanger: Bruker's brochure lists an "EasyLoad XY sample tray with 20 positions,
# removable; Grabber with automatic liquid sample detection", says "New samples can be loaded at any time" and "Trays
# with other sample batches can be exchanged during an analysis" (so the tray is outside the measuring chamber), and,
# for the Automation version, "Insertion of sample into sample chamber directly or via buffer positions". It measures
# from below (SampleCare protects the tube and detector "from particles of solid samples"). It does not describe how
# the grabber moves. Drawn here: a grabber on an XY gantry with a lift under the hood, which takes a cup from its seat
# to a port in the deck and sets it on a ring that lowers it into the chamber, film side down over the tube and the
# detector; a shutter closes the port. The gantry, the port, the ring and their travels are assumptions.
XRF_G = dict(park=(150.0, 170.0), up=100.0, grip=18.0, sink=44.0, port_dx=72.0)
XRF_HATCH = (-170.0, 170.0, -330.0, -90.0)   # the hatch's opening in the hood's top (x0, x1, y0, y1), over the port
XRF_SEAT = 15           # seats[i * 5 + j]: i = 3, j = 0, the front-right seat, the one nearest the arm at Shuttle 2's
                        # opening (alloy_powder.py); the grabber carries the cup from it to the port


def xrf_geometry() -> dict:
    import instruments_char as IC
    p, q = IC.XRF_SPECS, IC.XRF_LOOK
    D = p["D"]
    yf, yb, deck = -D / 2, D / 2, q["deck"]
    tx, ty = 40.0, (yf + 30 + yb - 60) / 2 + 30
    seats = [(tx - 105 + 70 * i, ty - 150 + 75 * j) for i in range(4) for j in range(5)]
    mx, my = tx - 105, ty - 150 - 75
    return dict(deck=deck, seats=seats, port=(mx, my), seat=seats[XRF_SEAT], yf=yf, yb=yb, W=p["W"], H=p["H"],
                st=q["side_t"], cup_d=p["cup_d"])


def xrf_keys() -> dict:
    """The grabber's keyframes {name: (gbeam y, gcar x, glift z)} (mm from its park) and the cup path's v at each."""
    g = xrf_geometry()
    G = XRF_G
    (sx, sy), (mx, my), dk = g["seat"], g["port"], g["deck"]
    px, py = G["park"]
    down_seat = (dk + 3 + G["grip"]) - (dk + G["up"])
    down_port = (dk + 2 + G["grip"]) - (dk + G["up"])
    keys = dict(park=(0.0, 0.0, 0.0), over=(sy - py, sx - px, 0.0), down=(sy - py, sx - px, down_seat),
                lift=(sy - py, sx - px, 0.0), port=(my - py, mx - px, 0.0), set=(my - py, mx - px, down_port),
                clear=(my - py, mx - px, 0.0))
    up = dk + 3 + G["grip"] + (0.0 - down_seat) - G["grip"]          # the cup's base, carried
    path = [(sx, sy, dk + 3), (sx, sy, up), (mx, my, up), (mx, my, dk + 2), (mx, my, dk + 2 - G["sink"])]
    seg = np.linalg.norm(np.diff(np.asarray(path), axis=0), axis=1)
    vs = np.r_[0, np.cumsum(seg)] / seg.sum()
    return dict(keys=keys, path=tuple(path), v=dict(seat=0.0, up=vs[1], over_port=vs[2], on_ring=vs[3], down=1.0))


def xrf() -> I.Instrument:
    import instruments_char as IC
    inst = IC.xrf()
    g = xrf_geometry()
    G = XRF_G
    dk, W, st = g["deck"], g["W"], g["st"]
    mx, my = g["port"]
    px, py = G["park"]
    kk = xrf_keys()
    K = kk["keys"]
    # the rails and the gantry: a beam across on two side rails (y), a carriage on it (x), a lift with the gripper (z)
    rails = _piece(inst, "rails")
    for sx_ in (-1, 1):
        rails.add(f"rail {sx_}", box(sx_ * (W / 2 - st - 22) - 6, -300, dk + 196, sx_ * (W / 2 - st - 22) + 6, 300,
                                     dk + 206), "aluminium")
    gb = _piece(inst, "gbeam")
    gb.add("gantry beam", box(-(W / 2 - st - 16), py - 12, dk + 206, W / 2 - st - 16, py + 12, dk + 228), "inst_grey")
    gc = _piece(inst, "gcar")
    gc.add("carriage", box(px - 26, py - 22, dk + 186, px + 26, py + 22, dk + 246), "inst_dark")
    gl = _piece(inst, "glift")
    tip = dk + G["up"]
    gl.add("lift rod", cyl(14, 130, x=px, y=py, z=tip + 36), "steel")
    gl.add("gripper head", box(px - 30, py - 11, tip + 22, px + 30, py + 11, tip + 38), "inst_dark")
    for sx_ in (-1, 1):
        x0 = px + sx_ * (g["cup_d"] / 2 + 1.5)
        gl.add(f"finger {sx_}", box(min(x0, x0 + sx_ * 6), py - 8, tip - 12, max(x0, x0 + sx_ * 6), py + 8, tip + 22),
               "inst_black")
    # the port: a shutter over a hole in the deck; under it, the chamber and the ring that lowers the cup into it
    port = _piece(inst, "port")
    port.add("port shutter", box(mx - 32, my - 32, dk + 1.5, mx + 32, my + 32, dk + 4.5).edges("|Z").fillet(4),
             "steel")
    ch = _piece(inst, "chamber")
    ch.add("sample chamber", tube(66, 54, 52, x=mx, y=my, z=dk - 66), "inst_grey")
    ring = _piece(inst, "ring")
    ring.add("lift ring", tube(46, 32, 3, x=mx, y=my, z=dk - 1).union(
        box(mx + 20, my - 3, dk - 60, mx + 26, my + 3, dk - 1)), "aluminium")
    # the tube and the detector under the measuring position, the cup's film at dk + 2 - sink
    spot = np.array([mx, my, dk + 2 - G["sink"]])
    inner = I.Model("xrf_inner", "S2 PUMA: tube and detector")
    tube_end, det_end = spot + (-40.0, 0.0, -80.0), spot + (40.0, 0.0, -80.0)
    for name, a, L, dia, mat in (("X-ray tube", tube_end, 120.0, 60.0, "inst_black"),
                                 ("detector", det_end, 140.0, 30.0, "steel")):
        dvec = (a - spot) / np.linalg.norm(a - spot)
        inner.add(name, cq.Workplane("XY").add(cq.Solid.makeCylinder(dia / 2, L, cq.Vector(*a), cq.Vector(*dvec))), mat)
    inst.pieces["inner"] = inner
    beam = I.Model("xrf_beam", "S2 PUMA: beam")
    beam.add("primary", _cone(tube_end, spot, 3.0, 12.0), "xray")
    beam.add("fluorescence", _cone(spot, det_end, 12.0, 8.0), "fluor")
    inst.pieces["beam"] = beam
    # the other cups in the tray, for company
    others = _piece(inst, "cups")
    for (sx_, sy_) in [q for i, q in enumerate(g["seats"]) if i % 3 == 1 and i != XRF_SEAT]:
        others.add(f"cup {sx_:.0f} {sy_:.0f}", tube(g["cup_d"], g["cup_d"] - 3, 25, x=sx_, y=sy_, z=dk + 4.5), "pp_white")
        others.add(f"powder {sx_:.0f} {sy_:.0f}", cyl(g["cup_d"] - 4, 10, x=sx_, y=sy_, z=dk + 4.2), "powder")
    # the robot's way in (round 8, alloy_powder.py): Bruker's Automation version takes samples "into the sample chamber
    # directly or via buffer positions" (S2 PUMA Series 2 brochure). Drawn here as a hatch in the hood's top, where the
    # window is, that slides back so a gripper can set a cup straight onto the chamber's ring under the port. The hood
    # itself can't open far enough at the VLM's opening for an arm to reach under it. The hatch is our assumption.
    q_ = IC.XRF_LOOK
    H_ = g["H"]
    hx0, hx1, hy0, hy1 = XRF_HATCH
    lid = inst.pieces["lid"]
    lid.parts = [pt for pt in lid.parts if "window" not in pt.name]
    for pt in lid.parts:                              # the opening, wider than the window it replaces
        if pt.name == "hood":
            pt.shape = pt.shape.cut(box(hx0, hy0, H_ - 30, hx1, hy1, H_ + 1).val())
    hatch = _piece(inst, "hatch")
    hatch.add("top hatch", box(hx0 - 6, hy0 - 6, H_ + 0.5, hx1 + 6, hy1 + 6, H_ + 3.5), "xrf_window")
    hatch.add("hatch handle", box(-40, hy0 - 4, H_ + 3.5, 40, hy0 + 6, H_ + 10), "inst_navy")
    j = inst.joints
    j["hatch"] = Joint("slide", vec=(0, hy1 - hy0 + 20.0, 0), parent="lid")
    j["sample"] = Joint("path", path=kk["path"])
    j["gbeam"] = Joint("slide", vec=(0, 1, 0))
    j["gcar"] = Joint("slide", vec=(1, 0, 0), parent="gbeam")
    j["glift"] = Joint("slide", vec=(0, 0, 1), parent="gcar")
    j["port"] = Joint("slide", vec=(G["port_dx"], 0, 0))
    j["ring"] = Joint("slide", vec=(0, 0, -G["sink"]))
    inst.props = ("sample", "beam")
    inst.aside = ("readout",)
    V = kk["v"]

    def mv(a, b):
        return {"gbeam": (K[a][0], K[b][0]), "gcar": (K[a][1], K[b][1]), "glift": (K[a][2], K[b][2])}
    inst.actions = [
        ("Bruker S2 PUMA Series 2 with the XY Autochanger, its hood drawn see-through: cups of powder in the "
         "removable 20-position tray, and the grabber that takes them to the measuring chamber under the deck.", 2.0,
         {"~lid": (0.0, 1.0), "sample": (0.0, 0.0), "beam": (0.0, 0.0), "readout": (0.0, 0.0), "port": (0.0, 0.0),
          "ring": (0.0, 0.0), **mv("park", "park")}),
        ("The grabber runs over the first cup and grips it (drawn as an XY gantry with a lift: Bruker doesn't "
         "publish the mechanism).", 2.0, mv("park", "over")),
        ("", 0.8, mv("over", "down")),
        ("It lifts the cup clear of the tray.", 0.9, {**mv("down", "lift"), "sample": (V["seat"], V["up"])}),
        ("And carries it to the chamber's port, which opens.", 1.6,
         {**mv("lift", "port"), "sample": (V["up"], V["over_port"]), "port": (0.0, 1.0)}),
        ("The cup goes down onto the chamber's ring, and the grabber lets go.", 1.0,
         {**mv("port", "set"), "sample": (V["over_port"], V["on_ring"])}),
        ("The ring lowers it into the chamber, film side down over the tube and the detector; the port shuts and the "
         "chamber fills with helium at reduced pressure, which keeps loose powder in place.", 2.4,
         {**mv("set", "clear"), "sample": (V["on_ring"], V["down"]), "ring": (0.0, 1.0), "~body": (0.0, 1.0)}),
        ("", 0.8, {"port": (1.0, 0.0)}),
        ("The beam, drawn see-through: up to 50 kV and 50 W from the tube; each element in the powder answers with "
         "its own X-ray lines, which the silicon drift detector counts. The tray stays free to load.", 3.0,
         {"beam": (0.0, 1.0), **mv("clear", "park")}),
        ("The spectrum: peaks at each element's lines give the composition, Na to Am, in minutes.", 4.6,
         {"readout": (0.0, 1.0)}),
    ]
    acts = []
    for cap, secs, t in inst.actions:                    # a blank caption keeps the one before
        acts.append((cap or acts[-1][0], secs, t))
    inst.actions = acts
    inst.labels = [("XY tray, 20 positions", (g["seats"][19][0], g["seats"][19][1], dk + 12), (0.86, 0.30)),
                   ("grabber", (px, py, dk + 230), (0.62, 0.14)),
                   ("measuring chamber port", (mx, my, dk + 4), (0.12, 0.62))]
    inst.zoom = {1: ((mx + 40, my + 60, dk + 70), 1500.0), 8: "out"}
    return inst


# ===================================================================================================== the prep station
# Our design, on tray D beside the MiniFlex (round 8, PR #318: "for powder XRD, you didn't show anything related to the
# sample prep for it, which is actually kind of an art"). It follows the literature Edison found (notes/edison_r8.md,
# out/edison/auto_pxrd_prep/): the powder as sieved, never ground (milling gas-atomized Al-Cu cold-welds spheres into
# flakes); sifted onto the holder through a mesh-capped vial, as A-Lab's UR5e does (Szymanski 2024); struck off flush
# with the holder's reference plane, with no pressing (Whitfield, Huq and Kaduk, International Tables H, 2019). On a
# pedestal: the zero-background holder at the front edge (its fin over the edge, so the gripper's fingers clear the
# pedestal), a 1.5 in stub carrier for the SEM (the same holder cup as the mounts, r8_char.SEM_CUP) and a film-bottomed
# XRF cup; behind the holder, a blade on a small linear axis, and a trough the excess falls into. Sizes are ours.
PREP = dict(w=380.0, d=220.0, h=100.0, zbh_x=-120.0, puck_x=15.0, cup_x=125.0, nest_y=50.0, blade_park=-62.0,
            blade_run=112.0, puck_d=38.1, puck_h=25.0, stub_d=12.7, cup_d=40.0)


def prep_frames() -> dict:
    """Where things sit on the station (its frame: the pedestal's bottom centre, y to the back): the holder's frame
    (the carrier's underside centre), the stub carrier's and the XRF cup's bases."""
    p = PREP
    y_zbh = -p["d"] / 2 + ZBH["l"] / 2 + 1.0              # the carrier's front edge 1 mm behind the pedestal's face
    return dict(zbh=(p["zbh_x"], y_zbh, p["h"] - 1.0), puck=(p["puck_x"], -p["d"] / 2 + p["nest_y"], p["h"] - 6.0),
                cup=(p["cup_x"], -p["d"] / 2 + p["nest_y"], p["h"] - 8.0), trough_x=p["zbh_x"] + 48.0)


def stub_puck_parts() -> dict:
    """The 1.5 in aluminium stub carrier (our design: it drops into the SEM's 1.5 in mount cup like a mount, so the
    spring plunger grounds it) with a 12.7 mm pin stub and a carbon tab in its middle. Frame: its base centre."""
    p = PREP
    puck = cyl(p["puck_d"], p["puck_h"]).cut(cyl(3.3, 8, z=p["puck_h"] - 7.9))
    stub = cyl(p["stub_d"], 2.5, z=p["puck_h"]).union(cyl(3.2, 8, z=p["puck_h"] - 7.5))
    tab = cyl(12.0, 0.3, z=p["puck_h"] + 2.5)
    return {"carrier": (puck, "aluminium"), "pin stub": (stub, "steel"), "carbon tab": (tab, "inst_black")}


def xrf_cup_parts() -> dict:
    """A 40 mm XRF cup, its film down (instruments_char.xrf's 'sample', without the powder). Frame: its base centre."""
    d = PREP["cup_d"]
    return {"cup": (tube(d, d - 3, 25, z=1.5), "pp_white"), "film": (cyl(d - 1, 0.4, z=0.6), "prolene"),
            "ring": (tube(d + 2, d - 1, 6, z=0.0), "pp_white")}


def pxrd_prep() -> I.Instrument:
    p = PREP
    f = prep_frames()
    inst = I.Instrument("pxrd_prep", "Powder prep station: XRD holder, SEM stub, XRF cup", "our design",
                        (p["w"], p["d"] + 14.0, p["h"] + 50.0),
                        "Our design (round 8): the sifting and striking-off of Whitfield, Huq and Kaduk (2019) and "
                        "A-Lab's mesh-capped vial (Szymanski 2024), as Edison summarized them (notes/edison_r8.md)")
    inst.name = "Powder prep station"            # setup_lab.item_label's name for an "our design" model
    body = _piece(inst, "body")
    zx, zy, zz = f["zbh"]
    ped = box(-p["w"] / 2, -p["d"] / 2, 0, p["w"] / 2, p["d"] / 2, p["h"]).edges("|Z").fillet(6)
    ped = ped.cut(box(zx - ZBH["w"] / 2 - 1, zy - ZBH["l"] / 2 - 1, zz, zx + ZBH["w"] / 2 + 1, zy + ZBH["l"] / 2 + 1,
                      p["h"] + 1))                                   # the holder's nest, 1 mm deep
    tx = f["trough_x"]
    ped = ped.cut(box(tx - 14, zy - 30, p["h"] - 16, tx + 14, zy + 30, p["h"] + 1))      # the trough
    for key, (x, y, z), dia in (("puck", f["puck"], p["puck_d"] + 0.8), ("cup", f["cup"], p["cup_d"] + 3.0)):
        ped = ped.cut(cyl(dia, p["h"] - z + 1, x=x, y=y, z=z))
    body.add("pedestal", ped, "aluminium")
    body.add("trough liner", box(tx - 13, zy - 29, p["h"] - 15.5, tx + 13, zy + 29, p["h"] - 15), "inst_dark")
    # the blade's axis: a rail block behind the holder, the carriage on it, an arm forward over the nest
    rx0, rx1 = zx + p["blade_park"] - 30, zx + p["blade_park"] + p["blade_run"] + 30
    body.add("blade rail", box(rx0, zy + 34, p["h"], rx1, zy + 52, p["h"] + 40).edges("|X").fillet(3), "inst_dark")
    body.add("blade motor", box(rx0 - 34, zy + 30, p["h"], rx0, zy + 56, p["h"] + 44), "inst_black")
    bl = _piece(inst, "blade")
    bx = zx + p["blade_park"]
    top = zz + ZBH["t"]                                           # the holder's reference plane
    bl.add("blade carriage", box(bx - 14, zy + 22, p["h"] + 18, bx + 14, zy + 36, p["h"] + 44), "aluminium")
    bl.add("blade arm", box(bx - 5, zy - 22, top + 14, bx + 5, zy + 30, top + 22), "aluminium")
    bl.add("blade", box(bx - 1.0, zy - 18, top + 0.2, bx + 1.0, zy + 18, top + 16), "steel")
    # what it holds, as stocked: the holder, the stub carrier, an empty XRF cup
    hz = _piece(inst, "zbh")
    for nm, (shape, mat) in zbh_parts().items():
        hz.add(nm, shape.translate((zx, zy, zz)), mat)
    pk = _piece(inst, "stub_puck")
    for nm, (shape, mat) in stub_puck_parts().items():
        pk.add(nm, shape.translate(f["puck"]), mat)
    cu = _piece(inst, "xrf_cup")
    for nm, (shape, mat) in xrf_cup_parts().items():
        cu.add(nm, shape.translate(f["cup"]), mat)
    inst.joints = {"blade": Joint("slide", vec=(p["blade_run"], 0, 0))}
    inst.props = ()
    inst.actions = [("Our prep station for the powder: a zero-background holder, a stub carrier for the SEM and an XRF "
                     "cup in their nests; a blade that strikes the powder off flush with the holder's face.", 2.0,
                     {"blade": (0.0, 0.0)}),
                    ("The blade's stroke, across the holder and over the trough.", 1.6, {"blade": (0.0, 1.0)}),
                    ("And back.", 1.2, {"blade": (1.0, 0.0)})]
    inst.labels = [("zero-background holder", (zx, zy, top + 20), (0.18, 0.30)),
                   ("blade", (bx, zy + 40, p["h"] + 50), (0.30, 0.16)),
                   ("SEM stub carrier", (f["puck"][0], f["puck"][1], p["h"] + 30), (0.62, 0.22)),
                   ("XRF cup", (f["cup"][0], f["cup"][1], p["h"] + 30), (0.84, 0.30))]
    inst.notes = ["Our design; every size an assumption."]
    return inst


# tray D: where the OpenFlexure array stood (round 8 dropped it), right of the MiniFlex, clear of the stream camera
# posts (services.TRAY_CAMS["D"]) and the UPS; setup_lab.merge_r8 puts it in the set-up movie and the tray plan
TRAY_PLACEMENT = {"pxrd_prep": dict(tray="D", x=620.0, y=-280.0, turn=0.0)}


# ===================================================================================================== registry
REGISTRY = {"xrd": xrd, "mastersizer": mastersizer, "xrf": xrf, "pxrd_prep": pxrd_prep}


def _overlay(key):
    def draw(img, scale, alpha):
        import r8_powder_data as D
        from PIL import Image
        pan = D.panel(key)
        W, H = img.size
        w = int(0.44 * W)
        h = int(w * pan.height / pan.width)
        p = pan.resize((w, h), Image.LANCZOS).convert("RGBA")
        p.putalpha(int(255 * min(1.0, alpha) * 0.96))
        img.paste(p, (W - w - int(0.012 * W), int(0.075 * H)), p)
    return draw


try:                    # the tour's readout panels: instruments_char's overlay hook draws OVERLAYS[key] (see there)
    import instruments_char as _IC
    _IC.OVERLAYS.update(xrd=_overlay("xrd"), mastersizer=_overlay("psd"), xrf=_overlay("xrf"))
except Exception:       # noqa: BLE001  (the overlays are a nicety; the models don't need them)
    pass
