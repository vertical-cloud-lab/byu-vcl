Please analyze the attached BYU VCL SEM-EDS dataset (see README.md in the bundle for full context, acquisition parameters, and our cross-sample comparison table) and give us an independent expert assessment.

The dataset contains three measurement sets on the SAME nominal material — AlSi10Mg gas-atomized AM powder (nominal: Si 9-11 wt%, Mg 0.20-0.45 wt%, Fe <0.55 wt%, Al balance) — collected on an FEI Apreo + EDAX Octane Plus SDD (TEAM software, eZAF Smart Quant standardless):
  1. Loose powder on carbon tape (Mar 2026, training session) — CSV/XML/MSA spectra, no PDF report
  2. Non-flat as-printed LPBF surface (Apr 30, 2026) — PDF report + raw spectrum; 15 kV, 460.8 s, 1.92 µs amp, 130.4 eV resolution; quant: O 8.10, Mg 1.64, Al 80.79, Si 9.47 wt%
  3. Polished cross-section of the same LPBF print (May 22, 2026) — two areas; 15 kV, 0.96 µs amp, 135.5 eV resolution; quant Area 6: Mg 1.43, Al 89.16, Si 9.41 wt%; Area 7: Mg 1.42, Al 89.45, Si 9.12 wt%

Specific questions:

A. **Are we on the right track?** Si recovery (~9.1-9.4 wt% after polishing) matches nominal. Polishing eliminated the 8 wt% oxygen signal that the non-flat sample showed. These both look like positive signs — agree?

B. **The Mg measurement is consistently ~1.4-1.6 wt% across ALL three datasets — about 3-7x higher than the nominal 0.20-0.45 wt%.** Why? Possible causes we are considering:
   1. eZAF standardless Cliff-Lorimer fit for the Mg Kα (1.253 keV) / Al Kα (1.486 keV) overlap is systematically biased high at this concentration ratio.
   2. The polished sample used amp time 0.96 µs (135.5 eV resolution) instead of 1.92 µs (130.4 eV resolution), worsening the Mg-Al peak separation.
   3. Real Mg-rich phases / precipitates in the as-built microstructure (Mg2Si, MgAl2O4 spinel, Mg surface segregation that survives polishing).
   4. Bremsstrahlung background under Mg Kα being mis-modeled because the BackgroundRegions defined in the XML (2.14-2.42, 2.865-3.145, 4.865-5.145, 6.865-7.145 keV) do not include any region between 0 and 2 keV — i.e. the background under Mg is being extrapolated from windows above the Si peak.
   5. Other?

Please read the raw .msa spectrum (EDS_Spectrum_NonFlat_AlSi10Mg_3d.msa) and reprocess it yourself if useful. Open-source HyperSpy/eXSpy is a fine choice; you can also use NIST DTSA-II numerically. The .msa header gives all calibration info (XPERCHAN=5 eV/channel, OFFSET=0, 4096 channels, 15 kV, 120 s on that one).

C. **The "small spheres" coating the polished AlSi10Mg surface** (which Gage flagged): is this likely Kapton/polishing residue, a real microstructure feature (e.g., spatter, Mg-rich nodules, intermetallic precipitates in the eutectic), or something else? The fishscale melt-pool pattern visible under optical microscopy was NOT visible in SEM at any magnification on the polished sample — what does that suggest about prep state or imaging mode?

D. **Anything weird in the spectra / acquisition setup you would flag**, e.g.:
   - The very short 0.96 µs amp time on the polished sample (Mike Standing's group used 7.68 µs in training; ASTM E1508 favors longer amp time = better resolution for trace elements).
   - The take-off angle changing from 48.7° (non-flat) to 35° (polished).
   - Sample-name field saying "Si-100" instead of "AlSi10Mg" (probably just a label that didn't get updated; please confirm there's no instrument-level confusion).
   - Dead time is not reported in the PDF — ASTM E1508 wants 20-30%. Can you infer it from the .msa (live time = 120 s; real time not given)?
   - Sum peaks or escape peaks visible? Si escape peak at ~1.74 keV could confuse Si quant.

E. **Things to watch out for next time / recommended changes** for our next acquisition session (we'll be running another polished sample soon, possibly with Mike Standing spot-checking). Please give concrete, parameter-level recommendations: kV, beam current/spot size, live time, amp time, target dead time, mag range, # of areas per sample, whether to use standards (and what), whether to use WDS instead of/in addition to EDS, etc.

F. **Clarifying questions** — list anything you would like us to provide (additional metadata, missing files, repeat measurements at different conditions, an ICP-OES bulk-composition reference value, etc.) before drawing firm conclusions.

Please structure your response as: (1) Verdict (right track / not on the right track / partial); (2) Key issues identified with severity; (3) Most-likely cause of the high Mg result, with quantitative reasoning; (4) Concrete recommendations; (5) Clarifying questions for the team.
