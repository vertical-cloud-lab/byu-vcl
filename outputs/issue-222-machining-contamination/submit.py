"""Submit the two Edison literature queries for the machining-contamination question (PR #232).

Writes the task ids to _task_id.json next to this file; fetch.py polls and saves the answers.
"""
import json
import os
from pathlib import Path

from edison_client import EdisonClient, JobNames

HERE = Path(__file__).parent

CONTEXT = """\
CONTEXT. We machine powder "cups" as feedstock for a vacuum-induction ultrasonic atomizer
(AMAZEMET rePowder: graphite crucible with a BN wash, chamber pumped down then backfilled with
argon to ~200 mbar, melt at ~800-840 C, pushed through a 0.7 mm nozzle onto a 40 kHz sonotrode),
to make Al-Si powder for laser powder bed fusion (target 15-45 um). Each cup is turned on a
shared university-shop manual lathe from 3/4 in (19.05 mm) 6063 aluminum bar: band-saw cut,
face, center drill, 1/2 in HSS twist drill 2.25 in (57 mm) deep into a blind hole, part off,
2.75 in (70 mm) long. A 6063 plug (12.9 mm dia, 14 mm long, 1 mm vent hole) is turned to a
0.0005-0.0008 in press fit. The cup is filled with 9-14 g of atomized Al-12Si (AA 4047) powder.
About four cups (~200 g total, ~60 cm2 of machined surface per cup incl. the blind bore) are
melted per run. Before filling, cups and plugs are wiped with isopropyl alcohol (IPA) on
Kimwipes and air dried. Lubricant use is not controlled: it may be dry, cutting oil, WD-40,
or a water-soluble coolant, and the lathe is shared with steel and brass work.
"""

QUERIES = {
    "literature_machining": CONTEXT + """
QUESTION 1 (machining contamination and what it does in the melt). Quantitatively, what does
lathe turning and drilling of 6xxx aluminum leave on or in the surface, and how much of it
would survive into remelted powder?
(a) Residual cutting fluid / oil / coolant film after machining, in ug/cm2 or mg/m2, and
after a solvent wipe. Convert to ppm of a ~50 g part with ~60 cm2 of surface where possible.
(b) Tool-wear debris from HSS (Fe, W, Mo, Cr, V, Co) or WC-Co tools when cutting aluminum:
wear rates or mass loss per part; built-up edge; embedded swarf or abrasive grit (SiC, Al2O3)
from shared machines, emery cloth or files.
(c) Machining-induced surface layers: oxide/hydroxide growth with water-based coolant,
staining, cold-worked layer depth.
(d) On remelting under vacuum then argon: fate of hydrocarbon and coolant residues (hydrogen
pickup and porosity, carbon or Al4C3, oxide films and bifilms, outgassing during pump-down).
Any documented effect of feedstock surface cleanliness on oxygen, hydrogen or carbon content
of gas- or ultrasonically-atomized Al alloy powder, or on LPBF porosity?
(e) Compare these levels with the composition limits of AA 6063 (e.g. Fe <= 0.35, Cu <= 0.10
wt%) and AA 4047, and with the oxygen the fine powder itself contributes (native oxide shell
on 15-45 um Al-Si powder, typical O wt%).
Give numbers with citations, and say plainly where the evidence is thin or only indirect.""",
    "literature_cleaning": CONTEXT + """
QUESTION 2 (how much does an IPA wipe help). How effective is wiping with isopropyl alcohol on
lint-free tissue for removing machining residues from aluminum, compared with acetone, a
hydrocarbon solvent, aqueous alkaline or detergent degreasing, and ultrasonic solvent
cleaning? Use quantitative cleanliness measures where available: residual carbon or
hydrocarbon by gravimetry, XPS, FTIR, optically stimulated electron emission, water-break or
contact angle, particle counts. Specifically:
(a) Solubility of typical cutting oils (mineral oil, esters, EP additives with S/Cl/P),
WD-40, and semi-synthetic coolant residues in IPA versus acetone or heptane; does IPA
redistribute rather than remove oil films? Effect of 70% vs 99% IPA (water content).
(b) Vacuum-component and pre-weld / pre-braze cleaning practice for aluminum (e.g. vacuum
hardware cleaning procedures, AWS D1.2 / brazing guidance, NASA or CERN cleaning
specifications): what do they require, and where does a solvent wipe fall short?
(c) Cleaning blind holes (12.7 mm diameter, 57 mm deep): can a wipe reach the bottom, and
what is recommended (flush, swab, ultrasonic, blow-dry, bake-out)?
(d) Residual IPA or water left in a blind hole before filling with fine Al powder: risks
(hydrogen, hydroxide, powder caking) and recommended drying.
(e) Any data on contamination introduced by handling: fingerprints (Na, Cl, K, lipids),
lint fibers, nitrile glove residue.
Give numbers with citations, and say plainly where the evidence is thin or only indirect.""",
}

if __name__ == "__main__":
    client = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])
    ids = {}
    for key, query in QUERIES.items():
        ids[key] = str(client.create_task({"name": JobNames.LITERATURE, "query": query}))
        print(key, "submitted")
    (HERE / "_task_id.json").write_text(json.dumps(ids, indent=1) + "\n")
    (HERE / "queries.json").write_text(json.dumps(QUERIES, indent=1) + "\n")
