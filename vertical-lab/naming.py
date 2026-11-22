"""Names for every piece of equipment in the vertical lab, generated from the model, with checks.

Sterling, PR #318, 2026-11-20: "open another PR focused on clever naming schemes for each piece of equipment". Round 2,
PR #376, 2026-11-22: people's names needed their history explained first ("prandtl" hard to spell, pronounce, and
obscure); "something kind of self-consistent with halite"; keep the mountains, and call one "timp". The write-up is
notes/naming.md. Three layers:

1. **A call name for each station**, from a family that says what class of thing it is. Stations are stones, and the
   stone's own property is the station's job, so the hint needs no history: the CubXL is halite (salt; its
   electrolyte is salt water), the XRF fluorite (fluorescence is named after it), the Mastersizer opal (its colours
   are diffraction), the PIP marble (a ball pressed into the metal), the three tensile frames pebble, cobble and
   boulder, by size. Robots are robots of history, the Shuttles the peaks over Provo (timp and nebo). The name
   belongs to the role, not the box: a replacement MiniFlex is still quartz.
2. **Everything bolted to a station, a tray, a Shuttle or a robot takes its parent's name and a suffix** from a fixed
   list (SUFFIX): ``quartz-pc``, ``tray-d-cam0``, ``timp-bay-front``, ``elsie-arm``. So a hostname says where to look,
   and code can derive one.
3. **A permanent asset number** (VCL-0001 ...) for the physical unit, on its label and in out/naming/asset_ids.json.
   It is keyed by the role (``xrd-pc``), not the name (``quartz-pc``), so it doesn't change when a unit moves or its
   role is renamed; round 2's renames kept every number. It is never reused.

Tray letters stay as they are (A-S); said aloud they are NATO words ("tray Delta"), since the narration voice said
"Tray A" as "tray uh" in round 12.

    python3 naming.py            # registry + checks + figures + labels (out/naming/)
    python3 naming.py check      # the checks only; exits 1 if a hard check fails
    python3 naming.py registry   # out/naming/registry.{json,csv,md}

Inputs, all from the model as committed: out/tray_plan.json (setup_lab.py fit: every tray's items and every floor
machine's footprint), out/voltage.json (every machine's maker and model), services.BAY_UNITS and atom_cams.CAMERAS
(read from the source, so no CAD is built). Nothing on a real device is renamed.
"""
from __future__ import annotations

import ast
import csv
import itertools
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "naming"
REPO_STRINGS = ("vertical-cloud-lab", "byu-vcl", "digital-alloy-lab", "digital-wetlab", "powder-doser", "robot-arms")

# ===================================================================================================== the families
# class -> (family, why this family). Round 2 (Sterling, PR #376, 2026-11-22): "a lot of people would need the
# historical context explained to them in advance ... 'prandtl' hard to spell, pronounce, and is obscure ... The
# names also don't have to be real people. It could also be something kind of self-consistent with halite. I
# particularly like the use of mountain names for the vertical lift modules. Referring to one as 'timp' would be
# quite good." So the stations are stones, and a stone's own property, not a person's history, is the hint.
FAMILIES = {
    "station": ("stones: minerals, rocks and gems", "A stone everyone has heard of, whose own property is the "
                "station's job: halite is salt, and the CubXL's electrolyte is salt water."),
    "printer": ("stones made the way a print is", "Stones built in layers for the polymer printers (shale, mica) "
                "and rocks from melt for the metal ones (magma, basalt, cinder, olivine)."),
    "robot": ("robots of history", "Elsie was built to steer home to her lit hutch to recharge (1949); Freddy "
              "assembled models from a heap of parts by vision (1973). A MiR250 with a UR12e and a wrist camera does "
              "both."),
    "shuttle": ("the Wasatch peaks over Provo", "The two tallest things in the lab after round 14's 9.15 m Shuttles: "
                "Timp and Nebo."),
}

# station key -> (call name, family, what it is, the stone, what it is made of, why the name fits, source). The
# columns are the round-1 ones (the 4th held a namesake, the 5th their dates), so the registry and labels didn't change
# shape. A name no one can spell from hearing it, or say from reading it, is out, however good its story.
W = "https://en.wikipedia.org/wiki/"
STATIONS = {
    # ---------------------------------------------------------------- tray A
    "ot2": ("aquamarine", "station", "Opentrons OT-2 liquid handler", "aquamarine (sea-blue beryl)", "Be3Al2Si6O18",
            "Latin aqua marina, 'sea water': the station that moves liquids", W + "Aquamarine_(gem)"),
    "cubxl": ("halite", "station", "CubXL corrosion cell with its EZstat Pro potentiostat", "halite (rock salt)",
              "NaCl", "salt: the cell's electrolytes are 0.6, 0.06 and 0.006 M NaCl, and salt water is what corrodes",
              W + "Halite"),
    # ---------------------------------------------------------------- tray B
    "doser": ("talc", "station", "multi-doser (chain carousel v5) on an A&D HR-202i", "talc", "Mg3Si4O10(OH)2",
              "talcum powder, the powder everyone knows: the doser weighs out powders", W + "Talc"),
    "vacuum_press": ("sandstone", "station", "Specac Atlas Autotouch 15T vacuum press", "sandstone", "rock",
                     "sand pressed and cemented into stone, as the press turns a powder into a pellet",
                     W + "Sandstone"),
    # ---------------------------------------------------------------- tray C
    "h2d": ("shale", "printer", "Bambu Lab H2D", "shale", "rock", "laid down in thin layers, and it splits along them: "
            "a print is built the same way", W + "Shale"),
    "a1mini": ("mica", "printer", "Bambu Lab A1 mini", "mica", "sheet silicate group", "it splits into layers thinner "
               "than paper, and a print is built of layers; the H2D's small partner", W + "Mica"),
    # ---------------------------------------------------------------- tray D
    "sem": ("pyrite", "station", "Hitachi TM4000PlusII SEM with Oxford AZtecOne EDS", "pyrite (fool's gold)", "FeS2",
            "it looks like gold; the SEM's EDS sees the iron and the sulfur", W + "Pyrite"),
    "xrd": ("quartz", "station", "Rigaku MiniFlex XRD", "quartz (rock crystal)", "SiO2",
            "the crystal the word was coined for (Greek krystallos, ice): the XRD tells one crystal from another",
            W + "Quartz"),
    # ---------------------------------------------------------------- tray E
    "pip": ("marble", "station", "Plastometrex PLX-Benchtop (indentation plastometry)", "marble", "rock (CaCO3)",
            "the rock, and the glass ball: the PIP presses a hard ball into the metal and reads its stress-strain "
            "curve from the dent", W + "Marble_(toy)"),
    "nanoindenter": ("sapphire", "station", "KLA iMicro nanoindenter", "sapphire (corundum)", "Al2O3",
                     "Mohs 9: of all minerals only diamond, the indenter's tip, is harder", W + "Sapphire"),
    "mastersizer": ("opal", "station", "Malvern Mastersizer 3000 with Aero S (laser diffraction)", "opal",
                    "SiO2·nH2O", "its colours are light diffracted by silica spheres a few hundred nanometres "
                    "across; the Mastersizer sizes particles by the light they diffract", W + "Opal"),
    # ---------------------------------------------------------------- tray F
    "polisher": ("emery", "station", "LECO PX500 grinder-polisher with its disc magazine", "emery",
                 "rock (corundum and magnetite)", "the abrasive of emery paper and emery boards",
                 W + "Emery_(rock)"),
    "furnace": ("obsidian", "station", "Nabertherm NAT 15/65 furnace with the quench tank", "obsidian",
                "volcanic glass", "lava quenched too fast to crystallize: the furnace is the station with the "
                "quench tank", W + "Obsidian"),
    "mounting_press": ("fossil", "station", "LECO MX400 hot mounting press", "a fossil", "",
                       "a specimen set in stone, as the press sets a sample in a resin puck", W + "Fossil"),
    # ---------------------------------------------------------------- tray K
    "glovebox_tray": ("agate", "station", "the tray's N2 glovebox (ours)", "agate", "SiO2",
                      "it grows inside a closed hollow in rock, shut off from the world outside", W + "Agate"),
    "vhx": ("tigereye", "station", "Keyence VHX-7000 digital microscope with EA-300 LIBS", "tiger's eye",
            "quartz with fibres", "the stone with an eye in it: the lab's eye for a close look", W + "Tiger's_eye"),
    # ---------------------------------------------------------------- tray L
    "tensile_h": ("rift", "station", "ZwickRoell zwickiLine Z5.0 TN (horizontal tensile)", "a rift", "landform",
                  "where the crust is pulled apart, as Utah's Basin and Range is: the frame that pulls sideways",
                  W + "Rift"),
    "hardness": ("topaz", "station", "Mitutoyo HM-220 micro-Vickers tester", "topaz", "Al2SiO4(F,OH)2",
                 "Mohs 8, the hardness scale everyone learns, and Utah's state gem (1969)", W + "Topaz"),
    # ---------------------------------------------------------------- tray M
    "xrf": ("fluorite", "station", "Bruker S2 PUMA XRF with XY autochanger", "fluorite", "CaF2",
            "fluorescence is named after it (Stokes, 1852), and an XRF reads X-ray fluorescence",
            W + "Fluorescence"),
    "cnc": ("garnet", "station", "Makera Carvera CNC mill", "garnet", "silicate group",
            "it cuts metal: the abrasive of garnet paper and of waterjet cutters", W + "Garnet"),
    # ---------------------------------------------------------------- tray H
    "pcb_line": ("galena", "station", "PCB line: DDM stencil printer, Opulo LumenPnP, Puhui reflow oven", "galena",
                 "PbS", "lead ore, and the crystal in a crystal radio: electronics' first semiconductor",
                 W + "Galena"),
    # ---------------------------------------------------------------- tray G
    "form4": ("gypsum", "printer", "Formlabs Form 4 resin printers with Form Wash and Form Cure", "gypsum (plaster)",
              "CaSO4·2H2O", "plaster of Paris is made from it: a liquid that sets solid, as the Form 4's resin does",
              W + "Gypsum"),
    # ---------------------------------------------------------------- tray I
    "snowpod": ("cinder", "printer", "SnowX SnowPod desktop LPBF printers with the NitroPod", "cinder",
                "volcanic rock", "small bits of lava that freeze as they fly: the two small powder-bed printers",
                W + "Cinder_cone"),
    # ---------------------------------------------------------------- floor
    "repowder": ("pearl", "station", "AMAZEMET rePowder ultrasonic atomizer", "a pearl", "aragonite (CaCO3)",
                 "a sphere: the atomizer makes metal powder in spheres", W + "Pearl"),
    "sieve_cell": ("dune", "station", "sieving cell: Retsch AS 200, tipper and wash module", "a dune", "sand",
                   "the wind sorts its sand by grain size, as the sieves sort powder", W + "Dune"),
    "aconity": ("magma", "printer", "Aconity MIDI+ LPBF printer and the depowdering box", "magma", "molten rock",
                "the melt every volcanic rock starts as: the printer melts its powder bed with a laser", W + "Magma"),
    "glovebox": ("geode", "station", "Inert PureLab HE glovebox", "a geode", "",
                 "a closed stone with a clean, crystal-lined room inside", W + "Geode"),
    "packaging": ("pumice", "station", "packaging station: sealer, label printers, foam inserts", "pumice",
                  "volcanic glass foam", "stone foam, light enough to float: the station packs samples in foam",
                  W + "Pumice"),
    "instron_floor": ("boulder", "station", "Instron 68FM-100 with its 3119-608 chamber", "a boulder", "over 256 mm",
                      "the big stone: the 100 kN frame (the 2 kN one is pebble)", W + "Boulder"),
    "instron_small": ("pebble", "station", "Instron 68SC-2 table frame", "a pebble", "4-64 mm",
                      "the small stone: the 2 kN frame (the 100 kN one is boulder)", W + "Pebble"),
    "fumehood": ("fumarole", "station", "Labconco Protector XStream ducted fume hood", "a fumarole", "volcanic vent",
                 "a vent that lets a volcano's gases out (Latin fumus, smoke), as the hood lets out the lab's fumes",
                 W + "Fumarole"),
    "ded": ("olivine", "printer", "InssTek MX-Lab DED (blends compositions in the melt pool)", "olivine",
            "(Mg,Fe)2SiO4", "one crystal with any blend of magnesium and iron, a solid solution: the DED blends "
            "compositions in its melt pool", W + "Olivine"),
    "wire_edm": ("flint", "station", "FANUC ROBOCUT wire EDM", "flint", "SiO2 (chert)",
                 "struck with steel it throws sparks, and the EDM cuts with sparks", W + "Flint"),
    "eos_m400": ("basalt", "printer", "EOS M 400-4 (scale-up)", "basalt", "volcanic rock",
                 "the commonest rock made from melt, laid down in the biggest volumes: the scale-up printer",
                 W + "Basalt"),
    "meltio_cell": ("lava", "station", "Meltio robot cell (propeller repair)", "lava", "molten rock",
                    "new rock laid down on old, as the cell lays new metal on a worn propeller", W + "Lava"),
    "icpms": ("ruby", "station", "Agilent 7850 ICP-MS with SPS 4, in its own trace-metals hood", "ruby (corundum)",
              "Al2O3 + Cr", "red from a trace of chromium: the ICP-MS measures traces", W + "Ruby"),
    "bn_station": ("borax", "station", "the atomizer's BN coating station (ours)", "borax", "Na2B4O7·10H2O",
                   "the boron mineral everyone knows: the station coats parts with boron nitride", W + "Borax"),
    # ---------------------------------------------------------------- robots and Shuttles
    "unit1": ("elsie", "robot", "MiR250 + UR12e + Robotiq 2F-85 + RealSense D405, unit 1", "W. Grey Walter's Elsie",
              "1949", "a robot tortoise built to steer home to its lit hutch to recharge",
              "https://cyberneticzoo.com/?p=491"),
    "unit2": ("freddy", "robot", "MiR250 + UR12e + Robotiq 2F-85 + RealSense D405, unit 2", "Edinburgh's Freddy",
              "1969-1976", "a hand-eye robot that assembled models from a heap of parts by vision", W + "Freddy_II"),
    "vlm": ("timp", "shuttle", "Kardex Shuttle XP 500, 9.15 m, Shuttle 1", "Mount Timpanogos", "3,582 m",
            "the peak over Provo, which everyone in Utah County calls Timp", W + "Mount_Timpanogos"),
    "vlm2": ("nebo", "shuttle", "Kardex Shuttle XP 500, 9.15 m, Shuttle 2", "Mount Nebo", "3,637 m",
             "the highest peak of the Wasatch, south of Provo", W + "Mount_Nebo_(Utah)"),
}
# round 1's names (people), for the record: notes/naming.md has the table, and asset_ids.json kept every number
ROUND1 = {"ot2": "ostwald", "cubxl": "tafel", "doser": "lavoisier", "vacuum_press": "bridgman", "h2d": "gutenberg",
          "a1mini": "aldus", "sem": "ruska", "xrd": "lonsdale", "pip": "prandtl", "nanoindenter": "sneddon",
          "mastersizer": "tyndall", "polisher": "beilby", "furnace": "preston", "mounting_press": "baekeland",
          "glovebox_tray": "rutherford", "vhx": "sorby", "tensile_h": "griffith", "hardness": "sandland",
          "xrf": "noddack", "cnc": "maudslay", "pcb_line": "eisler", "form4": "senefelder", "snowpod": "maiman",
          "repowder": "faraday", "sieve_cell": "agricola", "aconity": "deckard", "glovebox": "ramsay",
          "packaging": "mclean", "instron_floor": "kirkaldy", "instron_small": "galileo", "fumehood": "davy",
          "ded": "gibbs", "wire_edm": "lazarenko", "eos_m400": "javan", "meltio_cell": "brunel", "icpms": "aston",
          "bn_station": "blodgett", "unit1": "elsie", "unit2": "freddy", "vlm": "timpanogos", "vlm2": "nebo"}
# spare names, checked like the rest, for the next unit of a family (the three-each plan, a third robot, Shuttle 3,
# #367's machining station). Dropped: jade (MDI JADE, the XRD software), onyx (Markforged's filament), granite (the
# balance's granite block), amber (the beacons go amber), diamond and graphite (an indenter tip, a crucible),
# calcite (too like halite), hematite (likewise), apatite (said "appetite"), corundum ("conundrum"), niter
# ("neither"), touchstone, sunstone and whetstone (too like sandstone), jasper (a common first name), chalk (too like
# talc), cobble (too like pebble and marble), emerald (too like emery). beryl was the VHX's (the first spectacles were
# ground from it, hence German Brille) until it sounded like pebble, so it is not a spare either.
SPARES = {
    "robot": ["unimate", "genghis"],
    "shuttle": ["cascade", "lonepeak"],
    "station": ["lapis", "turquoise", "citrine", "chert"],
}

# How the narration voice is to say a name, for longform.SAY / longform.IPA once a name is narrated (longform.py is not
# changed here). Round 1's voice-and-recognizer check (out/naming/tts_check.json) found these for the names kept.
PRONOUNCE = {"Unimate": {"ipa": "jˈuːnɪmˌeɪt"}, "Genghis": {"ipa": "ɡˈɛŋɡɪs"}, "Cascade": {"ipa": "kæskˈeɪd"},
             "Quebec": {"ipa": "kwɪbˈɛk"}}

# Tray letters said aloud. ICAO spells two of them Alfa and Juliett so that they are said the same in every language.
NATO = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "Alfa Bravo Charlie Delta Echo Foxtrot Golf Hotel India Juliett Kilo "
                "Lima Mike November Oscar Papa Quebec Romeo Sierra Tango Uniform Victor Whiskey X-ray Yankee Zulu"
                .split()))

# the suffixes a child takes after its parent's name. Nothing else may follow a hyphen.
SUFFIX = {
    "pc": "the station's main computer (the bare call name is the station: a DNS alias for it)",
    "pi": "a Raspberry Pi that isn't a camera", "kvm": "a KVM-over-IP box", "cam": "a camera unit (Pi 5 + its cameras)",
    "air": "an AirGradient ONE (not 'ag', which here is silver)", "ups": "a UPS (its RDU120 card has the name)",
    "sw": "a network switch", "dock": "a dock in a slot or a bay", "plate": "a tray's coupling half (label only)",
    "arm": "a UR12e control box", "base": "a MiR250", "wrist": "a wrist camera", "chiller": "a chiller",
    "vac": "a vacuum pump", "oven": "a test chamber or oven", "prep": "a prep station", "rack": "a rack or magazine",
    "wash": "a wash or clean station", "cure": "a curing unit", "paste": "a stencil printer", "pnp": "a pick-and-place",
    "reflow": "a reflow oven", "quench": "a quench tank", "n2": "a nitrogen generator", "eds": "an EDS analyser",
    "depowder": "a depowdering box", "tipper": "a sieve tipper", "charger": "a robot charger", "exvac":
    "an explosion-proof vacuum cleaner", "back": "a bay's back ceiling camera", "front": "a bay's front ceiling "
    "camera", "top": "a top camera", "left": "a left camera", "bay": "a Shuttle's picking bay", "hood": "a tray hood",
    "store": "a passive store", "1": "", "2": "", "3": "", "tray": "a tray",
    "right": "a right camera", "mast": "a mast camera",     # #374's cameras on the mobile bases: elsie-left/-right/-mast
}


# ===================================================================================================== the inventory
def _source_literal(path: Path, name: str):
    """A module-level literal read from source without importing the module (which would build CAD)."""
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            return node.value
    raise KeyError(name)


def bay_units() -> list[str]:
    node = _source_literal(HERE / "services.py", "BAY_UNITS")
    return [k.value for k in node.keys]


def atom_camera_units() -> list[str]:
    node = _source_literal(HERE / "atom_cams.py", "CAMERAS")
    units = []
    for v in node.values:
        for kw in v.keywords:
            if kw.arg == "unit" and kw.value.value not in units:
                units.append(kw.value.value)
    return units                                   # front, left, and the top pod ("arm" in atom_cams)


TRAY_ITEMS = [   # (text in tray_plan.json's item label, station key or accessory, suffix)
    ("Opentrons OT-2", "ot2", None), ("CubXL", "cubxl", None), ("multi-doser", "doser", None),
    ("vial rack", "doser", "rack"), ("Autotouch", "vacuum_press", None), ("H2D", "h2d", None),
    ("A1 mini", "a1mini", None), ("TM4000", "sem", None), ("MiniFlex", "xrd", None),
    ("Powder prep station", "xrd", "prep"), ("PLX-Benchtop", "pip", None), ("iMicro", "nanoindenter", None),
    ("Mastersizer", "mastersizer", None), ("PX500", "polisher", None), ("disc magazine", "polisher", "rack"),
    ("Nabertherm", "furnace", None), ("water tank", "furnace", "quench"), ("MX400", "mounting_press", None),
    ("N2 glovebox", "glovebox_tray", None), ("VHX", "vhx", None), ("zwickiLine", "tensile_h", None),
    ("HM-220", "hardness", None), ("S2 PUMA", "xrf", None), ("ductless hood", "tray", "hood"),
    ("Carvera", "cnc", None), ("Novastar", "pcb_line", "paste"), ("LumenPnP", "pcb_line", "pnp"),
    ("T-962A", "pcb_line", "reflow"), ("Form Wash", "form4", "wash"), ("Form Cure", "form4", "cure"),
    ("Form 4", "form4", "#"), ("SnowPod", "snowpod", "#"), ("Storage load", "tray", "store"),
    ("powder jars", "tray", "store"),
]


def _row(name, kind, cls, parent, where, what, **kw) -> dict:
    return dict(name=name, kind=kind, cls=cls, parent=parent, where=where, what=what, **kw)


def inventory() -> list[dict]:
    """Every piece of equipment in the model, named. One row per physical unit."""
    plan = json.loads((HERE / "out" / "tray_plan.json").read_text())
    shuttle = {1: STATIONS["vlm"][0], 2: STATIONS["vlm2"][0]}
    rows, seen = [], set()

    def station(key, where):
        if key in seen:
            return
        seen.add(key)
        root, fam, what, who, life, why, src = STATIONS[key]
        rows.append(_row(root, "station", fam, None, where, what, namesake=who, life=life, why=why, source=src,
                         key=key))
        if key not in ("unit1", "unit2", "vlm", "vlm2", "doser", "form4", "snowpod", "pcb_line", "bn_station",
                       "fumehood"):                   # no computer of its own (a hood, a fixture, or a group of units)
            rows.append(_row(f"{root}-pc", "computer", fam, root, where, f"{what}: its computer"))

    for k in ("vlm", "vlm2"):
        n = 1 if k == "vlm" else 2
        station(k, f"floor, Shuttle {n}")
        sh = STATIONS[k][0]
        for u in bay_units():
            rows.append(_row(f"{sh}-bay-{u}", "camera", "camera", sh, f"{sh}, bay ceiling, {u}",
                             f"bay camera unit, ceiling {u} (Pi 5 + HQ + Camera Module 3 Wide)", stream=True))
        rows.append(_row(f"{sh}-bay-dock", "dock", "service", sh, f"{sh}, bay", "the bay's CombiTac dock"))
        rows.append(_row(f"{sh}-vac", "pump", "service", sh, f"{sh}, riser foot", "Pfeiffer HiScroll 12 scroll pump"))
    for k in ("unit1", "unit2"):
        r = STATIONS[k][0]
        station(k, "floor, mobile")
        for suf, what in (("base", "MiR250 (its fleet name)"), ("arm", "UR12e control box"),
                          ("wrist", "Intel RealSense D405 wrist camera")):
            rows.append(_row(f"{r}-{suf}", "robot part", "robot", r, "floor, mobile", what))

    for t, d in plan["trays"].items():
        sh = shuttle[d["shuttle"]]
        loc = f"{sh}, slot {d['slot']}"
        tray = f"tray-{t.lower()}"
        passive = all(it["kind"] == "item" and ("Storage" in it["item"] or "jars" in it["item"]) for it in d["items"])
        rows.append(_row(tray, "tray", "tray", sh, loc, f"tray {t} ({NATO[t]}): {d['role']}", letter=t,
                         spoken=f"tray {NATO[t]}", passive=passive))
        if not passive:
            slot = d["slot"].lower().lstrip("2") if d["shuttle"] == 2 else d["slot"].lower()
            rows.append(_row(f"{sh}-{slot}-dock", "dock", "service", sh, loc, f"slot {d['slot']}'s CombiTac dock"))
        n = {}
        for it in d["items"]:
            lab = it["item"]
            if it["kind"] == "ups":
                rows.append(_row(f"{tray}-ups", "ups", "service", tray, loc, "Vertiv Liebert UPS (RDU120 card)"))
                continue
            if it["kind"] == "monitor":
                rows.append(_row(f"{tray}-air", "sensor", "service", tray, loc, "AirGradient ONE (no display)"))
                continue
            if it["kind"] == "plate":
                rows.append(_row(f"{tray}-plate", "plate", "service", tray, loc, "CombiTac coupling, tray half"))
                rows.append(_row(f"{tray}-sw", "switch", "service", tray, loc, "PoE+ switch"))
                continue
            if it["kind"] == "cam":
                if lab.endswith("head"):
                    i = lab.split()[0].split("_")[1][1:]
                    rows.append(_row(f"{tray}-cam{i}", "camera", "camera", tray, loc,
                                     "stream camera unit (Pi 5 + HQ + Camera Module 3 Wide)", stream=True))
                continue
            if it["kind"] != "item":
                continue
            hit = next(((k, s) for txt, k, s in TRAY_ITEMS if txt in lab), None)
            if hit is None:
                raise KeyError(f"tray {t}: no name for {lab!r} (add it to TRAY_ITEMS)")
            key, suf = hit
            if key == "tray":
                rows.append(_row(f"{tray}-{suf}", suf, "service", tray, loc, lab))
                continue
            station(key, loc)
            root = STATIONS[key][0]
            if suf == "#":
                n[key] = n.get(key, 0) + 1
                rows.append(_row(f"{root}-{n[key]}", "unit", STATIONS[key][1], root, loc, lab))
            elif suf:
                rows.append(_row(f"{root}-{suf}", "unit", STATIONS[key][1], root, loc, lab))
    # the extra units on the trays that tray_plan.json has no box for
    extra = [("sem", "eds", "Oxford AZtecOne EDS analyser"), ("cubxl", "pi", "the CubXL's Raspberry Pi 5"),
             ("vhx", "kvm", "PiKVM V4 Mini"), ("snowpod", "n2", "SnowX NitroPod N2 generator"),
             ("vacuum_press", "vac", "Edwards RV3 rotary-vane pump"), ("glovebox_tray", "vac", "antechamber pump")]
    for key, suf, what in extra:
        rows.append(_row(f"{STATIONS[key][0]}-{suf}", "unit", "station", STATIONS[key][0], "", what))

    floor = plan["floor"]["machines"]
    for key in ("repowder", "sieve_cell", "aconity", "glovebox", "packaging", "instron_floor", "instron_small",
                "fumehood", "ded", "wire_edm", "eos_m400", "meltio_cell"):
        x0, x1, y0, y1 = floor[key]
        station(key, f"floor ({(x0 + x1) / 2000:+.1f}, {(y0 + y1) / 2000:+.1f}) m")
        if key not in ("eos_m400", "meltio_cell"):         # run A's floor AirGradients (round14_a_bom.json)
            rows.append(_row(f"{STATIONS[key][0]}-air", "sensor", "service", STATIONS[key][0], "",
                             "AirGradient ONE (with display)"))
    station("icpms", "floor, south row's east end (planned, notes/icpms.md)")
    station("bn_station", "floor, beside the atomizer (atom_bn_station.py)")
    fa = STATIONS["repowder"][0]
    for u in atom_camera_units():
        u = {"arm": "top"}.get(u, u)
        rows.append(_row(f"{fa}-{u}", "camera", "camera", fa, "on the rePowder", f"DAL PR 189 camera unit, {u}",
                         stream=True))
    rows += [_row(f"{fa}-chiller", "unit", "station", fa, "", "the rePowder's chiller and optimizer"),
             _row(f"{STATIONS['instron_floor'][0]}-oven", "unit", "station", STATIONS["instron_floor"][0], "",
                  "Instron 3119-608 environmental chamber"),
             _row(f"{STATIONS['aconity'][0]}-depowder", "unit", "printer", STATIONS["aconity"][0], "",
                  "depowdering box"),
             _row(f"{STATIONS['sieve_cell'][0]}-tipper", "unit", "station", STATIONS["sieve_cell"][0], "",
                  "sieve tipper"),
             _row(f"{STATIONS['sieve_cell'][0]}-wash", "unit", "station", STATIONS["sieve_cell"][0], "",
                  "sieve wash module"),
             _row("charger-1", "charger", "robot", None, f"floor ({sum(floor['charger0'][:2]) / 2000:+.1f}, "
                  f"{sum(floor['charger0'][2:]) / 2000:+.1f}) m", "MiR Charge 48V"),
             _row("charger-2", "charger", "robot", None, f"floor ({sum(floor['charger1'][:2]) / 2000:+.1f}, "
                  f"{sum(floor['charger1'][2:]) / 2000:+.1f}) m", "MiR Charge 48V"),
             _row("charger-air", "sensor", "service", "charger-1", "", "AirGradient ONE (with display)"),
             _row("exvac-1", "unit", "service", None, "floor", "Nilfisk CFM 118EXP explosion-proof vacuum"),
             _row("util-n2", "unit", "service", None, "floor", "Parker Balston UHPN2-1100 N2 generator"),
             _row("util-chiller", "unit", "service", None, "floor", "Thermo Scientific ThermoFlex 900 chiller")]
    return rows


# ===================================================================================================== asset numbers
def role_key(name: str) -> str:
    """A unit's role key: its name with the station's call name swapped for the station's key in STATIONS. A rename
    keeps the asset number: round 1's lonsdale-pc and round 2's quartz-pc are both xrd-pc."""
    root, sep, rest = name.partition("-")
    key = {v[0]: k for k, v in STATIONS.items()}.get(root)
    return key + sep + rest if key else name


def assign_assets(rows: list[dict]) -> None:
    """VCL-0001 ... in out/naming/asset_ids.json, keyed by role_key: a unit keeps its number through any rename, a new
    unit takes the next free one, and a number is never reused (retired keys stay in the file)."""
    p = OUT / "asset_ids.json"
    ids = json.loads(p.read_text())["ids"] if p.exists() else {}
    nxt = max((int(v.split("-")[1]) for v in ids.values()), default=0) + 1
    for r in rows:
        r["role"] = role_key(r["name"])
        if r["role"] not in ids:
            ids[r["role"]] = f"VCL-{nxt:04d}"
            nxt += 1
        r["asset"] = ids[r["role"]]
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dict(note="Permanent asset numbers, keyed by the unit's role (naming.role_key: the "
                                 "station's key in naming.STATIONS, not its call name, so a rename keeps every "
                                 "number). A number stays with its unit and is never reused; retired keys stay here.",
                                 ids=ids), indent=1) + "\n")


# ===================================================================================================== checks
def ipa(word: str) -> str:
    """espeak-ng's American reading, stress and length marks dropped (the voice's front end)."""
    out = subprocess.run(["espeak-ng", "-q", "-v", "en-us", "--ipa", word], capture_output=True, text=True).stdout
    return re.sub(r"[ˈˌː\s_]", "", out)


def lev(a, b) -> int:
    """Damerau-Levenshtein (adjacent swaps count one) on strings or lists."""
    d = {(i, -1): i + 1 for i in range(-1, len(a))} | {(-1, j): j + 1 for j in range(-1, len(b))}
    for i, j in itertools.product(range(len(a)), range(len(b))):
        c = a[i] != b[j]
        d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + c)
        if i and j and a[i] == b[j - 1] and a[i - 1] == b[j]:
            d[i, j] = min(d[i, j], d[i - 2, j - 2] + c)
    return d[len(a) - 1, len(b) - 1]


def lab_words(min_count: int = 3) -> dict:
    """Words the lab writes and says: the narration and every notes file, with their counts."""
    text = (HERE / "narration.json").read_text() + " ".join(p.read_text() for p in (HERE / "notes").glob("*.md")
                                                            if p.name != "naming.md")     # not this scheme's own
    words = {}
    for w in re.findall(r"[A-Za-z][a-z]{2,}", text):
        words[w.lower()] = words.get(w.lower(), 0) + 1
    return {w: c for w, c in words.items() if c >= min_count}


# people the notes credit (grep of notes/ and docs/, 2026-11-20), first and last names: "take it to Erickson" must
# not be a person and a machine
PEOPLE = ("sterling", "baird", "gage", "erickson", "ronnie", "guymon", "ben", "whitney", "madsen", "william", "borys")
BRANDS = ("opentrons", "bambu", "hitachi", "oxford", "rigaku", "plastometrex", "kla", "malvern", "leco", "nabertherm",
          "keyence", "zwick", "mitutoyo", "bruker", "makera", "opulo", "puhui", "formlabs", "snowx", "amazemet",
          "retsch", "aconity", "inert", "labconco", "insstek", "fanuc", "eos", "meltio", "agilent", "kardex",
          "vertiv", "staubli", "airgradient", "nilfisk", "parker", "thermo", "specac", "edwards", "pfeiffer", "instron",
          "robotiq", "intel", "universal", "mir", "teledyne", "michell", "sentry", "hemco", "olympus", "hamilton",
          "tyler", "gilson", "mettler", "sartorius", "struers", "buehler", "zeiss", "nikon", "leica", "thermofisher")


def check(rows: list[dict]) -> dict:
    """Hard checks (any failure exits 1) and soft ones (reported, a person decides)."""
    from wordfreq import zipf_frequency
    names = [r["name"] for r in rows]
    calls = [r["name"] for r in rows if r["kind"] == "station"]
    spares = [n for v in SPARES.values() for n in v]
    res = dict(hard={}, soft={})
    rfc = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
    res["hard"]["unique"] = sorted({n for n in names if names.count(n) > 1})
    res["hard"]["rfc1123"] = [n for n in names if not rfc.match(n)]                        # a valid DNS label
    res["hard"]["windows_15"] = [n for n in names if n.endswith("-pc") and len(n) > 15]   # NetBIOS name limit
    res["hard"]["length"] = ([n for n in calls if not 4 <= len(n) <= 10] +               # labels, and GitHub's
                             [n for n in names if len(n) > 20])                          # masking of short secrets
    res["hard"]["in_repo_strings"] = [n for n in calls if any(n in s for s in REPO_STRINGS)]
    bad_suffix = []
    for r in rows:
        if r["parent"] and r["kind"] not in ("station", "tray"):
            tail = r["name"].split("-")[-1]
            if tail not in SUFFIX and re.sub(r"\d+$", "", tail) not in SUFFIX:
                bad_suffix.append(r["name"])
    res["hard"]["suffix_list"] = bad_suffix
    streams = [r["name"] for r in rows if r.get("stream")]
    # streamingLambda matches a stream's WORKFLOW_NAME to broadcasts and playlists by substring (docs/stream-cams.md)
    res["hard"]["stream_substring"] = [(a, b) for a, b in itertools.permutations(streams, 2) if a in b]
    res["hard"]["brand"] = [n for n in calls + spares if n in BRANDS]
    # soft: easy to tell apart, said as written, not an everyday word, not a lab word's sound-alike
    pool = calls + spares
    ph = {n: ipa(n) for n in pool}
    close = []
    for a, b in itertools.combinations(pool, 2):
        ds, dp = lev(a, b), lev(list(ph[a]), list(ph[b]))
        sim = 1 - dp / max(len(ph[a]), len(ph[b]))
        if ds <= 2 or sim >= 0.5 or ph[a][:3] == ph[b][:3]:
            close.append(dict(a=a, b=b, spelled=ds, sounds=round(sim, 2), ipa=(ph[a], ph[b]),
                              both_in_use=a in calls and b in calls))
    res["soft"]["close_pairs"] = close
    res["soft"]["everyday_words"] = {n: round(zipf_frequency(n, "en"), 2) for n in pool
                                     if zipf_frequency(n, "en") >= 3.5}
    vocab = lab_words()
    vph = {}
    for w in vocab:
        vph.setdefault(ipa(w), []).append(w)
    res["soft"]["sounds_like_lab_word"] = {n: vph[ph[n]] for n in pool if ph[n] in vph and n not in vph[ph[n]]}
    res["soft"]["lab_word_itself"] = {n: vocab[n] for n in pool if n in vocab}
    pph = {p: ipa(p) for p in PEOPLE}
    res["hard"]["sounds_like_a_person"] = [(n, p) for n in pool for p in PEOPLE
                                           if ph[n] == pph[p] or lev(list(ph[n]), list(pph[p])) <= 1]
    res["ipa"] = ph
    res["ok"] = not any(res["hard"].values())
    return res


# ===================================================================================================== outputs
def registry(rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "registry.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    keys = ["asset", "role", "name", "kind", "cls", "parent", "where", "what", "namesake", "life", "why",
            "source"]
    with open(OUT / "registry.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    md = ["# The vertical lab's equipment names", "",
          "Generated by `python3 naming.py registry` from the model (out/tray_plan.json, out/voltage.json). "
          "notes/naming.md explains the scheme. Asset numbers are permanent (out/naming/asset_ids.json).", "",
          "## Stations, robots and Shuttles", "",
          "| Name | Asset | What | Where | Named for | Why |", "|---|---|---|---|---|---|"]
    for r in rows:
        if r["kind"] == "station":
            md.append(f"| <a id=\"{r['name']}\"></a>**{r['name']}** | {r['asset']} | {r['what']} | {r['where']} | "
                      f"[{r['namesake']}]({r['source']}) ({r['life']}) | {r['why']} |")
    md += ["", "## Everything else", "", "| Name | Asset | Kind | Part of | What | Where |", "|---|---|---|---|---|---|"]
    for r in rows:
        if r["kind"] != "station":
            md.append(f"| {r['name']} | {r['asset']} | {r['kind']} | {r['parent'] or ''} | {r['what']} | "
                      f"{r['where']} |")
    (OUT / "registry.md").write_text("\n".join(md) + "\n")


def main(argv):
    what = argv[1] if len(argv) > 1 else "all"
    rows = inventory()
    assign_assets(rows)
    if what in ("registry", "all"):
        registry(rows)
    res = check(rows)
    (OUT / "checks.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    n_st = sum(r["kind"] == "station" for r in rows)
    print(f"{len(rows)} names, {n_st} stations; hard checks {'pass' if res['ok'] else 'FAIL'}")
    for k, v in res["hard"].items():
        print(f"  {k:18s} {'ok' if not v else v}")
    print(f"  close pairs: {len(res['soft']['close_pairs'])}, everyday words: {res['soft']['everyday_words']}, "
          f"sound-alikes: {res['soft']['sounds_like_lab_word']}, lab words: {res['soft']['lab_word_itself']}")
    if what in ("figures", "all"):
        import naming_figures as NF
        NF.all_figures(rows, res)
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
