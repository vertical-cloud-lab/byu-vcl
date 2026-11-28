"""A taller opening on the Kardex Shuttle: what Kardex publishes, and what about 1000 mm of product height would put on
a tray (byu-vcl #303, PR #318).

    python3 kardex_tall.py json                       # the checks -> out/tall_opening.json and out/tall_opening_bays.png
    python3 kardex_tall.py bays                       # just the figure, out/tall_opening_bays.png (matplotlib, no 3D)
    PREVIEW=1 xvfb-run -a python3 kardex_tall.py      # the last frame of each sub-step -> /tmp/preview_vlm_tall_opening.png
    xvfb-run -a python3 kardex_tall.py                # -> out/vlm_tall_opening_still.png, .gif, out/mp4/vlm_tall_opening.mp4

**What Kardex publishes** is 727.5 mm of product height through the opening, with 20 mm clear above it: the "Kardex
Shuttle POF" order sheets for the XP 500 at 2450 x 864 mm (727.5 mm) and 3050 x 864 mm (727 mm), both "depends on tray
type selection" (``vlm.MAX_GOODS_H``). Kardex's blog gives "just over 28 inches". No brochure, factsheet or product page
found gives a taller opening for any Shuttle (notes/kardex_opening.md lists what was read).

**Why a taller one is plausible, all of it indirect:**
- Kardex's factsheet: "other sizes possible on request".
- The Shuttle 1000 stores "EURO pallets and mesh boxes on special trays" (kardex.com, heavy-duty units), with "special
  trays for pallet storage" and "tray extraction for forklift operation" (Shuttle XP brochure). A Euro mesh box
  (UIC 435-3, the old DIN 15155) is 1240 x 835 x 970 mm outside, so those trays must pass about 1 m.
- One used Shuttle XP 500 (2005/2006, 3050 x 864 mm) is listed with "Bedienoeffnung frontseitig auf 833 mm, Hoehe
  996 mm" (lagersysteme-paternoster.de, Pos. 89). If its header stands as far above the goods as on the order sheet's
  unit (vlm.py puts the header 867 mm over the 833 mm table for 727.5 mm of goods), that opening takes about 856 mm:
  an estimate.

So three heights are checked: 727.5 mm (today), about 856 mm (the 996 mm opening, estimated) and 1000 mm (Sterling's
figure, about a mesh box). Each machine is also checked against the load per tray, which Kardex rates per tray and per
area (a distributed load), and against the tray's depth.

**Kardex against Modula (round 8, Sterling's review of 2026-11-04):** each machine is also checked at five product
heights, ``BAYS``: Modula Lift's Bay S (695 mm, the bay the Apr 2 Modula quote is priced with, the lowest of the five),
Kardex's published 727.5 mm, our 856.5 mm estimate, and Modula's Bay M (895 mm) and Bay XL (1,295 mm), all from
Modula's catalogue for a single-delivery bay. Its mass goes against the quoted Kardex trays (``vlm.TRAYS``: light 228,
medium 360, strong 490 kg) and Modula's MC trays (MC50D 500, MC75D 750, MC1000D 990 kg on 2,500 x 857 mm, the MC1000D's
2,460 x 857), and its footprint against both trays. ``plot_bays()`` draws it: out/tall_opening_bays.png.

The scene: three trays of the same 2450 x 864 mm size with today's envelope (blue, 727.5 mm) and a 1000 mm one (green)
over each, the machines a taller opening would let on, and behind them, on red 1000 mm boxes, the ones still too tall.
The InssTek MX-Lab is ``instruments_lab.ded()`` without its base cabinet, the MetalONE, M450 and MPRINT are
``fab_metal.py``'s, the Form 4 ``fab_resin.py``'s and the Instron 68SC-2 ``instruments.py``'s. The Mastrex MX100, the
Lasefinity Fusion X, the Parker Balston N2 generator and the MX-Lab's base cabinet are drawn as boxes at their
published (or, for the cabinet, estimated) size: none of them is modelled.
"""
from __future__ import annotations

import hashlib
import json
import pickle
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
import pyvista as pv

import lab
import tour
import vlm as V
from scene import OUT, PREVIEW, R, Scene, T

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"
NAME = "vlm_tall_opening"
TITLE = "Vertical cloud lab: what a taller Kardex opening would put on a tray"

# ----------------------------------------------------------------------------------------------- the heights checked
H_STD = V.POF_GOODS_H         # 727.5 mm, Kardex's published figure: its order sheet (POF) for the XP 500 at 2450 x 864
CLEAR = V.GOODS_CLEAR         # 20 mm clear above the goods, required (POF)
HEADER_STD = V.POF_OPEN_H     # 867 mm: the standard unit's header over the table for 727.5 mm of goods (renders)
H_996 = round(H_STD + 996.0 - HEADER_STD, 1)  # a 996 mm opening over the same 833 mm access table: about 856 mm
assert abs(H_996 - V.MAX_GOODS_H) < 0.05      # vlm.py now draws that opening (round 7), and takes this figure
H_MESH = 970.0                # a Euro mesh box's outside height (UIC 435-3 / DIN 15155)
H_TALL = 1000.0               # the height checked: Sterling's figure, about a mesh box
HEIGHTS = {"today_727_5": H_STD, "opening_996_est": H_996, "mesh_box_970": H_MESH, "tall_1000": H_TALL}
IN_W, IN_D = V.TRAY_W - 24.0, V.TRAY_D - 24.0      # inside the tray's rim, 2426 x 840 mm

S = {   # sources: key -> (what, url)
    "pof1": ("Kardex Shuttle POF (order sheet), SHUTTLE-01-500-2450x864x6750: 'Maximum Product Height: 727.5 mm / "
             "28.64 in. Depends on Tray Type selection', 'Clearance Required Above Product: 20 mm', access table "
             "833 mm; tray ratings Light 230, Medium 360, Strong 500, 66-1-Medium-100 525 kg (StoreMoreStore option 1)",
             "https://products.storemorestore.com/hubfs/StoreMoreStore/Kardex-Vertical-Lift-Module/"
             "VLM-Option-1-96x34-Light-Specification-Sheet.pdf"),
    "pof6": ("Kardex Shuttle POF, SHUTTLE-01-500-3050x864x6750: 'Maximum Product Height: 727 mm / 28.62 in'; tray "
             "ratings Light 120, Medium 205, Strong 265 kg (20.6 lb/sq ft), 66-1-Medium-100 470, 75-3-Medium-100 505 kg "
             "(StoreMoreStore option 6)",
             "https://products.storemorestore.com/hubfs/StoreMoreStore/Kardex-Vertical-Lift-Module/"
             "VLM-Option-6-120x34Medium-Specification-Sheet.pdf"),
    "q53": ("byu-vcl #53, the quote's spec: XP 500, 96.46 x 34 in trays, light 502 lb (22.3 lb/sq ft), medium 794 lb, "
            "strong 1,080 lb (47.4 lb/sq ft)", "https://github.com/vertical-cloud-lab/byu-vcl/issues/53"),
    "xp": ("Kardex Remstar Shuttle XP brochure: XP 250/500 trays 1,250-4,050 x 610-1,270 mm, up to 560 kg, 25 mm pitch; "
           "XP 700 up to 725 kg, 50 mm pitch; XP 1000 trays 610-1,778 mm deep, 1,000 kg at 1,250 mm wide, 900 kg at "
           "2,450 mm, 800 kg at 4,050 mm; options 'Special trays for pallet storage', 'Tray extraction for forklift "
           "operation'. No product or opening height",
           "https://www.supplycore.com/wp-content/uploads/2022/01/Shuttle-XP-Vertical-Lift-Module-1108-1.pdf"),
    "xp_de": ("Kardex Remstar Shuttle XP brochure, German, 2017: the same tables; 'Sonder-Tablare fuer "
              "Palettenlagerung'. No product or opening height",
              "https://wtp.hoechsmann.com/lexikon/pdf/kad_shuttlexp_2017_de.pdf"),
    "fact": ("Kardex Shuttle factsheet (8103-US-2112): 250/500 up to 555 kg, 700 up to 725 kg, 1000 up to 1,000 kg; "
             "'When storing heavy loads or even pallets, the Kardex Shuttle 1000 is the perfect choice'; 'Standard "
             "technical data, other sizes possible on request'",
             "https://info.southwestsolutions.com/hubfs/Brochures/SSG-Brochures/KAR-198/Shuttle.pdf"),
    "heavy": ("kardex.com, heavy-duty units: 'Use a forklift to stack and store EURO pallets and mesh boxes on special "
              "trays'; Shuttle 1000 'up to 825 kg per tray'", "https://www.kardex.com/en/products/heavy-duty-units"),
    "blog": ("Kardex blog, VLMs vs vertical carousels: VLM trays 'with a max product height of just over 28 inches'",
             "https://www.kardex.com/en-us/blog/vertical-lift-modules-vs-vertical-carousels"),
    "towermat": ("Kardex TowerMat (heavy, oversized goods, pallets): EE carriers up to 8.2 x 1.5 m, 3,000 kg; FE up "
                 "to 12.2 x 2.1 m, 5,000 kg; no goods height published (Kardex product guide 5009-EN-0825)",
                 "https://www.kardex.com/en-us/products/vertical-lift-module/towermat"),
    "used996": ("A used Kardex Shuttle XP 500, 3050 x 864 mm, built 2005/2006: 'Bedienoeffnung Frontseitig auf 833 mm, "
                "Hoehe 996 mm'", "https://www.lagersysteme-paternoster.de/gebrauchte-lagertechnik/"
                                 "kardex-shuttle-xp500-3050x864-pos-89/"),
    "meshbox": ("Euro mesh box pallet (UIC 435-3, DIN 15155): outside 1240 x 835 x 970 mm, inside 1200 x 800 x 800 mm",
                "https://www.hellopro.fr//documentation/pdf_prod/3/0/9/88526_697b113fadeb2d9921786be336dce08a.pdf"),
    "acdev": ("ac-dev-lab #372 (the AC's XP-500 quote: 49.21 x 24 in trays, 992 lb per tray, floor to tray 32.8 in, "
              "'standard on all shuttles. They can change this height if necessary'); #471, #216, #370: no opening "
              "height", "https://github.com/AccelerationConsortium/ac-dev-lab/issues/372"),
    "mxlab": ("InssTek MX-Lab Technical Data Rev.3 (2020): 680 x 684 x 835 mm without accessories, 250 kg, 1-phase "
              "220 V 15(20) A; 2024 brochure: up to 500 W Yb fibre laser, six hoppers, Ar > 99.999 % with O2 <= 50 ppm "
              "as an option (via notes/instruments_lab.md)", "notes/instruments_lab.md"),
    "mx100": ("Tech-Labs, Mastrex MX-100: 22.05 x 22.05 x 31.50 in (560 x 560 x 800 mm), 276 lb (125 kg), 120 V, "
              "300 W laser; NG150 nitrogen generator as an accessory",
              "https://tech-labs.com/products/mastrex-mx-100-metal-3d-printer"),
    "fusionx": ("TCT Magazine, Lasefinity Fusion X launch: 600 x 650 x 860 mm, 500 W fibre laser, sealed N2 or Ar "
                "chamber, 'permanent filtration system'; no mass published",
                "https://tctmagazine.com/lasefinity-fusionx-compact-desktop-metal-3d-printer-launches-at-tct-3sixty"),
    "metalone": ("Sharebot MetalONE launch figures: 740 x 630 x 1000 mm, 150 kg (later listings 1000 x 600 x 1470 mm, "
                 "270-315 kg) (fab_metal.py)", "out/fabrication.json"),
    "dimetal": ("All3DP, 2026-07-31, Kings 3D DiMetal-100: 690 x 720 x 1000 mm, about 140 kg, 220 V 50 Hz, 300 W",
                "https://all3dp.com/4/kings-3ds-140-kg-dimetal-100-proves-desktop-sized-isnt-always-desktop-friendly/"),
    "fab": ("fab_metal.py and fab_resin.py, from the makers' figures (out/fabrication.json)", "out/fabrication.json"),
    "inst": ("instruments.py, instruments_lab.py, from the makers' figures (out/instruments.json)",
             "out/instruments.json"),
    "n2": ("Parker Balston UHPN2-1100 (notes/services.md): 305 x 406 x 889 mm, 50 kg, 120 V, 500-1100 cc/min at "
           "99.9999 %, needs compressed air at 60-125 psig", "notes/services.md"),
    "equip": ("lab_models/equipment.py (#199): Aconity MIDI 2450 x 1500 x 2320 mm, 1450 kg; rePowder 1000 x 800 x "
              "1600 mm, about 300 kg", "lab_models/equipment.py"),
    "modula_cat": ("Modula Lift catalogue (US, Sept 2025), PDF p. 5: 'Modula Lift is offered in 3 sizes of bays (S/M/XL) "
                   "... Maximum product height for single delivery level 27.36 / 35.24 / 50.98 in (695 / 895 / 1,295 "
                   "mm)'; dual delivery 320-320 / 320-520 / 320-920 mm. PDF p. 8, models: MC50D tray 2,500 x 857 mm, "
                   "walls 70-120 mm, 1,102 lb / 500 kg; MC75D 2,500 x 857 mm, 1,653 lb / 750 kg; MC1000D 2,460 x 857 mm, "
                   "walls 120 mm, 2,200 lb / 990 kg ('Maximum Tray Load Capacity'). No clearance above the goods is "
                   "stated, and the tray size isn't said to be inside or outside the walls",
                   "https://modula.us/wp-content/uploads/2025/11/USA_MODULA_CAT-LIFT_SEPT2025_WEB.pdf"),
    "modula_quote": ("The Apr 2 Modula quote, as Sterling's review gives it (PR #318, 2026-11-04 18:41): priced with "
                     "Lift Bay S. The quote itself is not in this repo", "https://github.com/vertical-cloud-lab/byu-vcl/pull/318"),
    "instron": ("Instron 6800 Series brochure, PDF p. 24, '6800 Single Column Series': footprint dimensions (h x w x d) "
                "68SC-05 1020 x 460 x 615 mm, 55 kg; 68SC-1, 68SC-2 and 68SC-5 1410 x 460 x 615 mm, 62 kg; the 68SC-5's "
                "extra height (E2) adds 27 cm",
                "https://4spe.org/files/events/Webinars/Instron-6800-Series-Universal-Testing-Systems-Brochure.pdf"),
}

# ------------------------------------------------------------------------- what each tray is rated for, per tray
# (model, width x depth mm, kg per tray, sources). Per area is kg over the tray's own area: Kardex rates a tray for a
# distributed load (the POF gives lb/sq ft), so a machine on a small footprint is checked against that as well.
TRAY_RATINGS = [
    dict(model="Shuttle XP 500", tray="2450 x 864, Strong", w=2450, d=864, kg=500, src=["pof1", "q53"],
         note="the quote in #53 gives 1,080 lb (490 kg) for the strong tray"),
    dict(model="Shuttle XP 500", tray="2450 x 864, 66-1-Medium-100", w=2450, d=864, kg=525, src=["pof1"],
         note="the strongest tray type on the POF at this width"),
    dict(model="Shuttle XP 500", tray="3050 x 864, Strong", w=3050, d=864, kg=265, src=["pof6"],
         note="wider is weaker: 265 kg against 500 at 2450 mm"),
    dict(model="Shuttle XP 500", tray="3050 x 864, 75-3-Medium-100", w=3050, d=864, kg=505, src=["pof6"], note=""),
    dict(model="Shuttle XP 700", tray="2450 x 864 ('up to 725 kg')", w=2450, d=864, kg=725, src=["xp", "fact"],
         note="trays up to 4050 x 1270 mm; the rating at a given width isn't published, so 725 kg is an upper bound"),
    dict(model="Shuttle XP 1000", tray="2450 x 864", w=2450, d=864, kg=900, src=["xp", "heavy"],
         note="900 kg at 2450 mm (brochure); Kardex's page now says up to 825 kg; special trays take pallets and mesh "
              "boxes, i.e. concentrated loads"),
]
STRONG = TRAY_RATINGS[0]
PER_AREA_STRONG = STRONG["kg"] / (STRONG["w"] * STRONG["d"] / 1e6)        # kg/m2, about 236 (48.4 lb/sq ft)

# ------------------------------------------------------------ five product heights, Kardex against Modula (round 8)
# Sterling's review (PR #318, 2026-11-04 18:41). Modula's are the catalogue's "maximum product height for single delivery
# level"; Kardex's 727.5 mm is the order sheet's, with 20 mm clear above it; 856.5 mm is ours (H_996, = vlm.MAX_GOODS_H).
# A machine fits a height if its tallest point in use (the Form 4's open lid) is at or under it.
BAYS = {
    "modula_s_695": dict(mm=695.0, system="Modula", label="Modula S 695", bay="Modula Lift Bay S",
                         what="Modula Lift Bay S, single delivery: maximum product height", estimate=False,
                         src=["modula_cat", "modula_quote"],
                         note="the bay the Apr 2 Modula quote is priced with, and the lowest of the five: 32.5 mm under "
                              "Kardex's published 727.5 mm"),
    "kardex_727_5": dict(mm=H_STD, system="Kardex", label="Kardex 727.5", bay="Kardex Shuttle XP 500, standard opening",
                         what="Kardex's published maximum product height (the POF order sheet, 2450 x 864 tray)",
                         estimate=False, src=["pof1"], note="20 mm clear required above it; 727 mm at 3050 x 864"),
    "kardex_856_5_est": dict(mm=H_996, system="Kardex", label="Kardex ~856.5 (est.)",
                             bay="Kardex, a 996 mm opening (one used XP 500)",
                             what="our estimate (vlm.MAX_GOODS_H): 727.5 + (996 - 867) mm", estimate=True,
                             src=["used996"], note="not published: the 867 mm header over the table is read off "
                                                   "Kardex's renders, and Kardex has not confirmed the 996 mm opening"),
    "modula_m_895": dict(mm=895.0, system="Modula", label="Modula M 895", bay="Modula Lift Bay M",
                         what="Modula Lift Bay M, single delivery: maximum product height", estimate=False,
                         src=["modula_cat"], note=""),
    "modula_xl_1295": dict(mm=1295.0, system="Modula", label="Modula XL 1295", bay="Modula Lift Bay XL",
                           what="Modula Lift Bay XL, single delivery: maximum product height", estimate=False,
                           src=["modula_cat"], note=""),
}
QUOTE_BAY = "modula_s_695"
assert abs(BAYS["kardex_856_5_est"]["mm"] - V.MAX_GOODS_H) < 0.05
# Kardex: the three trays of the #53 quote (vlm.TRAYS), lightest first. Modula: the MC models' 857 mm deep trays.
KARDEX_TRAYS = [dict(model="Kardex Shuttle XP 500 (#53 quote)", tray=f"2450 x 864, {t['kind']}",
                     key=f"{t['kind']}_{t['capacity_kg']}", w=V.TRAY_W, d=V.TRAY_D, kg=t["capacity_kg"], src=["q53"])
                for t in sorted(V.TRAYS.values(), key=lambda t: t["capacity_kg"])]
MODULA_TRAYS = [
    dict(model="Modula Lift MC50D", tray="2500 x 857, walls 70-120 mm", key="MC50D_500", w=2500.0, d=857.0, kg=500,
         src=["modula_cat"]),
    dict(model="Modula Lift MC75D", tray="2500 x 857, walls 70-120 mm", key="MC75D_750", w=2500.0, d=857.0, kg=750,
         src=["modula_cat"]),
    dict(model="Modula Lift MC1000D", tray="2460 x 857, walls 120 mm", key="MC1000D_990", w=2460.0, d=857.0, kg=990,
         src=["modula_cat"], note="2460 mm wide in the catalogue, not 2500"),
]
KARDEX_MAX, MODULA_MAX = KARDEX_TRAYS[-1], MODULA_TRAYS[-1]      # the strongest of each: 490 kg and 990 kg
# Footprints: Kardex inside its rim (IN_W x IN_D, 2426 x 840, as check() does); Modula as the catalogue gives it, at the
# narrowest MC tray (2460 x 857), since the catalogue doesn't say whether that is inside the walls.
MOD_W, MOD_D = min(t["w"] for t in MODULA_TRAYS), min(t["d"] for t in MODULA_TRAYS)
SHORT = {"mxlab": "InssTek MX-Lab", "mxlab_base": "MX-Lab base cabinet (est.)", "mx100": "Mastrex MX100",
         "fusionx": "Lasefinity Fusion X", "metalone": "Sharebot MetalONE", "dimetal": "Kings 3D DiMetal-100",
         "n2gen": "Parker Balston N2 generator", "form4": "Formlabs Form 4, lid open", "meltio_m450": "Meltio M450",
         "instron_small": "Instron 68SC-2", "mprint": "One Click Metal MPRINT", "hip": "Kobelco Dr.HIP",
         "repowder": "AMAZEMET rePowder", "glovebox": "Inert PureLab glovebox", "aconity_midi": "Aconity MIDI"}
BAY_FIG = ["mxlab", "mx100", "fusionx", "n2gen", "form4", "metalone", "dimetal", "meltio_m450", "mprint", "hip",
           "instron_small"]                     # the machines in Sterling's review: the figure's rows

# ----------------------------------------------------------------------------------------- the machines checked
# key, model, W x D x H closed (mm), H in use if taller (lid or cover open), kg (None: not published), needs, sources,
# how the scene draws it ("model": an Instrument; "box"; None: not drawn)
MACHINES = [
    dict(key="mxlab", model="InssTek MX-Lab (DED, powder-fed laser)", size=(680, 684, 835), kg=250, src=["mxlab"],
         needs="argon (> 99.999 %, O2 <= 50 ppm option), powder carrier gas, 220 V 1-phase 15(20) A; exhaust; its "
               "laser's cooling and what its base cabinet holds are not published", draw="model"),
    dict(key="mxlab_base", model="MX-Lab base cabinet (size estimated)", size=(900, 760, 1000), kg=None,
         src=["inst"], needs="unknown: not published", draw="box", h_est=True,
         note="instruments_lab.ded()'s estimate, scaled from a photo; if it holds the laser source, it rides with the "
              "MX-Lab, since a process fibre can't go through a dock"),
    dict(key="mx100", model="Mastrex MX100 (LPBF)", size=(560, 560, 800), kg=125, src=["mx100"],
         needs="120 V; nitrogen (an NG150 generator is the accessory)", draw="box"),
    dict(key="fusionx", model="Lasefinity Fusion X (LPBF)", size=(600, 650, 860), kg=None, src=["fusionx"],
         needs="N2 or Ar; on-board filtration", draw="box"),
    dict(key="metalone", model="Sharebot MetalONE (LPBF)", size=(740, 630, 1000), kg=150, src=["metalone"],
         needs="inert gas; later listings give 1470 mm and 270-315 kg, probably with a stand", draw="model",
         kg_note="published: 150 kg at launch; later listings 270-315 kg (probably with a stand), under Kardex's "
                 "strong 490 kg either way"),
    dict(key="dimetal", model="Kings 3D DiMetal-100 (LPBF)", size=(690, 720, 1000), kg=140, src=["dimetal"],
         needs="220 V 50 Hz; inert gas", draw=None),
    dict(key="n2gen", model="Parker Balston UHPN2-1100 (N2 generator)", size=(305, 406, 889), kg=50, src=["n2"],
         needs="compressed air 60-125 psig, 120 V", draw="box"),
    dict(key="form4", model="Formlabs Form 4, cover open", size=(398, 367, 554), h_open=844, kg=18.3, src=["fab"],
         needs="power; the resin and the IPA are open questions for Kardex and EHS (README)", draw="model"),
    dict(key="meltio_m450", model="Meltio M450 (wire-laser DED)", size=(560, 600, 1400), kg=250, src=["fab"],
         needs="argon, cooling, 2-5 kW peak", draw="model"),
    dict(key="instron_small", model="Instron 68SC-2", size=(460, 615, 1410), kg=62, src=["inst", "instron"],
         needs="power; the shortest single column, the 68SC-05, is 1020 mm", draw="model",
         note="1410 mm checked against Instron's brochure (h x w x d 1410 x 460 x 615 mm, 62 kg), not just the model"),
    dict(key="mprint", model="One Click Metal MPRINT (LPBF)", size=(1100, 790, 1900), kg=445, src=["fab"],
         needs="inert gas; 440-450 kg", draw="model"),
    dict(key="hip", model="Kobelco O2-Dr.HIP", size=(1315, 1100, 1300), kg=1100, src=["inst"],
         needs="argon, cooling water that must never stop, air", draw=None),
    dict(key="repowder", model="AMAZEMET rePowder", size=(1000, 800, 1600), kg=300, src=["equip"],
         needs="400 V 3-phase, chiller, argon", draw=None),
    dict(key="glovebox", model="Inert PureLab HE 2GB", size=(2005, 834, 1794), kg=None, src=["inst"], needs="",
         draw=None),
    dict(key="aconity_midi", model="Aconity MIDI", size=(2450, 1500, 2320), kg=1450, src=["equip"], needs="",
         draw=None),
]


def check(m: dict) -> dict:
    """One machine against each height, the tray's depth and every tray rating."""
    w, d, h = m["size"]
    h_use = max(h, m.get("h_open", 0))
    fits = {k: bool(h_use <= v) for k, v in HEIGHTS.items()}
    margin = {k: round(v - h_use, 1) for k, v in HEIGHTS.items()}
    footprint = (min(w, d) <= IN_D and max(w, d) <= IN_W)
    depth_needed = None if footprint else min(w, d)
    out = dict(model=m["model"], size_mm=list(m["size"]), height_in_use_mm=h_use, kg=m["kg"],
               fits_height=fits, margin_mm=margin, footprint_fits_864_tray=bool(footprint),
               needs_deeper_tray_mm=depth_needed, needs=m["needs"], sources=[S[k][0] for k in m["src"]],
               source_urls=[S[k][1] for k in m["src"]], drawn=m["draw"], note=m.get("note", ""))
    if m["kg"] is not None:
        area = w * d / 1e6
        per_area = m["kg"] / area
        out["kg_per_m2_on_its_footprint"] = round(per_area)
        out["times_strong_tray_per_area"] = round(per_area / PER_AREA_STRONG, 2)
        out["trays_that_carry_its_mass"] = [f"{t['model']} {t['tray']}: {t['kg']} kg" for t in TRAY_RATINGS
                                            if m["kg"] <= t["kg"]]
    out["verdict"] = verdict(m, fits, footprint)
    out.update(check_bays(m, footprint))
    return out


def weight_status(kg) -> str:
    """Its mass against the strongest tray of each system: 'both', 'modula_only', 'neither' or 'unknown'."""
    if kg is None:
        return "unknown"
    if kg <= KARDEX_MAX["kg"] and kg <= MODULA_MAX["kg"]:
        return "both"
    if kg <= MODULA_MAX["kg"]:
        return "modula_only"
    return "kardex_only" if kg <= KARDEX_MAX["kg"] else "neither"


WEIGHT_STATUS = {"both": f"within both strongest trays (Kardex strong {KARDEX_MAX['kg']} kg, Modula MC1000D "
                         f"{MODULA_MAX['kg']} kg)",
                 "modula_only": f"over Kardex strong {KARDEX_MAX['kg']} kg, within Modula MC1000D {MODULA_MAX['kg']} kg",
                 "kardex_only": "within Kardex strong, over Modula MC1000D",
                 "neither": f"over both: Kardex strong {KARDEX_MAX['kg']} kg and Modula MC1000D {MODULA_MAX['kg']} kg",
                 "unknown": "mass not published"}


def check_bays(m: dict, footprint_kardex: bool) -> dict:
    """One machine at the five product heights (BAYS), its mass against Kardex's quoted trays and Modula's MC trays,
    and its footprint on each system's tray. New keys only: check()'s are left as they were."""
    w, d, h = m["size"]
    h_use = max(h, m.get("h_open", 0))
    kg = m["kg"]
    fits = {k: bool(h_use <= b["mm"]) for k, b in BAYS.items()}
    foot_mod = bool(min(w, d) <= MOD_D and max(w, d) <= MOD_W)
    out = dict(fits_bay=fits, bay_margin_mm={k: round(b["mm"] - h_use, 1) for k, b in BAYS.items()},
               height_estimated=bool(m.get("h_est", False)),
               kg_status=m.get("kg_note") or ("unknown: not published" if kg is None else "published (see sources)"),
               footprint_fits_modula_857_tray=foot_mod,
               footprint_mm=f"{min(w, d):.0f} deep x {max(w, d):.0f} wide, against Kardex {IN_D:.0f} x {IN_W:.0f} "
                            f"inside the rim and Modula {MOD_D:.0f} x {MOD_W:.0f}",
               strongest_tray_status=weight_status(kg), strongest_tray_note=WEIGHT_STATUS[weight_status(kg)])
    if kg is None:
        out.update(kg_within_kardex_tray=None, kg_within_modula_tray=None, over_tray_ratings=None)
    else:
        out["kg_within_kardex_tray"] = {t["key"]: bool(kg <= t["kg"]) for t in KARDEX_TRAYS}
        out["kg_within_modula_tray"] = {t["key"]: bool(kg <= t["kg"]) for t in MODULA_TRAYS}
        out["over_tray_ratings"] = ([f"Kardex {t['tray']}: {t['kg']} kg" for t in KARDEX_TRAYS if kg > t["kg"]]
                                    + [f"{t['model']}: {t['kg']} kg" for t in MODULA_TRAYS if kg > t["kg"]])
        mod_area = MODULA_MAX["kg"] / (MODULA_MAX["w"] * MODULA_MAX["d"] / 1e6)          # about 470 kg/m2
        out["times_modula_mc1000d_per_area"] = round(kg / (w * d / 1e6) / mod_area, 2)
    out["bays_verdict"] = bays_verdict(m, fits, footprint_kardex, foot_mod)
    return out


def bays_verdict(m: dict, fits: dict, foot_kardex: bool, foot_mod: bool) -> str:
    h = max(m["size"][2], m.get("h_open", 0))
    kg = m["kg"]
    yes = [BAYS[k]["label"] for k, f in fits.items() if f]
    no = [BAYS[k]["label"] + (" (the quoted bay)" if k == QUOTE_BAY else "") for k, f in fits.items() if not f]
    est = " (height estimated)" if m.get("h_est") else ""
    if not yes:
        over = h - BAYS["modula_xl_1295"]["mm"]
        v = f"{h:.0f} mm{est}: too tall for all five ({over:.0f} mm over Modula XL 1295)"
    else:
        v = f"{h:.0f} mm{est}: fits {', '.join(yes)}" + (f"; too tall for {', '.join(no)}" if no else "")
    if kg is None:
        v += ". Mass not published"
    else:
        over = ([f"Kardex {t['tray'].split(', ')[-1]} {t['kg']}" for t in KARDEX_TRAYS if kg > t["kg"]]
                + [f"Modula {t['model'].split()[-1]} {t['kg']}" for t in MODULA_TRAYS if kg > t["kg"]])
        v += f". {kg:g} kg: " + WEIGHT_STATUS[weight_status(kg)]
        if over:
            v += f"; over {', '.join(over)} kg"
    if not (foot_kardex and foot_mod):
        d = min(m["size"][0], m["size"][1])
        v += (f". {d:.0f} mm deep: too deep for " + " and ".join(
            s for s, f in (("Kardex's 864 mm tray", foot_kardex), ("Modula's 857 mm tray", foot_mod)) if not f))
    return v


def verdict(m: dict, fits: dict, footprint: bool) -> str:
    kg = m["kg"]
    h = max(m["size"][2], m.get("h_open", 0))
    if not fits["tall_1000"]:
        v = f"still too tall at 1000 mm ({h:.0f} mm)"
        if kg and kg > max(t["kg"] for t in TRAY_RATINGS):
            v += f", and {kg:.0f} kg is over every Shuttle tray's rating"
        return v
    if fits["today_727_5"]:
        return "fits today"
    if fits["opening_996_est"]:
        v = f"needs {h:.0f} mm: fits under a 996 mm opening's ~{H_996:.0f} mm (estimated)"
    elif fits["mesh_box_970"]:
        v = f"needs {h:.0f} mm: over the 996 mm opening's ~{H_996:.0f} mm (estimated), under a mesh box's 970 mm"
    else:
        v = f"needs {h:.0f} mm: exactly the 1000 mm checked, no margin, so not at 970 mm"
    if not footprint:
        v += "; too deep for an 864 mm tray"
    if kg is None:
        v += "; mass not published"
    elif kg >= 100:
        per_area = kg / (m["size"][0] * m["size"][1] / 1e6)
        if per_area > PER_AREA_STRONG:
            v += (f"; {kg:.0f} kg is under a strong XP 500 tray's {STRONG['kg']} kg, but on its footprint it is "
                  f"{per_area / PER_AREA_STRONG:.1f}x that tray's rating per area: ask Kardex about point loads "
                  "(a spreader plate, or a Shuttle 1000 pallet tray)")
    return v


def report() -> dict:
    rows = {m["key"]: check(m) for m in MACHINES}
    return dict(
        question="byu-vcl PR #318, 2026-11-04: are there Kardex bay (opening) heights close to 1000 mm, and what would a "
                 "taller opening allow (the MX-Lab?)",
        heights_mm=dict(today=H_STD, clearance_above=CLEAR, opening_996_estimate=H_996, mesh_box=H_MESH,
                        checked=H_TALL),
        heights_note=(f"727.5 mm is Kardex's order sheet. {H_996:.0f} mm is an estimate: a 996 mm opening (one used "
                      f"XP 500) over the same 833 mm table, if its header stands where it does on the order sheet's "
                      f"unit (vlm.py's header, from Kardex's renders, {HEADER_STD:.0f} mm over the table for 727.5 mm of goods). "
                      "970 mm is a Euro mesh box, which the Shuttle 1000 stores on special trays: so those trays pass "
                      "about 1 m. 1000 mm is the height checked."),
        found=[
            "Kardex's order sheets (POF) for the XP 500 give 727.5 mm (2450 x 864) and 727 mm (3050 x 864) of product "
            "height, plus 20 mm clear, 'depends on tray type selection'.",
            "No Kardex brochure, factsheet, product page or blog found gives a taller opening for any Shuttle; Kardex's "
            "blog says 'just over 28 inches'.",
            "The Shuttle 1000 stores Euro pallets and mesh boxes on special trays, loaded by forklift. A Euro mesh box "
            "is 970 mm tall outside. Inference: the Shuttle 1000's pallet configuration passes about 1 m.",
            "One used XP 500 (2005/2006, 3050 x 864) is listed with a 996 mm opening over an 833 mm access table.",
            "ac-dev-lab has no opening height; its XP-500 quote (#372) says the 32.8 in floor-to-tray height is "
            "standard but can be changed before ordering.",
            "The Kardex TowerMat (heavy, oversized goods and pallets, 3-5 t carriers) publishes no goods height.",
        ],
        tray_ratings=[dict(t, kg_per_m2=round(t["kg"] / (t["w"] * t["d"] / 1e6)), sources=[S[k][0] for k in t["src"]])
                      for t in TRAY_RATINGS],
        machines=rows,
        enabled_at_1000=[r["model"] for k, r in rows.items() if r["fits_height"]["tall_1000"]
                         and not r["fits_height"]["today_727_5"]],
        still_too_tall_at_1000=[r["model"] for k, r in rows.items() if not r["fits_height"]["tall_1000"]],
        ask_kardex=[
            "The tallest product height through the opening on the Shuttle 700 and 1000, standard and as a special, "
            "and on the XP 500 (the used unit's 996 mm opening).",
            "The product height of the Shuttle 1000's pallet and mesh-box trays, and their rating for a concentrated "
            "load (a 250 kg machine on 0.47 m2).",
            "Whether a tall opening changes the tray delivery height (833 mm) or the unit height.",
        ],
        bay_heights_mm={k: dict(mm=b["mm"], system=b["system"], bay=b["bay"], what=b["what"], estimate=b["estimate"],
                                note=b["note"], sources=[S[s][0] for s in b["src"]], source_urls=[S[s][1] for s in b["src"]])
                        for k, b in BAYS.items()},
        bay_heights_note=(f"Five product heights, lowest first. {BAYS[QUOTE_BAY]['mm']:.0f} mm is Modula Lift Bay S, the "
                          "bay the Apr 2 Modula quote is priced with: the lowest of the five, under Kardex's published "
                          f"{H_STD} mm, so the quote as priced takes none of the machines checked here. {H_STD} mm is "
                          f"Kardex's order sheet (20 mm clear above it); {H_996} mm is our estimate (vlm.MAX_GOODS_H, the "
                          "used XP 500's 996 mm opening), not a Kardex figure; 895 and 1295 mm are Modula's Bay M and XL. "
                          "Modula's figures are for a single-delivery bay (dual delivery: 320-920 mm) and state no "
                          "clearance above the goods. The older keys (heights_mm, fits_height) are unchanged."),
        quote_bay=dict(key=QUOTE_BAY, mm=BAYS[QUOTE_BAY]["mm"], flag="the quote's bay is the lowest of the five",
                       fits=[r["model"] for r in rows.values() if r["fits_bay"][QUOTE_BAY]],
                       source=S["modula_quote"][0]),
        tray_ratings_by_system=dict(
            kardex=[dict(t, kg_per_m2=round(t["kg"] / (t["w"] * t["d"] / 1e6)), sources=[S[s][0] for s in t["src"]])
                    for t in KARDEX_TRAYS],
            modula=[dict(t, kg_per_m2=round(t["kg"] / (t["w"] * t["d"] / 1e6)), sources=[S[s][0] for s in t["src"]])
                    for t in MODULA_TRAYS],
            strongest=dict(kardex=f"{KARDEX_MAX['model']} {KARDEX_MAX['tray']}: {KARDEX_MAX['kg']} kg",
                           modula=f"{MODULA_MAX['model']} {MODULA_MAX['tray']}: {MODULA_MAX['kg']} kg"),
            note="Kardex's are the #53 quote's three trays (vlm.TRAYS); tray_ratings above has the order sheet's 500 "
                 "and 525 kg trays and the Shuttle 700 (725 kg) and 1000 (900 kg) for comparison. Modula's MC1000D "
                 "tray is 2460 mm wide, not 2500. Both rate a tray for a distributed load (per area: "
                 f"times_strong_tray_per_area, times_modula_mc1000d_per_area)."),
        fits_at_bay={k: [r["model"] for r in rows.values() if r["fits_bay"][k]] for k in BAYS},
        fits_at_bay_short={k: [SHORT[key] for key, r in rows.items() if r["fits_bay"][k]] for k in BAYS},
        over_tray_rating={**{f"kardex_{t['key']}": [r["model"] for r in rows.values()
                                                    if r["kg"] is not None and r["kg"] > t["kg"]] for t in KARDEX_TRAYS},
                          **{f"modula_{t['key']}": [r["model"] for r in rows.values()
                                                    if r["kg"] is not None and r["kg"] > t["kg"]] for t in MODULA_TRAYS}},
        mass_unknown=[r["model"] for r in rows.values() if r["kg"] is None],
        too_deep_for_both_trays=[r["model"] for r in rows.values()
                                 if not r["footprint_fits_864_tray"] and not r["footprint_fits_modula_857_tray"]],
        figure_bays="out/tall_opening_bays.png (python3 kardex_tall.py json, or bays): the machines in Sterling's review "
                    "(BAY_FIG) against the five heights, marked by their mass against each system's strongest tray",
        sources={k: dict(what=v[0], url=v[1]) for k, v in S.items()},
    )


def write_json() -> Path:
    path = OUT / "tall_opening.json"
    path.write_text(json.dumps(report(), indent=1, ensure_ascii=False) + "\n")
    return path


def plot_bays(rep: dict | None = None) -> Path:
    """out/tall_opening_bays.png: one row per machine in BAY_FIG, its height in use as a dot against the five product
    heights (Kardex blue, Modula orange, the estimate dashed), the dot marked by its mass against each system's
    strongest tray (Kardex strong 490 kg, Modula MC1000D 990 kg), with the tick or cross and the figures beside it."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.transforms import blended_transform_factory
    rep = rep or report()
    ink, ink2, muted, grid, axis, surf = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
    sysc = {"Kardex": "#2a78d6", "Modula": "#eb6834"}            # categorical slots 1 and 2 (validated)
    status = {"both": ("#0ca30c", "o", "full"), "modula_only": ("#fab219", "s", "full"),
              "neither": ("#d03b3b", "X", "full"), "unknown": (muted, "o", "none")}
    rows = sorted(((k, rep["machines"][k]) for k in BAY_FIG), key=lambda kv: (kv[1]["height_in_use_mm"], kv[0]))
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig = plt.figure(figsize=(12.8, 8.4), dpi=125, facecolor=surf)
    ax = fig.add_axes((0.175, 0.15, 0.50, 0.595), facecolor=surf)
    x0, x1 = 600.0, 2000.0
    n = len(rows)
    ax.set_xlim(x0, x1)
    ax.set_ylim(n - 0.5, -0.6)
    for i in range(n):
        ax.axhline(i, color=grid, lw=0.8, zorder=0)
    top = blended_transform_factory(ax.transData, ax.transAxes)
    bays = sorted(BAYS.items(), key=lambda kv: kv[1]["mm"])
    for j, (k, b) in enumerate(bays):          # a staircase of labels: the leftmost line reaches highest
        c = sysc[b["system"]]
        ls = (0, (5, 3)) if b["estimate"] else "-"
        lw = 2.4 if k == QUOTE_BAY else 1.6
        ax.axvline(b["mm"], color=c, lw=lw, ls=ls, zorder=1)
        yl = 1.0 + 0.04 * (len(bays) - j)
        ax.plot([b["mm"], b["mm"]], [1.0, yl], color=c, lw=lw, ls=ls, transform=top, clip_on=False)
        nfit = len([1 for _, r in rows if r["fits_bay"][k]])
        what = {"modula_s_695": "Modula Lift Bay S: the bay the Apr 2 quote is priced with",
                "kardex_727_5": "Kardex, published (order sheet)",
                "kardex_856_5_est": "Kardex, a 996 mm opening: our estimate, not published",
                "modula_m_895": "Modula Lift Bay M", "modula_xl_1295": "Modula Lift Bay XL"}[k]
        ax.text(b["mm"] + 8, yl, f"{b['mm']:g} mm  {what}  ·  {nfit} of {n} fit", transform=top, ha="left",
                va="center", fontsize=9.5, color=ink, clip_on=False,
                fontweight="bold" if k == QUOTE_BAY else "normal")
    ycol = blended_transform_factory(ax.transAxes, ax.transData)
    cols = (1.035, 1.20, 1.40)
    for xc, head in zip(cols, ("mass", f"Kardex strong\n{KARDEX_MAX['kg']} kg tray",
                               f"Modula MC1000D\n{MODULA_MAX['kg']} kg tray")):
        ax.text(xc, -0.75, head, transform=ycol, ha="left", va="bottom", fontsize=9, color=ink2, clip_on=False)
    for i, (key, r) in enumerate(rows):
        h, kg, st = r["height_in_use_mm"], r["kg"], r["strongest_tray_status"]
        col, mk, fill = status[st]
        ax.plot([h], [i], marker=mk, ms=11, color=col, mfc=col if fill == "full" else surf, mew=2.0 if fill == "none"
                else 1.2, mec=col if fill == "none" else surf, zorder=4, clip_on=False)
        note = f"{h:.0f}"
        if key == "form4":
            note += " (lid open; 554 closed)"
        elif key == "mxlab":
            note += " (without its base cabinet)"
        elif not any(r["fits_bay"].values()) and h - BAYS["modula_xl_1295"]["mm"] < 50:
            note += f" ({h - BAYS['modula_xl_1295']['mm']:.0f} mm over Bay XL)"
        ax.text(h + 22, i, note, ha="left", va="center", fontsize=9, color=ink2, zorder=5,
                bbox=dict(boxstyle="square,pad=0.15", fc=surf, ec="none"))
        if not (r["footprint_fits_864_tray"] or r["footprint_fits_modula_857_tray"]):      # left of the dot
            ax.text(h - 22, i, f"{min(r['size_mm'][:2]):.0f} mm deep: too deep for either tray", ha="right",
                    va="center", fontsize=9, color=ink2, zorder=5,
                    bbox=dict(boxstyle="square,pad=0.15", fc=surf, ec="none"))
        ax.text(cols[0], i, "not published" if kg is None else f"{kg:g} kg", transform=ycol, ha="left", va="center",
                fontsize=9.5, color=ink if kg is not None else muted, clip_on=False)
        for xc, cap in zip(cols[1:], (KARDEX_MAX["kg"], MODULA_MAX["kg"])):
            if kg is None:
                txt, c = "?  unknown", muted
            elif kg <= cap:
                txt, c = f"✓  {cap - kg:.0f} kg spare", ink
            else:
                txt, c = f"✗  {kg - cap:.0f} kg over", ink
            ax.text(xc, i, txt, transform=ycol, ha="left", va="center", fontsize=9.5, color=c, clip_on=False)
    ax.set_yticks(range(n))
    ax.set_yticklabels([SHORT[k] for k, _ in rows], fontsize=10.5, color=ink)
    ax.tick_params(axis="y", length=0, pad=8)
    ax.tick_params(axis="x", colors=muted, labelcolor=ink2, labelsize=9)
    ax.set_xticks(np.arange(600, 2001, 200))
    ax.set_xlabel("height in use, mm (the tallest point, lid open), over the tray floor", color=ink2, fontsize=9.5)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(axis)
    fig.text(0.02, 0.965, "Which machines fit through each bay: Kardex against Modula", fontsize=15, color=ink,
             fontweight="bold", ha="left", va="top")
    fig.text(0.02, 0.928, "Each machine's height against five maximum product heights; its dot marks its mass against "
             "the strongest tray of each system. A dot left of a line fits that bay.", fontsize=10, color=ink2,
             ha="left", va="top")
    present = []
    for st in ("both", "modula_only", "neither", "unknown"):
        if any(r["strongest_tray_status"] == st for _, r in rows):
            col, mk, fill = status[st]
            present.append(Line2D([], [], ls="none", marker=mk, ms=9, color=col, mfc=col if fill == "full" else surf,
                                  mec=col if fill == "none" else surf, mew=2.0 if fill == "none" else 1.0,
                                  label=WEIGHT_STATUS[st]))
    present += [Line2D([], [], color=sysc["Kardex"], lw=1.6, label="Kardex Shuttle"),
                Line2D([], [], color=sysc["Kardex"], lw=1.6, ls=(0, (5, 3)), label="Kardex, estimated"),
                Line2D([], [], color=sysc["Modula"], lw=1.6, label="Modula Lift (single delivery)")]
    fig.legend(handles=present, loc="lower left", bbox_to_anchor=(0.02, 0.035), ncol=3, frameon=False, fontsize=9,
               labelcolor=ink2, handlelength=2.2, columnspacing=1.6)
    fig.text(0.02, 0.012, "Sources: Kardex Shuttle POF order sheet (727.5 mm) and the #53 quote's trays (light 228, "
             "medium 360, strong 490 kg, 2450 x 864 mm); Modula Lift catalogue, US, Sept 2025 (bays S/M/XL; MC50D 500, "
             "MC75D 750, MC1000D 990 kg, 2460-2500 x 857 mm); the makers' figures, Instron's 6800 brochure for the "
             "68SC-2. Every figure, source and estimate: out/tall_opening.json.", fontsize=7.8, color=muted,
             ha="left", va="bottom", wrap=True)
    path = OUT / "tall_opening_bays.png"
    fig.savefig(path, dpi=125, facecolor=surf)
    plt.close(fig)
    return path


# ===================================================================================================== the scene
TRAYS3 = {"J": (-2700.0, "DED"), "K": (0.0, "desktop LPBF"), "L": (2700.0, "resin printing, N2")}
LOADS3 = {        # (key, x on the tray, turn about z); fronts 30 mm behind the tray's front lip
    "J": [("mxlab", -560.0, 0.0), ("mxlab_base", 380.0, 0.0)],
    "K": [("metalone", -780.0, 0.0), ("mx100", 60.0, 0.0), ("fusionx", 760.0, 0.0)],
    "L": [("form4", -820.0, 0.0), ("form4", -330.0, 0.0), ("n2gen", 420.0, 0.0)],
}
BACK = [("meltio_m450", 5000.0), ("instron_small", 6300.0), ("mprint", 7900.0)]   # (key, x) on red 1000 mm boxes
BACK_Y = -300.0                 # their fronts, in line with the trays
BLUE = (0.30, 0.55, 0.90)
GREEN = (0.20, 0.66, 0.36)
ORANGE = (0.95, 0.55, 0.12)
RED = (0.88, 0.30, 0.25)
BOXC = {"mxlab_base": (0.20, 0.20, 0.22), "mx100": (0.62, 0.64, 0.68), "fusionx": (0.78, 0.79, 0.81),
        "n2gen": (0.86, 0.87, 0.89)}
CAM_ALL = [(2000, -13800, 6200), (2200, 300, 500), (0, 0, 1)]
CAM_BACK = [(4600, -6400, 3400), (6400, 0, 900), (0, 0, 1)]
CAM_END = [(2270, -14000, 4300), (2270, 300, 1050), (0, 0, 1)]
CAM_J = [(-4700, -6300, 3300), (-2700, 0, 650), (0, 0, 1)]
CAM_K = [(-1500, -6300, 3300), (0, 0, 650), (0, 0, 1)]
CAM_L = [(4400, -6300, 3300), (2700, 0, 650), (0, 0, 1)]
MXLAB_BASE = ("base cabinet", "caster", "levelling foot", "base vent", "base panel", "base power", "shelf",
              "balance", "exhaust duct", "duct bellows")


def mxlab_on_tray():
    """instruments_lab.ded() without its base cabinet, shelf, balance and exhaust duct, set down by the cabinet's
    height so the MX-Lab stands on the tray floor. Its props (substrate, beads, glow) are left out."""
    import instruments_lab as IL
    inst = IL.ded()
    bh = IL.DED["base_h"]
    down = cq.Location(cq.Vector(0, 0, -bh))
    for name in list(inst.pieces):
        m = inst.pieces[name]
        if name in inst.props:
            del inst.pieces[name]
            continue
        keep = [p for p in m.parts if not (name == "body" and p.name.startswith(MXLAB_BASE))]
        m.parts = [type(p)(p.name, p.shape.moved(down), p.material) for p in keep]
    for name in list(inst.joints):
        if name not in inst.pieces:
            del inst.joints[name]
            continue
        j = inst.joints[name]
        j.pivot = (j.pivot[0], j.pivot[1], j.pivot[2] - bh)
    inst.meshes = {}
    inst.floor = False
    return inst


def _sources() -> list[Path]:
    return [HERE / f for f in ("kardex_tall.py", "instruments.py", "instruments_lab.py", "fab_metal.py", "fab_resin.py",
                               "lab.py", "lab_models/common.py")]


def load_models() -> dict:
    """{key: (Instrument, entries)} for the machines drawn as models, built one by one (not whole modules), cached."""
    import fab_metal
    import fab_resin
    import instruments
    import instruments_lab
    for mod in (instruments_lab, fab_metal, fab_resin):        # their materials, as tour._modules and fab_tour do
        tour.MATS.update(getattr(mod, "MATERIALS", {}))
        tour.GLOWY.update(m for m in getattr(mod, "MATERIALS", {}) if "glow" in m)
    CACHE.mkdir(exist_ok=True)
    h = hashlib.sha256()
    for f in _sources():
        h.update(f.read_bytes())
    path = CACHE / f"kardex_tall_{h.hexdigest()[:12]}.pkl"
    if path.exists():
        return pickle.loads(path.read_bytes())
    builds = {"mxlab": mxlab_on_tray, "metalone": fab_metal.REGISTRY["metalone"],
              "meltio_m450": fab_metal.REGISTRY["meltio_m450"], "mprint": fab_metal.REGISTRY["mprint"],
              "form4": fab_resin.REGISTRY["form4"], "instron_small": instruments.REGISTRY["instron_small"]}
    data = {}
    for key, build in builds.items():
        print(f"  building {key}", flush=True)
        inst = build()
        data[key] = (inst, tour.piece_entries(inst))
    path.write_bytes(pickle.dumps(data))
    return data


def add_tray(sc: Scene, k: str, x: float):
    for name, (shape, mat, group) in {**V.tray(k), **V.lamp(k)}.items():
        if hasattr(shape, "vals"):
            shape = shape.val() if len(shape.vals()) == 1 else cq.Compound.makeCompound(shape.vals())
        e = lab._entry(lab.to_mesh(shape, 2.0), mat, group)
        sc.add(name, e["mesh"], e["color"], group, opacity=e["opacity"])
    sc.gmat[f"tray_{k}"] = T((x, 0, 0))


def envelope(sc: Scene, name, x0, x1, y0, y1, z0, h, color, group="static", strength=1.0, lid_only=False):
    """A see-through box `h` tall from z0, its lid a little stronger; lid_only: just a thin plane at z0 + h."""
    if not lid_only:
        sc.add(f"{name} box", pv.Box(bounds=(x0, x1, y0, y1, z0, z0 + h)), color, group, opacity=0.06 * strength,
               specular=0.0, ambient=0.6)
    sc.add(f"{name} lid", pv.Box(bounds=(x0, x1, y0, y1, z0 + h - 3, z0 + h)), color, group,
           opacity=min(0.32 * strength, 0.8), specular=0.0, ambient=0.6)


def box_machine(sc: Scene, name, size, color, group, at_xy, z0, opacity=1.0):
    """A machine that isn't modelled: a box at its published size, a dark band on its front so it reads as a front."""
    w, d, h = size
    x, y = at_xy
    sc.add(f"{name} body", pv.Box(bounds=(x - w / 2, x + w / 2, y - d / 2, y + d / 2, z0, z0 + h)), color, group,
           opacity=opacity, specular=0.1)
    sc.add(f"{name} front", pv.Box(bounds=(x - w / 2 + 30, x + w / 2 - 30, y - d / 2 - 2, y - d / 2,
                                           z0 + 0.35 * h, z0 + 0.80 * h)), (0.18, 0.19, 0.21), group,
           opacity=opacity, specular=0.3)


def placed(inst, x, y, turn, z) -> np.ndarray:
    x0, x1, y0, y1, z0, _ = inst.bbox()
    c = np.array([(x0 + x1) / 2, (y0 + y1) / 2, z0])
    if y is None:
        y = -IN_D / 2 + 30 + (y1 - y0) / 2
    return T((x, y, z)) @ R((0, 0, 1), turn) @ T(-c)


def build():
    data = load_models()
    sizes = {m["key"]: m["size"] for m in MACHINES}
    sc = Scene(NAME, TITLE, gif=False)
    sc.cam = list(CAM_ALL)
    tour.studio(sc, size=24000, at=(2600, 700))
    rigs = {}
    for k, (tx, _) in TRAYS3.items():
        add_tray(sc, k, tx)
        envelope(sc, f"tray {k} today", -IN_W / 2, IN_W / 2, -IN_D / 2, IN_D / 2, V.T_FLOOR, H_STD, BLUE,
                 group=f"tray_{k}")
        envelope(sc, f"tray {k} tall", -IN_W / 2, IN_W / 2, -IN_D / 2, IN_D / 2, V.T_FLOOR, H_TALL, GREEN,
                 group=f"tray_{k}", strength=1.2)
        envelope(sc, f"tray {k} 996", -IN_W / 2, IN_W / 2, -IN_D / 2, IN_D / 2, V.T_FLOOR, H_996, ORANGE,
                 group=f"tray_{k}", strength=0.7, lid_only=True)
        for i, (key, x, turn) in enumerate(LOADS3[k]):
            if key in data:
                inst, ents = data[key]
                rig = tour.Rig(sc, inst, ents, f"{k}{i}_{key}:", at=placed(inst, x, None, turn, V.T_FLOOR),
                               parent=f"tray_{k}")
                if key == "form4":
                    rig.move({"cover": (0.0, 1.0)})(1.0)      # the cover open on its rear hinge, 844 mm
                rigs[f"{k}{i}"] = rig
            else:
                w, d, h = sizes[key]
                box_machine(sc, f"{k}{i} {key}", (w, d, h), BOXC[key], f"tray_{k}",
                            (x, -IN_D / 2 + 30 + d / 2), V.T_FLOOR, opacity=0.55 if key == "mxlab_base" else 1.0)
    for key, x in BACK:
        inst, ents = data[key]
        x0, x1, y0, y1, _, _ = inst.bbox()
        rigs[key] = tour.Rig(sc, inst, ents, f"back_{key}:", at=placed(inst, x, BACK_Y + (y1 - y0) / 2, 0.0, 0.0))
        w, d = x1 - x0, y1 - y0
        envelope(sc, f"back {key}", x - w / 2 - 20, x + w / 2 + 20, BACK_Y - 20, BACK_Y + d + 20, 0.0, H_TALL, RED,
                 strength=1.8)
    return sc, data, rigs


def movie():
    sc, data, rigs = build()
    r = report()["machines"]
    tx = {k: v[0] for k, v in TRAYS3.items()}
    zt = V.T_FLOOR
    n = 6
    sc.step(f"1/{n}", "Kardex publishes 727.5 mm of product height through the opening (blue, its order sheet). "
            "Green is 1000 mm: the Shuttle 1000 stores Euro mesh boxes, 970 mm tall, on special trays, so a taller "
            f"opening exists, but Kardex publishes no figure. Orange, about {H_996:.0f} mm: one used XP 500's 996 mm "
            "opening, estimated.", 3.4, None, hold=1.6,
            labels=[("727.5 mm today", (tx["J"] - IN_W / 2, -IN_D / 2, zt + H_STD), (0.07, 0.62)),
                    (f"~{H_996:.0f} mm (996 mm opening, est.)", (tx["J"] - IN_W / 2, -IN_D / 2, zt + H_996),
                     (0.07, 0.48)),
                    ("1000 mm", (tx["J"] - IN_W / 2, -IN_D / 2, zt + H_TALL), (0.07, 0.34))])
    mx = r["mxlab"]
    sc.step(f"2/{n}", f"The InssTek MX-Lab, 835 mm, {mx['kg']} kg: under 1000 mm with 165 mm to spare, and under a "
            f"strong XP 500 tray's 500 kg. But it puts {mx['kg_per_m2_on_its_footprint']} kg/m2 on its footprint, "
            f"{mx['times_strong_tray_per_area']:.1f} times the strong tray's rating per area: a spreader plate, or a "
            "Shuttle 1000 pallet tray. Its base cabinet (estimated, grey) and argon come too.", 4.4, None, hold=1.6,
            cam_to=CAM_J,
            labels=[("InssTek MX-Lab", (tx["J"] - 560, -IN_D / 2, zt + 835), (0.30, 0.20)),
                    ("base cabinet (estimated)", (tx["J"] + 380, -IN_D / 2, zt + 1000), (0.68, 0.18))])
    sc.step(f"3/{n}", "Desktop LPBF: the Sharebot MetalONE is exactly 1000 mm (150 kg), so it fits with no margin. "
            "The Mastrex MX100 (800 mm, 125 kg) and Lasefinity Fusion X (860 mm, mass not published; drawn as boxes) "
            "fit with room. Each needs inert gas through the dock.", 4.2, None, hold=1.4, cam_to=CAM_K,
            labels=[("Sharebot MetalONE", (tx["K"] - 780, -IN_D / 2, zt + 1000), (0.24, 0.18)),
                    ("Mastrex MX100 (box)", (tx["K"] + 60, -IN_D / 2, zt + 800), (0.50, 0.26)),
                    ("Lasefinity Fusion X (box)", (tx["K"] + 760, -IN_D / 2, zt + 860), (0.78, 0.20))])
    sc.step(f"4/{n}", "Two Formlabs Form 4s with their covers open (844 mm): with 1000 mm they could open in their "
            "slot, not just at the opening. The Parker Balston N2 generator (889 mm, 50 kg; a box) goes on a tray "
            "too.", 3.8, None, hold=1.4, cam_to=CAM_L,
            labels=[("Form 4, cover open", (tx["L"] - 820, -IN_D / 2, zt + 844), (0.26, 0.20)),
                    ("N2 generator (box)", (tx["L"] + 420, -IN_D / 2, zt + 889), (0.72, 0.22))])
    tall = [(f"{data[k][0].model}, {data[k][0].size[2]:.0f} mm", (x, BACK_Y, data[k][0].size[2]),
             (0.16 + 0.34 * i, 0.16 + 0.06 * (i % 2))) for i, (k, x) in enumerate(BACK)]
    sc.step(f"5/{n}", "Still too tall at 1000 mm (red boxes): the Meltio M450, the Instron 68SC-2 (its shortest "
            "single column, the 68SC-05, is 1020 mm) and the MPRINT. The Kobelco HIP, 1300 mm and 1100 kg, is over "
            "every Shuttle tray's rating as well.", 3.8, None, hold=1.6, cam_to=CAM_BACK, labels=tall)
    sc.step(f"6/{n}", "Blue 727.5 mm (today), orange ~856 mm (est.), green 1000 mm. About 1000 mm would put DED, "
            "desktop LPBF, an open Form 4 and an N2 generator on trays. Ask Kardex for the Shuttle 700 and 1000's "
            "tallest opening, and a pallet tray's rating for a point load.",
            3.6, None, hold=2.4, cam_to=CAM_END, still=True,
            labels=[(f"tray {k}: {role}", (tx[k], -IN_D / 2, zt + H_TALL), (fx, 0.20))
                    for (k, (_, role)), fx in zip(TRAYS3.items(), (0.06, 0.30, 0.70))]
            + [("too tall at 1000 mm", (BACK[1][1], BACK_Y, H_TALL + 500), (0.92, 0.16))])
    return sc.save()


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "json":
        print(write_json())
        rep = report()
        print(plot_bays(rep))
        print("enabled at 1000 mm:", rep["enabled_at_1000"])
        print("still too tall:", rep["still_too_tall_at_1000"])
        for k, v in rep["machines"].items():
            print(f"  {k:14s} {v['verdict']}")
        print("by product height (round 8):")
        for k, names in rep["fits_at_bay_short"].items():
            print(f"  {BAYS[k]['label']:22s} {', '.join(names) or 'none'}")
        for k, names in rep["over_tray_rating"].items():
            print(f"  over {k:20s} {', '.join(names) or 'none'}")
    elif args and args[0] == "bays":
        print(plot_bays())
    else:
        print(write_json())
        print(movie(), flush=True)
        if not PREVIEW:
            import line
            print(line.mp4_to_gif(OUT / "mp4" / f"{NAME}.mp4", OUT / f"{NAME}.gif"), flush=True)
