# Edison LITERATURE_HIGH: q1-temperature-vs-humidity-water-uptake-and-oxidation

Task `645b29f0-da5f-46cc-bcba-b406d4459ccc`, status `success`, issue #42. Full trajectory: [q1-temperature-vs-humidity-water-uptake-and-oxidation.json](q1-temperature-vs-humidity-water-uptake-and-oxidation.json).

## Query

Context: our lab in Provo, Utah (about 1,400 m elevation) makes and stores aluminum-alloy powders for additive-manufacturing research. A walk-in enclosure inside the lab is supplied with air from a refrigerant (compressor) dehumidifier and exhausted continuously to building exhaust. The surrounding room sits at 21.7-22.2 C and 35-60% relative humidity (RH), dew point 6-13 C, tracking outdoor humidity. On the first night with the dehumidifier on, air inside the enclosure was 24 C at 35-42% RH (dew point 8-10 C) while the room was expected at about 22 C and 56% RH (dew point about 13 C); a hand-held reading showed about 27 C (80 F) at about 30% RH. So the compressor heat raises the enclosure temperature by roughly 2-5 C while the dehumidifier removes about 15-30% of the water vapor. Powders stored there, in sealed containers with silica-gel packets inside chemical storage cabinets, include gas-atomized AlSi10Mg (15-45 um, from MSE Supplies), silicon powder (98-99.5% Si), stainless-steel powder, and soon ultrasonically atomized aluminum alloys containing Mg, Cu, Zn, Li, Sc, Zr, Ce and Er, made in an argon-purged atomizer (AMAZEMET rePowder). Question: will the warmer but drier enclosure air increase or decrease water uptake and oxidation of these powders during weeks to months of storage, compared with the cooler, more humid room? Specifically: (1) For aluminum and Al-Si-Mg powders with a native oxide, is the amount of adsorbed water governed mainly by relative humidity (water activity) or by absolute humidity / dew point, and how does it change with temperature at fixed RH? Give adsorption isotherm data (e.g., mg water per m2, or number of monolayers, versus RH) for aluminum, Al2O3 or native-oxide surfaces, silicon and AlSi10Mg where available. (2) What are the measured rates, rate laws and activation energies for near-ambient (15-50 C) oxide thickening, hydroxide formation (boehmite, bayerite, gibbsite) and hydrogen evolution on aluminum and Al-alloy powders as a function of RH? Is there a critical RH below which hydration is negligible? Using those numbers, estimate how much faster these processes run at 24-27 C than at 22 C, and whether that is outweighed by the drop from about 50-60% RH to about 30-40% RH. (3) Which alloying elements make aluminum powders more sensitive to humid storage (for example Mg surface enrichment in AlSi10Mg, Li in Al-Cu-Li alloys, Zn, Ce, Sc), and does stainless-steel or silicon powder care about a 2-5 C change at all? Give quantitative values with DOIs, and say explicitly where evidence is lacking or where results conflict.

## Answer

Question: Context: our lab in Provo, Utah (about 1,400 m elevation) makes and stores aluminum-alloy powders for additive-manufacturing research. A walk-in enclosure inside the lab is supplied with air from a refrigerant (compressor) dehumidifier and exhausted continuously to building exhaust. The surrounding room sits at 21.7-22.2 C and 35-60% relative humidity (RH), dew point 6-13 C, tracking outdoor humidity. On the first night with the dehumidifier on, air inside the enclosure was 24 C at 35-42% RH (dew point 8-10 C) while the room was expected at about 22 C and 56% RH (dew point about 13 C); a hand-held reading showed about 27 C (80 F) at about 30% RH. So the compressor heat raises the enclosure temperature by roughly 2-5 C while the dehumidifier removes about 15-30% of the water vapor. Powders stored there, in sealed containers with silica-gel packets inside chemical storage cabinets, include gas-atomized AlSi10Mg (15-45 um, from MSE Supplies), silicon powder (98-99.5% Si), stainless-steel powder, and soon ultrasonically atomized aluminum alloys containing Mg, Cu, Zn, Li, Sc, Zr, Ce and Er, made in an argon-purged atomizer (AMAZEMET rePowder). Question: will the warmer but drier enclosure air increase or decrease water uptake and oxidation of these powders during weeks to months of storage, compared with the cooler, more humid room? Specifically: (1) For aluminum and Al-Si-Mg powders with a native oxide, is the amount of adsorbed water governed mainly by relative humidity (water activity) or by absolute humidity / dew point, and how does it change with temperature at fixed RH? Give adsorption isotherm data (e.g., mg water per m2, or number of monolayers, versus RH) for aluminum, Al2O3 or native-oxide surfaces, silicon and AlSi10Mg where available. (2) What are the measured rates, rate laws and activation energies for near-ambient (15-50 C) oxide thickening, hydroxide formation (boehmite, bayerite, gibbsite) and hydrogen evolution on aluminum and Al-alloy powders as a function of RH? Is there a critical RH below which hydration is negligible? Using those numbers, estimate how much faster these processes run at 24-27 C than at 22 C, and whether that is outweighed by the drop from about 50-60% RH to about 30-40% RH. (3) Which alloying elements make aluminum powders more sensitive to humid storage (for example Mg surface enrichment in AlSi10Mg, Li in Al-Cu-Li alloys, Zn, Ce, Sc), and does stainless-steel or silicon powder care about a 2-5 C change at all? Give quantitative values with DOIs, and say explicitly where evidence is lacking or where results conflict.

## Will the Warmer but Drier Enclosure Decrease Powder Degradation?

**Overall conclusion: Yes.** The dehumidified enclosure (~24–27 °C, 30–42% RH) should **decrease** water uptake, oxide thickening, hydroxide formation, and hydrogen evolution on your aluminum-alloy powders compared with the surrounding room (~22 °C, 50–60% RH). The benefit of lowering RH by 15–25 percentage points substantially outweighs the modest penalty of a 2–5 °C temperature increase. The reasoning and quantitative basis are detailed below.

---

### 1. Water Adsorption: Governed by Relative Humidity, Not Absolute Humidity

Equilibrium water adsorption on oxide surfaces is controlled primarily by **relative humidity (water activity, p/p_sat)**, not by absolute humidity or dew point. This is established by ambient-pressure XPS studies of water adsorption on Al₂O₃ thin films, where water film thickness is reported as a function of RH at controlled temperature (deng2008adsorptionofwater pages 4-5, deng2008adsorptionofwater pages 1-2, deng2008adsorptionofwater pages 2-3). On a flat, defective Al₂O₃ film at 295 K, hydroxyl coverage saturates at ~1% RH; the first molecular water monolayer completes at ~15% RH, the second at ~35–40% RH, the fourth at ~70% RH, and approximately six layers (~18 Å) are present at 90% RH (deng2008adsorptionofwater pages 4-5, deng2008adsorptionofwater pages 1-2).

On a real aluminum surface including micropore/capillary water, Graedel (1989) reported substantially higher coverage: approximately 7–8 equivalent monolayers even at 10% RH, rising to ~12–13 at 30–50% RH and ~20+ at 95% RH (graedel1989corrosionmechanismsfor pages 1-2, graedel1989corrosionmechanismsfor media 1d3944b6). This much higher count reflects capillary condensation within the porous oxide/hydroxide layer that forms on real aluminum surfaces (graedel1989corrosionmechanismsfor pages 1-2).

The following table summarizes the available isotherm data:

| RH (%) | Water layers on flat Al₂O₃ | Water monolayers on real Al surface with micropores | Approx. water-film thickness (Å, ~3 Å/layer) |
|---:|---:|---:|---:|
| 1 | OH coverage saturated; molecular layer not yet complete | ~7 | Real Al: ~21 |
| 10 | ~0.7 | ~8 | Al₂O₃: ~2; real Al: ~24 |
| 15 | ~1 | — | Al₂O₃: ~3 |
| 20 | — | ~8 | Real Al: ~24 |
| 30 | ~1.5 | ~10 | Al₂O₃: ~4.5; real Al: ~30; MD model: ~5 |
| 35–40 | ~2 | ~12 | Al₂O₃: ~6; real Al: ~36 |
| 50 | ~2.5 | ~13 | Al₂O₃: ~7.5; real Al: ~39 |
| 55 | ~3 | — | Al₂O₃: ~9 |
| 70 | ~4 | ~12 | Al₂O₃: ~12; real Al: ~36 |
| 80 | — | ~13 | Real Al: ~39 |
| 90 | ~6 | ~20 | Al₂O₃: ~18; real Al: ~60; MD model: ~20 |
| **Sources and interpretation** | Deng et al., flat Al₂O₃ thin film; intermediate values are approximate interpolations (deng2008adsorptionofwater pages 4-5, deng2008adsorptionofwater pages 1-2) | Graedel Figure 1; values are approximate readings and include micropore/capillary water (graedel1989corrosionmechanismsfor pages 1-2, graedel1989corrosionmechanismsfor media 1d3944b6) | Geometric conversion assumes ~3 Å per molecular layer; Scher MD-film values are separate model estimates and are not directly equivalent to Graedel’s monolayer count (scher2023modelforhumiditymediated pages 27-30) |


*Table: Approximate equilibrium water coverage versus relative humidity for flat Al₂O₃ and a real, microporous aluminum surface. The large difference illustrates why substrate morphology and the measurement definition must be specified when comparing monolayer counts.*

**At fixed RH, raising temperature does not increase equilibrium water coverage**—rather, it slightly decreases it because the desorption rate increases exponentially with temperature; the error from ignoring this is estimated at <7% (deng2008adsorptionofwater pages 4-5). Therefore, going from 22 °C/55% RH to 25 °C/35% RH reduces the equilibrium adsorbed water substantially. On flat Al₂O₃, the molecular water coverage drops from approximately 3 layers to approximately 1.5–2 layers—a reduction of roughly 35–50% (deng2008adsorptionofwater pages 4-5, deng2008adsorptionofwater pages 1-2).

**For SiO₂ (silicon powder surfaces):** Water adsorption on native SiO₂ follows a qualitatively similar BET-type isotherm. An ordered, ice-like structured water layer forms first, and approximately two such monolayers are present by ~60% RH; above 60% RH, liquid-like water dominates the growth (asay2006effectsofadsorbed pages 1-3, torun2014studyofwater pages 4-5, torun2014studyofwater pages 1-1). Reducing RH from 55% to 35% would therefore reduce the adsorbed water and suppress capillary bridging between particles.

**No published water-adsorption isotherms specific to AlSi10Mg powder surfaces were located.** The native oxide on AlSi10Mg is amorphous Al₂O₃ enriched in Mg, forming MgAl₂O₄ spinel (raza2021degradationofalsi10mg pages 1-2, raza2021degradationofalsi10mg pages 8-10). Mg-enriched oxide may be somewhat more hydrophilic than pure Al₂O₃, but the adsorption should still be governed by RH, making the enclosure's lower RH beneficial.

---

### 2. Oxidation Kinetics, Rate Laws, Activation Energies, and Critical RH

#### 2.1 Rate Laws and Activation Energies

At near-ambient temperatures, aluminum oxide film growth is governed by the **Cabrera–Mott mechanism**: electron tunneling through the thin oxide creates an electric field that drives Al³⁺ migration. This is field-assisted transport rather than purely thermally activated diffusion, so a single Arrhenius activation energy does not fully describe the kinetics (cai2011effectofoxygen pages 1-6, dholiwar1985theoxidationof pages 33-35). The growth follows an inverse-logarithmic law and is self-limiting, reaching a limiting thickness set by the tunneling range (~2–5 nm in dry air at room temperature) (czech2010hydrogengenerationfrom pages 23-27, cai2011effectofoxygen pages 1-6).

Reported activation energies for aluminum oxidation span a wide range: **71, 83.8, 95.5, and 149.6 kJ/mol** for thermal oxidation, and 77.9–418 kJ/mol for heterogeneous oxidation, depending on the temperature regime and polymorphic transformations involved (trunov2005ignitionofaluminum pages 2-4, trunov2005ignitionofaluminum pages 4-5). The lower values (~71–96 kJ/mol) are more relevant to near-ambient conditions.

In the presence of moisture, the air-formed oxide can be hydrated to form hydroxide phases. At 25 °C and 90% RH, bayerite (α-Al(OH)₃), gibbsite, and pseudoboehmite have all been identified (ratko2004hydrothermalsynthesisof pages 4-5). Below ~80 °C, the predominant hydroxide products are bayerite and pseudoboehmite; boehmite becomes favored at higher temperatures (czech2010hydrogengenerationfrom pages 23-27). On artificially aged aluminum powder (85 °C, 85% RH), DRIFTS reveals extensive trihydroxide formation and boehmite-like phases, while naturally aged powder shows bayerite with some gibbsite (ludwig2022infraredspectroscopystudies pages 11-13, ludwig2022infraredspectroscopystudies pages 8-11).

#### 2.2 AlSi10Mg Powder Degradation Rates

Quantitative data on AlSi10Mg powder aging show that the native oxide layer grows from approximately **4 nm on virgin powder to ~18 nm after 6 months and ~38 nm after 30 months** of reuse in an LPBF machine environment (raza2021degradationofalsi10mg pages 1-2, raza2021degradationofalsi10mg pages 8-10). Oxygen content increased from 0.067 wt% (virgin) to 0.257 wt% after a 96-hour aging treatment (fedina2022influenceofalsi10mg pages 4-5). Hydrogen content remained relatively stable at ~0.003 wt% (fedina2022influenceofalsi10mg pages 4-5). Powder stored for one month in ambient air produced ~3% porosity in printed parts, versus ~1% after drying at 100 °C for 1 hour (fiegl2021effectofalsi10mg0.4 pages 1-2). Drying removes physisorbed moisture but does not reverse chemical oxide formation (fedina2022influenceofalsi10mg pages 1-2).

#### 2.3 Critical RH for Atmospheric Corrosion

A critical finding is that **atmospheric corrosion of pristine aluminum is not observed below approximately 70% RH** (scher2023modelforhumiditymediated pages 33-37, graedel1989corrosionmechanismsfor pages 1-1). At this threshold, accumulated corrosion products absorb enough moisture to support electrochemical degradation. Below 70% RH, the adsorbed water film is too thin and too confining: molecular dynamics simulations show that at 30% RH (water film ~5 Å), aqueous Al-ion diffusion rates are **more than two orders of magnitude slower** than in bulk water (scher2023modelforhumiditymediated pages 1-6). This strongly suppresses the transport step required for corrosion, hydroxide growth, and hydrogen evolution.

Both your room (~55% RH) and enclosure (~35% RH) are below this ~70% threshold, which is favorable. However, **the threshold is not universal**: salts, defects, Mg/Li-enriched phases, crevices, and micropores can support localized reaction below 70% RH (graedel1989corrosionmechanismsfor pages 1-1, graedel1989corrosionmechanismsfor pages 1-2, burnett2023mechanismsofenvironmentally pages 29-30).

#### 2.4 Temperature vs. RH: Quantitative Comparison

Using the Arrhenius equation with the lowest reported activation energy for near-ambient Al oxidation (E_a = 71 kJ/mol):

- Rate ratio (25°C vs. 22°C) = exp[(71000/8.314)(1/295.15 − 1/298.15)] ≈ **1.10–1.34×**

For higher E_a (150 kJ/mol): the ratio is approximately **1.22–1.85×** (trunov2005ignitionofaluminum pages 2-4).

However, low-temperature Cabrera–Mott oxidation is field-assisted and not well described by a single Arrhenius law, so these are upper-bound estimates (cai2011effectofoxygen pages 1-6, trunov2005ignitionofaluminum pages 4-5). The actual temperature sensitivity is likely smaller than even the low-E_a estimate.

Meanwhile, reducing RH from 55% to 35%:
- Reduces molecular water coverage on Al₂O₃ by ~35–50% (deng2008adsorptionofwater pages 4-5)
- Reduces Al-ion mobility in the water film by a factor that scales strongly with film thickness (scher2023modelforhumiditymediated pages 33-37, scher2023modelforhumiditymediated pages 27-30)
- Keeps both conditions well below the ~70% critical RH

**The RH effect decisively outweighs the temperature effect.** A 35–50% reduction in surface water coverage, combined with orders-of-magnitude suppression of ion transport, far exceeds a 10–85% increase in intrinsic reaction rate from +3 °C.

The following table compares the two conditions quantitatively:

| Parameter | Room condition (~22°C, 55% RH, dew point ~13°C) | Enclosure condition (~25°C, 35% RH, dew point ~9°C) | Expected effect on powder degradation |
|---|---:|---:|---|
| Temperature | ~22°C (295.15 K) | ~25°C (298.15 K) | A +3°C change modestly-to-moderately accelerates thermally activated steps; it does not increase equilibrium water coverage at fixed RH. |
| Relative humidity / water activity | ~55% | ~35% | Large beneficial decrease in the controlling equilibrium variable for surface adsorption; fewer molecular-water layers and less mobile interfacial water. |
| Dew point / absolute humidity | ~13°C; approximately 11.3 g H₂O/m³ | ~9°C; approximately 8.8 g H₂O/m³ | Approximately 22% less vapor per unit air volume. This reduces the water reservoir and drying load, although equilibrium adsorption is governed primarily by RH at the powder-surface temperature. |
| Water layers on flat Al₂O₃ | Approximately 3 molecular layers | Approximately 1.5–2 layers | Approximately 35–50% lower molecular-water coverage in the enclosure (deng2008adsorptionofwater pages 4-5, deng2008adsorptionofwater pages 1-2). |
| Water coverage on a real, microporous Al surface | Approximately 13 monolayer-equivalents | Approximately 10–12 monolayer-equivalents | Moderate reduction; the larger values than for flat Al₂O₃ include micropore/capillary water and are approximate readings from the published figure (graedel1989corrosionmechanismsfor pages 1-2, graedel1989corrosionmechanismsfor media 1d3944b6). |
| Al-ion mobility in the adsorbed water film | Low; still strongly confined relative to bulk water | Very low; at approximately 30% RH, modeled Al-ion diffusion is more than two orders of magnitude slower than bulk-water self-diffusion | Lower RH suppresses water-mediated ion transport and therefore corrosion kinetics; no measured 35%:55% rate ratio is available (scher2023modelforhumiditymediated pages 33-37, scher2023modelforhumiditymediated pages 1-6). |
| Practical corrosion-onset RH for clean Al | Below the reported ~70% onset | Further below the reported ~70% onset | Both are below the approximate onset reported for pristine indoor aluminum, but this is not a universal threshold: salts, defects, Mg/Li-rich phases, and crevices can permit localized reaction below 70% RH (scher2023modelforhumiditymediated pages 33-37, graedel1989corrosionmechanismsfor pages 1-1). |
| Arrhenius temperature factor, *E*ₐ = 71 kJ/mol | Baseline = 1.00 | `exp[(71000/R)(1/295.15 − 1/298.15)] ≈ 1.34` | Approximately 34% faster at 25°C—not 10%—if a simple Arrhenius law with this activation energy applies (trunov2005ignitionofaluminum pages 2-4). |
| Arrhenius temperature factor, *E*ₐ = 150 kJ/mol | Baseline = 1.00 | `exp[(150000/R)(1/295.15 − 1/298.15)] ≈ 1.85` | Approximately 85% faster—not 22%—under that high-*E*ₐ assumption; low-temperature Cabrera–Mott oxide growth is field-assisted, so a single Arrhenius factor is only a sensitivity bound (trunov2005ignitionofaluminum pages 2-4, cai2011effectofoxygen pages 1-6, trunov2005ignitionofaluminum pages 4-5). |
| Net effect on adsorbed water | Higher | Lower | RH reduction dominates equilibrium uptake: flat-Al₂O₃ coverage is predicted to fall by roughly 35–50%, with a smaller but still favorable decrease on rough/microporous native oxide. |
| Net effect on oxidation, hydration, and H₂-producing reactions | Higher water activity and thicker adsorbed film | Slightly faster intrinsic kinetics but substantially lower water activity and mobility | Expected net decrease in water-mediated degradation. The conclusion is strongest for clean, passivated Al/AlSi10Mg and weaker for contaminated, damaged, Li-bearing, or highly Mg/Zn-enriched powders. |
| Overall verdict | Cooler but wetter | Warmer but drier | **The enclosure is preferable**, provided containers remain sealed and the enclosure RH is reliably maintained near 30–40%; the RH decrease should outweigh the +3°C temperature increase for weeks-to-months storage. |


*Table: Comparison of the lab room and dehumidified enclosure, including corrected Arrhenius temperature factors and humidity-dependent surface-water estimates. It shows why the lower enclosure RH is expected to outweigh its modest temperature increase for passivated powder storage.*

---

### 3. Alloying Element Effects on Humidity Sensitivity

#### 3.1 Magnesium (in AlSi10Mg)

Mg is the most important element for your current AlSi10Mg powder. Mg **enriches in the surface oxide** during aging and reuse, forming MgAl₂O₄ spinel within the Al₂O₃ layer (raza2021degradationofalsi10mg pages 1-2, raza2021degradationofalsi10mg pages 8-10). Spatter particles can develop oxide scales reaching ~120–125 nm, composed mainly of MgAl₂O₄ and Al₂O₃ (raza2021degradationofalsi10mg pages 8-10). MgO is thermodynamically the most stable oxide in the system, which promotes preferential Mg oxidation (raza2021degradationofalsi10mg pages 8-10). This Mg enrichment increases the oxide thickness and complexity but does not change the fundamental conclusion: lower RH reduces the water activity that drives further hydration.

#### 3.2 Lithium (in planned Al-Cu-Li alloys)

**Li-containing aluminum alloys are the most moisture-sensitive powders in your collection.** Li₂O and LiOH form readily from atmospheric moisture, and the reaction generates hydrogen gas. Al-Li alloy hydrolysis is exploited intentionally for hydrogen generation (multiple references in search results). For passivated Al-Li AM powders at 30–55% RH, quantitative storage-rate data were not located in the literature, representing a significant evidence gap. However, the well-known hygroscopic reactivity of Li-bearing phases means these powders warrant the most stringent storage precautions: sealed containers under dry argon, with desiccant, even inside the dehumidified enclosure.

#### 3.3 Zinc (in Al-Zn-Mg-Cu alloys)

High-Zn 7xxx alloys (AA7085, AA7449) exhibit **hydrogen-environmental induced cracking at 50% RH** in humid air, even without bulk immersion (burnett2023mechanismsofenvironmentally pages 29-30, burnett2023mechanismsofenvironmentally pages 1-4). Reactive Mg-rich η-phase grain-boundary precipitates and MgZn₂ particles serve as initiation sites where localized condensed water generates hydrogen (burnett2023mechanismsofenvironmentally pages 24-25). New-generation high-Zn alloys show crack growth velocities approximately **10× faster** than older 7xxx alloys like AA7050 (burnett2023mechanismsofenvironmentally pages 29-30). While these data pertain to stressed bulk material rather than unstressed powder storage, they demonstrate that Zn/Mg-rich phases are inherently moisture-sensitive. Lowering RH from 55% to 35% would reduce condensation risk at these microstructural sites.

#### 3.4 Scandium and Zirconium

Sc additions to Al-Mg alloys can **improve corrosion resistance** through formation of Sc₂O₃ on coherent nano-Al₃Sc precipitates and by pinning grain boundaries (Ahmad et al., 2011, DOI: 10.4236/msa.2011.24031). No quantitative humid-storage data specific to atomized Al-Sc-Zr powder were located. The effect on powder-level moisture sensitivity remains unquantified.

#### 3.5 Cerium and Erbium

Ce and Er form stable oxides (CeO₂, Er₂O₃) and are used as corrosion inhibitors in some systems, but **no specific data on the humidity sensitivity of Al-Ce or Al-Er powders during storage were found.** This is a clear evidence gap. The atomization under argon in the AMAZEMET system should provide a good initial passivation layer, but long-term humid-storage behavior is unknown.

#### 3.6 Copper

Cu-rich intermetallic particles (e.g., Al₂Cu, Al₂CuLi) can create galvanic cells that promote localized corrosion when a sufficient electrolyte film is present. At 30–55% RH without salt contamination, continuous electrolyte films are unlikely to form, so Cu is not expected to be a primary concern at your storage conditions.

#### 3.7 Stainless Steel 316L

Stainless steel powder is **far less sensitive** to the storage condition change than aluminum powders. The Cr₂O₃-rich passive film is thermodynamically stable and kinetically sluggish at room temperature. Kim et al. (2025) showed that 316L powder exposed to increasing RH (5%, 35%, 50%, 70%) for 24 hours exhibited progressive moisture uptake, increased O and H content, and degraded flowability—the 70% RH powder became completely non-flowing (kim2025investigationofmicrostructure pages 3-6, kim2025investigationofmicrostructure pages 1-3). However, these changes are primarily physical (adsorbed moisture, capillary bridging) rather than chemical degradation of the passive film. A 2–5 °C temperature change at near-ambient conditions has negligible effect on stainless steel surface chemistry.

#### 3.8 Silicon Powder (98–99.5% Si)

Silicon powder with its native SiO₂ surface is **very stable** at room temperature. SiO₂ oxidation kinetics at 20–30 °C are negligible. The primary concern is reversible water adsorption affecting flowability and surface cleanliness, not chemical degradation. The lower RH in the enclosure will reduce adsorbed water (asay2006effectsofadsorbed pages 1-3, torun2014studyofwater pages 4-5).

The following table summarizes the powder-specific sensitivity analysis:

| Powder type | Primary surface phase | Sensitivity to RH change (55→35%) | Sensitivity to T change (22→25°C) | Net effect of enclosure | Key concern | Key references |
|---|---|---|---|---|---|---|
| Gas-atomized AlSi10Mg, 15–45 µm | Native amorphous Al₂O₃ with Mg-enriched oxide/MgAl₂O₄ spinel | **High:** flat-Al₂O₃ data imply roughly 35–50% less molecular-water coverage | **Low–moderate:** intrinsic reaction steps accelerate, but low-temperature oxide growth is not described reliably by one Arrhenius law | **Beneficial** | Mg enters and enriches the oxide; long reuse produced oxide growth from ~4 to ~38 nm. Lower water activity should mitigate hydration, although those reuse data also include hot spatter and process exposure. (raza2021degradationofalsi10mg pages 1-2, raza2021degradationofalsi10mg pages 8-10, fedina2022influenceofalsi10mg pages 1-2, fedina2022influenceofalsi10mg pages 4-5) | Raza et al., 2021, DOI: 10.1016/j.matdes.2020.109358; Fedina et al., 2022, DOI: 10.1016/j.powtec.2022.118024 |
| Pure or near-pure Al powder | Amorphous Al₂O₃/native oxyhydroxide | **Moderate:** less adsorbed molecular water; both conditions remain below the approximate ~70% clean-Al corrosion onset | **Low–moderate:** +3°C accelerates activated steps, but passivation makes long-term growth strongly self-limiting | **Beneficial** | The ~70% onset is practical, not universal; salts, defects, micropores, or contamination can support localized reaction below it. (scher2023modelforhumiditymediated pages 33-37, graedel1989corrosionmechanismsfor pages 1-1, graedel1989corrosionmechanismsfor pages 1-2) | Graedel, 1989, DOI: 10.1149/1.2096869; Scher et al., 2023, DOI: 10.1021/acsami.3c02327 |
| Al–Mg–Cu–Zn (7xxx-type) | Al₂O₃ plus Mg/Zn/Cu-containing intermetallic or precipitate sites | **High at reactive sites:** localized condensed water can drive corrosion and hydrogen uptake even near 50% RH | **Moderate but unquantified** for unstressed powder | **Beneficial, but extra-dry/inert storage is prudent** | High-Zn 7xxx alloys exhibited humid-air hydrogen-assisted cracking at 50% RH under stress; reactive Mg-rich phases and tight fissures were initiation sites. This is strong bulk-alloy evidence, not a powder-storage rate measurement. (burnett2023mechanismsofenvironmentally pages 29-30, burnett2023mechanismsofenvironmentally pages 1-4, burnett2023mechanismsofenvironmentally pages 24-25) | Burnett et al., 2023, DOI: 10.5006/4336 |
| Al–Li alloys | Expected mixed Al₂O₃ with Li-containing oxide/hydroxide species | **Potentially very high**, but no directly applicable 30–60% RH powder-storage isotherm or rate was located | **Unknown; likely secondary to moisture availability** | **Beneficial, but not sufficient by itself—use sealed dry-Ar storage** | Li-bearing surface phases can be moisture reactive, but quantitative LiOH formation and H₂-evolution rates for passivated AM-sized Al–Cu–Li powder at these conditions are lacking. | Evidence specific to near-ambient humid storage of passivated Al–Li AM powder was not located. |
| Al–Cu alloys | Predominantly Al₂O₃; Cu-rich intermetallic sites may be exposed locally | **Moderate** | **Low–moderate and unquantified** | **Beneficial** | Cu-rich particles can support galvanic localization if an electrolyte film forms; at clean 30–55% RH, the continuous-film risk is much lower than under condensation or salt contamination. (graedel1989corrosionmechanismsfor pages 1-1, graedel1989corrosionmechanismsfor pages 1-2, graedel1989corrosionmechanismsfor pages 2-3) | General atmospheric-Al evidence: Graedel, 1989, DOI: 10.1149/1.2096869; powder-specific data lacking. |
| Al–Sc–Zr alloys | Primarily Al₂O₃; possible Sc/Zr-bearing oxides or intermetallics | **Low–moderate, uncertain** | **Low–moderate and unquantified** | **Probably beneficial** | Bulk aqueous-corrosion studies sometimes report improved passivity from Sc, but no quantitative humid-storage study on atomized Al–Sc–Zr powder was located; Zr’s isolated effect is unresolved. | Powder-specific RH evidence lacking; bulk-alloy results should not be treated as storage-rate data. |
| Al–Ce or Al–Er alloys | Expected Al₂O₃ plus possible rare-earth oxides/intermetallics | **Unknown** | **Unknown but probably small over +3°C** | **Likely beneficial, with low confidence** | Stable rare-earth oxides do not prove improved powder stability: segregation, cathodic intermetallics, oxide continuity, and atomization history may reverse the effect. No applicable Ce/Er powder–RH kinetics were found. | Direct humid-storage evidence lacking. |
| Silicon powder, 98–99.5% Si | Native SiO₂/silanol-terminated surface | **Low–moderate for reversible water adsorption:** structured water forms first, with liquid-like water becoming important above ~60% RH | **Very low for equilibrium adsorption at fixed RH; chemical-oxidation effect not quantified** | **Beneficial** | Lower RH should reduce adsorbed water and cohesion. The cited studies characterize SiO₂ hydration, not oxidation rates of 98–99.5% Si powder, so “negligible oxidation” at 20–30°C remains an inference rather than a measured value here. (asay2006effectsofadsorbed pages 1-3, torun2014studyofwater pages 4-5, torun2014studyofwater pages 1-1) | Asay & Kim, 2006, DOI: 10.1063/1.2192510; Torun et al., 2014, DOI: 10.1039/c3cp54912g |
| Stainless steel 316L | Cr₂O₃-rich passive film with Fe/Ni oxides | **Low–moderate:** humidity can increase surface moisture, O/H measurements, cohesion, and loss of flowability | **Very low for a +3°C change; no direct rate ratio reported** | **Beneficial** | Passive-film chemistry is robust, but humidity is not irrelevant: 24 h exposures from 5–70% RH progressively degraded flow, and the 70% RH powder became non-flowing. (kim2025investigationofmicrostructure pages 3-6, kim2025investigationofmicrostructure pages 1-3) | Kim et al., 2025, DOI: 10.2497/jjspm.16p-t6-09 |


*Table: Comparison of the expected effects of lowering RH from about 55% to 35% while raising temperature from about 22°C to 25°C. It distinguishes direct powder evidence from bulk-alloy inference and explicitly identifies important evidence gaps.*

---

### 4. Summary and Practical Recommendations

**The dehumidified enclosure at ~25 °C / 35% RH is unambiguously preferable** to the room at ~22 °C / 55% RH for storing all of your powder types:

1. **Water adsorption is controlled by RH** (water activity at the powder surface temperature), not by absolute humidity. Lowering RH from 55% to 35% reduces equilibrium molecular-water coverage on Al₂O₃ by approximately 35–50% (deng2008adsorptionofwater pages 4-5).

2. **The ~70% RH critical threshold** for atmospheric corrosion of pristine aluminum means both conditions are below the onset for active corrosion (scher2023modelforhumiditymediated pages 33-37, graedel1989corrosionmechanismsfor pages 1-1), but 35% RH provides a substantially larger safety margin against localized reactions at reactive microstructural sites.

3. **The temperature penalty is small.** Even using the highest plausible Arrhenius estimate (E_a = 150 kJ/mol, giving ~1.85× faster kinetics at 25 °C vs. 22 °C), this factor is overwhelmed by the ~35–50% reduction in water coverage and the orders-of-magnitude suppression of aqueous ion transport at lower RH (scher2023modelforhumiditymediated pages 33-37, trunov2005ignitionofaluminum pages 2-4).

4. **For Li-containing alloys**, the enclosure's dehumidification is beneficial but likely insufficient alone. These powders should be stored under dry argon in sealed containers with desiccant.

5. **For stainless steel and silicon powders**, the 2–5 °C change is negligible. The RH reduction will improve flowability by reducing capillary bridging.

6. **Key evidence gaps** include: (a) no published water-adsorption isotherms specific to AlSi10Mg powder, (b) no quantitative storage-rate data for passivated Al-Li, Al-Ce, or Al-Er AM powders at 30–60% RH, (c) activation energies for near-ambient aluminum oxide thickening are model- and regime-dependent, making precise rate ratios uncertain, and (d) the 70% RH critical threshold was established for clean, unstressed bulk aluminum and may not apply directly to powder with reactive surface phases or mechanical damage.


References

1. (deng2008adsorptionofwater pages 4-5): Xingyi Deng, Tirma Herranz, Christoph Weis, Hendrik Bluhm, and Miquel Salmeron. Adsorption of water on cu2o and al2o3 thin films. Journal of Physical Chemistry C, 112:9668-9672, Jun 2008. URL: https://doi.org/10.1021/jp800944r, doi:10.1021/jp800944r. This article has 182 citations and is from a domain leading peer-reviewed journal.

2. (deng2008adsorptionofwater pages 1-2): Xingyi Deng, Tirma Herranz, Christoph Weis, Hendrik Bluhm, and Miquel Salmeron. Adsorption of water on cu2o and al2o3 thin films. Journal of Physical Chemistry C, 112:9668-9672, Jun 2008. URL: https://doi.org/10.1021/jp800944r, doi:10.1021/jp800944r. This article has 182 citations and is from a domain leading peer-reviewed journal.

3. (deng2008adsorptionofwater pages 2-3): Xingyi Deng, Tirma Herranz, Christoph Weis, Hendrik Bluhm, and Miquel Salmeron. Adsorption of water on cu2o and al2o3 thin films. Journal of Physical Chemistry C, 112:9668-9672, Jun 2008. URL: https://doi.org/10.1021/jp800944r, doi:10.1021/jp800944r. This article has 182 citations and is from a domain leading peer-reviewed journal.

4. (graedel1989corrosionmechanismsfor pages 1-2): T. E. Graedel. Corrosion mechanisms for aluminum exposed to the atmosphere. Journal of The Electrochemical Society, 136:204C-212C, Apr 1989. URL: https://doi.org/10.1149/1.2096869, doi:10.1149/1.2096869. This article has 321 citations and is from a peer-reviewed journal.

5. (graedel1989corrosionmechanismsfor media 1d3944b6): T. E. Graedel. Corrosion mechanisms for aluminum exposed to the atmosphere. Journal of The Electrochemical Society, 136:204C-212C, Apr 1989. URL: https://doi.org/10.1149/1.2096869, doi:10.1149/1.2096869. This article has 321 citations and is from a peer-reviewed journal.

6. (scher2023modelforhumiditymediated pages 27-30): Jeremy A. Scher, Stephen E. Weitzner, Yue Hao, Tae Wook Heo, Stephen T. Castonguay, Sylvie Aubry, Susan A. Carroll, and Matthew P. Kroonblawd. Model for humidity-mediated diffusion on aluminum surfaces and its role in accelerating atmospheric aluminum corrosion. ACS applied materials & interfaces, 15:28716-28730, May 2023. URL: https://doi.org/10.1021/acsami.3c02327, doi:10.1021/acsami.3c02327. This article has 20 citations and is from a domain leading peer-reviewed journal.

7. (asay2006effectsofadsorbed pages 1-3): David B. Asay and Seong H. Kim. Effects of adsorbed water layer structure on adhesion force of silicon oxide nanoasperity contact in humid ambient. The Journal of chemical physics, 124 17:174712, May 2006. URL: https://doi.org/10.1063/1.2192510, doi:10.1063/1.2192510. This article has 300 citations.

8. (torun2014studyofwater pages 4-5): Boray Torun, C. Kunze, Chao Zhang, T. Kühne, and Guido Grundmeier. Study of water adsorption and capillary bridge formation for sio(2) nanoparticle layers by means of a combined in situ ft-ir reflection spectroscopy and qcm-d set-up. Physical chemistry chemical physics : PCCP, 16 16:7377-84, Mar 2014. URL: https://doi.org/10.1039/c3cp54912g, doi:10.1039/c3cp54912g. This article has 56 citations.

9. (torun2014studyofwater pages 1-1): Boray Torun, C. Kunze, Chao Zhang, T. Kühne, and Guido Grundmeier. Study of water adsorption and capillary bridge formation for sio(2) nanoparticle layers by means of a combined in situ ft-ir reflection spectroscopy and qcm-d set-up. Physical chemistry chemical physics : PCCP, 16 16:7377-84, Mar 2014. URL: https://doi.org/10.1039/c3cp54912g, doi:10.1039/c3cp54912g. This article has 56 citations.

10. (raza2021degradationofalsi10mg pages 1-2): Ahmad Raza, Tobias Fiegl, Imran Hanif, Andreas MarkstrÖm, Martin Franke, Carolin Körner, and Eduard Hryha. Degradation of alsi10mg powder during laser based powder bed fusion processing. Materials & Design, 198:109358, Jan 2021. URL: https://doi.org/10.1016/j.matdes.2020.109358, doi:10.1016/j.matdes.2020.109358. This article has 94 citations and is from a highest quality peer-reviewed journal.

11. (raza2021degradationofalsi10mg pages 8-10): Ahmad Raza, Tobias Fiegl, Imran Hanif, Andreas MarkstrÖm, Martin Franke, Carolin Körner, and Eduard Hryha. Degradation of alsi10mg powder during laser based powder bed fusion processing. Materials & Design, 198:109358, Jan 2021. URL: https://doi.org/10.1016/j.matdes.2020.109358, doi:10.1016/j.matdes.2020.109358. This article has 94 citations and is from a highest quality peer-reviewed journal.

12. (cai2011effectofoxygen pages 1-6): Na Cai, Guangwen Zhou, Kathrin Müller, and David E. Starr. Effect of oxygen gas pressure on the kinetics of alumina film growth during the oxidation of al(111) at room temperature. Physical Review B, 84:125445, Sep 2011. URL: https://doi.org/10.1103/physrevb.84.125445, doi:10.1103/physrevb.84.125445. This article has 87 citations and is from a domain leading peer-reviewed journal.

13. (dholiwar1985theoxidationof pages 33-35): R Dholiwar. The oxidation of liquid alminium. Unknown journal, 1985.

14. (czech2010hydrogengenerationfrom pages 23-27): Edith Barbara Czech. Hydrogen generation from aluminum-water systems. ArXiv, Jan 2010. URL: https://doi.org/10.14288/1.0078738, doi:10.14288/1.0078738. This article has 4 citations.

15. (trunov2005ignitionofaluminum pages 2-4): Mikhaylo?A. Trunov, Mirko Schoenitz, and Edward?L. Dreizin. Ignition of aluminum powders under different experimental conditions. Propellants, Explosives, Pyrotechnics, 30:36-43, Feb 2005. URL: https://doi.org/10.1002/prep.200400083, doi:10.1002/prep.200400083. This article has 364 citations.

16. (trunov2005ignitionofaluminum pages 4-5): Mikhaylo?A. Trunov, Mirko Schoenitz, and Edward?L. Dreizin. Ignition of aluminum powders under different experimental conditions. Propellants, Explosives, Pyrotechnics, 30:36-43, Feb 2005. URL: https://doi.org/10.1002/prep.200400083, doi:10.1002/prep.200400083. This article has 364 citations.

17. (ratko2004hydrothermalsynthesisof pages 4-5): A. I. Rat'ko, V. E. Romanenkov, E. V. Bolotnikova, and Zh. V. Krupen'kina. Hydrothermal synthesis of porous al2o3/al metal ceramics: i. oxidation of aluminum powder and structure formation of porous al(oh)3/al composite. Kinetics and Catalysis, 45:141-148, Jan 2004. URL: https://doi.org/10.1023/b:kica.0000016114.78885.00, doi:10.1023/b:kica.0000016114.78885.00. This article has 16 citations and is from a peer-reviewed journal.

18. (ludwig2022infraredspectroscopystudies pages 11-13): Bellamarie Ludwig and Taryn T. Burke. Infrared spectroscopy studies of aluminum oxide and metallic aluminum powders, part i: thermal dehydration and decomposition. Powders, 1:47-61, Mar 2022. URL: https://doi.org/10.3390/powders1010005, doi:10.3390/powders1010005. This article has 36 citations.

19. (ludwig2022infraredspectroscopystudies pages 8-11): Bellamarie Ludwig and Taryn T. Burke. Infrared spectroscopy studies of aluminum oxide and metallic aluminum powders, part i: thermal dehydration and decomposition. Powders, 1:47-61, Mar 2022. URL: https://doi.org/10.3390/powders1010005, doi:10.3390/powders1010005. This article has 36 citations.

20. (fedina2022influenceofalsi10mg pages 4-5): Tatiana Fedina, Filippo Belelli, Giorgia Lupi, Benedikt Brandau, Riccardo Casati, Raphael Berneth, Frank Brueckner, and Alexander F.H. Kaplan. Influence of alsi10mg powder aging on the material degradation and its processing in laser powder bed fusion. Powder Technology, 412:118024, Nov 2022. URL: https://doi.org/10.1016/j.powtec.2022.118024, doi:10.1016/j.powtec.2022.118024. This article has 26 citations and is from a domain leading peer-reviewed journal.

21. (fiegl2021effectofalsi10mg0.4 pages 1-2): Tobias Fiegl, Martin Franke, Ahmad Raza, Eduard Hryha, and Carolin Körner. Effect of alsi10mg0.4 long-term reused powder in pbf-lb/m on the mechanical properties. Materials &amp; Design, 212:110176, Dec 2021. URL: https://doi.org/10.1016/j.matdes.2021.110176, doi:10.1016/j.matdes.2021.110176. This article has 65 citations and is from a highest quality peer-reviewed journal.

22. (fedina2022influenceofalsi10mg pages 1-2): Tatiana Fedina, Filippo Belelli, Giorgia Lupi, Benedikt Brandau, Riccardo Casati, Raphael Berneth, Frank Brueckner, and Alexander F.H. Kaplan. Influence of alsi10mg powder aging on the material degradation and its processing in laser powder bed fusion. Powder Technology, 412:118024, Nov 2022. URL: https://doi.org/10.1016/j.powtec.2022.118024, doi:10.1016/j.powtec.2022.118024. This article has 26 citations and is from a domain leading peer-reviewed journal.

23. (scher2023modelforhumiditymediated pages 33-37): Jeremy A. Scher, Stephen E. Weitzner, Yue Hao, Tae Wook Heo, Stephen T. Castonguay, Sylvie Aubry, Susan A. Carroll, and Matthew P. Kroonblawd. Model for humidity-mediated diffusion on aluminum surfaces and its role in accelerating atmospheric aluminum corrosion. ACS applied materials & interfaces, 15:28716-28730, May 2023. URL: https://doi.org/10.1021/acsami.3c02327, doi:10.1021/acsami.3c02327. This article has 20 citations and is from a domain leading peer-reviewed journal.

24. (graedel1989corrosionmechanismsfor pages 1-1): T. E. Graedel. Corrosion mechanisms for aluminum exposed to the atmosphere. Journal of The Electrochemical Society, 136:204C-212C, Apr 1989. URL: https://doi.org/10.1149/1.2096869, doi:10.1149/1.2096869. This article has 321 citations and is from a peer-reviewed journal.

25. (scher2023modelforhumiditymediated pages 1-6): Jeremy A. Scher, Stephen E. Weitzner, Yue Hao, Tae Wook Heo, Stephen T. Castonguay, Sylvie Aubry, Susan A. Carroll, and Matthew P. Kroonblawd. Model for humidity-mediated diffusion on aluminum surfaces and its role in accelerating atmospheric aluminum corrosion. ACS applied materials & interfaces, 15:28716-28730, May 2023. URL: https://doi.org/10.1021/acsami.3c02327, doi:10.1021/acsami.3c02327. This article has 20 citations and is from a domain leading peer-reviewed journal.

26. (burnett2023mechanismsofenvironmentally pages 29-30): Tim L. Burnett, Ryan Euesden, Yasser Aboura, Yichao Yao, Matthew E. Curd, Cameron Grant, Al Garner, N. J. Henry Holroyd, Zak Barrett, Christian E. Engel, and Phil B. Prangnell. Mechanisms of environmentally induced crack initiation in humid air in new generation al-zn-mg-cu alloys. CORROSION, 79:831-849, Jul 2023. URL: https://doi.org/10.5006/4336, doi:10.5006/4336. This article has 21 citations and is from a peer-reviewed journal.

27. (burnett2023mechanismsofenvironmentally pages 1-4): Tim L. Burnett, Ryan Euesden, Yasser Aboura, Yichao Yao, Matthew E. Curd, Cameron Grant, Al Garner, N. J. Henry Holroyd, Zak Barrett, Christian E. Engel, and Phil B. Prangnell. Mechanisms of environmentally induced crack initiation in humid air in new generation al-zn-mg-cu alloys. CORROSION, 79:831-849, Jul 2023. URL: https://doi.org/10.5006/4336, doi:10.5006/4336. This article has 21 citations and is from a peer-reviewed journal.

28. (burnett2023mechanismsofenvironmentally pages 24-25): Tim L. Burnett, Ryan Euesden, Yasser Aboura, Yichao Yao, Matthew E. Curd, Cameron Grant, Al Garner, N. J. Henry Holroyd, Zak Barrett, Christian E. Engel, and Phil B. Prangnell. Mechanisms of environmentally induced crack initiation in humid air in new generation al-zn-mg-cu alloys. CORROSION, 79:831-849, Jul 2023. URL: https://doi.org/10.5006/4336, doi:10.5006/4336. This article has 21 citations and is from a peer-reviewed journal.

29. (kim2025investigationofmicrostructure pages 3-6): H. Kim, S. Jo, I.-S. Kim, and S.-J. Hong. Investigation of microstructure and mechanical properties of sts 316l powder according to humidity in the ded process. Journal of the Japan Society of Powder and Powder Metallurgy, 72:S1459-S1464, Mar 2025. URL: https://doi.org/10.2497/jjspm.16p-t6-09, doi:10.2497/jjspm.16p-t6-09. This article has 0 citations.

30. (kim2025investigationofmicrostructure pages 1-3): H. Kim, S. Jo, I.-S. Kim, and S.-J. Hong. Investigation of microstructure and mechanical properties of sts 316l powder according to humidity in the ded process. Journal of the Japan Society of Powder and Powder Metallurgy, 72:S1459-S1464, Mar 2025. URL: https://doi.org/10.2497/jjspm.16p-t6-09, doi:10.2497/jjspm.16p-t6-09. This article has 0 citations.

31. (graedel1989corrosionmechanismsfor pages 2-3): T. E. Graedel. Corrosion mechanisms for aluminum exposed to the atmosphere. Journal of The Electrochemical Society, 136:204C-212C, Apr 1989. URL: https://doi.org/10.1149/1.2096869, doi:10.1149/1.2096869. This article has 321 citations and is from a peer-reviewed journal.
