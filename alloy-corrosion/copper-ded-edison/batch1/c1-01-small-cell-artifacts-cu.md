<!--
Edison Scientific LITERATURE_HIGH task (batch 1)
- Task ID: 3b467e17-0d18-4f39-bcc0-ea31409b87bd
- Submitted: 2026-10-18T01:19:44Z
- Fetched: 2026-10-18T01:53:30Z (status: success)
- Raw trajectory JSON: ../raw/c1-01-small-cell-artifacts-cu.json.gz
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

QUESTION: What goes wrong, physically and chemically, when Cu-Ni and NAB (or
copper and brasses, if nothing closer exists) are tested in a small-volume
cell (a 1-5 mm O-ring flat cell, droplet cell or capillary microcell holding
roughly 10-200 uL, open to air) instead of a conventional bulk cell (>100
mL)? Cover: (a) accumulation of dissolved copper (CuCl2-, Cu2+) in the small
volume and its redeposition on the specimen or on the Pt counter, and how it
shifts Ecorr, Rp and the cathodic current; (b) oxygen supply: the oxygen
reduction limiting current density in an unstirred well against a stirred
bulk cell, and whether a 30-60 min test depletes dissolved oxygen; (c)
evaporation and the resulting chloride rise over 1-2 h, and mitigations
(humidified lid, oil overlayer, gelled electrolyte); (d) pH change from the
counter electrode; (e) crevice attack under the gasket for copper alloys:
whether attack concentrates inside the crevice or just outside its mouth,
whether NAB shows selective phase attack under the O-ring, and which gasket
materials (FKM, PTFE, silicone) or cell designs minimize it; (f) published
measurements of how Ecorr, Rp or breakdown potentials of copper alloys change
with exposed area or electrolyte volume. Give the area and electrolyte
volume of each study, and say which artifacts are large enough to change the
ranking of alloys.

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

QUESTION: What goes wrong, physically and chemically, when Cu-Ni and NAB (or
copper and brasses, if nothing closer exists) are tested in a small-volume
cell (a 1-5 mm O-ring flat cell, droplet cell or capillary microcell holding
roughly 10-200 uL, open to air) instead of a conventional bulk cell (>100
mL)? Cover: (a) accumulation of dissolved copper (CuCl2-, Cu2+) in the small
volume and its redeposition on the specimen or on the Pt counter, and how it
shifts Ecorr, Rp and the cathodic current; (b) oxygen supply: the oxygen
reduction limiting current density in an unstirred well against a stirred
bulk cell, and whether a 30-60 min test depletes dissolved oxygen; (c)
evaporation and the resulting chloride rise over 1-2 h, and mitigations
(humidified lid, oil overlayer, gelled electrolyte); (d) pH change from the
counter electrode; (e) crevice attack under the gasket for copper alloys:
whether attack concentrates inside the crevice or just outside its mouth,
whether NAB shows selective phase attack under the O-ring, and which gasket
materials (FKM, PTFE, silicone) or cell designs minimize it; (f) published
measurements of how Ecorr, Rp or breakdown potentials of copper alloys change
with exposed area or electrolyte volume. Give the area and electrolyte
volume of each study, and say which artifacts are large enough to change the
ranking of alloys.

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


## Small-Volume Cell Artifacts for Copper Alloys: A Critical Assessment for the CubXL O-Ring Flat Cell

### Overview

The following assessment addresses what goes wrong—physically and chemically—when Cu–Ni (90-10, 70-30) and nickel-aluminum bronze (NAB) are tested in a small-volume O-ring flat cell (~150 µL, 0.07–0.13 cm², open to air) instead of a conventional bulk cell (>100 mL). The literature on small-area/small-volume electrochemistry is extensive for stainless steels and aluminum alloys but remarkably thin for copper alloys specifically. Many of the quantitative benchmarks below are therefore derived from pure copper, brass, or general microcell studies and extrapolated to the planned Cu–Ni/NAB system; where direct copper-alloy data in microliter cells do not exist, the gap is stated plainly.

| Part | Artifact | Mechanism and likely bias | Quantitative benchmark | Key reference(s) | Tags |
|---|---|---|---|---|---|
| (a) | Dissolved-Cu accumulation | High area/volume ratio and restricted transport retain Cu(I)-chloride complexes, Cu(II), Ni, Fe, Al, and Mn. Hydrolysis or precipitation changes pH and films; cathodic reduction of soluble Cu adds current, shifts mixed potential, and can distort Rp. | Concentration control becomes important below about 1 cm³. No Cu–Ni/NAB study directly measured the resulting Ecorr or Rp shift in a 10–200 µL cell. | Lohrengel, *Electrochimica Acta* 42 (1997) 3265–3271, DOI: 10.1016/S0013-4686(97)00177-1 (lohrengel1997interfaceandvolume pages 4-5); Lai et al., *Analytical Chemistry* 95 (2023) 15833–15850, DOI: 10.1021/acs.analchem.3c02423 (lai2023perspectivesoncorrosion pages 10-12, lai2023perspectivesoncorrosion pages 12-16) | [CITE] [CUBXL] [GAP] |
| (a) | Cu redeposition on specimen or Pt counter | During cathodic/reverse polarization, accumulated Cu ions can plate on the specimen. During anodic working-electrode polarization, the Pt counter is cathodic and can acquire Cu. Plated Cu changes cathodic kinetics and may contaminate later wells. | Pt visibly acquires Cu from 0.1–100 mM Cu²⁺ solutions; diffusion-limited deposition current rises with concentration. No seawater microliter-cell carryover measurement was found. | Gudić and Krišto, *Kemija u industriji* (2023), DOI: 10.15255/KUI.2022.061; Izquierdo et al., *Electrochimica Acta* 247 (2017) 588–599, DOI: 10.1016/j.electacta.2017.07.042 | [CITE] [NUMBERS] [CUBXL] [GAP] |
| (b) | Oxygen mass-transfer limitation | An unstirred 3–4 mm well develops a growing diffusion layer, whereas stirring renews oxygen. Cathodic current, Ecorr, and apparent Rp therefore depend on fill height, free-surface area, and elapsed time as well as alloy behavior. | A 0.113 cm² rotating Cu disk in aerated seawater gave oxygen-reduction limiting currents of about −0.32 to −2.38 mA cm⁻² with increasing rotation; these stirred values are not valid targets for an unstirred well. | Kear, Albarran, and Walsh, “Reduction of dissolved oxygen at a copper rotating disc electrode” (2005) (kear2005reductionofdissolved pages 5-6); Benzbiria et al., *SN Applied Sciences* 2 (2020), DOI: 10.1007/s42452-020-03957-8 (benzbiria2020oxygenreductionreaction pages 6-7) | [CITE] [NUMBERS] [CUBXL] |
| (b) | Finite dissolved-O₂ inventory | Air-saturated water contains roughly 0.25 mM O₂. A 150 µL well initially holds about 37.5 nmol O₂, equivalent to about 14.5 mC for four-electron reduction. Air replenishes an open well, but the metal interface can remain depleted. | The initial inventory lasts about 24 min at 10 µA or 48 min at 5 µA without replenishment. Thus, 30–60 min is sufficient for substantial depletion. Direct O₂-versus-time data for a 150 µL Cu–Ni/NAB well were not found. | Schindelholz et al., *Electrochimica Acta* 276 (2018) 194–206, DOI: 10.1016/j.electacta.2018.04.184 (schindelholz2018electrochemicalaspectsof pages 12-16) | [NUMBERS] [CUBXL] [GAP] |
| (c) | Evaporation and chloride increase | Water loss raises chloride concentration and changes fill height, oxygen path length, resistance, and wetted area. Airflow, temperature, humidity, and geometry control the rate, so no universal 1–2 h loss applies. | From 150 µL, losses of 15, 30, or 50 µL raise chloride by about 11%, 25%, or 50%. Saline SECCM droplets can crystallize; oil-SECCM supports 3.5 wt% NaCl tests for more than 20 h. | Lai et al., DOI: 10.1021/acs.analchem.3c02423 (lai2023perspectivesoncorrosion pages 12-16, lai2023perspectivesoncorrosion pages 10-12); Hong et al., *Journal of Electrochemical Science and Technology* 17 (2026) 304–320, DOI: 10.33961/jecst.2026.00010 (hong2026themeniscusin pages 9-12) | [CITE] [NUMBERS] [CUBXL] |
| (c) | Mitigation changes transport | A humidified lid is least intrusive. An oil layer suppresses evaporation and spreading but also restricts atmospheric O₂ transfer and changes wetting. Gelled electrolyte suppresses convection and evaporation but changes conductivity and diffusion, so it constitutes a different environment. | Oil-covered droplets can persist for months, but corrosion may decline as oil and products restrict oxygen. Oil-SECCM demonstrates stability, not equivalence to an open bulk cell. | Liang, *Corrosion Behavior of Pipeline Steel Transporting Diluted Bitumen* (2020), DOI: 10.14288/1.0389639 (liang2020corrosionbehaviorof pages 105-110); Lai et al. (lai2023perspectivesoncorrosion pages 12-16) | [CITE] [CUBXL] |
| (d) | Counter-electrode pH drift | With an anodic working electrode, cathodic Pt generates OH⁻; with a cathodic working electrode, anodic Pt can generate H⁺, O₂, or chlorine species. In 150 µL, small charge produces appreciable acid/base equivalents unless the electrolyte is strongly buffered. | One mC equals 10.4 nmol monovalent equivalents, or 0.069 mM in 150 µL; 100 mC gives 6.9 mM. Separately, a 1 µL NaCl droplet on Cu exceeded pH 9 within 7 min and was estimated to approach pH 10 in about 1 min. | Schindelholz et al., DOI: 10.1016/j.electacta.2018.04.184 (schindelholz2018electrochemicalaspectsof pages 12-16, schindelholz2018electrochemicalaspectsof pages 9-12, schindelholz2018electrochemicalaspectsof pages 16-20) | [CITE] [NUMBERS] [CUBXL] |
| (e) | Reverse crevice corrosion at gasket mouth | Copper and Cu alloys can show reverse crevice corrosion: attack occurs on the exposed surface just outside or near the mouth while the deeper crevice remains relatively protected. An attack ring should not automatically be interpreted as alloy pitting. | For 70Cu–30Ni, mild visible attack developed near the crevice mouth after two months in seawater. Deoxygenation suppressed reverse crevice corrosion. | Lu, *Experimental Study of Reverse Crevice Corrosion of Copper* (2005) (lu2005experimentalstudyof pages 18-22, lu2005experimentalstudyofa pages 18-22, lu2005experimentalstudyof pages 1-6, lu2005experimentalstudyof pages 35-39) | [CITE] [NAVY] [CUBXL] |
| (e) | NAB selective phase attack under O-ring | Oxygen and ion gradients can galvanically couple α matrix, retained β/β′, κ phases, and phase boundaries. Under-ring attack can therefore mimic a DED microstructure or repair-zone effect. | NAB literature establishes phase-selective corrosion, but no study was found that mapped attack beneath a 3–4 mm FKM O-ring in 10–200 µL seawater. | Jafari et al., *Corrosion and Materials Degradation* 2 (2021) 61–77, DOI: 10.3390/cmd2010004; microcrevice evidence (li2015electrochemicalcharacterizationof pages 39-43, yule2019highresolutionelectrochemical pages 105-109) | [CITE] [NAVY] [CUBXL] [GAP] |
| (e) | Gasket material and clamping | FKM seals reliably but creates a compressed polymer–metal crevice. Silicone is compliant and hydrophobic, but seal quality, leakage, damage, and extractables vary. PTFE is chemically clean but stiff and needs controlled loading or a compliant backing. Material alone cannot eliminate the crevice. | MAP-E used Viton, 1 cm² area, and 25 mL electrolyte; that bulk geometry does not establish FKM as artifact-free at 150 µL. Gasketed microcells report inconsistent sealing and crevice artifacts. | Persaud et al., *npj Materials Degradation* 10 (2026), DOI: 10.1038/s41529-026-00822-8 (persaud2026materialsaccelerationplatform pages 9-12); Suter and Böhni, DOI: 10.3323/jcorr1991.50.349 (suter2001localelectrochemicalmethods pages 7-9); gasket evidence (yule2019highresolutionelectrochemical pages 105-109, li2015electrochemicalcharacterizationof pages 34-39) | [CITE] [NUMBERS] [CUBXL] |
| (f) | Exposed-area dependence | Smaller areas contain fewer rare active sites and may sample different phase fractions. Breakdown potentials can become more positive and more variable as area decreases. Nominal-area normalization does not correct this sampling bias. | Microcell literature reports tip-size dependence of pitting potential and uncertainty in true wetted area, but no quantitative Cu–Ni/NAB Ecorr, Rp, or breakdown-potential series versus area was found. | Microcell evidence (li2015electrochemicalcharacterizationof pages 39-43, li2015electrochemicalcharacterizationof pages 34-39); Saxena et al., *ACS Measurement Science Au* 5 (2025) 178–188, DOI: 10.1021/acsmeasuresciau.4c00042 | [CITE] [CUBXL] [GAP] |
| (f) | Electrolyte-volume dependence | At fixed area, volume simultaneously changes Cu buildup, O₂ inventory, buffer capacity, counter-electrode contamination, and fractional evaporation. A volume-dependent shift cannot be assigned to one mechanism without solution analysis and controls. | No matched Cu–Ni, NAB, copper, or brass study was found reporting Ecorr, Rp, or breakdown potential at multiple volumes spanning roughly 10 µL to more than 100 mL. | Lohrengel, DOI: 10.1016/S0013-4686(97)00177-1 (lohrengel1997interfaceandvolume pages 4-5); Lai et al., DOI: 10.1021/acs.analchem.3c02423 (lai2023perspectivesoncorrosion pages 10-12, lai2023perspectivesoncorrosion pages 12-16) | [CITE] [CUBXL] [GAP] |
| Ranking risk | Artifacts most likely to reverse alloy ranking | Highest risks are oxygen-transfer differences, Cu-ion accumulation/redeposition, gasket-mouth or selective-phase attack, and evaporation-driven chloride change. Counter-electrode pH drift is potentially severe during polarization. Uncertain area mainly increases scatter and may bias heterogeneous DED specimens. | MAP-E’s bulk-cell validation achieved Ecorr −119 ± 21 mV and Epit 392 ± 75 mV versus Ag/AgCl in aerated 3.56 wt% NaCl for 304 stainless steel, but used 1 cm² and 25 mL—not a microliter copper-alloy geometry. | Persaud et al., DOI: 10.1038/s41529-026-00822-8 (persaud2026materialsaccelerationplatform pages 9-12, persaud2026materialsaccelerationplatform pages 4-6, persaud2026materialsaccelerationplatform pages 6-9) | [NUMBERS] [CUBXL] [GAP] |


*Table: Evidence matrix for artifacts expected when Cu–Ni and nickel-aluminum bronze are tested in microliter O-ring, droplet, or capillary cells rather than bulk cells. It identifies quantitative bounds, ranking risks, directly relevant literature, and unresolved copper-alloy gaps.*

---

### (a) Accumulation of Dissolved Copper and Redeposition

In a bulk cell (>100 mL), dissolved Cu(I) chloride complexes (CuCl₂⁻) and Cu²⁺ are diluted into a large reservoir. In a 150 µL well with 0.1 cm² exposed area, the surface-to-volume ratio is roughly 1000× larger than in a 1 L beaker with a 1 cm² coupon. Lohrengel (1997) established that concentration control becomes necessary for electrolyte volumes below about 1 cm³ because charge transfer at the working interface can substantially alter ionic concentrations in the limited electrolyte (lohrengel1997interfaceandvolume pages 4-5). In SECCM and capillary microcells, corrosion products accumulate near the specimen, may hydrolyze and precipitate as hydroxides blocking capillaries or changing local chemistry, and can deposit back on the surface or inside the probe (li2015electrochemicalcharacterizationof pages 39-43, yule2019highresolutionelectrochemical pages 86-93). For copper alloys dissolving at even modest rates (e.g., 1–10 µA cm⁻²), tens of minutes of open-circuit exposure could raise Cu concentration by micromolar to tens-of-micromolar levels in 150 µL, enough to add a cathodic Cu²⁺/Cu⁰ reduction wave that would shift Ecorr positive and reduce apparent Rp.

**Redeposition on Pt counter:** During anodic polarization of the specimen, the Pt counter electrode is cathodic and will plate any dissolved Cu from solution. Cu-contaminated Pt changes the counter's electrochemistry in subsequent wells unless cleaned. During cathodic or reverse sweeps on the specimen, Cu redeposition on the working electrode itself can occur, changing surface composition and confounding post-test ICP-OES/ICP-MS analysis (yule2019highresolutionelectrochemical pages 86-93).

**Quantitative gap:** No study was found that measured Ecorr, Rp, or cathodic current shifts caused by Cu-ion accumulation in a 10–200 µL cell for Cu–Ni or NAB. This is a clear **[GAP]**.

[CITE] Lohrengel, M.M. *Electrochimica Acta* 42 (1997) 3265–3271. DOI: 10.1016/S0013-4686(97)00177-1.
[CITE] Lai, Z. et al. *Analytical Chemistry* 95 (2023) 15833–15850. DOI: 10.1021/acs.analchem.3c02423.

**[CUBXL]** After each measurement, pipette the electrolyte out completely and rinse the Pt counter wire with dilute acid between wells to remove Cu deposits. Consider a disposable or sacrificial counter (graphite rod segment) to avoid cross-contamination.

---

### (b) Oxygen Supply and Depletion

**Diffusion-limited current density:** Kear et al. (2005) measured oxygen-reduction limiting current densities of approximately −0.32 to −2.38 mA cm⁻² on a rotating copper disk electrode in aerated seawater at 25 °C, spanning a range of rotation rates (kear2005reductionofdissolved pages 5-6). These stirred values are not applicable to an unstirred well. In a quiescent 150 µL well approximately 3 mm deep and 4 mm diameter, the natural-convection/diffusion boundary layer will grow with time. A rough estimate for the unstirred O₂-reduction limiting current density on copper in aerated NaCl is on the order of 10–50 µA cm⁻², depending on elapsed time and geometry, substantially below the stirred RDE values.

**Finite O₂ inventory:** Air-saturated seawater at 25 °C contains approximately 0.25 mM dissolved O₂. A 150 µL well therefore holds about 37.5 nmol O₂, equivalent to roughly 14.5 mC for four-electron reduction. At a corrosion current of 5–10 µA (i.e., 50–100 µA cm⁻² on 0.1 cm²), the initial dissolved O₂ inventory would be consumed in roughly 24–48 minutes without atmospheric resupply. Although the open-air surface allows re-aeration, the metal–electrolyte interface at the bottom of the well can remain significantly oxygen-depleted, particularly if corrosion products or the O-ring wall impede convective mixing. This means a 30-minute OCP followed by polarization may begin under partially depleted conditions, depressing cathodic currents and shifting Ecorr negative relative to a stirred bulk cell (schindelholz2018electrochemicalaspectsof pages 12-16).

**[NUMBERS]** Kear et al.: O₂-reduction limiting current on Cu RDE in seawater ≈ −0.32 to −2.38 mA cm⁻² (stirred). Calculated quiescent well O₂ inventory lifetime ≈ 24–48 min at 5–10 µA.

**[CUBXL]** Consider bubbling or gentle aspiration to partially refresh the well, or accept that the test ranks alloys under quiescent, partially depleted conditions and state this explicitly. A shorter OCP (10–15 min instead of 30 min) would reduce depletion before polarization.

---

### (c) Evaporation and Chloride Rise

In SECCM and microdroplet corrosion measurements, evaporation is consistently identified as a major limitation: it changes droplet geometry, raises electrolyte concentration, can crystallize NaCl and even break glass pipettes, and limits test duration (lai2023perspectivesoncorrosion pages 12-16). Hong et al. (2026) describe how evaporation of volatile solvents produces greater current variability and irregular droplet footprints (hong2026themeniscusin pages 9-12). For a 150 µL open well at 22 °C and ~40–50% RH, rough estimates suggest water loss on the order of 1–5 µL/h (depending on airflow), which would raise chloride concentration by roughly 1–3% per hour—modest over one hour, but potentially 5–15% over a two-hour cyclic-polarization test.

**Mitigations:**
- **Oil-SECCM / mineral oil overlay:** Lai et al. (2023) report that Oil-SECCM enables corrosion tests in standard 3.5 wt% NaCl lasting more than 20 hours by covering the sample with a thin mineral-oil layer that suppresses evaporation and confines the droplet (lai2023perspectivesoncorrosion pages 12-16, lai2023perspectivesoncorrosion pages 10-12). However, oil also restricts atmospheric O₂ transfer, changing oxygen supply to the well—which for Cu–Ni/NAB is already a concern.
- **Paraffin oil on droplets:** Liang (2020) demonstrated that oil-covered NaCl droplets on steel can persist for months, but corrosion rates decline as oil and products restrict oxygen diffusion (liang2020corrosionbehaviorof pages 105-110).
- **Humidified lid:** Least intrusive option; a local humidity chamber or snap-on lid with a small vent maintains >90% RH around the wells without changing O₂ access or electrolyte chemistry.
- **Gelled electrolyte:** Suppresses convection and evaporation but changes conductivity, diffusion coefficients, and possibly Cu complexation, constituting a different test environment.

**[CUBXL]** For 1-hour tests, a humidified snap-on lid is the simplest and least-artifact-prone mitigation. Oil overlays are effective against evaporation but would further restrict oxygen in a system already at risk of O₂ depletion. Weigh the well before and after to quantify loss.

---

### (d) pH Change from the Counter Electrode

In a bulk cell, counter-electrode products (OH⁻ from cathodic O₂ reduction or H⁺/Cl₂ from anodic water/chloride oxidation) are diluted into >100 mL. In 150 µL, one millicoulomb of charge produces approximately 10.4 nmol of monovalent acid or base equivalents, i.e., about 0.069 mM concentration change. A cyclic polarization scan passing 10–100 mC total charge would produce 0.7–6.9 mM OH⁻ or H⁺ in the well. Unbuffered 3.5% NaCl (pH ~6.5–7) has negligible buffer capacity, so even a few mM of OH⁻ can raise pH above 9.

Independently, Schindelholz et al. (2018) showed that on copper, cathodic oxygen reduction in a 1 µL NaCl droplet raised the bulk pH above 9 within 7 minutes and estimated the average pH could reach ~10 within approximately 1 minute at a corrosion current of ~1 µA cm⁻² (schindelholz2018electrochemicalaspectsof pages 12-16, schindelholz2018electrochemicalaspectsof pages 9-12, schindelholz2018electrochemicalaspectsof pages 16-20). While the CubXL well is 150× larger than 1 µL, the area-to-volume ratio is still high enough that counter-electrode-driven pH drift is a real concern, especially during anodic polarization sweeps where the Pt counter drives cathodic reactions (O₂ reduction → OH⁻) in the shared small electrolyte volume.

**[NUMBERS]** Schindelholz et al.: 1 µL, 4 m NaCl on Cu → pH >9 in 7 min, estimated pH ~10 in ~1 min. In 150 µL, 100 mC anodic charge → ~6.9 mM OH⁻.

**[CUBXL]** Use a Luggin capillary or salt bridge to isolate the counter electrode in a separate small reservoir, or at minimum use a counter electrode positioned at the top of the well (maximizing the diffusion path from counter products to the specimen surface). Adding a small amount of borate buffer would stabilize pH but changes the electrolyte from "simulated seawater."

---

### (e) Crevice Attack Under the Gasket

**Reverse crevice corrosion of copper:** This is perhaps the most consequential artifact for the planned cell design. Lu (2005) demonstrated that copper and copper alloys exhibit *reverse* crevice corrosion (RCC): unlike stainless steels and many other metals where attack concentrates inside the crevice, copper alloys corrode preferentially on the exposed (bold) surface just outside or near the crevice mouth, while the occluded crevice interior remains relatively protected (lu2005experimentalstudyof pages 18-22, lu2005experimentalstudyof pages 31-35, lu2005experimentalstudyof pages 1-6). For 70Cu–30Ni in ambient-temperature seawater, mild visible attack developed near the crevice mouth on the bold surface after two months (lu2005experimentalstudyof pages 18-22). The proposed mechanism involves a metal-ion concentration cell: dissolved Cu accumulates inside the restricted crevice, making the interior noble relative to the exterior, reversing the usual oxygen-concentration-cell polarity (lu2005experimentalstudyof pages 35-39). Deoxygenation suppressed RCC, and elevated temperature produced uniform corrosion instead (lu2005experimentalstudyof pages 1-6).

**Implications for O-ring cells:** In a 3–4 mm ID O-ring well, the gasket-to-metal contact creates a crevice at the perimeter of the exposed area. RCC means the ring of attack will appear *just inside* the O-ring opening on the exposed metal, not under the gasket. This attack ring could be mistaken for pitting or for an alloy-specific corrosion feature of the DED microstructure if it coincides with a fusion zone or HAZ boundary.

**NAB selective phase attack:** NAB (C95800) is well known for selective corrosion of the retained β phase, lamellar eutectoid, and κ phases in seawater (Jafari et al. 2021). Under an O-ring, oxygen and chloride gradients could galvanically couple different phases and preferentially attack the most susceptible microstructural constituents (e.g., κ_III in the α+κ_III eutectoid) at the crevice boundary. **No study was found that mapped NAB selective phase attack specifically beneath a 3–4 mm FKM O-ring in a microliter cell.** This is a clear **[GAP]** and a significant **[NOVELTY-RISK]**: the planned work on DED NAB repair coupons with fusion zones under small O-rings may produce crevice-influenced phase-selective attack that is not representative of open-surface behavior.

**Gasket materials:**
- **FKM (Viton):** Widely used (persaud2026materialsaccelerationplatform pages 9-12). Chemically resistant, but stiffer than silicone; requires controlled compression to avoid over-squeeze (which narrows the crevice gap and intensifies crevice chemistry) or under-squeeze (which leaks).
- **Silicone:** More compliant and hydrophobic, which Suter and Böhni (2001) noted can minimize crevice corrosion in capillary microcells (suter2001localelectrochemicalmethods pages 7-9, li2015electrochemicalcharacterizationof pages 34-39). However, silicone can fail under hydraulic pressure, is mechanically fragile, and may leach silicone oils that contaminate the surface.
- **PTFE:** Chemically the cleanest, but very stiff; without a compliant backing or precisely machined seat, it produces poor seals and high contact-stress variability.

**[CUBXL]** Photograph each spot *before and after* with attention to the gasket contact ring. Run a set of "blank" tests on wrought C71500 and cast C95800 reference coupons at multiple O-ring compression levels to characterize the RCC artifact. Consider a knife-edge or lacquer-masked exposed area (no gasket contact) as a periodic control.

---

### (f) Published Area and Volume Dependence of Cu-Alloy Electrochemical Parameters

**This is the weakest part of the available literature.** No systematic study was found reporting Ecorr, Rp, or breakdown potentials of Cu–Ni, NAB, copper, or brass as a function of exposed area spanning from ~0.01 cm² to ~1 cm², or as a function of electrolyte volume spanning from ~10 µL to >100 mL.

From microcell studies on other alloys (primarily Al alloys and stainless steels), it is well established that:
- Smaller areas contain fewer rare microstructural weak sites, so measured pitting or breakdown potentials tend to be more positive and more variable as area decreases (li2015electrochemicalcharacterizationof pages 39-43, li2015electrochemicalcharacterizationof pages 34-39).
- Capillary tip size changes the sampled population of active sites and can shift measured pitting potentials (li2015electrochemicalcharacterizationof pages 39-43).
- Wetted area in SECCM can differ substantially from the pipette aperture area, introducing systematic error in current-density normalization (Saxena et al. 2025, DOI: 10.1021/acsmeasuresciau.4c00042).

For the CubXL's 0.07–0.13 cm² area, the sampling issue is relevant for NAB, which has large (10–50 µm) κ phases and eutectoid colonies: a single 3 mm diameter spot may or may not include a representative population of κ_III lamellae or retained β, producing site-to-site variability that is microstructural rather than instrumental.

**MAP-E benchmark (304 stainless steel, not copper):** Persaud et al. (2026) reported Ecorr = −119 ± 21 mV and Epit = 392 ± 75 mV vs. Ag/AgCl (1 M KCl) for 304 SS in aerated 3.56 wt% NaCl using 1 cm² Viton-sealed flat cells with 25 mL electrolyte (persaud2026materialsaccelerationplatform pages 9-12, persaud2026materialsaccelerationplatform pages 4-6, persaud2026materialsaccelerationplatform pages 6-9). Individual cell standard deviations were below 40 mV. This validates the flat-cell approach at bulk scale but does not establish artifact-free performance at the CubXL's much smaller area and 150 µL volume.

**[GAP]** A controlled study measuring Cu–Ni or NAB Ecorr and Rp at several areas (e.g., 0.03, 0.1, 0.3, 1.0 cm²) and volumes (e.g., 50 µL, 500 µL, 5 mL, 50 mL) in the same electrolyte is needed to calibrate the CubXL against conventional data and to determine whether the small-cell artifacts are large enough to reverse alloy rankings.

---

### Top 5 Changes to the Small-Cell Plan for Copper Alloys

**1. Add an evaporation-control lid and weigh each well.** A snap-on humidified lid (>90% RH) over the O-ring array minimizes chloride rise without restricting O₂ access. Weigh the clamp assembly before and after each test to quantify and correct for water loss. An oil overlay suppresses evaporation effectively but restricts oxygen, compounding artifact (b). *Rationale:* Evaporation-driven chloride rise of 5–15% over a 2 h cyclic polarization test could shift Ecorr by tens of mV and change pitting behavior of Cu–Ni alloys.

**2. Rinse or replace the Pt counter wire between alloys and photograph the gasket contact ring.** Dissolved Cu will plate onto Pt during anodic specimen polarization; this contamination can carry over to the next well. A brief dip in dilute HNO₃ or electrochemical stripping between wells prevents cross-contamination. Photograph each spot before *and* after testing to distinguish reverse crevice corrosion (RCC attack ring at the gasket mouth) from true pitting or selective-phase attack in the DED microstructure. *Rationale:* RCC is the expected crevice mode for copper alloys—attack outside, not inside—and the O-ring contact ring could be confused with a microstructure-specific feature.

**3. Shorten OCP to 10–15 min and consider gentle electrolyte refresh.** The 150 µL O₂ inventory lasts roughly 25–50 min at typical Cu–Ni corrosion currents. A 30-minute OCP may substantially deplete dissolved O₂ before polarization begins, depressing cathodic currents and shifting Ecorr negative relative to a stirred bulk cell. A shorter OCP or a gentle mid-test electrolyte refresh (pipette out and refill) would maintain more representative O₂ levels. *Rationale:* Oxygen supply controls the cathodic reaction on Cu–Ni and NAB; O₂ depletion is the single largest source of systematic bias in the small cell.

**4. Run area/volume calibration experiments on wrought C71500 and cast C95800 reference coupons.** Before testing DED specimens, measure Ecorr, Rp, and cyclic polarization on the wrought and cast references at 2–3 O-ring sizes (e.g., 2 mm, 3 mm, 4 mm ID) and compare with conventional bulk-cell data (1 cm², 200 mL). This calibration quantifies the combined small-cell artifact and determines whether it is large enough to reverse alloy rankings. *Rationale:* No published Cu–Ni/NAB area-volume dependence data exist; the calibration is essential before interpreting DED results.

**5. Isolate or position the counter electrode to minimize pH drift.** In 150 µL of unbuffered 3.5% NaCl, counter-electrode reactions can shift pH by several units during a polarization sweep. Position the Pt wire at the top of the well (maximizing the diffusion path from counter products to the specimen), or route it through a small salt bridge or capillary. If the electrolyte is changed from plain NaCl to ASTM D1141 substitute ocean water, the natural buffering (borate, carbonate) will help, but the user should verify this does not change Cu–Ni rankings relative to natural seawater. *Rationale:* Schindelholz et al. (2018) showed pH >9 within 7 minutes in a 1 µL NaCl drop on copper; the 150 µL well is larger but still vulnerable during polarization scans passing tens of millicoulombs.

---

### Key References Cited

1. Lohrengel, M.M. "Interface and volume effects in biological cells and electrochemical microcells." *Electrochimica Acta* 42 (1997) 3265–3271. DOI: 10.1016/S0013-4686(97)00177-1. [CITE] [NUMBERS]

2. Lai, Z. et al. "Perspectives on Corrosion Studies Using Scanning Electrochemical Cell Microscopy: Challenges and Opportunities." *Analytical Chemistry* 95 (2023) 15833–15850. DOI: 10.1021/acs.analchem.3c02423. [CITE] [NUMBERS] [CUBXL]

3. Schindelholz, E.J. et al. "Electrochemical aspects of copper atmospheric corrosion in the presence of sodium chloride." *Electrochimica Acta* 276 (2018) 194–206. DOI: 10.1016/j.electacta.2018.04.184. [CITE] [NUMBERS]

4. Lu, L. "Experimental study of reverse crevice corrosion of copper." Thesis (2005). [CITE] [NAVY] [CUBXL]

5. Kear, G., Albarran, C.P.L., and Walsh, F.C. "Reduction of dissolved oxygen at a copper rotating disc electrode." (2005). [CITE] [NUMBERS]

6. Suter, T. and Böhni, H. "Local Electrochemical Methods to Study Corrosion Processes on a Molecular Level." *Zairyo-to-kankyo* 50 (2001) 349–363. DOI: 10.3323/jcorr1991.50.349. [CITE]

7. Persaud, D. et al. "Materials Acceleration Platform for Electrochemistry." *npj Materials Degradation* 10 (2026). DOI: 10.1038/s41529-026-00822-8. [CITE] [NUMBERS] [NOVELTY-RISK]

8. Hong, M. et al. "The Meniscus in SECCM: Formation, Stability, and Its Impact on Quantitative Electrochemistry." *J. Electrochem. Sci. Technol.* 17 (2026) 304–320. DOI: 10.33961/jecst.2026.00010. [CITE]

9. Jafari, H.R. et al. "Effect of Fluid Flow on the Corrosion Performance of as-Cast and Heat-Treated Nickel Aluminum Bronze Alloy (UNS C95800) in Saline Solution." *Corrosion and Materials Degradation* 2 (2021) 61–77. DOI: 10.3390/cmd2010004. [CITE] [NAVY]

10. Liang, H. "Corrosion behavior of pipeline steel transporting diluted bitumen." (2020). DOI: 10.14288/1.0389639. [CITE]

11. Saxena, N. et al. "In Situ Quantification of a Wetted Surface Area during Scanning Electrochemical Cell Microscopy Using Retraction Curves." *ACS Measurement Science Au* 5 (2025) 178–188. DOI: 10.1021/acsmeasuresciau.4c00042. [CITE]

### Summary of Gaps

The most significant finding of this review is that **no published study has systematically measured how Ecorr, Rp, or breakdown potentials of Cu–Ni or NAB change with exposed area or electrolyte volume in the range relevant to the CubXL (0.07–0.13 cm², 150 µL)**. The small-cell artifact literature is dominated by stainless steels and aluminum alloys. For copper alloys, the unique reverse crevice corrosion behavior, the sensitivity of cathodic kinetics to oxygen supply, the risk of dissolved-Cu accumulation and redeposition, and the rapid pH rise in small volumes are all well-established phenomena individually, but their combined effect in a microliter O-ring flat cell has not been quantified. The planned calibration experiments on wrought C71500 and cast C95800 reference coupons are therefore not optional—they are prerequisite to interpreting DED specimen data.

References

1. (lohrengel1997interfaceandvolume pages 4-5): M.M. Lohrengel. Interface and volume effects in biological cells and electrochemical microcells. Electrochimica Acta, 42:3265-3271, Jan 1997. URL: https://doi.org/10.1016/s0013-4686(97)00177-1, doi:10.1016/s0013-4686(97)00177-1. This article has 85 citations and is from a domain leading peer-reviewed journal.

2. (lai2023perspectivesoncorrosion pages 10-12): Zhaogui Lai, Min Liu, Peng Bi, Feifei Huang, and Ying Jin. Perspectives on corrosion studies using scanning electrochemical cell microscopy: challenges and opportunities. Analytical chemistry, 95:15833-15850, Oct 2023. URL: https://doi.org/10.1021/acs.analchem.3c02423, doi:10.1021/acs.analchem.3c02423. This article has 26 citations and is from a highest quality peer-reviewed journal.

3. (lai2023perspectivesoncorrosion pages 12-16): Zhaogui Lai, Min Liu, Peng Bi, Feifei Huang, and Ying Jin. Perspectives on corrosion studies using scanning electrochemical cell microscopy: challenges and opportunities. Analytical chemistry, 95:15833-15850, Oct 2023. URL: https://doi.org/10.1021/acs.analchem.3c02423, doi:10.1021/acs.analchem.3c02423. This article has 26 citations and is from a highest quality peer-reviewed journal.

4. (kear2005reductionofdissolved pages 5-6): G Kear, CPL Albarran, and FC Walsh. Reduction of dissolved oxygen at a copper rotating disc electrode. Unknown journal, 2005.

5. (benzbiria2020oxygenreductionreaction pages 6-7): Nisrine Benzbiria, Mustapha Zertoubi, and Mohammed Azzi. Oxygen reduction reaction kinetics on pure copper in neutral sodium sulfate solution. SN Applied Sciences, Nov 2020. URL: https://doi.org/10.1007/s42452-020-03957-8, doi:10.1007/s42452-020-03957-8. This article has 24 citations.

6. (schindelholz2018electrochemicalaspectsof pages 12-16): E.J. Schindelholz, H. Cong, C.F. Jove-Colon, S. Li, J.A. Ohlhausen, and H.K. Moffat. Electrochemical aspects of copper atmospheric corrosion in the presence of sodium chloride. Electrochimica Acta, 276:194-206, Jun 2018. URL: https://doi.org/10.1016/j.electacta.2018.04.184, doi:10.1016/j.electacta.2018.04.184. This article has 94 citations and is from a domain leading peer-reviewed journal.

7. (hong2026themeniscusin pages 9-12): Mini Hong, Ju-eon Park, and Ara Jo. The meniscus in seccm: formation, stability, and its impact on quantitative electrochemistry. Journal of Electrochemical Science and Technology, 17:304-320, Aug 2026. URL: https://doi.org/10.33961/jecst.2026.00010, doi:10.33961/jecst.2026.00010. This article has 2 citations and is from a peer-reviewed journal.

8. (liang2020corrosionbehaviorof pages 105-110): Hongxing Liang. Corrosion behavior of pipeline steel transporting diluted bitumen. ArXiv, Jan 2020. URL: https://doi.org/10.14288/1.0389639, doi:10.14288/1.0389639. This article has 1 citations.

9. (schindelholz2018electrochemicalaspectsof pages 9-12): E.J. Schindelholz, H. Cong, C.F. Jove-Colon, S. Li, J.A. Ohlhausen, and H.K. Moffat. Electrochemical aspects of copper atmospheric corrosion in the presence of sodium chloride. Electrochimica Acta, 276:194-206, Jun 2018. URL: https://doi.org/10.1016/j.electacta.2018.04.184, doi:10.1016/j.electacta.2018.04.184. This article has 94 citations and is from a domain leading peer-reviewed journal.

10. (schindelholz2018electrochemicalaspectsof pages 16-20): E.J. Schindelholz, H. Cong, C.F. Jove-Colon, S. Li, J.A. Ohlhausen, and H.K. Moffat. Electrochemical aspects of copper atmospheric corrosion in the presence of sodium chloride. Electrochimica Acta, 276:194-206, Jun 2018. URL: https://doi.org/10.1016/j.electacta.2018.04.184, doi:10.1016/j.electacta.2018.04.184. This article has 94 citations and is from a domain leading peer-reviewed journal.

11. (lu2005experimentalstudyof pages 18-22): L Lu. Experimental study of reverse crevice corrosion of copper. Unknown journal, 2005.

12. (lu2005experimentalstudyofa pages 18-22): L Lu. Experimental study of reverse crevice corrosion of copper. Unknown journal, 2005.

13. (lu2005experimentalstudyof pages 1-6): L Lu. Experimental study of reverse crevice corrosion of copper. Unknown journal, 2005.

14. (lu2005experimentalstudyof pages 35-39): L Lu. Experimental study of reverse crevice corrosion of copper. Unknown journal, 2005.

15. (li2015electrochemicalcharacterizationof pages 39-43): J Li. Electrochemical characterization of intermetallic compounds in aa2024-t3 and localized corrosion morphology of al-cu-mg at elevated temperature. Unknown journal, 2015.

16. (yule2019highresolutionelectrochemical pages 105-109): LC Yule. High resolution electrochemical measurements for corrosion. Unknown journal, 2019.

17. (persaud2026materialsaccelerationplatform pages 9-12): Daniel Persaud, Mike Werezak, Mark Xu, Melyne Zhou, Frank Benkel, Xin Pang, Vahid Attari, Brian DeCost, Ashley S. Dale, Nicholas Senior, Gabriel Birsan, and Jason Hattrick-Simpers. Materials acceleration platform for electrochemistry: a platform for autonomous electrochemistry. npj Materials Degradation, Jun 2026. URL: https://doi.org/10.1038/s41529-026-00822-8, doi:10.1038/s41529-026-00822-8. This article has 0 citations and is from a peer-reviewed journal.

18. (suter2001localelectrochemicalmethods pages 7-9): T. Suter and H. B^|^ouml;hni. Local electrochemical methods to study corrosion processes on a molecular level. Zairyo-to-kankyo, 50:349-363, Aug 2001. URL: https://doi.org/10.3323/jcorr1991.50.349, doi:10.3323/jcorr1991.50.349. This article has 2 citations.

19. (li2015electrochemicalcharacterizationof pages 34-39): J Li. Electrochemical characterization of intermetallic compounds in aa2024-t3 and localized corrosion morphology of al-cu-mg at elevated temperature. Unknown journal, 2015.

20. (persaud2026materialsaccelerationplatform pages 4-6): Daniel Persaud, Mike Werezak, Mark Xu, Melyne Zhou, Frank Benkel, Xin Pang, Vahid Attari, Brian DeCost, Ashley S. Dale, Nicholas Senior, Gabriel Birsan, and Jason Hattrick-Simpers. Materials acceleration platform for electrochemistry: a platform for autonomous electrochemistry. npj Materials Degradation, Jun 2026. URL: https://doi.org/10.1038/s41529-026-00822-8, doi:10.1038/s41529-026-00822-8. This article has 0 citations and is from a peer-reviewed journal.

21. (persaud2026materialsaccelerationplatform pages 6-9): Daniel Persaud, Mike Werezak, Mark Xu, Melyne Zhou, Frank Benkel, Xin Pang, Vahid Attari, Brian DeCost, Ashley S. Dale, Nicholas Senior, Gabriel Birsan, and Jason Hattrick-Simpers. Materials acceleration platform for electrochemistry: a platform for autonomous electrochemistry. npj Materials Degradation, Jun 2026. URL: https://doi.org/10.1038/s41529-026-00822-8, doi:10.1038/s41529-026-00822-8. This article has 0 citations and is from a peer-reviewed journal.

22. (yule2019highresolutionelectrochemical pages 86-93): LC Yule. High resolution electrochemical measurements for corrosion. Unknown journal, 2019.

23. (lu2005experimentalstudyof pages 31-35): L Lu. Experimental study of reverse crevice corrosion of copper. Unknown journal, 2005.
