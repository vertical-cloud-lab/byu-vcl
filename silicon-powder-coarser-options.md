# Coarser Silicon Powder Options for Autotrickler

## Background

The current silicon powder sourced from McMaster-Carr (Goodfellow, max. particle size ~45 µm, 99.5% purity) has been causing flow issues in the autotrickler — specifically gumming up and not flowing freely. Finer powders in the sub-50 µm range are prone to:

- **Bridging and arching** at constrictions in the feed path
- **Agglomeration** due to high surface-area-to-volume ratio (van der Waals forces dominate)
- **Electrostatic sticking** to the trickler tube and hopper walls
- **Moisture uptake** via the native SiO₂ oxide layer that forms on silicon surfaces in ambient air

Switching to a coarser particle size in the ~75–150 µm range (−100 +200 mesh) reduces these effects because gravity/inertia start to dominate over adhesive/cohesive surface forces.

---

## Coarser Silicon Powder Options

The following products offer silicon powder in the ~75–150 µm (−100 +200 mesh) range, which should flow substantially better in the autotrickler.

### Option 1 — Thermo Scientific / Fisher Scientific (Alfa Aesar)
- **Product**: Silicon powder, crystalline, −100 +200 mesh, 99.99% (metals basis)
- **Catalog #**: AA4560918 (Fisher Scientific listing) / 045609.18 (Thermo Fisher / Alfa Aesar direct — these are two catalog numbering systems for the same product)
- **Particle size**: ~75–150 µm (−100 +200 mesh)
- **Purity**: 99.99%
- **Sizes available**: 50 g, 250 g
- **Approximate price**: ~$127–$143 / 50 g (institutional pricing may vary)
- **URL**: https://www.fishersci.com/shop/products/silicon-powder-crystalline-100-200-mesh-99-99-metals-basis-thermo-scientific/AA4560918
- **Notes**: High-purity crystalline grade; widely used in research labs; available through BYU's existing Fisher Scientific account.

### Option 2 — Spectrum Chemical
- **Product**: Silicon, 100–200 Mesh, Powder, 98% ACS
- **Catalog #**: S1031
- **Particle size**: ~75–150 µm (−100 +200 mesh)
- **Purity**: 98%
- **Sizes available**: 250 g, 1 kg
- **Approximate price**: ~$208 / 250 g; ~$461–$483 / 1 kg
- **URL**: https://www.spectrumchemical.com/silicon-100-200-mesh-powder-s1031
- **Also available via**: Fisher Scientific (catalog # 18613107), Thomas Scientific, Capitol Scientific
- **Notes**: Lower purity than Alfa Aesar but less expensive per gram for larger quantities; may require special shipping and/or surcharges—check current vendor listing and SDS.

### Option 3 — Sigma-Aldrich / MilliporeSigma
- **Standard offering**: −325 mesh (<44 µm) — not suitable for improved flow
- **Custom sizing**: Contact Sigma-Aldrich bulk/custom division for a coarser mesh fraction (e.g., −100 +200 mesh). Custom or non-standard sizes require a quote request via https://www.sigmaaldrich.com
- **Notes**: Not a standard catalog item at coarser sizes; direct inquiry recommended for bulk quantities.

### Option 4 — Industrial Abrasives Suppliers (e.g., Panadyne, Washington Mills)
- **Product**: Silicon powder in custom mesh sizes
- **Panadyne**: https://panadyne.com/products/
- **Washington Mills**: https://www.washingtonmills.com/contact-us/
- **Notes**: These companies supply industrial-grade ceramic and metallurgical powders. Coarser silicon in 100–500 µm ranges is possible with custom orders, but purity documentation may be less rigorous than lab-chemical suppliers. Best for large-quantity bulk orders if cost is a concern.

### Summary Table

| Supplier | Product | Particle Size | Purity | Price (approx.) | Notes |
|---|---|---|---|---|---|
| Fisher/Thermo Scientific | AA4560918 | 75–150 µm (−100+200 mesh) | 99.99% | ~$127–$143 / 50 g | Preferred; BYU account available |
| Spectrum Chemical (S1031) | 100–200 Mesh Si | 75–150 µm | 98% | ~$208 / 250 g | Lower cost per gram at scale |
| Sigma-Aldrich | Custom inquiry | Custom | 99%+ | Quote required | Not a standard catalog item |
| Panadyne / Washington Mills | Custom order | 100–500 µm | Industrial grade | Quote required | Bulk only; purity may vary |

**Recommendation**: Start with the Fisher/Thermo Scientific AA4560918 (50 g or 250 g) to confirm it flows adequately in the autotrickler before committing to larger quantities.

---

## Processing the Existing ~45 µm Silicon to Improve Flow

If ordering new silicon is not immediately possible, there are several approaches to improve the flowability of the current fine powder.

### 1. Dry Granulation (Roll Compaction / Slugging)
- **What**: Compress the fine powder into a compact or "slug" using a press, then break it up through a screen to create coarser granules.
- **How**: Place powder in a pellet press (e.g., a benchtop hydraulic press with a 13 mm die) and apply light pressure to form a loose compact. Crush the compact and pass through a 100–200 µm sieve to collect a granulated fraction.
- **Pros**: No binder needed; keeps the silicon chemically pure; quick to try with existing lab equipment.
- **Cons**: Requires sieving to get a consistent size; granules may be irregular; some fines still produced.

### 2. Wet Granulation + Drying
- **What**: Disperse the fine silicon in a small amount of isopropanol (IPA) or ethanol, allow to settle into loose agglomerates, then gently dry and break up the cake.
- **How**: Mix ~10 g of Si powder with ~2–5 mL of IPA in a glass beaker. Stir briefly, spread thinly on a glass plate, and dry in a desiccator or oven at ~50–70 °C. Gently crush the dried cake and sieve.
- **Pros**: Low-cost; equipment available in most labs; IPA is a commonly used lab solvent—handle per SDS (flammable; use away from ignition sources / in a hood as appropriate).
- **Cons**: IPA must be fully removed before use (residual solvent); some risk of oxidation during drying if moisture is present; particle size distribution will be broad without further sieving.

### 3. Sieving and Classifying
- **What**: Simply sieve the existing powder to remove the very finest particles that contribute most to poor flow.
- **How**: Use a 75 µm (or 100 µm) wire mesh sieve to separate out sub-75 µm fines. The retained fraction (>75 µm) will flow better.
- **Pros**: Simplest option; no processing required; immediately actionable with lab sieves.
- **Cons**: The current batch is specified at max ~45 µm, so almost all material will pass through a 75 µm sieve. Limited benefit unless the actual distribution is broader than the nominal spec.

### 4. Adding a Flow Aid (Glidant)
- **What**: Blend a small quantity (~0.5–1 wt%) of a dry glidant such as fumed silica (e.g., Aerosil® 200, Cab-O-Sil®) into the silicon powder.
- **How**: Weigh out ~0.5 g fumed silica per 100 g Si powder. Mix thoroughly in a closed container or ball-mill briefly (10–15 min).
- **Pros**: A well-known technique in pharmaceutical and powder metallurgy; very effective at small additions; no bulk particle size change needed.
- **Cons**: Introduces a second component (SiO₂) into the silicon batch — acceptable if SiO₂ is a tolerable impurity at <1 wt% for the intended use (e.g., Al-Si alloy synthesis). Needs to be weighed for composition accounting.

### 5. Drying Under Vacuum / Inert Atmosphere
- **What**: The native oxide layer (SiO₂) on the silicon surface can attract moisture, increasing inter-particle adhesion. Drying the powder in a vacuum oven or under dry nitrogen before use may help.
- **How**: Place silicon in a vacuum oven at 80–100 °C for 2–4 hours. Transfer to a sealed, dry container (preferably under nitrogen or argon) for storage and use.
- **Pros**: Simple; improves flow by reducing adsorbed moisture; no change to particle size or composition.
- **Cons**: Effect is temporary — powder will re-adsorb moisture if exposed to ambient air; needs to be done close to time of use.

### Why Silicon Is Particularly Challenging

Pure silicon develops a native SiO₂ oxide layer on every particle surface almost instantly upon air exposure. This oxide is hydrophilic and tends to:
- Adsorb moisture (even in relatively dry environments), forming liquid bridges between particles
- Create electrostatic charge under low-humidity conditions, causing particles to stick to surfaces and each other

These factors are intrinsic to the material and explain why the ~45 µm silicon performs worse than organic powders of comparable size. Coarser particles (~100–200 µm) reduce the surface-area-to-volume ratio and gravity starts to dominate over the surface forces, so flow improves substantially even with the same surface chemistry.

**Bottom line**: The most practical near-term fix for the existing powder is **Option 4 (fumed silica flow aid)** or **Option 5 (pre-drying)**, both of which can be done immediately. For a long-term solution, switching to **−100 +200 mesh silicon (75–150 µm)** from Fisher/Thermo Scientific (AA4560918) is the recommended path.
