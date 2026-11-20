"""An ICP-MS station on the floor, its acids in a fume hood of their own (round 13, run D; PR #318, #303).

    xvfb-run -a python3 icpms.py              # the clip -> out/mp4/icpms.mp4, out/icpms.gif, out/icpms.json,
                                              #    out/icpms_still.png, out/icpms_bom.json
    PREVIEW=1 xvfb-run -a python3 icpms.py    # the last frame of each sub-step only, to /tmp
    ARM_AUDIT=1 xvfb-run -a python3 icpms.py  # no render: the arm checked every frame -> out/collisions/icpms.json
    python3 icpms.py bom                      # out/icpms_bom.json only

Sterling on PR #318 (2026-11-20): "Do we have ICP-MS as a module? If not, we should. Also, an OT-2 probably doesn't
have great compatibility with many of the solvents that would be required for ICP-MS and ICP-OES. And it would be very
risky to try to put high-hazard chemicals on a tray. This would be better for a standalone fumehood, and probably with
a liquid handler that's designed for those kinds of harsh solvents (maybe Hamilton? Really expensive, but we need good
chemical compatibility..). On a similar note, we might need a similar kind of sleeve or protection for the UR arms."

What it is (notes/icpms.md has every figure with its source):

* **The hood**: a metal-free polypropylene trace-metals hood, HEMCO UniFlow 6 ft (72 x 32 x 59 in, four horizontal
  sliding sashes on two tracks, so at most half open), on a ventilated acid-storage base cabinet. The concentrated acids
  (HNO3, HCl; no HF anywhere) live only here, in PFA bottles in a PP tray.
* **Inside it**: a graphite hot block (DigiPREP class) that digests a build's chips or powder in HNO3 + HCl, and an
  acid-rated dilutor with an all-fluoropolymer fluid path (Questron/HORIBA QPrep class): a PFA probe, syringe pumps,
  and a decapping head (ours). Hamilton's own resistance table rates the STAR's CO-RE pipetting head "not recommended"
  for nitric acid at 5-10 % and at 70 %, and a STARlet is 1124 x 795 x 903 mm: no room in a hood, so not a Hamilton.
* **Beside it, on a bench**: an Agilent 7850 ICP-MS (730 x 600 x 595 mm, 100 kg; ultra-high-matrix aerosol dilution
  standard, for samples up to 25 % dissolved solids, which the seawater electrolyte needs) with its SPS 4 autosampler
  under a vented cover; under the bench its chiller and forepump; beside it a 180 L liquid argon dewar. Its exhaust has
  a duct of its own, not the hood's.
* **The arm** works it from its MiR250 in a PTFE-laminate cover (Roboworld Robosuit class), and carries only capped
  sample tubes in and an autosampler rack of dilute (2 %) acid out: never an open concentrated acid.

Frame: x to the right along the station, y away from you (the wall at the back), z up, mm, the origin on the floor at
the middle of the station. The racks, the decapper, the transfer positions, the SPS 4 door's actuator, the arm's
carrier and the layout are our designs; sizes marked "estimate" in SOURCES are read off photos.
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import cadquery as cq
import numpy as np

import instruments as I
from instruments import Instrument, Joint, _piece, _ycyl

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
sys.path.insert(0, str(HERE / "lab_models"))
from common import box, cyl, hose, rbox, tube  # noqa: E402

# ===================================================================================================== sizes
HOOD = dict(W=1829.0, D=813.0, H=1499.0, cab=900.0, top=32.0, post=100.0, sill=38.0, sash_top=1890.0, collar=254.0)
BENCH = dict(W=1800.0, D=760.0, H=900.0, gap=100.0)
ICP = dict(W=730.0, D=600.0, H=595.0, mass=100.0)            # Agilent 7800/7850/7900 site prep (G8400-90020)
SPS = dict(W=600.0, D=363.0, H=510.0, mass=15.0)             # Agilent SPS 4 (same checklist)
CHILLER = dict(W=368.0, D=702.0, H=576.0, mass=85.0)         # Agilent G3292A recirculating chiller
PUMP = dict(W=164.0, D=541.0, H=242.0, mass=35.0)            # DS402 forepump (the 7800's; the 7850's not confirmed)
DEWAR = dict(d=508.0, H=1635.0, gap=60.0)                    # 180 L liquid argon, 22 psi (Airgas)
TOTAL_W = HOOD["W"] + BENCH["gap"] + BENCH["W"] + DEWAR["gap"] + DEWAR["d"]
X0 = -TOTAL_W / 2                                            # the hood's left edge
HX0, HX1 = X0, X0 + HOOD["W"]
BX0 = HX1 + BENCH["gap"]
BX1 = BX0 + BENCH["W"]
YB = HOOD["D"] / 2                                           # the wall: every back is at y = YB
HYF = -HOOD["D"] / 2                                         # the hood's front
BYF = YB - BENCH["D"]                                        # the bench's front
WS = HOOD["cab"] + HOOD["top"]                               # the hood's work surface, 932
HTOP = WS + HOOD["H"]                                        # the hood's top, 2431
POST = HOOD["post"]
XI0, XI1 = HX0 + POST, HX1 - POST                            # inside the side posts
PANEL = (XI1 - XI0) / 4                                      # four sliding sash panels, 407 mm
OPEN_X = (XI0 + 2 * PANEL, XI1)                              # the right half, open: panels 2-4 slid left
DEWAR_XY = (BX1 + DEWAR["gap"] + DEWAR["d"] / 2, YB - DEWAR["d"] / 2 - 30.0)

# the racks (ours): 15 mL PP tubes, 17 x 118 mm (+ 12 mm cap), 4 columns x 6 rows; a central handle for the 2F-85
RACK = dict(W=190.0, D=176.0, H=60.0, floor=8.0, cols=(-75.0, -50.0, 50.0, 75.0), rows=6, pitch=26.0,
            tube_d=17.0, tube_h=118.0, cap_d=20.0, cap_h=12.0, handle=(16.0, 110.0, 178.0))
# where they stand (rack centres, on the dilutor's deck and the SPS 4's)
DIL = dict(x0=-1290.0, x1=-450.0, y0=-260.0, y1=290.0, deck=40.0)       # the dilutor's frame, over the work surface
RACK_IN = (-600.0, -110.0, WS + DIL["deck"])                             # capped samples, set by the arm
RACK_OUT = (-850.0, -110.0, WS + DIL["deck"])                            # the SPS 4 rack the dilutor fills
GZ = WS + 600.0                                                          # the dilutor's head: its column's foot
HEAD_PARK = (-860.0, 150.0)                                              # the head parked behind the racks
PROBE_DX = 34.0                                                          # the probe beside the decapping chuck, in x
TUBE_TOP = RACK_IN[2] + RACK["floor"] + RACK["tube_h"]                   # a tube's rim, 1098; its cap's top 1110
PROBE_TIP = TUBE_TOP + RACK["cap_h"] + 25.0                              # the probe's tip at rest, over the caps
CHUCK_BOT = TUBE_TOP + RACK["cap_h"] + 30.0                              # the chuck's jaws at rest
SPS_X = BX0 + 80.0 + SPS["W"] / 2                                        # the SPS 4's centre
SPS_RACK = (SPS_X - 120.0, BYF + 60.0 + SPS["D"] / 2 - 20.0, BENCH["H"] + 45.0)
ICP_X = SPS_X + SPS["W"] / 2 + 60.0 + ICP["W"] / 2
SPS_TUBE_TOP = SPS_RACK[2] + RACK["floor"] + RACK["tube_h"]
SPS_TIP = SPS_TUBE_TOP + 22.0                                            # the SPS 4 probe's tip at rest
SPS_PARK = (SPS_RACK[0] + 200.0, SPS_RACK[1] - (RACK["rows"] - 1) / 2 * RACK["pitch"])   # over its standards

FOOTPRINTS = {
    "icpms": (TOTAL_W, HOOD["D"], HTOP, 520.0,
              "ICP-MS station (ours): HEMCO UniFlow 6 ft polypropylene trace-metals hood on an acid cabinet, with a "
              "digestion hot block and an acid-rated dilutor inside; Agilent 7850 ICP-MS + SPS 4 on a bench; chiller, "
              "forepump, 180 L argon dewar. Mass: the instruments' (100 + 15 + 85 + 35 kg) plus estimates",
              "https://www.agilent.com/en/product/atomic-spectroscopy/inductively-coupled-plasma-mass-spectrometry-"
              "icp-ms/icp-ms-instruments/7850-icp-ms", "floor"),
}

SOURCES = {   # notes/icpms.md has each with its provenance (maker, third party, estimate)
    "ICP-MS": "Agilent 7800/7900 site preparation checklist G8400-90020 (2016; the 2024 edition lists the 7850 at the "
              "same 730 x 600 x 595 mm, 100 kg): 200-240 V single phase on a 30 A circuit, argon 20 L/min at 500-700 kPa, "
              "one 150 mm exhaust at 5-7 m3/min, chiller G3292A (368 x 702 x 576 mm, 85 kg, 2900 W); SPS 4 600 x 363 x "
              "510 mm, 15 kg, its cover extracting 50-100 L/min through a 50 mm port when corrosive liquids are loaded",
    "UHMI": "Agilent 7850 page and app note 5994-4467EN: UHMI aerosol dilution is standard and takes samples 'up to 25% "
            "total dissolved solids'; undiluted seawater 'can be measured directly'",
    "price": "Agilent quotes in a 2017 West Virginia bid file: a 7800 system $215,975 list, $122,526 net; a 7900 with "
             "UHMI $162,005 net; SPS 4 $12,305 list. LabX's 2026 buyer's guide: a 7850 $160-220k",
    "hood": "HEMCO UniFlow Trace Metals hood (LabWrench listing; HEMCO's literature): one-piece welded polypropylene "
            "chamber and baffle, 6 ft = 72 x 32 x 59 in, four horizontal sliding sashes on two tracks (at most half "
            "open), 100 fpm face velocity. Base cabinet and work surface heights estimated",
    "dilutor": "Questron (HORIBA) QPrep: 'all-plastic construction', 'Teflon-coated rigid graphite probe', dilutes, "
               "spikes internal standard, fills racks, 6 autosampler racks; size not published (ours, estimated). "
               "Hamilton Microlab STAR line operator's manual: the CO-RE head is rated 3, not for continuous contact, "
               "with 5-10 % and 70 % nitric acid; STARlet 1124 x 795 x 903 mm, 135 kg. Gilson GX-271 manual: avoid "
               "nitric acid over 10 % on PEEK. Opentrons OT-2 and Flex manuals: 'Keep corrosive materials ... away "
               "from the robot'",
    "hot block": "SCP Science DigiPREP: graphite hot block, up to 450 C, 50 mL tubes; size estimated",
    "argon": "Airgas 180 L liquid argon, 22 psi: about 143 m3 of gas, 508 mm diameter, 1635 mm tall; at 20 L/min about "
             "119 h of plasma, three weeks of 8 h days less boil-off (PerkinElmer: expect a new dewar every 2-3 weeks)",
    "cover": "Roboworld Robosuit for UR3-UR12e (UR+ listing): over 18 fabrics, a 10-mil laminated Teflon option for "
             "'caustic chemical environments', zips or hook-and-loop, quote only; no maker publishes an IP rating. "
             "UR: the UR12e (the renamed UR10e) is IP54, and where liquids are present 'additional measures should be "
             "taken, such as utilizing a protective robot cover'",
}

MATERIALS = {
    "icp_pp": (0.93, 0.93, 0.90, 1.0, 0.15),          # white polypropylene (hood, cabinet, dilutor frame)
    "icp_pp_grey": (0.70, 0.71, 0.70, 1.0, 0.15),     # grey PP work surface and trays
    "icp_sash": (0.80, 0.88, 0.92, 0.22, 0.9),        # clear PVC/polycarbonate sash
    "icp_agilent": (0.92, 0.93, 0.94, 1.0, 0.25),     # the 7850's white
    "icp_agilent_dk": (0.30, 0.33, 0.38, 1.0, 0.3),   # its dark trim
    "icp_agilent_blue": (0.13, 0.36, 0.62, 1.0, 0.3),
    "icp_cover": (0.82, 0.88, 0.92, 0.25, 0.9),       # the SPS 4's clear cover
    "icp_pfa": (0.94, 0.95, 0.96, 0.55, 0.5),         # translucent PFA bottles and lines
    "icp_graphite": (0.18, 0.18, 0.19, 1.0, 0.35),
    "icp_tube": (0.95, 0.95, 0.93, 0.50, 0.5),        # PP sample tubes
    "icp_cap_in": (0.15, 0.42, 0.82, 1.0, 0.3),       # blue caps: the corrosion samples
    "icp_liquid": (0.78, 0.86, 0.92, 0.55, 0.6),
    "icp_acid_label": (0.98, 0.84, 0.15, 1.0, 0.1),   # yellow corrosive labels
    "icp_dewar": (0.75, 0.76, 0.78, 1.0, 0.7),
    "icp_duct": (0.80, 0.81, 0.82, 1.0, 0.4),
    "icp_sleeve": (0.95, 0.95, 0.93, 1.0, 0.08),      # the arm's PTFE-laminate cover
}
MATERIALS_ALL = dict(I.MATERIALS, **MATERIALS)


# ===================================================================================================== the racks
def rack_parts(capped: bool):
    """{name: (shape, material)} of one rack with its 24 tubes, its base centre at the origin. capped: the corrosion
    samples (blue screw caps); else open SPS 4 tubes."""
    r = RACK
    W, D, H = r["W"], r["D"], r["H"]
    xs = r["cols"]
    ys = [(-(r["rows"] - 1) / 2 + k) * r["pitch"] for k in range(r["rows"])]
    body = box(-W / 2, -D / 2, 0, W / 2, D / 2, H)
    holes = None
    for x in xs:
        for y in ys:
            c = cyl(r["tube_d"] + 1.0, H, x=x, y=y, z=r["floor"])
            holes = c if holes is None else holes.union(c)
    body = body.cut(holes)
    hw, hl, hh = r["handle"]
    body = body.union(box(-hw / 2, -hl / 2, H, hw / 2, hl / 2, hh))
    body = body.union(box(-hw / 2 - 10, -hl / 2, hh - 22, hw / 2 + 10, hl / 2, hh))    # a T top: the pads' seat
    tubes = liquid = caps = None
    for x in xs:
        for y in ys:
            t = tube(r["tube_d"], r["tube_d"] - 1.6, r["tube_h"], x=x, y=y, z=r["floor"]).union(
                cyl(r["tube_d"], 1.0, x=x, y=y, z=r["floor"]))
            tubes = t if tubes is None else tubes.union(t)
            lq = cyl(r["tube_d"] - 1.8, 70.0 if capped else 0.5, x=x, y=y, z=r["floor"] + 1.0)
            liquid = lq if liquid is None else liquid.union(lq)
            if capped:
                c = cyl(r["cap_d"], r["cap_h"], x=x, y=y, z=r["floor"] + r["tube_h"])
                caps = c if caps is None else caps.union(c)
    out = {"rack": (body, "icp_pp_grey"), "tubes": (tubes, "icp_tube"), "liquid": (liquid, "icp_liquid")}
    if caps is not None:
        out["caps"] = (caps, "icp_cap_in")
    return out


def tube_xy(i: int) -> tuple[float, float]:
    """Tube i's (x, y) in its rack: column-major from the rack's front left."""
    r = RACK
    ys = [(-(r["rows"] - 1) / 2 + k) * r["pitch"] for k in range(r["rows"])]
    return r["cols"][i // r["rows"]], ys[i % r["rows"]]


# ===================================================================================================== the station
def station() -> Instrument:
    p = HOOD
    inst = Instrument("icpms", "ICP-MS station, its acids in a fume hood", "Agilent 7850 + SPS 4; HEMCO UniFlow 6 ft",
                      (TOTAL_W, p["D"], HTOP), "Agilent's site prep (7850, SPS 4, chiller); HEMCO's UniFlow trace-"
                      "metals hood; Questron QPrep class dilutor; layout and fixtures ours (notes/icpms.md)", floor=True)
    body = _piece(inst, "body")
    # ---------------------------------------------------------------- the hood on its acid cabinet
    body.add("acid cabinet", box(HX0, HYF + 40, 0, HX1, YB, p["cab"]), "icp_pp")
    for k, (a, b) in enumerate(((HX0 + 15, HX0 + p["W"] / 2 - 5), (HX0 + p["W"] / 2 + 5, HX1 - 15))):
        body.add(f"cabinet door {k}", box(a, HYF + 37, 60, b, HYF + 40, p["cab"] - 40), "icp_pp_grey")
        body.add(f"cabinet handle {k}", box((a + b) / 2 - 50, HYF + 28, p["cab"] - 120, (a + b) / 2 + 50, HYF + 37,
                                            p["cab"] - 105), "inst_dark")
    body.add("cabinet label", box(HX0 + 60, HYF + 36, 700, HX0 + 300, HYF + 37, 780), "icp_acid_label")
    body.add("cabinet vent", hose([(HX0 + 120, YB - 60, p["cab"]), (HX0 + 120, YB - 60, HTOP - 160)], 50.0), "icp_pp")
    body.add("work surface", box(HX0, HYF, p["cab"], HX1, YB, WS), "icp_pp_grey")
    for sx, (a, b) in (("left", (HX0, XI0)), ("right", (XI1, HX1))):
        body.add(f"post {sx}", box(a, HYF, WS, b, YB, HTOP - 200), "icp_pp")
    body.add("hood top", box(HX0, HYF, HTOP - 200, HX1, YB, HTOP), "icp_pp")
    body.add("back", box(XI0, YB - 30, WS, XI1, YB, HTOP - 200), "icp_pp")
    body.add("baffle", box(XI0, YB - 80, WS + 40, XI1, YB - 68, HTOP - 260), "icp_pp")
    for k, zz in enumerate((WS + 70, WS + 640, HTOP - 320)):
        body.add(f"baffle slot {k}", box(XI0 + 50, YB - 81, zz, XI1 - 50, YB - 79.5, zz + 28), "inst_dark")
    body.add("fascia", box(XI0, HYF, p["sash_top"], XI1, HYF + 60, HTOP - 200), "icp_pp")
    body.add("fascia band", box(XI0, HYF - 1, HTOP - 190, XI1, HYF, HTOP - 165), "inst_blue")
    body.add("sill", box(XI0, HYF, WS, XI1, HYF + 60, WS + p["sill"]), "icp_pp")
    body.add("sash track", box(XI0, HYF + 2, p["sash_top"] - 12, XI1, HYF + 58, p["sash_top"]), "icp_pp_grey")
    body.add("light", box(XI0 + 200, -200, HTOP - 201, XI1 - 200, 200, HTOP - 200), "icp_pp")
    body.add("collar", cyl(p["collar"], 120, x=(HX0 + HX1) / 2, y=60, z=HTOP), "icp_pp")
    body.add("hood duct", cyl(p["collar"] - 20, 300, x=(HX0 + HX1) / 2, y=60, z=HTOP + 120), "icp_duct")
    body.add("airflow monitor", box(XI1 + 20, HYF - 1, 1700, XI1 + 80, HYF, 1760), "screen_on")
    # the sashes: four panels on two tracks (front 1 and 3, back 2 and 4); 2, 3 and 4 slide left to open the right half
    for k in range(4):
        yk = HYF + (14 if k % 2 == 0 else 36)
        x0, x1 = XI0 + k * PANEL - (0 if k == 0 else 8), XI0 + (k + 1) * PANEL + (0 if k == 3 else 8)
        pc = body if k == 0 else _piece(inst, f"sash{k}")
        pc.add(f"sash {k} glass", box(x0, yk, WS + p["sill"] + 4, x1, yk + 8, p["sash_top"] - 14), "icp_sash")
        pc.add(f"sash {k} frame", box(x0, yk - 2, WS + p["sill"] + 4, x1, yk + 10, WS + p["sill"] + 34), "icp_pp")
        pc.add(f"sash {k} pull", box(x0 + 12, yk - 14, 1300, x0 + 30, yk - 2, 1460), "icp_pp_grey")
    # ---------------------------------------------------------------- inside: the hot block, the acids, the dilutor
    hb_x, hb_y = HX0 + POST + 300, 40.0
    body.add("hot block base", rbox(500, 400, 170, 12, x=hb_x, y=hb_y, z=WS), "icp_pp")
    body.add("hot block panel", box(hb_x - 200, hb_y - 201, WS + 30, hb_x + 200, hb_y - 200, WS + 140), "screen_on")
    blk = rbox(420, 320, 110, 6, x=hb_x, y=hb_y + 20, z=WS + 170)
    holes = None
    for i in range(6):
        for j in range(4):
            c = cyl(30.0, 100.0, x=hb_x - 150 + 60 * i, y=hb_y + 20 - 90 + 60 * j, z=WS + 190)
            holes = c if holes is None else holes.union(c)
    body.add("hot block", blk.cut(holes), "icp_graphite")
    dig = None
    for i in range(6):
        for j in range(4):
            if (i + j) % 2:
                continue
            t = tube(29.0, 26.0, 115.0, x=hb_x - 150 + 60 * i, y=hb_y + 20 - 90 + 60 * j, z=WS + 192)
            dig = t if dig is None else dig.union(t)
    body.add("digestion tubes", dig, "icp_tube")
    # the acids: PFA bottles in a PP tray, back left of the dilutor
    body.add("acid tray", box(-1600, 150, WS, -1300, 360, WS + 30), "icp_pp_grey")
    for k, (nm, x) in enumerate((("HNO3", -1550.0), ("HCl", -1450.0), ("ultrapure water", -1350.0))):
        body.add(f"bottle {nm}", cyl(90, 210, x=x, y=255, z=WS + 6), "icp_pfa")
        body.add(f"bottle {nm} cap", cyl(44, 30, x=x, y=255, z=WS + 216), "icp_pp")
        if k < 2:
            body.add(f"bottle {nm} label", box(x - 30, 209, WS + 80, x + 30, 210, WS + 140), "icp_acid_label")
    for k, x in enumerate((-1550.0, -1450.0, -1350.0)):
        body.add(f"line {k}", hose([(x, 255, WS + 246), (x, 255, WS + 330), (DIL["x0"] + 60, 230, WS + 330),
                                    (DIL["x0"] + 60 + 40 * k, 230, WS + 440)], 4.0), "icp_pfa")
    # the dilutor (QPrep class; ours): a PP frame, side rails along y and a beam across them that carries the head; two
    # rack positions on its deck; three syringe pumps at the back
    x0, x1, y0, y1 = DIL["x0"], DIL["x1"], DIL["y0"], DIL["y1"]
    gz = GZ
    body.add("dilutor deck", box(x0, y0, WS, x1, y1, WS + DIL["deck"]), "icp_pp")
    for sx, xx in (("left", x0), ("right", x1 - 40)):
        body.add(f"dilutor column {sx} back", box(xx, y1 - 40, WS + DIL["deck"], xx + 40, y1, gz + 70), "icp_pp")
        body.add(f"dilutor column {sx} front", box(xx, y0, WS + DIL["deck"], xx + 40, y0 + 40, gz + 70), "icp_pp")
        body.add(f"dilutor rail {sx}", box(xx, y0, gz + 70, xx + 40, y1, gz + 100), "icp_pp_grey")
    for k in range(3):
        xs = x0 + 90 + 40 * k
        body.add(f"syringe pump {k}", box(xs - 16, y1 - 80, WS + 380, xs + 16, y1 - 45, WS + 560), "icp_pp_grey")
        body.add(f"syringe {k}", cyl(14, 120, x=xs, y=y1 - 95, z=WS + 420), "icp_pfa")
    for nm, (rx, ry, rz) in (("in", RACK_IN), ("out", RACK_OUT)):
        body.add(f"rack seat {nm}", box(rx - RACK["W"] / 2 - 8, ry - RACK["D"] / 2 - 8, rz - 2,
                                        rx + RACK["W"] / 2 + 8, ry + RACK["D"] / 2 + 8, rz), "icp_pp_grey")
        for sx in (-1, 1):
            body.add(f"rack stop {nm} {sx}", box(rx + sx * (RACK["W"] / 2 + 3) - 3, ry - 40, rz,
                                                 rx + sx * (RACK["W"] / 2 + 3) + 3, ry + 40, rz + 14), "icp_pp")
    beam = _piece(inst, "beam")
    hx, hy = HEAD_PARK
    beam.add("dilutor beam", box(x0, hy - 30, gz + 70, x1, hy + 30, gz + 110), "icp_pp")
    head = _piece(inst, "head")
    head.add("carriage", box(hx - 45, hy - 40, gz + 40, hx + 45, hy + 40, gz + 140), "icp_pp_grey")
    head.add("z column", box(hx - 20, hy - 20, gz - 20, hx + 20, hy + 20, gz + 40), "icp_pp")
    probe = _piece(inst, "probe")
    px_, py_ = hx + PROBE_DX, hy
    probe.add("probe body", box(hx + 20, py_ - 10, PROBE_TIP + 240, px_ + 10, py_ + 10, gz + 20), "icp_pp")
    probe.add("probe", cyl(2.4, 240, x=px_, y=py_, z=PROBE_TIP), "icp_pfa")
    chuck = _piece(inst, "chuck")
    chuck.add("chuck body", cyl(34, gz - 20 - (CHUCK_BOT + 40), x=hx, y=hy, z=CHUCK_BOT + 40), "icp_pp_grey")
    chuck.add("chuck jaws", tube(28, 22, 40, x=hx, y=hy, z=CHUCK_BOT), "inst_dark")
    # ---------------------------------------------------------------- the bench: the ICP-MS and its autosampler
    bh = BENCH["H"]
    body.add("bench top", box(BX0, BYF, bh - 30, BX1, YB, bh), "r7_epoxy" if "r7_epoxy" in I.MATERIALS else "inst_dark")
    for xx in (BX0 + 20, BX1 - 70):
        for yy in (BYF + 20, YB - 70):
            body.add(f"bench leg {xx:.0f} {yy:.0f}", box(xx, yy, 0, xx + 50, yy + 50, bh - 30), "stainless")
    body.add("bench rail", box(BX0 + 20, YB - 60, 120, BX1 - 20, YB - 20, 160), "stainless")
    # the SPS 4: its base, a rack tray, its XYZ arm, a clear cover with a front door (the door's actuator is ours)
    sx0, sx1 = SPS_X - SPS["W"] / 2, SPS_X + SPS["W"] / 2
    sy0, sy1 = BYF + 60, BYF + 60 + SPS["D"]
    body.add("SPS 4 base", rbox(SPS["W"], SPS["D"], 40, 10, x=SPS_X, y=(sy0 + sy1) / 2, z=bh), "icp_agilent")
    body.add("SPS 4 rinse station", rbox(90, 120, 60, 6, x=sx1 - 70, y=(sy0 + sy1) / 2, z=bh + 40), "icp_agilent_dk")
    body.add("SPS 4 tower", box(sx1 - 30, sy1 - 70, bh + 40, sx1 - 5, sy1 - 10, bh + 470), "icp_agilent")
    body.add("SPS 4 beam", box(sx0 + 20, sy1 - 70, bh + 430, sx1 - 5, sy1 - 30, bh + 470), "icp_agilent")
    body.add("SPS 4 rack seat", box(SPS_RACK[0] - RACK["W"] / 2 - 8, SPS_RACK[1] - RACK["D"] / 2 - 8, bh + 40,
                                    SPS_RACK[0] + RACK["W"] / 2 + 8, SPS_RACK[1] + RACK["D"] / 2 + 8, bh + 45),
             "icp_agilent_dk")
    for k in range(3):                                               # three more racks of standards and blanks
        rx = SPS_RACK[0] + 200.0 + 0 * k
        if k == 0:
            body.add("SPS 4 standards rack", box(rx - 60, SPS_RACK[1] - 80, bh + 45, rx + 60, SPS_RACK[1] + 80,
                                                 bh + 105), "icp_pp_grey")
    # its cover (Agilent's, vented): the walls stay; the top and the front's upper part are one lid, hinged at the
    # back, which an actuator (ours) lifts for the arm
    ch = bh + SPS["H"]
    cover = box(sx0 - 5, sy0 - 5, bh + 40, sx1 + 5, sy1 + 5, ch - 5).cut(box(sx0, sy0, bh + 40, sx1, sy1, ch))
    cover = cover.cut(box(sx0 - 10, sy0 - 10, bh + 250, sx1 + 10, sy0 + 1, ch))
    body.add("SPS 4 cover", cover, "icp_cover")
    body.add("SPS 4 cover port", _ycyl(50, 60, x=sx0 + 80, y=sy1 + 5, z=ch - 60), "icp_agilent_dk")
    lid = _piece(inst, "sps_door")
    lid.add("SPS 4 lid top", box(sx0 - 5, sy0 - 5, ch - 5, sx1 + 5, sy1 + 5, ch), "icp_cover")
    lid.add("SPS 4 lid front", box(sx0 - 5, sy0 - 5, bh + 252, sx1 + 5, sy0, ch - 5), "icp_cover")
    lid.add("SPS 4 lid edge", box(sx0 - 5, sy0 - 7, bh + 252, sx1 + 5, sy0 - 5, bh + 266), "icp_agilent_dk")
    lid.add("SPS 4 lid actuator", box(sx1 - 40, sy1 - 30, ch, sx1 - 10, sy1 + 5, ch + 25), "inst_dark")
    sarm = _piece(inst, "sps_arm")
    tx, ty = SPS_PARK
    sarm.add("SPS 4 carriage", box(tx - 25, sy1 - 75, bh + 400, tx + 25, sy1 - 25, bh + 440), "icp_agilent_dk")
    sarm.add("SPS 4 probe arm", box(tx - 10, ty - 10, bh + 410, tx + 10, sy1 - 75, bh + 430), "icp_agilent")
    sprobe = _piece(inst, "sps_probe")
    pl = bh + 410 - 24 - SPS_TIP                                      # the probe, up to a 24 mm holder under the arm
    sprobe.add("SPS 4 probe holder", box(tx - 8, ty - 8, SPS_TIP + pl, tx + 8, ty + 8, bh + 410), "icp_agilent_dk")
    sprobe.add("SPS 4 probe", cyl(3.0, pl, x=tx, y=ty, z=SPS_TIP), "stainless")
    # the 7850
    ix0, ix1 = ICP_X - ICP["W"] / 2, ICP_X + ICP["W"] / 2
    iy0 = YB - ICP["D"]
    body.add("7850", rbox(ICP["W"], ICP["D"], ICP["H"], 18, x=ICP_X, y=iy0 + ICP["D"] / 2, z=bh), "icp_agilent")
    body.add("7850 top", rbox(ICP["W"] - 20, ICP["D"] - 20, 6, 14, x=ICP_X, y=iy0 + ICP["D"] / 2, z=bh + ICP["H"]),
             "inst_light")
    body.add("7850 sample door", box(ix0 + 30, iy0 - 4, bh + 150, ix0 + 300, iy0, bh + 520), "icp_agilent_dk")
    body.add("7850 window", box(ix0 + 60, iy0 - 6, bh + 300, ix0 + 270, iy0 - 4, bh + 480), "window")
    body.add("7850 pump", box(ix0 + 30, iy0 - 40, bh + 60, ix0 + 160, iy0, bh + 140), "inst_dark")
    body.add("7850 stripe", box(ix0 + 320, iy0 - 2, bh + 470, ix1 - 30, iy0, bh + 490), "icp_agilent_blue")
    body.add("7850 status", box(ix1 - 120, iy0 - 2, bh + 420, ix1 - 40, iy0, bh + 440), "led_blue")
    body.add("7850 exhaust", cyl(150, 2900 - bh - ICP["H"], x=ICP_X + 200, y=YB - 120, z=bh + ICP["H"]), "icp_duct")
    body.add("SPS 4 exhaust", hose([(sx0 + 80, sy1 - 60, bh + SPS["H"] + 60), (sx0 + 80, sy1 - 60, 2000),
                                    (ICP_X + 200 - 75, YB - 120, 2300)], 50.0), "icp_duct")
    # the PC and its screen at the bench's right end
    body.add("monitor", box(BX1 - 330, YB - 220, bh + 120, BX1 - 60, YB - 200, bh + 420), "inst_black")
    body.add("monitor screen", box(BX1 - 320, YB - 222, bh + 130, BX1 - 70, YB - 220, bh + 410), "screen_on")
    body.add("monitor stand", box(BX1 - 215, YB - 200, bh, BX1 - 175, YB - 160, bh + 120), "inst_dark")
    # under the bench: the chiller and the forepump on its drip pan; hoses up the back
    cx = ICP_X + 120
    body.add("chiller", rbox(CHILLER["W"], CHILLER["D"], CHILLER["H"], 10, x=cx, y=YB - 20 - CHILLER["D"] / 2, z=0),
             "icp_agilent")
    body.add("chiller grille", box(cx - 150, YB - 23 - CHILLER["D"], 60, cx + 150, YB - 20 - CHILLER["D"], 300),
             "inst_dark")
    px = ICP_X - 260
    body.add("drip pan", box(px - 110, YB - 40 - PUMP["D"] - 30, 0, px + 110, YB - 10, 25), "stainless")
    body.add("forepump", rbox(PUMP["W"], PUMP["D"], PUMP["H"], 8, x=px, y=YB - 40 - PUMP["D"] / 2, z=25),
             "icp_agilent_dk")
    for k, dx in enumerate((-60.0, 60.0)):
        body.add(f"coolant hose {k}", hose([(cx + dx, YB - 30, CHILLER["H"] - 20), (cx + dx, YB - 30, bh + 100),
                                            (ICP_X + dx, YB - 10, bh + 100)], 16.0), "inst_dark")
    body.add("vacuum hose", hose([(px, YB - 40, PUMP["H"] + 25), (px, YB - 40, bh + 60), (ICP_X - 200, YB - 5, bh + 60)],
                                 30.0), "inst_dark")
    # the argon dewar, chained to the wall, its line to the 7850
    dx_, dy_ = DEWAR_XY
    body.add("dewar", cyl(DEWAR["d"], DEWAR["H"] - 150, x=dx_, y=dy_, z=40), "icp_dewar")
    body.add("dewar dome", cq.Workplane("XY").sphere(DEWAR["d"] / 2).intersect(
        box(-400, -400, 0, 400, 400, 200)).translate((dx_, dy_, DEWAR["H"] - 110 - 120)), "icp_dewar")
    body.add("dewar ring", tube(DEWAR["d"] + 10, DEWAR["d"] - 140, 90, x=dx_, y=dy_, z=DEWAR["H"] - 90), "stainless")
    body.add("dewar base", cyl(DEWAR["d"] + 20, 40, x=dx_, y=dy_, z=0), "inst_dark")
    body.add("dewar valves", box(dx_ - 60, dy_ - 40, DEWAR["H"] - 60, dx_ + 60, dy_ + 40, DEWAR["H"] + 30), "chrome")
    body.add("dewar chain", box(dx_ - DEWAR["d"] / 2 - 10, YB - 8, 1150, dx_ + DEWAR["d"] / 2 + 10, YB - 2, 1170),
             "inst_dark")
    body.add("argon line", hose([(dx_, dy_, DEWAR["H"] + 30), (dx_, dy_, 1900), (ix1 - 40, YB - 30, 1900),
                                 (ix1 - 40, YB - 30, bh + ICP["H"] - 60)], 10.0), "stainless")
    body.add("argon regulator", cyl(70, 50, x=dx_ - 90, y=dy_, z=1780).union(
        _ycyl(16, 90, x=dx_ - 90, y=dy_ - 45, z=1805)), "chrome")
    # ---------------------------------------------------------------- the moves, for a tour of the station alone
    inst.joints.update({
        "sash1": Joint("slide", vec=(-PANEL, 0, 0)),
        "sash2": Joint("slide", vec=(-PANEL, 0, 0)),
        "sash3": Joint("slide", vec=(-2 * PANEL, 0, 0)),
        "head": Joint("path", path=_head_path()),
        "beam": Joint("follow", path=_head_path(), jac=_Y_ONLY),
        "probe": Joint("slide", vec=(0, 0, -(PROBE_TIP - (RACK_IN[2] + RACK["floor"] + 12.0))), parent="head"),
        "chuck": Joint("slide", vec=(0, 0, -(CHUCK_BOT - TUBE_TOP + 1.0)), parent="head"),
        "sps_door": Joint("hinge", axis=(1, 0, 0), pivot=(0, sy1 + 5, bh + SPS["H"]), deg=-105.0),
        "sps_arm": Joint("path", path=_sps_path()),
        "sps_probe": Joint("slide", vec=(0, 0, -(SPS_TIP - (SPS_RACK[2] + RACK["floor"] + 12.0))), parent="sps_arm"),
    })
    inst.actions = [
        ("The right half of the sash slides open: three panels stack behind the first, half the hood's width.", 2.0,
         {"sash1": (0.0, 0.5), "sash2": (0.0, 1.0), "sash3": (0.0, 1.0)}),
        ("The dilutor's head goes to the first tube.", 2.0, {"head": (0.0, 0.33)}),
    ]
    inst.labels = _labels()
    inst.cam = (0.55, -1.6, 0.62)
    inst.props = ()
    return inst


# The head's path over the deck, as offsets from where it is modelled (parked at HEAD_PARK): the chuck over the
# in-rack's tube 0 (to take its cap off and put it back), the probe over that tube, the probe over the out-rack's tube
# 0. HEAD_V gives the joint value at each stop; the beam follows the head's y (a "follow" joint on the same path).
def _rel(p):
    return (p[0] - HEAD_PARK[0], p[1] - HEAD_PARK[1], 0.0)


IN0 = (RACK_IN[0] + tube_xy(0)[0], RACK_IN[1] + tube_xy(0)[1])
OUT0 = (RACK_OUT[0] + tube_xy(0)[0], RACK_OUT[1] + tube_xy(0)[1])
HEAD_STOPS = [("park", (0.0, 0.0, 0.0)), ("chuck_in0", _rel(IN0)), ("probe_in0", _rel((IN0[0] - PROBE_DX, IN0[1]))),
              ("probe_out0", _rel((OUT0[0] - PROBE_DX, OUT0[1]))), ("probe_in0b", _rel((IN0[0] - PROBE_DX, IN0[1]))),
              ("chuck_in0b", _rel(IN0)), ("park_end", (0.0, 0.0, 0.0))]


def _head_path():
    return tuple(p for _, p in HEAD_STOPS)


def _stop_values() -> dict:
    pts = np.asarray(_head_path(), float)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s_ = np.concatenate([[0.0], np.cumsum(seg)])
    return {name: float(s_[k] / s_[-1]) for k, (name, _) in enumerate(HEAD_STOPS)}


HEAD_V = _stop_values()
_Y_ONLY = (((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)), ((0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 0, 0)),
           ((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)))          # follow: move by d's y only


def _sps_path():
    """The SPS 4's arm: parked over its standards rack, then along the first row of the rack the arm set down: tubes
    0, 6, 12 and 18 (offsets from the park)."""
    pts = [(0.0, 0.0, 0.0)]
    for i in (0, 6, 12, 18):
        x, y = tube_xy(i)
        pts.append((SPS_RACK[0] + x - SPS_PARK[0], SPS_RACK[1] + y - SPS_PARK[1], 0.0))
    return tuple(pts)


def sps_v(k: int) -> float:
    """The SPS 4 arm's joint value over stop k (0: park, 1-4: tubes 0, 6, 12, 18)."""
    pts = np.asarray(_sps_path(), float)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s_ = np.concatenate([[0.0], np.cumsum(seg)])
    return float(s_[k] / s_[-1])


def _labels():
    bh = BENCH["H"]
    return [
        ("polypropylene trace-metals hood\n(HEMCO UniFlow 6 ft)", ((HX0 + HX1) / 2, HYF, HTOP - 220), (0.20, 0.10)),
        ("HNO3, HCl in PFA bottles\n(no HF)", (-1500.0, 210.0, WS + 150), (0.08, 0.32)),
        ("graphite hot block\n(digestion)", (HX0 + POST + 300, 40.0, WS + 280), (0.06, 0.55)),
        ("acid-rated dilutor,\nPFA fluid path", (-870.0, 200.0, WS + 640), (0.36, 0.20)),
        ("Agilent 7850 ICP-MS", (ICP_X, YB - ICP["D"], bh + ICP["H"] - 60), (0.80, 0.22)),
        ("SPS 4 autosampler,\nvented cover", (SPS_X, BYF + 60, bh + SPS["H"] - 40), (0.58, 0.28)),
        ("chiller, forepump", (ICP_X + 120, YB - 20 - CHILLER["D"], 400), (0.78, 0.82)),
        ("liquid argon, 180 L", (DEWAR_XY[0], DEWAR_XY[1] - DEWAR["d"] / 2, 1200), (0.94, 0.50)),
        ("own exhaust drop", (ICP_X + 200, YB - 120, 2300), (0.84, 0.06)),
    ]


REGISTRY = {"icpms": station}


# ===================================================================================================== the clip
MIR_X = -380.0                       # the MiR250 parks in front of the station, between the hood's opening and the SPS 4
MIR_Y = HYF - 60.0 - 290.0           # 60 mm clear of the hood's front
MIR_FROM = 1500.0                    # it drives in from 1.5 m to the right, at the MiR's published 0.3 m/s^2
CARRIER = (266.0, -40.0)             # the rack's carrier on the MiR's cabinet top (local), right of the arm's plate,
                                     # the rack turned 90 deg so it fits beside the plate
HANDLE_GRASP = RACK["handle"][2] - 11.0      # the pads' centre on the handle's T top, over the rack's base
STOW_DEG = (90.0, -150.0, 135.0, -75.0, -90.0, 180.0)   # animate.PARK_DEG turned to face away from the station, so the
#                                                          folded arm doesn't stand between the camera and the hood


def sleeve(sc, rb, inflate: float = 6.0):
    """The arm's PTFE-laminate cover (Roboworld Robosuit class): over the shoulder, upper arm, forearm and wrists 1-2,
    a loose skin on each link, here its convex hull pushed out `inflate` mm. Added to the links' own groups, so it moves
    with them; the collision checker keeps to the arm's own bodies (collide.ArmBodies), so the cover itself isn't
    checked: it is fabric, about 6 mm off the arm."""
    import pyvista as pv
    import ur_arm
    from scipy.spatial import ConvexHull
    for link, lst in ur_arm.arm_meshes(rb.model).items():
        if link not in ("shoulder", "upper_arm", "forearm", "wrist1", "wrist2"):
            continue
        pts = np.vstack([np.asarray(m.points) for m, _, _ in lst])
        hull = ConvexHull(pts)
        faces = np.hstack([np.full((len(hull.simplices), 1), 3), hull.simplices]).ravel()
        mesh = pv.PolyData(pts, faces).clean()
        mesh = mesh.compute_normals(auto_orient_normals=True, consistent_normals=True, split_vertices=False)
        mesh.points = mesh.points + mesh.point_data["Normals"] * inflate
        mesh = mesh.subdivide(1, "loop") if mesh.n_cells < 4000 else mesh
        r, g, b, a, spec = MATERIALS["icp_sleeve"]
        sc.add(f"{rb.prefix}_sleeve/{link}", mesh, (r, g, b), f"{rb.prefix}_{link}", opacity=a, specular=0.05)


def bom() -> dict:
    """The station's parts with their sizes, sources and prices where public (out/icpms_bom.json)."""
    return dict(
        note="Round 13, run D: the ICP-MS station (icpms.py, notes/icpms.md). Prices are public figures, not quotes.",
        items=[
            dict(item="ICP-MS", product="Agilent 7850 (UHMI standard)", size_mm=[730, 600, 595], mass_kg=100,
                 power="200-240 V single phase, 30 A circuit", argon="20 L/min", exhaust="150 mm, 5-7 m3/min",
                 price="$160-220k (LabX 2026 guide); a 7800 system was $122,526 net in 2017 (Agilent quote)",
                 source=SOURCES["ICP-MS"]),
            dict(item="Autosampler", product="Agilent SPS 4 with its vented cover", size_mm=[600, 363, 510],
                 mass_kg=15, price="$12,305 list (2017)", source=SOURCES["ICP-MS"]),
            dict(item="Chiller", product="Agilent G3292A", size_mm=[368, 702, 576], mass_kg=85, power="2900 W"),
            dict(item="Forepump", product="the 7850's own (DS402 on the 7800: 164 x 541 x 242 mm, 35 kg)"),
            dict(item="Fume hood", product="HEMCO UniFlow Trace Metals, 6 ft, polypropylene, on an acid cabinet",
                 size_mm=[1829, 813, 1499], price="quote", source=SOURCES["hood"]),
            dict(item="Dilutor", product="acid-rated, all-fluoropolymer fluid path (Questron/HORIBA QPrep class), "
                 "with a decapping head (ours)", size_mm=[840, 550, 700], price="quote", source=SOURCES["dilutor"]),
            dict(item="Hot block", product="graphite digestion block (SCP Science DigiPREP class), 24 x 50 mL",
                 size_mm=[500, 400, 280], price="quote", source=SOURCES["hot block"]),
            dict(item="Argon", product="180 L liquid argon dewar, 22 psi, regulator within 3 m", size_mm=[508, 508, 1635],
                 source=SOURCES["argon"]),
            dict(item="Arm cover", product="PTFE-laminate robot suit for the UR12e (Roboworld Robosuit class)",
                 price="quote", source=SOURCES["cover"]),
            dict(item="Racks and caps", product="15 mL PP tube racks with a central handle (ours); PP screw caps"),
        ])


def clip():
    """The station at work: the MiR250 + UR12e (the code's UR10e, renamed) in its PTFE cover brings a capped rack of
    corrosion samples from tray A and sets it in the hood; the dilutor takes tube 0's cap off, dilutes its sample tenfold
    into 2 % HNO3 with an internal standard in the autosampler rack, and puts the cap back (and so on for the rest);
    the arm takes the filled autosampler rack to the SPS 4, which feeds the 7850."""
    import animate as A
    import lab
    import props as P
    import robot as RB
    import tour
    import ur_arm
    from scene import Scene, T

    grip = ur_arm.close_for(RACK["handle"][0] + 0.3)          # on the handle's 16 mm web
    opened = ur_arm.close_for(52.0)                          # around the 36 mm T top, with room
    tour.MATS.update(MATERIALS_ALL)
    inst = station()
    ents = tour.piece_entries(inst)
    sc = Scene("icpms", "An ICP-MS station on the floor, its acids kept in a fume hood (round 13)")
    sc.intro = 0.8
    bb = inst.bbox()
    tour.studio(sc, size=12000.0, shadow_of=bb)
    rig = tour.Rig(sc, inst, ents, "icp:")

    def mesh_of(wp):
        shape = wp.val() if len(wp.vals()) == 1 else cq.Compound.makeCompound(wp.vals())
        return lab.to_mesh(shape, 0.5, 0.12)

    def add_parts(g, parts, parent, M):
        for part, (shape, mat) in parts.items():
            r, gg, b, a, spec = MATERIALS_ALL[mat]
            sc.add(f"{g}/{part}", mesh_of(shape), (r, gg, b), g, opacity=a, specular=spec)
        sc.parent[g] = parent
        sc.gmat[g] = M
    # the racks: the capped samples (tube 0's cap a group of its own, for the decapper), the empty autosampler rack
    parts_in = rack_parts(True)
    caps = parts_in.pop("caps")
    x0_, y0_ = tube_xy(0)
    cap0 = cyl(RACK["cap_d"], RACK["cap_h"], x=x0_, y=y0_, z=RACK["floor"] + RACK["tube_h"])
    parts_in["caps"] = (caps[0].cut(cyl(RACK["cap_d"] + 1, RACK["cap_h"] + 2, x=x0_, y=y0_,
                                        z=RACK["floor"] + RACK["tube_h"] - 1)), caps[1])
    for name, (mesh, col) in P.mir250().items():
        kw = dict(ambient=0.8) if "light" in name else {}
        sc.add(f"amr/{name}", mesh, col, "amr", **kw)
    cz = P.MIR["H"] + P.CAB_H                                # the cabinet's top, 780
    cw, cd = RACK["D"] + 12, RACK["W"] + 12                  # the carrier, the rack turned 90 deg in it
    car = box(CARRIER[0] - cw / 2, CARRIER[1] - cd / 2, cz, CARRIER[0] + cw / 2, CARRIER[1] + cd / 2, cz + 22).cut(
        box(CARRIER[0] - cw / 2 + 6, CARRIER[1] - cd / 2 + 6, cz + 4, CARRIER[0] + cw / 2 - 6, CARRIER[1] + cd / 2 - 6,
            cz + 30))
    sc.add("amr/rack carrier", mesh_of(car), (0.70, 0.71, 0.70), "amr")
    x_in = MIR_X + MIR_FROM
    sc.gmat["amr"] = T((x_in, MIR_Y, 0.0))
    from scene import R
    # turned -90 deg in the carrier: picked with the pads along y (spin 90) and set down with them along x (spin 0),
    # the gripper's turn brings it square on the deck, tube 0 at its front left
    add_parts("rack_in", parts_in, "amr", T((CARRIER[0], CARRIER[1], cz + 4.0)) @ R((0, 0, 1), -90.0))
    add_parts("rack_in_cap0", {"cap": (cap0, "icp_cap_in")}, "rack_in", np.eye(4))
    add_parts("rack_out", rack_parts(False), None, T(RACK_OUT))
    rb = RB.Robot(sc, A.ROBOT, "amr", T((*A.ARM_LOCAL, P.AMR_TOP)), q0=A.PARK_DEG)
    sleeve(sc, rb)
    rb.set(close=opened)

    def down_at(p, spin=0.0):
        return P.tcp_frame(np.asarray(p, float), (0, 0, -1), spin)

    def grasp_point(g):
        return (sc.world(g) @ np.r_[0.0, 0.0, HANDLE_GRASP, 1.0])[:3]

    def reparent(g, new_parent):
        W = sc.world(g)
        sc.parent[g] = new_parent
        sc.gmat[g] = np.linalg.inv(sc.world(new_parent)) @ W

    whole = tour.frame_cam(bb, (0.42, -1.7, 0.70), pad=0.78, look_z=0.45)
    sc.cam = whole
    hood_cam = tour.close_cam((-600.0, -300.0, 1150.0), 3300.0, (0.70, -1.45, 0.80))
    mir_cam = tour.close_cam((-100.0, -650.0, 1000.0), 3600.0, (0.45, -1.45, 0.75))
    deck_cam = tour.close_cam((-740.0, -90.0, 1110.0), 1300.0, (0.20, -1.25, 1.10))
    block_cam = tour.close_cam((HX0 + POST + 300, 40.0, WS + 200), 2300.0, (0.40, -1.5, 0.85))
    sps_cam = tour.close_cam((SPS_X + 150.0, BYF + 150.0, 1200.0), 2300.0, (0.70, -1.45, 0.80))
    labels = list(inst.labels)
    n = 8
    sc.step(f"1/{n}", "An ICP-MS station on the floor beside the VLM (round 13): its concentrated acids stay in a "
            "metal-free polypropylene fume hood, off every tray. Beside it an Agilent 7850 ICP-MS with its SPS 4 "
            "autosampler, the chiller and forepump under the bench, and liquid argon in a 180 L dewar.", 6.0, None,
            hold=1.5, labels=labels)
    dist = abs(MIR_FROM)

    def drive(u):
        f = P.ramp_frac(u, dist, 600.0)
        sc.gmat["amr"] = T((x_in + (MIR_X - x_in) * f, MIR_Y, 0.0))
        rb.set()
    sc.step(f"2/{n}", "A MiR250 + UR12e brings a capped rack of corrosion samples from tray A. The arm wears a "
            "PTFE-laminate cover zipped at its base and wrist: the arm itself is IP54, and UR asks for a cover where "
            "liquids are about.", P.ramp_secs(dist, 600.0), drive, hold=0.6, cam_to=mir_cam)
    sc.step(f"3/{n}", "The right half of the sash opens: on two tracks, three panels slide behind the first. The arm "
            "works through the opening, as a person does.", 2.2,
            rig.move({"sash1": (None, 1.0), "sash2": (None, 1.0), "sash3": (None, 1.0)}), hold=0.4, cam_to=hood_cam)
    # the capped rack: off the carrier (turned 90 deg there, so the pads close along y), onto the dilutor's deck
    cap4 = ("The arm takes the rack by its handle (ours) and sets it on the dilutor's deck, 250 mm inside the sash. Only "
            "capped tubes cross the opening, and the arm never carries an open concentrated acid.")
    gp = grasp_point("rack_in")
    sc.step(f"4/{n}", cap4, 1.8, rb.joint_to(Tw=down_at(gp + (0, 0, 150.0), 90.0)), hold=0.0)
    sc.step(f"4/{n}", cap4, 0.8, rb.line_to(down_at(gp, 90.0)), hold=0.0)
    sc.step(f"4/{n}", cap4, 0.4, rb.grip_to(grip), hold=0.0)
    rb.grasp("rack_in")
    sc.step(f"4/{n}", cap4, 0.8, rb.line_to(down_at(gp + (0, 0, 220.0), 90.0)), hold=0.0)
    tgt = np.asarray(RACK_IN, float) + (0, 0, HANDLE_GRASP + 1.0)
    sc.step(f"4/{n}", cap4, 2.8, rb.joint_to(Tw=down_at(tgt + (0, 0, 130.0))), hold=0.0)
    sc.step(f"4/{n}", cap4, 0.9, rb.line_to(down_at(tgt)), hold=0.0)
    sc.step(f"4/{n}", cap4, 0.4, rb.grip_to(opened), hold=0.0)
    rb.release("icp:body")
    sc.step(f"4/{n}", cap4, 0.8, rb.line_to(down_at(tgt + (0, 0, 180.0))), hold=0.0)
    sc.step(f"4/{n}", cap4, 2.4, rb.joint_to(q1=np.radians(STOW_DEG)), hold=0.3)
    # the dilutor: tube 0 in full
    cap5 = ("Inside, an acid-rated dilutor (QPrep class): PFA probe and lines, syringe pumps, no metal or PEEK where the "
            "acid goes. Its head (ours) unscrews tube 0's cap, takes an aliquot, makes a tenfold dilution into 2 % "
            "nitric acid with an internal standard in the autosampler rack, and caps the tube again.")
    hv = HEAD_V

    def head_to(name):
        return rig.move({"head": (None, hv[name]), "beam": (None, hv[name])})
    sc.step(f"5/{n}", cap5, 1.6, head_to("chuck_in0"), hold=0.0, cam_to=deck_cam)
    sc.step(f"5/{n}", cap5, 0.8, rig.move({"chuck": (None, 1.0)}), hold=0.2)
    reparent("rack_in_cap0", "icp:chuck")
    sc.step(f"5/{n}", cap5, 0.8, rig.move({"chuck": (None, 0.0)}), hold=0.0)
    sc.step(f"5/{n}", cap5, 0.5, head_to("probe_in0"), hold=0.0)
    sc.step(f"5/{n}", cap5, 1.0, rig.move({"probe": (None, 1.0)}), hold=0.5)
    sc.step(f"5/{n}", cap5, 0.8, rig.move({"probe": (None, 0.0)}), hold=0.0)
    sc.step(f"5/{n}", cap5, 1.4, head_to("probe_out0"), hold=0.0)
    sc.step(f"5/{n}", cap5, 0.8, rig.move({"probe": (None, 0.5)}), hold=0.5)
    sc.step(f"5/{n}", cap5, 0.6, rig.move({"probe": (None, 0.0)}), hold=0.0)
    sc.step(f"5/{n}", cap5, 1.4, head_to("chuck_in0b"), hold=0.0)
    sc.step(f"5/{n}", cap5, 0.8, rig.move({"chuck": (None, 1.0)}), hold=0.2)
    reparent("rack_in_cap0", "rack_in")
    sc.step(f"5/{n}", cap5, 0.7, rig.move({"chuck": (None, 0.0)}), hold=0.0)
    sc.step(f"5/{n}", "The same for the other 23 tubes, about 40 s each (an estimate), then the head parks.", 1.6,
            head_to("park_end"), hold=0.5)
    sc.step(f"6/{n}", "The hot block digests chips or powder of each build in nitric and hydrochloric acid, aqua regia "
            "for the copper alloys. With no HF, silicon over about 1 % won't dissolve, so Si comes from the XRF.", 4.0,
            None, hold=0.8, cam_to=block_cam)
    # the filled autosampler rack to the SPS 4
    cap7 = ("The filled autosampler rack (dilute acid, open tubes) goes to the SPS 4: its lid lifts (the actuator is "
            "ours) and the arm sets the rack on the tray.")
    gp = grasp_point("rack_out")
    sc.step(f"7/{n}", cap7, 2.0, rb.joint_to(Tw=down_at(gp + (0, 0, 150.0))), hold=0.0, cam_to=hood_cam)
    sc.step(f"7/{n}", cap7, 0.8, rb.line_to(down_at(gp)), hold=0.0)
    sc.step(f"7/{n}", cap7, 0.4, rb.grip_to(grip), hold=0.0)
    rb.grasp("rack_out")
    sc.step(f"7/{n}", cap7, 0.8, rb.line_to(down_at(gp + (0, 0, 220.0))), hold=0.0)
    sc.step(f"7/{n}", cap7, 1.6, rig.move({"sps_door": (None, 1.0)}), hold=0.0, cam_to=sps_cam)
    tgt = np.asarray(SPS_RACK, float) + (0, 0, HANDLE_GRASP + 1.0)
    sc.step(f"7/{n}", cap7, 2.8, rb.joint_to(Tw=down_at(tgt + (0, 0, 130.0))), hold=0.0)
    sc.step(f"7/{n}", cap7, 0.9, rb.line_to(down_at(tgt)), hold=0.0)
    sc.step(f"7/{n}", cap7, 0.4, rb.grip_to(opened), hold=0.0)
    rb.release("icp:body")
    sc.step(f"7/{n}", cap7, 0.8, rb.line_to(down_at(tgt + (0, 0, 220.0))), hold=0.0)
    sc.step(f"7/{n}", cap7, 2.4, rb.joint_to(q1=np.radians(STOW_DEG)), hold=0.0)
    sc.step(f"7/{n}", cap7, 1.4, rig.move({"sps_door": (None, 0.0), "sash1": (None, 0.0), "sash2": (None, 0.0),
                                           "sash3": (None, 0.0)}), hold=0.3)
    cap8 = ("The SPS 4 feeds the 7850, whose aerosol dilution takes salty samples up to 25 % dissolved solids. It needs "
            "20 L/min of argon (a 180 L dewar lasts about five days of plasma), 30 A at 208 V and an exhaust drop of its "
            "own. About $160-220k for the ICP-MS; the hood, dilutor and cover are quotes.")
    for k in (1, 2, 3, 4):
        sc.step(f"8/{n}", cap8, 1.0, rig.move({"sps_arm": (None, sps_v(k))}), hold=0.0)
        sc.step(f"8/{n}", cap8, 0.7, rig.move({"sps_probe": (None, 1.0)}), hold=0.4)
        sc.step(f"8/{n}", cap8, 0.6, rig.move({"sps_probe": (None, 0.0)}), hold=0.0)
    sc.step(f"8/{n}", cap8, 3.0, rig.move({"sps_arm": (None, 0.0)}), hold=2.0, cam_to=whole, labels=labels)
    return sc.save()


if __name__ == "__main__":
    args = sys.argv[1:]
    (OUT / "icpms_bom.json").write_text(json.dumps(bom(), indent=1) + "\n")
    if args and args[0] == "bom":
        print(OUT / "icpms_bom.json")
    else:
        print(clip(), flush=True)
