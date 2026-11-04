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
    "fl_alu": (0.74, 0.74, 0.73, 1.0, 0.45),          # the Form 4's satin silver base (Formlabs' frames)
    "fl_lip": (0.86, 0.86, 0.85, 1.0, 0.35),          # the lighter lip the cover sits on
    "fl_tank": (0.84, 0.85, 0.86, 1.0, 0.30),         # the Form 4 resin tank's light grey frame
    "fl_blue": (0.16, 0.45, 0.85, 1.0, 0.30),         # the blue latch at the front of its deck
    "fl_screen": (0.09, 0.12, 0.17, 1.0, 0.75),       # its touchscreen: a black UI, lit green and white
    "fl_ui": (0.36, 0.78, 0.42, 1.0, 0.2),            # the UI's green drawing and rows
}

# register.py's view of a model (see its docstring and instruments.py): key -> (its parameter dict, a function of
# (params, pose) giving named points and lines); FREE[key], the parameters fitted to the frames in refs/<key>/;
# CHECKS[key](params), numbers that must stay >= 0 for the fitted model to make sense.
ANCHORS: dict = {}
FREE: dict = {}
CHECKS: dict = {}

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
# 3D Printers Tech Specs", formlabs.com/3d-printers/resin/tech-specs/). Registered to Formlabs' and a reseller's videos
# (refs/form4/, notes/refine_form4.md): a silver base, 170 mm to the top of its light lip, whose front right is a
# black bezel holding the touchscreen (about 150 x 95 mm), "formlabs" small at the lower left; above it one orange
# shell, the cover, over the whole footprint, with rounded vertical edges. Its top fits at 537 mm, not 554: the
# published height is taken to be to the resin cartridge's cap, a knob just proud of the top at the back. Inside: a
# black deck round the LCD with a blue latch at its front left, the light grey resin tank, and at the back the Z tower,
# two aluminium columns either side of the lead screw, as tall as the cover, the build platform's black carrier riding
# up the screw; the cartridge stands behind it. The cover hinges sit "at the rear of the printer under the back panel"
# and "slide into the slots on the Z-tower" (Formlabs, "Replacing the Form 4 cover hinges"): it pivots on the tower's
# top, the front rising and the open side towards you, and stops where its front top edge reaches the published
# 844 mm. Proportions not published (the base, the bezel, the screen, the cover's top, the hinge) are fitted to frames.
FORM4 = dict(W=398.0, D=367.0, H=554.0, foot=10.0, base_h=169.8, lip_h=18.1, base_r=14.0, cover_r=24.0, top_r=12.0,
             cover_t=4.0, cover_h=537.1, bez_x0=5.3, bez_z0=12.0, bez_z1=160.7, scr_x0=26.6, scr_x1=174.8, scr_z0=36.9,
             scr_z1=131.7, hinge_y=162.3, hinge_z=495.7, open_h=844.0, raise_=170.0, tank_y=-45.0)


def _f4_open_deg(p) -> float:
    """The cover's opening angle: its front top edge, the point farthest from the hinge, ends at the published open
    height (844 mm), or the cover stops upright over the hinge if it can't reach that."""
    a, b = -p["D"] / 2 - p["hinge_y"], p["cover_h"] - p["hinge_z"]
    r, alpha = math.hypot(a, b), math.atan2(-a, b)
    need = p["open_h"] - p["hinge_z"]
    return math.degrees(alpha if need >= r else alpha - math.acos(need / r))


def _f4_turn(p, pt, v=1.0) -> tuple:
    """A point of the cover, closed, carried by the cover's hinge opened to the fraction v."""
    th = math.radians(_f4_open_deg(p)) * v
    y, z = pt[1] - p["hinge_y"], pt[2] - p["hinge_z"]
    c, s = math.cos(th), math.sin(th)
    return (pt[0], p["hinge_y"] + y * c + z * s, p["hinge_z"] - y * s + z * c)


def form4_anchors(p, pose=None) -> dict:
    """Named points and lines of the Form 4 model for register.py; the cover's follow pose["cover"] (0 shut, 1 open)."""
    W, D, H = p["W"], p["D"], p["H"]
    yf, yb, zb, ft = -D / 2, D / 2, p["base_h"], p["foot"]
    zl = zb - p["lip_h"]                                           # the lip's underside, the base's front face's top
    a = {"base fl bottom": (-W / 2, yf, ft), "base bl bottom": (-W / 2, yb, ft), "base fr bottom": (W / 2, yf, ft),
         "lip fl": (-W / 2, yf, zb), "lip bl": (-W / 2, yb, zb), "lip fr": (W / 2, yf, zb),
         "lip fl under": (-W / 2, yf, zl),
         "base left edge": ("line", (-W / 2, yf, ft + 20), (-W / 2, yf, zl - 15)),
         "base back left edge": ("line", (-W / 2, yb, ft + 20), (-W / 2, yb, zl - 15)),
         "base bottom": ("line", (-W / 2 + 25, yf, ft), (p["bez_x0"] - 10, yf, ft)),
         "lip underside": ("line", (-W / 2 + 25, yf, zl), (p["bez_x0"] - 10, yf, zl)),
         "bezel tl": (p["bez_x0"], yf, p["bez_z1"]), "bezel bl": (p["bez_x0"], yf, p["bez_z0"]),
         "bezel left": ("line", (p["bez_x0"], yf, p["bez_z0"] + 15), (p["bez_x0"], yf, p["bez_z1"] - 15)),
         "screen tl": (p["scr_x0"], yf - 4, p["scr_z1"]), "screen tr": (p["scr_x1"], yf - 4, p["scr_z1"]),
         "screen bl": (p["scr_x0"], yf - 4, p["scr_z0"]), "screen br": (p["scr_x1"], yf - 4, p["scr_z0"])}
    v = float((pose or {}).get("cover", 0.0))
    H = p["cover_h"]                                               # the cover's top; the cartridge cap is at p["H"]
    cov = {"cover fl top": (-W / 2, yf, H), "cover fr top": (W / 2, yf, H), "cover bl top": (-W / 2, yb, H),
           "cover left edge": ("line", (-W / 2, yf, zb + 30), (-W / 2, yf, H - 30)),
           "cover right edge": ("line", (W / 2, yf, zb + 30), (W / 2, yf, H - 30)),
           "cover back left edge": ("line", (-W / 2, yb, zb + 30), (-W / 2, yb, H - 30)),
           "cover back right edge": ("line", (W / 2, yb, zb + 30), (W / 2, yb, H - 30)),
           "cover top front": ("line", (-W / 2 + 30, yf, H), (W / 2 - 30, yf, H)),
           "cover top back": ("line", (-W / 2 + 30, yb, H), (W / 2 - 30, yb, H)),
           "cover top left": ("line", (-W / 2, yf + 30, H), (-W / 2, yb - 30, H)),
           "cover bottom front": ("line", (-W / 2 + 30, yf, zb), (W / 2 - 30, yf, zb))}
    for k, s in cov.items():
        if isinstance(s, tuple) and s and s[0] == "line":
            a[k] = ("line", _f4_turn(p, s[1], v), _f4_turn(p, s[2], v))
        else:
            a[k] = _f4_turn(p, s, v)
    return a


def form4() -> Instrument:
    p = FORM4
    W, D, H = p["W"], p["D"], p["H"]
    yf, yb = -D / 2, D / 2
    zb, ft = p["base_h"], p["foot"]
    zl = zb - p["lip_h"]
    inst = Instrument("form4", "Resin 3D printer (MSLA)", "Formlabs Form 4", (W, D, H),
                      "Formlabs Form 4 tech specs (398 x 367 x 554 mm, 18.3 kg; 407 x 478 x 844 mm with the cover "
                      "open; 200 x 125 x 210 mm build volume); proportions registered to videos of it (refs/form4/)")
    body = _piece(inst, "body")
    body.add("plinth", rbox(W - 40, D - 40, ft, 10, z=0), "fl_dark")
    body.add("base", rbox(W, D, zl - ft, p["base_r"], z=ft), "fl_alu")
    body.add("lip", rbox(W, D, p["lip_h"], p["base_r"], z=zl), "fl_lip")
    # the touchscreen's black bezel takes the front right of the base, up into the lip, round the right-hand corner
    bez = box(p["bez_x0"], yf - 3, p["bez_z0"], W / 2, yf + 30, p["bez_z1"]).intersect(
        rbox(W + 0.6, D + 6, H, p["base_r"], z=0))
    body.add("screen bezel", bez, "inst_black")
    body.add("touchscreen", box(p["scr_x0"], yf - 3.6, p["scr_z0"], p["scr_x1"], yf - 3, p["scr_z1"]), "fl_screen")
    # its home screen, as in Formlabs' frames: the printer drawn in green, and the cartridge, platform and tank rows
    sw, sh = p["scr_x1"] - p["scr_x0"], p["scr_z1"] - p["scr_z0"]
    sx, sz = p["scr_x0"], p["scr_z0"]
    ui = box(sx + 0.16 * sw, yf - 3.9, sz + 0.16 * sh, sx + 0.44 * sw, yf - 3.6, sz + 0.72 * sh)
    for k in range(3):
        ui = ui.union(box(sx + 0.50 * sw, yf - 3.9, sz + (0.62 - 0.2 * k) * sh, sx + 0.80 * sw, yf - 3.6,
                          sz + (0.66 - 0.2 * k) * sh))
    body.add("screen UI", ui, "fl_ui")
    body.add("logo", box(-176, yf - 1, 40, -126, yf, 47), "fl_dark")
    # inside the cover: the black deck round the LCD, its blue latch, the Z tower and the cartridge at the back
    body.add("deck", box(-W / 2 + 10, yf + 10, zb, W / 2 - 10, yb - 10, zb + 4), "fl_dark")
    body.add("latch", box(-150, yf + 22, zb + 4, -70, yf + 34, zb + 14), "fl_blue")
    ty = p["tank_y"]
    tz = zb + 4
    tank = rbox(310, 220, 46, 12, y=ty, z=tz).cut(rbox(286, 196, 50, 8, y=ty, z=tz + 6))
    body.add("resin tank", tank, "fl_tank")
    body.add("resin", rbox(284, 194, 16, 8, y=ty, z=tz + 6), "fl_resin")
    tw0, tw1 = yb - 112, yb - 14                                  # the tower's depth
    Hc = p["cover_h"]                              # the cover's top; the cartridge's cap stands to the published H
    top = Hc - p["cover_t"] - 8
    body.add("Z column left", rbox(112, tw1 - tw0, top - zb, 10, x=-94, y=(tw0 + tw1) / 2, z=zb), "aluminium")
    body.add("Z column right", rbox(92, tw1 - tw0, top - zb, 10, x=74, y=(tw0 + tw1) / 2, z=zb), "aluminium")
    body.add("Z rail", box(-38, tw0 + 6, zb + 4, 28, tw0 + 50, top - 30), "inst_black")
    body.add("lead screw", cyl(12, top - 50 - zb, x=-5, y=tw0 + 14, z=zb + 20), "steel")
    body.add("cartridge", rbox(104, 40, 200, 10, x=0, y=yb - 34, z=Hc - 210), "inst_black")
    body.add("cartridge cap", rbox(56, 26, H - (Hc - 10), 8, x=0, y=yb - 34, z=Hc - 10), "fl_dark")   # above the top
    # the carrier on the Z rail (moves with the print) and the build platform on it. Its arm reaches over the tank's
    # back wall to the platform's spine, its block in front of the rail.
    holder = _piece(inst, "holder")
    z0 = tz + 6                                    # plate underside at the start of a print: just over the tank floor
    holder.add("carrier", box(-50, ty + 85, z0 + 48, 50, tw0 + 6, z0 + 88).union(
        box(-34, tw0 - 10, z0 + 48, 24, tw0 + 8, z0 + 118)), "fl_dark")
    load = _piece(inst, "load")
    load.add("build platform", _build_platform(ty, z0), "aluminium")
    # The parts grow downward from the plate as it rises, so they are drawn in 10 mm bands, each one appearing as the
    # plate lifts its lower face off the tank floor (the film, at tz + 6); a band is never drawn below the film.
    band, film = 10.0, tz + 6
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
    # the cover: one orange shell over the whole footprint, open below, rounded on its vertical and top edges; its back
    # is closed but for the slot the Z tower stands in, and its top has a notch for the cartridge's cap
    cover = _piece(inst, "cover")
    t = p["cover_t"]
    outer = rbox(W, D, Hc - zb, p["cover_r"], z=zb).edges(">Z").fillet(p["top_r"])
    inner = rbox(W - 2 * t, D - 2 * t, Hc - zb - t, p["cover_r"] - t, z=zb - 1)
    shell = outer.cut(inner).cut(box(-152, yb - t - 2, zb - 1, 122, yb + 1, top + 2)).cut(
        box(-32, yb - 50, Hc - 20, 32, yb - 18, Hc + 1))
    cover.add("cover", shell, "fl_orange")
    open_deg = _f4_open_deg(p)
    inst.joints = {
        "holder": Joint("slide", vec=(0, 0, p["raise_"])),
        # the platform slides off its mount towards you and on again ("Slide a clean build platform onto the build
        # platform mount. Close the latch to lock it.", the Form 4's own screen)
        "load": Joint("path", path=((0, -470, -30), (0, -175, 0), (0, 0, 0)), parent="holder", v0=1.0),
        **{lname: Joint("fade", parent="load") for lname in layers},
        "sample": Joint("fade", parent="load"),
        "cover": Joint("hinge", axis=(1, 0, 0), pivot=(0, p["hinge_y"], p["hinge_z"]), deg=-open_deg),
    }
    inst.actions = [
        ("Printing: the build platform rises out of the resin layer by layer, the parts growing upside down.", 3.0,
         {"holder": (0.0, 1.0), **grow, "~cover": (0.0, 0.6)}),
        ("Done. The cover swings up and back on hinges at the Z tower's top, to 844 mm: only at the VLM's opening, "
         "never in a slot.", 1.6, {"cover": (0.0, 1.0), "~cover": (0.6, 0.0), **whole}),
        ("The build platform slides off its mount towards you by the handle, parts and all, for the Form Wash.", 1.8,
         {"load": (1.0, 0.0)}),
        # the fresh platform is bare: the old parts are gone in the step's first quarter, while it is still outside
        ("A fresh platform slides onto the raised mount; it lowers to the tank and the cover shuts.", 1.6,
         {"load": (0.0, 1.0), "sample": (1.0, -3.0)}),
        ("", 1.4, {"holder": (1.0, 0.0), "cover": (1.0, 0.0)}),
    ]
    inst.labels = [("tinted cover", (-W / 2 + 40, yf, Hc - 60), (0.14, 0.24)),
                   ("touchscreen", ((p["scr_x0"] + p["scr_x1"]) / 2, yf - 4, p["scr_z1"] - 20), (0.84, 0.70)),
                   ("resin cartridge", (0, yb - 34, H - 4), (0.80, 0.18))]
    inst.notes = ["Fits a tray with 173.5 mm to spare under Kardex's 727.5 mm, but the cover opens to 844 mm: the arm "
                  "can open it at the opening (about 845 mm under the header), never while the tray is in a slot",
                  f"The cover pivots on the Z tower's top (Formlabs' hinge-replacement guide) through {open_deg:.0f} "
                  f"degrees, its front top edge to {_f4_turn(p, (0, yf, Hc))[2]:.0f} mm against the published 844; "
                  "the hinge's position is fitted to a frame of the open cover"]
    inst.anchors = form4_anchors(p)
    inst.cam = (1.0, -1.7, 0.9)
    inst.framing = (1.32, 0.69)                # the base whole, and room above for the open cover (844 mm)
    return inst


# register.py: the Form 4's anchors, the proportions fitted to the frames in refs/form4/ (its published W x D x H is
# the scale and stays fixed), and what keeps a fitted model buildable: the lip and the bezel on the base, the screen
# inside its bezel, the hinge under the cover's top and inside its footprint.
ANCHORS["form4"] = (FORM4, form4_anchors)
FREE["form4"] = ["base_h", "lip_h", "bez_x0", "bez_z1", "scr_x0", "scr_x1", "scr_z0", "scr_z1", "hinge_y", "hinge_z",
                 "cover_h"]
CHECKS["form4"] = lambda p: [p["base_h"] - 2 - p["bez_z1"], p["bez_z1"] - p["scr_z1"] - 8,
                             p["scr_z0"] - p["bez_z0"] - 8, p["scr_x0"] - p["bez_x0"] - 8,
                             p["W"] / 2 - p["scr_x1"] - 8, p["cover_h"] - p["hinge_z"] - 20,
                             p["D"] / 2 - p["hinge_y"] - 5, p["scr_x1"] - p["scr_x0"] - 60, p["H"] - p["cover_h"]]


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
