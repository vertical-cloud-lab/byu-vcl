"""Capital and running costs of the two ways to run the campaigns, and the cost of an experiment on each.

    python3 -m twin.econ                      # each lab's capex and annual cost, printed
    python3 -m twin.econ all                  # figures, out/twin2/econ/econ_summary.json, notes/twin_econ.md results
    python3 -m twin.econ notes                # re-render the notes' results block from econ_summary.json
    python3 -m twin.econ report [runs.jsonl]  # cost per experiment of every run in a benchmark file, printed

Two facilities, matching ``twin.facility``:

* ``vertical_lab`` (PR 318's automated lab): two Kardex Shuttle XP 500 at 9.15 m, two MiR250 + UR12e units and a
  third for the floor, the rePowder, an Aconity MIDI, an MX-Lab, a wire EDM, furnaces, the Instron 68FM-100 with its
  3119-608 chamber and the zwickiLine, the tray instruments (SEM/EDS/EBSD, XRD, XRF, laser diffraction, micro-Vickers,
  nanoindenter, PIP, VHX + LIBS, polisher and mounting press, CubXL, OT-2), the ICP-MS station, the doser and press,
  the sieve cell, the glovebox, hoods, UPSs, couplings, cameras and the fit-out. One person on the day shift (the
  atomizer's crucible and upkeep, ``upkeep.py``: about 31 h a week) and a quarter of a research engineer for the
  robots' programs and repairs.
* ``conventional`` (``proposed`` in the twin): the proposals' own lab, which owns the atomizer, the sieve shaker, the
  doser and a press, a furnace, the CubXL and the glovebox, and rents everything else from BYU's core facilities and
  the partners at their rates (the twin's station fees, ``twin.facility.PROPOSED``). Graduate students do the hands-on
  work (``HANDS_ON``).

Every price says where it comes from: a procurement record or list price (with its URL; most were collected for the
$200M facility budget, ``facility/costs_and_sizes.md`` at commit aa41d0d, and the lab's notes), or ``estimate`` /
``assumed`` (ours). ``notes/twin_econ.md`` has the method and the limits.

Accounting (``allocate``): each item's annual fixed cost (straight-line depreciation, or a capital-recovery annuity
with ``discount``; its service contract; its electricity at an assumed duty; its floor space) is assigned to the twin
station(s) it serves. A station's fixed cost is recovered over its busy hours: a campaign pays
``F_s * B_cs / max(B_s, u * A_s)``, where ``B_cs`` is its hours on the station, ``B_s`` everyone's, ``A_s`` the
station's available hours on its calendar and ``u`` an assumed utilization (``utilization=None``: the campaigns are
the only users and absorb the whole cost). Shared infrastructure (Shuttles, units, cameras, UPSs, the fit-out, the open
floor, the fixed staff) and the stations no campaign used are overhead, spread in proportion to the direct fixed cost
each campaign absorbed. Labour that scales with the work (the conventional lab's hands-on hours) and the twin's own
ledger (feedstock and consumables bought, station fees) are added per campaign.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
H_YEAR = 8760.0
CSZ = "facility/costs_and_sizes.md (aa41d0d)"

# ------------------------------------------------------------------------------------------------------- rates
RATES = {
    # electricity, Utah commercial customers, Jan-Sep 2026 (EIA Electric Power Monthly, table 5.6.B)
    "kwh_usd": (0.104, "EIA Electric Power Monthly table 5.6.B, Utah commercial, Jan-Sep 2026: 10.40 c/kWh "
                       "(https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_b)"),
    # floor space: O&M of lab space (utilities, custodial, maintenance, renewal), and the building's own depreciation
    "space_om_usd_m2_yr": (215.0, "assumed $20/ft2/yr: EAB (Gordian 2025 data) puts a research lab's 50-year cost of "
                                  "ownership at $2.3M per 1,000 ft2, $46/ft2/yr, of which the building's own "
                                  "depreciation (below) is about $21 "
                                  "(https://eab.com/wp-content/uploads/2025/09/PDF-EAB-Research-True-Costs-of-Space-IG.pdf)"),
    "space_capex_usd_m2_yr": (222.0, "the $200M plan's high-bay building at $700-1,100/ft2 (published comps in "
                                     + CSZ + "), $825/ft2 over BYU's 40-year building life "
                                     "(https://finserve.byu.edu/asset-capitalization-procedures)"),
}

# fully loaded annual cost of a person (salary or stipend + tuition + fringe); hourly = annual / productive hours
FRINGE = (0.35, "assumed: BYU's negotiated staff fringe rate was not found (its rate agreement is a scanned PDF)")
PEOPLE = {
    "grad_student": dict(annual=31_500.0 + 8_936.0, hours=1500.0,
                         src="BYU Chemistry PhD stipend 2026-27 $31,500 "
                             "(https://gradprogram.chem.byu.edu/graduate-program/frequently-asked-questions) plus "
                             "two semesters of graduate tuition, $4,468 each for Latter-day Saint students "
                             "(https://catalog.byu.edu/policy/tuition-and-fees); BYU charges no fringe on student "
                             "wages (Sponsored Programs Handbook); 1,500 research hours a year assumed"),
    "technician": dict(annual=64_040.0 * 1.35, hours=1800.0,
                       src="BLS OEWS May 2025, engineering technologists (17-3029), Provo-Orem-Lehi, mean $64,040 "
                           "(series OEUM003934000000017302904), plus 35 % fringe (assumed)"),
    "research_engineer": dict(annual=105_770.0 * 1.35, hours=1800.0,
                              src="BLS OEWS May 2025, mechanical engineers (17-2141), Provo-Orem-Lehi, mean $105,770 "
                                  "(series OEUM003934000000017214104), plus 35 % fringe (assumed)"),
    "staff_scientist": dict(annual=100_130.0 * 1.35, hours=1800.0,
                            src="BLS OEWS May 2025, materials engineers (17-2131), Utah, mean $100,130 "
                                "(series OEUS490000000000017213104), plus 35 % fringe (assumed)"),
}
PRODUCTIVE_H = (1800.0, "assumed: 2,080 paid hours less leave and training")


def hourly(role: str) -> float:
    p = PEOPLE[role]
    return p["annual"] / p["hours"]


# fixed staff of each facility: (role, FTE, why)
STAFF = {
    "vertical_lab": [("technician", 1.0, "one person on the weekday day shift: the atomizer's crucible and upkeep "
                                         "(upkeep.py: 31 h a week of tasks after the ramp, 13 of them the crucible)"),
                     ("research_engineer", 0.25, "robot programs, recovery and repairs (assumed)")],
    "conventional": [("technician", 0.10, "upkeep of the lab's own atomizer, glovebox and furnace (assumed)")],
}


# ------------------------------------------------------------------------------------------------------- equipment
@dataclass(frozen=True)
class Item:
    key: str
    name: str
    qty: int
    price: float                  # each, USD, delivered (installed where the source says so)
    src: str                      # URL or 'estimate' / 'assumed', with a word on what it is
    life: float = 10.0            # years
    service: float = 0.08         # annual service contract as a fraction of the price
    service_src: str = "assumed"
    kw: float = 0.0               # average draw while powered, kW each
    duty: float = 0.3             # share of the year powered at that draw
    area: float = 0.0             # floor area each, m^2 (tray instruments: 0, they ride in the Shuttles)
    stations: dict = field(default_factory=dict)   # twin station -> share of this item's cost
    kind: str = "estimate"        # 'procurement' | 'list' | 'estimate' | 'assumed' | 'owned'

    @property
    def capex(self) -> float:
        return self.qty * self.price


SVC_A = ("8-15 % of the purchase price a year for full service (Lab Manager, "
         "https://www.labmanager.com/optimize-instrument-service-contracts-based-on-risk-costs-and-criticality-35207); "
         "about 10 % for electron microscopes (Univ. of Florida, "
         "https://mtl.mit.edu/pipermail/labnetwork/attachments/20240208/bb294d65/attachment.html)")
SVC_LOW = "assumed: 3 % a year (few moving parts)"
SVC_ROBOT = "assumed: 5 % a year"
UA = "https://www.usaspending.gov/award/"          # federal award records (read through the USAspending API)
LIFE_SRC = ("BYU capitalizes equipment over 3-10 years and buildings over 40 "
            "(https://finserve.byu.edu/asset-capitalization-procedures); Dartmouth uses 7 for scientific equipment "
            "(http://www.dartmouth.edu/finance/purchasing/ppe/useful_life_schedule.php)")


def _vertical() -> list[Item]:
    I = Item
    return [
        # infrastructure (overhead)
        I("shuttle", "Kardex Shuttle XP 500, 9.15 m (30 ft), 2450 x 864 mm trays", 2, 210_000.0,
          "https://www.kardex.com/en-us/blog/how-much-does-a-vertical-lift-module-cost ($6-8k per vertical foot); "
          "federal orders for 4.85-5.85 m XP 500s $103-108k (2018-19) in " + CSZ, life=15, service=0.03,
          service_src="assumed: 3 % (Kardex service visits twice a year, upkeep.py)", kw=6.8, duty=0.15, area=8.5,
          kind="list"),
        I("units", "MiR250 + UR12e + Robotiq 2F-85 mobile manipulator, with cabinet, cameras, Class D unit, "
                   "integration", 2, 140_000.0,
          "MiR250 $59-65k (US distributors, 2026), UR12e about $45k (Vention list), 2F-85 $5-6k, plus ours: "
          + CSZ + " and the $200M plan's $120-160k", life=7, service=0.05, service_src=SVC_ROBOT, kw=0.35, duty=0.7,
          area=1.2, kind="list"),
        I("floor_unit", "Third MiR250 unit for the floor, with a Nilfisk CFM 118EXP explosion-proof vacuum "
                        "(notes/floor_cleaning.md)", 1, 155_000.0,
          "estimate: a unit as above plus an explosion-proof vacuum and hose reel", life=7, service=0.05,
          service_src=SVC_ROBOT, kw=0.6, duty=0.15, area=1.2),
        I("glovebox", "Inert PureLab HE glovebox with purifier, O2 and dew-point sensors", 1, 55_000.0,
          "National Archives, Inert PureLab HE 1250 with extension, stand, installation and training, $54,848 (2023) "
          + UA + "CONT_AWD_88310323P00054_8800_-NONE-_-NONE-", life=10, service=0.04, kw=1.2, duty=0.5, area=2.0,
          kind="procurement"),
        I("hoods", "Ducted 6 ft fume hoods, installed", 2, 35_000.0,
          "estimate: $8-57k for a 6 ft hood before installation "
          "(https://www.onepointesolutions.com/blog/how-much-does-a-fume-hood-cost/)", life=20, service=0.02,
          kw=0.3, duty=1.0, area=1.5),
        I("ups", "UPSs on the powered trays (six PSI5-800, five GXT5LI-1500, one GXT5LI-3000; notes/ups.md)", 1,
          22_000.0, "GXT5LI-1500 $2,707 at CDW (notes/ups.md); the rest estimated", life=8, service=0.02,
          kw=0.25, duty=1.0),
        I("couplings", "CombiTac docks and tray plates on 12 powered trays and 2 bays (notes/coupling.md)", 14,
          4_000.0, "estimate", life=10, service=0.02),
        I("cameras", "Tray, bay and security cameras with their Pi 5s and switches (notes/security_cameras.md, "
                     "notes/base_cameras.md)", 1, 18_900.0,
          "notes/security_cameras.md ($17,300 NDAA-compliant) + notes/base_cameras.md (two bases, $1,600)",
          life=5, service=0.0, kw=0.6, duty=1.0, kind="list"),
        I("services", "Fit-out: argon and N2 lines, a Parker Balston N2 generator, chillers, power distribution, "
                      "dust collection and explosion protection, network and data store", 1, 450_000.0,
          "estimate (the $200M plan prices the same services at $8-14M for 34 Shuttles, " + CSZ + ")", life=20,
          service=0.02, kw=4.0, duty=1.0),
        # the atomizer and the floor machines
        I("repowder", "AMAZEMET rePowder ultrasonic atomizer, with its optimizer and chiller", 1, 350_000.0,
          "NASA MSFC $286,720 (2023) " + UA + "CONT_AWD_80MSFC24PA004_8000_-NONE-_-NONE- ; "
          "NIST $321,595 (2024); Hochschule Aalen EUR 407,700 (2025) (" + CSZ + ")", service=0.08,
          kw=12.0, duty=0.25, area=2.5, stations={"atomizer": 1.0}, kind="procurement"),
        I("midi", "Aconity3D AconityMIDI+ laser powder-bed fusion", 1, 700_000.0,
          "EU awards EUR 350-456k (2019-22), Forschungszentrum Juelich EUR 675,390 (2026) "
          "https://ted.europa.eu/en/notice/-/detail/689139-2026 (" + CSZ + ")", service=0.10,
          service_src="assumed: 10 % (lasers, optics, gas loop)", kw=10.0, duty=0.4, area=3.0,
          stations={"utah_midi": 1.0}, kind="procurement"),
        I("mxlab", "InssTek MX-Lab blown-powder DED", 1, 300_000.0,
          "InssTek awards: CNRS EUR 200,000 (2024) https://ted.europa.eu/en/notice/-/detail/137843-2024 , Wuppertal "
          "'Mini-DED' EUR 241,550 (2025) https://ted.europa.eu/en/notice/-/detail/76406-2025 , Chalmers SEK 3.6M "
          "(2024) https://ted.europa.eu/en/notice/-/detail/564443-2024 ; plus shipping and installation (estimate)",
          service=0.10, service_src="assumed: 10 %", kw=4.4, duty=0.3, area=2.5, stations={"utah_mxlab": 1.0},
          kind="procurement"),
        I("edm", "FANUC ROBOCUT wire EDM", 1, 230_000.0,
          "NASA FANUC C600iC-ADV $220,362 (2026) " + UA + "CONT_AWD_80NSSC27P0128_8000_-NONE-_-NONE- ;"
          " $200-302k awards 2020-26 (" + CSZ + ")", service=0.05, kw=7.5, duty=0.3, area=5.0,
          stations={"edm": 1.0}, kind="procurement"),
        I("instron", "Instron 68FM-100 floor frame with grips and extensometer", 1, 175_000.0,
          "USAF $145,607 (2022), NASA $161,830 (2023), Navy $207,865 (2024) "
          + UA + "CONT_AWD_80NSSC23PA554_8000_-NONE-_-NONE- (" + CSZ + ")",
          service=0.06, kw=3.0, duty=0.3, area=1.5, stations={"tensile": 0.5, "tensile_hot": 0.5},
          kind="procurement"),
        I("chamber", "Instron 3119-608 environmental chamber (to 600 C)", 1, 50_000.0,
          "estimate: $40-60k in the $200M plan", service=0.05, kw=3.0, duty=0.2, stations={"tensile_hot": 1.0}),
        I("zwick", "ZwickRoell zwickiLine Z5.0 TN with testControl II", 1, 35_000.0,
          "assumed: no public price or award found (quote only)", service=0.05, kw=0.5, duty=0.3,
          stations={"tensile": 1.0}, kind="assumed"),
        I("machining", "Machining cell (PR 373): lathe, pedestal UR10e, wash and accumulator (notes/machining.md)", 1,
          275_000.0, "notes/machining.md: capital about $230-320k", service=0.05, kw=5.0, duty=0.3, area=6.0,
          stations={"shop": 1.0}),
        I("icpms", "Agilent 7850 ICP-MS with SPS 4, chiller, trace-metals hood, hot block and dilutor "
                   "(notes/icpms.md)", 1, 260_000.0,
          "7850 $160-220k (LabX 2026 buyer's guide, notes/icpms.md); SPS 4 $12,305 list (Agilent quote in a 2017 "
          "West Virginia bid file); hood, dilutor and hot block estimated at $50k", service=0.10,
          service_src="assumed: 10 % (cones, pumps, plasma)", kw=4.5, duty=0.3, area=3.0,
          stations={"byu_icpms": 1.0}, kind="list"),
        I("sieve_cell", "Sieve cell: Retsch AS 200, tipper, wash module, downdraft enclosure", 1, 60_000.0,
          "AS 200 about $6.7k each with sieves (USAF, three for $19,968, 2022) " + UA +
          "CONT_AWD_FA860122P0079_9700_-NONE-_-NONE- ; the rest estimated ($40-80k in the $200M plan)",
          service=0.04, kw=1.0, duty=0.3, area=2.0, stations={"sieve": 1.0}),
        I("furnaces", "Nabertherm NAT 15/65 forced-convection furnaces (tray F)", 2, 20_000.0,
          "estimate; a Carbolite chamber furnace cost NASA $23,521 (2022) " + UA +
          "CONT_AWD_80NSSC22PB945_8000_-NONE-_-NONE-", service=0.03, kw=2.8, duty=0.3, stations={"furnace": 1.0}),
        # tray instruments
        I("sem", "Hitachi TM4000PlusII benchtop SEM", 1, 100_000.0,
          "USDA-ARS $98,900 with set-up and training (2021) " + UA + "CONT_AWD_12905B21P0255_12H2_-NONE-_-NONE- (" +
          CSZ + ")", service=0.10, service_src=SVC_A, kw=0.7, duty=0.5, stations={"byu_sem": 1.0},
          kind="procurement"),
        I("eds", "Oxford Instruments AZtecOne EDS for the TM4000", 1, 55_000.0,
          "Oxford EDS detector: USGS $49,995 (2025) " + UA + "CONT_AWD_140G0325P0065_1434_-NONE-_-NONE- ; "
          "USAF $57,990 (2021)", service=0.10, service_src=SVC_A, kw=0.4, duty=0.5, stations={"byu_sem": 1.0},
          kind="procurement"),
        I("ebsd", "EBSD detector on the SEM (assumed in the lab's plan)", 1, 120_000.0,
          "Oxford Symmetry S2: Army $87,430 (2021) " + UA + "CONT_AWD_W31P4Q21P0012_9700_-NONE-_-NONE- ; an "
          "Oxford EBSD added to AZtec $156,400 (2021)", service=0.10, service_src=SVC_A, kw=0.2, duty=0.3,
          stations={"byu_sem": 1.0}, kind="procurement"),
        I("xrd", "Rigaku MiniFlex 600-C benchtop XRD with prep station", 1, 105_000.0,
          "NASA $99,465 (2023), USDA-ARS $99,444 (2024), EPA $119,968 (2020) "
          + UA + "CONT_AWD_80NSSC23PB731_8000_-NONE-_-NONE- (" + CSZ + ")", service=0.10, service_src=SVC_A,
          kw=1.8, duty=0.3, stations={"xrd": 1.0}, kind="procurement"),
        I("xrf", "Bruker S2 PUMA Series 2 EDXRF with XY autochanger", 1, 120_000.0,
          "Univ. Copenhagen S2 PUMA EUR 115,000 (2019) https://ted.europa.eu/en/notice/-/detail/308367-2019 ; "
          "benchtop EDXRF: Rigaku NEX CG $93,565 (2020), Malvern Epsilon 4 $144,163 (2022)", service=0.10,
          service_src=SVC_A, kw=0.9, duty=0.3, stations={"xrf": 1.0}, kind="procurement"),
        I("mastersizer", "Malvern Mastersizer 3000 with Aero S", 1, 110_000.0,
          "Mastersizer 3000 awards $68-140k (2021-26), e.g. DLA $107,798 (2023) " + UA +
          "CONT_AWD_SPE8EL23F16XT_9700_SPE8EJ21D0020_9700 ; none names the Aero S", service=0.08,
          service_src="Mastersizer 3000 one-year agreements $5,550-12,375 (USDA 2020-21), 4-13 % of the price",
          kw=1.55, duty=0.3, stations={"psd": 1.0}, kind="procurement"),
        I("hardness", "Mitutoyo HM-220 micro-Vickers with AVPAK", 1, 70_000.0,
          "HM-220 Type B $58,385 list, PC not included "
          "(https://penntoolco.com/mitutoyo-pc-driven-micro-vickers-hardness-tester-hm-220-type-b-64aab325p); "
          "Type D's automation and the PC estimated", service=0.05, kw=0.24, duty=0.3, stations={"hardness": 1.0},
          kind="list"),
        I("nanoindenter", "KLA iMicro nanoindenter", 1, 250_000.0,
          "Navy, iMicro with iQwave2, $248,751 (2025) " + UA + "CONT_AWD_N0017325P0430_9700_-NONE-_-NONE-",
          service=0.10, service_src=SVC_A, kw=0.3, duty=0.3, stations={"nanoindent": 1.0}, kind="procurement"),
        I("pip", "Plastometrex PLX-Benchtop (indentation plastometry)", 1, 130_000.0,
          "NASA $127,500 (2025) " + UA + "CONT_AWD_80NSSC25PB546_8000_-NONE-_-NONE- ; Navy $160,187 (2025)",
          service=0.08, kw=0.2, duty=0.3, stations={"pip": 1.0}, kind="procurement"),
        I("vhx", "Keyence VHX-7000 with VHX-S750E stand and EA-300 LIBS head", 1, 190_000.0,
          "VHX-7000 $67-118k (federal awards 2020-23, e.g. USDA $118,385 " + UA +
          "CONT_AWD_12405B23F0240_12H2_GS07F5934R_4730 ); an EA-300-class LIBS head added to a VHX-7000 at Warsaw, "
          "PLN 385,012 (about $95k, 2025) https://ted.europa.eu/en/notice/-/detail/68926-2025", service=0.05,
          kw=0.56, duty=0.3, stations={"density": 1.0}, kind="procurement"),
        I("polish", "LECO PX500 grinder/polisher, MX400 mounting press, sectioning saw", 1, 55_000.0,
          "PX500A2 $22,904 (Navy 2021) " + UA + "CONT_AWD_N0016421PJ124_9700_-NONE-_-NONE- ; a mounting press "
          "$15.9-22.6k (Buehler SimpliMet 4000, DLA 2024; Struers, Army 2025); the saw estimated", service=0.05,
          kw=1.9, duty=0.3, stations={"prep": 1.0}, kind="procurement"),
        I("carvera", "Makera Carvera desktop CNC (tray M)", 1, 5_799.0,
          "list $5,799 (https://www.makera.com/products/carvera.json)", service=0.03, kw=0.4, duty=0.2,
          stations={"shop": 1.0}, kind="list"),
        I("cubxl", "CubXL gantry, NuVant EZstat Pro potentiostat, Opentrons OT-2 with P20 and P300, vials", 1,
          35_000.0, "estimate: OT-2 GEN2 P300 $2,950 (opentrons.com, notes/cubxl_pipettes.md); a Gamry Interface "
          "1010E cost the Navy $29,505 (2021); the EZstat Pro is quote only", service=0.03, kw=0.6, duty=0.5,
          stations={"cubxl": 0.9, "immersion": 0.1}),
        I("doser", "Multi-doser carousel, A&D HR-202i balance, Specac Atlas Autotouch 15T with vacuum dies and an "
                   "Edwards RV3 pump", 1, 50_000.0,
          "notes/multidoser.md (BoM $2,362); the Autotouch about EUR 37,660 at VWR (search snippet); pump and "
          "balance estimated", service=0.03, kw=1.0, duty=0.3, stations={"doser": 1.0}),
    ]


def _conventional() -> list[Item]:
    I = Item
    v = {it.key: it for it in _vertical()}
    return [
        Item(**dict(v["repowder"].__dict__, name=v["repowder"].name + " (the lab's own)")),
        I("sieve", "Retsch AS 200 sieve shaker and a set of sieves", 1, 8_000.0,
          "USAF, three AS 200 with sieves for $19,968 (2022) " + UA + "CONT_AWD_FA860122P0079_9700_-NONE-_-NONE-",
          service=0.03, kw=0.1, duty=0.1, area=0.5, stations={"sieve": 1.0}, kind="procurement"),
        I("doser", "Powder doser, balance and a manual hydraulic press with vacuum die", 1, 18_000.0, "estimate",
          service=0.03, kw=0.5, duty=0.1, area=1.0, stations={"doser": 1.0}),
        I("furnace", "Box furnace (about 1,200 C) and a forced-convection ageing oven", 1, 30_000.0,
          "estimate; a Carbolite chamber furnace cost NASA $23,521 (2022)", service=0.03, kw=3.0, duty=0.2,
          area=1.0, stations={"furnace": 1.0}),
        I("cubxl", "CubXL gantry, EZstat Pro potentiostat, OT-2 and immersion vials (DAL's own)", 1, 35_000.0,
          "estimate (as the vertical lab's)", service=0.03, kw=0.6, duty=0.3, area=1.5,
          stations={"cubxl": 0.9, "immersion": 0.1}),
        I("density", "Density balance kit and a stereo microscope", 1, 12_000.0, "estimate", service=0.02, kw=0.1,
          duty=0.2, area=0.5, stations={"density": 1.0}),
        I("glovebox", "Glovebox with purifier", 1, 55_000.0, "as the vertical lab's (Inert PureLab HE, $54,848)",
          life=10, service=0.04, kw=1.2, duty=0.5, area=2.0, kind="procurement"),
        I("hood", "Ducted fume hood", 1, 35_000.0, "estimate", life=20, service=0.02, kw=0.3, duty=1.0, area=1.5),
    ]


OPEN_FLOOR_M2 = {"vertical_lab": (305.0, "notes/floor_cleaning.md: the lab's 305 m2 of open floor"),
                 "conventional": (40.0, "assumed: benches and aisles of a university lab room")}


def horizon_days(cfg: dict) -> float:
    """A run's horizon: round 1's 'horizon_days', round 2's 'days' (bench2), else a year."""
    return float(cfg.get("horizon_days") or cfg.get("days") or 365.0)


CURVE_KEY = "curve_new"      # round 2: new alloys only (re-made reference alloys left out, as bench2's summary does)


def curve_of(c: dict) -> list:
    return [list(p) for p in (c.get(CURVE_KEY) if c.get(CURVE_KEY) is not None else c.get("curve", []))]


def facility_key(f: str) -> str:
    return "conventional" if f in ("proposed", "conventional", "dal256") else "vertical_lab"


def items(facility: str) -> list[Item]:
    return _vertical() if facility_key(facility) == "vertical_lab" else _conventional()


def crf(life: float, discount: float) -> float:
    """Capital recovery factor: the annuity that repays 1 over `life` years at `discount` (0: straight line)."""
    if discount <= 0:
        return 1.0 / life
    return discount / (1.0 - (1.0 + discount) ** -life)


def item_annual(it: Item, discount: float = 0.0) -> dict:
    kwh = RATES["kwh_usd"][0]
    return dict(capex=it.capex * crf(it.life, discount), service=it.capex * it.service,
                utilities=it.qty * it.kw * it.duty * H_YEAR * kwh,
                space=it.qty * it.area * RATES["space_om_usd_m2_yr"][0],
                space_capex=it.qty * it.area * RATES["space_capex_usd_m2_yr"][0])


def floor_area(facility: str) -> float:
    f = facility_key(facility)
    return sum(it.qty * it.area for it in items(f)) + OPEN_FLOOR_M2[f][0]


def capex(facility: str) -> float:
    return sum(it.capex for it in items(facility))


def equipment_table(facility: str, discount: float = 0.0) -> list[dict]:
    rows = []
    for it in items(facility):
        a = item_annual(it, discount)
        rows.append(dict(key=it.key, name=it.name, qty=it.qty, price_each=it.price, capex=it.capex, src=it.src,
                         kind=it.kind, life_yr=it.life, service_frac=it.service, service_src=it.service_src,
                         kw=it.kw, duty=it.duty, area_m2=it.qty * it.area, stations=it.stations,
                         annual={k: round(v, 2) for k, v in a.items()}))
    return rows


def fixed_labour(facility: str) -> float:
    return sum(PEOPLE[r]["annual"] * fte for r, fte, _ in STAFF[facility_key(facility)])


def annual_cost(facility: str, include_capex: bool = True, discount: float = 0.0, activity: dict | None = None,
                include_building: bool = True) -> dict:
    """The facility's cost for a year: fixed (depreciation, service, utilities and space, fixed staff), plus the
    variable costs of ``activity`` if given ({'labour_h': hands-on hours, 'consumables': $, 'outside_fees': $})."""
    f = facility_key(facility)
    out = dict(capex=0.0, service=0.0, utilities=0.0, labour=fixed_labour(f), consumables=0.0, outside_fees=0.0)
    for it in items(f):
        a = item_annual(it, discount)
        out["capex"] += a["capex"] + (a["space_capex"] if include_building else 0.0)
        out["service"] += a["service"]
        out["utilities"] += a["utilities"] + a["space"]
    open_m2 = OPEN_FLOOR_M2[f][0]
    out["utilities"] += open_m2 * RATES["space_om_usd_m2_yr"][0]
    if include_building:
        out["capex"] += open_m2 * RATES["space_capex_usd_m2_yr"][0]
    if activity:
        out["labour"] += activity.get("labour_h", 0.0) * hourly("grad_student")
        out["consumables"] += activity.get("consumables", 0.0)
        out["outside_fees"] += activity.get("outside_fees", 0.0)
    if not include_capex:
        out["capex"] = 0.0
    out["total"] = sum(v for k, v in out.items())
    return out


# ------------------------------------------------------------------------------------------------------- stations
# the twin's stations and their calendars (twin.facility), kept here so the accounting works from an event log alone
CAL = {"24/7": 168.0, "day": 45.0, "day6": 54.0}
ATOMIZER_SLOTS_H_WEEK = (3 * 5 + 1) * 2.5          # three starts a weekday and one on Saturday, 2.5 h a run


def available_hours(hours: str, units: int, horizon_h: float = H_YEAR, station: str = "") -> float:
    """Hours a station can work in the horizon: its calendar's open hours times its units. The atomizer is limited
    by its start slots (FLAIME: <= 3 a weekday and 1 on Saturday) rather than by the day's hours."""
    weeks = horizon_h / 168.0
    if station == "atomizer" and hours in ("day", "day6"):
        return units * ATOMIZER_SLOTS_H_WEEK * weeks
    return units * CAL.get(hours, 168.0) * weeks


def station_info(facility: str) -> dict:
    """{station: dict(name, units, hours, external)} from twin.facility (round 1 or 2, whichever is installed)."""
    from twin import facility as FAC
    kind = "vertical_lab" if facility_key(facility) == "vertical_lab" else "proposed"
    return {k: dict(name=s.name, units=s.units, hours=s.hours, external=s.external, fee_usd=s.fee_usd,
                    rate_usd_h=s.rate_usd_h) for k, s in FAC.facility(kind).items()}


# hands-on hours of a person for a booking of `dur` hours at a station, in the conventional lab: (fixed, per hour)
HANDS_ON = {
    "shop": (0.0, 1.0, "the student machines the cups at the BYU Prototyping Lab (DAL #250: about 40 min a cup)"),
    "doser": (0.25, 1.0, "weighing additions and pressing the charge by hand"),
    "atomizer": (1.0, 1.0, "the operator attends the run, plus loading, purge and cleaning (assumed 1 h)"),
    "sieve": (0.25, 1.0, "loading, shaking, weighing fractions, cleaning sieves"),
    "psd": (0.25, 1.0, "sampling, measuring, cleaning the dispersion unit"),
    "byu_sem": (0.5, 1.0, "mounting stubs or sections and the session at the Microscopy Center"),
    "byu_icpms": (0.5, 0.0, "digestion and dilution of each sample before the facility runs it"),
    "density": (0.25, 1.0, "Archimedes weighing and an optical crack check"),
    "edm": (0.5, 0.0, "drawings, drop-off and pick-up at the Provo EDM service"),
    "furnace": (0.5, 0.0, "loading, unloading and quenching"),
    "tensile": (0.25, 1.0, "set-up, extensometer, three pulls, data"),
    "tensile_hot": (0.5, 1.0, "as tensile, plus the furnace's soak"),
    "utah_midi": (3.0, 0.0, "powder and plate to Salt Lake City and back (about 45 min each way), set-up, "
                            "depowdering; Utah's staff run the build"),
    "utah_mxlab": (1.5, 1.0, "the student attends the half-day session at Utah, plus travel"),
    "mines_x2": (2.0, 0.0, "powder prepared and shipped to Golden; Mines' staff run the session (their labour is in "
                           "the fee)"),
    "nsl": (0.5, 0.0, "packaging, paperwork and shipping"),
    "cubxl": (0.5, 0.0, "electrolyte, cell set-up and cleaning; the gantry runs the spots"),
    "immersion": (1.0, 0.0, "setting up and taking down the vials (sectioning is booked at the SEM)"),
    "xrd": (0.25, 1.0, "back-loading the holder and the scan"),
    "xrf": (0.25, 1.0, "pressing the pellet or cup and the measurement"),
    "prep": (0.0, 1.0, "sectioning, mounting and polishing by hand"),
    "hardness": (0.0, 1.0, "indenting by hand"),
    "nanoindent": (0.25, 1.0, "mounting and the session"),
    "pip": (0.5, 0.0, "shipping the sample to the PIP service"),
    "valimet": (2.0, 0.0, "the order, drawings and shipping of a gas-atomization lot"),
    "ames": (2.0, 0.0, "as Valimet"),
    "hpc": (0.0, 0.0, "desk time, excluded from both labs"),
}
# in the vertical lab only the outside work keeps a person's hands on it
OUTSIDE_IN_VERTICAL = {"mines_x2", "nsl", "valimet", "ames"}


def hands_on_h(facility: str, station: str, dur: float, n_jobs: int = 1) -> float:
    f = facility_key(facility)
    if f == "vertical_lab" and station not in OUTSIDE_IN_VERTICAL:
        return 0.0
    a, b, _ = HANDS_ON.get(station, (0.25, 1.0, ""))
    return a * n_jobs + b * dur


# ------------------------------------------------------------------------------------------------------- station hours
# The routes of twin.campaign (hours per station per action), to estimate a run's station-hours from its counts when no
# event log exists (round 1). Per FLAIME lot: one atomizer run (runs=1, the policies' default) and its charge.
ROUTE = {
    "flaime_al": {
        "lot": {"shop": 2.5, "doser": 1.0, "atomizer": 2.5, "sieve": 0.75, "psd": 0.25, "byu_sem": 0.5},
        "build": {"utah_midi": 5.0, "density": 0.5, "byu_sem": 1.0},
        "demonstrated": {"edm": 0.75, "furnace": 3.0, "shop": 1.0, "tensile": 0.6},
        "sim": {"hpc": 0.05},
    },
    "onr_cu": {
        "lot": {"shop": 1.0, "doser": 1.0, "atomizer": 2.5, "sieve": 0.75, "psd": 0.25, "byu_sem": 0.5},
        "build": {"utah_mxlab": 4.0, "byu_sem": 2.0},
        "demonstrated": {"mines_x2": 5.0, "byu_sem": 3.0, "shop": 1.0, "tensile": 0.6, "cubxl": 1.2,
                         "immersion": 720.0, "byu_icpms": 0.5, "nsl": 0.01},
        "sim": {"hpc": 0.05},
    },
}
JOB_H = {"atomizer": 2.5, "shop": 2.5, "doser": 1.0, "sieve": 0.75, "psd": 0.25, "byu_sem": 1.0, "utah_midi": 5.0,
         "utah_mxlab": 4.0, "mines_x2": 5.0, "density": 0.5, "edm": 0.75, "furnace": 3.0, "tensile": 0.6,
         "tensile_hot": 1.5, "cubxl": 1.2, "immersion": 720.0, "byu_icpms": 0.1, "nsl": 0.01, "hpc": 0.05,
         "xrd": 0.75, "xrf": 0.5, "prep": 1.5, "hardness": 0.25, "nanoindent": 1.0, "pip": 0.5, "valimet": 8.0,
         "ames": 8.0}


def station_hours_from_events(ev: dict, t_max_h: float | None = None) -> dict:
    """{campaign: {station: [busy hours, jobs]}} from an event log (out/twin2/events/<run>.json schema)."""
    out: dict = {}
    for e in ev["events"]:
        a, b = float(e["t0_h"]), float(e["t1_h"])
        if t_max_h is not None:
            if a >= t_max_h:
                continue
            b = min(b, t_max_h)
        d = out.setdefault(e["campaign"], {}).setdefault(e["station"], [0.0, 0])
        d[0] += b - a
        d[1] += 1
    return out


def station_hours_from_run(run: dict, shares: dict | None = None) -> dict:
    """{campaign: {station: [hours, jobs]}} for a run without an event log. Each station's total busy hours come from
    the run itself (round 2's 'busy_h'; round 1's utilization x horizon x units); they are split between the
    campaigns by ``shares`` ({station: {campaign: fraction}}, e.g. from a sibling run's event log) where given, else
    by an estimate from the run's counts and ROUTE, else by the campaigns' overall split. Jobs: hours / JOB_H."""
    est = {}
    for camp, c in run["campaigns"].items():
        R = ROUTE.get(camp)
        if R is None:
            continue
        n = {"lot": c.get("n_lots", 0), "build": c.get("n_builds", 0), "demonstrated": c.get("n_demonstrated", 0),
             "sim": c.get("n_sims", 0)}
        d = {}
        for unit, steps in R.items():
            for st, h in steps.items():
                d[st] = d.get(st, 0.0) + n[unit] * h
        est[camp] = d
    camps = list(run["campaigns"])
    horizon = horizon_days(run["cfg"]) * 24.0
    busy = dict(run.get("busy_h") or {})
    if not busy and run.get("utilization"):
        units = run.get("units") or {}
        info = None
        if not units:
            try:
                info = station_info(run["cfg"]["facility"])
            except Exception:
                info = {}
        for st, u in run["utilization"].items():
            busy[st] = u * horizon * (units.get(st) or (info or {}).get(st, {}).get("units", 1))
    if not busy:                                     # nothing measured: the counts alone
        busy = {st: sum(est.get(c, {}).get(st, 0.0) for c in camps) for st in set().union(*[set(v) for v in est.values()])}
    tot_est = {c: sum(est.get(c, {}).values()) for c in camps}
    all_est = sum(tot_est.values()) or 1.0
    out = {c: {} for c in camps}
    for st, B in busy.items():
        if B <= 0:
            continue
        sh = (shares or {}).get(st)
        if not sh:
            e = {c: est.get(c, {}).get(st, 0.0) for c in camps}
            se = sum(e.values())
            sh = {c: v / se for c, v in e.items()} if se > 0 else {c: tot_est[c] / all_est for c in camps}
        for c in camps:
            h = B * sh.get(c, 0.0)
            if h > 0:
                out[c][st] = [h, max(h / JOB_H.get(st, 1.0), 1.0)]
    return out


def shares_from_events(ev: dict) -> dict:
    """{station: {campaign: share of its busy hours}} from an event log."""
    hrs = station_hours_from_events(ev)
    out = {}
    for c, d in hrs.items():
        if c == "external":
            continue
        for st, (h, _) in d.items():
            out.setdefault(st, {})[c] = h
    return {st: {c: h / sum(v.values()) for c, h in v.items()} for st, v in out.items() if sum(v.values()) > 0}


# ------------------------------------------------------------------------------------------------------- the ledger
OUTSIDE_KINDS = {"NSL", "gas_atomize", "blown_large", "sim_open", "sim_tc", "sim_am", "sim_heat"}


def split_cash(spend_by: dict, facility: str) -> dict:
    """The twin's ledger as consumables/feedstock against outside fees. Orders (feedstock, atomizer consumables) are
    consumables everywhere; station fees are outside fees in the conventional lab (BYU core facilities, Utah, Provo
    EDM, NSL) and consumables in the vertical lab (its in-house fees are plates, argon, wire, cones), except the
    work that stays outside (Mines, NSL, gas atomization, HPC)."""
    f = facility_key(facility)
    cons, fees = 0.0, 0.0
    for k, v in (spend_by or {}).items():
        if k == "order":
            cons += v
        elif f == "conventional" or k in OUTSIDE_KINDS:
            fees += v
        else:
            cons += v
    return dict(consumables=cons, outside_fees=fees)


# ------------------------------------------------------------------------------------------------------- allocation
def station_fixed(facility: str, discount: float = 0.0) -> tuple[dict, dict]:
    """({station: annual fixed cost by part}, {overhead part: annual}) for a facility. Parts: capex, service,
    utilities (electricity and the floor's O&M), capex includes the floor's building depreciation."""
    f = facility_key(facility)
    st, ov = {}, dict(capex=0.0, service=0.0, utilities=0.0, labour=fixed_labour(f))
    for it in items(f):
        a = item_annual(it, discount)
        parts = dict(capex=a["capex"] + a["space_capex"], service=a["service"], utilities=a["utilities"] + a["space"])
        if not it.stations:
            for k, v in parts.items():
                ov[k] += v
            continue
        tot = sum(it.stations.values())
        for s, w in it.stations.items():
            d = st.setdefault(s, dict(capex=0.0, service=0.0, utilities=0.0, items=[]))
            for k, v in parts.items():
                d[k] += v * w / tot
            d["items"].append(it.key)
    open_m2 = OPEN_FLOOR_M2[f][0]
    ov["utilities"] += open_m2 * RATES["space_om_usd_m2_yr"][0]
    ov["capex"] += open_m2 * RATES["space_capex_usd_m2_yr"][0]
    return st, ov


def allocate(facility: str, hours: dict, horizon_h: float = H_YEAR, utilization=None, discount: float = 0.0,
             info: dict | None = None, idle: str = "station") -> dict:
    """Each user's share of the facility's fixed costs over the horizon.

    hours: {campaign: {station: [busy h, jobs]}} ('external' allowed, for outside jobs in an event log).
    utilization: None (the users in `hours` are the only ones), a float (outside users bring every station up to at
    least that share of its available hours) or {station: float}.

    Rule (``idle='station'``, the default): a station someone uses is paid for by its users in proportion to their
    hours, idle hours included (a core facility's recharge: F_s * b / max(B_s, u * A_s)); a station nobody in
    `hours` uses sells u * A_s of its hours to outside users and its idle cost joins the overhead pool (the
    infrastructure, the fixed staff), which is shared in proportion to the direct cost each user absorbed. With the
    campaigns alone this charges them everything (full absorption), and the campaigns' cost falls smoothly as u
    rises. ``idle='pool'``: every station's idle hours go to the pool instead (so a campaign does not carry alone
    the idle time of an instrument only it uses)."""
    f = facility_key(facility)
    st_fixed, ov = station_fixed(f, discount)
    yr = horizon_h / H_YEAR
    info = info or {}
    camps = [c for c in hours if c != "external"]
    users = list(camps) + ["external"]
    zero = lambda: dict(capex=0.0, service=0.0, utilities=0.0, labour=0.0)
    res = {c: zero() for c in users}
    direct_abs = {c: 0.0 for c in users}
    pool = {k: ov[k] * yr for k in ov}
    idle_cost = zero()
    detail = {}
    for s, F in st_fixed.items():
        Fs = {k: F[k] * yr for k in ("capex", "service", "utilities")}
        Ftot = sum(Fs.values())
        si = info.get(s, {})
        A = available_hours(si.get("hours", "24/7"), si.get("units", 1), horizon_h, s)
        B = {c: hours.get(c, {}).get(s, [0.0])[0] for c in users}
        Bt = sum(B.values())
        u = utilization.get(s) if isinstance(utilization, dict) else utilization
        used = max(Bt, (u or 0.0) * A)
        ext_fill = used - Bt
        cap_h = max(A, used)                         # a station booked past its calendar (changeovers) is full
        if idle == "station" and Bt > 0:
            cap_h = used                             # its users carry its idle hours
        idle_h = max(cap_h - used, 0.0)
        for c, b in B.items():
            if b > 0:
                for k in Fs:
                    res[c][k] += Fs[k] * b / cap_h
                direct_abs[c] += Ftot * b / cap_h
        if ext_fill > 0:
            for k in Fs:
                res["external"][k] += Fs[k] * ext_fill / cap_h
            direct_abs["external"] += Ftot * ext_fill / cap_h
        for k in Fs:
            pool[k] += Fs[k] * idle_h / cap_h
            idle_cost[k] += Fs[k] * idle_h / cap_h
        detail[s] = dict(available_h=A, busy_h=Bt, util=Bt / A if A else 0.0, util_with_outside=used / A if A else 0.0,
                         fixed=Ftot, usd_per_busy_h=Ftot / used if used else None, idle_cost=Ftot * idle_h / cap_h)
    tot_abs = sum(direct_abs.values())
    for c, a in direct_abs.items():
        w = a / tot_abs if tot_abs > 0 else (1.0 / max(len(camps), 1) if c != "external" else 0.0)
        for k, v in pool.items():
            res[c][k] += v * w
    res["idle"] = idle_cost
    res["_detail"] = detail
    res["_pool"] = pool
    res["_shares"] = {c: (a / tot_abs if tot_abs else None) for c, a in direct_abs.items()}
    return res


# ------------------------------------------------------------------------------------------------------- per experiment
UNITS = ("demonstrated", "lots", "builds", "designs")


def _n(c: dict, unit: str) -> int:
    return int(c.get({"demonstrated": "n_demonstrated", "lots": "n_lots", "builds": "n_builds",
                      "designs": "n_designs"}[unit], 0))


def run_ledger(run: dict, events: dict | None = None, facility: str | None = None, include_capex: bool = True,
               utilization=None, discount: float = 0.0, t_max_h: float | None = None, shares: dict | None = None) -> dict:
    """Every campaign's costs over a run (or up to t_max_h): {campaign: {capex, service, utilities, labour,
    consumables, outside_fees, total, labour_h}}, plus 'external' when outside users are in the event log."""
    fac = facility or run["cfg"]["facility"]
    horizon_h = horizon_days(run["cfg"]) * 24.0
    span = t_max_h if t_max_h is not None else horizon_h
    if events is not None:
        hrs = station_hours_from_events(events, t_max_h)
        info = {k: dict(units=v.get("units", 1), hours=v.get("hours", "24/7")) for k, v in events["stations"].items()}
    else:
        hrs = station_hours_from_run(run, shares)
        if t_max_h is not None:
            hrs = {c: {s: [x[0] * span / horizon_h, x[1] * span / horizon_h] for s, x in d.items()}
                   for c, d in hrs.items()}
        if run.get("units") and run.get("calendar"):
            info = {k: dict(units=run["units"][k], hours=run["calendar"].get(k, "24/7")) for k in run["units"]}
        else:
            try:
                info = station_info(fac)
            except Exception:
                info = {}
    al = allocate(fac, hrs, span, utilization, discount, info)
    out = {}
    for camp, c in run["campaigns"].items():
        a = al.get(camp, dict(capex=0.0, service=0.0, utilities=0.0, labour=0.0))
        lab_h = sum(hands_on_h(fac, s, x[0], int(x[1])) for s, x in hrs.get(camp, {}).items())
        if t_max_h is None:
            cash = split_cash(c.get("spend_by", {}), fac)
        else:
            cash = split_cash(c.get("spend_by", {}), fac)
            tot = sum(cash.values())
            spent_t = _spent_at(c.get("curve", []), t_max_h / 24.0, c.get("spent", tot), horizon_h / 24.0)
            k = spent_t / tot if tot > 0 else 0.0
            cash = {kk: v * k for kk, v in cash.items()}
        row = dict(capex=a["capex"] if include_capex else 0.0, service=a["service"], utilities=a["utilities"],
                   labour=a["labour"] + lab_h * hourly("grad_student"), consumables=cash["consumables"],
                   outside_fees=cash["outside_fees"])
        row["total"] = sum(row.values())
        row["labour_h"] = lab_h
        out[camp] = row
    out["_alloc"] = al
    return out


def _spent_at(curve, day, final, horizon_d=365.0):
    """Cash spent by `day`: the curve's spend at its last point before `day` (the curve only has points at results;
    between them spend is interpolated linearly in time, from 0 at day 0 to `final` at the year's end)."""
    pts = [(0.0, 0.0)] + [(p[0], p[1]) for p in curve]
    if not curve:
        return final * min(day / horizon_d, 1.0)
    for (d0, s0), (d1, s1) in zip(pts, pts[1:]):
        if d0 <= day <= d1:
            return s0 + (s1 - s0) * (day - d0) / max(d1 - d0, 1e-9)
    d_last, s_last = pts[-1]
    return s_last + (final - s_last) * min((day - d_last) / max(horizon_d - d_last, 1e-9), 1.0)


def cost_per_experiment(run: dict, facility: str | None = None, include_capex: bool = True, utilization=None,
                        events: dict | None = None, unit: str = "demonstrated", discount: float = 0.0) -> dict:
    """Cost per experiment of a run, by part, for each campaign and for both together. ``run`` is one row of a
    benchmark's jsonl (round 1 or 2) or anything with 'cfg' and 'campaigns'; ``unit`` what counts as an experiment
    ('demonstrated': an alloy through the whole chain; 'lots', 'builds', 'designs')."""
    led = run_ledger(run, events, facility, include_capex, utilization, discount)
    parts = ("capex", "service", "utilities", "labour", "consumables", "outside_fees")
    out = {}
    tot = {k: 0.0 for k in parts}
    n_tot = 0
    for camp, c in run["campaigns"].items():
        n = _n(c, unit)
        n_tot += n
        row = led[camp]
        for k in parts:
            tot[k] += row[k]
        out[camp] = dict(n=n, total=row["total"], per=({k: row[k] / n for k in parts} if n else None),
                         per_total=row["total"] / n if n else None, labour_h=row["labour_h"])
    out["both"] = dict(n=n_tot, total=sum(tot.values()), per=({k: v / n_tot for k, v in tot.items()} if n_tot else None),
                       per_total=sum(tot.values()) / n_tot if n_tot else None)
    out["facility"] = facility_key(facility or run["cfg"]["facility"])
    out["include_capex"] = include_capex
    out["utilization"] = utilization
    out["unit"] = unit
    return out


def campaign_cost(run: dict, campaign: str, target: float, facility: str | None = None, include_capex: bool = True,
                  utilization=None, events: dict | None = None, discount: float = 0.0) -> dict:
    """Money and time for `campaign` to reach `target` (true utility of a demonstrated alloy) in one run: days, cash
    (the twin's ledger), operating (cash + labour + service + utilities and space) and full (operating + capex, charged
    pro rata to the share of the facility's time the campaign used up to then). Censored at the horizon if never."""
    c = run["campaigns"][campaign]
    horizon_d = horizon_days(run["cfg"])
    hit = next((p for p in curve_of(c) if p[2] >= target), None)
    day = hit[0] if hit else horizon_d
    led = run_ledger(run, events, facility, True, utilization, discount, t_max_h=day * 24.0)[campaign]
    cash = hit[1] if hit else c.get("spent", led["consumables"] + led["outside_fees"])
    operating = cash + led["labour"] + led["service"] + led["utilities"]
    return dict(reached=hit is not None, days=day, cash=cash, operating=operating, full=operating + led["capex"],
                parts=dict(led, cash=cash), n_experiments=sum(1 for p in curve_of(c) if p[0] <= day))


def cost_curves(runs: list, campaign: str, basis: str = "full", facility: str | None = None, utilization=None,
                events_of=None, shares_of=None) -> list:
    """The runs' best-so-far curves with spend replaced by `basis` ('cash', 'operating' or 'full'): the fixed and
    labour costs accrue in proportion to time (their year's total over 365 days), the cash as the twin spent it."""
    out = []
    for r in runs:
        c = r["campaigns"][campaign]
        ev = events_of(r) if events_of else None
        horizon_d = horizon_days(r["cfg"])
        cur = curve_of(c)
        spent = float(c.get("spent", cur[-1][1] if cur else 0.0))
        if basis == "cash":
            out.append(dict(curve=cur, spent=spent, horizon_days=horizon_d, n=c.get("n_demonstrated", len(cur))))
            continue
        led = run_ledger(r, ev, facility, basis == "full", utilization,
                         shares=shares_of(r) if (shares_of and ev is None) else None)[campaign]
        per_day = (led["labour"] + led["service"] + led["utilities"] + (led["capex"] if basis == "full" else 0.0)) \
            / horizon_d
        out.append(dict(curve=[[p[0], p[1] + per_day * p[0], p[2]] for p in cur], spent=spent + per_day * horizon_d,
                        horizon_days=horizon_d, n=c.get("n_demonstrated", len(cur))))
    return out


# ------------------------------------------------------------------------------------------------------- curves
def hours_per_experiment(campaign: str, facility: str = "vertical_lab") -> dict:
    """Station hours one demonstrated alloy needs, from ROUTE and a typical mix (FLAIME: 2.5 lots and 1.6 builds per
    demonstrated alloy; ONR: 5 lots and 5 deposits; round 1's cost-aware ratios in the vertical lab)."""
    R = ROUTE[campaign]
    mix = {"flaime_al": dict(lot=2.5, build=1.6, demonstrated=1.0, sim=5.0),
           "onr_cu": dict(lot=5.0, build=5.0, demonstrated=1.0, sim=20.0)}[campaign]
    out = {}
    for unit, steps in R.items():
        for s, h in steps.items():
            out[s] = out.get(s, 0.0) + mix[unit] * h
    return out


def depreciation_curve(facility: str = "vertical_lab", campaign: str = "flaime_al", utils=None,
                       discount: float = 0.0, parts=("capex",), runs=None, events_of=None, shares_of=None) -> dict:
    """Fixed cost per experiment (default: depreciation only) against utilization.

    With ``runs`` (a benchmark's runs on this facility): each run's own ledger, every station charged over
    max(the campaigns' hours, u x its available hours), the rest of the hours sold to outside users; so the curve
    starts at what the campaigns pay alone and falls as 1/u once u passes a station's own use. Without runs: a
    stylized experiment (``hours_per_experiment``) with every station at u."""
    utils = np.linspace(0.05, 0.95, 19) if utils is None else np.asarray(utils)
    if runs:
        y = []
        for u in utils:
            mb = mean_breakdown(runs, True, float(u) if u > 0 else None, campaign, events_of=events_of,
                                shares_of=shares_of)
            y.append(sum(mb["per"][p] for p in parts) if mb["per"] else float("nan"))
        return dict(utilization=[float(u) for u in utils], per_experiment=y, facility=facility_key(facility),
                    campaign=campaign, parts=list(parts), basis="ledger")
    f = facility_key(facility)
    st_fixed, ov = station_fixed(f, discount)
    try:
        info = station_info(f)
    except Exception:
        info = {}
    hpe = hours_per_experiment(campaign, f)
    direct_total = sum(sum(v[k] for k in ("capex", "service", "utilities")) for v in st_fixed.values())
    y = []
    for u in utils:
        cost = 0.0
        absorbed = 0.0
        for s, h in hpe.items():
            if s not in st_fixed:
                continue
            si = info.get(s, {})
            A = available_hours(si.get("hours", "24/7"), si.get("units", 1), H_YEAR, s)
            F = st_fixed[s]
            rate_part = sum(F[k] for k in parts if k in F) / (u * A)
            cost += rate_part * h
            absorbed += sum(F[k] for k in ("capex", "service", "utilities")) * h / (u * A)
        # overhead in proportion to the direct fixed cost absorbed
        ov_parts = sum(ov[k] for k in parts if k in ov)
        cost += ov_parts * absorbed / direct_total if direct_total else 0.0
        y.append(cost)
    return dict(utilization=[float(u) for u in utils], per_experiment=y, facility=f, campaign=campaign,
                parts=list(parts), basis="stylized")


def summary_tables() -> dict:
    out = {}
    for f in ("vertical_lab", "conventional"):
        out[f] = dict(capex=capex(f), area_m2=floor_area(f), annual=annual_cost(f),
                      annual_no_capex=annual_cost(f, include_capex=False),
                      staff=[dict(role=r, fte=x, why=w, annual=PEOPLE[r]["annual"] * x) for r, x, w in STAFF[f]],
                      items=equipment_table(f))
    out["rates"] = {k: dict(value=v[0], src=v[1]) for k, v in RATES.items()}
    out["people"] = {k: dict(v, hourly=round(hourly(k), 2)) for k, v in PEOPLE.items()}
    return out


# ------------------------------------------------------------------------------------------------------- the report
OUT2 = ROOT / "out" / "twin2" / "econ"
PART_LABEL = {"capex": "capex (depreciation)", "service": "service contracts", "utilities": "utilities and space",
              "labour": "labour", "consumables": "consumables and feedstock", "outside_fees": "outside fees"}
PARTS = tuple(PART_LABEL)
SHORT = {"conventional": "conventional", "vertical lab": "vertical"}
# fixed categorical order (the dataviz skill's reference palette, light mode)
PAL = ["#257de0", "#f47230", "#00b894", "#f2a600", "#ee7fac", "#008a17", "#6a4ce2", "#ec4647"]
INK, INK2, GRID = "#191919", "#666666", "#e6e6e6"


def load_runs(paths) -> list:
    rows = []
    for p in paths:
        p = Path(p)
        if p.exists():
            rows += [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    return rows


def _pol(p: str) -> str:
    return str(p).split(" ")[0]


def variant(cfg: dict) -> str:
    """What sets a run apart besides facility, policy and scenario (bench2's run_id suffixes)."""
    parts = []
    for k, dflt in (("stock", "stocked"), ("crucible", 225), ("reuse", True), ("cu_budget", None), ("kappa", 1.0),
                    ("isolated", False), ("wip", None), ("fidelity", "fast"), ("cu_hidden", 0.0), ("seeding", None)):
        if cfg.get(k, dflt) != dflt:
            parts.append(f"{k}-{cfg[k]}")
    return "_".join(parts)


def group_runs(rows) -> dict:
    g = {}
    for r in rows:
        c = r["cfg"]
        g.setdefault((c["facility"], _pol(c["policy"]), c.get("scenario", "historical"), variant(c)), []).append(r)
    return g


def events_index(paths) -> dict:
    idx = {}
    for p in paths:
        try:
            ev = json.loads(Path(p).read_text())
        except Exception:
            continue
        m = ev.get("meta", {})
        c = m.get("cfg", m)
        key = (c.get("facility") or m.get("facility"), _pol(c.get("policy", m.get("policy", ""))), int(c.get("seed", -1)))
        idx.setdefault(key, ev)
    return idx


def mean_breakdown(runs, include_capex=True, utilization=None, campaign=None, unit="demonstrated", events_of=None,
                   shares_of=None):
    """Ratio of sums over seeds: each part's total over all runs / experiments over all runs."""
    tot = {k: 0.0 for k in PARTS}
    n = 0
    for r in runs:
        ev = events_of(r) if events_of else None
        led = run_ledger(r, ev, None, include_capex, utilization,
                         shares=shares_of(r) if (shares_of and ev is None) else None)
        for camp, c in r["campaigns"].items():
            if campaign and camp != campaign:
                continue
            for k in PARTS:
                tot[k] += led[camp][k]
            n += _n(c, unit)
    return dict(per={k: v / n for k, v in tot.items()} if n else None, n=n, runs=len(runs),
                per_total=sum(tot.values()) / n if n else None)


def util_from_runs(runs: list, shares: dict | None = None) -> dict:
    """cloud.utilization's format from round-2 runs' own busy hours (every seed, not only the one with an event log),
    averaged; each station's hours split between the campaigns by `shares` where given."""
    rs = [r for r in runs if r.get("busy_h") and r.get("units") and r.get("calendar")]
    if not rs:
        return {}
    out = {}
    for k in sorted(set().union(*[set(r["busy_h"]) for r in rs])):
        r0 = rs[0]
        if (r0.get("external") or {}).get(k) or k == "hpc":
            continue
        units, hours = r0["units"].get(k, 1), r0["calendar"].get(k, "24/7")
        yrs = [horizon_days(r["cfg"]) / 365.0 for r in rs]
        B = float(np.mean([r["busy_h"].get(k, 0.0) / y for r, y in zip(rs, yrs)]))
        A = available_hours(hours, units, H_YEAR, k)
        sh = (shares or {}).get(k) or {}
        by = {c: B * f for c, f in sh.items()} if sh else {"campaigns": B}
        out[k] = dict(name=k, units=units, hours=hours, available_h=A, busy_h=B, by_campaign=by,
                      jobs={c: v / JOB_H.get(k, 1.0) for c, v in by.items()}, util=B / A if A else 0.0,
                      idle_h=max(A - B, 0.0))
    return out


def complete_util(U: dict, facility: str, run: dict | None = None) -> dict:
    """Add the in-house stations an event log leaves out (nobody booked them) with no busy hours, so their idle
    capacity counts as idle; calendars and units from the run (round 2) or twin.facility."""
    U = dict(U)
    if run and run.get("units") and run.get("calendar"):
        info = {k: dict(units=run["units"][k], hours=run["calendar"].get(k, "24/7"),
                        external=(run.get("external") or {}).get(k, False)) for k in run["units"]}
    else:
        try:
            info = station_info(facility)
        except Exception:
            info = {}
    for k, si in info.items():
        if k in U or si.get("external") or k == "hpc":
            continue
        A = available_hours(si.get("hours", "24/7"), int(si.get("units", 1)), H_YEAR, k)
        U[k] = dict(name=k, units=si.get("units", 1), hours=si.get("hours", "24/7"), available_h=A, busy_h=0.0,
                    by_campaign={}, jobs={}, util=0.0, idle_h=A)
    return U


def plain_cost(cmp: dict, bases) -> dict:
    """Says plainly, per cost basis, whether the new arm costs more or less to reach the target, and whether the
    95% CI settles it."""
    out = {}
    for b in bases:
        y = cmp["cost"].get(b)
        if not y:
            continue
        r = y.get("ratio_bound") if y.get("bound_kind") else y.get("ratio")
        if r is None or (isinstance(r, float) and math.isnan(r)):
            out[b] = "not estimable: neither lab reached the target in half its seeds"
            continue
        lo, hi = y.get("lo"), y.get("hi")
        word = "costs more" if r > 1 else "costs less"
        if y.get("bound_kind") == "upper":
            sure = "an upper bound on the ratio (the reference reached the target in fewer than half its seeds)"
        elif y.get("bound_kind") == "lower":
            sure = "a lower bound on the ratio (the vertical lab reached the target in fewer than half its seeds)"
        elif lo is not None and hi is not None and np.isfinite(lo) and np.isfinite(hi) and (lo > 1 or hi < 1):
            sure = "the 95% CI excludes parity"
        else:
            sure = "the 95% CI includes parity"
        out[b] = f"the vertical lab {word}: {r:.2f}x the conventional lab's {b.split(',')[0]} cost to the target " \
                 f"({sure})"
    return out


def _style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.yaxis.label.set_color(INK)
    ax.xaxis.label.set_color(INK)
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def report(runs_paths=None, events_paths=None, validate_path=None, out=OUT2, n_boot=2000, cap=0.6,
           demand_h_week=None, comparisons=None, targets=None) -> dict:
    """Everything the PR and the video quote: figures in out/twin2/econ/*.png and econ_summary.json."""
    import glob
    import time as _t
    import matplotlib
    matplotlib.use("Agg")
    from twin import cloud as _CL
    demand_h_week = _CL.DEMAND_H_WEEK[0] if demand_h_week is None else demand_h_week
    import matplotlib.pyplot as plt
    from twin import accel as AC, cloud as CL
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if runs_paths is None:
        # round 2's experiments, without the development runs (stand-in instruments, TWIN_INSTRUMENTS=stub, which
        # their configs don't record)
        r2 = sorted(p for p in glob.glob(str(ROOT / "out" / "twin2" / "runs" / "*.jsonl"))
                    if Path(p).stem != "dev" and not Path(p).stem.endswith(".errors"))
        g2 = group_runs(load_runs(r2))
        facs = {k[0] for k, v in g2.items() if len(v) >= 2}
        runs_paths = r2 if {"proposed", "vertical_lab"} <= facs else \
            [ROOT / "out" / "twin" / "runs" / "facility.jsonl", ROOT / "out" / "twin" / "runs" / "main.jsonl"]
    rows = load_runs(runs_paths)
    G = group_runs(rows)
    if events_paths is None:
        events_paths = sorted(glob.glob(str(ROOT / "out" / "twin2" / "events" / "*.json"))) + \
            sorted(glob.glob(str(OUT2 / "events" / "*.json")))
    EVI = events_index(events_paths)

    _ev_cache = {}

    def events_of(r):
        """The run's own event log (round 2's 'events_file'); runs without one use their own busy hours."""
        f = r.get("events_file")
        if f:
            p = ROOT / f if not Path(f).is_absolute() else Path(f)
            if p.exists():
                if str(p) not in _ev_cache:
                    _ev_cache[str(p)] = json.loads(p.read_text())
                return _ev_cache[str(p)]
            return None
        return None          # a log from another engine version would not match the run's own counts

    _sh_cache = {}

    def shares_of(r):
        """Per-station campaign shares from any event log of the run's group (same facility, policy, settings)."""
        c = r["cfg"]
        key = (c["facility"], _pol(c["policy"]), c.get("scenario", "historical"), variant(c))
        if key not in _sh_cache:
            ev = next((events_of(x) for x in G.get(key, []) if events_of(x) is not None), None)
            _sh_cache[key] = shares_from_events(ev) if ev else None
        return _sh_cache[key]
    # the target: the state of the art's true utility (out/twin2/oracle.json: AlSi10Mg for FLAIME, C95800 NAB for the
    # ONR), "matching or beating the state of the art"; the bench's own targets otherwise
    try:
        from twin import bench as B
        TARGET = dict(B.TARGET)
    except Exception:
        TARGET = {"flaime_al": 0.6, "onr_cu": 0.45}
    target_src = "twin.bench.TARGET"
    orc = ROOT / "out" / "twin2" / "oracle.json"
    if orc.exists():
        o = json.loads(orc.read_text())
        TARGET = {c: float(o[c]["sota_utility"]) for c in ("flaime_al", "onr_cu") if c in o and "sota_utility" in o[c]}
        target_src = "out/twin2/oracle.json sota_utility (" + ", ".join(f"{c}: {o[c].get('sota')}" for c in TARGET) + ")"
    if targets:
        TARGET.update(targets)
        target_src = "given"
    # the comparisons: the conventional lab with each policy against the vertical lab with BOFN (or the best stand-in
    # present), both on their defining settings (the vertical lab stocked; the conventional lab as bench2 runs it)
    pols_v = sorted({k[1] for k in G if k[0] == "vertical_lab" and k[3] == ""})
    new_pol = next((p for p in ("bofn_blend", "bofn", "bofn_saas", "cost_aware") if p in pols_v),
                   pols_v[0] if pols_v else None)
    vert_key = ("vertical_lab", new_pol, "historical", "") if new_pol else None

    def conv(pol):
        ks = [k for k in G if k[0] == "proposed" and k[1] == pol and k[2] == "historical"]
        ks.sort(key=lambda k: (k[3] != "stock-lean", k[3] != "", k[3]))
        return ks[0] if ks else None

    S = dict(generated_utc=_t.strftime("%Y-%m-%d %H:%M UTC", _t.gmtime()),
             inputs=dict(runs=[str(Path(p).relative_to(ROOT)) if str(p).startswith(str(ROOT)) else str(p)
                               for p in runs_paths],
                         groups={"|".join(k): len(v) for k, v in G.items()},
                         events=len(EVI), validate=str(validate_path) if validate_path else None),
             targets=dict(values=TARGET, src=target_src))
    tabs = summary_tables()
    S["facilities"] = {f: dict(capex=tabs[f]["capex"], area_m2=tabs[f]["area_m2"], annual=tabs[f]["annual"],
                               annual_no_capex=tabs[f]["annual_no_capex"], staff=tabs[f]["staff"],
                               n_items=len(tabs[f]["items"]))
                       for f in ("vertical_lab", "conventional")}
    S["rates"], S["people"] = tabs["rates"], tabs["people"]
    S["equipment"] = {f: [dict(key=i["key"], name=i["name"], qty=i["qty"], price_each=i["price_each"], kind=i["kind"],
                               src=i["src"], life_yr=i["life_yr"], service_frac=i["service_frac"], kw=i["kw"],
                               area_m2=i["area_m2"]) for i in tabs[f]["items"]] for f in ("vertical_lab", "conventional")}

    # ---- cost per experiment
    conv_key = conv(new_pol) or next((conv(p) for p in ("bofn", "heuristic", "tiered", "random") if conv(p)), None)
    if vert_key not in G:
        vert_key = None
    cpe = {}
    if conv_key and vert_key:
        cases = [("conventional, no capex", conv_key, False, None), ("conventional, with capex", conv_key, True, None),
                 ("vertical lab, campaigns only, no capex", vert_key, False, None),
                 ("vertical lab, campaigns only, with capex", vert_key, True, None),
                 (f"vertical lab, {cap:.0%} utilized, no capex", vert_key, False, cap),
                 (f"vertical lab, {cap:.0%} utilized, with capex", vert_key, True, cap)]
        for camp in (None, "flaime_al", "onr_cu"):
            cpe[camp or "both"] = {lab: mean_breakdown(G[k], inc, u, camp, events_of=events_of, shares_of=shares_of)
                                   for lab, k, inc, u in cases}
        S["cost_per_experiment"] = dict(unit="demonstrated alloy", conventional="|".join(conv_key),
                                        vertical="|".join(vert_key), cases=cpe)
        fig, axs = plt.subplots(1, 3, figsize=(17, 6.0), sharey=False)
        for ax, camp, title in zip(axs, ("both", "flaime_al", "onr_cu"),
                                   ("Both campaigns", "FLAIME (Al, LPBF)", "ONR (Cu, DED)")):
            labs = list(cpe[camp])
            bottom = np.zeros(len(labs))
            for j, part in enumerate(PARTS):
                v = np.array([(cpe[camp][l]["per"] or {}).get(part, 0.0) / 1e3 for l in labs])
                ax.bar(range(len(labs)), v, bottom=bottom, color=PAL[j], width=0.62, label=PART_LABEL[part],
                       edgecolor="white", linewidth=1.0)
                bottom += v
            for i, b in enumerate(bottom):
                ax.text(i, b * 1.01, f"${b:,.1f}k", ha="center", va="bottom", fontsize=9, color=INK)
            ax.set_xticks(range(len(labs)))
            ax.set_xticklabels(["no capex" if "no capex" in l else "with capex" for l in labs], fontsize=8, color=INK2)
            groups = [("conventional", 0.5), ("vertical, campaigns alone", 2.5), (f"vertical, {cap:.0%} utilized", 4.5)]
            for gl, gx in groups:
                if gx < len(labs):
                    ax.text(gx, -0.09, gl, transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=9,
                            color=INK)
            ax.set_title(title, fontsize=11, color=INK, loc="left")
            ax.set_ylabel("cost per demonstrated alloy (k$)")
            _style(ax)
            ax.grid(False, axis="x")
        axs[0].legend(frameon=False, fontsize=8, loc="upper left")
        fig.suptitle(f"Cost per experiment (an alloy through the whole chain): {conv_key[1]} policy on the proposals' "
                     f"partners against {vert_key[1]} in the vertical lab; mean of {len(G[conv_key])} and "
                     f"{len(G[vert_key])} twin-years", fontsize=10, color=INK, x=0.01, ha="left")
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        fig.savefig(out / "econ_cost_per_experiment.png", dpi=150)
        plt.close(fig)

    # ---- utilization and outside work (vertical lab event logs)
    vevs = [events_of(r) for r in G.get(vert_key, [])] if vert_key else []
    vevs = [e for e in vevs if e is not None]
    if not vevs:
        vevs = [ev for k, ev in EVI.items() if k[0] == "vertical_lab" and (new_pol is None or k[1] == new_pol)]
    if not vevs:
        vevs = [ev for k, ev in EVI.items() if k[0] == "vertical_lab"]
    S["inputs"]["utilization_logs"] = len(vevs)
    if vevs:
        Ur = util_from_runs(G.get(vert_key, []), shares_of(G[vert_key][0]) if G.get(vert_key) else None) \
            if vert_key else {}
        U = complete_util(Ur or CL.mean_utilization(vevs), "vertical_lab", (G.get(vert_key) or [None])[0])
        S["inputs"]["utilization_from"] = (f"the busy hours of {len(G.get(vert_key, []))} runs" if Ur else
                                           f"{len(vevs)} event logs")
        F = CL.fill(U, cap)
        Fd = CL.fill(U, cap, demand_h_week=demand_h_week)
        Fi = CL.fill(U, cap, price="industry", demand_h_week=demand_h_week)
        R, Rd, Ri = CL.capex_recovery(F), CL.capex_recovery(Fd), CL.capex_recovery(Fi)
        st_fixed, _ = station_fixed("vertical_lab")
        S["utilization"] = dict(n_logs=len(vevs), stations={k: dict(util=round(u["util"], 4), hours=u["hours"],
                                                                    units=u["units"], available_h=round(u["available_h"]),
                                                                    busy_h=round(u["busy_h"], 1),
                                                                    by_campaign={c: round(x, 1) for c, x in u["by_campaign"].items()},
                                                                    idle_h=round(u["idle_h"]))
                                                             for k, u in U.items()})
        fw = sum(st_fixed[k]["capex"] for k in U if k in st_fixed)
        S["utilization"]["capex_weighted_mean"] = sum(st_fixed[k]["capex"] * U[k]["util"] for k in U
                                                      if k in st_fixed) / fw if fw else None

        def _fill_json(Fx):
            return {k: dict(jobs_per_yr=round(v["jobs"]), ext_h=round(v["ext_h"]), revenue_per_yr=round(v["revenue"]),
                            net_per_yr=round(v["net"]), util_after=round(v["util_after"], 3), jobs=v["jobs_named"])
                    for k, v in CL.stations_of(Fx).items()}
        sens = []
        for hw in (5.0, 10.0, 20.0, 40.0):
            Rx = CL.capex_recovery(CL.fill(U, cap, demand_h_week=hw))
            sens.append(dict(h_week=hw, jobs=Rx["jobs"], revenue=Rx["revenue"], net=Rx["net"],
                             net_share_of_depreciation=Rx["net_share_of_depreciation"],
                             net_share_of_fixed=Rx["net_share_of_fixed"]))
        S["outside_work"] = dict(demand_sensitivity=sens, 
            cap=cap, demand_h_week=demand_h_week, demand_src=CL.DEMAND_H_WEEK[1], handling=CL.HANDLING_H[1],
            robots=F["_robots"], capacity=dict(stations=_fill_json(F), **{k: v for k, v in R.items() if k != "per_station"}),
            demand_limited=dict(stations=_fill_json(Fd), **{k: v for k, v in Rd.items() if k != "per_station"}),
            demand_limited_industry={k: v for k, v in Ri.items() if k != "per_station"},
            catalogue=[dict(c) for c in CL.CATALOGUE])
        keys = sorted([k for k in U if k in st_fixed], key=lambda k: -st_fixed[k]["capex"])
        fig, ax = plt.subplots(figsize=(11, 0.42 * len(keys) + 1.6))
        y = np.arange(len(keys))[::-1]
        segs = [("FLAIME", lambda k: U[k]["by_campaign"].get("flaime_al", 0.0) / U[k]["available_h"], PAL[0]),
                ("ONR", lambda k: U[k]["by_campaign"].get("onr_cu", 0.0) / U[k]["available_h"], PAL[1]),
                (f"outside users (up to {cap:.0%})", lambda k: CL.stations_of(F).get(k, {}).get("ext_h", 0.0) /
                 U[k]["available_h"], PAL[2]),
                (f"of which demand-limited ({demand_h_week:g} h/week)", None, None)]
        left = np.zeros(len(keys))
        for lab, fn, col in segs[:3]:
            v = np.array([fn(k) for k in keys])
            ax.barh(y, v, left=left, color=col, height=0.62, label=lab, edgecolor="white", linewidth=1.0)
            left += v
        dv = np.array([(U[k]["busy_h"] + CL.stations_of(Fd).get(k, {}).get("ext_h", 0.0)) / U[k]["available_h"]
                       for k in keys])
        ax.scatter(dv, y, marker="|", s=160, color=INK, label=f"campaigns + demand-limited outside work "
                                                               f"({demand_h_week:g} h a week)", zorder=3)
        for yy, k, l0 in zip(y, keys, left):
            u0 = U[k]["util"]
            ax.text(min(l0, 1.0) + 0.01, yy, f"{u0:.1%} campaigns", va="center", fontsize=8, color=INK2)
        ax.set_yticks(y)
        ax.set_yticklabels([f"{k} ({U[k]['hours']}, {U[k]['units']}x)" for k in keys], fontsize=8, color=INK2)
        ax.set_xlim(0, 1.12)
        ax.set_xlabel("share of the station's available hours in a year")
        ax.set_title(f"Vertical lab: what the two campaigns use ({S['inputs']['utilization_from']}), and the outside "
                     f"work that fits", fontsize=10, color=INK, loc="left")
        _style(ax)
        ax.grid(False, axis="y")
        ax.legend(frameon=False, fontsize=8, loc="lower right")
        fig.tight_layout()
        fig.savefig(out / "econ_utilization.png", dpi=150)
        plt.close(fig)

        # depreciation per experiment against utilization (the runs' own ledgers)
        fig, axs = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
        us = np.concatenate([[0.0], np.geomspace(0.001, 0.95, 31)])
        S["depreciation_vs_utilization"] = {}
        for ax, camp, title in zip(axs, ("flaime_al", "onr_cu"), ("FLAIME alloy", "ONR alloy")):
            for j, (key, lab) in enumerate(((vert_key, "vertical lab"), (conv_key, "conventional lab (its own tools)"))):
                if not key:
                    continue
                dc = depreciation_curve(key[0], camp, us, runs=G[key], events_of=events_of, shares_of=shares_of)
                y = np.array(dc["per_experiment"], float) / 1e3
                ax.plot(us[1:], y[1:], color=PAL[j], lw=2, label=lab)
                ax.plot([us[1]], [y[0]], "o", ms=8, color=PAL[j])
                ax.annotate(f"campaigns alone: ${y[0]:.1f}k", (us[1], y[0]), xytext=(8, 4), textcoords="offset points",
                            fontsize=8, color=INK2)
                S["depreciation_vs_utilization"][f"{key[0]}|{camp}"] = dict(
                    utilization=[round(float(x), 3) for x in us], per_experiment=[round(float(v), 1) for v in
                                                                                 dc["per_experiment"]],
                    campaigns_alone=dc["per_experiment"][0])
            ax.axvline(cap, color=INK2, lw=1, ls=":")
            ax.set_yscale("log")
            ax.set_xscale("log")
            ax.set_xlabel("utilization floor, log (outside users fill each station to it)")
            ax.set_title(f"{title}: depreciation per demonstrated alloy", fontsize=10, color=INK, loc="left")
            _style(ax)
        axs[0].set_ylabel("k$ per demonstrated alloy (log)")
        axs[0].legend(frameon=False, fontsize=8, loc="upper right")
        fig.tight_layout()
        fig.savefig(out / "econ_depreciation_vs_utilization.png", dpi=150)
        plt.close(fig)

        # slowdown: Kingman against the twin (validate.json: one policy (round 1) or several (round 2))
        V = json.loads(Path(validate_path).read_text()) if validate_path and Path(validate_path).exists() else None
        VP = (V.get("policies") if V and "policies" in V else ({V.get("policy", "cost_aware"): V} if V else {}))
        fig, axs = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
        levels = np.round(np.linspace(0.05, 0.9, 18), 3)
        S["slowdown"] = dict(kingman={}, validated=(dict(seeds=V["seeds"], levels=V["levels"], runs=V["runs"],
                                                          hook=V.get("hook"), engine=V.get("engine", "twin.bench"),
                                                          policies={}) if V else None))
        for ax, camp, title in zip(axs, ("flaime_al", "onr_cu"), ("FLAIME", "ONR")):
            ks = np.nanmean([CL.slowdown(ev, camp, levels=list(levels))["factor"] for ev in vevs], axis=0)
            ax.plot(levels, ks, color=INK2, lw=1.5, ls="--",
                    label=f"Kingman (G/G/m) on the comparison's {len(vevs)} event logs")
            S["slowdown"]["kingman"][camp] = dict(levels=[float(x) for x in levels], factor=[round(float(x), 4) for x in ks])
            for j, (pol, P) in enumerate(VP.items()):
                d = P["campaigns"][camp]
                lv = np.array(V["levels"], float)
                sc = np.array([np.nan if x is None else x for x in d["slowdown_cycle"]], float)
                sd = np.array([np.nan if x is None else x for x in d["slowdown_days"]], float)
                col = PAL[j]
                ax.plot(lv, d["kingman"], "-", lw=2, color=col, label=f"{pol}: Kingman on its own empty-lab runs")
                ax.plot(lv, sc, "o", ms=8, color=col, label=f"{pol}: twin, cycle time")
                ax.plot(lv, sd, "s", ms=8, mfc="white", mec=col, mew=1.5, label=f"{pol}: twin, days to target")
                S["slowdown"]["validated"]["policies"].setdefault(pol, {})[camp] = dict(
                    cycle=d["slowdown_cycle"], days_to_target=d["slowdown_days"], kingman=d["kingman"],
                    best_mean=d["best_mean"], n_demonstrated_mean=d["n_dem_mean"], hit_frac=d["hit_frac"],
                    throughput_ratio=d["throughput_ratio"], cycle_days=d["cycle_days"])
            ax.axhline(1.0, color=INK2, lw=0.8)
            ax.set_title(f"{title}: slowdown as outside work fills the lab", fontsize=10, color=INK, loc="left")
            ax.set_xlabel("utilization the outside work brings each station to")
            _style(ax)
        axs[0].set_ylabel("time relative to the empty lab")
        axs[0].legend(frameon=False, fontsize=7.5, loc="upper left")
        if V:
            fig.suptitle(f"Outside jobs booked into the twin before the campaigns run: {V['seeds']} seeds a level, "
                         f"{V['runs']} twin-years ({V.get('engine', 'twin.bench')})", fontsize=9, color=INK2,
                         x=0.01, ha="left")
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        fig.savefig(out / "econ_slowdown.png", dpi=150)
        plt.close(fig)

    # ---- acceleration, cost to target and throughput
    S["acceleration"] = {}
    heads = []
    shared_u = {}

    def shared_util(key):
        """Per-station utilization floors with realistic outside demand: the group's own campaign hours plus
        outside jobs up to `demand_h_week` a week per instrument (and the cap)."""
        if key in shared_u:
            return shared_u[key]
        evs = [e for e in (events_of(r) for r in G.get(key, [])) if e is not None]
        if not evs:
            evs = vevs
        Ur = util_from_runs(G.get(key, []), shares_of(G[key][0]) if G.get(key) else None)
        Uk = complete_util(Ur or (CL.mean_utilization(evs) if evs else {}), key[0], G.get(key, [None])[0])
        Fk = CL.stations_of(CL.fill(Uk, cap, demand_h_week=demand_h_week)) if Uk else {}
        shared_u[key] = {k: v["util_after"] for k, v in Fk.items()}
        return shared_u[key]
    news = [k for k in (("vertical_lab", p, "historical", "") for p in (new_pol, "heuristic")) if k in G]
    news = list(dict.fromkeys(news))
    # the references: the conventional lab run the usual ways (a metallurgist's heuristic, a Sobol DoE) and with the
    # same optimizer (BOFN), so that the lab's share of the acceleration shows apart from the optimizer's
    refs = [k for k in (conv(p) for p in ("heuristic", "sobol", "bofn")) if k]
    if not refs:
        refs = [k for k in (conv(p) for p in ("tiered", "random", new_pol)) if k]
    comparisons = comparisons or [(rk, nk) for nk in news for rk in refs]
    BASES = ("operating, alone", "full, alone", "operating, shared", "full, shared")
    if comparisons:
        fig, axs = plt.subplots(2, 2, figsize=(12, 8.4))
        for ci, (rk, nk) in enumerate(comparisons):
            name = f"vertical lab + {nk[1]} vs conventional + {rk[1]}"
            S["acceleration"][name] = {}
            su = shared_util(nk)
            for col, camp in enumerate(("flaime_al", "onr_cu")):
                ref, new = AC.curves_of(G[rk], camp), AC.curves_of(G[nk], camp)
                cc = lambda key, basis, u=None: cost_curves(G[key], camp, basis, utilization=u, events_of=events_of,
                                                            shares_of=shares_of)
                costs_ref = {"cash": cc(rk, "cash")}
                costs_new = {"cash": cc(nk, "cash")}
                for b in ("operating", "full"):
                    costs_ref[f"{b}, alone"] = costs_ref[f"{b}, shared"] = cc(rk, b)
                    costs_new[f"{b}, alone"] = cc(nk, b)
                    costs_new[f"{b}, shared"] = cc(nk, b, su or None)
                cmp = AC.compare(ref, new, TARGET[camp], costs_ref, costs_new, n_boot=n_boot,
                                 label_ref=f"conventional lab ({rk[1]})", label_new=f"vertical lab ({nk[1]})")
                hl = AC.headline(cmp, f"{'FLAIME' if camp == 'flaime_al' else 'ONR'}: ", basis_order=BASES)
                heads.append(hl)
                tg = np.round(np.linspace(0.2, 0.75, 12), 3)
                afs = [AC.acceleration_factor(ref, new, t, "days", n_boot=400) for t in tg]
                at = np.arange(30, 366, 15)
                efs = [AC.enhancement_factor(ref, new, a, "days", n_boot=400) for a in at]
                S["acceleration"][name][camp] = dict(
                    ref="|".join(rk), new="|".join(nk), target=TARGET[camp], n_ref=len(ref), n_new=len(new),
                    compare=_clean(cmp), headline=hl, shared_utilization=su, plain=plain_cost(cmp, BASES),
                    af_vs_target=[dict(target=float(t), af=a["af"], lo=a["lo"], hi=a["hi"], hit_ref=a["hit_ref"],
                                       hit_new=a["hit_new"], af_bound=a.get("af_bound"), bound_kind=a.get("bound_kind"))
                                  for t, a in zip(tg, afs)],
                    ef_vs_days=[dict(days=int(a), ef=e["ef"], lo=e["lo"], hi=e["hi"]) for a, e in zip(at, efs)])
                col_c = PAL[ci % len(PAL)]
                top = 60.0
                af = np.array([a["af"] for a in afs], float)
                lo = np.array([a["lo"] for a in afs], float)
                hi = np.array([a["hi"] for a in afs], float)
                fin = np.isfinite(af) & (af > 0)
                ax = axs[0, col]
                ax.plot(tg[fin], af[fin], "-o", color=col_c, lw=2, ms=5, label=name)
                ax.fill_between(tg, np.clip(np.where(np.isfinite(lo), lo, top), 0.1, top),
                                np.clip(np.where(np.isfinite(hi), hi, top), 0.1, top), color=col_c, alpha=0.10, lw=0)
                lb = np.array([a["af_bound"] if a.get("bound_kind") == "lower" else np.nan for a in afs], float)
                ax.plot(tg, lb, "^", ms=8, mfc="white", mec=col_c, mew=1.5)
                ub = np.array([a["af_bound"] if a.get("bound_kind") == "upper" else np.nan for a in afs], float)
                ax.plot(tg, ub, "v", ms=8, mfc="white", mec=col_c, mew=1.5)
                ax.axvline(TARGET[camp], color=INK2, lw=0.8, ls=":")
                ax.axhline(1.0, color=INK2, lw=0.8)
                ax.set_yscale("log")
                ax.set_ylim(0.1, top)
                ax.set_title(f"{'FLAIME' if camp == 'flaime_al' else 'ONR'}: acceleration factor in days "
                             f"(triangles: bounds)", fontsize=10, color=INK, loc="left")
                ax.set_xlabel("target (true utility of the best new alloy demonstrated); dotted: state of the art")
                ax.set_ylabel("AF = median days, ref / new (log)")
                _style(ax)
                ax = axs[1, col]
                ef = np.array([e["ef"] for e in efs], float)
                elo = np.array([e["lo"] for e in efs], float)
                ehi = np.array([e["hi"] for e in efs], float)
                ok = np.isfinite(ef) & (ef > 0)
                ax.plot(at[ok], ef[ok], "-", color=col_c, lw=2, label=name)
                okb = ok & np.isfinite(elo) & np.isfinite(ehi)
                ax.fill_between(at[okb], np.clip(elo[okb], 0.1, top), np.clip(ehi[okb], 0.1, top), color=col_c,
                                alpha=0.10, lw=0)
                ax.axhline(1.0, color=INK2, lw=0.8)
                ax.set_yscale("log")
                ax.set_ylim(0.1, top)
                ax.set_title(f"{'FLAIME' if camp == 'flaime_al' else 'ONR'}: enhancement factor (where the reference "
                             f"has a result)", fontsize=10, color=INK, loc="left")
                ax.set_xlabel("days")
                ax.set_ylabel("EF = mean best, new / ref (log)")
                _style(ax)
        axs[0, 0].legend(frameon=False, fontsize=8, loc="upper left")
        fig.suptitle("Acceleration (Rohr et al. 2020) and enhancement factors, 95% bootstrap CIs over seeds",
                     fontsize=10, color=INK, x=0.01, ha="left")
        fig.tight_layout(rect=(0, 0, 1, 0.96))
        fig.savefig(out / "econ_af_ef.png", dpi=150)
        plt.close(fig)
    S["headline"] = heads
    S["headline_setup"] = dict(
        bases={"operating": "cash + labour + service + utilities and space (no capex)",
               "full": "operating + depreciation (capex)",
               "alone": "the vertical lab's fixed costs carried by the two campaigns only",
               "shared": f"outside users take each in-house station's idle hours up to {demand_h_week:g} h a week of "
                         f"demand (assumed) and {cap:.0%} utilization, paying their share"},
        conventional_note="the conventional lab is charged alone in both cases; its rented facilities' rates already "
                          "include their sharing")

    # ---- throughput: demonstrated alloys and measurements a year, per policy and facility
    MEAS = ("psd", "byu_sem", "xrd", "xrf", "byu_icpms", "density", "tensile", "tensile_hot", "hardness", "nanoindent",
            "pip", "cubxl", "immersion")

    def _job_h(key):
        evs = [e for e in (events_of(r) for r in G.get(key, [])) if e is not None]
        out_h = {}
        if evs:
            for s_ in MEAS:
                d_ = [e["t1_h"] - e["t0_h"] for ev in evs for e in ev["events"] if e["station"] == s_
                      and e["campaign"] != "external"]
                if d_:
                    out_h[s_] = float(np.mean(d_))
        return out_h
    thr = {}
    for key, rs in G.items():
        if key[2] != "historical" or (key[0] == "vertical_lab" and key[3] != "") or \
                (key[0] == "proposed" and key != conv(key[1])):
            continue
        jh = _job_h(key)
        rows_ = []
        for r in rs:
            yrs = horizon_days(r["cfg"]) / 365.0
            dem = {c: r["campaigns"][c]["n_demonstrated"] / yrs for c in r["campaigns"]}
            busy = r.get("busy_h") or {}
            meas = sum(busy.get(s_, 0.0) / jh.get(s_, JOB_H.get(s_, 1.0)) for s_ in MEAS if s_ != "immersion") / yrs
            res_ = {c: sum(v for t_, v in (r["campaigns"][c].get("n_results") or {}).items() if t_ != "sim") / yrs
                    for c in r["campaigns"]}
            rows_.append((dem, meas if busy else None, res_))
        thr["|".join(key)] = dict(
            facility=key[0], policy=key[1], n=len(rs),
            demonstrated_per_yr={c: float(np.mean([x[0][c] for x in rows_])) for c in rows_[0][0]},
            demonstrated_per_yr_total=float(np.mean([sum(x[0].values()) for x in rows_])),
            measurements_per_yr=(float(np.mean([x[1] for x in rows_ if x[1] is not None]))
                                 if any(x[1] is not None for x in rows_) else None),
            results_per_yr=float(np.mean([sum(x[2].values()) for x in rows_])))
    S["throughput"] = thr
    pols_both = [p for p in ("random", "sobol", "heuristic", "tiered", "cost_aware", "gpbo", "bofn", "bofn_blend")
                 if any(v["policy"] == p and v["facility"] == "vertical_lab" for v in thr.values())]
    if pols_both:
        fig, axs = plt.subplots(1, 2, figsize=(12, 4.6))
        x = np.arange(len(pols_both))
        for ax, metric, lab in ((axs[0], "demonstrated_per_yr_total", "alloys demonstrated a year (both campaigns)"),
                                (axs[1], "measurements_per_yr", "instrument measurements a year")):
            for j, (fac_, nm) in enumerate((("vertical_lab", "vertical lab"), ("proposed", "conventional lab"))):
                vals = []
                for p in pols_both:
                    v = next((t for t in thr.values() if t["facility"] == fac_ and t["policy"] == p), None)
                    vals.append(np.nan if (v is None or v.get(metric) is None) else v[metric])
                ax.bar(x + (j - 0.5) * 0.38, vals, width=0.36, color=PAL[j], label=nm, edgecolor="white")
                for xx, vv in zip(x + (j - 0.5) * 0.38, vals):
                    if np.isfinite(vv):
                        ax.text(xx, vv, f"{vv:,.0f}", ha="center", va="bottom", fontsize=7, color=INK2)
            ax.set_xticks(x)
            ax.set_xticklabels(pols_both, fontsize=8, color=INK2)
            ax.set_title(lab, fontsize=10, color=INK, loc="left")
            _style(ax)
            ax.grid(False, axis="x")
        axs[0].legend(frameon=False, fontsize=8)
        fig.suptitle("Throughput per policy: the vertical lab (a year, stocked) against the conventional lab (per year "
                     "of its runs)", fontsize=10, color=INK, x=0.01, ha="left")
        fig.tight_layout(rect=(0, 0, 1, 0.94))
        fig.savefig(out / "econ_throughput.png", dpi=150)
        plt.close(fig)

    # ---- value per capex dollar
    if conv_key and vert_key and "outside_work" in S:
        conv_full = mean_breakdown(G[conv_key], True, None, events_of=events_of, shares_of=shares_of)
        n_v = np.mean([sum(c["n_demonstrated"] for c in r["campaigns"].values()) for r in G[vert_key]])
        val0 = n_v * (conv_full["per_total"] or 0.0)
        cap_v = capex("vertical_lab")
        S["value_per_capex_dollar"] = dict(
            note="a year's demonstrated alloys valued at what the conventional lab pays for one (its full cost per "
                 "alloy), plus outside users' net revenue, over the vertical lab's capex",
            experiments_per_yr=float(n_v), value_of_an_experiment=conv_full["per_total"],
            without_outside=val0 / cap_v,
            with_outside_demand_limited=(val0 + S["outside_work"]["demand_limited"]["net"]) / cap_v,
            with_outside_capacity=(val0 + S["outside_work"]["capacity"]["net"]) / cap_v)
    S["assumptions"] = [
        "Prices: procurement records and list prices where cited in econ.py's tables; estimates and assumptions marked "
        "so (zwickiLine, MX-Lab installation, fit-out, couplings, the CubXL bundle, hoods).",
        "Depreciation straight-line over 5-20 years (BYU capitalizes equipment over 3-10 years, buildings over 40); "
        "service contracts 2-10 % of the price a year (8-15 % for full service on analytical instruments).",
        "Labour: the conventional lab's hands-on hours per booking (econ.HANDS_ON, assumed) at a BYU PhD student's "
        "stipend and tuition over 1,500 research hours; the vertical lab's one day-shift technician (upkeep.py) and a "
        "quarter of a research engineer, at BLS Provo-Orem means plus an assumed 35 % fringe. Design and analysis "
        "time is excluded from both.",
        "The conventional lab's in-house stations that the twin leaves free (Instron frames, hardness, metallography)"
        " carry no charge; BYU's internal core-facility rates are subsidised (BYU EM: operating cost about $300/h).",
        "Outside work: catalogue rates from published user-facility rate sheets; demand is not modelled beyond a cap "
        f"of {cap:.0%} and an assumed {demand_h_week:g} h a week per instrument; handling 0.25 h of a technician and "
        "10 % consumables a job.",
    ]
    S["key_numbers"] = key_numbers(_clean(S))
    (out / "econ_summary.json").write_text(json.dumps(_clean(S), indent=1) + "\n")
    return S


def _clean(x):
    if isinstance(x, dict):
        return {str(k): _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    if isinstance(x, (np.floating, float)):
        v = float(x)
        return None if math.isnan(v) else (v if math.isfinite(v) else ("inf" if v > 0 else "-inf"))
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


# ------------------------------------------------------------------------------------------------------- notes
def _k(v):
    return "-" if v is None else f"${v / 1e3:,.1f}k"


def _m(v):
    return "-" if v is None else f"${v / 1e6:,.2f}M"


def key_numbers(S: dict) -> dict:
    """The numbers a PR description or a video would quote, in one place."""
    K = {}
    f = S["facilities"]
    K["capex_vertical"], K["capex_conventional"] = f["vertical_lab"]["capex"], f["conventional"]["capex"]
    K["fixed_per_year_vertical"] = f["vertical_lab"]["annual"]["total"]
    K["fixed_per_year_conventional"] = f["conventional"]["annual"]["total"]
    cpe = S.get("cost_per_experiment", {}).get("cases", {})
    for camp in ("both", "flaime_al", "onr_cu"):
        for case, v in cpe.get(camp, {}).items():
            K[f"cost_per_alloy|{camp}|{case}"] = v["per_total"]
    if "utilization" in S:
        K["capex_weighted_utilization_campaigns"] = S["utilization"]["capex_weighted_mean"]
        K["atomizer_utilization_campaigns"] = S["utilization"]["stations"].get("atomizer", {}).get("util")
        ow = S["outside_work"]
        for key in ("capacity", "demand_limited"):
            K[f"outside_{key}_jobs_per_yr"] = ow[key]["jobs"]
            K[f"outside_{key}_revenue_per_yr"] = ow[key]["revenue"]
            K[f"outside_{key}_net_per_yr"] = ow[key]["net"]
            K[f"outside_{key}_net_x_depreciation"] = ow[key]["net_share_of_depreciation"]
            K[f"outside_{key}_net_x_fixed"] = ow[key]["net_share_of_fixed"]
        K["outside_cap"], K["outside_demand_h_week"] = ow["cap"], ow["demand_h_week"]
    if S.get("value_per_capex_dollar"):
        v = S["value_per_capex_dollar"]
        K["value_per_capex_dollar_without_outside"] = v["without_outside"]
        K["value_per_capex_dollar_with_outside_demand_limited"] = v["with_outside_demand_limited"]
    V = (S.get("slowdown") or {}).get("validated")
    if V:
        for pol, P in (V.get("policies") or {}).items():
            for camp, d in P.items():
                for i, lv in enumerate(V["levels"]):
                    K[f"slowdown|{pol}|{camp}|{lv:g}|twin_cycle"] = d["cycle"][i]
                    K[f"slowdown|{pol}|{camp}|{lv:g}|twin_days_to_target"] = d["days_to_target"][i]
                    K[f"slowdown|{pol}|{camp}|{lv:g}|kingman"] = d["kingman"][i]
                    K[f"slowdown|{pol}|{camp}|{lv:g}|demonstrated_ratio"] = d["throughput_ratio"][i]
    for name, cc in (S.get("acceleration") or {}).items():
        for camp, x in cc.items():
            cm = x["compare"]
            for xk in ("days", "experiments"):
                d = cm[xk]
                K[f"af_{xk}|{name}|{camp}"] = d["af_bound"] if d.get("bound_kind") else d["af"]
                K[f"af_{xk}_kind|{name}|{camp}"] = d.get("bound_kind") or "estimate"
                K[f"af_{xk}_ci|{name}|{camp}"] = [d["lo"], d["hi"]]
            K[f"reached|{name}|{camp}"] = dict(new=cm["days"]["hit_new"], ref=cm["days"]["hit_ref"],
                                               n_new=cm["days"]["n_new"], n_ref=cm["days"]["n_ref"])
            for b, y in cm["cost"].items():
                K[f"cost_ratio|{b}|{name}|{camp}"] = y["ratio_bound"] if y.get("bound_kind") else y["ratio"]
                K[f"cost_ratio_kind|{b}|{name}|{camp}"] = y.get("bound_kind") or "estimate"
                K[f"cost_ratio_ci|{b}|{name}|{camp}"] = [y.get("lo"), y.get("hi")]
            for b, txt in (x.get("plain") or {}).items():
                K[f"plain|{b}|{name}|{camp}"] = txt
    for key, t in (S.get("throughput") or {}).items():
        K[f"throughput|{key}|demonstrated_per_yr"] = t["demonstrated_per_yr_total"]
        K[f"throughput|{key}|measurements_per_yr"] = t["measurements_per_yr"]
    return K


def key_bullets(S: dict) -> list:
    """The key numbers as sentences (the top of the notes' results block)."""
    K = S.get("key_numbers") or key_numbers(S)
    B = []
    B.append(f"**Capital.** The vertical lab's equipment and fit-out: {_m(K['capex_vertical'])}; the conventional lab's "
             f"own tools: {_m(K['capex_conventional'])}. A year of fixed cost (depreciation, service, utilities and "
             f"space, fixed staff): {_m(K['fixed_per_year_vertical'])} against {_m(K['fixed_per_year_conventional'])}.")
    if "capex_weighted_utilization_campaigns" in K:
        B.append(f"**Utilization.** The two campaigns use {K['capex_weighted_utilization_campaigns']:.1%} of the "
                 f"vertical lab's available hours (capex-weighted); the atomizer, the busiest, "
                 f"{K['atomizer_utilization_campaigns']:.0%} of its start slots.")
    c = lambda case: K.get(f"cost_per_alloy|both|{case}")
    cap = K.get("outside_cap", 0.6)
    if c("conventional, no capex") is not None:
        B.append(f"**Cost per demonstrated alloy** (both campaigns): conventional {_k(c('conventional, no capex'))} "
                 f"without capex, {_k(c('conventional, with capex'))} with; vertical lab used by the campaigns alone "
                 f"{_k(c('vertical lab, campaigns only, no capex'))} / {_k(c('vertical lab, campaigns only, with capex'))}; "
                 f"vertical lab {cap:.0%} utilized by outside users "
                 f"{_k(c(f'vertical lab, {cap:.0%} utilized, no capex'))} / "
                 f"{_k(c(f'vertical lab, {cap:.0%} utilized, with capex'))}.")
    if "outside_demand_limited_revenue_per_yr" in K:
        B.append(f"**Outside work.** At {K['outside_demand_h_week']:g} h a week of outside demand per instrument "
                 f"(assumed), {K['outside_demand_limited_jobs_per_yr']:,.0f} jobs a year bring "
                 f"{_m(K['outside_demand_limited_revenue_per_yr'])} at academic user-facility rates, "
                 f"{_m(K['outside_demand_limited_net_per_yr'])} net of handling and consumables: "
                 f"{K['outside_demand_limited_net_x_depreciation']:.1f}x the lab's depreciation and "
                 f"{K['outside_demand_limited_net_x_fixed']:.1f}x all its fixed costs. Filling every station to "
                 f"{cap:.0%} instead (capacity, no demand limit): {K['outside_capacity_jobs_per_yr']:,.0f} jobs, "
                 f"{_m(K['outside_capacity_revenue_per_yr'])}.")
    V = (S.get("slowdown") or {}).get("validated") or {}
    fx = lambda v: "-" if v is None else f"{v:.2f}"
    for pol, P in (V.get("policies") or {}).items():
        lv = [l for l in V["levels"] if l > 0]
        idx = [V["levels"].index(l) for l in lv]
        for camp, lab in (("flaime_al", "FLAIME"), ("onr_cu", "ONR")):
            d = P.get(camp)
            if not d:
                continue
            B.append(f"**Slowdown, {lab}, {pol}.** Outside work bringing each station to " +
                     ", ".join(f"{l:.0%}" for l in lv) + ": cycle time x" +
                     "/".join(fx(d["cycle"][i]) for i in idx) + " in the twin (Kingman x" +
                     "/".join(fx(d["kingman"][i]) for i in idx) + "), days to the state of the art x" +
                     "/".join(fx(d["days_to_target"][i]) for i in idx) + ", alloys demonstrated x" +
                     "/".join(fx(d["throughput_ratio"][i]) for i in idx) + ".")
    for t in (S.get("throughput") or {}).values():
        pass
    thr = S.get("throughput") or {}
    pv = {t["policy"]: t for t in thr.values() if t["facility"] == "vertical_lab"}
    pc = {t["policy"]: t for t in thr.values() if t["facility"] == "proposed"}
    common = [p for p in pv if p in pc]
    if common:
        B.append("**Throughput** (alloys demonstrated a year, both campaigns; vertical / conventional): " +
                 "; ".join(f"{p} {pv[p]['demonstrated_per_yr_total']:.0f} / {pc[p]['demonstrated_per_yr_total']:.0f}"
                           for p in common) + ". Instrument measurements a year: " +
                 "; ".join(f"{p} {(pv[p]['measurements_per_yr'] or 0):,.0f} / {(pc[p]['measurements_per_yr'] or 0):,.0f}"
                           for p in common) + ".")
    for name, cc in (S.get("acceleration") or {}).items():
        for camp, x in cc.items():
            B.append("**Headline.** " + x["headline"])
            for b, txt in (x.get("plain") or {}).items():
                if b.startswith("full"):
                    B.append(f"  - {name}, {camp}, {b}: {txt}.")
    return B


def notes_md(S: dict) -> str:
    """The results block of notes/twin_econ.md, from econ_summary.json (so the notes follow every re-run)."""
    L = []
    inp = S["inputs"]
    L.append(f"*Generated {S['generated_utc']} from {', '.join(inp['runs'])} "
             f"({'; '.join(f'{k}: {v}' for k, v in inp['groups'].items())}), {inp['events']} event logs"
             + (f", and the slowdown validation in out/twin2/econ/validate.json" if inp.get("validate") else "")
             + f". Targets: {S['targets']['src']}.*\n")
    L.append("### Key numbers\n")
    for b in key_bullets(S):
        L.append(f"- {b}")
    L.append("")
    L.append("### The two labs\n")
    L.append("| | capex | floor | depreciation a year | service | utilities and space | fixed staff | fixed cost a year |")
    L.append("|---|---|---|---|---|---|---|---|")
    for f, lab in (("vertical_lab", "vertical lab"), ("conventional", "conventional lab (its own tools)")):
        x = S["facilities"][f]
        a = x["annual"]
        L.append(f"| {lab} | {_m(x['capex'])} | {x['area_m2']:.0f} m² | {_k(a['capex'])} | {_k(a['service'])} | "
                 f"{_k(a['utilities'])} | {_k(a['labour'])} | {_k(a['total'])} |")
    L.append("")
    for f, lab in (("vertical_lab", "Vertical lab"), ("conventional", "Conventional lab")):
        L.append(f"**{lab}: equipment** (each item's price, life, service share, kW at an assumed duty, floor; "
                 f"source)\n")
        L.append("| item | n | each | life | service | kW | m² | kind | source |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for i in S["equipment"][f]:
            L.append(f"| {i['name']} | {i['qty']} | ${i['price_each']:,.0f} | {i['life_yr']:g} y | "
                     f"{i['service_frac']:.0%} | {i['kw']:g} | {i['area_m2']:g} | {i['kind']} | {i['src']} |")
        L.append("")
    L.append("**People** (fully loaded; hourly = a year's cost over productive hours)\n")
    L.append("| role | a year | hours | per hour | source |")
    L.append("|---|---|---|---|---|")
    for r, p in S["people"].items():
        L.append(f"| {r.replace('_', ' ')} | ${p['annual']:,.0f} | {p['hours']:,.0f} | ${p['hourly']:,.2f} | {p['src']} |")
    L.append("")
    L.append("| rate | value | source |")
    L.append("|---|---|---|")
    for k, v in S["rates"].items():
        L.append(f"| {k} | {v['value']:g} | {v['src']} |")
    L.append("")
    if "cost_per_experiment" in S:
        c = S["cost_per_experiment"]
        L.append(f"### Cost per experiment\n\nAn experiment is an alloy demonstrated through the whole chain "
                 f"(tensile for FLAIME; tensile and 30-day immersion for the ONR). Conventional: `{c['conventional']}`; "
                 f"vertical: `{c['vertical']}`. Ratio of sums over the seeds.\n")
        L.append("| case | alloys | capex | service | utilities, space | labour | consumables, feedstock | outside fees "
                 "| **total** |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for camp, lab in (("both", "both"), ("flaime_al", "FLAIME"), ("onr_cu", "ONR")):
            for case, v in c["cases"][camp].items():
                p = v["per"] or {}
                L.append(f"| {lab}: {case} | {v['n']} | " + " | ".join(_k(p.get(k)) for k in PARTS) +
                         f" | **{_k(v['per_total'])}** |")
        L.append("")
    if "utilization" in S:
        U = S["utilization"]
        ow = S["outside_work"]
        L.append(f"### Utilization and outside work\n\nFrom {inp.get('utilization_from', str(U['n_logs']) + ' event logs')} of the vertical lab "
                 f"(capex-weighted mean utilization by the two campaigns: {U['capex_weighted_mean']:.1%}). Outside "
                 f"jobs fill each station's idle hours up to {ow['cap']:.0%} of its available hours (capacity), or "
                 f"up to {ow['demand_h_week']:g} h a week of outside demand per instrument (demand-limited; "
                 f"{ow['demand_src']}).\n")
        L.append("| station | calendar | available h | campaigns' h | utilization | outside jobs a year (capacity) | "
                 "revenue (capacity) | outside jobs (demand-limited) | revenue (demand-limited) | jobs |")
        L.append("|---|---|---|---|---|---|---|---|---|---|")
        cs, ds = ow["capacity"]["stations"], ow["demand_limited"]["stations"]
        for k, u in sorted(U["stations"].items(), key=lambda kv: -kv[1]["util"]):
            a, b = cs.get(k), ds.get(k)
            L.append(f"| {k} | {u.get('hours', '')}, {u.get('units', '')}x | {u['available_h']:,} | {u['busy_h']:,.0f} | "
                     f"{u['util']:.1%} | "
                     + (f"{a['jobs_per_yr']:,} | {_k(a['revenue_per_yr'])} | {b['jobs_per_yr']:,} | "
                        f"{_k(b['revenue_per_yr'])} | {', '.join(a['jobs'])} |" if a else "- | - | - | - | - |"))
        L.append("")
        L.append("| | outside jobs a year | revenue | net of handling and consumables | x depreciation | "
                 "x all fixed costs |")
        L.append("|---|---|---|---|---|---|")
        for key, lab in (("capacity", f"capacity ({ow['cap']:.0%} cap)"),
                         ("demand_limited", f"demand-limited ({ow['demand_h_week']:g} h a week), academic rates")):
            d = ow[key]
            L.append(f"| {lab} | {d['jobs']:,.0f} | {_m(d['revenue'])} | {_m(d['net'])} | "
                     f"{d['net_share_of_depreciation']:.1f} | {d['net_share_of_fixed']:.1f} |")
        d = ow["demand_limited_industry"]
        L.append(f"| demand-limited, industry rates | {d['jobs']:,.0f} | {_m(d['revenue'])} | {_m(d['net'])} | "
                 f"{d['net_share_of_depreciation']:.1f} | {d['net_share_of_fixed']:.1f} |")
        if "demand_sensitivity" in ow:
            for row in ow["demand_sensitivity"]:
                L.append(f"| demand {row['h_week']:g} h a week, academic | {row['jobs']:,.0f} | {_m(row['revenue'])} | "
                         f"{_m(row['net'])} | {row['net_share_of_depreciation']:.1f} | "
                         f"{row['net_share_of_fixed']:.1f} |")
        L.append("")
        if "value_per_capex_dollar" in S:
            v = S["value_per_capex_dollar"]
            L.append(f"**Value per capex dollar.** The campaigns demonstrate {v['experiments_per_yr']:.1f} alloys a year "
                     f"in the vertical lab; at the conventional lab's full cost of {_k(v['value_of_an_experiment'])} "
                     f"an alloy that is {v['without_outside']:.2f} dollars of experiments a year per dollar of capex. "
                     f"With demand-limited outside work it is {v['with_outside_demand_limited']:.2f}, and "
                     f"{v['with_outside_capacity']:.2f} if the capacity sells.\n")
    if S.get("slowdown") and S["slowdown"].get("validated"):
        V = S["slowdown"]["validated"]
        L.append("### Slowdown\n")
        L.append(f"Outside jobs booked into the twin's facility before the campaigns run (`Twin(..., external=...)`, "
                 f"{V.get('engine', 'twin.bench')}), {V['seeds']} seeds a level, {V['runs']} twin-years in all, against "
                 f"Kingman's estimate on each policy's own empty-lab runs.\n")
        L.append("| policy | campaign | outside work up to | twin: cycle time | twin: days to the state of the art (KM) | "
                 "Kingman | alloys demonstrated | best new alloy |")
        L.append("|---|---|---|---|---|---|---|---|")
        f = lambda x: "-" if x is None else f"{x:.2f}x"
        for pol, P in V.get("policies", {}).items():
            for camp, d in P.items():
                for i, lv in enumerate(V["levels"]):
                    L.append(f"| {pol} | {camp} | {lv:.0%} | {f(d['cycle'][i])} | {f(d['days_to_target'][i])} | "
                             f"{f(d['kingman'][i])} | {d['n_demonstrated_mean'][i]:.1f} | {d['best_mean'][i]:.3f} |")
        L.append("")
    if S.get("throughput"):
        L.append("### Throughput\n")
        L.append("| facility | policy | runs | alloys demonstrated a year (FLAIME + ONR) | instrument measurements a year | "
                 "results a year (no simulations) |")
        L.append("|---|---|---|---|---|---|")
        for key, t in sorted(S["throughput"].items(), key=lambda kv: (kv[1]["facility"], kv[1]["policy"])):
            dm = t["demonstrated_per_yr"]
            ms = "-" if t["measurements_per_yr"] is None else f"{t['measurements_per_yr']:,.0f}"
            L.append(f"| {t['facility']} | {t['policy']} | {t['n']} | {t['demonstrated_per_yr_total']:.1f} "
                     f"({dm.get('flaime_al', 0):.1f} + {dm.get('onr_cu', 0):.1f}) | {ms} | {t['results_per_yr']:,.0f} |")
        L.append("")
    if S.get("acceleration"):
        L.append("### Acceleration and cost to the state of the art\n")
        hs = S.get("headline_setup", {})
        if hs:
            L.append("Cost bases: " + "; ".join(f"**{k}**: {v}" for k, v in hs.get("bases", {}).items()) +
                     f". {hs.get('conventional_note', '')}.\n")
        L.append("| comparison | campaign | target | reached (vertical / conventional) | AF in days (95% CI) | "
                 "AF in alloys | cost ratio: operating, alone | full, alone | operating, shared | full, shared |")
        L.append("|---|---|---|---|---|---|---|---|---|---|")

        def af(a):
            if a.get("bound_kind") == "lower":
                return f">= {a['af_bound']:.1f}"
            if a.get("bound_kind") == "upper":
                return f"<= {a['af_bound']:.2f}"
            if isinstance(a["af"], str) or a["af"] is None:
                return str(a["af"])
            hi = a["hi"] if not isinstance(a["hi"], str) else float("inf")
            lo = a["lo"] if not isinstance(a["lo"], str) else float("inf")
            return f"{a['af']:.2f} ({lo:.2f}-{'unbounded' if hi == float('inf') else f'{hi:.2f}'})"

        def cr(cm, b):
            y = cm["cost"].get(b)
            if not y:
                return "-"
            if y.get("bound_kind") == "upper":
                return f"<= {y['ratio_bound']:.2f}x"
            if y.get("bound_kind") == "lower":
                return f">= {y['ratio_bound']:.2f}x"
            r = y["ratio"]
            if r is None or isinstance(r, str):
                return "-"
            lo = y["lo"] if not isinstance(y["lo"], str) else float("inf")
            hi = y["hi"] if not isinstance(y["hi"], str) else float("inf")
            return f"{r:.2f}x ({lo:.2f}-{'unbounded' if hi == float('inf') else f'{hi:.2f}'})"
        for name, cc in S["acceleration"].items():
            for camp, x in cc.items():
                cm = x["compare"]
                d, e = cm["days"], cm["experiments"]
                L.append(f"| {name} | {camp} | {x['target']:.3f} | {d['hit_new']:.0%} of {d['n_new']} / "
                         f"{d['hit_ref']:.0%} of {d['n_ref']} | {af(d)} | {af(e)} | " +
                         " | ".join(cr(cm, b) for b in ("operating, alone", "full, alone", "operating, shared",
                                                         "full, shared")) + " |")
        L.append("")
        L.append("A cost ratio is the vertical lab's median cost to the target over the conventional lab's: above 1x the "
                 "vertical lab costs more. In plain words:\n")
        for name, cc in S["acceleration"].items():
            for camp, x in cc.items():
                for b, txt in (x.get("plain") or {}).items():
                    L.append(f"- {name}, {camp}, {b}: {txt}.")
        L.append("")
        L.append("Headlines:\n")
        for h in S.get("headline", []):
            L.append(f"- {h}")
        L.append("")
    return "\n".join(L)


def write_notes(S: dict | None = None, path: Path = ROOT / "notes" / "twin_econ.md") -> None:
    S = S or json.loads((OUT2 / "econ_summary.json").read_text())
    block = notes_md(S)
    txt = path.read_text() if path.exists() else "<!-- econ:begin -->\n<!-- econ:end -->\n"
    a, b = txt.index("<!-- econ:begin -->"), txt.index("<!-- econ:end -->")
    path.write_text(txt[:a] + "<!-- econ:begin -->\n" + block + "\n" + txt[b:])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "tables"
    if cmd == "tables":
        S = summary_tables()
        for f in ("vertical_lab", "conventional"):
            s = S[f]
            print(f"{f}: capex ${s['capex'] / 1e6:.2f}M, {s['area_m2']:.0f} m2; a year: " +
                  ", ".join(f"{k} ${v / 1e3:.0f}k" for k, v in s["annual"].items()))
    elif cmd == "all":
        vp = ROOT / "out" / "twin2" / "econ" / "validate.json"
        S = report(validate_path=vp)
        write_notes(S)
        print("\n".join(S.get("headline", [])))
    elif cmd == "notes":
        write_notes()
    elif cmd == "report":
        path = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "out" / "twin" / "runs" / "facility.jsonl"
        for line in path.read_text().splitlines():
            r = json.loads(line)
            for cap in (False, True):
                x = cost_per_experiment(r, include_capex=cap)
                b = x["both"]
                print(r["cfg"]["facility"], r["cfg"]["policy"], r["cfg"]["seed"], "capex" if cap else "no capex",
                      b["n"], None if b["per_total"] is None else round(b["per_total"]))
