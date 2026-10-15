We are establishing a standard SEM/EDS workflow for routine quantitative characterization of (a) gas-atomized metal AM powder feedstock and (b) polished cross-sections of LPBF-printed parts in a small academic AM lab (BYU Vertical Cloud Lab). Equipment: FEI Apreo FEG-SEM + EDAX Octane Plus 30 mm² SDD running TEAM software with eZAF Smart Quant standardless. Primary alloy of interest is AlSi10Mg (nominal Si 9-11 wt%, Mg 0.20-0.45 wt%, Fe <0.55 wt%, Al bal), but the SOP will be applied broadly to Al, Ti, Ni, and steel AM powders and parts.

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