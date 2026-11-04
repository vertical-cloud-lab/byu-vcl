"""Round 7 stations (#303, PR #318): a glovebox on a tray, a tensile tester lying on its side, an automatic
micro-Vickers tester, an autonomous CNC mill, two fume hoods, and a tray of stored samples.

Each is an ``instruments.Instrument`` (pieces, joints, an actions script), as in ``instruments.py``; ``tour.py`` loads
``REGISTRY`` and plays each one. Frame as in ``instruments.py``: x to the right, y away from you facing the front, z up,
origin at the centre of the footprint, millimetres. On a tray, the front (-y) faces the opening, where the arm works.

``FOOTPRINTS`` is for the tray layout: key -> (W, D, H mm, mass kg, product, source URL, "tray" or "floor"). W x D is
the footprint as drawn here, H the height closed (what opens upward is in the notes). The tray limits used: 2426 x 840
mm inside the rim, 856.5 mm product height (the 996 mm opening), light 228 / medium 360 / strong 490 kg. Each tray also
carries its UPS and dock plate at the back right (``services.UPS_AT``, ``services.PLATE_*``).

``storage_seats()`` lists every pocket of the storage load that the arm can pick from.

Moving parts that must stay in step (a capper and the lid it carries, a spindle and its tool) use ``instruments_lab``'s
``Timeline``, ``Track`` and ``Turn``. Live panels (the tensile curve, the hardness reading) use its ``PLOTS`` hook.

Sources are in ``SOURCES`` and in notes/instruments_r7.md. "Estimate" means read off photos or our own design.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
import pyvista as pv

import instruments as I
from instruments import Instrument, Joint, _piece, _xcyl, _ycyl
from instruments_lab import PLOTS, Timeline, Track, Turn, _gv

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
from common import box, cyl, hose, rbox, tube  # noqa: E402

# ===================================================================================================== footprints
# key -> (W, D, H mm, mass kg, product, source URL, "tray" | "floor")
FOOTPRINTS = {
    "glovebox_tray": (1390.0, 830.0, 810.0, 140.0,
                      "Custom N2 glovebox, purge-only, with a 150 mm mini antechamber loaded from the front (our "
                      "design; sizes after the Vigor SG1200/750 and the Plas-Labs 830-ABC). Mass is an estimate",
                      "https://www.pharmaceutical-tech.com/products/vigor-tech-usa/standard-gloveboxes", "tray"),
    "tensile_h": (1289.0, 638.0, 448.0, 83.0,
                  "ZwickRoell zwickiLine Z5.0 TN (5 kN) lying on its side, on a 40 mm base plate (ours); "
                  "1289 x 408 x 480 mm upright, 622 deep with its electronics, 78 kg",
                  "https://www.zwickroell.com/fileadmin/content/Files/SharePoint/user_upload/PI_EN/"
                  "02_396_zwickiLine_Z0_5_up_to_Z5_0_Materials_Testing_Machine_PI_EN.pdf", "tray"),
    "hardness": (533.0, 672.0, 595.0, 48.0,
                 "Mitutoyo HM-220 Type D (AVPAK): micro-Vickers, motorized XY stage, autofocus, motorized turret; "
                 "main unit 315 x 671 x 595 mm, 43 kg, plus its PC beside it (estimate, 5 kg)",
                 "https://www.mitutoyo.com/webfoo/wp-content/uploads/K_section.pdf", "tray"),
    "cnc": (610.0, 535.0, 540.0, 50.0,
            "Makera Carvera desktop CNC (580 x 520 x 540 mm), 6-tool changer; 840 mm tall with the lid open. The "
            "lid actuator (the extra 30 mm on the right) and the pneumatic vise are our additions",
            "https://www.makera.com/blogs/article/carvera-carvera-air-which-desktop-cnc-is-right-for-you", "tray"),
    "fumehood": (1219.0, 958.0, 2581.0, 260.0,
                 "Labconco Protector XStream 4 ft ducted hood (1219 x 958 x 1499 mm, about 200 kg) on a base "
                 "cabinet and work surface (900 + 32 mm, estimated); 2581 mm with its 150 mm exhaust collar",
                 "https://www.labconco.com/p/protector-xstream-laboratory-hoods", "floor"),
    "fumehood_tray": (1030.0, 610.0, 715.0, 41.0,
                      "Sentry Air Systems ductless fume hood, standard 24 in: 660 x 610 x 635 mm, about 41 kg, with "
                      "its 330 x 330 x 368 mm blower and filter box beside it and the hose over the top",
                      "https://www.sentryair.com/dfhapp.htm", "tray"),
    "storage": (1760.0, 760.0, 300.0, 95.0,
                "Sample storage load (our design): Al and Cu charge cups and plugs, 20 mL vials, ICP-MS tubes, SEM "
                "stubs, mounted coupons, tensile bars, powder jars, labelled bins, a two-drawer cabinet. Leaves the "
                "tray's right 660 mm free for the UPS and dock. Mass is an estimate", "", "tray"),
    # instruments_char's VHX, changed here: no stand-up monitor or console. Not centred on its origin: its box is
    # x -250..380, y -272..352 (the stage's axis at x 0, y -40)
    "vhx": (630.0, 625.0, 716.0, 43.4,
            "Keyence VHX-7000 + EA-300 on the VHX-S750E stand, the VHX-7000 controller (its 27 in screen built in) "
            "turned sideways beside it, a PiKVM V4 Mini on top; 23.8 + 7.2 + 12 + 0.35 kg",
            "https://www.keyence.com/products/microscope/digital-microscope/vhx-7000/models/vhx-7000/", "tray"),
}

SOURCES = {
    "glovebox_tray": [
        "Vigor standard gloveboxes (SG1200/750): 1200 x 750 x 900 mm body, 220 mm aluminium glove ports, mini "
        "antechamber 150 mm ID x 300 mm, main 370 x 600 mm; purifier < 1 ppm (distributor page "
        "https://www.pharmaceutical-tech.com/products/vigor-tech-usa/standard-gloveboxes)",
        "Plas-Labs 830-ABC: 1100 x 610 x 790 mm with a 12 in transfer chamber, interior 710 x 580 x 740 mm (resellers: "
        "https://spectraservices.com/product/plas-labs-830-ABC.html)",
        "Tenders ask for a mini antechamber of about 150 x 300-425 mm and ports of 200 mm or more (IIT Madras annexure)",
        "Our design: the box, the purge-only gas scheme, the sliding outer door, the internal capper and tipping cradle",
    ],
    "tensile_h": [
        "ZwickRoell PI 396 1123, zwickiLine Z0.5-Z5.0: Z5.0 TS/TN/TH 789/1289/1589 mm tall, 408 wide (411 with "
        "electronics), 480 deep (622 with electronics), 70/78/83 kg; 0.0005-600 mm/min; test area depth 105 mm",
        "Horizontal use: 'can be operated in vertical or horizontal position as required, and can be swiveled 180 "
        "degrees in horizontal mode' (ZwickRoell zwickiLine product information, as quoted by search results of its "
        "DirectIndustry copy; the page itself returned 403)",
        "No motorized horizontal machine with a published size reaches 14.8 kN: Tinius Olsen's horizontal machines "
        "(5-300 kN) and ADMET's eXpert 5000 horizontal option are quote-only; TecQuipment's SM1002 (20 kN) is "
        "hand-cranked",
    ],
    "hardness": [
        "Mitutoyo catalogue section K (https://www.mitutoyo.com/webfoo/wp-content/uploads/K_section.pdf): HM-210/220, "
        "315 x 671 x 595 mm, 43 kg; HM-220 0.4903-19610 mN (0.05 gf-2 kgf); motorized turret for up to 4 objectives "
        "and 2 indenters; Type D: AVPAK on a specified PC, motorized XY stage 50 x 50 mm (100 x 100 optional), table "
        "130 x 130 mm, 25 mm/s, motorized focusing 1.4 mm, 3 MP camera",
    ],
    "cnc": [
        "Makera (makera.com, and its Carvera vs Carvera Air article): 580 x 520 x 540 mm, about 50 kg, 840 mm with the "
        "lid open, work area 360 x 240 x 140 mm, 6-tool automatic changer with auto probing, 200 W spindle",
        "The lid is opened by hand; the actuator and the pneumatic vise are our additions (sizes estimated)",
    ],
    "fumehood": [
        "Labconco Protector XStream (https://www.labconco.com/p/protector-xstream-laboratory-hoods): sash stop at 18 in "
        "(457 mm) open, 325 mm exhaust collar; 4 ft size 1219 x 958 x 1499 mm and about 200 kg from Fisher and "
        "Labrepco listings; 440 CFM at 0.08 in static pressure. Base cabinet and work surface heights estimated",
    ],
    "fumehood_tray": [
        "Sentry Air Systems ductless fume hoods (https://www.sentryair.com/dfhapp.htm): standard 24 in, 24 D x 26 W x "
        "25 H in outside, 23.5 x 24 x 24 in inside, about 90 lb, blower 13 x 13 x 14.5 in; 100 fpm with HEPA, 60 fpm "
        "with carbon. The 9.25 in (235 mm) front opening is the figure the page gives for its carbon-steel models",
    ],
    "storage": [
        "Cups and plugs: charge.py (#222's charge_cad.py: 3/4 in x 2.5 in cups, 1/2 in x 3/8 in plugs); 20 mL vials: "
        "props.py (28 x 61 mm); tensile bars: alloy_models.E8_SUB (100 mm, 6 mm thick as printed)",
        "15 mL ICP-MS tubes 17 x 120 mm, 12.7 mm SEM pin stubs, 1.25 in mounts, 250 mL jars: common sizes, estimates",
    ],
}


# ===================================================================================================== materials
MATERIALS = {
    "r7_steel": (0.70, 0.71, 0.73, 1.0, 0.6),            # brushed stainless
    "r7_frame": (0.30, 0.31, 0.33, 1.0, 0.35),
    "r7_pc": (0.80, 0.86, 0.90, 0.22, 0.9),              # polycarbonate window
    "r7_glove": (0.10, 0.10, 0.11, 1.0, 0.2),            # butyl gloves
    "r7_jar": (0.86, 0.88, 0.90, 1.0, 0.4),              # a steel catch jar
    "r7_hdpe": (0.93, 0.93, 0.90, 0.85, 0.3),
    "r7_lid": (0.18, 0.36, 0.70, 1.0, 0.3),
    "r7_al_powder": (0.62, 0.63, 0.66, 1.0, 0.05),
    "r7_flow_n2": (0.30, 0.55, 0.95, 0.55, 0.0),         # gas, drawn see-through
    "r7_flow_air": (0.10, 0.62, 1.00, 0.85, 0.0),
    "r7_zwick": (0.86, 0.87, 0.86, 1.0, 0.3),            # zwickiLine light grey
    "r7_zwick_dk": (0.22, 0.23, 0.25, 1.0, 0.35),
    "r7_zwick_green": (0.42, 0.66, 0.20, 1.0, 0.3),
    "r7_mitu": (0.90, 0.90, 0.88, 1.0, 0.3),             # Mitutoyo's off-white
    "r7_mitu_dk": (0.25, 0.27, 0.30, 1.0, 0.35),
    "r7_carvera": (0.93, 0.93, 0.92, 1.0, 0.3),
    "r7_carvera_lid": (0.32, 0.33, 0.36, 0.22, 0.9),     # the Carvera's tinted lid, drawn lighter to see in
    "r7_carbide": (0.55, 0.56, 0.60, 1.0, 0.8),
    "r7_lab_white": (0.95, 0.95, 0.94, 1.0, 0.25),
    "r7_liner": (0.86, 0.87, 0.88, 1.0, 0.2),
    "r7_epoxy": (0.12, 0.12, 0.13, 1.0, 0.35),           # epoxy resin work surface
    "r7_sash": (0.80, 0.88, 0.92, 0.25, 0.9),
    "r7_keller": (0.92, 0.85, 0.55, 0.55, 0.7),          # Keller's reagent
    "r7_al_rack": (0.20, 0.38, 0.72, 1.0, 0.4),          # blue anodized: aluminium's rack
    "r7_cu_rack": (0.85, 0.42, 0.12, 1.0, 0.4),          # orange: copper's
    "r7_bin": (0.20, 0.45, 0.75, 1.0, 0.2),
    "r7_label": (0.98, 0.98, 0.96, 1.0, 0.1),
    "r7_dent": (0.06, 0.06, 0.07, 1.0, 0.1),
    "r7_ghost": (1.0, 1.0, 1.0, 0.0, 0.0),
}
AL_C = (0.84, 0.85, 0.87)          # charge.AL_5N
CU_C = (0.80, 0.46, 0.28)          # charge.CU


def _dummy(at=(0.0, 0.0, 0.0)):
    """An invisible speck: a piece that only carries a joint value (read by a panel) or children."""
    return [(pv.Sphere(radius=0.5, center=at, theta_resolution=4, phi_resolution=4), (1.0, 1.0, 1.0), 0.0)]


def _arrow(p0, p1, d=14.0) -> cq.Workplane:
    """A flow arrow from p0 to p1: a shaft and a cone at p1."""
    a, b = cq.Vector(*p0), cq.Vector(*p1)
    v = b - a
    L = v.Length
    u = v.normalized()
    head = min(3.2 * d, 0.45 * L)
    shaft = cq.Solid.makeCylinder(d / 2, L - head, a, u)
    cone = cq.Solid.makeCone(1.2 * d, 0.0, head, a + u * (L - head), u)
    return cq.Workplane().add(shaft.fuse(cone))


def _turn_knots(tl: Timeline, fn) -> tuple:
    T = tl.t[-1]
    return tuple((t / T, float(fn(s))) for t, s in zip(tl.t, tl.states))


# ===================================================================================================== a. glovebox
# A custom N2 glovebox for a tray (our design). Sizes from real compact boxes: Vigor's standard box is 1200 x 750 x 900
# mm with 220 mm ports and a 150 mm x 300 mm mini antechamber; Plas-Labs' 830-ABC is 1100 x 610 x 790 mm. Ours is 1100
# x 520 x 640 mm on a 40 mm frame, so it stays under 856.5 mm with its fittings, and its 150 mm mini antechamber
# sticks out of the front, so the arm loads it there and the box's depth plus the antechamber's stays inside the tray.
# Purge-only, with no purifier: N2 comes from the tray's dock line, flows through the box and out through an oil
# bubbler. A purifier (a catalyst and sieve column with a blower) needs regenerating with H2-bearing forming gas and a
# heater for hours, adds about 100 kg and heat inside the VLM, and holds < 1 ppm, which this job doesn't need. The
# cost is N2: about 7.6 box volumes (2.4 m3) to reach 100 ppm O2 from air, then a trickle. The dock's N2 generator
# gives only 0.5-1.1 L/min (services.md), far too little for the first purge: it needs a larger N2 supply.
GB = dict(X0=-700.0, X1=400.0, Y0=-125.0, Y1=395.0, Z0=40.0, Z1=680.0, wall=4.0, port_d=220.0, port_z=340.0,
          ports=(-450.0, -10.0), ax=270.0, az=230.0, a_od=170.0, a_id=150.0, a_y0=-385.0, door_t=18.0,
          sled_y=130.0, sled_z=182.0, jar_d=70.0, jar_h=85.0, sjar=(270.0, 215.0), holder=(270.0, 300.0))


def glovebox_tray() -> Instrument:
    p = GB
    W, D, H = FOOTPRINTS["glovebox_tray"][:3]
    inst = Instrument("glovebox_tray", "Inert glovebox for a tray, with an automatic mini antechamber",
                      "Custom N2 glovebox (purge-only)", (W, D, H),
                      "Our design; sizes after Vigor's SG1200/750 (220 mm ports, 150 x 300 mm mini antechamber) and "
                      "Plas-Labs' 830-ABC (1100 x 610 x 790 mm)")
    X0, X1, Y0, Y1, Z0, Z1, t = p["X0"], p["X1"], p["Y0"], p["Y1"], p["Z0"], p["Z1"], p["wall"]
    ax, az = p["ax"], p["az"]
    body = _piece(inst, "body")
    body.add("frame", box(X0, Y0, 0, X1, Y1, Z0), "r7_frame")
    shell = box(X0, Y0, Z0, X1, Y1, Z1).cut(box(X0 + t, Y0 + t, Z0 + t, X1 - t, Y1 - t, Z1 - t))
    shell = shell.cut(box(-660, Y0 - 1, 90, 140, Y0 + t + 1, 640))                    # the window
    shell = shell.cut(_ycyl(p["a_id"], t + 2, x=ax, y=Y0 - 1, z=az))                  # the antechamber's bore
    body.add("box", shell, "r7_steel")
    pane = box(-662, Y0 - 6, 88, 142, Y0 + 4, 642)
    for px in p["ports"]:
        pane = pane.cut(_ycyl(p["port_d"], 12, x=px, y=Y0 - 7, z=p["port_z"]))
    body.add("window", pane, "r7_pc")
    for px in p["ports"]:
        ring = _ycyl(p["port_d"] + 40, 30, x=px, y=Y0 - 22, z=p["port_z"]).cut(
            _ycyl(p["port_d"], 32, x=px, y=Y0 - 23, z=p["port_z"]))
        body.add(f"glove port {px:.0f}", ring, "r7_frame")
        glove = _ycyl(p["port_d"] - 30, 300, x=px, y=Y0 + 8, z=p["port_z"]).rotate(
            (px, Y0 + 8, p["port_z"]), (px + 1, Y0 + 8, p["port_z"]), -28)
        body.add(f"glove {px:.0f}", glove, "r7_glove")
    # the mini antechamber: a 150 mm tube out of the front, its outer door sliding sideways in a frame
    tube_ = _ycyl(p["a_od"], Y0 - p["a_y0"], x=ax, y=p["a_y0"], z=az).cut(
        _ycyl(p["a_id"], Y0 - p["a_y0"] + 2, x=ax, y=p["a_y0"] - 1, z=az))
    body.add("antechamber", tube_, "r7_steel")
    body.add("antechamber flange", _ycyl(210, 12, x=ax, y=p["a_y0"], z=az).cut(
        _ycyl(p["a_id"], 14, x=ax, y=p["a_y0"] - 1, z=az)), "r7_steel")
    fr = box(70, p["a_y0"], az - 125, 530, p["a_y0"] + 10, az + 125).cut(_ycyl(212, 12, x=ax, y=p["a_y0"] - 1, z=az))
    body.add("door frame", fr, "r7_frame")
    body.add("door rail top", box(160, p["a_y0"] - 26, az + 112, 530, p["a_y0"], az + 122), "r7_frame")
    body.add("door rail bottom", box(160, p["a_y0"] - 26, az - 122, 530, p["a_y0"], az - 112), "r7_frame")
    body.add("frame post", box(495, p["a_y0"], 0, 530, p["a_y0"] + 35, az - 125), "r7_frame")
    body.add("antechamber foot", box(225, -330, 0, 315, -290, az - p["a_od"] / 2 - 1), "r7_frame")
    # the vacuum gauge on the door frame, left of the door's travel (its needle swings with each pump-down)
    gx = 110.0
    body.add("gauge", _ycyl(70, 14, x=gx, y=p["a_y0"] - 14, z=az + 60), "r7_lab_white")
    body.add("gauge rim", _ycyl(76, 4, x=gx, y=p["a_y0"] - 15, z=az + 60).cut(
        _ycyl(66, 6, x=gx, y=p["a_y0"] - 16, z=az + 60)), "r7_frame")
    # inside: the transfer shelf the sled runs onto, the balance and storage jar, the lid holder, the capper's gantry,
    # the O2 and H2O sensors on the back wall
    sz = p["sled_z"]
    ins = _piece(inst, "inside")                       # its own piece, so it stays solid when the box goes see-through
    ins.add("shelf", box(205, -100, sz - 10, 335, 170, sz), "r7_steel")
    for gdx in (155.0, 375.0):                         # the inner door's guides: it slides up, clear of the shelf
        body.add(f"inner door guide {gdx:.0f}", box(gdx, -105, 120, gdx + 10, -100, 560), "r7_frame")
    ins.add("shelf leg", box(215, 150, Z0 + t, 325, 168, sz - 10), "r7_steel")
    sx, sy = p["sjar"]
    ins.add("balance", box(sx - 40, sy - 35, Z0 + t, sx + 40, sy + 35, 108), "r7_lab_white")
    ins.add("balance pan", cyl(76, 3, x=sx, y=sy, z=108), "r7_steel")
    ins.add("storage jar", tube(60, 56, 72, x=sx, y=sy, z=111).union(cyl(60, 3, x=sx, y=sy, z=111)), "r7_hdpe")
    hx, hy = p["holder"]
    ins.add("lid holder", cyl(20, 180 - Z0 - t, x=hx, y=hy, z=Z0 + t).union(cyl(70, 3, x=hx, y=hy, z=180)),
             "r7_frame")
    ins.add("gantry post", box(250, 350, Z0 + t, 290, 388, 520), "r7_frame")
    ins.add("gantry rail L", box(245, 40, 480, 258, 388, 520), "r7_frame")
    ins.add("gantry rail R", box(282, 40, 480, 295, 388, 520), "r7_frame")
    for i, (nm, z) in enumerate((("O2 sensor", 560.0), ("H2O sensor", 470.0))):
        body.add(nm, _ycyl(40, 40, x=-560 + 90 * i, y=Y1 - t - 40, z=z), "r7_lab_white")
    # the bay on the right: PLC and HMI (O2 and dew point readouts), the antechamber's pump, the gas lines
    body.add("controls", box(410, -120, Z0, 690, 120, 520), "r7_lab_white")
    body.add("HMI", box(450, -121.5, 330, 650, -120, 480), "screen_on")
    body.add("pump", box(430, 150, 0, 670, 390, 250), "inst_dark")
    body.add("pump line", hose([(560, 150, 20), (560, -330, 20), (330, -330, 20), (330, -330, 168)], 16),
             "lab_cable")
    body.add("N2 in", hose([(300, Y1, 600), (300, Y1 + 8, 600), (300, Y1 + 8, 60), (690, Y1 + 8, 60)], 12),
             "svc_n2")
    body.add("bubbler", cyl(50, 110, x=-600, y=300, z=Z1), "r7_pc")
    body.add("bubbler oil", cyl(44, 40, x=-600, y=300, z=Z1 + 4), "r7_keller")
    body.add("purge out", hose([(-600, 300, Z1 + 110), (-600, 300, Z1 + 125), (-600, 380, Z1 + 125)], 10),
             "lab_cable")
    # the outer door slides +x in its rails; the inner door slides up inside the box
    door = _piece(inst, "door")
    dy0 = p["a_y0"] - p["door_t"] - 2
    door.add("outer door", _ycyl(210, p["door_t"], x=ax, y=dy0, z=az), "r7_steel")
    door.add("door handle", box(ax + 50, dy0 - 12, az - 40, ax + 70, dy0, az + 40), "inst_dark")
    door.add("door shoe", box(ax - 100, dy0, az + 100, ax + 100, dy0 + 4, az + 110), "r7_frame")
    idoor = _piece(inst, "inner_door")
    idoor.add("inner door", _ycyl(200, 12, x=ax, y=Y0 + t + 2, z=az), "r7_steel")
    # the sled, the catch jar on its tipping cradle, the jar's lid, and the storage jar's lid
    sled = _piece(inst, "load")
    yc = p["sled_y"]
    sled.add("sled", box(ax - 55, yc - 70, sz, ax + 55, yc + 35, sz + 8), "aluminium")
    lifter = _piece(inst, "lifter")                    # two arms beside the jar, with the cradle's trunnions
    for x0 in (ax - 50, ax + 43):
        lifter.add(f"lift arm {x0:.0f}", box(x0, yc + 28, sz + 13, x0 + 7, yc + 42, sz + 98), "r7_frame")
    lifter.add("trunnions", _xcyl(10, 6, x=ax - 43, y=yc + 35, z=sz + 93).union(
        _xcyl(10, 6, x=ax + 37, y=yc + 35, z=sz + 93)), "steel")
    tip = _piece(inst, "tipper")
    jd, jh = p["jar_d"], p["jar_h"]
    jz = sz + 8
    tip.add("catch jar", tube(jd, jd - 4, jh, x=ax, y=yc, z=jz).union(cyl(jd, 3, x=ax, y=yc, z=jz)), "r7_jar")
    tip.add("cradle", tube(jd + 10, jd + 0.5, 30, x=ax, y=yc, z=jz), "r7_frame")
    tip.add("powder", cyl(jd - 5, 45, x=ax, y=yc, z=jz + 3), "r7_al_powder")
    lid = _piece(inst, "lid")
    lid.add("catch jar lid", cyl(jd + 4, 12, x=ax, y=yc, z=jz + jh), "r7_lid")
    lid2 = _piece(inst, "lid2")
    lid2.add("storage jar lid", cyl(64, 10, x=hx, y=hy, z=183), "r7_lid")
    cap_y = _piece(inst, "capper_y")
    cap_y.add("capper carriage", box(240, 270, 450, 300, 330, 479).cut(cyl(24, 40, x=270, y=300, z=445)), "inst_dark")
    cap_z = _piece(inst, "capper_z")
    zb = 330.0                                                         # the capper head's bottom, parked
    cap_z.add("capper head", cyl(80, 40, x=270, y=300, z=zb), "inst_dark")
    cap_z.add("capper pad", cyl(70, 3, x=270, y=300, z=zb - 0.5), "rubber")
    cap_z.add("capper rod", cyl(20, 260, x=270, y=300, z=zb + 40), "steel")
    # the pour and the fill
    stream = _piece(inst, "stream")
    s0, s1 = np.array([ax, 188.0, 310.0]), np.array([ax, 210.0, 155.0])
    v = s1 - s0
    stream.add("powder stream", cq.Workplane().add(cq.Solid.makeCylinder(5, float(np.linalg.norm(v)),
                                                                        cq.Vector(*s0), cq.Vector(*(v / np.linalg.norm(v))))),
               "r7_al_powder")
    fill = _piece(inst, "fill")
    fill.add("powder in the storage jar", cyl(54, 40, x=sx, y=sy, z=114), "r7_al_powder")

    # one timeline for the sled, the cradle, the capper and the two lids
    lid_top = jz + jh + 12                              # 287: where the capper's pad meets the catch jar's lid
    hold = 330.0 - lid_top                              # head offsets are from its parked bottom, 330
    tl = Timeline(dict(s=-760.0, tip=0.0, lift=0.0, cy=0.0, cz=0.0, lid="jar", lid2="holder"))
    tl.go(2.2, s=-440.0).mark("ante")
    tl.go(2.0, s=0.0).mark("inside")
    tl.go(1.3, cy=yc - 300.0).go(0.8, cz=lid_top - zb).mark("grip")
    tl.go(0.6, lid="cap").go(1.2, cz=40.0).mark("lid_off")
    tl.go(1.0, lift=70.0).go(2.2, tip=125.0).mark("poured")
    tl.go(1.6, tip=0.0).go(1.0, lift=0.0)
    tl.go(1.0, cz=lid_top - zb).go(0.4, lid="jar").go(0.8, cz=0.0).mark("lid_back")
    tl.go(1.0, cy=0.0).go(0.8, cz=193.0 - zb).go(0.4, lid2="cap").go(0.8, cz=0.0)
    tl.go(1.0, cy=GB["sjar"][1] - 300.0).go(0.8, cz=193.0 - zb).go(0.4, lid2="jar").go(0.8, cz=0.0)
    tl.go(1.0, cy=0.0).mark("sealed")

    def lid_pos(s):
        if s["lid"] == "jar":
            return (0.0, s["s"], 0.0)
        return (0.0, 300.0 + s["cy"] - yc, zb + s["cz"] - lid_top)

    def lid2_pos(s):
        if s["lid2"] == "holder":
            return (0.0, 0.0, 0.0)
        if s["lid2"] == "jar":
            return (0.0, GB["sjar"][1] - hy, 0.0)
        return (0.0, 300.0 + s["cy"] - hy, zb + s["cz"] - 193.0)

    pivot = (ax, yc + jd / 2, jz + jh)                  # the catch jar's back lip
    inst.joints = {
        "door": Joint("slide", vec=(230.0, 0.0, 0.0)),
        "inner_door": Joint("slide", vec=(0.0, 0.0, 215.0)),
        "load": Track(knots=tl.knots(lambda s: (0.0, s["s"], 0.0))),
        "lifter": Track(knots=tl.knots(lambda s: (0.0, 0.0, s["lift"])), parent="load"),
        "tipper": Turn(axis=(1, 0, 0), pivot=pivot, knots=_turn_knots(tl, lambda s: s["tip"]), parent="lifter"),
        "lid": Track(knots=tl.knots(lid_pos)),
        "lid2": Track(knots=tl.knots(lid2_pos)),
        "capper_y": Track(knots=tl.knots(lambda s: (0.0, s["cy"], 0.0))),
        "capper_z": Track(knots=tl.knots(lambda s: (0.0, 0.0, s["cz"])), parent="capper_y"),
        "needle": Turn(axis=(0, 1, 0), pivot=(gx, p["a_y0"] - 15, az + 60),
                       knots=((0.0, 0.0), (0.15, -230.0), (0.30, 0.0), (0.48, -230.0), (0.63, 0.0), (0.81, -230.0),
                              (1.0, 0.0))),
        "stream": Joint("fade"),
        "fill": Joint("fade"),
    }
    ndl = _piece(inst, "needle")
    ndl.add("gauge needle", box(gx - 2, p["a_y0"] - 16, az + 60, gx + 2, p["a_y0"] - 15, az + 88), "inst_red")
    V = tl.v
    tv = lambda a, b: {k: (a, b) for k in ("load", "lifter", "tipper", "lid", "lid2", "capper_y", "capper_z")}  # noqa
    inst.actions = [
        ("The arm slides the mini antechamber's outer door open. It slides rather than swings, so it never leaves "
         "the tray's footprint.", 1.8, {"door": (0.0, 1.0), **tv(0.0, 0.0)}),
        ("In goes the atomizer's catch jar, sealed, on a sled.", 2.2, {**tv(0.0, V("ante"))}),
        ("Door shut. The PLC pumps the antechamber down and refills it with N2 from the tray's dock line, three "
         "times.", 3.6, {"door": (1.0, 0.0), "needle": (0.0, 1.0)}),
        ("The inner door slides up.", 1.4, {"inner_door": (0.0, 1.0), "~body": (0.0, 0.85), "~inner_door": (0.0, 0.85)}),
        ("The sled runs onto the shelf inside.", 2.0, {**tv(V("ante"), V("inside"))}),
        ("The capper unscrews the jar's lid and lifts it clear.", 3.6, {**tv(V("inside"), V("lid_off"))}),
        ("Two arms lift the jar's cradle and tip it: the powder pours into the storage jar on the balance.", 3.6,
         {**tv(V("lid_off"), V("poured")), "stream": (0.0, 1.0), "fill": (0.0, 1.0)}),
        ("Upright and down again. The capper puts the catch jar's lid back, then screws the storage jar's lid on.",
         5.2,
         {**tv(V("poured"), V("sealed")), "stream": (1.0, 0.0)}),
        ("Sealed under N2, the jar leaves the same way. Purge-only: no purifier to regenerate inside the VLM. "
         "The box is 1100 x 520 x 640 mm; 810 mm tall with its fittings.", 2.6, {"inner_door": (1.0, 0.0), "~body": (0.85, 0.0), "~inner_door": (0.85, 0.0)}),
    ]
    inst.zoom = {5: ((240.0, 170.0, 280.0), 2100.0), 8: "out"}
    inst.labels = [("mini antechamber, 150 mm", (ax, -300, az + 85), (0.80, 0.18)),
                   ("outer door: the arm slides it", (ax + 60, dy0 - 12, az), (0.86, 0.55)),
                   ("220 mm glove ports", (p["ports"][0], Y0 - 22, p["port_z"] + 130), (0.12, 0.20)),
                   ("PLC, O2 and dew point", (550, -121, 480), (0.88, 0.30)),
                   ("N2 purge out: oil bubbler", (-600, 300, Z1 + 110), (0.16, 0.10)),
                   ("antechamber pump", (550, 150, 250), (0.90, 0.72))]
    inst.cam = (-0.35, -1.3, 1.5)
    inst.props = ("load", "lifter", "tipper", "lid", "lid2", "fill")
    return inst


# ===================================================================================================== b. tensile
# ZwickRoell zwickiLine Z5.0 TN, lying on its side (PI 396 1123): upright it is 1289 mm tall, 408 wide and 480 deep,
# 622 deep with its testControl II electronics, 78 kg; 5 kN; 0.0005-600 mm/min; 105 mm test-area depth. ZwickRoell
# says the zwickiLine can be run vertical or horizontal (search-result quote of its product information). Turned on
# its side, its height becomes the tray's length and its width the height: 1289 x 622 x 408 mm, plus our 40 mm base
# plate. The column runs along x, the base at the left; the crosshead pulls to the right; the test area faces the
# opening, so the arm drops the bar in from above between the open jaws. Layout read off ZwickRoell's photos: an
# estimate. The bar: the alloy route's E8 sub-size bar (alloy_models.E8_SUB) faced down to 1.5 mm thick, 6 x 1.5 mm in
# the gauge: 3.7 kN at 412 MPa, 74 % of the 5 kN. The 6 x 6 mm bar as printed needs 14.8 kN.
TH = dict(L=1289.0, Wd=408.0, D=480.0, De=622.0, plate=40.0, base_t=150.0, col=(160.0, 160.0), throat=105.0,
          bar_t=1.5, bar_w=6.0, bar_L=100.0, bar_C=10.0, bar_A=32.0, travel=40.0)
UTS, BAR_KN = 412.0, 412.0 * 6.0 * 1.5 / 1000.0          # MPa; kN for the 6 x 1.5 mm gauge


def _bar_half(x0, x1, xm, y, z, t, w, C, A, left=True):
    """One half of a flat E8 sub-size bar along x, faces normal to y: the grip end (C wide) and half the reduced
    section (w wide), joined by a straight taper (the 6 mm fillet, simplified)."""
    hw, hc = w / 2, C / 2
    if left:
        pts = [(x0, -hc), (xm - A / 2 - 6, -hc), (xm - A / 2, -hw), (xm, -hw), (xm, hw), (xm - A / 2, hw),
               (xm - A / 2 - 6, hc), (x0, hc)]
    else:
        pts = [(xm, -hw), (xm + A / 2, -hw), (xm + A / 2 + 6, -hc), (x1, -hc), (x1, hc), (xm + A / 2 + 6, hc),
               (xm + A / 2, hw), (xm, hw)]
    return cq.Workplane("XZ").polyline(pts).close().extrude(t / 2, both=True).translate((0, y, z))


def tensile_h() -> Instrument:
    p = TH
    W, D, H = FOOTPRINTS["tensile_h"][:3]
    inst = Instrument("tensile_h", "Tensile tester lying on its side, on a tray", "ZwickRoell zwickiLine Z5.0 TN",
                      (W, D, H), "ZwickRoell PI 396 1123 (Z5.0 TN 1289 x 408 x 480 mm, 622 deep with electronics, "
                      "78 kg, 5 kN); horizontal use per ZwickRoell's product information; layout from photos")
    L, zp = p["L"], p["plate"]
    xL, xR = -L / 2, L / 2
    yf, yb = -311.0, 311.0                            # overall: 622 deep with the electronics
    ybase = yf + p["D"]                               # the frame's back, 169; the electronics behind it
    zc = zp + p["Wd"] / 2                             # the load axis' height: the frame's mid-width, 244
    cw, cd = p["col"]
    ycf = ybase - cd                                  # the column's front face, 9
    yax = ycf - p["throat"]                           # the load axis, 105 mm in front of the column: -96
    body = _piece(inst, "body")
    body.add("base plate", box(xL, yf, 0, xR, yb, zp), "r7_frame")
    xb1 = xL + p["base_t"]
    body.add("frame base", box(xL, yf, zp, xb1, ybase, zp + p["Wd"]).edges("|Y").fillet(20), "r7_zwick")
    body.add("base badge", box(xL + 20, yf - 1, zp + 300, xL + 130, yf, zp + 330), "r7_zwick_green")
    body.add("e-stop", _ycyl(36, 16, x=xL + 75, y=yf - 16, z=zp + 120), "inst_red")
    body.add("e-stop collar", _ycyl(50, 4, x=xL + 75, y=yf - 4, z=zp + 120), "inst_yellow")
    body.add("column", box(xb1, ycf, zc - cw / 2, xR - 30, ybase, zc + cw / 2).edges("|X").fillet(12), "r7_zwick")
    body.add("column slot", box(xb1 + 30, ycf - 0.3, zc - 12, xR - 60, ycf + 2, zc + 12), "r7_zwick_dk")
    body.add("top cap", box(xR - 30, ycf - 10, zc - cw / 2 - 10, xR, ybase, zc + cw / 2 + 10), "r7_zwick_dk")
    body.add("electronics", box(xL, ybase, zp, xR - 200, yb, zp + 300), "r7_zwick_dk")
    body.add("electronics badge", box(xL + 40, ybase + 20, zp + 300, xL + 240, ybase + 120, zp + 301),
             "r7_zwick_green")
    # the lower grip on the base's face: a pneumatic parallel grip, its body to the left of its jaws
    xs = xb1 + 90 + 50 + 0.5                           # the bar's centre: grip body 90, then its 50 mm half
    gy0, gy1 = yax - 30, yax + 30
    body.add("lower grip", box(xb1, gy0, zc - 30, xb1 + 90, gy1, zc + 30), "steel")
    body.add("lower grip cylinder", _xcyl(50, 40, x=xb1, y=yax, z=zc - 55), "r7_zwick_dk")
    t2 = p["bar_t"] / 2
    xh0 = xs + 50.5                                   # the upper grip's body starts right of its jaws
    xh = _piece(inst, "crosshead")
    xh.add("upper grip", box(xh0, gy0, zc - 30, xh0 + 90, gy1, zc + 30), "steel")
    xh.add("load cell", _xcyl(70, 50, x=xh0 + 90, y=yax, z=zc), "chrome")
    xh.add("load cell band", _xcyl(72, 10, x=xh0 + 110, y=yax, z=zc), "inst_red")
    xa0 = xh0 + 140
    xh.add("crosshead", box(xa0, yax - 45, zc - 45, xa0 + 70, ycf - 0.5, zc + 45).edges("|Y").fillet(8),
           "r7_zwick_dk")
    jaws = {"jaw_l_f": (xb1 + 90.5, -1), "jaw_l_b": (xb1 + 90.5, 1), "jaw_u_f": (xs + 20.5, -1),
            "jaw_u_b": (xs + 20.5, 1)}
    for nm, (x0, sgn) in jaws.items():
        y_in = yax + sgn * t2
        y0, y1 = (y_in - 14, y_in) if sgn < 0 else (y_in, y_in + 14)
        _piece(inst, nm).add(nm, box(x0, y0, zc - 15, x0 + 29.5, y1, zc + 15), "r7_zwick_dk")
    # the bar, in two halves that are one bar until it breaks
    for nm, left in (("specimen", True), ("specimen_b", False)):
        _piece(inst, nm).add(nm, _bar_half(xs - 50, xs + 50, xs, yax, zc, p["bar_t"], p["bar_w"], p["bar_C"],
                                           p["bar_A"], left), "sample")
    inst.meshes["readout"] = _dummy((xs, yax, zc))
    up = 220.0
    dpull, dsep = 3.5, 24.0                            # mm of crosshead travel to fracture, and after it
    vs = up / (up + dsep)
    vp = (up + dpull) / (up + dsep)
    inst.joints = {
        "crosshead": Joint("slide", vec=(p["travel"], 0, 0)),
        "specimen": Joint("path", path=((0, 0, up), (0, 0, 0))),
        "specimen_b": Joint("path", path=((0, 0, up), (0, 0, 0), (dsep, 0, 0))),
        "jaw_u_f": Joint("slide", vec=(0, -6, 0), parent="crosshead", v0=1.0),
        "jaw_u_b": Joint("slide", vec=(0, 6, 0), parent="crosshead", v0=1.0),
        "jaw_l_f": Joint("slide", vec=(0, -6, 0), v0=1.0),
        "jaw_l_b": Joint("slide", vec=(0, 6, 0), v0=1.0),
        "readout": Joint("slide", vec=(1, 0, 0)),
    }
    c1, c2 = dpull / p["travel"], dsep / p["travel"]
    jaws_to = lambda a, b: {k: (a, b) for k in jaws}  # noqa: E731
    inst.actions = [
        ("A zwickiLine Z5.0 lying on its side: ZwickRoell says it can run horizontal. 1289 mm long, 408 mm tall "
         "this way, 78 kg.", 2.2, {**jaws_to(1.0, 1.0), "specimen": (0.0, 0.0), "specimen_b": (0.0, 0.0)}),
        ("The arm lowers the bar between the open jaws from above (it holds the bar by its middle; not drawn).", 2.4,
         {"specimen": (0.0, 1.0), "specimen_b": (0.0, vs)}),
        ("The pneumatic jaws close on both ends.", 1.2, {**jaws_to(1.0, 0.0)}),
        (f"The crosshead pulls at constant speed. An E8 sub-size bar faced to 6 x 1.5 mm: {BAR_KN:.1f} kN at "
         f"{UTS:.0f} MPa, within the 5 kN.", 3.6,
         {"crosshead": (0.0, c1), "specimen_b": (vs, vp), "readout": (0.0, 1.0)}),
        ("Fracture. The crosshead moves on 20 mm to show the break.", 1.8,
         {"crosshead": (c1, c2), "specimen_b": (vp, 1.0)}),
        ("The jaws open for the arm. The alloy route's 6 x 6 mm bar needs 14.8 kN: no motorized horizontal machine "
         "with a published size pulls that.", 2.6, {**jaws_to(0.0, 1.0), "readout": (1.0, 0.0)}),
    ]
    inst.zoom = {1: ((xs, yax, zc + 20), 480.0), 5: "out"}
    inst.labels = [("zwickiLine Z5.0 TN, on its side", (xR - 300, ycf, zc + cw / 2), (0.70, 0.16)),
                   ("pneumatic grips", (xb1 + 45, gy0, zc + 30), (0.14, 0.24)),
                   ("crosshead and load cell", (xa0 + 35, yax - 45, zc + 45), (0.56, 0.20)),
                   ("testControl II electronics", (xL + 300, yb, zp + 300), (0.30, 0.10))]
    inst.cam = (0.55, -1.6, 1.05)
    inst.props = ("specimen", "specimen_b")
    return inst


def _draw_tensile(sc, img, s):
    """The force-travel curve, drawn as the crosshead moves (an illustration, and labelled so)."""
    from PIL import ImageDraw
    from scene import font
    key = "tensile_h:"
    a = min(1.0, _gv(sc, key + "readout"))
    if a <= 0.02:
        return
    m = sc.gmat.get(key + "crosshead")
    d_mm = 0.0 if m is None else float(m[0, 3])
    W, H = img.size
    dr = ImageDraw.Draw(img, "RGBA")
    al = int(255 * a)
    x0, y0, x1, y1 = W - 300 * s, 46 * s, W - 12 * s, 46 * s + 200 * s
    dr.rounded_rectangle((x0, y0, x1, y1), 6 * s, fill=(255, 255, 255, int(236 * a)), outline=(150, 156, 164, al))
    dr.text((x0 + 10 * s, y0 + 6 * s), "Force vs crosshead travel", font=font(13 * s, bold=True),
            fill=(20, 20, 24, al))
    px0, px1, py0, py1 = x0 + 40 * s, x1 - 14 * s, y1 - 44 * s, y0 + 34 * s
    dr.line((px0, py0, px1, py0), fill=(90, 94, 100, al), width=max(1, int(s)))
    dr.line((px0, py0, px0, py1), fill=(90, 94, 100, al), width=max(1, int(s)))
    fmax, dmax = 5.0, 4.0
    dr.text((px0 - 34 * s, py1 - 6 * s), "5 kN", font=font(10.5 * s), fill=(80, 84, 90, al))
    dr.text((px1 - 34 * s, py0 + 2 * s), "4 mm", font=font(10.5 * s), fill=(80, 84, 90, al))

    def f_of(dd):
        e = 0.45
        return BAR_KN * 0.78 * dd / e if dd < e else BAR_KN * (0.78 + 0.22 * (1 - math.exp(-(dd - e) / 0.9)))
    end = min(d_mm, 3.5)
    pts = [(px0 + (px1 - px0) * (end * i / 60) / dmax, py0 + (py1 - py0) * f_of(end * i / 60) / fmax)
           for i in range(61)]
    if d_mm > 3.5:
        pts.append((px0 + (px1 - px0) * 3.55 / dmax, py0))
    dr.line(pts, fill=(30, 60, 140, al), width=max(2, int(2 * s)))
    yl = py0 + (py1 - py0) * BAR_KN / fmax
    dr.line((px0, yl, px1, yl), fill=(150, 40, 30, int(110 * a)), width=1)
    dr.text((x0 + 10 * s, y1 - 38 * s), f"peak {BAR_KN:.1f} kN = {UTS:.0f} MPa x 9 mm2", font=font(11 * s),
            fill=(30, 60, 140, al))
    dr.text((x0 + 10 * s, y1 - 20 * s), "Illustrative curve, not a measurement", font=font(11 * s),
            fill=(150, 40, 30, al))


PLOTS["instruments/tensile_h"] = _draw_tensile


# ===================================================================================================== c. hardness
# Mitutoyo HM-220 Type D (Mitutoyo catalogue section K): micro-Vickers, 0.4903 mN-19.61 N (0.05 gf-2 kgf); a
# motorized turret for up to 4 objectives and 2 indenters; Type D adds a motorized XY stage (50 x 50 mm, table 130 x
# 130 mm, 25 mm/s), motorized focus (1.4 mm) and AVPAK on a specified PC, which finds, measures and reports each indent.
# Main unit 315 x 671 x 595 mm, 43 kg. The layout (base, back column, head over the stage, camera on top) is read off
# Mitutoyo's photos: an estimate. Drawn: the Vickers indenter and three objectives, the 50x at the front. The indents
# are drawn 1.5 mm across and 3 mm apart; a real HV0.5 indent in AlSi10Mg (about 125 HV) is 86 um across.
HM = dict(W=315.0, D=671.0, H=595.0, base_h=140.0, ax=(0.0, -170.0), tur_c=(0.0, -120.0), tur_r=50.0, tip_z=280.0,
          top=277.0, step=3.0, n=5)


def hardness() -> Instrument:
    p = HM
    W, D, H = FOOTPRINTS["hardness"][:3]
    inst = Instrument("hardness", "Automatic micro-Vickers hardness tester", "Mitutoyo HM-220 Type D (AVPAK)",
                      (W, D, H), "Mitutoyo catalogue section K (HM-210/220: 315 x 671 x 595 mm, 43 kg; Type D "
                      "motorized XY stage and autofocus; motorized turret); layout from Mitutoyo's photos")
    w, d, h = p["W"], p["D"], p["H"]
    ax, ay = p["ax"]
    tx, ty = p["tur_c"]
    body = _piece(inst, "body")
    body.add("base", rbox(w, d, p["base_h"], 24).edges(">Z").fillet(10), "r7_mitu")
    body.add("base panel", box(-110, -d / 2 - 1, 40, 110, -d / 2, 110), "r7_mitu_dk")
    body.add("elevating screw", cyl(90, 60, x=ax, y=ay, z=p["base_h"]), "r7_mitu_dk")
    body.add("handwheel", _xcyl(110, 20, x=-157.5 - 20, y=ay + 40, z=90), "r7_mitu_dk")
    body.add("Y carriage", box(-90, ay - 90, 200, 90, ay + 90, 222), "r7_mitu_dk")
    body.add("column", rbox(200, 255, h - 35 - p["base_h"], 30, y=d / 2 - 127.5, z=p["base_h"]), "r7_mitu")
    body.add("head", rbox(230, 586, 180, 30, y=d / 2 - 293, z=380).edges(">Z").fillet(14), "r7_mitu")
    body.add("head band", box(-116, -251, 470, 116, d / 2 - 30, 480), "r7_mitu_dk")
    body.add("camera", rbox(50, 60, 35, 8, x=ax, y=ay - 30 + 30, z=560), "r7_mitu_dk")
    # the AVPAK PC and the joystick beside it (estimate)
    body.add("PC", box(185, 0, 0, 355, 335, 330), "inst_dark")
    body.add("PC light", box(250, -1.5, 280, 290, 0, 286), "led_blue")
    body.add("joystick box", box(205, -320, 0, 335, -200, 45).edges(">Z").fillet(8), "r7_mitu_dk")
    body.add("joystick", cyl(14, 50, x=290, y=-260, z=45).union(cq.Workplane("XY").sphere(11).translate((290, -260, 98))),
             "inst_black")
    stx = _piece(inst, "stage_x")
    stx.add("X carriage", box(-75, ay - 65, 222, 75, ay + 65, 244), "r7_mitu_dk")
    stx.add("table", rbox(130, 130, 8, 6, x=ax, y=ay, z=244), "steel")
    tur = _piece(inst, "turret")
    tur.add("turret", cyl(150, 25, x=tx, y=ty, z=355), "r7_mitu_dk")
    r = p["tur_r"]
    for nm, ang, dia in (("objective 50x", -90.0, 26.0), ("objective 10x", 180.0, 28.0), ("objective 100x", 90.0, 24.0)):
        ox, oy = tx + r * math.cos(math.radians(ang)), ty + r * math.sin(math.radians(ang))
        tur.add(nm, cyl(dia, 355 - p["tip_z"], x=ox, y=oy, z=p["tip_z"]), "chrome")
        tur.add(nm + " band", cyl(dia + 2, 8, x=ox, y=oy, z=330), "r7_mitu_dk")
    ind = _piece(inst, "indenter")
    ix, iy = tx + r, ty
    ind.add("indenter", cyl(24, 60, x=ix, y=iy, z=p["tip_z"] + 15), "steel")
    ind.add("diamond", cq.Workplane().add(cq.Solid.makeCone(0.1, 6.0, 15.0, cq.Vector(ix, iy, p["tip_z"]),
                                                            cq.Vector(0, 0, 1))), "r7_carbide")
    smp = _piece(inst, "sample")
    smp.add("mount", cyl(31.75, 25, x=ax, y=ay, z=252), "mount_red")
    smp.add("polished face", cyl(24, 0.4, x=ax, y=ay, z=p["top"] - 0.2), "sample")
    inst.meshes["readout"] = _dummy((ax, ay, 300))
    # the series on one timeline: stage step, turret to the indenter, press, dent, turret back, read
    n, step = p["n"], p["step"]
    tl = Timeline(dict(sx=0.0, tur=0.0, ind=0.0, **{f"d{i}": 0.0 for i in range(n)}))
    for i in range(n):
        if i:
            tl.go(0.5, sx=i * step)
        tl.go(0.8, tur=-90.0).go(0.5, ind=-2.9).go(0.5, **{f"d{i}": 1.0}).go(0.4, ind=0.0)
        if i == 0:
            tl.mark("pressed")
        tl.go(0.8, tur=0.0).go(0.7)
        if i == 0:
            tl.mark("read")
    for i in range(n):
        dn = _piece(inst, f"dent{i}")
        sq = box(-0.75, -0.75, 0, 0.75, 0.75, 0.3).rotate((0, 0, 0), (0, 0, 1), 45)
        dn.add(f"indent {i}", sq.translate((ax - i * step, ay, p["top"] - 1.0)), "r7_dent")
    inst.joints = {
        "stage_x": Track(knots=tl.knots(lambda s: (s["sx"], 0.0, 0.0))),
        "sample": Joint("path", path=((0, -260, 90), (0, -60, 0), (0, 0, 0)), parent="stage_x"),
        "turret": Turn(axis=(0, 0, 1), pivot=(tx, ty, 0), knots=_turn_knots(tl, lambda s: s["tur"])),
        "indenter": Track(knots=tl.knots(lambda s: (0.0, 0.0, s["ind"])), parent="turret"),
        "readout": Joint("slide", vec=(1, 0, 0)),
        **{f"dent{i}": Track(knots=tl.knots(lambda s, i=i: (0.0, 0.0, s[f"d{i}"])), parent="sample")
           for i in range(n)},
    }
    tv = lambda a, b: {k: (a, b) for k in ("stage_x", "turret", "indenter", *[f"dent{i}" for i in range(n)])}  # noqa
    V = tl.v
    inst.actions = [
        ("A polished 1.25 in mount goes onto the motorized XY stage (50 x 50 mm travel).", 2.4,
         {"sample": (0.0, 1.0), **tv(0.0, 0.0)}),
        ("The motorized turret swings the Vickers indenter over it; the force motor presses: HV0.5, 4.9 N.", 3.2,
         {**tv(0.0, V("pressed"))}),
        ("The 50x objective comes back. The 3 MP camera images the indent; AVPAK measures both diagonals.", 2.6,
         {**tv(V("pressed"), V("read")), "readout": (0.0, 1.0)}),
        ("A series across the coupon: the stage steps (0.5 mm apart; drawn 3 mm), and each indent is made and read "
         "the same way, unattended.", 6.0, {**tv(V("read"), 1.0)}),
        ("315 x 671 x 595 mm and 43 kg: on a tray, with 260 mm to spare under the opening. HM-220: 0.05 gf to "
         "2 kgf, enough for HV0.5 on Al alloys.", 2.6, {"readout": (1.0, 0.0)}),
    ]
    inst.zoom = {1: ((ax, ay, 300.0), 520.0), 4: "out"}
    inst.labels = [("motorized turret: indenter, objectives", (tx - 75, ty, 367), (0.12, 0.30)),
                   ("motorized XY stage", (-75, ay - 65, 233), (0.12, 0.70)),
                   ("3 MP camera", (ax, ay, 595), (0.40, 0.10)),
                   ("AVPAK PC and joystick", (270, 0, 300), (0.86, 0.30))]
    inst.cam = (0.9, -1.6, 0.85)
    inst.props = ("sample",)
    return inst


def _draw_hardness(sc, img, s):
    """The indent as AVPAK sees it, with its diagonals (an illustration, and labelled so)."""
    from PIL import ImageDraw
    from scene import font
    a = min(1.0, _gv(sc, "hardness:readout"))
    if a <= 0.02:
        return
    W, H = img.size
    dr = ImageDraw.Draw(img, "RGBA")
    al = int(255 * a)
    x0, y0, x1, y1 = W - 270 * s, 46 * s, W - 12 * s, 46 * s + 250 * s
    dr.rounded_rectangle((x0, y0, x1, y1), 6 * s, fill=(255, 255, 255, int(236 * a)), outline=(150, 156, 164, al))
    dr.text((x0 + 10 * s, y0 + 6 * s), "AVPAK: the indent at 50x", font=font(13 * s, bold=True), fill=(20, 20, 24, al))
    cx, cy, R = (x0 + x1) / 2, y0 + 120 * s, 70 * s
    dr.rectangle((cx - 1.4 * R, cy - 1.15 * R, cx + 1.4 * R, cy + 1.15 * R), fill=(150, 152, 156, al))
    dr.polygon([(cx, cy - R), (cx + R, cy), (cx, cy + R), (cx - R, cy)], fill=(40, 42, 46, al))
    dr.line((cx - R, cy, cx + R, cy), fill=(80, 200, 255, al), width=max(1, int(1.5 * s)))
    dr.line((cx, cy - R, cx, cy + R), fill=(255, 210, 60, al), width=max(1, int(1.5 * s)))
    dr.text((x0 + 10 * s, y1 - 56 * s), "d1 86.2 um   d2 85.9 um", font=font(12 * s, mono=True), fill=(30, 60, 140, al))
    dr.text((x0 + 10 * s, y1 - 38 * s), "125 HV0.5", font=font(15 * s, bold=True), fill=(30, 60, 140, al))
    dr.text((x0 + 10 * s, y1 - 18 * s), "Illustrative values, not a measurement", font=font(11 * s),
            fill=(150, 40, 30, al))


PLOTS["instruments/hardness"] = _draw_hardness


# ===================================================================================================== d. CNC
# Makera Carvera (Makera's spec): 580 x 520 x 540 mm, about 50 kg, 840 mm tall with the lid open; work area 360 x 240 x
# 140 mm; a 6-tool automatic changer with auto probing; 200 W spindle, ER11. Its lid is lifted by hand, and it has no
# automation interface: the lid actuator and the pneumatic vise here are ours (sizes estimated). The motion layout (a
# gantry over a fixed bed, the tool rack at the bed's left) is read off Makera's photos: an estimate. Fits a tray: 540
# mm tall, and the lid opened 40 degrees reaches 836 mm. 200 W is light for aluminium: facing and small profiles at
# shallow depths, not hogging. The job: face a printed blank's as-built skin.
CV = dict(W=580.0, D=520.0, H=540.0, bed_z=245.0, hinge=(200.0, 540.0), lid_deg=-40.0, nose=360.0, sp_y=-77.0,
          slots=((-185.0, -100.0), (-185.0, -60.0), (-185.0, -20.0), (-185.0, 20.0), (-185.0, 60.0), (-185.0, 100.0)),
          tool_top=302.0, face_z=300.0)


def _tool(x, y, top, d=6.0, flute=(0.55, 0.56, 0.60)):
    """An end mill in its holder collar, standing with its collar's top at `top`."""
    return (cyl(16, 12, x=x, y=y, z=top - 12), cyl(d, 38, x=x, y=y, z=top - 50))


def cnc() -> Instrument:
    p = CV
    W, D, H = FOOTPRINTS["cnc"][:3]
    inst = Instrument("cnc", "Desktop CNC mill with a tool changer, set up for the arm", "Makera Carvera",
                      (W, D, H), "Makera's Carvera spec (580 x 520 x 540 mm, 50 kg, 840 mm lid open, 360 x 240 x "
                      "140 mm, 6-tool changer, 200 W); lid actuator and pneumatic vise ours; layout from photos")
    w, d, h = p["W"], p["D"], p["H"]
    bz = p["bed_z"]
    hy, hz = p["hinge"]
    body = _piece(inst, "body")
    body.add("base", box(-w / 2, -d / 2, 0, w / 2, d / 2, bz - 15).edges("|Z").fillet(20), "r7_carvera")
    body.add("front panel", box(-120, -d / 2 - 1, 90, 120, -d / 2, 170), "inst_dark")
    body.add("front screen", box(-60, -d / 2 - 1.5, 110, 20, -d / 2 - 1, 150), "screen_on")
    body.add("back wall", box(-w / 2, hy, bz - 15, w / 2, d / 2, h).edges("|Z").fillet(10), "r7_carvera")
    for x0 in (-w / 2, w / 2 - 10):                    # the side sills, under the lid's sides
        body.add(f"sill {x0:.0f}", box(x0, -d / 2 + 10, bz - 15, x0 + 10, hy, 300), "r7_carvera")
    for x0 in (-275.0, 255.0):                         # the gantry's rails on the sills
        body.add(f"rail {x0:.0f}", box(x0, -240, 290, x0 + 20, hy, 300), "steel")
    body.add("bed", box(-200, -150, bz - 15, 200, 150, bz), "aluminium")
    for k in range(5):
        y = -120 + 60 * k
        body.add(f"T-slot {k}", box(-200, y - 4, bz - 0.4, 200, y + 4, bz + 0.2), "inst_dark")
    body.add("tool rack", box(-200, -125, 280, -170, 125, 290).cut(
        cq.Workplane("XY").pushPoints(list(p["slots"])).circle(4.5).extrude(12).translate((0, 0, 279))), "inst_dark")
    body.add("rack post", box(-200, -125, bz, -190, 125, 280), "inst_dark")
    for i, (x, y) in enumerate(p["slots"][2:]):
        col, sh = _tool(x, y, p["tool_top"])
        body.add(f"tool {i + 2} collar", col, "steel")
        body.add(f"tool {i + 2}", sh, "r7_carbide")
    # the pneumatic vise (ours) with its parallels
    body.add("vise base", box(0, -70, bz, 120, 70, bz + 20), "steel")
    body.add("fixed jaw", box(0, 20, bz + 20, 120, 32, 300), "steel")
    body.add("air cylinder", box(20, -95, bz + 4, 100, -71, bz + 28), "inst_blue")
    for yy in (-18.0, 12.0):
        body.add(f"parallel {yy:.0f}", box(5, yy, bz + 20, 115, yy + 6, 270), "steel")
    body.add("lid actuator", cyl(30, 220, x=w / 2 + 15, y=hy + 20, z=300), "inst_dark")
    body.add("actuator mount", box(w / 2, hy + 5, 300, w / 2 + 30, hy + 35, 315), "inst_dark")
    jaw = _piece(inst, "jaw")
    jaw.add("moving jaw", box(0, -32, bz + 20, 120, -20, 300), "steel")
    # the lid: tinted top, front and sides, hinged at the back top
    lid = _piece(inst, "lid")
    lid.add("lid top", box(-w / 2, -d / 2, h - 10, w / 2, hy, h), "r7_carvera_lid")
    lid.add("lid front", box(-w / 2, -d / 2, bz - 15, w / 2, -d / 2 + 10, h - 10), "r7_carvera_lid")
    for sx in (-1, 1):
        x0 = w / 2 - 10 if sx > 0 else -w / 2
        lid.add(f"lid side {sx}", box(x0, -d / 2 + 10, 300, x0 + 10, hy, h - 10), "r7_carvera_lid")
    lid.add("lid handle", box(-80, -d / 2 - 14, h - 60, 80, -d / 2, h - 40), "inst_dark")
    lid.add("lid arm", box(w / 2, hy - 50, h - 40, w / 2 + 10, hy - 5, h - 10), "inst_dark")
    # the gantry (y), the carriage (x) and the spindle (z)
    gan = _piece(inst, "gantry")
    gan.add("beam", box(-262, -20, 440, 262, 20, 490), "inst_dark")
    for sx in (-1, 1):
        x0 = 255 if sx > 0 else -275
        gan.add(f"upright {sx}", box(x0, -25, 300, x0 + 20, 25, 440), "inst_dark")
    car = _piece(inst, "carriage")
    car.add("carriage", box(-40, -50, 420, 40, -20.5, 500), "r7_carvera")
    spn = _piece(inst, "spindle")
    sy = p["sp_y"]
    spn.add("spindle", cyl(52, 120, x=0, y=sy, z=p["nose"] + 20), "steel")
    spn.add("spindle cap", cyl(54, 10, x=0, y=sy, z=p["nose"] + 120), "inst_dark")
    spn.add("nose", cyl(22, 20, x=0, y=sy, z=p["nose"]), "chrome")
    tools = {}
    for nm, (x, y) in (("tool_a", p["slots"][0]), ("tool_b", p["slots"][1])):
        col, sh = _tool(x, y, p["tool_top"])
        tp = _piece(inst, nm)
        tp.add(nm + " collar", col, "steel")
        tp.add(nm, sh, "r7_carbide")
        tools[nm] = (x, y)
    # the part: a printed blank, its as-printed skin on top
    part = _piece(inst, "part")
    part.add("blank", box(10, -19.8, 270, 110, 19.8, p["face_z"]), "sample")
    stock = _piece(inst, "stock")
    stock.add("as-printed skin", box(10, -19.8, p["face_z"], 110, 19.8, p["face_z"] + 2), "r7_al_powder")
    # one timeline: gantry y, carriage x, spindle z, and which tool rides the spindle
    tl = Timeline(dict(gy=120.0, cx=150.0, sz=20.0, a="rack", b="rack"))
    ga, gb = tools["tool_a"][1] - sy, tools["tool_b"][1] - sy
    grab = p["tool_top"] - p["nose"]
    tl.go(1.4, cx=tools["tool_a"][0], gy=ga).go(0.8, sz=grab).go(0.3, a="sp").go(0.8, sz=20.0).mark("tool_a")
    tl.go(1.2, cx=10.0, gy=-15.0 - sy).go(0.6, sz=p["face_z"] + 50.0 - p["nose"])
    for k, yy in enumerate((-15.0, -7.5, 0.0, 7.5, 15.0)):
        if k:
            tl.go(0.3, gy=yy - sy)
        tl.go(1.2, cx=110.0 if k % 2 == 0 else 10.0)
    tl.go(0.6, sz=20.0).mark("faced")
    tl.go(1.4, cx=tools["tool_a"][0], gy=ga).go(0.8, sz=grab).go(0.3, a="rack").go(0.8, sz=20.0)
    tl.go(0.6, gy=gb).go(0.8, sz=grab).go(0.3, b="sp").go(0.8, sz=20.0).mark("tool_b")
    tl.go(1.4, cx=150.0, gy=120.0)

    def tool_off(name, key):
        tx, ty = tools[name]

        def f(s):
            if s[key] == "rack":
                return (0.0, 0.0, 0.0)
            return (s["cx"] - tx, sy + s["gy"] - ty, p["nose"] + s["sz"] - p["tool_top"])
        return f
    inst.joints = {
        "lid": Joint("hinge", axis=(1, 0, 0), pivot=(0, hy, hz), deg=p["lid_deg"]),
        "jaw": Joint("slide", vec=(0, -25, 0), v0=1.0),
        "part": Joint("path", path=((0, -420, 200), (0, -180, 140), (0, 0, 80), (0, 0, 0))),
        "stock": Joint("fade", parent="part", v0=1.0),
        "gantry": Track(knots=tl.knots(lambda s: (0.0, s["gy"], 0.0))),
        "carriage": Track(knots=tl.knots(lambda s: (s["cx"], 0.0, 0.0)), parent="gantry"),
        "spindle": Track(knots=tl.knots(lambda s: (0.0, 0.0, s["sz"])), parent="carriage"),
        "tool_a": Track(knots=tl.knots(tool_off("tool_a", "a"))),
        "tool_b": Track(knots=tl.knots(tool_off("tool_b", "b"))),
    }
    V = tl.v
    tv = lambda a, b: {k: (a, b) for k in ("gantry", "carriage", "spindle", "tool_a", "tool_b")}  # noqa: E731
    top = hz + (d / 2 + hy) * math.sin(math.radians(-p["lid_deg"]))
    inst.actions = [
        (f"The lid actuator (ours: Makera's lid is lifted by hand) opens the lid. Open, it reaches {top:.0f} mm, "
         "under the 856.5 mm.", 2.0, {"lid": (0.0, 1.0), **tv(0.0, 0.0), "stock": (1.0, 1.0)}),
        ("The arm sets a printed blank on the parallels in the open vise.", 2.4, {"part": (0.0, 1.0)}),
        ("The pneumatic vise (ours) clamps it, and the lid closes.", 2.0, {"jaw": (1.0, 0.0), "lid": (1.0, 0.0)}),
        ("Tool change: the spindle takes a 6 mm end mill from the 6-tool changer.", 3.2, {**tv(0.0, V("tool_a"))}),
        ("It faces the top: the as-printed skin comes off in five passes.", 7.0,
         {**tv(V("tool_a"), V("faced")), "stock": (1.0, 0.0)}),
        ("Another change: the end mill goes back and the next tool comes on.", 4.6,
         {**tv(V("faced"), V("tool_b"))}),
        ("Park. The lid opens and the vise lets go for the arm. 200 W: light passes in aluminium, not hogging.", 2.8,
         {**tv(V("tool_b"), 1.0), "lid": (0.0, 1.0), "jaw": (0.0, 1.0)}),
    ]
    inst.zoom = {3: ((-40.0, 0.0, 320.0), 900.0), 6: "out"}
    inst.labels = [("6-tool changer", (-185, -125, 290), (0.10, 0.30)),
                   ("pneumatic vise (ours)", (60, -70, bz + 20), (0.20, 0.78)),
                   ("lid actuator (ours)", (w / 2 + 15, hy + 20, 480), (0.88, 0.22)),
                   ("200 W spindle", (0, sy - 26, p["nose"] + 80), (0.62, 0.12))]
    inst.cam = (0.8, -1.7, 1.0)
    inst.props = ("part", "stock")
    return inst


# ===================================================================================================== e. fume hoods
def _flow_dots(inst, prefix, paths, d=36.0, mat="r7_flow_air", seen=3, frac=0.72):
    """Puffs of air that ride a path each (offsets from the path's last point, where the puff is modelled: inside a
    duct or a blower, so it is hidden at v = 1). Played 0 -> 1, they flow in, through and out of sight. The first
    `seen` legs, the ones in view, take `frac` of the time; the rest, inside the ducts, the remainder."""
    names = []
    for k, pts in enumerate(paths):
        P = np.asarray(pts, float)
        end = P[-1]
        nm = f"{prefix}{k}"
        _piece(inst, nm).add(nm, cq.Workplane("XY").sphere(d / 2).translate(tuple(end)), mat)
        seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
        a, b = np.cumsum(seg[:seen]), np.cumsum(seg[seen:])
        vs = [0.0] + list(frac * a / a[-1]) + list(frac + (1 - frac) * b / b[-1])
        inst.joints[nm] = Track(knots=tuple((float(v), tuple(float(c) for c in q - end)) for v, q in zip(vs, P)),
                                v0=1.0)
        names.append(nm)
    return names


# Labconco Protector XStream, 4 ft (Labconco's product page: an 18 in, 457 mm, sash stop; a 325 mm exhaust collar;
# 440 CFM at 0.08 in static pressure, from Fisher's listing; 1219 x 958 x 1499 mm and about 200 kg from Fisher's and
# Labrepco's listings). On a base cabinet and an epoxy work surface, 900 + 32 mm: our estimate of Labconco's own. The
# arm reaches in under the raised sash, as a person does. Look from Labconco's photos (white, a vertical-rising sash,
# an airfoil sill, a slotted rear baffle): an estimate.
FH = dict(W=1219.0, D=958.0, Hh=1499.0, cab=900.0, top=32.0, post=100.0, sash=(960.0, 1750.0), stop=457.0,
          collar=325.0)


def fumehood() -> Instrument:
    p = FH
    W, D = p["W"], p["D"]
    z0 = p["cab"] + p["top"]                          # the work surface, 932
    zt = z0 + p["Hh"]                                 # the hood's top, 2431
    inst = Instrument("fumehood", "Ducted fume hood, on the floor beside the VLM", "Labconco Protector XStream 4 ft",
                      (W, D, zt), "Labconco's XStream page (18 in sash stop, 325 mm collar); 4 ft size from Fisher's "
                      "and Labrepco's listings (1219 x 958 x 1499 mm); base cabinet estimated", floor=True)
    xw, yf, yb = W / 2, -D / 2, D / 2
    xi = xw - p["post"]
    body = _piece(inst, "body")
    body.add("base cabinet", box(-xw, yf + 40, 0, xw, yb, p["cab"]), "r7_lab_white")
    for x0 in (-xw + 15, 5.0):
        body.add(f"cabinet door {x0:.0f}", box(x0, yf + 38, 60, x0 + xw - 20, yf + 40, p["cab"] - 40), "r7_liner")
        body.add(f"cabinet handle {x0:.0f}", box(x0 + xw / 2 - 40, yf + 30, p["cab"] - 110, x0 + xw / 2 + 40,
                                                 yf + 38, p["cab"] - 95), "steel")
    body.add("work surface", box(-xw, yf, p["cab"], xw, yb, z0), "r7_epoxy")
    for sx in (-1, 1):
        x0 = xi if sx > 0 else -xw
        body.add(f"post {sx}", box(x0, yf, z0, x0 + p["post"], yb, zt - 200), "r7_lab_white")
    body.add("hood top", box(-xw, yf, zt - 200, xw, yb, zt), "r7_lab_white")
    body.add("back", box(-xi, yb - 30, z0, xi, yb, zt - 200), "r7_lab_white")
    body.add("fascia", box(-xi, yf, p["sash"][1], xi, yf + 20, zt - 200), "r7_lab_white")
    body.add("fascia band", box(-xi, yf - 1, zt - 150, xi, yf, zt - 120), "inst_blue")
    body.add("airfoil", box(-xi, yf, z0, xi, yf + 39, z0 + 28), "steel")
    body.add("baffle", box(-xi, yb - 78, z0 + 28, xi, yb - 66, zt - 240), "r7_liner")
    for k, zz in enumerate((z0 + 60, z0 + 600, zt - 300)):
        body.add(f"baffle slot {k}", box(-xi + 40, yb - 79, zz, xi - 40, yb - 77.5, zz + 30), "inst_dark")
    body.add("light", box(-400, -250, zt - 201, 400, 250, zt - 200), "r7_lab_white")
    body.add("collar", cyl(p["collar"], 150, x=0, y=200, z=zt), "steel")
    body.add("airflow monitor", box(xi + 20, yf - 1, 1600, xi + 80, yf, 1660), "screen_on")
    # the etch: Keller's reagent and a rinse, in beakers on the work surface
    for nm, x, liq in (("etch beaker", -150.0, "r7_keller"), ("rinse beaker", 100.0, "water")):
        body.add(nm, tube(80, 74, 100, x=x, y=-100, z=z0).union(cyl(80, 3, x=x, y=-100, z=z0)), "r7_pc")
        body.add(nm + " liquid", cyl(73, 55, x=x, y=-100, z=z0 + 3), liq)
    body.add("reagent bottle", cyl(70, 160, x=-380, y=150, z=z0), "inst_white")
    body.add("reagent cap", cyl(36, 25, x=-380, y=150, z=z0 + 160), "inst_red")
    sash = _piece(inst, "sash")
    s0, s1 = p["sash"]
    sash.add("sash glass", box(-xi + 5, yf + 30, s0 + 30, xi - 5, yf + 40, s1), "r7_sash")
    sash.add("sash handle", box(-xi + 5, yf + 26, s0, xi - 5, yf + 44, s0 + 30), "aluminium")
    # the coupon: a polished mount, into the etch and then the rinse
    cp = _piece(inst, "load")
    cz = z0 + 20.0
    cp.add("mount", cyl(31.75, 25, x=-150, y=-100, z=cz), "mount_red")
    path = ((0, -600, 470), (0, -350, 220), (0, 0, 130), (0, 0, 0), (0, 0, 130), (250, 0, 130), (250, 0, 0))
    seg = [float(np.linalg.norm(np.subtract(b, a))) for a, b in zip(path[:-1], path[1:])]
    tot = sum(seg)
    v_dip = sum(seg[:3]) / tot
    v_up = sum(seg[:4]) / tot
    paths = []
    for k, x in enumerate((-420.0, -210.0, 0.0, 210.0, 420.0, -315.0, 105.0, 315.0)):
        zz = z0 + 80 + 60 * (k % 3)
        paths.append([(x, yf - 120, zz + 40), (x, yf + 60, zz), (x * 0.9, yb - 120, zz + 30), (x * 0.8, yb - 50, zz + 200),
                      (x * 0.4, yb - 50, zt - 260), (0.0, 200.0, zt + 60)])
    flow = _flow_dots(inst, "flow", paths, d=60.0, seen=3)
    inst.joints.update({"sash": Joint("slide", vec=(0, 0, p["stop"])), "load": Joint("path", path=path)})
    fl = lambda a, b: {k: (a, b) for k in flow}  # noqa: E731
    inst.actions = [
        ("The sash rises to its stop, 457 mm (18 in) open. The arm works through that opening, as a person does.",
         2.2, {"sash": (0.0, 1.0)}),
        ("Air sweeps in under the sash, over the airfoil, through the baffle's slots and up the 325 mm collar to the "
         "building's exhaust.", 3.2, {**fl(0.0, 1.0)}),
        ("A polished Al coupon goes into Keller's reagent (HF, HCl and HNO3 in water) for 10-20 s.", 3.0,
         {"load": (0.0, v_dip)}),
        ("Then into the rinse water, while the hood keeps pulling.", 3.0, {"load": (v_dip, 1.0), **fl(0.0, 1.0)}),
        ("Sash down. HF belongs in a ducted hood. 1219 mm wide, 2.4 m tall with its base: it stands on the floor.",
         2.2, {"sash": (1.0, 0.0)}),
    ]
    inst.labels = [("sash, 457 mm stop", (xi - 200, yf + 30, s1), (0.80, 0.20)),
                   ("325 mm exhaust collar", (0, 200, zt + 150), (0.40, 0.06)),
                   ("baffle slots", (-xi + 100, yb - 79, z0 + 615), (0.12, 0.30)),
                   ("Keller's reagent", (-150, -140, z0 + 90), (0.14, 0.72)),
                   ("airflow monitor", (xi + 50, yf, 1660), (0.88, 0.44))]
    inst.zoom = {2: ((-25.0, -100.0, 1060.0), 1500.0), 4: "out"}
    inst.cam = (0.7, -1.7, 0.75)
    inst.props = ("load",)
    return inst


# Sentry Air Systems ductless fume hood, standard 24 in (Sentry Air's page): 24 D x 26 W x 25 H in outside (610 x 660 x
# 635 mm), 23.5 x 24 x 24 in inside, about 90 lb (41 kg); a separate blower, 13 x 13 x 14.5 in (330 x 330 x 368 mm);
# 100 fpm with HEPA, 60 with carbon. The page gives a 9.25 in (235 mm) access opening for its carbon-steel models: used
# here. The filters sit in the hood's back here and the hose runs over the top to the blower: our layout. Fits a tray:
# 715 mm with the hose. Carbon filters take solvent vapours; HF from Keller's reagent is for the ducted hood.
ST = dict(W=660.0, D=610.0, H=635.0, x0=-515.0, open_z=(25.0, 260.0), blower=(330.0, 330.0, 368.0), bx=185.0)


def fumehood_tray() -> Instrument:
    p = ST
    W, D, H = FOOTPRINTS["fumehood_tray"][:3]
    inst = Instrument("fumehood_tray", "Ductless fume hood for a tray", "Sentry Air Systems ductless hood, 24 in",
                      (W, D, H), "Sentry Air's ductless hood page (standard 24 in: 610 x 660 x 635 mm, about 90 lb; "
                      "blower 13 x 13 x 14.5 in); filter and hose layout ours")
    x0, x1 = p["x0"], p["x0"] + p["W"]
    yf, yb = -p["D"] / 2, p["D"] / 2
    h, t = p["H"], 10.0
    oz0, oz1 = p["open_z"]
    body = _piece(inst, "body")
    body.add("floor", box(x0, yf, 0, x1, yb, t), "inst_light")
    body.add("top", box(x0, yf, h - t, x1, yb, h), "inst_light")
    body.add("back", box(x0, yb - t, t, x1, yb, h - t), "inst_light")
    for xx in (x0, x1 - t):
        body.add(f"side {xx:.0f}", box(xx, yf, t, xx + t, yb - t, h - t), "r7_pc")
    body.add("front", box(x0 + t, yf, oz1 + 20, x1 - t, yf + t, h - t), "r7_pc")
    body.add("opening lip", box(x0 + t, yf, oz1, x1 - t, yf + t, oz1 + 20), "inst_light")
    body.add("front sill", box(x0 + t, yf, t, x1 - t, yf + t, oz0), "inst_light")
    body.add("filters", box(x0 + 30, yb - 60, 30, x1 - 30, yb - t, h - 40), "inst_dark")
    body.add("filter frame", box(x0 + 20, yb - 64, 20, x1 - 20, yb - 60, h - 30).cut(
        box(x0 + 40, yb - 65, 40, x1 - 40, yb - 59, h - 50)), "inst_light")
    body.add("collar", cyl(90, 40, x=(x0 + x1) / 2, y=yb - 60, z=h), "inst_light")
    bw, bd, bh = p["blower"]
    bx0 = p["bx"]
    bxc = bx0 + bw / 2
    body.add("blower", box(bx0, -bd / 2, 0, bx0 + bw, bd / 2, bh).edges("|Z").fillet(12), "inst_light")
    body.add("blower grille", box(bxc - 90, -90, bh, bxc + 90, 90, bh + 2), "inst_dark")
    body.add("blower switch", box(bxc - 30, -bd / 2 - 2, bh - 80, bxc + 30, -bd / 2, bh - 40), "inst_dark")
    body.add("hose", hose([((x0 + x1) / 2, yb - 60, h + 40), ((x0 + x1) / 2, yb - 60, h + 40 + 1),
                           ((x0 + x1) / 2, 160, h + 40), (bxc - 60, 160, h + 40), (bxc - 60, 60, h + 40),
                           (bxc - 60, 60, bh)], 76), "inst_dark")
    load = _piece(inst, "load")
    lx = (x0 + x1) / 2
    load.add("solvent beaker", tube(70, 64, 95, x=lx, y=-40, z=t).union(cyl(70, 3, x=lx, y=-40, z=t)), "r7_pc")
    load.add("solvent", cyl(63, 45, x=lx, y=-40, z=t + 3), "water")
    paths = []
    for k, x in enumerate((-400.0, -300.0, -200.0, -100.0, 0.0, -350.0, -150.0)):
        x = lx + (x + 200.0)
        zz = 70.0 + 50.0 * (k % 3)
        paths.append([(x, yf - 160, zz), (x, yf + 40, zz), (x, yb - 120, zz + 120), (x, yb - 70, h - 120),
                      ((x0 + x1) / 2, yb - 60, h + 30), ((x0 + x1) / 2, 160, h + 40), (bxc - 60, 60, h + 40),
                      (bxc - 60, 60, bh - 40), (bxc, 0, bh * 0.5)])
    flow = _flow_dots(inst, "flow", paths, d=34.0, seen=4)
    inst.joints["load"] = Joint("path", path=((0, -420, 160), (0, -260, 60), (0, 0, 0)))
    fl = lambda a, b: {k: (a, b) for k in flow}  # noqa: E731
    inst.actions = [
        ("A beaker of solvent goes in through the 235 mm front opening.", 2.4, {"load": (0.0, 1.0)}),
        ("The blower draws air in at the face, about 100 fpm with HEPA and 60 with carbon, through the filters at "
         "the back...", 3.2, {**fl(0.0, 1.0)}),
        ("...and over to the blower, which returns it to the room: here, into the VLM. Nothing is ducted out.", 3.2,
         {**fl(0.0, 1.0)}),
        ("660 x 610 x 635 mm and 41 kg: it fits a tray, 715 mm with the hose. Carbon takes solvent vapours; acids "
         "with HF go to the ducted hood.", 2.6, {}),
    ]
    inst.labels = [("235 mm front opening", (lx, yf, oz1), (0.20, 0.78)),
                   ("HEPA and carbon filters", (x0 + 60, yb - 60, h - 100), (0.12, 0.20)),
                   ("blower", (bxc, -bd / 2, bh - 60), (0.86, 0.66)),
                   ("hose", (bxc - 60, 160, h + 40), (0.70, 0.12))]
    inst.cam = (0.5, -1.6, 0.9)
    inst.props = ("load",)
    return inst


# ===================================================================================================== f. storage
# A tray of stored samples (our design), 1760 x 760 mm, so a tray's right 660 mm stays free for its UPS and dock. The
# cups and plugs are #222's (charge.py), in racks coloured by metal (blue anodized for 5N Al, orange for C10100 Cu), the
# cups in the front rows where a level gripper takes them; 20 mL vials (props.py); 15 mL ICP-MS tubes; a two-drawer
# cabinet with SEM pin stubs in the top drawer and polished 1.25 in mounts in the lower one; E8 sub-size bars
# (alloy_models); 250 mL powder jars; labelled bins. Sizes of the tubes, stubs, jars and bins are common ones:
# estimates. storage_seats() lists every pocket (base centres, in this frame).
SG = dict(drawer=250.0)                               # the drawers' travel, mm


def _grid(x0, y0, nx, ny, dx, dy):
    return [(x0 + dx * i, y0 + dy * j) for j in range(ny) for i in range(nx)]


def storage_seats() -> dict:
    """{kind: [(x, y, z)]}: where each item stands (its base centre) in the storage load's frame, drawers closed (the
    drawers open 250 mm towards -y). Cups by metal, plugs by metal, vials, ICP-MS tubes, SEM stubs, mounted coupons,
    bars (the bar's centre, flat, long axis along y), jars and bins (the floor's centre)."""
    return {
        "cup_al": [(x, y, 18.0) for x, y in _grid(-852.0, -372.0, 8, 6, 40.0, 36.0)],
        "cup_cu": [(x, y, 18.0) for x, y in _grid(-508.0, -372.0, 8, 6, 40.0, 36.0)],
        "plug_al": [(x, y, 15.0) for x, y in _grid(-167.0, -376.0, 12, 4, 26.0, 24.0)],
        "plug_cu": [(x, y, 15.0) for x, y in _grid(-167.0, -260.0, 12, 4, 26.0, 24.0)],
        "vial": [(x, y, 8.0) for x, y in _grid(180.0, -367.0, 9, 6, 34.0, 34.0)],
        "icp_tube": [(x, y, 10.0) for x, y in _grid(515.0, -373.0, 14, 8, 26.0, 26.0)],
        "sem_stub": [(x, y, 216.0) for x, y in _grid(-818.0, -75.0, 12, 8, 25.0, 30.0)],
        "coupon": [(x, y, 112.0) for x, y in _grid(-818.0, -60.0, 8, 4, 42.0, 60.0)],
        "bar": [(x, -70.0, 16.0) for x, _ in _grid(-451.0, 0.0, 20, 1, 18.0, 0.0)],
        "jar": [(x, y, 5.0) for x, y in _grid(-415.0, 80.0, 4, 2, 90.0, 110.0)],
        "bin": [(-80.0 + 190.0 * k + 90.0, 210.0, 3.0) for k in range(4)],
    }


def _merged(mesh: pv.PolyData, pts) -> pv.PolyData:
    out = [mesh.translate(tuple(p), inplace=False) for p in pts]
    return out[0].merge(out[1:]) if len(out) > 1 else out[0]


def _rack(x0, y0, x1, y1, h, holes, d, depth):
    """A block with round pockets: holes [(x, y)], diameter d, depth from its top."""
    blk = box(x0, y0, 0, x1, y1, h)
    cut = cq.Workplane("XY").pushPoints(list(holes)).circle(d / 2).extrude(depth + 1).translate((0, 0, h - depth))
    return blk.cut(cut)


def storage() -> Instrument:
    import charge
    import props
    import alloy_models
    W, D, H = FOOTPRINTS["storage"][:3]
    inst = Instrument("storage", "Sample storage on a tray", "Storage load (our design)", (W, D, H),
                      "Our design: #222's charge cups and plugs (charge.py), 20 mL vials (props.py), E8 sub-size bars "
                      "(alloy_models); ICP-MS tubes, SEM stubs, mounts, jars and bins at common sizes (estimates)")
    seats = storage_seats()
    body = _piece(inst, "body")
    xy = lambda k: [(x, y) for x, y, _ in seats[k]]  # noqa: E731
    body.add("Al cup rack", _rack(-880, -398, -544, -166, 40, xy("cup_al"), 19.65, 22), "r7_al_rack")
    body.add("Cu cup rack", _rack(-536, -398, -200, -166, 40, xy("cup_cu"), 19.65, 22), "r7_cu_rack")
    body.add("Al plug rack", _rack(-192, -398, 144, -288, 20, xy("plug_al"), 13.3, 5), "r7_al_rack")
    body.add("Cu plug rack", _rack(-192, -282, 144, -172, 20, xy("plug_cu"), 13.3, 5), "r7_cu_rack")
    body.add("vial rack", _rack(152, -398, 480, -166, 32, xy("vial"), 29.5, 24), "r7_lab_white")
    body.add("tube rack", _rack(488, -398, 880, -166, 60, xy("icp_tube"), 17.8, 50), "r7_lab_white")
    for nm, x0, x1 in (("Al", -880, -544), ("Cu", -536, -200)):
        body.add(f"{nm} label", box(x0 + 120, -399, 10, x1 - 120, -398, 30), "r7_label")
    # the cabinet's carcass, its two drawers open towards the front
    cab = box(-880, -150, 0, -480, 360, 300)
    cab = cab.cut(box(-870, -151, 200, -490, 350, 292)).cut(box(-870, -151, 102, -490, 350, 194))
    body.add("drawer cabinet", cab, "inst_light")
    body.add("bar tray", box(-470, -140, 0, -90, 0, 20).cut(
        cq.Workplane("XY").pushPoints([(x, -70.0) for x, _, _ in seats["bar"]]).rect(11, 101).extrude(5)
        .translate((0, 0, 16))), "r7_lab_white")
    body.add("jar plate", box(-470, 20, 0, -90, 240, 5), "r7_lab_white")
    for k, (x, y, z) in enumerate(seats["bin"]):
        bx0 = x - 90
        b = box(bx0, 60, 0, bx0 + 180, 360, 120).cut(box(bx0 + 3, 63, 3, bx0 + 177, 357, 121))
        body.add(f"bin {k}", b, "r7_bin")
        body.add(f"bin {k} label", box(bx0 + 40, 59, 70, bx0 + 140, 60, 100), "r7_label")
    # cups and plugs: Al silver, Cu copper
    cupm, plugm = charge.cup(), charge.plug()
    inst.meshes["body"] = [
        (_merged(cupm, seats["cup_al"]), AL_C, 1.0), (_merged(cupm, seats["cup_cu"]), CU_C, 1.0),
        (_merged(plugm, seats["plug_al"]), AL_C, 1.0), (_merged(plugm, seats["plug_cu"]), CU_C, 1.0),
        (_merged(props.vial_glass(), seats["vial"]), props.GLASS, 0.55),
        (_merged(pv.Cylinder(center=(0, 0, 62), direction=(0, 0, 1), radius=14.8, height=12).triangulate(),
                 seats["vial"]), (0.95, 0.95, 0.93), 1.0),
    ]
    tubem = pv.Cylinder(center=(0, 0, 62), direction=(0, 0, 1), radius=8.5, height=104).triangulate().merge(
        pv.Cone(center=(0, 0, 5), direction=(0, 0, -1), height=10, radius=8.5).triangulate())
    capm = pv.Cylinder(center=(0, 0, 120), direction=(0, 0, 1), radius=9.0, height=12).triangulate()
    inst.meshes["body"] += [(_merged(tubem, seats["icp_tube"]), (0.90, 0.91, 0.88), 0.7),
                            (_merged(capm, seats["icp_tube"]), (0.20, 0.42, 0.80), 1.0)]
    barm = alloy_models.bar_mesh()
    inst.meshes["body"].append((_merged(barm, [(x, y, z) for x, y, z in seats["bar"]]), (0.60, 0.61, 0.62), 1.0))
    jarm = pv.Cylinder(center=(0, 0, 50), direction=(0, 0, 1), radius=35, height=100).triangulate()
    lidm = pv.Cylinder(center=(0, 0, 106), direction=(0, 0, 1), radius=36, height=12).triangulate()
    inst.meshes["body"] += [(_merged(jarm, seats["jar"]), (0.93, 0.93, 0.90), 1.0)]
    for k, (x, y, z) in enumerate(seats["jar"]):
        col = [(0.25, 0.45, 0.85), (0.85, 0.45, 0.20), (0.36, 0.37, 0.42), (0.20, 0.62, 0.30)][k % 4]
        inst.meshes["body"].append((lidm.translate((x, y, z), inplace=False), col, 1.0))
    # the drawers and what is in them
    for nm, z0, kind in (("drawer1", 202.0, "sem_stub"), ("drawer2", 104.0, "coupon")):
        dp = _piece(inst, nm)
        tray = box(-868, -151, z0, -492, 348, z0 + 86).cut(box(-864, -147, z0 + 4, -496, 344, z0 + 87))
        dp.add(nm + " tray", tray, "inst_light")
        dp.add(nm + " front", box(-874, -157, z0 - 2, -486, -151, z0 + 88), "inst_light")
        dp.add(nm + " handle", box(-720, -173, z0 + 36, -640, -157, z0 + 50), "steel")
        dp.add(nm + " label", box(-840, -158, z0 + 30, -760, -157, z0 + 56), "r7_label")
        if kind == "sem_stub":
            dp.add("stub box", _rack(-845, -100, -515, 150, 10, xy("sem_stub"), 3.4, 8).translate((0, 0, z0 + 4)),
                   "r7_lab_white")
            stub = pv.Cylinder(center=(0, 0, 1), direction=(0, 0, 1), radius=6.35, height=2).triangulate().merge(
                pv.Cylinder(center=(0, 0, -4), direction=(0, 0, 1), radius=1.6, height=8).triangulate())
            tab = pv.Cylinder(center=(0, 0, 2.1), direction=(0, 0, 1), radius=4.5, height=0.2).triangulate()
            inst.meshes[nm] = [(_merged(stub, seats[kind]), (0.80, 0.81, 0.83), 1.0),
                               (_merged(tab, seats[kind]), (0.08, 0.08, 0.09), 1.0)]
        else:
            dp.add("coupon tray", _rack(-845, -90, -500, 150, 12, xy("coupon"), 33.0, 8)
                   .translate((0, 0, z0 + 4)), "inst_dark")
            mnt = pv.Cylinder(center=(0, 0, 10), direction=(0, 0, 1), radius=15.875, height=20).triangulate()
            face = pv.Cylinder(center=(0, 0, 20.1), direction=(0, 0, 1), radius=11.0, height=0.2).triangulate()
            inst.meshes[nm] = [(_merged(mnt, seats[kind]), (0.46, 0.09, 0.11), 1.0),
                               (_merged(face, seats[kind]), (0.82, 0.83, 0.85), 1.0)]
        inst.joints[nm] = Joint("slide", vec=(0, -SG["drawer"], 0))
    inst.actions = [
        ("A storage tray: what the arm picks from. 1760 x 760 mm and 300 mm tall; the tray's right end stays free "
         "for its UPS and dock.", 2.6, {}),
        ("Charge cups turned from 5N Al (blue rack) and C10100 Cu (orange rack), 48 of each, in the front rows "
         "where a level gripper takes them.", 3.0, {}),
        ("Their plugs, Al and Cu apart; 54 capped 20 mL vials; 112 15 mL ICP-MS tubes.", 3.0, {}),
        ("The top drawer: 96 SEM pin stubs, 12.7 mm, carbon tabs on.", 2.8, {"drawer1": (0.0, 1.0)}),
        ("The lower drawer: 32 polished 1.25 in mounts.", 2.8, {"drawer1": (1.0, 0.0), "drawer2": (0.0, 1.0)}),
        ("Tensile bars (E8 sub-size), sealed 250 mL powder jars with lids by powder, labelled bins.", 3.0,
         {"drawer2": (1.0, 0.0)}),
        ("Every pocket is a seat: storage_seats() lists them for the arm's planner.", 2.2, {}),
    ]
    inst.zoom = {1: ((-540.0, -280.0, 60.0), 850.0), 2: ((300.0, -280.0, 60.0), 1150.0),
                 3: ((-680.0, -330.0, 230.0), 950.0), 4: ((-680.0, -330.0, 130.0), 950.0),
                 5: ((-150.0, 60.0, 80.0), 1100.0), 6: "out"}
    inst.labels = [("5N Al cups", (-712, -280, 82), (0.10, 0.80)), ("C10100 Cu cups", (-368, -280, 82), (0.30, 0.86)),
                   ("20 mL vials", (316, -280, 75), (0.56, 0.86)), ("ICP-MS tubes", (684, -280, 132), (0.84, 0.80)),
                   ("drawers: stubs, mounts", (-680, -157, 280), (0.10, 0.18)),
                   ("powder jars", (-280, 130, 118), (0.40, 0.12)), ("labelled bins", (200, 60, 120), (0.70, 0.16))]
    inst.cam = (0.55, -1.5, 1.35)
    return inst


REGISTRY = {"glovebox_tray": glovebox_tray, "tensile_h": tensile_h, "hardness": hardness, "cnc": cnc,
            "fumehood": fumehood, "fumehood_tray": fumehood_tray, "storage": storage}
