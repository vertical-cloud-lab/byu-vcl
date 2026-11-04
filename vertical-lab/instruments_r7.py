"""Round 7 stations (#303, PR #318): a glovebox on a tray, a tensile tester lying on its side, an automatic
micro-Vickers tester, an autonomous CNC mill, two fume hoods, and a tray of stored samples.

Each is an ``instruments.Instrument`` (pieces, joints, an actions script), as in ``instruments.py``; ``tour.py`` loads
``REGISTRY`` and plays each one. Frame as in ``instruments.py``: x to the right, y away from you facing the front, z up,
origin at the centre of the footprint, millimetres. On a tray, the front (-y) faces the opening, where the arm works.

``FOOTPRINTS`` is for the tray layout: key -> (W, D, H mm, mass kg, product, source URL, "tray" or "floor"). W x D is
the footprint as drawn here, H the height closed (what opens upward is in the notes). The tray limits used: 2426 x 840
mm inside the rim, 856.5 mm product height (the 996 mm opening), light 228 / medium 360 / strong 490 kg. Each tray also
carries its UPS and dock plate at the back right (``services.UPS_AT``, ``services.PLATE_*``).

Sources are in ``SOURCES`` and in notes/instruments_r7.md. "Estimate" means read off photos or our own design.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np

import instruments as I
from instruments import Instrument, Joint, _piece, _wedge, _xcyl, _ycyl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
from common import box, cyl, hose, rbox, tube  # noqa: E402

# ===================================================================================================== footprints
# key -> (W, D, H mm, mass kg, product, source URL, "tray" | "floor")
FOOTPRINTS = {
    "glovebox_tray": (1400.0, 810.0, 760.0, 140.0,
                      "Custom N2 glovebox, purge-only, with a 150 mm mini antechamber loaded from the front (our "
                      "design; sizes after the Vigor SG1200/750 and the Plas-Labs 830-ABC). Mass is an estimate",
                      "https://www.pharmaceutical-tech.com/products/vigor-tech-usa/standard-gloveboxes", "tray"),
    "tensile_h": (1289.0, 622.0, 451.0, 83.0,
                  "ZwickRoell zwickiLine Z5.0 TN (5 kN) lying on its side, on a 40 mm base plate (ours); "
                  "1289 x 408 x 480 mm upright, 622 deep with its electronics, 78 kg",
                  "https://www.zwickroell.com/fileadmin/content/Files/SharePoint/user_upload/PI_EN/"
                  "02_396_zwickiLine_Z0_5_up_to_Z5_0_Materials_Testing_Machine_PI_EN.pdf", "tray"),
    "hardness": (520.0, 671.0, 595.0, 48.0,
                 "Mitutoyo HM-220 Type D (AVPAK): micro-Vickers, motorized XY stage, autofocus, motorized turret; "
                 "main unit 315 x 671 x 595 mm, 43 kg, plus its PC beside it (estimate, 5 kg)",
                 "https://www.mitutoyo.com/webfoo/wp-content/uploads/K_section.pdf", "tray"),
    "cnc": (580.0, 520.0, 540.0, 50.0,
            "Makera Carvera desktop CNC, 6-tool changer; 840 mm tall with the lid open. The lid actuator and the "
            "pneumatic vise are our additions",
            "https://www.makera.com/products/carvera", "tray"),
    "fumehood": (1219.0, 958.0, 2400.0, 260.0,
                 "Labconco Protector XStream 4 ft ducted hood on a base cabinet (cabinet height and mass estimated)",
                 "https://www.labconco.com/p/protector-xstream-laboratory-hoods", "floor"),
    "fumehood_tray": (940.0, 610.0, 635.0, 32.0,
                      "Sentry Air Systems SS-224-DCH ductless fume hood, 660 x 610 x 635 mm, with its separate "
                      "267 x 203 x 216 mm blower beside it",
                      "https://sentryair.com/dfhapp.htm", "tray"),
    "storage": (1780.0, 820.0, 330.0, 95.0,
                "Sample storage load (our design): Al and Cu charge cups and plugs, 20 mL vials, ICP-MS tubes, SEM "
                "stubs, mounted coupons, tensile bars, powder jars, labelled bins, a two-drawer cabinet. Leaves the "
                "tray's right 630 mm free for the UPS and dock. Mass is an estimate", "", "tray"),
}
