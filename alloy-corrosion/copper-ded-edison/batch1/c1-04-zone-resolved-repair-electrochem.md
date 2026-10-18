<!--
Edison Scientific LITERATURE task (batch 1)
- Task ID: 8615ce8a-6a59-4dd1-b44c-7e3fc3b832b3
- Submitted: 2026-10-18T01:20:03Z
- Fetched: 2026-10-18T01:50:04Z (status: success)
- Raw trajectory JSON: ../raw/c1-04-zone-resolved-repair-electrochem.json.gz
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

QUESTION: How do the deposit, fusion boundary, heat-affected zone and
substrate of welded, laser-clad, friction-stir-processed or additively
repaired NAB and Cu-Ni differ electrochemically in chloride or seawater, as
measured by spatially resolved methods (microcapillary cell, scanning droplet
cell, SVET, SECM, SKPFM/Volta potential, local EIS) or by masked
macro-specimens? Report the potential and current differences between zones,
the microstructural features responsible (kappa phases, retained beta or
martensite, interdendritic Ni depletion, interlayer bands, dilution from the
substrate), and the size of each feature compared with a 3-4 mm measurement
spot and with a DED track (about 1 mm wide, 0.2-0.5 mm layers). Report
galvanic coupling between a deposit and its substrate (ZRA, mixed-potential
or area-ratio studies): galvanic current densities and which member is
anodic. Recommend how to place wells on a polished cross-section of a repair
coupon, and say whether a 3-4 mm well averages over features that matter.

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

QUESTION: How do the deposit, fusion boundary, heat-affected zone and
substrate of welded, laser-clad, friction-stir-processed or additively
repaired NAB and Cu-Ni differ electrochemically in chloride or seawater, as
measured by spatially resolved methods (microcapillary cell, scanning droplet
cell, SVET, SECM, SKPFM/Volta potential, local EIS) or by masked
macro-specimens? Report the potential and current differences between zones,
the microstructural features responsible (kappa phases, retained beta or
martensite, interdendritic Ni depletion, interlayer bands, dilution from the
substrate), and the size of each feature compared with a 3-4 mm measurement
spot and with a DED track (about 1 mm wide, 0.2-0.5 mm layers). Report
galvanic coupling between a deposit and its substrate (ZRA, mixed-potential
or area-ratio studies): galvanic current densities and which member is
anodic. Recommend how to place wells on a polished cross-section of a repair
coupon, and say whether a 3-4 mm well averages over features that matter.

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


# Local corrosion of repaired naval copper alloys: evidence and test implications

**Bottom line.** The clearest measured *repair-zone galvanic* result is for a 90–10 Cu–Ni arc weld: its heat-affected zone (HAZ) was anodic to the Ni-rich weld, with an initial coupled current of **4.43 µA cm⁻²** in seawater flowing at 5 m s⁻¹. For NAB, the literature establishes corrosion-sensitive weld microstructures and strong effects of deposition dilution, but the accessible studies do **not** supply an equivalent zone-by-zone, matched-alloy laser-DED repair map or a measured deposit–cast-NAB galvanic current. Air-measured Volta contrasts must not be substituted for aqueous electrode-potential differences. (xing2023characterizationofcorrosion pages 9-12, zhao2020effectofweld pages 1-4, zhao2022thelaserdeposited pages 7-10, iannuzzi2017unusualcorrelationbetween pages 4-6)

The table gives the experimental specifications and numerical benchmarks. **NR** means that the cited study did not report the quantity; in particular, electrolyte *volume* is unavailable for most bulk-cell studies. Areas and volumes in this table describe the published experiments, **not** the proposed wells. The cited figures show the Cu–Ni weld's zone comparison, air-potential map and coupled-current history. (xing2023characterizationofcorrosion media 9ceaa802, xing2023characterizationofcorrosion media c0dc77ed, xing2023characterizationofcorrosion media 4f4b1c2c)

| Paper / DOI | Material, process, composition (wt%) | Cell area; volume | Electrolyte; duration | Exact metric | Limitation |
|---|---|---|---|---|---|
| Xing et al., *Metals* 13 (2023) 294; [10.3390/met13020294](https://doi.org/10.3390/met13020294) | TIG-welded 90–10 Cu–Ni: Ni 9–11, Fe 1.5–1.8, Mn 0.5–1.0, Cu balance. Filler: Ni 28–33, Ti 0.2–0.5, Fe 0.4–0.75, Mn 0.5–1.0, Cu balance. (xing2023characterizationofcorrosion pages 1-2) | Ø10 mm face = 0.785 cm²; volume NR. Ag/AgCl reference. Original HAZ:WZ ZRA at 1:1 area ratio. (xing2023characterizationofcorrosion pages 2-5) | Seawater, 20 ± 0.5 °C, 0–5 m/s; EIS and galvanic monitoring for 30 d. | **Air SKP, not solution Ecorr:** WZ ≈ −80 mV, HAZ ≈ −160 mV; HAZ anodic. **Original ZRA:** initial galvanic current reached 4.43 µA/cm² at 5 m/s and approached zero after ≈3 d. WZ had the greatest mature corrosion resistance and HAZ the least; all exceeded 1.4 × 10⁴ Ω·cm² at 20–30 d. HAZ pit depths after 30 d were 7, 6, and 4 µm at 1, 3, and 5 m/s. WZ grains were 15–25 µm; some HAZ grains exceeded 100 µm. (xing2023characterizationofcorrosion pages 9-12, xing2023characterizationofcorrosion pages 2-5) | Not 70–30 Cu–Ni or laser DED. SKP work potential is not an aqueous electrode potential. Volume and elemental dissolution were not reported. |
| Zhao et al., *Metals* 10 (2020) 1227; [10.3390/met10091227](https://doi.org/10.3390/met10091227) | Cast UNS C95810 NAB weld repair. Defect-free: Cu 79.9, Al 9.24, Fe 4.8, Ni 4.43, Mn 1.39. Weld-repaired: Cu 81.9, Al 8.66, Fe 3.4, Ni 4.2, Mn 1.52. Filler: Cu 85.66, Al 8.5, Fe 1.9, Ni 2.06, Mn 1.85. Repaired material contained retained beta-prime. (zhao2020effectofweld pages 1-4) | Electrochemistry 0.38 cm²; immersion specimens nominally 1 cm²; volume NR. Pt mesh and SCE. (zhao2020effectofweld pages 1-4) | Naturally aerated 3.5% NaCl, pH 6.9, renewed weekly; 3–432 h. | Weld repair increased dissolution and produced a more porous early film. Before 168 h, repaired NAB had lower fitted film and charge-transfer resistance than defect-free NAB; the ranking reversed by 432 h as a thicker repair film developed. (zhao2020effectofweld pages 4-8, zhao2020effectofweld pages 11-14) | Masked macro-specimen containing the weld, not separate deposit, fusion-zone, HAZ, and substrate cells. No ZRA, local EIS, numerical zone polarity, pit depth, or volume. |
| Zhao et al., *Metals* 12 (2022) 781; [10.3390/met12050781](https://doi.org/10.3390/met12050781) | Blown-powder laser deposition of NAB powder, Cu 81.1, Al 10.8, Ni 4.1, Fe 4.0, on SUS630 steel: N-1 direct; N-2 with 0.6–0.8 mm Ni–5Fe interlayer; N-3 with Ni–20Cr interlayer. NAB layer 1.6–1.8 mm. Direct deposition raised upper-layer Fe to 11.2 wt% through dilution. (zhao2022thelaserdeposited pages 4-7, zhao2022thelaserdeposited pages 2-4) | Bulk flat cell, 1.00 ± 0.01 cm²; volume NR. Ag/AgCl saturated-KCl reference and 4 cm² Pt counter. (zhao2022thelaserdeposited pages 2-4) | 3.5 wt% NaCl, 25 ± 5 °C; 20 min before polarization; immersion and EIS through 21 d. | Versus Ag/AgCl: N-1 Ecorr −248 mV, icorr 7.82 µA/cm², Rp 2810 Ω·cm²; N-2 −255 mV, 4.65 µA/cm², 5275 Ω·cm²; N-3 −252 mV, 4.09 µA/cm², 4865 Ω·cm². At 21 d, maximum attack depths were 3.4 ± 0.1, 2.0 ± 0.1, and 1.8 ± 0.1 µm; Rct values were 1.44, 51.47, and 85.10 kΩ·cm². N-1 Fe-rich dendrites, locally 56.1 wt% Fe, dissolved preferentially. (zhao2022thelaserdeposited pages 7-10, zhao2022thelaserdeposited pages 10-13, zhao2022thelaserdeposited pages 13-14) | Directly relevant laser DED, but on stainless steel rather than cast NAB or wrought Cu–Ni. Top surfaces, not repair cross-sections, were tested. No ZRA; icorr and Rp rely on Tafel and Stern–Geary analysis. |
| Iannuzzi, Vasanth, and Frankel, *J. Electrochem. Soc.* 164 (2017) C488–C497; [10.1149/2.0391709jes](https://doi.org/10.1149/2.0391709jes) | Rolled UNS C63200 NAB: Ni 4.0–4.8, Al 8.7–9.5, Fe 3.5–4.3, Mn 1.2–2.0, Cu balance; as-received and annealed 1 h at 927 °C. Kappa-II was 2–3 µm as received and 4–6 µm after heat treatment. (iannuzzi2017unusualcorrelationbetween pages 3-4, iannuzzi2017unusualcorrelationbetween pages 2-3) | SKPFM maps 80 × 80 µm, 512 × 512 pixels, 100 nm lift height; coupons ≈1 × 1 cm; wetted area and volume NR. (iannuzzi2017unusualcorrelationbetween pages 3-4, iannuzzi2017unusualcorrelationbetween pages 2-3) | 0.5 M NaCl, pH 6, for 1–24 h; 0.5 M NaCl plus 10 vol% ammonia, pH 12.2, for 15–105 min; separate Na₂SO₄ polarization. | **Air SKPFM Volta values, not solution Ecorr:** polished alpha −620 mV versus Ni calibration, kappa-II −564 mV, kappa-III −605 mV. Despite the apparent +56 and +15 mV contrasts, the higher-Volta alpha matrix dissolved preferentially in chloride while kappa phases remained intact. Separate Na₂SO₄ OCP was ≈−250 mV SCE; imposed polarization produced +200 or −58 µA. (iannuzzi2017unusualcorrelationbetween pages 6-8, iannuzzi2017unusualcorrelationbetween pages 4-6) | Not a repair coupon. No weld-zone comparison, local current map, Rp, icorr, or ZRA. Ex-situ SKPFM cannot be treated as direct aqueous nobility. |
| Song et al., *Corrosion* 69 (2013) 1111–1121; [10.5006/0984](https://doi.org/10.5006/0984) | Cast UNS C95800 NAB: Al 9.18, Ni 4.49, Fe 4.06, Mn 1.03, Cu balance; friction-stir processed at 1200 rpm and 50 mm/min. Cast Widmanstätten alpha exceeded 100 µm; FSP alpha was below 20 µm, ≈10 µm equiaxed, and 3–4 µm in stream-like regions. (song2013comparisonofcorrosion pages 4-8) | Bulk flat cell, 0.49 cm²; volume NR. Pt counter and SCE. (song2013comparisonofcorrosion pages 4-8) | 3.5 wt% NaCl at ≈20 °C; solution renewed weekly; EIS immersion to 82 d. Separate 20 kHz cavitation tests. | After 10 d, the FSP-zone Nyquist diameter was approximately one order of magnitude above cast NAB. Cavitation shifted OCP active by ≈80 mV for cast NAB and ≈100 mV for FSP NAB. After 16 h cavitation in NaCl, mass losses were 33.4 mg cast versus 15.9 mg FSP; after 20 h, cavities were over 150 µm deep in cast NAB versus below 10 µm in FSP NAB. (song2013comparisonofcorrosion pages 12-15, song2013comparisonofcorrosion pages 8-12) | FSP center and cast substrate were separate macro-electrodes; the FSP boundary and HAZ were not mapped. No ZRA or local electrochemistry. Cavitation results do not represent a quiescent one-hour well. |
| Huo et al., *Materials* 18 (2025) 2205; [10.3390/ma18102205](https://doi.org/10.3390/ma18102205) | CMT wire-arc AM C63280 from pre-alloyed ERCuNiAl wire: Al 8.73, Fe 5.90, Ni 4.52, Mn 1.39, Si 0.058, Pb 0.005, Zn 0.002, Cu balance; heat input 243.8–644.7 J/mm. Grain size increased 38.26→74.62 µm; kappa phases coarsened from submicron to micron or tens-of-microns scale. (huo2025modulatingheatinput pages 5-7, huo2025modulatingheatinput pages 7-10, huo2025modulatingheatinput pages 4-5) | Bulk flat cell, 1 cm²; volume NR. Pt foil and SCE. (huo2025modulatingheatinput pages 4-5) | Aerated 3.5 wt% NaCl, 25 ± 5 °C; OCP 3600 s before EIS and another 1800 s before polarization. | S1→S4 one-hour OCP was approximately −237, −274, −391, and −421 mV SCE. Polarization-derived potentials were −269.61 ± 40, −466.62 ± 10, −517.77 ± 20, and −700.94 ± 15 mV; icorr was 2.56 ± 0.04, 3.85 ± 0.11, 5.03 ± 0.08, and 7.52 ± 0.07 µA/cm². Unambiguous EIS endpoints: Rct fell 2485→707 Ω·cm² and film resistance 1152→185.8 Ω·cm². (huo2025modulatingheatinput pages 10-13, huo2025modulatingheatinput pages 13-15) | WAAM/CMT, not laser DED or matched-substrate repair. An intermediate EIS row is mislabelled S2, so no intermediate resistance assignment is inferred. No zone resolution, ZRA, or volume. |
| Krogstad, Johnsen, and Coey, *Corrosion* 74 (2018) 197–209; [10.5006/2531](https://doi.org/10.5006/2531) | Cast UNS C95800 NAB: Cu 80.5, Al 9.4, Ni 5.0, Fe 4.3, Mn 0.7. Rotating-disk and magnetic-field forced-convection experiments, not repair. (krogstad2018effectofa pages 3-4) | RDE: Ø10 mm = 0.785 cm² in 1 L. Magnetic cell: Ø28 mm nominal face = 6.16 cm² in 0.2 L. Pt counter and saturated Ag/AgCl. (krogstad2018effectofa pages 3-4, krogstad2018effectofa pages 4-6) | 3.5 wt% NaCl, pH 6.3–6.6, 22 ± 2 °C; fresh surfaces exposed no more than 30 min before testing; ≈1 h potentiostatic tests. | OCP ≈−210 ± 7 mV Ag/AgCl. At −180 mV, 0→800 rpm raised anodic current from 0.103 to 2.023 A/m²; at −25 mV, from 28.5 to 71.3 A/m². An 800 mT field increased current by as much as 52%. **Secondary quotation, not this paper’s original ZRA:** earlier NAB–stainless-steel seawater work reportedly gave a mixed potential of ≈−50 mV Ag/AgCl and 0.06–11 A/m², strongly dependent on area ratio. (krogstad2018effectofa pages 1-2, krogstad2018effectofa pages 7-8) | Direct results quantify convection sensitivity, not repair galvanism. The NAB–steel range is a secondary quotation and cannot replace original matched-area ZRA data. No verified Cu–Ni DED evidence. |


*Table: Seven directly inspected studies are compared by alloy, process, cell geometry, exposure, and quantitative electrochemical result. The table separates aqueous potentials and original ZRA measurements from air SKP/SKPFM values and secondary galvanic quotations.*

## Interpretation and relevance of each item

1. **[CITE] [NUMBERS] [NAVY] [CUBXL]** Xing, S., Bai, S., Liu, R., Liu, Y., Qi, J., Hou, J., and Zhang, D. “Characterization of Corrosion Behavior and Corrosion Production Property of 90-10 Cupronickel Welding Joints in Flowing Seawater.” *Metals* **13** (2023): 294. **DOI: 10.3390/met13020294.** This is TIG-welded, nominal 90–10 Cu–Ni with **Ni 9–11, Fe 1.5–1.8, Mn 0.5–1.0 wt%; Cu balance**, joined using substantially more Ni-rich filler (**Ni 28–33 wt%; Cu balance**). Individually cut parent, HAZ and weld electrodes had 10-mm-diameter working faces; the flowing-seawater apparatus used Ag/AgCl, at 20 ± 0.5 °C for up to 30 days; electrolyte volume was **NR**. Its 14 × 6 mm air scanning-Kelvin-probe survey, at 300 µm steps, gave roughly **−160 mV HAZ versus −80 mV weld**, a **roughly 80 mV *air-work-potential* contrast**, *not* two measured solution *E*corr values. At equal exposed areas, direct HAZ–weld galvanic measurement identified the **HAZ as anode**; current initially reached **4.43 µA cm⁻² at 5 m s⁻¹** and approached zero after approximately three days as films developed. At 20–30 days, EIS-derived resistance ranked **weld > parent > HAZ** in flowing seawater; all zones exceeded **1.4 × 10⁴ Ω cm²**. HAZ pits after 30 days measured **7, 6 and 4 µm** deep at 1, 3 and 5 m s⁻¹, respectively. Weld grains measured **15–25 µm**, whereas some HAZ grains exceeded **100 µm**. **CubXL implication:** measure fresh-zone polarity *and* aged-film behavior; do not transfer the sign or magnitude to a same-composition Cu–Ni DED repair, which lacks this strongly Ni-rich filler. (xing2023characterizationofcorrosion pages 1-2, xing2023characterizationofcorrosion pages 2-5, xing2023characterizationofcorrosion pages 9-12)

2. **[CITE] [NUMBERS] [NAVY] [CUBXL]** Zhao, X., Qi, Y., Wang, J., Peng, T., Zhang, Z., and Li, K. “Effect of Weld and Surface Defects on the Corrosion Behavior of Nickel Aluminum Bronze in 3.5% NaCl Solution.” *Metals* **10** (2020): 1227. **DOI: 10.3390/met10091227.** These were cast **UNS C95810** coupons, including a weld-repaired coupon—not separate electrically isolated zones. The sound casting was **Cu 79.9, Al 9.24, Fe 4.8, Ni 4.43, Mn 1.39 wt%**; the repaired specimen measured **Cu 81.9, Al 8.66, Fe 3.4, Ni 4.2, Mn 1.52 wt%**, with lower-Ni/lower-Fe welding wire (**Cu 85.66, Al 8.5, Fe 1.9, Ni 2.06, Mn 1.85 wt%**). Unlike the sound casting, repaired metal contained **retained β′**. Electrochemistry used a **0.38 cm²** exposed working area, Pt mesh, SCE and 3.5% NaCl at **pH 6.9**; separate gravimetric specimens exposed **1 cm²**. Solution was renewed weekly; observations extended from **3 to 432 h**; cell volume was **NR**. Weld repair accelerated loss and had a poorer, more porous early film: fitted film and charge-transfer resistances were initially lower than for sound casting, but reversed at late times as corrosion products accumulated. No extractable numerical zone-specific *E*corr, *R*p, *i*corr, ZRA current or pit depth was reported. **CubXL implication:** a late high impedance does not negate earlier dissolution; record time and used-electrolyte chemistry separately. The study received equipment pre-research funding, but it is **not** a measured weld/HAZ galvanic-polarity study. (zhao2020effectofweld pages 1-4, zhao2020effectofweld pages 4-8, zhao2020effectofweld pages 11-14)

3. **[CITE] [NUMBERS] [CUBXL] [NOVELTY-RISK]** Zhao, L., Li, K., Yao, J., Yuan, Y., and Du, B. “The Laser Deposited Nickel-Aluminum Bronze Coatings on SUS630 Stainless Steel and Its Corrosion Resistance in 3.5 wt.% NaCl Solution.” *Metals* **12** (2022): 781. **DOI: 10.3390/met12050781.** **Pre-alloyed blown-powder laser deposition**, rather than in-situ blending, used powder **Cu 81.1, Al 10.8, Ni 4.1, Fe 4.0 wt%** and compared direct NAB-on-17-4PH-steel deposition with **Ni–5Fe** and **Ni–20Cr** intervening layers. This was **2,400 W**, a **3.2-mm laser spot**, a **1.6–1.8-mm NAB deposit** and, where present, a **0.6–0.8-mm interlayer**: it is not a demonstration on cast NAB, nor at the proposed 300–500 W/∼1-mm-track scale. A **1 cm²** polished deposit-top-face bulk cell, saturated-KCl Ag/AgCl and Pt foil was used in 3.5 wt% NaCl, with **20 min** pre-immersion for polarization and immersion/EIS through **21 days**; volume was **NR**. For direct/Ni–5Fe/Ni–20Cr variants, respectively, *E*corr was **−248/−255/−252 mV versus Ag/AgCl**; reported Tafel-derived *i*corr was **7.82/4.65/4.09 µA cm⁻²**; reported Stern–Geary-derived *R*p was **2,810/5,275/4,865 Ω cm²**; maximum attack depth was **3.4 ± 0.1/2.0 ± 0.1/1.8 ± 0.1 µm**. At 21 days fitted *R*ct was **1.44/51.47/85.10 kΩ cm²**. Direct deposition produced **Fe-rich dendrites** (a measured local point contained **56.1 wt% Fe**) through substrate dilution; these attacked preferentially. The intermediate layers changed deposit chemistry and suppressed that failure route. **CubXL implication:** sample the first diluted bead independently, rather than assigning it the bulk powder composition. **Novelty boundary:** laser-deposited NAB corrosion on steel already exists; matched-NAB repair cross-section mapping remains distinct. Do not use the published fitted *i*corr or *R*p as a calibration of physical dissolution without checking the underlying kinetics. (zhao2022thelaserdeposited pages 2-4, zhao2022thelaserdeposited pages 4-7, zhao2022thelaserdeposited pages 7-10, zhao2022thelaserdeposited pages 13-14)

4. **[CITE] [NUMBERS] [CUBXL]** Iannuzzi, M., Vasanth, K. L., and Frankel, G. S. “Unusual Correlation between SKPFM and Corrosion of Nickel Aluminum Bronzes.” *Journal of The Electrochemical Society* **164** (2017): C488–C497. **DOI: 10.1149/2.0391709jes.** Rolled **UNS C63200**, nominal **Al 8.7–9.5, Ni 4.0–4.8, Fe 3.5–4.3, Mn 1.2–2.0 wt%; Cu balance**, was examined as received and after heat treatment. The method was **ex-situ 80 × 80 µm SKPFM mapping**, not a 3-mm solution droplet; coupon dimensions were approximately **10 × 10 × 2 mm**, but wetted area and electrolyte volume were **NR**. Exposures were **0.5 M NaCl, pH ∼6, for 1–24 h**, or **0.5 M NaCl plus 10 vol% ammonia, pH 12.2, for up to 105 min**. Initially measured air-Volta values were **α −620, κII −564 and κIII −605 mV against a Ni calibration specimen**: α was lower than κII by **56 mV**, not higher, although the text's qualitative description of the sign/contrast should be read alongside its reported table. In chloride exposure the **α matrix or α–κ boundaries attacked while κ particles survived**; a simple Volta-nobility rule cannot reliably predict which phase dissolves. As-received κII particles were **2–3 µm**, coarsening to **4–6 µm** after treatment. The approximately **−250 mV versus SCE** potential in a *separate sulfate-polarization experiment* is not a NaCl solution *E*corr for each phase. *R*p, *i*corr, galvanic phase current, deposit–substrate potential difference and solution volume were **NR**. **CubXL implication:** correlate well results with post-test microscopy and solution chemistry, rather than declaring the apparently more negative air-SKPFM phase the corroding one. (iannuzzi2017unusualcorrelationbetween pages 2-3, iannuzzi2017unusualcorrelationbetween pages 3-4, iannuzzi2017unusualcorrelationbetween pages 4-6, iannuzzi2017unusualcorrelationbetween pages 6-8)

5. **[CITE] [NUMBERS] [NAVY] [CUBXL]** Song, Q. N., Zheng, Y. G., Jiang, S. L., Ni, D. R., and Ma, Z. Y. “Comparison of Corrosion and Cavitation Erosion Behaviors Between the As-Cast and Friction-Stir-Processed Nickel Aluminum Bronze.” *Corrosion* **69** (2013): 1111–1121. **DOI: 10.5006/0984.** Cast **C95800**, **Al 9.18, Ni 4.49, Fe 4.06, Mn 1.03 wt%; Cu balance**, was friction-stir-processed; specimens came from the cast material and **centre of the stir zone**, **not** a mapped process boundary. A conventional **0.49 cm²** epoxy-masked electrode with Pt and SCE was followed by EIS in **3.5 wt% NaCl for up to 82 days**, with weekly electrolyte changes; cell volume was **NR**. Cast α features exceeded **100 µm**; processed equiaxed α was around **10 µm** and some stream-like grains **3–4 µm**. After **10 days**, the stir-zone Nyquist diameter was **about one order of magnitude larger** than the cast specimen's, whereas short-time polarization distinguished them poorly. In separate cavitation experiments, 16-hour saltwater losses were **33.4 versus 15.9 mg**, and 20-hour cavity depths were **>150 versus <10 µm**, cast versus processed; these are **cavitation**, not quiescent-well, benchmarks. The paper identifies prior US Naval Surface Warfare Center application of FSP to propeller repair; that is **Navy application**, not an assertion that this paper received DoD funding. **CubXL implication:** preserve a longer film-growth endpoint and examine microstructure along depth; a 30-min screen can miss a consequential difference. (song2013comparisonofcorrosion pages 1-4, song2013comparisonofcorrosion pages 4-8, song2013comparisonofcorrosion pages 8-12)

6. **[CITE] [NUMBERS] [CUBXL]** Huo, R., Wang, Z., Wang, M., Wang, R., Zhang, S., Zhang, C., Wu, C., Chen, H., and Chen, J. “Modulating Heat Input to Optimize Corrosion Resistance of Nickel–Aluminum Bronze Manufactured by Cold Metal Transfer Additive Manufacturing.” *Materials* **18** (2025): 2205. **DOI: 10.3390/ma18102205.** This is **wire-arc/CMT additive manufacturing**, *not* laser DED: pre-alloyed ERCuNiAl wire had **Al 8.73, Fe 5.90, Ni 4.52, Mn 1.39, Si 0.058 wt%; Cu balance**. The bulk cell exposed **1 cm²**, used Pt foil/SCE, **aerated 3.5 wt% NaCl**, and stabilized OCP for **3,600 s** before EIS; electrolyte volume was **NR**. At heat inputs **243.8→644.7 J mm⁻¹**, 1-hour OCP endpoints were about **−237→−421 mV versus SCE**, while *polarization-derived* potentials were **−269.61 ± 40→−700.94 ± 15 mV** and fitted *i*corr values **2.56 ± 0.04→7.52 ± 0.07 µA cm⁻²**. Fitted *R*ct fell **2,485→707 Ω cm²**, as κ precipitates coarsened from submicrometre to micrometre/tens-of-micrometres scale and grains from **38.26→74.62 µm**. The paper's **third EIS row repeats the label “S2”**; its intermediate resistance must not be attributed to S3 without checking underlying data. **CubXL implication:** log bead-level heat input and thermal history; do not assume a visually sound single track and reheated wall have the same electrochemical response. (huo2025modulatingheatinput pages 4-5, huo2025modulatingheatinput pages 5-7, huo2025modulatingheatinput pages 7-10, huo2025modulatingheatinput pages 10-13, huo2025modulatingheatinput pages 13-15)

7. **[CITE] [NUMBERS] [NAVY] [CUBXL]** Krogstad, H. N., Johnsen, R., and Coey, M. “Effect of a Uniform Magnetic Field on Corrosion of Ni-Al Bronze in 3.5 wt% NaCl.” *Corrosion* **74** (2018): 197–209. **DOI: 10.5006/2531.** Cast **C95800**, **Cu 80.5, Al 9.4, Ni 5.0, Fe 4.3, Mn 0.7 wt%**, was tested as a **10-mm-diameter rotating disk in 1 L** or in a separate **0.2-L magnetic-field cell**, with Pt and saturated Ag/AgCl, 3.5 wt% NaCl at **22 ± 2 °C**. The freshly prepared electrode's OCP was about **−210 mV versus Ag/AgCl**. At **−180 mV versus Ag/AgCl**, rotation from zero to 800 rpm raised anodic current **0.103→2.023 A m⁻²**; at **−25 mV**, **28.5→71.3 A m⁻²**. The maximum field-induced current increase was **52%**. Importantly, the paper **quotes earlier**, rather than itself measures, natural-seawater **NAB–stainless-steel** coupling at **∼−50 mV Ag/AgCl and 0.06–11 A m⁻² (= 6–1,100 µA cm⁻²)**, depending on area ratio. That is **not a NAB-on-NAB deposit–substrate current**; the underlying earlier experiment needs inspection before using its geometry as a design load. **CubXL implication:** define whether fill/recirculation creates convection, and do not interpret an air-open, nominally static ∼150-µL well as a flowing-seawater service test. (krogstad2018effectofa pages 1-2, krogstad2018effectofa pages 3-4, krogstad2018effectofa pages 7-8)

## Feature scale, boundary placement and actual evidence gaps

A **3–4 mm-diameter** aperture is **3–4 times wider than a ∼1-mm DED track** and **6–20 times** a **0.2–0.5-mm layer thickness**. Even its area is approximately **7.1–12.6 mm²** (0.071–0.126 cm²). It cannot isolate a single thin-wall track, a narrow HAZ or an individual layer on a cross-section, and a spot centered on the fusion line deliberately **electrically couples** deposit and substrate. By contrast, κII precipitates of **2–6 µm**, κI particles up to approximately **50 µm**, and κIII lamellae around **5–10 µm wide** are hundreds of times smaller than the aperture; it will average their areal fractions and local anodic/cathodic sites. Some cast α or Cu–Ni HAZ grains exceed **100 µm**, still substantially below the well diameter. The fusion-boundary *width* for the proposed 300–500 W builds has **not been established** by these experiments; do not assign it an invented value. (iannuzzi2017unusualcorrelationbetween pages 3-4, song2013comparisonofcorrosion pages 4-8, xing2023characterizationofcorrosion pages 2-5, krogstad2018effectofa pages 2-3)

For NAB, the relevant mechanism is **not one fixed phase-polarity ordering**. Rolled NAB in near-neutral NaCl showed α or α–κ attack and protected κ; cast/welded NAB can add retained **β′**, while wire-arc deposits show heat-input-dependent κ and γ₂. Dilution can create entirely new Fe-rich, preferentially corroding dendrites, as demonstrated specifically for NAB deposited on **steel**, not yet for NAB-on-NAB repair. In acidic or occluded chloride, κ and β′ behavior may differ from the open neutral exposure. **Interdendritic Ni depletion and corrosion of interlayer bands in the proposed pre-alloyed 70–30/90–10 laser-DED Cu–Ni have not been quantified in the retrieved zone-resolved literature**; map Ni/Fe/Mn/Cr by SEM–EDS or EPMA before invoking them as causes. Nor can Zhao's steel-derived Fe-rich phase be assumed to arise in matching NAB powder on cast NAB. (iannuzzi2017unusualcorrelationbetween pages 8-9, iannuzzi2017unusualcorrelationbetween pages 4-6, zhao2020effectofweld pages 1-4, huo2025modulatingheatinput pages 5-7, zhao2022thelaserdeposited pages 4-7)

**No supported numerical answer** emerged for *E*corr, local current, breakdown/protection potential, element-by-element dissolution rate, or galvanic current of a **pre-alloyed, single-stream, 300–500 W laser-DED C70600/C71500-on-Cu–Ni or C95800-on-NAB repair**, separately resolved into deposit/fusion zone/HAZ/substrate. The retrieved repair studies primarily used individually cut **macro-electrodes**, whole repaired coupons, or microstructural **air** SKP/SKPFM, not microcapillary-cell, scanning-droplet-cell, SVET, SECM or local-EIS quantitative line scans across those matched-material DED repairs. The available laser-clad quantitative comparison is **NAB on SUS630**, a materially different galvanic couple. Numerical Cu–Ni **Cr-bearing** repair behavior and ultrasonic-atomization splat/skull corrosion are also **unreported here**, rather than presumed equivalent to the nominal powder. (xing2023characterizationofcorrosion pages 1-2, zhao2020effectofweld pages 1-4, zhao2022thelaserdeposited pages 2-4, nemani2024advancementsinadditive pages 105-106, nemani2024advancementsinadditive pages 26-28)

## Ranked Top 5 changes to the small-cell plan for copper alloys

1. **Add a genuine finer-resolution cross-section tier.** First image/EDS-map an unetched polished section and locate the melt boundary, track overlap, HAZ and layers. On a *wide, thick* repair coupon place separate 3–4 mm wells **entirely within** upper undiluted deposit, first diluted deposit if thick enough, HAZ if wide enough, and unaffected substrate; allow the well **radius plus alignment/O-ring tolerance** as clearance from each boundary. Put a separate **boundary-straddling** well across the fusion line and label it a *coupled mixed-area test*, never a fusion-zone-only test. For ∼1-mm tracks, 0.2–0.5-mm layers and narrow HAZs, supplement with ≤100–500 µm capillary/droplet apertures or SVET/SECM/local EIS and microscopy; if such access is unavailable, report only the composite-well response. Quantify metal area fractions inside each aperture from an image. (song2013comparisonofcorrosion pages 4-8, xing2023characterizationofcorrosion pages 2-5, zhao2022thelaserdeposited pages 4-7)

2. **Add direct, reference-calibrated galvanic experiments.** Provide two independently wired exposed pieces—deposit and cast NAB, or deposit and wrought Cu–Ni—behind separate masks in one seawater bath, joined through a **zero-resistance ammeter**, with an isolated common-electrolyte reference. Measure uncoupled OCPs, *mixed* potential, signed current and **area ratio**, at least **1:1** and a **small repair/anode versus large parent/cathode** configuration; repeat after films age. Deliberately test HAZ against deposit as well. A boundary-straddling single well retains internal electrical coupling but cannot directly read the boundary's galvanic current. The weld study's **4.43 µA cm⁻²** supplies a *Cu–Ni dissimilar-filler* instrument-range benchmark, not a prediction for matched DED repair. (xing2023characterizationofcorrosion pages 9-12, xing2023characterizationofcorrosion pages 2-5, krogstad2018effectofa pages 1-2)

3. **Run a time- and seawater-matched endpoint series, rather than treating 30-min OCP as service ranking.** Keep the fresh-surface screen, then use **separate, non-repolarized replicate spots** or corrosion-safe exposure cells over days and weeks, tracking OCP, near-OCP response, film impedance where the instrument allows it, and microscopy. Compare **3.5% NaCl, synthetic seawater and controlled natural seawater** with logged pH, oxygen, temperature, chloride and flow/renewal. Record stock age and whether pipette filling imposes convection; avoid pooling electrolyte from unlike exposure histories. The published Cu–Ni zone ranking evolved over approximately **20 days**, and cast-versus-FSP NAB separated strongly only after extended immersion. (xing2023characterizationofcorrosion pages 2-5, xing2023characterizationofcorrosion pages 9-12, song2013comparisonofcorrosion pages 8-12, krogstad2018effectofa pages 7-8)

4. **Make dissolution and surface integrity the decision endpoints, not a fitted Tafel rate.** Collect each well's entire effluent **and a measured rinse**, run time-zero stock, head/O-ring and carryover blanks, and analyze Cu, Ni, Fe, Mn, Al and Cr as applicable by ICP; calculate **mass per wetted area and time** with measured volume, accounting separately for adherent products. Photograph/profile *before and after* and examine polished cross-sections for selective β′/κ/interdendritic attack and O-ring-edge crevices. Start with OCP and carefully checked small-overpotential LPR, report the **measured differential slope** rather than converting through an assumed Stern–Geary coefficient, and treat large cyclic polarization as a **separate destructive endpoint**: chloride-active Cu alloys need not show stainless-steel-like breakdown/repassivation or a meaningful current-threshold reversal potential. Published laser-clad NAB *i*corr and *R*p are extrapolated/model quantities, whereas its observed attack depth and dilution are independent observations. (zhao2022thelaserdeposited pages 7-10, zhao2022thelaserdeposited pages 2-4, zhao2022thelaserdeposited pages 13-14, zhao2020effectofweld pages 1-4)

5. **Qualify geometry, chemistry and electronics for the actual copper-alloy signal.** Validate FKM sealing and exposed area on polished Cu-rich metal, ensure a thin wall or splat is never smaller than the aperture, check back contact and insulation against side leakage, and quantify oxygen depletion and evaporation in ∼150 µL during extended runs. Use a calibrated Ag/AgCl reference with stated filling solution and a potentiostat verified for low-current near-OCP measurements and impedance **if EIS is claimed**; do not assume any candidate has the required EIS mode. Keep Pt-counter products and the reference's chloride bridge out of the aliquot intended for trace-element ICP, and establish corrosion/adsorption blanks using each stock solution. Record deposited powder, splats and crucible skulls as **separate measured compositions and microstructures**, not surrogate C71500/C95800 coupons. These controls matter because the source studies changed cell size, alloy dilution and transport conditions enough to change their reported electrochemical responses. (zhao2022thelaserdeposited pages 2-4, zhao2022thelaserdeposited pages 4-7, huo2025modulatingheatinput pages 4-5, krogstad2018effectofa pages 4-6, krogstad2018effectofa pages 7-8)

References

1. (xing2023characterizationofcorrosion pages 9-12): Shaohua Xing, Shuyu Bai, Ran Liu, Yingshuang Liu, Jiantao Qi, Jian Hou, and Dalei Zhang. Characterization of corrosion behavior and corrosion production property of 90-10 cupronickel welding joints in flowing seawater. Metals, 13:294, Feb 2023. URL: https://doi.org/10.3390/met13020294, doi:10.3390/met13020294. This article has 7 citations.

2. (zhao2020effectofweld pages 1-4): Xu Zhao, Yuhong Qi, Jintao Wang, Tianxiang Peng, Zhanping Zhang, and Kejiao Li. Effect of weld and surface defects on the corrosion behavior of nickel aluminum bronze in 3.5% nacl solution. ArXiv, 10:1227, Sep 2020. URL: https://doi.org/10.3390/met10091227, doi:10.3390/met10091227. This article has 9 citations.

3. (zhao2022thelaserdeposited pages 7-10): Lu Zhao, Kailun Li, Jun Yao, Yixiang Yuan, and Baorui Du. The laser deposited nickel-aluminum bronze coatings on sus630 stainless steel and its corrosion resistance in 3.5 wt.% nacl solution. Metals, 12:781, Apr 2022. URL: https://doi.org/10.3390/met12050781, doi:10.3390/met12050781. This article has 8 citations.

4. (iannuzzi2017unusualcorrelationbetween pages 4-6): M. Iannuzzi, K. L. Vasanth, and G. S. Frankel. Unusual correlation between skpfm and corrosion of nickel aluminum bronzes. Journal of The Electrochemical Society, 164:C488-C497, Jan 2017. URL: https://doi.org/10.1149/2.0391709jes, doi:10.1149/2.0391709jes. This article has 53 citations and is from a peer-reviewed journal.

5. (xing2023characterizationofcorrosion media 9ceaa802): Shaohua Xing, Shuyu Bai, Ran Liu, Yingshuang Liu, Jiantao Qi, Jian Hou, and Dalei Zhang. Characterization of corrosion behavior and corrosion production property of 90-10 cupronickel welding joints in flowing seawater. Metals, 13:294, Feb 2023. URL: https://doi.org/10.3390/met13020294, doi:10.3390/met13020294. This article has 7 citations.

6. (xing2023characterizationofcorrosion media c0dc77ed): Shaohua Xing, Shuyu Bai, Ran Liu, Yingshuang Liu, Jiantao Qi, Jian Hou, and Dalei Zhang. Characterization of corrosion behavior and corrosion production property of 90-10 cupronickel welding joints in flowing seawater. Metals, 13:294, Feb 2023. URL: https://doi.org/10.3390/met13020294, doi:10.3390/met13020294. This article has 7 citations.

7. (xing2023characterizationofcorrosion media 4f4b1c2c): Shaohua Xing, Shuyu Bai, Ran Liu, Yingshuang Liu, Jiantao Qi, Jian Hou, and Dalei Zhang. Characterization of corrosion behavior and corrosion production property of 90-10 cupronickel welding joints in flowing seawater. Metals, 13:294, Feb 2023. URL: https://doi.org/10.3390/met13020294, doi:10.3390/met13020294. This article has 7 citations.

8. (xing2023characterizationofcorrosion pages 1-2): Shaohua Xing, Shuyu Bai, Ran Liu, Yingshuang Liu, Jiantao Qi, Jian Hou, and Dalei Zhang. Characterization of corrosion behavior and corrosion production property of 90-10 cupronickel welding joints in flowing seawater. Metals, 13:294, Feb 2023. URL: https://doi.org/10.3390/met13020294, doi:10.3390/met13020294. This article has 7 citations.

9. (xing2023characterizationofcorrosion pages 2-5): Shaohua Xing, Shuyu Bai, Ran Liu, Yingshuang Liu, Jiantao Qi, Jian Hou, and Dalei Zhang. Characterization of corrosion behavior and corrosion production property of 90-10 cupronickel welding joints in flowing seawater. Metals, 13:294, Feb 2023. URL: https://doi.org/10.3390/met13020294, doi:10.3390/met13020294. This article has 7 citations.

10. (zhao2020effectofweld pages 4-8): Xu Zhao, Yuhong Qi, Jintao Wang, Tianxiang Peng, Zhanping Zhang, and Kejiao Li. Effect of weld and surface defects on the corrosion behavior of nickel aluminum bronze in 3.5% nacl solution. ArXiv, 10:1227, Sep 2020. URL: https://doi.org/10.3390/met10091227, doi:10.3390/met10091227. This article has 9 citations.

11. (zhao2020effectofweld pages 11-14): Xu Zhao, Yuhong Qi, Jintao Wang, Tianxiang Peng, Zhanping Zhang, and Kejiao Li. Effect of weld and surface defects on the corrosion behavior of nickel aluminum bronze in 3.5% nacl solution. ArXiv, 10:1227, Sep 2020. URL: https://doi.org/10.3390/met10091227, doi:10.3390/met10091227. This article has 9 citations.

12. (zhao2022thelaserdeposited pages 4-7): Lu Zhao, Kailun Li, Jun Yao, Yixiang Yuan, and Baorui Du. The laser deposited nickel-aluminum bronze coatings on sus630 stainless steel and its corrosion resistance in 3.5 wt.% nacl solution. Metals, 12:781, Apr 2022. URL: https://doi.org/10.3390/met12050781, doi:10.3390/met12050781. This article has 8 citations.

13. (zhao2022thelaserdeposited pages 2-4): Lu Zhao, Kailun Li, Jun Yao, Yixiang Yuan, and Baorui Du. The laser deposited nickel-aluminum bronze coatings on sus630 stainless steel and its corrosion resistance in 3.5 wt.% nacl solution. Metals, 12:781, Apr 2022. URL: https://doi.org/10.3390/met12050781, doi:10.3390/met12050781. This article has 8 citations.

14. (zhao2022thelaserdeposited pages 10-13): Lu Zhao, Kailun Li, Jun Yao, Yixiang Yuan, and Baorui Du. The laser deposited nickel-aluminum bronze coatings on sus630 stainless steel and its corrosion resistance in 3.5 wt.% nacl solution. Metals, 12:781, Apr 2022. URL: https://doi.org/10.3390/met12050781, doi:10.3390/met12050781. This article has 8 citations.

15. (zhao2022thelaserdeposited pages 13-14): Lu Zhao, Kailun Li, Jun Yao, Yixiang Yuan, and Baorui Du. The laser deposited nickel-aluminum bronze coatings on sus630 stainless steel and its corrosion resistance in 3.5 wt.% nacl solution. Metals, 12:781, Apr 2022. URL: https://doi.org/10.3390/met12050781, doi:10.3390/met12050781. This article has 8 citations.

16. (iannuzzi2017unusualcorrelationbetween pages 3-4): M. Iannuzzi, K. L. Vasanth, and G. S. Frankel. Unusual correlation between skpfm and corrosion of nickel aluminum bronzes. Journal of The Electrochemical Society, 164:C488-C497, Jan 2017. URL: https://doi.org/10.1149/2.0391709jes, doi:10.1149/2.0391709jes. This article has 53 citations and is from a peer-reviewed journal.

17. (iannuzzi2017unusualcorrelationbetween pages 2-3): M. Iannuzzi, K. L. Vasanth, and G. S. Frankel. Unusual correlation between skpfm and corrosion of nickel aluminum bronzes. Journal of The Electrochemical Society, 164:C488-C497, Jan 2017. URL: https://doi.org/10.1149/2.0391709jes, doi:10.1149/2.0391709jes. This article has 53 citations and is from a peer-reviewed journal.

18. (iannuzzi2017unusualcorrelationbetween pages 6-8): M. Iannuzzi, K. L. Vasanth, and G. S. Frankel. Unusual correlation between skpfm and corrosion of nickel aluminum bronzes. Journal of The Electrochemical Society, 164:C488-C497, Jan 2017. URL: https://doi.org/10.1149/2.0391709jes, doi:10.1149/2.0391709jes. This article has 53 citations and is from a peer-reviewed journal.

19. (song2013comparisonofcorrosion pages 4-8): Q. Song, Yingkui Zheng, Shenglin Jiang, D. Ni, and Zhi Ma. Comparison of corrosion and cavitation erosion behaviors between the as-cast and friction-stir-processed nickel aluminum bronze. Jul 2013. URL: https://doi.org/10.5006/0984, doi:10.5006/0984. This article has 63 citations and is from a peer-reviewed journal.

20. (song2013comparisonofcorrosion pages 12-15): Q. Song, Yingkui Zheng, Shenglin Jiang, D. Ni, and Zhi Ma. Comparison of corrosion and cavitation erosion behaviors between the as-cast and friction-stir-processed nickel aluminum bronze. Jul 2013. URL: https://doi.org/10.5006/0984, doi:10.5006/0984. This article has 63 citations and is from a peer-reviewed journal.

21. (song2013comparisonofcorrosion pages 8-12): Q. Song, Yingkui Zheng, Shenglin Jiang, D. Ni, and Zhi Ma. Comparison of corrosion and cavitation erosion behaviors between the as-cast and friction-stir-processed nickel aluminum bronze. Jul 2013. URL: https://doi.org/10.5006/0984, doi:10.5006/0984. This article has 63 citations and is from a peer-reviewed journal.

22. (huo2025modulatingheatinput pages 5-7): Renjie Huo, Zheying Wang, Mingsheng Wang, Rui Wang, Song Zhang, Chunhua Zhang, Chenliang Wu, Haitao Chen, and Jiang Chen. Modulating heat input to optimize corrosion resistance of nickel–aluminum bronze manufactured by cold metal transfer additive manufacturing. Materials, 18:2205, May 2025. URL: https://doi.org/10.3390/ma18102205, doi:10.3390/ma18102205. This article has 5 citations.

23. (huo2025modulatingheatinput pages 7-10): Renjie Huo, Zheying Wang, Mingsheng Wang, Rui Wang, Song Zhang, Chunhua Zhang, Chenliang Wu, Haitao Chen, and Jiang Chen. Modulating heat input to optimize corrosion resistance of nickel–aluminum bronze manufactured by cold metal transfer additive manufacturing. Materials, 18:2205, May 2025. URL: https://doi.org/10.3390/ma18102205, doi:10.3390/ma18102205. This article has 5 citations.

24. (huo2025modulatingheatinput pages 4-5): Renjie Huo, Zheying Wang, Mingsheng Wang, Rui Wang, Song Zhang, Chunhua Zhang, Chenliang Wu, Haitao Chen, and Jiang Chen. Modulating heat input to optimize corrosion resistance of nickel–aluminum bronze manufactured by cold metal transfer additive manufacturing. Materials, 18:2205, May 2025. URL: https://doi.org/10.3390/ma18102205, doi:10.3390/ma18102205. This article has 5 citations.

25. (huo2025modulatingheatinput pages 10-13): Renjie Huo, Zheying Wang, Mingsheng Wang, Rui Wang, Song Zhang, Chunhua Zhang, Chenliang Wu, Haitao Chen, and Jiang Chen. Modulating heat input to optimize corrosion resistance of nickel–aluminum bronze manufactured by cold metal transfer additive manufacturing. Materials, 18:2205, May 2025. URL: https://doi.org/10.3390/ma18102205, doi:10.3390/ma18102205. This article has 5 citations.

26. (huo2025modulatingheatinput pages 13-15): Renjie Huo, Zheying Wang, Mingsheng Wang, Rui Wang, Song Zhang, Chunhua Zhang, Chenliang Wu, Haitao Chen, and Jiang Chen. Modulating heat input to optimize corrosion resistance of nickel–aluminum bronze manufactured by cold metal transfer additive manufacturing. Materials, 18:2205, May 2025. URL: https://doi.org/10.3390/ma18102205, doi:10.3390/ma18102205. This article has 5 citations.

27. (krogstad2018effectofa pages 3-4): Hedda Nordby Krogstad, Roy Johnsen, and Michael Coey. Effect of a uniform magnetic field on corrosion of ni-al bronze in 3.5 wt% nacl. Corrosion, 74:197-209, Feb 2018. URL: https://doi.org/10.5006/2531, doi:10.5006/2531. This article has 5 citations and is from a peer-reviewed journal.

28. (krogstad2018effectofa pages 4-6): Hedda Nordby Krogstad, Roy Johnsen, and Michael Coey. Effect of a uniform magnetic field on corrosion of ni-al bronze in 3.5 wt% nacl. Corrosion, 74:197-209, Feb 2018. URL: https://doi.org/10.5006/2531, doi:10.5006/2531. This article has 5 citations and is from a peer-reviewed journal.

29. (krogstad2018effectofa pages 1-2): Hedda Nordby Krogstad, Roy Johnsen, and Michael Coey. Effect of a uniform magnetic field on corrosion of ni-al bronze in 3.5 wt% nacl. Corrosion, 74:197-209, Feb 2018. URL: https://doi.org/10.5006/2531, doi:10.5006/2531. This article has 5 citations and is from a peer-reviewed journal.

30. (krogstad2018effectofa pages 7-8): Hedda Nordby Krogstad, Roy Johnsen, and Michael Coey. Effect of a uniform magnetic field on corrosion of ni-al bronze in 3.5 wt% nacl. Corrosion, 74:197-209, Feb 2018. URL: https://doi.org/10.5006/2531, doi:10.5006/2531. This article has 5 citations and is from a peer-reviewed journal.

31. (song2013comparisonofcorrosion pages 1-4): Q. Song, Yingkui Zheng, Shenglin Jiang, D. Ni, and Zhi Ma. Comparison of corrosion and cavitation erosion behaviors between the as-cast and friction-stir-processed nickel aluminum bronze. Jul 2013. URL: https://doi.org/10.5006/0984, doi:10.5006/0984. This article has 63 citations and is from a peer-reviewed journal.

32. (krogstad2018effectofa pages 2-3): Hedda Nordby Krogstad, Roy Johnsen, and Michael Coey. Effect of a uniform magnetic field on corrosion of ni-al bronze in 3.5 wt% nacl. Corrosion, 74:197-209, Feb 2018. URL: https://doi.org/10.5006/2531, doi:10.5006/2531. This article has 5 citations and is from a peer-reviewed journal.

33. (iannuzzi2017unusualcorrelationbetween pages 8-9): M. Iannuzzi, K. L. Vasanth, and G. S. Frankel. Unusual correlation between skpfm and corrosion of nickel aluminum bronzes. Journal of The Electrochemical Society, 164:C488-C497, Jan 2017. URL: https://doi.org/10.1149/2.0391709jes, doi:10.1149/2.0391709jes. This article has 53 citations and is from a peer-reviewed journal.

34. (nemani2024advancementsinadditive pages 105-106): Alireza Vahedi Nemani, Mahya Ghaffari, Kazem Sabet Bokati, Nima Valizade, Elham Afshari, and Ali Nasiri. Advancements in additive manufacturing for copper-based alloys and composites: a comprehensive review. Journal of Manufacturing and Materials Processing, 8:54, Mar 2024. URL: https://doi.org/10.3390/jmmp8020054, doi:10.3390/jmmp8020054. This article has 100 citations.

35. (nemani2024advancementsinadditive pages 26-28): Alireza Vahedi Nemani, Mahya Ghaffari, Kazem Sabet Bokati, Nima Valizade, Elham Afshari, and Ali Nasiri. Advancements in additive manufacturing for copper-based alloys and composites: a comprehensive review. Journal of Manufacturing and Materials Processing, 8:54, Mar 2024. URL: https://doi.org/10.3390/jmmp8020054, doi:10.3390/jmmp8020054. This article has 100 citations.
