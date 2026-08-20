"""Dispatch an Edison Scientific LITERATURE_HIGH query verifying the crevice-tool
ground-continuity measurement results for the Nilfisk CFM 118EXP.

Continuation of the §14 first-test-run verification trajectory
(d7ff65b9-...), which itself chains back through the powder-disposal SOP and the
bag-vs-liner / emptying-cadence reviews, so Edison retains the full vacuum context.

Writes _task_id.json next to this file. Fetching/artifact archival is done by
fetch_results.py (kept separate so the long poll can run as one blocking call).
"""
import os, json
from uuid import UUID
from edison_client import EdisonClient, TaskRequest, JobNames
from edison_client.models.app import RuntimeConfig

key = os.environ.get("EDISON_API_KEY") or os.environ.get("EDISON_PLATFORM_API_KEY")
if not key:
    raise SystemExit("Set EDISON_API_KEY (or EDISON_PLATFORM_API_KEY) in the environment.")
key = key.strip()
client = EdisonClient(api_key=key)

# Continue from the §14 first-test-run verification trajectory so Edison keeps the
# full prior context (vacuum config, continuity targets, EXP bonding, tools).
PRIOR = "d7ff65b9-1211-4ced-934e-c3c402eddee0"

query = r"""
Context: We operate a Nilfisk CFM 118EXP explosion-proof industrial vacuum in a university research lab
(BYU) to collect excess gas-atomized AlSi10Mg (aluminum-silicon-magnesium, ~20-63 um with sub-micron
fines) and elemental silicon powder from additive-manufacturing / ultrasonic-atomization research. The
unit is CSA Class I Group D / Class II Groups E,F,G. Its OEM 118EXP manual (UL 1213 par. 22, "TEST FOR
GROUND CONTINUITY BEFORE EACH USE") requires that the resistance of the grounding-continuity path
"shall not exceed 0.1 ohm," checked connection-by-connection (tool to wand, wand to hose, hose to
machine), and states "any alteration to this equipment by a third party will nullify its certification."
The manual's accessories BOM lists the crevice tool (P/N 01768900) with material = "Aluminium" (no
finish specified) and the hose as "Conductive." Prior Edison trajectories in this chain already covered
bag-vs-liner selection, emptying cadence, the powder-disposal SOP, and verification of the first-test-run
operating procedure (continuity acceptance targets, PPE, technique, sealing, cleaning).

We are doing pre-use ground-continuity testing before the first live powder run and hit an anomaly on
one attachment. Please VERIFY and interpret the following ACTUAL BENCH MEASUREMENTS against the
combustible-metal-dust / static-control literature and standards (NFPA 484, NFPA 652/654, NFPA 77,
UL 1213, OSHA 1910, ANSI/ESD, Aluminum Association, peer-reviewed dust-ignition/MIE and anodize/dielectric
literature). Meter: bench DMM accurate to ~0.01 ohm, REL used to null lead resistance (low-ohms range).

MEASUREMENTS (probes pressed firmly, large contact area, held still):
- Aluminum wand (01768601), tool-less: < 0.1 ohm end-to-end. Accessory coupler: < 0.1 ohm.
- Conductive antistatic hose: ~4 ohm end-to-end (manufacturer confirmed this is NORMAL for their
  conductive/flex hose; spec R <= 10^4 ohm).
- Vacuum body sections to each other ~0.2 ohm; lid-to-ground cable ~1 ohm.
- DUST BRUSH (01719401): tool-to-wand ~0.03 ohm — a clean, genuine metal-to-metal bond. PASSES.
- CREVICE TOOL (01768900), BRAND-NEW genuine Nilfisk part, unambiguously solid METAL (not plastic),
  the SAME silvery color as the low-resistance aluminum wand:
    * Surface-to-surface probing on the outer body: reads OL (over-range/open) on the REL-locked low
      range; with REL off and autoranging on, it climbs to MEGOHMS. So the outer skin behaves as an
      INSULATOR (~10^6 ohm class), roughly 10^5x over the < 10 ohm bonding target.
    * Probing AT THE JOINT where the crevice tool seats onto the wand: still OPEN — the tool does NOT
      bond to the wand through its socket as supplied.
    * Making LIGHT SCRATCHES in the surface and probing on/near the scratches: NO change, still open.
    * Nilfisk general technical customer support says the tool is "just aluminum," the rep did not know
      why it fails continuity, and referred us to their industrial-vacuum division (callback pending).

OUR WORKING HYPOTHESIS (please confirm, correct, or refute with citations): the crevice tool is
CLEAR/NATURAL ANODIZED aluminum — i.e., conductive aluminum bulk under a hard aluminum-oxide (Al2O3)
DIELECTRIC skin. That would explain: solid metal yet a persistent surface open; identical appearance to
the (also-aluminum) wand; a scratch that fails to restore continuity (anodize is Mohs ~9, harder than
the base metal, so a light scratch/probe-drag does not reach bright metal, and a low-voltage DMM at < ~3 V
cannot break down a coating that insulates to hundreds of volts). "Just aluminum" from Nilfisk names the
alloy, not the finish, and does not rule out anodize.

Please address, each with a CORRECT / CORRECT-WITH-CAVEAT / INCORRECT / UNSUPPORTED verdict and citations:

1. MEASUREMENT INTERPRETATION. Is the "OL on REL-locked range, megohms with autoranging" behavior a
   correct reading of a genuinely high (~10^6 ohm) surface resistance rather than a meter artifact? Is a
   persistent surface open that SURVIVES light scratching diagnostic of an engineered dielectric skin
   (anodize) as opposed to a few-nm native-oxide or machining-oil film (which ordinary probe pressure or
   a wipe defeats)? Give the expected surface resistivity / dielectric strength of sulfuric (clear)
   anodize and confirm a low-range ohmmeter cannot punch through it.

2. IS IT ANODIZED? From the physics + any available Nilfisk/industry sourcing or standard practice for
   aluminum vacuum tubes/nozzles, is clear anodize the most likely explanation for this exact symptom
   set (vs bare mill aluminum with native oxide, vs carbon-loaded "dissipative" plastic that merely looks
   metallic)? If you can find documentation of the 01768900 finish, report it; if the literature is
   silent, say so and give the most-likely conclusion.

3. IS AN ANODIZED EXP TOOL A DEFECT / A CONTRADICTION WITH "EXPLOSION-PROOF"? Explain the isolated-
   (ungrounded-) conductor ignition hazard (NFPA 77/484): a conductive aluminum mass insulated from ground
   can accumulate charge and produce an incendive spark. Then explain whether the hazard is resolved once
   the tool BODY is bonded to ground through a clean metal-to-metal joint — i.e., is a tens-of-micron
   anodized skin over GROUNDED metal itself an ignition concern (propagating brush discharge / coating-
   thickness thresholds), or is the only real requirement that the assembled tool not float? Is supplying
   an anodized tool consistent with an EXP-certified vacuum as long as the assembled chain bonds?

3b. AS-SUPPLIED FAILURE. Given the tool does NOT bond to the wand through its socket as supplied
   (joint reads open), is this an out-of-spec / non-conforming condition for a tool the OEM sells as part
   of an EXP-certified system whose own manual demands <= 0.1 ohm tool-to-wand before each use? What is
   the defensible course: insist on a conforming part / RMA, vs field-remediate the joint?

4. GOVERNING ACCEPTANCE CRITERION. Confirm the governing pass/fail is the OEM manual's ASSEMBLED
   tip-of-tool -> wand -> hose -> machine <= 0.1 ohm (UL 1213 par. 22), and reconcile that with the more
   permissive general NFPA 77 bonding figures (< 10 ohm for a bonded system, < 1 Mohm for static
   dissipation). Are our other readings acceptable within that chain: wand/coupler < 0.1 ohm, dust brush
   0.03 ohm, and specifically the ~4 ohm conductive hose (mfr says normal, spec R <= 10^4) — does a 4 ohm
   hose segment violate a strict 0.1-ohm-per-connection reading of the manual, and how should we treat a
   listed-conductive hose whose bulk resistance legitimately exceeds 0.1 ohm?

5. REMEDIATION. Is the correct fix to BOND THE JOINT rather than strip the tool — i.e., clean / lightly
   abrade ONLY the socket bore of the tool and the wand tip to bright metal, seat metal-to-metal, and
   re-verify <= 0.1 ohm — rather than removing the finish from the working surface? Address: (a) whether
   this counts as an "alteration that nullifies certification" and how to keep it minimal / get EHS-DHA
   sign-off; (b) non-destructive checks to try first (probe the bare masked rack-contact points left by
   anodizing; probe machined faces / cut ends that may be bare; confirm full tight seating; plastic-safe
   contact cleaner / fine non-metallic Scotch-Brite on mating surfaces only); (c) when to STOP and simply
   REPLACE it with a confirmed-conductive / ESD crevice tool instead.

6. SAFETY OF THE DIAGNOSTIC ITSELF. Aluminum abrasion/grinding dust is itself a combustible-dust hazard:
   confirm the abrade-to-bright-metal test must be done BEFORE the tool ever contacts AlSi10Mg, away from
   powder and ignition sources, with debris captured by a damp wipe, and any other controls.

Finally: list anything IMPORTANT we may be OMITTING (e.g., verifying the dust brush is the conductive-
BRISTLE EXP variant and that its ferrule path is in the continuity check; marking standardized probe
points for repeatable readings; documenting expected per-connection resistances; whether a single
non-conforming tool should gate the whole first live run). Where the literature is genuinely silent or
quantity-dependent, say so and give the conservative recommendation.
"""

task = TaskRequest(
    name=JobNames.LITERATURE_HIGH,
    query=query,
    runtime_config=RuntimeConfig(continued_job_id=UUID(PRIOR)),
)
task_id = client.create_task(task)
print("TASK_ID", task_id)
here = os.path.dirname(__file__) or "."
with open(os.path.join(here, "_task_id.json"), "w") as f:
    json.dump({"task_id": str(task_id), "continued_from": PRIOR}, f, indent=2)
print("wrote _task_id.json")
