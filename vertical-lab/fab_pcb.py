"""PCB assembly for the vertical cloud lab: a semi-automatic stencil printer and an open-source pick-and-place (#303).

Both are ``instruments.Instrument``s, rendered by ``fab_tour.py`` and laid out on tray H by ``fab_trays.py``. Frame as in
``instruments.py``: x to the right and y away from you when you face the front, z up from the tray, origin at the centre
of the footprint, millimetres. The envelopes are the makers' figures; the layout in between is read off their photos and
is approximate, as ``SPECS`` in ``instruments.py`` says for the others.
"""
from __future__ import annotations

import math

import numpy as np

from instruments import Instrument, Joint, _piece, _xcyl, _ycyl, box, cyl, hose, rbox  # noqa: F401

MATERIALS = {
    "lumen_black": (0.10, 0.10, 0.11, 1.0, 0.25),     # LumenPnP's black printed parts and anodised extrusion
    "lumen_yellow": (0.96, 0.70, 0.12, 1.0, 0.30),    # its yellow tension arms and feeder drive gears
    "extrusion_black": (0.13, 0.13, 0.14, 1.0, 0.45),  # black anodised V-slot
    "lumen_white": (0.94, 0.94, 0.92, 1.0, 0.10),     # the white diffuser rings of the top and bottom lights
    "lumen_red": (0.80, 0.12, 0.12, 1.0, 0.30),       # the red and blue Z gantry back plates (bom.json)
    "lumen_blue": (0.12, 0.35, 0.80, 1.0, 0.30),
    "lumen_hole": (0.55, 0.55, 0.55, 1.0, 0.20),      # the plates' hole grid, light against the black
    "lumen_glow": (0.95, 0.97, 1.00, 1.0, 0.10),      # the bottom ring light, lit
    "tape": (0.58, 0.58, 0.56, 1.0, 0.30),            # component tape in the feeders
    "staging": (0.07, 0.07, 0.08, 1.0, 0.45),         # the black staging-plate PCBs
    "gold": (0.85, 0.66, 0.25, 1.0, 0.85),            # their gold pads and the feeders' contacts
    "chip": (0.06, 0.06, 0.07, 1.0, 0.35),            # a moulded IC package
    "paste": (0.66, 0.67, 0.69, 1.0, 0.35),           # solder paste
    "fr4": (0.08, 0.42, 0.20, 1.0, 0.45),             # a bare green board
    "ddm_grey": (0.83, 0.84, 0.83, 1.0, 0.25),        # the stencil printer's light grey cabinet
    "ddm_blue": (0.12, 0.30, 0.60, 1.0, 0.35),
    "squeegee": (0.82, 0.83, 0.85, 1.0, 0.90),        # a stainless squeegee blade
}

# register.py's view of a model (see instruments.py): key -> (parameter dict, anchors(params, pose)); FREE[key], the
# parameters it may fit to the frames in refs/<key>/; CHECKS[key](params), numbers that must stay >= 0.
ANCHORS: dict = {}
FREE: dict = {}
CHECKS: dict = {}


# ===================================================================================================== LumenPnP
# Opulo LumenPnP v4.2, an open-source desktop pick-and-place. Every dimension of the machine is read off Opulo's own CAD,
# github.com/opulo-inc/lumenpnp at commit 64cf68d (2026-10-14): src/assembly.FCStd, a FreeCAD 1.0 assembly whose parts
# are stored as BREP in one frame, and src/CSM/*.FCStd for the plates; bom.json for the parts list. The frame is seven
# 600 mm 20 x 20 V-slot extrusions: two upper side rails carrying the 550 mm MGN12H Y rails, two lower side rails that
# carry the plates, the front and back rails carrying the 25-slot feeder "blades", and the X gantry with its 525 mm
# MGN12H rail; four printed legs on leg extensions, the front ones with the yellow Y-belt tension arms. The head: two
# nozzles on NEMA 11 hollow-shaft steppers, each on a Z gantry; one NEMA 17 (the diamond on top) drives the two Z
# gantries on one belt, counterweighted, so one nozzle goes down as the other goes up; the down-looking camera sits
# behind and between them in a white diffuser ring. The up-looking camera is under the 120 mm staging plate (its white
# ring light shows through a hole); two 75 mm build plates behind it; all three are 600 mm black powder-coated steel.
# The control box hangs under the left side; drag chains run along the left side (Y) and behind the gantry (X). The
# powered feeders are a separate Opulo design, not in this repository: their shape is read from Opulo's videos
# (refs/lumenpnp/, notes/refine_lumenpnp.md). Positions below are in the assembly's frame (x 0..600 along the
# extrusions, y back from the front rail's front face at -20, z up from the front rail's underside), converted by _lp().
LUMEN = dict(foot=101.0,                     # the floor under the leg extensions (z -100.8) and their rubber feet
             gy0=-25.0, gtravel=447.0,       # the X extrusion's centre line: y -25 (front legs) to 422 (back legs)
             hx0=81.0, htravel=438.0,        # the head's centre: x 81 (X motor mount) to 519 (X idler mount)
             drop=31.0,                      # nozzle 1 down until a part on it sits on the board
             feed_top=55.0, feed_in=74.0, feed_low=-37.0,   # the feeders' top, inner end and bottom: fitted (refs)
             n_front=10, n_back=5)
LP_C = (288.4, 232.0)                        # the envelope's centre (x -65..641.8, y -104.6..568.7) is the model's 0, 0
G0, H0 = 209.12, 443.78                      # the X extrusion's centre line and the head's centre in the assembly
NZ = ((420.08, 152.05), (467.49, 152.05))    # the two nozzle axes in the assembly
TIP_Z = 77.0                                 # the nozzle tips, head up: 34 mm over the plates
SLOT0, PITCH = 102.6, 15.8                   # the feeder blades: 25 slots from x 102.6 to 497.6


def _lp(p, x, y, z, dx=0.0, dy=0.0, dz=0.0) -> tuple:
    """A point of Opulo's assembly frame in the model's frame (shifted by dx, dy, dz first)."""
    return (x + dx - LP_C[0], y + dy - LP_C[1], z + dz + p["foot"])


def _lpbox(p, x0, y0, z0, x1, y1, z1, dx=0.0, dy=0.0, dz=0.0):
    a, b = _lp(p, x0, y0, z0, dx, dy, dz), _lp(p, x1, y1, z1, dx, dy, dz)
    return box(min(a[0], b[0]), min(a[1], b[1]), min(a[2], b[2]), max(a[0], b[0]), max(a[1], b[1]), max(a[2], b[2]))


def _lpcyl(p, d, z0, z1, x, y, dx=0.0, dy=0.0):
    c = _lp(p, x, y, z0, dx, dy)
    return cyl(d, z1 - z0, x=c[0], y=c[1], z=c[2])


def _prism(p, plane, pts, a0, a1, dx=0.0, dy=0.0, holes=()):
    """A polygon in the assembly's (y, z) or (x, z) plane, extruded along x or y from a0 to a1."""
    import cadquery as cq
    if plane == "yz":
        sh = [(y - LP_C[1] + dy, z + p["foot"]) for y, z in pts]
        w = cq.Workplane("YZ").polyline(sh).close().extrude(a1 - a0).translate((a0 + dx - LP_C[0], 0, 0))
        for h in holes:
            hs = [(y - LP_C[1] + dy, z + p["foot"]) for y, z in h]
            w = w.cut(cq.Workplane("YZ").polyline(hs).close().extrude(a1 - a0 + 2).translate((a0 + dx - LP_C[0] - 1, 0, 0)))
        return w
    sh = [(x - LP_C[0] + dx, z + p["foot"]) for x, z in pts]
    return cq.Workplane("XZ").polyline(sh).close().extrude(-(a1 - a0)).translate((0, a0 + dy - LP_C[1], 0))


def _lp_pose(p, pose=None):
    """(dx, dy, dz) of the head, the gantry and nozzle 1 from their joint values."""
    pose = pose or {}
    gy = p["gy0"] + p["gtravel"] * float(pose.get("gantry", 0.0)) - G0
    hx = p["hx0"] + p["htravel"] * float(pose.get("head", 0.0)) - H0
    return hx, gy, p["drop"] * float(pose.get("zl", 0.0))


def _slot_x(k):
    """The centre of feeder slot k (1..25) along the rails."""
    return SLOT0 + PITCH * (k - 0.5)


def lumenpnp_anchors(p, pose=None) -> dict:
    """Named points and lines of the model for register.py, from the same numbers that build it."""
    hx, gy, zd = _lp_pose(p, pose)
    P = lambda x, y, z, dx=0.0, dy=0.0, dz=0.0: _lp(p, x, y, z, dx, dy, dz)   # noqa: E731
    L = lambda a, b: ("line", a, b)                                            # noqa: E731
    a = {"FL arm top outer": P(-10, -104.6, 115.6), "FL arm top inner": P(30, -104.6, 115.6),
         "FR arm top outer": P(610, -104.6, 115.6), "FR arm top inner": P(570, -104.6, 115.6),
         "FL arm bottom outer": P(-10, -104.6, 84.5), "FR arm bottom outer": P(610, -104.6, 84.5),
         "FL arm bottom inner": P(30, -104.6, 84.5), "FR arm bottom inner": P(570, -104.6, 84.5),
         # the leg extensions are 30 mm wide, flush with the legs' outer faces
         "FL foot outer": P(-10, -83.6, -100.0), "FR foot outer": P(610, -83.6, -100.0),
         "FL foot inner": P(20, -83.6, -100.0), "FR foot inner": P(580, -83.6, -100.0),
         "FL foot inner back": P(20, -57.4, -98.5), "FR foot inner back": P(580, -57.4, -98.5),
         "FL foot back outer": P(-10, -57.4, -98.5), "FR foot back outer": P(610, -57.4, -98.5),
         "BL leg top back": P(-12.1, 566.6, 120.1), "BR leg top back": P(612.0, 566.6, 120.1),
         "BL leg top front": P(-12.1, 500.1, 119.1), "BR leg top front": P(612.0, 500.1, 119.1),
         "BL foot back": P(-12.1, 567.6, -87.2), "BR foot back": P(612.0, 567.6, -87.2),
         "plate FL": P(0, 80, 43.1), "plate FR": P(600, 80, 43.1), "plate BL": P(0, 350.3, 43.1),
         "plate BR": P(600, 350.3, 43.1),
         "camera ring": ("circle", P(120.1, 140.15, 43.1), 28.0),
         "left rail top": L(P(0, -60, 110), P(0, 500, 110)), "right rail top": L(P(600, -60, 110), P(600, 500, 110)),
         "left y rail top": L(P(9.9, -55.9, 118), P(9.9, 494.1, 118)),
         "right y rail top": L(P(590.0, -55.9, 118), P(590.0, 494.1, 118)),
         "left rail top inner": L(P(20, -60, 110), P(20, 500, 110)),
         "right rail top inner": L(P(580, -60, 110), P(580, 500, 110)),
         "left lower rail top": L(P(0, -57, 40), P(0, 500, 40)), "right lower rail top": L(P(600, -57, 40), P(600, 500, 40)),
         "left lower rail bottom": L(P(0, -57, 20), P(0, 500, 20)),
         "right lower rail bottom": L(P(600, -57, 20), P(600, 500, 20)),
         "front rail top": L(P(30, -20, 20), P(570, -20, 20)), "front rail bottom": L(P(30, -20, 0), P(570, -20, 0)),
         "back rail top": L(P(32, 430, 20), P(568, 430, 20)),
         "blade front bottom": L(P(102.6, -35.3, -34.0), P(497.6, -35.3, -34.0)),
         "front feeder 1 top front": P(_slot_x(1) - 7, -46, p["feed_top"]),
         "front feeder 25 top front": P(_slot_x(25) + 7, -46, p["feed_top"]),
         "front feeder 1 bottom front": P(_slot_x(1) - 7, -46, p["feed_low"]),
         "front feeder 25 bottom front": P(_slot_x(25) + 7, -46, p["feed_low"]),
         "back feeders top": L(P(_slot_x(1) - 7, 430 - p["feed_in"], p["feed_top"]),
                               P(_slot_x(25) + 7, 430 - p["feed_in"], p["feed_top"])),
         # the gantry, at the pose's place
         "x rail top front": L(P(40, 199, 154.8, dy=gy), P(560, 199, 154.8, dy=gy)),
         "x rail bottom front": L(P(40, 199, 134.8, dy=gy), P(560, 199, 134.8, dy=gy)),
         "x motor top left": P(-64.5, 188.1, 201.9, dy=gy), "x motor top right": P(-22.5, 188.1, 201.9, dy=gy),
         "x motor mount left": P(-65, 175.1, 164.8, dy=gy), "x idler right": P(641.7, 188.1, 163.8, dy=gy),
         "x tension arm top": P(634.2, 189.2, 159.7, dy=gy),
         "x tension arm top front left": P(627.2, 189.2, 159.7, dy=gy),
         "head motor top": P(443.78, 170.1, 239.1, dx=hx, dy=gy),
         "z motor face": P(443.78, 170.1, 212.2, dx=hx, dy=gy),
         "head plate bottom left": P(398.8, 179.1, 104.6, dx=hx, dy=gy),
         "head plate bottom right": P(488.8, 179.1, 104.6, dx=hx, dy=gy),
         "nozzle 1 tip": P(NZ[0][0], NZ[0][1], TIP_Z, dx=hx, dy=gy, dz=-zd),
         "nozzle 2 tip": P(NZ[1][0], NZ[1][1], TIP_Z, dx=hx, dy=gy, dz=zd)}
    return a


def _stretch(axis, s0, r0, s1, r1) -> tuple:
    """A follow joint's jacobian (instruments.Joint): along `axis`, the point at s0 moves r0 mm per mm of its driver
    and the point at s1 moves r1, linearly between: a drag chain's run, one end on the carriage, the other at its
    bend, which moves half as far."""
    a = (r1 - r0) / (s1 - s0)
    J = np.zeros((3, 4))
    J[axis, axis], J[axis, 3] = a, r0 - a * s0
    jac = [np.zeros((3, 4)) for _ in range(3)]
    jac[axis] = J
    return tuple(tuple(map(tuple, j)) for j in jac)


def _chain_bend(p, plane, c, R, w0, w1, sign, h=15.3):
    """The U bend of a drag chain: half an annulus of centre-line radius R about c ((y, z) or (x, z), assembly), on
    the +sign side, across w0..w1."""
    import cadquery as cq
    if plane == "yz":
        u, v = c[0] - LP_C[1], c[1] + p["foot"]
        ring = cq.Workplane("YZ").center(u, v).circle(R + h / 2).circle(R - h / 2).extrude(w1 - w0) \
            .translate((w0 - LP_C[0], 0, 0))
        cut = box(w0 - LP_C[0] - 1, u - (R + h) if sign > 0 else u, v - R - h, w1 - LP_C[0] + 1,
                  u if sign > 0 else u + R + h, v + R + h)
        return ring.cut(cut)
    u, v = c[0] - LP_C[0], c[1] + p["foot"]
    ring = cq.Workplane("XZ").center(u, v).circle(R + h / 2).circle(R - h / 2).extrude(-(w1 - w0)) \
        .translate((0, w0 - LP_C[1], 0))
    cut = box(u - (R + h) if sign > 0 else u, w0 - LP_C[1] - 1, v - R - h, u if sign > 0 else u + R + h,
              w1 - LP_C[1] + 1, v + R + h)
    return ring.cut(cut)


FRONT_LEG = [(-83.6, -100.0), (-85.1, 78.7), (-104.4, 80.0), (-104.4, 120.0), (-60.1, 120.0), (-59.4, 55.2),
             (-43.9, 40.2), (-18.6, 38.5), (-0.9, 20.0), (-0.1, 0.5), (-57.4, -98.5)]          # (y, z), with extension
FRONT_LEG_HOLES = [[(-73.1, -40.0), (-34.4, -39.8), (-18.4, -11.8), (-30.1, -8.0), (-32.1, 15.0), (-75.1, 13.0)],
                   [(-73.6, -90.0), (-63.4, -88.8), (-47.9, -60.0), (-75.1, -61.5)]]
BACK_LEG = [(504.1, -99.9), (500.1, -95.9), (500.1, 119.1), (566.6, 120.1), (568.1, 81.6), (525.3, 80.1),
            (525.1, 41.6), (526.1, 16.6), (567.8, -25.4), (567.6, -87.2), (541.3, -98.4)]
BACK_LEG_HOLES = [[(553.3, -32.7), (554.3, -25.7), (517.3, 11.1), (512.1, 10.6), (510.8, -37.7), (528.1, -39.2)],
                  [(510.8, -87.7), (532.3, -89.4), (555.3, -82.2), (557.1, -57.7), (551.6, -55.4), (512.3, -60.7)]]
Y_GANTRY = [(174.1, 86.6), (174.1, 129.6), (179.1, 134.6), (280.6, 134.6), (285.6, 129.6), (285.6, 122.9),
            (244.1, 122.6), (242.1, 84.6)]                                                      # (y, z)
X_MOTOR_MOUNT = [(-65.0, 154.8), (-65.0, 164.8), (31.0, 164.8), (36.0, 158.8), (36.0, 133.8), (-11.7, 132.8),
                 (-12.0, 93.8), (-24.0, 93.8), (-22.0, 134.5)]                                  # (x, z)
X_IDLER_MOUNT = [(624.7, 94.0), (612.2, 93.8), (612.0, 132.8), (564.2, 133.8), (565.2, 164.8), (641.7, 163.8),
                 (641.7, 124.8), (622.2, 124.5)]
HEAD_PLATE = [(398.8, 104.6), (398.8, 197.3), (425.0, 224.0), (462.5, 224.0), (488.8, 197.3), (488.8, 104.6),
              (479.5, 94.1), (408.0, 94.1)]                                                     # (x, z), the front plate


def lumenpnp() -> Instrument:
    import cadquery as cq
    p = LUMEN
    W, D, H = 707.0, 673.0, 342.0
    inst = Instrument("lumenpnp", "Pick-and-place, open source", "Opulo LumenPnP v4.2", (W, D, H),
                      "Opulo's CAD (github.com/opulo-inc/lumenpnp at 64cf68d: src/assembly.FCStd, src/CSM plates, "
                      "bom.json): seven 600 mm V-slot extrusions, two nozzles, top and bottom vision; the powered "
                      "feeders from Opulo's videos; checked against them with register.py (refs/lumenpnp/)")
    inst.notes = ["707 x 673 x 342 mm is the envelope of Opulo's own assembly (src/assembly.FCStd at 64cf68d): legs "
                  "and their extensions, the X motor and control box on the left, the X idler on the right; the "
                  "nozzle tubes loop about 40 mm higher.",
                  "Work area 360 x 270 mm (Opulo's v4 video); boards up to 225 x 400 mm (DESIGN_DECISIONS.md).",
                  "Open hardware: the CAD is FreeCAD, the firmware Marlin, driven by OpenPnP. Its vacuum pumps are in "
                  "the control box, so it needs no compressed air."]
    hx0, gy0 = p["hx0"] - H0, p["gy0"] - G0           # the head and the gantry are modelled at the front left
    B = lambda *a, **k: _lpbox(p, *a, **k)            # noqa: E731
    body = _piece(inst, "body")
    # ---- the frame: legs, extrusions, Y rails
    for x0, x1 in ((-10.0, 30.0), (570.0, 610.0)):
        leg = _prism(p, "yz", FRONT_LEG, x0, x1, holes=FRONT_LEG_HOLES)
        xi = x1 - 10 if x0 < 0 else x0                  # the extension is 30 mm wide, flush with the outer face
        leg = leg.cut(B(xi, -110, -102, xi + 10, 0, -50))
        body.add(f"front leg {x0:+.0f}", leg, "lumen_black")
        body.add(f"tension arm {x0:+.0f}", B(x0, -104.6, 84.5, x1, -90.6, 115.6), "lumen_yellow")
    for x0, x1 in ((-12.1, 31.9), (568.0, 612.0)):
        body.add(f"back leg {x0:+.0f}", _prism(p, "yz", BACK_LEG, x0, x1, holes=BACK_LEG_HOLES), "lumen_black")
        body.add(f"y motor {x0:+.0f}", B(x0 + 1, 525.5, 50.0, x1 - 1, 567.5, 79.0), "inst_dark")
    for x0 in (0.0, 580.0):
        body.add(f"upper side rail {x0:.0f}", B(x0, -80, 90, x0 + 20, 520, 110), "extrusion_black")
        body.add(f"lower side rail {x0:.0f}", B(x0, -80, 20, x0 + 20, 520, 40), "extrusion_black")
        body.add(f"y rail {x0:.0f}", B(x0 + 3.9, -55.9, 110, x0 + 15.9, 494.1, 118), "steel")
    for y0 in (-20.0, 430.0):
        body.add(f"cross rail {y0:.0f}", B(0, y0, 0, 600, y0 + 20, 20), "extrusion_black")
    body.add("y limit striker", B(-16, -85.1, 73.2, 11, -60.1, 135.4), "lumen_black")
    body.add("thumb screw", _lpcyl(p, 14, 135.4, 149.4, 4.2, -64.1), "lumen_yellow")
    # ---- the feeder blades: 25 slots on each of the front and back rails, the slot PCBs hanging below
    for side, (yb0, yb1, ytop, ybot) in {"front": (-27.7, 5.4, -17.8, -35.3),
                                         "back": (424.6, 457.6, 447.7, 465.2)}.items():
        body.add(f"{side} blade", B(102.6, yb0, -24.6, 497.6, yb1, 0), "lumen_black")
        # the slot PCB slopes out and down from under the rail, its face (25 numbered gold contacts) up and outwards
        d = np.array([ybot - ytop, -34.0 + 8.6])
        n = np.array([d[1], -d[0]]) / np.linalg.norm(d)
        n = n if n[1] > 0 else -n                        # the face's normal, (y, z): outwards and up

        def strip(f0, f1, off, t):
            a = np.array([ytop, -8.6]) + (np.array([ybot, -34.0]) - np.array([ytop, -8.6])) * f0
            b = np.array([ytop, -8.6]) + (np.array([ybot, -34.0]) - np.array([ytop, -8.6])) * f1
            return [tuple(a + n * off), tuple(b + n * off), tuple(b + n * (off + t)), tuple(a + n * (off + t))]
        body.add(f"{side} blade PCB", _prism(p, "yz", strip(0.0, 1.0, -1.6, 1.6), 102.6, 497.6), "staging")
        for k in range(1, 26):
            x = _slot_x(k)
            body.add(f"{side} slot {k}", _prism(p, "yz", strip(0.15, 0.55, 0.0, 0.4), x - 3.4, x + 3.4), "gold")
    # ---- the plates: the staging plate (up-looking camera) and two build plates, black steel with a hole grid
    for (y0, y1), name in (((80.0, 200.0), "staging plate"), ((200.3, 275.0), "build plate 1"),
                           ((275.3, 350.3), "build plate 2")):
        plate = B(0, y0, 40.1, 600, y1, 43.1)
        if name == "staging plate":
            plate = plate.cut(_lpcyl(p, 56, 39, 44, 120.1, 140.15))
        body.add(name, plate, "staging")
        pts = [_lp(p, 12.5 + 25 * i, y, 43.1)[:2] for i in range(24)
               for y in np.arange(y0 + 12.5, y1 - 5, 25.0)
               if not (name == "staging plate" and math.hypot(12.5 + 25 * i - 120.1, y - 140.15) < 40)]
        body.add(f"{name} holes", cq.Workplane("XY").pushPoints(pts).circle(1.7).extrude(0.25)
                 .translate((0, 0, 43.1 + p["foot"])), "lumen_hole")
    body.add("bottom light", _lpcyl(p, 70, 31.9, 39.9, 120.05, 140.15).cut(_lpcyl(p, 18, 31, 41, 120.05, 140.15)),
             "lumen_white")
    body.add("bottom camera lens", _lpcyl(p, 18, 33.0, 34.0, 120.05, 140.15), "inst_black")
    body.add("bottom vision cover", B(82.5, 102.6, -5.0, 157.5, 177.6, 31.9)
             .cut(_lpcyl(p, 72, 20, 33, 120.05, 140.15)), "lumen_black")
    body.add("discard bin", B(150.6, 115.8, 43.1, 179.1, 164.3, 52.1).cut(B(153, 118, 45, 176.7, 162, 53)), "lumen_black")
    body.add("calibration fiducial mount", B(67.8, 84.0, 43.1, 172.0, 106.0, 50.0), "lumen_black")
    body.add("calibration fiducial", _lpcyl(p, 6, 50.0, 50.4, 82.0, 95.0), "inst_white")
    body.add("nozzle rack", B(54.7, 116.9, 43.2, 74.7, 192.9, 73.2), "lumen_black")
    for i in range(6):
        body.add(f"spare nozzle {i + 1}", _lpcyl(p, 6, 73.2, 78.0, 64.7, 125.0 + 12.5 * i), "steel")
    # ---- the control box under the left side, its pneumatics inside; the Y drag chain's fixed end
    body.add("control box", B(-63.0, 30.0, -80.0, 0.8, 244.0, 40.0), "lumen_black")
    body.add("control box lid", B(-65.1, 28.3, -78.0, -63.0, 245.6, 38.0), "inst_dark")
    body.add("y chain end", B(-55.0, 37.3, 40.0, -16.0, 76.3, 59.5), "lumen_black")
    # ---- the powered feeders on the front and back rails (n_front from slot 1, n_back from slot 1)
    ft, fi, fl = p["feed_top"], p["feed_in"], p["feed_low"]
    for side, n in (("front", p["n_front"]), ("back", p["n_back"])):
        for k in range(1, n + 1):
            x = _slot_x(k)
            m = (lambda y: y) if side == "front" else (lambda y: 430.0 - y)     # the back ones mirror the front ones
            Bm = lambda x0, y0, z0, x1, y1, z1: B(x0, m(y0), z0, x1, m(y1), z1)   # noqa: E731
            f = Bm(x - 7, -46, ft - 16, x + 7, fi, ft).union(Bm(x - 7, -46, fl, x + 7, -22, ft - 16)) \
                .union(Bm(x - 7, -22, fl + 12, x + 7, -8, -26))
            f = f.cut(Bm(x - 3, fi - 14, ft - 3, x + 3, fi - 6, ft + 1))                # the pick window
            body.add(f"{side} feeder {k}", f, "lumen_black")
            g = _lp(p, x, m(-46), fl + 26)
            body.add(f"{side} feeder {k} drive", (_ycyl(12, 8, x=g[0], y=g[1] - 8, z=g[2]) if side == "front" else
                                                  _ycyl(12, 8, x=g[0], y=g[1], z=g[2])), "lumen_yellow")
            body.add(f"{side} feeder {k} tab", Bm(x - 4, -48, fl - 6, x + 4, -44, fl), "lumen_yellow")
            body.add(f"{side} feeder {k} tape", Bm(x - 4, -40, ft, x + 4, fi - 16, ft + 0.3), "tape")
    # ---- the gantry: the X extrusion and its rail on the two Y gantries, the X motor and idler mounts
    gantry = _piece(inst, "gantry")
    G = lambda *a: _lpbox(p, *a, dy=gy0)              # noqa: E731
    gantry.add("x extrusion", G(0, 199.1, 134.8, 600, 219.1, 154.8), "extrusion_black")
    gantry.add("x rail", G(37.6, 203.1, 154.8, 562.6, 215.1, 162.8), "steel")
    for x0, x1, xc in ((-12.0, 26.9, 9.9), (573.3, 612.2, 590.0)):
        gantry.add(f"y gantry {xc:.0f}", _prism(p, "yz", Y_GANTRY, x0, x1, dy=gy0), "lumen_black")
        gantry.add(f"y carriage {xc:.0f}", G(xc - 13.5, 186.1, 110.0, xc + 13.5, 232.1, 123.0), "steel")
    gantry.add("x motor mount", _prism(p, "xz", X_MOTOR_MOUNT, 175.1, 230.6, dy=gy0), "lumen_black")
    gantry.add("x motor", G(-64.5, 188.1, 164.8, -22.5, 230.1, 201.9), "inst_dark")
    gantry.add("x idler mount", _prism(p, "xz", X_IDLER_MOUNT, 188.1, 230.1, dy=gy0), "lumen_black")
    gantry.add("x tension arm", G(627.2, 189.2, 128.7, 641.2, 229.2, 159.7), "lumen_yellow")
    gantry.add("x chain support", G(-64.1, 235.6, 134.8, 599.9, 280.1, 137.8), "inst_dark")
    gantry.add("x chain end", G(1.9, 245.6, 137.8, 40.9, 284.6, 157.3), "lumen_black")
    gantry.add("y chain moving end", G(-55.0, 236.3, 137.8, -16.0, 275.3, 157.3), "lumen_black")
    # ---- the head: front plate, carriage block, the Z motor (the diamond), the camera's white diffuser, cable splay
    head = _piece(inst, "head")
    Hh = lambda *a: _lpbox(p, *a, dx=hx0, dy=gy0)     # noqa: E731
    head.add("head plate", _prism(p, "xz", HEAD_PLATE, 179.1, 194.7, dx=hx0, dy=gy0), "lumen_black")
    head.add("head carriage", Hh(398.8, 194.1, 103.1, 488.8, 234.1, 183.6), "lumen_black")
    c = _lp(p, H0, 170.1, 212.2, hx0, gy0)
    zmot = cq.Workplane("XZ").rect(38.0, 38.0).extrude(-61.0).edges("|Y").chamfer(4.0) \
        .rotate((0, 0, 0), (0, 1, 0), 45).translate(c)
    head.add("z motor", zmot, "inst_dark")
    head.add("top light diffuser", Hh(410.0, 195.0, 103.1, 477.0, 246.0, 117.0), "lumen_white")
    tc = _lp(p, 443.77, 215.17, 102.6, hx0, gy0)
    head.add("top camera lens", cyl(16, 0.6, x=tc[0], y=tc[1], z=tc[2]), "inst_black")
    head.add("cable splay", Hh(419.5, 228.9, 167.8, 489.0, 284.4, 241.1), "lumen_black")
    head.add("x carriage", Hh(420.8, 195.6, 162.8, 466.8, 222.6, 167.8), "steel")
    head.add("x chain moving end", Hh(469.8, 245.6, 197.4, 508.8, 284.6, 216.9), "lumen_black")
    # the two Z gantries, each with its NEMA 11, rotary union, nozzle holder, camera mask and tube; the left one
    # (red back plate) carries nozzle 1, the right one (blue) nozzle 2
    for side, (nx, ny), plate_x, col, tube in (("zl", NZ[0], (412.8, 442.8), "lumen_red", "inst_red"),
                                                ("zr", NZ[1], (444.9, 482.0), "lumen_blue", "inst_blue")):
        z = _piece(inst, side)
        Z = lambda *a: _lpbox(p, *a, dx=hx0, dy=gy0)    # noqa: E731
        z.add("z gantry", Z(nx - 19.5, 166.2, 118.1, nx + 19.5, 171.2, 160.6), "lumen_black")
        z.add("back plate", Z(plate_x[0], 171.2, 130.6, plate_x[1], 179.0, 165.6), col)
        z.add("nema 11", Z(nx - 14.1, ny - 14.1, 118.0, nx + 14.1, ny + 14.1, 160.0), "inst_dark")
        z.add("nema 11 cap", Z(nx - 13.0, ny - 13.0, 160.0, nx + 13.0, ny + 13.0, 166.6), "lumen_black")
        z.add("rotary union", _lpcyl(p, 12.8, 166.6, 207.2, nx, ny, hx0, gy0), "aluminium")
        z.add("camera mask", _lpcyl(p, 42, 106.7, 110.7, nx, ny, hx0, gy0), "inst_dark")
        z.add("nozzle holder", _lpcyl(p, 10, 88.3, 118.0, nx, ny, hx0, gy0), "brass")
        a0 = _lp(p, nx, ny, 207.2, hx0, gy0)
        s = -1 if side == "zl" else 1
        z.add("tube", hose([a0, (a0[0], a0[1], a0[2] + 30), (a0[0] + 10 * s, a0[1] + 25, a0[2] + 55),
                            (a0[0] + 18 * s, a0[1] + 75, a0[2] + 40)], 4.0), tube)
        if side == "zr":
            z.add("nozzle 2 tip", _lpcyl(p, 5, TIP_Z, 88.3, nx, ny, hx0, gy0), "steel")
    tip = _piece(inst, "tip")
    t1 = _lp(p, NZ[0][0], NZ[0][1], TIP_Z, hx0, gy0)
    tip.add("nozzle 1 tip", cyl(5, 88.3 - TIP_Z, x=t1[0], y=t1[1], z=t1[2]), "steel")
    part = _piece(inst, "part")
    part.add("part on the nozzle", box(t1[0] - 3, t1[1] - 3, t1[2] - 1.2, t1[0] + 3, t1[1] + 3, t1[2]), "chip")
    part.add("pin 1 dot", cyl(1.2, 0.2, x=t1[0] + 1.8, y=t1[1] + 1.8, z=t1[2] - 1.3), "inst_white")
    # ---- the drag chains: one end fixed, the other on the carriage, the bend moving half as far (follow joints)
    def chain(name, plane, parent, fixed, moving, bend, R, lo, hi, w0, w1):
        """fixed/moving: the run ends' coordinate along the chain at the modelled position; bend: the U's centre
        line coordinate; lo/hi: the lower and upper runs' centre heights (assembly z); w0..w1 its width."""
        ax = 1 if plane == "yz" else 0
        o = LP_C[ax]
        if plane == "yz":
            low = B(w0, fixed, lo - 7.65, w1, bend, lo + 7.65)
            up = B(w0, moving, hi - 7.65, w1, bend, hi + 7.65)
        else:
            low = B(fixed, w0, lo - 7.65, bend, w1, lo + 7.65, dy=gy0)
            up = B(moving, w0, hi - 7.65, bend, w1, hi + 7.65, dy=gy0)
        if plane == "yz":
            bend_s = _chain_bend(p, "yz", (bend, (lo + hi) / 2), (hi - lo) / 2, w0, w1, 1)
        else:
            bend_s = _chain_bend(p, "xz", (bend, (lo + hi) / 2), (hi - lo) / 2, w0 + gy0, w1 + gy0, 1)
        _piece(inst, name + " low").add(name + " lower run", low, "lumen_black")
        _piece(inst, name + " up").add(name + " upper run", up, "lumen_black")
        _piece(inst, name + " bend").add(name + " bend", bend_s, "lumen_black")
        return {name + " low": _stretch(ax, fixed - o, 0.0, bend - o, 0.5),
                name + " up": _stretch(ax, moving - o, 1.0, bend - o, 0.5),
                name + " bend": _stretch(ax, bend - o, 0.5, bend - o + 1.0, 0.5)}
    yfix, ymov = 76.3, 255.8 + gy0                    # the Y chain: fixed at the front left, moving end on the gantry
    ybend = 403.5 + gy0 / 2
    yj = chain("ychain", "yz", None, yfix, ymov + 19.5, ybend, 49.0, 49.5, 147.5, -51.0, -20.0)
    xfix, xmov = 40.9, 469.8 + hx0                    # the X chain: fixed at the gantry's left end, moving end on the head
    xbend = 566.0 + hx0 / 2
    xj = chain("xchain", "xz", "gantry", xfix, xmov, xbend, 33.0, 149.45, 215.5, 244.9, 285.3)
    # ---- the board and the parts
    board = _piece(inst, "load")
    bx0, by0, bx1, by1 = 250.0, 235.0, 350.0, 305.0
    board.add("board", B(bx0, by0, 43.1, bx1, by1, 44.7), "fr4")
    for i in range(8):
        board.add(f"paste {i}", B(bx0 + 14 + 10 * i, by0 + 12, 44.7, bx0 + 18 + 10 * i, by1 - 12, 44.8), "paste")
    fids = ((bx0 + 5.0, by0 + 5.0), (bx1 - 5.0, by1 - 5.0))
    for i, (fx, fy) in enumerate(fids):
        board.add(f"fiducial {i + 1}", _lpcyl(p, 2.0, 44.7, 44.8, fx, fy), "gold")
    for i, (cx, cy) in enumerate(((bx0 - 4, (by0 + by1) / 2), (bx1 + 4, (by0 + by1) / 2), ((bx0 + bx1) / 2, by0 - 4),
                                  ((bx0 + bx1) / 2, by1 + 4))):
        board.add(f"board mount {i + 1}", B(cx - 6, cy - 6, 43.1, cx + 6, cy + 6, 49.0), "lumen_white")
    chips = {"chip1": (275.0, 255.0), "chip2": (300.0, 285.0), "chip3": (328.0, 262.0)}
    for name, (cx, cy) in chips.items():
        q = _lp(p, cx, cy, 44.8)
        _piece(inst, name).add(name, box(q[0] - 3, q[1] - 3, q[2], q[0] + 3, q[1] + 3, q[2] + 1.2), "chip") \
            .add(name + " pin 1", cyl(1.2, 0.2, x=q[0] + 1.8, y=q[1] - 1.8, z=q[2] + 1.2), "inst_white")
    glow = _piece(inst, "glow")
    glow.add("bottom ring light on", _lpcyl(p, 56, 40.0, 40.6, 120.05, 140.15)
             .cut(_lpcyl(p, 18, 39, 41, 120.05, 140.15)), "lumen_glow")

    # where nozzle 1 goes, as joint values (gantry, head), and how far it drops
    def at(x, y):
        return (round((x - NZ[0][0] + H0 - p["hx0"]) / p["htravel"], 4),
                round((y - NZ[0][1] + G0 - p["gy0"]) / p["gtravel"], 4))

    def cam_at(x, y):                                 # the top camera over (x, y)
        return (round((x - 443.77 + H0 - p["hx0"]) / p["htravel"], 4),
                round((y - 215.17 + G0 - p["gy0"]) / p["gtravel"], 4))
    feeds = {"chip1": at(_slot_x(2), 65.0), "chip2": at(_slot_x(5), 65.0), "chip3": at(_slot_x(3), 430.0 - 65.0)}
    camv = at(120.05, 140.15)
    place = {k: at(*xy) for k, xy in chips.items()}
    v_feed = (TIP_Z - (p["feed_top"] - 0.5)) / p["drop"]
    v_cam = 0.30
    inst.joints = {
        "gantry": Joint("slide", vec=(0, p["gtravel"], 0), v0=0.5),
        "head": Joint("slide", vec=(p["htravel"], 0, 0), parent="gantry", v0=0.5),
        "zl": Joint("slide", vec=(0, 0, -p["drop"]), parent="head"),
        "zr": Joint("slide", vec=(0, 0, p["drop"]), parent="head"),
        "tip": Joint("spin", axis=(0, 0, 1), pivot=(t1[0], t1[1], 0), deg=-90.0, parent="zl"),
        "part": Joint("fade", parent="tip"),
        "glow": Joint("fade"),
        "load": Joint("path", path=((0, -700, 380), (0, -250, 300), (0, 0, 120), (0, 0, 0))),
        **{k: Joint("fade", parent="load") for k in chips},
        **{k: Joint("follow", vec=(0, p["gtravel"], 0), jac=j, v0=0.5) for k, j in yj.items()},
        **{k: Joint("follow", vec=(p["htravel"], 0, 0), jac=j, parent="gantry", v0=0.5) for k, j in xj.items()},
    }

    def go(hv, gv):
        return {"head": (None, hv), "gantry": (None, gv), **{k: (None, gv) for k in yj}, **{k: (None, hv) for k in xj}}

    def z(v0, v1):
        return {"zl": (v0, v1), "zr": (v0, v1)}
    home = (0.62, 0.95)
    acts = [("Opulo's LumenPnP v4.2, built to Opulo's own CAD. A pasted board goes onto the build plate, between the "
             "board mounts.", 2.2, {"load": (0.0, 1.0), **go(*home)}),
            ("The top camera finds the board's two fiducials.", 1.2, go(*cam_at(*fids[0]))),
            ("", 0.8, go(*cam_at(*fids[1])))]
    for i, k in enumerate(chips):
        first = i == 0
        acts += [
            ("Nozzle 1 to a feeder's pick window (front and back rails, 25 slots each)." if first else
             ("" if i == 1 else "The third part from a feeder on the back rail."), 1.3 if first else 0.9, go(*feeds[k])),
            ("One Z motor drives both nozzles on one belt: as nozzle 1 goes down, nozzle 2 goes up. Vacuum picks the "
             "part." if first else "", 1.0 if first else 0.5, {**z(0.0, v_feed), "part": (0.0, 1.0)}),
            ("", 0.4, z(v_feed, 0.0)),
            ("Over the up-looking camera, its ring light on: it measures the part's offset and angle, and the "
             "nozzle turns it square." if first else "", 1.3 if first else 0.8, go(*camv)),
            ("", 0.9 if first else 0.6, {**z(0.0, v_cam), "glow": (0.0, 1.0), "tip": (0.0, 1.0)}),
            ("", 0.3, {**z(v_cam, 0.0), "glow": (1.0, 0.0)}),
            ("To its place, found from the fiducials; down, and the vacuum lets go." if first else "",
             1.3 if first else 0.8, go(*place[k])),
            ("", 0.6 if first else 0.5, {**z(0.0, 1.0), "part": (1.0, 0.0), k: (0.0, 1.0)}),
            ("", 0.4, {**z(1.0, 0.0), "tip": (1.0, 0.0)}),       # the nozzle turns back, empty
        ]
    # the head goes home first: lifting out under it, the board ran through the nozzle holder, the camera mask and
    # the Z motor (collide.py)
    acts += [("Three parts placed; the head goes home and the board goes on to reflow.", 0.8, go(*home)),
             ("", 1.6, {"load": (1.0, 0.0)})]
    inst.actions = acts
    inst.labels = [("two nozzles, counterweighted Z", _lp(p, H0, 160.0, 200.0, hx0 + 0.5 * p["htravel"],
                                                           gy0 + 0.5 * p["gtravel"]), (0.20, 0.16)),
                   ("powered feeders", _lp(p, _slot_x(1) - 7, -46, 20.0), (0.12, 0.70)),
                   ("up-looking camera", _lp(p, 120.05, 140.15, 43.1), (0.30, 0.86)),
                   ("feeder rail, 25 slots", _lp(p, 497.6, -35.3, -30.0), (0.80, 0.86))]
    inst.anchors = lumenpnp_anchors(p, {"gantry": 0.0, "head": 0.0})
    inst.cam = (0.9, -1.6, 1.05)
    # in close for the first part (feeder, up-looking camera, board: the nozzle moves only 20-30 mm), out for the rest
    inst.zoom = {3: (_lp(p, 210.0, 150.0, 60.0), 760.0), 12: "out"}
    return inst


# register.py: the LumenPnP's anchors and the few numbers Opulo's CAD leaves open (the feeders, from the videos);
# the feeders must reach the plates from their rails without hitting them, and stand on the slot blades.
ANCHORS["lumenpnp"] = (LUMEN, lumenpnp_anchors)
FREE["lumenpnp"] = ["feed_top", "feed_in", "feed_low"]
CHECKS["lumenpnp"] = lambda p: [80.0 - p["feed_in"], p["feed_in"] - 40.0, p["feed_top"] - 44.0,
                                -20.0 - p["feed_low"]]


# ===================================================================================================== stencil printer
# DDM Novastar SPR-45VA, a benchtop semi-automatic stencil printer with vision assist: 762 W x 889 D x 406 H mm (30 x
# 35 x 16 in, Pentalogix's listing; "H x W x D 16 x 30 x 35 in"), about 73 kg (160 lb, the SPR-45's listed weight);
# frame holder for stencil frames up to 584 x 584 mm (23 x 23 in); dual squeegees on a motorised print head and an
# automatic power frame lift (DDM Novastar's SPR-45 description at its resellers). The layout is generic for the type
# and read from resellers' photos: a low grey cabinet with the controls at the front, the board nest on the deck, the
# frame holder over it on two lift columns, the print head riding across the frame on side rails. 889 mm deep is more
# than the tray's 840, so on the tray it stands turned 90 degrees.
STENCIL = dict(W=762.0, D=889.0, H=406.0, deck=230.0, frame=584.0, lift=110.0, stroke=420.0)


def stencil_printer() -> Instrument:
    p = STENCIL
    W, D, H = p["W"], p["D"], p["H"]
    inst = Instrument("stencil", "Solder paste stencil printer, semi-automatic", "DDM Novastar SPR-45VA", (W, D, H),
                      "Pentalogix's SPR-45VA listing (762 x 889 x 406 mm, 584 mm frames); DDM Novastar's SPR-45 "
                      "description (160 lb, dual squeegees, power frame lift); layout from resellers' photos")
    inst.notes = ["The layout between the published outline is generic for a benchtop semi-automatic printer.",
                  "Semi-automatic: someone, or the arm, puts the board on the nest and takes it off; the machine "
                  "aligns, prints and separates.",
                  "889 mm deep against the tray's 840, so it goes on the tray turned 90 degrees.",
                  "Solder paste lives in a fridge and needs time to warm up; the paste on the stencil dries out over "
                  "a few hours, so someone has to wipe the stencil."]
    dz = p["deck"]
    fr = p["frame"]
    zs = dz + 70.0                                    # underside of the stencil when it is down on the board
    body = _piece(inst, "body")
    body.add("cabinet", rbox(W, D - 60, dz, 14, y=30), "ddm_grey")
    body.add("front panel", _wedge_front(W, dz), "ddm_grey")
    body.add("control panel", box(W / 2 - 260, -D / 2 - 4, 60, W / 2 - 40, -D / 2, 160), "inst_dark")
    body.add("screen", box(W / 2 - 245, -D / 2 - 6, 90, W / 2 - 140, -D / 2 - 4, 150), "screen_on")
    body.add("start buttons", box(-W / 2 + 40, -D / 2 - 3, 100, -W / 2 + 160, -D / 2, 130), "inst_green")
    body.add("e-stop", _ycyl(34, 14, x=-W / 2 + 210, y=-D / 2 - 14, z=115), "inst_red")
    body.add("logo", box(-80, -D / 2 - 2, 40, 80, -D / 2, 55), "ddm_blue")
    body.add("deck", box(-W / 2 + 10, -D / 2 + 40, dz, W / 2 - 10, D / 2 - 10, dz + 8), "inst_dark")
    body.add("board nest", box(-150, -110, dz + 8, 150, 110, zs - 1.6), "aluminium")
    # the frame holder slides on two lift posts, which pass through it and stop inside the published height; a sleeve
    # under the holder keeps hold of each post with the frame up
    px = W / 2 - 45
    for sx in (-1, 1):
        body.add(f"lift column {sx}", box(sx * px - 25, -60, dz + 8, sx * px + 25, 60, H - 4), "inst_dark")
    body.add("vision camera", box(-40, D / 2 - 90, dz + 8, 40, D / 2 - 30, zs - 20), "inst_black")
    frame = _piece(inst, "frame")
    ring = box(-W / 2 + 20, -fr / 2 - 30, zs + 20, W / 2 - 20, fr / 2 + 30, zs + 40).cut(
        box(-fr / 2, -fr / 2, zs + 19, fr / 2, fr / 2, zs + 41))
    for sx in (-1, 1):
        ring = ring.cut(box(sx * px - 27, -62, zs + 19, sx * px + 27, 62, zs + 41))
        frame.add(f"lift sleeve {sx}", box(sx * px - 30, -65, zs - 50, sx * px + 30, 65, zs + 20).cut(
            box(sx * px - 27, -62, zs - 51, sx * px + 27, 62, zs + 21)), "inst_dark")
    frame.add("frame holder", ring, "inst_black")
    frame.add("stencil frame", box(-fr / 2, -fr / 2, zs, fr / 2, fr / 2, zs + 38).cut(
        box(-fr / 2 + 32, -fr / 2 + 32, zs - 1, fr / 2 - 32, fr / 2 - 32, zs + 39)), "aluminium")
    frame.add("stencil foil", box(-fr / 2 + 32, -fr / 2 + 32, zs, fr / 2 - 32, fr / 2 - 32, zs + 0.8), "stainless")
    for i in range(10):                               # the apertures, where the board's pad rows are
        frame.add(f"aperture {i}", box(-90 + 20 * i, -40, zs + 0.8, -84 + 20 * i, 40, zs + 0.9), "inst_dark")
    for sx in (-1, 1):
        frame.add(f"head rail {sx}", box(sx * (fr / 2 + 6) - 8, -fr / 2 - 20, zs + 40, sx * (fr / 2 + 6) + 8,
                                         fr / 2 + 20, zs + 52), "steel")
    head = _piece(inst, "squeegee")
    y0 = -p["stroke"] / 2
    head.add("print head", box(-fr / 2 - 10, y0 - 40, zs + 52, fr / 2 + 10, y0 + 40, H - 4), "ddm_blue")
    head.add("head motor", box(-60, y0 - 20, H - 4, 60, y0 + 20, H), "inst_dark")
    for sy in (-1, 1):
        blade = box(-150, -1.5, zs + 1, 150, 1.5, zs + 52).rotate((0, 0, zs + 52), (1, 0, zs + 52), sy * 30)
        head.add(f"squeegee {sy}", blade.translate((0, y0 + sy * 18, 0)), "squeegee")
    head.add("paste bead", _xcyl(10, 280, x=-140, y=y0 + 40, z=zs + 6), "paste")
    board = _piece(inst, "load")
    board.add("board", box(-110, -60, zs - 1.6, 110, 60, zs), "fr4")
    paste = _piece(inst, "paste")
    for i in range(10):
        paste.add(f"paste row {i}", box(-90 + 20 * i, -40, zs, -84 + 20 * i, 40, zs + 0.6), "paste")
    inst.joints = {
        "frame": Joint("slide", vec=(0, 0, p["lift"]), v0=1.0),
        "squeegee": Joint("slide", vec=(0, p["stroke"], 0), parent="frame"),
        "load": Joint("path", path=((0, -650, 60), (0, -300, 40), (0, 0, 20), (0, 0, 0))),
        "paste": Joint("fade", parent="load"),
    }
    inst.actions = [
        ("The frame is up. A bare board goes onto the vacuum nest.", 2.0, {"load": (0.0, 1.0)}),
        ("The vision assist lines the stencil's apertures up with the pads; the frame comes down onto the board.", 1.6,
         {"frame": (1.0, 0.0)}),
        ("The print head drives a squeegee across: paste rolls ahead of the blade and fills the apertures.", 2.0,
         {"squeegee": (0.0, 1.0)}),
        ("The frame lifts straight up off the board, leaving the paste on the pads.", 1.4,
         {"frame": (0.0, 1.0), "paste": (0.0, 1.0)}),
        ("The pasted board goes on to the pick-and-place.", 1.8, {"load": (1.0, 0.0), "squeegee": (1.0, 0.0)}),
    ]
    inst.labels = [("stencil in its frame", (fr / 2 - 40, -fr / 2 + 40, zs + p["lift"] + 30), (0.84, 0.28)),
                   ("print head, dual squeegees", (-fr / 2, y0, H), (0.15, 0.22)),
                   ("controls", (W / 2 - 150, -D / 2, 140), (0.82, 0.78))]
    inst.cam = (0.8, -1.6, 1.2)
    return inst


def _wedge_front(W, dz):
    """The cabinet's sloped front, from 60 mm deep at the floor to the deck edge."""
    import cadquery as cq
    D = STENCIL["D"]
    pts = [(-D / 2 + 60, 0), (-D / 2, 0), (-D / 2, dz - 60), (-D / 2 + 60, dz)]
    return cq.Workplane("YZ").polyline(pts).close().extrude(W - 28).translate((-W / 2 + 14, 0, 0))


REGISTRY = {"stencil": stencil_printer, "lumenpnp": lumenpnp}
