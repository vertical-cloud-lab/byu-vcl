# Vacuum / inert atmosphere for AMAZEMET ultrasonic atomization: avoiding molten-metal ejection

This note responds to [issue #104](https://github.com/vertical-cloud-lab/byu-vcl/issues/104)
("Vacuum Hydraulic Powder Press to Avoid Explosions"). The lab was warned that
**compacting metal powder inside an aluminum crucible and then melting it in the
atomizer can eject molten metal** (a violent spatter / "explosion"). The question
raised in the issue comments is what role a **vacuum press** and/or a
**vacuum / inert protective atmosphere** plays, specifically for ultrasonic
atomization runs with the **AMAZEMET rePowder** on the lab's aluminum-based
feedstock (1100 Al wire, Si powder, and AlSi10Mg powder blends; see
[the 100 g mixture note](thermo-calc-100g-mixture-composition.md)).

The literature review below was assembled with Edison Scientific's literature
tooling; sources are listed at the end.

## TL;DR recommendation

1. **Prefer solid feedstock (wire / rod / button) over loose powder or powder
   packed into a crucible.** Solid feed has orders of magnitude less interparticle
   porosity and trapped gas, so it is inherently far less prone to gas-driven
   ejection on melting. The rePowder is designed to accept wire, rods, and buttons
   as well as crucible-melted charges.
2. **If powder must be used, dry and degas it first** (bake ~100-200 degC to
   remove physisorbed moisture; for thorough treatment, aerospace Al powder
   practice vacuum-degasses encapsulated compacts at 450-575 degC for several hours).
3. **A vacuum press helps for the right reason:** evacuating the die / crucible
   before and during compaction removes the interstitial air that would otherwise
   be sealed into the compact and erupt through the first liquid that forms on
   melting. Do **not** pack powder tightly against crucible walls in a way that
   creates closed gas pockets.
4. **Run the atomization under vacuum-purge + high-purity argon, not air.** This
   is exactly what published AMAZEMET rePowder aluminum-alloy work does, and it
   simultaneously improves safety, lowers powder oxygen, and improves sphericity
   and flowability.
5. **Heat gradually and start small.** Ramp through the solidus slowly so trapped
   gas can vent before a continuous liquid skin seals it in; validate each new
   blend at the smallest feasible mass with shielding/remote operation.

## 1. Why melting compacted powder ejects molten metal

The violent spatter when melting compacted aluminum powder comes from the rapid
release of gas that is trapped, adsorbed, or chemically bound in the powder mass:

- **Trapped interstitial gas.** Even a well-compacted pellet retains ~5-15 vol%
  (or more) interparticle porosity. When the first liquid forms it can seal the
  surface, trapping air in internal voids; above the solidus that gas expands
  rapidly and ruptures the thin liquid film, ejecting droplets.
- **Adsorbed moisture and hydrogen.** Aluminum powder surfaces carry an oxide
  film plus hydroxides (chemisorbed water) and physisorbed water. On heating, the
  water desorbs and hydroxides decompose, releasing H2O and hydrogen into the
  melt; water vapor also reacts exothermically with liquid aluminum
  (2 Al + 3 H2O -> Al2O3 + 6 H), generating still more hydrogen and heat.
- **Hydrogen solubility drop.** Hydrogen is the only gas appreciably soluble in
  liquid aluminum: ~0.69 ppm at 660 degC in the liquid vs ~0.039 ppm in the
  solid (roughly an 18x drop at solidification). Hydrogen dissolved on melting is
  forcefully rejected on any local cooling, nucleating bubbles that burst the
  melt surface.
- **Oxide skins.** Each particle is encased in a tenacious Al2O3 shell (~3-20 nm).
  These skins impede coalescence and trap gas pockets that cannot easily vent.
- **Fine-powder amplification.** Fine reactive powders (e.g. AlSi10Mg, <63 um)
  have high specific surface area, so more oxide, more adsorbed moisture, and more
  void volume per unit mass; gas-atomized powder can also carry intra-particle
  pores that release gas on remelting.

## 2. How vacuum / inert compaction mitigates the hazard

- **Vacuum compaction / degassing** removes the air that would otherwise be sealed
  into interparticle voids, and a vacuum-degas step drives off physisorbed and
  chemisorbed water and hydroxides before melting. This is the established reason
  aerospace Al PM billets are vacuum-degassed (450-575 degC, several hours) prior
  to consolidation: to prevent blistering and gas-driven defects.
- **Inert-atmosphere compaction** (dry high-purity argon backfill) replaces
  moisture- and oxygen-bearing air with a gas that does not react with aluminum;
  even if some argon is trapped, it does not generate hydrogen or exothermic
  reactions, greatly reducing the violence of any release.
- **Reduced oxide growth.** Handling under vacuum/inert atmosphere slows oxide-film
  growth and further moisture pickup. Powder atomized after evacuation + UHP
  backfill reached ~800 ppm O vs ~2600-3300 ppm O for commercially air- or
  inert-handled powder.
- **Melt degassing** (rotary inert-gas injection) is the industrial state of the
  art for bulk Al melts, reaching <0.05 ppm dissolved H; the same principle can be
  scaled down for lab melt prep before atomization.

## 3. Ultrasonic atomization: with vs. without vacuum / inert atmosphere

| Condition | Powder oxygen | Particle shape | Flowability | Safety / process |
| --- | --- | --- | --- | --- |
| **Vacuum (~0.133 Pa)** | <0.02 wt% O | perfectly spherical | good | lowest oxidation; thin oxide skin; higher fine-fraction yield |
| **Inert argon** | ~0.02 wt% O (Zn, <63 um) | spherical | 21 s (Zn) | safe, stable for reactive melts |
| **Air** | 0.14 wt% O (Zn); 0.33 wt% O (Sn) | irregular (refractory oxide skins) | 38 s (Zn) | highest oxidation; oxide skins distort particles; worst for reactive metals |

Key points for the AMAZEMET rePowder specifically:

- **Documented rePowder practice for Al alloys** evacuates the chamber to
  ~4x10^-1 mbar and performs at least three argon purge cycles before backfilling
  with argon for induction melting/atomization (Ukabhai et al., Al-Cu). For AMC
  (AlSi9Mg + SiC) atomization on the rePowder, the atomization atmosphere was
  "pure argon, with O2 consistently maintained below 100 ppm" (Jedynak et al.).
- **Quantitative atmosphere effect.** Ultrasonic atomization of zinc in argon gave
  0.02 wt% O vs 0.14 wt% O in air (~7x reduction); tin gave 0.01 vs 0.33 wt% O.
  Vacuum/inert powders were "perfectly spherical," air powders "irregular."
- **Fine-fraction yield.** Lower external (chamber) pressure increased the yield of
  fine powder by facilitating cavitation-driven atomization - useful for the
  sub-63 um fraction wanted for AM.
- **Tradeoffs.** Vacuum/inert operation needs pumps, sealed chambers, and gas
  handling, and argon purity must be controlled. For reactive aluminum alloys the
  safety, powder-quality, and stability benefits strongly favor vacuum/argon over
  air. (AlSi12 ultrasonically atomized under argon scored ~21% higher suitability
  than commercial gas-atomized powder; Yankin et al.)

## 4. Practical recommendations for the lab

| Step | Recommendation | Guidance |
| --- | --- | --- |
| Feedstock form | Prefer wire / rod / button over loose powder or powder-in-crucible | rePowder accepts solid feed; far less trapped interparticle gas |
| Drying | Bake powder, blends, crucibles, tooling before charging | ~100-200 degC bakeout for physisorbed moisture; keep dried powder out of humid air |
| Degassing | Vacuum-degas compacts before full melting when feasible | Aerospace Al PM: 450-575 degC, several hours, encapsulated |
| Compaction | Evacuate die / crucible / chamber before and during pressing ("vacuum press") | rePowder Al work evacuates to ~4x10^-1 mbar before Ar refill; don't seal closed gas pockets |
| Atmosphere | Never melt loose/compacted Al powder in air; vacuum-purge then high-purity Ar | >=3 Ar purge cycles; keep O2 <100 ppm during atomization |
| Melt H control | If making a bulk melt, degas hydrogen before atomizing | Inline Al degassing reaches <0.05 ppm H |
| Heating | Ramp slowly through the solidus, with holds below full melt | Lets trapped gas vent before a continuous liquid seal forms |
| Charge design | If powder is unavoidable, keep pellets vent-able; don't overfill or tightly seal against walls | Avoid closed internal gas reservoirs |
| Operation | Start with the smallest feasible trial mass; use shielding / remote operation until validated | Limits consequence while tuning preheat, vacuum, and Ar procedure |
| Post-processing | Collect and store powder under inert atmosphere | Prevents oxide growth / moisture pickup that degrades AM powder |

**Bottom line for the issue:** a vacuum press is worthwhile *because it removes the
trapped air and moisture that drive the ejection*, but it is only part of the
answer. The biggest single risk reduction is **avoiding loose powder in a crucible
altogether** (use solid feed), and the atomization itself should be run under the
rePowder's documented **vacuum-purge + argon** procedure rather than in air - which
also yields cleaner, more spherical, better-flowing aluminum powder.

## Sources

Researched with Edison Scientific literature tooling.

- Sola & Nouri (2019), *Microstructural porosity in additive manufacturing*,
  J. Adv. Manuf. Process. <https://doi.org/10.1002/amp2.10021>
- Anderson & Foley (2001), *Determining the role of surfaces and interfaces in the
  powder metallurgy processing of aluminum alloy powders*, Surf. Interface Anal.
  31:599-608. <https://doi.org/10.1002/sia.1087>
- Friedrich, Kraeutlein & Krone (2006), *Melt treatment of copper and aluminium -
  the complex step before casting*. <https://doi.org/10.1002/9783527607969.ch1>
- Sheikhaliev & Popel' (1983), *Production of metal powders by ultrasonic
  atomization of melts*, Sov. Powder Metall. Met. Ceram. 22:793-798.
  <https://doi.org/10.1007/bf00790857>
- Jedynak, Haertel & Pippig (2024), *Processability of aluminum-matrix composite
  (AMC) by ultrasonic powder atomization*, Mater. Res. Proc. 41:156-163.
  <https://doi.org/10.21741/9781644903131-17>
- Ukabhai, Mkhonto & Phasha (2025), *Investigation of Al-Cu using different
  preparation methods on the AMAZEMET rePowder machine*, MATEC Web Conf.
  417:03001. <https://doi.org/10.1051/matecconf/202541703001>
- Oezbilen, Uenal & Sheppard (2000), *Influence of atomizing gases on the
  oxide-film morphology and thickness of aluminum powders*, Oxid. Met. 53:1-23.
  <https://doi.org/10.1023/a:1004505728950>
- Yankin et al. (2025), *Effect of ultrasonic atomization parameters on AlSi12
  aluminum powder characteristics for additive manufacturing*, Sci. Rep.
  <https://doi.org/10.1038/s41598-025-06086-7>
- Ciftcli et al. (2025), *Alloy development from sustainable materials - close-loop
  of materials using ultrasonic atomization*, J. Jpn. Soc. Powder Powder Metall.
  72:S729-S735. <https://doi.org/10.2497/jjspm.15e-sis13-03>
