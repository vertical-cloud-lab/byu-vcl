"""Round 8, the char stream (#303, PR #318): the characterization instruments refitted for chapter 7
(``alloy_characterize.py``) and their tour clips. ``tour.load()`` lets this module's REGISTRY replace the older builders'
keys, so these are the models in every scene that loads them.

    xvfb-run --server-num=12 -a python3 tour.py sem vhx nanoindenter pip hardness

Every builder starts from the older one (``instruments.py``, ``instruments_char.py``, ``instruments_r7.py``, which are
not edited) and changes it here. What changed, after Sterling's review of 2026-11-05 (PR #318):

* **sem, the Hitachi TM4000PlusII.** The box to the right of the SEM is the EDS analyser, Oxford Instruments' AZtecOne
  (290 x 260 x 330 mm in Hitachi's EDS brochure): it is now lettered and labelled. The sample no longer stands loose on a
  pin: a holder for 1.5 in mounts stays in the stage's socket, an aluminium cup with a spring plunger (a ball-nose set
  screw, McMaster-Carr's kind) through its side. The conductive hot mount (``r8_specimens.hot_mount``) drops in and the
  plunger presses it against the cup's wall, so the path to ground is coupon -> carbon-filled phenolic -> the mount's
  side and base -> the cup -> the stage. The 70 deg pre-tilted EBSD holder (a proposal) is gone from the stage; the
  EBSD detector on the left is still drawn, as a proposal.
* **nanoindenter, the KLA iMicro.** Made readable: the cabinet and the hood are drawn see-through while it works; the
  XY stage really has two axes (a carriage in y that runs out to a load position, the stage in x on it), so the sample
  only ever moves with the stage; the steel mount (``r8_specimens.steel_mount``: the slice on steel) sits on the steel
  floor of a holder cup and a spring plunger clamps it; the stage carries it under the microscope objective, then under
  the indenter head, whose Berkovich tip comes down onto the surface for each indent.
* **vhx, the Keyence VHX-7000.** The head is on the sample's axis: the VH-ZST zoom lens points at the middle of the
  stage, and the free-angle head tilts about the focal point on the sample's surface (eucentric). The EA-300 LIBS
  head is left out of this model (it hung the lens 110 mm in front of the stage, off the sample's axis, which is what
  looked misaligned); the SEM's EDS does the chemistry in chapter 7. The stage has its motorized Z and theta rotation,
  so the head can tilt round a broken tensile bar from chapter 5 at every angle and the bar be turned over once: a
  3-D reconstruction of the whole piece, which is what the OpenFlexure array was going to be for.
* **pip, the Plastometrex PLX-Benchtop.** The sample is the steel mount, metal on metal from the slice down to the
  platen and its load cell; the indenter and the profilometer sit 14 mm higher for its 20 mm.
* **hardness, the Mitutoyo HM-220.** The sample is the conductive hot mount, in a holder on the XY table (a 5 mm plate
  with a V-block at the back: the mount slides in from the front, under the turret); the indents run across the coupon
  and stay on it.

Data panels for the tour clips: ``data_panels.py`` (drawn through ``instruments_char.OVERLAYS``).
"""
from __future__ import annotations

import math
import sys

import cadquery as cq
import numpy as np
import pyvista as pv

import instruments as I
from instruments import Instrument, Joint, _piece, _xcyl, _ycyl
import r8_specimens as SP

sys.path.insert(0, str(I.HERE / "lab_models"))
from common import Model, Part, box, cyl, rbox  # noqa: E402

MATERIALS = dict(SP.MATERIALS)
MATERIALS.update({
    "r8c_al": (0.80, 0.81, 0.83, 1.0, 0.70),        # machined aluminium holders
    "r8c_steel": (0.62, 0.63, 0.66, 1.0, 0.70),     # steel holders
    "r8c_label": (0.97, 0.97, 0.95, 1.0, 0.10),     # lettering
    "r8c_oxford": (0.06, 0.22, 0.45, 1.0, 0.35),    # Oxford Instruments' blue
    "r8c_glass": (0.80, 0.86, 0.90, 0.16, 0.90),    # a hood drawn see-through
    "r8c_ring": (0.95, 0.95, 0.85, 1.0, 0.10),      # a lit ring light
    "r8c_bar": (0.60, 0.61, 0.62, 1.0, 0.30),       # as-built LPBF AlSi10Mg (alloy_models.AS_BUILT)
    "r8c_frac": (0.48, 0.49, 0.50, 1.0, 0.05),      # its fracture surface
})


def _dummy(at=(0.0, 0.0, 0.0)):
    """An invisible speck: a piece that only carries a joint (a readout panel's opacity, or children)."""
    return [(pv.Sphere(radius=0.5, center=at, theta_resolution=4, phi_resolution=4), (1.0, 1.0, 1.0), 0.0)]


def _moved_part(q: Part, dx=0.0, dy=0.0, dz=0.0) -> Part:
    return Part(q.name, q.shape.moved(cq.Location(cq.Vector(dx, dy, dz))), q.material)


def _drop(model: Model, *names):
    model.parts = [q for q in model.parts if q.name not in names]


def _add_solids(piece: Model, solids: dict, dx=0.0, dy=0.0, dz=0.0, rz=0.0, prefix=""):
    """r8_specimens' {part: (Workplane, material)} into an instrument piece, turned rz about z, then moved."""
    for name, (w, mat) in solids.items():
        s = w.rotate((0, 0, 0), (0, 0, 1), rz) if rz else w
        piece.add(f"{prefix}{name}", s.translate((dx, dy, dz)), mat)


def plunger(x, y, z, toward, L=12.0, d=6.0) -> cq.Workplane:
    """A spring plunger (a ball-nose set screw): a threaded body of diameter d whose ball end is at (x, y, z), its
    body running L back along -toward (unit xy), a hex flange at the back. A robot needs no screwdriver: the mount
    pushes the ball back as it goes in, and the spring clamps it."""
    t = np.r_[np.asarray(toward, float), 0.0]
    t /= np.linalg.norm(t)
    ang = math.degrees(math.atan2(t[1], t[0]))
    body = cq.Workplane("YZ").circle(d / 2).extrude(L).translate((-L, 0, 0))
    ball = cq.Workplane("XY").sphere(d * 0.32)
    hexa = cq.Workplane("YZ").polygon(6, d * 1.5).extrude(3.0).translate((-L - 3.0, 0, 0))
    w = body.union(ball).union(hexa)
    return w.rotate((0, 0, 0), (0, 0, 1), ang).translate((x, y, z))


def cup(d_out, floor, depth, bore=SP.MOUNT_D + 0.6) -> cq.Workplane:
    """A holder cup for a 1.5 in mount, its base at z = 0: a floor `floor` thick, a bore `depth` deep."""
    w = cq.Workplane("XY").circle(d_out / 2).extrude(floor + depth)
    return w.cut(cq.Workplane("XY").circle(bore / 2).extrude(depth + 1).translate((0, 0, floor)))


# ===================================================================================================== SEM
SEM_CUP = dict(d=50.0, floor=5.0, depth=12.0, dy=-30.0, lift=6.0)   # our holder: an aluminium cup, 30 mm ahead of the stage's socket (estimate)
AZTEC = "Oxford Instruments AZtecOne EDS analyser, 290 x 260 x 330 mm"


def sem() -> Instrument:
    inst = I.sem()
    p, g = I.SEM, I._tm4000(I.SEM)
    W, ys = g["W"], g["ys"]
    fz = p["front_z0"]
    st = fz + 62.0                                 # the socket's top (instruments.sem)
    c = SEM_CUP
    dr = inst.pieces["drawer"]
    _drop(dr, "pre-tilted holder")
    # the cup stands on an adapter bar 30 mm ahead of the socket (its pin in the socket), as round 7's did: at the
    # socket itself, 40 mm in front of the SEM's face with the door out, every IK solution put the wrist into the
    # SEM's front (notes/alloy_characterize.md)
    yc = ys + SEM_CUP["dy"]
    za = st + SEM_CUP["lift"]                       # the cup's foot, on the adapter
    dr.add("holder adapter", box(-12, yc - 12, st, 12, ys + 12, za).union(cyl(12, 10, y=ys, z=st - 10)), "r8c_al")
    dr.add("mount holder cup", cup(c["d"], c["floor"], c["depth"]).translate((0, yc, za)), "r8c_al")
    zc = za + c["floor"] + c["depth"] / 2
    dr.add("spring plunger", plunger(-(SP.MOUNT_D / 2 + 0.3), yc, zc, (1, 0), L=10.0), "steel")
    body = inst.pieces["body"]
    # the AZtecOne: lettered on its front (rbox at x = W/2 + 190, y = -90, front face at y = -235)
    body.add("AZtecOne lettering", box(W / 2 + 115, -237.2, 262, W / 2 + 265, -236.0, 280), "r8c_label")
    body.add("Oxford Instruments band", box(W / 2 + 70, -237.0, 40, W / 2 + 310, -236.0, 60), "r8c_oxford")
    inst.pieces.pop("stub")
    stub = _piece(inst, "stub")
    _add_solids(stub, SP.hot_mount_solids("polished"))
    zf = za + c["floor"]
    inst.joints["stub"] = Joint("path", parent="drawer", path=((W / 2 + 70, yc - 230, zf + 200),
                                                                (0, yc, zf + 150), (0, yc, zf + 30), (0, yc, zf)))
    inst.meshes["readout"] = _dummy((0, ys, 300))
    inst.joints["readout"] = Joint("fade")
    inst.props = tuple(inst.props) + ("readout",)
    inst.actions = [
        ("EVAC/AIR vents the chamber; the door comes straight out with the X-Y stage on it. In the stage's socket: our "
         "holder for 1.5 in mounts, an aluminium cup with a spring plunger through its side.", 2.0,
         {"drawer": (0.0, 1.0), "stub": (0.0, 0.0), "readout": (0.0, 0.0)}),
        ("The conductive hot mount (carbon-filled phenolic) drops into the cup and the plunger presses it against the "
         "wall: coupon -> compound -> cup -> stage, the path to ground.", 2.4, {"stub": (0.0, 1.0)}),
        ("Door in, EVAC/AIR: about three minutes to vacuum. Then BSE images and EDS; the detector is built in, and "
         "the box on the right is its analyser, Oxford Instruments' AZtecOne.", 2.6, {"drawer": (1.0, 0.0)}),
        ("The polished section in backscattered electrons (illustrative: no image of this section exists yet).", 4.0,
         {"readout": (0.0, 1.0)}),
    ]
    inst.labels = [(AZTEC, (W / 2 + 190, -90, 330), (0.80, 0.16)),
                   ("EBSD (proposed)", (-W / 2 - 110, ys, 180), (0.12, 0.30)),
                   ("1.5 in mount holder: Al cup + spring plunger", (0, yc - 25, st + 15), (0.20, 0.80)),
                   ("EVAC/AIR", (p["btn_x"], g["yp"], p["btn_z"]), (0.62, 0.42))]
    inst.zoom = {1: ((0, g["yf"] - 150, st + 40), 700.0), 2: "out"}
    inst.notes = inst.notes + ["Round 8: a cup holder with a spring plunger grounds the conductive 1.5 in mount; the "
                               "AZtecOne EDS analyser is lettered and labelled."]
    return inst


# ===================================================================================================== nanoindenter
NANO_HOLD = dict(d=50.0, floor=4.0, depth=10.0)    # the steel cup on the stage (estimate)
NANO_LOAD = -130.0          # the carriage's run to the load position, mm (estimate; clear of the objective for a gripper)
NANO_TIP = 33.9             # the tip's approach from its parked height to the surface (drawn; the actuator's own
                            # range is tens of um, the coarse approach is the head's Z motor)


def nanoindenter() -> Instrument:
    p = I.NANO
    W, D, H = p["W"], p["D"], p["H"]
    inst = Instrument("nanoindenter", "Nanoindenter", "KLA iMicro", (W, D, H),
                      "KLA Instruments iMicro / iNano product photos and data sheet (InForce 50 actuator, Berkovich "
                      "tip, 50 mN; motorized XY stage; optical microscope); envelope in SPECS; holder ours")
    yf, yb = -D / 2, D / 2
    body = _piece(inst, "body")
    for sx in (-1, 1):
        for sy in (-1, 1):
            body.add(f"foot {sx}{sy}", box(sx * (W / 2 - 60) - 30, sy * (D / 2 - 50) - 25, 0, sx * (W / 2 - 60) + 30,
                                           sy * (D / 2 - 50) + 25, p["feet"]), "inst_black")
    hz = H - p["lid_t"]
    sz = p["feet"] + 70 + p["stage_z"] - 60        # the stage's top, as instruments.nanoindenter
    cab = _piece(inst, "cabinet")                  # its own piece, so it can be drawn see-through
    shell = box(-W / 2, yf, p["feet"], W / 2, yb, hz).edges("|Y").fillet(16)
    shell = shell.cut(box(-W / 2 + 40, yf - 1, p["feet"] + 70, W / 2 - 30, yb - 30, hz + 1))
    cab.add("cabinet", shell, "inst_white")
    cab.add("side panel", box(-W / 2 - 3, yf + 10, p["feet"] + 10, -W / 2, yb - 10, hz - 10), "inst_purple")
    cab.add("status light", box(-50, yf - 2, p["feet"] + 28, 50, yf, p["feet"] + 42), "inst_green")
    body.add("floor plate", box(-W / 2 + 40, yf + 2, p["feet"] + 66, W / 2 - 30, yb - 30, p["feet"] + 70), "inst_dark")
    body.add("back wall", box(-W / 2 + 40, yb - 34, p["feet"] + 70, W / 2 - 30, yb - 30, hz), "inst_dark")
    hx, ox = p["head_x"], p["scope_x"]
    body.add("frame", box(-120, yb - 160, p["feet"] + 70, 120, yb - 34, hz - 40), "inst_black")
    body.add("bridge", box(-120, -40, hz - 120, 120, yb - 160, hz - 40), "inst_black")
    body.add("indenter head", cyl(70, 150, x=hx, y=0, z=sz + 90), "inst_black")
    body.add("InForce label", box(hx - 12, -35.3, sz + 170, hx + 12, -33.0, sz + 185), "r8c_label")
    body.add("objective", cyl(30, 60, x=ox, y=0, z=sz + 40), "chrome")
    body.add("objective nose", cyl(36, 16, x=ox, y=0, z=sz + 100), "inst_dark")
    body.add("microscope tube", cyl(40, hz - 120 - (sz + 116), x=ox, y=0, z=sz + 116), "inst_dark")
    body.add("camera", rbox(60, 60, 50, 6, x=ox, y=0, z=hz - 120), "inst_dark")
    body.add("stage base", box(-150, -230, p["feet"] + 70, 150, 110, sz - 30), "inst_dark")
    for sx in (-1, 1):
        body.add(f"y rail {sx}", box(sx * 100 - 8, -230, sz - 34, sx * 100 + 8, 110, sz - 30), "steel")
    car = _piece(inst, "carriage")                 # y: out to the load position and back
    car.add("y carriage", box(-120, -100, sz - 30, 120, 100, sz - 20), "aluminium")
    car.add("x rails", box(-120, -60, sz - 20, 120, -50, sz - 17).union(box(-120, 50, sz - 20, 120, 60, sz - 17)),
            "steel")
    stage = _piece(inst, "stage")                  # x: from under the objective to under the indenter
    stage.add("x stage", box(-90, -80, sz - 17, 90, 80, sz - 6), "aluminium")
    hc = NANO_HOLD
    stage.add("holder cup", cup(hc["d"], hc["floor"], hc["depth"]).translate((ox, 0, sz - 6)), "r8c_steel")
    stage.add("spring plunger", plunger(ox, SP.MOUNT_D / 2 + 0.3, sz - 6 + hc["floor"] + hc["depth"] / 2, (0, -1),
                                        L=10.0), "steel")
    tip = _piece(inst, "tip")
    tip.add("tip shaft", cyl(10, 90, x=hx, y=0, z=sz + 60), "chrome")
    tip.add("Berkovich tip", cq.Workplane().add(cq.Solid.makeCone(0.2, 5.0, 8.0, cq.Vector(hx, 0, sz + 52),
                                                                  cq.Vector(0, 0, 1))), "inst_dark")
    smp = _piece(inst, "sample")
    _add_solids(smp, SP.steel_mount_solids("polished"))
    zb = sz - 6 + hc["floor"]                       # the mount's base on the cup's floor
    lid = _piece(inst, "lid")
    lid.add("lid", box(-W / 2, yf, hz, W / 2, yb, H).edges("|Y").fillet(14), "inst_white")
    lid.add("lid window", box(-W / 2 + 120, yf + 80, H, W / 2 - 80, yb - 120, H + 1), "inst_black")
    lid.add("hood front", box(-W / 2 + 40, yf, p["feet"] + 70, W / 2 - 30, yf + 12, hz).cut(
        box(-W / 2 + 90, yf - 1, p["feet"] + 120, W / 2 - 80, yf + 13, hz - 50)), "inst_white")
    lid.add("hood glass", box(-W / 2 + 90, yf + 4, p["feet"] + 120, W / 2 - 80, yf + 8, hz - 50), "window")
    inst.meshes["readout"] = _dummy((0, 0, 300))
    inst.joints = {
        "lid": Joint("hinge", axis=(1, 0, 0), pivot=(0, yb, hz), deg=-p["lid_deg"]),
        "carriage": Joint("slide", vec=(0, NANO_LOAD, 0)),
        "stage": Joint("slide", vec=(hx - ox, 0, 0), parent="carriage"),
        "sample": Joint("path", parent="stage", path=((ox, -260, zb + 260), (ox, -60, zb + 120), (ox, 0, zb + 30),
                                                      (ox, 0, zb))),
        "tip": Joint("slide", vec=(0, 0, -NANO_TIP)),
        "readout": Joint("fade"),
    }
    inst.props = ("sample", "readout")
    see = {"~cabinet": (0.0, 1.0), "~lid": (0.0, 1.0)}
    inst.actions = [
        ("The hood lifts on its gas struts, hinged at the back, and the XY stage's carriage runs forward to its load "
         "position.", 2.0, {"lid": (0.0, 1.0), "carriage": (0.0, 1.0), "sample": (0.0, 0.0), "readout": (0.0, 0.0)}),
        ("The steel mount goes into the holder cup: its steel base on the cup's steel floor, a spring plunger "
         "clamping it. Nothing soft under the slice.", 2.4, {"sample": (0.0, 1.0)}),
        ("Hood down (drawn see-through). The stage carries the slice back under the microscope objective, which "
         "finds the polished face and picks the grid.", 2.4, {"lid": (1.0, 0.0), "carriage": (1.0, 0.0), **see}),
        ("Then 100 mm across, under the indenter head (the InForce 50 actuator).", 1.6, {"stage": (0.0, 1.0)}),
        ("The Berkovich tip comes down onto the surface and is driven in to 500 nm, recording load and depth.", 1.8,
         {"tip": (0.0, 1.0)}),
        ("25 indents, a 5 x 5 grid 20 um apart: the stage steps between them. Hardness and modulus from each "
         "unloading curve (Oliver-Pharr).", 3.6, {"tip": (1.0, 0.0), "readout": (0.0, 1.0)}),
        ("Back under the objective to image the grid.", 2.0, {"stage": (1.0, 0.0)}),
    ]
    inst.labels = [("indenter head: InForce 50, Berkovich tip", (hx, 0, sz + 200), (0.12, 0.22)),
                   ("microscope objective and camera", (ox, 0, sz + 160), (0.84, 0.22)),
                   ("XY stage", (0, -80, sz - 12), (0.14, 0.78)),
                   ("steel mount, clamped in a steel cup", (ox, 0, zb + 20), (0.80, 0.76))]
    inst.cam = (-0.55, -1.8, 1.0)
    inst.framing = (1.2, 0.85)
    inst.zoom = {1: ((ox, NANO_LOAD, zb + 20), 650.0), 3: ((0, 0, sz + 60), 900.0), 6: "out"}
    return inst


# ===================================================================================================== PIP
# The PLX-Benchtop's working bay is about 130 mm tall with the indenter 7 mm over the sample, so a gripper can't
# reach the platen from above. A loading slide (ours): a 6 mm steel plate on a linear guide, which runs 310 mm out of
# the bay to the front, where the arm sets the steel mount on it from above, and back over the platen, where the plate
# sits on it: steel from the slice down to the load cell. The indenter and the profilometer sit 6 mm higher for it.
PIP_SLIDE = dict(t=6.0, w=70.0, l=90.0, travel=310.0, rail_w=40.0, ring_h=3.0)


def pip() -> Instrument:
    inst = I.pip()
    p, g = I.PIP, I._plx(I.PIP)
    W, D, stz, yc, zb = g["W"], g["D"], g["stz"], g["yc"], g["zb"]
    yf = -D / 2
    sl = PIP_SLIDE
    zs = stz + sl["t"]                             # the mount's base, on the slide plate
    s_top = zs + SP.FACE_Z                         # the steel mount's face
    xz0 = p["xh_z0"]
    # the indenter, rebuilt for the taller sample: the ball 7 mm over the face with the ram up
    inst.pieces.pop("head")
    head = _piece(inst, "head")
    hold_z = s_top + 7.0 + 12.0
    head.add("indenter cylinder", cyl(40, xz0 - hold_z + 10, y=yc, z=hold_z), "stainless")
    head.add("indenter collar", cyl(32, 4, y=yc, z=hold_z - 4), "inst_black")
    head.add("indenter tip", cq.Workplane("XY").circle(8).workplane(offset=8).circle(3).loft()
             .rotate((0, 0, 0), (1, 0, 0), 180).translate((0, yc, hold_z - 4)), "inst_dark")
    head.add("indenter", cq.Workplane("XY").sphere(1.0).translate((0, yc, hold_z - 12)), "inst_black")
    # the profilometer, its foot at the new face height (the same construction as instruments.pip)
    inst.pieces.pop("stylus")
    sty = _piece(inst, "stylus")
    ya = yc + 30.0
    tip_z = s_top + p["drop"]
    foot = np.array([p["park"], ya, tip_z + 14.0])
    rise = xz0 - 10 - foot[2]
    t = math.radians(p["arm_deg"])
    top = foot + np.array([-rise * math.tan(t), 0, rise])
    sty.add("profilometer carriage", box(top[0] - 18, ya - 7, xz0 - 22, top[0] + 18, ya + 7, xz0 - 10), "inst_dark")
    L = float(np.linalg.norm(foot - top))
    arm = (cq.Workplane("XZ").rect(18, L + 10).extrude(-6).edges("|Y").fillet(8.5)
           .faces("<Y").workplane().rect(9, L - 20).cutBlind(-2)
           .rotate((0, 0, 0), (0, 1, 0), -p["arm_deg"]).translate(tuple((foot + top) / 2 + np.array([0, -3, 0]))))
    sty.add("profilometer arm", arm, "aluminium")
    sty.add("profilometer shaft", _ycyl(6, 30, x=foot[0], y=ya - 30, z=foot[2]), "steel")
    sty.add("stylus pick-up", box(foot[0] - 5, ya - 36, foot[2] - 11, foot[0] + 5, ya - 26, foot[2] + 3), "inst_black")
    sty.add("stylus", cyl(1.6, 3.5, x=foot[0], y=yc, z=tip_z).union(
        cq.Workplane("XY").sphere(0.5).translate((foot[0], yc, tip_z))), "steel")
    # the slide: its rail on the plinth in front of the platen, out past the front; the plate and a locating ring
    body = inst.pieces["body"]
    y_rail0 = yc - sl["travel"] - sl["l"] / 2 - 10.0
    body.add("loading slide rail (ours)", box(-sl["rail_w"] / 2, y_rail0, zb, sl["rail_w"] / 2, yc - p["stage_d"] / 2 - 2,
                                              stz - 0.5), "r8c_steel")
    slide = _piece(inst, "slide")
    slide.add("slide plate", box(-sl["w"] / 2, yc - sl["l"] / 2, stz, sl["w"] / 2, yc + sl["l"] / 2, zs), "r8c_steel")
    slide.add("locating ring", cq.Workplane("XY").circle(SP.MOUNT_D / 2 + 4.0).circle(SP.MOUNT_D / 2 + 0.4)
              .extrude(sl["ring_h"]).translate((0, yc, zs)), "r8c_steel")
    inst.pieces.pop("sample")
    smp = _piece(inst, "sample")
    _add_solids(smp, SP.steel_mount_solids("polished"))
    inst.pieces.pop("indent")
    dent = _piece(inst, "indent")
    dent.add("indent", cyl(2.0, 0.3, z=SP.FACE_Z - 0.25), "inst_dark")
    inst.joints["slide"] = Joint("slide", vec=(0, -sl["travel"], 0))
    # the sample in the slide's frame: down from above onto the plate (the slide is out when it arrives)
    inst.joints["sample"] = Joint("path", parent="slide", path=((0, yc, zs + 240), (0, yc, zs + 60), (0, yc, zs)))
    inst.meshes["readout"] = _dummy((0, yc, 300))
    inst.joints["readout"] = Joint("fade")
    inst.props = tuple(inst.props) + ("readout",)
    acts = list(inst.actions)              # instruments.pip: [sample in, press, lift + profilometer in, trace, out, fit]
    inst.actions = [
        ("A loading slide (ours) runs its steel plate out of the working bay to the front: the bay is ~130 mm tall "
         "and the indenter waits 7 mm over the sample, too tight for a gripper.", 2.0,
         {"slide": (0.0, 1.0), "sample": (0.0, 0.0), "readout": (0.0, 0.0)}),
        ("The steel mount from chapter 6 (the wire-EDM slice on steel, polished flush) goes on the plate, in its "
         "locating ring.", 2.2, {"sample": (0.0, 1.0)}),
        ("The slide runs back in and the plate sits on the platen: metal on metal from the slice down to the load cell, "
         "nothing soft to compress.", 2.2, {"slide": (1.0, 0.0)}),
        *acts[1:-1],
        ("CORSICA fits a stress-strain curve to that profile by finite elements, in minutes.", 4.0,
         {**acts[-1][2], "sample": (1.0, 1.0), "readout": (0.0, 1.0)}),
        ("The slide runs out and the sample comes off.", 2.0, {"slide": (0.0, 1.0), "readout": (1.0, 0.0)}),
        ("", 1.4, {"sample": (1.0, 0.0)}),
    ]
    inst.actions = [(c or inst.actions[i - 1][0], sec, tg) for i, (c, sec, tg) in enumerate(inst.actions)]
    s_lab = list(inst.labels)
    s_lab.append(("loading slide (ours): steel plate on a linear guide", (0, yc - sl["travel"], zs), (0.16, 0.74)))
    inst.labels = s_lab
    inst.zoom = {3: ((30.0, yc, s_top + 30), 520.0), 8: "out"}
    inst.notes = list(inst.notes) + ["Round 8: a loading slide (ours) carries the steel mount out of the bay for the "
                                     "arm; the indenter and profilometer sit 6 mm higher for its plate."]
    return inst


# ===================================================================================================== micro-Vickers
HM_HOLD = dict(plate=5.0, w=64.0, d=64.0, vee=6.0)   # the mount holder on the HM-220's table (ours, estimate)
HM_SLIDE = 150.0          # its loading slide's run to the front (ours): the gripper 32 mm clear of the head


def hardness() -> Instrument:
    import instruments_r7 as R7
    inst = R7.hardness()
    p = R7.HM
    ax, ay = p["ax"]
    tx, ty = p["tur_c"]
    top = p["top"]                                # the face height under the objectives, as before
    table = 252.0                                 # the table's top (instruments_r7.hardness)
    stx = inst.pieces["stage_x"]
    h = HM_HOLD
    # the holder rides a loading slide (ours) on the XY table: out 130 mm to the front, clear of the head and the
    # turret, where the arm sets the mount on it from above; back under the objectives for the test. Its rail runs
    # forward of the table on the X carriage.
    stx.add("loading slide rail (ours)", box(ax - 20, ay - HM_SLIDE - h["d"] / 2 - 8, 244.0, ax + 20, ay - 65.0, table),
            "r8c_steel")
    sld = _piece(inst, "slide")
    sld.add("mount holder plate", box(ax - h["w"] / 2, ay - h["d"] / 2, table, ax + h["w"] / 2, ay + h["d"] / 2,
                                      table + h["plate"]), "r8c_steel")
    # the V-block at the back: two jaws at +-45 deg the mount sits against (its base is on the plate)
    r = SP.MOUNT_D / 2
    for s in (-1, 1):
        a = math.radians(90 + s * 40)
        cx, cy = ax + (r + 4) * math.cos(a), ay + (r + 4) * math.sin(a)
        jaw = box(-12, -4, 0, 12, 4, h["vee"]).rotate((0, 0, 0), (0, 0, 1), math.degrees(a) - 90)
        sld.add(f"V-block jaw {s}", jaw.translate((cx, cy, table + h["plate"])), "r8c_steel")
    inst.pieces.pop("sample")
    smp = _piece(inst, "sample")
    zb = table + h["plate"]
    # the face 3 mm under the objectives as before: the mount (20 mm) on the 5 mm plate puts it at 277 = top
    _add_solids(smp, SP.hot_mount_solids("polished"), dx=ax, dy=ay, dz=zb + (top - zb - SP.FACE_Z))
    # the indents: 5 across the coupon, 2.5 mm apart (drawn 1.2 mm across), on a rebuilt timeline so they stay on it
    n, step, x0 = p["n"], 2.5, -5.0
    tl = R7.Timeline(dict(sx=0.0, tur=0.0, ind=0.0, **{f"d{i}": 0.0 for i in range(n)}))
    for i in range(n):
        tl.go(0.5, sx=x0 + i * step)
        tl.go(0.8, tur=-90.0).go(0.5, ind=-2.9).go(0.5, **{f"d{i}": 1.0}).go(0.4, ind=0.0)
        if i == 0:
            tl.mark("pressed")
        tl.go(0.8, tur=0.0).go(0.7)
        if i == 0:
            tl.mark("read")
    for i in range(n):
        inst.pieces.pop(f"dent{i}", None)
        dn = _piece(inst, f"dent{i}")
        sq = box(-0.6, -0.6, 0, 0.6, 0.6, 0.3).rotate((0, 0, 0), (0, 0, 1), 45)
        dn.add(f"indent {i}", sq.translate((ax - (x0 + i * step), ay, top - 1.0)), "r7_dent")
    inst.joints.update({
        "stage_x": R7.Track(knots=tl.knots(lambda s: (s["sx"], 0.0, 0.0))),
        "slide": Joint("slide", vec=(0, -HM_SLIDE, 0), parent="stage_x"),
        "readout": Joint("fade"),           # instruments_r7's was a slide, which kept data_panels' panel on screen
        "sample": Joint("path", path=((0, 0, 220), (0, 0, 40), (0, 0, 0)), parent="slide"),
        "turret": R7.Turn(axis=(0, 0, 1), pivot=(tx, ty, 0), knots=R7._turn_knots(tl, lambda s: s["tur"])),
        "indenter": R7.Track(knots=tl.knots(lambda s: (0.0, 0.0, s["ind"])), parent="turret"),
        **{f"dent{i}": R7.Track(knots=tl.knots(lambda s, i=i: (0.0, 0.0, s[f"d{i}"])), parent="sample")
           for i in range(n)},
    })
    inst.props = tuple(dict.fromkeys(tuple(inst.props) + ("readout",)))
    tv = lambda a, b: {k: (a, b) for k in ("stage_x", "turret", "indenter", *[f"dent{i}" for i in range(n)])}  # noqa
    V = tl.v
    inst.actions = [
        ("A loading slide (ours) on the XY table runs the mount holder out to the front, clear of the head and the "
         "turret.", 1.8, {"slide": (0.0, 1.0), "sample": (0.0, 0.0), "readout": (0.0, 0.0), **tv(0.0, 0.0)}),
        ("The conductive hot mount goes on the holder from above, against its V-block (a 5 mm plate: the polished "
         "face where the objectives focus).", 2.2, {"sample": (0.0, 1.0)}),
        ("The slide runs back in, under the turret.", 1.8, {"slide": (1.0, 0.0)}),
        ("The motorized turret swings the Vickers indenter over it; the force motor presses: HV0.1, 0.98 N.", 3.2,
         {**tv(0.0, V("pressed"))}),
        ("The 50x objective comes back. The 3 MP camera images the indent; AVPAK measures both diagonals.", 2.6,
         {**tv(V("pressed"), V("read")), "readout": (0.0, 1.0)}),
        ("A row across the coupon, 0.25 mm apart (drawn 2.5 mm apart and 1.2 mm across), each made and read the "
         "same way, unattended.", 6.0, {**tv(V("read"), 1.0)}),
        ("315 x 671 x 595 mm and 43 kg: on a tray. HM-220: 0.05 gf to 2 kgf.", 2.4, {"readout": (1.0, 0.0)}),
        ("The slide runs out and the mount comes off.", 1.8, {"slide": (0.0, 1.0)}),
        ("", 1.4, {"sample": (1.0, 0.0)}),
    ]
    inst.actions = [(c or inst.actions[i - 1][0], sec, tg) for i, (c, sec, tg) in enumerate(inst.actions)]
    lab = [x for x in inst.labels if not x[0].startswith("motorized XY")]
    lab.append(("mount holder on a loading slide (ours)", (ax, ay - h["d"] / 2, table + 3), (0.14, 0.74)))
    inst.labels = lab
    inst.zoom = {1: ((ax, ay - HM_SLIDE / 2, 300.0), 560.0), 6: "out"}
    return inst


# ===================================================================================================== VHX
BAR_T = 6.0                 # the E8 subsize bar as printed (alloy_models.E8_SUB)
VHX_SLIDE = 110.0           # the loading slide's run to the front, clear of the ring light and the camera (ours)
VHX_CARRIER = dict(w=40.0, l=70.0, t=4.0, ped_w=8.0, ped_h=10.0)   # its carrier and the bar's pedestal (ours)


def bar_half_mesh() -> pv.PolyData:
    """The upper half of a broken tensile bar (alloy_models.bar_mesh('hi')), lying flat: long axis along y from the
    fracture at y = 0, z 0..6. Centred in x."""
    import alloy_models as AM
    return AM.bar_mesh("hi")


def vhx() -> Instrument:
    import instruments_char as IC
    inst = IC.vhx()
    p, q = IC.VHX_SPECS, IC.VHX_LOOK
    sx0, ys = 0.0, IC.VHX_STAGE_Y
    sz = q["stage_z"]
    zs = sz + q["plate_t"]
    inst.model = "Keyence VHX-7000 (VHX-S750E free-angle stand)"
    inst.title = "Digital microscope, free-angle, 3-D"
    body = inst.pieces["body"]
    _drop(body, "stage plate", "stage disk")
    # the stage top: motorized Z (50 mm) and theta (+-90 deg) on the XY stage
    tab = _piece(inst, "table")
    tab.add("stage Z plate", rbox(120, 120, 4, 4, x=sx0, y=ys, z=sz - 2), "char_vhx_grey")
    turn = _piece(inst, "turntable")
    turn.add("stage plate", rbox(p["stage"][0], p["stage"][1], q["plate_t"], 4, x=sx0, y=ys, z=sz), "char_vhx_grey")
    turn.add("stage disk", cyl(p["disk"], 1.0, x=sx0, y=ys, z=zs), "inst_grey")
    # the head: the VH-ZST zoom lens on the stage's axis, the camera on top, a ring light at its nose, the arm back to
    # the tilt guide on the column. Its focal point (the tilt's pivot) is on the sample's surface.
    inst.pieces.pop("head")
    for k in ("laser", "plasma"):
        inst.pieces.pop(k, None)
        inst.joints.pop(k, None)
    head = _piece(inst, "head")
    wd = 25.0                                    # working distance to the ring light's face (estimate, VH-ZST ~25 mm)
    zf = zs + 1.0 + SP.FACE_Z                     # the focal point: a 20 mm mount's face (the bar is raised to it)
    z0 = zf + wd
    head.add("ring light", cyl(66, 12, x=sx0, y=ys, z=z0).cut(cyl(40, 14, x=sx0, y=ys, z=z0 - 1)), "char_vhx_dark")
    head.add("ring light LEDs", cyl(60, 0.8, x=sx0, y=ys, z=z0 - 0.4).cut(cyl(44, 2, x=sx0, y=ys, z=z0 - 1)),
             "r8c_ring")
    head.add("VH-ZST zoom lens", cyl(54, 160, x=sx0, y=ys, z=z0 + 12), "char_vhx_silver")
    head.add("zoom lens grip", cyl(60, 60, x=sx0, y=ys, z=z0 + 80), "char_vhx_dark")
    head.add("camera", rbox(96, 110, 90, 12, x=sx0, y=ys + 10, z=z0 + 172).edges(">Z").fillet(8), "char_vhx_dark")
    head.add("camera badge", box(sx0 - 25, ys - 45.6, z0 + 225, sx0 + 25, ys - 45.0, z0 + 235), "inst_light")
    yg = IC.VHX_COL_Y - q["col_d"] / 2            # the column's front face (its tilt guide is 6 mm in front)
    head.add("head arm", box(sx0 - 40, ys + 40, z0 + 120, sx0 + 40, yg - 7, z0 + 230), "char_vhx_grey")
    pivot = (sx0, ys, zf)
    inst.meshes["focus"] = _dummy((sx0, ys, zf))
    inst.joints["focus"] = Joint("path", path=((0, 0, 0), (0, 0, -4), (0, 0, 4), (0, 0, 0)))
    inst.joints["head"] = Joint("hinge", axis=(0, 1, 0), pivot=pivot, deg=-45.0, parent="focus")   # v = 1: 45 deg left
    inst.joints["table"] = Joint("slide", vec=(0, 0, 50.0))
    inst.joints["turntable"] = Joint("spin", axis=(0, 0, 1), pivot=(sx0, ys, 0), deg=180.0, parent="table")
    # A loading slide (ours) on the stage: the head's ring light is 25 mm over the focal point, so a gripper can't
    # reach the stage from above. A carrier runs out VHX_SLIDE to the front on a rail fixed to the turntable (it turns
    # with theta), where the arm sets the bar on it and turns it over, and back to the stage's centre. On the carrier
    # a narrow pedestal (8 mm wide, narrower than the bar) holds the bar with its top face at the focal point and
    # leaves room for the gripper's pads either side.
    c = VHX_CARRIER
    zc0 = zs + 1.0                                 # the disk's top
    zb = zc0 + c["t"] + c["ped_h"]                 # the bar's underside
    turn.add("loading slide rail (ours)", box(sx0 - 10, ys - VHX_SLIDE - c["l"] / 2 - 8, zs - 6.0, sx0 + 10,
                                             ys - q["stage_d"] / 2 + 10, zc0), "r8c_steel")
    car = _piece(inst, "carrier")
    car.add("carrier plate", box(sx0 - c["w"] / 2, ys - c["l"] / 2, zc0, sx0 + c["w"] / 2, ys + c["l"] / 2,
                                 zc0 + c["t"]), "r8c_al")
    car.add("bar pedestal", box(sx0 - c["ped_w"] / 2, ys + 25.0 - 48.0, zc0 + c["t"], sx0 + c["ped_w"] / 2,
                                ys + 25.0 - 12.0, zb), "r8c_steel")
    inst.joints["carrier"] = Joint("slide", vec=(0, -VHX_SLIDE, 0), parent="turntable")
    # the sample: the broken bar's upper half on the pedestal, its fracture to the back (+y) and its grip end to the
    # front, where the arm takes it; its top face at the focal point. "bar" turns it over about its long axis.
    inst.pieces.pop("sample", None)
    bar = bar_half_mesh()                          # x +-5, y 0 (fracture) .. 50 (grip end), z 0..6
    bar_c = bar.rotate_z(180.0, inplace=False).translate((sx0, ys + 25.0, zb), inplace=False)
    inst.meshes["sample"] = _dummy((sx0, ys, zb))
    inst.meshes["bar"] = [(bar_c, MATERIALS["r8c_bar"][:3], 1.0)]
    zc = zb + BAR_T / 2
    inst.meshes["lift"] = _dummy((sx0, ys, zb))
    inst.joints["lift"] = Joint("slide", vec=(0, 0, 25.0), parent="carrier")       # off the pedestal for the flip
    inst.joints["sample"] = Joint("path", parent="lift", path=((0, 0, 220), (0, 0, 40), (0, 0, 0)))
    inst.joints["bar"] = Joint("hinge", axis=(0, 1, 0), pivot=(sx0, ys, zc), deg=180.0, parent="sample")
    inst.joints["readout"] = Joint("fade")
    inst.props = ("sample", "bar", "readout", "lift")
    inst.actions = [
        ("A loading slide (ours) runs its carrier out of the stage to the front: the ring light is 25 mm over the "
         "focal point, too close for a gripper.", 1.8,
         {"carrier": (0.0, 1.0), "sample": (0.0, 0.0), "head": (0.0, 0.0), "turntable": (0.0, 0.0),
          "bar": (0.0, 0.0), "lift": (0.0, 0.0), "readout": (0.0, 0.0)}),
        ("Half of a broken tensile bar from chapter 5 goes on the carrier's narrow pedestal, grip end to the front.",
         2.2, {"sample": (0.0, 1.0)}),
        ("Back to the stage's centre: the bar's top face at the focal point.", 1.8, {"carrier": (1.0, 0.0)}),
        ("The free-angle head tilts about the focal point (eucentric: the view stays on the bar) while the stage "
         "turns: a series of views from every side.", 4.0, {"head": (0.0, 1.0), "turntable": (0.0, 0.5)}),
        ("", 3.0, {"head": (1.0, -0.45), "turntable": (0.5, 0.0)}),
        ("Depth composition at each view: the motorized focus sweeps through the relief.", 2.0,
         {"head": (-0.45, 0.0), "focus": (0.0, 1.0)}),
        ("Turned over once (the arm does it in chapter 7), and the series again: the whole bar in 3-D, the fracture "
         "surface included.", 1.4, {"carrier": (0.0, 1.0)}),
        ("", 0.8, {"lift": (0.0, 1.0)}),
        ("", 1.6, {"bar": (0.0, 1.0)}),
        ("", 0.8, {"lift": (1.0, 0.0)}),
        ("", 1.4, {"carrier": (1.0, 0.0)}),
        ("The reconstruction: a height map of the fracture surface (illustrative).", 4.0, {"readout": (0.0, 1.0)}),
        ("The carrier runs out and the bar comes off.", 1.6, {"carrier": (0.0, 1.0), "readout": (1.0, 0.0)}),
        ("", 1.4, {"sample": (1.0, 0.0)}),
    ]
    acts = []
    for cap, secs, tg in inst.actions:
        acts.append((cap or acts[-1][0], secs, tg))
    inst.actions = acts
    lx = [x for x in inst.labels if x[0].startswith("VHX-7000 controller") or x[0].startswith("PiKVM")]
    inst.labels = [("VH-ZST zoom lens on the free-angle head", (sx0 + 27, ys, z0 + 120), (0.40, 0.12)),
                   ("motorized XY, Z and theta stage", (sx0 - q["stage_w"] / 2, ys - q["stage_d"] / 2, sz - 20),
                    (0.08, 0.72)), *lx]
    inst.labels.append(("loading slide (ours): carrier and pedestal", (sx0, ys - VHX_SLIDE, zb), (0.62, 0.80)))
    inst.zoom = {1: ((sx0, ys - VHX_SLIDE / 2, zf + 40), 760.0), 12: "out"}
    inst.notes = ["Round 8: the head is on the sample's axis and tilts about the focal point on its surface; the "
                  "EA-300 is not drawn."]
    bb = inst.bbox()
    inst.size = (round(bb[1] - bb[0]), round(bb[3] - bb[2]), round(bb[5] - bb[4]))
    return inst


# ===================================================================================================== registry
REGISTRY = {"sem": sem, "nanoindenter": nanoindenter, "vhx": vhx, "pip": pip, "hardness": hardness}


def _overlay(key):
    def draw(img, scale, alpha):
        import data_panels as D
        from PIL import Image
        pan = D.panel(key)
        W, H = img.size
        w = int(0.44 * W)
        h = int(w * pan.height / pan.width)
        pnl = pan.resize((w, h), Image.LANCZOS).convert("RGBA")
        pnl.putalpha(int(255 * min(1.0, alpha) * 0.96))
        img.paste(pnl, (W - w - int(0.012 * W), int(0.075 * H)), pnl)
    return draw


try:                    # the tour's readout panels, through instruments_char's overlay hook (see there)
    import instruments_char as _IC
    import instruments_lab as _IL
    _IL.PLOTS.pop("instruments/hardness", None)       # instruments_r7's indent sketch: data_panels' "hv" replaces it
    _IC.OVERLAYS.update(sem=_overlay("sem"), nanoindenter=_overlay("nano"), vhx=_overlay("vhx"), pip=_overlay("pip"),
                        hardness=_overlay("hv"))
except Exception:       # noqa: BLE001  (the overlays are a nicety; the models don't need them)
    pass
