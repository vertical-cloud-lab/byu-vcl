"""Round 9 (PR #318, Sterling 2026-11-05 22:56): the CubXL's magnet holds one cap at a time, so where does the other cap
go?  ``instruments_lab.cubxl_corrosion`` copied here (instruments_lab.py is the jars stream's) and registered under the
same REGISTRY key, so ``tour.load`` and ``cubxl_rig.CubRig`` pick it up everywhere.

The answer drawn: a **cap-parking vial**, an empty 20 mL vial of Ben's 9-position holder (seat 6, y 233: DAL's plan leaves
seats 6 and 7 empty) kept only to hold a vial cap.  The capper sets the cap on it exactly as it sets one on a stock vial
(CubOS ``decap a`` / ``cap b`` is already the primitive; DAL's park cup is the same idea for the electrode cap), so it adds
no hardware and no deck area, and it sits on the capper's own x-line, 33 mm from the stocks.  Where it matters in the
clip: the ASW stock stays open (its cap parked) while the sulfide stock is opened (its cap on the magnet) for the
15 uL sulfide draw, then the caps go back in turn.  See notes/cubxl_corrosion.md.
"""
from __future__ import annotations

import math

import instruments_lab as IL

# every helper, constant and material of instruments_lab, so the copied functions below run unchanged
globals().update({k: v for k, v in vars(IL).items()
                  if not k.startswith("__") and k not in ("REGISTRY", "CAMS", "PLOTS", "LABELS", "MATERIALS")})
MATERIALS = {}
CAMS, PLOTS = IL.CAMS, IL.PLOTS

PARK_SEAT = 6                       # holder seat of the cap-parking vial (y 233)

# ---- round 14 (PR #372, notes/cubxl_pipettes.md): an OT-2 GEN2 P300 single beside the P20, as that note recommends.
# It sits 34 mm in front of the P20 (the spacing of an OT-2's two mounts): beside it in x, the capper would sit over the
# cup block whenever the P300 worked at S1. Its nozzle is 16 mm above the P20's, so a seated 300 uL tip (59.3 mm long,
# 8.3 mm on the nozzle) ends 35 mm below the carriage's reference, as a P20 tip does: on the CubXL's one Z axis the
# two tips' ends share a height, and only one tip is on the head at a time. Its tips: a printed 2 x 4 rack at the
# deck's front left, the one place found clear of the capper, the camera and the bare P20 whenever either pipette works
# (the capper's footprint over the tube rack, rack 2 and the holder ruled out the middle of the deck).
P3 = dict(off=(55.0, -23.0), noz=16.0, tip_len=59.3, seat=8.3, rack=(55.0, 10.0), pitch=9.0, cols=4, rows=2,
          rack_top=60.0, tip_top=68.0)
P3_HANG = P3["tip_len"] - P3["seat"] - P3["noz"]            # 35.0: a 300 uL tip's end below the carriage's reference
P3_TIPS = {"ptip": (0, 0), "ptip2": (1, 0), "ptip3": (2, 0), "ptip4": (3, 0)}     # (column, row) of the four used
P3_TIP_HOME = {k: (P3["rack"][0] + c * P3["pitch"], P3["rack"][1] + r * P3["pitch"]) for k, (c, r) in P3_TIPS.items()}
P3_JITTER = {"ptip2": (-7.0, 6.0), "ptip3": (7.0, -6.0), "ptip4": (-2.0, -9.0), "ptip": (8.0, 8.0)}
MIX_UL = 80.0                       # a mixing stroke: 150 uL stands 4.4 mm; 70 uL left still covers the tip at 2 mm


def p3_tip_level(ul: float) -> float:
    """Height above a 300 uL tip's end of `ul` microlitres: its bore widens from 0.7 mm at the end at 0.09 mm/mm."""
    if ul <= 0:
        return 0.0
    z, v, dz = 0.0, 0.0, 0.05
    while v < ul and z < 50:
        r = 0.35 + 0.045 * (z + dz / 2)
        v += math.pi * r * r * dz
        z += dz
    return z


def _corr_start(**kw) -> dict:
    return IL._corr_start(pcap="", ptip="rack", ptip2="rack", ptip3="rack", ptip4="rack", p3_ul=0.0, p3_liq="",
                          di=CORR["stock_ml"], **kw)




_CORR_SEGS = (("start", "Copper corrosion on the CubXL, as DAL's copper screen lays it out (PR #180): four stations, S1 "
                        "C71500 Cu-Ni, S2 C95800 NAB, S3 a DED pad, S4 a PTFE blank; Ben's 9-vial holder of stocks; three "
                        "cups; 2 x 8 ICP-MS tubes; tip racks. On the head: the capper, the P20, a P300 34 mm in front of "
                        "it (proposed, notes/cubxl_pipettes.md) and a camera."),
              ("tip", "1  The P300 (20-300 µL) takes a 300 µL tip from its rack at the deck's front left. One tip on "
                      "the head at a time: the two pipettes share one Z axis."),
              ("asw", "2  The capper lifts the seawater cap. The P300 builds S1's well from 135 µL of ASW in one "
                      "transfer (the P20 alone took 7), dispensed from above the meniscus; the cap goes back. The tip "
                      "only ever touches ASW, so it goes back to its rack for the next well."),
              ("filled", "3  Sulfide last, with the P20 (1-20 µL): a 20 µL tip, 15 µL of the 10 mg/L S stock, 150 µL "
                         "at 1 mg/L S. Then the P300 mixes the well, 3 strokes of 80 µL with a fresh tip: H2S leaves "
                         "a sulfide layer at the top far faster than it reaches the metal."),
              ("leak", "4  The head camera checks for liquid outside the O-ring (2 min)."),
              ("capped", "5  The capper carries the electrode cap (leak-free Ag/AgCl reference, Pt coil counter) from "
                         "its park cup and sets it over S1's boss: no O-ring, two small lid magnets hold it. No tip on."),
              ("measured", "6  Cap on, head free: OCP 20 min, EIS at OCP 10 min, LPR ±10 mV, rest 5 min, a +50 mV hold "
                           "for 10 min, OCP 5 min. EIS needs the requested potentiostat: the EZstat Pro has none, so "
                           "until then OCP runs 30 min."),
              ("parked", "7  The magnet lifts the cap off S1. It is dipped in DI water, then seawater, and parked."),
              ("collected", "8  The P300 moves the well's 150 µL to tube 1 in one transfer (the P20 took 8). A fresh "
                            "tip adds 150 µL of DI water from above, rinses S1 twice and carries the rinse to the "
                            "tube: 3 transfers where the P20 took 24."),
              ("acid", "9  Acidify at once: the capper opens the acid vial and the night's one acid tip adds 20 µL of "
                       "1 M HNO3 from above the rim with the P20: 320 µL at 62 mM HNO3. The acid tip goes back to "
                       "rack 2."),
              ("imaged", "10  The head camera images the spot. Next: S2. With the P300 the head works about 9 min a spot, "
                         "against 22.5 with the P20 alone (CubXL step times, notes/cubxl_pipettes.md)."),
              ("end", "Cyclic polarization runs only on selected spots, and last on each: fill to EIS, then the scan, "
                      "then its own tube. On every spot it would swamp the tube's copper (3.4 mC against the "
                      "hold's 0.2-2.8 mC)."))




def _corr_spot() -> Timeline:
    """The head and everything that changes on the deck through one spot (protocol.md section 4, render_cubxl_cu.py's
    build_story), with the P300 of round 14 taking the big transfers. Numbers interpolate between waypoints; text (what
    the tip holds, which transfer) holds from the waypoint where it is set."""
    p = CORR
    TZ = p["travel_z"]
    tl = Timeline(_corr_start())
    h = Head(tl)
    go, travel, down, pip_to, bare_to, capper_to, camera_to = (h.go, h.travel, h.down, h.pip_to, h.bare_to,
                                                               h.capper_to, h.camera_to)

    def p3_to(x, y, tip_end):            # the P300 with a tip, its end at deck z tip_end
        travel(x - P3["off"][0], y - P3["off"][1])
        down(tip_end + P3_HANG)

    def p3_bare(x, y, nozzle):           # the bare P300 nozzle at deck z `nozzle`
        travel(x - P3["off"][0], y - P3["off"][1])
        down(nozzle - P3["noz"])
    st = p["stations"]
    S1 = (st[0], p["station_y"])
    hy = lambda k: p["holder_y0"] + k * p["holder_dy"]     # noqa: E731
    acid, asw, s10, di = (p["holder_x"], hy(1)), (p["holder_x"], hy(2)), (p["holder_x"], hy(3)), (p["holder_x"], hy(5))
    tube1 = (p["tubes_x0"], p["tubes_y"][0])
    r1a1 = p["rack1"]
    r2a1 = CORR["rack2_drawn"]
    lid, face, cup = p["lid"], p["face"], p["cup_rim"]
    cap_face = p["cap_h"]              # the magnet face sits on the cap's disc, cap_h above where the cap rests
    over = lid + 1.0                   # dispense with the tip end 1 mm over the lid: above the meniscus (4.4 mm max)
    seat = P3["tip_top"] - P3["seat"]  # the P300's nozzle, pressed into a tip in its rack
    # 0. the deck, the head parked
    go(2.6)
    tl.mark("start")
    # 1. the P300 takes a 300 µL tip from its rack (front left); one tip on the head at a time
    p3_bare(*P3_TIP_HOME["ptip"], seat)
    go(0.25, ptip="head", panel=1, what="the P300 takes a 300 µL tip from its rack")
    go(0.3, z=TZ)
    tl.mark("tip")
    # 2. the capper lifts the ASW cap; the P300 draws 135 µL and dispenses it into S1 from above the meniscus; the cap
    # goes back; the tip, which only ever touches ASW, goes back to its rack for the next well
    capper_to(*asw, p["vial_cap"])
    go(0.2, vcap="asw", what="the capper lifts the ASW cap")
    go(0.25, z=TZ)
    p3_to(*asw, 35.0)
    go(0.5, p3_ul=135.0, p3_liq="ASW", asw=p["stock_ml"] - 0.135, xfer="ASW: 1 transfer of 135 µL (P300)",
       what="the P300 draws 135 µL of ASW")
    p3_to(*S1, over)
    go(0.5, p3_ul=0.0, well=135.0, what="and dispenses it into S1, above the meniscus")
    capper_to(*asw, p["vial_cap"])
    go(0.2, vcap="", what="the ASW cap goes back")
    go(0.25, z=TZ)
    p3_bare(*P3_TIP_HOME["ptip"], seat + 2.0)
    go(0.25, ptip="rack", xfer="", p3_liq="", what="the P300's ASW tip goes back to its rack, for the next well")
    go(0.3, z=TZ)
    tl.mark("asw")
    # 3. sulfide last, with the P20: a 20 µL tip, the sulfide cap off, 15 µL from above the meniscus, the cap back, the
    # tip to the waste; then the P300 mixes S1 with a fresh tip (3 strokes of 80 µL), and that tip to the waste too
    bare_to(*r1a1, p["tip_top"] - 4.0)
    go(0.2, tip="head", what="the P20 takes a 20 µL tip from Ben's rack 1")
    go(0.3, z=TZ)
    capper_to(*s10, p["vial_cap"])
    go(0.2, vcap="s10", what="the capper lifts the 10 mg/L S cap")
    go(0.25, z=TZ)
    pip_to(*s10, 35.0)
    go(0.35, tip_ul=15.0, liq="10 mg/L S", s10=p["stock_ml"] - 0.015, xfer="sulfide: 1 transfer of 15 µL (P20)",
       what="the P20 draws 15 µL of the 10 mg/L S stock")
    pip_to(*S1, over)
    go(0.35, tip_ul=0.0, well=150.0, what="adds it to S1: 150 µL at 1 mg/L S")
    capper_to(*s10, p["vial_cap"])
    go(0.2, vcap="", what="the sulfide cap goes back")
    go(0.25, z=TZ)
    pip_to(*p["waste"], 60.0)
    go(0.3, tip="waste", xfer="", liq="", what="the P20's tip drops into the waste")
    p3_bare(*P3_TIP_HOME["ptip2"], seat)
    go(0.25, ptip2="head", what="the P300 takes a fresh tip to mix the well")
    go(0.3, z=TZ)
    for k in range(1, 4):
        h.speed = 1.0 if k == 1 else 0.5
        p3_to(*S1, face + 2.0)
        go(0.3, p3_ul=MIX_UL, p3_liq="the well's liquid", well=150.0 - MIX_UL, xfer=f"mix: stroke {k} of 3 (P300)",
           what=f"mixes S1: draws {MIX_UL:.0f} µL", lapse=0 if k == 1 else 1)
        go(0.3, p3_ul=0.0, well=150.0, what="and returns it")
    h.speed = 1.0
    p3_to(*p["waste"], 60.0)
    go(0.3, ptip2="waste", xfer="", p3_liq="", lapse=0, what="the mixing tip drops into the waste")
    tl.mark("filled")
    # 4. leak check with the head camera, 2 min
    camera_to(*S1)
    go(1.6, what="head camera: no liquid outside the O-ring after 2 min")
    tl.mark("leak")
    # 5. the electrode cap from the park cup onto S1's boss (tipless)
    capper_to(p["cups"][2][1], p["cup_y"], cup + cap_face)
    go(0.25, cap="head", what="the capper picks up the electrode cap")
    go(0.3, z=TZ)
    capper_to(*S1, lid + cap_face)
    go(0.25, cap="S1", capped=1, what="it sets the cap over S1's boss")
    go(0.3, z=TZ)
    travel(*p["park"])
    tl.mark("capped")
    # 6. the measurement; the head is free
    go(9.0, meas=1.0, what="")
    tl.mark("measured")
    # 7. the cap off, dipped in DI water, then in seawater, parked
    capper_to(*S1, lid + cap_face)
    go(0.25, cap="head", capped=0, what="the magnet lifts the cap off S1")
    for (_, cx_, _), what in ((p["cups"][1], "dipped in DI water"), (p["cups"][0], "dipped in seawater")):
        capper_to(cx_, p["cup_y"], cup + cap_face)
        go(0.35, what=what)
        go(0.25, z=TZ)
    capper_to(p["cups"][2][1], p["cup_y"], cup + cap_face)
    go(0.25, cap="park", what="parked")
    go(0.25, z=TZ)
    tl.mark("parked")
    # 8. the P300: a new tip moves the well's 150 µL to tube 1 in one transfer; a fresh tip draws 150 µL of DI water
    # (the capper opens the DI vial), adds it to S1 from above, rinses S1 with two strokes and carries it to tube 1
    p3_bare(*P3_TIP_HOME["ptip3"], seat)
    go(0.25, ptip3="head", what="the P300 takes a new tip")
    go(0.3, z=TZ)
    p3_to(*S1, face + 0.5)
    go(0.5, p3_ul=150.0, p3_liq="the well's liquid", well=0.0, xfer="collect: 1 transfer of 150 µL (P300)",
       what="draws S1's 150 µL")
    p3_to(*tube1, 40.0)
    go(0.5, p3_ul=0.0, tube=150.0, what="dispenses it into tube 1, above the rim")
    p3_to(*p["waste"], 60.0)
    go(0.3, ptip3="waste", xfer="", p3_liq="", what="the tip drops into the waste")
    p3_bare(*P3_TIP_HOME["ptip4"], seat)
    go(0.25, ptip4="head", what="a fresh tip for the rinse")
    go(0.3, z=TZ)
    capper_to(*di, p["vial_cap"])
    go(0.2, vcap="di", what="the capper lifts the DI water cap")
    go(0.25, z=TZ)
    p3_to(*di, 35.0)
    go(0.5, p3_ul=150.0, p3_liq="DI water", di=p["stock_ml"] - 0.150, xfer="rinse: 150 µL of DI water (P300)",
       what="draws 150 µL of DI water")
    p3_to(*S1, over)
    go(0.5, p3_ul=0.0, well=150.0, what="adds it to S1 from above")
    capper_to(*di, p["vial_cap"])
    go(0.2, vcap="", what="the DI cap goes back")
    go(0.25, z=TZ)
    for k in range(1, 3):
        h.speed = 0.5
        p3_to(*S1, face + 2.0)
        go(0.3, p3_ul=MIX_UL, p3_liq="the rinse", well=150.0 - MIX_UL, xfer=f"rinse: stroke {k} of 2", lapse=1)
        go(0.3, p3_ul=0.0, well=150.0)
    h.speed = 1.0
    p3_to(*S1, face + 0.5)
    go(0.5, p3_ul=150.0, p3_liq="the rinse", well=0.0, xfer="rinse: to the tube", lapse=0, what="draws the rinse")
    p3_to(*tube1, 40.0)
    go(0.5, p3_ul=0.0, tube=300.0, what="into tube 1: 300 µL")
    p3_to(*p["waste"], 60.0)
    go(0.3, ptip4="waste", xfer="", p3_liq="", what="the tip drops into the waste")
    tl.mark("collected")
    # 9. acidify at once: the acid cap off, the night's one acid tip (rack 2), 20 µL of 1 M HNO3 from above the rim,
    # the acid tip back to its rack, the cap back
    capper_to(*acid, p["vial_cap"])
    go(0.2, vcap="acid", what="the capper lifts the acid cap")
    go(0.25, z=TZ)
    bare_to(*r2a1, p["tip_top"] - 4.0)
    go(0.2, tip3="head", what="the night's one acid tip, from rack 2")
    go(0.3, z=TZ)
    pip_to(*acid, 35.0)
    go(0.35, tip_ul=20.0, liq="1 M HNO3", acid=p["stock_ml"] - 0.020, xfer="acid, 1 transfer (P20)",
       what="draws 20 µL of 1 M HNO3")
    pip_to(*tube1, 37.0)
    go(0.35, tip_ul=0.0, tube=320.0, what="adds it from above the rim: 320 µL, 62 mM HNO3")
    bare_to(*r2a1, p["tip_top"] - 1.0)
    go(0.25, tip3="rack", xfer="", liq="", what="the acid tip goes back to rack 2")
    go(0.3, z=TZ)
    capper_to(*acid, p["vial_cap"])
    go(0.2, vcap="", what="the acid cap goes back")
    go(0.25, z=TZ)
    tl.mark("acid")
    # 10. image the spot; park
    camera_to(*S1)
    go(1.0, what="head camera: the spot after the test")
    travel(*p["park"])
    tl.mark("imaged")
    # 11. the sequence, in one card
    go(4.0, end=1.0, panel=0, what="")
    tl.mark("end")
    return tl




def _corr_parts(inst: Instrument):
    """Every deck item, the head's tools and the electrode cap, in the model's frame (CubOS -> _corr_w)."""
    p = CORR
    body = _piece(inst, "body")
    dz = p["deck_z"]
    face, lid = _cz(p["face"]), _cz(p["lid"])
    # ---- the coupon tray: four stations under printed lids, each with an O-ring well, RE and CE pads
    tx0, tx1, ty0, ty1 = _cx(p["tray"][0]), _cx(p["tray"][1]), _cy(p["tray"][2]), _cy(p["tray"][3])
    body.add("coupon tray", box(tx0, ty0, dz, tx1, ty1, face - 6), "lab_tray")
    sy = _cy(p["station_y"])
    lids = None
    for i, sx_ in enumerate(p["stations"]):
        x = _cx(sx_)
        name, mat = p["specimens"][i]
        spec = box(x - 10, sy - 10, face - 6, x + 10, sy + 10, face) if i < 3 else cyl(20, 6, x=x, y=sy, z=face - 6)
        body.add(f"S{i + 1} {name}", spec, mat)
        plate = box(x - 11.5, sy - 17, face, x + 11.5, sy + 17, face + 3.0).union(cyl(16, 6, x=x, y=sy, z=face))
        plate = plate.cut(cyl(7.3, 1.42, x=x, y=sy, z=face - 0.01)).cut(cyl(2 * p["a_spot"], 2, x=x, y=sy, z=face)) \
            .cut(cyl(2 * p["r_bore"], 10, x=x, y=sy, z=face + p["z_step"]))
        lids = plate if lids is None else lids.union(plate)
        body.add(f"S{i + 1} O-ring", tube(6.46, 2.9, 1.42, x=x, y=sy, z=face), "pp_black")
        for sgn in (-1, 1):
            body.add(f"pad S{i + 1} {sgn:+d}", box(x + sgn * 11 - 1.5, sy - 3, face + 3.0, x + sgn * 11 + 1.5, sy + 3,
                                                   face + 3.6), "brass")
    body.add("lids", lids, "lab_lid")
    body.add("bus connector", box(tx0 + 40, ty1, dz + 6, tx0 + 80, ty1 + 6, face - 6), "printer_black")
    # ---- Ben's 9-position holder (STEP) and its six vials, caps from Ben's VialCap16mm STEP
    hx = _cx(p["holder_x"])
    hy = [_cy(p["holder_y0"] + k * p["holder_dy"]) for k in range(9)]
    try:
        holder = cq.importers.importStep(str(CAPPER_CAD / "9VialHolder20mL_TightFit.step"))
        holder = holder.rotate((0, 0, 0), (0, 0, 1), 180).translate((hx, hy[0], dz))
    except Exception:                              # no STEP: its envelope (33.4 x 297.4 x 35 mm)
        holder = box(hx - 16.7, hy[0] - 16.7, dz, hx + 16.7, hy[-1] + 16.7, dz + p["holder_top"])
    body.add("9-vial holder", holder, "lab_petg_dark")
    try:
        vcap = cq.importers.importStep(str(CAPPER_CAD / "VialCap16mm.step"))
    except Exception:
        vcap = cyl(28, 18.5, z=-18.0)
    movable = {"1 M HNO3, trace metal": "vcap_acid", "ASW (D1141, no heavy metals)": "vcap_asw",
               "ASW + 10 mg/L S": "vcap_s10", "DI water": "vcap_di"}
    for name, k, mat in p["stocks"]:
        x, y = hx, hy[k]
        body.add(f"vial {name}", tube(27.5, 25.2, p["vial_rim"], x=x, y=y, z=dz).union(cyl(27.5, 1.5, x=x, y=y, z=dz)),
                 "glass")
        body.add(f"{name} liquid", cyl(25.0, 36.0, x=x, y=y, z=dz + 1.5), mat)
        tgt = _piece(inst, movable[name]) if name in movable else body
        tgt.add(f"{name} cap", vcap.translate((x, y, _cz(p["vial_cap"] - 0.5))), "pp_white")
        if k == 0:                # the spare seat's vial (FeSO4 nights only): a piece, so round 2's workflow can drop it
            spare = _piece(inst, "spare")
            for part in [pt for pt in body.parts if pt.name in (f"vial {name}", f"{name} liquid", f"{name} cap")]:
                body.parts.remove(part)
                spare.parts.append(part)
    # ---- the cap-parking vial (round 9): an empty 20 mL vial in the holder's seat 6 whose only job is to hold a cap
    px_, py_ = hx, hy[PARK_SEAT]
    body.add("cap-parking vial (empty)", tube(27.5, 25.2, p["vial_rim"], x=px_, y=py_, z=dz)
             .union(cyl(27.5, 1.5, x=px_, y=py_, z=dz)), "glass")
    # ---- the three cups (4 mL vials) on their block
    cy_ = _cy(p["cup_y"])
    body.add("cup block", box(_cx(16), cy_ - 12, dz, _cx(104), cy_ + 12, dz + 8), "lab_petg")
    for name, x_, mat in p["cups"]:
        x = _cx(x_)
        body.add(name, tube(15, 13.2, p["cup_rim"], x=x, y=cy_, z=dz).union(cyl(15, 1.5, x=x, y=cy_, z=dz)), "glass")
        body.add(f"{name} liquid", cyl(13.0, 40.0, x=x, y=cy_, z=dz + 1.5), mat)
    # ---- the tube rack, 2 x 8 open 0.5 mL tubes
    rx0, rx1, ry0, ry1 = (_cx(p["tube_rack"][0]), _cx(p["tube_rack"][1]), _cy(p["tube_rack"][2]),
                          _cy(p["tube_rack"][3]))
    xs = [p["tubes_x0"] + p["tubes_dx"] * k for k in range(8)]
    rack = box(rx0, ry0, dz, rx1, ry1, dz + 20)
    for x_ in xs:
        for y_ in p["tubes_y"]:
            rack = rack.cut(cyl(8.4, 25, x=_cx(x_), y=_cy(y_), z=dz + 1))
    body.add("tube rack", rack, "lab_petg")
    prof_out = [(0, 0), (1.3, 0), (3.6, 12.4), (3.85, 30.5), (4.6, 30.5), (4.6, p["tube_top"]), (0, p["tube_top"])]
    prof_in = [(0, _TUBE_IN[0][0])] + [(r, z) for z, r in _TUBE_IN] + [(0, _TUBE_IN[-1][0] + 1)]
    tshape = _revolve_rz(prof_out).cut(_revolve_rz(prof_in))
    tubes = [tshape.translate((_cx(x_), _cy(y_), dz + 1)).val() for x_ in xs for y_ in p["tubes_y"]]
    body.add("0.5 mL tubes", cq.Workplane().add(cq.Compound.makeCompound(tubes)), "lab_tube")
    # tube 1's liquid, modelled to the 320 uL level and scaled by its Level joint
    h320 = tube_level(320.0)
    liq = _revolve_rz([(0, _TUBE_IN[0][0])] + [(r - 0.05, z) for z, r in _TUBE_IN if z < h320] +
                      [(_tube_r(h320) - 0.05, h320), (0, h320)])
    _piece(inst, "tubeliq").add("tube 1 liquid", liq.translate((_cx(xs[0]), _cy(p["tubes_y"][0]), dz + 1)), "lab_well")
    # ---- tip racks: Ben's (rack 1) and DAL's printed rack 2, 2 x 15 tips each; the three tips the spot uses move
    tip = _revolve_rz([(0, 0), (0.45, 0), (2.6, 30), (2.9, 37), (3.3, p["tip_len"]), (0, p["tip_len"])])
    tips = []
    for rk, (ax, ay) in (("rack 1", p["rack1"]), ("rack 2", CORR["rack2_drawn"])):
        cols = (ax, ax - p["rack_pitch"])
        x0r, x1r = _cx(min(cols) - 5.75), _cx(max(cols) + 5.75)
        y0r, y1r = _cy(ay - 4.0), _cy(ay + (p["rack_rows"] - 1) * p["rack_pitch"] + 4.0)
        body.add(f"tip {rk}", box(x0r, y0r, dz, x1r, y1r, _cz(p["rack_top"])),
                 "lab_petg_dark" if rk == "rack 1" else "lab_petg")
        for r in range(p["rack_rows"]):
            for c, cx_ in enumerate(cols):
                at = (_cx(cx_), _cy(ay + r * p["rack_pitch"]), _cz(p["tip_top"] - p["tip_len"]))
                key = {("rack 1", 0, 0): "tip", ("rack 1", 0, 1): "tip2", ("rack 2", 0, 0): "tip3"}.get((rk, r, c))
                if key:
                    _piece(inst, key).add(f"{key} ({rk})", tip.translate(at), "lab_tip")
                    continue
                tips.append(tip.translate(at).val())
    body.add("tips", cq.Workplane().add(cq.Compound.makeCompound(tips)), "lab_tip")
    wx, wy = _cx(p["waste"][0]), _cy(p["waste"][1])
    body.add("tip waste", tube(p["waste_d"], p["waste_d"] - 3, p["waste_top"], x=wx, y=wy, z=dz)
             .union(cyl(p["waste_d"], 2, x=wx, y=wy, z=dz)), "printer_grey")
    # ---- round 14: the P300's tips, a printed 2 x 4 rack at the deck's front left (Opentrons 300 uL tips, 59.3 mm,
    # their collars on the rack's top, in pockets so nothing overlaps)
    tip3 = _revolve_rz([(0, 0), (0.45, 0), (2.4, 46.0), (2.9, 50.0), (3.8, 51.5), (3.8, P3["tip_len"]),
                        (0, P3["tip_len"])])
    xs3 = [P3["rack"][0] + c * P3["pitch"] for c in range(P3["cols"])]
    ys3 = [P3["rack"][1] + r * P3["pitch"] for r in range(P3["rows"])]
    rk3 = box(_cx(xs3[0] - 5.5), _cy(ys3[0] - 5.5), dz, _cx(xs3[-1] + 5.5), _cy(ys3[-1] + 5.5), _cz(P3["rack_top"]))
    for x_ in xs3:
        for y_ in ys3:
            rk3 = rk3.cut(cyl(8.2, P3["rack_top"], x=_cx(x_), y=_cy(y_), z=dz + 4.0))
    body.add("P300 tip rack", rk3, "lab_petg")
    z_tip3 = _cz(P3["tip_top"] - P3["tip_len"])
    spare3 = []
    for c, x_ in enumerate(xs3):
        for r, y_ in enumerate(ys3):
            key = next((k for k, cr in P3_TIPS.items() if cr == (c, r)), None)
            if key:
                _piece(inst, key).add(f"{key} (P300 rack)", tip3.translate((_cx(x_), _cy(y_), z_tip3)), "lab_tip")
            else:
                spare3.append(tip3.translate((_cx(x_), _cy(y_), z_tip3)).val())
    body.add("P300 tips", cq.Workplane().add(cq.Compound.makeCompound(spare3)), "lab_tip")
    return body




def corr_offsets(s: dict) -> dict:
    """{piece: (dx, dy, dz)} of everything that moves, for a timeline state: the gantry (y), the carriage (x), the
    tools (z, from travel height), the electrode cap, the three vial caps and the three tips, each from where it is
    modelled."""
    p = CORR
    out = {"gantry": (0.0, s["y"], 0.0), "carriage": (s["x"], 0.0, 0.0), "tools": (0.0, 0.0, s["z"] - p["travel_z"])}
    park = (p["cups"][2][1], p["cup_y"], p["cup_rim"])
    if s["cap"] == "head":       # the cap's skirt underside: the magnet face, less the cap's height
        at = (s["x"], s["y"], s["z"] - p["magnet"] - p["cap_h"])
    elif s["cap"] == "S1":
        at = (p["stations"][0], p["station_y"], p["lid"])
    else:
        at = park
    out["cap"] = tuple(a - b for a, b in zip(at, park))
    for name, k in (("asw", 2), ("s10", 3), ("acid", 1), ("di", 5)):   # a vial cap on the magnet: its top at the face
        hx, hy = p["holder_x"], p["holder_y0"] + k * p["holder_dy"]
        out[f"vcap_{name}"] = ((s["x"] - hx, s["y"] - hy, s["z"] - p["magnet"] - p["vial_cap"])
                               if s["vcap"] == name else
                               (0.0, p["holder_dy"] * (PARK_SEAT - k), 0.0) if s.get("pcap", "") == name
                               else (0.0, 0.0, 0.0))
    jitter = {"tip": (-5.0, -4.0), "tip2": (5.0, 3.0), "tip3": (0.0, 5.0)}
    for key, home in TIP_HOME.items():
        if s[key] == "head":         # its top 4 mm above the nozzle, its end 35 mm below
            at = (s["x"] + p["pip"][0], s["y"] + p["pip"][1], s["z"] + 4.0 - p["tip_len"])
        elif s[key] == "waste":      # lying in the waste, side by side (collide.py found two in one spot before)
            at = (p["waste"][0] + jitter[key][0], p["waste"][1] + jitter[key][1], 2.0)
        else:
            at = (home[0], home[1], p["tip_top"] - p["tip_len"])
        out[key] = (at[0] - home[0], at[1] - home[1], at[2] - (p["tip_top"] - p["tip_len"]))
    # round 14: the P300's four tips (states without them, e.g. instruments_lab.powder_test's, leave them in the rack)
    z_home = P3["tip_top"] - P3["tip_len"]
    for key, home in P3_TIP_HOME.items():
        where = s.get(key, "rack")
        if where == "head":          # its end P3_HANG below the carriage's reference
            at = (s["x"] + P3["off"][0], s["y"] + P3["off"][1], s["z"] - P3_HANG)
        elif where == "waste":
            at = (p["waste"][0] + P3_JITTER[key][0], p["waste"][1] + P3_JITTER[key][1], 2.0)
        else:
            at = (home[0], home[1], z_home)
        out[key] = (at[0] - home[0], at[1] - home[1], at[2] - z_home)
    return out


# the liquid in the P300's tip (round 14): a cone up the bore from the tip's end, modelled 150 uL tall, on the head
LEVEL_AT = dict(IL.LEVEL_AT)
LEVEL_AT["p3liq"] = (_cz(CORR["travel_z"]) - P3_HANG + 0.15, p3_tip_level(150.0), "tools")


def corr_levels(s: dict) -> dict:
    """instruments_lab.corr_levels, and the P300 tip's liquid."""
    out = IL.corr_levels(s)
    out["p3liq"] = p3_tip_level(s.get("p3_ul", 0.0))
    return out




def cubxl_corrosion() -> Instrument:
    import equipment
    p = CORR
    W, D = equipment.CUBXL["W"], equipment.CUBXL["D"]
    inst = Instrument(
        "cubxl_corrosion", "Copper corrosion spots on the CubXL", "CubXL + NuVant EZstat Pro",
        (W + 70 + 30 + p["ez"][0], D, equipment.CUBXL["H"] + 50),
        "The CubXL from lab_models.equipment.cubxl() (#199); the deck, the head and one spot as digital-alloy-lab PR "
        "#180 lays them out for copper (alloy-corrosion/copper/deck_cu.py, protocol.md, render_cubxl_cu.py at aeda51a); "
        "Ben's capper mount, 9-vial holder and vial cap STEPs (modules/electromagnetic-capper/cad); NuVant's EZstat Pro "
        "(255 x 245 x 102 mm, nuvant.com) beside it, as in byu-vcl #231 / DAL #221",
        props=("cap", "vcap_asw", "vcap_s10", "vcap_acid", "vcap_di", "tip", "tip2", "tip3", "ptip", "ptip2", "ptip3",
               "ptip4", "tipliq", "p3liq", "wellliq", "tubeliq", "led", "clock"))
    cub = equipment.cubxl(0.05, 0.0, 0.5)          # carriage at CubOS x 0, gantry at y 0
    gantry_names = ("gantry upright L", "gantry upright R", "gantry beam", "cable chain")
    carriage_names = ("z carriage", "tool plate", "controller")
    dropped = ("pipette", "capper", "vial rack", "tip rack") + tuple(f"vial {i}" for i in range(1, 7)) + \
        tuple(f"vial {i} cap" for i in range(1, 7))
    body, gantry, carriage = _piece(inst, "body"), _piece(inst, "gantry"), _piece(inst, "carriage")
    for part in cub.parts:
        if part.name in dropped:
            continue
        target = gantry if part.name in gantry_names else carriage if part.name in carriage_names else body
        target.parts.append(part)
    body = _corr_parts(inst)
    dz = p["deck_z"]
    # ---- the potentiostat beside the frame, and its cell cable to the tray's back edge
    ew, ed, eh = p["ez"]
    ex = p["ez_x"]
    tx0, ty1 = _cx(p["tray"][0]), _cy(p["tray"][3])
    body.add("EZstat Pro", rbox(ew, ed, eh - 8, 6, x=ex, y=60, z=8), "paint_grey")
    body.add("EZstat front", box(ex - ew / 2 + 6, 60 - ed / 2 - 1, 14, ex + ew / 2 - 6, 60 - ed / 2, eh - 6), "inst_dark")
    for sxx in (-1, 1):
        for syy in (-1, 1):
            body.add(f"EZstat foot {sxx}{syy}", cyl(14, 8, x=ex + sxx * (ew / 2 - 25), y=60 + syy * (ed / 2 - 25)),
                     "pp_black")
    body.add("cell connector", _xcyl(16, 12, x=ex - ew / 2 - 12, y=110, z=50), "steel")
    body.add("cell cable", hose([(ex - ew / 2 - 12, 110, 50), (ex - ew / 2 - 40, 200, 45), (360, 268, 70),
                                 (300, 268, 70), (200, 150, 92), (tx0 + 60, ty1 + 25, dz + 6),
                                 (tx0 + 60, ty1 + 6, dz + 10)], 6), "lab_cable")
    _piece(inst, "led").add("cell-on LED", _ycyl(7, 3, x=ex + ew / 2 - 30, y=60 - ed / 2 - 3, z=eh - 25), "glow")
    # ---- the head, at CubOS x 0, y 0, carriage at travel height: Ben's PAW-V2 mount and magnet, the P20, the camera
    tools = _piece(inst, "tools")
    zr = _cz(p["travel_z"])                      # the carriage's reference: the bare P20 nozzle's end
    hx0, hy0 = _cx(0), _cy(0)
    try:
        mount = cq.importers.importStep(str(CAPPER_CAD / "PAW-V2-ElectromagnetMount.step"))
        mount = mount.rotate((0, 0, 0), (1, 0, 0), 180)
        zmin = mount.val().BoundingBox().zmin
        mount = mount.translate((hx0 - 63.17, hy0 + 6.53, zr - p["magnet"] - zmin))   # its bore axis on (0, 0)
    except Exception:
        mount = cyl(30, 43, x=hx0, y=hy0, z=zr - p["magnet"])
    tools.add("capper mount (PAW-V2)", mount, "lab_mount")
    tools.add("capper magnet", cyl(25, 20, x=hx0, y=hy0, z=zr - p["magnet"] + 0.5), "steel")
    tools.add("capper arm", box(hx0 - 8, hy0 + 10, zr, hx0 + 8, hy0 + 25, zr + 26), "lab_mount")
    px, py = hx0 + p["pip"][0], hy0 + p["pip"][1]
    tools.add("P20 shaft", cyl(8, 44, x=px, y=py, z=zr), "lab_pip_shaft")
    tools.add("P20 body", box(px - 17, py - 13, zr + 44, px + 17, py + 13, zr + 150), "lab_pip")
    tools.add("P20 top", box(px - 17, py - 13, zr + 150, px + 17, py + 13, zr + 162), "inst_grey")
    cxm, cym = hx0 + p["cam"][0], hy0 + p["cam"][1]
    tools.add("camera_3", box(cxm - 11, cym - 11, zr + 8, cxm + 11, cym + 11, zr + 34), "printer_black")
    tools.add("camera lens", cyl(10, 3, x=cxm, y=cym, z=zr + 5), "glass")
    tools.add("camera arm", box(cxm - 5, cym + 11, zr + 20, cxm + 5, hy0 + 25, zr + 34), "printer_black")
    # the liquid in whichever tip is on the P20: a cone up the tip's bore from its end, modelled 11.4 mm (20 uL) tall
    hang = p["tip_hang"]
    h20 = tip_level(20.0)
    tl_shape = cq.Workplane().add(cq.Solid.makeCone(0.3, 0.3 + 0.072 * h20, h20, cq.Vector(px, py, zr - hang + 0.15),
                                                    cq.Vector(0, 0, 1)))
    _piece(inst, "tipliq").add("liquid in the tip", tl_shape, "lab_well")
    # ---- round 14: the P300 (OT-2 GEN2 single, 20-300 uL) on a bracket 34 mm in front of the P20, its nozzle 16 mm
    # higher (P3): shaft, body and top drawn as the P20's, the bracket back to the capper's arm
    qx, qy, qz = hx0 + P3["off"][0], hy0 + P3["off"][1], zr + P3["noz"]
    tools.add("P300 shaft", cyl(9, 44, x=qx, y=qy, z=qz), "lab_pip_shaft")
    tools.add("P300 body", box(qx - 16, qy - 13, qz + 44, qx + 16, qy + 13, qz + 150), "lab_pip")
    tools.add("P300 top", box(qx - 16, qy - 13, qz + 150, qx + 16, qy + 13, qz + 162), "inst_grey")
    tools.add("P300 bracket", box(qx - 10, qy + 13, qz + 70, qx + 10, py - 13, qz + 110), "lab_mount")
    h150 = p3_tip_level(150.0)
    p3_shape = cq.Workplane().add(cq.Solid.makeCone(0.35, 0.35 + 0.045 * h150, h150,
                                                    cq.Vector(qx, qy, zr - P3_HANG + 0.15), cq.Vector(0, 0, 1)))
    _piece(inst, "p3liq").add("liquid in the P300's tip", p3_shape, "lab_well")
    # ---- the electrode cap, modelled on the park cup: 26 mm flange, 16 mm body, steel disc, the Ag/AgCl capillary in a
    # Pt coil 3 mm below the skirt, two pogo pins at +-11 mm
    cap = _piece(inst, "cap")
    kx, ky, kz = _cx(p["cups"][2][1]), _cy(p["cup_y"]), _cz(p["cup_rim"])
    cap.add("cap flange", cyl(p["cap_d"], 4.0, x=kx, y=ky, z=kz), "pla_white")
    cap.add("cap body", cyl(18, p["cap_h"] - 5.2, x=kx, y=ky, z=kz + 4.0), "pla_white")
    cap.add("steel disc", cyl(12, 1.2, x=kx, y=ky, z=kz + p["cap_h"] - 1.2), "steel")
    cap.add("Ag/AgCl reference", cyl(2, p["cap_h"] + p["cap_el"] - 1.5, x=kx, y=ky, z=kz - p["cap_el"]), "lab_agcl")
    coil = None
    for k in range(4):
        c = tube(5.2, 4.4, 0.45, x=kx, y=ky, z=kz - p["cap_el"] + 0.3 + k * 0.7)
        coil = c if coil is None else coil.union(c)
    cap.add("Pt coil", coil, "chrome")
    for sgn in (-1, 1):
        cap.add(f"pogo {sgn:+d}", cyl(1.4, 2.6, x=kx + sgn * 11, y=ky, z=kz - 2.4), "brass")
    # ---- the liquid in well S1, modelled 3 mm deep and scaled by its Level joint
    s1x, s1y = _cx(p["stations"][0]), _cy(p["station_y"])
    _piece(inst, "wellliq").add("liquid in S1", cyl(2 * p["r_bore"] - 0.1, 3.0, x=s1x, y=s1y, z=_cz(p["face"]) + 0.02),
                                "lab_well")

    # ---- the joints: one timeline for the head, what it carries, and the liquid levels
    tl = _CORR_TL
    off = [corr_offsets(st) for st in tl.states]
    lev = [corr_levels(st) for st in tl.states]

    def knots(key):
        return tuple((t / tl.t[-1], tuple(float(c) for c in o[key])) for t, o in zip(tl.t, off))

    def lknots(key):
        return tuple((t / tl.t[-1], float(lv[key])) for t, lv in zip(tl.t, lev))
    inst.joints = {
        "gantry": Track(knots=knots("gantry")),
        "carriage": Track(parent="gantry", knots=knots("carriage")),
        "tools": Track(parent="carriage", knots=knots("tools")),
        **{k: Track(knots=knots(k)) for k in ("cap", "vcap_asw", "vcap_s10", "vcap_acid", "vcap_di", "tip", "tip2",
                                              "tip3", "ptip", "ptip2", "ptip3", "ptip4")},
        **{k: Level(parent=LEVEL_AT[k][2], knots=lknots(k), z0=LEVEL_AT[k][0], h0=LEVEL_AT[k][1])
           for k in ("tipliq", "p3liq", "wellliq", "tubeliq")},
        "led": Joint("fade"),
        "clock": Track(knots=((0.0, (0.0, 0.0, 0.0)), (1.0, (1.0, 0.0, 0.0)))),
    }
    moving = [k for k in inst.joints if k != "led"]

    def seg(a, b, **extra):
        out = {k: (tl.v(a), tl.v(b)) for k in moving}
        out.update(extra)
        return out
    inst.actions = []
    prev = None
    for m, cap_txt in _CORR_SEGS:
        if prev is None:
            # the carriage's 220 x 290 mm tool plate (#199's model) stands behind the head: drawn see-through
            inst.actions.append((cap_txt, tl.t[tl.marks[m]] * PACE,
                                 seg("start", "start") | {"clock": (0.0, tl.v(m)), "~carriage": (0.0, 0.7)}))
        else:
            extra = {"led": (0.0, 1.0)} if m == "measured" else {"led": (1.0, 0.0)} if m == "parked" else {}
            secs = (tl.t[tl.marks[m]] - tl.t[tl.marks[prev]]) * PACE
            inst.actions.append((cap_txt, secs, seg(prev, m, **extra)))
        prev = m
    hxw = _cx(p["holder_x"])
    hpy = p["holder_y0"] + PARK_SEAT * p["holder_dy"]
    # labels for the opening wide view only: the camera moves in after it (CAMS), where leaders would cross the deck
    inst.labels = [("electrode cap, parked", (kx, ky, kz + 18), (0.10, 0.24)),
                   ("S1-S4: Cu-Ni, NAB, DED pad, PTFE blank", (_cx(222), _cy(p["tray"][3]), _cz(p["lid"])), (0.40, 0.13)),
                   ("Ben's 9-vial holder: ASW, sulfide, acid, DI", (hxw, _cy(150), _cz(60)), (0.74, 0.80)),
                   ("empty vial: parks a cap", (hxw, _cy(hpy), _cz(60)), (0.62, 0.30)),
                   ("ICP-MS tubes", (_cx(200), _cy(28), _cz(32)), (0.14, 0.70)),
                   ("P300 tips (proposed)", (_cx(68), _cy(14), _cz(P3["tip_top"])), (0.06, 0.52)),
                   ("NuVant EZstat Pro", (ex - 40, 60 - ed / 2, eh), (0.90, 0.40))]
    inst.step_labels = {i: [] for i in range(1, len(inst.actions))}
    inst.cam = (0.55, -1.5, 1.25)
    inst.framing = (0.80, 0.30)
    inst.notes = ["Deck, head and spot: DAL PR #180's copper plan (aeda51a), not yet built",
                  "Round 14: a P300 beside the P20 takes the 135 and 150 uL transfers and mixes the well; proposed in "
                  "notes/cubxl_pipettes.md, not DAL's plan",
                  "P20 and P300 volumes and levels to scale; the measurement plot is illustrative"]
    return inst


# cameras (model frame), by action index. DAL's own run view (render_cubxl_cu.RUN_WIDE, CubOS (700, -520, 540) looking at
# (225, 150, 30)) for the deck; closer in for the fill and the cell.
_C_WIDE = (_corr_w(700.0, -560.0, 640.0), _corr_w(205.0, 150.0, 30.0))
_C_FILL = (_corr_w(540.0, -330.0, 430.0), _corr_w(250.0, 170.0, 30.0))
_C_WELL = (_corr_w(120.0, 60.0, 170.0), _corr_w(200.0, 235.0, 22.0))
_C_CELL = (_corr_w(400.0, 360.0, 230.0), _corr_w(150.0, 225.0, 25.0))
_C_TUBE = (_corr_w(400.0, -340.0, 400.0), _corr_w(210.0, 100.0, 30.0))
_C_OVER = ((560.0, -1450.0, 1250.0), (60.0, 0.0, 180.0))
# the stock-and-parking-vial view: the holder from the side of the deck, the stocks and the parking vial in frame
_C_HOLD = (_corr_w(140.0, 40.0, 340.0), _corr_w(318.0, 175.0, 45.0))
def _draw_corr_overlay_r14(sc, img, s):
    """instruments_lab._draw_corr_overlay with both pipettes in the liquid panel and the P300's transfer counts on the
    closing card (round 14)."""
    from PIL import ImageDraw
    from scene import font
    v = _gv(sc, "cubxl_corrosion:clock")
    st = _corr_state(v)
    W, H = img.size
    d = ImageDraw.Draw(img, "RGBA")
    ft, fs, fm = font(13.5 * s, bold=True), font(12 * s), font(12 * s, mono=True)
    ink, mute = (20, 20, 24, 255), (80, 84, 90, 255)
    measuring = 0.0005 < st["meas"] < 0.9999 or (st["meas"] >= 0.9999 and st["cap"] == "S1")
    if st["panel"] > 0.5 and not measuring:
        x0, y0 = W - 345 * s, 46 * s
        p3ul, p3liq = st.get("p3_ul", 0.0), st.get("p3_liq", "")
        rows = [("P300 tip", f"{p3ul:5.1f} µL {p3liq}" if p3ul > 0.05 else "  0.0 µL"),
                ("P20 tip", f"{st['tip_ul']:5.1f} µL {st['liq']}" if st["tip_ul"] > 0.05 else "  0.0 µL"),
                ("well S1", f"{st['well']:5.1f} µL, {well_level(st['well'], st['capped'] > 0.5):.1f} mm deep"),
                ("tube 1", f"{st['tube']:5.1f} µL, {tube_level(st['tube']):4.1f} mm"),
                ("ASW vial", f"{st['asw']:.3f} mL")]
        if st.get("di", CORR["stock_ml"]) < CORR["stock_ml"] - 1e-6:
            rows.append(("DI vial", f"{st['di']:.3f} mL"))
        if st["acid"] < CORR["stock_ml"] - 1e-6:
            rows.append(("acid vial", f"{st['acid']:.3f} mL"))
        h = (30 + 19 * len(rows) + (20 if st["xfer"] else 0)) * s
        d.rounded_rectangle((x0, y0, W - 10 * s, y0 + h), 6 * s, fill=(255, 255, 255, 232), outline=(150, 156, 164, 255))
        d.text((x0 + 10 * s, y0 + 6 * s), "P300 (20-300 µL) + P20 (1-20 µL)", font=ft, fill=ink)
        for i, (k, val) in enumerate(rows):
            yy = y0 + (28 + 19 * i) * s
            d.text((x0 + 10 * s, yy), k, font=fs, fill=mute)
            d.text((x0 + 92 * s, yy), val, font=fm, fill=ink)
        if st["xfer"]:
            yy = y0 + (28 + 19 * len(rows)) * s
            d.text((x0 + 10 * s, yy), st["xfer"] + ("  (sped up)" if st["lapse"] > 0.5 else ""), font=ft,
                   fill=(30, 60, 140, 255))
    if measuring:
        _draw_corr_measure(d, W, H, s, st["meas"])
    if st["end"] > 0.02:
        a = min(1.0, st["end"] * 4)
        x0, y0, x1 = W * 0.16, 70 * s, W * 0.84
        d.rounded_rectangle((x0, y0, x1, y0 + 275 * s), 8 * s, fill=(255, 255, 255, int(238 * a)),
                            outline=(150, 156, 164, int(255 * a)))
        al = int(255 * a)
        lines = [("One spot (DAL protocol.md section 4), with a P300 beside the P20 (proposed)", True),
                 ("fill: 135 µL ASW (P300, 1 transfer)  >  15 µL sulfide (P20)  >  mix (P300)", False),
                 ("leak check  >  cap on  >  OCP 20 min  >  EIS at OCP 10 min  >  LPR ±10 mV", False),
                 ("rest 5 min  >  +50 mV hold 10 min  >  OCP 5 min  >  cap off, rinsed", False),
                 ("well + DI rinse to its tube (3 P300 transfers, the P20 alone took 24)  >  20 µL HNO3", False),
                 ("6 transfers a spot instead of 33; the head works about 9 min a spot instead of 22.5", False),
                 ("Each piece's second well: the same, OCP only (the companion)", False),
                 ("Selected spots only, last: fill to EIS, then cyclic polarization", True),
                 ("from 50 mV below OCP at 1 mV/s, reversing at 1 mA/cm2, back to E_corr; its own tube", False),
                 ("Nobody has run a spot yet: DAL's plan, PR #180; the P300 is notes/cubxl_pipettes.md's", False)]
        for i, (t, b) in enumerate(lines):
            d.text((x0 + 16 * s, y0 + (14 + 25 * i) * s), t, font=ft if b else fs,
                   fill=(20, 20, 24, al) if i < 9 else (150, 40, 30, al))


_CORR_TL = _corr_spot()
IL._CORR_TL = _CORR_TL          # the measurement overlay (instruments_lab._draw_corr_overlay) reads the timeline there
PLOTS["instruments/cubxl_corrosion"] = _draw_corr_overlay_r14
# round 14: the P300 fetches its tips from the deck's front left and works at the holder and S1, so steps 1-3 use a
# view of the whole front half of the deck
_C_P300 = (_corr_w(240.0, -470.0, 600.0), _corr_w(195.0, 135.0, 75.0))
CAMS["instruments/cubxl_corrosion"] = {0: _C_WIDE, 1: _C_P300, 2: _C_P300, 3: _C_P300, 4: _C_FILL, 5: _C_CELL,
                                       6: _C_CELL, 7: _C_FILL, 8: _C_P300, 10: _C_WIDE, 11: _C_OVER}
REGISTRY = {"cubxl_corrosion": cubxl_corrosion}
