# Powder Disposal SOP — Nilfisk CFM 118EXP Vacuum (AlSi10Mg / Si / Reactive Metals)

> **Provenance.** This SOP was synthesized by an Edison Scientific `LITERATURE_HIGH` query
> (task `56c08a19-eebc-477b-a627-bf82808189ec`, a continuation of the prior bag/liner and
> emptying-cadence reviews `ce98952d-…` → `8288144a-…`; 15 cited references). It answers
> Ronnie's request in
> [PR #80 comment 4833708843](https://github.com/vertical-cloud-lab/byu-vcl/pull/80#issuecomment-4833708843)
> for a single, citation-backed disposal procedure covering liner removal, passivation,
> interim-pail storage, transfer to EHS, metal-switching rules, and vacuum cleaning.
> Direct link to the Edison response:
> <https://platform.edisonscientific.com/trajectories/56c08a19-eebc-477b-a627-bf82808189ec>
> (raw answer + task JSON archived under [`edison/powder-disposal-sop/`](edison/powder-disposal-sop/)).
>
> ⚠️ **This is AI-synthesized guidance.** It must be reviewed and approved by BYU EHS / Risk
> Management and the faculty PI, and incorporated into a site-specific NFPA 652 Dust Hazard
> Analysis (DHA), **before** use with live powder.

---

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
