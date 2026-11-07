"""Round 8, the tensile stream (#303, PR #318 review of 2026-11-05): the models chapter 5 (``alloy_workflow.py``) needs
that ``instruments.py`` doesn't have, and the tour clips that show them. ``tour.load()`` lets this module's REGISTRY
replace the older model of the same key in every scene.

* ``furnace``: the Nabertherm NAT 15/65 of ``instruments.furnace()``, loaded with ASTM E8 subsize dogbones, the
  chapter's own tensile specimens, lying flat in a stainless specimen tray, instead of plain bars ("those aren't
  tensile specimens. They're just bars."). The tray has a fin at its front that the gripper takes, so the arm can slide
  it in and out of the chamber; the chamber glows while it is hot.
* ``instron_floor``: the 68FM-100 of ``instruments.instron_floor()`` with what an automated, elevated-temperature test
  needs, from Instron's AT6 and AT3 videos and its 3119-600 chamber page: a 3119-608 chamber (to 600 C) round the
  load string, its grips on pull rods so the load cell stays outside; an AVE 2 video extensometer reading through the
  door's window, so no clip-on extensometer goes on by hand; and a scrap chute for the broken halves.
* ``quench_tank``: a water tank beside the furnace on tray F, for the T6's quench (``TRAY_PLACEMENT``).

    xvfb-run -a python3 tour.py furnace instron_floor     # the tour clips, at 8 fps (VIZ3D_FPS=8)
"""
from __future__ import annotations

import cadquery as cq

import instruments as I
from common import box, cyl, rbox  # noqa: F401  (lab_models helpers, on the path via instruments)
from instruments import Joint, _piece, _xcyl, _ycyl  # noqa: F401

import alloy_models as M

# ------------------------------------------------------------------------------------------------ the specimen rack
# A stainless rack for the four cut specimens, standing on end, 30 mm apart along x, each in a slot 25 mm deep: the arm
# handles every specimen level, by its upper grip end (chapter 5), from the wire EDM's comb to the Instron's grips, so
# they never have to be laid flat and picked up again. A fin at the front (-y) is for the gripper when the rack is cold
# and for the tongs when it is hot (12 mm thick, like the plate's lug, so GRIP_LUG closes on it). Our design: a
# heat-treatment rack of this size is an assumption, not a product. Frame: the rack's floor centre, z up.
# Round 9: six slots, 26 mm apart, for the plate's four flat (XY) bars and its two vertical (Z) ones; the fingers
# straddling a bar's 10 mm end still clear its neighbours by 6 mm. Slots 1-4 (x -39..39) take the flat bars, 0 and 5
# (x -65, 65) the vertical ones.
TRAY = dict(W=150.0, D=40.0, H=28.0, floor=3.0, slot_w=11.0, slot_d=7.5, fin_t=12.0, fin_l=36.0, fin_h=64.0,
            pitch=26.0, n=6)
SPEC_X = tuple(TRAY["pitch"] * (i - (TRAY["n"] - 1) / 2) for i in range(TRAY["n"]))     # -65, -39, -13, 13, 39, 65
XY_SLOTS = (1, 2, 3, 4)                                         # rack slots of the flat bars, in the order they come
Z_SLOTS = (0, 5)                                                # and of the vertical ones


def tray_fin_grasp() -> tuple:
    """Where the gripper takes the fin (rack frame): its middle, 14 mm under its top."""
    t = TRAY
    return (0.0, -t["D"] / 2 - t["fin_l"] / 2, t["fin_h"] - 14.0)


def dogbone(x=0.0, y=0.0, z=0.0) -> cq.Workplane:
    """The E8 subsize specimen (alloy_models.E8_SUB), lying flat, long axis along y, bottom face at z."""
    pts = [tuple(map(float, p)) for p in M.bar_outline()]
    return cq.Workplane("XY").polyline(pts).close().extrude(M.E8_SUB["T"]).translate((x, y, z))


def dogbone_up(x=0.0, y=0.0, z=0.0) -> cq.Workplane:
    """The same specimen standing on end in the rack: long axis along z, its 6 mm thickness along y, its lower end at
    z, centred on (x, y)."""
    e = M.E8_SUB
    return (dogbone(0.0, 0.0, -e["T"] / 2).rotate((0, 0, 0), (1, 0, 0), 90)
            .translate((x, y, z + e["L"] / 2)))


def spec_tray() -> cq.Workplane:
    t = TRAY
    w, d, h = t["W"], t["D"], t["H"]
    rack = box(-w / 2, -d / 2, 0, w / 2, d / 2, h).edges("|Z").fillet(3)
    for x in SPEC_X:
        rack = rack.cut(box(x - t["slot_w"] / 2, -t["slot_d"] / 2, t["floor"], x + t["slot_w"] / 2, t["slot_d"] / 2,
                            h + 1))
    fin = box(-t["fin_t"] / 2, -d / 2 - t["fin_l"], 0, t["fin_t"] / 2, -d / 2, t["fin_h"])
    return rack.union(fin)


# ===================================================================================================== furnace
def furnace() -> I.Instrument:
    """instruments.furnace(), its load a tray of four E8 subsize dogbones, and the chamber glowing while hot."""
    inst = I.furnace()
    p = I.FURNACE
    D = p["D"]
    yf = -D / 2
    y1 = yf + p["panel_t"]
    mx, mz0, mh = p["mouth_x"], p["mouth_z0"], p["mouth_h"]
    cw, cd, chh = p["ch_w"], p["ch_d"], p["ch_h"]
    cz = mz0 + (mh - chh) / 2
    load = _piece(inst, "load")
    load.parts.clear()
    load.add("specimen tray", spec_tray(), "stainless")
    for i, x in enumerate(SPEC_X):
        load.add(f"specimen {i + 1}", dogbone_up(x, 0.0, TRAY["floor"]), "sample")
    glow = _piece(inst, "glow")
    glow.add("hot chamber", box(mx - cw / 2 + 2, y1 + cd - 6, cz + 2, mx + cw / 2 - 2, y1 + cd - 3, cz + chh - 2)
             .union(box(mx - cw / 2 + 2, y1 + 22, cz + chh - 5, mx + cw / 2 - 2, y1 + cd - 3, cz + chh - 2)), "glow")
    # the rack in the chamber: its fin's front 70 mm behind the mouth, past the door's 60 mm plug; the specimens'
    # tops 47 mm under the chamber's roof (150 mm inside)
    chamber_c = (mx, y1 + 70 + TRAY["fin_l"] + TRAY["D"] / 2, cz)
    inst.joints["load"] = Joint("path", path=((-330, yf - 330, cz + 80), (mx, yf - 60, cz + 10), chamber_c))
    inst.joints["glow"] = Joint("fade")
    inst.actions = [
        ("The door swings open on its two right-hand hinges; its insulating plug comes out of the chamber's mouth.",
         1.6, {"door": (0.0, 1.0), "load": (0.0, 0.0), "glow": (0.0, 0.0)}),
        ("A rack of the printed tensile specimens goes in: four ASTM E8 subsize dogbones, 100 mm long, cut off their "
         "build plate, standing on end.", 1.8, {"load": (0.0, 1.0)}),
        ("Door shut. A T6: solution treatment at about 530 C, a water quench in the tank beside it, then ageing at "
         "about 160 C (the schedule is an assumption until DAL sets one). The circulation fan holds +-5 C, so one "
         "furnace does both.", 3.0,
         {"door": (1.0, 0.0), "fan": (0.0, 1.0), "~door": (0.0, 0.7), "glow": (0.0, 1.0)}),
        ("", 0.8, {"~door": (0.7, 0.0), "glow": (1.0, 0.0)}),
    ]
    return inst


# ===================================================================================================== Instron
# Round 9 (Sterling, PR #318, 2026-11-05: "The angle and transparency at 32:20 is off. Can't see the tensile test
# happening. Can't tell if there are collisions. Something weird with that heated box."). What was wrong with the box:
# its shell's front wall was solid, so with the door open the arm reached through 30 mm of wall; and its controller
# stood in the 12.5 mm between the chamber and the right column, 24 mm into the column. Now the shell has the door's
# 400 x 560 mm opening, the controller sits on the chamber's roof, left of the pull rod, and the shell is also built
# cut in half through the load string (piece "chamber_cut", the back half) so the chapter can show the test as a
# cutaway instead of through stacked see-through walls.
# Instron's 3119-608 environmental chamber, for floor frames: -150 to 600 C, inside 400 x 400 x 560 mm (D x W x H),
# outside 550 W x 710 H (the outside depth isn't published: 550 assumed); a left-hinged door with a heated triple-pane
# window and an inside light; heating, cooling and fan shut off when the door opens (Instron's 3119-600 product page).
# It mounts on a rigid bracket or on a roller bracket that slides back behind the frame (Instron's chamber video,
# n15Qg7eOph4 at 157 s): drawn here in use, on its rails. Inside it the grips hang on pull rods, so the load cell and the
# crosshead stay outside: the lower grip stands LOWER_UP higher than instruments.instron_floor()'s, on a pull rod, and
# the upper one hangs ROD under the load cell, the crosshead raised by as much, so the upper grip starts where it was.
CHAMBER = dict(W=550.0, D=550.0, z0=560.0, z1=1270.0, wall=75.0, port_r=48.0, door_deg=95.0)
LOWER_UP = 100.0
ROD = 360.0
LOWER_TOP = I.INSTRON_FM["base_h"] + 90.0 + LOWER_UP + 110.0      # 800: the lower grip's jaws start here (body frame)
UPPER_BOTTOM0 = I.INSTRON_FM["xh_z"] - 70.0 - 110.0               # 1070: the upper grip's bottom at crosshead v = 0
AVE = dict(x=-470.0, y=-480.0, z=830.0, yaw=-44.0)   # the AVE 2 on a bracket off the left column, through the window
CHUTE = dict(x=420.0, y=-300.0)                       # the scrap chute on the right of the worktop (AT6: removers drop
#                                                       the broken halves into angled steel chutes)


def instron_floor() -> I.Instrument:
    p = dict(I.INSTRON_FM)
    p["xh_z"] = I.INSTRON_FM["xh_z"] + ROD
    inst = I.Instrument("instron_floor", "Universal testing machine, floor model, with an environmental chamber",
                        "Instron 68FM-100 with a 3119-608 chamber", (p["W"], p["D"], p["H"]),
                        "Instron 6800 Series floor-model sheet (2287 x 1140 x 786 mm, 799 kg, 1494 mm test space, 575 mm "
                        "between columns); 3119-600 series chamber page; the AT6 and AT3 videos (5Hb-zpZ9Bk0, "
                        "Tiipz6Yezek) for the automation", floor=True)
    W, D, H = p["W"], p["D"], p["H"]
    yf = -D / 2
    body = _piece(inst, "body")
    base = box(-W / 2, yf, 0, W / 2, D / 2, p["base_h"] - 30).edges("|Z").fillet(40)
    body.add("base", base, "inst_dark")
    body.add("worktop", rbox(W + 10, D + 10, 30, 40, z=p["base_h"] - 30), "aluminium")
    body.add("base logo", box(-W / 2 + 70, yf - 2, p["base_h"] - 120, -W / 2 + 250, yf, p["base_h"] - 80), "inst_red")
    body.add("base recess", box(-W / 2 + 60, yf - 1, 60, W / 2 - 60, yf + 4, p["base_h"] - 160), "inst_black")
    cx = p["col_dx"] / 2 + p["col_w"] / 2
    for sx in (-1, 1):
        body.add(f"column {'LR'[sx > 0]}", I._ribbed_column(p["col_w"], p["col_d"], H - p["base_h"] - p["top_h"],
                                                           sx * cx, 0, p["base_h"]), "inst_black")
    body.add("top plate", rbox(p["col_dx"] + 2 * p["col_w"] + 40, p["col_d"] + 40, p["top_h"], 16, z=H - p["top_h"]),
             "inst_dark")
    zl = p["base_h"] + 90 + LOWER_UP
    body.add("lower grip", I._wedge_grip(zl, up=True), "steel")
    body.add("lower pull rod", cyl(56, zl - p["base_h"], z=p["base_h"]), "steel")
    xr = cx + p["col_w"] / 2
    body.add("handset", rbox(90, 50, 150, 8, x=xr + 30, y=-p["col_d"] / 2 + 40, z=1100), "inst_dark")
    body.add("e-stop", _ycyl(40, 20, x=xr + 30, y=-p["col_d"] / 2 - 5, z=1320), "inst_red")
    body.add("e-stop label", box(xr + 5, -p["col_d"] / 2 + 13, 1295, xr + 55, -p["col_d"] / 2 + 15, 1345), "inst_yellow")
    body.add("dashboard arm", box(xr, -20, 1480, xr + 260, 20, 1510), "inst_dark")
    body.add("dashboard", box(xr + 220, -150, 1390, xr + 520, -120, 1610).rotate((xr + 370, -135, 1500),
                                                                                  (xr + 370, -135, 1501), 25),
             "inst_black")
    body.add("dashboard screen", box(xr + 235, -152, 1405, xr + 505, -150, 1595).rotate((xr + 370, -135, 1500),
                                                                                        (xr + 370, -135, 1501), 25),
             "screen_on")
    # the chamber, in use round the load string, on its roller bracket's rails (they run back behind the frame)
    c = CHAMBER
    w, d, z0, z1, t = c["W"], c["D"], c["z0"], c["z1"], c["wall"]
    shell = box(-w / 2, -d / 2, z0, w / 2, d / 2, z1).cut(box(-w / 2 + t, -d / 2 + 30, z0 + t, w / 2 - t, d / 2 - t,
                                                             z1 - t))
    shell = shell.cut(box(-w / 2 + t, -d / 2 - 1, z0 + t, w / 2 - t, -d / 2 + 31, z1 - t))     # the door's opening
    for zz in (z0 - 1, z1 - t - 1):
        shell = shell.cut(cyl(2 * c["port_r"], t + 2, z=zz))
    whole = _piece(inst, "chamber")
    whole.add("chamber", shell, "inst_offwhite")
    half = _piece(inst, "chamber_cut")                 # the back half, cut through the load string's axis (y = 0)
    half.add("chamber, cut", shell.cut(box(-w / 2 - 1, -d / 2 - 1, z0 - 1, w / 2 + 1, 0.0, z1 + 1)), "inst_offwhite")
    half.add("chamber, cut faces", box(-w / 2, -1.0, z0, -w / 2 + t, 0.5, z1).union(
        box(w / 2 - t, -1.0, z0, w / 2, 0.5, z1)).union(box(-w / 2, -1.0, z0, w / 2, 0.5, z0 + t)).union(
        box(-w / 2, -1.0, z1 - t, w / 2, 0.5, z1)).cut(cyl(2 * c["port_r"], 2 * z1, z=-1)), "refractory")
    body.add("chamber controller", box(-w / 2 + 30, 20, z1, -w / 2 + 210, d / 2 - 30, z1 + 120), "inst_dark")
    body.add("chamber controller screen", box(-w / 2 + 50, 18, z1 + 20, -w / 2 + 190, 20.01, z1 + 100), "screen_on")
    for sx in (-1, 1):
        body.add(f"chamber rail {sx}", box(sx * (w / 2 - 60) - 15, -d / 2 + 40, z0 - 40, sx * (w / 2 - 60) + 15,
                                           d / 2 + 380, z0 - 10), "aluminium")
        body.add(f"chamber rail leg {sx}", box(sx * (w / 2 - 60) - 15, d / 2 + 340, 0, sx * (w / 2 - 60) + 15,
                                               d / 2 + 380, z0 - 40), "aluminium")
    door = _piece(inst, "chamber_door")
    door.add("chamber door", box(-w / 2, -d / 2, z0 + 20, w / 2, -d / 2 + 30, z1 - 20)
             .cut(box(-w / 2 + 110, -d / 2 - 1, z0 + 170, w / 2 - 110, -d / 2 + 31, z1 - 170)), "inst_offwhite")
    door.add("chamber window", box(-w / 2 + 110, -d / 2 + 10, z0 + 170, w / 2 - 110, -d / 2 + 20, z1 - 170), "window")
    door.add("chamber handle", box(w / 2 - 60, -d / 2 - 34, z0 + 260, w / 2 - 44, -d / 2, z1 - 260), "chrome")
    hot = _piece(inst, "glow")
    hot.add("chamber hot", box(-w / 2 + t + 2, d / 2 - t - 4, z0 + t + 4, w / 2 - t - 2, d / 2 - t - 2, z1 - t - 4),
            "glow")
    # the AVE 2: a camera head on a bracket off the left column's front, looking at the gauge through the window
    a = AVE
    ave = _piece(inst, "ave")              # a prop: it stands in front of the frame, outside its published footprint
    ave.add("ave bracket", box(-p["col_dx"] / 2 - 120, a["y"] + 40, a["z"] - 15, -p["col_dx"] / 2 - 80, -130,
                               a["z"] + 15), "inst_dark")
    cam = rbox(150, 110, 90, 8, x=a["x"], y=a["y"], z=a["z"] - 45).union(
        _ycyl(46, 30, x=a["x"], y=a["y"] + 70, z=a["z"]))
    ave.add("ave camera", cam.rotate((a["x"], a["y"], 0), (a["x"], a["y"], 1), a["yaw"]), "inst_black")
    # the scrap chute, right of the grips on the worktop: a steel chute angled down into a bin under its mouth
    hx, hy = CHUTE["x"], CHUTE["y"]
    chute = box(hx - 70, hy - 70, p["base_h"] + 120, hx + 70, hy + 70, p["base_h"] + 126).union(
        box(hx - 70, hy - 76, p["base_h"] + 126, hx + 70, hy - 70, p["base_h"] + 170)).union(
        box(hx - 76, hy - 70, p["base_h"] + 126, hx - 70, hy + 70, p["base_h"] + 170)).union(
        box(hx + 70, hy - 70, p["base_h"] + 126, hx + 76, hy + 70, p["base_h"] + 170))
    body.add("scrap chute", chute.rotate((hx, hy, p["base_h"] + 120), (hx, hy + 1, p["base_h"] + 120), -18), "steel")
    body.add("scrap chute post", box(hx - 10, hy - 10, p["base_h"], hx + 10, hy + 10, p["base_h"] + 122), "steel")
    xh = _piece(inst, "crosshead")
    z = p["xh_z"]
    xh.add("crosshead", rbox(p["col_dx"] + p["col_w"], p["col_d"] - 30, p["xh_h"], 12, z=z), "inst_black")
    xh.add("crosshead logo", box(-90, -(p["col_d"] - 30) / 2 - 2, z + 80, 90, -(p["col_d"] - 30) / 2,
                                 z + 120), "inst_red")
    xh.add("load cell", cyl(110, 70, z=z - 70), "chrome")
    xh.add("load cell band", cyl(112, 14, z=z - 42), "inst_red")
    xh.add("upper pull rod", cyl(56, ROD, z=z - 70 - ROD), "steel")
    xh.add("upper grip", I._wedge_grip(z - 70 - ROD, up=False), "steel")
    spec = _piece(inst, "specimen")
    spec.add("specimen", dogbone(0.0, 0.0, -M.E8_SUB["T"] / 2).rotate((0, 0, 0), (1, 0, 0), 90)
             .translate((0, 0, LOWER_TOP - 30 + M.E8_SUB["L"] / 2)), "sample")
    inst.joints = {"crosshead": I.Joint("slide", vec=(0, 0, p["travel"])),
                   "chamber_door": I.Joint("hinge", axis=(0, 0, 1), pivot=(-w / 2, -d / 2, 0), deg=-c["door_deg"]),
                   "glow": I.Joint("fade"), "chamber": I.Joint("fade", v0=1.0), "chamber_cut": I.Joint("fade")}
    inst.props = tuple(inst.props) + ("ave",)
    v_test = (LOWER_TOP - 30 + M.E8_SUB["L"] - 30 - UPPER_BOTTOM0) / p["travel"]
    inst.actions = [
        ("A floor frame set up for unattended tests, as in Instron's AT6 and AT3 cells: a printed tensile specimen in "
         "hydraulic wedge grips, inside a 3119-608 chamber (to 600 C) on pull rods.", 2.6,
         {"crosshead": (v_test, v_test), "chamber_door": (0.0, 0.0), "glow": (0.0, 0.0)}),
        ("Its left-hinged door has a heated triple-pane window: the AVE 2 video extensometer reads the strain "
         "through it, so no clip-on extensometer goes on by hand.", 2.0, {"chamber_door": (0.0, 1.0)}),
        ("", 1.4, {"chamber_door": (1.0, 0.0)}),
        ("It heats the grips and the specimen to the test temperature; then the pull.", 2.2, {"glow": (0.0, 1.0)}),
        ("", 2.4, {"crosshead": (v_test, v_test + 0.06)}),
        ("Broken. The halves go down the scrap chute, right of the grips (the AT6 drops them into angled steel "
         "chutes).", 2.4, {"glow": (1.0, 0.0), "crosshead": (v_test + 0.06, v_test + 0.2)}),
    ]
    inst.labels = [("moving crosshead", (-200, -(p["col_d"] - 30) / 2, z + p["xh_h"] / 2), (0.15, 0.20)),
                   ("3119-608 chamber", (0, -d / 2, z1 - 60), (0.84, 0.24)),
                   ("AVE 2 video extensometer", (a["x"], a["y"], a["z"] + 50), (0.12, 0.52)),
                   ("scrap chute", (hx, hy, p["base_h"] + 170), (0.84, 0.66))]
    inst.cam = (0.9, -2.4, 0.8)
    return inst


# ===================================================================================================== quench tank
# A water tank with a lift basket, so the arm never has to reach into the water: the rack is set on the basket's plate,
# which stands just over the rim, and the basket drops it 150 mm into the water (a pneumatic cylinder behind the tank),
# then lifts it out again. A drop quench of this kind is our design; the sizes are assumed.
QUENCH = dict(W=240.0, D=200.0, H=210.0, water=170.0, plate_z=216.0, drop=150.0)


def quench_tank() -> I.Instrument:
    q = QUENCH
    inst = I.Instrument("quench_tank", "Quench tank", "water tank with a lift basket, our design",
                        (q["W"], q["D"], q["H"]),
                        "a stainless tank of water beside the furnace, for the T6's quench, with a basket that drops "
                        "the rack in; size assumed")
    body = _piece(inst, "body")
    w, d, h = q["W"], q["D"], q["H"]
    body.add("tank", box(-w / 2, -d / 2, 0, w / 2, d / 2, h).cut(box(-w / 2 + 3, -d / 2 + 3, 3, w / 2 - 3, d / 2 - 3,
                                                                    h + 1)), "stainless")
    body.add("water", box(-w / 2 + 3.5, -d / 2 + 3.5, 3, w / 2 - 3.5, d / 2 - 3.5, q["water"]), "window")
    body.add("lift cylinder", cyl(32, h + 90, x=0.0, y=d / 2 + 22, z=0), "aluminium")
    lift = _piece(inst, "lift")
    pz = q["plate_z"]
    plate = box(-95, -80, pz - 6, 95, 70, pz)
    for i in range(-3, 4):                                  # drain slots, so the water runs through
        plate = plate.cut(box(i * 24 - 4, -70, pz - 7, i * 24 + 4, 60, pz + 1))
    lift.add("basket plate", plate, "stainless")
    lift.add("basket arm", box(-14, 70, pz - 6, 14, d / 2 + 22, pz + 6), "stainless")
    lift.add("basket rod", cyl(14, 120, x=0.0, y=d / 2 + 22, z=pz - 10), "chrome")
    inst.joints = {"lift": Joint("slide", vec=(0, 0, -q["drop"]))}
    inst.actions = [("A tank of water beside the furnace for the T6's quench, with a lift basket: the rack is set on "
                     "its plate at the rim and dropped into the water.", 2.0, {"lift": (0.0, 1.0)}),
                    ("", 1.4, {"lift": (1.0, 0.0)})]
    return inst


# tray F: the polisher at x -420 and the furnace at 280 (line.TRAY_LOADS); the tank right of the furnace's hinge side,
# clear of its door's swing (the door opens 100 deg on the right-hand hinges, its free edge 466 mm out)
TRAY_PLACEMENT = {"quench_tank": dict(tray="F", x=860.0, y=-150.0, turn=0.0)}

REGISTRY = {"furnace": furnace, "instron_floor": instron_floor, "quench_tank": quench_tank}
