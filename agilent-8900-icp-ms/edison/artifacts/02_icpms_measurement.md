Question: Context: We operate an Agilent 8900 triple-quadrupole ICP-MS (ICP-QQQ) and want to characterize the elemental composition of metallic alloy samples, primarily aluminum alloys such as AlSi10Mg (Al-Si-Mg, e.g. from laser powder bed fusion feedstock) and 1100 aluminum wire, and silicon powder feedstock. Samples must be acid-digested into a clear, water-soluble solution with no suspended particles before nebulization. We are a university lab setting up this workflow for the first time. Give detailed best practices for measuring aluminum-alloy digests on an Agilent 8900 triple-quadrupole ICP-MS. Cover isotope selection for Al, Si, Mg, Fe, Cu, Mn, Zn, Ti, Cr, Ni and trace elements; major spectral and polyatomic interferences in an aluminum/nitric-acid matrix and how MS/MS modes with He collision gas, H2, O2, and NH3 reaction gases (including mass-shift methods) remove them; recommended internal standards (Sc, Ge, Rh, In, Bi); plasma and torch settings; and how to deal with the very high aluminum matrix (e.g. via dilution) to avoid detector saturation and matrix suppression.

# Best Practices for Measuring Aluminum-Alloy Digests on an Agilent 8900 Triple-Quadrupole ICP-MS

## 1. Sample Preparation and Acid Digestion

Aluminum alloys such as AlSi10Mg and 1100 aluminum wire dissolve readily in mineral acids. The recommended approach for ICP-MS is microwave-assisted closed-vessel acid digestion using a mixture of concentrated HNO₃ (and optionally small amounts of HCl or HF depending on the alloy). HNO₃ is preferred as the primary acid because it avoids introducing chloride, which forms severe polyatomic interferences (e.g., ⁴⁰Ar³⁵Cl⁺ on ⁷⁵As, ³⁵Cl¹⁶O⁺ on ⁵¹V) (wilschefski2019inductivelycoupledplasma pages 10-12). For AlSi10Mg, a small addition of HF may be needed to dissolve silicon-rich phases, but HF attacks quartz torch/spray chamber components and must be kept minimal or used with HF-resistant sample introduction hardware (lotter2014analysisofzirconium pages 107-112). Silicon powder feedstock can be dissolved in mixtures of HNO₃ + HF. In all cases, the digest must be a clear solution with no suspended particles before nebulization.

**Practical digestion protocol:** Weigh 50–100 mg of alloy chip/powder into a microwave vessel, add 5–8 mL concentrated HNO₃ (trace-metal grade) and, if required, 0.5–1 mL concentrated HF. Run a staged microwave program (e.g., ramp to 180–200 °C over 15 min, hold 15–20 min). After cooling, transfer quantitatively to a volumetric flask and dilute to volume with ultrapure water, targeting a final acid concentration of ~2–5% v/v HNO₃.

## 2. Dealing with the High Aluminum Matrix

A primary analytical challenge is that aluminum constitutes 85–99% of the sample mass. A total dissolved solids (TDS) content below ~0.2% (2000 mg/L) is generally recommended to avoid nebulizer clogging, cone deposition, signal suppression, and detector saturation (wilschefski2019inductivelycoupledplasma pages 9-10, wolf2015multielementalanalysisof pages 5-7). For a 100 mg sample dissolved to 100 mL, the initial Al concentration is approximately 1000 mg/L (~0.1% TDS), which is near the acceptable limit. Most laboratories apply a further 10- to 100-fold dilution to bring major-element concentrations (Al, Si) into the linear calibration range and to reduce matrix-induced signal suppression and polyatomic interference severity. Extended Dynamic Range (EDR) or detector attenuation modes on the 8900 can handle some high-concentration elements, but dilution remains essential for routine accuracy.

**Two-dilution strategy:** Prepare (i) a low-dilution aliquot (e.g., 10× or 50×) for trace impurities (Fe, Cu, Mn, Cr, Ni, Ti, Zn at ppm levels in the alloy → low ppb in solution), and (ii) a high-dilution aliquot (e.g., 1000× or more) for major elements (Al, Si, Mg) to bring them within the detector linear range. Matrix-matched calibration standards (adding a known amount of high-purity Al standard to calibration blanks/standards) or standard-additions calibration should be used for best accuracy (wolf2015multielementalanalysisof pages 5-7, wilschefski2019inductivelycoupledplasma pages 10-12).

## 3. Isotope Selection, Polyatomic Interferences, and Recommended Cell Gas Modes

The Agilent 8900 ICP-QQQ in MS/MS mode uses both quadrupoles (Q1 and Q2) as unit-mass filters with a collision/reaction cell (ORS⁴) between them. This tandem mass-selection architecture is critical: Q1 pre-selects the analyte mass before the cell, preventing non-target masses from entering and forming new interfering product ions—a key advantage over single-quadrupole CRC operation (yamanakaUnknownyeardeterminationoftrace pages 44-47, takahashiUnknownyearsiliconwaferanalysis pages 69-71, hsuUnknownyearanalysisofnanoparticles pages 69-71).

The following table provides a comprehensive element-by-element guide to isotope selection, major interferences in an Al/HNO₃ matrix, and recommended cell gas modes:

| Element | Preferred Isotope (m/z) | Major Polyatomic Interferences in Al/HNO3 Matrix | Recommended Cell Gas Mode | MS/MS Mass Pair (Q1→Q2) | Notes |
|---|---:|---|---|---|---|
| Al | 27 | ^12C^15N^+, ^13C^14N^+, ^12C^14N^1H^+; in general CN/CNH background if carbon is present | Cool plasma + NH3, on-mass | 27→27 | Only stable Al isotope. Usually a major matrix element, so extensive dilution is required to avoid detector saturation and severe matrix suppression; method best used for residual/low-level Al or highly diluted major-element screening rather than direct high-% Al quantitation by ICP-MS (takahashiUnknownyearsiliconwaferanalysis pages 106-108, shimamura2022multielementnanoparticleanalysis pages 106-108, yamanakaUnknownyeardeterminationoftrace pages 35-37) |
| Si | 28 | ^14N_2^+, ^12C^16O^+; also CO-derived species can react in-cell; SiO^+/SiO2^+ chemistry may be complicated by background | H2 on-mass preferred for routine Si; alternative O2 mass-shift | 28→28; alternatives 28→44 or 28→60 | H2 on-mass works because Si^+ is relatively unreactive with H2 while major interferences react. O2 mass-shift to SiO^+ is possible, but SiO2^+ at m/z 60 may give lower BEC than SiO^+ at m/z 44 in some matrices (takahashiUnknownyearsiliconwaferanalysis pages 44-46, yamanakaUnknownyeardeterminationoftrace pages 104-106, takahashiUnknownyearsiliconwaferanalysis pages 90-92) |
| Mg | 24 | ^12C_2^+ | Cool plasma + NH3, on-mass | 24→24 | ^24Mg gives highest sensitivity but is most interference-prone in carbon-bearing matrices; cool plasma suppresses C-based background. If needed, ^25Mg or ^26Mg can be checked as confirmatory isotopes at lower sensitivity (takahashiUnknownyearsiliconwaferanalysis pages 106-108, hsuUnknownyearanalysisofnanoparticles pages 106-108, shimamura2022multielementnanoparticleanalysis pages 106-108) |
| Fe | 56 | ^40Ar^16O^+ is the dominant classical interference; possible matrix oxides/hydroxides from high TDS | He KED for routine work; H2 on-mass can also help depending on tune | 56→56 | For high-matrix alloy digests, also monitor ^57Fe as a confirmation isotope if sensitivity allows. Robust plasma and low oxide tune are important because Fe is highly sensitive to oxide background (lomaxvogt2019buildingadatabase pages 72-78, lomaxvogt2019buildingadatabase pages 20-23, rowley2000fundamentalstudiesof pages 41-47) |
| Cu | 63 | ^40Ar^23Na^+, ^31P^16O_2^+; possible matrix-based polyatomics in salty digests | He KED, on-mass | 63→63 | ^63Cu is usually preferred for sensitivity; ^65Cu can be run as a qualifier where Zn overlap or high Na/P background is problematic (lomaxvogt2019buildingadatabase pages 108-113, wolf2015multielementalanalysisof pages 5-7) |
| Mn | 55 | ^40Ar^15N^+, ^40Ar^14N^1H^+, ^23Na^16O_2^+; chloride-derived species possible in dirty matrices | He KED, on-mass | 55→55 | Monoisotopic element, so interference control is essential. Keep chloride and nitrogen background low; clean nitric digestion is advantageous (lomaxvogt2019buildingadatabase pages 108-113) |
| Zn | 66 preferred; 64 optional | For ^64Zn: ^32S_2^+, ^32S^16O_2^+, SrAr^++; for ^66Zn: sulfur/oxide species are typically lower than at 64 | He KED for routine alloy digests; O2-based mass-shift can be explored for difficult S-rich matrices | 66→66; optional 64→64 | ^66Zn is often safer than ^64Zn in matrices containing sulfur or phosphorus. If using ^64Zn, confirm with ^66Zn. O2-based modes are more specialized and should be validated on your matrix (lomaxvogt2019buildingadatabase pages 108-113, takahashiUnknownyearsiliconwaferanalysis pages 71-73) |
| Ti | 48 | ^32S^16O^+; direct isobaric overlap from ^48Ca^+ | NH3 mass-shift to Ti–ammonia cluster | 48→114 | One of the clearest ICP-QQQ advantages: NH3 MS/MS allows measurement of Ti as a cluster product ion, avoiding S-based interference on Ti in complex matrices. Major isotope ^48Ti gives best sensitivity if Ca/Ti chemistry is controlled by MS/MS (takahashiUnknownyearsiliconwaferanalysis pages 69-71, hsuUnknownyearanalysisofnanoparticles pages 69-71, shimamura2022multielementnanoparticleanalysis pages 69-71) |
| Cr | 52 | ^40Ar^12C^+; in some matrices also chloride- or oxide-related polyatomics | O2 mass-shift to CrO^+ preferred; He KED may suffice for cleaner matrices | 52→68; optional 52→52 | O2 mass-shift is a strong Agilent 8900 method for Cr because it cleanly separates Cr from ArC background. ^53Cr can be used as confirmation but has lower abundance and possible other overlaps (takahashiUnknownyearsiliconwaferanalysis pages 69-71, hsuUnknownyearanalysisofnanoparticles pages 69-71, takahashiUnknownyearsiliconwaferanalysis pages 106-108) |
| Ni | 60 preferred; 58 optional | For ^58Ni: possible Fe-based overlaps and CaO-related background; for ^60Ni: ^44Ca^16O^+, possible NaCl-derived species such as ^23Na^37Cl^+ | He KED, on-mass | 60→60 | ^60Ni is often preferred in Ca-rich matrices to avoid stronger issues at 58, but both 58 and 60 should be reviewed during development. Keep chloride low because NaCl polyatomics can affect Ni masses (wilschefski2019inductivelycoupledplasma pages 10-12, wolf2015multielementalanalysisof pages 5-7) |
| V | 51 | ^35Cl^16O^+, possible Ar-based reaction products if non-MS/MS modes are used | NH3 on-mass MS/MS | 51→51 | NH3 in true MS/MS is particularly valuable because Q1 rejects non-target masses before the cell, reducing creation of new product-ion interferences at m/z 51 (takahashiUnknownyearsiliconwaferanalysis pages 69-71, hsuUnknownyearanalysisofnanoparticles pages 69-71, shimamura2022multielementnanoparticleanalysis pages 69-71) |
| Pb | 208 preferred; 206, 207 confirmatory | Usually fewer severe polyatomics than first-row transition metals; possible doubly charged REE or matrix tailing at very high TDS | No gas or He KED | 208→208 | Pb is generally straightforward on ICP-MS once matrix loading is controlled. Use ^208Pb for sensitivity and 206/207 as isotope-ratio checks for contamination or memory effects (wilschefski2019inductivelycoupledplasma pages 9-10, wolf2015multielementalanalysisof pages 5-7) |
| Sn | 118 or 120 | Oxide and doubly charged rare-earth/background species can affect some Sn masses; high-matrix suppression often more important than spectral overlap | He KED or no gas | 118→118 or 120→120 | Select isotope after checking expected Cd/Te/Xe background and availability of clean blank. Sn can show memory; rinse thoroughly after standards and samples (wolf2015multielementalanalysisof pages 5-7, wilschefski2019inductivelycoupledplasma pages 9-10) |
| Ga | 69 preferred; 71 confirmatory | Possible oxide/doubly charged background depending on matrix; some overlap risk varies by instrument background | He KED | 69→69 | Useful trace/impurity element in Al alloys. Run both 69 and 71 during development if concentrations permit; verify no Zn- or matrix-related tailing into Ga masses (wolf2015multielementalanalysisof pages 5-7, wilschefski2019inductivelycoupledplasma pages 9-10) |
| Co | 59 | Matrix-based polyatomics possible in dirty matrices; generally less interfered than Fe/Cr/V | He KED | 59→59 | Good trace impurity isotope for alloy screening; monitor with Ni and Cr in the same He method block (wolf2015multielementalanalysisof pages 5-7) |
| Mo | 95 or 98 | Oxide and doubly charged species possible depending on matrix composition | He KED | 95→95 or 98→98 | Choose isotope based on expected Zr/Ru background and blank cleanliness. Usually not the hardest analyte in Al alloy digests once matrix is diluted (wolf2015multielementalanalysisof pages 5-7) |
| As | 75 | ^40Ar^35Cl^+ classically; in chloride-bearing digests severe | O2 mass-shift to AsO^+ | 75→91 | Not a typical alloy major element, but relevant for impurity screening. O2 MS/MS with 75→91 avoids many on-mass chloride problems and rejects ^91Zr^+ by Q1 control (takahashiUnknownyearsiliconwaferanalysis pages 64-66) |
| Se | 78 or 80 | Ar_2^+ and other Ar-based species; matrix-based background often severe | O2 mass-shift if needed; otherwise specialized method | 78→94 or 80→96 (method-dependent) | Usually a dedicated trace-element method, not a routine alloy panel analyte. Include only if needed and validate carefully in your matrix (rowley2000fundamentalstudiesof pages 41-47, takahashiUnknownyearsiliconwaferanalysis pages 71-73) |


*Table: This table summarizes recommended isotopes, key spectral interferences, and practical Agilent 8900 MS/MS gas-mode choices for aluminum-alloy digests. It is designed as a starting method-development map for Al-rich nitric-acid matrices.*

### Key Interference Highlights in Aluminum/Nitric Acid Matrices

- **²⁷Al** (monoisotopic): Interfered by ¹²C¹⁵N⁺, ¹³C¹⁴N⁺, and ¹²C¹⁴N¹H⁺ from carbon/nitrogen in the plasma and solvent. Cool plasma combined with NH₃ cell gas in MS/MS on-mass mode effectively suppresses these backgrounds, yielding detection limits below 0.05 ppt in semiconductor applications (takahashiUnknownyearsiliconwaferanalysis pages 106-108, shimamura2022multielementnanoparticleanalysis pages 106-108, hsuUnknownyearanalysisofnanoparticles pages 106-108).

- **²⁸Si**: Severely interfered by ¹⁴N₂⁺ and ¹²C¹⁶O⁺. Two primary strategies exist on the 8900: (a) H₂ on-mass mode (28→28), which works because Si⁺ is unreactive with H₂ while N₂⁺ and CO⁺ react and are neutralized (takahashiUnknownyearsiliconwaferanalysis pages 44-46); or (b) O₂ mass-shift mode to SiO⁺ at m/z 44 (28→44) or SiO₂⁺ at m/z 60 (28→60), though the Si⁺ + O₂ reaction is slightly endothermic and CO⁺ can also form product ions at m/z 44, so SiO₂⁺ at m/z 60 may provide a lower background equivalent concentration (yamanakaUnknownyeardeterminationoftrace pages 104-106).

- **⁵⁶Fe**: The classic ⁴⁰Ar¹⁶O⁺ interference is among the most intense polyatomic overlaps in ICP-MS (lomaxvogt2019buildingadatabase pages 72-78, lomaxvogt2019buildingadatabase pages 20-23). He KED mode effectively attenuates ArO⁺ for routine work. H₂ on-mass reaction can also be used.

- **⁵²Cr**: Interfered by ⁴⁰Ar¹²C⁺ (takahashiUnknownyearsiliconwaferanalysis pages 106-108). O₂ mass-shift to ⁵²Cr¹⁶O⁺ at m/z 68 (52→68) is a powerful approach on the 8900 because Q1 rejects all non-52 masses, cleanly separating Cr from the ArC⁺ background (takahashiUnknownyearsiliconwaferanalysis pages 69-71, hsuUnknownyearanalysisofnanoparticles pages 69-71).

- **⁴⁸Ti**: Isobarically interfered by ⁴⁸Ca⁺ and by ³²S¹⁶O⁺ in sulfur-containing matrices. NH₃ mass-shift mode converts ⁴⁸Ti⁺ to a Ti–ammonia cluster ion at m/z 114 (⁴⁸Ti¹⁴NH(¹⁴NH₃)₃⁺), which is one of the clearest demonstrations of the ICP-QQQ advantage (takahashiUnknownyearsiliconwaferanalysis pages 69-71, hsuUnknownyearanalysisofnanoparticles pages 69-71, shimamura2022multielementnanoparticleanalysis pages 69-71).

- **⁵¹V** (monoisotopic): Interfered by ³⁵Cl¹⁶O⁺, which is problematic when any chloride is present. NH₃ in MS/MS on-mass mode (51→51) is effective because Q1 blocks Ar⁺ from entering the cell and generating ArNH-type secondary product ions at m/z 51 (takahashiUnknownyearsiliconwaferanalysis pages 64-66, shimamura2022multielementnanoparticleanalysis pages 69-71).

## 4. Collision/Reaction Cell Gas Modes: He, H₂, O₂, and NH₃

The Agilent 8900 supports multi-tune (multi-mode) acquisition, allowing different cell gas conditions to be applied sequentially within a single sample acquisition. The following table summarizes each gas's mechanism and application:

| Cell Gas | Mode of Action | Typical Flow Rate | Key Applications in Al Alloy Analysis | MS/MS Advantage |
|---|---|---|---|---|
| He | Kinetic Energy Discrimination (KED) / collision mode; larger polyatomic ions undergo more collisions and lose more kinetic energy than monatomic analyte ions, so the energy barrier preferentially attenuates the polyatomic background | 4-5 mL/min | Good routine mode for moderately interfered analytes in Al-alloy digests, especially Fe, Mn, Cu, Zn, Ni, and Co; useful when the main problem is generic Ar-, N-, O-, C-based polyatomics rather than a highly specific chemistry problem (yamanakaUnknownyeardeterminationoftrace pages 44-47, rowley2000fundamentalstudiesof pages 41-47, lomaxvogt2019buildingadatabase pages 72-78, lomaxvogt2019buildingadatabase pages 20-23) | In true MS/MS, Q1 passes only the target nominal mass into the cell, so He-KED works more cleanly because off-mass ions are excluded before collision processes occur; this reduces the chance of new cell-formed backgrounds and improves robustness in complex alloy matrices (yamanakaUnknownyeardeterminationoftrace pages 44-47, shimamura2022multielementnanoparticleanalysis pages 71-73, wolf2015multielementalanalysisof pages 5-7) |
| H2 | On-mass reaction mode; selective chemistry where some polyatomic interferents react with H2 while certain analyte ions react little or not at all, preserving analyte signal | 3-7 mL/min | Primary use is routine on-mass measurement of 28Si in matrices where 14N2+ and 12C16O+ interfere at m/z 28; can also assist some mixed-gas methods, but for Al-alloy digests its most useful role is Si determination without mass shift (takahashiUnknownyearsiliconwaferanalysis pages 44-46, takahashiUnknownyearsiliconwaferanalysis pages 90-92, hsuUnknownyearanalysisofnanoparticles pages 90-92) | MS/MS ensures only m/z 28 enters the cell for Si work, so H2 chemistry removes/reacts interfering polyatomics while preserving Si+; this gives a cleaner on-mass Si method than single-quadrupole operation in difficult matrices (takahashiUnknownyearsiliconwaferanalysis pages 44-46, yamanakaUnknownyeardeterminationoftrace pages 102-104) |
| O2 | Reaction gas used mainly in mass-shift mode; analyte ion reacts with O2 to form oxide product ions (MO+) detected at M+16, and in some cases higher oxide products such as SiO2+ can be monitored | 0.3-0.7 mL/min | Key for Si to SiO+ or SiO2+, Cr to CrO+ (52→68), and As to AsO+ (75→91); especially valuable when direct on-mass analysis suffers severe Ar-, C-, Cl-, or matrix-based polyatomics; very effective for elements that form stable oxides in the cell (takahashiUnknownyearsiliconwaferanalysis pages 69-71, takahashiUnknownyearsiliconwaferanalysis pages 71-73, takahashiUnknownyearsiliconwaferanalysis pages 64-66, yamanakaUnknownyeardeterminationoftrace pages 104-106, yamanakaUnknownyeardeterminationoftrace pages 122-124) | Q1 isolates the precursor mass before the cell, so product-mass isobars are rejected; e.g., only 52Cr enters for 52→68 and only 75As enters for 75→91, which is the central advantage of MS/MS over single-quad oxide chemistry (takahashiUnknownyearsiliconwaferanalysis pages 69-71, takahashiUnknownyearsiliconwaferanalysis pages 64-66, yamanakaUnknownyeardeterminationoftrace pages 104-106) |
| NH3 | Highly reactive gas usable in both on-mass and mass-shift/cluster-shift modes; forms reaction and cluster product ions, enabling selective chemistry for difficult analytes | Typically optimized per analyte; often used in the low-single-digit mL/min range | Most important for Ti via Ti-NH3 cluster formation (e.g., 48→114), V on-mass at 51 with reduced cell-generated background, and also Al and Mg when combined with cool/high-power cool plasma to suppress matrix-derived carbon/nitrogen polyatomics; particularly useful where S-based or matrix-based interferences defeat He alone (takahashiUnknownyearsiliconwaferanalysis pages 69-71, hsuUnknownyearanalysisofnanoparticles pages 69-71, shimamura2022multielementnanoparticleanalysis pages 69-71, takahashiUnknownyearsiliconwaferanalysis pages 106-108, hsuUnknownyearanalysisofnanoparticles pages 106-108) | Q1 is essential because NH3 is very reactive and can generate many cluster/product ions; MS/MS prevents non-target masses from entering the cell, which is why NH3 methods for Ti cluster-shift and V on-mass are much cleaner and more selective on the 8900 than in non-MS/MS reaction-cell operation (yamanakaUnknownyeardeterminationoftrace pages 44-47, takahashiUnknownyearsiliconwaferanalysis pages 69-71, hsuUnknownyearanalysisofnanoparticles pages 69-71, shimamura2022multielementnanoparticleanalysis pages 69-71) |


*Table: This table summarizes how He, H2, O2, and NH3 are used on the Agilent 8900 ICP-QQQ for aluminum-alloy digests. It highlights each gas’s mechanism, practical flow range, and why MS/MS improves interference control in complex Al-rich matrices.*

A practical multi-tune method for aluminum alloy digests typically includes 3–4 tune blocks:
1. **He KED mode:** Fe, Mn, Cu, Zn, Ni, Co, and other moderately interfered mid-mass elements (yamanakaUnknownyeardeterminationoftrace pages 44-47, shimamura2022multielementnanoparticleanalysis pages 71-73).
2. **H₂ on-mass mode:** Si at 28→28 (takahashiUnknownyearsiliconwaferanalysis pages 44-46).
3. **O₂ mass-shift mode:** Cr at 52→68 (and optionally As at 75→91 if needed) (takahashiUnknownyearsiliconwaferanalysis pages 69-71, hsuUnknownyearanalysisofnanoparticles pages 69-71).
4. **NH₃ mode (cool plasma + NH₃ or hot plasma + NH₃):** Ti at 48→114 (mass-shift), V at 51→51 (on-mass), and optionally Mg at 24→24 and Al at 27→27 using cool plasma + NH₃ (takahashiUnknownyearsiliconwaferanalysis pages 69-71, takahashiUnknownyearsiliconwaferanalysis pages 106-108, hsuUnknownyearanalysisofnanoparticles pages 106-108).

## 5. Internal Standards

Internal standards are essential for correcting matrix-induced signal suppression and instrumental drift. An ideal internal standard should be at a similar mass and ionization potential to the analytes it corrects, must not be present endogenously in the sample, and should not suffer spectral interferences (wilschefski2019inductivelycoupledplasma pages 9-10). The user's proposed set of five internal standards (Sc, Ge, Rh, In, Bi) provides excellent coverage across the full analyte mass range:

| Internal Standard | m/z | Ionization Potential (eV) | Analyte Mass Range Covered | Notes |
|---|---:|---:|---|---|
| Sc | 45 | 6.56 | Low mass; especially Mg-24, Al-27, Si-28 | Good low-mass internal standard because its mass is close to the light analytes and its ionization behavior is reasonably similar for routine ICP-MS correction. Avoid if Sc is expected in the sample. Typical IS spike: 50-100 µg/L. Monitor recovery; <20% deviation from the calibration average is generally acceptable. Match IS mass and ionization behavior to analytes whenever possible. (wilschefski2019inductivelycoupledplasma pages 9-10) |
| Ge | 72 | 7.90 | Mid-low mass; especially Ti-48, V-51, Cr-52, Mn-55, Fe-56 | Useful bridge internal standard for the transition from low-mass to mid-mass analytes. Can be appropriate for oxide-prone/interference-prone elements in this mass region, but may itself require interference review depending on matrix and cell mode. Typical IS spike: 50-100 µg/L. Monitor recovery; <20% deviation is a practical criterion. (wilschefski2019inductivelycoupledplasma pages 9-10) |
| Rh | 103 | 7.46 | Mid mass; especially Cu-63, Zn-64/66, Ni-58/60 | Commonly used and robust for mid-mass analytes. Good choice for alloy work when HCl is minimized; some Rh stock or matrix combinations involving chloride can complicate backgrounds, so nitric-acid matrices are preferred. Typical IS spike: 50-100 µg/L. Monitor recovery continuously across the run. (wilschefski2019inductivelycoupledplasma pages 9-10) |
| In | 115 | 5.79 | Mid-high mass; especially Sn and neighboring masses | Very common general-purpose internal standard in multi-element ICP-MS methods. Useful for analytes above Rh and below Bi, including Sn-region analytes. Typical IS spike: 50-100 µg/L. Check for stable recovery and use matrix-matched standards when matrix effects are strong. (wilschefski2019inductivelycoupledplasma pages 9-10, wolf2015multielementalanalysisof pages 5-7) |
| Bi | 209 | 7.29 | High mass; especially Pb-208 and nearby heavy elements | Preferred high-mass internal standard for Pb and other high-mass trace elements. Usually excellent for Pb correction in inorganic matrices; avoid only in unusual matrices where Bi contamination is plausible. Typical IS spike: 50-100 µg/L. Recovery should remain within about ±20% of expected response; larger drift suggests matrix suppression, deposition, or introduction problems. (wilschefski2019inductivelycoupledplasma pages 9-10) |


*Table: This table summarizes practical internal standard choices for aluminum-alloy ICP-QQQ analysis across the mass range. It is useful for building a first-pass method with Sc, Ge, Rh, In, and Bi while tracking matrix effects and drift.*

Add the internal standard mixture online via a mixing tee at the peristaltic pump, typically at 50–100 µg/L final concentration. Monitor IS recovery throughout the run; inter-sample recovery should remain within ±20% of the calibration blank value. Deviations exceeding 20% indicate matrix suppression, nebulizer blockage, or other problems requiring investigation (wilschefski2019inductivelycoupledplasma pages 9-10).

## 6. Plasma and Torch Settings

Typical Agilent 8900 operating conditions for high-matrix aqueous samples include:

- **RF Power:** 1500–1600 W for robust hot-plasma conditions. Higher RF power improves decomposition of matrix aerosol and reduces oxide formation, which is important in Al-rich matrices (rowley2000fundamentalstudiesof pages 73-79, hsuUnknownyearanalysisofnanoparticles pages 106-108, shimamura2022multielementnanoparticleanalysis pages 106-108). For cool-plasma measurements (Mg, Al with NH₃), the 8900 can achieve cool-plasma-like conditions by increasing the make-up gas flow while maintaining RF power at 1500 W, preserving plasma robustness (hsuUnknownyearanalysisofnanoparticles pages 106-108, shimamura2022multielementnanoparticleanalysis pages 106-108, takahashiUnknownyearsiliconwaferanalysis pages 106-108).

- **Sample Introduction:** PFA MicroFlow nebulizer (~0.1–0.4 mL/min uptake) with a quartz Scott-type double-pass spray chamber. A Peltier-cooled spray chamber (2–5 °C) reduces solvent vapor loading and oxide formation (lomaxvogt2019buildingadatabase pages 56-62, hsuUnknownyearanalysisofnanoparticles pages 12-13, takahashiUnknownyearsiliconwaferanalysis pages 12-13). For high-matrix alloy digests, a lower sample uptake rate reduces the total matrix load reaching the plasma.

- **Torch/Injector:** Quartz ShieldTorch with a 2.5 mm i.d. injector is standard. The shield plate reduces secondary discharge and lowers background, improving detection limits for challenging elements (hsuUnknownyearanalysisofnanoparticles pages 12-13, takahashiUnknownyearsiliconwaferanalysis pages 12-13).

- **Interface Cones:** Platinum-tipped sampler and skimmer cones with a brass skimmer base are standard. In high-Al matrices, cone blockage/deposition is a concern; clean cones regularly and monitor sensitivity trends during runs (hsuUnknownyearanalysisofnanoparticles pages 12-13, takahashiUnknownyearsiliconwaferanalysis pages 12-13).

- **Sampling Depth:** Typically 8–10 mm for robust hot-plasma operation; optimize to balance sensitivity against oxide and doubly charged formation. Shallower depths increase sensitivity but may worsen oxide ratios (rowley2000fundamentalstudiesof pages 73-79).

- **Carrier Gas Flow:** Typically ~1.0–1.1 L/min nebulizer Ar; optimize for best sensitivity and lowest oxide ratio (CeO⁺/Ce⁺ < 2–3%) and doubly charged ratio (Ce²⁺/Ce⁺ < 2–3%) (wilschefski2019inductivelycoupledplasma pages 10-12, lomaxvogt2019buildingadatabase pages 56-62).

## 7. Calibration and Quality Control

- **Matrix-matched standards:** Prepare calibration standards in a matrix-matched solution containing ~100–500 mg/L Al (high-purity Al standard in 2% HNO₃) to simulate the digested alloy matrix after dilution. This reduces systematic bias from matrix-dependent signal suppression (wolf2015multielementalanalysisof pages 5-7, wilschefski2019inductivelycoupledplasma pages 10-12).

- **Standard additions:** For the most accurate quantification in complex alloy digests, especially during initial method development, standard-additions calibration on representative samples is advisable. Isotope dilution is the most effective approach where applicable, though it requires enriched isotope spikes and is typically reserved for certification work (wilschefski2019inductivelycoupledplasma pages 10-12, wolf2015multielementalanalysisof pages 5-7).

- **QC samples:** Include certified reference materials (CRMs) for aluminum alloys, process blanks (acid blanks carried through the full digestion), calibration verification standards from an independent source (within ±10%), and continuing calibration verification (CCV) checks every 10–20 samples (wolf2015multielementalanalysisof pages 14-17).

- **Rinse protocol:** Between samples, rinse with 2–5% HNO₃ for 60–120 seconds. Al and Si can show memory effects; monitor blank levels after high-concentration samples and extend rinse times if carryover is observed.

## 8. Summary of Recommended Workflow

1. **Digest** alloy samples in HNO₃ (± small HF) by closed-vessel microwave digestion.
2. **Dilute** to bring TDS below ~0.1–0.2%; prepare two dilution levels for majors vs. traces.
3. **Add internal standards** (Sc, Ge, Rh, In, Bi at 50–100 µg/L) online.
4. **Run a multi-tune method** on the Agilent 8900 in MS/MS mode with He KED, H₂ on-mass, O₂ mass-shift, and NH₃ on-mass/mass-shift tunes.
5. **Calibrate** with matrix-matched standards; verify with CRMs and independent QC standards.
6. **Monitor** IS recovery, oxide/doubly charged ratios, and rinse blanks throughout the run.

This approach leverages the full capability of the Agilent 8900 ICP-QQQ's tandem mass spectrometry to resolve the complex spectral interferences inherent in aluminum-alloy nitric acid digests while managing the extreme matrix challenge of a >85% aluminum sample.

References

1. (wilschefski2019inductivelycoupledplasma pages 10-12): Scott Wilschefski and Matthew Baxter. Inductively coupled plasma mass spectrometry: introduction to analytical aspects. Aug 2019. URL: https://doi.org/10.33176/aacb-19-00024, doi:10.33176/aacb-19-00024. This article has 1151 citations.

2. (lotter2014analysisofzirconium pages 107-112): SJ Lotter. Analysis of zirconium containing materials using multiple digestion and spectrometric techniques. Unknown journal, 2014.

3. (wilschefski2019inductivelycoupledplasma pages 9-10): Scott Wilschefski and Matthew Baxter. Inductively coupled plasma mass spectrometry: introduction to analytical aspects. Aug 2019. URL: https://doi.org/10.33176/aacb-19-00024, doi:10.33176/aacb-19-00024. This article has 1151 citations.

4. (wolf2015multielementalanalysisof pages 5-7): Ruth E. Wolf and Monique Adams. Multi-elemental analysis of aqueous geochemical samples by quadrupole inductively coupled plasma-mass spectrometry (icp-ms). ArXiv, Jan 2015. URL: https://doi.org/10.3133/ofr20151010, doi:10.3133/ofr20151010. This article has 27 citations.

5. (yamanakaUnknownyeardeterminationoftrace pages 44-47): M Yamanaka and K Yamanaka. Determination of trace elements in ultrapure semiconductor grade sulfuric acid using the agilent 8900 icp-qqq in ms/ms mode. Unknown journal, Unknown year.

6. (takahashiUnknownyearsiliconwaferanalysis pages 69-71): J Takahashi. Silicon wafer analysis by icp-qqq: determination of phosphorus and titanium in a high silicon matrix. Unknown journal, Unknown year.

7. (hsuUnknownyearanalysisofnanoparticles pages 69-71): D Hsu, Y Shimamura, B Liao, and M Yamanaka. Analysis of nanoparticles in organic reagents by agilent 8900 icp-qqq in spicp-ms mode. Unknown journal, Unknown year.

8. (takahashiUnknownyearsiliconwaferanalysis pages 106-108): J Takahashi. Silicon wafer analysis by icp-qqq: determination of phosphorus and titanium in a high silicon matrix. Unknown journal, Unknown year.

9. (shimamura2022multielementnanoparticleanalysis pages 106-108): Y Shimamura and D Hsu. Multielement nanoparticle analysis of semiconductor process chemicals using spicp-qqq. Unknown journal, 2022.

10. (yamanakaUnknownyeardeterminationoftrace pages 35-37): M Yamanaka and K Yamanaka. Determination of trace elements in ultrapure semiconductor grade sulfuric acid using the agilent 8900 icp-qqq in ms/ms mode. Unknown journal, Unknown year.

11. (takahashiUnknownyearsiliconwaferanalysis pages 44-46): J Takahashi. Silicon wafer analysis by icp-qqq: determination of phosphorus and titanium in a high silicon matrix. Unknown journal, Unknown year.

12. (yamanakaUnknownyeardeterminationoftrace pages 104-106): M Yamanaka and K Yamanaka. Determination of trace elements in ultrapure semiconductor grade sulfuric acid using the agilent 8900 icp-qqq in ms/ms mode. Unknown journal, Unknown year.

13. (takahashiUnknownyearsiliconwaferanalysis pages 90-92): J Takahashi. Silicon wafer analysis by icp-qqq: determination of phosphorus and titanium in a high silicon matrix. Unknown journal, Unknown year.

14. (hsuUnknownyearanalysisofnanoparticles pages 106-108): D Hsu, Y Shimamura, B Liao, and M Yamanaka. Analysis of nanoparticles in organic reagents by agilent 8900 icp-qqq in spicp-ms mode. Unknown journal, Unknown year.

15. (lomaxvogt2019buildingadatabase pages 72-78): MC Lomax-Vogt. Building a database of spectral overlap ions for inductively coupled plasma mass spectrometry (icp-ms). Unknown journal, 2019.

16. (lomaxvogt2019buildingadatabase pages 20-23): MC Lomax-Vogt. Building a database of spectral overlap ions for inductively coupled plasma mass spectrometry (icp-ms). Unknown journal, 2019.

17. (rowley2000fundamentalstudiesof pages 41-47): LK Rowley. Fundamental studies of interferences in icp-ms. Unknown journal, 2000.

18. (lomaxvogt2019buildingadatabase pages 108-113): MC Lomax-Vogt. Building a database of spectral overlap ions for inductively coupled plasma mass spectrometry (icp-ms). Unknown journal, 2019.

19. (takahashiUnknownyearsiliconwaferanalysis pages 71-73): J Takahashi. Silicon wafer analysis by icp-qqq: determination of phosphorus and titanium in a high silicon matrix. Unknown journal, Unknown year.

20. (shimamura2022multielementnanoparticleanalysis pages 69-71): Y Shimamura and D Hsu. Multielement nanoparticle analysis of semiconductor process chemicals using spicp-qqq. Unknown journal, 2022.

21. (takahashiUnknownyearsiliconwaferanalysis pages 64-66): J Takahashi. Silicon wafer analysis by icp-qqq: determination of phosphorus and titanium in a high silicon matrix. Unknown journal, Unknown year.

22. (shimamura2022multielementnanoparticleanalysis pages 71-73): Y Shimamura and D Hsu. Multielement nanoparticle analysis of semiconductor process chemicals using spicp-qqq. Unknown journal, 2022.

23. (hsuUnknownyearanalysisofnanoparticles pages 90-92): D Hsu, Y Shimamura, B Liao, and M Yamanaka. Analysis of nanoparticles in organic reagents by agilent 8900 icp-qqq in spicp-ms mode. Unknown journal, Unknown year.

24. (yamanakaUnknownyeardeterminationoftrace pages 102-104): M Yamanaka and K Yamanaka. Determination of trace elements in ultrapure semiconductor grade sulfuric acid using the agilent 8900 icp-qqq in ms/ms mode. Unknown journal, Unknown year.

25. (yamanakaUnknownyeardeterminationoftrace pages 122-124): M Yamanaka and K Yamanaka. Determination of trace elements in ultrapure semiconductor grade sulfuric acid using the agilent 8900 icp-qqq in ms/ms mode. Unknown journal, Unknown year.

26. (rowley2000fundamentalstudiesof pages 73-79): LK Rowley. Fundamental studies of interferences in icp-ms. Unknown journal, 2000.

27. (lomaxvogt2019buildingadatabase pages 56-62): MC Lomax-Vogt. Building a database of spectral overlap ions for inductively coupled plasma mass spectrometry (icp-ms). Unknown journal, 2019.

28. (hsuUnknownyearanalysisofnanoparticles pages 12-13): D Hsu, Y Shimamura, B Liao, and M Yamanaka. Analysis of nanoparticles in organic reagents by agilent 8900 icp-qqq in spicp-ms mode. Unknown journal, Unknown year.

29. (takahashiUnknownyearsiliconwaferanalysis pages 12-13): J Takahashi. Silicon wafer analysis by icp-qqq: determination of phosphorus and titanium in a high silicon matrix. Unknown journal, Unknown year.

30. (wolf2015multielementalanalysisof pages 14-17): Ruth E. Wolf and Monique Adams. Multi-elemental analysis of aqueous geochemical samples by quadrupole inductively coupled plasma-mass spectrometry (icp-ms). ArXiv, Jan 2015. URL: https://doi.org/10.3133/ofr20151010, doi:10.3133/ofr20151010. This article has 27 citations.