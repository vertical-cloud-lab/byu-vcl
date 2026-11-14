"""The whole lab set up from scratch (#303), on the warehouse floor of ``warehouse.py``: an empty bay; the layout taped
on the floor, with a MiR250 dock and an AprilTag target at every station; the utilities; two Kardex Shuttles
assembled; the floor machines moved in; the UR10e arms installed on their MiR250s; every tray loaded, A to M, each
with its UPS and its stream cameras; the bay cameras; a closing orbit. Mobile bases only: no rail anywhere.

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
    out["K"] = [("glovebox_tray", -460.0, 7.0, 0.0), ("vhx", 570.0, -50.0, 0.0)]
    out["L"] = [("tensile_h", -23.5, None, 0.0), ("hardness", -944.0, 11.0, 0.0)]      # the tester in front of the UPS
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
                  "on tray H its heaters pause in transit: 1500 W is over the tray's UPS (1500 VA, services.py)",
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
FLOOR_PLAN = {
    "glovebox": (-7300.0, "N", -90.0, -7300.0),
    "repowder": (None, "N", 0.0, A.REPOWDER_AT[0] + 288.0),
    "sieve_cell": (-1982.5, "N", 0.0, -1700.0),
    "vlm": (0.0, "N", 0.0, 0.0),
    "vlm2": (X2, "N", 0.0, X2),
    "aconity": (6950.0, "N", 0.0, 6650.0),
    "packaging": (10050.0, "N", 0.0, 10050.0),
    "instron_floor": (-6400.0, "S", 0.0, -6600.0),
    "instron_small": (-4300.0, "S", 0.0, -4300.0),
    "fumehood": (1500.0, "S", 0.0, 1500.0),
    "ded": (3900.0, "S", 0.0, 3900.0),
    "wire_edm": (6600.0, "S", 0.0, 6600.0),
}
BACK_IN = {"instron_small", "vlm", "aconity", "sieve_cell"}   # backed into from the open end beyond the MiR's back
# the rePowder sticks out 337 mm past the row's fronts, so a MiR docks there 298 mm further out, as the alloy route's
# chapters 2-3 park it (alloy_atomize.END_POSE); so does the sieving cell's (alloy_print: 300 mm off its bench)
DOCK_Y = {"repowder": -2230.0, "sieve_cell": W.DOCK_N - 300.0}
# targets that can't stand where warehouse.target_xy puts them: the VLMs' stand outside the opening's width, so a tray
# pulled out to the front for maintenance passes them; the rePowder's in front of its own front
TARGET_AT = {"vlm": (-1330.0, -1742.0), "vlm2": (X2 + 1330.0, -1742.0),
             "repowder": (A.REPOWDER_AT[0] + 288.0 + 650.0, -1899.0 - 180.0)}
SIEVE_BENCH = dict(x=-1982.5, w=1065.0, d=600.0, h=700.0, encl_h=1150.0)    # alloy_print.BENCH, ENCL_H
INSTALL_AT = 0                                 # the first unit is put together at charger 0

CAM_ROOM = [(11000, -22000, 15500), (500, -2700, 0), (0, 0, 1)]
CAM_TOP = [(2000, -15000, 22500), (300, -2800, 0), (0, 0, 1)]
CAM_UTIL = [(9600, -17500, 9800), (300, -2600, 2400), (0, 0, 1)]
CAM_VLM = [(9800, -10400, 6600), (1800, -400, 1900), (0, 0, 1)]
CAM_FLOOR = [(6200, -21500, 17500), (700, -2900, 0), (0, 0, 1)]
# round 8: the scale-up machines past the south row's ends (the EOS lower left, the Meltio cell lower right) with the
# whole lab behind them; a camera test of five views found this the one that shows both whole
CAM_SCALE = [(6200, -31000, 24000), (0, -6500, 0), (0, 0, 1)]
CAM_UNIT = [(1900, -2900, 2300), (-1300, -5600, 800), (0, 0, 1)]
CAM_OPEN = [(3500, -5900, 2700), (0, -1000, 1300), (0, 0, 1)]      # north of the south row's cable tray and argon
CAM_OPEN2 = [(X2 + 3500, -5900, 2700), (X2, -1000, 1300), (0, 0, 1)]
# round 11: the bay cameras from an operator's eyes, 1.6 m up and 0.9 m in front of the Shuttle's face, 420 mm right of
# its centre (services.movie_bay_camera's view), looking up under the header at the unit
BAY_EYE = (420.0, -2450.0, 1600.0)
BAY_VIEW_ANGLE = 40.0
ORBIT = [[(-9000, -16500, 9000), (700, -2300, 600), (0, 0, 1)],
         [(-15500, -2000, 9500), (700, -2300, 600), (0, 0, 1)],
         [(3500, -15500, 5600), (700, -2300, 900), (0, 0, 1)],
         [(11500, -18500, 12500), (700, -2600, 300), (0, 0, 1)]]


# ------------------------------------------------------------------------------------------------ round 8's modules
R8_MERGED: dict = {"trays": {}, "floor": {}, "new_trays": {}, "skipped": [], "moved": {}}  # what merge_r8() took in
# Floor machines no MiR250 serves, so no dock tape, no target post and no dock check: the EOS M 400-4 and the Meltio
# cell (notes/scaleup.md: "Neither has a MiR dock: the powder comes by the 100 kg in EOS's containers, and a propeller
# by forklift or crane"). A module adds its own with NO_DOCK = {...}, or dock=False in a FLOOR_PLACEMENT.
NO_DOCK = {"eos_m400", "meltio_cell"}
# Where two streams' placements collide, the tray plan's call (fit found it; notes/lab_r8.md): tray F's quench tank
# (r8_test, x 860, y -150) stood inside the disc magazine (r8_prep, x 1022, y -190). The magazine keeps its place in
# front of the UPS; the tank moves left and back, between the furnace's right side and the magazine, behind camera
# F1's post: 25 mm from the furnace, 44 mm from the magazine, 40 mm behind the post, clear of the furnace door's swing
# (it opens to the front on its right-hand hinges). Its rig is where every scene built on setup_lab.build finds it.
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
        for name, e in data["vlm"].items():
            kw = {}
            if e["material"] in ("vlm_skin", "vlm_bay"):
                kw = dict(specular=0.05, ambient=0.35)
            if e["material"] == "vlm_led":
                kw = dict(ambient=0.9, diffuse=0.2)
            g = f"u2_{e['group']}"
            sc.add(f"u2/{name}", e["mesh"], e["color"], g, opacity=e["opacity"], **kw)
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
    """The tray's UPS (services.ups_parts) as its own group, so it can be carried in."""
    import services
    g = f"ups_{k}"
    names = services.add_meshes(sc, g, services.meshes_of("ups", services.ups_parts, 1.0), g)
    sc.parent[g] = f"tray_{k}"
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


def footprints(sc: Scene, F: Floor) -> pv.PolyData:
    """Tape round every floor machine's footprint, from where it will stand."""
    out = []
    for key, (x0, x1, y0, y1) in machine_rects(sc, F).items():
        if key.startswith("charger"):
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
        bb = _bounds_of(sc, [n for n in names if sc.base_alpha.get(n, 1.0) > 0.0])
        if bb is not None:
            out[key] = bb[:4]
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


def utilities(hood=None) -> tuple[dict, tuple]:
    """Cable trays over both rows with a drop to each station ending in a grey junction box (sockets and a network
    port), a network cable in each tray, an argon line from a cylinder manifold to the gas users, and the fume hood's
    duct. Layout choices, drawn to read, not a design. -> ({name: (mesh, colour)}, a junction box's label point)."""
    zn, yn = 4300.0, W.Y_FACE_N + 700.0          # over the north row, above the VLM's 3950 mm roof
    zs, ys = 3200.0, W.Y_FACE_S - 600.0
    xs = (-9200.0, 11000.0)

    def tray(x0, x1, y, z):
        return W._merge([W._box(x0, y - 150, z, x1, y + 150, z + 12), W._box(x0, y - 150, z, x1, y - 138, z + 100),
                         W._box(x0, y + 138, z, x1, y + 150, z + 100)])
    trays = W._merge([tray(*xs, yn, zn), tray(xs[0] + 1200, xs[1], ys, zs)])
    hangers = W._merge([W._box(x - 15, y - 15, z + 100, x + 15, y + 15, 6000) for x in np.arange(xs[0], xs[1], 3000)
                        for y, z in ((yn, zn), (ys, zs))])
    net = W._merge([pv.Cylinder(center=((xs[0] + xs[1]) / 2, y + 60, z + 35), direction=(1, 0, 0), radius=18,
                                height=xs[1] - xs[0], resolution=16).triangulate() for y, z in ((yn, zn), (ys, zs))])
    drops, parts = [], {}
    north = {"glovebox": -7300.0, "repowder": -3640.0, "sieve_cell": -1700.0, "vlm": 900.0, "vlm2": X2 + 900.0,
             "aconity": 7300.0, "packaging": 10050.0}
    south = {"instron_floor": -6400.0, "instron_small": -4300.0, "chargers": -900.0, "fumehood": 900.0,
             "ded": 3900.0, "wire_edm": 6600.0}

    def add(d):
        for k, (m, c) in d.items():
            parts.setdefault(k, ([], c))[0].append(m)
    label = None
    for key, x in north.items():
        z_end = 3975.0 if key.startswith("vlm") else 2500.0
        drops.append(pv.Cylinder(center=(x, yn - 60, (zn + z_end) / 2), direction=(0, 0, 1), radius=22,
                                 height=zn - z_end, resolution=16).triangulate())
        if not key.startswith("vlm"):
            add(junction_box(x, yn - 60, z_end, -1))
        else:
            add({"junction boxes": (W._box(x - 120, yn - 120, z_end - 5, x + 120, yn, z_end + 150), (0.62, 0.64, 0.66))})
    for key, x in south.items():
        drops.append(pv.Cylinder(center=(x, ys + 60, (zs + 1900) / 2), direction=(0, 0, 1), radius=22,
                                 height=zs - 1900, resolution=16).triangulate())
        add(junction_box(x, ys + 60, 1900.0, +1))
        if key == "instron_small":
            label = (x, ys + 60, 1800.0)
    gas_users = [-7300.0, -3640.0, 7300.0]
    gx0 = xs[0] - 400
    ar = [pv.Cylinder(center=((gx0 + gas_users[-1]) / 2, yn + 230, zn - 150), direction=(1, 0, 0), radius=14,
                      height=gas_users[-1] - gx0, resolution=14).triangulate(),
          pv.Cylinder(center=(gx0, yn + 230, zn / 2), direction=(0, 0, 1), radius=14, height=zn,
                      resolution=14).triangulate()]
    for x in gas_users:
        ar.append(pv.Cylinder(center=(x + 200, yn + 230, (zn - 150 + 1800) / 2), direction=(0, 0, 1), radius=12,
                              height=zn - 150 - 1800, resolution=14).triangulate())
    xd = FLOOR_PLAN["ded"][0]                    # the DED's argon: down the south tray
    ar.append(pv.Cylinder(center=(gx0, (yn + 230 + ys - 200) / 2, zs - 150), direction=(0, 1, 0), radius=14,
                          height=yn + 230 - (ys - 200), resolution=14).triangulate())
    ar.append(pv.Cylinder(center=((gx0 + xd) / 2, ys - 200, zs - 150), direction=(1, 0, 0), radius=14,
                          height=xd - gx0, resolution=14).triangulate())
    ar.append(pv.Cylinder(center=(xd + 200, ys - 200, (zs - 150 + 1800) / 2), direction=(0, 0, 1), radius=12,
                          height=zs - 150 - 1800, resolution=14).triangulate())
    cyl = [pv.Cylinder(center=(gx0 - 300 + 260 * i, yn + 700, 750), direction=(0, 0, 1), radius=115, height=1500,
                       resolution=24).triangulate() for i in range(4)]
    # the ducted hood's exhaust: up from its top, behind the south cable tray, to the roof (a 180 mm duct; a layout
    # choice). hood: the hood's world bounds
    duct = None
    if hood is not None:
        z0 = hood[5]
        duct = pv.Cylinder(center=((hood[0] + hood[1]) / 2, hood[2] + 110.0, (z0 + 6200.0) / 2), direction=(0, 0, 1),
                           radius=90, height=6200.0 - z0, resolution=28).triangulate()
    # round 10: what the trays' couplings carry besides mains and Ethernet (services.py: compressed air, N2, chilled
    # water) comes from units at the back of the 800 mm gap between the Shuttles, where no MiR turns (they turn at the
    # front): the N2 generator (Parker Balston UHPN2-1100, 305 x 406 x 889 mm, services.SOURCES["n2"]), an oil-free
    # compressor for it and for the docks' air (our size), and the chiller (ThermoFlex 900, size not found: not to
    # size). A line from them goes up and over both roofs to the risers' drops.
    xg = X2 / 2                                  # the gap's middle: 1815
    units_ = {"N2 generator": (305.0, 406.0, 889.0, 200.0, (0.86, 0.87, 0.88)),
              "air compressor": (450.0, 450.0, 650.0, 660.0, (0.30, 0.45, 0.62)),
              "chiller": (420.0, 600.0, 700.0, 1160.0, (0.80, 0.81, 0.83))}
    for nm, (w, d, h, y0, col) in units_.items():
        out_units = W._box(xg - w / 2, y0, 0.0, xg + w / 2, y0 + d, h)
        parts.setdefault(nm, ([], col))[0].append(out_units)
    svc = [pv.Cylinder(center=(xg, 900.0, (950.0 + 4150.0) / 2), direction=(0, 0, 1), radius=30, height=3200.0,
                       resolution=14).triangulate(),
           pv.Cylinder(center=((900.0 + X2 + 900.0) / 2, 900.0, 4150.0), direction=(1, 0, 0), radius=30,
                       height=X2, resolution=14).triangulate()]
    for x in (900.0, X2 + 900.0):
        svc.append(pv.Cylinder(center=(x, 900.0, (V.UNIT_H + 4150.0) / 2), direction=(0, 0, 1), radius=30,
                               height=4150.0 - V.UNIT_H, resolution=14).triangulate())
    parts.setdefault("dock supply line", ([], (0.55, 0.66, 0.74)))[0].extend(svc)
    out = {"cable trays": (trays, (0.70, 0.72, 0.74)), "tray hangers": (hangers, (0.55, 0.57, 0.60)),
           "network cable": (net, (0.15, 0.40, 0.85)), "power drops": (W._merge(drops), (0.30, 0.31, 0.33)),
           "argon line": (W._merge(ar), (0.25, 0.60, 0.35)), "argon cylinders": (W._merge(cyl), (0.30, 0.55, 0.36)),
           "hood duct": (duct, (0.78, 0.79, 0.81))}
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
    "ups": (23.0, "Eaton 5PX1500RTNG2, 50.7 lb (services.SOURCES['ups'], a snippet)"),
    "reflow": (15.0, "Puhui T-962A (REFLOW)"),
    "vhx": (7.2, "Keyence VHX-7000's EA-300 controller alone; the stand and head not found (out/instruments.json)"),
}
MASS_ONE_PERSON = 23.0                         # NIOSH's load constant, kg: the most one person should lift, at best


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
    util = {}
    hood = _bounds_of(sc, F.groups["fumehood"]) if F.groups.get("fumehood") else None
    umesh, ulabel = utilities(hood)
    for nm, (mesh, col) in umesh.items():
        sc.add(f"util/{nm}", mesh, col, "util", specular=0.2)
        util[nm] = f"util/{nm}"
    L.apply_state()
    sc.apply()
    sc.add("footprints", footprints(sc, F), W.TAPE_W, "tape", specular=0.0, ambient=0.5)
    return sc, L, F, items, rigs, units, util, ulabel, vp


def add_bay_cams(sc: Scene) -> list[str]:
    """The overhead camera over each Shuttle's bay (services.py's, and a copy at X2). -> their actor names."""
    import services as S
    S.add_bay_camera(sc)
    S.add_meshes(sc, "baycam2", S.meshes_of("baybar", S.bay_parts, 0.5), "baycam2")
    sc.gmat["baycam2"] = T((X2, 0, 0))
    # the second unit as services.add_bay_camera builds the first (on its bar, no post), over Shuttle 2's bay. Round 7's
    # copy still called _add_rig with the post-mounted unit's BAY_CAM["h"], which services.py no longer has
    sc.gmat["baycamrig2"] = S.bay_at(X2)
    for k in ("pan", "head"):
        S.add_meshes(sc, f"baycamrig2{k}", S.meshes_of(f"rig_{k}", lambda k=k: S.rig_pieces()[k], 0.3),
                     f"baycamrig2{k}")
    sc.gmat["baycamrig2pan"] = S.I._R((0, 0, 1), 0.0, S.PAN_AXIS)
    sc.parent["baycamrig2pan"] = "baycamrig2"
    sc.gmat["baycamrig2head"] = S.I._R((1, 0, 0), S.BAY_CAM["tilt"], S.TILT_AXIS)
    sc.parent["baycamrig2head"] = "baycamrig2pan"
    return [nm for nm in sc.actors if sc.group_of[nm].startswith(("baycam", "baycamrig"))]


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
            grp = cab if ("cabinet" in nm or "e-stop" in nm) else name
            sc.add(f"{name}/{nm}", mesh, col, grp, **(dict(ambient=0.8) if "light" in nm else {}))
        holder, seat = P.buffer_holder()
        sc.add(f"{name}/holder", holder.translate((*A.BUFFER_LOCAL, P.AMR_TOP - 20), inplace=False), P.RACK_C, cab)
        sc.parent[cab] = name
        sc.gmat[cab] = np.eye(4)
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
            return [n for n, g in sc.group_of.items() if g == f"{nm}_cab"]
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
    # round 10: where each item's centre is in its tray (for its start on the lift table), and the two lift tables
    yc_of = {}
    for k in items:
        Mi = np.linalg.inv(sc.world(f"tray_{k}"))
        for key, g, names, _ in items[k]:
            bb = _bounds_of(sc, names, Mi)
            yc_of[(k, g)] = 0.0 if bb is None else (bb[2] + bb[3]) / 2
    tables = {}
    for u, xu in V.SHUTTLE_X.items():
        g = f"lift_table{u}"
        for nm, (mesh, col) in lift_table_parts().items():
            sc.add(f"{g}/{nm}", mesh, col, g, specular=0.3)
        sc.gmat[g] = T((xu, LIFT_TABLE_Y, 0.0))
        tables[u] = sc.members(g)
    A.hide(L, L.groups(*vlm_groups, *u2, *tray_groups) + eq + machines + layout + chargers + unit_names +
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
    ulbls = [("cable tray: power and network", (5200, W.Y_FACE_N + 700, 4400)),
             ("argon cylinders", (-9500, W.Y_FACE_N + 1400, 1500)),
             ("VLM supply, 208 V 3-phase", (900, W.Y_FACE_N + 640, 4300)),
             ("N2 generator, compressor, chiller", (X2 / 2, 900.0, 950.0))]
    if ulabel is not None:
        ulbls.append(("power and network drop", ulabel))
    sc.step(f"3/{n}", "Utilities: cable trays over both rows. A drop comes down to every station and ends in a grey "
            "junction box with sockets and a network port. 208 V three-phase goes to each VLM (#53), argon from a "
            "cylinder manifold to the glovebox, the rePowder, the Aconity and the DED, and a duct up from the fume "
            "hood. Between the Shuttles, at the back: an N2 generator, a compressor and a chiller for the trays' "
            "couplings. Layout choices, not a design.", 4.2, util_on, hold=2.0, cam_to=CAM_UTIL,
            labels=W.auto(sc, CAM_UTIL, ulbls))
    # ------------------------------------------------------------------ 4. the VLMs
    s = A.slide_in
    sc.step(f"4/{n}", "Two Kardex Shuttle XP 500s go together where their footprints are taped, 800 mm apart: base "
            "frames, posts, storage columns.", 2.6,
            A.both(s(L, ["base", "u2_base"], (0, 0, 900)), s(L, ["posts", "u2_posts"], (0, 0, 1800)),
                   s(L, ["col_front", "col_rear", "u2_col_front", "u2_col_rear"], (2600, 0, 0))),
            hold=0.3, cam_to=CAM_VLM)
    passive = [k for k in trays if k in PASSIVE]
    pas = ", ".join(passive[:-1]) + f" and {passive[-1]}" if len(passive) > 1 else "".join(passive)
    sc.step(f"4/{n}", f"The extractors and their drives, then {len(trays)} empty trays, A to {max(trays)}: "
            f"{len(trays) - len(passive)} electrified, each with its dock plate at the back right, and "
            f"{len(passive)} plain ones for storage ({pas}).", 2.6,
            A.both(s(L, ["lift_rails", "u2_lift_rails"], (0, 0, 2500)), s(L, ["drive", "u2_drive"], (0, 0, 1400)),
                   s(L, ["lift", "belts", "u2_lift", "u2_belts"], (0, 0, 2400)), s(L, tray_groups, (3200, 0, 0))),
            hold=0.3)
    sc.step(f"4/{n}", "The cladding, the openings (996 mm tall), the consoles and the shutters.", 2.2,
            A.both(s(L, ["skin_L", "u2_skin_L"], (-900, 0, 0)), s(L, ["skin_R", "u2_skin_R"], (900, 0, 0)),
                   s(L, ["skin_back", "u2_skin_back"], (0, 900, 0)), s(L, ["skin_top", "u2_skin_top"], (0, 0, 900)),
                   s(L, ["skin_front", "bay", "console", "shutter", "u2_skin_front", "u2_bay", "u2_console",
                         "u2_shutter"], (0, -900, 0))),
            hold=0.6)
    L.apply_state()
    # ------------------------------------------------------------------ 5. the floor machines
    order = [k for k in ("glovebox", "repowder", "sieve_cell", "aconity", "packaging", "instron_floor", "instron_small",
                         "fumehood", "ded", "wire_edm", *R8_MERGED["floor"]) if k in F.groups and F.groups[k]]
    fs = []
    for k in order:
        root = {"repowder": "repowder", "aconity": "aconity", "sieve_cell": "sieve_cell"}.get(k, f"wh_{k}:body")
        row = FLOOR_PLAN[k][1]
        names = F.groups[k]
        roots = [root] + (["wh_sieve:body"] if k == "sieve_cell" and "sieve_cell" in F.rigs else []) + \
            ([f"bench_{k}"] if k in W.BENCH else [])
        dy = -2600 if row == "N" or k in R8_MERGED["floor"] else 2600   # the scale-up machines come in from outside
        fs.append(s(L, roots, (0, dy, 0), names=names))
    late = [k for k in R8_MERGED["floor"] if k in order]      # round 8's scale-up machines, past the south row's ends
    main = [k for k in order if k not in late]
    fs_main = [f for k, f in zip(order, fs) if k not in late]
    sc.step(f"5/{n}", "The floor machines are rigged in on pallet jacks and machine skates (the Aconity MIDI is "
            "1450 kg, the 100 kN Instron 799 kg), fronts to the aisle: the glovebox (its antechamber to the aisle), "
            "the rePowder, the sieving cell, the Aconity MIDI, the packaging station; across the aisle the two "
            "Instrons, the ducted fume hood, the DED and the wire EDM.", 5.8,
            stagger(fs_main, overlap=0.36), hold=1.2, cam_to=CAM_FLOOR,
            labels=W.auto(sc, CAM_FLOOR, W.floor_labels(F, main, have)))
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
    sc.step(f"6/{n}", "Two MiR Charge 48V chargers go in, then the first MiR250 rolls onto its charging plate.", 1.4,
            chargers_on, hold=0.1, cam_to=CAM_UNIT)
    base_names = u0.part_names("base")

    def roll(u):
        for nm in base_names:
            sc.alpha[nm] = min(1.0, u * 4)
        u0.set((x, start[1] + (y - start[1]) * u, hd))
    sc.step(f"6/{n}", "Two MiR Charge 48V chargers go in, then the first MiR250 rolls onto its charging plate.", 2.0,
            roll, hold=0.2, labels=[("MiR250, 800 x 580 x 300 mm", (x, y, 300), (0.20, 0.60))])
    cab_names = u0.part_names("cabinet")

    def cabinet(u):
        sc.gmat[f"{u0.name}_cab"] = T((0, 0, 700 * (1 - u)))
        for nm in cab_names:
            sc.alpha[nm] = min(1.0, u * 3)
    sc.step(f"6/{n}", "Its cabinet goes on top: it carries the arm and holds the UR control box.", 1.6, cabinet, hold=0.2)
    cb_names = u0.part_names("control box")
    cab_body = [nm for nm in cab_names if "holder" not in nm]

    def control_box(u):
        sc.gmat[f"{u0.name}_cb"] = T((0, -700 * (1 - u), 0))
        for nm in cb_names:
            sc.alpha[nm] = min(1.0, u * 4)
        for nm in cab_body:
            sc.alpha[nm] = 1.0 - 0.7 * math.sin(math.pi * u)
    sc.step(f"6/{n}", "The UR control box (460 x 449 x 254 mm, 12 kg) goes into the cabinet.", 1.8, control_box,
            hold=0.2, labels=[("UR control box", (x, y, 600), (0.20, 0.42))])
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
    others = [nm for uu in units if uu is not u0 for nm in uu.all_names()]
    q_ready = np.radians((-90.0, -100.0, 110.0, -100.0, -90.0, 0.0))

    def wake(u):
        for nm in others:
            sc.alpha[nm] = u
    sc.step(f"6/{n}", "It wakes up and stretches. The second unit is built the same way at the other charger.", 1.8,
            A.both(rb.joint_to(q_ready), wake), hold=0.2)
    sc.step(f"6/{n}", "It wakes up and stretches. The second unit is built the same way at the other charger.", 1.4,
            rb.joint_to(A.PARK_RAD), hold=0.4)
    # ------------------------------------------------------------------ 7. the trays
    def tables_on(u):
        for nm in (n for v in tables.values() for n in v):
            sc.alpha[nm] = u
    heavy = sorted(((m, key) for key, (m, _) in MASS_KG.items() if m and m > MASS_ONE_PERSON), reverse=True)
    sc.step(f"7/{n}", "Loading, drawn see-through. Most of what goes on a tray weighs 20-110 kg (the S2 PUMA "
            f"{heavy[0][0]:.0f} kg, each UPS 23), more than the arm's 12.5 kg or one person should lift (NIOSH: 23 kg), "
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
            for key, g, names, nm in lst:
                tr = V.Y_OPEN + yc_of.get((k, g), 0.0) - LIFT_START_Y     # from the lift table's deck
                fs.append(rig_in(sc, g, names, travel=tr) if key != "rack" and not g.startswith("eq_") else
                          A.item_in(L, g, travel=tr))
                if key not in ("ups", "cam"):
                    lbls.append((nm, tuple(np.array(sc.world(g)[:3, 3]) + (0, 0, 420))))
            ncam = sum(1 for it in lst if it[0] == "cam")
            extra = ", its UPS" + (f" and {ncam} camera post{'s' if ncam > 1 else ''}" if ncam else "")
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
    u2_cam = [nm for nm in cam_names if sc.group_of[nm].startswith(("baycam2", "baycamrig2"))]
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
        tgt = np.array([x, *services.bay_cam_point()[1:]])
        view = [(x + BAY_EYE[0], BAY_EYE[1], BAY_EYE[2]), tuple(tgt + (0, 0, -60)), (0, 0, 1)]
        lbl = [(f"Shuttle {unit}'s overhead camera: a Pi 5 with the HQ Camera (16 mm lens) and the Camera "
                "Module 3 Wide, on a pan-tilt head", tuple(tgt), (0.56, 0.12)),
               ("on a 2020 bar across the back of the bay, under the tray stored over the opening",
                (x - 700.0, services.BAY_CAM["y"], services.BAY_CAM["bar_z"]), (0.18, 0.27))]
        if i == 0:
            cap = (f"The bay cameras go on, one over each opening: Shuttle {unit}'s first, seen from where an operator "
                   "stands, eyes at 1.6 m (the cladding drawn solid for it). It sits up under the header at the back "
                   "of the bay and looks down over the presented tray.")
            sc.step(f"8/{n}", cap, 1.4, A.both(L.skin(0.0), cams_on(unit, tables=True)), hold=1.0, cam_to=view,
                    labels=lbl, view_angle_to=BAY_VIEW_ANGLE)
        else:
            cap = (f"Then Shuttle {unit}'s: the same unit on the same bar. Together with the D405 on the arm's wrist, "
                   "it sees what is on every tray the Shuttle presents.")
            sc.step(f"8/{n}", cap, 1.3, cams_on(unit), hold=1.0, cam_to=view, labels=lbl)
    pas = ", ".join(sorted(PASSIVE)[:-1]) + f" and {sorted(PASSIVE)[-1]}" if len(PASSIVE) > 1 else "".join(PASSIVE)
    sc.step(f"8/{n}", f"Every tray with instruments carries its own stream cameras; the storage trays ({pas}) carry "
            "none: the bay camera takes their stock whenever one is presented, the only time a jar or a sample can "
            "come or go.", 1.0, L.skin(1.0), hold=0.6, cam_to=CAM_VLM, view_angle_to=va0,
            labels=W.auto(sc, CAM_VLM, [("overhead camera at the bay", services.bay_cam_point()),
                                        ("overhead camera at the bay", (X2, *services.bay_cam_point()[1:]))]))
    # ------------------------------------------------------------------ 9. orbit
    L.apply_state()
    cap = (f"Set up: two Shuttles with trays A-{max(trays)}, the floor machines, two MiR250 + UR10e units on charge.")
    sc.step(f"9/{n}", cap, 1.2, L.skin(0.0), hold=0.0)
    for i, cam in enumerate(ORBIT):
        last = i == len(ORBIT) - 1
        sc.step(f"9/{n}", cap, 2.2, None, hold=2.0 if last else 0.0, cam_to=cam, still=last)
    return sc.save()


# ================================================================================================ the checks
def _fcl_of(sc: Scene, names, Mi):
    """One FCL mesh of the visible actors `names`, in the frame Mi maps to (the tray's)."""
    import fcl
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
    bvh = fcl.BVHModel()
    v, f = np.vstack(vs), np.vstack(fs)
    bvh.beginModel(len(v), len(f))
    bvh.addSubModel(v, f)
    bvh.endModel()
    return fcl.CollisionObject(bvh, fcl.Transform())


def tray_parts(sc: Scene, items: dict, k: str) -> list:
    """[(label, kind, (x0, x1, y0, y1, z0, z1))] on tray k, in the tray's frame: its items, its UPS, its dock plate and
    tray lines, and each camera rig in two parts (the post on its foot, and the head with its yoke)."""
    Mi = np.linalg.inv(sc.world(f"tray_{k}"))
    out = []
    for key, g, names, nm in items.get(k, []):
        if key == "cam":
            post = [n for n in names if sc.group_of[n] == g]
            head = [n for n in names if sc.group_of[n] != g]
            out.append((f"{g} post", "cam", _bounds_of(sc, post, Mi), post))
            out.append((f"{g} head", "cam", _bounds_of(sc, head, Mi), head))
            continue
        out.append((nm if key != "ups" else "UPS", "ups" if key == "ups" else "item", _bounds_of(sc, names, Mi), names))
    plate = [n for n in sc.actors if n.startswith((f"plate_{k}/", f"lines_{k}/"))]
    out.append(("dock plate and tray lines", "plate", _bounds_of(sc, plate, Mi), plate))
    return [o for o in out if o[2] is not None]


def check_trays(sc: Scene, items: dict) -> dict:
    """Each tray's parts against each other: their boxes first, then, where two boxes overlap, the meshes themselves
    (FCL), so a camera head over an instrument's low corner isn't a clash."""
    import fcl
    inside = (V.TRAY_W / 2 - 12.0, V.TRAY_D / 2 - 12.0)
    edge = (V.TRAY_W / 2, V.TRAY_D / 2)
    rep = {}
    for k in ORDER:
        parts = tray_parts(sc, items, k)
        Mi = np.linalg.inv(sc.world(f"tray_{k}"))
        objs = {}

        def obj(i):
            if i not in objs:
                objs[i] = _fcl_of(sc, parts[i][3], Mi)
            return objs[i]

        def hit(i, j):
            a, b = obj(i), obj(j)
            if a is None or b is None:
                return True
            res = fcl.CollisionResult()
            return fcl.collide(a, b, fcl.CollisionRequest(), res) > 0 or res.is_collision
        rows, top = [], 0.0
        for i, (lbl, kind, b, _) in enumerate(parts):
            over = []
            for j, (lbl2, kind2, b2, _) in enumerate(parts):
                if j == i or (kind == kind2 == "cam" and lbl.split()[0] == lbl2.split()[0]):
                    continue
                if {kind, kind2} <= {"ups", "plate", "cam"} and kind != kind2:
                    continue                             # services.py's own parts against each other: its call
                if all(b[2 * a] < b2[2 * a + 1] - 1.0 and b2[2 * a] < b[2 * a + 1] - 1.0 for a in range(3)) and \
                        hit(min(i, j), max(i, j)):
                    over.append(lbl2)
            lim = edge if kind == "cam" else inside           # a camera head may lean over the rim, not the edge
            rim = kind == "plate" or (b[0] >= -lim[0] - 0.5 and b[1] <= lim[0] + 0.5 and b[2] >= -lim[1] - 0.5
                                      and b[3] <= lim[1] + 0.5)
            h = b[5] - V.T_FLOOR
            top = max(top, b[5])
            rows.append(dict(item=lbl, kind=kind, box_mm=[round(float(v)) for v in b], height_mm=round(float(h), 1),
                             under_goods_height=bool(h <= V.MAX_GOODS_H + 0.5), inside_rim=bool(rim),
                             overlaps=over))
        slot = TRAYS[k][0]
        need = V.PITCH * math.ceil((top + V.GOODS_CLEAR - 1e-6) / V.PITCH)
        rep[k] = dict(role=TRAYS[k][1], slot=slot, shuttle=V.SLOT_SHUTTLE[slot], slot_z_mm=V.SLOTS[slot][1],
                      span_mm=V.SPAN[slot], tallest_mm=round(float(top - V.T_FLOOR), 1), span_needed_mm=need,
                      span_ok=bool(need <= V.SPAN[slot]), items=rows,
                      ok=bool(need <= V.SPAN[slot] and all(not r["overlaps"] and r["inside_rim"] and
                                                           r["under_goods_height"] for r in rows)))
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
    """Every tray from above, its items, UPS, dock plate and camera posts, with its slot; and both Shuttles' columns."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    cols = {"item": "#4a7bd0", "ups": "#e0a020", "plate": "#c8553d", "cam": "#2e9c6a"}
    trays = [k for k in ORDER]
    nrow = math.ceil(len(trays) / 2)
    fig = plt.figure(figsize=(18, 2.35 * nrow), dpi=110)
    gs = fig.add_gridspec(nrow, 3, width_ratios=[1, 1, 0.55], wspace=0.06, hspace=0.55, top=0.95)
    for i, k in enumerate(trays):
        ax = fig.add_subplot(gs[i % nrow, i // nrow])
        r = rep[k]
        ax.add_patch(Rectangle((-V.TRAY_W / 2, -V.TRAY_D / 2), V.TRAY_W, V.TRAY_D, fc="#eceef0", ec="#555", lw=1.0))
        ax.add_patch(Rectangle((-V.TRAY_W / 2 + 12, -V.TRAY_D / 2 + 12), V.TRAY_W - 24, V.TRAY_D - 24, fc="none",
                               ec="#999", lw=0.6, ls=":"))
        for it in r["items"]:
            x0, x1, y0, y1 = it["box_mm"][:4]
            bad = it["overlaps"] or not it["inside_rim"] or not it["under_goods_height"]
            kind = it["kind"]
            alpha = 0.35 if it["item"].endswith("head") else 0.75
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=cols[kind], alpha=alpha,
                                   ec="red" if bad else "#222", lw=1.4 if bad else 0.5))
            if kind == "item":
                ax.text((x0 + x1) / 2, (y0 + y1) / 2, f"{it['item'][:26]}\n{it['height_mm']:.0f} mm", ha="center",
                        va="center", fontsize=6.0, color="white")
        ax.set_xlim(-V.TRAY_W / 2 - 30, V.TRAY_W / 2 + 30)
        ax.set_ylim(-V.TRAY_D / 2 - 30, V.TRAY_D / 2 + 30)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ok = "fits" if r["ok"] else "CHECK"
        pas = " (passive: no UPS, dock plate or cameras)" if k in PASSIVE else ""
        ax.set_title(f"Tray {k}: {r['role']}{pas}\nShuttle {r['shuttle']}, slot {r['slot']}: {r['span_mm']:.0f} mm "
                     f"(needs {r['span_needed_mm']:.0f}; tallest {r['tallest_mm']:.0f}): {ok}", fontsize=8,
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
    fig.suptitle("The tray plan: every tray from above, front (the opening) at the bottom. Items blue, UPS amber, "
                 "dock plate and tray lines red, camera posts and heads green; a red outline is a clash.\nRight: the "
                 "two Shuttles' columns, each slot as tall as its tray needs, and what each column has left (dashed) "
                 "(setup_lab.py fit)", fontsize=10.5,
                 x=0.12, y=0.995, ha="left")
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
            if m is None:
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
               method="setup_lab.py fit: each item, UPS, dock plate (with its tray lines) and camera rig measured from "
                      "its meshes as drawn, an axis-aligned box in the tray's frame; overlaps are 3-D box overlaps "
                      "of more than 1 mm; a slot needs the tallest top + 20 mm, on the 25 mm pitch")
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
            bad = [(it["item"], it["overlaps"], it["inside_rim"], it["under_goods_height"]) for it in r["items"]
                   if it["overlaps"] or not it["inside_rim"] or not it["under_goods_height"]]
            print(f"tray {k} {r['slot']}: span {r['span_mm']:.0f}, needs {r['span_needed_mm']:.0f} "
                  f"(tallest {r['tallest_mm']:.0f}) {'ok' if r['ok'] else 'CHECK'} {bad if bad else ''}")
        if "-v" in args:
            for k, r in out["trays"].items():
                print("tray", k)
                for it in r["items"]:
                    print("   ", it["item"][:40].ljust(40), it["box_mm"], it["overlaps"], it["inside_rim"])
        for k, d in out["floor"]["docks"].items():
            print(f"dock {k}: {'ok' if d['ok'] else 'CHECK'} pivot {d['pivot']} {d['hits']}")
        print("machines in the aisle:", out["floor"]["machines_in_aisle"])
    else:
        print(movie(data, idata), flush=True)
        if not PREVIEW:
            print(line.mp4_to_gif(OUT / "mp4" / "setup_lab.mp4", OUT / "setup_lab.gif", **W.GIF), flush=True)
