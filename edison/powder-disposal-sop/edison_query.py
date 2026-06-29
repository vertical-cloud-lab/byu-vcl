import os, json, time
from uuid import UUID
from edison_client import EdisonClient, TaskRequest, JobNames
from edison_client.models.app import RuntimeConfig

key = (os.environ.get('EDISON_API_KEY') or os.environ.get('EDISON_PLATFORM_API_KEY')).strip()
client = EdisonClient(api_key=key)

PRIOR = "8288144a-12bc-4f3a-84ad-a7eec45a58bb"  # prior LITERATURE_HIGH continuation (emptying cadence)

query = r"""
Context: We operate a Nilfisk CFM 118EXP explosion-proof industrial vacuum in a university research
lab (BYU) to collect excess metal powders used in additive manufacturing / ultrasonic atomization
research. The primary powder is gas-atomized AlSi10Mg (aluminum-silicon-magnesium alloy, particle
size ~20-63 um with sub-micron fines), and we also handle elemental silicon powder and may handle
other reactive metal powders in the future. The vacuum is configured with an antistatic main filter,
an upstream HEPA filter, a downstream HEPA filter, a fully conductive steel-wire-reinforced antistatic
hose, conductive aluminum wand/coupler, and a bonded carbon-loaded conductive polyethylene bin liner
(surface resistivity ~10^3-10^5 ohm/sq) inside the collection bin. The whole grounding chain is verified
to building earth with a multimeter (<1 ohm typical, hose end-to-end ~4 ohm which the manufacturer
confirmed is normal for their conductive hose). Waste goes: conductive liner -> grounded steel interim
pail (Uline S-22507BL 3.5 gal with S-21135BL lever-lock lid) -> BYU EHS unwanted-materials pickup.

We need a single, authoritative, citation-backed Standard Operating Procedure (SOP) for the safe
disposal of collected AlSi10Mg (and Si and general reactive metal) powder. Different AI tools and papers
give conflicting guidance and there is no single standardized procedure, so please synthesize the
combustible-metal-dust safety literature (NFPA 484, NFPA 652, NFPA 654, NFPA 77, OSHA, Aluminum
Association guidance, peer-reviewed powder-handling and passivation literature, AM powder safety
literature) into concrete, defensible steps. Please address each of the following explicitly:

1. LINER REMOVAL: Exact step-by-step procedure for removing the full conductive liner from the vacuum
   collection bin without aerosolizing powder or breaking the grounding/bonding chain. Address: vacuum
   power-off and settling time; operator PPE and personal grounding (wrist strap); the "gooseneck"
   twist-and-fold seal with conductive cable ties; whether/when to keep the operator and bin bonded
   during the transfer; the 25%-fill / layer-depth limits.

2. PASSIVATION: Is chemical passivation of the collected AlSi10Mg powder necessary or recommended before
   storage/disposal? Specifically evaluate the common practice of wetting/coating fine aluminum-alloy
   powder with mineral oil (or other passivation agents) to suppress dust-cloud ignitability and
   pyrophoricity. Discuss the trade-offs: (a) mineral-oil passivation vs (b) keeping the powder dry and
   relying on inert, sealed, grounded containment; the hydrogen-gas hazard if any water/moisture is
   involved (Al + H2O -> H2); whether passivation changes the EHS waste classification; and give a clear
   recommendation for our low-quantity (tens of grams per week) dry lab scenario, including whether
   mineral oil is appropriate or whether it creates new hazards (oil-soaked metal fines, disposal
   complications). If passivation is recommended, give the exact method (agent, ratio, mixing technique).

3. INTERIM PAIL STORAGE: How to store the sealed liners in the grounded steel interim pail: max number
   of liners / max fill, keeping the pail grounded and closed, labeling, segregation from incompatibles,
   location, and any inerting or moisture-exclusion requirements.

4. TRANSFER TO FINAL DISPOSAL CONTAINER: How to move the powder/liners from the interim pail to the final
   EHS disposal container, including whether the sealed liner should be opened or transferred intact,
   hazardous-waste labeling/manifest expectations (RCRA D001 ignitable / reactive considerations for
   aluminum and silicon powders), and coordination with university EHS.

5. SWITCHING METALS - PAILS: When we switch the metal being vacuumed (e.g., from AlSi10Mg to Si, or to a
   different reactive metal), do we need a separate/dedicated interim pail and liner per metal? Address
   cross-contamination, thermite-type or galvanic incompatibility risks between mixed metal powders
   (e.g., aluminum + iron oxide, aluminum + other metal oxides), and give a clear rule for when dedicated
   containers are required vs when a shared container is acceptable.

6. SWITCHING METALS - VACUUM CLEANING: Is cleaning/purging of the vacuum itself necessary between
   different powders? What residual-powder contamination risks exist (incompatible mixtures inside the
   filter stack, hose, bin)? Provide a recommended decision rule.

7. VACUUM CLEANING / PURIFICATION METHOD: Provide the recommended safe method to clean/purify the vacuum
   interior (bin, hose, wand, and how to treat the antistatic main filter and the two HEPA filters)
   between powder types or periodically. Address: dry wiping vs damp wiping vs solvent; the prohibition
   on water with aluminum; whether filters must be replaced rather than cleaned; HEPA/main-filter
   replacement cadence given ~40 um metal powder loading; antistatic cleaning agents (e.g., plastic-safe
   electronic contact cleaner, fine Scotch-Brite for contact surfaces) and whether they are appropriate;
   and how to re-verify ground continuity after cleaning.

Also include: required PPE, a Class D extinguisher requirement and placement, what NOT to do (no water,
no compressed-air blow-down, no vacuuming sparks/hot particles, no smoking/ignition sources), and a
concise master checklist a student operator can follow. Where the literature is genuinely silent or
quantity-dependent, say so and give the conservative best-practice recommendation. Provide specific
citations for each major claim.
"""

task = TaskRequest(
    name=JobNames.LITERATURE_HIGH,
    query=query,
    runtime_config=RuntimeConfig(continued_job_id=UUID(PRIOR)),
)
task_id = client.create_task(task)
print("TASK_ID", task_id)
with open("/tmp/edison_task_id.txt", "w") as f:
    f.write(str(task_id))
