"""Kardex Shuttle XP 500 vertical lift module, as quoted in #53, in CadQuery.

Kardex publishes no CAD for the Shuttle XP (no STEP, BIM or Revit file turned up, and the
dealer listings carry none), so this one is built from the published figures. Every number
that has a source is in SOURCES below; the rest are marked as layout choices.

Frame: x to the right and y away from you when you face the access opening, z up from the
floor, origin at the centre of the footprint. Millimetres.

Layout (front to back): the access opening's bay, the front storage column, the extractor
(the lift) and the rear storage column. Trays are stored on supports in the columns at a
25 mm pitch; the extractor pulls a tray off its supports onto its own platform, rides up or
down between the columns, and pushes the tray into another slot or out into the opening.
"""
from __future__ import annotations

import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent / "lab_models"))
from common import box, cyl, rbox  # noqa: E402  (lab-models' helpers, copied from #199's branch)

# --- sourced figures ------------------------------------------------------------------------
IN = 25.4
TRAY_W, TRAY_D = 2450.0, 864.0       # #53: 96.46 x 34.00 in; the Shuttle XP's 864 mm tray depth
UNIT_W, UNIT_D = 2780.0, 3074.0      # Relevator Group listing for an XP 500 2450 x 864 (module W x D)
UNIT_H = 3950.0                      # #53: "less than 13'" (3962 mm); Shuttle XP heights step 100 mm from 2550
PITCH = 25.0                         # Kardex: tray supports on a 25 mm pitch (Optiflex)
TRAYS = {                            # #53: one light, one medium and one strong tray
    "A": dict(capacity_lb=1080, capacity_kg=490, kind="strong"),
    "B": dict(capacity_lb=794, capacity_kg=360, kind="medium"),
    "C": dict(capacity_lb=502, capacity_kg=228, kind="light"),
}

SOURCES = {
    "tray_w_d_mm": [TRAY_W, TRAY_D, "#53: tray size 96.46 in W x 34.00 in D (2450 x 864 mm), "
                                      "the 2450 x 864 configuration Kardex sells as XP 500-2450x864"],
    "unit_w_d_mm": [UNIT_W, UNIT_D, "Relevator Group, 'Vertical Lift Modules Kardex Shuttle XP 500 - 3 units 2450x864': "
                                      "module width 2 780 mm / tray 2 450 mm, module depth 3 074 mm / tray 864 mm"],
    "unit_h_mm": [UNIT_H, "#53: height of machine less than 13 ft; Kardex data sheet: system heights from 2 550 mm "
                          "in 100 mm steps, so 3 950 mm is the tallest under 13 ft"],
    "tray_pitch_mm": [PITCH, "Kardex Shuttle XP literature: 25 mm incremental tray storage (Optiflex)"],
    "tray_capacity": [TRAYS, "#53: light 502 lb, medium 794 lb, strong 1 080 lb per tray"],
    "electrified_trays": "#53: power reaches a tray in storage and again at the access opening, not in transit",
    "shutter": "#53: powered safety shutter doors",
    "power": "#53: 208 V three-phase",
}

# --- the access opening, from Kardex's order sheet for this configuration -------------------------------------------
# "Kardex Shuttle POF Version 16", SHUTTLE-01-500-2450x864 (StoreMoreStore's VLM option 1 specification sheet):
# front access table (TH1) 833 mm above the floor, the presented tray's underside at TH1 + 21 mm, tray floor top at
# TH1 + 22.5-23.5 mm, maximum product height 727.5 mm with 20 mm clearance required above it, a single front opening.
# The look (header with the logo and an LED light under it, anthracite side posts, the blue shutter at the back of the
# bay, slatted side walls, a blue cover under the tray, the 12 in OPTIC panel on the right post) is from Kardex's
# Shuttle 500 product renders and fact sheet. Kardex lists no separate "large" opening for the 250/500: the largest
# is this full-width one (the only bigger option is full tray extraction onto a table in front, for cranes).
Z_SILL = 833.0          # TH1, the access table
Z_OPEN = 854.0          # TH1 + 21: tray underside when presented (in the opening, not a storage slot)
MAX_GOODS_H = 727.5     # maximum product height through the opening, over the tray floor
GOODS_CLEAR = 20.0      # clearance Kardex requires above it
OPEN_W = 2500.0         # clear width between the side posts: about tray + 50 mm (renders, a real 2450 x 864 unit)
Z_OPEN_TOP = 1700.0     # underside of the header, where the LED light is (the mouth reads ~850-870 mm tall)
OPEN_H = Z_OPEN_TOP - Z_SILL
HEADER_H = 95.0         # white header band with the logo
POST_W = 115.0          # anthracite side posts of the opening
CONSOLE_X = OPEN_W / 2 + POST_W / 2       # the OPTIC panel, on the right post at header height
CONSOLE_Z = Z_OPEN_TOP - 40.0

# --- layout choices (not published; set so the lab's equipment fits) ------------------------
T_FLOOR = 3.0           # tray floor (TH1 + 22.5-23.5 - 21: a 1.5-2.5 mm sheet; 3 mm here)
T_RIM = 50.0            # tray rim on the back and both sides (overall tray height 50-53 mm)
SKIN = 25.0             # cladding panel thickness
POST = 70.0             # corner posts
Y_FRONT, Y_LIFT, Y_REAR = -1030.0, 0.0, 1030.0      # tray centres: front column, extractor, rear column
Y_OPEN = Y_FRONT        # the opening is a gap in the front column: the tray is presented 75 mm behind the front
Y_SHUTTER = Y_FRONT + TRAY_D / 2 + 35.0             # the shutter: behind the presented tray, between it and the shaft
Z_TOP_IN = UNIT_H - 260.0                           # underside of the drive bay
SLOTS = {               # tray-bottom heights of the storage positions used here, on the 25 mm pitch
    "R1": (Y_REAR, 300.0), "R2": (Y_REAR, 1100.0), "R3": (Y_REAR, 1900.0), "R4": (Y_REAR, 2700.0),
    "F1": (Y_FRONT, 1900.0), "F2": (Y_FRONT, 2700.0),
    "open": (Y_OPEN, Z_OPEN),
}
for _k, (_y, _z) in SLOTS.items():
    assert _k == "open" or abs(_z / PITCH - round(_z / PITCH)) < 1e-9, _k

# materials: name -> (r, g, b, opacity, specular)
RAL7035 = (203 / 255, 208 / 255, 204 / 255)        # light grey panels (Kardex's order sheet: RAL 7035)
FIR_BLUE = (112 / 255, 150 / 255, 164 / 255)       # shutter and the cover under the tray: RAL 230 60 15 "Silver Fir Blue"
MATERIALS = {
    "vlm_skin": (*RAL7035, 0.16, 0.2),            # cladding; the animation turns it from opaque to ghosted
    "vlm_skin_solid": (*RAL7035, 1.0, 0.2),
    "vlm_seam": (0.62, 0.65, 0.64, 0.16, 0.1),    # the joints between the 490 mm panels
    "vlm_frame": (0.23, 0.24, 0.26, 1.0, 0.3),       # anthracite posts and rails
    "vlm_post": (56 / 255, 62 / 255, 66 / 255, 1.0, 0.3),   # the opening's side posts
    "vlm_header": (0.90, 0.91, 0.91, 1.0, 0.2),      # white header band over the opening
    "vlm_logo": (0.20, 0.36, 0.56, 1.0, 0.2),
    "vlm_wall": (0.78, 0.80, 0.83, 0.22, 0.1),       # column side walls (perforated sheet)
    "vlm_bay": (*RAL7035, 1.0, 0.2),                 # slatted side walls of the bay
    "vlm_rib": (0.66, 0.68, 0.71, 1.0, 0.3),         # tray supports
    "vlm_tray": (0.42, 0.45, 0.50, 1.0, 0.3),        # tray pans
    "vlm_lift": (0.80, 0.18, 0.16, 1.0, 0.3),        # the extractor, picked out in red
    "vlm_rail": (0.62, 0.63, 0.66, 1.0, 0.6),
    "vlm_drive": (0.20, 0.36, 0.62, 1.0, 0.4),
    "vlm_belt": (0.10, 0.10, 0.11, 1.0, 0.2),
    "vlm_shutter": (*FIR_BLUE, 0.85, 0.3),
    "vlm_cover": (*FIR_BLUE, 1.0, 0.3),
    "vlm_led": (0.98, 0.97, 0.88, 1.0, 0.1),
    "vlm_screen": (0.06, 0.08, 0.12, 1.0, 0.8),
    "vlm_counter": (0.18, 0.18, 0.19, 1.0, 0.3),
    "vlm_curtain": (0.85, 0.20, 0.15, 1.0, 0.3),
    "vlm_power": (0.95, 0.75, 0.15, 1.0, 0.3),       # power connectors (electrified trays)
}


def _x(a, b):
    return box(*a, *b)


def housing() -> dict:
    """Base frame, posts, rails and cladding. Returns {name: (shape, material, group)}."""
    W, D, H = UNIT_W, UNIT_D, UNIT_H
    p = {}
    xo, yo = W / 2, D / 2
    # base frame: a steel plinth with levelling feet
    base = box(-xo, -yo, 60, xo, yo, 140).cut(box(-xo + 120, -yo + 120, 59, xo - 120, yo - 120, 141))
    p["base frame"] = (base, "vlm_frame", "base")
    feet = None
    for sx in (-1, 1):
        for sy in (-1, -0.33, 0.33, 1):
            f = cyl(90, 60, x=sx * (xo - 80), y=sy * (yo - 80))
            feet = f if feet is None else feet.union(f)
    p["levelling feet"] = (feet, "vlm_rail", "base")
    # posts at the outer corners and at both column/extractor boundaries
    posts = None
    for sx in (-1, 1):
        for y in (-yo + POST / 2, -515.0, 515.0, yo - POST / 2):
            q = box(sx * (xo - POST / 2) - POST / 2, y - POST / 2, 140, sx * (xo - POST / 2) + POST / 2, y + POST / 2, H)
            posts = q if posts is None else posts.union(q)
    p["posts"] = (posts, "vlm_frame", "posts")
    # top rails all round and across the boundaries
    rails = None
    for y in (-yo + POST / 2, -515.0, 515.0, yo - POST / 2):
        r = box(-xo, y - POST / 2, H - POST, xo, y + POST / 2, H)
        rails = r if rails is None else rails.union(r)
    for sx in (-1, 1):
        r = box(sx * (xo - POST / 2) - POST / 2, -yo, H - POST, sx * (xo - POST / 2) + POST / 2, yo, H)
        rails = rails.union(r)
    p["top rails"] = (rails, "vlm_frame", "posts")
    # cladding: sides, back, top and the front around the opening's bay
    p["side panel L"] = (box(-xo - SKIN, -yo, 140, -xo, yo, H), "vlm_skin", "skin_L")
    p["side panel R"] = (box(xo, -yo, 140, xo + SKIN, yo, H), "vlm_skin", "skin_R")
    p["back panel"] = (box(-xo, yo, 140, xo, yo + SKIN, H), "vlm_skin", "skin_back")
    p["roof"] = (box(-xo - SKIN, -yo - SKIN, H, xo + SKIN, yo + SKIN, H + SKIN), "vlm_skin", "skin_top")
    ow = OPEN_W / 2 + POST_W                 # the opening with its posts
    front = box(-xo, -yo - SKIN, 140, xo, -yo, H).cut(
        box(-ow, -yo - SKIN - 1, Z_SILL - 120, ow, -yo + 1, Z_OPEN_TOP + HEADER_H))
    p["front panel"] = (front, "vlm_skin", "skin_front")
    # panel joints, as on Kardex's renders: horizontal panels about 490 mm tall above the opening and below it
    seams = {"skin_front": None, "skin_L": None, "skin_R": None}
    for z in [Z_OPEN_TOP + HEADER_H + 490.0 * i for i in range(1, 8)] + [480.0]:
        if z > H - 100:
            continue
        for grp, b in (("skin_front", box(-xo, -yo - SKIN - 2, z - 3, xo, -yo - SKIN, z + 3)),
                       ("skin_L", box(-xo - SKIN - 2, -yo, z - 3, -xo - SKIN, yo, z + 3)),
                       ("skin_R", box(xo + SKIN, -yo, z - 3, xo + SKIN + 2, yo, z + 3))):
            seams[grp] = b if seams[grp] is None else seams[grp].union(b)
    for grp, b in seams.items():
        p[f"{grp} seams"] = (b, "vlm_seam", grp)
    return p


def columns() -> dict:
    """Front and rear storage columns: side walls with tray supports under both tray edges."""
    p = {}
    wall_x = TRAY_W / 2 + 45                  # inner face of each side wall
    rib_x = TRAY_W / 2 - 20                   # supports reach 20 mm under the tray's edge
    front = [(160, Z_SILL - 40), (Z_OPEN_TOP + 120, Z_TOP_IN)]
    for key, yc, zones in (("front", Y_FRONT, front), ("rear", Y_REAR, [(160, Z_TOP_IN)])):
        walls = ribs = None
        y0, y1 = yc - TRAY_D / 2 - 30, yc + TRAY_D / 2 + 30
        for sx in (-1, 1):
            for z0, z1 in zones:
                w = box(min(sx * wall_x, sx * (wall_x + 12)), y0, z0, max(sx * wall_x, sx * (wall_x + 12)), y1, z1)
                walls = w if walls is None else walls.union(w)
                # supports drawn every 100 mm (the real ones are every 25 mm); a tray rests on the one at its height
                for z in range(int(z0 // 100 + 1) * 100, int(z1) - 20, 100):
                    x0, x1 = sorted((sx * wall_x, sx * rib_x))
                    r = box(x0, yc - TRAY_D / 2, z - 6, x1, yc + TRAY_D / 2, z)
                    ribs = r if ribs is None else ribs.union(r)
            if key == "front":                # the presented tray rests on the opening's own supports
                x0, x1 = sorted((sx * (wall_x + 12), sx * rib_x))
                ribs = ribs.union(box(x0, yc - TRAY_D / 2, Z_OPEN - 30, x1, yc + TRAY_D / 2, Z_OPEN))
        p[f"{key} column walls"] = (walls, "vlm_wall", f"col_{key}")
        p[f"{key} column supports"] = (ribs, "vlm_rib", f"col_{key}")
    return p


def lift_rails() -> dict:
    """Four vertical guide rails, one at each corner of the extractor's shaft."""
    rails = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = sx * (UNIT_W / 2 - 115)
            y = sy * (TRAY_D / 2 + 38)
            r = box(x - 20, y - 15, 140, x + 20, y + 15, Z_TOP_IN + 120)
            rails = r if rails is None else rails.union(r)
    return {"extractor guide rails": (rails, "vlm_rail", "lift_rails")}


def drive() -> dict:
    """The extractor's drive on the roof frame: motor and gearbox, cross shaft and two belt pulleys."""
    z = Z_TOP_IN + 140
    xo = UNIT_W / 2 - 115
    p = {}
    shaft = cq.Workplane("YZ").circle(30).extrude(2 * xo).translate((-xo, 0, z))
    p["drive shaft"] = (shaft, "vlm_rail", "drive")
    pul = None
    for sx in (-1, 1):
        q = cq.Workplane("YZ").circle(95).extrude(70).translate((sx * xo - 35, 0, z))
        pul = q if pul is None else pul.union(q)
    p["belt pulleys"] = (pul, "vlm_frame", "drive")
    motor = box(UNIT_W / 2 - 560, -170, z - 110, UNIT_W / 2 - 230, 170, z + 110)
    can = cq.Workplane("YZ").circle(95).extrude(330).translate((UNIT_W / 2 - 890, 0, z))
    p["drive motor"] = (motor.union(can), "vlm_drive", "drive")
    p["drive frame"] = (box(-UNIT_W / 2 + 60, -260, Z_TOP_IN, UNIT_W / 2 - 60, 260, Z_TOP_IN + 25), "vlm_frame", "drive")
    return p


def extractor() -> dict:
    """The lift platform, its own frame, at z = 0 (tray bottom) and y = 0: moved by the animation."""
    p = {}
    w = TRAY_W + 110
    plat = box(-w / 2, -TRAY_D / 2 - 20, -90, w / 2, TRAY_D / 2 + 20, -10)
    plat = plat.cut(box(-w / 2 + 80, -TRAY_D / 2 + 60, -91, w / 2 - 80, TRAY_D / 2 - 60, -9))
    p["extractor platform"] = (plat, "vlm_lift", "lift")
    # side carriages that ride the guide rails, and the tray-pull unit along the middle
    car = None
    for sx in (-1, 1):
        x = sx * (UNIT_W / 2 - 115)
        c = box(x - 45 if sx > 0 else x - 45, -TRAY_D / 2 - 60, -160, x + 45, TRAY_D / 2 + 60, 40)
        bar = box(min(sx * w / 2, x), -40, -90, max(sx * w / 2, x), 40, -20)
        c = c.union(bar)
        car = c if car is None else car.union(c)
    p["extractor carriages"] = (car, "vlm_lift", "lift")
    p["tray-pull unit"] = (box(-140, -TRAY_D / 2 + 10, -60, 140, TRAY_D / 2 - 10, -12), "vlm_frame", "lift")
    return p


def belts() -> dict:
    """Belt runs from the pulleys down to the carriages, unit height 1: the animation stretches them."""
    p = {}
    b = None
    for sx in (-1, 1):
        x = sx * (UNIT_W / 2 - 115)
        q = box(x - 30, 88, 0, x + 30, 98, 1.0).union(box(x - 30, -98, 0, x + 30, -88, 1.0))
        b = q if b is None else b.union(q)
    p["drive belts"] = (b, "vlm_belt", "belts")
    return p


def opening() -> dict:
    """The access opening as Kardex builds it (renders and fact sheet): anthracite side posts, a white header with the
    logo and the LED light under it, slatted side walls in the bay, a blue cover under the presented tray with the
    LED-Navigator strip, the OPTIC panel on the right post, and the safety shutter at the back of the bay, between the
    presented tray and the shaft (it closes while the extractor moves; the animation lifts it)."""
    p = {}
    yo = -UNIT_D / 2 - SKIN                   # outer face of the front panel
    ow = OPEN_W / 2
    posts = box(-ow - POST_W, yo - 30, Z_SILL - 120, -ow, yo + 40, Z_OPEN_TOP + HEADER_H).union(
        box(ow, yo - 30, Z_SILL - 120, ow + POST_W, yo + 40, Z_OPEN_TOP + HEADER_H))
    p["opening posts"] = (posts, "vlm_post", "bay")
    p["opening header"] = (box(-ow, yo - 20, Z_OPEN_TOP, ow, yo + 40, Z_OPEN_TOP + HEADER_H), "vlm_header", "bay")
    p["LED light"] = (box(-ow + 20, yo - 10, Z_OPEN_TOP - 12, ow - 20, yo + 160, Z_OPEN_TOP), "vlm_led", "bay")
    # the blue cover under the tray, with the LED-Navigator strip along its top; a 50 mm lip, not a counter
    p["tray cover"] = (box(-ow, yo - 50, Z_SILL - 120, ow, yo + 30, Z_SILL), "vlm_cover", "bay")
    p["LED-Navigator"] = (box(-ow + 40, yo - 52, Z_SILL - 26, ow - 40, yo - 48, Z_SILL - 14), "vlm_led", "bay")
    # slatted side walls of the bay (the shelf rails' L-profiles), front panel to shutter
    yb0, yb1 = -UNIT_D / 2, Y_SHUTTER
    walls = None
    for sx in (-1, 1):
        x0, x1 = sorted((sx * ow, sx * (ow + 12)))
        w = box(x0, yb0, Z_SILL, x1, yb1, Z_OPEN_TOP)
        for z in range(int(Z_OPEN + 60), int(Z_OPEN_TOP) - 20, 50):
            x2, x3 = sorted((sx * ow, sx * (ow - 8)))
            w = w.union(box(x2, yb0, z, x3, yb1, z + 4))
        walls = w if walls is None else walls.union(w)
    p["bay side walls"] = (walls, "vlm_bay", "bay")
    # the 12 in OPTIC touch panel on the right post, at header height, tilted towards the operator
    pan = rbox(300, 40, 200, 8).rotate((0, 0, 0), (1, 0, 0), -10).translate((CONSOLE_X, yo - 60, CONSOLE_Z - 100))
    p["console"] = (pan, "vlm_frame", "console")
    scr = box(-130, -2, 0, 130, 0, 165).rotate((0, 0, 0), (1, 0, 0), -10).translate((CONSOLE_X, yo - 81, CONSOLE_Z - 82))
    p["console screen"] = (scr, "vlm_screen", "console")
    p["console arm"] = (box(CONSOLE_X - 20, yo - 40, CONSOLE_Z - 20, CONSOLE_X + 20, yo - 30, CONSOLE_Z + 20),
                        "vlm_frame", "console")
    # the red switch box under the opening on the right, as on the renders
    p["switch box"] = (box(ow - 260, yo - 30, 560, ow - 180, yo, 660), "vlm_curtain", "bay")
    # shutter: at the back of the bay, closed here; it slides up into the front column to open
    p["safety shutter"] = (box(-ow, Y_SHUTTER - 6, Z_OPEN - 10, ow, Y_SHUTTER + 6, Z_OPEN_TOP + 40), "vlm_shutter",
                           "shutter")
    return p


def logo() -> dict:
    """'kardex' on the header's left and 'Shuttle 500' on its right, as on the renders (PyVista text, built in lab.py)."""
    yo = -UNIT_D / 2 - SKIN - 21
    return {"kardex": (-OPEN_W / 2 + 60, yo, Z_OPEN_TOP + 22, 52.0),
            "Shuttle 500": (OPEN_W / 2 - 520, yo, Z_OPEN_TOP + 28, 40.0)}


def tray(key: str) -> dict:
    """One tray, its own frame: centre of its floor's underside at the origin."""
    p = {}
    w, d = TRAY_W, TRAY_D
    pan = box(-w / 2, -d / 2, 0, w / 2, d / 2, T_FLOOR + T_RIM)
    pan = pan.cut(box(-w / 2 + 12, -d / 2 + 12, T_FLOOR, w / 2 - 12, d / 2 - 12, T_FLOOR + T_RIM + 1))
    pan = pan.cut(box(-w / 2 + 12, -d / 2 - 1, T_FLOOR + 12, w / 2 - 12, -d / 2 + 13, T_FLOOR + T_RIM + 1))  # low front lip
    p[f"tray {key}"] = (pan, "vlm_tray", f"tray_{key}")
    # the tray's own socket at the back right, where the slot's connector meets it, and a power strip
    p[f"tray {key} socket"] = (box(w / 2 - 250, d / 2 - 50, T_FLOOR, w / 2 - 150, d / 2 - 12, T_FLOOR + 70), "vlm_power",
                               f"tray_{key}")
    p[f"tray {key} power strip"] = (box(-w / 2 + 40, d / 2 - 70, T_FLOOR, w / 2 - 280, d / 2 - 30, T_FLOOR + 40),
                                    "printer_white", f"tray_{key}")
    return p


def lamp(key: str) -> dict:
    """The tray's power lamp, a separate part so the animation can light it."""
    return {f"tray {key} lamp": (cyl(34, 14, x=TRAY_W / 2 - 200, y=TRAY_D / 2 - 31, z=T_FLOOR + 70), "led_off",
                                 f"tray_{key}")}


def all_parts() -> dict:
    parts = {}
    for f in (housing, columns, lift_rails, drive, extractor, belts, opening):
        parts.update(f())
    for k in TRAYS:
        parts.update(tray(k))
        parts.update(lamp(k))
    return parts
