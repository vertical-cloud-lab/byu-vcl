"""Sandbox objects for the PiPER arm (#199), following docs/sandbox-object-set.md: its Tier 1
core set (15 objects, with fill states), most of Tier 2, a few common extras, and the stations
and printed holders the objects move between.

Each builder returns a `Model` standing on z = 0 and centred in XY. Numbers come from the
vendor sheets and standards collected in ../README.md (dimension table), or from the object
list itself; anything marked "assumed" is a modelling choice. The charge cups, plugs, slug,
sleeve and crucible are not remodelled: they are the lab's own STEP files from #222 / PR #232
(inputs/atomizer-charge/), so a change there flows through.
"""
from __future__ import annotations

import math

import cadquery as cq

from common import HERE, Model, box, cyl, rbox, tube

SBS_W, SBS_D = 127.76, 85.48          # ANSI/SLAS 1-2004 footprint
SBS_R = 3.18                          # ANSI/SLAS 1-2004 outside corner radius


def _revolve(pts, z0: float = 0.0) -> cq.Workplane:
    """Solid of revolution about Z from an (r, z) outline."""
    return cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0)).translate((0, 0, z0))


def _at(shape, x=0.0, y=0.0, z=0.0, rz=0.0):
    s = shape.val() if isinstance(shape, cq.Workplane) else shape
    return s.moved(cq.Location(cq.Vector(x, y, z)) * cq.Location(cq.Vector(), cq.Vector(0, 0, 1), rz))


# --- vials -----------------------------------------------------------------------------------
# od, h: glass without cap; neck: thread OD (T) and finish height (H); cap OD, height, and how
# far its top stands above the glass lip. Finish dims from the GPI/SPI tables.
VIALS = {
    "20ml": dict(title="20 mL vial, 24-400 cap", od=28.0, h=57.0, wall=1.2, base=1.5,
                 neck_od=23.7, neck_h=10.2, cap_od=27.8, cap_h=11.4, cap_over=3.0, cap="pp_black"),
    "8ml":  dict(title="8 mL vial, 15-425 cap", od=16.75, h=60.0, wall=1.1, base=1.0,
                 neck_od=14.6, neck_h=8.0, cap_od=17.5, cap_h=11.0, cap_over=3.0, cap="pp_black"),
    "4ml":  dict(title="4 mL vial, 13-425 cap", od=14.75, h=45.0, wall=1.0, base=1.0,
                 neck_od=12.9, neck_h=7.7, cap_od=15.5, cap_h=11.0, cap_over=3.0, cap="pp_black"),
    "2ml":  dict(title="2 mL autosampler vial, 9 mm screw cap", od=11.6, h=32.0, wall=0.9, base=1.0,
                 neck_od=9.5, neck_h=5.0, cap_od=12.0, cap_h=6.5, cap_over=2.5, cap="pp_blue"),
}


def _vial_glass(v: dict) -> cq.Workplane:
    od, h, nh, nod, w = v["od"], v["h"], v["neck_h"], v["neck_od"], v["wall"]
    shoulder = min(4.0, od - nod)                     # shoulder height (assumed)
    top = h - nh
    outer = _revolve([(0, 0), (od / 2 - 1.0, 0), (od / 2, 1.0), (od / 2, top - shoulder), (nod / 2, top),
                      (nod / 2, h), (0, h)])
    inner = _revolve([(0, v["base"]), (od / 2 - w, v["base"]), (od / 2 - w, top - shoulder),
                      (nod / 2 - w * 1.3, top), (nod / 2 - w * 1.3, h + 1), (0, h + 1)])
    return outer.cut(inner)


def vial(size: str, fill: str | None = None, frac: float = 0.5) -> Model:
    """fill: None (empty), 'water' or 'powder'."""
    v = VIALS[size]
    state = fill or "empty"
    m = Model(f"vial_{size}_{state}", f"{v['title']}, {state}", source="modelled from specs")
    m.add("glass", _vial_glass(v), "glass")
    cap_top = v["h"] + v["cap_over"]
    m.add("cap", cyl(v["cap_od"], v["cap_h"], z=cap_top - v["cap_h"]).faces(">Z").edges().fillet(0.6)
          .cut(cyl(v["neck_od"] + 0.3, v["cap_h"] - 2.0, z=cap_top - v["cap_h"] - 0.01)), v["cap"])
    if fill:
        d = v["od"] - 2 * v["wall"] - 0.2
        fh = (v["h"] - v["neck_h"] - 4.0 - v["base"]) * frac
        if fill == "water":
            m.add("water", cyl(d, fh, z=v["base"] + 0.05), "liquid")
        else:   # a powder bed with a shallow heap (angle of repose, assumed)
            cone = min(d / 2 * math.tan(math.radians(20)), fh * 0.3)
            m.add("powder", _revolve([(0, 0), (d / 2, 0), (d / 2, fh - cone), (0, fh)], v["base"] + 0.05), "powder_al")
    m.notes = {"od_mm": v["od"], "height_with_cap_mm": round(cap_top, 2), "fill": state}
    return m


def headspace_vial() -> Model:
    m = Model("headspace_vial_10ml", "10 mL crimp-top headspace vial, 20 mm crimp", source="modelled from specs")
    od, h = 22.5, 46.0
    m.add("glass", _revolve([(0, 0), (od / 2 - 1, 0), (od / 2, 1), (od / 2, h - 7), (9.0, h - 4), (9.0, h - 2.5),
                             (10.0, h - 2.5), (10.0, h), (0, h)]).cut(
        _revolve([(0, 1.5), (od / 2 - 1.2, 1.5), (od / 2 - 1.2, h - 7), (7.5, h - 4), (7.5, h + 1), (0, h + 1)])), "glass")
    m.add("crimp cap", tube(20.6, 8.0, 6.0, z=h - 5.5).union(tube(20.6, 18.0, 5.0, z=h - 5.5)), "aluminium")
    return m


def beaker() -> Model:
    """100 mL Griffin low-form beaker, the doser's receiving vessel (object #5)."""
    m = Model("griffin_beaker_100ml", "100 mL Griffin beaker (low form)", source="modelled from specs (~50 x 70 mm)")
    od, h, w = 50.0, 70.0, 1.3
    body = cyl(od, h).cut(cyl(od - 2 * w, h, z=1.8))
    rim = tube(od + 2.4, od - 2 * w, 2.0, z=h - 2.0)
    spout = (cq.Workplane("XY").polyline([(-5, 0), (5, 0), (0, 7)]).close().extrude(3.0)
             .translate((0, od / 2 - 1.0, h - 3.0)))
    m.add("glass", body.union(rim).union(spout).cut(cyl(od - 2 * w, 5, z=h - 4)), "glass")
    return m


def media_bottle() -> Model:
    """100 mL GL45 media bottle with its blue cap: WetRobo's cap task (Tier 2)."""
    m = Model("media_bottle_gl45", "100 mL media bottle, GL45 cap (WetRobo cap task)", source="modelled from specs (assumed ~56 x 105 mm)")
    od, h = 56.0, 100.0
    glass = _revolve([(0, 0), (od / 2 - 2, 0), (od / 2, 2), (od / 2, 62), (24.0, 80), (22.5, 82), (22.5, h), (0, h)])
    glass = glass.cut(_revolve([(0, 2.5), (od / 2 - 2.2, 2.5), (od / 2 - 2.2, 62), (19.5, 80), (19.5, h + 1), (0, h + 1)]))
    m.add("glass", glass, "glass")
    m.add("water", cyl(od - 5, 45, z=2.6), "liquid")
    m.add("cap", cyl(54.0, 25.0, z=h - 12).faces(">Z").edges().fillet(1.5), "pp_blue")
    m.add("pouring ring", tube(54.0, 45.0, 8.0, z=h - 22), "pp_blue")
    return m


# --- SBS microplates --------------------------------------------------------------------------
# H: overall height; skirt: bottom flange height; a1x/a1y: A1 centre from the left and top edges;
# well: diameter (round) or side (square), depth from the top. From the vendor drawings via
# Opentrons' labware definitions.
PLATES = {
    "96_nest":  dict(title="96-well plate, 200 uL flat (NEST, the OT-2 plate in use)", H=14.3, skirt=2.5, rows=8,
                     cols=12, pitch=9.0, a1x=14.38, a1y=11.24, well=6.96, depth=10.9, square=False),
    "96_flat":  dict(title="96-well plate, flat (Corning 3370)", H=14.22, skirt=6.1, rows=8, cols=12, pitch=9.0,
                     a1x=14.3, a1y=11.2, well=6.86, depth=10.67, square=False),
    "384_flat": dict(title="384-well plate (Corning 3701)", H=14.22, skirt=6.1, rows=16, cols=24, pitch=4.5,
                     a1x=12.12, a1y=8.99, well=3.63, depth=11.43, square=True),
    "24_flat":  dict(title="24-well plate (Costar 3524)", H=19.69, skirt=13.7, rows=4, cols=6, pitch=19.3,
                     a1x=17.52, a1y=13.84, well=16.26, depth=17.4, square=False),
    "6_flat":   dict(title="6-well plate (Costar 3516)", H=20.27, skirt=13.7, rows=2, cols=3, pitch=39.12,
                     a1x=24.76, a1y=23.16, well=35.43, depth=17.4, square=False),
    "96_deep":  dict(title="96 deep-well plate, 2 mL (NEST 503001)", H=44.0, skirt=2.5, rows=8, cols=12, pitch=9.0,
                     a1x=14.38, a1y=11.24, well=8.2, depth=41.0, square=True),
}


def _sbs_body(H: float, skirt: float, inset: float = 1.5, top_r: float = 2.5) -> cq.Workplane:
    """Skirt at the full SBS footprint plus a slightly smaller body; A1 corner chamfered."""
    shape = rbox(SBS_W, SBS_D, skirt, SBS_R).union(rbox(SBS_W - 2 * inset, SBS_D - 2 * inset, H, top_r))
    notch = (cq.Workplane("XY").polyline([(0, 0), (5, 0), (0, -5)]).close().extrude(H + 1)
             .translate((-SBS_W / 2, SBS_D / 2, -0.5)))
    return shape.cut(notch)


def _grid(rows, cols, pitch, a1x, a1y, pitch_y=None):
    """Well centres with A1 at the back left: x to the right, y towards the back."""
    for r in range(rows):
        for c in range(cols):
            yield (-SBS_W / 2 + a1x + c * pitch, SBS_D / 2 - a1y - r * (pitch_y or pitch))


def plate(kind: str, sealed: bool = False, lid: bool = False) -> Model:
    p = PLATES[kind]
    suffix = "_sealed" if sealed else "_lid" if lid else ""
    m = Model(f"plate_{kind}{suffix}", p["title"] + (", sealed with water" if sealed else ", with lid" if lid else ""),
              source="modelled from specs")
    body = _sbs_body(p["H"], p["skirt"])
    body = body.cut(rbox(SBS_W - 6.0, SBS_D - 6.0, p["H"] - p["depth"] - 1.2, 1.5, z=-0.01))   # hollow underneath
    pts = list(_grid(p["rows"], p["cols"], p["pitch"], p["a1x"], p["a1y"]))
    wells = cq.Workplane("XY").pushPoints(pts)
    wells = (wells.rect(p["well"], p["well"]) if p["square"] else wells.circle(p["well"] / 2)).extrude(p["depth"])
    m.add("plate", body.cut(wells.translate((0, 0, p["H"] - p["depth"]))), "polystyrene")
    if sealed:
        water = cq.Workplane("XY").pushPoints(pts).circle(p["well"] / 2 - 0.05).extrude(p["depth"] * 0.55)
        m.add("water", water.translate((0, 0, p["H"] - p["depth"] + 0.05)), "liquid")
        m.add("seal film", rbox(SBS_W - 4.0, SBS_D - 4.0, 0.1, 2.0, z=p["H"]), "acrylic")
    if lid:
        m.add("lid", rbox(SBS_W + 1.6, SBS_D + 1.6, 9.0, SBS_R + 0.8).faces("<Z").shell(-1.0)
              .translate((0, 0, p["H"] - 5.5)), "polystyrene")
    m.notes = {"footprint_mm": [SBS_W, SBS_D], "height_mm": p["H"], "wells": len(pts)}
    return m


def tiprack(kind: str = "20ul") -> Model:
    """Opentrons 96 tip rack: a hollow body with a deck plate, the tips hanging in it."""
    s = {"300ul": dict(title="Opentrons 96 tip rack, 300 uL", total=64.49, tip_len=59.3, top_d=7.3),
         "20ul": dict(title="Opentrons 96 tip rack, 20 uL (the P20 rack in slot 2)", total=64.69, tip_len=39.2,
                      top_d=5.6)}[kind]
    m = Model(f"tiprack_{kind}", s["title"], source="modelled from specs (Opentrons labware definition)")
    collar = 9.0                                   # tip collar above the deck (assumed)
    deck_z = s["total"] - collar
    body = _sbs_body(deck_z, 5.0, inset=1.0, top_r=2.0).cut(rbox(SBS_W - 6, SBS_D - 6, deck_z - 2.0, 2.0, z=-0.01))
    pts = list(_grid(8, 12, 9.0, 14.38, 11.24))
    body = body.cut(cq.Workplane("XY").pushPoints(pts).circle(s["top_d"] / 2 - 0.4).extrude(3).translate((0, 0, deck_z - 2.5)))
    m.add("rack", body, "pp_black")
    tip = _revolve([(0, 0), (0.5, 0), (s["top_d"] / 2 - 1.2, s["tip_len"] - collar - 2),
                    (s["top_d"] / 2 - 0.3, s["tip_len"] - collar), (s["top_d"] / 2, s["tip_len"]), (0, s["tip_len"])]).val()
    z0 = s["total"] - s["tip_len"]
    m.add("tips", cq.Compound.makeCompound([_at(tip, x, y, z0) for x, y in pts]), "polypropylene")
    return m


# --- tubes ------------------------------------------------------------------------------------

def microtube() -> Model:
    m = Model("microtube_1_5ml", "1.5 mL microcentrifuge tube (Eppendorf Safe-Lock)", source="modelled from specs")
    L = 38.9
    body = _revolve([(0, 0), (2.8, 0), (5.35, 18.9), (5.4, L - 2), (6.55, L - 2), (6.55, L), (0, L)])
    body = body.cut(_revolve([(0, 1.0), (1.8, 1.0), (4.35, 18.9), (4.9, L + 1), (0, L + 1)]))
    lid = cyl(13.1, 2.1, z=L).union(box(-2, 6.0, L - 1.5, 2, 12.0, L + 1.0))
    m.add("tube", body, "polypropylene")
    m.add("lid", lid, "polypropylene")
    return m


def conical(size: str = "15ml") -> Model:
    # Falcon 352096 / 352070: length without cap, body OD, cone length, thread OD, cap OD x height
    s = {"15ml": dict(L=118.8, od=17.37, cone=22.48, thread=19.25, cap_od=22.98, cap_h=10.41, over=1.95, tip=3.2),
         "50ml": dict(L=114.55, od=29.72, cone=16.0, thread=31.5, cap_od=34.75, cap_h=13.21, over=1.25, tip=7.0)}[size]
    m = Model(f"conical_{size}", f"{size[:-2]} mL conical tube (Falcon)", source="modelled from specs")
    L, r = s["L"], s["od"] / 2
    body = _revolve([(0, 0), (s["tip"] / 2, 0), (r - 0.8, s["cone"]), (r, s["cone"] + 1), (r, L - 10),
                     (s["thread"] / 2, L - 9), (s["thread"] / 2, L), (0, L)])
    body = body.cut(_revolve([(0, 1.0), (s["tip"] / 2 - 0.8, 1.0), (r - 1.6, s["cone"] + 0.5), (r - 1.2, L + 1), (0, L + 1)]))
    if size == "50ml":        # the 50 mL tube stands on a skirt round its cone (assumed geometry)
        body = body.union(tube(s["od"] - 1, s["od"] - 3, s["cone"] - 1))
    m.add("tube", body, "polypropylene")
    m.add("cap", cyl(s["cap_od"], s["cap_h"], z=L + s["over"] - s["cap_h"]).faces(">Z").edges().fillet(1.0), "pp_blue")
    return m


def cuvette() -> Model:
    m = Model("cuvette", "Cuvette, PS, 12.5 x 12.5 x 45 mm (BRAND 759075D)", source="modelled from specs")
    m.add("cuvette", rbox(12.5, 12.5, 45.0, 0.5).cut(rbox(10.5, 10.5, 45.0, 0.3, z=1.0)), "polystyrene")
    return m


# --- SEM -------------------------------------------------------------------------------------------
STUBS = {"12.7": dict(title="SEM pin stub, 12.7 mm (Ted Pella 16111)", d=12.7, head_t=3.2, pin_d=3.15, pin_l=8.0),
         "25.4": dict(title="SEM pin stub, 25.4 mm", d=25.4, head_t=3.2, pin_d=3.15, pin_l=9.5)}


def sem_stub(size: str = "12.7", sample: bool = True) -> Model:
    s = STUBS[size]
    m = Model(f"sem_stub_{size.replace('.', '_')}", s["title"] + (", with sample" if sample else ""), source="modelled from specs")
    top = s["pin_l"] + s["head_t"]
    head = cyl(s["d"], s["head_t"], z=s["pin_l"]).faces(">Z").edges().chamfer(0.2)
    head = head.cut(tube(s["d"] + 1, s["d"] - 1.0, 1.0, z=top - 1.6 - 0.5))        # the tweezer groove
    m.add("stub", cyl(s["pin_d"], s["pin_l"]).faces("<Z").chamfer(0.4).union(head), "aluminium")
    if sample:
        m.add("carbon tab", cyl(s["d"] - 1.0, 0.15, z=top), "graphite")
        m.add("sample", rbox(s["d"] * 0.45, s["d"] * 0.35, 1.5, 0.4, z=top + 0.15), "aluminium")
    m.notes = {"head_d_mm": s["d"], "overall_h_mm": top}
    return m


def stub_box() -> Model:
    """Hinged clear box for 12.7 mm pin stubs: 120 x 84 x 36 mm, 24 seats at 18 x 16 mm."""
    m = Model("sem_stub_box", "SEM pin-stub storage box (Ted Pella / EMS class), 24 seats", source="modelled from specs")
    base = rbox(120, 84, 24, 3).faces(">Z").shell(-1.6)
    pts = [(-45 + c * 18, -24 + r * 16) for r in range(4) for c in range(6)]
    insert = rbox(116, 72, 10, 2, z=1.6).cut(cq.Workplane("XY").pushPoints(pts).circle(1.6).extrude(8).translate((0, 0, 3.6)))
    m.add("base", base, "acrylic")
    m.add("insert", insert, "pp_white")
    m.add("lid", rbox(120, 84, 12, 3).faces("<Z").shell(-1.6).translate((0, 0, 24.0)), "acrylic")
    stub = sem_stub("12.7")
    for i, (x, y) in enumerate(pts[:9]):
        for p in stub.parts:
            m.add(f"stub {i + 1} {p.name}", _at(p.shape, x, y, 11.6 - 8.0 + 0.01), p.material)
    return m


# --- atomizer charge: the lab's CAD from #222 / PR #232 ----------------------------------------------
CHARGE_DIR = HERE / "inputs" / "atomizer-charge"


def _step(name: str) -> cq.Shape:
    return cq.importers.importStep(str(CHARGE_DIR / f"{name}.step")).val()


def _standing(shape: cq.Shape) -> cq.Shape:
    bb = shape.BoundingBox()
    return shape.moved(cq.Location(cq.Vector(-bb.center.x, -bb.center.y, -bb.zmin)))


def charge_cup(charged: bool) -> Model:
    """P2, the bored 3/4 in 6063 cup (#199's "aluminium crucible"), empty or charged + plugged."""
    cup, plug = _standing(_step("std_cup")), _step("std_plug")
    H, pbb = cup.BoundingBox().zlen, plug.BoundingBox()
    m = Model(f"charge_cup_{'charged' if charged else 'empty'}",
              "Atomizer charge cup (P2), " + ("charged with powder, plug pressed in" if charged else "empty"),
              source="lab CAD (#222 STEP)")
    m.add("cup", cup, "aluminium")
    if charged:
        m.add("powder", cyl(12.6, 47.625 - pbb.zlen - 0.5, z=H - 47.625 + 0.2), "powder_al")
        m.add("plug", plug.moved(cq.Location(cq.Vector(-pbb.center.x, -pbb.center.y, H - pbb.zlen - 0.8 - pbb.zmin))), "aluminium")
    m.notes = {"mass_g": 32.0 if not charged else "40-45"}
    return m


def charge_part(name: str, key: str, title: str, material: str = "aluminium") -> Model:
    m = Model(key, title, source="lab CAD (#222 STEP)")
    m.add(name, _standing(_step(name)), material)
    return m


def crucible_replica() -> Model:
    """Station: the rePOWDER crucible, filling cone, sealing rod and rod adapter, scaled in PR #232."""
    sols = cq.importers.importStep(str(CHARGE_DIR / "crucible_context_4x_std_cup.step")).solids().vals()
    m = Model("crucible_replica", "Crucible replica station (rePOWDER 225 cm3, PR #232 model)", source="lab CAD (PR #232 STEP)")
    for i, (name, mat) in enumerate([("crucible", "graphite"), ("filling cone", "pp_white"), ("sealing rod", "graphite"),
                                     ("rod adapter and arm", "steel")]):
        m.add(name, sols[i], mat)
    bb = cq.Compound.makeCompound([p.shape for p in m.parts]).BoundingBox()
    m.parts = [type(p)(p.name, p.shape.moved(cq.Location(cq.Vector(0, 0, -bb.zmin))), p.material) for p in m.parts]
    return m


# --- printing, powder and mechanical-test objects -------------------------------------------------

def auger() -> Model:
    """Doser auger module: PLA tube 25 x 250 mm with a 48-tooth 50 mm gear, lying down (object #6)."""
    m = Model("auger_module", "Powder-doser auger module (PLA, 48T gear)", source="modelled from powder-doser#128/#131 dims")
    z = 25.0                                          # axis height when resting on the gear
    m.add("tube", cq.Workplane("YZ").circle(12.5).circle(10.5).extrude(250.0).translate((-125.0, 0, z)), "pla_white")
    teeth, r_out, r_root = 48, 25.0, 22.8
    pts = []
    for i in range(teeth):
        a = 2 * math.pi * i / teeth
        for da, r in ((-0.30, r_root), (-0.14, r_out), (0.14, r_out), (0.30, r_root)):
            ang = a + da * 2 * math.pi / teeth
            pts.append((r * math.cos(ang), r * math.sin(ang)))
    gear = cq.Workplane("YZ").polyline(pts).close().extrude(8.0).faces(">X").workplane().hole(25.0)
    m.add("gear", gear.translate((-125.0 - 8.0 + 250.0 - 12.0, 0, z)), "pla_orange")
    return m


def coupon(kind: str) -> Model:
    """Tensile coupons (object #13): the lab's LPBF dog-bone as a PETG replica, and ASTM D638 Type V."""
    if kind == "lpbf":
        L, W, t, gl, gw, tr = 100.0, 10.0, 6.0, 32.0, 6.0, 8.0
        m = Model("coupon_lpbf_dogbone", "Tensile coupon, PETG replica of the LPBF dog-bone (100 x 10 x 6)", source="modelled from #77")
        half = [(-L / 2, -W / 2), (-gl / 2 - tr, -W / 2), (-gl / 2, -gw / 2), (gl / 2, -gw / 2), (gl / 2 + tr, -W / 2),
                (L / 2, -W / 2), (L / 2, W / 2), (gl / 2 + tr, W / 2), (gl / 2, gw / 2), (-gl / 2, gw / 2),
                (-gl / 2 - tr, W / 2), (-L / 2, W / 2)]
        shape = cq.Workplane("XY").polyline(half).close().extrude(t)
        m.add("coupon", shape, "petg_teal")
    else:
        L0, W0, Wn, Ln, R, t = 63.5, 9.53, 3.18, 9.53, 12.7, 3.2      # ASTM D638 Type V
        dx = math.sqrt(R ** 2 - (R - (W0 - Wn) / 2) ** 2)
        m = Model("coupon_d638_type_v", "Tensile coupon, ASTM D638 Type V", source="ASTM D638 Type V")
        prof = (cq.Workplane("XY").moveTo(-L0 / 2, -W0 / 2).lineTo(-Ln / 2 - dx, -W0 / 2)
                .radiusArc((-Ln / 2, -Wn / 2), R).lineTo(Ln / 2, -Wn / 2).radiusArc((Ln / 2 + dx, -W0 / 2), R)
                .lineTo(L0 / 2, -W0 / 2).lineTo(L0 / 2, W0 / 2).lineTo(Ln / 2 + dx, W0 / 2)
                .radiusArc((Ln / 2, Wn / 2), R).lineTo(-Ln / 2, Wn / 2).radiusArc((-Ln / 2 - dx, W0 / 2), R)
                .lineTo(-L0 / 2, W0 / 2).close())
        m.add("coupon", prof.extrude(t), "petg_teal")
    return m


def weigh_boat() -> Model:
    m = Model("weigh_boat_41mm", "Anti-static weigh boat, 41 x 41 x 8 mm", source="modelled from specs")
    top, bot, h = 41.0, 29.0, 8.0
    solid = cq.Workplane("XY").rect(bot, bot).workplane(offset=h).rect(top, top).loft()
    m.add("boat", solid.faces(">Z").shell(-0.3), "pp_white")
    return m


def spoonula() -> Model:
    m = Model("spoonula", "Spoonula / micro-spatula, stainless, 180 mm", source="modelled from specs (assumed)")
    handle = box(-60, -3.0, 0, 60, 3.0, 1.5)
    blade = cq.Workplane("XY").polyline([(60, -3), (70, -4.5), (88, -4.5), (90, 0), (88, 4.5), (70, 4.5), (60, 3)]).close().extrude(0.8)
    bowl = cq.Workplane("XY").ellipse(11, 6.5).extrude(3.0).translate((-78, 0, 0)).cut(
        cq.Workplane("XY").ellipse(10.2, 5.7).extrude(3.0).translate((-78, 0, 0.6)))
    neck = box(-67.5, -2.2, 0.5, -60, 2.2, 1.5)
    m.add("spoonula", handle.union(blade).union(bowl).union(neck), "steel")
    return m


def al_weigh_dish() -> Model:
    m = Model("al_weigh_dish_57mm", "Aluminium weighing dish, 57 mm, with tab", source="modelled from specs")
    d = cq.Workplane("XY").circle(23.5).workplane(offset=15.0).circle(28.5).loft().cut(
        cq.Workplane("XY").circle(23.35).workplane(offset=15.0).circle(28.35).loft().translate((0, 0, 0.15)))
    rim = tube(63.5, 57.0, 0.3, z=14.7)
    tab = box(28.0, -7.5, 14.7, 40.0, 7.5, 15.0)
    m.add("dish", d.union(rim).union(tab), "aluminium")
    return m


def alumina_crucible() -> Model:
    m = Model("alumina_crucible_10ml", "Alumina crucible, 10 mL, with lid (22 x 33 mm)", source="modelled from specs (CoorsTek/AdValue)")
    m.add("crucible", cyl(22.0, 33.0).cut(cyl(18.3, 31.0, z=2.1)), "pp_white")
    m.add("lid", cyl(22.0, 2.0, z=33.0).union(cyl(17.7, 1.4, z=31.6)), "pp_white")
    return m


def dsc_pan() -> Model:
    m = Model("dsc_pan_tzero", "TA Tzero Al DSC pan + lid (901683.901 + 901671.901)", source="modelled from specs")
    pan = cq.Workplane("XY").circle(2.7).workplane(offset=2.3).circle(3.1).loft()
    pan = pan.union(tube(7.3, 6.2, 0.3, z=2.3)).cut(cq.Workplane("XY").circle(2.5).workplane(offset=2.4).circle(2.95).loft().translate((0, 0, 0.3)))
    m.add("pan", pan, "aluminium")
    m.add("lid", cyl(5.5, 0.1, x=9.0).union(cyl(3.0, 0.3, x=9.0)), "aluminium")
    return m


def mini_build_plate() -> Model:
    m = Model("mini_lpbf_build_plate", "Mini LPBF build plate, 26 x 25 x 1 mm", source="#61")
    m.add("plate", box(-13, -12.5, 0, 13, 12.5, 1.0), "steel")
    return m


def furnace_stack() -> Model:
    """Induction-furnace sample stack, shown exploded: cup, disc, lid, window."""
    m = Model("furnace_sample_stack", "Induction-furnace sample stack (graphite cup, alumina disc, lid, sapphire window)",
              source="custom-induction-furnace SI")
    m.add("graphite cup", cyl(20.3, 6.5).cut(cyl(14.4, 5.0, z=1.5)), "graphite")
    m.add("alumina disc", cyl(14.0, 1.0, z=12.0), "pp_white")
    m.add("stepped lid", cyl(20.3, 1.5, z=18.0).union(cyl(14.2, 1.0, z=17.0)).cut(cyl(8.0, 3, z=16.9)), "graphite")
    m.add("sapphire window", cyl(9.5, 0.5, z=24.0), "glass")
    return m


def xrf_cup() -> Model:
    m = Model("xrf_cup", "XRF sample cup (Chemplex 1330), 30.7 x 22.9 mm", source="modelled from specs")
    m.add("cell", tube(30.7, 27.0, 22.9), "polypropylene")
    m.add("snap ring", tube(32.5, 30.5, 5.0, z=17.9), "polypropylene")
    m.add("film", cyl(28.0, 0.05, z=22.9), "acrylic")
    return m


def si_plate() -> Model:
    m = Model("si_zero_bg_plate", "Zero-background Si plate, 32 x 2 mm (use a printed dummy first)", source="modelled from specs")
    m.add("plate", cyl(32.0, 2.0), "graphite")
    return m


def mount() -> Model:
    m = Model("metallographic_mount_32mm", "Metallographic mount, 1.25 in, with AlSi10Mg sample", source="modelled from specs")
    m.add("mount", cyl(31.75, 20.0).faces("<Z").chamfer(1.0).faces(">Z").chamfer(0.5).cut(rbox(12.0, 10.0, 6.0, 1.0, z=14.01)), "resin")
    m.add("sample", rbox(12.0, 10.0, 6.0, 1.0, z=14.0), "aluminium")
    return m


def coin_cell() -> Model:
    m = Model("coin_cell_cr2032", "CR2032 coin cell, 20 x 3.2 mm", source="IEC 60086")
    m.add("can", cyl(20.0, 2.6).faces(">Z").edges().fillet(0.3), "steel")
    m.add("cap", cyl(16.5, 0.6, z=2.6), "steel")
    return m


def colour_sensor() -> Model:
    m = Model("wireless_colour_sensor", "Wireless colour sensor (AS7341 + Pico W), ~40 x 60 x 84 mm", source="#197 (assumed shape)")
    m.add("housing", rbox(40.0, 60.0, 84.0, 5.0), "pla_white")
    m.add("sensor window", rbox(14.0, 14.0, 0.5, 1.0, z=-0.4), "acrylic")
    m.add("tip socket", cyl(9.0, 20.0, z=84.0), "pla_grey")
    return m


def tensegrity() -> Model:
    """T3 tensegrity prism: 3 PLA struts, 9 TPU tendons (two triangles and three verticals)."""
    m = Model("tensegrity_t3_prism", "Tensegrity T3 prism (PLA struts, TPU tendons), ~80 x 80 x 100 mm", source="tensegrity-optimization (assumed geometry)")
    R, H = 40.0, 100.0
    bot = [cq.Vector(R * math.cos(math.radians(120 * i)), R * math.sin(math.radians(120 * i)), 4.0) for i in range(3)]
    top = [cq.Vector(R * math.cos(math.radians(120 * i + 150)), R * math.sin(math.radians(120 * i + 150)), H) for i in range(3)]

    def rod(a: cq.Vector, b: cq.Vector, d: float) -> cq.Solid:
        return cq.Solid.makeCylinder(d / 2, (b - a).Length, a, (b - a).normalized())
    struts = [rod(bot[i], top[i], 5.0) for i in range(3)]
    tendons = [rod(bot[i], bot[(i + 1) % 3], 1.6) for i in range(3)] + [rod(top[i], top[(i + 1) % 3], 1.6) for i in range(3)] + \
              [rod(bot[i], top[(i - 1) % 3], 1.6) for i in range(3)]
    m.add("struts", cq.Compound.makeCompound(struts), "pla_orange")
    m.add("tendons", cq.Compound.makeCompound(tendons), "printer_black")
    m.add("nodes", cq.Compound.makeCompound([cq.Solid.makeSphere(4.0, p) for p in bot + top]), "printer_black")
    return m


def petri() -> Model:
    m = Model("petri_90mm", "90 mm Petri dish with lid (WetRobo lid task)", source="modelled from specs")
    m.add("base", cyl(87.91, 14.4).faces(">Z").shell(-0.9), "polystyrene")
    m.add("lid", cyl(92.4, 8.76).faces("<Z").shell(-0.9).translate((0, 0, 16.1 - 8.76)), "polystyrene")
    return m


def slide() -> Model:
    m = Model("glass_slide", "Glass microscope slide, 75 x 25 x 1 mm", source="modelled from specs")
    m.add("slide", rbox(75.0, 25.0, 1.0, 0.5), "glass")
    return m


# --- stations and printed holders (our designs, PETG, SBS footprint) ----------------------------------
# Rules from the object list: 1-2 mm lead-in chamfers, >= 1 mm diametral clearance, a 20 mm
# AprilTag on a sidewall, raised plate nests narrower than the SBS footprint.
TAG = 22.0


def _holder_block(H: float) -> cq.Workplane:
    blk = rbox(SBS_W, SBS_D, H, SBS_R).edges(">Z").chamfer(0.8)
    if H > TAG + 2:
        blk = blk.cut(box(-TAG / 2, -SBS_D / 2 - 0.01, (H - TAG) / 2, TAG / 2, -SBS_D / 2 + 0.6, (H + TAG) / 2))
    return blk


def _pockets(blk, pts, d, depth, H, chamfer=1.5):
    """Round pockets with a 45 deg lead-in chamfer (a 30 deg cone is kinder, 45 deg is what prints clean)."""
    for x, y in pts:
        blk = blk.cut(cyl(d, depth, x=x, y=y, z=H - depth)).cut(
            cq.Workplane("XY").circle(d / 2).workplane(offset=chamfer).circle(d / 2 + chamfer).loft().translate((x, y, H - chamfer)))
    return blk


def holder_vials(size: str = "20ml", cols: int = 3, rows: int = 2, pitch: float = 40.0, depth: float = 20.0) -> Model:
    """Vial rack for a parallel gripper: pitch leaves room for fingers, and slots between pockets
    let them close below the vial's shoulder."""
    v = VIALS[size]
    H = max(depth + 4.0, 26.0)
    m = Model(f"holder_vial_{size}", f"Printed SBS rack, {cols * rows} x {size[:-2]} mL vials, finger slots", source="our design (parametric)")
    pts = [(-(cols - 1) * pitch / 2 + c * pitch, -(rows - 1) * pitch / 2 + r * pitch) for r in range(rows) for c in range(cols)]
    blk = _pockets(_holder_block(H), pts, v["od"] + 1.2, depth, H)
    for x, y in pts:
        blk = blk.cut(box(x - v["od"] / 2 - 9, y - 6, H - 12, x + v["od"] / 2 + 9, y + 6, H + 1))
    m.add("holder", blk, "petg_teal")
    for i, (x, y) in enumerate(pts):
        vm = vial(size, fill=("water" if i % 3 == 0 else "powder" if i % 3 == 1 else None), frac=0.45)
        for p in vm.parts:
            m.add(f"vial {i + 1} {p.name}", _at(p.shape, x, y, H - depth), p.material)
    return m


def holder_stubs(cols: int = 5, rows: int = 3, pitch: float = 22.0) -> Model:
    """Stub tray with tapered pin bores, so a pin 0.5 mm off-axis still self-seats."""
    H = 16.0
    m = Model("holder_sem_stubs", f"Printed SBS stub tray, {cols * rows} seats, tapered bores", source="our design (parametric)")
    pts = [(-(cols - 1) * pitch / 2 + c * pitch, -(rows - 1) * pitch / 2 + r * pitch) for r in range(rows) for c in range(cols)]
    blk = _holder_block(H)
    for x, y in pts:
        blk = blk.cut(cyl(3.4, 9, x=x, y=y, z=H - 8.99)).cut(
            cq.Workplane("XY").circle(1.7).workplane(offset=2.0).circle(3.7).loft().translate((x, y, H - 2.0)))
    m.add("holder", blk, "petg_teal")
    stub = sem_stub("12.7")
    for i, (x, y) in enumerate(pts[:11]):
        for p in stub.parts:
            m.add(f"stub {i + 1} {p.name}", _at(p.shape, x, y, H - 8.0), p.material)
    return m


def holder_charge(n: int = 3, pitch: float = 30.0) -> Model:
    """Charge station: cup pockets, plug pockets, and a socket for the steel press sleeve."""
    H = 30.0
    m = Model("holder_charge", f"Printed SBS charge station: {n} cups, {n} plugs, press-sleeve socket", source="our design (parametric)")
    xs = [-48.0 + i * pitch for i in range(n)]
    blk = _pockets(_holder_block(H), [(x, 18) for x in xs], 19.05 + 1.2, 22, H)
    blk = _pockets(blk, [(x, -22) for x in xs], 12.7 + 1.0, 5, H, chamfer=1.0)
    blk = _pockets(blk, [(44, -2)], 31.75 + 1.2, 26, H)
    m.add("holder", blk, "petg_teal")
    charged = charge_cup(True)
    cup = charge_cup(False).parts[0].shape
    plug = _standing(_step("std_plug"))
    for i, x in enumerate(xs):
        if i < n - 1:
            for p in charged.parts:
                m.add(f"cup {i + 1} {p.name}", _at(p.shape, x, 18, H - 22), p.material)
        else:
            m.add(f"cup {i + 1}", _at(cup, x, 18, H - 22), "aluminium")
            m.add(f"plug {i + 1}", _at(plug, x, -22, H - 5), "aluminium")
    m.add("press sleeve", _at(_standing(_step("support_sleeve")), 44, -2, H - 26), "steel")
    return m


def plate_nest() -> Model:
    """OT-2 slot replica: a 128.0 x 86.0 mm pocket of corner posts round a raised pedestal
    narrower than the plate, so stepped fingers reach under the plate's top edge."""
    m = Model("ot2_slot_nest", "Printed OT-2 slot replica: 128.0 x 86.0 pocket, raised nest", source="our design (parametric)")
    base = rbox(160.0, 118.0, 5.0, 4.0)
    ped = rbox(96.0, 56.0, 30.0, 3.0, z=5.0)
    # corner posts: 6 mm square, 40 mm tall, their inner faces on the 128.0 x 86.0 pocket
    posts = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = sx * (64.0 + 3.0), sy * (43.0 + 3.0)
            p = box(px - 3, py - 3, 5, px + 3, py + 3, 45)
            posts = p if posts is None else posts.union(p)
    m.add("nest", base.union(ped).union(posts), "petg_teal")
    pl = plate("96_nest")
    for p in pl.parts:
        m.add(f"plate {p.name}", _at(p.shape, 0, 0, 35.0), p.material)
    return m


def tube_rack_6() -> Model:
    """The AC 6-tube rack already used on the OT-2: 127.76 x 85.48 x 61 mm, 20 x 58 mm wells."""
    m = Model("tube_rack_6", "6-tube rack (AC, OT-2) with 15 mL tubes", source="#64 dims")
    H = 61.0
    pts = list(_grid(2, 3, 35.0, 28.88, 25.24))
    blk = rbox(SBS_W, SBS_D, H, SBS_R).cut(cq.Workplane("XY").pushPoints(pts).circle(10.0).extrude(58.0).translate((0, 0, H - 58.0)))
    m.add("rack", blk, "pla_white")
    t = conical("15ml")
    for i, (x, y) in enumerate(pts[:4]):
        for p in t.parts:
            m.add(f"tube {i + 1} {p.name}", _at(p.shape, x, y, H - 58.0 + 1.0), p.material)
    return m


def balance() -> Model:
    """HR-100A-sized dummy with a breeze break and a drop hole (station). Outer dims assumed."""
    m = Model("balance_hr100a_dummy", "A&D HR-100A balance dummy with breeze break and drop hole", source="assumed dims")
    m.add("body", rbox(200.0, 290.0, 85.0, 8.0), "printer_white")
    m.add("display", box(-70, -145.5, 30, 70, -144.9, 70), "screen")
    brk = rbox(170.0, 170.0, 160.0, 4.0, y=40.0, z=85.0).faces("<Z").shell(-3.0)
    brk = brk.cut(cyl(20.0, 10.0, x=0, y=40.0, z=240.0))                       # drop hole in the top
    brk = brk.cut(box(-60, -46, 85, 60, -40, 85 + 76.2))                        # 3 in front opening
    m.add("breeze break", brk, "acrylic")
    m.add("pan", cyl(90.0, 3.0, y=40.0, z=95.0), "steel")
    m.add("beaker", _at(beaker().parts[0].shape, 0, 40.0, 98.0), "glass")
    return m


def arbor_press() -> Model:
    """A 1-ton arbor press (station for the plug press-fit). Rough, assumed dims."""
    m = Model("arbor_press_1t", "Arbor press, 1 t (press-fit station)", source="assumed dims")
    m.add("base", box(-90, -60, 0, 90, 70, 35), "paint_grey")
    m.add("column", box(-35, 40, 35, 35, 90, 330), "paint_grey")
    m.add("head", box(-50, -40, 250, 50, 90, 340), "paint_grey")
    m.add("ram", cyl(25.0, 200.0, y=-15, z=150), "steel")
    m.add("pinion shaft", cyl(30.0, 110.0, z=0).rotate((0, 0, 0), (0, 1, 0), 90).translate((-55, 25, 300)), "steel")
    m.add("handle", cyl(12.0, 280.0, z=0).rotate((0, 0, 0), (1, 0, 0), -35).translate((55, 25, 300)), "steel")
    m.add("sleeve", _at(_standing(_step("support_sleeve")), 0, -15, 35), "steel")
    return m


def catalog() -> dict[str, Model]:
    """Every sandbox object, keyed by export name, grouped as in docs/sandbox-object-set.md."""
    return {m.key: m for m in CATALOG_BUILDERS()}


def CATALOG_BUILDERS():
    tier1 = [
        charge_cup(False), charge_cup(True), charge_part("std_plug", "charge_plug", "Vented press-fit plug (P3)"),
        charge_part("solid_slug", "solid_slug", "Solid slug (P1), the reference object"),
        charge_part("support_sleeve", "press_sleeve", "Press sleeve (F1), 1018 steel", "steel"),
        beaker(), auger(), sem_stub("12.7"),
        vial("20ml"), vial("20ml", "powder", 0.4), vial("20ml", "water", 0.5), vial("2ml"),
        conical("15ml"), plate("96_nest"), plate("96_nest", sealed=True), tiprack("20ul"),
        coupon("lpbf"), coupon("d638"), weigh_boat(), spoonula(),
    ]
    tier2 = [
        media_bottle(), petri(), headspace_vial(), alumina_crucible(), dsc_pan(), al_weigh_dish(), mini_build_plate(),
        furnace_stack(), cuvette(), xrf_cup(), si_plate(), mount(), colour_sensor(), tensegrity(), coin_cell(),
    ]
    extras = [
        vial("8ml"), vial("4ml"), vial("2ml", "water", 0.6), plate("96_flat", lid=True), plate("384_flat"),
        plate("24_flat"), plate("6_flat"), plate("96_deep"), tiprack("300ul"), microtube(), conical("50ml"),
        sem_stub("25.4"), stub_box(), slide(),
    ]
    stations = [
        holder_charge(), holder_vials("20ml"), holder_stubs(), plate_nest(), tube_rack_6(), crucible_replica(),
        balance(), arbor_press(),
    ]
    for group, items in (("tier1", tier1), ("tier2", tier2), ("extra", extras), ("station", stations)):
        for m in items:
            m.notes["group"] = group
            yield m
