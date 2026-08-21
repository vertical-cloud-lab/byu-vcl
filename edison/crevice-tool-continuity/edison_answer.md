
# Verification of Nilfisk CFM 118EXP Crevice Tool Ground-Continuity Anomaly

---

## CLAIM 1: MEASUREMENT INTERPRETATION

**Verdict: CORRECT**

The "OL on REL-locked low range, megohms with autoranging" behavior is a genuine reading of a high surface resistance (≥ 10⁶ Ω), not a meter artifact. A standard bench DMM applies an open-circuit test voltage of typically 0.5–3 V on its resistance ranges. Aluminum oxide (Al₂O₃) — the material produced by anodization — is a high-quality dielectric insulator with the following measured properties:

- **Resistivity**: > 10¹² Ω·cm at moderate electric fields, with leakage current densities < 10⁻⁷ A/cm² at 0.3 MV/cm (kolodzey2000electricalconductionand pages 1-2). Published values for sapphire (crystalline Al₂O₃) exceed 10¹⁵ Ω·cm (kolodzey2000electricalconductionand pages 3-5).
- **Dielectric breakdown field strength**: 4–5 MV/cm for thermally produced Al₂O₃ (kolodzey2000electricalconductionand pages 1-2, kolodzey2000electricalconductionand pages 3-5). For a typical sulfuric-acid clear anodize layer of 5–25 µm thickness, this corresponds to a **breakdown voltage of 200–1,250 V** — orders of magnitude above any DMM test voltage.
- **Dielectric constant**: 3–9 depending on crystallinity and processing (kolodzey2000electricalconductionand pages 2-3, kolodzey2000electricalconductionand pages 5-6).

A few-nanometer **native oxide** (the natural Al₂O₃ that forms spontaneously on all aluminum in air) is only ~2–5 nm thick. At a breakdown field of ~5 MV/cm, a 5 nm native oxide breaks down at ~2.5 V — easily pierced by a DMM's test voltage and by normal probe pressure. An engineered anodize layer is **1,000–5,000× thicker** than native oxide and therefore cannot be penetrated by the DMM. The fact that **light scratching does not restore conductivity** is diagnostic: anodize (Mohs ~9, Vickers ~400–600 HV) is harder than the underlying aluminum alloy (Mohs ~2.5–3), so a fingernail, probe drag, or light abrasion does not reach bright metal. This is pathognomonic of an engineered dielectric coating, not native oxide or machining oil.

**Your reading is real. The crevice tool surface is insulating at ≥ 10⁶ Ω.**

---

## CLAIM 2: IS IT ANODIZED?

**Verdict: CORRECT — most likely explanation, though no specific documentation of the 01768900 finish was found**

The symptom set — solid aluminum alloy body, silvery/clear metallic appearance identical to the bare-aluminum wand, megohm surface resistance surviving light scratches, and a Nilfisk support representative describing it as "just aluminum" — is fully consistent with **Type II sulfuric-acid clear (natural) anodize** per MIL-A-8625F. Clear anodize is transparent, preserves the metallic appearance, is the most common commercial anodize process for aluminum, and produces the exact dielectric behavior observed.

No documentation of the 01768900 crevice tool's specified finish was found in any retrieved literature, patent, or manufacturer database. Nilfisk's own technical support did not identify the finish. **The literature is silent on this specific part number's surface treatment.** However, the following reasoning strongly favors anodize over alternatives:

- **Bare mill aluminum with native oxide only**: Would show < 1 Ω surface resistance under probe pressure. Eliminated by the megohm reading.
- **Carbon-loaded static-dissipative plastic that looks metallic**: Possible in theory, but the user has confirmed the part is unambiguously solid metal (machined aluminum), not plastic. Eliminated.
- **Conductive coating over aluminum** (e.g., nickel plating, chromate conversion): Would show low resistance. Eliminated.
- **Clear anodize**: Matches all observations. This is the most likely explanation by exclusion.

It is plausible that Nilfisk anodizes the crevice tool for corrosion protection and abrasion resistance (reasonable for a tool that contacts hard surfaces) without considering the static-control implication, or that the tool was designed for non-EXP applications and is shared across product lines.

---

## CLAIM 3: IS AN ANODIZED EXP TOOL A DEFECT / CONTRADICTION?

**Verdict: CORRECT-WITH-CAVEAT — the anodize itself is not necessarily a hazard IF the tool body is properly bonded to ground through the joint, but the as-supplied failure to bond IS a non-conformance**

### 3a. Isolated-conductor hazard

An electrically conductive mass (aluminum crevice tool) that is **insulated from ground** by a dielectric coating is the textbook definition of an **isolated conductor** — a recognized ignition hazard in combustible-dust environments. Charge can accumulate on the isolated conductor from triboelectric contact with powder, and the stored energy can discharge as an incendive spark when the conductor approaches a grounded surface or the operator. All metal components in the airstream path must be electrically bonded and grounded; metal components must not be allowed to act as isolated capacitors (comer2020explosionventedequipment pages 140-146).

### 3b. Propagating brush discharge (PBD) from the anodize layer

Once the tool body is properly **bonded to ground through a clean metal-to-metal joint at the socket**, the question becomes: is the anodize layer on the outer surface itself a PBD hazard?

The established criterion is that propagating brush discharges cannot be produced when the wall breakdown voltage is below **4 kV** (Glor's criterion) (britton1993statichazardsusing pages 10-12, britton2010avoidingstaticignition pages 53-56). For sulfuric-acid clear anodize:

- Typical thickness: 5–25 µm
- Breakdown field: ~4–5 MV/cm (kolodzey2000electricalconductionand pages 1-2, kolodzey2000electricalconductionand pages 3-5)
- Breakdown voltage at 25 µm: ~100–125 V; at 5 µm: ~20–25 V

These breakdown voltages are **far below the 4 kV PBD threshold**. Therefore, even if the anodize layer is fully insulating, its breakdown voltage (~20–125 V) is well below 4 kV, meaning **propagating brush discharges cannot develop on it**. Any charge deposited on the outer anodize surface will punch through the thin dielectric and drain to the grounded aluminum substrate before reaching PBD-capable potentials.

**Conclusion**: A tens-of-microns anodized skin over **grounded** aluminum is NOT a PBD hazard. The anodize is too thin to support the 4 kV potential needed for PBD. The only real requirement is that the assembled tool not float — i.e., the aluminum body must be bonded to ground through the socket joint (britton2010avoidingstaticignition pages 53-56).

### 3b (AS-SUPPLIED FAILURE)

**Verdict: CORRECT — this is a non-conforming condition**

The OEM manual (UL 1213 par. 22) requires ≤ 0.1 Ω tool-to-wand before each use. The crevice tool reads **open** at the socket joint as supplied. This means:

1. The tool fails the OEM's own acceptance criterion.
2. If used as-supplied, the tool body would be an isolated conductor in the airstream — an ignition hazard in a Class II hazardous location.
3. This is an out-of-spec / non-conforming condition for a tool sold as part of an EXP-certified system.

**Defensible courses of action** (in order of preference):
1. **Contact Nilfisk industrial vacuum division** (callback pending) and request either (a) a confirmed-conductive replacement crevice tool, or (b) written confirmation that the anodized tool is intended to bond through its socket when properly seated.
2. **Field-remediate the joint** per Claim 5 below, documented in the DHA.
3. **Replace** with a confirmed-conductive third-party crevice tool of the same diameter.

---

## CLAIM 4: GOVERNING ACCEPTANCE CRITERION

**Verdict: CORRECT-WITH-CAVEAT — the 0.1 Ω figure is a per-connection UL 1213 criterion, but the conductive hose is a different class of component**

The OEM manual's ≤ 0.1 Ω criterion (UL 1213 par. 22) applies to **metal-to-metal connections** — tool to wand, wand to coupler, coupler to inlet. These are hard-metal joints where 0.1 Ω is achievable and verifiable.

The conductive hose is a fundamentally different component: a polymer tube with embedded conductive elements (carbon loading and/or wire helix). Its specification is R ≤ 10⁴ Ω (manufacturer-confirmed), and the measured ~4 Ω is well within that spec. This is consistent with NFPA 77 guidance that grounding resistance should be routinely checked and kept below 10⁶ Ω for grounding wires, with < 10 Ω for continuous all-metal ground paths (johnson2008designingyourdust pages 7-8, comer2020explosionventedequipment pages 140-146).

**Reconciliation**: The 0.1 Ω criterion applies **per metal-to-metal connection**. The hose is not a metal-to-metal connection — it is a listed conductive component with its own resistance specification. The correct interpretation is:

| Connection | Criterion | Your Reading | Verdict |
|---|---|---|---|
| Tool → wand (metal-to-metal) | ≤ 0.1 Ω per UL 1213 | Dust brush: 0.03 Ω; Crevice: OPEN | Brush PASS; Crevice FAIL |
| Wand → coupler (metal-to-metal) | ≤ 0.1 Ω | < 0.1 Ω | PASS |
| Hose end-to-end (conductive polymer) | ≤ 10⁴ Ω per manufacturer spec; < 10 Ω per NFPA 77 bonded-system criterion | ~4 Ω | PASS |
| Bin/body → building ground | < 1 Ω (metal-to-metal) | < 1 Ω | PASS |
| Liner → ground (conductive polymer contact) | < 1 kΩ (per Britton guidance for conductive objects near powder) | < 1 kΩ measured | PASS |

**A 4 Ω conductive hose does NOT violate the 0.1 Ω per-connection criterion** because the hose is not a "connection" in the UL 1213 sense — it is a listed conductive component with bulk resistance. Your system passes at every point except the crevice tool joint.

---

## CLAIM 5: REMEDIATION

**Verdict: CORRECT-WITH-CAVEAT**

The correct fix is to **bond the joint** (restore metal-to-metal contact at the socket interface), NOT to strip the entire tool.

### Recommended diagnostic sequence (before any abrasion):

1. **Check for anodize rack marks**: The anodizing process requires electrical contact to the part. There are typically small uncoated spots where the anodizing rack touched the part — often inside the bore, on internal flats, or at sharp edges. Probe these locations with the DMM. If you find a bare-metal spot reading < 0.1 Ω inside the socket bore, the tool may bond when fully seated on the wand with firm pressure.

2. **Confirm full tight seating**: Push the crevice tool fully onto the wand with firm hand pressure. The socket bore may have a tighter interference fit that scrapes through the anodize. Re-measure at full seating.

3. **Contact cleaner**: Apply plastic-safe electronic contact cleaner (e.g., CRC QD Contact Cleaner) to the socket bore and the wand tip, seat firmly, and re-measure. This removes any oil film but will not penetrate anodize.

4. **Fine non-metallic abrasion of mating surfaces ONLY**: If the above fail, use a fine non-metallic Scotch-Brite pad (gray or maroon, NOT green — green is too aggressive) to lightly abrade **only the inner bore of the crevice tool socket** and the mating section of the wand tip. The goal is to break through the anodize layer at the contact band (~5–10 mm) where the tool seats on the wand. This is a minimal, targeted intervention.

5. **Re-verify**: After seating, the tool-to-wand resistance must read ≤ 0.1 Ω per UL 1213.

### Does this nullify certification?

The OEM manual states "any alteration to this equipment by a third party will nullify its certification." Strictly interpreted, abrading the socket bore is an "alteration." However:

- The alteration is **restoring the tool to the condition it should have been in at delivery** (i.e., bondable to ground per UL 1213 par. 22). It is corrective, not additive.
- The alteration does not change the tool's material, geometry, or function — it removes a coating from the mating surface to restore electrical continuity.
- **Document the remediation** in the DHA: "Crevice tool P/N 01768900 delivered with anodized socket bore preventing ground continuity per UL 1213 par. 22. Socket bore lightly abraded to bright metal at contact band. Post-remediation resistance: [value] Ω. DHA approved by PI and EHS on [date]."

### When to STOP and REPLACE:

If the socket bore abrasion does not achieve ≤ 0.1 Ω tool-to-wand (e.g., if the geometry prevents clean metal-to-metal contact, or if the anodize was applied after machining and there is a dimensional mismatch), **do not escalate further**. Instead, replace the tool with a confirmed-conductive crevice nozzle from a third-party ESD/EXP vacuum accessories supplier (e.g., Tiger-Vac, Ruwac, or a generic conductive aluminum crevice tool of the same bore diameter).

---

## CLAIM 6: SAFETY OF THE DIAGNOSTIC ITSELF

**Verdict: CORRECT**

Aluminum abrasion/grinding dust is itself a combustible-dust hazard — fine aluminum particles generated by abrading the tool surface are the same class of material you are trying to safely collect. The abrade-to-bright-metal test must be done:

- **BEFORE** the tool ever contacts AlSi10Mg powder.
- **Away from** any powder, powder containers, the vacuum collection bin, and any ignition sources.
- With abrasion debris captured by a **damp (IPA-dampened, not water) lint-free wipe** immediately after abrasion. The quantity of dust from lightly abrading a ~5 mm contact band is negligible (micrograms), but the principle of not creating uncontrolled combustible-dust accumulations applies (myers2013tutorialoncombustible pages 8-9).
- Wear N95 respirator and nitrile gloves during abrasion.
- Do not use power tools (grinder, Dremel) — hand abrasion with Scotch-Brite only.

---

## IMPORTANT OMISSIONS

### OMISSION A: DUST BRUSH VERIFICATION

Your procedure mentions the dust brush passed at 0.03 Ω tool-to-wand, which is good. However, you should also verify that:
1. The **brush bristles themselves** are the conductive/EXP variant (not nylon or natural fiber). Conductive bristles are typically carbon-loaded or stainless-steel wire. If the bristles are non-conductive, they can accumulate charge and produce brush discharges even though the ferrule is bonded.
2. The **ferrule-to-bristle-tip** path is conductive. Some brushes have conductive ferrules but non-conductive bristles, which creates an isolated-conductor situation at the bristle tips.

### OMISSION B: STANDARDIZED PROBE POINTS

For **repeatable** pre-use continuity checks, mark standardized probe points on each component with a small paint dot or engraving (e.g., "probe here" marks on the wand, coupler, crevice tool body, brush ferrule). This ensures that different operators measure at the same locations and that readings are comparable session-to-session. Document the expected resistance at each probe point in the SOP.

### OMISSION C: EXPECTED PER-CONNECTION RESISTANCES TABLE

Your SOP should include a table of expected per-connection resistances (as in the table in Claim 4 above) so that a student operator has a clear pass/fail reference without needing to interpret the UL 1213 standard.

### OMISSION D: GATE THE FIRST LIVE RUN ON ALL CONNECTIONS PASSING

**A single non-conforming tool should gate the entire first live run.** Do not use the crevice tool until it passes ≤ 0.1 Ω tool-to-wand. The first run can proceed with the dust brush alone (which passes), but the crevice tool must be remediated or replaced before it enters service. This is the conservative position consistent with UL 1213 par. 22 and NFPA 484 §15.3.1.1 (bruceUnknownyeartechnicalcommitteeon pages 29-32, comer2020explosionventedequipment pages 140-146).

### OMISSION E: DOCUMENT THE ANOMALY FOR NILFISK

File a formal product-quality inquiry with Nilfisk (not just a phone call) documenting: (1) the part number, (2) the measured resistance, (3) the UL 1213 par. 22 criterion, and (4) the hypothesis that the tool is anodized. Request either a replacement with a confirmed-bare or conductive-coated crevice tool, or a written engineering statement confirming that the anodize is intentional and that the tool bonds through its socket when properly seated. This creates a record that protects the lab if there is ever an audit or incident investigation.

---

## SUMMARY TABLE

| Claim | Verdict | Key Finding |
|---|---|---|
| 1. Measurement interpretation | **CORRECT** | OL/megohm is a real reading; Al₂O₃ anodize has resistivity > 10¹² Ω·cm and breakdown voltage 20–1,250 V, far above DMM test voltage; light scratches cannot penetrate Mohs 9 anodize |
| 2. Is it anodized? | **CORRECT** (most likely; no P/N documentation found) | Clear sulfuric-acid anodize matches all symptoms; alternatives eliminated; literature silent on P/N 01768900 finish |
| 3. Anodized EXP tool — defect? | **CORRECT-WITH-CAVEAT** | Anodize over grounded metal is NOT a PBD hazard (breakdown voltage ~20–125 V ≪ 4 kV PBD threshold); BUT the as-supplied socket failure to bond IS a UL 1213 non-conformance |
| 3b. As-supplied failure | **CORRECT** | Tool fails OEM's own ≤ 0.1 Ω criterion; this is non-conforming; do not use until remediated |
| 4. Governing acceptance criterion | **CORRECT-WITH-CAVEAT** | 0.1 Ω applies per metal-to-metal connection; the ~4 Ω conductive hose is a listed component with its own spec (≤ 10⁴ Ω) and does not violate the per-connection criterion |
| 5. Remediation | **CORRECT-WITH-CAVEAT** | Bond the joint (abrade socket bore to bright metal); document in DHA; if unsuccessful, replace the tool; do not strip the entire working surface |
| 6. Safety of diagnostic | **CORRECT** | Abrade before powder contact, away from ignition sources, capture debris with IPA-dampened wipe |

**Critical actions before the first live run:**
1. **Gate**: Do NOT use the crevice tool until it passes ≤ 0.1 Ω tool-to-wand. Proceed with dust brush only if needed.
2. **Diagnose**: Check for rack marks, full seating, and contact cleaner before resorting to abrasion.
3. **Remediate or replace**: Abrade socket bore per Claim 5 sequence. If unsuccessful, replace.
4. **Document**: File anomaly report with Nilfisk and record remediation in DHA.
5. **Verify brush bristles**: Confirm the dust brush has conductive (not nylon) bristles.
