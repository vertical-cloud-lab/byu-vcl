"""Build the OpenRAMAN-on-CubXL bill of materials from the price data in raw/.

Every price comes from a file in raw/, fetched on 2026-10-10 from the stream-cam
Pi's residential IP (see ../README.md#how-the-prices-were-fetched). Nothing here
is typed in by hand except the quantities, which follow the official OpenRAMAN
BOM CSVs (git.thepulsar.be/openraman/cad.git @ 778dfda, exports/**/MAIN ASSEMBLY.csv).

    python build_bom.py            # writes bom.csv and bom_tables.md next to this file
"""
from __future__ import annotations

import csv
import json
import math
import re
from collections import OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"

# --------------------------------------------------------------------------
# Price lookups
# --------------------------------------------------------------------------
THORLABS = {}
for line in (RAW / "thorlabs_graphql_2026-10-10.jsonl").read_text().splitlines():
    d = json.loads(line)
    for item in d.get("exact", []):
        THORLABS[item["code"]] = item  # later rows win; all rows are the same day

PAGES = {}
for line in (RAW / "vendor_pages_2026-10-10.jsonl").read_text().splitlines():
    d = json.loads(line)
    PAGES[d["url"]] = d

# Printed-part volumes (cm^3), measured from the STEP files by ../cad/build_cad.py
_pp = HERE.parent / "cad" / "printed_parts.json"
PRINTED = json.loads(_pp.read_text()) if _pp.exists() else {}


def thorlabs(code):
    it = THORLABS[code]
    return dict(vendor="Thorlabs", part_no=code, title=it["title"].replace("&quot;", '"').replace("&nbsp;", " ")
                .replace("&Delta;", "Δ"), unit_price=it["price"]["actual"]["amount"],
                url=f"https://www.thorlabs.com/item/{it['slug']}", status=it["itemStatusTL"])


def page(url, vendor, part_no, title, price_index=0):
    d = PAGES[url]
    if d.get("jsonld_price"):
        price = float(d["jsonld_price"][0].rstrip(",").replace(",", ""))
    else:  # first real "$x.yy" on an Amazon page; "$10" is the free-shipping banner
        prices = [p for p in d["prices"] if re.fullmatch(r"\$[0-9,]+\.[0-9]{2}", p)]
        price = float(prices[price_index].lstrip("$").replace(",", ""))
    return dict(vendor=vendor, part_no=part_no, title=title, unit_price=price, url=url, status="Active")


AMZ = "https://www.amazon.com/dp/"
TVS = "https://www.teledynevisionsolutions.com/products/blackfly-s-gige/?model=BFS-PGE-31S4M-C"

# Filament: Polymaker ASA black, the closest printable stand-in for the official
# black ABS cover and the anodised-black aluminium holders.
ASA = page(AMZ + "B09DKPYYBP", "Amazon", "B09DKPYYBP", "Polymaker ASA filament 1.75 mm, black, 1 kg")
ASA_DENSITY = 1.07      # g/cm^3, Polymaker ASA datasheet value
FILL = 0.65             # effective solid fraction: 4 walls + 40 % gyroid, typical for these sizes


def printed(name, desc, qty=1, official=None):
    if name not in PRINTED:  # part not generated yet
        return dict(vendor="Print in-house (Bambu H2D)", part_no=name, title=desc, unit_price=0.0, url="",
                    status="", note="volume pending: run ../cad/build_cad.py")
    v = PRINTED[name]["volume_cm3"]
    grams = v * ASA_DENSITY * FILL
    return dict(vendor="Print in-house (Bambu H2D)", part_no=name, title=desc,
                unit_price=round(grams * ASA["unit_price"] / 1000.0, 2), url="", status="",
                note=f"{v:.1f} cm³ solid → ≈{grams:.0f} g ASA" + (f"; official spec: {official}" if official else ""))


# --------------------------------------------------------------------------
# The bill of materials. (bom_ref, qty_needed, pack_size, item, note)
# --------------------------------------------------------------------------
S = OrderedDict()
S["A. Base spectrometer: purchased parts (official BOM P00000)"] = [
    ("FLIR-BFS-PGE-31S4M-C", 1, 1, page(TVS, "Teledyne FLIR", "BFS-PGE-31S4M-C",
                                         "Blackfly S GigE 3.2 MP mono camera, Sony IMX265, C-mount"), ""),
    ("NMV50M23", 1, 1, thorlabs("MVL50M23"), "Navitar NMV-50M23; Thorlabs sells it as MVL50M23"),
    ("CPS532", 1, 1, thorlabs("CPS532"), "Class 3R, 4.5 mW"),
    ("DMLP550", 1, 1, thorlabs("DMLP550"), ""),
    ("FELH0550", 1, 1, thorlabs("FELH0550"), ""),
    ("GR25-1205", 1, 1, thorlabs("GR25-1205"), ""),
    ("WG41050-A", 1, 1, thorlabs("WG41050-A"), ""),
    ("S50K", 1, 1, thorlabs("S50K"), ""),
    ("AC254-050-A", 1, 1, thorlabs("AC254-050-A"), ""),
    ("AC127-019-A", 1, 1, thorlabs("AC127-019-A"), ""),
    ("PF10-03-G01", 1, 1, thorlabs("PF10-03-G01"), ""),
    ("KM100", 3, 1, thorlabs("KM100"), ""),
    ("FMP1", 2, 1, thorlabs("FMP1/M"), "metric FMP1/M: the baseplate screws are M4"),
    ("CRM1M", 1, 1, thorlabs("CRM1T/M"), "CRM1/M is superseded; Thorlabs names CRM1T/M"),
    ("CP14", 1, 1, thorlabs("CP14"), ""),
    ("CP35M", 1, 1, thorlabs("CP35/M"), ""),
    ("CP02B", 2, 1, thorlabs("CP33B"), "CP02B is superseded; Thorlabs names CP33B"),
    ("ER3", 4, 1, thorlabs("ER3"), ""),
    ("SM1RR", 1, 1, thorlabs("SM1RR"), ""),
]
S["B. Base spectrometer: fasteners (official BOM P00000)"] = [
    ("DIN912 M4x10", 7, 50, thorlabs("SH4MS10"), "50-pack"),
    ("DIN912 M4x12", 7, 50, thorlabs("SH4MS12"), "50-pack"),
    ("DIN912 M4x6", 3, 50, thorlabs("SH4MS06"), "50-pack"),
    ("SS4MN4", 1, 10, thorlabs("SS4MN4"), "10-pack; clamps the laser"),
    ("DIN7 3x8", 2, 100, page(AMZ + "B0F54D5ZC4", "Amazon", "B0F54D5ZC4",
                              "uxcell 3 × 8 mm dowel pins, bearing steel, ±0.02 mm, 100 pcs"), "100-pack; camera bracket"),
    ("(drawing sheet 5)", 1, 1, thorlabs("G14250"), "glues the grating to its holder"),
]
S["C. Base spectrometer: custom parts, printed in-house (official P00001–P00005)"] = [
    ("P00001 BASEPLATE", 1, 1, printed("P00001_BASEPLATE", "Baseplate 300 × 150 × 10 mm", official="Al 6061, black anodised"), ""),
    ("P00002 COVER", 1, 1, printed("P00002_COVER", "Cover", official="ABS, black"), ""),
    ("P00003 LASER HOLDER", 1, 1, printed("P00003_LASER_HOLDER", "Laser holder", official="Al 6061, black anodised"), ""),
    ("P00004 GRATING HOLDER", 1, 1, printed("P00004_GRATING_HOLDER", "Grating holder", official="Al 6061, black anodised"), ""),
    ("P00005 CAMERA BRACKET", 1, 1, printed("P00005_CAMERA_BRACKET", "Camera bracket", official="Al 2017, black anodised"), ""),
]
S["D. Needed to run it, not in the official BOM"] = [
    ("laser power", 1, 1, thorlabs("CPSA"), "USB-A → 2.5 mm phono; powers the CPS532 from the CubXL Pi's USB"),
    ("camera power", 1, 1, page(AMZ + "B001PS9E5I", "Amazon", "B001PS9E5I", "TP-Link Omada POE150S gigabit PoE injector, 15.4 W"), "the Blackfly S PGE is PoE-powered"),
    ("camera link", 1, 1, page(AMZ + "B0CP9XGZKM", "Amazon", "B0CP9XGZKM", "Cable Matters Cat 6 snagless cable, 6 ft"), "to the CubXL Pi's free eth0"),
]
S["E. CubXL integration (new parts in ../cad/)"] = [
    ("deck adapter", 1, 1, printed("CUBXL_DECK_ADAPTER", "OpenRAMAN → PandaDeck adapter plate with 8 deck keys"), ""),
    ("tip dock", 1, 1, printed("CUBXL_TIP_DOCK", "Pipette-tip sampling dock (sample port, beam dump)"), ""),
    ("adapter inserts", 6, 50, page(AMZ + "B07YSV66Y5", "Amazon", "B07YSV66Y5",
                                    "ruthex M4 heat-set inserts RX-M4x8.1, 50 pcs"), "4 baseplate corners + 2 dock"),
    ("adapter screws", 4, 50, thorlabs("SH4MS16"), "M4 × 16, through the baseplate's corner counterbores"),
    ("dock lens", 1, 1, thorlabs("AC127-019-A"), "focuses the beam into the tip, as in the official liquid cuvette"),
    ("dock cage plate", 1, 1, thorlabs("CP33/M"), "holds the dock lens on the sample-port bracket"),
    ("dock cage rods", 2, 1, thorlabs("ER1"), ""),
    ("dock lens retaining ring", 1, 1, thorlabs("SM05RR"), "holds the Ø1/2\" lens in the dock's SM05 bore"),
]
# Optional, not in the CubXL total: the official vial-based sample interface, for comparison
S["F. Optional: official Standard Liquid Cuvette (vials instead of a pipette tip; P00008)"] = [
    ("ER1", 2, 1, thorlabs("ER1"), ""),
    ("AC127-019-A", 1, 1, thorlabs("AC127-019-A"), ""),
    ("LK1085L1-A", 1, 1, thorlabs("LK1085L1-A"), "cylindrical lens: corrects the vial wall's lensing"),
    ("CP33M (drawing)", 1, 1, thorlabs("CP33/M"), "on the assembly drawing, not in its CSV"),
    ("DIN914 M4x10", 1, 50, thorlabs("SS4MS10"), "50-pack"),
    ("DIN7 3m6x50", 1, 50, page(AMZ + "B0F6D3P7DW", "Amazon", "B0F6D3P7DW", "HARFINGTON 3 × 50 mm dowel pins, 304 SS, 50 pcs"), "the 'axis'"),
    ("P00009 BODY", 1, 1, printed("P00009_BODY", "Cuvette body", official="PA12, black dye"), ""),
    ("P00010 CAP", 1, 1, printed("P00010_CAP", "Cuvette cap", official="PA12, black dye"), ""),
    ("P00012 SPACER BLOCK", 1, 1, printed("P00012_SPACER_BLOCK", "Spacer block", official="ABS"), ""),
    ("P00011 LENS BARREL", 1, 1, printed("P00011_LENS_BARREL", "Lens barrel", official="brass, machined"), ""),
]


def rows():
    for section, items in S.items():
        for ref, need, pack, it, note in items:
            buy = math.ceil(need / pack)
            yield dict(section=section, bom_ref=ref, qty_needed=need, pack_size=pack, buy=buy,
                       vendor=it["vendor"], part_no=it["part_no"], title=it["title"],
                       unit_price=it["unit_price"], ext_price=round(buy * it["unit_price"], 2),
                       status=it.get("status", ""), url=it.get("url", ""),
                       note="; ".join(x for x in (it.get("note", ""), note) if x))


def main():
    R = list(rows())
    with open(HERE / "bom.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(R[0].keys()))
        w.writeheader()
        w.writerows(R)

    out = []
    totals = OrderedDict()
    for section in S:
        rs = [r for r in R if r["section"] == section]
        totals[section] = sum(r["ext_price"] for r in rs)
        out.append(f"### {section}\n")
        out.append("| BOM ref | Buy | Vendor | Part | Description | Unit | Ext. | Note |")
        out.append("|---|---:|---|---|---|---:|---:|---|")
        for r in rs:
            part = f"[{r['part_no']}]({r['url']})" if r["url"] else r["part_no"]
            out.append(f"| {r['bom_ref']} | {r['buy']} | {r['vendor']} | {part} | {r['title']} | "
                       f"${r['unit_price']:,.2f} | ${r['ext_price']:,.2f} | {r['note']} |")
        out.append(f"| | | | | **Subtotal** | | **${totals[section]:,.2f}** | |\n")

    out.append("### Totals\n")
    out.append("| Section | USD |")
    out.append("|---|---:|")
    for k, v in totals.items():
        out.append(f"| {k} | ${v:,.2f} |")
    core = sum(v for k, v in totals.items() if k[0] in "ABC")
    cubxl = sum(v for k, v in totals.items() if k[0] in "ABCDE")
    out.append(f"| **Spectrometer as specified (A + B + C)** | **${core:,.2f}** |")
    out.append(f"| **Running on the CubXL with the tip dock (A–E)** | **${cubxl:,.2f}** |")
    out.append(f"| Optional official vial cuvette instead (F) | +${totals[list(S)[-1]]:,.2f} |\n")

    out.append("### Shopping list by vendor\n")
    by = defaultdict(list)
    for r in R:
        if not r["section"].startswith("F."):
            by[r["vendor"]].append(r)
    out.append("| Vendor | Lines | Items | USD |")
    out.append("|---|---:|---|---:|")
    for v, rs in sorted(by.items(), key=lambda kv: -sum(r["ext_price"] for r in kv[1])):
        merged = OrderedDict()
        for r in rs:
            merged[r["part_no"]] = merged.get(r["part_no"], 0) + r["buy"]
        items = ", ".join(f"{k} ×{n}" if n > 1 else k for k, n in merged.items())
        out.append(f"| {v} | {len(merged)} | {items} | ${sum(r['ext_price'] for r in rs):,.2f} |")
    (HERE / "bom_tables.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
