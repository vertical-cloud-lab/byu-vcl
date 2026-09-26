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

from common import Model, box, cyl, rbox, tube


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
