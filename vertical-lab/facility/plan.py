"""What the $200M buys: the facility's counts (layout.py) against unit costs, and the building.

    python3 facility/plan.py            # -> out/budget.json, out/budget.md

**A plan, not a quote.** Every unit cost below says where it comes from: a published price or a procurement record
where one was found, otherwise an estimate of ours, marked so. The counts are what the film draws. The building is
priced per square foot from published ranges for US high-bay advanced-manufacturing and R&D space. Soft costs and the
contingency take what is left to $200M, and the check is that this remainder lands in a normal range (10-25 %).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import layout as LY  # noqa: E402

OUT = HERE / "out"
TOTAL = 200.0e6
FT2_PER_M2 = 10.7639

# unit costs, USD: (low, high, source, kind). kind: "published" (a list price, quote or award found), "estimate" (ours)
UNIT = {
    "shuttle": (270e3, 400e3, "Kardex Shuttle XP 500, 10.7 m, 2450 x 864 mm trays: Kardex's own buying guide (Dec 2025) "
                              "gives $6-8k per vertical foot, $210-280k at 35 ft; federal orders for XP 500s with the "
                              "same trays, 4.85-5.85 m tall, were $103-108k (2018-19). Plus ours on about 15 powered "
                              "trays each: a CombiTac dock and plate and a UPS (notes/coupling.md, notes/ups.md), "
                              "about $60-120k", "published + estimate"),
    "tray_instruments": (0.9e6, 1.6e6, "a Shuttle's worth of the pilot cell's tray instruments (SEM, XRD, XRF, "
                                       "laser diffraction, nanoindenter, PIP, VHX, furnace, polisher, mounting press, "
                                       "CubXL, OT-2...), for half the hall's Shuttles; the other half store jars, cups "
                                       "and samples", "estimate"),
    "repowder": (290e3, 440e3, "AMAZEMET rePowder: NASA $286,720 (2023), NIST $321,595 (2024), Hochschule Aalen "
                               "EUR 407,700 (2025), procurement records", "published"),
    "sieve_cell": (40e3, 80e3, "sieve shaker, tipper, wash module and downdraft enclosure (ours, alloy_print.py)",
                   "estimate"),
    "aconity": (600e3, 800e3, "Aconity3D AconityMIDI: EU awards EUR 350-456k (2019-22) and EUR 675k (2026); a "
                              "multi-laser MIDI+ at Nottingham GBP 893k (2021)", "published"),
    "eos_m400": (2.2e6, 2.5e6, "EOS M 400-4: a US Navy order with installation, training and consumables, $2.36M "
                               "(2023)", "published"),
    "gas_atomizer": (1.0e6, 2.0e6, "lab/pilot close-coupled VIGA (HERMIGA 100/10 VI class), installed: a Blue Power "
                                   "VIGA for Hochschule Trier EUR 533,605 (2025); Swerim's 4-12 L R&D atomizer about "
                                   "EUR 2M; an ALD VIGA 35 production unit $3.5M new (2022)", "published + estimate"),
    "instron_floor": (180e3, 260e3, "Instron 68FM-100: federal awards $146-208k (2022-24), plus a furnace (ours, "
                                    "$40-60k)", "published + estimate"),
    "instron_small": (40e3, 70e3, "Instron 68SC-2", "estimate"),
    "wire_edm": (200e3, 300e3, "wire EDM: federal awards for Sodick, FANUC, Mitsubishi, GF and Makino machines, "
                               "$200-302k (2020-26)", "published"),
    "ded": (400e3, 700e3, "InssTek MX-Lab", "estimate"),
    "meltio_cell": (250e3, 450e3, "Meltio robot cell", "estimate"),
    "fumehood": (25e3, 60e3, "ducted fume hood, installed", "estimate"),
    "packaging": (40e3, 80e3, "packaging station (labellers, sealer, scale)", "estimate"),
    "glovebox": (40e3, 90e3, "inert glovebox with purifier", "estimate"),
    "units": (120e3, 160e3, "MiR250 $59-65k (US distributors, 2026), UR10e $47-51k (NASA, 2022-23; the UR12e lists "
                            "at about $45k), Robotiq 2F-85 $5-6k; plus ours: cabinet, cameras, Class D unit, "
                            "integration", "published + estimate"),
}
BUILDING_PER_FT2 = (600.0, 900.0, "total project cost of a US high-bay advanced-manufacturing / R&D building: "
                                  "Virginia's 2026 cost database $484-503/ft2 for an engineering dry lab; Purdue's "
                                  "hypersonics high bay about $630/ft2; LSU's planned manufacturing building about "
                                  "$730/ft2; Texas's standard for a general lab $854/ft2", "published")
SITE = (8e6, 14e6, "bulk argon and nitrogen (federal tank-and-installation awards $79-248k a station, plus "
                   "the piping), power service and switchgear, chillers, dust collection and explosion protection for "
                   "Al powder, IT and the data store", "estimate")


def area_m2() -> float:
    B = LY.BUILDING
    return (B["x1"] - B["x0"]) * (B["y1"] - B["y0"]) / 1e6


def budget() -> dict:
    c = LY.counts()
    rows = []

    def add(what, n, key=None, lo=None, hi=None, src="", kind=""):
        if key is not None:
            lo, hi, src, kind = UNIT[key]
        mid = (lo + hi) / 2
        rows.append(dict(what=what, n=n, unit_low=lo, unit_high=hi, usd_m=round(n * mid / 1e6, 1),
                         low_m=round(n * lo / 1e6, 1), high_m=round(n * hi / 1e6, 1), source=src, kind=kind))

    add(f"{c['shuttle']} Kardex Shuttles, 35 ft, docks and UPSs on every powered tray", c["shuttle"], "shuttle")
    add(f"Tray instruments for {math.ceil(c['shuttle'] / 2)} of them", math.ceil(c["shuttle"] / 2), "tray_instruments")
    add(f"{c['repowder']} AMAZEMET rePowder ultrasonic atomizers", c["repowder"], "repowder")
    add(f"{c['sieve_cell']} sieving and wash cells", c["sieve_cell"], "sieve_cell")
    add(f"{c['gas_atomizer']} gas atomizers, HERMIGA 100/10 class", c["gas_atomizer"], "gas_atomizer")
    add(f"{c['aconity']} Aconity MIDI laser powder-bed printers", c["aconity"], "aconity")
    add(f"{c['eos_m400']} EOS M 400-4 large-format printers", c["eos_m400"], "eos_m400")
    add(f"{c['instron_floor']} Instron 68FM-100 frames with furnaces, 1 68SC-2",
        c["instron_floor"], "instron_floor")
    add(f"{c['wire_edm']} wire EDMs", c["wire_edm"], "wire_edm")
    add(f"{c['ded']} DED (MX-Lab) and {c['meltio_cell']} Meltio cells", 1,
        lo=c["ded"] * UNIT["ded"][0] + c["meltio_cell"] * UNIT["meltio_cell"][0],
        hi=c["ded"] * UNIT["ded"][1] + c["meltio_cell"] * UNIT["meltio_cell"][1], src="InssTek MX-Lab; Meltio cell",
        kind="estimate")
    add(f"{c['fumehood']} fume hoods, {c['glovebox']} gloveboxes, {c['packaging']} packaging stations", 1,
        lo=c["fumehood"] * UNIT["fumehood"][0] + c["glovebox"] * UNIT["glovebox"][0] + c["packaging"] * UNIT["packaging"][0],
        hi=c["fumehood"] * UNIT["fumehood"][1] + c["glovebox"] * UNIT["glovebox"][1] + c["packaging"] * UNIT["packaging"][1],
        src="", kind="estimate")
    add(f"{c['units']} MiR250 + UR12e mobile manipulators", c["units"], "units")
    a = area_m2() * FT2_PER_M2
    add(f"Building, {a / 1000:.0f},000 ft² of high bay ({area_m2():,.0f} m²)", 1, lo=a * BUILDING_PER_FT2[0],
        hi=a * BUILDING_PER_FT2[1], src=BUILDING_PER_FT2[2], kind=BUILDING_PER_FT2[3])
    add("Gases, power, chillers, dust and explosion protection, IT", 1, lo=SITE[0], hi=SITE[1], src=SITE[2],
        kind=SITE[3])
    sub = sum(r["usd_m"] for r in rows)
    rest = TOTAL / 1e6 - sub
    rows.append(dict(what="Design, permits, commissioning and contingency", n=1, usd_m=round(rest, 1),
                     low_m=None, high_m=None, source=f"what is left of $200M: {100 * rest / (TOTAL / 1e6):.0f} %",
                     kind="remainder"))
    note = ("Unit costs: midpoints of ranges, from public procurement records where found, estimates otherwise "
            "(facility/costs_and_sizes.md). Counts: what the film draws.")
    return dict(rows=rows, subtotal_m=round(sub, 1), total_m=round(TOTAL / 1e6, 1), remainder_pct=round(100 * rest / 200, 1),
                low_m=round(sum(r["low_m"] for r in rows if r["low_m"] is not None), 1),
                high_m=round(sum(r["high_m"] for r in rows if r["high_m"] is not None), 1), counts=c,
                area_m2=round(area_m2()), area_ft2=round(area_m2() * FT2_PER_M2), note=note)


def write():
    b = budget()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "budget.json").write_text(json.dumps(b, indent=1) + "\n")
    lines = ["| | Count | Each (USD) | Total, midpoint | Range | Source |", "|---|---|---|---|---|---|"]
    for r in b["rows"]:
        each = (f"{r['unit_low'] / 1e3:,.0f}k-{r['unit_high'] / 1e3:,.0f}k" if r.get("unit_low") and r["n"] > 1
                else "")
        rng = f"{r['low_m']}-{r['high_m']}" if r.get("low_m") is not None else ""
        lines.append(f"| {r['what']} | {r['n'] if r['n'] > 1 else ''} | {each} | ${r['usd_m']}M | {rng} | "
                     f"{r['source']} ({r['kind']}) |")
    lines.append(f"| **Total** | | | **${b['total_m']:.0f}M** | ${b['low_m']}-{b['high_m']}M before the remainder | |")
    (OUT / "budget.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({k: v for k, v in b.items() if k != "rows"}, indent=1))
    for r in b["rows"]:
        print(f"  {r['usd_m']:7.1f}  {r['what']}")


if __name__ == "__main__":
    write()
