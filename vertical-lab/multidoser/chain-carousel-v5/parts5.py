"""v5 parts: the A&D HR-202i balance, the beaker riser, the lift bar and its shoes, guides and P16 mounts, and EC v5 (EC
v4 with its clevis replaced by two saddles that clamp the lift bar). Each builder works in its own frame, given in its
docstring; layout.py places them.
"""
from __future__ import annotations

import math

import cadquery as cq

from params import *  # noqa: F401,F403
import parts as PT
import parts3 as P3
import parts4 as P4
from parts3 import _box, _cyl


# ---------------------------------------------------------------- A&D HR-202i
def hr202i(door_left: float = 0.0, door_right: float = 0.0, top_door: float = 0.0) -> dict[str, cq.Workplane]:
    """The HR-202i in named solids, its frame: origin on the bench under the pan's centre, x from the display (front, -x)
    to the mechanism tower (+x), y across, z up. Doors slide back (+x) by the given mm. From A&D's HR-i manual, 15.1
    "External Dimensions": 217 x 442 x 316 mm overall, body 200 x 428 x 310; pan dia. 90, its centre 163 mm behind the
    front; chamber 183 x 164.5 inside and 250 high above the pan; side doors 148.5 x 251; top door 164 x 148.5. The pan's
    height (50 mm) and the display's slope are read off the drawing, not dimensioned. Outline as byu-vcl's lab_models
    (vertical-lab/lab_models/labware.py, HR202I), re-drawn in this frame; the feet are inside the base's outline."""
    W, D, H = HR2_W, HR2_D, HR2_H
    x0 = -HR2_PAN_Y                                  # front of the body
    x1 = x0 + D                                      # back of the tower
    g, fr = HR2_GLASS, HR2_FRAME
    cw, cd, ch = HR2_CH
    cx0 = x0 + HR2_CH_Y                              # chamber's front glass, inside face
    cx1 = cx0 + cd                                   # the tower's front
    zf = HR2_FLOOR                                   # chamber floor and door sills (A&D's DXF: 40)
    ztop = HR2_PAN_TOP + ch                          # chamber ceiling (inside): 250 over the pan
    hw = cw / 2
    out: dict[str, cq.Workplane] = {}
    xs = cx0 - g - 2.0                               # the display section ends at the chamber's front frame
    body = _box(xs, x1, -W / 2, W / 2, 0.0, zf).edges("|Z").fillet(6.0)
    # behind the chamber: its back wall and the frame that carries the top door's rails, full height, then the lower rear
    # housing (A&D's DXF: x 276-428 from the front, its top 244 falling to 221 at the back); the doors slide back over it
    xr = x0 + HR2_REAR[0]
    body = body.union(_box(cx1, xr, -W / 2 + 0.5, W / 2 - 0.5, 1.0, H))
    rear = (cq.Workplane("XZ").polyline([(xr - 1.0, 1.0), (x1 - 0.5, 1.0), (x1 - 0.5, HR2_REAR[2]), (xr - 1.0, HR2_REAR[1])]).close()
            .extrude(W / 2 - 1.0, both=True))
    body = body.union(rear)
    # the display section, 73 deep: its top rises from 28 at the nose to 50 at the glass (A&D's DXF; a 600 mm radius, drawn flat)
    n0, n1 = HR2_NOSE
    nose = (cq.Workplane("XZ").polyline([(x0, 1.0), (xs + 1.0, 1.0), (xs + 1.0, n1 + 4), (x0 + 6, n0 + 4), (x0, n0)]).close()
            .extrude(W / 2 - 0.5, both=True))
    body = body.union(nose)
    for sy in (-1, 1):
        ya, yb = sorted((sy * hw, sy * (hw + fr)))
        body = body.union(_box(cx0 - g - 2, cx0 + 4, ya, yb, zf, ztop))               # front posts
        body = body.union(_box(cx0, cx1, ya, yb, zf, zf + 6))                          # door sills
    tw, td = HR2_TOP_DOOR
    ring = _box(cx0 - g - 2, cx1 + g, -hw - fr, hw + fr, ztop, H).cut(_box(cx0 + 8, cx0 + 8 + td, -tw / 2, tw / 2, ztop - 1, H + 1))
    body = body.union(ring)
    body = body.union(_cyl(HR2_PAN_D / 2 + 7, 4.0, 0, 0, zf).cut(_cyl(HR2_PAN_D / 2 + 3, 6.0, 0, 0, zf - 1)))   # breeze ring
    out["hr202i_body"] = body
    ang = math.atan2(n1 - n0, xs - x0 - 6)
    org = ((x0 + 6 + xs) / 2, 0.0, (n0 + 4 + n1 + 4) / 2 + 0.4)
    pl = cq.Plane(origin=org, xDir=(0, 1, 0), normal=(-math.sin(ang), 0, math.cos(ang)))
    out["hr202i_display"] = cq.Workplane(pl).rect(110.0, 30.0).extrude(0.8)
    out["hr202i_front_glass"] = _box(cx0 - g, cx0, -hw, hw, zf, ztop)
    out["hr202i_pan"] = _cyl(HR2_PAN_D / 2, 2.0, 0.0, 0.0, HR2_PAN_TOP - 2.0).union(_cyl(7.0, HR2_PAN_TOP - 2.0 - zf + 0.5, 0.0, 0.0, zf - 0.5))
    dw, dh = HR2_DOOR
    for name, sy, slide in (("hr202i_door_left", -1, door_left), ("hr202i_door_right", 1, door_right)):
        yy = sy * (hw + fr / 2)
        xa = cx0 + (cd - dw) / 2 + slide
        pane = _box(xa, xa + dw, yy - g / 2, yy + g / 2, zf + 6, zf + 6 + dh - 6)
        ga, gb = sorted((yy + sy * g / 2, yy + sy * (g / 2 + 7)))
        grip = _box(xa + 4, xa + 16, ga, gb, zf + 60, zf + 200)
        out[name] = pane.union(grip)
    top = _box(cx0 + 8 + top_door, cx0 + 8 + td + top_door, -tw / 2, tw / 2, H - 5, H - 1)
    out["hr202i_top_door"] = top.union(_box(cx0 + 4 + top_door, cx0 + 16 + top_door, -30, 30, H - 1, H + 2))
    return out


HR2_DOOR_OPEN = HR2_DOOR_TRAVEL         # the side doors slide straight back, clearing the whole 148.5 mm opening
HR2_TOP_OPEN = HR2_DOOR_TRAVEL          # the top door too, over the rear housing


def hr202i_pan_top() -> float:
    """The pan's top above the bench, with the balance on its feet (the drawing's 50 mm is from the body's underside)."""
    return HR2_PAN_TOP


def beaker_riser() -> cq.Workplane:
    """Printed PETG riser on the pan (its frame: origin on the pan's top at its centre): an 80 mm foot, a 44 mm tube with
    1.6 mm walls and a cup for the 25 mL beaker at the top. About 30 g; tared with the beaker."""
    h = BEAKER_RISER_H
    foot = _cyl(BRISER_FOOT_D / 2, 3.0, 0, 0, 0)
    tube = _cyl(BRISER_TUBE_D / 2, h, 0, 0, 0).cut(_cyl(BRISER_TUBE_D / 2 - BRISER_WALL, h - 3.0, 0, 0, -0.01))
    cup = _cyl(BEAKER_D / 2 + 3.0, 8.0, 0, 0, h - 8.0).cut(_cyl(BEAKER_D / 2 + 0.4, 9.0, 0, 0, h - 5.0))
    return foot.union(tube).union(cup)


# ---------------------------------------------------------------- lift bar, shoes, guides, P16 mounts
def lift_bar() -> cq.Workplane:
    """8 mm precision steel shaft along y, centred on its frame's origin (the EC's old clevis-pin axis)."""
    return _cyl(LIFT_BAR_D / 2, LIFT_BAR_L, 0, -LIFT_BAR_L / 2, 0, axis="Y")


def bar_end() -> cq.Workplane:
    """Printed end block on each end of the lift bar (its frame: origin at the P16 rod end's hole, on the bar's axis; y
    outward, away from the machine's centre; z along the P16): a clamp on the bar's end (y -26..-12, the bar 12 mm in, an
    M3 pinch screw), two cheeks either side of the rod end's 6 mm tab with 2 mm tall slots for its 4 x 16 shoulder screw
    (v4's lost motion, so the two P16s can stop anywhere without forcing the dock), a bridge over the tab, and the guide
    shoe outboard: 14 x 10 x 20 mm, its flat sides 0.1 mm off its guide's slot, so the bar and the EC clamped to it can't
    turn while they rise. The shoulder screw goes in from outside, its head in a 6.6 mm counterbore through the shoe; its
    nylock sits between the inner cheek and the bar's end."""
    t = 3.1                                            # half the tab's gap (6.2)
    clamp = _box(-7.0, 7.0, -26.0, -12.0, -7.0, 7.0).cut(_cyl(LIFT_BAR_D / 2 + 0.02, 14.6, 0, -26.3, 0, axis="Y"))
    web = _box(-6.0, 6.0, -12.01, -t - 5.0 + 0.01, 3.5, 8.0)
    cheeks = _box(-6.0, 6.0, -t - 5.0, -t, -4.5, 8.0).union(_box(-6.0, 6.0, t, t + 5.0, -4.5, 8.0))
    bridge = _box(-6.0, 6.0, -t - 5.0, t + 5.0, 5.0, 8.0)
    shoe = _box(-SHOE[0] / 2, SHOE[0] / 2, t + 5.0 - 0.01, t + 5.0 + SHOE[1], -SHOE[2] / 2, SHOE[2] / 2)
    body = clamp.union(web).union(cheeks).union(bridge).union(shoe)
    slot = cq.Workplane("XZ").slot2D(4.1 + EC_SLOT, 4.1, 90).extrude(t + 6.0, both=True)
    cbore = _cyl(3.3, SHOE[1] + 0.2, 0, t + 5.0 - 0.1, 0, axis="Y")
    return body.cut(slot).cut(cbore)


BAR_END_SHOE_Y = (3.1 + 5.0, 3.1 + 5.0 + SHOE[1])     # the shoe's span along the block's y


def guide_block(z_floor: float, z_top: float) -> cq.Workplane:
    """Printed guide on a station post's inner face (its frame: x across the post, y from the post's inner face toward
    the machine's centre, z world height): a vertical slot 10.2 mm wide, open toward the bar and at the top, where the
    shoe leaves it as the EC docks (2 mm lead-in). Two M5 screws into T-nuts in the post."""
    w = GUIDE_SLOT_W
    blk = _box(-EXT / 2, EXT / 2, 0.0, SHOE[1] + 4.0, z_floor - 6.0, z_top)
    slot = _box(-w / 2, w / 2, 4.0 - 0.01, SHOE[1] + 4.01, z_floor, z_top + 1)
    lead = (cq.Workplane("XZ").polyline([(-w / 2, z_top - 2.0), (-w / 2 - 2.0, z_top + 0.01), (w / 2 + 2.0, z_top + 0.01), (w / 2, z_top - 2.0)])
            .close().extrude(-(SHOE[1] + 4.02)).translate((0, 4.0 - 0.01, 0)))
    return blk.cut(slot).cut(lead)


def p16_shelf(z_top: float) -> cq.Workplane:
    """Printed L-bracket on a station post's inner face (its frame as guide_block's) that the P16's base clevis (v4's,
    printed) sits on: a plate on the post (two M5 screws) and a shelf out to the clevis."""
    reach = STATION_POST_Y - EXT / 2 - P16_Y + 20.0          # post face -> 20 mm past the P16's axis
    plate = _box(-EXT / 2, EXT / 2, 0.0, 6.0, z_top - 40.0, z_top)
    shelf = _box(-EXT / 2 - 12.0, EXT / 2 + 12.0, 0.0, reach, z_top - 6.0, z_top)
    return plate.union(shelf)


# ---------------------------------------------------------------- EC v5
def ec_additions_v5() -> tuple[cq.Workplane, cq.Workplane]:
    """(added, cut) for EC v5, in its as-drawn frame: EC v4's arms, dock seats, magnets and door finger, unchanged; its base
    plate kept, but its slotted clevis replaced by two saddles that clamp the lift bar on the same axis (EC_PIN), and its
    three seat-ball pockets dropped (the cradle they parked on is gone; the shoes in their guides square the EC instead)."""
    add4, cut4 = P4.ec_additions_v4()
    px, pz = EC_PIN[0], -EC_PIN[1]
    c0, c1 = EC_CHEEK_Y
    zb0 = -(EC_BASE_Z - EC_BASE_T)
    # v4's cheeks and their slot: fill the slot back in (the saddles replace them)
    sad = None
    for sy in (-1, 1):
        ya, yb = (c0, c1 + 4.0) if sy > 0 else (-c1 - 4.0, -c0)
        s = _box(px - 7.0, px + 7.0, ya, yb, zb0 - 0.01, pz + LIFT_BAR_D / 2 + 4.0)
        sad = s if sad is None else sad.union(s)
    add = add4.union(sad)
    cut = cut4.cut(_box(px - 8.0, px + 8.0, -c1 - 5.0, c1 + 5.0, zb0 - 3.0, pz + 20.0))        # v4's clevis slot: not cut any more
    for (x, y) in EC_BALLS:                                                                   # nor the seat-ball pockets
        cut = cut.cut(_cyl(3.3, 3.0, x, y, zb0 - 2.8))
    cut = cut.union(_cyl(LIFT_BAR_D / 2 + 0.02, 2 * (c1 + 6.0), px, -(c1 + 6.0), pz, axis="Y"))
    return add, cut
