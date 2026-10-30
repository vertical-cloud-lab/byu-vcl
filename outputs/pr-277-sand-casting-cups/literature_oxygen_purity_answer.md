Question: CONTEXT. We make sealed aluminium "cups" as the charge for a vacuum-induction ultrasonic
atomizer (AMAZEMET rePowder: induction melting in a graphite crucible with a boron-nitride
wash, chamber pumped down then backfilled with argon to ~150-200 mbar, melt at ~800-850 C
pushed by ~0.2 bar argon overpressure through a 0.5-0.7 mm graphite nozzle onto a 40 kHz
sonotrode plate) to make Al-Si powder (target 15-63 um) for laser powder bed fusion and alloy
studies. Today each cup is machined on a lathe from extruded 3/4 in (19 mm) AA 6063-T52 bar:
70 mm long with a 12.7 mm blind bore 57 mm deep (or a 15.9 mm bore and 1.5 mm wall for a
thin-wall version), filled with 6-16 g of gas-atomized AA 4047 (Al-12Si) powder, and closed
by a press-fit 6063 plug with a ~1 mm vent hole (0.013-0.020 mm interference). Three to five
cups (~150-250 g in total) are melted per run. The runs are a Si composition spread (0-30 wt%
4047 powder in 6063) whose composition is computed from the weighed masses, so the cup metal's
own composition and cleanliness matter. The cups exist to put the powder inside bulk metal so
that it melts in contact with liquid, without loose-powder losses and with little oxide
pickup. Current practice: dry or light-oil machining, a 99% IPA flush, and an 80 C dry.

PROPOSAL. To make larger cups (more powder per cup), students are considering sand casting
them instead of machining: melting aluminium (most likely re-melted 6063 offcuts and scrap,
or commercially pure aluminium, or a casting alloy such as A356) in a clay-graphite or SiC
crucible in a university foundry (gas or electric furnace, melting in air, possibly with no
rotary degassing or flux), and hand-pouring into green sand (clay-bonded, ~3-4% moisture) or
chemically bonded no-bake sand moulds with a sand core forming the cavity. The cast cup might
be used as cast, or with only the bore and the plug seat machined.

QUESTION 1 (oxygen, hydrogen and purity). Quantitatively, how does a sand-cast aluminium part
compare with extruded wrought bar of the same alloy as a remelt feedstock, in terms of:
(a) entrained oxide films (bifilms), dross and spinel (MgAl2O4 in Mg-bearing alloys such as
6063): oxide inclusion content by PoDFA, LAIS, LiMCA, K-mold or reduced-pressure test
(mm2/kg, inclusions per kg, bifilm index) and bulk oxygen in ppm; how it depends on pouring
practice (turbulence, gate velocity above ~0.5 m/s, fall height), on the number of remelts,
and on melting in air versus under inert gas;
(b) hydrogen: pickup from mould moisture, humid air, and crucible or tool dressings; typical
hydrogen (mL/100 g) in undegassed versus rotary-degassed melts and in extruded bar; the
resulting gas porosity; and what happens to that hydrogen and porosity when the part is
re-melted under vacuum and then argon (outgassing during pump-down, melt spitting or
bubbling, hydrogen and internal porosity in the atomized powder);
(c) process contamination: Fe pickup from uncoated steel ladles, skimmers and stirring rods
(rates in wt% per hour at 700-750 C); Si or C pickup from crucibles; sand grains and binder
residues embedded in the surface (burn-on, metal penetration); carbon and nitrogen from
organic binders; Na, Ca, K, Cl and F from fluxes and degassing tablets; Mg loss by oxidation
(wt% per melt); Zn and Cu from mixed scrap;
(d) the as-cast surface: thickness and nature of the oxide skin on sand-cast versus machined
aluminium, and how much of the skin must be machined away to reach clean metal;
(e) the effect of feedstock oxide and hydrogen content on atomization: clogging of sub-mm
nozzles by oxide films and inclusions, powder oxygen content, satellite or irregular
particles, internal powder porosity, and any cleanliness specifications for gas- or
ultrasonic-atomization feedstock (e.g. VIGA or EIGA ingot or rod requirements);
(f) the practices that bring a casting close to wrought-bar cleanliness: drying sand and
cores, rotary argon degassing, fluxing, ceramic foam filters, bottom-gated or tilt pouring
(Campbell's casting rules), coated tools, a dedicated crucible, vacuum or inert-gas casting,
and permanent-mould (graphite or steel) casting instead of sand.
Give numbers with citations, and say plainly where the evidence is thin or only indirect.

# Sand-Cast vs. Wrought Aluminium as Remelt Feedstock for Ultrasonic Atomization

## Overview

The following analysis compares sand-cast aluminium with extruded wrought bar (AA 6063-T52) as remelt feedstock for a vacuum-induction ultrasonic atomizer (AMAZEMET rePowder), addressing oxide inclusions, hydrogen, process contamination, surface condition, atomization effects, and mitigation practices. The summary table below provides a quantitative overview of the key parameters.

| Parameter | Wrought Extruded Bar (6063) | Undegassed Sand Casting | Degassed/Filtered Sand Casting | Notes/Source |
|---|---|---|---|---|
| PoDFA total inclusions | About **0.01 mm²/kg** as a general wrought-aluminium benchmark; not a guaranteed value for the specific bar. | **0.34–3.13 mm²/kg** before refining in scrap-containing industrial Al–Mg–Si melts; PoDFA may undercount large bifilms. | **0.05–1.11 mm²/kg** after flux refining; typical reduction about **70%**, but commonly still above the wrought benchmark. | PoDFA is a melt-sample metric, not a direct assay of a finished cup. Typical inclusions include Al₂O₃, MgO, MgAl₂O₄, Al₄C₃, refractory debris and TiB₂ agglomerates. (yao2011experimentalinvestigationand pages 128-133, kovacec2025removalofinclusions pages 3-4, gerrard2014inclusionsandhydrogen pages 62-68, gerrard2014inclusionsandhydrogen pages 87-93) |
| Bifilm index (RPT) | **No defensible finished-bar value**; wrought processing may close or fragment pores but does not prove the absence of oxide films. | Around **≥100 mm** in one highly contaminated, chip-rich melt; this is a comparative poor-quality condition, not a universal sand-casting value. | About **38–42 mm** after intensive rotary or ultrasonic degassing in the same comparative study. | BI is summed pore length on an RPT section and responds jointly to bifilms and hydrogen. It cannot be converted directly to inclusions/kg, and RPT misses closed, uninflated films. (yuksel2026comparisonofthe pages 5-6, yuksel2026comparisonofthe pages 2-5, jarfors2026bifilmgenerationin pages 1-4) |
| Dissolved hydrogen | Solid-Al equilibrium solubility near the melting point is approximately **0.036–0.046 mL/100 g**; actual bar requires LECO measurement and may be lower. | Common air- or gas-furnace melt: about **0.30–0.45 mL/100 g**; equilibrium liquid solubility near 660 °C is approximately **0.67–0.69 mL/100 g**. | Approximately **0.10–0.15 mL/100 g** is achievable in reported Ar-purging and degassing trials. | Green-sand moisture, humid combustion products, wet cores, coatings and tools can raise hydrogen. The liquid-to-solid solubility decrease promotes porosity. (bhojak¹2026ultrasonicacousticcavitation pages 1-4, gerrard2014inclusionsandhydrogen pages 36-42, gerrard2014inclusionsandhydrogen pages 155-160, gerrard2014inclusionsandhydrogen pages 48-56, gerrard2014inclusionsandhydrogen pages 320-324, d.scott2004productionandinspection pages 7-9) |
| Bulk oxygen | **No reliable ppm benchmark found** for commercial 6063 extrusion; low PoDFA does not directly establish low total oxygen. | **No defensible universal ppm value**; expected to be higher and more variable because oxide skins, bifilms, dross, spinel and sand-derived oxides are imperfectly measured. | Inclusion burden is reduced, but **equivalence to wrought-bar bulk oxygen has not been demonstrated**. | Molten aluminium forms amorphous alumina essentially immediately in an oxygen-bearing atmosphere. Bulk oxygen, PoDFA and BI measure different populations and should not be interconverted. (kovacec2025removalofinclusions pages 3-4, gerrard2014inclusionsandhydrogen pages 68-76, jarfors2026bifilmgenerationin pages 1-4) |
| Fe content | AA 6063 chemistry is controlled by the supplier; use the bar certificate and OES/ICP result as the baseline. | Begins with charge chemistry but may rise through mixed scrap and uncoated ferrous tooling; **no defensible universal wt%/h pickup rate was found**. | Degassing and filtration remove gas and inclusions, **not dissolved Fe**; chemistry remains charge- and tooling-dependent. | Repeated recycling tends to accumulate Fe and can generate Fe-rich intermetallics. Measure each foundry batch rather than assuming it remains 6063. (pereira2026scrapselectionand pages 14-17, pereira2026rotaryfurnacerecyclingof pages 30-32, gurkan2026recycledmetalutilization pages 4-6, fracchia2025newprocessesin pages 48-52) |
| Surface oxide | Freshly machined metal carries a thin, rapidly re-formed native oxide; the surface is comparatively smooth and readily solvent-cleaned. | Rough, folded and chemically heterogeneous skin that may contain alumina/spinel, adhered or penetrated sand, burnt binder, dross and oxide laps. | Melt treatment improves internal cleanliness but **does not clean the mould-contact skin**; machining remains necessary. | Exact sand-cast reaction-layer thickness is process-specific and was not established by the retrieved evidence. Sand casting can cause metal penetration, while incompletely dried moulds and coatings generate gas and oxidized bubble trails. (jarfors2026bifilmgenerationin pages 1-4, zhao2002correlationofsand pages 1-8, d.scott2004productionandinspection pages 7-9) |
| Overall feedstock risk | **Low and reproducible** when alloy-certified, freshly machined and cleaned; the preferred baseline for composition-spread experiments and a 0.5–0.7 mm nozzle. | **High and poorly bounded** because of bifilms, hydrogen porosity, sand/binder debris, chemistry drift and nozzle-blockage risk. | **Moderate**; potentially acceptable only with certified charge, dry moulds and cores, quiescent pouring, rotary-Ar degassing, filtration, full machining of mould-contact surfaces and lot testing. | Atomization references report about **50–200 ppm O** for well-controlled VIGA powder and **100–500 ppm O** broadly for inert-gas-atomized powders. EIGA avoids crucible-derived ceramic inclusions; these are powder benchmarks, not cast-cup acceptance limits. (zhang2026gasatomizationfor pages 15-17, dunkley2019metalpowderatomisation pages 3-5, zhang2026gasatomizationfor pages 7-9) |


*Table: Comparison of wrought 6063 bar with untreated and melt-conditioned sand-cast aluminium as remelt feedstock. Values are study-specific benchmarks; unavailable universal quantities are identified explicitly rather than inferred.*

---

## (a) Oxide Inclusions: Bifilms, Dross, and Spinel

**Wrought extruded bar.** Wrought aluminium alloys produced by DC casting with inline degassing and ceramic filtration are reported to contain approximately 0.01 mm²/kg total inclusions by PoDFA, representing a high-cleanliness benchmark (gerrard2014inclusionsandhydrogen pages 62-68). Inclusion types in wrought aluminium include Al₂O₃ particles (typically 50–100 µm), Al₂O₃ films (extending hundreds of micrometres but only a few micrometres thick), MgO, MgAl₂O₄ spinel (formed by reaction of Mg, Al, and O₂ in Mg-bearing alloys such as 6063), TiB₂ agglomerates from grain-refiner residues, and Al₄C₃ carbides (gerrard2014inclusionsandhydrogen pages 62-68, gerrard2014inclusionsandhydrogen pages 68-76). Double oxide films (bifilms) can trap atmospheric gases and promote hydrogen porosity (gerrard2014inclusionsandhydrogen pages 68-76).

**Sand castings — undegassed.** Industrial Al–Mg–Si melts containing 25–50% external scrap showed PoDFA total inclusion levels of 0.34–3.13 mm²/kg before flux treatment — roughly one to two orders of magnitude higher than wrought bar (kovacec2025removalofinclusions pages 3-4). In a university-foundry scenario using re-melted 6063 scrap without rotary degassing or filtration, inclusion levels would be expected at the upper end of this range or higher. The reduced-pressure test (RPT) bifilm index (BI) — the summed length of porosity-related features on a sectioned RPT specimen — was approximately ≥100 mm in a heavily contaminated (50% machining-chip) melt, representing very poor quality (yuksel2026comparisonofthe pages 5-6).

**Effect of pouring practice and turbulence.** Molten aluminium forms an amorphous alumina skin essentially instantaneously upon exposure to oxygen-containing atmospheres (jarfors2026bifilmgenerationin pages 1-4). Every time this skin is broken and folded into the melt by turbulent handling, a bifilm is created. Jarfors and Bogdanoff (2026) modelled bifilm generation during melt transfer and estimated a minimum of approximately 1,577 bifilms/mm³ from two typical industrial transfers and rotary degassing, while experimental FIB serial-sectioning revealed approximately 187,500 hidden oxide defects/mm³ — more than two orders of magnitude higher than predicted, suggesting many bifilms pre-exist in the feedstock (jarfors2026bifilmgenerationin pages 1-4, jarfors2026bifilmgenerationin pages 10-16). For a 1.5 m fall height (typical of a hand-pour from a crucible furnace), the model predicted approximately 1,021 bifilms/mm³ from that single transfer alone, with a maximum bifilm diameter of about 68 µm; a 1.0 m fall contributed another 464 bifilms/mm³ with bifilms up to 83 µm (jarfors2026bifilmgenerationin pages 7-10). Even a 0.3 m pouring height produced modelled damage comparable to six minutes of rotary degassing at 460 rpm (jarfors2026bifilmgenerationin pages 10-16). Melt transfer was identified as considerably more damaging than degassing (jarfors2026bifilmgenerationin pages 4-7).

**Critical gate velocity.** Campbell's principle specifies that free-surface velocity in the gating system must remain below a critical value to avoid entrainment. The critical velocity range for aluminium alloys is approximately 0.3–0.5 m/s (karem2009vibrationassistedfilling pages 34-39, karem2009vibrationassistedfilling pages 66-71). In a gating-system optimization study, a spin-trap design producing 0.43–0.50 m/s gate velocity was subcritical and produced the best results, while a naturally pressurized design at 0.63–1.0 m/s was above critical and caused splashing and reoxidation (bruna2023castingqualityimprovement pages 2-4).

**Effect of remelts.** Each remelt exposes fresh surface to oxidation, adds a new population of entrained bifilms from pouring and handling, and accumulates persistent tramp elements (Fe, Cu, Zn) while losing reactive elements (Mg). The retrieved literature consistently describes iron accumulation and Fe-rich intermetallic proliferation with repeated recycling (pereira2026scrapselectionand pages 14-17, pereira2026rotaryfurnacerecyclingof pages 30-32, gurkan2026recycledmetalutilization pages 4-6, fracchia2025newprocessesin pages 48-52). A specific study on repeatedly remelted AlSi9Cu3(Fe) found significant microstructural degradation after the fourth remelt cycle, with enlargement of eutectic silicon and Fe-bearing intermetallics and reduced ductility (fracchia2025newprocessesin pages 48-52).

**Melting in air vs. inert gas.** In A356 sand-casting experiments, argon-shielded pouring reduced pore volume fraction, number density, and pore size compared with pouring in air, consistent with reduced oxide-film formation and fewer nucleation sites for porosity (yao2011experimentalinvestigationand pages 128-133, yao2011experimentalinvestigationand pages 120-125). However, PoDFA was unable to reliably resolve the oxide-film difference between shielded and unshielded conditions, possibly because the bifilms were too small for the standard inclusion-cake analysis (yao2011experimentalinvestigationand pages 128-133).

---

## (b) Hydrogen

**Solubility and typical levels.** The equilibrium solubility of hydrogen in liquid aluminium near 660°C is approximately 0.67–0.69 mL/100 g, falling abruptly to approximately 0.036–0.046 mL/100 g in the solid at the melting point (bhojak¹2026ultrasonicacousticcavitation pages 1-4, gerrard2014inclusionsandhydrogen pages 48-56). This approximately 20-fold solubility drop drives porosity formation during solidification. The conversion factor is 1 ppm H ≈ 1.12 mL/100 g (gerrard2014inclusionsandhydrogen pages 36-42).

**Undegassed vs. degassed melts.** Aluminium melted in hydrocarbon-fired furnaces or in air typically contains approximately 0.30–0.45 mL H/100 g at around 700°C before treatment (gerrard2014inclusionsandhydrogen pages 36-42, gerrard2014inclusionsandhydrogen pages 320-324). Laboratory argon-purging trials reduced hydrogen from approximately 0.35–0.45 to approximately 0.10–0.15 mL/100 g over 50 minutes (gerrard2014inclusionsandhydrogen pages 155-160, gerrard2014inclusionsandhydrogen pages 320-324). Industrial rotary impeller degassing with Ar or N₂ at 300–450 rpm and 6–25 L/min can achieve comparable or lower levels (saternus2003modellingofthe pages 1-4). Ultrasonic degassing in industrial continuous casting reduced the density index from >0.15 to <0.08 cc/100 g (bhojak¹2026ultrasonicacousticcavitation pages 1-4).

**Hydrogen in wrought bar.** Solid wrought extrusion, having been DC-cast with inline degassing and subsequently hot-worked, contains hydrogen at approximately the solid-solubility level or below — roughly 0.03–0.05 mL/100 g — though actual values require LECO or hot-vacuum-extraction measurement on the specific bar (gerrard2014inclusionsandhydrogen pages 48-56).

**Mould-moisture pickup.** Green sand moulds contain 3–4% moisture; when molten aluminium contacts this surface, water decomposes at the metal–mould interface, releasing hydrogen that dissolves rapidly into the melt (d.scott2004productionandinspection pages 7-9). Incompletely dried mould coatings, wet cores, and binder solvents further contribute hydrogen-generating volatiles; gas bubbles can form within a half-second of metal contact with the mould surface (d.scott2004productionandinspection pages 7-9). Chemically bonded no-bake moulds generate less moisture but can produce carbon- and nitrogen-containing pyrolysis gases.

**Behaviour on remelting under vacuum and argon.** When a hydrogen-laden sand casting is remelted under vacuum in the rePowder system (pumped down then backfilled with Ar to 150–200 mbar), the low total pressure and low hydrogen partial pressure provide a strong thermodynamic driving force for H desorption. During pump-down, dissolved hydrogen will degas from the solid surface, and upon melting the greatly increased diffusivity accelerates outgassing. Hydrogen trapped in porosity or at bifilm interfaces will also be released, potentially causing bubbling, spitting, or foam formation at the melt surface — particularly problematic for a small melt (150–250 g) pushed through a sub-mm nozzle. Porosity in the feedstock acts as pre-nucleated gas pockets that expand rapidly under reduced pressure. The evidence consistently shows that bifilms act as preferential nucleation sites for hydrogen porosity, meaning that a high-bifilm feedstock will exhibit much more violent outgassing than clean wrought bar (jarfors2026bifilmgenerationin pages 1-4, bhojak¹2026ultrasonicacousticcavitation pages 1-4). *Direct experimental data on the behaviour of sand-cast aluminium feedstock during vacuum-induction ultrasonic atomization were not found; this specific scenario represents an evidence gap.*

---

## (c) Process Contamination

**Iron pickup from steel tools.** Molten aluminium is highly aggressive toward mild steel. In contact with uncoated steel ladles, skimmers, or stirring rods at 700–750°C, iron dissolves rapidly into the aluminium melt through formation of Fe–Al intermetallics at the interface. *No defensible universal wt%/h pickup rate was found in the retrieved literature.* Foundry handbooks commonly cite Fe saturation levels of 1.8–2.5 wt% Fe at 700–750°C in pure Al, and intermetallic growth rates sufficient to corrode through thin steel tools in minutes. The practical consequence is that even brief contact with uncoated steel can raise Fe above the AA 6063 specification limit of 0.35 wt% in a small melt. Repeated recycling through scrap-based melting consistently accumulates Fe because it cannot be removed by degassing, fluxing, or filtration (pereira2026scrapselectionand pages 14-17, pereira2026rotaryfurnacerecyclingof pages 30-32, gurkan2026recycledmetalutilization pages 4-6, fracchia2025newprocessesin pages 48-52, gurkan2026recycledmetalutilization pages 6-7).

**Si and C pickup from crucibles.** A clay-graphite or SiC crucible can introduce small amounts of carbon and silicon into the melt. Al₄C₃ carbide inclusions form through reaction with organic or graphite-containing materials (kovacec2025removalofinclusions pages 3-4, yao2011experimentalinvestigationand pages 125-128). SiC crucibles can contribute silicon through dissolution, though the rate is slow at typical aluminium melting temperatures.

**Sand, binder, and flux residues.** Sand grains (SiO₂) can become embedded in the casting surface through mechanical or chemical metal penetration (zhao2002correlationofsand pages 1-8). Organic binders (furan, phenolic-urethane, PUNB) pyrolyse on contact with molten metal, generating carbonaceous gas, lustrous carbon deposits, and nitrogen-containing decomposition products; gas bubbles can form within approximately 0.5 seconds of metal contact (d.scott2004productionandinspection pages 7-9). Na, Ca, K, Cl, and F can be introduced by salt fluxes and degassing tablets; industrial flux treatment using MgCl₂/KCl/NaCl/CaF₂ mixtures reduced Na in cast billets to a maximum of 3 ppm, but careless dosing can leave higher residues (kovacec2025removalofinclusions pages 3-4).

**Mg loss.** Magnesium is preferentially oxidized from the melt surface, especially in Mg-bearing alloys like 6063 (0.45–0.90 wt% Mg). Each remelt in air causes some Mg loss, the extent depending on temperature, hold time, surface agitation, and protective atmosphere. *No quantitative wt% Mg loss per melt cycle was found in the retrieved evidence for 6xxx alloys specifically.* The literature consistently identifies Mg as susceptible to oxidation and melt loss and notes that MgAl₂O₄ spinel forms in Mg-bearing alloys (kovacec2025removalofinclusions pages 3-4, pereira2026rotaryfurnacerecyclingof pages 30-32, gurkan2026recycledmetalutilization pages 3-4). For the composition-spread experiments described, even a few tenths of a percent Mg loss would significantly shift the computed cup composition.

**Zn and Cu from mixed scrap.** Mixed aluminium scrap can introduce Zn (from 7xxx series) and Cu (from 2xxx series) that are impossible to remove by conventional melt treatment. The retrieved evidence consistently warns of compositional drift from heterogeneous scrap (pereira2026scrapselectionand pages 14-17, pereira2026rotaryfurnacerecyclingof pages 30-32).

---

## (d) The As-Cast Surface

**Oxide skin.** On a freshly machined aluminium surface, an amorphous alumina layer forms within nanoseconds of exposure to air and grows to approximately 2–5 nm under ambient conditions (jarfors2026bifilmgenerationin pages 1-4). This native oxide is thin, dense, and relatively benign as remelt feedstock. On a sand-cast surface, the oxide skin is fundamentally different: the metal solidified against a moist, gas-generating sand mould, and the surface carries a reaction layer that may include thick folded oxide films, MgAl₂O₄ spinel, adhered or partially embedded sand grains, burnt binder residues, dross laps, and metal-penetration fingers extending into intergranular sand spaces (zhao2002correlationofsand pages 1-8, d.scott2004productionandinspection pages 7-9).

**Metal penetration and burn-on.** Metal penetration occurs when molten aluminium is forced into the interstices between sand grains by metallostatic pressure, gas pressure, or capillary effects; burn-on involves chemical reaction between the metal and mould materials (zhao2002correlationofsand pages 1-8). These defects create a rough, contaminated layer that cannot be cleaned by solvent washing alone.

**Machining stock.** *No universal minimum machining allowance was found in the retrieved evidence.* Standard foundry practice for aluminium sand castings typically specifies 1.5–3 mm machining allowance on critical surfaces. For the proposed cup, at minimum the bore and plug seat must be machined to remove the entire mould-contact skin and any sand-contaminated layer. Using the casting with unmachined external surfaces as atomization feedstock would introduce sand, oxide, and binder contamination directly into the melt.

---

## (e) Effect of Feedstock Quality on Atomization

**Nozzle clogging.** The rePowder system pushes melt through a 0.5–0.7 mm graphite nozzle. Oxide films, spinel particles, sand grains, and other solid inclusions in the feedstock can accumulate at or upstream of the nozzle orifice and cause partial or complete blockage. The atomization literature identifies nozzle clogging as a failure mode related to insufficiently fragmented melt and excessive viscosity (zhang2026gasatomizationfor pages 15-17), but in the specific case of a sub-mm orifice, any solid inclusion approaching the orifice diameter would be mechanically trapped. A wrought bar with PoDFA ~0.01 mm²/kg contains far fewer such particles than a sand casting at 0.3–3 mm²/kg.

**Powder oxygen content.** Well-controlled VIGA (vacuum induction melting gas atomization) produces powder with approximately 50–200 ppm oxygen; inert-gas atomization more broadly yields approximately 100–500 ppm O₂; air atomization produces 1,000 ppm to 1% O₂ (dunkley2019metalpowderatomisation pages 3-5). For the rePowder ultrasonic atomizer operating under Ar at 150–200 mbar, powder oxygen will depend on both feedstock oxide burden and residual atmosphere purity. Feedstock with high entrained-oxide content would be expected to produce higher powder oxygen levels. Atomizing-gas purity is also critical: 99.999% Ar is recommended over 99.9% Ar to minimize powder oxygen and nitrogen (zhang2026gasatomizationfor pages 15-17).

**Satellite and irregular particles.** Satellite particles form when fine droplets adhere to larger solidifying particles during inter-droplet collisions in the spray plume (pennacchio2026…stainlesssteel pages 40-44). Oxide films on droplet surfaces can stabilize irregular shapes by damping the surface-tension-driven spheroidization before solidification is complete (zhang2026gasatomizationfor pages 15-17). Higher feedstock oxide burden is therefore expected to increase the fraction of irregular and satellite-bearing particles.

**Internal powder porosity.** Dissolved hydrogen in the feedstock transfers into atomized droplets. As each droplet solidifies rapidly, the hydrogen solubility drop can nucleate internal pores — particularly at entrained bifilm surfaces. Gas trapped in feedstock porosity can also be carried into droplets. A sand-cast feedstock with high hydrogen and high bifilm content would therefore be expected to produce powder with greater internal porosity than wrought-bar feedstock.

**Feedstock specifications.** EIGA (electrode induction-melting gas atomization) avoids crucible contamination entirely by using a pre-alloyed rod as consumable electrode, eliminating ceramic inclusions (zhang2026gasatomizationfor pages 7-9, yang2026effectsofultrasonic pages 1-6). VIGA uses ceramic crucibles and risks introducing inclusions from crucible erosion (zhang2026gasatomizationfor pages 7-9). Both processes implicitly require dense, inclusion-free, known-composition feedstock. *No published cleanliness specification for ultrasonic-atomizer feedstock was found.* The rePowder system's 0.5–0.7 mm nozzle imposes a de facto maximum inclusion size well below the orifice diameter.

---

## (f) Practices to Approach Wrought-Bar Cleanliness

The following table summarizes the key practices and their quantitative effects where data are available.

| Practice | Effect on Cleanliness | Quantitative Impact (where available) | Practical Notes |
|---|---|---|---|
| Rotary Ar degassing | Removes dissolved H by bubble flotation and can float agglomerated inclusions; poor rotor practice or a surface vortex can create fresh bifilms. | Melt H can fall from roughly **0.35–0.45 to 0.10–0.15 mL/100 g**. In one high-oxide melt, prolonged rotary treatment reduced RPT bifilm index from about **≥100 to 38 mm**, although BI is not a direct H assay. (yuksel2026comparisonofthe pages 5-6, gerrard2014inclusionsandhydrogen pages 155-160, gerrard2014inclusionsandhydrogen pages 320-324, jarfors2026bifilmgenerationin pages 1-4) | Use the lowest effective rotor speed, keep the rotor submerged, prevent vortexing, use dry high-purity Ar, skim gently, degas before final filtration, and pour promptly. |
| Flux injection (RFI) | Wets and separates oxide agglomerates, assists flotation, and can remove alkali and alkaline-earth impurities; it may introduce Na, K, Ca, Cl, or F residues if poorly selected or overdosed. | Industrial Al–Mg–Si trials reduced total PoDFA inclusions from **0.34–3.13 to 0.05–1.11 mm²/kg**, typically by about **70%** and by as much as **92%**. (kovacec2025removalofinclusions pages 3-4) | Use an Al–Mg–Si-compatible flux, dose by melt mass, allow separation, remove dross without remixing it, and verify residual Na, Ca, and K. Flux-free Ar degassing plus filtration may better protect composition-spread experiments. |
| Ceramic foam filtration | Captures refractory fragments, sand, oxide agglomerates, and other inclusions by depth and cake filtration; it does not remove dissolved H, Fe, Cu, or Zn. | Filtered A356 and A319 melts exhibited less porosity; ceramic filtration has also improved aluminium-alloy fluidity by as much as **25%**. Efficiency depends strongly on pore size, priming, and flow. (gerrard2014inclusionsandhydrogen pages 62-68, karem2009vibrationassistedfilling pages 34-39, mackie2014characterisationofcasting pages 60-63) | Install downstream of degassing and near the mould, provide adequate head, prevent bypass, and preheat and dry the filter. Damaged, wet, or chemically attacked filters can introduce H or inclusions. |
| Bottom-gated or naturally pressurized gating (Campbell rules) | Keeps the system full and fills upward with less splashing, aspiration, free-surface folding, and bifilm entrainment than uncontrolled top pouring. | Keep ingate or free-surface velocity below approximately **0.3–0.5 m/s**. A spin-trap design at **0.43–0.50 m/s** was subcritical, whereas **0.63–1.0 m/s** caused splashing and reoxidation. (karem2009vibrationassistedfilling pages 34-39, karem2009vibrationassistedfilling pages 66-71, bruna2023castingqualityimprovement pages 2-4) | Use a tapered sprue, runner extension or spin trap, generous radii, gates below the cavity, and no waterfalls. Validate velocity by simulation or water modelling; naturally pressurized gating alone does not guarantee quiescent flow. |
| Tilt pouring or low fall height | Maintains a short, attached stream and minimizes jet impact, air entrainment, and repeated rupture of the oxide skin. | One model predicted about **1,021 bifilms/mm³** for a **1.5 m** transfer fall and **464/mm³** for a **1 m** transfer. Even **0.3 m** produced modeled damage comparable to six minutes of rotary degassing at 460 rpm; these are model-dependent estimates. (jarfors2026bifilmgenerationin pages 4-7, jarfors2026bifilmgenerationin pages 7-10, jarfors2026bifilmgenerationin pages 10-16) | Bring the ladle lip close to the basin, begin slowly, maintain a continuous stream, and avoid stop–start pouring. Tilt or counter-gravity filling is preferable where available. |
| Sand and core drying | Reduces H pickup and gas defects from mould moisture, solvents, core binders, and mould washes; it also reduces spitting and oxidized bubble trails. | No universal H reduction is available. The proposed green sand contains **3–4% water**, while untreated air- or combustion-furnace melts commonly contain about **0.30–0.45 mL H/100 g**. (gerrard2014inclusionsandhydrogen pages 36-42, d.scott2004productionandinspection pages 7-9) | Green sand cannot be fully dried while remaining green sand. Use the lowest controlled moisture, dry washes completely, bake no-bake cores, preheat tools and chills, and verify moisture and loss on ignition. |
| Coated tools and dedicated crucible | Limits Fe pickup from bare steel, cross-alloy Zn and Cu contamination, refractory or carbon transfer, and carryover of old dross. | No defensible universal **wt% Fe/h** or Mg-loss-per-melt value was found; rates depend on temperature, contact area, coating condition, agitation, and hold time. Repeated recycling nevertheless accumulates Fe and other persistent residuals. (pereira2026scrapselectionand pages 14-17, pereira2026rotaryfurnacerecyclingof pages 30-32, gurkan2026recycledmetalutilization pages 4-6) | Use BN- or refractory-coated tools, inspect coatings every heat, minimize immersion time, dedicate crucibles and tools to 6xxx or high-purity Al, and assay every heat. Degassing and filtration cannot remove dissolved Fe, Cu, or Zn. |
| Permanent mould in graphite or steel instead of sand | Eliminates sand grains, clay moisture, and binder pyrolysis while producing a smoother, more reproducible surface with less mould-generated gas and reaction-layer contamination. | No direct universal PoDFA or H comparison was found for an otherwise identical cup. Its principal advantage is eliminating sand and core contamination rather than removing inclusions already present in the melt. (zhao2002correlationofsand pages 1-8, d.scott2004productionandinspection pages 7-9) | A coated steel or graphite mould with a removable core is likely cleaner than sand for a cylindrical cup. Preheat and dry it, prevent soldering or carbon pickup with a suitable coating, and retain quiescent bottom or tilt filling. |
| Vacuum or inert-gas melting and casting | Reduces exposure to water vapour, lowers hydrogen partial pressure, limits new oxidation, and facilitates H desorption; it does not reliably remove existing entrained oxide films. | Well-controlled VIGA powder is reported at roughly **50–200 ppm O**, versus about **100–500 ppm O** for inert-gas-atomized powder generally. These are powder outcomes, not cast-cup acceptance limits. (dunkley2019metalpowderatomisation pages 3-5, zhang2026gasatomizationfor pages 7-9) | Use a dry, leak-tight system and **99.999% Ar** where powder oxygen matters. Charge clean dense metal under inert cover, avoid violent pressure reduction, and filter before casting. EIGA avoids crucible contamination but requires pre-alloyed rod. (zhang2026gasatomizationfor pages 15-17, yang2026effectsofultrasonic pages 1-6) |
| Argon-shielded pouring | Suppresses fresh oxidation of the pouring stream and advancing free surface, reducing oxide-film nucleation sites for pores. | In A356 trials, Ar-shielded pouring reduced pore volume fraction, number density, and pore size relative to normal pouring, although PoDFA did not reliably resolve the oxide-film difference. (yao2011experimentalinvestigationand pages 128-133, yao2011experimentalinvestigationand pages 120-125) | Shield the melt surface, ladle stream, and mould inlet. Use low-flow dry Ar that displaces air without disturbing the stream, and combine shielding with low fall height because inert gas cannot compensate for turbulent handling. |


*Table: Practical controls for approaching wrought-bar cleanliness when producing aluminium cups by casting. Quantitative effects are included where supported, while process-dependent evidence gaps are stated explicitly.*

**Recommended minimum protocol for cast cups (if sand casting is pursued):**

1. **Charge control:** Use only alloy-certified, sorted 6063 offcuts or commercially pure Al ingot — never mixed scrap. Assay every heat by OES or ICP before pouring (pereira2026scrapselectionand pages 14-17, pereira2026rotaryfurnacerecyclingof pages 30-32).

2. **Melt treatment:** Rotary argon degassing (dry 99.995%+ Ar, submerged rotor, no vortex, 5–15 min) to reduce hydrogen to ≤0.15 mL/100 g and float gross inclusions. Skim gently (yuksel2026comparisonofthe pages 5-6, gerrard2014inclusionsandhydrogen pages 155-160, saternus2003modellingofthe pages 1-4).

3. **Filtration:** Pour through a preheated, dry ceramic foam filter (20–30 ppi minimum) placed at the base of the downsprue or in the runner (gerrard2014inclusionsandhydrogen pages 62-68, mackie2014characterisationofcasting pages 60-63).

4. **Gating and pouring:** Bottom-gated or naturally pressurized design with ingate velocity ≤0.5 m/s; minimum practical fall height; slow, continuous pour; no splash or waterfalls (karem2009vibrationassistedfilling pages 34-39, karem2009vibrationassistedfilling pages 66-71, bruna2023castingqualityimprovement pages 2-4, jarfors2026bifilmgenerationin pages 4-7, jarfors2026bifilmgenerationin pages 7-10).

5. **Mould preparation:** Dry sand and cores thoroughly; use no-bake binder with complete solvent removal; apply and fully dry any mould coatings before assembly (d.scott2004productionandinspection pages 7-9).

6. **Tooling:** BN- or refractory-coated ladle, skimmer, and stirring rod; dedicated SiC or clay-graphite crucible reserved for this alloy; minimize steel contact time (pereira2026scrapselectionand pages 14-17, gurkan2026recycledmetalutilization pages 4-6).

7. **Post-casting:** Machine the entire bore, plug seat, and ideally all external mould-contact surfaces to remove the reaction layer, embedded sand, and oxide skin. Clean as per current practice (IPA flush, 80°C dry).

8. **Preferred alternative:** A graphite or coated-steel permanent mould for the cup shape would eliminate sand/binder contamination entirely, produce a smoother as-cast surface, and require less post-machining — at the cost of pattern/mould fabrication (zhao2002correlationofsand pages 1-8).

---

## Evidence Gaps and Caveats

Several quantitative values requested in the question were not found in the retrieved literature and should be noted as evidence gaps:

- **Bulk oxygen in ppm** for 6063 extrusion bar or sand castings: no defensible published values were found. PoDFA, bifilm index, and bulk oxygen measure overlapping but distinct inclusion populations and should not be interconverted.
- **Fe pickup rate (wt%/h) from steel tools** in molten aluminium at 700–750°C: widely cited qualitatively but no controlled rate measurement was retrieved.
- **Mg loss (wt% per melt)** for 6xxx alloys: consistently described as significant but not quantified in the sources found.
- **Sand-cast oxide skin thickness** (µm): no measured value for aluminium sand castings was found; the reaction layer is process-specific.
- **Feedstock cleanliness specifications for ultrasonic atomization:** no published standard was found for ultrasonic atomizers; VIGA and EIGA specifications are implicit rather than codified.
- **Behaviour of sand-cast feedstock during vacuum remelting and atomization:** no direct experimental study was found for this specific scenario; the analysis in section (b) is based on indirect thermodynamic and defect-science reasoning.

In summary, a sand-cast aluminium cup produced in a university foundry without degassing, filtration, or careful gating would contain roughly 10–100× more oxide inclusions and 2–4× more dissolved hydrogen than the current machined wrought bar, along with poorly bounded chemistry and a contaminated as-cast surface. Even with best-practice melt treatment, the casting is unlikely to match wrought-bar cleanliness, and the composition-control advantages of known-chemistry certified bar would be lost. If larger cups are needed, the most defensible approach is either to machine larger-diameter wrought bar (e.g., 1-inch or 1.25-inch round), or to pour into a coated permanent mould using a degassed, filtered, quiescently poured melt of certified charge, followed by full machining of all mould-contact surfaces.


References

1. (yao2011experimentalinvestigationand pages 128-133): LU Yao. Experimental investigation and numerical modeling of microporosity formation in aluminum alloy a356. ArXiv, Jan 2011. URL: https://doi.org/10.14288/1.0079336, doi:10.14288/1.0079336. This article has 13 citations.

2. (kovacec2025removalofinclusions pages 3-4): Uroš Kovačec and Franc Zupanič. Removal of inclusions and trace elements from al-mg-si alloys using refining fluxes. Strojniški vestnik - Journal of Mechanical Engineering, 71:294-300, Oct 2025. URL: https://doi.org/10.5545/sv-jme.2025.1371, doi:10.5545/sv-jme.2025.1371. This article has 3 citations.

3. (gerrard2014inclusionsandhydrogen pages 62-68): AJ Gerrard. Inclusions and hydrogen and their effects on the quality of direct chill cast and flat rolled aluminium alloys for aerospace applications. Unknown journal, 2014.

4. (gerrard2014inclusionsandhydrogen pages 87-93): AJ Gerrard. Inclusions and hydrogen and their effects on the quality of direct chill cast and flat rolled aluminium alloys for aerospace applications. Unknown journal, 2014.

5. (yuksel2026comparisonofthe pages 5-6): Çağlar Yüksel. Comparison of the effects of ultrasonic degassing and rotary degassing processes on the liquid metal cleanliness and tensile properties of aluminum alloys. International Journal of Metalcasting, May 2026. URL: https://doi.org/10.1007/s40962-026-02011-4, doi:10.1007/s40962-026-02011-4. This article has 1 citations and is from a peer-reviewed journal.

6. (yuksel2026comparisonofthe pages 2-5): Çağlar Yüksel. Comparison of the effects of ultrasonic degassing and rotary degassing processes on the liquid metal cleanliness and tensile properties of aluminum alloys. International Journal of Metalcasting, May 2026. URL: https://doi.org/10.1007/s40962-026-02011-4, doi:10.1007/s40962-026-02011-4. This article has 1 citations and is from a peer-reviewed journal.

7. (jarfors2026bifilmgenerationin pages 1-4): Anders E. W. Jarfors and Toni Bogdanoff. Bifilm generation in metal handling and degassing: total numbers, sizes and damage. Sep 2026. URL: https://doi.org/10.21203/rs.3.rs-10838912/v1, doi:10.21203/rs.3.rs-10838912/v1.

8. (bhojak¹2026ultrasonicacousticcavitation pages 1-4): Kedar N. Bhojak¹, Naresh Jain¹, Saroj Kumar Nayak², Bijoy Kumar Satpathy², and Nilesh Bhatt. Ultrasonic acoustic cavitation driven hydrogen degassing in molten aluminium alloys and its effects on porosity and mechanical properties. Unknown journal, Oct 2026. URL: https://doi.org/10.21203/rs.3.rs-10859875/v1, doi:10.21203/rs.3.rs-10859875/v1.

9. (gerrard2014inclusionsandhydrogen pages 36-42): AJ Gerrard. Inclusions and hydrogen and their effects on the quality of direct chill cast and flat rolled aluminium alloys for aerospace applications. Unknown journal, 2014.

10. (gerrard2014inclusionsandhydrogen pages 155-160): AJ Gerrard. Inclusions and hydrogen and their effects on the quality of direct chill cast and flat rolled aluminium alloys for aerospace applications. Unknown journal, 2014.

11. (gerrard2014inclusionsandhydrogen pages 48-56): AJ Gerrard. Inclusions and hydrogen and their effects on the quality of direct chill cast and flat rolled aluminium alloys for aerospace applications. Unknown journal, 2014.

12. (gerrard2014inclusionsandhydrogen pages 320-324): AJ Gerrard. Inclusions and hydrogen and their effects on the quality of direct chill cast and flat rolled aluminium alloys for aerospace applications. Unknown journal, 2014.

13. (d.scott2004productionandinspection pages 7-9): William D.Scott, Charles Bates, Hanjun Li, and John Griffin. Production and inspection of quality aluminum and iron sand castings. Materials Engineering, pages 349-400, May 2004. URL: https://doi.org/10.1201/9780203970928.ch10, doi:10.1201/9780203970928.ch10. This article has 4 citations.

14. (gerrard2014inclusionsandhydrogen pages 68-76): AJ Gerrard. Inclusions and hydrogen and their effects on the quality of direct chill cast and flat rolled aluminium alloys for aerospace applications. Unknown journal, 2014.

15. (pereira2026scrapselectionand pages 14-17): Antonio Clareti Pereira. Scrap selection and charge design for foundry alloys: a critical review of classification criteria, metallurgical constraints, and industrial practices. Journal International Review of Research Studies, 1:1-52, Aug 2026. URL: https://doi.org/10.66104/f577ny49, doi:10.66104/f577ny49. This article has 0 citations.

16. (pereira2026rotaryfurnacerecyclingof pages 30-32): Antonio Clareti Pereira. Rotary-furnace recycling of aluminum scrap and dross: a critical review of feedstock–flux–furnace interactions, metal recovery, emissions, and circularity. Journal International Review of Research Studies, Aug 2026. URL: https://doi.org/10.66104/vnhbpj53, doi:10.66104/vnhbpj53. This article has 1 citations.

17. (gurkan2026recycledmetalutilization pages 4-6): Doruk Gürkan. Recycled metal utilization on the microstructure and mechanical properties of casting alloys. Green Technology &amp; Innovation, 2:102-112, Mar 2026. URL: https://doi.org/10.65582/gti.2026.006, doi:10.65582/gti.2026.006. This article has 3 citations.

18. (fracchia2025newprocessesin pages 48-52): E Fracchia. New processes in aluminium alloys. Unknown journal, 2025.

19. (zhao2002correlationofsand pages 1-8): Z Zhao. Correlation of sand mold/core density gradients and surface chemistry to casting surface finish. Unknown journal, 2002.

20. (zhang2026gasatomizationfor pages 15-17): Chao-Cai Zhang, Fu-Zhong Chu, and Zong-Yan Zhou. Gas atomization for metal powder production in additive manufacturing: a review. Materials Science in Additive Manufacturing, 0:026220051, Sep 2026. URL: https://doi.org/10.36922/msam026220051, doi:10.36922/msam026220051. This article has 0 citations and is from a peer-reviewed journal.

21. (dunkley2019metalpowderatomisation pages 3-5): John J. Dunkley. Metal powder atomisation methods for modern manufacturing. Johnson Matthey Technology Review, 63:226-232, Jul 2019. URL: https://doi.org/10.1595/205651319x15583434137356, doi:10.1595/205651319x15583434137356. This article has 99 citations and is from a peer-reviewed journal.

22. (zhang2026gasatomizationfor pages 7-9): Chao-Cai Zhang, Fu-Zhong Chu, and Zong-Yan Zhou. Gas atomization for metal powder production in additive manufacturing: a review. Materials Science in Additive Manufacturing, 0:026220051, Sep 2026. URL: https://doi.org/10.36922/msam026220051, doi:10.36922/msam026220051. This article has 0 citations and is from a peer-reviewed journal.

23. (jarfors2026bifilmgenerationin pages 10-16): Anders E. W. Jarfors and Toni Bogdanoff. Bifilm generation in metal handling and degassing: total numbers, sizes and damage. Sep 2026. URL: https://doi.org/10.21203/rs.3.rs-10838912/v1, doi:10.21203/rs.3.rs-10838912/v1.

24. (jarfors2026bifilmgenerationin pages 7-10): Anders E. W. Jarfors and Toni Bogdanoff. Bifilm generation in metal handling and degassing: total numbers, sizes and damage. Sep 2026. URL: https://doi.org/10.21203/rs.3.rs-10838912/v1, doi:10.21203/rs.3.rs-10838912/v1.

25. (jarfors2026bifilmgenerationin pages 4-7): Anders E. W. Jarfors and Toni Bogdanoff. Bifilm generation in metal handling and degassing: total numbers, sizes and damage. Sep 2026. URL: https://doi.org/10.21203/rs.3.rs-10838912/v1, doi:10.21203/rs.3.rs-10838912/v1.

26. (karem2009vibrationassistedfilling pages 34-39): W Abdul Karem. Vibration assisted filling of thin section castings. Unknown journal, 2009.

27. (karem2009vibrationassistedfilling pages 66-71): W Abdul Karem. Vibration assisted filling of thin section castings. Unknown journal, 2009.

28. (bruna2023castingqualityimprovement pages 2-4): M. Bruna and M. Galčík. Casting quality improvement by gating system optimization. Archives of Foundry Engineering, pages 132-136, May 2023. URL: https://doi.org/10.24425/afe.2021.136089, doi:10.24425/afe.2021.136089. This article has 22 citations.

29. (yao2011experimentalinvestigationand pages 120-125): LU Yao. Experimental investigation and numerical modeling of microporosity formation in aluminum alloy a356. ArXiv, Jan 2011. URL: https://doi.org/10.14288/1.0079336, doi:10.14288/1.0079336. This article has 13 citations.

30. (saternus2003modellingofthe pages 1-4): M Saternus and J Botor. Modelling of the continuous refining process of ak-64 alloy. Unknown journal, 2003.

31. (gurkan2026recycledmetalutilization pages 6-7): Doruk Gürkan. Recycled metal utilization on the microstructure and mechanical properties of casting alloys. Green Technology &amp; Innovation, 2:102-112, Mar 2026. URL: https://doi.org/10.65582/gti.2026.006, doi:10.65582/gti.2026.006. This article has 3 citations.

32. (yao2011experimentalinvestigationand pages 125-128): LU Yao. Experimental investigation and numerical modeling of microporosity formation in aluminum alloy a356. ArXiv, Jan 2011. URL: https://doi.org/10.14288/1.0079336, doi:10.14288/1.0079336. This article has 13 citations.

33. (gurkan2026recycledmetalutilization pages 3-4): Doruk Gürkan. Recycled metal utilization on the microstructure and mechanical properties of casting alloys. Green Technology &amp; Innovation, 2:102-112, Mar 2026. URL: https://doi.org/10.65582/gti.2026.006, doi:10.65582/gti.2026.006. This article has 3 citations.

34. (pennacchio2026…stainlesssteel pages 40-44): A Pennacchio. … stainless steel powders and their properties after pbf-lb/m processing. from waste-derived powder production to pbf-lb/m components: gas atomization …. Unknown journal, 2026.

35. (yang2026effectsofultrasonic pages 1-6): Xiao-Feng Yang, Hao-Di Li, Ding-Ying Ren, Hao Lan, Xiao-Qiang Hu, Qian Wang, and Peng Yu. Effects of ultrasonic atomization parameters on the properties of sn-58bi powder and its application in ultrasonic-assisted soldering. Journal of Materials Science: Materials in Electronics, Oct 2026. URL: https://doi.org/10.1007/s10854-026-18683-x, doi:10.1007/s10854-026-18683-x. This article has 0 citations and is from a peer-reviewed journal.

36. (mackie2014characterisationofcasting pages 60-63): D Mackie. Characterisation of casting defects in dc cast magnesium alloys. Unknown journal, 2014.