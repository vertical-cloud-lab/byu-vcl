#!/usr/bin/env python3
"""The vertical lab's waste: every stream its workflows make, how much, and where it goes (#303, PR #318).

Sterling, on PR #318 (2026-11-20): "consider waste and disposal procedures. Where does each waste go, how do we get
pickups, and what can we do to minimize the hazard and risk, and thereby the cost of disposal?"

This file is the arithmetic behind notes/waste.md: for each stream, an amount per unit of work (an atomizer run, an
alloy, a build, a polish, an hour of the wire EDM, a corrosion night, ...), multiplied by how many of those units a
year holds in two schedules:

* **one a day**: the finale's year (``timelapse.py model`` -> out/timelapse_model.json, ``totals["1 year"]``: 667
  atomizer runs, 309 alloys fully tested, with upkeep and failures);
* **ten a day**: PR #332's rung R11 (``bottleneck.py`` at cc31ddc, out/bottleneck.json: 16.8 runs, 10.3 alloys fully
  tested, 12.0 screening plates and 1.03 full plates a day, with three rePowders, four MIDIs and promoted alloys from
  684 g charges). If that file is here (PR #332 merged), it is read; otherwise the figures below are used.

Every amount carries its basis: a workflow note, ``upkeep.py``'s consumables, a maker's figure, or "assumed". Most are
assumed: nothing here has been weighed. The point is the relative size of the streams and how they scale, which is
what decides containers, pickups and where the effort to cut hazard and cost should go.

    python3 waste.py            # out/waste_model.json, out/waste_streams.png
    python3 waste.py table      # the table, printed
    python3 waste.py markdown   # the table as notes/waste.md has it
    python3 waste.py pickups    # Risk Management's containers a year, and what stands in the lab between pickups
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

# ===================================================================================================== work units
# PR #332 (bottleneck.py at cc31ddc), out/bottleneck.json: ladder R11's "simulated" and consumables["R11"], per day.
R11_DAY = dict(runs=16.77, tested=10.29, promoted=1.03, screening_builds=12.0, full_builds=1.03, mounts=20.6,
               promote_charge_g=684.0, rePowders=3, midis=4, furnaces=2, cubxls=2, sieve_wash=2, fte=5.2)
R11_SRC = "PR #332, bottleneck.py at cc31ddc: out/bottleneck.json ladder R11 (simulated) and consumables R11, per day"
RUN_FAIL_EVERY = 10          # timelapse PARAMS run_fail_every: one run in ten drips
BUILD_FAIL_EVERY = 7         # timelapse PARAMS build_fail_every: one screening build in seven fails
CHARGE_G = 300.0             # timelapse PARAMS charge_per_run
USABLE, FINES = 0.91, 0.17   # timelapse PARAMS usable_frac (< 250 um) and fines_frac (< 63 um), the Oct 27 run
SCREEN_G, FULL_G = 30.0, 440.0   # timelapse PARAMS screen_build_g, full_build_g
SAMPLE_G = 15.0              # notes/alloy_powder.md: "a retained sample of the sieved 20-63 um cut, about 15 g"
WELLS_A_NIGHT = 8            # DAL protocol.md section 4: eight wells and the stock blank, nine tubes a night
EDM_H = dict(edm=0.75, section=0.4, edm_full=1.0)     # timelapse STEPS, h a step
BUILD_LASER_H = dict(screen=3.0, full=6.0)            # timelapse STEPS: a 3 h build; print_full 8 h with inerting,
                                                       # cooling and unloading, about 6 h of it building (assumed)


def _timelapse_year() -> dict:
    m = json.loads((OUT / "timelapse_model.json").read_text())
    return m["totals"]["1 year"]


def _r11_day() -> tuple[dict, str]:
    p = OUT / "bottleneck.json"
    if not p.exists():
        return dict(R11_DAY), R11_SRC
    b = json.loads(p.read_text())
    sim = next(r for r in b["ladder"] if r["key"] == "R11")["simulated"]
    c = b["consumables"]["R11"]
    d = dict(R11_DAY, runs=sim["runs_per_day"], tested=sim["tested_per_day"], promoted=sim["promoted_per_day"],
             screening_builds=c["screening_plates"], full_builds=c["full_plates"], mounts=c["mounts"])
    return d, "out/bottleneck.json (PR #332's bottleneck.py), ladder R11 and consumables R11"


def units() -> dict:
    """Units of work a year in each schedule, and how each is counted."""
    y = _timelapse_year()
    d, r11_src = _r11_day()
    out = {}
    # ---- one a day: the finale's year as booked
    r0 = dict(runs=y["runs"], tested=y["tested"], promoted=y["promoted"], atomized=y["atomized"],
              screening_builds=y["tested"] * BUILD_FAIL_EVERY / (BUILD_FAIL_EVERY - 1), full_builds=y["promoted"],
              tensile=y["tensile"], spots=y["corrosion"], mounts=2 * y["tested"], polishes=y["tested"])
    r0["screen_runs"] = r0["runs"] - r0["promoted"] * 8 / (1 - 1 / RUN_FAIL_EVERY)
    r0["promo_runs"] = r0["runs"] - r0["screen_runs"]
    r0["promo_charge_g"] = CHARGE_G
    r0.update(rePowders=1, midis=1, furnaces=1, cubxls=1, sieve_wash=1, fte=1.0)
    # ---- ten a day: PR #332's R11, a day x 365
    r11 = {k: d[k] * 365 for k in ("runs", "tested", "promoted", "screening_builds", "full_builds", "mounts")}
    r11["atomized"] = r11["screening_builds"]
    r11["tensile"] = 4 * (r11["tested"] + r11["promoted"])          # 3 + 1 an alloy, 2 + 2 E8 a promoted one
    r11["spots"] = 2 * r11["tested"]
    r11["polishes"] = r11["tested"]
    r11["promo_runs"] = r11["promoted"] * 3 / (1 - 1 / RUN_FAIL_EVERY)  # 684 g charges: 3 more runs, not 8
    r11["screen_runs"] = r11["runs"] - r11["promo_runs"]
    r11["promo_charge_g"] = d["promote_charge_g"]
    r11.update({k: d[k] for k in ("rePowders", "midis", "furnaces", "cubxls", "sieve_wash", "fte")})
    for s in (r0, r11):
        s["good_runs"] = s["runs"] * (1 - 1 / RUN_FAIL_EVERY)
        s["failed_runs"] = s["runs"] / RUN_FAIL_EVERY
        s["charge_kg"] = (s["screen_runs"] * CHARGE_G + s["promo_runs"] * s["promo_charge_g"]) / 1000
        s["edm_h"] = EDM_H["edm"] * s["tested"] + EDM_H["section"] * s["tested"] + EDM_H["edm_full"] * s["promoted"]
        s["build_h"] = BUILD_LASER_H["screen"] * s["screening_builds"] + BUILD_LASER_H["full"] * s["full_builds"]
        s["nights"] = s["spots"] / WELLS_A_NIGHT
        s["crucibles"] = s["runs"] / 15                               # upkeep rp_crucible_stock: 15 runs a crucible
        s["weeks"] = 52.0
        s["person_days"] = 250 * s["fte"]
        # vacuums: one per family per rePowder (Al, Cu) and one per two printers (atom_vacuum.md "How many: three")
        s["vacuums"] = 2 * s["rePowders"] + max(1, s["midis"] // 2)
        s["one"] = 1.0
    out["one_a_day"] = dict(r0, source="out/timelapse_model.json totals['1 year'] (the finale's year, with upkeep "
                                       "and failures); screening builds = tested x 7/6, mounts and spots = 2 x tested")
    out["ten_a_day"] = dict(r11, source=r11_src + "; x 365")
    return out


# ===================================================================================================== the streams
# Routes, in the order the figure draws them (each a categorical slot, fixed order; dataviz palette, validated):
ROUTES = {
    "metal": ("EHS: combustible metal", "#eb6834"),
    "chem": ("EHS: chemical", "#e87ba4"),
    "universal": ("Universal waste", "#eda100"),
    "recycle": ("Recycle or reuse", "#2a78d6"),
    "drain": ("Drain, if EHS approves", "#1baf7a"),
    "trash": ("Ordinary trash", "#008300"),
    "vendor": ("Back to the vendor, or sent out", "#6250d6"),
}
IPA = 0.786                 # kg/L
CAN_G = 368.0               # Momentive BN Spray II, 13 oz (atom_bn.md, McMaster 10515K35)


def S(key, name, route, per, amount, unit, basis, kg_per_unit=1.0, workflow="", undecided=False):
    """A stream: `amount` of `unit` per `per` (a key of units()); kg_per_unit turns the unit into kg for the figure."""
    return dict(key=key, name=name, route=route, per=per, amount=amount, unit=unit, kg_per_unit=kg_per_unit,
                basis=basis, workflow=workflow, undecided=undecided)


STREAMS = [
    # ------------------------------------------------------------------ combustible metal: dry, sealed, grounded
    S("fines_vac", "Atomizer and sieve-cell fines, vacuumed", "metal", "runs", 7.0, "g",
      "assumed: 5 g a run from the chamber, plate, cone and bowl after the brush (DAL SOP 'Powder collection'; PR 80's "
      "SOP: 'tens of grams a week' at the lab's pace now) plus 2 g a run of spills in the sieve cell's downdraft "
      "enclosure", kg_per_unit=1e-3, workflow="chapter 2 (atomize), chapter 3 (sieve); atom_vacuum"),
    S("liners", "Vacuum liners (the plastic round the fines)", "metal", "vacuums", 52.0, "liners",
      "PR 80's SOP: a liner after each use or weekly, transferred to EHS at least every 2 weeks; 24 x 36 in, 4 mil "
      "conductive PE, about 0.1 kg (computed)", kg_per_unit=0.1, workflow="atom_vacuum"),
    S("char_powder", "Characterization powder (Mastersizer, XRF, XRD, SEM)", "metal", "atomized", 10.0, "g",
      "alloy_powder.md: about 5 g into the Aero S, whose extractor keeps it; an XRF cup about 4 g and the XRD holder "
      "about 1 g (assumed); stubs are mg", kg_per_unit=1e-3, workflow="chapter 4 (powder checked)"),
    S("lpbf_screen", "LPBF powder left from screening builds", "metal", "screening_builds", 26.0, "g",
      "the 55 mm kit's 30 g (DAL #138) less about 4 g in the miniature specimens (assumed); each alloy's leftover is "
      "small, spattered and unique, so it is waste", kg_per_unit=1e-3, workflow="chapter 5 (print, depowder)"),
    S("lpbf_full", "LPBF powder left from full plates", "metal", "full_builds", 380.0, "g",
      "the 170 mm cylinder's 440 g (powder-doser#31) less about 60 g of E8 bars (assumed); sieved and kept while the "
      "alloy may be rebuilt, then waste", kg_per_unit=1e-3, workflow="chapter 5", undecided=True),
    S("filters", "Filters loaded with metal fines", "metal", "one", 1.0, "kg",
      "a year, one a day: the rePowder's safety and pump filters, inspected every 20 h of running and replaced when "
      "worn (AMAZEMET manual via DAL PR 178; one in four assumed: 21 x 0.05 kg), its main (HEPA) filter about every "
      "two months, backfilled with sand in a grounded container (6 x 6 kg with the sand), Nilfisk main "
      "and two HEPAs a year per vacuum (3 x 1.5 kg), the MIDI's circulation filter every 1,000 build hours (upkeep "
      "ac_filter: 1.3 x 5 kg, wetted), the depowdering box's monthly filter (13 x 0.3 kg), the Mastersizer "
      "extractor's (1 kg): about 53 kg; half fixed and half scaled by runs for ten a day", kg_per_unit=1.0, workflow="upkeep.py"),
    S("surplus", "Surplus powder: the 63-250 um cuts", "metal", "one", 1.0, "kg",
      "74 % of every good run's charge (USABLE 91 % less FINES 17 %, DAL #219): 222 g of a 300 g run; kept in tray O's "
      "jars until the lab decides (archive, DED, re-melt, recycle or EHS)", kg_per_unit=1.0,
      workflow="chapter 3 (sieved cuts)", undecided=True),
    # ------------------------------------------------------------------ solid metal: recycle by family
    S("splats", "Splats, flakes over 250 um, bowl metal, skulls", "recycle", "good_runs", 31.0, "g",
      "7 % of the charge over 250 um or on the bowl (the rest of the 9 % is in the vacuumed fines), plus a 10 g skull "
      "(DAL SOP 178: 'slag always remains at the bottom'; un-atomized metal is feedstock, not waste)",
      kg_per_unit=1e-3, workflow="chapter 2, atom_bn"),
    S("drips", "Failed runs: the metal that dripped", "recycle", "failed_runs", 270.0, "g",
      "one run in ten drips instead of atomizing (timelapse run_fail_every); about 90 % of the charge comes back solid "
      "(assumed)", kg_per_unit=1e-3, workflow="chapter 2"),
    S("edm_wire", "Spent EDM wire (brass)", "recycle", "edm_h", 15.9 / 120, "kg",
      "upkeep edm_wire: a 15.9 kg spool of 0.25 mm brass every 120 h of EDM work", kg_per_unit=1.0,
      workflow="chapters 5-6 (cut, section)"),
    S("specimens", "Tested specimens, sections, plates retired", "recycle", "tested", 40.0, "g",
      "4 miniature specimens (about 5 g each), two sections and a share of a 55 mm build plate re-used ten times "
      "(assumed); kept as records first", kg_per_unit=1e-3, workflow="chapters 5-7"),
    # ------------------------------------------------------------------ chemical (EHS)
    S("ipa_sieve", "Sieve-wash IPA with Al fines", "chem", "runs", 38.0, "mL",
      "alloy_print.md: the wash vessel holds a few hundred mL; changed weekly (upkeep sv_ipa), 0.5 L for about 13 runs "
      "a week (assumed); 'the rinse slurry is hazardous waste, kept wet'", kg_per_unit=IPA * 1e-3,
      workflow="chapter 3 (wash module)"),
    S("ipa_misc", "IPA from the bar rinse and wipes", "chem", "edm_h", 0.03, "L",
      "the bar-rinse jar beside the EDM (alloy_workflow.md), about 0.1 L a week, and IPA-wet wipes for seals and "
      "tools (assumed), as L per EDM hour", kg_per_unit=IPA, workflow="chapter 5 (rinse), atomizer seals"),
    S("formwash", "Form Wash IPA with resin", "chem", "weeks", 0.3, "L",
      "tray G, off the route: a bucket of about 8.6 L changed at 10 % resin (Formlabs), about twice a year at ten "
      "prints a week (assumed); the same at ten a day", kg_per_unit=IPA, workflow="tray G (fabrication)"),
    S("resin", "Uncured resin: tank dregs, failed prints", "chem", "weeks", 0.02, "L",
      "tray G, off the route: a tank's dregs twice a year per Form 4 and uncured failures (assumed); cured supports "
      "go in the trash", kg_per_unit=1.1, workflow="tray G"),
    S("weck", "Weck's etchant, spent", "chem", "tested", 5.0, "mL",
      "lab_r8.md: 4 g KMnO4 + 1 g NaOH in 100 mL water, mixed fresh; 25 mL a session, one session for every 5 alloys "
      "(assumed: most mounts are imaged as polished)", kg_per_unit=1.04e-3, workflow="fume hood (tray / ducted)"),
    S("icp_acid", "Acidified ICP leftovers and tube-leach acid", "chem", "nights", 0.14, "L",
      "DAL protocol.md: 9 tubes of 320 uL a night at 62 mM HNO3, 220 uL of each left after the 10x dilution; the "
      "tubes leached overnight in 2 % HNO3, about 1 L a week (assumed)", kg_per_unit=1.0,
      workflow="tray A (OT-2, CubXL)"),
    S("solder", "Solder paste, stencil wipes", "chem", "one", 0.3, "kg",
      "tray H, off the route: an expired jar and the stencil's wipes a year (assumed)", kg_per_unit=1.0,
      workflow="tray H (PCB)"),
    S("pump_oil", "Vacuum pump oil", "recycle", "rePowders", 6.0, "L",
      "upkeep rp_pump_oil every 91 days (about 1 L, assumed) and the glovebox pump twice a year, per rePowder; used "
      "oil is recycled",
      kg_per_unit=0.87, workflow="upkeep.py"),
    # ------------------------------------------------------------------ universal waste
    S("aerosol", "BN spray cans", "universal", "runs", 13.0 / CAN_G, "cans",
      "atom_bn.md: a touch-up of two light passes of 0.35 s bursts and 4 s inverted, about 12 g a run, and about 30 g "
      "a new crucible every 15 runs (assumed), from 368 g cans", kg_per_unit=0.12, workflow="atom_bn"),
    S("batteries", "Batteries: UPS, MiR, small cells", "universal", "one", 1.0, "kg",
      "averaged over their lives: 12 LiFePO4 UPS batteries at up to 10 years (Vertiv, ups.md: 1.2 a year, about 5 kg "
      "each), the MiR250s' Li-NMC packs at 3,000 cycles (upkeep: 2.5 and 4.9 years, about 11 kg each), 1 kg of small "
      "cells; none in the first year. Ten a day x 1.86, PR #332's equipment scale", kg_per_unit=1.0,
      workflow="ups.md, upkeep.py"),
    # ------------------------------------------------------------------ drain, if EHS approves (else collected)
    S("polish_water", "Polishing water and slurry", "drain", "polishes", 2.5, "L",
      "the PX500's waste tank, emptied weekly (upkeep px_waste): five SiC grits with water and a rinse after each "
      "(the lab's SOP), alumina and OP-U; about 2.5 L a polish (assumed)", kg_per_unit=1.0,
      workflow="chapter 6 (polish)"),
    S("seawater", "Seawater with sulfide (stocks, rinse cups)", "chem", "nights", 0.03, "L",
      "DAL protocol.md: the 10 and 0.1 mg/L S stocks fresh each night in ASTM D1141 water at pH 8.2, two 4 mL rinse "
      "cups; about 30 mL a night (assumed). Collected (it is litres a year), and never mixed with the acid",
      kg_per_unit=1.0, workflow="tray A"),
    S("quench", "Quench water", "drain", "furnaces", 98.0, "L",
      "r8_test QUENCH: 240 x 200 x 170 mm of water (8.2 L), changed monthly (assumed)", kg_per_unit=1.0,
      workflow="chapter 5 (heat treat)"),
    S("edm_water", "EDM dielectric water (tank change)", "drain", "edm_h", 550.0 / 1000.0, "L",
      "a 550 L tank (alpha-C400iC, a third-party listing) cleaned every 1,000 h (upkeep's Langenhorst source); "
      "filtered and deionized, so mostly clean water", kg_per_unit=1.0, workflow="wire EDM"),
    # ------------------------------------------------------------------ trash (non-hazardous, if EHS agrees)
    S("sic", "SiC papers, cloths", "trash", "polishes", 45.0, "g",
      "the lab's SOP: 320, 400, 600, 800 and 1200 grit, single use, about 8 g each, and a cloth every 40 polishes "
      "(upkeep px_restock)", kg_per_unit=1e-3, workflow="chapter 6"),
    S("mounts", "Phenolic mounts, once archived", "trash", "tested", 20.0, "g",
      "upkeep mx_restock: about 20 g of phenolic a hot mount (LECO, UMich SOP); the steel mounts are re-used",
      kg_per_unit=1e-3, workflow="chapter 6"),
    S("crucibles", "Graphite crucibles, BN flakes, insulation", "trash", "runs", 50.0, "g",
      "upkeep: a crucible and nozzle holder every 15 runs (about 0.6 kg), the insulation set every 60 (0.3 kg), the "
      "thermocouple sheath every 40 (0.05 kg), and the BN flakes scraped off at each touch-up (atom_bn.md; about 2 g)",
      kg_per_unit=1e-3, workflow="atom_crucible, atom_bn, upkeep.py"),
    S("ppe", "Gloves, wipes, N95s, tips, tubes", "trash", "person_days", 0.12, "kg",
      "assumed: six pairs of nitrile gloves, twenty wipes and an N95 a person-day; with the CubXL's 17 tips, the "
      "OT-2's and 9 tubes a night. Anything with visible powder goes in the metal pail", kg_per_unit=1.0,
      workflow="every station"),
    S("edm_resin", "EDM resin and filter cartridges", "vendor", "edm_h", 1.0 / 200 * 12 + 2.0 / 600 * 4, "kg",
      "upkeep: the deionizing resin every 200 h (about 10 L, 12 kg wet; a 20 L ion exchanger is FANUC's option on the "
      "older alpha-0iC) and two paper filters every 600 h (about 4 kg each with sludge); the resin goes back for "
      "regeneration, the filters dried and to EHS", kg_per_unit=1.0, workflow="wire EDM"),
    S("icp_out", "ICP-MS samples, to the Spectroscopic Facility", "vendor", "nights", 0.009, "L",
      "the OT-2's 10x dilutions, 1.0 mL a tube, 9 a night (ot2_corrosion.md); the facility disposes of them",
      kg_per_unit=1.0, workflow="tray A"),
]


def filters_kg(u: dict, r0: dict) -> float:
    """The filters' year (stream "filters"): one a day as itemised in its basis, scaled for ten a day."""
    base = 21 * 0.05 + 6 * 6.0 + 3 * 1.5 + 1.3 * 5.0 + 13 * 0.3 + 1.0
    return base * (0.5 + 0.5 * u["runs"] / r0["runs"]) if u is not r0 else base


def surplus_kg(u: dict) -> float:
    coarse = USABLE - FINES
    screen_good = u["screen_runs"] * (1 - 1 / RUN_FAIL_EVERY)
    promo_good = u["promo_runs"] * (1 - 1 / RUN_FAIL_EVERY)
    left_fines = max(0.0, CHARGE_G * FINES - SCREEN_G - SAMPLE_G)            # 6 g of fines a screening run
    return (screen_good * (CHARGE_G * coarse + left_fines) + promo_good * u["promo_charge_g"] * coarse) / 1000


def batteries_kg() -> float:
    return 12 / 10 * 5.0 + (1 / 2.5 + 1 / 4.9) * 11.0 + 1.0


def amounts() -> dict:
    us = units()
    r0 = us["one_a_day"]
    res = {"units": us, "streams": []}
    for s in STREAMS:
        row = {k: v for k, v in s.items()}
        for name, u in us.items():
            if s["key"] == "filters":
                native = filters_kg(u, r0)
            elif s["key"] == "surplus":
                native = surplus_kg(u)
            elif s["key"] == "batteries":
                native = batteries_kg() * (1 if u is r0 else 1.86)
            else:
                native = s["amount"] * u[s["per"]]
            row[name] = dict(year=round(native, 3), day=round(native / 365, 4), unit=s["unit"],
                             kg_year=round(native * s["kg_per_unit"], 2))
        res["streams"].append(row)
    # ---- totals by route (kg a year)
    for name in us:
        tot = {}
        for row in res["streams"]:
            tot[row["route"]] = tot.get(row["route"], 0.0) + row[name]["kg_year"]
        res.setdefault("route_kg_year", {})[name] = {k: round(v, 1) for k, v in tot.items()}
    res["charge"] = charge_split()
    res["pickups"] = pickups(res)
    return res


# ===================================================================================================== containers, pickups
# Risk Management's containers (RMS ULM procedures and FAQ, read through archive.org snapshots, 2026): 5 gal Acid
# Aqueous, Base Aqueous and Flammable Solvents containers, 5 gal buckets for solids; "Schedule a pickup when a container
# is 80% full"; at most 55 gal of unwanted material in a lab; nothing older than 12 months.
GAL = 3.785
FULL = 0.8                                   # RMS: request a pickup at 80 % full
LAB_LIMIT_L = 55 * GAL                       # RMS / Subpart K: 55 gal of unwanted material in a laboratory
POWDER_KG_L = 1.4                            # bulk density of the Al alloy powders, kg/L (assumed: AlSi10Mg taps ~1.4-1.5)
LINER_L = 1.5                                # a sealed liner with its fines, L (assumed)
CONTAINERS = [
    # (what, container, volume L, streams (key, how many L per native unit))
    ("waste powder, LPBF leftovers, characterization powder", "5 gal solids bucket (combustible metal)", 5 * GAL,
     [("lpbf_screen", 1e-3 / POWDER_KG_L), ("char_powder", 1e-3 / POWDER_KG_L)]),          # g -> L
    ("sealed vacuum liners", "5 gal solids bucket via the grounded pail", 5 * GAL, [("liners", LINER_L)]),
    ("filters in sand", "grounded can, one a filter (counted as 4 L each)", 4.0, [("filters", 4.0 / 6.0)]),
    ("IPA: sieve wash with Al fines", "Flammable Solvents, 5 gal (or a 2.5 gal safety can)", 5 * GAL,
     [("ipa_sieve", 1e-3)]),                                                              # mL -> L
    ("IPA: bar rinse and wipes", "Flammable Solvents, 5 gal", 5 * GAL, [("ipa_misc", 1.0)]),
    ("IPA with resin (Form Wash)", "Flammable Solvents, 5 gal", 5 * GAL, [("formwash", 1.0)]),
    ("acidified ICP leftovers, leach acid", "Acid Aqueous, 5 gal", 5 * GAL, [("icp_acid", 1.0)]),
    ("Weck's, spent", "1 L bottle (base, oxidizer)", 1.0, [("weck", 1e-3)]),
    ("seawater with sulfide", "1 L bottle on tray A", 1.0, [("seawater", 1.0)]),
    # undecided: only if the lab discards them
    ("IF DISCARDED: surplus powder and full plates' leftovers", "5 gal solids bucket (combustible metal)", 5 * GAL,
     [("surplus", 1.0 / POWDER_KG_L), ("lpbf_full", 1e-3 / POWDER_KG_L)]),
]


def pickups(res: dict) -> dict:
    """Container loads a year by kind, and the unwanted material standing in the lab at a pickup interval."""
    by = {r["key"]: r for r in res["streams"]}
    out = {}
    for name in res["units"]:
        rows, litres_year = [], 0.0
        for what, cont, vol, parts in CONTAINERS:
            L = sum(by[k][name]["year"] * f for k, f in parts)
            loads = L / (vol * FULL)
            rows.append(dict(what=what, container=cont, litres_year=round(L, 1),
                             loads_year=round(max(loads, 1.0 if L > 0 else 0.0), 1)))
            litres_year += L
        # the lab's standing stock just before a pickup, every `days`, counting every open container as full
        decided = [r for r in rows if not r["what"].startswith("IF DISCARDED")]
        stand = {d: round(sum(r["litres_year"] * d / 365 for r in decided), 0) for d in (7, 14, 30, 90)}
        stand_all = {d: round(sum(r["litres_year"] * d / 365 for r in rows), 0) for d in (7, 14, 30, 90)}
        out[name] = dict(containers=rows, litres_year=round(sum(r["litres_year"] for r in decided), 0),
                         litres_year_with_surplus=round(litres_year, 0),
                         loads_year=round(sum(r["loads_year"] for r in decided), 0),
                         loads_year_with_surplus=round(sum(r["loads_year"] for r in rows), 0),
                         standing_litres_before_pickup=stand, standing_litres_with_surplus=stand_all,
                         lab_limit_litres=round(LAB_LIMIT_L))
    return out


def charge_split() -> list:
    """Where a good screening run's 300 g goes (panel a): the print, the sample, and what is left."""
    fines = CHARGE_G * FINES
    left = fines - SCREEN_G - SAMPLE_G
    coarse = CHARGE_G * (USABLE - FINES)
    over = CHARGE_G * (1 - USABLE)
    vac = 5.0
    return [
        dict(part="the print (55 mm kit)", g=SCREEN_G, route=None),
        dict(part="the powder checks", g=SAMPLE_G, route="metal"),
        dict(part="fines kept", g=round(left, 1), route="metal", undecided=True),
        dict(part="63-250 um, surplus", g=round(coarse, 1), route="metal", undecided=True),
        dict(part="over 250 um, splats", g=round(over - vac, 1), route="recycle"),
        dict(part="vacuumed fines", g=vac, route="metal"),
    ]


# ===================================================================================================== outputs
def fmt(v: float, unit: str) -> str:
    if unit == "g" and v >= 1000:
        v, unit = v / 1000, "kg"
    if unit == "mL" and v >= 1000:
        v, unit = v / 1000, "L"
    if v >= 100:
        s = f"{v:,.0f}"
    elif v >= 10:
        s = f"{v:.0f}"
    elif v >= 1:
        s = f"{v:.1f}"
    else:
        s = f"{v:.2g}"
    return f"{s} {unit}"


def table(res: dict | None = None) -> str:
    res = res or amounts()
    lines = [f"{'stream':52s} {'per unit':>16s} {'1/day: day':>12s} {'year':>12s} {'10/day: day':>12s} {'year':>12s}"]
    for r in res["streams"]:
        a, b = r["one_a_day"], r["ten_a_day"]
        per = "" if r["per"] in ("one",) else f"{fmt(r['amount'], r['unit'])}/{r['per']}"
        lines.append(f"{r['name'][:52]:52s} {per[:16]:>16s} {fmt(a['day'], a['unit']):>12s} {fmt(a['year'], a['unit']):>12s} "
                     f"{fmt(b['day'], b['unit']):>12s} {fmt(b['year'], b['unit']):>12s}")
    for name, tot in res["route_kg_year"].items():
        lines.append(f"{name}: " + ", ".join(f"{ROUTES[k][0]} {v:,.0f} kg" for k, v in tot.items()))
    return "\n".join(lines)


PER = {"runs": "an atomizer run", "good_runs": "a good run", "failed_runs": "a failed run", "atomized": "an alloy atomized",
       "screening_builds": "a screening build", "full_builds": "a full plate", "tested": "an alloy tested",
       "polishes": "a polish", "nights": "a corrosion night", "edm_h": "an EDM hour", "weeks": "a week",
       "vacuums": "a vacuum a year", "rePowders": "a rePowder a year", "furnaces": "a furnace a year",
       "person_days": "a person-day", "one": "a year"}


def markdown(res: dict | None = None) -> str:
    """The notes' table: per unit of work, a day and a year at one a day and at ten (native units)."""
    res = res or amounts()
    out = ["| Stream | Goes to | Per unit of work | One a day: a day | a year | Ten a day: a day | a year |",
           "|---|---|---|---|---|---|---|"]
    for r in sorted(res["streams"], key=lambda r: (list(ROUTES).index(r["route"]), -r["ten_a_day"]["kg_year"])):
        a, b = r["one_a_day"], r["ten_a_day"]
        per = "see basis" if r["per"] == "one" or r["key"] in ("filters", "surplus", "batteries") else \
            f"{fmt(r['amount'], r['unit'])} {PER[r['per']]}"
        name = r["name"] + (" *(undecided)*" if r.get("undecided") else "")
        out.append(f"| {name} | {ROUTES[r['route']][0]} | {per} | {fmt(a['day'], a['unit'])} | "
                   f"{fmt(a['year'], a['unit'])} | {fmt(b['day'], b['unit'])} | {fmt(b['year'], b['unit'])} |")
    tot = res["route_kg_year"]
    out.append("")
    out.append("| Goes to | One a day, kg a year | Ten a day, kg a year |")
    out.append("|---|---|---|")
    for k in ROUTES:
        out.append(f"| {ROUTES[k][0]} | {tot['one_a_day'].get(k, 0):,.0f} | {tot['ten_a_day'].get(k, 0):,.0f} |")
    return "\n".join(out)


def figure(res: dict | None = None, path: Path | None = None) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D

    res = res or amounts()
    path = path or OUT / "waste_streams.png"
    ink, ink2, ink3, grid, surf = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#fcfcfb"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.edgecolor": grid,
                         "axes.labelcolor": ink2, "xtick.color": ink2, "ytick.color": ink2, "text.color": ink,
                         "hatch.color": surf, "hatch.linewidth": 1.2})
    rows = sorted(res["streams"], key=lambda r: (list(ROUTES).index(r["route"]), -r["ten_a_day"]["kg_year"]))
    n = len(rows)
    W, row_h = 13.0, 0.33
    head, a_h, gap_a, leg_h, b_h, foot = 1.0, 1.75, 0.2, 0.75, n * row_h, 0.75
    H = head + a_h + gap_a + leg_h + b_h + foot
    fig = plt.figure(figsize=(W, H), dpi=150, facecolor=surf)
    L, R = 3.75 / W, 1 - 0.35 / W

    def box(top_in, h_in, left=L):
        return [left, 1 - (top_in + h_in) / H, R - left, h_in / H]

    fig.text(0.18 / W, 1 - 0.22 / H, "The vertical lab's waste: every stream, a year, at one fully tested alloy a day "
             "and at ten", fontsize=14, fontweight="bold", va="top", color=ink)
    fig.text(0.18 / W, 1 - 0.58 / H,
             "Modelled, not weighed: an amount per unit of work (notes/waste.md) times the finale's year (667 atomizer "
             "runs, 309 alloys fully tested) and PR #332's rung R11\n(16.8 runs and 10.3 alloys a day). "
             "Colour is where each stream goes.", fontsize=9.5, va="top", color=ink2, linespacing=1.35)

    # ---- panel a: one good screening run's 300 g
    ax0 = fig.add_axes(box(head + 0.25, 0.42))
    ax0.set_facecolor(surf)
    for sp in ("top", "right", "left", "bottom"):
        ax0.spines[sp].set_visible(False)
    x = 0.0
    parts = res["charge"]
    spans = []
    for p in parts:
        col = ROUTES[p["route"]][1] if p["route"] else "#c3c2b7"
        ax0.barh(0, p["g"], left=x, height=1.0, color=col, edgecolor=surf, linewidth=2,
                 hatch="////" if p.get("undecided") else None)
        spans.append((x, x + p["g"], p))
        x += p["g"]
    ax0.set_xlim(0, CHARGE_G)
    ax0.set_ylim(-0.5, 0.5)
    ax0.set_yticks([])
    ax0.set_xticks([])
    # labels: the big segment inside; every segment numbered under the bar, and a key below in the same order (the
    # thin segments can't carry a label, and leader lines to six labels crossed each other)
    trans = ax0.get_xaxis_transform()
    key = []
    for i, (x0, x1, p) in enumerate(spans, 1):
        if p["g"] >= 100:
            ax0.text((x0 + x1) / 2, 0, f"{p['part']}: {p['g']:.0f} g  (kept until the lab decides)", ha="center",
                     va="center", fontsize=9, color=ink, fontweight="bold",
                     bbox=dict(boxstyle="round,pad=0.25", facecolor=surf, edgecolor="none"))
        ax0.text((x0 + x1) / 2, -0.62, str(i), transform=trans, ha="center", va="top", fontsize=8.5, color=ink2,
                 fontweight="bold")
        key.append(f"{i}  {p['part']}, {p['g']:.0f} g")
    ax0.text(0, -1.25, "     ".join(key[:3]) + "\n" + "     ".join(key[3:]), transform=trans, ha="left", va="top",
             fontsize=8.5, color=ink2, linespacing=1.5)
    fig.text(0.18 / W, 1 - (head + 0.15) / H, "a. Where a 300 g charge goes", fontsize=10.5, fontweight="bold",
             va="top", color=ink)
    fig.text(0.18 / W, 1 - (head + 0.45) / H,
             "A good screening run. Only 17 % of the\ncharge is under 63 um, the printer's cut:\n"
             "three quarters of every run is coarse\npowder the route never uses.", fontsize=8.5, va="top",
             color=ink2, linespacing=1.35)

    # ---- legend between the panels
    handles = [Patch(facecolor=ROUTES[k][1], edgecolor="none", label=ROUTES[k][0]) for k in ROUTES]
    handles += [Line2D([], [], marker="o", ls="none", markerfacecolor=surf, markeredgecolor=ink2, markersize=7,
                       markeredgewidth=2, label="one a day (the finale's year)"),
                Line2D([], [], marker="o", ls="none", markerfacecolor=ink2, markeredgecolor=surf, markersize=8,
                       label="ten a day (PR #332, R11)"),
                Patch(facecolor=ink3, edgecolor=surf, hatch="////", label="undecided: kept until the lab decides")]
    top_b = head + a_h + gap_a
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(L, 1 - top_b / H), ncol=4, frameon=False,
               fontsize=8.5, handlelength=1.6, columnspacing=1.6, borderaxespad=0)
    fig.text(0.18 / W, 1 - top_b / H, "b. Every stream, kg a year", fontsize=10.5, fontweight="bold", va="top",
             color=ink)

    # ---- panel b: every stream, kg a year, one a day (hollow) and ten a day (filled)
    ax = fig.add_axes(box(top_b + leg_h, b_h))
    ax.set_facecolor(surf)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(grid)
    ys = list(range(n))[::-1]
    prev = None
    for y, r in zip(ys, rows):
        col = ROUTES[r["route"]][1]
        a, b = max(r["one_a_day"]["kg_year"], 0.01), max(r["ten_a_day"]["kg_year"], 0.01)
        ax.plot([a, b], [y, y], color=col, lw=2, solid_capstyle="round", zorder=2, alpha=0.5)
        ax.scatter([a], [y], s=46, facecolor=surf, edgecolor=col, linewidth=2, zorder=3)
        ax.scatter([b], [y], s=60, facecolor=col, edgecolor=surf, linewidth=1.6, zorder=4,
                   hatch="////" if r.get("undecided") else None)
        name = r["name"] + ("  (undecided)" if r.get("undecided") else "")
        ax.text(-0.012, y, name, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=9, color=ink)
        if prev is not None and prev != r["route"]:
            ax.axhline(y + 0.5, color=grid, lw=1, zorder=0)
        prev = r["route"]
        if b >= 300 or r["key"] in ("fines_vac", "liners", "lpbf_screen", "weck"):
            ax.text(b * 1.3, y, f"{a:,.0f} \u2192 {b:,.0f} kg" if a >= 1 else f"{a:.1f} \u2192 {b:,.0f} kg",
                    va="center", ha="left", fontsize=8, color=ink2)
    ax.set_xscale("log")
    ax.set_xlim(0.05, 6e4)
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_yticks([])
    ax.grid(axis="x", color=grid, lw=1)
    ax.set_axisbelow(True)
    ticks = [0.1, 1, 10, 100, 1000, 10000]
    ax.set_xticks(ticks)
    ax.set_xticklabels(["0.1", "1", "10", "100", "1,000", "10,000 kg a year"])
    ax.minorticks_off()
    ax.tick_params(axis="x", length=0, labelsize=8.5)
    tot0 = sum(res["route_kg_year"]["one_a_day"].values())
    tot1 = sum(res["route_kg_year"]["ten_a_day"].values())
    m0 = res["route_kg_year"]["one_a_day"]["metal"]
    m1 = res["route_kg_year"]["ten_a_day"]["metal"]
    fig.text(0.18 / W, 0.22 / H, f"All streams, liquids by mass: about {tot0:,.0f} kg a year at one a day, "
             f"{tot1 / 1000:,.1f} t at ten. Combustible metal through EHS: {m0:,.0f} kg and {m1 / 1000:,.1f} t, most "
             f"of it the undecided surplus powder.\nwaste.py; each stream's basis is in out/waste_model.json and "
             f"notes/waste.md.", fontsize=8.5, color=ink3, va="bottom", linespacing=1.4)
    fig.savefig(path, dpi=150, facecolor=surf)
    plt.close(fig)
    return path


def main(argv: list[str]) -> None:
    res = amounts()
    if argv[:1] == ["table"]:
        print(table(res))
        return
    if argv[:1] == ["markdown"]:
        print(markdown(res))
        return
    if argv[:1] == ["pickups"]:
        print(json.dumps(res["pickups"], indent=1))
        return
    OUT.mkdir(exist_ok=True)
    res["what"] = ("The vertical lab's waste streams (waste.py): an amount per unit of work, times the units in a year at "
                   "one fully tested alloy a day (the finale's year) and at ten (PR #332's R11). Modelled, not "
                   "weighed; each stream's basis says what is sourced and what is assumed.")
    res["routes"] = {k: v[0] for k, v in ROUTES.items()}
    (OUT / "waste_model.json").write_text(json.dumps(res, indent=1) + "\n")
    print(table(res))
    print(figure(res))


if __name__ == "__main__":
    main(sys.argv[1:])
