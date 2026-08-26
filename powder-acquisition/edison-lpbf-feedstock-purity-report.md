# Edison Scientific Literature Report: Feedstock Purity & Particle Size for Al-Alloy LPBF Powder Synthesis

**Context:** [Issue #161 — Atomizer Powder Acquisition](https://github.com/vertical-cloud-lab/byu-vcl/issues/161)

- **Edison task ID:** `a0bdf588-4bb1-4f75-8950-b069ac7bd154`
- **Job type:** `job-futurehouse-paperqa3-high` (high-effort literature query)
- **Submitted:** 2026-07-15 18:46 UTC · **Status:** success
- **Scope:** Purity levels for elemental feedstocks (Al, Mn, Cr, Zr, Mg, Si, Cu, Ti, Fe, Ni, Ce, Sc, Li, Er, Zn, Sn), feedstock particle size for melt-and-atomize workflows (~100 g ultrasonic atomization batches), and handling/master-alloy guidance for reactive/expensive elements.

Everything below this line is the verbatim Edison Scientific output (query, answer, and references).

---

Question: 
We are synthesizing custom aluminum-based alloy powders for laser powder bed fusion (LPBF)
by blending elemental feedstock powders, melting, and ultrasonic atomization (~100 g batches).
The base is Al, with alloying additions drawn from: Mn, Cr, Zr, Mg, Si, Cu, Ti, Fe, Ni, Ce, Sc,
Li, Er, Zn, and Sn in varying quantities.

Questions:
1. What purity levels (e.g., 99.5%, 99.9%, 99.99%) should we purchase for each elemental
   feedstock powder (Al, Mn, Cr, Zr, Mg, Si, Cu, Ti, Fe, Ni, Ce, Sc, Li, Er, Zn, Sn) for
   optimal LPBF powder synthesis? Which impurities (especially O, H, Fe, alkali metals) are
   most damaging to Al-alloy LPBF performance (porosity, hot cracking, mechanical properties),
   and which elements justify paying for higher purity vs. standard technical grade?
2. What feedstock particle sizes are appropriate when the powders are used as melt feedstock
   for atomization (not directly printed)? Are coarser powders (e.g., 45-150 um or -100 mesh)
   acceptable or preferable to fine 15-45 um powder for melting/blending, considering oxide
   surface area, safety (pyrophoricity of fine Al, Mg, Li powders), and dissolution kinetics?
3. Any special handling/sourcing considerations for reactive or expensive elements (Li, Mg, Sc,
   Er, Ce) — e.g., should Li or Sc be added via master alloys (Al-Sc, Al-Li, Al-Zr) instead of
   elemental powders, and what purity/form are these available in?
Please cite literature on feedstock purity effects in Al LPBF alloys (e.g., Scalmalloy, Al-Ce,
Al-Mn-Sc systems) where possible.



# Feedstock Powder Selection for Custom Aluminum Alloy Synthesis via Ultrasonic Atomization for LPBF

## 1. Purity Levels for Elemental Feedstock Powders

### 1.1 Published Purity Precedents from Custom Al-Alloy LPBF Powder Workflows

Several recent studies have produced custom aluminum alloys for LPBF via elemental blending, melting, and atomization, providing direct precedents for feedstock purity selection:

- **Al-Er-Zr-Ni system (ultrasonic atomization):** Taheri-Mousavi et al. (2026) used high-purity granulates (<5 mm) for induction melting at 1000°C followed by ultrasonic atomization: Al 99.99%, Ni 99.99%, Er 99.9%, and Zr 99.95% (taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 22-25).

- **Al-Mn-Ce system (EIGA atomization):** Gabrysiak et al. (2021) produced Al₉₂Mn₆Ce₂ (at.%) powder by induction melting followed by electrode induction melting inert gas atomization (EIGA), using Al 99.99%, Mn 99.7%, and Ce >99% (gabrysiak2021developmentandcharacterization pages 2-3).

- **HEA system (ultrasonic atomization):** Goncharov et al. (2026) used 99.9% purity elemental powders (Al, Cr, Cu, Fe, Mn, Ni) with particle sizes <45 μm from Sigma-Aldrich, blended by mechanical mixing, cold pressed into rods, arc remelted, and then ultrasonically atomized on an Amazemet rePowder platform (goncharov2026designofcobaltfree pages 2-4, goncharov2026designofcobaltfree pages 8-10).

- **Al-Sc-Zr system (direct LPBF of elemental blends):** Glerum (2023) used Al powder (99.7% nominal, confirmed 99.9% by chemical analysis, 30 μm average, from US Nano), Sc powder (99.5%, <44 μm, from Nanografi), and Zr powder (99%, <44 μm and <20 μm, from US Nano) (anne2023laserpowderbedfusion pages 31-35).

- **Scalmalloy® (commercial gas-atomized):** The commercial Scalmalloy specification is Al-4.6Mg-0.66Sc-0.42Zr-0.49Mn (wt%), with Fe tightly controlled at ~0.068 wt% nominal, though one powder lot measured 0.169 wt% Fe (spierings2018powderspreadabilityand pages 133-137, cerri2024mainheattreatments pages 2-5).

### 1.2 Recommended Purity Levels

The following table consolidates recommended purity levels, preferred feedstock forms, and key impurity concerns for each element:

| Element | Recommended Purity | Preferred Form | Key Impurity Concerns | Literature Precedent |
|---|---:|---|---|---|
| Al | 99.9–99.99% | Granules/shot/ingot preferred; coarse powder acceptable if remelting from small batches | O/H pickup, Fe, Si, alkalis; oxide films and moisture are major LPBF defect drivers | Al 99.99% granulate in induction melt + UA; Al 99.99% for Al-Mn-Ce ingot + EIGA; Al powder 99.7% nominal, 99.9% measured in elemental-blend LPBF (taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 22-25, gabrysiak2021developmentandcharacterization pages 2-3, anne2023laserpowderbedfusion pages 31-35, fedina2022influenceofalsi10mg pages 5-6) |
| Mn | ≥99.7% | Granules/lumps or coarse powder | O, Fe; Mn oxidation and composition drift during atomization | Mn 99.7% used successfully for Al-Mn-Ce powder production by induction melting + EIGA (gabrysiak2021developmentandcharacterization pages 2-3) |
| Cr | 99.9% | Powder or granules | O, Fe, alkalis; avoid oxide-rich fine powder | 99.9% elemental Cr powder <45 µm used in blend → remelted rod → UA workflow (goncharov2026designofcobaltfree pages 2-4) |
| Zr | 99.9% minimum; 99.95% preferred when Zr is a key microalloy addition | Master alloy (Al-Zr) preferred; otherwise granules/coarse powder | O, H, Fe; undissolved particles and oxide surface films if too fine/dirty | Zr 99% powder used in elemental-blend LPBF; Zr 99.95% granulate used in induction melt + UA; published custom Al alloys rely strongly on Zr-controlled precipitation behavior (anne2023laserpowderbedfusion pages 31-35, taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 22-25, anne2023laserpowderbedfusion pages 27-31, taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 7-9) |
| Mg | 99.9% minimum; 99.95% preferred | Master alloy (Al-Mg) or clean lump/granule; avoid very fine powder if possible | O/H, moisture, oxidation loss, evaporation during melting/LPBF | No direct purity number in retrieved LPBF atomization studies, but Mg is central in Scalmalloy/AlMgScZr and highly sensitive to oxidation and H porosity; drying and oxide control are critical (cerri2024mainheattreatments pages 2-5, zhao2021somefactorsaffecting pages 2-3, zhao2021somefactorsaffecting pages 1-2, fedina2022influenceofalsi10mg pages 5-6) |
| Si | 99.9% | Lump/granule or coarse powder | Fe, Ca/alkalis, O | Si additions are commonly used in LPBF Al alloys; for atomization feedstock, technical rationale supports 99.9% to limit Fe-bearing brittle phases and oxide carry-in (anne2023laserpowderbedfusion pages 27-31, spierings2018powderspreadabilityand pages 133-137, cerri2024mainheattreatments pages 2-5) |
| Cu | 99.9% | Granules/lumps or coarse powder | O, Fe, Pb/Bi-type tramp elements | 99.9% elemental Cu powder <45 µm used in UA precursor blending workflow; Cu loss during remelting/atomization was observed, so clean feedstock helps composition control (goncharov2026designofcobaltfree pages 2-4, goncharov2026designofcobaltfree pages 10-13) |
| Ti | 99.9% | Master alloy (Al-Ti or Al-Ti-B) preferred; otherwise powder/granule | O, N, Fe; coarse undissolved Ti if melting is insufficient | Elemental-blend LPBF work includes Ti-containing alloys and Al-Ti compositions; recommendation is to use high-purity Ti or master alloy for cleaner dissolution and less oxide burden (anne2023laserpowderbedfusion pages 45-49, anne2023laserpowderbedfusion pages 27-31) |
| Fe | 99.9% if intentionally alloyed; otherwise keep as low as possible as impurity | Granules/lumps or coarse powder only if intentional addition | Fe is itself often the damaging impurity in Al alloys; promotes brittle Fe-rich intermetallics | Scalmalloy specification shows Fe tightly limited (~0.068 wt% nominal; measured 0.169 wt% in one powder lot), supporting strict control unless Fe is a designed addition (spierings2018powderspreadabilityand pages 133-137, cerri2024mainheattreatments pages 2-5) |
| Ni | 99.9–99.99% | Granules preferred; powder acceptable | O, Fe cross-contamination | Ni 99.99% granulate used in induction melt + UA; 99.9% Ni powder <45 µm used in blend → remelt → UA process (taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 22-25, goncharov2026designofcobaltfree pages 2-4) |
| Ce | >99% minimum; 99.5–99.9% preferred if budget allows | Master alloy (Al-Ce) or clean lump/granule preferred; powder acceptable with inert handling | O, moisture, oxide skin, rare-earth oxide inclusions | Al-Mn-Ce LPBF powder used Ce >99% with induction melting + EIGA successfully (gabrysiak2021developmentandcharacterization pages 2-3) |
| Sc | 99.5% minimum; 99.9% preferred if economically tolerable | Strongly prefer master alloy (Al-Sc or Al-Mg-Sc); elemental powder only for research-scale blends | O, Fe, cost loss in dross, dissolution uniformity | Sc 99.5% powder used in elemental-blend LPBF; Scalmalloy relies on low Sc additions with tight chemistry control, making master-alloy practice attractive for repeatability (anne2023laserpowderbedfusion pages 31-35, spierings2018powderspreadabilityand pages 133-137, cerri2024mainheattreatments pages 2-5) |
| Li | 99.9% if elemental, but master alloy strongly preferred | Strongly prefer Al-Li master alloy under inert handling; avoid fine elemental Li powder | Extreme reactivity to O/H/N, moisture, alkalis; high handling/safety risk and composition loss | No direct Li purity precedent in retrieved set; recommendation is based on Li’s exceptional reactivity versus the demonstrated importance of H/O control in Al AM feedstocks (fedina2022influenceofalsi10mg pages 5-6, zhao2021somefactorsaffecting pages 2-3, zhao2021somefactorsaffecting pages 1-2) |
| Er | 99.9% minimum; 99.95% preferred when Er is a primary strengthening addition | Master alloy (Al-Er) or granules preferred | O, Fe, rare-earth oxide inclusions | Er 99.9% granulate used successfully in induction melt + UA custom Al alloy development (taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 22-25, taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 7-9) |
| Zn | 99.9–99.99% | Lump/granule or master alloy preferred | O, Cd/Pb/Sn-type tramp elements, evaporation loss | No direct purity precedent in retrieved custom-UA studies; recommendation reflects volatility/composition-loss sensitivity in high-solute Al-Zn-Mg LPBF alloys (taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 18-22) |
| Sn | 99.9% | Lump/granule | Pb, Bi, Sb contamination; low-melting segregation | No direct precedent in retrieved Al LPBF atomization studies; use high-purity Sn only if intentionally added and keep tramp low due to segregation and cracking concerns in Al melts (taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 15-18, taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 18-22) |


*Table: This table summarizes recommended purity levels, preferred feedstock form, and main impurity concerns for each elemental addition used to make custom Al-alloy powders for LPBF via ultrasonic atomization. It combines direct literature precedents from published custom-alloy workflows with practical recommendations for elements not explicitly covered in the retrieved studies.*

### 1.3 Most Damaging Impurities

**Oxygen** is the most critical impurity for Al-alloy LPBF performance. Oxide films on powder particle surfaces cause lack-of-fusion (LoF) porosity due to poor wetting between molten aluminum and Al₂O₃/MgAl₂O₄ oxide phases (yakubov2024recycledaluminiumfeedstock pages 7-9). In AlSi10Mg LPBF powder, virgin oxygen content of 0.067 wt% increased approximately 4-fold to 0.257 wt% after 96 hours of aging, causing porosity to increase from 3.16% to 6.5% and significant degradation of yield strength and UTS (fedina2022influenceofalsi10mg pages 1-2, fedina2022influenceofalsi10mg pages 5-6). Oxide-related pores are irregular in shape and can reach several hundred micrometers in diameter, making them critical "killer" defects for fatigue performance (kramer2025impactofdifferent pages 1-2).

**Hydrogen** is the second most important impurity. Hydrogen is absorbed from moisture on powder surfaces and from atmospheric humidity during processing. When molten aluminum solidifies, the dramatic drop in hydrogen solubility causes nucleation of gas pores. However, hydrogen-induced pores are typically small (<5–30 μm) and spherical, with a relatively minor impact on static mechanical properties compared to oxide-related defects (kramer2025impactofdifferent pages 1-2). Powder drying at 80°C for 10 hours has been shown to reduce small hydrogen pores (<50 μm) in AlMgScZr alloys, though it does not eliminate larger pores (zhao2021somefactorsaffecting pages 3-5, zhao2021somefactorsaffecting pages 1-2).

**Iron** is a damaging tramp element in most Al alloys. Even at low levels, Fe forms brittle intermetallic phases (e.g., β-Al₅FeSi, Al₃Fe) that reduce ductility and fatigue life. The Scalmalloy specification limits Fe to ~0.068 wt%, underscoring the importance of Fe control (spierings2018powderspreadabilityand pages 133-137). When purchasing Al feedstock, Fe and Si are the most common impurities, and going from 99.7% to 99.99% Al primarily reduces these contaminants.

**Alkali metals (Na, K, Ca)** are known embrittlers in conventional aluminum metallurgy (causing hot shortness and grain boundary weakening), though specific quantitative data in LPBF literature is limited. These are controlled by purchasing higher-purity Al and Mg feedstock.

### 1.4 Which Elements Justify Higher Purity?

- **Al (the base metal):** Justifies 99.9–99.99% because it constitutes >85 wt% of the alloy; even small impurity fractions translate to significant absolute contamination. Going from 99.7% to 99.99% primarily reduces Fe and Si from ~0.035 at.% each to <0.005% (anne2023laserpowderbedfusion pages 31-35).

- **Zr, Er, Sc (microalloying additions at 0.1–1 wt%):** Higher purity (≥99.9%) is justified because these elements control critical L1₂ precipitate nucleation and grain refinement; impurities in these feedstocks (especially oxygen) could introduce oxide inclusions that act as crack nucleation sites (taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 22-25, anne2023laserpowderbedfusion pages 31-35).

- **Mn, Cr, Si, Cu, Zn, Fe, Ti, Ni, Sn:** Standard 99.9% is generally sufficient for these elements. They are added at higher concentrations or are less sensitive to trace impurity effects. For Fe specifically, 99.9% is adequate only if Fe is an intentional addition; otherwise, Fe should be minimized through high-purity Al.

- **Li:** Justifies the highest practical purity to avoid alkali metal cross-contamination (Na, K), but the strong recommendation is to avoid elemental Li powder entirely and use Al-Li master alloy instead.

---

## 2. Feedstock Particle Size for Melt Feedstock (Not Directly Printed)

### 2.1 Coarse Powders and Alternative Forms Are Acceptable for Melt Feedstock

Since the elemental powders are being melted and re-atomized rather than directly printed, the strict LPBF particle size requirements (15–45 μm for LPBF, 45–106 μm for EBM) do not apply to the feedstock (anderson2018feedstockpowderprocessing pages 2-3, anderson2018feedstockpowderprocessing pages 4-5). Gas atomization and ultrasonic atomization methods accept various feedstock forms including cast alloy, pure metal ingots, and recycled oversized powder (anderson2018feedstockpowderprocessing pages 3-4). Ultrasonic atomization (rePowder-type systems) accepts "any form" of feedstock according to comparative reviews of atomization technologies (yadegari2025aluminumlaseradditive pages 8-9).

Published workflows confirm this flexibility:
- Taheri-Mousavi et al. used **granulates <5 mm** for induction melting at 1000°C before ultrasonic atomization (taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 22-25).
- Goncharov et al. used **<45 μm elemental powders** that were blended, cold pressed into cylindrical rods, and arc remelted before ultrasonic atomization (goncharov2026designofcobaltfree pages 2-4, goncharov2026designofcobaltfree pages 8-10).
- Gabrysiak et al. used bulk raw materials that were **induction melted into ingots** before EIGA atomization (gabrysiak2021developmentandcharacterization pages 2-3).

### 2.2 Advantages of Coarser Feedstock

**Coarser powders (45–150 μm, or -100 mesh), granules, lumps, or shot are preferable** over fine 15–45 μm powder as melt feedstock for several reasons:

1. **Reduced oxide surface area:** Fine powders have much higher specific surface area, leading to proportionally greater oxide film mass per unit of metal. Since all feedstock will be completely melted, the total oxide burden carried into the melt is directly proportional to the cumulative surface oxide. Coarser particles minimize this contamination pathway (yakubov2024recycledaluminiumfeedstock pages 6-7, yakubov2024recycledaluminiumfeedstock pages 7-9).

2. **Safety:** Fine aluminum powder (<45 μm) presents significant dust explosion and pyrophoricity hazards. Fine Mg and Li powders are especially dangerous—Mg powder is readily ignitable in air, and Li is extremely reactive with moisture and oxygen. Using coarser granules, lumps, or shot dramatically reduces these risks.

3. **Dissolution kinetics are irrelevant:** Since the feedstock is fully melted (not dissolved in a solid-state process), particle size does not affect dissolution kinetics. Complete melting occurs regardless of initial particle size.

4. **Reduced hydrogen pickup:** Finer powders adsorb more moisture per unit mass due to higher surface area. Hydroxide layers on Al powder surfaces are a primary source of hydrogen that causes porosity during solidification (zhao2021somefactorsaffecting pages 2-3, yakubov2024recycledaluminiumfeedstock pages 7-9).

### 2.3 Practical Recommendation

For ~100 g batch ultrasonic atomization: use **granules, shot, or lumps (1–5 mm)** for the major elements (Al, Cu, Zn, Ni, Si, Sn) and **coarse powder (45–150 μm) or small granules** for refractory/high-melting elements (Cr, Mn, Ti, Zr, Fe) where finer subdivision aids faster melting. Master alloy pieces or chips are ideal for Sc, Er, Ce, and Li additions.

---

## 3. Special Handling and Sourcing Considerations for Reactive/Expensive Elements

### 3.1 Lithium (Li)

Li is the most challenging element in this list. Elemental Li is extremely reactive with oxygen, nitrogen, and moisture—it tarnishes in seconds in ambient air and reacts vigorously with water. Fine Li powder is pyrophoric and a severe fire/explosion hazard. **The strong recommendation is to add Li exclusively via Al-Li master alloy** (typically Al-5Li or Al-10Li, available from suppliers such as KBM Affilips or AMG Aluminum). Al-Li master alloys are commercially available with controlled Li content and are far safer to handle, store, and weigh than elemental Li. All handling should occur under inert atmosphere (Ar glovebox) or dry room conditions.

### 3.2 Magnesium (Mg)

Fine Mg powder (<45 μm) is a significant fire and explosion hazard and is classified as a dangerous good for shipping. Mg also has high vapor pressure, leading to evaporation losses during melting and LPBF processing—a well-known issue in Scalmalloy production (cerri2024mainheattreatments pages 2-5). **Coarse Mg granules, turnings, or Al-Mg master alloy (e.g., Al-50Mg)** are preferred for melt feedstock. Mg feedstock should be stored under inert atmosphere and handled with care to avoid moisture exposure, as Mg(OH)₂ formation introduces hydrogen into the melt. Purity of ≥99.9% is recommended; common Mg impurities include Fe, Ni, Cu, and alkali metals.

### 3.3 Scandium (Sc)

Sc is extremely expensive (~$3,000–15,000/kg depending on form and purity). Elemental Sc powder oxidizes readily and is costly. **Al-Sc master alloys (typically Al-2Sc) are strongly preferred** and are the standard practice in conventional and AM alloy production. Al-2Sc master alloy is commercially available from suppliers such as KBM Affilips, RUSAL, or Stanford Advanced Materials. For research-scale elemental blending, Glerum (2023) demonstrated that 99.5% Sc powder (<44 μm) can be successfully used in direct LPBF of elemental blends (anne2023laserpowderbedfusion pages 31-35), but for melt-and-atomize workflows, master alloy lumps/granules are more practical.

### 3.4 Erbium (Er)

Er is a moderately expensive rare earth element. Taheri-Mousavi et al. successfully used 99.9% Er granulates (<5 mm) for induction melting followed by ultrasonic atomization (taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 22-25). **Al-Er master alloy (typically Al-5Er or Al-10Er)** is commercially available and reduces oxide introduction and handling complexity. Elemental Er lumps/granules are acceptable if handled to minimize surface oxidation.

### 3.5 Cerium (Ce)

Ce is the least expensive rare earth element and more readily available than Sc or Er. Gabrysiak et al. used Ce >99% successfully for Al-Mn-Ce alloy production via induction melting + EIGA (gabrysiak2021developmentandcharacterization pages 2-3). Ce is mildly pyrophoric as a fine powder but is generally safe as lumps or granules. **Al-Ce master alloy (Al-10Ce or Al-20Ce) or Ce mischmetal** can be used; alternatively, Ce lumps (>99%) are practical for small-batch work. Surface oxide on Ce pieces should be mechanically removed or the pieces should be stored under inert atmosphere.

### 3.6 General Handling Recommendations

- **Inert atmosphere:** All weighing and blending of reactive powders (especially Li, Mg, and fine Al) should be performed in an Ar-filled glovebox or under Ar blanket (anne2023laserpowderbedfusion pages 35-39).
- **Powder drying:** All feedstock powders should be oven-dried at 80°C for ≥10 hours before use to remove adsorbed moisture that would introduce hydrogen into the melt (zhao2021somefactorsaffecting pages 3-5, zhao2021somefactorsaffecting pages 1-2, zhao2021somefactorsaffecting pages 2-3).
- **Atomization atmosphere:** The atomization chamber should be purged to low oxygen levels. Goncharov et al. achieved O₂ content of 23 ppm at start and 50 ppm during working conditions for their ultrasonic atomization (goncharov2026designofcobaltfree pages 10-13).
- **Sonotrode contamination:** Ultrasonic atomization can introduce Mo contamination from molybdenum sonotrodes—Goncharov et al. observed ~2.6 at.% Mo pickup (goncharov2026designofcobaltfree pages 10-13). Ti sonotrodes may similarly contaminate the melt. This should be considered when selecting atomization equipment.
- **Composition losses:** Volatile elements (Mg, Zn, Li, Mn) may experience evaporation losses during melting and atomization. Goncharov et al. observed Mn and Cu losses during arc remelting and atomization (goncharov2026designofcobaltfree pages 10-13). Over-alloying the melt charge by 5–15% for volatile elements is standard practice.

### 3.7 Master Alloy Summary

For the workflow described (blending → melting → ultrasonic atomization at ~100 g scale), the following master alloys are recommended where practical:

| Element | Recommended Master Alloy | Typical Composition | Rationale |
|---------|-------------------------|-------------------|-----------|
| Li | Al-Li | Al-5Li or Al-10Li | Safety (Li pyrophoricity), composition control |
| Sc | Al-Sc | Al-2Sc | Cost, oxide reduction, dissolution uniformity |
| Er | Al-Er | Al-5Er or Al-10Er | Oxide reduction, handling convenience |
| Ce | Al-Ce | Al-10Ce or Al-20Ce | Handling convenience; lumps also acceptable |
| Zr | Al-Zr | Al-10Zr or Al-15Zr | Dissolution uniformity, avoids undissolved Zr particles |
| Ti | Al-Ti or Al-Ti-B | Al-5Ti-1B or Al-10Ti | Standard grain refinement practice |

For small research batches (~100 g), elemental granules/lumps at the purities listed in the table above remain a practical and published approach, as demonstrated by Taheri-Mousavi et al. and Goncharov et al. (taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 22-25, goncharov2026designofcobaltfree pages 2-4). The choice between elemental feedstock and master alloys depends on the specific alloy design, batch size economics, and available handling infrastructure.


References

1. (taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 22-25): S. Mohadeseh Taheri‐Mousavi, Michael Xu, Florian Hengsbach, Clay Houser, Zhaoxuan Ge, Benjamin Glaser, Shaolou Wei, Mirko Schaper, James M. LeBeau, Greg B. Olson, and A. John Hart. Additively manufacturable high‐strength aluminum alloys with coarsening‐resistant microstructures achieved via rapid solidification. Advanced Materials, Oct 2026. URL: https://doi.org/10.1002/adma.202509507, doi:10.1002/adma.202509507. This article has 13 citations and is from a highest quality peer-reviewed journal.

2. (gabrysiak2021developmentandcharacterization pages 2-3): Katharina Gabrysiak, Tobias Gustmann, Jens Freudenberger, Kai Neufeld, Lars Giebeler, Christoph Leyens, and Uta Kühn. Development and characterization of a metastable al-mn-ce alloy produced by laser powder bed fusion. Additive Manufacturing Letters, Oct 2021. URL: https://doi.org/10.1016/j.addlet.2021.100017, doi:10.1016/j.addlet.2021.100017. This article has 13 citations and is from a peer-reviewed journal.

3. (goncharov2026designofcobaltfree pages 2-4): Ivan Goncharov, Vera Popovich, Marcel Sluiter, Anatoly Popovich, and Maurizio Vedani. Design of cobalt-free high-entropy alloy binder for wc-base cemented carbides. Metals, 16:318, Mar 2026. URL: https://doi.org/10.3390/met16030318, doi:10.3390/met16030318. This article has 1 citations.

4. (goncharov2026designofcobaltfree pages 8-10): Ivan Goncharov, Vera Popovich, Marcel Sluiter, Anatoly Popovich, and Maurizio Vedani. Design of cobalt-free high-entropy alloy binder for wc-base cemented carbides. Metals, 16:318, Mar 2026. URL: https://doi.org/10.3390/met16030318, doi:10.3390/met16030318. This article has 1 citations.

5. (anne2023laserpowderbedfusion pages 31-35): Laser Powder-Bed Fusion of Elemental Powder Blends to Manufacture Precipitation and Oxide-dispersion Strengthened Aluminum Alloys This article has 0 citations and is from a peer-reviewed journal.

6. (spierings2018powderspreadabilityand pages 133-137): AB Spierings. Powder spreadability and characterization of sc- and zr-modified aluminium alloys processed by selective laser melting: quality management system for additive manufacturing. Unknown journal, 2018. URL: https://doi.org/10.3929/ethz-b-000253924, doi:10.3929/ethz-b-000253924. This article has 32 citations.

7. (cerri2024mainheattreatments pages 2-5): Emanuela Cerri, Lorenzo Curti, and Emanuele Ghio. Main heat treatments currently applied on laser powder bed-fused scalmalloy®: a review. Crystals, 15:25, Dec 2024. URL: https://doi.org/10.3390/cryst15010025, doi:10.3390/cryst15010025. This article has 13 citations.

8. (fedina2022influenceofalsi10mg pages 5-6): Tatiana Fedina, Filippo Belelli, Giorgia Lupi, Benedikt Brandau, Riccardo Casati, Raphael Berneth, Frank Brueckner, and Alexander F.H. Kaplan. Influence of alsi10mg powder aging on the material degradation and its processing in laser powder bed fusion. Nov 2022. URL: https://doi.org/10.1016/j.powtec.2022.118024, doi:10.1016/j.powtec.2022.118024. This article has 26 citations and is from a domain leading peer-reviewed journal.

9. (anne2023laserpowderbedfusion pages 27-31): Laser Powder-Bed Fusion of Elemental Powder Blends to Manufacture Precipitation and Oxide-dispersion Strengthened Aluminum Alloys This article has 0 citations and is from a peer-reviewed journal.

10. (taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 7-9): S. Mohadeseh Taheri‐Mousavi, Michael Xu, Florian Hengsbach, Clay Houser, Zhaoxuan Ge, Benjamin Glaser, Shaolou Wei, Mirko Schaper, James M. LeBeau, Greg B. Olson, and A. John Hart. Additively manufacturable high‐strength aluminum alloys with coarsening‐resistant microstructures achieved via rapid solidification. Advanced Materials, Oct 2026. URL: https://doi.org/10.1002/adma.202509507, doi:10.1002/adma.202509507. This article has 13 citations and is from a highest quality peer-reviewed journal.

11. (zhao2021somefactorsaffecting pages 2-3): Tong Zhao, Yuhan Wang, Tianshan Xu, Maha Bakir, Wangcan Cai, Mengjie Wang, Marius Dahmen, Qihong Zheng, Xianke Wei, Chen Hong, Chongliang Zhong, Patrick Albus, Thomas Schopphoven, Andres Gasser, and Constantin Leon Häfner. Some factors affecting porosity in directed energy deposition of almgsczr-alloys. Optics and Laser Technology, 143:107337, Nov 2021. URL: https://doi.org/10.1016/j.optlastec.2021.107337, doi:10.1016/j.optlastec.2021.107337. This article has 75 citations and is from a peer-reviewed journal.

12. (zhao2021somefactorsaffecting pages 1-2): Tong Zhao, Yuhan Wang, Tianshan Xu, Maha Bakir, Wangcan Cai, Mengjie Wang, Marius Dahmen, Qihong Zheng, Xianke Wei, Chen Hong, Chongliang Zhong, Patrick Albus, Thomas Schopphoven, Andres Gasser, and Constantin Leon Häfner. Some factors affecting porosity in directed energy deposition of almgsczr-alloys. Optics and Laser Technology, 143:107337, Nov 2021. URL: https://doi.org/10.1016/j.optlastec.2021.107337, doi:10.1016/j.optlastec.2021.107337. This article has 75 citations and is from a peer-reviewed journal.

13. (goncharov2026designofcobaltfree pages 10-13): Ivan Goncharov, Vera Popovich, Marcel Sluiter, Anatoly Popovich, and Maurizio Vedani. Design of cobalt-free high-entropy alloy binder for wc-base cemented carbides. Metals, 16:318, Mar 2026. URL: https://doi.org/10.3390/met16030318, doi:10.3390/met16030318. This article has 1 citations.

14. (anne2023laserpowderbedfusion pages 45-49): Laser Powder-Bed Fusion of Elemental Powder Blends to Manufacture Precipitation and Oxide-dispersion Strengthened Aluminum Alloys This article has 0 citations and is from a peer-reviewed journal.

15. (taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 18-22): S. Mohadeseh Taheri‐Mousavi, Michael Xu, Florian Hengsbach, Clay Houser, Zhaoxuan Ge, Benjamin Glaser, Shaolou Wei, Mirko Schaper, James M. LeBeau, Greg B. Olson, and A. John Hart. Additively manufacturable high‐strength aluminum alloys with coarsening‐resistant microstructures achieved via rapid solidification. Advanced Materials, Oct 2026. URL: https://doi.org/10.1002/adma.202509507, doi:10.1002/adma.202509507. This article has 13 citations and is from a highest quality peer-reviewed journal.

16. (taheri‐mousavi2026additivelymanufacturablehigh‐strength pages 15-18): S. Mohadeseh Taheri‐Mousavi, Michael Xu, Florian Hengsbach, Clay Houser, Zhaoxuan Ge, Benjamin Glaser, Shaolou Wei, Mirko Schaper, James M. LeBeau, Greg B. Olson, and A. John Hart. Additively manufacturable high‐strength aluminum alloys with coarsening‐resistant microstructures achieved via rapid solidification. Advanced Materials, Oct 2026. URL: https://doi.org/10.1002/adma.202509507, doi:10.1002/adma.202509507. This article has 13 citations and is from a highest quality peer-reviewed journal.

17. (yakubov2024recycledaluminiumfeedstock pages 7-9): Vladislav Yakubov, Halsey Ostergaard, Shishira Bhagavath, Chu Lun Alex Leung, James Hughes, Evren Yasa, Mani Khezri, Sandra K. Löschke, Qing Li, and Anna Paradowska. Recycled aluminium feedstock in metal additive manufacturing: a state of the art review. Heliyon, Mar 2024. URL: https://doi.org/10.1016/j.heliyon.2024.e27243, doi:10.1016/j.heliyon.2024.e27243. This article has 39 citations.

18. (fedina2022influenceofalsi10mg pages 1-2): Tatiana Fedina, Filippo Belelli, Giorgia Lupi, Benedikt Brandau, Riccardo Casati, Raphael Berneth, Frank Brueckner, and Alexander F.H. Kaplan. Influence of alsi10mg powder aging on the material degradation and its processing in laser powder bed fusion. Nov 2022. URL: https://doi.org/10.1016/j.powtec.2022.118024, doi:10.1016/j.powtec.2022.118024. This article has 26 citations and is from a domain leading peer-reviewed journal.

19. (kramer2025impactofdifferent pages 1-2): Steffen Kramer, Helena Wexel, Anisa Purwitasari, M. Jarwitz, V. Schulze, and F. Zanger. Impact of different pore types on the tensile and fatigue properties of alsi10mg parts produced by laser powder bed fusion. Progress in Additive Manufacturing, Aug 2025. URL: https://doi.org/10.1007/s40964-025-01288-x, doi:10.1007/s40964-025-01288-x. This article has 11 citations and is from a peer-reviewed journal.

20. (zhao2021somefactorsaffecting pages 3-5): Tong Zhao, Yuhan Wang, Tianshan Xu, Maha Bakir, Wangcan Cai, Mengjie Wang, Marius Dahmen, Qihong Zheng, Xianke Wei, Chen Hong, Chongliang Zhong, Patrick Albus, Thomas Schopphoven, Andres Gasser, and Constantin Leon Häfner. Some factors affecting porosity in directed energy deposition of almgsczr-alloys. Optics and Laser Technology, 143:107337, Nov 2021. URL: https://doi.org/10.1016/j.optlastec.2021.107337, doi:10.1016/j.optlastec.2021.107337. This article has 75 citations and is from a peer-reviewed journal.

21. (anderson2018feedstockpowderprocessing pages 2-3): Iver E. Anderson, Emma M.H. White, and Ryan Dehoff. Feedstock powder processing research needs for additive manufacturing development. Current Opinion in Solid State & Materials Science, 22:8-15, Feb 2018. URL: https://doi.org/10.1016/j.cossms.2018.01.002, doi:10.1016/j.cossms.2018.01.002. This article has 377 citations and is from a domain leading peer-reviewed journal.

22. (anderson2018feedstockpowderprocessing pages 4-5): Iver E. Anderson, Emma M.H. White, and Ryan Dehoff. Feedstock powder processing research needs for additive manufacturing development. Current Opinion in Solid State & Materials Science, 22:8-15, Feb 2018. URL: https://doi.org/10.1016/j.cossms.2018.01.002, doi:10.1016/j.cossms.2018.01.002. This article has 377 citations and is from a domain leading peer-reviewed journal.

23. (anderson2018feedstockpowderprocessing pages 3-4): Iver E. Anderson, Emma M.H. White, and Ryan Dehoff. Feedstock powder processing research needs for additive manufacturing development. Current Opinion in Solid State & Materials Science, 22:8-15, Feb 2018. URL: https://doi.org/10.1016/j.cossms.2018.01.002, doi:10.1016/j.cossms.2018.01.002. This article has 377 citations and is from a domain leading peer-reviewed journal.

24. (yadegari2025aluminumlaseradditive pages 8-9): Mohammad Javad Yadegari, Alessandra Martucci, Sara Biamino, Daniele Ugues, Laura Montanaro, Paolo Fino, and Mariangela Lombardi. Aluminum laser additive manufacturing: a review on challenges and opportunities through the lens of sustainability. Applied Sciences, 15:2221, Feb 2025. URL: https://doi.org/10.3390/app15042221, doi:10.3390/app15042221. This article has 17 citations.

25. (yakubov2024recycledaluminiumfeedstock pages 6-7): Vladislav Yakubov, Halsey Ostergaard, Shishira Bhagavath, Chu Lun Alex Leung, James Hughes, Evren Yasa, Mani Khezri, Sandra K. Löschke, Qing Li, and Anna Paradowska. Recycled aluminium feedstock in metal additive manufacturing: a state of the art review. Heliyon, Mar 2024. URL: https://doi.org/10.1016/j.heliyon.2024.e27243, doi:10.1016/j.heliyon.2024.e27243. This article has 39 citations.

26. (anne2023laserpowderbedfusion pages 35-39): Laser Powder-Bed Fusion of Elemental Powder Blends to Manufacture Precipitation and Oxide-dispersion Strengthened Aluminum Alloys This article has 0 citations and is from a peer-reviewed journal.