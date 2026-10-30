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

QUESTION 2 (metal quality after casting, and fitness for this purpose). For the same proposal:
(a) castability of AA 6063 and other wrought 6xxx alloys in sand moulds compared with casting
alloys (A356, 4047 / Al-12Si) and commercially pure Al: fluidity, hot-tearing susceptibility,
shrinkage porosity, freezing range;
(b) as-cast microstructure and properties of sand-cast 6063 or pure Al relative to extruded
6063-T5/T52: grain size, secondary dendrite arm spacing, Mg2Si and beta-AlFeSi intermetallics,
macro- and microsegregation, density, yield strength and ductility;
(c) whether a thin-walled (1.5-3 mm) sand-cast aluminium cup can take a press-fit plug with
0.013-0.020 mm interference without cracking or leaking, given its porosity and lower yield
strength; how gas and shrinkage porosity affect sealing and leak tightness of thin walls;
(d) achievable dimensional tolerances and surface roughness for small sand castings and for
alternatives (gravity permanent-mould casting in graphite or steel, investment casting,
lost-foam), and what machining would still be needed for a press fit;
(e) whether cups cast from re-melted 6063 stay within AA 6063 composition limits (Mg, Fe, Si,
Cu, Zn) and how many remelt cycles it takes to drift out;
(f) other ways to make larger aluminium containers for powder (tube with welded or press-fit
end plugs, impact-extruded or deep-drawn 1xxx/3xxx cans, larger-diameter bar, canning or
compacting powder into a can as in powder-metallurgy HIP canning) and how they compare on
oxide and hydrogen content and on effort.
Give numbers with citations, and say plainly where the evidence is thin or only indirect.

## Metal Quality After Casting and Fitness for Ultrasonic Atomizer Charge Cups

### (a) Castability of AA 6063 and Other Wrought 6xxx Alloys Versus Casting Alloys and Commercially Pure Al

The castability of an aluminium alloy for sand moulds is governed primarily by its fluidity, hot-tearing susceptibility, freezing (solidification) range, and shrinkage-porosity tendency. These parameters differ dramatically between wrought Al–Mg–Si (6xxx) alloys and casting Al–Si alloys.

**Fluidity.** Silicon is the principal contributor to fluidity in aluminium alloys because its high latent heat slows solidification and keeps the alloy liquid longer during mould filling (tripathy2022studyofmicrostructure pages 29-31). CALPHAD-calculated kinematic viscosities at 680 °C show that Al–Mg alloy families have much higher viscosity (lower fluidity) than Al–Si10 systems; AlSi10MnMg compositions exhibit the minimum viscosity (highest fluidity) among the investigated variant sets (asghar2025developmentofnew pages 9-10). Wrought alloys such as 6063, with only ~0.2–0.6 wt% Si and ~0.45–0.9 wt% Mg, contain far less silicon than the ~7 wt% Si of A356 or the ~12 wt% Si of AA 4047. This means 6063 will have substantially poorer mould-filling ability, especially in thin-walled sand-cast cups. Al–Si casting alloys are characterised as having high fluidity and short freezing ranges, making them suitable for complex, thin-walled, leak-proof castings (sumanUnknownyeartheeffectsof pages 5-8). Commercially pure aluminium has moderate fluidity—better than 6063 owing to its near-zero freezing range—but is rarely sand cast because of its high pouring superheat, large solidification contraction, and absence of a fluid eutectic.

**Hot-tearing susceptibility.** Alloys with wide thermal freezing ranges are more susceptible to hot tearing than those with short ranges (asghar2025developmentofnew pages 11-12, asghar2025developmentofnew pages 10-11). For 6xxx alloys, hot-tearing susceptibility is non-monotonic with Si and Mg content; peak susceptibility has been observed at approximately 0.10–0.25 wt% Si and 0.1–0.2 wt% Mg, but remains significant across the 6063 composition range (giansante2026influenceofintermetallic pages 1-2). The type of iron intermetallic is critical: plate-like β-Al₅FeSi disrupts interdendritic feeding and promotes crack initiation, whereas Chinese-script α-Al₁₅(Fe,Mn)₃Si₂ strengthens the solid skeleton and improves resistance (giansante2026influenceofintermetallic pages 4-6). In constrained-rod casting tests, 6xxx alloys showed complete ball-end separation—a hallmark of severe hot tearing—in the longest rods (giansante2026influenceofintermetallic pages 4-6). A356 and Al–12Si, by contrast, have a late-solidification fluid second phase that heals incipient tears and compensates for solidification stresses (tripathy2022studyofmicrostructure pages 29-31).

**Freezing range.** The overall solidification range (T_liq – T_sol) under non-equilibrium conditions was calculated by Asghar et al. (2025) for Al–Mg and Al–Si alloy sets. Al–Mg-dominated sets (SET 1–2, analogous to dilute Al–Mg–Si wrought alloys) showed the widest total ranges, approximately 180–260 °C, whereas AlSi10MnMg sets showed approximately 50–75 °C (asghar2025developmentofnew pages 11-12). The thermal freezing range in the critical 95–99.5% solid fraction interval was also widest for the Al–Mg alloys (asghar2025developmentofnew pages 11-12). For near-eutectic Al–12Si (4047), the freezing range is extremely narrow—approximately 5–20 °C—making it exceptionally resistant to hot tearing. Commercially pure Al freezes over a near-zero range (depending on impurity level).

**Shrinkage porosity.** Volumetric solidification shrinkage calculated for the Al–Si10 systems was approximately 6.3–6.7%, whereas the Al–Mg systems showed approximately 7.0–8.1% (asghar2025developmentofnew pages 10-11). The Al–Si eutectic also forms a low-melting liquid phase that feeds shrinkage regions late in solidification, further reducing porosity risk (tripathy2022studyofmicrostructure pages 29-31). A 6063-type alloy, with minimal eutectic liquid, freezes with extensive dendritic mushy zones that impede feeding and promote distributed microporosity.

The following table summarises the castability comparison:

| Alloy | Approx. freezing range (°C) | Relative fluidity | Hot-tearing susceptibility | Shrinkage-porosity tendency | Suitability for sand casting | Key qualification |
|---|---:|---|---|---|---|---|
| AA 6063 (Al–Mg–Si wrought) | ~35–50 | Poor | High | High | Poor | Low Si gives poorer filling than foundry Al–Si alloys; a prolonged mushy stage impedes feeding. Plate-like β-Al₅FeSi can obstruct interdendritic flow and initiate tears, while Mg oxidation and hydrogen/oxide defects add risk. The numerical range is an approximate phase-diagram estimate, not direct thin-cup test data. (sumanUnknownyeartheeffectsof pages 5-8, giansante2026influenceofintermetallic pages 1-2, giansante2026influenceofintermetallic pages 4-6) |
| Commercially pure Al (1xxx) | ~0–10, depending on purity | Fair | Low | Moderate–high | Fair | Its narrow freezing interval reduces hot tearing, but high pouring temperature, large solidification contraction, modest strength, and absence of a fluid Al–Si eutectic make sound thin sections difficult. Evidence specific to 1.5–3 mm hand-poured sand cups is thin. (sumanUnknownyeartheeffectsof pages 5-8, tripathy2022studyofmicrostructure pages 29-31) |
| A356 (Al–7Si–0.3Mg casting alloy) | ~50–65 | Good | Low–moderate | Moderate | Good | Designed for casting: Si improves flow and late interdendritic liquid assists feeding. Nevertheless, slow sand-mould cooling, hydrogen, bifilms, and inadequate risering can still produce substantial porosity; un-degassed sand-cast examples showed coarse grains, Fe intermetallics, and large pores. (tripathy2022studyofmicrostructure pages 29-31, mckenna2010gravityandcentrifugal pages 131-137, mckenna2010gravityandcentrifugal pages 126-131, dispinar2010degassinghydrogenand pages 1-3) |
| AA 4047 / Al–12Si (near-eutectic) | ~5–20 | Excellent | Very low | Low–moderate | Good | Closest to the Al–Si eutectic, so it has the shortest practical freezing interval, best thin-section filling, and least hot-tearing tendency of these choices. It remains vulnerable to hydrogen, oxide bifilms, and isolated shrinkage if melt treatment or feeding is poor. (sumanUnknownyeartheeffectsof pages 5-8, tripathy2022studyofmicrostructure pages 29-31, asghar2025developmentofnew pages 9-10) |


*Table: Comparison of alloy-family behavior for thin sand-cast cups. Freezing ranges are approximate phase-diagram values; the strongest direct evidence supports the relative ranking—6063 is the least forgiving, while near-eutectic Al–12Si is the most castable.*

**Summary for part (a).** AA 6063 is among the worst aluminium alloys for sand casting: low fluidity, wide freezing range, high hot-tearing susceptibility, and poor feeding. A356 and especially Al–12Si (4047) are far more castable. Commercially pure Al is intermediate—narrow freezing range and low hot-tearing risk, but poor fluidity for thin sections and high shrinkage.

---

### (b) As-Cast Microstructure and Properties of Sand-Cast 6063 or Pure Al Relative to Extruded 6063-T5/T52

**Grain size and SDAS.** Sand-cast aluminium alloys solidify slowly, producing coarse columnar and equiaxed grain structures. In sand-cast A356 (a proxy for slow solidification of an Al–Si alloy), microstructures contain coarse grains, plate-like silicon eutectic, and iron intermetallics (mckenna2010gravityandcentrifugal pages 126-131). SDAS in sand castings is large and reflects the slow cooling rate; finer SDAS is associated with higher mechanical properties and ductility, and smaller, less elongated silicon particles (mckenna2010gravityandcentrifugal pages 131-137). For comparison, one study of a grain-refined 6063 alloy cast near the liquidus reported equiaxed crystals of approximately 22 µm (Zhang et al., 2022). Extruded 6063-T5/T52 bar, by contrast, has a fibrous or fine recrystallised grain structure with grains typically in the range of 10–50 µm depending on extrusion parameters and T5/T6 temper, and no dendritic structure at all.

**Intermetallics and phases.** In as-cast 6063, the primary second phases are Mg₂Si and iron-bearing intermetallics—either needle/plate-like β-Al₅FeSi or, if Mn is present, Chinese-script α-Al₁₅(Fe,Mn)₃Si₂ (giansante2026influenceofintermetallic pages 1-2, giansante2026influenceofintermetallic pages 4-6). Sand-cast structures allow these intermetallics to grow to larger sizes, reducing ductility. In extruded and tempered 6063, hot working fragments and distributes intermetallics, and the T5/T52 age-hardening treatment produces a fine Mg₂Si precipitate distribution that strengthens the matrix. The β-Al₅FeSi phase is particularly detrimental in castings: it acts as a stress concentrator and disrupts interdendritic feeding (giansante2026influenceofintermetallic pages 4-6).

**Macro- and microsegregation.** Slow sand-mould solidification produces significant microsegregation (coring) within dendrite arms. In 6063, Mg and Si segregate to interdendritic regions and grain boundaries, producing coarse Mg₂Si and eutectic. Extruded bar is homogenised before extrusion, eliminating most as-cast segregation.

**Density and porosity.** Extruded 6063 bar is fully dense (ρ ≈ 2.69 g/cm³). Sand castings—especially those made without rotary degassing—contain hydrogen porosity and shrinkage porosity. Hydrogen solubility in liquid aluminium is approximately 0.69 ppm (0.69 mL/100 g) just above the liquidus, dropping to approximately 0.04 ppm in the solid—a ratio of about 17:1 (islam2010effectofsurface pages 34-39). Un-degassed melts leaving a gas-fired furnace at ~700 °C typically contain approximately 0.3–0.4 mL H₂/100 g Al (gerrard2014inclusionsandhydrogen pages 36-42). In sand moulds, slow cooling gives hydrogen ample time to diffuse and form interdendritic pores (mckenna2010gravityandcentrifugal pages 131-137, dispinar2006determinationofmetal pages 35-39). Moisture from green-sand moulds (3–4% water) further elevates hydrogen pickup via the reaction 2 Al + 3 H₂O → Al₂O₃ + 3 H₂ (dispinar2006determinationofmetal pages 23-27). Porosity in un-degassed sand castings can readily reach 1–5% by volume, reducing effective density and creating leak paths.

**Mechanical properties.** Sand-cast A356 (as-cast, un-modified, un-degassed, silica-sand mould) exhibited UTS of approximately 93–102 MPa and elongation of about 0.89%, compared with approximately 130–150 MPa for properly melt-treated sand-cast A356 (mckenna2010gravityandcentrifugal pages 131-137, mckenna2010gravityandcentrifugal pages 112-115). Yield strength was not explicitly reported but is typically 60–80% of UTS for as-cast A356, i.e. approximately 70–120 MPa. By comparison, the optimised sand-cast A356 with degassing reached UTS of 215 MPa, YS of 165 MPa, and elongation of 5.8% after proper treatment and gating optimisation (Arif et al., 2026). Extruded 6063-T5 typically provides YS ≈ 110–150 MPa, UTS ≈ 150–186 MPa, and elongation ≈ 8–12%, far exceeding as-cast properties. Sand-cast 6063 without heat treatment would likely show YS ≈ 50–90 MPa, UTS ≈ 90–130 MPa, and elongation ≈ 2–5%, though direct data on sand-cast 6063 are very scarce because it is not a casting alloy.

---

### (c) Press-Fit Feasibility in Thin-Walled Sand-Cast Cups

The question is whether a 1.5–3 mm sand-cast aluminium wall can sustain a press-fit plug with 0.013–0.020 mm interference without cracking or leaking.

**Mechanical feasibility.** The hoop stress generated by the interference fit on a thin cylindrical wall of inner radius *r* and thickness *t* is approximately σ_hoop ≈ (δ/2r) × E × (r/t), where δ is interference and E is Young's modulus (~70 GPa for Al). For r ≈ 8 mm, t ≈ 1.5 mm, δ ≈ 0.015 mm, this gives approximately 35 MPa—modest compared to the YS of wrought 6063-T5 (~130 MPa) but potentially close to or exceeding the YS of as-cast, porous 6063 or pure Al (~50–90 MPa). Moreover, sand-cast walls are unlikely to be uniform: local thin spots, porosity concentrations, and surface-intersecting defects create stress raisers that can initiate cracking at stresses well below the bulk yield strength.

**Porosity and leak tightness.** This is the critical concern. Porosity in aluminium castings is a major cause of leak failures (islam2010effectofsurface pages 34-39). In sand moulds without degassing, hydrogen-related microporosity and shrinkage porosity form interdendritic networks that can connect through a 1.5–3 mm wall (mckenna2010gravityandcentrifugal pages 131-137, dispinar2006determinationofmetal pages 35-39). Even in high-quality HPDC aluminium compressor parts produced with gas-tightness requirements, interconnected porosity networks consisting of cavities connected by capillary-like channels cause leakage that persists even after vacuum resin impregnation (reger2024impregnationproblemsof pages 3-6, reger2023detectionofporosity pages 2-3, reger2023detectionofporosity pages 1-2). Modelling shows that capillary channels below approximately 28 µm can prevent reliable gas-tightness after impregnation (reger2024modellingtheimpregnation pages 1-2), and sections with capillary radii below ~4 µm allow less than 1% resin saturation (reger2024impregnationproblemsof pages 6-9). Even impregnated, mass-produced AlSi9Cu3(Fe) die castings leaked during helium inspection (reger2023detectionofporosity pages 2-3).

Sand castings have substantially more porosity—and coarser porosity—than HPDC parts. A 1.5–3 mm sand-cast wall will almost certainly contain through-wall leak paths when poured from an un-degassed melt into a moist green-sand mould. Press fitting a plug into such a wall applies additional mechanical deformation that can open or interconnect porosity at the bore surface, as machining and thread forming are known to expose previously sealed internal networks (reger2024impregnationproblemsof pages 3-6, reger2024impregnationproblemsof pages 1-3).

**Verdict.** A thin-walled sand-cast aluminium cup made under the proposed conditions (no degassing, moist sand, wrought alloy) is very unlikely to achieve the seal quality needed to prevent loose-powder losses and oxide pickup during the atomiser's vacuum-argon cycle. The combination of low yield strength, high porosity, and through-wall leak risk makes the press-fit plug approach impractical for thin sand-cast walls. A thicker wall (≥5 mm) from a properly degassed melt might be adequate if the bore is machined, but this sacrifices the volume advantage of a thin-walled cup.

---

### (d) Dimensional Tolerances and Surface Roughness

The following table compares achievable tolerances and roughness for the relevant casting processes applied to small aluminium parts:

| Process | Typical tolerance (mm) | Surface roughness Ra (μm) | Minimum practical wall (mm) | Indicative IT grade | Machining needed for 0.013–0.020 mm press fit |
|---|---:|---:|---:|---|---|
| Green sand casting | About ±0.4 for a small casting; size- and process-dependent | 10–15 | 3–5 typical; 1.5–3 is high-risk | Approximately IT15–IT16 | Mandatory: bore or ream the plug seat; leave machining allowance and inspect wall thickness and porosity. (campbell2000theconceptof pages 6-8, mckenna2010gravityandcentrifugal pages 39-42) |
| Chemically bonded sand or no-bake | Roughly ±0.25–0.5; tooling and core control dominate | Approximately 6–15; evidence is indirect | About 2.5–4; 1.5–3 requires optimized processing | Approximately IT14–IT16 | Mandatory: machine the bore and seat in one setup; an as-cast core cannot reliably produce the required diameter and roundness. (campbell2000theconceptof pages 6-8, mckenna2010gravityandcentrifugal pages 39-42) |
| Gravity permanent mould, graphite or steel | ±0.1–0.2 | 1.6–3.2 | About 5 routinely; thinner walls require specialized design | Approximately IT11–IT14; direct IT evidence is limited | Mandatory: finish-bore or ream the seat; casting repeatability remains far wider than the 0.007 mm interference range. (sassu2023preventionofcasting pages 25-29, campbell2000theconceptof pages 6-8) |
| Investment casting or lost wax | About ±0.13 per 25 mm; ±0.10 possible for dimensions up to 13 mm | 1.5–3.0 | About 1.0 for light alloys | Approximately IT14–IT16 in cited rapid-pattern examples | Mandatory: finish-machine and inspect the seat despite its near-net capability. (greenspikesley1979investmentcasting pages 3-4, greenspikesley1979investmentcasting pages 2-3, mckenna2010gravityandcentrifugal pages 39-42) |


*Table: Comparison of realistic dimensional and surface capabilities for small aluminium castings. Every process still requires finish machining of the plug seat because the specified 0.013–0.020 mm interference is much tighter than normal as-cast variation.*

For a good aluminium sand-casting process, the probable dimensional variability is approximately ±0.04% of casting length; for a 70 mm cup, this translates to roughly ±0.03 mm for dimensional features—but this is the best achievable in controlled production (campbell2000theconceptof pages 6-8). Typical green-sand casting practice is much worse. Investment casting achieves ±0.13 mm per 25 mm on general dimensions, with ±0.10 mm possible for small features up to 13 mm, and surface roughness of 1.5–3.0 µm (greenspikesley1979investmentcasting pages 3-4, greenspikesley1979investmentcasting pages 2-3). Gravity permanent-mould casting achieves approximately ±0.1–0.2 mm with surface finish of 1.6–3.2 µm (sassu2023preventionofcasting pages 25-29). In one study, precision sand castings were found to be more than twice as accurate as standard gravity-die castings for aluminium cylinder heads (campbell2000theconceptof pages 6-8).

**Practical implication.** A press fit with 0.013–0.020 mm interference requires bore dimensional control to approximately ±0.005 mm—far tighter than any casting process can deliver. Therefore, **the bore and plug seat must be machined regardless of the casting method**. The casting process determines only the outer geometry, wall thickness, and amount of stock to be removed. Sand casting saves little if the bore must be machined anyway, and introduces porosity and composition risks that do not exist with wrought bar.

---

### (e) Composition Stability of Remelted 6063

AA 6063 has relatively tight composition limits: Mg 0.45–0.9, Si 0.20–0.6, Fe ≤ 0.35, Cu ≤ 0.10, Mn ≤ 0.10, Zn ≤ 0.10 wt% (approximate per ASTM/AA registration). The key concerns during remelting are magnesium loss and iron pickup.

**Magnesium loss.** Magnesium tends to "fade" during melting because it reacts readily with oxygen and moisture in the atmosphere to form MgO and spinel (MgAl₂O₄) (wangombe2022developmentofrecycled pages 120-125, wangombe2022developmentofrecycleda pages 120-125). The extent of Mg loss depends strongly on operating conditions—temperature, atmosphere, residence time, salt or flux chemistry, and the physical form of the scrap (pereira2026rotaryfurnacerecyclingof pages 30-32). In a university foundry melting in air without protective flux or cover gas, Mg oxidation will be aggressive. Quantitative per-cycle Mg loss data for 6063 under these specific conditions were not found in the retrieved literature; however, one study of recycled Al closest to 6063 (batch B) contained only 0.238% Mg compared with the 6063 specification minimum of 0.45% (wangombe2022developmentofrecycled pages 120-125), indicating that Mg depletion can drop the alloy well below specification after even a single careless air remelt. The narrow 6063 Mg window (0.45–0.9 wt%) means that a loss of even ~0.1–0.2 wt% Mg—plausible in a single extended air melt—can push the alloy out of specification.

**Iron pickup.** Iron cannot be removed from aluminium once incorporated (wangombe2022developmentofrecycled pages 120-125, wangombe2022developmentofrecycleda pages 120-125). Sources of iron contamination include iron fasteners mixed with scrap, handling equipment such as ladles, and crucible/furnace materials. The 6063 Fe limit of 0.35 wt% is relatively strict. Each remelt cycle in a university foundry using steel ladles, tongs, or contaminated crucibles will incrementally raise Fe. Iron promotes detrimental β-Al₅FeSi intermetallics that reduce ductility, castability, and extrudability. Mitigation through rapid cooling, Mn additions (Mn:Fe ≈ 2:1), or dilution with primary Al is possible but adds complexity (wangombe2022developmentofrecycled pages 120-125).

**How many remelts before drifting out of specification.** Direct evidence is thin. Under well-controlled industrial conditions with flux cover, inert atmosphere, and master-alloy makeup additions, many remelt cycles are possible. Under the proposed university conditions (air melt, no flux, no degassing, scrap handling), a single remelt could drop Mg below specification and begin significant Fe accumulation. Without chemical analysis after each melt and compensating additions, the cups cannot be assumed to remain within AA 6063 composition limits.

---

### (f) Alternative Methods for Making Larger Aluminium Containers

The following table compares practical alternatives:

| Container route | Alloy options | Relative oxide / H₂ burden | Effort / cost at university scale | Expected seal quality | Key advantages and disadvantages |
|---|---|---|---|---|---|
| Machined from larger bar | Certified 6063-T5/T52; optionally composition-matched 6xxx or certified 1xxx bar | **Low**: wrought stock avoids a local remelt and its associated hydrogen, bifilms, sand, dross, and flux residues | **Low–moderate**: familiar process, but increasing bore volume raises material removal and swarf | **Excellent** after machining and plug validation | Best compositional traceability, density, concentricity, surface finish, and continuity with existing mass-balance calculations. Main penalties are bar cost, machining time, and wasted material. |
| Tube with welded or press-fit end plugs | Seamless 6063/6061 tube; 1xxx or 3xxx tube if its contribution is included in the composition calculation; matching plugs | **Low** for press-fit assembly; **low–moderate** for welding because oxide cleaning is needed and aluminium weld metal can develop hydrogen porosity | **Low–moderate**: cut tube, make plugs, clean, assemble; welding adds fixtures, shielding gas, qualification, and post-cleaning | **Good–excellent** with machined seats and two plugs; welded closure can be excellent if qualified | Uses little machining and provides wrought, dense walls. A press-fit bottom needs axial retention and leak testing; welding adds a heat-affected zone, oxide disturbance, filler-metal chemistry, and possible hydrogen porosity. Solid-state joining would reduce fusion porosity; optimized FSW aluminium joints have been reported leak-tight to 32 bar, versus 23–25 bar for TIG in one indirect comparison (reger2024impregnationproblemsof pages 3-6, islam2010effectofsurface pages 34-39). |
| Impact-extruded 1xxx/3xxx can | Typically AA1050/1070 or Al99.5/99.7; suitably annealed 3003/3004/3104-type alloys | **Low** in the finished seamless wrought wall; recycled slug production still requires melt cleaning and degassing | **High** for tooling and press setup, but **low per piece** at volume | **Excellent** for the integral bottom; only the top closure must be developed | Seamless containers can undergo over 80% reduction. Reported walls span roughly 0.003–0.080 in (0.076–2.03 mm); tested containers had about 0.20–0.36 mm walls and 23–32 bar burst pressure. Pure 1xxx has the best formability; 3xxx needs optimized annealing. Commercial tooling is disproportionate for a small experimental program (javidani2024processingtechniquesand pages 12-14, javidani2024processingtechniquesand pages 27-29, kores2016developmentofaluminium pages 1-2, javidani2024processingtechniquesand pages 4-5). |
| Deep-drawn / drawn-and-ironed can | Commonly 3003, 3004, 3104, 3105, or other annealed 1xxx/3xxx sheet | **Low**: wrought sheet and no fusion joint in the body; surface lubricants and coatings must be removed completely | **High** for dies and multiple drawing/ironing stages; economical mainly when outsourced or produced in quantity | **Excellent** for the integral bottom; **good–excellent** after a machined or formed top closure | Produces seamless, thin, dense walls and large volumes with little metal. Published bottle routes use approximately 0.146–0.203 mm cylindrical walls and can use high-recycled-content 3xxx sheet. Draw ratio, ironing, earing, trimming, annealing, and cleaning make in-house development unattractive for a few cups (javidani2024processingtechniquesand pages 10-12). |
| Sand casting (proposed) | Remelted 6063; commercially pure Al; preferably A356 or near-eutectic Al–12Si if casting quality dominates | **High** under the proposed air-melting, moist-sand, hand-pour, no-degassing conditions: elevated hydrogen, oxide bifilms, dross, sand/core debris, and shrinkage porosity are credible | **Moderate–high** after mould/core making, gating and risering development, fettling, machining, inspection, rejects, and chemistry control | **Poor–fair** for a 1.5–3 mm wall unless process development and leak testing are extensive | Can make a larger cavity with little stock removal, but 6063 has poor casting robustness and cast walls can contain interconnected leak paths. Even high-quality die castings may leak after resin impregnation when narrow pore channels prevent complete filling; machining can expose previously closed networks (giansante2026influenceofintermetallic pages 1-2, reger2024impregnationproblemsof pages 3-6, reger2023detectionofporosity pages 2-3, reger2024impregnationproblemsof pages 6-9, reger2024modellingtheimpregnation pages 1-2). |
| PM/HIP-style evacuated canning | Usually weldable mild or stainless steel in cited practice; aluminium tube/can is conceivable but requires an aluminium-specific welding and degassing procedure | **Low internal gas** after proper evacuation and bakeout; powder surface oxide remains and the can itself must be clean and leak-tight | **High**: fill tube, settling, welded lid and evacuation stem, vacuum system, heated degassing, stem pinch-off, and leak verification | **Excellent** when correctly fabricated, but unnecessarily elaborate for a cup that will simply be remelted | Provides the most controlled powder atmosphere and a documented route to very high consolidated density. A cited procedure purged three times with purified Ar, evacuated to about 10⁻¹ mbar with a rotary pump or as low as 5×10⁻⁵ mbar with diffusion pumping, heated during degassing, and crimp-sealed the evacuation tube. The evidence is for steel cans containing titanium powder, so transfer to aluminium charge cups is indirect (meng2008thepreparationof pages 56-61, meng2008thepreparationof pages 72-76, meng2008thepreparationof pages 85-90). |


*Table: Comparison of practical routes for larger powder-containing cups, emphasizing melt cleanliness, sealing reliability, and implementation effort. Wrought seamless or machined routes avoid the hydrogen, bifilm, porosity, and compositional-control risks inherent to the proposed student sand-casting process.*

**Larger-diameter bar (simplest approach).** Scaling up from 19 mm (3/4 in) to 25 mm (1 in) or 32 mm (1-1/4 in) extruded 6063 round bar directly increases the bore diameter and powder capacity with no process change. Certified bar stock provides known composition, full density, and wrought microstructure with no additional hydrogen, oxide, or porosity risk. The only limitation is bar availability and the cost of machining a larger blind bore.

**Tube with welded or press-fit end plugs.** Seamless 6063 or 6061 tube in appropriate OD and wall thickness can be cut to length. One end can be sealed by a press-fit or TIG-welded plug, filled with powder, and closed with the vent-hole plug. This approach provides wrought wall quality with minimal machining. FSW-welded aluminium joints have been demonstrated to remain leak-tight to 32 bar (reger2024impregnationproblemsof pages 3-6). The weld or press-fit at the closed end must be qualified for seal quality.

**Impact-extruded 1xxx/3xxx cans.** Impact extrusion produces seamless thin-walled containers from punched aluminium slugs, typically AA1050/1070 (99.5%/99.7% Al) or 3xxx alloys (javidani2024processingtechniquesand pages 2-4, kores2016developmentofaluminium pages 1-2, kores2016developmentofaluminium pages 2-4). The process commonly achieves wall thicknesses of 0.003–0.080 in (0.08–2 mm) and container heights of 1.8–11 in (46–280 mm) (javidani2024processingtechniquesand pages 4-5). Burst pressures of 23–32 bar have been reported (javidani2024processingtechniquesand pages 12-14). However, impact extrusion requires specialised tooling and presses, making it impractical for a small university program making a few cups. Commercially available impact-extruded cans or tubes (e.g., aerosol can bodies, ~38 mm diameter) could potentially be repurposed if the 1xxx/3xxx alloy contribution to the final melt composition is acceptable.

**Deep-drawn 1xxx/3xxx cans.** Similar to impact extrusion but using sheet/strip as feedstock. DWI (draw-wall-iron) processes can produce containers up to 750 mL using at least 90% recycled 3xxx can body stock (javidani2024processingtechniquesand pages 10-12). Wall thicknesses as thin as 0.006–0.020 in (0.15–0.5 mm) are achievable. Again, tooling requirements make this impractical for small-scale university use, but commercial beverage cans could potentially be repurposed.

**PM/HIP-style canning.** For the most controlled powder encapsulation, powder metallurgy practice uses welded metal cans with an attached evacuation tube. The cited procedure loads powder into a mild-steel can, purges three times with purified argon, evacuates to ~10⁻¹ mbar (rotary pump) or ~5 × 10⁻⁵ mbar (diffusion pump), heats at controlled rates to degas surface moisture and hydroxides, and crimp-seals the evacuation tube (meng2008thepreparationof pages 56-61, meng2008thepreparationof pages 72-76, meng2008thepreparationof pages 79-85). This gives excellent atmosphere control but is unnecessarily elaborate for a cup that will simply be remelted. Steel canning also introduces Fe contamination into the Al melt. An aluminium can could be used instead, but developing the welding and degassing procedure adds substantial effort.

**Recommended practical alternative.** For a university program needing larger cups with known composition and clean metal, the simplest and most reliable approach is to source larger-diameter extruded 6063 bar (25–38 mm OD is readily available) and machine the cups with a deeper or wider bore. The second-best option is seamless 6063 tube with machined end plugs. Both approaches avoid the hydrogen, porosity, oxide, composition-drift, and leak-tightness problems inherent to sand casting, and require no new process development.

---

### Summary Assessment

The proposed sand-casting route for atomiser charge cups faces severe obstacles on multiple fronts. AA 6063 is a poor casting alloy with low fluidity, wide freezing range, and high hot-tearing susceptibility (sumanUnknownyeartheeffectsof pages 5-8, giansante2026influenceofintermetallic pages 1-2, asghar2025developmentofnew pages 11-12). Air melting without degassing produces hydrogen-laden metal (gerrard2014inclusionsandhydrogen pages 36-42), and moist green sand further elevates hydrogen uptake via water–aluminium reaction (dispinar2006determinationofmetal pages 23-27). The resulting porosity creates through-wall leak paths in thin walls (reger2024impregnationproblemsof pages 3-6, reger2023detectionofporosity pages 2-3, islam2010effectofsurface pages 34-39), which cannot be reliably sealed even by vacuum resin impregnation (reger2024impregnationproblemsof pages 6-9, reger2024modellingtheimpregnation pages 1-2). Mg loss and Fe pickup during air remelting of 6063 scrap are likely to push composition outside AA 6063 limits within one or two uncontrolled remelt cycles (wangombe2022developmentofrecycled pages 120-125, pereira2026rotaryfurnacerecyclingof pages 30-32). Regardless of casting process, the bore and plug seat must be machined to achieve the required ±0.005 mm interference-fit tolerance (greenspikesley1979investmentcasting pages 3-4, sassu2023preventionofcasting pages 25-29, campbell2000theconceptof pages 6-8), so the net saving from casting versus machining from bar is marginal. Using a casting alloy (A356 or Al–12Si) instead of 6063 would improve castability but would change the cup's chemical contribution to the melt composition—which must be accounted for in the Si composition-spread calculation—and would still not resolve the hydrogen, porosity, and leak-tightness problems without proper melt treatment. **Scaling up via larger-diameter wrought bar or seamless tube remains the most practical, reliable, and compositionally traceable approach.**

References

1. (tripathy2022studyofmicrostructure pages 29-31): S Tripathy. Study of microstructure and mechanical behaviour of aluminium copper alloy for high temperature applications. Unknown journal, 2022.

2. (asghar2025developmentofnew pages 9-10): Osama Asghar, Mattia Franceschi, Paolo Ferro, and Franco Bonollo. Development of new aluminium alloys for future automotive structural components with less criticality and higher casting processability. International Journal of Metalcasting, 20:2215-2237, Aug 2025. URL: https://doi.org/10.1007/s40962-025-01715-3, doi:10.1007/s40962-025-01715-3. This article has 15 citations and is from a peer-reviewed journal.

3. (sumanUnknownyeartheeffectsof pages 5-8): S Suman and VC Jha. The effects of pressure on the mechanical properties and microstructure of die cast aluminium alloys. Unknown journal, Unknown year.

4. (asghar2025developmentofnew pages 11-12): Osama Asghar, Mattia Franceschi, Paolo Ferro, and Franco Bonollo. Development of new aluminium alloys for future automotive structural components with less criticality and higher casting processability. International Journal of Metalcasting, 20:2215-2237, Aug 2025. URL: https://doi.org/10.1007/s40962-025-01715-3, doi:10.1007/s40962-025-01715-3. This article has 15 citations and is from a peer-reviewed journal.

5. (asghar2025developmentofnew pages 10-11): Osama Asghar, Mattia Franceschi, Paolo Ferro, and Franco Bonollo. Development of new aluminium alloys for future automotive structural components with less criticality and higher casting processability. International Journal of Metalcasting, 20:2215-2237, Aug 2025. URL: https://doi.org/10.1007/s40962-025-01715-3, doi:10.1007/s40962-025-01715-3. This article has 15 citations and is from a peer-reviewed journal.

6. (giansante2026influenceofintermetallic pages 1-2): Emidio Giansante, Alberto Fabrizi, and Giulio Timelli. Influence of intermetallic phases and grain refinement on hot-tearing susceptibility in 6xxx-series aluminum alloys. International Journal of Metalcasting, Aug 2026. URL: https://doi.org/10.1007/s40962-026-02098-9, doi:10.1007/s40962-026-02098-9. This article has 1 citations and is from a peer-reviewed journal.

7. (giansante2026influenceofintermetallic pages 4-6): Emidio Giansante, Alberto Fabrizi, and Giulio Timelli. Influence of intermetallic phases and grain refinement on hot-tearing susceptibility in 6xxx-series aluminum alloys. International Journal of Metalcasting, Aug 2026. URL: https://doi.org/10.1007/s40962-026-02098-9, doi:10.1007/s40962-026-02098-9. This article has 1 citations and is from a peer-reviewed journal.

8. (mckenna2010gravityandcentrifugal pages 131-137): N McKenna. Gravity and centrifugal casting of light metal alloys using rapidly produced sand moulds. Unknown journal, 2010.

9. (mckenna2010gravityandcentrifugal pages 126-131): N McKenna. Gravity and centrifugal casting of light metal alloys using rapidly produced sand moulds. Unknown journal, 2010.

10. (dispinar2010degassinghydrogenand pages 1-3): D. Dispinar, S. Akhtar, A. Nordmark, M. Di Sabatino, and L. Arnberg. Degassing, hydrogen and porosity phenomena in a356. Materials Science and Engineering A-structural Materials Properties Microstructure and Processing, 527:3719-3725, Jun 2010. URL: https://doi.org/10.1016/j.msea.2010.01.088, doi:10.1016/j.msea.2010.01.088. This article has 206 citations.

11. (islam2010effectofsurface pages 34-39): MA Islam. Effect of surface porosity on tribological properties of automotive al-si alloys. Unknown journal, 2010.

12. (gerrard2014inclusionsandhydrogen pages 36-42): AJ Gerrard. Inclusions and hydrogen and their effects on the quality of direct chill cast and flat rolled aluminium alloys for aerospace applications. Unknown journal, 2014.

13. (dispinar2006determinationofmetal pages 35-39): D Dispinar. Determination of metal quality of aluminium and its alloys. Unknown journal, 2006.

14. (dispinar2006determinationofmetal pages 23-27): D Dispinar. Determination of metal quality of aluminium and its alloys. Unknown journal, 2006.

15. (mckenna2010gravityandcentrifugal pages 112-115): N McKenna. Gravity and centrifugal casting of light metal alloys using rapidly produced sand moulds. Unknown journal, 2010.

16. (reger2024impregnationproblemsof pages 3-6): M. Réger, R. Horváth, ER Fábian, and T. Réti. Impregnation problems of aluminum castings. IOP Conference Series: Materials Science and Engineering, 1313:012007, Sep 2024. URL: https://doi.org/10.1088/1757-899x/1313/1/012007, doi:10.1088/1757-899x/1313/1/012007. This article has 0 citations.

17. (reger2023detectionofporosity pages 2-3): Mihály Réger, József Gáti, Ferenc Oláh, Richárd Horváth, Enikő Réka Fábián, and Tamás Bubonyi. Detection of porosity in impregnated die-cast aluminum alloy piece by metallography and computer tomography. Crystals, 13:1014, Jun 2023. URL: https://doi.org/10.3390/cryst13071014, doi:10.3390/cryst13071014. This article has 9 citations.

18. (reger2023detectionofporosity pages 1-2): Mihály Réger, József Gáti, Ferenc Oláh, Richárd Horváth, Enikő Réka Fábián, and Tamás Bubonyi. Detection of porosity in impregnated die-cast aluminum alloy piece by metallography and computer tomography. Crystals, 13:1014, Jun 2023. URL: https://doi.org/10.3390/cryst13071014, doi:10.3390/cryst13071014. This article has 9 citations.

19. (reger2024modellingtheimpregnation pages 1-2): Mihály Réger, Richárd Horváth, Enikő Réka Fábián, and Tamás Réti. Modelling the impregnation of a pressure-tight casting. International Journal of Metalcasting, 19:165-175, Mar 2024. URL: https://doi.org/10.1007/s40962-024-01272-1, doi:10.1007/s40962-024-01272-1. This article has 4 citations and is from a peer-reviewed journal.

20. (reger2024impregnationproblemsof pages 6-9): M. Réger, R. Horváth, ER Fábian, and T. Réti. Impregnation problems of aluminum castings. IOP Conference Series: Materials Science and Engineering, 1313:012007, Sep 2024. URL: https://doi.org/10.1088/1757-899x/1313/1/012007, doi:10.1088/1757-899x/1313/1/012007. This article has 0 citations.

21. (reger2024impregnationproblemsof pages 1-3): M. Réger, R. Horváth, ER Fábian, and T. Réti. Impregnation problems of aluminum castings. IOP Conference Series: Materials Science and Engineering, 1313:012007, Sep 2024. URL: https://doi.org/10.1088/1757-899x/1313/1/012007, doi:10.1088/1757-899x/1313/1/012007. This article has 0 citations.

22. (campbell2000theconceptof pages 6-8): J. Campbell. The concept of net shape for castings. Materials & Design, 21:373-380, Aug 2000. URL: https://doi.org/10.1016/s0261-3069(99)00072-2, doi:10.1016/s0261-3069(99)00072-2. This article has 88 citations and is from a highest quality peer-reviewed journal.

23. (mckenna2010gravityandcentrifugal pages 39-42): N McKenna. Gravity and centrifugal casting of light metal alloys using rapidly produced sand moulds. Unknown journal, 2010.

24. (sassu2023preventionofcasting pages 25-29): N Sassu. Prevention of casting defects in an aluminum alloy component. Unknown journal, 2023.

25. (greenspikesley1979investmentcasting pages 3-4): E. Green-Spikesley. Investment casting. International Journal of Materials in Engineering Applications, 1:328-334, Dec 1979. URL: https://doi.org/10.1016/0141-5530(79)90012-8, doi:10.1016/0141-5530(79)90012-8. This article has 12 citations.

26. (greenspikesley1979investmentcasting pages 2-3): E. Green-Spikesley. Investment casting. International Journal of Materials in Engineering Applications, 1:328-334, Dec 1979. URL: https://doi.org/10.1016/0141-5530(79)90012-8, doi:10.1016/0141-5530(79)90012-8. This article has 12 citations.

27. (wangombe2022developmentofrecycled pages 120-125): DN Wang'ombe. Development of recycled friendly aluminium alloys for automotive and structural applications. Unknown journal, 2022.

28. (wangombe2022developmentofrecycleda pages 120-125): DN Wang'ombe. Development of recycled friendly aluminium alloys for automotive and structural applications. Unknown journal, 2022.

29. (pereira2026rotaryfurnacerecyclingof pages 30-32): Antonio Clareti Pereira. Rotary-furnace recycling of aluminum scrap and dross: a critical review of feedstock–flux–furnace interactions, metal recovery, emissions, and circularity. Journal International Review of Research Studies, Aug 2026. URL: https://doi.org/10.66104/vnhbpj53, doi:10.66104/vnhbpj53. This article has 1 citations.

30. (javidani2024processingtechniquesand pages 12-14): Mousa Javidani, Siamak Nikzad Khangholi, and Alain Chapdelaine. Processing techniques and metallurgical perspectives and their potential correlation in aluminum bottle manufacturing for sustainable packaging solutions. Crystals, 14:434, May 2024. URL: https://doi.org/10.3390/cryst14050434, doi:10.3390/cryst14050434. This article has 13 citations.

31. (javidani2024processingtechniquesand pages 27-29): Mousa Javidani, Siamak Nikzad Khangholi, and Alain Chapdelaine. Processing techniques and metallurgical perspectives and their potential correlation in aluminum bottle manufacturing for sustainable packaging solutions. Crystals, 14:434, May 2024. URL: https://doi.org/10.3390/cryst14050434, doi:10.3390/cryst14050434. This article has 13 citations.

32. (kores2016developmentofaluminium pages 1-2): Stanislav Kores, Jože Turk, Jožef Medved, and Maja Vončina. Development of aluminium alloys for aerosol cans. Materiali in tehnologije, 50:601-605, Aug 2016. URL: https://doi.org/10.17222/mit.2015.330, doi:10.17222/mit.2015.330. This article has 8 citations and is from a peer-reviewed journal.

33. (javidani2024processingtechniquesand pages 4-5): Mousa Javidani, Siamak Nikzad Khangholi, and Alain Chapdelaine. Processing techniques and metallurgical perspectives and their potential correlation in aluminum bottle manufacturing for sustainable packaging solutions. Crystals, 14:434, May 2024. URL: https://doi.org/10.3390/cryst14050434, doi:10.3390/cryst14050434. This article has 13 citations.

34. (javidani2024processingtechniquesand pages 10-12): Mousa Javidani, Siamak Nikzad Khangholi, and Alain Chapdelaine. Processing techniques and metallurgical perspectives and their potential correlation in aluminum bottle manufacturing for sustainable packaging solutions. Crystals, 14:434, May 2024. URL: https://doi.org/10.3390/cryst14050434, doi:10.3390/cryst14050434. This article has 13 citations.

35. (meng2008thepreparationof pages 56-61): DT MEng. The preparation of titanium alloys and composites via non melt processing. Unknown journal, 2008.

36. (meng2008thepreparationof pages 72-76): DT MEng. The preparation of titanium alloys and composites via non melt processing. Unknown journal, 2008.

37. (meng2008thepreparationof pages 85-90): DT MEng. The preparation of titanium alloys and composites via non melt processing. Unknown journal, 2008.

38. (javidani2024processingtechniquesand pages 2-4): Mousa Javidani, Siamak Nikzad Khangholi, and Alain Chapdelaine. Processing techniques and metallurgical perspectives and their potential correlation in aluminum bottle manufacturing for sustainable packaging solutions. Crystals, 14:434, May 2024. URL: https://doi.org/10.3390/cryst14050434, doi:10.3390/cryst14050434. This article has 13 citations.

39. (kores2016developmentofaluminium pages 2-4): Stanislav Kores, Jože Turk, Jožef Medved, and Maja Vončina. Development of aluminium alloys for aerosol cans. Materiali in tehnologije, 50:601-605, Aug 2016. URL: https://doi.org/10.17222/mit.2015.330, doi:10.17222/mit.2015.330. This article has 8 citations and is from a peer-reviewed journal.

40. (meng2008thepreparationof pages 79-85): DT MEng. The preparation of titanium alloys and composites via non melt processing. Unknown journal, 2008.