# Resolving Mg discrepancy in LPBF AlSi10Mg using Agilent 8900 ICP-MS/MS — feasibility, ASTM-aligned SOP, and comparison to SEM-EDS

> **Edison `LITERATURE_HIGH` task `a5c9d1c7-2fd2-446c-811e-dceed9d6381a`** — submitted in response to [PR #93 comment 4566517533](https://github.com/vertical-cloud-lab/byu-vcl/pull/93#issuecomment-4566517533). Follow-up Edison query after the Agilent 8900 ICP-MS/MS at the [BYU Spectroscopic Facility — Atomic Analysis](https://labs.chem.byu.edu/byu-spectroscopic-facility/atomic-analysis) was identified as a candidate technique to validate the SEM-EDS Mg result (see also: comment 4566266267 referencing the digital-alloy-lab-private repo for other BYU composition-analysis instruments). Not waiting on the response — fetch + integrate when prompted.

## Context

The BYU Vertical Cloud Lab is characterizing **AlSi10Mg** gas-atomized powder and laser-powder-bed-fusion (LPBF) printed parts. Independent SEM-EDS (FEI Apreo + EDAX TEAM, standardless eZAF Smart Quant) measurements give Mg ≈ **1.4–1.6 wt%** consistently — about **3–7× higher than the nominal 0.20–0.45 wt% Mg** in AlSi10Mg — including on a metallographically polished cross-section that no longer shows surface oxygen. Si (~9.1–9.4 wt%) and Al (~89 wt%) recover to nominal after polishing, so the discrepancy is specific to Mg.

Suspect root causes already flagged (from prior Edison literature queries `1c63284b`, `21ba848f`, `afe8c121`, `705df51f`):
- standardless eZAF deconvolution bias for the Mg Kα (1.253 keV) / Al Kα (1.486 keV) overlap on a ~135 eV-FWHM SDD,
- background-fit extrapolation under the Mg shoulder,
- short amp-time (0.96 µs) on the polished session degrading resolution.

We have BYU campus access to an **Agilent 8900 ICP-MS/MS (triple-quad ICP-MS)** at the BYU Spectroscopic Facility — Atomic Analysis (https://labs.chem.byu.edu/byu-spectroscopic-facility/atomic-analysis, contact via https://labs.chem.byu.edu/instruments-training). It has standard ICP-MS reaction-cell capability (He, H2, O2, NH3, etc.).

## What we need

Please give a **practical, ASTM-aligned, Edison-grade answer** to the following questions, with primary references where possible:

1. **Is ICP-MS/MS the right technique to resolve a ~1 wt% vs ~0.3 wt% Mg discrepancy in AlSi10Mg?**
   - Expected precision, accuracy, and detection limit for Mg (24Mg, 25Mg, 26Mg) in an Al-Si matrix on the Agilent 8900 vs typical SEM-EDS — quantitative comparison.
   - Polyatomic / isobaric interferences on Mg isotopes in an Al-Si-Mg digest (12C12C, 48Ca2+ / 48Ti2+ on 24Mg, 50Ti2+ on 25Mg, etc.); best reaction-cell mode on the 8900 (He KED, H2, O2 mass-shift, NH3) for clean Mg quantification.
   - Internal-standard / mass-shift schemes for Al-rich digests.
   - Total-Al matrix suppression at % level; dilution / TDS limit (typical 8900 spec < 0.2 % TDS).
   - Would ICP-OES instead (cheaper, faster, well-suited to wt%-level analytes) be a better fit than ICP-MS/MS for major elements at this concentration range? Pros/cons.

2. **ASTM and ISO standards** governing this workflow — citation + what each prescribes:
   - ASTM E1097, E3061, E3097, E1479, E2823, B557 / B557M, E34, B215; ISO/ASTM 52907 / 52900 / F3301 / F3318; ISO 17025.

3. **Sample preparation procedure** for AlSi10Mg powder and printed-part coupons.
   - Digestion: aqua regia? HF + HNO3 + HCl? Microwave (CEM MARS6 / Anton Paar Multiwave)? Hot-block?
   - Mass to dissolve (typical 100–250 mg), final dilution, dilution factor, blank + spike + duplicate cadence.
   - HF safety / labware / calcium-gluconate first aid.
   - Representative sampling per ASTM B215 (riffle splitter) for 20–63 µm powder.
   - For printed parts: where to cut a coupon (build-direction); surface prep before dissolution.

4. **Calibration strategy.**
   - Matrix-matched external standards (Inorganic Ventures / SPEX / High-Purity).
   - Standard addition for AlSi10Mg matrix.
   - CRMs: NIST SRM 854 / 855, IARM Al-alloy CRMs from Brammer Standard, NIST SRM 1257b.
   - Mass-bias / drift correction with Sc or In internal standard.

5. **Expected sources of disagreement between SEM-EDS and ICP-MS/MS.**
   - SEM-EDS ~µm³ interaction volume at one spot vs ICP-MS/MS ~100–250 mg bulk — explain the bulk vs local distinction for an LPBF AlSi10Mg matrix where Mg is partitioned to nm-scale Mg2Si / Mg–Si co-clusters and the Si-rich eutectic network (Lefebvre 2021, Hadadzadeh 2019, Cauwenbergh 2021).
   - Could the SEM-EDS values be physically real for localized Mg-rich regions while bulk ICP-MS/MS confirms nominal 0.2–0.45 wt%?

6. **Concrete recommended action plan for BYU VCL.**
   - Step-by-step protocol (sample → digest → dilute → calibrate → measure → report) for AlSi10Mg powder + printed-part bulk Mg / Al / Si on the Agilent 8900.
   - QA/QC: % recovery on matched CRM, n ≥ 3 replicates, RSD < 5 % for majors, blank correction, spike recovery 95–105 %.
   - Approximate per-sample cost / turn-around at a typical university facility (for Genesis-proposal budgeting).
   - Whether to also do ICP-OES as an independent cross-check.
   - Whether EPMA + WDS at a partner lab would be a complementary local-scale check on Mg with better Mg Kα / Al Kα separation than SDD-EDS.

7. **Explicit verdict.** Is ICP-MS/MS (a) the gold-standard way to confirm bulk Mg in AlSi10Mg, (b) overkill — ICP-OES is sufficient, or (c) the wrong avenue (because trace Mg in Al is not the issue and instead the SEM-EDS deconvolution is the only thing that needs fixing)?

Please return primary citations, ASTM standard numbers, and the most up-to-date Agilent 8900 application notes / EPA / ISO methods relevant to Al-alloy ICP-MS/MS.
