"""Real UPS units for the powered trays, sized tray by tray (#303, PR #318).

Sterling, 2026-11-18: "you should also probably identify real UPS's rather than what looks like a placeholder there,
and we might need multiple types of UPS units (i.e., multiple capacities depending on the tray requirements)".

Until now every powered tray carried the same grey box with "UPS" on it, sized as an Eaton 5PX1500RTNG2, and
everything on the tray drew through it (services.py). That couldn't work on tray F (3.7 kW through a 1440 W unit)
and was far too much UPS on the trays that hold only printers. Here each tray gets a real unit, chosen from what that
tray actually has to keep alive.

    python3 ups.py                       # the sizing, tray by tray -> out/ups.json; prints the table
    python3 ups.py figure                # out/ups_sizing.png: each tray's backed load against its unit
    xvfb-run -a python3 ups.py lineup    # out/ups_lineup.png: the units side by side, to scale, front and back
    xvfb-run -a python3 ups.py still     # each unit on its own -> /tmp/ups_<model>.png

**Two branches on every tray.** The dock brings 208Y/120 V on a 30 A breaker (services.py). On the tray it goes to a
small distribution box with two branches:

* the **backed** branch, through the tray's UPS: whatever loses state, needs a long warm-up or must not stop (PCs,
  controllers, the SEM's pumps, a 0.1 mg balance, a nanoindenter's thermal equilibrium, the potentiostat, the stream
  cameras and the tray's network switch);
* the **unbacked** branch, straight from the dock: heaters and big motors (the furnace, the mounting press, the
  reflow oven, the printers' heated beds and chambers, the Aero S's vacuum extractor). They stop for the few seconds of
  a transit, and the schedule never moves a tray while one of them is working.

Most instruments have one plug, so the split is by plug, not by load inside a machine (``TRAY_LOADS``).

**The rule** (``choose``): the smallest unit in ``CATALOGUE`` whose watt rating covers everything on the backed branch
at its maker's rated draw (so nothing trips the UPS if a machine is busy when the dock lets go), and whose runtime
at the backed branch's typical draw is at least ``RUNTIME_MIN`` minutes: enough for the PCs to shut down cleanly
through the UPS's network card if a tray is ever stranded off its dock (a lift fault), against a transit of 6-8 s.

Frames as in services.py: the tray's frame has its origin at the centre of its floor's underside, x to the right, y to
the back, z up. Each unit stands on its side at the tray's back right, its back (the inlet and outlets) towards the
dock plate, at ``BACK_X``, centred on ``Y_C``; its front (display and buttons) faces the middle of the tray (-x).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
sys.path.insert(0, str(HERE / "lab_models"))

T_FLOOR = 3.0                 # vlm.T_FLOOR: the tray floor's top over its underside
BACK_X = 1060.0               # the unit's back face, tray frame (services.UPS_AT's back since round 4: the mains line
#                               from the dock plate ends here)
Y_C = 319.0                   # the unit's centre line, tray frame (services.UPS_AT[1])
RIM_LINES_Y = 388.0           # the tray's own lines run along the back rim from here back (services.line_paths)
RUNTIME_MIN = 10.0            # minutes at the typical backed draw (see the docstring)
TRANSIT_S = 8.0               # the longest transit, R4 or 2R4 to the opening (services.py: about 6 s from R2)
SLOT = {"A": "R2", "B": "R3", "C": "F1", "D": "R1", "E": "R4", "F": "F2",           # setup_lab.TRAYS
        "K": "2R1", "L": "2R2", "M": "2R3", "H": "2R4", "G": "2F1", "I": "2F2"}
SHUTTLE = {k: 2 if v.startswith("2") else 1 for k, v in SLOT.items()}
RULE = (f"the smallest unit that carries the tray's backed branch at its rated draw and runs at least "
        f"{RUNTIME_MIN:.0f} min at its typical draw; heaters and big motors on the unbacked branch")


# ===================================================================================================== materials
MATERIALS = {      # (r, g, b, opacity, specular), as instruments.MATERIALS
    "ups_body": (0.11, 0.11, 0.12, 1.0, 0.30),        # black powder-coated steel
    "ups_bezel": (0.08, 0.08, 0.09, 1.0, 0.25),       # black plastic front
    "ups_vent": (0.025, 0.025, 0.03, 1.0, 0.05),      # the dark of a vent slot
    "ups_trim": (0.42, 0.43, 0.45, 1.0, 0.45),        # a grey or silver trim on the front
    "ups_rear": (0.20, 0.21, 0.22, 1.0, 0.35),        # the rear panel, bare zinc-plated or dark
    "ups_outlet": (0.06, 0.06, 0.06, 1.0, 0.20),      # receptacles and cords
    "ups_lcd": (0.55, 0.72, 0.86, 1.0, 0.60),         # a lit display
    "ups_button": (0.30, 0.31, 0.33, 1.0, 0.40),
    "ups_green": (0.15, 0.80, 0.30, 1.0, 0.20),       # LED colours, as services.UPS_LED
    "ups_amber": (1.00, 0.62, 0.10, 1.0, 0.20),
    "ups_bracket": (0.62, 0.63, 0.66, 1.0, 0.60),     # our cradle and strap, zinc-plated steel
    "ups_label": (0.95, 0.95, 0.93, 1.0, 0.15),       # an asset label
    "ups_dcu": (0.80, 0.81, 0.80, 1.0, 0.25),         # a DIN-rail module's light grey housing
    "ups_rail": (0.70, 0.71, 0.73, 1.0, 0.70),        # DIN rail
    "ups_silver": (0.74, 0.75, 0.77, 1.0, 0.55),      # a brushed or silver-painted bezel (APC's lithium units)
    "ups_panel": (0.05, 0.05, 0.06, 1.0, 0.70),       # a gloss black display panel
    "ups_blue": (0.16, 0.36, 0.78, 1.0, 0.30),        # APC's blue battery-pack connector; Eaton's badge
    "ups_red": (0.82, 0.12, 0.12, 1.0, 0.30),
    "ups_orange": (0.93, 0.42, 0.12, 1.0, 0.30),      # Vertiv's stripe
    "ups_purple": (0.55, 0.22, 0.62, 1.0, 0.30),
    "ups_body_grey": (0.27, 0.28, 0.30, 1.0, 0.35),   # APC's Ultra: a charcoal chassis
    "ups_strap": (0.07, 0.07, 0.08, 1.0, 0.15),       # black polyester webbing
    "ups_lcd_white": (0.82, 0.85, 0.88, 1.0, 0.50),   # a white-backlit display
}


def _box(x0, y0, z0, x1, y1, z1):
    from common import box
    return box(min(x0, x1), min(y0, y1), min(z0, z1), max(x0, x1), max(y0, y1), max(z0, z1))


def _xcyl(d, x0, x1, y, z):
    """A cylinder along x from x0 to x1 at (y, z)."""
    import cadquery as cq
    lo, hi = min(x0, x1), max(x0, x1)
    return cq.Workplane("YZ").circle(d / 2).extrude(hi - lo).translate((lo, y, z))


# ===================================================================================================== geometry
# A unit is drawn in its own "tower" frame: standing on its side as on the tray, its back face (inlet, outlets, card
# slot, fans) at x = 0, its front (bezel, display, buttons) at x = -D, its thickness (the rack height: 1U or 2U) along
# y, centred, and the rack width standing up along z from its foot at z = 0. A unit sold as a tower ("form": "tower")
# is drawn the same way with its own width along y and its height along z.
#
# What each part of the face is comes from the maker's photos and drawings (CATALOGUE[m]["face"], notes/ups.md); sizes
# of the details (display, buttons, receptacles) are read off the photos against the published overall size, so they
# are approximate to a few mm.
NEMA = {      # receptacle faces as drawn: (w, h) of the plate and the slot pattern; NEMA WD 6 sizes, rounded
    "5-15R": (26.0, 34.0), "5-20R": (26.0, 34.0), "L5-30R": (44.0, 44.0), "L6-20R": (40.0, 40.0),
    "L6-30R": (44.0, 44.0), "C13": (24.0, 16.0), "C19": (30.0, 20.0),
}


def _yz(m, u, v):
    """Rack-face coordinates to the tower frame's face: u along the rack width from its left end (as the front is seen
    in a rack) becomes z, up from the foot; v up the rack height from its bottom becomes y (the rack's top towards
    +y). The makers' tower orientation stands the unit on its left end, so the display (at the right end) is at the
    top."""
    D, T, H = tower_dims(m)
    return v - T / 2, u


def _pattern(m, x, u0, u1, v0, v1, shape, size, pitch, depth=0.7):
    """Holes (or slots) of a grille as one compound: `shape` 'round', 'hex' or 'tri' of `size` across, staggered on
    `pitch`, cut `depth` mm into the face at x (they are drawn as dark solids just proud of the plate)."""
    import cadquery as cq
    pts = []
    row = 0
    v = v0 + pitch / 2
    while v <= v1 - pitch / 2 + 1e-6:
        off = (pitch / 2) if row % 2 else 0.0
        u = u0 + pitch / 2 + off
        while u <= u1 - pitch / 2 + 1e-6:
            pts.append(_yz(m, u, v))
            u += pitch
        v += pitch * (0.866 if shape in ("hex", "tri", "round") else 1.0)
        row += 1
    if not pts:
        return None
    wp = cq.Workplane("YZ", origin=(x, 0, 0)).pushPoints(pts)
    if shape == "hex":
        wp = wp.polygon(6, size)
    elif shape == "tri":
        wp = wp.polygon(3, size)
    elif shape == "slot":
        wp = wp.rect(size, pitch * 0.45)
    else:
        wp = wp.circle(size / 2)
    return wp.extrude(-depth)


def unit_parts(m: dict) -> dict:
    """{name: (shape, material)} of catalogue entry m in its tower frame (see above): the chassis, the bezel with its
    grilles, display module, buttons and status LEDs (CATALOGUE[m]["face"], in rack-face mm, from the maker's photos
    scaled to its published size), the back with its receptacles, inlet or cord, card slot, ports, vents and battery
    connector (CATALOGUE[m]["rear"], tower mm)."""
    import cadquery as cq
    D, T, H = tower_dims(m)
    f = face(m) if m.get("family") else m.get("face", {})
    p = {}
    bt = f.get("bezel_t", 16.0)
    body = cq.Workplane("XY").box(D - bt, T, H, centered=False).translate((-(D - bt), -T / 2, 0))
    try:
        body = body.edges("|X").fillet(f.get("edge_r", 2.0))
    except Exception:                             # noqa: BLE001  (a fillet that won't take: square corners)
        pass
    p["chassis"] = (body, f.get("body", "ups_body"))
    # the bezel: a moulding over the whole face, rounded at its edges
    bez = cq.Workplane("XY").box(bt, T - 0.6, H - 0.6, centered=False).translate((-D, -(T - 0.6) / 2, 0.3))
    try:
        bez = bez.faces("<X").edges().fillet(min(3.0, bt / 3))
    except Exception:                             # noqa: BLE001
        pass
    p["bezel"] = (bez, f.get("bezel", "ups_bezel"))
    xf = -D                                        # the bezel's face
    holes = None
    for i, g in enumerate(f.get("grilles", [])):
        (u0, u1), (v0, v1) = g["u"], g["v"]
        y0, z0 = _yz(m, u0, v0)
        y1, z1 = _yz(m, u1, v1)
        p[f"grille {i}"] = (_box(xf - 0.6, y0, z0, xf, y1, z1), g.get("plate", "ups_bezel"))
        shape, size, pitch = g.get("hole", ("hex", 5.0, 7.0))
        h = _pattern(m, xf - 0.65, u0 + 2, u1 - 2, v0 + 2, v1 - 2, shape, size, pitch)
        if h is not None:
            holes = h if holes is None else holes.add(h)
    if holes is not None:
        p["grille holes"] = (holes, "ups_vent")
    for i, (u0, u1, v0, v1, mat) in enumerate(f.get("stripes", [])):
        y0, z0 = _yz(m, u0, v0)
        y1, z1 = _yz(m, u1, v1)
        p[f"stripe {i}"] = (_box(xf - 1.9, y0, z0, xf - 1.4, y1, z1), mat)       # proud of the grille's holes
    for i, (u, v, d, mat) in enumerate(f.get("discs", [])):           # a round badge on the front
        y, z = _yz(m, u, v)
        p[f"badge {i}"] = (_xcyl(d, xf - 2.0 - 0.3 * i, xf - 0.5, y, z), mat)
    if f.get("module"):
        md = f["module"]
        (u0, u1), (v0, v1) = md["u"], md["v"]
        y0, z0 = _yz(m, u0, v0)
        y1, z1 = _yz(m, u1, v1)
        p["display module"] = (_box(xf - 1.2, y0, z0, xf, y1, z1), md.get("mat", "ups_bezel"))
    if f.get("lcd"):
        (u0, u1), (v0, v1) = f["lcd"]
        y0, z0 = _yz(m, u0, v0)
        y1, z1 = _yz(m, u1, v1)
        p["lcd"] = (_box(xf - 1.8, y0, z0, xf - 1.2, y1, z1), f.get("lcd_mat", "ups_lcd"))
    btns = None
    for (u, v, d) in f.get("buttons", []):
        y, z = _yz(m, u, v)
        b = _xcyl(d, xf - 2.6, xf - 1.0, y, z)
        btns = b if btns is None else btns.union(b)
    if btns is not None:
        p["buttons"] = (btns, "ups_button")
    if f.get("power"):
        u, v, d = f["power"]
        y, z = _yz(m, u, v)
        p["power button"] = (_xcyl(d, xf - 3.2, xf - 1.0, y, z), "ups_button")
        p["power ring"] = (_xcyl(d + 4, xf - 2.0, xf - 1.0, y, z).cut(_xcyl(d + 0.5, xf - 3, xf, y, z)),
                           f.get("power_ring", "ups_trim"))
    # the status LEDs, their own parts so a scene can light them: green on mains, amber on battery
    lu, lv = f.get("leds", (H - 30.0, T - 14.0))
    y, z = _yz(m, lu, lv)
    p["led mains"] = (_box(xf - 1.6, y - 3, z - 3, xf - 0.5, y + 3, z + 3), "ups_green")
    y, z = _yz(m, lu, lv - 10.0)
    p["led battery"] = (_box(xf - 1.6, y - 3, z - 3, xf - 0.5, y + 3, z + 3), "ups_amber")
    # ---- the back (tower mm: y across, z up from the foot)
    r = rear(m) if m.get("family") else m.get("rear", {})
    xb = 0.0
    p["rear panel"] = (_box(-1.0, -T / 2 + 1.5, 1.5, xb + 0.4, T / 2 - 1.5, H - 1.5), r.get("panel", "ups_rear"))
    outs = None
    for typ, y, z in r.get("outlets", []):
        w, h = NEMA[typ]
        o = _box(xb, y - h / 2, z - w / 2, xb + 4, y + h / 2, z + w / 2)      # a receptacle turned with the unit
        for dz in (-5.5, 5.5):                                                 # its two blade slots
            o = o.cut(_box(xb + 2.5, y - 4, z + dz - 1.2, xb + 5, y + 4, z + dz + 1.2))
        o = o.cut(_xcyl(5.0, xb + 2.5, xb + 5, y - 9.0, z))                     # and its ground hole
        outs = o if outs is None else outs.union(o)
    if outs is not None:
        p["receptacles"] = (outs, "ups_outlet")
    for i, (y0, y1, z0, z1) in enumerate(r.get("plates", [])):               # an outlet group's metal plate
        p[f"outlet plate {i}"] = (_box(xb, y0, z0, xb + 1.5, y1, z1), "ups_trim")
    for i, (y0, y1, z0, z1, shape, size, pitch) in enumerate(r.get("vents", [])):
        p[f"rear vent {i}"] = (_box(xb, y0, z0, xb + 0.5, y1, z1), "ups_rear")
        mm = dict(m)
        h = _pattern(dict(tower_mm=(D, T, H)), xb + 1.2, z0, z1, y0 + T / 2, y1 + T / 2, shape, size, pitch)
        if h is not None:
            p[f"rear vent holes {i}"] = (h, "ups_vent")
    for i, (y, z, w, h) in enumerate(r.get("ports", [])):                     # RJ45, USB, serial, EPO
        p[f"port {i}"] = (_box(xb, y - h / 2, z - w / 2, xb + 3, y + h / 2, z + w / 2), "ups_outlet")
    if r.get("slot"):
        y0, y1, z0, z1 = r["slot"]
        p["card slot"] = (_box(xb, y0, z0, xb + 2.0, y1, z1), "ups_rear")
    if r.get("ebm"):
        y, z = r["ebm"]
        p["battery connector"] = (_box(xb, y - 18, z - 12, xb + 16, y + 18, z + 12), "ups_blue")
    if r.get("cover"):
        y0, y1, z0, z1 = r["cover"]
        p["battery cover"] = (_box(xb, y0, z0, xb + 1.5, y1, z1), "ups_body")
    if r.get("breaker"):
        y, z = r["breaker"]
        p["breaker"] = (_xcyl(12.0, xb, xb + 8, y, z), "ups_outlet")
    cy, cz = r.get("cord", (0.0, 130.0))                 # the input cord's strain relief (the cord: cord_parts)
    p["cord gland"] = (_xcyl(17.0, xb, xb + 14, cy, cz), "ups_outlet")
    return p


def tower_dims(m: dict) -> tuple:
    """(depth, thickness, height) of entry m as it stands on the tray, mm: its published front (width x height, as it
    sits in a rack) and depth, turned on its side; or "tower_mm" as given."""
    if "front_mm" in m:
        W, Hr = m["front_mm"]
        return (float(m["depth_mm"]), float(Hr), float(W))
    return tuple(m["tower_mm"])


def cradle_parts(m: dict) -> dict:
    """Our restraint, in the unit's tower frame (a tray starts and stops at up to about 1 m/s^2, and the makers' tower
    feet aren't made to be bolted down): two 25 x 25 x 3 mm zinc-plated steel angles along the foot, bolted to the
    tray floor, and two 20 mm black ratchet straps over the top, at a quarter and three quarters of the depth, hooked
    into the angles. The straps come off and the angles stay when the unit is changed."""
    D, T, H = tower_dims(m)
    p = {}
    for s in (-1, 1):
        y0 = s * (T / 2 + 0.5)
        p[f"angle {s:+d}"] = (_box(-D + 15, y0, 0, -15, y0 + s * 25, 3).union(
            _box(-D + 15, y0, 0, -15, y0 + s * 3, 25)), "ups_bracket")
    for i, fx in enumerate((-D / 4, -3 * D / 4)):
        strap = _box(fx - 10, -T / 2 - 2.0, H, fx + 10, T / 2 + 2.0, H + 1.6)
        for s in (-1, 1):
            strap = strap.union(_box(fx - 10, s * (T / 2 + 0.4), 22, fx + 10, s * (T / 2 + 2.0), H + 1.6))
        p[f"strap {i}"] = (strap, "ups_strap")
        p[f"buckle {i}"] = (_box(fx - 13, -T / 2 - 6.0, H * 0.55, fx + 13, -T / 2 - 1.5, H * 0.55 + 34), "ups_bracket")
    return p



# ===================================================================================================== faces
# Each family's front and back, read off the maker's product photos (notes/ups.md lists them) as fractions of the
# published width and height of its front (rack orientation: fu from the left end, fv from the bottom), so one entry
# draws every size of the family. face(): mm for a catalogue entry. The backs are given in tower mm by rear() from the
# rear photos where there is one; where there is none (said in the entry's "rear_note"), the layout is ours.
FACES = {
    # APC Smart-UPS Lithium-Ion, short depth (SMTL750/1000/1500/2200RM2UC, 2U): a silver bezel perforated with
    # alternating triangles, a red APC logo with "by Schneider Electric" at the left, a black display module at the
    # right end: four LEDs over a blue-backlit text LCD, four keys under it, the power key over it.
    "smtl": dict(bezel="ups_silver", body="ups_body",
                 grilles=[dict(fu=(0.02, 0.78), fv=(0.07, 0.93), plate="ups_silver", hole=("tri", 7.0, 10.5))],
                 module=dict(fu=(0.795, 0.975), fv=(0.06, 0.94), mat="ups_bezel"),
                 lcd=((0.82, 0.955), (0.40, 0.62)), lcd_mat="ups_lcd",
                 buttons=[(0.85, 0.27, 7.0), (0.85, 0.13, 7.0), (0.925, 0.27, 7.0), (0.925, 0.13, 7.0)],
                 power=(0.888, 0.86, 7.0), leds=(0.845, 0.74),
                 logos=[("APC", 0.115, 0.50, 0.11, "red")]),
    # APC Smart-UPS SRT (SRT1000/1500/2200/3000RMXLA, 2U): a black bezel over a black hexagonal mesh, a white APC logo
    # at its lower left, the display module at the right end: a white-backlit graphic LCD, ESC/OK and up/down keys
    # under it, the power key over it.
    "srt": dict(bezel="ups_bezel", body="ups_body",
                grilles=[dict(fu=(0.05, 0.78), fv=(0.08, 0.92), plate="ups_bezel", hole=("hex", 6.0, 8.0))],
                module=dict(fu=(0.80, 0.965), fv=(0.04, 0.96), mat="ups_panel"),
                lcd=((0.815, 0.95), (0.36, 0.72)), lcd_mat="ups_lcd_white",
                buttons=[(0.84, 0.24, 7.0), (0.84, 0.11, 7.0), (0.925, 0.24, 7.0), (0.925, 0.11, 7.0)],
                power=(0.882, 0.86, 7.0), leds=(0.955, 0.86),
                logos=[("APC", 0.10, 0.22, 0.13, "white")]),
    # APC Smart-UPS Ultra (SRTL2K2RM1UC, SRTL3KRM1UC, 1U): a silver bezel perforated with triangles, a band of green
    # status triangles and the APC Smart-UPS logo at its right end, a gloss black display panel: a round power key
    # ringed in green, a white LCD with touch arrows; the Schneider Electric logo at the left end. It stands as a tower
    # on its left end, display at the top (APC's own tower photo).
    "srtl": dict(bezel="ups_silver", body="ups_body_grey",
                 grilles=[dict(fu=(0.07, 0.70), fv=(0.12, 0.88), plate="ups_silver", hole=("tri", 4.6, 7.0))],
                 module=dict(fu=(0.735, 0.94), fv=(0.0, 1.0), mat="ups_panel"),
                 lcd=((0.80, 0.90), (0.12, 0.88)), lcd_mat="ups_lcd_white",
                 buttons=[(0.92, 0.70, 4.0), (0.92, 0.30, 4.0)],
                 power=(0.775, 0.50, 11.0), power_ring="ups_green", leds=(0.705, 0.70),
                 logos=[("APC", 0.60, 0.40, 0.30, "grey"), ("Schneider", 0.015, 0.30, 0.17, "white")]),
    # Vertiv Liebert PSI5 Lithium-Ion short depth (PSI5-500SRT1ULI, PSI5-800SRT2ULI): a black diamond-mesh grille the
    # length of the front with a thin orange stripe along its middle, Vertiv's round badge at the left end and a
    # "PSI5 Lithium-ion" tag on the stripe; at the right end a display module: four LEDs over a colour LCD and four
    # keys under it (Vertiv's family photo; it stands as a tower on its left end, display at the top).
    "psi5sd": dict(bezel="ups_bezel", body="ups_body",
                   grilles=[dict(fu=(0.015, 0.80), fv=(0.06, 0.94), plate="ups_bezel", hole=("hex", 5.0, 6.6))],
                   module=dict(fu=(0.805, 0.955), fv=(0.03, 0.97), mat="ups_panel"),
                   lcd=((0.82, 0.925), (0.28, 0.80)), lcd_mat="ups_lcd",
                   buttons=[(0.825, 0.13, 4.5), (0.855, 0.13, 4.5), (0.885, 0.13, 4.5), (0.915, 0.13, 4.5)],
                   power=(0.94, 0.55, 5.5), leds=(0.94, 0.85),
                   stripes=[(0.06, 0.80, 0.48, 0.52, "ups_orange"), (0.958, 0.99, 0.48, 0.52, "ups_orange")],
                   discs=[(0.035, 0.50, 0.17, "ups_label")],
                   logos=[("PSI5 Lithium-ion", 0.60, 0.56, 0.085, "white")]),
    # Eaton 9PX lithium-ion (9PX1500RT-L ..., 2U): two silver panels perforated with round holes either side of a
    # black display module (a blue-backlit graphic LCD over five keys), the blue Eaton badge on the right panel.
    "9pxl": dict(bezel="ups_bezel", body="ups_body",
                 grilles=[dict(fu=(0.01, 0.335), fv=(0.06, 0.94), plate="ups_silver", hole=("round", 5.0, 7.5)),
                          dict(fu=(0.67, 0.99), fv=(0.06, 0.94), plate="ups_silver", hole=("round", 5.0, 7.5))],
                 module=dict(fu=(0.345, 0.66), fv=(0.0, 1.0), mat="ups_bezel"),
                 lcd=((0.44, 0.565), (0.36, 0.86)), lcd_mat="ups_lcd",
                 buttons=[(0.445, 0.18, 6.0), (0.475, 0.18, 6.0), (0.505, 0.18, 6.0), (0.535, 0.18, 6.0)],
                 power=(0.565, 0.18, 6.0), leds=(0.62, 0.80), badge=(0.76, 0.84, 0.30, 0.70, "ups_blue"),
                 logos=[("EATON", 0.765, 0.47, 0.13, "white")]),
    # Vertiv Liebert GXT5 lithium-ion (GXT5LI-...LVRT2UXL, 2U): black diamond-mesh grilles either side of a display
    # module with a colour LCD, keys at its left and the power key at its right; an orange stripe and the Vertiv badge
    # on the left grille, a purple stripe and "Liebert GXT5 / Lithium-ion" on the right one.
    "gxt5li": dict(bezel="ups_bezel", body="ups_body",
                   grilles=[dict(fu=(0.01, 0.42), fv=(0.06, 0.94), plate="ups_bezel", hole=("hex", 5.0, 6.5)),
                            dict(fu=(0.70, 0.99), fv=(0.06, 0.94), plate="ups_bezel", hole=("hex", 5.0, 6.5))],
                   module=dict(fu=(0.43, 0.69), fv=(0.0, 1.0), mat="ups_panel"),
                   lcd=((0.495, 0.66), (0.25, 0.78)), lcd_mat="ups_lcd",
                   buttons=[(0.465, 0.75, 5.0), (0.465, 0.58, 5.0), (0.465, 0.41, 5.0), (0.465, 0.24, 5.0)],
                   power=(0.675, 0.35, 6.0), leds=(0.675, 0.75),
                   stripes=[(0.03, 0.42, 0.47, 0.53, "ups_orange"), (0.70, 0.98, 0.47, 0.53, "ups_purple")],
                   discs=[(0.115, 0.50, 0.30, "ups_panel"), (0.115, 0.50, 0.17, "ups_label")],
                   logos=[("Liebert GXT5", 0.76, 0.56, 0.12, "white"), ("Lithium-ion", 0.80, 0.30, 0.09, "grey")]),
}


def face(m: dict) -> dict:
    """m's front in rack-face mm (unit_parts' "face"), from its family's FACES entry and its published front."""
    fam = FACES[m["family"]]
    W, Hr = m["front_mm"]                       # the front's width and height as it sits in a rack
    out = dict(bezel=fam["bezel"], body=fam["body"], bezel_t=m.get("bezel_t", 16.0 if Hr > 60 else 10.0))
    out["grilles"] = [dict(u=(g["fu"][0] * W, g["fu"][1] * W), v=(g["fv"][0] * Hr, g["fv"][1] * Hr),
                           plate=g["plate"], hole=g["hole"]) for g in fam.get("grilles", [])]
    md = fam["module"]
    out["module"] = dict(u=(md["fu"][0] * W, md["fu"][1] * W), v=(md["fv"][0] * Hr, md["fv"][1] * Hr), mat=md["mat"])
    (a, b), (c, d) = fam["lcd"]
    out["lcd"] = ((a * W, b * W), (c * Hr, d * Hr))
    out["lcd_mat"] = fam.get("lcd_mat", "ups_lcd")
    out["buttons"] = [(fu * W, fv * Hr, dd) for fu, fv, dd in fam.get("buttons", [])]
    if fam.get("power"):
        fu, fv, dd = fam["power"]
        out["power"] = (fu * W, fv * Hr, dd)
    out["power_ring"] = fam.get("power_ring", "ups_trim")
    fu, fv = fam.get("leds", (0.9, 0.9))
    out["leds"] = (fu * W, fv * Hr)
    out["stripes"] = [(a * W, b * W, c * Hr, d * Hr, mat) for a, b, c, d, mat in fam.get("stripes", [])]
    if fam.get("badge"):
        a, b, c, d, mat = fam["badge"]
        out["stripes"].append((a * W, b * W, c * Hr, d * Hr, mat))
    out["logos"] = [(t, fu * W, fv * Hr, fh * Hr, col) for t, fu, fv, fh, col in fam.get("logos", [])]
    out["discs"] = [(fu * W, fv * Hr, fd * Hr, mat) for fu, fv, fd, mat in fam.get("discs", [])]
    return out


# The backs, from the rear photos as fractions of the rear seen square on (gf from its left, gg from its bottom). Seen
# from behind, the rack's left end is on the right; standing as a tower on that end, the rear's left is at the top.
REARS = {
    "smtl": dict(outlets=[("5-15R", 0.22, 0.72), ("5-15R", 0.29, 0.72), ("5-15R", 0.355, 0.72),
                          ("5-15R", 0.135, 0.30), ("5-15R", 0.20, 0.30), ("5-15R", 0.265, 0.30)],
                 vents=[(0.28, 0.50, 0.05, 0.45, "hex", 5.0, 7.0)], slot=(0.37, 0.62, 0.55, 0.95),
                 ports=[(0.505, 0.22), (0.53, 0.22), (0.585, 0.22)], cover=(0.63, 0.995, 0.03, 0.97),
                 breaker=(0.13, 0.85), cord=(0.13, 0.47)),
    "srt": dict(outlets=[("5-15R", 0.72, 0.72), ("5-15R", 0.81, 0.72), ("5-15R", 0.90, 0.72),
                         ("5-15R", 0.72, 0.28), ("5-15R", 0.81, 0.28), ("5-15R", 0.90, 0.28)],
                plates=[(0.64, 0.98, 0.03, 0.97)],
                vents=[(0.075, 0.47, 0.08, 0.58, "hex", 5.0, 7.0)], slot=(0.10, 0.46, 0.62, 0.95),
                ports=[(0.045, 0.82), (0.045, 0.60), (0.045, 0.38), (0.09, 0.12)], ebm=(0.54, 0.55),
                cord=(0.42, 0.85)),
    "srtl": dict(outlets=[("5-20R", 0.66, 0.5), ("5-20R", 0.73, 0.5), ("5-20R", 0.80, 0.5), ("5-20R", 0.87, 0.5)],
                 vents=[(0.06, 0.40, 0.12, 0.88, "hex", 4.0, 6.0)], slot=(0.42, 0.58, 0.10, 0.90),
                 ports=[(0.60, 0.70), (0.60, 0.30)], cord=(0.95, 0.5)),
    "psi5sd": dict(outlets=[("5-15R", 0.58, 0.68), ("5-15R", 0.66, 0.68), ("5-15R", 0.74, 0.68),
                            ("5-15R", 0.58, 0.30), ("5-15R", 0.66, 0.30), ("5-15R", 0.74, 0.30)],
                   vents=[(0.05, 0.36, 0.12, 0.88, "hex", 4.0, 6.0)], slot=(0.38, 0.54, 0.55, 0.95),
                   ports=[(0.40, 0.25), (0.45, 0.25)], cord=(0.90, 0.5), breaker=(0.84, 0.75)),
    "9pxl": dict(outlets=[("5-15R", 0.70, 0.72), ("5-15R", 0.78, 0.72), ("5-15R", 0.86, 0.72),
                          ("5-15R", 0.70, 0.28), ("5-15R", 0.78, 0.28), ("5-15R", 0.86, 0.28)],
                 vents=[(0.05, 0.40, 0.10, 0.90, "round", 4.0, 6.0)], slot=(0.44, 0.62, 0.55, 0.95),
                 ports=[(0.46, 0.25), (0.50, 0.25)], cord=(0.95, 0.5)),
    "gxt5li": dict(outlets=[("5-15R", 0.66, 0.72), ("5-15R", 0.74, 0.72), ("5-15R", 0.82, 0.72),
                            ("5-15R", 0.66, 0.28), ("5-15R", 0.74, 0.28), ("5-15R", 0.82, 0.28)],
                   vents=[(0.05, 0.40, 0.10, 0.90, "hex", 4.0, 6.0)], slot=(0.44, 0.62, 0.55, 0.95),
                   ports=[(0.46, 0.25), (0.50, 0.25)], cord=(0.95, 0.5)),
}


def rear(m: dict) -> dict:
    """m's back in tower mm (unit_parts' "rear"), from its family's REARS entry: the rear's gf (from its left as seen
    from behind) is the tower's height from the top, gg (from its bottom) the thickness from -y."""
    r = REARS[m["family"]]
    D, T, H = tower_dims(m)

    def yz(gf, gg):
        return gg * T - T / 2, (1.0 - gf) * H
    out = dict(panel="ups_rear")
    out["outlets"] = [(typ, *yz(gf, gg)) for typ, gf, gg in r.get("outlets", [])]
    if m.get("outlets_rear"):                                     # the entry's own receptacles, where it differs
        out["outlets"] = [(typ, *yz(gf, gg)) for typ, gf, gg in m["outlets_rear"]]
    out["plates"] = []
    for a, b, c, d in r.get("plates", []):
        y0, z1 = yz(a, c)
        y1, z0 = yz(b, d)
        out["plates"].append((min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1)))
    out["vents"] = []
    for a, b, c, d, shape, size, pitch in r.get("vents", []):
        y0, z1 = yz(a, c)
        y1, z0 = yz(b, d)
        out["vents"].append((min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1), shape, size, pitch))
    out["ports"] = [(*yz(gf, gg), 14.0, 12.0) for gf, gg in r.get("ports", [])]
    if r.get("slot"):
        a, b, c, d = r["slot"]
        y0, z1 = yz(a, c)
        y1, z0 = yz(b, d)
        out["slot"] = (min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))
    if r.get("cover"):
        a, b, c, d = r["cover"]
        y0, z1 = yz(a, c)
        y1, z0 = yz(b, d)
        out["cover"] = (min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))
    for key in ("ebm", "breaker", "cord"):
        if r.get(key):
            out[key] = yz(*r[key])
    return out

# ===================================================================================================== sizing
def runtime_min(m: dict, w: float) -> float:
    """Minutes the unit m carries w watts, from its maker's runtime table (CATALOGUE[m]["runtime"]: [(W, min)]),
    interpolated on log-log axes; beyond the table's light end, scaled as 1/W from its lightest point (conservative:
    a battery delivers more of its energy at a light load). Beyond its rating: 0."""
    if w > m["w"] + 1e-6:
        return 0.0
    pts = sorted(m["runtime"])
    if w <= pts[0][0]:
        return pts[0][1] * pts[0][0] / max(w, 1.0)
    for (w0, t0), (w1, t1) in zip(pts[:-1], pts[1:]):
        if w0 <= w <= w1:
            a = (math.log(w) - math.log(w0)) / (math.log(w1) - math.log(w0))
            return math.exp(math.log(t0) + a * (math.log(t1) - math.log(t0)))
    (w0, t0), (w1, t1) = pts[-2], pts[-1]       # past the last point, up to the rating: extrapolate the last segment
    a = (math.log(w) - math.log(w0)) / (math.log(w1) - math.log(w0))
    return math.exp(math.log(t0) + a * (math.log(t1) - math.log(t0)))


def delivered_wh(m: dict) -> float:
    """The most energy unit m's runtime table shows it delivering, Wh (its lightest-load point, as a rule: a battery
    gives up more of its charge slowly)."""
    return max(w * t / 60.0 for w, t in m["runtime"])


def eff_at(m: dict, w: float) -> float:
    """Unit m's efficiency on mains carrying w watts: its published curve (CATALOGUE[m]["eff"]: [(load fraction,
    efficiency)]) interpolated, held flat beyond its ends."""
    eff = sorted(m.get("eff", [(1.0, 0.95)]))
    frac = w / m["w"]
    return float(np.interp(frac, [a for a, _ in eff], [b for _, b in eff]))


def loss_w(m: dict, w: float) -> float:
    """The unit's own loss carrying w watts on mains, W: its no-load input (CATALOGUE[m]["idle_w"]) at 0 W, then
    P (1/efficiency - 1) at each of ENERGY STAR's tested loads (25, 50, 75, 100 %), interpolated linearly between
    them. An online unit's loss is mostly its no-load input at the light loads of most trays."""
    pts = [(0.0, m.get("idle_w", 0.0))] + [(f * m["w"], f * m["w"] * (1.0 / e - 1.0)) for f, e in sorted(m["eff"])]
    return float(np.interp(w, [a for a, _ in pts], [b for _, b in pts]))


def tray_load(k: str) -> dict:
    """The tray's backed and unbacked branches from TRAY_LOADS: rated (what the UPS must be able to carry) and typical
    (what it carries in a transit, for its runtime), W."""
    rows = TRAY_LOADS[k]
    backed = [r for r in rows if r["backed"]]
    unbacked = [r for r in rows if not r["backed"]]
    return dict(backed_rated_w=round(sum(r["rated_w"] for r in backed)),
                backed_typical_w=round(sum(r["typical_w"] for r in backed)),
                unbacked_rated_w=round(sum(r["rated_w"] for r in unbacked)),
                connected_w=round(sum(r["rated_w"] for r in rows)),
                estimated_share=round(sum(r["typical_w"] for r in backed if r["kind"] == "estimate") /
                                      max(1.0, sum(r["typical_w"] for r in backed)), 2))


def choose(k: str, family: str | None = None) -> tuple:
    """(model key, why) for tray k: the smallest unit of the family (CATALOGUE order, smallest first) that carries the
    backed branch's rated draw and runs RUNTIME_MIN minutes at its typical draw."""
    ld = tray_load(k)
    fam = family or FAMILY
    for key in FAMILIES[fam]:
        m = CATALOGUE[key]
        if k in ONLINE_ONLY and not m["topology"].startswith("online"):
            continue
        if m["w"] >= ld["backed_rated_w"] and runtime_min(m, ld["backed_typical_w"]) >= RUNTIME_MIN:
            return key, (f"{m['w']:.0f} W covers the backed branch's {ld['backed_rated_w']} W at its machines' ratings "
                         f"({100 * ld['backed_rated_w'] / m['w']:.0f} %); {runtime_min(m, ld['backed_typical_w']):.0f} "
                         f"min at its typical {ld['backed_typical_w']} W"
                         + ("; online, as the tray holds a PC, a vacuum or a measurement" if k in ONLINE_ONLY else
                            "; line-interactive is enough: nothing on the branch minds a 4-6 ms transfer"))
    raise ValueError(f"tray {k}: nothing in {fam} carries {ld}")


def assignment() -> dict:
    """{tray: model key}: ASSIGN where it says, else choose()."""
    return {k: ASSIGN.get(k) or choose(k)[0] for k in TRAY_LOADS}


def unit_of(k: str) -> dict | None:
    """The catalogue entry of tray k's unit, or None for a passive tray."""
    if k not in TRAY_LOADS:
        return None
    return CATALOGUE[assignment()[k]]


def placement(k: str) -> tuple:
    """(x of the back face, y of the centre line, z of the foot), tray frame, for tray k's unit: the back at BACK_X, and
    the centre at Y_C unless that would put the unit's back side into the rim lines (RIM_LINES_Y - 8 mm), then forward."""
    m = unit_of(k)
    _, T, _ = tower_dims(m)
    yc = min(Y_C, RIM_LINES_Y - 8.0 - 3.0 - T / 2)      # 3 mm for the cradle's angle
    return BACK_X, yc, T_FLOOR


_BOX: dict = {}


def box_on_tray(k: str) -> tuple:
    """(x0, x1, y0, y1, z0, z1) of tray k's unit with its cradle, straps and input cord, tray frame: measured from
    the parts (parts_on_tray), once per tray and unit."""
    key = (k, assignment()[k])
    if key not in _BOX:
        import cadquery as cq
        bb = cq.Compound.makeCompound([s for s, _ in parts_on_tray(k).values()]).BoundingBox()
        _BOX[key] = (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)
    return _BOX[key]


def parts_on_tray(k: str) -> dict:
    """{name: (shape, material)} of tray k's unit and its cradle, tray frame."""
    import cadquery as cq
    m = unit_of(k)
    bx, yc, z0 = placement(k)
    loc = cq.Location(cq.Vector(bx, yc, z0))
    out = {}
    for n, (s, mat) in {**unit_parts(m), **cradle_parts(m), **cord_parts(k)}.items():
        if isinstance(s, cq.Workplane):
            vals = s.vals()
            s = vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals)
        out[f"UPS {n}"] = (s.moved(loc), mat)
    return out


SOCKET = (1025.0, 401.0, 73.0)     # tray frame: the top of the tray's distribution box ("tray k socket", vlm.tray)


def cord_parts(k: str) -> dict:
    """Tray k's unit's input cord, in its tower frame: from where it leaves the back (rear()["cord"]) out and down to
    the tray's distribution box at the back right corner, which takes the dock's mains and feeds the UPS and the
    unbacked branch's strip (notes/ups.md)."""
    from common import hose
    m = unit_of(k)
    D, T, H = tower_dims(m)
    bx, yc, z0 = placement(k)
    r = rear(m) if m.get("family") else m.get("rear", {})
    cy, cz = r.get("cord", (0.0, 130.0))
    sx, sy, sz = SOCKET[0] - bx, SOCKET[1] - yc, SOCKET[2] - z0
    pts = [(14.0, cy, cz), (52.0, cy, cz), (52.0, cy, sz + 40.0), (52.0, sy, sz + 40.0), (sx + 20.0, sy, sz + 40.0),
           (sx + 20.0, sy, sz - 2.0)]
    return {"input cord": (hose(pts, 11.0), "ups_outlet")}


def display_point(k: str) -> tuple:
    """(x, y, z) of the middle of tray k's unit's display, tray frame: where a label about its state points."""
    m = unit_of(k)
    D, T, H = tower_dims(m)
    bx, yc, z0 = placement(k)
    f = face(m) if m.get("family") else m.get("face", {})
    (u0, u1), (v0, v1) = f.get("lcd", ((H - 60.0, H - 20.0), (T * 0.3, T * 0.7)))
    return (bx - D - 2.0, yc + (v0 + v1) / 2 - T / 2, z0 + (u0 + u1) / 2)


def _text(s: str, h: float, R, at) -> "pv.PolyData":
    """3-D text `s`, letters h mm tall, turned by R (columns: where the text's x, y and depth go) and moved to `at`
    (the text's bottom left)."""
    import pyvista as pv
    t = pv.Text3D(s, depth=0.6)
    b = t.bounds
    t = t.translate((-b[0], -b[2], -b[4]), inplace=False).scale(h / max(b[3] - b[2], 1e-6), inplace=False)
    pts = np.asarray(t.points) @ np.asarray(R, float).T + np.asarray(at, float)
    t.points = pts
    return t


FRONT = ((0, -1, 0), (0, 0, 1), (-1, 0, 0))     # text on a face looking -x: reads along -y, up +z, out of the face
SIDE = ((1, 0, 0), (0, 0, 1), (0, -1, 0))        # on the side looking -y: reads along +x, up +z


FRONT_UP = ((0, 0, 1), (0, 1, 0), (-1, 0, 0))     # on the front, reading up the standing unit (as in its rack)
LOGO_RGB = {"white": (0.95, 0.95, 0.93), "red": (0.82, 0.10, 0.12), "blue": (0.10, 0.36, 0.72),
            "grey": (0.55, 0.56, 0.58), "black": (0.05, 0.05, 0.05)}


def markings(m: dict, tag: str | None = None) -> list:
    """Unit m's markings in its tower frame, [(PolyData, rgb)]: its logos and model name as the maker prints them on
    its front (CATALOGUE[m]["face"]["logos"]: text, u, v, letter height, colour, in rack-face mm) and, with a tag, an
    asset label on its side towards the front of the tray ("UPS A  <model>", "<VA> VA / <W> W, <chemistry>"), as a
    lab would put on it."""
    D, T, H = tower_dims(m)
    f = face(m) if m.get("family") else m.get("face", {})
    out = []
    for text, u, v, h, colour in f.get("logos", [(m["maker"].upper(), 20.0, T / 2 - 5.0, 10.0, "white")]):
        y, z = _yz(m, u, v)
        t = _text(text, h, np.array(FRONT_UP, float).T, (-D - 2.0, y, z))
        out.append((t.triangulate(), LOGO_RGB.get(colour, colour)))
    if tag:
        R = np.array(SIDE, float).T
        a = _text(f"UPS {tag}   {m['maker']} {m['model']}", 12.0, R, (-D + 30.0, -T / 2 - 0.7, H - 36.0))
        b = _text(f"{m['va']} VA / {m['w']} W, {m['chem_short']}", 9.5, R, (-D + 30.0, -T / 2 - 0.7, H - 56.0))
        out.append((a.merge(b).triangulate(), LOGO_RGB["white"]))
    return out


def marking_mesh(k: str) -> list:
    """Tray k's unit's markings (markings), tray frame: [(PolyData, rgb)]."""
    out = []
    for mesh, rgb in markings(unit_of(k), tag=k):
        mesh.points = np.asarray(mesh.points) + np.asarray(placement(k), float)
        out.append((mesh, rgb))
    return out


# ===================================================================================================== on its own
def instrument(key: str):
    """Catalogue entry `key` as an instruments.Instrument, for a still or the tour: its origin at the centre of its
    footprint and its front to -y (turned from the tower frame), with its cradle."""
    import cadquery as cq
    import instruments as I
    m = CATALOGUE[key]
    D, T, H = tower_dims(m)
    inst = I.Instrument(f"ups_{key}", "UPS", f"{m['maker']} {m['model']}", (T, D, H), m.get("source", ""))
    loc = cq.Location(cq.Vector(0, D / 2, 0)) * cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 90)
    body = I._piece(inst, "body")
    for n, (s, mat) in {**unit_parts(m), **cradle_parts(m)}.items():
        if isinstance(s, cq.Workplane):
            vals = s.vals()
            s = vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals)
        body.add(n, s.moved(loc), mat)
    inst.meshes["body"] = []
    for mk, rgb in markings(m):
        P = np.asarray(mk.points)
        mk.points = np.c_[-P[:, 1], P[:, 0] + D / 2, P[:, 2]]
        inst.meshes["body"].append((mk, rgb, 1.0))
    inst.cam = (-0.9, -1.5, 0.7)
    return inst


def _entries(inst):
    import tour
    import instruments as I
    tour.MATS.update(I.MATERIALS)
    tour.MATS.update(MATERIALS)
    return tour.piece_entries(inst)


def _studio_scene(name, size=(1600, 900)):
    from scene import Scene
    import tour
    sc = Scene(name, name, size=size, gif=False, mp4=False)
    tour.studio(sc, size=60000.0)
    return sc


def still(keys=None) -> list:
    """Each unit on its own, from its front left and from its back right -> /tmp/ups_<key>.png."""
    from PIL import Image
    import tour
    out = []
    for key in keys or list(CATALOGUE):
        inst = instrument(key)
        sc = _studio_scene(f"ups_{key}", size=(960, 720))
        tour.Rig(sc, inst, _entries(inst), f"{key}:")
        bb = inst.bbox()
        tour.contact_shadow(sc, bb)
        shots = []
        for d in ((-0.9, -1.5, 0.7), (1.2, 1.4, 0.6)):
            sc.cam = tour.frame_cam(bb, d, pad=0.9, look_z=0.5)
            shots.append(sc.render_base())
        sc.pl.close()
        sheet = Image.new("RGB", (960 * len(shots), 720), "white")
        for i, im in enumerate(shots):
            sheet.paste(Image.fromarray(im), (i * 960, 0))
        path = f"/tmp/ups_{key}.png"
        sheet.save(path)
        out.append(path)
        print(key, path, flush=True)
    return out


# ===================================================================================================== the record
def summary() -> dict:
    """Everything out/ups.json holds: the rule, the catalogue, and per tray its loads, its unit and the margins."""
    trays = {}
    for k in TRAY_LOADS:
        ld = tray_load(k)
        key = assignment()[k]
        m = CATALOGUE[key]
        t = ld["backed_typical_w"]
        trays[k] = dict(
            slot=SLOT[k], shuttle=SHUTTLE[k], ups=key, model=f"{m['maker']} {m['model']}", **ld,
            ups_w=m["w"], ups_va=m["va"], load_pct_rated=round(100 * ld["backed_rated_w"] / m["w"]),
            load_pct_typical=round(100 * t / m["w"]),
            runtime_min_typical=round(runtime_min(m, t), 1), runtime_min_rated=round(runtime_min(m, ld["backed_rated_w"]), 1),
            transit_battery_wh=round(t * TRANSIT_S / 3600.0, 2),
            transits_per_charge=int(runtime_min(m, t) * 60 / TRANSIT_S),
            ups_loss_w=round(loss_w(m, t), 1), efficiency=round(eff_at(m, t), 3),
            mass_kg=m["kg"], box_on_tray_mm=[round(v) for v in box_on_tray(k)],
            why=choose(k)[1] if k not in ASSIGN else ASSIGN_WHY.get(k, "assigned"),
            items=TRAY_LOADS[k])
    used = sorted(set(assignment().values()), key=lambda key: CATALOGUE[key]["w"])
    return dict(
        what="each powered tray's UPS, sized for what it must keep alive (ups.py)", rule=RULE,
        runtime_target_min=RUNTIME_MIN, transit_s=TRANSIT_S, family=FAMILY,
        used={key: dict(trays=[k for k, v in assignment().items() if v == key], **{
            f: CATALOGUE[key].get(f) for f in ("maker", "model", "topology", "chemistry", "va", "w", "tower_mm", "kg",
                                               "eff", "runtime", "transfer_ms", "battery_life_y", "outlets_text",
                                               "plug", "price_usd", "sources")}) for key in used},
        trays=trays,
        catalogue={key: {f: v for f, v in m.items() if f not in ("face", "rear")} for key, m in CATALOGUE.items()},
        totals=dict(ups_mass_kg=round(sum(t["mass_kg"] for t in trays.values()), 1),
                    ups_loss_w=round(sum(t["ups_loss_w"] for t in trays.values())),
                    backed_typical_w=sum(t["backed_typical_w"] for t in trays.values()),
                    unbacked_rated_w=sum(t["unbacked_rated_w"] for t in trays.values())))


def write_json() -> dict:
    s = summary()
    OUT.mkdir(exist_ok=True)
    (OUT / "ups.json").write_text(json.dumps(s, indent=1) + "\n")
    return s


def table(s: dict | None = None) -> str:
    s = s or summary()
    rows = ["tray slot  backed rated/typical W  unbacked W  UPS                         W     load%  min@typ  loss W  kg"]
    for k, t in s["trays"].items():
        rows.append(f"{k:4s} {t['slot']:4s}  {t['backed_rated_w']:6d} / {t['backed_typical_w']:<6d}       "
                    f"{t['unbacked_rated_w']:6d}   {t['model']:27s} {t['ups_w']:5d}  {t['load_pct_typical']:4d}  "
                    f"{t['runtime_min_typical']:7.1f}  {t['ups_loss_w']:6.1f}  {t['mass_kg']:4.1f}")
    return "\n".join(rows)


# ===================================================================================================== figures
INK, INK2, SURF, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]      # the dataviz reference palette, slots 1-4, in order


def _colours() -> dict:
    """{model key: colour}, the units in use from smallest to largest in the palette's fixed order."""
    used = sorted(set(assignment().values()), key=lambda key: CATALOGUE[key]["w"])
    return {key: SERIES[i % len(SERIES)] for i, key in enumerate(used)}


def figure() -> str:
    """out/ups_sizing.png: per tray, the backed branch (rated and typical) against its unit's rating, and the unit's
    runtime at the typical draw against the 10-minute target and the transit."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    s = summary()
    col = _colours()
    order = [k for k in ("A", "B", "C", "D", "E", "F", "K", "L", "M", "H", "G", "I") if k in s["trays"]]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 7.2), gridspec_kw=dict(width_ratios=[1.55, 1.0]),
                                   facecolor=SURF)
    for ax in (ax1, ax2):
        ax.set_facecolor(SURF)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GRID)
        ax.tick_params(colors=INK2, labelsize=9)
        ax.grid(axis="x", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
    ys = np.arange(len(order))[::-1]
    for y, k in zip(ys, order):
        t = s["trays"][k]
        c = col[t["ups"]]
        ax1.barh(y, t["backed_rated_w"], height=0.56, color=c, alpha=0.35, lw=0)
        ax1.barh(y, t["backed_typical_w"], height=0.56, color=c, lw=0)
        ax1.plot([t["ups_w"]] * 2, [y - 0.38, y + 0.38], color=INK, lw=2.0, solid_capstyle="butt")
        ax1.text(t["ups_w"] + 30, y, f"{CATALOGUE[t['ups']]['short']}, {t['ups_w']} W", va="center", ha="left",
                 fontsize=8.5, color=INK)
        ax2.plot([t["runtime_min_typical"]], [y], "o", ms=8, color=c, mec=SURF, mew=2)
        ax2.text(t["runtime_min_typical"] * 1.12, y, f"{t['runtime_min_typical']:.0f} min", va="center",
                 fontsize=8.5, color=INK2)
    labels = [f"{k}  ({s['trays'][k]['slot']})" for k in order]
    ax1.set_yticks(ys, labels)
    ax2.set_yticks(ys, [""] * len(ys))
    ax1.set_xlabel("watts on the tray's backed branch (pale: rated, solid: typical); black tick: the UPS's rating",
                   color=INK2, fontsize=9)
    xmax = max(t["ups_w"] for t in s["trays"].values())
    ax1.set_xlim(0, xmax * 1.42)
    ax2.set_xscale("log")
    lo = 0.08
    hi = max(t["runtime_min_typical"] for t in s["trays"].values()) * 2.2
    ax2.set_xlim(lo, hi)
    ax2.axvline(RUNTIME_MIN, color=INK2, lw=1.2, ls=(0, (4, 3)))
    ax2.text(RUNTIME_MIN * 1.06, ys[0] + 0.62, f"target: {RUNTIME_MIN:.0f} min", fontsize=8.5, color=INK2)
    ax2.axvline(TRANSIT_S / 60.0, color=INK2, lw=1.2, ls=(0, (1, 2)))
    ax2.text(TRANSIT_S / 60.0 * 1.08, ys[0] + 0.62, f"a transit: {TRANSIT_S:.0f} s", fontsize=8.5, color=INK2)
    ax2.set_xlabel("minutes on battery at the typical draw (log scale; below a maker's lightest published load, "
                   "scaled as 1/W, which understates it)", color=INK2, fontsize=8.5)
    for ax in (ax1, ax2):
        ax.set_ylim(-0.7, len(order) - 0.1)
    ax1.axhline(ys[order.index("F")] - 0.5, color=GRID, lw=1.0) if "F" in order and "K" in order else None
    handles = [plt.Line2D([], [], marker="s", ls="", ms=10, color=c,
                          label=f"{CATALOGUE[key]['maker']} {CATALOGUE[key]['model']}, "
                                f"{CATALOGUE[key]['va']} VA / {CATALOGUE[key]['w']} W, "
                                f"{CATALOGUE[key]['topology']}, {CATALOGUE[key]['chem_short']}")
               for key, c in col.items()]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, fontsize=9, labelcolor=INK)
    fig.suptitle("Each powered tray's UPS, sized for what the tray must keep alive", x=0.06, ha="left", fontsize=13,
                 color=INK, fontweight="bold")
    fig.text(0.06, 0.925, "Shuttle 1: trays A-F; Shuttle 2: K, L, M, H, G, I. The unbacked branch (heaters, big "
             "motors) comes straight from the dock and pauses in transit.", fontsize=9.5, color=INK2, ha="left")
    fig.subplots_adjust(left=0.07, right=0.98, top=0.88, bottom=0.17, wspace=0.05)
    path = OUT / "ups_sizing.png"
    fig.savefig(path, dpi=110, facecolor=SURF)
    plt.close(fig)
    return str(path)


def lineup() -> str:
    """out/ups_lineup.png: the units the trays use, side by side and to scale, from the front and from the back, each
    captioned with its figures and the trays it serves."""
    from PIL import Image, ImageDraw
    import tour
    from scene import font
    s = summary()
    used = list(s["used"])
    insts = [instrument(key) for key in used]
    sc = _studio_scene("ups_lineup", size=(1920, 1080))
    x = 0.0
    xs, bbs = [], []
    gap = 260.0
    for key, inst in zip(used, insts):
        bb = inst.bbox()
        w = bb[1] - bb[0]
        at = np.eye(4)
        at[0, 3] = x - bb[0]
        tour.Rig(sc, inst, _entries(inst), f"{key}:", at=at)
        bbs.append((x, x + w, bb[2], bb[3], bb[4], bb[5]))
        xs.append(x + w / 2)
        x += w + gap
    allbb = (min(b[0] for b in bbs), max(b[1] for b in bbs), min(b[2] for b in bbs), max(b[3] for b in bbs), 0.0,
             max(b[5] for b in bbs))
    for i, b in enumerate(bbs):
        tour.contact_shadow(sc, b, name=f"shadow {i}")
    shots = []
    for d in ((-0.55, -1.6, 0.55), (0.55, 1.6, 0.55)):
        sc.cam = tour.frame_cam(allbb, d, pad=0.70, look_z=0.40)
        sc.view_angle = 30.0
        shots.append((Image.fromarray(sc.render_base()), [sc.project((xx, (b[2] + b[3]) / 2, 0.0))
                                                          for xx, b in zip(xs, bbs)]))
    sc.pl.close()
    W, H = 1920, 1080
    cap_h = 200
    sheet = Image.new("RGB", (W, 70 + H // 2 + cap_h), SURF)
    d = ImageDraw.Draw(sheet)
    d.text((40, 18), "The trays' three UPSs, to scale, in their cradles: front (left) and back (right)",
           font=font(30, bold=True), fill=INK)
    for row, (im, _) in enumerate(shots):
        sheet.paste(im.resize((W // 2, H // 2)), (row * W // 2, 70))
    y0 = 70 + H // 2 + 14
    cw = W // len(used)
    for i, key in enumerate(used):
        m = CATALOGUE[key]
        u = s["used"][key]
        D, T, Hh = tower_dims(m)
        lines = [f"{m['maker']} {m['model']}", f"{m['va']} VA / {m['w']} W, {m['topology']}",
                 f"{m['chemistry']}", f"{Hh:.0f} x {T:.0f} x {D:.0f} mm standing, {m['kg']:.1f} kg",
                 f"trays {', '.join(u['trays'])}"]
        cx = i * cw + 30
        d.rectangle((cx, y0 + 4, cx + 14, y0 + 18), fill=_colours().get(key, INK))
        for j, t in enumerate(lines):
            d.text((cx + (22 if j == 0 else 0), y0 + j * 34), t, font=font(26 if j == 0 else 22, bold=j == 0),
                   fill=INK if j == 0 else INK2)
    path = OUT / "ups_lineup.png"
    sheet.save(path, optimize=True)
    return str(path)


def on_trays(trays=("D", "A", "F")) -> str:
    """out/ups_on_trays.png: Shuttle 1 (services.build_vlm) with each of `trays` presented at the opening in turn, one
    tray per unit type, the cladding see-through and the tray's own instruments faint, so its UPS shows: the unit, its
    cradle, its cord and its asset label."""
    from PIL import Image, ImageDraw
    import animate as A
    import lab
    import services as S
    import setup_lab
    import vlm as V
    from scene import font
    data, idata = lab.meshes(), setup_lab.tour_load_safe()
    sc, L, live = S.build_vlm("ups_on_trays", data, idata, "The trays' UPSs", mp4=False)
    L.skin(1.0)(1.0)
    L.lift_z = V.Z_OPEN
    shots = []
    for k in trays:
        for kk, pos in S.HOME.items():
            L.tray[kk] = list(V.SLOTS[pos])
            L.where[kk] = pos
        L.tray[k] = [V.Y_OPEN, V.Z_OPEN]
        L.where[k] = "open"
        S.set_dock(sc, "open", 0.0)
        S.set_dock(sc, S.HOME[k], 1.0)
        L.apply_state()
        eq = tuple(g.split(":")[0] + ":" for g in L.eq_groups.get(k, [])) + (f"eq_{k}", f"{k}_")
        S.ghost_prefix(sc, eq, 0.22)                     # every piece of the tray's instruments, doors and all
        x0, x1, y0, y1, z0, z1 = box_on_tray(k)
        tgt = A.tray_world(k, ((x0 + x1) / 2 - 60.0, (y0 + y1) / 2, (z0 + z1) / 2))
        sc.cam = [(tgt[0] - 1050.0, tgt[1] - 1650.0, tgt[2] + 760.0), tuple(tgt), (0, 0, 1)]
        sc.view_angle = 30.0
        shots.append((k, sc.render_base()))
        S.ghost_prefix(sc, eq, 1.0)
    sc.pl.close()
    w, h = 960, 540
    sheet = Image.new("RGB", (w * len(shots), h + 110), SURF)
    d = ImageDraw.Draw(sheet)
    for i, (k, im) in enumerate(shots):
        sheet.paste(Image.fromarray(im).resize((w, h)), (i * w, 0))
        m = unit_of(k)
        t = tray_load(k)
        d.text((i * w + 24, h + 14), f"Tray {k} ({SLOT[k]}): {m['maker']} {m['model']}", font=font(22, bold=True),
               fill=INK)
        d.text((i * w + 24, h + 50), f"{m['va']} VA / {m['w']} W, {m['topology']}; backed branch "
               f"{t['backed_typical_w']} W typical, {t['backed_rated_w']} W rated", font=font(18), fill=INK2)
    path = OUT / "ups_on_trays.png"
    sheet.save(path, optimize=True)
    return str(path)

# ===================================================================================================== data
# ---------------------------------------------------------------------------------------------------- the units
# Three units, one maker (Vertiv's Liebert), all lithium iron phosphate, all with Vertiv's IntelliSlot RDU120 network
# card (the "N" bundles), so one spares kit, one card and one piece of software serve all twelve trays. notes/ups.md
# has the 44 units compared (APC, Eaton, Vertiv) and why these. "runtime": the maker's figures, (W, minutes); where a
# datasheet and ENERGY STAR's certification database disagree, the lower is used for the sizing and both are kept.
# "eff": (load fraction, efficiency) on mains, ENERGY STAR's tested figures; "idle_w": its no-load input.
SRC = {
    "es": "ENERGY STAR certified UPS dataset (data.energystar.gov, resource ifxy-2uty, fetched 2026-11-18): efficiency "
          "at 25/50/75/100 % load, input at no load, runtime at 50 and 100 % load (the makers' own test submissions)",
    "gxt5li_gs": "Vertiv, Liebert GXT5 Lithium-Ion 1000-3000VA rack/tower guide specifications, REV0 04-2022 "
                 "(prep.vertiv.com/491871/globalassets/products/critical-power/uninterruptible-power-supplies-ups/"
                 "liebert--gxt5-lithium-ion-1000-3000va-rack-tower-guide-specifications.pdf, fetched)",
    "gxt5li_pp": "Vertiv product page GXT5LI-1500LVRT2UXL (vertiv.com, fetched): 18 kg, 476 mm deep, RDU120 card, "
                 "5-year warranty including the battery, 'up to 14 minutes at full load'",
    "psi5sd": "Vertiv product catalogue, Liebert PSI5 Lithium-Ion (vertiv.com/en-us/products-catalog/critical-power/"
              "uninterruptible-power-supplies-ups/vertiv-liebert-psi5-lithium-ion-ups/, fetched): PSI5-800SRT2ULI "
              "800 VA / 720 W, 2U short depth, 3.39 x 17.28 x 11.81 in, 18.5 lb; its family photo",
    "psi5_ds": "Vertiv, Liebert PSI5 Lithium-Ion UPS data sheet SL-70581 (42u.com copy, fetched) and short-depth "
               "data sheet SL-70889 Rev.1 02/2025 (vertiv.com, fetched): LiFePO4, 4-6 ms transfer, 5 years on UPS "
               "and battery, RDU120 bundles ('N'), 'up to 10 years' battery life, 'up to 10x more discharge cycles'",
    "photos": "front photos: vertiv.com GXT5LI-1500LVRT2UXL front (800 x 600) and the PSI5 Lithium-Ion short-depth "
              "family image (1000 x 1000), fetched 2026-11-18",
}
CATALOGUE = {
    # the trays that keep only cameras, the switch and light controllers alive (C, F, G, I), and B and H
    "psi5_800": dict(
        maker="Vertiv", model="Liebert PSI5-800SRT2ULIN", short="PSI5-800 Li", family="psi5sd",
        topology="line-interactive", chemistry="LiFePO4 lithium-ion", chem_short="LiFePO4", va=800, w=720,
        front_mm=(439.0, 86.0), depth_mm=300.0, kg=8.4, transfer_ms="4-6 typical",
        runtime=[(360, 16.0), (720, 8.0)], eff=[(0.25, 0.973), (0.50, 0.986), (0.75, 0.989), (1.0, 0.989)],
        idle_w=4.0, battery_life_y="up to 10 (Vertiv); 5-year warranty on UPS and battery",
        plug="NEMA 5-15P", outlets_text="NEMA 5-15R, some programmable (load shedding)", card="IntelliSlot RDU120",
        price_usd=None,
        notes=["Runtime: ENERGY STAR's 16 min at 50 % and 8 min at 100 % load.",
               "No-load input not published: 4 W assumed, as APC's line-interactive units of this size (3.6-5.3 W, "
               "ENERGY STAR)."],
        sources=[SRC["psi5sd"], SRC["es"], SRC["psi5_ds"], SRC["photos"]]),
    # the trays whose PCs and instruments must not see even a 4 ms transfer, thousands of times a year
    "gxt5li_1500": dict(
        maker="Vertiv", model="Liebert GXT5LI-1500LVRT2UXL", short="GXT5LI-1500", family="gxt5li",
        topology="online double conversion", chemistry="LiFePO4 lithium-ion", chem_short="LiFePO4", va=1500, w=1350,
        front_mm=(430.0, 85.0), depth_mm=476.0, kg=18.0, transfer_ms="0 (online)",
        runtime=[(675, 9.0), (1350, 3.0)], runtime_datasheet=[(675, 28.0), (1350, 14.0)],
        eff=[(0.25, 0.888), (0.50, 0.916), (0.75, 0.921), (1.0, 0.917)], idle_w=29.1,
        battery_life_y="5-year warranty including the battery (Vertiv product page)",
        plug="NEMA 5-15P", outlets_text="6 x NEMA 5-15R, 4 programmable (load shedding on battery)",
        card="IntelliSlot RDU120", price_usd=2707,
        notes=["Runtime for the sizing: ENERGY STAR's 9 min at 50 % and 3 min at 100 % load. Vertiv's guide gives "
               "14 min at full load and a retailer 28 min at half; the lower is used.",
               "Price: CDW, $2,706.99 (search snippet, undated)."],
        sources=[SRC["gxt5li_gs"], SRC["gxt5li_pp"], SRC["es"], SRC["photos"]]),
    # tray D: the SEM, its EDS, the MiniFlex and two PCs, about 2.5 kVA at their nameplates
    "gxt5li_3000": dict(
        maker="Vertiv", model="Liebert GXT5LI-3000LVRT2UXL", short="GXT5LI-3000", family="gxt5li",
        topology="online double conversion", chemistry="LiFePO4 lithium-ion", chem_short="LiFePO4", va=3000, w=2700,
        front_mm=(430.0, 85.0), depth_mm=546.0, kg=21.5, transfer_ms="0 (online)",
        runtime=[(1350, 9.0), (2700, 3.0)], runtime_datasheet=[(2700, 6.0)],
        eff=[(0.25, 0.913), (0.50, 0.927), (0.75, 0.924), (1.0, 0.916)], idle_w=39.7,
        battery_life_y="5-year warranty including the battery (Vertiv)",
        plug="NEMA L5-30P", outlets_text="6 x NEMA 5-15/20R and 1 x L5-30R, 4 programmable", card="IntelliSlot RDU120",
        price_usd=None,
        notes=["Runtime for the sizing: ENERGY STAR's 9 min at 50 % and 3 min at 100 % load (Vertiv's guide: 6 min "
               "at full load).", "Its L5-30P takes up to 22.5 A at 120 V: tray D's backed branch is all it feeds, "
               "inside the dock's 30 A."],
        sources=[SRC["gxt5li_gs"], SRC["es"], SRC["photos"]]),
}
FAMILIES = {"vertiv_li": ["psi5_800", "gxt5li_1500", "gxt5li_3000"]}
FAMILY = "vertiv_li"
# The line-interactive unit goes only where nothing on the backed branch minds a 4-6 ms transfer (ups.ONLINE_ONLY: the
# trays with a PC, a vacuum, a beam or a measurement in progress take an online unit whatever their load).
ONLINE_ONLY = {"A", "D", "E", "K", "L", "M"}
ASSIGN: dict = {}
ASSIGN_WHY: dict = {}

TRAY_LOADS = {      # tray: [row]; generated from the research in notes/ups.md (tray_power), cameras per tray as drawn
    'A': [
        dict(key='ot2', qty=1, backed=True, rated_w=220, typical_w=120, kind='published',
             what='Opentrons OT-2 liquid handler',
             cut='Its Raspberry Pi controller reboots, up to about 45 s or longer before it is ready. A protocol in progress is lost: Opentrons documents no power-loss resume for the OT-2, and its open-loop steppers have to home before the next run (estimate). Repeated hard cuts also risk its SD-card file system (estimate).',
             branch='UPS-backed', sources=['https://docs.opentrons.com/ot-2/system-description/specs/', 'https://docs.opentrons.com/ot-2/installation/requirements/', 'https://sandbox.docs.opentrons.com/docs-ot2-install-relocate/ot-2/installation/first-run']),
        dict(key='cubxl', qty=1, backed=True, rated_w=100, typical_w=30, kind='estimate',
             what='CubXL gantry on a Genmitsu PROVerXL 4030 frame (custom), Arduino Uno R3 + CH340 board',
             cut='The controller resets and the open-loop steppers lose position, so it homes again after every cut. The electromagnetic capper drops whatever it holds when unpowered (estimates).',
             branch='UPS-backed', sources=['https://manuals.plus/genmitsu/4030-v1-proverxl-spindle-set-manual', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/CLAUDE.md?plain=1#L233']),
        dict(key='ezstat', qty=1, backed=True, rated_w=30, typical_w=10, kind='estimate',
             what='NuVant EZstat Pro potentiostat/galvanostat',
             cut='A measurement in progress (OCP, LPR, CV) stops and leaves the cell at open circuit; EZware loses the instrument and the run has to be started again (estimate).',
             branch='UPS-backed', sources=['https://www.environmental-expert.com/products/potentiostat-galvanostat-1085908']),
        dict(key='ezware_pc', qty=1, backed=True, rated_w=150, typical_w=40, kind='estimate',
             what='Windows 7 PC that runs EZware for the EZstat Pro (if it rides on the tray)',
             cut='Unclean Windows shutdown and a reboot of about 2 min; EZware and any Remote Desktop session drop (estimate).',
             branch='UPS-backed', sources=['https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/CLAUDE.md?plain=1#L233']),
        dict(key='cubxl_pi', qty=1, backed=True, rated_w=27, typical_w=5, kind='published',
             what="the CubXL's own Raspberry Pi 5 (serial to the Arduino and CH340)",
             cut="Reboots in about 30 s; the CubXL's serial sessions drop (estimate).",
             branch='UPS-backed', sources=['https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/CLAUDE.md?plain=1#L233']),
        dict(key='pi_unit', qty=2, backed=True, rated_w=54, typical_w=8, kind='published',
             what='Raspberry Pi 5 camera unit (Pi 5 4 GB, Active Cooler, HQ Camera and Camera Module 3 Wide), x2',
             cut='Reboots in about 30 s and the stream drops; repeated hard cuts put the SD card at risk (estimate).',
             branch='UPS-backed', sources=['https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='poe_switch', qty=1, backed=True, rated_w=60, typical_w=8, kind='published',
             what='Small managed PoE+ switch, e.g. Ubiquiti USW-Lite-8-PoE (8 ports, 4 PoE+)',
             cut='Every device on the tray loses its network link; the switch takes about a minute to boot (estimate).',
             branch='UPS-backed', sources=['https://techspecs.ui.com/unifi/switching/usw-lite-8-poe']),
    ],
    'B': [
        dict(key='carousel', qty=1, backed=True, rated_w=395, typical_w=25, kind='published',
             what='powder-doser multi-doser, chain carousel v5 (powder-doser PR #185)',
             cut="The Pi reboots; the closed-loop driver loses its encoder count, so the carousel homes again; unpowered, the NEMA 34 has only detent torque, so an unbalanced chain could creep during the lift's accelerations; the P16s (potentiometer feedback) know their position on power-up; a dose in progress is lost (all estimates).",
             branch='UPS-backed', sources=['https://www.meanwell.com/Upload/PDF/LRS-350/LRS-350-SPEC.PDF', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/multidoser/chain-carousel-v5/layout.py#L717-L725', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='balance', qty=1, backed=True, rated_w=11, typical_w=11, kind='published',
             what='A&D HR-202i analytical balance (220 g x 0.1 mg; 51 g x 0.01 mg)',
             cut='Weighing stops. It returns in standby with its settings kept (non-volatile memory), but A&D asks for at least 1 h of warm-up before precision weighing, so every cut costs an hour.',
             branch='UPS-backed', sources=['https://www.aandd.jp/products/manual/balances/hr-i.pdf']),
        dict(key='vacuum_press', qty=1, backed=False, rated_w=400, typical_w=0, kind='estimate',
             what='Specac Atlas Autotouch 15T automatic hydraulic press (GS2581X)',
             cut='A program aborts. Whether the ram holds or bleeds its load, and whether the press switches itself back on, are not published (estimate). Never move the tray with a program running.',
             branch='unbacked branch (if it restarts by itself; otherwise back its ~15 W controller)', sources=['https://specac.com/product/autotouch-press-high-throughput-xrf-press/']),
        dict(key='vacuum_pump', qty=1, backed=False, rated_w=550, typical_w=0, kind='published',
             what='Edwards RV3 two-stage rotary-vane pump for the evacuable die (vacuum_press.md)',
             cut='The pump stops and its inlet valve closes fast, so no oil sucks back; the die stays under vacuum only if V1 is shut. It restarts on its own switch when power returns (estimate).',
             branch='unbacked branch', sources=['https://www.ajvs.com/library/Edwards_RV_Series_Brochure.pdf', 'https://www.manualslib.com/manual/2427823/Edwards-Rv3.html?page=22', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/notes/vacuum_press.md?plain=1#L87-L88']),
        dict(key='pi_unit', qty=1, backed=True, rated_w=27, typical_w=4, kind='published',
             what='Raspberry Pi 5 camera unit (Pi 5 4 GB, Active Cooler, HQ Camera and Camera Module 3 Wide), x1',
             cut='Reboots in about 30 s and the stream drops; repeated hard cuts put the SD card at risk (estimate).',
             branch='UPS-backed', sources=['https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='poe_switch', qty=1, backed=True, rated_w=60, typical_w=8, kind='published',
             what='Small managed PoE+ switch, e.g. Ubiquiti USW-Lite-8-PoE (8 ports, 4 PoE+)',
             cut='Every device on the tray loses its network link; the switch takes about a minute to boot (estimate).',
             branch='UPS-backed', sources=['https://techspecs.ui.com/unifi/switching/usw-lite-8-poe']),
    ],
    'C': [
        dict(key='h2d', qty=1, backed=False, rated_w=1320, typical_w=0, kind='published',
             what='Bambu Lab H2D',
             cut='An idle printer simply reboots (about a minute; estimate). A print in progress is offered for power-loss recovery (supported), but bed and chamber cool meanwhile and owners report mixed results.',
             branch='unbacked branch', sources=['https://materialpro3d.cz/user/related_files/h2d_spec.pdf', 'https://forum.bambulab.com/t/why-does-the-h2d-have-such-high-standby-power-consumption/172758', 'https://forum.bambulab.com/t/powerloss-recovery-issues/258431']),
        dict(key='a1mini', qty=1, backed=False, rated_w=150, typical_w=0, kind='published',
             what='Bambu Lab A1 mini',
             cut='Reboots; power-loss recovery is supported for a print in progress.',
             branch='unbacked branch (cheap to back instead: 6 W in transit, 150 W docked)', sources=['https://www.3dprintergear.com.au/assets/files/A1%20Mini%20TDS.pdf', 'https://wiki.bambulab.com/en/a1-mini/manual/faq']),
        dict(key='pi_unit', qty=2, backed=True, rated_w=54, typical_w=8, kind='published',
             what='Raspberry Pi 5 camera unit (Pi 5 4 GB, Active Cooler, HQ Camera and Camera Module 3 Wide), x2',
             cut='Reboots in about 30 s and the stream drops; repeated hard cuts put the SD card at risk (estimate).',
             branch='UPS-backed', sources=['https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='poe_switch', qty=1, backed=True, rated_w=60, typical_w=8, kind='published',
             what='Small managed PoE+ switch, e.g. Ubiquiti USW-Lite-8-PoE (8 ports, 4 PoE+)',
             cut='Every device on the tray loses its network link; the switch takes about a minute to boot (estimate).',
             branch='UPS-backed', sources=['https://techspecs.ui.com/unifi/switching/usw-lite-8-poe']),
    ],
    'D': [
        dict(key='sem', qty=1, backed=True, rated_w=500, typical_w=200, kind='published',
             what='Hitachi TM4000PlusII tabletop SEM, main unit',
             cut="The turbo (67 L/s) and diaphragm (20 L/min) pumps stop, the beam and high voltage drop, and the chamber leaks up as the turbo coasts down. After power returns it needs a full pump-down and turbo spin-up (Hitachi: an image within several minutes of start) and the tungsten filament is heated again. Whether it restarts without a button press isn't published (estimate).",
             branch='UPS-backed (evacuated standby, beam off)', sources=['https://hte.hitachi-hightech.com/hubfs/Product%20Page%20-%20TM4000/Hitachi_TM4000_Series_III_Brochure.pdf?hsLang=en', 'https://matcl.umd.edu/files/2022/06/TM400PlusII-2.pdf', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='sem_pc', qty=1, backed=True, rated_w=200, typical_w=60, kind='estimate',
             what="the SEM's PC and monitor (Hitachi-supplied)",
             cut='Unclean Windows shutdown, a reboot of about 2 min, the SEM software reconnects (estimate).',
             branch='UPS-backed', sources=['https://hte.hitachi-hightech.com/hubfs/Product%20Page%20-%20TM4000/Hitachi_TM4000_Series_III_Brochure.pdf?hsLang=en']),
        dict(key='eds', qty=1, backed=True, rated_w=400, typical_w=60, kind='published',
             what='Oxford Instruments AZtecOne EDS for the TM4000 (analyser unit and 30 mm² SDD)',
             cut="The SDD's two-stage thermoelectric cooler stops; it cools again 'on demand' (a few minutes; estimate) before analysis, and the analyser and its software restart.",
             branch='UPS-backed', sources=['https://matcl.umd.edu/files/2022/06/TM400PlusII-2.pdf']),
        dict(key='xrd', qty=1, backed=True, rated_w=1100, typical_w=150, kind='published',
             what='Rigaku MiniFlex (6th generation), 600 W tube',
             cut='High voltage drops (safe); the goniometer and software re-initialise; on restart the tube is aged back up to 40 kV/15 mA (7.5 min in one university SOP), and it trips if the cooling water stops. Its front has separate on and off buttons, so after a cut it probably stays off until someone presses on (estimate).',
             branch='UPS-backed (X-rays off)', sources=['https://resources.rigaku.com/hubfs/2024%20Rigaku%20Global%20Site/Resource%20Hub/Knowledge%20Library/Brochures/BR_23_MiniFlex_Rev0723_226325528_SinglePgs_low-res.pdf?hsLang=en', 'https://www.depts.ttu.edu/coe/research/mcc/brochures/MiniFlex6G.pdf', 'https://answers.uillinois.edu/97837']),
        dict(key='xrd_pc', qty=1, backed=True, rated_w=200, typical_w=50, kind='published',
             what="the MiniFlex's PC (SmartLab Studio II)",
             cut='Unclean shutdown and reboot; the instrument reconnects (estimate).',
             branch='UPS-backed', sources=['https://resources.rigaku.com/hubfs/2024%20Rigaku%20Global%20Site/Resource%20Hub/Knowledge%20Library/Brochures/BR_23_MiniFlex_Rev0723_226325528_SinglePgs_low-res.pdf?hsLang=en']),
        dict(key='pi_unit', qty=3, backed=True, rated_w=81, typical_w=12, kind='published',
             what='Raspberry Pi 5 camera unit (Pi 5 4 GB, Active Cooler, HQ Camera and Camera Module 3 Wide), x3',
             cut='Reboots in about 30 s and the stream drops; repeated hard cuts put the SD card at risk (estimate).',
             branch='UPS-backed', sources=['https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='poe_switch', qty=1, backed=True, rated_w=60, typical_w=8, kind='published',
             what='Small managed PoE+ switch, e.g. Ubiquiti USW-Lite-8-PoE (8 ports, 4 PoE+)',
             cut='Every device on the tray loses its network link; the switch takes about a minute to boot (estimate).',
             branch='UPS-backed', sources=['https://techspecs.ui.com/unifi/switching/usw-lite-8-poe']),
    ],
    'E': [
        dict(key='pip', qty=1, backed=True, rated_w=200, typical_w=80, kind='estimate',
             what='Plastometrex PLX-Benchtop indentation plastometer, with its PC',
             cut='An indent or profilometer scan in progress is lost; the indenter drive and stage home again (estimate). No warm-up is published.',
             branch='UPS-backed', sources=['https://plastometrex.com/products/plx-benchtop', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='nanoindenter', qty=1, backed=True, rated_w=300, typical_w=120, kind='estimate',
             what='KLA iMicro nanoindenter (InQuest controller and isolation gantry in the enclosure), with its PC',
             cut='Controller and PC restart and a test is lost. Worse, the electronics inside the enclosure are a heat source: a cut changes its thermal balance and drift then takes hours to settle. KLA publishes no settling time; nanoindenters generally need a stabilisation period (estimate).',
             branch='UPS-backed', sources=['https://www.kla.com/products/instruments/nanoindenters/imicro', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146', 'https://arxiv.org/pdf/1709.07714']),
        dict(key='mastersizer', qty=1, backed=True, rated_w=200, typical_w=65, kind='published',
             what='Malvern Mastersizer 3000 optical bench with the Aero S dry disperser',
             cut='The He-Ne laser goes off, and Malvern asks for 30 min after power-on for it to stabilise before a measurement; the Aero S and the software reconnect.',
             branch='UPS-backed', sources=['https://www.malvernpanalytical.com/br/assets/MRK1872-07-EN_MS3000_Broch_BrandUpdate_LR_web_tcm55-17232.pdf', 'https://ougfc.montana.edu/eal-lres/documents/Mastersizer-3000-user-manual-English-MAN0474-2-1.pdf', 'https://brand.malvernpanalytical.com/prototype/product']),
        dict(key='mastersizer_pc', qty=1, backed=True, rated_w=150, typical_w=40, kind='estimate',
             what="the Mastersizer's PC",
             cut='Unclean shutdown and reboot; the software reconnects (estimate).',
             branch='UPS-backed', sources=['https://www.malvernpanalytical.com/br/assets/MRK1872-07-EN_MS3000_Broch_BrandUpdate_LR_web_tcm55-17232.pdf']),
        dict(key='ms_extractor', qty=1, backed=False, rated_w=1200, typical_w=0, kind='estimate',
             what="the Aero S vacuum extractor (Malvern's 'vacuum unit'; model not named)",
             cut='Stops. It only runs during a measurement.',
             branch='unbacked branch', sources=['https://ougfc.montana.edu/eal-lres/documents/Mastersizer-3000-user-manual-English-MAN0474-2-1.pdf']),
        dict(key='pi_unit', qty=3, backed=True, rated_w=81, typical_w=12, kind='published',
             what='Raspberry Pi 5 camera unit (Pi 5 4 GB, Active Cooler, HQ Camera and Camera Module 3 Wide), x3',
             cut='Reboots in about 30 s and the stream drops; repeated hard cuts put the SD card at risk (estimate).',
             branch='UPS-backed', sources=['https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='poe_switch', qty=1, backed=True, rated_w=60, typical_w=8, kind='published',
             what='Small managed PoE+ switch, e.g. Ubiquiti USW-Lite-8-PoE (8 ports, 4 PoE+)',
             cut='Every device on the tray loses its network link; the switch takes about a minute to boot (estimate).',
             branch='UPS-backed', sources=['https://techspecs.ui.com/unifi/switching/usw-lite-8-poe']),
    ],
    'F': [
        dict(key='polisher', qty=1, backed=False, rated_w=740, typical_w=0, kind='snippet',
             what='LECO PX500 semi-automatic grinder/polisher',
             cut='Wheel and head stop and the program ends; the water valve closes (estimate). Nothing to keep.',
             branch='unbacked branch', sources=['https://eu.leco.com/product/px400-px500-grinder-polisher-series', 'https://pdf.directindustry.com/pdf/leco/px300-grinder-polisher/114499-752979.html', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='furnace', qty=1, backed=False, rated_w=2800, typical_w=0, kind='published',
             what='Nabertherm NAT 15/65 forced-convection chamber furnace (650 °C), B500/B510 controller',
             cut='Heaters and fan stop and the controller rides it out: by default a program continues if the outage is shorter than about 2 min, and outages under 5 s always continue. Modes cancel, delta-T, time and continue can be set. The chamber loses a few kelvin in 8 s (estimate).',
             branch='unbacked branch', sources=['https://nabertherm.com/en/products/industrie/thermprozesstechnik/prozesse-unter-luft/forced-convection-furnaces/forced', 'https://nabertherm.com/sites/default/files/noindex/2024-05/M03.0022_Englisch_2024-04.pdf', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/notes/services.md?plain=1#L139-L165']),
        dict(key='mounting_press', qty=1, backed=False, rated_w=1400, typical_w=0, kind='estimate',
             what='LECO MX400 automatic mounting press (hydraulic, 1200-4300 psi; 90-200 °C)',
             cut='A heat, cure and cool cycle aborts and the mount in the mold is probably spoiled; hydraulic pressure may bleed off (estimate). Cooling water from a recirculator or the dock is cut in transit anyway.',
             branch='unbacked branch', sources=['https://pdf.directindustry.com/pdf/leco/mx400/114499-936234.html', 'https://www.labcompare.com/5207-Laboratory-Press/14224274-MX400-Mounting-Press/']),
        dict(key='quench_tank', qty=1, backed=False, rated_w=60, typical_w=0, kind='estimate',
             what='quench tank with a small lift (our design)',
             cut="The lift stops where it is (a leadscrew doesn't back-drive) and homes on power-up (estimate).",
             branch='unbacked branch', sources=[]),
        dict(key='pi_unit', qty=2, backed=True, rated_w=54, typical_w=8, kind='published',
             what='Raspberry Pi 5 camera unit (Pi 5 4 GB, Active Cooler, HQ Camera and Camera Module 3 Wide), x2',
             cut='Reboots in about 30 s and the stream drops; repeated hard cuts put the SD card at risk (estimate).',
             branch='UPS-backed', sources=['https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='poe_switch', qty=1, backed=True, rated_w=60, typical_w=8, kind='published',
             what='Small managed PoE+ switch, e.g. Ubiquiti USW-Lite-8-PoE (8 ports, 4 PoE+)',
             cut='Every device on the tray loses its network link; the switch takes about a minute to boot (estimate).',
             branch='UPS-backed', sources=['https://techspecs.ui.com/unifi/switching/usw-lite-8-poe']),
    ],
    'K': [
        dict(key='glovebox_tray', qty=1, backed=True, rated_w=30, typical_w=20, kind='estimate',
             what='glovebox controller: a 24 VDC PLC with a 7 in touch HMI and its 24 V supply (our design)',
             cut='Its I/O state and alarms go; kept up, the box stays sealed and logged through the move (estimate).',
             branch='UPS-backed', sources=['https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/notes/instruments_r7.md?plain=1#L21-L47']),
        dict(key='o2_analyzer', qty=1, backed=True, rated_w=20, typical_w=15, kind='published',
             what='Teledyne 3000TA-XL trace oxygen analyser (micro-fuel cell)',
             cut='The reading and its alarms stop; the cell is unaffected but the reading takes a while to settle again (estimate).',
             branch='UPS-backed', sources=['https://www.chromservis.eu/media/0/05_pdf/Catalogues/Teledyne_3000TAXL_UK.pdf']),
        dict(key='h2o_sensor', qty=1, backed=True, rated_w=0.5, typical_w=0.5, kind='snippet',
             what='Michell Easidew TX dew-point transmitter (2-wire 4-20 mA)',
             cut='The reading stops and resumes with the loop (estimate).',
             branch='UPS-backed', sources=['https://www.processsensing.com/docs/datasheet/Michell_Instruments_Easidew_TX_I.S._Datasheet.pdf']),
        dict(key='gb_valves', qty=1, backed=True, rated_w=40, typical_w=0, kind='estimate',
             what='glovebox solenoid valves (purge in, exhaust, antechamber evacuate and refill), 4-6 x 24 VDC',
             cut="Normally closed valves shut and seal the box; the dock's N2 is cut in transit anyway (estimate).",
             branch='UPS-backed (de-energised in transit)', sources=[]),
        dict(key='gb_antechamber_pump', qty=1, backed=False, rated_w=550, typical_w=0, kind='estimate',
             what="antechamber vacuum pump (an Edwards RV3 if the same as the press's; or a diaphragm pump)",
             cut='Stops; the antechamber holds what it has if its valve is shut (estimate).',
             branch='unbacked branch', sources=['https://www.ajvs.com/library/Edwards_RV_Series_Brochure.pdf']),
        dict(key='gb_balance', qty=1, backed=True, rated_w=11, typical_w=11, kind='published',
             what='the balance inside the box (model not chosen; an analytical balance like the HR-202i)',
             cut='Weighing stops; an analytical balance wants about 1 h of warm-up again.',
             branch='UPS-backed', sources=['https://www.aandd.jp/products/manual/balances/hr-i.pdf']),
        dict(key='gb_capper', qty=1, backed=True, rated_w=60, typical_w=10, kind='estimate',
             what='capper on a small gantry and the tipping cradle (our design)',
             cut='Steppers lose torque and position; a lid held by the capper could slip (estimate).',
             branch='UPS-backed', sources=['https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/notes/instruments_r7.md?plain=1#L21-L47']),
        dict(key='vhx', qty=1, backed=True, rated_w=430, typical_w=120, kind='published',
             what='Keyence VHX-7000 controller (with its 27 in 4K screen), EA-300 cabled to it',
             cut='A PC-based controller: unclean shutdown, a reboot of a few minutes, and the motorised stand and EA-300 re-initialise (estimate).',
             branch='UPS-backed', sources=['https://www.keyence.com/products/microscope/digital-microscope/vhx-7000/models/vhx-7000/', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/notes/instruments_r7.md?plain=1#L21-L47']),
        dict(key='vhx_stand', qty=1, backed=True, rated_w=130, typical_w=20, kind='published',
             what='Keyence VHX-S750E motorised free-angle stand',
             cut='Its steppers (5-phase Z, 2-phase XY) lose position and it homes again (estimate).',
             branch='UPS-backed', sources=['https://www.keyence.com/products/microscope/digital-microscope/vhx-7000/models/vhx-s750e/']),
        dict(key='ea300', qty=1, backed=True, rated_w=0, typical_w=0, kind='estimate',
             what='Keyence EA-300 LIBS head (Nd:YAG, 355 nm, Class 1)',
             cut='Goes down with the controller.',
             branch='UPS-backed (through the controller)', sources=['https://www.keyence.com/products/microscope/elemental-analyzer/ea-300/models/ea-300']),
        dict(key='pikvm', qty=1, backed=True, rated_w=12, typical_w=5, kind='published',
             what='PiKVM V4 Mini (KVM over IP for the VHX)',
             cut='Reboots; remote control of the VHX drops (estimate).',
             branch='UPS-backed', sources=['https://docs.pikvm.org/v4/v4mini_datasheet.pdf']),
        dict(key='pi_unit', qty=1, backed=True, rated_w=27, typical_w=4, kind='published',
             what='Raspberry Pi 5 camera unit (Pi 5 4 GB, Active Cooler, HQ Camera and Camera Module 3 Wide), x1',
             cut='Reboots in about 30 s and the stream drops; repeated hard cuts put the SD card at risk (estimate).',
             branch='UPS-backed', sources=['https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='poe_switch', qty=1, backed=True, rated_w=60, typical_w=8, kind='published',
             what='Small managed PoE+ switch, e.g. Ubiquiti USW-Lite-8-PoE (8 ports, 4 PoE+)',
             cut='Every device on the tray loses its network link; the switch takes about a minute to boot (estimate).',
             branch='UPS-backed', sources=['https://techspecs.ui.com/unifi/switching/usw-lite-8-poe']),
    ],
    'L': [
        dict(key='tensile_h', qty=1, backed=True, rated_w=500, typical_w=40, kind='published',
             what='ZwickRoell zwickiLine Z5.0 TN (testControl II)',
             cut='testControl II restarts and a test in progress is lost; testXpert loses the machine; the load cell is zeroed automatically at the start of each test; the crosshead may need re-referencing (estimate).',
             branch='UPS-backed (in Eco mode)', sources=['https://www.zwickroell.com/fileadmin/content/Files/SharePoint/user_upload/PI_EN/02_396_zwickiLine_Z0_5_up_to_Z5_0_Materials_Testing_Machine_PI_EN.pdf']),
        dict(key='zwick_pc', qty=1, backed=True, rated_w=150, typical_w=40, kind='estimate',
             what='the testXpert PC',
             cut='Unclean shutdown and reboot (estimate).',
             branch='UPS-backed', sources=['https://www.zwickroell.com/fileadmin/content/Files/SharePoint/user_upload/PI_EN/02_396_zwickiLine_Z0_5_up_to_Z5_0_Materials_Testing_Machine_PI_EN.pdf']),
        dict(key='hardness', qty=1, backed=True, rated_w=90, typical_w=40, kind='published',
             what='Mitutoyo HM-220 Type D micro-Vickers (motorised XY stage and focus), PC-driven',
             cut='Stage and focus lose position; an indent series and the AVPAK session are lost (estimate).',
             branch='UPS-backed', sources=['https://www.mitutoyo.com/webfoo/wp-content/uploads/K_section.pdf']),
        dict(key='avpak_pc', qty=1, backed=True, rated_w=150, typical_w=40, kind='estimate',
             what='the AVPAK PC (Mitutoyo-specified)',
             cut='Unclean shutdown and reboot (estimate).',
             branch='UPS-backed', sources=['https://www.mitutoyo.com/webfoo/wp-content/uploads/K_section.pdf']),
        dict(key='pi_unit', qty=2, backed=True, rated_w=54, typical_w=8, kind='published',
             what='Raspberry Pi 5 camera unit (Pi 5 4 GB, Active Cooler, HQ Camera and Camera Module 3 Wide), x2',
             cut='Reboots in about 30 s and the stream drops; repeated hard cuts put the SD card at risk (estimate).',
             branch='UPS-backed', sources=['https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='poe_switch', qty=1, backed=True, rated_w=60, typical_w=8, kind='published',
             what='Small managed PoE+ switch, e.g. Ubiquiti USW-Lite-8-PoE (8 ports, 4 PoE+)',
             cut='Every device on the tray loses its network link; the switch takes about a minute to boot (estimate).',
             branch='UPS-backed', sources=['https://techspecs.ui.com/unifi/switching/usw-lite-8-poe']),
    ],
    'M': [
        dict(key='xrf', qty=1, backed=True, rated_w=600, typical_w=120, kind='published',
             what='Bruker S2 PUMA Series 2 EDXRF with the XY Autochanger',
             cut="The tube's high voltage drops; the SDD's cooler stops and the chamber loses its vacuum or helium. After power returns the detector cools and the tube warms before results are stable; Bruker publishes no time (15-30 min, estimate).",
             branch='UPS-backed', sources=['https://technology-products.dksh.com/product/bruker-s2-puma-series-2-high-end-versatile-benchtop-edxrf/', 'https://www.bruker.com/en/products-and-solutions/elemental-analyzers/xrf-spectrometers/s2-puma-series2/other-applications.html']),
        dict(key='xrf_vacuum_pump', qty=1, backed=False, rated_w=300, typical_w=0, kind='estimate',
             what="the S2 PUMA's optional vacuum pump (not specified by Bruker)",
             cut='Stops; the chamber leaks up (estimate).',
             branch='unbacked branch', sources=['https://www.bruker.com/en/products-and-solutions/elemental-analyzers/xrf-spectrometers/s2-puma-series2/other-applications.html']),
        dict(key='fumehood_tray', qty=1, backed=True, rated_w=35, typical_w=35, kind='published',
             what='Sentry Air ductless fume hood, standard 24 in, separate blower (13 x 13 x 14.5 in)',
             cut='The blower stops, so there is no capture during the move (estimate).',
             branch='UPS-backed (35 W keeps capture through the move)', sources=['https://www.sentryair.com/dfhapp.htm']),
        dict(key='cnc', qty=1, backed=False, rated_w=430, typical_w=0, kind='published',
             what='Makera Carvera desktop CNC (200 W spindle), with our lid actuator and pneumatic vise',
             cut="The job aborts; the controller resets and the machine homes again and re-probes its tool (estimate). The pneumatic vise has to hold without air, since the dock's air is cut in transit (estimate).",
             branch='unbacked branch', sources=['https://www.makera.com/blogs/article/carvera-carvera-air-which-desktop-cnc-is-right-for-you', 'https://eu.makera.com/pages/cnc-comparison', 'https://carvera-community.gitbook.io/docs/anatomy-of-a-carvera']),
        dict(key='pi_unit', qty=2, backed=True, rated_w=54, typical_w=8, kind='published',
             what='Raspberry Pi 5 camera unit (Pi 5 4 GB, Active Cooler, HQ Camera and Camera Module 3 Wide), x2',
             cut='Reboots in about 30 s and the stream drops; repeated hard cuts put the SD card at risk (estimate).',
             branch='UPS-backed', sources=['https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='poe_switch', qty=1, backed=True, rated_w=60, typical_w=8, kind='published',
             what='Small managed PoE+ switch, e.g. Ubiquiti USW-Lite-8-PoE (8 ports, 4 PoE+)',
             cut='Every device on the tray loses its network link; the switch takes about a minute to boot (estimate).',
             branch='UPS-backed', sources=['https://techspecs.ui.com/unifi/switching/usw-lite-8-poe']),
    ],
    'H': [
        dict(key='stencil', qty=1, backed=False, rated_w=240, typical_w=0, kind='published',
             what='DDM Novastar SPR-45VA semi-automatic stencil printer',
             cut='Squeegee and power frame lift stop; the optional vacuum hold-down lets go; nothing to resume (estimate).',
             branch='unbacked branch', sources=['https://pentalogix.com/pdf/SPR_45VA_Stencil_Printers.pdf']),
        dict(key='lumenpnp', qty=1, backed=True, rated_w=300, typical_w=15, kind='published',
             what='Opulo LumenPnP v4 pick-and-place',
             cut='Its Marlin board resets: the axes lose position and home again; OpenPnP on the host loses the serial link and any job; the 24 V vacuum pumps and valves stop (estimate).',
             branch='UPS-backed', sources=['https://www.opulo.io/products/lumenpnp-24v-6a-power-supply', 'https://cdn.shopify.com/s/files/1/0570/4256/7355/files/Opulo_Power_Supply_Datasheet-24V_6A.pdf?v=1723229996', 'https://www.opulo.io/products/vacuum-pump-and-valve-set']),
        dict(key='lumenpnp_pc', qty=1, backed=True, rated_w=100, typical_w=25, kind='estimate',
             what='the OpenPnP host PC (a mini PC)',
             cut='OpenPnP and its job state are lost (estimate).',
             branch='UPS-backed', sources=[]),
        dict(key='reflow', qty=1, backed=False, rated_w=1500, typical_w=0, kind='published',
             what='Puhui T-962A infrared reflow oven',
             cut='Heaters and fan stop and the reflow profile aborts; it boots back to its menu (estimate).',
             branch='unbacked branch', sources=['https://taianpuhui.en.made-in-china.com/product/GXLmWKoTvtUI/China-Desktop-Reflow-Oven-Puhui-T962A.html', 'https://wiki.bitraf.no/w/images/1/18/T962A_INFRARED_IC_HEATER_User_Manual.pdf']),
        dict(key='pi_unit', qty=2, backed=True, rated_w=54, typical_w=8, kind='published',
             what='Raspberry Pi 5 camera unit (Pi 5 4 GB, Active Cooler, HQ Camera and Camera Module 3 Wide), x2',
             cut='Reboots in about 30 s and the stream drops; repeated hard cuts put the SD card at risk (estimate).',
             branch='UPS-backed', sources=['https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='poe_switch', qty=1, backed=True, rated_w=60, typical_w=8, kind='published',
             what='Small managed PoE+ switch, e.g. Ubiquiti USW-Lite-8-PoE (8 ports, 4 PoE+)',
             cut='Every device on the tray loses its network link; the switch takes about a minute to boot (estimate).',
             branch='UPS-backed', sources=['https://techspecs.ui.com/unifi/switching/usw-lite-8-poe']),
    ],
    'G': [
        dict(key='form4', qty=2, backed=False, rated_w=960, typical_w=0, kind='published',
             what='Formlabs Form 4, x2',
             cut="A print in progress fails and can't be resumed (Formlabs). An idle printer reboots, and its resin heater (25-45 °C, conduction with infrared sensing) heats again before the next print.",
             branch='unbacked branch', sources=['https://formlabs.com/3d-printers/resin/tech-specs/', 'https://formlabs.com/support/Choosing-an-Uninterruptible-Power-Supply-UPS-for-your-Formlabs-printer/']),
        dict(key='form_wash', qty=1, backed=False, rated_w=50, typical_w=0, kind='published',
             what='Formlabs Form Wash (2nd Gen)',
             cut='A wash stops with the basket where it is (estimate).',
             branch='unbacked branch', sources=['https://formlabs.com/store/form-wash/']),
        dict(key='form_cure', qty=1, backed=False, rated_w=1800, typical_w=0, kind='estimate',
             what='Formlabs Form Cure (2nd Gen)',
             cut='A cure stops; the parts stay in (estimate).',
             branch='unbacked branch', sources=['https://formlabs.com/store/form-cure/', 'https://formlabs.com/global/products/form-cure/']),
        dict(key='pi_unit', qty=2, backed=True, rated_w=54, typical_w=8, kind='published',
             what='Raspberry Pi 5 camera unit (Pi 5 4 GB, Active Cooler, HQ Camera and Camera Module 3 Wide), x2',
             cut='Reboots in about 30 s and the stream drops; repeated hard cuts put the SD card at risk (estimate).',
             branch='UPS-backed', sources=['https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='poe_switch', qty=1, backed=True, rated_w=60, typical_w=8, kind='published',
             what='Small managed PoE+ switch, e.g. Ubiquiti USW-Lite-8-PoE (8 ports, 4 PoE+)',
             cut='Every device on the tray loses its network link; the switch takes about a minute to boot (estimate).',
             branch='UPS-backed', sources=['https://techspecs.ui.com/unifi/switching/usw-lite-8-poe']),
    ],
    'I': [
        dict(key='snowpod', qty=2, backed=False, rated_w=2000, typical_w=0, kind='estimate',
             what='SnowX SnowPod desktop LPBF printer, x2',
             cut="A build in progress is lost (LPBF builds aren't resumable as a rule) and the chamber's gas circulation stops; the machine reboots (estimate).",
             branch='unbacked branch', sources=['https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/fab_metal.py#L438-L441', 'https://makers101.com/snowpod-desktop-metal-3d-printer/']),
        dict(key='nitropod', qty=1, backed=False, rated_w=500, typical_w=0, kind='estimate',
             what='SnowX NitroPod nitrogen generator (99.9 % at 3 L/min, made from air)',
             cut='Stops; N2 flow to the printers stops with it (estimate).',
             branch='unbacked branch', sources=['https://www.3dnatives.com/en/desktop-metal-3d-printer-snowpod-22102026/']),
        dict(key='pi_unit', qty=2, backed=True, rated_w=54, typical_w=8, kind='published',
             what='Raspberry Pi 5 camera unit (Pi 5 4 GB, Active Cooler, HQ Camera and Camera Module 3 Wide), x2',
             cut='Reboots in about 30 s and the stream drops; repeated hard cuts put the SD card at risk (estimate).',
             branch='UPS-backed', sources=['https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply', 'https://github.com/vertical-cloud-lab/byu-vcl/blob/61dbd78/vertical-lab/services.py#L116-L146']),
        dict(key='poe_switch', qty=1, backed=True, rated_w=60, typical_w=8, kind='published',
             what='Small managed PoE+ switch, e.g. Ubiquiti USW-Lite-8-PoE (8 ports, 4 PoE+)',
             cut='Every device on the tray loses its network link; the switch takes about a minute to boot (estimate).',
             branch='UPS-backed', sources=['https://techspecs.ui.com/unifi/switching/usw-lite-8-poe']),
    ],
}



if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "still":
        still(args[1:] or None)
    elif args and args[0] == "lineup":
        print(lineup(), flush=True)
    elif args and args[0] == "figure":
        print(figure(), flush=True)
    elif args and args[0] == "trays":
        print(on_trays(tuple(args[1:]) or ("D", "A", "F")), flush=True)
    else:
        print(table(write_json()), flush=True)
