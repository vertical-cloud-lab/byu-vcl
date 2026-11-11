Question: For SEM-EDS quantitative characterization of AlSi10Mg LPBF samples (cast or AM) to recover the Mg content (0.2-0.45 wt% nominal) and confirm the alloy composition per ASTM E1508-12AR19:
1. Recommended accelerating voltage (kV): trade-offs between 10, 15, 20 kV for Mg/Al/Si K-line excitation, interaction volume, and absorption of soft Mg Kα.
2. Recommended beam current / probe current / dead-time target. ASTM E1508 says 20-30 % dead time; how much beam current does that require on a typical Schottky FEG (Apreo/Helios/etc.) with an Octane Plus SDD?
3. Live time: how long is required to get statistically meaningful Mg counts at 0.3 wt% Mg in Al with a 30 mm² SDD? Provide a rule-of-thumb or formula.
4. Amplifier time constant: ASTM E1508 favors longer amp times for trace work; what is the optimal value for resolving Mg Kα from Al Kα tail?
5. Working distance, take-off angle, magnification: optimal values and why. Is the change from 48.7° take-off (non-flat sample) to 35° (polished) likely to cause a problem?
6. Standards: which Mg-bearing standards (pure Mg, MgO, Mg2Si, NIST SRM AlSi alloys) should be used, and how often should they be re-measured?
7. Sample-prep workflow per ASTM E1078: metallographic mount in conductive epoxy, grind through 320/600/1200/2400 SiC, polish through 6/3/1 µm diamond + 0.05 µm colloidal silica, ultrasonic clean, dry, mount on stub with conductive tape and silver paint, optional carbon coat (~10 nm). Anything specific for AlSi10Mg / soft Al alloys (avoid smearing, recommended polishing time/load)?
8. ICP-OES cross-validation: how often, and what's a reasonable accuracy expectation for ICP-OES Mg measurements on AlSi10Mg?
Provide a concrete, parameter-by-parameter SOP. Cite ASTM E1508-12AR19, ASTM E1078-14R20, Goldstein et al. (4th ed.), NIST DTSA-II/EPQ, EDAX TEAM application notes, and recent AlSi10Mg LPBF characterization papers.

## SEM-EDS Standard Operating Procedure for Quantitative Characterization of AlSi10Mg LPBF Samples: Recovery of Mg Content (0.2–0.45 wt% Nominal)

The following SOP provides parameter-by-parameter guidance for SEM-EDS quantitative analysis of AlSi10Mg alloy (cast or additively manufactured by laser powder bed fusion, LPBF), with the specific goal of recovering the Mg content at its nominal 0.2–0.45 wt% level. The recommendations are synthesized from the ASTM E1508-12a(R19) standard for quantitative EDS analysis, the Goldstein et al. textbook on SEM/X-ray microanalysis, NIST DTSA-II methodology, and recent AlSi10Mg characterization literature.

The consolidated parameter recommendations are provided in the table below:

| Parameter | Recommended Value / Notes |
|---|---|
| Accelerating voltage (kV) | **15 kV recommended for routine quantitative AlSi10Mg bulk checks.** Tradeoff: **10 kV** gives smaller interaction volume and less absorption error for soft Mg Kα, but lower total count rate and greater sensitivity to surface oxide/contamination; **15 kV** keeps overvoltage high for Mg/Al/Si K lines while reducing interaction volume and absorption relative to 20 kV; **20 kV** maximizes excitation and count rate but increases X-ray generation depth, self-absorption, and matrix-correction burden for low-energy Mg Kα. For bulk polished AlSi10Mg, 15 kV is the best compromise; use 10 kV only when near-surface resolution is more important than throughput, and 20 kV mainly for comparison with legacy workflows or if count rate is limiting (goldstein2003specialtopicsin pages 46-52, goldstein2003specialtopicsin pages 77-82, small2002theanalysisof pages 6-7, hua2004estimatingmethodfor pages 3-5, hua2004estimatingmethodfor pages 1-3). |
| Beam current / probe current / dead time | **Target SDD dead time: ~10% preferred for trace Mg work; ASTM E1508 allows 20–30%.** In practice on a Schottky FEG SEM with a 30 mm² SDD, this is commonly reached at about **0.5–5 nA**, but the exact current is geometry- and detector-dependent, so tune current empirically on a high-flux Al standard at the chosen WD and kV. Higher dead time raises throughput but increases coincidence/sum-peak risk; Newbury recommends conservative dead time for trace work, especially when measuring weak Mg on an Al-rich matrix (newbury2015performingelementalmicroanalysis pages 11-13, newbury2014rigorousquantitativeelemental pages 14-15, newbury*2013isscanningelectron pages 7-9, newbury2015performingelementalmicroanalysis pages 20-21). |
| Live time | **Rule of thumb: 120–300 s live time** for ~0.3 wt% Mg in polished AlSi10Mg with a 30 mm² SDD at 15 kV and low dead time, assuming stable beam and standards-based fitting. Use the counting-statistics expression: **CDL = 3·sqrt(NB)/(NS−NB) · CS** and solve for time using count rates from a Mg-bearing standard. For planning, **t ≈ [3·sqrt(bS)·CS / ((sS−bS)·Ctarget)]²**. For stronger confidence in minor-Mg recovery and replicate averaging, **200–300 s** is a practical SOP default (newbury2014rigorousquantitativeelemental pages 12-14, newbury2015performingelementalmicroanalysis pages 20-21, newbury2016measurementoftrace pages 1-2, newbury2019electronexcitedxraymicroanalysis pages 13-15). |
| Amplifier time constant / process time | **Medium process time, about 0.5–1.0 µs, recommended.** Modern SDDs achieve ~127.5 eV FWHM at Mn Kα at ~470 ns peaking time; somewhat longer shaping improves resolution at the cost of throughput. Because Mg Kα (1.254 keV) and Al Kα (1.487 keV) are separated by ~233 eV, they are generally resolvable with a modern SDD, but medium/longer shaping helps suppress tailing and improves peak fitting for low-level Mg in Al-rich spectra. Avoid very fast settings unless throughput is the overriding need (teng2020highresolutionxray pages 27-31, newbury2014rigorousquantitativeelemental pages 5-6, teng2020highresolutionxray pages 71-77, newbury*2013isscanningelectron pages 5-7, goldstein2018quantitativeanalysisthe pages 1-4). |
| Working distance / take-off angle / magnification | **WD: 10–15 mm; TOA: ~35° minimum, higher if instrument geometry allows; magnification: ~500–1000× for bulk composition points on flat, representative fields.** Shorter WD improves solid angle and count rate, but avoid so short a WD that pole-piece/geometry artifacts appear. Higher take-off angle shortens absorption path length and is especially beneficial for Mg Kα. A change from **48.7° to 35°** is usually acceptable on a flat polished specimen if standards and unknowns are acquired at the same geometry, but lower TOA increases absorption sensitivity, so it becomes less forgiving of residual relief, pores, or tilt. Keep specimen tilt at 0° for quantitative work (xing2016informationorresolution pages 10-11, newbury*2013isscanningelectron pages 18-19, newbury2012faultsandfoibles pages 5-7, newbury*2013isscanningelectron pages 5-7, newbury2012faultsandfoibles pages 7-9). |
| Standards | **Use standards-based k-ratio quantification, not standardless.** Recommended set: **pure Mg** (best elemental sensitivity if oxidation is controlled), **MgO** (stable Mg-bearing compound), optionally **Mg₂Si** if phase-matched standards are available, plus **pure Al** and **pure Si** or well-characterized compounds. **NIST SRM 470 / K412 glass** is useful because it contains Mg, Al, and Si in one homogeneous reference. Re-measure standards at session start, after major parameter changes, and at least every **4–8 h** or once per shift as a QA check; archived spectra are acceptable only if beam energy, geometry, and detector settings are verified unchanged (newbury2015performingelementalmicroanalysis pages 11-13, heinrich2013electronprobequantitation pages 257-258, newbury2014rigorousquantitativeelemental pages 2-5, heinrich2013electronprobequantitation pages 249-252). |
| Sample preparation workflow | **Conductive mount → grind (e.g., 320/600/1200/2400 SiC) → polish 6/3/1 µm diamond → final 0.05 µm colloidal silica → ultrasonic clean → dry → conductive mounting to stub → optional thin carbon coat (~10 nm).** For soft Al alloys, use the finest practical starting grit, low loads, flat woven cloths, ample lubricant, short polishing intervals, full scratch removal between steps, and consider **20+ min vibratory final polish** to minimize smearing/deformation. Avoid etched surfaces for quantitative EDS; flat polished, unetched surfaces are preferred (newbury2015performingelementalmicroanalysis pages 11-13, newbury2014rigorousquantitativeelemental pages 2-5, voort2006metallographicpreparationfor pages 2-3, voort2006metallographicpreparationfor pages 1-2, jiao2019microstructurecharacterizationof pages 1-2, jiao2019microstructurecharacterizationof pages 2-3, voort2006metallographicpreparationfor pages 3-5). |
| ICP-OES cross-validation | **Cross-check SEM-EDS against ICP-OES for each new powder lot, each process/material change, and at least quarterly for stable production; more conservatively, once per batch for qualification work.** For AlSi10Mg, reported ICP/OES-type Mg results include **0.32 ± 0.01 wt%** for feedstock powder and **0.073 ± 0.001 wt%** for one additive sample showing Mg loss/off-spec chemistry. Bulk OES/ICP methods are materially more precise than SEM-EDS for low-level Mg; a reasonable expectation is about **±3–5% relative** for well-run ICP-OES at 0.2–0.45 wt% Mg, with SEM-EDS serving as the microanalytical confirmation tool rather than the sole release method (brumbach2016compositionalanalysisfor pages 10-15, kallio2025accuracyandprecision pages 51-55, luttergunther2018spatterformationduring pages 3-4). |


*Table: This table summarizes recommended operating conditions, standards, specimen preparation, and cross-validation practices for quantitative SEM-EDS recovery of Mg in AlSi10Mg LPBF samples. It is designed as a practical SOP-style reference grounded in the cited evidence.*

---

### 1. Accelerating Voltage: 15 kV Recommended

The critical excitation energies for the K-lines of interest are: Mg Kα = 1.254 keV (E_c = 1.305 keV), Al Kα = 1.487 keV (E_c = 1.560 keV), and Si Kα = 1.740 keV (E_c = 1.839 keV). For efficient X-ray generation, the overvoltage ratio U = E₀/E_c should be at least 2, and ideally 2–5 for light elements (goldstein2003specialtopicsin pages 46-52, kallio2025accuracyandprecision pages 15-20). At 15 kV, the overvoltage ratios are approximately U_Mg ≈ 11.5, U_Al ≈ 9.6, and U_Si ≈ 8.2, all well above the minimum threshold, ensuring strong K-line excitation for all three elements.

The key tradeoffs are as follows. At **10 kV**, interaction volume in Al is ~1.0 µm depth, absorption corrections for Mg Kα are minimized, and the smaller excitation volume improves spatial resolution (small2002theanalysisof pages 6-7, hua2004estimatingmethodfor pages 3-5). However, the total X-ray yield is lower, the peak-to-background ratio for Mg decreases, and the spectrum becomes more sensitive to surface oxide layers and carbon contamination (goldstein2003specialtopicsin pages 77-82). At **20 kV**, X-ray count rates are maximized, and published NIST DTSA-II benchmarks use this voltage extensively—for example, achieving Mg detection limits of ~190 ppm (0.019 wt%) in NIST glass K523 at E₀ = 20 keV with a 200 s acquisition (newbury2014rigorousquantitativeelemental pages 12-14). However, the interaction volume in Al increases to ~3.4 µm (hua2004estimatingmethodfor pages 3-5), self-absorption of the soft Mg Kα line becomes more severe, and the ZAF absorption correction grows substantially. At **15 kV**, one obtains a good balance: strong excitation, moderate interaction volume (~2.0 µm in Al), and manageable absorption corrections. This voltage is also commonly used in quantitative Mg–Al–Zn alloy microanalysis (teng2019thefratioquantificationa pages 5-6).

### 2. Beam Current and Dead-Time Target

ASTM E1508-12a(R19) specifies a target dead time of 20–30% for conventional Si(Li) detectors. However, for modern SDD-EDS systems, Newbury and Ritchie recommend a more conservative dead time of approximately 10% to substantially suppress coincidence (sum) peaks, which can interfere with trace-element identification (newbury2014rigorousquantitativeelemental pages 14-15, newbury*2013isscanningelectron pages 7-9). A practical example from the literature used a QUAD SDD at 11% dead time with an output count rate (OCR) of 133 kHz and a 440 ns time constant (newbury2014rigorousquantitativeelemental pages 12-14).

On a typical Schottky FEG SEM (e.g., Apreo, Helios) with a 30 mm² Octane Plus SDD at a working distance of 10–15 mm, ~10% dead time is generally achieved at a beam current of approximately **0.5–5 nA**, depending on the exact detector-to-specimen geometry and solid angle. The beam current should be measured with a Faraday cup and digital picoammeter, and the detector dead time verified on a high-flux target such as pure Al or Si at the operational kV and WD before commencing measurements (newbury2015performingelementalmicroanalysis pages 11-13, newbury*2013isscanningelectron pages 7-9).

### 3. Live Time: 120–300 s Rule of Thumb

The concentration limit of detection (CDL) for EDS follows counting statistics as described by Newbury and Ritchie: **CDL = 3·√N_B / (N_S − N_B) · C_S**, where N_S and N_B are the integrated peak and background counts, respectively, and C_S is the standard concentration (newbury2014rigorousquantitativeelemental pages 12-14, newbury2015performingelementalmicroanalysis pages 20-21, newbury2016measurementoftrace pages 1-2, newbury2019electronexcitedxraymicroanalysis pages 13-15). The analogous "quantifiable level" (Currie criterion) is C_Quant = 10·√N_B / N_S · C_S (newbury2016measurementoftrace pages 1-2).

Since both N_S and N_B scale linearly with live time t, and peak/background count rates (s_S, b_S) are measurable on a Mg-bearing standard, the required live time to reach a target CDL (e.g., C_target = 0.003, i.e., 0.3 wt%) can be estimated as:

**t ≈ [3·√b_S · C_S / ((s_S − b_S) · C_target)]²**

In practice, for a 30 mm² SDD at 15 kV and ~10% dead time on an Al-rich matrix, achieving reliable quantification at 0.3 wt% Mg (well above typical CDL values of ~200 ppm achievable in 200 s) requires **120–300 s** live time per analysis point (newbury2014rigorousquantitativeelemental pages 12-14, newbury2015performingelementalmicroanalysis pages 20-21). For the SOP, a default of **200 s** provides a comfortable margin for statistical reliability and replicate averaging.

### 4. Amplifier Time Constant / Process Time

The EDS amplifier time constant (shaping time, peaking time, or process time) directly controls the tradeoff between energy resolution and maximum count rate. A modern SDD at a medium peaking time of ~470 ns achieves approximately 127.5 eV FWHM at Mn Kα (5.9 keV) (newbury2014rigorousquantitativeelemental pages 5-6). Energy resolution at the Mg Kα energy (~1.25 keV) is somewhat better (narrower), scaling with √E.

The separation between Mg Kα (1.254 keV) and Al Kα (1.487 keV) is ~233 eV, which exceeds the FWHM of a modern SDD by a comfortable margin; the two peaks are therefore well resolved even at medium process times. However, for trace-level Mg in an Al-rich matrix, the high-energy tail of the dominant Al Kα peak can encroach on the Mg peak region, making FWHM minimization important. Longer process times (~1.0 µs) reduce electronic noise and improve FWHM, which in turn improves the accuracy of MLLSQ peak fitting (teng2020highresolutionxray pages 27-31, teng2020highresolutionxray pages 71-77, newbury*2013isscanningelectron pages 5-7). Conversely, very short process times (< 300 ns) increase throughput but degrade resolution to ~180 eV or worse (struder1998highresolutionxrayspectroscopy pages 3-6).

**Recommendation:** Use a medium-to-long process time of **0.5–1.0 µs** (corresponding to the "best resolution" or "medium" setting on most EDAX TEAM or similar software) to achieve FWHM ≤ 130 eV at Mn Kα. Confirm that standards and unknowns are acquired at the identical process-time setting (goldstein2018quantitativeanalysisthe pages 1-4).

### 5. Working Distance, Take-Off Angle, and Magnification

**Working distance (WD):** 10–15 mm. A shorter analytical WD (~8–10 mm) increases the solid angle of the EDS detector and thus count rates, but excessively short WDs risk spurious X-rays from BSEs hitting the pole piece (xing2016informationorresolution pages 10-11). For most FEG-SEMs with side-mounted SDDs, the manufacturer's "analytical working distance" (typically 10 mm) is optimal.

**Take-off angle (TOA):** A higher take-off angle reduces the X-ray absorption path length through the specimen, which is critical for low-energy lines like Mg Kα. Newbury demonstrated that on rough surfaces, Mg Kα intensity can vary by a factor of 5× depending on local surface orientation relative to the detector, due to the strong energy dependence of mass absorption coefficients (newbury2012faultsandfoibles pages 7-9). A TOA of **35° or higher** is recommended for flat polished samples. The change from 48.7° (as may occur on non-flat or as-built AM surfaces) to 35° (standard polished geometry) is acceptable provided that (a) all specimens and standards are measured at the same geometry and (b) the specimen surface is truly flat and polished. The lower TOA increases the absorption path length somewhat, making the measurement more sensitive to residual relief, porosity, and tilt, but on a well-polished flat specimen the ZAF correction adequately accounts for this (newbury*2013isscanningelectron pages 18-19, newbury2012faultsandfoibles pages 5-7, newbury*2013isscanningelectron pages 5-7).

**Magnification:** 500–1000× is appropriate for bulk composition analysis of representative areas. At this magnification, the beam raster covers a field of ~100–250 µm, averaging over multiple Al cells and Si-rich eutectic regions in the LPBF microstructure. For phase-specific analysis (e.g., Mg₂Si precipitates), higher magnification and spot analysis may be needed.

**Specimen tilt:** Maintain 0° tilt for quantitative analysis to preserve the calibrated geometry.

### 6. Standards

Standards-based k-ratio quantification yields far superior accuracy compared to standardless methods: 95% of analyses fall within ±5% relative of the correct value (newbury2014rigorousquantitativeelemental pages 2-5). The recommended standard set includes:

- **Pure Mg** (polished, stored under vacuum or inert atmosphere to prevent oxidation): provides the best sensitivity calibration for Mg Kα.
- **MgO** (polished single crystal or sintered pellet): a stable alternative if pure Mg oxidation is a concern; requires oxygen correction.
- **Pure Al** and **pure Si** for the matrix elements.
- **NIST SRM 470 (K412 glass):** contains Mg (11.9 wt% MgO), Al₂O₃, SiO₂, CaO, and FeO in a homogeneous glass—ideal as a multi-element secondary check standard that simultaneously tests Mg, Al, and Si quantification (newbury2015performingelementalmicroanalysis pages 11-13, heinrich2013electronprobequantitation pages 257-258).
- **Mg₂Si** (if available) provides a phase-matched Mg-in-Si compound standard useful for verifying absorption corrections.

**Re-measurement frequency:** Acquire standard spectra at the start of each analytical session, after any parameter change (kV, WD, process time), and as a QA check every 4–8 hours or at least once per shift. Archived standard spectra may be reused if a quality-assurance protocol confirms that current measurement conditions match the archived conditions (newbury2015performingelementalmicroanalysis pages 11-13, heinrich2013electronprobequantitation pages 249-252).

### 7. Sample Preparation Workflow

Following ASTM E1078-14(R20) and best practices for soft FCC metals (voort2006metallographicpreparationfor pages 2-3, voort2006metallographicpreparationfor pages 1-2, jiao2019microstructurecharacterizationof pages 1-2, jiao2019microstructurecharacterizationof pages 2-3, voort2006metallographicpreparationfor pages 3-5):

1. **Sectioning:** Use a precision saw with a thin abrasive blade at low force to minimize deformation.
2. **Mounting:** Embed in conductive epoxy (e.g., Struers PolyFast, Buehler Konductomet) to ensure electrical grounding without carbon tape artifacts.
3. **Grinding:** Progressive SiC paper: 320 → 600 → 1200 → 2400 grit. Use copious water lubrication. For soft Al alloys, use the finest possible starting grit that removes sectioning damage; apply low loads (~10–15 N per specimen on auto-polisher). Ensure full removal of the previous scratch pattern at each step. Ultrasonic clean between grit changes.
4. **Polishing:** 6 µm → 3 µm → 1 µm diamond suspension on flat woven cloths (silk, nylon, or polyurethane pads), using appropriate extender lubricant. For AlSi10Mg, keep polishing times short per step (1–3 min) at low loads to minimize smearing of the soft α-Al matrix over Si-rich eutectic regions (voort2006metallographicpreparationfor pages 1-2).
5. **Final polish:** 0.05 µm colloidal silica (e.g., MasterMet 2) on a chemically resistant pad. A **vibratory polish of ≥ 20 minutes** is strongly recommended for Al alloys to remove the final layer of deformation and polishing-induced smearing without introducing new damage (voort2006metallographicpreparationfor pages 2-3, voort2006metallographicpreparationfor pages 3-5).
6. **Cleaning:** Ultrasonic clean in ethanol or isopropanol, dry with filtered compressed air or nitrogen.
7. **Mounting to stub:** Conductive carbon tape plus silver paint around the perimeter for grounding.
8. **Carbon coating:** Apply ~10 nm amorphous carbon by evaporation if charging is observed; however, for a metallic sample in conductive mount, coating may be optional provided the mount provides a good ground path to the stub. If coating is applied, note that carbon contributes to the continuum background and must be accounted for in the ZAF correction.

Surface quality target: roughness < 50 nm rms for reliable low-energy X-ray quantification (newbury2015performingelementalmicroanalysis pages 11-13, newbury2014rigorousquantitativeelemental pages 2-5). Do not etch the surface for quantitative EDS.

### 8. ICP-OES Cross-Validation

ICP-OES (or ICP-MS) is the most precise bulk technique for elemental analysis of Al alloys, with reported RSD values ≤ 8 for low-concentration elements (kallio2025accuracyandprecision pages 51-55). Published ICP-OES data for AlSi10Mg include Mg = 0.32 ± 0.01 wt% for feedstock powder (luttergunther2018spatterformationduring pages 3-4) and Mg = 0.073 ± 0.001 wt% for one additively manufactured sample that showed significant Mg loss (brumbach2016compositionalanalysisfor pages 10-15). These results demonstrate that ICP-OES provides both the sensitivity and precision needed to detect off-specification Mg levels that SEM-EDS alone may struggle to resolve quantitatively.

**Recommended cross-validation schedule:**
- At initial qualification of a new powder lot or process change: ICP-OES on ≥ 3 dissolution replicates.
- During production: at least quarterly, or once per build batch for qualification-critical parts.
- Whenever SEM-EDS results deviate from nominal by > 0.05 wt% Mg, confirm by ICP-OES.

**Accuracy expectation:** For well-run ICP-OES at Mg concentrations of 0.2–0.45 wt% in dissolved AlSi10Mg samples, a relative accuracy of ±3–5% (i.e., ±0.01–0.02 wt% absolute at 0.3 wt% Mg) is a reasonable expectation (farinas2016determinationofrare pages 8-12). SEM-EDS should be regarded as the microanalytical tool for verifying spatial homogeneity and phase-specific composition, not as the sole release measurement for bulk Mg content.

---

**Summary.** For quantitative SEM-EDS recovery of Mg at 0.2–0.45 wt% in AlSi10Mg, use 15 kV, ~10% dead time on an SDD (~0.5–5 nA on a Schottky FEG), 200 s live time, a medium-to-long process time (0.5–1.0 µs), standards-based k-ratio quantification with pure Mg (or MgO) and NIST SRM 470 as check standard, and a carefully controlled metallographic preparation designed to prevent smearing of the soft Al matrix. Cross-validate against ICP-OES for each powder lot. This protocol ensures that the 0.3 wt% Mg signal is comfortably above the EDS detection limit (~200 ppm) and that systematic errors from absorption, geometry, and specimen preparation are minimized.

References

1. (goldstein2003specialtopicsin pages 46-52): Joseph I. Goldstein, Dale E. Newbury, Patrick Echlin, David C. Joy, Charles E. Lyman, Eric Lifshin, Linda Sawyer, and Joseph R. Michael. Special topics in electron beam x-ray microanalysis. ArXiv, pages 453-536, Jan 2003. URL: https://doi.org/10.1007/978-1-4615-0215-9\_10, doi:10.1007/978-1-4615-0215-9\_10. This article has 41 citations.

2. (goldstein2003specialtopicsin pages 77-82): Joseph I. Goldstein, Dale E. Newbury, Patrick Echlin, David C. Joy, Charles E. Lyman, Eric Lifshin, Linda Sawyer, and Joseph R. Michael. Special topics in electron beam x-ray microanalysis. ArXiv, pages 453-536, Jan 2003. URL: https://doi.org/10.1007/978-1-4615-0215-9\_10, doi:10.1007/978-1-4615-0215-9\_10. This article has 41 citations.

3. (small2002theanalysisof pages 6-7): J.A. Small. The analysis of particles at low accelerating voltages (&lt;= 10 kv) with energy dispersive x-ray spectroscopy (eds). Journal of Research of the National Institute of Standards and Technology, 107:555, Nov 2002. URL: https://doi.org/10.6028/jres.107.047, doi:10.6028/jres.107.047. This article has 63 citations and is from a peer-reviewed journal.

4. (hua2004estimatingmethodfor pages 3-5): Younan Hua. Estimating method for electron beam accelerating voltage used in energy‐dispersive x‐ray microanalysis: application in failure analysis of wafer fabrication. Instrumentation Science & Technology, 32:115-126, Dec 2004. URL: https://doi.org/10.1081/ci-120028765, doi:10.1081/ci-120028765. This article has 7 citations and is from a peer-reviewed journal.

5. (hua2004estimatingmethodfor pages 1-3): Younan Hua. Estimating method for electron beam accelerating voltage used in energy‐dispersive x‐ray microanalysis: application in failure analysis of wafer fabrication. Instrumentation Science & Technology, 32:115-126, Dec 2004. URL: https://doi.org/10.1081/ci-120028765, doi:10.1081/ci-120028765. This article has 7 citations and is from a peer-reviewed journal.

6. (newbury2015performingelementalmicroanalysis pages 11-13): Dale E. Newbury and Nicholas W. M. Ritchie. Performing elemental microanalysis with high accuracy and high precision by scanning electron microscopy/silicon drift detector energy-dispersive x-ray spectrometry (sem/sdd-eds). Journal of Materials Science, 50:493-518, Nov 2015. URL: https://doi.org/10.1007/s10853-014-8685-2, doi:10.1007/s10853-014-8685-2. This article has 553 citations and is from a peer-reviewed journal.

7. (newbury2014rigorousquantitativeelemental pages 14-15): Dale E. Newbury and Nicholas W. M. Ritchie. Rigorous quantitative elemental microanalysis by scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds) with spectrum processing by nist dtsa-ii. SPIE Proceedings, 9236:92360H, Sep 2014. URL: https://doi.org/10.1117/12.2065842, doi:10.1117/12.2065842. This article has 24 citations.

8. (newbury*2013isscanningelectron pages 7-9): Dale E. Newbury* and Nicholas W. M. Ritchie. Is scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds) quantitative? Scanning, 35 3:141-68, May 2013. URL: https://doi.org/10.1002/sca.21041, doi:10.1002/sca.21041. This article has 729 citations.

9. (newbury2015performingelementalmicroanalysis pages 20-21): Dale E. Newbury and Nicholas W. M. Ritchie. Performing elemental microanalysis with high accuracy and high precision by scanning electron microscopy/silicon drift detector energy-dispersive x-ray spectrometry (sem/sdd-eds). Journal of Materials Science, 50:493-518, Nov 2015. URL: https://doi.org/10.1007/s10853-014-8685-2, doi:10.1007/s10853-014-8685-2. This article has 553 citations and is from a peer-reviewed journal.

10. (newbury2014rigorousquantitativeelemental pages 12-14): Dale E. Newbury and Nicholas W. M. Ritchie. Rigorous quantitative elemental microanalysis by scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds) with spectrum processing by nist dtsa-ii. SPIE Proceedings, 9236:92360H, Sep 2014. URL: https://doi.org/10.1117/12.2065842, doi:10.1117/12.2065842. This article has 24 citations.

11. (newbury2016measurementoftrace pages 1-2): Dale E. Newbury and Nicholas W. M. Ritchie. Measurement of trace constituents by electron-excited x-ray microanalysis with energy-dispersive spectrometry. Microscopy and Microanalysis, 22:520-535, May 2016. URL: https://doi.org/10.1017/s1431927616000738, doi:10.1017/s1431927616000738. This article has 32 citations and is from a peer-reviewed journal.

12. (newbury2019electronexcitedxraymicroanalysis pages 13-15): Dale E. Newbury and Nicholas W.M. Ritchie. Electron-excited x-ray microanalysis by energy dispersive spectrometry at 50: analytical accuracy, precision, trace sensitivity, and quantitative compositional mapping. Microscopy and Microanalysis, 25:1075-1105, Oct 2019. URL: https://doi.org/10.1017/s143192761901482x, doi:10.1017/s143192761901482x. This article has 53 citations and is from a peer-reviewed journal.

13. (teng2020highresolutionxray pages 27-31): C Teng. High resolution x-ray imaging and quantitative microanalysis in electron microscopy. Unknown journal, 2020.

14. (newbury2014rigorousquantitativeelemental pages 5-6): Dale E. Newbury and Nicholas W. M. Ritchie. Rigorous quantitative elemental microanalysis by scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds) with spectrum processing by nist dtsa-ii. SPIE Proceedings, 9236:92360H, Sep 2014. URL: https://doi.org/10.1117/12.2065842, doi:10.1117/12.2065842. This article has 24 citations.

15. (teng2020highresolutionxray pages 71-77): C Teng. High resolution x-ray imaging and quantitative microanalysis in electron microscopy. Unknown journal, 2020.

16. (newbury*2013isscanningelectron pages 5-7): Dale E. Newbury* and Nicholas W. M. Ritchie. Is scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds) quantitative? Scanning, 35 3:141-68, May 2013. URL: https://doi.org/10.1002/sca.21041, doi:10.1002/sca.21041. This article has 729 citations.

17. (goldstein2018quantitativeanalysisthe pages 1-4): Joseph I. Goldstein, Dale E. Newbury, Joseph R. Michael, Nicholas W. M. Ritchie, John Henry J. Scott, and David C. Joy. Quantitative analysis: the sem/eds elemental microanalysis k-ratio procedure for bulk specimens, step-by-step. ArXiv, pages 309-339, Nov 2018. URL: https://doi.org/10.1007/978-1-4939-6676-9\_20, doi:10.1007/978-1-4939-6676-9\_20. This article has 9 citations.

18. (xing2016informationorresolution pages 10-11): Q. Xing. Information or resolution: which is required from an sem to study bulk inorganic materials? Scanning, 38 6:864-879, Nov 2016. URL: https://doi.org/10.1002/sca.21336, doi:10.1002/sca.21336. This article has 18 citations.

19. (newbury*2013isscanningelectron pages 18-19): Dale E. Newbury* and Nicholas W. M. Ritchie. Is scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds) quantitative? Scanning, 35 3:141-68, May 2013. URL: https://doi.org/10.1002/sca.21041, doi:10.1002/sca.21041. This article has 729 citations.

20. (newbury2012faultsandfoibles pages 5-7): Dale E. Newbury and Nicholas W. M. Ritchie. Faults and foibles of quantitative scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds). SPIE Proceedings, 8378:837803, May 2012. URL: https://doi.org/10.1117/12.912770, doi:10.1117/12.912770. This article has 15 citations.

21. (newbury2012faultsandfoibles pages 7-9): Dale E. Newbury and Nicholas W. M. Ritchie. Faults and foibles of quantitative scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds). SPIE Proceedings, 8378:837803, May 2012. URL: https://doi.org/10.1117/12.912770, doi:10.1117/12.912770. This article has 15 citations.

22. (heinrich2013electronprobequantitation pages 257-258): KFJ Heinrich and D Newbury. Electron probe quantitation. ArXiv, Jan 2013. URL: https://doi.org/10.1007/978-1-4899-2617-3, doi:10.1007/978-1-4899-2617-3. This article has 170 citations.

23. (newbury2014rigorousquantitativeelemental pages 2-5): Dale E. Newbury and Nicholas W. M. Ritchie. Rigorous quantitative elemental microanalysis by scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds) with spectrum processing by nist dtsa-ii. SPIE Proceedings, 9236:92360H, Sep 2014. URL: https://doi.org/10.1117/12.2065842, doi:10.1117/12.2065842. This article has 24 citations.

24. (heinrich2013electronprobequantitation pages 249-252): KFJ Heinrich and D Newbury. Electron probe quantitation. ArXiv, Jan 2013. URL: https://doi.org/10.1007/978-1-4899-2617-3, doi:10.1007/978-1-4899-2617-3. This article has 170 citations.

25. (voort2006metallographicpreparationfor pages 2-3): G Vander Voort, W Van Geertruyden, S Dillon, and E Manilova. Metallographic preparation for electron backscattered diffraction. Microscopy and Microanalysis, 12:1610-1611, Jul 2006. URL: https://doi.org/10.1017/s1431927606069327, doi:10.1017/s1431927606069327. This article has 39 citations and is from a peer-reviewed journal.

26. (voort2006metallographicpreparationfor pages 1-2): G Vander Voort, W Van Geertruyden, S Dillon, and E Manilova. Metallographic preparation for electron backscattered diffraction. Microscopy and Microanalysis, 12:1610-1611, Jul 2006. URL: https://doi.org/10.1017/s1431927606069327, doi:10.1017/s1431927606069327. This article has 39 citations and is from a peer-reviewed journal.

27. (jiao2019microstructurecharacterizationof pages 1-2): Zhenhua Jiao, Renke Kang, Zhigang Dong, and Jiang Guo. Microstructure characterization of w-ni-fe heavy alloys with optimized metallographic preparation method. International Journal of Refractory Metals and Hard Materials, 80:114-122, Apr 2019. URL: https://doi.org/10.1016/j.ijrmhm.2019.01.011, doi:10.1016/j.ijrmhm.2019.01.011. This article has 53 citations and is from a peer-reviewed journal.

28. (jiao2019microstructurecharacterizationof pages 2-3): Zhenhua Jiao, Renke Kang, Zhigang Dong, and Jiang Guo. Microstructure characterization of w-ni-fe heavy alloys with optimized metallographic preparation method. International Journal of Refractory Metals and Hard Materials, 80:114-122, Apr 2019. URL: https://doi.org/10.1016/j.ijrmhm.2019.01.011, doi:10.1016/j.ijrmhm.2019.01.011. This article has 53 citations and is from a peer-reviewed journal.

29. (voort2006metallographicpreparationfor pages 3-5): G Vander Voort, W Van Geertruyden, S Dillon, and E Manilova. Metallographic preparation for electron backscattered diffraction. Microscopy and Microanalysis, 12:1610-1611, Jul 2006. URL: https://doi.org/10.1017/s1431927606069327, doi:10.1017/s1431927606069327. This article has 39 citations and is from a peer-reviewed journal.

30. (brumbach2016compositionalanalysisfor pages 10-15): MT Brumbach, BL Boyce, DF Susan, and J Rodelas. Compositional analysis for additive manufacturing. Unknown journal, 2016.

31. (kallio2025accuracyandprecision pages 51-55): M Kallio. Accuracy and precision comparison with elemental analysis parameter optimization for xrf. Unknown journal, 2025.

32. (luttergunther2018spatterformationduring pages 3-4): Max Lutter-Günther, M. Bröker, T. Mayer, S. Lizak, C. Seidel, and G. Reinhart. Spatter formation during laser beam melting of alsi10mg and effects on powder quality. Procedia CIRP, 74:33-38, Jan 2018. URL: https://doi.org/10.1016/j.procir.2018.08.008, doi:10.1016/j.procir.2018.08.008. This article has 79 citations and is from a peer-reviewed journal.

33. (kallio2025accuracyandprecision pages 15-20): M Kallio. Accuracy and precision comparison with elemental analysis parameter optimization for xrf. Unknown journal, 2025.

34. (teng2019thefratioquantificationa pages 5-6): Chaoyi Teng, Hendrix Demers, Xin Chu, and Raynald Gauvin. The f-ratio quantification method for x-ray microanalysis applied to mg–al–zn alloys. Microscopy and Microanalysis, 25:58-69, Feb 2019. URL: https://doi.org/10.1017/s1431927618015684, doi:10.1017/s1431927618015684. This article has 5 citations and is from a peer-reviewed journal.

35. (struder1998highresolutionxrayspectroscopy pages 3-6): L. Strüder, N. Meidinger, D. Stötter, J. Kemmer, Peter Lechner, P. Leutenegger, H. Soltau, F. Eggert, M. Rohde, and T. Schülein. High-resolution x-ray spectroscopy close to room temperature. Microscopy and Microanalysis, 4:622-631, Dec 1998. URL: https://doi.org/10.1017/s1431927698980606, doi:10.1017/s1431927698980606. This article has 94 citations and is from a peer-reviewed journal.

36. (farinas2016determinationofrare pages 8-12): Juan C. Fariñas, Isabel Rucandio, Mario S. Pomares-Alfonso, Margarita E. Villanueva-Tagle, and María T. Larrea. Determination of rare earth and concomitant elements in magnesium alloys by inductively coupled plasma optical emission spectrometry. Talanta, 154:53-62, Jul 2016. URL: https://doi.org/10.1016/j.talanta.2016.03.047, doi:10.1016/j.talanta.2016.03.047. This article has 48 citations and is from a peer-reviewed journal.