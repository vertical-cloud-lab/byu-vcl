"""Lab equipment: rough parametric models where no vendor CAD exists, loaders where it does.

Rough models (A1 mini, H2D, CubXL, drop tower, atomizer) get their envelope from a published
spec and their layout from a drawing or photo; the proportions in between are read off those
references and are approximate. They are for layout, reach and collision planning, not for
fitting parts. Vendor models (OT-2, PiPER) are downloaded by vendor.py and used as-is.

Frames: x to the right and y away from the viewer when facing the machine's front; z up from
the floor or bench it stands on; origin at the centre of the footprint.
"""
from __future__ import annotations

import math

import cadquery as cq

from common import Model, box, cyl, hose, rbox, tube


# --- Bambu Lab A1 mini ------------------------------------------------------------------------
# Envelope: 347 x 315 x 365 mm, build volume 180^3 (Bambu Lab spec page). Layout and
# proportions: Bambu's "A1 mini + AMS lite" space drawing (358 mm printer space width), read at
# 1.615 px/mm: Z column on the right, X arm cantilevered to the left, screen on the column base.
A1 = dict(W=347.0, D=315.0, H=365.0, bed=180.0, bed_top=80.5, base_h=51.0, col_w=52.0, col_d=42.0,
          arm_z=235.0)


def a1_mini(gantry_z: float | None = None, bed_y: float = 0.0) -> Model:
    p = A1
    m = Model("bambu_a1_mini", "Bambu Lab A1 mini", source="modelled from Bambu's spec and outline drawing")
    x0 = -p["W"] / 2                                    # left edge of the printer space
    X = lambda mm: x0 + mm                              # noqa: E731, drawing x (mm from the left edge)
    # base: Y rail under the bed, column foot, and a cross-member joining them
    m.add("base rail", rbox(82, p["D"] - 20, p["base_h"], 8, x=X(152), y=0), "printer_white")
    m.add("column base", rbox(75, 170, p["base_h"], 8, x=X(278.5), y=35), "printer_white")
    m.add("base cross", box(X(185), -40, 0, X(245), 40, 28), "printer_grey")
    m.add("screen", box(X(252), -50.6, 10, X(305), -49.8, 42), "screen")    # on the column base's front face
    # bed: heatbed with the PEI sheet, sliding along y
    bw = 191.0
    m.add("bed carriage", box(X(152) - 38, bed_y - 70, p["base_h"], X(152) + 38, bed_y + 70, p["bed_top"] - 12), "printer_grey")
    m.add("heatbed", rbox(bw, bw, 6.0, 6, x=X(153.5), y=bed_y, z=p["bed_top"] - 7), "aluminium")
    m.add("build plate", rbox(183, 183, 1.0, 4, x=X(153.5), y=bed_y, z=p["bed_top"] - 1.0), "pei")
    # Z column and its top cap with the spool holder stub
    col_y = 45.0                                        # the column sits towards the rear
    m.add("z column", rbox(p["col_w"], p["col_d"], p["H"] - p["base_h"] - 6, 4, x=X(279), y=col_y, z=p["base_h"]), "printer_white")
    m.add("column cap", rbox(p["col_w"] + 4, p["col_d"] + 4, 6, 3, x=X(279), y=col_y, z=p["H"] - 6), "printer_grey")
    m.add("spool holder", box(X(273), col_y + p["col_d"] / 2, p["H"] - 60, X(285), col_y + p["col_d"] / 2 + 70, p["H"] - 48), "printer_grey")
    # X arm + Z carriage + X motor box, at gantry height
    az = gantry_z if gantry_z is not None else p["arm_z"]
    arm_y0, arm_y1 = col_y - p["col_d"] / 2 - 26, col_y - p["col_d"] / 2 - 2
    m.add("x arm", box(X(3), arm_y0, az, X(262), arm_y1, az + 21), "aluminium")
    m.add("z carriage", box(X(260), col_y - p["col_d"] / 2 - 8, az - 22, X(299), col_y + p["col_d"] / 2 + 8, az + 45), "printer_white")
    m.add("x motor box", rbox(62, 62, 62, 5, x=X(329), y=col_y, z=az - 12), "printer_white")
    m.add("arm end cap", box(X(0), arm_y0 - 4, az - 55, X(20), arm_y1, az + 26), "printer_grey")
    # toolhead hanging in front of the arm; nozzle 150 mm up in the drawing, set by gantry_z here
    th_x = X(155)
    m.add("toolhead", rbox(65, 52, 106, 6, x=th_x, y=arm_y0 - 26, z=az - 66), "printer_white")
    m.add("hotend", cyl(10, 12, x=th_x, y=arm_y0 - 26, z=az - 78).union(
        cq.Workplane("XY").circle(0.4).workplane(offset=6).circle(4).loft().translate((th_x, arm_y0 - 26, az - 84))), "brass")
    m.add("extruder", rbox(28, 30, 40, 4, x=th_x, y=arm_y0 - 26, z=az + 40), "printer_grey")
    # PTFE feed tube: an arc from the spool holder up and over into the extruder (drawing: 483 mm high)
    path = cq.Workplane("XZ").spline([(X(300), p["H"] - 35), (X(260), 470), (X(200), 478), (th_x, az + 110), (th_x, az + 80)],
                                     includeCurrent=False).val()
    try:
        prof = cq.Workplane(cq.Plane(origin=path.startPoint(), normal=path.tangentAt(0))).circle(2.0)
        ptfe = prof.sweep(cq.Workplane().add(path)).val()
        m.add("ptfe tube", ptfe.moved(cq.Location(cq.Vector(0, arm_y0 - 26, 0))), "pp_white")
    except Exception:   # the tube is cosmetic; skip it if the sweep fails
        pass
    m.notes = {"envelope_mm": [p["W"], p["D"], p["H"]], "build_volume_mm": [180, 180, 180],
               "build_plate_mm": [183, 183], "bed_top_above_bench_mm": p["bed_top"]}
    return m


# --- Bambu Lab H2D ----------------------------------------------------------------------------
# Envelope 492 x 514 x 626 mm, 31 kg; build volume 325 x 320 x 325 mm with one nozzle, 350 mm wide
# across both (bambulab.com spec page, fetched through the CubXL Pi).
H2D = dict(W=492.0, D=514.0, H=626.0, bed_w=350.0, bed_d=320.0)


def h2d(bed_z: float = 260.0) -> Model:
    p = H2D
    W, D, H = p["W"], p["D"], p["H"]
    m = Model("bambu_h2d", "Bambu Lab H2D", source="modelled from Bambu's spec")
    shell = rbox(W, D, H, 18).edges(">Z or <Z").fillet(8)
    cavity = rbox(W - 36, D - 36, H - 70, 10, z=40)
    door = box(-W / 2 + 22, -D / 2 - 1, 48, W / 2 - 70, -D / 2 + 20, H - 40)
    lid = rbox(W - 60, D - 60, 40, 10, z=H - 25)
    m.add("frame", shell.cut(cavity).cut(door).cut(lid), "printer_grey")
    m.add("door glass", box(-W / 2 + 22, -D / 2 + 2, 48, W / 2 - 70, -D / 2 + 7, H - 40), "tinted")
    m.add("lid glass", rbox(W - 64, D - 64, 5, 10, z=H - 6), "tinted")
    m.add("screen", box(W / 2 - 62, -D / 2 - 0.5, H - 180, W / 2 - 18, -D / 2 + 1, H - 90), "screen")
    m.add("front strip", box(W / 2 - 68, -D / 2 - 0.2, 48, W / 2 - 12, -D / 2 + 1, H - 200), "printer_black")
    m.add("bed", rbox(p["bed_w"] + 10, p["bed_d"] + 10, 8, 6, y=5, z=bed_z), "aluminium")
    m.add("build plate", rbox(p["bed_w"] + 4, p["bed_d"] + 4, 1.0, 4, y=5, z=bed_z + 8), "pei")
    for sx in (-1, 1):
        m.add(f"z screw {'LR'[sx > 0]}", cyl(12, H - 110, x=sx * (W / 2 - 40), y=D / 2 - 45, z=45), "steel")
    gz = H - 110
    m.add("x gantry", box(-W / 2 + 24, -20, gz, W / 2 - 24, 20, gz + 30), "aluminium")
    for sx in (-1, 1):
        m.add(f"y rail {'LR'[sx > 0]}", box(sx * (W / 2 - 22) - 6, -D / 2 + 30, gz + 5, sx * (W / 2 - 22) + 6, D / 2 - 25, gz + 25), "aluminium")
    m.add("toolhead", rbox(110, 70, 110, 8, x=15, y=-50, z=gz - 70), "printer_black")
    m.add("nozzles", cyl(8, 10, x=-10, y=-50, z=gz - 80).union(cyl(8, 10, x=40, y=-50, z=gz - 80)), "brass")
    m.notes = {"envelope_mm": [W, D, H], "build_volume_single_nozzle_mm": [325, 320, 325]}
    return m


# --- AMAZEMET rePowder induction module ----------------------------------------------------------
# Envelope: operational footprint 1000 x 800 x 1600 mm, ~300 kg on four feet at 714 x 600 mm
# (O&MM p. 42, Facility Guide p. 7, via the repowder-reference zip). Layout from the delivered
# unit in its crate (#124) and AMAZEMET's render: a blue cabinet; Blue Power "aus500" furnace
# head at the top left; a slanted stainless atomization chamber with the ultrasonic unit in its
# door; a cone down to the airlock powder container; the melting control panel top right.
# Superseded once it lands: PR #255 is building a more accurate one from the installation and
# training videos, so this rough model is only kept for the room layout until then.
REPOWDER = dict(W=1000.0, D=800.0, H=1600.0, feet_x=714.0, feet_y=600.0)


def atomizer() -> Model:
    p = REPOWDER
    m = Model("amazemet_repowder", "AMAZEMET rePowder induction module (atomizer)",
              source="modelled from AMAZEMET/Indutherm specs and photos (repowder-reference zip, #124)")
    cw, cd, cz0, cz1 = 860.0, 480.0, 110.0, 1590.0          # blue cabinet (proportions from the photos)
    y0 = -p["D"] / 2 + 300.0                                 # cabinet front face; the process parts sit in front
    m.add("cabinet", box(-cw / 2, y0, cz0, cw / 2, y0 + cd, cz1).edges("|Z").fillet(6), "paint_blue")
    for sx in (-1, 1):                                       # U-frame feet under the cabinet
        fy0 = y0 + cd / 2 - 60                              # feet centred under cabinet + chamber (assumed)
        m.add(f"foot rail {'LR'[sx > 0]}", box(sx * p["feet_x"] / 2 - 30, fy0 - p["feet_y"] / 2 - 20, 55,
                                              sx * p["feet_x"] / 2 + 30, fy0 + p["feet_y"] / 2 + 20, cz0), "paint_blue")
        for sy in (-1, 1):
            m.add(f"foot {sx:+d}{sy:+d}", cyl(50, 55, x=sx * p["feet_x"] / 2, y=fy0 + sy * p["feet_y"] / 2), "steel")
    # melting control panel (recessed, top right) and the main switch below it
    m.add("control panel", box(150, y0 - 6, 1180, 400, y0 + 0.01, 1480), "printer_white")
    m.add("controller display", box(190, y0 - 8, 1380, 330, y0 - 5.9, 1450), "screen")
    m.add("main switch", cyl(70, 25, x=320, y=0, z=0).rotate((0, 0, 0), (1, 0, 0), 90).translate((0, y0, 1080)), "paint_red")
    # HMI (15.6 in Weintek) on the right side of the module
    m.add("hmi", box(cw / 2, y0 + 80, 1150, cw / 2 + 45, y0 + 80 + 400, 1420), "printer_black")
    m.add("hmi screen", box(cw / 2 + 45, y0 + 100, 1170, cw / 2 + 46, y0 + 460, 1400), "screen")
    # furnace head: Blue Power aus500, a stainless drum with a faceted top and a small display
    fx, fy = -230.0, y0 - 170.0
    m.add("furnace head", cyl(290, 270, x=fx, y=fy, z=1060).union(
        cq.Workplane("XY").circle(145).workplane(offset=70).circle(85).loft().translate((fx, fy, 1330))), "aluminium")
    m.add("furnace display", box(fx - 40, fy - 60, 1395, fx + 40, fy + 10, 1410), "screen")
    m.add("furnace mount", box(fx - 150, y0 - 60, 1040, fx + 150, y0, 1330), "aluminium")
    # sealing collar under the head and the neck into the chamber
    m.add("collar", tube(190, 90, 70, x=fx, y=fy - 10, z=960), "printer_black")
    m.add("neck", cyl(150, 120, x=fx, y=fy, z=900), "steel")
    # atomization chamber: slanted stainless housing (front profile from the photos), 330 mm deep
    prof = (cq.Workplane("XZ").polyline([(-300, 1000), (230, 1000), (230, 560), (80, 560), (-300, 800)]).close()
            .extrude(-330.0))
    m.add("atomization chamber", prof.translate((0, y0 - 330.0, 0)).edges("|Y").fillet(20), "steel")
    # ultrasonic unit in the chamber door: a tube angled down to the left
    us = cq.Workplane("XY").circle(45).extrude(300).rotate((0, 0, 0), (0, 1, 0), -120).translate((-300, y0 - 165, 830))
    m.add("ultrasonic unit", us, "pp_white")
    # chute cone to the airlock powder container
    cx, cy = 150.0, y0 - 165.0
    m.add("clamp ring", cyl(250, 30, x=cx, y=cy, z=530), "steel")
    m.add("chute cone", cq.Workplane("XY").circle(35).workplane(offset=150).circle(110).loft().translate((cx, cy, 380)), "steel")
    m.add("airlock valve", cyl(110, 50, x=cx, y=cy, z=330), "steel")
    m.add("powder container", cyl(90, 150, x=cx, y=cy, z=180), "steel")
    m.notes = {"envelope_mm": [p["W"], p["D"], p["H"]], "feet_spacing_mm": [p["feet_x"], p["feet_y"]], "mass_kg": 300}
    return m


# --- CubXL -----------------------------------------------------------------------------------------
# The lab's liquid-handling gantry is built on a Genmitsu PROVerXL 4030 V2 frame (the badge in
# the #133/#200 photos): 740 x 605 x 488 mm, 400 x 300 x 110 mm travel (SainSmart spec). The
# clear slotted deck, tool plate with pipette and capper/decapper, and vial rack are from photos.
CUBXL = dict(W=740.0, D=605.0, H=488.0, travel=(400.0, 300.0, 110.0))


def cubxl(x: float = 0.45, y: float = 0.5, z: float = 0.6) -> Model:
    """x, y, z: carriage position as a fraction of travel."""
    p = CUBXL
    W, D, H = p["W"], p["D"], p["H"]
    m = Model("cubxl", "CubXL liquid-handling gantry (Genmitsu PROVerXL 4030 V2 frame)",
              source="modelled from the frame's spec and lab photos (#133, #200)")
    ex = 40.0                                              # 40 mm extrusions (assumed)
    for sx in (-1, 1):                                     # Y rails with blue end plates
        m.add(f"y rail {'LR'[sx > 0]}", box(sx * (W / 2 - 70) - ex / 2, -D / 2 + 15, 30, sx * (W / 2 - 70) + ex / 2, D / 2 - 15, 30 + 2 * ex), "extrusion")
        for sy in (-1, 1):
            m.add(f"end plate {sx:+d}{sy:+d}", box(sx * (W / 2 - 70) - 45, sy * (D / 2 - 7.5) - 7.5, 0, sx * (W / 2 - 70) + 45, sy * (D / 2 - 7.5) + 7.5, 130), "paint_blue")
    for sy in (-1, 1):                                     # front and back cross members
        m.add(f"cross {'FB'[sy > 0]}", box(-W / 2 + 70, sy * (D / 2 - 35) - 20, 10, W / 2 - 70, sy * (D / 2 - 35) + 20, 50), "extrusion")
    m.add("deck", rbox(W - 200, D - 110, 10, 4, z=70), "acrylic")
    gy = -D / 2 + 150 + y * p["travel"][1]                 # gantry y position
    for sx in (-1, 1):
        m.add(f"gantry upright {'LR'[sx > 0]}", box(sx * (W / 2 - 45) - 12, gy - 60, 30, sx * (W / 2 - 45) + 12, gy + 60, H - 10), "paint_blue")
    m.add("gantry beam", box(-W / 2 + 30, gy - 10, H - 150, W / 2 - 30, gy + 70, H - 60), "extrusion")
    m.add("cable chain", box(-W / 2 + 30, gy + 70, H - 60, W / 2 - 150, gy + 110, H - 10), "printer_black")
    cx = -p["travel"][0] / 2 + x * p["travel"][0]
    m.add("z carriage", box(cx - 60, gy - 40, H - 260, cx + 60, gy - 10, H + 10), "aluminium")
    m.add("tool plate", box(cx - 110, gy - 55, H - 330, cx + 110, gy - 40, H - 40), "printer_black")
    zt = 100 + z * p["travel"][2]
    m.add("pipette", cyl(34, 170, x=cx - 50, y=gy - 80, z=zt).union(cyl(8, 40, x=cx - 50, y=gy - 80, z=zt - 40)), "printer_black")
    m.add("capper", cyl(40, 150, x=cx + 55, y=gy - 80, z=zt + 20), "printer_grey")
    m.add("controller", rbox(160, 90, 40, 6, x=cx, y=gy - 30, z=H + 10), "pcb")
    for i in range(6):                                     # six-vial rack (Ben's deck file)
        m.add(f"vial {i + 1}", cyl(28, 55, x=-60 + i * 32, y=-60, z=80), "glass")
        m.add(f"vial {i + 1} cap", cyl(25, 14, x=-60 + i * 32, y=-60, z=135), "pp_black")
    m.add("vial rack", box(-85, -85, 80, 125, -35, 110), "pla_white")
    m.add("tip rack", rbox(127.76, 85.48, 60, 3, x=150, y=90, z=80), "pp_black")
    m.add("control box", rbox(260, 200, 90, 8, x=-W / 2 - 170, y=-D / 2 + 130), "printer_black")
    m.add("e-stop", cyl(40, 20, x=-W / 2 - 110, y=-D / 2 + 90, z=90), "paint_red")
    m.notes = {"envelope_mm": [W, D, H], "travel_mm": list(p["travel"]), "frame": "Genmitsu PROVerXL 4030 V2"}
    return m


# --- Lansmont M23 drop tower -------------------------------------------------------------------
# In Jeff Hill's SMASH Lab (CB 152A), not CB154 (#90). Official: envelope 21 x 24 in (53 x 61 cm),
# 96-120 in (244-305 cm) tall, table 9.06 x 9.06 in (23 x 23 cm) (Lansmont M23 data sheet, #27/#28).
# The frame inside that envelope is read off the lab's photos (sources/drop_tower.json): two ~25 mm
# chrome rods ~280 mm apart, one rear column, a latch head under the chain hoist, ~2.8 m as set up.
M23 = dict(W=533.0, D=610.0, H=2800.0, table=230.0, rod_d=25.0, rod_gap=280.0)


def drop_tower(carriage_z: float = 1500.0) -> Model:
    p = M23
    W, D, H = p["W"], p["D"], p["H"]
    m = Model("lansmont_m23_drop_tower", "Lansmont M23 shock test system (drop tower)",
              source="Lansmont's data sheet (envelope, table) and lab photos (frame)")
    m.add("base slab", box(-240, -270, 0, 240, 270, 90), "steel")
    m.add("seismic block", box(-140, -160, 90, 140, 160, 430), "printer_black")
    m.add("mat stack", box(-115, -115, 430, 115, 115, 470), "pp_white")
    for sx in (-1, 1):
        m.add(f"guide rod {'LR'[sx > 0]}", cyl(p["rod_d"], H - 330 - 90, x=sx * p["rod_gap"] / 2, y=0, z=90), "steel")
    m.add("rear column", box(-40, 200, 0, 40, 280, H - 250), "printer_black")
    m.add("crosshead", box(-W / 2 + 60, -60, H - 330, W / 2 - 60, 280, H - 250), "paint_grey")
    m.add("chain hoist", cyl(160, 220, x=0, y=60, z=H - 250), "paint_blue")     # near the ceiling
    m.add("latch head", box(-110, -70, carriage_z + 140, 110, 70, carriage_z + 230), "paint_grey")
    for sx in (-1, 1):                               # the table's rod housings with the brake pads
        m.add(f"rod housing {'LR'[sx > 0]}", cyl(60, 140, x=sx * p["rod_gap"] / 2, y=0, z=carriage_z), "aluminium")
    table = box(-p["table"] / 2, -p["table"] / 2, carriage_z, p["table"] / 2, p["table"] / 2, carriage_z + 140)
    holes = cq.Workplane("XY").pushPoints([(-76.2 + 38.1 * i, -76.2 + 38.1 * j) for i in range(5) for j in range(5)]) \
        .circle(6.35).extrude(12).translate((0, 0, carriage_z + 128.01))
    m.add("drop table", table.cut(holes), "aluminium")
    m.add("hoist chain", cyl(10, H - 330 - (carriage_z + 230), x=0, y=0, z=carriage_z + 230), "steel")
    m.notes = {"envelope_mm": [W, D, H], "table_mm": [p["table"], p["table"]], "standard_drop_in": 60,
               "location": "CB 152A (SMASH Lab), not CB154"}
    return m


# --- Labconco Protector controlled-atmosphere glove box on its stand ----------------------------
# The cheap pick from PR #78 (proposed 2026-07-20, agreed the same day): a used $2,999 unit in
# Alabama. Its data plate reads catalog 50701-00: a Protector with a type 304 stainless liner,
# automatic pressure control and 115 V, built July 2001, with an AtmosPure 51218-00 purifier
# already fitted. The liner, window, ports and transfer chamber follow Labconco's drawing. The
# 38 in height is the seller's (the current model is 45.7 in), and the control column, the rear
# purifier and the bubbler are scaled from the listing photos (sources/glovebox.json).
# Inches, as on the drawing.
LABCONCO = dict(body_w=41.5, base_d=30.0, h=38.0, cab_w=16.3, cab_h=31.0, overall_w=63.5,
                win_w=36.0, win_h=27.7, win_z=3.6, slope_deg=10.0,
                int_d_floor=28.0, int_h_front=32.0, int_h_rear=28.1, int_floor=1.6,
                port_id=8.0, port_od=11.0, port_x=(12.3, 29.3), port_z=9.3,
                ante=(11.0, 13.0, 20.0), ante_floor=5.1, ante_y=(9.0, 22.0),
                stand_w=60.0, stand_d=30.0, stand_h=34.0, stand_top=1.125, caster=5.0)
IN = 25.4


def glovebox() -> Model:
    p = {k: (tuple(v * IN for v in val) if isinstance(val, tuple) else val * IN) for k, val in LABCONCO.items()
         if k != "slope_deg"}
    a = math.radians(LABCONCO["slope_deg"])
    m = Model("labconco_glovebox", "Labconco Protector glove box (cat. 50701), stainless, on its stand",
              source="Labconco's drawing and 2002 manual; the listing's photos and 38 in height (PR #78)")
    # stand (Labconco 5062000): phenolic top, two pedestal uprights on T-feet, lower shelf, casters
    sw, sd, S = p["stand_w"], p["stand_d"], p["stand_h"]
    c = p["caster"]
    m.add("stand top", box(-sw / 2, -sd / 2, S - p["stand_top"], sw / 2, sd / 2, S), "benchtop")
    for sx in (-1, 1):
        x = sx * (sw / 2 - 120)
        m.add(f"stand upright {'LR'[sx > 0]}", box(x - 40, -40, c + 40, x + 40, 40, S - p["stand_top"]), "printer_black")
        m.add(f"stand foot {'LR'[sx > 0]}", box(x - 40, -sd / 2 + 30, c, x + 40, sd / 2 - 30, c + 40), "printer_black")
        for sy in (-1, 1):
            m.add(f"caster {sx:+d}{sy:+d}", cyl(c * 0.8, c, x=x, y=sy * (sd / 2 - 70)), "printer_black")
    m.add("stand shelf", box(-sw / 2 + 180, -sd / 2 + 60, 330, sw / 2 - 180, sd / 2 - 60, 350), "printer_black")
    m.add("stand beam", box(-sw / 2 + 120, -30, 520, sw / 2 - 120, 30, 580), "printer_black")
    # main body: side profile with the window plane leaning back 10 deg, a lamp facade above it
    x0 = -sw / 2                                          # left end flush with the stand; the right end overhangs
    y0 = -p["base_d"] / 2                                 # base front
    bw, H, wz = p["body_w"], p["h"], p["win_z"]
    wy1, wz1 = y0 + p["win_h"] * math.sin(a), S + wz + p["win_h"] * math.cos(a)     # window top edge
    prof = [(y0, S), (-y0, S), (-y0, S + H), (wy1, S + H), (wy1, wz1), (y0, S + wz)]
    body = cq.Workplane("YZ").polyline(prof).close().extrude(bw).translate((x0, 0, 0))
    # interior: 35.5 W, 28.0 deep at the floor, 32.0 tall at the front falling to 28.1 at the rear
    iw = 35.5 * IN
    fz = S + p["int_floor"]
    iy0 = y0 + (p["int_floor"] - wz) * math.tan(a) + 12.0          # inner face of the window at the floor
    ih, ihr = p["int_h_front"], p["int_h_rear"]
    inner = [(iy0, fz), (iy0 + p["int_d_floor"], fz), (iy0 + p["int_d_floor"], fz + ihr),
             (iy0 + ih * math.tan(a), fz + ih)]
    cav = cq.Workplane("YZ").polyline(inner).close().extrude(iw).translate((x0 + (bw - iw) / 2, 0, 0))
    # the window: a 36.0 x 27.7 opening through the sloped face, glazed with 3/8 in laminated glass
    nrm = (0, -math.cos(a), math.sin(a))                         # outward normal of the window plane
    wc = (x0 + bw / 2, (y0 + wy1) / 2, (S + wz + wz1) / 2)
    wpl = cq.Plane(origin=wc, xDir=(1, 0, 0), normal=nrm)
    opening = cq.Workplane(wpl).rect(p["win_w"], p["win_h"]).extrude(-80.0)
    m.add("body", body.cut(cav).cut(opening), "anthracite")
    m.add("liner floor", box(x0 + (bw - iw) / 2, iy0, fz - 2.7, x0 + (bw + iw) / 2, iy0 + p["int_d_floor"], fz), "steel")
    # ports: 8 in ID in the glass, centres 12.3 and 29.3 in from the left edge, 9.3 in up
    pts = []
    for px in p["port_x"]:
        up = (p["port_z"] - wz) / math.cos(a)                    # distance up the window plane from its bottom edge
        pts.append((x0 + px - wc[0], up - p["win_h"] / 2))
    glass = cq.Workplane(wpl).rect(p["win_w"], p["win_h"]).extrude(-9.5)
    glass = glass.cut(cq.Workplane(wpl).pushPoints(pts).circle(p["port_id"] / 2).extrude(-30, both=True))
    m.add("window", glass, "glass")
    m.add("window frame", cq.Workplane(wpl).rect(p["win_w"] + 60, p["win_h"] + 50).rect(p["win_w"], p["win_h"]).extrude(8),
          "printer_black")
    for i, (u, v) in enumerate(pts):
        ring = cq.Workplane(wpl).center(u, v).circle(p["port_od"] / 2).circle(p["port_id"] / 2).extrude(25.4)
        m.add(f"glove port {i + 1}", ring, "aluminium")
        glove = cq.Workplane(wpl).center(u, v).circle(p["port_id"] / 2 - 6).extrude(-380)
        m.add(f"glove {i + 1}", glove, "pp_black")
    m.add("badge", box(x0 + bw / 2 - 180, wy1 - 0.6, wz1 + 60, x0 + bw / 2 + 180, wy1 + 0.01, wz1 + 110), "aluminium")
    # control column on the right end, with the transfer chamber through it and the AtmosPure controller on top
    cx0, cx1 = x0 + bw, x0 + bw + p["cab_w"]
    m.add("control column", box(cx0, y0, S, cx1, -y0, S + p["cab_h"]), "anthracite")
    m.add("atmospure control", box(cx0, y0, S + p["cab_h"], cx1, y0 + 330, S + p["cab_h"] + 100), "printer_black")
    for i, (z0, z1, mat) in enumerate(((0.80, 0.95, "printer_white"), (0.60, 0.77, "printer_black"),
                                        (0.40, 0.57, "printer_white"), (0.20, 0.37, "printer_black"))):
        m.add(f"control panel {i + 1}", box(cx0 + 20, y0 - 3, S + z0 * p["cab_h"], cx1 - 20, y0 + 0.01, S + z1 * p["cab_h"]), mat)
    m.add("box pressure gauge", cyl(90, 20, x=0, y=0, z=0).rotate((0, 0, 0), (1, 0, 0), 90)
          .translate(((cx0 + cx1) / 2 - 90, y0 - 3, S + 0.47 * p["cab_h"])), "printer_white")
    m.add("chamber vacuum gauge", cyl(90, 20, x=0, y=0, z=0).rotate((0, 0, 0), (1, 0, 0), 90)
          .translate(((cx0 + cx1) / 2 + 90, y0 - 3, S + 0.47 * p["cab_h"])), "printer_white")
    aw, ah, al = p["ante"]
    ay0, az0 = y0 + p["ante_y"][0], S + p["ante_floor"]
    ax1 = x0 + p["overall_w"] - 70.0                      # outer door face; door hardware takes the rest of the 63.5 in
    tube_ = box(ax1 - al - 30, ay0 - 12, az0 - 12, ax1, ay0 + aw + 12, az0 + ah + 12)
    tube_ = tube_.cut(box(ax1 - al - 31, ay0, az0, ax1 + 1, ay0 + aw, az0 + ah))
    m.add("transfer chamber", tube_, "steel")
    m.add("outer door", box(ax1, ay0 - 30, az0 - 30, ax1 + 16, ay0 + aw + 30, az0 + ah + 30), "steel")
    m.add("door pivot arms", box(ax1 + 16, ay0 - 30, az0 + ah + 10, ax1 + 70, ay0 + aw + 30, az0 + ah + 40), "steel")
    m.add("door latch", box(ax1 + 16, ay0 + aw / 2 - 40, az0 - 10, ax1 + 45, ay0 + aw / 2 + 40, az0 + 20), "printer_black")
    # rear: purifier enclosure (rear left) and the oil bubbler (mid rear)
    m.add("purifier enclosure", box(x0 + 60, -y0, S + 120, x0 + 340, -y0 + 140, S + 680), "printer_black")
    m.add("bubbler", box(x0 + bw / 2 - 125, -y0, S + 250, x0 + bw / 2 + 125, -y0 + 100, S + 850), "printer_black")
    m.add("vacuum pump", rbox(380, 200, 250, 10, x=-sw / 2 + 420, y=0, z=350), "paint_blue")
    m.notes = {"envelope_mm": [round(p["overall_w"], 1), round(p["base_d"], 1), round(S + H, 1)],
               "interior_mm": [round(iw), round(p["int_d_floor"]), round(ih)],
               "transfer_chamber_inside_mm": [round(aw), round(ah), round(al)],
               "glove_port_centre_height_mm": round(S + p["port_z"]),
               "floor_centre_mm": [round(x0 + bw / 2, 1), round(iy0 + p["int_d_floor"] / 2, 1), round(fz, 1)],
               "status": "a used listing (PR #78); not bought",
               "fit_note": "Inside 902 x 711 x 813 mm. The HR-100A (198 x 262 x 176 mm) passes the 279 x 330 mm "
                           "transfer chamber"}
    return m


# --- MSE PRO 378L two-port acrylic glove box with airlock (#30) ----------------------------------
# The alternative to the Labconco: MSE Supplies GB0068899 (the GB0010 of #30, same specs), made by
# Changsha MITR (their MT008-B). MSE's data: 900 W x 600 D x 700 H mm (outside, per MITR's table) of
# 10 mm PMMA, a 240 mm airlock, a 400 x 400 mm side door, two ball valves on the chamber and two
# on the airlock, one gauge, one socket inside, 68 kg, no stand. MSE's listing photo shows a plain
# box with a vertical front; port positions, the airlock's height, both doors' hardware and the
# fittings are scaled from it (camera fitted to the known 900 x 700 face, about +-25 mm). MITR's own
# manual shows a sloped front and a 300 mm round side door instead, so ask MSE which one ships
# (sources/glovebox.json, mse_pro_acrylic_airlock).
MSE = dict(W=900.0, D=600.0, H=700.0, t=10.0, port_od=150.0, port_id=125.0, port_x=210.0, port_z=305.0,
           ante=(450.0, 695.0, 240.0, 55.0, 285.0), ante_door=200.0, door=400.0, door_z=335.0, door_plate=470.0)


def mse_glovebox() -> Model:
    p = MSE
    W, D, H, t = p["W"], p["D"], p["H"], p["t"]
    m = Model("mse_pro_glovebox", "MSE PRO 378L two-port acrylic glove box with airlock (GB0068899), candidate",
              source="MSE's product data and listing photo; MITR's manual (sources/glovebox.json)")

    def along(axis, d, length, at):                       # a cylinder of diameter d along +x/-x/+y/-y from `at`
        c = cq.Workplane("XY").circle(d / 2).extrude(abs(length))
        rot = {"x": ((0, 1, 0), 90), "y": ((1, 0, 0), -90)}[axis]
        c = c.rotate((0, 0, 0), rot[0], rot[1] if length > 0 else -rot[1])
        return c.translate(at)

    shell = box(-W / 2, -D / 2, 0, W / 2, D / 2, H).cut(box(-W / 2 + t, -D / 2 + t, t, W / 2 - t, D / 2 - t, H - t))
    ports = [(-p["port_x"], p["port_z"]), (p["port_x"], p["port_z"])]
    for x, z in ports:
        shell = shell.cut(along("y", p["port_id"], 3 * t, (x, -D / 2 - t, z)))
    ax0, ax1, aw, az0, az1 = p["ante"]
    azc = (az0 + az1) / 2
    shell = shell.cut(along("x", p["ante_door"], 3 * t, (W / 2 - 2 * t, 0, azc)))
    dz, dw = p["door_z"], p["door"]
    shell = shell.cut(box(-W / 2 - 1, -dw / 2, dz - dw / 2, -W / 2 + t + 1, dw / 2, dz + dw / 2))
    m.add("chamber", shell, "acrylic")
    # glove ports: a ring with a flange on the front wall, the glove held on by a red O-ring
    for i, (x, z) in enumerate(ports):
        m.add(f"glove port {i + 1}", along("y", p["port_od"], -35.0, (x, -D / 2, z)).cut(along("y", p["port_id"], -40.0, (x, -D / 2 + 1, z)))
              .union(along("y", 180.0, -6.0, (x, -D / 2, z)).cut(along("y", p["port_id"], -10.0, (x, -D / 2 + 1, z)))), "printer_white")
        m.add(f"glove o-ring {i + 1}", along("y", p["port_od"] + 6, -6.0, (x, -D / 2 - 22, z)).cut(
            along("y", p["port_od"] - 1, -8.0, (x, -D / 2 - 21, z))), "paint_red")
        m.add(f"glove {i + 1}", along("y", p["port_id"] - 10, 320.0, (x, -D / 2 + t, z)), "latex")
    # airlock on the right end: a 240 mm acrylic box, round doors at both ends; the inner one is
    # clamped by a crossbar inside the chamber, the outer by a swing bar and a T-handle screw
    lock = box(ax0, -aw / 2, az0, ax1, aw / 2, az1).cut(box(ax0 - 1, -aw / 2 + t, az0 + t, ax1 - t, aw / 2 - t, az1 - t))
    lock = lock.cut(along("x", p["ante_door"], 2 * t, (ax1 - 1.5 * t, 0, azc)))
    m.add("airlock", lock, "acrylic")
    m.add("airlock outer door", along("x", 225.0, 15.0, (ax1, 0, azc)), "acrylic")
    m.add("airlock swing bar", box(ax1 + 15, -135, azc - 10, ax1 + 27, 135, azc + 10), "steel")
    m.add("airlock t-handle screw", along("x", 12.0, 60.0, (ax1 + 27, 0, azc)), "steel")
    m.add("airlock t-handle", along("y", 10.0, 80.0, (ax1 + 87, -40, azc)), "steel")
    m.add("airlock inner door", along("x", 225.0, -15.0, (W / 2 - t, 0, azc)), "acrylic")
    m.add("airlock inner crossbar", box(W / 2 - t - 27, -135, azc - 10, W / 2 - t - 15, 135, azc + 10), "steel")
    # side door on the left end: a removable plate on a white gasket, held by four toggle latches
    dp = p["door_plate"]
    m.add("side door gasket", box(-W / 2 - 4, -dp / 2, dz - dp / 2, -W / 2, dp / 2, dz + dp / 2)
          .cut(box(-W / 2 - 5, -dw / 2, dz - dw / 2, -W / 2 + 1, dw / 2, dz + dw / 2)), "printer_white")
    m.add("side door", box(-W / 2 - 4 - t, -dp / 2, dz - dp / 2, -W / 2 - 4, dp / 2, dz + dp / 2), "acrylic")
    for sy in (-1, 1):
        for z in (180.0, 460.0):
            m.add(f"side door latch {sy:+d} {z:.0f}", box(-W / 2 - 22, sy * (dp / 2 - 30) - 12, z - 15, -W / 2 - 14, sy * (dp / 2 - 30) + 12, z + 15),
                  "steel")
    # fittings: gauge and red vacuum valve on the airlock, black ball valves low on the airlock
    # front and the left end, the inlet valve high on the right end, the socket strip inside
    m.add("vacuum gauge stem", cyl(14, 50, x=510, y=-80, z=az1), "steel")
    m.add("vacuum gauge", along("y", 60.0, -25.0, (510, -80 + 12, 360)), "printer_white")
    m.add("vacuum valve", cyl(22, 40, x=600, y=0, z=az1), "steel")
    m.add("vacuum valve handle", box(570, -6, az1 + 40, 630, 6, az1 + 48), "paint_red")
    m.add("airlock ball valve", along("y", 22.0, -35.0, (500, -aw / 2, 100)), "steel")
    m.add("airlock ball valve handle", box(470, -aw / 2 - 43, 108, 530, -aw / 2 - 35, 116), "printer_black")
    m.add("exhaust valve", along("x", 22.0, -40.0, (-W / 2, -250, 40)), "steel")
    m.add("exhaust valve handle", box(-W / 2 - 48, -280, 48, -W / 2 - 40, -220, 56), "printer_black")
    m.add("inlet valve", along("x", 22.0, 35.0, (W / 2, -250, 650)), "steel")
    m.add("inlet valve handle", box(W / 2 + 35, -280, 658, W / 2 + 43, -220, 666), "printer_black")
    m.add("socket strip", box(-W / 2 + t + 20, D / 2 - t - 45, t, -W / 2 + t + 220, D / 2 - t - 5, t + 35), "printer_white")
    for i in range(4):
        m.add(f"socket {i + 1}", box(-W / 2 + t + 40 + 45 * i, D / 2 - t - 35, t + 35, -W / 2 + t + 70 + 45 * i, D / 2 - t - 15, t + 36),
              "pp_blue")
    m.add("power cable", hose([(-W / 2 + t + 220, D / 2 - t - 25, t + 17), (-120, D / 2 - t - 25, t + 17), (-120, D / 2 - 30, 110),
                               (-120, D / 2 + 60, 110), (-120, D / 2 + 140, 5)], 8), "printer_black")
    bb = cq.Compound.makeCompound([q.shape for q in m.parts]).BoundingBox()
    m.notes = {"envelope_mm": [round(bb.xlen), round(bb.ylen), round(bb.zlen)], "chamber_outside_mm": [W, D, H],
               "interior_mm": [W - 2 * t, D - 2 * t, H - 2 * t], "airlock_mm": [ax1 - ax0, aw, az1 - az0],
               "side_door_mm": [dw, dw], "floor_centre_mm": [0.0, 0.0, t], "status": "candidate, not bought",
               "open_question": "MSE's listing: a 400 x 400 mm square side door and a vertical front. MITR's manual for "
                                "the same model: a 300 mm round door and a sloped front. Ask MSE which ships.",
               "fit_note": "Inside 880 x 580 x 680 mm. The HR-100A (198 x 262 x 176 mm) can't pass the 240 mm airlock, "
                           "so it goes in through the 400 mm side door."}
    return m


# --- Aconity3D AconityMIDI (metal laser powder-bed fusion) ---------------------------------------
# Not bought: the candidate metal printer. Envelope 2450 x 1500 x 2320 mm, 1450 kg, build space
# 170 mm dia. x 200 mm (Aconity's configurator data behind aconity3d.com, 2026; the 2018/2022 sheets
# give 2170 x 1590 x 2340 for the older design). The layout is read off Aconity's own configurator
# layers and front photos (CMU's at 4.036 mm/px, Aconity's 2026 cover) and Amazemet's photos of
# theirs (sources/aconity_midi.json, "corrections_2026-10-03"):
#   - the optics hang off a Rexroth Z module bolted to a crossbar between two posts, with no top
#     slab: the module moves an L-shaped scanner tray, which has a beam opening;
#   - a stepped beam tube runs from under that opening to a window flange in the chamber lid;
#   - each yellow fibre leaves a vertical cable chain on the tray, bends 180 deg and drops into the
#     collimator on its scan head; the fibres reach the lasers in the control cabinet as a bundle;
#   - the filter is a cyclone (jar, cone, drum) with a cartridge filter on top, on four legs that
#     run up to the drum's rim, piped into the base cabinet's left wall.
# x and z come from the photos; every depth (y) is inferred from how the parts fit, since no side
# view is published. Blocks are in the photo frame: x from the left edge, y back from the front
# face, z up.
ACONITY = dict(W=2450.0, D=1500.0, H=2320.0, build_d=170.0, build_h=200.0, feet=100.0)


def aconity_midi() -> Model:
    p = ACONITY
    W, D, H = p["W"], p["D"], p["H"]
    m = Model("aconity_midi", "Aconity3D AconityMIDI (metal LPBF), candidate",
              source="Aconity's spec (envelope, build space), configurator layers and front photos (layout); depths inferred")

    def B(x0, x1, y0, y1, z0, z1):                         # photo frame -> centred frame, front at -D/2
        return box(x0 - W / 2, y0 - D / 2, z0, x1 - W / 2, y1 - D / 2, z1)

    def P(x, y, z):
        return (x - W / 2, y - D / 2, z)

    def C(d, x, y, z0, z1):                                # vertical cylinder in the photo frame
        return cyl(d, z1 - z0, x=x - W / 2, y=y - D / 2, z=z0)

    def levelling_feet(xs, ys, top):
        for x in xs:
            for y in ys:
                m.add(f"levelling foot {x:.0f}-{y:.0f}", C(60, x, y, 0, 25), "steel")
                m.add(f"foot ring {x:.0f}-{y:.0f}", C(46, x, y, 25, 35), "paint_red")
                m.add(f"foot stem {x:.0f}-{y:.0f}", C(20, x, y, 35, top), "steel")

    f = p["feet"]
    # filter unit, left: a cyclone (jar, cone, drum) with a cartridge filter on top, on four legs
    # that run from castors up to the drum's rim; it stands back beside the base cabinet
    fx, fy = 210.0, 750.0
    m.add("filter jar", C(90, fx, fy, 230, 330), "steel")
    m.add("filter cone", cq.Workplane("XY").circle(45).workplane(offset=170).circle(195).loft()
          .translate(P(fx, fy, 330)), "printer_black")
    m.add("filter drum", C(390, fx, fy, 500, 850), "printer_black")
    m.add("filter drum lid", C(410, fx, fy, 850, 862), "printer_black")
    m.add("filter neck", C(80, fx, fy, 862, 940), "steel")
    m.add("cartridge filter", C(230, fx, fy, 940, 1200), "printer_black")
    m.add("valve block", C(70, fx, fy, 1200, 1330), "steel")
    m.add("valve elbow", hose([P(fx, fy, 1300), P(fx + 70, fy, 1300)], 50), "steel")
    m.add("valve actuator", B(fx - 35, fx + 35, fy - 35, fy + 35, 1330, 1420), "pp_blue")
    for i, (dx, dy) in enumerate(((-1, 0), (1, 0), (0, -1), (0, 1))):
        lx, ly = fx + dx * 209.0, fy + dy * 209.0
        m.add(f"filter leg {i + 1}", C(28, lx, ly, 62, 862), "printer_black")
        m.add(f"filter castor fork {i + 1}", B(lx - 18, lx + 18, ly - 18, ly + 18, 40, 62), "steel")
        m.add(f"filter castor {i + 1}", cyl(40, 16).rotate((0, 0, 0), (0, 1, 0), 90).translate(P(lx - 8, ly, 20)), "printer_black")
    # into the machine: a stainless pipe from the drum's side to the base cabinet's left wall, a
    # clear hose from the valve block to the wall's top, and a thin air line from the actuator
    m.add("cyclone inlet pipe", hose([P(fx + 190, fy, 790), P(470.5, fy, 790)], 60), "steel")
    m.add("filter hose", hose([P(fx + 70, fy, 1300), P(fx + 170, fy, 1300), P(430, fy - 60, 1150), P(470.5, fy - 80, 960)], 38),
          "acrylic")
    m.add("air line", hose([P(fx + 35, fy - 20, 1390), P(fx + 120, fy - 40, 1390), P(440, fy - 150, 1080), P(470.5, fy - 160, 1040)], 8),
          "pp_blue")
    # base cabinet: one door hinged on the left, handle on the right
    m.add("base cabinet", B(470, 1390, 0, 1200, f, 990).edges("|Z").fillet(8), "anthracite")
    levelling_feet((510.0, 1350.0), (40.0, 1160.0), f)
    m.add("base door split", B(488, 491, -1, 0.01, f + 20, 970), "printer_black")
    m.add("base door handle", B(1243, 1257, -25, 0.01, 500, 580), "aluminium")
    # process chamber on the base, with its viewport, bar handle, clamp levers and carry handle
    m.add("process chamber", B(634, 1243, 250, 950, 990, 1300).edges("|Y").fillet(10), "anthracite")
    m.add("chamber viewport", B(855, 1000, 244, 250.01, 1120, 1180), "tinted")
    m.add("chamber handle", hose([P(870, 250, 1017), P(870, 225, 1017), P(1030, 225, 1017), P(1030, 250, 1017)], 16), "printer_black")
    for i, z in enumerate((1060.0, 1230.0)):
        m.add(f"chamber clamp {i + 1}", B(645, 690, 225, 250.01, z - 12, z + 12), "steel")
    arc = [P(770 + 310 * k / 10, 330, 1300 + 35 * math.sin(math.pi * k / 10)) for k in range(11)]
    m.add("chamber carry handle", hose(arc, 18), "printer_black")
    # beam path: a stepped tube from the chamber lid's window flange up to the tray's opening
    bx, by = 935.0, 600.0
    m.add("beam tube flange", C(230, bx, by, 1300, 1335), "anthracite")
    m.add("beam tube", C(200, bx, by, 1335, 1420), "anthracite")
    m.add("beam tube ring", C(290, bx, by, 1420, 1490), "anthracite")
    # optics frame: two posts on the base cabinet (no top slab), a crossbar with gussets, and the
    # Rexroth Z module bolted to its front
    for i, x0 in enumerate((540.0, 1290.0)):
        m.add(f"portal post {i + 1}", B(x0, x0 + 60, 900, 960, 990, 1905), "printer_black")
        m.add(f"post cap {i + 1}", B(x0, x0 + 60, 900, 960, 1905, 1915), "aluminium")
        rx = x0 + 60 if i == 0 else x0 - 8
        m.add(f"post rail {i + 1}", B(rx, rx + 8, 915, 945, 1100, 1890), "aluminium")
    m.add("crossbar", B(600, 1290, 900, 960, 1620, 1680), "printer_black")
    for i, (xa, xb) in enumerate(((600.0, 750.0), (1290.0, 1140.0))):
        gus = (cq.Workplane("XZ").polyline([(xa - W / 2, 1620), (xb - W / 2, 1620), (xa - W / 2, 1470)]).close()
               .extrude(-10).translate((0, 925 - D / 2, 0)))
        m.add(f"crossbar gusset {i + 1}", gus, "printer_black")
    m.add("z module", B(890, 1020, 815, 900, 1330, 2060), "aluminium")
    m.add("z motor", B(895, 1015, 820, 895, 2060, 2095), "printer_black")
    m.add("z carriage", B(880, 1030, 800, 815, 1480, 1730), "aluminium")
    # the scanner tray it moves: floor with the beam opening, back wall, end gussets, side boxes
    tray = B(545, 1345, 400, 800, 1490, 1505).cut(C(220, bx, by, 1480, 1520))
    m.add("scanner tray", tray, "printer_black")
    m.add("tray back wall", B(545, 1345, 790, 800, 1505, 1720), "printer_black")
    for i, x0 in enumerate((545.0, 1335.0)):
        gus = (cq.Workplane("YZ").polyline([(500 - D / 2, 1505), (790 - D / 2, 1505), (790 - D / 2, 1715)]).close()
               .extrude(10).translate((x0 - W / 2, 0, 0)))
        m.add(f"tray gusset {i + 1}", gus, "printer_black")
    m.add("tray box left", B(560, 725, 450, 750, 1505, 1700), "printer_black")
    m.add("tray box right", B(1160, 1330, 450, 750, 1505, 1700), "printer_black")
    # two scan heads, a collimator and fibre connector on each
    for i, (x0, x1, cx) in enumerate(((740.0, 945.0, 767.0), (945.0, 1145.0, 1115.0))):
        m.add(f"scan head {i + 1}", B(x0, x1, 430, 780, 1505, 1810).edges("|Z").fillet(6), "printer_black")
        m.add(f"collimator {i + 1}", C(50, cx, by, 1810, 1995), "pp_blue")
        m.add(f"fibre connector {i + 1}", C(28, cx, by, 1995, 2100), "steel")
    # cable chains on brackets off the back wall; each fibre rises out of its chain, bends 180 deg
    # and drops into its collimator (bend tops 2290 and 2320 mm, the spec height)
    for i, (x0, cx, top) in enumerate(((680.0, 767.0, 2290.0), (1150.0, 1115.0, 2320.0))):
        m.add(f"chain bracket {i + 1}", B(x0, x0 + 60, 720, 790, 1700, 1720), "printer_black")
        m.add(f"cable chain {i + 1}", B(x0, x0 + 60, 720, 765, 1720, 2120), "printer_black")
        a, b = (x0 + 30, 742.5), (cx, by)
        r = math.hypot(b[0] - a[0], b[1] - a[1]) / 2
        zc = top - r
        pts = [P(a[0], a[1], 2120), P(a[0], a[1], zc)]
        for k in range(1, 12):
            t = math.pi * k / 12
            u = (1 - math.cos(t)) / 2
            pts.append(P(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, zc + r * math.sin(t)))
        pts += [P(b[0], b[1], zc), P(b[0], b[1], 2100)]
        m.add(f"fibre {i + 1}", hose(pts, 8), "pp_yellow")
    # fibre and cable bundle from the tray's right side down to the worktop, with slack for the Z travel
    m.add("fibre bundle", hose([P(1345, 650, 1600), P(1420, 600, 1440), P(1490, 470, 1260), P(1540, 360, 1200)], 30),
          "pp_yellow")
    # service fittings on the base cabinet's right wall, hoses hanging into the control cabinet
    for i, (yy, zz) in enumerate(((150, 1050), (300, 900), (450, 750), (600, 600), (750, 450))):
        m.add(f"service fitting {i + 1}", hose([P(1390, yy, zz), P(1425, yy, zz)], 25), "brass")
        m.add(f"service hose {i + 1}", hose([P(1425, yy, zz), P(1460, yy, zz - 80), P(1470, yy, zz - 200), P(1500.5, yy, zz - 260)], 16),
              "pp_blue" if i % 2 else "acrylic")
    # control cabinet, right: two doors, e-stop, buttons, wood worktop, tower with LED strip, monitor
    m.add("control cabinet", B(1500, 2450, 0, 800, f, 1170).edges("|Z").fillet(6), "anthracite")
    levelling_feet((1540.0, 2410.0), (40.0, 760.0), f)
    m.add("door split", B(1969, 1973, -1, 0.01, f + 20, 1150), "printer_black")
    m.add("worktop", B(1495, 2455, -20, 800, 1170, 1200), "wood")
    m.add("e-stop", cyl(60, 22).rotate((0, 0, 0), (1, 0, 0), 90).translate(P(1703.0, 0.0, 1065)), "pp_yellow")
    m.add("e-stop cap", cyl(40, 12).rotate((0, 0, 0), (1, 0, 0), 90).translate(P(1703.0, -22.0, 1065)), "paint_red")
    m.add("button panel", B(1562, 1849, -6, 0.01, 868, 1001), "printer_black")
    m.add("control tower", B(1500, 2380, 380, 800, 1200, 1905), "anthracite")
    m.add("led strip", B(1500, 2380, 375, 380.01, 1870, 1905), "led_cyan")
    m.add("monitor pole", B(1950, 1975, 355, 380, 1200, 1850), "aluminium")
    m.add("monitor", B(1663, 2238, 315, 355, 1440, 1735), "screen")
    m.add("keyboard", B(1750, 2177, 60, 210, 1200, 1220), "printer_black")
    m.notes = {"envelope_mm": [W, D, H], "mass_kg": 1450, "build_volume_mm": {"diameter": p["build_d"], "height": p["build_h"]},
               "status": "candidate, not bought", "needs": "argon 6 bar, compressed air 6 bar, 208 V 3-phase 32 A (US option), "
               "a ~15 kW chiller for heating or lasers over 400 W (not modelled)"}
    return m
