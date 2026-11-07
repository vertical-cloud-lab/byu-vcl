"""v4's new and changed parts (CadQuery): the augers ride OUTSIDE the loop (Sam's item 7 of 2026-10-29).

parts.py is v2's and parts3.py v3's, both unchanged here. Frames: Sam's studio frame for the module (x along the auger from
the hinge axis, y along the hinge axis, z away from the plate on the auger's side; plate underside z = -18). On a v4
carriage Sam's z points OUT of the loop, so the plate's underside sits on the carriage's outer face. The electronics
carriage v4 (EC v4) is Sam's Oct 13 carriage mirrored through the auger's axis plane (z -> -z): it docks from the auger's
side, its NEMA 11 32.25 mm beyond the auger, and two arms reach past the auger to the plate's auger-side face. EC parts are
drawn in that mirrored "as drawn" frame, which sits DOCK_RISE_V4 (-0.9 mm, i.e. 0.9 mm further out) from where it docks.
"""
from __future__ import annotations

import math

import cadquery as cq

from params import *  # noqa: F401,F403
import parts as PT
import parts3 as P3
from parts3 import _box, _cyl

DR4 = DOCK_RISE_V4         # docked z = as-drawn z + DR4


# ---------------------------------------------------------------- plate v4 (Sam's plate + the auger-side dock and a pin latch)
def plate_additions_v4() -> tuple[cq.Workplane, cq.Workplane]:
    """(added, cut) for the v4 mounting plate, Sam's frame. The dock is on the plate's auger side (top face, z -13), on the
    two strips beside the tube between the clamps: balls A (cone) and B (vee) pressed in 2.6 mm, a steel washer flush in
    a pocket at C (the flat). The latch keeper on the back end has a 4.2 mm hole along x for the latch's pin, so the plate
    is held both ways (the carriage's opening leaves nothing under it). The door housing's two M2 inserts as v3."""
    kx0, kx1 = LATCH4_KEEPER_X
    add = _box(kx0, kx1, 14.0, 24.0, -18.0, -9.0).edges("|Z and >X").fillet(1.5)
    cut = None
    for (x, y) in (KC4_A, KC4_B):
        c = _cyl(3.125, 2.61, x, y, -13.0 - 2.6)
        cut = c if cut is None else cut.union(c)
    cx, cy = KC4_C
    cut = cut.union(_cyl(KC4_PAD[0] / 2 + 0.1, KC4_PAD[1] + 0.01, cx, cy, -13.0 - KC4_PAD[1]))
    cut = cut.union(cq.Workplane("YZ").center(LATCH_Y, LATCH4_PIN[1]).circle(2.1).extrude(LATCH4_ENGAGE + 1.0).translate((kx1 - LATCH4_ENGAGE - 1.0, 0, 0)))
    for sy in (-1, 1):
        cut = cut.union(_cyl(1.6, 4.0, 18.5, sy * 13.7, -17.0))
    return add, cut


def flat_pad_v4() -> cq.Workplane:
    """M5 steel flat washer (case-hardened) flush in the plate's top face at C: face at z = 0, body along -z."""
    return cq.Workplane("XY").circle(KC4_PAD[0] / 2).circle(2.7).extrude(-KC4_PAD[1])


# ---------------------------------------------------------------- door v4 (v3's door turned over: it opens toward the plate)
def _door_body(sign: float) -> cq.Workplane:
    """v3's door housing body (rails, cap, spring tower, push-strip bush) with z -> sign * z, no mounting arms."""
    xb, xf = P3.DOOR_XB, P3.DOOR_XF
    z0, z1 = DOOR_CLOSED_Z
    top = DOOR_TOP
    xl = xf - 1.6
    yl, yr = P3.DOOR_Y
    h = None
    for (y0, y1) in ((-12.5, yl + 1.5), (yr - 1.5, 12.5)):
        r = _box(xl, xb, y0, y1, z0 - 1.0, top)
        h = r if h is None else h.union(r)
    h = h.union(_box(xf - 3.2, xb, -12.5, 12.5, top - 3.0, top))
    h = h.union(_box(xf - 3.2, xl, -4.0, 4.0, z1 - 1.0, top))
    h = h.cut(_box(xf - 0.1, xb + 0.1, yl - 0.2, yr + 0.2, z0 - 2.0, top - 3.0))
    h = h.cut(_box(xf - 1.61, xb + 0.01, -4.5, 4.5, z0 - 3.0, top - 2.5))
    h = h.cut(_box(xf - 1.9, xb + 0.1, -2.0, 2.0, z1 - 1.5, top - 3.0))
    h = h.cut(_cyl(DOOR_SPRING[0] / 2 + 0.2, 2.0, P3.DOOR_SPRING_X, 0.0, top - 3.5))
    bush = _box(xl, xb, DOOR_ROD_Y - DOOR_ROD_D / 2 - 1.5, DOOR_ROD_Y + DOOR_ROD_D / 2 + 1.5, -11.6, -8.0)
    bush = bush.cut(_box(xf - 0.15, xb + 0.15, DOOR_ROD_Y - DOOR_ROD_D / 2 - 0.2, DOOR_ROD_Y + DOOR_ROD_D / 2 + 0.2, -12.0, -7.0))
    h = h.union(bush)
    h = h.union(_box(xl, xb, DOOR_ROD_Y - 1.0, 12.5, -9.0, z0 - 0.5))
    h = h.cut(_box(xf - 0.15, xb + 0.15, DOOR_ROD_Y - DOOR_ROD_D / 2 - 0.2, DOOR_ROD_Y + DOOR_ROD_D / 2 + 0.2, -12.0, z0 + 0.5))
    return h.mirror("XY") if sign < 0 else h


def door_housing_v4() -> cq.Workplane:
    """The door housing turned over (the shutter now slides toward the plate to open, and its push strip runs out past the
    auger to where EC v4's finger meets it), on v3's two mounting arms beside the tube to the plate's top face (M2 x 8)."""
    h = _door_body(-1.0)
    xl = P3.DOOR_XF - 1.6
    for sy in (-1, 1):
        ya, yb = (12.8, 14.6) if sy > 0 else (-14.6, -12.8)
        h = h.union(_box(xl, 22.0, ya, yb, -13.0, -8.0))
        h = h.cut(_cyl(1.1, 6.0, 18.5, sy * 13.7, -13.5))
    return h


def door_shutter_v4() -> cq.Workplane:
    """v3's shutter turned over: closed it covers the exit from z -4 to 6; its strip runs out to z +22."""
    return P3.door_shutter().mirror("XY")


# ---------------------------------------------------------------- latch v4 (a pin in the keeper's hole)
LATCH4_TAIL = (110.0, 129.0)          # the bolt's printed carrier block (x), round the pin's tail and the follower. It starts at
                                      # 110 (was 118): the 22 mm pin ran through the follower at x 120 (26 mm3, found by the BoM
                                      # lookup); the pin is now 4 x 14, its tail pressed 6 mm into the block, 2.5 mm short of the follower
LATCH4_PIN_L = 14.0                   # McMaster 91595A-series 4 x 14 mm dowel


def latch_bolt_v4() -> cq.Workplane:
    """Latch bolt v4, Sam's frame, CLOSED: a 4 mm steel pin (dowel) along x whose tip is LATCH4_ENGAGE into the keeper's
    hole, pressed into a printed carrier block that slides in the housing; the follower dowel goes through the block."""
    kx1 = LATCH4_KEEPER_X[1]
    tip = kx1 - LATCH4_ENGAGE
    d, zp = LATCH4_PIN
    pin = cq.Workplane("YZ").center(LATCH_Y, zp).circle(d / 2).extrude(LATCH4_PIN_L).translate((tip, 0, 0)).edges("<X").chamfer(0.5)
    blk = _box(LATCH4_TAIL[0], LATCH4_TAIL[1], LATCH_Y - 4.0, LATCH_Y + 4.0, zp - 2.8, zp + 2.8)
    blk = blk.cut(_cyl(1.5, 10.0, LATCH_FOLLOW_X, LATCH_Y, zp - 5.0))
    return pin.union(blk)


def latch_follower_v4() -> cq.Workplane:
    """3 x 40 mm dowel through the carrier block, out of the housing on the auger's side to z +24, along z, in Sam's
    frame at the follower's x, y (as parts3.latch_follower, longer and pointing the other way)."""
    z0 = LATCH4_PIN[1] - 2.8
    return _cyl(1.5, LATCH4_FOLLOW_TIP - z0, 0, 0, z0).edges().chamfer(0.3)


def latch_housing_v4() -> cq.Workplane:
    """The latch's printed guide on the carriage's outer face (Sam's z -18), behind the keeper: a bore for the pin, a
    channel for the carrier block, a spring pocket behind it and a slot in its outer wall for the follower."""
    kx1 = LATCH4_KEEPER_X[1]
    x0, x1 = kx1 + 0.5, LATCH4_TAIL[1] + 9.0
    d, zp = LATCH4_PIN
    h = _box(x0, x1, LATCH_Y - 6.5, LATCH_Y + 6.5, -18.0, zp + 5.0)
    h = h.cut(cq.Workplane("YZ").center(LATCH_Y, zp).circle(d / 2 + 0.15).extrude(x1 - x0 + 2).translate((x0 - 1, 0, 0)))
    h = h.cut(_box(LATCH4_TAIL[0] - 0.3, x1 - 3.0, LATCH_Y - 4.2, LATCH_Y + 4.2, zp - 3.0, zp + 3.0))
    h = h.cut(cq.Workplane("XY").center(LATCH_FOLLOW_X + LATCH_TRAVEL / 2, LATCH_Y).slot2D(LATCH_TRAVEL + 3.4, 3.4, 0)
              .extrude(10.0).translate((0, 0, zp)))
    return h


def latch_rail_v4(post_x: float, post_y: float) -> cq.Workplane:
    """The station's latch rail, Sam's frame at the station: along y, 6.5 mm out from the passing augers' tubes, its face
    LATCH_TRAVEL behind the closed followers' tips (which reach z +24), 25 deg ramps at both ends; an arm behind the face to
    a 2020 post."""
    xf = LATCH_FOLLOW_X + 1.5 + LATCH_TRAVEL
    z0, z1 = 19.0, 25.0
    half = LATCH_RAIL_FLAT
    ramp = LATCH_TRAVEL / math.tan(math.radians(25))
    pts = [(xf, -half), (xf, half), (xf + LATCH_TRAVEL, half + ramp), (xf + 10.0, half + ramp), (xf + 10.0, -half - ramp),
           (xf + LATCH_TRAVEL, -half - ramp)]
    r = cq.Workplane("XY").polyline(pts).close().extrude(z1 - z0).translate((0, LATCH_Y, z0))
    y_end = LATCH_Y - half - ramp
    arm = _box(xf + 2.0, max(xf + 10.0, post_x + 10.0), min(post_y - 10.0, y_end + 1.0), max(post_y + 10.0, y_end + 1.0), z0, z1)
    pad = _box(post_x - 10.0, post_x + 10.0, post_y - 10.0, post_y + 10.0, z0, z1)
    return r.union(arm).union(pad).cut(_cyl(3.3, 10.0, post_x, post_y, z0 - 1.0))


# ---------------------------------------------------------------- cap rest at the station
def cap_rest(post_x: float, post_y: float) -> cq.Workplane:
    """Printed rest under the auger's cap at the station, Sam's frame at the station: a bar along y whose face sits
    CAP_REST_GAP beyond the cap's outermost line (z +14.5), with 2 mm lead-in ramps; while the station's rail holds the
    latch open, the module rests on it by its cap, and the EC lifts it off when it docks. An arm out to a 2020 post."""
    x0, x1 = CAP_REST_X
    zf = 14.5 + CAP_REST_GAP
    half, ramp = 30.0, 12.0
    prof = [(-half - ramp, zf + 2.0), (-half, zf), (half, zf), (half + ramp, zf + 2.0), (half + ramp, zf + 8.0), (-half - ramp, zf + 8.0)]
    bar = cq.Workplane("YZ").polyline(prof).close().extrude(x1 - x0).translate((x0, 0, 0))
    arm = _box(min(x0, post_x - 10.0), max(x1, post_x + 10.0), min(post_y - 10.0, -half - ramp), max(post_y + 10.0, -half - ramp + 1.0),
               zf + 2.0, zf + 8.0)
    return bar.union(arm).cut(_cyl(3.3, 10.0, post_x, post_y, zf + 1.0))


# ---------------------------------------------------------------- carriage v4
def carriage_v4(print_web: bool = False) -> cq.Workplane:
    """Printed (PETG) carriage v4 in the carriage frame (X = u along the travel, Y = w into the loop, Z = x front -> back).
    As v2's on the chain side (5 mm plate on the two A-1 tabs, screws from the outer face into locknuts in the printed hooks,
    tongues past both chains, edge ribs on the inner face, magnet pockets), 66 mm wide. The module sits on its OUTER face:
    a 51.6 mm opening from in front of the hinge to past the cap lets the module swing up through it into the loop, the
    hinge lugs stand out from the outer face round the plate's knuckles, and the latch housing sits on the outer face behind
    the plate. No snap hooks, no pads (the latch's pin holds the plate both ways)."""
    u0 = CAR_W / 2
    w0, w1 = CAR_W0 - CAR_T, CAR_W0
    xa, xb = -8.0, CHAIN_L + 8.0
    plate = (cq.Workplane("XY").rect(CAR_W, CAR_T).extrude(xb - xa).translate((0, (w0 + w1) / 2, xa)).edges("|Y").fillet(3))
    for x0, x1 in ((CAR_X0, xa + 1), (xb - 1, CAR_X1)):
        t = (cq.Workplane("XY").rect(TONGUE_W, CAR_T).extrude(x1 - x0).translate((0, (w0 + w1) / 2, x0)).edges("|Y").fillet(2))
        plate = plate.union(t)
    rw, rh = RIB
    rx0, rx1 = 17.0, CHAIN_L - 17.0
    for su in (-1, 1):
        rib = (cq.Workplane("XY").center(su * (u0 - rw / 2), w1 + rh / 2).rect(rw, rh).extrude(rx1 - rx0).translate((0, 0, rx0)))
        plate = plate.union(rib)
    ox0, ox1 = OPEN_X
    opening = (cq.Workplane("XY").rect(2 * OPEN_U, CAR_T + 2).extrude(ox1 - ox0).translate((0, (w0 + w1) / 2, ox0)).edges("|Y").fillet(3))
    plate = plate.cut(opening)
    # Sam's plate is +-27.02 wide from his x 60 to 100 (his back strip): the opening widens to OPEN_U_BACK there, so that
    # strip passes through the carriage plate when the module swings up (it touched the 25.8 mm edges at 5-10 deg)
    bx0, bx1 = OPEN_BACK_X
    plate = plate.cut(cq.Workplane("XY").rect(2 * OPEN_U_BACK, CAR_T + 2).extrude(bx1 - bx0).translate((0, (w0 + w1) / 2, HINGE_X + bx0))
                      .edges("|Y").fillet(1.5))
    # hinge lugs on the outer face: from w0 out past the hinge axis (w = HINGE_W), |u| LUG_U4..LUG_U4 + LUG_T
    lug_out = HINGE_W - 8.0
    for su in (-1, 1):
        lug = (cq.Workplane("YZ").center((w0 + lug_out) / 2, HINGE_X).rect(w0 - lug_out, 16).extrude(LUG_T)
               .translate((LUG_U4 if su > 0 else -LUG_U4 - LUG_T, 0, 0)))
        lug = lug.edges("|X and <Y").fillet(7.9)
        plate = plate.union(lug)
    pin = cq.Workplane("YZ").center(HINGE_W, HINGE_X).circle((PIN_D + 0.15) / 2).extrude(2 * u0 + 2).translate((-u0 - 1, 0, 0))
    plate = plate.cut(pin)
    for su in (-1, 1):
        u_out = LUG_U4 + LUG_T
        cb = cq.Workplane("YZ").center(HINGE_W, HINGE_X).circle(PIN_CBORE[0] / 2).extrude(PIN_CBORE[1] + 0.01)
        plate = plate.cut(cb.translate((u_out - PIN_CBORE[1], 0, 0)) if su > 0 else cb.translate((-u_out - 0.01, 0, 0)))
    # A-1 tabs: as v2 (screw from the outer face through plate and tab into the hook's locknut)
    for x in (A1_HOLE_C, CHAIN_L - A1_HOLE_C):
        plate = plate.cut(cq.Workplane("XZ").center(0, x).circle(3.4 / 2).extrude(CAR_T + 2).translate((0, w1 + 1, 0)))
        plate = plate.cut(cq.Workplane("XZ").center(0, x).circle(6.4 / 2).extrude(TAB_SCREW_CB).translate((0, w0 + TAB_SCREW_CB, 0)))
        plate = plate.union(PT.tab_hook(x > CHAIN_L / 2, print_web).translate((0, 0, x)))
    pin_end = PIN_LEN / 2
    for z0 in (pin_end - 0.8, CHAIN_L - pin_end - 0.8):
        plate = plate.cut(cq.Workplane("XY").center(4.6, 0.0).rect(23.8, 4.8).extrude(1.6).translate((0, 0, z0)))
    for x in (CAR_X0 + 7.0, CAR_X1 - 7.0):
        plate = plate.cut(cq.Workplane("XZ").center(0, x).circle(MAGNET_D / 2 + 0.15).extrude(MAGNET_H + 0.3).translate((0, w1 + 0.01, 0)))
    # latch housing on the outer face: Sam's frame -> carriage frame (x_c = x_s + HINGE_X, u = -y_s, w = HINGE_W - z_s)
    h = latch_housing_v4().mirror("XZ").mirror("XY")              # (x, y, z) -> (x, -y, -z)
    h = h.rotate((0, 0, 0), (1, 1, 1), -120)                      # (x, -y, -z) -> (-y, -z, x) = (u, w - HINGE_W, x_c - HINGE_X)
    plate = plate.union(h.translate((0, HINGE_W, HINGE_X)))
    return plate


# ---------------------------------------------------------------- EC v4: Sam's carriage turned over + arms round the auger
def ec_additions_v4() -> tuple[cq.Workplane, cq.Workplane]:
    """(added, cut) for EC v4, in its as-drawn frame (Sam's Oct 13 carriage mirrored z -> -z). Two arms run from its rim
    past the auger (|y| 15.5-23.5, between the clamps) to the plate's auger-side face: the +y arm carries the cone (A) and
    ball C (the flat's partner), the -y arm the dowel vee (B); an N52 behind each. Underneath, v3's base with the three seat
    balls and the slotted clevis (pin 12 mm below the base, cheeks 9.6 mm apart), turned over. At the front, the door
    finger. No dock electromagnet: there is no room for one beside the tube, and the module's weight and the carriage
    over it hold the dock (see the README)."""
    zt = KC4_SEAT_TOP - DR4                     # arms' seat faces, as drawn (-10.525)
    zb = KC4_BALL_Z - DR4                       # plate balls' centres, as drawn
    add = None
    (ax0, ax1), (bx0, bx1) = EC4_ARM_X
    y0, y1 = EC4_ARM
    cx, cy = KC4_C
    c_face = (-13.0 - DR4) + (KC_BALL_D - 2.6)  # ball C, pressed 2.6 into the arm, stands 3.75 proud; its tip on the pad (z -13 docked)
    arm_p = _box(ax0, ax1, y0, y1, zt, 30.0)
    arm_p = arm_p.cut(_box(cx - 6.0, ax1 + 1.0, y0 - 1.0, y1 + 1.0, zt - 1.0, c_face))   # the C end steps back to ball C's face
    arm_m = _box(bx0, bx1, -y1, -y0, zt, 30.0)
    add = arm_p.union(arm_m)
    # ---- base, legs and clevis (v3's, z -> -z)
    zb0, zb1 = -(EC_BASE_Z - EC_BASE_T), -EC_BASE_Z           # +63.8 (outer), +60.8
    base = _box(2.3, 73.3, -15.0, 15.0, zb1, zb0)
    for x in (31.0, 70.0):
        for y in (-12.5, 12.5):
            base = base.union(_box(x - 2.0, x + 2.0, y - 2.0, y + 2.0, 52.6, zb1 + 0.01))
    px, pz = EC_PIN[0], -EC_PIN[1]
    c0, c1 = EC_CHEEK_Y
    for sy in (-1, 1):
        base = base.union(_box(px - 5.0, px + 5.0, c0 if sy > 0 else -c1, c1 if sy > 0 else -c0, zb0 - 0.01, pz + 4.6))
    add = add.union(base)
    # ---- door finger: under the push strip's end (z +22 closed); docked it holds the strip DOOR_TRAVEL in
    fy = DOOR_ROD_Y
    f_top = -(DOOR_ROD_BOTTOM + DOOR_TRAVEL) - DR4            # as drawn: +14.4
    add = add.union(_box(-3.6, -0.6, fy - 2.0, fy + 2.0, f_top, 26.0)).union(_box(-3.6, 2.4, fy - 2.0, fy + 2.0, 22.0, 26.0))

    cut = None
    # cone A: opening toward the plate (-z), truncated at its magnet's face
    axx, ayy = KC4_A
    r = KC_BALL_D / 2
    c_contact = zb + r * math.cos(math.radians(KC_CONE_HALF))
    r_contact = r * math.sin(math.radians(KC_CONE_HALF))
    apex = c_contact + r_contact / math.tan(math.radians(KC_CONE_HALF))
    mag_face = zb + r + KC_MAG_GAP
    r_top = (apex - zt) * math.tan(math.radians(KC_CONE_HALF))
    r_mag = (apex - mag_face) * math.tan(math.radians(KC_CONE_HALF))
    cone = cq.Workplane("XY").add(cq.Solid.makeCone(r_top + 0.3, r_mag, mag_face - (zt - 0.3), cq.Vector(axx, ayy, zt - 0.3), cq.Vector(0, 0, 1)))
    cut = cone.union(_cyl(KC_MAG_D / 2 + 0.1, KC_MAG_H + 0.2, axx, ayy, mag_face))
    # vee B: two dowels along y beyond the ball, a groove toward the plate, a magnet beyond the dowels
    bxx, byy = KC4_B
    h = math.sqrt((r + VEE_DOWEL_D / 2) ** 2 - (VEE_SPACING / 2) ** 2)
    zd = zb + h
    for sx in (-1, 1):
        cut = cut.union(_cyl(VEE_DOWEL_D / 2 - 0.02, 8.02, bxx + sx * VEE_SPACING / 2, byy + 4.01, zd, axis="Y"))
    cut = cut.union(_box(bxx - VEE_SPACING / 2 + 0.2, bxx + VEE_SPACING / 2 - 0.2, byy - 4.5, byy + 4.5, zt - 0.5, zd))
    cut = cut.union(_cyl(KC_MAG_D / 2 + 0.1, KC_MAG_H + 0.2, bxx, byy, zd + VEE_DOWEL_D / 2 + 0.4))
    # ball C pocket (3.8 proud of its face) and its magnet behind it
    cut = cut.union(_cyl(3.125, 2.6, cx, cy, c_face - 0.01))
    cut = cut.union(_cyl(KC_MAG_D / 2 + 0.1, KC_MAG_H + 0.2, cx, cy, c_face + 2.6 + 0.4))
    # base: three seat-ball pockets on the outer face, the clevis slots
    for (x, y) in EC_BALLS:
        cut = cut.union(_cyl(3.125, 2.6, x, y, zb0 - 2.6 + 0.01))
    cut = cut.union(cq.Workplane("XZ").center(px, pz).slot2D(4.1 + EC_SLOT, 4.1, 90).extrude(12.0, both=True))
    return add, cut


def ec_ball_centres_v4() -> dict:
    """Ball centres on EC v4, as drawn: C (on the +y arm) and the three seat balls under the base."""
    cx, cy = KC4_C
    c_face = (-13.0 - DR4) + (KC_BALL_D - 2.6)
    zb0 = -(EC_BASE_Z - EC_BASE_T)
    out = {"C": (cx, cy, c_face + 2.6 - KC_BALL_D / 2)}
    for name, (x, y) in zip(("base_cone", "base_vee", "base_flat"), EC_BALLS):
        out[name] = (x, y, zb0 - 2.6 + KC_BALL_D / 2)
    return out


def vee_dowel_centres_v4() -> list:
    bxx, byy = KC4_B
    h = math.sqrt((KC_BALL_D / 2 + VEE_DOWEL_D / 2) ** 2 - (VEE_SPACING / 2) ** 2)
    zd = KC4_BALL_Z - DR4 + h
    return [(bxx - VEE_SPACING / 2, byy, zd), (bxx + VEE_SPACING / 2, byy, zd)]


def kc_magnet_faces_v4() -> list:
    """(x, y, face z) of EC v4's three seat magnets, as drawn; each magnet's body runs +z from its face."""
    zb = KC4_BALL_Z - DR4
    r = KC_BALL_D / 2
    h = math.sqrt((r + VEE_DOWEL_D / 2) ** 2 - (VEE_SPACING / 2) ** 2)
    cx, cy = KC4_C
    c_face = (-13.0 - DR4) + (KC_BALL_D - 2.6)
    return [(KC4_A[0], KC4_A[1], zb + r + KC_MAG_GAP), (KC4_B[0], KC4_B[1], zb + h + VEE_DOWEL_D / 2 + 0.4 + 0.1),
            (cx, cy, c_face + 2.6 + 0.5)]


def cradle_v4(post_x: float, post_y: float) -> cq.Workplane:
    """v3's guide cradle turned over (the parked EC v4 sits in it beyond the auger), its side walls notched where EC v4's
    arms pass; its arm out to a 2020 post at (post_x, post_y), Sam's frame."""
    c = P3.cradle_with_arm(post_x, post_y).mirror("XY")
    return c.cut(_box(37.5, 70.0, -25.0, 25.0, 0.0, 60.0))


STATION_RAILS_OUTER = 31.0            # Sam's z of the station rails' outer face, where they sit on their post


def station_rails_v4(post_x: float, post_y: float) -> cq.Workplane:
    """One printed part on one 2020 post, Sam's frame at the station: the latch rail (as latch_rail_v4) and the tube rest
    under the auger tubes behind the keeper (TUBE_REST_X, face 0.5 mm off the tubes' outer line z +12.5, lead-ins at both
    ends). While a carriage is at the station its latch is open and its module rests there by its tube; the EC lifts it
    off when it docks. A web behind the followers' tips (z 25-31) joins the two and runs to the post."""
    r = latch_rail_v4(post_x, post_y)
    x0, x1 = TUBE_REST_X
    zf = 12.5 + CAP_REST_GAP
    half, ramp = 46.0, 10.0
    prof = [(-half - ramp, zf + 2.0), (-half, zf), (half, zf), (half + ramp, zf + 2.0), (half + ramp, STATION_RAILS_OUTER), (-half - ramp, STATION_RAILS_OUTER)]
    rest = cq.Workplane("YZ").polyline(prof).close().extrude(x1 - x0).translate((x0, 0, 0))
    web = _box(x0, max(post_x + 10.0, LATCH_FOLLOW_X + 1.5 + LATCH_TRAVEL + 10.0), post_y - 10.0, post_y + 10.0, 25.0, STATION_RAILS_OUTER)
    pad = _box(post_x - 10.0, post_x + 10.0, post_y - 10.0, post_y + 10.0, 19.0, STATION_RAILS_OUTER)
    return r.union(rest).union(web).union(pad).cut(_cyl(3.3, 20.0, post_x, post_y, 18.0))
