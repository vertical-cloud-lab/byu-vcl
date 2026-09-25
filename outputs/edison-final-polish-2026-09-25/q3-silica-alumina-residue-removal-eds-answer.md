# q3-silica-alumina-residue-removal-eds

**Query:** After final polishing of aluminum alloys with colloidal silica or fine alumina suspensions, how much abrasive residue typically remains on the surface after cleaning, and how does such residue bias quantitative SEM-EDS or EPMA results for Si, Al, and O, especially at low accelerating voltages (5 kV) where the X-ray generation depth is only about 0.3 um? What cleaning procedures are documented to remove colloidal silica residue most effectively from aluminum without etching or corroding it (e.g., flushing with water on the cloth at the end of the polishing cycle, detergent solutions, cotton swabbing, ultrasonic cleaning in water, ethanol, or alkaline detergents, plasma cleaning)? Does colloidal silica chemically bond to or redeposit on aluminum surfaces, and can it be dissolved without attacking aluminum?

**Task ID:** `70fbcddf-cac9-436e-a37b-12644fe8e445`

---

Question: After final polishing of aluminum alloys with colloidal silica or fine alumina suspensions, how much abrasive residue typically remains on the surface after cleaning, and how does such residue bias quantitative SEM-EDS or EPMA results for Si, Al, and O, especially at low accelerating voltages (5 kV) where the X-ray generation depth is only about 0.3 um? What cleaning procedures are documented to remove colloidal silica residue most effectively from aluminum without etching or corroding it (e.g., flushing with water on the cloth at the end of the polishing cycle, detergent solutions, cotton swabbing, ultrasonic cleaning in water, ethanol, or alkaline detergents, plasma cleaning)? Does colloidal silica chemically bond to or redeposit on aluminum surfaces, and can it be dissolved without attacking aluminum?

# Abrasive residue on polished aluminum and its microanalytical consequences

## Executive conclusion

There is **no well-supported universal “typical” mass, thickness, surface coverage, or EDS concentration** of colloidal-silica residue remaining on aluminum after routine metallographic cleaning. The amount depends strongly on whether the slurry was allowed to dry, surface relief and scratches, abrasive size and concentration, cloth condition, rinsing, and whether particles became embedded. The literature establishes that submicrometer particles can remain on AA6061-T6 even after repeated high-pressure detergent washing, while embedded alumina on other polished or blasted metals can survive steam cleaning. A demanding aluminum-component cleanliness criterion—useful as a benchmark rather than a measured polishing-residue value—is nonvolatile residue below **0.1 µg cm⁻²**. Therefore, a clean-looking surface cannot be assumed to be analytically residue-free. (cherepy2005characterizationofan pages 2-3, cherepy2005characterizationofan pages 1-2, jabbari2012effectofsandblasting pages 4-7)

At **5 kV**, a silica or alumina overlayer is disproportionately important because the analysis is surface-weighted. Colloidal SiO₂ produces falsely high Si and O and depresses the normalized Al and alloying-element concentrations. Al₂O₃ residue produces falsely high O, usually raises apparent Al relative to the other alloy constituents, and dilutes all elements absent from the abrasive. The safest cleaning strategy is to prevent slurry drying: flush with water on the cloth during approximately the final 30 s, rinse immediately with cold high-purity water, wipe gently with clean soft cotton or tissue—optionally alcohol-moistened—and use a short clean-water or alcohol ultrasonic step only after confirming alloy compatibility. Strong alkali or fluoride can remove silica chemically, but neither can be assumed to preserve bare aluminum and its native oxide.

## 1. How much residue remains?

### What is directly documented

Published metallographic guidance describes residual colloidal silica as a persistent haze, streaks, or particles and notes that residual alumina can become embedded, but it does not report a reproducible residue thickness or mass for polished aluminum. Prompt rinsing is required precisely because dried silica becomes difficult to remove. (westin2025enhancingmicrostructuralanalysis pages 9-10)

In an AA6061-T6 cleanliness study, generally submicrometer particles remained or reappeared even after several rigorous detergent washes. Isopropanol hand wiping could remove such particles. That study’s cleanliness limits were **<0.1 µg cm⁻² nonvolatile residue** and no more than **908 particles larger than 5 µm per square foot**, but these are acceptance limits—not measurements of colloidal-silica residue after metallographic polishing. (cherepy2005characterizationofan pages 2-3, cherepy2005characterizationofan pages 1-2)

Fine alumina can be more troublesome than a removable film because fragments may be mechanically embedded. In sandblasted dental alloys, retained alumina appeared as coincident Al–O regions and remained after steam-jet cleaning; the study is not directly transferable quantitatively to fine polishing of aluminum, but it demonstrates that an oxide abrasive can resist ordinary cleaning once embedded. (jabbari2012effectofsandblasting pages 4-7)

**Thus, the defensible answer is not “a few percent” or a specified nanometer thickness.** After effective wet cleaning, residue may be sparse and discontinuous; after drying or embedding, local particles can be tens of nanometers to submicrometers thick and dominate individual low-voltage analysis points. Any laboratory claiming a routine residue level should establish it experimentally with polished blanks, pre/post-cleaning maps, or an independent surface method.

## 2. Bias in SEM-EDS or EPMA

### Direction of bias

For a surface carrying colloidal silica:

- **Si:** biased high; on low-Si aluminum alloys, even a weak Si peak may be entirely or partly preparation-derived.
- **O:** biased high from SiO₂, adsorbed water, and the native/hydrated aluminum oxide.
- **Al:** absolute Al X-ray generation from the substrate is attenuated or displaced, and normalized quantitative Al is biased low because Si and O consume part of the 100% total.
- Other alloying elements are likewise diluted after normalization.

For fine alumina residue:

- **O:** biased high.
- **Al:** usually biased high relative to Mg, Cu, Zn, Si, and other alloying elements because the abrasive itself contributes Al; whether Al rises in the final normalized result depends on residue geometry and correction behavior.
- **Si:** not directly added by pure alumina, but normalized Si and other alloying elements generally decrease.

### Why 5 kV is especially vulnerable

Low accelerating voltage markedly reduces electron range and makes emitted signals, including X-rays, more surface-localized. Low-voltage work can provide nanometer-scale spatial sensitivity, but surface cleanliness becomes correspondingly critical. (wuhrer2016lowvoltageimaging pages 4-7, wuhrer2016lowvoltageimaging pages 1-4, kawano2012applicationofthe pages 56-61)

Using the question’s approximate **0.3 µm X-ray-generation depth**, a simple geometric first estimate for a uniform film of thickness *t* is *t*/300 nm of the sampled depth:

- 3 nm film: approximately 1%
- 10 nm: approximately 3.3%
- 30 nm: approximately 10%
- 50 nm: approximately 17%
- 100 nm particle/patch: approximately 33%

These are **depth fractions, not predicted EDS weight percentages**. Real intensities are nonlinear because SiO₂, Al₂O₃, and Al have different densities, stopping powers, ionization distributions, absorption, take-off geometry, and matrix corrections. A discrete 50–100 nm particle under the beam can contribute much more strongly than its field-average surface coverage suggests.

A published low-voltage example illustrates the scale of surface-layer distortion: at 1 kV, an approximately 3 nm BeO surface film and carbon contamination caused EDS to report 87.5 at.% O, 11.9 at.% C, and only 0.6 at.% substrate Be. This is not an aluminum calibration, but it demonstrates that bulk quantification assumptions can fail catastrophically when the sampled depth approaches the surface-layer thickness. (mallinson2015thechlorideinduced pages 162-165)

Low-voltage quantification also has independent instrumental limitations: stronger absorption of low-energy X-rays, lower fluorescence yield, line overlaps, and uncertain mass-absorption coefficients. Standards-based analysis is preferable, but it does not correct an unknown heterogeneous abrasive overlayer; in multielement materials, low-voltage results may be reliable only qualitatively. (wuhrer2016lowvoltageimaging pages 10-12)

**Practical implication:** at 5 kV, do not interpret weak Si or O quantitatively until residue has been excluded. Compare maps before and after recleaning, analyze an identically prepared low-Si aluminum blank, inspect Si–O colocalization in BSE/EDS maps, and repeat selected measurements at a higher voltage. A surface-derived Si signal should fall disproportionately as analytical depth increases.

## 3. Cleaning procedures

The evidence supports a prevention-first sequence rather than trying to dissolve dried silica afterward. The options and their analytical risks are summarized below.

| Method | Documented effect/evidence | Aluminum-surface risk | Recommendation for quantitative 5 kV SEM-EDS/EPMA |
|---|---|---|---|
| Final ~30 s water flush on the polishing cloth | **General metallography:** replacing colloidal silica with water for the final ~30 s is documented to displace residual slurry before it dries (westin2025enhancingmicrostructuralanalysis pages 9-10) | Low if brief and followed by immediate drying; prolonged wet exposure may oxidize or stain reactive alloys | **Preferred first step.** Keep the specimen wet, flush thoroughly, and transfer immediately to rinsing; do not allow slurry to dry |
| Immediate cold-water rinse plus soft cotton/tissue wiping, optionally ethanol-moistened | **General metallography:** prompt cold-water rinsing and gentle wiping remove persistent silica; ethanol-moistened soft cotton is recommended. Hot water is discouraged because it may crystallize or harden silica residue (westin2025enhancingmicrostructuralanalysis pages 9-10) | Low when wiping is gentle and lint-free; aggressive rubbing can scratch soft Al or transfer fibers | **Strongly recommended.** Use fresh lint-free cotton/swabs and inspect for Si-rich particles before analysis |
| Short ultrasonic cleaning in clean water | **General metallography; indirect Al evidence:** ultrasonics are effective at dislodging particles before SEM, although aluminum-specific removal efficiency for colloidal silica was not quantified (westin2025enhancingmicrostructuralanalysis pages 9-10, cherepy2005characterizationofan pages 2-3) | Water can promote staining, oxide growth, or galvanic attack around intermetallics if exposure is prolonged; ultrasonics may eject weak inclusions | Use briefly only after alloy-specific validation; rinse with high-purity water, displace water with alcohol, and dry promptly |
| Short ultrasonic cleaning in isopropanol or ethanol | **General metallography:** alcohol ultrasonics are documented for pre-SEM cleaning; isopropanol is reported to remove residual silica. Solvent wiping removed submicrometer particles from AA6061-T6 (**direct Al evidence**) (westin2025enhancingmicrostructuralanalysis pages 9-10, cherepy2005characterizationofan pages 1-2) | Usually lower corrosion risk than aqueous cleaning, but alcohol is not a reliable chemical solvent for bulk SiO₂; bath contamination can redeposit particles | **Preferred secondary step** after wet flushing and wiping. Use fresh high-purity alcohol and a clean bath; treat the action as particle displacement, not guaranteed silica dissolution |
| Neutral/mild detergent wash | **Direct Al evidence:** detergent washing removes particles and nonvolatile residue, but submicrometer particles may persist or reappear after repeated washing (cherepy2005characterizationofan pages 2-3, cherepy2005characterizationofan pages 1-2) | Surfactant or salt residue can create C/O/Na signals; prolonged aqueous contact may alter the native oxide | Useful if water/alcohol cleaning is insufficient. Use dilute, residue-free detergent, gentle contact, and exhaustive high-purity-water rinsing |
| Mild alkaline detergent, controlled dilution and time | **Direct AA6061 evidence:** alkaline detergents contributed to low particle/NVR levels when used after phosphoric-acid treatment; detergent also changed the hydrated oxide surface chemistry (cherepy2005characterizationofan pages 2-3, cherepy2005characterizationofan pages 7-7) | Aluminum and its oxide are amphoteric; excessive pH, temperature, or time can etch Al, attack Mg-rich phases, and alter O/Al results | **Conditional only.** Validate on a sacrificial specimen, minimize exposure, rinse thoroughly, and reject the method if quantitative surface O or the native oxide is of interest |
| Phosphoric-acid etch followed by alkaline detergent | **Direct AA6061 evidence:** a 30 vol% phosphoric-acid etch followed by ultrasonic alkaline-detergent cleaning produced low residual particle counts; a reported cleanliness target was NVR below 0.1 µg/cm². The acid also rebuilt the oxide and selectively dissolved Mg₂Si (cherepy2005characterizationofan pages 2-3, cherepy2005characterizationofan pages 1-2, cherepy2005characterizationofan pages 7-7) | Intentionally etches and chemically reconstructs the surface; may generate debris initially and remove or modify constituent phases | **Not appropriate for an as-polished quantitative microanalysis surface.** Reserve for component cleanliness when controlled surface alteration is acceptable |
| Oxygen/air or argon plasma cleaning | No retrieved study demonstrated removal of inorganic SiO₂ or Al₂O₃ abrasive from polished aluminum; surface-finishing literature supports plasma/ion methods mainly for hydrocarbons or contamination, not selective silica removal (kawano2012applicationofthe pages 56-61) | Oxygen plasma can grow or modify aluminum oxide and raise measured O; ion bombardment can sputter preferentially, roughen, or redistribute material | Use only for organic contamination after abrasive removal. Do not regard disappearance of carbon as proof that silica/alumina is gone; avoid when native O is to be quantified |
| Strong alkali to dissolve/desorb silica | **Mechanistic, not polished-Al validation:** NaOH desorbed chemisorbed silica from an Al(OH)₃ surface, but also released Al and decomposed the hydroxide substrate (guan2019silicaremovalusing pages 12-15) | High risk of attacking amphoteric Al/Al₂O₃, producing aluminate, roughness, pits, and altered Al/O signals | **Reject for quantitative surface analysis** unless controlled etching is intended; there is no demonstrated selectivity that preserves bare polished aluminum |
| Fluoride/HF-based silica dissolution | Silica can be chemically dissolved by fluoride chemistry, but no retrieved evidence established a nonattacking fluoride treatment for polished aluminum | Severe safety hazard; removes/modifies native alumina and can attack or contaminate Al, invalidating surface-sensitive Si/Al/O measurements | **Do not use** for residue removal on an analytical aluminum surface; repolish instead if residue cannot be removed mechanically |


*Table: Evidence-calibrated comparison of cleaning routes for silica or alumina residue, distinguishing direct aluminum evidence from general metallographic guidance. Recommendations prioritize preserving the near-surface region sampled by 5 kV microanalysis.*

### Recommended nonetching workflow

1. **Never let colloidal silica dry on the specimen.** During approximately the final 30 s of polishing, stop the silica feed and introduce water onto the rotating cloth to dilute and displace slurry. This is explicitly recommended in metallographic guidance. (westin2025enhancingmicrostructuralanalysis pages 9-10)
2. **Immediately rinse with cold, high-purity water.** Avoid hot water, which has been reported to harden or crystallize silica residue and make repolishing necessary. (westin2025enhancingmicrostructuralanalysis pages 9-10)
3. **Gently wipe while wet** with fresh, soft, lint-free cotton or tissue. For persistent material, use ethanol-moistened cotton. Avoid aggressive pressure on soft aluminum.
4. **Use a short ultrasonic step if needed.** General metallographic guidance identifies ultrasonics as highly effective before SEM and reports isopropanol as effective against residual SiO₂. On aluminum, fresh high-purity ethanol or isopropanol generally presents less aqueous-corrosion risk than a prolonged water bath, although alcohol should be understood primarily as a carrier and particle-displacement medium, not a true solvent for bulk silica. (westin2025enhancingmicrostructuralanalysis pages 9-10, cherepy2005characterizationofan pages 1-2)
5. **If using water ultrasonics, keep exposure short**, use a clean bath, follow with a high-purity-water rinse, displace water with alcohol, and dry promptly with clean gas. Validate first on alloys containing corrosion-sensitive intermetallics.
6. **Verify analytically**, preferably with low-kV BSE imaging and Si/O maps before accepting quantitative data.

### Detergents

A neutral, low-residue detergent can improve removal of loosely held particles, followed by exhaustive DI-water rinsing. Alkaline detergents are effective component cleaners but require caution: the AA6061 work used a phosphoric-acid etch followed by a mild alkaline detergent or ultrasonic detergent bath and achieved low particle/NVR levels. However, the process changed the hydrated oxide chemistry, and the acid selectively dissolved Mg₂Si. It is therefore a cleanliness treatment, not a surface-preserving preparation for quantitative analysis of the original polished microstructure. (cherepy2005characterizationofan pages 2-3, cherepy2005characterizationofan pages 1-2, cherepy2005characterizationofan pages 7-7)

### Plasma cleaning

No retrieved study showed that oxygen, air, or argon plasma selectively removes inorganic colloidal SiO₂ or Al₂O₃ from polished aluminum. Plasma is useful mainly for hydrocarbons and other organics. Oxygen plasma may thicken or modify the aluminum oxide and raise O; energetic ion cleaning can sputter, roughen, preferentially remove constituents, or redistribute particles. It should not be used as evidence that abrasive residue has been removed. Surface-finishing literature likewise distinguishes removal of hydrocarbons/contamination from preservation of the original surface. (kawano2012applicationofthe pages 56-61)

## 4. Does silica bond or redeposit on aluminum?

Both physical retention and chemical interaction are plausible:

- Particles can remain by capillary drying, electrostatic/colloidal forces, lodging in scratches or pores, and mechanical embedding.
- Aluminum immediately carries a native oxide/hydroxide surface—reported for AA6061 as an approximately 1 nm Al₂O₃ barrier plus a roughly 5–10 nm hydrated hydroxide/oxyhydroxide region—rather than exposing bare metallic Al to the slurry. (cherepy2005characterizationofan pages 2-3)
- Aqueous-silica studies show strong interaction with aluminum hydroxide-like surfaces. Aluminum can become incorporated into silica as tetrahedral Al–O–Si sites; less than an atomic layer can substantially suppress silica dissolution. Direct XPS evidence supports framework incorporation rather than merely weak adsorption under sufficiently alkaline, long-duration exposure. (chappex2013theeffectof pages 1-2, chappex2013theeffectof pages 2-3, iler1973effectofadsorbed pages 1-3)
- Silica adsorbed onto Al(OH)₃ was observed to progress from Q² species to polymerized Q³/Q⁴ structures; the authors interpreted this as chemisorption requiring strong alkali to break the bonds. Silica can also redeposit from supersaturated solution as temperature and solution chemistry change. (iler1973effectofadsorbed pages 6-8, guan2019silicaremovalusing pages 12-15)

These findings establish chemical plausibility, **not that every colloidal-silica particle forms a covalent bond during a short metallographic polish**. On a freshly polished aluminum alloy, most readily removed residue is probably particulate or gel-like, while a smaller fraction may interact strongly with the hydrated oxide, particularly after drying, prolonged contact, elevated pH, or local dissolution of Al.

## 5. Can silica be dissolved without attacking aluminum?

No retrieved source demonstrates a chemical bath that reliably dissolves chemisorbed or dried silica from a bare polished aluminum alloy while leaving both metal and native oxide analytically unchanged.

- **Strong NaOH** can desorb/dissolve silica, but a study using Al(OH)₃-coated particles also measured Al release and decomposition of the hydroxide under basic regeneration conditions. Aluminum and its oxide are amphoteric, so strong alkali cannot be considered selective. (guan2019silicaremovalusing pages 12-15)
- **Fluoride/HF chemistry** dissolves silica but also attacks or substantially modifies aluminum oxide and can attack aluminum; it is inappropriate for preserving a surface intended for Si/Al/O microanalysis.
- **Acid cleaning** can remove or reconstruct the oxide and selectively dissolve alloy phases, as shown for phosphoric acid and Mg₂Si in AA6061. (cherepy2005characterizationofan pages 2-3)
- **Alcohol does not truly dissolve bulk SiO₂** under normal cleaning conditions; its benefit is wetting, displacement, drying, and helping detach particles.

Accordingly, the least destructive solution is **wet dilution and mechanical displacement before drying**, followed by gentle wiping and brief ultrasonics. If a persistent Si–O layer remains after that sequence, repolishing with a non-silica final abrasive—or preparing parallel specimens with colloidal silica and alumina/diamond—is more defensible than chemical stripping when quantitative 5 kV Si, Al, and O data are required.

References

1. (cherepy2005characterizationofan pages 2-3): Nerine J. Cherepy, Tien H. Shen, Anthony P. Esposito, and Thomas M. Tillotson. Characterization of an effective cleaning procedure for aluminum alloys: surface enhanced raman spectroscopy and zeta potential analysis. Journal of Colloid and Interface Science, 282:80-86, Feb 2005. URL: https://doi.org/10.1016/j.jcis.2004.08.064, doi:10.1016/j.jcis.2004.08.064. This article has 59 citations and is from a peer-reviewed journal.

2. (cherepy2005characterizationofan pages 1-2): Nerine J. Cherepy, Tien H. Shen, Anthony P. Esposito, and Thomas M. Tillotson. Characterization of an effective cleaning procedure for aluminum alloys: surface enhanced raman spectroscopy and zeta potential analysis. Journal of Colloid and Interface Science, 282:80-86, Feb 2005. URL: https://doi.org/10.1016/j.jcis.2004.08.064, doi:10.1016/j.jcis.2004.08.064. This article has 59 citations and is from a peer-reviewed journal.

3. (jabbari2012effectofsandblasting pages 4-7): Youssef S. AL JABBARI, Spiros ZINELIS, and George ELIADES. Effect of sandblasting conditions on alumina retention in representative dental alloys. Dental materials journal, 31 2:249-55, Mar 2012. URL: https://doi.org/10.4012/dmj.2011-210, doi:10.4012/dmj.2011-210. This article has 59 citations and is from a peer-reviewed journal.

4. (westin2025enhancingmicrostructuralanalysis pages 9-10): Elin Marianne Westin, Jan Yngve Jonsson, Kaue Correa Riffel, Martijn Marinus Bos, Constantinos Goulas, and Antonio José Ramirez. Enhancing microstructural analysis: best practices for preparing duplex stainless steel welds and additive manufacturing deposits. Welding in the World, 70:4549-4581, Dec 2026. URL: https://doi.org/10.1007/s40194-025-02286-x, doi:10.1007/s40194-025-02286-x. This article has 5 citations and is from a domain leading peer-reviewed journal.

5. (wuhrer2016lowvoltageimaging pages 4-7): Richard Wuhrer and K. Moran. Low voltage imaging and x-ray microanalysis in the sem: challenges and opportunities. IOP Conference Series: Materials Science and Engineering, 109:012019, Feb 2016. URL: https://doi.org/10.1088/1757-899x/109/1/012019, doi:10.1088/1757-899x/109/1/012019. This article has 69 citations.

6. (wuhrer2016lowvoltageimaging pages 1-4): Richard Wuhrer and K. Moran. Low voltage imaging and x-ray microanalysis in the sem: challenges and opportunities. IOP Conference Series: Materials Science and Engineering, 109:012019, Feb 2016. URL: https://doi.org/10.1088/1757-899x/109/1/012019, doi:10.1088/1757-899x/109/1/012019. This article has 69 citations.

7. (kawano2012applicationofthe pages 56-61): K Kawano. Application of the ultra high resolution, low voltage scanning electron microscopy in the materials science. Unknown journal, 2012.

8. (mallinson2015thechlorideinduced pages 162-165): CF Mallinson. The chloride induced localised corrosion of aluminium and beryllium: a study by electron and x-ray spectroscopies. Unknown journal, 2015.

9. (wuhrer2016lowvoltageimaging pages 10-12): Richard Wuhrer and K. Moran. Low voltage imaging and x-ray microanalysis in the sem: challenges and opportunities. IOP Conference Series: Materials Science and Engineering, 109:012019, Feb 2016. URL: https://doi.org/10.1088/1757-899x/109/1/012019, doi:10.1088/1757-899x/109/1/012019. This article has 69 citations.

10. (cherepy2005characterizationofan pages 7-7): Nerine J. Cherepy, Tien H. Shen, Anthony P. Esposito, and Thomas M. Tillotson. Characterization of an effective cleaning procedure for aluminum alloys: surface enhanced raman spectroscopy and zeta potential analysis. Journal of Colloid and Interface Science, 282:80-86, Feb 2005. URL: https://doi.org/10.1016/j.jcis.2004.08.064, doi:10.1016/j.jcis.2004.08.064. This article has 59 citations and is from a peer-reviewed journal.

11. (guan2019silicaremovalusing pages 12-15): Yan-Fang Guan, Mariana Marcos-Hernández, Xinglin Lu, Wei Cheng, Han-Qing Yu, Menachem Elimelech, and Dino Villagrán. Silica removal using magnetic iron-aluminum (fe-al) hybrid nanomaterials: measurements, adsorption mechanisms, and implications for silica scaling in reverse osmosis. Environmental science & technology, 53:13302-13311, Oct 2019. URL: https://doi.org/10.1021/acs.est.9b02883, doi:10.1021/acs.est.9b02883. This article has 36 citations and is from a domain leading peer-reviewed journal.

12. (chappex2013theeffectof pages 1-2): Théodore Chappex and Karen L. Scrivener. The effect of aluminum in solution on the dissolution of amorphous silica and its relation to cementitious systems. Journal of the American Ceramic Society, 96:592-597, Feb 2013. URL: https://doi.org/10.1111/jace.12098, doi:10.1111/jace.12098. This article has 151 citations and is from a domain leading peer-reviewed journal.

13. (chappex2013theeffectof pages 2-3): Théodore Chappex and Karen L. Scrivener. The effect of aluminum in solution on the dissolution of amorphous silica and its relation to cementitious systems. Journal of the American Ceramic Society, 96:592-597, Feb 2013. URL: https://doi.org/10.1111/jace.12098, doi:10.1111/jace.12098. This article has 151 citations and is from a domain leading peer-reviewed journal.

14. (iler1973effectofadsorbed pages 1-3): R.K Iler. Effect of adsorbed alumina on the solubility of amorphous silica in water. Journal of Colloid and Interface Science, 43:399-408, May 1973. URL: https://doi.org/10.1016/0021-9797(73)90386-x, doi:10.1016/0021-9797(73)90386-x. This article has 332 citations and is from a peer-reviewed journal.

15. (iler1973effectofadsorbed pages 6-8): R.K Iler. Effect of adsorbed alumina on the solubility of amorphous silica in water. Journal of Colloid and Interface Science, 43:399-408, May 1973. URL: https://doi.org/10.1016/0021-9797(73)90386-x, doi:10.1016/0021-9797(73)90386-x. This article has 332 citations and is from a peer-reviewed journal.
