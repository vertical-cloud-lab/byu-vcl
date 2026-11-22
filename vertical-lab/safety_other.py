"""The lab's other safety assets (#303, after safety.py's Class D units): the building's ordinary extinguishers, kept
apart from the Class D units and signed differently; an eyewash and drench shower at each hood that holds acids or
caustics; and oxygen monitors where argon and nitrogen are used. notes/safety.md ("The other safety assets") has the
sources, the rules and the checks.

Sterling, PR #379 (2026-11-22), on the PR's list of what wasn't modelled ("the building's ordinary extinguishers (keep
them apart and signed differently); an eyewash and shower at the ICP-MS hood and the fume hood; O2 monitors where argon
and nitrogen are used"): "Do these."

The assets, each built part by part from the maker's figures:

* **Amerex B456** (``abc_parts``): the building's ordinary unit, 10 lb ABC dry chemical (monoammonium phosphate),
  4-A:80-B:C, stored pressure. Red, so it can't be taken for the yellow Class D units, and hung where a warehouse keeps
  its extinguishers: on the racking's uprights, at the ends of the aisle (``rack_parts``), under a red FIRE
  EXTINGUISHER sign and an ABC placard that says NOT FOR METAL FIRES. Never next to a powder station.
* **Combination drench shower and eye/face wash** (``shower_parts``), Guardian G1902 class: a floor-mounted galvanized
  column, an ABS showerhead on its arm with a pull rod and triangle handle, an ABS eye/face wash bowl with two flip-top
  heads and a push flag, stay-open ball valves, the green ISO 7010 sign; with what the standard asks round it (ANSI/ISEA
  Z358.1): tepid water from a thermostatic mixing valve, a clear floor under the spray, and (ours) a floor drain.
* **Oxygen-deficiency monitor** (``o2_parts``), PureAire class: a zirconia O2 sensor that reads to 25 %, its display,
  two alarm relays at 19.5 % and 18 %, a horn and strobe on top, a CAUTION sign. For argon (heavier than air) the
  sensor goes low, 300 mm off the floor, on a lead from the monitor; for nitrogen it sits in the breathing zone.

    python3 safety_other.py                     # the checks -> out/safety_other.json
    python3 safety_other.py plan                # the floor: every unit, the walks -> out/safety_other_plan.png
    python3 safety_other.py abc-search          # the fewest ordinary units on the racking that pass the rules
    xvfb-run -a python3 safety_other.py sheet   # the assets one by one -> out/safety_other_assets.png
    VLAB_ONLY_TRAYS= xvfb-run -a python3 safety_other.py lab   # in the lab -> out/safety_other_lab.png

The placed units (PLACES) go into ``setup_lab.build`` after the Class D units; ``VLAB_SAFETY_OTHER=0`` leaves them out.
The ICP-MS station isn't on setup_lab's floor yet (notes/icpms.md suggests the south row's east end); its shower and O2
monitor are placed at that suggestion and go into the lab with the station (``ICPMS_ON_FLOOR``).
"""
from __future__ import annotations

import heapq
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

import safety as S
from safety import IN, LB, _add, _box, _cyl, _flat_poly, _merge, _mesh, _on_cyl, _on_face, _prism, _revolve, _sector, \
    _text, _tube

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

# ================================================================================================ what each part is
# Amerex B456, its own frame as safety.B570's: the origin at the centre of the cylinder's bottom, z up, the label (its
# front) to -y, the hose down its left side (-x) to the nozzle in its clip. Heights from the bottom.
ABC = dict(
    model="Amerex B456", agent="10 lb ABC dry chemical (monoammonium phosphate)", rating="4-A:80-B:C",
    d=5.0 * IN,             # the cylinder, 127 mm
    z_wall=338.0,           # the top of the straight wall
    z_dome=376.0,           # the head's top, at the neck
    z_seat=388.0,           # the wall hook's seat, under the valve
    z_gauge=410.0,
    z_top=20.0 * IN,        # the lever's tip, the highest point (508 mm)
    width=7.75 * IN,        # with the hose and the lever
    ship_lb=18.0, psig=195, range_ft=(15, 21), discharge_s=22, price_usd=92.99,
    source="Amerex's catalogue, ABC dry chemical table (p. 16) and brackets (p. 19), via webstaurantstore.com's copies: "
           "B456, 10 lb ABC, UL 4-A:80-B:C, 20 H x 7.75 W x 5 D in, cylinder 5 in, 18 lb shipping, 195 psig, 15-21 ft, "
           "22 s, aluminium valve, hose and nozzle, the 801 wall bracket; $92.99 (Webstaurant). The valve, lever and "
           "hose shapes are Amerex's family look (safety.B570's), not measured")
# The combination unit, its own frame: the column's axis on the floor at the origin, the showerhead and the bowl out to
# -y (its front: where a person stands), the supply into the top from above.
SHOWER = dict(
    model="Guardian G1902", pipe_od=42.2, cover_od=52.0, flange_d=9 * IN,   # 1-1/4 in galvanized, orange PE covers
    z_arm=89 * IN, z_top=94.75 * IN,                 # the shower arm's centre line; the actuating arm's top
    head_d=10 * IN, head_z=84 * IN, head_y=-24 * IN,  # the orange ABS head, its underside 84 in up, 24 in out
    bowl_d=11.125 * IN, eye_z=37.5 * IN, bowl_y=-9.25 * IN, eye_gap=6.5 * IN,   # stainless bowl; the heads' tops
    rod_z=65.5 * IN,                                 # the triangle handle's bottom (ANSI: at most 69 in)
    valve_x=6 * IN, flag=5 * IN,                     # the eyewash valve beside the bowl, its flag handle beyond it
    waste_z=9.25 * IN, gpm_shower=20.0, price_usd=967.75,
    source="Guardian Equipment G1902 spec sheet (rev. 0615, cooneybrothers.com's copy; dimensions +-1/4 in; 'tested "
           "to and comply with ANSI Z358.1-2014'): the shower arm's centre line 89 in up, the actuating arm 5-3/4 in "
           "over it; a 10 in orange ABS showerhead, its underside 84 in up, its centre 24 in from the pipe; a 1 in "
           "stay-open brass ball valve, a stainless actuating arm and 29 in pull rod with a triangle handle 23-1/2 in "
           "under the arm; two GS-Plus eyewash heads 6-1/2 in apart, their tops 37-1/2 in up, in an 11-1/8 in "
           "stainless bowl 9-1/4 in from the pipe; a 1/2 in ball valve 6 in beside the bowl with a cast aluminium flag "
           "handle 5 in beyond it; schedule 40 galvanized pipe with orange polyethylene covers on the vertical runs; "
           "1-1/4 in NPT top or side inlet, waste outlet 9-1/4 in up; a 9 in cast aluminium floor flange; 20 gpm; its "
           "green ANSI sign included; $967.75 (Webstaurant)")
MIXER = dict(w=12 * IN, h=10.75 * IN, d=7.125 * IN, cab=(16 * IN, 14 * IN, 8 * IN), price_usd=994.0,
             source="Guardian G3800LF thermostatic mixing valve (its spec sheet): 3-44 gpm, blends to 85 F with a 90 F "
                    "high limit, 1 in inlets and a 1-1/4 in outlet, 12 in between the inlets, 10-3/4 in tall, 7-1/8 in "
                    "deep; in a surface cabinet (G3802LF; the cabinet's size is ours). Discontinued: its successor, the "
                    "G6040, about $994 on sale ($1,603 list)")
ANSI = dict(travel_s=10.0, travel_m=16.8, adjacent_m=3.0, head_min=82 * IN, head_max=96 * IN, spray_d=20 * IN,
            spray_clear=16 * IN, eye_min=33 * IN, eye_max=53 * IN, actuator_max=69 * IN, shower_gpm=20.0,
            eye_gpm=0.4, minutes=15, tepid_f=(60, 100),
            source="ANSI/ISEA Z358.1-2014 (R2020): reached within 10 s (about 55 ft, 16.8 m, at a normal walk), on the "
                   "same level, unobstructed; immediately adjacent where the hazard is a strong acid or caustic "
                   "(Appendix B5, read here as within 3 m); the shower's column of water 82-96 in up, 20 in across at "
                   "60 in, its centre at least 16 in from any obstruction, 20 gpm for 15 min; the eyewash's heads "
                   "33-53 in up, 0.4 gpm for 15 min; tepid water, 60-100 F; the actuator at most 69 in up, on in 1 s; a "
                   "highly visible sign; activated weekly")
# The O2 monitor, its own frame: the back of its enclosure on the plane y = 0 (a post's face or a wall), its display to
# -y, the bottom of the enclosure at z = 0 (placed by the mount).
O2 = dict(
    model="PureAire 99028", box=(6.5 * IN, 4.5 * IN, 3.25 * IN), sensor=(64.0, 64.0, 90.0), strobe_d=102.0,
    strobe_h=127.0, alarm_low=19.5, alarm_high=18.0, range_pct=25.0, horn_db=90, price_usd=2375.0, strobe_usd=220.0,
    source="PureAire Monitoring Systems' O2 deficiency monitor with remote sensor (99028/99121/99117; its product page "
           "and manual): zirconium oxide sensor, 0-25 % O2, over 10 years' life, responds within 1 s; 3/4 in backlit "
           "LCD; alarms at 19.5 % and 18.0 %, two 2 A relays and a fault relay, a 90 dB horn built in, 4-20 mA, "
           "24 VDC; a 6.5 x 4.5 x 3.25 in polycarbonate enclosure (the product page; the manual says 5.125 x 3.15 x "
           "3.00 in); the sensor on a 10, 20 or 30 ft cable; $2,375-2,755. Its horn/strobe, P/N 42002, 24 VDC, "
           "$220-315. The sensor head's and the strobe's sizes aren't published: ours")
# argon is 1.38 times as dense as air: its sensor at PureAire's lowest, 12 in up; nitrogen (0.97) in the breathing zone,
# 5 ft (Emory's 4-6 ft for liquid nitrogen; Columbia's PureAire units at about 5 ft)
SENSOR_Z = {"argon": 12 * IN, "nitrogen": 60 * IN}
O2_RADIUS = 20 * 12 * IN                             # Columbia's "approximate 20-foot detection radius" per sensor
POST2 = dict(s=41.3, h=2300.0, base=203.0, base_t=9.5)   # the O2 monitor's post (ours): galvanized strut on a base
OSHA_O2 = 19.5                                       # 29 CFR 1910.134(b): oxygen deficient below 19.5 %
NFPA10_ABC = dict(travel_A=75 * 12 * IN, travel_B80=50 * 12 * IN, top_max=60 * IN, apart_m=3.0,
                  source="NFPA 10 (2022) Table 6.2.1.1 (Class A, ordinary hazard: 75 ft of travel, 11,250 ft2 per "
                         "unit, 1,500 ft2 per A) and Table 6.3.1.1 (Class B, extra hazard: an 80-B unit within 50 ft); "
                         "6.1.3.8.1 (40 lb or less: top at most 5 ft up). Kept 3 m from any Class D unit: ours")

S.MATS.update({
    "abc_red": (0.80, 0.07, 0.06, 1.0, 0.55),        # the fire-red enamel
    "brass": (0.78, 0.62, 0.30, 1.0, 0.8),
    "sym_green": (0.10, 0.60, 0.25, 1.0, 0.2),       # NFPA 10's letter symbols: A a green triangle,
    "sym_red": (0.82, 0.10, 0.10, 1.0, 0.2),         # B a red square,
    "sym_blue": (0.10, 0.30, 0.75, 1.0, 0.2),        # C a blue circle (D: the yellow star)
    "galv": (0.66, 0.68, 0.70, 1.0, 0.55),
    "shower_orange": (0.97, 0.45, 0.05, 1.0, 0.35),  # Guardian's orange ABS head and polyethylene covers
    "safety_green": (0.00, 0.55, 0.30, 1.0, 0.2),    # ISO 7010's safe-condition green
    "floor_green": (0.10, 0.55, 0.30, 1.0, 0.1),
    "drain": (0.35, 0.36, 0.37, 1.0, 0.4),
    "enclosure": (0.86, 0.87, 0.86, 1.0, 0.3),       # the monitor's grey-white enclosure
    "lcd": (0.04, 0.05, 0.05, 1.0, 0.6),
    "led_red": (0.95, 0.15, 0.10, 1.0, 0.4),
    "strobe": (0.92, 0.10, 0.08, 0.85, 0.7),
    "caution": (0.98, 0.80, 0.05, 1.0, 0.15),        # ANSI Z535's caution yellow
    "rack_blue": (0.10, 0.25, 0.55, 1.0, 0.4),
})


def _cq():
    import cadquery as cq
    return cq


def _letter_symbols(h=24.0, depth=0.4):
    """NFPA 10 Annex B's letter symbols side by side: A in a green triangle, B in a red square, C in a blue circle; flat,
    facing +z, the row centred on the origin. -> [(mesh, mat)]."""
    pv = S._pv()
    out = []
    gap = h * 1.25
    for i, (shape, letter, mat) in enumerate((("tri", "A", "sym_green"), ("sq", "B", "sym_red"), ("circ", "C", "sym_blue"))):
        cx = (i - 1) * gap
        if shape == "tri":
            pts = [(cx - h / 2, -h / 2), (cx + h / 2, -h / 2), (cx, h / 2)]
        elif shape == "sq":
            pts = [(cx - h * 0.42, -h * 0.42), (cx + h * 0.42, -h * 0.42), (cx + h * 0.42, h * 0.42), (cx - h * 0.42, h * 0.42)]
        else:
            pts = [(cx + h * 0.46 * math.cos(a), h * 0.46 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 28)[:-1]]
        out.append((_flat_poly(pts, depth), mat))
        t = _text(letter, h * 0.45, depth * 0.6)
        b = t.bounds
        dy = -h * 0.14 if shape == "tri" else 0.0
        out.append((t.translate((cx - (b[0] + b[1]) / 2, -(b[2] + b[3]) / 2 + dy, depth), inplace=False), "sign_white"))
    return out


# ================================================================================================ the Amerex B456
def abc_parts(lod: str = "full") -> dict:
    """{name: (PolyData, material)}: the Amerex B456 in its own frame (ABC): the red shell, the aluminium valve and its
    gauge, the squeeze lever over the carry handle, the pin and seal, the hose to the nozzle in its clip, the label with
    the A, B and C symbols, and the inspection tag. The proportions are Amerex's catalogue's (ABC); the valve, lever and
    hose are the family look of the B570 (safety.py), not measured off a B456."""
    cq = _cq()
    a = ABC
    R = a["d"] / 2
    zw, zd = a["z_wall"], a["z_dome"]
    p: dict = {}
    prof = [(0.0, 0.0), (R - 6.0, 0.0)]
    prof += [(R - 6.0 + 6.0 * math.sin(t), 6.0 - 6.0 * math.cos(t)) for t in np.linspace(0.2, math.pi / 2, 5)]
    prof += [(R, zw)]
    for t in np.linspace(0.1, math.pi / 2, 12):
        x = R * math.cos(t)
        if x < 19.0:
            break
        prof.append((x, zw + (zd - zw) * math.sin(t)))
    prof += [(19.0, zd), (0.0, zd)]
    _add(p, "B456 cylinder", _mesh(_revolve(prof), 0.2), "abc_red")
    # the valve: an aluminium collar and body, the gauge to the front, the outlet to the left
    zs, zg, zt = a["z_seat"], a["z_gauge"], a["z_top"]
    body = _cyl(16.0, zs - zd, (0, 0, zd)).fuse(_cyl(14.0, 46.0, (0, 0, zs)))
    body = body.fuse(_cyl(12.5, 22.0, (0, 2.0, zg), (0, -1, 0)))
    body = body.fuse(_cyl(8.5, 28.0, (-6.0, 0, zs + 26.0), (-1, 0, 0)))
    body = body.fuse(_box(-26.0, -8.0, zs + 38.0, 12.0, 8.0, zs + 50.0))
    _add(p, "B456 valve", _mesh(body), "alu")
    _add(p, "B456 gauge bezel", _mesh(_cyl(12.0, 3.0, (0, -20.0, zg), (0, -1, 0)).cut(
        _cyl(9.5, 4.0, (0, -19.5, zg), (0, -1, 0)))), "chrome")
    _add(p, "B456 gauge face", _mesh(_cyl(9.5, 1.0, (0, -20.0, zg), (0, -1, 0))), "label")
    arc = [(7.5 * math.cos(t), 7.5 * math.sin(t)) for t in np.radians(np.linspace(60, 120, 7))]
    arc += [(5.0 * math.cos(t), 5.0 * math.sin(t)) for t in np.radians(np.linspace(120, 60, 7))]
    _add(p, "B456 gauge arc", _on_face(_flat_poly(arc, 0.4), 0.0, zg, -21.0, -1), "gauge_green")
    _add(p, "B456 gauge needle", _on_face(_flat_poly([(-0.6, 0.0), (0.6, 0.0), (0.2, 7.0), (-0.2, 7.0)], 0.4), 0.0,
                                          zg, -21.4, -1), "print")
    # the squeeze lever over the carry handle, both to the right (+x), the lever's tip the highest point
    lever = [(-26.0, zs + 42.0), (-26.0, zs + 52.0), (-8.0, zs + 60.0), (50.0, zt - 14.0), (92.0, zt), (94.0, zt - 6.0),
             (50.0, zt - 23.0), (-4.0, zs + 49.0)]
    _add(p, "B456 lever", _mesh(_prism(lever, -7.0, 7.0)), "chrome")
    handle = [(8.0, zs + 32.0), (20.0, zs + 38.0), (58.0, zs + 26.0), (96.0, zs + 6.0), (96.0, zs - 2.0),
              (58.0, zs + 16.0), (18.0, zs + 26.0)]
    _add(p, "B456 handle", _mesh(_prism(handle, -8.0, 8.0)), "chrome")
    pin = _cyl(1.8, 22.0, (6.0, -11.0, zs + 45.0), (0, 1, 0))
    ring = cq.Solid.makeTorus(10.0, 1.2, cq.Vector(6.0, -12.0, zs + 67.0), cq.Vector(1, 0, 0))
    _add(p, "B456 pin", _mesh(pin.fuse(ring)), "steel")
    _add(p, "B456 seal", _mesh(_box(3.0, -15.0, zs + 49.0, 9.0, -12.0, zs + 58.0)), "seal")
    # the inspection tag on the pin's ring: the monthly checks are punched on it
    _add(p, "B456 tag", _mesh(_box(-4.0, -15.0, zs - 30.0, 22.0, -14.0, zs + 14.0)), "caution")
    # the hose: out of the valve to the left, down the left side to the nozzle, held in a clip at mid height
    zo = zs + 26.0
    hose = [(-34.0, 0.0, zo), (-58.0, -4.0, zo - 15.0), (-76.0, -8.0, zo - 60.0), (-80.0, -10.0, zo - 140.0),
            (-78.0, -10.0, zo - 190.0), (-76.0, -10.0, 196.0)]
    _add(p, "B456 hose", _tube(hose, 7.5), "rubber")
    noz = cq.Solid.makeCone(9.5, 6.0, 58.0, cq.Vector(-76.0, -10.0, 196.0), cq.Vector(0, 0, -1))
    _add(p, "B456 nozzle", _mesh(noz.fuse(_cyl(9.5, 14.0, (-76.0, -10.0, 196.0)))), "black_plastic")
    clip = _cyl(R + 2.0, 16.0, (0, 0, 186.0)).cut(_cyl(R + 0.2, 18.0, (0, 0, 185.0)))
    clip = clip.intersect(_box(-R - 30.0, -30.0, 180.0, -R * 0.5, 30.0, 210.0))
    clip = clip.fuse(_cyl(12.0, 16.0, (-76.0, -10.0, 186.0)).cut(_cyl(9.6, 18.0, (-76.0, -10.0, 185.0))))
    _add(p, "B456 clip", _mesh(clip), "black_plastic")
    # the label: white, a red header band, the A B C symbols, its words; the Amerex diamond under it
    rl = R + 0.25
    l0, l1 = 110.0, 312.0
    _add(p, "B456 label", _sector(rl, -70.0, 70.0, l0, l1, 0.35), "label")
    _add(p, "B456 label header", _sector(rl + 0.3, -70.0, 70.0, l1 - 26.0, l1 - 2.0, 0.2), "abc_red")
    for mesh, mat in _letter_symbols(20.0, 0.4):
        _add(p, f"B456 label {mat}", _on_cyl(mesh, rl + 0.45, 0.0, 252.0), mat)
    if lod == "full":
        for txt, h, z, mat in (("DRY CHEMICAL", 9.0, l1 - 19.0, "label"), ("FIRE EXTINGUISHER", 6.5, 222.0, "print"),
                               ("NOT FOR METAL FIRES", 5.5, 208.0, "abc_red")):
            t = _text(txt, h, 0.25)
            _add(p, f"B456 label text {mat}", _on_cyl(t, rl + 0.55, -t.bounds[1] / 2, z), mat)
        for i in range(8):
            zz = l0 + 10.0 + i * 10.0
            _add(p, "B456 label pictos", _sector(rl + 0.35, -60.0, 60.0, zz, zz + 3.0, 0.12, 8), "picto")
    dia = [(-38.0, 0.0), (0.0, -10.0), (38.0, 0.0), (0.0, 10.0)]
    _add(p, "B456 logo", _on_cyl(_flat_poly(dia, 0.3), R + 0.3, 0.0, 70.0), "print")
    _add(p, "B456 logo white", _on_cyl(_flat_poly([(x * 0.9, y * 0.75) for x, y in dia], 0.5), R + 0.35, 0.0, 70.0),
         "label")
    return p


def abc_sign_parts() -> dict:
    """The ordinary unit's signs, flat, facing -y, bottom centre at the origin: a red 7 x 10 in FIRE EXTINGUISHER sign
    with a white arrow down, and under it a 7 x 5 in placard (ours): the A B C symbols and NOT FOR METAL FIRES / USE
    THE YELLOW CLASS D. Red on white where the Class D signs are white with a yellow star."""
    pv = S._pv()
    p: dict = {}
    w, h, t = S.SIGN["w"], S.SIGN["h"], S.SIGN["t"]
    hp = 5 * IN
    gap = 20.0
    z0 = hp + gap                                     # the big sign's bottom
    _add(p, "abc sign", pv.Box(bounds=(-w / 2, w / 2, 0.0, t, z0, z0 + h)).triangulate(), "sign_red")
    for txt, hh, z in (("FIRE", 26.0, z0 + h - 40.0), ("EXTINGUISHER", 14.0, z0 + h - 64.0)):
        tx = _text(txt, hh, 0.4)
        sc = min(1.0, (w - 16.0) / tx.bounds[1])
        tx = tx.scale((sc, 1.0, 1.0), inplace=False)
        _add(p, "abc sign white", _on_face(tx, -tx.bounds[1] / 2, z, -0.4, -1), "sign_white")
    arrow = [(-14.0, 60.0), (14.0, 60.0), (14.0, 120.0), (-14.0, 120.0)]
    head = [(-40.0, 62.0), (40.0, 62.0), (0.0, 12.0)]
    for poly in (arrow, head):
        _add(p, "abc sign white", _on_face(_flat_poly(poly, 0.4), 0.0, z0 + 10.0, -0.4, -1), "sign_white")
    _add(p, "abc placard", pv.Box(bounds=(-w / 2, w / 2, 0.0, t, 0.0, hp)).triangulate(), "sign_white")
    _add(p, "abc placard band", pv.Box(bounds=(-w / 2, w / 2, -0.3, 0.0, hp - 30.0, hp)).triangulate(), "sign_red")
    tx = _text("ABC ONLY", 14.0, 0.4)
    _add(p, "abc placard white", _on_face(tx, -tx.bounds[1] / 2, hp - 23.0, -0.6, -1), "sign_white")
    for mesh, mat in _letter_symbols(24.0, 0.4):
        _add(p, f"abc placard {mat}", _on_face(mesh, 0.0, hp - 52.0, -0.5, -1), mat)
    for txt, hh, z, mat in (("NOT FOR METAL FIRES", 8.0, 24.0, "sign_red"), ("USE THE YELLOW CLASS D", 6.0, 8.0, "print")):
        tx = _text(txt, hh, 0.4)
        sc = min(1.0, (w - 14.0) / tx.bounds[1])
        tx = tx.scale((sc, 1.0, 1.0), inplace=False)
        _add(p, "abc placard red" if mat == "sign_red" else "abc placard print", _on_face(tx, -tx.bounds[1] / 2, z, -0.4,
                                                                                          -1), mat)
    return p


# a B456 on a rack upright: the top of the unit at 1,200 mm (NFPA 10: at most 5 ft for 40 lb or less; the handle within
# the ADA's 48 in reach), its hook on a 3 mm steel plate clamped to the upright's face, the signs over it
ABC_TOP_Z = 1200.0
RACK_UP = 76.0                                        # warehouse.RACK["upright"]


def rack_parts(lod: str = "full") -> dict:
    """A B456 on a rack upright, in a frame whose y = 0 plane is the upright's aisle face and -y the aisle, the origin on
    the floor at the upright's centre line: the clamp plate and its two U-bolts, the hook, the unit, the signs at
    1,750 mm, and a stub of the upright itself (blue, as warehouse.py draws the racking) for the sheet."""
    pv = S._pv()
    from scene import T
    p: dict = {}
    R = ABC["d"] / 2
    zb = ABC_TOP_Z - ABC["z_top"]                     # the unit's bottom
    plate = pv.Box(bounds=(-60.0, 60.0, -3.0, 0.0, zb + 240.0, zb + 470.0)).triangulate()
    _add(p, "abc mount plate", plate, "steel")
    ub = []
    for z in (zb + 270.0, zb + 440.0):
        ub.append(_tube([(-45.0, -3.0, z), (-45.0, 40.0, z), (-42.0, 82.0, z), (42.0, 82.0, z), (45.0, 40.0, z),
                         (45.0, -3.0, z)], 4.0, 10))
    _add(p, "abc mount u-bolts", _merge(ub), "steel")
    hook = pv.Box(bounds=(-22.0, 22.0, -R - 18.0, -3.0, zb + ABC["z_seat"] - 3.0, zb + ABC["z_seat"])).triangulate()
    hook2 = pv.Box(bounds=(-22.0, 22.0, -3.0 - 2.5, -3.0, zb + ABC["z_seat"] - 110.0, zb + ABC["z_seat"])).triangulate()
    _add(p, "abc hook", _merge([hook, hook2]), "abc_red")
    M = T((0.0, -3.0 - R - 8.0, zb))
    for name, (mesh, mat) in abc_parts(lod).items():
        _add(p, name, mesh.transform(M, inplace=False), mat)
    for name, (mesh, mat) in abc_sign_parts().items():
        _add(p, name, mesh.translate((0.0, -3.0 - S.SIGN["t"], 1750.0), inplace=False), mat)
    return p


def upright_stub(h=2400.0) -> dict:
    pv = S._pv()
    return {"rack upright": (pv.Box(bounds=(-RACK_UP / 2, RACK_UP / 2, 0.0, 76.0, 0.0, h)).triangulate(), "rack_blue")}


# ================================================================================================ the shower
def shower_parts(lod: str = "full") -> dict:
    """{name: (PolyData, material)}: the Guardian G1902 in its own frame (SHOWER): the cast aluminium floor flange, the
    galvanized column in its orange covers, the top tee and inlet, the shower arm out to the orange ABS head, the
    stay-open ball valve with its actuating arm, pull rod and triangle handle; the eyewash's branch, its two heads with
    their flip-top covers in the stainless bowl, its ball valve and flag handle, the bowl's waste down to its outlet; the
    green identification sign on the column; and (ours) the drain grate and the green floor square under the spray."""
    cq = _cq()
    pv = S._pv()
    s = SHOWER
    r, rc = s["pipe_od"] / 2, s["cover_od"] / 2
    p: dict = {}
    fl = _cyl(s["flange_d"] / 2, 14.0).fuse(_cyl(r + 10.0, 50.0, (0, 0, 14.0)))
    for k in range(4):
        a = math.radians(45.0 + 90.0 * k)
        fl = fl.cut(_cyl(5.6, 20.0, (3.8125 * IN * math.cos(a), 3.8125 * IN * math.sin(a), -2.0)))
    _add(p, "shower flange", _mesh(fl), "alu")
    _add(p, "shower anchors", _merge([pv.Cylinder(center=(3.8125 * IN * math.cos(math.radians(45.0 + 90.0 * k)),
                                                          3.8125 * IN * math.sin(math.radians(45.0 + 90.0 * k)), 18.0),
                                                  direction=(0, 0, 1), radius=7.0, height=8.0, resolution=6).triangulate()
                                      for k in range(4)]), "steel")
    za, zt = s["z_arm"], s["z_top"]
    col = _cyl(r, za - 14.0, (0, 0, 14.0)).fuse(_cyl(r + 6.0, 80.0, (0, 0, za - 40.0)))      # the column, the top tee
    col = col.fuse(_cyl(r + 6.0, 60.0, (0, 0, za), (0, -1, 0)))
    _add(p, "shower column", _mesh(col), "galv")
    ey = s["eye_z"]
    covers = [_cyl(rc, za - 60.0 - (ey + 120.0), (0, 0, ey + 120.0)), _cyl(rc, ey - 220.0 - 90.0, (0, 0, 90.0))]
    _add(p, "shower covers", _mesh(covers[0].fuse(covers[1])), "shower_orange")
    # the shower arm out to -y at za, an elbow down to the head (its underside at head_z, its centre at head_y)
    hy, hz = s["head_y"], s["head_z"]
    arm = _cyl(r, -hy, (0, 0, za), (0, -1, 0)).fuse(_cyl(r + 5.0, 60.0, (0, hy, za - 30.0)))
    arm = arm.fuse(_cyl(r, za - (hz + 60.0), (0, hy, hz + 60.0)))
    _add(p, "shower arm", _mesh(arm), "galv")
    head = cq.Solid.makeCone(s["head_d"] / 2, 28.0, 60.0, cq.Vector(0, hy, hz), cq.Vector(0, 0, 1))
    head = head.fuse(_cyl(s["head_d"] / 2, 8.0, (0, hy, hz)))
    _add(p, "shower head", _mesh(head, 0.4), "shower_orange")
    holes = [pv.Cylinder(center=(rr * math.cos(t), hy + rr * math.sin(t), hz - 0.4), direction=(0, 0, 1), radius=3.0,
                         height=1.2, resolution=8).triangulate()
             for rr in (30.0, 60.0, 90.0) for t in np.linspace(0, 2 * math.pi, int(rr / 5))[:-1]]
    _add(p, "shower head holes", _merge(holes), "black_plastic")
    # the 1 in stay-open ball valve on the arm, its stainless actuating arm rising 5-3/4 in over the arm's centre line
    # and reaching forward, the 29 in pull rod down from its tip, the triangle handle 23-1/2 in under the arm
    vy, ry = -160.0, -400.0
    _add(p, "shower valve", _mesh(_box(-24.0, vy - 32.0, za - 24.0, 24.0, vy + 32.0, za + 24.0)), "brass")
    act = _tube([(0.0, vy, za + 24.0), (0.0, vy - 20.0, zt - 10.0), (0.0, (vy + ry) / 2, zt), (0.0, ry, zt - 6.0)],
                6.0, 10)
    _add(p, "shower actuating arm", act, "steel")
    rz = s["rod_z"]
    _add(p, "shower pull rod", pv.Cylinder(center=(0, ry, (zt - 6.0 + rz + 150.0) / 2), direction=(0, 0, 1),
                                           radius=4.0, height=zt - 6.0 - rz - 150.0, resolution=10).triangulate(),
         "steel")
    tri = [(-90.0, rz + 6.0), (90.0, rz + 6.0), (0.0, rz + 150.0)]
    _add(p, "shower handle", _tube([(x, ry, z) for x, z in tri + [tri[0]]], 6.0, 10), "steel")
    # the eyewash: a branch from the column at its heads' height, the two heads in the stainless bowl, flip-top covers,
    # the 1/2 in ball valve beside the bowl and the cast aluminium flag handle beyond it; the bowl's waste
    by = s["bowl_y"]
    zb = ey - 40.0                                         # the bowl's rim
    br = _cyl(r * 0.55, -by, (0, 0, ey - 90.0), (0, -1, 0))
    br = br.fuse(_cyl(r * 0.55, s["valve_x"], (0, by, ey - 90.0), (1, 0, 0)))
    _add(p, "eyewash branch", _mesh(br), "galv")
    bowl_o = cq.Solid.makeCone(36.0, s["bowl_d"] / 2, 80.0, cq.Vector(0, by, zb - 80.0), cq.Vector(0, 0, 1))
    bowl_i = cq.Solid.makeCone(30.0, s["bowl_d"] / 2 - 3.0, 78.0, cq.Vector(0, by, zb - 77.0), cq.Vector(0, 0, 1))
    _add(p, "eyewash bowl", _mesh(bowl_o.cut(bowl_i), 0.4), "steel")
    g = s["eye_gap"] / 2
    for dx in (-g, g):
        hd = _cyl(9.0, 70.0, (dx, by, ey - 90.0)).fuse(cq.Solid.makeCone(9.0, 15.0, 20.0, cq.Vector(dx, by, ey - 20.0),
                                                                         cq.Vector(0, 0, 1)))
        _add(p, "eyewash heads", _mesh(hd), "shower_orange")
        cap = _cyl(17.0, 4.0, (dx, by, ey)).rotate(cq.Vector(dx, by - 17.0, ey), cq.Vector(1, 0, 0), -70.0)
        _add(p, "eyewash covers", _mesh(cap), "shower_orange")
    _add(p, "eyewash manifold", _mesh(_box(-g, by - 7.0, ey - 97.0, g, by + 7.0, ey - 83.0)), "galv")
    vx = s["valve_x"]
    _add(p, "eyewash valve", _mesh(_box(vx - 20.0, by - 22.0, ey - 115.0, vx + 20.0, by + 22.0, ey - 65.0)), "brass")
    flag = _box(vx, by - 8.0, ey - 70.0, vx + s["flag"], by + 8.0, ey - 60.0)
    flag = flag.fuse(_box(vx + s["flag"] - 30.0, by - 55.0, ey - 75.0, vx + s["flag"], by + 55.0, ey - 55.0))
    _add(p, "eyewash flag", _mesh(flag), "alu")
    waste = _cyl(r * 0.55, zb - 80.0 - s["waste_z"], (0, by, s["waste_z"])).fuse(
        _cyl(r * 0.55, -by, (0, 0, s["waste_z"]), (0, -1, 0)))
    _add(p, "eyewash waste", _mesh(waste), "galv")
    # its green identification sign on the column, both faces printed (EMERGENCY SHOWER / EYE WASH, ISO 7010 E012/E011)
    sw, sh = 10 * IN, 7 * IN
    zs0 = 1830.0
    _add(p, "shower sign", pv.Box(bounds=(-sw / 2, sw / 2, -rc - 3.0, -rc, zs0, zs0 + sh)).triangulate(), "safety_green")
    _add(p, "shower sign", pv.Box(bounds=(-sw / 2, sw / 2, rc, rc + 3.0, zs0, zs0 + sh)).triangulate(), "safety_green")
    for side, yy in ((-1, -rc - 3.0), (1, rc + 3.0)):
        for txt, hh, z in (("EMERGENCY", 15.0, zs0 + sh - 26.0), ("SHOWER", 15.0, zs0 + sh - 48.0),
                           ("EYE WASH", 15.0, zs0 + 14.0)):
            t = _text(txt, hh, 0.4)
            sc = min(1.0, (sw * 0.55 - 14.0) / t.bounds[1])
            t = t.scale((sc, 1.0, 1.0), inplace=False)
            _add(p, "shower sign white", _on_face(t, (-sw / 2 + 10.0) if side < 0 else (sw / 2 - 10.0), z, yy, side),
                 "sign_white")
        px = (sw / 2 - 52.0) if side < 0 else -(sw / 2 - 52.0)
        sq = _flat_poly([(-40.0, -40.0), (40.0, -40.0), (40.0, 40.0), (-40.0, 40.0)], 0.4)
        _add(p, "shower sign white", _on_face(sq, px, zs0 + sh / 2, yy, side), "sign_white")
        fig = [(-7.0, -32.0), (7.0, -32.0), (7.0, 4.0), (-7.0, 4.0)]
        headc = [(10.0 * math.cos(t), 14.0 + 10.0 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 18)[:-1]]
        drops = [[(x - 2.5, 28.0), (x + 2.5, 28.0), (x, 35.0)] for x in (-20.0, -10.0, 0.0, 10.0, 20.0)]
        for poly in [fig, headc] + drops:
            _add(p, "shower sign green", _on_face(_flat_poly(poly, 0.4), px, zs0 + sh / 2, yy + 0.4 * side, side),
                 "safety_green")
    # the floor (ours): a 300 mm drain grate under the spray and a 36 in green square round it, kept clear
    gs = 300.0
    _add(p, "shower drain", pv.Box(bounds=(-gs / 2, gs / 2, hy - gs / 2, hy + gs / 2, 0.0, 2.0)).triangulate(), "drain")
    slots = [pv.Box(bounds=(-gs / 2 + 20.0, gs / 2 - 20.0, hy - gs / 2 + 20.0 + 26.0 * k, hy - gs / 2 + 32.0 + 26.0 * k,
                            1.5, 2.6)).triangulate() for k in range(10)]
    _add(p, "shower drain slots", _merge(slots), "floor_black")
    k = 36 * IN
    tape = []
    for (xa, xb, ya, yb) in ((-k / 2, k / 2, hy - k / 2, hy - k / 2 + 50), (-k / 2, k / 2, hy + k / 2 - 50, hy + k / 2),
                             (-k / 2, -k / 2 + 50, hy - k / 2, hy + k / 2), (k / 2 - 50, k / 2, hy - k / 2, hy + k / 2)):
        tape.append(pv.Box(bounds=(xa, xb, ya, yb, 0.0, 1.2)).triangulate())
    _add(p, "shower floor square", _merge(tape), "floor_green")
    return p


def mixer_parts(z_bottom: float = 2560.0) -> dict:
    """The thermostatic mixing valve's surface cabinet (MIXER["cab"], ours) on the supply over the column, in the
    shower's frame: its back to +y, hung on a strut from the supply; the hot and cold feeds into its top, the tempered
    line out of its bottom to the column's top inlet."""
    pv = S._pv()
    cw, ch, cd = MIXER["cab"]
    p: dict = {}
    zb = z_bottom
    y1 = cd / 2
    _add(p, "mixer cabinet", pv.Box(bounds=(-cw / 2, cw / 2, y1 - cd, y1, zb, zb + ch)).triangulate(), "steel")
    _add(p, "mixer door", pv.Box(bounds=(-cw / 2 + 12.0, cw / 2 - 12.0, y1 - cd - 2.0, y1 - cd, zb + 12.0,
                                         zb + ch - 12.0)).triangulate(), "steel")
    _add(p, "mixer label", pv.Box(bounds=(-110.0, 110.0, y1 - cd - 2.6, y1 - cd - 2.0, zb + ch - 80.0,
                                          zb + ch - 30.0)).triangulate(), "safety_green")
    t = _text("TEMPERED WATER", 13.0, 0.3)
    _add(p, "mixer print", _on_face(t, -t.bounds[1] / 2, zb + ch - 62.0, y1 - cd - 2.9, -1), "sign_white")
    feeds = [pv.Cylinder(center=(x, 0.0, zb + ch + 150.0), direction=(0, 0, 1), radius=17.0, height=300.0,
                         resolution=12).triangulate() for x in (-90.0, 90.0)]
    _add(p, "mixer feeds", _merge(feeds), "galv")
    za = SHOWER["z_arm"]
    _add(p, "mixer feeds", pv.Cylinder(center=(0.0, 0.0, (za + 40.0 + zb) / 2), direction=(0, 0, 1), radius=21.0,
                                       height=zb - za - 40.0, resolution=12).triangulate(), "galv")
    return p


# ================================================================================================ the O2 monitor
def o2_parts(gas: str = "argon", lead: float = 0.0) -> dict:
    """{name: (PolyData, material)}: the O2 monitor in its own frame (O2): its enclosure on the plane y = 0 (the back),
    the backlit display reading 20.9 and the two alarm lamps, the conduit hub; the horn/strobe on its own box 300 mm
    over it; and for argon the remote sensor `lead` mm under the enclosure's bottom on its conduit (0: no remote
    sensor: the sensor is in the enclosure, in the breathing zone, for nitrogen)."""
    pv = S._pv()
    o = O2
    w, h, d = o["box"]
    p: dict = {}
    _add(p, "O2 enclosure", pv.Box(bounds=(-w / 2, w / 2, -d, 0.0, 0.0, h)).triangulate(), "enclosure")
    _add(p, "O2 lid", pv.Box(bounds=(-w / 2 + 3.0, w / 2 - 3.0, -d - 2.0, -d, 3.0, h - 3.0)).triangulate(), "enclosure")
    _add(p, "O2 display", pv.Box(bounds=(-45.0, 45.0, -d - 3.0, -d - 2.0, h - 58.0, h - 26.0)).triangulate(), "lcd")
    t = _text("20.9", 19.0, 0.3)
    _add(p, "O2 digits", _on_face(t, -t.bounds[1] / 2, h - 51.0, -d - 3.3, -1), "led_red")
    t = _text("OXYGEN %", 7.0, 0.3)
    _add(p, "O2 print", _on_face(t, -t.bounds[1] / 2, h - 69.0, -d - 2.3, -1), "print")
    for i, (txt, x) in enumerate((("19.5", -35.0), ("18.0", 35.0))):
        _add(p, f"O2 lamp {txt}", pv.Cylinder(center=(x, -d - 3.0, 27.0), direction=(0, -1, 0), radius=6.0, height=3.0,
                                               resolution=16).triangulate(), "led_red" if i else "caution")
        tt = _text(txt, 6.0, 0.3)
        _add(p, "O2 print", _on_face(tt, x - tt.bounds[1] / 2, 10.0, -d - 2.3, -1), "print")
    t = _text("O2 MONITOR", 8.0, 0.3)
    _add(p, "O2 print", _on_face(t, -t.bounds[1] / 2, h - 17.0, -d - 2.3, -1), "print")
    _add(p, "O2 hub", pv.Cylinder(center=(0.0, -d / 2, -10.0), direction=(0, 0, 1), radius=11.0, height=20.0,
                                  resolution=14).triangulate(), "galv")
    # the horn/strobe (PureAire 42002), over the enclosure on its own box, its lens red
    zs = h + 300.0
    _add(p, "O2 strobe base", pv.Box(bounds=(-55.0, 55.0, -70.0, 0.0, zs, zs + 50.0)).triangulate(), "enclosure")
    _add(p, "O2 strobe lens", pv.Cylinder(center=(0.0, -35.0, zs + 50.0 + (o["strobe_h"] - 50.0) / 2),
                                          direction=(0, 0, 1), radius=o["strobe_d"] / 2 - 10.0,
                                          height=o["strobe_h"] - 50.0, resolution=24).triangulate(), "strobe")
    _add(p, "O2 horn", pv.Cylinder(center=(0.0, -72.0, zs + 25.0), direction=(0, -1, 0), radius=20.0, height=5.0,
                                   resolution=18).triangulate(), "black_plastic")
    _add(p, "O2 conduit", pv.Cylinder(center=(w / 2 - 20.0, -12.0, (h + zs) / 2), direction=(0, 0, 1), radius=7.0,
                                      height=zs - h, resolution=10).triangulate(), "galv")
    if lead > 0:                                           # the remote sensor down its conduit, its gauze down
        sw, sh, sd = o["sensor"]
        zh = -lead - sh                                    # the sensor head's bottom, from the enclosure's bottom
        _add(p, "O2 conduit", pv.Cylinder(center=(0.0, -d / 2, (zh + sh - 20.0) / 2), direction=(0, 0, 1), radius=7.0,
                                          height=-(zh + sh) - 20.0, resolution=10).triangulate(), "galv")
        _add(p, "O2 sensor", pv.Box(bounds=(-sw / 2, sw / 2, -d / 2 - sd / 2, -d / 2 + sd / 2, zh, zh + sh)).triangulate(),
             "enclosure")
        _add(p, "O2 sensor gauze", pv.Cylinder(center=(0.0, -d / 2, zh - 10.0), direction=(0, 0, 1), radius=18.0,
                                               height=20.0, resolution=18).triangulate(), "steel")
    return p


def o2_sign_parts(gas: str = "argon") -> dict:
    """A 7 x 10 in ANSI Z535 CAUTION sign, flat, facing -y, bottom centre at the origin: ARGON (or NITROGEN) IN USE /
    OXYGEN MONITOR / IF THE ALARM SOUNDS LEAVE THE AREA."""
    pv = S._pv()
    p: dict = {}
    w, h, t = S.SIGN["w"], S.SIGN["h"], S.SIGN["t"]
    _add(p, "o2 sign", pv.Box(bounds=(-w / 2, w / 2, 0.0, t, 0.0, h)).triangulate(), "sign_white")
    _add(p, "o2 sign band", pv.Box(bounds=(-w / 2, w / 2, -0.3, 0.0, h - 48.0, h)).triangulate(), "caution")
    tri = [(-17.0, -14.0), (17.0, -14.0), (0.0, 16.0)]
    _add(p, "o2 sign print", _on_face(_flat_poly(tri, 0.4), -w / 2 + 28.0, h - 24.0, -0.4, -1), "print")
    tx = _text("CAUTION", 20.0, 0.4)
    _add(p, "o2 sign print", _on_face(tx, -w / 2 + 50.0, h - 34.0, -0.4, -1), "print")
    lines = ((f"{gas.upper()} IN USE", 13.0, h - 80.0), ("OXYGEN MONITOR", 11.0, h - 108.0),
             ("IF THE ALARM SOUNDS", 8.5, 70.0), ("LEAVE THE AREA", 8.5, 54.0), (f"ALARM {O2['alarm_low']} % O2", 7.0, 24.0))
    for txt, hh, z in lines:
        tx = _text(txt, hh, 0.4)
        sc = min(1.0, (w - 16.0) / tx.bounds[1])
        tx = tx.scale((sc, 1.0, 1.0), inplace=False)
        _add(p, "o2 sign print", _on_face(tx, -tx.bounds[1] / 2, z, -0.4, -1), "print")
    return p


O2_BOX_Z = 1400.0                                    # the enclosure's bottom: its display at eye level, 1.5-1.6 m


def o2_post_parts(gas: str = "argon", post: bool = True) -> dict:
    """An O2 monitor on its post (ours, POST2: galvanized strut on a base plate, anchored), or on a wall (post=False), in
    a frame whose origin is the post's axis on the floor, front -y: the monitor at O2_BOX_Z, the horn/strobe over it,
    the CAUTION sign over that, and for argon the remote sensor at 12 in (SENSOR_Z) on its conduit."""
    pv = S._pv()
    from scene import T
    p: dict = {}
    s = POST2["s"]
    yf = -s / 2 if post else 0.0
    if post:
        bp = pv.Box(bounds=(-POST2["base"] / 2, POST2["base"] / 2, -POST2["base"] / 2, POST2["base"] / 2, 0.0,
                            POST2["base_t"])).triangulate()
        ch = pv.Box(bounds=(-s / 2, s / 2, -s / 2, s / 2, POST2["base_t"], POST2["h"])).triangulate()
        _add(p, "o2 post", _merge([bp, ch]), "galv")
        _add(p, "o2 post slot", pv.Box(bounds=(-11.0, 11.0, -s / 2 - 0.4, -s / 2 + 0.2, POST2["base_t"] + 30.0,
                                               POST2["h"] - 30.0)).triangulate(), "floor_black")
        _add(p, "o2 post anchors", _merge([pv.Cylinder(center=(x, y, POST2["base_t"] + 6.0), direction=(0, 0, 1),
                                                       radius=8.0, height=12.0, resolution=6).triangulate()
                                           for x in (-75.0, 75.0) for y in (-75.0, 75.0)]), "steel")
    zs = SENSOR_Z[gas]
    # argon: the enclosure at eye level, the remote sensor's head centred at zs; nitrogen: the sensor is in the
    # enclosure, so the enclosure's centre is at zs
    zb = O2_BOX_Z if gas == "argon" else zs - O2["box"][1] / 2
    lead = zb - zs - O2["sensor"][1] / 2 if gas == "argon" else 0.0
    for name, (mesh, mat) in o2_parts(gas, lead).items():
        _add(p, name, mesh.translate((0.0, yf, zb), inplace=False), mat)
    zsign = zb + O2["box"][1] + 300.0 + O2["strobe_h"] + 30.0         # over the strobe, clear of its conduit
    for name, (mesh, mat) in o2_sign_parts(gas).items():
        _add(p, name, mesh.translate((0.0, yf - S.SIGN["t"], zsign), inplace=False), mat)
    return p


# ================================================================================================ where they go
# The ICP-MS station at notes/icpms.md's suggestion (the south row's east end, facing north; not on setup_lab's floor
# yet): the bench with the ICP-MS at the west end, the hood at the east end, the dewar behind the bench; its two MiR250
# docks, in front of the SPS 4 and in front of the hood's open half, on the south row's dock line.
ICPMS = dict(bench=(7850.0, 9650.0, -6238.0 - 760.0, -6238.0), hood=(9750.0, 11580.0, -6238.0 - 813.0, -6238.0),
             dewar=(8750.0, -7500.0, 254.0), docks={"icpms_sps": 9340.0, "icpms_hood": 10260.0})
ROOF_Z = 10970.0                                     # setup_lab.Z_CEIL: the roof steel, where the water comes from
ICPMS_ON_FLOOR = False                               # set True (or put "icpms" in setup_lab.FLOOR_PLAN) when it's placed

# station, kind, x, y, face (the way its front looks, deg: 0 is -y, 90 is +x, 180 is +y, -90 is -x), what, extra. Each
# spot is the nearest to its hazard that clears everything (place_search below), then rounded.
PLACES = [
    # the building's ordinary units, on the racking's uprights where the aisle meets it, facing the aisle: 3 m or more
    # from every Class D unit, and never the nearest extinguisher to a powder station (abc_check)
    ("building", "abc", -11833.0, -3714.0, 90.0, "the aisle's west end (rack W's upright)", {}),
    ("building", "abc", 11833.0, -6457.0, -90.0, "the south-east (rack E's upright), by the ICP-MS station", {}),
    ("building", "abc", -28.0, 2800.0, 0.0, "behind the Shuttles (rack N's upright)", {}),
    # an eyewash and drench shower beside each hood with acids or caustics, the side away from any powder
    ("fumehood", "shower", 450.0, -7300.0, 180.0, "the ducted fume hood (Weck's reagent: KMnO4 and NaOH)", {}),
    ("icpms", "shower", 10950.0, -5750.0, 180.0, "the ICP-MS station's hood (HNO3, HCl), at its suggested spot",
     {"icpms": True}),
    # O2 monitors: one where each gas is stored or used; argon's sensor low, nitrogen's in the breathing zone
    ("argon cylinders", "o2", -9500.0, -700.0, 0.0, "the argon cylinder manifold", {"gas": "argon"}),
    ("glovebox", "o2", -7950.0, -500.0, 0.0, "the glovebox's argon", {"gas": "argon"}),
    ("repowder", "o2", -3440.0, -350.0, 0.0, "the rePowder's argon (behind it, where the line comes down)",
     {"gas": "argon"}),
    ("aconity", "o2", 7500.0, 0.0, 0.0, "the Aconity MIDI's argon (behind it, where the line comes down)",
     {"gas": "argon"}),
    ("ded", "o2", 4100.0, -7350.0, 180.0, "the DED's argon (behind it, where the line comes down)", {"gas": "argon"}),
    ("eos_m400", "o2", -7000.0, -9300.0, 180.0, "the EOS M 400-4's argon", {"gas": "argon"}),
    ("icpms", "o2", 9300.0, -7500.0, 0.0, "the ICP-MS station's 180 L liquid argon dewar", {"gas": "argon",
                                                                                           "icpms": True}),
    # nitrogen's on Shuttle 1's side in front of the generator: beside it, its display would face the generator 92 mm off
    ("n2 generator", "o2wall", 1415.0, -300.0, 90.0, "the N2 generator between the Shuttles (on Shuttle 1's side, "
                                                     "in front of it)", {"gas": "nitrogen"}),
]
# where each hazard is: the point a person would be at (the hoods' fronts), or where the gas comes in
HAZARDS = {
    "fumehood": (1500.0, -6000.0), "icpms": (10665.0, -6000.0),
    "argon cylinders": (-9510.0, -162.0), "glovebox": (-7100.0, -632.0), "repowder": (-3440.0, -632.0),
    "aconity": (7500.0, -632.0), "ded": (4100.0, -7038.0), "eos_m400": (-9450.0, -9763.0),
    "icpms dewar": (8750.0, -7500.0), "n2 generator": (1815.0, 400.0),
}
POWDER = ("glovebox", "repowder", "sieve_cell", "vlm", "vlm2", "aconity", "packaging", "ded", "eos_m400")


def _rot(face_deg):
    from scene import R
    return R((0, 0, 1), face_deg)


def _turn(rect_local, x, y, face):
    """A local plan rectangle (x0, x1, y0, y1) turned by face (a multiple of 90) and moved to (x, y) -> world."""
    x0, x1, y0, y1 = rect_local
    c = [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]
    a = math.radians(face)
    w = [(x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a)) for px, py in c]
    xs, ys = [q[0] for q in w], [q[1] for q in w]
    return (min(xs), max(xs), min(ys), max(ys))


def place_rects(kind, x, y, face) -> dict:
    """World plan rectangles of a unit: what stands on the floor or sticks out ("solid"), and the floor it needs clear
    ("clear": the shower's spray circle, 16 in round its centre, as its square; the user's floor)."""
    if kind == "abc":
        return dict(solid=_turn((-130.0, 130.0, -ABC["d"] - 60.0, 0.0), x, y, face))
    if kind == "shower":
        s = SHOWER
        sol = _turn((-s["flange_d"] / 2 - 10.0, s["bowl_d"] / 2 + 80.0, s["head_y"] - s["head_d"] / 2,
                     s["flange_d"] / 2 + 10.0), x, y, face)
        c = ANSI["spray_clear"]
        cl = _turn((-c, c, s["head_y"] - c, s["head_y"] + c), x, y, face)
        return dict(solid=sol, clear=cl)
    if kind == "o2":
        b = POST2["base"] / 2
        return dict(solid=_turn((-max(b, O2["box"][0] / 2 + 10.0), max(b, O2["box"][0] / 2 + 10.0),
                                 -POST2["s"] / 2 - O2["box"][2] - 80.0, b), x, y, face))
    if kind == "o2wall":
        return dict(solid=_turn((-O2["box"][0] / 2 - 10.0, O2["box"][0] / 2 + 10.0, -O2["box"][2] - 80.0, 0.0), x, y,
                                face))
    raise ValueError(kind)


def _icpms_rects():
    r = {"ICP-MS bench (suggested)": ICPMS["bench"], "ICP-MS hood (suggested)": ICPMS["hood"]}
    dx, dy, dd = ICPMS["dewar"]
    r["ICP-MS dewar (suggested)"] = (dx - dd / 2, dx + dd / 2, dy - dd / 2, dy + dd / 2)
    return r


def obstacles() -> dict:
    """safety_render.obstacles (machines, racking, ch. 5's fixtures, docked MiR250s with their units, lanes, pivot
    circles, target posts' feet, the aisle, the Shuttles' fronts, the rePowder's plates), with the ICP-MS station at its
    suggested spot and its two docked MiR250s, and every Class D unit (solid and keep-clear area) as placed."""
    import safety_render as SR
    fl = SR.floor()
    fp = S.mir_footprint()
    ob = SR.obstacles(fl, fp)
    ob["rects"].update(_icpms_rects())
    for k, xd in ICPMS["docks"].items():
        for i, r in enumerate(SR.mir_rects(fp)):
            ob["mirs"][f"{k}{'+unit' if i else ''}"] = SR._to_world(r, xd, -5868.0, 180.0)
    ob["classd"] = []
    for st, kind, x, y, face, _ in S.PLACES:
        pr = SR.place_rects(kind, x, y, face)
        ob["classd"].append(pr["solid"])
        if "clear" in pr:
            ob["classd"].append(pr["clear"])
    return ob


def spot_hits(kind, x, y, face, ob, placed=()) -> list:
    """What a unit at (x, y) facing `face` hits (empty: the spot is good). The O2 posts and the showers keep to the
    floor like the Class D posts; a unit on the racking or a Shuttle's side is checked for what stands in front of it."""
    import safety_render as SR
    pr = place_rects(kind, x, y, face)
    sol, cl = pr["solid"], pr.get("clear")
    on_rack = kind in ("abc", "o2wall")
    h = []
    for k, rr in ob["rects"].items():
        if on_rack and (k.startswith("rack") or k in ("vlm", "vlm2")):
            continue                                          # it hangs on these
        if SR._rect_hit(sol, rr, 50.0):
            h.append(f"machine {k}")
    h += [f"docked MiR {k}" for k, rr in ob["mirs"].items() if SR._rect_hit(sol, rr, SR.MARGIN)]
    h += [f"lane {k}" for k, rr in ob["lanes"].items() if SR._rect_hit(sol, rr, SR.MARGIN)]
    h += [f"pivot {k}" for k, (c, r) in ob["circles"].items() if SR._rect_circle(sol, c, r + SR.MARGIN)]
    h += [f"post {k}" for k, rr in ob["feet"].items() if SR._rect_hit(sol, rr, SR.MARGIN)]
    if SR._rect_hit(sol, ob["plates"], 0.0):
        h.append("the rePowder's floor plates")
    h += [k for k, rr in ob["keep"].items() if SR._rect_hit(sol, rr, 0.0)]
    h += [f"Class D unit {i}" for i, rr in enumerate(ob["classd"]) if SR._rect_hit(sol, rr, 50.0)]
    h += [f"unit {i}" for i, rr in enumerate(placed) if SR._rect_hit(sol, rr, 50.0)]
    if cl is not None:
        h += [f"clear floor: machine {k}" for k, rr in ob["rects"].items() if SR._rect_hit(cl, rr, 0.0)]
        h += [f"clear floor: docked MiR {k}" for k, rr in ob["mirs"].items() if SR._rect_hit(cl, rr, 0.0)]
        h += [f"clear floor: post {k}" for k, rr in ob["feet"].items() if SR._rect_hit(cl, rr, 0.0)]
        h += [f"clear floor: {k}" for k, rr in ob["keep"].items() if SR._rect_hit(cl, rr, 0.0)]
        h += [f"clear floor: Class D unit {i}" for i, rr in enumerate(ob["classd"]) if SR._rect_hit(cl, rr, 0.0)]
        h += [f"clear floor: unit {i}" for i, rr in enumerate(placed) if SR._rect_hit(cl, rr, 0.0)]
    return h


def place_search(kind, face, near, box, ob, placed=(), step=50.0):
    """The spot nearest `near` inside `box` (x0, x1, y0, y1) where a unit hits nothing -> (d, x, y) or None."""
    best = None
    for x in np.arange(box[0], box[1] + 1, step):
        for y in np.arange(box[2], box[3] + 1, step):
            d = math.hypot(x - near[0], y - near[1])
            if best is not None and d >= best[0]:
                continue
            if not spot_hits(kind, x, y, face, ob, placed):
                best = (d, float(x), float(y))
    return best


def places_check(ob=None) -> list:
    ob = ob or obstacles()
    sols = [place_rects(k, x, y, f)["solid"] for _, k, x, y, f, _, _ in PLACES]
    out = []
    for i, (st, kind, x, y, face, what, ex) in enumerate(PLACES):
        hits = spot_hits(kind, x, y, face, ob, [s for j, s in enumerate(sols) if j != i])
        out.append(dict(station=st, kind=kind, at=[x, y], face=face, covers=what, solid=[round(v) for v in sols[i]],
                        hits=hits, ok=not hits, **ex))
    return out


# --------------------------------------------------------------------------------------------- the walks
def walk_field(sources, extra_block=()):
    """Walking distance (mm) from the nearest of `sources` [(x, y)] to every cell of safety_render's 100 mm grid, round
    the machines (grown 250 mm for a body), the ICP-MS station at its suggested spot included. -> (dist, x0, y0)."""
    import safety_render as SR
    fl = SR.floor()
    x0, x1, y0, y1 = SR.BOUNDS
    g = SR.GRID_MM
    nx, ny = int((x1 - x0) / g) + 1, int((y1 - y0) / g) + 1
    xs, ys = x0 + np.arange(nx) * g, y0 + np.arange(ny) * g
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    block = np.zeros((nx, ny), bool)
    rects = [v for k, v in fl["machines"].items() if not k.startswith("charger")] + list(_icpms_rects().values())
    rects += list(SR.RACKING.values()) + list(extra_block)
    for a, b, c, d in rects:
        block |= (X > a - SR.BODY) & (X < b + SR.BODY) & (Y > c - SR.BODY) & (Y < d + SR.BODY)
    dist = np.full((nx, ny), np.inf)
    pq = []
    for sx, sy in sources:
        i, j = int(round((sx - x0) / g)), int(round((sy - y0) / g))
        dist[i, j] = 0.0
        block[i, j] = False
        heapq.heappush(pq, (0.0, i, j))
    nb = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142),
          (-1, -1, 1.4142)]
    while pq:
        dd, i, j = heapq.heappop(pq)
        if dd > dist[i, j]:
            continue
        for di, dj, w in nb:
            a_, b_ = i + di, j + dj
            if 0 <= a_ < nx and 0 <= b_ < ny and not block[a_, b_]:
                nd = dd + w * g
                if nd < dist[a_, b_]:
                    dist[a_, b_] = nd
                    heapq.heappush(pq, (nd, a_, b_))
    return dist, x0, y0, block


def walk_at(field, x, y):
    dist, x0, y0, _ = field
    g = 100.0
    i, j = int(round((x - x0) / g)), int(round((y - y0) / g))
    d = dist[i, j]
    if not np.isfinite(d):
        best = np.inf
        for di in range(-9, 10):
            for dj in range(-9, 10):
                a, b = i + di, j + dj
                if 0 <= a < dist.shape[0] and 0 <= b < dist.shape[1] and np.isfinite(dist[a, b]):
                    best = min(best, dist[a, b] + math.hypot(di, dj) * g)
        d = best
    return float(d)


def take_point(kind, x, y, face):
    """Where a person takes the unit from (or stands under the shower): in front of it."""
    a = math.radians(face)
    out = {"abc": 400.0, "shower": -SHOWER["head_y"], "o2": 450.0, "o2wall": 300.0}[kind]
    return (x + out * math.sin(a), y - out * math.cos(a))


# floor the NFPA 10 walk leaves out: the dead ends round the Meltio cell in the south-east corner, against walls the model
# doesn't have: the pocket behind it, 1.1 m between it and the east wall and closed at its north end by rack E (the
# cell's corner is 54 mm from the rack), and the strip south of it, which is only there because the walk's grid runs on
# to y -13,000. Up to 26.9 m from the nearest unit; if people work there, the cell wants a unit of its own
NOT_FLOOR = {"behind the Meltio cell": (11779.0, 13100.0, -13100.0, -9200.0),
             "south of the Meltio cell": (7175.0, 13100.0, -13100.0, -12415.0)}


def checked(field) -> np.ndarray:
    """The cells NFPA 10's walk is checked over: reachable, and not in NOT_FLOOR."""
    dist, x0, y0 = field[0], field[1], field[2]
    xs = x0 + np.arange(dist.shape[0]) * 100.0
    ys = y0 + np.arange(dist.shape[1]) * 100.0
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    m = np.isfinite(dist)
    for a, b, c, d in NOT_FLOOR.values():
        m &= ~((X > a) & (X < b) & (Y > c) & (Y < d))
    return m


def abc_check() -> dict:
    """NFPA 10 for the ordinary units: every reachable cell of the floor within 75 ft of walking (Class A, ordinary
    hazard), each hood within 50 ft (an 80-B unit, extra hazard); and kept apart from the Class D: 3 m or more in a
    straight line from every fixed Class D unit, and at every powder station the nearest extinguisher a Class D one."""
    import safety_render as SR
    abc = [take_point(k, x, y, f) for _, k, x, y, f, _, _ in PLACES if k == "abc"]
    fa = walk_field(abc)
    dist = fa[0]
    reach = checked(fa)
    worst = float(dist[reach].max())
    left_out = {k: round(float(np.nanmax(np.where(np.isfinite(dist) & ~reach, dist, np.nan))) / 1000.0, 2)
                for k in NOT_FLOOR}
    iw = np.unravel_index(np.argmax(np.where(reach, dist, -1)), dist.shape)
    worst_at = [float(fa[1] + iw[0] * 100.0), float(fa[2] + iw[1] * 100.0)]
    hoods = {k: round(walk_at(fa, *HAZARDS[k]) / 1000.0, 2) for k in ("fumehood", "icpms")}
    cd = [(x, y) for _, k, x, y, f, _ in S.PLACES if k != "pail"]
    apart = []
    for st, k, x, y, f, what, _ in PLACES:
        if k != "abc":
            continue
        dmin = min(math.hypot(x - a, y - b) for a, b in cd)
        apart.append(dict(at=[x, y], nearest_class_d_m=round(dmin / 1000.0, 2), ok=dmin >= NFPA10_ABC["apart_m"] * 1000))
    fd = SR.walk_field(SR.floor())
    powder = {}
    for k, (x, y) in S.HAZARDS.items():
        i, j = int(round((x - fd[1]) / 100.0)), int(round((y - fd[2]) / 100.0))
        d_cd = walk_at((fd[0], fd[1], fd[2], None), x, y)
        d_abc = walk_at(fa, x, y)
        powder[k] = dict(class_d_m=round(d_cd / 1000.0, 2), abc_m=round(d_abc / 1000.0, 2), ok=d_abc > d_cd + 3000.0)
    return dict(worst_walk_m=round(worst / 1000.0, 2), worst_at=worst_at, nfpa10_75ft=worst <= NFPA10_ABC["travel_A"],
                hoods_m=hoods, hoods_50ft=all(v * 1000.0 <= NFPA10_ABC["travel_B80"] for v in hoods.values()),
                apart=apart, powder=powder, apart_ok=all(a["ok"] for a in apart) and all(v["ok"] for v in powder.values()),
                left_out_m=left_out, cells=int(reach.sum()), floor_m2=round(float(reach.sum()) * 0.01, 0))


def shower_check() -> dict:
    """ANSI Z358.1 for each shower: the walk from its hood (10 s: 16.8 m; strong acid or caustic: immediately adjacent,
    3 m), the heights, the spray's clear floor (place_rects 'clear', in places_check), and how far its water is from any
    powder (its 36 in floor square to the nearest powder station's machine)."""
    import safety_render as SR
    fl = SR.floor()
    out = {}
    s = SHOWER
    for st, k, x, y, f, what, ex in PLACES:
        if k != "shower":
            continue
        tp = take_point(k, x, y, f)
        fw = walk_field([tp])
        hz = HAZARDS[st]
        d = walk_at(fw, *hz)
        sq = _turn((-18 * IN, 18 * IN, s["head_y"] - 18 * IN, s["head_y"] + 18 * IN), x, y, f)
        dp = min((math.hypot(max(rr[0] - sq[1], 0, sq[0] - rr[1]), max(rr[2] - sq[3], 0, sq[2] - rr[3])), m)
                 for m, rr in fl["machines"].items() if m in POWDER)
        out[st] = dict(at=[x, y], walk_m=round(d / 1000.0, 2), within_10s=d <= ANSI["travel_m"] * 1000.0,
                       adjacent_3m=d <= ANSI["adjacent_m"] * 1000.0, head_mm=round(s["head_z"]),
                       head_ok=ANSI["head_min"] <= s["head_z"] <= ANSI["head_max"], eyewash_mm=round(s["eye_z"]),
                       eyewash_ok=ANSI["eye_min"] <= s["eye_z"] <= ANSI["eye_max"], handle_mm=round(s["rod_z"]),
                       handle_ok=s["rod_z"] <= ANSI["actuator_max"], nearest_powder=[dp[1], round(dp[0] / 1000.0, 2)],
                       icpms_suggested=bool(ex.get("icpms")))
    return out


def o2_check() -> dict:
    """Each O2 monitor: its gas, its sensor's height against the gas's density, and how far it is from where the gas
    comes in."""
    out = {}
    for st, k, x, y, f, what, ex in PLACES:
        if k not in ("o2", "o2wall"):
            continue
        hz = HAZARDS["icpms dewar" if st == "icpms" else st]
        gas = ex["gas"]
        out[st] = dict(at=[x, y], gas=gas, sensor_mm=SENSOR_Z[gas], from_source_m=round(math.hypot(x - hz[0],
                                                                                                   y - hz[1]) / 1000, 2),
                       density_vs_air={"argon": 1.38, "nitrogen": 0.97}[gas], icpms_suggested=bool(ex.get("icpms")))
    return out


# the racking's uprights a unit can hang on, facing the floor (warehouse.RACKS: 2,743 mm bays from y -9,200 on racks W
# and E, from x -11,000 on rack N); and the two south ends of racks W and E, facing south
def abc_candidates() -> list:
    c = [(-11833.0, -9200.0 + 2743.0 * k, 90.0) for k in range(5)]
    c += [(11833.0, -9200.0 + 2743.0 * k, -90.0) for k in range(5)]
    c += [(-11000.0 + 2743.0 * k, 2800.0, 0.0) for k in range(9)]
    c += [(-11871.0, -9200.0, 0.0), (11871.0, -9200.0, 0.0)]
    return c


def abc_search(n_max: int = 4) -> dict:
    """The fewest ordinary units on the racking (abc_candidates) that meet NFPA 10 (every reachable cell within 75 ft of
    walking, both hoods within 50 ft) and keep apart from the Class D (3 m from every Class D unit; at every powder
    station a Class D unit nearer by 3 m or more), then the shortest farthest walk. -> the fewest and the runners-up.
    PLACES doesn't take the fewest (two, both where few walk): it takes three that pass, one at each end of the floor
    and one behind the Shuttles (notes/safety.md)."""
    import itertools
    import safety_render as SR
    cd = [(x, y) for _, k, x, y, f, _ in S.PLACES if k != "pail"]
    cands = [c for c in abc_candidates() if min(math.hypot(c[0] - a, c[1] - b) for a, b in cd) >=
             NFPA10_ABC["apart_m"] * 1000.0]
    fields = [walk_field([take_point("abc", x, y, f)]) for x, y, f in cands]
    fd = SR.walk_field(SR.floor())
    d_cd = {k: walk_at((fd[0], fd[1], fd[2], None), x, y) for k, (x, y) in S.HAZARDS.items()}
    reach = checked(walk_field([take_point("abc", *cands[0])]))
    best = []
    for n in range(1, n_max + 1):
        for combo in itertools.combinations(range(len(cands)), n):
            dist = np.min([fields[i][0] for i in combo], axis=0)
            worst = float(np.max(np.where(reach, dist, 0.0)))
            if worst > NFPA10_ABC["travel_A"]:
                continue
            f0 = (dist, fields[0][1], fields[0][2], None)
            if any(walk_at(f0, *HAZARDS[h]) > NFPA10_ABC["travel_B80"] for h in ("fumehood", "icpms")):
                continue
            if any(walk_at(f0, x, y) <= d_cd[k] + 3000.0 for k, (x, y) in S.HAZARDS.items()):
                continue
            best.append((n, worst, [cands[i] for i in combo]))
        if best:
            break
    best.sort(key=lambda b: (b[0], b[1]))
    return dict(candidates=len(cands), choice=best[0] if best else None, runners_up=best[1:6])


def bom() -> dict:
    n = {k: sum(1 for p in PLACES if p[1] == k) for k in ("abc", "shower", "o2", "o2wall")}
    rows = [
        ("Amerex B456, 10 lb ABC, with its 801 wall bracket", n["abc"], ABC["price_usd"], "Webstaurant"),
        ("Rack-upright clamp plate and U-bolts for it (ours)", n["abc"], 25.0, "estimate"),
        ("FIRE EXTINGUISHER sign, 7 x 10 in, and an ABC / NOT FOR METAL FIRES placard", n["abc"], 30.0, "estimate"),
        ("Guardian G1902 combination drench shower and eyewash, its sign", n["shower"], SHOWER["price_usd"],
         "Webstaurant"),
        ("Thermostatic mixing valve (Guardian G3800LF, now the G6040) in a surface cabinet", n["shower"],
         MIXER["price_usd"], "the G6040's sale price (list $1,603)"),
        ("Plumbing: hot and cold water to each shower, a floor drain under it (a contractor's quote)", n["shower"],
         None, "not priced"),
        ("PureAire 99028 O2 deficiency monitor with remote sensor", n["o2"] + n["o2wall"], O2["price_usd"],
         "PureAire ($2,375-2,755)"),
        ("PureAire 42002 horn/strobe", n["o2"] + n["o2wall"], O2["strobe_usd"], "PureAire ($220-315)"),
        ("O2 monitor post: strut, base, anchors, conduit (ours)", n["o2"], 120.0, "estimate"),
        ("CAUTION ARGON / NITROGEN IN USE sign, 7 x 10 in", n["o2"] + n["o2wall"], 20.0, "estimate"),
    ]
    total = sum(q * p for _, q, p, _ in rows if p)
    return dict(rows=[dict(item=i, qty=q, unit_usd=p, source=s) for i, q, p, s in rows], total_usd=round(total, 2),
                note="the ICP-MS station's shower and O2 monitor are counted; they go in with the station",
                upkeep="showers: activated weekly, inspected yearly (ANSI Z358.1); O2 monitors: calibrated and their "
                       "alarms tested as PureAire's manual says; ABC units: monthly checks, yearly service, a 6-year "
                       "maintenance and a 12-year hydrostatic test (NFPA 10)")


def report() -> dict:
    ob = obstacles()
    srch = abc_search()
    rep = dict(abc=dict(model=ABC["model"], rating=ABC["rating"], source=ABC["source"], top_mm=ABC_TOP_Z,
                        top_ok=ABC_TOP_Z <= NFPA10_ABC["top_max"], check=abc_check(),
                        fewest=dict(n=srch["choice"][0], worst_m=round(srch["choice"][1] / 1000.0, 2),
                                    at=srch["choice"][2]) if srch["choice"] else None),
               shower=dict(model=SHOWER["model"], source=SHOWER["source"], ansi=ANSI, check=shower_check()),
               o2=dict(model=O2["model"], source=O2["source"], alarms=[O2["alarm_low"], O2["alarm_high"]],
                       osha=OSHA_O2, sensor_mm=SENSOR_Z, check=o2_check()),
               places=places_check(ob), nfpa10=NFPA10_ABC, bom=bom())
    rep["places_ok"] = all(p["ok"] for p in rep["places"])
    path = OUT / "safety_other.json"
    path.write_text(json.dumps(rep, indent=1, default=float) + "\n")
    print(json.dumps(dict(places=[(p["station"], p["kind"], p["hits"]) for p in rep["places"]],
                          abc=rep["abc"]["check"], showers=rep["shower"]["check"], o2=rep["o2"]["check"],
                          bom=rep["bom"]["total_usd"]), indent=1, default=float))
    print("->", path.relative_to(HERE))
    return rep


# ================================================================================================ the lab's meshes
def floor_parts(lod: str = "lab", icpms: bool | None = None) -> dict:
    """{name: (PolyData, material)}, world: every unit of PLACES where it stands, turned to face the way PLACES says;
    the ICP-MS station's only if it is on the floor (ICPMS_ON_FLOOR) or `icpms` asks for them."""
    from scene import T
    icpms = ICPMS_ON_FLOOR if icpms is None else icpms
    out: dict = {}
    built = {}
    for st, kind, x, y, face, _, ex in PLACES:
        if ex.get("icpms") and not icpms:
            continue
        key = (kind, ex.get("gas"))
        if key not in built:
            built[key] = {"abc": lambda: rack_parts(lod), "shower": lambda: {**shower_parts(lod), **mixer_parts()},
                          "o2": lambda: o2_post_parts(ex["gas"], True),
                          "o2wall": lambda: o2_post_parts(ex["gas"], False)}[kind]()
        parts = dict(built[key])
        M = T((x, y, 0.0)) @ _rot(face)
        for name, (mesh, mat) in parts.items():
            _add(out, f"{kind} {name}", mesh.transform(M, inplace=False), mat)
        if kind == "shower":                     # its hot and cold feeds: from the mixing valve's cabinet up to the roof
            pv = S._pv()
            z0 = 2560.0 + MIXER["cab"][1] + 300.0
            feeds = [pv.Cylinder(center=(x_, 0.0, (z0 + ROOF_Z) / 2), direction=(0, 0, 1), radius=17.0,
                                 height=ROOF_Z - z0, resolution=12).triangulate() for x_ in (-90.0, 90.0)]
            _add(out, "shower supply", _merge(feeds).transform(M, inplace=False), "galv")
    return out


def floor_meshes() -> dict:
    """{name: (PolyData, rgb, specular)} for setup_lab.build: floor_parts merged by material, cached on this file and
    safety.py."""
    import hashlib
    import pickle
    cache = HERE / ".cache"
    cache.mkdir(exist_ok=True)
    h = hashlib.sha256((HERE / "safety_other.py").read_bytes() + (HERE / "safety.py").read_bytes()).hexdigest()[:16]
    path = cache / f"safety_other_floor_{h}_{int(ICPMS_ON_FLOOR)}.pkl"
    if path.exists():
        return pickle.loads(path.read_bytes())
    by: dict = {}
    for name, (mesh, mat) in floor_parts().items():
        by.setdefault(mat, []).append(mesh)
    out = {}
    for mat, ms in by.items():
        m = _merge(ms).clean().triangulate()
        if m.n_cells > 20000:
            m = m.decimate(0.75).compute_normals(split_vertices=True, feature_angle=35.0)
        out[f"safety {mat}"] = (m, S.colour(mat), S.MATS[mat][4])
    path.write_bytes(pickle.dumps(out))
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("what", nargs="?", default="report")
    a = ap.parse_args()
    import safety_other_render as SOR
    SOR.main(a.what)
