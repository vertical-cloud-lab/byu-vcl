"""The whole lab set up from scratch (#303), on the warehouse floor of ``warehouse.py``: an empty bay; the layout taped
on the floor, with a MiR250 dock and an AprilTag target at every station; the utilities; two Kardex Shuttles
assembled; the floor machines moved in; the UR10e arms installed on their MiR250s; every tray loaded, A to O, each
powered one with its UPS and its stream cameras (the storage trays J, N and O are passive: ``PASSIVE``); the bay
cameras, each seen from an operator's eyes; a closing orbit. Mobile bases only: no rail anywhere.

    xvfb-run --server-num=60 python3 setup_lab.py            # -> out/setup_lab.gif, out/mp4/setup_lab.mp4, still
    PREVIEW=1 xvfb-run --server-num=60 python3 setup_lab.py  # the last frame of each sub-step -> /tmp/preview_setup_lab.png
    xvfb-run --server-num=60 python3 setup_lab.py fit        # every tray and the floor, measured as drawn ->
                                                             #   out/tray_plan.json, out/tray_plan.png, out/tray_plan_floor.png

What goes where is data: ``TRAYS`` (tray -> slot and role), ``ITEMS`` (tray -> [(key, x, y, turn)]), ``CAMS`` (the
stream cameras of the trays services.TRAY_CAMS doesn't cover yet) and ``FLOOR_PLAN`` (the floor, in
warehouse.STATIONS's form). Slots and their heights are ``vlm.COLUMNS``; notes/tray_plan.md explains the plan.
``fit`` builds the scene, then measures every tray item, the tray's UPS, its dock plate and its camera rigs from their
meshes, in the tray's frame: overlaps, the rim, the opening's product height and the slot's span. On the floor it
checks every MiR250 dock, its approach and the pivot spot it turns on, against every machine and every target post.

Everything here that isn't a maker's figure is a layout choice: the cable trays, drops, junction boxes and the argon
line, the cameras and where they sit, the second Shuttle and the floor plan. Kardex's 208 V three-phase supply is
#53's. Installing the arm follows UR's manual (four M8 bolts at 20 Nm, two 8 mm pins for re-mounting; UR10e user manual
SW5.26, 6.1).
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import math
import pickle
import sys

import numpy as np
import pyvista as pv

import animate as A
import lab
import line
import props as P
import tour
import vlm as V
import warehouse as W
from scene import FPS, OUT, PREVIEW, Scene, T, R, S, window

TITLE = "Vertical cloud lab, set up from scratch"
X2 = V.SHUTTLE_X[2]                            # the second Shuttle's centre

# ================================================================================================ what goes where
# tray: (slot in vlm.SLOTS, role). Shuttle 1 holds the alloy route and characterization, Shuttle 2 fabrication, the
# inert glovebox and the round-7 testing trays (notes/tray_plan.md).
TRAYS = {
    "A": ("R2", "liquid handling, corrosion"), "B": ("R3", "powder dosing, vacuum press"),
    "C": ("F1", "3D printing"), "D": ("R1", "microscopy and diffraction"),
    "E": ("R4", "mechanical testing, particle size"), "F": ("F2", "polishing and heat treatment"),
    "J": ("F0", "sample storage"),
    "K": ("2R1", "inert glovebox, digital microscope"), "L": ("2R2", "tensile and hardness"), "M": ("2R3", "machining and XRF, under a hood"),
    "H": ("2R4", "PCB assembly"), "G": ("2F1", "resin printing"), "I": ("2F2", "desktop LPBF"),
}
ORDER = ["D", "A", "B", "E", "J", "C", "F", "K", "L", "M", "H", "G", "I"]      # loading order: Shuttle 1, then 2
# Round 14: the 9150 mm Shuttles (vlm.UNIT_H) take three more passive stores over the trays they have, in slots of
# their own height (vlm.COLUMNS): a second sample store over tray E, and a second rack each of atomized lots and of
# feedstock over tray H, both as r8_store builds N's and O's (TALL_TRAYS; added after merge_r8, which would otherwise
# move r8_store's stores back onto N and O)
TALL_TRAYS = {"S": ("R5", "sample storage, second store", [("storage", 0.0, 0.0, 0.0)]),
              "P": ("2R5", "powder store: atomized lots, second rack", [("powder_store_lots", 0.0, 0.0, 0.0)]),
              "Q": ("2R6", "powder store: feedstock, second rack", [("powder_store_feed", 0.0, 0.0, 0.0)])}
# Round 11 (Sterling, PR #318, 2026-11-13: "Do we actually need cameras on the jars at all times? In terms of inventory,
# we're going to get that with the overhead camera in the bay anyway"): the storage trays are passive. Nothing on them
# draws power or gas, so they carry no UPS, no dock plate or tray lines, no socket, power strip or power lamp and no
# stream cameras; the bay's overhead camera (and the wrist D405) sees what is on one whenever it is presented, the only
# time anything on it can change. Their slots mate with nothing, so they have no dock either (notes/tray_plan.md). A
# module adds its own with PASSIVE_TRAYS = {...} (r8_store: the jar stores N and O).
PASSIVE = {"J"}
# tray: [(key, x, y, turn)] in the tray's frame (centre of its floor, y to the back); y None puts the item's front 30 mm
# behind the tray's front lip, as fab_trays does. A-C's round-2 items are animate.LOADS's (built by animate.Lab), D-F
# line.TRAY_LOADS's, G-I fab_trays.LOADS's. Each tray also carries its UPS and dock plate at the back right
# (services.UPS_AT, services.PLATE_*) and its camera posts (services.TRAY_CAMS or CAMS below); `fit` checks them all.


STORAGE_X = 0.0         # tray J's storage load, centred (round 7: x -320, its right 630 mm left for the UPS and dock)


def _items() -> dict:
    import alloy_press as AP
    import fab_trays as FT
    out = {k: [(key, x, y, 0.0) for key, x, y in v] for k, v in A.LOADS.items()}
    out["A"] = [it for it in out["A"] if it[0] != "cubxl"] + [("cubxl_corrosion", -300.0, -114.5, 0.0)]
    out["B"] += [("vacuum_press", *AP.PRESS_AT, 0.0)]           # alloy_press.PRESS_AT, as in the alloy route
    for k, v in line.TRAY_LOADS.items():
        out[k] = [(key, x, y, 0.0) for key, x, y in v]
    for k, v in FT.LOADS.items():
        out[k] = [tuple(it) for it in v]
    out["J"] = [("storage", STORAGE_X, 0.0, 0.0)]               # centred on the tray (round 11: no UPS, no dock)
    # the Keyence VHX is 624 mm deep as modelled: tray C has no room for it between its camera posts and the UPS, so it
    # went to K, beside the glovebox, in front of the UPS
    # round 14 (fit's clearance check, CLEAR_MM): the VHX stood 7 mm from tray K's UPS, solid to solid, and the
    # zwickiLine 3 mm from tray L's and 9.7 mm from the HM-220; the VHX moves 5 mm forward (y -50 -> -55), the
    # zwickiLine 10 mm forward (its front 20 mm behind the lip, not 30) and 5 mm right: 12, 13 and 14.7 mm
    out["K"] = [("glovebox_tray", -460.0, 7.0, 0.0), ("vhx", 570.0, -55.0, 0.0)]
    out["L"] = [("tensile_h", -18.5, -81.0, 0.0), ("hardness", -944.0, 11.0, 0.0)]      # the tester in front of the UPS
    out["M"] = [("xrf", -875.0, None, 0.0), ("fumehood_tray", -13.0, None, 0.0), ("cnc", 819.0, None, 0.0)]
    # round 8 (PR #318: "It's also not really clear why we'd want both v7's and delta stages"): the OpenFlexure array
    # leaves tray D; the Keyence VHX does its imaging (notes/lab_r8.md)
    out["D"] = [it for it in out["D"] if it[0] != "openflexure_array"]
    # round 10: the PCB line's reflow oven (README since round 4: "The right end, about 470 mm, is free for a reflow
    # oven"), its drawer to the front, 16 mm right of the LumenPnP and 14 mm inside the rim (reflow_oven())
    out["H"] = [it for it in out.get("H", []) if it[0] != "reflow"] + [("reflow", 984.0, None, 0.0)]
    return out


# the reflow oven on tray H (round 10, the coordinator's ledger: the PCB line never had one). Puhui's T-962A, an
# infrared and hot-air batch oven with a windowed drawer: Puhui's listing gives 430 x 370 x 260 mm (43 x 37 x 26 cm),
# 15 kg, 1500 W at 110 or 220 V, a 300 x 320 mm soldering area. The LPKF ProtoFlow S4 (555 x 480 x 300 mm, 38 kg) is
# 85-125 mm too wide for the 460 mm left at the tray's right end, either way round, with its drawer to the front.
REFLOW = dict(W=430.0, D=370.0, H=260.0, kg=15.0, watts=1500.0, area_mm=(300.0, 320.0),
              source="Puhui T-962A listing (taianpuhui.en.made-in-china.com): 430 x 370 x 260 mm, 15 kg, 1500 W, "
                     "AC 110/220 V, 300 x 320 mm soldering area, infrared and hot-air; the front's layout (drawer at the "
                     "left, LCD and keys at the right) is ours, from photos",
              url="https://taianpuhui.en.made-in-china.com/product/GXLmWKoTvtUI/China-Desktop-Reflow-Oven-Puhui-T962A.html",
              alt="LPKF ProtoFlow S4: 555 x 480 x 300 mm, 38 kg (lpkfusa.com): too wide for the tray's free end")


def reflow_oven():
    """Puhui's T-962A as an Instrument: the case on four feet, the windowed drawer on the left of the front with its
    handle, the control panel (an LCD and five keys) on the right, vents on the top. Origin at the centre of its
    footprint, its front to -y."""
    import instruments as I
    sys.path.insert(0, str(lab.HERE / "lab_models"))
    from common import box
    w, d, h = REFLOW["W"], REFLOW["D"], REFLOW["H"]
    inst = I.Instrument("reflow", "Benchtop batch reflow oven", "Puhui T-962A", (w, d, h), REFLOW["source"])
    b = I._piece(inst, "body")
    x0, x1, y0, y1 = -w / 2, w / 2, -d / 2, d / 2
    for fx in (x0 + 25, x1 - 25):
        for fy in (y0 + 25, y1 - 25):
            b.add(f"foot {fx:.0f} {fy:.0f}", box(fx - 15, fy - 15, 0, fx + 15, fy + 15, 12), "inst_black")
    b.add("case", box(x0, y0 + 6, 12, x1, y1, h), "inst_offwhite")
    xd = x1 - 120.0                                    # the drawer's right edge; the control panel right of it
    b.add("drawer front", box(x0 + 10, y0, 30, xd, y0 + 6, h - 30), "inst_dark")
    b.add("drawer window", box(x0 + 50, y0 - 1, 70, xd - 40, y0 + 1, h - 80), "window")
    b.add("drawer handle", box(x0 + 90, y0 - 22, h - 62, xd - 80, y0 - 1, h - 48), "inst_light")
    b.add("control panel", box(xd + 8, y0 + 2, 30, x1 - 10, y0 + 6, h - 30), "inst_black")
    b.add("LCD", box(xd + 20, y0 + 1, h - 105, x1 - 22, y0 + 2, h - 50), "screen_on")
    for i in range(5):
        kx = xd + 22 + i * 17.0
        b.add(f"key {i}", box(kx, y0 - 2, 60, kx + 11, y0 + 2, 74), "inst_grey")
    for i in range(6):
        vy = y0 + 90 + i * 34.0
        b.add(f"vent {i}", box(x0 + 60, vy, h, x1 - 140, vy + 12, h + 1.5), "inst_dark")
    inst.labels = [("windowed drawer, 300 x 320 mm", (-60, y0, h - 40), (0.25, 0.25)),
                   ("LCD and keys", (x1 - 60, y0, h - 60), (0.75, 0.25))]
    inst.notes = ["430 x 370 x 260 mm, 15 kg, 1500 W (Puhui's listing); the front's layout is ours",
                  "on tray H it is on the unbacked branch: its heaters pause in transit (ups.TRAY_LOADS)",
                  "solder flux fumes: it wants extraction, which tray H doesn't have yet"]
    return inst


def reflow_entries() -> dict:
    """{"reflow": (Instrument, entries)} for load_all."""
    import tour as TR
    inst = reflow_oven()
    return {"reflow": (inst, TR.piece_entries(inst))}


ITEMS = _items()
# the stream cameras of the trays services.TRAY_CAMS has no entry for: tray: ([(mast x, mast y, aim x, aim y, aim z
# [, post yaw])], block height on the post, post height). The short tray H has short posts, so its slot stays low: the
# head's top is about block + 148 mm over the tray's underside (services.TILT_AXIS, head_reach). Round 11: tray J's two
# short posts are gone (PASSIVE); SHORT_CAMS is what they were, the default for a new tray from a module that isn't
# passive.
SHORT_CAMS = ([(680.0, -360.0, -320.0, -100.0, 150.0), (1160.0, 100.0, -700.0, -100.0, 150.0)], 270.0, 320.0)
CAMS = {
    "G": ([(-1150.0, 361.0, -920.0, -150.0, 300.0, 90.0), (160.0, 361.0, 200.0, -150.0, 250.0, 90.0)], None, None),
    "H": ([(-1150.0, 361.0, -640.0, -100.0, 250.0, 90.0), (-130.0, 361.0, 400.0, -100.0, 200.0, 90.0)], 270.0, 320.0),
    "I": ([(-1150.0, 361.0, -500.0, -150.0, 400.0, 90.0), (-100.0, 361.0, 300.0, -150.0, 400.0, 90.0)], None, None),
    "K": ([(470.0, 361.0, -460.0, -300.0, 450.0, 90.0)], None, None),
    "L": ([(-620.0, 361.0, -944.0, -150.0, 400.0, 90.0), (180.0, 361.0, -23.0, -150.0, 300.0, 90.0)], None, None),
    "M": ([(-480.0, 361.0, -873.0, -150.0, 400.0, 90.0), (470.0, 361.0, 722.0, -150.0, 400.0, 90.0)], None, None),
}

# ------------------------------------------------------------------------------------------------ the floor
# warehouse.STATIONS's form: key: (x of its centre, row, turn about z, dock x). The second Shuttle stands 800 mm right
# of the first: a MiR250 turns on the spot between them (its corners sweep 0.49 m), then backs into the first one's
# dock or drives forwards into the second's. The wire EDM and the DED went to the south row and the packaging station
# to the north, so every dock has a pivot spot at its open end (``fit`` checks it).
# the 68FM-100's load axis on the floor (round 11): r8_test's model, 1575 mm wide with its dashboard, centred on the
# station's x = -6400 and turned to face north, puts its axis at x -6187.5, where chapter 5 parks the MiR (ins_x)
INSTRON_AXIS_X = -6187.5
FLOOR_PLAN = {
    "glovebox": (-7300.0, "N", -90.0, -7300.0),
    "repowder": (None, "N", 0.0, A.REPOWDER_AT[0] + 288.0),
    "sieve_cell": (-1982.5, "N", 0.0, -1700.0),
    "vlm": (0.0, "N", 0.0, 0.0),
    "vlm2": (X2, "N", 0.0, X2),
    "aconity": (6950.0, "N", 0.0, 6520.0),           # round 11: chapter 5's stop, 146 mm short of the build cylinder
    "packaging": (10050.0, "N", 0.0, 10050.0),
    "instron_floor": (-6400.0, "S", 0.0, INSTRON_AXIS_X),         # round 11: dock on the load axis (was x -6600)
    "instron_small": (-4300.0, "S", 0.0, -4300.0),
    "fumehood": (1500.0, "S", 0.0, 1500.0),
    "ded": (3900.0, "S", 0.0, 3900.0),
    "wire_edm": (6600.0, "S", 0.0, 6600.0),
}
BACK_IN = {"instron_small", "vlm", "aconity", "sieve_cell"}   # backed into from the open end beyond the MiR's back
# the rePowder sticks out 337 mm past the row's fronts, so a MiR docks there 298 mm further out, as the alloy route's
# chapters 2-3 park it (alloy_atomize.END_POSE); so does the sieving cell's (alloy_print: 300 mm off its bench)
DOCK_Y = {"repowder": -2230.0, "sieve_cell": W.DOCK_N - 300.0,
          # round 11: chapter 5's MiR stops 500 mm off the row at the Instron, 68 mm clear of the 3119-608 chamber's
          # 550 mm door, which swings 432 mm out in front of the frame (alloy_workflow, MIR_YI); the tape follows it
          "instron_floor": W.Y_FACE_S + 500.0 + P.MIR["W"] / 2,
          # round 11: chapter 5's MiR stops 230 mm off the row at the Aconity MIDI, so the tray on its deck clears the
          # chamber's front; at the old tape (80 mm off, x 6650) it stood with its skirt on the target post's foot plate
          "aconity": W.Y_FACE_N - 230.0 - P.MIR["W"] / 2}
# targets that can't stand where warehouse.target_xy puts them: the VLMs' stand outside the opening's width, so a tray
# pulled out to the front for maintenance passes them; the rePowder's in front of its own front
TARGET_AT = {"vlm": (-1330.0, -1742.0), "vlm2": (X2 + 1330.0, -1742.0),
             # round 11: 150 mm off the Instron's face as before, 650 mm beyond the docked MiR's front end, west of the
             # chamber door's sweep, though the dock moved 420 mm out from the row
             "instron_floor": (INSTRON_AXIS_X - 650.0, W.Y_FACE_S + 150.0)}
# round 15 (#303, round 14 (C)'s open fault): the rePowder's own post (model x 938, y -379) stood where MiR250 1 parks
# for the latch (atom_latch.A_AT: model x 250..1050, y -850..-270). Nothing else fits between that spot, the dock line
# and the aisle, so the rePowder's docked unit reads the sieving cell's post, 737 mm beyond its front end and 218 mm to
# its left: one post, its cube's west face for the rePowder, its east face for the sieving cell (warehouse.tag: five
# faces, five patterns). 115 mm clear of MiR250 1 at atom_base.PARK["right"], off every dock and approach.
SHARED_POST = {"repowder": "sieve_cell"}
SIEVE_BENCH = dict(x=-1982.5, w=1065.0, d=600.0, h=700.0, encl_h=1150.0)    # alloy_print.BENCH, ENCL_H
INSTALL_AT = 0                                 # the first unit is put together at charger 0
# round 16 (#303; PR #371's check of 2026-11-26: "Give the machining cell a place on the floor that doesn't take unit 3's
# charger"): PR #373's cup-and-plug machining cell south of the south row, front to the north, behind the 68SC-2, unit
# 3's charger and charger 0 (machining.FLOOR; notes/lab_r16.md). Its dock is on a line of its own, the corridor behind
# the row (DOCK_Y), backed into from the west, where its MiR250 comes in from the aisle down the row's west end; so its
# post stands beyond the docked unit's back end (BACK_IN), 150 mm off the front's light-curtain posts (TARGET_AT).
# Floor._stations draws the cell. VLAB_MCELL=0 leaves it out, with its dock and post.
if os.environ.get("VLAB_MCELL", "1") != "0":
    import machining as MA
    FLOOR_PLAN["machining"] = (MA.FLOOR["x"], "S", MA.FLOOR["turn"], MA.FLOOR["dock"][0])
    DOCK_Y["machining"] = MA.FLOOR["dock"][1]
    BACK_IN.add("machining")
    TARGET_AT["machining"] = MA.FLOOR["target"]

CAM_ROOM = [(11000, -22000, 15500), (500, -2700, 0), (0, 0, 1)]
CAM_TOP = [(2000, -15000, 22500), (300, -2800, 0), (0, 0, 1)]
CAM_UTIL = [(16000, -32000, 20000), (700, -2200, 3300), (0, 0, 1)]    # round 14: up to the 10.97 m roof steel
CAM_VLM = [(19500, -24500, 12500), (1800, -500, 4600), (0, 0, 1)]    # round 14: the 9150 mm Shuttles whole
CAM_FLOOR = [(6200, -21500, 17500), (700, -2900, 0), (0, 0, 1)]
# round 8: the scale-up machines past the south row's ends (the EOS lower left, the Meltio cell lower right) with the
# whole lab behind them; a camera test of five views found this the one that shows both whole
CAM_SCALE = [(6200, -31000, 24000), (0, -6500, 0), (0, 0, 1)]
CAM_UNIT = [(1900, -2900, 2300), (-1300, -5600, 800), (0, 0, 1)]
CAM_OPEN = [(3500, -5900, 2700), (0, -1000, 1300), (0, 0, 1)]      # north of the south row's cable tray and argon
CAM_OPEN2 = [(X2 + 3500, -5900, 2700), (X2, -1000, 1300), (0, 0, 1)]
# round 11: the bay cameras from an operator's eyes, 1.6 m up and 0.9 m in front of the Shuttle's face, 420 mm right of
# its centre (services.movie_bay_camera's view), looking up under the header at the unit
# round 14: at the opening, 0.26 m in front of its face, 1.5 m up, looking up under the header at the bay's roof and its
# two cameras (services.CAM_S_EYE); 0.9 m out, the header hid them
BAY_EYE = (420.0, -1820.0, 1500.0)
BAY_VIEW_ANGLE = 62.0
ORBIT = [[(-9000, -16500, 9000), (700, -2300, 600), (0, 0, 1)],
         [(-15500, -2000, 9500), (700, -2300, 600), (0, 0, 1)],
         [(3500, -15500, 5600), (700, -2300, 900), (0, 0, 1)],
         [(18000, -28500, 17500), (1200, -2200, 3600), (0, 0, 1)]]    # round 14: the 9150 mm Shuttles in the last


# ------------------------------------------------------------------------------------------------ round 8's modules
R8_MERGED: dict = {"trays": {}, "floor": {}, "new_trays": {}, "skipped": [], "moved": {}}  # what merge_r8() took in
# Floor machines no MiR250 serves, so no dock tape, no target post and no dock check: the EOS M 400-4 and the Meltio
# cell (notes/scaleup.md: "Neither has a MiR dock: the powder comes by the 100 kg in EOS's containers, and a propeller
# by forklift or crane"). A module adds its own with NO_DOCK = {...}, or dock=False in a FLOOR_PLACEMENT.
NO_DOCK = {"eos_m400", "meltio_cell"}
# Where two streams' placements collide, the tray plan's call (fit found it; notes/lab_r8.md): tray F's quench tank
# (r8_test, x 860, y -150) stood inside the disc magazine (r8_prep, x 1022, y -190). The magazine keeps its place in
# front of the UPS; the tank moves left and back, between the furnace's right side and the magazine: 25 mm from the
# furnace, 44 mm from the magazine, clear of the furnace door's swing (it opens to the front on its right-hand hinges).
# Its rig is where every scene built on setup_lab.build finds it. Until round 10 camera F1's post stood in front of
# the tank, 40 mm from it; since round 11 (services.TRAY_CAMS["F"], chapter 5's stream) F1 stands behind the tank, post
# at y 85-175, 16 mm off its back, looking down into it, out of the path the tongs carry the rack along.
R8_MOVES = {"quench_tank": dict(tray="F", x=680.0, y=-50.0, turn=0.0)}


def add_slots(slots: dict):
    """New storage slots {slot: (column, span)} on Shuttle 2, added for this process (vlm.py's own COLUMNS stay as
    they are, so no cache that hashes vlm.py changes): each starts where its column's last slot ends. A slot vlm.COLUMNS
    has already (round 11: r8_store's 2F0 and 2F0b) is left as it is; a span that disagrees with it is reported."""
    for slot, (col, span) in slots.items():
        if slot in V.SLOTS:
            if abs(V.SPAN.get(slot, span) - float(span)) > 1e-6 or V.SLOT_SHUTTLE.get(slot) != 2:
                msg = f"slot {slot}: {span} mm asked for, vlm.COLUMNS has {V.SPAN.get(slot)} (Shuttle " \
                      f"{V.SLOT_SHUTTLE.get(slot)}): vlm.COLUMNS kept"
                R8_MERGED["skipped"].append(msg)
                print("setup_lab:", msg, flush=True)
            continue
        lst = V.COLUMNS[2][col]
        if col == "front":
            z = V.Z_FRONT_HI
        else:
            z = V.Z_LOW
        z += sum(s for _, s in lst)
        top = V.Z_FRONT_LOW_TOP if col == "front_low" else V.Z_TOP_IN
        assert z + span <= top + 1e-6, (slot, z, span, top)
        lst.append((slot, span))
        V.SLOTS[slot] = (V.Y_REAR if col == "rear" else V.Y_FRONT, z)
        V.SPAN[slot], V.SLOT_SHUTTLE[slot] = float(span), 2


def merge_r8() -> dict:
    """Every TRAY_PLACEMENT and FLOOR_PLACEMENT of the round-8 modules that exist (tour.MODULES' r8_* names) into
    ITEMS and FLOOR_PLAN; new trays (a module's NEW_TRAYS: {tray: (slot, role)}, with NEW_SLOTS for the slots) into
    TRAYS and ORDER. A placement of a key a tray already has moves it. Runs once per process, when the scene is built."""
    if R8_MERGED.get("done"):
        return R8_MERGED
    for name in tour.MODULES:
        if not name.startswith("r8_") or not (lab.HERE / f"{name}.py").exists():
            continue
        try:
            mod = importlib.import_module(name)
        except Exception as e:                       # noqa: BLE001  (a module mid-edit must not stop the set-up)
            R8_MERGED["skipped"].append(f"{name}: {e}")
            print(f"setup_lab: {name} not merged: {e}", flush=True)
            continue
        add_slots(getattr(mod, "NEW_SLOTS", {}))
        PASSIVE.update(getattr(mod, "PASSIVE_TRAYS", ()))
        for k, (slot, role) in getattr(mod, "NEW_TRAYS", {}).items():
            if k not in TRAYS and slot in V.SLOTS:
                TRAYS[k] = (slot, role)
                ORDER.append(k)
                if k not in PASSIVE:
                    CAMS.setdefault(k, SHORT_CAMS)     # short posts, as tray J's were: a short slot
                R8_MERGED["new_trays"][k] = dict(slot=slot, role=role, module=name, passive=k in PASSIVE)
        for key, p in getattr(mod, "TRAY_PLACEMENT", {}).items():
            k = p["tray"]
            if k not in TRAYS:
                R8_MERGED["skipped"].append(f"{name}: {key} on tray {k}, which has no slot")
                continue
            for kk in ITEMS:                           # a key placed again moves (from any tray)
                ITEMS[kk] = [it for it in ITEMS[kk] if it[0] != key]
            ITEMS.setdefault(k, []).append((key, float(p["x"]), None if p.get("y") is None else float(p["y"]),
                                            float(p.get("turn", 0.0))))
            R8_MERGED["trays"][key] = dict(p, module=name)
        for key, p in getattr(mod, "FLOOR_PLACEMENT", {}).items():
            row = "N" if p["y"] > (W.AISLE[0] + W.AISLE[1]) / 2 else "S"     # its front on its row's face
            FLOOR_PLAN[key] = (float(p["x"]), row, float(p.get("turn", 0.0)), float(p.get("dock_x", p["x"])))
            if "setback" in p:                       # back from its row's face, away from the aisle (warehouse.place)
                W.SETBACK[key] = float(p["setback"])
            if p.get("dock") is False:
                NO_DOCK.add(key)
            R8_MERGED["floor"][key] = dict(p, row=row, module=name)
        NO_DOCK.update(getattr(mod, "NO_DOCK", ()))
    for key, p in R8_MOVES.items():                  # the tray plan's resolutions, last
        if p["tray"] not in TRAYS or not any(it[0] == key for v in ITEMS.values() for it in v):
            continue
        for kk in ITEMS:
            ITEMS[kk] = [it for it in ITEMS[kk] if it[0] != key]
        ITEMS[p["tray"]].append((key, float(p["x"]), None if p.get("y") is None else float(p["y"]),
                                 float(p.get("turn", 0.0))))
        R8_MERGED["moved"][key] = dict(p, was=R8_MERGED["trays"].get(key))
    for k, (slot, role, its) in TALL_TRAYS.items():   # round 14: the stores the taller Shuttles take
        if k in TRAYS or slot not in V.SLOTS:
            continue
        TRAYS[k] = (slot, role)
        PASSIVE.add(k)
        ORDER.insert(ORDER.index("F") + 1 if V.SLOT_SHUTTLE[slot] == 1 else len(ORDER), k)
        ITEMS[k] = list(its)
        R8_MERGED["new_trays"][k] = dict(slot=slot, role=role, module="setup_lab.TALL_TRAYS", passive=True)
    R8_MERGED["no_dock"] = sorted(NO_DOCK)
    R8_MERGED["passive_trays"] = sorted(PASSIVE)
    R8_MERGED["done"] = True
    return R8_MERGED


def use_floor_plan():
    """Point warehouse.py's floor plan at FLOOR_PLAN for this process: its stations, docks and targets."""
    W.STATIONS.clear()
    W.STATIONS.update(FLOOR_PLAN)
    W.BACK_IN.clear()
    W.BACK_IN.update(BACK_IN)
    W.RESERVED.clear()
    W.NAMES.update(fumehood="ducted fume hood", sieve_cell="sieving cell", vlm2="second Kardex Shuttle",
                   eos_m400="EOS M 400-4 (no MiR dock)", meltio_cell="Meltio robot cell (no MiR dock)")
    if getattr(W, "_setup_lab_patched", False):
        return
    dock0, target0 = W.dock_pose, W.target_xy

    def dock_pose(key):
        x, y, hd = dock0(key)
        return (x, DOCK_Y.get(key, y), hd)

    def target_xy(key):
        key = SHARED_POST.get(key, key)
        return np.array(TARGET_AT[key]) if key in TARGET_AT else target0(key)
    W.dock_pose, W.target_xy, W._setup_lab_patched = dock_pose, target_xy, True


# ================================================================================================ the models
def load_r7() -> dict:
    """instruments_r7's models (round 7: the tray glovebox, the sideways tensile tester, the hardness tester, the CNC,
    the fume hoods, the storage load), cached on their sources, unless tour.MODULES loads them already."""
    try:
        mod = importlib.import_module("instruments_r7")
    except ModuleNotFoundError:
        return {}
    if "instruments_r7" in tour.MODULES or not getattr(mod, "REGISTRY", None):
        return {}
    tour.MATS.update(getattr(mod, "MATERIALS", {}))
    h = hashlib.sha256()
    for f in [*tour._sources("instruments"), lab.HERE / "instruments_r7.py"]:
        if f.exists():
            h.update(f.read_bytes())
    path = tour.CACHE / f"instruments_r7_{h.hexdigest()[:12]}.pkl"
    if path.exists():
        return pickle.loads(path.read_bytes())
    out = {}
    for key, build in mod.REGISTRY.items():
        print(f"  building {key}", flush=True)
        try:
            inst = build()
        except FileNotFoundError as e:
            print(f"  skipping {key}: {e}", flush=True)
            continue
        out[key] = (inst, tour.piece_entries(inst))
    path.write_bytes(pickle.dumps(out))
    return out


def r7_stand_ins(have) -> dict:
    """A plain box at its FOOTPRINTS size for each instruments_r7 model not built yet, so the layout and the checks
    run before the models land. Each one says so in its model name."""
    try:
        import instruments_r7 as R7
    except ModuleNotFoundError:
        return {}
    import instruments as I
    sys.path.insert(0, str(lab.HERE / "lab_models"))
    from common import box
    out = {}
    for key, (w, d, h, _kg, product, url, where) in getattr(R7, "FOOTPRINTS", {}).items():
        if key in have:
            continue
        inst = I.Instrument(key, key, product.split(",")[0].split(" (")[0] + " (stand-in box)", (w, d, h), url,
                            floor=where == "floor")
        I._piece(inst, "body").add("stand-in", box(-w / 2, -d / 2, 0, w / 2, d / 2, h), "inst_light")
        out[key] = (inst, tour.piece_entries(inst))
    return out


def tour_load_safe() -> dict:
    """tour.load(), except that a module that won't import, or a model whose build raises (another stream's module in
    the middle of an edit), is skipped with a note instead of stopping the scene. A module with a failed model is not
    cached here, so its owner's next good build still caches normally."""
    try:
        return tour.load()
    except Exception as e:                           # noqa: BLE001
        print(f"setup_lab: tour.load() failed ({type(e).__name__}: {e}); loading module by module", flush=True)
    data = {}
    for name in tour.MODULES:
        if not (lab.HERE / f"{name}.py").exists():
            continue
        try:
            mod = tour.I if name == "instruments" else importlib.import_module(name)
        except Exception as e:                       # noqa: BLE001
            print(f"setup_lab: {name} skipped, it does not import: {e}", flush=True)
            continue
        if not getattr(mod, "REGISTRY", None):
            continue
        tour.MATS.update(getattr(mod, "MATERIALS", {}))
        h = hashlib.sha256()
        for f in tour._sources(name):
            if f.exists():
                h.update(f.read_bytes())
        h.update(str((tour.CACHE / "openflexure" / "v7").is_dir() and
                     (tour.CACHE / "openflexure" / "delta").is_dir()).encode())
        path = tour.CACHE / f"{name}_{h.hexdigest()[:12]}.pkl"
        if path.exists():
            try:
                data.update(pickle.loads(path.read_bytes()))
                continue
            except Exception:                        # noqa: BLE001  (a cache being written: build it here)
                pass
        part, failed = {}, []
        for key, build in mod.REGISTRY.items():
            try:
                inst = build()
            except Exception as e:                   # noqa: BLE001
                print(f"  skipping {key} ({name}): {type(e).__name__}: {e}", flush=True)
                failed.append(key)
                continue
            part[key] = (inst, tour.piece_entries(inst))
        if not failed:
            path.write_bytes(pickle.dumps(part))
        data.update(part)
    return data


def load_all() -> dict:
    """{key: (Instrument, entries)}: tour.load()'s, fab_tour's for trays G-I, and instruments_r7's (stand-in boxes
    for the ones not built yet)."""
    import fab_tour
    idata = tour_load_safe()
    fab = {key for k in "GHI" for key, *_ in ITEMS[k]}
    idata.update(fab_tour.load(fab))
    idata.update(load_r7())
    idata.update(r7_stand_ins(idata))
    if "reflow" not in idata:
        try:
            idata.update(reflow_entries())
        except Exception as e:                       # noqa: BLE001  (a nicety: the set-up still runs without it)
            print("setup_lab: no reflow oven:", e, flush=True)
    return idata


def item_label(inst) -> str:
    """The name a tray item goes by in captions and labels: its model, unless the model is only "our design" (round
    8's powder-prep station), when its name says what it is."""
    m = inst.model.strip()
    return f"{inst.title} (our design)" if m.lower() in ("our design", "ours", "(ours)") else m


def placed(inst, x, y, turn) -> np.ndarray:
    """An instrument's own frame -> (x, y) on the tray floor, turned about z; y None: its front 30 mm behind the lip."""
    x0, x1, y0, y1, z0, _ = inst.bbox()
    if y is None:
        d = (y1 - y0) if abs(turn) % 180 < 1 else (x1 - x0)
        y = -(V.TRAY_D - 24.0) / 2 + 30.0 + d / 2
    return T((x, y, V.T_FLOOR)) @ R((0, 0, 1), turn) @ T((-(x0 + x1) / 2, -(y0 + y1) / 2, -z0))


# ================================================================================================ two Shuttles
class TwoLab(A.Lab):
    """animate.Lab with a second Shuttle at x = X2: a copy of the VLM's meshes (groups 'u2_*'), its own extractor and
    shutter, and the trays whose slot is in it (vlm.SLOT_SHUTTLE). fetch/store work on the tray's own Shuttle."""

    def __init__(self, sc, data, highlight=None):
        self.unit = {}
        self.other = dict(lift_z=A.LIFT_HOME, shutter=0.0)
        self.active = 1
        self.focus = None
        super().__init__(sc, data, robot=False, highlight=highlight)
        # round 11 (orchestrator): Shuttle 2's tray supports follow its own slot plan (vlm.support_parts), drawn only
        # where its trays rest inside a slot; data["vlm"]'s are Shuttle 1's
        sup2 = {}
        for name, (shape, mat, grp) in V.support_parts(2).items():
            if hasattr(shape, "vals"):
                shape = shape.val() if len(shape.vals()) == 1 else line.I.cq.Compound.makeCompound(shape.vals())
            sup2[name] = lab._entry(lab.to_mesh(shape, 2.0), mat, grp)["mesh"]
        for name, e in data["vlm"].items():
            kw = {}
            if e["material"] in ("vlm_skin", "vlm_bay"):
                kw = dict(specular=0.05, ambient=0.35)
            if e["material"] == "vlm_led":
                kw = dict(ambient=0.9, diffuse=0.2)
            g = f"u2_{e['group']}"
            sc.add(f"u2/{name}", sup2.get(name, e["mesh"]), e["color"], g, opacity=e["opacity"], **kw)
            sc.gmat[g] = T((X2, 0, 0))
            if e["material"] in A.GHOST:
                self.ghost[f"u2/{name}"] = A.GHOST[e["material"]]
        self.skin(getattr(self, "_skin_f", 0.0))(1.0)
        self.apply_state()

    def use(self, unit):
        if unit != self.active:
            cur = dict(lift_z=self.lift_z, shutter=self.shutter)
            self.lift_z, self.shutter = self.other["lift_z"], self.other["shutter"]
            self.other, self.active = cur, unit

    def apply_state(self):
        sc = self.sc
        for k, (y, z) in self.tray.items():
            sc.gmat[f"tray_{k}"] = T((X2 if self.unit.get(k, 1) == 2 else 0.0, y, z))
            on = self.where[k] is not None
            sc.color[f"tray {k} lamp"] = A.GREEN if on else A.OFF
            sc.ambient[f"tray {k} lamp"] = 0.9 if on else 0.2
        mine, other = (self.lift_z, self.shutter), (self.other["lift_z"], self.other["shutter"])
        states = {1: mine if self.active == 1 else other, 2: other if self.active == 1 else mine}
        for unit, pre, x in ((1, "", 0.0), (2, "u2_", X2)):
            z, s = states[unit]
            sc.gmat[f"{pre}lift"] = T((x, 0, z))
            sc.gmat[f"{pre}belts"] = T((x, 0, z + 40)) @ S((1, 1, max(1.0, A.Z_BELT_TOP - (z + 40))))
            sc.gmat[f"{pre}shutter"] = T((x, 0, s * (V.Z_OPEN_TOP - V.Z_SILL + 10)))
        if self.robot is not None and self.robot.held is not None:     # animate.lab_scene's docked arm
            self.robot.set()
        self.gauges()

    def gauges(self):
        """The focused tray's state and Shuttle, then the scene's own status lines (extra_gauges: empty in the set-up
        movie; animate.workflow's arm, doser, load cell and pipette)."""
        extra = list(getattr(self, "extra_gauges", []) or [])
        if not self.show_gauges or (self.focus is None and not extra):
            self.sc.gauges = []
            return
        g = []
        if self.focus is not None:
            k = self.focus
            w = self.where[k]
            pw = "passive, no power" if k in PASSIVE else "powered"
            state = ("moving" if k in PASSIVE else "moving, unpowered") if w is None else (
                f"at the opening, {pw}" if w == "open" else f"stored ({w}), {pw}")
            g = [(f"Tray {k}", state), ("Shuttle", str(self.unit.get(k, 1)))]
        self.sc.gauges = g + extra

    def fetch(self, k, label, caption, fast=1.0, cam=None, hold=0.4, mint=0.6):
        """animate.Lab.fetch on tray k's own Shuttle, to its opening; mint: the shortest lift move (s)."""
        self.use(self.unit.get(k, 1))
        self.focus = k
        sc = self.sc
        ys, zs = V.SLOTS[self.where[k]]
        yt, zt = V.SLOTS["open"]
        if abs(self.lift_z - zs) > 1:
            sc.step(label, caption, max(mint, abs(self.lift_z - zs) / 1333 * fast), self.lift_to(zs), hold=0.1,
                    cam_to=cam)
            cam = None
        self.where[k] = None
        self.apply_state()
        sc.step(label, caption, 2.2 * fast, self.slide(k, 0.0), hold=0.1, cam_to=cam)
        sc.step(label, caption, max(mint, abs(zs - zt) / 1333 * fast), self.lift_to(zt, carry=k), hold=0.1)
        sc.step(label, caption, 0.7 * fast, self.shut(1.0), hold=0.0)
        sc.step(label, caption, 2.2 * fast, self.slide(k, yt), hold=0.0)
        sc.step(label, caption, 0.7 * fast, self.shut(0.0), hold=0.0)
        self.where[k] = "open"
        self.apply_state()
        sc.snap(max(1, int(round(hold * FPS))))

    def store(self, k, label, caption, fast=1.0, cam=None, hold=0.3, mint=0.6):
        """animate.Lab.store on tray k's own Shuttle."""
        self.use(self.unit.get(k, 1))
        self.focus = k
        self.where[k] = None
        self.apply_state()
        ys, zs = V.SLOTS[A.HOME[k]]
        sc = self.sc
        sc.step(label, caption, 0.7 * fast, self.shut(1.0), hold=0.0, cam_to=cam)
        sc.step(label, caption, 2.2 * fast, self.slide(k, 0.0), hold=0.0)
        sc.step(label, caption, 0.7 * fast, self.shut(0.0), hold=0.1)
        sc.step(label, caption, max(mint, abs(self.lift_z - zs) / 1333 * fast), self.lift_to(zs, carry=k), hold=0.1)
        sc.step(label, caption, 2.2 * fast, self.slide(k, ys), hold=0.0)
        self.where[k] = A.HOME[k]
        self.apply_state()
        sc.snap(max(1, int(round(hold * FPS))))


def add_tray(sc: Scene, L: TwoLab, k: str):
    """Tray k in its slot (TRAYS), with its dock plate and its tray lines (services.py) riding on it. A passive tray
    (PASSIVE) is the bare pan: no socket, power strip or lamp, no plate, no lines."""
    import services
    slot, role = TRAYS[k]
    passive = k in PASSIVE
    V.TRAYS.setdefault(k, dict(kind="extra", role=role))
    A.HOME[k], A.ROLE[k] = slot, role
    L.unit[k] = V.SLOT_SHUTTLE[slot]
    if f"tray_{k}" not in {g for g in sc.group_of.values()}:
        for name, (shape, mat, group) in {**V.tray(k), **V.lamp(k)}.items():
            if passive and name != f"tray {k}":
                continue
            if hasattr(shape, "vals"):
                shape = shape.val() if len(shape.vals()) == 1 else line.I.cq.Compound.makeCompound(shape.vals())
            e = lab._entry(lab.to_mesh(shape, 2.0), mat, group)
            sc.add(name, e["mesh"], e["color"], group, opacity=e["opacity"])
    L.tray[k] = [*V.SLOTS[slot]]
    L.where[k] = slot
    L.eq_groups.setdefault(k, [])
    if not passive:
        services.add_tray_services(sc, k, ups=False)


def add_ups(sc: Scene, k: str) -> list:
    """The tray's UPS as its own group, so it can be carried in: round 12, its own real unit (ups.py: sized for what
    the tray must keep alive), with its cradle, markings and status lights (services.add_ups_meshes)."""
    import airgradient
    import services
    g = f"ups_{k}"
    names = services.add_ups_meshes(sc, k, g)
    sc.parent[g] = f"tray_{k}"
    # round 14 (PR #318: "Each tray should have an airgradient"): the tray's AirGradient ONE stands on its UPS on a
    # printed riser (airgradient.py), so it goes on with the UPS; tray_parts checks it as a part of its own
    names += airgradient.add_to_tray(sc, k, parent=g)
    return names


def add_cams(sc: Scene, k: str) -> list[str]:
    """The tray's stream camera rigs: services.TRAY_CAMS, or CAMS for the trays it doesn't cover. -> post groups."""
    import services
    if services.TRAY_CAMS.get(k):
        return services.add_tray_cameras(sc, k)
    if k not in CAMS:
        return []
    layout, h, post_h = CAMS[k]
    h = services.CAM_H if h is None else h
    groups = []
    for i, (x, y, ax, ay, az, *fixed) in enumerate(layout):
        post, pan, tilt = services.rig_pose(x, y, (ax, ay, az), h, post=fixed[0] if fixed else None)
        g = f"cam_{k}{i}"
        services._add_rig(sc, g, f"tray_{k}", T((x, y, V.T_FLOOR)), post, h, pan, tilt,
                          post_h=post_h or services.POST_H)
        groups.append(g)
    return groups


def group_names(sc: Scene, prefix: str) -> list[str]:
    return [n for n, g in sc.group_of.items() if g == prefix or g.startswith(prefix)]


# ================================================================================================ the floor
class Floor(W.Floor):
    """warehouse.Floor on FLOOR_PLAN, plus the second Shuttle's dock and the sieving cell's bench; no dock or target
    for the machines in NO_DOCK."""

    def _tape(self):
        held = {k: W.STATIONS.pop(k) for k in list(W.STATIONS) if k in NO_DOCK}   # they come last: no tag id shifts
        try:
            super()._tape()
        finally:
            W.STATIONS.update(held)
        # round 15: a dock that reads another's post (SHARED_POST) gets no post of its own. warehouse.Floor._tape drew
        # one for every dock, so the posts are drawn again here without those, each cube keeping its tag id
        sc, posts, blacks, whites = self.sc, [], [], []
        for ident, key in enumerate(k for k in W.STATIONS if k not in NO_DOCK):
            if key in SHARED_POST or (key not in ("vlm", "repowder") and key not in self.groups):
                continue
            tx, ty = W.target_xy(key)
            posts.append(pv.Cylinder(center=(tx, ty, W.TARGET_Z / 2), direction=(0, 0, 1), radius=25,
                                     height=W.TARGET_Z, resolution=20).triangulate())
            posts.append(W._box(tx - 150, ty - 150, 0, tx + 150, ty + 150, 12))
            b, w = W.tag(ident=ident)
            blacks.append(b.translate((tx, ty, W.TARGET_Z), inplace=False))
            whites.append(w.translate((tx, ty, W.TARGET_Z), inplace=False))
        sc.set_mesh("target posts", W._merge(posts).compute_normals(split_vertices=True, feature_angle=30.0))
        sc.set_mesh("target black", W._merge(blacks))
        sc.set_mesh("target white", W._merge(whites))

    def _stations(self):
        super()._stations()
        sc = self.sc
        self.groups["vlm2"] = []
        self.where["vlm2"] = np.array([X2, W.Y_FACE_N, V.UNIT_H])
        b = SIEVE_BENCH
        x0, x1, y0, y1 = b["x"] - b["w"] / 2, b["x"] + b["w"] / 2, W.Y_FACE_N, W.Y_FACE_N + b["d"]
        sc.add("sieve_cell/top", W._box(x0, y0, b["h"] - 30, x1, y1, b["h"]), (0.28, 0.29, 0.31), "sieve_cell",
               specular=0.2)
        sc.add("sieve_cell/legs", W._merge([W._box(x - 20, y - 20, 0, x + 20, y + 20, b["h"] - 30)
                                            for x in (x0 + 30, x1 - 30) for y in (y0 + 30, y1 - 30)]),
               (0.66, 0.67, 0.70), "sieve_cell", specular=0.4)
        try:
            import sieve_station as SS
            for name, (mesh, col, spec, op) in SS.enclosure_parts(b["w"], b["d"], b["encl_h"]).items():
                sc.add(f"sieve_cell/encl {name}", mesh.translate((b["x"], (y0 + y1) / 2, b["h"]), inplace=False),
                       col, "sieve_cell", opacity=op, specular=spec)
        except Exception as e:                       # noqa: BLE001  (the enclosure is a nicety)
            print("setup_lab: no sieving-cell enclosure:", e, flush=True)
        names = sc.members("sieve_cell")
        if "sieve" in self.idata:
            inst, ents = self.idata["sieve"]
            bb = inst.bbox()
            at = T((b["x"] + 11.5, W.Y_FACE_N + 60.0 - bb[2], b["h"] - bb[4]))
            rig = tour.Rig(self.sc, inst, ents, "wh_sieve:", at=at)
            for piece in [pc for pc in rig.names if pc in inst.props]:
                for nm in rig.names.pop(piece):
                    sc.alpha[nm] = 0.0
            self.rigs["sieve_cell"] = rig
            names += rig.all_names()
        self.groups["sieve_cell"] = names
        self.where["sieve_cell"] = np.array([b["x"], W.Y_FACE_N + 300, b["h"] + b["encl_h"]])
        # round 15 (#303: one complete lab in every whole-lab clip): the chemical waste station (PR #371, notes/waste.md)
        # in the ducted fume hood, in the hood's own frame (waste_station.FH is instruments_r7's hood), so it comes in
        # with it. VLAB_WASTE=0 leaves it out.
        if _on("VLAB_WASTE") and "fumehood" in self.rigs:
            for nm, (mesh, col, op) in waste_parts().items():
                sc.add(f"waste/{nm}", mesh, col, "waste", opacity=op, specular=0.2)
            sc.parent["waste"] = "wh_fumehood:body"
            sc.gmat["waste"] = np.eye(4)
            self.groups["fumehood"] = self.groups["fumehood"] + sc.members("waste")
        # round 16 (PR #371's check: the atomizer cell's powder waste was on no floor): the powder point (powder_point.py:
        # the two 118EXPs on their station post, a grounded pail per alloy family, the Solid Material bucket, the sand
        # can for filters, the area sign), behind the rePowder's fire point. World meshes in the rePowder's floor group,
        # so the set-up movie fades it in with the machine; not under the machine's root, which the movie lowers 80 mm
        # as it sets it down (the station's drop cord rode 50 mm into the cable tray above: the lead's audit, round
        # 16); machine_rects gives it its own plan rectangle. VLAB_POWDER_POINT=0 leaves it out.
        if _on("VLAB_POWDER_POINT") and "repowder" in self.groups and "repowder" in sc.gmat:
            import powder_point as PP
            for nm, (mesh, col, op) in PP.parts().items():
                sc.add(f"powder_point/{nm}", mesh, col, "powder_point", opacity=op, specular=0.3)
            sc.gmat["powder_point"] = np.eye(4)
            self.groups["repowder"] = self.groups["repowder"] + sc.members("powder_point")
        # round 15: floor-cleaning unit 3's charger (PR #369, floor_cleaning.BAY: a third MiR Charge 48V in the south
        # row, 1.6 m west of unit 1's, outside every powder zone), drawn as warehouse.Floor._chargers draws the others;
        # unit 3 itself is built in build(). VLAB_UNIT3=0 leaves both out.
        if _on("VLAB_UNIT3"):
            import floor_cleaning as FC
            x3, g = (FC.BAY["charger"][0] + FC.BAY["charger"][1]) / 2, "charger2"
            for nm, (mesh, col) in W.charger_mesh().items():
                sc.add(f"{g}/{nm}", mesh, col, g, **(dict(ambient=0.8) if "led" in nm else {}))
            sc.gmat[g] = T((x3, W.Y_FACE_S + (W.CHARGER["D_plate"] - W.CHARGER["D"]), 0))
            bay = W.tape_rect(x3, W.Y_FACE_S + 20.0 + P.MIR["L"] / 2, P.MIR["W"] + 140, P.MIR["L"] + 140, t=50.0)
            sc.add(f"{g}/bay tape", bay, W.TAPE_W, f"{g}_tape", specular=0.0, ambient=0.5)
        # round 16: the cup-and-plug machining cell (PR #373) south of the south row (FLOOR_PLAN["machining"], set at
        # import: notes/lab_r16.md). Its parts at rest, merged by colour (machining_cell.lab_parts, about 64,000
        # triangles), in group wh_machining:body, so the set-up movie can set it down as it does the other floor
        # machines; warehouse.Floor._tape gives it its dock tape and post. VLAB_MCELL=0 leaves it out.
        if _on("VLAB_MCELL") and "machining" in FLOOR_PLAN:
            import machining as MA
            import machining_cell as MC
            g = "wh_machining:body"
            for nm, (mesh, col, op) in MC.lab_parts().items():
                sc.add(f"mcell/{nm}", mesh, col, g, opacity=op, specular=0.2)
            sc.gmat[g] = T((MA.FLOOR["x"], MA.FLOOR["y"], 0.0)) @ R((0, 0, 1), MA.FLOOR["turn"])
            self.groups["machining"] = sc.members(g)
            self.where["machining"] = np.array([MA.FLOOR["x"], MA.FLOOR["y"] + MC.FRONT_Y - 300.0, 1842.0])
            W.NAMES.setdefault("machining", "cup-and-plug machining cell")


def _on(flag: str) -> bool:
    """A round-15 floor item's switch: on unless the environment sets it to 0."""
    return os.environ.get(flag, "1") != "0"


def waste_parts() -> dict:
    """What of the waste station (waste_station.py) shows on the lab's fume hood: {name: (mesh, rgb, opacity)} in the
    hood's own frame. Its two base cabinets' doors (solvent yellow, acid blue) with their bands, 2 mm in front of the
    hood's own doors (instruments_r7: yf + 38), and the intake tray, the delivered bottle, the empties and the etch on
    the work surface, merged by colour. The cabinets' contents stay out: behind opaque doors they'd only cost triangles."""
    import waste_station as WS
    out, gap = {}, 10.0
    for (x0, x1), door_c, band_c, name in (((-WS.XW, -gap / 2), WS.YELLOW, WS.RED, "solvent"),
                                           ((gap / 2, WS.XW), WS.ACIDBLUE, (0.95, 0.95, 0.95), "acid")):
        out[f"{name} cabinet doors"] = (WS.box(x0 + 8, WS.YF + 33, 50, x1 - 8, WS.YF + 36, WS.FH["cab"] - 40), door_c, 1.0)
        out[f"{name} warning band"] = (WS.box(x0 + 60, WS.YF + 31, WS.FH["cab"] - 160, x1 - 60, WS.YF + 33,
                                              WS.FH["cab"] - 100), band_c, 1.0)
    by: dict = {}
    for _, m, c, op in WS.work_surface()[0]:
        by.setdefault((tuple(float(v) for v in c), float(op)), []).append(m)
    for i, ((c, op), ms) in enumerate(by.items()):
        out[f"surface {i}"] = (W._merge(ms), c, op)
    return out


def footprints(sc: Scene, F: Floor) -> pv.PolyData:
    """Tape round every floor machine's footprint, from where it will stand."""
    out = []
    for key, (x0, x1, y0, y1) in machine_rects(sc, F).items():
        if key.startswith("charger") or key == "powder_point":     # its tape would run under the fire point's units
            continue
        out.append(W.tape_rect((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0 + 160, y1 - y0 + 160, t=50.0))
    return W._merge(out)


def _bounds_of(sc: Scene, names, M_inv=None):
    """(x0, x1, y0, y1, z0, z1) of the actors `names` as placed now, in the frame M_inv maps to (world if None)."""
    lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
    for n in names:
        a = sc.actors.get(n)
        if a is None or sc.alpha.get(n, 1.0) <= 0.0 or sc.base_alpha.get(n, 1.0) <= 0.0:
            continue
        b = a.GetMapper().GetInput().GetBounds()
        if b[0] > b[1]:
            continue
        c = np.array([[x, y, z, 1.0] for x in b[:2] for y in b[2:4] for z in b[4:]])
        M = sc.world(sc.group_of[n])
        if M_inv is not None:
            M = M_inv @ M
        p = (c @ M.T)[:, :3]
        lo, hi = np.minimum(lo, p.min(0)), np.maximum(hi, p.max(0))
    return (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]) if np.isfinite(lo).all() else None


def machine_rects(sc: Scene, F: Floor) -> dict:
    """Plan rectangles (x0, x1, y0, y1) of everything that stands on the floor: the machines, the two Shuttles, the
    sieving cell, the chargers."""
    out = {}
    for key, names in F.groups.items():
        if key in ("tape", "docks", "racking", "chargers", "vlm", "vlm2") or not names:
            continue
        # round 16: the powder point rides in the rePowder's group (Floor._stations) but is measured on its own below
        bb = _bounds_of(sc, [n for n in names if sc.base_alpha.get(n, 1.0) > 0.0
                             and sc.group_of.get(n) != "powder_point"])
        if bb is not None:
            out[key] = bb[:4]
    if sc.members("powder_point"):
        bb = _bounds_of(sc, sc.members("powder_point"))
        if bb is not None:
            out["powder_point"] = bb[:4]
    if "repowder" not in out:
        bb = _bounds_of(sc, sc.members("repowder"))
        if bb is not None:
            out["repowder"] = bb[:4]
    xo, yo = V.UNIT_W / 2 + V.SKIN, V.UNIT_D / 2 + V.SKIN
    out["vlm"] = (-xo, xo, -yo, yo)
    out["vlm2"] = (X2 - xo, X2 + xo, -yo, yo)
    for i, x in enumerate(W.CHARGERS):
        out[f"charger{i}"] = (x - W.CHARGER["W"] / 2, x + W.CHARGER["W"] / 2, W.Y_FACE_S - W.CHARGER["D_plate"],
                              W.Y_FACE_S)
    if "charger2" in sc.gmat:                   # round 15: unit 3's (floor_cleaning.BAY)
        x = sc.gmat["charger2"][0, 3]
        out["charger2"] = (x - W.CHARGER["W"] / 2, x + W.CHARGER["W"] / 2, W.Y_FACE_S - W.CHARGER["D_plate"], W.Y_FACE_S)
    return out


# ================================================================================================ utilities
def junction_box(x, y, z, face):
    """A grey electrical junction box at the end of a power and network drop: two sockets and a network port on its
    face. face = -1: the face looks to -y (the north row), +1 to +y. -> {name: (mesh, colour)}."""
    w, d, h = 240.0, 120.0, 180.0
    body = W._box(x - w / 2, y - d / 2, z - h, x + w / 2, y + d / 2, z)
    yf = y + face * d / 2
    sockets, holes, port = [], [], []
    for sx in (-60.0, 30.0):
        sockets.append(W._box(x + sx - 32, yf, z - h + 60, x + sx + 32, yf + face * 6, z - h + 130))
        for dx in (-9.0, 9.0):
            holes.append(W._box(x + sx + dx - 3, yf + face * 6, z - h + 98, x + sx + dx + 3, yf + face * 7.5,
                                z - h + 110))
        holes.append(W._box(x + sx - 4, yf + face * 6, z - h + 74, x + sx + 4, yf + face * 7.5, z - h + 84))
    port.append(W._box(x + 80, yf, z - h + 80, x + 106, yf + face * 6, z - h + 104))
    return {"junction boxes": (body, (0.62, 0.64, 0.66)), "box sockets": (W._merge(sockets), (0.93, 0.93, 0.92)),
            "socket holes": (W._merge(holes), (0.10, 0.10, 0.11)), "network ports": (W._merge(port), (0.15, 0.40, 0.85))}


# Round 14: the building and its services for 9150 mm Shuttles (vlm.UNIT_H; Sterling, PR #318, 2026-11-20: taller VLMs
# "affect many other things, like the overhead facilities (power, etc.)"). Until round 13 the north cable tray ran at
# 4.3 m "over the north row, above the VLM's 3950 mm roof", the argon line beside it, the VLMs' feeds and the docks'
# supply line came down onto the Shuttles' roofs, and the hangers and the fume hood's duct stopped at 6 m. With 9.15 m
# units all of that ran through them. Now the north tray and the argon line jog round the back of both Shuttles, the
# VLMs' 208 V feeds drop to a disconnect on each one's back, the docks' supply goes into each Shuttle's right-hand side
# cavity (where its risers are) at 2.6 m, and the building is PR #344's 36 ft high bay: roof steel at 10.97 m, the
# hangers and the duct up to it, LED high-bay lights at 10.2 m. The routes are ours, drawn to read, not a design.
Z_CEIL = 10970.0                 # PR #344: the 36 ft buildings near BYU; a 9.15 m Shuttle needs 31.5 ft clear under
#                                  NFPA 13's 18 in, 33 ft under ESFR (notes/kardex_height.md)
LIGHT = dict(z=10200.0, d=330.0, h=150.0, pitch=(4000.0, 3600.0), lm=24000.0, w=150.0)   # UFO high bays (ours)


def _path_tray(path, z, w=300.0, h=100.0):
    """A ladder-less cable tray (a sheet with two side walls) along an axis-aligned plan path at height z."""
    out = []
    for (xa, ya), (xb, yb) in zip(path[:-1], path[1:]):
        if abs(ya - yb) < 1e-6:
            x0, x1 = sorted((xa, xb))
            x0, x1 = x0 - w / 2, x1 + w / 2
            out += [W._box(x0, ya - w / 2, z, x1, ya + w / 2, z + 12), W._box(x0, ya - w / 2, z, x1, ya - w / 2 + 12,
                                                                               z + h),
                    W._box(x0, ya + w / 2 - 12, z, x1, ya + w / 2, z + h)]
        else:
            y0, y1 = sorted((ya, yb))
            out += [W._box(xa - w / 2, y0, z, xa + w / 2, y1, z + 12), W._box(xa - w / 2, y0, z, xa - w / 2 + 12, y1,
                                                                               z + h),
                    W._box(xa + w / 2 - 12, y0, z, xa + w / 2, y1, z + h)]
    return W._merge(out)


def _pipe(pts, r=14.0, res=14):
    """A pipe along a polyline."""
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        a, b = np.asarray(a, float), np.asarray(b, float)
        d = b - a
        L_ = float(np.linalg.norm(d))
        if L_ < 1e-6:
            continue
        out.append(pv.Cylinder(center=(a + b) / 2, direction=d / L_, radius=r, height=L_ + r * 0.5,
                               resolution=res).triangulate())
    return W._merge(out)


def _along(path, step):
    """Points every `step` mm along an axis-aligned plan path."""
    pts = []
    for (xa, ya), (xb, yb) in zip(path[:-1], path[1:]):
        L_ = math.hypot(xb - xa, yb - ya)
        for t in np.arange(0.0, L_, step):
            pts.append((xa + (xb - xa) * t / L_, ya + (yb - ya) * t / L_))
    return pts


def utilities(hood=None) -> tuple[dict, tuple]:
    """Cable trays over both rows with a drop to each station ending in a grey junction box (sockets and a network
    port) and an AirGradient ONE on the box (round 14), a network cable in each tray, an argon line from a cylinder
    manifold to the gas users, the fume hood's duct, and (round 14) the high bay's lights. Layout choices, drawn to
    read, not a design. -> ({name: (mesh, colour)}, a junction box's label point)."""
    import airgradient as AGm
    zn, yn = 4300.0, W.Y_FACE_N + 700.0          # over the north row
    zs, ys = 3200.0, W.Y_FACE_S - 600.0
    xs = (-9200.0, 11000.0)
    yb = V.UNIT_D / 2 + V.SKIN + 250.0           # round 14: behind both Shuttles (their backs at 1562)
    xa, xb = -V.UNIT_W / 2 - V.SKIN - 335.0, X2 + V.UNIT_W / 2 + V.SKIN + 335.0     # round them, 335 mm clear
    north_path = [(xs[0], yn), (xa, yn), (xa, yb), (xb, yb), (xb, yn), (xs[1], yn)]
    south_path = [(xs[0] + 1200, ys), (xs[1], ys)]
    trays = W._merge([_path_tray(north_path, zn), _path_tray(south_path, zs)])
    hangers = W._merge([W._box(x - 15, y - 15, z + 100, x + 15, y + 15, Z_CEIL)
                        for path, z in ((north_path, zn), (south_path, zs)) for x, y in _along(path, 3000.0)])
    net = W._merge([_pipe([(x, y + (60 if abs(y - yn) < 1 or abs(y - ys) < 1 else 0), z + 35) for x, y in path],
                          18.0, 16) for path, z in ((north_path, zn), (south_path, zs))])
    drops, parts = [], {}
    north = {"glovebox": -7300.0, "repowder": -3640.0, "sieve_cell": -1700.0, "vlm": 900.0, "vlm2": X2 + 900.0,
             "aconity": 7300.0, "packaging": 10050.0}
    south = {"instron_floor": -6400.0, "instron_small": -4300.0, "chargers": -900.0, "fumehood": 900.0,
             "ded": 3900.0, "wire_edm": 6600.0}

    def add(d):
        for k, (m, c) in d.items():
            parts.setdefault(k, ([], c))[0].append(m)

    def add_ag(x, y, z, face):                  # round 14: the station's AirGradient ONE on its junction box
        for mat, mesh in AGm.at_junction_box(x, y, z, face).items():
            parts.setdefault(f"AirGradient {mat}", ([], AGm.colour(mat)))[0].append(mesh)
    label = None
    yv = V.UNIT_D / 2 + V.SKIN                   # the Shuttles' backs
    for key, x in north.items():
        if key.startswith("vlm"):                # round 14: down behind the Shuttle to a disconnect on its back
            z_end = 2650.0
            drops.append(_pipe([(x, yb, zn), (x, yb, z_end + 150.0), (x, yv + 140.0, z_end + 150.0)], 22.0, 16))
            add({"junction boxes": (W._box(x - 160, yv, z_end - 260, x + 160, yv + 140, z_end + 200),
                                    (0.62, 0.64, 0.66))})
            continue
        z_end = 2500.0
        drops.append(pv.Cylinder(center=(x, yn - 60, (zn + z_end) / 2), direction=(0, 0, 1), radius=22,
                                 height=zn - z_end, resolution=16).triangulate())
        add(junction_box(x, yn - 60, z_end, -1))
        add_ag(x, yn - 60, z_end, -1)
    # round 11: the box at the 68FM-100 hung at 1720-1900 mm, inside the frame's crosshead (1610-1810 at rest in
    # r8_test's model, up to the top plate at 2137 over its travel; chapter 5 found it): it goes over the frame's top
    # (2287 mm), 63 mm clear, at 2350-2530 mm, the machine's cable up its back
    z_box = {"instron_floor": 2530.0}
    for key, x in south.items():
        ze = z_box.get(key, 1900.0)
        drops.append(pv.Cylinder(center=(x, ys + 60, (zs + ze) / 2), direction=(0, 0, 1), radius=22,
                                 height=zs - ze, resolution=16).triangulate())
        add(junction_box(x, ys + 60, ze, +1))
        add_ag(x, ys + 60, ze, +1)
        if key == "instron_small":
            label = (x, ys + 60, 1800.0)
    # the argon line: from the cylinders at the west end along the north tray (beside it, 230 mm behind, 150 mm under
    # its floor), round the Shuttles with it, a drop to each gas user; the DED's down the west end to the south tray
    gas_users = [-7300.0, -3640.0, 7300.0]
    gx0 = xs[0] - 400
    za = zn - 150
    ar_path = [(gx0, yn + 230), (xa + 230, yn + 230), (xa + 230, yb + 230), (xb + 230, yb + 230), (xb + 230, yn + 230),
               (gas_users[-1] + 200, yn + 230)]
    ar = [_pipe([(x, y, za) for x, y in ar_path]), _pipe([(gx0, yn + 230, 0.0), (gx0, yn + 230, za)])]
    for x in gas_users:
        ar.append(_pipe([(x + 200, yn + 230, za), (x + 200, yn + 230, 1800.0)], 12.0))
    xd = FLOOR_PLAN["ded"][0]                    # the DED's argon: down the south tray
    ar.append(_pipe([(gx0, yn + 230, zs - 150), (gx0, ys - 200, zs - 150), (xd + 200, ys - 200, zs - 150),
                     (xd + 200, ys - 200, 1800.0)]))
    cyl = [pv.Cylinder(center=(gx0 - 300 + 260 * i, yn + 700, 750), direction=(0, 0, 1), radius=115, height=1500,
                       resolution=24).triangulate() for i in range(4)]
    # the ducted hood's exhaust: up from its top, behind the south cable tray, through the roof (a 180 mm duct; a layout
    # choice). hood: the hood's world bounds
    duct = None
    if hood is not None:
        z0 = hood[5]
        duct = pv.Cylinder(center=((hood[0] + hood[1]) / 2, hood[2] + 110.0, (z0 + Z_CEIL + 300.0) / 2),
                           direction=(0, 0, 1), radius=90, height=Z_CEIL + 300.0 - z0, resolution=28).triangulate()
    # round 10: what the trays' couplings carry besides mains and Ethernet (services.py: compressed air, N2, chilled
    # water) comes from units at the back of the 800 mm gap between the Shuttles, where no MiR turns (they turn at the
    # front): the N2 generator (Parker Balston UHPN2-1100, 305 x 406 x 889 mm, services.SOURCES["n2"]), an oil-free
    # compressor for it and for the docks' air (our size), and the chiller (ThermoFlex 900, size not found: not to
    # size). Round 14: their line goes into each Shuttle's right-hand side cavity at 2.6 m, where the risers run, not
    # over the roofs: Shuttle 1's straight across the gap, Shuttle 2's round its back.
    xg = X2 / 2                                  # the gap's middle: 1815
    units_ = {"N2 generator": (305.0, 406.0, 889.0, 200.0, (0.86, 0.87, 0.88)),
              "air compressor": (450.0, 450.0, 650.0, 660.0, (0.30, 0.45, 0.62)),
              "chiller": (420.0, 600.0, 700.0, 1160.0, (0.80, 0.81, 0.83))}
    for nm, (w, d, h, y0, col) in units_.items():
        out_units = W._box(xg - w / 2, y0, 0.0, xg + w / 2, y0 + d, h)
        parts.setdefault(nm, ([], col))[0].append(out_units)
    xr1 = V.UNIT_W / 2 + V.SKIN                  # Shuttle 1's right side, Shuttle 2's
    xr2 = X2 + V.UNIT_W / 2 + V.SKIN
    zsv = 2600.0
    svc = [_pipe([(xg, 900.0, 950.0), (xg, 900.0, zsv), (xr1 - 20.0, 900.0, zsv)], 30.0),
           _pipe([(xg, 900.0, zsv), (xg, yv + 120.0, zsv), (xr2 + 220.0, yv + 120.0, zsv), (xr2 + 220.0, 900.0, zsv),
                  (xr2 - 20.0, 900.0, zsv)], 30.0)]
    parts.setdefault("dock supply line", ([], (0.55, 0.66, 0.74)))[0].extend(svc)
    # round 14: LED high-bay lights (UFO fixtures, 24,000 lm, 150 W: a common size, ours) on a 4.0 x 3.6 m grid at
    # 10.2 m, each on a hook from the roof steel
    lights, hooks = [], []
    for x in np.arange(-8000.0, 10001.0, LIGHT["pitch"][0]):
        for y in np.arange(1800.0, -9001.0, -LIGHT["pitch"][1]):
            z = LIGHT["z"]
            lights.append(pv.Cylinder(center=(x, y, z), direction=(0, 0, 1), radius=LIGHT["d"] / 2,
                                      height=LIGHT["h"], resolution=28).triangulate())
            hooks.append(W._box(x - 6, y - 6, z + LIGHT["h"] / 2, x + 6, y + 6, Z_CEIL))
    out = {"cable trays": (trays, (0.70, 0.72, 0.74)), "tray hangers": (hangers, (0.55, 0.57, 0.60)),
           "network cable": (net, (0.15, 0.40, 0.85)), "power drops": (W._merge(drops), (0.30, 0.31, 0.33)),
           "argon line": (W._merge(ar), (0.25, 0.60, 0.35)), "argon cylinders": (W._merge(cyl), (0.30, 0.55, 0.36)),
           "hood duct": (duct, (0.78, 0.79, 0.81)), "high-bay lights": (W._merge(lights), (0.86, 0.87, 0.85)),
           "light hooks": (W._merge(hooks), (0.40, 0.41, 0.43))}
    for k, (ms, c) in parts.items():
        out[k] = (W._merge(ms), c)
    return {k: v for k, v in out.items() if v[0] is not None}, label


# ------------------------------------------------------------------------------------------------ loading the trays
# Round 10 (Sterling, PR #318: "the entire lab getting set up from scratch as well, including installation of arms,
# loading of all equipment onto the trays"): what goes on a tray mostly weighs 15-110 kg (MASS_KG), over the arm's
# 12.5 kg and over what one person should lift (NIOSH's lifting equation: 23 kg at best). So the set-up movie puts a
# scissor lift table in front of the opening being loaded, its deck 20 mm over the presented tray's floor, and each
# machine slides from the deck across the access table's lip onto the tray. A 2440 x 915 mm deck (96 x 36 in, a common
# size) rated 1000 kg is our assumption, not a quote. Kardex's alternative for the heaviest loads is its "tray
# extraction for forklift operation" option (Shuttle XP brochure, kardex_tall.SOURCES["xp"]), not drawn.
LIFT_TABLE = dict(w=2440.0, d=915.0, deck_t=50.0, base_h=90.0)
LIFT_DECK_Z = V.Z_OPEN + V.T_FLOOR + 20.0      # the items slide 20 mm over the tray floor (rig_in, animate.item_in)
LIFT_TABLE_Y = -V.UNIT_D / 2 - V.SKIN - 55.0 - LIFT_TABLE["d"] / 2     # its back edge 5 mm off the cover's 50 mm lip
LIFT_START_Y = LIFT_TABLE_Y + 120.0             # where an item's centre starts on the deck (world y)
# what the trays carry, kg, where a maker or the model's source gives it (published unless marked): how heavy the
# loading is. None: not found. The UPS is Eaton's (services.SOURCES["ups"]).
MASS_KG = {
    "xrf": (108.0, "Bruker S2 PUMA Series 2 with the XY autochanger (out/instruments.json)"),
    "vacuum_press": (95.0, "Specac Atlas Autotouch 15T (vacuum_press.AT)"),
    "xrd": (80.0, "Rigaku MiniFlex 6G (out/instruments.json)"),
    "tensile_h": (78.0, "ZwickRoell zwickiLine Z5.0 TN (out/instruments.json)"),
    "furnace": (60.0, "Nabertherm NAT 15/65 (out/instruments.json)"),
    "sem": (54.0, "Hitachi TM4000PlusII main unit, the pump extra (out/instruments.json)"),
    "cnc": (50.0, "Makera Carvera (out/instruments.json)"),
    "hardness": (43.0, "Mitutoyo HM-220 (out/instruments.json)"),
    "mastersizer": (40.5, "Malvern Mastersizer 3000 30 kg + Aero S 10.5 kg (out/instruments.json)"),
    "ups": (None, "each tray's own unit, 11-37 kg with its batteries (ups.CATALOGUE, ups_mass())"),
    "reflow": (15.0, "Puhui T-962A (REFLOW)"),
    "vhx": (7.2, "Keyence VHX-7000's EA-300 controller alone; the stand and head not found (out/instruments.json)"),
}
MASS_ONE_PERSON = 23.0                         # NIOSH's load constant, kg: the most one person should lift, at best


def _ups_kg() -> str:
    """'11-37 kg': the lightest and heaviest of the trays' UPSs (round 12: each tray its own unit, ups.py)."""
    import ups
    kg = [ups.unit_of(k)["kg"] for k in ups.TRAY_LOADS]
    return f"{min(kg):.0f}-{max(kg):.0f}" if max(kg) - min(kg) >= 1 else f"{kg[0]:.0f}"


def lift_table_parts() -> dict:
    """{name: (mesh, colour)} of a scissor lift table, deck top at z = LIFT_DECK_Z, centred on x = 0, y = 0 (its own
    frame; the long side along x): the deck, two scissor packs each side, the base frame on four castors, the cylinder."""
    w, d, t, hb = LIFT_TABLE["w"], LIFT_TABLE["d"], LIFT_TABLE["deck_t"], LIFT_TABLE["base_h"]
    zt = LIFT_DECK_Z
    deck = W._box(-w / 2, -d / 2, zt - t, w / 2, d / 2, zt)
    base = W._box(-w / 2 + 70, -d / 2 + 40, 60, w / 2 - 70, d / 2 - 40, 60 + hb)
    bars, wheels = [], []
    for xc in (-w / 4, w / 4):                 # two scissor packs, each an X on both long sides
        for y in (-d / 2 + 70, d / 2 - 70):
            for s in (-1, 1):
                p0 = np.array([xc - s * 420.0, y, 60 + hb])
                p1 = np.array([xc + s * 420.0, y, zt - t])
                c = (p0 + p1) / 2
                L_ = float(np.linalg.norm(p1 - p0))
                bars.append(pv.Cylinder(center=c, direction=p1 - p0, radius=22, height=L_,
                                        resolution=10).triangulate())
    cyl = pv.Cylinder(center=(0, 0, (60 + hb + zt - t) / 2 - 80), direction=(0.55, 0, 1), radius=45,
                      height=420, resolution=16).triangulate()
    for x in (-w / 2 + 140, w / 2 - 140):
        for y in (-d / 2 + 100, d / 2 - 100):
            wheels.append(pv.Cylinder(center=(x, y, 50), direction=(0, 1, 0), radius=50, height=40,
                                      resolution=16).triangulate())
    return {"deck": (deck, (0.46, 0.48, 0.51)), "base": (base, (0.25, 0.26, 0.28)),
            "scissors": (W._merge(bars + [cyl]), (0.93, 0.72, 0.12)), "castors": (W._merge(wheels), (0.12, 0.12, 0.13))}


def rig_in(sc: Scene, g, names, out=False, travel=1700.0):
    """A tray item (a group riding on its tray) comes in through the opening onto its place, as animate.item_in."""
    base = sc.gmat[g].copy()

    def up(u):
        v = u if out else 1.0 - u
        sc.gmat[g] = T((0, -travel * v, min(1.0, v * 6) * 20.0)) @ base
        for n in names:
            sc.alpha[n] = 1.0 if v < 0.7 else max(0.0, 1 - (v - 0.7) / 0.3)
    return up


def stagger(fs, overlap=0.45):
    """Run updates one after another within one step, each over `overlap` of it."""
    n = len(fs)

    def up(u):
        for i, f in enumerate(fs):
            t0 = 0.0 if n == 1 else i * (1.0 - overlap) / (n - 1)
            f(window(u, t0, t0 + overlap if n > 1 else 1.0))
    return up


# ================================================================================================ build
def build(data, idata, mp4=True, name="setup_lab", title=TITLE, highlight=None):
    merge_r8()
    use_floor_plan()
    sc = Scene(name, title, gif=False, mp4=mp4)              # fit: no encoder, so it leaves the MP4 alone
    sc.cam = list(CAM_ROOM)
    L = TwoLab(sc, data, highlight=highlight)
    for k in ("A", "B", "C"):
        add_tray(sc, L, k)
    for g in L.eq_groups.get("A", []):                  # round 2's CubXL stays hidden: the corrosion set-up replaces it
        if L.eq_key[g] == "cubxl" and "cubxl_corrosion" in idata:
            for nm in L.eq_names(g):
                sc.alpha[nm] = 0.0
    F = Floor(sc, L, idata)
    for k in ORDER:
        if k not in "ABC":
            add_tray(sc, L, k)
    items, rigs = {k: [] for k in ORDER}, {}
    vp = None
    # VLAB_ONLY_TRAYS=DEFKL: only those trays get their instruments, UPS and cameras (round 8, runner_guard.py). For an
    # ARM_AUDIT=1 pass (the arm can't reach the trays in their slots; a scene with all fifteen loaded holds about 5.5 GB
    # and audits slowly), and for a render whose Shuttles stay clad, where only the tray at the opening shows. Not for a
    # render that shows the Shuttles as open frames (the set-up, the 9:09 clip): they would look half empty (Sterling,
    # 2026-11-05: "In 9:09, suddenly the VLM only has a few things on board"). Unset: every tray.
    only = os.environ.get("VLAB_ONLY_TRAYS")
    for k in ORDER:
        if only is not None and k not in only:
            continue
        for i, (key, x, y, turn) in enumerate(ITEMS.get(k, [])):
            if k in A.LOADS and any(it[0] == key for it in A.LOADS[k]) and key != "cubxl":
                g = next(gg for gg in L.eq_groups[k] if L.eq_key[gg] == key)
                names = L.eq_names(g) + (L.groups("vial", "vial_powder", "vial_liquid") if key == "rack" else [])
                items[k].append((key, g, names, A.NAMES.get(key, key)))
                continue
            if key == "vacuum_press":
                import alloy_press as AP
                import vacuum_press as VPm
                vp = AP.VacPress(sc, f"tray_{k}", (x, y), V.T_FLOOR)
                vp.st["guard"] = 0.0                     # stored with its guard down
                vp.apply()
                names = group_names(sc, "vpress") + group_names(sc, "vp_")
                items[k].append((key, "vpress", names, VPm.AT["model"].split(" (")[0] + ", vacuum press"))
                continue
            if key not in idata:
                print(f"setup_lab: {key} (tray {k}) not loaded: skipped", flush=True)
                continue
            inst, ents = idata[key]
            pre = f"{k}{i}_{key}:"
            rig = tour.Rig(sc, inst, ents, pre, at=placed(inst, x, y, turn), parent=f"tray_{k}")
            for piece in [pc for pc in rig.names if pc in inst.props]:
                for nm in rig.names.pop(piece):
                    sc.alpha[nm] = 0.0
            rigs[pre[:-1]] = rig
            # round 10: a fade piece that starts hidden (v0 = 0: the jar store's tint sleeves, a glow, a powder) is left
            # out of the names the loading fades in, so it stays hidden; it still answers its rig's moves. Round 10's
            # first set-up render showed tray N's and O's jars tinted teal and amber with no legend.
            hid = {nm for pc, ns in rig.names.items() if pc in inst.joints and inst.joints[pc].kind == "fade"
                   and not inst.joints[pc].v0 for nm in ns}
            items[k].append((key, f"{pre}body", [nm for nm in rig.all_names() if nm not in hid], item_label(inst)))
        if k in PASSIVE:                                 # round 11: nothing on it draws power, so no UPS, no cameras
            continue
        ups = add_ups(sc, k)
        items[k].append(("ups", f"ups_{k}", ups, "UPS"))
        for g in add_cams(sc, k):
            items[k].append(("cam", g, group_names(sc, g), "camera"))
    units = [W_unit(sc, i) for i in range(len(W.CHARGERS))]
    # round 15: floor-cleaning unit 3 (PR #369, notes/floor_cleaning.md, option C: a third MiR250 + arm of its own,
    # its orange band) parked on its charger (Floor._stations draws it); not one of `units`, which the clips drive.
    # Its 118EXP vacuums stay on wall power at their station: since round 16 the powder point (Floor._stations).
    F.unit3 = None
    if "charger2" in sc.gmat:
        import floor_cleaning as FC
        F.unit3 = Unit(sc, "unit3", FC.BAY["park"])
        lc, wc, zb = P.MIR["L"] - 80, P.MIR["W"] - 60, P.MIR["H"] + P.CAB_H
        sc.add("unit3/unit 3 band", W._box(-lc / 2 - 1, -wc / 2 - 1, zb - 90, lc / 2 + 1, wc / 2 + 1, zb - 40),
               (0.93, 0.47, 0.13), "unit3_cab")
    util = {}
    hood = _bounds_of(sc, F.groups["fumehood"]) if F.groups.get("fumehood") else None
    umesh, ulabel = utilities(hood)
    for nm, (mesh, col) in umesh.items():
        sc.add(f"util/{nm}", mesh, col, "util", specular=0.2)
        util[nm] = f"util/{nm}"
    # the safety PR (Sterling, PR #318, 2026-11-20: "Class D fire extinguishers at each station"): the fixed Class D
    # units at the powder stations (safety.PLACES: a B570 on a post with its CLASS D signs, the 680Rs, the Super D
    # pails), with the utilities, so the set-up movie brings them in with them. VLAB_CLASS_D=0 leaves them out.
    if os.environ.get("VLAB_CLASS_D", "1") != "0":
        import safety
        for nm, (mesh, col, spec) in safety.floor_meshes().items():
            sc.add(f"util/{nm}", mesh, col, "util", specular=spec)
            util[nm] = f"util/{nm}"
    # the safety PR's other assets (Sterling, PR #379, 2026-11-22: "Do these"): the building's ordinary extinguishers on
    # the racking, a shower and eyewash at the fume hood, the O2 monitors at the argon users and the N2 generator
    # (safety_other.PLACES; the ICP-MS station's come in with the station). VLAB_SAFETY_OTHER=0 leaves them out.
    if os.environ.get("VLAB_SAFETY_OTHER", "1") != "0":
        import safety_other
        for nm, (mesh, col, spec) in safety_other.floor_meshes().items():
            sc.add(f"util/{nm}", mesh, col, "util", specular=spec)
            util[nm] = f"util/{nm}"
    L.apply_state()
    sc.apply()
    sc.add("footprints", footprints(sc, F), W.TAPE_W, "tape", specular=0.0, ambient=0.5)
    return sc, L, F, items, rigs, units, util, ulabel, vp


def add_bay_cams(sc: Scene) -> list[str]:
    """The overhead cameras over each Shuttle's bay (services.py's two units, hung from the bay's roof since round 14,
    and a copy of both at X2). -> their actor names."""
    import services as S
    S.add_bay_camera(sc)
    S.add_bay_camera(sc, x=X2, tag="2")
    return [nm for nm in sc.actors if sc.group_of[nm].startswith(("baycam", "baycamf"))]


def W_unit(sc, i):
    return Unit(sc, f"unit{i}", W.charger_pose(i))


# ================================================================================================ the lab's units
class Unit:
    """A MiR250 + UR10e built so it can be put together: the MiR250, its cabinet (a child group), the UR control box
    (UR10e data sheet: 460 x 449 x 254 mm) inside it, the arm on the cabinet's top plate and the gripper on the arm."""

    def __init__(self, sc: Scene, name: str, pose):
        import robot as RB
        self.sc, self.name, self.pose = sc, name, list(pose)
        cab = f"{name}_cab"
        for nm, (mesh, col) in P.mir250().items():
            # the safety PR's Class D unit hangs on the cabinet's side (safety.mir_mount), so it comes in with it: a
            # group of its own under the cabinet's, so an audit names it
            grp = (f"{name}_classd" if "class D" in nm else
                   cab if ("cabinet" in nm or "e-stop" in nm) else name)
            sc.add(f"{name}/{nm}", mesh, col, grp, **(dict(ambient=0.8) if "light" in nm else {}))
        holder, seat = P.buffer_holder()
        sc.add(f"{name}/holder", holder.translate((*A.BUFFER_LOCAL, P.AMR_TOP - 20), inplace=False), P.RACK_C, cab)
        sc.parent[cab] = name
        sc.gmat[cab] = np.eye(4)
        if any(g == f"{name}_classd" for g in sc.group_of.values()):
            sc.parent[f"{name}_classd"] = cab
            sc.gmat[f"{name}_classd"] = np.eye(4)
        cb = f"{name}_cb"                         # the control box, standing on the MiR's top, inside the cabinet
        H0 = P.MIR["H"]
        box = pv.Box(bounds=(-230, 230, -127, 127, H0 + 5, H0 + 5 + 449)).triangulate()
        sc.add(f"{name}/control box", box, (0.60, 0.62, 0.64), cb)
        sc.add(f"{name}/control box front", pv.Box(bounds=(-200, 200, -129, -127, H0 + 60, H0 + 400)).triangulate(),
               (0.25, 0.27, 0.30), cb)
        sc.parent[cb] = name
        sc.gmat[cb] = np.eye(4)
        self.robot = RB.Robot(sc, A.ROBOT, cab, T((*A.ARM_LOCAL, P.AMR_TOP)), q0=A.PARK_DEG, prefix=f"{name}ur")
        self.set()

    def set(self, pose=None):
        if pose is not None:
            self.pose = list(pose)
        x, y, hd = self.pose
        self.sc.gmat[self.name] = T((x, y, 0)) @ R((0, 0, 1), hd)

    def part_names(self, part):
        sc, nm = self.sc, self.name
        if part == "base":
            return [n for n, g in sc.group_of.items() if g == nm]
        if part == "cabinet":
            return [n for n, g in sc.group_of.items() if g in (f"{nm}_cab", f"{nm}_classd")]
        if part == "control box":
            return [n for n, g in sc.group_of.items() if g == f"{nm}_cb"]
        if part == "arm":
            return [n for n, g in sc.group_of.items() if g.startswith(f"{nm}ur_") and "_gr_" not in g]
        if part == "gripper":
            return [n for n, g in sc.group_of.items() if g.startswith(f"{nm}ur_gr_")]
        raise KeyError(part)

    def all_names(self):
        return [n for p in ("base", "cabinet", "control box", "arm", "gripper") for n in self.part_names(p)]

    def gripper_offset(self, d):
        """Slide the gripper d mm off the flange, along the tool axis (the arm's own set() puts it back)."""
        import ur_arm
        rb = self.robot
        fk = ur_arm.fk(rb.model, rb.q)
        gfk = ur_arm.gripper_fk(rb.close)
        for part in rb.gparts:
            self.sc.gmat[f"{rb.prefix}_gr_{part}"] = fk["tool0"] @ T((0, 0, d)) @ gfk[part]


# ================================================================================================ the movie
def movie(data, idata):
    sc, L, F, items, rigs, units, util, ulabel, vp = build(data, idata)
    import services
    vlm_groups = ["base", "posts", "col_front", "col_rear", "lift_rails", "drive", "lift", "belts", "bay", "console",
                  "shutter", "skin_L", "skin_R", "skin_back", "skin_front", "skin_top"]
    u2 = [f"u2_{g}" for g in vlm_groups]
    trays = list(ORDER)
    tray_groups = [f"tray_{k}" for k in trays]
    eq = [n for k in items for _, _, names, _ in items[k] for n in names]
    floor_keys = [k for k in FLOOR_PLAN if k not in ("vlm", "vlm2") and k in F.groups]
    machines = [n for key in floor_keys for n in F.groups[key]]
    layout = F.groups["tape"] + F.groups["docks"] + ["footprints"] + \
        [n for n, g in sc.group_of.items() if g.startswith("charger") and g.endswith("_tape")]
    chargers = [n for n, g in sc.group_of.items() if g.startswith("charger") and not g.endswith("_tape")]
    unit_names = [n for u in units for n in u.all_names()]
    u3_names = F.unit3.all_names() if F.unit3 is not None else []       # round 15: unit 3, with the second unit
    # round 10: where each item's centre is in its tray (for its start on the lift table), and the two lift tables
    yc_of, ynear_of = {}, {}
    for k in items:
        Mi = np.linalg.inv(sc.world(f"tray_{k}"))
        for key, g, names, _ in items[k]:
            bb = _bounds_of(sc, names, Mi)
            yc_of[(k, g)] = 0.0 if bb is None else (bb[2] + bb[3]) / 2
            ynear_of[(k, g)] = 0.0 if bb is None else bb[2]       # the edge nearest the opening
    tables = {}
    for u, xu in V.SHUTTLE_X.items():
        g = f"lift_table{u}"
        for nm, (mesh, col) in lift_table_parts().items():
            sc.add(f"{g}/{nm}", mesh, col, g, specular=0.3)
        sc.gmat[g] = T((xu, LIFT_TABLE_Y, 0.0))
        tables[u] = sc.members(g)
    A.hide(L, L.groups(*vlm_groups, *u2, *tray_groups) + eq + machines + layout + chargers + unit_names + u3_names +
           list(util.values()) + [n for v in tables.values() for n in v])
    L.skin(0.0)(1.0)
    L.show_gauges = False
    L.apply_state()
    n = 9
    have = set(idata)
    # ------------------------------------------------------------------ 1. the empty bay
    sc.step(f"1/{n}", "An empty bay in a warehouse, about 24 m between the racks on its side walls. Everything that "
            "follows goes into it.", 2.0, None, hold=0.8)
    # ------------------------------------------------------------------ 2. the layout on the floor
    fl = {nm: 1.0 for nm in layout}

    def tape_on(u):
        for nm in fl:
            sc.alpha[nm] = u
    sc.step(f"2/{n}", "The layout goes down in tape first: the 3.0 m aisle, each machine's footprint, and a MiR250 dock "
            "at every front with an AprilTag target on a post. Every dock has room at its open end for a MiR to turn "
            "on the spot; nothing stands in a dock or on the way into one.", 3.0, tape_on, hold=1.8, cam_to=CAM_TOP,
            labels=W.auto(sc, CAM_TOP, [("main aisle, 3.0 m", (-7000, (W.AISLE[0] + W.AISLE[1]) / 2, 0)),
                                         ("two Kardex Shuttles", (X2 / 2, -1000, 0)),
                                         ("dock and AprilTag target", (*W.target_xy("aconity"), W.TARGET_Z)),
                                         ("charger bays", (W.CHARGERS[0], W.Y_FACE_S + 400, 0))]))
    # ------------------------------------------------------------------ 3. utilities
    names_u = list(util.values())

    def util_on(u):
        for i, nm in enumerate(names_u):
            sc.alpha[nm] = window(u, i / (len(names_u) + 1), (i + 2) / (len(names_u) + 1))
    ulbls = [("cable tray: power and network, round the Shuttles' backs", (8000, W.Y_FACE_N + 700, 4400)),
             ("argon cylinders", (-9500, W.Y_FACE_N + 1400, 1500)),
             ("VLM supply, 208 V 3-phase, onto its back", (900, V.UNIT_D / 2 + V.SKIN + 70, 2700)),
             ("N2 generator, compressor, chiller", (X2 / 2, 900.0, 950.0)),
             ("LED high-bay lights at 10.2 m, 36 ft roof", (-4000, -2400, 10200))]
    if ulabel is not None:
        ulbls.append(("power and network drop", ulabel))
    sc.step(f"3/{n}", "Utilities, in a high bay with a 36 ft roof for the 30 ft Shuttles: cable trays over both rows, "
            "round the Shuttles' backs. A drop comes down to every station and ends in a grey junction box with "
            "sockets, a network port and an AirGradient air monitor. 208 V three-phase goes to each VLM (#53), argon "
            "from a cylinder manifold to the glovebox, the rePowder, the Aconity and the DED, and a duct up from the "
            "fume hood. Between the Shuttles, at the back: an N2 generator, a compressor and a chiller for the trays' "
            "couplings. Layout choices, not a design.", 4.6, util_on, hold=2.2, cam_to=CAM_UTIL,
            labels=W.auto(sc, CAM_UTIL, ulbls))
    # ------------------------------------------------------------------ 4. the VLMs
    s = A.slide_in
    sc.step(f"4/{n}", f"Two Kardex Shuttle XP 500s, {V.UNIT_H / 1000:.2f} m (30 ft) tall, go together where their "
            "footprints are taped, 800 mm apart: base frames, posts, storage columns.", 2.8,
            # round 13: the posts and columns fade in on the base, not slid in (round 12's audit: the columns slid
            # through the base frames as it came down, the lift's rails through the posts, the trays through the
            # columns and the cladding through the cable trays overhead)
            stagger([s(L, ["base", "u2_base"], (0, 0, 900)),          # down first, then the rest on it
                     s(L, ["posts", "u2_posts"], (0, 0, 0)),
                     s(L, ["col_front", "col_rear", "u2_col_front", "u2_col_rear"], (0, 0, 0))], overlap=0.4),
            hold=0.3, cam_to=CAM_VLM)
    passive = [k for k in trays if k in PASSIVE]
    pas = ", ".join(passive[:-1]) + f" and {passive[-1]}" if len(passive) > 1 else "".join(passive)
    sc.step(f"4/{n}", f"The extractors and their drives, then {len(trays)} empty trays, A to {max(trays)}: "
            f"{len(trays) - len(passive)} electrified, each with its dock plate at the back right, and "
            f"{len(passive)} plain ones for storage ({pas}).", 2.6,
            stagger([s(L, ["lift_rails", "u2_lift_rails", "drive", "u2_drive"], (0, 0, 0)),
                     s(L, ["lift", "belts", "u2_lift", "u2_belts"], (0, 0, 0)), s(L, tray_groups, (0, 0, 0))],
                    overlap=0.5),
            hold=0.3)
    sc.step(f"4/{n}", "The cladding, the openings (996 mm tall), the consoles and the shutters.", 2.2,
            stagger([s(L, ["skin_L", "u2_skin_L", "skin_R", "u2_skin_R", "skin_back", "u2_skin_back"], (0, 0, 0)),
                     s(L, ["skin_top", "u2_skin_top"], (0, 0, 0)),
                     s(L, ["skin_front", "bay", "console", "shutter", "u2_skin_front", "u2_bay", "u2_console",
                           "u2_shutter"], (0, 0, 0))], overlap=0.5),
            hold=0.6)
    L.apply_state()
    # ------------------------------------------------------------------ 5. the floor machines
    order = [k for k in ("glovebox", "repowder", "sieve_cell", "aconity", "packaging", "instron_floor", "instron_small",
                         "fumehood", "ded", "wire_edm", "machining", *R8_MERGED["floor"]) if k in F.groups and F.groups[k]]
    fs = []
    for k in order:
        root = {"repowder": "repowder", "aconity": "aconity", "sieve_cell": "sieve_cell"}.get(k, f"wh_{k}:body")
        row = FLOOR_PLAN[k][1]
        names = F.groups[k]
        roots = [root] + (["wh_sieve:body"] if k == "sieve_cell" and "sieve_cell" in F.rigs else []) + \
            ([f"bench_{k}"] if k in W.BENCH else [])
        # round 13: set down on its footprint, 80 mm, not rolled 2.6 m in from the aisle: the roll took the wire EDM
        # through its utility drop and the fume hood through its dock's target post (round 12's audit)
        fs.append(s(L, roots, (0, 0, 80), names=names))
    late = [k for k in R8_MERGED["floor"] if k in order]      # round 8's scale-up machines, past the south row's ends
    main = [k for k in order if k not in late]
    fs_main = [f for k, f in zip(order, fs) if k not in late]
    sc.step(f"5/{n}", "The floor machines, rigged in on pallet jacks and machine skates (the Aconity MIDI is "
            "1450 kg, the 100 kN Instron 799 kg), are set down fronts to the aisle: the glovebox (its antechamber to the aisle), "
            "the rePowder" + (" with its powder-waste point (two vacuums, a pail for each alloy family)"
                              if sc.members("powder_point") else "") +
            ", the sieving cell, the Aconity MIDI, the packaging station; across the aisle the two "
            "Instrons, the ducted fume hood" + (" (its base the chemical waste's solvent and acid cabinets)"
                                                if sc.members("waste") else "") + ", the DED and the wire EDM" +
            (", and behind the south row the cups' machining cell" if "machining" in order else "") + ".", 6.4,
            stagger(fs_main, overlap=0.36), hold=1.2, cam_to=CAM_FLOOR,
            labels=W.auto(sc, CAM_FLOOR, W.floor_labels(F, main, have)))
    # round 16 (PR #371's check, 2026-11-26: the waste station "is probably never on screen": the hood's front faces
    # the aisle and every camera that showed the hood looked at its back): the hood from the aisle, close
    if sc.members("waste"):
        import waste_station as WS
        Mh = sc.world("wh_fumehood:body")

        def hw(x_, y_, z_):
            return tuple(float(v) for v in (Mh @ np.r_[x_, y_, z_, 1.0])[:3])
        cam_hood = [hw(900.0, WS.YF - 3300.0, 2300.0), hw(0.0, WS.YF + 200.0, 850.0), (0, 0, 1)]
        sc.step(f"5/{n}", "The chemical waste station, from the aisle: the fume hood's base is a vented solvent cabinet "
                "(yellow doors) and a vented acid cabinet (blue). Capped bottles come in to the intake tray under the "
                "sash, one class a trip, and a person consolidates them on the day shift (PR #371).", 3.2, None,
                hold=1.8, cam_to=cam_hood,
                labels=[("solvent cabinet: the IPA wastes", hw(-330.0, WS.YF + 30.0, 620.0), (0.06, 0.66)),
                        ("acid cabinet: acid aqueous; Weck's a shelf apart", hw(330.0, WS.YF + 30.0, 380.0),
                         (0.58, 0.80)),
                        ("intake tray: closed bottles only", hw(WS.INTAKE["x"], WS.INTAKE["y"], WS.Z0 + 60.0),
                         (0.62, 0.30))])
    # round 16: the powder point beside the rePowder (powder_point.py: PR #371's powder waste and #369's two vacuums)
    if sc.members("powder_point"):
        import powder_point as PP
        # from the east and above: from the aisle the fire point's 680R and B570 stand in front of it (stills, round 16)
        cam_pp = [(-3800.0, -2600.0, 4200.0), (-5250.0, -650.0, 300.0), (0, 0, 1)]
        sc.step(f"5/{n}", "Beside the rePowder, the powder-waste point: an explosion-proof 118EXP vacuum for each alloy "
                "family on wall power, a grounded pail for each family's sealed liners (lids set on, not crimped), "
                "Risk Management's Solid Material bucket and a can of dry sand for filters. People seal and carry "
                "the liners; powder waste never rides a MiR250.", 3.2, None, hold=2.0, cam_to=cam_pp,
                labels=[("118EXP vacuums, Al and Cu family", (PP.VAC["Cu"][0], PP.VAC["Cu"][1], 950.0), (0.56, 0.06)),
                        ("a pail for each family", (PP.PAIL["Cu"][0], PP.PAIL["Cu"][1], 420.0), (0.70, 0.44)),
                        ("Solid Material bucket", (PP.BUCKET[0], PP.BUCKET[1], 420.0), (0.74, 0.24)),
                        ("dry sand for filters", (PP.SAND[0], PP.SAND[1], 300.0), (0.04, 0.58))])
    # round 16: the cups' machining cell behind the south row (machining.FLOOR; notes/lab_r16.md), from the south-west
    if "machining" in order:
        import machining as MA
        cam_mc = [(-10500.0, -15500.0, 7600.0), (-4200.0, -8600.0, 600.0), (0, 0, 1)]
        sc.step(f"5/{n}", "Behind the south row, the cell that machines the charge cups and plugs (PR #373): a bar-fed "
                "lathe, an arm on a pedestal, IPA baths, a vacuum dryer, a scale and a gauge. Its MiR250 comes down "
                "the row's west end and along a corridor behind the row, then backs in to its front.", 3.2, None,
                hold=2.0, cam_to=cam_mc,
                labels=[("cup-and-plug machining cell", (MA.FLOOR["x"], MA.FLOOR["y"] + 600.0, 1500.0), (0.42, 0.20)),
                        ("its MiR250 dock", (MA.FLOOR["dock"][0], MA.FLOOR["dock"][1], 300.0), (0.62, 0.42)),
                        ("its way in, from the aisle", (-7977.0, -7000.0, 0.0), (0.08, 0.40))])
    if late:
        names_late = {"eos_m400": "an EOS M 400-4 (large-format LPBF)", "meltio_cell": "a Meltio robot cell (DED repair)"}
        fs_late = [f for k, f in zip(order, fs) if k in late]
        sc.step(f"5/{n}", "For scaling up, beyond the south row's ends, " +
                " and ".join(names_late.get(k, k) for k in late) + ", fronts to the north, each with a clear strip to "
                "the aisle. No MiR250 serves them: their powder, wire and parts come by forklift (notes/scaleup.md).",
                3.6, stagger(fs_late, overlap=0.5), hold=1.4, cam_to=CAM_SCALE,
                labels=W.auto(sc, CAM_SCALE, W.floor_labels(F, late, have)))
    # ------------------------------------------------------------------ 6. the arms
    u0 = units[INSTALL_AT]
    x, y, hd = u0.pose
    start = (x, y + 2200.0, hd)
    u0.set(start)
    ch = chargers

    def chargers_on(u):
        for nm in ch:
            sc.alpha[nm] = u
    sc.step(f"6/{n}", ("Three MiR Charge 48V chargers go in (the third, to the west, for the floor cleaner, unit 3), "
                       if F.unit3 is not None else "Two MiR Charge 48V chargers go in, ") +
            "then the first MiR250 rolls onto its charging plate.", 1.4,
            chargers_on, hold=0.1, cam_to=CAM_UNIT)
    base_names = u0.part_names("base")

    def roll(u):
        for nm in base_names:
            sc.alpha[nm] = min(1.0, u * 4)
        u0.set((x, start[1] + (y - start[1]) * u, hd))
    # round 15: the second half of the same step, so it no longer repeats the chargers (three since unit 3)
    sc.step(f"6/{n}", "The first MiR250 rolls onto its charging plate.", 2.0,
            roll, hold=0.2, labels=[("MiR250, 800 x 580 x 300 mm", (x, y, 300), (0.20, 0.60))])
    cab_names = u0.part_names("cabinet")
    cb_names = u0.part_names("control box")
    # round 16 (PR #371's check, and round 15's audit: "the UR control box slides through a MiR's Class D unit"): the
    # box went in sideways from the -y side, where the safety PR hung the Class D unit and moved the cabinet's door to
    # the front end. Now the box is set on the MiR's top first, lowered from above, and the cabinet comes down over it,
    # so nothing passes through anything; the box is serviced later through the door at the cabinet's front end.

    # (the box settles only the last 40 mm: lowered from higher it passed where the arm will stand on the cabinet's top
    # plate, 46 mm above the box, and the cabinet fades in round it in place, since lowering it over the box read as
    # the box inside its shell: the audit, round 16)
    def control_box(u):
        sc.gmat[f"{u0.name}_cb"] = T((0, 0, 40 * (1 - u)))
        for nm in cb_names:
            sc.alpha[nm] = min(1.0, u * 4)
    sc.step(f"6/{n}", "The UR control box (460 x 449 x 254 mm, 12 kg) is set on the MiR250's top.",
            1.4, control_box, hold=0.2, labels=[("UR control box", (x, y, 600), (0.20, 0.42))])

    def cabinet(u):
        for nm in cab_names:
            sc.alpha[nm] = min(1.0, u * 1.5)
    sc.step(f"6/{n}", "Its cabinet goes on over the box: it carries the arm, the Class D extinguisher on its aisle "
            "side and a door at its front end for the control box.", 1.6, cabinet, hold=0.2)
    rb = u0.robot
    arm_names = u0.part_names("arm")
    root0 = sc.gmat[rb.root].copy()

    def arm_on(u):
        sc.gmat[rb.root] = T((0, 0, 900 * (1 - u))) @ root0
        for nm in arm_names:
            sc.alpha[nm] = min(1.0, u * 3)
    sc.step(f"6/{n}", "The UR10e (33.3 kg: two people, or a small hoist) is set on the cabinet's top plate and bolted "
            "down: four M8 bolts at 20 Nm, two 8 mm pins so it goes back in the same place (UR's manual).", 2.4,
            arm_on, hold=0.4,
            labels=[("UR10e, 33.3 kg", (x, y, 1300), (0.20, 0.30))])
    g_names = u0.part_names("gripper")

    def gripper_on(u):
        u0.gripper_offset(160 * (1 - u))
        for nm in g_names:
            sc.alpha[nm] = min(1.0, u * 3)
    sc.step(f"6/{n}", "The Robotiq 2F-85 goes on the flange.", 1.4, gripper_on, hold=0.2)
    rb.set()
    others = [nm for uu in units if uu is not u0 for nm in uu.all_names()] + u3_names
    # round 13: it stretches straight up; round 12's stretch reached sideways, its wrist camera 12 mm into the second
    # unit's upper arm, 1.2 m away at the other charger
    q_ready = np.radians((-90.0, -90.0, 0.0, -90.0, -90.0, 180.0))

    def wake(u):
        for nm in others:
            sc.alpha[nm] = u
    wake_cap = "It wakes up and stretches. The second unit is built the same way at the other charger" + \
        (", and unit 3, the floor cleaner (orange band), at its own charger to the west." if u3_names else ".")
    sc.step(f"6/{n}", wake_cap, 1.8, A.both(rb.joint_to(q_ready), wake), hold=0.2)
    sc.step(f"6/{n}", wake_cap, 1.4, rb.joint_to(A.PARK_RAD), hold=0.4)
    # ------------------------------------------------------------------ 7. the trays
    def tables_on(u):
        for nm in (n for v in tables.values() for n in v):
            sc.alpha[nm] = u
    heavy = sorted(((m, key) for key, (m, _) in MASS_KG.items() if m and m > MASS_ONE_PERSON), reverse=True)
    sc.step(f"7/{n}", "Loading, drawn see-through. Most of what goes on a tray weighs 20-110 kg (the S2 PUMA "
            f"{heavy[0][0]:.0f} kg, each UPS {_ups_kg()}), more than the arm's 12.5 kg or one person should lift (NIOSH: 23 kg), "
            "so a scissor lift table stands at the opening, its deck level with the tray, and people slide each "
            "machine across. After the first tray of each Shuttle, a time-lapse.", 2.6,
            A.both(L.skin(1.0), tables_on), hold=0.4, cam_to=CAM_OPEN,
            labels=W.auto(sc, CAM_OPEN, [("scissor lift table, deck at the tray's floor",
                                          (700.0, LIFT_TABLE_Y, LIFT_DECK_Z))]))
    L.show_gauges = True
    cam_now = CAM_OPEN
    first = set()
    for k in trays:
        lst = items.get(k, [])
        role = A.ROLE.get(k, "")
        unit = L.unit.get(k, 1)
        want = CAM_OPEN if unit == 1 else CAM_OPEN2
        cam = None if want is cam_now else want
        cam_now = want
        full = unit not in first                 # the first tray of each Shuttle in full, the rest a time-lapse
        first.add(unit)
        fast, mint = 0.28, 0.6
        if full:
            L.fetch(k, f"7/{n}", f"Tray {k} ({role}) comes to the opening of Shuttle {unit}.", fast=fast,
                    hold=0.05, cam=cam, mint=mint)
        else:                                    # a cut: the tray is at the opening, the extractor under it
            L.use(unit)
            L.focus = k
            L.where[k] = "open"
            L.tray[k] = [*V.SLOTS["open"]]
            L.lift_z = A.LIFT_HOME
            L.apply_state()
        if lst:
            fs, lbls = [], []
            # round 13: back to front. Everything comes in from the lift table's deck at the opening, so an item put
            # down before one that goes behind it was crossed by it: round 12's audit had the VHX, the CNC, the reflow
            # oven and the Mastersizer sliding through their trays' UPSs, and camera posts through their instruments.
            # Farthest first, each later item stops short of what is already down.
            for key, g, names, nm in sorted(lst, key=lambda it: -ynear_of.get((k, it[1]), 0.0)):
                tr = V.Y_OPEN + yc_of.get((k, g), 0.0) - LIFT_START_Y     # from the lift table's deck
                fs.append(rig_in(sc, g, names, travel=tr) if key != "rack" and not g.startswith("eq_") else
                          A.item_in(L, g, travel=tr))
                if key not in ("ups", "cam"):
                    lbls.append((nm, tuple(np.array(sc.world(g)[:3, 3]) + (0, 0, 420))))
            ncam = sum(1 for it in lst if it[0] == "cam")
            extra = ", its UPS with an AirGradient on it" + (f", and {ncam} camera post{'s' if ncam > 1 else ''}"
                                                             if ncam else "")
            if k in PASSIVE:                     # round 11: no UPS, no dock plate, no cameras
                extra = (f". Nothing on it draws power: no UPS, no dock plate, no cameras, and a slot "
                         f"{V.SPAN[A.HOME[k]]:.0f} mm tall")
            cap = f"Tray {k}: " + ", ".join(lb[0] for lb in lbls) + extra + "."
            sc.step(f"7/{n}", cap, (1.0 + 0.32 * len(lst)) if full else (0.7 + 0.18 * len(lst)),
                    stagger(fs, overlap=0.5), hold=0.6 if full else 0.5, labels=W.auto(sc, cam_now, lbls, dy=0.16),
                    cam_to=None if full else cam)
        if full:
            L.store(k, f"7/{n}", f"Tray {k} goes back to its slot ({A.HOME[k]}), {V.SPAN[A.HOME[k]]:.0f} mm tall" +
                    (", which has no dock: nothing on the tray needs one." if k in PASSIVE else ", where it has power."),
                    fast=fast, hold=0.05, mint=mint)
        else:
            L.where[k] = A.HOME[k]
            L.tray[k] = [*V.SLOTS[A.HOME[k]]]
            L.apply_state()
    L.focus = None
    # ------------------------------------------------------------------ 8. the bay cameras
    # Round 11 (Sterling, PR #318, 2026-11-13: "Can't see the overhead camera from the angle. Should change the view
    # angle and temporarily make things opaque again"): round 10 showed both units from CAM_VLM, far off and through
    # the see-through cladding. Now each is seen from where an operator stands at its opening, eyes at 1.6 m, looking
    # up under the header (services.py's bay_camera clip opens on the same view), with the cladding and the other
    # ghosted parts solid while it is shown: Shuttle 2's first (the loading ends there), then Shuttle 1's; then back
    # to the wide view, the cladding see-through again.
    cam_names = add_bay_cams(sc)
    L.show_gauges = False
    L.apply_state()
    for nm in cam_names:
        sc.alpha[nm] = 0.0
    u2_cam = [nm for nm in cam_names if sc.group_of[nm] in {g for u in services.BAY_UNITS
                                                             for g in services.bay_groups(u, "2").values()}]
    by_unit = {2: u2_cam, 1: [nm for nm in cam_names if nm not in set(u2_cam)]}
    va0 = sc.view_angle

    def cams_on(unit, tables=False):
        def up(u):
            for nm in by_unit[unit]:
                sc.alpha[nm] = u
            if tables:
                tables_on(1.0 - min(1.0, 2 * u))
        return up
    for i, unit in enumerate((2, 1)):
        x = V.SHUTTLE_X[unit]
        tb = np.array(services.bay_cam_point("back", x))
        tf = np.array(services.bay_cam_point("front", x))
        tgt = (tb + tf) / 2
        side = 1.0 if i == 0 else -1.0          # the operator right of the middle at the first, left at the second
        view = [(x + side * BAY_EYE[0], BAY_EYE[1], BAY_EYE[2]), tuple(tgt + (0, 0, 10)), (0, 0, 1)]
        lbl = [(f"Shuttle {unit}'s back unit: a Pi 5, HQ Camera (16 mm lens)\nand Camera Module 3 Wide, on a "
                "pan-tilt head", tuple(tb), (0.96, 0.15)),
               ("its front unit, looking back", tuple(tf), (0.50, 0.08) if side > 0 else (0.50, 0.08)),
               ("both hung from the bay's roof", (x - side * 700.0, tgt[1], V.BAY_ROOF_Z),
                (0.03, 0.62) if side > 0 else (0.97, 0.62))]
        if i == 0:
            cap = (f"The bay cameras go on, two in each bay: Shuttle {unit}'s first, seen by an operator at the "
                   "opening looking up (the cladding drawn solid for them). They hang from the bay's roof, one at "
                   "the back looking forward over the presented tray, one behind the header looking back at it.")
            sc.step(f"8/{n}", cap, 1.2, A.both(L.skin(0.0), cams_on(unit, tables=True)), hold=1.1, cam_to=view,
                    labels=lbl, view_angle_to=BAY_VIEW_ANGLE)
        else:
            cap = (f"Then Shuttle {unit}'s: the same two. With the D405 on the arm's wrist, they see what is on every "
                   "tray the Shuttle presents.")
            sc.step(f"8/{n}", cap, 1.1, cams_on(unit), hold=0.9, cam_to=view, labels=lbl)
    pas = ", ".join(sorted(PASSIVE)[:-1]) + f" and {sorted(PASSIVE)[-1]}" if len(PASSIVE) > 1 else "".join(PASSIVE)
    sc.step(f"8/{n}", f"Every tray with instruments carries its own stream cameras; the storage trays ({pas}) carry "
            "none: the bay camera takes their stock whenever one is presented, the only time a jar or a sample can "
            "come or go.", 0.9, L.skin(1.0), hold=0.4, cam_to=CAM_VLM, view_angle_to=va0,
            labels=W.auto(sc, CAM_VLM, [("overhead cameras at the bay", services.bay_cam_point("back")),
                                        ("overhead cameras at the bay", services.bay_cam_point("back", X2))]))
    # ------------------------------------------------------------------ 9. orbit
    L.apply_state()
    cap = (f"Set up: two Shuttles with trays A-{max(trays)}, the floor machines, two MiR250 + UR10e units on charge" +
           (", and unit 3, the floor cleaner, on its own charger." if u3_names else "."))
    sc.step(f"9/{n}", cap, 1.2, L.skin(0.0), hold=0.0)
    for i, cam in enumerate(ORBIT):
        last = i == len(ORBIT) - 1
        sc.step(f"9/{n}", cap, 2.2, None, hold=2.0 if last else 0.0, cam_to=cam, still=last)
    return sc.save()


# ================================================================================================ the checks
def _tri_of(sc: Scene, names, Mi):
    """(points (n, 3), faces (m, 3)) of the visible actors `names`, in the frame Mi maps to (the tray's), or None."""
    vs, fs, off = [], [], 0
    for n in names:
        a = sc.actors.get(n)
        if a is None or sc.alpha.get(n, 1.0) <= 0.0 or sc.base_alpha.get(n, 1.0) <= 0.0:
            continue
        poly = pv.wrap(a.GetMapper().GetInput())
        if not poly.n_points or not poly.n_cells:
            continue
        tri = poly.triangulate()
        if not tri.faces.size:
            continue
        f = tri.faces.reshape(-1, 4)
        f = f[f[:, 0] == 3][:, 1:]
        if not len(f):
            continue
        M = Mi @ sc.world(sc.group_of[n])
        p = (np.c_[tri.points, np.ones(len(tri.points))] @ M.T)[:, :3]
        vs.append(p)
        fs.append(f + off)
        off += len(p)
    if not vs:
        return None
    return np.vstack(vs), np.vstack(fs)


def _fcl_obj(tri):
    """An FCL collision object of a (points, faces) mesh, or None."""
    import fcl
    if tri is None:
        return None
    v, f = tri
    bvh = fcl.BVHModel()
    bvh.beginModel(len(v), len(f))
    bvh.addSubModel(v, f)
    bvh.endModel()
    return fcl.CollisionObject(bvh, fcl.Transform())


def _fcl_of(sc: Scene, names, Mi):
    """One FCL mesh of the visible actors `names`, in the frame Mi maps to (the tray's)."""
    return _fcl_obj(_tri_of(sc, names, Mi))


# Round 14 (Sterling, PR #318, 2026-11-20, of the tray plan at 2:50 in round 12's video: "the overhead planning layouts
# (2D) ... show overlap between certain modules and the UPS"). Until round 13 the plan drew every part as its bounding
# box, the dock plate and the tray's lines as one box (x 550-1219, y 190-420 on every powered tray) over the UPS, and
# `fit` failed a pair only when the boxes overlapped *and* FCL found the solids touching. So the drawing showed boxes
# lapping over the OT-2, the Mastersizer, the VHX, the LumenPnP and the zwickiLine where the solids were in fact
# apart, and a pair 1 mm apart passed as "fits". Now: the plan draws each part's own footprint (its triangles
# projected onto the tray), the plate and the lines are two parts, and two things on a tray must stand CLEAR_MM apart,
# solid to solid (FCL's distance), or CLEAR_LINES_MM from the lines and the plate on the back rim.
CLEAR_MM = 10.0                # the least gap between two things on a tray: placing them by hand from a lift table
CLEAR_LINES_MM = 5.0           # from the tray's own lines and its dock plate, which lie on the back rim and the side
BY_DESIGN = {frozenset(("ups", "plate")), frozenset(("ups", "lines")), frozenset(("plate", "lines")),
             frozenset(("ups", "monitor"))}         # they join: the mains line ends at the UPS, the monitor sits on it
PLAN_GRID = 4.0                # mm per pixel of the footprints
PLAN_MASKS: dict = {}          # tray -> [(label, kind, mask)], for draw_plan


def _footprint(tri, x0, y0, nx, ny, res=PLAN_GRID):
    """A boolean mask (ny, nx) of a mesh's footprint on the tray: its triangles projected onto z = 0, rasterized."""
    from PIL import Image, ImageDraw
    img = Image.new("L", (nx, ny), 0)
    if tri is None:
        return np.zeros((ny, nx), bool)
    v, f = tri
    p = (v[:, :2] - (x0, y0)) / res
    a, b, c = p[f[:, 0]], p[f[:, 1]], p[f[:, 2]]
    area = np.abs((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (c[:, 0] - a[:, 0]) * (b[:, 1] - a[:, 1])) / 2
    d = ImageDraw.Draw(img)
    for i in np.nonzero(area > 0.02)[0]:
        d.polygon([tuple(a[i]), tuple(b[i]), tuple(c[i])], fill=1)
    return np.asarray(img, bool)


def tray_parts(sc: Scene, items: dict, k: str) -> list:
    """[(label, kind, (x0, x1, y0, y1, z0, z1), names)] on tray k, in the tray's frame: its items, its UPS, its dock
    plate, the tray's lines (round 14: two parts, not one box), and each camera rig in two parts (the post on its foot,
    and the head with its yoke)."""
    Mi = np.linalg.inv(sc.world(f"tray_{k}"))
    out = []
    for key, g, names, nm in items.get(k, []):
        if key == "cam":
            post = [n for n in names if sc.group_of[n] == g]
            head = [n for n in names if sc.group_of[n] != g]
            out.append((f"{g} post", "cam", _bounds_of(sc, post, Mi), post))
            out.append((f"{g} head", "cam", _bounds_of(sc, head, Mi), head))
            continue
        if key == "ups":                             # round 14: the UPS and the AirGradient on it, apart
            ag = [n for n in names if sc.group_of[n].startswith("ag_")]
            rest = [n for n in names if n not in set(ag)]
            out.append(("UPS", "ups", _bounds_of(sc, rest, Mi), rest))
            if ag:
                out.append(("AirGradient ONE", "monitor", _bounds_of(sc, ag, Mi), ag))
            continue
        out.append((nm, "item", _bounds_of(sc, names, Mi), names))
    plate = [n for n in sc.actors if n.startswith(f"plate_{k}/")]
    lines = [n for n in sc.actors if n.startswith(f"lines_{k}/")]
    out.append(("dock plate", "plate", _bounds_of(sc, plate, Mi), plate))
    out.append(("tray lines", "lines", _bounds_of(sc, lines, Mi), lines))
    return [o for o in out if o[2] is not None]


def check_trays(sc: Scene, items: dict) -> dict:
    """Each tray's parts against each other. Where two boxes come within the clearance of each other, the solids
    themselves: FCL says whether they touch and, if not, how far apart they are (round 14: a gap under CLEAR_MM, or
    CLEAR_LINES_MM to the lines and the plate, fails, as a touch always did). Also each part's footprint for the
    plan (PLAN_MASKS), and the nearest points of every pair under 30 mm."""
    import fcl
    inside = (V.TRAY_W / 2 - 12.0, V.TRAY_D / 2 - 12.0)
    edge = (V.TRAY_W / 2, V.TRAY_D / 2)
    x0g, y0g = -V.TRAY_W / 2 - 20.0, -V.TRAY_D / 2 - 20.0
    nx, ny = int((V.TRAY_W + 40.0) / PLAN_GRID) + 1, int((V.TRAY_D + 40.0) / PLAN_GRID) + 1
    rep = {}
    for k in ORDER:
        parts = tray_parts(sc, items, k)
        Mi = np.linalg.inv(sc.world(f"tray_{k}"))
        tris, objs = {}, {}

        def tri(i):
            if i not in tris:
                tris[i] = _tri_of(sc, parts[i][3], Mi)
            return tris[i]

        def obj(i):
            if i not in objs:
                objs[i] = _fcl_obj(tri(i))
            return objs[i]

        def gap(i, j):
            """(gap mm, point on i, point on j): 0 if the solids touch."""
            a, b = obj(i), obj(j)
            if a is None or b is None:
                return 0.0, None, None
            res = fcl.CollisionResult()
            if fcl.collide(a, b, fcl.CollisionRequest(), res) > 0 or res.is_collision:
                c = res.contacts[0].pos if res.contacts else None
                return 0.0, c, c
            dres = fcl.DistanceResult()
            d = fcl.distance(a, b, fcl.DistanceRequest(enable_nearest_points=True), dres)
            return max(0.0, float(d)), np.asarray(dres.nearest_points[0]), np.asarray(dres.nearest_points[1])
        near = {i: [] for i in range(len(parts))}
        for i in range(len(parts)):
            for j in range(i + 1, len(parts)):
                (lbl, kind, b, _), (lbl2, kind2, b2, _) = parts[i], parts[j]
                if kind == kind2 == "cam" and lbl.split()[0] == lbl2.split()[0]:
                    continue                             # a rig's own post and head
                if frozenset((kind, kind2)) in BY_DESIGN:
                    continue                             # the mains line ends at the UPS, the lines leave the plate
                need = CLEAR_LINES_MM if {kind, kind2} & {"plate", "lines"} else CLEAR_MM
                box_gap = max(max(b2[2 * a] - b[2 * a + 1], b[2 * a] - b2[2 * a + 1]) for a in range(3))
                if box_gap >= 30.0:
                    continue
                g, pa, pb = gap(i, j)
                rec = dict(other=None, gap_mm=round(g, 1), need_mm=need,
                           a=None if pa is None else [round(float(v), 1) for v in pa[:2]],
                           b=None if pb is None else [round(float(v), 1) for v in pb[:2]])
                near[i].append({**rec, "other": lbl2})
                near[j].append({**rec, "other": lbl, "a": rec["b"], "b": rec["a"]})
        rows, top, masks = [], 0.0, []
        for i, (lbl, kind, b, _) in enumerate(parts):
            lim = edge if kind == "cam" else inside           # a camera head may lean over the rim, not the edge
            rim = kind in ("plate", "lines") or (b[0] >= -lim[0] - 0.5 and b[1] <= lim[0] + 0.5 and
                                                 b[2] >= -lim[1] - 0.5 and b[3] <= lim[1] + 0.5)
            h = b[5] - V.T_FLOOR
            top = max(top, b[5])
            clash = sorted({n["other"] for n in near[i] if n["gap_mm"] <= 0.0})
            close = sorted({n["other"] for n in near[i] if 0.0 < n["gap_mm"] < n["need_mm"]})
            rows.append(dict(item=lbl, kind=kind, box_mm=[round(float(v)) for v in b], height_mm=round(float(h), 1),
                             under_goods_height=bool(h <= V.MAX_GOODS_H + 0.5), inside_rim=bool(rim),
                             overlaps=clash, too_close=close,
                             nearest=sorted(near[i], key=lambda n: n["gap_mm"])[:4]))
            masks.append((lbl, kind, _footprint(tri(i), x0g, y0g, nx, ny)))
        PLAN_MASKS[k] = masks
        slot = TRAYS[k][0]
        need = V.PITCH * math.ceil((top + V.GOODS_CLEAR - 1e-6) / V.PITCH)
        rep[k] = dict(role=TRAYS[k][1], slot=slot, shuttle=V.SLOT_SHUTTLE[slot], slot_z_mm=V.SLOTS[slot][1],
                      span_mm=V.SPAN[slot], tallest_mm=round(float(top - V.T_FLOOR), 1), span_needed_mm=need,
                      span_ok=bool(need <= V.SPAN[slot]), items=rows,
                      ok=bool(need <= V.SPAN[slot] and all(not r["overlaps"] and not r["too_close"] and r["inside_rim"]
                                                           and r["under_goods_height"] for r in rows)))
    return rep


def _rect_circle(rect, c, r):
    x0, x1, y0, y1 = rect
    dx = max(x0 - c[0], 0.0, c[0] - x1)
    dy = max(y0 - c[1], 0.0, c[1] - y1)
    return dx * dx + dy * dy < r * r


def _rects_hit(a, b, m=0.0):
    return a[0] < b[1] + m and b[0] < a[1] + m and a[2] < b[3] + m and b[2] < a[3] + m


def check_floor(sc: Scene, F: Floor) -> dict:
    """Every dock: the docked MiR250, its approach along the dock line from the pivot spot at its open end, and the
    pivot itself (a circle of the MiR's half-diagonal), against every machine's plan rectangle and every target post's
    foot; and the aisle against the machines. Margin 30 mm."""
    m = 30.0
    rects = machine_rects(sc, F)
    Lm, Wm = P.MIR["L"], P.MIR["W"]
    r_piv = math.hypot(Lm / 2, Wm / 2)
    posts = {k: tuple(W.target_xy(k)) for k in FLOOR_PLAN
             if (k in F.groups or k in ("vlm", "repowder")) and k not in NO_DOCK}
    feet = {k: (x - 150, x + 150, y - 150, y + 150) for k, (x, y) in posts.items()}
    docks = {}
    for key in posts:
        x, y, hd = W.dock_pose(key)
        fwd = 1.0 if abs(hd) < 1 else -1.0                    # along +x (north row) or -x (south)
        back = key in W.BACK_IN
        open_dir = fwd if back else -fwd                      # the end it comes in from
        docked = (x - Lm / 2, x + Lm / 2, y - Wm / 2, y + Wm / 2)
        piv, hits = None, []
        for d in np.arange(Lm / 2 + 50.0, 4000.0, 25.0):        # the nearest clear pivot spot on the dock line
            c = (x + open_dir * d, y)
            if not any(_rect_circle(rr, c, r_piv + m) for kk, rr in rects.items()) and \
                    not any(_rect_circle(ff, c, r_piv + m) for kk, ff in feet.items()):
                piv = c
                break
        if piv is None:
            hits.append("no pivot spot within 4 m")
        else:
            lane = (min(x, piv[0]) - Lm / 2, max(x, piv[0]) + Lm / 2, y - Wm / 2, y + Wm / 2)
            hits += [kk for kk, rr in rects.items() if _rects_hit(lane, rr, m)]
            hits += [f"post {kk}" for kk, ff in feet.items() if kk != key and _rects_hit(lane, ff, 0.0)]
            ff = feet[key]
            if _rects_hit(docked, ff, 0.0):
                hits.append("its own post under the docked MiR")
        docks[key] = dict(dock=[round(x), round(y), round(hd)], backs_in=back,
                          pivot=None if piv is None else [round(piv[0]), round(piv[1])],
                          approach_mm=None if piv is None else round(abs(piv[0] - x)),
                          target_post=[round(v) for v in posts[key]], hits=sorted(set(hits)), ok=not hits)
    aisle = (W.X_END[0], W.X_END[1], W.AISLE[1], W.AISLE[0])
    in_aisle = [k for k, rr in rects.items() if _rects_hit(aisle, rr, 0.0)]
    return dict(docks=docks, machines={k: [round(v) for v in r] for k, r in rects.items()},
                aisle_mm=[round(v) for v in aisle], machines_in_aisle=in_aisle,
                ok=bool(all(d["ok"] for d in docks.values()) and not in_aisle),
                method=" ".join(check_floor.__doc__.split()))


def draw_plan(rep: dict, path):
    """Every tray from above: each part's own footprint (round 14; until round 13 its bounding box), items blue, the
    UPS amber with its model, the dock plate red, the tray's lines thin red, camera posts and heads green; a part that
    touches another or stands closer than the clearance is outlined red, with a red tick between the nearest points and
    the gap. And both Shuttles' columns."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    import ups as U
    cols = {"item": "#4a7bd0", "ups": "#e0a020", "plate": "#b8402c", "lines": "#d06a50", "cam": "#2e9c6a",
            "monitor": "#8a4fbf"}
    order = {"lines": 0, "plate": 1, "item": 2, "ups": 3, "monitor": 4, "cam": 5}
    trays = [k for k in ORDER]
    nrow = math.ceil(len(trays) / 2)
    fig = plt.figure(figsize=(18, 2.35 * nrow), dpi=110)
    gs = fig.add_gridspec(nrow, 3, width_ratios=[1, 1, 0.55], wspace=0.06, hspace=0.55, top=0.95)
    x0g, y0g = -V.TRAY_W / 2 - 20.0, -V.TRAY_D / 2 - 20.0
    for i, k in enumerate(trays):
        ax = fig.add_subplot(gs[i % nrow, i // nrow])
        r = rep[k]
        ax.add_patch(Rectangle((-V.TRAY_W / 2, -V.TRAY_D / 2), V.TRAY_W, V.TRAY_D, fc="#eceef0", ec="#555", lw=1.0))
        ax.add_patch(Rectangle((-V.TRAY_W / 2 + 12, -V.TRAY_D / 2 + 12), V.TRAY_W - 24, V.TRAY_D - 24, fc="none",
                               ec="#999", lw=0.6, ls=":"))
        rows = {it["item"]: it for it in r["items"]}
        masks = sorted(PLAN_MASKS.get(k, []), key=lambda m: order.get(m[1], 9))
        for lbl, kind, mask in masks:
            if not mask.any():
                continue
            it = rows.get(lbl, {})
            bad = bool(it.get("overlaps") or it.get("too_close") or not it.get("inside_rim", True)
                       or not it.get("under_goods_height", True))
            ny, nx = mask.shape
            xs = x0g + (np.arange(nx) + 0.5) * PLAN_GRID
            ys = y0g + (np.arange(ny) + 0.5) * PLAN_GRID
            alpha = 0.35 if lbl.endswith("head") else 0.85
            ax.contourf(xs, ys, mask.astype(float), levels=[0.5, 1.5], colors=[cols.get(kind, "#777")], alpha=alpha)
            ax.contour(xs, ys, mask.astype(float), levels=[0.5], colors=["red" if bad else "#222"],
                       linewidths=1.4 if bad else 0.4)
            yy, xx = np.nonzero(mask)
            cx, cy = x0g + (xx.mean() + 0.5) * PLAN_GRID, y0g + (yy.mean() + 0.5) * PLAN_GRID
            if kind == "item":
                ax.text(cx, cy, f"{lbl[:26]}\n{it.get('height_mm', 0):.0f} mm", ha="center", va="center",
                        fontsize=6.0, color="white")
            elif kind == "ups" and U.unit_of(k):
                m = U.unit_of(k)
                ax.text(cx, cy, f"UPS {m.get('short', m['model'])}", ha="center", va="center", fontsize=5.2,
                        color="#3a2a00")
            elif kind == "monitor":
                ax.text(cx, cy + 60, "AirGradient", ha="center", va="bottom", fontsize=5.0, color="#4a2070")
        for it in r["items"]:                            # the pairs under the clearance: a red tick and the gap
            for n in it.get("nearest", []):
                if n["gap_mm"] < n["need_mm"] and n["a"] and n["b"] and it["item"] < n["other"]:
                    (xa, ya), (xb, yb) = n["a"], n["b"]
                    ax.plot([xa, xb], [ya, yb], color="red", lw=1.6)
                    ax.text((xa + xb) / 2, (ya + yb) / 2 + 25, f"{n['gap_mm']:.0f} mm", color="red", fontsize=6.0,
                            ha="center")
        ax.set_xlim(-V.TRAY_W / 2 - 30, V.TRAY_W / 2 + 30)
        ax.set_ylim(-V.TRAY_D / 2 - 30, V.TRAY_D / 2 + 30)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ok = "fits" if r["ok"] else "CHECK"
        pas = " (passive: no UPS, dock plate or cameras)" if k in PASSIVE else ""
        gaps = [n["gap_mm"] for it in r["items"] for n in it.get("nearest", []) if n["need_mm"] == CLEAR_MM]
        least = f"; least gap {min(gaps):.0f} mm" if gaps else ""
        ax.set_title(f"Tray {k}: {r['role']}{pas}\nShuttle {r['shuttle']}, slot {r['slot']}: {r['span_mm']:.0f} mm "
                     f"(needs {r['span_needed_mm']:.0f}; tallest {r['tallest_mm']:.0f}{least}): {ok}", fontsize=8,
                     loc="left")
        ax.text(0, -V.TRAY_D / 2 - 22, "front: the opening, where the arm works", ha="center", va="top", fontsize=5.5,
                color="#555")
    ax = fig.add_subplot(gs[:, 2])
    for u, x in V.SHUTTLE_X.items():
        for slot, (y, z) in V.SLOTS.items():
            if slot == "open" or V.SLOT_SHUTTLE[slot] != u:
                continue
            xc = (0.0 if y > 0 else -1.05) + (u - 1) * 2.4
            tray = next((k for k, (s, _) in TRAYS.items() if s == slot), None)
            span = V.SPAN[slot]
            ax.add_patch(Rectangle((xc, z), 0.95, span, fc="#dfe8f5" if tray else "#f4f4f4", ec="#456", lw=0.7))
            if tray:
                need = rep[tray]["span_needed_mm"]
                ax.add_patch(Rectangle((xc, z), 0.95, rep[tray]["tallest_mm"] + V.T_FLOOR, fc="#4a7bd0", alpha=0.45,
                                       ec="none"))
                ax.text(xc + 0.475, z + span / 2, f"{slot}: tray {tray}\n{span:.0f} (needs {need:.0f})",
                        ha="center", va="center", fontsize=6.4)
            else:
                ax.text(xc + 0.475, z + span / 2, f"{slot}: free\n{span:.0f}", ha="center", va="center", fontsize=6.4,
                        color="#777")
        for col, lst in V.COLUMNS[u].items():       # round 11: what each column has left at its top
            if not lst and col != "front_low":
                continue
            z_end = (V.Z_FRONT_HI if col == "front" else V.Z_LOW) + sum(sp for _, sp in lst)
            top = V.Z_FRONT_LOW_TOP if col == "front_low" else V.Z_TOP_IN
            free = top - z_end
            if free >= V.PITCH:
                xc = (0.0 if col == "rear" else -1.05) + (u - 1) * 2.4
                ax.add_patch(Rectangle((xc, z_end), 0.95, free, fc="none", ec="#9a9", lw=0.7, ls="--"))
                ax.text(xc + 0.475, z_end + free / 2, f"free {free:.0f}", ha="center", va="center", fontsize=6.0,
                        color="#585")
        x0 = (u - 1) * 2.4 - 1.05
        ax.add_patch(Rectangle((x0, V.Z_SILL), 0.95, V.OPEN_H, fc="#fff7e0", ec="#c90", lw=0.8))
        ax.text(x0 + 0.475, V.Z_SILL + V.OPEN_H / 2, f"opening\n{V.OPEN_H:.0f} mm\ngoods\n{V.MAX_GOODS_H:.1f}",
                ha="center", va="center", fontsize=6.0, color="#963")
        ax.text(x0 + 1.0, V.UNIT_H + 90, f"Shuttle {u}" + (" (x = 0)" if u == 1 else f" (x = {x:.0f} mm)"),
                ha="center", fontsize=8)
        ax.text(x0 + 0.475, 120, "front", ha="center", fontsize=6.5, color="#555")
        ax.text(x0 + 1.525, 120, "rear", ha="center", fontsize=6.5, color="#555")
    ax.axhline(V.Z_TOP_IN, color="#999", lw=0.6, ls="--")
    ax.text(3.6, V.Z_TOP_IN + 30, "drive bay", fontsize=6, ha="right", color="#777")
    ax.set_xlim(-1.2, 3.8)
    ax.set_ylim(0, V.UNIT_H + 250)
    ax.set_xticks([])
    ax.set_ylabel("height over the floor, mm (tray bottoms; 25 mm pitch)", fontsize=7)
    ax.tick_params(labelsize=6.5)
    fig.suptitle("The tray plan: every tray from above, front (the opening) at the bottom, each part's own footprint. "
                 "Items blue, UPS amber, dock plate and tray lines red, camera posts and heads green, AirGradient "
                 f"purple; a red outline and tick: closer than {CLEAR_MM:.0f} mm, solid to solid ({CLEAR_LINES_MM:.0f} "
                 "mm to the lines).\nRight: the two Shuttles' columns, each slot as tall as its tray needs, and what each "
                 "column has left (dashed) (setup_lab.py fit)", fontsize=10.5, x=0.12, y=0.995, ha="left")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def draw_floor(frep: dict, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle
    fig, ax = plt.subplots(figsize=(16, 7.2), dpi=110)
    a = frep["aisle_mm"]
    ax.add_patch(Rectangle((a[0], a[2]), a[1] - a[0], a[3] - a[2], fc="#fff6cf", ec="#d8b400", lw=0.8))
    ax.text(a[0] + 200, (a[2] + a[3]) / 2, "aisle, 3.0 m", fontsize=8, va="center", color="#8a7300")
    for k, (x0, x1, y0, y1) in frep["machines"].items():
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#9aa6b5", ec="#334", lw=0.7, alpha=0.8))
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, W.NAMES.get(k, k).split(":")[0], ha="center", va="center", fontsize=6.5)
    Lm, Wm = P.MIR["L"], P.MIR["W"]
    for k, d in frep["docks"].items():
        x, y, _ = d["dock"]
        c = "#2e9c6a" if d["ok"] else "#d03030"
        ax.add_patch(Rectangle((x - Lm / 2, y - Wm / 2), Lm, Wm, fc=c, alpha=0.35, ec=c, lw=0.8))
        if d["pivot"]:
            px, py = d["pivot"]
            ax.add_patch(Circle((px, py), math.hypot(Lm / 2, Wm / 2), fc="none", ec=c, lw=0.7, ls="--"))
            ax.annotate("", xy=(x, y), xytext=(px, py), arrowprops=dict(arrowstyle="->", color=c, lw=0.8))
        tx, ty = d["target_post"]
        ax.add_patch(Rectangle((tx - 150, ty - 150), 300, 300, fc="#222", ec="none"))
    ax.set_aspect("equal")
    ys = [v for r in frep["machines"].values() for v in r[2:]]
    ax.set_xlim(-12200, 12400)
    ax.set_ylim(min(-9300, min(ys) - 300), 1900)
    ax.set_xlabel("x, mm", fontsize=7)
    ax.set_ylabel("y, mm", fontsize=7)
    ax.tick_params(labelsize=6.5)
    ok = "every dock clear" if frep["ok"] else "CHECK: " + ", ".join(k for k, d in frep["docks"].items() if not d["ok"])
    ax.set_title("The floor plan for MiR250 docking: docked MiR (green), the pivot spot it turns on (dashed) and its "
                 f"way in, target posts (black). {ok}", fontsize=9, loc="left")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


TRAY_KINDS_KG = {"light": 228.0, "medium": 360.0, "strong": 490.0}     # #53's quote: 502, 794, 1080 lb (vlm.TRAYS)


def tray_loads(items: dict) -> dict:
    """Round 10: what each tray carries, kg, from MASS_KG where a figure is published, the rest listed as not found;
    and the lightest of #53's three tray kinds that carries the known part (a lower bound: the unknowns add to it).
    Each item heavier than one person should lift (MASS_ONE_PERSON) goes on with the lift table."""
    out = {}
    for k in ORDER:
        known, unknown, heavy = 0.0, [], []
        for key, g, names, nm in items.get(k, []):
            if key == "cam":
                continue                               # a post, a Pi and two cameras: a few kg, by hand
            m = MASS_KG.get(key)
            if key == "ups":                           # round 12: each tray's own unit (ups.py)
                import ups as U
                m = (U.unit_of(k)["kg"], f"{U.unit_of(k)['model']} (ups.CATALOGUE)")
            if m is None or m[0] is None:
                unknown.append(nm)
                continue
            known += m[0]
            if m[0] > MASS_ONE_PERSON:
                heavy.append(f"{nm} ({m[0]:.0f} kg)")
        kind = next((kd for kd, cap in TRAY_KINDS_KG.items() if known <= cap), "over a strong tray")
        out[k] = dict(known_kg=round(known, 1), not_found=unknown, over_one_person=heavy,
                      lightest_tray_for_the_known_part=kind)
    return out


def fit(data, idata) -> dict:
    sc, L, F, items, rigs, units, util, ulabel, vp = build(data, idata, mp4=False)
    L.apply_state()
    rep = check_trays(sc, items)
    for k, ld in tray_loads(items).items():
        rep[k]["load"] = ld
    frep = check_floor(sc, F)
    out = dict(trays=rep, floor=frep, slots={k: dict(y=v[0], z=v[1], span=V.SPAN.get(k), shuttle=V.SLOT_SHUTTLE[k])
                                             for k, v in V.SLOTS.items()},
               shuttle_x=V.SHUTTLE_X, max_goods_h_mm=V.MAX_GOODS_H, goods_clear_mm=V.GOODS_CLEAR,
               r8={k: v for k, v in R8_MERGED.items() if k != "done"},
               clearance_mm=CLEAR_MM, clearance_to_lines_mm=CLEAR_LINES_MM,
               method="setup_lab.py fit (round 14): each item, UPS, the dock plate, the tray's lines and each camera "
                      "rig's post and head, as drawn, in the tray's frame. Pairs whose boxes come within 30 mm are "
                      "measured solid to solid with FCL (python-fcl, on the meshes): a touch ('overlaps') or a gap under "
                      f"{CLEAR_MM:.0f} mm ({CLEAR_LINES_MM:.0f} mm to the lines and the plate; 'too_close') fails; the "
                      "UPS against the plate and lines is by design. Until round 13 a pair failed only if its boxes "
                      "overlapped and the solids touched. A slot needs the tallest top + 20 mm, on the 25 mm pitch")
    (OUT / "tray_plan.json").write_text(json.dumps(out, indent=1) + "\n")
    draw_plan(rep, OUT / "tray_plan.png")
    draw_floor(frep, OUT / "tray_plan_floor.png")
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    data = lab.meshes()
    idata = load_all()
    if args and args[0] == "fit":
        out = fit(data, idata)
        for k, r in out["trays"].items():
            bad = [(it["item"], it["overlaps"], it["too_close"], it["inside_rim"], it["under_goods_height"])
                   for it in r["items"] if it["overlaps"] or it["too_close"] or not it["inside_rim"]
                   or not it["under_goods_height"]]
            print(f"tray {k} {r['slot']}: span {r['span_mm']:.0f}, needs {r['span_needed_mm']:.0f} "
                  f"(tallest {r['tallest_mm']:.0f}) {'ok' if r['ok'] else 'CHECK'} {bad if bad else ''}")
        if "-v" in args:
            for k, r in out["trays"].items():
                print("tray", k)
                for it in r["items"]:
                    print("   ", it["item"][:40].ljust(40), it["box_mm"], it["overlaps"], it["inside_rim"],
                          [(n["other"][:24], n["gap_mm"]) for n in it["nearest"][:3]])
        for k, d in out["floor"]["docks"].items():
            print(f"dock {k}: {'ok' if d['ok'] else 'CHECK'} pivot {d['pivot']} {d['hits']}")
        print("machines in the aisle:", out["floor"]["machines_in_aisle"])
    else:
        print(movie(data, idata), flush=True)
        if not PREVIEW:
            print(line.mp4_to_gif(OUT / "mp4" / "setup_lab.mp4", OUT / "setup_lab.gif", **W.GIF), flush=True)
