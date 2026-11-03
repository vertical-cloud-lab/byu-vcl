"""Metal additive manufacturing for the vertical cloud lab: two compact LPBF machines and the most compact DED (#303).

None of these goes through the Kardex Shuttle's opening, which takes 727.5 mm of product height (Kardex's order sheet,
``vlm.py``): the Sharebot MetalONE is 1000 mm tall, the One Click Metal MPRINT 1900 mm and the Meltio M450 1400 mm.
So all three are ``floor=True``: they stand in the line beside the VLM, as the Aconity MIDI does. The shortest powder
bed machine found, SnowX's SnowPod (360 x 360 x 660 mm, 40 kg), would fit, but it is a crowdfunded kit not yet
shipping (see ``NOTES``).

Every model is an ``instruments.Instrument``, in the same frame (x right, y away from you, z up from the floor, origin
at the centre of the footprint, mm). The envelopes are the makers' published figures; the layouts are read off the
makers' product photos and are approximate. None of the makers publishes CAD.

The two LPBF machines share one process chamber (``_lpbf``): a build plate on a platform in a square build well, a
dosing hopper and a recoater blade, a scanner on the ceiling, and a laser spot that rasters each layer. Layers are drawn
3 mm thick (100x the real 20-60 um) so the platform's drop can be seen at all.
"""
from __future__ import annotations

import math

import cadquery as cq
import numpy as np

from instruments import Instrument, Joint, _piece, _wedge, _xcyl, _ycyl, box, cyl, rbox, tube  # noqa: F401

MATERIALS = {
    "sharebot_orange": (0.93, 0.42, 0.10, 1.0, 0.35),
    "ocm_teal": (0.05, 0.55, 0.60, 1.0, 0.35),
    "meltio_black": (0.13, 0.13, 0.14, 1.0, 0.35),
    "laser_window": (0.25, 0.55, 0.30, 0.38, 0.9),     # laser-safety glazing, green tint
    "melt": (1.00, 0.62, 0.12, 1.0, 0.1),              # a melt pool, glowing
}

NOTES = {
    "under_727": "Shortest LPBF found: SnowX SnowPod, 360 x 360 x 660 mm, 40 kg, 80 x 80 x 100 mm build, 200 W fibre "
                 "laser (3DWithUs hands-on review; 3Dnatives 2026-10-22), a Kickstarter kit planned for Q4 2026, 316L "
                 "only at launch. Next shortest: Mastrex MX100, 560 x 560 x 800 mm, about 125 kg (tech-labs listing); "
                 "Lasefinity Fusion X, 600 x 650 x 860 mm (TCT Magazine); Kings 3D DiMetal-100, 690 x 720 x 1000 mm, "
                 "140 kg (All3DP). No DED found under 1 m: the Meltio M450 is the most compact at 1400 mm.",
}


# ===================================================================================================== shared LPBF
def _lpbf(inst: Instrument, cx: float, cy: float, P: float, well: float, ceiling: float, hopper_x: float,
          n_layers: int = 3, t: float = 3.0, plate_t: float = 12.0, come_x: float = 0.0) -> dict:
    """The process chamber of a powder-bed machine, around a square build well of side `well` centred on (cx, cy),
    with the powder surface at z = P. Adds the pieces "deck" (static), "platform", "load" (the build plate, riding the
    platform), "layer1".."layerN" (riding the plate), "powder", "recoater", "scan" and "beam" (riding the scan), and
    returns the joints and some heights. Left to right: the dosing hopper (0.7 x `well` wide at the top), the recoater
    parked just clear of it and of the well, the well, and the overflow slot, over which the recoater stops. The build
    plate waits `come_x` to the right of the well, clear of the chamber door's swing."""
    deck = _piece(inst, "deck")
    half = well / 2
    deck_plate = box(hopper_x - 60, cy - half - 70, P - 15, cx + half + 80, cy + half + 70, P)
    deck_plate = deck_plate.cut(box(cx - half, cy - half, P - 16, cx + half, cy + half, P + 1))
    deck_plate = deck_plate.cut(box(cx + half + 15, cy - half, P - 16, cx + half + 40, cy + half, P + 1))  # overflow
    deck.add("deck", deck_plate, "stainless")
    deck.add("overflow", box(cx + half + 15, cy - half, P - 60, cx + half + 40, cy + half, P - 15), "inst_black")
    deck.add("build well", box(cx - half - 12, cy - half - 12, P - well - 40, cx + half + 12, cy + half + 12, P - 15)
             .cut(box(cx - half, cy - half, P - well - 41, cx + half, cy + half, P - 14)), "steel")
    hop = (cq.Workplane("XY").rect(0.36 * well, 0.8 * well).workplane(offset=60).rect(0.7 * well, well + 10).loft()
           .translate((hopper_x, cy, P)))
    deck.add("dosing hopper", hop, "stainless")
    deck.add("scanner", box(cx - 70, cy - 60, ceiling - 70, cx + 70, cy + 60, ceiling), "inst_dark")
    deck.add("scanner window", cyl(56, 4, x=cx, y=cy, z=ceiling - 74), "window")
    deck.add("gas inlet", box(hopper_x - 55, cy + half + 48, P + 20, cx + half + 70, cy + half + 68, P + 45), "inst_grey")
    platform = _piece(inst, "platform")
    platform.add("piston", box(cx - half + 1, cy - half + 1, P - t - plate_t - 30, cx + half - 1, cy + half - 1,
                               P - t - plate_t), "steel")
    load = _piece(inst, "load")
    load.add("build plate", box(cx - half + 2, cy - half + 2, P - t - plate_t, cx + half - 2, cy + half - 2, P - t),
             "steel")
    for k in range(1, n_layers + 1):                 # layer k is fused when the platform has dropped k-1 layers
        _piece(inst, f"layer{k}").add(f"layer {k}", _cross_section(cx, cy, well, P + (k - 2) * t + 0.8, t), "sample")
    powder = _piece(inst, "powder")
    powder.add("powder bed", box(cx - half + 0.5, cy - half + 0.5, P - 0.7, cx + half - 0.5, cy + half - 0.5, P - 0.1),
               "powder")
    rec = _piece(inst, "recoater")
    rx0 = hopper_x + 0.35 * well + 3               # parked against the hopper, left of the well and the plate
    assert rx0 + 18 < cx - half + 2, f"{inst.key}: the parked recoater is over the build well"
    rec.add("recoater arm", box(rx0, cy - half - 45, P + 4, rx0 + 18, cy + half + 45, P + 40), "inst_grey")
    rec.add("recoater blade", box(rx0 + 6, cy - half - 8, P + 0.2, rx0 + 12, cy + half + 8, P + 6), "rubber")
    sweep = (cx + half + 24) - rx0                 # the blade stops over the overflow slot
    scan = _piece(inst, "scan")
    scan.add("galvo target", box(cx - 1, cy - 1, P - 40, cx + 1, cy + 1, P - 38), "inst_dark")
    beam = _piece(inst, "beam")
    beam.add("beam", cyl(3.0, ceiling - 74 - P, x=cx, y=cy, z=P), "laser")
    beam.add("melt pool", cyl(10.0, 1.6, x=cx, y=cy, z=P - 0.2), "melt")
    r = 0.36 * well
    raster = []
    for i in range(7):
        y = -r + i * 2 * r / 6
        raster += [(-r, y, 0), (r, y, 0)] if i % 2 == 0 else [(r, y, 0), (-r, y, 0)]
    joints = {
        "platform": Joint("slide", vec=(0, 0, -n_layers * t)),
        "load": Joint("path", path=((come_x, -480, 170), (0, -160, 60), (0, 0, 30), (0, 0, 0)), parent="platform"),
        "recoater": Joint("slide", vec=(sweep, 0, 0)),
        "powder": Joint("fade"),
        "scan": Joint("path", path=tuple(raster)),
        "beam": Joint("fade", parent="scan"),
    }
    for k in range(1, n_layers + 1):
        joints[f"layer{k}"] = Joint("fade", parent="load")
    return joints


def _cross_section(cx, cy, well, z0, h) -> cq.Workplane:
    """What the layers fuse: two flat tensile coupons and a round boss, the same cross-section every layer."""
    s = box(cx - 0.36 * well, cy - 0.26 * well, z0, cx + 0.36 * well, cy - 0.13 * well, z0 + h)
    s = s.union(box(cx - 0.36 * well, cy + 0.04 * well, z0, cx + 0.36 * well, cy + 0.17 * well, z0 + h))
    return s.union(cyl(0.2 * well, h, x=cx, y=cy + 0.32 * well, z=z0))


def _layer_actions(n_layers: int, first: str, laser: str) -> list:
    """Recoat, scan, drop, for each layer: [(caption, seconds, targets)]."""
    acts = []
    for k in range(1, n_layers + 1):
        acts.append((first if k == 1 else "The platform drops a layer; the recoater spreads fresh powder over it.",
                     1.3, {"recoater": (0.0, 1.0) if k % 2 else (1.0, 0.0), "powder": (0.0 if k == 1 else 1.0, 1.0),
                           "beam": (0.0, 0.0), "platform": (None, (k - 1) / n_layers)}))
        acts.append((laser if k == 1 else "", 1.8, {"scan": (0.0, 1.0), "beam": (1.0, 1.0), f"layer{k}": (0.0, 1.0)}))
    return acts


# ===================================================================================================== MetalONE
# Sharebot MetalONE, a desktop laser powder bed fusion (LPBF) machine, launched 2019. Launch figures: 740 W x 630 D x
# 1000 H mm, 150 kg (engineering.com; 3D Printing Industry; Aniwaa; Fabbaloo gives 174 kg). Build area 65 x 65 or
# 100 x 100 mm, 100 mm tall (medicalexpo listing); fibre laser, 1070 nm, 200 W at launch (Fabbaloo 2020), later
# 300, 500 or 1000 W versions at 1064 nm (Sharebot's medicalexpo listing); spot 40-45 um. Later dealer listings give
# 1000 x 600 x 1470 mm and 270-315 kg (filament2print, 3ddevice, DirectIndustry), probably with its stand or a
# bigger configuration; the launch figures are used. Look, read off Sharebot's photos (approximate): a white cabinet,
# a dark front band round the chamber door in the upper half, the door's window, the touchscreen to its right.
METALONE = dict(W=740.0, D=630.0, H=1000.0, feet=30.0, ch_x0=-300.0, ch_x1=90.0, ch_z0=560.0, ch_z1=910.0,
                P=610.0, well=100.0)


def metalone() -> Instrument:
    p = METALONE
    W, D, H = p["W"], p["D"], p["H"]
    inst = Instrument("metalone", "Desktop metal printer (LPBF)", "Sharebot MetalONE", (W, D, H),
                      "Sharebot MetalONE launch figures (740 x 630 x 1000 mm, 150 kg; 100 x 100 x 100 mm build; "
                      "200 W fibre laser), engineering.com, 3D Printing Industry, Fabbaloo; look from Sharebot's photos",
                      floor=True, props=("load", "powder", "beam", "layer1", "layer2", "layer3"))
    yf = -D / 2
    yb = yf + 34                                   # the front face; the door handle stands proud of it, to yf
    x0, x1, z0, z1 = p["ch_x0"], p["ch_x1"], p["ch_z0"], p["ch_z1"]
    body = _piece(inst, "body")
    body.add("feet", box(-W / 2 + 20, yb + 20, 0, -W / 2 + 70, D / 2 - 20, p["feet"])
             .union(box(W / 2 - 70, yb + 20, 0, W / 2 - 20, D / 2 - 20, p["feet"])), "inst_black")
    shell = box(-W / 2, yb + 24, p["feet"], W / 2, D / 2, H).edges("|Y").fillet(18)
    shell = shell.cut(box(x0, yb + 10, z0, x1, D / 2 - 140, z1))
    body.add("housing", shell, "inst_white")
    band = box(-W / 2 + 2, yb, z0 - 60, W / 2 - 2, yb + 24, H - 40).cut(box(x0 - 10, yb - 1, z0 - 10, x1 + 10,
                                                                           yb + 25, z1 + 10))
    body.add("front band", band, "inst_dark")
    body.add("lower front", box(-W / 2 + 2, yb + 6, p["feet"] + 20, W / 2 - 2, yb + 24, z0 - 80), "inst_offwhite")
    for i in range(6):                                  # the vents in the lower front
        body.add(f"vent {i}", box(-W / 2 + 80, yb + 4, 120 + i * 40, -W / 2 + 300, yb + 6, 135 + i * 40), "inst_dark")
    body.add("service door seam", box(W / 2 - 300, yb + 4, p["feet"] + 40, W / 2 - 296, yb + 6, z0 - 110), "inst_grey")
    body.add("touchscreen", box(x1 + 70, yb - 3, z1 - 170, W / 2 - 50, yb, z1 - 30), "screen_on")
    body.add("logo", box(-W / 2 + 40, yb - 3, H - 75, -W / 2 + 200, yb, H - 55), "sharebot_orange")
    body.add("e-stop", _ycyl(34, 16, x=W / 2 - 90, y=yb - 16, z=z0 - 20), "inst_red")
    body.add("gas port", _xcyl(16, 30, x=W / 2 - 30, y=D / 2 - 120, z=200), "brass")
    door = _piece(inst, "door")
    door.add("door frame", box(x0 - 8, yb - 12, z0 - 8, x1 + 8, yb + 14, z1 + 8)
             .cut(box(x0 + 30, yb - 13, z0 + 30, x1 - 30, yb + 15, z1 - 30)), "inst_dark")
    door.add("door window", box(x0 + 30, yb - 6, z0 + 30, x1 - 30, yb + 4, z1 - 30), "laser_window")
    door.add("door handle", box(x1 - 22, yf, (z0 + z1) / 2 - 60, x1 - 8, yb - 12, (z0 + z1) / 2 + 60), "aluminium")
    cx, cy = (x0 + x1) / 2 + 30, yf + 230
    joints = _lpbf(inst, cx, cy, p["P"], p["well"], z1, hopper_x=x0 + 60, come_x=260.0)
    joints["door"] = Joint("hinge", axis=(0, 0, 1), pivot=(x0 - 8, yb - 12, 0), deg=-100.0)
    inst.joints = joints
    inst.actions = [
        ("The chamber door swings open on its left-hand hinge.", 1.4, {"door": (0.0, 1.0), "load": (0.0, 0.0)}),
        ("A 100 mm build plate goes onto the platform in the build well.", 1.8, {"load": (0.0, 1.0)}),
        ("Door shut; the chamber is purged with argon. Drawn see-through from here.", 1.6,
         {"door": (1.0, 0.0), "~body": (0.0, 0.8), "~door": (0.0, 0.8)}),
        *_layer_actions(3, "The recoater spreads a layer of powder from the dosing hopper over the plate.",
                        "The fibre laser (200 W at launch) melts the layer's cross-section, spot by spot."),
        ("Three layers drawn, 3 mm each; real ones are 20-60 um. 1000 mm tall, so it stands beside the VLM.",
         2.2, {"beam": (1.0, 0.0), "~body": (0.8, 0.0), "~door": (0.8, 0.0)}),
    ]
    inst.labels = [("chamber door", (x0 + 20, yb - 12, z1 - 40), (0.16, 0.30)),
                   ("touchscreen", (x1 + 140, yb - 3, z1 - 100), (0.84, 0.30))]
    inst.notes = ["1000 mm tall at launch (740 x 630 x 1000 mm, 150 kg); later listings give 1000 x 600 x 1470 mm and "
                  "270-315 kg, probably a stand or a bigger configuration.",
                  "Needs argon (or nitrogen for some alloys) and powder handling, which the VLM's trays don't have."]
    inst.cam = (0.8, -1.8, 1.0)
    inst.framing = (1.0, 0.5)
    return inst


# ===================================================================================================== MPRINT
# One Click Metal MPRINT (and MPRINT+), a compact LPBF machine: 1100 x 790 x 1900 mm, 440 kg (MPRINT, filament2print,
# "1100 x 1900 x 790 mm"); MPRINT+ 1.9 x 1.1 x 0.79 m, 450 kg (3D Printing Industry); MPRINTpro 1.1 x 1.9 x 0.8 m,
# 490 kg (filament2print). Read here as 1100 W x 790 D x 1900 H: the photos show a cabinet taller than it is wide,
# which the published figures don't say outright. Build 150 x 150 x 150 mm; 200 W fibre laser, 45-70 um focus,
# up to 3000 mm/s; powder in a revolver of five cartridges, 250 % of the build volume when full (Autodesk's case
# study; MPRINT+ lists four slots). Depowdering is in a separate unpacking station, MUNPACK. Look from One Click
# Metal's photos (approximate): a white cabinet on a dark plinth, the chamber door at working height, the cartridge
# hatch above it and the touchscreen on the right.
MPRINT = dict(W=1100.0, D=790.0, H=1900.0, plinth=70.0, ch_x0=-430.0, ch_x1=170.0, ch_z0=900.0, ch_z1=1340.0,
              P=980.0, well=150.0, rev_x=-260.0, rev_y=40.0, rev_z=1480.0, rev_r=150.0, cart_d=110.0, cart_h=250.0)


def mprint() -> Instrument:
    p = MPRINT
    W, D, H = p["W"], p["D"], p["H"]
    inst = Instrument("mprint", "Compact metal printer (LPBF)", "One Click Metal MPRINT", (W, D, H),
                      "One Click Metal MPRINT/MPRINT+ (1100 x 790 x 1900 mm, 440-450 kg; 150 mm cube build; 200 W "
                      "fibre laser; five-cartridge powder revolver), filament2print, 3D Printing Industry, Autodesk; "
                      "look from One Click Metal's photos", floor=True,
                      props=("load", "powder", "beam", "cartridge", "layer1", "layer2", "layer3"))
    yf = -D / 2
    yb = yf + 38                                   # the front face; handles stand proud of it, to yf
    x0, x1, z0, z1 = p["ch_x0"], p["ch_x1"], p["ch_z0"], p["ch_z1"]
    rx, ry, rz, rr = p["rev_x"], p["rev_y"], p["rev_z"], p["rev_r"]
    # the cartridge hatch; the bay behind it has room over a cartridge for the 20 mm lift off the turntable, and
    # clears the turntable's rim
    hx0, hx1, hz0, hz1 = rx - 230, rx + 230, rz - 20, rz + p["cart_h"] + 80
    body = _piece(inst, "body")
    body.add("plinth", box(-W / 2 + 15, yb + 15, 0, W / 2 - 15, D / 2 - 15, p["plinth"]), "inst_black")
    shell = box(-W / 2, yb + 24, p["plinth"], W / 2, D / 2, H).edges("|Y").fillet(20)
    shell = shell.cut(box(x0, yb + 10, z0, x1, D / 2 - 160, z1))                 # process chamber
    shell = shell.cut(box(hx0 + 10, yb + 10, hz0 + 20, hx1 - 10, D / 2 - 120, hz1 - 20))   # cartridge bay
    body.add("housing", shell, "inst_white")
    body.add("front panel", box(-W / 2 + 2, yb, z0 - 120, W / 2 - 2, yb + 24, H - 30)
             .cut(box(x0 - 10, yb - 1, z0 - 10, x1 + 10, yb + 25, z1 + 10))
             .cut(box(hx0 - 2, yb - 1, hz0 - 2, hx1 + 2, yb + 25, hz1 + 2)), "inst_offwhite")   # the hatch sits in it
    body.add("accent", box(-W / 2 + 2, yb - 2, z0 - 150, W / 2 - 2, yb + 1, z0 - 130), "ocm_teal")
    body.add("lower doors", box(-W / 2 + 20, yb + 6, p["plinth"] + 30, W / 2 - 20, yb + 24, z0 - 190), "inst_light")
    body.add("lower door seam", box(-2, yb + 4, p["plinth"] + 30, 2, yb + 6, z0 - 190), "inst_grey")
    body.add("touchscreen bezel", box(x1 + 110, yb - 2, z1 - 70, W / 2 - 50, yb, z1 + 180), "inst_black")
    body.add("touchscreen", box(x1 + 120, yb - 4, z1 - 60, W / 2 - 60, yb - 2, z1 + 170), "screen_on")
    body.add("logo", box(x1 + 120, yb - 3, H - 140, W / 2 - 60, yb, H - 110), "ocm_teal")
    body.add("e-stop", _ycyl(36, 16, x=W / 2 - 110, y=yb - 16, z=z0 - 40), "inst_red")
    body.add("feed tube", cyl(36, rz - z1 + 5, x=rx, y=ry - rr, z=z1 - 5), "stainless")     # up to the turntable
    door = _piece(inst, "door")
    door.add("door frame", box(x0 - 8, yb - 14, z0 - 8, x1 + 8, yb + 14, z1 + 8)
             .cut(box(x0 + 35, yb - 15, z0 + 35, x1 - 35, yb + 15, z1 - 35)), "inst_dark")
    door.add("door window", box(x0 + 35, yb - 6, z0 + 35, x1 - 35, yb + 4, z1 - 35), "laser_window")
    door.add("door handle", box(x1 - 26, yf, (z0 + z1) / 2 - 80, x1 - 10, yb - 14, (z0 + z1) / 2 + 80), "aluminium")
    hatch = _piece(inst, "hatch")
    hatch.add("hatch", box(hx0, yb - 10, hz0, hx1, yb + 14, hz1).edges("|Y").fillet(10), "inst_light")
    hatch.add("hatch handle", box(hx1 - 30, yf, (hz0 + hz1) / 2 - 50, hx1 - 16, yb - 10, (hz0 + hz1) / 2 + 50),
              "aluminium")
    rev = _piece(inst, "revolver")
    rev.add("turntable", cyl(2 * rr + p["cart_d"] + 20, 14, x=rx, y=ry, z=rz), "aluminium")
    rev.add("hub", cyl(60, p["cart_h"], x=rx, y=ry, z=rz + 14), "inst_grey")
    front = None
    for i in range(5):
        a = math.radians(-90 + 72 * i)
        px, py = rx + rr * math.cos(a), ry + rr * math.sin(a)
        if i == 0:
            front = (px, py)
            continue
        rev.add(f"cartridge {i}", cyl(p["cart_d"], p["cart_h"], x=px, y=py, z=rz + 14), "stainless")
        rev.add(f"cartridge cap {i}", cyl(p["cart_d"] + 6, 18, x=px, y=py, z=rz + 14 + p["cart_h"]), "ocm_teal")
    cart = _piece(inst, "cartridge")
    cart.add("cartridge", cyl(p["cart_d"], p["cart_h"], x=front[0], y=front[1], z=rz + 14), "stainless")
    cart.add("cartridge cap", cyl(p["cart_d"] + 6, 18, x=front[0], y=front[1], z=rz + 14 + p["cart_h"]), "ocm_teal")
    cx, cy = (x0 + x1) / 2 + 70, yf + 290
    joints = _lpbf(inst, cx, cy, p["P"], p["well"], z1, hopper_x=x0 + 70, come_x=400.0)
    out = -(front[1] - yf)
    joints.update({
        "door": Joint("hinge", axis=(0, 0, 1), pivot=(x0 - 8, yb - 14, 0), deg=-100.0),
        "hatch": Joint("hinge", axis=(0, 0, 1), pivot=(hx0, yb - 10, 0), deg=-100.0),
        "revolver": Joint("spin", axis=(0, 0, 1), pivot=(rx, ry, 0), deg=72.0),
        "cartridge": Joint("path", path=((0, 0, 0), (0, 0, 20), (0, out - 260, 20), (0, out - 330, -120)),
                           parent="revolver"),
    })
    inst.joints = joints
    inst.actions = [
        ("The hatch opens on the powder revolver: five sealed cartridges, 250 % of the build volume when full.", 1.6,
         {"hatch": (0.0, 1.0), "cartridge": (0.0, 0.0), "load": (0.0, 0.0)}),
        ("A spent cartridge comes out to be refilled outside; a full one goes in. No open powder.", 2.4,
         {"cartridge": (0.0, 1.0)}),
        ("", 1.6, {"cartridge": (1.0, 0.0)}),
        ("Hatch shut. The chamber door opens and a 150 mm build plate goes onto the platform.", 2.6,
         {"hatch": (1.0, 0.0), "door": (0.0, 1.0), "load": (0.0, 1.0)}),
        ("Door shut; argon purge. See-through: the revolver turns a full cartridge over the feed to the hopper.", 2.0,
         {"door": (1.0, 0.0), "revolver": (0.0, 1.0), "~body": (0.0, 0.8), "~hatch": (0.0, 0.8),
          "~door": (0.0, 0.8)}),
        *_layer_actions(3, "The recoater spreads a layer of powder over the plate.",
                        "The 200 W fibre laser melts each layer's cross-section."),
        ("Done: the plate comes out through the door to the MUNPACK station, which depowders it.", 2.4,
         {"beam": (1.0, 0.0), "~body": (0.8, 0.0), "~hatch": (0.8, 0.0), "~door": (0.8, 0.0), "door": (0.0, 1.0),
          "load": (1.0, 0.0)}),
        ("1900 mm tall: it stands beside the VLM.", 1.2, {"door": (1.0, 0.0)}),
    ]
    inst.labels = [("powder cartridge hatch", ((hx0 + hx1) / 2, yb - 10, hz1 - 30), (0.15, 0.20)),
                   ("process chamber", (x0 + 40, yb - 14, z0 + 60), (0.15, 0.55)),
                   ("touchscreen", (x1 + 200, yb - 4, z1 + 50), (0.85, 0.40))]
    inst.notes = ["The published figures are 1100 x 1900 x 790 mm (and 1.9 x 1.1 x 0.79 m); read as W x H x D from "
                  "the photos, a 1.9 m cabinet.",
                  "Needs argon and depowdering in its separate MUNPACK station; check the supply rating with the "
                  "maker."]
    inst.cam = (0.9, -2.2, 1.0)
    inst.framing = (1.05, 0.5)
    return inst


# ===================================================================================================== Meltio M450
# Meltio M450, wire-laser directed energy deposition (DED): 560 W x 600 D x 1400 H mm, 250 kg; print envelope
# 145 x 168 x 390 mm; six 200 W direct diode lasers at 976 nm, 1200 W in all, converging on a wire fed through the
# head's centre; wire 0.8-1.2 mm; 2-5 kW peak depending on options; controlled inert atmosphere (Meltio's M450
# technical specifications; MatterHackers gives 1414 mm tall; MTC's machine hub). The most compact DED found: the
# next, Meltio's own M600, is 1050 x 1050 x 1950 mm. Look from Meltio's photos (approximate): a dark cabinet, the
# print chamber behind a tall door with laser-safety glazing in the upper half, the touchscreen on the right; the
# housing colour is a guess.
M450 = dict(W=560.0, D=600.0, H=1400.0, plinth=60.0, ch_x0=-240.0, ch_x1=150.0, ch_z0=700.0, ch_z1=1290.0,
            bed_z=760.0, plate_t=12.0, wall_l=100.0, wall_w=60.0, bead=7.0, layer=9.0, n=4, standoff=10.0)


def meltio_m450() -> Instrument:
    p = M450
    W, D, H = p["W"], p["D"], p["H"]
    n = p["n"]
    inst = Instrument("meltio_m450", "Compact wire-laser DED", "Meltio M450", (W, D, H),
                      "Meltio M450 technical specifications (560 x 600 x 1400 mm, 250 kg; 145 x 168 x 390 mm "
                      "envelope; 6 x 200 W diode lasers at 976 nm; 0.8-1.2 mm wire); look from Meltio's photos",
                      floor=True, props=("load", "glow", *(f"wall{k}" for k in range(1, n + 1))))
    yf = -D / 2
    yb = yf + 34                                   # the front face; the door handle stands proud of it, to yf
    x0, x1, z0, z1 = p["ch_x0"], p["ch_x1"], p["ch_z0"], p["ch_z1"]
    body = _piece(inst, "body")
    body.add("plinth", box(-W / 2 + 10, yb + 10, 0, W / 2 - 10, D / 2 - 10, p["plinth"]), "inst_black")
    shell = box(-W / 2, yb + 24, p["plinth"], W / 2, D / 2, H).edges("|Y").fillet(14)
    shell = shell.cut(box(x0, yb + 10, z0, x1 + 80, D / 2 - 40, z1))
    body.add("housing", shell, "inst_offwhite")
    body.add("front frame", box(-W / 2 + 2, yb, z0 - 30, W / 2 - 2, yb + 24, H - 20)
             .cut(box(x0 - 10, yb - 1, z0 - 10, x1 + 10, yb + 25, z1 + 10)), "meltio_black")
    body.add("lower front", box(-W / 2 + 2, yb + 4, p["plinth"] + 20, W / 2 - 2, yb + 24, z0 - 40), "inst_dark")
    body.add("lower seam", box(-W / 2 + 20, yb + 2, z0 - 70, W / 2 - 20, yb + 4, z0 - 66), "inst_grey")
    body.add("logo", box(-W / 2 + 40, yb - 3, H - 60, -W / 2 + 200, yb, H - 40), "inst_white")
    body.add("touchscreen", box(x1 + 15, yb - 3, z1 - 230, W / 2 - 20, yb, z1 - 60), "screen_on")
    body.add("e-stop", _ycyl(34, 16, x=W / 2 - 60, y=yb - 16, z=z0 - 110), "inst_red")
    frame = _piece(inst, "frame")                  # what stays opaque when the housing goes see-through
    frame.add("bed", box(-110, -115, p["bed_z"] - 20, 110, 115, p["bed_z"]), "steel")
    frame.add("bed column", box(-60, -60, p["plinth"], 60, 60, p["bed_z"] - 20), "inst_grey")
    frame.add("spool", _xcyl(300, 100, x=-50, y=D / 2 - 200, z=380).cut(_xcyl(60, 102, x=-51, y=D / 2 - 200, z=380)),
              "inst_dark")
    frame.add("wire on spool", _xcyl(280, 90, x=-45, y=D / 2 - 200, z=380).cut(_xcyl(150, 92, x=-46, y=D / 2 - 200,
                                                                                     z=380)), "copper")
    frame.add("z column", box(-40, D / 2 - 160, z0, 40, D / 2 - 80, z1), "aluminium")
    door = _piece(inst, "door")
    door.add("door", box(x0 - 8, yb - 12, z0 - 8, x1 + 8, yb + 14, z1 + 8)
             .cut(box(x0 + 30, yb - 13, z0 + 260, x1 - 30, yb + 15, z1 - 30)), "meltio_black")
    door.add("door window", box(x0 + 30, yb - 6, z0 + 260, x1 - 30, yb + 4, z1 - 30), "laser_window")
    door.add("door handle", box(x1 - 24, yf, z0 + 300, x1 - 10, yb - 12, z0 + 460), "aluminium")
    top = p["bed_z"] + p["plate_t"]
    tip = top + p["standoff"]
    head = _piece(inst, "head")
    head.add("head body", cyl(110, 150, z=tip + 60), "inst_light")
    head.add("nozzle", cq.Workplane("XY").circle(6).workplane(offset=60).circle(22).loft().translate((0, 0, tip)),
             "copper")
    for i in range(6):                                   # the six laser fibres into the head
        a = math.radians(60 * i)
        head.add(f"fibre {i}", cyl(10, 90, x=46 * math.cos(a), y=46 * math.sin(a), z=tip + 210), "inst_orange")
    head.add("wire guide", cyl(8, 95, z=tip + 210), "brass")       # under the ceiling with the head at its highest
    head.add("carriage", box(-40, 50, tip + 120, 40, D / 2 - 160, tip + 200), "inst_grey")
    glow = _piece(inst, "glow")
    glow.add("laser cone", cq.Workplane("XY").circle(3).workplane(offset=26).circle(16).loft()
             .translate((0, 0, tip - p["standoff"] - 2)), "laser")
    glow.add("melt pool", cyl(12, 3, z=tip - p["standoff"] - 1.5), "melt")
    load = _piece(inst, "load")
    load.add("substrate plate", box(-80, -90, p["bed_z"], 80, 90, top), "steel")
    L, Wd, b, h = p["wall_l"], p["wall_w"], p["bead"], p["layer"]
    for k in range(1, n + 1):
        ring = box(-L / 2 - b / 2, -Wd / 2 - b / 2, 0, L / 2 + b / 2, Wd / 2 + b / 2, h).cut(
            box(-L / 2 + b / 2, -Wd / 2 + b / 2, -1, L / 2 - b / 2, Wd / 2 - b / 2, h + 1))
        _piece(inst, f"wall{k}").add(f"bead layer {k}", ring.translate((0, 0, top + (k - 1) * h)), "steel")
    # the head's path: from home down to a corner, round the wall, up a layer, round again ...
    pts = [(0, 0, 160)]
    s_marks = []
    for k in range(n):
        z = k * h
        pts += [(-L / 2, -Wd / 2, z), (L / 2, -Wd / 2, z), (L / 2, Wd / 2, z), (-L / 2, Wd / 2, z), (-L / 2, -Wd / 2, z)]
        s_marks.append(len(pts) - 1)
    pts.append((0, 0, 160 + n * h))
    arr = np.asarray(pts, float)
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(arr, axis=0), axis=1))])
    f = [float(s[i] / s[-1]) for i in s_marks]
    f_start = float(s[1] / s[-1])
    inst.joints = {
        "door": Joint("hinge", axis=(0, 0, 1), pivot=(x0 - 8, yb - 12, 0), deg=-100.0),
        "load": Joint("path", path=((220, -560, 200), (0, -170, 80), (0, 0, 25), (0, 0, 0))),    # clear of the door
        "head": Joint("path", path=tuple(pts)),
        "glow": Joint("fade", parent="head"),
        **{f"wall{k}": Joint("fade") for k in range(1, n + 1)},
    }
    acts = [
        ("The door opens on its left-hand hinge.", 1.4, {"door": (0.0, 1.0), "load": (0.0, 0.0)}),
        ("A steel substrate plate goes onto the bed.", 1.8, {"load": (0.0, 1.0)}),
        ("Door shut; the chamber fills with argon. Drawn see-through from here.", 1.6,
         {"door": (1.0, 0.0), "~body": (0.0, 0.8), "~door": (0.0, 0.8), "head": (0.0, f_start)}),
    ]
    prev = f_start
    for k in range(1, n + 1):
        cap = ("Six 200 W diode lasers converge on the wire fed through the head's centre; a bead of metal "
               "follows the head." if k == 1 else "Up a layer, and round again: a wall one bead wide (beads drawn "
               "about 5x)." if k == 2 else "")
        acts.append((cap, 1.8, {"head": (prev, f[k - 1]), "glow": (0.0 if k == 1 else 1.0, 1.0),
                                f"wall{k}": (0.0, 1.0)}))
        prev = f[k - 1]
    acts.append(("Lasers off; the head lifts. 1400 mm tall, about twice what the VLM's opening takes, so it stands "
                 "beside the VLM.", 2.4, {"glow": (1.0, 0.0), "head": (prev, 1.0), "~body": (0.8, 0.0),
                                          "~door": (0.8, 0.0)}))
    inst.actions = acts
    inst.labels = [("deposition head: 6 lasers, wire at the centre", (0, -55, tip + 120), (0.80, 0.20)),
                   ("laser-safe window", (x0 + 40, yb - 6, z1 - 60), (0.15, 0.30)),
                   ("touchscreen", (x1 + 60, yb - 3, z1 - 140), (0.86, 0.55))]
    inst.notes = ["The most compact DED found; Meltio's M600 is 1050 x 1050 x 1950 mm.",
                  "Needs argon and cooling, and 2-5 kW peak; wire feedstock means no loose powder."]
    inst.cam = (1.0, -2.0, 0.9)
    inst.framing = (1.05, 0.5)
    return inst


# ===================================================================================================== SnowPod
# SnowX SnowPod, a desktop LPBF machine: 360 W x 360 D x 660 H mm, 40 kg, fibre laser, 200 W (3DWithUs's hands-on
# review); build 80 x 80 x 100 mm, 40 um spot, 316L at launch; powder in sealed supply and recovery cartridges; a
# cyclone, two H13 filters inside and an H14 at the exhaust; nitrogen from the companion NitroPod, which separates it
# from air, 99.9 % at 3 L/min (3Dnatives, 2026-10-22; Makers101; 3DPrint.com). A Kickstarter kit, launch planned for
# Q4 2026: not shipping yet. The only powder-bed machine found that goes through the Shuttle's 727.5 mm opening. Look
# approximate, not checked against SnowX's photos: a white cabinet, the chamber door with a window in the upper half,
# the touchscreen to its right, the cartridges' caps on top and the exhaust filter at the back.
SNOWPOD = dict(W=360.0, D=360.0, H=660.0, feet=15.0, ch_x0=-150.0, ch_x1=60.0, ch_z0=300.0, ch_z1=560.0,
               P=330.0, well=80.0)


def snowpod() -> Instrument:
    p = SNOWPOD
    W, D, H = p["W"], p["D"], p["H"]
    inst = Instrument("snowpod", "Desktop metal printer (LPBF), pre-release", "SnowX SnowPod", (W, D, H),
                      "3DWithUs's review (360 x 360 x 660 mm, 40 kg, 200 W fibre laser); 3Dnatives and Makers101 "
                      "(80 x 80 x 100 mm build, 40 um spot, sealed cartridges, NitroPod nitrogen); look approximate",
                      props=("load", "powder", "beam", "layer1", "layer2", "layer3"))
    yf = -D / 2
    yb = yf + 20
    x0, x1, z0, z1 = p["ch_x0"], p["ch_x1"], p["ch_z0"], p["ch_z1"]
    body = _piece(inst, "body")
    body.add("feet", box(-W / 2 + 15, yb + 15, 0, -W / 2 + 45, D / 2 - 15, p["feet"])
             .union(box(W / 2 - 45, yb + 15, 0, W / 2 - 15, D / 2 - 15, p["feet"])), "inst_black")
    shell = box(-W / 2, yb + 16, p["feet"], W / 2, D / 2, H - 10).edges("|Y").fillet(14)
    shell = shell.cut(box(x0, yb + 6, z0, x1, D / 2 - 80, z1))
    body.add("housing", shell, "inst_white")
    band = box(-W / 2 + 2, yb, z0 - 40, W / 2 - 2, yb + 16, H - 40).cut(box(x0 - 8, yb - 1, z0 - 8, x1 + 8, yb + 17,
                                                                           z1 + 8))
    body.add("front band", band, "inst_dark")
    body.add("touchscreen", box(x1 + 25, yb - 3, z1 - 140, W / 2 - 22, yb, z1 - 40), "screen_on")
    body.add("logo", box(-W / 2 + 30, yb - 3, 60, -W / 2 + 130, yb, 80), "inst_blue")
    body.add("power switch", box(W / 2 - 60, yb + 12, 60, W / 2 - 35, yb + 16, 85), "inst_green")
    for i, x in enumerate((-70.0, 50.0)):              # the sealed supply and recovery cartridges' caps
        body.add(f"cartridge cap {i}", cyl(70, 10, x=x, y=60, z=H - 10), "inst_grey" if i else "inst_blue")
    body.add("exhaust filter", box(-110, D / 2 - 2, H - 220, 110, D / 2 + 4, H - 60), "inst_dark")
    door = _piece(inst, "door")
    door.add("door frame", box(x0 - 6, yb - 10, z0 - 6, x1 + 6, yb + 12, z1 + 6)
             .cut(box(x0 + 22, yb - 11, z0 + 22, x1 - 22, yb + 13, z1 - 22)), "inst_dark")
    door.add("door window", box(x0 + 22, yb - 5, z0 + 22, x1 - 22, yb + 3, z1 - 22), "laser_window")
    door.add("door handle", box(x1 - 18, yf, (z0 + z1) / 2 - 40, x1 - 6, yb - 10, (z0 + z1) / 2 + 40), "aluminium")
    cx, cy = (x0 + x1) / 2 + 18, yf + 150         # hopper, parked recoater, well and overflow just fit across it
    joints = _lpbf(inst, cx, cy, p["P"], p["well"], z1, hopper_x=x0 + 32)
    joints["door"] = Joint("hinge", axis=(0, 0, 1), pivot=(x0 - 6, yb - 10, 0), deg=-100.0)
    inst.joints = joints
    inst.actions = [
        ("The chamber door swings open on its left-hand hinge.", 1.2, {"door": (0.0, 1.0), "load": (0.0, 0.0)}),
        ("An 80 mm build plate goes onto the platform.", 1.6, {"load": (0.0, 1.0)}),
        ("Door shut; nitrogen from the NitroPod, made from air, fills the chamber. Drawn see-through from here.", 1.6,
         {"door": (1.0, 0.0), "~body": (0.0, 0.8), "~door": (0.0, 0.8)}),
        *_layer_actions(3, "The recoater spreads 316L powder from the sealed supply cartridge over the plate.",
                        "The fibre laser, a 40 um spot, melts the layer's cross-section."),
        ("660 mm tall, so it goes through the opening with 67.5 mm to spare. A Kickstarter kit: not shipping yet.",
         2.4, {"beam": (1.0, 0.0), "~body": (0.8, 0.0), "~door": (0.8, 0.0)}),
    ]
    inst.labels = [("chamber door", (x0 + 20, yb - 10, z1 - 30), (0.18, 0.30)),
                   ("powder cartridges", (-70, 60, H), (0.78, 0.20))]
    inst.notes = ["360 x 360 x 660 mm and 40 kg are 3DWithUs's figures; SnowX's announcements give the build, the "
                  "spot and the price but no outer size.",
                  "A Kickstarter kit, launch planned for Q4 2026 ($5,299 launch special, $9,299 MSRP), 316L only at "
                  "launch: not shipping yet.",
                  "Nitrogen comes from SnowX's NitroPod, which makes it from air (99.9 % at 3 L/min), so on a tray it "
                  "needs power, not a gas line. The NitroPod's size isn't published; it isn't modelled.",
                  "Powder stays in sealed supply and recovery cartridges; a cyclone, two H13 filters and an H14 at "
                  "the exhaust."]
    inst.cam = (0.9, -1.8, 1.0)
    inst.framing = (1.0, 0.5)
    return inst


REGISTRY = {"metalone": metalone, "snowpod": snowpod, "mprint": mprint, "meltio_m450": meltio_m450}
