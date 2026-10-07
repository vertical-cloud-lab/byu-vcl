Question: We are running a Bayesian-optimization alloy-design campaign on ALUMINIUM-based alloys for laser powder-bed fusion (LPBF). Powder is made in-house by ULTRASONIC ATOMIZATION of ~100 g charges (induction melting in a graphite crucible under argon, melt poured onto a vibrating sonotrode; induction module rated to ~1300 C). The current solute list is Mn, Cr, Zr, Mg, Si, Cu, Ti, Fe, Ni, Ce, Sc, Li, Er, Zn, Sn. A collaborator suggested also including CESIUM (Cs), and cerium (Ce) is already included.

Please answer, with citations and quantitative values wherever the literature has them:

1. CESIUM in aluminium alloys. Is there ANY published use of Cs as an alloying or trace addition to Al alloys (for example as a eutectic-silicon modifier like Na, Sr, K, Rb; as a grain refiner; for precipitation strengthening; for corrosion; in Al-Mg or Al-Li alloys; Cs-containing brazing fluxes such as Cs-fluoroaluminates contaminating the alloy)? What does the Al-Cs binary phase diagram look like (solid solubility of Cs in Al, intermetallic compounds, liquid miscibility gap)? What are the physical constraints on charging Cs into molten aluminium at 700-1000 C under argon: Cs melts at 28 C and boils at 671 C, so what retention/recovery is realistic in an open crucible and during atomization, and what are the safety hazards (pyrophoric, water-reactive)? In what feedstock forms could Cs be dosed (metal in ampoules, Cs compounds such as CsF, Cs2CO3, Cs-aluminate flux, Al-Cs master alloys)? Based on all of this, what lower and upper bounds (in wt.%) would be defensible for Cs in an LPBF Al-alloy design space, or is the evidence that Cs is not a viable alloying element and the suggestion was more likely Ce, Ca, Sr or another element?

2. CERIUM in aluminium alloys for LPBF: what wt.% ranges have been used in published LPBF or rapid-solidification Al-Ce, Al-Ce-Mg, Al-Ce-Ni, Al-Ce-Mn and Al-Ce-Sc-Zr alloys; where is the Al-Al11Ce3 eutectic and where does primary Al11Ce3 appear at rapid-solidification cooling rates; what are hot-cracking, printability and evaporation constraints; and what lower and upper bounds (wt.%) would you recommend for a design-of-experiments / Bayesian-optimization campaign? Also note how Ce is normally charged (Ce metal, Al-10Ce / Al-20Ce master alloy, mischmetal) and any oxidation or purity issues with each form.

Please state clearly where evidence is missing.


# Cesium (Cs) and Cerium (Ce) in Aluminium Alloys for LPBF: A Literature Assessment

## 1. CESIUM (Cs) IN ALUMINIUM ALLOYS

### 1.1 Al–Cs Binary Phase Diagram

The Al–Cs system was assessed by Sangster and Pelton (1993), who reported that liquid Al and Cs are **nearly immiscible** near the melting point of Al (660.5 °C) (songster1993thealcs(aluminumcesium) pages 1-1). The addition of Cs has no measurable effect on the melting point of Al; taking the experimental error limits to be ±1 °C, the thermodynamic freezing-point-depression equation gives **≤0.1 at.% Cs** as an upper limit to the solubility at the melting point of Al (songster1993thealcs(aluminumcesium) pages 1-1). By analogy with Na (whose solubility in liquid Al at 660 °C is 0.18 at.%), the solubility of Cs is expected to be lower by at least a factor of ten, i.e., a few hundredths of an atomic percent (songster1993thealcs(aluminumcesium) pages 1-1). **No intermetallic compounds** have been reported in the Al–Cs system, paralleling the Al–Na, Al–K, and Al–Rb systems, none of which form intermetallics (songster1993thealcs(aluminumcesium) pages 1-1). Mutual solid solubilities are also expected to be extremely small. A claimed liquid–liquid miscibility-gap critical temperature of 675 ± 2 °C was deemed thermodynamically implausible and should be discounted entirely (songster1993thealcs(aluminumcesium) pages 1-1).

In summary, the Al–Cs binary is characterized by: (i) near-complete liquid immiscibility, (ii) no solid solubility of practical significance, and (iii) no intermetallic compounds. There is no eutectic, peritectic, or other useful solidification reaction.

### 1.2 Published Uses of Cs in Al Alloys

**Eutectic-silicon modification.** Davies and West, as cited by Steen (1973), investigated the modifying effects of a number of elements on the pure Al–Si eutectic and found that chloride/fluoride fluxes were effective modifiers for potassium, rubidium, **caesium**, and sodium, but not for lithium (steen1973thesolidificationof pages 24-28). Additionally, 0.2 wt.% of lithium or bismuth produced some modification, while magnesium, cadmium, and lead were ineffective (steen1973thesolidificationof pages 24-28). Baragar et al. (1977) confirmed that Cs could modify non-Al eutectic systems (e.g., Bi–Pb), with only 0.3 wt.% Cs producing complete modification, and noted that the chemisorption strength of alkali metals follows Na < K < Rb < Cs (baragar1977thestructuralmodification pages 1-4, baragar1977thestructuralmodification pages 5-8). However, Cs modification of Al–Si was achieved via **flux additions** (chloride/fluoride salts) rather than direct metallic Cs alloying—the Cs acts as a transient surface-active species rather than a retained solute.

**Brazing fluxes.** Cesium-containing potassium fluoroaluminate fluxes (e.g., KF–CsF–AlF₃ systems with approximately 2% Cs substitution) are used in controlled atmosphere brazing (CAB) of aluminum alloys, particularly for brazing heat-treatable Mg-containing alloys where standard NOCOLOK flux is insufficiently effective (johanssonUnknownyearc5990132003controlledatmosphere pages 1-12). These are surface coatings that are removed or remain as thin residue; they do not constitute Cs alloying of the base metal.

**No published use of Cs as a retained alloying element** in any Al alloy system was identified in this literature search—not for grain refinement, precipitation strengthening, corrosion resistance, or in Al–Mg, Al–Li, or any other wrought/cast Al alloy family.

### 1.3 Physical Constraints on Charging Cs into Molten Aluminium

**Volatility.** Cs melts at 28.4 °C and boils at 671 °C. Since typical Al melting and holding temperatures are 700–800 °C, and your induction module is rated to ~1300 °C, Cs is **above its boiling point** throughout the entire melt-handling and atomization process. Pure Cs would have a vapor pressure exceeding 1 atm at 700 °C. Even accounting for the reduced thermodynamic activity of Cs in an Al melt (due to its near-zero solubility), evaporative loss would be rapid, irreproducible, and essentially complete during pouring and ultrasonic atomization.

**Safety hazards.** Cs is classified as **pyrophoric** (spontaneously igniting on contact with air) and **violently water-reactive** (phillips2005reactivesandexplosives pages 1-3, stout1958safetyconsiderationsfor pages 10-12). The recommended controls include storage under dry inert gas or anhydrous hydrocarbon, transfers under inert atmosphere (preferably in a glove box), purchasing only the amount needed, and keeping containers sealed (phillips2005reactivesandexplosives pages 1-3). Alkali metals including Cs present hazards of explosions or fires from contact with water, chlorinated hydrocarbons, or moist air, as well as caustic burns from metal–water reaction products (stout1958safetyconsiderationsfor pages 10-12). Adding pyrophoric liquid Cs (it is liquid at room temperature) to a >700 °C melt in an open graphite crucible under argon presents extreme fire and explosion risk, particularly during pouring onto a sonotrode where splashing is inherent.

### 1.4 Potential Feedstock Forms for Cs

- **Cs metal** in glass ampoules under argon or mineral oil: extremely hazardous to handle; would flash-boil on contact with molten Al.
- **CsF** (mp 682 °C): could serve as a flux component but would not dissolve Cs into the Al lattice; would form a separate salt phase and produce F-containing fumes.
- **Cs₂CO₃** (mp 610 °C, decomposes): would react with molten Al to produce CO₂ and Cs₂O; Cs would evaporate rather than alloy.
- **No Al–Cs master alloy** exists commercially, consistent with the complete immiscibility of the system.

### 1.5 Recommended Bounds for Cs in the Design Space

**Cs should be excluded from the LPBF alloy design space (fix at 0 wt.%).** The rationale is:

1. Near-zero thermodynamic solubility in both liquid and solid Al—no alloying mechanism exists (songster1993thealcs(aluminumcesium) pages 1-1).
2. No intermetallic compounds to provide strengthening or grain refinement (songster1993thealcs(aluminumcesium) pages 1-1).
3. Boiling point (671 °C) is below the Al melting point, ensuring negligible retention in an open-crucible, ultrasonic-atomization process.
4. Extreme pyrophoricity and water-reactivity create unacceptable safety risks for a laboratory with an open induction-melting/atomization setup (phillips2005reactivesandexplosives pages 1-3, stout1958safetyconsiderationsfor pages 10-12).
5. No published evidence of Cs as a retained metallic solute in any Al alloy.

**The collaborator's suggestion of "Cs" was most likely a misunderstanding or typographical confusion for Ce (cerium), Ca (calcium), or Sr (strontium)**—all of which are well-established alloying elements in Al, and Ce is already on your solute list.

---

## 2. CERIUM (Ce) IN ALUMINIUM ALLOYS FOR LPBF

### 2.1 Al–Ce Binary Phase Diagram and Eutectic

The Al–Al₁₁Ce₃ eutectic has been experimentally determined at **10.6 wt.% Ce (≈2.1 at.% Ce) and 644.5 ± 0.6 °C** (czerwinski2020ontheal–al11ce3 pages 20-22, czerwinski2020ontheal–al11ce3 pages 1-3, czerwinski2020ontheal–al11ce3 media ec44ab80). This clarifies prior literature ambiguity where values ranged from ~10 to 17.8 wt.% Ce and 621–643 °C depending on the diagram version (czerwinski2020ontheal–al11ce3 media 86feeecd). The Al-rich portion of the phase diagram is shown below.

(czerwinski2020ontheal–al11ce3 media ec44ab80)

Ce has extremely low equilibrium solid solubility in α-Al, approximately **0.005 wt.% at the eutectic temperature** (hesselmann2022effectofprecipitationforming pages 1-3). This means that essentially all Ce is present as the intermetallic Al₁₁Ce₃ phase, which provides exceptional thermal stability since there is no supersaturation to drive coarsening via diffusion (hesselmann2022effectofprecipitationforming pages 1-3, liu2024reviewoflaser pages 2-4).

**Primary Al₁₁Ce₃** appears in hypereutectic alloys (>10.6 wt.% Ce). At 15 wt.% Ce, approximately 8% of the liquid transforms to proeutectic Al₁₁Ce₃ before the eutectic reaction; at 20 wt.% Ce, this increases to approximately 13% (czerwinski2020ontheal–al11ce3 pages 5-9). Even slightly hypereutectic compositions such as Al–11Ce show elevated liquidus temperatures (660.1 °C) consistent with primary Al₁₁Ce₃ nucleation (czerwinski2020ontheal–al11ce3 pages 5-9). Under rapid solidification (LPBF cooling rates of 10⁵–10⁷ K/s), the eutectic structure is greatly refined, and the formation/growth of primary Al₁₁Ce₃ is suppressed relative to equilibrium solidification, favoring finer eutectic or cellular structures (behera2026microstructurewettingand pages 28-33, behera2026microstructurewettingand pages 91-99, liu2024reviewoflaser pages 2-4).

### 2.2 LPBF Compositions and Mechanical Properties

A wide range of Al–Ce alloy compositions have been processed by LPBF, spanning approximately 3–12 wt.% Ce with various ternary and quaternary additions. The following table summarizes published compositions and properties:

| LPBF alloy (wt.%) | Ce (wt.%) | Other additions (wt.%) | Processing condition | YS / Rp0.2 (MPa) | UTS / Rm (MPa) | Elongation (%) | Other reported result | Source |
|---|---:|---|---|---:|---:|---:|---|---|
| Al–10Ce | 10 | — | As-built LPBF | 222.1 | 319.3 | 10.8 | Refined Al₁₁Ce₃; estimated Orowan contribution ≈193 MPa | Zhou et al.; summarized by Liu et al. (liu2024reviewoflaser pages 15-17, liu2024reviewoflaser pages 13-15) |
| Al–8Ce–10Mg | 8 | Mg 10 | LPBF, 200 W | 377 | 468.6 | 1.8 | High strength but low ductility; Mg solid-solution strengthening is important | Lv et al.; summarized by Liu et al. (liu2024reviewoflaser pages 15-17) |
| AlCe10MgSi | 10.20 | Mg 5.03; Si 3.30; Fe 0.13 | LPBF, 69 J/mm³ | 430 | 593 | 1.6 | High-energy condition produced greater strength and more columnar microstructure | Hesselmann et al. (hesselmann2022effectofprecipitationforming pages 3-5, hesselmann2022effectofprecipitationforming pages 11-14) |
| Al–10Ce–0.4Sc–0.2Zr | 10 | Sc 0.4; Zr 0.2 | As-built LPBF | 344 | 445 | 10 | After 300 °C/12 h: YS 404 MPa and UTS 474 MPa with little plasticity loss | Summarized by Liu et al. (liu2024reviewoflaser pages 13-15, liu2024reviewoflaser pages 23-25) |
| Near-eutectic Al–Ce–7Mn | Near eutectic; exact Ce not stated in available excerpt | Mn ≈7 | As-built LPBF | ≈268 | Not reported | Slightly above 1 | Primary Al₂₀Mn₂Ce rosettes plus Al₁₁Ce₃ and traces of Al₆Mn; strong 300–400 °C performance | Summarized by Hesselmann et al. (hesselmann2022effectofprecipitationforming pages 1-3) |
| Al–10.5Ce–3.1Ni–1.2Mn | 10.5 | Ni 3.1; Mn 1.2 | LPBF; APT/phase analysis reported | Not reported | Not reported | Not reported | Reported phases include Al₁₁Ce₃, Al₁₀Mn₂Ce, Al₂₀Mn₂Ce, Al₂₃Ni₆Ce₄, and Al₃Ni | Summarized by Liu et al. (liu2024reviewoflaser pages 13-15) |
| Ce-modified Al–Cu alloy (“M1_3Ce”) | 3 | Al–Cu base chemistry not specified in available excerpt | As-built LPBF | Not reported | Not reported | Not reported | Crack-free specimens and hardness up to 130 HV, versus cracking and ≈110 HV without Ce | Arias (ariasUnknownyeartailoringthecomposition pages 192-197) |


*Table: Published LPBF Al–Ce-based compositions and reported room-temperature properties. “Not reported” identifies gaps in the accessible evidence rather than zero performance.*

Key observations from the literature:

- **Binary Al–10Ce** LPBF achieves YS ~222 MPa, UTS ~319 MPa, and elongation ~10.8%, with the refined nanoscale Al₁₁Ce₃ contributing approximately 193 MPa through Orowan strengthening (liu2024reviewoflaser pages 15-17, liu2024reviewoflaser pages 13-15).
- **Al–10Ce–0.4Sc–0.2Zr** is among the strongest LPBF Al–Ce alloys, achieving YS 344 MPa and UTS 445 MPa with 10% elongation as-built, and further strengthening to YS 404 MPa and UTS 474 MPa after thermal exposure at 300 °C for 12 h, with yield retention of 68% at 300 °C, 55% at 350 °C, and 38% at 400 °C (liu2024reviewoflaser pages 23-25).
- **AlCe10MgSi** (Al–10.2Ce–5.0Mg–3.3Si) reached the highest reported UTS of 593 MPa (Rp0.2 = 430 MPa) at a volumetric energy density of 69 J/mm³, though with limited elongation of 1.6% (hesselmann2022effectofprecipitationforming pages 11-14).
- **Al–8Ce–10Mg** achieved YS 377 MPa and UTS 469 MPa at 200 W, but elongation was only 1.8%; higher power (350 W) caused Mg vaporization and reduced strength (liu2024reviewoflaser pages 15-17).
- **Al–Ce–7Mn** near-eutectic alloys showed YS ~268 MPa with slightly above 1% elongation, with particularly good elevated-temperature performance (2–4× conventional AM Al alloys between 300–400 °C) (hesselmann2022effectofprecipitationforming pages 1-3).
- **3 wt.% Ce addition** to an Al–Cu alloy eliminated hot cracking during LPBF and increased hardness from ~110 to ~130 HV relative to the Ce-free version (ariasUnknownyeartailoringthecomposition pages 192-197).

### 2.3 Hot Cracking, Printability, and Evaporation

Near-eutectic Al–Ce compositions exhibit **excellent printability** for LPBF (hesselmann2022effectofprecipitationforming pages 1-3, liu2024reviewoflaser pages 4-6, liu2024reviewoflaser pages 2-4):

- The eutectic Al–Ce system has good fluidity and **low hot-cracking tendency**, enabling crack-free samples over a wide LPBF process-parameter range (hesselmann2022effectofprecipitationforming pages 1-3, liu2024reviewoflaser pages 4-6).
- The binary Al–Ce system has been described as having a broad processing window, solidifying without cracking or porosity (liu2024reviewoflaser pages 2-4).
- Adding 3 wt.% Ce to an Al–Cu alloy eliminated hot cracking that was present in the Ce-free composition regardless of LPBF parameters, with no cracks or delamination observed even in scaled-up cubic and cylindrical parts (ariasUnknownyeartailoringthecomposition pages 192-197).
- The high thermal stability of Al₁₁Ce₃ (no significant coarsening after 300 °C for 24 h) supports high-temperature applications (liu2024reviewoflaser pages 2-4).

**Evaporation constraints:** Ce has a boiling point of 3443 °C, so evaporative losses during melting and LPBF are negligible. However, when Ce is combined with Mg (bp ~1091 °C), higher energy densities can cause **Mg vaporization**, reducing solid-solution strengthening and hardness (liu2024reviewoflaser pages 15-17). Process parameters must be balanced to avoid keyholing/vaporization while ensuring full powder melting (hesselmann2022effectofprecipitationforming pages 3-5).

### 2.4 Recommended Ce Bounds for Bayesian Optimization

Based on the literature:

- **Lower bound: 4 wt.% Ce.** Below ~4 wt.%, the volume fraction of eutectic Al₁₁Ce₃ is insufficient to provide meaningful strengthening or crack resistance. The 3 wt.% Ce addition by Arias was effective for hot-crack elimination in an Al–Cu alloy, so 4 wt.% provides a margin (ariasUnknownyeartailoringthecomposition pages 192-197). Cast alloys with additions ≤1% did not produce appreciable improvements historically.
- **Upper bound: 12 wt.% Ce.** The eutectic is at 10.6 wt.% Ce; compositions above this produce primary Al₁₁Ce₃, which can be beneficial in rapidly solidified material (where primary phase formation is suppressed) but becomes coarse at slow cooling rates (behera2026microstructurewettingand pages 28-33, czerwinski2020ontheal–al11ce3 pages 5-9). Published LPBF work has used up to ~10.5 wt.% Ce. An upper bound of 12 wt.% provides exploration slightly into the hypereutectic regime, which rapid LPBF solidification may tolerate.
- **Highest-priority region: 8–10.6 wt.% Ce** (near-eutectic), where the maximum eutectic fraction maximizes the refined intermetallic network and printability benefits.

### 2.5 Ce Charging Methods and Feedstock Forms

Three approaches have been reported in the literature:

1. **Elemental Ce metal (≥99.9% purity):** Czerwinski and Amirkhiz (2020) used 99.9 wt.% purity elemental Ce and Al, melting 5 kg charges in a clay–graphite crucible in a resistance furnace under **protective argon atmosphere** at 780–800 °C for 0.5 h with intense mixing, followed by composition measurement and adjustment (czerwinski2020ontheal–al11ce3 pages 1-3). This is the most common approach in research. *Oxidation issues:* Ce is highly reactive with oxygen; dross formation is significant without inert gas protection. Ce metal tarnishes rapidly in air and can be pyrophoric when finely divided, requiring storage under oil or argon.

2. **Al–Ce master alloy (e.g., Al–25 wt.% Ce):** Behera (2026) used an Al–25 wt.% Ce master alloy diluted with 99.99% pure Al to produce alloys from Al–2Ce to Al–10Ce, poured at 750 °C (behera2026microstructurewettingand pages 53-58). Master alloys are more convenient and safer to handle than pure Ce metal, as the Ce is pre-alloyed and less reactive. *Oxidation issues:* The Ce in master alloy is already bound as Al₁₁Ce₃ intermetallic, reducing reactivity compared to elemental Ce. Commercial master alloys (Al–10Ce, Al–20Ce) are available but may contain impurities (Fe, Si) from production.

3. **LREE mischmetal:** Sims et al. (2020) used industrial mischmetal containing 51.9 wt.% Ce, 26.15 wt.% La, 5.35 wt.% Pr, and 16.60 wt.% Nd as a substitute for pure Ce (sims2020theefficacyof pages 1-4, sims2020theefficacyof pages 4-9). The Al was melted under argon cover gas, with Ce/mischmetal added incrementally after the Al became fully molten at 750 °C, followed by treatment with a fluorinated salt flux to remove contaminants (sims2020theefficacyof pages 1-4). *Purity issues:* Mischmetal introduces multiple LREE elements; the principal intermetallic was close to Al₁₁(Ce,La,Nd)₃. Small third and fourth phases attributed to contaminant metals in the Ce, mischmetal, and industrial Al were observed (sims2020theefficacyof pages 4-9). For a controlled Bayesian-optimization campaign where Ce is the specific design variable, pure Ce metal or a high-Ce master alloy is preferable to mischmetal to avoid confounding compositional variables.

**For your ultrasonic-atomization setup (~100 g charges, graphite crucible, induction melting under Ar, ≤1300 °C):** An Al–Ce master alloy (e.g., Al–20Ce or Al–25Ce) is the most practical and safest feedstock. It dissolves readily at typical superheats of 750–800 °C, avoids the handling hazards of pure Ce metal, and introduces fewer oxide contaminants than charging loose Ce pieces. The Ar atmosphere in your setup is adequate for oxidation control.

---

## Summary: Cs vs. Ce Feasibility Comparison

The following table provides a comprehensive comparison of Cs and Ce for your LPBF campaign:

| Property | Cesium (Cs) | Cerium (Ce) |
|---|---|---|
| Melting point | 28.4 °C | 798 °C |
| Normal boiling point | 671 °C | 3443 °C |
| Solubility / behavior near Al melting point | Liquid Al and Cs are nearly immiscible; **<0.1 at.% Cs** is the experimental upper bound in liquid Al near 660 °C, and mutual solid solubilities are expected to be extremely small. (songster1993thealcs(aluminumcesium) pages 1-1) | Equilibrium solid solubility in α-Al is only about **0.005 wt.% Ce** at the eutectic temperature; larger additions solidify predominantly as Al–Ce intermetallic/eutectic constituents. (hesselmann2022effectofprecipitationforming pages 1-3) |
| Al intermetallic compounds | **None reported** in the assessed binary Al–Cs system. (songster1993thealcs(aluminumcesium) pages 1-1) | Principally **Al₁₁Ce₃** on the Al-rich side; other reported/calculated Al–Ce phases include Al₃Ce, while multicomponent alloys form additional Ce-bearing compounds. (liu2024reviewoflaser pages 13-15, czerwinski2020ontheal–al11ce3 pages 20-22) |
| Binary eutectic with Al | No conventional Al-rich eutectic: the liquids are nearly immiscible, with a broad liquid–liquid miscibility gap; a reported 675 °C critical point was judged thermodynamically implausible and should be discounted. (songster1993thealcs(aluminumcesium) pages 1-1) | **L → α-Al + Al₁₁Ce₃ at 10.6 wt.% Ce and 644.5 ± 0.6 °C.** (czerwinski2020ontheal–al11ce3 pages 20-22, czerwinski2020ontheal–al11ce3 media ec44ab80) |
| Safety hazards | Extremely air- and moisture-reactive; treat as **pyrophoric and violently water-reactive**, with fire, hydrogen-generation/explosion and caustic-residue hazards. Store and transfer under dry inert gas or suitable anhydrous hydrocarbon—not in contact with water. (phillips2005reactivesandexplosives pages 1-3, stout1958safetyconsiderationsfor pages 10-12) | Reactive and readily oxidized, especially as chips or fine powder, but bulk Ce is far less hazardous than Cs; requires dry handling and inert-gas melt protection to limit Ce oxide/dross formation. Elemental Ce has been melted into Al under Ar. (sims2020theefficacyof pages 1-4, czerwinski2020ontheal–al11ce3 pages 1-3) |
| Volatility at 700–1000 °C | Temperature exceeds the 671 °C normal boiling point. Pure Cs would have vapor pressure **>1 atm**; its equilibrium partial pressure over an Al-rich melt is reduced by its very low activity, but rapid evaporation remains dominant. | Far below the 3443 °C boiling point; volatility is negligible relative to Cs. Oxidation/dross loss, rather than evaporation, is the principal melt-recovery concern. |
| Expected retention during open-crucible melting and ultrasonic atomization | **Very poor and irreproducible—practically near zero for intentional alloying.** Open charging above 700 °C promotes flashing/boiling, while pouring onto a sonotrode and droplet atomization greatly increase area and vapor loss. The literature found here supplies no quantitative Cs recovery value. | **Generally high** under dry Ar when charged as Ce metal or an Al–Ce master alloy. Published melts used 750–800 °C, Ar protection and mixing; quantitative recovery was not reported in the retrieved studies. (sims2020theefficacyof pages 1-4, czerwinski2020ontheal–al11ce3 pages 1-3, behera2026microstructurewettingand pages 53-58) |
| Published Al-alloy / LPBF use | Historical evidence exists for Cs-bearing chloride/fluoride fluxes modifying Al–Si eutectic silicon, and Cs fluoroaluminates are used as brazing fluxes; these are **flux/surface-chemistry uses, not evidence for retained metallic Cs alloying**. No Cs-containing LPBF Al alloy was found. (johanssonUnknownyearc5990132003controlledatmosphere pages 1-12, steen1973thesolidificationof pages 24-28) | Extensive LPBF evidence includes approximately **3–10.6 wt.% Ce**, with cast/rapid-solidification studies extending to roughly **12–20 wt.% Ce**. Examples include Al–10Ce, Al–8Ce–10Mg, Al–10Ce–0.4Sc–0.2Zr and Al–10.5Ce–3.1Ni–1.2Mn. (ariasUnknownyeartailoringthecomposition pages 192-197, liu2024reviewoflaser pages 15-17, liu2024reviewoflaser pages 13-15, liu2024reviewoflaser pages 23-25) |
| LPBF printability | No supporting evidence; volatility, immiscibility, powder contamination and severe handling hazards make Cs unsuitable. | Near-eutectic Al–Ce has good fluidity, a broad processing window and low hot-cracking tendency; crack-free material has been reported. (hesselmann2022effectofprecipitationforming pages 1-3, liu2024reviewoflaser pages 4-6, liu2024reviewoflaser pages 2-4) |
| Defensible Bayesian-optimization bounds | **Recommended: fix at 0 wt.% Cs.** If a deliberately separate, safety-reviewed screening experiment is unavoidable, use only a trace target such as **0–0.01 wt.%**, not because efficacy is established but to test analytical detectability/retention; do not make Cs a routine compositional variable. | **Recommended broad design space: 4–12 wt.% Ce**; a focused near-eutectic LPBF campaign should use approximately **6–11 wt.% Ce**, with **8–10.6 wt.%** as the highest-priority region. Values above 10.6 wt.% increasingly risk primary Al₁₁Ce₃. (hesselmann2022effectofprecipitationforming pages 1-3, behera2026microstructurewettingand pages 28-33, czerwinski2020ontheal–al11ce3 pages 5-9) |
| Overall feasibility | **No:** Cs is not a credible retained LPBF alloying element for the stated open-crucible/ultrasonic-atomization route. | **Yes:** Ce is a demonstrated Al-alloy and LPBF constituent with tractable melting, established phase relations and useful crack-resistant eutectic solidification. |


*Table: Comparison of Cs and Ce as additions to aluminium for LPBF, emphasizing phase equilibria, volatility, safety, melt retention, published evidence and defensible optimization bounds. The evidence strongly favors Ce and supports excluding Cs from routine alloy-design variables.*

### Evidence Gaps

- **No quantitative Cs recovery data** exist for any molten Al system. The conclusion of near-zero retention is inferred from thermodynamic immiscibility and the boiling point being below the Al melting point.
- **No LPBF-specific evaporation loss data** for Ce were found; the literature assumes negligible Ce evaporation given its high boiling point, but quantitative melt-loss measurements during LPBF are absent.
- **Mechanical properties for Al–10.5Ce–3.1Ni–1.2Mn** (LPBF) and **Al–6Ce–3Ni–0.7Fe** (LPBF specifically) were not available in the retrieved literature; the Wu et al. Al–6Ce–3Ni study appears to concern casting or LPBF but full data could not be accessed.
- **Oxidation losses and Ce recovery** during ultrasonic atomization specifically have not been reported; the literature covers conventional crucible melting under Ar.


References

1. (songster1993thealcs(aluminumcesium) pages 1-1): J. Songster and A. D. Pelton. The al-cs (aluminum-cesium) system. Journal of Phase Equilibria, 14:365, Jun 1993. URL: https://doi.org/10.1007/bf02668234, doi:10.1007/bf02668234. This article has 1 citations.

2. (steen1973thesolidificationof pages 24-28): H Steen. The solidification of some metal/non-metal eutectics. Unknown journal, 1973.

3. (baragar1977thestructuralmodification pages 1-4): D. Baragar, M. Sahoo, and Reginald W. Smith. The structural modification of the complex-regular eutectics of bismuth-lead, bismuth-tin and bismuth-thallium. Journal of Crystal Growth, 41:278-286, Dec 1977. URL: https://doi.org/10.1016/0022-0248(77)90056-2, doi:10.1016/0022-0248(77)90056-2. This article has 17 citations and is from a peer-reviewed journal.

4. (baragar1977thestructuralmodification pages 5-8): D. Baragar, M. Sahoo, and Reginald W. Smith. The structural modification of the complex-regular eutectics of bismuth-lead, bismuth-tin and bismuth-thallium. Journal of Crystal Growth, 41:278-286, Dec 1977. URL: https://doi.org/10.1016/0022-0248(77)90056-2, doi:10.1016/0022-0248(77)90056-2. This article has 17 citations and is from a peer-reviewed journal.

5. (johanssonUnknownyearc5990132003controlledatmosphere pages 1-12): H JOHANSSON, T STENQVIST, and HW SWIDERSKY. C599/013/2003 controlled atmosphere brazing of heat treatable alloys with cesium flux. Unknown journal, Unknown year.

6. (phillips2005reactivesandexplosives pages 1-3): LB Phillips and C CHMM. Reactives and explosives: avoiding the big bang. Unknown journal, 2005.

7. (stout1958safetyconsiderationsfor pages 10-12): E.L. comp. Stout. Safety considerations for handling plutonium, uranium, thorium, the alkali metals, zirconium, titanium, magnesium, and calcium. ArXiv, Sep 1958. URL: https://doi.org/10.2172/4336976, doi:10.2172/4336976. This article has 1 citations.

8. (czerwinski2020ontheal–al11ce3 pages 20-22): Frank Czerwinski and Babak Shalchi Amirkhiz. On the al–al11ce3 eutectic transformation in aluminum–cerium binary alloys. Materials, 13:4549, Oct 2020. URL: https://doi.org/10.3390/ma13204549, doi:10.3390/ma13204549. This article has 106 citations.

9. (czerwinski2020ontheal–al11ce3 pages 1-3): Frank Czerwinski and Babak Shalchi Amirkhiz. On the al–al11ce3 eutectic transformation in aluminum–cerium binary alloys. Materials, 13:4549, Oct 2020. URL: https://doi.org/10.3390/ma13204549, doi:10.3390/ma13204549. This article has 106 citations.

10. (czerwinski2020ontheal–al11ce3 media ec44ab80): Frank Czerwinski and Babak Shalchi Amirkhiz. On the al–al11ce3 eutectic transformation in aluminum–cerium binary alloys. Materials, 13:4549, Oct 2020. URL: https://doi.org/10.3390/ma13204549, doi:10.3390/ma13204549. This article has 106 citations.

11. (czerwinski2020ontheal–al11ce3 media 86feeecd): Frank Czerwinski and Babak Shalchi Amirkhiz. On the al–al11ce3 eutectic transformation in aluminum–cerium binary alloys. Materials, 13:4549, Oct 2020. URL: https://doi.org/10.3390/ma13204549, doi:10.3390/ma13204549. This article has 106 citations.

12. (hesselmann2022effectofprecipitationforming pages 1-3): Marcel Hesselmann, Daniel Knoop, Jérémy Epp, Volker Uhlenwinkel, Axel von Hehl, and Anastasiya Toenjes. Effect of precipitation-forming elements in a near-eutectic al-ce alloy for laser powder bed fusion. Additive Manufacturing, 57:102959, Sep 2022. URL: https://doi.org/10.1016/j.addma.2022.102959, doi:10.1016/j.addma.2022.102959. This article has 32 citations and is from a highest quality peer-reviewed journal.

13. (liu2024reviewoflaser pages 2-4): Yuan-Fan Liu, Yang Li, Mingliang Wang, and Zhe Chen. Review of laser powder bed fusion’s microstructure and mechanical characteristics for al-ce alloys. Materials, 17:5085, Oct 2024. URL: https://doi.org/10.3390/ma17205085, doi:10.3390/ma17205085. This article has 12 citations.

14. (czerwinski2020ontheal–al11ce3 pages 5-9): Frank Czerwinski and Babak Shalchi Amirkhiz. On the al–al11ce3 eutectic transformation in aluminum–cerium binary alloys. Materials, 13:4549, Oct 2020. URL: https://doi.org/10.3390/ma13204549, doi:10.3390/ma13204549. This article has 106 citations.

15. (behera2026microstructurewettingand pages 28-33): SK Behera. Microstructure, wetting and solidification modeling of al-ce alloys. Unknown journal, 2026.

16. (behera2026microstructurewettingand pages 91-99): SK Behera. Microstructure, wetting and solidification modeling of al-ce alloys. Unknown journal, 2026.

17. (liu2024reviewoflaser pages 15-17): Yuan-Fan Liu, Yang Li, Mingliang Wang, and Zhe Chen. Review of laser powder bed fusion’s microstructure and mechanical characteristics for al-ce alloys. Materials, 17:5085, Oct 2024. URL: https://doi.org/10.3390/ma17205085, doi:10.3390/ma17205085. This article has 12 citations.

18. (liu2024reviewoflaser pages 13-15): Yuan-Fan Liu, Yang Li, Mingliang Wang, and Zhe Chen. Review of laser powder bed fusion’s microstructure and mechanical characteristics for al-ce alloys. Materials, 17:5085, Oct 2024. URL: https://doi.org/10.3390/ma17205085, doi:10.3390/ma17205085. This article has 12 citations.

19. (hesselmann2022effectofprecipitationforming pages 3-5): Marcel Hesselmann, Daniel Knoop, Jérémy Epp, Volker Uhlenwinkel, Axel von Hehl, and Anastasiya Toenjes. Effect of precipitation-forming elements in a near-eutectic al-ce alloy for laser powder bed fusion. Additive Manufacturing, 57:102959, Sep 2022. URL: https://doi.org/10.1016/j.addma.2022.102959, doi:10.1016/j.addma.2022.102959. This article has 32 citations and is from a highest quality peer-reviewed journal.

20. (hesselmann2022effectofprecipitationforming pages 11-14): Marcel Hesselmann, Daniel Knoop, Jérémy Epp, Volker Uhlenwinkel, Axel von Hehl, and Anastasiya Toenjes. Effect of precipitation-forming elements in a near-eutectic al-ce alloy for laser powder bed fusion. Additive Manufacturing, 57:102959, Sep 2022. URL: https://doi.org/10.1016/j.addma.2022.102959, doi:10.1016/j.addma.2022.102959. This article has 32 citations and is from a highest quality peer-reviewed journal.

21. (liu2024reviewoflaser pages 23-25): Yuan-Fan Liu, Yang Li, Mingliang Wang, and Zhe Chen. Review of laser powder bed fusion’s microstructure and mechanical characteristics for al-ce alloys. Materials, 17:5085, Oct 2024. URL: https://doi.org/10.3390/ma17205085, doi:10.3390/ma17205085. This article has 12 citations.

22. (ariasUnknownyeartailoringthecomposition pages 192-197): NR Arias. Tailoring the composition of the aa2017 to reduce its hot cracking susceptibility during lpbf. Unknown journal, Unknown year.

23. (liu2024reviewoflaser pages 4-6): Yuan-Fan Liu, Yang Li, Mingliang Wang, and Zhe Chen. Review of laser powder bed fusion’s microstructure and mechanical characteristics for al-ce alloys. Materials, 17:5085, Oct 2024. URL: https://doi.org/10.3390/ma17205085, doi:10.3390/ma17205085. This article has 12 citations.

24. (behera2026microstructurewettingand pages 53-58): SK Behera. Microstructure, wetting and solidification modeling of al-ce alloys. Unknown journal, 2026.

25. (sims2020theefficacyof pages 1-4): Zachary C. Sims, David Weiss, Orlando Rios, Hunter B. Henderson, Michael S. Kesler, Scott K. McCall, Michael J. Thompson, Aurelien Perron, and Emily E. Moore. The efficacy of replacing metallic cerium in aluminum–cerium alloys with lree mischmetal. ArXiv, pages 216-221, Jan 2020. URL: https://doi.org/10.1007/978-3-030-36408-3\_30, doi:10.1007/978-3-030-36408-3\_30. This article has 24 citations.

26. (sims2020theefficacyof pages 4-9): Zachary C. Sims, David Weiss, Orlando Rios, Hunter B. Henderson, Michael S. Kesler, Scott K. McCall, Michael J. Thompson, Aurelien Perron, and Emily E. Moore. The efficacy of replacing metallic cerium in aluminum–cerium alloys with lree mischmetal. ArXiv, pages 216-221, Jan 2020. URL: https://doi.org/10.1007/978-3-030-36408-3\_30, doi:10.1007/978-3-030-36408-3\_30. This article has 24 citations.