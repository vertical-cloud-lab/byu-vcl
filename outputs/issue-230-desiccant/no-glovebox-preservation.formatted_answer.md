Question: Without an argon glovebox, what are the most effective measures for preserving reactive metal powders in long-term storage?

Context: a university additive-manufacturing lab stores aluminium-based LPBF/ultrasonic-atomization feedstock powders, 150-300 um particle size: elemental Al, Mg, Si, Mn, Cr, Ti, Fe, Ni, Cu, Zn, Sn powders plus brittle crushed Al-Zr, Al-Sc, Al-Er, Al-Ce and Al-Li master-alloy granules for use as melt feedstock. Storage may last several months at room temperature in a lab room with a dehumidifier. There is no glovebox; powder is handled in open air during weighing and transfer, and the lab already has airtight containers and silica gel packets.

Please identify and rank, with literature evidence and quantitative targets:
1. Inert-gas or vacuum packaging without a glovebox: argon backfill/purge of sealed containers, vacuum sealing in metallized foil/Mylar barrier bags, heat-sealed pouches. How low must O2 and H2O be, what oxygen transmission rate does the barrier film need, and how effective is a simple Ar purge-and-seal compared with a glovebox? Are iron-based oxygen absorbers appropriate (they release moisture) for metal powders?
2. Pre-use drying/degassing: recommended temperature, time, and atmosphere for drying aluminium and Al-alloy powders before melting (e.g. vacuum or inert oven at 80-200 C), the threshold above which drying itself grows oxide or coarsens the powder, and how much hydrogen porosity moisture removal actually prevents.
3. Container and aliquot strategy: keeping powder in original unopened supplier packaging, subdividing into single-run aliquots so a jar is opened once, container material choice (glass vs HDPE vs metal), electrostatic-dissipative containers and grounding, headspace minimization, and temperature stability to avoid condensation cycling.
4. Environmental control and monitoring: target room and container relative humidity for reactive metal powder storage, the usefulness of inexpensive RH/temperature data loggers or humidity indicator cards inside the containers, and the risk that opening a cold container in a humid room causes condensation.
5. Low-cost alternatives to a glovebox for transfers: inflatable argon-purged glovebags, purged desiccator cabinets, inert-atmosphere dry boxes, nitrogen vs argon choice for Mg-containing and Li-containing materials.
6. Shelf-life expectations: what published evidence exists for how much aluminium alloy powder chemistry (oxygen content, hydrogen content, flowability) degrades over months of ambient sealed storage versus inert storage, and how powder reuse/aging studies inform this?


# Effective Measures for Preserving Reactive Metal Powders in Long-Term Storage Without an Argon Glovebox

## Overview

Storing reactive aluminium-based powders and master-alloy granules for months at room temperature without a glovebox is feasible, provided a layered defence of atmosphere control, moisture exclusion, container strategy, and environmental management is implemented. The following ranked recommendations synthesize literature evidence with quantitative targets. A summary ranking of measures is presented in the table below.

| Rank | Measure | Key Parameters/Targets | Effectiveness/Impact | Literature Source |
|---:|---|---|---|---|
| 1 | Preserve original packaging; after opening, aliquot and **argon purge-and-seal** | Practical transfer target: **O₂ <100 ppm, H₂O <10 ppm**; stringent benchmark: **<0.5 ppm each**. Minimize headspace; verify residual O₂ rather than relying on purge time alone. Overbag rigid containers in heat-sealed aluminum-foil/metallized barrier pouches. Specify the **lowest available certified OTR and WVTR**; literature reviewed here does not establish a metal-powder-specific OTR cutoff. | Best practical long-term intervention: limits both initial contamination and later permeation. A purge-and-seal is not equivalent to a continuously purified glovebox because open-air loading traps air/moisture and seals/permeation permit later ingress, but repeated purge–vent cycles and low headspace can substantially reduce residual air. | High-purity handling benchmark and comparison with dry/humid exposure (yamasaki2004effectofvacuum pages 1-2); practical glovebox limits (towndrow2007fabricationandhandling pages 2-3); argon-filled steel-drum guidance (benson2012safetyconsiderationswhen pages 10-12); high-barrier Mylar evidence, but no validated powder-specific OTR threshold (gupta2024roleofoxygen pages 8-9) |
| 2 | **Single-run aliquoting** in hermetic containers | Divide each newly opened lot into quantities used in one run; published example: **50 g** portions in borosilicate vials sealed under Ar. Prefer gasketed metal cans or borosilicate glass; use grounded conductive/ESD containers for transfer. Keep containers nearly full without compacting powder. | Prevents cumulative humidity and oxygen exposure from repeatedly opening a bulk jar; improves traceability and confines contamination. Grounded metal is preferable during transfer; glass is an effective storage barrier but cannot itself be grounded, so static controls remain necessary. | Fifty-gram borosilicate aliquots packaged under Ar (grubbs2022explorationofthe pages 2-4); conductive-container grounding and ESD control (ebadat2010electrostatichazardsassociated pages 4-6, benson2012safetyconsiderationswhen pages 9-10); long-term argon-filled steel drums (benson2012safetyconsiderationswhen pages 10-12) |
| 3 | **Environmental humidity and temperature control** | Room: **15–25 °C**, **<55% RH maximum**; aim for **≤30% RH** during opening/transfer. Experimental dry conditions of **17–29% RH** preserved flow better than humid exposure. Avoid temperature cycling; let a cold sealed container equilibrate to room temperature before opening. | Dry, stable conditions suppress adsorption, hydroxide/oxide growth, agglomeration, and condensation. At **80% RH**, AlSi10Mg formed persistent agglomerates; micron Al degraded far less than nano-Al but still lost active metal under severe humid aging. | Storage conditions and condensation control (gomes2023analysisanddevelopment pages 42-44, gomes2023analysisanddevelopment pages 38-42); low-RH AlSi10Mg results (peres2024influenceofmoisture pages 1-2); 80% RH agglomeration (weiss2022investigationonthe pages 2-3); humid-aging particle-size dependence (paravan2019acceleratedageingof pages 1-4) |
| 4 | **Argon-purged glovebag or small inert transfer enclosure** | Load closed containers and tools first; purge with dry Ar, verify atmosphere where practicable, then open and transfer. Use **Ar rather than N₂ for Al–Li/Li-bearing material**; Ar is also the conservative choice for Mg-bearing powders or any heated Mg operation. Maintain grounding, containment, and local dust controls. | Much better than an open-air transfer and inexpensive, but less reliable than a rigid recirculating glovebox because flexible bags leak, lack continuous purification, and are harder to clean and monitor. Nitrogen is not chemically inert toward Li: nitridation becomes significant with heat or moisture. | Inert-enclosure principles and glovebag application (gomes2023analysisanddevelopment pages 42-44, gomes2023analysisanddevelopment pages 38-42, benson2012safetyconsiderationswhen pages 9-10); Li–N₂ reactivity and Ar preference (jeppson1978lithiumliteraturereview pages 35-39, jeppson1978lithiumliteraturereview pages 29-33, sorbie2011synthesisandstructure pages 97-100) |
| 5 | **Pre-use vacuum drying/degassing** as reconditioning, not a substitute for dry storage | Conservative starting schedule for ordinary Al/Al-alloy powder: **80–120 °C for 2–8 h under dynamic vacuum**, then cool under vacuum or dry Ar and keep sealed; validate by mass loss/moisture analysis. Use **120–150 °C** only when needed and alloy-qualified. Hydrated powders showed fresh oxide formation beginning near **390 K (117 °C)** or **450 K (177 °C)**, depending on alloy; H₂ evolution became important near **473 K (200 °C)**. Avoid routine 200 °C treatment of unknown Al–Mg, Al–Li, rapidly solidified, or precipitation-sensitive powders. | Removes physisorbed water and can reduce a hydrogen source, but cannot reverse existing oxide/hydroxide. Excessive heating can consume Al/Mg to form fresh oxide and H₂ or alter metastable phases. Reported laser drying reduced final hydrogen by **up to 25%**, while another LPBF study found little porosity benefit; therefore qualify the schedule experimentally. | Vacuum-degassing thresholds and reaction mechanisms (yamasaki2004effectofvacuum pages 1-2, yamasaki2004effectofvacuum pages 2-3); up-to-25% hydrogen reduction (kramer2026investigationofthe pages 1-2); limited drying benefit in another study (cauwenbergh2019reducinghydrogenpores pages 2-4) |
| 6 | **Container-level monitoring** | Put a cobalt-free humidity-indicator card or compact RH/temperature logger in the secondary barrier bag or clean headspace where compatible. Suggested alarms: **>30% RH internal**, sustained temperature excursions outside **15–25 °C**, broken seal, or repeated cycling. For critical Al–Li/Mg lots, periodically measure headspace O₂/H₂O with a sampling port rather than relying only on RH cards. | Low-cost evidence of seal failure, desiccant exhaustion, or condensation history. RH cards are qualitative and may not respond accurately in Ar or near zero RH; loggers also occupy headspace and may outgas, so qualify them and keep them isolated from direct powder contact. | Temperature/RH/O₂ sensor monitoring and alerts (gomes2023analysisanddevelopment pages 42-44, gomes2023analysisanddevelopment pages 38-42); moisture-related changes justify monitoring (grubbs2022explorationofthe pages 1-2, grubbs2022explorationofthe pages 9-11) |
| 7 | **Do not routinely use iron-based oxygen-absorber sachets** | Most commercial Fe scavengers need available moisture or an internal water/activator system. Do not place them in direct contact with powder. Consider only a supplier-qualified **dry-activated, non-outgassing** scavenger in a separately sealed compartment, with RH validation. | Conventional iron scavengers do **not inherently release water**—rusting generally consumes/requires it—but moisture-dependent activation is ineffective or counterproductive in the ultra-dry package desired for reactive powders. They also add contamination, rupture, and compatibility risks; dry Ar plus desiccant and a sound barrier is preferable. | Moisture dependence of Fe scavengers (akelah2013polymersinfood pages 36-38, gupta2024roleofoxygen pages 9-10, gupta2024roleofoxygen pages 2-4); achievable O₂ below 0.01% in suitable food packages, not validation for metal powder (gupta2024roleofoxygen pages 2-4) |


*Table: Ranked controls for preserving reactive metal powders without a glovebox, including practical atmosphere, drying, packaging, environmental, transfer, and monitoring targets. The table distinguishes evidence-based limits from conservative engineering recommendations where metal-powder-specific data are unavailable.*

---

## 1. Inert-Gas or Vacuum Packaging Without a Glovebox

### Argon Purge-and-Seal

The most effective single intervention is to argon-purge and hermetically seal the storage container. A stringent benchmark for reactive-powder handling is O₂ <0.5 ppm and H₂O <0.5 ppm, as used for research-grade aluminium alloy powder handling in a controlled glovebox environment (yamasaki2004effectofvacuum pages 1-2). A practical glovebox operational limit for highly reactive powders is O₂ <100 ppm and H₂O <10 ppm, with processing halted if moisture exceeds 30 ppm (towndrow2007fabricationandhandling pages 2-3). For a purge-and-seal operation without a glovebox, repeated purge–vent cycles (three or more cycles of evacuating or displacing headspace with dry argon) can substantially reduce residual air. Minimising headspace volume improves the final atmosphere quality.

A simple argon purge-and-seal is not equivalent to a continuously purified glovebox because open-air loading inevitably traps some ambient air and moisture, and the seal/barrier film permits slow permeation over time. However, it is far superior to ambient storage: powders exposed to high-purity argon (<0.5 ppm O₂, <0.5 ppm H₂O) showed no gas desorption during vacuum heating, whereas humid-air-exposed powders showed substantial hydrogen and water desorption (yamasaki2004effectofvacuum pages 1-2, yamasaki2004effectofvacuum pages 2-3).

### Barrier Films and Vacuum Sealing

Metallised foil/Mylar barrier bags provide excellent O₂ and H₂O barriers when heat-sealed. Although the literature reviewed does not establish a metal-powder-specific oxygen transmission rate (OTR) threshold, food-packaging standards recommend high-barrier films with OTR values of approximately 20 mL/m²·day or lower for oxygen-sensitive applications (gupta2024roleofoxygen pages 8-9). For reactive metal powders, the lowest available certified OTR and water-vapour transmission rate (WVTR) should be selected, ideally aluminium-foil laminates with OTR effectively approaching zero. Vacuum sealing within such bags before argon backfill is an excellent strategy for long-term storage.

### Iron-Based Oxygen Absorbers

Iron-based oxygen absorbers are **not recommended** for reactive metal powder storage. These systems require moisture to activate the iron oxidation reaction; metallic iron becomes inert in dry environments (gupta2024roleofoxygen pages 9-10, gupta2024roleofoxygen pages 2-4). While they do not inherently release water—they consume it during the rusting reaction (akelah2013polymersinfood pages 36-38, gupta2024roleofoxygen pages 2-4)—their moisture-dependent activation is ineffective in the ultra-dry package desired for reactive powders. If any moisture were introduced to activate them, it would be counterproductive for moisture-sensitive metal powders. Additionally, there are risks of sachet rupture, iron contamination, and incompatibility with the stored powders. Dry argon plus desiccant plus a sound barrier film is the preferred approach.

---

## 2. Pre-Use Drying and Degassing

### Recommended Parameters

Vacuum degassing studies on rapidly solidified Al-alloy powders provide critical temperature thresholds (yamasaki2004effectofvacuum pages 1-2, yamasaki2004effectofvacuum pages 2-3):

- **Water desorption** rises sharply around **400 K (~127 °C)**, indicating this is an effective temperature for moisture removal.
- **Fresh oxide formation** begins at approximately **390 K (~117 °C)** for highly hydrated alloys (e.g., Al–Zn–Mg–Cu–Ag) and at approximately **450 K (~177 °C)** for less-hydrated alloys (e.g., Al–Ti–Fe–Cr) (yamasaki2004effectofvacuum pages 1-2).
- **Hydrogen evolution** from aluminium–water reactions becomes important near or above **473 K (~200 °C)** (yamasaki2004effectofvacuum pages 2-3).

A conservative starting schedule for ordinary Al/Al-alloy powder is **80–120 °C for 2–8 hours under dynamic vacuum**, followed by cooling under vacuum or dry argon and keeping the powder sealed until use. Temperatures of 120–150 °C should be used only when qualified for the specific alloy. Routine treatment at 200 °C should be avoided for unknown Al–Mg, Al–Li, rapidly solidified, or precipitation-sensitive powders, as fresh oxide growth and hydrogen evolution become significant at these temperatures.

### Hydrogen Porosity Prevention

In-process laser powder drying reduced hydrogen content in PBF-LB-manufactured AlSi10Mg parts by up to 25%, effectively preventing hydrogen-pore formation during subsequent welding (kramer2026investigationofthe pages 1-2). However, another study found that laser powder drying produced little meaningful reduction in hydrogen porosity during LPBF, suggesting that moisture had already been removed during the machine's vacuum pre-cycle (cauwenbergh2019reducinghydrogenpores pages 2-4). AlSi7Mg powder contained approximately 45 ± 11 ppm hydrogen, while printed parts contained 13 ± 4 ppm—roughly one-third as much—attributed partly to the LPBF vacuum pre-cycle (cauwenbergh2019reducinghydrogenpores pages 4-6). These results indicate that pre-drying is beneficial but must be validated for the specific process; it cannot reverse existing oxide/hydroxide formation.

---

## 3. Container and Aliquot Strategy

### Single-Run Aliquoting

Subdividing each powder lot into **single-run aliquots** is among the most practical and effective measures. A published protocol used **50 g portions sealed in borosilicate glass vials under argon** inside a glovebox, demonstrating that small sealed containers limit cumulative exposure (grubbs2022explorationofthe pages 2-4). Without a glovebox, aliquots can be sealed inside an argon-purged glovebag (see Section 5). Each aliquot is opened once immediately before use, eliminating repeated exposure of a bulk container.

### Container Material Selection

- **Grounded metal containers** (stainless steel or aluminium cans with gasketed, clamp-on lids) are recommended for long-term storage, particularly argon-filled steel drums (benson2012safetyconsiderationswhen pages 10-12). Metal provides an impermeable barrier, excellent grounding, and fire resistance.
- **Borosilicate glass** is an effective moisture and gas barrier suitable for smaller aliquots, but it cannot be grounded and requires external static-control measures (grubbs2022explorationofthe pages 2-4).
- **HDPE** containers are permeable to oxygen and moisture over time and are not recommended for long-term inert storage of reactive powders. However, if used short-term, they should be over-bagged in metallised barrier pouches.

### Electrostatic Considerations

Metal powders are conductive (volume resistivity ≤10⁶ Ω·m) and can generate electrostatic charge during pouring, sieving, and transfer (ebadat2010electrostatichazardsassociated pages 1-4). All containers, drums, scoops, funnels, and personnel should be **bonded and grounded** during powder handling to prevent spark discharges that could ignite suspended dust (benson2012safetyconsiderationswhen pages 9-10, benson2012safetyconsiderationswhen pages 10-12). Non-conductive containers, liners, and transfer surfaces should be avoided during active handling unless their breakdown voltage is below 4 kV (ebadat2010electrostatichazardsassociated pages 4-6). Humidity above 65% can accelerate charge dissipation for some materials, but this is impractical for reactive metal powders because high humidity causes agglomeration and oxidation (ebadat2010electrostatichazardsassociated pages 4-6).

### Headspace and Temperature

Containers should be filled as full as practical without compacting the powder, minimising headspace volume and thus the quantity of residual air/moisture after purging. Powder and container should be maintained at the same temperature to prevent condensation during transfers (gomes2023analysisanddevelopment pages 42-44, gomes2023analysisanddevelopment pages 38-42). A cold sealed container must be allowed to equilibrate to room temperature before opening in a warmer, more humid environment.

---

## 4. Environmental Control and Monitoring

### Target Conditions

Published guidance recommends storing metal powders at **15–25 °C and below 55% relative humidity** (gomes2023analysisanddevelopment pages 42-44, gomes2023analysisanddevelopment pages 38-42). However, for reactive aluminium powders, lower humidity is clearly preferable: experimental conditions of **17–29% RH** (with silica gel desiccant) preserved AlSi10Mg flow properties better than higher humidity, while **80% RH** caused persistent agglomerates that could not be dispersed even after shaking (peres2024influenceofmoisture pages 1-2, weiss2022investigationonthe pages 2-3). A practical target for the storage room is **≤30% RH**, achievable with a room dehumidifier plus silica gel in sealed containers.

### Condensation Risk

Opening a cold container in a warm, humid room creates condensation on powder surfaces, which is particularly damaging to reactive metals. The powder and container should be thermally equilibrated to room temperature before opening (gomes2023analysisanddevelopment pages 42-44). Temperature cycling should be minimised; stable storage temperature is more important than low temperature.

### Monitoring

Containers can be equipped with **RH/temperature data loggers or humidity indicator cards (HICs)** to provide evidence of seal integrity, desiccant exhaustion, or environmental excursions (gomes2023analysisanddevelopment pages 42-44, gomes2023analysisanddevelopment pages 38-42). IoT-connected sensors monitoring temperature, humidity, and oxygen have been proposed for powder-management systems. For critical Al–Li or Mg-containing lots, periodic headspace O₂ analysis through a sampling port is more reliable than relying solely on RH cards, which may not respond accurately in argon atmospheres.

---

## 5. Low-Cost Alternatives to a Glovebox for Transfers

### Argon-Purged Glovebags

Inflatable, disposable or reusable glovebags purged with dry argon represent the most practical low-cost alternative to a glovebox for powder weighing and transfer. The procedure involves loading sealed containers and tools into the bag, sealing it, performing multiple purge–vent cycles with dry argon, verifying atmosphere quality where practicable, and then opening containers and performing the transfer (gomes2023analysisanddevelopment pages 42-44, gomes2023analysisanddevelopment pages 38-42). Glovebags are much better than open-air transfer but less reliable than a rigid recirculating glovebox because flexible bags leak, lack continuous atmosphere purification, and are harder to clean and monitor (benson2012safetyconsiderationswhen pages 9-10).

### Purged Desiccator Cabinets and Dry Boxes

A continuously purged desiccator cabinet or inert-atmosphere dry box, maintained with a slow argon flow and desiccant, provides an intermediate level of protection between a glovebag and a full glovebox. These are suitable for temporary storage of opened containers and for weighing/sampling operations.

### Nitrogen vs. Argon

**Argon is mandatory for lithium-containing materials.** Lithium reacts with nitrogen to form lithium nitride (Li₃N), and this reaction is promoted by elevated temperature and moisture. While dry nitrogen reportedly does not react with lithium below approximately 160 °C, reactions become highly exothermic at higher temperatures, and powdered lithium has ignited in flowing nitrogen at 388–410 °C (jeppson1978lithiumliteraturereview pages 35-39, jeppson1978lithiumliteraturereview pages 29-33). In a handling context, trace moisture can catalyse lithium–nitrogen reactions even at lower temperatures (jeppson1978lithiumliteraturereview pages 29-33). Argon was consistently used as the handling and storage atmosphere for lithium-containing materials in all reviewed studies (sorbie2011synthesisandstructure pages 163-167, jolodosky2015reviewofreactivity pages 4-7, sorbie2011synthesisandstructure pages 97-100).

For **magnesium-containing powders**, argon is likewise the conservative choice. Magnesium can react with nitrogen at elevated temperatures to form magnesium nitride (Mg₃N₂), making nitrogen unsuitable as an inert atmosphere for heated Mg operations or long-term storage of fine Mg powder (sorbie2011synthesisandstructure pages 163-167, jeppson1978lithiumliteraturereview pages 29-33).

For **standard Al, Si, Cu, Fe, Ni, Sn, Mn, Cr, Ti, and Zn** powders, nitrogen is generally acceptable as a protective atmosphere at room temperature, but argon is preferable as a universal choice when the lab handles multiple powder types including Li and Mg.

---

## 6. Shelf-Life Expectations

Quantitative literature data on aluminium alloy powder degradation are summarised in the following table.

| Study/source | Powder material | Condition/duration | Oxygen content (virgin) | Oxygen content (after) | Oxide-layer change | Key finding |
|---|---|---|---:|---:|---|---|
| Fedina et al. (2022) (fedina2022influenceofalsi10mg pages 4-5, fedina2022influenceofalsi10mg pages 5-6, fedina2022influenceofalsi10mg pages 1-2) | AlSi10Mg | Induced ambient-atmosphere aging, 96 h; R0 processed reference also measured | 0.067 wt% O | R0: 0.072 wt% O; aged: 0.257 wt% O; R0-aged: 0.274 wt% O | Not quantified in the cited passage | Aging raised oxygen by about 0.190 percentage points (approximately 3.8×). Printed-part porosity increased from 3.16% with virgin powder to 6.5% with aged powder; accelerated aging is not equivalent to ordinary sealed storage. |
| Raza et al. (2021) (raza2021degradationofalsi10mg pages 1-2) | AlSi10Mg | Approximately 30 months of LPBF reuse | Not reported in the cited passage | Not reported in the cited passage | Mean surface oxide: approximately 4 nm → 38 nm; oxidized-spatter scale reached approximately 120–125 nm | Reused powder contained up to 3% heavily oxidized spatter. This combines storage, handling, thermal exposure, and reuse—not passive shelf aging alone. |
| Ferreira et al. (2025), including reviewed 21-build study (ferreira2025reusepowderimpacts pages 12-14) | AlSi10Mg | Consecutive LPBF reuse builds without rejuvenation | Approximately 0.08 wt% O in the cited 21-build study | Approximately 0.19 wt% O after 21 builds | Not reported in the cited passage | Oxygen rose by roughly 0.005 percentage points per build; the review notes substantial study-to-study variation, with other campaigns remaining around 0.11–0.14 wt% O. |
| Paravan et al. (2019) (paravan2019acceleratedageingof pages 1-4, paravan2019acceleratedageingof pages 16-18) | Approximately 30 µm elemental Al; nano-Al comparators | Accelerated aging at 333 K: dry, RH <10%, or humid, RH approximately 80%, for up to 14 days | Not reported as oxygen content | Not reported as oxygen content | Not measured directly; degradation reported as loss of active Al and hydroxide/passivation growth | Dry exposure caused no marked change over 14 days. At 80% RH, micron Al lost approximately 13% of active Al in 14 days, while nano-Al was nearly consumed within 24–72 h; these severe conditions should not be extrapolated directly to sealed room-temperature storage. |
| Yamasaki & Kawamura (2004) (yamasaki2004effectofvacuum pages 1-2, yamasaki2004effectofvacuum pages 2-3) | Al–Zn–Mg–Cu–Ag and Al–Ti–Fe–Cr rapidly solidified powders | Vacuum heating after controlled Ar, dry-air, or humid-air exposure | Not reported in the cited passage | Not reported in the cited passage | Fresh oxide began near 390 K (117 °C) for hydrated Al–Zn–Mg–Cu–Ag and near 450 K (177 °C) for Al–Ti–Fe–Cr | Adsorbed water, rather than oxygen alone, drove fresh oxide formation; water desorption rose near 400 K and hydrogen evolution became important near/above 473 K (200 °C), limiting aggressive drying schedules. |
| Kramer et al. (2026) (kramer2026investigationofthe pages 1-2, kramer2026investigationofthe pages 2-4) | AlSi10Mg | In-process laser drying before melting | Not reported in the cited passage | Not reported in the cited passage | Not reported | Laser powder drying reduced hydrogen in manufactured material by up to 25% and suppressed hydrogen-pore formation during later welding; this does not establish the performance of a specific 200 °C vacuum-oven treatment. |


*Table: Quantitative literature benchmarks for oxidation, active-aluminum loss, oxide growth, porosity, and hydrogen reduction. The conditions range from passive humidity exposure to accelerated aging and LPBF reuse, so they should not be interpreted as a single universal shelf-life curve.*

### Key Observations

**Virgin AlSi10Mg** typically contains approximately **0.067–0.08 wt% oxygen** (fedina2022influenceofalsi10mg pages 4-5, ferreira2025reusepowderimpacts pages 12-14). Under accelerated ambient-atmosphere aging (96 hours), oxygen content increased approximately four-fold to **0.257 wt%**, and printed-part porosity increased from 3.16% to 6.5% (fedina2022influenceofalsi10mg pages 4-5, fedina2022influenceofalsi10mg pages 1-2). During LPBF reuse without rejuvenation, oxygen increased by approximately **0.005 percentage points per build cycle**, reaching approximately 0.19 wt% after 21 builds—a rate that would exceed the 0.2% specification limit after approximately nine consecutive builds (ferreira2025reusepowderimpacts pages 12-14).

Over a **30-month reuse campaign**, the mean surface oxide layer on AlSi10Mg grew from approximately 4 nm to 38 nm—nearly an order of magnitude—and up to 3% of the powder consisted of heavily oxidised spatter particles with oxide scales reaching 120–125 nm (raza2021degradationofalsi10mg pages 1-2).

For **micron-scale elemental aluminium**, dry storage at <10% RH caused **no marked changes over 14 days** in accelerated testing at 333 K. In contrast, humid storage at 80% RH caused micron Al to lose approximately 13% of its active aluminium content in 14 days, while nano-aluminium was nearly completely consumed within 24–72 hours (paravan2019acceleratedageingof pages 1-4, paravan2019acceleratedageingof pages 16-18). These results underscore the critical importance of humidity control: properly sealed, dry, argon-filled storage can preserve micron-scale powder for extended periods, while humid ambient storage causes rapid degradation.

For powder stored continuously for **six months or longer**, oxygen content, moisture, and flow properties should be rechecked against specification before use (gomes2023analysisanddevelopment pages 42-44). This verification is especially important for the Mg, Li, Zn, and Sc-containing materials in the user's inventory, which are more moisture-sensitive than binary Al–Si alloys.

### Practical Shelf-Life Guidance

Based on the available evidence, micron-scale (150–300 µm) aluminium and aluminium alloy powders stored **sealed under argon, with desiccant, at <30% RH and 15–25 °C**, can be expected to remain within specification for several months to approximately one year. The primary degradation pathway is moisture-driven oxide/hydroxide formation, not oxygen gas permeation; thus, the quality of the moisture barrier and the initial dryness of the powder are the dominant factors. Elemental Mg, Li-containing, and Zn-containing powders should be considered more sensitive and re-tested at shorter intervals (e.g., every 2–3 months).

References

1. (yamasaki2004effectofvacuum pages 1-2): Michiaki Yamasaki and Yoshihito Kawamura. Effect of vacuum degassing on surface characteristics of rapidly solidified al-based alloy powders. Materials Transactions, 45:1335-1338, Apr 2004. URL: https://doi.org/10.2320/matertrans.45.1335, doi:10.2320/matertrans.45.1335. This article has 34 citations and is from a peer-reviewed journal.

2. (towndrow2007fabricationandhandling pages 2-3): Peter Towndrow. Fabrication and handling aspects of highly reactive powders. Powder Technology, 174:38-41, May 2007. URL: https://doi.org/10.1016/j.powtec.2006.10.018, doi:10.1016/j.powtec.2006.10.018. This article has 5 citations and is from a domain leading peer-reviewed journal.

3. (benson2012safetyconsiderationswhen pages 10-12): JM Benson. Safety considerations when handling metal powders. Unknown journal, 2012.

4. (gupta2024roleofoxygen pages 8-9): Prerna Gupta. Role of oxygen absorbers in food as packaging material, their characterization and applications. Journal of Food Science and Technology, 61:242-252, Feb 2024. URL: https://doi.org/10.1007/s13197-023-05681-8, doi:10.1007/s13197-023-05681-8. This article has 116 citations.

5. (grubbs2022explorationofthe pages 2-4): Jack Grubbs, Bryer C. Sousa, and Danielle Cote. Exploration of the effects of metallic powder handling and storage conditions on flowability and moisture content for additive manufacturing applications. Metals, 12:603, Mar 2022. URL: https://doi.org/10.3390/met12040603, doi:10.3390/met12040603. This article has 34 citations.

6. (ebadat2010electrostatichazardsassociated pages 4-6): V Ebadat. Electrostatic hazards associated with liquid and powder processing. Unknown journal, 2010.

7. (benson2012safetyconsiderationswhen pages 9-10): JM Benson. Safety considerations when handling metal powders. Unknown journal, 2012.

8. (gomes2023analysisanddevelopment pages 42-44): VHO Gomes. Analysis and development of powder-metal vacuum systems for post-processing in l-pbf. Unknown journal, 2023.

9. (gomes2023analysisanddevelopment pages 38-42): VHO Gomes. Analysis and development of powder-metal vacuum systems for post-processing in l-pbf. Unknown journal, 2023.

10. (peres2024influenceofmoisture pages 1-2): Lucas Salomão Peres, Piter Gargarella, Marcus Vinicius Paiva, Ariano De Giovanni Rodrigues, Marcin Adamiak, and Gilmar Ferreira Batalha. Influence of moisture on the properties of alsi10mg powder for laser powder bed fusion. Materials Research, Jan 2024. URL: https://doi.org/10.1590/1980-5373-mr-2023-0490, doi:10.1590/1980-5373-mr-2023-0490. This article has 4 citations.

11. (weiss2022investigationonthe pages 2-3): Christian Weiss, Jonas Heslenfeld, Jasmin Kathrin Saewe, Sebastian Bremen, and Constantin Leon Häfner. Investigation on the influence of powder humidity in laser powder bed fusion (lpbf). Procedia CIRP, 111:115-120, Jan 2022. URL: https://doi.org/10.1016/j.procir.2022.08.102, doi:10.1016/j.procir.2022.08.102. This article has 22 citations and is from a peer-reviewed journal.

12. (paravan2019acceleratedageingof pages 1-4): Christian Paravan, Alberto Verga, Filippo Maggi, and Luciano Galfetti. Accelerated ageing of micron- and nano-sized aluminum powders: metal content, composition and non-isothermal oxidation reactivity. Acta Astronautica, 158:397-406, May 2019. URL: https://doi.org/10.1016/j.actaastro.2018.08.001, doi:10.1016/j.actaastro.2018.08.001. This article has 47 citations and is from a peer-reviewed journal.

13. (jeppson1978lithiumliteraturereview pages 35-39): D.W. Jeppson, J.L. Ballif, W.W. Yuan, and B.E. Chou. Lithium literature review: lithium's properties and interactions. ArXiv, Apr 1978. URL: https://doi.org/10.2172/6885395, doi:10.2172/6885395. This article has 203 citations.

14. (jeppson1978lithiumliteraturereview pages 29-33): D.W. Jeppson, J.L. Ballif, W.W. Yuan, and B.E. Chou. Lithium literature review: lithium's properties and interactions. ArXiv, Apr 1978. URL: https://doi.org/10.2172/6885395, doi:10.2172/6885395. This article has 203 citations.

15. (sorbie2011synthesisandstructure pages 97-100): N Sorbie. Synthesis and structure of group i and ii nitrides as potential hydrogen stores. Unknown journal, 2011.

16. (yamasaki2004effectofvacuum pages 2-3): Michiaki Yamasaki and Yoshihito Kawamura. Effect of vacuum degassing on surface characteristics of rapidly solidified al-based alloy powders. Materials Transactions, 45:1335-1338, Apr 2004. URL: https://doi.org/10.2320/matertrans.45.1335, doi:10.2320/matertrans.45.1335. This article has 34 citations and is from a peer-reviewed journal.

17. (kramer2026investigationofthe pages 1-2): Steffen Kramer, Victor Lubkowitz, Michael Haas, Johannes Michel, Christoph Spurk, Alexander Olowinsky, Guilherme Abreu Faria, Michael Jarwitz, Thomas Graf, Volker Schulze, and Frederik Zanger. Investigation of the formation and reduction of hydrogen porosity during laser welding of additively manufactured alsi10mg parts. The International Journal of Advanced Manufacturing Technology, 142:6105-6123, Jan 2026. URL: https://doi.org/10.1007/s00170-025-17198-9, doi:10.1007/s00170-025-17198-9. This article has 7 citations.

18. (cauwenbergh2019reducinghydrogenpores pages 2-4): P Van Cauwenbergh. Reducing hydrogen pores and blisters by novel strategies and tailored heat treatments for laser powder bed fusion of alsi7mg0. 6. Unknown journal, 2019.

19. (grubbs2022explorationofthe pages 1-2): Jack Grubbs, Bryer C. Sousa, and Danielle Cote. Exploration of the effects of metallic powder handling and storage conditions on flowability and moisture content for additive manufacturing applications. Metals, 12:603, Mar 2022. URL: https://doi.org/10.3390/met12040603, doi:10.3390/met12040603. This article has 34 citations.

20. (grubbs2022explorationofthe pages 9-11): Jack Grubbs, Bryer C. Sousa, and Danielle Cote. Exploration of the effects of metallic powder handling and storage conditions on flowability and moisture content for additive manufacturing applications. Metals, 12:603, Mar 2022. URL: https://doi.org/10.3390/met12040603, doi:10.3390/met12040603. This article has 34 citations.

21. (akelah2013polymersinfood pages 36-38): Ahmed Akelah. Polymers in food packaging and protection. ArXiv, pages 293-347, Jan 2013. URL: https://doi.org/10.1007/978-1-4614-7061-8\_6, doi:10.1007/978-1-4614-7061-8\_6. This article has 39 citations.

22. (gupta2024roleofoxygen pages 9-10): Prerna Gupta. Role of oxygen absorbers in food as packaging material, their characterization and applications. Journal of Food Science and Technology, 61:242-252, Feb 2024. URL: https://doi.org/10.1007/s13197-023-05681-8, doi:10.1007/s13197-023-05681-8. This article has 116 citations.

23. (gupta2024roleofoxygen pages 2-4): Prerna Gupta. Role of oxygen absorbers in food as packaging material, their characterization and applications. Journal of Food Science and Technology, 61:242-252, Feb 2024. URL: https://doi.org/10.1007/s13197-023-05681-8, doi:10.1007/s13197-023-05681-8. This article has 116 citations.

24. (cauwenbergh2019reducinghydrogenpores pages 4-6): P Van Cauwenbergh. Reducing hydrogen pores and blisters by novel strategies and tailored heat treatments for laser powder bed fusion of alsi7mg0. 6. Unknown journal, 2019.

25. (ebadat2010electrostatichazardsassociated pages 1-4): V Ebadat. Electrostatic hazards associated with liquid and powder processing. Unknown journal, 2010.

26. (sorbie2011synthesisandstructure pages 163-167): N Sorbie. Synthesis and structure of group i and ii nitrides as potential hydrogen stores. Unknown journal, 2011.

27. (jolodosky2015reviewofreactivity pages 4-7): A. Jolodosky, A. Bolind, and M. Fratoni. Review of reactivity experiments for lithium ternary alloys. ArXiv, Sep 2015. URL: https://doi.org/10.2172/1223843, doi:10.2172/1223843. This article has 0 citations.

28. (fedina2022influenceofalsi10mg pages 4-5): Tatiana Fedina, Filippo Belelli, Giorgia Lupi, Benedikt Brandau, Riccardo Casati, Raphael Berneth, Frank Brueckner, and Alexander F.H. Kaplan. Influence of alsi10mg powder aging on the material degradation and its processing in laser powder bed fusion. Powder Technology, 412:118024, Nov 2022. URL: https://doi.org/10.1016/j.powtec.2022.118024, doi:10.1016/j.powtec.2022.118024. This article has 26 citations and is from a domain leading peer-reviewed journal.

29. (fedina2022influenceofalsi10mg pages 5-6): Tatiana Fedina, Filippo Belelli, Giorgia Lupi, Benedikt Brandau, Riccardo Casati, Raphael Berneth, Frank Brueckner, and Alexander F.H. Kaplan. Influence of alsi10mg powder aging on the material degradation and its processing in laser powder bed fusion. Powder Technology, 412:118024, Nov 2022. URL: https://doi.org/10.1016/j.powtec.2022.118024, doi:10.1016/j.powtec.2022.118024. This article has 26 citations and is from a domain leading peer-reviewed journal.

30. (fedina2022influenceofalsi10mg pages 1-2): Tatiana Fedina, Filippo Belelli, Giorgia Lupi, Benedikt Brandau, Riccardo Casati, Raphael Berneth, Frank Brueckner, and Alexander F.H. Kaplan. Influence of alsi10mg powder aging on the material degradation and its processing in laser powder bed fusion. Powder Technology, 412:118024, Nov 2022. URL: https://doi.org/10.1016/j.powtec.2022.118024, doi:10.1016/j.powtec.2022.118024. This article has 26 citations and is from a domain leading peer-reviewed journal.

31. (raza2021degradationofalsi10mg pages 1-2): Ahmad Raza, Tobias Fiegl, Imran Hanif, Andreas MarkstrÖm, Martin Franke, Carolin Körner, and Eduard Hryha. Degradation of alsi10mg powder during laser based powder bed fusion processing. Materials & Design, 198:109358, Jan 2021. URL: https://doi.org/10.1016/j.matdes.2020.109358, doi:10.1016/j.matdes.2020.109358. This article has 94 citations and is from a highest quality peer-reviewed journal.

32. (ferreira2025reusepowderimpacts pages 12-14): Bruna T. Ferreira, João Monteiro, Anderson Borille, Marco Leite, and Inês Ribeiro. Reuse powder impacts in additive manufacturing for aeronautical parts. The International Journal of Advanced Manufacturing Technology, 141:2027-2062, Oct 2025. URL: https://doi.org/10.1007/s00170-025-16619-z, doi:10.1007/s00170-025-16619-z. This article has 8 citations.

33. (paravan2019acceleratedageingof pages 16-18): Christian Paravan, Alberto Verga, Filippo Maggi, and Luciano Galfetti. Accelerated ageing of micron- and nano-sized aluminum powders: metal content, composition and non-isothermal oxidation reactivity. Acta Astronautica, 158:397-406, May 2019. URL: https://doi.org/10.1016/j.actaastro.2018.08.001, doi:10.1016/j.actaastro.2018.08.001. This article has 47 citations and is from a peer-reviewed journal.

34. (kramer2026investigationofthe pages 2-4): Steffen Kramer, Victor Lubkowitz, Michael Haas, Johannes Michel, Christoph Spurk, Alexander Olowinsky, Guilherme Abreu Faria, Michael Jarwitz, Thomas Graf, Volker Schulze, and Frederik Zanger. Investigation of the formation and reduction of hydrogen porosity during laser welding of additively manufactured alsi10mg parts. The International Journal of Advanced Manufacturing Technology, 142:6105-6123, Jan 2026. URL: https://doi.org/10.1007/s00170-025-17198-9, doi:10.1007/s00170-025-17198-9. This article has 7 citations.