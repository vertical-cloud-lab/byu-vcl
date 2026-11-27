HF-free recommendation, first line: do not build this workflow around HF, and do not treat HBF4 as truly HF-free. For a first-time university lab, the clean split is:

- Route A, if silicon itself must be quantified: use lithium metaborate (LiBO2) fusion followed by acid dissolution and heavy dilution.
- Route B, if silicon does not need to be quantified: use HCl/HNO3 or aqua regia digestion of the alloy, then remove the insoluble Si-rich residue before ICP-MS.
- For low-Si 1100 Al wire: use a simple non-HF acid digestion; no fusion needed.

That is the most consistent conclusion across the four reviews. They agree on the core chemistry: ordinary mineral acids dissolve Al well, but not elemental Si / Si-rich phases; fluoride chemistry solves that, but your lab constraint rules it out. The only genuinely HF-free total-digestion route with a plausible path to quantitative Si is borate fusion. Acid-only routes are fine for Al and many trace metals, but they are partial digestions for AlSi10Mg because Si remains in the residue.

Executive summary

1. Recommended decision
- Adopt a two-route workflow from the start.
- Use Route A (LiBO2 fusion) only for samples where total Si is required: AlSi10Mg when Si must be reported, and silicon powder.
- Use Route B (HNO3 + HCl / aqua regia digestion with residue removal) for routine alloy screening when Si is not required.
- Use a simple HCl-based digestion for 1100 aluminum wire.

2. Why this is the right split
- All four reviews converge that Al dissolves readily in HCl-containing media, while Si-rich phases do not dissolve in HNO3/HCl alone.
- The HF-free digestion review identifies LiBO2 fusion as the strongest HF-free route for quantitative total Si because the silica/silicon is retained in the melt and then dissolved after fusion, unlike Na2CO3 routes where silica can separate on acidification.
- The acid digestion review and the HF-free review both indicate that acid-only digestion of Al-Si alloys leaves a Si-rich residue, so any such method is partial unless the residue is separately processed.
- The measurement and QA/QC reviews agree that high dissolved solids are the main ICP-MS problem, so the fusion route is chemically complete but analytically expensive in dilution and matrix handling.

3. What not to do
- Do not choose HBF4 as your default “HF-free” method. It hydrolyzes to HF on heating/storage and should be treated as a fluoride method with HF-equivalent precautions. If the lab’s hard constraint is to avoid HF entirely if possible, HBF4 fails the spirit of that constraint.
- Do not use NaOH/KOH dissolution as a total-digestion method for AlSi10Mg. It dissolves Al, but Si recovery is unreliable and aluminosilicate precipitation is a built-in failure mode.
- Do not claim “total elemental composition” from aqua regia digestion of AlSi10Mg after filtering residue. That is a partial digestion by definition.

Step-by-step SOP outline

Route A. HF-free total digestion when Si must be quantified
Use for: AlSi10Mg when total Si is required; silicon powder; any sample where a clear, particle-free solution must still represent the full Si inventory.

A1. Scope and principle
- Principle: convert the sample into a borate melt using LiBO2, then dissolve the cooled bead in dilute acid.
- Strength: best-supported HF-free path to quantitative Si.
- Cost: high Li/B matrix, high dilution, no B or Li quantitation from the same digest, worse trace-element detection limits than acid-only digestion.

A2. Sample mass and fusion setup
- Start conservatively at 0.10 g sample for method setup.
- Acceptable development range from the reviews: about 0.10 to 0.25 g sample.
- Use high-purity LiBO2 flux at about 8:1 flux:sample by mass.
  - Example startup condition: 0.100 g sample + 0.800 g LiBO2.
  - Literature example summarized in the review: 0.250 g + 2.000 g LiBO2.
- Use Pt crucibles. Avoid glass. Keep crucibles dedicated to low-contamination trace work.
- Use a flux-sample-flux sandwich if needed for better contact.

A3. Fusion conditions
- Furnace: 950 to 1050 °C.
- Hold: about 2 to 2.5 h, or until a clear homogeneous melt is obtained.
- For first setup, start near 950 °C and 2.5 h because that is the better-documented condition in the review.
- Cool enough to handle; transfer bead quantitatively.

A4. Dissolution of fused bead
- Dissolve the bead in dilute mineral acid in fluoropolymer or acid-clean PP/PFA ware.
- Practical startup: 100 to 200 mL of about 2.5 to 5% HCl.
- Use stirring or ultrasonic assistance until the bead is completely dissolved.
- The target is a clear, particle-free solution. If particles remain, do not ignore them. Investigate incomplete fusion, crucible carryover, or contamination before proceeding.

A5. Dilution strategy after fusion
This route adds a lot of Li and B. That is the main analytical tax.
- First, make the fusion dissolution a stock digest.
- Then prepare at least two measurement dilutions:
  - Major-elements dilution for Al, Si, Mg: typically a much higher dilution.
  - Trace-elements dilution for Fe, Cu, Mn, Zn, Ti, Cr, Ni, etc.: as low as the instrument tolerates while keeping total dissolved solids manageable.
- The reviews repeatedly recommend keeping final TDS around or below roughly 0.1 to 0.2% for conventional ICP-MS robustness.
- Because the fusion stock contains both original sample dissolved solids and added Li/B flux, extra dilution versus Route B is unavoidable.

A6. Matrix consequences of fusion and how to handle them
- Li and B are introduced by the flux, so this digest cannot be used to quantify Li or B.
- Li/B raise blank burden and suppress sensitivity through matrix loading.
- Prepare matrix-matched standards with the same acid composition and approximately the same dissolved LiBO2 contribution as the final sample dilutions.
- Use online internal standards for every solution.
- Expect trace-element limits of quantification to worsen compared with Route B because of required dilution.
- For very low-level trace work, consider running Route B in parallel for better sensitivity on trace metals, while using Route A only for Si and for total-composition confirmation.

A7. ICP-MS measurement block for Route A digests
Recommended first-pass Agilent 8900 method blocks synthesized from the measurement review:
- He KED mode for routine trace metals: Fe, Cu, Mn, Zn, Ni, Co, Pb, Sn, Ga, Mo.
- H2 on-mass for Si: 28→28.
  - This is the preferred starting Si method in the review because Si+ is relatively unreactive while N2+/CO+ interferences are reduced.
  - If blank/background at m/z 28 is still problematic, validate O2 mass-shift as an alternate Si method.
- O2 mass-shift for Cr: 52→68.
- NH3 mode for Ti: 48→114 cluster-shift; for V: 51→51 if V is required.
- Mg can be measured at 24 with careful background control; confirm with 25 or 26 during development if needed.
- Al at 27 is possible only on very high dilution because it is the dominant matrix element.

A8. Instrument setup for Route A
Use robust plasma conditions because matrix tolerance matters more than squeezing out the last bit of sensitivity.
- RF power: about 1500 to 1600 W.
- Sample uptake: low-flow PFA nebulizer.
- Peltier-cooled spray chamber if available.
- Quartz torch is acceptable here because no free fluoride is intended, but the main risk is cone deposition from matrix load.
- Tune for low oxide and doubly charged ratios before runs.
- Watch cone loading closely; LiBO2 fusion digests will dirty the interface faster than acid-only digests.

A9. QA/QC for Route A
- Reagent blank and full fusion blank with each batch.
- CRM with similar matrix whenever possible.
- Matrix spike / matrix spike duplicate on at least one representative sample per batch.
- Continuing calibration verification every 10 samples.
- Internal-standard recovery acceptance: 80 to 120% of initial response is a practical startup rule from the reviews.
- For Si specifically, validate Route A with a matrix-relevant CRM before using it for publication-grade total Si values.

A10. Route A limitations to state explicitly
- Best HF-free route for Si, but not the easiest route for trace elements.
- B and Li cannot be reported from these digests.
- Trace-element detection limits are poorer because of Li/B salt load and required dilution.
- High-temperature fusion may be unsuitable for some volatile analytes unless separately validated.

Route B. Partial digestion for Al matrix and trace metals when Si does not need to be quantified
Use for: routine alloy screening, impurity profiling, many QC applications, and first-pass characterization of AlSi10Mg where the lab does not need total Si from ICP-MS.

B1. Scope and principle
- Dissolve the Al matrix with HCl/HNO3 or aqua regia.
- Accept that Si-rich phases remain insoluble.
- Remove residue before nebulization.
- Report results as acid-soluble fraction unless you have demonstrated that the residue is analytically irrelevant for your target elements.

B2. Reagents and sample mass
- Start with 0.10 g sample for AlSi10Mg method setup.
- Practical acid charge for startup: 5 to 7 mL aqua regia, or equivalent HCl:HNO3 = 3:1 mixture, in a PFA/PTFE vessel.
- For low-Si materials you may scale up after validation.

B3. Digestion conditions
Two workable formats are consistent with the reviews:
- Open-vessel hotplate: gentle heating around 80 to 120 °C until Al dissolves.
- Closed-vessel microwave: moderate program around 160 to 180 °C if you prefer reduced contamination and reproducibility.
Either way:
- Allow initial reaction to subside before heating; Al in HCl-containing media reacts briskly.
- Continue digestion until the metallic Al matrix is dissolved.
- Expect a white/grey Si-rich residue for AlSi10Mg.

B4. Clarification step
Because the solution must be particle-free before nebulization:
- Cool, dilute, then remove residue by filtration or centrifugation/decanting.
- Use acid-clean, low-background filters if filtering.
- Record this as a deliberate fractionation step, not a cleanup footnote.

B5. What is lost in Route B
- Silicon is not quantified.
- Trace elements concentrated in eutectic Si or silicide-rich particles may be partly lost with the residue.
- So Route B is suitable for “dissolved matrix + soluble trace elements,” not for defensible total composition of AlSi10Mg.

B6. When Route B is still the right answer
- When the analytical question is about routine alloy impurities in the acid-soluble fraction.
- When the lab needs simple startup, lower blanks, and better trace sensitivity.
- When Si can be measured by another technique, or does not matter.

B7. Dilution strategy for Route B
- Route B is much more ICP-friendly than fusion, but Al is still a huge matrix.
- Use at least two dilutions:
  - High dilution for majors (Al, Mg; and Si only if you are separately analyzing a residue digest, which this SOP does not recommend as default).
  - Lower dilution for trace metals.
- The reviews repeatedly point to keeping TDS around or below roughly 0.1 to 0.2% for stable ICP-MS operation.
- Because there is no added Li/B flux, Route B supports much better trace-metal detection limits than Route A.

B8. ICP-MS measurement block for Route B digests
Recommended startup method on the Agilent 8900:
- He KED: Fe-56, Cu-63, Mn-55, Zn-66, Ni-60, Co-59, Pb-208.
- O2 mass-shift: Cr-52→68.
- NH3 mass-shift / cluster: Ti-48→114; V-51→51 if V is needed.
- H2 on-mass for Si is not useful here unless you are explicitly measuring dissolved Si in another digest because most Si is in the removed residue.
- Al-27 and Mg-24 only on sufficiently high dilution.

B9. QA/QC for Route B
- Reagent blank and full method blank each batch.
- Matrix-matched external calibration as default.
- Use standard additions during development to see whether high-Al suppression remains after dilution.
- Analyze at least one matrix-relevant CRM routinely.
- If reporting trace metals in AlSi10Mg from Route B, validate whether residue removal biases the specific elements you care about by comparing a subset of samples against Route A or another total method.

Simple non-HF digestion for low-Si 1100 aluminum wire
Use for: 1100 Al wire and similar low-Si aluminum where Si is negligible.

W1. Recommended digestion
- Weigh about 50 to 100 mg cleaned wire into a PFA/PTFE vessel.
- Add about 25 to 50 mL of 5% v/v HCl.
- Heat at about 50 to 70 °C until fully dissolved.
- If needed after dissolution, add a small amount of HNO3 to oxidize residual Fe/Cu species, then dilute to the final matrix.
- Target a clear final solution without filtration.

W2. Why this is preferred
- The acid digestion review is clear that HCl dissolves Al readily, while HNO3 alone passivates Al.
- No fluoride is needed because Si is very low.
- This is the simplest, safest, lowest-blank path for 1100 Al.

W3. ICP-MS handling
- Still dilute enough to keep Al matrix manageable.
- Same trace-metal method blocks as Route B.
- Use matrix-matched standards if the remaining Al concentration is substantial.

Consolidated startup table

| Topic | Route A: LiBO2 fusion, Si required | Route B: HCl/HNO3 or aqua regia, Si not required | 1100 Al wire |
|---|---|---|---|
| Intended claim | Total digestion incl. Si | Partial digestion; acid-soluble fraction | Near-total for intended analytes |
| Sample types | AlSi10Mg, silicon powder | AlSi10Mg and similar when Si not needed | Low-Si Al |
| Sample mass | Start 0.10 g; validate up to 0.25 g | Start 0.10 g | 50–100 mg |
| Core chemistry | Borate fusion then acid dissolution | Dissolve Al matrix only; Si remains residue | HCl dissolution |
| Reagents | LiBO2 flux, dilute HCl or HNO3 for bead dissolution | HCl + HNO3, typically 3:1 | 5% HCl |
| Typical conditions | ~8:1 flux:sample; 950–1050 °C; ~2–2.5 h | 5–7 mL acid mix; ~80–120 °C hotplate or ~160–180 °C microwave | 50–70 °C |
| Particle-free step | Must dissolve bead fully | Remove Si-rich residue by filtration/centrifugation | None expected |
| Si recovery | Yes, best HF-free option | No | Not a target |
| Matrix burden | High Li/B; large extra dilution | Moderate acid matrix | Low to moderate |
| Best for trace sensitivity | No | Yes | Yes |
| Cannot measure well from same digest | Li, B | Si total | n/a |

Recommended isotopes, gas modes, and internal standards

| Analyte | Preferred isotope | Main issue | Recommended Agilent 8900 mode | Notes |
|---|---:|---|---|---|
| Al | 27 | CN/CNH background; extreme concentration | On-mass, only at very high dilution; cool-plasma/NH3 can help if needed | Usually treat as major element requiring separate high dilution |
| Si | 28 | N2+, CO+ | H2 on-mass 28→28 | Primary method for Route A; validate O2 shift only if needed |
| Mg | 24 | C2+ background; major element | On-mass with careful control; confirm with 25 or 26 if needed | Separate higher dilution recommended |
| Fe | 56 | ArO+ | He KED | 57 as confirmation if needed |
| Cu | 63 | NaAr+, other polyatomics | He KED | 65 as qualifier if needed |
| Mn | 55 | ArN+, related species | He KED | Monoisotopic, so cell mode matters |
| Zn | 66 | S-based overlaps lower than at 64 | He KED | 64 optional confirmatory only after validation |
| Ti | 48 | Ca, SO+ | NH3 cluster-shift 48→114 | Strong 8900 use case |
| Cr | 52 | ArC+ | O2 shift 52→68 | Default startup choice |
| Ni | 60 | CaO+, NaCl-related species | He KED | Review 58/60 during method development |
| V | 51 | ClO+ and related | NH3 on-mass 51→51 | Optional if V needed |

Recommended internal standards from the measurement review:
- Sc for low-mass region, especially Al/Mg/Si.
- Ge for the Ti/V/Cr/Mn/Fe region.
- Rh for Cu/Zn/Ni and nearby mid-mass analytes.
- In for mid-high mass analytes.
- Bi for Pb and other heavy analytes.

Use online addition if available. A practical startup concentration from the review is 50 to 100 µg/L final for each internal standard. Monitor recovery continuously. A practical acceptance window is 80 to 120% of the calibration-blank response.

Calibration and QA/QC recommendations

What the reports agree on:
- External calibration with internal-standard correction is the default workflow.
- Matrix matching matters in high-Al digests.
- Standard addition is best reserved for development, disputed analytes, or severe matrix effects.
- Use at least one matrix-relevant CRM during validation and routine use.
- Carry a full method blank through each digestion batch.
- Keep final dissolved solids low enough to prevent suppression, drift, and cone fouling.

Practical startup plan:
1. Calibration
- Use 5-point or broader external calibration.
- Match acid composition to the digest matrix.
- For Route A, match LiBO2-derived matrix approximately in standards.
- For Route B and 1100 Al, include Al in standards if residual Al concentration is still substantial.

2. Verification
- Initial calibration verification from an independent source: target within ±10%.
- Continuing calibration verification every 10 samples: target within ±10%.

3. Blanks
- Reagent blank each batch.
- Full method blank each digestion batch.
- For Route A, run a fusion blank, not just an acid blank.

4. Spikes and CRMs
- Matrix spike and matrix spike duplicate on at least one representative sample per batch.
- A practical acceptance target from the reviews is 75 to 125% recovery during startup, tightening later if your data support it.
- Analyze matrix-relevant CRMs routinely. For Al-Si work, prioritize Al-Si alloy CRMs rather than pure Al CRMs alone.

5. Detection/quantification limits
- Establish them empirically from replicate blanks in your own lab after the final method and dilution scheme are fixed.
- Do not borrow LOD/LOQ claims from literature because Route A and Route B will have very different blank structure and dilution penalties.

6. Contamination control
- Acid-wash PFA/PTFE/PP ware.
- Use trace-metal grade acids and high-purity flux.
- Keep solutions covered; use clean benches if available.
- For Route A especially, flux purity and crucible cleanliness will decide whether your blanks are decent or awful.

Prioritized HF-free safety checklist

1. Hot concentrated acids
- Handle HCl and HNO3 only in a fume hood.
- Use acid-resistant gloves, splash goggles, lab coat, and face shield for transfers.
- Add acid to water, not the reverse.
- Expect vigorous initial reaction and gas evolution when Al contacts HCl-containing mixtures.
- Keep oxidizing HNO3 away from organics and reducing materials.

2. High-temperature fusion
- Use heat-rated gloves, face shield, tongs, and appropriate furnace tools.
- Handle Pt crucibles carefully; avoid cross-contamination.
- Work behind splash/heat protection when moving hot melts.
- Let beads/crucibles cool under controlled conditions before dissolution.
- Add fused material to dissolution acid carefully; hot/partially cooled beads can react briskly.

3. Caustic reagents, if used for any exploratory work
- NaOH/KOH are strongly corrosive and exothermic on dilution.
- Do not use them as the default total-digestion route for AlSi10Mg.
- If explored at all, expect hydrogen evolution with Al and difficult precipitate/gel formation.

4. Pressurized digestion systems
- Follow vessel fill limits and manufacturer pressure/temperature limits.
- Allow vessels to cool fully before opening.
- Use acid-compatible vessels only.

5. Why HF and HBF4 are avoided
- HF is avoided because it creates severe exposure hazards and adds major operational burden.
- HBF4 is avoided as a default because it is not genuinely HF-free for your purposes: it hydrolyzes to HF on heating/storage, introduces boron, and still requires fluoride-aware materials and HF-equivalent precautions. So it is not a clean escape hatch.
- Only consider HBF4 as a last resort if Route A fusion proves unworkable and the lab is willing to accept fluoride chemistry, special controls, and alloy-specific validation.

Key open decisions the lab must resolve

1. Does silicon actually need to be quantified by this ICP-MS workflow?
- If yes, choose Route A now.
- If no, choose Route B for routine work and avoid a lot of pain.
This is the single highest-leverage decision.

2. If Si must be quantified, must it be by ICP-MS?
- If another technique is available and better suited to Si in Al alloys or silicon powder, the lab may choose to keep ICP-MS focused on trace metals and majors other than Si.
- If Si is moved to another method, Route B becomes far more attractive as the default ICP-MS workflow.

3. What claim will the lab make for AlSi10Mg results?
- “Total composition” requires Route A or another proven total method.
- “Acid-soluble composition” supports Route B.
Pick the reporting language before running samples.

4. Which analytes are truly required?
- If B or Li matter, LiBO2 fusion is a problem because it contaminates both.
- If ultra-trace volatile elements matter, fusion needs dedicated validation.

5. What throughput is needed?
- Route A is slower, dirtier, and more dilution-heavy.
- Route B is much simpler and better for routine sample throughput.

6. What matrix-matched CRMs can the lab obtain?
- A workable startup method needs at least one Si-bearing Al alloy CRM for validation if Route A or Route B will be used on AlSi10Mg.

7. Will the lab run one workflow or two in parallel?
- Best practice here is two workflows:
  - Route A for total Si and total composition questions.
  - Route B for routine trace-metal sensitivity and faster throughput.
This is the most defensible compromise.

Where the reports agree, and how conflicting advice was reconciled

Agreement across reports
- Al dissolves readily in HCl-containing media; HNO3 alone passivates Al.
- Si-rich phases are not quantitatively dissolved by HNO3/HCl alone.
- High matrix load is the central ICP-MS challenge; dilution and matrix matching are mandatory.
- Agilent 8900 MS/MS modes are useful for Si, Cr, Ti, V, and general interference cleanup.
- QA/QC must include matrix-aware calibration, blanks, internal standards, and CRMs.

Conflict reconciliation
- Some source material presented HBF4 as a safer alternative. I did not elevate it because your lab constraint is stricter: HBF4 is not genuinely HF-free in practice once heated/stored, and the HF-free review itself documents hydrolysis back to HF. Under your rule, that makes HBF4 a last resort, not a preferred route.
- Some acid-digestion material implicitly treated complete AlSi10Mg dissolution as a fluoride problem solved by HF. That is chemically true, but it is not operationally acceptable here. So the synthesis shifts the decision point from “how to use HF safely” to “when do you need total Si badly enough to justify fusion.”
- Some measurement advice assumed nitric-only matrices are preferable to avoid Cl polyatomics. For this application, HCl-containing dissolution is still reasonable because Al dissolution is much better, and the Agilent 8900 can handle many chloride-derived interferences with cell chemistry. Dissolution completeness of the Al matrix matters more than a theoretical preference for chloride-free reagents.

Bottom-line recommendation
- Default lab workflow: Route B for routine Al alloy impurity work and 1100 Al wire.
- Total-Si workflow: Route A by LiBO2 fusion, reserved for samples where Si must be reported.
- Do not use HF.
- Do not pretend HBF4 is HF-free.
- Do not claim total composition from acid-only digestion of AlSi10Mg after removing the Si-rich residue.

- Discretionary analytical decisions made during the synthesis:
  - Prioritized LiBO2 fusion over other alkaline fusion chemistries because the reviews most strongly supported it for retaining Si without silica separation after dissolution.
  - Recommended a two-workflow SOP instead of a single universal digestion because the evidence showed no single HF-free method optimizes both total Si recovery and low-matrix ICP-MS performance.
  - Chose H2 on-mass 28→28 as the default Si measurement mode, with O2 mass-shift reserved as a validated fallback.
  - Used practical startup sample masses near 0.10 g for development, even though some literature examples used larger masses, to reduce matrix load and make first-time method setup safer.
  - Recommended matrix-matched external calibration as the routine default, with standard additions reserved for development/problem cases.
  - Used practical QA/QC acceptance targets from the reviews, including CCV within ±10%, internal-standard recovery 80–120%, and startup spike-recovery targets of 75–125%.
  - Treated filtered Route B results as acid-soluble/partial digestion results unless total-composition equivalence is independently demonstrated.
  - Recommended running Route A and Route B in parallel for selected validation samples to quantify residue-related bias before routine deployment.