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

import instruments_lab as IL

# every helper, constant and material of instruments_lab, so the copied functions below run unchanged
globals().update({k: v for k, v in vars(IL).items()
                  if not k.startswith("__") and k not in ("REGISTRY", "CAMS", "PLOTS", "LABELS", "MATERIALS")})
MATERIALS = {}
CAMS, PLOTS = IL.CAMS, IL.PLOTS

PARK_SEAT = 6                       # holder seat of the cap-parking vial (y 233)


def _corr_start(**kw) -> dict:
    return IL._corr_start(pcap="", **kw)




_CORR_SEGS = (("start", "Copper corrosion on the CubXL, as DAL's copper screen lays it out (PR #180): four stations, S1 "
                        "C71500 Cu-Ni, S2 C95800 NAB, S3 a DED pad, S4 a PTFE blank; Ben's 9-vial holder of stocks; three "
                        "cups; 2 x 8 ICP-MS tubes; two tip racks. On the head: the capper, a P20 and a camera."),
              ("tip", "1  The CubXL's P20 (1-20 µL) takes a 20 µL tip from Ben's rack."),
              ("asw", "2  The capper lifts the seawater cap and sets it on an empty parking vial in the same holder, so the "
                      "magnet is free. The P20 builds S1's well from 135 µL of ASW: 7 transfers of 19.3 µL, each "
                      "dispensed from above the meniscus."),
              ("filled", "3  Sulfide last, with the ASW still open: the magnet takes the sulfide cap (two stocks open, "
                         "one cap parked, one carried). 15 µL of the 10 mg/L S stock, same tip, makes 150 µL at 1 mg/L S; "
                         "then each cap goes home in turn and the tip goes to the waste."),
              ("leak", "4  The head camera checks for liquid outside the O-ring (2 min)."),
              ("capped", "5  The capper carries the electrode cap (leak-free Ag/AgCl reference, Pt coil counter) from "
                         "its park cup and sets it over S1's boss: no O-ring, two small lid magnets hold it. No tip on."),
              ("measured", "6  Cap on, head free: OCP 20 min, EIS at OCP 10 min, LPR ±10 mV, rest 5 min, a +50 mV hold "
                           "for 10 min, OCP 5 min. EIS needs the requested potentiostat: the EZstat Pro has none, so "
                           "until then OCP runs 30 min."),
              ("parked", "7  The magnet lifts the cap off S1. It is dipped in DI water, then seawater, and parked."),
              ("collected", "8  A new tip moves the well's 150 µL to tube 1 for ICP-MS, 8 transfers of 18.75 µL, then "
                            "a 150 µL DI rinse the same way: 16 transfers."),
              ("acid", "9  Acidify at once: the capper opens the acid vial and the night's one acid tip adds 20 µL of "
                       "1 M HNO3 from above the rim: 320 µL at 62 mM HNO3. The acid tip goes back to rack 2."),
              ("imaged", "10  The head camera images the spot. Next: S2. A spot is 67 min of deck time: eight wells "
                         "(three pieces, two wells each, and S4's two blanks) take about 9 h of a 12 h night."),
              ("end", "Cyclic polarization runs only on selected spots, and last on each: fill to EIS, then the scan, "
                      "then its own tube. On every spot it would swamp the tube's copper (3.4 mC against the "
                      "hold's 0.2-2.8 mC)."))




def _corr_spot() -> Timeline:
    """The head and everything that changes on the deck through one spot (protocol.md section 4, render_cubxl_cu.py's
    build_story). Numbers interpolate between waypoints; text (what the tip holds, which transfer) holds from the
    waypoint where it is set."""
    p = CORR
    TZ = p["travel_z"]
    tl = Timeline(_corr_start())
    h = Head(tl)
    go, travel, down, pip_to, bare_to, capper_to, camera_to = (h.go, h.travel, h.down, h.pip_to, h.bare_to,
                                                               h.capper_to, h.camera_to)
    st = p["stations"]
    S1 = (st[0], p["station_y"])
    hy = lambda k: p["holder_y0"] + k * p["holder_dy"]     # noqa: E731
    acid, asw, s10, di = (p["holder_x"], hy(1)), (p["holder_x"], hy(2)), (p["holder_x"], hy(3)), (p["holder_x"], hy(5))
    tube1 = (p["tubes_x0"], p["tubes_y"][0])
    r1a1, r1a2 = p["rack1"], (p["rack1"][0] - p["rack_pitch"], p["rack1"][1])
    r2a1 = CORR["rack2_drawn"]
    lid, face, cup = p["lid"], p["face"], p["cup_rim"]
    cap_face = p["cap_h"]              # the magnet face sits on the cap's disc, cap_h above where the cap rests
    over = lid + 1.0                   # dispense with the tip end 1 mm over the lid: above the meniscus (4.4 mm max)
    # 0. the deck, the head parked
    go(2.6)
    tl.mark("start")
    # 1. a 20 µL tip from Ben's rack
    bare_to(*r1a1, p["tip_top"] - 4.0)
    go(0.2, tip="head", panel=1, what="takes a 20 µL tip from Ben's rack 1")
    go(0.3, z=TZ)
    tl.mark("tip")
    # 2. the capper lifts the seawater cap and parks it on the empty parking vial (seat 6), so the magnet is free; 135 µL
    # of ASW in 7 transfers of 19.3 µL, from above the meniscus
    pv = (p["holder_x"], hy(PARK_SEAT))
    capper_to(*asw, p["vial_cap"])
    go(0.2, vcap="asw", what="the capper lifts the ASW cap")
    go(0.25, z=TZ)
    capper_to(*pv, p["vial_cap"])
    go(0.2, vcap="", pcap="asw", what="and sets it on the empty parking vial: the magnet is free")
    go(0.25, z=TZ)
    for k in range(1, 8):
        h.speed = 1.0 if k == 1 else 0.18
        lapse = 0 if k == 1 else 1
        pip_to(*asw, 35.0)
        go(0.35, tip_ul=TIP_UL, liq="ASW", asw=p["stock_ml"] - k * TIP_UL / 1000, xfer=f"ASW transfer {k} of 7",
           what=f"draws {TIP_UL:.1f} µL of ASW", lapse=lapse)
        pip_to(*S1, over)
        go(0.35, tip_ul=0.0, well=k * TIP_UL, what=f"dispenses it into S1, above the meniscus")
    h.speed = 1.0
    tl.mark("asw")
    # 3. sulfide last, with the ASW still open: the magnet takes the sulfide stock's cap (the ASW cap is on the parking
    # vial), 15 µL of the 10 mg/L S stock with the same tip -> 150 µL at 1 mg/L S; the tip to the waste; then each cap
    # goes back on its own vial, one at a time
    capper_to(*s10, p["vial_cap"])
    go(0.2, vcap="s10", what="the capper lifts the 10 mg/L S cap: two stocks open, one cap parked, one on the magnet")
    go(0.25, z=TZ)
    pip_to(*s10, 35.0)
    go(0.35, tip_ul=15.0, liq="10 mg/L S", s10=p["stock_ml"] - 0.015, xfer="sulfide, 1 transfer",
       what="draws 15 µL of the 10 mg/L S stock")
    pip_to(*S1, over)
    go(0.35, tip_ul=0.0, well=150.0, what="adds it to S1: 150 µL at 1 mg/L S")
    capper_to(*s10, p["vial_cap"])
    go(0.2, vcap="", what="the sulfide cap goes back")
    go(0.25, z=TZ)
    capper_to(*pv, p["vial_cap"])
    go(0.2, vcap="asw", pcap="", what="the magnet fetches the ASW cap from the parking vial")
    go(0.25, z=TZ)
    capper_to(*asw, p["vial_cap"])
    go(0.2, vcap="", what="and returns it to the ASW vial")
    go(0.25, z=TZ)
    pip_to(*p["waste"], 60.0)
    go(0.3, tip="waste", xfer="", liq="", what="the tip drops into the waste")
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
    # 8. a new tip; the well's 150 µL to tube 1 in 8 transfers of 18.75 µL; the 150 µL DI rinse the same way
    bare_to(*r1a2, p["tip_top"] - 4.0)
    go(0.2, tip2="head", what="a new tip")
    go(0.3, z=TZ)
    for k in range(1, 9):
        h.speed = 1.0 if k == 1 else 0.15
        pip_to(*S1, face + 0.5)
        go(0.35, tip_ul=18.75, liq="the well's liquid", well=150.0 - k * 18.75, xfer=f"collect: transfer {k} of 8",
           what="draws 18.75 µL from S1", lapse=0 if k == 1 else 1)
        pip_to(*tube1, 40.0)
        go(0.35, tip_ul=0.0, tube=k * 18.75, what="dispenses it into tube 1, above the rim")
    h.speed = 1.0
    go(0.6, well=150.0, xfer="DI rinse: 150 µL into S1", liq="", lapse=1, what="the 150 µL DI rinse")
    for k in range(1, 9):
        h.speed = 0.10
        pip_to(*S1, face + 0.5)
        go(0.35, tip_ul=18.75, liq="the rinse", well=150.0 - k * 18.75, xfer=f"rinse: transfer {k} of 8", lapse=1)
        pip_to(*tube1, 40.0)
        go(0.35, tip_ul=0.0, tube=150.0 + k * 18.75)
    h.speed = 1.0
    pip_to(*p["waste"], 60.0)
    go(0.3, tip2="waste", xfer="", liq="", lapse=0, what="the tip drops into the waste")
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
    go(0.35, tip_ul=20.0, liq="1 M HNO3", acid=p["stock_ml"] - 0.020, xfer="acid, 1 transfer",
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
               "ASW + 10 mg/L S": "vcap_s10"}
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
    for name, k in (("asw", 2), ("s10", 3), ("acid", 1)):     # a vial cap on the magnet: its top at the magnet face
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
        props=("cap", "vcap_asw", "vcap_s10", "vcap_acid", "tip", "tip2", "tip3", "tipliq", "wellliq", "tubeliq", "led",
               "clock"))
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
        **{k: Track(knots=knots(k)) for k in ("cap", "vcap_asw", "vcap_s10", "vcap_acid", "tip", "tip2", "tip3")},
        **{k: Level(parent=LEVEL_AT[k][2], knots=lknots(k), z0=LEVEL_AT[k][0], h0=LEVEL_AT[k][1])
           for k in ("tipliq", "wellliq", "tubeliq")},
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
                   ("NuVant EZstat Pro", (ex - 40, 60 - ed / 2, eh), (0.90, 0.40))]
    inst.step_labels = {i: [] for i in range(1, len(inst.actions))}
    inst.cam = (0.55, -1.5, 1.25)
    inst.framing = (0.80, 0.30)
    inst.notes = ["Deck, head and spot: DAL PR #180's copper plan (aeda51a), not yet built",
                  "P20 volumes and levels to scale; the measurement plot is illustrative"]
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
_C_HOLD = (_corr_w(560.0, -120.0, 300.0), _corr_w(318.0, 140.0, 40.0))
_CORR_TL = _corr_spot()
IL._CORR_TL = _CORR_TL          # the measurement overlay (instruments_lab._draw_corr_overlay) reads the timeline there
CAMS["instruments/cubxl_corrosion"] = {0: _C_WIDE, 2: _C_HOLD, 3: _C_HOLD, 4: _C_FILL, 5: _C_CELL, 6: _C_CELL,
                                       7: _C_FILL, 8: _C_TUBE, 10: _C_WIDE, 11: _C_OVER}
REGISTRY = {"cubxl_corrosion": cubxl_corrosion}
