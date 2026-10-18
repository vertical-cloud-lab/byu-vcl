<!--
Edison Scientific LITERATURE task (batch 1)
- Task ID: 235c810c-380a-4154-88be-bb5e315f0ebe
- Submitted: 2026-10-18T01:20:08Z
- Fetched: 2026-10-18T01:50:09Z (status: success)
- Raw trajectory JSON: ../raw/c1-09-rapid-solidification-proxies-cu.json.gz
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

QUESTION: Which cheap, rapidly solidified forms of a copper alloy predict the
corrosion of its blown-powder DED deposit? Cover laser surface melting (LSM)
of NAB and Cu-Ni, single laser tracks, splat-quenched or melt-spun ribbons,
arc-melted buttons, and atomized powder consolidated by other routes. For
each, report the cooling rate, the resulting phases (retained beta or
martensite, suppressed kappa, Ni and Fe in solution), and corrosion in
chloride against the cast or wrought alloy, with numbers. Has any study
compared LSM or single-track corrosion with a multi-layer deposit of the
same alloy, showing whether reheating by later layers changes it? Which proxy
would rank compositions the same way as multi-layer DED, and which would
mislead?

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

QUESTION: Which cheap, rapidly solidified forms of a copper alloy predict the
corrosion of its blown-powder DED deposit? Cover laser surface melting (LSM)
of NAB and Cu-Ni, single laser tracks, splat-quenched or melt-spun ribbons,
arc-melted buttons, and atomized powder consolidated by other routes. For
each, report the cooling rate, the resulting phases (retained beta or
martensite, suppressed kappa, Ni and Fe in solution), and corrosion in
chloride against the cast or wrought alloy, with numbers. Has any study
compared LSM or single-track corrosion with a multi-layer deposit of the
same alloy, showing whether reheating by later layers changes it? Which proxy
would rank compositions the same way as multi-layer DED, and which would
mislead?

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


# Can a rapidly solidified coupon predict copper-alloy DED corrosion?

**Not yet reliably.** Laser surface melting (LSM) demonstrably improves the chloride corrosion of *one manganese–nickel–aluminium bronze* relative to its own casting, but that is not evidence that LSM ranks compositions as their **multilayer, single-powder-feed laser DED deposits** will. In the studies located, no same-alloy experiment measured chloride corrosion of an LSM surface or isolated single laser track **and** a multilayer blown-powder DED build under matched conditions. Reheating, substrate dilution, defects and film-growth time remain uncalibrated differences. Unless otherwise noted, electrolyte volume and alloy-specific cooling rate were **not reported**; absence of a number below is intentional. (tang2004effectoflaser pages 2-4, zhao2022thelaserdeposited pages 2-4, huo2025modulatingheatinput pages 2-4)

## Direct proxy evidence and quantitative controls

**1. Cast manganese–nickel–aluminium bronze versus LSM — the strongest direct proxy comparison.** C. H. Tang, F. T. Cheng and H. C. Man, “Effect of laser surface melting on the corrosion and cavitation erosion behaviors of a manganese-nickel-aluminium bronze,” *Materials Science and Engineering A* **373** (2004), 195–203. **DOI: 10.1016/j.msea.2004.01.016.** The cast UNS C95700 material contained **Cu 75.6, Mn 10.8, Al 7.8, Fe 3.6, Ni 2.2 wt%**. Overlapping, powder-free Nd:YAG LSM tracks at 1 kW produced an approximately single-phase, fine-grained **bcc β-derived phase** rather than the casting’s heterogeneous α/β/intermetallic structure; the measured laser-zone grain size was **4.2 µm**. The study does **not** report a measured °C/s cooling rate: **10³–10⁶ °C/s** is a *general LSM range*, not its measured rate. This is **retained β-type material**, not evidence for completely transformed β′ martensite; dissolving the Mn/Fe-rich particles increased Mn and Fe in solution. The bulk flat immersion cell exposed **1 cm² in 300 mL** aerated **3.5 wt% NaCl at 23 °C** for **12 h**; OCP was followed for **24 h**. For cast, and LSM conditions MAB-1-15/MAB-2-35/MAB-4-45 respectively, mass-loss rates were **31.85/28.67/16.59/21.33 µg cm⁻² h⁻¹**, *E*corr **−372/−286/−290/−287 mV versus saturated calomel electrode (SCE)**, and fitted *i*corr **9.52/9.05/4.26/6.81 µA cm⁻²**. Thus even three rapidly melted surfaces of the **same chemistry** differed; the best halved the 12-h mass loss. No element-resolved dissolution, *R*p, breakdown/protection potential or deposit comparison was reported. **[CITE] [NUMBERS] [NAVY: propeller application] [CUBXL: validate a bulk-cell bridge; 150 µL/0.1 cm² is only ~1.5 mL cm⁻², versus 300 mL cm⁻² here] [GAP: no multilayer DED arm].** (tang2004effectoflaser pages 1-2, tang2004effectoflaser pages 2-4, cottam2012lasermaterialsprocessing pages 5-7, tang2004effectoflaser pages 6-7)

**2. The same bronze, LSM versus deliberately Al-alloyed laser surface — a warning against equating corrosion and cavitation rankings.** C. H. Tang, F. T. Cheng and H. C. Man, “Laser surface alloying of a marine propeller bronze using aluminium powder: Part I: Microstructural analysis and cavitation erosion study,” *Surface & Coatings Technology* **200** (2006), 2602–2609. **DOI: 10.1016/j.surfcoat.2004.12.021**; and the same authors, “Part II: Corrosion and erosion–corrosion synergism,” *Surface & Coatings Technology* **200** (2006), 2594–2601. **DOI: 10.1016/j.surfcoat.2004.12.022.** Starting from **Cu–10.8Mn–7.8Al–3.6Fe–2.2Ni wt%**, preplaced Al powder raised surface Al to about **10.5 wt%**: this is **laser surface alloying, not single-stream pre-alloyed-powder DED**. Both the LSM and alloyed zones were reported as predominantly **bcc β-type single phase**; the modified zone was approximately **1 mm** deep. In a **1-cm², 300-mL** flat cell, aerated **3.5% NaCl at 23 °C**, renewed daily for **14 days**, cast/LSM/Al-alloyed mass-loss rates were **5.1/3.4/2.4 µg cm⁻² h⁻¹**; *i*corr **9.52/4.26/3.92 µA cm⁻²**, and *i*pass **5.67/5.91/5.10 mA cm⁻²**. The accompanying table’s extraction loses the minus signs on its potential entries; the curves and the preceding paper support approximately **−372/−290/−300 mV versus SCE**, rather than positive potentials. Under cavitation in chloride, loss rates were **2284/431/233 µg cm⁻² h⁻¹**: the **9.8-fold** improvement for alloying is an *erosion–corrosion* result, **not** a 9.8-fold static-corrosion improvement. No measured cooling rate, element-resolved dissolution, breakdown potential, or multilayer DED comparison. **[CITE] [NUMBERS] [NAVY: propellers] [CUBXL: retain time-matched gravimetry and distinguish static corrosion from cavitation] [NOVELTY-RISK: LSM-versus-cast chloride comparisons already exist; a matched DED-plus-microcell comparison does not].** (tang2006lasersurfacealloying pages 1-2, tang2006lasersurfacealloying pages 4-6, tang2006lasersurfacealloyinga pages 2-4, tang2006lasersurfacealloyinga pages 4-5)

**3. Cu–Ni surface remelting: available numbers concern an *arc*, not Cu–Ni LSM.** F. Koeini, M. Heydarzadeh Sohi and P. Pirayesh, “Surface Alloying of Cupronickel Alloy with Aluminum using Tungsten Inert Gas Process,” *Archives of Metallurgy and Materials* **68** (2023), 161–170. **DOI: 10.24425/amm.2023.141490.** The **wrought Cu–Ni** starting material was **Cu 87.71, Ni 10.60, Fe 0.93, Zn 0.60 wt%** (Mn **0.04%**), not C71500. TIG surface melting without added powder yielded fine **α-Cu–Ni dendrites and porosity**; adding preplaced Al changed composition and, depending on heat input, produced α, Al₂Cu/Cu₉Al₄, κ-bearing regions and β′-like martensitic structures. Those Al-alloyed structures must **not** be attributed to powder-free Cu–Ni melting. In a conventional three-electrode cell of **unreported area and volume**, room-temperature **3.5 wt% NaCl**, polarization at **2 mV s⁻¹ versus SCE**, substrate/TIG-melted/one-pass Al-alloyed/two-pass Al-alloyed *E*corr were **−249/−255/−281/−211 mV versus SCE**, and fitted *i*corr were **7.19/11.40/3.84/17.76 µA cm⁻²**. The **two-pass** specimen was *more noble but had the highest fitted current*: even remelting a surface did not preserve its apparent ranking. No cooling rate, reported immersion duration, *R*p, attack depth, Cu/Ni dissolution or laser-versus-DED experiment. **[CITE] [NUMBERS] [NAVY: Cu–Ni marine alloy] [CUBXL: log pores/defects and do not rank by *E*corr alone] [GAP: Cu–Ni laser-LSM-to-DED comparison].** (koeini2023surfacealloyingof pages 1-2, koeini2023surfacealloyingof pages 2-4, koeini2023surfacealloyingof pages 6-8, koeini2023surfacealloyingof pages 4-6)

**4. Atomized NAB powder consolidated without laser deposition: an unusually useful *counterexample*.** A. Fayanas, A. Veiga, A. Perez, A. Concustell, S. Molas and N. Ordas, “Nickel Aluminium Bronze Alloys With Enhanced Erosion-Corrosion Resistance And Mechanical Strength,” *Journal of the Japan Society of Powder and Powder Metallurgy* **72** (2025), S819–S826. **DOI: 10.2497/jjspm.15F-T13-08.** Compared **continuous-cast Cu–9.7Al–4.4Ni–4.3Fe–0.9Mn** to **pressed/sintered/HIP Cu–10.0Al–5.0Ni–4.0Fe–1.0Mn**, all wt%, plus an independently HIP-consolidated powder. Sintering was **1035 °C/3 h**, then HIP **950 °C/2 h at 140 MPa**; the other route HIPed powder at **950 °C/3 h**. These are *high-temperature consolidation histories*, not preservation of the particles’ rapid quench: measured as-processed β′ fractions were about **1% cast versus 4% sinter+HIP**; κII and κIII persisted and prior-particle-boundary κII occurred in the directly HIPed material. Annealing **700 °C/2 h** transformed β′ toward α plus κ and introduced fine κV. Using a **bulk three-electrode cell, volume and working area unreported**, **3.5 wt% NaCl**, **Ag/AgCl (3 M KCl)**, the cast versus sinter+HIP had initial *E*corr **−0.260 versus −0.388 V** and fitted *j*corr **9.90 versus 6.85 µA cm⁻²**; after **480 h**, they were **−0.208 versus −0.277 V** and **6.45 versus 3.02 µA cm⁻²**. After annealing and 480 h, **cast 2.12 versus sinter+HIP 10.4 µA cm⁻²**: **the relative ordering inverted after heat treatment**. The paper’s calculated penetration rates at 480 h were **0.07 versus 0.04 mm y⁻¹** unannealed, but **0.02 versus 0.12 mm y⁻¹** annealed; these are *electrochemical estimates*, not measured 480-h pit depths. Cooling rates and element-specific dissolution were not measured. **[CITE] [NUMBERS] [NAVY: marine components] [CUBXL: benchmark both fresh and aged states; assay prior-particle boundaries] [NOVELTY-RISK: powder-to-consolidate versus cast NAB corrosion is published] [GAP: it does not predict DED from as-atomized splats].** The cropped corrosion table and associated curves were also inspected. (fayanas2025nickelaluminiumbronze pages 1-2, fayanas2025nickelaluminiumbronze pages 2-5, fayanas2025nickelaluminiumbronze pages 5-7, fayanas2025nickelaluminiumbronze media d6642ebf)

**5. Actual laser-deposited NAB: substrate chemistry can overwhelm an apparent cooling-rate proxy.** L. Zhao, K. Li, J. Yao, Y. Yuan and B. Du, “The Laser Deposited Nickel-Aluminum Bronze Coatings on SUS630 Stainless Steel and Its Corrosion Resistance in 3.5 wt.% NaCl Solution,” *Metals* **12** (2022), 781. **DOI: 10.3390/met12050781.** Pre-alloyed powder was **Cu 81.1, Al 10.8, Ni 4.1, Fe 4.0 wt%**; the **laser-deposited/clad** coating was made on stainless steel either directly (N-1), across a Ni–5Al interlayer (N-2), or across an 80Ni–20Cr interlayer (N-3). The actual experiment used **2400 W**, **3.2-mm** spot and **50%** overlapping passes—not the proposed 300–500-W process. Deposits contained α, β′/retained-β-related constituents and κ; direct steel dilution added Fe-rich dendrites. A **1-cm² bulk flat electrode** in **3.5 wt% NaCl, 25 ± 5 °C**, volume **unreported**, used **Ag/AgCl/saturated KCl** and **20-min** pre-polarization stabilization; EIS followed immersion through **21 days**. For N-1/N-2/N-3: *E*corr **−248/−255/−252 mV versus Ag/AgCl**, fitted *i*corr **7.82/4.65/4.09 µA cm⁻²**, and **Stern–Geary-derived, not directly LPR-measured** *R*p **2810/5275/4865 Ω cm²**. Maximum attack depth by 21 days was **3.4 ± 0.1/2.0 ± 0.1/1.8 ± 0.1 µm**. Fitted charge-transfer resistance on day 21 was **1444/51,470/85,100 Ω cm²**. These are *different composite chemistries/substrate-dilution controls*, **not** a single-track-versus-multilayer test or a paired cast control; a literature cast comparison in the article is not method-matched. The paper did **not** measure cooling rates, electrolyte volume or individual elemental release. **[CITE] [NUMBERS] [NAVY: proposed propeller architecture] [CUBXL: spot fusion zone and substrate separately; measure Fe/Ni/Cr dilution] [NOVELTY-RISK: laser-deposited NAB chloride corrosion and long-term EIS already published] [GAP: matched low-power same-feedstock single-track/multilayer data].** (zhao2022thelaserdeposited pages 2-4, zhao2022thelaserdeposited pages 7-10, zhao2022thelaserdeposited pages 13-14, zhao2022thelaserdeposited pages 10-13)

**6. Multilayer thermal cycling is consequential, but the accessible quantitative experiment used WAAM rather than laser DED.** R. Huo, Z. Wang, M. Wang, R. Wang, S. Zhang, C. Zhang, C. Wu, H. Chen and J. Chen, “Modulating Heat Input to Optimize Corrosion Resistance of Nickel–Aluminum Bronze Manufactured by Cold Metal Transfer Additive Manufacturing,” *Materials* **18** (2025), 2205. **DOI: 10.3390/ma18102205.** **Wire-arc AM**, ERCuNiAl wire **Al 8.73, Fe 5.90, Ni 4.52, Mn 1.39 wt%, Cu balance**, deposited on a different-composition copper substrate. Four heat inputs **243.8/378.8/502.8/644.7 J mm⁻¹** produced increasing α grain sizes **38.26/47.50/65.37/74.62 µm**, coarser κ, and **α + κ + γ₂-Cu₉Al₄**, with **no detected retained β or β′** in these specimens: rapid solidification does *not* guarantee martensite after thermal cycling. In an aerated **1-cm² bulk cell**, volume **unreported**, **3.5 wt% NaCl at 25 ± 5 °C**, *OCP* was monitored **3600 s** and then EIS; the S1–S4 reported polarization-derived potentials were **−269.61/−466.62/−517.77/−700.94 mV versus SCE**, and fitted *i*corr **2.56/3.85/5.03/7.52 µA cm⁻²**. Corresponding EIS *R*ct were **2485/1966/1284/707 Ω cm²**; the paper does not supply measured °C/s, corrosion depth or dissolution rates. Note that the authors’ **1-h OCP values differ from their polarization-derived potentials**, and their EIS table repeats “S2” where the third row appears to denote S3; neither should be silently substituted for the other. **[CITE] [NUMBERS] [NAVY: shipbuilding application] [CUBXL: add a 60-min OCP/EIS timepoint and record layer position] [GAP: not an LSM/DED matched test].** (huo2025modulatingheatinput pages 4-5, huo2025modulatingheatinput pages 5-7, huo2025modulatingheatinput pages 7-10, huo2025modulatingheatinput pages 10-13, huo2025modulatingheatinput pages 13-15)

**7. A cast composition control, not an arc-melted button.** Y. Tan, H. Xie, X. Feng, S. Huang, W. Zhang, L. Peng, W. Wang and Y. Zhao, “Effect of Al/Ni Ratio on the Microstructure and Properties of Nickel–Aluminum Bronze Alloys,” *Materials* **17** (2024), 1330. **DOI: 10.3390/ma17061330.** Four **4-kg vacuum-induction-melted *cast ingots***, with Cu balance and measured **Al/Ni/Fe/Mn** respectively **6.94/6.82/4.10/1.72; 7.90/6.13/3.92/2.12; 8.94/5.18/4.12/2.18; 9.94/3.99/3.94/1.82 wt%**. Increasing Al/Ni introduced more β′ and κ, rather than proving any small arc button has DED-like phases. In **3.5 wt% NaCl, 25 °C**, bulk **1-cm²** electrochemical specimens versus **Ag/AgCl**, solution volume **unreported**, had fitted *i*corr after **10 d** of **0.50/1.34/1.77/2.16 µA cm⁻²** and after **30 d** of **0.35/0.36/0.69/0.78 µA cm⁻²**; 30-d EIS-derived *R*p was **521,367/196,434/111,544/90,707 Ω cm²**. At 30 d the first composition’s gravimetric penetration was **0.00267 mm y⁻¹**, while the most Al-rich exhibited **>3 µm maximum localized depth**. These are *cast-composition* and film-maturation controls; reported polarization *R*p is inferred from Tafel fits, whereas EIS *R*p is circuit-derived. No measured solidification rate, elemental dissolution or DED ranking. **[CITE] [NUMBERS] [CUBXL: avoid confusing composition effects with quench effects; retain EIS and depth endpoints] [GAP: these are cast ingots, not rapidly quenched arc buttons].** (tan2024effectofalni pages 2-4, tan2024effectofalni pages 4-6, tan2024effectofalni pages 10-12, tan2024effectofalni pages 12-16)

**8. Welded cast NAB is a repair control, not a laser proxy.** X. Zhao, Y. Qi, J. Wang, T. Peng, Z. Zhang and K. Li, “Effect of Weld and Surface Defects on the Corrosion Behavior of Nickel Aluminum Bronze in 3.5% NaCl Solution,” *Metals* **10** (2020), 1227. **DOI: 10.3390/met10091227.** Cast C95810 defect-free metal was **Cu 79.9, Al 9.24, Fe 4.8, Ni 4.43, Mn 1.39 wt%**, versus **Cu 81.9, Al 8.66, Fe 3.4, Ni 4.2, Mn 1.52 wt%** in the welded specimen; weld metal additionally contained β′. **Bulk electrochemical area 0.38 cm²**, volume **unreported**, with **SCE** in **3.5% NaCl**; morphology/impedance followed **3–432 h**, with electrolyte refreshed every **7 days**. The weld corroded faster early, but its film and charge-transfer resistances overtook the defect-free casting at **432 h**; casting defects prevented development of the outer copper-hydroxychloride layer. The accessible text provides **no reliable extractable numerical *E*corr, *R*p, dissolution rate or depth**. Funding included equipment pre-research programs, but the record does not establish US Navy funding. **[CITE] [NAVY: maritime repair relevance, not a verified Navy grant] [CUBXL: treat HAZ, deposit and defects as separate locations and retain an aged reading] [NOVELTY-RISK: weld-versus-cast chloride studies exist].** (zhao2020effectofweld pages 1-4, zhao2020effectofweld pages 4-8, zhao2020effectofweld pages 11-14)

## Requested candidates without a validated prediction

- **NAB LSM specifically:** R. Cottam and colleagues’ NAB laser-processing work is referenced in the accessible laser-processing review, but the underlying NAB laser electrochemical paper was not available as verifiable full text here. Do **not** transfer Tang’s **high-Mn C95700** numbers to **C95800 or C63020**. R. Cottam, “Laser Materials Processing for Improved Corrosion Performance,” in *Environmental and Industrial Corrosion* (2012), **DOI: 10.5772/52423**, distinguishes **laser *heat treatment*** from *surface melting* and states that the former can dissolve κ lamellae while avoiding the laser-clad Widmanstätten structure; its reproduced polarization plot does **not** establish numerical rates or multilayer predictive validity. Cooling **10³–10⁶ °C s⁻¹** is a broad LSM process range. **[CITE] [NAVY: review acknowledges Defence Materials Technology Centre submarine/surface-ship repair funding] [GAP].** (cottam2012lasermaterialsprocessing pages 5-7, cottam2012lasermaterialsprocessing pages 10-13)
- **Cu–Ni laser LSM; laser DED single tracks:** no directly verifiable matched Cu–Ni laser-LSM/cast-or-wrought/DED chloride dataset, or isolated NAB/Cu–Ni single-track-versus-multilayer corrosion dataset, was located. A laser *track* is not a 3–4-mm uniform exposure if its width is narrower than the O-ring. The Cu–Ni TIG evidence above is an **arc** analogy only. **[GAP] [CUBXL: do not bridge a track with a well that also wets substrate].** (koeini2023surfacealloyingof pages 2-4, zhao2022thelaserdeposited pages 2-4)
- **Atomization splats, crucible skull and melt-spun ribbons:** no verified chloride-corrosion ranking of these forms against a same-feedstock, multilayer blown-powder NAB or naval Cu–Ni DED deposit was located; therefore **cooling rate, retained β′/κ fractions and corrosion numbers for the proposed forms are unknown**, not interchangeable with the measured laser values above. Thin splats/ribbons also present substrate, oxidation, area and electrical-contact problems. **[GAP] [CUBXL: require a continuous, characterized, electrically isolated metal patch before electrochemistry].** (fayanas2025nickelaluminiumbronze pages 1-2, tang2004effectoflaser pages 2-4)
- **Arc-melted buttons:** no direct validated arc-button-to-DED corrosion ranking was located. Do not relabel the **kilogram-scale induction-cast ingots** in item 7 as small arc buttons, nor assume an arc button’s unmeasured °C/s matches a laser melt pool. **[GAP].** (tan2024effectofalni pages 2-4)
- **LPBF is not DED:** A. Sparrow, W. Smith and T. Y. Ansell, “LPBF Parameter Optimization of Mechanical, Non-Thermal Generated C71500 Powder,” *Metals* **16** (2026), 10, **DOI: 10.3390/met16010010**, documents naval-use C71500 **laser powder-bed fusion**, using **mechanically generated—not atomized—powder** and mechanical/porosity optimization; it reports **no seawater electrochemical results or DED-proxy ranking**. This is a genuine existing Navy-institution materials-process comparator, not corrosion validation. **[CITE] [NAVY: Naval Postgraduate School] [GAP].** (sparrow2025lpbfparameteroptimization pages 1-3, sparrow2025lpbfparameteroptimization pages 3-6)

**Proxy-ranking judgment.** For *selecting which experiment to run first*, a same-powder **multitrack, multilayer miniature DED coupon**—ideally including a repair interface—has the closest plausible thermal and chemical history, followed provisionally by a same-feedstock *laser-deposited* pad after confirming its dilution and κ/β′ map. This is an **experimental priority, not an experimentally validated composition ranking**. LSM of a matching casting is valuable as a controlled **surface-microstructure intervention**, but would mislead if its dissolved κ and retained bcc β were assumed to describe reheated deposit layers. A single track, splat/ribbon, arc button or sintered/HIP powder should **not** be used to predict DED composition order without paired calibration: the direct powder-consolidation example actually changes its cast-versus-powder ordering after annealing. (tang2004effectoflaser pages 2-4, fayanas2025nickelaluminiumbronze pages 5-7, huo2025modulatingheatinput pages 5-7, zhao2022thelaserdeposited pages 2-4)

## Top 5 changes to the small-cell plan for copper alloys

1. **Make proxy validation the first design-of-experiments block.** For each actual feedstock, compare wrought/cast reference, LSM of matching bulk, a single DED track, and a **≥several-layer same-powder DED pad**, on both self-built and repair substrates. Record thermal history or estimate °C/s from a validated melt-pool measurement; map β/β′, κ, α and Fe/Ni/Cr by cross-sectional microscopy before asserting a cooling-rate mechanism. Place spots individually on top layer, reheated interior, HAZ and substrate. **Do not claim a universal proxy before paired rank-order replication.** (tang2004effectoflaser pages 2-4, fayanas2025nickelaluminiumbronze pages 2-5, huo2025modulatingheatinput pages 5-7, zhao2022thelaserdeposited pages 2-4)
2. **Add a volume- and oxygen-controlled bulk-cell bridge.** Compare the proposed **150 µL, approximately 0.1-cm² O-ring well** against the **300-mL/1-cm²** MAB benchmark under the same electrolyte, temperature, elapsed time and area. Measure actual filled/recovered volume, evaporation, pH, dissolved oxygen and solution resistance; renew or flow electrolyte for extended aging. An existing automated scanning droplet system already uses **FKM O-rings, Ag/AgCl, Pt, mixing and an approximately 4-mL recirculating loop**, so automation/O-rings alone are **not novel**. (tang2004effectoflaser pages 1-2, joress2022developmentofan pages 4-7, joress2022developmentofan pages 1-4)
3. **Separate fresh-surface screening from film-maturation qualification.** Keep the 30-min OCP for throughput, add **≥1-h and 1-, 7-, 21- and 30-day** OCP/EIS/replicated mass-loss or depth checkpoints on dedicated spots; do not serially reuse a spot after destructive polarization. The same systems changed *R*ct strongly over **21 days**, and the cast/powder response changed after **480 h** and annealing. (zhao2022thelaserdeposited pages 13-14, fayanas2025nickelaluminiumbronze pages 5-7, huo2025modulatingheatinput pages 10-13)
4. **Replace a pitting-only pass/fail rule with copper-specific endpoints.** Retain directly measured near-OCP *R*p and film-sensitive EIS where supported; report *E*corr with electrode fill and reference scale, corrosion-product morphology, maximal pit/selective-phase depth and **Cu, Ni, Fe, Al, Mn and Cr** released into electrolyte **plus an acid-recovered film/precipitate fraction**, blanks and spike recoveries. A reversal at a fixed current is an *operational* threshold, not automatically a chloride breakdown or protection potential; fitted Tafel *i*corr and assumed *B* do not substitute for element-resolved material loss. (tang2004effectoflaser pages 2-4, zhao2022thelaserdeposited pages 7-10, tan2024effectofalni pages 10-12, joress2022developmentofan pages 11-14)
5. **Engineer around narrow tracks and repair galvanics.** Verify each O-ring footprint stays wholly within its intended phase/zone; use smaller verified-area capillaries for narrow tracks and fusion boundaries, or build wider pads. Record surface roughness, cracks, porosity and O-ring-edge leakage; include galvanically coupled deposit/substrate controls rather than measuring each in isolation. Prior O-ring scanning work reports substantial cell resistance and distorted high-current scans; low-cost potentiostats must pass dummy-cell, reference-stability, compliance, *iR*-drop and reproducibility checks before accepting chloride-cycle data. (joress2022developmentofan pages 1-4, joress2022developmentofan pages 7-11, zhao2022thelaserdeposited pages 7-10, tang2006lasersurfacealloyinga pages 6-7)

References

1. (tang2004effectoflaser pages 2-4): C.H Tang, F.T Cheng, and H.C Man. Effect of laser surface melting on the corrosion and cavitation erosion behaviors of a manganese-nickel-aluminium bronze. Materials Science and Engineering A-structural Materials Properties Microstructure and Processing, 373:195-203, May 2004. URL: https://doi.org/10.1016/j.msea.2004.01.016, doi:10.1016/j.msea.2004.01.016. This article has 168 citations.

2. (zhao2022thelaserdeposited pages 2-4): Lu Zhao, Kailun Li, Jun Yao, Yixiang Yuan, and Baorui Du. The laser deposited nickel-aluminum bronze coatings on sus630 stainless steel and its corrosion resistance in 3.5 wt.% nacl solution. Metals, 12:781, Apr 2022. URL: https://doi.org/10.3390/met12050781, doi:10.3390/met12050781. This article has 8 citations.

3. (huo2025modulatingheatinput pages 2-4): Renjie Huo, Zheying Wang, Mingsheng Wang, Rui Wang, Song Zhang, Chunhua Zhang, Chenliang Wu, Haitao Chen, and Jiang Chen. Modulating heat input to optimize corrosion resistance of nickel–aluminum bronze manufactured by cold metal transfer additive manufacturing. Materials, 18:2205, May 2025. URL: https://doi.org/10.3390/ma18102205, doi:10.3390/ma18102205. This article has 5 citations.

4. (tang2004effectoflaser pages 1-2): C.H Tang, F.T Cheng, and H.C Man. Effect of laser surface melting on the corrosion and cavitation erosion behaviors of a manganese-nickel-aluminium bronze. Materials Science and Engineering A-structural Materials Properties Microstructure and Processing, 373:195-203, May 2004. URL: https://doi.org/10.1016/j.msea.2004.01.016, doi:10.1016/j.msea.2004.01.016. This article has 168 citations.

5. (cottam2012lasermaterialsprocessing pages 5-7): Ryan Cottam. Laser materials processing for improved corrosion performance. Environmental and Industrial Corrosion - Practical and Theoretical Aspects, Dec 2012. URL: https://doi.org/10.5772/52423, doi:10.5772/52423. This article has 8 citations.

6. (tang2004effectoflaser pages 6-7): C.H Tang, F.T Cheng, and H.C Man. Effect of laser surface melting on the corrosion and cavitation erosion behaviors of a manganese-nickel-aluminium bronze. Materials Science and Engineering A-structural Materials Properties Microstructure and Processing, 373:195-203, May 2004. URL: https://doi.org/10.1016/j.msea.2004.01.016, doi:10.1016/j.msea.2004.01.016. This article has 168 citations.

7. (tang2006lasersurfacealloying pages 1-2): C.H. Tang, F.T. Cheng, and H.C. Man. Laser surface alloying of a marine propeller bronze using aluminium powder: part i: microstructural analysis and cavitation erosion study. Surface & Coatings Technology, 200:2602-2609, Jan 2006. URL: https://doi.org/10.1016/j.surfcoat.2004.12.021, doi:10.1016/j.surfcoat.2004.12.021. This article has 89 citations and is from a domain leading peer-reviewed journal.

8. (tang2006lasersurfacealloying pages 4-6): C.H. Tang, F.T. Cheng, and H.C. Man. Laser surface alloying of a marine propeller bronze using aluminium powder: part i: microstructural analysis and cavitation erosion study. Surface & Coatings Technology, 200:2602-2609, Jan 2006. URL: https://doi.org/10.1016/j.surfcoat.2004.12.021, doi:10.1016/j.surfcoat.2004.12.021. This article has 89 citations and is from a domain leading peer-reviewed journal.

9. (tang2006lasersurfacealloyinga pages 2-4): C.H. Tang, F.T. Cheng, and H.C. Man. Laser surface alloying of a marine propeller bronze using aluminium powder: part ii: corrosion and erosion–corrosion synergism. Surface & Coatings Technology, 200:2594-2601, Jan 2006. URL: https://doi.org/10.1016/j.surfcoat.2004.12.022, doi:10.1016/j.surfcoat.2004.12.022. This article has 53 citations and is from a domain leading peer-reviewed journal.

10. (tang2006lasersurfacealloyinga pages 4-5): C.H. Tang, F.T. Cheng, and H.C. Man. Laser surface alloying of a marine propeller bronze using aluminium powder: part ii: corrosion and erosion–corrosion synergism. Surface & Coatings Technology, 200:2594-2601, Jan 2006. URL: https://doi.org/10.1016/j.surfcoat.2004.12.022, doi:10.1016/j.surfcoat.2004.12.022. This article has 53 citations and is from a domain leading peer-reviewed journal.

11. (koeini2023surfacealloyingof pages 1-2): Fatemeh Koeini, Mahmoud Heydarzadeh Sohi, and Parham Pirayesh. Surface alloying of cupronickel alloy with aluminum using tungsten inert gas process. Archives of Metallurgy and Materials, pages 161-170, Jul 2023. URL: https://doi.org/10.24425/amm.2023.141490, doi:10.24425/amm.2023.141490. This article has 1 citations and is from a peer-reviewed journal.

12. (koeini2023surfacealloyingof pages 2-4): Fatemeh Koeini, Mahmoud Heydarzadeh Sohi, and Parham Pirayesh. Surface alloying of cupronickel alloy with aluminum using tungsten inert gas process. Archives of Metallurgy and Materials, pages 161-170, Jul 2023. URL: https://doi.org/10.24425/amm.2023.141490, doi:10.24425/amm.2023.141490. This article has 1 citations and is from a peer-reviewed journal.

13. (koeini2023surfacealloyingof pages 6-8): Fatemeh Koeini, Mahmoud Heydarzadeh Sohi, and Parham Pirayesh. Surface alloying of cupronickel alloy with aluminum using tungsten inert gas process. Archives of Metallurgy and Materials, pages 161-170, Jul 2023. URL: https://doi.org/10.24425/amm.2023.141490, doi:10.24425/amm.2023.141490. This article has 1 citations and is from a peer-reviewed journal.

14. (koeini2023surfacealloyingof pages 4-6): Fatemeh Koeini, Mahmoud Heydarzadeh Sohi, and Parham Pirayesh. Surface alloying of cupronickel alloy with aluminum using tungsten inert gas process. Archives of Metallurgy and Materials, pages 161-170, Jul 2023. URL: https://doi.org/10.24425/amm.2023.141490, doi:10.24425/amm.2023.141490. This article has 1 citations and is from a peer-reviewed journal.

15. (fayanas2025nickelaluminiumbronze pages 1-2): Aintzane Fayanas, Angela Veiga, Alejandro Perez, Amadeu Concustell, Silvia Molas, and Nerea Ordas. Nickel aluminium bronze alloys with enhanced erosion-corrosion resistance and mechanical strength. Journal of the Japan Society of Powder and Powder Metallurgy, 72:S819-S826, Mar 2025. URL: https://doi.org/10.2497/jjspm.15f-t13-08, doi:10.2497/jjspm.15f-t13-08. This article has 1 citations.

16. (fayanas2025nickelaluminiumbronze pages 2-5): Aintzane Fayanas, Angela Veiga, Alejandro Perez, Amadeu Concustell, Silvia Molas, and Nerea Ordas. Nickel aluminium bronze alloys with enhanced erosion-corrosion resistance and mechanical strength. Journal of the Japan Society of Powder and Powder Metallurgy, 72:S819-S826, Mar 2025. URL: https://doi.org/10.2497/jjspm.15f-t13-08, doi:10.2497/jjspm.15f-t13-08. This article has 1 citations.

17. (fayanas2025nickelaluminiumbronze pages 5-7): Aintzane Fayanas, Angela Veiga, Alejandro Perez, Amadeu Concustell, Silvia Molas, and Nerea Ordas. Nickel aluminium bronze alloys with enhanced erosion-corrosion resistance and mechanical strength. Journal of the Japan Society of Powder and Powder Metallurgy, 72:S819-S826, Mar 2025. URL: https://doi.org/10.2497/jjspm.15f-t13-08, doi:10.2497/jjspm.15f-t13-08. This article has 1 citations.

18. (fayanas2025nickelaluminiumbronze media d6642ebf): Aintzane Fayanas, Angela Veiga, Alejandro Perez, Amadeu Concustell, Silvia Molas, and Nerea Ordas. Nickel aluminium bronze alloys with enhanced erosion-corrosion resistance and mechanical strength. Journal of the Japan Society of Powder and Powder Metallurgy, 72:S819-S826, Mar 2025. URL: https://doi.org/10.2497/jjspm.15f-t13-08, doi:10.2497/jjspm.15f-t13-08. This article has 1 citations.

19. (zhao2022thelaserdeposited pages 7-10): Lu Zhao, Kailun Li, Jun Yao, Yixiang Yuan, and Baorui Du. The laser deposited nickel-aluminum bronze coatings on sus630 stainless steel and its corrosion resistance in 3.5 wt.% nacl solution. Metals, 12:781, Apr 2022. URL: https://doi.org/10.3390/met12050781, doi:10.3390/met12050781. This article has 8 citations.

20. (zhao2022thelaserdeposited pages 13-14): Lu Zhao, Kailun Li, Jun Yao, Yixiang Yuan, and Baorui Du. The laser deposited nickel-aluminum bronze coatings on sus630 stainless steel and its corrosion resistance in 3.5 wt.% nacl solution. Metals, 12:781, Apr 2022. URL: https://doi.org/10.3390/met12050781, doi:10.3390/met12050781. This article has 8 citations.

21. (zhao2022thelaserdeposited pages 10-13): Lu Zhao, Kailun Li, Jun Yao, Yixiang Yuan, and Baorui Du. The laser deposited nickel-aluminum bronze coatings on sus630 stainless steel and its corrosion resistance in 3.5 wt.% nacl solution. Metals, 12:781, Apr 2022. URL: https://doi.org/10.3390/met12050781, doi:10.3390/met12050781. This article has 8 citations.

22. (huo2025modulatingheatinput pages 4-5): Renjie Huo, Zheying Wang, Mingsheng Wang, Rui Wang, Song Zhang, Chunhua Zhang, Chenliang Wu, Haitao Chen, and Jiang Chen. Modulating heat input to optimize corrosion resistance of nickel–aluminum bronze manufactured by cold metal transfer additive manufacturing. Materials, 18:2205, May 2025. URL: https://doi.org/10.3390/ma18102205, doi:10.3390/ma18102205. This article has 5 citations.

23. (huo2025modulatingheatinput pages 5-7): Renjie Huo, Zheying Wang, Mingsheng Wang, Rui Wang, Song Zhang, Chunhua Zhang, Chenliang Wu, Haitao Chen, and Jiang Chen. Modulating heat input to optimize corrosion resistance of nickel–aluminum bronze manufactured by cold metal transfer additive manufacturing. Materials, 18:2205, May 2025. URL: https://doi.org/10.3390/ma18102205, doi:10.3390/ma18102205. This article has 5 citations.

24. (huo2025modulatingheatinput pages 7-10): Renjie Huo, Zheying Wang, Mingsheng Wang, Rui Wang, Song Zhang, Chunhua Zhang, Chenliang Wu, Haitao Chen, and Jiang Chen. Modulating heat input to optimize corrosion resistance of nickel–aluminum bronze manufactured by cold metal transfer additive manufacturing. Materials, 18:2205, May 2025. URL: https://doi.org/10.3390/ma18102205, doi:10.3390/ma18102205. This article has 5 citations.

25. (huo2025modulatingheatinput pages 10-13): Renjie Huo, Zheying Wang, Mingsheng Wang, Rui Wang, Song Zhang, Chunhua Zhang, Chenliang Wu, Haitao Chen, and Jiang Chen. Modulating heat input to optimize corrosion resistance of nickel–aluminum bronze manufactured by cold metal transfer additive manufacturing. Materials, 18:2205, May 2025. URL: https://doi.org/10.3390/ma18102205, doi:10.3390/ma18102205. This article has 5 citations.

26. (huo2025modulatingheatinput pages 13-15): Renjie Huo, Zheying Wang, Mingsheng Wang, Rui Wang, Song Zhang, Chunhua Zhang, Chenliang Wu, Haitao Chen, and Jiang Chen. Modulating heat input to optimize corrosion resistance of nickel–aluminum bronze manufactured by cold metal transfer additive manufacturing. Materials, 18:2205, May 2025. URL: https://doi.org/10.3390/ma18102205, doi:10.3390/ma18102205. This article has 5 citations.

27. (tan2024effectofalni pages 2-4): Yinxun Tan, Haofeng Xie, Xue Feng, Shuhui Huang, Wenjing Zhang, Lijun Peng, Wanyu Wang, and Yizhi Zhao. Effect of al/ni ratio on the microstructure and properties of nickel–aluminum bronze alloys. Materials, 17:1330, Mar 2024. URL: https://doi.org/10.3390/ma17061330, doi:10.3390/ma17061330. This article has 14 citations.

28. (tan2024effectofalni pages 4-6): Yinxun Tan, Haofeng Xie, Xue Feng, Shuhui Huang, Wenjing Zhang, Lijun Peng, Wanyu Wang, and Yizhi Zhao. Effect of al/ni ratio on the microstructure and properties of nickel–aluminum bronze alloys. Materials, 17:1330, Mar 2024. URL: https://doi.org/10.3390/ma17061330, doi:10.3390/ma17061330. This article has 14 citations.

29. (tan2024effectofalni pages 10-12): Yinxun Tan, Haofeng Xie, Xue Feng, Shuhui Huang, Wenjing Zhang, Lijun Peng, Wanyu Wang, and Yizhi Zhao. Effect of al/ni ratio on the microstructure and properties of nickel–aluminum bronze alloys. Materials, 17:1330, Mar 2024. URL: https://doi.org/10.3390/ma17061330, doi:10.3390/ma17061330. This article has 14 citations.

30. (tan2024effectofalni pages 12-16): Yinxun Tan, Haofeng Xie, Xue Feng, Shuhui Huang, Wenjing Zhang, Lijun Peng, Wanyu Wang, and Yizhi Zhao. Effect of al/ni ratio on the microstructure and properties of nickel–aluminum bronze alloys. Materials, 17:1330, Mar 2024. URL: https://doi.org/10.3390/ma17061330, doi:10.3390/ma17061330. This article has 14 citations.

31. (zhao2020effectofweld pages 1-4): Xu Zhao, Yuhong Qi, Jintao Wang, Tianxiang Peng, Zhanping Zhang, and Kejiao Li. Effect of weld and surface defects on the corrosion behavior of nickel aluminum bronze in 3.5% nacl solution. ArXiv, 10:1227, Sep 2020. URL: https://doi.org/10.3390/met10091227, doi:10.3390/met10091227. This article has 9 citations.

32. (zhao2020effectofweld pages 4-8): Xu Zhao, Yuhong Qi, Jintao Wang, Tianxiang Peng, Zhanping Zhang, and Kejiao Li. Effect of weld and surface defects on the corrosion behavior of nickel aluminum bronze in 3.5% nacl solution. ArXiv, 10:1227, Sep 2020. URL: https://doi.org/10.3390/met10091227, doi:10.3390/met10091227. This article has 9 citations.

33. (zhao2020effectofweld pages 11-14): Xu Zhao, Yuhong Qi, Jintao Wang, Tianxiang Peng, Zhanping Zhang, and Kejiao Li. Effect of weld and surface defects on the corrosion behavior of nickel aluminum bronze in 3.5% nacl solution. ArXiv, 10:1227, Sep 2020. URL: https://doi.org/10.3390/met10091227, doi:10.3390/met10091227. This article has 9 citations.

34. (cottam2012lasermaterialsprocessing pages 10-13): Ryan Cottam. Laser materials processing for improved corrosion performance. Environmental and Industrial Corrosion - Practical and Theoretical Aspects, Dec 2012. URL: https://doi.org/10.5772/52423, doi:10.5772/52423. This article has 8 citations.

35. (sparrow2025lpbfparameteroptimization pages 1-3): Andrew Sparrow, Walter Smith, and Troy Y. Ansell. Lpbf parameter optimization of mechanical, non-thermal generated c71500 powder. Metals, 16:10, Dec 2025. URL: https://doi.org/10.3390/met16010010, doi:10.3390/met16010010. This article has 1 citations.

36. (sparrow2025lpbfparameteroptimization pages 3-6): Andrew Sparrow, Walter Smith, and Troy Y. Ansell. Lpbf parameter optimization of mechanical, non-thermal generated c71500 powder. Metals, 16:10, Dec 2025. URL: https://doi.org/10.3390/met16010010, doi:10.3390/met16010010. This article has 1 citations.

37. (joress2022developmentofan pages 4-7): Howie Joress, Brian DeCost, Najlaa Hassan, Trevor M. Braun, Justin M. Gorham, and Jason Hattrick-Simpers. Development of an automated millifluidic platform and data-analysis pipeline for rapid electrochemical corrosion measurements: a ph study on zn-ni. SSRN Electronic Journal, Apr 2022. URL: https://doi.org/10.48550/arxiv.2204.06094, doi:10.48550/arxiv.2204.06094. This article has 19 citations.

38. (joress2022developmentofan pages 1-4): Howie Joress, Brian DeCost, Najlaa Hassan, Trevor M. Braun, Justin M. Gorham, and Jason Hattrick-Simpers. Development of an automated millifluidic platform and data-analysis pipeline for rapid electrochemical corrosion measurements: a ph study on zn-ni. SSRN Electronic Journal, Apr 2022. URL: https://doi.org/10.48550/arxiv.2204.06094, doi:10.48550/arxiv.2204.06094. This article has 19 citations.

39. (joress2022developmentofan pages 11-14): Howie Joress, Brian DeCost, Najlaa Hassan, Trevor M. Braun, Justin M. Gorham, and Jason Hattrick-Simpers. Development of an automated millifluidic platform and data-analysis pipeline for rapid electrochemical corrosion measurements: a ph study on zn-ni. SSRN Electronic Journal, Apr 2022. URL: https://doi.org/10.48550/arxiv.2204.06094, doi:10.48550/arxiv.2204.06094. This article has 19 citations.

40. (joress2022developmentofan pages 7-11): Howie Joress, Brian DeCost, Najlaa Hassan, Trevor M. Braun, Justin M. Gorham, and Jason Hattrick-Simpers. Development of an automated millifluidic platform and data-analysis pipeline for rapid electrochemical corrosion measurements: a ph study on zn-ni. SSRN Electronic Journal, Apr 2022. URL: https://doi.org/10.48550/arxiv.2204.06094, doi:10.48550/arxiv.2204.06094. This article has 19 citations.

41. (tang2006lasersurfacealloyinga pages 6-7): C.H. Tang, F.T. Cheng, and H.C. Man. Laser surface alloying of a marine propeller bronze using aluminium powder: part ii: corrosion and erosion–corrosion synergism. Surface & Coatings Technology, 200:2594-2601, Jan 2006. URL: https://doi.org/10.1016/j.surfcoat.2004.12.022, doi:10.1016/j.surfcoat.2004.12.022. This article has 53 citations and is from a domain leading peer-reviewed journal.
