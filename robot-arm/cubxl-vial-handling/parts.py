"""Printable parts for mock-up v2 (#266), parametric in CadQuery from Cubware's and AgileX's own CAD.

    python parts.py        # -> exports/*.step, exports/*.stl (print orientation), exports/params.json

- **Dock**: two identical end blocks, one under each end of the carrier. Each has a cup around the end
  pocket's disc with a 3 mm x 45 degree lead-in and a cone pin, and sits on an offset plate.
- **Offset plates**: keyed into the PandaDeck's slots with Cubware's own key, and carrying the dock block
  on two dowels. The 0 plate is the permanent mount. The others shift the dock by 1 to 4 mm in x or y, or
  turn it 2 or 4 degrees about the carrier's centre, for the capture-envelope test.
- **8 + 1 carrier**: Cubware's 9VialHolder itself, with slot 5's pocket replaced by a grooved handle post,
  a cone-pin hole and slot under the end pockets in place of the glued keys, and 1 mm entry chamfers.
  It is 297 mm long and the A1 mini's bed is 180 mm, so it prints as two halves. The post's flange
  bolts across the joint.
- **Finger inserts**: replace AgileX's jaws on their MGN7 carriages (same four M2 screws, same F4-9M
  bearing). Each is a 90 degree V-block whose V runs vertical at the 45 degree grasp, with recesses for
  silicone pads on both flanks and a rib at the bottom of the V that drops into the post's groove.

Frames, in mm. Carrier: slot 5 (the post) on the origin, the carrier's underside at z = 0, pockets along
y with pocket 1 at +132 and pocket 9 at -132. Dock blocks and plates: their own cone pin on the origin,
y pointing out along the carrier towards its end, the plate's top (the block's underside) at z = 0.
Finger inserts: AgileX's STEP frame with the carriage where AgileX modelled it (tool axis along -y,
fingers closing along z; the upper insert is the +z one).
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import cadquery as cq

import sources as S

HERE = Path(__file__).resolve().parent
OUT = HERE / "exports"
SQ2 = math.sqrt(2.0)


@dataclass(frozen=True)
class Params:
    fit: float = 0.15            # clearance per side for printed sliding fits
    # ---- carrier
    post_slot: int = 5
    post_r: float = 8.0           # smaller than a vial on purpose: see finger inserts
    post_top: float = 64.0        # above the carrier's underside
    groove_z: float = 50.0        # geometry.POST["groove_z"], so analysis.py's IK still holds
    groove_depth: float = 2.5
    groove_h: float = 6.0         # at the post's surface; 45 degree flanks
    flange_r: float = 16.5
    flange_h: float = 8.0
    tongue: tuple = (4.0, 3.0)    # joint tongue on half A: width (x), length (y)
    bolt_y: float = 12.0          # 2 x M3 x 20 through the flange, one into each half
    m3_clear: float = 3.4
    m3_head_d: float = 6.2
    m3_head_bottom_z: float = 22.0
    m3_nut_af: float = 5.8
    m3_nut_pocket_h: float = 4.5
    pin_y: float = 125.0          # cone pins at +-125 mm: 5 deck pitches each side, 7 mm in from pockets 1 and 9
    hole_d: float = 8.1
    hole_depth: float = 9.0
    hole_chamfer: float = 1.0
    pin_slot_len: float = 12.0    # half B: the pin may slide +-1.95 mm along the carrier
    pocket_chamfer: float = 1.0
    # ---- dock block
    floor_t: float = 6.0
    cup_clear: float = 0.5
    cup_wall: float = 4.5
    cup_h: float = 12.0
    lead_in: float = 3.0          # 3 mm x 45 degrees
    cup_gap_half_deg: float = 40.0  # open towards pocket 2 so the cup clears its disc
    pin_d: float = 7.9
    pin_cyl_h: float = 4.0
    pin_tip_d: float = 3.0
    pin_half_angle_deg: float = 30.0
    block_x: float = 26.0         # half-width
    block_y: tuple = (-60.0, 30.0)
    dowel_d: float = 4.0          # 2 x 4 mm dowel pins (steel, or printed) per block
    dowels: tuple = ((-14.0, -25.0), (14.0, -25.0))
    dowel_slot: float = 6.0       # the +x dowel's hole in the block is a slot along x
    dowel_depth_block: float = 4.5
    m4_clear: float = 4.5
    m4_head_d: float = 8.2
    m4_head_depth: float = 4.0
    # ---- offset plates
    plate_t: float = 6.0
    plate_x: float = 24.0         # half-width
    plate_y: tuple = (-58.0, 8.0)
    keys_y: tuple = (0.0, -50.0)  # two deck slots, 2 pitches apart, along the carrier
    dowel_depth_plate: float = 4.0
    shifts_mm: tuple = (1.0, 2.0, 3.0, 4.0)
    yaws_deg: tuple = (2.0, 4.0)
    label_depth: float = 0.6
    # ---- finger inserts
    v_depth: float = 11.0         # 90 degree V
    behind_apex: float = 3.0
    jaw_w: float = 26.0           # across the V (along the carrier at the grasp)
    jaw_h: float = 20.0           # along the V (vertical at the grasp)
    pad_recess: float = 1.0
    pad_t: float = 1.5            # silicone sheet; stands 0.5 mm proud
    pad_s: tuple = (8.0, 14.8)    # recess along each flank, from the apex
    pad_v: float = 9.0
    rib_reach: float = 5.4        # from the apex: clears a 27 mm vial, reaches into a 16 mm post's groove
    rib_t: float = 2.0
    rib_chamfer: float = 0.5
    open_stock_mm: float = 60.0   # opening (as the SDK reports it for AgileX's own fingers) when open
    approach_clear: float = 3.0
    vial_r: float = 13.5
    cap_r: float = 14.0
    root_x: tuple = (-27.6, 2.0)
    root_front_y: float = -14.5
    beam_x: tuple = (-22.0, 6.0)
    beam_top: float = 38.8        # stays below the lower M2 heads, so a hex key reaches them from the front
    web_x: tuple = (-10.9, -4.9)
    web_top: float = 52.0
    m2_clear: float = 2.4
    m2_head_d: float = 4.2
    m2_head_depth: float = 2.0
    bearing_tap_d: float = 2.5
    bearing_tap_depth: float = 5.5


P = Params()


# ------------------------------------------------------------------ helpers
def cyl(r, z0, z1, x=0.0, y=0.0):
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1))


def cone(r0, r1, z0, z1, x=0.0, y=0.0):
    return cq.Solid.makeCone(r0, r1, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1))


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def wp(*shapes):
    w = cq.Workplane("XY")
    for s in shapes:
        w = w.add(s)
    return w.combine() if len(shapes) > 1 else w


def fuse(*shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.clean()


def cut(shape, *tools):
    for t in tools:
        shape = shape.cut(t)
    return shape.clean()


def stadium(length, width, z0, z1, x=0.0, y=0.0, along="y", taper=0.0):
    """End-to-end length along `along`."""
    w = cq.Workplane("XY").workplane(offset=z0).center(x, y)
    w = w.slot2D(length, width, angle=90 if along == "y" else 0)
    return w.extrude(z1 - z0, taper=taper).val()


def hexagon(af, z0, z1, x=0.0, y=0.0):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).polygon(6, af / math.cos(math.pi / 6)) \
        .extrude(z1 - z0).val()


def prism_xz(pts, y0, y1):
    """Polygon in the x-z plane, extruded over y0..y1."""
    w = cq.Workplane("XZ", origin=(0, 0, 0)).polyline(pts).close().extrude(-(y1 - y0))
    return w.val().translate(cq.Vector(0, y0, 0))


def prism_yz(pts, x0, x1):
    """Polygon in the y-z plane, extruded over x0..x1."""
    w = cq.Workplane("YZ").polyline(pts).close().extrude(x1 - x0)
    return w.val().translate(cq.Vector(x0, 0, 0))


def solid_volume(s):
    return sum(x.Volume() for x in s.Solids())


# ------------------------------------------------------------------ 8 + 1 carrier
def carrier_frame_holder():
    """Cubware's holder moved into the carrier frame (slot 5 on the origin, pocket 1 at +y)."""
    h = S.holder()
    y5 = h["pockets"][P.post_slot - 1][1]
    return h["solid"].translate(cq.Vector(-h["x0"], -y5, 0)), h, y5


def slot_y(i):
    h = S.holder()
    return h["pockets"][i - 1][1] - h["pockets"][P.post_slot - 1][1]


def carrier_body():
    sol, h, y5 = carrier_frame_holder()
    top, seat, rtop = h["body_top"], h["seat_z"], h["pocket_r_top"]
    # slot 5: take off its four fingers and fill its seat, leaving a flat puck at the body's top
    sol = cut(sol, cyl(h["outline_r"] + 0.2, top, h["finger_top"] + 1))
    sol = fuse(sol, cyl(h["pocket_r_seat"] + 0.5, seat - 0.5, top))
    # fill Cubware's two key sockets; cone pins replace the glued keys
    for kx, ky in h["key_sockets"]:
        sol = fuse(sol, cyl(4.6, 0.0, h["horizontal_planes"][1] + 0.2, kx - h["x0"], ky - y5))
    # 1 mm x 45 degree entry chamfer on every pocket's fingers
    c = P.pocket_chamfer
    r_at = rtop + c * math.tan(math.radians(h["pocket_taper_deg"]))
    for i in range(1, 10):
        if i != P.post_slot:
            sol = cut(sol, cone(r_at, r_at + 1.5 * c, h["finger_top"] - c, h["finger_top"] + 0.5 * c, 0, slot_y(i)))
    return sol, h


def carrier_halves():
    """Half A (pockets 1-4, the round pin hole) and half B (pockets 6-9, the pin slot), split through slot 5."""
    body, h = carrier_body()
    top = h["body_top"]
    big = 400.0
    a = body.intersect(box(-50, 50, 0, big, -1, 60))
    b = body.intersect(box(-50, 50, -big, 0, -1, 60))
    tw, tl = P.tongue
    a = fuse(a, box(-tw / 2, tw / 2, -tl, 0.0, 0.0, top))
    b = cut(b, box(-tw / 2 - P.fit, tw / 2 + P.fit, -tl - P.fit, 0.01, -1, top + 1))
    for half, sign in ((a, 1), (b, -1)):
        y = sign * P.bolt_y
        half = cut(half, cyl(P.m3_clear / 2, -1, top + 1, 0, y), hexagon(P.m3_nut_af, -1, P.m3_nut_pocket_h, 0, y))
        if sign > 0:
            a = half
        else:
            b = half
    # cone-pin hole under half A, slot under half B, each with a 1 mm x 45 degree entry chamfer
    ch = P.hole_chamfer
    ya, yb = P.pin_y, -P.pin_y
    a = cut(a, cyl(P.hole_d / 2, -1, P.hole_depth, 0, ya), cone(P.hole_d / 2 + ch + 1, P.hole_d / 2, -1, ch, 0, ya))
    b = cut(b, stadium(P.pin_slot_len, P.hole_d, -1, P.hole_depth, 0, yb),
            stadium(P.pin_slot_len + 2 * ch + 2, P.hole_d + 2 * ch + 2, -1, ch, 0, yb, taper=45))
    return a, b


def handle_post():
    """Flange over slot 5 (bolted to both halves) and a 16 mm post with a 45 degree V groove."""
    z0 = S.holder()["body_top"]
    z1 = z0 + P.flange_h
    r, zg, d, hg = P.post_r, P.groove_z, P.groove_depth, P.groove_h
    post = fuse(cyl(P.flange_r, z0, z1), cone(r + 0.6, r, z1, z1 + 0.6), cyl(r, z1 + 0.5, P.post_top - 1),
                cone(r, r - 1, P.post_top - 1, P.post_top))
    keep = fuse(cone(r, r - d, zg - hg / 2, zg - hg / 2 + d), cyl(r - d, zg - hg / 2 + d - 0.01, zg + hg / 2 - d + 0.01),
                cone(r - d, r, zg + hg / 2 - d, zg + hg / 2))
    groove = cut(cyl(r + 1, zg - hg / 2, zg + hg / 2), keep)
    post = cut(post, groove)
    for y in (P.bolt_y, -P.bolt_y):
        post = cut(post, cyl(P.m3_clear / 2, z0 - 1, z1 + 1, 0, y), cyl(P.m3_head_d / 2, P.m3_head_bottom_z, z1 + 1, 0, y))
    return post


# ------------------------------------------------------------------ dock block
def pocket_centre_local():
    """End pocket's centre in a dock block's frame (pin on the origin, y out towards the carrier's end)."""
    return slot_y(1) - P.pin_y


def dock_block():
    h = S.holder()
    pc = pocket_centre_local()
    ft = P.floor_t
    r_in = h["outline_r"] + P.cup_clear
    r_out = r_in + P.cup_wall
    blk = box(-P.block_x, P.block_x, P.block_y[0], P.block_y[1], 0, ft)
    cupw = cut(cyl(r_out, ft - 0.5, ft + P.cup_h, 0, pc), cyl(r_in, ft - 1, ft + P.cup_h + 1, 0, pc))
    a = math.radians(P.cup_gap_half_deg)
    L = 60.0
    wedge = cq.Workplane("XY").workplane(offset=ft - 0.4).polyline(
        [(0, pc), (-L * math.sin(a), pc - L * math.cos(a)), (L * math.sin(a), pc - L * math.cos(a))]).close() \
        .extrude(P.cup_h + 2).val()
    cupw = cut(cupw, wedge)
    zt = ft + P.cup_h
    cupw = cut(cupw, cone(r_in, r_in + P.lead_in + 0.01, zt - P.lead_in, zt + 0.01, 0, pc))
    rp, rt = P.pin_d / 2, P.pin_tip_d / 2
    tip_h = (rp - rt) / math.tan(math.radians(P.pin_half_angle_deg))
    pin = fuse(cyl(rp, ft - 0.5, ft + P.pin_cyl_h), cone(rp, rt, ft + P.pin_cyl_h, ft + P.pin_cyl_h + tip_h))
    blk = fuse(blk, cupw, pin)
    (x0, y0), (x1, y1) = P.dowels
    dh = P.dowel_d / 2 + 0.05
    blk = cut(blk, cyl(dh, -1, P.dowel_depth_block, x0, y0),
              stadium(P.dowel_slot, 2 * dh, -1, P.dowel_depth_block, x1, y1, along="x"),
              cyl(P.m4_clear / 2, -1, ft + 1, 0, P.dowels[0][1]),
              cyl(P.m4_head_d / 2, ft - P.m4_head_depth, ft + 1, 0, P.dowels[0][1]))
    return blk, dict(pocket_centre_y=pc, cup_r=[r_in, r_out], cup_top_z=zt, lead_in_r_top=r_in + P.lead_in,
                     pin_top_z=ft + P.pin_cyl_h + tip_h, pin_tip_h=tip_h)


# ------------------------------------------------------------------ offset plates
CARRIER_CENTRE_LOCAL = (0.0, -P.pin_y)  # in a block's own frame


def offset_xform(kind, value):
    """(dx, dy, dtheta_deg) of a dock block on its plate, in the block's frame."""
    if kind == "0":
        return 0.0, 0.0, 0.0
    if kind == "x":
        return value, 0.0, 0.0
    if kind == "y":
        return 0.0, value, 0.0
    return None, None, value


def plate_dowels(kind, value):
    """Dowel hole centres on a plate, and where the block's pin ends up."""
    if kind == "r":
        t = math.radians(value)
        cx, cy = CARRIER_CENTRE_LOCAL
        def rot(p):
            x, y = p[0] - cx, p[1] - cy
            return (cx + x * math.cos(t) - y * math.sin(t), cy + x * math.sin(t) + y * math.cos(t))
        return [rot(p) for p in P.dowels], rot((0.0, 0.0))
    dx, dy, _ = offset_xform(kind, value)
    return [(x + dx, y + dy) for x, y in P.dowels], (dx, dy)


PLATES = [("0", 0.0)] + [(k, v) for k in ("x", "y") for v in P.shifts_mm] + \
         [("r", s * v) for v in P.yaws_deg for s in (1, -1)]


def plate_name(kind, value):
    if kind == "0":
        return "plate_0"
    if kind == "r":
        return f"plate_yaw{'+' if value > 0 else '-'}{abs(value):g}deg"
    return f"plate_{kind}+{value:g}mm"


def plate_label(kind, value):
    if kind == "0":
        return "0"
    if kind == "r":
        return f"R{'+' if value > 0 else '-'}{abs(value):g}"
    return f"{kind.upper()}+{value:g}"


def offset_plate(kind, value):
    k = S.key()
    d = S.deck()
    t = P.plate_t
    pl = box(-P.plate_x, P.plate_x, P.plate_y[0], P.plate_y[1], -t, 0)
    # Cubware's key, turned so its long axis runs across the carrier (the deck's slots run across it too)
    for ky in P.keys_y:
        key = k["solid"].rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 90).translate(cq.Vector(0, ky, -t))
        pl = fuse(pl, key)
    holes, pin = plate_dowels(kind, value)
    dh = P.dowel_d / 2 + 0.05
    pl = cut(pl, *[cyl(dh, -P.dowel_depth_plate, 1, x, y) for x, y in holes])
    pl = cut(pl, cyl(P.m4_clear / 2, -t - 1, 1, 0, P.dowels[0][1]))
    # label and an arrow pointing out along the carrier, engraved in the top face
    txt = cq.Workplane("XY").workplane(offset=-P.label_depth).center(0, -44).text(
        plate_label(kind, value), 9, P.label_depth + 1, kind="bold", halign="center", valign="center").val()
    arrow = cq.Workplane("XY").workplane(offset=-P.label_depth).polyline(
        [(-4, -6), (4, -6), (0, 1)]).close().extrude(P.label_depth + 1).val()
    pl = cut(pl, txt, arrow)
    return pl, dict(dowels=[[round(x, 3), round(y, 3)] for x, y in holes],
                    pin_moves_to=[round(pin[0], 3), round(pin[1], 3)],
                    key_slot_pitch=d["pitch_x"], keys_y=list(P.keys_y))


# ------------------------------------------------------------------ finger inserts
def grip_states():
    """Carriage travel from where AgileX modelled it, and the opening the SDK would report for AgileX's
    own fingers there, for each grasp. V apex distance from the tool axis: (r + pad)*sqrt(2)."""
    g = S.gripper()
    zt = g["tool_axis_xz"][1]
    pad = P.pad_t - P.pad_recess
    n_open = P.vial_r + P.approach_clear + P.v_depth
    d_open = (P.open_stock_mm - g["stock_opening"]) / 2
    z_apex = n_open + zt - d_open
    out = {}
    for name, n in (("open", n_open), ("vial", (P.vial_r + pad) * SQ2), ("post", (P.post_r + pad) * SQ2),
                    ("vial, no pads", P.vial_r * SQ2), ("post, no pads", P.post_r * SQ2)):
        d = n + zt - z_apex
        out[name] = dict(apex_from_axis=round(n, 3), carriage_travel=round(d, 3),
                         stock_opening=round(g["stock_opening"] + 2 * d, 2))
    return z_apex, out


def rib_numbers():
    pad = P.pad_t - P.pad_recess
    r, rg = P.post_r, P.post_r - P.groove_depth
    out = {}
    for label, p in (("with pads", pad), ("no pads", 0.0)):
        vial_gap = (P.vial_r + p) * SQ2 - P.vial_r
        post_gap = (r + p) * SQ2 - r
        out[label] = dict(vial_clearance=round(vial_gap - P.rib_reach, 3),
                          rib_into_groove=round(P.rib_reach - post_gap, 3),
                          rib_to_groove_floor=round((r + p) * SQ2 - rg - P.rib_reach, 3))
    return out


def jaw_block(z_apex):
    """V-block in its own frame: x across the V, y along it, z = the STEP's z. Apex at z_apex."""
    hw, hh = P.jaw_w / 2, P.jaw_h / 2
    zf, zb = z_apex - P.v_depth, z_apex + P.behind_apex
    blk = box(-hw, hw, -hh, hh, zf, zb)
    big = 40.0
    vcut = prism_xz([(0, z_apex), (-big, z_apex - big), (big, z_apex - big)], -hh - 1, hh + 1)
    blk = cut(blk, vcut)
    r = P.rib_reach
    tri = prism_xz([(-(r + 1), z_apex - r), (r + 1, z_apex - r), (0, z_apex + 1)], -P.rib_t, P.rib_t)
    zr = z_apex - r
    c, t2 = P.rib_chamfer, P.rib_t / 2
    prof = prism_yz([(-t2 + c, zr), (t2 - c, zr), (t2, zr + c), (t2, z_apex + 2), (-t2, z_apex + 2), (-t2, zr + c)],
                    -(r + 2), r + 2)
    blk = fuse(blk, tri.intersect(prof))
    s0, s1 = P.pad_s
    rec = box(s0, s1, -P.pad_v, P.pad_v, -1.0, P.pad_recess).rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 45) \
        .translate(cq.Vector(0, 0, z_apex))
    blk = cut(blk, rec, rec.mirror("YZ"))
    return blk


def finger_insert(v_dir=1):
    """v_dir +1 for the upper (+z) carriage, -1 for the lower; the lower one is then mounted turned 180
    degrees about the tool axis, so both V-grooves run the same way."""
    g = S.gripper()
    xt, zt = g["tool_axis_xz"]
    ytcp = g["tcp"][1]
    car = g["carriage"]
    back = max(g["jaw_back_y"])
    top = g["jaw_bbox"][5]
    z_apex, _ = grip_states()
    zb = z_apex + P.behind_apex
    jb = jaw_block(z_apex).rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -45 * v_dir).translate(cq.Vector(xt, ytcp, 0))
    root = box(P.root_x[0], P.root_x[1], P.root_front_y, back, zb - 0.5, top)
    beam = box(P.beam_x[0], P.beam_x[1], ytcp - 2, P.root_front_y + 0.5, zb - 0.5, P.beam_top)
    web = box(P.web_x[0], P.web_x[1], ytcp + 8, P.root_front_y + 0.5, P.beam_top - 0.5, P.web_top)
    ins = fuse(root, beam, web, jb)
    cx0, cy0, cz0, cx1, cy1, cz1 = car["bbox"]
    ins = cut(ins, box(cx0 - 0.2, cx1 + 0.2, car["front_y"], back + 1, cz0 - 0.2, cz1 + 0.2))
    for x, z in car["m2_holes_xz"]:
        ins = cut(ins, cq.Solid.makeCylinder(P.m2_clear / 2, 20, cq.Vector(x, P.root_front_y - 5, z), cq.Vector(0, 1, 0)),
                  cq.Solid.makeCylinder(P.m2_head_d / 2, P.m2_head_depth + 5, cq.Vector(x, P.root_front_y - 5, z),
                                        cq.Vector(0, 1, 0)))
    bx, bz = g["bearing"]["centre_xz"]
    ins = cut(ins, cq.Solid.makeCylinder(P.bearing_tap_d / 2, P.bearing_tap_depth + 1,
                                         cq.Vector(bx, back + 1, bz), cq.Vector(0, -1, 0)))
    return ins


# ------------------------------------------------------------------ print orientation and export
def for_print(name, shape):
    """Each part as it goes on the bed: standing on z = 0, footprint centred on x = y = 0."""
    if name.startswith("finger_insert"):
        shape = shape.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), -90)   # back face down
    if name.startswith("plate"):
        shape = shape.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180)   # top face down, keys up
    bb = shape.BoundingBox()
    return shape.translate(cq.Vector(-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


def build():
    parts, info = {}, {}
    a, b = carrier_halves()
    parts["carrier_half_a"], parts["carrier_half_b"], parts["handle_post"] = a, b, handle_post()
    parts["dock_block"], info["dock_block"] = dock_block()
    parts["finger_insert_upper"] = finger_insert(+1)
    parts["finger_insert_lower"] = finger_insert(-1)
    info["plates"] = {}
    for kind, value in PLATES:
        n = plate_name(kind, value)
        parts[n], info["plates"][n] = offset_plate(kind, value)
    return parts, info


def export(parts, info):
    OUT.mkdir(exist_ok=True)
    pla = 1.24e-3  # g/mm^3, solid
    vols = {}
    for name, shape in parts.items():
        assert shape.isValid(), name
        n = len(shape.Solids())
        assert n == 1, f"{name}: {n} solids"
        cq.exporters.export(cq.Workplane().add(shape), str(OUT / f"{name}.step"))
        cq.exporters.export(cq.Workplane().add(for_print(name, shape)), str(OUT / f"{name}.stl"),
                            tolerance=0.05, angularTolerance=0.2)
        bb = shape.BoundingBox()
        vols[name] = dict(volume_mm3=round(shape.Volume(), 1), solid_pla_g=round(shape.Volume() * pla, 1),
                          bbox_mm=[round(v, 2) for v in (bb.xlen, bb.ylen, bb.zlen)])
    z_apex, states = grip_states()
    params = dict(params=asdict(P), measured=S.summary(), parts=vols, dock_block=info["dock_block"],
                  plates=info["plates"], finger=dict(apex_z_in_step_frame=round(z_apex, 3), states=states,
                                                     rib=rib_numbers()))
    (OUT / "params.json").write_text(json.dumps(params, indent=1) + "\n")
    return params


if __name__ == "__main__":
    parts, info = build()
    p = export(parts, info)
    for k, v in p["parts"].items():
        print(f"{k:28s} {v['volume_mm3']:10.0f} mm3  {v['solid_pla_g']:6.1f} g solid  bbox {v['bbox_mm']}")
    print(json.dumps(p["finger"], indent=1))
