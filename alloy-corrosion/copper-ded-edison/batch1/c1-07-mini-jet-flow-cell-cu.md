<!--
Edison Scientific LITERATURE task (batch 1)
- Task ID: 2e6fd2b4-00d1-4d16-ba36-0c879952bc24
- Submitted: 2026-10-18T01:20:06Z
- Fetched: 2026-10-18T01:50:07Z (status: success)
- Raw trajectory JSON: ../raw/c1-07-mini-jet-flow-cell-cu.json.gz
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

QUESTION: Can erosion-corrosion of Cu-Ni and NAB be screened on millimetre
spots with a small pumped flow: a submerged micro-jet, wall-jet,
channel-flow or impinging-jet cell fed by a syringe or peristaltic pump?
Report small-scale flow cells used on copper alloys (nozzle diameter,
standoff, flow rate, wall shear stress, duration); the wall shear stresses or
velocities at which Cu-Ni and NAB films break down, and how they relate to
the critical pipe velocities of about 3-4 m/s for 90-10 and higher for 70-30;
how electrochemical signals (current transients, Rp, OCP) were recorded
during flow; and whether such tests ranked alloys the same way as pipe-loop,
jet-impingement rig or rotating-cylinder tests. Include welded or
additively manufactured copper alloys if any exist. If the literature allows,
estimate the flow rate needed to reach those shear stresses in a 3-4 mm cell.

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

QUESTION: Can erosion-corrosion of Cu-Ni and NAB be screened on millimetre
spots with a small pumped flow: a submerged micro-jet, wall-jet,
channel-flow or impinging-jet cell fed by a syringe or peristaltic pump?
Report small-scale flow cells used on copper alloys (nozzle diameter,
standoff, flow rate, wall shear stress, duration); the wall shear stresses or
velocities at which Cu-Ni and NAB films break down, and how they relate to
the critical pipe velocities of about 3-4 m/s for 90-10 and higher for 70-30;
how electrochemical signals (current transients, Rp, OCP) were recorded
during flow; and whether such tests ranked alloys the same way as pipe-loop,
jet-impingement rig or rotating-cylinder tests. Include welded or
additively manufactured copper alloys if any exist. If the literature allows,
estimate the flow rate needed to reach those shear stresses in a 3-4 mm cell.

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


# Can a millimetre-scale pumped cell screen Cu–Ni and NAB erosion–corrosion?

**Yes, as a comparative, locally calibrated flow challenge—not as a direct measurement of a pipe’s critical velocity.** A published copper–nickel experiment used a 1-mm submerged impinging jet and measured electrochemical changes within 1–3 h. Its electrode was 10 mm across, however, not a 3–4 mm O-ring spot. The most relevant pipe-loop measurements ran for **10 days**, and their alloy ranking differed from the short-jet ranking. A pumped spot can therefore measure *fresh-surface response to flow* and, with separately aged specimens, *film durability*; it cannot presently be claimed to predict service ranking or the critical velocity of a repaired pipe or propeller. (metikoshukovic2011corrosionresistanceof pages 1-2, metikoshukovic2011corrosionresistanceof pages 3-5, wu2023erosion–corrosionbehaviorof pages 1-2, wu2023erosion–corrosionbehaviorof pages 19-21)

**Reporting convention.** “Not reported” below means the cited work does not supply the requested value, rather than that its value is zero. Potentials and corrosion-current estimates are compared only where their reference electrode and estimation method are stated. A jet-exit velocity, mean pipe velocity, and *local* wall shear stress are different quantities. (metikoshukovic2011corrosionresistanceof pages 2-3, metikoshukovic2011corrosionresistanceof pages 3-5, wu2023erosion–corrosionbehaviorof pages 2-4)

## Direct flow evidence and quantitative comparators

1. **[CITE] [NUMBERS] [CUBXL] [NOVELTY-RISK]** Metikoš-Huković, M.; Babić, R.; Škugor Rončević, I.; Grubač, Z. “Corrosion resistance of copper–nickel alloy under fluid jet impingement.” *Desalination* **276** (2011), 228–232. **DOI: 10.1016/j.desal.2011.03.056.** Laboratory-prepared, rolled and annealed binary Cu–Ni containing **10, 20, 30 or 40 atomic % Ni**, **not commercial C70600/C71500**: Fe, Mn and Cr additions were not reported. The metal was a polished, Teflon-mounted **10-mm disc, 0.78 cm²** in a recirculating three-electrode cell, not a droplet or O-ring cell; **electrolyte volume and nozzle standoff were not reported**. A **1-mm-diameter, normally incident nozzle** supplied 3.5% NaCl, pH 7.9, at **2.7, 6.4 or 8.3 m/s**, corresponding by calculation to approximately **0.127, 0.302 or 0.391 L/min** through that nozzle. Measurements followed **1–3 h** immersion; the tabulated bare-alloy results are at **3 h**. Ag/AgCl/3 M KCl (**+209 mV versus SHE**) and carbon-rod counters were used. Polarization scans were **1 mV/s**; impedance at OCP used **±10 mV, 30 mHz–100 kHz**. At jet velocity **2.7 m/s**, the authors **calculated**, rather than measured, **35 Pa** local shear at radial position *r/r₀* = 3; at **6.4 m/s**, **268 Pa**. These are **not demonstrated film-breakdown thresholds**. Bare-alloy impedance-derived **Rₚ in kΩ·cm²**, ordered 10/20/30/40 at.% Ni, was **6.0/8.0/8.3/8.0** without flow, **1.3/0.9/0.7/0.5** at 2.7 m/s, and **0.7/0.5/0.4/0.5** at 6.4 m/s; at 8.3 m/s, only **0.6/0.4** was reported for the first two compositions. Thus the short, bare-jet ranking favored **Cu–10Ni**, whereas stagnant measurements favored approximately Cu–30Ni. Optional diethyldithiocarbamate pretreatment is **not a seawater-film analogue**. Numerical *E*₍corr₎, *i*₍corr₎, depth and element-resolved dissolution were not tabulated for this comparison. **CubXL consequence:** adapt the nozzle concept and OCP/EIS sequence, but do not transfer its 10-mm spatial average or binary-alloy ranking directly to an Fe-bearing 3-mm deposit. The overlap is the already-published use of a small nozzle and in-situ electrochemistry on Cu–Ni, **not** automated micro-area testing of DED repairs. (metikoshukovic2011corrosionresistanceof pages 1-2, metikoshukovic2011corrosionresistanceof pages 2-3, metikoshukovic2011corrosionresistanceof pages 3-5, metikoshukovic2011corrosionresistanceof pages 5-5)

2. **[CITE] [NUMBERS] [NAVY] [CUBXL]** Wu, L.; Ma, A.; Zhang, L.; Li, G.; Hu, L.; Wang, Z.; Zheng, Y. “Erosion–Corrosion Behavior of 90/10 and 70/30 Copper–Nickel Tubes in 1 wt% NaCl Solution.” *Metals* **13** (2023), 401. **DOI: 10.3390/met13020401.** Annealed, commercial-type **90/10 tube:** Ni **10.72**, Fe **1.68**, Mn **0.76 wt%**, Cu balance; **70/30 tube:** Ni **30.4**, Fe **0.75**, Mn **0.88 wt%**, Cu balance. Cr was not listed. This was a **25-mm-outer-diameter, 2-mm-wall recirculating pipe loop**, with separately mounted **1.0-cm²** electrochemical pieces—not a jet, droplet, capillary or O-ring cell; **loop inventory was not reported in the examined text**. In **1 wt% NaCl** for **10 days**, mean tube velocities were **0.5, 1.5, 3, 4 and 4.7 m/s**. Investigators monitored **OCP for 30 min** and acquired EIS (**±10 mV, 100 kHz–10 mHz**) during exposure, then ran a **0.3333-mV/s** broad polarization scan on the final day. Their film-continuity criterion places the 90/10 breakaway **between 3 and 4 m/s**: partially bare at 4 and essentially unfilmed at 4.7 m/s. The 70/30 film remained continuous, albeit markedly cracked at 4–4.7 m/s: its corresponding threshold was **above 4.7 m/s**. At **1.5 m/s**, aged 90/10 had *E*₍corr₎ **−438.9 mV vs SCE**, fitted *i*₍corr₎ **2.39 µA/cm²**; at **4.7 m/s**, **−280.3 mV vs SCE** and **13.44 µA/cm²**. Aged 70/30 at **0.5 m/s** had fitted *i*₍corr₎ **1.60 µA/cm²** and at **4.7 m/s** **8.49 µA/cm²**; at the latter velocity its tabulated *E*₍corr₎ was **−251.5 mV vs SCE**. These fitted currents used **different extraction methods for freshly polished 90/10, aged 90/10 and 70/30**; they are not a uniform set of Tafel-derived dissolution rates. No quantified wall shear, nozzle or standoff applies. **CubXL consequence:** retain polished and aged-film cohorts, repeat non-destructive EIS during the flow hold, and corroborate electrical changes with post-flow film images. The paper lists an author at a ship-design institute, but its declared grant support is Chinese civilian research funding: **[NAVY] denotes the vessel application, not demonstrated US Navy/DoD funding**. (wu2023erosion–corrosionbehaviorof pages 1-2, wu2023erosion–corrosionbehaviorof pages 2-4, wu2023erosion–corrosionbehaviorof pages 4-7, wu2023erosion–corrosionbehaviorof pages 11-13, wu2023erosion–corrosionbehaviorof pages 10-11, wu2023erosion–corrosionbehaviorof pages 19-21, wu2023erosion–corrosionbehaviorof media b78de47e)

3. **[CITE] [NUMBERS] [NAVY] [CUBXL]** Jafari, H. R.; Davoodi, A.; Hosseinpour, S. “Effect of Fluid Flow on the Corrosion Performance of as-Cast and Heat-Treated Nickel Aluminum Bronze Alloy (UNS C95800) in Saline Solution.” *Corrosion and Materials Degradation* **2** (2021), 61–77. **DOI: 10.3390/cmd2010004.** **Cast C95800**, Cu balance; **Al 8.79, Ni 4.50, Fe 3.70, Mn 1.00, Cr 0.007 wt%**; compared as-cast with annealed **675 °C/6 h**. **Five-mm-diameter rotating-disc electrodes** were immersed in **250 mL** of **3.5 wt% NaCl** at **25 or 40 °C**; rotation **0–9000 rpm**. This was neither an impinging jet nor a 3–4 mm flow well: nozzle diameter, standoff and volumetric pump flow are **inapplicable**. OCP was recorded for approximately **1000 s**, followed by EIS (**±10 mV, 0.01–100,000 Hz**) and a **1-mV/s** polarization scan from **−200 to +500 mV relative to OCP**; reference **saturated Ag/AgCl**. At 25 °C, as-cast *E*₍corr₎ changed from **−262 mV** static to **−278 mV vs saturated Ag/AgCl** at 9000 rpm, with reported polarization-fit *i*₍corr₎ **1.74→5.57 µA/cm²**; annealed material **−255→−284 mV**, **0.918→5.22 µA/cm²**. The **authors calculated a rotation-dependent shear curve**, but did **not establish a NAB film-breakdown wall stress**; they considered electrochemical effects dominant to 9000 rpm. Their Tafel-based current and Stern–Geary-style values should be treated as **authors’ fit outputs**, not independent element-resolved loss or validated kinetic constants. **CubXL consequence:** test cast and heat-treated controls, log OCP during flow transitions, and do not label any selected shear a NAB critical stress without a film-loss endpoint. The cited marine-valve/propeller application earns [NAVY], not a verified DoD-funding claim. (jafari2021effectoffluid pages 1-2, jafari2021effectoffluid pages 2-4, jafari2021effectoffluid pages 4-7, jafari2021effectoffluid pages 8-11, jafari2021effectoffluid pages 7-8)

4. **[CITE] [NAVY] [CUBXL] [GAP]** Lewis, R. O.; LaQue, F. “Evaluation of copper-nickel alloys for OTEC applications.” Technical report (1981). **DOI: 10.2172/6255887.** This is a **synthesis of commercial wrought/formed C70600, C71500 and Cr-modified Cu–Ni**, rather than a newly demonstrated millimetre flow cell; it supplies **no single cell area, volume, electrolyte inventory, jet standoff, potentiostat protocol or common exposure duration**. It reports that impinging-jet methods can *often* rank impingement resistance usefully, but explicitly describes discrepancies between once-through and recirculated seawater, rigs and laboratories. In particular, **Fe and Cr content matter**: Fe-bearing 90/10 can match 70/30 in some jet comparisons, while Cr-modified Cu–Ni resists high-speed impingement despite potential quiet-water localized-attack trade-offs. Its discussion cautions that a jet’s filmed/unfilmed area gradient can introduce galvanic effects absent from uniform pipe flow. **CubXL consequence:** match composition and water history before comparing ranks, isolate the exposed spot from surrounding conductive metal, and use a pipe-loop reference set for validation. This is marine/ship/heat-exchanger relevance, **not verified Navy/DoD sponsorship**. (lewis1981evaluationofcoppernickel pages 17-19, lewis1981evaluationofcoppernickel pages 14-17, lewis1981evaluationofcoppernickel pages 19-21)

5. **[CITE] [NUMBERS] [NOVELTY-RISK] [GAP]** Zhao, L.; Li, K.; Yao, J.; Yuan, Y.; Du, B. “The Laser Deposited Nickel-Aluminum Bronze Coatings on SUS630 Stainless Steel and Its Corrosion Resistance in 3.5 wt.% NaCl Solution.” *Metals* **12** (2022), 781. **DOI: 10.3390/met12050781.** Pre-alloyed NAB powder **Cu 81.1, Al 10.8, Ni 4.1, Fe 4.0 wt%** was **laser deposited** directly on steel (N-1) or over separately deposited NiAl- or NiCr-bearing interlayers (N-2/N-3), using a **2400-W** laser for NAB: **not** a demonstration of 300–500-W, single-stream DED repair on NAB or Cu–Ni. Dilution altered the deposited upper-layer compositions: reported area analyses for N-1/N-2/N-3 were respectively **Cu/Al/Ni/Fe/Cr = 75.2/9.8/3.8/11.2/0; 73.2/10.4/12.4/4.0/0; 72.3/10.9/10.8/4.1/1.9 wt%**. Polished **1.00-cm²** embedded electrodes were measured in a **bulk three-electrode glass cell** with **3.5 wt% NaCl**, Pt counter, **Ag/AgCl/saturated KCl** reference; **electrolyte volume was not stated**. After **20 min** initial immersion, polarization and EIS were acquired; separate static immersion extended to **21 days**. Authors’ polarization-fit (*E*₍corr₎ **mV vs saturated Ag/AgCl**, *i*₍corr₎ **µA/cm²**) was **N-1 −248, 7.82; N-2 −255, 4.65; N-3 −252, 4.09**. Their **calculated, not directly measured, Stern–Geary Rₚ** values were **2810, 5275 and 4865 Ω·cm²**: notably N-2 has the higher fitted Rₚ while N-3 has the lower fitted current. After immersion, reported maximum attack depths were respectively **3.4 ± 0.1, 2.0 ± 0.1 and 1.8 ± 0.1 µm**. **Overlap:** laser-deposited NAB plus static chloride electrochemistry and depth measurement already exist. **Gap:** no pumped millimetre spot, cast-NAB repair-interface map or shear-dependent ranking was shown. (zhao2022thelaserdeposited pages 1-2, zhao2022thelaserdeposited pages 2-4, zhao2022thelaserdeposited pages 4-7, zhao2022thelaserdeposited pages 7-10, zhao2022thelaserdeposited pages 10-13)

**Additional directly relevant but unquantified citation:** Barik, R. C.; Wharton, J. A.; Wood, R. J. K.; Stokes, K. R. “Further studies into the flow corrosion cathodic mass transfer kinetics of copper and nickel-aluminium bronze wall-jet electrodes.” *Corrosion Science* **170** (2020), 108660. **DOI: 10.1016/j.corsci.2020.108660.** Its title establishes a **Cu/NAB wall-jet electrode precedent**, but the primary full text was not available in this retrieval. Accordingly, its **NAB composition and processing, nozzle, standoff, rate, stress, area, cell inventory, electrolyte, duration and electrochemical numbers cannot responsibly be supplied here**. It demonstrates neither, on evidence checked here, a NAB critical shear nor a pipe-loop ranking. **[CITE] [NOVELTY-RISK] [GAP]** Check this paper before claiming wall-jet testing of NAB is novel; the proposed distinguishing experiment is spatially registered flow testing of *DED repair zones*. No retrieved primary work establishes corresponding numeric flow thresholds for welded, WAAM, LPBF or blown-powder-DED Cu–Ni/NAB, nor for atomization splats or skull. (wu2023erosion–corrosionbehaviorof pages 2-4, zhao2022thelaserdeposited pages 1-2)

## What “breakdown” means—and what the pump would have to deliver

The often-cited **43.1 Pa for 90/10** is an **estimated critical pipe-wall shear** attributed to Efird for a particular seawater/film condition, **not a measured universal detachment strength**. A secondary engineering account pairs it with an estimated **4.4 m/s** for a roughly **30-mm-diameter tube at 27 °C**; pipe diameter, temperature, film maturation, salt chemistry and sand change the correspondence. No similarly defensible **NAB critical wall-shear value** was established in the inspected primary studies. The jet study’s **35 and 268 Pa** instead describe calculated local forcing at specified nozzle speeds; observing lower Rₚ at either value does **not** prove physical film removal. The 10-day tube work distinguishes loss of 90/10’s *outer* deposit near 3 m/s, partially exposed metal at 4 m/s, and nearly complete loss at 4.7 m/s, while 70/30 retains an inner protective layer. Thus **3–4 m/s for 90/10 and >4.7 m/s for 70/30 are loop-specific, film-continuity criteria**, not jet-exit settings. (schleich2004typicalfailuresof pages 7-9, metikoshukovic2011corrosionresistanceof pages 3-5, wu2023erosion–corrosionbehaviorof pages 1-2, wu2023erosion–corrosionbehaviorof pages 16-18, wu2023erosion–corrosionbehaviorof pages 18-19, wu2023erosion–corrosionbehaviorof pages 19-21)

For a **1.00-mm-ID nozzle**, the explicitly geometric estimate is *Q* = π*d*²*v*/4: **0.127 L/min** at 2.7 m/s, **0.141 L/min** at 3.0 m/s and **0.302 L/min** at 6.4 m/s. Extrapolating the published unconfined-jet shear relation very approximately puts **43 Pa near 3.0 m/s**, hence near **140 mL/min**, but **this is a design starting point, not a demonstrated 43-Pa measurement in an O-ring well**. The quoted local peak lies at *r/r₀* = 3, or **1.5 mm radius for a 1-mm nozzle**: it approaches the edge of a **3-mm-ID** opening and would be near the edge even in a **4-mm-ID** opening. A 150-µL well would exchange its nominal contents in only **~0.07 s at 127 mL/min**; a 10-min once-through run would consume **~1.27 L**. A small **pump** is plausible, but a pipetting head delivering discrete aliquots to an open 150-µL well is not a sustained high-shear apparatus. Use a **sealed, inlet-and-outlet flow lid** with a defined nozzle-to-surface gap and an independently measured outlet flow; establish local shear by CFD plus a flow/mass-transfer or velocimetry calibration. For a channel cell, hydraulic gap and width—not well diameter alone—set shear, so a channel flow rate **cannot be inferred uniquely** from the published jet results. These calculations inherit the jet paper’s geometry and are not performance specifications for NAB. (metikoshukovic2011corrosionresistanceof pages 1-2, metikoshukovic2011corrosionresistanceof pages 3-5)

**Ranking across rigs:** an instructive **failure of automatic agreement** is already evident: the short, binary-alloy jet gives **Cu–10Ni > Cu–20Ni > Cu–30Ni** by flowing Rₚ, whereas the separately conducted, Fe-bearing 10-day tube loop finds the **70/30 product film more resistant than 90/10** at tested velocities. Because both **composition and exposure history differ**, this is not a controlled head-to-head disproof of jet methods; it **is** a reason not to infer predictive agreement. The historical review says jet rigs may rank impingement resistance but warns of between-rig, water and recirculation differences. I found **no verified same-heat comparison of a 3–4-mm Cu–Ni/NAB pumped cell against pipe-loop, large jet and rotating-cylinder rankings**. A rotating *disc* study of cast NAB shows increased fitted dissolution with rotation; it does not supply that missing cross-rig comparison. Neither a potentiostatic film-stripping **current-transient threshold** nor time-resolved **element-specific effluent loss** was demonstrated for the above small copper-alloy jet. (metikoshukovic2011corrosionresistanceof pages 3-5, wu2023erosion–corrosionbehaviorof pages 4-7, wu2023erosion–corrosionbehaviorof pages 19-21, lewis1981evaluationofcoppernickel pages 17-19, lewis1981evaluationofcoppernickel pages 19-21, jafari2021effectoffluid pages 8-11)

## Top 5 changes to the small-cell plan for copper alloys

1. **Add a genuinely pumped, sealed flow head—not flow by pipetting into an open well.** Provide a submerged 1-mm inlet jet or defined-width channel, adjustable documented standoff/gap, outlet and pressure-safe gasket. Calibrate **local shear and exposed area**, including whether the O-ring obscures the jet’s high-shear annulus; do not quote nozzle speed as surface speed. Begin near **0.13–0.14 L/min**, then bracket the response rather than declaring a failure threshold. (metikoshukovic2011corrosionresistanceof pages 1-2, metikoshukovic2011corrosionresistanceof pages 3-5)
2. **Separate fresh and deliberately aged-film protocols.** Run identical wrought C70600/C71500 and cast C95800 controls alongside deposits, fusion boundary, HAZ and substrate. For service-film claims, extend exposure well beyond the initial **30-min OCP/one-hour polarization** schedule, use documented water chemistry and exposure history, and independently confirm actual film retention at the spot. (schleich2004typicalfailuresof pages 3-6, wu2023erosion–corrosionbehaviorof pages 2-4, wu2023erosion–corrosionbehaviorof pages 11-13, wu2023erosion–corrosionbehaviorof pages 19-21)
3. **Record OCP and non-destructive impedance before, during and after stepped flow.** Log pump onset/stop transients and current **only at a specified applied potential**, with reference position, uncompensated resistance and dissolved-oxygen control documented. Use short, limited-amplitude polarization or EIS-derived resistance as an operational signal; **do not equate an arbitrary assumed Stern–Geary constant or oxygen-limited cathodic-branch fit with true metal loss**. Reserve wide cyclic scans for separate spots because they change the film being tested. (metikoshukovic2011corrosionresistanceof pages 2-3, wu2023erosion–corrosionbehaviorof pages 2-4, jafari2021effectoffluid pages 8-11, wu2023erosion–corrosionbehaviorof pages 10-11)
4. **Redesign effluent analytics around volume and background.** A flow test produces **hundreds of millilitres per minute, not 150 µL per spot**: collect timed inlet/effluent fractions, record delivered volume, blank the tubing/pump and measure **Cu, Ni, Fe, Mn, Al and Cr individually** by ICP as applicable. Calculate an element-resolved mass balance, and image/section the exact impacted and annular regions to distinguish dissolved metal from loose film or particles. No reviewed small-jet paper supplies these proposed ICP values. (metikoshukovic2011corrosionresistanceof pages 1-2, metikoshukovic2011corrosionresistanceof pages 3-5, wu2023erosion–corrosionbehaviorof pages 2-4, zhao2022thelaserdeposited pages 7-10)
5. **Validate ranking before assigning a naval design meaning.** Blind-test replicated wrought C71500 and cast C95800 alongside the corresponding repairs in the *same* water, film state and preconditioning; compare the millimetre-cell rank with a longer flow loop or impingement rig and quantify scatter. Keep single tracks, thin walls, splats and skull separate from repair cross-sections, and report each zone’s **measured wt% composition and dilution**, not the powder label. This preserves the genuine novelty—**automated, spatially resolved, chemistry-linked flow tests of single-feed copper-alloy DED repairs**—without claiming novelty for copper-alloy jets, wall-jet NAB electrodes or static laser-deposit electrochemistry themselves. (metikoshukovic2011corrosionresistanceof pages 3-5, wu2023erosion–corrosionbehaviorof pages 2-4, wu2023erosion–corrosionbehaviorof pages 19-21, zhao2022thelaserdeposited pages 4-7, zhao2022thelaserdeposited pages 2-4, lewis1981evaluationofcoppernickel pages 19-21)

References

1. (metikoshukovic2011corrosionresistanceof pages 1-2): M. Metikoš-Huković, R. Babić, I. Škugor Rončević, and Z. Grubač. Corrosion resistance of copper–nickel alloy under fluid jet impingement. Desalination, 276:228-232, Aug 2011. URL: https://doi.org/10.1016/j.desal.2011.03.056, doi:10.1016/j.desal.2011.03.056. This article has 25 citations and is from a domain leading peer-reviewed journal.

2. (metikoshukovic2011corrosionresistanceof pages 3-5): M. Metikoš-Huković, R. Babić, I. Škugor Rončević, and Z. Grubač. Corrosion resistance of copper–nickel alloy under fluid jet impingement. Desalination, 276:228-232, Aug 2011. URL: https://doi.org/10.1016/j.desal.2011.03.056, doi:10.1016/j.desal.2011.03.056. This article has 25 citations and is from a domain leading peer-reviewed journal.

3. (wu2023erosion–corrosionbehaviorof pages 1-2): Lei Wu, Aili Ma, Lianmin Zhang, Guangming Li, Lingyue Hu, Zhengbin Wang, and Yugui Zheng. Erosion–corrosion behavior of 90/10 and 70/30 copper–nickel tubes in 1 wt% nacl solution. Metals, 13:401, Feb 2023. URL: https://doi.org/10.3390/met13020401, doi:10.3390/met13020401. This article has 42 citations.

4. (wu2023erosion–corrosionbehaviorof pages 19-21): Lei Wu, Aili Ma, Lianmin Zhang, Guangming Li, Lingyue Hu, Zhengbin Wang, and Yugui Zheng. Erosion–corrosion behavior of 90/10 and 70/30 copper–nickel tubes in 1 wt% nacl solution. Metals, 13:401, Feb 2023. URL: https://doi.org/10.3390/met13020401, doi:10.3390/met13020401. This article has 42 citations.

5. (metikoshukovic2011corrosionresistanceof pages 2-3): M. Metikoš-Huković, R. Babić, I. Škugor Rončević, and Z. Grubač. Corrosion resistance of copper–nickel alloy under fluid jet impingement. Desalination, 276:228-232, Aug 2011. URL: https://doi.org/10.1016/j.desal.2011.03.056, doi:10.1016/j.desal.2011.03.056. This article has 25 citations and is from a domain leading peer-reviewed journal.

6. (wu2023erosion–corrosionbehaviorof pages 2-4): Lei Wu, Aili Ma, Lianmin Zhang, Guangming Li, Lingyue Hu, Zhengbin Wang, and Yugui Zheng. Erosion–corrosion behavior of 90/10 and 70/30 copper–nickel tubes in 1 wt% nacl solution. Metals, 13:401, Feb 2023. URL: https://doi.org/10.3390/met13020401, doi:10.3390/met13020401. This article has 42 citations.

7. (metikoshukovic2011corrosionresistanceof pages 5-5): M. Metikoš-Huković, R. Babić, I. Škugor Rončević, and Z. Grubač. Corrosion resistance of copper–nickel alloy under fluid jet impingement. Desalination, 276:228-232, Aug 2011. URL: https://doi.org/10.1016/j.desal.2011.03.056, doi:10.1016/j.desal.2011.03.056. This article has 25 citations and is from a domain leading peer-reviewed journal.

8. (wu2023erosion–corrosionbehaviorof pages 4-7): Lei Wu, Aili Ma, Lianmin Zhang, Guangming Li, Lingyue Hu, Zhengbin Wang, and Yugui Zheng. Erosion–corrosion behavior of 90/10 and 70/30 copper–nickel tubes in 1 wt% nacl solution. Metals, 13:401, Feb 2023. URL: https://doi.org/10.3390/met13020401, doi:10.3390/met13020401. This article has 42 citations.

9. (wu2023erosion–corrosionbehaviorof pages 11-13): Lei Wu, Aili Ma, Lianmin Zhang, Guangming Li, Lingyue Hu, Zhengbin Wang, and Yugui Zheng. Erosion–corrosion behavior of 90/10 and 70/30 copper–nickel tubes in 1 wt% nacl solution. Metals, 13:401, Feb 2023. URL: https://doi.org/10.3390/met13020401, doi:10.3390/met13020401. This article has 42 citations.

10. (wu2023erosion–corrosionbehaviorof pages 10-11): Lei Wu, Aili Ma, Lianmin Zhang, Guangming Li, Lingyue Hu, Zhengbin Wang, and Yugui Zheng. Erosion–corrosion behavior of 90/10 and 70/30 copper–nickel tubes in 1 wt% nacl solution. Metals, 13:401, Feb 2023. URL: https://doi.org/10.3390/met13020401, doi:10.3390/met13020401. This article has 42 citations.

11. (wu2023erosion–corrosionbehaviorof media b78de47e): Lei Wu, Aili Ma, Lianmin Zhang, Guangming Li, Lingyue Hu, Zhengbin Wang, and Yugui Zheng. Erosion–corrosion behavior of 90/10 and 70/30 copper–nickel tubes in 1 wt% nacl solution. Metals, 13:401, Feb 2023. URL: https://doi.org/10.3390/met13020401, doi:10.3390/met13020401. This article has 42 citations.

12. (jafari2021effectoffluid pages 1-2): Hamid Reza Jafari, Ali Davoodi, and Saman Hosseinpour. Effect of fluid flow on the corrosion performance of as-cast and heat-treated nickel aluminum bronze alloy (uns c95800) in saline solution. Corrosion and Materials Degradation, 2:61-77, Feb 2021. URL: https://doi.org/10.3390/cmd2010004, doi:10.3390/cmd2010004. This article has 12 citations.

13. (jafari2021effectoffluid pages 2-4): Hamid Reza Jafari, Ali Davoodi, and Saman Hosseinpour. Effect of fluid flow on the corrosion performance of as-cast and heat-treated nickel aluminum bronze alloy (uns c95800) in saline solution. Corrosion and Materials Degradation, 2:61-77, Feb 2021. URL: https://doi.org/10.3390/cmd2010004, doi:10.3390/cmd2010004. This article has 12 citations.

14. (jafari2021effectoffluid pages 4-7): Hamid Reza Jafari, Ali Davoodi, and Saman Hosseinpour. Effect of fluid flow on the corrosion performance of as-cast and heat-treated nickel aluminum bronze alloy (uns c95800) in saline solution. Corrosion and Materials Degradation, 2:61-77, Feb 2021. URL: https://doi.org/10.3390/cmd2010004, doi:10.3390/cmd2010004. This article has 12 citations.

15. (jafari2021effectoffluid pages 8-11): Hamid Reza Jafari, Ali Davoodi, and Saman Hosseinpour. Effect of fluid flow on the corrosion performance of as-cast and heat-treated nickel aluminum bronze alloy (uns c95800) in saline solution. Corrosion and Materials Degradation, 2:61-77, Feb 2021. URL: https://doi.org/10.3390/cmd2010004, doi:10.3390/cmd2010004. This article has 12 citations.

16. (jafari2021effectoffluid pages 7-8): Hamid Reza Jafari, Ali Davoodi, and Saman Hosseinpour. Effect of fluid flow on the corrosion performance of as-cast and heat-treated nickel aluminum bronze alloy (uns c95800) in saline solution. Corrosion and Materials Degradation, 2:61-77, Feb 2021. URL: https://doi.org/10.3390/cmd2010004, doi:10.3390/cmd2010004. This article has 12 citations.

17. (lewis1981evaluationofcoppernickel pages 17-19): R. O. Lewis and F. Laque. Evaluation of copper-nickel alloys for otec applications. ArXiv, Apr 1981. URL: https://doi.org/10.2172/6255887, doi:10.2172/6255887. This article has 5 citations.

18. (lewis1981evaluationofcoppernickel pages 14-17): R. O. Lewis and F. Laque. Evaluation of copper-nickel alloys for otec applications. ArXiv, Apr 1981. URL: https://doi.org/10.2172/6255887, doi:10.2172/6255887. This article has 5 citations.

19. (lewis1981evaluationofcoppernickel pages 19-21): R. O. Lewis and F. Laque. Evaluation of copper-nickel alloys for otec applications. ArXiv, Apr 1981. URL: https://doi.org/10.2172/6255887, doi:10.2172/6255887. This article has 5 citations.

20. (zhao2022thelaserdeposited pages 1-2): Lu Zhao, Kailun Li, Jun Yao, Yixiang Yuan, and Baorui Du. The laser deposited nickel-aluminum bronze coatings on sus630 stainless steel and its corrosion resistance in 3.5 wt.% nacl solution. Metals, 12:781, Apr 2022. URL: https://doi.org/10.3390/met12050781, doi:10.3390/met12050781. This article has 8 citations.

21. (zhao2022thelaserdeposited pages 2-4): Lu Zhao, Kailun Li, Jun Yao, Yixiang Yuan, and Baorui Du. The laser deposited nickel-aluminum bronze coatings on sus630 stainless steel and its corrosion resistance in 3.5 wt.% nacl solution. Metals, 12:781, Apr 2022. URL: https://doi.org/10.3390/met12050781, doi:10.3390/met12050781. This article has 8 citations.

22. (zhao2022thelaserdeposited pages 4-7): Lu Zhao, Kailun Li, Jun Yao, Yixiang Yuan, and Baorui Du. The laser deposited nickel-aluminum bronze coatings on sus630 stainless steel and its corrosion resistance in 3.5 wt.% nacl solution. Metals, 12:781, Apr 2022. URL: https://doi.org/10.3390/met12050781, doi:10.3390/met12050781. This article has 8 citations.

23. (zhao2022thelaserdeposited pages 7-10): Lu Zhao, Kailun Li, Jun Yao, Yixiang Yuan, and Baorui Du. The laser deposited nickel-aluminum bronze coatings on sus630 stainless steel and its corrosion resistance in 3.5 wt.% nacl solution. Metals, 12:781, Apr 2022. URL: https://doi.org/10.3390/met12050781, doi:10.3390/met12050781. This article has 8 citations.

24. (zhao2022thelaserdeposited pages 10-13): Lu Zhao, Kailun Li, Jun Yao, Yixiang Yuan, and Baorui Du. The laser deposited nickel-aluminum bronze coatings on sus630 stainless steel and its corrosion resistance in 3.5 wt.% nacl solution. Metals, 12:781, Apr 2022. URL: https://doi.org/10.3390/met12050781, doi:10.3390/met12050781. This article has 8 citations.

25. (schleich2004typicalfailuresof pages 7-9): W Schleich. Typical failures of cuni 90/10 seawater tubing systems and how to avoid them. Unknown journal, 2004.

26. (wu2023erosion–corrosionbehaviorof pages 16-18): Lei Wu, Aili Ma, Lianmin Zhang, Guangming Li, Lingyue Hu, Zhengbin Wang, and Yugui Zheng. Erosion–corrosion behavior of 90/10 and 70/30 copper–nickel tubes in 1 wt% nacl solution. Metals, 13:401, Feb 2023. URL: https://doi.org/10.3390/met13020401, doi:10.3390/met13020401. This article has 42 citations.

27. (wu2023erosion–corrosionbehaviorof pages 18-19): Lei Wu, Aili Ma, Lianmin Zhang, Guangming Li, Lingyue Hu, Zhengbin Wang, and Yugui Zheng. Erosion–corrosion behavior of 90/10 and 70/30 copper–nickel tubes in 1 wt% nacl solution. Metals, 13:401, Feb 2023. URL: https://doi.org/10.3390/met13020401, doi:10.3390/met13020401. This article has 42 citations.

28. (schleich2004typicalfailuresof pages 3-6): W Schleich. Typical failures of cuni 90/10 seawater tubing systems and how to avoid them. Unknown journal, 2004.
