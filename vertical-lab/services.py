"""Tray services for the vertical cloud lab (#303): docking couplers on the trays, the stream cameras, the cabling, and
the utilities and their heat.

    xvfb-run -a python3 services.py services      # the dock close-up            -> out/vlm_services.gif, out/mp4/...
    xvfb-run -a python3 services.py cabling       # the line with its cabling    -> out/vlm_cabling.gif, out/mp4/...
    xvfb-run -a python3 services.py tether        # a tray on a retractable line -> out/vlm_tether.gif, out/mp4/...
    python3 services.py json                      # out/services.json (heat budget), out/cabling.json (circuits)
    xvfb-run -a python3 tour.py tray_dock stream_cam   # the two models on their own -> out/instruments/

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
from common import box, cyl, rbox  # noqa: E402

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
    "lab_units": "DAL PR #189 (atomizer-viewport-cameras): the front unit pairs an HQ Camera (M12) with a 16 mm M12 lens "
                 "(about O16 x 18 mm) and a Camera Module 3 Wide side by side, boards 2 mm apart, HQ lens 15 mm left "
                 "of the axis and the Wide's 18.5 mm right; Pi 5 4 GB with Active Cooler and 27 W PSU; black PETG; "
                 "the top unit rides a 2020 extrusion arm. DAL #147: 1/4-20 insert to a bought arm rather than a "
                 "printed ball joint; cameras within the 200/300/500 mm ribbons of the board.",
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
    "e_spool": "igus e-spool flex 2.0: extension up to 15 m, cables 5-15 mm, spring (SP, SB) or crank; 'No slip ring: "
               "Uninterrupted supply of power, data and air.' igus e-spool power: motor-driven, up to 25 m, 1.2 m/s, "
               "power, data, fibre, air and liquids, no slip ring (igus.com).",
    "spring_reels": "Conductix-Wampfler SR spring reels: up to 56 m horizontal, 34 m lift; power 4G2.5-4G6 "
                    "(conductix.com). Hannay 800 series spring-rewind: 3/4 in x 85 ft hose (retailer listing).",
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
    "xrd": (600.0, "published", "Rigaku MiniFlex 600: '600 W X-ray tube', '1-phase, 100-240 V' (rigaku.com); the "
                                "total draw was not found, so this counts the tube alone"),
    "openflexure_v7": (10.0, "estimate", "a Pi and three small steppers: ours, 10 W"),
    "openflexure_delta": (10.0, "estimate", "the same: ours, 10 W"),
    "pip": (200.0, "estimate", "Plastometrex PLX-Benchtop: no rating found; 200 W is ours"),
    "nanoindenter": (200.0, "estimate", "KLA iMicro: no rating found; 200 W is ours"),
    "mastersizer": (200.0, "snippet", "Malvern Mastersizer 3000+ Ultra: '50 W (no dispersion) up to 200 W' "
                                      "(DirectIndustry, snippet)"),
    "polisher": (740.0, "snippet", "Buehler EcoMet 30: base motor 440 W, semi-automatic head 300 W (distributors' "
                                   "sheets, snippets)"),
    "furnace": (2800.0, "published", "Nabertherm NAT 15/65: connected load 2.8 kW, 1-phase (nabertherm.com)"),
    "pi_unit": (4.0, "published", "Raspberry Pi 5: typical bare-board active current 800 mA at 5 V; the supply is "
                                  "rated 27 W (raspberrypi.com). Cameras add well under 1 W"),
    "ups_loss_frac": (0.03, "estimate", "the UPS's own loss: Eaton publishes none; APC's SMT1500RM2UC is 98.9 % "
                                        "efficient at 50 % load (ENERGY STAR), so 3 % covers charging as well"),
}

TRAY_ITEMS = {      # what's on each tray (animate.LOADS, line.TRAY_LOADS)
    "A": ["cubxl", "ot2"], "B": ["carousel"], "C": ["h2d", "a1mini"],
    "D": ["sem", "xrd", "openflexure_v7", "openflexure_delta"], "E": ["pip", "nanoindenter", "mastersizer"],
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
# never turned, so a side plate meets an identical dock in every slot and in the bay, and the dock's 45 mm stroke is
# across the tray's travel, out of the way of the extractor and the shutter.
PLATE_Y = V.TRAY_D / 2 - 12 - 140      # centre of the plate along the tray's depth (tray frame): 290
PLATE_L = 200.0                        # along y
PLATE_Z0 = V.T_FLOOR + 10.0            # bottom of the plate, over the support it slides on
PLATE_H = 90.0
PLATE_T = 16.0
X_FACE = V.TRAY_W / 2                  # the tray's outer side face: 1225; the mated faces meet here
STROKE = 45.0                          # the dock pulls back this far: 20 mm clear of the tray's side
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


def tray_lines(live_mat=True) -> dict:
    """The tray's lines from the plate inwards, along the back rim (tray frame); coloured when live."""
    p = {}
    for i, ((key, _, mat, _), dy) in enumerate(zip(MEDIA, INSERT_DY)):
        y = PLATE_Y + dy * 0.6
        z = PLATE_Z0 + PLATE_H + 25 + 0  # over the bracket
        x0 = X_FACE - PLATE_T - 60
        x1 = x0 - 120 - 18 * i
        seg = _xc(8, x1, x0, y, z - i * 3)
        p[f"line {key}"] = (seg, mat if live_mat else "svc_plate")
    return p


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
    hx0, hx1 = 1288.0, 1372.0
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
# The lab's own Pi 5 dual-camera design, DAL PR #189's front unit, without its display (no one stands at a tray):
# an HQ Camera (M12) with a 16 mm M12 lens beside a Camera Module 3 Wide, the Pi 5 with its Active Cooler behind them,
# in a black PETG box, on a 2020 extrusion post (the top unit's arm) through a 1/4-20 tilt joint (DAL #147).
CAM = dict(box_w=95.0, box_h=66.0, box_d=46.0, hq_dx=-15.0, wide_dx=18.5, lens_d=16.0, lens_l=18.0, holder=17.0,
           wide_lens_d=9.2, pivot_z=640.0, ext=20.0)


def cam_unit_parts() -> dict:
    """The camera box in its own frame: the tilt axis (x) at the origin, cameras looking along -y."""
    c = CAM
    p = {}
    w, h, d = c["box_w"], c["box_h"], c["box_d"]
    yb = -d / 2                                             # the face the cameras look out of
    body = rbox(w, d, h, 5, z=-h / 2 + 8)                   # box centred a little above the tilt axis
    body = body.cut(box(-w / 2 - 1, -6, -h / 2 + 18, -w / 2 + 1.5, 6, h / 2 - 2))   # vent slots, both ends
    body = body.cut(box(w / 2 - 1.5, -6, -h / 2 + 18, w / 2 + 1, 6, h / 2 - 2))
    p["box"] = (body, "svc_print")
    zc = 8.0 + 4.0
    hq = box(c["hq_dx"] - c["holder"] / 2, yb - 8, zc - c["holder"] / 2, c["hq_dx"] + c["holder"] / 2, yb,
             zc + c["holder"] / 2)
    lens = cq.Workplane("XZ").circle(c["lens_d"] / 2).extrude(c["lens_l"]).translate((c["hq_dx"], yb - 8, zc))
    p["HQ lens"] = (hq.union(lens), "svc_lens")
    p["HQ glass"] = (cq.Workplane("XZ").circle(c["lens_d"] / 2 - 2).extrude(0.6).translate(
        (c["hq_dx"], yb - 8 - c["lens_l"], zc)), "svc_glass")
    wide = box(c["wide_dx"] - 4.25, yb - 6.5, zc - 4.25, c["wide_dx"] + 4.25, yb, zc + 4.25)
    wl = cq.Workplane("XZ").circle(c["wide_lens_d"] / 2).extrude(3.8).translate((c["wide_dx"], yb - 6.5, zc))
    p["Wide lens"] = (wide.union(wl), "svc_lens")
    # the two boards just show at the face's edges, as on the PR's unit (a skirt round each)
    p["boards"] = (box(c["hq_dx"] - 19, yb - 1.4, zc - 19, c["hq_dx"] + 19, yb, zc + 19).union(
        box(c["wide_dx"] - 12.5, yb - 1.1, zc - 14.4 + 4.0, c["wide_dx"] + 12.5, yb, zc + 9.5)), "svc_pcb")
    # tilt cheeks either side and the 1/4-20 boss underneath
    p["tilt cheeks"] = (box(-w / 2 - 6, -12, -h / 2 - 10, -w / 2, 12, 6).union(
        box(w / 2, -12, -h / 2 - 10, w / 2 + 6, 12, 6)), "svc_alu")
    return p


def cam_mast_parts(height: float) -> dict:
    """The post and its foot, in the mast's frame (z = 0 the tray floor or a ceiling bar); height to the tilt axis."""
    e = CAM["ext"]
    p = {}
    post = box(-e / 2, -e / 2, 10, e / 2, e / 2, height - CAM["box_h"] / 2 - 10)
    for s in (-1, 1):       # T-slots
        post = post.cut(box(-3, s * e / 2 - 3 if s < 0 else e / 2 - 3, 10, 3, s * e / 2 + 3 if s < 0 else e / 2 + 3,
                            height))
    p["post"] = (post, "svc_alu")
    p["foot"] = (box(-45, -35, 0, 45, 35, 10), "svc_alu")
    # the yoke from the post to the cheeks
    w = CAM["box_w"]
    p["yoke"] = (box(-w / 2 - 6, -12, height - CAM["box_h"] / 2 - 16, w / 2 + 6, 12, height - CAM["box_h"] / 2 - 10),
                 "svc_alu")
    # the PoE cable down the post
    p["cable"] = (box(e / 2, -3, 10, e / 2 + 6, 3, height - CAM["box_h"] / 2 - 10), "svc_print")
    return p


def stream_cam(pivot_z: float = 260.0) -> Instrument:
    """The unit on a short post for its tour; on a tray the post is taller (TRAY_CAMS)."""
    c = dict(CAM, pivot_z=pivot_z)
    inst = Instrument("stream_cam", "Stream camera unit for a tray", "Raspberry Pi 5, HQ Camera + Camera Module 3 Wide",
                      (c["box_w"] + 12, 70.0, c["pivot_z"] + c["box_h"] / 2 + 8),
                      "the lab's Pi 5 dual-camera unit, DAL PR #189's front unit without its display (Raspberry Pi's "
                      "drawings for the boards, a 16 mm M12 lens), on a 2020 post as its top unit; the post's height "
                      "is ours")
    body = _piece(inst, "body")
    for n, (s, m) in cam_mast_parts(c["pivot_z"]).items():
        body.add(n, s, m)
    head = _piece(inst, "head")
    for n, (s, m) in cam_unit_parts().items():
        head.add(n, _shape(s).moved(cq.Location(cq.Vector(0, 0, c["pivot_z"]))), m)
    inst.joints = {"head": Joint("hinge", axis=(1, 0, 0), pivot=(0, 0, c["pivot_z"]), deg=30.0, v0=0.0)}
    inst.actions = [
        ("A Raspberry Pi 5 with two cameras, as the lab's own units in DAL PR #189: an HQ Camera with a 16 mm M12 "
         "lens beside a Camera Module 3 Wide, the Pi 5 and its Active Cooler behind them in a black PETG box.", 2.6,
         {"head": (0.0, 0.0)}),
        ("It tilts on a 1/4-20 joint at the top of a 2020 post: down onto the instrument it watches.", 1.8,
         {"head": (0.0, 1.0)}),
        ("The Wide sees 102 x 67 degrees; the HQ with its 16 mm lens about 22 x 17 degrees, the detail. One PoE cable "
         "carries power and the stream.", 2.4, {"head": (1.0, 1.0), "~head": (0.0, 0.0)}),
    ]
    zc = c["pivot_z"] + 12
    inst.labels = [("HQ Camera (M12), 16 mm lens", (c["hq_dx"], -c["box_d"] / 2 - 20, zc), (0.16, 0.24)),
                   ("Camera Module 3 Wide", (c["wide_dx"], -c["box_d"] / 2 - 8, zc), (0.84, 0.24)),
                   ("Pi 5 + Active Cooler, black PETG box", (c["box_w"] / 2, 0, zc + 20), (0.84, 0.42)),
                   ("2020 post, 1/4-20 tilt", (0, 0, c["pivot_z"] * 0.55), (0.16, 0.60))]
    inst.cam = (0.9, -1.6, 0.7)
    inst.framing = (0.62, 0.78)
    inst.notes = ["Per-tray cameras: the top of the box stays under Kardex's 727.5 mm product height."]
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
    pan = box(-300, -330, 0, 0, 142, V.T_FLOOR + V.T_RIM)
    pan = pan.cut(box(-301, -331, V.T_FLOOR, -12, 130, V.T_FLOOR + V.T_RIM + 1))
    pan = pan.cut(box(-13, -PLATE_L / 2 - 2, PLATE_Z0 - 2, 1, PLATE_L / 2 + 2, V.T_FLOOR + V.T_RIM + 1))
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
         "pressure), the tray's UPS takes the load, and the dock pulls back 45 mm.", 2.6,
         {"live": (1.0, 0.0), "head": (0.0, 1.0)}),
        ("The extractor pulls the tray out of the slot, across the dock, which is now 20 mm clear.", 2.0,
         {"tray": (0.0, 1.0)}),
        ("At the opening an identical dock waits in the bay's side wall. The tray stops against it ...", 2.0,
         {"tray": (1.0, 0.0)}),
        ("... the guide pins find the plate's bushings (4 mm of misalignment, CombiTac align), the plate is pressed "
         "home, the supplies open: back on mains.", 2.4, {"head": (1.0, 0.0), "live": (0.0, 1.0)}),
    ]
    z = ZC
    inst.labels = [("guide pin", (-24, PIN_DY, z), (0.84, 0.20)),
                   ("mains", (0, INSERT_DY[0], z + 20), (0.16, 0.18)),
                   ("Ethernet", (0, INSERT_DY[1], z + 20), (0.16, 0.28)),
                   ("air", (0, INSERT_DY[2], z), (0.16, 0.38)),
                   ("N2", (0, INSERT_DY[3], z), (0.16, 0.48)),
                   ("water in / out", (0, INSERT_DY[4], z), (0.16, 0.58)),
                   ("dock: actuator in the side wall", (110, -60, PLATE_Z0 + PLATE_H + 25), (0.84, 0.40)),
                   ("service plate on the tray", (-PLATE_T, -PLATE_L / 2, PLATE_Z0 + 5), (0.84, 0.66))]
    inst.cam = (1.0, -1.5, 1.0)
    inst.framing = (0.62, 0.45)
    inst.props = ("live",)
    return inst


# ===================================================================================================== utilities
UPS = dict(w=86.0, d=447.0, h=437.0)        # Eaton 5PX1500RTNG2 standing as a tower: 86 thick (y), 447 deep (x)
UPS_AT = (X_FACE - 165 - UPS["d"] / 2, 276.0 + UPS["w"] / 2)    # tray frame: just ahead of the power strip
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
TRAY_CAMS = {   # per tray: (mast x, mast y, aim x, aim y, aim z) in the tray's frame; the post's foot on the floor
    "A": [(-760.0, 320.0, -150.0, -150.0, 150.0), (420.0, 320.0, 760.0, -60.0, 330.0)],
    "B": [(-560.0, 320.0, -250.0, -372.0, 60.0), (480.0, 320.0, 250.0, -316.0, 300.0)],
    "C": [(-1150.0, -330.0, -560.0, -60.0, 330.0), (380.0, 320.0, 360.0, 0.0, 200.0)],
    "D": [(-1150.0, 320.0, -760.0, -150.0, 300.0), (-300.0, -380.0, 60.0, -230.0, 360.0),
          (560.0, 320.0, 680.0, -150.0, 100.0)],
    "E": [(-1150.0, 320.0, -880.0, 0.0, 420.0), (-570.0, 320.0, -250.0, 0.0, 300.0), (90.0, 320.0, 590.0, 0.0, 300.0)],
    "F": [(-1150.0, 320.0, -500.0, 0.0, 420.0), (-200.0, 320.0, 300.0, -200.0, 300.0)],
}
CAM_PIVOT = 640.0                       # the tilt axis over the tray floor; the box stays under 727.5 mm
BAY_CAM = dict(y=-650.0, bar_z=1735.0, pivot_z=1672.0, tilt=58.0)   # in the bay, at its back, under the header line
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


def _aim(mx, my, t, pivot=CAM_PIVOT):
    """yaw (about z) and tilt (down) that point a unit at (mx, my, pivot) at t: the cameras look along -y."""
    dx, dy, dz = t[0] - mx, t[1] - my, t[2] - (V.T_FLOOR + pivot)
    yaw = math.degrees(math.atan2(dx, -dy))
    tilt = math.degrees(math.atan2(-dz, math.hypot(dx, dy)))
    return yaw, tilt


def add_tray_cameras(sc, tray: str, layout=None, pivot=CAM_PIVOT) -> list:
    """Stream camera units on tray `tray` (they ride with group tray_<k>). layout: [(x, y, aim_x, aim_y, aim_z)] in
    the tray's frame, default TRAY_CAMS[tray]. Returns the groups, one per unit."""
    from scene import R, T
    layout = TRAY_CAMS.get(tray, []) if layout is None else layout
    mast = meshes_of(f"mast{pivot}", lambda: cam_mast_parts(pivot), 0.5)
    unit = meshes_of("unit", cam_unit_parts, 0.3)
    groups = []
    for i, (x, y, ax, ay, az) in enumerate(layout):
        yaw, tilt = _aim(x, y, (ax, ay, az), pivot)
        g, gh = f"cam_{tray}{i}", f"camhead_{tray}{i}"
        add_meshes(sc, g, mast, g)
        add_meshes(sc, gh, unit, gh)
        sc.gmat[g] = T((x, y, V.T_FLOOR)) @ R((0, 0, 1), yaw)
        sc.parent[g] = f"tray_{tray}"
        sc.gmat[gh] = T((0, 0, pivot)) @ R((1, 0, 0), tilt)
        sc.parent[gh] = g
        groups.append(g)
    return groups


def add_bay_camera(sc, x=0.0) -> str:
    """The overhead unit at the bay: on a 2020 bar across the back of the bay, under the header's line, above
    Kardex's product envelope (tray floor + 727.5 + 20 mm), looking down and forward over the presented tray."""
    import pyvista as pv
    from scene import R, T
    b = BAY_CAM
    bar = pv.Box(bounds=(-V.OPEN_W / 2, V.OPEN_W / 2, b["y"] - 10, b["y"] + 10, b["bar_z"] - 10, b["bar_z"] + 10))
    drop = pv.Box(bounds=(x - 10, x + 10, b["y"] - 10, b["y"] + 10, b["pivot_z"] + 30, b["bar_z"] - 10))
    M = mats()
    sc.add("baycam/bar", bar.merge(drop).triangulate(), M["svc_alu"][:3], "baycam", specular=0.6)
    unit = meshes_of("unit", cam_unit_parts, 0.3)
    add_meshes(sc, "baycamhead", unit, "baycamhead")
    sc.gmat["baycam"] = np.eye(4)
    sc.gmat["baycamhead"] = T((x, b["y"], b["pivot_z"])) @ R((1, 0, 0), b["tilt"])
    return "baycamhead"


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
    riser = meshes_of("riser", riser_parts, 2.0)
    for yc, name in ((V.Y_FRONT, "front"), (V.Y_REAR, "rear")):
        add_meshes(sc, f"riser_{name}", riser, f"riser_{name}")
        sc.gmat[f"riser_{name}"] = T((0, yc, 0))
    return out


def set_dock(sc, pos, u):
    """u = 0 engaged, 1 pulled back."""
    from scene import T
    sc.gmat[f"dockhead_{pos}"] = T((STROKE * u, 0, 0))


def add_tray_services(sc, tray: str, ups=True) -> list:
    """The tray's plate, its lines (coloured when live) and its UPS, riding with group tray_<k>."""
    add_meshes(sc, f"plate_{tray}", meshes_of("plate", plate_parts, 0.4), f"tray_{tray}")
    names = add_meshes(sc, f"lines_{tray}", meshes_of("lines", tray_lines, 0.5), f"tray_{tray}")
    if ups:
        add_meshes(sc, f"ups_{tray}", meshes_of("ups", ups_parts, 1.0), f"tray_{tray}")
    return names


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


def build_vlm(name, data, idata, title, docks=True, cams=True):
    """The VLM with trays A-F and their equipment (as line.py has them, without the floor line), the docks, plates,
    UPSs and cameras. Returns (scene, lab, {tray: [line actor names]})."""
    import line
    import tour
    from scene import Scene, T
    sc = Scene(name, title, gif=False)
    L = make_lab(sc, data)
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
CAM_S_CAMS = [(2400, -4300, 2500), (0, -1050, 1200), (0, 0, 1)]


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
            "pressure), the tray's UPS takes the load, and the dock pulls back 45 mm, 20 mm clear of the tray.", 2.8,
            release, hold=1.2, labels=[("UPS takes over", (UPS_AT[0], yc + UPS_AT[1], zs + UPS["h"]), (0.84, 0.55)),
                                       ("dock pulled back 45 mm", (1290, wy, wz), (0.84, 0.30))])
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
    cam_lbl = [(f"stream camera on tray {k}", A.tray_world(k, (x, y, V.T_FLOOR + CAM_PIVOT + 40)),
                (0.14 if x < 0 else 0.86, 0.30)) for (x, y, *_r) in TRAY_CAMS[k]]
    sc.step(f"6/{n}", "The cameras: two Pi 5 units on tray A, on 2020 posts under the 727.5 mm product height, and an "
            "overhead one at the back of the bay, above Kardex's product envelope, looking down on the presented "
            "tray.", 3.2, None, hold=2.6, cam_to=CAM_S_CAMS, still=True,
            labels=cam_lbl + [("overhead camera at the bay", (0, BAY_CAM["y"], BAY_CAM["pivot_z"]), (0.60, 0.13))])
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


# ----------------------------------------------------------------------------------------------- the tether
TETHER_X = V.TRAY_W / 2 + 15.0          # the line runs in the 30 mm between the tray's side (1225) and the rails (1255)
TETHER_ATTACH = (TETHER_X, V.TRAY_D / 2 - 20, 60.0)     # on the tray's back right corner, tray frame


def movie_tether(data, idata):
    """Tray A on a retractable line from an e-spool on the rear wall, from R2 to the opening."""
    import pyvista as pv
    k = "A"
    slot = HOME[k]
    sc, L, _ = build_vlm("vlm_tether", data, idata, "Vertical cloud lab: a tray on a retractable line", docks=False,
                         cams=False)
    L.skin(1.0)(1.0)
    hide(sc, ("skin_R",))
    M = mats()
    ys, zs = V.SLOTS[slot]
    spool = np.array([TETHER_X, V.UNIT_D / 2 - 60, zs + TETHER_ATTACH[2]])
    drum = pv.Cylinder(center=(TETHER_X + 10, spool[1] + 20, spool[2] + 120), direction=(1, 0, 0), radius=150,
                       height=70).triangulate()
    sc.add("tether/spool", drum, M["svc_chain"][:3], "tether", specular=0.4)

    def attach():
        y, z = L.tray[k]
        return np.array([TETHER_ATTACH[0], y + TETHER_ATTACH[1], z + TETHER_ATTACH[2]])

    sc.add("tether/line", _tube([spool, attach()], 9), M["svc_power"][:3], "tether")
    state = {"bad": False}

    def redraw():
        a = attach()
        sc.set_mesh("tether/line", _tube([spool, a], 9))
        sc.color["tether/line"] = (0.9, 0.1, 0.1) if state["bad"] else M["svc_power"][:3]
        pay = float(np.linalg.norm(a - spool))
        L.svc_lines = [(f"Tray {k}", "on its line: mains, the whole way"), ("Payout", f"{pay / 1000:.2f} m"),
                       ("Extractor", state.get("ext", "free"))]
        L.gauges()

    def wrap(f):
        def up(u):
            f(u)
            redraw()
        return up
    redraw()
    cam = [(4300, 900, 2300), (700, 0, 1050), (0, 0, 1)]
    n = 5
    sc.step(f"1/{n}", "The other way: no plug at all. Tray A's line runs from an e-spool on the rear wall (igus: power, "
            "data and air on one spool, no slip ring, up to 15 m), along the 30 mm between the tray's side and the "
            "extractor's guide rails.", 3.2, None, hold=1.4, cam_to=cam,
            labels=[("e-spool (marker, not to size)", tuple(spool + (0, 20, 120)), (0.80, 0.20)),
                    ("the line", tuple((spool + attach()) / 2), (0.80, 0.40))])
    sc.step(f"2/{n}", "Out of the slot: the line pays out as the extractor pulls the tray.", 0.6 + abs(L.lift_z - zs)
            / 1333, wrap(L.lift_to(zs)), hold=0.1)
    sc.step(f"2/{n}", "Out of the slot: the line pays out as the extractor pulls the tray.", 2.2, wrap(L.slide(k, 0.0)),
            hold=0.2)
    yt, zt = V.SLOTS["open"]
    pay = tether_payout()["rows"]
    cap3 = (f"Down {abs(zs - zt):.0f} mm and through the shutter to the opening: {pay[k]['payout_mm'] / 1000:.1f} m of "
            "line from R2. The shutter needs a notch at its right-hand end for it.")
    sc.step(f"3/{n}", cap3, max(0.6, abs(zs - zt) / 1333), wrap(L.lift_to(zt, carry=k)),
            hold=0.1)
    sc.step(f"3/{n}", cap3, 0.6, wrap(L.shut(1.0)), hold=0.0)
    sc.step(f"3/{n}", cap3, 2.2, wrap(L.slide(k, yt)), hold=0.0)
    sc.step(f"3/{n}", cap3, 0.6, wrap(L.shut(0.0)), hold=1.0)
    L.where[k] = "open"
    state["bad"], state["ext"] = True, "blocked: the line spans the shaft"
    redraw()
    sc.step(f"4/{n}", "The catch: while tray A is out, its line spans the shaft at the extractor's height, so the "
            "extractor can't move to fetch any other tray until tray A goes home.", 2.4, None, hold=2.0,
            cam_to=[(3600, -2600, 2600), (600, 0, 1000), (0, 0, 1)],
            labels=[("the line across the shaft", tuple((spool + attach()) / 2), (0.80, 0.30))])
    sc.step(f"5/{n}", "So a tether suits one tray, stored at the opening's own height so it never moves up or down. "
            f"From the top slot here (R4, 2700 mm) it would need {pay['E']['payout_mm'] / 1000:.1f} m and cross the "
            "shaft on the slant.", 3.0,
            None, hold=2.6, still=True)
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
                     transit_s="about 6 s from R2 to the opening; under 15 s from any slot at Kardex's speeds",
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
            "the column wall and the cladding (taken here as about 105 mm).",
            "Whether power to a slot can stay on while a tray is stored, and what they would fit (the dealer offered "
            "a quick-connect cord).",
        ],
    )


def tether_payout() -> dict:
    """How much line a tray on a tether needs: from a spool on the wall behind its slot (the rear wall for a rear slot,
    the front wall for a front one), at the slot's height, to the tray's back right corner, wherever the tray goes on its
    way to the opening (in the slot, on the extractor at the slot's height and at the opening's, presented)."""
    rows = {}
    for k, slot in HOME.items():
        ys, zs = V.SLOTS[slot]
        sy = math.copysign(V.UNIT_D / 2 - 60, ys)
        spool = np.array([sy, zs + TETHER_ATTACH[2]])
        pts = [(ys, zs), (0.0, zs), (0.0, V.Z_OPEN), (V.Y_OPEN, V.Z_OPEN)]
        d = [float(np.linalg.norm(np.array([y + TETHER_ATTACH[1], z + TETHER_ATTACH[2]]) - spool)) for y, z in pts]
        rows[k] = dict(slot=slot, column="rear" if ys > 0 else "front", vertical_mm=round(abs(zs - V.Z_OPEN)),
                       payout_mm=round(max(d)))
    return dict(rows=rows, note="The line has to stay in the 30 mm between the tray's side and the extractor's guide "
                                "rails, the shutter needs a notch for it, and while the tray is out the line spans the "
                                "shaft, so the extractor can't fetch any other tray. It suits one tray stored at the "
                                "opening's own height.",
                source=SOURCES["e_spool"])


def bay_view() -> dict:
    """What the bay camera covers on the presented tray: distance along its axis to the tray floor, and the width the
    Wide's 102 deg and the HQ's 22 deg span there."""
    b = BAY_CAM
    t = math.radians(b["tilt"])
    floor = V.Z_OPEN + V.T_FLOOR
    dist = (b["pivot_z"] - floor) / math.sin(t)
    hit_y = b["y"] - dist * math.cos(t)
    return dict(axis_hits_tray_at_y=round(hit_y), distance_mm=round(dist),
                wide_width_mm=round(2 * dist * math.tan(math.radians(51))),
                hq_width_mm=round(2 * dist * math.tan(math.atan(6.287 / 32))),
                tray_y_range=[V.Y_OPEN - V.TRAY_D / 2, V.Y_OPEN + V.TRAY_D / 2])


def camera_clearances() -> dict:
    """The top of every tray unit over the tray floor (against Kardex's 727.5 mm), and the bay unit's lowest point
    against the top of the product envelope at the opening (tray floor + 727.5 + 20 mm), from the meshes."""
    from scene import R, T
    pts = np.vstack([m.points for m in meshes_of("unit", cam_unit_parts, 0.3).values() if m.n_points])
    h = np.c_[pts, np.ones(len(pts))]
    tops = {}
    for k, layout in TRAY_CAMS.items():
        for i, (x, y, ax, ay, az) in enumerate(layout):
            yaw, tilt = _aim(x, y, (ax, ay, az))
            m = T((x, y, V.T_FLOOR)) @ R((0, 0, 1), yaw) @ T((0, 0, CAM_PIVOT)) @ R((1, 0, 0), tilt)
            tops[f"{k}{i}"] = dict(top_over_floor_mm=round(float((h @ m.T)[:, 2].max()) - V.T_FLOOR, 1),
                                   yaw_deg=round(yaw, 1), tilt_down_deg=round(tilt, 1))
    b = BAY_CAM
    m = T((0, b["y"], b["pivot_z"])) @ R((1, 0, 0), b["tilt"])
    low = float((h @ m.T)[:, 2].min())
    env = V.Z_OPEN + V.T_FLOOR + V.MAX_GOODS_H + V.GOODS_CLEAR
    return dict(tray_units=tops, limit_mm=V.MAX_GOODS_H, bay_lowest_mm=round(low, 1), envelope_top_mm=env,
                bay_margin_mm=round(low - env, 1))


def write_json():
    OUT.mkdir(exist_ok=True)
    services = dict(coupling=dict(
        design="one plate per tray at its back right corner, facing out through the right-hand side; an actuated "
               "dock in the side wall of each slot a tray uses and of the bay; stroke 45 mm across the tray's travel",
        plate_mm=dict(along_tray=PLATE_L, height=PLATE_H, centre_from_back=V.TRAY_D / 2 - PLATE_Y),
        media=[dict(key=k, what=lab_, coupling=c) for k, lab_, _, c in MEDIA],
        why_not_the_back_edge="in a front-column slot and at the opening the back edge faces the shaft; a dock there "
                              "would sit in the 106-146 mm between the tray and the extractor's platform, in the path "
                              "of every tray it pulls, and at the opening the shutter is 35 mm behind the tray",
        sequence=["shut and vent air, N2 and water (CombiTac: no mating or parting under pressure)",
                  "UPS takes the load", "dock pulls back 45 mm", "extractor moves the tray",
                  "bay dock pushes in, pins first", "contacts mate, supplies open, back on mains"],
        sources={k: SOURCES[k] for k in ("kardex_tray_power", "combitac_align4", "combitac_power", "combitac_data",
                                         "combitac_air", "combitac_fluid", "odu_dock", "harting_dock", "cpc_everis")}),
        cameras=dict(per_tray={k: len(v) for k, v in TRAY_CAMS.items()}, bay=1, unit=SOURCES["lab_units"],
                     clearances=camera_clearances(),
                     bay_camera=dict(y=BAY_CAM["y"], pivot_z=BAY_CAM["pivot_z"], tilt_deg=BAY_CAM["tilt"]),
                     fov=dict(wide="102 x 67 deg (Camera Module 3 Wide)",
                              hq_16mm="about 22 x 17 deg: the IMX477's 6.29 x 4.71 mm active area behind a 16 mm "
                                      "lens (2 atan(w / 2f)); ours, from the published sensor"),
                     bay_view=bay_view()),
        heat=heat_budget(), tether=tether_payout())
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
        if word in ("services", "cabling", "tether") and data is None:
            import lab
            import tour
            data, idata = lab.meshes(), tour.load()
        if word == "services":
            print(movie_services(data, idata), flush=True)
            _gif("vlm_services")
        elif word == "cabling":
            print(movie_cabling(data, idata), flush=True)
            _gif("vlm_cabling")
        elif word == "tether":
            print(movie_tether(data, idata), flush=True)
            _gif("vlm_tether")
        elif word == "json":
            s, c = write_json()
            for k, t in s["heat"]["trays"].items():
                print(k, t["slot"], t["total_w"], "W", "UPS ok" if t["ups_ok"] else "over the UPS")
            for name, r in s["heat"]["vlm"]["scenarios"].items():
                print(name, r)
            print(json.dumps(s["tether"]["rows"]))


def _gif(name):
    from scene import PREVIEW
    if PREVIEW:
        return
    import line
    print(line.mp4_to_gif(OUT / "mp4" / f"{name}.mp4", OUT / f"{name}.gif"), flush=True)


if __name__ == "__main__":
    _main()
