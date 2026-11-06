"""v3's new and changed parts (CadQuery), after Sam's critiques of 2026-10-29. parts.py is v2's, unchanged.

Frames: Sam's studio frame for everything on the module or the electronics carriage (EC) (x along the auger from the
hinge axis, y along the hinge axis, z away from the plate; plate underside z = -18). EC parts are drawn in the EC's
own "as drawn" frame (Sam's Oct 13 Part Studio), which sits DOCK_RISE_V3 (0.9 mm) lower than when it is docked.
Every builder returns a solid in its own frame; layout.py places them.
"""
from __future__ import annotations

import math

import cadquery as cq

from params import *  # noqa: F401,F403
import parts as PT

DR = DOCK_RISE_V3          # docked z = as-drawn z + DR


def _cyl(r, h, x=0.0, y=0.0, z=0.0, axis="Z"):
    if axis == "Z":
        return cq.Workplane("XY").circle(r).extrude(h).translate((x, y, z))
    if axis == "Y":
        return cq.Workplane("XZ").circle(r).extrude(-h).translate((x, y, z))
    return cq.Workplane("YZ").circle(r).extrude(h).translate((x, y, z))


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


# ---------------------------------------------------------------- purchased bits
def kc_ball(d: float = KC_BALL_D) -> cq.Workplane:
    """Chrome-steel ball (52100, grade 25), centred on the origin."""
    return cq.Workplane("XY").sphere(d / 2)


def dowel(d: float = VEE_DOWEL_D, L: float = 8.0) -> cq.Workplane:
    """Hardened dowel pin along +y, centred on the origin, 0.3 mm chamfers."""
    return cq.Workplane("XZ").circle(d / 2).extrude(L / 2, both=True).edges().chamfer(0.3)


def disc_magnet(d: float = KC_MAG_D, h: float = KC_MAG_H) -> cq.Workplane:
    """N52 disc magnet (K&J D44-N52 by default): face at z = 0, body along -z."""
    return cq.Workplane("XY").circle(d / 2).extrude(-h)


def spring(od: float, length: float, wire: float = 0.4, turns: float = 8.0) -> cq.Workplane:
    """Compression spring as a stack of coil rings (a light stand-in for the helix): along +z from z = 0."""
    s = None
    n = int(turns)
    for k in range(n + 1):
        z = k * (length - wire) / n
        ring = cq.Workplane("XY").circle(od / 2).circle(od / 2 - wire).extrude(wire).translate((0, 0, z))
        s = ring if s is None else s.union(ring)
    return s


def steel_washer_flat(d: float = 8.0, t: float = 1.0) -> cq.Workplane:
    """Flat steel pad (M4 washer, ground face up) bonded into the cradle floor: the bottom Kelvin clamp's flat."""
    return cq.Workplane("XY").circle(d / 2).circle(2.2).extrude(-t)


# ---------------------------------------------------------------- 1. the plate side of the kinematic dock
def armature_v3() -> cq.Workplane:
    """Low-carbon steel armature, 2 mm (laser cut), Sam's frame: top face on the plate's underside (z -18) from x 86 to
    the plate's back edge, cantilevered on to x 118 under the EC's flat ball (C, x 112) and the dock electromagnet
    (x 100). Two countersunk M3 holes into heat-set inserts in the plate's back strip (v2's tab was 89-111, |y| <= 14)."""
    x0, x1 = ARMATURE_X3
    t = _box(x0, x1, -ARMATURE_HW3, ARMATURE_HW3, -18.0 - 2.0, -18.0).edges("|Z").fillet(2.0)
    for x, y in ARMATURE_SCREWS3:
        t = t.cut(_cyl(1.7, 5, x, y, -21.0))
        t = t.cut(cq.Workplane("XY").add(cq.Solid.makeCone(3.0, 1.6, 1.4, cq.Vector(x, y, -20.0), cq.Vector(0, 0, 1))))
    return t


def plate_additions() -> tuple[cq.Workplane, cq.Workplane]:
    """(material added to Sam's Oct 13 plate, material cut from it) for the v3 mounting plate, Sam's frame.

    Added: the latch keeper on the back end (|y| 14-24, top face z -13), the nothing else. Cut: pockets for the two dock balls (A, B; a 6.25 mm press fit 2.6 mm deep), the armature's
    insert holes, a 1 mm relief over the NEMA 11 (its top stands 0.25 mm under the plate when docked), the door push
    rod's clearance, and v2's locating-pin hole and slot are not cut (v2 cut them; v3 starts from Sam's file)."""
    add = None
    for sy in (-1, 1):
        k = _box(LATCH_KEEPER_X[0], LATCH_KEEPER_X[1], 14.0 if sy > 0 else -24.0, 24.0 if sy > 0 else -14.0, -18.0, -13.0)
        k = k.edges("|Z and >X").fillet(1.5)
        add = k if add is None else add.union(k)
    cut = None
    for (x, y) in (KC_A, KC_B):
        c = _cyl(3.125, 2.6 + 0.01, x, y, -18.01)                    # 6.25 press fit, the ball's centre at -18.6
        cut = c if cut is None else cut.union(c)
    for x, y in ARMATURE_SCREWS3:
        cut = cut.union(_cyl(2.0, 4.5, x, y, -18.01))
    cut = cut.union(_box(23.0, 69.0, -14.5, 14.5, -18.01, -17.0))     # NEMA 11 relief
    for sy in (-1, 1):                                                # M2 heat-set insert holes for the door housing's arms
        cut = cut.union(_cyl(1.6, 4.0, 18.5, sy * 13.7, -17.0))
    return add, cut


# ---------------------------------------------------------------- 1+2. the electronics carriage v3 (printed additions)
def ec_additions() -> tuple[cq.Workplane, cq.Workplane]:
    """(material added to Sam's Oct 13 electronics carriage, material cut) for EC v3, in the EC's as-drawn frame.
    Printed as one part with his carriage body (his file with these features added).

    Top (the dock): two ears outside his side walls at x 24-36 carry the cone seat (A, +y) and the dowel vee (B, -y)
    with a magnet pocket under each; v2's magnet bracket becomes a back bracket holding the dock electromagnet at x 100
    and the flat ball C at x 112. His top rim is cut 1 mm so only the three contacts touch the plate.
    Bottom (the guide's seat): a 3 mm base under both bays with three ball pockets (cone, vee, flat in the cradle) and a
    slotted clevis for the P16's rod end. Front: the door finger that lifts the outlet door's push rod."""
    zt = KC_SEAT_TOP - DR                                     # ear top, as drawn (-20.5)
    zb = KC_BALL_Z - DR                                       # dock balls' centres, as drawn (-19.5)
    add = None
    # ---- ears (cone +y, vee -y): x 24-36, |y| 14.6-22.6, from the ear top down to z -30, with a 45 deg chamfer under
    for sy in (-1, 1):
        x, y = KC_A if sy > 0 else KC_B
        y_in, y_out = 14.6, 22.8
        e = _box(x - 6.0, x + 6.0, y_in if sy > 0 else -y_out, y_out if sy > 0 else -y_in, -30.0, zt)
        under = (cq.Workplane("YZ").polyline([(sy * 18.0, -30.0), (sy * y_out, -30.0), (sy * y_out, -30.0 + (y_out - 18.0)), ])
                 .close().extrude(12.0).translate((x - 6.0, 0, 0)))
        e = e.cut(under)
        add = e if add is None else add.union(e)
    # ---- back bracket: foot on the back face (x 73.33), arms beside the pinion, cup for the electromagnet at x 100,
    # a boss for the flat ball at x 112
    mx, my = DOCK_MAG_XY3
    mag_face = -18.0 - 2.0 - 0.15 - DR                        # -21.05 as drawn (v2's DOCK_MAG_FACE_Z)
    ztop = mag_face - 0.3
    zbot = mag_face - 15.0 - 2.0
    foot = _box(73.33, 76.33, -18.0, 18.0, -26.5, -19.9 - EC_RIM_CUT)
    arms = _box(73.33, PAD_X0_V3 - 0.5, 12.0, 15.0, zbot, ztop).union(_box(73.33, PAD_X0_V3 - 0.5, -15.0, -12.0, zbot, ztop))
    cup = _cyl(12.0, ztop - zbot, mx, my, zbot)
    cx, cy = KC_C
    c_ball_z = -18.0 - 2.0 - KC_BALL_D / 2 - DR               # ball C's centre (as drawn), its top on the armature
    boss = _box(mx + 8.0, cx + 4.5, -5.5, 5.5, zbot, c_ball_z + 1.2)
    bracket = foot.union(arms).union(cup).union(boss)
    bracket = bracket.cut(_box(76.5, 89.5, -12.0, 12.0, zbot - 5.0, ztop + 5.0))   # open round the pinion and the 44T gear
    add = add.union(bracket)
    # ---- base under both bays, legs up to the back bay's floor, slotted clevis
    zb0, zb1 = EC_BASE_Z - EC_BASE_T, EC_BASE_Z
    base = _box(2.3, 73.3, -15.0, 15.0, zb0, zb1)
    for x in (31.0, 70.0):
        for y in (-12.5, 12.5):
            base = base.union(_box(x - 2.0, x + 2.0, y - 2.0, y + 2.0, zb1 - 0.01, -52.6))
    px, pz = EC_PIN
    c0, c1 = EC_CHEEK_Y
    for sy in (-1, 1):
        cheek = _box(px - 5.0, px + 5.0, c0 if sy > 0 else -c1, c1 if sy > 0 else -c0, pz - 4.6, zb0 + 0.01)
        base = base.union(cheek)
    add = add.union(base)
    # ---- door finger: a post in front of the auger's end face, under the push rod
    fy = DOOR_ROD_Y
    f_top = DOOR_ROD_BOTTOM + DOOR_TRAVEL - DR                # docked: lifts the strip's lower end DOOR_TRAVEL (door open)
    post = _box(-3.6, -0.6, fy - 2.0, fy + 2.0, -26.0, f_top)
    arm = _box(-3.6, 2.4, fy - 2.0, fy + 2.0, -26.0, -22.0)  # joins the post to the EC's front wall (x 2.3)
    add = add.union(post).union(arm)

    cut = None
    # rim cut: Sam's rim (z -18.9 as drawn) down EC_RIM_CUT, everywhere but the ears and the bracket
    cut = _box(-10.0, 76.0, -19.0, 19.0, -18.9 - EC_RIM_CUT, -15.0)
    # cone seat A: 90 deg cone truncated at the magnet face, magnet pocket under it
    ax, ay = KC_A
    c_contact = zb - KC_BALL_D / 2 * math.cos(math.radians(KC_CONE_HALF))
    r_contact = KC_BALL_D / 2 * math.sin(math.radians(KC_CONE_HALF))
    apex = c_contact - r_contact / math.tan(math.radians(KC_CONE_HALF))
    mag_top = zb - KC_BALL_D / 2 - KC_MAG_GAP
    r_top = (zt - apex) * math.tan(math.radians(KC_CONE_HALF))
    r_mag = (mag_top - apex) * math.tan(math.radians(KC_CONE_HALF))
    cone = cq.Workplane("XY").add(cq.Solid.makeCone(r_mag, r_top + 0.3, zt + 0.3 - mag_top, cq.Vector(ax, ay, mag_top), cq.Vector(0, 0, 1)))
    cut = cut.union(cone).union(_cyl(KC_MAG_D / 2 + 0.1, KC_MAG_H + 0.2, ax, ay, mag_top - KC_MAG_H - 0.2))
    # vee B: two dowels along y; their holes and a magnet pocket under the pair
    bx, by = KC_B
    h = math.sqrt((KC_BALL_D / 2 + VEE_DOWEL_D / 2) ** 2 - (VEE_SPACING / 2) ** 2)
    zd = zb - h
    for sx in (-1, 1):
        cut = cut.union(_cyl(VEE_DOWEL_D / 2 - 0.02, 8.02, bx + sx * VEE_SPACING / 2, by + 4.01, zd, axis="Y"))
    cut = cut.union(_box(bx - VEE_SPACING / 2 + 0.2, bx + VEE_SPACING / 2 - 0.2, by - 4.5, by + 4.5, zd, zt + 0.5))   # the groove
    cut = cut.union(_cyl(KC_MAG_D / 2 + 0.1, KC_MAG_H + 0.2, bx, by, zd - VEE_DOWEL_D / 2 - 0.4 - KC_MAG_H - 0.2))
    # electromagnet pocket (bonded in, face at mag_face) and the flat ball's pocket (pressed, 3.8 proud)
    cut = cut.union(_cyl(10.1, 15.0 + 5.0, mx, my, mag_face - 15.0))
    cut = cut.union(_cyl(3.125, 2.6, cx, cy, c_ball_z + KC_BALL_D / 2 - 3.8 - 2.6 + 0.01))
    # base: three ball pockets underneath (balls 3.8 proud), clevis slots for the pin
    for (x, y) in EC_BALLS:
        cut = cut.union(_cyl(3.125, 2.6, x, y, zb0 - 0.01))
    cut = cut.union(cq.Workplane("XZ").center(px, pz).slot2D(4.1 + EC_SLOT, 4.1, 90).extrude(10.0, both=True))

    return add, cut


def ec_ball_centres() -> dict:
    """Ball centres on the EC, as drawn: the flat ball C and the three base balls."""
    c_ball_z = -18.0 - 2.0 - KC_BALL_D / 2 - DR
    zb0 = EC_BASE_Z - EC_BASE_T
    out = {"C": (KC_C[0], KC_C[1], c_ball_z)}
    for name, (x, y) in zip(("base_cone", "base_vee", "base_flat"), EC_BALLS):
        out[name] = (x, y, zb0 + 2.6 - KC_BALL_D / 2)
    return out


def vee_dowel_centres() -> list:
    """The two vee dowels' centres on the EC, as drawn (axis along y)."""
    bx, by = KC_B
    h = math.sqrt((KC_BALL_D / 2 + VEE_DOWEL_D / 2) ** 2 - (VEE_SPACING / 2) ** 2)
    zd = KC_BALL_Z - DR - h
    return [(bx - VEE_SPACING / 2, by, zd), (bx + VEE_SPACING / 2, by, zd)]


def kc_magnet_tops() -> list:
    """(x, y, face z) of the two seat magnets, as drawn."""
    ax, ay = KC_A
    bx, by = KC_B
    zb = KC_BALL_Z - DR
    h = math.sqrt((KC_BALL_D / 2 + VEE_DOWEL_D / 2) ** 2 - (VEE_SPACING / 2) ** 2)
    return [(ax, ay, zb - KC_BALL_D / 2 - KC_MAG_GAP), (bx, by, zb - h - VEE_DOWEL_D / 2 - 0.4 - 0.2)]


# ---------------------------------------------------------------- 2. the guide (cradle) at the station
def cradle() -> cq.Workplane:
    """Printed guide cradle, in the parked EC's as-drawn frame (the cradle is fixed; layout places it so the parked EC's
    base balls sit in its seats). Floor under the base with a cone (front +y), a dowel vee along y (front -y) and a pocket
    for a steel flat (back); side walls at |y| 15.3-17.8 up to the EC's narrow body's top (z -29.5 as drawn), a front
    wall 0.3 mm ahead of the EC's front face, a low back lip; a slot for the P16's rod; a foot on a 2020 post."""
    zb0 = EC_BASE_Z - EC_BASE_T
    ball_z = zb0 + 2.6 - KC_BALL_D / 2
    floor_top = ball_z - 1.0                      # seats are cut down from the floor's top
    f0 = floor_top - 6.0
    xf, xb = 2.3 - GUIDE_CLEAR, 73.3 + 1.0
    floor_ = _box(xf - GUIDE_WALL_T, xb + 3.0, -15.0 - GUIDE_CLEAR - GUIDE_WALL_T, 15.0 + GUIDE_CLEAR + GUIDE_WALL_T, f0, floor_top)
    walls = None
    for sy in (-1, 1):
        y0 = 15.0 + GUIDE_CLEAR
        w = _box(xf - GUIDE_WALL_T, xb, y0 if sy > 0 else -y0 - GUIDE_WALL_T, y0 + GUIDE_WALL_T if sy > 0 else -y0, f0, -29.5)
        walls = w if walls is None else walls.union(w)
    front = _box(xf - GUIDE_WALL_T, xf, -15.0 - GUIDE_CLEAR - GUIDE_WALL_T, 15.0 + GUIDE_CLEAR + GUIDE_WALL_T, f0, -29.5)
    lip = _box(xb, xb + 3.0, -15.0, 15.0, f0, floor_top + 4.0)
    c = floor_.union(walls).union(front).union(lip)
    c = c.cut(_box(23.5, 39.4, -25.0, 25.0, floor_top + 1.0, 0.0))      # notch: Sam's side posts (x 29-39, |y| 18) and the dock ears pass
    # lead-in chamfers on the walls' tops (the EC re-enters from above and behind after a tilt)
    c = c.edges(">Z").chamfer(1.0)
    # seats: cone (front +y), vee (front -y), flat pocket (back)
    (x1, y1), (x2, y2), (x3, y3) = EC_BALLS
    c_contact = ball_z - KC_BALL_D / 2 * math.cos(math.radians(45))
    r_contact = KC_BALL_D / 2 * math.sin(math.radians(45))
    apex = c_contact - r_contact
    c = c.cut(cq.Workplane("XY").add(cq.Solid.makeCone(0.2, floor_top - apex + 0.5, floor_top + 0.5 - apex, cq.Vector(x1, y1, apex), cq.Vector(0, 0, 1))))
    h = math.sqrt((KC_BALL_D / 2 + VEE_DOWEL_D / 2) ** 2 - (VEE_SPACING / 2) ** 2)
    zd = ball_z - h
    for sx in (-1, 1):
        c = c.cut(_cyl(VEE_DOWEL_D / 2 - 0.02, 8.02, x2 + sx * VEE_SPACING / 2, y2 + 4.01, zd, axis="Y"))
    c = c.cut(_box(x2 - VEE_SPACING / 2 + 0.2, x2 + VEE_SPACING / 2 - 0.2, y2 - 4.5, y2 + 4.5, zd, floor_top + 0.5))
    c = c.cut(_cyl(4.1, 1.0 + 0.01, x3, y3, ball_z - KC_BALL_D / 2 - 1.0))          # flat: an 8 mm steel washer, face at the ball's bottom
    c = c.cut(_cyl(4.1, floor_top - (ball_z - KC_BALL_D / 2) + 0.5, x3, y3, ball_z - KC_BALL_D / 2))
    # the P16's rod and rod end pass up through the floor to the clevis
    px, pz = EC_PIN
    c = c.cut(_box(px - 5.5, px + 5.5, -13.5, 13.5, f0 - 1.0, floor_top + 5.0))    # the rod, the clevis cheeks, the pin's head and nut
    c = c.cut(_box(px, xb + 10.0, -5.5, 5.5, f0 - 1.0, floor_top + 5.0))          # the rod's path backward as the station tilts
    # foot: a tab off the -y wall onto the post (two M5 into the 2020's end: tapped centre bore and a T-nut bracket)
    return c


def cradle_seat_centres() -> list:
    """Where the cradle's dowels and flat pad sit, as drawn (parked EC frame): [(kind, x, y, z)]."""
    zb0 = EC_BASE_Z - EC_BASE_T
    ball_z = zb0 + 2.6 - KC_BALL_D / 2
    h = math.sqrt((KC_BALL_D / 2 + VEE_DOWEL_D / 2) ** 2 - (VEE_SPACING / 2) ** 2)
    (x2, y2), (x3, y3) = EC_BALLS[1], EC_BALLS[2]
    return [("dowel", x2 - VEE_SPACING / 2, y2, ball_z - h), ("dowel", x2 + VEE_SPACING / 2, y2, ball_z - h),
            ("flat", x3, y3, ball_z - KC_BALL_D / 2)]


# ---------------------------------------------------------------- 4. outlet door
DOOR_XB = 0.4 - DOOR_GAP                 # shutter's back face (the auger's end face is at x 0.4)
DOOR_XF = DOOR_XB - DOOR_T               # shutter's front face
DOOR_Y = (-5.0, DOOR_ROD_Y + DOOR_ROD_D / 2)   # shutter's edges: -5 .. 9 (the +y strip is the push strip)
DOOR_SPRING_X = DOOR_XF - DOOR_SPRING[0] / 2 + 0.05   # spring axis: in front of the shutter, clear of the auger's end face


def door_shutter() -> cq.Workplane:
    """Shutter (printed PETG, 1.5 mm), Sam's frame, CLOSED: back face DOOR_GAP in front of the auger's end face, covering
    the 3 mm exit (z -1.5..1.5) from z -6 to 8; its +y strip (y 6-9) runs on down past the auger and the plate's front as
    the push strip, to DOOR_ROD_BOTTOM, where the EC's finger meets it. A spring boss on top."""
    z0, z1 = DOOR_CLOSED_Z
    s = _box(DOOR_XF, DOOR_XB, DOOR_Y[0], DOOR_Y[1], z0, z1)
    strip = _box(DOOR_XF, DOOR_XB, DOOR_ROD_Y - DOOR_ROD_D / 2, DOOR_ROD_Y + DOOR_ROD_D / 2, DOOR_ROD_BOTTOM, z0 + 0.01)
    boss = _box(DOOR_XF - 1.8, DOOR_XB, -1.5, 1.5, z1 - 1.0, z1 + 1.0)
    return s.union(strip).union(boss).edges("|X").fillet(0.4)


def door_housing() -> cq.Workplane:
    """Printed door housing, Sam's frame: two rails with 0.2 mm clearance grooves for the shutter's edges, front lips
    over the edges (open between y -3.5 and 7.5, so nothing is in front of the exit), a cap with the spring pocket, a
    bush for the push strip below the auger, and two arms back beside the tube (|y| 12.8-14.6, under the hinge pins' e-clips)
    to the plate's top face at x 15-22 (an M2 x 8 into a heat-set insert each). Nothing of it is behind the shutter, so
    the auger's end face turns free."""
    z0, z1 = DOOR_CLOSED_Z
    top = DOOR_TOP
    xl = DOOR_XF - 1.6                                       # front lips' front face
    yl, yr = DOOR_Y
    h = None
    for (y0, y1) in ((-12.5, yl + 1.5), (yr - 1.5, 12.5)):
        r = _box(xl, DOOR_XB, y0, y1, z0 - 1.0, top)
        h = r if h is None else h.union(r)
    h = h.union(_box(DOOR_XF - 3.2, DOOR_XB, -12.5, 12.5, top - 3.0, top))
    h = h.union(_box(DOOR_XF - 3.2, xl, -4.0, 4.0, z1 - 1.0, top))           # spring tower in front of the shutter's top
    # groove for the shutter: its thickness + 0.2, its width + 0.4, from below up to the cap
    h = h.cut(_box(DOOR_XF - 0.1, DOOR_XB + 0.1, yl - 0.2, yr + 0.2, z0 - 2.0, top - 3.0))
    h = h.cut(_box(DOOR_XF - 1.9, DOOR_XB + 0.1, -2.0, 2.0, z1 - 1.5, top - 3.0))   # the boss and spring run in the tower
    h = h.cut(_cyl(DOOR_SPRING[0] / 2 + 0.2, 2.0, DOOR_SPRING_X, 0.0, top - 3.5))    # spring seat in the cap's underside
    # bush for the push strip, below the auger's end face (its bottom at z -12.5) and above the EC's finger (-12 open)
    bush = _box(xl, DOOR_XB, DOOR_ROD_Y - DOOR_ROD_D / 2 - 1.5, DOOR_ROD_Y + DOOR_ROD_D / 2 + 1.5, -11.6, -8.0)
    bush = bush.cut(_box(DOOR_XF - 0.15, DOOR_XB + 0.15, DOOR_ROD_Y - DOOR_ROD_D / 2 - 0.2, DOOR_ROD_Y + DOOR_ROD_D / 2 + 0.2, -12.0, -7.0))
    h = h.union(bush)
    h = h.union(_box(xl, DOOR_XB, DOOR_ROD_Y - 1.0, 13.0, -9.0, z0 - 0.5))      # ties the bush to the +y rail
    h = h.cut(_box(DOOR_XF - 0.15, DOOR_XB + 0.15, DOOR_ROD_Y - DOOR_ROD_D / 2 - 0.2, DOOR_ROD_Y + DOOR_ROD_D / 2 + 0.2, -12.0, z0 + 0.5))
    # arms back to the plate, beside the tube, under the e-clips (they reach z -4.4 round the hinge axis)
    for sy in (-1, 1):
        ya, yb = (12.8, 14.6) if sy > 0 else (-14.6, -12.8)
        h = h.union(_box(xl, 22.0, ya, yb, -13.0, -8.0))
        h = h.union(_box(xl, DOOR_XB, ya, yb, -8.0, z0 - 0.5))
        h = h.cut(_cyl(1.1, 6.0, 18.5, sy * 13.7, -13.5))
    return h


# ---------------------------------------------------------------- 4a. plate latch
def latch_bolt() -> cq.Workplane:
    """Printed latch bolt, Sam's frame, CLOSED (tip LATCH_LAP over the keeper's back end, at y = LATCH_Y): slides along
    x in the housing on the carriage; a dowel (the follower) pressed through its tail runs down through the carriage."""
    k0, k1 = LATCH_KEEPER_X
    tip = k1 - LATCH_LAP
    b = _box(tip, LATCH_FOLLOW_X + 3.0, LATCH_Y - LATCH_W / 2, LATCH_Y + LATCH_W / 2, -12.6, -9.6)
    b = b.edges("|Y and <X").chamfer(1.2)
    b = b.cut(_cyl(1.5, 4.0, LATCH_FOLLOW_X, LATCH_Y, -13.0))
    return b


def latch_follower() -> cq.Workplane:
    """3 mm x 18 mm dowel pin pressed into the bolt's tail, down through the carriage plate's slot; its tip 5.1 mm below
    the carriage's outer face (Sam's z -23), 1.5 mm clear of the rail's post. Along z, in Sam's frame at its x, y."""
    L = 18.0
    zt = -9.6 - 0.5
    return _cyl(1.5, L, 0, 0, zt - L).edges().chamfer(0.3)


def latch_housing() -> cq.Workplane:
    """The latch's printed guide, part of the v3 carriage (returned in Sam's frame for the carriage builder to place):
    a channel on the carriage's inner face (z -18) behind the plate, the bolt in a 0.2 mm clearance slot, a spring
    pocket behind it, a slot down through the carriage for the follower."""
    k1 = LATCH_KEEPER_X[1]
    x0, x1 = k1 + 2.5, LATCH_FOLLOW_X + 16.0              # 2.5 mm behind the keeper: its corner swings back 1.3 mm in the first 6 deg of tilt
    y0, y1 = LATCH_Y - LATCH_W / 2 - 2.5, LATCH_Y + LATCH_W / 2 + 2.5
    h = _box(x0, x1, y0, y1, -18.0, -7.0)
    h = h.cut(_box(x0 - 1, x1 - 3.0, LATCH_Y - LATCH_W / 2 - 0.2, LATCH_Y + LATCH_W / 2 + 0.2, -12.8, -9.4))
    # follower slot through the housing floor (and the carriage plate, cut in the carriage builder)
    h = h.cut(cq.Workplane("XY").center(LATCH_FOLLOW_X + LATCH_TRAVEL / 2, LATCH_Y).slot2D(LATCH_TRAVEL + 3.4, 3.4, 0)
              .extrude(10.0).translate((0, 0, -19.0)))
    return h


def latch_rail() -> cq.Workplane:
    """Fixed cam rail at the station (printed on an aluminium bar), in the station carriage's Sam frame: a bar along y
    (the travel) whose front face sits LATCH_TRAVEL behind the closed follower, with 25 deg ramps at both ends, so each
    carriage's bolt is drawn back while the carriage is within +-22 mm of the station and pushed home as it leaves."""
    xf = LATCH_FOLLOW_X + 1.5 + LATCH_TRAVEL          # rail face: follower's back edge when open
    zt = -23.0 - 0.6                                  # 0.6 mm under the carriage's outer face
    zb = zt - 6.0
    half = LATCH_RAIL_FLAT
    ramp = LATCH_TRAVEL / math.tan(math.radians(25))
    pts = [(xf, -half), (xf, half), (xf + LATCH_TRAVEL, half + ramp), (xf + 10.0, half + ramp), (xf + 10.0, -half - ramp),
           (xf + LATCH_TRAVEL, -half - ramp)]
    r = cq.Workplane("XY").polyline(pts).close().extrude(zt - zb).translate((0, LATCH_Y, zb))
    return r


# ---------------------------------------------------------------- v3 carriage
def carriage_v3(print_web: bool = False) -> cq.Workplane:
    """v2's carriage (parts.carriage) with: the snap hooks removed (the latch holds the plate now), the window reshaped
    for EC v3 (|u| <= 23.5 from the front to x 88 Sam, |u| <= 13 behind it, where the plate's back corners rest on two
    pads), the latch housing behind the plate and its follower slot through the plate."""
    c = PT.carriage(print_web)
    u0 = CAR_W / 2
    w0, w1 = CAR_W0 - CAR_T, CAR_W0
    # remove the snap hooks (arms and lips): everything on the inner face at the snap position; the ribs go back below
    snap = (cq.Workplane("XY").rect(2 * u0 + 2, 30.0).extrude(14).translate((0, w1 + 15.0 + 0.01, SNAP_X - 7.0)))
    c = c.cut(snap)
    for su in (-1, 1):                          # rebuild the ribs where v2 cut them for the hooks to flex
        rw, rh = RIB
        c = c.union(cq.Workplane("XY").center(su * (u0 - rw / 2), w1 + rh / 2).rect(rw, rh).extrude(16).translate((0, 0, SNAP_X - 8)))
    # the window runs on to Sam x WIN_BACK_V3 (EC v3's flat ball) at |u| <= 13; pads fill it under the plate's back corners
    c = c.cut(cq.Workplane("XY").box(26.0, CAR_T + 2, HINGE_X + WIN_BACK_V3 - WIN_X[1] + 1.0, centered=False)
              .translate((-13.0, w0 - 1.0, WIN_X[1] - 1.0)))
    xs0, xs1 = HINGE_X + PAD_X0_V3, WIN_X[1]
    for su in (-1, 1):
        c = c.union(cq.Workplane("XY").box(23.5 - PAD_U0_V3, CAR_T, xs1 - xs0, centered=False)
                    .translate((PAD_U0_V3 if su > 0 else -23.5, w0, xs0)))
    # latch housing (Sam's frame -> carriage frame: x_c = x_s + HINGE_X, u = y_s, w = z_s + HINGE_W)
    h = latch_housing()
    h = h.rotate((0, 0, 0), (1, 1, 1), -120)         # (x, y, z) -> (y, z, x): Sam x -> carriage z, y -> u (X), z -> w (Y)
    c = c.union(h.translate((0, HINGE_W, HINGE_X)))
    slot = (cq.Workplane("XY").center(LATCH_FOLLOW_X + LATCH_TRAVEL / 2, LATCH_Y).slot2D(LATCH_TRAVEL + 3.4, 3.4, 0)
            .extrude(30.0).translate((0, 0, -40.0)))
    c = c.cut(slot.rotate((0, 0, 0), (1, 1, 1), -120).translate((0, HINGE_W, HINGE_X)))
    return c


# ---------------------------------------------------------------- 5. enclosure
def acrylic_panel(w: float, h: float, cut: tuple | None = None, holes: list | None = None) -> cq.Workplane:
    """Clear cast acrylic sheet, w along x, h along y, ACRYLIC_T along z (z 0..t), corner at the origin. `cut`:
    (x0, y0, x1, y1) opening for a hatch; `holes`: [(x, y)] 5.5 mm mounting holes."""
    p = cq.Workplane("XY").box(w, h, ACRYLIC_T, centered=False).edges("|Z").fillet(4.0)
    if cut:
        x0, y0, x1, y1 = cut
        p = p.cut(_box(x0, x1, y0, y1, -1, ACRYLIC_T + 1).edges("|Z").fillet(3.0))
    for (x, y) in holes or []:
        p = p.cut(_cyl(2.75, ACRYLIC_T + 2, x, y, -1))
    return p


def hatch_door(w: float, h: float) -> cq.Workplane:
    """Hatch door: clear acrylic, 4 mm larger than its opening all round, hinge line along its -x edge (x = 0), with a
    printed knob on the free edge. z 0..t."""
    d = cq.Workplane("XY").box(w, h, ACRYLIC_T, centered=False).edges("|Z").fillet(3.0)
    knob = _cyl(8.0, 14.0, w - 18.0, h / 2, ACRYLIC_T).union(_cyl(5.0, 4.0, w - 18.0, h / 2, ACRYLIC_T + 14.0))
    return d.union(knob)


def hinge_leaf_pair() -> cq.Workplane:
    """Small stainless butt hinge, 1-1/2 x 1-1/2 in open (McMaster 1549A-class), leaves flat in the z = 0 plane, pin
    along y at x = 0; drawn open flat (the door's own angle is set by layout)."""
    leaf = _box(-19.05, 19.05, -19.05, 19.05, 0, 1.0)
    barrel = cq.Workplane("XZ").circle(2.4).extrude(19.05, both=True).translate((0, 0, 1.0))
    return leaf.union(barrel)


def magnetic_catch() -> cq.Workplane:
    """Panel magnetic catch (McMaster 1660A-class), 20 x 12 x 8 body, face at z = 0, body along -z."""
    return _box(-10.0, 10.0, -6.0, 6.0, -8.0, 0.0)


def turn_button() -> cq.Workplane:
    """Printed turn button that holds a hatch shut: a 3 mm spacer on the panel and a 24 x 10 x 3 tab on an M4 screw that
    turns over the door's edge; frame: panel face at z = 0, tab toward +x (over the door when locked), z up from the panel."""
    spacer = _cyl(5.0, ACRYLIC_T + 0.2, 0, 0, 0)
    tab = _box(-6.0, 18.0, -5.0, 5.0, ACRYLIC_T + 0.2, ACRYLIC_T + 3.2).edges("|Z").fillet(2.0)
    return spacer.union(tab).cut(_cyl(2.1, 10.0, 0, 0, -1.0))


def standoff(L: float = PANEL_STANDOFF) -> cq.Workplane:
    """Nylon spacer, 10 OD x L, M5 clearance: along +z from z = 0."""
    return cq.Workplane("XY").circle(5.0).circle(2.75).extrude(L)


def side_tab() -> cq.Workplane:
    """5a: printed tab at the loading position, on a side plate's inner face (parts.hold_down's frame: X = u along the
    travel, Y = w inward, Z = from the side plate's inner face toward the chain). A thin C round the carriage's tongue:
    a 3 mm lip HOLD_DOWN_GAP inside its inner face and a 3 mm foot SIDE_TAB_FOOT_GAP outside its outer face, both over
    only the tongue's -u 8 mm, so the carriage's own swap slide (+u 10 mm, which frees its hooks from the A-1 tabs) frees
    it from the tab too. Kept within 7 mm of the tongue outward, inside the enclosure's panels. Its web runs inward past
    the tongue's tip and takes two M5 x 10 from inside into tapped holes in the side plate (the frame's posts are right
    behind the plate here, so screws from outside had no room for their heads)."""
    tz = CAR_W0 + HOLD_DOWN_GAP                          # lip's underside (w)
    wf = CAR_W0 - CAR_T - SIDE_TAB_FOOT_GAP             # foot's top (w)
    tongue_end = SIDE_GAP + CAR_X0                       # 7: tongue tip's distance from the plate
    z_in = SIDE_GAP - 9.0                                # lip and foot stop 1 mm short of the carriage's full-width body (x -8):
    u0, u1 = -24.0, -12.0                                # its corner would catch the foot as the carriage comes out
    lip = _box(u0, u1, tz, tz + 3.0, tongue_end - 1.5, z_in)
    foot = _box(u0, u1, wf - 3.0, wf, tongue_end - 1.5, z_in)
    web = _box(u0, u1 + 10.0, wf - 3.0, tz + 3.0 + 14.0, 0.0, tongue_end - 1.5)
    t = lip.union(foot).union(web)
    for (y0, dy) in ((tz, 1.5), (wf, -1.5)):                  # lead-ins at the open (-u) end
        t = t.cut(cq.Workplane("XY").polyline([(u0 - 0.01, y0 - 0.01 * dy / abs(dy)), (u0 + 3.0, y0 - 0.01 * dy / abs(dy)), (u0 - 0.01, y0 + dy)])
                  .close().extrude(z_in + 1).translate((0, 0, -0.5)))
    for (u, w) in SIDE_TAB_INSERTS:
        t = t.cut(_cyl(2.75, 10.0, u, w, -1.0))                                # clearance (M5 x 8)
        t = t.cut(_cyl(4.6, 10.0, u, w, SIDE_TAB_CB_Z))                        # counterbore for the head, from the chain side
    return t


SIDE_TAB_INSERTS = ((-20.0, CAR_W0 + HOLD_DOWN_GAP + 14.0), (-8.0, CAR_W0 + HOLD_DOWN_GAP + 14.0))   # (u, w): M5 x 8 into the tapped plate, 6 mm clear of the post
SIDE_TAB_CB_Z = 1.5                                       # counterbore floor: 1.5 mm of web under the head, 6.35 mm of thread in the plate


# ---------------------------------------------------------------- 6. scale
def hr100a() -> tuple[cq.Workplane, cq.Workplane, cq.Workplane]:
    """A&D HR-100A (102 g x 0.1 mg), from A&D's HR-A/HR-AZ manual section 22 (external dimensions): base 198 wide,
    253 deep (61.5 + 191.5), sloped front with the display, pan dia 90 at 86.5 mm, round glass breeze break 156 inside
    and 198 inside height above the pan, 315 overall, top door 105 mm open. Frame: bench at z = 0, the pan's centre on
    the z axis, the display side toward -x. Returns (body, glass, pan)."""
    pc = HR_PAN_FROM_FRONT
    x0, x1 = -pc, -pc + HR_D
    base = _box(x0 + 20.0, x1, -HR_W / 2, HR_W / 2, 6.0, 80.0).edges("|Z").fillet(10.0)
    front = (cq.Workplane("XZ").polyline([(x0, 6.0), (x0 + 20.0, 6.0), (x0 + 20.0, 80.0), (x0 + 6.0, 60.0)]).close()
             .extrude(HR_W / 2 - 8.0, both=True))
    feet = None
    for x in (x0 + 30.0, x1 - 20.0):
        for y in (-80.0, 80.0):
            f = _cyl(7.0, 6.0, x, y, 0.0)
            feet = f if feet is None else feet.union(f)
    r_in = HR_CHAMBER_D_IN / 2
    ring_bot = _cyl(r_in + 8.0, 6.0, 0, 0, 80.0).cut(_cyl(r_in, 7.0, 0, 0, 79.5))
    top_z = HR_PAN_Z + HR_CHAMBER_H_IN
    lid = _cyl(r_in + 8.0, HR_H - top_z, 0, 0, top_z).cut(_cyl(38.0, HR_H - top_z + 1, 0, 0, top_z - 0.5))   # top door opening (closed: glass slide in it)
    posts = None
    for ang in (60, 120, 240, 300):
        a = math.radians(ang)
        p = _cyl(5.0, top_z - 86.0, (r_in + 4.0) * math.cos(a), (r_in + 4.0) * math.sin(a), 86.0)
        posts = p if posts is None else posts.union(p)
    body = base.union(front).union(feet).union(ring_bot).union(lid).union(posts)
    display = _box(x0 + 2.0, x0 + 18.0, -40.0, 40.0, 30.0, 58.0)
    body = body.union(display)
    glass = _cyl(r_in + 3.0, top_z - 86.0, 0, 0, 86.0).cut(_cyl(r_in, top_z - 85.0, 0, 0, 85.5))
    pan = _cyl(HR_PAN_D / 2, 2.0, 0, 0, HR_PAN_Z - 2.0).union(_cyl(4.0, HR_PAN_Z - 2.0 - 78.0, 0, 0, 78.0))
    return body, glass, pan


def beaker(d: float = BEAKER_D, h: float = BEAKER_H) -> cq.Workplane:
    """Low-form glass beaker with a spout lip, base at z = 0."""
    b = _cyl(d / 2, h).cut(_cyl(d / 2 - 1.2, h, 0, 0, 1.2))
    return b.union(_cyl(d / 2 + 1.0, 1.5, 0, 0, h - 1.5).cut(_cyl(d / 2 - 1.2, 2, 0, 0, h - 1.6)))


def cradle_with_arm(post_x: float, post_y: float) -> cq.Workplane:
    """The cradle plus a 6 mm arm from its -y wall to a 2020 post at (post_x, post_y) (Sam's x, y), resting on the post's
    top (an M6 into the post's tapped centre bore). Same frame as cradle()."""
    c = cradle()
    zb0 = EC_BASE_Z - EC_BASE_T
    f0 = zb0 + 2.6 - KC_BALL_D / 2 - 1.0 - 6.0
    y_wall = -(15.0 + GUIDE_CLEAR + GUIDE_WALL_T)
    arm = _box(post_x - 10.0, post_x + 10.0, post_y - 10.0, y_wall + 0.5, f0, f0 + 6.0)
    arm = arm.cut(_cyl(3.3, 8.0, post_x, post_y, f0 - 1.0))
    return c.union(arm)


LATCH_RAIL_Z0 = -23.0 - 0.6 - 6.0             # rail's underside, Sam's z at the station (rail 6 mm tall)


def latch_rail_with_arm(post_x: float, post_y: float) -> cq.Workplane:
    """The latch rail plus its arm to a 2020 post at (post_x, post_y), Sam's frame at the station. The arm runs behind the
    rail's working face (x >= the face + 2), so the followers, which pass in front of that face, never meet it."""
    r = latch_rail()
    xf = LATCH_FOLLOW_X + 1.5 + LATCH_TRAVEL
    zt = -23.0 - 0.6
    y_end = LATCH_Y - LATCH_RAIL_FLAT - LATCH_TRAVEL / math.tan(math.radians(25))
    arm = _box(xf + 2.0, max(xf + 10.0, post_x + 10.0), min(post_y - 10.0, y_end + 1.0), max(post_y + 10.0, y_end + 1.0), LATCH_RAIL_Z0, zt)
    pad = _box(post_x - 10.0, post_x + 10.0, post_y - 10.0, post_y + 10.0, LATCH_RAIL_Z0, zt)
    arm = arm.union(pad).cut(_cyl(3.3, 8.0, post_x, post_y, LATCH_RAIL_Z0 - 1.0))
    return r.union(arm)


def hinge_leaf() -> cq.Workplane:
    """One leaf of a small stainless butt hinge (1-1/2 in, McMaster 1549A-class): 19 x 38 x 1 mm, the knuckle along y
    at x = 0, the leaf toward +x, z 0..1."""
    leaf = _box(0.0, 19.0, -19.0, 19.0, 0.0, 1.0)
    barrel = cq.Workplane("XZ").circle(2.0).extrude(19.0, both=True).translate((0, 0, 1.0))
    return leaf.union(barrel)


def shoulder_screw_4x20() -> cq.Workplane:
    """18-8 shoulder screw, 4 mm x 20 mm shoulder, M3 x 5 thread, 6 x 3 head (the family of McMaster 90265A123): the EC's
    clevis pin through cheek, washers, the P16 rod end's tab, washers, cheek. Underside of the head at z = 0, shoulder
    along -z."""
    head = cq.Workplane("XY").circle(3.0).extrude(3.0).cut(cq.Workplane("XY").polygon(6, 2.0 / math.cos(math.pi / 6)).extrude(1.5).translate((0, 0, 1.5)))
    sh = cq.Workplane("XY").circle(2.0).extrude(-20.0)
    th = cq.Workplane("XY").circle(1.5).extrude(-5.0).translate((0, 0, -20.0))
    return head.union(sh).union(th)
