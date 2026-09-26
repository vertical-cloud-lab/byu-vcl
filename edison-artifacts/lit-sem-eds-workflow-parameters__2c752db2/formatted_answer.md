Question: We are establishing a standard SEM/EDS workflow for routine quantitative characterization of (a) gas-atomized metal AM powder feedstock and (b) polished cross-sections of LPBF-printed parts in a small academic AM lab (BYU Vertical Cloud Lab). Equipment: FEI Apreo FEG-SEM + EDAX Octane Plus 30 mm² SDD running TEAM software with eZAF Smart Quant standardless. Primary alloy of interest is AlSi10Mg (nominal Si 9-11 wt%, Mg 0.20-0.45 wt%, Fe <0.55 wt%, Al bal), but the SOP will be applied broadly to Al, Ti, Ni, and steel AM powders and parts.

Please provide a literature-backed, parameter-by-parameter recommendation for STANDARD SEM/EDS workflow settings, distinguishing what should be FIXED across all samples vs. what should be TUNED per sample. Specifically cover:

1. Magnification levels — what is the recommended set of magnification levels to capture for each sample type, and why?
   a. For powder feedstock characterization (gas-atomized particles 10-100 µm): what magnifications best capture (i) overall particle size distribution and morphology, (ii) surface texture and satellite/spatter content, (iii) cross-section microstructure of mounted/polished powder? Cite ASTM B214/B243/F3049 and ISO 13322 if applicable.
   b. For printed-part polished cross-sections: what magnifications best capture (i) melt-pool/fishscale morphology, (ii) cellular/dendritic substructure, (iii) defect populations (lack-of-fusion, gas porosity, keyhole), (iv) intermetallic precipitate populations? Cite ASTM E1245, E2109, F3122, F2792 if applicable.
   c. For EDS quantitative point/area analysis vs. EDS mapping: what magnification ranges are appropriate, and what is the relationship between magnification, beam dwell time, pixel resolution, and quantification reliability?
   d. Recommended scout-to-detail magnification ladder (e.g., 100x → 500x → 2,500x → 10,000x → 50,000x) and what data product should come from each level.

2. Imaging parameters — recommended fixed defaults and acceptable ranges for:
   a. Accelerating voltage (kV) for SE vs. BSE vs. EDS, and per material class (Al alloys vs. Ti vs. Ni vs. steel).
   b. Beam current / spot size / probe current (nA) and how to tune by target detector dead time (10-30%) on the EDS side.
   c. Working distance (analytical WD vs. imaging WD).
   d. Aperture / objective lens current settings (high-current vs. high-resolution modes).
   e. Dwell time, line average, frame integration for SE/BSE imaging at each magnification level.
   f. Tilt / take-off angle considerations.

3. EDS-specific parameters that should be standardized across all sessions:
   a. Live time and target net counts per spectrum (per ASTM E1508).
   b. Amp time / shaping time (1-8 µs range and tradeoffs).
   c. Detector energy resolution target (FWHM at Mn Kα).
   d. Background fit windows.
   e. Element list construction (kα/kβ/L-lines) and standard reference materials.
   f. Number of spot analyses per sample, number of map fields per sample, area-coverage targets.

4. Sample type-specific deviations — when to depart from the standard SOP, e.g.:
   a. Trace-element work (Mg in Al at 0.3 wt%; Y in Ni-base; trace impurities at <0.1 wt%): longer live times, longer amp times, standards required.
   b. Light-element work (O, N, C contamination assessment, oxide-layer characterization): lower kV (5-10 kV), windowless detector mode, specific background windows.
   c. Phase-specific quantification (intermetallics, eutectic constituents): high-mag spot analysis with awareness of interaction volume (~1-3 µm at 15 kV).
   d. Powder vs. polished cross-section vs. as-printed rough surface tradeoffs.

5. QA/QC and SOP structure — what should appear in a written SOP document?
   a. Pre-session checks (vacuum, beam alignment, gun saturation, detector cooling, dead-time on a Cu/Al/Si standard).
   b. Within-session checks (mid-session standard re-measurement; sample-to-sample reproducibility).
   c. Calibration cadence (energy calibration, beam-current measurement with Faraday cup, detector resolution check on Mn Kα or Cu Kα).
   d. Data logging — what metadata MUST be saved for each spectrum/image so it is reproducible 6 months later (kV, current, WD, mag, dwell, amp time, live time, dead time, TOA, detector serial, software version, MSA + raw spectrum + PDF report)?
   e. ICP-OES / WDS cross-validation cadence and acceptance criteria.

6. Existing standards and guidance documents to cite — please collect and cite the relevant ASTM, ISO, and instrument-vendor SOPs (ASTM E1508 quant EDS, E1078 specimen prep, E1245 inclusion measurement, E2109 phase analysis, B214/B243 powder PSD, F3049/F3122/F2792 AM terminology and powder characterization, ISO 13322 particle size by image analysis, Goldstein/Newbury/Joy SEM textbook chapters on SOP construction).

Please return a synthesized lab SOP draft structure with explicit recommended values + acceptable ranges + citations, plus a one-page quick-reference table that a student could pin next to the microscope.

# Literature-Backed SEM/EDS Standard Operating Procedure for AM Powder and LPBF Part Characterization

## BYU Vertical Cloud Lab — FEI Apreo FEG-SEM + EDAX Octane Plus 30 mm² SDD

---

## 1. Magnification Levels

### 1a. Powder Feedstock Characterization (Gas-Atomized, 10–100 µm)

A structured magnification ladder is essential for capturing the multi-scale features of AM powder. Reference photomicrographs should be collected at a minimum of 100×, 250×, 500×, and 1000× as a standard set for batch-to-batch comparisons (carlton2011scanningelectronmicroscopy pages 19-21). For gas-atomized powder:

- **50–100× (HFW ~3–6 mm):** Overview images capturing hundreds of particles for apparent particle size distribution (PSD) panoramas. This magnification enables image-analysis-based PSD per ISO 13322-1 requirements, though SEM-based image analysis typically resolves only a few hundred particles per field and is considered lower throughput than automated optical instruments (groarke2021powdercharacterization—methodsstandards pages 12-14). ASTM F3049-14 designates SEM morphology as a recommended characterization method for AM metal powders (groarke2021powdercharacterization—methodsstandards pages 12-14).
- **250–500× (HFW ~0.6–1.2 mm):** Satellite/spatter content assessment, agglomeration, and broad particle shape classification. This magnification range is commonly used in AM powder studies for overall morphology assessment per ASTM F3049 and ISO 13322-2 workflows (groarke2021powdercharacterization—methodsstandards pages 12-14).
- **1,000–2,500× (HFW ~120–300 µm):** Individual particle surface texture, fine satellite distribution, and surface oxide features. Materials with primary particle sizes below ~20 µm may require different preparation and imaging strategies to obtain representative morphology (carlton2011scanningelectronmicroscopy pages 19-21).
- **5,000–10,000× (for mounted/polished cross-sections):** Internal microstructure of individual particles, dendritic or cellular solidification structure within gas-atomized powder, and internal porosity.

### 1b. Printed-Part Polished Cross-Sections

LPBF AlSi10Mg cross-sections exhibit features spanning from macro-scale melt pool patterns (~100 µm) down to nanoscale precipitates. Multiple AlSi10Mg studies employ FE-SEM at 20 kV in SE and BSE modes with standard metallographic preparation (grinding to 4000 grit, diamond polish to 1 µm, optional brief 0.5% HF etch or colloidal silica final polish) (qin2020rapidsolidificationand pages 2-3, cauwenbergh2021unravellingthemultiscale pages 2-3, hyer2020understandingthelaser pages 1-2):

- **50–100× (HFW ~3–6 mm):** Whole cross-section overview revealing scan strategy, layer structure, and macro-defect distribution. Applicable to ASTM E1245 field-of-view requirements for inclusion/porosity measurement.
- **250–500× (HFW ~0.6–1.2 mm):** Melt-pool fishscale morphology, defect field survey (lack-of-fusion voids, gas porosity >50 µm, keyhole pores). ASTM E1245 (automated inclusion analysis) and ASTM E2109 (phase fraction by image analysis) both specify representative field selection at this scale.
- **1,000–2,500× (HFW ~120–300 µm):** Individual melt-pool boundaries, inter-track bonding quality, coarse porosity (>10 µm).
- **5,000–10,000× (HFW ~30–60 µm):** Cellular/dendritic substructure within melt pools, eutectic Si network morphology. LPBF AlSi10Mg exhibits a characteristic fine α-Al cellular structure with Si-rich intercellular networks visible at this scale (qin2020rapidsolidificationand pages 2-3, hyer2020understandingthelaser pages 1-2).
- **20,000–50,000× (HFW ~6–15 µm):** Fine intermetallic precipitates (Fe-bearing phases, Mg₂Si), melt-pool boundary coarsened zones.

### 1c. EDS Quantitative Analysis vs. Mapping Magnification

For EDS quantitative point analysis, magnification should be chosen so that the rastered area or stationary beam spot is placed entirely within the phase of interest, with awareness that the X-ray interaction volume at 15 kV in aluminum is approximately 1–3 µm in diameter (small2002theanalysisof pages 1-2). Reducing pixel size below the interaction volume provides no additional spatial resolution for EDS (carlton2011scanningelectronmicroscopy pages 4-7). For area analysis mode, a scanning field of view (FoV) of ~50 µm–1 mm is typical (magnification 500×–5,000×), with pixel resolution of at least 512×384 to avoid aliasing while maintaining meaningful dwell times per pixel of 50–200 µs for SDD-EDS mapping (carlton2011scanningelectronmicroscopy pages 37-40, guyett2024optimizingsemedxfor pages 4-6). Higher pixel counts (2048×1557) with 200 µs dwell per pixel have been demonstrated for high-quality compositional maps (guyett2024optimizingsemedxfor pages 4-6).

### 1d. Recommended Magnification Ladder

The following magnification ladder provides a systematic scout-to-detail workflow. Each level should produce a defined data product:

| Magnification Level | Horizontal Field Width (HFW) | Sample Type(s) | Data Product / Feature Captured | Detector Mode | Recommended kV |
|---|---|---|---|---|---|
| 50-100× | ~3-6 mm | Powder + Part | Overview/scout images: powder panorama for apparent particle size distribution and morphology; whole polished cross-section overview for scan strategy and large-scale melt-pool pattern/fishscale context. Use as the session starting image set and archive overview. (carlton2011scanningelectronmicroscopy pages 19-21, groarke2021powdercharacterization—methodsstandards pages 12-14) | SE or BSE | 15 kV |
| 250-500× | ~0.6-1.2 mm | Powder + Part | Powder: satellite/spatter content, agglomeration, irregular particles, broad shape-class assessment for image-based morphology workflows. Part: melt-pool fishscale morphology and defect field survey for lack-of-fusion and gas porosity populations before higher-mag targeting. (carlton2011scanningelectronmicroscopy pages 19-21, groarke2021powdercharacterization—methodsstandards pages 12-14) | BSE preferred | 15 kV |
| 1,000-2,500× | ~120-300 µm | Powder + Part | Powder: individual particle surface texture, local surface defects, fine satellites. Part: individual melt-pool boundaries, coarse porosity (>10 µm), inter-track/inter-layer bonding, localized defect morphology. Good bridge from morphology imaging to analytical targeting. (carlton2011scanningelectronmicroscopy pages 4-7, qin2020rapidsolidificationand pages 2-3, hyer2020understandingthelaser pages 1-2) | SE + BSE | 15-20 kV |
| 5,000-10,000× | ~30-60 µm | Part (polished XS) | Cellular/dendritic substructure within melt pools, eutectic Si network morphology in AlSi10Mg, microsegregation context, and practical EDS point-analysis targeting on polished flat areas. Use BSE for phase contrast and EDS spots for local quant. (qin2020rapidsolidificationand pages 2-3, hyer2020understandingthelaser pages 1-2, newbury2015performingelementalmicroanalysis pages 2-4) | BSE + EDS spots | 15-20 kV |
| 20,000-50,000× | ~6-15 µm | Part (polished XS) | Fine intermetallic precipitates (e.g., Fe-rich phases, Mg2Si), nanoscale cellular boundaries, and phase-specific EDS spot analysis where feature size still exceeds the effective interaction volume. If the feature approaches the ~1-3 µm interaction volume typical of conventional SEM-EDS at ~15 kV, reduce kV or do not report phase-pure composition from that spot. (small2002theanalysisof pages 1-2, burgess2017ultralowkveds pages 5-6, newbury2011isscanningelectron pages 2-3) | BSE + EDS spot | 15-20 kV (or 10 kV for smaller features) |
| EDS Area/Map Mode | 500-5,000× typical | Both | Quantitative area analysis and compositional mapping over representative fields; suitable for Si, Mg, Fe segregation, contamination screening, and phase distribution maps. Match pixel size to interaction volume; use at least 512×384 pixels and record dwell/integration settings. (carlton2011scanningelectronmicroscopy pages 4-7, carlton2011scanningelectronmicroscopy pages 37-40, guyett2024optimizingsemedxfor pages 4-6) | EDS map mode | 15-20 kV |
| EDS Point/Spot Quant | 2,500-10,000× | Both | Routine quantitative point analysis on flat, representative regions. Recommended for standards-based or standardless routine lab screening only when spot placement avoids edges/topography; use ≥60 s live time, target ≥1M total counts, and acquire ≥10 spots/sample (≥20 preferred for powder). (newbury2015performingelementalmicroanalysis pages 11-13, newbury*2013isscanningelectron pages 7-9, giunto2026accuratesem‑edsquantification pages 1-3, guyett2024optimizingsemedxfor pages 4-6) | EDS spot mode | 15-20 kV |


*Table: This table gives a practical scout-to-detail magnification ladder for routine SEM/EDS of AM powders and LPBF cross-sections. It links each magnification band to the expected data product, detector choice, and typical accelerating voltage for a reproducible SOP.*

---

## 2. Imaging Parameters

### 2a. Accelerating Voltage

The recommended default for routine SE and BSE imaging of metal AM samples is **15 kV**, which provides a strong balance of signal strength, surface detail, and interaction volume control (carlton2011scanningelectronmicroscopy pages 29-31, carlton2011scanningelectronmicroscopy pages 31-34). For quantitative EDS of metallic alloys, the overvoltage rule specifies that the accelerating voltage should be 1.5–2× the energy of the highest characteristic X-ray line of interest (carlton2011scanningelectronmicroscopy pages 29-31, carlton2011scanningelectronmicroscopy pages 31-34). Practical recommendations by material class:

- **Al alloys (AlSi10Mg):** 15 kV is adequate (Si Kα = 1.74 keV; Al Kα = 1.49 keV; overvoltage >8×). Multiple AlSi10Mg LPBF studies use 20 kV for combined imaging and EDS (qin2020rapidsolidificationand pages 2-3, hyer2020understandingthelaser pages 1-2).
- **Ti alloys (Ti-6Al-4V):** 15–20 kV (Ti Kα = 4.51 keV; overvoltage ~3.3–4.4×).
- **Ni-base alloys (IN718):** 20 kV (Ni Kα = 7.47 keV; overvoltage ~2.7×).
- **Steel (316L):** 20–25 kV for rigorous quantification of Cr, Ni, Mo, Mn (Mo Lα = 2.29 keV at 20 kV gives ample overvoltage; Fe Kα = 6.40 keV) (garzon2023effectsofvariations pages 3-6, garzon2023effectsofvariations pages 2-3).

### 2b. Beam Current / Spot Size / Probe Current

Beam current should not be set to an arbitrary value but rather **tuned to achieve a target dead time of approximately 10% on the SDD-EDS detector** when the beam is placed on a high-flux standard (pure Al, Si, or Cu) at the analytical working distance (newbury2015performingelementalmicroanalysis pages 11-13, newbury*2013isscanningelectron pages 7-9). For the EDAX Octane Plus 30 mm² on the Apreo, this typically corresponds to 0.5–1.5 nA for routine quantitative work. The same beam current must be used for both standards and unknowns to maintain consistent dose and minimize sum-peak artifacts (newbury2015performingelementalmicroanalysis pages 11-13). Coincidence events (sum peaks such as 2AlK, 2SiK) become significant above approximately 15% dead time on modern SDDs (newbury2015performingelementalmicroanalysis pages 11-13, newbury*2013isscanningelectron pages 7-9).

### 2c. Working Distance

The analytical working distance must be fixed and recorded for all quantitative sessions because the EDS detector solid angle varies as A/r², making measured intensities sensitive to even small changes in specimen-to-detector distance (newbury*2013isscanningelectron pages 7-9). For the FEI Apreo with EDAX Octane, the recommended analytical WD is **10 mm** (verify against the vendor-specified optimal EDS position). This WD should be maintained constant between standards and unknowns and between sessions if archived standard spectra are used (newbury*2013isscanningelectron pages 7-9, newbury2015performingelementalmicroanalysis pages 11-13). For pure imaging (no EDS), WD may be varied to optimize resolution or depth of field.

### 2d. Aperture / Lens Modes

For quantitative EDS, use the high-current or analytical mode of the Apreo objective lens to maximize probe current delivered to the specimen at the required spot size. High-resolution/immersion-lens modes trade current for resolution and are reserved for pure imaging at high magnification. Switch to high-current mode when EDS acquisition is the primary objective.

### 2e. Dwell Time, Line Average, Frame Integration

Image quality should be built up through frame integration rather than excessively long pixel dwell times to minimize drift and charging artifacts (carlton2011scanningelectronmicroscopy pages 4-7, carlton2011scanningelectronmicroscopy pages 19-21):

- **100–500× SE/BSE:** 1024×884 pixels, 8–16 frame average, 1–3 µs dwell.
- **1,000–5,000× BSE:** 1024×884 or 2048×1768 pixels, 16–32 frame average.
- **10,000–50,000× BSE:** 2048×1768 pixels, 32–64 frame average, with drift correction if available.

### 2f. Tilt / Take-off Angle

Specimen tilt should be **0°** (beam perpendicular to polished surface) for all routine quantitative work. Even modest tilt introduces differential absorption path lengths that create large errors, especially for low-energy X-ray lines below ~4 keV (newbury2015performingelementalmicroanalysis pages 11-13, newbury2011isscanningelectrona pages 2-4). The EDS take-off angle is instrument-fixed (typically ~35° on the Apreo/Octane geometry) and should be recorded in metadata (carlton2011scanningelectronmicroscopy pages 29-31, newbury2015performingelementalmicroanalysis pages 2-4).

---

## 3. EDS-Specific Parameters

### 3a. Live Time and Target Net Counts

Per ASTM E1508 principles and Newbury & Ritchie's recommendations, spectra should contain sufficient counts for the desired statistical precision. A relative counting precision of ~1% on a given peak requires approximately **10,000 net counts above background** for that peak (newbury*2013isscanningelectron pages 7-9). For routine quantitative point analysis, a minimum of **≥1 million integrated counts** (across the full spectrum, 0.1–20 keV) should be collected, achievable in ~60–100 s live time with modern SDD throughput (newbury2011isscanningelectrona pages 2-4, guyett2024optimizingsemedxfor pages 4-6). For trace constituent work (e.g., Mg at 0.3 wt% in Al), extend live time to 200–500 s to push detection limits below ~0.1 wt% (newbury*2013isscanningelectron pages 14-16, newbury2019electronexcitedxraymicroanalysis pages 2-3). The recommended minimum live time for fully quantitative analysis of glass reference materials has been benchmarked at conditions yielding ≥1M counts, with ~15 s acquisition at ~100 kcps output count rate sufficient for major elements (guyett2024optimizingsemedxfor pages 4-6).

### 3b. Amp Time / Shaping Time

The EDAX TEAM software offers selectable amp times that trade energy resolution against throughput (camus2007reevaluatingacquisitionparameters pages 1-2, newbury*2013isscanningelectron pages 7-9):

- **0.96–1.92 µs:** Fast throughput mode for EDS mapping; higher dead time tolerance (15–25%) acceptable.
- **3.84 µs:** Default routine quantitative analysis; good compromise between resolution and throughput.
- **7.68 µs:** Maximum resolution mode; use for trace-element work, severe peak overlaps (e.g., Mn Kα / Cr Kβ in steel), or when best possible spectral resolution is required.

Traditional guidance recommended the slowest shaping time with 20–30% dead time, but modern SDD detectors and quantification algorithms perform well across a wider range of settings (camus2007reevaluatingacquisitionparameters pages 1-2).

### 3c. Detector Energy Resolution

The target FWHM at Mn Kα (5.895 keV) should be **≤130 eV**, with best-performing modern SDDs achieving ~127.5–128 eV (newbury2011isscanningelectrona pages 2-4, newbury2014rigorousquantitativeelemental pages 5-6). This should be verified at the start of each session. Resolution degradation beyond 135 eV should trigger recalibration or service review (garzon2023effectsofvariations pages 2-3).

### 3d. Background Fit Windows

For standardless eZAF Smart Quant in TEAM, the software performs automatic background modeling and subtraction. For critical quantitative work, the operator should inspect the background fit in the 0.5–2 keV region, where absorption edges and detector artifacts (especially for light elements O, N, C) can distort the continuum shape (giunto2026accuratesem‑edsquantification pages 1-3, giunto2026accuratesem‑edsquantification pages 3-5). Users of standards-based protocols (e.g., NIST DTSA-II) should define background windows on either side of each peak, avoiding interfering peaks.

### 3e. Element List Construction

For AlSi10Mg, the element list should include: Al Kα, Si Kα, Mg Kα, Fe Kα, Cu Kα (if applicable), Mn Kα, Zn Kα, Ti Kα, and O Kα (if low-kV work). A predefined element list covering all expected species facilitates batch processing of many points from the same sample (rossen2017optimizationofsemeds pages 6-9). The analyst should manually verify automatic peak identifications, especially for minor/trace constituents, because commercial standardless software produces systematic misidentifications at a high rate for low-intensity peaks (newbury2014rigorousquantitativeelemental pages 1-2, newbury*2013isscanningelectron pages 14-16). For steel, note the severe Mn Kα / Cr Kβ overlap requiring careful deconvolution (garzon2023effectsofvariations pages 2-3). For Ni-base alloys, select appropriate L-lines for heavier elements (Nb, Mo, W) at lower kV.

### 3f. Number of Analyses

- **Polished cross-sections:** ≥10 EDS spot analyses per sample, distributed across representative microstructural regions (melt pool interior, boundary, HAZ).
- **Powder feedstock:** ≥20 spot analyses per batch, sampling particles across the size distribution. Automated particle-based workflows commonly collect ~100 spectra of 50,000 counts each per sample for statistical robustness (giunto2026accuratesem‑edsquantification pages 1-3, giunto2026accuratesem‑edsquantification pages 3-5).
- **EDS maps:** At least 3 representative fields per sample at 500–2,500× magnification, covering ≥0.5 mm² cumulative area for defect/phase distribution statistics.

---

## 4. Sample Type-Specific Deviations

### 4a. Trace-Element Work

For Mg at 0.3 wt% in Al (approaching the LPBF AlSi10Mg specification lower bound), or Y/Hf in Ni-base superalloys, or impurities below 0.1 wt%: extend live time to 200–500 s, use the longest available amp time (7.68 µs) for best resolution, target ≥5M integrated counts, and strongly consider standards-based k-ratio analysis rather than standardless to achieve relative errors within ±5% (newbury2014rigorousquantitativeelemental pages 2-5, newbury*2013isscanningelectron pages 14-16, newbury2015performingelementalmicroanalysis pages 11-13). Standardless analysis has demonstrated systematic errors of ±25% at the 95% confidence level, whereas standards-based analysis achieves ±5% (newbury2014rigorousquantitativeelemental pages 2-5). The analytical total (un-normalized sum of all element concentrations) should be checked as a quality indicator; totals far from 100% indicate geometric or calibration problems masked by standardless normalization (newbury*2013isscanningelectron pages 23-26, newbury2012howtodo pages 1-2).

### 4b. Light-Element Work (O, N, C)

For oxide layer characterization or contamination assessment, reduce the accelerating voltage to **5–10 kV** to decrease the interaction volume and increase surface sensitivity (small2002theanalysisof pages 1-2, burgess2017ultralowkveds pages 5-6). Ultra-low kV EDS (1–3 kV) provides extreme surface sensitivity but requires windowless detectors or very thin-window detectors and introduces additional challenges in background modeling below 2 keV (burgess2017ultralowkveds pages 5-6). At 5 kV, useful characteristic peaks can be excited for all elements except H and He, and standards-based analysis at 5 kV has been demonstrated with >98% of results within ±5% relative deviation (newbury2019electronexcitedxraymicroanalysis pages 2-3). However, quantification of O by EDS is often unreliable due to its low-energy peak sensitivity to detector window absorption; oxygen is commonly calculated by stoichiometry instead (rossen2017optimizationofsemeds pages 6-9). Relative uncertainties for particle-based EDS at low kV are higher (0.10–0.20) compared to bulk flat specimens (0.02–0.05) (small2002theanalysisof pages 1-2).

### 4c. Phase-Specific Quantification

For quantifying intermetallic precipitates (e.g., Fe-bearing phases in AlSi10Mg, β-Al₅FeSi, π-Al₈FeMg₃Si₆), the beam interaction volume at 15 kV in Al is approximately 1–3 µm diameter (small2002theanalysisof pages 1-2). If the phase of interest is smaller than this, the measured composition will include signal from the surrounding matrix. Reducing kV to 10 kV significantly shrinks the interaction volume. Alternatively, WDS on an EPMA or TEM-EDS provides the spatial resolution needed for sub-micrometer phases. The analyst must document whether the analyzed volume is fully contained within the phase and flag results from volumes that may include matrix contributions.

### 4d. Powder vs. Polished Cross-Section vs. As-Printed Surface

Irregular particle geometry fundamentally compromises quantitative EDS accuracy through mass effects (electron escape from small particles) and absorption effects (path-length variations through non-flat surfaces) (small2002theanalysisof pages 1-2, newbury2011isscanningelectrona pages 2-4, giunto2026accuratesem‑edsquantification pages 1-3). For loose powder on carbon tape, standardless quantitative results should be treated as semi-quantitative (relative uncertainties 10–20% for micron-scale particles) (giunto2026accuratesem‑edsquantification pages 1-3). The peak-to-background (P/B) method with experimental standards per element can reduce relative errors to 5–10% even on irregular powder surfaces (giunto2026accuratesem‑edsquantification pages 1-3, giunto2026accuratesem‑edsquantification pages 3-5). For as-printed rough surfaces, quantitative EDS is unreliable without metallographic preparation; topographic variations can cause errors exceeding a factor of ten for some elements (newbury2012howtodo pages 1-2, newbury2011isscanningelectrona pages 2-4). Polished, flat specimens (surface roughness <50 nm rms) are required for reliable quantitative analysis (newbury2015performingelementalmicroanalysis pages 11-13, newbury*2013isscanningelectron pages 23-26).

---

## 5. QA/QC and SOP Structure

### 5a. Pre-Session Checks

Before any quantitative session:
1. Verify vacuum is at operating level (<5×10⁻⁴ Pa).
2. Confirm Schottky field-emission gun is saturated and stable; record tip hours.
3. Verify EDAX Octane thermoelectric cooling is at operating temperature.
4. Perform energy calibration on a Cu standard (30 s acquisition): confirm Cu Lα at 0.930 keV and Cu Kα at 8.04 keV (carlton2011scanningelectronmicroscopy pages 29-31).
5. Verify detector resolution: Mn Kα FWHM ≤130 eV (newbury2011isscanningelectrona pages 2-4, newbury2014rigorousquantitativeelemental pages 5-6).
6. Measure beam current with Faraday cup and record value in nA (newbury2015performingelementalmicroanalysis pages 11-13).
7. On pure Al or Si at analytical WD, adjust beam current to achieve 10% dead time (newbury2015performingelementalmicroanalysis pages 11-13, newbury*2013isscanningelectron pages 7-9).

### 5b. Within-Session Checks

Calibration stability should be verified periodically during sessions. In long sessions, re-measure the energy calibration standard every **2 hours** to limit the effect of beam current drift (rossen2017optimizationofsemeds pages 6-9). Beam current drift on modern FE-SEMs is typically small (~0.5%/hour) but should be monitored (rossen2017optimizationofsemeds pages 6-9, guyett2024optimizingsemedxfor pages 3-4). For sample-to-sample reproducibility, acquire at least one re-measurement of a known standard or reference material between sample changes.

### 5c. Calibration Cadence

- **Energy calibration:** Every session start and every 2 hours during extended sessions (rossen2017optimizationofsemeds pages 6-9).
- **Beam current measurement:** Every session start; before and after long acquisitions.
- **Detector resolution check:** Every session start; flag if FWHM at Mn Kα exceeds 135 eV.
- **Dead-time verification:** Every session start on high-flux standard.
- **Full instrument service calibration:** Per manufacturer schedule or annually.

### 5d. Data Logging — Required Metadata

Every spectrum and image must be saved with the following minimum metadata for reproducibility (newbury2015performingelementalmicroanalysis pages 11-13, newbury*2013isscanningelectron pages 7-9, newbury2015performingelementalmicroanalysis pages 2-4):

- Accelerating voltage (kV)
- Probe/beam current (nA)
- Working distance (mm)
- Magnification and/or horizontal field width (µm)
- Pixel dwell time and frame integration count
- EDS amp time / process time index
- Live time (s) and real time (s)
- Dead time (%)
- Take-off angle (°)
- Detector model and serial number
- Software name and version (TEAM version)
- Specimen ID, mount ID, and spot location coordinates
- Carbon coat thickness (nm)
- Date, time, and operator name
- Raw spectrum files (.msa and/or .spc format) plus PDF/image reports

### 5e. ICP-OES / WDS Cross-Validation

For each new alloy lot entering the lab, compare SEM/EDS bulk composition (area analysis, ≥5 fields at 500×) against ICP-OES or supplier certificate values. Acceptance criterion: all major elements (>1 wt%) should agree within ±5% relative; minor elements (0.1–1 wt%) within ±15% relative. If standardless eZAF results consistently exceed these thresholds for a given alloy system, transition to standards-based k-ratio analysis using NIST DTSA-II or equivalent (newbury2014rigorousquantitativeelemental pages 2-5, newbury2014rigorousquantitativeelemental pages 1-2). WDS cross-validation on an EPMA should be performed annually or when introducing a new alloy class, particularly for trace elements and severe peak overlaps.

---

## 6. Relevant Standards and Guidance Documents

The following ASTM, ISO, and reference publications should be cited and maintained as part of the SOP:

**EDS/Microanalysis:**
- ASTM E1508 — Standard Guide for Quantitative Analysis by EDS Using SEM
- ASTM E1078 — Standard Guide for Specimen Preparation for SEM/EDS
- Goldstein, Newbury, Michael, Ritchie, Scott, Joy — *Scanning Electron Microscopy and X-Ray Microanalysis* (4th ed., 2018) — comprehensive SEM/EDS textbook
- Newbury & Ritchie (2013) — "Is SEM/EDS Quantitative?" (newbury*2013isscanningelectron pages 23-26, newbury*2013isscanningelectron pages 1-2, newbury*2013isscanningelectron pages 14-16)
- Newbury & Ritchie (2015) — "Performing Elemental Microanalysis with High Accuracy and High Precision by SEM/SDD-EDS" (newbury2015performingelementalmicroanalysis pages 11-13)
- Newbury & Ritchie (2019) — "Electron-Excited X-ray Microanalysis by EDS at 50" (newbury2019electronexcitedxraymicroanalysis pages 2-3)

**Metallography and Phase Analysis:**
- ASTM E1245 — Standard Practice for Determining Inclusion or Second-Phase Constituent Content by Automatic Image Analysis
- ASTM E2109 — Standard Practices for Phase Fraction Determination by Systematic Manual Point Count
- ASTM F3122 — Standard Guide for Evaluating Mechanical Properties of AM Materials

**Powder Characterization:**
- ASTM B214 — Standard Test Method for Sieve Analysis of Metal Powders
- ASTM B243 — Standard Terminology for Powder Metallurgy
- ASTM F3049 — Standard Guide for Characterizing Properties of Metal Powders Used in AM (groarke2021powdercharacterization—methodsstandards pages 12-14)
- ASTM F2792/ISO/ASTM 52900 — Standard Terminology for Additive Manufacturing
- ISO 13322-1/13322-2 — Particle Size Analysis by Image Analysis Methods (groarke2021powdercharacterization—methodsstandards pages 12-14)

---

## Master Parameter Table

The following table provides the complete parameter-by-parameter SOP with fixed defaults, acceptable ranges, and literature citations:

| Parameter | FIXED Default Value | Acceptable Range | Tune Per Sample? | Notes/Citation |
|---|---|---|---|---|
| Accelerating Voltage (SE/BSE imaging) | 15 kV | 5-20 kV | Yes | 15 kV is a strong general starting point for SEM imaging; lower kV improves surface sensitivity and reduces interaction volume, while higher kV helps for coarse microstructures and BSE contrast. Use lower kV for delicate topography/light-element surfaces and higher kV for dense metallic cross-sections. (carlton2011scanningelectronmicroscopy pages 29-31, carlton2011scanningelectronmicroscopy pages 31-34, kallioUnknownyearaccuracyandprecision pages 15-20, garzon2023effectsofvariations pages 3-6) |
| Accelerating Voltage (EDS - standard quantitative) | 15-20 kV | 10-20 kV | Yes | Quantitative alloy EDS is typically strongest at 15-20 kV; 20 kV is common in rigorous standards-based work and AlSi10Mg studies. Follow the overvoltage rule of ~1.5-2× line energy and keep standards/unknowns at identical E0. (newbury2015performingelementalmicroanalysis pages 11-13, newbury2011isscanningelectrona pages 2-4, carlton2011scanningelectronmicroscopy pages 29-31, qin2020rapidsolidificationand pages 2-3, hyer2020understandingthelaser pages 1-2) |
| Accelerating Voltage (EDS - low kV light element) | 5-10 kV | 3-10 kV | Yes | Use lower kV to improve near-surface sensitivity and reduce interaction volume for O, C, N and thin oxide work; ≤10 kV is the established low-kV EDS regime. Expect different lines and more demanding calibration/background behavior than at 15-20 kV. (small2002theanalysisof pages 1-2, burgess2017ultralowkveds pages 5-6, newbury2019electronexcitedxraymicroanalysis pages 2-3) |
| Beam Current (EDS quant) | 0.5-1.0 nA, adjusted to dead time | ~0.1-3 nA practical lab range | Yes | Probe current should be set by count-rate performance, not fixed blindly. For SDD-EDS, adjust current to achieve ~10% dead time on a high-flux material and keep the same current for standards and unknowns; higher beam current may be needed for maps or low-kV work. (newbury2015performingelementalmicroanalysis pages 11-13, newbury*2013isscanningelectron pages 7-9, rossen2017optimizationofsemeds pages 6-9, guyett2024optimizingsemedxfor pages 3-4) |
| Working Distance | 10 mm analytical WD | 10-15 mm | Usually fixed | Hold WD constant for quantitative work because detector solid angle depends strongly on detector distance. 10 mm is appropriate as the analytical WD for the EDAX Octane geometry on the Apreo; 15 mm is also widely used in optimized SEM-EDX studies if that is the vendor-calibrated analytical position, but do not mix WDs within a dataset. (carlton2011scanningelectronmicroscopy pages 29-31, newbury*2013isscanningelectron pages 7-9, carlton2011scanningelectronmicroscopy pages 37-40, guyett2024optimizingsemedxfor pages 3-4, garzon2023effectsofvariations pages 3-6) |
| Dead Time Target | 10% | 5-15% | Yes | Newbury/Ritchie repeatedly recommend ~10% dead time for SDD systems to minimize coincidence artifacts; avoid exceeding ~15% for routine quant and only go higher deliberately for fast screening. Older Si(Li) guidance of 20-30% does not transfer directly to modern SDD quantitative work. (newbury2015performingelementalmicroanalysis pages 11-13, newbury*2013isscanningelectron pages 7-9, camus2007reevaluatingacquisitionparameters pages 1-2) |
| Amp Time / Shaping Time | 3.84 µs | 0.96-7.68 µs | Yes | Use intermediate shaping for routine quant, short shaping for high-throughput mapping, and long shaping for trace/minor elements when maximum resolution is worth the lower throughput. Literature consistently frames this as a resolution-vs-throughput tradeoff. (camus2007reevaluatingacquisitionparameters pages 1-2, newbury*2013isscanningelectron pages 7-9, newbury2014rigorousquantitativeelemental pages 5-6) |
| Live Time (quant point) | 60-100 s | 30-300 s | Yes | 60-100 s is a practical default for routine alloy spots; extend to 300 s for trace/minor constituents or difficult overlaps. Modern SDD systems can reach very high integrated counts quickly, but live time should be increased when detection limit, not throughput, is the priority. (carlton2011scanningelectronmicroscopy pages 31-34, newbury2011isscanningelectrona pages 2-4, guyett2024optimizingsemedxfor pages 3-4, garzon2023effectsofvariations pages 2-3) |
| Target Counts (quant point) | ≥1M integrated counts; ≥10,000 net peak counts/element | 100k-5M integrated counts depending purpose | Yes | ≥10,000 counts above background gives ~1% relative counting precision for a given peak; ≥1M total counts is a strong routine quantitative target, while high-rigor work often uses multi-million-count spectra. 100k counts may suffice for fast screening only. (newbury*2013isscanningelectron pages 7-9, newbury2011isscanningelectrona pages 2-4, guyett2024optimizingsemedxfor pages 4-6, guyett2024optimizingsemedxfor pages 3-4) |
| FWHM at Mn Kα | ≤130 eV | ≤128-130 eV preferred; ≤135 eV acceptable | Usually fixed/QC check | Modern quantitative SDD work commonly reports ~127.5-128 eV at Mn Kα; use this as a detector health criterion before analytical sessions. Resolution drift should trigger recalibration or service review. (newbury2011isscanningelectrona pages 2-4, newbury2014rigorousquantitativeelemental pages 5-6, garzon2023effectsofvariations pages 2-3) |
| Take-off Angle | ~35° | Instrument-fixed | No | EDS geometry must be treated as fixed and reproducible. Carlton notes typical EDS detector geometry around 35°, and Newbury/Ritchie emphasize keeping take-off angle and detector geometry identical between standards and unknowns. (carlton2011scanningelectronmicroscopy pages 29-31, newbury2015performingelementalmicroanalysis pages 11-13, newbury2015performingelementalmicroanalysis pages 2-4) |
| Tilt | 0° | 0° preferred; avoid routine tilt for quant | Yes, but default no | Keep beam perpendicular to the polished surface for quantitative analysis. Even modest topography/tilt can create large composition errors, especially for low-energy lines; tilt should be reserved for special imaging only, not routine quant. (newbury2015performingelementalmicroanalysis pages 11-13, newbury*2013isscanningelectron pages 23-26, newbury*2013isscanningelectron pages 14-16) |
| Carbon Coat | 7-10 nm for polished cross-sections; uncoated for powder on C-tape if charging allows | 5-12 nm on polished mounts | Yes | Thin conductive carbon coating is consistent with quantitative practice on polished bulk samples; several quantitative studies use ~7 nm or ~12 nm carbon. For loose conductive metal powders on carbon tape, uncoated operation is preferable if charging is absent, because particle geometry and extra film thickness can complicate low-energy quant. (newbury2011isscanningelectrona pages 2-4, guyett2024optimizingsemedxfor pages 3-4) |
| EDS Spot Analyses per Sample | ≥10 spots for polished part; ≥20 for powder | 10-30+ | Yes | Routine academic QA should include replication across microstructural fields. Powder studies and automated particle workflows commonly collect many more spectra; for powders, ≥20 spots is a practical manual minimum, with more required for heterogeneous reuse/contamination studies. (giunto2026accuratesem‑edsquantification pages 1-3, giunto2026accuratesem‑edsquantification pages 3-5, newbury*2013isscanningelectron pages 23-26) |
| EDS Map pixel resolution | ≥512×384 pixels | 512×384 to 2048×1557 | Yes | Pixel size must remain meaningful relative to interaction volume; higher pixel counts help registration but do not improve true spatial resolution if oversampling the X-ray generation volume. High-quality practical maps in recent work use resolutions from ~512-class up to 2048×1557, with drift correction as needed. (carlton2011scanningelectronmicroscopy pages 4-7, carlton2011scanningelectronmicroscopy pages 37-40, guyett2024optimizingsemedxfor pages 4-6) |
| EDS Map dwell time | 50-200 µs/pixel | 10 µs-200 ms/pixel depending map purpose | Yes | For routine compositional maps on metallic sections, 50-200 µs/pixel is a reasonable default with SDDs; shorter dwell is faster but noisier, and much longer dwell is reserved for high-quality publication maps or trace-element mapping. Published examples span from rapid scans to 200 ms/pixel high-count maps. (carlton2011scanningelectronmicroscopy pages 37-40, guyett2024optimizingsemedxfor pages 4-6) |
| Frame integration (imaging) | 8-32 frames | 4-64 frames | Yes | Use frame integration/line averaging to improve SNR while limiting drift; higher integration is appropriate at high magnification or low-kV low-current imaging. Keep the number of integrated frames recorded in metadata for reproducibility. (carlton2011scanningelectronmicroscopy pages 4-7, carlton2011scanningelectronmicroscopy pages 19-21, garzon2023effectsofvariations pages 3-6) |


*Table: This table summarizes fixed defaults and tunable ranges for routine SEM/EDS imaging and quantification in the BYU Vertical Cloud Lab SOP. It consolidates literature-backed starting values and QA limits for consistent operation across powders and polished LPBF cross-sections.*

---

## Quick-Reference Card (for posting next to the microscope)

| Section | Item | Standard / Action | Notes / Trigger | Citation |
|---|---|---|---|---|
| Pre-session checklist | Vacuum | Chamber <5×10⁻⁴ Pa | Do not start quantitative work if unstable vacuum | (newbury2015performingelementalmicroanalysis pages 2-4) |
| Pre-session checklist | Gun | Confirm emission; check Schottky tip hours | Record if emission unstable or hours unusually high | (newbury2015performingelementalmicroanalysis pages 2-4) |
| Pre-session checklist | Detector | EDAX Octane Plus cooled; verify thermoelectric status | Start only after detector is thermally stable | (newbury2019electronexcitedxraymicroanalysis pages 2-3, garzon2023effectsofvariations pages 2-3) |
| Pre-session checklist | Energy calibration | Collect 30 s spectrum on Cu standard | Confirm Cu Lα ≈ 0.930 keV and Cu Kα ≈ 8.04 keV before session | (carlton2011scanningelectronmicroscopy pages 29-31) |
| Pre-session checklist | Resolution check | Verify Mn Kα FWHM ≤130 eV on Mn standard or Cu standard | Typical good SDD performance is ~127.5–128 eV | (newbury2011isscanningelectrona pages 2-4, newbury2014rigorousquantitativeelemental pages 5-6, garzon2023effectsofvariations pages 2-3) |
| Pre-session checklist | Beam current | Measure with Faraday cup; record in nA | Keep standards and unknowns at same current | (newbury2015performingelementalmicroanalysis pages 11-13) |
| Pre-session checklist | Dead-time check | On pure Al or Si, adjust current to 10% dead time at analytical WD | SDD routine quant target; avoid >15% for quant | (newbury*2013isscanningelectron pages 7-9, newbury2015performingelementalmicroanalysis pages 11-13) |
| Standard imaging settings | SE imaging | 15 kV; spot 5; WD 10 mm; 1024×884 px; 8-frame average | Default scout and morphology imaging | (carlton2011scanningelectronmicroscopy pages 29-31, carlton2011scanningelectronmicroscopy pages 4-7) |
| Standard imaging settings | BSE imaging | 15 kV; spot 5–6; WD 10 mm; 1024×884 px; 16-frame average | Default compositional/topographic balance | (carlton2011scanningelectronmicroscopy pages 29-31, carlton2011scanningelectronmicroscopy pages 19-21) |
| Standard imaging settings | High-mag BSE | 20 kV; spot 4; WD 10 mm; 2048×1768 px; 32-frame average | Use for polished XS, fine phase contrast, precipitates | (qin2020rapidsolidificationand pages 2-3, hyer2020understandingthelaser pages 1-2) |
| EDS quantitative defaults | kV | 15 kV for Al/Ti; 20 kV for Ni/Fe alloys | Follow overvoltage rule and keep same E0 for standards/unknowns | (newbury2015performingelementalmicroanalysis pages 11-13, carlton2011scanningelectronmicroscopy pages 29-31, hyer2020understandingthelaser pages 1-2, garzon2023effectsofvariations pages 3-6) |
| EDS quantitative defaults | Probe current | Tune to 10% dead time | Set by count-rate performance, not arbitrary spot size alone | (newbury2015performingelementalmicroanalysis pages 11-13, newbury*2013isscanningelectron pages 7-9) |
| EDS quantitative defaults | Working distance | 10 mm analytical WD | Keep WD fixed for all standards and unknowns | (carlton2011scanningelectronmicroscopy pages 29-31, newbury*2013isscanningelectron pages 7-9, guyett2024optimizingsemedxfor pages 3-4) |
| EDS quantitative defaults | Amp time | 3.84 µs | Routine quant default; compromise between throughput and resolution | (camus2007reevaluatingacquisitionparameters pages 1-2, newbury*2013isscanningelectron pages 7-9) |
| EDS quantitative defaults | Live time | 60 s minimum; 100 s preferred | Extend for minor/trace work | (carlton2011scanningelectronmicroscopy pages 31-34, guyett2024optimizingsemedxfor pages 4-6) |
| EDS quantitative defaults | Counts target | ≥1M total counts per spectrum | Also aim for ≥10,000 net counts above background for key peaks | (newbury*2013isscanningelectron pages 7-9, guyett2024optimizingsemedxfor pages 4-6) |
| EDS quantitative defaults | Replicates | ≥10 spots/sample (polished); ≥20/sample (powder) | Increase for heterogeneous powders or reused feedstock | (giunto2026accuratesem‑edsquantification pages 1-3, giunto2026accuratesem‑edsquantification pages 3-5) |
| EDS mapping defaults | kV | 15–20 kV | Use lower end for Al/light-element sensitivity, upper end for Ni/Fe alloys | (small2002theanalysisof pages 1-2, carlton2011scanningelectronmicroscopy pages 37-40) |
| EDS mapping defaults | Amp time | 0.96–1.92 µs | Faster throughput than spot quant | (camus2007reevaluatingacquisitionparameters pages 1-2, newbury*2013isscanningelectron pages 7-9) |
| EDS mapping defaults | Pixel resolution | 512×384 minimum | Do not oversample beyond interaction-volume-limited resolution | (carlton2011scanningelectronmicroscopy pages 4-7, carlton2011scanningelectronmicroscopy pages 37-40) |
| EDS mapping defaults | Dwell | 50–200 µs/pixel | Increase only when map noise or low-abundance elements require it | (carlton2011scanningelectronmicroscopy pages 37-40, guyett2024optimizingsemedxfor pages 4-6) |
| EDS mapping defaults | Frames | ≥32 accumulated | Use drift correction on long maps | (carlton2011scanningelectronmicroscopy pages 37-40) |
| EDS mapping defaults | Dead time | 15–25% acceptable for mapping speed | Faster than quant; do not use for best quantitative spots | (camus2007reevaluatingacquisitionparameters pages 1-2, newbury*2013isscanningelectron pages 7-9) |
| Magnification ladder | 100× | Overview / scout | Powder panorama; whole cross-section context | (carlton2011scanningelectronmicroscopy pages 19-21) |
| Magnification ladder | 500× | Morphology / defects | Satellites, agglomerates, melt-pool survey, pore field survey | (carlton2011scanningelectronmicroscopy pages 19-21, groarke2021powdercharacterization—methodsstandards pages 12-14) |
| Magnification ladder | 2,500× | Melt-pool detail | Individual melt-pool boundaries, coarse porosity, bonding | (qin2020rapidsolidificationand pages 2-3, hyer2020understandingthelaser pages 1-2) |
| Magnification ladder | 10,000× | Cellular / dendritic | AlSi10Mg cellular substructure, eutectic Si network | (qin2020rapidsolidificationand pages 2-3, hyer2020understandingthelaser pages 1-2) |
| Magnification ladder | 50,000× | Precipitates | Fine intermetallics; lower kV if feature size approaches interaction volume | (small2002theanalysisof pages 1-2, burgess2017ultralowkveds pages 5-6) |
| End-of-session | QC recheck | Re-measure Cu/Al standard dead time | Confirms no large drift over session | (rossen2017optimizationofsemeds pages 6-9, guyett2024optimizingsemedxfor pages 3-4) |
| End-of-session | Save files | Save all spectra (.msa + .spc), images (.tif 16-bit), metadata log | Keep raw + processed outputs | (newbury*2013isscanningelectron pages 23-26, newbury2015performingelementalmicroanalysis pages 11-13) |
| End-of-session | Required metadata | Record kV, current (nA), WD, mag, amp time, live time, dead time, date, operator, detector S/N, software version | Minimum reproducibility record for future reanalysis | (newbury2015performingelementalmicroanalysis pages 11-13, newbury*2013isscanningelectron pages 7-9, newbury2015performingelementalmicroanalysis pages 2-4) |


*Table: This compact table summarizes the default startup checks, imaging settings, EDS acquisition parameters, magnification ladder, and end-of-session requirements for routine FEI Apreo + EDAX TEAM work. It is designed to be printed and pinned next to the microscope for student use.*

---

## Summary

This SOP framework distinguishes parameters that should be **fixed** across all sessions (working distance at analytical WD, take-off angle, tilt at 0°, energy calibration procedure, metadata logging requirements) from those that must be **tuned per sample** (accelerating voltage per alloy class, beam current per dead-time target, amp time per analysis type, live time per concentration level). The critical operational principles are: (1) maintain identical conditions between standards and unknowns (newbury2015performingelementalmicroanalysis pages 11-13); (2) target ~10% dead time on SDD-EDS to minimize coincidence artifacts (newbury2015performingelementalmicroanalysis pages 11-13, newbury*2013isscanningelectron pages 7-9); (3) collect sufficient counts for statistical precision (≥10,000 net counts per peak for ~1% relative precision) (newbury*2013isscanningelectron pages 7-9); (4) use flat, polished specimens for quantitative analysis and understand that powder particle and rough-surface geometries introduce large systematic errors that standardless normalization conceals (newbury*2013isscanningelectron pages 23-26, newbury2012howtodo pages 1-2, small2002theanalysisof pages 1-2, newbury2011isscanningelectrona pages 2-4); and (5) verify analytical quality through pre-session calibration, within-session standard re-measurement, and cross-validation against ICP-OES or WDS (rossen2017optimizationofsemeds pages 6-9, guyett2024optimizingsemedxfor pages 3-4). Adoption of standards-based k-ratio analysis (rather than relying solely on standardless eZAF) is strongly recommended for any results intended for publication or alloy qualification, as standardless analysis carries systematic errors of up to ±25% relative at the 95% confidence level compared to ±5% for standards-based protocols (newbury2014rigorousquantitativeelemental pages 2-5, newbury2014rigorousquantitativeelemental pages 1-2).

References

1. (carlton2011scanningelectronmicroscopy pages 19-21): Robert Allen Carlton. Scanning electron microscopy and energy-dispersive x-ray spectrometry. ArXiv, pages 85-130, Jan 2011. URL: https://doi.org/10.1007/978-1-4419-8831-7\_4, doi:10.1007/978-1-4419-8831-7\_4. This article has 6 citations.

2. (groarke2021powdercharacterization—methodsstandards pages 12-14): Robert Groarke, Rajani K. Vijayaraghavan, Daniel Powell, Allan Rennie, and Dermot Brabazon. Powder characterization—methods, standards, and state of the art. Fundamentals of Laser Powder Bed Fusion of Metals, pages 491-527, Jun 2021. URL: https://doi.org/10.1016/b978-0-12-824090-8.00006-8, doi:10.1016/b978-0-12-824090-8.00006-8. This article has 52 citations.

3. (qin2020rapidsolidificationand pages 2-3): Hong Qin, Qingshan Dong, Vahid Fallah, and Mark R. Daymond. Rapid solidification and non-equilibrium phase constitution in laser powder bed fusion (lpbf) of alsi10mg alloy: analysis of nano-precipitates, eutectic phases, and hardness evolution. Metallurgical and Materials Transactions A, 51:448-466, Nov 2020. URL: https://doi.org/10.1007/s11661-019-05505-5, doi:10.1007/s11661-019-05505-5. This article has 118 citations.

4. (cauwenbergh2021unravellingthemultiscale pages 2-3): P. Van Cauwenbergh, V. Samaee, L. Thijs, J. Nejezchlebová, P. Sedlák, A. Iveković, D. Schryvers, B. Van Hooreweder, and K. Vanmeensel. Unravelling the multi-scale structure–property relationship of laser powder bed fusion processed and heat-treated alsi10mg. Scientific Reports, Mar 2021. URL: https://doi.org/10.1038/s41598-021-85047-2, doi:10.1038/s41598-021-85047-2. This article has 219 citations and is from a peer-reviewed journal.

5. (hyer2020understandingthelaser pages 1-2): Holden Hyer, Le Zhou, Sharon Park, Guilherme Gottsfritz, George Benson, Bjorn Tolentino, Brandon McWilliams, Kyu Cho, and Yongho Sohn. Understanding the laser powder bed fusion of alsi10mg alloy. Metallography, Microstructure, and Analysis, 9:484-502, Jul 2020. URL: https://doi.org/10.1007/s13632-020-00659-w, doi:10.1007/s13632-020-00659-w. This article has 173 citations.

6. (small2002theanalysisof pages 1-2): J.A. Small. The analysis of particles at low accelerating voltages (&lt;= 10 kv) with energy dispersive x-ray spectroscopy (eds). Journal of Research of the National Institute of Standards and Technology, 107:555, Nov 2002. URL: https://doi.org/10.6028/jres.107.047, doi:10.6028/jres.107.047. This article has 63 citations and is from a peer-reviewed journal.

7. (carlton2011scanningelectronmicroscopy pages 4-7): Robert Allen Carlton. Scanning electron microscopy and energy-dispersive x-ray spectrometry. ArXiv, pages 85-130, Jan 2011. URL: https://doi.org/10.1007/978-1-4419-8831-7\_4, doi:10.1007/978-1-4419-8831-7\_4. This article has 6 citations.

8. (carlton2011scanningelectronmicroscopy pages 37-40): Robert Allen Carlton. Scanning electron microscopy and energy-dispersive x-ray spectrometry. ArXiv, pages 85-130, Jan 2011. URL: https://doi.org/10.1007/978-1-4419-8831-7\_4, doi:10.1007/978-1-4419-8831-7\_4. This article has 6 citations.

9. (guyett2024optimizingsemedxfor pages 4-6): Paul C. Guyett, David Chew, Vitor Azevedo, Lucy C. Blennerhassett, Carolina Rosca, and Emma Tomlinson. Optimizing sem-edx for fast, high-quality and non-destructive elemental analysis of glass. Journal of Analytical Atomic Spectrometry, 39:2565-2579, Jan 2024. URL: https://doi.org/10.1039/d4ja00212a, doi:10.1039/d4ja00212a. This article has 40 citations and is from a peer-reviewed journal.

10. (newbury2015performingelementalmicroanalysis pages 2-4): Dale E. Newbury and Nicholas W. M. Ritchie. Performing elemental microanalysis with high accuracy and high precision by scanning electron microscopy/silicon drift detector energy-dispersive x-ray spectrometry (sem/sdd-eds). Journal of Materials Science, 50:493-518, Nov 2015. URL: https://doi.org/10.1007/s10853-014-8685-2, doi:10.1007/s10853-014-8685-2. This article has 553 citations and is from a peer-reviewed journal.

11. (burgess2017ultralowkveds pages 5-6): Simon Burgess, James Sagar, James Holland, Xiaobing Li, and Frank Bauer. Ultra-low kv eds – a new approach to improved spatial resolution, surface sensitivity, and light element compositional imaging and analysis in the sem. Microscopy Today, 25:20-29, Mar 2017. URL: https://doi.org/10.1017/s1551929517000013, doi:10.1017/s1551929517000013. This article has 56 citations.

12. (newbury2011isscanningelectron pages 2-3): Dale E. Newbury and Nicholas W. M. Ritchie. Is scanning electron microscopy/energy dispersive x-ray spectroscopy (sem/eds) quantitative? effect of specimen shape. SPIE Proceedings, 8036:803602, May 2011. URL: https://doi.org/10.1117/12.881040, doi:10.1117/12.881040. This article has 3 citations.

13. (newbury2015performingelementalmicroanalysis pages 11-13): Dale E. Newbury and Nicholas W. M. Ritchie. Performing elemental microanalysis with high accuracy and high precision by scanning electron microscopy/silicon drift detector energy-dispersive x-ray spectrometry (sem/sdd-eds). Journal of Materials Science, 50:493-518, Nov 2015. URL: https://doi.org/10.1007/s10853-014-8685-2, doi:10.1007/s10853-014-8685-2. This article has 553 citations and is from a peer-reviewed journal.

14. (newbury*2013isscanningelectron pages 7-9): Dale E. Newbury* and Nicholas W. M. Ritchie. Is scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds) quantitative? Scanning, 35 3:141-68, May 2013. URL: https://doi.org/10.1002/sca.21041, doi:10.1002/sca.21041. This article has 729 citations.

15. (giunto2026accuratesem‑edsquantification pages 1-3): Andrea Giunto, Yuxing Fei, Pragnay Nevatia, Bernardus Rendy, Nathan Szymanski, and Gerbrand Ceder. Accurate sem‑eds quantification, automation, and machine learning enable high‑throughput compositional characterization of powders. Unknown journal, Jan 2026. URL: https://doi.org/10.21203/rs.3.rs-7837297/v2, doi:10.21203/rs.3.rs-7837297/v2.

16. (carlton2011scanningelectronmicroscopy pages 29-31): Robert Allen Carlton. Scanning electron microscopy and energy-dispersive x-ray spectrometry. ArXiv, pages 85-130, Jan 2011. URL: https://doi.org/10.1007/978-1-4419-8831-7\_4, doi:10.1007/978-1-4419-8831-7\_4. This article has 6 citations.

17. (carlton2011scanningelectronmicroscopy pages 31-34): Robert Allen Carlton. Scanning electron microscopy and energy-dispersive x-ray spectrometry. ArXiv, pages 85-130, Jan 2011. URL: https://doi.org/10.1007/978-1-4419-8831-7\_4, doi:10.1007/978-1-4419-8831-7\_4. This article has 6 citations.

18. (garzon2023effectsofvariations pages 3-6): Carlos M. Garzón, Juan P.N. Cruz, Johan K. Noreña, Eduar F. Pineda, and Juan S. Cachaya. Effects of variations in operating conditions on the preci-sion and accuracy of standardless elemental analysis of stainless steel by sem-eds. Ingeniería e Investigación, 43:e94361, Nov 2023. URL: https://doi.org/10.15446/ing.investig.94361, doi:10.15446/ing.investig.94361. This article has 2 citations.

19. (garzon2023effectsofvariations pages 2-3): Carlos M. Garzón, Juan P.N. Cruz, Johan K. Noreña, Eduar F. Pineda, and Juan S. Cachaya. Effects of variations in operating conditions on the preci-sion and accuracy of standardless elemental analysis of stainless steel by sem-eds. Ingeniería e Investigación, 43:e94361, Nov 2023. URL: https://doi.org/10.15446/ing.investig.94361, doi:10.15446/ing.investig.94361. This article has 2 citations.

20. (newbury2011isscanningelectrona pages 2-4): D Newbury and N Ritchie. Is scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds) quantitative? effects of specimen shape. Unknown journal, 2011.

21. (newbury*2013isscanningelectron pages 14-16): Dale E. Newbury* and Nicholas W. M. Ritchie. Is scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds) quantitative? Scanning, 35 3:141-68, May 2013. URL: https://doi.org/10.1002/sca.21041, doi:10.1002/sca.21041. This article has 729 citations.

22. (newbury2019electronexcitedxraymicroanalysis pages 2-3): Dale E. Newbury and Nicholas W.M. Ritchie. Electron-excited x-ray microanalysis by energy dispersive spectrometry at 50: analytical accuracy, precision, trace sensitivity, and quantitative compositional mapping. Microscopy and Microanalysis, 25:1075-1105, Oct 2019. URL: https://doi.org/10.1017/s143192761901482x, doi:10.1017/s143192761901482x. This article has 53 citations and is from a peer-reviewed journal.

23. (camus2007reevaluatingacquisitionparameters pages 1-2): P. Camus, D. Rohde, and D. McMillan. Reevaluating acquisition parameters for elemental quantification with eds. Microscopy and Microanalysis, 13:1436-1437, Aug 2007. URL: https://doi.org/10.1017/s1431927607073990, doi:10.1017/s1431927607073990. This article has 0 citations and is from a peer-reviewed journal.

24. (newbury2014rigorousquantitativeelemental pages 5-6): Dale E. Newbury and Nicholas W. M. Ritchie. Rigorous quantitative elemental microanalysis by scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds) with spectrum processing by nist dtsa-ii. SPIE Proceedings, 9236:92360H, Sep 2014. URL: https://doi.org/10.1117/12.2065842, doi:10.1117/12.2065842. This article has 24 citations.

25. (giunto2026accuratesem‑edsquantification pages 3-5): Andrea Giunto, Yuxing Fei, Pragnay Nevatia, Bernardus Rendy, Nathan Szymanski, and Gerbrand Ceder. Accurate sem‑eds quantification, automation, and machine learning enable high‑throughput compositional characterization of powders. Unknown journal, Jan 2026. URL: https://doi.org/10.21203/rs.3.rs-7837297/v2, doi:10.21203/rs.3.rs-7837297/v2.

26. (rossen2017optimizationofsemeds pages 6-9): J.E. Rossen and K.L. Scrivener. Optimization of sem-eds to determine the c-a-s-h composition in matured cement paste samples. Materials Characterization, 123:294-306, Jan 2017. URL: https://doi.org/10.1016/j.matchar.2016.11.041, doi:10.1016/j.matchar.2016.11.041. This article has 239 citations and is from a peer-reviewed journal.

27. (newbury2014rigorousquantitativeelemental pages 1-2): Dale E. Newbury and Nicholas W. M. Ritchie. Rigorous quantitative elemental microanalysis by scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds) with spectrum processing by nist dtsa-ii. SPIE Proceedings, 9236:92360H, Sep 2014. URL: https://doi.org/10.1117/12.2065842, doi:10.1117/12.2065842. This article has 24 citations.

28. (newbury2014rigorousquantitativeelemental pages 2-5): Dale E. Newbury and Nicholas W. M. Ritchie. Rigorous quantitative elemental microanalysis by scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds) with spectrum processing by nist dtsa-ii. SPIE Proceedings, 9236:92360H, Sep 2014. URL: https://doi.org/10.1117/12.2065842, doi:10.1117/12.2065842. This article has 24 citations.

29. (newbury*2013isscanningelectron pages 23-26): Dale E. Newbury* and Nicholas W. M. Ritchie. Is scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds) quantitative? Scanning, 35 3:141-68, May 2013. URL: https://doi.org/10.1002/sca.21041, doi:10.1002/sca.21041. This article has 729 citations.

30. (newbury2012howtodo pages 1-2): D.E. Newbury and N.W. Ritchie. How to do really bad sem/eds quantitative analysis, and never even notice! Microscopy and Microanalysis, 18:1004-1005, Jul 2012. URL: https://doi.org/10.1017/s1431927612006873, doi:10.1017/s1431927612006873. This article has 4 citations and is from a peer-reviewed journal.

31. (guyett2024optimizingsemedxfor pages 3-4): Paul C. Guyett, David Chew, Vitor Azevedo, Lucy C. Blennerhassett, Carolina Rosca, and Emma Tomlinson. Optimizing sem-edx for fast, high-quality and non-destructive elemental analysis of glass. Journal of Analytical Atomic Spectrometry, 39:2565-2579, Jan 2024. URL: https://doi.org/10.1039/d4ja00212a, doi:10.1039/d4ja00212a. This article has 40 citations and is from a peer-reviewed journal.

32. (newbury*2013isscanningelectron pages 1-2): Dale E. Newbury* and Nicholas W. M. Ritchie. Is scanning electron microscopy/energy dispersive x-ray spectrometry (sem/eds) quantitative? Scanning, 35 3:141-68, May 2013. URL: https://doi.org/10.1002/sca.21041, doi:10.1002/sca.21041. This article has 729 citations.

33. (kallioUnknownyearaccuracyandprecision pages 15-20): M Kallio. Accuracy and precision comparison with elemental analysis parameter optimization for xrf, oes, and sem-eds. Unknown journal, Unknown year.