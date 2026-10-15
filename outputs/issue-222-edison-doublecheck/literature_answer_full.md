Question: I am designing the first feedstock charges for an AMAZEMET rePowder ultrasonic
atomiser (induction melting module, graphite crucible with a bottom nozzle sealed by a
central sealing rod; melt is pushed out by argon over-pressure, then atomised on a
vibrating sonotrode). Please critically check the following engineering decisions against
the literature and flag anything that is wrong, unsafe, or missing. Be specific and cite.

CONTEXT / GEOMETRY
The crucible is graphite. AMAZEMET publish 225 ml and 400 ml interchangeable crucibles and
state ~20 mm between the sealing rod and the crucible wall (i.e. max feedstock rod diameter
20 mm), inner depth 10-11 cm. I INFERRED the bore as 52 mm and the sealing rod as 12 mm
(225 ml at 105 mm deep -> 52.2 mm; 52 - 2x20 = 12). Q1: is there any published rePowder /
ultrasonic-atomisation crucible dimension, or AMAZEMET feedstock rod spec (they ship Al 4047
benchmark rods), that confirms or contradicts this? What rod diameter and length do they use?

THE CHARGE DESIGN
Instead of a solid feedstock rod, I want to run powder. The plan: turn small cups from
6063 aluminium bar (19.05 mm OD, 63.5 mm long, 12.7 mm bore 47.6 mm deep, so a 3.2 mm wall),
fill the bore with powder, and close it with a press-fit lid turned from the same bar, with a
1 mm vent hole through the lid. Two cups per run stand vertically in the annulus around the
sealing rod. Runs planned: (E1) AlSi10Mg powder in the cup; (E2) solid rod control;
(E3) AlSi10Mg + elemental Si premixed so the total is Al-10Si; (E4) same as E1 but the lid
pressed hydraulically to compact the powder; (E5) elemental Si powder only, total Al-12Si;
(E6) re-atomising our own 6063 powder; (E7) a thin-wall (1.6 mm) shorter cup for a ~19 g charge.

Q2: Will aluminium alloy powder sealed inside a solid aluminium cup actually melt and
homogenise in an induction melt, or does the oxide shell on each particle plus the trapped
gas cause a spongy, unmelted mass? Is there literature on melting/remelting loose Al powder,
oxide-film breakdown, or "powder-in-tube" / encapsulated-powder melting for atomisation?
Q3: Si dissolution: how long does elemental Si powder take to dissolve into molten Al at the
temperatures used for atomisation (roughly 700-850 C), and what Si recovery should I expect?
Is there a minimum superheat or hold time? Is Si segregation or undissolved primary Si a real
risk for E3/E5, and would a master-alloy (AlSi50) be the standard answer instead of elemental Si?
Q4: The 1 mm vent: is venting the right call, or does an open vent let molten Al wick out /
let powder escape / defeat the point? What does the literature say about gas entrapment and
melt ejection when heating encapsulated powder under vacuum or reduced pressure?
Q5: Graphite crucible with aluminium: carbide (Al4C3) formation, boron-nitride wash - is a
wash standard practice, and at what temperature/hold does Al4C3 matter?
Q6: Oxygen pickup per atomisation pass for Al / AlSi10Mg - how much does one re-atomisation
pass add, and how many passes before the powder is out of spec for LPBF?
Q7: Anything else about this charge design that a careful process metallurgist would object to.


## Critical Review of AMAZEMET rePowder Powder-in-Cup Charge Design

The following review addresses each of your seven questions against the available published literature. A summary of verdicts, key findings, and recommended corrective actions is provided in the table below.

| Question ID | Topic | Verdict | Key finding | Recommended action |
|---|---|---|---|---|
| Q1 | Crucible and feedstock geometry | **Missing** | Published rePowder studies found here do not report crucible bore, sealing-rod diameter, or Al 4047 benchmark-rod dimensions. They report 100 g pellet charges, a 50 g arc-melted rod, 400–500 g mixed charges, and—in one graphite setup—a 0.7 mm hBN nozzle, but none validates the inferred 52 mm bore or 12 mm sealing rod. (ge2025highstrengthadditivelymanufacturable pages 7-8, ukabhai2025investigationofalcu pages 3-7, ukabhai2025investigationofalcu pages 1-3) | Do not release cup drawings from inferred geometry. Obtain the controlled drawing or physically measure the actual crucible, rod, nozzle assembly, usable fill height, clearances, and thermal-expansion allowance; obtain the Al 4047 rod drawing directly from AMAZEMET. |
| Q2 | Melting powder inside an Al cup | **Flag** | The cup will melt, but this does **not** ensure a clean homogeneous bath. Every Al particle carries a refractory oxide skin; impinging skins form weak double-film interfaces, while atomized powder can contain trapped Ar and adsorbed moisture/hydrogen. Heating can therefore leave oxide agglomerates, bifilms, dross, pores, or a transient spongy skeleton. Vacuum degassing removes moisture and hydrogen but does not remove alumina. (estrada1991gasentrapmentand pages 4-5, yamasaki2006changesinthe pages 4-4, estrada1991gasentrapmentand pages 1-2, campbell2016crackpopulationsin pages 1-4) | Prefer clean solid feedstock or first consolidate/remelt powder separately and qualify the resulting ingot. If powder must be charged, dry/vacuum-degas it, minimize surface area and oxide inventory, provide a substantial clean molten heel and verified electromagnetic mixing, and inspect a quenched trial melt for oxide clusters, porosity, and undissolved material before atomizing. |
| Q3 | Elemental-Si dissolution and recovery | **Flag** | Solid Si dissolves rather than simply melting at 700–850 °C; dissolution is mass-transfer controlled. At 738 °C with local gas agitation, cylindrical Si specimens showed only about 29–44% dissolved after 2–3.5 min in one study. Raising superheat from 40 to 80 °C increased the mass-transfer coefficient about 30%, while forced convection had a larger effect. Fine powder has shorter diffusion distance but is difficult to wet, oxidizes readily, and may segregate or reach the nozzle before complete dissolution. (ahmadiUnknownyeardissolutionstudiesof pages 1-5, xu2021dissolutionoftitaniumnitrogen pages 43-47, ahmadiUnknownyeardissolutionstudiesof pages 5-9, najafabadi1996thekineticsofa pages 28-33) | Replace elemental Si with certified Al–Si master alloy—commonly AlSi50—or a prealloyed charge. If elemental Si is retained, use coarse clean granules rather than dusty fines, add them below the melt surface, establish a validated superheat/hold/mixing cycle, and confirm Si recovery and homogeneity by multi-location chemistry before opening the nozzle. |
| Q4 | One-millimetre cup vent | **Flag** | Both alternatives are hazardous: a sealed capsule can pressurize from trapped gas, hydrated oxide, moisture, or lubricant; an open 1 mm path can release powder during evacuation/purging and become a capillary outlet for molten Al. Entrapped Ar is not removed by melting, and inadequate powder degassing can cause blistering or porosity. (estrada1991gasentrapmentand pages 4-5, estrada1991gasentrapmentand pages 1-2, estrada1991gasentrapmentand pages 2-4) | Do not use an ordinary press-fit lid as a pressure boundary. Prefer a pre-dried, vacuum-degassed charge in a container whose controlled evacuation path remains above the metal level and is protected by a sintered-metal or labyrinth retainer; validate cold evacuation and hot behavior outside the atomizer. Never hydraulically compact a sealed or nearly sealed capsule. |
| Q5 | Graphite–Al reaction and BN wash | **OK with conditions / Flag long holds** | Al₄C₃ formation from Al and carbon is thermodynamically feasible, and Al-bearing melts can infiltrate and damage graphite severely at high temperature. Direct rePowder practice documents a BN-spray-coated graphite crucible and an hBN nozzle. The available literature does not establish a universal safe time–temperature threshold at 700–850 °C; reaction is slower than at 1500 °C but cannot be assumed absent, especially at coating defects or during repeated long holds. (hoseinpur2020mechanismsofgraphite pages 11-15, hoseinpur2020mechanismsofgraphite pages 8-11, hoseinpur2020mechanismsofgraphite pages 23-43, ge2025highstrengthadditivelymanufacturable pages 7-8) | Apply the manufacturer-approved BN coating uniformly, including wetted graphite and sealing components without obstructing the nozzle; dry/bake it completely, inspect between runs, minimize superheat and residence time, and monitor carbon/Al₄C₃ contamination and coating spallation. |
| Q6 | Oxygen pickup and allowable recycling | **Flag / insufficient pass-specific data** | No reliable universal oxygen increment per Al ultrasonic re-atomization pass was found. LPBF-reuse data are only a proxy: one AlSi10Mg study reported about **0.005 percentage point O per build** and used **0.2 wt% O** as a limit; another reported oxygen nearly doubling after six reuse cycles. Ultrasonic atomization added about 220 ppm O in a titanium example, illustrating strong process dependence—not an Al conversion factor. Full remelting also retains prior oxide and creates fresh droplet surface, so pickup may exceed ordinary powder reuse. (ferreira2025reusepowderimpacts pages 12-14, weiss2021investigationtowardsalsi10mg pages 1-3, sojoodi2025integrationofcircular pages 18-19, ciftcli2025alloydevelopmentfrom pages 3-6) | Do not specify an allowable number of passes in advance. Measure total O by inert-gas fusion before and after every pass, together with H, Mg, particle-size fraction and oxide/inclusion metrics; define acceptance from the powder supplier, LPBF process qualification, and part-property requirements rather than treating 0.2 wt% as universal. |
| Q7 | Other charge-design and safety issues | **Multiple flags** | The 6063 cup is a major fraction of these small charges and therefore changes Mg, Si, Fe and Cu balance; its contribution must be included in every mass balance. Mg can oxidize or evaporate during long/hot holds. Oxides or undissolved Si can block the approximately sub-millimetre outlet. The two 19.05 mm cups also cannot be assumed to fit merely because each is below a stated 20 mm maximum rod diameter: annular placement, sealing-rod motion, induction coupling, buoyancy after partial melting, and the 1.6 mm cup’s collapse mode remain unverified. Powder handling additionally presents combustible-dust, static, contamination, moisture and housekeeping hazards. Published rePowder work uses repeated evacuation/Ar washing, high-purity Ar and low measured chamber oxygen. (ge2025highstrengthadditivelymanufacturable pages 7-8, chen2025recentadvancesin pages 7-9, ukabhai2025investigationofalcu pages 1-3) | Begin with the supplier-approved solid Al 4047 benchmark and one solid-alloy control; next use a single simple consolidated charge. Suspend E3–E7 until geometry, full compositional mass balances, drying/degassing, outlet blockage protection, Mg recovery, pressure relief, dust-risk assessment, and post-run chemical/oxygen/inclusion analyses are documented in a formal process-hazard review. |


*Table: Summary of the literature-based verdicts for Q1–Q7, separating unsupported geometry from metallurgical and safety risks. It also identifies the minimum corrective action before each proposed charge is attempted.*

---

### Q1 — Crucible Dimensions and Feedstock Rod Specifications

No published AMAZEMET rePowder study reports the crucible inner bore, sealing-rod diameter, or the dimensions of the Al 4047 benchmark rods. The closest published data describe the graphite setup as consisting of a graphite crucible, a sealing rod, and a hexagonal boron nitride (hBN) nozzle with an orifice diameter of 0.7 mm, with batch sizes of 400–500 g of feedstock (pure Al discs and arc-melted master-alloy bars) for the induction module at up to 1300 °C (ge2025highstrengthadditivelymanufacturable pages 7-8). A separate study using the induction module charged 100 g of pure Al and Cu pellets at 1100 °C, with 50 g rods produced by arc melting; no rod or crucible dimensions were stated (ukabhai2025investigationofalcu pages 1-3, ukabhai2025investigationofalcu pages 3-7). A conference abstract mentions a 400 cm³ graphite crucible for a different alloy system (ukabhai2025investigationofalcu pages 1-3). Your inferred geometry (52 mm bore, 12 mm sealing rod) is therefore **neither confirmed nor contradicted** by any identified publication. Critically, the 20 mm maximum feedstock diameter stated by AMAZEMET refers to the annular gap between the sealing rod and crucible wall, but your 19.05 mm OD cup leaves essentially zero radial clearance for thermal expansion, fit tolerance, or gas flow. This dimension must be physically verified before committing cup drawings.

**Verdict:** The geometry is unverified. Obtain the controlled drawing or physically measure the crucible, sealing rod, and benchmark rod dimensions from AMAZEMET directly.

---

### Q2 — Melting Powder Inside a Solid Aluminium Cup

This is the single highest-risk element of the proposed design. The literature strongly warns against assuming that loose aluminium powder will melt cleanly into a homogeneous bath.

**Oxide barriers.** Every aluminium powder particle is coated with a tenacious, amorphous Al₂O₃ film that forms within nanoseconds of exposure to oxygen. When particles are brought together during consolidation, the opposed oxide skins form a doubled-over interface—Campbell's "bifilm"—that acts mechanically as a crack rather than a metallic bond (campbell2016crackpopulationsin pages 1-4, campbell2016crackpopulationsin pages 6-7). Alumina is thermodynamically stable in molten aluminium; it does not dissolve. The oxide film is initially amorphous and ductile, but transforms to crystalline alumina at approximately 350 °C (623 K), becoming brittle (yamasaki2006changesinthe pages 4-4). In a small, unstirred melt without flux, the particle-oxide inventory creates a dense population of bifilms and oxide agglomerates that will persist in the liquid (dispinar2006determinationofmetal pages 23-27).

**Gas entrapment and hydrogen.** Gas-atomized aluminium powder retains both trapped atomizing gas (often argon) and adsorbed moisture on the oxide layer. Liquid aluminium dissolves nearly 15× more hydrogen than solid aluminium; during melting, moisture decomposes and hydrogen is absorbed, producing porosity upon solidification (estrada1991gasentrapmentand pages 4-5, estrada1991gasentrapmentand pages 1-2). Vacuum degassing at approximately 350–450 °C is standard practice before powder consolidation (yamasaki2006changesinthe pages 4-4, estrada1991gasentrapmentand pages 1-2). Your enclosed cup provides no vacuum degassing path.

**Metal recovery.** Remelting aluminium scrap with high surface-area-to-volume ratio (e.g., chips) yields only 60–83% metal recovery without protective atmosphere and flux, rising to approximately 90% with argon protection and optimal practice (puga2009recyclingofaluminium pages 5-7, puga2009recyclingofaluminium pages 1-2). Powder has an even higher surface-area-to-volume ratio than chips. Without flux—which is not practical in this atomizer—substantial oxide-related losses should be expected.

**Verdict:** The powder charge will melt, but it will likely produce a dirty melt containing oxide clusters, bifilms, hydrogen porosity, and potentially dross that can block the sub-millimetre nozzle. The "powder in a solid cup" concept is feasible only if the powder is first pre-dried and vacuum-degassed, and the cup is charged into a substantial clean molten heel with adequate electromagnetic stirring.

---

### Q3 — Silicon Dissolution Kinetics (Experiments E3 and E5)

Dissolution of solid silicon in molten aluminium is a mass-transfer-controlled process, not a simple melting event, because Si melts at 1414 °C—far above the Al bath temperature of 700–850 °C (najafabadi1996thekineticsofa pages 28-33, najafabadi1996thekineticsof pages 28-33). When a cold Si specimen is immersed, a solidified aluminium shell ("chill shell") first forms around it; after reheating, dissolution proceeds by diffusion of Si through a concentration boundary layer at the solid–liquid interface (xu2021dissolutionoftitaniumnitrogen pages 43-47).

**Quantitative rates.** Ahmadi et al. immersed metallurgical-grade Si cylinders in molten Al at 738 °C (78 °C superheat) with nitrogen gas agitation. After 2, 3, and 3.5 minutes, dissolved fractions were only 0.29, 0.43, and 0.44, respectively—indicating that even with vigorous stirring, dissolution of bulk Si is measured in minutes, not seconds, and may plateau as the local melt approaches saturation (ahmadiUnknownyeardissolutionstudiesof pages 1-5, ahmadiUnknownyeardissolutionstudiesof pages 5-9). Gas injection at 5 L/min produced approximately five times the dissolved fraction compared to no agitation at 2 minutes, and increasing superheat from 40 to 80 °C raised the mass-transfer coefficient by approximately 30% (xu2021dissolutionoftitaniumnitrogen pages 43-47, ahmadiUnknownyeardissolutionstudiesof pages 5-9).

**Implications for E3/E5.** In the rePowder induction module, electromagnetic stirring is the only available convection source—there is no gas lancing. Fine Si powder presents a larger total surface area than a rod, potentially accelerating dissolution, but fine Si particles are extremely difficult to wet, are prone to floating on the melt surface, and can reach the nozzle before dissolving. Industrial foundry practice for producing Al-Si alloys uses pre-alloyed master alloys (typically AlSi50 or AlSi25) rather than elemental Si powder, precisely because dissolution kinetics and recovery are unreliable with elemental additions (kuzmin2019obtainingofal–si pages 1-2). The poor absorption of silicon particles below approximately 5–6 mm is specifically noted as a disadvantage of elemental-Si addition (kuzmin2019obtainingofal–si pages 1-2).

**Verdict:** E3 and E5 carry a serious risk of undissolved primary Si particles reaching the nozzle and either blocking it or producing inhomogeneous powder. Replace elemental Si with a certified AlSi50 or AlSi25 master alloy. If elemental Si is retained, use coarse, clean granules, not dusty fines; apply maximum practical superheat; hold with mixing for a validated period; and confirm Si content and homogeneity by multi-location sampling before opening the nozzle.

---

### Q4 — The 1 mm Vent Hole

Both venting and sealing present hazards. The literature identifies two countervailing problems:

**Sealed capsule risk.** Aluminium powder carries adsorbed moisture, hydrated oxides, and trapped atomizing gas. On heating, moisture decomposes and hydrogen is liberated; hydrated alumina decomposes at approximately 350 °C (623 K) (yamasaki2006changesinthe pages 4-4). In a sealed or semi-sealed container, these gases can pressurize the capsule, potentially causing rupture or violent ejection of powder into the melt. Entrapped argon, being insoluble in aluminium, can persist as gas pockets that reopen during later heating or service (estrada1991gasentrapmentand pages 4-5, estrada1991gasentrapmentand pages 2-4).

**Open vent risk.** A 1 mm hole in the lid creates a capillary path. Under the argon overpressure used to push melt through the nozzle (Ge et al. report 200 mbar overpressure (ge2025highstrengthadditivelymanufacturable pages 7-8)), molten aluminium could wick into or through the vent before the cup walls have fully melted, ejecting metal unpredictably. During chamber evacuation and gas-wash cycles, fine powder can also be aspirated out of the vent hole.

**Verdict:** The 1 mm vent is a flawed compromise. Neither a press-fit lid nor a simple drilled hole provides a controlled degassing path or a reliable pressure boundary. A better approach would be to (a) pre-dry and vacuum-degas the powder outside the atomizer, (b) use an open-top charge (e.g., pellets, granules, or loose powder on top of a solid heel) that is compatible with the chamber atmosphere, or (c) design a container with a labyrinth or sintered-metal plug that permits gas escape during evacuation but prevents powder ejection and metal wicking. If a sealed container must be used, hydraulic compaction (E4) is contraindicated because it reduces the interparticle volume available for gas expansion.

---

### Q5 — Graphite Crucible Compatibility with Aluminium; BN Wash

**Al₄C₃ formation.** The reaction 4Al + 3C → Al₄C₃ is thermodynamically favorable (negative ΔG) at all temperatures above the aluminium liquidus (hoseinpur2020mechanismsofgraphite pages 8-11, hoseinpur2020mechanismsofgraphite pages 23-43). Hoseinpur and Safarian demonstrated catastrophic graphite crucible failure when a Si–20 wt% Al melt was introduced at 1500 °C; aluminium infiltrated the graphite and formed Al₄C₃ with a volume strain of approximately 2.83%, causing the crucible to burst (hoseinpur2020mechanismsofgraphite pages 11-15, hoseinpur2020mechanismsofgraphite pages 23-43). At the lower temperatures relevant to aluminium casting (700–850 °C), the reaction is kinetically slower but is not absent, particularly at coating defects, porous graphite regions, or with extended hold times.

**BN coating as barrier.** Published AMAZEMET practice explicitly includes coating the graphite crucible with BN spray and using an hBN nozzle (ge2025highstrengthadditivelymanufacturable pages 7-8). This is confirmed as standard practice for the system. The BN layer acts as a barrier between molten aluminium and the graphite substrate. However, BN coatings can spall, erode, or develop pinholes during repeated thermal cycling, potentially exposing graphite to the melt.

**Verdict:** BN coating is correct and confirmed by published practice. For aluminium at 700–850 °C with hold times of a few minutes, Al₄C₃ formation is manageable provided the BN layer is intact. Inspect and recoat between runs, minimize superheat and hold time, and monitor for carbon contamination in the product powder. Repeated or extended holds will progressively degrade the coating.

---

### Q6 — Oxygen Pickup per Atomisation Pass

No study was found that reports oxygen pickup per ultrasonic re-atomization pass for aluminium alloys specifically. The available data come from two proxy sources:

**LPBF powder reuse (not re-atomization).** For AlSi10Mg, Ferreira et al. report an oxygen increase of approximately 0.005 percentage points per build cycle, with the 0.2 wt% specification limit predicted to be exceeded after approximately 9 sequential builds without powder refreshing (ferreira2025reusepowderimpacts pages 12-14). Weiss et al. cite Cordova's finding that oxygen approximately doubled over six reuse cycles (weiss2021investigationtowardsalsi10mg pages 1-3). Fedina et al. measured virgin AlSi10Mg at 0.067 wt% O, rising to 0.257 wt% O after 96 hours of atmospheric aging—nearly quadrupling (fedina2022influenceofalsi10mg pages 4-5).

**Ultrasonic atomization (titanium, NiTi).** Ciftcli et al. report approximately 220 ppm oxygen pickup during ultrasonic atomization of recycled titanium chips (ciftcli2025alloydevelopmentfrom pages 3-6). For NiTi, UPA-recycled powder showed 0.118–0.155 wt% oxygen, well above the 0.05 wt% functional limit, primarily attributed to atmospheric control limitations (bajaj2026sustainablepathwaysin pages 4-5, sojoodi2025integrationofcircular pages 18-19).

**Assessment.** Full re-atomization involves complete melting, droplet formation, and re-solidification—creating entirely fresh oxide surfaces. This is fundamentally more oxidizing than LPBF reuse, where only the sieved fraction re-enters the bed. Each pass therefore likely adds substantially more than the ~0.005%/cycle seen in LPBF reuse. Aluminium is also far more oxygen-sensitive than titanium at comparable processing temperatures.

**Verdict:** Expect significant oxygen pickup per re-atomization pass—probably on the order of 0.01–0.05 wt% per pass depending on atmosphere quality, but no reliable aluminium-specific number exists. With virgin AlSi10Mg starting at approximately 0.06–0.07 wt% O and a specification limit of 0.2 wt% O, the margin is narrow. Measure total oxygen by inert-gas fusion before and after every pass. Do not pre-specify an allowable number of passes.

---

### Q7 — Additional Process Metallurgy Concerns

Several issues are not addressed in your charge design and would be flagged by a process metallurgist:

1. **Compositional dilution by the 6063 cup.** AA 6063 is nominally Al-0.4Si-0.7Mg. For a ~19 g cup wall surrounding ~12 g of AlSi10Mg powder, the cup is approximately 60% of the charge mass. This substantially dilutes Si, adds Mg (which will oxidize preferentially during melting and superheating), and shifts the final composition away from AlSi10Mg. Every experiment requires a full mass balance including the cup alloy.

2. **Magnesium loss.** Mg oxidizes and evaporates preferentially from Al melts above approximately 700 °C. Published LPBF reuse studies report measurable Mg loss: Warner et al. found a 7.8% reduction in Mg content over ten build cycles for AlSi7Mg (warner2026theinfluenceof pages 1-2). In a small open melt with high surface-area-to-volume ratio, Mg loss will be even more severe. Puga et al. note the importance of protective atmosphere and degassing practice in controlling such losses (puga2009recyclingofaluminium pages 5-7, puga2009recyclingofaluminium pages 1-2).

3. **Nozzle blockage.** The nozzle orifice is only 0.7 mm (ge2025highstrengthadditivelymanufacturable pages 7-8). Oxide agglomerates, undissolved Si particles, bifilm rafts, or dross from a dirty melt can easily block this. This is a critical single-point-of-failure that makes melt cleanliness non-negotiable.

4. **Chamber atmosphere.** Published AMAZEMET practice uses three evacuation/argon-fill cycles, achieving oxygen below 50 ppm at 200 mbar overpressure (ge2025highstrengthadditivelymanufacturable pages 7-8). The rePowder system evacuates to 4×10⁻¹ mbar before argon filling (ukabhai2025investigationofalcu pages 1-3). Ensure this protocol is followed rigorously; any residual moisture from the powder charge will decompose and add hydrogen to the melt.

5. **Powder handling safety.** Fine aluminium powder is a combustible dust and presents fire and explosion hazards during weighing, filling, and transfer. This must be addressed in a formal process-hazard analysis.

6. **Thin-wall cup (E7, 1.6 mm wall).** A 1.6 mm wall may not survive induction heating without premature melting-through or collapse before the powder charge has melted and degassed. The electromagnetic skin depth at the frequencies used (40 kHz sonotrode, but the induction furnace frequency may differ) determines heating distribution. Cup integrity during the heat-up transient must be verified.

7. **Experiment sequencing.** The proposed experiments jump from a conceptually uncertain powder-in-cup charge (E1) to increasingly complex modifications (elemental Si, hydraulic compaction, elemental-Si-only, re-atomization) without first establishing baseline feasibility. Standard practice would be: (a) run the supplier-approved solid Al 4047 benchmark, (b) run a solid-rod control of the target alloy, (c) attempt a minimal-complexity powder charge with full post-run analysis before adding variables.

---

### Overall Assessment

The powder-in-cup concept is creative but introduces multiple compounding risks—oxide contamination, gas entrapment, compositional uncertainty from the cup alloy, Si dissolution kinetics, nozzle blockage, vent-path failures, and oxygen pickup—that are individually well-documented in the literature as serious challenges. No published rePowder study uses this charging method; all identified publications use solid rods, pellets, discs, or arc-melted ingots as feedstock (ge2025highstrengthadditivelymanufacturable pages 7-8, ukabhai2025investigationofalcu pages 1-3, ciftcli2025alloydevelopmentfrom pages 1-3). The recommendation is to begin with the manufacturer's proven feedstock format, validate the system baseline, and then introduce powder charges incrementally with full analytical characterization at each step.

References

1. (ge2025highstrengthadditivelymanufacturable pages 7-8): Zhaoxuan Ge, Shaolou Wei, Zehua Liu, Tomasz Choma, Lukasz Zrodowski, Marc De Graef, A. John Hart, and S. Mohadeseh Taheri-Mousavi. High-strength additively manufacturable al-zr-er-ni alloys with high as-built ductility and thermal stability. Unknown journal, May 2025. URL: https://doi.org/10.21203/rs.3.rs-6558867/v1, doi:10.21203/rs.3.rs-6558867/v1.

2. (ukabhai2025investigationofalcu pages 3-7): Kiyaasha Dyal Ukabhai, Donald Mkhonto, and Maje Phasha. Investigation of al-cu using different preparation methods on the amazemet repowder machine. MATEC Web of Conferences, 417:03001, Jan 2025. URL: https://doi.org/10.1051/matecconf/202541703001, doi:10.1051/matecconf/202541703001. This article has 0 citations.

3. (ukabhai2025investigationofalcu pages 1-3): Kiyaasha Dyal Ukabhai, Donald Mkhonto, and Maje Phasha. Investigation of al-cu using different preparation methods on the amazemet repowder machine. MATEC Web of Conferences, 417:03001, Jan 2025. URL: https://doi.org/10.1051/matecconf/202541703001, doi:10.1051/matecconf/202541703001. This article has 0 citations.

4. (estrada1991gasentrapmentand pages 4-5): J. L. Estrada, J. Duszczyk, and B. M. Korevaar. Gas entrapment and evolution in prealloyed aluminium powders. Journal of Materials Science, 26:1431-1442, Mar 1991. URL: https://doi.org/10.1007/bf00544650, doi:10.1007/bf00544650. This article has 37 citations and is from a peer-reviewed journal.

5. (yamasaki2006changesinthe pages 4-4): Michiaki Yamasaki and Yoshihito Kawamura. Changes in the surface characteristics of gas-atomized pure aluminum powder during vacuum degassing. Materials Transactions, 47:1902-1905, Aug 2006. URL: https://doi.org/10.2320/matertrans.47.1902, doi:10.2320/matertrans.47.1902. This article has 29 citations and is from a peer-reviewed journal.

6. (estrada1991gasentrapmentand pages 1-2): J. L. Estrada, J. Duszczyk, and B. M. Korevaar. Gas entrapment and evolution in prealloyed aluminium powders. Journal of Materials Science, 26:1431-1442, Mar 1991. URL: https://doi.org/10.1007/bf00544650, doi:10.1007/bf00544650. This article has 37 citations and is from a peer-reviewed journal.

7. (campbell2016crackpopulationsin pages 1-4): John Campbell. Crack populations in metals. ArXiv, 3:1436-1442, Oct 2016. URL: https://doi.org/10.3934/matersci.2016.4.1436, doi:10.3934/matersci.2016.4.1436. This article has 11 citations.

8. (ahmadiUnknownyeardissolutionstudiesof pages 1-5): MS Ahmadi, SA Argyropoulos, M Bussmann, and D Doutre. Dissolution studies of si metal in liquid al with gas injection. Unknown journal, Unknown year.

9. (xu2021dissolutionoftitaniumnitrogen pages 43-47): Jixiang Xu. Dissolution of titanium-nitrogen inclusions in liquid titanium during electron beam melting. ArXiv, Jan 2021. URL: https://doi.org/10.14288/1.0400210, doi:10.14288/1.0400210. This article has 0 citations.

10. (ahmadiUnknownyeardissolutionstudiesof pages 5-9): MS Ahmadi, SA Argyropoulos, M Bussmann, and D Doutre. Dissolution studies of si metal in liquid al with gas injection. Unknown journal, Unknown year.

11. (najafabadi1996thekineticsofa pages 28-33): A Shafyei Najafabadi. The kinetics of dissolution of high melting point alloying elements in molten aluminum. Unknown journal, 1996.

12. (estrada1991gasentrapmentand pages 2-4): J. L. Estrada, J. Duszczyk, and B. M. Korevaar. Gas entrapment and evolution in prealloyed aluminium powders. Journal of Materials Science, 26:1431-1442, Mar 1991. URL: https://doi.org/10.1007/bf00544650, doi:10.1007/bf00544650. This article has 37 citations and is from a peer-reviewed journal.

13. (hoseinpur2020mechanismsofgraphite pages 11-15): Arman Hoseinpur and Jafar Safarian. Mechanisms of graphite crucible degradation in contact with si–al melts at high temperatures and vacuum conditions. Vacuum, 171:108993, Jan 2020. URL: https://doi.org/10.1016/j.vacuum.2019.108993, doi:10.1016/j.vacuum.2019.108993. This article has 23 citations and is from a peer-reviewed journal.

14. (hoseinpur2020mechanismsofgraphite pages 8-11): Arman Hoseinpur and Jafar Safarian. Mechanisms of graphite crucible degradation in contact with si–al melts at high temperatures and vacuum conditions. Vacuum, 171:108993, Jan 2020. URL: https://doi.org/10.1016/j.vacuum.2019.108993, doi:10.1016/j.vacuum.2019.108993. This article has 23 citations and is from a peer-reviewed journal.

15. (hoseinpur2020mechanismsofgraphite pages 23-43): Arman Hoseinpur and Jafar Safarian. Mechanisms of graphite crucible degradation in contact with si–al melts at high temperatures and vacuum conditions. Vacuum, 171:108993, Jan 2020. URL: https://doi.org/10.1016/j.vacuum.2019.108993, doi:10.1016/j.vacuum.2019.108993. This article has 23 citations and is from a peer-reviewed journal.

16. (ferreira2025reusepowderimpacts pages 12-14): Bruna T. Ferreira, João Monteiro, Anderson Borille, Marco Leite, and Inês Ribeiro. Reuse powder impacts in additive manufacturing for aeronautical parts. The International Journal of Advanced Manufacturing Technology, 141:2027-2062, Oct 2025. URL: https://doi.org/10.1007/s00170-025-16619-z, doi:10.1007/s00170-025-16619-z. This article has 8 citations.

17. (weiss2021investigationtowardsalsi10mg pages 1-3): C. Weiss, J. Munk, and C.L. Haefner. Investigation towards alsi10mg powder recycling behavior in the lpbf process and its influences on mechanical properties. Jan 2021. URL: https://doi.org/10.26153/tsw/17605, doi:10.26153/tsw/17605. This article has 8 citations.

18. (sojoodi2025integrationofcircular pages 18-19): Mahyar Sojoodi, Alireza Behvar, Harsh Bajaj, Shiva Mohajerani, Saeedeh Vanaei, Nasrin Taheri Andani, Anwar Algamal, Fatemeh Ghasemibojd, Mahsa Beyk Khorasani, Ahu Celebi, and Mohammad Elahinia. Integration of circular economy into metal additive manufacturing: a review of ultrasonic plasma atomization for producing virgin and recycled niti powder. Shape Memory and Superelasticity, 12:5-45, Oct 2026. URL: https://doi.org/10.1007/s40830-025-00589-y, doi:10.1007/s40830-025-00589-y. This article has 7 citations.

19. (ciftcli2025alloydevelopmentfrom pages 3-6): Jakub Ciftcli, Tomasz Choma, Bartosz Morończyk, Bartosz Kalicki, Filip Puchalski, and Łukasz Żrodowski. Alloy development from sustainable materials – close-loop of materials using ultrasonic atomization. Journal of the Japan Society of Powder and Powder Metallurgy, 72(Supplement):S729-S735, Mar 2025. URL: https://doi.org/10.2497/jjspm.15e-sis13-03, doi:10.2497/jjspm.15e-sis13-03. This article has 7 citations.

20. (chen2025recentadvancesin pages 7-9): Xin Chen, Mariem Ben Saada, Bruno Lavisse, and Amine Ammar. Recent advances in the remelting process for recycling aluminium alloy chips: a critical review. International Journal of Material Forming, Apr 2025. URL: https://doi.org/10.1007/s12289-025-01904-9, doi:10.1007/s12289-025-01904-9. This article has 24 citations and is from a peer-reviewed journal.

21. (campbell2016crackpopulationsin pages 6-7): John Campbell. Crack populations in metals. ArXiv, 3:1436-1442, Oct 2016. URL: https://doi.org/10.3934/matersci.2016.4.1436, doi:10.3934/matersci.2016.4.1436. This article has 11 citations.

22. (dispinar2006determinationofmetal pages 23-27): D Dispinar. Determination of metal quality of aluminium and its alloys. Unknown journal, 2006.

23. (puga2009recyclingofaluminium pages 5-7): H. Puga, J. Barbosa, D. Soares, F. Silva, and S. Ribeiro. Recycling of aluminium swarf by direct incorporation in aluminium melts. Journal of Materials Processing Technology, 209:5195-5203, Jun 2009. URL: https://doi.org/10.1016/j.jmatprotec.2009.03.007, doi:10.1016/j.jmatprotec.2009.03.007. This article has 133 citations and is from a domain leading peer-reviewed journal.

24. (puga2009recyclingofaluminium pages 1-2): H. Puga, J. Barbosa, D. Soares, F. Silva, and S. Ribeiro. Recycling of aluminium swarf by direct incorporation in aluminium melts. Journal of Materials Processing Technology, 209:5195-5203, Jun 2009. URL: https://doi.org/10.1016/j.jmatprotec.2009.03.007, doi:10.1016/j.jmatprotec.2009.03.007. This article has 133 citations and is from a domain leading peer-reviewed journal.

25. (najafabadi1996thekineticsof pages 28-33): A Shafyei Najafabadi. The kinetics of dissolution of high melting point alloying elements in molten aluminum. Unknown journal, 1996.

26. (kuzmin2019obtainingofal–si pages 1-2): MP Kuz'min, PK Chu, AM Qasim, and LM Larionov. Obtaining of al–si foundry alloys using amorphous microsilica–crystalline silicon production waste. Unknown journal, 2019.

27. (fedina2022influenceofalsi10mg pages 4-5): Tatiana Fedina, Filippo Belelli, Giorgia Lupi, Benedikt Brandau, Riccardo Casati, Raphael Berneth, Frank Brueckner, and Alexander F.H. Kaplan. Influence of alsi10mg powder aging on the material degradation and its processing in laser powder bed fusion. Powder Technology, 412:118024, Nov 2022. URL: https://doi.org/10.1016/j.powtec.2022.118024, doi:10.1016/j.powtec.2022.118024. This article has 26 citations and is from a domain leading peer-reviewed journal.

28. (bajaj2026sustainablepathwaysin pages 4-5): Harsh K. Bajaj, Mahyar Sojoodi, Francis Y. Asare Baffour, Maedeh Hesami, Shiva Houshmand, Vidura R. De Silva Kanakaratne, Ahu Celebi, and Mohammad Elahinia. Sustainable pathways in powder reuse: a comparative study of virgin, reused, and ultrasonic-atomization-recycled niti powder for additive manufacturing. Sustainability, 18:1843, Feb 2026. URL: https://doi.org/10.3390/su18041843, doi:10.3390/su18041843. This article has 3 citations.

29. (warner2026theinfluenceof pages 1-2): James H. Warner, Simon P. Ringer, and Gwénaëlle Proust. The influence of powder reuse on alsi7mg manufactured by laser powder bed fusion. Progress in Additive Manufacturing, 11:6191-6208, May 2026. URL: https://doi.org/10.1007/s40964-026-01699-4, doi:10.1007/s40964-026-01699-4. This article has 2 citations and is from a peer-reviewed journal.

30. (ciftcli2025alloydevelopmentfrom pages 1-3): Jakub Ciftcli, Tomasz Choma, Bartosz Morończyk, Bartosz Kalicki, Filip Puchalski, and Łukasz Żrodowski. Alloy development from sustainable materials – close-loop of materials using ultrasonic atomization. Journal of the Japan Society of Powder and Powder Metallurgy, 72(Supplement):S729-S735, Mar 2025. URL: https://doi.org/10.2497/jjspm.15e-sis13-03, doi:10.2497/jjspm.15e-sis13-03. This article has 7 citations.
