"""Names for every piece of equipment in the vertical lab, generated from the model, with checks.

Sterling, PR #318, 2026-11-20: "open another PR focused on clever naming schemes for each piece of equipment".
The write-up is notes/naming.md. Three layers:

1. **A call name for each station**, from a family that says what class of thing it is, and inside the family from
   someone whose own work is the station's job: the XRD is Lonsdale (X-ray crystallography), the SEM Ruska (the first
   electron microscope), the tensile frame Kirkaldy (the first universal testing machine), the doser Lavoisier
   (weighing), the atomizer Faraday (the surface waves ultrasonic atomization breaks into drops). Robots are named
   after robots of history, the Shuttles after the peaks over Provo, printers after printers. The name belongs to the
   role, not the box: a replacement MiniFlex is still Lonsdale.
2. **Everything bolted to a station, a tray, a Shuttle or a robot takes its parent's name and a suffix** from a fixed
   list (SUFFIX): ``lonsdale-pc``, ``tray-d-cam0``, ``timp-bay-front``, ``elsie-arm``. So a hostname says where to look,
   and code can derive one.
3. **A permanent asset number** (VCL-0001 ...) for the physical unit, on its label and in out/naming/asset_ids.json.
   It is never reused, and it doesn't change when a unit moves or its role is renamed.

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
# class -> (family, why this family). The family tells you the class from the name alone.
FAMILIES = {
    "station": ("people whose own work is the station's job", "Say the name and you have a hint of what it does."),
    "printer": ("pioneers of printing", "The polymer printers are printers; the metal ones are named for laser and "
                "powder-bed pioneers, since that is the process."),
    "robot": ("robots of history", "Elsie found her own way back to her hutch to recharge (1949); Freddy assembled "
              "models from a heap of parts by vision (1973). A MiR250 with a UR12e and a wrist camera does both."),
    "shuttle": ("the Wasatch peaks over Provo", "The two tallest things in the lab after round 14's 9.15 m Shuttles."),
}

# station key -> (call name, family, what it is, namesake, life, why the name fits, source). Every namesake is dead:
# a living person's name on a machine is a favour you can't ask for. Women where the fit is as good: Lonsdale,
# Noddack, Blodgett; Lazarenko and Lavoisier are couples.
W = "https://en.wikipedia.org/wiki/"
STATIONS = {
    # ---------------------------------------------------------------- tray A
    "ot2": ("pasteur", "station", "Opentrons OT-2 liquid handler", "Louis Pasteur", "1822-1895",
            "the Pasteur pipette is named for him; the OT-2 is the lab's pipette", W + "Pasteur_pipette"),
    "cubxl": ("tafel", "station", "CubXL corrosion cell with its EZstat Pro potentiostat", "Julius Tafel", "1862-1918",
              "the Tafel equation (1905); the CubXL's polarization scans are read as Tafel slopes", W + "Julius_Tafel"),
    # ---------------------------------------------------------------- tray B
    "doser": ("lavoisier", "station", "multi-doser (chain carousel v5) on an A&D HR-202i", "Antoine and Marie-Anne "
              "Paulze Lavoisier", "1743-1794, 1758-1836", "chemistry by the balance: mass in, mass out, and she "
              "drew and translated the work", W + "Antoine_Lavoisier"),
    "vacuum_press": ("bridgman", "station", "Specac Atlas Autotouch 15T vacuum press", "Percy W. Bridgman", "1882-1961",
                     "high-pressure physics, Nobel 1946", W + "Percy_Williams_Bridgman"),
    # ---------------------------------------------------------------- tray C
    "h2d": ("gutenberg", "printer", "Bambu Lab H2D", "Johannes Gutenberg", "c. 1400-1468",
            "the movable-type press", W + "Johannes_Gutenberg"),
    "a1mini": ("aldus", "printer", "Bambu Lab A1 mini", "Aldus Manutius", "c. 1450-1515",
               "the Aldine Press: italic type and the small, portable octavo book; the H2D's small partner",
               W + "Aldus_Manutius"),
    # ---------------------------------------------------------------- tray D
    "sem": ("ruska", "station", "Hitachi TM4000PlusII SEM with Oxford AZtecOne EDS", "Ernst Ruska", "1906-1988",
            "built the first electron microscope (1931-33), Nobel 1986", W + "Ernst_Ruska"),
    "xrd": ("lonsdale", "station", "Rigaku MiniFlex XRD", "Kathleen Lonsdale", "1903-1971",
            "X-ray crystallographer; showed by X-ray diffraction that the benzene ring is flat (1929); one of the "
            "first two women elected FRS (1945)", W + "Kathleen_Lonsdale"),
    # ---------------------------------------------------------------- tray E
    "pip": ("tabor", "station", "Plastometrex PLX-Benchtop (indentation plastometry)", "David Tabor", "1913-2005",
            "The Hardness of Metals (1951): indentation hardness as about three times the flow stress, at a "
            "representative strain; plastometry turns an indent into a stress-strain curve", W + "David_Tabor"),
    "nanoindenter": ("sneddon", "station", "KLA iMicro nanoindenter", "Ian Sneddon", "1919-2000",
                     "the elastic contact solution for a punch of any profile (1965) that nanoindentation's "
                     "unloading analysis rests on", W + "Ian_Sneddon"),
    "mastersizer": ("tyndall", "station", "Malvern Mastersizer 3000 with Aero S (laser diffraction)", "John Tyndall",
                    "1820-1893", "the Tyndall effect: light scattered by particles", W + "Tyndall_effect"),
    # ---------------------------------------------------------------- tray F
    "polisher": ("beilby", "station", "LECO PX500 grinder-polisher with its disc magazine", "George Beilby",
                 "1850-1924", "the Beilby layer, the flowed skin polishing leaves on a metal", W + "George_Beilby"),
    "furnace": ("wilm", "station", "Nabertherm NAT 15/65 furnace with the quench tank", "Alfred Wilm", "1869-1937",
                "found age hardening in aluminium alloys (1906); the furnace does the bars' T6", W + "Alfred_Wilm"),
    "mounting_press": ("baekeland", "station", "LECO MX400 hot mounting press", "Leo Baekeland", "1863-1944",
                       "Bakelite, the phenolic of a hot-mounted puck", W + "Leo_Baekeland"),
    # ---------------------------------------------------------------- tray K
    "glovebox_tray": ("schlenk", "station", "the tray's N2 glovebox (ours)", "Wilhelm Schlenk", "1879-1943",
                      "the Schlenk line: handling air-sensitive material", W + "Wilhelm_Schlenk"),
    "vhx": ("sorby", "station", "Keyence VHX-7000 digital microscope with EA-300 LIBS", "Henry Clifton Sorby",
            "1826-1908", "first to look at polished, etched steel under a microscope (1863): metallography",
            W + "Henry_Clifton_Sorby"),
    # ---------------------------------------------------------------- tray L
    "tensile_h": ("petch", "station", "ZwickRoell zwickiLine Z5.0 TN (horizontal tensile)", "Norman Petch",
                  "1917-1992", "the Hall-Petch relation: yield strength from grain size, read off tensile tests",
                  W + "Hall%E2%80%93Petch_relation"),
    "hardness": ("sandland", "station", "Mitutoyo HM-220 micro-Vickers tester", "George E. Sandland", "1920s",
                 "devised the Vickers test with Robert L. Smith at Vickers Ltd (1921)", W + "Vickers_hardness_test"),
    # ---------------------------------------------------------------- tray M
    "xrf": ("noddack", "station", "Bruker S2 PUMA XRF with XY autochanger", "Ida Noddack", "1896-1978",
            "found rhenium (1925) by its X-ray spectrum, which is what an XRF reads", W + "Ida_Noddack"),
    "cnc": ("maudslay", "station", "Makera Carvera CNC mill", "Henry Maudslay", "1771-1831",
            "the screw-cutting lathe and the machine-tool trade", W + "Henry_Maudslay"),
    # ---------------------------------------------------------------- tray H
    "pcb_line": ("eisler", "station", "PCB line: DDM stencil printer, Opulo LumenPnP, Puhui reflow oven",
                 "Paul Eisler", "1907-1992", "invented the printed circuit board", W + "Paul_Eisler"),
    # ---------------------------------------------------------------- tray G
    "form4": ("senefelder", "printer", "Formlabs Form 4 resin printers with Form Wash and Form Cure",
              "Alois Senefelder", "1771-1834", "invented lithography (1796), which stereolithography is named from",
              W + "Alois_Senefelder"),
    # ---------------------------------------------------------------- tray I
    "snowpod": ("maiman", "printer", "SnowX SnowPod desktop LPBF printers with the NitroPod",
                "Theodore Maiman", "1927-2007", "the first working laser (1960): a small laser for small printers",
                W + "Theodore_Maiman"),
    # ---------------------------------------------------------------- floor
    "repowder": ("faraday", "station", "AMAZEMET rePowder ultrasonic atomizer", "Michael Faraday", "1791-1867",
                 "Faraday waves (1831): the surface waves on a vibrated liquid that ultrasonic atomization breaks "
                 "into drops", W + "Faraday_wave"),
    "sieve_cell": ("agricola", "station", "sieving cell: Retsch AS 200, tipper and wash module", "Georgius Agricola",
                   "1494-1555", "De re metallica (1556), whose woodcuts show ore sieved and screened by size",
                   W + "Georgius_Agricola"),
    "aconity": ("deckard", "printer", "Aconity MIDI+ LPBF printer and the depowdering box", "Carl Deckard",
                "1961-2019", "invented selective laser sintering: the powder bed and the laser", W + "Carl_Deckard"),
    "glovebox": ("ramsay", "station", "Inert PureLab HE glovebox", "William Ramsay", "1852-1916",
                 "found argon (with Rayleigh, 1894) and the other noble gases", W + "William_Ramsay"),
    "packaging": ("mclean", "station", "packaging station: sealer, label printers, foam inserts", "Malcom McLean",
                  "1913-2001", "the shipping container", W + "Malcom_McLean"),
    "instron_floor": ("kirkaldy", "station", "Instron 68FM-100 with its 3119-608 chamber", "David Kirkaldy",
                      "1820-1897", "built the first universal testing machine and ran the first testing works "
                      "(London, 1866): 'Facts not Opinions'", W + "David_Kirkaldy"),
    "instron_small": ("galileo", "station", "Instron 68SC-2 table frame", "Galileo Galilei", "1564-1642",
                      "Two New Sciences (1638) began the strength of materials with a bar pulled in tension",
                      W + "Two_New_Sciences"),
    "fumehood": ("davy", "station", "Labconco Protector XStream ducted fume hood", "Humphry Davy", "1778-1829",
                 "the safety lamp (1815): working safely in bad air", W + "Davy_lamp"),
    "ded": ("gibbs", "printer", "InssTek MX-Lab DED (blends compositions in the melt pool)", "J. Willard Gibbs",
            "1839-1903", "the phase rule and free energy, the thermodynamics behind screening alloy compositions",
            W + "Josiah_Willard_Gibbs"),
    "wire_edm": ("lazarenko", "station", "FANUC ROBOCUT wire EDM", "Boris and Natalya Lazarenko", "1910-1979, "
                 "1911-1979", "invented electrical discharge machining (1943)", W + "Electrical_discharge_machining"),
    "eos_m400": ("javan", "printer", "EOS M 400-4 (scale-up)", "Ali Javan", "1926-2016",
                 "the first gas laser (helium-neon, 1960)", W + "Ali_Javan"),
    "meltio_cell": ("brunel", "station", "Meltio robot cell (propeller repair)", "Isambard Kingdom Brunel",
                    "1806-1859", "the SS Great Britain (1843), the first iron, screw-propelled ocean liner",
                    W + "SS_Great_Britain"),
    "icpms": ("aston", "station", "Agilent 7850 ICP-MS with SPS 4, in its own trace-metals hood", "Francis Aston",
              "1877-1945", "the mass spectrograph and isotopes, Nobel 1922", W + "Francis_William_Aston"),
    "bn_station": ("blodgett", "station", "the atomizer's BN coating station (ours)", "Katharine Burr Blodgett",
                   "1898-1979", "thin coatings (Langmuir-Blodgett films, non-reflective glass)",
                   W + "Katharine_Burr_Blodgett"),
    # ---------------------------------------------------------------- robots and Shuttles
    "unit1": ("elsie", "robot", "MiR250 + UR12e + Robotiq 2F-85 + RealSense D405, unit 1", "W. Grey Walter's Elsie",
              "1949", "a robot tortoise that found its way back to its hutch to recharge",
              W + "William_Grey_Walter"),
    "unit2": ("freddy", "robot", "MiR250 + UR12e + Robotiq 2F-85 + RealSense D405, unit 2", "Edinburgh's Freddy",
              "1969-1976", "a hand-eye robot that assembled models from a heap of parts by vision", W + "Freddy_II"),
    "vlm": ("timp", "shuttle", "Kardex Shuttle XP 500, 9.15 m, Shuttle 1", "Mount Timpanogos", "3,582 m",
            "the peak over Provo; locals call it Timp", W + "Mount_Timpanogos"),
    "vlm2": ("nebo", "shuttle", "Kardex Shuttle XP 500, 9.15 m, Shuttle 2", "Mount Nebo", "3,636 m",
             "the highest peak of the Wasatch, south of Provo", W + "Mount_Nebo_(Utah)"),
}
# spare names, checked like the rest, for the next unit of a family (the three-each plan, a third robot, Shuttle 3)
# (dropped by the checks: caxton, too like aston; rammler, like ramsay; tresca, like ruska; ayrton, like aston;
# shakey, like davy and beilby; ericsson, like Gage Erickson)
SPARES = {
    "robot": ["unimate", "genghis"],
    "shuttle": ["cascade", "lonepeak"],
    "station": ["moseley", "bragg", "pourbaix", "kibble"],
    "printer": ["bodoni", "schawlow"],
}

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
        if key not in ("unit1", "unit2", "vlm", "vlm2", "doser", "form4", "snowpod", "pcb_line", "bn_station"):
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
             _row(f"{STATIONS['instron_floor'][0]}-oven", "unit", "station", "kirkaldy", "",
                  "Instron 3119-608 environmental chamber"),
             _row(f"{STATIONS['aconity'][0]}-depowder", "unit", "printer", "deckard", "", "depowdering box"),
             _row(f"{STATIONS['sieve_cell'][0]}-tipper", "unit", "station", "agricola", "", "sieve tipper"),
             _row(f"{STATIONS['sieve_cell'][0]}-wash", "unit", "station", "agricola", "", "sieve wash module"),
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
def assign_assets(rows: list[dict]) -> None:
    """VCL-0001 ... in out/naming/asset_ids.json: a name keeps its number, a new name takes the next free one, and a
    number is never reused (retired names stay in the file)."""
    p = OUT / "asset_ids.json"
    ids = json.loads(p.read_text())["ids"] if p.exists() else {}
    nxt = max((int(v.split("-")[1]) for v in ids.values()), default=0) + 1
    for r in rows:
        if r["name"] not in ids:
            ids[r["name"]] = f"VCL-{nxt:04d}"
            nxt += 1
        r["asset"] = ids[r["name"]]
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dict(note="Permanent asset numbers: a number stays with its unit and is never reused. "
                                 "Retired names stay here.", ids=ids), indent=1) + "\n")


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
    text = (HERE / "narration.json").read_text() + " ".join(p.read_text() for p in (HERE / "notes").glob("*.md"))
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
    res["soft"]["lab_word_itself"] = {n: vocab[n] for n in pool if n in vocab and n not in ("faraday",)}
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
    keys = ["asset", "name", "kind", "cls", "parent", "where", "what", "namesake", "life", "why", "source"]
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
