<!--
Edison Scientific LITERATURE task (batch 1)
- Task ID: 6780e82f-75ad-4e6d-bcc6-1d7d4c81e1c8
- Submitted: 2026-10-18T01:19:59Z
- Fetched: 2026-10-18T01:53:32Z (status: success)
- Raw trajectory JSON: ../raw/c1-02-dc-sequence-for-cu.json.gz
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

QUESTION: The aluminum plan runs OCP (30 min), LPR (+/-10 mV at 0.167 mV/s),
then an ASTM G61-style cyclic polarization reversed at 1 mA/cm2 to obtain
pitting and repassivation potentials. Copper alloys in seawater mostly
corrode actively under a Cu2O-based film rather than pitting from a passive
state. Which sequences of DC measurements (and EIS, where used) have
characterized Cu-Ni and NAB in chloride or seawater within about 2 hours, and
what does each step return? Is cyclic polarization meaningful for these
alloys: are there published breakdown, pitting or protection potentials for
Cu-Ni (including in sulfide-polluted water) and for NAB selective phase
corrosion, and which reversal criteria were used? Should potentiostatic holds
be added at service-relevant potentials, such as the mixed potential of a
galvanic couple with steel or titanium, or the cathodic protection potentials
applied to NAB propellers (including potentials reported to suppress
selective phase corrosion), and what current densities do such holds draw?
Report measured ranges for wrought, cast and additively manufactured Cu-Ni
and NAB: Ecorr (vs SCE or Ag/AgCl), Rp (ohm cm2), icorr (uA/cm2),
oxygen-reduction limiting current density, anodic current density up to
+300 mV above Ecorr, and the potential window used, so that a potentiostat's
current ranges and compliance can be sized for 0.07-0.13 cm2 spots.

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

QUESTION: The aluminum plan runs OCP (30 min), LPR (+/-10 mV at 0.167 mV/s),
then an ASTM G61-style cyclic polarization reversed at 1 mA/cm2 to obtain
pitting and repassivation potentials. Copper alloys in seawater mostly
corrode actively under a Cu2O-based film rather than pitting from a passive
state. Which sequences of DC measurements (and EIS, where used) have
characterized Cu-Ni and NAB in chloride or seawater within about 2 hours, and
what does each step return? Is cyclic polarization meaningful for these
alloys: are there published breakdown, pitting or protection potentials for
Cu-Ni (including in sulfide-polluted water) and for NAB selective phase
corrosion, and which reversal criteria were used? Should potentiostatic holds
be added at service-relevant potentials, such as the mixed potential of a
galvanic couple with steel or titanium, or the cathodic protection potentials
applied to NAB propellers (including potentials reported to suppress
selective phase corrosion), and what current densities do such holds draw?
Report measured ranges for wrought, cast and additively manufactured Cu-Ni
and NAB: Ecorr (vs SCE or Ag/AgCl), Rp (ohm cm2), icorr (uA/cm2),
oxygen-reduction limiting current density, anodic current density up to
+300 mV above Ecorr, and the potential window used, so that a potentiostat's
current ranges and compliance can be sized for 0.07-0.13 cm2 spots.

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


# Electrochemical screening of marine Cu–Ni and nickel–aluminium bronze

**Recommendation.** Keep the short open-circuit measurement, but do not make an ASTM G61-style “pitting potential” the principal copper-alloy outcome. Measure the near-OCP differential resistance, an optional short EIS spectrum, oxygen-reduction and *anodic dissolution at specified potentials*, and element-resolved release. Reserve cyclic polarization for a separately labelled, deliberately aggressive comparison with a specified current-reversal rule. Report the electrolyte, aeration, immersion age, reference electrode, exposed area and reversal current with every result. Published Cu–Ni and NAB curves show CuCl/Cu₂O film formation, active dissolution, pseudopassivity and sometimes phase-selective attack; a current-defined inflection is not automatically pit initiation. (kear2004electrochemicalcorrosionbehaviour pages 4-5, kear2004electrochemicalcorrosionbehaviour pages 6-7, ding2019evolutionofthe pages 6-9, shahriari2023corrosionperformanceof pages 2-4)

## 1. Published measurement sequences and quantitative comparators

In the items below, **Rₚ** means a near-*E*<sub>corr</sub> differential polarization resistance only when it was actually measured that way. **R<sub>ct</sub>**, film resistance **R<sub>f</sub>**, and fitted total impedance are identified separately. Reported *i*<sub>corr</sub> values from broad polarization/Tafel fits are **published descriptors, not validated metal-loss measurements**. “Volume not reported” means the paper does not support transferring its bulk-cell mass transport to a 150-µL well. Numerical potentials are not interchangeable between SCE and the particular Ag/AgCl filling solution without calibration. (yuan2007surfacecharacterizationand pages 3-5, kear2004electrochemicalcorrosionbehaviour pages 9-10, abreu2024influenceofdeep pages 4-5)

1. **[CITE] [NUMBERS] [NAVY] [CUBXL] Yuan, S. J.; Pehkonen, S. O. “Surface characterization and corrosion behavior of 70/30 Cu–Ni alloy in pristine and sulfide-containing simulated seawater.” *Corrosion Science* **49** (2007), 1276–1304. DOI: **10.1016/j.corsci.2006.07.003**.** CDA 715 plate, nominal **Cu 67.84, Ni 30.60, Fe 0.63, Mn 0.60, Zn 0.02 wt%**; polished to 1200 grit. A bulk **500-mL** three-electrode cell exposed **0.785 cm²**, with Pt counter and Ag/AgCl reference. Aerated, stagnant, nine-salt simulated seawater, pH **8.2 ± 0.1**, 25 °C, was tested fresh and after **1, 3, 6 and 10 days**; the polluted arm began at **10 ppm sulfide**, which declined during exposure. The applicable short sequence is immersion/OCP → **EIS at OCP, 10 mV, 100 kHz–5 mHz** → polarization **−250 to +250 mV relative to OCP at 2 mV/s** (a 250-s sweep, excluding equilibration/EIS). Published Tafel-derived *i*<sub>corr</sub> for fresh surfaces was **8.44 µA/cm²** in clean solution versus **87.39 µA/cm²** initially with sulfide; at day 10 it was **1.01 versus 18.44 µA/cm²**, respectively. **Neither value is a measured LPR-derived dissolution rate.** EIS distinguished increasingly resistant clean oxide from persistently porous sulfide-containing product. **CubXL:** separately track preparation-to-measurement age, sulfide concentration and dissolved oxygen; do not equate fresh-surface rankings with mature-film rankings. The published short sweep gives corrosion and polarization response, **not a cyclic protection potential**. Electrolyte-to-area ratio was much larger than in the proposed wells. (yuan2007surfacecharacterizationand pages 3-5, yuan2007surfacecharacterizationand pages 5-8, yuan2007surfacecharacterizationand pages 8-11, yuan2007surfacecharacterizationand pages 26-29)

2. **[CITE] [NUMBERS] [NAVY] [CUBXL] Gao, X.; Liu, M. “Corrosion Behavior of High-Strength C71500 Copper-Nickel Alloy in Simulated Seawater with High Concentration of Sulfide.” *Materials* **15** (2022), 8513. DOI: **10.3390/ma15238513**.** Forged, cold-rolled and heat-treated pipe, **Ni 30.54, Mn 0.93, Fe 0.80 wt%, Cu balance**; polished outside pipe surface, epoxy masked. Bulk three-electrode cell, **SCE**, Pt-mesh counter; exposed curved area was measured individually, but solution volume was not reported in the examined methods. At **35 ± 2 °C**, pH **8.20**, electrolyte was **3.5 wt% NaCl + 0.5 wt% Na₂S**, a severe *pollution simulant*, not ordinary seawater. Sequence: **30-min OCP → EIS, 10 mV, 100 kHz–0.01 Hz → potentiodynamic scan from OCP−0.3 to OCP+0.8 V at 1 mV/s**. The scan alone spans about **18 min**. Fitted EIS charge-transfer resistance was **1,817 Ω·cm² at 0.5 h**, **2,213 at 24 h**, and **6,619 at 672 h**; these are **not Rₚ**. Anodic features at approximately **−525 and −404 mV SCE** changed with ageing and were attributed to reactions/products, **not measured *E*<sub>pit</sub> or *E*<sub>prot</sub>**. The published polarization fit reports exceptionally large early *i*<sub>corr</sub>, but its extracted table is internally misaligned; it should not be used to set a precise kinetic specification. Gravimetric corrosion declined from about **0.15 mm/y** initially to about **0.09 mm/y** at 168 h. **CubXL:** sulfur chemistry and accumulation in a tiny well warrant dedicated volume, pH and blank controls; the paper supplies no cyclic reversal criterion. (gao2022corrosionbehaviorof pages 2-4, gao2022corrosionbehaviorof pages 4-5, gao2022corrosionbehaviorof pages 6-8)

3. **[CITE] [NUMBERS] [NAVY] [CUBXL] [NOVELTY-RISK] Song, J.; Jimenez, X. A.; To, A. C.; Fu, Y. “Microstructures and Corrosion Properties of Wire Arc Additive Manufactured Copper–Nickel Alloys.” *Materials* **17** (2024), 876. DOI: **10.3390/ma17040876**.** This is **wire-arc AM (WAAM), not powder-fed laser DED**. Wire: **Cu 67.5, Ni 30.0, Mn 0.7, Fe 0.55, Ti 0.25, Si 0.10 wt%**; comparison wrought plate: **Cu 68.046, Ni 30.46, Mn 0.73, Fe 0.56 wt%**. Epoxy-masked **0.32-cm² bulk flat-cell** specimens were tested on build-transverse and build-longitudinal cuts; solution volume was not reported. In naturally aerated **3.5 wt% NaCl**, sequence was **3 h at OCP → EIS, 10 mV rms, 100 kHz–10 mHz**, or, on a freshly reground surface, **cyclic polarization beginning OCP−250 mV, forward at 0.1667 mV/s, reversed at 3 mA/cm², reverse at 1.667 mV/s**. Thus **the published experiment is not a ≤2-h sequence**. Authors *operationally defined* “breakdown” as potential at **50 µA/cm²**, separately from the **3-mA/cm²** reversal. EIS **R<sub>f</sub>**, reported as absolute Ω rather than Ω·cm², was **1.08–1.18 × 10⁵ Ω wrought** and **0.68–1.66 × 10⁵ Ω across WAAM cuts/conditions**. A genuinely higher breakdown descriptor was reported for selected WAAM specimens, but no numerically verified *E*<sub>prot</sub> is available in the inspected text. **CubXL:** cite this work when claiming novelty: Cu–Ni AM-versus-wrought chloride cycling and build-direction comparisons already exist; the distinct opportunity is *powder* DED repair-zone mapping plus microvolume dissolution. Do not label the **50-µA/cm²** crossing “pit initiation” without microscopy. (song2024microstructuresandcorrosion pages 2-5, song2024microstructuresandcorrosion pages 10-13, song2024microstructuresandcorrosion pages 14-17)

4. **[CITE] [NUMBERS] [NAVY] [CUBXL] Ding, Y.; Zhao, R.; Qin, Z.-b.; Wu, Z.; Wang, L.; Liu, L.; Lu, W. “Evolution of the Corrosion Product Film on Nickel-Aluminum Bronze and Its Corrosion Behavior in 3.5 wt % NaCl Solution.” *Materials* **12** (2019), 209. DOI: **10.3390/ma12020209**.** Vacuum-induction **cast C95800**, **Al 9.22, Fe 4.17, Ni 4.17, Mn 1.23 wt%, Cu balance**; ground to 2000 grit and polished to 0.5 µm. Bulk **1-cm²**, Pt-counter, **SCE** cell in aerated **3.5 wt% NaCl** at **20 ± 2 °C**; electrolyte volume not reported. On fresh material and after **48, 120 and 240 h** immersion, the sequence comprised stable OCP, **EIS at OCP, 5 mV, 100 kHz–0.01 Hz**, and a **0.5-mV/s** polarization curve; scan endpoints are not specified in the inspected methods. Fresh **OCP −0.264 V SCE; fitted *E*<sub>corr</sub> −0.260 V SCE; fitted *i*<sub>corr</sub> 11.35 µA/cm²; EIS R<sub>f</sub> 1,761 and R<sub>ct</sub> 317.6 Ω·cm²**. At 240 h these became **−0.237 V, −0.257 V, 3.78 µA/cm², 11,976 and 35,939 Ω·cm²**, respectively: **R<sub>f</sub> + R<sub>ct</sub> is not an independently measured LPR**. Crucially, in situ AFM observed **~25-nm attack of lamellar α at 60 min** and **>50-nm β′ attack at 60 min, reaching ~500 nm by 150 min**; local scanning-vibrating-electrode anodic peaks at a fresh scratch were **~260 µA/cm² initially, ~190 at 30 min and ~340 at 90 min**. These *local fluxes are not the global potentiostat current density*. **CubXL:** place distinct wells on α/κ-rich and β′/fusion-zone regions where feasible; photograph and profilometer-map registered spots because selective damage can develop within the proposed test duration even without a conventional pit threshold. (ding2019evolutionofthe pages 1-3, ding2019evolutionofthe pages 3-6, ding2019evolutionofthe pages 6-9, ding2019evolutionofthe pages 9-12)

5. **[CITE] [NUMBERS] [NAVY] [NOVELTY-RISK] [CUBXL] Shahriari, A.; Chalasani, D.; Amirkhiz, B. S.; Mohammadi, M. “Corrosion performance of wire arc additively manufactured NAB alloy.” *npj Materials Degradation* **7** (2023). DOI: **10.1038/s41529-023-00405-x**.** **GMAW-WAAM** ERCuNiAl deposits, as-built and heat treated, compared with cast NAB: *not* blown-powder laser DED. Exact feed and cast wt% and bath volume could not be verified in accessible evidence. Bulk-cell exposed areas **0.181–1.171 cm²**, graphite counter, **saturated Ag/AgCl** reference, naturally aerated **3.5 wt% NaCl**, **23 ± 2 °C**. **30-min OCP → EIS, 10 mV, 100 kHz–0.01 Hz → cyclic scan starting OCP−500 mV at 0.166 mV/s; reverse at 10 mA/cm²**. Additional immersion was **96 h** for as-built/cast and **24 h** for heat-treated specimens. As-built OCP was approximately **−0.293 V Ag/AgCl** versus approximately **−0.222 V** for the other conditions; oxidation features were approximately **+0.07 V** as-built and **+0.03 V** cast/selected heat treatments. Authors specifically reported that **most specimens had no distinct pitting-potential range**. For WAAM heat treatments, reported fitted *i*<sub>corr</sub> was approximately **4.4, 6.6 and 8 µA/cm²**, with EIS total resistance approximately **10.2, 2.58 and 3.8 kΩ·cm²**, respectively. **CubXL:** a nominally similar “G61” experiment already exists and its **10-mA/cm²** reversal is tenfold the aluminum plan’s **1-mA/cm²**: claim novelty in spatially resolved *laser-powder-DED repair interfaces and element-resolved dissolution*, not in cyclic testing of AM NAB. The cited results do not supply validated LPR, ICP release, or a unique protection potential. (shahriari2023corrosionperformanceof pages 14-14, shahriari2023corrosionperformanceof pages 2-4, shahriari2023corrosionperformanceof pages 12-14)

6. **[CITE] [NUMBERS] [NAVY] [CUBXL] [NOVELTY-RISK] Huo, R.; Wang, Z.; Wang, M.; Wang, R.; Zhang, S.; Zhang, C.; Wu, C.; Chen, H.; Chen, J. “Modulating Heat Input to Optimize Corrosion Resistance of Nickel–Aluminum Bronze Manufactured by Cold Metal Transfer Additive Manufacturing.” *Materials* **18** (2025), 2205. DOI: **10.3390/ma18102205**.** **Arc/CMT-AM**, not laser DED; ERCuNiAl wire **Al 8.73, Fe 5.90, Ni 4.52, Mn 1.39 wt%, Cu balance**, deposited onto a **Cu–8.62Al–2.32Fe** substrate, *not* a cast C95800 repair interface. Bulk flat **1-cm²** epoxy cell, Pt counter, **SCE**; electrolyte volume unreported. In aerated **3.5 wt% NaCl**, sequence **60-min OCP → EIS, 3 mV, 100 kHz–0.01 Hz → another 30-min OCP before polarization from −0.6 to +1.3 V SCE at 0.5 mV/s**; that scan alone lasts **~63 min**, so the combined protocol **exceeds two hours**. After one hour, measured OCPs across increasing heat input were approximately **−237, −274, −391, −421 mV SCE**; *separately*, the paper’s polarization-fit potential column lists **−270, −467, −518, −701 mV**, a discrepancy that must **not** be merged into a single *E*<sub>corr</sub> range. Fitted *i*<sub>corr</sub> increased **2.56 → 3.85 → 5.03 → 7.52 µA/cm²**. EIS fitted **R<sub>ct</sub> 2,485 → 1,966 → 1,284 → 707 Ω·cm²** and **R<sub>f</sub> 1,152 → 1,047 → 947 → 186 Ω·cm²**; the table accidentally labels its third row “S2,” interpreted here by its order as S3. **CubXL:** compare heat-input histories and phase maps, but neither these resistances nor fit currents establish corrosion performance of 300–500-W powder-laser repair. (huo2025modulatingheatinput pages 4-5, huo2025modulatingheatinput pages 10-13, huo2025modulatingheatinput pages 13-15)

7. **[CITE] [NUMBERS] [NAVY] [CUBXL] Abreu, C. M.; Feijoo, I.; Pena, G.; Pérez, M. C. “Influence of Deep Cryogenic Treatment on the Mechanical Properties and Corrosion Resistance of Nickel–Aluminum Bronze.” *Corrosion and Materials Degradation* **5** (2024), 624–640. DOI: **10.3390/cmd5040030**.** **Cast C95800** (**Al 8.96, Ni 4.93, Fe 5.09, Mn 1.24 wt%, Cu balance**), cryogenically treated and/or annealed. Conventional bulk **0.28-cm²** cell, Pt mesh, **SCE**, **3.5% NaCl at pH 7.9**; volume unreported. **60-min OCP** gave approximately **−0.28 V SCE** for the cryogenically treated sample. Following oxide removal, the investigators performed a **fixed-endpoint cyclic voltammogram at 1 mV/s**, described in the results/figure as **−1.5 → +0.75 → −1.5 V SCE**, with a separately repolished surface used for **OCP EIS, 10 mV rms, 1 MHz–1 mHz**, after 1–72 h exposure. The methods text gives contradictory scan signs/endpoints: **confirm the original instrument program before attempting replication**. Oxidation peaks were **~−0.29 V SCE** (Cu₂O) and **~+0.29 V SCE** (Cu/CuCl chemistry), with another assigned near **+0.38 V**; currents in the published cycle extend to **tens of mA/cm²**. These are **reaction peaks and a fixed upper reversal**, not verified pit/protection potentials. **CubXL:** do not apply the −1.5-to-+0.75-V cycle to the same spot intended for representative OCP dissolution/ICP. (abreu2024influenceofdeep pages 2-4, abreu2024influenceofdeep pages 4-5, abreu2024influenceofdeep pages 8-10)

8. **[CITE] [NUMBERS] [NAVY] [CUBXL] Tan, Y.; Xie, H.; Feng, X.; Huang, S.; Zhang, W.; Peng, L.; Wang, W.; Zhao, Y. “Effect of Al/Ni Ratio on the Microstructure and Properties of Nickel–Aluminum Bronze Alloys.” *Materials* **17** (2024), 1330. DOI: **10.3390/ma17061330**.** Vacuum-melted **cast** composition series (Al/Ni/Fe/Mn wt%): **6.94/6.82/4.10/1.72**, **7.90/6.13/3.92/2.12**, **8.94/5.18/4.12/2.18**, **9.94/3.99/3.94/1.82**, Cu balance. Flat bulk **1-cm²** working area, Pt counter, **Ag/AgCl**, **3.5 wt% NaCl**; solution volume unreported. Following **10- or 30-day immersion**, EIS at stabilized OCP used **10 mV, 100 kHz–0.01 Hz**, followed by **−0.5 to +0.8 V at 0.5 mV/s** (a **~43-min** noncyclic sweep). At **10 days**, fitted ** *E*<sub>corr</sub> −266 to −245 mV Ag/AgCl, *i*<sub>corr</sub> 0.50–2.16 µA/cm², derived Stern–Geary Rₚ 11.07–78.12 kΩ·cm²**. At **30 days**, corresponding ranges are **−296 to −249 mV, 0.35–0.78 µA/cm² and 54.04–173.48 kΩ·cm²**. **These Rₚ were calculated from Tafel slopes and fitted currents, not measured by ±10-mV LPR**; the alloys also differ in composition. The paper identifies oxidation/film regions near **0.2–0.4 V**, not a reproducible NAB phase-selective pitting potential. **CubXL:** use these only as *aged, composition-dependent* impedance/current benchmarks, not fresh C95800 design targets. (tan2024effectofalni pages 2-4, tan2024effectofalni pages 4-6, tan2024effectofalni pages 10-12)

9. **[CITE] [NUMBERS] [NAVY] [CUBXL] Roberge, P. R.; Beaudoin, R. “Behavior of the corrosion potential and corrosion current of Cu-Ni alloys under erosion corrosion conditions. Effect of oxygen.” *Journal of Applied Electrochemistry* **18** (1988), 601–607. DOI: **10.1007/BF01022257**.** Machined **cast** rotating-cylinder alloys: 90/10 **Cu 88.12, Ni 10.35, Fe 0.59 wt%**; Nb-modified 70/30 **Cu 67.7, Ni 29.3, Fe 1.0, Mn 0.81, Nb 0.42**; Cr-modified 70/30 **Cu 65.7, Ni 30.78, Fe 0.77, Mn 0.75, Cr 2.1**. About **1 L of 3% NaCl** in a 2-L bulk vessel, controlled dissolved oxygen, **SCE**; sample rotation **0 or 5,000 rpm** after **10 days** initial immersion. EIS tracked *E*<sub>corr</sub> and resistance during changing flow; the 70/30-Nb material’s impedance-extrapolated resistance fell from **~35–37 to ~15–15.5 kΩ·cm²** during 5 h of rotation. **Not an unaged 2-h measurement.** A pure-Cu-cylinder experiment characterized oxygen mass-transfer limiting current but **does not report a directly transferable Cu–Ni small-well *i*<sub>L,O₂</sub>**. **CubXL:** static, open-air 150 µL is a distinct hydrodynamic/oxygen condition; measure a cathodic branch under controlled aeration rather than copying a pipe-flow limiting-current value. (roberge1988behaviorofthe pages 1-2, roberge1988behaviorofthe pages 2-3, roberge1988behaviorofthe pages 3-5)

10. **[CITE] [NUMBERS] [NAVY] [CUBXL] [NOVELTY-RISK] Luo, K.; Zhao, P.; Fang, K.-W.; Zhao, W.-X.; Lu, J.; Liu, H.-Q.; Wang, S.-Y.; Zhu, M.; Qiao, Y.-X. “The Galvanic Corrosion Behavior of ZCuAl10Fe5Ni5 Coupled with SAF2507 Duplex Stainless Steel in Seawater.” *Metals* **16** (2026), 473. DOI: **10.3390/met16050473**.** NAB-type **Cu balance, Al 10.45, Fe 5.44, Ni 4.69 wt%** coupled to duplex steel; bulk ASTM-D1141-type seawater; electrolyte volume unreported, **SCE** for separate electrode potentials. Anode:cathode exposed area was **1:1 (1:1 cm²)** or **1:50 (0.06:3 cm²)**—the latter anode is *smaller than one proposed CubXL spot*. **10 min galvanic current/potential → 10 min separate OCP → OCP EIS, 10 mV, 100 kHz–0.1 Hz**, repeated after longer coupled exposure. At **1:50**, initial reported galvanic *anode* current density was **~38 µA/cm²**, dropping to **~2 at 72 h** and rising to **~4 at 360 h**; the 1:1 measurements were near zero. The article establishes the **area-ratio dependence**, but an exact mixed potential suitable as a universal potentiostatic setpoint cannot be verified from the inspected text. **CubXL:** first determine the mixed potential of *the intended actual steel/titanium pair and area ratio* in a separate coupled bulk cell, then impose that measured potential on an independent Cu-alloy spot. An artificial “steel mixed potential” chosen without pairing and area ratio is not service-specific. (luo2026thegalvaniccorrosion pages 3-4, luo2026thegalvaniccorrosion pages 4-6, luo2026thegalvaniccorrosion pages 9-11)

11. **[CITE] [NUMBERS] [NAVY] [CUBXL] Kear, G.; Barker, B. D.; Stokes, K.; Walsh, F. C. “Electrochemical Corrosion Behaviour of 90–10 Cu–Ni Alloy in Chloride-Based Electrolytes.” *Journal of Applied Electrochemistry* **34** (2004), 659–669. DOI: **10.1023/B:JACH.0000031164.32520.58**.** This is a **review of wrought/cast and rotating-electrode studies**, **not one cell protocol or one composition**; 90/10 designations cover approximately **9–11 wt% Ni and 1–2 wt% Fe**. Across distinct aerated seawater reports, freshly polished corrosion rates correspond to approximately **0.5–21 µA/cm²**; the review gives a freshwater-versus-marine and surface-age caveat, and reports one freshly polished estimate **~12 µA/cm²** falling to **~5 µA/cm²** after **20–22 h** of flowing-water ageing. Anodic copper dissolution can show an initial peak, CuCl₂⁻-transport-associated limiting region, and subsequently Cu(II) formation. One reported peak was around **−0.010 V SCE** in its particular chloride/flow experiment and a limiting region reached approximately **+0.09 V SCE** elsewhere: **neither is a transferable pit potential**. This review explicitly cautions that Stern–Geary **B** and apparent Tafel slopes are transport-dependent. It acknowledges UK defence-related financial support. **CubXL:** use actual near-OCP *Rₚ* and signed current–potential curves, not a fixed B to claim a material-loss rate. (kear2004electrochemicalcorrosionbehaviour pages 1-2, kear2004electrochemicalcorrosionbehaviour pages 4-5, kear2004electrochemicalcorrosionbehaviour pages 5-6, kear2004electrochemicalcorrosionbehaviour pages 6-7, kear2004electrochemicalcorrosionbehaviour pages 9-10)

**Other near-term corrosion modes.** Song, Q.; Zheng, Y.; Jiang, S.; Ni, D.; Ma, Z. “Comparison of Corrosion and Cavitation Erosion Behaviors Between the As-Cast and Friction-Stir-Processed Nickel Aluminum Bronze.” *Corrosion* **69** (2013), 1111–1121. DOI: **10.5006/0984**. Cast **C95800** (**Al 9.18, Ni 4.49, Fe 4.06, Mn 1.03 wt%**), versus **friction-stir-processed cast NAB**, not additive manufacturing. Bulk **0.49-cm²** epoxy-sealed SCE/Pt cell, **3.5 wt% NaCl**; bath volume unreported. OCP-EIS was **100 kHz–10 mHz, 5 mV peak-to-peak** on long-immersed samples; under cavitation, EIS was **20 kHz–0.1 Hz**, followed by a **noncyclic ±250-mV-from-OCP scan at 1 mV/s**. After 10 days, FSP impedance arc was approximately one order of magnitude larger than cast; cavitation in saltwater produced **33.4 versus 15.9 mg loss at 16 h** for cast versus FSP. These numbers concern **cavitation-assisted damage**, not static micro-well dissolution. **[CITE] [NUMBERS] [NAVY] [CUBXL]** (song2013comparisonofcorrosion pages 4-8, song2013comparisonofcorrosion pages 8-12)

## 2. What a cyclic scan can—and cannot—establish

**Cu–Ni:** A published WAAM Cu–Ni study reverses at **3 mA/cm²** and reports a **50-µA/cm² operational breakdown descriptor**. Literature on conventional 90/10 instead describes anodic film/transport peaks and Cu(II) oxidation, not a universally reproducible chloride *E*<sub>pit</sub>. In the examined **10-ppm-sulfide** 70/30 study, the test is a **noncyclic ±250-mV OCP sweep**; in the severe **0.5%-Na₂S** C71500 study the **−525/−404-mV SCE** peaks occur on noncyclic anodic curves. **Neither supplies a verified sulfide-water *E*<sub>pit</sub>, *E*<sub>prot</sub>, or reversal criterion.** Thus no numerical sulfide-polluted-Cu–Ni protection potential should be adopted from these data. Document any anodic feature as “current threshold/film-transition potential” until post-test localization and reverse-sweep behavior support a more specific term. (song2024microstructuresandcorrosion pages 2-5, song2024microstructuresandcorrosion pages 10-13, yuan2007surfacecharacterizationand pages 3-5, gao2022corrosionbehaviorof pages 2-4, gao2022corrosionbehaviorof pages 4-5, kear2004electrochemicalcorrosionbehaviour pages 4-5)

**NAB:** Shahriari and colleagues used **10 mA/cm²** to reverse a WAAM/cast comparison and explicitly found no clear pitting-potential range for most samples. Abreu and colleagues used an **upper fixed potential near +0.75 V SCE** in a broad oxide-redox cycle; Huo and Ding used **noncyclic** polarization. Film oxidation, active-to-pseudopassive transitions and dissolution of specific β′/α–κ regions are *not equivalent* to stainless-steel pit nucleation/repassivation. A “protection potential” based solely on the returning-branch intersection should therefore not be claimed to suppress NAB selective phase corrosion. A useful exploratory cyclic experiment should specify its **absolute reference, initial potential, scan rate, current-density reversal, back-scan endpoint, electrolyte volume, and microscopic attack**; carry it out on **separate sacrificial spots**. (shahriari2023corrosionperformanceof pages 14-14, shahriari2023corrosionperformanceof pages 2-4, abreu2024influenceofdeep pages 4-5, abreu2024influenceofdeep pages 8-10, ding2019evolutionofthe pages 9-12)

**High-anodic-current envelope.** At the aluminum plan’s **1 mA/cm²** reversal, a **0.07–0.13-cm²** spot draws **70–130 µA**. The published **3- and 10-mA/cm²** reversals would draw **0.21–0.39 mA** and **0.70–1.30 mA**, respectively. The broad cast-NAB oxide-redox cycle reaches **order-10-mA/cm²** currents, implying order-mA spot currents. *Numerical oxygen-reduction plateaus and anodic current specifically at **E*<sub>corr</sub> + 300 mV** are not tabulated in the examined primary studies for the proposed static wells; it would be unsound to present a universal value.* Select potentiostat current range to cover **nA–at least several mA** with suitable resolution and check counter-electrode compliance empirically, particularly for the wide −1.5-to-+0.75-V SCE experiment; no manufacturer-specific compliance specification was verified here. (song2024microstructuresandcorrosion pages 2-5, shahriari2023corrosionperformanceof pages 14-14, abreu2024influenceofdeep pages 8-10)

## 3. Service-potential holds, small-well limitations and unresolved evidence

**Add holds, but measure the setpoints first.** A galvanic mixed potential is a property of the *couple plus electrolyte, aeration, surface condition and exposed-area ratio*, not a fixed property of C71500 or C95800. Luo and colleagues directly show that increasing duplex-steel cathode:NAB anode area from 1:1 to **50:1** yields approximately **38 µA/cm²** initially, equivalent to **~2.7–4.9 µA** for an isolated CubXL-sized anode *at the same measured current density*. This **is a galvanic-current benchmark, not a potentiostatic-hold current guarantee**. Obtain the actual steel or titanium mixed potential in a separately wired/zero-resistance-ammeter experiment and reproduce it in short **10–30-min potentiostatic holds** on fresh, independently allocated Cu–Ni/NAB spots. Log signed *i*(t), integrated charge, subsequent OCP and Cu/Ni/Fe/Mn or Cu/Al/Ni/Fe/Mn in recovered solution. Use a **separate bulk connected-couple experiment** when electrical continuity and cathode/anode area are central questions: simply putting both phases within the same well does not reproduce an external 50:1 cathode. (luo2026thegalvaniccorrosion pages 4-6, luo2026thegalvaniccorrosion pages 9-11)

For **NAB propeller cathodic protection**, a negative-potential hold is scientifically relevant, but **these accessible primary results do not establish an exact Ag/AgCl/SCE setpoint that suppresses selective phase corrosion, or its steady current density**. Do **not** re-label generic steel CP criteria or an aluminium-alloy CP measurement as a demonstrated NAB β′/κ suppression threshold. Determine representative in-service propeller potential versus an identified seawater-compatible reference; test a small bracket around it against open-circuit controls, with **post-exposure phase-specific profilometry/SEM and dissolved Al/Cu/Fe/Ni**. A sufficiently negative hold may consume oxygen, raise local pH and eventually generate hydrogen: characterize those responses before assigning a protective range. At near-OCP, Ding and colleagues observed **~500-nm β′ recession within 150 min**, so demonstrating a true suppression claim requires *phase-resolved depth*, not just a low net current. (ding2019evolutionofthe pages 9-12, ding2019evolutionofthe pages 3-6, basumatary2015thesynergisticeffects pages 9-11)

**A 150-µL open well is not a miniature bulk seawater cell.** The cited electrochemistry generally used **~0.28–1 cm²** in bulk electrolyte; Yuan’s study used **500 mL for 0.785 cm²**, whereas the proposed robot supplies **~1.2–2.1 mL/cm²**. Anodic Cu(I) and Al species can accumulate; O₂ supply depends on liquid depth, rim shape and agitation; pH and sulfide speciation can drift; and evaporation changes salinity. Add an **aeration/oxygen and electrolyte-refresh matrix**, measured-before/after pH, temperature and volume, reference-junction and counter-electrode controls, and an O-ring-edge/leak blank. Use independent wells for near-OCP/ICP, cathodic, service-anodic and severe cyclic protocols. After aspirating electrolyte, rinse the well with a measured aliquot and analyze electrolyte **plus rinse**; report element-specific mass per exposed area and duration, recognizing that ICP of *dissolved liquid alone* misses redeposited corrosion product. **No verified study in the retrieved primary set combines powder-DED marine Cu–Ni/NAB repair-zone O-ring measurements with per-spot element-resolved ICP.** That is a defensible *specific research gap*, not a claim that AM-alloy corrosion or automated flat-cell corrosion testing is new. (yuan2007surfacecharacterizationand pages 3-5, song2024microstructuresandcorrosion pages 2-5, shahriari2023corrosionperformanceof pages 14-14, ding2019evolutionofthe pages 3-6, luo2026thegalvaniccorrosion pages 9-11)

### Top 5 changes to the small-cell plan for copper alloys

1. **Replace the default 1-mA/cm² G61 endpoint with a nondestructive first-pass sequence:** registered image → OCP versus a calibrated Ag/AgCl for **30–60 min**, recording drift → **±10-mV LPR with solution-resistance correction** → optional short **OCP EIS** on a separately validated frequency window. Report *R*ₚ and measured impedance separately; do not infer *i*<sub>corr</sub> from an assumed Stern–Geary B. (kear2004electrochemicalcorrosionbehaviour pages 9-10, ding2019evolutionofthe pages 6-9, huo2025modulatingheatinput pages 4-5)
2. **Prioritize fixed-potential, fixed-time anodic and service-potential holds on separate wells.** Record *i*(t), charge, after-images/profiles, and elemental ICP release. Determine steel/titanium mixed potentials with the intended pair and area ratio; determine any NAB CP suppression threshold experimentally instead of assuming one. (luo2026thegalvaniccorrosion pages 4-6, luo2026thegalvaniccorrosion pages 9-11, ding2019evolutionofthe pages 9-12)
3. **Make age and environment explicit experimental factors:** freshly polished versus deliberately prefilmed coupons; 3.5% NaCl versus ASTM D1141 versus natural seawater; controlled dissolved oxygen and, where relevant, separately controlled sulfide. A two-hour screen answers an *early-surface* question, not long-term pipe/propeller life. (yuan2007surfacecharacterizationand pages 3-5, yuan2007surfacecharacterizationand pages 5-8, kear2004electrochemicalcorrosionbehaviour pages 9-10, ding2019evolutionofthe pages 3-6)
4. **Validate the microcell itself before ranking alloys:** repeat bulk-reference comparisons, measure oxygen availability/pH/evaporation, use chemically compatible reference and counter geometry, track seal leakage, recover metal-bearing electrolyte *and rinse*, and size instruments for **nA-to-mA** measured current while verifying voltage compliance on the assembled head. (yuan2007surfacecharacterizationand pages 3-5, song2024microstructuresandcorrosion pages 2-5, abreu2024influenceofdeep pages 8-10, shahriari2023corrosionperformanceof pages 14-14)
5. **Sample microstructure, not merely nominal alloy:** put distinct spots across powder-DED deposit, fusion boundary, HAZ and cast/wrought substrate; include build-direction cuts, tracks/walls and atomization byproducts as *separate* geometries; co-register β′, α/κ and segregation with depth and Cu–Ni–Fe–Mn or Cu–Al–Ni–Fe–Mn release. This differentiates the intended experiment from prior **WAAM** bulk-cell studies and directly interrogates the fast selective attack observed in cast NAB. (song2024microstructuresandcorrosion pages 2-5, shahriari2023corrosionperformanceof pages 14-14, huo2025modulatingheatinput pages 4-5, ding2019evolutionofthe pages 9-12)

References

1. (kear2004electrochemicalcorrosionbehaviour pages 4-5): G. Kear, B.D. Barker, K. Stokes, and F.C. Walsh. Electrochemical corrosion behaviour of 90—10 cu—ni alloy in chloride-based electrolytes. Journal of Applied Electrochemistry, 34:659-669, Jul 2004. URL: https://doi.org/10.1023/b:jach.0000031164.32520.58, doi:10.1023/b:jach.0000031164.32520.58. This article has 238 citations and is from a peer-reviewed journal.

2. (kear2004electrochemicalcorrosionbehaviour pages 6-7): G. Kear, B.D. Barker, K. Stokes, and F.C. Walsh. Electrochemical corrosion behaviour of 90—10 cu—ni alloy in chloride-based electrolytes. Journal of Applied Electrochemistry, 34:659-669, Jul 2004. URL: https://doi.org/10.1023/b:jach.0000031164.32520.58, doi:10.1023/b:jach.0000031164.32520.58. This article has 238 citations and is from a peer-reviewed journal.

3. (ding2019evolutionofthe pages 6-9): Yang Ding, Ronggen Zhao, Zhen-bo Qin, Zhong Wu, Liqiang Wang, Lei Liu, and Weijie Lu. Evolution of the corrosion product film on nickel-aluminum bronze and its corrosion behavior in 3.5 wt % nacl solution. Materials, 12:209, Jan 2019. URL: https://doi.org/10.3390/ma12020209, doi:10.3390/ma12020209. This article has 60 citations.

4. (shahriari2023corrosionperformanceof pages 2-4): Ayda Shahriari, Dharmendra Chalasani, Babak Shalchi Amirkhiz, and Mohsen Mohammadi. Corrosion performance of wire arc additively manufactured nab alloy. npj Materials Degradation, 7:1-15, Oct 2023. URL: https://doi.org/10.1038/s41529-023-00405-x, doi:10.1038/s41529-023-00405-x. This article has 30 citations and is from a peer-reviewed journal.

5. (yuan2007surfacecharacterizationand pages 3-5): S.J. Yuan and S.O. Pehkonen. Surface characterization and corrosion behavior of 70/30 cu-ni alloy in pristine and sulfide-containing simulated seawater. Corrosion Science, 49:1276-1304, Mar 2007. URL: https://doi.org/10.1016/j.corsci.2006.07.003, doi:10.1016/j.corsci.2006.07.003. This article has 298 citations and is from a highest quality peer-reviewed journal.

6. (kear2004electrochemicalcorrosionbehaviour pages 9-10): G. Kear, B.D. Barker, K. Stokes, and F.C. Walsh. Electrochemical corrosion behaviour of 90—10 cu—ni alloy in chloride-based electrolytes. Journal of Applied Electrochemistry, 34:659-669, Jul 2004. URL: https://doi.org/10.1023/b:jach.0000031164.32520.58, doi:10.1023/b:jach.0000031164.32520.58. This article has 238 citations and is from a peer-reviewed journal.

7. (abreu2024influenceofdeep pages 4-5): Carmen M. Abreu, Iria Feijoo, Gloria Pena, and M. Consuelo Pérez. Influence of deep cryogenic treatment on the mechanical properties and corrosion resistance of nickel–aluminum bronze. Corrosion and Materials Degradation, 5:624-640, Dec 2024. URL: https://doi.org/10.3390/cmd5040030, doi:10.3390/cmd5040030. This article has 1 citations.

8. (yuan2007surfacecharacterizationand pages 5-8): S.J. Yuan and S.O. Pehkonen. Surface characterization and corrosion behavior of 70/30 cu-ni alloy in pristine and sulfide-containing simulated seawater. Corrosion Science, 49:1276-1304, Mar 2007. URL: https://doi.org/10.1016/j.corsci.2006.07.003, doi:10.1016/j.corsci.2006.07.003. This article has 298 citations and is from a highest quality peer-reviewed journal.

9. (yuan2007surfacecharacterizationand pages 8-11): S.J. Yuan and S.O. Pehkonen. Surface characterization and corrosion behavior of 70/30 cu-ni alloy in pristine and sulfide-containing simulated seawater. Corrosion Science, 49:1276-1304, Mar 2007. URL: https://doi.org/10.1016/j.corsci.2006.07.003, doi:10.1016/j.corsci.2006.07.003. This article has 298 citations and is from a highest quality peer-reviewed journal.

10. (yuan2007surfacecharacterizationand pages 26-29): S.J. Yuan and S.O. Pehkonen. Surface characterization and corrosion behavior of 70/30 cu-ni alloy in pristine and sulfide-containing simulated seawater. Corrosion Science, 49:1276-1304, Mar 2007. URL: https://doi.org/10.1016/j.corsci.2006.07.003, doi:10.1016/j.corsci.2006.07.003. This article has 298 citations and is from a highest quality peer-reviewed journal.

11. (gao2022corrosionbehaviorof pages 2-4): Xin Gao and Ming Liu. Corrosion behavior of high-strength c71500 copper-nickel alloy in simulated seawater with high concentration of sulfide. Materials, 15:8513, Nov 2022. URL: https://doi.org/10.3390/ma15238513, doi:10.3390/ma15238513. This article has 34 citations.

12. (gao2022corrosionbehaviorof pages 4-5): Xin Gao and Ming Liu. Corrosion behavior of high-strength c71500 copper-nickel alloy in simulated seawater with high concentration of sulfide. Materials, 15:8513, Nov 2022. URL: https://doi.org/10.3390/ma15238513, doi:10.3390/ma15238513. This article has 34 citations.

13. (gao2022corrosionbehaviorof pages 6-8): Xin Gao and Ming Liu. Corrosion behavior of high-strength c71500 copper-nickel alloy in simulated seawater with high concentration of sulfide. Materials, 15:8513, Nov 2022. URL: https://doi.org/10.3390/ma15238513, doi:10.3390/ma15238513. This article has 34 citations.

14. (song2024microstructuresandcorrosion pages 2-5): Jie Song, Xavier A. Jimenez, Albert C. To, and Yao Fu. Microstructures and corrosion properties of wire arc additive manufactured copper–nickel alloys. Materials, 17:876, Feb 2024. URL: https://doi.org/10.3390/ma17040876, doi:10.3390/ma17040876. This article has 11 citations.

15. (song2024microstructuresandcorrosion pages 10-13): Jie Song, Xavier A. Jimenez, Albert C. To, and Yao Fu. Microstructures and corrosion properties of wire arc additive manufactured copper–nickel alloys. Materials, 17:876, Feb 2024. URL: https://doi.org/10.3390/ma17040876, doi:10.3390/ma17040876. This article has 11 citations.

16. (song2024microstructuresandcorrosion pages 14-17): Jie Song, Xavier A. Jimenez, Albert C. To, and Yao Fu. Microstructures and corrosion properties of wire arc additive manufactured copper–nickel alloys. Materials, 17:876, Feb 2024. URL: https://doi.org/10.3390/ma17040876, doi:10.3390/ma17040876. This article has 11 citations.

17. (ding2019evolutionofthe pages 1-3): Yang Ding, Ronggen Zhao, Zhen-bo Qin, Zhong Wu, Liqiang Wang, Lei Liu, and Weijie Lu. Evolution of the corrosion product film on nickel-aluminum bronze and its corrosion behavior in 3.5 wt % nacl solution. Materials, 12:209, Jan 2019. URL: https://doi.org/10.3390/ma12020209, doi:10.3390/ma12020209. This article has 60 citations.

18. (ding2019evolutionofthe pages 3-6): Yang Ding, Ronggen Zhao, Zhen-bo Qin, Zhong Wu, Liqiang Wang, Lei Liu, and Weijie Lu. Evolution of the corrosion product film on nickel-aluminum bronze and its corrosion behavior in 3.5 wt % nacl solution. Materials, 12:209, Jan 2019. URL: https://doi.org/10.3390/ma12020209, doi:10.3390/ma12020209. This article has 60 citations.

19. (ding2019evolutionofthe pages 9-12): Yang Ding, Ronggen Zhao, Zhen-bo Qin, Zhong Wu, Liqiang Wang, Lei Liu, and Weijie Lu. Evolution of the corrosion product film on nickel-aluminum bronze and its corrosion behavior in 3.5 wt % nacl solution. Materials, 12:209, Jan 2019. URL: https://doi.org/10.3390/ma12020209, doi:10.3390/ma12020209. This article has 60 citations.

20. (shahriari2023corrosionperformanceof pages 14-14): Ayda Shahriari, Dharmendra Chalasani, Babak Shalchi Amirkhiz, and Mohsen Mohammadi. Corrosion performance of wire arc additively manufactured nab alloy. npj Materials Degradation, 7:1-15, Oct 2023. URL: https://doi.org/10.1038/s41529-023-00405-x, doi:10.1038/s41529-023-00405-x. This article has 30 citations and is from a peer-reviewed journal.

21. (shahriari2023corrosionperformanceof pages 12-14): Ayda Shahriari, Dharmendra Chalasani, Babak Shalchi Amirkhiz, and Mohsen Mohammadi. Corrosion performance of wire arc additively manufactured nab alloy. npj Materials Degradation, 7:1-15, Oct 2023. URL: https://doi.org/10.1038/s41529-023-00405-x, doi:10.1038/s41529-023-00405-x. This article has 30 citations and is from a peer-reviewed journal.

22. (huo2025modulatingheatinput pages 4-5): Renjie Huo, Zheying Wang, Mingsheng Wang, Rui Wang, Song Zhang, Chunhua Zhang, Chenliang Wu, Haitao Chen, and Jiang Chen. Modulating heat input to optimize corrosion resistance of nickel–aluminum bronze manufactured by cold metal transfer additive manufacturing. Materials, 18:2205, May 2025. URL: https://doi.org/10.3390/ma18102205, doi:10.3390/ma18102205. This article has 5 citations.

23. (huo2025modulatingheatinput pages 10-13): Renjie Huo, Zheying Wang, Mingsheng Wang, Rui Wang, Song Zhang, Chunhua Zhang, Chenliang Wu, Haitao Chen, and Jiang Chen. Modulating heat input to optimize corrosion resistance of nickel–aluminum bronze manufactured by cold metal transfer additive manufacturing. Materials, 18:2205, May 2025. URL: https://doi.org/10.3390/ma18102205, doi:10.3390/ma18102205. This article has 5 citations.

24. (huo2025modulatingheatinput pages 13-15): Renjie Huo, Zheying Wang, Mingsheng Wang, Rui Wang, Song Zhang, Chunhua Zhang, Chenliang Wu, Haitao Chen, and Jiang Chen. Modulating heat input to optimize corrosion resistance of nickel–aluminum bronze manufactured by cold metal transfer additive manufacturing. Materials, 18:2205, May 2025. URL: https://doi.org/10.3390/ma18102205, doi:10.3390/ma18102205. This article has 5 citations.

25. (abreu2024influenceofdeep pages 2-4): Carmen M. Abreu, Iria Feijoo, Gloria Pena, and M. Consuelo Pérez. Influence of deep cryogenic treatment on the mechanical properties and corrosion resistance of nickel–aluminum bronze. Corrosion and Materials Degradation, 5:624-640, Dec 2024. URL: https://doi.org/10.3390/cmd5040030, doi:10.3390/cmd5040030. This article has 1 citations.

26. (abreu2024influenceofdeep pages 8-10): Carmen M. Abreu, Iria Feijoo, Gloria Pena, and M. Consuelo Pérez. Influence of deep cryogenic treatment on the mechanical properties and corrosion resistance of nickel–aluminum bronze. Corrosion and Materials Degradation, 5:624-640, Dec 2024. URL: https://doi.org/10.3390/cmd5040030, doi:10.3390/cmd5040030. This article has 1 citations.

27. (tan2024effectofalni pages 2-4): Yinxun Tan, Haofeng Xie, Xue Feng, Shuhui Huang, Wenjing Zhang, Lijun Peng, Wanyu Wang, and Yizhi Zhao. Effect of al/ni ratio on the microstructure and properties of nickel–aluminum bronze alloys. Materials, 17:1330, Mar 2024. URL: https://doi.org/10.3390/ma17061330, doi:10.3390/ma17061330. This article has 14 citations.

28. (tan2024effectofalni pages 4-6): Yinxun Tan, Haofeng Xie, Xue Feng, Shuhui Huang, Wenjing Zhang, Lijun Peng, Wanyu Wang, and Yizhi Zhao. Effect of al/ni ratio on the microstructure and properties of nickel–aluminum bronze alloys. Materials, 17:1330, Mar 2024. URL: https://doi.org/10.3390/ma17061330, doi:10.3390/ma17061330. This article has 14 citations.

29. (tan2024effectofalni pages 10-12): Yinxun Tan, Haofeng Xie, Xue Feng, Shuhui Huang, Wenjing Zhang, Lijun Peng, Wanyu Wang, and Yizhi Zhao. Effect of al/ni ratio on the microstructure and properties of nickel–aluminum bronze alloys. Materials, 17:1330, Mar 2024. URL: https://doi.org/10.3390/ma17061330, doi:10.3390/ma17061330. This article has 14 citations.

30. (roberge1988behaviorofthe pages 1-2): Pierre R. Roberge and R�jean Beaudoin. Behavior of the corrosion potential and corrosion current of cu-ni alloys under erosion corrosion conditions. effect of oxygen. Journal of Applied Electrochemistry, 18:601-607, Jul 1988. URL: https://doi.org/10.1007/bf01022257, doi:10.1007/bf01022257. This article has 32 citations and is from a peer-reviewed journal.

31. (roberge1988behaviorofthe pages 2-3): Pierre R. Roberge and R�jean Beaudoin. Behavior of the corrosion potential and corrosion current of cu-ni alloys under erosion corrosion conditions. effect of oxygen. Journal of Applied Electrochemistry, 18:601-607, Jul 1988. URL: https://doi.org/10.1007/bf01022257, doi:10.1007/bf01022257. This article has 32 citations and is from a peer-reviewed journal.

32. (roberge1988behaviorofthe pages 3-5): Pierre R. Roberge and R�jean Beaudoin. Behavior of the corrosion potential and corrosion current of cu-ni alloys under erosion corrosion conditions. effect of oxygen. Journal of Applied Electrochemistry, 18:601-607, Jul 1988. URL: https://doi.org/10.1007/bf01022257, doi:10.1007/bf01022257. This article has 32 citations and is from a peer-reviewed journal.

33. (luo2026thegalvaniccorrosion pages 3-4): Kun Luo, Pu Zhao, Ke-Wei Fang, Wan-Xiang Zhao, Jiachang Lu, Hong-Qun Liu, Shui-Yong Wang, Mengmeng Zhu, and Y.-X. Qiao. The galvanic corrosion behavior of zcual10fe5ni5 coupled with saf2507 duplex stainless steel in seawater. Metals, 16:473, Apr 2026. URL: https://doi.org/10.3390/met16050473, doi:10.3390/met16050473. This article has 0 citations.

34. (luo2026thegalvaniccorrosion pages 4-6): Kun Luo, Pu Zhao, Ke-Wei Fang, Wan-Xiang Zhao, Jiachang Lu, Hong-Qun Liu, Shui-Yong Wang, Mengmeng Zhu, and Y.-X. Qiao. The galvanic corrosion behavior of zcual10fe5ni5 coupled with saf2507 duplex stainless steel in seawater. Metals, 16:473, Apr 2026. URL: https://doi.org/10.3390/met16050473, doi:10.3390/met16050473. This article has 0 citations.

35. (luo2026thegalvaniccorrosion pages 9-11): Kun Luo, Pu Zhao, Ke-Wei Fang, Wan-Xiang Zhao, Jiachang Lu, Hong-Qun Liu, Shui-Yong Wang, Mengmeng Zhu, and Y.-X. Qiao. The galvanic corrosion behavior of zcual10fe5ni5 coupled with saf2507 duplex stainless steel in seawater. Metals, 16:473, Apr 2026. URL: https://doi.org/10.3390/met16050473, doi:10.3390/met16050473. This article has 0 citations.

36. (kear2004electrochemicalcorrosionbehaviour pages 1-2): G. Kear, B.D. Barker, K. Stokes, and F.C. Walsh. Electrochemical corrosion behaviour of 90—10 cu—ni alloy in chloride-based electrolytes. Journal of Applied Electrochemistry, 34:659-669, Jul 2004. URL: https://doi.org/10.1023/b:jach.0000031164.32520.58, doi:10.1023/b:jach.0000031164.32520.58. This article has 238 citations and is from a peer-reviewed journal.

37. (kear2004electrochemicalcorrosionbehaviour pages 5-6): G. Kear, B.D. Barker, K. Stokes, and F.C. Walsh. Electrochemical corrosion behaviour of 90—10 cu—ni alloy in chloride-based electrolytes. Journal of Applied Electrochemistry, 34:659-669, Jul 2004. URL: https://doi.org/10.1023/b:jach.0000031164.32520.58, doi:10.1023/b:jach.0000031164.32520.58. This article has 238 citations and is from a peer-reviewed journal.

38. (song2013comparisonofcorrosion pages 4-8): Q. Song, Yingkui Zheng, Shenglin Jiang, D. Ni, and Zhi Ma. Comparison of corrosion and cavitation erosion behaviors between the as-cast and friction-stir-processed nickel aluminum bronze. Jul 2013. URL: https://doi.org/10.5006/0984, doi:10.5006/0984. This article has 63 citations and is from a peer-reviewed journal.

39. (song2013comparisonofcorrosion pages 8-12): Q. Song, Yingkui Zheng, Shenglin Jiang, D. Ni, and Zhi Ma. Comparison of corrosion and cavitation erosion behaviors between the as-cast and friction-stir-processed nickel aluminum bronze. Jul 2013. URL: https://doi.org/10.5006/0984, doi:10.5006/0984. This article has 63 citations and is from a peer-reviewed journal.

40. (basumatary2015thesynergisticeffects pages 9-11): J. Basumatary, M. Nie, and R. J. K. Wood. The synergistic effects of cavitation erosion–corrosion in ship propeller materials. Journal of Bio- and Tribo-Corrosion, 1:1-12, Mar 2015. URL: https://doi.org/10.1007/s40735-015-0012-1, doi:10.1007/s40735-015-0012-1. This article has 80 citations and is from a peer-reviewed journal.
