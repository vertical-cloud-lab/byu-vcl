<!--
Edison Scientific LITERATURE task (batch 1)
- Task ID: 89ec074c-6d1b-42a3-9f97-25c1aced8bb6
- Submitted: 2026-10-18T01:20:09Z
- Fetched: 2026-10-18T01:39:53Z (status: success)
- Raw trajectory JSON: ../raw/c1-10-coulometric-oxide-reduction-cu.json.gz
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

QUESTION: Can coulometric (cathodic) reduction, such as sequential
electrochemical reduction analysis (SERA) or galvanostatic or linear-sweep
reduction in borate buffer or KCl, quantify oxides and corrosion products on
copper alloys with the same low-cost potentiostat? Cover (a) films formed on
Cu-Ni and NAB in seawater (Cu2O, CuO, Cu2(OH)3Cl, Ni- and Fe-rich layers):
reduction potentials, charge-to-thickness conversion, precision, and
agreement with XPS or other methods; (b) the native oxide on copper alloy
powders or polished surfaces, and whether reduction of a powder (for example
in a cavity microelectrode or a packed-powder electrode) has been used to
estimate the oxide thickness or oxygen content of metal powders, compared
with inert-gas-fusion oxygen analysis; (c) interference from Ni, Fe, Al and
Mn oxides that do not reduce in the same potential window. Report the
electrolyte, current density and detection limit (nm or mC/cm2).

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

QUESTION: Can coulometric (cathodic) reduction, such as sequential
electrochemical reduction analysis (SERA) or galvanostatic or linear-sweep
reduction in borate buffer or KCl, quantify oxides and corrosion products on
copper alloys with the same low-cost potentiostat? Cover (a) films formed on
Cu-Ni and NAB in seawater (Cu2O, CuO, Cu2(OH)3Cl, Ni- and Fe-rich layers):
reduction potentials, charge-to-thickness conversion, precision, and
agreement with XPS or other methods; (b) the native oxide on copper alloy
powders or polished surfaces, and whether reduction of a powder (for example
in a cavity microelectrode or a packed-powder electrode) has been used to
estimate the oxide thickness or oxygen content of metal powders, compared
with inert-gas-fusion oxygen analysis; (c) interference from Ni, Fe, Al and
Mn oxides that do not reduce in the same potential window. Report the
electrolyte, current density and detection limit (nm or mC/cm2).

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


# Cathodic oxide coulometry for naval copper alloys

**Conclusion.** A potentiostat capable of controlled low-microampere currents, recording potential versus time, and integrating current can perform galvanostatic oxide reduction on a copper-alloy coupon. That does **not** make its charge a measurement of *total* oxide thickness: the strongest demonstrations concern copper-rich products on flat Cu or simple Cu–Al alloys, not phase-resolved, months-old seawater films on Cu–Ni or nickel–aluminum bronze (NAB). Use cathodic coulometry as a calibrated, **destructive measurement of reducible film charge**, on a separate spot *after* corrosion exposure; use XPS/Raman and microscopy to establish what that charge represents. Published SERA cells also differ materially from a 150-µL, air-open corrosion well: they exclude oxygen and isolate the counter electrode. (tench1994solderabilityassessmentvia pages 1-2, tench1994solderabilityassessmentvia pages 5-6, tench1994solderabilityassessmentvia pages 9-11, hutchison2018solutecaptureand pages 2-3)

**Reporting convention.** Potentials below are versus the electrode named in each item; calculated equilibrium potentials are not experimental peak positions. “Not reported” means a value could not be verified in the cited account, not that it is zero. None of the oxide-metrology papers reports the requested naval-alloy *E*₍corr₎, *R*ₚ, *i*₍corr₎, breakdown/protection potential, elemental dissolution rate, or depth of attack unless specifically noted.

## Evidence directly bearing on the reduction measurement

1. **[CITE] [NUMBERS] [CUBXL]** D. Morgan Tench, D. P. Anderson and P. Kim, “Solderability assessment via sequential electrochemical reduction analysis,” *Journal of Applied Electrochemistry* **24**, 18–29 (1994), **DOI: 10.1007/BF00243325**. Materials were chiefly hot-tin-dipped copper wire, with separate tests of copper and other bulk-metal specimens; **not Cu–Ni or NAB**. A bulk, approximately **200-mL** cell held argon-saturated **pH 8.4 borate** (9.55 g/L sodium borate plus 6.18 g/L boric acid); SCE and Pt counter occupied separate fritted compartments. Areas for specimen tests were **0.5–7 cm²**; the authors also described O-ring pad/through-hole geometries, including **1.6-mm-ID** rings. Typical reduction current was **−20 µA/cm²**. Calculated equilibrium potentials at this pH were CuO/Cu **−0.168 V**, Cu₂O/Cu **−0.267 V**, NiO/Ni **−0.628 V**, Ni(OH)₂/Ni **−0.622 V**, Fe₂O₃/Fe **−0.789 V**, and Fe₃O₄/Fe **−0.823 V**, all **versus SCE**; observed copper-oxide reduction generally occupied **−0.3 to −0.6 V versus SCE**. For their prepared **tin** oxides, three retained measurements had **<10% standard deviation**; that is *not* demonstrated Cu–Ni/NAB precision. No Cu-alloy seawater-film detection limit was established. **Robot implication:** inert-gas handling and Pt-counter isolation are essential controls before claiming an oxide charge. (tench1994solderabilityassessmentvia pages 1-2, tench1994solderabilityassessmentvia pages 3-5, tench1994solderabilityassessmentvia pages 5-6, tench1994solderabilityassessmentvia pages 9-11)

2. **[CITE] [NUMBERS] [CUBXL]** Mauricio Ramirez, Lothar Henneken and Sannakaisa Virtanen, “Oxidation kinetics of thin copper films and wetting behaviour of copper and Organic Solderability Preservatives (OSP) with lead-free solder,” *Applied Surface Science* **257**, 6481–6488 (2011), **DOI: 10.1016/j.apsusc.2011.02.048**. Material: approximately **3.5-µm polycrystalline Cu deposited on Si**, air-oxidized at **100–260 °C**; not a marine alloy. SERA used **pH 8.4 borate**, **−30 µA/cm²**, and a commercial surface-scanning analyzer; cell volume and exposed area were not specified in the retrieved methods. The initial Cu₂O was approximately **4 nm**. A reflow-treated calibration specimen had approximately **37 nm Cu₂O** by XPS depth profiling and a **CuO overlayer <2 nm**, which SERA **did not detect**; the measured Cu(II) surface fraction was **8.7 ± 0.9%**. The reported Cu₂O plateau was approximately **−0.45 V** in the instrument’s reduction curves; the retrieved description does not establish the reference for that particular plotted voltage. This study’s practical sensitivity was **insufficient below approximately 2 nm**, *not* a universal instrumental limit. PCB copper roughness made SERA insufficiently repeatable, and an organic coating prevented reliable oxide measurement. SERA/SIMS comparisons cited by the authors disagreed particularly during the first **30 min** of oxidation; XPS did not simply validate all SERA-derived thicknesses. **Robot implication:** polish and measure roughness; validate native-film sensitivity separately for each alloy and finish. (ramirez2011oxidationkineticsof pages 2-3, ramirez2011oxidationkineticsof pages 3-5, ramirez2011oxidationkineticsof pages 1-2, ramirez2011oxidationkineticsof pages 6-7)

3. **[CITE] [NUMBERS] [CUBXL]** M. J. Hutchison and J. R. Scully, “Solute capture and doping of Al in Cu₂O: Corrosion, tarnish resistance, and cation release of high-purity Cu–Al alloys in artificial perspiration,” *Journal of The Electrochemical Society* **165**, C689–C702 (2018), **DOI: 10.1149/2.1301810jes**. Material: **argon-arc-melted, solution-treated Cu–Al**, measured Al contents **0.09, 0.99 and 4.78 wt%**, balance Cu; **not cast NAB or laser DED**. Corrosion exposures were in artificial perspiration; the separate oxide-reduction cell contained approximately **400 mL nitrogen-deaerated pH 8.4 borate** (**0.11 M boric acid, 0.02 M sodium tetraborate**), on an **0.8-cm²** O-ring-defined area. Applied current was **−20 µA total = −25 µA/cm²**, with potential measured versus a **mercury/mercurous sulfate electrode (MMSE)**. Reduction curves followed exposures through **130 h**; XPS/Raman characterized **96-h** films, while soluble Cu was assessed by ICP-OES. The study explicitly calculated oxide charge from **current density × plateau duration** and an *assumed* Cu₂O density of **6.0 g/cm³**. Al incorporation into Cu₂O changed its electrical properties, so the plateau can shift with composition independently of thickness; the plotted Al₂O₃/Al equilibrium is around **−2.6 V versus MMSE**, inaccessible to practical aqueous oxide coulometry. The reported experiments do **not** establish a seawater NAB calibration, powder oxygen assay, detection limit, or transferable XPS-versus-charge precision. **Robot implication:** reserve neighboring Cu–Al/NAB spots for reduction and XPS, rather than treating one potential as an invariant phase label. (hutchison2018solutecaptureand pages 2-3, hutchison2018solutecaptureand pages 1-1, hutchison2018solutecaptureand pages 8-9)

4. **[CITE] [CUBXL]** U. Bertocci, “An EQMB examination of Cu surface oxides in borate buffer,” *Electrochimica Acta* **49**, 1831–1841 (2004), **DOI: 10.1016/j.electacta.2003.11.033**. Material: electrodeposited or vapor-deposited **Cu**, including Cu on quartz-crystal microbalances, not naval alloy. Bulk **pH 8.8 and 10 borate** solutions were nitrogen-deaerated; geometric cell area/solution volume were not established in the extracted passages. Experiments included **5 mV/s** scans and galvanostatic reduction, including **−30 µA/cm²**. Simultaneous mass and charge showed that an apparent cathodic “oxide” peak at pH 8.8 could instead involve **redeposition of Cu dissolved on the anodic scan**. At pH 10, a reported example recovered **108.8 of 111.6 nanoequivalents** assigned to oxygen uptake, yet estimated real area was **1.5–2 times** geometric area even for electrodeposited Cu. The roughly **1–2%** quoted microbalance-calibration uncertainty is *not* oxide-thickness accuracy. **Robot implication:** run unoxidized blanks, avoid preceding anodic scans on reduction-assay spots, and do not integrate every cathodic peak as oxide. (bertocci2004aneqmbexamination pages 2-5, bertocci2004aneqmbexamination pages 7-8)

5. **[CITE]** Masahiro Seo, Xiang Chun Jiang and Norio Sato, “Photoacoustic study on cathodic reduction of anodic oxide films formed on copper in borate solution,” *Materials and Corrosion/Werkstoffe und Korrosion* **39**, 583–588 (1988), **DOI: 10.1002/maco.19880391205**. Material: anodically oxidized flat **Cu**, including **20-min** formation at **0.4 or 0.8 V versus SHE**. Cell volume/area were not reported in the accessible passage. Electrolyte was **nitrogen-deaerated pH 8.4 borate, 0.3 mol/L total boron**; Pt counter, saturated-KCl Ag/AgCl reference, and **10 mV/s** reduction sweeps were used. Photoacoustics resolved an outer-layer reduction toward Cu₂O and a subsequent Cu₂O-to-Cu response; optical response differed with the potential used to make the film. It is an independent mechanistic cross-check, not a quantitative Cu–Ni seawater-film precision or detection-limit study. (seo1988photoacousticstudyon pages 2-3, seo1988photoacousticstudyon pages 3-5)

**Charge-to-thickness calculation.** For an identified, continuous oxide of uniform thickness, use *d* = (*Q/A*)*M*/(*nFρ*). Assuming Cu₂O density **6.0 g/cm³** and **two electrons per Cu₂O formula unit**, **1 nm Cu₂O ≈ 0.81 mC/cm²**. Assuming CuO density **6.31 g/cm³** and two electrons to Cu, **1 nm CuO ≈ 2.1 mC/cm²**; **CuO → Cu₂O** would require a different electron accounting. These are **stoichiometric calculations, not reported method detection limits**. Thus, on a **0.07–0.13-cm²** well, 1 nm of ideal Cu₂O corresponds to roughly **57–105 µC** total; at **20–30 µA/cm²**, the requested whole-well current is only **1.4–3.9 µA**. At **25 µA/cm²**, 1 ideal Cu₂O nanometre takes approximately **32 s**, before blank and efficiency corrections. For porous/rough, chloride-bearing seawater products, report **mC/cm² geometric area** first, and convert to an “equivalent Cu₂O thickness” only with a clearly labeled phase, density, roughness and faradaic-efficiency assumption. The Cu–Al paper supplies the equation and density assumption; the Cu-film paper demonstrates why a calculated sub-2-nm signal need not be detectable. (tench1994solderabilityassessmentvia pages 1-2, ramirez2011oxidationkineticsof pages 2-3, hutchison2018solutecaptureand pages 2-3)

| Species | Defensible measurement or limitation | Approximate charge density |
|---|---|---:|
| Cu₂O | In deaerated pH 8.4 borate, Cu-oxide reduction occurs experimentally around −0.3 to −0.6 V vs SCE; thermodynamic Cu₂O/Cu value is −0.267 V vs SCE. Ramirez detected an approximately 4 nm native Cu₂O film. Hutchison used −25 µA/cm² for Cu–Al alloys. (tench1994solderabilityassessmentvia pages 1-2, ramirez2011oxidationkineticsof pages 1-2, hutchison2018solutecaptureand pages 2-3) | **0.81 mC/cm² per nm**, calculated with ρ = 6.0 g/cm³ and 2 e⁻ per Cu₂O formula unit |
| CuO | Thermodynamic CuO/Cu value is −0.168 V vs SCE, but kinetic shifts and mixed/duplex films prevent phase assignment from potential alone. SERA missed an XPS-detected CuO overlayer thinner than 2 nm. (tench1994solderabilityassessmentvia pages 1-2, ramirez2011oxidationkineticsof pages 2-3) | **2.1 mC/cm² per nm**, calculated with ρ = 6.31 g/cm³ and 2 e⁻ per CuO formula unit |
| Cu₂(OH)₃Cl | No validated, phase-specific reduction potential or coulometric conversion was located for Cu-alloy seawater films; overlapping Cu-oxide/chloride-product reduction is therefore unresolved. | Not established |
| NiO / Ni(OH)₂ | Thermodynamic values at pH 8.4 are −0.628 and −0.622 V vs SCE, respectively. Nickel oxides are described as recalcitrant; incomplete reduction and hydrogen-evolution overlap make quantitative charge unreliable without calibration. (tench1994solderabilityassessmentvia pages 1-2, tench1994solderabilityassessmentvia pages 9-11, tench1994solderabilityassessmentvia pages 11-12) | Not reliably convertible |
| Fe₂O₃ and other Fe oxides | Thermodynamic Fe₂O₃ value is −0.789 V vs SCE; Fe₃O₄ is −0.823 V vs SCE. Iron-oxide chronopotentiometry is at best semiquantitative because dissolution, mixed phases, and hydrogen evolution can interfere. (tench1994solderabilityassessmentvia pages 1-2, tench1994solderabilityassessmentvia pages 9-11) | Not reliably convertible |
| Al₂O₃ / Al-rich oxide | Aluminum oxide is too stable for reduction to Al in aqueous electrolyte; the cited Al₂O₃/Al value is about −2.6 V vs MMSE, outside the aqueous window. Its charge is absent from Cu-oxide coulometry rather than proof that Al oxide is absent. (tench1994solderabilityassessmentvia pages 9-11, hutchison2018solutecaptureand pages 8-9) | Not aqueous-reducible |
| Mn oxides | No validated reduction potential, charge-to-thickness factor, or selectivity benchmark was located for Mn-bearing Cu-alloy films in borate or KCl. | Unknown |


*Table: Phase-specific potentials and charge conversions that are defensible for cathodic reduction of copper-alloy films. The table separates calibrated Cu-oxide signals from alloying-element oxides that are unresolved or inaccessible in aqueous electrolyte.*

## What the marine-alloy studies establish—and do not establish

6. **[CITE] [NUMBERS] [NAVY] [CUBXL]** Tingzhu Jin, Weifang Zhang, Ning Li, Xuerong Liu, Lu Han and Wei Dai, “Surface Characterization and Corrosion Behavior of 90/10 Copper-Nickel Alloy in Marine Environment,” *Materials* **12**, 1869 (2019), **DOI: 10.3390/ma12111869**. Material: polished **Cu–Ni sheet**, **9.76 Ni, 1.20 Fe, 0.74 Mn wt%**, minor Zn/P/Si/S, Cu balance; not a DED deposit. Coupons were **100 × 50 × 3 mm**; electrochemical exposed area and solution volume were not stated. Exposures were **0, 7, 14, 28 and 56 days** at **30 °C** in sterilized natural Xiamen Bay seawater **mixed with 0.5 M H₂O₂ and continuously oxygenated**—critically, **not unmodified natural seawater**. Electrochemical polarization used an air-equilibrated three-electrode bulk cell at **20 ± 1 °C**, **−0.4 to 0 V versus SCE**, **0.01 mV/s**. Reported *E*₍corr₎ for the five times was **−0.249, −0.241, −0.234, −0.224, −0.198 V versus SCE**, and fitted *i*₍corr₎ **3.812, 1.310, 1.284, 1.129, 1.056 µA/cm²**. Authors’ **Tafel-derived**, not independently measured, *R*ₚ values were **4.786, 13.488, 14.165, 17.359, 19.916 kΩ·cm²**; do **not** use these fitted values to validate LPR or dissolution rates. XPS/Raman identified CuO/Cu₂O/Cu(OH)₂ and, with aging, CuCl/CuCl₂ and some **Cu₂(OH)₃Cl**; O 1s components included jointly assigned **CuO/NiO** and **Cu(OH)₂/Ni(OH)₂**, illustrating phase overlap. Surface-film EDS Cl increased **2.02 to 8.45 at%** from 7 to 56 days; visible intergranular attack/pits and exfoliation were described, **without verified numerical attack depths**. No cathodic film charge, element-resolved solution flux, or breakdown/protection potential was reported. **Robot implication:** keep H₂O₂-accelerated and genuinely unmodified seawater cohorts separate, and validate chloride-containing films spectroscopically. (jin2019surfacecharacterizationand pages 3-5, jin2019surfacecharacterizationand pages 8-11, jin2019surfacecharacterizationand pages 5-8)

7. **[CITE] [NUMBERS] [NAVY] [CUBXL]** Kun Luo *et al.*, “The Galvanic Corrosion Behavior of ZCuAl10Fe5Ni5 Coupled with SAF2507 Duplex Stainless Steel in Seawater,” *Metals* **16**, 473 (2026), **DOI: 10.3390/met16050473**. Material: **cast/engineering ZCuAl10Fe5Ni5 NAB** (**Al 10.45, Fe 5.44, Ni 4.69, Zn 0.49, Sn 0.015, Pb 0.048 wt%; Cu balance**) coupled to duplex steel; not laser DED. Exposed bronze area was **1 cm²** at 1:1 or **0.06 cm²** against **3 cm²** steel at **bronze:steel 1:50**. Bulk-cell volume was not given. Medium: **ASTM D1141 synthetic seawater** (including **24.53 g/L NaCl and 5.20 g/L MgCl₂**); measurements at corrosion-exposure intervals through approximately **360 h**, with **10-min** coupled-current/OCP observations and **10-mV, 100-kHz-to-0.1-Hz** EIS, **versus SCE**. The 1:50 galvanic current density was about **38 µA/cm² initially**, about **2 µA/cm² at 72 h**, and about **4 µA/cm² at 360 h**, compared with near-zero 1:1 current. These are **galvanic currents, not *i*₍corr₎ or cathodic oxide-reduction currents**. The authors describe layered Cu–Al–Mg oxides/hydroxides and selective Al loss; no oxide coulometry, element-resolved dissolution rates, numerical depth-of-attack series or validated Cu₂(OH)₃Cl reduction potential was given. **Robot implication:** record exact fractions of deposit, fusion zone, heat-affected zone and substrate within each well; a mixed-metal interface is itself a galvanic-coupling experiment. (luo2026thegalvaniccorrosion pages 9-11, luo2026thegalvaniccorrosion pages 14-15, luo2026thegalvaniccorrosion pages 3-4, luo2026thegalvaniccorrosion pages 4-6)

8. **[CITE] [NOVELTY-RISK] [GAP]** La-Mei Zhang, Xiao-Yu Cai, Bai-Long Song, Bo-Lun Dong, San-Wai Lin and Fuad Khoshnaw, “Effect of low-level Ti microalloying on the microstructure, mechanical properties, and corrosion behaviour of WAAM-processed nickel-aluminium bronze,” *Advanced Materials Joining* **1**, article 17 (2026), **DOI: 10.1007/s44500-026-00016-x**. **Cold-metal-transfer wire-arc AM**, *not* pre-alloyed blown-powder laser DED; Ti nanoparticles were separately coated between layers. The materials section lists **Al 8.73, Ni 4.28, Fe 3.22, Mn 1.44 wt%** and prints **“Mg: Bal.”**; because that is incompatible with a copper-base NAB designation, **the balance Cu cannot safely be inferred from that line**. Added Ti was **0.03, 0.05 or 0.10 wt%**. The bulk-area/volume were not reported in the consulted methods. Static immersion used **3.5 wt% NaCl for 7, 14 and 21 days**; separate polarization employed **SCE** and Pt mesh. The available passages do not establish numerical *E*₍corr₎, independently measured *R*ₚ, *i*₍corr₎, phase-resolved cathodic oxide charge, or seawater rankings. **Overlap:** additive-manufactured NAB corrosion already exists; **gap:** matched-spot Cu-oxide coulometry and element-resolved dissolution across *pre-alloyed laser-powder DED NAB repair interfaces* remain unestablished here. (zhang2026effectoflowlevel pages 2-4, zhang2026effectoflowlevel pages 8-11)

## Powders, inaccessible oxides, and limits of interpretation

**[GAP] Powder oxygen is not yet established by these reduction methods.** A cavity microelectrode can electrochemically interrogate *powder*: Julian Behnken *et al.*, “Oxygen Reduction Reaction Activity of Mesostructured Cobalt-Based Metal Oxides Studied with the Cavity-Microelectrode Technique,” *ChemElectroChem* **6**, 3460–3467 (2019), **DOI: 10.1002/celc.201900722**, filled an etched **50-µm-diameter Au cavity** with **nanocast Co₃O₄/NiCo₂O₄/CuCo₂O₄ catalyst powders**. Their test concerned oxygen-reduction catalysis, **not reducing the native oxide on metallic Cu-alloy powder**. Accessible powder area depended on filling and electrolyte access; capacitance-derived areas included **0.017 cm²** for one cavity and approximately **0.012–0.034 cm²** across tested oxides. No validated Cu–Ni/NAB metallic-powder oxide thickness, feedstock oxygen mass fraction, comparison with inert-gas-fusion oxygen, or powder-oxide detection limit follows from this paper. Powder mass, accessible area, particle contacts and unreduced Al-rich oxide would all need independent calibration. A packed-powder or cavity measurement should therefore be labeled a **proposed assay**, with inert-gas-fusion oxygen on matched feedstock/splats/skull and XPS/TEM used as complementary controls—not a replacement oxygen assay. (behnken2019oxygenreductionreaction pages 2-3, ramirez2011oxidationkineticsof pages 1-2, ramirez2011oxidationkineticsof pages 6-7)

**[CUBXL] [GAP] Ni, Fe, Al and Mn are not one common ‘invisible oxide’ class.** NiO/Ni(OH)₂ have calculated reduction equilibria more negative than Cu oxides; the SERA review notes nickel oxides can be electrochemically reduced but may be **recalcitrant**. Fe oxides can be detected on iron, sometimes only **semiquantitatively because of Fe²⁺ dissolution**. Hydrogen evolution and mixed-product kinetics confound either assignment on an alloy. **Al₂O₃ cannot be reduced to Al in an aqueous SERA cell.** No validated Mn-oxide potential/quantitative contribution specific to these NAB/Mn-bronze films, nor phase-specific **Cu₂(OH)₃Cl** plateau and charge calibration for Cu–Ni/NAB seawater films, was established by the retrieved studies. Accordingly, a small copper-reduction charge can coexist with substantial Ni/Fe/Al/Mn-rich material; XPS/Raman plus cross-sectional analysis must audit the non-coulometric remainder. (tench1994solderabilityassessmentvia pages 1-2, tench1994solderabilityassessmentvia pages 9-11, tench1994solderabilityassessmentvia pages 11-12, jin2019surfacecharacterizationand pages 5-8, hutchison2018solutecaptureand pages 8-9)

## Ranked Top 5 changes to the small-cell plan for copper alloys

1. **Add a dedicated, deoxygenated reduction assay on a fresh neighboring spot.** Preserve the original air-open seawater well for corrosion; after defined exposure, rinse/transfer a matched spot into freshly nitrogen-purged **pH 8.4 borate**, isolate Pt from the sample solution where practical, and run a controlled **~20–30 µA/cm²** cathodic-current pilot with a stable stated reference. Do not do reduction *before* OCP/LPR/cyclic polarization or use corrosion-well solution as reduction electrolyte. Check potentiostat galvanostatic capability, low-µA resolution, compliance voltage and charge integration experimentally. (tench1994solderabilityassessmentvia pages 1-2, tench1994solderabilityassessmentvia pages 5-6, tench1994solderabilityassessmentvia pages 9-11, hutchison2018solutecaptureand pages 2-3)
2. **Calibrate charge and detection in the *actual 0.07–0.13-cm² wells*.** Run oxide-free blanks, flat-Cu/Cu₂O standards, independent current-density sweeps, repeat spots, O-ring leak/crevice controls, and XPS/Raman cross-checks. Report geometric-area-normalized charge and empirically measured limit of detection; **<2 nm CuO was missed** even on smooth Cu by one SERA implementation. (ramirez2011oxidationkineticsof pages 2-3, tench1994solderabilityassessmentvia pages 9-11, ramirez2011oxidationkineticsof pages 1-2, ramirez2011oxidationkineticsof pages 6-7)
3. **Make exposure history and water chemistry explicit.** Keep genuine natural, ASTM D1141 and simple NaCl as distinct cohorts, with fresh versus aged films, oxygen/flow/pH/temperature and handling recorded. Do not import an H₂O₂-accelerated 56-day Cu–Ni benchmark as if it represented untreated seawater. (jin2019surfacecharacterizationand pages 3-5, jin2019surfacecharacterizationand pages 8-11)
4. **Spatially separate repair microstructures and quantify what reduction misses.** Register photographs and metallography to rings entirely inside deposit, fusion zone, heat-affected zone or substrate where possible; include deliberately interface-spanning controls. Analyze film chemistry/cross-sections and used electrolyte **for Cu, Ni, Fe, Al and Mn**, while retaining direct LPR slopes rather than turning an oxygen-limited Tafel fit into *i*₍corr₎. The 1:50 NAB/steel experiment illustrates how strongly electrode area ratio can matter. (tench1994solderabilityassessmentvia pages 9-11, jin2019surfacecharacterizationand pages 8-11, luo2026thegalvaniccorrosion pages 3-4, luo2026thegalvaniccorrosion pages 4-6)
5. **Treat feedstock and atomization byproducts as a separately validated metrology project.** First establish powder mass/size-specific area and electrical contact in a cavity or packed electrode; measure matched aliquots by **inert-gas-fusion oxygen**, XPS and microscopy, and determine how much Ni/Fe/Al/Mn oxide remains after Cu-product reduction. Do not convert an uncalibrated powder-electrode charge into either whole-particle oxide thickness or total oxygen wt%. (behnken2019oxygenreductionreaction pages 2-3, tench1994solderabilityassessmentvia pages 9-11, ramirez2011oxidationkineticsof pages 1-2)

References

1. (tench1994solderabilityassessmentvia pages 1-2): D. Morgan Tench, D.P. Anderson, and P. Kim. Solderability assessment via sequential electrochemical reduction analysis. Journal of Applied Electrochemistry, 24:18-29, Jan 1994. URL: https://doi.org/10.1007/bf00243325, doi:10.1007/bf00243325. This article has 66 citations and is from a peer-reviewed journal.

2. (tench1994solderabilityassessmentvia pages 5-6): D. Morgan Tench, D.P. Anderson, and P. Kim. Solderability assessment via sequential electrochemical reduction analysis. Journal of Applied Electrochemistry, 24:18-29, Jan 1994. URL: https://doi.org/10.1007/bf00243325, doi:10.1007/bf00243325. This article has 66 citations and is from a peer-reviewed journal.

3. (tench1994solderabilityassessmentvia pages 9-11): D. Morgan Tench, D.P. Anderson, and P. Kim. Solderability assessment via sequential electrochemical reduction analysis. Journal of Applied Electrochemistry, 24:18-29, Jan 1994. URL: https://doi.org/10.1007/bf00243325, doi:10.1007/bf00243325. This article has 66 citations and is from a peer-reviewed journal.

4. (hutchison2018solutecaptureand pages 2-3): M. J. Hutchison and J. R. Scully. Solute capture and doping of al in cu2o: corrosion, tarnish resistance, and cation release of high-purity cu-al alloys in artificial perspiration. Journal of The Electrochemical Society, 165:C689-C702, Jan 2018. URL: https://doi.org/10.1149/2.1301810jes, doi:10.1149/2.1301810jes. This article has 18 citations and is from a peer-reviewed journal.

5. (tench1994solderabilityassessmentvia pages 3-5): D. Morgan Tench, D.P. Anderson, and P. Kim. Solderability assessment via sequential electrochemical reduction analysis. Journal of Applied Electrochemistry, 24:18-29, Jan 1994. URL: https://doi.org/10.1007/bf00243325, doi:10.1007/bf00243325. This article has 66 citations and is from a peer-reviewed journal.

6. (ramirez2011oxidationkineticsof pages 2-3): Mauricio Ramirez, Lothar Henneken, and Sannakaisa Virtanen. Oxidation kinetics of thin copper films and wetting behaviour of copper and organic solderability preservatives (osp) with lead-free solder. Applied Surface Science, 257:6481-6488, May 2011. URL: https://doi.org/10.1016/j.apsusc.2011.02.048, doi:10.1016/j.apsusc.2011.02.048. This article has 64 citations and is from a domain leading peer-reviewed journal.

7. (ramirez2011oxidationkineticsof pages 3-5): Mauricio Ramirez, Lothar Henneken, and Sannakaisa Virtanen. Oxidation kinetics of thin copper films and wetting behaviour of copper and organic solderability preservatives (osp) with lead-free solder. Applied Surface Science, 257:6481-6488, May 2011. URL: https://doi.org/10.1016/j.apsusc.2011.02.048, doi:10.1016/j.apsusc.2011.02.048. This article has 64 citations and is from a domain leading peer-reviewed journal.

8. (ramirez2011oxidationkineticsof pages 1-2): Mauricio Ramirez, Lothar Henneken, and Sannakaisa Virtanen. Oxidation kinetics of thin copper films and wetting behaviour of copper and organic solderability preservatives (osp) with lead-free solder. Applied Surface Science, 257:6481-6488, May 2011. URL: https://doi.org/10.1016/j.apsusc.2011.02.048, doi:10.1016/j.apsusc.2011.02.048. This article has 64 citations and is from a domain leading peer-reviewed journal.

9. (ramirez2011oxidationkineticsof pages 6-7): Mauricio Ramirez, Lothar Henneken, and Sannakaisa Virtanen. Oxidation kinetics of thin copper films and wetting behaviour of copper and organic solderability preservatives (osp) with lead-free solder. Applied Surface Science, 257:6481-6488, May 2011. URL: https://doi.org/10.1016/j.apsusc.2011.02.048, doi:10.1016/j.apsusc.2011.02.048. This article has 64 citations and is from a domain leading peer-reviewed journal.

10. (hutchison2018solutecaptureand pages 1-1): M. J. Hutchison and J. R. Scully. Solute capture and doping of al in cu2o: corrosion, tarnish resistance, and cation release of high-purity cu-al alloys in artificial perspiration. Journal of The Electrochemical Society, 165:C689-C702, Jan 2018. URL: https://doi.org/10.1149/2.1301810jes, doi:10.1149/2.1301810jes. This article has 18 citations and is from a peer-reviewed journal.

11. (hutchison2018solutecaptureand pages 8-9): M. J. Hutchison and J. R. Scully. Solute capture and doping of al in cu2o: corrosion, tarnish resistance, and cation release of high-purity cu-al alloys in artificial perspiration. Journal of The Electrochemical Society, 165:C689-C702, Jan 2018. URL: https://doi.org/10.1149/2.1301810jes, doi:10.1149/2.1301810jes. This article has 18 citations and is from a peer-reviewed journal.

12. (bertocci2004aneqmbexamination pages 2-5): U. Bertocci. An eqmb examination of cu surface oxides in borate buffer. Electrochimica Acta, 49:1831-1841, Apr 2004. URL: https://doi.org/10.1016/j.electacta.2003.11.033, doi:10.1016/j.electacta.2003.11.033. This article has 31 citations and is from a domain leading peer-reviewed journal.

13. (bertocci2004aneqmbexamination pages 7-8): U. Bertocci. An eqmb examination of cu surface oxides in borate buffer. Electrochimica Acta, 49:1831-1841, Apr 2004. URL: https://doi.org/10.1016/j.electacta.2003.11.033, doi:10.1016/j.electacta.2003.11.033. This article has 31 citations and is from a domain leading peer-reviewed journal.

14. (seo1988photoacousticstudyon pages 2-3): Masahiro Seo, Xiang Chun Jiang, and Norio Sato. Photoacoustic study on cathodic reduction of anodic oxide films formed on copper in borate solution. Materials and Corrosion-werkstoffe Und Korrosion, 39:583-588, Dec 1988. URL: https://doi.org/10.1002/maco.19880391205, doi:10.1002/maco.19880391205. This article has 22 citations and is from a peer-reviewed journal.

15. (seo1988photoacousticstudyon pages 3-5): Masahiro Seo, Xiang Chun Jiang, and Norio Sato. Photoacoustic study on cathodic reduction of anodic oxide films formed on copper in borate solution. Materials and Corrosion-werkstoffe Und Korrosion, 39:583-588, Dec 1988. URL: https://doi.org/10.1002/maco.19880391205, doi:10.1002/maco.19880391205. This article has 22 citations and is from a peer-reviewed journal.

16. (tench1994solderabilityassessmentvia pages 11-12): D. Morgan Tench, D.P. Anderson, and P. Kim. Solderability assessment via sequential electrochemical reduction analysis. Journal of Applied Electrochemistry, 24:18-29, Jan 1994. URL: https://doi.org/10.1007/bf00243325, doi:10.1007/bf00243325. This article has 66 citations and is from a peer-reviewed journal.

17. (jin2019surfacecharacterizationand pages 3-5): Tingzhu Jin, Weifang Zhang, Ning Li, Xuerong Liu, Lu Han, and Wei Dai. Surface characterization and corrosion behavior of 90/10 copper-nickel alloy in marine environment. Materials, 12:1869, Jun 2019. URL: https://doi.org/10.3390/ma12111869, doi:10.3390/ma12111869. This article has 148 citations.

18. (jin2019surfacecharacterizationand pages 8-11): Tingzhu Jin, Weifang Zhang, Ning Li, Xuerong Liu, Lu Han, and Wei Dai. Surface characterization and corrosion behavior of 90/10 copper-nickel alloy in marine environment. Materials, 12:1869, Jun 2019. URL: https://doi.org/10.3390/ma12111869, doi:10.3390/ma12111869. This article has 148 citations.

19. (jin2019surfacecharacterizationand pages 5-8): Tingzhu Jin, Weifang Zhang, Ning Li, Xuerong Liu, Lu Han, and Wei Dai. Surface characterization and corrosion behavior of 90/10 copper-nickel alloy in marine environment. Materials, 12:1869, Jun 2019. URL: https://doi.org/10.3390/ma12111869, doi:10.3390/ma12111869. This article has 148 citations.

20. (luo2026thegalvaniccorrosion pages 9-11): Kun Luo, Pu Zhao, Ke-Wei Fang, Wan-Xiang Zhao, Jiachang Lu, Hong-Qun Liu, Shui-Yong Wang, Mengmeng Zhu, and Y.-X. Qiao. The galvanic corrosion behavior of zcual10fe5ni5 coupled with saf2507 duplex stainless steel in seawater. Metals, 16:473, Apr 2026. URL: https://doi.org/10.3390/met16050473, doi:10.3390/met16050473. This article has 0 citations.

21. (luo2026thegalvaniccorrosion pages 14-15): Kun Luo, Pu Zhao, Ke-Wei Fang, Wan-Xiang Zhao, Jiachang Lu, Hong-Qun Liu, Shui-Yong Wang, Mengmeng Zhu, and Y.-X. Qiao. The galvanic corrosion behavior of zcual10fe5ni5 coupled with saf2507 duplex stainless steel in seawater. Metals, 16:473, Apr 2026. URL: https://doi.org/10.3390/met16050473, doi:10.3390/met16050473. This article has 0 citations.

22. (luo2026thegalvaniccorrosion pages 3-4): Kun Luo, Pu Zhao, Ke-Wei Fang, Wan-Xiang Zhao, Jiachang Lu, Hong-Qun Liu, Shui-Yong Wang, Mengmeng Zhu, and Y.-X. Qiao. The galvanic corrosion behavior of zcual10fe5ni5 coupled with saf2507 duplex stainless steel in seawater. Metals, 16:473, Apr 2026. URL: https://doi.org/10.3390/met16050473, doi:10.3390/met16050473. This article has 0 citations.

23. (luo2026thegalvaniccorrosion pages 4-6): Kun Luo, Pu Zhao, Ke-Wei Fang, Wan-Xiang Zhao, Jiachang Lu, Hong-Qun Liu, Shui-Yong Wang, Mengmeng Zhu, and Y.-X. Qiao. The galvanic corrosion behavior of zcual10fe5ni5 coupled with saf2507 duplex stainless steel in seawater. Metals, 16:473, Apr 2026. URL: https://doi.org/10.3390/met16050473, doi:10.3390/met16050473. This article has 0 citations.

24. (zhang2026effectoflowlevel pages 2-4): La-Mei Zhang, Xiao-Yu Cai, Bai-Long Song, Bo-Lun Dong, San-Wai Lin, and Fuad Khoshnaw. Effect of low-level ti microalloying on the microstructure, mechanical properties, and corrosion behaviour of waam-processed nickel-aluminium bronze. Advanced Materials Joining, Oct 2026. URL: https://doi.org/10.1007/s44500-026-00016-x, doi:10.1007/s44500-026-00016-x. This article has 0 citations.

25. (zhang2026effectoflowlevel pages 8-11): La-Mei Zhang, Xiao-Yu Cai, Bai-Long Song, Bo-Lun Dong, San-Wai Lin, and Fuad Khoshnaw. Effect of low-level ti microalloying on the microstructure, mechanical properties, and corrosion behaviour of waam-processed nickel-aluminium bronze. Advanced Materials Joining, Oct 2026. URL: https://doi.org/10.1007/s44500-026-00016-x, doi:10.1007/s44500-026-00016-x. This article has 0 citations.

26. (behnken2019oxygenreductionreaction pages 2-3): Julian Behnken, Mingquan Yu, Xiaohui Deng, Harun Tüysüz, Corinna Harms, Alexander Dyck, and Gunther Wittstock. Oxygen reduction reaction activity of mesostructured cobalt‐based metal oxides studied with the cavity‐microelectrode technique. ChemElectroChem, 6:3460-3467, Jul 2019. URL: https://doi.org/10.1002/celc.201900722, doi:10.1002/celc.201900722. This article has 17 citations and is from a peer-reviewed journal.
