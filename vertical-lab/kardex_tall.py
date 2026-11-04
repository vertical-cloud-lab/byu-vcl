"""A taller opening on the Kardex Shuttle: what Kardex publishes, and what about 1000 mm of product height would put on
a tray (byu-vcl #303, PR #318).

    python3 kardex_tall.py json                       # the checks -> out/tall_opening.json (no rendering)
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
  unit (vlm.py draws the mouth about 846 mm tall for 727.5 mm of goods), that opening takes about 856 mm: an estimate.

So three heights are checked: 727.5 mm (today), about 856 mm (the 996 mm opening, estimated) and 1000 mm (Sterling's
figure, about a mesh box). Each machine is also checked against the load per tray, which Kardex rates per tray and per
area (a distributed load), and against the tray's depth.

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
H_STD = V.MAX_GOODS_H         # 727.5 mm, Kardex's order sheet (POF) for the XP 500 at 2450 x 864
CLEAR = V.GOODS_CLEAR         # 20 mm clear above the goods, required (POF)
MOUTH_STD = V.Z_OPEN_TOP - V.Z_OPEN        # the mouth vlm.py draws for 727.5 mm of goods, from Kardex's renders
H_996 = round(H_STD + 996.0 - (V.Z_OPEN_TOP - V.Z_SILL), 1)  # a 996 mm opening over the same 833 mm access table
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
    dict(model="Shuttle XP 700", tray="up to 4050 x 1270", w=2450, d=864, kg=725, src=["xp", "fact"],
         note="'up to 725 kg'; the rating at a given width isn't published"),
    dict(model="Shuttle XP 1000", tray="2450 wide, 610-1778 deep", w=2450, d=864, kg=900, src=["xp", "heavy"],
         note="900 kg at 2450 mm (brochure); Kardex's page now says up to 825 kg; special trays take pallets and mesh "
              "boxes, i.e. concentrated loads"),
]
STRONG = TRAY_RATINGS[0]
PER_AREA_STRONG = STRONG["kg"] / (STRONG["w"] * STRONG["d"] / 1e6)        # kg/m2, about 236 (48.4 lb/sq ft)

# ----------------------------------------------------------------------------------------- the machines checked
# key, model, W x D x H closed (mm), H in use if taller (lid or cover open), kg (None: not published), needs, sources,
# how the scene draws it ("model": an Instrument; "box"; None: not drawn)
MACHINES = [
    dict(key="mxlab", model="InssTek MX-Lab (DED, powder-fed laser)", size=(680, 684, 835), kg=250, src=["mxlab"],
         needs="argon (> 99.999 %, O2 <= 50 ppm option), powder carrier gas, 220 V 1-phase 15(20) A; exhaust; its "
               "laser's cooling and what its base cabinet holds are not published", draw="model"),
    dict(key="mxlab_base", model="MX-Lab base cabinet (size estimated)", size=(900, 760, 1000), kg=None,
         src=["inst"], needs="unknown: not published", draw="box",
         note="instruments_lab.ded()'s estimate, scaled from a photo; if it holds the laser source, it rides with the "
              "MX-Lab, since a process fibre can't go through a dock"),
    dict(key="mx100", model="Mastrex MX100 (LPBF)", size=(560, 560, 800), kg=125, src=["mx100"],
         needs="120 V; nitrogen (an NG150 generator is the accessory)", draw="box"),
    dict(key="fusionx", model="Lasefinity Fusion X (LPBF)", size=(600, 650, 860), kg=None, src=["fusionx"],
         needs="N2 or Ar; on-board filtration", draw="box"),
    dict(key="metalone", model="Sharebot MetalONE (LPBF)", size=(740, 630, 1000), kg=150, src=["metalone"],
         needs="inert gas; later listings give 1470 mm and 270-315 kg, probably with a stand", draw="model"),
    dict(key="dimetal", model="Kings 3D DiMetal-100 (LPBF)", size=(690, 720, 1000), kg=140, src=["dimetal"],
         needs="220 V 50 Hz; inert gas", draw=None),
    dict(key="n2gen", model="Parker Balston UHPN2-1100 (N2 generator)", size=(305, 406, 889), kg=50, src=["n2"],
         needs="compressed air 60-125 psig, 120 V", draw="box"),
    dict(key="form4", model="Formlabs Form 4, cover open", size=(398, 367, 554), h_open=844, kg=18.3, src=["fab"],
         needs="power; the resin and the IPA are open questions for Kardex and EHS (README)", draw="model"),
    dict(key="meltio_m450", model="Meltio M450 (wire-laser DED)", size=(560, 600, 1400), kg=250, src=["fab"],
         needs="argon, cooling, 2-5 kW peak", draw="model"),
    dict(key="instron_small", model="Instron 68SC-2", size=(460, 615, 1410), kg=62, src=["inst"],
         needs="power; the shortest single column, the 68SC-05, is 1020 mm", draw="model"),
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
    return out


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
                      f"unit (vlm.py's mouth, from Kardex's renders, about {MOUTH_STD:.0f} mm for 727.5 mm of goods). "
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
        sources={k: dict(what=v[0], url=v[1]) for k, v in S.items()},
    )


def write_json() -> Path:
    path = OUT / "tall_opening.json"
    path.write_text(json.dumps(report(), indent=1, ensure_ascii=False) + "\n")
    return path


# ===================================================================================================== the scene
TRAYS3 = {"J": (-2700.0, "DED"), "K": (0.0, "desktop LPBF"), "L": (2700.0, "resin printing, N2")}
LOADS3 = {        # (key, x on the tray, turn about z); fronts 30 mm behind the tray's front lip
    "J": [("mxlab", -560.0, 0.0), ("mxlab_base", 380.0, 0.0)],
    "K": [("metalone", -780.0, 0.0), ("mx100", 60.0, 0.0), ("fusionx", 760.0, 0.0)],
    "L": [("form4", -820.0, 0.0), ("form4", -330.0, 0.0), ("n2gen", 420.0, 0.0)],
}
BACK = [("meltio_m450", -2400.0), ("instron_small", 0.0), ("mprint", 2400.0)]   # (key, x) on red 1000 mm boxes
BACK_Y = 1250.0
BLUE = (0.30, 0.55, 0.90)
GREEN = (0.20, 0.66, 0.36)
ORANGE = (0.95, 0.55, 0.12)
RED = (0.88, 0.30, 0.25)
BOXC = {"mxlab_base": (0.20, 0.20, 0.22), "mx100": (0.62, 0.64, 0.68), "fusionx": (0.78, 0.79, 0.81),
        "n2gen": (0.86, 0.87, 0.89)}
CAM_ALL = [(-2600, -8800, 4300), (0, 400, 800), (0, 0, 1)]
CAM_J = [(-3900, -4300, 2500), (-2700, 0, 520), (0, 0, 1)]
CAM_K = [(-1100, -4300, 2500), (0, 0, 560), (0, 0, 1)]
CAM_L = [(3900, -4300, 2500), (2700, 0, 520), (0, 0, 1)]
CAM_BACK = [(1800, -7600, 3600), (0, BACK_Y, 1000), (0, 0, 1)]
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


def first_action(rig) -> dict:
    for cap, _, targets in rig.inst.actions:
        if cap:
            return targets
    return {}


def build():
    data = load_models()
    sizes = {m["key"]: m["size"] for m in MACHINES}
    sc = Scene(NAME, TITLE, gif=False)
    sc.cam = list(CAM_ALL)
    tour.studio(sc, size=17000, at=(0, 700))
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
                    rig.move(first_action(rig))(1.0)          # the cover open, 844 mm
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
    n = 5
    sc.step(f"1/{n}", "Kardex publishes 727.5 mm of product height through the opening (blue, its order sheet). "
            "Green is 1000 mm: the Shuttle 1000 stores Euro mesh boxes, 970 mm tall, on special trays, so a taller "
            f"opening exists, but Kardex publishes no figure. Orange, about {H_996:.0f} mm: one used XP 500's 996 mm "
            "opening, estimated.", 3.4, None, hold=1.6,
            labels=[("727.5 mm today", (tx["L"] + IN_W / 2, -IN_D / 2, zt + H_STD), (0.90, 0.56)),
                    (f"~{H_996:.0f} mm (996 mm opening, est.)", (tx["L"] + IN_W / 2, -IN_D / 2, zt + H_996),
                     (0.90, 0.44)),
                    ("1000 mm", (tx["L"] + IN_W / 2, -IN_D / 2, zt + H_TALL), (0.90, 0.32))])
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
    sc.step(f"5/{n}", "Still too tall at 1000 mm: the Meltio M450 (1400 mm), the Instron 68SC-2 (1410; the shortest "
            "single column is 1020) and the MPRINT (1900). The Kobelco HIP (1300 mm, 1100 kg) is over every Shuttle "
            "tray's rating as well.", 3.8, None, hold=2.4, cam_to=CAM_ALL, still=True,
            labels=[(f"tray {k}: {role}", (tx[k], -IN_D / 2, zt + H_TALL + 60), (0.18 + 0.32 * i, 0.20))
                    for i, (k, (_, role)) in enumerate(TRAYS3.items())])
    return sc.save()


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "json":
        print(write_json())
        rep = report()
        print("enabled at 1000 mm:", rep["enabled_at_1000"])
        print("still too tall:", rep["still_too_tall_at_1000"])
        for k, v in rep["machines"].items():
            print(f"  {k:14s} {v['verdict']}")
    else:
        print(write_json())
        print(movie(), flush=True)
        if not PREVIEW:
            import line
            print(line.mp4_to_gif(OUT / "mp4" / f"{NAME}.mp4", OUT / f"{NAME}.gif"), flush=True)
