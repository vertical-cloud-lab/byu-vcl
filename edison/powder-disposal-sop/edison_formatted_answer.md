Question: You are following up on a prior task: You are following up on a prior task: Context: We are setting up a Nilfisk CFM 118EXP explosion-proof industrial vacuum cleaner for collecting combustible/reactive metal AM powders (AlSi10Mg and elemental Si, typical particle size 20–63 µm with sub-micron fines). The vacuum already has, or will have installed:
- Antistatic main filter (Nilfisk PN 40000460, 99.7% @ 1.5 µm)
- Upstream HEPA filter (Nilfisk PN 01727631 / 1408678500, 99.97% @ 0.3 µm)
- Downstream HEPA filter (Nilfisk PN 01727631)
- OEM antistatic 1.5" hose with grounded cuffs, conductive metal wand and crevice tool, full grounding chain to building earth

Vacuum is CSA-rated Class I Group D and Class II Groups E, F, G (combustible metal dust). Spec follows NFPA 484 (Combustible Metals) and NFPA 652/660 (Combustible Dust).

The OEM Nilfisk dust collection bag (PN 107413584, the only model confirmed by a Nilfisk distributor to fit the 118EXP collection container) is paper/fleece based and not explicitly antistatic. A previous attempt to buy bags via Grainger (Nilfisk Vacuum Bag 4RYH6 fleece) was identified as non-antistatic and rejected.

Question 1 (primary): For combustible metal powder collection (AlSi10Mg, Si) in an explosion-proof industrial vacuum, is it acceptable per NFPA 484 / NFPA 652 / NFPA 660 / OSHA / ATEX consensus practice to operate WITHOUT a disposable collection bag and instead rely on:
(a) the antistatic main filter + upstream HEPA + downstream HEPA already installed, AND
(b) an antistatic / conductive polyethylene liner placed inside the stainless-steel collection bin (electrically bonded to the bin / vacuum body so the grounding chain is preserved)?

Specifically address:
- Whether conductive (10^4 – 10^6 Ω surface resistivity) or static-dissipative (10^6 – 10^11 Ω) liners satisfy NFPA 484 / NFPA 652 grounding and static-control requirements for combustible metal dust collection,
- Whether the absence of a bag introduces unacceptable risks (powder fluidization, filter blinding, dust resuspension during emptying, MIE-related ignition hazards) that a bag would otherwise mitigate,
- Whether collected metal powder in a liner can be safely disposed of / transferred to an outer waste container, and what NFPA 484 says about temporary storage of reactive metal fines,
- Any documented industry guidance from Nilfisk, Ruwac, Tiger-Vac, VAC-U-MAX, or similar manufacturers about bag-vs-liner-vs-bagless for AlSi10Mg / aluminum / silicon powder.

Question 2 (secondary, sourcing): If a true antistatic / conductive disposable filter bag IS required (not just a liner), please identify specific commercial part numbers that:
- Fit the Nilfisk CFM 118EXP collection container (~12.5" / 320 mm internal diameter container, sized to nest in the stainless drum used on 118 EXP and A15EXP models),
- Are explicitly rated antistatic / conductive (carbon-loaded paper, conductive plastic, or antistatic-treated fleece) and suitable for combustible metal dust per NFPA 484,
- Are available from a US supplier (Nilfisk direct, Fisher Scientific, Grainger, Caliber Equipment, SweepScrub, IndustrialVacs, etc.) with a sourceable link or distributor contact.

Note that Nilfisk technical support has told us this 118EXP model is old enough that it is no longer fully supported and they cannot definitively confirm parts compatibility, so primary literature, NFPA standards interpretation, and cross-referencing alternative manufacturer (Ruwac, Tiger-Vac, VAC-U-MAX, Hafco) combustible-metal-dust accessories are particularly valuable. The serial-number sticker shows "L" prefix per Nilfisk telephone guidance.

Please cite NFPA standards by section number where possible, and provide direct product URLs for any recommended bags/liners.

To perform a new task using prior context: Follow-up to the previous LITERATURE_HIGH analysis of bagless operation of the Nilfisk CFM 118EXP with a bonded conductive PE liner for AlSi10Mg / silicon LPBF powder collection.

The user has the following practical-implementation questions arising from the §9.5 "Recommended Configuration" / emptying SOP recommendation in the prior answer ("Empty into a covered, grounded steel pail; operator wears grounding strap; empty daily; Class D extinguisher nearby; no water"):

1. **Empty-daily clarification.** What exactly should be emptied daily — the conductive PE liner inside the vacuum collection bin, or the outer grounded steel pail that the sealed liner is transferred into for transport / interim storage? Cite NFPA 484, NFPA 652, OSHA 1910, or related guidance for the time/quantity threshold. Is the "daily" cadence quantitative (e.g. based on a max accumulation mass or layer depth such as 1/32" per NFPA 654 housekeeping)? In a low-duty research lab generating, say, only tens of grams of AlSi10Mg / Si powder per week (not continuous production), is daily emptying still required, or is a fill-level / volume / time threshold (e.g. <25 % of bin, or weekly when contaminated) defensible?

2. **Outer pail vs existing waste container.** The lab already has a labeled chemical/solid hazardous-waste container provided by Environmental Health & Safety / Risk Management. They unscrew the lid each time they add waste. Can the sealed conductive liner from the vacuum simply be deposited into that existing EHS waste container (treating the liner as the primary containment), or is a *separate* dedicated grounded steel pail with a tight-fitting lid required as an intermediate interim container before final disposal? Specifically:
   - Is the intermediate steel pail a hard NFPA requirement, a best practice, or only relevant where a DHA identifies an interim staging/storage hazard?
   - Does the bond/ground status of the existing EHS container matter (typical EHS solid-waste containers are HDPE drums or carboard fiber drums, not conductive)?
   - If a separate grounded steel pail IS needed, what spec? (5 gal carbon-steel pail with bolted/lever-lock lid, bonded ground tab; UN-rated 1A2/1H2; ATEX/UL listed?) Recommend specific commercially available products, ideally with **Uline part numbers and direct uline.com product page URLs that you have verified exist**. Quantity-1 cost target ≤ $100.

3. **Conductive PE bin liner sourcing — validated Uline links.** Recommend **specific Uline SKUs** for carbon-loaded conductive (black) polyethylene bags or drum liners suitable for nesting in a vacuum collection bin with internal diameter ~320 mm (12.5") and depth ~25–30 cm (~10–12") of the Nilfisk CFM 118EXP. Spec requirements:
   - Surface resistivity ≤ 10⁶ Ω/square (conductive — ANSI/ESD S541 or MIL-PRF-81705 Type III; *not* Type II static-dissipative / pink antistatic)
   - Carbon-loaded polyethylene
   - 3–4 mil (or thicker) gauge
   - Size approximately 15"×18" or larger to fold over the bin rim with at least 4–6" of overhang
   - Quantity-100 case acceptable
   Provide the **Uline part number, exact product title, full direct URL (uline.com/Product/Detail/...), and current per-unit price** for the best 2–3 candidate SKUs. Also flag whether the Uline product description explicitly states carbon-loaded conductive (not just "antistatic" / static-dissipative, which is the wrong spec). Cross-reference Protective Packaging Corporation, Daubert Cromwell, International Plastics, or McMaster-Carr if a verified Uline SKU cannot be confirmed.

For all recommended part-page URLs, you MUST verify by actually fetching the page that the URL resolves to the intended product (Uline product pages have stable URLs of the form `https://www.uline.com/Product/Detail/<SKU>/...` and 404 if the SKU is wrong). Do NOT fabricate part numbers; if you cannot verify a URL, say so explicitly and suggest an alternative supplier or a search query the user can run themselves.

Context for grounding (from the prior answer): vacuum is a Nilfisk CFM 118EXP, CSA Class I Group D / Class II Groups E,F,G, stainless collection bin ~320 mm ID, used in a university research lab (BYU VCL) to collect AlSi10Mg (MIE 80 mJ at the most sensitive concentration, with sub-micron AM-process fines potentially <5 mJ) and silicon Hazard Class 1 dust. End user is a research student, not a powder-handling specialist; recommendations should be practically implementable in a normal university lab environment overseen by EHS and a faculty PI.

To perform a new task using prior context: 
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



# STANDARD OPERATING PROCEDURE: Safe Disposal of Collected Reactive Metal Powder from the Nilfisk CFM 118EXP Explosion-Proof Vacuum

**Facility**: BYU Vibration-Assisted Consolidation Laboratory (VCL)
**Applicable Powders**: AlSi10Mg, elemental Si, and other reactive/combustible metal powders
**Document Basis**: NFPA 484, NFPA 652, NFPA 654, NFPA 77, OSHA 29 CFR 1910.157, peer-reviewed combustible-dust safety literature

---

## REQUIRED PPE (Worn for All Steps Below)

- Safety glasses / splash goggles
- Nitrile gloves (non-sparking; no latex)
- ESD-grounding wrist strap connected to verified building ground
- N95 or P100 half-face respirator (metal-fume-rated)
- Cotton or FR-rated lab coat (no synthetic fabrics that accumulate static charge) (may1987firesandexplosions pages 4-6)
- Closed-toe shoes

## REQUIRED SAFETY EQUIPMENT AT STATION

- **Class D fire extinguisher** (Met-L-X, Lith-X, or equivalent) within 75 feet of the vacuum station per OSHA 29 CFR 1910.157 (cheremisinoff2014dustexplosionand pages 229-232)
- Grounded steel interim pail (Uline S-22507BL 3.5 gal with S-21135BL lever-lock lid) with bonding wire to building ground
- Spare conductive (carbon-loaded, black PE) bin liners
- Conductive cable ties or conductive twist-ties
- Digital multimeter for ground continuity verification

---

## SECTION 1: LINER REMOVAL PROCEDURE

NFPA 484 requires that combustible metal dust "not be allowed to accumulate" and that cleaning methods minimize dust-cloud generation (myers2013tutorialoncombustible pages 7-8, myers2013tutorialoncombustible pages 8-9). Even a 1 mm deposited layer of aluminum-alloy dust can be re-dispersed to form dust clouds at or above the minimum explosive concentration (~100 g/m³) (li2016acatastrophicaluminiumalloy pages 9-10).

**Step-by-step procedure:**

1. **Power off** the vacuum. Wait **≥ 60 seconds** for airborne powder inside the bin to settle.
2. **Don PPE** including ESD wrist strap connected to building ground.
3. **Verify grounding**: Confirm the bonding clip from the conductive liner to the vacuum bin body is still attached. Do not disconnect it yet.
4. **Disconnect the hose** from the vacuum inlet by gently pulling straight — do not shake or bang.
5. **Unlatch the collection bin** from the vacuum body. Slowly lower or tilt the bin to a stable work surface. Move slowly — avoid jerking motions that fluidize the powder.
6. **Inspect fill level**: If the liner is above ~25% full (roughly 2–3 cm depth of powder in the 320 mm ID bin), proceed to empty. If below 25%, it may remain in service until the next use session unless switching metals.
7. **Gooseneck seal**: While the bonding clip is still attached, gently gather the liner walls above the powder level, twist the gathered neck 2–3 full turns to form a "gooseneck," and secure with **two conductive cable ties** cinched tight around the twist. The powder is now sealed inside.
8. **Disconnect the bonding clip** from the liner. The sealed gooseneck prevents any powder release.
9. **Lift the sealed liner** out of the bin slowly and place it directly into the **grounded steel interim pail**. Do not drop it.
10. **Close the pail lid** immediately (lever-lock engagement).
11. **Install a fresh conductive liner** in the bin, fold 4–6 inches over the rim, and reattach the bonding clip from the new liner to the bin body.
12. **Reassemble** the vacuum: re-seat the bin, reconnect the hose, verify bonding clip contact.
13. **Log the event**: Date, operator initials, approximate mass collected (or "light dusting" / "~X grams"), powder type.

---

## SECTION 2: PASSIVATION — RECOMMENDATION AGAINST MINERAL OIL

**Recommendation: Do NOT passivate. Keep the collected powder dry and sealed.**

The literature and standards basis for this decision:

- Aluminum dust when damp may heat spontaneously; the hazard increases with fineness (cheremisinoff2014dustexplosionand pages 229-232). Adding any liquid to fine aluminum powder introduces the risk of exothermic reaction and hydrogen gas evolution: 2Al + 3H₂O → Al₂O₃ + 3H₂ (cheremisinoff2014dustexplosionand pages 229-232).
- Water and CO₂ are explicitly not recommended for aluminum fires because at combustible-metal fire temperatures (5,000–8,500°F) they dissociate into reactive gases (cheremisinoff2014dustexplosionand pages 215-219).
- Mineral oil passivation introduces a **new Class IB flammable-liquid hazard** onto an already-combustible solid. The mixing process itself risks aerosolizing powder. Oil-soaked metal fines are harder to classify under RCRA and more difficult for EHS to dispose of.
- No NFPA 484 section or retrieved peer-reviewed source requires or recommends mineral-oil passivation for small-quantity laboratory disposal of gas-atomized AlSi10Mg powder (which already has a native oxide passivation layer).

**For this low-quantity scenario (tens of grams/week)**: The sealed conductive liner inside a covered grounded steel pail provides adequate containment. The NFPA 484-derived guidance to handle metal powder in "covered containers" is satisfied without chemical treatment (cheremisinoff2014dustexplosionand pages 229-232).

---

## SECTION 3: INTERIM PAIL STORAGE

NFPA 484-derived guidance requires combustible metal powder residues to be "handled in covered containers" with compatible fire-extinguishing agents available in the storage area (cheremisinoff2014dustexplosionand pages 229-232).

**Rules for the grounded steel interim pail:**

1. **Maximum fill**: ≤ 50% of pail volumetric capacity. For the 3.5-gallon Uline S-22507BL pail, this means no more than ~6.6 liters of sealed liners. At tens of grams per week, this capacity lasts many weeks.
2. **Keep the pail grounded**: Maintain the bonding wire from the pail handle/rim to a verified building-ground point at all times.
3. **Keep the lid closed** except when adding or removing liners. Re-engage the lever lock immediately after each access.
4. **Keep dry**: Do not store the pail near sinks, eyewash stations, water lines, or any moisture source. Damp aluminum dust can self-heat (cheremisinoff2014dustexplosionand pages 229-232).
5. **Segregation**: Keep the pail away from water, acids, caustics, organic solvents, and oxidizing compounds. Specifically, do **not** store near iron oxide, copper oxide, or any metal-oxide powders (thermite precursors) (cadwallader2003dustcombustionsafety pages 32-34).
6. **Labeling**: Label the pail: *"COMBUSTIBLE METAL POWDER WASTE — AlSi10Mg / Silicon — Class D Fire Risk — NO WATER — Keep Dry and Sealed"*.
7. **Location**: Within 75 feet of a Class D extinguisher (cheremisinoff2014dustexplosionand pages 229-232). Not in a hallway, exit path, or high-traffic area.
8. **No inerting required** for this small-scale sealed-liner scenario: the sealed liner and closed pail lid limit air exchange sufficiently for tens of grams of powder.

---

## SECTION 4: TRANSFER TO FINAL DISPOSAL

1. **Transfer intact**: Place the entire sealed conductive liner into the BYU EHS unwanted-materials container **without opening the liner**. The sealed liner is the primary containment.
2. **Hazardous waste classification**: Fine aluminum powder (< 420 µm) capable of ignition through friction, moisture absorption, or spontaneous chemical change qualifies as RCRA characteristic hazardous waste under **D001 (Ignitability)**. Additionally, aluminum's vigorous reaction with water producing hydrogen gas may qualify it under **D003 (Reactivity)** per 40 CFR 261.23. The generator (BYU) must make the hazardous-waste determination per **40 CFR 262.11**. Silicon powder is less reactive but may also qualify as D001 for ignitability in dust-cloud form.
3. **Labeling on EHS container**: Work with BYU EHS to label the waste as: *"Ignitable/Reactive — Combustible Metal Powder — AlSi10Mg (Aluminum-Silicon-Magnesium Alloy) / Elemental Silicon — D001/D003 — NO WATER"*.
4. **Coordinate with BYU EHS**: Schedule regular pickups. At the low generation rate of this lab, monthly or bimonthly pickup is likely sufficient. Do not accumulate waste beyond the small-quantity generator time limits (90 days for SQG, 270 days for VSQG depending on BYU's generator status).

---

## SECTION 5: SWITCHING METALS — PAILS AND LINERS

**Rule: Use a dedicated conductive liner AND a dedicated interim pail per alloy family.**

The basis for this rule is the documented thermite-reaction hazard when aluminum powder is mixed with metal oxides. A DOE incident report documents ignition of ~50 g of aluminum + copper oxide powder in a polyethylene bottle, initiated by static discharge igniting an aluminum dust cloud that then triggered the thermite reaction (cadwallader2003dustcombustionsafety pages 32-34). Aluminum is highly reactive and difficult to inert (reding2018metaldustexplosion pages 4-5).

**Compatibility matrix:**

| Powder A | Powder B | Shared Container OK? | Rationale |
|---|---|---|---|
| AlSi10Mg | Elemental Si | **YES** | Silicon is a component of AlSi10Mg; no thermite or incompatibility risk |
| AlSi10Mg | Other Al alloys (AlSi12, Al6061, etc.) | **YES** | Same alloy family |
| AlSi10Mg | Iron-based alloys (316L SS, 17-4 PH, etc.) | **NO — NEVER** | Iron oxide on stainless particles + aluminum = thermite precursor (cadwallader2003dustcombustionsafety pages 32-34) |
| AlSi10Mg | Titanium alloys (Ti-6Al-4V, etc.) | **NO** | No thermite risk, but mixing changes waste characterization; use separate containers for traceability |
| AlSi10Mg | Copper alloys (CuCrZr, etc.) | **NO — NEVER** | Copper oxide + aluminum = thermite precursor (cadwallader2003dustcombustionsafety pages 32-34) |
| AlSi10Mg | Nickel alloys (IN718, IN625, etc.) | **NO** | Nickel oxide + aluminum can react; use separate containers |

---

## SECTION 6: SWITCHING METALS — VACUUM CLEANING

**Decision rule:** If switching between **incompatible alloy families** (e.g., aluminum → iron-based), the vacuum **must** be cleaned AND the filters replaced before the new powder is introduced. If staying within the **same alloy family** (e.g., AlSi10Mg → AlSi12 → Si), a dry wipe and visual inspection are sufficient.

**When full cleaning IS required (incompatible alloy switch):**
- Remove and dispose of the used main filter and both HEPA filters as contaminated waste (same waste stream as the powder).
- Clean the bin, hose interior, and wand per Section 7 below.
- Install new filters and new liner.
- Re-verify ground continuity.

**When full cleaning is NOT required (same alloy family):**
- Replace the conductive liner.
- Dry-wipe the bin interior with a lint-free cloth.
- Visual inspection: if visible powder residue is absent, the vacuum is ready for the next powder.

---

## SECTION 7: VACUUM CLEANING / PURIFICATION METHOD

NFPA 484 prohibits compressed-air blowdown except under a completed hazard analysis with all ignition sources controlled (myers2013tutorialoncombustible pages 8-9). Water must NOT be used to clean aluminum dust residues due to hydrogen generation and spontaneous-heating risks (cheremisinoff2014dustexplosionand pages 229-232).

**Cleaning procedure:**

1. **Power off** the vacuum, disconnect from power.
2. **Remove and bag** the used conductive liner (per Section 1).
3. **Bin cleaning**: Wipe the bin interior with a **lint-free cloth lightly dampened with isopropyl alcohol (IPA, 70% or 99%)**. IPA is non-water-reactive with aluminum, fast-evaporating, and effective at picking up fine residues. Do not use water, acetone (too flammable), or any chlorinated solvent.
4. **Hose cleaning**: Disconnect both ends. Run a lint-free cloth dampened with IPA through the bore using a pull-through rod or by gravity. Alternatively, for light residue, simply running the vacuum for 30 seconds with the clean hose attached to the reassembled unit (with a new liner and clean filters) will flush residual fines into the new liner.
5. **Wand and crevice tool**: Wipe exterior and interior with an IPA-dampened cloth. Inspect aluminum contact surfaces of couplers for oxide buildup; clean with a fine Scotch-Brite (non-metallic) pad if needed for electrical contact, then re-verify continuity.
6. **Filters**: 
   - **Replacement trigger**: Replace the antistatic main filter and HEPA filters (a) when switching to an incompatible alloy family, (b) when vacuum suction noticeably decreases, or (c) at minimum annually for light-duty use.
   - **Do NOT attempt to blow out or wash filters.** Bag used filters in a conductive liner and dispose through the same EHS waste stream.
   - The literature does not provide a specific loading-based replacement interval for ~40 µm metal powder at tens of grams per week; filter life under this light loading may be many months.
7. **Ground continuity re-verification**: After any filter change, reassembly, or cleaning, use a digital multimeter to verify:
   - Hose end-to-end: < 10 Ω (per manufacturer spec; ~4 Ω typical)
   - Bin body to building ground: < 1 Ω
   - Liner bonding clip to bin body: < 1 kΩ (target < 100 Ω)
   - Wand/coupler to hose ground wire: < 10 Ω
   
   Grounding resistance should be routinely checked and kept below 10⁶ Ω for grounding wires (johnson2008designingyourdust pages 7-8). All-metal grounding paths should be < 10 Ω (comer2020explosionventedequipment pages 140-146).

---

## ABSOLUTE PROHIBITIONS

| ⛔ DO NOT | Reason |
|---|---|
| Use water to clean aluminum residues or fight aluminum fires | H₂ generation; spontaneous heating of damp Al dust (cheremisinoff2014dustexplosionand pages 229-232) |
| Use CO₂ extinguisher on metal fires | CO₂ dissociates at metal-fire temperatures (cheremisinoff2014dustexplosionand pages 215-219) |
| Use compressed air to blow out the bin, hose, or filters | Creates explosive dust clouds (myers2013tutorialoncombustible pages 8-9) |
| Vacuum hot or glowing particles | Ignition source inside the collection bin |
| Mix aluminum-family and iron-family powders in the same container | Thermite reaction precursor (cadwallader2003dustcombustionsafety pages 32-34) |
| Passivate with mineral oil for disposal | Adds flammable-liquid hazard; complicates RCRA classification |
| Allow smoking, open flames, or uncontrolled ignition sources within 20 feet of vacuum or waste pail | Standard combustible-dust ignition-source control (myers2013tutorialoncombustible pages 8-9) |
| Use synthetic (nylon/polyester) cleaning rags | Static-charge accumulation (may1987firesandexplosions pages 4-6) |
| Leave the interim pail lid open | Moisture intrusion → self-heating; dust-cloud escape risk (cheremisinoff2014dustexplosionand pages 229-232) |

---

## MASTER CHECKLIST — OPERATOR QUICK REFERENCE

**Before Vacuuming:**
- [ ] Class D extinguisher visible and within 75 ft
- [ ] PPE on (glasses, nitrile gloves, respirator, grounding wrist strap, cotton coat)
- [ ] Conductive liner in bin, bonding clip attached
- [ ] Hose, wand, coupler connections secure
- [ ] Ground continuity verified with multimeter (< 10 Ω hose, < 1 Ω bin-to-earth)

**After Vacuuming (each session):**
- [ ] Power off, wait 60 seconds
- [ ] Check liner fill level — if > 25%, proceed to seal and remove
- [ ] Gooseneck twist, two conductive cable ties
- [ ] Disconnect bonding clip from liner
- [ ] Place sealed liner in grounded steel pail, close lid
- [ ] Install fresh liner, reattach bonding clip
- [ ] Log: date, initials, powder type, approximate mass

**Weekly (or at each EHS transfer):**
- [ ] Verify pail grounding wire connected
- [ ] Check pail fill level — if > 50%, transfer sealed liners to EHS
- [ ] Inspect Class D extinguisher gauge
- [ ] Verify vacuum ground continuity with multimeter

**When Switching Incompatible Alloy Families:**
- [ ] Remove and bag used liner
- [ ] Replace main filter and both HEPA filters
- [ ] IPA-wipe bin interior
- [ ] Clean hose bore
- [ ] Install fresh liner and new filters
- [ ] Re-verify all ground continuity
- [ ] Use a dedicated fresh interim pail for the new alloy family
- [ ] Log: "Alloy switch from [X] to [Y], date, filters replaced"

---

## CITATIONS AND STANDARDS REFERENCED

The procedures in this SOP are synthesized from the following sources:

- **NFPA 484** — Standard for Combustible Metals, Metal Dusts, and Metal Powders. Key sections: §15.3.1.1 (grounding/bonding per NFPA 77), §15.3.1.2 (personnel grounding for MIE < 30 mJ), §15.3.1.5 (portable vacuums comply with §13.4) (bruceUnknownyeartechnicalcommitteeon pages 29-32).
- **NFPA 654** — Standard for Prevention of Fire and Dust Explosions from Manufacturing, Processing, and Handling of Combustible Particulate Solids. 1/32-inch layer-depth housekeeping criterion (rodgers2012applicationofthe pages 8-9, rodgers2012applicationofthe pages 7-8, rodgers2012applicationofthe pages 3-4, rodgers2012applicationofthe pages 1-2).
- **NFPA 77** — Recommended Practice on Static Electricity.
- **OSHA 29 CFR 1910.157** — Portable fire extinguishers, Class D placement within 75 feet (cheremisinoff2014dustexplosionand pages 229-232).
- **40 CFR 261.21/261.23** — RCRA characteristic hazardous waste: D001 Ignitability, D003 Reactivity.
- **40 CFR 262.11** — Hazardous waste determination by generators.
- Cheremisinoff (2014), *Dust Explosion and Fire Prevention Handbook* (cheremisinoff2014dustexplosionand pages 229-232).
- Cadwallader (2003), DOE occurrence report on thermite ignition of Al + CuO powder (cadwallader2003dustcombustionsafety pages 32-34).
- Reding & Shiflett (2018), Metal Dust Explosion Hazards: A Technical Review (reding2018metaldustexplosion pages 4-5).
- Li et al. (2016), 1 mm aluminum dust layer resuspension to ~100 g/m³ (li2016acatastrophicaluminiumalloy pages 9-10).
- Johnson (2008), dust collection grounding requirements (johnson2008designingyourdust pages 7-8).
- Comer (2020), filter bag grounding and operator grounding at MIE < 30 mJ (comer2020explosionventedequipment pages 140-146).
- Myers & Ibarreta (2013), NFPA combustible dust housekeeping thresholds (myers2013tutorialoncombustible pages 7-8, myers2013tutorialoncombustible pages 8-9).
- May & Berard (1987), aluminum dust fire/explosion hazards, synthetic fabric prohibition (may1987firesandexplosions pages 4-6).
- Britton (2010), *Avoiding Static Ignition Hazards in Chemical Operations* — container grounding, FIBC classification (britton2010avoidingstaticignition pages 222-225).

**Disclaimer**: This SOP is synthesized from the cited literature and regulatory sources. It should be reviewed and approved by BYU EHS and the faculty PI before implementation. The user's specific Dust Hazard Analysis (DHA) per NFPA 652 should incorporate these procedures and may impose additional site-specific requirements.


References

1. (may1987firesandexplosions pages 4-6): David C. May and David L. Berard. Fires and explosions associated with aluminum dust from finishing operations. Journal of Hazardous Materials, 17:81-88, Dec 1987. URL: https://doi.org/10.1016/0304-3894(87)85043-4, doi:10.1016/0304-3894(87)85043-4. This article has 35 citations and is from a highest quality peer-reviewed journal.

2. (cheremisinoff2014dustexplosionand pages 229-232): Nicholas P. Cheremisinoff. Dust explosion and fire prevention handbook: a guide to good industry practices. ArXiv, Jul 2014. URL: https://doi.org/10.1002/9781118773567, doi:10.1002/9781118773567. This article has 34 citations.

3. (myers2013tutorialoncombustible pages 7-8): Timothy J. Myers and Alfonso F. Ibarreta. Tutorial on combustible dust. Process Safety Progress, 32:298-306, Sep 2013. URL: https://doi.org/10.1002/prs.11596, doi:10.1002/prs.11596. This article has 8 citations and is from a peer-reviewed journal.

4. (myers2013tutorialoncombustible pages 8-9): Timothy J. Myers and Alfonso F. Ibarreta. Tutorial on combustible dust. Process Safety Progress, 32:298-306, Sep 2013. URL: https://doi.org/10.1002/prs.11596, doi:10.1002/prs.11596. This article has 8 citations and is from a peer-reviewed journal.

5. (li2016acatastrophicaluminiumalloy pages 9-10): G. Li, H.-X. Yang, C.-M. Yuan, and R.K. Eckhoff. A catastrophic aluminium-alloy dust explosion in china. Journal of Loss Prevention in The Process Industries, 39:121-130, Jan 2016. URL: https://doi.org/10.1016/j.jlp.2015.11.013, doi:10.1016/j.jlp.2015.11.013. This article has 263 citations and is from a peer-reviewed journal.

6. (cheremisinoff2014dustexplosionand pages 215-219): Nicholas P. Cheremisinoff. Dust explosion and fire prevention handbook: a guide to good industry practices. ArXiv, Jul 2014. URL: https://doi.org/10.1002/9781118773567, doi:10.1002/9781118773567. This article has 34 citations.

7. (cadwallader2003dustcombustionsafety pages 32-34): L. C. Cadwallader. Dust combustion safety issues for fusion applications. ArXiv, May 2003. URL: https://doi.org/10.2172/910731, doi:10.2172/910731. This article has 2 citations.

8. (reding2018metaldustexplosion pages 4-5): Nicholas S. Reding and Mark B. Shiflett. Metal dust explosion hazards: a technical review. Industrial & Engineering Chemistry Research, 57:11473-11482, Aug 2018. URL: https://doi.org/10.1021/acs.iecr.8b02465, doi:10.1021/acs.iecr.8b02465. This article has 46 citations and is from a peer-reviewed journal.

9. (johnson2008designingyourdust pages 7-8): GQ Johnson. Designing your dust collection system to meet nfpa standards—part i. Unknown journal, 2008.

10. (comer2020explosionventedequipment pages 140-146): Robert C. Comer. Explosion vented equipment system protection guide. ArXiv, Nov 2020. URL: https://doi.org/10.1002/9781119640059, doi:10.1002/9781119640059. This article has 0 citations.

11. (bruceUnknownyeartechnicalcommitteeon pages 29-32): LMD Bruce. Technical committee on combustible metals and metal dusts nfpa 484 second draft meeting agenda july 15-17, 2020 11: 00 am–5: 00 pm …. Unknown journal, Unknown year.

12. (rodgers2012applicationofthe pages 8-9): Samuel A. Rodgers. Application of the nfpa 654 dust layer thickness criteria—recognizing the hazard. Process Safety Progress, 31:24-35, Mar 2012. URL: https://doi.org/10.1002/prs.10500, doi:10.1002/prs.10500. This article has 3 citations and is from a peer-reviewed journal.

13. (rodgers2012applicationofthe pages 7-8): Samuel A. Rodgers. Application of the nfpa 654 dust layer thickness criteria—recognizing the hazard. Process Safety Progress, 31:24-35, Mar 2012. URL: https://doi.org/10.1002/prs.10500, doi:10.1002/prs.10500. This article has 3 citations and is from a peer-reviewed journal.

14. (rodgers2012applicationofthe pages 3-4): Samuel A. Rodgers. Application of the nfpa 654 dust layer thickness criteria—recognizing the hazard. Process Safety Progress, 31:24-35, Mar 2012. URL: https://doi.org/10.1002/prs.10500, doi:10.1002/prs.10500. This article has 3 citations and is from a peer-reviewed journal.

15. (rodgers2012applicationofthe pages 1-2): Samuel A. Rodgers. Application of the nfpa 654 dust layer thickness criteria—recognizing the hazard. Process Safety Progress, 31:24-35, Mar 2012. URL: https://doi.org/10.1002/prs.10500, doi:10.1002/prs.10500. This article has 3 citations and is from a peer-reviewed journal.

16. (britton2010avoidingstaticignition pages 222-225): Laurence G. Britton. Avoiding static ignition hazards in chemical operations: a ccps concept book. ArXiv, Sep 2010. URL: https://doi.org/10.1002/9780470935408, doi:10.1002/9780470935408. This article has 171 citations.