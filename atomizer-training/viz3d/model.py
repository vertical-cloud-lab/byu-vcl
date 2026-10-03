"""CadQuery model of BYU's AMAZEMET rePowder induction atomizer, for the 3-D step animations.

Every part is a named CadQuery solid with a colour, placed where it sits in the assembled
machine (millimetres, z up from the floor, the operator stands at -y). ``parts()`` returns them;
``meshes()`` tessellates them into PyVista meshes (whole, and halved at y = 0 for cutaways),
cached in ``.cache/`` because the CadQuery build takes about a minute.

The crucible, sealing rod, adapter, holder arm and coil are copied from #222's
``atomizer-charge/cad/charge_cad.py`` (crucible scaled from Indutherm's GU500 section to
AMAZEMET's quoted 225 cm3). Everything else is proportioned from the training-video frames in
``../keyframes`` and the vendor numbers in #222's ``repowder-reference/README.md``: see the
"measured vs. assumed" table in README.md.

    python model.py      # builds and caches the meshes, prints the part list
"""
from __future__ import annotations

import hashlib
import math
import pickle
from dataclasses import dataclass, field
from pathlib import Path

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"

# ------------------------------------------------------------------------------------------ colours
STEEL = (0.78, 0.79, 0.81)
STEEL_DK = (0.58, 0.60, 0.63)
BLUE = (0.08, 0.24, 0.62)
GRAPHITE = (0.18, 0.18, 0.20)
COPPER = (0.78, 0.45, 0.25)
TITANIUM = (0.66, 0.64, 0.60)
INSUL = (0.95, 0.94, 0.90)
BLACK = (0.07, 0.07, 0.08)
SCREEN = (0.04, 0.06, 0.09)
FLANGE = (0.33, 0.34, 0.37)
GLASS = (0.62, 0.83, 0.94)
LCD = (0.25, 0.55, 0.95)
PANEL = (0.95, 0.95, 0.96)
YELLOW = (0.98, 0.80, 0.10)
RED = (0.80, 0.10, 0.08)
ORING = (0.15, 0.40, 0.85)
BRASS = (0.80, 0.65, 0.32)
ALU = (0.70, 0.72, 0.75)          # cold aluminium charge
CERAMIC = (0.93, 0.92, 0.88)
ARGON_BOTTLE = (0.30, 0.42, 0.36)
PUMP = (0.30, 0.36, 0.44)
HX = (0.90, 0.91, 0.92)
FLOOR = (0.955, 0.955, 0.96)
FRAME = (0.25, 0.26, 0.28)
GREEN = (0.10, 0.55, 0.25)
WATER_IN, WATER_OUT = (0.15, 0.35, 0.85), (0.85, 0.20, 0.15)
ARGON_LINE = (0.10, 0.62, 0.35)
AIR_LINE = (0.35, 0.72, 0.95)
VAC_LINE = (0.45, 0.46, 0.50)

# ----------------------------------------------------------------- crucible (from #222, documented)
CRUCIBLE_ID = 57.1
BORE_STRAIGHT = 81.1
FLOOR_CONE_H = 20.5
CRUCIBLE_WALL = 9.1
CRUCIBLE_BOTTOM = 13.7
POUR_HOLE_D = 6.9
SEALING_ROD_D = 12.6
ROD_ADAPTER_D = 21.7
ROD_ADAPTER_ABOVE_RIM = 18.3
ARM_ABOVE_RIM = 46.8
ARM_D = 16.0
COIL_RADIUS, COIL_TUBE_D, COIL_PITCH = 47.0, 8.0, 12.5
COIL_Z0, COIL_Z1 = -28.0, 72.0

# --------------------------------------------------------------- machine layout (see README: measured vs. assumed)
# Envelope 1000 W x 800 D x 1600 H (O&MM), feet 714 x 600 (Facility Guide); proportions measured off the training
# videos (720p frames) and AMAZEMET's 2025-26 renders, scaled to those numbers.
Z_PLATFORM = (1130.0, 1150.0)       # the chamber's top plate; the furnace stands on it
BODY_R, BODY_TOP = 135.0, 1345.0    # "BLUE POWER" furnace body
Z_CR = 1219.2                        # crucible datum: where the straight bore meets the floor cone
RIM = Z_CR + BORE_STRAIGHT
CRUCIBLE_BASE = Z_CR - FLOOR_CONE_H - CRUCIBLE_BOTTOM
HOOD_Z0, HOOD_H1, HOOD_H2 = BODY_TOP, 75.0, 90.0
HOOD_R0, HOOD_R1 = 142.0, 86.0
HINGE = np.array([-HOOD_R0, 0.0, BODY_TOP])       # lid hinge axis is along y through this point
ARM_ANGLE = 80.0                     # sealing-rod lift post: at the back (the operator stands at -y)
ARM_DIR = np.array([math.cos(math.radians(ARM_ANGLE)), math.sin(math.radians(ARM_ANGLE)), 0.0])
POST_R = 108.0
SLUG_D, SLUG_L, SLUG_R = 17.0, 100.0, 20.0
SLUG_ANGLES = (130.0, 205.0, 280.0, 355.0)        # clear of the rod adapter, the holder arm and the thermocouple
TC_ANGLE = 40.0                      # thermocouple: back right (Video 8, 4:10-4:35)

# chamber ("aus500" housing): D-shaped in plan (flat front and back, half-round right end), its left wall vertical for
# the top half, then the underside slopes down to the right at 45 deg to a narrow round bottom under the rounded end
CH_X, CH_Y = (-170.0, 230.0), (-110.0, 110.0)      # flat part; the half-round end (radius CH_Y[1]) is centred on x = CH_X[1]
CH_TOP, CH_BOTTOM = Z_PLATFORM[0], 420.0
CH_Z = (CH_BOTTOM, CH_TOP)
SLOPE_C = 610.0                      # underside plane: z = SLOPE_C - x (45 deg), so the left wall is vertical down to 780
CH_RIGHT = CH_X[1] + CH_Y[1]         # rightmost point of the rounded end
CH_WALL = 4.0
CHUTE_X = 280.0                      # outlet, valve and container axis (x, y = 0): under the rounded end
CHUTE_Z = (330.0, CH_BOTTOM)         # short cone under the chamber's bottom flange
VALVE_Z = (300.0, 330.0)
CLAMP_Z = (288.0, 300.0)
CVALVE_Z = (262.0, 288.0)
CONT_Z = (60.0, 262.0)
CONT_R = 65.0
VIEWPORT = np.array([-112.0, CH_Y[0] - 8.0, 1030.0])                   # at the front-left top corner, under the furnace
VIEWPORT_N = np.array([-0.55, -1.0, 0.40]) / np.linalg.norm([-0.55, -1.0, 0.40])   # looks in and down at the plate

# Ultrasonic stack: comes in through the door (left wall) at 40 deg, plate face centre at PLATE_C.
STACK_ANGLE = 40.0
STACK_DIR = np.array([math.cos(math.radians(STACK_ANGLE)), 0.0, math.sin(math.radians(STACK_ANGLE))])
PLATE_UP = np.array([-STACK_DIR[2], 0.0, STACK_DIR[0]])                              # up the plate's slope
IMPACT_S = 25.0                       # the stream lands this far up the plate from its centre
PLATE_C = np.array([IMPACT_S * STACK_DIR[2], 0.0, 970.0])   # chosen so the stream at x = 0 lands high
IMPACT = PLATE_C + IMPACT_S * PLATE_UP
DOOR_S = (PLATE_C[0] - CH_X[0]) / STACK_DIR[0]              # plate face to the door plane, along the stack

# graphite nozzle holder: its threaded shank passes the furnace floor and the top plate; the thin graphite nut goes on
# from below, inside the chamber, against a graphite seal
SHANK_R, SHANK_Z0 = 12.0, 1108.0
NUT_R, NUT_Z = 30.0, (1114.0, 1126.0)          # thin: 60 x 12 mm, a few threads
NUT_PITCH = 2.0
NOZZLE_EXIT_Z = SHANK_Z0

DOOR_Z = (790.0, 1115.0)                        # U-shaped door: flat top, round bottom
DOOR_W = 200.0
DOOR_HINGE = np.array([CH_X[0] - 8.0, DOOR_W / 2 + 12.0])  # vertical hinge axis at the back edge
# swing bolts with star knobs: two on the door's front edge, one under it
CLAMP_PTS = [np.array([CH_X[0] + 6, -DOOR_W / 2 + 4, 1050.0]), np.array([CH_X[0] + 6, -DOOR_W / 2 + 4, 880.0]),
             np.array([CH_X[0] + 6, 0.0, DOOR_Z[0] - 6])]
CLAMP_AXES = [np.array([0.0, 0.0, 1.0]), np.array([0.0, 0.0, 1.0]), np.array([0.0, 1.0, 0.0])]
CLAMP_SWING = (80.0, 80.0, -80.0)                 # degrees about CLAMP_AXES that swing each bolt clear of the door

# blue frame: the machine's own cabinet, behind the chamber, with the induction generator, PLC and pneumatics inside
FR_X, FR_Y, FR_Z = (CH_X[0], CH_X[0] + 745.0), (CH_Y[1] + 25.0, CH_Y[1] + 525.0), (175.0, 1600.0)
FEET_X, FEET_Y = (CH_X[0] + 15.0, CH_X[0] + 15.0 + 714.0), (-90.0, 510.0)


def chamber_floor(x: float) -> float:
    """Height of the chamber's inside floor at x (the 45 deg underside, then the round bottom)."""
    return max(CH_BOTTOM + CH_WALL, SLOPE_C + CH_WALL * math.sqrt(2) - x)


def floor_z(r: float) -> float:
    """Height of the crucible's conical floor at radius r, relative to Z_CR."""
    return -(CRUCIBLE_ID / 2 - r) * FLOOR_CONE_H / (CRUCIBLE_ID / 2)


def rod_ball_z() -> float:
    r = SEALING_ROD_D / 2
    half_angle = math.atan((CRUCIBLE_ID / 2) / FLOOR_CONE_H)
    return -FLOOR_CONE_H + r / math.sin(half_angle) + 0.05


# ------------------------------------------------------------------------------------- primitives
V = cq.Vector


def box(x0, x1, y0, y1, z0, z1) -> cq.Shape:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, pnt=V(x0, y0, z0))


def rbox(x0, x1, y0, y1, z0, z1, r) -> cq.Shape:
    """Box with its vertical edges rounded."""
    r = min(r, 0.45 * min(x1 - x0, y1 - y0))
    wp = cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).edges("|Z").fillet(r)
    return wp.val().translate(V((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


def cyl(r, h, base=(0, 0, 0), d=(0, 0, 1)) -> cq.Shape:
    return cq.Solid.makeCylinder(r, h, V(*base), V(*d))


def tube(ro, ri, h, base=(0, 0, 0), d=(0, 0, 1)) -> cq.Shape:
    return cyl(ro, h, base, d).cut(cyl(ri, h + 2, np.array(base) - np.array(d) * 1.0, d))


def sphere(r, c=(0, 0, 0)) -> cq.Shape:
    return cq.Workplane("XY").sphere(r).val().translate(V(*c))


def lathe(pts, z0=0.0, x=0.0, y=0.0) -> cq.Shape:
    """Revolve a closed half-profile of (r, z) points about the z axis, then move it."""
    wp = cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))
    return wp.val().translate(V(x, y, z0))


def along(shape: cq.Shape, origin, direction) -> cq.Shape:
    """Move a part built along +z (base at the origin) so its axis runs along `direction` from `origin`."""
    d = np.asarray(direction, float)
    d /= np.linalg.norm(d)
    z = np.array([0, 0, 1.0])
    ax = np.cross(z, d)
    s = np.linalg.norm(ax)
    if s > 1e-9:
        ang = math.degrees(math.atan2(s, float(np.dot(z, d))))
        shape = shape.rotate(V(0, 0, 0), V(*(ax / s)), ang)
    elif d[2] < 0:
        shape = shape.rotate(V(0, 0, 0), V(1, 0, 0), 180)
    return shape.translate(V(*origin))


def fuse(*shapes) -> cq.Shape:
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.clean()


def compound(*shapes) -> cq.Shape:
    return cq.Compound.makeCompound(list(shapes))


def hexframe(r0, r1, z0, h1, h2) -> cq.Shape:
    """Faceted hood: a hexagonal prism of height h1 topped by a hexagonal frustum of height h2."""
    return (cq.Workplane("XY").workplane(offset=z0).polygon(6, 2 * r0)
            .workplane(offset=h1).polygon(6, 2 * r0)
            .workplane(offset=h2).polygon(6, 2 * r1).loft(ruled=True)).val()


# ------------------------------------------------------------------------------------------- parts
@dataclass
class Part:
    name: str
    shape: cq.Shape
    color: tuple
    group: str = "machine"
    opacity: float = 1.0
    cut: bool = True               # halve it in cutaway views
    tol: float = 0.4
    tags: tuple = field(default_factory=tuple)


def furnace_parts() -> list[Part]:
    P = []
    ri, ro = CRUCIBLE_ID / 2, CRUCIBLE_ID / 2 + CRUCIBLE_WALL
    rh = POUR_HOLE_D / 2
    zb, zt = -FLOOR_CONE_H - CRUCIBLE_BOTTOM, BORE_STRAIGHT
    crucible = lathe([(rh, zb), (ro - 2, zb), (ro, zb + 2), (ro, zt - 2), (ro - 2, zt), (ri + 1, zt),
                      (ri, zt - 1), (ri, 0), (rh, floor_z(rh))], Z_CR)
    tc_xy = 33.1 * np.array([math.cos(math.radians(TC_ANGLE)), math.sin(math.radians(TC_ANGLE))])
    crucible = crucible.cut(cyl(2.4, 45, (tc_xy[0], tc_xy[1], RIM - 44)))     # wall thermocouple hole
    P.append(Part("crucible", crucible, GRAPHITE, "crucible", tol=0.15))
    # nozzle holder under the crucible (graphite), nozzle plate in its top recess, white side up; its threaded shank
    # runs down through the bottom insulation, the furnace floor and the chamber's top plate
    zs = SHANK_Z0 - CRUCIBLE_BASE
    holder = lathe([(1.0, zs), (SHANK_R, zs), (SHANK_R, -25), (15, -25), (15, 0), (8.2, 0), (8.2, -5), (1.0, -5)],
                   CRUCIBLE_BASE)
    for z in (SHANK_Z0 + 3, SHANK_Z0 + 3 + NUT_PITCH * 2, SHANK_Z0 + 3 + NUT_PITCH * 4, SHANK_Z0 + 3 + NUT_PITCH * 6):
        holder = holder.cut(tube(SHANK_R + 1, SHANK_R - 0.8, 0.9, (0, 0, z)))     # a few threads
    holder = holder.cut(box(11.5, 16, -2.5, 2.5, CRUCIBLE_BASE - 22, CRUCIBLE_BASE - 3))   # a flat, so turning shows
    P.append(Part("nozzle_holder", holder, GRAPHITE, "holder", tol=0.1))
    P.append(Part("nozzle", lathe([(0.6, -5), (8, -5), (8, -1), (0.6, -1)], CRUCIBLE_BASE), GRAPHITE,
                  "nozzle", tol=0.05))
    P.append(Part("nozzle_white", lathe([(0.6, -1), (8, -1), (8, 0), (0.6, 0)], CRUCIBLE_BASE), INSUL,
                  "nozzle", tol=0.05))
    # graphite seal and the thin graphite nut, under the top plate inside the chamber (snug, never forced)
    P.append(Part("graphite_seal", tube(NUT_R, SHANK_R + 0.5, Z_PLATFORM[0] - NUT_Z[1], (0, 0, NUT_Z[1])), GRAPHITE,
                  "seal", tol=0.1))
    nut = tube(NUT_R, SHANK_R + 0.3, NUT_Z[1] - NUT_Z[0], (0, 0, NUT_Z[0]))
    for k in range(6):                                        # grip notches round the rim
        a = math.radians(30 + 60 * k)
        nut = nut.cut(cyl(3.2, NUT_Z[1] - NUT_Z[0] + 2, (NUT_R * math.cos(a), NUT_R * math.sin(a), NUT_Z[0] - 1)))
    P.append(Part("nut", nut.clean(), (0.24, 0.24, 0.27), "nut", tol=0.1))
    # insulation: bottom (C022), side tube (C011), top / filling cone (C020)
    P.append(Part("bottom_insulation", lathe([(16, 1157), (75, 1157), (75, CRUCIBLE_BASE), (16, CRUCIBLE_BASE)]),
                  INSUL, "bottom_ins", tol=0.2))
    side = lathe([(ro + 0.6, CRUCIBLE_BASE), (42.4, CRUCIBLE_BASE), (42.4, RIM), (ro + 0.6, RIM)])
    P.append(Part("side_insulation", side, INSUL, "side_ins", tol=0.15))
    top = lathe([(ri, RIM), (98, RIM), (98, BODY_TOP - 4), (50, BODY_TOP - 4), (ri + 2, RIM + 12)])
    tc_hole = cyl(2.6, 60, (tc_xy[0], tc_xy[1], RIM - 5))
    P.append(Part("top_insulation", top.cut(tc_hole), INSUL, "top_ins", tol=0.2))
    # induction coil (water-cooled copper tube)
    helix = cq.Wire.makeHelix(COIL_PITCH, COIL_Z1 - COIL_Z0, COIL_RADIUS)
    coil = (cq.Workplane("XZ").center(COIL_RADIUS, 0).circle(COIL_TUBE_D / 2)
            .sweep(cq.Workplane().add(helix), isFrenet=True)).val().translate(V(0, 0, Z_CR + COIL_Z0))
    P.append(Part("coil", coil, COPPER, "coil", tol=0.15))
    # body, top deck with the blue O-ring, floor
    body = tube(BODY_R, BODY_R - 3, BODY_TOP - Z_PLATFORM[1], (0, 0, Z_PLATFORM[1]))
    body = body.fuse(tube(BODY_R, 100, 5, (0, 0, BODY_TOP - 5)))
    body = body.fuse(tube(BODY_R, 25, 7, (0, 0, Z_PLATFORM[1])))
    P.append(Part("furnace_body", body.clean(), STEEL, "furnace", tol=0.4))
    P.append(Part("oring", cq.Solid.makeTorus(BODY_R - 9, 3.0, V(0, 0, BODY_TOP + 0.5), V(0, 0, 1)), ORING,
                  "furnace", tol=0.2))
    # sealing rod (ball tip), its adapter, holder arm and the pneumatic lift post
    r, zc = SEALING_ROD_D / 2, rod_ball_z()
    rod_top = BORE_STRAIGHT + ROD_ADAPTER_ABOVE_RIM
    rod = fuse(sphere(r, (0, 0, Z_CR + zc)), cyl(r, rod_top - zc, (0, 0, Z_CR + zc)))
    P.append(Part("sealing_rod", rod, GRAPHITE, "rod", tol=0.1))
    z_ad = Z_CR + rod_top
    z_arm = RIM + ARM_ABOVE_RIM + ARM_D / 2
    adapter = cyl(ROD_ADAPTER_D / 2, z_arm + ARM_D / 2 + 6 - z_ad, (0, 0, z_ad))
    P.append(Part("rod_adapter", adapter, BRASS, "rod", tol=0.1))
    post = np.array([POST_R * ARM_DIR[0], POST_R * ARM_DIR[1]])
    arm = along(cyl(ARM_D / 2, POST_R, (0, 0, 0)), (0, 0, z_arm), ARM_DIR)
    arm = arm.fuse(cyl(ROD_ADAPTER_D / 2 + 5, ARM_D, (0, 0, z_arm - ARM_D / 2)).cut(
        cyl(ROD_ADAPTER_D / 2 + 0.3, ARM_D + 2, (0, 0, z_arm - ARM_D / 2 - 1))))
    P.append(Part("holder_arm", arm.clean(), STEEL_DK, "arm", tol=0.15))
    P.append(Part("lift_post", fuse(cyl(16, z_arm - BODY_TOP + 12, (post[0], post[1], BODY_TOP)),
                                    cyl(22, 10, (post[0], post[1], BODY_TOP))), STEEL_DK, "furnace", tol=0.2))
    # wall thermocouple, Type N: ceramic sheath from its plug over the top insulation into the wall hole
    a = math.radians(TC_ANGLE)
    u = np.array([math.cos(a), math.sin(a), 0.0])
    p0 = np.array([tc_xy[0], tc_xy[1], RIM - 40])
    p1 = np.array([tc_xy[0], tc_xy[1], BODY_TOP + 6])
    p2 = np.array([0, 0, BODY_TOP + 6]) + u * 112
    tc = fuse(cyl(1.9, p1[2] - p0[2], p0), along(cyl(1.9, 112 - 33.1, (0, 0, 0)), p1, u),
              sphere(1.9, p1))
    plug = cyl(9, 26, p2 + np.array([0, 0, -13]))
    P.append(Part("thermocouple", tc, CERAMIC, "tc", tol=0.1))
    P.append(Part("tc_plug", plug, BLACK, "furnace", tol=0.2))
    # connector plate at the back left (three plugs) and the water-cooled coil leads on the left side
    b = math.radians(150.0)
    cp = np.array([(BODY_R + 4) * math.cos(b), (BODY_R + 4) * math.sin(b), 1250.0])
    plate = cq.Workplane("XY").box(10, 70, 46).val().rotate(V(0, 0, 0), V(0, 0, 1), 150).translate(V(*cp))
    plugs = [along(cyl(8, 16), cp + np.array([0, 0, dz]) + 4 * np.array([math.cos(b), math.sin(b), 0]),
                   (math.cos(b), math.sin(b), 0)) for dz in (-14, 0, 14)]
    P.append(Part("connector_plate", fuse(plate, *plugs), STEEL_DK, "furnace", tol=0.2, cut=False))
    for k, dy in enumerate((-35.0, -5.0)):
        a0 = np.array([-BODY_R - 2, dy, 1195.0 + 12 * k])
        P.append(Part(f"coil_lead{k}", fuse(along(cyl(9, 60), a0, (-1, 0, 0)),
                                            along(cyl(9, 300), a0 + np.array([-60, 0, 0]), (0, 1, -0.15))),
                      BLACK, "furnace", tol=0.3, cut=False))
    # charge: four 6063 rods, 17 mm x 100 mm (~245 g), standing in the annulus round the rod
    for k, ang in enumerate(SLUG_ANGLES):
        c = SLUG_R * np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))])
        slug = cq.Workplane("XY").circle(SLUG_D / 2).extrude(SLUG_L).edges().chamfer(0.8).val()
        P.append(Part(f"slug{k}", slug.translate(V(c[0], c[1], Z_CR + 0.2)), ALU, f"slug{k}", tol=0.1, cut=False))
    return P


def hood_parts() -> list[Part]:
    P = []
    outer = hexframe(HOOD_R0, HOOD_R1, HOOD_Z0, HOOD_H1, HOOD_H2)
    inner = hexframe(HOOD_R0 - 5, HOOD_R1 - 5, HOOD_Z0 - 1, HOOD_H1 + 1, HOOD_H2 - 6)
    a0, a1 = HOOD_R0 * math.cos(math.pi / 6), HOOD_R1 * math.cos(math.pi / 6)
    zc = HOOD_Z0 + HOOD_H1 + HOOD_H2 / 2
    tilt = math.atan2(a0 - a1, HOOD_H2)
    n = np.array([0, -math.cos(tilt), math.sin(tilt)])
    centre = np.array([0, -(a0 + a1) / 2, zc])
    plane = cq.Plane(origin=V(*(centre - n * 1.0)), xDir=V(1, 0, 0), normal=V(*n))
    hood = outer.cut(inner).cut(cq.Workplane(plane).rect(66, 50).extrude(8).val())
    P.append(Part("hood", hood.clean(), STEEL, "hood", tol=0.4))
    window = cq.Workplane(plane).rect(70, 54).extrude(3).val()
    P.append(Part("hood_window", window, (0.12, 0.13, 0.15), "hood", tol=0.2))
    plane2 = cq.Plane(origin=V(*(centre - n * 0.5 + np.array([0, 0, -40]) * 1.0
                                 + np.array([0, -1, 0]) * 40 * math.tan(tilt))), xDir=V(1, 0, 0), normal=V(*n))
    hot = cq.Workplane(plane2).polygon(3, 22).extrude(2).val()
    P.append(Part("hood_hot_label", hot, YELLOW, "hood", tol=0.1))
    knob_base = np.array([HOOD_R0 * 0.62, -20, HOOD_Z0 + HOOD_H1 + 30])
    P.append(Part("hood_knob", fuse(cyl(5, 30, knob_base, (0.6, 0, 0.8)),
                                    sphere(14, knob_base + np.array([0.6, 0, 0.8]) * 38)), BLACK, "hood", tol=0.2))
    P.append(Part("hood_hinge", cyl(9, 90, (HINGE[0] - 6, -45, HINGE[2] + 6), (0, 1, 0)), STEEL_DK, "furnace",
                  tol=0.2))
    return P


def chamber_solid(inset: float = 0.0) -> cq.Shape:
    """The chamber's outline as a solid, shrunk by `inset` all round (CH_WALL gives the inside)."""
    x0, x1 = CH_X[0] + inset, CH_X[1]
    y0, y1 = CH_Y[0] + inset, CH_Y[1] - inset
    z0, z1 = CH_BOTTOM + inset, CH_TOP - inset
    plan = (cq.Workplane("XY").workplane(offset=z0).moveTo(x0, y0).lineTo(x1, y0)
            .threePointArc((x1 + y1, 0.0), (x1, y1)).lineTo(x0, y1).close().extrude(z1 - z0)).val()
    c = SLOPE_C + inset * math.sqrt(2)          # underside plane z = c - x, moved inwards by `inset`
    below = (cq.Workplane("XZ").workplane(offset=-1000).polyline([(-1000, c + 1000), (c + 1000, -1000), (-1000, -1000)])
             .close().extrude(2000)).val()
    return plan.cut(below)


def u_shape(w, z0, z1, x, thick):
    """A U (flat top, round bottom) in the y-z plane, `thick` deep in x from `x`."""
    r = w / 2
    return (cq.Workplane("YZ").workplane(offset=x).moveTo(-r, z1).lineTo(r, z1).lineTo(r, z0 + r)
            .threePointArc((0, z0), (-r, z0 + r)).close().extrude(thick)).val()


def chamber_parts() -> list[Part]:
    P = []
    x0 = CH_X[0]
    y0 = CH_Y[0]
    shell = chamber_solid().cut(chamber_solid(CH_WALL))
    shell = shell.cut(u_shape(DOOR_W - 30, DOOR_Z[0] + 15, DOOR_Z[1] - 15, x0 - 5, CH_WALL + 10))   # door opening
    shell = shell.cut(along(cyl(45, 40), VIEWPORT + VIEWPORT_N * 10, -VIEWPORT_N))                  # view port
    shell = shell.cut(cyl(52, 30, (CHUTE_X, 0, CH_BOTTOM - 10)))                                   # to the cone
    shell = shell.cut(cyl(22, 30, (0, 0, CH_TOP - 15)))                                            # from the furnace
    P.append(Part("chamber", shell.clean(), STEEL, "chamber", tol=0.5))
    # vertical slots on the front face, above the sloped underside
    slots = []
    for k in range(9):
        x = -40 + 30 * k
        zb = max(CH_BOTTOM, SLOPE_C - x) + 45
        slots.append(box(x - 4, x + 4, y0 - 1.5, y0 + 0.5, zb, 960.0 - 10 * (k % 2)))
    P.append(Part("chamber_slots", compound(*slots), STEEL_DK, "chamber", tol=0.3))
    # view port: dark-grey 12-sided cover with the light-blue glass, tilted down at the plate
    vp = cq.Workplane("XY").polygon(12, 180).extrude(46).val().cut(cyl(44, 60, (0, 0, -5)))
    P.append(Part("viewport_flange", along(vp, VIEWPORT - VIEWPORT_N * 6, VIEWPORT_N), FLANGE, "chamber", tol=0.3))
    P.append(Part("viewport_glass", along(cyl(45, 6), VIEWPORT + VIEWPORT_N * 4, VIEWPORT_N), GLASS, "chamber",
                  opacity=0.8, tol=0.2))
    # small tri-clamp port low at the back of the left face
    P.append(Part("left_port", along(fuse(cyl(16, 30), cyl(25, 6, (0, 0, 30))), (x0, CH_Y[1] - 45, 810.0),
                                     (-1, 0, 0)), STEEL, "chamber", tol=0.2))
    # door on the left wall, hinged at its back edge; the stack goes through its lower half at 40 deg
    door = u_shape(DOOR_W, DOOR_Z[0], DOOR_Z[1], x0 - 16, 16)
    door = door.fuse(u_shape(DOOR_W - 50, DOOR_Z[0] + 25, DOOR_Z[1] - 25, x0 - 26, 10))
    port = PLATE_C - STACK_DIR * DOOR_S          # the stack crosses the door plane here
    door = door.cut(along(cyl(30, 200), port - STACK_DIR * 100, STACK_DIR))
    door = door.fuse(along(tube(42, 30, 60), port - STACK_DIR * 45, STACK_DIR))
    sight = np.array([x0 - 26, -45.0, 1060.0])
    door = door.fuse(along(tube(30, 22, 12), sight, (-1, 0, 0)))
    P.append(Part("door", door.clean(), STEEL, "door", tol=0.4))
    P.append(Part("door_glass", along(cyl(22, 4), sight + np.array([-4, 0, 0]), (-1, 0, 0)), GLASS, "door",
                  opacity=0.8, tol=0.2))
    P.append(Part("door_hinge", compound(*[cyl(8, 50, (DOOR_HINGE[0], DOOR_HINGE[1], z), (0, 0, 1))
                                           for z in (DOOR_Z[0] + 80, DOOR_Z[1] - 90)]), STEEL_DK, "chamber",
                  tol=0.2, cut=False))
    # swing bolts with black star knobs: bracket on the chamber, bolt and knob swing clear to open
    for k, (pt, ax) in enumerate(zip(CLAMP_PTS, CLAMP_AXES)):
        P.append(Part(f"clamp_body{k}", along(cyl(9, 18), pt + np.array([-2, 0, 0]), (1, 0, 0)), STEEL_DK, "chamber",
                      tol=0.2, cut=False))
        knob_c = pt + np.array([-44.0, 0, 0])
        lobes = [along(cyl(5.5, 12), knob_c + 11 * np.array([0, math.cos(t), math.sin(t)]), (-1, 0, 0))
                 for t in np.linspace(0, 2 * math.pi, 5, endpoint=False)]
        bolt = fuse(along(cyl(4, 40), pt, (-1, 0, 0)), along(cyl(10, 12), knob_c, (-1, 0, 0)), *lobes,
                    along(cyl(4, 8), knob_c + np.array([-12, 0, 0]), (-1, 0, 0)))
        P.append(Part(f"clamp{k}", bolt, BLACK, f"clamp{k}", tol=0.2, cut=False))
    # catch bowl round the outlet, and the splash plate leaning over it
    P.append(Part("catch_bowl", lathe([(46, 0), (60, 0), (82, 26), (78, 26), (57, 4), (46, 4)], CH_BOTTOM + CH_WALL,
                                      CHUTE_X, 0), STEEL_DK, "bowl", tol=0.3))
    splash = cq.Workplane("XY").rect(130, 150).extrude(3).val().rotate(V(0, 0, 0), V(0, 1, 0), 32)
    P.append(Part("splash_plate", splash.translate(V(CHUTE_X - 10, 0, 610)), STEEL, "splash", tol=0.3))
    # bottom flange, short cone, valve, then the airlock powder container
    P.append(Part("chute", fuse(tube(108, 52, 10, (CHUTE_X, 0, CH_BOTTOM - 10)),
                                cq.Solid.makeCone(44, 104, CHUTE_Z[1] - 10 - CHUTE_Z[0], V(CHUTE_X, 0, CHUTE_Z[0])).cut(
                                    cq.Solid.makeCone(38, 98, CHUTE_Z[1] - 10 - CHUTE_Z[0] + 0.5,
                                                      V(CHUTE_X, 0, CHUTE_Z[0] - 0.2)))),
                  STEEL, "chamber", tol=0.4))
    P.append(Part("valve", fuse(tube(56, 38, VALVE_Z[1] - VALVE_Z[0], (CHUTE_X, 0, VALVE_Z[0])),
                                box(CHUTE_X - 10, CHUTE_X + 10, -95, -50, VALVE_Z[0] + 6, VALVE_Z[1] - 6)),
                  STEEL_DK, "chamber", tol=0.3))
    P.append(Part("valve_handle", box(CHUTE_X - 5, CHUTE_X + 95, -110, -95, VALVE_Z[0] + 8, VALVE_Z[1] - 8),
                  GREEN, "chamber", tol=0.2))
    h = CONT_Z[1] - CONT_Z[0]
    cont = lathe([(0, 0), (CONT_R - 12, 0), (CONT_R, 12), (CONT_R, h - 12), (52, h - 4), (52, h), (0, h)],
                 CONT_Z[0], CHUTE_X)
    cont = cont.cut(lathe([(0, 4), (CONT_R - 15, 4), (CONT_R - 4, 15), (CONT_R - 4, h - 14), (40, h - 6),
                           (40, h + 5), (0, h + 5)], CONT_Z[0], CHUTE_X))
    cont = cont.fuse(tube(54, 38, CVALVE_Z[1] - CVALVE_Z[0], (CHUTE_X, 0, CVALVE_Z[0])))
    cont = cont.fuse(box(CHUTE_X - 8, CHUTE_X + 8, -88, -50, CVALVE_Z[0] + 5, CVALVE_Z[1] - 5))
    P.append(Part("container", cont.clean(), STEEL, "container", tol=0.4))
    P.append(Part("container_handle", box(CHUTE_X - 4, CHUTE_X + 85, -100, -88, CVALVE_Z[0] + 7,
                                          CVALVE_Z[1] - 7), RED, "container", tol=0.2))
    P.append(Part("flange_clamp", fuse(tube(60, 39, CLAMP_Z[1] - CLAMP_Z[0], (CHUTE_X, 0, CLAMP_Z[0])),
                                      cyl(5, 30, (CHUTE_X + 60, 0, (CLAMP_Z[0] + CLAMP_Z[1]) / 2), (1, 0, 0)),
                                      sphere(8, (CHUTE_X + 94, 0, (CLAMP_Z[0] + CLAMP_Z[1]) / 2))),
                  STEEL_DK, "flange_clamp", tol=0.3))
    return P


def stack_parts() -> list[Part]:
    """Ultrasonic stack along STACK_DIR. Distances are measured back from the plate face."""
    P = []

    def seg(name, r, s0, s1, color, group, tol=0.15, **kw):
        P.append(Part(name, along(cyl(r, s1 - s0), PLATE_C - STACK_DIR * s1, STACK_DIR), color, group, tol=tol,
                      cut=False, **kw))

    plate = cq.Workplane("XY").rect(100, 20).extrude(4).edges("|Z").fillet(3).val()
    plate = plate.translate(V(0, 0, -4))
    # orient: plate long side up the slope, normal along STACK_DIR, face at PLATE_C
    plate = plate.rotate(V(0, 0, 0), V(0, 1, 0), 45).translate(V(*PLATE_C))
    P.append(Part("plate", plate, TITANIUM, "plate", tol=0.1, cut=False))
    seg("stud", 4, 4, 14, STEEL_DK, "plate")
    sono = fuse(along(cyl(12, 128), PLATE_C - STACK_DIR * 132, STACK_DIR),
                along(cyl(17, 8), PLATE_C - STACK_DIR * 126, STACK_DIR),
                along(cyl(37, 8), PLATE_C - STACK_DIR * 120, STACK_DIR))       # KF50 flange at the booster end
    P.append(Part("sonotrode", sono, TITANIUM, "sonotrode", tol=0.15, cut=False))
    boost = fuse(along(cyl(20, 120), PLATE_C - STACK_DIR * 254, STACK_DIR),
                 along(cyl(34, 10), PLATE_C - STACK_DIR * 199, STACK_DIR))
    P.append(Part("booster", boost, (0.72, 0.73, 0.76), "booster", tol=0.15, cut=False))
    trans = fuse(along(cyl(36, 100), PLATE_C - STACK_DIR * 354, STACK_DIR),
                 along(cyl(30, 10), PLATE_C - STACK_DIR * 364, STACK_DIR),
                 along(cyl(9, 25), PLATE_C - STACK_DIR * 389, STACK_DIR))
    P.append(Part("transducer", trans, (0.25, 0.27, 0.30), "transducer", tol=0.2, cut=False))
    cover = along(tube(50, 46, 170), PLATE_C - STACK_DIR * 400, STACK_DIR)
    cover = cover.fuse(along(cyl(50, 5), PLATE_C - STACK_DIR * 405, STACK_DIR).cut(
        along(cyl(12, 12), PLATE_C - STACK_DIR * 410, STACK_DIR)))
    cover = cover.fuse(along(tube(62, 46, 8), PLATE_C - STACK_DIR * 238, STACK_DIR))
    P.append(Part("stack_cover", cover.clean(), STEEL, "cover", tol=0.3, cut=False))
    return P


# label anchors on the frame (used by the animations and the hero stills)
PANEL_C = np.array([FR_X[1] - 145.0, FR_Y[0] + 20.0, 1350.0])
SWITCH_C = np.array([FR_X[1] - 110.0, FR_Y[0] - 14.0, 1100.0])
HMI_C = np.array([FR_X[1] + 170.0, 40.0, 1450.0])


def frame_parts() -> list[Part]:
    """The blue frame: the machine's own cabinet. The induction generator, PLC, relays and pneumatics are built into it
    (side doors left and right), so there is no separate electrical cabinet."""
    P = []
    fx0, fx1 = FR_X
    fy0, fy1 = FR_Y
    P.append(Part("floor", box(-1100, 1450, -700, 1550, -6, 0), FLOOR, "static", tol=2.0, cut=False))
    rails = [box(x - 20, x + 20, CH_Y[0] - 30, fy1, 110, FR_Z[0]) for x in FEET_X]
    rails += [box(FEET_X[0] - 20, FEET_X[1] + 20, fy1 - 40, fy1, 110, FR_Z[0])]
    P.append(Part("base_frame", fuse(*rails), FRAME, "static", tol=1.0, cut=False))
    feet = [fuse(cyl(10, 112, (x, y, 0)), cyl(25, 12, (x, y, 0))) for x in FEET_X for y in FEET_Y]
    P.append(Part("feet", compound(*feet), FRAME, "static", tol=0.5, cut=False))
    body = rbox(fx0, fx1, fy0, fy1, FR_Z[0], FR_Z[1], 12)
    nx0, nx1, nz0, nz1 = fx1 - 250, fx1 - 40, FR_Z[1] - 130 - 355, FR_Z[1] - 130     # recess for the GU 500 panel
    body = body.cut(box(nx0, nx1, fy0 - 5, fy0 + 40, nz0, nz1))
    P.append(Part("cabinet", body, BLUE, "static", tol=0.8, cut=False))
    # side doors (left: air, argon, pneumatics; right: PLC, relays, generator control), shown by a seam and a handle
    for side, x in (("l", fx0 - 1.5), ("r", fx1 + 1.5)):
        seam = box(min(x, x + (1 if side == "r" else -1)) - 0.5, max(x, x + (1 if side == "r" else -1)) + 0.5,
                   fy0 + 40, fy1 - 40, FR_Z[0] + 60, FR_Z[1] - 60).cut(
            box(x - 3, x + 3, fy0 + 46, fy1 - 46, FR_Z[0] + 66, FR_Z[1] - 66))
        handle = box(x - 6 if side == "l" else x, x if side == "l" else x + 6, fy0 + 70, fy0 + 90, 1020, 1120)
        P.append(Part(f"side_door_{side}", fuse(seam, handle), (0.05, 0.14, 0.40), "static", tol=0.3, cut=False))
    # melting control panel ("GU 500 AMA") in its recess: white housing, blue LCD, keypad
    px0, px1, pz0, pz1 = nx0 + 35, nx1 - 35, nz1 - 25 - 195, nz1 - 25
    py = fy0 + 40
    P.append(Part("control_panel", rbox(px0, px1, py - 12, py, pz0, pz1, 6), PANEL, "static", tol=0.3, cut=False))
    P.append(Part("panel_lcd", box(px0 + 14, px1 - 14, py - 15, py - 12, pz1 - 80, pz1 - 22), LCD, "static", tol=0.2,
                  cut=False))
    keys = [box(px0 + 14 + 23 * i, px0 + 32 + 23 * i, py - 16, py - 12, pz0 + 20 + 24 * j, pz0 + 36 + 24 * j)
            for i in range(5) for j in range(3)]
    P.append(Part("panel_keys", compound(*keys), (0.35, 0.36, 0.40), "static", tol=0.2, cut=False))
    # main switch under the panel, right of the chamber: yellow plate, red rotary handle
    sx, sz = SWITCH_C[0], SWITCH_C[2]
    P.append(Part("main_switch", box(sx - 40, sx + 40, fy0 - 10, fy0, sz - 45, sz + 45), YELLOW, "static", tol=0.2,
                  cut=False))
    P.append(Part("main_switch_handle", fuse(cyl(22, 14, (sx, fy0 - 10, sz), (0, -1, 0)),
                                            box(sx - 10, sx + 10, fy0 - 40, fy0 - 20, sz - 35, sz + 37)), RED,
                  "switch", tol=0.2, cut=False))
    # 15.6 in HMI (Weintek cMT2166X, 400 x 263) on an arm from the frame's right front edge
    arm = fuse(box(fx1, fx1 + 30, fy0 + 10, fy0 + 50, 1380, 1440), along(cyl(14, 170), (fx1 + 20, fy0 + 30, 1410),
                                                                           (0.55, -0.83, 0)),
               cyl(20, 50, (fx1 + 115, 50, 1385)))
    P.append(Part("hmi_arm", arm, BLACK, "static", tol=0.4, cut=False))
    hmi = rbox(-200, 200, -14, 14, -131, 131, 8)
    hmi_screen = box(-186, 186, -18, -13, -112, 112)
    widgets = [box(-170 + 70 * i, -120 + 70 * i, -20, -17, 40 - 40 * j, 62 - 40 * j)
               for i in range(5) for j in range(3) if (i + j) % 2 == 0]
    rot = lambda s: s.rotate(V(0, 0, 0), V(0, 0, 1), -25).translate(V(*HMI_C))
    P.append(Part("hmi", rot(hmi), BLACK, "static", tol=0.4, cut=False))
    P.append(Part("hmi_screen", rot(hmi_screen), SCREEN, "static", tol=0.3, cut=False))
    P.append(Part("hmi_widgets", rot(compound(*widgets)), (0.55, 0.70, 0.85), "static", tol=0.3, cut=False))
    P.append(Part("cabinet_ports", compound(cyl(30, 14, (fx0, 450, 660), (-1, 0, 0)),
                                            cyl(12, 12, (fx0, 520, 1180), (-1, 0, 0))), STEEL_DK, "static",
                  tol=0.3, cut=False))
    # the furnace's top plate: the chamber's lid, D-shaped like the chamber
    top = (cq.Workplane("XY").workplane(offset=Z_PLATFORM[0]).moveTo(CH_X[0], CH_Y[0]).lineTo(CH_X[1], CH_Y[0])
           .threePointArc((CH_RIGHT, 0.0), (CH_X[1], CH_Y[1])).lineTo(CH_X[0], CH_Y[1]).close()
           .extrude(Z_PLATFORM[1] - Z_PLATFORM[0])).val().cut(cyl(20, 40, (0, 0, Z_PLATFORM[0] - 10)))
    P.append(Part("platform", top, STEEL, "furnace", tol=0.5))
    return P


def utility_parts() -> list[Part]:
    P = []
    # argon 5N cylinder, chained at the back left, with a two-gauge regulator
    ax, ay = -560.0, 760.0
    bottle = fuse(cyl(115, 1250, (ax, ay, 0)), sphere(115, (ax, ay, 1250)), cyl(30, 140, (ax, ay, 1300)))
    P.append(Part("argon_cylinder", bottle, ARGON_BOTTLE, "utilities", tol=1.0, cut=False))
    reg = fuse(cyl(16, 70, (ax, ay, 1440)), cyl(30, 60, (ax, ay - 30, 1495), (0, 1, 0)),
               cyl(26, 16, (ax - 40, ay - 10, 1470), (0, -1, 0)), cyl(26, 16, (ax + 40, ay - 10, 1470), (0, -1, 0)),
               cyl(8, 90, (ax - 40, ay, 1470), (1, 0, 0)))
    P.append(Part("argon_regulator", reg, BRASS, "utilities", tol=0.3, cut=False))
    P.append(Part("argon_gauges", compound(cyl(22, 2, (ax - 40, ay - 26, 1470), (0, -1, 0)),
                                           cyl(22, 2, (ax + 40, ay - 26, 1470), (0, -1, 0))), PANEL, "utilities",
                  tol=0.2, cut=False))
    # vacuum pump on the floor at the left, oil sight glass on its end
    vx, vy = -650.0, 230.0
    pump = fuse(rbox(vx - 230, vx + 230, vy - 110, vy + 110, 0, 40, 10), cyl(95, 230, (vx - 220, vy, 150), (1, 0, 0)),
                rbox(vx + 20, vx + 210, vy - 100, vy + 100, 40, 260, 20))
    P.append(Part("vacuum_pump", pump, PUMP, "utilities", tol=0.8, cut=False))
    P.append(Part("pump_sight_glass", cyl(18, 4, (vx + 60, vy - 103, 110), (0, -1, 0)), (0.95, 0.70, 0.15),
                  "utilities", tol=0.2, cut=False))
    # heat exchanger (recirculating, chilled-water side) behind the cabinet on the right
    hx0 = np.array([680.0, 140.0])
    hxb = rbox(hx0[0], hx0[0] + 480, hx0[1], hx0[1] + 560, 0, 900, 15)
    P.append(Part("heat_exchanger", hxb, HX, "utilities", tol=0.8, cut=False))
    grille = [box(hx0[0] + 60, hx0[0] + 420, hx0[1] - 3, hx0[1], 120 + 40 * k, 136 + 40 * k) for k in range(9)]
    P.append(Part("hx_grille", compound(*grille), (0.55, 0.57, 0.60), "utilities", tol=0.3, cut=False))
    P.append(Part("hx_display", box(hx0[0] + 140, hx0[0] + 340, hx0[1] - 4, hx0[1], 700, 800), SCREEN, "utilities",
                  tol=0.3, cut=False))
    # compressed-air drop: filter-regulator on the wall at the back left
    P.append(Part("air_frl", fuse(box(-320, -230, 980, 1000, 1350, 1520), cyl(26, 40, (-275, 960, 1430), (0, 1, 0))),
                  (0.35, 0.36, 0.40), "utilities", tol=0.3, cut=False))
    return P


def pipe_routes() -> dict[str, dict]:
    """Utility lines as centre-line polylines (rendered as tubes by PyVista, not CadQuery)."""
    cover_end = PLATE_C - STACK_DIR * 405
    fx0, fx1 = FR_X
    return {
        "water_supply": dict(color=WATER_IN, r=7, pts=[(678, 300, 260), (640, 320, 150), (600, 360, 140),
                                                        (fx1 + 2, 400, 400), (fx1 + 2, 420, 900)]),
        "water_return": dict(color=WATER_OUT, r=7, pts=[(678, 360, 290), (645, 380, 170), (605, 420, 160),
                                                         (fx1 + 2, 460, 420), (fx1 + 2, 480, 950)]),
        "argon": dict(color=ARGON_LINE, r=4, pts=[(-600, 755, 1470), (-650, 740, 1440), (-520, 700, 1200),
                                                  (-300, 560, 1150), (fx0 - 2, 520, 1180)]),
        "air": dict(color=AIR_LINE, r=4, pts=[(-275, 955, 1430), (-275, 880, 1300), (-330, 400, 800),
                                              (-340, 0, 640), tuple(cover_end + np.array([-20, 0, -8]))]),
        "vacuum": dict(color=VAC_LINE, r=17, pts=[(-500, 230, 270), (-470, 240, 420), (-380, 330, 560),
                                                  (-280, 420, 640), (fx0 - 2, 450, 660)]),
    }


def parts() -> list[Part]:
    return furnace_parts() + hood_parts() + chamber_parts() + stack_parts() + frame_parts() + utility_parts()


# ------------------------------------------------------------------------ variants built per frame
def pool_solid(level: float) -> cq.Shape:
    """Melt standing `level` mm above Z_CR (negative: still in the floor cone), round the rod."""
    rr = SEALING_ROD_D / 2 + 0.4
    if level <= floor_z(rr) + 0.5:
        level = floor_z(rr) + 0.5
    if level >= 0:
        pts = [(rr, floor_z(rr)), (CRUCIBLE_ID / 2 - 0.3, -0.3), (CRUCIBLE_ID / 2 - 0.3, level), (rr, level)]
    else:
        r_l = CRUCIBLE_ID / 2 * (1 + level / FLOOR_CONE_H)
        pts = [(rr, floor_z(rr)), (r_l - 0.3, level), (rr, level)]
    return lathe(pts, Z_CR)


def powder_solid(level: float) -> cq.Shape:
    """Powder heap in the container, `level` mm deep at the wall, slightly heaped in the middle."""
    level = max(level, 2.0)
    r = CONT_R - 5
    pts = [(0, 4), (r - 14, 4), (r, 18), (r, level), (0, level + min(18.0, level * 0.3))]
    if level < 18:
        pts = [(0, 4), (r - 14, 4), (r - 14 + level * 0.7, level), (0, level + 3)]
    return lathe(pts, CONT_Z[0], CHUTE_X)


# ------------------------------------------------------------------------------- tessellation
def _poly(shape: cq.Shape, tol: float):
    import pyvista as pv
    verts, tris = shape.tessellate(tol, 0.3)
    if not tris:
        return None
    pts = np.array([(v.x, v.y, v.z) for v in verts], float)
    faces = np.hstack([[3, *t] for t in tris]).astype(np.int64)
    return pv.PolyData(pts, faces)


def tess(shape: cq.Shape, tol: float = 0.4, split_cut: bool = False):
    """PyVista mesh of a CadQuery shape. With split_cut, returns (body, cut faces lying on y = 0)."""
    import pyvista as pv
    body, cut = [], []
    for f in shape.Faces():
        p = _poly(f, tol)
        if p is None:
            continue
        if split_cut and f.geomType() == "PLANE":
            bb = f.BoundingBox()
            if abs(bb.ymin) < 1e-4 and abs(bb.ymax) < 1e-4:
                cut.append(p)
                continue
        body.append(p)

    def merge(ps):
        if not ps:
            return None
        m = pv.merge(ps, merge_points=False) if len(ps) > 1 else ps[0]
        return m.compute_normals(split_vertices=True, feature_angle=40, auto_orient_normals=False)

    return (merge(body), merge(cut)) if split_cut else merge(body)


def halve(shape: cq.Shape) -> cq.Shape:
    """Keep y >= 0 (the camera looks from -y, so the cut faces point at it)."""
    return shape.cut(box(-3000, 3000, -3000, 0, -3000, 3000))


def _source_hash() -> str:
    return hashlib.sha1(Path(__file__).read_bytes()).hexdigest()[:12]


def meshes(force: bool = False) -> dict:
    """{name: dict(whole=mesh, half=mesh or None, half_cut=mesh or None, color, group, opacity)} (cached)."""
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"meshes_{_source_hash()}.pkl"
    if path.exists() and not force:
        return pickle.loads(path.read_bytes())
    out = {}
    for p in parts():
        whole = tess(p.shape, p.tol)
        half = half_cut = None
        gone = False
        if p.cut:
            try:
                h = halve(p.shape)
                if h.isValid() and h.Volume() > 1e-3:
                    half, half_cut = tess(h, p.tol, split_cut=True)
                else:
                    gone = p.shape.BoundingBox().ymax <= 1e-6
            except Exception as exc:  # noqa: BLE001 - a failed boolean just means no cutaway for that part
                print("halve failed:", p.name, exc)
        out[p.name] = dict(whole=whole, half=half, half_cut=half_cut, color=p.color, group=p.group,
                           opacity=p.opacity, cut=p.cut, gone=gone)
    path.write_bytes(pickle.dumps(out))
    return out


def variant_meshes(force: bool = False) -> dict:
    """Melt-pool and powder-heap meshes at a series of levels (whole and halved), cached."""
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"variants_{_source_hash()}.pkl"
    if path.exists() and not force:
        return pickle.loads(path.read_bytes())
    pool_levels = np.linspace(-14, 37, 35)
    powder_levels = np.linspace(3, 70, 24)
    out = {"pool_levels": pool_levels, "powder_levels": powder_levels, "pool": [], "pool_half": [],
           "powder": [], "powder_half": []}
    for lv in pool_levels:
        s = pool_solid(lv)
        out["pool"].append(tess(s, 0.1))
        out["pool_half"].append(tess(halve(s), 0.1, split_cut=True))
    for lv in powder_levels:
        s = powder_solid(lv)
        out["powder"].append(tess(s, 0.3))
        out["powder_half"].append(tess(halve(s), 0.3, split_cut=True))
    path.write_bytes(pickle.dumps(out))
    return out


if __name__ == "__main__":
    import time
    t = time.time()
    m = meshes(force=True)
    print(f"{len(m)} parts in {time.time() - t:.0f} s")
    for k, v in m.items():
        print(f"  {k:22s} {v['group']:12s} {v['whole'].n_cells if v['whole'] is not None else 0:7d} tris"
              f"{'  (cutaway)' if v['half'] is not None else ''}")
    t = time.time()
    variant_meshes(force=True)
    print(f"variants in {time.time() - t:.0f} s")
