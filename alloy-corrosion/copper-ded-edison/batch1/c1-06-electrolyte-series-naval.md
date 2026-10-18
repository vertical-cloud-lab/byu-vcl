<!--
Edison Scientific LITERATURE task (batch 1)
- Task ID: 505fcd13-7172-4cbd-bb62-7f7c37a64ce6
- Submitted: 2026-10-18T01:20:05Z
- Fetched: 2026-10-18T01:50:06Z (status: success)
- Raw trajectory JSON: ../raw/c1-06-electrolyte-series-naval.json.gz
- Synthesis: ../README.md
-->

Question:

CONTEXT (do not summarize this back): Brigham Young University's Vertical
Cloud Lab (EXCLUDE publications by Sterling G. Baird) is planning automated
small-area corrosion tests on a Cartesian gantry robot with a pipetting head
and a potentiostat (the "CubXL"). The plan, written first for the lab's
aluminum alloys, is: polished metallographic cross-sections with a bare metal
back for electrical contact; a 3D-printed clamp holding 2-4 fluoroelastomer
(FKM) O-ring wells per piece (3-4 mm inner diameter, 0.07-0.13 cm2, about
150 uL of electrolyte each, open to air); a leak-free Ag/AgCl mini-reference
and a Pt-wire counter carried by the gantry head. The robot fills each well
from stock solutions, runs open-circuit potential (30 min), linear
polarization resistance (+/-10 mV), then a cyclic polarization reversed at a
current threshold; it photographs each spot before and after, and pipettes
the used electrolyte into a tube for offline ICP-OES/ICP-MS (element-resolved
dissolution). Candidate potentiostats are low-cost (IO Rodeo Rodeostat,
MYSTAT, PalmSens EmStat Pico). We now want to do the same for COPPER ALLOYS
FOR NAVAL USE (seawater piping, heat exchangers and condensers, propellers,
valves and fittings, and repair of cast nickel-aluminum bronze (NAB) and
wrought Cu-Ni), deposited by single-stream blown-powder laser directed energy
deposition (DED: one pre-alloyed powder feed, not in-situ blending), likely on
a 300-500 W infrared fiber-laser DED unit. Alloys: Cu-Ni 90-10 (C70600) and
70-30 (C71500) with Fe, Mn and Cr; NAB (C95800, C63000/C63020) and Mn-Al
bronze; reference coupons of wrought C71500 and cast C95800. Specimens:
deposits built on themselves; deposits on cast NAB and wrought Cu-Ni plates
(repair coupons with deposit, fusion zone, heat-affected zone and substrate);
single tracks and thin walls; and byproducts (splats, crucible skull) of
in-house ultrasonic atomization of the powders.

ALREADY ESTABLISHED (do not re-derive; build on it): Cu-Ni corrosion product
films take weeks to months to mature, so one-hour tests rank fresh surfaces;
Tafel fits on an oxygen-diffusion-limited cathodic branch and an assumed
Stern-Geary B are unreliable for these alloys; natural seawater can reverse
rankings obtained in 3.5% NaCl or ASTM D1141; DeCost et al. 2022 (JOM,
autonomous scanning droplet cell) optimized Al-Ni-Ti coatings only in
simulation on an existing dataset; MAP-E (Persaud et al. 2026, npj Mater.
Degrad.) automated O-ring flat-cell pitting tests on 304 stainless steel;
blown-powder laser DED of NAB and of Cu-30Ni has been published (Li et al.
2021; Bhattacharya et al. 2011).

QUESTION: For an automated screen that mixes each test solution from stocks,
which electrolyte series would give each copper alloy a slope rather than a
single point (as a log[chloride] series does for aluminum pitting) while
staying relevant to naval seawater service? Candidates: chloride
concentration; sulfide additions (polluted harbor water, e.g. 0.01-10 mg/L),
including the order of sulfide and clean-seawater exposure; dissolved
oxygen; pH; ammonia; ferrous ion dosing (ferrous sulfate pre-filming of naval
condensers); temperature. For each, report how Cu-Ni (90-10, 70-30) and NAB
respond (Ecorr, icorr, film composition, localized attack) with numbers,
which variables have reversed the ranking of alloys, and how to make and keep
these solutions stable in small open wells (sulfide oxidation and loss as
H2S, precipitation in ASTM D1141, oxygen equilibration). Say which 2-3
variables give the most naval-relevant information per test.

OUTPUT FORMAT: For each relevant item give the full citation with DOI; the
material and how it was made (wrought, cast, weld, laser clad or laser
surface melted, blown-powder DED, WAAM, LPBF); the composition in wt%; the
cell (bulk flat cell, droplet or capillary cell, O-ring area) and electrolyte
volume; the electrolyte and duration; and the key numbers (Ecorr against a
stated reference, Rp, icorr, breakdown or protection potentials, current
ranges, dissolution rates by element, depth of attack). Tag each item: [CITE]
worth citing; [NUMBERS] gives a quantitative benchmark; [NAVY] Navy/DoD-funded
or a Navy application; [CUBXL] changes how the small-cell robot test should be
built or run (say how); [NOVELTY-RISK] overlaps the planned work (say how);
[GAP] shows something not yet done. If the literature does not answer part
of the question, say so plainly instead of padding with loosely related work.
End with a ranked "Top 5 changes to the small-cell plan for copper alloys".

---

Question: CONTEXT (do not summarize this back): Brigham Young University's Vertical
Cloud Lab (EXCLUDE publications by Sterling G. Baird) is planning automated
small-area corrosion tests on a Cartesian gantry robot with a pipetting head
and a potentiostat (the "CubXL"). The plan, written first for the lab's
aluminum alloys, is: polished metallographic cross-sections with a bare metal
back for electrical contact; a 3D-printed clamp holding 2-4 fluoroelastomer
(FKM) O-ring wells per piece (3-4 mm inner diameter, 0.07-0.13 cm2, about
150 uL of electrolyte each, open to air); a leak-free Ag/AgCl mini-reference
and a Pt-wire counter carried by the gantry head. The robot fills each well
from stock solutions, runs open-circuit potential (30 min), linear
polarization resistance (+/-10 mV), then a cyclic polarization reversed at a
current threshold; it photographs each spot before and after, and pipettes
the used electrolyte into a tube for offline ICP-OES/ICP-MS (element-resolved
dissolution). Candidate potentiostats are low-cost (IO Rodeo Rodeostat,
MYSTAT, PalmSens EmStat Pico). We now want to do the same for COPPER ALLOYS
FOR NAVAL USE (seawater piping, heat exchangers and condensers, propellers,
valves and fittings, and repair of cast nickel-aluminum bronze (NAB) and
wrought Cu-Ni), deposited by single-stream blown-powder laser directed energy
deposition (DED: one pre-alloyed powder feed, not in-situ blending), likely on
a 300-500 W infrared fiber-laser DED unit. Alloys: Cu-Ni 90-10 (C70600) and
70-30 (C71500) with Fe, Mn and Cr; NAB (C95800, C63000/C63020) and Mn-Al
bronze; reference coupons of wrought C71500 and cast C95800. Specimens:
deposits built on themselves; deposits on cast NAB and wrought Cu-Ni plates
(repair coupons with deposit, fusion zone, heat-affected zone and substrate);
single tracks and thin walls; and byproducts (splats, crucible skull) of
in-house ultrasonic atomization of the powders.

ALREADY ESTABLISHED (do not re-derive; build on it): Cu-Ni corrosion product
films take weeks to months to mature, so one-hour tests rank fresh surfaces;
Tafel fits on an oxygen-diffusion-limited cathodic branch and an assumed
Stern-Geary B are unreliable for these alloys; natural seawater can reverse
rankings obtained in 3.5% NaCl or ASTM D1141; DeCost et al. 2022 (JOM,
autonomous scanning droplet cell) optimized Al-Ni-Ti coatings only in
simulation on an existing dataset; MAP-E (Persaud et al. 2026, npj Mater.
Degrad.) automated O-ring flat-cell pitting tests on 304 stainless steel;
blown-powder laser DED of NAB and of Cu-30Ni has been published (Li et al.
2021; Bhattacharya et al. 2011).

QUESTION: For an automated screen that mixes each test solution from stocks,
which electrolyte series would give each copper alloy a slope rather than a
single point (as a log[chloride] series does for aluminum pitting) while
staying relevant to naval seawater service? Candidates: chloride
concentration; sulfide additions (polluted harbor water, e.g. 0.01-10 mg/L),
including the order of sulfide and clean-seawater exposure; dissolved
oxygen; pH; ammonia; ferrous ion dosing (ferrous sulfate pre-filming of naval
condensers); temperature. For each, report how Cu-Ni (90-10, 70-30) and NAB
respond (Ecorr, icorr, film composition, localized attack) with numbers,
which variables have reversed the ranking of alloys, and how to make and keep
these solutions stable in small open wells (sulfide oxidation and loss as
H2S, precipitation in ASTM D1141, oxygen equilibration). Say which 2-3
variables give the most naval-relevant information per test.

OUTPUT FORMAT: For each relevant item give the full citation with DOI; the
material and how it was made (wrought, cast, weld, laser clad or laser
surface melted, blown-powder DED, WAAM, LPBF); the composition in wt%; the
cell (bulk flat cell, droplet or capillary cell, O-ring area) and electrolyte
volume; the electrolyte and duration; and the key numbers (Ecorr against a
stated reference, Rp, icorr, breakdown or protection potentials, current
ranges, dissolution rates by element, depth of attack). Tag each item: [CITE]
worth citing; [NUMBERS] gives a quantitative benchmark; [NAVY] Navy/DoD-funded
or a Navy application; [CUBXL] changes how the small-cell robot test should be
built or run (say how); [NOVELTY-RISK] overlaps the planned work (say how);
[GAP] shows something not yet done. If the literature does not answer part
of the question, say so plainly instead of padding with loosely related work.
End with a ranked "Top 5 changes to the small-cell plan for copper alloys".


# Electrolyte series for a naval-copper-alloy screen

**Recommendation.** Use a fixed, characterized seawater background and measure a **sulfide dose–response, with exposure history as a second axis**. Among solution variables, dissolved oxygen is the most important interaction to test, but an oxygen-poor series cannot be held reliably in the proposed open wells. For condenser-repair work, make **ferrous-sulfate prefilming** the third axis; it is a conditioning treatment, not another salt to add immediately before polarization. These choices measure the response of *each* material rather than treating a single chloride polarization curve as a service-life ranking. Published sulfide experiments show large responses, but do **not** establish a universal sulfide slope—or a ranking reversal—among C70600, C71500, and C95800. (yuan2007surfacecharacterizationand pages 3-5, yuan2007surfacecharacterizationand pages 8-11, nady2017corrosionbehaviorand pages 1-2, lewis1981evaluationofcoppernickel pages 43-48)

The matrix distinguishes **proposed CubXL levels** from literature measurements:

| Priority / variable | Proposed CubXL series for 150 µL wells | Cu–Ni 90–10 response | Cu–Ni 70–30 response | NAB response | Critical control / interpretation |
|---|---|---|---|---|---|
| **1. Sulfide × exposure order** | **Proposed, not a single literature protocol:** target 0, 0.01, 0.1, 1, and 10 mg/L total dissolved sulfide; verify the **actual** concentration immediately after mixing and after testing. Run fresh→sulfide, clean-seawater-prefilmed→sulfide, and sulfide→clean-seawater sequences. | Accelerated attack has been reported from 0.01 mg/L; expect a negative shift in corrosion potential, a porous Cu₂S-rich film, suppression of protective Cu₂O, and greater localized-attack risk. The exact response over the proposed five-level series is unmeasured. (yuan2007surfacecharacterizationand pages 1-3) | At 10 mg/L, corrosion-current density rose from 8.44 to 87.39 µA/cm² initially and remained 17.29–19.15 µA/cm² after sulfide depletion, versus 1.01 µA/cm² after 10 days of clean exposure; products included Cu₂S, NiS, CuCl, and oxides. (yuan2007surfacecharacterizationand pages 3-5, yuan2007surfacecharacterizationand pages 8-11) | Cast Cu–11.28Al–9.95Ni–2.26Fe in 2 mg/L sulfide gave a corrosion potential of −609 mV SCE and corrosion-current density of 30 µA/cm², versus −464 mV SCE and 7.4 µA/cm² without sulfide; Cu₂S undermined Cu₂O protection. (nady2017corrosionbehaviorand pages 3-4, nady2017corrosionbehaviorand pages 4-5, nady2017corrosionbehaviorand pages 1-2) | Add Na₂S last from fresh, oxygen-excluded stock; use capped mixing vials and low-headspace wells. Sulfide in aerated seawater can have a roughly 20-minute half-life; 10 mg/L fell to 1.2±0.2 mg/L in 1 day, about 0.1 mg/L in 3 days, and below detection by 4 days. Measure by methylene blue or a sulfide microsensor. Do not combine sulfide and Fe²⁺ stocks. (yuan2007surfacecharacterizationand pages 3-5) |
| **2. Dissolved oxygen** | Use an air-equilibrated baseline. Conduct oxygen-poor testing only in a **sealed, gas-controlled cell**, not an open well; use controlled N₂/air gas mixtures rather than nominally deaerated pipetted liquid. | Oxygen controls cathodic reduction and interacts synergistically with sulfide; an open 150 µL well will drift rapidly toward air equilibrium. Quantitative alloy-specific dissolved-oxygen slopes were not found. (yuan2007surfacecharacterizationand pages 1-3) | Coexisting oxygen and sulfide accelerates cathodic and anodic processes; clean-film protection and sulfide damage cannot be interpreted without measured dissolved oxygen. (yuan2007surfacecharacterizationand pages 8-11, yuan2007surfacecharacterizationand pages 5-8) | Oxygen reduction is the principal cathodic process in aerated chloride media; no reliable quantitative dissolved-oxygen series for C95800 or C63020 was located. | Record dissolved oxygen immediately before filling and after electrochemistry. Cover wells to suppress exchange and evaporation. For oxygen-poor work, use a gasketed chamber, gas-equilibrated electrolyte, and optical dissolved-oxygen sensing. An open-well low-oxygen series is not stable. |
| **3. Ferrous-sulfate prefilming** | Use a separate conditioning experiment: clean seawater plus FeSO₄ dosing over repeated exposures, followed by rinse and transfer to a clean or sulfide challenge. Do **not** treat this as a one-time Fe²⁺ spike in the test well. | Iron-bearing 90–10 films can become Fe- and Ni-enriched; 1.3–2.0 wt% alloy Fe historically made 90–10 performance approach that of 70–30. This is evidence about alloy Fe, not proof of an optimal FeSO₄ dose. (lewis1981evaluationofcoppernickel pages 17-19, lewis1981evaluationofcoppernickel pages 43-48) | Protective Cu₂O films have substantially higher electronic and ionic resistance than 90–10 films; Fe and Ni incorporation supports film resistivity. (lewis1981evaluationofcoppernickel pages 43-48) | No validated FeSO₄-prefilming response for C95800 or C63020 was found; Fe may precipitate rather than beneficially enter the Al-rich film. | Prepare FeSO₄ fresh under low oxygen and add it before alkalinity salts or in a separate conditioning bath. At seawater pH, Fe²⁺ oxidizes and precipitates rapidly; verify dissolved and deposited Fe by ICP and XPS. Include seawater-only conditioning and unconditioned controls. |
| **4. Chloride concentration** | Use a secondary series centered on matched brackish-to-seawater chloride rather than logarithmic decades; keep ionic strength, sulfate, and alkalinity controlled. | Higher Ni generally improves Cu₂O-film resistance; ASTM D1141 testing gave a corrosion-current density of about 1.2 µA/cm² for Cu–10Ni. Chloride forms soluble CuCl₂⁻ and Cu₂O/Cu₂(OH)₃Cl products. (zarebidaki2025evaluationofcorrosion pages 11-14, zarebidaki2025evaluationofcorrosion pages 1-5, zarebidaki2025evaluationofcorrosion pages 7-11) | ASTM D1141 testing gave about 1.1 µA/cm² for the study’s Cu–20Ni material, marginally below Cu–10Ni; this was not certified C71500 chemistry. (zarebidaki2025evaluationofcorrosion pages 5-7, zarebidaki2025evaluationofcorrosion pages 1-5) | As-built WAAM NAB showed a broad passive or pseudopassive interval and lower passive current than cast or heat-treated NAB in 3.5 wt% NaCl; κ phases promote microgalvanic attack. (shahriari2023corrosionperformanceof pages 2-4, shahriari2023corrosionperformanceof pages 2-2) | Mix complete marine salts, not NaCl alone, when naval relevance is the objective. Avoid CaCO₃ or Mg(OH)₂ precipitation by preparing and filtering the base seawater before adding modifiers; inspect blanks for turbidity. No verified cross-alloy ranking reversal caused solely by chloride concentration was found. |
| **5. pH** | **Proposed:** pH 7.6, 8.0, and 8.4, with small acid or base additions to a common marine base; verify pH after all modifiers are added. | pH changes CuCl₂⁻ hydrolysis, Cu₂O/CuO formation, and H₂S/HS⁻ partitioning, but no quantitative C70600 slope over this proposed range was found. | Yuan’s clean and sulfide work used pH 8.2±0.1; the proposed pH series remains a gap for C71500 and DED material. (yuan2007surfacecharacterizationand pages 3-5) | Al₂O₃, Al-hydroxide, and Cu-oxide stability should change with pH, but no quantitative C95800 or C63020 slope over pH 7.6–8.4 was located. | Use a low-capacity, marine-compatible buffer only after demonstrating negligible complexation. Measure pH in the mixed reservoir and in a sacrificial 150 µL well; CO₂ exchange can shift open-well pH. Report sulfide results with both total dissolved sulfide and pH. |
| **6. Ammonia** | Use a zero-ammonia baseline. Add a conditional low-mg/L NH₃/NH₄⁺ leak scenario only when condenser leakage is a target use case. **Numeric levels require a service specification and analytical verification.** | Ammonia can complex dissolved Cu and defeat Cu-oxide protection; Cu–Ni was judged unsuitable where ammonia/seawater cross-leakage was credible. No reliable short-test numeric slope was found. (lewis1981evaluationofcoppernickel pages 60-64) | The same concern applies; higher Ni does not justify assuming immunity to ammoniacal copper complexation or stress-corrosion effects. | No directly applicable quantitative ammonia series for naval NAB was found. | Control total ammonia, pH, and headspace because free NH₃ is volatile and pH-dependent. Use sealed reservoirs, minimize delay, and analyze total ammonia after testing. Avoid claiming alloy rankings from an unverified nominal dose. |
| **7. Temperature** | **Proposed:** externally controlled 15, 25, and 35 °C; equilibrate the specimen, reference electrode, and electrolyte before filling. | Temperature affects oxygen solubility, reaction kinetics, and film formation, but no supported numeric response over this proposed range was found. | High-sulfide C71500 testing at 35±2 °C gave an initial rate of 0.15 mm/year and about 0.09 mm/year after 168 hours, but this was an extreme 0.5 wt% Na₂S condition and not a clean-seawater temperature slope. (gao2022corrosionbehaviorof pages 2-4, gao2022corrosionbehaviorof pages 1-2) | No quantitative temperature slope suitable for cast-versus-DED NAB screening was located. | Heat the specimen stage and solution reservoir; 150 µL droplets equilibrate and evaporate quickly. Cover wells, monitor actual liquid temperature, correct Ag/AgCl potential for temperature, and replenish only in dedicated evaporation controls. No verified relative ranking reversal among 90–10, 70–30, and NAB with temperature was found. |


*Table: Decision matrix for selecting and controlling electrolyte variables in 150 µL CubXL tests of Cu–Ni and NAB. Proposed levels are distinguished from published measurements, with stability constraints and evidence gaps identified.*

## Quantitative anchors and their limits

**[CITE] [NUMBERS] [NAVY] [CUBXL]** Yuan, S. J., and Pehkonen, S. O., “Surface characterization and corrosion behavior of 70/30 Cu-Ni alloy in pristine and sulfide-containing simulated seawater,” *Corrosion Science* **49** (2007), 1276–1304. **DOI: 10.1016/j.corsci.2006.07.003.** The commercial, as-received CDA 715 plate contained **67.84 Cu, 30.6 Ni, 0.63 Fe, 0.6 Mn, and 0.02 Zn wt%**, plus trace elements; it was polished, not additively manufactured. A **500-mL bulk glass cell**, PVDF-mounted **0.785-cm²** working area, Pt counter, and **Ag/AgCl** reference were used. Nine-salt simulated seawater was air-equilibrated, stagnant, **pH 8.2 ± 0.1**, **25 ± 0.1 °C**; the comparison was clean water versus an **initial 10 mg/L sulfide** dose, sampled at 0, 1, 3, 6, and 10 days. In clean water, reported polarization-derived *i*corr fell **8.44 → 1.01 µA cm⁻²** over 10 days. With sulfide, it was **87.39 µA cm⁻² initially** and **18.44 µA cm⁻² at day 10**, even though sulfide became undetectable by day 4. The clean film developed an inner Cu₂O/outer CuO structure; exposure to sulfide produced porous Cu₂S, NiS, CuCl, and oxide products. **CubXL implication:** the result measures both chemistry *and exposure history*; one clean-water rinse does not reset a sulfided spot. Numerical *R*p, metal-by-metal dissolution, and attack depth were not established in this comparison. The bulk-cell currents are benchmarks, **not** predictions for a 150-µL well. (yuan2007surfacecharacterizationand pages 3-5, yuan2007surfacecharacterizationand pages 5-8, yuan2007surfacecharacterizationand pages 8-11, yuan2007surfacecharacterizationand pages 26-29)

**[CITE] [NUMBERS] [NAVY] [CUBXL]** Nady, H., El-Rabiei, M. M., and Samy, M., “Corrosion behavior and electrochemical properties of carbon steel, commercial pure titanium, copper and copper–aluminum–nickel alloy in 3.5% sodium chloride containing sulfide ions,” *Egyptian Journal of Petroleum* **26** (2017), 79–94. **DOI: 10.1016/j.ejpe.2016.02.008.** Their **cast** Cu–Al–Ni bronze contained **76.00 Cu, 11.28 Al, 9.95 Ni, 2.26 Fe, 0.14 Sn, and 0.02 Mn wt%**, with minor constituents. It is **not a certified C95800 or C63020**. Polished, epoxy-mounted rods exposed **0.2 cm²** in a **bulk all-glass three-electrode cell** with Pt counter and **SCE**; electrolyte volume was not reported in the retrieved methods. Following approximately **240 min** in stagnant, naturally aerated **3.5% NaCl** at **25 °C**, the bronze’s tabulated *E*corr/*i*corr were **−464 mV versus SCE / 7.4 µA cm⁻²** without sulfide, versus **−609 mV versus SCE / 30 µA cm⁻²** with **2 mg/L sulfide**. The sulfide-containing film was discussed in terms of Cu₂S disrupting Cu₂O protection; Al and Ni contribute to the otherwise more resistant oxide. There is no quantitative bronze depth-of-attack or element-resolved dissolution result. **CubXL implication:** measure an actual NAB grade rather than transferring this fourfold current change to every NAB microstructure. The source’s PDF text drops minus signs from its table; the reported signs follow the adjoining polarization plots and discussion. (nady2017corrosionbehaviorand pages 1-2, nady2017corrosionbehaviorand pages 2-3, nady2017corrosionbehaviorand pages 3-4, nady2017corrosionbehaviorand pages 4-5)

**[CITE] [NUMBERS] [NAVY] [CUBXL]** Gao, X., and Liu, M., “Corrosion Behavior of High-Strength C71500 Copper-Nickel Alloy in Simulated Seawater with High Concentration of Sulfide,” *Materials* **15** (2022), 8513. **DOI: 10.3390/ma15238513.** This **forged, rolled, heat-treated pipe**, not DED, contained **30.54 Ni, 0.93 Mn, and 0.80 Fe wt%; Cu balance**. Electrochemistry used an approximately **10 × 10-mm pipe-wall surface**, epoxy masking, Pt mesh, and **SCE**; solution volume was not established. Exposure was **3.5 wt% NaCl + 0.5 wt% Na₂S**, **pH 8.20**, **35 ± 2 °C**, for **0.5–672 h**. Gravimetric corrosion fell from approximately **0.15 mm year⁻¹ initially** to **0.09 mm year⁻¹ by 168 h**. Anodic features occurred near **−525 and −404 mV versus SCE**; fitted charge-transfer resistance reached **6619 Ω cm² at 672 h**. The products included Cu₂S, CuS, copper hydroxychloride, and Mn/Fe compounds, with Fe and Ni depletion reported in the film analysis; attack was described as predominantly uniform. The paper’s extracted polarization table has inconsistent column alignment, so it is **not** a secure source for a time-by-time *E*corr/*i*corr list. **CubXL implication:** this is an extreme stagnant-system experiment, **not a 0.01–10 mg/L harbor-water dose or a calibration point for that slope**; the Na₂S mass fraction should not be relabeled a measured dissolved-sulfide concentration. (gao2022corrosionbehaviorof pages 2-4, gao2022corrosionbehaviorof pages 4-5, gao2022corrosionbehaviorof pages 5-6, gao2022corrosionbehaviorof pages 8-10, gao2022corrosionbehaviorof pages 1-2)

**[CITE] [NUMBERS] [NAVY] [CUBXL] [NOVELTY-RISK]** Shahriari, A., Chalasani, D., Amirkhiz, B. S., and Mohammadi, M., “Corrosion performance of wire arc additively manufactured NAB alloy,” *npj Materials Degradation* **7** (2023), 1–15. **DOI: 10.1038/s41529-023-00405-x.** The authors compared **as-cast** NAB with **gas-metal-arc WAAM** material made using **ERCuNiAl filler wire on a 316L substrate**, both as-built and heat-treated; the exact wire and cast wt% values were **not recoverable from the accessible excerpts**. This is **WAAM, not single-powder laser DED**. A **bulk three-electrode cell** with graphite counter and saturated **Ag/AgCl** reference exposed **0.181–1.171 cm²** in air-exposed **3.5 wt% NaCl**, approximately **23 ± 2 °C**; volume was not reported. The as-built and cast specimens had **96-h** immersions; heat-treated specimens had **24-h** immersions. OCP was held **1800 s** before EIS and cyclic polarization. As-built WAAM’s reported potential was approximately **−0.293 V versus Ag/AgCl**, compared with approximately **−0.222 V** for the other conditions collectively; nevertheless, the as-built material showed the lower passive current and better chloride-corrosion response. Heat-treatment benchmarks include **4.4, 6.6, and 8 µA cm⁻²** fitted *i*corr for **350 °C/2 h, 550 °C/4 h, and 675 °C/6 h**, respectively; these are **not** measured values for cast versus as-built. Cathodic κ phases relative to the α matrix provide a plausible site for phase-selective attack. Exact cast/as-built *R*p, dissolution, and attack depths were not supported by the retrieved excerpts. **Novelty boundary:** comparing AM and cast NAB in chloride solution has already been done; measuring **powder-laser-DED repair-zone maps and chemistry-by-history responses** is the distinguishable experiment. (shahriari2023corrosionperformanceof pages 1-2, shahriari2023corrosionperformanceof pages 14-14, shahriari2023corrosionperformanceof pages 2-4, shahriari2023corrosionperformanceof pages 2-2, shahriari2023corrosionperformanceof pages 12-14)

**[CITE] [NUMBERS] [CUBXL]** Jin, T., Zhang, W., Li, N., Liu, X., Han, L., and Dai, W., “Surface Characterization and Corrosion Behavior of 90/10 Copper-Nickel Alloy in Marine Environment,” *Materials* **12** (2019), 1869. **DOI: 10.3390/ma12111869.** A polished **sheet**, with **9.76 Ni, 1.20 Fe, 0.74 Mn wt%; Cu balance**, was immersed for up to **56 days at 30 °C**; subsequent conventional-cell electrochemistry used **SCE**, with no recoverable exposed area or volume. **Important qualification:** the immersion fluid was **sterilized natural Xiamen Bay seawater mixed with 0.5 mol/L H₂O₂ and supplied oxygen**, not ordinary natural seawater. The authors reported *i*corr falling **3.812 → 1.056 µA cm⁻²**, with evolving Cu₂O/CuO, hydroxide, and chloride-containing products and eventual local film breakdown. Do not use these currents as an untreated natural-seawater benchmark or as a temperature response. (jin2019surfacecharacterizationand pages 3-5, jin2019surfacecharacterizationand pages 11-13)

**[CITE] [NUMBERS] [NAVY] [CUBXL]** Lewis, R. O., and LaQue, F., *Evaluation of copper-nickel alloys for OTEC applications* (1981), technical report. **DOI: 10.2172/6255887.** This is a **compiled service/test assessment**, not one controlled small-cell experiment; nominal marine **C70600 contains about 90 Cu/10 Ni with approximately 1.0–1.8 Fe wt%**, and **C71500 about 70 Cu/30 Ni with approximately 0.4–0.7 Fe wt%**. In its low-velocity seawater comparison, **quiet-water corrosion-rate ranges** were **0.2–0.6 mil year⁻¹ for 90/10** and **0.3–0.5 for 70/30**; at **2 ft s⁻¹**, **0.5–1.1** and **0.5–0.7 mil year⁻¹**, respectively. Six-month flowing-seawater film data show how markedly alloy Fe can alter film Fe/Ni composition. Separately compiled **60-day, 3.4% NaCl** rates were **38.4, 33.0, and 12.2 µm year⁻¹** for Cu–10Ni with **0, 0.3, and 1.5 wt% Fe**. Neither observation specifies an optimal **ferrous-sulfate dosing regimen**: alloying Fe and administering dissolved Fe²⁺ are different experiments. These cited tests do not supply common cell volume/area, *E*corr/reference, *R*p, or ICP rates. OTEC is a marine heat-exchanger application; the report is **not identified here as Navy/DoD-funded**. (lewis1981evaluationofcoppernickel pages 14-17, lewis1981evaluationofcoppernickel pages 43-48, lewis1981evaluationofcoppernickel pages 60-64)

**[CITE] [NUMBERS] [GAP]** Zarebidaki, A., and Dadras, D., “Evaluation of corrosion resistance of Cu, Cu-10 wt% Ni, Cu-20 wt% Ni, and electroless Ni-B and Ni-P coatings in Simulated Seawater,” **2025 preprint**, **DOI: 10.21203/rs.3.rs-6881634/v1**. Commercial Cu–Ni coupons were tested in a **500-mL ASTM D1141 bulk cell** at **1 cm²**, with Pt counter and **Ag/AgCl** reference. Reported fitted currents are **1.2 µA cm⁻² for Cu–10Ni** and **1.1 µA cm⁻² for Cu–20Ni**, compared with **2.5 µA cm⁻² for Cu**. Its stated “Cu–20Ni (UNS C71500)” designation is compositionally inconsistent with **70/30 C71500**: it is **not** evidence for a measured C70600-versus-C71500 seawater ranking. OCP duration, *E*corr, *R*p, and attack depth were not established here. (zarebidaki2025evaluationofcorrosion pages 5-7, zarebidaki2025evaluationofcorrosion pages 1-5, zarebidaki2025evaluationofcorrosion pages 7-11)

## Which variables can supply a defensible slope?

**Sulfide: yes, provided the x-axis is measured exposure, not the dispensing recipe.** A proposed **0, 0.01, 0.1, 1, 10 mg/L total dissolved sulfide** series brackets the low-concentration concern for Cu–Ni and Nady’s 2-mg/L bronze comparison. Run the same levels after *fresh polish*, *clean-seawater prefilming*, and *sulfide exposure followed by clean seawater*; report both dose and the resulting film/history. The cited Cu–Ni values at **0.01 mg/L for 90/10 and 0.1 mg/L for 70/30 are thresholds mentioned from earlier work in Yuan’s introduction**, not matched experiments proving 70/30 universally outperforms 90/10. Yuan’s 10-mg/L starting solution fell to **1.2 ± 0.2 mg/L after one day**, approximately **0.1 mg/L after three**, and below detection after four. Thus a 30-min OCP plus polarization sequence does **not** guarantee a constant sulfide concentration. Do not treat all points as a simple monotonic line without measuring the changing chemistry. (yuan2007surfacecharacterizationand pages 1-3, yuan2007surfacecharacterizationand pages 3-5, yuan2007surfacecharacterizationand pages 5-8, yuan2007surfacecharacterizationand pages 8-11)

**Dissolved oxygen: mechanistically essential, but requires hardware different from the open-well baseline.** Oxygen reduction is the important cathodic process; oxygen and sulfide together have produced strongly accelerated Cu–Ni attack. Open 150-µL wells equilibrate toward room air while filling, waiting, and scanning. Measure oxygen in matched sacrificial wells and use a sealed, gas-controlled fixture if oxygen is an intentional series. Available evidence does **not** give a transferable numeric oxygen–*i*corr slope for each requested alloy. (yuan2007surfacecharacterizationand pages 8-11, yuan2007surfacecharacterizationand pages 5-8, nady2017corrosionbehaviorand pages 2-3)

**Ferrous ion: high-value for condensers, but a film-history experiment.** Dose freshly prepared FeSO₄ into a **separate conditioning bath**, compare clean-conditioned and Fe-conditioned coupons, then rinse consistently and challenge both in clean or sulfided seawater. Directly adding Fe²⁺ to a seawater/sulfide screening well risks oxidation, hydroxide/oxide precipitation, and sulfide scavenging; it does not isolate beneficial prefilming. Measure soluble and deposited Fe. The accessible quantified iron results concern **Fe in the Cu–Ni alloy**, not a demonstrated FeSO₄ dose–response for Cu–Ni or NAB. (lewis1981evaluationofcoppernickel pages 17-19, lewis1981evaluationofcoppernickel pages 43-48, lewis1981evaluationofcoppernickel pages 60-64)

**Chloride, pH, ammonia, temperature: secondary or service-specific series.** Chloride should first be held at a reproducible seawater-relevant background; varying NaCl alone also changes ionic strength and omits marine sulfate, alkalinity, Ca, and Mg. A narrower brackish-to-seawater chloride comparison is preferable to aluminum-style logarithmic decades. Control pH as a *co-variable* because it changes oxides and H₂S/HS⁻ partitioning; the quantitative Yuan comparison used **pH 8.2 ± 0.1**, not a pH sweep. Add ammonia only for a defined condenser leak scenario: the marine heat-exchanger assessment flags cross-leakage, but no suitable C70600/C71500/C95800 ammonia–current slope was retrieved. An externally temperature-controlled series could represent service differences, but Gao’s **35 ± 2 °C** measurement in **0.5 wt% Na₂S** is not a temperature comparison. No quantitative three-alloy response or verified ranking reversal for these proposed ranges was established from the retrieved primary studies. (yuan2007surfacecharacterizationand pages 3-5, gao2022corrosionbehaviorof pages 2-4, lewis1981evaluationofcoppernickel pages 14-17, lewis1981evaluationofcoppernickel pages 60-64, zarebidaki2025evaluationofcorrosion pages 5-7)

**Ranking reversals: state the comparator precisely.** The available WAAM NAB study shows one important **metric reversal**: a more negative potential for as-built WAAM than for the other NAB conditions did **not** mean inferior chloride performance; its passive response was better. Lewis and LaQue’s broad quiet-versus-flowing rate ranges also caution against a fixed 90/10-versus-70/30 ordering, but their ranges overlap and **do not prove a reversal for a matched pair**. The retrieved literature does **not** establish a measured C70600/C71500/C95800 rank reversal attributable specifically to sulfide dose or order, oxygen, chloride, pH, ammonia, ferrous dosing, or temperature. Any such interaction in the proposed screen is a hypothesis, not a known result. (shahriari2023corrosionperformanceof pages 2-4, shahriari2023corrosionperformanceof pages 2-2, lewis1981evaluationofcoppernickel pages 43-48)

## Mixing, stability, and interpretation in 150-µL wells

Prepare a characterized seawater **base first**, then make condition-specific aliquots. Check that Ca/Mg-containing artificial seawater remains clear after alkalinity or pH adjustment; reject or separately characterize turbid mixtures rather than calling a precipitated dose “dissolved.” Keep sulfide, Fe²⁺, and ammonia stocks separate. Make sulfide aliquots immediately before use, add sulfide last, minimize headspace and waiting time, randomize plate position/order, and assay dissolved sulfide at filling and at termination. At seawater pH, H₂S/HS⁻ partitioning and oxygen-dependent sulfide consumption mean an open-well nominal spike may differ from actual exposure; acidifying sulfide-containing liquid can also release H₂S and requires appropriate containment. Use optically measured oxygen and recorded pH/temperature as test metadata rather than assuming air saturation or constant composition. The published approximately **20-min sulfide half-life at 3.8 mg/L in air-saturated seawater**, cited in Yuan’s methods from earlier work, makes blank-well stability tests indispensable. (yuan2007surfacecharacterizationand pages 3-5, nady2017corrosionbehaviorand pages 1-2)

For each condition, retain **unpolarized companions** for film analysis and ICP mass balance: a cyclic scan itself changes the oxide/sulfide surface and may dissolve or deposit material. Acidify recovered electrolyte only **after** electrochemistry, in a separate analytical tube; distinguish filtered dissolved metal from total recoverable metal if precipitates form, and run stock, O-ring, tip, and electrode blanks. Report Cu, Ni, Fe, Mn, Al, and Cr separately, normalized to measured exposed area, elapsed time, and initial alloy composition. These procedures are proposed **CubXL controls**, not published element-resolved rates for the specified DED alloys; such rates were not located in the evidence above. The **0.07–0.13-cm²** proposed wells are also substantially smaller than Yuan’s **0.785-cm²** exposed area and can change local oxygen and product accumulation. (yuan2007surfacecharacterizationand pages 3-5, gao2022corrosionbehaviorof pages 2-4, nady2017corrosionbehaviorand pages 1-2)

## Novelty boundary and priority

**[NOVELTY-RISK]** An AM-versus-cast NAB comparison in chloride already exists, using **WAAM**; a generic Cu–Ni sulfide observation already exists in bulk cells. **[GAP]** The retrieved evidence does not establish a quantitative sulfide-by-oxygen-by-history map for **single-stream pre-alloyed-powder laser DED** C70600/C71500/C95800/C63020; nor did it establish small-well, element-resolved comparisons of **deposit, fusion zone, HAZ, substrate, single track, thin wall, atomization splat, and crucible skull**. Report those as *evidence gaps in this search*, not a claim that no publication exists. Establish actual powder, deposit, and substrate wt% by assay before assigning a nominal grade. (shahriari2023corrosionperformanceof pages 1-2, shahriari2023corrosionperformanceof pages 14-14, yuan2007surfacecharacterizationand pages 3-5)

**Most naval-relevant information per test:** **(1)** sulfide dose **× exposure order**, because it interrogates polluted harbor exposure and persistent film damage; **(2)** sulfide **× measured oxygen**, but only with gas-controlled containment; **(3)** FeSO₄ prefilm **× subsequent challenge** for condenser applications. With the currently described open wells, prioritize **sulfide/history plus measured air-equilibrated oxygen** first, and perform the FeSO₄ conditioning in a separate station. (yuan2007surfacecharacterizationand pages 3-5, yuan2007surfacecharacterizationand pages 8-11, lewis1981evaluationofcoppernickel pages 43-48)

## Top 5 changes to the small-cell plan for copper alloys

1. **Replace a single freshly polished NaCl CPP ranking with measured sulfide dose × exposure-history cohorts**, including clean-prefilmed and sulfided-then-clean specimens; retain 24-h and longer companion exposures. (yuan2007surfacecharacterizationand pages 3-5, yuan2007surfacecharacterizationand pages 8-11)
2. **Characterize the fluid in the actual well:** sulfide at start/end; dissolved oxygen, pH, temperature, evaporation and turbidity controls. Use a sealed variant before claiming oxygen-poor results. (yuan2007surfacecharacterizationand pages 3-5, nady2017corrosionbehaviorand pages 1-2)
3. **Make film formation and ferrous-sulfate conditioning separate, controlled steps.** Include untreated, clean-prefilmed, and Fe-conditioned references rather than dosing Fe²⁺ into a sulfide-containing well. (lewis1981evaluationofcoppernickel pages 17-19, lewis1981evaluationofcoppernickel pages 43-48)
4. **Prioritize area-registered, unpolarized deposit/fusion-zone/HAZ/substrate comparisons and element-resolved ICP mass balance.** Use microscopy and depth profiling to distinguish NAB phase-selective attack from Cu–Ni film changes; qualify O-ring sealing and electrical isolation at every narrow boundary. (shahriari2023corrosionperformanceof pages 1-2, shahriari2023corrosionperformanceof pages 14-14, yuan2007surfacecharacterizationand pages 3-5)
5. **Use OCP, directly measured near-OCP resistance, full current traces, and post-test morphology as complementary outputs—not an assumed Stern–Geary *i*corr, a forced Tafel fit, or a universal breakdown potential.** Record Ag/AgCl temperature and reference conditions, scan termination criterion, and whether each value describes fresh, conditioned, or previously polarized metal. (yuan2007surfacecharacterizationand pages 3-5, shahriari2023corrosionperformanceof pages 14-14, shahriari2023corrosionperformanceof pages 2-4)

References

1. (yuan2007surfacecharacterizationand pages 3-5): S.J. Yuan and S.O. Pehkonen. Surface characterization and corrosion behavior of 70/30 cu-ni alloy in pristine and sulfide-containing simulated seawater. Corrosion Science, 49:1276-1304, Mar 2007. URL: https://doi.org/10.1016/j.corsci.2006.07.003, doi:10.1016/j.corsci.2006.07.003. This article has 298 citations and is from a highest quality peer-reviewed journal.

2. (yuan2007surfacecharacterizationand pages 8-11): S.J. Yuan and S.O. Pehkonen. Surface characterization and corrosion behavior of 70/30 cu-ni alloy in pristine and sulfide-containing simulated seawater. Corrosion Science, 49:1276-1304, Mar 2007. URL: https://doi.org/10.1016/j.corsci.2006.07.003, doi:10.1016/j.corsci.2006.07.003. This article has 298 citations and is from a highest quality peer-reviewed journal.

3. (nady2017corrosionbehaviorand pages 1-2): H. Nady, M.M. El-Rabiei, and M. Samy. Corrosion behavior and electrochemical properties of carbon steel, commercial pure titanium, copper and copper–aluminum–nickel alloy in 3.5% sodium chloride containing sulfide ions. Egyptian Journal of Petroleum, 26:79-94, Mar 2017. URL: https://doi.org/10.1016/j.ejpe.2016.02.008, doi:10.1016/j.ejpe.2016.02.008. This article has 110 citations.

4. (lewis1981evaluationofcoppernickel pages 43-48): R. O. Lewis and F. Laque. Evaluation of copper-nickel alloys for otec applications. ArXiv, Apr 1981. URL: https://doi.org/10.2172/6255887, doi:10.2172/6255887. This article has 5 citations.

5. (yuan2007surfacecharacterizationand pages 1-3): S.J. Yuan and S.O. Pehkonen. Surface characterization and corrosion behavior of 70/30 cu-ni alloy in pristine and sulfide-containing simulated seawater. Corrosion Science, 49:1276-1304, Mar 2007. URL: https://doi.org/10.1016/j.corsci.2006.07.003, doi:10.1016/j.corsci.2006.07.003. This article has 298 citations and is from a highest quality peer-reviewed journal.

6. (nady2017corrosionbehaviorand pages 3-4): H. Nady, M.M. El-Rabiei, and M. Samy. Corrosion behavior and electrochemical properties of carbon steel, commercial pure titanium, copper and copper–aluminum–nickel alloy in 3.5% sodium chloride containing sulfide ions. Egyptian Journal of Petroleum, 26:79-94, Mar 2017. URL: https://doi.org/10.1016/j.ejpe.2016.02.008, doi:10.1016/j.ejpe.2016.02.008. This article has 110 citations.

7. (nady2017corrosionbehaviorand pages 4-5): H. Nady, M.M. El-Rabiei, and M. Samy. Corrosion behavior and electrochemical properties of carbon steel, commercial pure titanium, copper and copper–aluminum–nickel alloy in 3.5% sodium chloride containing sulfide ions. Egyptian Journal of Petroleum, 26:79-94, Mar 2017. URL: https://doi.org/10.1016/j.ejpe.2016.02.008, doi:10.1016/j.ejpe.2016.02.008. This article has 110 citations.

8. (yuan2007surfacecharacterizationand pages 5-8): S.J. Yuan and S.O. Pehkonen. Surface characterization and corrosion behavior of 70/30 cu-ni alloy in pristine and sulfide-containing simulated seawater. Corrosion Science, 49:1276-1304, Mar 2007. URL: https://doi.org/10.1016/j.corsci.2006.07.003, doi:10.1016/j.corsci.2006.07.003. This article has 298 citations and is from a highest quality peer-reviewed journal.

9. (lewis1981evaluationofcoppernickel pages 17-19): R. O. Lewis and F. Laque. Evaluation of copper-nickel alloys for otec applications. ArXiv, Apr 1981. URL: https://doi.org/10.2172/6255887, doi:10.2172/6255887. This article has 5 citations.

10. (zarebidaki2025evaluationofcorrosion pages 11-14): Arman Zarebidaki and Danesh Dadras. Evaluation of corrosion resistance of cu, cu-10 wt% ni, cu-20 wt% ni, and electroless ni-b and ni-p coatings in simulated seawater. Jun 2025. URL: https://doi.org/10.21203/rs.3.rs-6881634/v1, doi:10.21203/rs.3.rs-6881634/v1.

11. (zarebidaki2025evaluationofcorrosion pages 1-5): Arman Zarebidaki and Danesh Dadras. Evaluation of corrosion resistance of cu, cu-10 wt% ni, cu-20 wt% ni, and electroless ni-b and ni-p coatings in simulated seawater. Jun 2025. URL: https://doi.org/10.21203/rs.3.rs-6881634/v1, doi:10.21203/rs.3.rs-6881634/v1.

12. (zarebidaki2025evaluationofcorrosion pages 7-11): Arman Zarebidaki and Danesh Dadras. Evaluation of corrosion resistance of cu, cu-10 wt% ni, cu-20 wt% ni, and electroless ni-b and ni-p coatings in simulated seawater. Jun 2025. URL: https://doi.org/10.21203/rs.3.rs-6881634/v1, doi:10.21203/rs.3.rs-6881634/v1.

13. (zarebidaki2025evaluationofcorrosion pages 5-7): Arman Zarebidaki and Danesh Dadras. Evaluation of corrosion resistance of cu, cu-10 wt% ni, cu-20 wt% ni, and electroless ni-b and ni-p coatings in simulated seawater. Jun 2025. URL: https://doi.org/10.21203/rs.3.rs-6881634/v1, doi:10.21203/rs.3.rs-6881634/v1.

14. (shahriari2023corrosionperformanceof pages 2-4): Ayda Shahriari, Dharmendra Chalasani, Babak Shalchi Amirkhiz, and Mohsen Mohammadi. Corrosion performance of wire arc additively manufactured nab alloy. npj Materials Degradation, 7:1-15, Oct 2023. URL: https://doi.org/10.1038/s41529-023-00405-x, doi:10.1038/s41529-023-00405-x. This article has 30 citations and is from a peer-reviewed journal.

15. (shahriari2023corrosionperformanceof pages 2-2): Ayda Shahriari, Dharmendra Chalasani, Babak Shalchi Amirkhiz, and Mohsen Mohammadi. Corrosion performance of wire arc additively manufactured nab alloy. npj Materials Degradation, 7:1-15, Oct 2023. URL: https://doi.org/10.1038/s41529-023-00405-x, doi:10.1038/s41529-023-00405-x. This article has 30 citations and is from a peer-reviewed journal.

16. (lewis1981evaluationofcoppernickel pages 60-64): R. O. Lewis and F. Laque. Evaluation of copper-nickel alloys for otec applications. ArXiv, Apr 1981. URL: https://doi.org/10.2172/6255887, doi:10.2172/6255887. This article has 5 citations.

17. (gao2022corrosionbehaviorof pages 2-4): Xin Gao and Ming Liu. Corrosion behavior of high-strength c71500 copper-nickel alloy in simulated seawater with high concentration of sulfide. Materials, 15:8513, Nov 2022. URL: https://doi.org/10.3390/ma15238513, doi:10.3390/ma15238513. This article has 34 citations.

18. (gao2022corrosionbehaviorof pages 1-2): Xin Gao and Ming Liu. Corrosion behavior of high-strength c71500 copper-nickel alloy in simulated seawater with high concentration of sulfide. Materials, 15:8513, Nov 2022. URL: https://doi.org/10.3390/ma15238513, doi:10.3390/ma15238513. This article has 34 citations.

19. (yuan2007surfacecharacterizationand pages 26-29): S.J. Yuan and S.O. Pehkonen. Surface characterization and corrosion behavior of 70/30 cu-ni alloy in pristine and sulfide-containing simulated seawater. Corrosion Science, 49:1276-1304, Mar 2007. URL: https://doi.org/10.1016/j.corsci.2006.07.003, doi:10.1016/j.corsci.2006.07.003. This article has 298 citations and is from a highest quality peer-reviewed journal.

20. (nady2017corrosionbehaviorand pages 2-3): H. Nady, M.M. El-Rabiei, and M. Samy. Corrosion behavior and electrochemical properties of carbon steel, commercial pure titanium, copper and copper–aluminum–nickel alloy in 3.5% sodium chloride containing sulfide ions. Egyptian Journal of Petroleum, 26:79-94, Mar 2017. URL: https://doi.org/10.1016/j.ejpe.2016.02.008, doi:10.1016/j.ejpe.2016.02.008. This article has 110 citations.

21. (gao2022corrosionbehaviorof pages 4-5): Xin Gao and Ming Liu. Corrosion behavior of high-strength c71500 copper-nickel alloy in simulated seawater with high concentration of sulfide. Materials, 15:8513, Nov 2022. URL: https://doi.org/10.3390/ma15238513, doi:10.3390/ma15238513. This article has 34 citations.

22. (gao2022corrosionbehaviorof pages 5-6): Xin Gao and Ming Liu. Corrosion behavior of high-strength c71500 copper-nickel alloy in simulated seawater with high concentration of sulfide. Materials, 15:8513, Nov 2022. URL: https://doi.org/10.3390/ma15238513, doi:10.3390/ma15238513. This article has 34 citations.

23. (gao2022corrosionbehaviorof pages 8-10): Xin Gao and Ming Liu. Corrosion behavior of high-strength c71500 copper-nickel alloy in simulated seawater with high concentration of sulfide. Materials, 15:8513, Nov 2022. URL: https://doi.org/10.3390/ma15238513, doi:10.3390/ma15238513. This article has 34 citations.

24. (shahriari2023corrosionperformanceof pages 1-2): Ayda Shahriari, Dharmendra Chalasani, Babak Shalchi Amirkhiz, and Mohsen Mohammadi. Corrosion performance of wire arc additively manufactured nab alloy. npj Materials Degradation, 7:1-15, Oct 2023. URL: https://doi.org/10.1038/s41529-023-00405-x, doi:10.1038/s41529-023-00405-x. This article has 30 citations and is from a peer-reviewed journal.

25. (shahriari2023corrosionperformanceof pages 14-14): Ayda Shahriari, Dharmendra Chalasani, Babak Shalchi Amirkhiz, and Mohsen Mohammadi. Corrosion performance of wire arc additively manufactured nab alloy. npj Materials Degradation, 7:1-15, Oct 2023. URL: https://doi.org/10.1038/s41529-023-00405-x, doi:10.1038/s41529-023-00405-x. This article has 30 citations and is from a peer-reviewed journal.

26. (shahriari2023corrosionperformanceof pages 12-14): Ayda Shahriari, Dharmendra Chalasani, Babak Shalchi Amirkhiz, and Mohsen Mohammadi. Corrosion performance of wire arc additively manufactured nab alloy. npj Materials Degradation, 7:1-15, Oct 2023. URL: https://doi.org/10.1038/s41529-023-00405-x, doi:10.1038/s41529-023-00405-x. This article has 30 citations and is from a peer-reviewed journal.

27. (jin2019surfacecharacterizationand pages 3-5): Tingzhu Jin, Weifang Zhang, Ning Li, Xuerong Liu, Lu Han, and Wei Dai. Surface characterization and corrosion behavior of 90/10 copper-nickel alloy in marine environment. Materials, 12:1869, Jun 2019. URL: https://doi.org/10.3390/ma12111869, doi:10.3390/ma12111869. This article has 148 citations.

28. (jin2019surfacecharacterizationand pages 11-13): Tingzhu Jin, Weifang Zhang, Ning Li, Xuerong Liu, Lu Han, and Wei Dai. Surface characterization and corrosion behavior of 90/10 copper-nickel alloy in marine environment. Materials, 12:1869, Jun 2019. URL: https://doi.org/10.3390/ma12111869, doi:10.3390/ma12111869. This article has 148 citations.

29. (lewis1981evaluationofcoppernickel pages 14-17): R. O. Lewis and F. Laque. Evaluation of copper-nickel alloys for otec applications. ArXiv, Apr 1981. URL: https://doi.org/10.2172/6255887, doi:10.2172/6255887. This article has 5 citations.
