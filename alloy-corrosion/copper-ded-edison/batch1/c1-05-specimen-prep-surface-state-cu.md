<!--
Edison Scientific LITERATURE task (batch 1)
- Task ID: a5b11125-a660-4aac-8d39-7d801a6578c3
- Submitted: 2026-10-18T01:20:03Z
- Fetched: 2026-10-18T01:53:33Z (status: success)
- Raw trajectory JSON: ../raw/c1-05-specimen-prep-surface-state-cu.json.gz
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

QUESTION: How does surface preparation change the short-term electrochemistry
and early film formation of Cu-Ni and NAB in seawater, and how should a
robot-tested specimen of an additively manufactured copper alloy be prepared?
Cover the final polish (SiC grit vs 1 um diamond vs colloidal silica or
alumina), the deformed surface layer and smearing of kappa phases in NAB,
cleaning (ethanol, ultrasonic, water rinse), and the time and humidity
between polishing and immersion (air-formed Cu2O). Cover AM-specific issues:
as-deposited rough surfaces with adhered powder vs machined vs polished
faces; build-plane orientation (top vs side, XY vs XZ) in DED, WAAM or LPBF
copper alloys; and porosity: how pores intersecting a small spot act as
crevices, how pore fraction correlates with corrosion of printed copper
alloys, and how to detect or exclude pore-affected spots (imaging before the
test, X-ray CT). Include mounting effects (crevice at the resin interface,
conductive mounts). Give numbers where available, such as Ecorr or Rp shifts
with finish and density thresholds.

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

QUESTION: How does surface preparation change the short-term electrochemistry
and early film formation of Cu-Ni and NAB in seawater, and how should a
robot-tested specimen of an additively manufactured copper alloy be prepared?
Cover the final polish (SiC grit vs 1 um diamond vs colloidal silica or
alumina), the deformed surface layer and smearing of kappa phases in NAB,
cleaning (ethanol, ultrasonic, water rinse), and the time and humidity
between polishing and immersion (air-formed Cu2O). Cover AM-specific issues:
as-deposited rough surfaces with adhered powder vs machined vs polished
faces; build-plane orientation (top vs side, XY vs XZ) in DED, WAAM or LPBF
copper alloys; and porosity: how pores intersecting a small spot act as
crevices, how pore fraction correlates with corrosion of printed copper
alloys, and how to detect or exclude pore-affected spots (imaging before the
test, X-ray CT). Include mounting effects (crevice at the resin interface,
conductive mounts). Give numbers where available, such as Ecorr or Rp shifts
with finish and density thresholds.

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


# Surface preparation for small-area tests of naval copper alloys

**Bottom line.** A reproducible copper-alloy test needs a defined *surface state*, not merely a nominal alloy and an O-ring diameter. Finishing changes deformation, exposed phases, roughness and the initial oxide; immersion then changes the film on a timescale longer than the proposed 30-minute open-circuit hold. Published comparisons provide useful benchmarks, but I found **no defensible numerical shift in corrosion potential or polarization resistance attributable specifically to changing C71500 or C95800 from SiC to 1 µm diamond to colloidal silica/alumina under otherwise identical seawater conditions**. The proposed finish comparison is therefore an experiment, not a settled ranking. Published Cu–Ni and NAB studies also do not establish an allowable polish-to-immersion delay or relative-humidity tolerance. (song2024microstructuresandcorrosion pages 2-5, song2024microstructuresandcorrosion pages 10-13, abreu2024influenceofdeep pages 4-5, metikoshukovic2011corrosionresistanceof pages 1-2)

## Directly relevant studies and operating benchmarks

In the items below, **bulk-cell volume “unreported” means it should not be assumed equivalent to a 150 µL well**. Potentials must retain their stated reference; *EIS film resistance* is not automatically linear-polarization resistance, and a reported polarization-derived current is not element-resolved dissolution.

1. **[CITE] [NUMBERS] [CUBXL] [GAP]** M. Metikoš-Huković, R. Babić, I. Škugor Rončević and Z. Grubač, “Corrosion resistance of copper–nickel alloy under fluid jet impingement,” *Desalination* **276** (2011) 228–232. **DOI: 10.1016/j.desal.2011.03.056.** Materials: laboratory-prepared, rolled and annealed binary Cu–Ni containing **10, 20, 30 or 40 atomic % Ni**, **not** Fe/Mn-bearing naval C70600/C71500 and **not** 10–40 wt% Ni. Discs were abraded and finished with **0.05 µm alumina**, ultrasonically degreased in ethanol, rinsed with distilled water and nitrogen-dried. A Teflon-mounted **0.78 cm²** disc was tested in a pumped bulk/impinging-jet three-electrode cell (**volume unreported**), 3.5% NaCl at pH 7.9, after **1–3 h** immersion; potentials refer to **Ag/AgCl, 3 M KCl**. At 3 h, reported EIS-derived **polarization resistance** for bare Cu–10Ni/Cu–20Ni/Cu–30Ni/Cu–40Ni was **6.0/8.0/8.3/8.0 kΩ cm²** in stagnant solution but **1.3/0.9/0.7/0.5 kΩ cm²** at 2.7 m s⁻¹ jet velocity. *Robot implication:* specify mixing and pipette-jet history, position the head reproducibly, and do not equate an open, nominally stagnant microwell with a flowing condenser. This paper compares flow and Ni content, **not polishing finishes**. (metikoshukovic2011corrosionresistanceof pages 1-2, metikoshukovic2011corrosionresistanceof pages 2-3, metikoshukovic2011corrosionresistanceof pages 3-5)

2. **[CITE] [NUMBERS] [CUBXL] [NOVELTY-RISK]** J. Song, X. A. Jimenez, A. C. To and Y. Fu, “Microstructures and Corrosion Properties of Wire Arc Additive Manufactured Copper–Nickel Alloys,” *Materials* **17** (2024) 876. **DOI: 10.3390/ma17040876.** Material: **WAAM**, single alloy wire nominally 70/30 Cu–Ni, compared with conventional/wrought plate. Wire, wt%: **Cu 67.5, Ni 30, Mn 0.7, Fe 0.55, Ti 0.25, Si 0.1**; plate: **Cu 68.046, Ni 30.46, Mn 0.73, Fe 0.56**, plus reported minor Pb/Zn/P. The wire/plate chemistry difference is a comparison caveat. EDM-cut **XY** and **YZ** cross-sections were epoxy-mounted, exposed over **0.32 cm²**, finished at **P2400 SiC**, and immersed **3 h at OCP** in naturally aerated 3.5 wt% NaCl before EIS or cyclic polarization; bulk three-electrode cell with graphite counter and aqueous **Ag/AgCl** reference; **volume unreported**. EIS-fit **film resistance**, wrought XY/YZ: **1.08/1.18 × 10⁵ Ω**; WAAM sample 6 XY/YZ: **1.40/1.66 × 10⁵ Ω**, or about **34/52 kΩ cm²** versus **35/38 kΩ cm²** after multiplication by the reported 0.32 cm² exposed area. These are **Rfilm, not Rp**. The authors find generally higher film resistance and breakdown potential and lower passive current on **YZ than XY**; sample 6 was best overall. Breakdown was *defined* at **5 × 10⁻⁵ A cm⁻²**; polarization reversed at **3 mA cm⁻²**. EDS found up to **20% difference in local Ni concentration**, with preferential attack of Ni-depleted interdendritic material; EIS-derived oxide thicknesses were model estimates, **0.021–0.20 µm**, not directly measured cross-sections. Optical examination reported **no visible porosity**, not a numerical density or a CT-negative result. *Robot implication:* record the actual XY/top and vertical side plane, build height, track position and finish; deliberately compare planes on identically finished material. **Overlap:** marine Cu–30Ni AM-versus-conventional electrochemistry and orientation have already been published; the planned **blown-powder DED, 150 µL mapped wells and element-resolved dissolution** remain different questions. One concluding passage inconsistently labels a 5.25 mm-track example as 800 mm min⁻¹; the paper’s fabrication table specifies **sample 2 = 500 mm min⁻¹**, and **sample 6 = 1000 mm min⁻¹/3.85 mm**. (song2024microstructuresandcorrosion pages 13-14, song2024microstructuresandcorrosion pages 2-5, song2024microstructuresandcorrosion pages 10-13)

3. **[CITE] [NUMBERS] [NAVY] [CUBXL]** C. M. Abreu, I. Feijoo, G. Pena and M. C. Pérez, “Influence of Deep Cryogenic Treatment on the Mechanical Properties and Corrosion Resistance of Nickel–Aluminum Bronze,” *Corrosion and Materials Degradation* **5** (2024) 624–640. **DOI: 10.3390/cmd5040030.** Material: **cast C95800**, wt% **Al 8.96, Ni 4.93, Fe 5.09, Mn 1.24, Si 0.09, Zn 0.53, Cu balance**, examined after cryogenic and/or annealing treatments; it is **not an experiment varying polish**. Metallographic specimens received **2400-grit SiC → 1 µm diamond → 0.04 µm colloidal silica**. Bulk three-electrode measurements used **0.28 cm²**, Pt mesh, **SCE**, 3.5% NaCl adjusted to **pH 7.9**, **cell volume unreported**: **60 min OCP**, separate freshly prepared specimens followed by EIS over **1–72 h**. Cryogenically treated-only material stabilized near **−0.28 V versus SCE**; combining annealing and cryotreatment changed early OCP and produced more protective time-dependent impedance, particularly when **annealing followed cryotreatment**. The paper’s prose prints positive **0.25/0.23 V** for the combined-treatment OCP, while its plotted OCPs lie in the **negative** potential range; those signed values should **not** be reused as quantitative benchmarks without checking original data. Its method and figure captions also disagree about the cyclic-voltammetry starting potential; that very wide cathodic-to-anodic sweep is not a suitable unchanged CubXL pitting program. *Robot implication:* put the 1 µm/colloidal-silica sequence into a controlled finishing arm and track OCP and oxide development over more than one initial hold; do not treat two heat-treatment states as proof of a polish effect. (abreu2024influenceofdeep pages 2-4, abreu2024influenceofdeep pages 4-5, abreu2024influenceofdeep pages 10-12, abreu2024influenceofdeep pages 8-10)

4. **[CITE] [NUMBERS] [NAVY] [CUBXL]** Y. Lv, B. Zhao, H. Zhang, C. Su, B. Nie, R. Wang, L. Cao and F. Lyu, “Improving Corrosion Resistance Properties of Nickel-Aluminum Bronze (NAB) Alloys via Shot Peening Treatment,” *Materials Transactions* **60** (2019) 1629–1637. **DOI: 10.2320/matertrans.M2019031.** Material: **cast**, then shot-peened NAB; reported wt% **Al 9.5, Fe 4.0, Ni 4.2, Mn 1.2, Cu balance**. **No post-peening polish**: deformation and roughness therefore change together. Bulk glass three-electrode cell, **1 cm²** wax-defined face, Pt counter, **calomel reference**; electrolyte **3.5% NaCl**, volume unreported; first OCP/polarization at **15 min**, EIS at **15 min, 2, 5 and 10 days**, microscopy after **20 days**. Roughness **Ra** increased from **0.009 µm** as-cast to **0.177, 0.218, 0.348 µm** at peening intensities 0.15, 0.20, 0.25 mmA. Table 3 reports early **Ecorr −0.283, −0.312, −0.315, −0.340 V** in that order and fit current entries **14.316, 9.355, 8.632, 7.759** in the paper’s unusual heading **“10⁻⁶ mA mm⁻²”**; do **not** silently relabel these as validated µA cm⁻² or dissolution rates. The prose’s **−3.40 V** is inconsistent with its table’s **−0.340 V**. At 10 days the moderately peened surface’s impedance loop was reported approximately **twice** the cast one; after 20 days cast material showed approximately **40–60 µm-wide pits**, especially near α/κIII, whereas the most aggressive peening introduced cracks/chipping. *Robot implication:* coarse grinding or machining damage and a mirror polish cannot be pooled; log finish/topography and inspect NAB phase edges. Peening changes the actual subsurface microstructure, so these values do **not** quantify a SiC-versus-diamond shift. (lv2019improvingcorrosionresistance pages 2-4, lv2019improvingcorrosionresistance pages 4-5, lv2019improvingcorrosionresistance pages 5-8, lv2019improvingcorrosionresistance media 88fb0691)

5. **[CITE] [NUMBERS] [NAVY] [CUBXL]** Q. N. Song, Y. G. Zheng, S. L. Jiang, D. R. Ni and Z. Y. Ma, “Comparison of Corrosion and Cavitation Erosion Behaviors Between the As-Cast and Friction-Stir-Processed Nickel Aluminum Bronze,” *Corrosion* **69** (2013) 1111–1121. **DOI: 10.5006/0984.** Material: **cast UNS C95800** then **solid-state friction-stir-processed**, wt% **Al 9.18, Ni 4.49, Fe 4.06, Mn 1.03, Cu balance**; neither laser clad nor AM. Immersion electrodes were epoxy-mounted with rear Cu-wire contact, **0.49 cm²**, finished to **1000-grit SiC**, in bulk 3.5% NaCl (**volume unreported**), with **SCE**, followed by EIS over days; the **1 µm diamond** finish was used on a *different set for cavitation morphology*, not as a controlled electrochemical alternative. Cavitation specimens were ultrasonically cleaned in **ethanol**, air-dried; solution was refreshed weekly for immersion work. After **10 days**, FSP’s EIS capacitive-loop diameter was about **one order of magnitude** above cast NAB, although the authors report little early electrochemical separation. *Robot implication:* do not infer long-term protective-film performance from a 30-minute comparison, or attribute their FSP effect to diamond polish. The paper notes previous **U.S. Naval Surface Warfare Center** use of FSP on NAB propellers; it does not establish that this particular study was DoD-funded. (song2013comparisonofcorrosion pages 1-4, song2013comparisonofcorrosion pages 4-8, song2013comparisonofcorrosion pages 8-12)

6. **[CITE] [NUMBERS] [NAVY] [CUBXL]** I. Cobo Ocejo, M. V. Biezma Moraleda and P. Linhardt, “Corrosion Behavior of Heat-Treated Nickel-Aluminum Bronze and Manganese-Aluminum Bronze in Natural Waters,” *Metals* **12** (2022) 380. **DOI: 10.3390/met12030380.** Materials: **cast** NAB, wt% **Cu 79.80, Al 9.31, Fe 4.92, Ni 4.57, Mn 1.23**, and **cast** Mn-Al bronze, foundry wt% **Cu 71.90, Mn 12.50, Al 7.03, Fe 3.82, Ni 2.21**; as-cast versus quenched and quenched/tempered. For **metallography** they used **320-grit SiC → 9 and 3 µm diamond → 0.05 µm alumina** and phenolic embedding; do not assume that this is an independently tested electrochemical finish. Potentiostatic testing used a **6 L bulk vessel** and **SCE**, four simultaneously clamped electrodes, simulated seawater prepared to **DIN 50905-4** or simulated freshwater, **72 h**. At **−200/−150/−100 mV versus SCE**, as-cast NAB’s final seawater currents were **0.92/2.06/82.10 µA cm⁻²**; quenched NAB gave **0.06/1.51/185**, and quenched/tempered **1.72/2.36/200**. This is a particularly strong warning that a seemingly small imposed potential shift and different β-phase state can transform the outcome; **these are imposed-potential currents, not Ecorr, icorr or measured dissolution**. *Robot implication:* map repair HAZ and fusion zone separately, use an electrode-referenced potential window, and avoid claiming every sharp current increase is a pit. (ocejo2022corrosionbehaviorof pages 1-3, ocejo2022corrosionbehaviorof pages 8-10, ocejo2022corrosionbehaviorof pages 3-5)

7. **[CITE] [NUMBERS] [NAVY] [CUBXL] [GAP]** C. Berlanga-Labari, A. Claver, M. V. Biezma-Moraleda and J. Fernández-Palacio, “The Effect of Kappa Phases on Tribocorrosion Behaviour of Nickel Aluminum Bronze (NAB) and Manganese Aluminum Bronze (MAB),” *Lubricants* **13** (2025) 290. **DOI: 10.3390/lubricants13070290.** Materials: **cast** NAB nominal **Cu–10Al–5Fe–5Ni**, Mn approximately **1.2 wt%**, and MAB nominal **Cu–10Al–12Mn–5Fe**, Ni approximately **2.1 wt%**; 320-grit SiC → 9/3 µm diamond → **0.05 µm alumina**, with etching for metallography. Pin-on-disc **bulk electrochemical cell**, **1 M NaCl**, Pt counter, **Ag/AgCl** reference, **3,600 s** sliding at 10 or 40 N; **area and volume unreported**, and **not a stationary O-ring cell**. Approximate OCPs are **−250 mV** NAB and **−500 mV** MAB versus Ag/AgCl; published solution ICP-AES after sliding (mg L⁻¹; NAB then MAB) **Cu 29.66/1.19, Ni 0.72/0.25, Al 3.24/1.71, Fe 1.36/13.18, Mn 0.57/6.98**. *Robot implication:* collect and report **Cu, Ni, Al, Fe and Mn separately**, with solution blanks and recovery; these sliding-induced concentrations are **not** predicted yields from 150 µL stationary wells. This paper establishes element-resolved solution analysis in bronze tribocorrosion, **not** novelty of a robotic mapped O-ring/DED test. (berlangalabari2025theeffectof pages 4-7, berlangalabari2025theeffectof pages 7-11, berlangalabari2025theeffectof pages 2-4)

8. **[CITE] [NUMBERS] [NAVY] [CUBXL] [NOVELTY-RISK]** D. Ding, Z. Pan, S. van Duin, H. Li and C. Shen, “Fabricating Superior NiAl Bronze Components through Wire Arc Additive Manufacturing,” *Materials* **9** (2016) 652. **DOI: 10.3390/ma9080652.** Material: **WAAM NAB wire deposited onto cast NAB**, cast substrate wt% **Al 8.8, Ni 5.2, Fe 4.4, Mn 1.1, Cu balance**, with commercial feed wire **Al 8.5–9.5, Ni 4–5.5, Fe 3–5, Mn 0.6–3.5, Cu balance**. Its microscopy found approximately **200 µm** interlayer reheated bands and **<1 mm** cast-substrate HAZ. **No corrosion cell, electrolyte volume, exposure duration, Ecorr, Rp or corrosion rate were measured**: it is microstructure/mechanics, not a corrosion ranking. It reports visibly fully dense WAAM walls, **not a CT-derived percent-density threshold**. The work acknowledges **Australian Defence Materials Technology Centre/DFCTC** support. *Robot implication:* 3–4 mm wells cannot resolve a **<1 mm HAZ** in isolation; use a narrower, validated microcell or explicitly label mixed-zone wells and register each footprint to metallography. **Overlap:** naval NAB additive deposition onto cast NAB exists; short-term mapped corrosion/dissolution across the repair interface is the proposed distinction. (ding2016fabricatingsuperiornial pages 9-12, ding2016fabricatingsuperiornial pages 3-6)

9. **[CITE] [NUMBERS] [NAVY] [CUBXL] [GAP]** C. Arcos, C. Guerra, J. A. Ramos-Grez and M. Sancy, “Ni-Al Bronze in Molten Carbonate Manufactured by LPBF: Effect of Porosity Design on Mechanical Properties and Oxidation,” *Materials* **16** (2023) 3893. **DOI: 10.3390/ma16103893.** Material: **LPBF pre-alloyed Cu–11Al–5Ni–4Fe wt%** powder, nominally bulk or deliberately porous gyroid architecture; ground **#400–#4000**, then colloidal silica. **No aqueous electrochemical cell, potential reference or electrolyte volume**: the specimens underwent gravimetric exposure in aerated molten **Li₂CO₃–K₂CO₃ at 550 °C for 21 days**. Reported apparent porosity: bulk **3.5 ± 1.7%**, gyroid-with-wall **81.4 ± 12%**, gyroid **84.9 ± 11%**; as-built bulk surface pores were **2–5 µm**. The authors describe a slight corrosion-rate increase with designed porosity in that molten salt. *Robot implication:* inspect the polished face for newly opened pores and unmelted particles, but **do not extrapolate the gyroid corrosion result or posit a 96.5%-density seawater threshold**. (arcos2023nialbronzein pages 2-4, arcos2023nialbronzein pages 4-6, arcos2023nialbronzein pages 6-8)

10. **[CITE] [NUMBERS] [CUBXL] [GAP] — mechanistic analogue, NOT COPPER.** M. Laleh, A. E. Hughes, S. Yang, J. Li, W. Xu, I. Gibson and M. Y. Tan, “Two and three-dimensional characterisation of localised corrosion affected by lack-of-fusion pores in 316L stainless steel produced by selective laser melting,” *Corrosion Science* **165** (2020) 108394. **DOI: 10.1016/j.corsci.2019.108394.** Material: **LPBF 316L stainless steel, not a copper alloy**; Cu/Ni/Al/Fe/Mn naval-alloy composition **not applicable**. Epoxy-mounted, polished 4000-grit SiC electrochemical specimens were compared in a **bulk cell of unreported volume**, **0.6 M NaCl, 24 ± 2 °C, 1 h OCP**, **Ag/AgCl**, versus a Ti-mesh counter. Separately, **6 wt% FeCl₃ for one week** enabled before/after **X-ray CT**, effective pixel **2.95 µm**. Regions bearing irregular, surface-connected *lack-of-fusion* pores broke down earlier than locally dense regions; specimens **>99.1% density** gave the highest breakdown potentials in *this steel dataset*, whereas specimens below that value included much poorer performers. CT demonstrated corrosion entering surface-connected defects and advancing into underlying pores. *Robot implication:* use bright-field/reflected-light or confocal pre-imaging to reject a visible pore within or near a well footprint, and CT representative coupons to flag connected subsurface porosity. **99.1% is not a validated NAB, Cu–Ni or DED acceptance threshold**; local connectivity and pore shape matter more than an unqualified global density number. (laleh2020twoandthreedimensional pages 1-6, laleh2020twoandthreedimensional pages 6-10, laleh2020twoandthreedimensional pages 10-14, laleh2020twoandthreedimensional pages 14-17, laleh2020twoandthreedimensional pages 17-21)

## Specimen preparation and unresolved questions

**Define two distinct surfaces.** For a *microstructure-comparable* DED-versus-cast/wrought arm, section **well inside sound deposit** or through a mapped repair interface, machine flat without overheating, progressively grind with fresh SiC media, and finish all comparison coupons identically—for example **1 µm diamond followed by 0.04–0.05 µm colloidal silica or alumina**. Include a separately labeled, replicated **P2400/2000 SiC-only arm** and optionally a **1 µm-diamond-only arm**; never change finish and alloy class simultaneously. Colloidal silica and alumina are documented preparation endpoints, **not proven electrochemical equivalents**. Acquire unetched pre-test optical/BSE images and profilometry; use *separate etched sister sections* for α/β/κ phase attribution rather than immersing a chemically etched test surface. The harder, compositionally distinct κ particles and soft Cu-rich matrix make a ground/deformed or mechanically smeared top layer a plausible confounder; confirm its removal and check for particle pull-out/phase-edge relief by microscopy rather than assigning an unsupported deformation-layer thickness. For single tracks or thin walls, section or fixture to provide a flat footprint and sufficient material beneath the seal; a well spanning the track edge is a different, mixed-zone experiment. (ocejo2022corrosionbehaviorof pages 5-8, abreu2024influenceofdeep pages 4-5, berlangalabari2025theeffectof pages 2-4, song2024microstructuresandcorrosion pages 2-5, lv2019improvingcorrosionresistance pages 2-4)

Run a **separate service-surface arm** for genuinely as-deposited DED crowns or sides with adhered powder, oxides and waviness; distinguish **as-deposited**, **machined**, and **metallographically polished** in the database. Do not force an O-ring over a crown that cannot seal: surface texture and partially attached powder can change wetted area and leave occluded pockets, so a nominal 0.07–0.13 cm² will not represent the true electroactive area. Never infer an as-deposited-versus-polished Cu–Ni/NAB Ecorr difference from the cited WAAM XY/YZ study: **both its tested planes were ground to P2400 and the exterior was deliberately avoided**. Label atomizer splats/skulls separately from dense DED feedstock and obtain a continuous, conductive, sufficiently broad face before applying the same quantitative area normalization. (song2024microstructuresandcorrosion pages 2-5, lv2019improvingcorrosionresistance pages 2-4, arcos2023nialbronzein pages 2-4, arcos2023nialbronzein pages 4-6)

**Clean and time the surface.** After the assigned polish, remove abrasives and organics using a documented sequence such as short, controlled ethanol ultrasonic cleaning followed by a fresh ultrapure-water rinse and clean nitrogen drying; inspect for retained silica/alumina and for detached κ particles. Published Cu–Ni work used ethanol ultrasonication, distilled-water rinse and nitrogen drying, but did **not** establish optimal sonication time, a universal compatibility of abrasive residues or benefit of an ethanol film left in seawater. Record polishing end, end of rinse/dry, immersion start, storage **temperature and RH**, and order of well filling; use a short fixed fresh-surface delay and deliberate randomized air-aging arms, rather than uncontrolled overnight storage. Air exposure plausibly grows a native Cu-rich oxide/hydroxide and adsorbates that affect first-minute OCP/film nucleation, but **a quantified humidity-dependent Cu₂O growth law or resulting Ecorr/Rp shift for these naval alloys was not established by the retrieved experiments**. Separately measure any deliberately preformed surface oxide, e.g. using XPS/Raman on sister specimens. (song2013comparisonofcorrosion pages 4-8, metikoshukovic2011corrosionresistanceof pages 1-2, lu2024effectsofmedium pages 2-4, nemani2024advancementsinadditive pages 50-53, abreu2024influenceofdeep pages 8-10)

**Isolate the well, not just the back contact.** A pore mouth, powder–substrate junction, resin–metal gap, or O-ring pressed over a groove can create an occluded local electrolyte whose chemistry and active area differ from the freely aerated 150 µL above it. Polish the metal/resin interface flush if embedding is essential, place the O-ring **fully on metal away from the resin boundary**, keep exposed conductive mounting media outside the wetted footprint, and test leak-tightness with a sacrificial blank. Make the rear electrical connection without exposing a dissimilar metal or conductive adhesive to electrolyte. For repair maps, a seal bridging **deposit/fusion line/HAZ/substrate** is explicitly a mixed-material well, not an independent phase-specific result. The pore/CT evidence above establishes this concern directly in LPBF steel; its *quantitative* occurrence in blown-powder DED Cu–Ni/NAB small cells remains a **[GAP]**. (song2013comparisonofcorrosion pages 4-8, ding2016fabricatingsuperiornial pages 3-6, laleh2020twoandthreedimensional pages 6-10, laleh2020twoandthreedimensional pages 10-14, laleh2020twoandthreedimensional pages 17-21)

**Limits of available evidence.** I did not find a validated copper-alloy **pore-fraction–seawater-corrosion regression, pore-free density cutoff, controlled SiC/diamond/silica/alumina ranking, quantified as-built-versus-machined DED copper corrosion contrast, controlled humidity/air-aging series, or CT-registered 3–4 mm O-ring Cu–Ni/NAB pore study** in the primary evidence examined. The accessible WAAM 70/30 paper provides an *XY-versus-YZ*, not a generic *XY-versus-XZ*, comparison; WAAM, LPBF, arc repair, FSP, laser cladding and blown-powder laser DED must not be silently combined. None of the quantitative bulk-cell results above predicts Cu/Ni/Al/Fe/Mn dissolution **per 150 µL** or a valid fixed cyclic-polarization reversal potential for the planned wells. (song2024microstructuresandcorrosion pages 2-5, song2024microstructuresandcorrosion pages 10-13, arcos2023nialbronzein pages 2-4, metikoshukovic2011corrosionresistanceof pages 3-5, laleh2020twoandthreedimensional pages 1-6)

## Ranked Top 5 changes to the small-cell plan for copper alloys

1. **Make finish and exposure history experimental variables.** Standardize a SiC → 1 µm diamond → verified fine-oxide-polish baseline; include controlled SiC-only and diamond-only comparisons, solvent/rinse blanks, timed polish-to-immersion intervals and recorded RH. Do not invent a preferred finish from studies that did not compare finishes. (abreu2024influenceofdeep pages 4-5, song2024microstructuresandcorrosion pages 2-5, metikoshukovic2011corrosionresistanceof pages 1-2)
2. **Pre-register and screen every wetted footprint.** Photograph/profilometer before sealing; reject O-ring overlap with resin, visible pores, adhered powder, scratches or a nonflat face in the *intrinsic-material* arm; CT representative deposits for connected pores, and keep a separately labeled *pore-affected* arm. Report actual density and surface-pore prevalence without imposing the **steel-only 99.1%** cutoff on copper. (laleh2020twoandthreedimensional pages 10-14, laleh2020twoandthreedimensional pages 14-17, laleh2020twoandthreedimensional pages 17-21)
3. **Separate geometry, build orientation and repair zone.** Test polished DED **top/XY and side/vertical** surfaces at comparable height, track center/boundary and as-deposited/machined/finished states as distinct strata. Map deposit, fusion zone, **<1 mm NAB HAZ** and parent plate with microscopy; shrink/validate the cell if an isolated HAZ result is required. (song2024microstructuresandcorrosion pages 13-14, song2024microstructuresandcorrosion pages 2-5, ding2016fabricatingsuperiornial pages 3-6)
4. **Add time-resolved, minimally perturbing film measurements.** Retain OCP traces beyond 30 min on dedicated wells and compare 30 min, 3 h, 24–72 h and longer preconditioned specimens; use raw LPR slopes or EIS with explicitly distinguished **Rp/Rfilm**, then do destructive polarization on separate spots. Log oxygenation, temperature, water formulation, head agitation and evaporative loss. Do not calculate Cu–Ni corrosion rate from an assumed Stern–Geary constant. (ocejo2022corrosionbehaviorof pages 8-10, abreu2024influenceofdeep pages 4-5, song2024microstructuresandcorrosion pages 13-14, metikoshukovic2011corrosionresistanceof pages 3-5)
5. **Treat the tiny electrolyte as an analytical sample.** Randomize wells, run solution/electrode/fixture blanks and volume-recovery controls, distinguish dissolved from particulate-bound metal by a predefined filtration/acidification workflow, and analyze **Cu, Ni, Fe, Mn and—in bronzes—Al**, normalized both to measured exposure area and recovered liquid volume. Include a naturally aerated reference seawater condition alongside simple NaCl, with independently documented water source and chemistry; do not interpret polarization-derived currents or sliding-test ICP concentrations as the well’s measured dissolution. (berlangalabari2025theeffectof pages 7-11, berlangalabari2025theeffectof pages 2-4, song2024microstructuresandcorrosion pages 2-5)

References

1. (song2024microstructuresandcorrosion pages 2-5): Jie Song, Xavier A. Jimenez, Albert C. To, and Yao Fu. Microstructures and corrosion properties of wire arc additive manufactured copper–nickel alloys. Materials, 17:876, Feb 2024. URL: https://doi.org/10.3390/ma17040876, doi:10.3390/ma17040876. This article has 11 citations.

2. (song2024microstructuresandcorrosion pages 10-13): Jie Song, Xavier A. Jimenez, Albert C. To, and Yao Fu. Microstructures and corrosion properties of wire arc additive manufactured copper–nickel alloys. Materials, 17:876, Feb 2024. URL: https://doi.org/10.3390/ma17040876, doi:10.3390/ma17040876. This article has 11 citations.

3. (abreu2024influenceofdeep pages 4-5): Carmen M. Abreu, Iria Feijoo, Gloria Pena, and M. Consuelo Pérez. Influence of deep cryogenic treatment on the mechanical properties and corrosion resistance of nickel–aluminum bronze. Corrosion and Materials Degradation, 5:624-640, Dec 2024. URL: https://doi.org/10.3390/cmd5040030, doi:10.3390/cmd5040030. This article has 1 citations.

4. (metikoshukovic2011corrosionresistanceof pages 1-2): M. Metikoš-Huković, R. Babić, I. Škugor Rončević, and Z. Grubač. Corrosion resistance of copper–nickel alloy under fluid jet impingement. Desalination, 276:228-232, Aug 2011. URL: https://doi.org/10.1016/j.desal.2011.03.056, doi:10.1016/j.desal.2011.03.056. This article has 25 citations and is from a domain leading peer-reviewed journal.

5. (metikoshukovic2011corrosionresistanceof pages 2-3): M. Metikoš-Huković, R. Babić, I. Škugor Rončević, and Z. Grubač. Corrosion resistance of copper–nickel alloy under fluid jet impingement. Desalination, 276:228-232, Aug 2011. URL: https://doi.org/10.1016/j.desal.2011.03.056, doi:10.1016/j.desal.2011.03.056. This article has 25 citations and is from a domain leading peer-reviewed journal.

6. (metikoshukovic2011corrosionresistanceof pages 3-5): M. Metikoš-Huković, R. Babić, I. Škugor Rončević, and Z. Grubač. Corrosion resistance of copper–nickel alloy under fluid jet impingement. Desalination, 276:228-232, Aug 2011. URL: https://doi.org/10.1016/j.desal.2011.03.056, doi:10.1016/j.desal.2011.03.056. This article has 25 citations and is from a domain leading peer-reviewed journal.

7. (song2024microstructuresandcorrosion pages 13-14): Jie Song, Xavier A. Jimenez, Albert C. To, and Yao Fu. Microstructures and corrosion properties of wire arc additive manufactured copper–nickel alloys. Materials, 17:876, Feb 2024. URL: https://doi.org/10.3390/ma17040876, doi:10.3390/ma17040876. This article has 11 citations.

8. (abreu2024influenceofdeep pages 2-4): Carmen M. Abreu, Iria Feijoo, Gloria Pena, and M. Consuelo Pérez. Influence of deep cryogenic treatment on the mechanical properties and corrosion resistance of nickel–aluminum bronze. Corrosion and Materials Degradation, 5:624-640, Dec 2024. URL: https://doi.org/10.3390/cmd5040030, doi:10.3390/cmd5040030. This article has 1 citations.

9. (abreu2024influenceofdeep pages 10-12): Carmen M. Abreu, Iria Feijoo, Gloria Pena, and M. Consuelo Pérez. Influence of deep cryogenic treatment on the mechanical properties and corrosion resistance of nickel–aluminum bronze. Corrosion and Materials Degradation, 5:624-640, Dec 2024. URL: https://doi.org/10.3390/cmd5040030, doi:10.3390/cmd5040030. This article has 1 citations.

10. (abreu2024influenceofdeep pages 8-10): Carmen M. Abreu, Iria Feijoo, Gloria Pena, and M. Consuelo Pérez. Influence of deep cryogenic treatment on the mechanical properties and corrosion resistance of nickel–aluminum bronze. Corrosion and Materials Degradation, 5:624-640, Dec 2024. URL: https://doi.org/10.3390/cmd5040030, doi:10.3390/cmd5040030. This article has 1 citations.

11. (lv2019improvingcorrosionresistance pages 2-4): Yuting Lv, Bingjie Zhao, Hongbin Zhang, Chunjian Su, Bin Nie, Rui Wang, Lianmin Cao, and Fuyan Lyu. Improving corrosion resistance properties of nickel-aluminum bronze (nab) alloys via shot peening treatment. MATERIALS TRANSACTIONS, 60:1629-1637, Aug 2019. URL: https://doi.org/10.2320/matertrans.m2019031, doi:10.2320/matertrans.m2019031. This article has 23 citations and is from a peer-reviewed journal.

12. (lv2019improvingcorrosionresistance pages 4-5): Yuting Lv, Bingjie Zhao, Hongbin Zhang, Chunjian Su, Bin Nie, Rui Wang, Lianmin Cao, and Fuyan Lyu. Improving corrosion resistance properties of nickel-aluminum bronze (nab) alloys via shot peening treatment. MATERIALS TRANSACTIONS, 60:1629-1637, Aug 2019. URL: https://doi.org/10.2320/matertrans.m2019031, doi:10.2320/matertrans.m2019031. This article has 23 citations and is from a peer-reviewed journal.

13. (lv2019improvingcorrosionresistance pages 5-8): Yuting Lv, Bingjie Zhao, Hongbin Zhang, Chunjian Su, Bin Nie, Rui Wang, Lianmin Cao, and Fuyan Lyu. Improving corrosion resistance properties of nickel-aluminum bronze (nab) alloys via shot peening treatment. MATERIALS TRANSACTIONS, 60:1629-1637, Aug 2019. URL: https://doi.org/10.2320/matertrans.m2019031, doi:10.2320/matertrans.m2019031. This article has 23 citations and is from a peer-reviewed journal.

14. (lv2019improvingcorrosionresistance media 88fb0691): Yuting Lv, Bingjie Zhao, Hongbin Zhang, Chunjian Su, Bin Nie, Rui Wang, Lianmin Cao, and Fuyan Lyu. Improving corrosion resistance properties of nickel-aluminum bronze (nab) alloys via shot peening treatment. MATERIALS TRANSACTIONS, 60:1629-1637, Aug 2019. URL: https://doi.org/10.2320/matertrans.m2019031, doi:10.2320/matertrans.m2019031. This article has 23 citations and is from a peer-reviewed journal.

15. (song2013comparisonofcorrosion pages 1-4): Q. Song, Yingkui Zheng, Shenglin Jiang, D. Ni, and Zhi Ma. Comparison of corrosion and cavitation erosion behaviors between the as-cast and friction-stir-processed nickel aluminum bronze. Jul 2013. URL: https://doi.org/10.5006/0984, doi:10.5006/0984. This article has 63 citations and is from a peer-reviewed journal.

16. (song2013comparisonofcorrosion pages 4-8): Q. Song, Yingkui Zheng, Shenglin Jiang, D. Ni, and Zhi Ma. Comparison of corrosion and cavitation erosion behaviors between the as-cast and friction-stir-processed nickel aluminum bronze. Jul 2013. URL: https://doi.org/10.5006/0984, doi:10.5006/0984. This article has 63 citations and is from a peer-reviewed journal.

17. (song2013comparisonofcorrosion pages 8-12): Q. Song, Yingkui Zheng, Shenglin Jiang, D. Ni, and Zhi Ma. Comparison of corrosion and cavitation erosion behaviors between the as-cast and friction-stir-processed nickel aluminum bronze. Jul 2013. URL: https://doi.org/10.5006/0984, doi:10.5006/0984. This article has 63 citations and is from a peer-reviewed journal.

18. (ocejo2022corrosionbehaviorof pages 1-3): Ignacio Cobo Ocejo, Maria Victoria Biezma Moraleda, and Paul Linhardt. Corrosion behavior of heat-treated nickel-aluminum bronze and manganese-aluminum bronze in natural waters. Metals, 12:380, Feb 2022. URL: https://doi.org/10.3390/met12030380, doi:10.3390/met12030380. This article has 10 citations.

19. (ocejo2022corrosionbehaviorof pages 8-10): Ignacio Cobo Ocejo, Maria Victoria Biezma Moraleda, and Paul Linhardt. Corrosion behavior of heat-treated nickel-aluminum bronze and manganese-aluminum bronze in natural waters. Metals, 12:380, Feb 2022. URL: https://doi.org/10.3390/met12030380, doi:10.3390/met12030380. This article has 10 citations.

20. (ocejo2022corrosionbehaviorof pages 3-5): Ignacio Cobo Ocejo, Maria Victoria Biezma Moraleda, and Paul Linhardt. Corrosion behavior of heat-treated nickel-aluminum bronze and manganese-aluminum bronze in natural waters. Metals, 12:380, Feb 2022. URL: https://doi.org/10.3390/met12030380, doi:10.3390/met12030380. This article has 10 citations.

21. (berlangalabari2025theeffectof pages 4-7): Carlos Berlanga-Labari, Adrián Claver, María Victoria Biezma-Moraleda, and José Fernández-Palacio. The effect of kappa phases on tribocorrosion behaviour of nickel aluminum bronze (nab) and manganese aluminum bronze (mab). Lubricants, 13:290, Jun 2025. URL: https://doi.org/10.3390/lubricants13070290, doi:10.3390/lubricants13070290. This article has 4 citations.

22. (berlangalabari2025theeffectof pages 7-11): Carlos Berlanga-Labari, Adrián Claver, María Victoria Biezma-Moraleda, and José Fernández-Palacio. The effect of kappa phases on tribocorrosion behaviour of nickel aluminum bronze (nab) and manganese aluminum bronze (mab). Lubricants, 13:290, Jun 2025. URL: https://doi.org/10.3390/lubricants13070290, doi:10.3390/lubricants13070290. This article has 4 citations.

23. (berlangalabari2025theeffectof pages 2-4): Carlos Berlanga-Labari, Adrián Claver, María Victoria Biezma-Moraleda, and José Fernández-Palacio. The effect of kappa phases on tribocorrosion behaviour of nickel aluminum bronze (nab) and manganese aluminum bronze (mab). Lubricants, 13:290, Jun 2025. URL: https://doi.org/10.3390/lubricants13070290, doi:10.3390/lubricants13070290. This article has 4 citations.

24. (ding2016fabricatingsuperiornial pages 9-12): Donghong Ding, Zengxi Pan, Stephen Van Duin, Huijun Li, and Chen Shen. Fabricating superior nial bronze components through wire arc additive manufacturing. Materials, 9:652, Aug 2016. URL: https://doi.org/10.3390/ma9080652, doi:10.3390/ma9080652. This article has 279 citations.

25. (ding2016fabricatingsuperiornial pages 3-6): Donghong Ding, Zengxi Pan, Stephen Van Duin, Huijun Li, and Chen Shen. Fabricating superior nial bronze components through wire arc additive manufacturing. Materials, 9:652, Aug 2016. URL: https://doi.org/10.3390/ma9080652, doi:10.3390/ma9080652. This article has 279 citations.

26. (arcos2023nialbronzein pages 2-4): Camila Arcos, Carolina Guerra, Jorge A. Ramos-Grez, and Mamié Sancy. Ni-al bronze in molten carbonate manufactured by lpbf: effect of porosity design on mechanical properties and oxidation. Materials, 16:3893, May 2023. URL: https://doi.org/10.3390/ma16103893, doi:10.3390/ma16103893. This article has 8 citations.

27. (arcos2023nialbronzein pages 4-6): Camila Arcos, Carolina Guerra, Jorge A. Ramos-Grez, and Mamié Sancy. Ni-al bronze in molten carbonate manufactured by lpbf: effect of porosity design on mechanical properties and oxidation. Materials, 16:3893, May 2023. URL: https://doi.org/10.3390/ma16103893, doi:10.3390/ma16103893. This article has 8 citations.

28. (arcos2023nialbronzein pages 6-8): Camila Arcos, Carolina Guerra, Jorge A. Ramos-Grez, and Mamié Sancy. Ni-al bronze in molten carbonate manufactured by lpbf: effect of porosity design on mechanical properties and oxidation. Materials, 16:3893, May 2023. URL: https://doi.org/10.3390/ma16103893, doi:10.3390/ma16103893. This article has 8 citations.

29. (laleh2020twoandthreedimensional pages 1-6): Majid Laleh, Anthony E. Hughes, Sam Yang, Jianli Li, Wei Xu, Ian Gibson, and Mike Y. Tan. Two and three-dimensional characterisation of localised corrosion affected by lack-of-fusion pores in 316l stainless steel produced by selective laser melting. Corrosion Science, 165:108394, Apr 2020. URL: https://doi.org/10.1016/j.corsci.2019.108394, doi:10.1016/j.corsci.2019.108394. This article has 175 citations and is from a highest quality peer-reviewed journal.

30. (laleh2020twoandthreedimensional pages 6-10): Majid Laleh, Anthony E. Hughes, Sam Yang, Jianli Li, Wei Xu, Ian Gibson, and Mike Y. Tan. Two and three-dimensional characterisation of localised corrosion affected by lack-of-fusion pores in 316l stainless steel produced by selective laser melting. Corrosion Science, 165:108394, Apr 2020. URL: https://doi.org/10.1016/j.corsci.2019.108394, doi:10.1016/j.corsci.2019.108394. This article has 175 citations and is from a highest quality peer-reviewed journal.

31. (laleh2020twoandthreedimensional pages 10-14): Majid Laleh, Anthony E. Hughes, Sam Yang, Jianli Li, Wei Xu, Ian Gibson, and Mike Y. Tan. Two and three-dimensional characterisation of localised corrosion affected by lack-of-fusion pores in 316l stainless steel produced by selective laser melting. Corrosion Science, 165:108394, Apr 2020. URL: https://doi.org/10.1016/j.corsci.2019.108394, doi:10.1016/j.corsci.2019.108394. This article has 175 citations and is from a highest quality peer-reviewed journal.

32. (laleh2020twoandthreedimensional pages 14-17): Majid Laleh, Anthony E. Hughes, Sam Yang, Jianli Li, Wei Xu, Ian Gibson, and Mike Y. Tan. Two and three-dimensional characterisation of localised corrosion affected by lack-of-fusion pores in 316l stainless steel produced by selective laser melting. Corrosion Science, 165:108394, Apr 2020. URL: https://doi.org/10.1016/j.corsci.2019.108394, doi:10.1016/j.corsci.2019.108394. This article has 175 citations and is from a highest quality peer-reviewed journal.

33. (laleh2020twoandthreedimensional pages 17-21): Majid Laleh, Anthony E. Hughes, Sam Yang, Jianli Li, Wei Xu, Ian Gibson, and Mike Y. Tan. Two and three-dimensional characterisation of localised corrosion affected by lack-of-fusion pores in 316l stainless steel produced by selective laser melting. Corrosion Science, 165:108394, Apr 2020. URL: https://doi.org/10.1016/j.corsci.2019.108394, doi:10.1016/j.corsci.2019.108394. This article has 175 citations and is from a highest quality peer-reviewed journal.

34. (ocejo2022corrosionbehaviorof pages 5-8): Ignacio Cobo Ocejo, Maria Victoria Biezma Moraleda, and Paul Linhardt. Corrosion behavior of heat-treated nickel-aluminum bronze and manganese-aluminum bronze in natural waters. Metals, 12:380, Feb 2022. URL: https://doi.org/10.3390/met12030380, doi:10.3390/met12030380. This article has 10 citations.

35. (lu2024effectsofmedium pages 2-4): Bochao Lu, Ning Cui, Yimeng Zhang, Ding Guo, Yanan Wang, Xiaopeng Wang, and Jizhou Duan. Effects of medium and flow rate on the film-forming structures of b10 cu-ni alloys and their resistance to corrosion caused by sulfate-reducing bacteria. Metals, 14:1451, Dec 2024. URL: https://doi.org/10.3390/met14121451, doi:10.3390/met14121451. This article has 3 citations.

36. (nemani2024advancementsinadditive pages 50-53): Alireza Vahedi Nemani, Mahya Ghaffari, Kazem Sabet Bokati, Nima Valizade, Elham Afshari, and Ali Nasiri. Advancements in additive manufacturing for copper-based alloys and composites: a comprehensive review. Journal of Manufacturing and Materials Processing, 8:54, Mar 2024. URL: https://doi.org/10.3390/jmmp8020054, doi:10.3390/jmmp8020054. This article has 100 citations.
