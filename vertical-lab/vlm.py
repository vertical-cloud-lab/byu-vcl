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

# --- layout choices (not published; set so the lab's equipment fits) ------------------------
T_FLOOR = 25.0          # tray floor, steel
T_RIM = 50.0            # tray rim on the back and both sides
SKIN = 25.0             # cladding panel thickness
POST = 70.0             # corner posts
Y_FRONT, Y_LIFT, Y_REAR = -1030.0, 0.0, 1030.0      # tray centres: front column, extractor, rear column
Y_OPEN = Y_FRONT        # the opening is a gap in the front column: the tray is presented 75 mm behind the front
Z_SILL = 880.0          # top of the operation counter under the opening
Z_OPEN = 900.0          # tray bottom when presented
Z_OPEN_TOP = 1720.0     # top of the opening: 795 mm clear over the tray floor, for the 662 mm OT-2
Z_TOP_IN = UNIT_H - 260.0                           # underside of the drive bay
SLOTS = {               # tray-bottom heights of the storage positions used here, on the 25 mm pitch
    "R1": (Y_REAR, 300.0), "R2": (Y_REAR, 1100.0), "R3": (Y_REAR, 1900.0), "R4": (Y_REAR, 2700.0),
    "F1": (Y_FRONT, 1900.0), "F2": (Y_FRONT, 2700.0),
    "open": (Y_OPEN, Z_OPEN),
}
for _k, (_y, _z) in SLOTS.items():
    assert abs(_z / PITCH - round(_z / PITCH)) < 1e-9, _k

# materials: name -> (r, g, b, opacity, specular)
MATERIALS = {
    "vlm_skin": (0.86, 0.88, 0.90, 0.16, 0.2),       # cladding, ghosted so the inside shows
    "vlm_skin_solid": (0.86, 0.88, 0.90, 1.0, 0.2),
    "vlm_frame": (0.23, 0.24, 0.26, 1.0, 0.3),       # anthracite posts and rails
    "vlm_wall": (0.78, 0.80, 0.83, 0.22, 0.1),       # column side walls (perforated sheet)
    "vlm_rib": (0.66, 0.68, 0.71, 1.0, 0.3),         # tray supports
    "vlm_tray": (0.42, 0.45, 0.50, 1.0, 0.3),        # tray pans
    "vlm_lift": (0.80, 0.18, 0.16, 1.0, 0.3),        # the extractor, picked out in red
    "vlm_rail": (0.62, 0.63, 0.66, 1.0, 0.6),
    "vlm_drive": (0.20, 0.36, 0.62, 1.0, 0.4),
    "vlm_belt": (0.10, 0.10, 0.11, 1.0, 0.2),
    "vlm_shutter": (0.80, 0.88, 0.95, 0.25, 0.4),
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
    ow = TRAY_W / 2 + 60                     # half-width of the opening
    front = box(-xo, -yo - SKIN, 140, xo, -yo, H).cut(box(-ow, -yo - SKIN - 1, Z_SILL, ow, -yo + 1, Z_OPEN_TOP))
    p["front panel"] = (front, "vlm_skin", "skin_front")
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
    """Access opening in the front panel: operation counter, frame, LED light bar, light curtains,
    the operator console, and the powered safety shutter (behind the panel; the animation lifts it)."""
    p = {}
    yo = -UNIT_D / 2 - SKIN                   # outer face of the front panel
    ow = TRAY_W / 2 + 60
    p["operation counter"] = (box(-ow - 80, yo - 160, Z_SILL - 110, ow + 80, yo, Z_SILL), "vlm_counter", "bay")
    frame = box(-ow - 70, yo - 30, Z_SILL, -ow, yo, Z_OPEN_TOP + 90).union(
        box(ow, yo - 30, Z_SILL, ow + 70, yo, Z_OPEN_TOP + 90)).union(
        box(-ow - 70, yo - 30, Z_OPEN_TOP, ow + 70, yo, Z_OPEN_TOP + 90))
    p["opening frame"] = (frame, "vlm_frame", "bay")
    p["LED bar"] = (box(-ow + 30, yo - 26, Z_OPEN_TOP - 10, ow - 30, yo + 30, Z_OPEN_TOP), "vlm_led", "bay")
    cur = box(-ow + 2, yo - 26, Z_SILL + 20, -ow + 16, yo - 4, Z_OPEN_TOP - 30).union(
        box(ow - 16, yo - 26, Z_SILL + 20, ow - 2, yo - 4, Z_OPEN_TOP - 30))
    p["light curtains"] = (cur, "vlm_curtain", "bay")
    # operator console to the right of the opening, tilted back towards the user
    cx, cz = ow + 330, 1330.0
    p["console arm"] = (box(ow + 70, yo - 60, cz - 20, cx, yo, cz + 20), "vlm_frame", "console")
    pan = rbox(330, 40, 250, 8).rotate((0, 0, 0), (1, 0, 0), -15).translate((cx, yo - 70, cz - 100))
    p["console"] = (pan, "vlm_frame", "console")
    scr = box(-145, -2, 0, 145, 0, 200).rotate((0, 0, 0), (1, 0, 0), -15).translate((cx, yo - 91, cz - 76))
    p["console screen"] = (scr, "vlm_screen", "console")
    # shutter: behind the front panel, closed here; it slides up behind the panel to open
    ys = -UNIT_D / 2 + 15
    p["safety shutter"] = (box(-ow + 20, ys, Z_SILL + 5, ow - 20, ys + 10, Z_OPEN_TOP - 5), "vlm_shutter", "shutter")
    return p


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
