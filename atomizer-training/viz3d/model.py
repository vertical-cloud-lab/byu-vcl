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

# --------------------------------------------------------------- machine layout (assumed, see README)
Z_PLATFORM = (1050.0, 1150.0)       # stainless furnace base, on top of the chamber
BODY_R, BODY_TOP = 135.0, 1345.0    # "BLUE POWER" furnace body
Z_CR = 1219.2                        # crucible datum: where the straight bore meets the floor cone
RIM = Z_CR + BORE_STRAIGHT
CRUCIBLE_BASE = Z_CR - FLOOR_CONE_H - CRUCIBLE_BOTTOM
HOOD_Z0, HOOD_H1, HOOD_H2 = BODY_TOP, 75.0, 90.0
HOOD_R0, HOOD_R1 = 142.0, 86.0
HINGE = np.array([-HOOD_R0, 0.0, BODY_TOP])       # lid hinge axis is along y through this point
ARM_DIR = np.array([math.cos(math.radians(30)), math.sin(math.radians(30)), 0.0])
POST_R = 108.0
SLUG_D, SLUG_L, SLUG_R = 17.0, 100.0, 20.0
SLUG_ANGLES = (105.0, 180.0, 255.0, 330.0)        # clear of the rod adapter and of the holder arm
TC_ANGLE = 142.0

CH_X, CH_Y, CH_Z = (-120.0, 240.0), (-180.0, 180.0), (620.0, 1050.0)   # chamber box: 57 L inside
CH_WALL = 4.0
CHUTE_X = 50.0                      # chute, valves and container axis (x, y = 0)
CHUTE_Z = (470.0, 620.0)
VALVE_Z = (438.0, 470.0)
CLAMP_Z = (424.0, 438.0)
CVALVE_Z = (392.0, 424.0)
CONT_Z = (150.0, 392.0)
CONT_R = 92.0
VIEWPORT = np.array([45.0, CH_Y[0], 960.0])

# Ultrasonic stack: comes in through the door (left wall) at 45 deg, plate face centre at PLATE_C.
STACK_DIR = np.array([math.cos(math.radians(45)), 0.0, math.sin(math.radians(45))])  # transducer -> plate
PLATE_UP = np.array([-STACK_DIR[2], 0.0, STACK_DIR[0]])                              # up the plate's slope
IMPACT_S = 25.0                       # the stream lands this far up the plate from its centre
PLATE_C = np.array([IMPACT_S * STACK_DIR[2], 0.0, 880.0])   # chosen so the stream at x = 0 lands high
IMPACT = PLATE_C + IMPACT_S * PLATE_UP
NOZZLE_EXIT_Z = 1150.0

DOOR_HINGE = np.array([CH_X[0] - 8.0, CH_Y[1] - 6.0])  # vertical hinge axis at the back edge


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
    # nozzle holder under the crucible (graphite), nozzle plate in its top recess, white side up
    holder = lathe([(1.0, -25), (15, -25), (15, 0), (8.2, 0), (8.2, -5), (1.0, -5)], CRUCIBLE_BASE)
    P.append(Part("nozzle_holder", holder, GRAPHITE, "crucible", tol=0.1))
    P.append(Part("nozzle", lathe([(0.6, -5), (8, -5), (8, -1), (0.6, -1)], CRUCIBLE_BASE), GRAPHITE,
                  "nozzle", tol=0.05))
    P.append(Part("nozzle_white", lathe([(0.6, -1), (8, -1), (8, 0), (0.6, 0)], CRUCIBLE_BASE), INSUL,
                  "nozzle", tol=0.05))
    P.append(Part("crucible_nut", lathe([(15.5, 1150), (23, 1150), (23, 1160), (15.5, 1160)]), GRAPHITE,
                  "furnace", tol=0.1))
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


def chamber_parts() -> list[Part]:
    P = []
    x0, x1 = CH_X
    y0, y1 = CH_Y
    z0, z1 = CH_Z
    outer = rbox(x0, x1, y0, y1, z0, z1, 40)
    inner = rbox(x0 + CH_WALL, x1 - CH_WALL, y0 + CH_WALL, y1 - CH_WALL, z0 + CH_WALL, z1 - CH_WALL, 36)
    shell = outer.cut(inner)
    shell = shell.cut(box(x0 - 5, x0 + CH_WALL + 5, y0 + 30, y1 - 30, z0 + 40, z1 - 40))     # door opening
    shell = shell.cut(cyl(45, 30, VIEWPORT + np.array([0, -10, 0]), (0, 1, 0)))              # view port
    shell = shell.cut(cyl(52, 30, (CHUTE_X, 0, z0 - 10)))                                    # to the chute
    shell = shell.cut(cyl(22, 30, (0, 0, z1 - 10)))                                          # from the furnace
    P.append(Part("chamber", shell.clean(), STEEL, "chamber", tol=0.5))
    # cooling slots on the right wall (the vertical louvres in the photos)
    slots = [box(x1 - 1, x1 + 2, y0 + 50 + 26 * k, y0 + 58 + 26 * k, z0 + 60, z1 - 70) for k in range(10)]
    P.append(Part("chamber_slots", compound(*slots), STEEL_DK, "chamber", tol=0.3))
    # view port: dark-grey 12-sided flange with the light-blue glass
    vp = cq.Workplane("XZ").polygon(12, 175).extrude(46).val()
    vp = vp.cut(cyl(44, 60, (0, 5, 0), (0, -1, 0))).translate(V(*(VIEWPORT + np.array([0, 0, 0]))))
    P.append(Part("viewport_flange", vp, FLANGE, "chamber", tol=0.3))
    P.append(Part("viewport_glass", cyl(45, 6, VIEWPORT + np.array([0, -20, 0]), (0, 1, 0)), GLASS, "chamber",
                  opacity=0.8, tol=0.2))
    # door on the left wall, hinged at its back edge; the stack goes through it at 45 deg
    door = box(x0 - 16, x0, y0 + 14, y1 - 14, z0 + 18, z1 - 18)
    door = door.fuse(rbox(x0 - 30, x0 - 16, y0 + 40, y1 - 40, z0 + 45, z1 - 45, 10))
    port = PLATE_C - STACK_DIR * (194 + 0)      # booster flange sits here, in the door plane
    door = door.cut(along(cyl(30, 200, (0, 0, 0)), port - STACK_DIR * 100, STACK_DIR))
    door = door.fuse(along(tube(42, 30, 60, (0, 0, 0)), port - STACK_DIR * 45, STACK_DIR))
    P.append(Part("door", door.clean(), STEEL, "door", tol=0.4))
    P.append(Part("door_hinge", compound(*[cyl(8, 60, (DOOR_HINGE[0], DOOR_HINGE[1], z), (0, 0, 1))
                                           for z in (z0 + 60, z1 - 120)]), STEEL_DK, "chamber", tol=0.2,
                  cut=False))
    # three toggle clamps on the door's front edge (bodies on the chamber, levers swing)
    for k, z in enumerate((z0 + 75, (z0 + z1) / 2, z1 - 75)):
        P.append(Part(f"clamp_body{k}", box(x0 - 6, x0 + 30, y0 - 16, y0, z - 16, z + 16), STEEL_DK, "chamber",
                      tol=0.2))
        lever = fuse(box(x0 - 40, x0 - 4, y0 - 26, y0 - 12, z - 7, z + 7), cyl(9, 30, (x0 - 40, y0 - 34, z), (0, 1, 0)))
        P.append(Part(f"clamp{k}", lever, BLACK, f"clamp{k}", tol=0.2))
    # splash plate and catch bowl inside, on the chamber floor
    P.append(Part("catch_bowl", lathe([(70, 0), (95, 0), (118, 34), (114, 34), (92, 4), (70, 4)], z0 + CH_WALL,
                                      CHUTE_X - 10, 0), STEEL_DK, "bowl", tol=0.3))
    splash = cq.Workplane("XY").rect(150, 120).extrude(3).val().rotate(V(0, 0, 0), V(0, 1, 0), -20)
    P.append(Part("splash_plate", splash.translate(V(CHUTE_X + 70, 0, z0 + 90)), STEEL, "splash", tol=0.3))
    # chute cone down to the valves and the airlock powder container
    lo = cq.Workplane("XY").workplane(offset=CHUTE_Z[1]).rect(300, 300).workplane(offset=-(CHUTE_Z[1] - CHUTE_Z[0])) \
        .circle(56).loft().val()
    li = cq.Workplane("XY").workplane(offset=CHUTE_Z[1] + 1).rect(292, 292).workplane(
        offset=-(CHUTE_Z[1] - CHUTE_Z[0]) - 2).circle(52).loft().val()
    P.append(Part("chute", lo.cut(li).translate(V(CHUTE_X, 0, 0)), STEEL, "chamber", tol=0.4))
    P.append(Part("valve", fuse(tube(80, 52, VALVE_Z[1] - VALVE_Z[0], (CHUTE_X, 0, VALVE_Z[0])),
                                box(CHUTE_X - 12, CHUTE_X + 12, -130, -80, VALVE_Z[0] + 8, VALVE_Z[1] - 8)),
                  STEEL_DK, "chamber", tol=0.3))
    P.append(Part("valve_handle", box(CHUTE_X - 6, CHUTE_X + 120, -150, -130, VALVE_Z[0] + 10, VALVE_Z[1] - 10),
                  RED, "chamber", tol=0.2))
    # container (two people lift it into the clamp), its own valve and the clamped flange
    cont = lathe([(0, 0), (CONT_R - 15, 0), (CONT_R, 15), (CONT_R, CONT_Z[1] - CONT_Z[0] - 10),
                  (88, CONT_Z[1] - CONT_Z[0] - 10), (88, CONT_Z[1] - CONT_Z[0]), (0, CONT_Z[1] - CONT_Z[0])],
                 CONT_Z[0], CHUTE_X)
    cont = cont.cut(lathe([(0, 4), (CONT_R - 18, 4), (CONT_R - 4, 18), (CONT_R - 4, CONT_Z[1] - CONT_Z[0] + 5),
                           (0, CONT_Z[1] - CONT_Z[0] + 5)], CONT_Z[0], CHUTE_X))
    cont = cont.fuse(tube(78, 52, CVALVE_Z[1] - CVALVE_Z[0], (CHUTE_X, 0, CVALVE_Z[0])))
    cont = cont.fuse(box(CHUTE_X - 10, CHUTE_X + 10, -118, -76, CVALVE_Z[0] + 6, CVALVE_Z[1] - 6))
    P.append(Part("container", cont.clean(), STEEL, "container", tol=0.4))
    P.append(Part("container_handle", box(CHUTE_X - 5, CHUTE_X + 105, -134, -118, CVALVE_Z[0] + 8,
                                          CVALVE_Z[1] - 8), GREEN, "container", tol=0.2))
    P.append(Part("flange_clamp", fuse(tube(84, 54, CLAMP_Z[1] - CLAMP_Z[0], (CHUTE_X, 0, CLAMP_Z[0])),
                                      cyl(6, 40, (CHUTE_X + 84, 0, (CLAMP_Z[0] + CLAMP_Z[1]) / 2), (1, 0, 0)),
                                      sphere(10, (CHUTE_X + 128, 0, (CLAMP_Z[0] + CLAMP_Z[1]) / 2))),
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


def cabinet_parts() -> list[Part]:
    P = []
    P.append(Part("floor", box(-1100, 1450, -700, 1550, -6, 0), FLOOR, "static", tol=2.0, cut=False))
    P.append(Part("base_frame", fuse(box(-330, 470, -230, -190, 60, 110), box(-330, 470, 680, 720, 60, 110),
                                     box(-330, -290, -230, 720, 60, 110), box(430, 470, -230, 720, 60, 110)),
                  FRAME, "static", tol=1.0, cut=False))
    feet = [fuse(cyl(18, 60, (x, y, 0)), cyl(32, 10, (x, y, 0))) for x in (-300, 414) for y in (-200, 400)]
    P.append(Part("feet", compound(*feet), FRAME, "static", tol=0.5, cut=False))
    P.append(Part("cabinet", rbox(-210, 440, 215, 700, 110, 1780, 12), BLUE, "static", tol=0.8, cut=False))
    P.append(Part("platform", rbox(-150, 330, -170, 215, Z_PLATFORM[0], Z_PLATFORM[1], 90).cut(
        cyl(25, 120, (0, 0, Z_PLATFORM[0] - 10))), STEEL, "furnace", tol=0.5))
    P.append(Part("chamber_mount", box(-120, 240, 180, 215, 640, 1050), STEEL_DK, "static", tol=0.5, cut=False))
    # melting control panel ("GU 500 AMA"): white housing, blue LCD, keypad
    px0, px1, pz0, pz1 = 262, 412, 1360, 1580
    P.append(Part("control_panel", rbox(px0, px1, 203, 215, pz0, pz1, 6), PANEL, "static", tol=0.3, cut=False))
    P.append(Part("panel_lcd", box(px0 + 18, px1 - 18, 200, 203, pz1 - 95, pz1 - 25), LCD, "static", tol=0.2,
                  cut=False))
    keys = [box(px0 + 20 + 23 * i, px0 + 38 + 23 * i, 199, 203, pz0 + 30 + 26 * j, pz0 + 46 + 26 * j)
            for i in range(5) for j in range(3)]
    P.append(Part("panel_keys", compound(*keys), (0.35, 0.36, 0.40), "static", tol=0.2, cut=False))
    # main switch: yellow plate, red rotary handle
    P.append(Part("main_switch", box(300, 390, 205, 215, 1150, 1240), YELLOW, "static", tol=0.2, cut=False))
    P.append(Part("main_switch_handle", fuse(cyl(22, 14, (345, 205, 1195), (0, -1, 0)),
                                            box(335, 355, 172, 192, 1160, 1232)), RED, "switch", tol=0.2, cut=False))
    # 15.6 in HMI on a black swing arm off the cabinet's right edge
    arm = fuse(box(440, 470, 300, 340, 1400, 1460), along(cyl(14, 190), (465, 320, 1430), (0.45, -0.89, 0)),
               cyl(20, 50, (548, 150, 1405)))
    P.append(Part("hmi_arm", arm, BLACK, "static", tol=0.4, cut=False))
    hmi = rbox(-205, 205, -22, 22, -135, 135, 8)
    hmi_screen = box(-188, 188, -26, -21, -112, 112)
    widgets = [box(-170 + 70 * i, -120 + 70 * i, -28, -25, 40 - 40 * j, 62 - 40 * j)
               for i in range(5) for j in range(3) if (i + j) % 2 == 0]
    rot = lambda s: s.rotate(V(0, 0, 0), V(0, 0, 1), -18).translate(V(600, 95, 1455))
    P.append(Part("hmi", rot(hmi), BLACK, "static", tol=0.4, cut=False))
    P.append(Part("hmi_screen", rot(hmi_screen), SCREEN, "static", tol=0.3, cut=False))
    P.append(Part("hmi_widgets", rot(compound(*widgets)), (0.55, 0.70, 0.85), "static", tol=0.3, cut=False))
    P.append(Part("cabinet_ports", compound(cyl(30, 14, (-210, 450, 660), (-1, 0, 0)),
                                            cyl(12, 12, (-210, 520, 1180), (-1, 0, 0))), STEEL_DK, "static",
                  tol=0.3, cut=False))
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
    return {
        "water_supply": dict(color=WATER_IN, r=7, pts=[(678, 300, 260), (600, 320, 120), (480, 380, 110),
                                                        (443, 400, 400), (443, 420, 1000)]),
        "water_return": dict(color=WATER_OUT, r=7, pts=[(678, 360, 290), (610, 380, 140), (490, 440, 130),
                                                         (443, 460, 420), (443, 480, 1050)]),
        "argon": dict(color=ARGON_LINE, r=4, pts=[(-600, 755, 1470), (-650, 740, 1440), (-520, 700, 1200),
                                                  (-300, 560, 1150), (-212, 520, 1180)]),
        "air": dict(color=AIR_LINE, r=4, pts=[(-275, 955, 1430), (-275, 880, 1300), (-330, 400, 800),
                                              (-340, 0, 560), tuple(cover_end + np.array([-20, 0, -8]))]),
        "vacuum": dict(color=VAC_LINE, r=17, pts=[(-500, 230, 270), (-470, 240, 420), (-380, 330, 560),
                                                  (-280, 420, 640), (-215, 450, 660)]),
    }


def parts() -> list[Part]:
    return furnace_parts() + hood_parts() + chamber_parts() + stack_parts() + cabinet_parts() + utility_parts()


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
