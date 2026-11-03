"""Resin printing for the vertical cloud lab: the Formlabs Form 4, Form Wash (2nd Gen) and Form Cure (2nd Gen), each
its own model in the ``instruments.py`` framework, for a VLM tray (#303).

The three make one workflow, each machine's animation one step of it: the Form 4 prints, its cover lifts and the
build platform comes off by its handle; the platform goes into the Form Wash, which lowers the parts into IPA and lifts
them out to dry; the washed parts go onto the Form Cure's turntable under 405 nm light and heat.

Frame as in ``instruments.py``: x to the right, y away from you when you face the front (front face at y = -D/2), z up
from the tray, origin at the centre of the footprint, millimetres. Envelopes are Formlabs' published W x D x H; the
layout in between is read off Formlabs' product photos and is approximate. Formlabs publishes no CAD for these.
"""
from __future__ import annotations

import math  # noqa: F401

import cadquery as cq  # noqa: F401
import numpy as np  # noqa: F401

from instruments import Instrument, Joint, _piece, _wedge, _xcyl, _ycyl, box, cyl, rbox, tube  # noqa: F401

# name: (r, g, b, opacity, specular); only names instruments.MATERIALS and lab_models/common.MATERIALS don't have
MATERIALS = {
    "fl_orange": (0.98, 0.46, 0.08, 0.42, 0.9),       # Formlabs' orange tint: blocks the 405 nm light
    "fl_grey": (0.83, 0.84, 0.84, 1.0, 0.3),          # the housings' light grey
    "fl_dark": (0.20, 0.21, 0.22, 1.0, 0.3),          # lids, trim, the tank frame
    "fl_part": (0.56, 0.57, 0.59, 1.0, 0.35),         # printed parts, Grey Resin
    "fl_resin": (0.42, 0.43, 0.45, 0.80, 0.6),        # liquid resin in the tank
    "ipa": (0.78, 0.88, 0.96, 0.32, 0.8),             # isopropyl alcohol in the wash bucket
    "uv_glow": (0.56, 0.30, 1.00, 0.40, 0.0),         # 405 nm light filling the cure chamber
}

FEET = 10.0


def _feet(W, D, inset=30.0, d=22.0, h=FEET) -> cq.Workplane:
    f = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = cyl(d, h, x=sx * (W / 2 - inset), y=sy * (D / 2 - inset))
            f = c if f is None else f.union(c)
    return f


def _build_platform(y0: float, z0: float, handle=True) -> cq.Workplane:
    """A Form 4 build platform, plate face down at z0, centred on y0: the 200 x 125 mm plate, its spine to the carrier
    at the back, and the handle on top, grip at the front. The spine stands 58 mm tall so that, with the plate down on
    the Form 4's tank floor, the carrier it hangs from clears the tank's back wall."""
    plate = box(-100, y0 - 62.5, z0, 100, y0 + 62.5, z0 + 10)
    spine = box(-28, y0 + 40, z0 + 10, 28, y0 + 88, z0 + 58)
    plate = plate.union(spine)
    if handle:
        plate = plate.union(box(-14, y0 - 70, z0 + 10, 14, y0 + 45, z0 + 34)).union(
            box(-22, y0 - 82, z0 + 10, 22, y0 - 62, z0 + 44))
    return plate


def _parts(y0: float, z_top: float, n=3) -> list:
    """A few small printed parts hanging face down from a plate whose underside is at z_top: a lattice block, a gear
    blank and a bracket, the sort a lab prints for fixtures."""
    out = []
    out.append(("lattice block", box(-80, y0 - 30, z_top - 70, -30, y0 + 30, z_top).cut(
        box(-72, y0 - 31, z_top - 62, -38, y0 + 31, z_top - 8)).cut(box(-81, y0 - 22, z_top - 62, -29, y0 + 22,
                                                                         z_top - 8))))
    out.append(("gear blank", cyl(56, 45, x=10, y=y0, z=z_top - 45).cut(cyl(16, 46, x=10, y=y0, z=z_top - 45.5))))
    if n > 2:
        out.append(("bracket", box(50, y0 - 25, z_top - 90, 62, y0 + 25, z_top).union(
            box(50, y0 - 25, z_top - 90, 88, y0 + 25, z_top - 78))))
    return out


# ===================================================================================================== Form 4
# Formlabs Form 4 (MSLA: a 405 nm LCD under the resin tank): 398 W x 367 D x 554 H mm, 18.3 kg; minimum access
# dimensions 407 x 478 x 844 mm, i.e. with the cover open; build volume 200 x 125 x 210 mm (Formlabs, "Stereolithography
# 3D Printers Tech Specs", formlabs.com/3d-printers/resin/tech-specs/). The look is from Formlabs' photos: a light grey
# base with the touchscreen on its front, right of centre; the orange-tinted cover over the tank and the Z tower; the
# resin cartridge at the back. The cover is modelled hinged along its top rear edge, lifting the front, because that is
# what makes the published open envelope: 73 degrees takes it to 844 mm tall and about 460 mm deep, against Formlabs'
# 844 and 478. The base height (225 mm), the tank and the tower are read off photos.
FORM4 = dict(W=398.0, D=367.0, H=554.0, base_h=225.0, hinge_y=118.0, cover_t=4.0, raise_=170.0, cover_deg=-73.0)


def form4() -> Instrument:
    p = FORM4
    W, D, H = p["W"], p["D"], p["H"]
    yf, yb = -D / 2, D / 2
    zb = p["base_h"]
    inst = Instrument("form4", "Resin 3D printer (MSLA)", "Formlabs Form 4", (W, D, H),
                      "Formlabs Form 4 tech specs (398 x 367 x 554 mm, 18.3 kg; 407 x 478 x 844 mm with the cover "
                      "open; 200 x 125 x 210 mm build volume); look from Formlabs' photos")
    body = _piece(inst, "body")
    body.add("feet", _feet(W, D), "rubber")
    body.add("base", rbox(W, D, zb - FEET, 18, z=FEET), "fl_grey")
    body.add("deck", box(-W / 2 + 6, yf + 6, zb - 2, W / 2 - 6, p["hinge_y"], zb + 2), "fl_dark")
    body.add("screen bezel", box(55, yf - 1.5, 95, 185, yf, 185), "inst_black")
    body.add("touchscreen", box(62, yf - 2, 102, 178, yf - 1.5, 178), "screen_on")
    body.add("logo", box(-160, yf - 1, 170, -90, yf, 180), "fl_dark")
    # the rear housing behind the cover: the Z drive, and the cartridge bay on top
    body.add("rear housing", rbox(W, yb - p["hinge_y"], H - 8 - zb, 14, y=(yb + p["hinge_y"]) / 2, z=zb), "fl_grey")
    body.add("cartridge", rbox(118, 48, 150, 10, x=0, y=(yb + p["hinge_y"]) / 2 + 2, z=H - 158), "inst_black")
    body.add("cartridge cap", rbox(60, 30, 8, 6, x=0, y=(yb + p["hinge_y"]) / 2 + 2, z=H - 8), "fl_dark")
    # the resin tank and the Z tower inside the cover
    ty = -35.0
    tank = rbox(290, 200, 48, 10, y=ty, z=zb + 2).cut(rbox(270, 180, 50, 6, y=ty, z=zb + 6))
    body.add("resin tank", tank, "fl_dark")
    body.add("resin", rbox(268, 178, 20, 6, y=ty, z=zb + 6), "fl_resin")
    body.add("Z tower", box(-40, 78, zb + 2, 40, p["hinge_y"] - 2, H - 40), "aluminium")
    body.add("Z rail", box(-12, 70, zb + 40, 12, 78, H - 42), "steel")
    # the carrier on the tower (moves with the print) and the build platform on it. Its arm reaches over the tank's
    # back wall (top at zb + 50) to the platform's spine, and its block rides in front of the Z rail.
    holder = _piece(inst, "holder")
    z0 = zb + 8                                    # plate underside at the start of a print: just over the tank floor
    holder.add("carrier", box(-50, 40, zb + 56, 50, 70, zb + 96).union(box(-30, 60, zb + 56, 30, 70, zb + 116)),
               "fl_dark")
    load = _piece(inst, "load")
    load.add("build platform", _build_platform(ty, z0), "aluminium")
    # The parts grow downward from the plate as it rises, so they are drawn in 10 mm bands, each one appearing as the
    # plate lifts its lower face off the tank floor (the film, at zb + 6); a band is never drawn below the film.
    band, film = 10.0, zb + 6
    parts = _parts(ty, z0)
    depth = max(z0 - s.val().BoundingBox().zmin for _, s in parts)
    layers = [f"layer{k}" for k in range(1, int(math.ceil(depth / band - 1e-6)) + 1)]
    for k, lname in enumerate(layers):
        cut = box(-150, ty - 150, z0 - (k + 1) * band, 150, ty + 150, z0 - k * band)
        for name, shape in parts:
            s = shape.intersect(cut)
            if s.vals() and s.val().Volume() > 1.0:
                _piece(inst, lname).add(f"{name}, band {k + 1}", s, "fl_part")
    # each band's fade runs 0 -> 1 over the last 3 mm of the plate's rise that prints it, in the same step as the
    # rise; Rig/Scene clip opacities to 0..1, so values past either end just hold it hidden or shown
    grow = {lname: ((z0 - film - (k + 1) * band + 3.0) / 3.0, (z0 - film + p["raise_"] - (k + 1) * band + 3.0) / 3.0)
            for k, lname in enumerate(layers)}
    sample = _piece(inst, "sample")                # the same parts whole, swapped in for the bands once printed
    for name, shape in parts:
        sample.add(name, shape, "fl_part")
    whole = {"sample": (1.0, 1.0), **{lname: (0.0, 0.0) for lname in layers}}
    inst.props = ("load", "holder", "sample")
    cover = _piece(inst, "cover")
    t = p["cover_t"]
    shell = box(-W / 2 + 1, yf, zb + 2, W / 2 - 1, p["hinge_y"], H).cut(
        box(-W / 2 + 1 + t, yf + t, zb, W / 2 - 1 - t, p["hinge_y"] + 1, H - t))
    cover.add("cover", shell, "fl_orange")
    cover.add("cover lip", box(-60, yf - 2, zb + 4, 60, yf, zb + 14), "fl_dark")
    inst.joints = {
        "holder": Joint("slide", vec=(0, 0, p["raise_"])),
        "load": Joint("path", path=((0, -470, -30), (0, -175, 0), (0, 0, 0)), parent="holder", v0=1.0),
        **{lname: Joint("fade", parent="load") for lname in layers},
        "sample": Joint("fade", parent="load"),
        "cover": Joint("hinge", axis=(1, 0, 0), pivot=(0, p["hinge_y"], H), deg=p["cover_deg"]),
    }
    inst.actions = [
        ("Printing: the build platform rises out of the resin layer by layer, the parts growing upside down.", 3.0,
         {"holder": (0.0, 1.0), **grow, "~cover": (0.0, 0.6)}),
        ("Done. The cover lifts on its rear hinge, to 844 mm: only at the VLM's opening, never in a slot.", 1.6,
         {"cover": (0.0, 1.0), "~cover": (0.6, 0.0), **whole}),
        ("The build platform comes off its carrier by the handle, parts and all, for the Form Wash.", 1.8,
         {"load": (1.0, 0.0)}),
        # the fresh platform is bare: the old parts are gone in the step's first quarter, while it is still outside
        ("A fresh platform goes onto the raised carrier; it lowers to the tank and the cover shuts.", 1.6,
         {"load": (0.0, 1.0), "sample": (1.0, -3.0)}),
        ("", 1.4, {"holder": (1.0, 0.0), "cover": (1.0, 0.0)}),
    ]
    inst.labels = [("tinted cover", (-W / 2 + 40, yf, H - 60), (0.14, 0.24)),
                   ("touchscreen", (120, yf - 2, 140), (0.84, 0.70)),
                   ("resin cartridge", (0, (yb + p["hinge_y"]) / 2, H - 20), (0.80, 0.18))]
    inst.notes = ["Fits a tray with 173.5 mm to spare under Kardex's 727.5 mm, but the cover opens to 844 mm: the arm "
                  "can open it at the opening (about 845 mm under the header), never while the tray is in a slot",
                  "The cover's rear hinge is inferred from the published open envelope, not from a drawing"]
    inst.cam = (1.0, -1.7, 0.9)
    inst.framing = (1.1, 0.72)                  # room above for the open cover
    return inst


# ===================================================================================================== Form Wash
# Formlabs Form Wash (2nd Gen): 315 W x 293 D x 405 H mm, 714 mm tall with the lid open (Formlabs; MatterHackers'
# listing of the 2nd Gen). It takes the Form 4's build platform whole, parts face down, on an elevator that lowers them
# into the IPA bucket, agitates, and lifts them out of the solvent when the wash is done ("raises parts out of the
# solvent automatically", Formlabs' wash-and-cure page). Look from Formlabs' photos: a light grey body with a dark lid
# hinged at the back and a small display and button at the top of the front. The bucket, the impeller under it and the
# elevator are read off photos; the lid's hinge is placed so that it opens to the published 714 mm.
WASH = dict(W=315.0, D=293.0, H=405.0, lid_t=42.0, solvent_top=200.0, lift=150.0, lid_deg=-95.0)


def form_wash() -> Instrument:
    p = WASH
    W, D, H = p["W"], p["D"], p["H"]
    yf, yb = -D / 2, D / 2
    zl = H - p["lid_t"]                         # top of the body, underside of the lid
    inst = Instrument("form_wash", "Wash station for resin parts", "Formlabs Form Wash (2nd Gen)", (W, D, H),
                      "Formlabs Form Wash (2nd Gen): 315 x 293 x 405 mm, 714 mm tall with the lid open; look from "
                      "Formlabs' photos")
    body = _piece(inst, "body")
    body.add("feet", _feet(W, D, inset=28), "rubber")
    shell = rbox(W, D, zl - FEET, 22, z=FEET).cut(box(-128, yf + 18, 40, 128, yb - 34, zl + 1))
    body.add("housing", shell, "fl_grey")
    body.add("bucket", box(-128, yf + 18, 36, 128, yb - 34, 40), "fl_dark")
    body.add("display", box(-40, yf - 2, zl - 46, 40, yf, zl - 18), "screen_on")
    body.add("button", _ycyl(16, 3, x=70, y=yf - 3, z=zl - 32), "fl_dark")
    body.add("elevator rail", box(-14, yb - 42, 40, 14, yb - 34, zl - 4), "steel")    # proud of the bucket's back
    solvent = _piece(inst, "solvent")
    solvent.add("IPA", box(-126, yf + 20, 40, 126, yb - 36, p["solvent_top"]), "ipa")
    imp = _piece(inst, "impeller")
    for i in range(3):
        blade = box(-55, -6, 0, 55, 6, 8).rotate((0, 0, 0), (0, 0, 1), i * 60.0)
        imp.add(f"blade {i}", blade.translate((0, -10, 44)), "fl_dark")
    imp.add("hub", cyl(24, 12, y=-10, z=42), "fl_dark")
    holder = _piece(inst, "holder")
    py = -10.0                                     # the platform's centre over the bucket
    z_plate = zl - 62                              # plate underside with the elevator up: parts clear of the IPA
    # from the rail's face to the platform's spine (which ends at py + 88), so the platform hangs from it
    holder.add("carriage", box(-40, py + 80, z_plate + 18, 40, yb - 42, z_plate + 58), "fl_dark")
    load = _piece(inst, "load")
    load.add("build platform", _build_platform(py, z_plate), "aluminium")
    for name, shape in _parts(py, z_plate):
        load.add(name, shape, "fl_part")
    lid = _piece(inst, "lid")
    lid.add("lid", rbox(W, D, p["lid_t"], 22, z=zl), "fl_dark")
    lid.add("lid window", rbox(150, 110, 2, 10, y=-20, z=H - 1.5), "fl_orange")
    inst.joints = {
        "lid": Joint("hinge", axis=(1, 0, 0), pivot=(0, yb + 8, H + 8), deg=p["lid_deg"]),
        "holder": Joint("slide", vec=(0, 0, -p["lift"]), v0=0.0),
        "load": Joint("path", path=((0, -420, 330), (0, -40, 260), (0, 0, 0)), parent="holder"),
        "impeller": Joint("spin", axis=(0, 0, 1), pivot=(0, -10, 0), deg=1800.0),
    }
    inst.actions = [
        ("The lid lifts on its rear hinge, to 714 mm.", 1.4, {"lid": (0.0, 1.0), "load": (0.0, 0.0)}),
        ("The Form 4's build platform goes onto the elevator, parts face down.", 1.8, {"load": (0.0, 1.0)}),
        ("Lid shut.", 0.9, {"lid": (1.0, 0.0)}),
        ("The elevator lowers the parts into the IPA and the impeller under them stirs it.", 3.0,
         {"holder": (0.0, 1.0), "impeller": (0.0, 1.0), "~body": (0.0, 0.75), "~lid": (0.0, 0.75)}),
        ("Washed: the elevator lifts the parts out of the solvent to drip dry.", 1.8,
         {"holder": (1.0, 0.0), "~body": (0.75, 0.0), "~lid": (0.75, 0.0)}),
    ]
    inst.labels = [("lid", (0, 0, H), (0.20, 0.20)), ("display", (0, yf - 2, zl - 32), (0.84, 0.68))]
    inst.notes = ["Fits a tray closed (405 mm) and open (714 mm), under Kardex's 727.5 mm with 13.5 mm to spare",
                  "The bucket holds several litres of IPA: flammable vapour inside an enclosed VLM is a question for "
                  "Kardex and EHS, as is the waste solvent"]
    inst.cam = (1.0, -1.7, 1.0)
    inst.framing = (1.25, 0.82)                 # room above for the open lid and the platform coming in
    return inst


# ===================================================================================================== Form Cure
# Formlabs Form Cure (2nd Gen): 337 W x 356 D x 404 H mm, 12.1 kg (Formlabs; resellers' listings of the 2nd Gen),
# 405 nm LEDs and heat (Formlabs' wash-and-cure page: "precisely combines heat and 405 nm light"; up to 80 C on
# resellers' listings), a 235 mm turntable on rollers. Formlabs' own service guide says "Open the Form Cure door" and
# lifts the turntable "directly upwards off the rollers", so it is modelled with a front door; which side the door is
# hinged on is not published, and the left is assumed. Look from Formlabs' photos: the light grey body of the Wash,
# a dark door with an orange-tinted window, and the display on the top of the front.
CURE = dict(W=337.0, D=356.0, H=404.0, door_t=20.0, ch_z0=48.0, ch_z1=350.0, table_d=235.0)


def form_cure() -> Instrument:
    p = CURE
    W, D, H = p["W"], p["D"], p["H"]
    yf, yb = -D / 2, D / 2
    dt = p["door_t"]
    inst = Instrument("form_cure", "Post-cure chamber, 405 nm and heat", "Formlabs Form Cure (2nd Gen)", (W, D, H),
                      "Formlabs Form Cure (2nd Gen): 337 x 356 x 404 mm, 12.1 kg, 405 nm light and heat, 235 mm "
                      "turntable; look from Formlabs' photos and service guide")
    cy = yf + dt + (D - dt - 30) / 2               # the chamber's centre
    body = _piece(inst, "body")
    body.add("feet", _feet(W, D, inset=28), "rubber")
    shell = rbox(W, D - dt, H - FEET, 22, y=dt / 2, z=FEET).cut(
        box(-135, yf + dt - 1, p["ch_z0"], 135, yb - 30, p["ch_z1"]))
    body.add("housing", shell, "fl_grey")
    body.add("LED panels", box(-135, yb - 32, p["ch_z0"] + 20, 135, yb - 30, p["ch_z1"] - 20).union(
        box(-135, yf + dt, p["ch_z1"] - 2, 135, yb - 30, p["ch_z1"])), "inst_light")
    body.add("display", box(-45, yf + dt - 2, p["ch_z1"] + 12, 45, yf + dt, H - 14), "screen_on")
    body.add("roller", cyl(40, 10, y=cy, z=p["ch_z0"]), "fl_dark")
    table = _piece(inst, "turntable")
    table.add("turntable", cyl(p["table_d"], 6, y=cy, z=p["ch_z0"] + 10), "inst_light")
    table.add("turntable mark", box(80, cy - 4, p["ch_z0"] + 16, 110, cy + 4, p["ch_z0"] + 17), "fl_dark")
    sample = _piece(inst, "sample")
    zt = p["ch_z0"] + 16
    sample.add("lattice block", box(-75, cy - 30, zt, -25, cy + 30, zt + 70).cut(
        box(-67, cy - 31, zt + 8, -33, cy + 31, zt + 62)).cut(box(-76, cy - 22, zt + 8, -24, cy + 22, zt + 62)),
               "fl_part")
    sample.add("gear blank", cyl(56, 45, x=20, y=cy - 30, z=zt).cut(cyl(16, 46, x=20, y=cy - 30, z=zt - 0.5)),
               "fl_part")
    sample.add("bracket", box(30, cy + 20, zt, 80, cy + 60, zt + 12).union(box(30, cy + 20, zt, 42, cy + 60, zt + 90)),
               "fl_part")
    glow = _piece(inst, "glow")
    glow.add("405 nm light", box(-133, yf + dt + 2, p["ch_z0"] + 18, 133, yb - 33, p["ch_z1"] - 4), "uv_glow")
    door = _piece(inst, "door")                    # up to just over the chamber, so the display shows above it
    door.add("door", rbox(W - 4, dt, p["ch_z1"] + 6 - FEET - 4, 8, y=yf + dt / 2, z=FEET + 4).cut(
        box(-115, yf - 1, 80, 115, yf + dt + 1, 320)), "fl_dark")
    door.add("door window", box(-116, yf + 6, 79, 116, yf + 10, 321), "fl_orange")
    door.add("door handle", box(W / 2 - 40, yf - 4, 150, W / 2 - 22, yf, 260), "fl_dark")
    inst.joints = {
        "door": Joint("hinge", axis=(0, 0, 1), pivot=(-W / 2 + 4, yf, 0), deg=-105.0),
        "turntable": Joint("spin", axis=(0, 0, 1), pivot=(0, cy, 0), deg=720.0),
        # the parts wait over the top of the door, out of its swing, and come in once it is open
        "sample": Joint("path", path=((0, -460, 300), (0, -180, 40), (0, 0, 0)), parent="turntable"),
        "glow": Joint("fade"),
    }
    inst.actions = [
        ("The door swings open on its left-hand hinge.", 1.4, {"door": (0.0, 1.0), "sample": (0.0, 0.0)}),
        ("The washed, dried parts go onto the 235 mm turntable.", 1.8, {"sample": (0.0, 1.0)}),
        ("Door shut. The turntable turns under 405 nm light while the chamber heats, up to 80 C.", 3.2,
         {"door": (1.0, 0.0), "turntable": (0.0, 1.0), "glow": (0.0, 1.0), "~body": (0.0, 0.7),
          "~door": (0.0, 0.7)}),
        ("", 0.8, {"glow": (1.0, 0.0), "~body": (0.7, 0.0), "~door": (0.7, 0.0)}),
    ]
    inst.labels = [("door, tinted window", (W / 2 - 60, yf, 300), (0.82, 0.24)),
                   ("display", (0, yf + dt - 2, H - 30), (0.16, 0.22))]
    inst.notes = ["Fits a tray with 323.5 mm to spare; the door swings out in front, so it opens at the opening",
                  "The door's hinge side is assumed; Formlabs' service guide confirms a door, not a lid"]
    inst.cam = (1.0, -1.7, 0.9)
    inst.framing = (1.0, 0.45)                  # the whole cabinet in frame
    return inst


REGISTRY = {"form4": form4, "form_wash": form_wash, "form_cure": form_cure}
