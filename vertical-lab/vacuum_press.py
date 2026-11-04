"""A vacuum press for the charge cups (#303; DAL #140, #156): a Specac Atlas Autotouch 15T automatic hydraulic press,
with the lab's own evacuable die built round #222's F1 sleeve, a vacuum pump, two valves and a Pirani gauge.

    xvfb-run -a python3 vacuum_press.py           # -> out/vacuum_press.gif, out/mp4/vacuum_press.mp4, .json, still
    PREVIEW=1 xvfb-run -a python3 vacuum_press.py # last frame of each sub-step -> /tmp/preview_vacuum_press.png
    python3 vacuum_press.py numbers               # the compaction numbers only -> out/vacuum_press.json

**Why this press.** It is automatic: a program of up to 10 steps ("pump up to", "maintain for", "release to") runs
from one Start press and tops the load back up as the powder settles ("Maintain Load"). Its numbers are published.
It takes evacuable dies (Specac sells them), and Specac's own videos show the whole cycle. The 15T's load range,
2-15 t in 0.2 t steps, brackets the 3.2 t this needs with room for Cu cups. The 8T and 25T share its frame.

**Off the shelf:** the press; a two-stage rotary-vane pump; isolation valve V1, vent valve V2 with a needle valve for
a soft start, and a Pirani gauge. **Ours:** the evacuable die (body, punch with an O-ring, ejector pin) round F1, the
catch ring on F1 that the ejected cup stands in, the shuttle that carries the die out of the press to the arm, the
ejector under the shuttle's out position, and the dry Ar line on V2.

Sources of every dimension (mm; press frame: origin on the bench at the centre of the press's footprint, z up, front
= -y, as ``charge.press_parts``):

* Published, Specac's Autotouch page (specac.com/product/autotouch-press-high-throughput-xrf-press, read
  2026-11-04): 425 x 405 x 640 mm (W x D x H, 8T/15T/25T), 95 kg, ram stroke 24 mm, piston 82 mm, leadscrew nose 32
  mm, 40-155 mm between the pressing faces, working area 220 mm across x 155 mm high, 15T load 2-15 t in 0.2 t steps,
  6 programs x 10 steps, hold 0.1-99.9 min (or until Stop), fast/medium/slow release.
* Read off Specac's product shot and videos (YouTube BH___JpLYeE at 0:17, 1:12-1:19 and 2:25; b2jWgsfSmMQ at
  0:51 and 1:37), scaled to the published 425 x 640 mm: the press column (frame) on the left, 292 mm wide, the blue
  control tower on the right, about 133 mm wide and 500 mm tall, the touchscreen at the top of the tower (about 110 x
  65 mm, centre ~420 mm up) with the silver Start and Stop buttons under it; the grey plinth ~115 mm tall with a
  rounded front; the blue drum round the cylinder ~250 mm across and ~120 mm tall; the clear curved PETG guard in a
  grey frame, slid up to open and down to close (handle on its bottom rail); the crosshead with the leadscrew.
* Assumed (no published drawing): the press axis 66 mm left of the footprint's centre and 56 mm in front of it; the
  depth of the column and tower; the guard's curvature.
* Ours: the die, punch, shuttle, rails, ejector and the vacuum plumbing are designed here and are not built. The pump
  is drawn the size of a small two-stage rotary-vane pump (assumed, ~300 x 140 x 190 mm; check the one bought).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pyvista as pv

import charge as C
from charge import _box, _cylz, lathe

HERE = Path(__file__).resolve().parent

# ------------------------------------------------------------------ the press, published (see the docstring)
AT = dict(model="Specac Atlas Autotouch 15T (GS2581X)", W=425.0, D=405.0, H=640.0, mass_kg=95.0, stroke=24.0,
          piston_d=82.0, nose_d=32.0, faces=(40.0, 155.0), work_d=220.0, work_h=155.0, load_t=(2.0, 15.0),
          step_t=0.2, programs=6, steps=10, hold_min=(0.1, 99.9))

# ------------------------------------------------------------------ layout (press frame, mm)
AXX, AXY = -66.0, -56.0          # the press axis (assumed from the product shot)
Z_PLINTH, Z_DRUM = 115.0, 235.0
Z_PISTON = 245.0                 # piston face, ram down (10 mm proud of the drum, so the shuttle's rails fit under it)
Z_XHEAD = Z_PISTON + AT["faces"][1]   # crosshead underside: 155 mm between the faces with the leadscrew fully up
COL_X = (AXX - 146.0, AXX + 146.0)    # the column's outer faces
TOWER_X = (COL_X[1], AT["W"] / 2)
COL_FRONT = AXY - 60.0
G_R, G_CY = 220.0, AXY + 100.0        # the guard: a cylinder section, radius 220, centred behind the axis
GUARD_Z0, GUARD_H, GUARD_OPEN = Z_PISTON + 2.0, Z_XHEAD + 22.0 - (Z_PISTON + 2.0), 165.0

# the die, in the shuttle's frame: origin at the shuttle plate's underside, on the axis of the die
PLATE_T, BASE_T = 15.0, 15.0
CUP_BASE = PLATE_T + BASE_T                      # 30: the bore floor, where the cup stands
F1_TOP = CUP_BASE + C.SLEEVE_L                   # 93.5
GUIDE = 22.0                                     # the catch ring on F1 (below): guides the punch's nose, which seals
BODY_TOP = F1_TOP + GUIDE                        # 115.5
BODY_R, BORE_R = 40.0, C.SLEEVE_OD / 2 + 0.025   # Ø80 body; F1 and the catch ring a slip fit in its bore
PORT_Z = F1_TOP + 4.0                            # the vacuum port opens into the bore 4 mm above F1, through the ring
LEAD = C.PLUG_LEADIN_L * 0.98                    # the plug stands in the mouth on its lead-in (as alloy_charge)
PLUG_SET = C.SLUG_L - LEAD                       # plug bottom when set by the arm, cup frame
TRAVEL = PLUG_SET - C.PLUG_HOME_Z                # 8.03 mm to flush
# The catch (Sterling, PR #318: a cup raised on the bare pin "looks very unstable"). Nothing riding on the pin can hold
# the cup round its base: the pin pushes the cup up through F1, a line-to-line fit on the cup (+0.013 mm), so whatever
# goes up with it has to fit inside the cup's own diameter. The catch is in the die's mouth instead: a hardened ring
# as wide as F1, standing on it in the top of the bore, bored 0.25 mm over the cup with a 30° lead-in. The pin stops
# with the cup's bottom CATCH mm still in the ring, so the cup stands in a socket, not on a pin, while the arm sets it
# and lifts it off. The punch gets a nose that fits the ring and a collar that lands on the ring's top at flush, so the
# load past flush still goes into F1 (through the ring), and the punch is as tall as before.
RING_D, RING_LEAD = C.STOCK_D + 0.25, (1.5, 2.6)  # Ø19.30 bore; lead-in 1.5 mm across over 2.6 mm (30° off the axis)
CATCH = 10.0                                     # the cup's bottom 10 mm stay in the ring with the pin up
PUNCH_R, PUNCH_L, FLANGE_R, FLANGE_T, ORING_Z = 15.85, 30.0, 25.0, 12.0, 10.0
NOSE_R = 9.60                                    # the punch's nose, Ø19.20 and as long as the ring; then a Ø31.70
#                                                  collar, 8 mm, that lands on the ring at flush; then the flange
PUNCH_SET = CUP_BASE + PLUG_SET + C.PLUG_L      # punch face resting on the set plug
GAP = 2.0                                        # leadscrew nose over the punch's top, ram down (set once by hand)
Y_OUT = AXY - 230.0                              # the shuttle's out position, in front of the press

VP = dict(axis=(AXX, AXY), W=AT["W"], D=AT["D"], H=AT["H"], piston_down=Z_PISTON, stroke=AT["stroke"],
          shuttle_in_y=AXY, shuttle_out_y=Y_OUT, plate_t=PLATE_T, cup_base_local=CUP_BASE, f1_top_local=F1_TOP,
          body_top_local=BODY_TOP, port_local=(-BODY_R - 18.0, 0.0, PORT_Z), punch_set_local=PUNCH_SET,
          punch_top_local=PUNCH_SET + PUNCH_L + FLANGE_T, travel=TRAVEL, plug_set=PLUG_SET, gap=GAP,
          eject=BODY_TOP - CUP_BASE - CATCH, catch=CATCH, ring_d=RING_D, guard_open=GUARD_OPEN)
VP["nose_z"] = Z_PISTON + VP["punch_top_local"] + GAP                  # leadscrew nose (set once for this die)
VP["faces_set"] = VP["nose_z"] - Z_PISTON                              # within 40-155
VP["ram_touch"] = GAP                                                  # ram travel when the nose meets the punch
VP["ram_flush"] = GAP + TRAVEL                                         # ... and when the plug is flush
VP["cup_base_in"] = (AXX, AXY, Z_PISTON + CUP_BASE)                    # world (press frame), ram down
VP["cup_base_out"] = (AXX, Y_OUT, Z_PISTON + CUP_BASE)                 # where the pin takes the cup, pin down
VP["cup_base_eject"] = (AXX, Y_OUT, Z_PISTON + CUP_BASE + VP["eject"])  # where the arm sets / picks it, pin up
VP["footprint_with_shuttle"] = dict(x=(-560.0, AT["W"] / 2), y=(Y_OUT - 75.0, AT["D"] / 2))

# ------------------------------------------------------------------ colours
BLUE = (0.36, 0.45, 0.64)
GREY = (0.80, 0.81, 0.83)
GREY2 = (0.70, 0.71, 0.74)
DARK = (0.12, 0.13, 0.15)
SCREEN = (0.17, 0.24, 0.66)
BRIGHT = (0.74, 0.75, 0.78)
PETG = (0.82, 0.88, 0.94)
PETG_ALPHA = 0.20
TOOL = (0.52, 0.53, 0.57)          # hardened tool steel
CATCH_C = (0.66, 0.58, 0.36)       # the catch ring (hardened steel, drawn bronze-toned so it reads against the body)
PUMP = (0.25, 0.27, 0.30)
AR = (0.20, 0.45, 0.78)


def arc(profile, a0, a1, cx=0.0, cy=0.0, res=40) -> pv.PolyData:
    """Revolve a closed (r, z) profile from angle a0 to a1 (degrees, from +x) about a vertical axis at (cx, cy)."""
    pts = np.array([(r, 0.0, z) for r, z in profile], float)
    n = len(pts)
    m = pv.PolyData(pts, faces=np.r_[n, np.arange(n)]).extrude_rotate(resolution=res, angle=a1 - a0, capping=True,
                                                                        rotation_axis=(0, 0, 1))
    m = m.triangulate().clean().rotate_z(a0, inplace=False).translate((cx, cy, 0.0), inplace=False)
    return m.compute_normals(split_vertices=True, feature_angle=50.0, auto_orient_normals=True)


def _cylx(r, x0, x1, y, z, res=32):
    return pv.Cylinder(center=((x0 + x1) / 2, y, z), direction=(1, 0, 0), radius=r, height=abs(x1 - x0),
                       resolution=res).triangulate()


def _cyly(r, y0, y1, x, z, res=32):
    return pv.Cylinder(center=(x, (y0 + y1) / 2, z), direction=(0, 1, 0), radius=r, height=abs(y1 - y0),
                       resolution=res).triangulate()


def _merge(*ms):
    out = ms[0]
    for m in ms[1:]:
        out = out.merge(m)
    return out


# ------------------------------------------------------------------ our die, in the shuttle frame
def body_profile():
    c = 1.0
    return [(8.0, PLATE_T), (BODY_R - c, PLATE_T), (BODY_R, PLATE_T + c), (BODY_R, BODY_TOP - c),
            (BODY_R - c, BODY_TOP), (BORE_R + 0.6, BODY_TOP), (BORE_R, BODY_TOP - 0.6), (BORE_R, CUP_BASE),
            (8.0, CUP_BASE)]


def punch_profile():
    """The nose (Ø19.20, as long as the catch ring, the O-ring on it), the collar (Ø31.70) whose underside lands on
    the ring at flush, and the flange the gripper holds. Face at z = 0."""
    return [(0.0, 0.0), (NOSE_R - 0.5, 0.0), (NOSE_R, 0.5), (NOSE_R, GUIDE), (PUNCH_R, GUIDE), (PUNCH_R, PUNCH_L),
            (FLANGE_R - 1.0, PUNCH_L), (FLANGE_R, PUNCH_L + 1.0), (FLANGE_R, PUNCH_L + FLANGE_T - 1.0),
            (FLANGE_R - 1.0, PUNCH_L + FLANGE_T), (0.0, PUNCH_L + FLANGE_T)]


def ring_profile():
    """The catch ring, shuttle frame: on F1, filling the bore up to the body's top, bored 0.25 mm over the cup, with
    a 30° lead-in."""
    ri, ro = RING_D / 2, C.SLEEVE_OD / 2
    dl, hl = RING_LEAD
    return [(ri, F1_TOP), (ro, F1_TOP), (ro, BODY_TOP - 0.5), (ro - 0.5, BODY_TOP), (ri + dl, BODY_TOP),
            (ri, BODY_TOP - hl)]


def die_parts(cut=False) -> dict:
    """The die's lathe parts, whole or cut in half (back half kept, as charge.lathe): body (with its port), F1, the
    catch ring on F1, the punch (face at z = 0) and the ejector pin (top at z = 0). Body, F1 and the catch ring are
    in the shuttle frame."""
    body = lathe(body_profile(), cut)
    f1 = C.sleeve(cut).translate((0, 0, CUP_BASE), inplace=False)
    catch = lathe(ring_profile(), cut)
    punch = lathe(punch_profile(), cut)
    ring = pv.ParametricTorus(ringradius=NOSE_R - 0.6, crosssectionradius=1.2).translate((0, 0, ORING_Z),
                                                                                          inplace=False)
    if cut:
        ring = ring.clip(normal=(0, 1, 0), origin=(0, 0, 0), invert=False)
    pin = lathe([(0, -CUP_BASE), (7.9, -CUP_BASE), (7.9, 0.0), (0, 0.0)], cut, res=32)
    x0 = -BODY_R + 0.5
    port = _merge(_cylx(7.0, x0, -BODY_R - 14.0, 0.0, PORT_Z), _cylx(15.0, -BODY_R - 14.0, -BODY_R - 18.0, 0.0, PORT_Z))
    hole = _cylx(1.6, -RING_D / 2 + 0.2, -BODY_R - 18.2, 0.0, PORT_Z, res=16)  # through the ring and the body wall
    return dict(body=body, f1=f1, catch=catch, punch=punch, oring=ring, pin=pin, port=port, hole=hole)


def channel_strip(cut=False):
    """DAL #156's channel across the plug's top, through the vent, drawn as a dark strip (cup frame, plug at home
    = its bottom at z = 0)."""
    r = C.CUP_BORE_D / 2 - 0.3
    return _box(-0.6, 0.6, 0.0 if cut else -r, r, C.PLUG_L - 0.05, C.PLUG_L + 0.06)


# ------------------------------------------------------------------ the press
def press_parts() -> dict:
    """{group: {name: (mesh, colour)}}. Groups and their frames:

    * fixed: plinth, drum, column, crosshead, leadscrew, rails and the shuttle's stand, press frame.
    * screen: the tower's touchscreen, buttons and labels (press frame; separate so it can be highlighted).
    * guard: frame and clear panel ("panel", draw it at PETG_ALPHA) at closed; open = +VP["guard_open"] in z.
    * ram: the piston, face at Z_PISTON; moves +z by 0 to VP["stroke"].
    * shuttle: plate, die body, F1, the catch ring on F1, the port; its frame's origin is the plate's underside on
      the die axis. Place it at (AXX, y, Z_PISTON + ram) with y from VP["shuttle_out_y"] to VP["shuttle_in_y"].
    * pin: the ejector pin, child of the shuttle, top at the bore floor (VP["cup_base_local"]) + 0 to VP["eject"]
      (the cup's bottom VP["catch"] mm still in the catch ring).
    * ejector: the push rod in the stand at the out position, top at 0 (place it at (AXX, Y_OUT, Z_PISTON + e)).
    * punch: the die's punch (lid), face at z = 0; the arm sets it in the bore on the plug (VP["punch_set_local"]).
    * vacuum: pump, valve block (V1, V2, needle valve), Pirani gauge and the fixed lines (press frame).
    The die's flexible hose runs from the port (moving) to the block: ``hose(p_port, HOSE_END)``.
    """
    x0, x1 = COL_X
    fixed = {
        "plinth": (_merge(arc([(0, 0), (146.0, 0), (146.0, Z_PLINTH), (0, Z_PLINTH)], 180, 360, AXX, AXY),
                          _box(x0, x1, AXY, AT["D"] / 2 - 15, 0, Z_PLINTH)), GREY),
        "drum": (_merge(_cylz(125.0, Z_PLINTH, Z_DRUM, AXX, AXY, res=72),
                        *[C._ring(r + 0.8, r, Z_DRUM, Z_DRUM + 0.4, AXX, AXY) for r in (50.0, 70.0, 90.0)]), BLUE),
        "column": (_merge(_box(x0, x0 + 20, COL_FRONT, AT["D"] / 2 - 15, Z_PLINTH, AT["H"] - 5),
                          _box(x1 - 20, x1, COL_FRONT, AT["D"] / 2 - 15, Z_PLINTH, AT["H"] - 5),
                          _box(x0, x1, AXY + 120, AT["D"] / 2 - 15, Z_PLINTH, Z_DRUM),
                          _box(x0, x1, COL_FRONT, AT["D"] / 2 - 15, Z_XHEAD, AT["H"]),
                          _box(x0 + 20, x1 - 20, AXY + 150, AXY + 160, Z_DRUM, Z_XHEAD)), GREY),
        "dome": (lathe([(0, 0), (16.5, 0), (22, -4), (34, -10), (45, -12), (45, 0)], res=48)
                 .translate((AXX, AXY, Z_XHEAD), inplace=False), (0.93, 0.93, 0.94)),
        "leadscrew": (_merge(_cylz(AT["nose_d"] / 2, VP["nose_z"], Z_XHEAD - 10, AXX, AXY),
                             *[C._ring(16.6, 15.5, z, z + 1.2, AXX, AXY)
                               for z in np.arange(VP["nose_z"] + 2.0, Z_XHEAD - 11, 2.5)]), BRIGHT),
        "rails": (_merge(_box(AXX - 55, AXX - 45, Y_OUT - 58, AXY + 45, Z_DRUM, Z_PISTON),
                         _box(AXX + 45, AXX + 55, Y_OUT - 58, AXY + 45, Z_DRUM, Z_PISTON)), C.STEEL),
        "stand": (_box(AXX - 62, AXX + 62, Y_OUT - 64, AXY - 140, 0, Z_DRUM), (0.30, 0.31, 0.34)),
        "tower": (_merge(_box(TOWER_X[0], TOWER_X[1] - 6, -165.0, AT["D"] / 2, 0, 500.0),
                         _box(TOWER_X[1] - 6, TOWER_X[1], -150.0, AT["D"] / 2, 0, 488.0)), BLUE),
    }
    tx = (TOWER_X[0] + TOWER_X[1]) / 2
    yf = -165.0
    screen = {
        "bezel": (_box(tx - 60, tx + 60, yf - 3, yf, 380, 458), DARK),
        "screen": (_box(tx - 54, tx + 54, yf - 3.6, yf - 3, 388, 450), SCREEN),
        "label": (_box(tx - 60, tx + 60, yf - 2, yf, 464, 488), (0.86, 0.87, 0.90)),
        "badge": (_box(tx + 34, tx + 58, yf - 2.6, yf - 2, 467, 485), (0.80, 0.12, 0.12)),
        "buttons": (_merge(_cyly(11.0, yf - 6, yf, tx + 38, 352), _cyly(11.0, yf - 6, yf, tx + 38, 318)), BRIGHT),
        "switch": (_box(tx + 30, tx + 46, yf - 6, yf, 88, 110), (0.10, 0.55, 0.20)),
    }
    a = math.degrees(math.asin(150.0 / G_R))
    a0, a1 = 270.0 - a, 270.0 + a
    z0, z1 = GUARD_Z0, GUARD_Z0 + GUARD_H
    rail = lambda za, zb, r0, r1: arc([(r0, za), (r1, za), (r1, zb), (r0, zb)], a0, a1, AXX, G_CY, res=48)  # noqa
    stile = []
    for s in (-1, 1):
        ang = math.radians(270.0 + s * a)
        px, py = AXX + G_R * math.cos(ang), G_CY + G_R * math.sin(ang)
        stile.append(_box(px - 7, px + 7, py - 6, py + 6, z0, z1))
    guard = {
        "frame": (_merge(rail(z0, z0 + 14, G_R - 3, G_R + 6), rail(z1 - 14, z1, G_R - 3, G_R + 6), *stile), GREY),
        "handle": (arc([(G_R + 6, z0 + 2), (G_R + 16, z0 + 2), (G_R + 16, z0 + 12), (G_R + 6, z0 + 12)],
                       270 - 9, 270 + 9, AXX, G_CY, res=12), GREY2),
        "panel": (rail(z0 + 14, z1 - 14, G_R - 1.5, G_R + 1.5), PETG),
    }
    ram = {"piston": (_cylz(AT["piston_d"] / 2, Z_DRUM - 40.0, Z_PISTON, AXX, AXY, res=64), BRIGHT)}
    d = die_parts()
    shuttle = {"plate": (_box(-55, 55, -55, 55, 0, PLATE_T), TOOL), "body": (d["body"], C.STEEL),
               "f1": (d["f1"], (0.47, 0.48, 0.52)), "catch": (d["catch"], CATCH_C), "port": (d["port"], BRIGHT)}
    pin = {"pin": (d["pin"].translate((0, 0, CUP_BASE), inplace=False), BRIGHT)}
    ejector = {"rod": (_cylz(7.5, -130.0, 0.0, res=24), BRIGHT)}
    punch = {"punch": (d["punch"], TOOL), "oring": (d["oring"], DARK)}
    vacuum = vacuum_parts()
    return dict(fixed=fixed, screen=screen, guard=guard, ram=ram, shuttle=shuttle, pin=pin, ejector=ejector,
                punch=punch, vacuum=vacuum)


BLOCK = (-330.0, -110.0, 262.0)              # valve block centre (press frame), left of the press
HOSE_END = (BLOCK[0] + 34.0, BLOCK[1], BLOCK[2])


def vacuum_parts() -> dict:
    """Pump on the bench to the press's left, the valve block on a post in front of it (V1 to the pump, V2 to the
    dry Ar line through a needle valve), the Pirani gauge on top with its display to the front, and the fixed lines."""
    bx, by, bz = BLOCK
    pump = _merge(_box(-560, -420, -60, 80, 18, 200), _cylx(68.0, -420, -270, 10.0, 110.0),
                  _box(-555, -275, -50, 70, 0, 18))
    fan = _cylx(60.0, -270, -262, 10.0, 110.0)
    handle = _merge(_box(-505, -495, 0, 20, 200, 232), _box(-475, -465, 0, 20, 200, 232), _box(-505, -465, 0, 20, 226, 236))
    block = _box(bx - 30, bx + 30, by - 20, by + 20, bz - 20, bz + 20)
    post = _merge(_cylz(10.0, 0, bz - 20, bx, by), _box(bx - 45, bx + 45, by - 45, by + 45, 0, 8))
    valves = _merge(_cylz(13.0, bz + 20, bz + 58, bx - 15, by), _cylz(13.0, bz + 20, bz + 58, bx + 15, by + 0),
                    _cylx(5.0, bx - 30, bx - 52, by, bz - 6))
    knob = _cylx(9.0, bx - 52, bx - 64, by, bz - 6)
    gauge = _box(bx - 26, bx + 26, by - 24, by + 10, bz - 62, bz - 22)
    display = _box(bx - 20, bx + 20, by - 25, by - 24, bz - 52, bz - 32)
    line = pv.Spline(np.array([(bx - 15, by, bz + 58), (bx - 15, by + 20, bz + 120), (-450, -60, 300),
                               (-500, 10, 236), (-500, 10, 200)]), 40).tube(radius=6.0)
    ar = pv.Spline(np.array([(bx + 15, by, bz + 58), (bx + 15, by + 30, bz + 110), (-260, 60, 330),
                             (-240, 150, 250), (-240, 220, 0)]), 50).tube(radius=3.0)
    return {"pump": (pump, PUMP), "fan": (fan, DARK), "handle": (handle, DARK), "block": (_merge(block, post), BRIGHT),
            "valves": (valves, (0.15, 0.16, 0.18)), "knob": (knob, (0.80, 0.12, 0.12)), "gauge": (gauge, (0.90, 0.90, 0.88)),
            "display": (display, DARK), "line": (line, BRIGHT), "ar_line": (ar, AR)}


def hose_line(p_port, p_end=HOSE_END) -> pv.PolyData:
    """The centreline of the die's flexible KF16 hose, from its port flange (world) to the valve block. With the die
    in the press it drops to the drum and leaves under the guard, beside the rails."""
    p0, p1 = np.asarray(p_port, float), np.asarray(p_end, float)
    if p0[1] > Y_OUT + 60:                      # die in (or on its way): out under the guard's bottom rail
        mid = [(p0[0] - 16.0, p0[1] - 50.0, Z_DRUM + 14.0), (p0[0] - 12.0, AXY - 125.0, Z_DRUM + 6.0),
               (p0[0] - 40.0, min(AXY - 190.0, p0[1] - 100.0), Z_DRUM + 6.0)]
    else:
        mid = [(p0[0] - 40.0, p0[1] - 5.0, p0[2] - 60.0)]
    pts = np.array([p0, p0 + (-30.0, 0, 0), *mid, p1 + (40.0, 0, -6.0), p1])
    return pv.Spline(pts, 80)


def hose(p_port, p_end=HOSE_END, r=6.0) -> pv.PolyData:
    return hose_line(p_port, p_end).tube(radius=r)


def press() -> dict:
    """The press assembled for static scenes, guard closed, shuttle in, punch off: {name: (mesh, colour)}."""
    p = press_parts()
    out = {}
    for g in ("fixed", "screen", "guard", "ram", "vacuum"):
        out.update({f"{g}/{k}": v for k, v in p[g].items()})
    T = (AXX, AXY, Z_PISTON)
    for g in ("shuttle", "pin"):
        out.update({f"{g}/{k}": (m.translate(T, inplace=False), c) for k, (m, c) in p[g].items()})
    out["hose"] = (hose(np.array(T) + VP["port_local"]), BRIGHT)
    return out


# ------------------------------------------------------------------ the compaction model
SOLID = {"AlSi10Mg": 2.67, "Si": 2.33, "Ni": 8.91}            # g/cm3, full density
TAP = {"AlSi10Mg": 1.60, "Si": 1.10, "Ni": 4.9}                # tapped: #222 (AlSi10Mg, Si); Ni assumed (charge.py)
E4 = dict(mass_g=9.9, bore_MPa=100.0)                          # #222: E4 9.9 g pressed flush, ~100 MPa (1.3 t)
P_FIT, MU_S, MU_K = 30.7, (1.05, 1.35), 0.40                   # #222: contact MPa at .0008 in; static and sliding mu
RESERVE_T = 2.0                                                # #222: "Reserve 2 t" for the press fit
G = 9.80665
T_ROOM, T_MELT = 293.0, 973.0


def bore_area():
    return math.pi / 4 * C.CUP_BORE_D ** 2


def cavity(top):
    """Bore volume (mm3) from the drill point up to `top` (cup frame)."""
    a = bore_area()
    return a * C.drill_point_h(C.CUP_BORE_D) / 3 + a * (top - C.FLOOR_Z)


def heckel_k(powder="AlSi10Mg"):
    """Heckel slope (1/MPa) through the tapped density at 0 MPa and #222's E4 point (9.9 g flush, ~100 MPa).
    Only AlSi10Mg has a point; the others are not calibrated."""
    d_tap = TAP[powder] / SOLID[powder]
    d_e4 = E4["mass_g"] / (SOLID["AlSi10Mg"] * cavity(C.PLUG_HOME_Z) / 1000)
    return (math.log(1 / (1 - d_e4)) - math.log(1 / (1 - TAP["AlSi10Mg"] / SOLID["AlSi10Mg"]))) / E4["bore_MPa"], d_tap


def powder_mpa(rel, powder="AlSi10Mg"):
    k, d_tap = heckel_k(powder)
    return max(0.0, (math.log(1 / (1 - rel)) - math.log(1 / (1 - d_tap))) / k)


def fit_kN(x, mu):
    """Plug friction (kN) at travel x: #222's press fit (contact p over the plug's length, 1.3-1.6 t at mu 1.05-1.35
    when fully in), taken in proportion to how much of the plug's straight land has entered the bore's straight part."""
    x0 = max(0.0, C.PLUG_LEADIN_L - LEAD + C.RIM_CHAMFER)     # the land's lower edge reaches the bore's straight part
    e = min(1.0, max(0.0, (x - x0) / (TRAVEL - x0)))
    return mu * P_FIT * math.pi * C.CUP_BORE_D * C.PLUG_L * e / 1000.0


def compaction(powder="AlSi10Mg", mass_g=None, n=41) -> dict:
    """The plug's stroke from set (lead-in in the mouth) to flush, with the powder tapped up to the set plug's bottom
    unless `mass_g` is given: fill heights, green densities, the ram force over the stroke and the set point."""
    v0, v1 = cavity(PLUG_SET) / 1000, cavity(C.PLUG_HOME_Z) / 1000           # cm3
    m = TAP[powder] * v0 if mass_g is None else mass_g
    rho = SOLID[powder]
    a = bore_area()
    xs = np.linspace(0, TRAVEL, n)
    rows = []
    for x in xs:
        v = v1 + (v0 - v1) * (1 - x / TRAVEL)
        rel = m / (rho * v)
        p = powder_mpa(rel, powder) if rel > TAP[powder] / rho else 0.0
        fp = p * a / 1000
        rows.append(dict(x_mm=round(float(x), 3), rel_density=round(rel, 4), powder_MPa=round(p, 1),
                         powder_kN=round(fp, 2), fit_slide_kN=round(fit_kN(x, MU_K), 2),
                         fit_break_kN=round(fit_kN(x, MU_S[1]), 2), total_slide_kN=round(fp + fit_kN(x, MU_K), 2),
                         total_break_kN=round(fp + fit_kN(x, MU_S[1]), 2)))
    f = rows[-1]
    need_t = (f["powder_kN"] + fit_kN(TRAVEL, MU_S[1])) / G
    set_t = math.ceil((f["powder_kN"] / G + RESERVE_T) / AT["step_t"] - 1e-9) * AT["step_t"]
    set_t = max(set_t, AT["load_t"][0])
    f1_area = math.pi / 4 * (C.SLEEVE_OD ** 2 - C.SLEEVE_BORE_D ** 2)
    pore0, pore1 = v0 - m / rho, v1 - m / rho
    gas = {}
    for name, p0 in (("air, no vacuum", 1013.0), ("pumped to 1 mbar", 1.0)):
        p_flush = p0 * pore0 / pore1                         # if no gas left through the vent while the plug went in
        gas[name] = dict(start_mbar=p0, at_flush_mbar=round(p_flush, 2),
                         at_700C_if_sealed_mbar=round(p_flush * T_MELT / T_ROOM, 2),
                         gas_umol=round(p0 * 100 * pore0 * 1e-6 / (8.314 * T_ROOM) * 1e6, 3))
    return dict(powder=powder, mass_g=round(m, 2), solid_g_cm3=rho, tapped_g_cm3=TAP[powder],
                fill_top_mm_before=round(PLUG_SET - C.FLOOR_Z, 2), fill_top_mm_after=round(C.PLUG_HOME_Z - C.FLOOR_Z, 2),
                column_note="heights above the bore floor (the 118 deg drill point under it is full too)",
                volume_cm3_before=round(v0, 3), volume_cm3_after=round(v1, 3),
                rel_density_before=round(m / (rho * v0), 3), rel_density_after=round(f["rel_density"], 3),
                plug_travel_mm=round(TRAVEL, 3), powder_MPa_at_flush=f["powder_MPa"],
                powder_t_at_flush=round(f["powder_kN"] / G, 2),
                fit_t_at_flush=dict(sliding=round(fit_kN(TRAVEL, MU_K) / G, 2),
                                    breakaway=[round(fit_kN(TRAVEL, mu) / G, 2) for mu in MU_S]),
                needed_t_at_flush_breakaway=round(need_t, 2), set_point_t=round(set_t, 1),
                set_point_kN=round(set_t * G, 1),
                f1_MPa_at_set_point=round((set_t * G - f["powder_kN"] - fit_kN(TRAVEL, MU_K)) * 1000 / f1_area, 1),
                gas_in_pores=gas, stroke=rows)


def runs_vs_set_line() -> dict:
    """Do charge.py's current doses reach the plug? (Headspace under the set plug means pressing compacts nothing.)"""
    rec = C.recipe()
    out = {}
    v_set = cavity(PLUG_SET) / 1000
    for name, (metal, pw, wt, _) in C.RUNS.items():
        cup = rec["runs"][name]["cups"][0]
        m_fill = v_set * C.POWDERS[pw][1]
        m_host = cup["cup_g"] + cup["plug_g"]
        out[name] = dict(powder=pw, dose_g=cup["powder_g"], fill_mm=cup["fill_mm"],
                         gap_under_set_plug_mm=round(PLUG_SET - C.FLOOR_Z - cup["fill_mm"], 1),
                         dose_to_fill_set_line_g=round(m_fill, 2),
                         wt_pct_if_filled=round(100 * m_fill / (m_fill + m_host), 1))
    return out


def report() -> dict:
    c = compaction()
    e4 = compaction(mass_g=E4["mass_g"])
    r = dict(press=AT, layout={k: (list(v) if isinstance(v, tuple) else v) for k, v in VP.items()},
             alsi10mg_filled_to_set_line={k: v for k, v in c.items() if k != "stroke"},
             e4_dose_9p9g={k: e4[k] for k in ("mass_g", "rel_density_after", "powder_MPa_at_flush", "powder_t_at_flush",
                                              "set_point_t")},
             e4_note="9.9 g at 1.60 g/cm3 stands 1.5 mm above the set plug's bottom (#222 filled to the rim and pressed "
                     "by hand), so the arm could not set the plug in the mouth on it",
             current_runs=runs_vs_set_line(), stroke=c["stroke"],
             program=[("P1 step 1", f"pump up to {c['set_point_t']:.1f} t"), ("P1 step 2", "maintain for 1.0 min"),
                      ("P1 step 3", "slow release to 0.0 t")],
             assumed=["Heckel line through the tapped density and #222's E4 point (an estimate, not a measurement)",
                      "plug friction in proportion to the land engaged; #222's 1.3-1.6 t breakaway when fully in",
                      "no gas leaves through the vent while the plug goes in (upper bound on the trapped gas)",
                      "pumped to 1 mbar before pressing"])
    return r


# ------------------------------------------------------------------ the clip
def movie():
    import scene
    scene.GIF_FPS = 8
    scene.GIF_SIZE = (640, 360)
    from scene import Scene, T, S, window

    model = compaction()
    stroke = model["stroke"]
    set_t = model["set_point_t"]
    sc = Scene("vacuum_press", "A vacuum press for the charge cups: Specac Atlas Autotouch 15T + our evacuable die")
    parts = press_parts()
    for g in ("fixed", "screen", "vacuum"):
        for k, (m, col) in parts[g].items():
            sc.add(f"vp_{g}/{k}", m, col, "vp", specular=0.25 if g != "vacuum" else 0.15)
    for k, (m, col) in parts["guard"].items():
        sc.add(f"guard/{k}", m, col, "guard", opacity=PETG_ALPHA if k == "panel" else 1.0, specular=0.5)
    sc.add("ram/piston", parts["ram"]["piston"][0], BRIGHT, "ram", specular=0.6)
    cut = die_parts(cut=True)
    for k, (m, col) in parts["shuttle"].items():
        sc.add(f"sh/{k}", m, col, "shuttle", specular=0.5)
    sc.add("sh/body_cut", cut["body"], C.STEEL, "shuttle", specular=0.5, shown=False)
    sc.add("sh/f1_cut", cut["f1"], (0.47, 0.48, 0.52), "shuttle", specular=0.5, shown=False)
    sc.add("sh/catch_cut", cut["catch"], CATCH_C, "shuttle", specular=0.5, shown=False)
    sc.add("sh/hole", cut["hole"], DARK, "shuttle", shown=False)
    sc.add("pin/pin", parts["pin"]["pin"][0], BRIGHT, "pin", specular=0.5)
    sc.add("pin/cut", cut["pin"].translate((0, 0, CUP_BASE), inplace=False), BRIGHT, "pin", specular=0.5, shown=False)
    sc.add("ej/rod", parts["ejector"]["rod"][0], BRIGHT, "ejector", specular=0.5)
    sc.add("punch/whole", parts["punch"]["punch"][0], TOOL, "punch", specular=0.5)
    sc.add("punch/cut", cut["punch"], TOOL, "punch", specular=0.5, shown=False)
    sc.add("punch/oring", parts["punch"]["oring"][0], DARK, "punch")
    sc.add("punch/oring_cut", cut["oring"], DARK, "punch", shown=False)
    pw_col = C.POWDERS["Al"][0]
    sc.add("cup/whole", C.cup(), C.AL_5N, "cup", specular=0.6)
    sc.add("cup/cut", C.cup(cut=True), C.AL_5N, "cup", specular=0.6, shown=False)
    sc.add("cup/point", C.drill_point_fill(cut=True), pw_col, "cup", specular=0.05, shown=False)
    sc.add("powder/col", C.unit_powder(cut=True), pw_col, "powder", specular=0.05, shown=False)
    sc.add("plug/whole", C.plug(), C.AL_5N, "plug", specular=0.6)
    sc.add("plug/cut", C.plug(cut=True), C.AL_5N, "plug", specular=0.6, shown=False)
    sc.add("plug/chan", channel_strip(), DARK, "plug")
    sc.add("plug/chan_cut", channel_strip(cut=True), DARK, "plug", shown=False)
    sc.add("hose", hose((0, 0, 300)), BRIGHT, "vp", specular=0.4)
    sc.add("air", pv.PolyData(np.zeros((30, 3))), (0.35, 0.65, 0.95), "vp", shown=False, style="points",
           point_size=5.0, render_points_as_spheres=True)
    for g in ("guard", "ram", "shuttle", "ejector"):
        sc.parent[g] = "vp"
    sc.parent.update(pin="shuttle", cup="pin", powder="cup", plug="cup", punch="shuttle")

    st = dict(guard=0.0, y=AXY, s=0.0, e=0.0, x=0.0, punch_up=200.0, cup_up=0.0, plug_up=0.0, mbar=1013.0, load=0.0,
              loaded=False, cutaway=False, rel=model["rel_density_before"])
    h0 = PLUG_SET - C.FLOOR_Z - 0.05

    def apply():
        sc.gmat["guard"] = T((0, 0, st["guard"] * GUARD_OPEN))
        sc.gmat["ram"] = T((0, 0, st["s"]))
        sc.gmat["shuttle"] = T((AXX, st["y"], Z_PISTON + st["s"]))
        sc.gmat["pin"] = T((0, 0, st["e"]))
        sc.gmat["ejector"] = T((AXX, Y_OUT, Z_PISTON + st["e"]))
        sc.gmat["cup"] = T((0, 0, CUP_BASE + st["cup_up"]))
        sc.gmat["plug"] = T((0, 0, PLUG_SET - st["x"] + st["plug_up"]))
        sc.gmat["powder"] = T((0, 0, C.FLOOR_Z + 0.05)) @ S((1, 1, h0 - st["x"]))
        sc.gmat["punch"] = T((0, 0, PUNCH_SET - st["x"] + st["punch_up"]))
        on = st["loaded"]
        for n in ("cup/whole", "plug/whole", "plug/chan"):
            sc.alpha[n] = 1.0 if on and not st["cutaway"] else 0.0
        for n in ("cup/cut", "plug/cut", "plug/chan_cut", "cup/point", "powder/col"):
            sc.alpha[n] = 1.0 if on and st["cutaway"] else 0.0
        for whole, half in (("sh/body", "sh/body_cut"), ("sh/f1", "sh/f1_cut"), ("sh/catch", "sh/catch_cut"),
                            ("punch/whole", "punch/cut"), ("punch/oring", "punch/oring_cut")):
            sc.alpha[whole] = 0.0 if st["cutaway"] else 1.0
            sc.alpha[half] = 1.0 if st["cutaway"] else 0.0
        sc.alpha["sh/hole"] = 1.0 if st["cutaway"] else 0.0
        if st["plug_up"] > 150:
            for n in ("plug/whole", "plug/cut", "plug/chan", "plug/chan_cut"):
                sc.alpha[n] = 0.0
        sc.alpha["pin/pin"] = 0.0 if st["cutaway"] else 1.0
        sc.alpha["pin/cut"] = 1.0 if st["cutaway"] else 0.0
        if st["punch_up"] > 150:
            sc.alpha["punch/whole"] = sc.alpha["punch/cut"] = sc.alpha["punch/oring"] = sc.alpha["punch/oring_cut"] = 0.0
        k = (st["rel"] - model["rel_density_before"]) / (model["rel_density_after"] - model["rel_density_before"])
        sc.color["powder/col"] = tuple(c * (1 - 0.22 * k) for c in pw_col)
        port = (sc.world("shuttle") @ np.r_[VP["port_local"], 1.0])[:3]
        sc.set_mesh("hose", hose(port))
        gauges()

    def gauges():
        g = "open" if st["guard"] > 0.5 else "closed"
        sc.gauges = [("Press", f"{AT['model'][:27]}, guard {g}"),
                     ("Load", f"{st['load']:4.1f} t  {st['load'] * G:5.1f} kN   set point {set_t:.1f} t"),
                     ("Vacuum", f"{st['mbar']:7.1f} mbar (Pirani)" if st["mbar"] >= 1 else f"{st['mbar']:7.2f} mbar"),
                     ("Plug", "not set" if not st["loaded"] or st["plug_up"] > 0.5 else
                      (f"{TRAVEL - st['x']:.1f} mm proud" if TRAVEL - st["x"] > 0.05 else "flush")),
                     ("Powder", f"{model['mass_g']:.2f} g AlSi10Mg, {100 * st['rel']:.0f} % dense")]

    def to(**kw):
        start = {k: st[k] for k in kw}

        def up(u):
            for k, v in kw.items():
                st[k] = start[k] + (v - start[k]) * u
            apply()
        return up

    def air(u, out=True):
        """Air leaving the cup: up the vent, along the plug's channel, out of the port and down the hose."""
        cup = sc.world("cup")
        top = PLUG_SET - st["x"] + C.PLUG_L + 0.3
        path = [(0, 0, PLUG_SET - 12), (0, 0, top), (0, C.CUP_BORE_D / 2 - 0.5, top), (-3.0, 7.6, C.SLUG_L + 1.5),
                (-RING_D / 2 + 0.6, 0, PORT_Z - CUP_BASE), (-BODY_R - 18, 0, PORT_Z - CUP_BASE)]
        P = [(cup @ np.r_[p, 1.0])[:3] for p in path]
        line = hose_line((sc.world("shuttle") @ np.r_[VP["port_local"], 1.0])[:3])
        P += [np.asarray(q) for q in line.points[4::8]]
        k = np.arange(30)
        s = (k / 30 + u * 2.5) % 1.0
        seg = np.minimum((s * (len(P) - 1)).astype(int), len(P) - 2)
        f = s * (len(P) - 1) - seg
        pts = np.array([P[i] + (P[i + 1] - P[i]) * t for i, t in zip(seg, f)])
        sc.set_mesh("air", pv.PolyData(pts))

    apply()
    wide = [(-820.0, -1650.0, 900.0), (-150.0, -120.0, 300.0), (0, 0, 1)]
    out_c = np.array([AXX, Y_OUT, Z_PISTON + 80.0])
    in_c = np.array([AXX, AXY, Z_PISTON + 80.0])
    cam_out = [tuple(out_c + (230.0, -520.0, 190.0)), tuple(out_c + (0, 0, 10.0)), (0, 0, 1)]
    cam_in = [tuple(in_c + (200.0, -560.0, 150.0)), tuple(in_c + (0, 0, 10.0)), (0, 0, 1)]
    cam_load = [tuple(out_c + (420.0, -900.0, 380.0)), tuple(out_c + (0, 80.0, 60.0)), (0, 0, 1)]
    top_in = np.array([AXX, AXY, Z_PISTON + CUP_BASE + 50.0])
    cam_press = [tuple(top_in + (95.0, -270.0, 50.0)), tuple(top_in + (0, 0, 2.0)), (0, 0, 1)]
    sc.cam = list(wide)
    n = 9

    cap = ("A Specac Atlas Autotouch 15T: an automatic hydraulic press, 425 x 405 x 640 mm. Our evacuable die, built "
           "round #222's steel sleeve F1, rides on a shuttle in front of it. A pump, two valves and a gauge make the vacuum.")
    sc.step(f"1/{n}", cap, 1.5, None, hold=2.6, labels=[
        ("touchscreen: programs of load, hold, release", (TOWER_X[0] + 66, -170, 420), (0.86, 0.20)),
        ("clear guard, interlocked", (AXX + 60, AXY - 160, 330), (0.80, 0.42)),
        ("leadscrew, set once for the die", (AXX, AXY, Z_XHEAD - 6), (0.62, 0.12)),
        ("our die and shuttle", (AXX - 50, Y_OUT, Z_PISTON + 100), (0.12, 0.60)),
        ("vacuum pump", (-480, 10, 190), (0.10, 0.30)),
        ("valves V1, V2 and Pirani gauge", (BLOCK[0], BLOCK[1], BLOCK[2] - 40), (0.12, 0.80))])

    cap = "The guard slides up. The shuttle brings the die out of the press, to the arm."
    sc.step(f"2/{n}", cap, 1.4, to(guard=1.0), hold=0.1)
    sc.step(f"2/{n}", cap, 1.6, to(y=Y_OUT), hold=0.3, cam_to=cam_load)

    cap = (f"Cut open. The ejector raises its pin. The arm sets a dosed cup in the die's mouth, on the pin: a catch "
           f"ring on F1 holds its bottom {CATCH:.0f} mm, so it stands in a socket, not on a bare pin. 9.61 g of "
           f"AlSi10Mg, tapped up to where the plug will stand. The pin lowers the cup into F1.")
    st["cutaway"] = True
    ring_lbl = [("catch ring: Ø19.30 on the 19.05 mm cup, 30° lead-in", (AXX - 14, Y_OUT, Z_PISTON + BODY_TOP - 4),
                 (0.10, 0.55)),
                ("F1, #222's sleeve", (AXX - 14, Y_OUT, Z_PISTON + CUP_BASE + 30), (0.10, 0.80)),
                ("ejector pin", (AXX - 6, Y_OUT, Z_PISTON + 18), (0.60, 0.78))]
    sc.step(f"3/{n}", cap, 1.2, to(e=VP["eject"]), hold=0.1, cam_to=cam_out)
    st.update(loaded=True, cup_up=110.0, plug_up=200.0)
    sc.step(f"3/{n}", cap, 1.0, to(cup_up=0.0), hold=1.2, labels=ring_lbl)
    sc.step(f"3/{n}", cap, 1.5, to(e=0.0), hold=0.3)
    cap = ("The arm sets the plug in the mouth, on its lead-in, 8.0 mm proud. Then the punch: the O-ring on its nose "
           "seals in the catch ring, and the channel across the plug's top (DAL #156) keeps the vent open under it.")
    sc.step(f"4/{n}", cap, 1.3, to(plug_up=0.0), hold=0.2)
    sc.step(f"4/{n}", cap, 1.6, to(punch_up=0.0), hold=0.6)

    cap = "The shuttle slides in under the leadscrew. The guard closes: the press will not start with it open."
    sc.step(f"5/{n}", cap, 1.6, to(y=AXY), hold=0.1, cam_to=cam_in)
    sc.step(f"5/{n}", cap, 1.2, to(guard=0.0), hold=0.3)

    cap = ("V1 opens to the pump, slowly at first through the needle valve, so the powder stays put. Air leaves the "
           "cup through the vent and out of the port. Hold 2 min under 1 mbar.")
    sc.alpha["air"] = 1.0

    def pump(u):
        st["mbar"] = float(10 ** (math.log10(1013.0) + (math.log10(0.8) - math.log10(1013.0)) * min(1.0, u * 1.25)))
        apply()
        air(u)
    sc.step(f"6/{n}", cap, 4.5, pump, hold=0.4, live=False, cam_to=cam_press)
    sc.alpha["air"] = 0.0

    cap = (f"Start: program P1 pumps up to {set_t:.1f} t. The ram lifts the die {GAP:.0f} mm to the leadscrew, then "
           f"drives the plug {TRAVEL:.1f} mm to flush. The powder goes from {100 * model['rel_density_before']:.0f} to "
           f"{100 * model['rel_density_after']:.0f} % dense.")
    xs = np.array([r["x_mm"] for r in stroke])
    fs = np.array([r["total_slide_kN"] for r in stroke]) / G
    rels = np.array([r["rel_density"] for r in stroke])

    def press_up(u):
        s = VP["ram_flush"] * window(u, 0.0, 0.78)
        st["s"] = s
        x = min(TRAVEL, max(0.0, s - GAP))
        st["x"] = x
        st["rel"] = float(np.interp(x, xs, rels))
        if u <= 0.78:
            st["load"] = float(np.interp(x, xs, fs)) if s > GAP else 0.0
        else:
            st["load"] = float(fs[-1] + (set_t - fs[-1]) * window(u, 0.78, 1.0))
        apply()
    sc.step(f"7/{n}", cap, 5.5, press_up, hold=0.3)
    cap = (f"It holds {set_t:.1f} t for a minute, topping up as the powder settles. At flush the punch's collar lands "
           f"on the catch ring, so F1 under it takes the load past flush: {model['powder_t_at_flush']:.1f} t is on the "
           f"powder.")
    sc.step(f"7/{n}", cap, 2.2, None, hold=1.0)

    cap = "V1 closes. V2 lets in dry argon, back to 1013 mbar, so the pores fill with argon, not room air."
    sc.step(f"8/{n}", cap, 2.4, to(mbar=1013.0), hold=0.3, cam_to=cam_in)
    cap = "Slow release to 0 t. The ram goes down; the plug stays where it is, flush."
    sc.step(f"8/{n}", cap, 1.4, to(load=0.0), hold=0.05)
    sc.step(f"8/{n}", cap, 1.0, to(s=0.0), hold=0.2)

    cap = (f"The guard opens and the shuttle comes out. The arm lifts the punch off. The ejector pushes the cup up out "
           f"of F1 and stops with its bottom {CATCH:.0f} mm still in the catch ring, where it stands until the arm "
           f"takes it.")
    sc.step(f"9/{n}", cap, 1.2, to(guard=1.0), hold=0.05)
    sc.step(f"9/{n}", cap, 1.5, to(y=Y_OUT), hold=0.1, cam_to=cam_out)
    sc.step(f"9/{n}", cap, 1.3, to(punch_up=200.0), hold=0.1)
    sc.step(f"9/{n}", cap, 1.6, to(e=VP["eject"]), hold=0.4, labels=ring_lbl[:1])
    cap = (f"Charged: the plug flush and the powder {100 * model['rel_density_after']:.0f} % dense, pressed under "
           f"vacuum. Set point {set_t:.1f} t: {model['powder_t_at_flush']:.1f} t on the powder plus #222's 2 t "
           f"reserve for the plug's press fit. The cup waits in the catch ring for the arm.")
    st["cutaway"] = False
    apply()
    look = np.array([AXX, Y_OUT, Z_PISTON + BODY_TOP + 20.0])
    cam_end = [tuple(look + (300.0, -620.0, 260.0)), tuple(look), (0, 0, 1)]
    sc.step(f"9/{n}", cap, 1.6, None, hold=2.6, still=True, cam_to=cam_end,
            labels=[(f"catch ring: the cup's bottom {CATCH:.0f} mm stay in it", (AXX - 8, Y_OUT - 8, Z_PISTON + BODY_TOP),
                     (0.14, 0.62))])
    return sc.save()


if __name__ == "__main__":
    r = report()
    (HERE / "out").mkdir(exist_ok=True)
    path = HERE / "out" / "vacuum_press.json"
    if not (len(sys.argv) > 1 and sys.argv[1] == "numbers"):
        movie()                                   # scene.save writes the clip's frame record to the same file
        try:
            r["clip"] = json.loads(path.read_text())
        except (OSError, ValueError):
            pass
    path.write_text(json.dumps(r, indent=1) + "\n")
    print(json.dumps({k: v for k, v in r.items() if k not in ("stroke", "layout", "press")}, indent=1))
