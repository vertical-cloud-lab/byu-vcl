Question: I am setting up a hand-sieving step for metal powder made on an AMAZEMET rePowder ultrasonic atomizer (induction melting module, Al 4047 and later other Al alloys such as 6063 / AlSi10Mg), in a university lab, for use as laser powder bed fusion (LPBF / SLM) feedstock. Each atomization run yields only tens of grams (typically 10-100 g). The powder container is poured onto paper after the run and currently contains chunks (unatomized splats, beads several mm across) mixed with spherical powder. Please critically check the following sieve plan against the literature, ESPECIALLY the experimental/methods sections of papers that sieve or classify atomized powder for LPBF, and flag anything wrong, unusual, unsafe or missing. Be specific and cite.

THE PLAN: a stack of 3-inch (76 mm) diameter, full-height, all-stainless-steel ASTM E11 test sieves: No. 60 (250 um) on top to scalp out chunks, No. 230 (63 um) and No. 635 (20 um) below, over a pan, with a cover; the 20-63 um fraction retained on the 20 um sieve is to be the LPBF print fraction. Optional No. 325 (45 um) for a 20-45 um cut. Sieving by hand with tapping, cover on, dust mask, with the intent to buy a small sieve shaker later.

Q1. What particle size ranges do LPBF papers actually use for Al alloys (AlSi10Mg, Al-Si, 4047, 6xxx), and what sieve cut points do the EXPERIMENTAL SECTIONS report when they sieve atomized or recycled powder for LPBF (e.g. "sieved through 63 um", "classified to 20-63 um", "15-45 um", "<53 um")? Is a LOWER cut at 20 um by dry sieving standard practice, or do labs and suppliers remove fines by air classification (and often leave them in) instead? Is 63 um the usual upper cut for Al LPBF powders, and is the 45 um alternative common?
Q2. Papers that use ultrasonic atomization (AMAZEMET rePowder or similar) for Al alloys: what particle size distribution (D10/D50/D90) do they report, what sieve sizes do they use after atomization, and what yield falls within 20-63 um? Does the atomized powder typically need the fine (<20 um) fraction removed at all?
Q3. Practicality of a 20 um (No. 635) woven-wire test sieve: how prone is it to blinding with Al powder, how much mass can be put on a 76 mm (3 inch) sieve per charge without overloading (ASTM E11 / ISO 3310-1 / ASTM C136 / ISO 2591 / ASTM B214 guidance on sieve loading and residue limits), and is hand tapping sufficient or is a mechanical shaker / ultrasonic deblinding / air-jet sieving needed at 20-45 um? What does ASTM B214 (sieve analysis of metal powders) say about charge mass and sieve size? Note that ASTM B214 is a sieve-analysis method, not a production-sieving method; say what guidance applies to production sieving of small batches.
Q4. 3-inch vs 8-inch (203 mm) sieves for batches of tens of grams: is 3 inch the right choice; what does the literature or sieve-maker guidance say about small-diameter sieves and sample mass?
Q5. Safety: aluminium powder is a combustible dust (NFPA 484, NFPA 652 / 660). Do sieves and sieving stations used for Al/Ti LPBF powders need to be BONDED AND GROUNDED, and does the literature or any standard (NFPA 484, ISO/ASTM 52907, machine-maker guidance from EOS, SLM Solutions, Renishaw, Russell Finex, Farleygreene, etc.) say that sieving reactive metal powders should be done under inert gas or in a glovebox? Is an all-stainless sieve (vs brass frame / stainless cloth) the right choice for Al powder contamination (Cu/Zn pickup) and for ESD?
Q6. Are standard woven-wire ASTM E11 test sieves actually what LPBF labs use for small-batch production sieving of powder, or do they use vibratory sieving stations (e.g. Russell Finex AMPro, Farleygreene Sievgen, EOS/SLM/Renishaw sieve stations) with ultrasonic deblinding? What do research labs with small atomizers (ultrasonic or lab-scale gas atomizers producing 10-500 g) do?
Q7. Does sieving (shear and impact) damage or oxidize Al powder, pick up Fe/Cr from stainless mesh, or change flowability? Any evidence on sieving-induced contamination or satellite breakage?
Q8. Anything else a powder-metallurgy / AM process engineer would object to in the plan above, including record-keeping (weighing every fraction, labelling), moisture/humidity, and cleaning sieves between alloys.


# Critical Review of a Hand-Sieving Plan for Ultrasonically Atomized Al Powder for LPBF

The following is a detailed, literature-referenced critique of the proposed sieve plan for classifying Al 4047 (and related Al alloys) powder produced on an AMAZEMET rePowder ultrasonic atomizer for laser powder bed fusion (LPBF) feedstock.

---

## Q1. Particle Size Ranges and Sieve Cut Points for Al Alloy LPBF Powders

The proposed 20–63 µm print fraction is broadly consistent with the literature but contains an important nuance: **the lower cut at 20 µm is not standard commercial or laboratory practice for Al LPBF powders.**

Commercial AlSi10Mg powder from SLM Solutions is nominally specified as 20–63 µm, while EOS specifies a broader 25–70 µm range (pal2022linkingpowderproperties pages 2-4). A general LPBF guideline for 30 µm layer thicknesses places the mean particle size between 15 and 45 µm (trevisan2018studyandcharacterisation pages 63-66). Weiss et al. (2021) confirmed their virgin AlSi10Mg powder had D10 = 27.3 µm, D50 = 39.7 µm, and D90 = 59.2 µm, consistent with a nominal 20–63 µm range (weiss2021investigationtowardsalsi10mg pages 3-6).

**However, in essentially all experimental LPBF papers reviewed, only an upper scalping sieve is applied—not a lower cut.** Recycling sieves reported include 60 µm (weiss2021investigationtowardsalsi10mg pages 1-3), 70 µm (weiss2021investigationtowardsalsi10mg pages 1-3), 80 µm (moylan2013lessonslearnedin pages 13-16), 90 µm (weiss2021investigationtowardsalsi10mg pages 3-6), and 100 µm (weiss2021investigationtowardsalsi10mg pages 1-3). The purpose of these sieves is to remove spatter and agglomerates, not to classify the lower tail. Commercial gas-atomized Al powders are typically classified by the powder producer using air classification to remove fines and control the lower end of the PSD; the end user simply applies a single upper-cut sieve. A lower cut at 20 µm by dry sieving in a university lab is therefore **unusual and technically problematic** (see Q3 below).

The 45 µm alternative (No. 325) is more commonly encountered in the literature as a fine LPBF specification (15–45 µm is a recognized LPBF feedstock class) (trevisan2018studyandcharacterisation pages 63-66), but again, the lower cut in commercial powders is set by the atomizer/classifier at the supplier, not by the user's test sieve.

**Flag:** Your plan to use a 63 µm upper cut is well-supported. Your 20 µm lower cut is non-standard and will be very difficult to execute by dry sieving (see Q3). Consider whether you actually need a lower cut at all—ultrasonically atomized powder may have very little sub-20 µm material (see Q2).

---

## Q2. Ultrasonic Atomization PSD and Yield for Al Alloys

The following table summarizes the available literature on LPBF-relevant powder produced by ultrasonic atomization:

| Source / paper | Alloy | Powder size range | D10 / D50 / D90 (µm) | Sieve size used | Notes |
|---|---|---:|---:|---:|---|
| SLM Solutions commercial specification summarized by Pal & Basak (2022) | AlSi10Mg | 20–63 µm | Not reported | Not reported | Supplier nominal feedstock range; a specification is not proof of sharp sieve cuts. (pal2022linkingpowderproperties pages 2-4) |
| EOS commercial specification summarized by Pal & Basak (2022) | AlSi10Mg | 25–70 µm | Not reported | Not reported | Demonstrates that 63 µm is not a universal upper limit for Al LPBF powder. (pal2022linkingpowderproperties pages 2-4) |
| Weiss, Munk & Haefner (2021) | AlSi10Mg | Nominal 20–63 µm | 27.3 / 39.7 / 59.2 | 90 µm recycling sieve | The 90 µm sieve removed build by-products; it did not create the nominal 20–63 µm supplier fraction. (weiss2021investigationtowardsalsi10mg pages 3-6) |
| Recycling studies summarized by Weiss et al. (2021) | AlSi10Mg | Typical context: about 10–60 µm | Not consistently reported | 60, 70, and 100 µm, depending on study | Experimental recycling sieves are often coarser than the feedstock’s nominal upper size because their purpose is spatter/agglomerate removal. (weiss2021investigationtowardsalsi10mg pages 1-3) |
| NIST/EOS laboratory workflow, Moylan et al. (2013) | Metal LPBF powder; account not Al-specific | Not reported | Not reported | EOS-supplied 80 µm sieve | Used to recycle unexposed powder after a build; illustrates practical upper-scalping rather than lower-cut classification. (moylan2013lessonslearnedin pages 13-16) |
| Smolina et al. (2022) | AlSi7Mg0.6 | Not reported in cited excerpt | Not reported | Initial 75 µm sieve; double-sieving during reuse | Incoming powder was dried and sieved; powder and sieve waste were separately labelled by reuse history. (smolina2022influenceofthe pages 2-4) |
| Cordova et al. (2020) | Al–Mg–Sc–Zr | Not reported in cited excerpt | Not reported | Mesh not reported in cited excerpt | SLM Solutions PSM100 station combined vibration and ultrasonic excitation under argon; shows industrial practice for deblinding and atmosphere control. (cordova2020effectsofpowder pages 4-6) |
| General LPBF guidance summarized by Trevisan (2018) | Gas-atomized LPBF metals, including Al context | Mean/typical range 15–45 µm for 30 µm layers | Not reported | No production cut reported | Supports 15–45 µm as a common fine LPBF feedstock class, but not as a universal Al specification. (trevisan2018studyandcharacterisation pages 63-66) |
| Yankin et al. (2025), ATO Lab+ US35 ultrasonic atomization | AlSi12 | Usable fraction defined as <63 µm | 38.7–44.7 / 52.3–54.7 / 66.4–72.7 | 63 µm | Approximately 75% passed the 63 µm sieve and was called usable for a Renishaw AM400; no 20 µm lower cut was applied. (yankin2025effectofultrasonic pages 3-4, yankin2025effectofultrasonic pages 2-3) |
| Ukabhai, Mkhonto & Phasha (2025), AMAZEMET rePowder induction module | Al–10Cu | Authors cite 15–75 µm as an LPBF target | 36 / 65 / 78 | No sieve cut reported | Paper also states 90% below 70 µm, inconsistent with its tabulated D90 of 78 µm; no measured 20–63 µm yield was reported. (ukabhai2025investigationofalcu pages 3-7) |
| Jedynak, Härtel & Pippig (2024), rePowder | AlSiMg–SiC aluminum-matrix composite | Powder pre-scalped below 0.2 mm; mean particle sizes about 88–120 µm | Not reported | 200 µm | Induction gave the highest process efficiency, nearly 50%; results are composite- and parameter-specific and are not representative of optimized AlSi10Mg LPBF powder. (jedynak2024processabilityofaluminummatrix pages 3-6) |
| Ciftcli et al. (2025), rePowder | Ti alloy from machining chips | >85% below 100 µm | Volume: 36 / 49 / 118; number: 30 / 41 / 52 | No sieve cut reported | Non-Al comparison showing that number- and volume-based PSDs can differ greatly; the PSD basis must always be recorded. (ciftcli2025alloydevelopmentfrom pages 3-6) |
| Bałasz et al. (2023), ultrasonic atomization comparison | Ti6Al4V | Classified nominally as 63 ± 20 µm | Number: 40.2 / 52.0 / 60.8; volume: 45.4 / 55.0 / 62.4 | Mesh sequence not reported; DIN 66165-1 classification | Used a Multiserw LPzE-3e mechanical sieve shaker at 50 Hz; >98% useful-powder recovery refers to feedstock recovery, not necessarily 20–63 µm yield. (scientific2023comparisonofultrasonic pages 7-8) |


*Table: Reported Al-alloy LPBF feedstock ranges, recycling sieve apertures, and ultrasonic-atomization PSD results. The comparison distinguishes nominal feedstock classifications from coarser sieves used only to remove spatter and agglomerates.*

Key findings for the user's situation:

**AlSi12 on an ATO Lab+ (35 kHz, comparable to rePowder):** Yankin et al. (2025) reported D10 = 38.7–44.7 µm, D50 = 52.3–54.7 µm, D90 = 66.4–72.7 µm, with approximately 75% of powder passing a 63 µm sieve and being deemed suitable for a Renishaw AM400 SLM system. No 20 µm lower cut was applied (yankin2025effectofultrasonic pages 3-4, yankin2025effectofultrasonic pages 2-3).

**Al-10Cu on the AMAZEMET rePowder (induction module):** Ukabhai et al. (2025) reported D10 = 36 µm, D50 = 65 µm, D90 = 78 µm, with an identified LPBF target of 15–75 µm. No lower cut or sieve classification was reported (ukabhai2025investigationofalcu pages 3-7).

**AMC (AlSiMg–SiC) on rePowder (induction):** Jedynak et al. (2024) obtained average particle sizes of 88–120 µm, sieved below 200 µm. Process efficiency with induction was nearly 50%. These larger sizes reflect composite-specific and parameter-specific challenges, not optimized Al LPBF conditions (jedynak2024processabilityofaluminummatrix pages 3-6).

**Ti6Al4V on AMAZEMET-type ultrasonic atomizer:** Bałasz et al. (2023) reported a classified 63 ± 20 µm fraction with number-based D10/D50/D90 of 40.2/52.0/60.8 µm and volume-based 45.4/55.0/62.4 µm, with >98% feedstock recovery. Classification used a Multiserw LPzE-3e mechanical sieve shaker at 50 Hz per DIN 66165-1 (scientific2023comparisonofultrasonic pages 7-8).

**Key implication for your plan:** Ultrasonic atomization characteristically produces a narrow, monomodal PSD centered around 40–65 µm. The D10 values reported are typically 36–45 µm, meaning **very little powder falls below 20 µm.** The 20 µm lower-cut sieve may therefore be unnecessary. You are more likely to lose yield to an oversized fraction above 63 µm than to fines below 20 µm. Consider running your first batch through just the 250 µm scalping sieve and 63 µm sieve, collecting the <63 µm fraction, and measuring its PSD by laser diffraction before deciding whether a 20 µm cut is needed.

---

## Q3. Practicality of a 20 µm (No. 635) Woven-Wire Test Sieve

This is the single most problematic element of the proposed plan. The literature is clear that **conventional dry sieving becomes deficient below approximately 45 µm** (neikov2019powdercharacterizationand pages 4-6). Several mechanisms contribute:

1. **Blinding/blocking:** Near-mesh particles wedge into apertures. Electrostatic charging causes fine Al particles to agglomerate or adhere to the mesh and to larger particles, obstructing openings (neikov2019powdercharacterizationand pages 3-4). Brushing may help, but if it does not, ultrasonic cleaning with a wetting agent is recommended (neikov2019powdercharacterizationand pages 3-4).

2. **Inadequacy of hand sieving:** Standard sieve analysis per ASTM B214 and ISO 4497 specifies a vibrating table with rotary and tapping action, not hand tapping (neikov2019powdercharacterizationand pages 3-4). The powder technology literature emphasizes that lateral/side-to-side shaking causes blinding; vigorous combined vertical and horizontal motion (e.g., Ro-Tap machine) is needed (kaye2008characterizationofpowders pages 77-80). Hand tapping alone will give very poor separation efficiency at 20 µm.

3. **Air-jet sieving for sub-45 µm:** For sieves finer than approximately 45 µm, specialized methods such as the Alpine micromesh jet sieve (which uses suction and a rotating blowback nozzle) are recommended and can operate down to about 10 µm (neikov2019powdercharacterizationand pages 3-4, neikov2019powdercharacterizationand pages 4-6).

4. **Sieve loading:** The Handbook of Non-Ferrous Metal Powders describes charging 100–300 g onto the top sieve of a stack using 75 mm or 200 mm ring sieves with 15–20 min sieving time (neikov2019powdercharacterizationand pages 3-4). For a 76 mm (3-inch) sieve with ~45 cm² area, the charge should be proportionally lower—10–50 g per sieve is a reasonable working limit. ASTM B214 is a sieve-analysis method intended for characterization, not production sieving; it does not provide explicit guidance for production classification of small batches. The user should treat the ASTM B214 charge-mass guidance as an upper bound and use smaller charges on a 20 µm sieve.

5. **Sieve cost and fragility:** Fine woven-wire sieves (No. 635 / 20 µm) are expensive and extremely delicate. Damaged or stretched mesh produces unreliable separations and should be inspected microscopically after each use (neikov2019powdercharacterizationand pages 3-4). Gibbons et al. (2024) note that fine sieve meshes are expensive and easily damaged (gibbons2024metalpowderfeedstock pages 22-23).

**Flag: A 20 µm woven-wire sieve used with hand tapping will almost certainly blind with Al powder and give a poor, irreproducible cut.** If you must remove sub-20 µm fines, an air-jet sieve or air classification is the appropriate method. For a university lab with 10–100 g batches, consider simply omitting the lower cut and characterizing the <63 µm fraction by laser diffraction instead.

---

## Q4. 3-Inch vs. 8-Inch Sieves for Tens-of-Grams Batches

Standard sieve analysis equipment uses sieves mounted in either 75 mm or 200 mm rings (neikov2019powdercharacterizationand pages 3-4). For batches of 10–100 g, 76 mm (3-inch) sieves are an appropriate and common choice. The 200 mm (8-inch) sieves have approximately 7× the sieving area (~324 cm² vs. ~45 cm²), and standard charges of 100–300 g are designed for 200 mm sieves (neikov2019powdercharacterizationand pages 3-4). Using 200 mm sieves with only 10–50 g would result in an excessively thin powder layer, making it difficult to track yield and increasing losses to the sieve surfaces and edges. **The 3-inch choice is correct for this batch size.**

---

## Q5. Safety: Bonding, Grounding, Inerting, and Sieve Material

Aluminum powder is unambiguously a combustible dust. NFPA 484 is the applicable standard for combustible metals and metal dusts, and it references ASTM E11 for test sieve specifications (bruceUnknownyeartechnicalcommitteeon pages 13-22, bruceUnknownyeartechnicalcommitteeon pages 22-26).

**Bonding and grounding are mandatory.** All movable equipment used during powder transfer—including drums, containers, scoops, and by extension sieves—must be bonded and grounded using clips and flexible ground leads. Personnel must also be grounded. Powder must not be poured or slid over nonconductive surfaces, as even small objects can generate sufficient static charge to ignite fine Al powder (benson2012safetyconsiderationswhen pages 10-12, benson2012safetyconsiderationswhena pages 9-10, benson2012safetyconsiderationswhena pages 10-12).

**Inert atmosphere is the preferred/ideal approach.** The safety literature identifies an oxygen-free environment such as a glovebox as the preferred working arrangement for reactive metal powders (benson2012safetyconsiderationswhena pages 9-10, benson2012safetyconsiderationswhen pages 9-10, bensonUnknownyearjsafr pages 9-10). Where a glovebox is not practicable, powder handling should occur carefully within suitable dust extraction, keeping dust concentrations below the minimum explosible concentration (MEC) (benson2012safetyconsiderationswhena pages 9-10). Industrial LPBF sieve stations (e.g., SLM Solutions PSM100) operate under argon for exactly this reason (cordova2020effectsofpowder pages 4-6). For a university lab handling only tens of grams at a time, a fume hood with local extraction and rigorous grounding may be an acceptable risk-managed alternative, but this should be documented in a formal dust hazard analysis (DHA) as required by NFPA 652/484.

**Sieve material:** All-stainless-steel construction is the correct choice for Al alloys. Brass frames contain Cu and Zn, which are contaminants for Al alloys and can affect mechanical properties of printed parts. The NIST AM laboratory noted the use of brass for non-sparking properties (moylan2013lessonslearnedin pages 13-16), but for aluminum powder metallurgy, contamination avoidance takes priority, and stainless steel is both conductive (enabling grounding) and compositionally benign for Al alloys.

**Flag: Your plan mentions a dust mask. This is inadequate.** The NIOSH Health Hazard Evaluation for an AM facility recommends powered air-purifying respirators (PAPRs) during sieving and powder handling activities, especially for reactive powders such as AlSi10Mg (stefaniak2025healthhazardevaluationa pages 96-101, stefaniak2025healthhazardevaluation pages 96-101). At minimum, use a half-face respirator with P100 particulate filters, not a simple dust mask. Nitrile gloves, safety glasses, and fire-resistant lab coat are also required.

---

## Q6. Sieving Equipment: Test Sieves vs. Vibratory/Ultrasonic Stations

Industrial LPBF powder management uses purpose-built sieve stations with vibration plus ultrasonic deblinding under inert gas. Cordova et al. (2020) describe the SLM Solutions PSM100, which operates under argon with combined low-frequency vibration and ultrasonic excitation (cordova2020effectsofpowder pages 4-6). The NIST AM laboratory used an EOS-supplied 80 µm sieve for manual sieving of stainless steel powder (moylan2013lessonslearnedin pages 13-16).

For small-batch atomizer laboratories, standard test sieves with mechanical sieve shakers are the norm. Bałasz et al. (2023) used a Multiserw LPzE-3e sieve shaker at 50 Hz per DIN 66165-1 after ultrasonic atomization (scientific2023comparisonofultrasonic pages 7-8). The Handbook of Non-Ferrous Metal Powders describes a vibrating table with rotary and tapping action as the standard method (neikov2019powdercharacterizationand pages 3-4).

**For your situation:** Hand sieving with tapping is acceptable as a temporary measure for the 250 µm scalping sieve and may work for 63 µm, but a small bench-top sieve shaker (e.g., Fritsch Analysette, Retsch AS 200, or equivalent) is strongly recommended for reproducible results, especially if you attempt separations below 63 µm. Your plan to buy a shaker later is sound, but prioritize it over the 20 µm sieve purchase.

---

## Q7. Sieving-Induced Contamination, Damage, and Oxidation

Soundarapandiyan et al. (2021) identify that particles contacting stainless-steel surfaces (atomizer walls) can pick up iron, and that sieving is not a complete powder-cleanliness solution because small process-affected particles can pass through the mesh (soundarapandiyan2021atechnicalreview pages 5-5). Powell et al. (2020) note that sieving can introduce contaminants from handling accessories (soundarapandiyan2021atechnicalreview pages 5-5). Trevisan (2018) emphasizes that LPBF powders are highly sensitive to contamination and oxidation because of their large surface area, requiring inert-gas storage and handling (trevisan2018studyandcharacterisation pages 63-66).

No quantitative study specifically measuring Fe/Cr pickup from stainless-steel sieve mesh onto Al powder was found in the reviewed literature. However, the contamination pathway is analogous to that documented for atomizer walls, and the risk increases with aggressive sieving (mechanical shaking, ultrasonic excitation) and worn mesh. For tens-of-grams batches sieved a few times, Fe/Cr pickup from a clean stainless-steel sieve is expected to be negligible, but the sieve should be cleaned thoroughly between uses and inspected for wear.

Regarding satellite breakage: sieving action (shear and impact) can break weakly attached satellite particles from larger powder grains, which may actually improve the PSD by releasing them as individual fine particles. This is generally beneficial for LPBF flowability but may slightly increase the fine fraction.

Oxidation during sieving in air is a concern for Al powders. Each handling step in ambient air increases the oxide layer thickness. Minimizing exposure time and, if possible, sieving under argon or in a glovebox will mitigate this (trevisan2018studyandcharacterisation pages 63-66, gomes2023analysisanddevelopment pages 38-42).

---

## Q8. Additional Process Engineering Concerns

Several important items are missing from or should be strengthened in the proposed plan:

1. **Record-keeping and traceability:** Every fraction should be weighed before and after sieving, and the masses recorded along with date, alloy, atomization run number, sieve mesh sizes used, and environmental conditions. ISO/ASTM 52907 and ISO/ASTM 52928 provide frameworks for powder characterization and life-cycle management (gomes2023analysisanddevelopment pages 38-42). Containers should be labelled with alloy, batch, fraction, date, and reuse history (smolina2022influenceofthe pages 2-4, gomes2023analysisanddevelopment pages 42-44).

2. **Moisture and humidity control:** Powder handling should occur at 15–25°C and below 55% relative humidity. Powder and its container should be equilibrated to the same conditions before opening to prevent condensation (gomes2023analysisanddevelopment pages 42-44, gomes2023analysisanddevelopment pages 38-42). Al powder is hygroscopic and moisture promotes oxide growth and agglomeration.

3. **Cleaning sieves between alloys:** Containers and equipment should be dedicated to one alloy base where possible and cleaned thoroughly between batches to prevent cross-contamination (gomes2023analysisanddevelopment pages 42-44, soundarapandiyan2021atechnicalreview pages 5-5). Sieves should be ultrasonically cleaned (in solvent or with wetting agent) and inspected microscopically after use, especially the fine meshes (neikov2019powdercharacterizationand pages 3-4).

4. **Storage:** Sieved powder fractions should be stored in sealed containers backfilled with argon. Long-term storage in argon-filled steel containers is recommended (benson2012safetyconsiderationswhen pages 10-12, gibbons2024metalpowderfeedstock pages 22-23). Do not leave powder exposed on paper or in open containers.

5. **Pouring powder onto paper:** Your current practice of pouring atomized powder onto paper is a contamination and static-charge concern. Paper is nonconductive and can generate triboelectric charge with Al powder. Use a grounded stainless-steel tray or conductive surface instead.

6. **Dust mask inadequacy (reiterated):** Replace with at minimum a half-face P100 respirator; PAPRs are recommended for routine operations (stefaniak2025healthhazardevaluationa pages 96-101).

7. **PSD verification:** After sieving, verify the PSD of your print fraction by laser diffraction (e.g., Malvern Mastersizer). Sieve classification alone does not provide the D10/D50/D90 and span data needed to qualify powder for LPBF.

8. **Yield expectation management:** With ultrasonic atomization at ~40 kHz and induction melting of Al 4047, expect D50 in the range of 50–65 µm based on available Al-alloy UA data (yankin2025effectofultrasonic pages 3-4, ukabhai2025investigationofalcu pages 3-7). With a 63 µm upper cut, you may retain only 50–75% of the atomized powder as print-fraction, and your yield per run of 10–100 g feed could be as low as 5–50 g of usable powder after scalping and classification.

---

## Summary of Flags

| Issue | Severity | Recommendation |
|---|---|---|
| 20 µm lower-cut sieve by dry hand sieving | **Critical** | Omit the 20 µm sieve. UA powder has very little sub-20 µm material. If fine removal is needed, use air-jet sieve or air classification. |
| Hand tapping instead of mechanical shaker | **Moderate** | Acceptable temporarily for 250 µm and 63 µm; inadequate for ≤45 µm. Prioritize purchasing a sieve shaker. |
| "Dust mask" for Al powder | **Critical (safety)** | Replace with P100 half-face respirator minimum; PAPRs recommended. |
| No bonding/grounding mentioned | **Critical (safety)** | Bond and ground all sieves, pans, containers, and personnel. Use conductive surfaces. |
| Pouring powder onto paper | **Moderate (safety + contamination)** | Replace paper with grounded stainless-steel tray. |
| No inert atmosphere during sieving | **Moderate–High (safety)** | Preferred practice is sieving under argon or in glovebox. At minimum, use fume hood with local extraction and conduct formal DHA. |
| No record-keeping or PSD verification mentioned | **Moderate** | Weigh all fractions; label and log every batch; verify PSD by laser diffraction. |
| All-stainless sieve choice | **Correct** | Avoids Cu/Zn contamination from brass. Ensure conductive path for grounding. |
| 3-inch sieve diameter for 10–100 g batches | **Correct** | Well-matched to batch size. |
| 63 µm upper cut | **Correct and well-supported** | Standard LPBF feedstock boundary. |
| 250 µm scalping sieve | **Correct** | Appropriate for removing chunks and splats. |



References

1. (pal2022linkingpowderproperties pages 2-4): Ritam Pal and Amrita Basak. Linking powder properties, printing parameters, post-processing methods, and fatigue properties in additive manufacturing of alsi10mg. Alloys, 1:149-179, Jul 2022. URL: https://doi.org/10.3390/alloys1020010, doi:10.3390/alloys1020010. This article has 44 citations.

2. (trevisan2018studyandcharacterisation pages 63-66): FRANCESCO TREVISAN. Study and characterisation of different metal alloys processed through laser powder bed fusion. ArXiv, Jun 2018. URL: https://doi.org/10.6092/polito/porto/2709711, doi:10.6092/polito/porto/2709711. This article has 7 citations.

3. (weiss2021investigationtowardsalsi10mg pages 3-6): C. Weiss, J. Munk, and C.L. Haefner. Investigation towards alsi10mg powder recycling behavior in the lpbf process and its influences on mechanical properties. Unknown, Jan 2021. URL: https://doi.org/10.26153/tsw/17605, doi:10.26153/tsw/17605. This article has 8 citations.

4. (weiss2021investigationtowardsalsi10mg pages 1-3): C. Weiss, J. Munk, and C.L. Haefner. Investigation towards alsi10mg powder recycling behavior in the lpbf process and its influences on mechanical properties. Unknown, Jan 2021. URL: https://doi.org/10.26153/tsw/17605, doi:10.26153/tsw/17605. This article has 8 citations.

5. (moylan2013lessonslearnedin pages 13-16): Shawn Moylan, John Slotwinski, April Cooke, Kevin Jurrens, and M. Alkan Donmez. Lessons learned in establishing the nist metal additive manufacturing laboratory. ArXiv, Jun 2013. URL: https://doi.org/10.1002/https://dx.doi.org/10.6028/nist.tn.1801, doi:10.1002/https://dx.doi.org/10.6028/nist.tn.1801. This article has 56 citations.

6. (smolina2022influenceofthe pages 2-4): Irina Smolina, Konrad Gruber, Andrzej Pawlak, Grzegorz Ziółkowski, Emilia Grochowska, Daniela Schob, Karol Kobiela, Robert Roszak, Matthias Ziegenhorn, and Tomasz Kurzynowski. Influence of the alsi7mg0.6 aluminium alloy powder reuse on the quality and mechanical properties of lpbf samples. Materials, 15:5019, Jul 2022. URL: https://doi.org/10.3390/ma15145019, doi:10.3390/ma15145019. This article has 36 citations.

7. (cordova2020effectsofpowder pages 4-6): Laura Cordova, Ton Bor, Marc de Smit, Simone Carmignato, Mónica Campos, and Tiedo Tinga. Effects of powder reuse on the microstructure and mechanical behaviour of al–mg–sc–zr alloy processed by laser powder bed fusion (lpbf). Additive Manufacturing, 36:101625, Dec 2020. URL: https://doi.org/10.1016/j.addma.2020.101625, doi:10.1016/j.addma.2020.101625. This article has 117 citations and is from a highest quality peer-reviewed journal.

8. (yankin2025effectofultrasonic pages 3-4): Andrei Yankin, Hussain Ali Murtaza, Boris Golman, Asma Perveen, and Didier Talamona. Effect of ultrasonic atomization parameters on alsi12 aluminum powder characteristics for additive manufacturing. Scientific Reports, Jul 2025. URL: https://doi.org/10.1038/s41598-025-06086-7, doi:10.1038/s41598-025-06086-7. This article has 5 citations and is from a peer-reviewed journal.

9. (yankin2025effectofultrasonic pages 2-3): Andrei Yankin, Hussain Ali Murtaza, Boris Golman, Asma Perveen, and Didier Talamona. Effect of ultrasonic atomization parameters on alsi12 aluminum powder characteristics for additive manufacturing. Scientific Reports, Jul 2025. URL: https://doi.org/10.1038/s41598-025-06086-7, doi:10.1038/s41598-025-06086-7. This article has 5 citations and is from a peer-reviewed journal.

10. (ukabhai2025investigationofalcu pages 3-7): Kiyaasha Dyal Ukabhai, Donald Mkhonto, and Maje Phasha. Investigation of al-cu using different preparation methods on the amazemet repowder machine. MATEC Web of Conferences, 417:03001, Jan 2025. URL: https://doi.org/10.1051/matecconf/202541703001, doi:10.1051/matecconf/202541703001. This article has 0 citations.

11. (jedynak2024processabilityofaluminummatrix pages 3-6): A JEDYNAK, S HÄRTEL, and R PIPPIG. Processability of aluminum-matrix composite (amc) by ultrasonic powder atomization. Materials Research Proceedings, 41:156-163, May 2024. URL: https://doi.org/10.21741/9781644903131-17, doi:10.21741/9781644903131-17. This article has 1 citations.

12. (ciftcli2025alloydevelopmentfrom pages 3-6): Jakub Ciftcli, Tomasz Choma, Bartosz Morończyk, Bartosz Kalicki, Filip Puchalski, and Łukasz Żrodowski. Alloy development from sustainable materials – close-loop of materials using ultrasonic atomization. Journal of the Japan Society of Powder and Powder Metallurgy, 72:S729-S735, Mar 2025. URL: https://doi.org/10.2497/jjspm.15e-sis13-03, doi:10.2497/jjspm.15e-sis13-03. This article has 7 citations.

13. (scientific2023comparisonofultrasonic pages 7-8): International Scientific, B. Bałasz, M. Bielecki, W. Gulbiński, and Ł. Słoboda. Comparison of ultrasonic and other atomization methods in metal powder production. Journal of Achievements in Materials and Manufacturing Engineering, 116:11-24, Jan 2023. URL: https://doi.org/10.5604/01.3001.0016.3393, doi:10.5604/01.3001.0016.3393. This article has 38 citations.

14. (neikov2019powdercharacterizationand pages 4-6): Oleg D. Neikov and Nikolay A. Yefimov. Powder characterization and testing. Handbook of Non-Ferrous Metal Powders, pages 3-62, Jan 2019. URL: https://doi.org/10.1016/b978-0-08-100543-9.00001-4, doi:10.1016/b978-0-08-100543-9.00001-4. This article has 109 citations.

15. (neikov2019powdercharacterizationand pages 3-4): Oleg D. Neikov and Nikolay A. Yefimov. Powder characterization and testing. Handbook of Non-Ferrous Metal Powders, pages 3-62, Jan 2019. URL: https://doi.org/10.1016/b978-0-08-100543-9.00001-4, doi:10.1016/b978-0-08-100543-9.00001-4. This article has 109 citations.

16. (kaye2008characterizationofpowders pages 77-80): Brian H. Kaye. Characterization of powders and aerosols. ArXiv, Mar 2008. URL: https://doi.org/10.1002/9783527614028, doi:10.1002/9783527614028. This article has 62 citations.

17. (gibbons2024metalpowderfeedstock pages 22-23): Duncan W. Gibbons, Preyin Govender, and Andre F. van der Merwe. Metal powder feedstock evaluation and management for powder bed fusion: a review of literature, standards, and practical guidelines. Progress in Additive Manufacturing, 9:805-833, Jul 2024. URL: https://doi.org/10.1007/s40964-023-00484-x, doi:10.1007/s40964-023-00484-x. This article has 52 citations and is from a peer-reviewed journal.

18. (bruceUnknownyeartechnicalcommitteeon pages 13-22): LMD Bruce. Technical committee on combustible metals and metal dusts nfpa 484 second draft meeting agenda july 15-17, 2020 11: 00 am–5: 00 pm …. Unknown journal, Unknown year.

19. (bruceUnknownyeartechnicalcommitteeon pages 22-26): LMD Bruce. Technical committee on combustible metals and metal dusts nfpa 484 second draft meeting agenda july 15-17, 2020 11: 00 am–5: 00 pm …. Unknown journal, Unknown year.

20. (benson2012safetyconsiderationswhen pages 10-12): JM Benson. Safety considerations when handling metal powders. Unknown journal, 2012.

21. (benson2012safetyconsiderationswhena pages 9-10): JM Benson. Safety considerations when handling metal powders. Unknown journal, 2012.

22. (benson2012safetyconsiderationswhena pages 10-12): JM Benson. Safety considerations when handling metal powders. Unknown journal, 2012.

23. (benson2012safetyconsiderationswhen pages 9-10): JM Benson. Safety considerations when handling metal powders. Unknown journal, 2012.

24. (bensonUnknownyearjsafr pages 9-10): JM Benson. Js afr. Unknown journal, Unknown year.

25. (stefaniak2025healthhazardevaluationa pages 96-101): AB Stefaniak, ED Brusak, LN Bowers, and S Friend. Health hazard evaluation program: evaluation of metals exposure in a metal powder additive manufacturing facility. Unknown journal, 2025.

26. (stefaniak2025healthhazardevaluation pages 96-101): AB Stefaniak, ED Brusak, LN Bowers, and S Friend. Health hazard evaluation program: evaluation of metals exposure in a metal powder additive manufacturing facility. Unknown journal, 2025.

27. (soundarapandiyan2021atechnicalreview pages 5-5): Gowtham Soundarapandiyan, Carol Johnston, Raja H.U. Khan, Bo Chen, and Michael E. Fitzpatrick. A technical review of the challenges of powder recycling in the laser powder bed fusion additive manufacturing process. The Journal of Engineering, 2021:97-103, Jan 2021. URL: https://doi.org/10.1049/tje2.12013, doi:10.1049/tje2.12013. This article has 50 citations and is from a peer-reviewed journal.

28. (gomes2023analysisanddevelopment pages 38-42): VHO Gomes. Analysis and development of powder-metal vacuum systems for post-processing in l-pbf. Unknown journal, 2023.

29. (gomes2023analysisanddevelopment pages 42-44): VHO Gomes. Analysis and development of powder-metal vacuum systems for post-processing in l-pbf. Unknown journal, 2023.