"""CubXL electromagnetic-capper parts, v2 (issue #354).

Builds three printable parts with CadQuery and writes STEP + STL:

  rack   9-position 20 mL vial rack. Drop-in replacement for PANDA-BEAR's
         9VialHolder20mL_TightFit: same 33.4 x 297.38 mm stadium outline, same
         33.0 mm pitch, same 18.0 mm seat height, same 35.0 mm height, same key
         positions (under vial 1 and 225 mm away). Each cup grips the vial with
         two long curved spring arms that bend in the horizontal plane, so the
         bending stress runs along the printed lines instead of across layers,
         and pushes it against a rigid rib, so the vial's position is set by
         the rib, not by the springs.
  key    clip-in deck key for the 10 x 25 mm pill slots. A rigid pill locates
         it in the slot (0.10 mm a side, as before); two horizontal latch arms
         below it carry barbs whose 30-degree ramps catch under the deck for
         any plate thickness from 9.0 to 10.45 mm, with no vertical play.
         Press up on the key's bottom to unclip. The top is a crush-rib stem
         that presses into the rack.
  bar    gantry bar for the existing electromagnet housing (Cubware
         VialDecapperMount): two hook prongs for the backboard's 3 x 10 mm
         slots (20 mm apart), a dovetail channel for the housing's tongue with
         a bottom stop, and a 3.2 mm cross hole to pin the housing in place.

Run:  python build.py [outdir]     (needs cadquery)
All dimensions in mm.  Rack frame: z=0 is the rack bottom (deck top), vial 1 at
(0,0), vials along -y.  Key frame: z=0 is the deck top.  Bar frame: y=0 is the
backboard's front face, z=0 the bar's top.
"""
import json, math, os, sys
import cadquery as cq

P = dict(
    # ---- rack (matches 9VialHolder20mL_TightFit) ----
    n_vials=9, pitch=33.0, width=33.4, length=297.38, height=35.0, seat_z=18.0,
    key_y=(0.0, -225.0),
    # ---- cup ----
    r_floor=14.2,          # vial floor (pedestal) radius
    r_bore=14.6,           # rigid bore radius (posts), clears vials up to 29.2
    r_rib=13.9,            # rigid locating rib on the +y post: vial is pushed onto it
    rib_half_deg=9.0,      # rib angular half-width
    r_arm_in=14.8,         # spring arm inner radius
    t_arm=1.7,             # spring arm radial thickness
    arm_root_deg=62.0,     # right arm root angle (left arm is mirrored: 180-62)
    arm_tip_deg=-50.0,     # right arm free-tip angle
    gap=0.6,               # slot width around the arms
    out_gap=2.4,           # radial room behind each arm for outward travel
    z_root=0.0,            # arm root attached to the post from z_root up to the top
    r_pad=12.4,            # pad radius at rest (contact circle 24.8 mm)
    pad_deg=(-46.0, -26.0),# right pad angular span (left mirrored)
    pad_z=(22.5, 34.6),    # pad z span incl. 45-degree chamfers both ends
    # ---- key pocket in rack (crush-rib press fit) ----
    stem_x=6.0, stem_y=12.0, stem_h=5.0, stem_r=1.0, pocket_clear=0.05, pocket_extra_depth=0.6,
    # ---- key ----
    pill_w=9.8, pill_l=24.8, deck_min=9.0, deck_max=10.45,
    rigid_bottom=-6.0,      # rigid locating pill from z=0 down to here (full stadium)
    spine_half=1.3,         # spine half-width (x) below the rigid pill
    arm_t=1.3,              # latch arm thickness (x)
    arm_top=-8.9,           # latch arm top (z); clears the chamfer for arm_travel of inward travel
    arm_travel=1.2,
    arm_y=(-7.5, 6.8),      # latch arm span in y: root plane at -7.5, free end at +6.8 (0.7 gap to the rigid end)
    arm_root_fillet=1.0,
    key_bottom=-15.0,
    barb_u=0.85,            # barb protrusion beyond the pill flat (x = 4.9 -> 5.75)
    barb_y=(3.0, 6.8),      # barb only at the free end of the arm
    barb_top=-8.85,         # retention ramp starts here (protrusion 0) ...
    ramp_deg=30.0,          # ... at 30 deg from vertical, both ramps
    rib_h=0.35, rib_w=0.6,  # crush ribs on the stem
    # ---- bar ----
    bar_w=13.0, bar_t=10.0, bar_len=135.0,
    prong_t=2.7, prong_h=5.6, prong_len=6.4, hook_drop=3.2, hook_t=3.0, prong_pitch=20.0, prong_top=8.0,
    board_t=6.04, slot_w=3.0, slot_h=10.0,
    dt_narrow=8.17, dt_wide=12.98, dt_depth=5.3, dt_h=14.5, dt_clear=0.12, dt_neck_w=20.0,
    foot_w=22.0, foot_h=22.0, entry_h=18.0, stop_t=2.5, pin_d=3.2,
)

def sector(r0, r1, a0, a1, z0, z1):
    """Annular sector solid between radii r0<r1, angles a0<a1 (deg), heights z0<z1."""
    a0r, a1r = math.radians(a0), math.radians(a1)
    am = (a0r + a1r) / 2
    pts_out = [(r1 * math.cos(a0r), r1 * math.sin(a0r)), (r1 * math.cos(am), r1 * math.sin(am)), (r1 * math.cos(a1r), r1 * math.sin(a1r))]
    pts_in = [(r0 * math.cos(a1r), r0 * math.sin(a1r)), (r0 * math.cos(am), r0 * math.sin(am)), (r0 * math.cos(a0r), r0 * math.sin(a0r))]
    w = (cq.Workplane("XY").workplane(offset=z0)
         .moveTo(*pts_out[0]).threePointArc(pts_out[1], pts_out[2])
         .lineTo(*pts_in[0]).threePointArc(pts_in[1], pts_in[2]).close()
         .extrude(z1 - z0))
    return w

def revolved_profile(rz_pts, a0, a1):
    """Revolve an (r,z) polygon about Z from angle a0 to a1 (deg)."""
    prof = cq.Workplane("XZ").polyline(rz_pts).close()
    solid = prof.revolve(a1 - a0, (0, 0, 0), (0, 1, 0))
    # Workplane("XZ") local x->X, local y->Z; revolve() above sweeps from +X toward -Y,
    # so mirror the sweep direction by rotating with the opposite sign.
    return solid.rotate((0, 0, 0), (0, 0, 1), a0)

def cup_cuts_and_adds(p):
    """Returns (cut, add) solids for one cup centred at the origin."""
    cut = cq.Workplane("XY").circle(p["r_bore"]).extrude(p["height"] + 1).translate((0, 0, p["seat_z"]))
    adds = []
    ri, t = p["r_arm_in"], p["t_arm"]
    for side in (+1, -1):   # +1: right arm (x>0), -1: left arm (mirror about the y axis)
        def ang(a):  # mirror an angle of the right side to the left side
            return a if side > 0 else 180.0 - a
        root, tip = p["arm_root_deg"], p["arm_tip_deg"]
        lo, hi = sorted((ang(tip), ang(root)))
        g = math.degrees(p["gap"] / ri)
        # inner slot frees the arm from pedestal/bore; outer slot gives room to move
        tip_side = ang(tip)
        if side > 0:
            a_lo, a_hi = tip - 2 * g, root
        else:
            a_lo, a_hi = 180 - root, 180 - tip + 2 * g
        cut = cut.union(sector(p["r_floor"], ri, a_lo, a_hi, -1, p["height"] + 1))
        cut = cut.union(sector(ri + t, ri + t + 12.0, a_lo, a_hi, -1, p["height"] + 1))
        # tip slot: gap between the free tip and the -y post
        if side > 0:
            cut = cut.union(sector(p["r_floor"], ri + t + 12.0, tip - 2 * g, tip, -1, p["height"] + 1))
        else:
            cut = cut.union(sector(p["r_floor"], ri + t + 12.0, 180 - tip, 180 - tip + 2 * g, -1, p["height"] + 1))
        # root slot below z_root
        if p["z_root"] > 0:
            if side > 0:
                cut = cut.union(sector(p["r_floor"], ri + t + p["out_gap"], root, root + 2 * g, -1, p["z_root"]))
            else:
                cut = cut.union(sector(p["r_floor"], ri + t + p["out_gap"], 180 - root - 2 * g, 180 - root, -1, p["z_root"]))
        # pad: (r,z) profile with 45-degree chamfers, revolved over the pad span
        z0, z1 = p["pad_z"]; d = ri + 0.05 - p["r_pad"]
        prof = [(ri + 0.05, z0), (p["r_pad"], z0 + d), (p["r_pad"], z1 - d), (ri + 0.05, z1)]
        a0, a1 = p["pad_deg"]
        if side < 0:
            a0, a1 = 180 - a1, 180 - a0
        adds.append(revolved_profile(prof, a0, a1))
    # rigid locating rib on the +y post, above the seat
    adds.append(sector(p["r_rib"], p["r_bore"] + 0.05, 90 - p["rib_half_deg"], 90 + p["rib_half_deg"], p["seat_z"], p["height"] - 0.6)
                .edges("|Z").fillet(0.3))
    return cut, adds

def stem_profile(p, grow=0.0):
    return (cq.Workplane("XY").rect(p["stem_x"] + 2 * grow, p["stem_y"] + 2 * grow)
            .extrude(1).edges("|Z").fillet(p["stem_r"]).faces("<Z").wires().toPending())

def build_rack(p=P):
    L, W, H = p["length"], p["width"], p["height"]
    r = W / 2
    yc = [-i * p["pitch"] for i in range(p["n_vials"])]
    y_mid = (yc[0] + yc[-1]) / 2
    body = (cq.Workplane("XY").center(0, y_mid).slot2D(L, W, angle=90).extrude(H))
    cut_one, adds_one = cup_cuts_and_adds(p)
    for y in yc:
        body = body.cut(cut_one.translate((0, y, 0)))
    for y in yc:
        for a in adds_one:
            body = body.union(a.translate((0, y, 0)))
    # key pockets (stem + clearance), from the bottom
    c = p["pocket_clear"]
    for ky in p["key_y"]:
        pocket = (cq.Workplane("XY").rect(p["stem_x"] + 2 * c, p["stem_y"] + 2 * c).extrude(p["stem_h"] + p["pocket_extra_depth"])
                  .edges("|Z").fillet(p["stem_r"] + c).translate((0, ky, -0.01)))
        body = body.cut(pocket)
        # 0.4 mm entry chamfer
        body = body.cut(cq.Workplane("XY").rect(p["stem_x"] + 2 * c + 0.8, p["stem_y"] + 2 * c + 0.8)
                        .workplane(offset=0.4).rect(p["stem_x"] + 2 * c, p["stem_y"] + 2 * c).loft()
                        .translate((0, ky, -0.001)))
    # small bottom chamfer against elephant foot
    try:
        body = body.faces("<Z").edges().chamfer(0.4)
    except Exception:
        pass
    return body

def build_key(p=P):
    w, l = p["pill_w"], p["pill_l"]
    hx = w / 2
    # rigid locating pill z in [rigid_bottom, 0]
    rigid = cq.Workplane("XY").slot2D(l, w, angle=90).extrude(-p["rigid_bottom"]).translate((0, 0, p["rigid_bottom"]))
    # 45-degree chamfered transition from the pill flats to the spine (no overhang)
    zt = p["rigid_bottom"]; drop = hx - p["spine_half"]
    trans = (cq.Workplane("XY").workplane(offset=zt - drop).rect(2 * p["spine_half"], l - w + 2 * 0.0)
             .workplane(offset=drop).rect(w, l - w).loft())
    # keep the rounded ends full-depth so the pill keeps locating in y
    lower_top = zt - drop          # bottom of the transition
    zb = p["key_bottom"]
    ends = cq.Workplane("XY").slot2D(l, w, angle=90).extrude(zt - zb).translate((0, 0, zb))
    ends = ends.cut(cq.Workplane("XY").rect(w + 1, l - w).extrude(zt - zb + 1).translate((0, 0, zb - 0.5)))
    # spine down to the bottom
    spine = cq.Workplane("XY").rect(2 * p["spine_half"], l - w).extrude(lower_top - zb).translate((0, 0, zb))
    # root block at -y end (the U-bend), full stadium end, from bottom to the transition
    root = (cq.Workplane("XY").slot2D(l, w, angle=90).extrude(lower_top - zb).translate((0, 0, zb))
            .intersect(cq.Workplane("XY").center(0, -l / 2 - 5).rect(w + 2, 2 * (l / 2 + 5 + p["arm_y"][0])).extrude(50).translate((0, 0, -40))))
    # latch arms: x in [hx-t, hx] (and mirror), y in arm_y, z from bottom to arm_top (under the 45 chamfer)
    # The arms' tops must stay clear of the 45-degree chamfer above them while the arms
    # deflect inward by up to ~1.1 mm at the free end (FEA). v2 as first printed on
    # 2026-11-19 had them only 0.45 mm (horizontal) below the chamfer, so they would have
    # jammed against it before the barbs could clear a 10.0 mm slot.
    arm_top = p["arm_top"]
    x_in = hx - p["arm_t"] - p["arm_travel"]               # arm's inner face at full travel
    z_ch = p["rigid_bottom"] - (hx - x_in)                   # chamfer height there
    assert arm_top <= z_ch - 0.3, (arm_top, z_ch)
    arms = cq.Workplane("XY")
    y0, y1 = p["arm_y"]
    for s in (1, -1):
        a = (cq.Workplane("XY").center(s * (hx - p["arm_t"] / 2), (y0 + y1) / 2).rect(p["arm_t"], y1 - y0)
             .extrude(arm_top - zb).translate((0, 0, zb)))
        arms = arms.union(a) if arms.vals() else a
    key = rigid.union(trans).union(ends).union(spine).union(root).union(arms)
    # R1 fillet (plan view) where each arm's inner face meets the root block
    rf = p["arm_root_fillet"]
    for s in (1, -1):
        xi = s * (hx - p["arm_t"])          # arm inner face
        blk = cq.Workplane("XY").center(xi - s * rf / 2, y0 + rf / 2).rect(rf, rf).extrude(arm_top - zb).translate((0, 0, zb))
        cyl = cq.Workplane("XY").center(xi - s * rf, y0 + rf).circle(rf).extrude(arm_top - zb + 2).translate((0, 0, zb - 1))
        key = key.union(blk.cut(cyl))
    # barbs: x-z profile extruded over barb_y; retention ramp from barb_top down, lead-in below
    u = p["barb_u"]; tn = math.tan(math.radians(p["ramp_deg"]))
    zt_b = p["barb_top"]; z_tip = zt_b - u / tn; z_bot = z_tip - u / tn
    by0, by1 = p["barb_y"]
    for s in (1, -1):
        prof = [(s * (hx - 0.3), min(zt_b + 0.3, arm_top)), (s * hx, min(zt_b, arm_top)), (s * (hx + u), z_tip), (s * (hx + u), z_tip - 0.25), (s * hx, z_bot - 0.25), (s * (hx - 0.3), z_bot - 0.25)]
        barb = cq.Workplane("XZ").polyline(prof).close().extrude(-(by1 - by0)).translate((0, by0, 0))
        key = key.union(barb)
    # top stem with crush ribs
    stem = (cq.Workplane("XY").rect(p["stem_x"], p["stem_y"]).extrude(p["stem_h"]).edges("|Z").fillet(p["stem_r"])
            .faces(">Z").edges().chamfer(0.5))
    rh, rw = p["rib_h"], p["rib_w"]
    ribs = []
    for (x, y, nx, ny) in [(p["stem_x"] / 2, -3.0, 1, 0), (p["stem_x"] / 2, 3.0, 1, 0), (-p["stem_x"] / 2, -3.0, -1, 0), (-p["stem_x"] / 2, 3.0, -1, 0),
                           (0, p["stem_y"] / 2, 0, 1), (0, -p["stem_y"] / 2, 0, -1)]:
        # triangular rib along z, base 1.2 mm on the face, apex rh out, 0.6 mm wide flat tip
        if nx:
            tri = [(x - nx * 0.05, y - 0.6), (x + nx * rh, y - rw / 2), (x + nx * rh, y + rw / 2), (x - nx * 0.05, y + 0.6)]
        else:
            tri = [(x - 0.6, y - ny * 0.05), (x - rw / 2, y + ny * rh), (x + rw / 2, y + ny * rh), (x + 0.6, y - ny * 0.05)]
        rib = cq.Workplane("XY").polyline(tri).close().extrude(p["stem_h"] - 1.0)
        ribs.append(rib)
    for rb in ribs:
        stem = stem.union(rb)
    key = key.union(stem)
    # bottom edge chamfer for printing (elephant foot) on the bottom face outline
    return key

def build_bar(p=P):
    """Bar: x in [0, W] (prongs flush with x=0), y in [0, T] (y=0 against the backboard),
    z in [-Lb, 0].  The housing's dovetail tongue drops into a channel in the foot from
    above and rests on a solid stop; a 3.2 mm cross hole above the tongue takes an M3
    screw, a 3 mm pin or a zip tie so capping can't push the housing up."""
    W, T, Lb = p["bar_w"], p["bar_t"], p["bar_len"]
    fw, fh, entry = p["foot_w"], p["foot_h"], p["entry_h"]
    xc = fw / 2                      # channel (and housing) centre line
    bar = cq.Workplane("XY").box(W, T, Lb, centered=False).translate((0, 0, -Lb)).edges("|Y").fillet(1.5)
    foot = cq.Workplane("XY").box(fw, T, fh + entry, centered=False).translate((0, 0, -Lb)).edges("|Y").fillet(1.5)
    bar = bar.union(foot)
    # 45-degree shoulder from the foot back to the bar width (self-supporting on its side)
    sh = fw - W
    tri = (cq.Workplane("XZ").polyline([(W - 0.01, -Lb + fh + entry - 0.01), (fw, -Lb + fh + entry - 0.01), (W - 0.01, -Lb + fh + entry + sh)])
           .close().extrude(-T))
    bar = bar.union(tri)
    c = p["dt_clear"]; dn, dw, dd = p["dt_narrow"] + 2 * c, p["dt_wide"] + 2 * c, p["dt_depth"] + c
    z_stop = -Lb + p["stop_t"]
    prof = [(xc - dn / 2, T + 0.01), (xc + dn / 2, T + 0.01), (xc + dw / 2, T - dd), (xc - dw / 2, T - dd)]
    chan = cq.Workplane("XY").polyline(prof).close().extrude(fh + entry + 1).translate((0, 0, z_stop))
    bar = bar.cut(chan)
    # entry zone: above the channel the foot is only the back plate, so the tongue can be lowered in
    ez = cq.Workplane("XY").box(fw + 2, dd + 0.6, entry + sh + 1, centered=False).translate((-1, T - dd, -Lb + fh))
    bar = bar.cut(ez)
    zpin = z_stop + p["dt_h"] + 0.3 + p["pin_d"] / 2
    pin = cq.Workplane("YZ").circle(p["pin_d"] / 2).extrude(fw + 2).translate((xc - fw / 2 - 1, T - dd / 2, zpin))
    bar = bar.cut(pin)
    pt, ph, pl, hd, ht = p["prong_t"], p["prong_h"], p["prong_len"], p["hook_drop"], p["hook_t"]
    for i in range(2):
        ztop = -p["prong_top"] - i * p["prong_pitch"]
        stem = cq.Workplane("XY").box(pt, pl + 0.5, ph, centered=False).translate((0, -pl, ztop - ph))
        hook = cq.Workplane("XY").box(pt, ht, ph + hd, centered=False).translate((0, -pl - ht, ztop - ph - hd))
        pr = stem.union(hook)
        pr = pr.edges("|X").fillet(0.5)
        bar = bar.union(pr)
        # root fillet: a 1.5 mm 45-degree gusset above and below the stem where it meets the bar
        for zz, sg in ((ztop, 1), (ztop - ph, -1)):
            g = cq.Workplane("YZ").polyline([(0.0, zz), (-1.5, zz), (0.0, zz + sg * 1.5)]).close().extrude(pt)
            bar = bar.union(g)
    return bar

def export(obj, name, outdir):
    os.makedirs(os.path.join(outdir, "step"), exist_ok=True); os.makedirs(os.path.join(outdir, "stl"), exist_ok=True)
    cq.exporters.export(obj, os.path.join(outdir, "step", name + ".step"))
    cq.exporters.export(obj, os.path.join(outdir, "stl", name + ".stl"), tolerance=0.01, angularTolerance=0.1)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    which = sys.argv[2].split(",") if len(sys.argv) > 2 else ["rack", "key", "bar"]
    builders = {"rack": build_rack, "key": build_key, "bar": build_bar}
    for nm in which:
        o = builders[nm]()
        bb = o.val().BoundingBox()
        print(nm, "valid", o.val().isValid(), "solids", len(o.solids().vals()), "bbox", [round(v, 2) for v in (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)], "vol", round(o.val().Volume(), 1))
        export(o, {"rack": "vial_rack_9x20mL_v2", "key": "deck_clip_key_v2_1", "bar": "magnet_bar_v2"}[nm], out)
    json.dump(P, open(os.path.join(out, "cad", "params.json"), "w"), indent=1)
