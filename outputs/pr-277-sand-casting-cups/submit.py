"""Submit the Edison literature queries on sand-casting the larger charge cups (PR #277).

Writes the task ids to _task_id.json next to this file; fetch.py polls and saves the answers.
"""
import json
import os
from pathlib import Path

from edison_client import EdisonClient, JobNames

HERE = Path(__file__).parent

CONTEXT = """\
CONTEXT. We make sealed aluminium "cups" as the charge for a vacuum-induction ultrasonic
atomizer (AMAZEMET rePowder: induction melting in a graphite crucible with a boron-nitride
wash, chamber pumped down then backfilled with argon to ~150-200 mbar, melt at ~800-850 C
pushed by ~0.2 bar argon overpressure through a 0.5-0.7 mm graphite nozzle onto a 40 kHz
sonotrode plate) to make Al-Si powder (target 15-63 um) for laser powder bed fusion and alloy
studies. Today each cup is machined on a lathe from extruded 3/4 in (19 mm) AA 6063-T52 bar:
70 mm long with a 12.7 mm blind bore 57 mm deep (or a 15.9 mm bore and 1.5 mm wall for a
thin-wall version), filled with 6-16 g of gas-atomized AA 4047 (Al-12Si) powder, and closed
by a press-fit 6063 plug with a ~1 mm vent hole (0.013-0.020 mm interference). Three to five
cups (~150-250 g in total) are melted per run. The runs are a Si composition spread (0-30 wt%
4047 powder in 6063) whose composition is computed from the weighed masses, so the cup metal's
own composition and cleanliness matter. The cups exist to put the powder inside bulk metal so
that it melts in contact with liquid, without loose-powder losses and with little oxide
pickup. Current practice: dry or light-oil machining, a 99% IPA flush, and an 80 C dry.

PROPOSAL. To make larger cups (more powder per cup), students are considering sand casting
them instead of machining: melting aluminium (most likely re-melted 6063 offcuts and scrap,
or commercially pure aluminium, or a casting alloy such as A356) in a clay-graphite or SiC
crucible in a university foundry (gas or electric furnace, melting in air, possibly with no
rotary degassing or flux), and hand-pouring into green sand (clay-bonded, ~3-4% moisture) or
chemically bonded no-bake sand moulds with a sand core forming the cavity. The cast cup might
be used as cast, or with only the bore and the plug seat machined.
"""

QUERIES = {
    "literature_oxygen_purity": CONTEXT + """
QUESTION 1 (oxygen, hydrogen and purity). Quantitatively, how does a sand-cast aluminium part
compare with extruded wrought bar of the same alloy as a remelt feedstock, in terms of:
(a) entrained oxide films (bifilms), dross and spinel (MgAl2O4 in Mg-bearing alloys such as
6063): oxide inclusion content by PoDFA, LAIS, LiMCA, K-mold or reduced-pressure test
(mm2/kg, inclusions per kg, bifilm index) and bulk oxygen in ppm; how it depends on pouring
practice (turbulence, gate velocity above ~0.5 m/s, fall height), on the number of remelts,
and on melting in air versus under inert gas;
(b) hydrogen: pickup from mould moisture, humid air, and crucible or tool dressings; typical
hydrogen (mL/100 g) in undegassed versus rotary-degassed melts and in extruded bar; the
resulting gas porosity; and what happens to that hydrogen and porosity when the part is
re-melted under vacuum and then argon (outgassing during pump-down, melt spitting or
bubbling, hydrogen and internal porosity in the atomized powder);
(c) process contamination: Fe pickup from uncoated steel ladles, skimmers and stirring rods
(rates in wt% per hour at 700-750 C); Si or C pickup from crucibles; sand grains and binder
residues embedded in the surface (burn-on, metal penetration); carbon and nitrogen from
organic binders; Na, Ca, K, Cl and F from fluxes and degassing tablets; Mg loss by oxidation
(wt% per melt); Zn and Cu from mixed scrap;
(d) the as-cast surface: thickness and nature of the oxide skin on sand-cast versus machined
aluminium, and how much of the skin must be machined away to reach clean metal;
(e) the effect of feedstock oxide and hydrogen content on atomization: clogging of sub-mm
nozzles by oxide films and inclusions, powder oxygen content, satellite or irregular
particles, internal powder porosity, and any cleanliness specifications for gas- or
ultrasonic-atomization feedstock (e.g. VIGA or EIGA ingot or rod requirements);
(f) the practices that bring a casting close to wrought-bar cleanliness: drying sand and
cores, rotary argon degassing, fluxing, ceramic foam filters, bottom-gated or tilt pouring
(Campbell's casting rules), coated tools, a dedicated crucible, vacuum or inert-gas casting,
and permanent-mould (graphite or steel) casting instead of sand.
Give numbers with citations, and say plainly where the evidence is thin or only indirect.""",
    "literature_cast_quality": CONTEXT + """
QUESTION 2 (metal quality after casting, and fitness for this purpose). For the same proposal:
(a) castability of AA 6063 and other wrought 6xxx alloys in sand moulds compared with casting
alloys (A356, 4047 / Al-12Si) and commercially pure Al: fluidity, hot-tearing susceptibility,
shrinkage porosity, freezing range;
(b) as-cast microstructure and properties of sand-cast 6063 or pure Al relative to extruded
6063-T5/T52: grain size, secondary dendrite arm spacing, Mg2Si and beta-AlFeSi intermetallics,
macro- and microsegregation, density, yield strength and ductility;
(c) whether a thin-walled (1.5-3 mm) sand-cast aluminium cup can take a press-fit plug with
0.013-0.020 mm interference without cracking or leaking, given its porosity and lower yield
strength; how gas and shrinkage porosity affect sealing and leak tightness of thin walls;
(d) achievable dimensional tolerances and surface roughness for small sand castings and for
alternatives (gravity permanent-mould casting in graphite or steel, investment casting,
lost-foam), and what machining would still be needed for a press fit;
(e) whether cups cast from re-melted 6063 stay within AA 6063 composition limits (Mg, Fe, Si,
Cu, Zn) and how many remelt cycles it takes to drift out;
(f) other ways to make larger aluminium containers for powder (tube with welded or press-fit
end plugs, impact-extruded or deep-drawn 1xxx/3xxx cans, larger-diameter bar, canning or
compacting powder into a can as in powder-metallurgy HIP canning) and how they compare on
oxide and hydrogen content and on effort.
Give numbers with citations, and say plainly where the evidence is thin or only indirect.""",
}

if __name__ == "__main__":
    client = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])
    ids = {}
    for key, query in QUERIES.items():
        ids[key] = str(client.create_task({"name": JobNames.LITERATURE_HIGH, "query": query}))
        print(key, "submitted")
    (HERE / "_task_id.json").write_text(json.dumps(ids, indent=1) + "\n")
    (HERE / "queries.json").write_text(json.dumps(QUERIES, indent=1) + "\n")
