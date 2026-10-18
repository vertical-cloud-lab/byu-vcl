<!--
Edison Scientific LITERATURE_HIGH task (batch 1)
- Task ID: 45bee772-225f-417b-b6e6-ab3631ffd309
- Submitted: 2026-10-18T01:20:01Z
- Fetched: 2026-10-18T01:50:01Z (status: success)
- Raw trajectory JSON: ../raw/c1-03-element-resolved-dissolution-cu.json.gz
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

QUESTION: What has element-resolved dissolution analysis shown for Cu-Ni
(90-10, 70-30) and aluminum bronzes/NAB in chloride or seawater? Cover atomic
emission spectroelectrochemistry (AESEC; Ogle and co-workers), scanning flow
cell ICP-MS, and offline ICP-OES/ICP-MS or AAS of test solutions or immersion
water. Report dissolution rates by element (Cu, Ni, Fe, Mn, Al) in
ug/cm2/day or an equivalent unit; whether dissolution is congruent or
selective (for example Ni and Fe retained in the film, or dealuminification
of NAB's kappa/alpha phases); and whether the electrolyte's Al/Cu or Ni/Cu
ratio tracks selective phase corrosion depth. How well does dissolved metal
agree with the passed charge (faradaic balance), given that copper
redeposits and corrosion products stay on the surface? Practical points for
a 150 uL sample in 3.5% NaCl or substitute ocean water: dilution and sodium
matrix effects on ICP-OES vs ICP-MS, acidification, loss to polypropylene
tubes, detection limits. For naval relevance, include copper release rates of
Cu-Ni and NAB in seawater, their link to antifouling performance (any
release-rate threshold), how the release rate falls as the film matures,
regulatory or Navy limits on copper discharge from ships and seawater
systems, and any standard method for metal release rates (e.g. ASTM D6442,
ISO 15181 for antifouling coatings) that could be adapted to bare alloys.

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

QUESTION: What has element-resolved dissolution analysis shown for Cu-Ni
(90-10, 70-30) and aluminum bronzes/NAB in chloride or seawater? Cover atomic
emission spectroelectrochemistry (AESEC; Ogle and co-workers), scanning flow
cell ICP-MS, and offline ICP-OES/ICP-MS or AAS of test solutions or immersion
water. Report dissolution rates by element (Cu, Ni, Fe, Mn, Al) in
ug/cm2/day or an equivalent unit; whether dissolution is congruent or
selective (for example Ni and Fe retained in the film, or dealuminification
of NAB's kappa/alpha phases); and whether the electrolyte's Al/Cu or Ni/Cu
ratio tracks selective phase corrosion depth. How well does dissolved metal
agree with the passed charge (faradaic balance), given that copper
redeposits and corrosion products stay on the surface? Practical points for
a 150 uL sample in 3.5% NaCl or substitute ocean water: dilution and sodium
matrix effects on ICP-OES vs ICP-MS, acidification, loss to polypropylene
tubes, detection limits. For naval relevance, include copper release rates of
Cu-Ni and NAB in seawater, their link to antifouling performance (any
release-rate threshold), how the release rate falls as the film matures,
regulatory or Navy limits on copper discharge from ships and seawater
systems, and any standard method for metal release rates (e.g. ASTM D6442,
ISO 15181 for antifouling coatings) that could be adapted to bare alloys.

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


# Element-Resolved Dissolution Analysis of Cu-Ni and Aluminum Bronze / NAB Alloys in Chloride and Seawater: Literature Review for CubXL Small-Cell Planning

## 1. Overview of Techniques and Key Findings

The following table consolidates the most relevant studies across the three analytical modalities requested—AESEC, scanning flow cell ICP-MS (SFC-ICP-MS), and offline ICP-OES/ICP-MS—together with naval copper release data and regulatory benchmarks.

| Reference (author, year, DOI) | Alloy / material | Technique | Electrolyte | Cell type and area | Key findings | Tags |
|---|---|---|---|---|---|---|
| Sur et al. (2025), *Journal of The Electrochemical Society* 172, 101502. DOI: [10.1149/1945-7111/ae0eb6](https://doi.org/10.1149/1945-7111/ae0eb6) | Arc-melted and solution-treated Cu–23Al and Cu–23Al–3Sn, compositions in at.% (approximately Cu–10.5Al and Cu–10.4Al–3.5Sn in wt.%) | AESEC–LSV and AESEC–chronoamperometry; ICP-AES measurement of Cu, Al, and Sn | Deaerated 0.1 M Na₂SO₄, pH 4; LSV after cathodic oxide reduction; potentiostatic tests at +0.6 V vs SHE | Flow cell: 1 cm², approximately 0.02 cm³ s⁻¹; conventional O-ring cell: 0.066 cm² | Sn reduced Cu dissolution about 10-fold and Al dissolution about 25-fold. Cu–23Al showed preferential Al loss during the active–passive transition; Cu–23Al–3Sn retained/enriched Al and Sn. XPS film enrichment factors reached about 2.25 for Al and 12 for Sn, while Cu fell to about 0.2; film was 49 at.% Al(III), 37 at.% Sn(II/IV), and 14 at.% Cu(I/II). No chloride or seawater and not NAB. (sur2025revisitingtheinfluence pages 16-19, sur2025revisitingtheinfluence pages 8-10, sur2025revisitingtheinfluence pages 13-16) | [CITE] [NUMBERS] [CUBXL] Convert ICP concentration to elemental current using flow and area; compare measured and congruent currents. [NOVELTY-RISK] Closest AESEC overlap for Cu–Al alloys. [GAP] Not NAB or chloride. |
| Hou et al. (2026), *npj Materials Degradation* 10. DOI: [10.1038/s41529-026-00747-2](https://doi.org/10.1038/s41529-026-00747-2) | Equiatomic CoCrFeMnNi Cantor alloy; non-copper methodological comparator | Operando AESEC / flow-through electrochemistry–ICP-AES | 0.5 M H₂SO₄ with localized chloride injection | Low-dispersion flow-through cell; area and volume not reported in the available extract | Sub-ppb element-resolved detection: Co 4.7, Cr 2.2–3.4, Fe 1.8, Mn 0.4, and Ni 7.6 µg L⁻¹. Co and Fe dissolved slightly more during pit initiation; Cr dominated repassivation. Repassivation charge greatly exceeded that expected for a compact film, implying repeated hydrated-oxide formation and dissolution. (hou2026trackingelementspecificdissolution pages 1-2, hou2026trackingelementspecificdissolution pages 6-7) | [CITE] [NUMBERS] [CUBXL] Demonstrates time-response correction and direct charge–dissolution comparison. [GAP] Not a copper alloy or seawater study. |
| Speck & Cherevko (2020), *Electrochemistry Communications* 115, 106739. DOI: [10.1016/j.elecom.2020.106739](https://doi.org/10.1016/j.elecom.2020.106739) | Polished polycrystalline Cu foil | Scanning flow cell–online ICP-MS | 0.05 M KOH and 0.05 M phosphate buffers, pH 6.8–12; Ar-purged | Custom polycarbonate SFC; Ag/AgCl reference through a capillary; graphite counter at inlet; 220 µL min⁻¹; area not stated | One CV dissolved 523 ± 1 ng Cu cm⁻², equivalent to 3.25 monolayers. Cu dissolution represented about 4–7% of anodic charge, about 15.5% during Cu(II)→Cu(I) reduction, and about 1.1% during Cu(I)→Cu(0). Low-potential Cu redeposition suppressed measured dissolved Cu. (speck2020electrochemicalcopperdissolution pages 1-2, speck2020electrochemicalcopperdissolution pages 2-3) | [CITE] [NUMBERS] [CUBXL] Dissolved Cu cannot be assumed equal to passed charge; avoid Pt-counter Cu plating and collect electrolyte immediately. [NOVELTY-RISK] SFC automation precedent. [GAP] Pure Cu, no chloride. |
| Vavra et al. (2024), *Nature Catalysis* 7, 89–97. DOI: [10.1038/s41929-023-01070-8](https://doi.org/10.1038/s41929-023-01070-8) | Electropolished Cu foil and Cu nanoparticles on glassy carbon | SFC–online ICP-MS plus UV–Vis identification of transient Cu complexes | CO₂- or Ar-saturated 0.05 M KHCO₃; tests with 0.1 mM 2,9-dimethylphenanthroline | XYZ-positioned flow cell; double-junction Ag/AgCl/3 M KCl reference; glassy-carbon counter; approximately 3.5 µL s⁻¹; area not stated | ICP-MS sensitivity reached pg cm⁻². Little Cu reached the detector without ligand because short-lived Cu⁺ species redeposited near the electrode; ligand stabilization increased the signal and UV–Vis identified [Cu(dmphen)₂]⁺. Electrolytes above 0.05 M prevented reliable ion detection in this configuration. (vavra2024solutionbasedcu+transient pages 5-9, vavra2024solutionbasedcu+transient pages 12-16) | [CITE] [NUMBERS] [CUBXL] Strong warning that stagnant 150 µL wells undercount Cu through redeposition and precipitation. [GAP] Pure Cu and bicarbonate, not saline alloys. |
| Earley et al. (2020), *Biofouling* 36, 276–291. DOI: [10.1080/08927014.2020.1756267](https://doi.org/10.1080/08927014.2020.1756267) | Commercial flat sheet and expanded mesh, Cu–10Ni (90/10 wt.%); also Cu–Zn mesh, silicon bronze, and Cu₂O-coated nylon | Navy Dome release test; offline ICP-MS for total and 0.45 µm-filtered Cu, Ni, and Zn | Natural San Diego Bay seawater; 1-h release measurements after 1–365 d exposure | Closed-loop 30.5 cm Dome, approximately 2.8 L; planar area 707 cm² for sheet and 613 cm² for mesh; samples at 0, 15, 30, 45, and 60 min | Cu dominated release; Ni was a fractional component. Initial alloy Cu release was approximately 100–200 µg cm⁻² d⁻¹, declining within about 30 d to pseudo-steady-state values of 1.4 µg cm⁻² d⁻¹ for flat 90/10 sheet and 3.9 µg cm⁻² d⁻¹ for 90/10 mesh. Alloy rates of 1.4–6.9 µg cm⁻² d⁻¹ delayed fouling, whereas coated net below 0.5 µg cm⁻² d⁻¹ fouled most. Samples were acidified to pH 2 and diluted in 0.1 N HNO₃ or preconcentrated before ICP-MS. (earley2020estimatesofenvironmental pages 1-3, earley2020estimatesofenvironmental pages 5-6, earley2020estimatesofenvironmental pages 6-8, earley2020estimatesofenvironmental pages 10-12) | [CITE] [NUMBERS] [NAVY] [CUBXL] Include filtered/unfiltered fractions and multi-time-point release slopes; one-hour polished-surface data represent initial release, not mature-film performance. |
| Gao & Liu (2022), *Materials* 15, 8513. DOI: [10.3390/ma15238513](https://doi.org/10.3390/ma15238513) | High-strength commercial C71500, nominally Cu–30Ni with Fe and Mn; processing condition not fully specified | Bulk immersion, polarization, EIS, SEM/EDS, XPS, and XRD; not solution ICP | 3.5 wt.% NaCl + 0.5 wt.% Na₂S; 0.5–672 h | Bulk three-electrode and immersion cells; volume and exposed area not reported in the available extract | Initial corrosion rate about 0.15 mm y⁻¹ and initial *i*<sub>corr</sub> about 96.6 µA cm⁻²; rate stabilized near 0.09 mm y⁻¹ after 168 h. Anodic features occurred near −525 and −404 mV vs SCE. Sulfide promoted Ni and Fe dissolution and prevented protective Cu₂O development. Product-film EDS showed Mn 0.3–1.7 wt.%, Fe 0.2–1.7 wt.%, and Ni decreasing from 30.8 wt.% at 24 h to 0.6 wt.% at 672 h. (gao2022corrosionbehaviorof pages 4-5, gao2022corrosionbehaviorof pages 8-10) | [CITE] [NUMBERS] [NAVY] Polluted-seawater benchmark. [CUBXL] Add a sulfide condition only as a separate protocol; do not pool it with clean seawater rankings. [GAP] No dissolved-solution mass balance. |
| Kievits & Ijsseling (1972), *Werkstoffe und Korrosion* 23, 1084–1096. DOI: [10.1002/maco.19720231203](https://doi.org/10.1002/maco.19720231203) | Commercial CuNi10Fe, broadly corresponding to 90/10 Cu–Ni with Fe | Seawater exposure with metallographic and elemental analysis of corrosion-product films; not online dissolution analysis | Seawater; duration and hydrodynamics vary and are not completely specified in the available extract | Bulk exposure; volume and area not reported | Mature films were generally 10–25 µm thick, locally about 50 µm, porous and layered. Alternating layers were enriched in Ni and Fe and depleted in Cu, or depleted in Ni and Fe. This demonstrates strongly non-congruent partitioning into retained products but supplies no element-specific release flux. (kievits1972researchintothe pages 8-9) | [CITE] [NUMBERS] [CUBXL] Preserve and analyze residual films; solution ICP alone misses retained Ni/Fe and corrosion products. [GAP] No quantitative dissolved-metal rates or faradaic balance. |
| Zhu et al. (2021), *Anti-Corrosion Methods and Materials* 68, 113–121. DOI: [10.1108/ACMM-01-2021-2422](https://doi.org/10.1108/ACMM-01-2021-2422) | Induction-melted Cu–30Ni–1Mn–*x*Fe, *x* = 0.4, 0.6, 0.8, or 1.0 wt.% | EIS, SEM, XRD, and XPS of corrosion films; not element-resolved solution ICP | Saline/chloride exposure; exact concentration, duration, cell volume, and area not available in the retrieved extract | Bulk cell; geometry not reported | The 1.0 wt.% Fe alloy had the best corrosion resistance. Films comprised a dense inner Cu₂O composite layer and a loose hydrated outer layer; Ni accumulated in the inner film and Fe enriched as γ-FeOOH. Added Fe reduced Cu₂(OH)₃Cl while Cu₂O content remained broadly unchanged. (mantzavinos2001durabilitystudiesrelevant pages 59-63, mantzavinos2001durabilitystudiesrelevant pages 55-59) | [CITE] [CUBXL] Measure Fe and Ni retained in the film as well as solution release. [GAP] No elemental dissolution flux, charge balance, or small-cell test. |
| Paquin et al. (2000), *Environmental Science & Policy* 3, 165–174. DOI: [10.1016/S1462-9011(00)00045-9](https://doi.org/10.1016/S1462-9011(00)00045-9) | Copper-alloy seawater condenser discharges; not a specific alloy coupon experiment | Environmental discharge and bioavailability assessment; water-quality-criterion analysis | Marine cooling-water discharge | Full-scale condenser/discharge context; no electrochemical cell | Reports U.S. EPA saltwater criteria of 4.8 µg L⁻¹ acute and 3.1 µg L⁻¹ chronic dissolved Cu, with site-specific water-effect-ratio adjustment where justified. These are receiving-water concentrations, not alloy surface-release limits. (paquin2000revisitingtheaquatic pages 4-5, paquin2000revisitingtheaquatic pages 5-8) | [CITE] [NUMBERS] [NAVY] Receiving-water relevance. [CUBXL] Do not compare a 150 µL well concentration directly with a discharge criterion without dilution and transport modeling. |


*Table: Summary of direct dissolution measurements, film-retention studies, and naval copper-release benchmarks. It distinguishes true element-resolved methods from related evidence and highlights the principal CubXL design implications and unresolved gaps.*

## 2. AESEC (Atomic Emission Spectroelectrochemistry) — Ogle and Co-Workers

### 2.1 Methodology
AESEC couples an electrochemical flow cell directly to an ICP-AES spectrometer. Dissolved species are transported continuously from the electrode surface through a low-dispersion flow system (typically ~0.02 cm³ s⁻¹) to the plasma, where element-specific emission is converted to concentration (C_M) and then to a dissolution current density via i_M = n_M · F · f · C_M / A (sur2025revisitingtheinfluence pages 8-10). The technique achieves sub-ppb detection limits for transition metals (e.g., Fe 1.8 ppb, Mn 0.4 ppb, Ni 7.6 ppb in sulfuric acid) (hou2026trackingelementspecificdissolution pages 6-7). Selectivity is assessed by comparing the measured elemental current (i_M) with the hypothetical congruent-dissolution current (i_cg_M), and the integral difference gives the surface enrichment (Θ_M) (sur2025revisitingtheinfluence pages 8-10).

### 2.2 AESEC on Cu-Al Alloys (Closest Analog to NAB)
**Sur et al. (2025), J. Electrochem. Soc. 172, 101502, DOI: 10.1149/1945-7111/ae0eb6** (Scully, Han, and Ogle groups, UVA/Sorbonne). [CITE] [NUMBERS] [GAP]

- **Material:** Arc-melted Cu-23Al and Cu-23Al-3Sn (at.%), single-phase FCC solid solutions (not commercial NAB with multiphase κ structures), tested in deaerated 0.1 M Na₂SO₄ at pH 4.
- **Key AESEC findings:** Cu-23Al showed preferential Al dissolution (Al depletion from the surface) during the active-passive transition: i_Al exceeded i_cg_Al. In contrast, Cu-23Al-3Sn showed Al enrichment (i_Al < i_cg_Al) and Sn enrichment (i_Sn < i_cg_Sn) (sur2025revisitingtheinfluence pages 13-16, sur2025revisitingtheinfluence pages 19-22). Adding 3 at.% Sn reduced Cu dissolution approximately 10-fold and Al dissolution approximately 25-fold (sur2025revisitingtheinfluence pages 13-16). XPS film enrichment factors for Cu-23Al-3Sn reached f_Al ≈ 2.25, f_Sn ≈ 12, and f_Cu ≈ 0.2; the passive film contained 49 at.% Al(III), 37 at.% Sn(II/IV), and only 14 at.% Cu(I/II) (sur2025revisitingtheinfluence pages 16-19). The number of dissolved monolayers required to passivate dropped from ~7000 (Cu-11.5Al) to ~70 (Cu-23Al-3Sn) (sur2025revisitingtheinfluence pages 10-13). Polarization resistance after 28 days: Cu-23Al-3Sn had Rp ≈ 10 kΩ·cm² versus ~1.5 kΩ·cm² for Cu-23Al and ~0.25 kΩ·cm² for pure Cu (sur2025revisitingtheinfluence pages 16-19).
- **[CUBXL]** The AESEC methodology of comparing spectral dissolution current with congruent-dissolution current is directly transferable: CubXL should compute i_cg for each element from the measured Cu signal and bulk composition, then compare with ICP results. The Viton O-ring cell in the Sur study (0.066 cm² exposed area) is geometrically similar to the planned FKM O-ring wells.
- **[NOVELTY-RISK]** This study is the closest published AESEC work on Cu-Al alloys; extending it to commercial multi-phase NAB in chloride would be novel.

### 2.3 AESEC on HEA (Methodological Benchmark)
**Hou et al. (2026), npj Mater. Degrad. 10, DOI: 10.1038/s41529-026-00747-2** (Ogle, Vivier). [CITE] [NUMBERS]

- Demonstrated operando AESEC during pitting of CoCrFeMnNi in 0.5 M H₂SO₄ with Cl⁻ injection; tracked four stages (incubation, initiation, propagation, repassivation) with element specificity (hou2026trackingelementspecificdissolution pages 1-2). Charge analysis showed repassivation consumed far more charge than expected for a compact passive film, indicating iterative hydrated-oxide dissolution and reformation (hou2026trackingelementspecificdissolution pages 1-2).
- **[GAP]** Not a copper alloy. **No published AESEC study on Cu-Ni 90/10, 70/30, or multi-phase NAB was found.**

### 2.4 AESEC on Cu-Containing Phases in Al Alloys
Ogle et al. (Electrochim. Acta, 2009, DOI: 10.1016/j.electacta.2009.01.037) studied dealloying of intermetallic phases on stainless steel leaving residual Cu films; Lebouil et al. (Mater. Corros. 2014) studied dealloying of Al₂Cu and Al₇Cu₂Fe intermetallics to form nanoparticulate Cu. These provide precedent for tracking Cu redeposition but are on Al-alloy intermetallics, not on Cu-Ni or NAB. [GAP]

## 3. Scanning Flow Cell ICP-MS (SFC-ICP-MS)

### 3.1 Pure Copper Benchmark
**Speck & Cherevko (2020), Electrochem. Commun. 115, 106739, DOI: 10.1016/j.elecom.2020.106739** [CITE] [NUMBERS]

- **Setup:** Polycarbonate SFC with Ag/AgCl reference via capillary, graphite counter at inlet (angled 60°), flow rate 220 µL min⁻¹ to Perkin Elmer NexION 350X ICP-MS (speck2020electrochemicalcopperdissolution pages 1-2).
- **Key data:** One CV in 0.05 M KOH dissolved 523 ± 1 ng cm⁻² Cu (3.25 monolayers). During anodic transitions, 4–7% of passed charge appeared as dissolved Cu; during CuII → CuI reduction, ~15.5% of charge dissolved; during CuI → Cu⁰ reduction, only ~1.1%, likely due to redeposition at low potentials (speck2020electrochemicalcopperdissolution pages 2-3). After accounting for anodic dissolution, the anodic-cathodic charge discrepancy was reduced to 0.2 ± 0.2 mC cm⁻², within integration error (speck2020electrochemicalcopperdissolution pages 2-3).
- **[CUBXL]** Demonstrates that dissolved Cu is a small fraction of passed charge; redeposition is rapid. In a stagnant 150 µL well, this problem is amplified because dissolved Cu⁺ is not swept away. The CubXL post-test solution will undercount total dissolution unless the well is acidified rapidly.

### 3.2 Cu Redeposition Dynamics
**Vavra et al. (2024), Nature Catalysis 7, 89–97, DOI: 10.1038/s41929-023-01070-8** [CITE] [NUMBERS]

- Without a ligand to stabilize Cu⁺ in solution, very little Cu was detected by SFC-ICP-MS at pg cm⁻² sensitivity, indicating that transient Cu⁺ species redeposit near the electrode faster than they can be transported to the detector (vavra2024solutionbasedcu+transient pages 5-9). Adding 0.1 mM 2,9-dimethylphenanthroline stabilized Cu⁺ and dramatically increased the ICP-MS signal (vavra2024solutionbasedcu+transient pages 5-9). Electrolyte concentrations above 0.05 M prevented reliable ion detection due to matrix effects (vavra2024solutionbasedcu+transient pages 12-16).
- **[CUBXL]** This is a strong warning: in a stagnant 150 µL O-ring well, Cu dissolution during a short polarization test may largely redeposit on the alloy surface or precipitate as Cu₂O/CuCl, making the recovered solution an underestimate of total anodic dissolution. Rapid acidification of the post-test electrolyte is essential.
- **[GAP]** SFC-ICP-MS has not been applied to Cu-Ni alloys or NAB in chloride.

## 4. Selective Dissolution, Film Composition, and Corrosion Rates of Cu-Ni Alloys

### 4.1 Corrosion-Product Film and Ni/Fe Enrichment
The corrosion-product film on Cu-Ni alloys in seawater is a bilayer: an inner, relatively dense Cu₂O composite incorporating Ni and Fe ions, and an outer, porous hydrated layer containing Cu₂(OH)₃Cl and CuO (mantzavinos2001durabilitystudiesrelevant pages 59-63, mantzavinos2001durabilitystudiesrelevant pages 55-59). Nickel and iron progressively accumulate in the inner film, becoming clearly concentrated after 6–8 weeks of seawater exposure (mantzavinos2001durabilitystudiesrelevant pages 59-63). Iron additions (especially 0.8–1.0 wt.% Fe) enhance this enrichment and reduce the proportion of Cu₂(OH)₃Cl in the outer film while Cu₂O remains broadly constant, thereby improving corrosion resistance (mantzavinos2001durabilitystudiesrelevant pages 59-63). In CuNi10Fe, mature films were 10–25 µm thick with alternating layers enriched and depleted in Ni and Fe relative to Cu, confirming strongly non-congruent element partitioning (kievits1972researchintothe pages 8-9).

**Zhu et al. (2021), Anti-Corros. Meth. Mater. 68, 113–121, DOI: 10.1108/ACMM-01-2021-2422** [CITE] [CUBXL]
- Cu-30Ni-xFe-1Mn (x = 0.4–1.0 wt.%); XPS showed Ni accumulation in the inner film and Fe enrichment as γ-FeOOH (mantzavinos2001durabilitystudiesrelevant pages 59-63).
- **[CUBXL]** Solution ICP alone misses the Ni and Fe retained in the corrosion product film. CubXL should consider measuring both dissolved metals in the recovered electrolyte AND post-test surface composition (SEM-EDS or XPS) to close the mass balance.

### 4.2 Quantitative Corrosion Rates for C71500
**Gao & Liu (2022), Materials 15, 8513, DOI: 10.3390/ma15238513** [CITE] [NUMBERS] [NAVY]
- C71500 in 3.5 wt.% NaCl + 0.5 wt.% Na₂S: initial corrosion rate ~0.15 mm/a (i_corr ~96.6 µA cm⁻²) stabilizing at ~0.09 mm/a after 168 h (gao2022corrosionbehaviorof pages 4-5). Anodic features at −525 and −404 mV vs SCE. Sulfide promoted Ni and Fe dissolution and inhibited protective Cu₂O formation (gao2022corrosionbehaviorof pages 4-5). EDS of corrosion products showed Ni declining from 30.8 wt.% at 24 h to 0.6 wt.% at 672 h, consistent with initial Ni enrichment followed by selective leaching under sulfide (gao2022corrosionbehaviorof pages 8-10).

### 4.3 Ecorr and General Corrosion Behavior
**Mantzavinos (2001), PhD thesis, University of Glasgow, DOI: 10.5525/gla.thesis.73974** [CITE]
- Cu-10%Ni in artificial seawater at 20°C: Ecorr approximately −220 to −233 mV; corrosion resistance improved progressively from 2 to 7 days of exposure as the protective film developed (mantzavinos2001durabilitystudiesrelevant pages 123-128). Iron additions are essential for adequate corrosion resistance (mantzavinos2001durabilitystudiesrelevant pages 55-59). Long-term weight-loss rates continued to decline through 7 years in quiet and flowing seawater (mantzavinos2001durabilitystudiesrelevant pages 59-63).

### 4.4 Congruent vs. Selective Dissolution in Cu-Ni
Dissolution of Cu-Ni alloys in seawater is **not congruent**: Cu dissolves preferentially while Ni and Fe are retained in the corrosion product film (mantzavinos2001durabilitystudiesrelevant pages 59-63, kievits1972researchintothe pages 8-9, mantzavinos2001durabilitystudiesrelevant pages 55-59). The solution Ni/Cu ratio is expected to be lower than the bulk alloy ratio, because Ni is incorporated into the protective Cu₂O-based inner oxide. **Quantitative element-resolved dissolution rates in µg cm⁻² day⁻¹ for individual elements (Cu, Ni, Fe, Mn) from ICP analysis of test solutions have not been widely published for Cu-Ni alloys.** [GAP] This is a significant gap that the CubXL program would address.

## 5. Dealuminification of NAB

**Cuevas (2002), MSc thesis** [CITE]
- In nickel-aluminum bronze C95800, the γ₂ phase (also referred to as the γ phase in older nomenclature) preferentially corrodes because its high aluminum content gives it a lower electrochemical potential than the α (Cu-rich) matrix (cuevas2002microstructurecharacterizationof pages 21-26, cuevas2002microstructurecharacterizationofa pages 21-26). The selective dissolution of aluminum from this phase is termed dealuminification (or dealuminization), analogous to dezincification in brass. The corrosion resistance and mechanical properties of the alloy degrade accordingly. Nickel and iron additions extend the α-phase field and help avoid formation of the undesirable γ phase (cuevas2002microstructurecharacterizationof pages 21-26).
- **[GAP]** No quantitative Al/Cu ratio threshold or depth-of-attack data from ICP solution analysis of NAB was found in the retrieved literature. EDS cross-sections of dealuminified NAB are published but element-resolved dissolution fluxes (µg cm⁻² day⁻¹ for Al, Cu, Ni, Fe) have apparently not been measured by online or offline ICP.

## 6. Faradaic Balance and Cu Redeposition

The faradaic balance—whether the charge passed equals the mass of metal dissolved—is problematic for copper alloys for several reasons:

1. **Cu redeposition:** Dissolved Cu⁺ can rapidly redeposit on the electrode surface or on cathodic sites, especially in stagnant solutions. In SFC-ICP-MS at 220 µL min⁻¹, only 4–7% of anodic charge appeared as dissolved Cu during oxidation, and redeposition during reduction brought the cathodic dissolution fraction down to ~1% (speck2020electrochemicalcopperdissolution pages 2-3). In a stagnant 150 µL well, this effect will be more severe.

2. **Corrosion product retention:** Cu₂O, Cu₂(OH)₃Cl, CuCl, and other insoluble products remain on the surface. Ni and Fe are preferentially retained in the film (mantzavinos2001durabilitystudiesrelevant pages 59-63, kievits1972researchintothe pages 8-9). The dissolved metal in solution therefore underestimates total anodic dissolution.

3. **Oxygen reduction current:** On copper alloys in near-neutral aerated chloride, the cathodic current is dominated by O₂ diffusion-limited reduction. This contributes to the net measured current but does not dissolve metal. Separating anodic dissolution charge from cathodic charge requires careful analysis.

4. **AESEC comparison:** In AESEC, the sum of elemental spectral currents (i_sum) can be compared with the convoluted electrical current (i*_e). When i_sum > i*_e, chemical (non-electrochemical) dissolution or dissolution of previously formed corrosion products is occurring (sur2025revisitingtheinfluence pages 13-16). No such analysis has been published for Cu-Ni or NAB.

## 7. Copper Release Rates, Antifouling, and Regulatory Limits

### 7.1 Navy Dome Release Measurements
**Earley et al. (2020), Biofouling 36, 276–291, DOI: 10.1080/08927014.2020.1756267** [CITE] [NUMBERS] [NAVY]
- **Material:** Cu-Ni 90/10 flat sheet and expanded mesh, Cu-Zn 65/35 mesh, silicon bronze, and Cu₂O-coated nylon net; all deployed in San Diego Bay seawater.
- **Method:** Navy Dome enclosure (30.5 cm polycarbonate dome, ~2.8 L sealed volume, 1 h closed-loop circulation, samples at 0/15/30/45/60 min, slope gives release rate in µg cm⁻² d⁻¹) (earley2020estimatesofenvironmental pages 3-5).
- **Key numbers:** Initial copper release from alloys was ~100–200 µg cm⁻² d⁻¹, declining within ~30 days to pseudo-steady-state (PSS) values: **Cu-Ni 90/10 flat sheet 1.4 µg cm⁻² d⁻¹, expanded mesh 3.9 µg cm⁻² d⁻¹**, silicon bronze 2.9 µg cm⁻² d⁻¹, Cu-Zn 65/35 mesh 6.9 µg cm⁻² d⁻¹ (earley2020estimatesofenvironmental pages 10-12, earley2020estimatesofenvironmental pages 8-10). AF-coated nylon net fell below 0.5 µg cm⁻² d⁻¹ (earley2020estimatesofenvironmental pages 10-12).
- **Antifouling threshold:** Materials releasing 1.4–6.9 µg cm⁻² d⁻¹ Cu delayed biofouling for the duration observed, whereas coated net below 0.5 µg cm⁻² d⁻¹ fouled most heavily (earley2020estimatesofenvironmental pages 10-12). Toxicity (sea urchin embryo EC50) correlated linearly with Cu concentration (r² = 0.94) (earley2020estimatesofenvironmental pages 10-12).
- **ICP-MS details:** Samples were acidified to pH 2 with quartz-still-grade HNO₃, diluted in 0.1N HNO₃ when necessary to minimize matrix interference, or preconcentrated on AF-Chelate-650M resin using a flow injection system. Method detection limits: Cu 0.13 µg L⁻¹, Ni 0.19 µg L⁻¹, Zn 0.21 µg L⁻¹; SRM 1643e recoveries 95 ± 7% Cu, 95 ± 7% Ni, 99 ± 6% Zn (earley2020estimatesofenvironmental pages 5-6, earley2020estimatesofenvironmental pages 6-8).
- **[CUBXL]** The one-hour Dome test on a freshly deployed surface corresponds to the "initial release" regime, not the mature-film PSS. CubXL's one-hour tests on freshly polished surfaces will likewise capture initial release, which is ~100× higher than PSS. This must be acknowledged when comparing to field performance.

### 7.2 Cu Release from Laser DED Stainless Steel Coatings
**Hong et al. (2025), npj Mater. Degrad. 9, DOI: 10.1038/s41529-025-00699-z** [CITE] [NUMBERS]
- Laser DED 304L-5Cu and 304L-10Cu coatings in synthetic seawater: initial Cu release peaked at 6.1 and 8.4 µg cm⁻² d⁻¹ (day 4), stabilizing below 1 µg cm⁻² d⁻¹ afterward; cumulative release ~37–40 µg cm⁻² over 42 days versus ~331 µg cm⁻² for a self-polishing copolymer (hong2025catalyticcuionregulation pages 6-7).

### 7.3 EPA Water Quality Criteria
**Paquin et al. (2000), Environ. Sci. Policy 3, 165–174, DOI: 10.1016/S1462-9011(00)00045-9** [CITE] [NUMBERS] [NAVY]
- US EPA revised saltwater criteria: **acute 4.8 µg L⁻¹ and chronic 3.1 µg L⁻¹ dissolved Cu** (paquin2000revisitingtheaquatic pages 4-5). These are receiving-water criteria, not effluent limits. Site-specific Water Effect Ratio (WER) adjustments can increase the effective criterion by factors of 2–9 depending on DOC (paquin2000revisitingtheaquatic pages 5-8).
- **[CUBXL]** These criteria apply to ambient harbor water, not to the concentrated electrolyte inside a test cell. However, when designing experiments whose data will inform environmental assessments, the relationship between alloy release rate and resultant water-column concentration (through dilution and transport modeling) should be noted.

### 7.4 Standard Methods
ASTM D6442 and ISO 15181 (referenced by Earley et al. 2020) are laboratory rotating-cylinder and immersion-based methods designed for antifouling coatings, not bare alloys. They do not produce release-rate data representative of natural environments (earley2020estimatesofenvironmental pages 5-6). The Navy Dome method is considered more accurate for in-situ measurements. For CubXL's O-ring flat-cell geometry, neither standard directly applies, but the ISO 15181 approach of measuring metal concentration increase over time in a defined volume is conceptually analogous.

## 8. Practical Points for 150 µL Samples in 3.5% NaCl

### 8.1 Matrix Effects
A 3.5% NaCl solution contains ~35,000 mg L⁻¹ total dissolved solids. This high sodium/chloride matrix causes signal suppression or enhancement in ICP-OES, altered aerosol generation and nebulizer loading, and polyatomic interferences in ICP-MS (e.g., ⁴⁰Ar²³Na⁺ on ⁶³Cu) (smanova2026ecologicalsignificancesources pages 22-23, smanova2026ecologicalsignificancesources pages 13-15). Mitigation requires dilution, matrix-matched standards, internal standards, and/or collision/reaction cell (He-KED) mode for ICP-MS (smanova2026ecologicalsignificancesources pages 13-15, smanova2026ecologicalsignificancesources pages 12-13).

### 8.2 Dilution and Detection Limits
A 150 µL sample at ~1 µg cm⁻² d⁻¹ release over 0.1 cm² for 1 hour would yield only ~4 ng total Cu, or ~27 µg L⁻¹ Cu in 150 µL. After 10× dilution to reduce the NaCl matrix to ~0.35% (acceptable for most ICP instruments), the concentration drops to ~2.7 µg L⁻¹. This is well above the ICP-MS detection limits achieved by Earley et al. (~0.13 µg L⁻¹ Cu) (earley2020estimatesofenvironmental pages 5-6) but may challenge ICP-OES, whose typical detection limits for Cu are ~1–5 µg L⁻¹. For minor alloy components (Ni at 10–30% of the alloy, Fe at 0.4–1%, Mn at ~1%), the dissolved concentration will be proportionally lower and may require preconcentration or ICP-MS rather than ICP-OES.

### 8.3 Acidification and Container Losses
Earley et al. acidified samples to pH 2 with quartz-still HNO₃ immediately after collection in an ultra-clean HEPA environment (earley2020estimatesofenvironmental pages 5-6). Copper and other transition metals adsorb to polypropylene tube walls at neutral pH, particularly at low concentrations. Prompt acidification to pH < 2 with trace-metal-grade HNO₃ is critical. The CubXL robot should dispense acid into the collection tube before or immediately after pipetting the post-test electrolyte.

### 8.4 ICP-OES vs ICP-MS
For 150 µL volumes: ICP-MS is preferred because of its 10–100× lower detection limits, multi-element capability, and lower sample-volume requirements (many modern ICP-MS systems can handle 100–200 µL with micro-nebulizers). ICP-OES is more tolerant of high TDS but requires ~1–5 mL per measurement, necessitating pooling of wells or significant dilution. For the 150 µL CubXL protocol, ICP-MS with He-KED is the recommended technique.

## 9. Gaps Identified

The literature does not answer several parts of the question:

1. **[GAP] No AESEC study on Cu-Ni 90/10, 70/30, or multi-phase NAB.** The closest published AESEC work on Cu-Al alloys (Sur et al. 2025) used single-phase solid solutions in sulfate, not commercial NAB in chloride. Peng Zhou's 2017 PhD thesis (Chimie ParisTech/Ogle group) on "selective dissolution mechanism of Cu alloys" via AESEC was identified but could not be retrieved; it may contain relevant data.

2. **[GAP] No SFC-ICP-MS on Cu-Ni alloys or NAB.** SFC-ICP-MS has been applied to pure Cu (Speck & Cherevko 2020) and Cu catalysts (Vavra et al. 2024), but not to naval copper alloys in chloride or seawater.

3. **[GAP] Quantitative element-resolved dissolution rates (µg cm⁻² d⁻¹ for Cu, Ni, Fe, Mn, Al individually) from offline ICP of test solutions are extremely scarce for Cu-Ni and NAB.** Published corrosion studies mostly report total weight loss or electrochemical icorr, not element-specific solution concentrations.

4. **[GAP] No published faradaic balance for Cu-Ni or NAB in chloride.** The extent to which dissolved metal agrees with passed charge on these alloys remains unmeasured.

5. **[GAP] No antifouling Cu-release threshold specifically for NAB.** Earley et al. measured Cu-Ni 90/10 and Cu-Zn alloys but not NAB.

## 10. Top 5 Changes to the Small-Cell Plan for Copper Alloys

**Rank 1: Acidify recovered electrolyte immediately.** Cu⁺ redeposits rapidly on the alloy surface or precipitates as CuCl/Cu₂O in near-neutral stagnant electrolyte. The robot must dispense concentrated trace-metal-grade HNO₃ into each collection tube (target pH < 2) before or within seconds of aspirating the post-test solution. Without this, ICP results will systematically undercount Cu dissolution (vavra2024solutionbasedcu+transient pages 5-9, speck2020electrochemicalcopperdissolution pages 2-3).

**Rank 2: Choose ICP-MS (not ICP-OES) and plan for matrix dilution.** The 150 µL sample in 3.5% NaCl is too small and too saline for conventional ICP-OES. ICP-MS with He-KED collision cell and micro-nebulizer can handle the volume and matrix after 5–10× dilution, achieving sub-µg/L limits for Cu, Ni, Fe, Al, and Mn. If ICP-OES must be used, pool multiple wells to reach the required ~2 mL volume (smanova2026ecologicalsignificancesources pages 22-23, smanova2026ecologicalsignificancesources pages 13-15, earley2020estimatesofenvironmental pages 5-6).

**Rank 3: Supplement solution ICP with post-test surface analysis.** Cu-Ni and NAB dissolution is strongly non-congruent: Ni, Fe, and (in NAB) Al are retained in the corrosion product film while Cu dissolves preferentially. Solution ICP alone misses the retained species. After each test, photograph the spot (already planned), then analyze representative spots by SEM-EDS or portable XRF to measure the film composition and quantify Ni/Fe enrichment. The Al/Cu ratio in the corrosion products can serve as an indicator of selective phase attack in NAB (mantzavinos2001durabilitystudiesrelevant pages 59-63, kievits1972researchintothe pages 8-9, cuevas2002microstructurecharacterizationof pages 21-26).

**Rank 4: Interpret one-hour tests as "initial release" only.** One-hour electrochemical tests on freshly polished surfaces measure the high initial release regime (~100–200 µg cm⁻² d⁻¹ equivalent for Cu-Ni), not the pseudo-steady-state release that develops over 30+ days (PSS 1.4–6.9 µg cm⁻² d⁻¹) (earley2020estimatesofenvironmental pages 10-12, earley2020estimatesofenvironmental pages 8-10). Rankings between alloys may not translate to long-term performance. Consider running a subset of wells as multi-day static immersion (refilling electrolyte daily) to capture the film-maturation effect (mantzavinos2001durabilitystudiesrelevant pages 59-63).

**Rank 5: Do not assume a reliable Stern-Geary B or attempt Tafel fitting.** On Cu-Ni alloys in aerated near-neutral chloride, the cathodic branch is O₂-diffusion-limited and Tafel extrapolation is unreliable (as established). Additionally, the faradaic balance between passed charge and dissolved metal is poor because of Cu redeposition and insoluble corrosion products. Use the ICP-derived dissolution rate as the primary corrosion metric rather than electrochemical icorr. Compute element-specific dissolution currents from ICP concentrations using i_M = n_M · F · (mass dissolved) / (area × time), following the AESEC framework, and compare with the electrochemical charge to assess the "missing" fraction retained on the surface (speck2020electrochemicalcopperdissolution pages 2-3, sur2025revisitingtheinfluence pages 8-10, sur2025revisitingtheinfluence pages 13-16).


References

1. (sur2025revisitingtheinfluence pages 16-19): Debashish Sur, Nathan C. Smith, Elaf A. Anber, Kaitlyn L. Anderson, Peter F. Connors, Daniel Foley, Mitra L. Taheri, Junsoo Han, Christopher M. Wolverton, and John R. Scully. Revisiting the influence of sn in cu-al alloys: a <i>third element effect</i> enabling stainless steel type corrosion behavior. Journal of The Electrochemical Society, 172(10):101502, Oct 2025. URL: https://doi.org/10.1149/1945-7111/ae0eb6, doi:10.1149/1945-7111/ae0eb6. This article has 6 citations and is from a peer-reviewed journal.

2. (sur2025revisitingtheinfluence pages 8-10): Debashish Sur, Nathan C. Smith, Elaf A. Anber, Kaitlyn L. Anderson, Peter F. Connors, Daniel Foley, Mitra L. Taheri, Junsoo Han, Christopher M. Wolverton, and John R. Scully. Revisiting the influence of sn in cu-al alloys: a <i>third element effect</i> enabling stainless steel type corrosion behavior. Journal of The Electrochemical Society, 172(10):101502, Oct 2025. URL: https://doi.org/10.1149/1945-7111/ae0eb6, doi:10.1149/1945-7111/ae0eb6. This article has 6 citations and is from a peer-reviewed journal.

3. (sur2025revisitingtheinfluence pages 13-16): Debashish Sur, Nathan C. Smith, Elaf A. Anber, Kaitlyn L. Anderson, Peter F. Connors, Daniel Foley, Mitra L. Taheri, Junsoo Han, Christopher M. Wolverton, and John R. Scully. Revisiting the influence of sn in cu-al alloys: a <i>third element effect</i> enabling stainless steel type corrosion behavior. Journal of The Electrochemical Society, 172(10):101502, Oct 2025. URL: https://doi.org/10.1149/1945-7111/ae0eb6, doi:10.1149/1945-7111/ae0eb6. This article has 6 citations and is from a peer-reviewed journal.

4. (hou2026trackingelementspecificdissolution pages 1-2): Yaojun Hou, Oumaïma Gharbi, Chenyang Xie, Divino Salvador Ramírez Rico, Fan Sun, Mireille Turmine, Kevin Ogle, and Vincent Vivier. Tracking element-specific dissolution during pitting corrosion: an operando icp-aes–electrochemical study of the cocrfemnni cantor alloy. npj Materials Degradation, Feb 2026. URL: https://doi.org/10.1038/s41529-026-00747-2, doi:10.1038/s41529-026-00747-2. This article has 3 citations and is from a peer-reviewed journal.

5. (hou2026trackingelementspecificdissolution pages 6-7): Yaojun Hou, Oumaïma Gharbi, Chenyang Xie, Divino Salvador Ramírez Rico, Fan Sun, Mireille Turmine, Kevin Ogle, and Vincent Vivier. Tracking element-specific dissolution during pitting corrosion: an operando icp-aes–electrochemical study of the cocrfemnni cantor alloy. npj Materials Degradation, Feb 2026. URL: https://doi.org/10.1038/s41529-026-00747-2, doi:10.1038/s41529-026-00747-2. This article has 3 citations and is from a peer-reviewed journal.

6. (speck2020electrochemicalcopperdissolution pages 1-2): Florian D. Speck and Serhiy Cherevko. Electrochemical copper dissolution: a benchmark for stable co2 reduction on copper electrocatalysts. Electrochemistry Communications, 115:106739, Jun 2020. URL: https://doi.org/10.1016/j.elecom.2020.106739, doi:10.1016/j.elecom.2020.106739. This article has 135 citations and is from a peer-reviewed journal.

7. (speck2020electrochemicalcopperdissolution pages 2-3): Florian D. Speck and Serhiy Cherevko. Electrochemical copper dissolution: a benchmark for stable co2 reduction on copper electrocatalysts. Electrochemistry Communications, 115:106739, Jun 2020. URL: https://doi.org/10.1016/j.elecom.2020.106739, doi:10.1016/j.elecom.2020.106739. This article has 135 citations and is from a peer-reviewed journal.

8. (vavra2024solutionbasedcu+transient pages 5-9): Jan Vavra, Gaétan P. L. Ramona, Federico Dattila, Attila Kormányos, Tatiana Priamushko, Petru P. Albertini, Anna Loiudice, Serhiy Cherevko, Núria Lopéz, and Raffaella Buonsanti. Solution-based cu+ transient species mediate the reconstruction of copper electrocatalysts for co2 reduction. Nature Catalysis, 7:89-97, Jan 2024. URL: https://doi.org/10.1038/s41929-023-01070-8, doi:10.1038/s41929-023-01070-8. This article has 278 citations and is from a domain leading peer-reviewed journal.

9. (vavra2024solutionbasedcu+transient pages 12-16): Jan Vavra, Gaétan P. L. Ramona, Federico Dattila, Attila Kormányos, Tatiana Priamushko, Petru P. Albertini, Anna Loiudice, Serhiy Cherevko, Núria Lopéz, and Raffaella Buonsanti. Solution-based cu+ transient species mediate the reconstruction of copper electrocatalysts for co2 reduction. Nature Catalysis, 7:89-97, Jan 2024. URL: https://doi.org/10.1038/s41929-023-01070-8, doi:10.1038/s41929-023-01070-8. This article has 278 citations and is from a domain leading peer-reviewed journal.

10. (earley2020estimatesofenvironmental pages 1-3): Patrick J. Earley, Brandon L. Swope, Marienne A. Colvin, Gunther Rosen, Pei-Fang Wang, Jessica Carilli, and Ignacio Rivera-Duarte. Estimates of environmental loading from copper alloy materials. Biofouling, 36:276-291, Mar 2020. URL: https://doi.org/10.1080/08927014.2020.1756267, doi:10.1080/08927014.2020.1756267. This article has 12 citations and is from a peer-reviewed journal.

11. (earley2020estimatesofenvironmental pages 5-6): Patrick J. Earley, Brandon L. Swope, Marienne A. Colvin, Gunther Rosen, Pei-Fang Wang, Jessica Carilli, and Ignacio Rivera-Duarte. Estimates of environmental loading from copper alloy materials. Biofouling, 36:276-291, Mar 2020. URL: https://doi.org/10.1080/08927014.2020.1756267, doi:10.1080/08927014.2020.1756267. This article has 12 citations and is from a peer-reviewed journal.

12. (earley2020estimatesofenvironmental pages 6-8): Patrick J. Earley, Brandon L. Swope, Marienne A. Colvin, Gunther Rosen, Pei-Fang Wang, Jessica Carilli, and Ignacio Rivera-Duarte. Estimates of environmental loading from copper alloy materials. Biofouling, 36:276-291, Mar 2020. URL: https://doi.org/10.1080/08927014.2020.1756267, doi:10.1080/08927014.2020.1756267. This article has 12 citations and is from a peer-reviewed journal.

13. (earley2020estimatesofenvironmental pages 10-12): Patrick J. Earley, Brandon L. Swope, Marienne A. Colvin, Gunther Rosen, Pei-Fang Wang, Jessica Carilli, and Ignacio Rivera-Duarte. Estimates of environmental loading from copper alloy materials. Biofouling, 36:276-291, Mar 2020. URL: https://doi.org/10.1080/08927014.2020.1756267, doi:10.1080/08927014.2020.1756267. This article has 12 citations and is from a peer-reviewed journal.

14. (gao2022corrosionbehaviorof pages 4-5): Xin Gao and Ming Liu. Corrosion behavior of high-strength c71500 copper-nickel alloy in simulated seawater with high concentration of sulfide. Materials, 15:8513, Nov 2022. URL: https://doi.org/10.3390/ma15238513, doi:10.3390/ma15238513. This article has 34 citations.

15. (gao2022corrosionbehaviorof pages 8-10): Xin Gao and Ming Liu. Corrosion behavior of high-strength c71500 copper-nickel alloy in simulated seawater with high concentration of sulfide. Materials, 15:8513, Nov 2022. URL: https://doi.org/10.3390/ma15238513, doi:10.3390/ma15238513. This article has 34 citations.

16. (kievits1972researchintothe pages 8-9): F. J. Kievits and F. P. Ijsseling. Research into the corrosion behaviour of cuni10fe alloys in seawater. Materials and Corrosion-werkstoffe Und Korrosion, 23:1084-1096, Dec 1972. URL: https://doi.org/10.1002/maco.19720231203, doi:10.1002/maco.19720231203. This article has 23 citations and is from a peer-reviewed journal.

17. (mantzavinos2001durabilitystudiesrelevant pages 59-63): Dimitris Mantzavinos. Durability studies relevant to marine equipment. Text, Jan 2001. URL: https://doi.org/10.5525/gla.thesis.73974, doi:10.5525/gla.thesis.73974. This article has 1 citations and is from a peer-reviewed journal.

18. (mantzavinos2001durabilitystudiesrelevant pages 55-59): Dimitris Mantzavinos. Durability studies relevant to marine equipment. Text, Jan 2001. URL: https://doi.org/10.5525/gla.thesis.73974, doi:10.5525/gla.thesis.73974. This article has 1 citations and is from a peer-reviewed journal.

19. (paquin2000revisitingtheaquatic pages 4-5): Paul R Paquin, Robert C Santore, Kuen B Wu, Paul J Anid, Christos D Kavvadas, and Dominic M Di Toro. Revisiting the aquatic impacts of copper discharged by water-cooled copper alloy condensers used by power and desalination plants. Environmental Science & Policy, 3:165-174, Sep 2000. URL: https://doi.org/10.1016/s1462-9011(00)00045-9, doi:10.1016/s1462-9011(00)00045-9. This article has 16 citations and is from a domain leading peer-reviewed journal.

20. (paquin2000revisitingtheaquatic pages 5-8): Paul R Paquin, Robert C Santore, Kuen B Wu, Paul J Anid, Christos D Kavvadas, and Dominic M Di Toro. Revisiting the aquatic impacts of copper discharged by water-cooled copper alloy condensers used by power and desalination plants. Environmental Science & Policy, 3:165-174, Sep 2000. URL: https://doi.org/10.1016/s1462-9011(00)00045-9, doi:10.1016/s1462-9011(00)00045-9. This article has 16 citations and is from a domain leading peer-reviewed journal.

21. (sur2025revisitingtheinfluence pages 19-22): Debashish Sur, Nathan C. Smith, Elaf A. Anber, Kaitlyn L. Anderson, Peter F. Connors, Daniel Foley, Mitra L. Taheri, Junsoo Han, Christopher M. Wolverton, and John R. Scully. Revisiting the influence of sn in cu-al alloys: a <i>third element effect</i> enabling stainless steel type corrosion behavior. Journal of The Electrochemical Society, 172(10):101502, Oct 2025. URL: https://doi.org/10.1149/1945-7111/ae0eb6, doi:10.1149/1945-7111/ae0eb6. This article has 6 citations and is from a peer-reviewed journal.

22. (sur2025revisitingtheinfluence pages 10-13): Debashish Sur, Nathan C. Smith, Elaf A. Anber, Kaitlyn L. Anderson, Peter F. Connors, Daniel Foley, Mitra L. Taheri, Junsoo Han, Christopher M. Wolverton, and John R. Scully. Revisiting the influence of sn in cu-al alloys: a <i>third element effect</i> enabling stainless steel type corrosion behavior. Journal of The Electrochemical Society, 172(10):101502, Oct 2025. URL: https://doi.org/10.1149/1945-7111/ae0eb6, doi:10.1149/1945-7111/ae0eb6. This article has 6 citations and is from a peer-reviewed journal.

23. (mantzavinos2001durabilitystudiesrelevant pages 123-128): Dimitris Mantzavinos. Durability studies relevant to marine equipment. Text, Jan 2001. URL: https://doi.org/10.5525/gla.thesis.73974, doi:10.5525/gla.thesis.73974. This article has 1 citations and is from a peer-reviewed journal.

24. (cuevas2002microstructurecharacterizationof pages 21-26): AM Cuevas. Microstructure characterization of friction-stir processed nickel. Unknown journal, 2002.

25. (cuevas2002microstructurecharacterizationofa pages 21-26): AM Cuevas. Microstructure characterization of friction-stir processed nickel. Unknown journal, 2002.

26. (earley2020estimatesofenvironmental pages 3-5): Patrick J. Earley, Brandon L. Swope, Marienne A. Colvin, Gunther Rosen, Pei-Fang Wang, Jessica Carilli, and Ignacio Rivera-Duarte. Estimates of environmental loading from copper alloy materials. Biofouling, 36:276-291, Mar 2020. URL: https://doi.org/10.1080/08927014.2020.1756267, doi:10.1080/08927014.2020.1756267. This article has 12 citations and is from a peer-reviewed journal.

27. (earley2020estimatesofenvironmental pages 8-10): Patrick J. Earley, Brandon L. Swope, Marienne A. Colvin, Gunther Rosen, Pei-Fang Wang, Jessica Carilli, and Ignacio Rivera-Duarte. Estimates of environmental loading from copper alloy materials. Biofouling, 36:276-291, Mar 2020. URL: https://doi.org/10.1080/08927014.2020.1756267, doi:10.1080/08927014.2020.1756267. This article has 12 citations and is from a peer-reviewed journal.

28. (hong2025catalyticcuionregulation pages 6-7): Heting Hong, Lijia Chen, Zhen Zhou, Chunguang Yang, Yan-Ge Yang, Lingrui Zha, Xin-Rui Zhang, Min Liu, Jin-Long Zhao, Guijun Bi, and Ke Yang. Catalytic cu-ion regulation in laser-directed energy deposited stainless steel coatings for sustainable surface biofouling mitigation. npj Materials Degradation, Nov 2025. URL: https://doi.org/10.1038/s41529-025-00699-z, doi:10.1038/s41529-025-00699-z. This article has 1 citations and is from a peer-reviewed journal.

29. (smanova2026ecologicalsignificancesources pages 22-23): Z Smanova, D Azimova, and J Todjiev. Ecological significance, sources, and analytical determination methods of chromium and zinc in environmental objects: a critical review. Unknown journal, 2026.

30. (smanova2026ecologicalsignificancesources pages 13-15): Z Smanova, D Azimova, and J Todjiev. Ecological significance, sources, and analytical determination methods of chromium and zinc in environmental objects: a critical review. Unknown journal, 2026.

31. (smanova2026ecologicalsignificancesources pages 12-13): Z Smanova, D Azimova, and J Todjiev. Ecological significance, sources, and analytical determination methods of chromium and zinc in environmental objects: a critical review. Unknown journal, 2026.
