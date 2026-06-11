# Agilent 8900 ICP-MS — Sample Preparation & Characterization of Aluminum Alloys

Working notes and an evidence-based starting workflow for using the **Agilent 8900
triple-quadrupole ICP-MS (ICP-QQQ)** to characterize the elemental composition of
metallic feedstocks in the lab — primarily **aluminum alloys** (AlSi10Mg from LPBF
feedstock, 1100 aluminum wire) and **silicon powder**.

- Related issue: [vertical-cloud-lab/byu-vcl#128](https://github.com/vertical-cloud-lab/byu-vcl/issues/128)
- Initial training video: <https://youtu.be/yFkYrjH0SDE>

Key constraint from the training: any sample must be **acid-digested into a clear,
water-soluble solution with no suspended particles** before it can be nebulized.

## How these notes were produced

Three high-effort [Edison Scientific](https://edisonscientific.gitbook.io/edison-cookbook/edison-client)
literature reviews were run, then synthesized with an Edison **Analysis** task that
ingested all three reviews and produced one cohesive, deduplicated set of
recommendations. The scripts and raw outputs are under [`edison/`](edison/):

| File | Content |
| --- | --- |
| [`edison/artifacts/01_acid_digestion.md`](edison/artifacts/01_acid_digestion.md) | Acid digestion protocols (hot-plate vs. microwave; HNO₃/HCl/HF/HBF₄; HF safety & boric-acid complexation) |
| [`edison/artifacts/02_icpms_measurement.md`](edison/artifacts/02_icpms_measurement.md) | ICP-MS/MS measurement: isotope selection, interferences, He/H₂/O₂/NH₃ cell modes, internal standards, plasma settings |
| [`edison/artifacts/03_qaqc_calibration.md`](edison/artifacts/03_qaqc_calibration.md) | Calibration, matrix matching, CRMs, blanks, spike recovery, LOD/LOQ, contamination control |
| [`edison/artifacts/analysis_synthesis.md`](edison/artifacts/analysis_synthesis.md) | **Cohesive synthesis: executive summary, SOP outline, consolidated table, safety checklist, open questions** |

Reproduce / continue: `python edison/submit_literature.py` → `fetch_literature.py`
→ `submit_analysis.py` → `fetch_analysis.py`. Task IDs are stored in
`edison/tasks.json` so a run can be resumed in a later session. The scripts read the
API key from `EDISON_API_KEY` (the secret value is never echoed).

> These notes are AI-assisted literature syntheses for getting started, **not** a
> validated SOP. Verify every protocol against instrument/vessel manuals, your CRMs,
> and BYU EHS before running samples — especially anything involving HF.

## TL;DR — recommended starting workflow

1. **Triage by silicon content.**
   - **1100 Al wire (low-Si):** simple **open-vessel** digestion in ~5% v/v HCl,
     50–70 °C, 15–60 min. No HF needed.
   - **AlSi10Mg and Si powder (Si-bearing):** require a **fluoride source** and
     **closed-vessel microwave** digestion to fully dissolve Si phases.
2. **Primary total-dissolution digest (AlSi10Mg, 50 mg):** 5 mL HNO₃ + 2 mL HCl +
   1 mL HF, microwave to 180–200 °C, 20–30 min hold; then complex residual fluoride
   with ~10 mL of 5% w/v **boric acid** before introduction to quartz hardware.
   - **HF-deferred alternative:** swap HF for **HBF₄** during method development, but
     validate against a CRM/HF method before routine use.
   - **Silicon powder:** 5 mL HNO₃ + 2 mL HF, microwave ~180 °C, then boric acid.
3. **Tame the high-Al matrix with dilution.** Keep TDS < ~0.1–0.2%; run **two
   dilutions** per digest (high-dilution for majors Al/Si/Mg, lower-dilution for traces).
4. **Run the 8900 as a multi-mode MS/MS method:** He KED (mid-mass), H₂ on-mass for
   Si, O₂ mass-shift for Cr, NH₃ for Ti/V. Internal standards Sc/Ge/Rh/In/Bi at
   ~50–100 µg/L.
5. **QA/QC is mandatory:** matrix-matched external calibration + internal standards,
   independent ICV, CCV every ~10 samples, method/reagent blanks, matrix spikes
   (75–125%), and a Si-bearing Al-alloy **CRM**.
6. **HF safety first:** approved EHS SOP, buddy system, fume hood, PTFE/PFA only (no
   glass), HF-rated PPE, and in-date **2.5% calcium gluconate gel** before any HF work.

See [`edison/artifacts/analysis_synthesis.md`](edison/artifacts/analysis_synthesis.md)
for the full SOP outline, the consolidated isotope/mode/internal-standard table, the
prioritized safety checklist, and the open decisions the lab still needs to make
(e.g. HF-now vs. HBF₄-first, CRM selection, whether majors stay on ICP-MS or move to
ICP-OES/XRF).
