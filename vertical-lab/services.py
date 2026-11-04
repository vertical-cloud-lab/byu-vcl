"""Tray services for the vertical cloud lab (#303): docking couplers on the trays, the stream cameras, the cabling, and
the utilities and their heat.

    xvfb-run -a python3 services.py services      # the dock close-up            -> out/vlm_services.gif, out/mp4/...
    xvfb-run -a python3 services.py hookups       # one tray's hookups and UPS   -> out/vlm_hookups.gif, out/mp4/...
    xvfb-run -a python3 services.py baycam        # the bay camera and its view  -> out/bay_camera.gif, out/mp4/...
    xvfb-run -a python3 services.py cabling       # the line with its cabling    -> out/vlm_cabling.gif, out/mp4/...
    python3 services.py clearance                 # docks against the lift       -> out/dock_lift_clearance.png, .json
    python3 services.py json                      # out/services.json (heat budget), out/cabling.json (circuits)
    python3 services.py join                      # out/mp4/vlm_services_all.mp4 from the clips above
    xvfb-run -a python3 tour.py tray_dock stream_cam   # the two models on their own -> out/instruments/

The retractable line (an igus e-spool on the rear wall, round 4's ``tether`` clip) was dropped on PR #318: "Let's
remove the retractable line option for now. It overcomplicates things for now." notes/services.md says why it was
a poor fit anyway.

What Kardex gives (#53): a tray has power in its storage slot and again at the opening, not while the extractor carries
it. The dealer offered a quick-connect cord to the device on the tray. This module puts every service a tray needs
(mains, Ethernet, compressed air, N2, chilled water) through one automatic multi-media coupling, a Staubli CombiTac,
whose plate is on the tray and whose actuated dock is in the side wall of each slot and of the bay. The tray carries
a UPS for the seconds it is in transit.

Frame as in ``vlm.py``: x to the right and y away from you facing the opening, z up from the floor, mm. A tray's own
frame has its origin at the centre of its floor's underside, y towards its back; trays are never turned.

Every figure with a source is in ``SOURCES``. Estimates say so.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np

import instruments as I
import vlm as V
from instruments import Instrument, Joint, _piece

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
from common import box, cyl, hose, rbox  # noqa: E402

OUT = HERE / "out"

# ===================================================================================================== sources
SOURCES = {
    "kardex_tray_power": "#53: 'the trays will not retain power while in motion. They will only have power when stored, "
                         "or again when they arrive at the delivery bay'; the dealer offered 'a quick connect cord' to "
                         "the device on the tray. Kardex's own Shuttle option list shows no powered-tray or media "
                         "option (kardex.com/products/vertical-lift/kardex-shuttle).",
    "kardex_supply": "#53: 208 V three-phase. A used XP 500 2450x864 listed '3/N/PE 400V, 17A' (machineseeker, page now "
                     "404); used XP listings show 17 A, 8.6 kVA.",
    "combitac_align4": "Staubli CombiTac uniq catalogue (CT-Main-11014009-en) p.80-81: CombiTac align 4, misalignment "
                       "compensation radial 4 mm, angular +-2 deg; 100,000 mating cycles; the plug side's pins guide, "
                       "the socket side is conical. p.82: 'the customer must provide a stable guide system, e.g. with "
                       "mechanical pins'. p.87: largest gap between mated carriers 1-2 mm.",
    "combitac_power": "CombiTac catalogue p.26: 'O 3 mm power unit up to 39 A', 600 V (pollution degree 2/CAT II).",
    "combitac_data": "CombiTac catalogue p.46-49: 10 Gbit module, 'Ethernet up to 10 Gbit/s (Cat6a or higher)', RJ45 "
                     "or M12 X-coded, 100,000 cycles, 14 N sliding force, 22 mm wide.",
    "combitac_air": "CombiTac catalogue p.61-69: RCT06 pneumatic, 6 mm bore, shut-off on one side, 15 bar; "
                    "'Connecting and disconnecting under pressure is prohibited.'",
    "combitac_fluid": "CombiTac catalogue p.70-75: SCT03 (G1/8) and LCT06 (G1/4), 'leakproof, shut-off on both "
                      "sides', 15 bar; LCT06 8.48 L/min at 5 m/s, counter force 135 N at 10 bar; pressure drop "
                      "0.2-0.3 bar. Fluid couplings 'can also be used for pneumatic applications'.",
    "odu_dock": "ODU-MAC Silver-Line P4+ docking frame: 'axial 1mm, radial +/- 4mm', floating, 100,000 cycles "
                "(ODU via adsgroup.org.uk).",
    "harting_dock": "Harting Han 6 Mod Docking Frame 09140061716: floating +-2 mm, lock-in +-4 mm, >=10,000 cycles "
                    "(harting.com).",
    "cpc_everis": "CPC Everis BLQ6 blind-mate liquid coupling: Cv ~2.2, vacuum to 8.3 bar, 'disconnect under pressure "
                  "without drips' (cpcworldwide.com; search snippet, page not opened).",
    "kardex_speeds": "Kardex Shuttle XP brochure: up to 2.0 m/s vertical, 0.7 m/s in and out (vlm.py).",
    "pi5": "raspberrypi.com: Pi 5 '5V/5A DC power via USB-C'; 27 W USB-C supply recommended; typical bare-board "
           "active current 800 mA (4 W); 'PoE+ support (requires separate PoE+ HAT)'. The official PoE+ HAT lists only "
           "the Pi 4 and 3B+; Waveshare's PoE HAT (H)/(J) are sold for the Pi 5 (5 V 5 A max).",
    "pi5_drawings": "DAL PR #189 viewport_mounts.fs, from Raspberry Pi's drawings: Pi 5 85 x 56, 4 x M2.5 on 58 x 49; "
                    "Active Cooler 63.5 x 42.5, ports to 17.6 mm; HQ Camera 38 x 38 board, M12 holder 17 x 17 x 8; "
                    "Camera Module 3 25 x 23.862, lens axis 14.4 mm from the far edge.",
    "hq_camera": "raspberrypi.com: HQ Camera 38 x 38 x 18.4 mm excluding lens, 30.4 g, C/CS or M12 mount, 1/4-20 "
                 "tripod mount, 200 mm ribbon; IMX477, 7.9 mm sensor diagonal.",
    "cm3_wide": "raspberrypi.com: Camera Module 3 Wide about 25 x 24 x 12.4 mm, 4 g, 102 deg horizontal, 67 deg "
                "vertical, 120 deg diagonal; 200 mm ribbon. Pi 5 camera cables: 200, 300 and 500 mm.",
    "hq_sensor": "Raspberry Pi HQ Camera product brief: Sony IMX477R, 12.3 MP, 4056 x 3040 pixels of 1.55 x 1.55 um "
                 "(so 6.29 x 4.71 mm), 7.9 mm sensor diagonal. With a 16 mm lens: 2 atan(6.29 / 32) = 22.2 deg across, "
                 "16.8 deg up and down, 27.6 deg diagonally, as Raspberry Pi's lens table gives (22.2 x 16.7).",
    "lab_units": "DAL PR #189 (atomizer-viewport-cameras): the front unit pairs an HQ Camera (M12) with a 16 mm M12 lens "
                 "(about O16 x 18 mm) and a Camera Module 3 Wide side by side, boards 2 mm apart, HQ lens 15 mm left "
                 "of the axis and the Wide's 18.5 mm right; Pi 5 4 GB with Active Cooler and 27 W PSU; black PETG; "
                 "the top unit rides a 2020 extrusion arm. DAL #147: 1/4-20 insert to a bought arm rather than a "
                 "printed ball joint; cameras within the 200/300/500 mm ribbons of the board.",
    "robot_arms_models": "robot-arms PR #10 (branch claude/issue-239-20260926-2347), piper-camera-mount/cad/"
                         "piper_mount.py: make_pi5_local (Pi 5 board, holes, connectors), make_hq_camera_local "
                         "(HQ board, CS seat 14.43 mm, O36 back-focus ring, O34.8 housing, tripod mount and "
                         "lock block off Raspberry Pi's drawing RP-008200-DS-1), make_cm_camera_local (Camera "
                         "Module 3 board 25 x 23.862, housing 10.8, lens 8.3 mm proud); lenses.py: the 16 mm C-mount "
                         "lens, O39 x 50 mm, 133.7 g, 22.2 x 16.7 deg on the HQ, with its 5 mm C-CS adapter.",
    "robot_arms_fixtures": "robot-arms PR #40 (branch claude/issue-24-20261021-2053), docs/issue-24/camera-fixtures: "
                           "2020 posts in printed 90 x 90 mm feet with 50 mm sockets, wedges and Pi 5 plates on M5 "
                           "drop-in T-nuts in the slot, a Camera Module 3 case on M2 standoffs, ribbon clips; one "
                           "Pi per camera post, so a 200-300 mm ribbon is enough.",
    "ups": "Eaton 5PX1500RTNG2 (120 V, 1500 VA, rack/tower 2U): 3.4 x 17.2 x 17.6 in (86 x 437 x 447 mm), weight "
           "'50.7' (lb, about 23 kg), farnell.com data sheet (search snippet); 44 min at 300 W (230 V model, retailer "
           "listing). Heat dissipation not published. APC SMT1500RM2UC for comparison: 432 x 477 x 86 mm, 26.5 kg, "
           "1440 VA / 1000 W, 98.9 % efficient at 50 % load (ENERGY STAR).",
    "n2": "Parker Balston UHPN2-1100: 35 in H x 12 in W x 16 in D (889 x 305 x 406 mm), 50 kg (VWR), 120 VAC 60 Hz, "
          "500-1100 cc/min at 99.9999 %, needs compressed air at 60-125 psig, no compressor of its own (govsci.com, "
          "gmi-inc.com, marshallscientific.com; search snippets). Peak Precision Nitrogen 1000: 1000 cc/min, 26 kg, no "
          "compressor (Peak's sheet, snippet).",
    "chiller": "Thermo Scientific ThermoFlex 900: up to 900 W of cooling at a +20 C setpoint and 25 C ambient (60 Hz), "
               "5-40 C, pump 15.1 L/min at 4.1 bar (thermofisher.com TF900, snippet). Its size and electrical input "
               "were not found.",
}

# Electrical figures for what the trays and the line carry: (watts used for the budget, kind, source). 'kind' says what
# the figure is: 'published' is the maker's own figure; 'snippet' a search-result figure not opened; 'estimate' ours.
POWER = {
    "ot2": (180.0, "published", "Opentrons OT-2 specs: idle 90-120 W, active 100-180 W (docs.opentrons.com)"),
    "cubxl": (100.0, "estimate", "the lab's gantry (Genmitsu PROVerXL 4030 frame, #199): no rating found; 100 W is ours"),
    "carousel": (40.0, "estimate", "the multi-doser's steppers, actuator and board (powder-doser #185): ours, 40 W"),
    "h2d": (1050.0, "snippet", "Bambu Lab H2D: average 1050 W; max 1320 W at 110 V for under 3 min (bambulab.com, "
                               "search snippet)"),
    "a1mini": (150.0, "snippet", "Bambu Lab A1 mini: max power 150 W (Bambu's TDS via a retailer)"),
    "sem": (500.0, "snippet", "Hitachi TM4000PlusIII: 'Single phase AC100-240 V ... 500 VA', PC separate (Series III "
                              "brochure; the PlusII's figure was not found)"),
    "xrd": (600.0, "published", "Rigaku MiniFlex (6th generation; the 600 before it had the same tube): '600 W X-ray "
                                "tube', '1-phase, 100-240 V' (rigaku.com); the "
                                "total draw was not found, so this counts the tube alone"),
    "openflexure_v7": (10.0, "estimate", "a Pi and three small steppers: ours, 10 W"),
    "openflexure_delta": (10.0, "estimate", "the same: ours, 10 W"),
    "openflexure_array": (60.0, "estimate", "six OpenFlexures (4 x v7, 2 x Delta), a Pi and three small steppers each: "
                                            "ours, 10 W each"),
    "pip": (200.0, "estimate", "Plastometrex PLX-Benchtop: no rating found; 200 W is ours"),
    "nanoindenter": (200.0, "estimate", "KLA iMicro: no rating found; 200 W is ours"),
    "mastersizer": (200.0, "snippet", "Malvern Mastersizer 3000+ Ultra: '50 W (no dispersion) up to 200 W' "
                                      "(DirectIndustry, snippet)"),
    "polisher": (740.0, "estimate", "LECO PX500 (the lab's): LECO publishes no rating, so this is the Buehler "
                                    "EcoMet 30's, a machine of the same class: base motor 440 W, semi-automatic head "
                                    "300 W (distributors' sheets, snippets)"),
    "furnace": (2800.0, "published", "Nabertherm NAT 15/65: connected load 2.8 kW, 1-phase (nabertherm.com)"),
    "pi_unit": (4.0, "published", "Raspberry Pi 5: typical bare-board active current 800 mA at 5 V; the supply is "
                                  "rated 27 W (raspberrypi.com). Cameras add well under 1 W"),
    "ups_loss_frac": (0.03, "estimate", "the UPS's own loss: Eaton publishes none; APC's SMT1500RM2UC is 98.9 % "
                                        "efficient at 50 % load (ENERGY STAR), so 3 % covers charging as well"),
}

TRAY_ITEMS = {      # what's on each tray (animate.LOADS, line.TRAY_LOADS)
    "A": ["cubxl", "ot2"], "B": ["carousel"], "C": ["h2d", "a1mini"],
    "D": ["sem", "xrd", "openflexure_array"], "E": ["pip", "nanoindenter", "mastersizer"],
    "F": ["polisher", "furnace"],
}
HOME = {"A": "R2", "B": "R3", "C": "F1", "D": "R1", "E": "R4", "F": "F2"}

# ===================================================================================================== materials
MATERIALS = {
    "svc_power": (0.96, 0.55, 0.10, 1.0, 0.3),      # orange: mains
    "svc_data": (0.18, 0.68, 0.32, 1.0, 0.3),       # green: Ethernet
    "svc_air": (0.55, 0.80, 0.95, 1.0, 0.3),        # light blue: compressed dry air
    "svc_n2": (0.55, 0.38, 0.78, 1.0, 0.3),         # purple: nitrogen
    "svc_cws": (0.12, 0.36, 0.85, 1.0, 0.3),        # blue: chilled water supply
    "svc_cwr": (0.86, 0.18, 0.18, 1.0, 0.3),        # red: chilled water return
    "svc_plate": (0.30, 0.31, 0.33, 1.0, 0.5),      # anodised carrier plates
    "svc_housing": (0.20, 0.21, 0.23, 0.55, 0.3),   # the dock's actuator housing, drawn see-through
    "svc_alu": (0.78, 0.79, 0.81, 1.0, 0.6),        # 2020 extrusion
    "svc_steel": (0.74, 0.75, 0.77, 1.0, 0.8),      # guide pins
    "svc_print": (0.12, 0.12, 0.13, 1.0, 0.3),      # black PETG, as in DAL PR #189
    "svc_pcb": (0.05, 0.42, 0.20, 1.0, 0.3),
    "svc_lens": (0.04, 0.04, 0.05, 1.0, 0.9),
    "svc_ribbon": (0.93, 0.93, 0.90, 1.0, 0.2),     # the cameras' flat ribbons
    "svc_petg": (0.27, 0.28, 0.30, 1.0, 0.25),      # the camera mount's printed parts, dark grey PETG
    "svc_port": (0.80, 0.81, 0.83, 1.0, 0.7),       # USB and Ethernet shells
    "svc_cooler": (0.62, 0.64, 0.67, 1.0, 0.6),     # the Active Cooler's heatsink
    "svc_fan": (0.10, 0.10, 0.11, 1.0, 0.3),
    "svc_glass": (0.55, 0.80, 0.95, 0.6, 0.9),
    "svc_ups": (0.16, 0.17, 0.18, 1.0, 0.3),
    "svc_ups_face": (0.30, 0.32, 0.35, 1.0, 0.4),
    "svc_screen": (0.18, 0.40, 0.62, 1.0, 0.8),
    "svc_tray": (0.42, 0.45, 0.50, 1.0, 0.3),       # the tray pan (vlm_tray)
    "svc_wall": (0.78, 0.80, 0.83, 0.35, 0.1),      # a column side wall (vlm_wall), see-through
    "svc_rib": (0.66, 0.68, 0.71, 1.0, 0.3),
    "svc_ladder": (0.70, 0.71, 0.73, 1.0, 0.6),     # galvanised ladder tray
    "svc_chain": (0.15, 0.15, 0.16, 1.0, 0.3),      # an energy chain
    "svc_cabinet": (0.86, 0.87, 0.86, 1.0, 0.3),
}
MEDIA = [   # (key, label for the leader lines, material, coupling)
    ("power", "mains: L1, L2, N, PE", "svc_power", "4 x O3 mm power units, 39 A each"),
    ("data", "Ethernet, Cat 6A", "svc_data", "10 Gbit module, RJ45"),
    ("air", "compressed air", "svc_air", "RCT06, 6 mm, shut-off"),
    ("n2", "nitrogen", "svc_n2", "SCT03, shut-off both sides"),
    ("cws", "chilled water in", "svc_cws", "LCT06, shut-off both sides"),
    ("cwr", "chilled water out", "svc_cwr", "LCT06, shut-off both sides"),
]

# ===================================================================================================== the coupling
# One plate per tray, at its back right corner, facing out through the tray's right-hand side (+x). A plate on the
# back edge itself would face the rear wall in a rear-column slot but the shaft in a front-column slot and at the
# opening, where the dock would sit in the extractor's path and the shutter's (see notes/services.md). Trays are
# never turned, so a side plate meets an identical dock in every slot and in the bay, and the dock's 60 mm stroke is
# across the tray's travel, out of the way of the extractor and the shutter.
# The plate's face is sunk 6 mm inside the tray's side (PR #318 review, "are any of the docks going to interfere with
# the lift itself?", dock_clearance()): the tray rides the extractor 5 mm from its carriages, and with the face flush
# the inserts, 1.5 mm proud, passed them at 3.5 mm. Now nothing on a tray stands proud of its side.
PLATE_Y = V.TRAY_D / 2 - 12 - 140      # centre of the plate along the tray's depth (tray frame): 280
PLATE_L = 200.0                        # along y
PLATE_Z0 = V.T_FLOOR + 10.0            # bottom of the plate, over the support it slides on
PLATE_H = 90.0
PLATE_T = 16.0
SIDE = V.TRAY_W / 2                    # the tray's outer side face: 1225
X_FACE = SIDE - 6.0                    # the mated faces meet here, 6 mm inside it: 1219
STROKE = 60.0                          # the dock pulls back this far: its pins' tips (32 mm) 22 mm clear of the tray
DOCK_HX0 = X_FACE + STROKE + PLATE_T + 3.0     # the dock housing's inner face, behind the head pulled back: 1298
PIN_DY = 86.0                          # guide pins either side of the plate's centre
INSERT_DY = (-60.0, -36.0, -12.0, 12.0, 36.0, 60.0)
ZC = PLATE_Z0 + PLATE_H / 2
RISER = {"x": 1335.0, "dy": -175.0}    # a service riser per column in the right-hand side cavity, ahead of the docks


def _shape(s):
    if isinstance(s, cq.Workplane):
        vals = s.vals()
        return vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals)
    return s


def _xc(d, x0, x1, y, z):
    """Cylinder along x from x0 to x1."""
    lo, hi = min(x0, x1), max(x0, x1)
    return cq.Workplane("YZ").circle(d / 2).extrude(hi - lo).translate((lo, y, z))


def plate_parts() -> dict:
    """The tray's half, in the tray's frame: {name: (shape, material)}."""
    p = {}
    x0 = X_FACE - PLATE_T
    y0, y1 = PLATE_Y - PLATE_L / 2, PLATE_Y + PLATE_L / 2
    plate = box(x0, y0, PLATE_Z0, X_FACE, y1, PLATE_Z0 + PLATE_H)
    for s in (-1, 1):                                      # the guide pins' conical bushings
        plate = plate.cut(_xc(14, X_FACE - 30, X_FACE + 1, PLATE_Y + s * PIN_DY, ZC))
    p["service plate"] = (plate, "svc_plate")
    # the bracket behind it, bolted to the tray floor, and the box where the tray's own lines start
    p["plate bracket"] = (box(x0 - 60, y0 + 10, V.T_FLOOR, x0, y1 - 10, PLATE_Z0 + PLATE_H + 15), "svc_housing")
    for (key, _, mat, _), dy in zip(MEDIA, INSERT_DY):
        y = PLATE_Y + dy
        if key in ("power", "data"):
            ins = box(X_FACE - 1, y - 9, ZC - 24, X_FACE + 1.5, y + 9, ZC + 24)
        else:
            ins = _xc(17, X_FACE - 1, X_FACE + 1.5, y, ZC)
        p[f"plate {key}"] = (ins, mat)
    return p


MANIFOLD_X = 520.0          # tray frame: the end of the tray's lines, a manifold block left of the UPS on the back rim


def line_paths() -> dict:
    """{medium: [(x, y, z)]} of the tray's lines, tray frame: up out of the plate's top edge, over its bracket, then
    mains into the UPS's back (the UPS feeds the tray's power strip) and the rest back to the rim and along it, over
    the power strip, to a manifold block left of the UPS."""
    out = {}
    ux = UPS_AT[0] + UPS["d"] / 2                       # the UPS's back, facing the plate: x = 1060
    xs = X_FACE - 8.0                                   # inside the plate, at its top edge
    j = 0
    for i, ((key, _, _, _), dy) in enumerate(zip(MEDIA, INSERT_DY)):
        y = PLATE_Y + dy
        zt = PLATE_Z0 + PLATE_H + 30.0 + 6.0 * i        # over the bracket, one layer each
        if key == "power":
            out[key] = [(xs, y, PLATE_Z0 + PLATE_H - 4), (xs, y, zt), (ux + 40, y, zt), (ux + 40, UPS_AT[1], zt),
                        (ux + 1, UPS_AT[1], zt)]
            continue
        yr = V.TRAY_D / 2 - 18.0 - 6.5 * j              # along the back rim, over the power strip
        zr = 58.0 + 6.5 * j
        out[key] = [(xs, y, PLATE_Z0 + PLATE_H - 4), (xs, y, zt), (ux + 60 - 8 * j, y, zt), (ux + 60 - 8 * j, yr, zt),
                    (ux + 60 - 8 * j, yr, zr), (MANIFOLD_X + 40, yr, zr)]
        j += 1
    return out


def tray_lines(live_mat=True) -> dict:
    """The tray's lines (line_paths) and the manifold they end at (tray frame); coloured when live."""
    p = {}
    for (key, _, mat, _) in MEDIA:
        p[f"line {key}"] = (hose(line_paths()[key], 7.0), mat if live_mat else "svc_plate")
    yr0 = V.TRAY_D / 2 - 18.0 - 6.5 * 4 - 6
    p["manifold"] = (box(MANIFOLD_X - 30, yr0, 40.0, MANIFOLD_X + 40, V.TRAY_D / 2 - 12, 100.0), "svc_alu")
    return p


def dock_paths() -> dict:
    """{medium: [(x, y, z)]} of the dock's side, slot frame: from the service riser along the hose, through its valve
    (or the mains contactor, or the Ethernet link), down into the housing and across to its insert in the head."""
    out = {}
    y0 = PLATE_Y - PLATE_L / 2
    ry = PLATE_Y + RISER["dy"]
    zr = PLATE_Z0 + PLATE_H + 25 + 30
    for i, ((key, _, _, _), dy) in enumerate(zip(MEDIA, INSERT_DY)):
        x = DOCK_HX0 + 14 + i * 13
        out[key] = [(x, ry, zr), (x, y0 + 30, zr), (x, y0 + 30, PLATE_Z0 + PLATE_H + 25),
                    (X_FACE + PLATE_T + 6, PLATE_Y + dy, ZC), (X_FACE + 2, PLATE_Y + dy, ZC)]
    return out


VALVE_Y = PLATE_Y - PLATE_L / 2 - 20.0      # slot frame: where each hose's valve sits on its run to the riser
SWITCH_C = {True: (0.15, 0.78, 0.30), False: (0.88, 0.16, 0.12)}      # open / closed


def switch_parts() -> dict:
    """The dock's switching, slot frame: a solenoid valve with a vent on each of the air, N2 and two water hoses, a
    contactor on the mains and a link light on the Ethernet. {name: (shape, material)}; the indicator on each is
    switch_lights()."""
    p = {}
    zr = PLATE_Z0 + PLATE_H + 25 + 30
    for i, (key, _, mat, _) in enumerate(MEDIA):
        x = DOCK_HX0 + 14 + i * 13
        if key in ("air", "n2", "cws", "cwr"):
            body = box(x - 5.5, VALVE_Y - 12, zr - 8, x + 5.5, VALVE_Y + 12, zr + 8)
            sol = cyl(9.0, 14.0, x=x, y=VALVE_Y, z=zr + 8)
            vent = cq.Workplane("XZ").circle(2.5).extrude(-8).translate((x, VALVE_Y + 12, zr - 3))
            p[f"valve {key}"] = (body.union(vent), "svc_steel")
            p[f"solenoid {key}"] = (sol, "svc_print")
        else:
            p[f"{'contactor' if key == 'power' else 'link'} {key}"] = (
                box(x - 5.5, VALVE_Y - 14, zr - 9, x + 5.5, VALVE_Y + 14, zr + 20), "svc_print")
    return p


def switch_light_mesh(key: str):
    """The indicator disc on top of a medium's valve, contactor or link (slot frame), a PolyData."""
    import pyvista as pv
    i = [m[0] for m in MEDIA].index(key)
    zr = PLATE_Z0 + PLATE_H + 25 + 30
    return pv.Cylinder(center=(DOCK_HX0 + 14 + i * 13, VALVE_Y, zr + 23.5), direction=(0, 0, 1), radius=4.6,
                       height=3.0).triangulate()


def dock_parts(head=True) -> dict:
    """The slot's half, in the slot's frame (the frame of a tray standing in the slot): {name: (shape, material)}.
    head=True gives the moving head (it slides +x by STROKE to let go), False the fixed housing and its hoses."""
    p = {}
    y0, y1 = PLATE_Y - PLATE_L / 2, PLATE_Y + PLATE_L / 2
    if head:
        hp = box(X_FACE, y0, PLATE_Z0, X_FACE + PLATE_T, y1, PLATE_Z0 + PLATE_H)
        p["dock head"] = (hp, "svc_plate")
        pins = None
        for s in (-1, 1):
            pin = _xc(12, X_FACE - 24, X_FACE, PLATE_Y + s * PIN_DY, ZC)
            tip = cq.Workplane("YZ").circle(6).workplane(offset=-8).circle(2.5).loft().translate(
                (X_FACE - 24, PLATE_Y + s * PIN_DY, ZC))
            pin = pin.union(tip)
            pins = pin if pins is None else pins.union(pin)
        p["guide pins"] = (pins, "svc_steel")
        for (key, _, mat, _), dy in zip(MEDIA, INSERT_DY):
            y = PLATE_Y + dy
            if key in ("power", "data"):
                ins = box(X_FACE + 0.5, y - 9, ZC - 24, X_FACE + 3, y + 9, ZC + 24)
            else:
                ins = _xc(17, X_FACE + 0.5, X_FACE + 3, y, ZC)
            p[f"dock {key}"] = (ins, mat)
        # the rod of the actuator, through the side wall's window
        p["dock rod"] = (box(X_FACE + PLATE_T, PLATE_Y - 14, ZC - 14, 1300, PLATE_Y + 14, ZC + 14), "svc_steel")
        return p
    hx0, hx1 = DOCK_HX0, 1372.0
    p["dock housing"] = (box(hx0, y0 + 20, PLATE_Z0 - 15, hx1, y1 - 20, PLATE_Z0 + PLATE_H + 25), "svc_housing")
    # its hoses: six lines from the housing's front into the column's riser
    ry = PLATE_Y + RISER["dy"]
    for i, (key, _, mat, _) in enumerate(MEDIA):
        x = hx0 + 14 + i * 13
        z = PLATE_Z0 + PLATE_H + 25 + 30
        vert = cq.Workplane("XY").circle(4).extrude(30).translate((x, y0 + 30, PLATE_Z0 + PLATE_H + 25))
        run = cq.Workplane("XZ").circle(4).extrude(y0 + 30 - ry).translate((x, y0 + 30, z))
        p[f"hose {key}"] = (vert.union(run), mat)
    return p


def riser_parts(z0=180.0, z1=3800.0) -> dict:
    """A vertical service duct in the right-hand side cavity of a column, in the column's frame (y = column centre)."""
    x, y = RISER["x"], PLATE_Y + RISER["dy"]
    duct = box(x - 30, y - 40, z0, x + 30, y + 40, z1)
    return {"service riser": (duct, "svc_housing")}


# ===================================================================================================== camera unit
# The stream camera as it is built, after review on PR #318 ("more realistic by using actual Pi 5, camera, etc. See
# robot-arms for some nice models ... able to be adjusted in terms of angle and height"):
# * the boards, the HQ Camera's housing and the 16 mm lens are robot-arms' models, from Raspberry Pi's drawings
#   (robot-arms PR #10, branch claude/issue-239-20260926-2347, piper-camera-mount/cad/piper_mount.py:
#   make_pi5_local, make_hq_camera_local, make_cm_camera_local, and lenses.py's "16mm" lens);
# * the mount is ours, after robot-arms PR #40's printed 2020 fixtures (branch claude/issue-24-20261021-2053,
#   docs/issue-24/camera-fixtures): a printed foot with a socket for the post, blocks on M5 drop-in T-nuts in the
#   post's slot, a camera case and a Pi 5 plate on standoffs.
# Three adjustments, each a joint: a block that slides up the post's T-slot (height), a yoke that turns on an M6 bolt
# through the block's arm (pan), and the head turning between the yoke's arms on two thumb knobs (tilt).
#
# Frames. Head: the tilt axis is x through the origin, the cameras look along -y, z up. Yoke: the pan axis is z
# through the origin, z = 0 the top of the arm. Rig: the post's axis is z through the origin, z = 0 the middle of the
# sliding block, and the post's front face (the one the block is on) faces -y.
HQ_BOARD, HQ_PITCH, HQ_PCB_T = 38.0, 30.0, 1.4      # HQ Camera, Raspberry Pi drawing (robot-arms piper_mount.Params)
HQ_CS_SEAT, HQ_RING_D, HQ_HOUSING_D = 14.43, 36.0, 34.8     # PCB front face to the CS seat; back-focus ring; housing
HQ_HOUSING_FRONT = 10.35
LENS_16 = dict(od=39.0, length=50.0, thread=4.0, glass_d=30.0, mass_g=133.7, fov=(22.2, 16.7),
               # (s0, s1, diameter) forward of the CS seat: the 5 mm C-CS adapter, the aperture ring, the focus ring,
               # the front (robot-arms lenses.py, "16mm"; Raspberry Pi's 16 mm telephoto, C mount, O39 x 50 mm)
               profile=((0.0, 5.0, 31.0), (5.0, 16.0, 36.0), (16.0, 36.0, 38.0), (36.0, 51.0, 39.0)),
               screws=((10.5, 200.0), (26.0, 160.0)), screw_tip_r=24.0)    # (s, angle round the axis) thumbscrews
CM3 = dict(w=25.0, h=23.862, lens_from_top=14.4, pcb_t=1.12, lens_h=8.3, housing=10.8, housing_d=4.07, lens_d=6.95)
PI5 = dict(w=85.0, h=56.0, t=1.6, holes=((3.5, 3.5), (3.5, 52.5), (61.5, 3.5), (61.5, 52.5)))
HEAD = dict(plate=(-48.0, 48.0, -26.0, 26.0), plate_t=5.0, hq_x=-15.0, hq_standoff=4.0, wide_x=24.0, wide_z=2.0,
            nose_y=-56.0, pi_carrier_y=24.0, pi_standoff=5.0, tilt_y=10.0)     # build frame: plate front at y = 0
YOKE = dict(half=56.0, arm_t=6.0, base_z=(6.0, 12.0), tilt=(-13.0, 68.0), base_y=(-13.0, 17.0))   # tilt axis (y, z)
RIG = dict(post=20.0, block=(-20.0, 20.0, -35.0, 25.0), block_t=14.0, arm_y=(-82.0, -24.0), arm_w=28.0,
           arm_z=(13.0, 25.0), pan_y=-67.0, knuckle_t=4.0)
PAN_AXIS = (0.0, RIG["pan_y"], RIG["arm_z"][1] + RIG["knuckle_t"])          # rig frame: the yoke frame's origin
TILT_AXIS = (0.0, PAN_AXIS[1] + YOKE["tilt"][0], PAN_AXIS[2] + YOKE["tilt"][1])  # rig frame, pan 0: (0, -80, 97)
TILT_MAX = 65.0      # tilt down at which the 16 mm lens's front reaches the yoke's base (head_reach() checks it)


def _rot(shape, steps):
    """cq shape rotated by [(axis, deg)] in turn about the origin."""
    for axis, deg in steps:
        shape = shape.rotate((0, 0, 0), axis, deg)
    return shape


def _to_head(shape, at):
    """A board-frame part (board in the x-y plane, its parts on +z, optical axis -z) into the head's build frame:
    local x -> -x, y -> z, z -> y (a turn of -90 about x, then 180 about y), then moved to `at`."""
    return _rot(shape, [((1, 0, 0), -90), ((0, 1, 0), 180)]).translate(at)


def _poly_z(pts, z0, z1) -> cq.Workplane:
    return cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)


def _hq_tripod_outline():
    """The HQ Camera's tripod mount seen from the front (robot-arms piper_mount.hq_tripod_outline, off Raspberry Pi's
    drawing RP-008200-DS-1): out from the focus ring, the shoulders, then the 13.97 mm foot to 30.35 mm below the
    axis. Bezier corners as straight runs."""
    half = [(9.91, -13.56), (12.07, -16.65), (11.467, -19.975), (8.88, -21.22), (6.985, -24.136), (6.985, -30.35)]
    return half + [(-x, y) for x, y in reversed(half)]


def hq_camera_parts() -> dict:
    """The HQ Camera with its 16 mm C-mount lens, camera frame (robot-arms make_hq_camera_local): optical axis -z,
    the PCB's front face at z = 0, the ribbon connector and the tripod foot toward -y."""
    b, t = HQ_BOARD, HQ_PCB_T
    pcb = cq.Workplane("XY").box(b, b, t, centered=(True, True, False)).edges("|Z").fillet(1.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            pcb = pcb.cut(cyl(2.5, t + 2, x=sx * HQ_PITCH / 2, y=sy * HQ_PITCH / 2, z=-1))
    seat = -HQ_CS_SEAT
    mount = cyl(HQ_RING_D, 5.8, z=seat).union(cyl(HQ_HOUSING_D, -seat - 5.8, z=seat + 5.8))
    mount = mount.union(_poly_z(_hq_tripod_outline(), -HQ_HOUSING_FRONT, 0.0))
    mount = mount.union(box(-5.08, 16.0, -HQ_HOUSING_FRONT, 5.08, 21.55, 0.0))        # focus-lock block
    lens = cyl(25.4, LENS_16["thread"], z=seat)
    for s0, s1, d in LENS_16["profile"]:
        lens = lens.union(cyl(d, s1 - s0, z=seat - s1))
    front = seat - LENS_16["profile"][-1][1]
    lens = lens.cut(cyl(LENS_16["glass_d"], 3.5, z=front - 1.0))
    screws = None
    for s, a in LENS_16["screws"]:
        r0 = next(d for s0, s1, d in LENS_16["profile"] if s0 <= s <= s1) / 2 - 0.5
        sc = cq.Workplane("YZ").circle(1.5).extrude(LENS_16["screw_tip_r"] - r0).translate((r0, 0, seat - s))
        sc = sc.rotate((0, 0, 0), (0, 0, 1), a)
        screws = sc if screws is None else screws.union(sc)
    glass = cyl(LENS_16["glass_d"] - 2, 0.6, z=front + 1.6)
    conn = box(-10, -b / 2 + 0.55, t, 10, -b / 2 + 6.25, t + 2.75)
    return {"HQ board": (pcb, "svc_pcb"), "HQ connector": (conn, "svc_print"), "HQ mount": (mount, "svc_lens"),
            "16 mm lens": (lens, "svc_lens"), "lens screws": (screws, "svc_steel"), "lens glass": (glass, "svc_glass")}


def cm3_parts() -> dict:
    """Camera Module 3 Wide, camera frame (robot-arms make_cm_camera_local): lens at the origin, optical axis -z, the
    PCB's front face at z = 0, its connector edge toward -y."""
    c = CM3
    top, bot = c["lens_from_top"], -(c["h"] - c["lens_from_top"])
    pcb = box(-c["w"] / 2, bot, 0, c["w"] / 2, top, c["pcb_t"])
    for sx in (-1, 1):
        for y in (top - 2.0, top - 14.5):
            pcb = pcb.cut(cyl(2.2, 4, x=sx * 10.5, y=y, z=-1))
    h = c["housing"] / 2
    module = box(-h, -h, -c["housing_d"], h, h, 0).union(cyl(c["lens_d"], c["lens_h"] - c["housing_d"],
                                                                 z=-c["lens_h"]))
    conn = box(-10, bot, c["pcb_t"], 10, bot + 5.71, c["pcb_t"] + 2.75)
    glass = cyl(c["lens_d"] - 2.0, 0.4, z=-c["lens_h"] - 0.2)
    return {"Wide board": (pcb, "svc_pcb"), "Wide connector": (conn, "svc_print"), "Wide lens": (module, "svc_lens"),
            "Wide glass": (glass, "svc_glass")}


def pi5_parts() -> dict:
    """Raspberry Pi 5 with its Active Cooler, board frame: x along the 85 mm, y along the 56, z up from the board's
    underside, parts on +z. Board, holes and connectors are robot-arms' make_pi5_local (Raspberry Pi's drawing); the
    cooler is ours from photos, a finned heatsink and the blower in its corner over robot-arms' 52 x 38 mm box."""
    p, t = PI5, PI5["t"]
    board = cq.Workplane("XY").box(p["w"], p["h"], t, centered=False).edges("|Z").fillet(3.0)
    for u, v in p["holes"]:
        board = board.cut(cyl(2.7, t + 2, x=u, y=v, z=-1))
    ports = [box(64.0, 2.5, t, 87.0, 18.5, t + 13.5),        # Ethernet
             box(69.5, 22.5, t, 87.0, 35.5, t + 16.0),       # USB 3
             box(69.5, 40.5, t, 87.0, 53.5, t + 16.0),       # USB 2
             box(6.7, -1.0, t, 15.7, 6.5, t + 3.3),          # USB-C
             box(22.8, -1.0, t, 28.8, 6.5, t + 3.0),         # micro HDMI 0
             box(36.2, -1.0, t, 42.2, 6.5, t + 3.0)]         # micro HDMI 1
    shells = ports[0]
    for q in ports[1:]:
        shells = shells.union(q)
    header = box(7.0, 50.0, t, 58.0, 55.0, t + 8.5)           # GPIO
    fpc = box(45.5, 4.0, t, 48.5, 17.0, t + 4.0).union(box(50.5, 4.0, t, 53.5, 17.0, t + 4.0))   # CAM/DISP 0, 1
    sink = box(4.0, 12.0, t + 1.0, 56.0, 50.0, t + 3.0)
    for i in range(9):                                         # fins along x over the SoC end
        sink = sink.union(box(4.0, 12.5 + i * 2.6, t + 3.0, 34.0, 13.5 + i * 2.6, t + 10.0))
    fan = box(35.0, 12.0, t + 3.0, 56.0, 50.0, t + 10.0).cut(cyl(17.0, 8.0, x=45.5, y=31.0, z=t + 3.6))
    hub = cyl(7.0, 6.2, x=45.5, y=31.0, z=t + 3.0)
    return {"Pi board": (board, "svc_pcb"), "Pi ports": (shells, "svc_port"), "Pi header": (header, "svc_print"),
            "Pi camera connectors": (fpc, "svc_print"), "Active Cooler heatsink": (sink, "svc_cooler"),
            "Active Cooler fan": (fan.union(hub), "svc_fan")}


def _strip(pts, x, w=13.0, t=0.6):
    """A flat ribbon w wide (along x), through (y, z) waypoints, at x."""
    out = None
    for (y0, z0), (y1, z1) in zip(pts[:-1], pts[1:]):
        L = math.hypot(y1 - y0, z1 - z0)
        seg = box(-w / 2, -t / 2, 0, w / 2, t / 2, L)
        seg = seg.rotate((0, 0, 0), (1, 0, 0), -math.degrees(math.atan2(y1 - y0, z1 - z0)))
        seg = seg.translate((x, y0, z0))
        out = seg if out is None else out.union(seg)
    return out


def head_parts() -> dict:
    """The head in the head frame: a black PETG camera plate with the HQ Camera behind it and its 16 mm lens through
    it; the Camera Module 3 Wide on a nose, 56 mm forward, so that it sits level with the lens's front and the lens
    stays out of its 102-degree picture; the Pi 5 on a carrier plate behind; side cheeks with the tilt bosses; the two
    ribbons and the Ethernet lead."""
    h = HEAD
    x0, x1, z0, z1 = h["plate"]
    pt = h["plate_t"]
    p = {}
    hq_at = (h["hq_x"], pt + h["hq_standoff"], 0.0)           # the HQ board's front face, build frame
    plate = box(x0, 0, z0, x1, pt, z1).edges("|Y").fillet(4.0)
    plate = plate.cut(cq.Workplane("XZ").circle(37.0 / 2).extrude(-pt - 2).translate((h["hq_x"], -1, 0)))
    foot = _to_head(_poly_z(_hq_tripod_outline(), -HQ_HOUSING_FRONT - 1, 2.0), hq_at)
    lock = _to_head(box(-6.1, 15.0, -HQ_HOUSING_FRONT - 1, 6.1, 22.6, 2.0), hq_at)
    plate = plate.cut(foot).cut(lock)                         # the pocket round the tripod mount and lock block
    plate = plate.cut(box(h["wide_x"] - 12.0, -1, h["wide_z"] - 16.0, h["wide_x"] + 4.0, pt + 1,
                          h["wide_z"] - 13.0))                # the Wide's ribbon goes through here
    wx0, wx1 = h["wide_x"] - 14.0, h["wide_x"] + 18.0
    ny = h["nose_y"]
    nose = box(wx0, ny, h["wide_z"] - 16, wx1, ny + 5, h["wide_z"] + 16)                 # the Wide's carrier
    nose = nose.cut(box(h["wide_x"] - 5.7, ny - 1, h["wide_z"] - 5.7, h["wide_x"] + 5.7, ny + 6, h["wide_z"] + 5.7))
    nose = nose.union(box(wx0, ny, h["wide_z"] - 20, wx1, 0, h["wide_z"] - 16))          # its shelf to the plate
    nose = nose.union(box(wx1 - 4, ny + 5, h["wide_z"] - 16, wx1, 0, h["wide_z"] + 8))   # and a side web
    carrier = box(x0, h["pi_carrier_y"], z0 - 4, x1, h["pi_carrier_y"] + 4, z1 + 4).edges("|Y").fillet(4.0)
    cheeks = box(x0, pt, z0, x0 + 4, h["pi_carrier_y"], z1).union(box(x1 - 4, pt, z0, x1, h["pi_carrier_y"], z1))
    for sx in (-1, 1):
        cheeks = cheeks.union(cq.Workplane("YZ").circle(9.0).extrude(2.0).translate(
            ((x1 if sx > 0 else x0 - 2.0), h["tilt_y"], 0.0)))
    p["camera plate"] = (plate, "svc_petg")
    p["Wide nose"] = (nose, "svc_petg")
    p["Pi carrier"] = (carrier, "svc_petg")
    p["cheeks"] = (cheeks, "svc_petg")
    for name, (s, m) in hq_camera_parts().items():
        p[name] = (_to_head(s, hq_at), m)
    wide_at = (h["wide_x"], ny + 5 + 2.5, h["wide_z"])       # the Wide's PCB front face, 2.5 mm behind its carrier
    for name, (s, m) in cm3_parts().items():
        p[name] = (_to_head(s, wide_at), m)
    pi_y = h["pi_carrier_y"] + 4 + h["pi_standoff"]          # the Pi board's underside
    pi_at = (PI5["w"] / 2, pi_y, -PI5["h"] / 2)
    for name, (s, m) in pi5_parts().items():
        p[name] = (_rot(s, [((1, 0, 0), -90), ((0, 1, 0), 180)]).translate(pi_at), m)
    stand = None
    for u, v in PI5["holes"]:
        x, z = PI5["w"] / 2 - u, v - PI5["h"] / 2
        s = cq.Workplane("XZ").circle(3.0).extrude(-h["pi_standoff"]).translate((x, h["pi_carrier_y"] + 4, z))
        stand = s if stand is None else stand.union(s)
    for sx in (-1, 1):
        for sz in (-1, 1):
            s = cq.Workplane("XZ").circle(2.6).extrude(-h["hq_standoff"]).translate(
                (h["hq_x"] + sx * HQ_PITCH / 2, pt, sz * HQ_PITCH / 2))
            stand = stand.union(s)
    p["standoffs"] = (stand, "svc_steel")
    # ribbons: from each camera's connector edge, down under the plates, round the Pi's lower edge to its CAM/DISP
    # connectors (x = -4.5 and -9.5 once the Pi is turned into the head)
    zr = z0 - 6.0
    yb = pi_y + PI5["t"] + 4.5
    p["HQ ribbon"] = (_strip([(hq_at[1] + 2.0, -HQ_BOARD / 2 + 3.0), (hq_at[1] + 2.0, zr), (yb, zr),
                              (yb, -PI5["h"] / 2 + 12.0)], x=-10.0), "svc_ribbon")
    zs = h["wide_z"] - 14.5                                   # along the top of the nose's shelf, through the plate
    p["Wide ribbon"] = (_strip([(wide_at[1] + 2.0, h["wide_z"] - 9.0), (wide_at[1] + 2.0, zs), (pt + 3.0, zs),
                                (pt + 3.0, zr - 1.2), (yb + 1.2, zr - 1.2), (yb + 1.2, -PI5["h"] / 2 + 12.0)],
                               x=h["wide_x"] - 4.0), "svc_ribbon")
    ex = -PI5["w"] / 2 - 2.0                                  # the Ethernet jack's face, once turned
    ej = (pi_y + 9.0, -PI5["h"] / 2 + 10.5)
    p["Ethernet lead"] = (hose([(ex, *ej), (-47.0, *ej), (-47.0, ej[0] + 22.0, ej[1]), (-47.0, ej[0] + 22.0, z0 - 14.0)],
                               6.0), "svc_print")         # out behind the yoke's arm, clear of it at any tilt
    ty = h["tilt_y"]
    return {n: (s.translate((0, -ty, 0)), m) for n, (s, m) in p.items() if s is not None}


def yoke_parts() -> dict:
    """The yoke in the yoke frame: the pan disc on the arm's M6 bolt, the base under the head and the two arms up to
    the tilt axis, with its thumb knobs; black PETG, the knobs and bolt heads steel."""
    y = YOKE
    a, t = y["half"], y["arm_t"]
    ty, tz = y["tilt"]
    b0, b1 = y["base_z"]
    base = box(-a, y["base_y"][0], b0, a, y["base_y"][1], b1).edges("|Z").fillet(3.0)
    disc = cyl(40.0, b0, z=0.0)
    arms = None
    for sx in (-1, 1):
        x0 = a - t if sx > 0 else -a
        prof = [(y["base_y"][0], b1), (y["base_y"][1], b1), (ty + 9.0, tz), (ty - 9.0, tz)]
        arm = cq.Workplane("YZ").polyline(prof).close().extrude(t).translate((x0, 0, 0))
        arm = arm.union(cq.Workplane("YZ").circle(9.0).extrude(t).translate((x0, ty, tz)))
        arms = arm if arms is None else arms.union(arm)
    knobs = None
    for sx in (-1, 1):
        k = cq.Workplane("YZ").circle(11.0).extrude(8.0).edges().fillet(1.5)
        k = k.translate((a if sx > 0 else -a - 8.0, ty, tz))
        knobs = k if knobs is None else knobs.union(k)
    return {"yoke": (base.union(disc).union(arms), "svc_petg"), "tilt knobs": (knobs, "svc_steel"),
            "pan bolt": (cyl(10.0, 3.0, z=b1), "svc_steel")}


def slider_parts() -> dict:
    """The block on the post's front face and its arm, rig frame: two M5 screws into drop-in T-nuts in the slot (as
    robot-arms PR #40's wedges and Pi plates), the arm out 58 mm to the pan bolt, its knuckle disc on top."""
    r = RIG
    e = r["post"] / 2
    bx0, bx1, bz0, bz1 = r["block"]
    blk = box(bx0, -e - r["block_t"], bz0, bx1, -e, bz1).edges("|Y").fillet(3.0)
    key = box(-2.8, -e, bz0 + 5, 2.8, -e + 1.6, bz1 - 5)                           # a key in the post's T-slot
    arm = box(-r["arm_w"] / 2, r["arm_y"][0], r["arm_z"][0], r["arm_w"] / 2, r["arm_y"][1], r["arm_z"][1])
    arm = arm.edges("|Z").fillet(4.0)
    knuckle = cyl(40.0, r["knuckle_t"], x=0, y=r["pan_y"], z=r["arm_z"][1])
    heads = None
    for z in (bz0 + 9.0, 1.0):                                                       # under the arm
        hd = cq.Workplane("XZ").circle(4.75).extrude(2.8).translate((0, -e - r["block_t"], z))
        heads = hd if heads is None else heads.union(hd)
    return {"slide block": (blk.union(key).union(arm).union(knuckle), "svc_petg"), "M5 screws": (heads, "svc_steel")}


def mast_parts(post_h: float, foot=True) -> dict:
    """The 2020 post, standing in a printed foot (robot-arms PR #40's foot: a 90 x 90 x 6 plate, a 50 mm socket and
    four gussets), with its PoE lead clipped down the back slot. Rig frame, z = 0 the surface it stands on."""
    e = RIG["post"] / 2
    p = {}
    z_post0 = 6.0 if foot else 0.0
    post = box(-e, -e, z_post0, e, e, post_h)
    for ang in (0, 90, 180, 270):                      # the four T-slots
        slot = box(-3.0, e - 1.8, z_post0 - 1, 3.0, e + 1, post_h + 1).rotate((0, 0, 0), (0, 0, 1), ang)
        post = post.cut(slot)
    p["2020 post"] = (post, "svc_alu")
    if foot:
        ow = 20.5 + 9.0
        sock = box(-ow / 2, -ow / 2, 0, ow / 2, ow / 2, 56.0).cut(box(-10.25, -10.25, 6.0, 10.25, 10.25, 57.0))
        plate = box(-45, -45, 0, 45, 45, 6.0).edges("|Z").fillet(6.0)
        for ang in (0, 90, 180, 270):
            g = cq.Workplane("XZ").polyline([(ow / 2 - 0.5, 6.0), (41.0, 6.0), (ow / 2 - 0.5, 41.0)]).close() \
                .extrude(2.5, both=True).rotate((0, 0, 0), (0, 0, 1), ang)
            sock = sock.union(g)
        p["foot"] = (plate.union(sock), "svc_petg")
        p["PoE lead"] = (hose([(0, e + 3.0, post_h - 40.0), (0, e + 3.0, 66.0), (0, 40.0, 8.0)], 6.0), "svc_print")
    return p


def _rig_matrix(h: float, pan: float, tilt: float, h0: float = 0.0) -> dict:
    """{piece: 4x4} for the slider raised by h (rig frame), the yoke turned `pan` degrees (left, seen from above, is
    positive) and the head tilted `tilt` degrees down; pieces modelled with the block at h0, pan = tilt = 0."""
    ms = I._T((0, 0, h))
    mp = ms @ I._R((0, 0, 1), pan, (PAN_AXIS[0], PAN_AXIS[1], PAN_AXIS[2] + h0))
    mh = mp @ I._R((1, 0, 0), tilt, (TILT_AXIS[0], TILT_AXIS[1], TILT_AXIS[2] + h0))
    return {"slider": ms, "pan": mp, "head": mh}


_RIG: dict = {}


def rig_pieces() -> dict:
    """{piece: {name: (shape, material)}} for the moving pieces in the rig frame at h = 0, pan = tilt = 0."""
    if _RIG:
        return _RIG
    yoke_at = cq.Location(cq.Vector(*PAN_AXIS))
    head_at = cq.Location(cq.Vector(*TILT_AXIS))
    _RIG.update({"slider": slider_parts(),
                 "pan": {n: (_shape(s).moved(yoke_at), m) for n, (s, m) in yoke_parts().items()},
                 "head": {n: (_shape(s).moved(head_at), m) for n, (s, m) in head_parts().items()}})
    return _RIG


def head_reach(tilt_max=TILT_MAX) -> dict:
    """How high the head rises over its tilt axis and how low it reaches, over 0 to tilt_max degrees down, and the
    smallest gap between the head and the yoke's base: from the meshes."""
    import lab
    from scene import R
    hp = np.vstack([lab.to_mesh(_shape(s), 0.6).points for s, _ in head_parts().values()])
    h = np.c_[hp, np.ones(len(hp))]
    yb = YOKE["base_y"]
    out = dict(up=0.0, down=0.0, gap_to_base=1e9)
    for tilt in np.linspace(-15.0, tilt_max, 33):
        q = (h @ R((1, 0, 0), float(tilt)).T)[:, :3]
        out["up"] = max(out["up"], float(q[:, 2].max()))
        out["down"] = min(out["down"], float(q[:, 2].min()))
        over = (q[:, 0] > -YOKE["half"]) & (q[:, 0] < YOKE["half"]) & (q[:, 1] > yb[0] - YOKE["tilt"][0]) & \
               (q[:, 1] < yb[1] - YOKE["tilt"][0])
        if over.any():
            out["gap_to_base"] = min(out["gap_to_base"], float(q[over, 2].min() - (YOKE["base_z"][1] - YOKE["tilt"][1])))
    return {k: round(v, 1) for k, v in out.items()}


def stream_cam(post_h: float = 600.0, h0: float = 360.0) -> Instrument:
    """The unit on its own for the tour: the post in its foot, the block at h0 on it, then each adjustment in turn."""
    inst = Instrument("stream_cam", "Stream camera unit for a tray", "Raspberry Pi 5, HQ Camera (16 mm) + Camera Module 3 "
                      "Wide", (140.0, 210.0, post_h + 20.0),
                      "robot-arms' Pi 5, HQ Camera, 16 mm lens and Camera Module 3 models (PR #10, from Raspberry Pi's "
                      "drawings) on a printed pan-tilt head and sliding block on a 2020 post, after robot-arms PR #40's "
                      "fixtures; the mount's layout is ours")
    body = _piece(inst, "body")
    for n, (s, m) in mast_parts(post_h).items():
        body.add(n, s, m)
    up = cq.Location(cq.Vector(0, 0, h0))
    for piece, parts in rig_pieces().items():
        pc = _piece(inst, piece)
        for n, (s, m) in parts.items():
            pc.add(n, _shape(s).moved(up), m)
    pan_pivot = (PAN_AXIS[0], PAN_AXIS[1], PAN_AXIS[2] + h0)
    tilt_pivot = (TILT_AXIS[0], TILT_AXIS[1], TILT_AXIS[2] + h0)
    inst.joints = {"slider": Joint("slide", vec=(0, 0, 100.0)),
                   "pan": Joint("spin", axis=(0, 0, 1), pivot=pan_pivot, deg=40.0, parent="slider"),
                   "head": Joint("hinge", axis=(1, 0, 0), pivot=tilt_pivot, deg=30.0, parent="pan")}

    def at(piece, xyz, vs=0.0, vp=0.0, vt=0.0):
        m = _rig_matrix(100.0 * vs, 40.0 * vp, 30.0 * vt, h0)[piece]
        return tuple(float(c) for c in (m @ np.array([xyz[0], xyz[1], xyz[2] + h0, 1.0]))[:3])

    hx, hy, hz = TILT_AXIS
    lens_tip = (HEAD["hq_x"], hy - HEAD["tilt_y"] - HQ_CS_SEAT + HEAD["plate_t"] + HEAD["hq_standoff"] - 51.0, hz)
    wide = (HEAD["wide_x"], hy - HEAD["tilt_y"] + HEAD["nose_y"], hz + HEAD["wide_z"])
    pi = (-20.0, hy - HEAD["tilt_y"] + 40.0, hz + 18.0)
    intro = [("HQ Camera, 16 mm C-mount lens", at("head", lens_tip), (0.14, 0.20)),
             ("Camera Module 3 Wide, on a nose", at("head", wide), (0.86, 0.20)),
             ("Pi 5 + Active Cooler", at("head", pi), (0.86, 0.36)),
             ("ribbons to the Pi's camera ports", at("head", (-7.0, hy - HEAD["tilt_y"] + 30.0, hz - 32.0)),
              (0.14, 0.42)),
             ("2020 post in a printed foot", (0.0, 0.0, 120.0), (0.14, 0.72))]
    slide = [("block on two M5 T-nuts: height", at("slider", (20.0, -30.0, 0.0), vs=1.0), (0.14, 0.50))]
    pan = [("pan: the yoke on an M6 bolt", at("pan", (0.0, PAN_AXIS[1], PAN_AXIS[2]), vs=1.0, vp=-1.0),
            (0.14, 0.50))]
    tilt = [("tilt: two thumb knobs", at("head", (YOKE["half"] + 4.0, hy, hz), vs=1.0, vt=2.0), (0.86, 0.36))]
    r = head_reach()
    acts = [
        ("The stream camera as built: a Raspberry Pi 5 with its Active Cooler, a Raspberry Pi HQ Camera with the 16 mm "
         "C-mount lens, and a Camera Module 3 Wide, on a printed head. The Wide sits on a nose level with the lens's "
         "front, so the 39 mm lens stays out of its 102-degree picture.", 3.4, {"slider": (0.0, 0.0)}, intro),
        ("Height: the block slides up the post's T-slot and locks on two M5 drop-in T-nuts, as robot-arms' camera "
         "fixtures do.", 2.6, {"slider": (0.0, 1.0)}, slide),
        ("Pan: the yoke turns on an M6 bolt through the block's arm, 40 degrees each way.", 2.6,
         {"pan": (0.0, -1.0)}, pan),
        ("", 1.8, {"pan": (-1.0, 1.0)}, pan),
        (f"Tilt: the head turns between the yoke's arms on two thumb knobs, from level to {TILT_MAX:.0f} degrees down, "
         f"where the lens's front reaches the yoke. Tilted down, the head stands {r['up']:.0f} mm at most over its "
         "axis.", 2.8, {"pan": (1.0, 0.0), "head": (0.0, 2.0)}, tilt),
        ("Aimed: down and to one side at an instrument's working face. The Wide sees 102 x 67 degrees, the HQ with the "
         "16 mm lens 22 x 17: the detail. One PoE lead carries power and the stream.", 3.0,
         {"slider": (1.0, 0.4), "pan": (0.0, 0.5), "head": (2.0, 1.2)}, intro[4:]),
    ]
    inst.actions = [a[:3] for a in acts]
    inst.step_labels = {i: a[3] for i, a in enumerate(acts)}
    inst.labels = []
    inst.cam = (1.0, -1.25, 0.55)
    inst.framing = (0.80, 0.55)
    inst.zoom = {0: ((0.0, hy - 10.0, hz + h0 - 10.0), 600.0), 1: ((0.0, hy + 20.0, hz + h0 + 10.0), 1050.0),
                 5: ((0.0, hy + 20.0, hz + h0 + 30.0), 900.0)}
    inst.notes = [f"Per-tray cameras: the head's top stays under Kardex's 727.5 mm product height; tilted down it "
                  f"rises at most {r['up']:.0f} mm over its tilt axis."]
    return inst


# ===================================================================================================== dock model
def tray_dock() -> Instrument:
    """The coupling on its own, round the plate: the corner of a tray, the slot's side wall and the dock."""
    off = cq.Location(cq.Vector(-X_FACE, -PLATE_Y, 0))
    inst = Instrument("tray_dock", "Tray service dock", "Staubli CombiTac-style docking plate, actuated",
                      (STROKE + 180.0, PLATE_L + 40, PLATE_H + 60),
                      "CombiTac uniq catalogue (inserts, align 4 docking), Kardex #53 (power in a slot and at the "
                      "opening); the layout, plate and stroke are ours")
    body = _piece(inst, "body")
    # the side wall of the slot with a window for the dock, the support the tray rides on, the housing and hoses
    wx = V.TRAY_W / 2 + 45
    y0, y1 = -190.0, 150.0
    wall = box(wx - X_FACE, y0, -30, wx + 12 - X_FACE, y1, 200)
    wall = wall.cut(box(wx - X_FACE - 1, -PLATE_L / 2 - 12, PLATE_Z0 - 12, wx + 13 - X_FACE, PLATE_L / 2 + 12,
                        PLATE_Z0 + PLATE_H + 12))
    body.add("slot side wall", wall, "svc_wall")
    body.add("tray support", box(-20, y0, -6, wx - X_FACE, y1, 0), "svc_rib")
    for n, (s, m) in dock_parts(head=False).items():
        body.add(n, _shape(s).moved(off), m)
    tray = _piece(inst, "tray")
    sx = SIDE - X_FACE                                    # the tray's side, 6 mm outside the mated faces
    pan = box(-300, -330, 0, sx, 142, V.T_FLOOR + V.T_RIM)
    pan = pan.cut(box(-301, -331, V.T_FLOOR, sx - 12, 130, V.T_FLOOR + V.T_RIM + 1))
    pan = pan.cut(box(-PLATE_T - 1, -PLATE_L / 2 - 2, PLATE_Z0 - 2, sx + 1, PLATE_L / 2 + 2, V.T_FLOOR + V.T_RIM + 1))
    tray.add("tray corner", pan, "svc_tray")
    for n, (s, m) in plate_parts().items():
        tray.add(n, _shape(s).moved(off), m)
    live = _piece(inst, "live")
    for n, (s, m) in tray_lines().items():
        live.add(n, _shape(s).moved(off), m)
    head = _piece(inst, "head")
    for n, (s, m) in dock_parts(head=True).items():
        head.add(n, _shape(s).moved(off), m)
    inst.joints = {
        "head": Joint("slide", vec=(STROKE, 0, 0)),
        "tray": Joint("slide", vec=(0, -700, 0)),
        "live": Joint("fade", parent="tray", v0=1.0),
    }
    inst.actions = [
        ("In its slot the tray's plate is held against the dock: mains, Ethernet, compressed air, N2 and chilled water "
         "are all live through one coupling.", 2.4, {"live": (1.0, 1.0)}),
        ("Before the tray moves: air, N2 and water are shut and vented (CombiTac's couplings must not part under "
         f"pressure), the tray's UPS takes the load, and the dock pulls back {STROKE:.0f} mm.", 2.6,
         {"live": (1.0, 0.0), "head": (0.0, 1.0)}),
        (f"The extractor pulls the tray out of the slot, across the dock, whose pins are now "
         f"{X_FACE - 24 + STROKE - SIDE:.0f} mm clear of the tray's side.", 2.0,
         {"tray": (0.0, 1.0)}),
        ("At the opening an identical dock waits in the bay's side wall. The tray stops against it ...", 2.0,
         {"tray": (1.0, 0.0)}),
        ("... the guide pins find the plate's bushings (4 mm of misalignment, CombiTac align), the plate is pressed "
         "home, the supplies open: back on mains.", 2.4, {"head": (1.0, 0.0), "live": (0.0, 1.0)}),
    ]
    z = ZC
    inst.labels = [("guide pin", (-24, PIN_DY, z), (0.84, 0.20)),          # on the dock's head, which stays
                   ("mains", (8, INSERT_DY[0], z + 20), (0.16, 0.18)),
                   ("Ethernet", (8, INSERT_DY[1], z + 20), (0.16, 0.28)),
                   ("air", (8, INSERT_DY[2], z), (0.16, 0.38)),
                   ("N2", (8, INSERT_DY[3], z), (0.16, 0.48)),
                   ("water in / out", (8, INSERT_DY[4], z), (0.16, 0.58)),
                   ("dock: actuator in the side wall", (110, -60, PLATE_Z0 + PLATE_H + 25), (0.84, 0.40)),
                   ("service plate on the tray", (-PLATE_T, -PLATE_L / 2, PLATE_Z0 + 5), (0.84, 0.66))]
    inst.cam = (1.0, -1.5, 1.0)
    inst.framing = (0.48, 0.45)
    inst.props = ("live",)
    return inst


# ===================================================================================================== utilities
UPS = dict(w=86.0, d=447.0, h=437.0)        # Eaton 5PX1500RTNG2 standing as a tower: 86 thick (y), 447 deep (x)
UPS_AT = (SIDE - 165 - UPS["d"] / 2, 276.0 + UPS["w"] / 2)      # tray frame: just ahead of the power strip
N2GEN = dict(w=305.0, d=406.0, h=889.0)     # Parker Balston UHPN2-1100
CHILLER = dict(w=0.0, d=0.0, h=0.0)         # ThermoFlex 900: size not found; not drawn to a size


def ups_parts() -> dict:
    """The tray's UPS, a 2U rack/tower unit standing on its side at the back right (tray frame)."""
    x, y = UPS_AT
    u = UPS
    body = box(x - u["d"] / 2, y - u["w"] / 2, V.T_FLOOR, x + u["d"] / 2, y + u["w"] / 2, V.T_FLOOR + u["h"])
    face = box(x - u["d"] / 2 - 3, y - u["w"] / 2 + 6, V.T_FLOOR + 10, x - u["d"] / 2, y + u["w"] / 2 - 6,
               V.T_FLOOR + u["h"] - 10)
    scr = box(x - u["d"] / 2 - 4, y - 18, V.T_FLOOR + u["h"] - 110, x - u["d"] / 2 - 3, y + 18, V.T_FLOOR + u["h"] - 60)
    return {"UPS": (body, "svc_ups"), "UPS face": (face, "svc_ups_face"), "UPS screen": (scr, "svc_screen")}


# ===================================================================================================== registry
REGISTRY = {"tray_dock": tray_dock, "stream_cam": stream_cam}


# ===================================================================================================== scenes
# Below here: the pieces in the VLM (docks, plates, risers, UPSs, cameras), the animations and the JSON. The scene
# modules are imported late, so tour.py can import this module for REGISTRY without loading the lab's meshes.
TRAY_CAMS = {   # per tray: (mast x, mast y, aim x, aim y, aim z, post yaw) in the tray's frame; the post's foot on the
                # floor.
    # Placed (PR #318: "positioned closer to the front or middle to avoid capturing irrelevant things outside the bay
    # (e.g., people/faces)") by a search over post positions and yaws and a few aim points on each instrument: the
    # least of the room in either camera's picture with the tray presented (unit_view), then the closest view; posts
    # 15 mm or more clear of every instrument's box, the UPS and the service plate, inside the rim, off the middle
    # half of each instrument's front (where the arm works) and, on tray B, off the front between the rack and the
    # doser's cup. Each unit stands in front of or beside its instrument and looks back or down at it. Tray B's doser
    # is at the front edge and the OT-2 has no room in front, so B0, A1 and D2 still see some of the
    # room (cameras.views in services.json).
    "A": [(-680.0, -270.0, -467.0, 6.0, 92.0, 90.0), (210.0, 275.0, 916.0, 102.0, 600.0, 90.0)],
    "B": [(685.0, -340.0, 460.0, -222.0, 339.0, 270.0)],     # one: a unit over the rack stood in the middle of the tray
    "C": [(-960.0, -340.0, -560.0, 0.0, 600.0, 90.0), (125.0, -235.0, 360.0, 0.0, 486.0, 90.0)],
    "D": [(-225.0, -305.0, -552.0, 0.0, 550.0, 270.0), (300.0, -340.0, 60.0, 0.0, 600.0, 270.0),
          (860.0, 185.0, 1066.0, -43.0, 109.0, 90.0)],
    "E": [(-470.0, -340.0, -880.0, 0.0, 420.0, 270.0), (-50.0, -340.0, -250.0, 0.0, 524.0, 180.0),
          (965.0, -375.0, 860.0, 0.0, 509.0, 180.0)],
    "F": [(-960.0, -305.0, -578.0, 0.0, 600.0, 90.0), (685.0, -235.0, 408.0, 0.0, 513.0, 270.0)],
}
TRAY_CAMS_ROUND5 = {   # where they stood before: at the back, looking forward over their instruments and out of the bay
    "A": [(-760.0, 320.0, -150.0, -150.0, 150.0), (380.0, 350.0, 760.0, -60.0, 330.0, 90.0)],
    "B": [(480.0, 320.0, 250.0, -316.0, 300.0), (-560.0, 320.0, -250.0, -372.0, 60.0)],     # doser first, as now
    "C": [(-1150.0, -330.0, -560.0, -60.0, 330.0), (380.0, 320.0, 360.0, 0.0, 200.0)],
    "D": [(-1150.0, 361.0, -760.0, -150.0, 300.0, 90.0), (-290.0, -345.0, 60.0, -230.0, 360.0, 90.0),
          (560.0, 320.0, 680.0, -150.0, 100.0)],
    "E": [(-1150.0, 361.0, -880.0, 0.0, 420.0, 90.0), (-570.0, 320.0, -250.0, 0.0, 300.0, 90.0),
          (90.0, 361.0, 590.0, 0.0, 300.0, 90.0)],
    "F": [(-1150.0, 320.0, -500.0, 0.0, 420.0), (-170.0, 350.0, 300.0, -200.0, 300.0, 90.0)],
}
CAM_PIVOT = 640.0                       # the tilt axis over the tray floor; the head's top stays under 727.5 mm
POST_H = 590.0                          # the tray posts: 22 mm over the sliding block at its CAM_PIVOT height
CAM_H = CAM_PIVOT - TILT_AXIS[2]        # the block's height on a tray post: 543 mm
# The bay unit sits on a 2020 bar across the back of the bay, 72 mm in front of the shutter's plane, over the top of
# Kardex's product envelope at the opening and under tray F1, which is stored over the opening. With the 996 mm
# opening (vlm.py) that envelope tops out at 1733.5 mm, only 166.5 mm under F1 at 1900, so the bay unit has no post or
# sliding block: its yoke is bolted straight onto a saddle clamp on the bar (bay_at). y and bar_z are the bar's centre;
# the head looks forward (-y), tilted down.
BAY_CAM = dict(y=-635.0, bar_z=V.Z_OPEN + V.T_FLOOR + V.MAX_GOODS_H + V.GOODS_CLEAR + 25.0, tilt=64.0)
BAY_CAM["pivot_z"] = BAY_CAM["bar_z"] + 14.0 + TILT_AXIS[2] - PAN_AXIS[2]     # the tilt axis, 68 mm over the clamp
BAY_CAM["pivot_y"] = BAY_CAM["y"] + TILT_AXIS[1] - PAN_AXIS[1]               # 13 mm in front of the bar
LAMP_UPS = (1.0, 0.62, 0.10)


def mats() -> dict:
    import lab
    m = dict(lab.MATS)
    m.update(I.MATERIALS)
    m.update(MATERIALS)
    return m


_MESH_CACHE: dict = {}


def meshes_of(key: str, parts_fn, tol=1.0) -> dict:
    """{material: PolyData} of a parts dict, tessellated once per key."""
    if key not in _MESH_CACHE:
        import lab
        by = {}
        for name, (s, mat) in parts_fn().items():
            by.setdefault(mat, []).append(lab.to_mesh(_shape(s), tol))
        _MESH_CACHE[key] = {mat: lab._merge(ms) for mat, ms in by.items()}
    return _MESH_CACHE[key]


def add_meshes(sc, prefix: str, by_mat: dict, group: str, **kw) -> list:
    M = mats()
    names = []
    for mat, mesh in by_mat.items():
        if not mesh.n_points:
            continue
        r, g, b, a, spec = M[mat]
        n = f"{prefix}/{mat}"
        sc.add(n, mesh, (r, g, b), group, opacity=a, specular=spec, **kw)
        names.append(n)
    return names


def rig_pose(mx, my, t, h=CAM_H, z0=V.T_FLOOR, post=None):
    """How a rig standing at (mx, my) is set to look at t (all in the tray's frame): the post's yaw (its foot goes on
    square to the tray: the nearest multiple of 90 degrees to the target's bearing, unless `post` is given, where that
    would put the head in an instrument), the pan that does the rest and the tilt down, both from where the yoke and
    the head then are. -> (post yaw, pan, tilt), degrees."""
    def yaw_tilt(px, py, pz):
        dx, dy, dz = t[0] - px, t[1] - py, t[2] - pz
        return math.degrees(math.atan2(dx, -dy)), math.degrees(math.atan2(-dz, math.hypot(dx, dy)))
    yaw0, _ = yaw_tilt(mx, my, z0 + h + TILT_AXIS[2])
    post = 90.0 * round(yaw0 / 90.0) if post is None else float(post)
    c, s = math.cos(math.radians(post)), math.sin(math.radians(post))
    px, py = mx - s * PAN_AXIS[1], my + c * PAN_AXIS[1]
    yaw1, _ = yaw_tilt(px, py, z0 + h + TILT_AXIS[2])
    pan = (yaw1 - post + 180.0) % 360.0 - 180.0
    a = math.radians(post + pan)
    tx, ty = px - math.sin(a) * YOKE["tilt"][0], py + math.cos(a) * YOKE["tilt"][0]
    _, tilt = yaw_tilt(tx, ty, z0 + h + TILT_AXIS[2])
    return post, max(-75.0, min(75.0, pan)), max(-15.0, min(TILT_MAX, tilt))


def rig_matrices(at: np.ndarray, post: float, h: float, pan: float, tilt: float) -> dict:
    """World (or parent-frame) 4x4 of each piece of a rig whose post stands at `at` (4x4), turned `post` degrees."""
    m0 = at @ I._R((0, 0, 1), post)
    out = {"mast": m0}
    out.update({k: m0 @ m for k, m in _rig_matrix(h, pan, tilt).items()})
    return out


def _add_rig(sc, prefix: str, parent: str | None, at: np.ndarray, post: float, h: float, pan: float, tilt: float,
             post_h: float = POST_H, foot=True) -> str:
    """One stream camera rig in a scene, as groups prefix (the post), prefix+'sl', +'pan', +'head'; returns the head's
    group."""
    from scene import T
    mast = meshes_of(f"mast{post_h}{foot}", lambda: mast_parts(post_h, foot), 0.5)
    pieces = {k: meshes_of(f"rig_{k}", lambda k=k: rig_pieces()[k], 0.3) for k in ("slider", "pan", "head")}
    add_meshes(sc, prefix, mast, prefix)
    names = {"slider": f"{prefix}sl", "pan": f"{prefix}pan", "head": f"{prefix}head"}
    for k, g in names.items():
        add_meshes(sc, g, pieces[k], g)
    sc.gmat[prefix] = at @ I._R((0, 0, 1), post)
    if parent:
        sc.parent[prefix] = parent
    sc.gmat[names["slider"]] = T((0, 0, h))
    sc.parent[names["slider"]] = prefix
    sc.gmat[names["pan"]] = I._R((0, 0, 1), pan, PAN_AXIS)
    sc.parent[names["pan"]] = names["slider"]
    sc.gmat[names["head"]] = I._R((1, 0, 0), tilt, TILT_AXIS)
    sc.parent[names["head"]] = names["pan"]
    return names["head"]


def add_tray_cameras(sc, tray: str, layout=None, h=CAM_H) -> list:
    """Stream camera rigs on tray `tray` (they ride with group tray_<k>). layout: [(x, y, aim_x, aim_y, aim_z)] in
    the tray's frame, default TRAY_CAMS[tray]. Returns the post groups, one per unit."""
    from scene import T
    layout = TRAY_CAMS.get(tray, []) if layout is None else layout
    groups = []
    for i, (x, y, ax, ay, az, *fixed) in enumerate(layout):
        post, pan, tilt = rig_pose(x, y, (ax, ay, az), h, post=fixed[0] if fixed else None)
        g = f"cam_{tray}{i}"
        _add_rig(sc, g, f"tray_{tray}", T((x, y, V.T_FLOOR)), post, h, pan, tilt)
        groups.append(g)
    return groups


def bay_cam_point() -> tuple:
    """The bay unit's tilt axis, world: where its labels point."""
    return (0.0, BAY_CAM["pivot_y"], BAY_CAM["pivot_z"])


def head_point(x, y, ax, ay, az, post=None, h=CAM_H, dz=0.0) -> tuple:
    """A tray rig's tilt axis (plus dz), in the tray's frame: where its labels point."""
    post, pan, _ = rig_pose(x, y, (ax, ay, az), h, post=post)
    m = rig_matrices(I._T((x, y, V.T_FLOOR)), post, h, pan, 0.0)["pan"]
    return tuple(float(c) for c in (m @ np.array([*TILT_AXIS[:2], TILT_AXIS[2] + dz, 1.0]))[:3])


def add_cameras(sc, L=None, trays="ABCDEF") -> list:
    """setup_lab's CAMERA_HOOK: every tray's stream cameras (TRAY_CAMS) and the bay camera. [(label, xyz)] for captions."""
    labels = []
    for k in trays:
        if f"tray_{k}" in sc.gmat and TRAY_CAMS.get(k):
            groups = add_tray_cameras(sc, k)
            if groups and len(labels) < 1:
                labels.append((f"Pi 5 + HQ + Wide, on tray {k}", tuple(sc.world(groups[0])[:3, 3] + (0, 0, 640))))
    add_bay_camera(sc)
    labels.insert(0, ("overhead camera at the bay", bay_cam_point()))
    return labels


def bay_parts() -> dict:
    """The bar across the bay and the printed saddle clamp the bay unit's yoke is bolted to, world frame."""
    b = BAY_CAM
    x0, x1 = -V.OPEN_W / 2, V.OPEN_W / 2
    bar = box(x0, b["y"] - 10, b["bar_z"] - 10, x1, b["y"] + 10, b["bar_z"] + 10)
    clamp = box(-24, b["y"] - 14, b["bar_z"] - 14, 24, b["y"] + 14, b["bar_z"] + 14).edges("|X").fillet(3.0)
    clamp = clamp.cut(box(-25, b["y"] - 10.2, b["bar_z"] - 10.2, 25, b["y"] + 10.2, b["bar_z"] + 10.2))
    return {"bay bar": (bar, "svc_alu"), "saddle clamp": (clamp, "svc_petg")}


def bay_at(x: float = 0.0) -> np.ndarray:
    """The bay unit's rig frame, world: placed so that its pan axis stands on the saddle clamp's top (no post, no
    block); use with h = 0."""
    return I._T((x, BAY_CAM["y"] - PAN_AXIS[1], BAY_CAM["bar_z"] + 14.0 - PAN_AXIS[2]))


def add_bay_camera(sc, x=0.0) -> str:
    """The overhead unit at the bay: its yoke on a saddle clamp on a 2020 bar across the back of the bay, over Kardex's
    product envelope and under the tray stored over the opening; the head looks down and forward over the presented
    tray. Returns the head's group."""
    b = BAY_CAM
    add_meshes(sc, "baycam", meshes_of("baybar", bay_parts, 0.5), "baycam")
    sc.gmat["baycam"] = np.eye(4)
    sc.gmat["baycamrig"] = bay_at(x)
    for k in ("pan", "head"):
        add_meshes(sc, f"baycamrig{k}", meshes_of(f"rig_{k}", lambda k=k: rig_pieces()[k], 0.3), f"baycamrig{k}")
    sc.gmat["baycamrigpan"] = I._R((0, 0, 1), 0.0, PAN_AXIS)
    sc.parent["baycamrigpan"] = "baycamrig"
    sc.gmat["baycamrighead"] = I._R((1, 0, 0), b["tilt"], TILT_AXIS)
    sc.parent["baycamrighead"] = "baycamrigpan"
    return "baycamrighead"


def add_docks(sc, positions) -> dict:
    """A dock at each storage slot or bay position: {pos: head group}. The head slides +x by STROKE (set_dock)."""
    from scene import T
    fixed = meshes_of("dock_fixed", lambda: dock_parts(head=False), 0.5)
    head = meshes_of("dock_head", lambda: dock_parts(head=True), 0.3)
    out = {}
    for pos in positions:
        yc, zs = V.SLOTS[pos]
        g, gh = f"dock_{pos}", f"dockhead_{pos}"
        add_meshes(sc, g, fixed, g)
        add_meshes(sc, gh, head, gh)
        sc.gmat[g] = T((0, yc, zs))
        sc.parent[gh] = g
        sc.gmat[gh] = np.eye(4)
        out[pos] = gh
        add_meshes(sc, f"sw_{pos}", meshes_of("switches", switch_parts, 0.3), g)
        for key, *_ in MEDIA:
            sc.add(f"swlight_{pos}_{key}", switch_light_mesh(key), SWITCH_C[True], g, ambient=0.7, specular=0.2)
    riser = meshes_of("riser", riser_parts, 2.0)
    for yc, name in ((V.Y_FRONT, "front"), (V.Y_REAR, "rear")):
        add_meshes(sc, f"riser_{name}", riser, f"riser_{name}")
        sc.gmat[f"riser_{name}"] = T((0, yc, 0))
    return out


def set_dock(sc, pos, u):
    """u = 0 engaged, 1 pulled back."""
    from scene import T
    sc.gmat[f"dockhead_{pos}"] = T((STROKE * u, 0, 0))


def set_switches(sc, pos, on):
    """The dock's valves, contactor and link light at `pos`: on = True / False for all, or {medium: bool}."""
    for key, *_ in MEDIA:
        v = on.get(key, False) if isinstance(on, dict) else bool(on)
        sc.color[f"swlight_{pos}_{key}"] = SWITCH_C[v]


UPS_LED = {"mains": (0.15, 0.80, 0.30), "battery": (1.0, 0.62, 0.10)}     # charging on mains / carrying the tray


def ups_label_mesh():
    """'UPS' in white on the tray UPS's top and on its side facing the front of the tray, tray frame (PR #318: "I
    didn't see anywhere that showed UPS-s")."""
    import pyvista as pv
    x, y = UPS_AT
    u = UPS
    t = pv.Text3D("UPS", depth=0.1)
    k = 1.0 / (t.bounds[3] - t.bounds[2])

    def place(h, turn, at):
        m = t.scale(h * k, inplace=False)
        if turn:
            m = m.rotate_x(90, inplace=False)
        return m.translate(at, inplace=False)
    top = place(56.0, False, (x - 60, y, V.T_FLOOR + u["h"] + 1.5))
    side = place(120.0, True, (x, y - u["w"] / 2 - 1.5, V.T_FLOOR + u["h"] * 0.62))
    return top.merge(side).triangulate()


def ups_led_mesh():
    """The UPS's status strip, on its top and on its front-facing side (tray frame): green on mains, amber on battery."""
    x, y = UPS_AT
    u = UPS
    a = box(x - 170, y - u["w"] / 2 - 2.5, V.T_FLOOR + u["h"] * 0.32, x + 170, y - u["w"] / 2, V.T_FLOOR + u["h"] * 0.32
            + 26)
    b = box(x + 60, y - 26, V.T_FLOOR + u["h"], x + 200, y + 26, V.T_FLOOR + u["h"] + 2.5)
    return a.union(b)


def add_tray_services(sc, tray: str, ups=True) -> list:
    """The tray's plate, its lines (coloured when live) and its UPS with its label and status strip, riding with group
    tray_<k>."""
    add_meshes(sc, f"plate_{tray}", meshes_of("plate", plate_parts, 0.4), f"tray_{tray}")
    names = add_meshes(sc, f"lines_{tray}", meshes_of("lines", tray_lines, 0.5), f"tray_{tray}")
    if ups:
        add_meshes(sc, f"ups_{tray}", meshes_of("ups", ups_parts, 1.0), f"tray_{tray}")
        if "upslabel" not in _MESH_CACHE:
            import lab
            _MESH_CACHE["upslabel"] = ups_label_mesh()
            _MESH_CACHE["upsled"] = lab.to_mesh(_shape(ups_led_mesh()), 0.5)
        sc.add(f"ups label {tray}", _MESH_CACHE["upslabel"], (0.97, 0.97, 0.95), f"tray_{tray}", ambient=0.6,
               specular=0.1)
        sc.add(f"ups led {tray}", _MESH_CACHE["upsled"], UPS_LED["mains"], f"tray_{tray}", ambient=0.75, specular=0.1)
    return names


def set_ups(sc, tray: str, battery: bool):
    sc.color[f"ups led {tray}"] = UPS_LED["battery" if battery else "mains"]


class Flow:
    """Dots running along each live medium, from the service riser through the dock and the plate to the tray's end of
    the line, at the places given (slots, or 'open' for the bay): a frame hook moves them. on[(pos, key)] is how much
    of the path, from the riser end, is filled: 0 shut, 1 flowing all the way."""

    def __init__(self, sc, places, speed=160.0, pitch=45.0, bead=6.5):
        import pyvista as pv
        from scene import FPS, lighter
        self.sc, self.speed, self.pitch, self.dt = sc, speed, pitch, 1.0 / FPS
        self.t = 0.0
        self.on, self.paths = {}, {}
        self.ball = pv.Sphere(radius=bead, theta_resolution=10, phi_resolution=8)   # wider than the 7-8 mm lines
        M = mats()
        lp, dp = line_paths(), dock_paths()
        for pos in places:
            yc, zs = V.SLOTS[pos]
            for (key, _, mat, _), dy in zip(MEDIA, INSERT_DY):
                pts = np.array(dp[key] + [(X_FACE - 8.0, PLATE_Y + dy, ZC)] + lp[key], float) + (0.0, yc, zs)
                cum = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
                self.paths[(pos, key)] = (pts, cum)
                name = f"flow_{pos}_{key}"
                sc.add(name, self.ball.translate(pts[0], inplace=False), lighter(M[mat][:3], 0.55), name,
                       ambient=0.75, specular=0.1)
                sc.alpha[name] = 0.0
                self.on[(pos, key)] = 0.0
        sc.frame_hooks.append(self)

    def set(self, pos, f, keys=None):
        for key, *_ in MEDIA:
            if keys is None or key in keys:
                self.on[(pos, key)] = float(f)

    def __call__(self, sc):
        import pyvista as pv
        self.t += self.dt
        for (pos, key), (pts, cum) in self.paths.items():
            name = f"flow_{pos}_{key}"
            f = self.on[(pos, key)]
            L = cum[-1]
            n = max(4, int(L / self.pitch))
            s = ((np.arange(n) / n + self.t * self.speed / L) % 1.0) * L
            s = s[s <= f * L]
            if f <= 0.01 or not len(s):
                sc.alpha[name] = 0.0
                continue
            P = np.c_[np.interp(s, cum, pts[:, 0]), np.interp(s, cum, pts[:, 1]), np.interp(s, cum, pts[:, 2])]
            sc.set_mesh(name, pv.PolyData(P).glyph(geom=self.ball, scale=False, orient=False))
            sc.alpha[name] = 1.0


def set_live(sc, names, f):
    """Tray lines from grey (0, shut) to their colours (1, live)."""
    M = mats()
    grey = M["svc_plate"][:3]
    for n in names:
        c = M[n.split("/")[-1]][:3]
        sc.color[n] = tuple(g + (cc - g) * f for g, cc in zip(grey, c))


def make_lab(sc, data, robot=False):
    """animate.Lab whose gauges are set by the scene (svc_lines) and whose lamps go amber on a UPS (on_ups)."""
    import animate as A

    class SLab(A.Lab):
        def apply_state(self):
            super().apply_state()
            for k, on in getattr(self, "on_ups", {}).items():
                if on:
                    self.sc.color[f"tray {k} lamp"] = LAMP_UPS
                    self.sc.ambient[f"tray {k} lamp"] = 0.9

        def gauges(self):
            lines = getattr(self, "svc_lines", None)
            self.sc.gauges = list(lines) if lines else []
    return SLab(sc, data, robot=robot)


def build_vlm(name, data, idata, title, docks=True, cams=True, mp4=True, robot=False, scene_cls=None):
    """The VLM with trays A-F and their equipment (as line.py has them, without the floor line), the docks, plates,
    UPSs and cameras; robot=True adds the MiR250 and UR10e at the opening. Returns (scene, lab, {tray: [line actor
    names]})."""
    import line
    import tour
    from scene import Scene, T
    sc = (scene_cls or Scene)(name, title, gif=False, mp4=mp4)
    L = make_lab(sc, data, robot=robot)
    for k, loads in line.TRAY_LOADS.items():
        line.add_tray(sc, L, k)
        for key, x, y in loads:
            if key not in idata:
                continue
            inst, ents = idata[key]
            x0, x1, y0, y1, z0, _ = inst.bbox()
            at = T((x - (x0 + x1) / 2, y - (y0 + y1) / 2, V.T_FLOOR - z0))
            tour.Rig(sc, inst, ents, f"{k}_{key}:", at=at, parent=f"tray_{k}")
            L.eq_groups[k].append(f"{k}_{key}:body")
    live = {}
    if docks:
        add_docks(sc, [HOME[k] for k in HOME] + ["open"])
        for k in HOME:
            live[k] = add_tray_services(sc, k)
            set_live(sc, live[k], 1.0)
    if cams:
        for k in HOME:
            add_tray_cameras(sc, k)
        add_bay_camera(sc)
    L.apply_state()
    return sc, L, live


def hide(sc, groups=(), a=0.0):
    for n, g in sc.group_of.items():
        if g in groups:
            sc.alpha[n] = a


# ----------------------------------------------------------------------------------------------- vlm_services
CAM_S_WIDE = [(6800, -5200, 4300), (300, 0, 1700), (0, 0, 1)]
CAM_S_R2 = [(1930, 930, 1480), (1240, 1320, 1150), (0, 0, 1)]
CAM_S_MID = [(5200, -2900, 2500), (700, -200, 1100), (0, 0, 1)]
CAM_S_BAY = [(1930, -1130, 1240), (1240, -740, 910), (0, 0, 1)]
CAM_S_CAMS = [(1500, -3900, 1560), (-150, -1000, 1180), (0, 0, 1)]     # under the header, as the camera still


def movie_services(data, idata):
    import animate as A
    k = "A"
    slot = HOME[k]
    sc, L, live = build_vlm("vlm_services", data, idata,
                            "Vertical cloud lab: tray services through one docking coupling")
    L.skin(1.0)(1.0)
    L.on_ups = {}
    hide(sc, ("skin_R",))
    load_w = sum(POWER[i][0] for i in TRAY_ITEMS[k]) + len(TRAY_CAMS[k]) * POWER["pi_unit"][0]
    for pos in HOME.values():
        set_dock(sc, pos, 0.0)
    set_dock(sc, "open", 1.0)

    def lines_(tray_state, ups, dock_slot, dock_bay):
        L.svc_lines = [(f"Tray {k}", tray_state), ("UPS", ups), (f"Dock {slot}", dock_slot), ("Bay dock", dock_bay)]
        L.gauges()
    lines_(f"in {slot}, docked: on mains", "charged, standing by", "engaged", "pulled back, waiting")
    L.apply_state()
    n = 6
    dock_lbl = [(f"dock, slot {HOME[t]} (tray {t})", (1330, V.SLOTS[HOME[t]][0] + PLATE_Y, V.SLOTS[HOME[t]][1] + 160),
                 (0.86, 0.14 + 0.07 * i)) for i, t in enumerate(("E", "C", "B", "A", "D", "F"))]
    sc.step(f"1/{n}", "Every service a tray needs goes through one automatic coupling. The plate is on the tray's back "
            "right corner; each slot a tray uses, and the bay, has a matching dock in its right-hand side wall, fed by "
            "a riser in the side of the machine.", 3.6, None, hold=1.6, cam_to=CAM_S_WIDE,
            labels=dock_lbl + [("dock in the bay", (1330, V.Y_OPEN + PLATE_Y, V.Z_OPEN + 160), (0.86, 0.60)),
                               ("service risers", (RISER["x"], V.Y_REAR + PLATE_Y + RISER["dy"], 3200), (0.30, 0.16))])
    yc, zs = V.SLOTS[slot]
    wy, wz = yc + PLATE_Y, zs + ZC
    media_lbl = [(f"{lab_}: {cpl}", (X_FACE + 2, wy + dy, wz + (14 if key in ("power", "data") else 0)),
                  (0.03, 0.25 + 0.07 * i))
                 for i, ((key, lab_, _, cpl), dy) in enumerate(zip(MEDIA, INSERT_DY))]
    cut = ("col_rear", "posts", "lift_rails", "lift")
    sc.step(f"2/{n}", f"Tray {k} in its slot ({slot}). The dock holds the plate home: mains, Ethernet, compressed air, "
            "nitrogen and chilled water are live. CombiTac's docking frame lets the pins take up 4 mm of misalignment.",
            3.4, lambda u: hide(sc, cut, 1.0 - u), hold=2.4, cam_to=CAM_S_R2,
            labels=media_lbl + [("guide pins", (X_FACE - 20, wy + PIN_DY, wz), (0.84, 0.30)),
                                ("tray's UPS (Eaton 5PX 1500)", (UPS_AT[0], yc + UPS_AT[1], zs + UPS["h"]),
                                 (0.84, 0.55))])

    def release(u):
        f = min(1.0, u * 2.5)
        set_live(sc, live[k], 1.0 - f)
        L.on_ups[k] = f > 0.4
        set_dock(sc, slot, max(0.0, (u - 0.35) / 0.65))
        L.apply_state()
    lines_(f"in {slot}, releasing", f"carrying the tray, about {load_w:.0f} W", "pulling back", "pulled back, waiting")
    sc.step(f"3/{n}", "To let it go: the air, N2 and water supplies close and vent (the couplings must not part under "
            f"pressure), the tray's UPS takes the load, and the dock pulls back {STROKE:.0f} mm, clear of the tray.", 2.8,
            release, hold=1.2, labels=[("UPS takes over", (UPS_AT[0], yc + UPS_AT[1], zs + UPS["h"]), (0.84, 0.55)),
                                       (f"dock pulled back {STROKE:.0f} mm", (1290, wy, wz), (0.84, 0.30))])
    hide(sc, cut, 1.0)
    L.where[k] = None
    lines_("in transit, unplugged", f"carrying the tray, about {load_w:.0f} W", "pulled back", "pulled back, waiting")
    cap = (f"In transit: the extractor takes tray {k} from {slot} to the opening, about 6 s at Kardex's 0.7 m/s in and "
           "out and 2 m/s up and down. The UPS carries the instruments, the cameras and the tray's switch.")
    sc.step(f"4/{n}", cap, max(0.6, abs(L.lift_z - zs) / 1333), L.lift_to(zs), hold=0.1, cam_to=CAM_S_MID)
    sc.step(f"4/{n}", cap, 2.0, L.slide(k, 0.0), hold=0.1)
    yt, zt = V.SLOTS["open"]
    sc.step(f"4/{n}", cap, max(0.6, abs(zs - zt) / 1333), L.lift_to(zt, carry=k), hold=0.1)
    sc.step(f"4/{n}", cap, 0.6, L.shut(1.0), hold=0.0)
    sc.step(f"4/{n}", cap, 2.0, L.slide(k, yt), hold=0.0)
    sc.step(f"4/{n}", cap, 0.6, L.shut(0.0), hold=0.2)
    L.where[k] = "open"
    by, bz = V.Y_OPEN + PLATE_Y, V.Z_OPEN + ZC
    lines_("at the opening, docking", f"carrying the tray, about {load_w:.0f} W", "pulled back, empty slot",
           "pushing in")

    cut2 = ("col_front", "posts", "lift_rails", "bay", "shutter", "lift")

    def engage(u):
        set_dock(sc, "open", 1.0 - min(1.0, u / 0.65))
        f = max(0.0, (u - 0.6) / 0.4)
        set_live(sc, live[k], f)
        L.on_ups[k] = f < 0.5
        L.apply_state()
    sc.step(f"5/{n}", "At the opening the bay's dock pushes in: the guide pins enter the plate's bushings first, then "
            "the contacts and couplings mate and the supplies open. The instruments are back on mains and the UPS "
            "recharges.", 3.4, lambda u: (hide(sc, cut2, 1.0 - min(1.0, 3 * u)), engage(max(0.0, u * 1.4 - 0.4))),
            hold=1.8, cam_to=CAM_S_BAY,
            labels=[("bay dock", (1300, by, bz), (0.84, 0.25)),
                    ("guide pins", (X_FACE - 20, by + PIN_DY, bz), (0.84, 0.40)),
                    ("service plate", (X_FACE - 8, by - 60, bz - 30), (0.16, 0.40))])
    lines_("at the opening, docked: on mains", "recharging", "pulled back, empty slot", "engaged")
    hide(sc, ("skin_R",) + cut2, 1.0)
    cam_lbl = [(f"stream camera on tray {k}", A.tray_world(k, head_point(*c, dz=40.0)),
                (0.14 if c[0] < 0 else 0.86, 0.30)) for c in TRAY_CAMS[k]]
    sc.step(f"6/{n}", "The cameras: two Pi 5 units on tray A, standing in front of or beside their instruments and "
            "looking back, so they keep the room out of the picture, and an overhead one at the back of the bay, above "
            "Kardex's product envelope, looking down on the presented tray.", 3.2, None, hold=2.6, cam_to=CAM_S_CAMS,
            still=True, labels=cam_lbl + [("overhead camera at the bay", bay_cam_point(), (0.60, 0.13))])
    return sc.save()


def still_cameras(data, idata, k="E"):
    """out/vlm_cameras_still.png: tray k presented, its stream cameras and the bay's overhead one. Tray E, as tray D's
    OpenFlexures need their OpenSCAD meshes in .cache/ (openflexure/README.md)."""
    import animate as A
    sc, L, live = build_vlm("vlm_cameras", data, idata, f"Stream cameras: tray {k} at the opening", mp4=False)
    L.skin(1.0)(1.0)
    L.tray[k] = [V.Y_OPEN, V.Z_OPEN]
    L.where[k] = "open"
    L.lift_z = V.Z_OPEN
    set_dock(sc, "open", 0.0)
    set_dock(sc, HOME[k], 1.0)
    L.svc_lines = [(f"Tray {k}", f"at the opening, {len(TRAY_CAMS[k])} cameras"), ("Bay", "one overhead camera")]
    L.apply_state()
    # over the header, through the ghosted cladding: the bay unit stands above the header's underside
    sc.cam = [(1400, -3700, 2150), (-150, -950, 1250), (0, 0, 1)]
    lbl = []
    for i, c in enumerate(TRAY_CAMS[k]):
        lbl.append((f"Pi 5 + HQ + Wide, on tray {k}", tuple(A.tray_world(k, head_point(*c, dz=30.0))),
                    (0.12 + 0.30 * i + (0.08 if i == 2 else 0.0), 0.20 + 0.06 * (i % 2))))
    lbl.append(("overhead camera at the bay", bay_cam_point(), (0.60, 0.09)))
    cl = camera_clearances()
    top = max(v["top_over_floor_mm"] for kk, v in cl["tray_units"].items() if kk.startswith(k))
    sc.step("", f"Tray {k} at the opening: {len(TRAY_CAMS[k])} Pi 5 units, each on a 2020 post with a sliding block and "
            f"a pan-tilt head, aimed at an instrument's working face; the highest stands {top:.0f} mm over the tray "
            f"floor. They stand in front of or beside their instruments and look back, away from the opening. The overhead "
            f"unit sits on a bar at the back of the bay, {cl['bay_margin_mm']:.0f} mm over Kardex's product envelope and "
            f"{cl['bay_margin_to_F1_mm']:.0f} mm under the tray stored above the opening.", 0.1, None, hold=0.0, labels=lbl,
            still=True)
    return sc.save()


# ----------------------------------------------------------------------------------------------- vlm_hookups
# PR #318: "Assume UPS for now, and show the automatic electrical, gas, and water hookup setups during storage and
# when in the picking bay ... I didn't see anywhere that showed UPS-s." One tray, A, from its slot to the bay.
CAM_H_WIDE = [(6300, -3900, 4200), (450, 250, 1750), (0, 0, 1)]
CAM_H_SLOT = [(1760, 560, 1760), (1150, 1280, 1230), (0, 0, 1)]       # outside the right side, over tray A in R2
CAM_H_MID = [(5600, -3300, 2700), (600, -250, 1250), (0, 0, 1)]
CAM_H_BAY = [(2080, -1420, 1500), (1110, -760, 1020), (0, 0, 1)]      # outside the right side, at the bay
CAM_H_END = [(1500, -3300, 1900), (500, -950, 1150), (0, 0, 1)]


def ghost_prefix(sc, prefixes, a):
    """Every actor whose group starts with one of `prefixes` to opacity factor a (1 back to normal)."""
    for n, g in sc.group_of.items():
        if g.startswith(tuple(prefixes)):
            sc.alpha[n] = a


def ups_points() -> dict:
    """{tray: world point on top of its UPS} with every tray in its slot."""
    out = {}
    for k, pos in HOME.items():
        yc, zs = V.SLOTS[pos]
        out[k] = (UPS_AT[0], yc + UPS_AT[1], zs + V.T_FLOOR + UPS["h"])
    return out


def movie_hookups(data, idata):
    import animate as A
    k = "A"
    slot = HOME[k]
    sc, L, live = build_vlm("vlm_hookups", data, idata,
                            "Vertical cloud lab: one tray's hookups and its UPS, from its slot to the bay")
    L.skin(1.0)(1.0)
    L.on_ups = {}
    hide(sc, ("skin_R",))
    flow = Flow(sc, [slot, "open"])
    for pos in HOME.values():
        set_dock(sc, pos, 0.0)
        set_switches(sc, pos, True)
    set_dock(sc, "open", 1.0)
    set_switches(sc, "open", False)
    flow.set(slot, 1.0)
    load_w = sum(POWER[i][0] for i in TRAY_ITEMS[k]) + len(TRAY_CAMS[k]) * POWER["pi_unit"][0]
    ups_min = 44 * 300 / load_w                        # the retailer's 44 min at 300 W, scaled: a rough figure
    yc, zs = V.SLOTS[slot]
    by, bz = V.SLOTS["open"]
    fluids = ("air", "n2", "cws", "cwr")
    names_by = {key: [n for n in live[k] if n.split("/")[-1] == mat] for key, _, mat, _ in MEDIA}

    def gauges(tray, ups, dock_slot, dock_bay):
        L.svc_lines = [(f"Tray {k}", tray), ("UPS", ups), (f"Dock {slot}", dock_slot), ("Bay dock", dock_bay)]
        L.gauges()

    def at_slot(x, y, z, pos=slot):
        y0, z0 = V.SLOTS[pos]
        return (x, y0 + y, z0 + z)

    zr = PLATE_Z0 + PLATE_H + 25 + 30
    xv = DOCK_HX0 + 14
    gauges(f"in {slot}, docked: on mains", "charging from the dock's mains", "engaged, all six live", "pulled back")
    L.apply_state()
    n = 6
    ups_lbl = [(f"UPS, tray {t} ({HOME[t]})", p, (0.08 if i < 3 else 0.92, 0.30 + 0.08 * (i % 3)))
               for i, (t, p) in enumerate(sorted(ups_points().items(), key=lambda kv: -kv[1][2]))]
    sc.step(f"1/{n}", "Every tray carries its own UPS, an Eaton 5PX 1500 standing at its back right (white 'UPS' on "
            "top, a status strip: green on mains, amber on battery). In its slot, a tray is plugged into the machine "
            "through one automatic coupling in the slot's right-hand side wall.", 3.6, None, hold=2.2,
            cam_to=CAM_H_WIDE, labels=ups_lbl)
    # ---- 2: docked in storage
    cut = ("col_rear", "posts", "lift_rails", "lift", "riser_rear")
    eq = tuple(L.eq_groups[k]) + ("eq_A",)

    def into(u):
        hide(sc, cut, 1.0 - u)
        ghost_prefix(sc, eq, 1.0 - 0.75 * u)
    lbl2 = [("UPS: charging from the mains", (UPS_AT[0] - 80, yc + UPS_AT[1], zs + V.T_FLOOR + UPS["h"]), (0.10, 0.20)),
            ("valves on air, N2, water in and out: open", at_slot(xv + 13 * 3, VALVE_Y, zr + 25), (0.88, 0.16)),
            ("mains contactor: closed", at_slot(xv, VALVE_Y, zr + 25), (0.88, 0.26)),
            ("Ethernet: linked", at_slot(xv + 13, VALVE_Y, zr + 25), (0.88, 0.34)),
            ("dock head pressed on the plate", at_slot(X_FACE + 10, PLATE_Y + 70, PLATE_Z0 + PLATE_H), (0.88, 0.52)),
            ("lines on the tray: mains into the UPS,\nthe rest along the back rim", at_slot(1100, 400, 70), (0.10, 0.62))]
    sc.step(f"2/{n}", f"Stored in {slot}, docked: the dock in the side wall holds the plate home. Mains, Ethernet, "
            "compressed air, nitrogen and chilled water in and out are all live (the dots), from the service riser "
            "through the coupling to the tray; the UPS charges. Tray A's instruments are drawn faint.",
            3.4, into, hold=3.2, cam_to=CAM_H_SLOT, labels=lbl2, live=True)

    # ---- 3: shut, vent, on battery, pull back
    def release(u):
        state = {kk: True for kk, *_ in MEDIA}
        for i, key in enumerate(fluids):
            f = min(1.0, max(0.0, (u - 0.08 * i) / 0.12))
            state[key] = f < 0.5
            flow.set(slot, 1.0 - f, (key,))
            set_live(sc, names_by[key], 1.0 - f)
        g = min(1.0, max(0.0, (u - 0.40) / 0.10))
        state["power"] = state["data"] = g < 0.5
        set_switches(sc, slot, state)
        flow.set(slot, 1.0 - g, ("power", "data"))
        set_live(sc, names_by["power"] + names_by["data"], 1.0 - g)
        L.on_ups[k] = g > 0.5
        set_ups(sc, k, g > 0.5)
        set_dock(sc, slot, min(1.0, max(0.0, (u - 0.55) / 0.45)))
        L.apply_state()
    gauges(f"in {slot}, letting go", f"takes the load: about {load_w:.0f} W", "shutting, venting, pulling back",
           "pulled back")
    lbl3 = [("valves shut, lines vented", at_slot(xv + 13 * 3, VALVE_Y, zr + 25), (0.88, 0.16)),
            ("contactor open: mains off", at_slot(xv, VALVE_Y, zr + 25), (0.88, 0.26)),
            ("UPS: on battery", (UPS_AT[0] - 80, yc + UPS_AT[1], zs + V.T_FLOOR + UPS["h"]), (0.10, 0.20)),
            (f"dock pulls back {STROKE:.0f} mm", at_slot(X_FACE + 40, PLATE_Y + 70, PLATE_Z0 + PLATE_H),
             (0.88, 0.52))]
    sc.step(f"3/{n}", "Before the tray may move: the air, N2 and water valves shut and their lines vent (Staubli: the "
            "couplings must not part under pressure); the contactor opens, so the UPS takes the load; then the dock "
            f"pulls back {STROKE:.0f} mm, its pins 22 mm clear of the tray.", 4.6, release, hold=1.6, labels=lbl3,
            live=True)

    # ---- 4: in transit on the UPS
    tag = np.array([0.0, 0.0, 0.0])

    def follow():
        y, z = L.tray[k]
        tag[:] = (UPS_AT[0] - 80, y + UPS_AT[1], z + V.T_FLOOR + UPS["h"])

    def moving(f):
        def up(u):
            f(u)
            follow()
            ghost_prefix(sc, eq, 0.25 + 0.75 * min(1.0, u * 3) if f is first else 1.0)
        return up
    first = L.lift_to(zs)
    follow()
    hide(sc, cut, 1.0)
    L.where[k] = None
    gauges("in transit, unplugged", f"on battery, about {load_w:.0f} W (roughly {ups_min:.0f} min of it)",
           "pulled back", "pulled back, waiting")
    cap = (f"In transit, about 6 s from {slot} to the opening: no coupling, the UPS carries the instruments, the "
           "cameras and the tray's switch. The tray's lamp and the UPS's strip are amber.")
    lbl4 = [(f"tray {k}: on its UPS", tag, (0.16, 0.22))]
    sc.step(f"4/{n}", cap, max(0.6, abs(L.lift_z - zs) / 1333), moving(first), hold=0.1, cam_to=CAM_H_MID,
            labels=lbl4)
    sc.step(f"4/{n}", cap, 2.0, moving(L.slide(k, 0.0)), hold=0.1, labels=lbl4)
    sc.step(f"4/{n}", cap, max(0.6, abs(zs - bz) / 1333), moving(L.lift_to(bz, carry=k)), hold=0.1, labels=lbl4)
    sc.step(f"4/{n}", cap, 0.6, moving(L.shut(1.0)), hold=0.0, labels=lbl4)
    sc.step(f"4/{n}", cap, 2.0, moving(L.slide(k, by)), hold=0.0, labels=lbl4)
    sc.step(f"4/{n}", cap, 0.6, moving(L.shut(0.0)), hold=0.3, labels=lbl4)
    L.where[k] = "open"

    # ---- 5: the bay's dock takes over
    cut2 = ("col_front", "posts", "lift_rails", "lift", "riser_front", "shutter")

    def engage(u):
        hide(sc, cut2, 1.0 - min(1.0, 3 * u))
        set_dock(sc, "open", 1.0 - min(1.0, u / 0.35))
        g = min(1.0, max(0.0, (u - 0.38) / 0.10))
        state = {kk: False for kk, *_ in MEDIA}
        state["power"] = state["data"] = g > 0.5
        flow.set("open", g, ("power", "data"))
        set_live(sc, names_by["power"] + names_by["data"], g)
        L.on_ups[k] = g < 0.5
        set_ups(sc, k, g < 0.5)
        for i, key in enumerate(fluids):
            f = min(1.0, max(0.0, (u - 0.52 - 0.08 * i) / 0.16))
            state[key] = f > 0.05
            flow.set("open", f, (key,))
            set_live(sc, names_by[key], f)
        set_switches(sc, "open", state)
        L.apply_state()
    gauges("at the opening, docking", f"on battery, about {load_w:.0f} W", "pulled back, empty slot", "pushing in")
    lbl5 = [("bay dock: pins first", at_slot(X_FACE + 10, PLATE_Y + PIN_DY, ZC, "open"), (0.88, 0.50)),
            ("contactor closes: back on mains", at_slot(xv, VALVE_Y, zr + 25, "open"), (0.88, 0.22)),
            ("valves open: air, N2, water", at_slot(xv + 13 * 3, VALVE_Y, zr + 25, "open"), (0.88, 0.32)),
            ("UPS: recharging", (UPS_AT[0] - 80, by + UPS_AT[1], bz + V.T_FLOOR + UPS["h"]), (0.10, 0.24))]
    sc.step(f"5/{n}", "At the opening the bay's identical dock pushes in: the guide pins find the plate's bushings, "
            "the contacts and couplings mate, the contactor closes (the UPS recharges) and only then the valves open: "
            "the supplies fill the tray's lines again.", 5.0, engage, hold=2.4, cam_to=CAM_H_BAY, labels=lbl5,
            live=True)
    gauges("at the opening, docked: on mains", "recharging", "pulled back, empty slot", "engaged, all six live")
    hide(sc, cut2, 1.0)
    ghost_prefix(sc, eq, 1.0)
    lbl6 = [("tray A's UPS", A.tray_world(k, (UPS_AT[0] - 80, UPS_AT[1], V.T_FLOOR + UPS["h"])), (0.86, 0.20)),
            ("bay dock", A.tray_world(k, (X_FACE + 40, PLATE_Y, PLATE_Z0 + PLATE_H)), (0.86, 0.36))]
    sc.step(f"6/{n}", "Docked at the opening, as in its slot: on mains, with air, N2 and water. Where the tray is "
            "stored and where it is worked on, the same coupling; only the seconds between run on the tray's UPS.",
            3.0, lambda u: None, hold=2.6, cam_to=CAM_H_END, labels=lbl6, still=True, live=True)
    return sc.save()


# ----------------------------------------------------------------------------------------------- bay_camera
# PR #318: "The way the overhead camera at the bay gets called out is kind of weird. It probably deserves its own
# sequence and showing an upward looking angle from the front of the bay as if an operator and then also a rendered
# view of what the camera would see."
HQ_SENSOR = dict(w=4056 * 1.55e-3, h=3040 * 1.55e-3)        # IMX477, mm (SOURCES["hq_sensor"])


def camera_fov() -> dict:
    """Each bay camera's picture, degrees: the Wide's from Raspberry Pi's figures, the HQ's from its sensor and the
    16 mm lens's focal length."""
    f = 16.0
    w, h = HQ_SENSOR["w"], HQ_SENSOR["h"]
    hq = dict(across=2 * math.degrees(math.atan(w / 2 / f)), up_down=2 * math.degrees(math.atan(h / 2 / f)),
              diagonal=2 * math.degrees(math.atan(math.hypot(w, h) / 2 / f)), sensor_mm=[round(w, 2), round(h, 2)],
              focal_mm=f, source=SOURCES["hq_sensor"])
    wide = dict(across=102.0, up_down=67.0, diagonal=120.0, source=SOURCES["cm3_wide"],
                note="Raspberry Pi's figures. A 16:9 rectilinear picture 102 deg across is 69.6 deg up and down; the "
                     "lens's own distortion makes it 67")
    return {"wide": {k: (round(v, 1) if isinstance(v, float) else v) for k, v in wide.items()},
            "hq_16mm": {k: (round(v, 1) if isinstance(v, float) else v) for k, v in hq.items()}}


def frustum_meshes(c, f, r, u, half, z_floor, far=2400.0):
    """A camera's picture as a see-through pyramid from its lens to where it meets z_floor, and its edges."""
    import pyvista as pv
    ta, tb = math.tan(math.radians(half[0])), math.tan(math.radians(half[1]))
    pts = [np.asarray(c, float)]
    for a, b in ((1, 1), (1, -1), (-1, -1), (-1, 1)):
        d = f + a * ta * r + b * tb * u
        d = d / np.linalg.norm(d)
        t = (z_floor - c[2]) / d[2] if d[2] < -1e-6 else far
        pts.append(c + d * min(t, far))
    P = np.array(pts)
    sides = pv.PolyData(P, faces=np.hstack([[3, 0, 1, 2], [3, 0, 2, 3], [3, 0, 3, 4], [3, 0, 4, 1]]))
    lines = []
    for i in range(1, 5):
        lines.append(_tube([P[0], P[i]], 3.0, 6))
        lines.append(_tube([P[i], P[1 + i % 4]], 3.0, 6))
    return sides, pv.merge(lines), P


def _cam_scene_cls():
    from scene import Scene

    class CamScene(Scene):
        """A Scene that can black out the edges of the frame, so a camera's own picture keeps its shape."""
        mask_x = 0.0
        mask_y = 0.0

        def render_base(self):
            img = super().render_base()
            if self.mask_x > 0 or self.mask_y > 0:
                img = np.array(img)
                h, w = img.shape[:2]
                mx, my = int(round(self.mask_x * w)), int(round(self.mask_y * h))
                if mx:
                    img[:, :mx] = 22
                    img[:, w - mx:] = 22
                if my:
                    img[:my] = 22
                    img[h - my:] = 22
            return img
    return CamScene


def movie_bay_camera(data, idata):
    import animate as A
    import reach
    from scene import SIZE, T
    sc, L, live = build_vlm("bay_camera", data, idata, "Vertical cloud lab: the overhead camera at the bay",
                            robot=True, scene_cls=_cam_scene_cls())
    L.skin(1.0)(1.0)
    k = "B"                                           # the doser's tray: the arm's busiest
    L.tray[k] = [V.Y_OPEN, V.Z_OPEN]
    L.where[k] = "open"
    L.lift_z = V.Z_OPEN
    set_dock(sc, "open", 0.0)
    set_dock(sc, HOME[k], 1.0)
    L.svc_lines = [(f"Tray {k}", "at the opening, docked"), ("Arm", "UR10e on a MiR250")]
    L.apply_state()
    sc.cam = [(2500, -6600, 2500), (0, -900, 1350), (0, 0, 1)]
    rb = L.robot
    b = BAY_CAM
    opt = camera_optics(bay_at(), 0.0, 0.0, 0.0, b["tilt"])
    fov = camera_fov()
    zf = V.Z_OPEN + V.T_FLOOR
    M = mats()
    fr = {}
    for key, col in (("wide", (0.20, 0.45, 0.85)), ("hq", (0.95, 0.55, 0.10))):
        c, f, r, u = opt[key]
        half = (51.0, 33.5) if key == "wide" else (fov["hq_16mm"]["across"] / 2, fov["hq_16mm"]["up_down"] / 2)
        sides, edges, P = frustum_meshes(c, f, r, u, half, zf)
        sc.add(f"frustum {key}", sides, col, "frusta", opacity=0.16 if key == "wide" else 0.30, specular=0.0,
               ambient=0.6)
        sc.add(f"frustum {key} edges", edges, col, "frusta", ambient=0.6, specular=0.0)
        fr[key] = P
    hide(sc, ("frusta",), 0.0)
    rig = ("baycamrig", "baycamrigsl", "baycamrigpan", "baycamrighead")
    # the arm's work: from parked, over the vial rack, down to the vial, up, over to the doser's cup and in
    seeds = [np.radians(q) for q in ((-90, -100, 120, -110, -90, 0), (-90, -60, 90, -120, -90, 0),
                                     (-60, -80, 100, -110, -90, 0), (-120, -80, 100, -110, -90, 0))]
    seats = reach.seats()
    rack, cup = seats["vial rack (tray B)"], seats["multi-doser cup (tray B)"]
    poses = [T((0, 0, 140)) @ rack, rack, T((0, 0, 140)) @ rack, T((0, -140, 60)) @ cup, cup, T((0, -140, 60)) @ cup,
             T((0, 0, 140)) @ rack]
    qs = [rb.q.copy()]
    for Tw in poses:
        sol = reach.solve("ur10e", Tw, [qs[-1]] + seeds)
        if sol is not None:
            qs.append(np.asarray(sol[0], float))

    def arm(i0, i1):
        """The arm along the joint waypoints qs[i0..i1], over the step."""
        path = qs[i0:i1 + 1]

        def up(u):
            s = u * (len(path) - 1)
            j = min(int(s), len(path) - 2)
            rb.set(path[j] + (path[j + 1] - path[j]) * (s - j))
        return up if len(path) > 1 else (lambda u: None)
    n = 4
    eye = np.array([420.0, -2450.0, 1600.0])           # an operator's eyes, 1.6 m up, 0.9 m in front of the VLM's face
    target = np.array(bay_cam_point())
    cam_op = [tuple(eye), tuple(target + (0, 0, -60)), (0, 0, 1)]
    lbl1 = [("overhead camera: Pi 5, HQ Camera with a 16 mm lens,\nCamera Module 3 Wide, on a pan-tilt head",
             target, (0.62, 0.12)),
            ("on a 2020 bar across the back of the bay", (-700.0, b["y"], b["bar_z"]), (0.20, 0.26))]
    sc.step(f"1/{n}", "From where an operator stands, 0.9 m in front of the opening, eyes at 1.6 m: the bay's overhead "
            "camera, up under the header at the back of the bay, looking down over the presented tray (here tray B, "
            "the doser's).", 4.0, None, hold=2.6, cam_to=cam_op, view_angle_to=50.0, labels=lbl1)

    def show_fr(u):
        hide(sc, ("frusta",), u)
        arm(0, 1)(u)
    lbl2 = [(f"Wide: {fov['wide']['across']:.0f} x {fov['wide']['up_down']:.0f} deg", tuple(fr["wide"][2]),
             (0.10, 0.60)),
            (f"HQ, 16 mm lens: {fov['hq_16mm']['across']:.1f} x {fov['hq_16mm']['up_down']:.1f} deg",
             tuple((fr["hq"][1] + fr["hq"][2]) / 2), (0.86, 0.66))]
    sc.step(f"2/{n}", f"What it covers: the Camera Module 3 Wide (blue) sees {fov['wide']['across']:.0f} x "
            f"{fov['wide']['up_down']:.0f} degrees, the whole tray; the HQ Camera with the 16 mm lens (orange) "
            f"{fov['hq_16mm']['across']:.1f} x {fov['hq_16mm']['up_down']:.1f} degrees, a patch about a tenth of it, "
            "for detail.", 3.0, show_fr, hold=2.6, labels=lbl2)
    # ---- through its own lenses
    c, f, r, u = opt["wide"]
    va_wide = 2 * math.degrees(math.atan(math.tan(math.radians(51.0)) * SIZE[1] / SIZE[0]))
    cam_wide = [tuple(c), tuple(c + f * 1000.0), tuple(u)]

    def into_wide(s):
        hide(sc, ("frusta",), 1.0 - min(1.0, 2 * s))
        hide(sc, rig, 1.0 - min(1.0, max(0.0, (s - 0.6) / 0.3)))
        sc.mask_y = (1.0 - math.tan(math.radians(33.5)) / math.tan(math.radians(va_wide / 2))) / 2 * \
            max(0.0, (s - 0.85) / 0.15)
    sc.step(f"3/{n}", "Into the camera.", 2.2, into_wide, hold=0.0, cam_to=cam_wide, view_angle_to=va_wide)
    L.svc_lines = [("Camera", "Camera Module 3 Wide"), ("Picture", "102 x 67 deg, 16:9"), ("Arm", "to the vial rack")]
    L.gauges()
    capw = ("What the Wide sees: the whole presented tray and the arm working on it. Rendered from the camera's own "
            "position and aim, 102 degrees across (Raspberry Pi's figures: 102 x 67, 120 diagonal).")
    sc.step(f"3/{n}", capw, 3.4, arm(1, 3), hold=0.2)
    L.svc_lines[2] = ("Arm", "to the doser's cup")
    L.gauges()
    sc.step(f"3/{n}", capw, 3.4, arm(3, 5), hold=0.6, still=True)
    # the head turns on its pan and tilt joints to put the HQ on the doser's cup, where the gripper is
    at = bay_at()
    _, pan_c, tilt_c = rig_pose(float(at[0, 3]), float(at[1, 3]), tuple(cup[:3, 3]), h=0.0, z0=float(at[2, 3]), post=0.0)
    c, f, r, u = camera_optics(at, 0.0, 0.0, pan_c, tilt_c)["hq"]
    hq = fov["hq_16mm"]
    cam_hq = [tuple(c), tuple(c + f * 1000.0), tuple(u)]
    va_hq = hq["up_down"]
    mx = (1.0 - math.tan(math.radians(hq["across"] / 2)) /
          (math.tan(math.radians(va_hq / 2)) * SIZE[0] / SIZE[1])) / 2

    def to_hq(s):
        sc.mask_y = 0.0
        sc.mask_x = mx * s
        sc.gmat["baycamrigpan"] = I._R((0, 0, 1), pan_c * s, PAN_AXIS)
        sc.gmat["baycamrighead"] = I._R((1, 0, 0), b["tilt"] + (tilt_c - b["tilt"]) * s, TILT_AXIS)
    L.svc_lines = [("Camera", "HQ Camera, 16 mm lens"), ("Picture", f"{hq['across']:.1f} x {hq['up_down']:.1f} deg, "
                                                                     "4:3"), ("Arm", "at the doser's cup")]
    L.gauges()
    caph = (f"What the HQ Camera sees through the 16 mm lens, {hq['across']:.1f} x {hq['up_down']:.1f} degrees (its "
            f"sensor is {hq['sensor_mm'][0]} x {hq['sensor_mm'][1]} mm: 2 atan(6.29 / 32) across), with the head "
            f"turned {abs(pan_c):.0f} degrees and tilted {tilt_c:.0f} down onto the doser's cup: a 4:3 close-up of "
            "the gripper at work.")
    sc.step(f"4/{n}", caph, 1.4, to_hq, hold=0.2, cam_to=cam_hq, view_angle_to=va_hq)
    sc.step(f"4/{n}", caph, 3.2, arm(5, 6), hold=0.4)
    sc.step(f"4/{n}", caph, 3.0, arm(6, 7), hold=1.6)
    return sc.save()


# ----------------------------------------------------------------------------------------------- cabling
# An overhead ladder tray at 2800 mm, behind the line's machines (their backs are at y = -758 to -927; it passes over
# the Aconity and the wire EDM, which are deeper), round the back of the VLM, with a drop to each machine. The
# placements of the tray, the panel, the switch and the controls are ours; the ratings are the makers'.
LADDER_Z, LADDER_Y, LADDER_W = 2800.0, -560.0, 300.0
LADDER_PATH = [(-8200.0, LADDER_Y), (-1750.0, LADDER_Y), (-1750.0, 2000.0), (1750.0, 2000.0), (1750.0, LADDER_Y),
               (10200.0, LADDER_Y)]
PANEL = (-500.0, 2300.0, 900.0, 500.0, 2450.0, 2100.0)        # a 208Y/120 V panelboard on the wall behind the VLM
SWITCH_AT = (1430.0, 200.0, 2600.0)                            # PoE+ switch on the VLM's right-hand side
UTIL = {"n2": (1700.0, 700.0), "chiller": (1700.0, 1250.0)}    # beside the VLM, right-hand side, behind the line
CHARGER_AT = (-2000.0, -1500.0)                                # MiR Charge 48V, in the gap left of the VLM
RAIL_CTRL_AT = (10150.0, -2250.0)                              # MachineMotion 2 and the UR control box, rail's end

CIRCUITS = [   # (key, what, supply, load, source, kind)
    ("vlm", "Kardex Shuttle XP 500 (drives, controls)", "208 V 3-phase (#53)",
     "not published by Kardex; a used XP 500 2450x864 lists 400 V 17 A, used XP listings 8.6 kVA (24 A per phase at "
     "208 V)", "#53; machineseeker and exapro listings (search snippets)", "snippet"),
    ("docks", "tray docks: six slots and the bay, at most six live", "208Y/120 V: L1, L2, N, PE per dock, 30 A "
     "breaker (CombiTac O3 mm contacts: 39 A)", "tray F 3.5 kW, tray C 1.2 kW, tray D 1.1 kW, the rest under 0.7 kW "
     "(services.json)", "the instruments' ratings in POWER; CombiTac catalogue p.26", "derived"),
    ("repowder", "AMAZEMET rePowder atomizer and its chiller", "400 V 3-phase and 230 V, 32 A plugs; the optimizer "
     "draws up to about 60 A", "as left", "rePowder-BYU-Installation-Details.txt (the install call)", "published"),
    ("glovebox", "Inert PureLab HE 2GB glovebox", "not found", "not found", "Inert's manual (NIST copy) has a "
     "pre-installation chapter, not read", "not found"),
    ("aconity", "Aconity MIDI LPBF printer", "not found", "laser 500 W (Gauss) or 1200 W (ring); the machine's supply "
     "was not found", "zhaw.ch's page on its MIDI (snippet)", "snippet"),
    ("instron_floor", "Instron 68FM-100", "208-240 V 1-phase (reduced ratings) or 208/240/400 V 3-phase (preferred)",
     "not found", "Instron 6800 floor-model sheet (snippet)", "snippet"),
    ("instron_small", "Instron 68SC-2", "100/120/220/240 V 1-phase, 47-63 Hz", "1400 VA max (table models)",
     "Instron 6800 table-model brochure (snippet)", "snippet"),
    ("wire_edm", "FANUC ROBOCUT alpha-C400iC", "200 V +-10 % 3-phase (or 220 V)", "13 kVA (36 A per phase at 208 V)",
     "FANUC Europe data sheet (snippet)", "snippet"),
    ("rail", "Vention MachineMotion 2 (four-drive) for the rail", "85-264 V 1-phase", "1200 W typical, 9 A rated at "
     "120 V", "Vention MachineMotion 2 user manual (snippet)", "snippet"),
    ("ur", "UR10e control box", "100-240 V 1-phase, 47-440 Hz", "350 W typical, 615 W maximum average",
     "UR's specifications via a cobot guide (snippet)", "snippet"),
    ("mir", "MiR Charge 48V (MiR250 layout only)", "100-240 V 1-phase, a standard 15 A outlet",
     "48 V at up to 40 A out, about 1.9 kW", "MiR (fetched); IDEC listing; Konica Minolta (snippets)", "snippet"),
    ("n2", "Parker Balston UHPN2-1100 N2 generator", "120 V 1-phase", "not found; needs 60-125 psig air",
     "govsci, gmi-inc, marshallscientific (snippets)", "snippet"),
    ("chiller", "Thermo Scientific ThermoFlex 900 chiller", "not found", "900 W of cooling at 20 C; its input was not "
     "found", "thermofisher.com TF900 (snippet)", "snippet"),
    ("network", "PoE+ switch: the bay camera, a link to each riser and on to the docks", "120 V 1-phase",
     "PoE+ (IEEE 802.3at): up to 30 W a port at the switch; a Pi 5 takes about 4 W typical, 27 W supply rating",
     "raspberrypi.com", "published"),
]


def _tube(pts, r=12.0, sides=10):
    import pyvista as pv
    pts = np.asarray(pts, float)
    poly = pv.PolyData(pts)
    poly.lines = np.hstack([[len(pts)], np.arange(len(pts))])
    return poly.tube(radius=r, n_sides=sides).triangulate()


def _box(x0, y0, z0, x1, y1, z1):
    import pyvista as pv
    return pv.Box(bounds=(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))).triangulate()


def ladder_mesh(path=LADDER_PATH, z=LADDER_Z, w=LADDER_W, h=90.0, pitch=300.0):
    """A ladder cable tray along an axis-aligned path: two side rails and rungs every `pitch`."""
    import pyvista as pv
    parts = []
    for (xa, ya), (xb, yb) in zip(path[:-1], path[1:]):
        if abs(ya - yb) < 1e-6:                   # along x
            x0, x1 = sorted((xa, xb))
            x0, x1 = x0 - w / 2, x1 + w / 2
            for s in (-1, 1):
                parts.append(_box(x0, ya + s * w / 2 - 4, z, x1, ya + s * w / 2 + 4, z + h))
            for x in np.arange(x0 + pitch / 2, x1, pitch):
                parts.append(_box(x - 12, ya - w / 2, z, x + 12, ya + w / 2, z + 18))
        else:
            y0, y1 = sorted((ya, yb))
            for s in (-1, 1):
                parts.append(_box(xa + s * w / 2 - 4, y0, z, xa + s * w / 2 + 4, y1, z + h))
            for y in np.arange(y0 + pitch / 2, y1, pitch):
                parts.append(_box(xa - w / 2, y - 12, z, xa + w / 2, y + 12, z + 18))
    return pv.merge(parts)


def movie_cabling(data, idata):
    import line
    import pyvista as pv
    M = mats()
    loads = line.TRAY_LOADS        # the OpenFlexure meshes may not be built yet: leave out what isn't loaded
    line.TRAY_LOADS = {k: [x for x in v if x[0] in idata] for k, v in loads.items()}
    try:
        sc, L, rigs = line.build("vlm_cabling", data, idata)
    finally:
        line.TRAY_LOADS = loads
    sc.title = "Vertical cloud lab: power and network cabling"
    add_docks(sc, [HOME[k] for k in HOME] + ["open"])
    for k in HOME:
        add_tray_services(sc, k)
        add_tray_cameras(sc, k)
    add_bay_camera(sc)
    L.skin(1.0)(1.0)
    L.apply_state()
    L.show_gauges = False
    keep = {n for n, g in sc.group_of.items() if g.startswith(("dock", "riser", "cam", "baycam", "floor"))}
    for n in sc.actors:
        if n in keep or n in ("floor", "line floor", "floor shadow"):
            continue
        sc.base_alpha[n] = min(sc.base_alpha[n], 0.16)
    POW, NET = M["svc_power"][:3], M["svc_data"][:3]
    # the machines' extents in the line (from the models; see notes/services.md)
    mach = {"glovebox": (-6350.0, -758.0, 1795.0), "repowder": (-3600.0, -700.0, 1600.0),
            "aconity": (3250.0, -328.0, 2324.0), "instron_floor": (5600.0, -766.0, 2287.0),
            "instron_small": (7000.0, -927.0, 1410.0), "wire_edm": (8700.0, 982.0, 1970.0)}
    sc.add("cab/ladder", ladder_mesh(), M["svc_ladder"][:3], "cabling", specular=0.5)
    sc.add("cab/panel", _box(*PANEL), M["svc_cabinet"][:3], "cabling")
    feed = _tube([((PANEL[0] + PANEL[3]) / 2, (PANEL[1] + PANEL[4]) / 2, PANEL[5]),
                  ((PANEL[0] + PANEL[3]) / 2, (PANEL[1] + PANEL[4]) / 2, LADDER_Z + 30),
                  ((PANEL[0] + PANEL[3]) / 2, 2000.0, LADDER_Z + 30)], 30)
    sc.add("cab/feed", feed, POW, "cabling")
    drops = {}
    for key, (x, back, top) in mach.items():
        if back > LADDER_Y:                  # the ladder passes over it: straight down into its top
            pts = [(x, LADDER_Y, LADDER_Z), (x, LADDER_Y, top + 30)]
        else:
            pts = [(x, LADDER_Y, LADDER_Z), (x, LADDER_Y, 1150.0), (x, back + 5, 1150.0)]
        drops[key] = pts[-1]
        sc.add(f"cab/drop {key}", _tube(pts, 16), POW, "cabling")
    # the VLM: its supply into the back panel, and the riser feeds over the top from the utilities and the switch
    sc.add("cab/drop vlm", _tube([(1200, 2000, LADDER_Z), (1200, 1600, LADDER_Z)], 22), POW, "cabling")
    drops["vlm"] = (1200, 1600, LADDER_Z)
    sc.add("cab/drop docks", _tube([(1450, 2000, LADDER_Z), (1450, 1700, LADDER_Z), (1450, 1700, 3880),
                                    (RISER["x"], 1700, 3880), (RISER["x"], V.Y_REAR + PLATE_Y + RISER["dy"], 3880),
                                    (RISER["x"], V.Y_REAR + PLATE_Y + RISER["dy"], 3800)], 18), POW, "cabling")
    sc.add("cab/drop docks front", _tube([(RISER["x"], 1700, 3880), (RISER["x"], V.Y_FRONT + PLATE_Y + RISER["dy"],
                                                                       3880),
                                          (RISER["x"], V.Y_FRONT + PLATE_Y + RISER["dy"], 3800)], 18), POW, "cabling")
    # the switch and its links
    sx, sy, sz = SWITCH_AT
    sc.add("cab/switch", _box(sx, sy - 220, sz - 22, sx + 60, sy + 220, sz + 22), M["svc_ups"][:3], "cabling")
    net = [_tube([(1750, sy, LADDER_Z), (sx + 30, sy, LADDER_Z), (sx + 30, sy, sz + 22)], 8),
           _tube([(sx + 30, sy - 200, sz), (sx + 30, sy - 200, 3860), (RISER["x"] + 20, sy - 200, 3860),
                  (RISER["x"] + 20, V.Y_FRONT + PLATE_Y + RISER["dy"], 3860),
                  (RISER["x"] + 20, V.Y_FRONT + PLATE_Y + RISER["dy"], 3800)], 8),
           _tube([(sx + 30, sy + 200, sz), (sx + 30, sy + 200, 3860), (RISER["x"] + 20, sy + 200, 3860),
                  (RISER["x"] + 20, V.Y_REAR + PLATE_Y + RISER["dy"], 3860),
                  (RISER["x"] + 20, V.Y_REAR + PLATE_Y + RISER["dy"], 3800)], 8),
           _tube([(sx + 30, sy - 100, sz - 22), (sx + 30, sy - 100, 1900), (1380, sy - 100, 1900),
                  (1380, BAY_CAM["y"], 1900), (1380, BAY_CAM["y"], BAY_CAM["bar_z"]),
                  (V.OPEN_W / 2, BAY_CAM["y"], BAY_CAM["bar_z"])], 8)]
    sc.add("cab/network", pv.merge(net), NET, "cabling")
    # the N2 generator and the chiller beside the VLM, and their hoses to the risers' tops
    nx, ny = UTIL["n2"]
    sc.add("cab/n2 generator", _box(nx, ny, 0, nx + N2GEN["w"], ny + N2GEN["d"], N2GEN["h"]), M["svc_cabinet"][:3],
           "cabling")
    cx, cy = UTIL["chiller"]
    sc.add("cab/chiller", _box(cx, cy, 0, cx + 500, cy + 600, 700), (0.55, 0.62, 0.70), "cabling")
    hoses = {"svc_n2": [(nx + 150, ny + 200, N2GEN["h"]), (nx + 150, ny + 200, 3900), (RISER["x"] - 20, ny + 200, 3900)],
             "svc_cws": [(cx + 150, cy + 300, 700), (cx + 150, cy + 300, 3920), (RISER["x"] - 10, cy + 300, 3920)],
             "svc_cwr": [(cx + 300, cy + 300, 700), (cx + 300, cy + 300, 3940), (RISER["x"], cy + 300, 3940)],
             "svc_air": [(1750, 900, LADDER_Z), (1600, 900, LADDER_Z), (1600, 900, 3960), (RISER["x"] + 10, 900, 3960)]}
    for mat, pts in hoses.items():
        sc.add(f"cab/{mat}", _tube(pts, 10), M[mat][:3], "cabling")
    sc.add("cab/drop utilities", _tube([(1750, 1000, LADDER_Z), (nx + 250, 1000, LADDER_Z), (nx + 250, 1000, 1200),
                                        (nx + 250, ny + 300, 1200), (nx + 250, ny + 300, N2GEN["h"])], 12), POW,
           "cabling")
    # the rail: its cable chain in a trough in front of the beam, and the controls at its right-hand end
    ry = line.RAIL_Y - 124.0 - 70.0
    sc.add("cab/rail trough", _box(line.RAIL_X[0], ry - 45, 0, line.RAIL_X[1], ry + 45, 70), M["svc_ladder"][:3],
           "cabling")
    fx = (line.RAIL_X[0] + line.RAIL_X[1]) / 2
    chain = pv.merge([_box(line.PARK_X, ry - 35, 8, fx, ry + 35, 36), _box(line.PARK_X - 60, ry - 35, 8,
                                                                            line.PARK_X, ry + 35, 360)])
    sc.add("cab/rail chain", chain, M["svc_chain"][:3], "cabling")
    rx, ry2 = RAIL_CTRL_AT
    sc.add("cab/rail controls", _box(rx - 250, ry2 - 200, 0, rx + 250, ry2 + 200, 900), M["svc_cabinet"][:3], "cabling")
    sc.add("cab/rail feed", _tube([(10200, LADDER_Y, LADDER_Z), (10200, LADDER_Y, 2400), (10200, ry2, 2400),
                                   (10200, ry2, 900)], 14), POW, "cabling")
    sc.add("cab/rail run", _tube([(rx - 250, ry, 40), (fx, ry, 40)], 12), (0.2, 0.2, 0.22), "cabling")
    # the MiR's charger (marker, not to size) and its feed from the ladder
    mx, my = CHARGER_AT
    sc.add("cab/mir charger", _box(mx - 150, my - 60, 0, mx + 150, my + 60, 450), (0.25, 0.25, 0.27), "cabling")
    sc.add("cab/mir feed", _tube([(-1750, -900, LADDER_Z), (mx, -900, LADDER_Z), (mx, -900, 30), (mx, my + 60, 30)],
                                 12), POW, "cabling")
    L.apply_state()
    n = 6
    def lbl(t, p, at):
        return (t, tuple(p), at)
    sc.step(f"1/{n}", "Power and network for the line, everything else drawn faint: one ladder tray overhead at 2.8 m, "
            "behind the machines and round the back of the VLM, with a drop to each machine.", 3.4, None, hold=1.6,
            cam_to=[(4600, -16800, 11500), (1200, -300, 1200), (0, 0, 1)],
            labels=[lbl("ladder tray, 2.8 m up", (-4500, LADDER_Y, LADDER_Z + 90), (0.30, 0.12)),
                    lbl("208Y/120 V panel (placement ours)", (0, 2375, 2100), (0.66, 0.22))])
    sc.step(f"2/{n}", "Left: the glovebox (rating not found) and the rePowder atomizer, which needs 400 V three-phase "
            "and 230 V on 32 A plugs, its optimizer drawing up to about 60 A (the install call).", 3.0, None, hold=1.6,
            cam_to=[(-7400, -8200, 4600), (-4600, -900, 1300), (0, 0, 1)],
            labels=[lbl("rePowder: 400 V 3-ph + 230 V, 32 A plugs", drops["repowder"], (0.70, 0.18)),
                    lbl("glovebox: rating not found", drops["glovebox"], (0.20, 0.18)),
                    lbl("MiR Charge 48V: 100-240 V in, 48 V 40 A out", (mx, my, 450), (0.80, 0.42))])
    sc.step(f"3/{n}", "The VLM: its 208 V three-phase supply (#53) into the back, and the dock circuits up and over the "
            "top into the two risers. A PoE+ switch on its side feeds the risers and the bay camera; N2 and chilled "
            "water come from units standing beside it.", 3.4, None, hold=2.0,
            cam_to=[(6200, -5200, 5600), (900, 300, 2600), (0, 0, 1)],
            labels=[lbl("VLM: 208 V 3-phase", drops["vlm"], (0.20, 0.14)),
                    lbl("dock circuits, 208Y/120 V", (RISER["x"], 1700, 3880), (0.20, 0.24)),
                    lbl("PoE+ switch", (sx + 60, sy, sz), (0.84, 0.30)),
                    lbl("N2 generator (Parker UHPN2-1100)", (nx + 150, ny, N2GEN["h"]), (0.84, 0.46)),
                    lbl("chiller (ThermoFlex 900; box not to size)", (cx + 250, cy, 700), (0.84, 0.58)),
                    lbl("service risers", (RISER["x"], V.Y_FRONT + PLATE_Y + RISER["dy"], 2600), (0.20, 0.40))])
    sc.step(f"4/{n}", "Right: the Aconity MIDI (supply not found), the two Instrons and the wire EDM, the biggest load "
            "here at 13 kVA, three-phase 200 V.", 3.0, None, hold=1.8,
            cam_to=[(9400, -9800, 5200), (6000, -800, 1300), (0, 0, 1)],
            labels=[lbl("Aconity MIDI: not found", drops["aconity"], (0.16, 0.16)),
                    lbl("68FM-100: 208-240 V 1-ph or 3-ph", drops["instron_floor"], (0.36, 0.10)),
                    lbl("68SC-2: 1-ph, 1400 VA", drops["instron_small"], (0.62, 0.10)),
                    lbl("ROBOCUT: 200 V 3-ph, 13 kVA", drops["wire_edm"], (0.84, 0.16))])
    sc.step(f"5/{n}", "The rail: its cable chain lies in a trough in front of the beam and follows the carriage; "
            "MachineMotion 2 (1200 W typical) and the UR10e's control box (350 W typical) stand at its end.", 3.0,
            None, hold=1.8, cam_to=[(3600, -6400, 2600), (2200, -1900, 300), (0, 0, 1)],
            labels=[lbl("cable chain to the carriage", (line.PARK_X + 300, ry, 36), (0.20, 0.30)),
                    lbl("chain trough, full length", (2600, ry, 70), (0.70, 0.30))])
    sc.step(f"6/{n}", "All of it: one overhead route, drops at the machines' backs, nothing on the floor of the cell "
            "but the rail's own chain.", 2.6, None, hold=2.4,
            cam_to=[(4600, -16800, 11500), (1200, -300, 1200), (0, 0, 1)], still=True)
    return sc.save()


# ----------------------------------------------------------------------------------------------- the numbers
def heat_budget() -> dict:
    """Per tray: the load from the instruments' ratings, the cameras and the UPS's loss; for the VLM: what that puts
    into the enclosure, the airflow to carry it away, and the rise with no ventilation."""
    trays = {}
    for k, items in TRAY_ITEMS.items():
        rows = {i: dict(w=POWER[i][0], kind=POWER[i][1], source=POWER[i][2]) for i in items}
        ncam = len(TRAY_CAMS.get(k, []))
        rows["cameras"] = dict(w=ncam * POWER["pi_unit"][0], kind="published", source=POWER["pi_unit"][2] +
                               f"; {ncam} units")
        load = sum(r["w"] for r in rows.values())
        rows["ups loss"] = dict(w=round(load * POWER["ups_loss_frac"][0], 1), kind="estimate",
                                source=POWER["ups_loss_frac"][2])
        total = sum(r["w"] for r in rows.values())
        trays[k] = dict(slot=HOME[k], items=rows, total_w=round(total), ups_ok=load <= 1500.0,
                        estimated_share=round(sum(r["w"] for r in rows.values() if r["kind"] == "estimate") /
                                              max(total, 1), 2))
    all_w = sum(t["total_w"] for t in trays.values())
    rho_cp = 1.2 * 1005.0                  # air, J/(m3 K)
    W, D, H = (V.UNIT_W + 2 * V.SKIN) / 1000, (V.UNIT_D + 2 * V.SKIN) / 1000, V.UNIT_H / 1000
    area = 2 * (W * H + D * H) + W * D     # walls and roof, m2
    k_encl = 5.5                           # W/(m2 K), painted sheet steel, still air: the usual enclosure-sizing figure
    scen = {"everything on at its rating": all_w,
            "printing in storage (tray C) and the furnace holding (tray F at a third of 2.8 kW)":
                trays["C"]["total_w"] + round(2800 / 3) + 100,
            "idle: controllers, cameras and UPSs only (about 60 W a tray, an estimate)": 6 * 60}
    out = {}
    for name, w in scen.items():
        out[name] = dict(w=round(w), rise_k_unventilated=round(w / (k_encl * area), 1),
                         airflow_m3h_for_5k=round(w / (rho_cp * 5) * 3600),
                         airflow_m3h_for_10k=round(w / (rho_cp * 10) * 3600))
    return dict(
        trays=trays,
        vlm=dict(enclosure_m=[round(W, 2), round(D, 2), round(H, 2)], surface_m2=round(area, 1),
                 scenarios=out,
                 method="rise with no ventilation = W / (5.5 W/m2K x surface): the usual figure for painted sheet "
                        "steel in still air, an estimate for a machine this size; airflow = W / (rho cp dT), air at "
                        "1.2 kg/m3 and 1005 J/kg K"),
        utilities=dict(
            ups=dict(model="Eaton 5PX1500RTNG2", size_mm=[UPS["w"], UPS["d"], UPS["h"]], rating="1500 VA, 120 V",
                     runtime="44 min at 300 W (230 V model, retailer)", where="on every tray, back right",
                     transit_s="about 6 s from R2 to the opening: 2 x 1030 mm at 0.7 m/s (3 s), 246 mm at 2 m/s "
                               "(0.1 s), plus the shutter and accelerations (not published); R4 adds about 0.8 s",
                     source=SOURCES["ups"]),
            n2=dict(model="Parker Balston UHPN2-1100", size_mm=[N2GEN["w"], N2GEN["d"], N2GEN["h"]],
                    fits_tray=N2GEN["h"] <= V.MAX_GOODS_H, where="beside the VLM; N2 through the docks",
                    source=SOURCES["n2"]),
            chiller=dict(model="Thermo Scientific ThermoFlex 900", cooling_w=900,
                         heat_to_room="900 W plus its own input, which was not found", where="beside the VLM; water "
                         "through the docks, so its heat stays out of the enclosure", source=SOURCES["chiller"]),
        ),
        ask_kardex=[
            "The heat a tray may give off in a slot, and in total, and the interior temperature the drives and "
            "controls are rated for.",
            "Whether a column can be ventilated (a filtered fan and an outlet on the roof), and whether a furnace at "
            "650 C may run inside at all.",
            "The extractor's repeatability at a slot, for a dock that takes 4 mm of misalignment.",
            "Whether the side walls can take a window and a dock behind the supports at a slot, and the space between "
            "the column wall and the cladding (about 108 mm in the model).",
            "Whether power to a slot can stay on while a tray is stored, and what they would fit (the dealer offered "
            "a quick-connect cord).",
        ],
    )


def _rig_points(post_h=POST_H, foot=True) -> dict:
    """{piece: (n, 4) homogeneous points} of a rig's meshes, rig frame, modelled pose."""
    out = {}
    for k in ("slider", "pan", "head"):
        pts = np.vstack([m.points for m in meshes_of(f"rig_{k}", lambda k=k: rig_pieces()[k], 0.3).values()
                         if m.n_points])
        out[k] = np.c_[pts, np.ones(len(pts))]
    pts = np.vstack([m.points for m in meshes_of(f"mast{post_h}{foot}", lambda: mast_parts(post_h, foot), 0.5).values()
                     if m.n_points])
    out["mast"] = np.c_[pts, np.ones(len(pts))]
    return out


def _world_points(at, post, h, pan, tilt, post_h=POST_H, foot=True) -> dict:
    ms = rig_matrices(at, post, h, pan, tilt)
    return {k: (p @ ms[k].T)[:, :3] for k, p in _rig_points(post_h, foot).items()}


def bay_points() -> np.ndarray:
    """Every point of the bay unit, its clamp and bar, world."""
    from scene import T
    b = BAY_CAM
    pts = {k: v for k, v in _world_points(bay_at(), 0.0, 0.0, 0.0, b["tilt"]).items() if k in ("pan", "head")}
    bar = np.vstack([m.points for m in meshes_of("baybar", bay_parts, 0.5).values() if m.n_points])
    return np.vstack([*pts.values(), bar])


def camera_optics(at, post, h, pan, tilt) -> dict:
    """{camera: (centre, forward, right, up)} world, for the Wide and the HQ of a rig."""
    m = rig_matrices(at, post, h, pan, tilt)["head"]
    out = {}
    hy, hz = TILT_AXIS[1], TILT_AXIS[2]
    lens = {"wide": (HEAD["wide_x"], hy - HEAD["tilt_y"] + HEAD["nose_y"] - 0.8, hz + HEAD["wide_z"]),
            "hq": (HEAD["hq_x"], hy - HEAD["tilt_y"] + HEAD["plate_t"] + HEAD["hq_standoff"] - HQ_CS_SEAT - 51.0, hz)}
    R3 = m[:3, :3]
    for k, c in lens.items():
        centre = (m @ np.array([*c, 1.0]))[:3]
        out[k] = (centre, R3 @ np.array([0, -1.0, 0]), R3 @ np.array([-1.0, 0, 0]), R3 @ np.array([0, 0, 1.0]))
    return out


def bay_view(step=25.0) -> dict:
    """What the bay unit sees of the presented tray's floor: the share of a 25 mm grid inside each camera's picture
    (rectilinear, the published angles: Wide 102 x 67, HQ with the 16 mm lens 22.2 x 16.7 degrees), where the Wide's
    axis meets the floor, and what it misses."""
    from scene import T
    b = BAY_CAM
    opt = camera_optics(bay_at(), 0.0, 0.0, 0.0, b["tilt"])
    z = V.Z_OPEN + V.T_FLOOR
    xs = np.arange(-V.TRAY_W / 2, V.TRAY_W / 2 + 1, step)
    ys = np.arange(V.Y_OPEN - V.TRAY_D / 2, V.Y_OPEN + V.TRAY_D / 2 + 1, step)
    P = np.array([(x, y, z) for x in xs for y in ys])
    out = {}
    for k, (hw, hv) in (("wide", (51.0, 33.5)), ("hq", (11.1, 8.35))):
        c, f, r, u = opt[k]
        d = P - c
        fw = d @ f
        ok = (fw > 0) & (np.abs(d @ r) <= fw * math.tan(math.radians(hw))) & \
             (np.abs(d @ u) <= fw * math.tan(math.radians(hv)))
        t = (z - c[2]) / f[2]
        hit = c + f * t
        miss = P[~ok]
        out[k] = dict(share_of_tray=round(float(ok.mean()), 3), axis_hits_y=round(float(hit[1])),
                      axis_hits_from_tray_centre_mm=round(float(hit[1] - V.Y_OPEN)),
                      distance_mm=round(float(t)), lens_at=[round(float(v)) for v in c],
                      missed_y_range=None if not len(miss) else [round(float(miss[:, 1].min())),
                                                                 round(float(miss[:, 1].max()))])
    out["tray_y_range"] = [V.Y_OPEN - V.TRAY_D / 2, V.Y_OPEN + V.TRAY_D / 2]
    return out


FOV_HALF = {"wide": (51.0, 33.5), "hq": (11.1, 8.35)}      # half-angles, degrees (FOV in SOURCES; hq is 22.2 x 16.7)


def frustum_rays(f, r, u, half, n=(41, 27)) -> np.ndarray:
    """Unit directions over a rectilinear picture of half-angles `half` (degrees) about forward f, right r and up u."""
    a = math.tan(math.radians(half[0])) * np.linspace(-1.0, 1.0, n[0])
    b = math.tan(math.radians(half[1])) * np.linspace(-1.0, 1.0, n[1])
    A, B = np.meshgrid(a, b)
    d = f[None, :] + A.reshape(-1, 1) * r[None, :] + B.reshape(-1, 1) * u[None, :]
    return d / np.linalg.norm(d, axis=1)[:, None]


def out_of_bay(c, d) -> np.ndarray:
    """Rays from c along d (world, the tray presented): True where a ray leaves through the opening into the room
    before it meets the presented tray's floor. Nothing else counts as cover: the instruments have windows, so a camera
    that would see the room through one does."""
    y_face = -V.UNIT_D / 2 - V.SKIN
    zf = V.Z_OPEN + V.T_FLOOR
    with np.errstate(divide="ignore", invalid="ignore"):
        tf = np.where(d[:, 2] < -1e-9, (zf - c[2]) / d[:, 2], np.inf)
        ty = np.where(d[:, 1] < -1e-9, (y_face - c[1]) / d[:, 1], np.inf)
    pf = c + d * np.where(np.isfinite(tf), tf, 0.0)[:, None]
    on_floor = np.isfinite(tf) & (np.abs(pf[:, 0]) <= V.TRAY_W / 2) & (np.abs(pf[:, 1] - V.Y_OPEN) <= V.TRAY_D / 2)
    py = c + d * np.where(np.isfinite(ty), ty, 0.0)[:, None]
    through = np.isfinite(ty) & (np.abs(py[:, 0]) <= V.OPEN_W / 2) & (py[:, 2] >= V.Z_SILL) & \
        (py[:, 2] <= V.Z_OPEN_TOP)
    return through & ~(on_floor & (tf < ty))


def unit_view(x, y, ax, ay, az, post=None, h=None) -> dict:
    """What a tray unit at (x, y) aimed at (ax, ay, az) (tray frame) sees with its tray presented: the share of the
    Wide's and the HQ's picture that looks out through the opening into the room (out_of_bay), and how far the HQ is
    from what it is aimed at."""
    from scene import T
    h = CAM_H if h is None else h
    post, pan, tilt = rig_pose(x, y, (ax, ay, az), h, post=post)
    opt = camera_optics(T((x, V.Y_OPEN + y, V.Z_OPEN + V.T_FLOOR)), post, h, pan, tilt)
    out = {}
    for k, (c, f, r, u) in opt.items():
        out[f"{k}_sees_room"] = round(float(out_of_bay(c, frustum_rays(f, r, u, FOV_HALF[k])).mean()), 3)
    c = opt["hq"][0]
    out["hq_to_aim_mm"] = round(float(np.linalg.norm(c - np.array([ax, V.Y_OPEN + ay, V.Z_OPEN + az]))))
    out.update(post_yaw_deg=round(post), pan_deg=round(pan, 1), tilt_down_deg=round(tilt, 1))
    return out


def camera_views() -> dict:
    """Every tray unit, with its tray presented: the share of the Wide's and the HQ's picture that looks out through
    the opening into the room, now and where round 5 stood it (TRAY_CAMS_ROUND5)."""
    out = {}
    for k, layout in TRAY_CAMS.items():
        for i, (x, y, ax, ay, az, *fixed) in enumerate(layout):
            v = unit_view(x, y, ax, ay, az, post=fixed[0] if fixed else None)
            old = TRAY_CAMS_ROUND5.get(k, [])
            if i < len(old):
                ox, oy, oax, oay, oaz, *of = old[i]
                o = unit_view(ox, oy, oax, oay, oaz, post=of[0] if of else None)
                v["round5"] = dict(post_xy=[ox, oy], wide_sees_room=o["wide_sees_room"],
                                   hq_sees_room=o["hq_sees_room"])
            v["post_xy"] = [x, y]
            v["aim"] = [ax, ay, az]
            out[f"{k}{i}"] = v
    return out


def _seg_dist(P, a, b):
    """Distance of each point in P (n, 3) to the segment a-b."""
    ab = b - a
    t = np.clip(((P - a) @ ab) / max(float(ab @ ab), 1e-9), 0.0, 1.0)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


def bay_arm_clearance(radius=75.0) -> dict:
    """The UR10e on its MiR250 at the opening (reach.py's poses: the workflow's seats, and every reachable point of
    the presented tray on a 50 mm grid, gripper down, 100 and 250 mm over its floor) against the bay unit, its post
    and its bar: the arm as capsules of `radius` round its links from the shoulder to the TCP (the UR10e's tubes are
    about 90 mm across, its joints about 150, the 2F-85 about 150 wide), so this is conservative."""
    import animate as A
    import reach
    import ur_arm
    P = bay_points()
    seeds = [np.radians(q) for q in ((-90, -100, 120, -110, -90, 0), (-90, -60, 90, -120, -90, 0),
                                     (-60, -80, 100, -110, -90, 0), (-120, -80, 100, -110, -90, 0),
                                     (-90, -120, 60, -30, 90, 0), (-90, -45, 45, -90, -90, 0))]
    poses = dict(reach.seats())
    for hgt in (100.0, 250.0):
        for x in np.arange(-V.TRAY_W / 2 + 50, V.TRAY_W / 2 - 49, 100.0):
            for y in np.arange(-V.TRAY_D / 2 + 50, V.TRAY_D / 2 - 49, 100.0):
                poses[f"grid {x:.0f} {y:.0f} {hgt:.0f}"] = A.down(A.tray_world("B", (x, y, V.T_FLOOR + hgt)))
    B = reach.base_world()
    worst = (float("inf"), None, None)
    n = 0
    for name, Tw in poses.items():
        sol = reach.solve("ur10e", Tw, seeds)
        if sol is None:
            continue
        n += 1
        fk = ur_arm.fk("ur10e", sol[0])
        chain = [(B @ fk[k])[:3, 3] for k in ("shoulder", "upper_arm", "forearm", "wrist1", "wrist2", "wrist3")]
        chain.append((B @ fk["tool0"] @ np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, ur_arm.TCP_MM],
                                                   [0, 0, 0, 1.0]]))[:3, 3])
        d = min(float(_seg_dist(P, a, b).min()) for a, b in zip(chain[:-1], chain[1:])) - radius
        if d < worst[0]:
            worst = (d, name, max(float(c[2]) for c in chain))
    return dict(poses_checked=n, smallest_gap_mm=round(worst[0]), at_pose=worst[1],
                highest_joint_there_mm=None if worst[2] is None else round(worst[2]), capsule_radius_mm=radius,
                note="reach.py's poses; the arm as capsules round its joint origins, the 2F-85 to the TCP")


def tray_instrument_boxes() -> dict:
    """{tray: [(name, (x0, x1, y0, y1, z0, z1))]}: each instrument's box as modelled, tray frame, where line.py
    (trays D-F, sizes from out/instruments.json) and animate.py (trays A-C, lab.meshes()) put it. The multi-doser on
    tray B is a 600 x 470 x 560 mm box round its model."""
    import animate as A
    import lab
    import line
    sizes = json.loads((OUT / "instruments.json").read_text())
    out = {}
    for k, loads in line.TRAY_LOADS.items():
        for key, x, y in loads:
            w, d, h = sizes[key]["model_mm"]
            out.setdefault(k, []).append((key, (x - w / 2, x + w / 2, y - d / 2, y + d / 2, V.T_FLOOR, V.T_FLOOR + h)))
    eq = lab.meshes()["equipment"]
    for k, items in A.LOADS.items():
        for key, x, y in items:
            ent = eq.get(key) or eq.get(f"{key}_frame")
            if ent is not None:
                b = ent[1]
                w, d, h = b[1] - b[0], b[3] - b[2], b[5] - b[4]
                out.setdefault(k, []).append((key, (x - w / 2, x + w / 2, y - d / 2, y + d / 2, V.T_FLOOR,
                                                    V.T_FLOOR + h)))
    out.setdefault("B", []).append(("carousel", (-50.0, 550.0, -551.0, -81.0, V.T_FLOOR, V.T_FLOOR + 560.0)))
    if "rack" in dict((key, 0) for key, *_ in A.LOADS.get("B", [])) and not any(n == "rack" for n, _ in out["B"]):
        import props
        _, rx, ry = next(item for item in A.LOADS["B"] if item[0] == "rack")
        b = props.vial_rack()[0].bounds                     # the printed vial rack the arm takes the vial from
        out["B"].append(("rack", (rx + b[0], rx + b[1], ry + b[2], ry + b[3], V.T_FLOOR, V.T_FLOOR + b[5])))
    for k in HOME:                       # every tray's UPS, and its service plate with the bracket and the lines
        x, y = UPS_AT
        out.setdefault(k, []).append(("UPS", (x - UPS["d"] / 2, x + UPS["d"] / 2, y - UPS["w"] / 2, y + UPS["w"] / 2,
                                              V.T_FLOOR, V.T_FLOOR + UPS["h"])))
        out[k].append(("service plate", (X_FACE - PLATE_T - 60 - 120 - 18 * 5 - 4, SIDE, PLATE_Y - PLATE_L / 2,
                                         PLATE_Y + PLATE_L / 2, V.T_FLOOR, PLATE_Z0 + PLATE_H + 30)))
    return out


def tray_unit_gaps() -> dict:
    """{unit: smallest gap (mm) from the rig to an instrument's box on its tray, which instrument, and whether it
    stays 12 mm inside the tray's rim}. Boxes are coarse: a unit over a low instrument shows its gap to the box."""
    from scene import T
    boxes = tray_instrument_boxes()
    out = {}
    for k, layout in TRAY_CAMS.items():
        for i, (x, y, ax, ay, az, *fixed) in enumerate(layout):
            post, pan, tilt = rig_pose(x, y, (ax, ay, az), post=fixed[0] if fixed else None)
            P = np.vstack(list(_world_points(T((x, y, V.T_FLOOR)), post, CAM_H, pan, tilt).values()))
            best = (1e9, None)
            for key, (x0, x1, y0, y1, z0, z1) in boxes.get(k, []):
                d = np.sqrt(np.maximum(np.maximum(x0 - P[:, 0], P[:, 0] - x1), 0) ** 2 +
                            np.maximum(np.maximum(y0 - P[:, 1], P[:, 1] - y1), 0) ** 2 +
                            np.maximum(np.maximum(z0 - P[:, 2], P[:, 2] - z1), 0) ** 2)
                if float(d.min()) < best[0]:
                    best = (float(d.min()), key)
            inside = bool(((np.abs(P[:, 0]) <= V.TRAY_W / 2 - 12) & (np.abs(P[:, 1]) <= V.TRAY_D / 2 - 12)).all())
            out[f"{k}{i}"] = dict(gap_mm=round(best[0]), nearest=best[1], inside_rim=inside)
    return out


def camera_clearances() -> dict:
    """The top of every tray unit over the tray floor (against Kardex's 727.5 mm), and the bay unit's lowest point
    against the top of the product envelope at the opening (tray floor + 727.5 + 20 mm) and its highest against
    the underside of tray F1, stored over the opening: from the meshes."""
    from scene import T
    tops = {}
    for k, layout in TRAY_CAMS.items():
        for i, (x, y, ax, ay, az, *fixed) in enumerate(layout):
            post, pan, tilt = rig_pose(x, y, (ax, ay, az), post=fixed[0] if fixed else None)
            pts = _world_points(T((x, y, V.T_FLOOR)), post, CAM_H, pan, tilt)
            top = max(float(p[:, 2].max()) for p in pts.values()) - V.T_FLOOR
            tops[f"{k}{i}"] = dict(top_over_floor_mm=round(top, 1), post_yaw_deg=round(post), pan_deg=round(pan, 1),
                                   tilt_down_deg=round(tilt, 1))
    P = bay_points()
    env = V.Z_OPEN + V.T_FLOOR + V.MAX_GOODS_H + V.GOODS_CLEAR
    f1 = V.SLOTS["F1"][1]
    r = head_reach()
    return dict(tray_units=tops, limit_mm=V.MAX_GOODS_H, bay_lowest_mm=round(float(P[:, 2].min()), 1),
                envelope_top_mm=env, bay_margin_mm=round(float(P[:, 2].min()) - env, 1),
                bay_highest_mm=round(float(P[:, 2].max()), 1), tray_F1_underside_mm=f1,
                bay_margin_to_F1_mm=round(f1 - float(P[:, 2].max()), 1),
                bay_to_shutter_mm=round(V.Y_SHUTTER - float(P[:, 1].max()), 1),
                tray_units_to_instruments=tray_unit_gaps(),
                head=dict(rises_over_tilt_axis_mm=r["up"], reaches_below_mm=-r["down"],
                          gap_to_yoke_base_at_max_tilt_mm=r["gap_to_base"], tilt_max_deg=TILT_MAX))


# ----------------------------------------------------------------------------------------------- docks and the lift
def _bbox(shape) -> np.ndarray:
    b = _shape(shape).BoundingBox()
    return np.array([b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax])


def _bboxes(name: str, shape) -> dict:
    """{name (#i): box} for each solid of a shape: the two carriages, say, are two boxes, not one across the shaft."""
    solids = _shape(shape).Solids()
    if len(solids) <= 1:
        return {name: _bbox(shape)}
    return {f"{name} #{i + 1}": _bbox(s) for i, s in enumerate(solids)}


def _shift(bb, d) -> np.ndarray:
    return np.asarray(bb, float) + np.array([d[0], d[0], d[1], d[1], d[2], d[2]], float)


def _gap(a, b) -> float:
    """Distance between two boxes [x0, x1, y0, y1, z0, z1]; 0 where they touch or overlap."""
    d = np.maximum(0.0, np.maximum(np.asarray(a)[0::2] - np.asarray(b)[1::2], np.asarray(b)[0::2] - np.asarray(a)[1::2]))
    return float(np.linalg.norm(d))


def _nearest(A: dict, B: dict) -> tuple:
    """(gap, name in A, name in B) of the closest pair of boxes."""
    return min((_gap(a, b), na, nb) for na, a in A.items() for nb, b in B.items())


def tray_boxes(k: str) -> dict:
    """{part: box} of tray k with everything on it, tray frame: the pan, the plate, its bracket and lines, the UPS,
    each instrument's box and each camera unit's pieces."""
    from scene import T
    out = {"tray pan": np.array([-V.TRAY_W / 2, V.TRAY_W / 2, -V.TRAY_D / 2, V.TRAY_D / 2, 0.0, V.T_FLOOR + V.T_RIM])}
    for parts in (plate_parts(), tray_lines(), ups_parts()):
        for n, (s, _) in parts.items():
            out.update(_bboxes(n, s))
    for key, bb in tray_instrument_boxes().get(k, []):
        if key not in ("UPS", "service plate"):
            out[key] = np.array(bb, float)
    for i, (x, y, ax, ay, az, *fixed) in enumerate(TRAY_CAMS.get(k, [])):
        post, pan, tilt = rig_pose(x, y, (ax, ay, az), post=fixed[0] if fixed else None)
        for piece, P in _world_points(T((x, y, V.T_FLOOR)), post, CAM_H, pan, tilt).items():
            out[f"camera {k}{i} {piece}"] = np.array([P[:, 0].min(), P[:, 0].max(), P[:, 1].min(), P[:, 1].max(),
                                                      P[:, 2].min(), P[:, 2].max()])
    return out


def dock_boxes(pos: str, u: float) -> dict:
    """{part: box} of the dock at a slot or the bay, world; u = 0 engaged, 1 pulled back."""
    yc, zs = V.SLOTS[pos]
    out = {}
    for head in (False, True):
        for n, (s, _) in dock_parts(head=head).items():
            out.update({m: _shift(b, (STROKE * u if head else 0.0, yc, zs)) for m, b in _bboxes(n, s).items()})
    return out


def dock_clearance(dz: float = 10.0) -> dict:
    """Are the docks in the lift's way? Every part is taken as its bounding box, so each gap is a lower bound.
    * The extractor (platform, carriages, tray-pull unit), empty and carrying each tray with all it holds, travels the
      shaft from 300 mm under the lowest slot to 300 mm over the highest, past every dock (each slot a tray uses, and
      the bay's), engaged and pulled back.
    * Each tray slides out of its slot onto the extractor, and from the extractor into the bay, past that place's dock,
      pulled back.
    * The plate's inserts against the extractor's carriages, with the tray on the extractor, as built and as it was
      with the plate's face flush with the tray's side."""
    ext = {}
    for n, (s, _, _) in V.extractor().items():
        ext.update(_bboxes(n, s))
    places = sorted({*HOME.values(), "open"}, key=lambda p: (V.SLOTS[p][0], V.SLOTS[p][1]))
    docks = {(p, u): dock_boxes(p, u) for p in places for u in (0.0, 1.0)}
    zs_all = [V.SLOTS[p][1] for p in places]
    zz = np.arange(min(zs_all) - 300.0, max(zs_all) + 300.0 + 1, dz)
    trays = {k: tray_boxes(k) for k in HOME}
    lift = {}
    for load in ["empty"] + list(HOME):
        rows = {}
        for (p, u), D in docks.items():
            best = (1e9, None, None, None)
            for z in zz:
                moving = {f"extractor: {n}": _shift(b, (0, 0, z)) for n, b in ext.items()}
                if load != "empty":
                    moving.update({f"tray {load}: {n}": _shift(b, (0, 0, z)) for n, b in trays[load].items()})
                g, a, b = _nearest(moving, D)
                if g < best[0]:
                    best = (g, a, b, z)
            rows[f"{p} {'engaged' if u == 0 else 'pulled back'}"] = dict(gap_mm=round(best[0], 1), moving=best[1],
                                                                         dock=best[2], lift_z=float(best[3]))
        lift[load] = rows
    slide = {}
    moves = [(k, HOME[k], V.SLOTS[HOME[k]][0], 0.0, V.SLOTS[HOME[k]][1]) for k in HOME] + \
            [(k, "open", 0.0, V.Y_OPEN, V.Z_OPEN) for k in HOME]
    for k, p, y0, y1, z in moves:
        best = (1e9, None, None)
        for y in np.linspace(y0, y1, 121):
            moving = {n: _shift(b, (0, y, z)) for n, b in trays[k].items()}
            g, a, b = _nearest(moving, docks[(p, 1.0)])
            if g < best[0]:
                best = (g, a, b)
        slide[f"tray {k} {'out of ' + p if p != 'open' else 'into the bay'}"] = dict(
            gap_mm=round(best[0], 1), tray_part=best[1], dock_part=best[2])
    plate = {n: b for n, b in trays["A"].items() if n.startswith("plate ")}
    car = {n: b for n, b in ext.items() if n.startswith("extractor carriages")}
    now = _nearest(plate, car)
    flush = _nearest({n: _shift(b, (SIDE - X_FACE, 0, 0)) for n, b in plate.items()}, car)
    shutter = np.array([-V.OPEN_W / 2, V.OPEN_W / 2, V.Y_SHUTTER - 6, V.Y_SHUTTER + 6, V.Z_OPEN - 10,
                        V.Z_OPEN_TOP + 40 + (V.Z_OPEN_TOP - V.Z_SILL + 10)])
    shut = min(_nearest({"shutter": shutter}, docks[("open", u)]) for u in (0.0, 1.0))
    lift_min = min((r["gap_mm"], load, name) for load, rows in lift.items() for name, r in rows.items())
    slide_min = min((r["gap_mm"], name) for name, r in slide.items())
    return dict(
        method="every part as its bounding box (a lower bound on each gap); the extractor at every height from "
               f"{zz[0]:.0f} to {zz[-1]:.0f} mm in {dz:.0f} mm steps; each slide in 121 steps",
        lift=lift, slide=slide,
        plate_inserts_to_carriages_mm=dict(now=round(now[0], 1), with_the_face_flush=round(flush[0], 1)),
        bay_dock_to_shutter_mm=round(shut[0], 1),
        smallest=dict(lift_mm=lift_min[0], lift_case=f"{lift_min[1]}, {lift_min[2]}",
                      slide_mm=slide_min[0], slide_case=slide_min[1]),
        walls="each dock's head passes through a window in its side wall (a column's perforated wall, or the bay's "
              "slatted one); the window takes out the tray supports 25-100 mm over the slot on that side, which only "
              "a tray stored in that slot would use",
    )


def draw_clearance(res: dict | None = None, path=None):
    """out/dock_lift_clearance.png: the right-hand side in plan at a front slot's height, with the gaps, and every
    case's smallest gap."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    res = res or dock_clearance()
    path = path or OUT / "dock_lift_clearance.png"
    ink, muted, grid = "#1f2328", "#59636e", "#d0d7de"
    c_lift, c_dock, c_tray, c_plate = "#c0392b", "#57606a", "#8c959f", "#24292f"
    fig = plt.figure(figsize=(13.0, 6.6), dpi=130)
    ax = fig.add_axes([0.07, 0.16, 0.47, 0.74])
    yf, yr = V.Y_FRONT, V.Y_REAR

    def rect(bb, color, alpha=1.0, lw=0.0, fill=True, z=1, ls="-"):
        ax.add_patch(Rectangle((bb[0], bb[2]), bb[1] - bb[0], bb[3] - bb[2], facecolor=color if fill else "none",
                               edgecolor=color, alpha=alpha, lw=lw, zorder=z, ls=ls))
    # columns' side walls, the shaft's guide rails, the extractor's carriage and platform edge
    wall_x = V.TRAY_W / 2 + 45
    for yc in (yf, yr):
        rect([wall_x, wall_x + 12, yc - V.TRAY_D / 2 - 30, yc + V.TRAY_D / 2 + 30], "#afb8c1", 0.9)
    ext = {}
    for n, (s, _, _) in V.extractor().items():
        ext.update(_bboxes(n, s))
    rect(ext["extractor platform"], c_lift, 0.25)
    for n, b in ext.items():
        if n.startswith("extractor carriages"):
            rect(b, c_lift, 0.9, z=3)
    for sy in (-1, 1):
        x = V.UNIT_W / 2 - 115
        y = sy * (V.TRAY_D / 2 + 38)
        rect([x - 20, x + 20, y - 15, y + 15], "#6e7781", 1.0, z=4)
    # a tray on the extractor, and the trays in a front and a rear slot, with their plates
    plate = {n: _bbox(s) for n, (s, _) in plate_parts().items()}
    for yc, ls in ((0.0, "--"), (yf, "-"), (yr, "-")):
        rect([-V.TRAY_W / 2, V.TRAY_W / 2, yc - V.TRAY_D / 2, yc + V.TRAY_D / 2], c_tray, 1.0, lw=1.2, fill=False,
             z=2, ls=ls)
        for n, b in plate.items():
            rect(_shift(b, (0, yc, 0)), c_plate if n in ("service plate", "plate bracket") else "#e36209", 1.0, z=5)
    for p, u in (("F1", 1.0), ("R2", 0.0)):
        for n, b in dock_boxes(p, u).items():
            if n.startswith("hose"):
                continue
            rect(b, c_dock, 0.55 if n == "dock housing" else 1.0, z=4)
    ax.set_xlim(820, 1420)
    ax.set_ylim(-1500, 1500)
    ax.set_aspect("auto")
    ax.set_xlabel("x, mm (right-hand side of the machine)", color=muted)
    ax.set_ylabel("y, mm (front to back)", color=muted)
    ax.tick_params(colors=muted)
    for s in ax.spines.values():
        s.set_color(grid)
    ax.grid(color=grid, lw=0.5)
    lm = res["lift"]["empty"]
    g_front = min(r["gap_mm"] for n, r in lm.items() if n.startswith(("F", "open")))
    g_rear = min(r["gap_mm"] for n, r in lm.items() if n.startswith("R"))
    car = max((b for n, b in ext.items() if n.startswith("extractor carriages")), key=lambda b: b[0])
    fd = dock_boxes("F1", 1.0)
    y_dock = max(b[3] for n, b in fd.items() if not n.startswith("hose"))
    ax.annotate("", xy=(1290, car[2]), xytext=(1290, y_dock), arrowprops=dict(arrowstyle="<->", color=ink, lw=1.2))
    ax.text(1080, (car[2] + y_dock) / 2 - 20, f"{g_front:.0f} mm: the extractor to\nthe front-column and bay docks",
            color=ink, fontsize=8.5, va="center", ha="center",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
    rd = dock_boxes("R2", 0.0)
    y_rd = min(b[2] for n, b in rd.items() if not n.startswith("hose"))
    ax.annotate("", xy=(1290, car[3]), xytext=(1290, y_rd), arrowprops=dict(arrowstyle="<->", color=ink, lw=1.2))
    ax.text(1300, (car[3] + y_rd) / 2, f"{g_rear:.0f} mm: to the\nrear-column docks", color=ink, fontsize=8.5,
            va="center")
    sl = min(r["gap_mm"] for r in res["slide"].values())
    pc = res["plate_inserts_to_carriages_mm"]
    ax.text(840, yf - 300, f"tray in F1 (the bay's dock is the same, lower):\nits dock pulled back, the tray "
                           f"slides past\nthe pins' tips {sl:.0f} mm clear", color=ink, fontsize=8.5)
    ax.text(840, 40, f"tray on the extractor (dashed): the plate's\ninserts {pc['now']:.1f} mm from the carriage\n"
                     f"(it was {pc['with_the_face_flush']:.1f} mm with the face flush)", color=ink, fontsize=8.5)
    ax.text(840, yr - 380, "tray in R2, docked", color=ink, fontsize=8.5)
    ax.set_title("Plan of the right-hand side at a slot's height (x stretched): the extractor (red) rides the shaft,\n"
                 "the docks (grey) sit in the columns' side walls; plates dark, their inserts orange",
                 fontsize=9.5, color=ink, loc="left")
    # each case's smallest gap
    bx = fig.add_axes([0.70, 0.16, 0.27, 0.70])
    lift_f = min(r["gap_mm"] for rr in res["lift"].values() for n, r in rr.items() if n.startswith(("F", "open")))
    lift_r = min(r["gap_mm"] for rr in res["lift"].values() for n, r in rr.items() if n.startswith("R"))
    rows = [("lift past the rear-column docks", lift_r, False),
            ("lift past the front-column\nand bay docks", lift_f, False),
            ("bay dock to the shutter", res["bay_dock_to_shutter_mm"], False),
            ("a tray past its own dock,\npulled back (slot or bay)", sl, False),
            ("plate inserts to the\nextractor's carriages", pc["now"], False),
            ("the same, face flush (before)", pc["with_the_face_flush"], True)][::-1]
    vals = [r[1] for r in rows]
    bx.barh(range(len(rows)), vals, color=["#9fb7dc" if r[2] else "#3b6fb6" for r in rows], height=0.6)
    for i, v in enumerate(vals):
        bx.text(v + 8, i, f"{v:.0f} mm" if v >= 10 else f"{v:.1f} mm", va="center", fontsize=8.5, color=ink)
    bx.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=8.5, color=ink)
    bx.set_xlabel("smallest gap, mm", color=muted)
    bx.tick_params(axis="x", colors=muted)
    for sp in ("top", "right"):
        bx.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        bx.spines[sp].set_color(grid)
    bx.set_xlim(0, max(vals) * 1.2)
    bx.set_title("Smallest gap in each case", fontsize=10, color=ink, loc="left")
    fig.text(0.04, 0.012, "Every part as its bounding box, so each gap is a lower bound. The extractor empty and carrying "
                          "each of trays A-F with its instruments, UPS and cameras,\nfrom 300 mm under the lowest slot "
                          "to 300 mm over the highest, docks engaged and pulled back. services.py dock_clearance().",
             fontsize=8, color=muted)
    OUT.mkdir(exist_ok=True)
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def write_json():
    OUT.mkdir(exist_ok=True)
    services = dict(coupling=dict(
        design="one plate per tray at its back right corner, facing out through the right-hand side; an actuated "
               f"dock in the side wall of each slot a tray uses and of the bay; stroke {STROKE:.0f} mm across the "
               "tray's travel; the plate's face 6 mm inside the tray's side",
        plate_mm=dict(along_tray=PLATE_L, height=PLATE_H, centre_from_back=V.TRAY_D / 2 - PLATE_Y),
        media=[dict(key=k, what=lab_, coupling=c) for k, lab_, _, c in MEDIA],
        why_not_the_back_edge="in a front-column slot and at the opening the back edge faces the shaft; a dock there "
                              "would sit in the 106-146 mm between the tray and the extractor's platform, in the path "
                              "of every tray it pulls, and at the opening the shutter is 35 mm behind the tray",
        sequence=["shut and vent air, N2 and water (CombiTac: no mating or parting under pressure)",
                  "UPS takes the load", f"dock pulls back {STROKE:.0f} mm", "extractor moves the tray",
                  "bay dock pushes in, pins first", "contacts mate, supplies open, back on mains"],
        sources={k: SOURCES[k] for k in ("kardex_tray_power", "combitac_align4", "combitac_power", "combitac_data",
                                         "combitac_air", "combitac_fluid", "odu_dock", "harting_dock", "cpc_everis")}),
        cameras=dict(per_tray={k: len(v) for k, v in TRAY_CAMS.items()}, bay=1,
                     unit=dict(models=SOURCES["robot_arms_models"], mount=SOURCES["robot_arms_fixtures"],
                               earlier_unit=SOURCES["lab_units"],
                               adjust=dict(height="block on the post's T-slot, two M5 drop-in T-nuts",
                                           pan="yoke on an M6 bolt through the block's arm, up to 75 deg each way",
                                           tilt=f"head between the yoke's arms, two thumb knobs, 15 deg up to "
                                                f"{TILT_MAX:.0f} down")),
                     clearances=camera_clearances(),
                     bay_camera=dict(bar_y=BAY_CAM["y"], bar_z=BAY_CAM["bar_z"], tilt_axis_y=BAY_CAM["pivot_y"],
                                     tilt_axis_z=BAY_CAM["pivot_z"], tilt_deg=BAY_CAM["tilt"],
                                     arm=bay_arm_clearance()),
                     fov=dict(wide="102 x 67 deg (Camera Module 3 Wide)",
                              hq_16mm="22.2 x 16.7 deg: Raspberry Pi's figure for its 16 mm C-mount lens on the HQ "
                                      "Camera (robot-arms lenses.py)"),
                     bay_view=bay_view(),
                     views=dict(method="the tray presented, the share of each camera's rectilinear picture (Wide 102 x "
                                       "67 deg, HQ with the 16 mm lens 22.2 x 16.7 deg) whose rays leave through the "
                                       "opening into the room before they meet the tray's floor; nothing else counts "
                                       "as cover",
                                units=camera_views())),
        docks_and_lift=dock_clearance(),
        heat=heat_budget())
    (OUT / "services.json").write_text(json.dumps(services, indent=1) + "\n")
    cab = dict(route=dict(ladder_z_mm=LADDER_Z, ladder_y_mm=LADDER_Y, width_mm=LADDER_W, path_xy_mm=LADDER_PATH,
                          note="placements of the ladder, panel, switch and controls are ours"),
               circuits=[dict(key=k, what=w, supply=s, load=l, source=src, kind=kind)
                         for k, w, s, l, src, kind in CIRCUITS])
    (OUT / "cabling.json").write_text(json.dumps(cab, indent=1) + "\n")
    return services, cab


def _main():
    args = sys.argv[1:] or ["services"]
    data = idata = None
    for word in args:
        if word in ("services", "hookups", "baycam", "cabling", "cameras") and data is None:
            import lab
            import tour
            data, idata = lab.meshes(), tour.load()
        if word == "services":
            print(movie_services(data, idata), flush=True)
            _gif("vlm_services")
        elif word == "cabling":
            print(movie_cabling(data, idata), flush=True)
            _gif("vlm_cabling")
        elif word == "cameras":
            print(still_cameras(data, idata), flush=True)
        elif word == "hookups":
            print(movie_hookups(data, idata), flush=True)
            _gif("vlm_hookups")
        elif word == "baycam":
            print(movie_bay_camera(data, idata), flush=True)
            _gif("bay_camera")
        elif word == "clearance":
            res = dock_clearance()
            (OUT / "dock_lift_clearance.json").write_text(json.dumps(res, indent=1) + "\n")
            print(json.dumps(res["smallest"]), res["plate_inserts_to_carriages_mm"], flush=True)
            print(draw_clearance(res), flush=True)
        elif word == "join":
            print(join(), flush=True)
        elif word == "json":
            s, c = write_json()
            for k, t in s["heat"]["trays"].items():
                print(k, t["slot"], t["total_w"], "W", "UPS ok" if t["ups_ok"] else "over the UPS")
            for name, r in s["heat"]["vlm"]["scenarios"].items():
                print(name, r)


JOIN = ["vlm_services", "vlm_hookups", "bay_camera", "vlm_cabling"]     # out/mp4/vlm_services_all.mp4, in order


def join(parts=JOIN, name="vlm_services_all") -> str:
    """The services video: the clips' MP4s end to end. Each is brought to 1280 x 720 at 15 fps first (a clip
    rendered at VIZ3D_FPS=10 joins the others), then the concat demuxer copies them."""
    import subprocess
    import tempfile
    mp4 = OUT / "mp4"
    with tempfile.TemporaryDirectory() as tmp:
        lst = Path(tmp) / "concat.txt"
        lines = []
        for i, part in enumerate(parts):
            src = mp4 / f"{part}.mp4"
            dst = Path(tmp) / f"{i}.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf",
                            "scale=1280:720:flags=lanczos,fps=15", "-an", "-c:v", "libx264", "-preset", "medium", "-crf",
                            "21", "-pix_fmt", "yuv420p", str(dst)], check=True)
            lines.append(f"file '{dst}'")
        lst.write_text("\n".join(lines) + "\n")
        out = mp4 / f"{name}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                        "-movflags", "+faststart", str(out)], check=True)
    return f"{out}: {out.stat().st_size / 1e6:.1f} MB"


def _gif(name):
    from scene import PREVIEW
    if PREVIEW:
        return
    import line
    print(line.mp4_to_gif(OUT / "mp4" / f"{name}.mp4", OUT / f"{name}.gif"), flush=True)


if __name__ == "__main__":
    _main()
