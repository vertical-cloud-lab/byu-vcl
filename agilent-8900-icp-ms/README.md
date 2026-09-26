# Agilent 8900 ICP-MS — Sample Preparation & Characterization of Aluminum Alloys

Working notes and an evidence-based starting workflow for using the **Agilent 8900
triple-quadrupole ICP-MS (ICP-QQQ)** to characterize the elemental composition of
metallic feedstocks in the lab — primarily **aluminum alloys** (AlSi10Mg from LPBF
feedstock, 1100 aluminum wire) and **silicon powder**.

- Related issue: [vertical-cloud-lab/byu-vcl#128](https://github.com/vertical-cloud-lab/byu-vcl/issues/128)
- Initial training video: <https://youtu.be/yFkYrjH0SDE>

Key constraint from the training: any sample must be **digested into a clear,
water-soluble solution with no suspended particles** before it can be nebulized.

> **Lab safety decision: we avoid hydrofluoric acid (HF).** HF is the classical
> reagent for dissolving silicon, but its acute toxicity is unacceptable for our lab.
> The recommendations below are built around **HF-free** routes. Note that
> **tetrafluoroboric acid (HBF₄) is *not* a true HF-free substitute** — it hydrolyzes
> back to HF on heating/storage and requires HF-equivalent precautions — so it is
> treated only as a last resort, not a primary method.

## How these notes were produced

High-effort [Edison Scientific](https://edisonscientific.gitbook.io/edison-cookbook/edison-client)
literature reviews were run, then synthesized with an Edison **Analysis** task that
ingested them and produced one cohesive, deduplicated, HF-free-prioritized set
of recommendations. A later review compares **XRF vs. ICP-OES vs. ICP-MS** for bulk
composition. The scripts and raw outputs are under [`edison/`](edison/):

| File | Content |
| --- | --- |
| [`edison/artifacts/01_acid_digestion.md`](edison/artifacts/01_acid_digestion.md) | Acid digestion protocols (hot-plate vs. microwave; HNO₃/HCl/HF/HBF₄; HF safety & boric-acid complexation) |
| [`edison/artifacts/02_icpms_measurement.md`](edison/artifacts/02_icpms_measurement.md) | ICP-MS/MS measurement: isotope selection, interferences, He/H₂/O₂/NH₃ cell modes, internal standards, plasma settings |
| [`edison/artifacts/03_qaqc_calibration.md`](edison/artifacts/03_qaqc_calibration.md) | Calibration, matrix matching, CRMs, blanks, spike recovery, LOD/LOQ, contamination control |
| [`edison/artifacts/04_hf_free_digestion.md`](edison/artifacts/04_hf_free_digestion.md) | **HF-free digestion options** for Si-bearing Al alloys (HBF₄, alkaline fusion, NaOH/KOH, aqua regia, HF-free microwave) and their ICP-MS trade-offs |
| [`edison/artifacts/05_technique_selection.md`](edison/artifacts/05_technique_selection.md) | **XRF vs. ICP-OES vs. ICP-MS** for *bulk* composition of a 16-element Al-alloy palette: dynamic range, accuracy, sample-prep burden, element coverage, cost, and a scenario-based decision guide |
| [`edison/artifacts/analysis_synthesis_hf_free.md`](edison/artifacts/analysis_synthesis_hf_free.md) | **HF-free-prioritized synthesis** (current recommendation): executive summary, two-route SOP, consolidated table, safety checklist, open decisions |
| [`edison/artifacts/analysis_synthesis.md`](edison/artifacts/analysis_synthesis.md) | Earlier synthesis (includes HF-based routes; superseded by the HF-free synthesis above, kept for reference) |

Reproduce / continue: `python edison/submit_literature.py` → `fetch_literature.py`
→ `submit_analysis.py` → `fetch_analysis.py`. The analysis step defaults to the
HF-free synthesis (`ANALYSIS_MODE=hf_free`). Task IDs are stored in
`edison/tasks.json` so a run can be resumed in a later session. The scripts read the
API key from `EDISON_API_KEY` (the secret value is never echoed).

> These notes are AI-assisted literature syntheses for getting started, **not** a
> validated SOP. Verify every protocol against instrument/vessel manuals, your CRMs,
> and BYU EHS before running samples.

## TL;DR — recommended HF-free starting workflow

No single HF-free method does everything HF does, so the practical answer is **two
routes plus a triage step**. First decide: *does silicon itself need to be quantified,
or only the aluminum matrix and trace metals?*

1. **Low-Si aluminum (1100 wire):** simple **open-vessel** digestion in ~5% v/v HCl,
   50–70 °C, 15–60 min. No HF, no fusion needed.
2. **Route A — silicon MUST be quantified (AlSi10Mg, Si powder): lithium metaborate
   (LiBO₂) fusion.** This is the strongest HF-free route to *total* silicon. Fuse
   ~0.10–0.25 g sample with ~8× mass LiBO₂ (≥99.99%) in a Pt crucible at 950–1050 °C
   for ~2–2.5 h, dissolve the melt in ~5% HNO₃ (or HCl), filter, then dilute heavily.
   *Cost:* high Li/B salt burden → large dilution (degrades trace detection limits),
   and B/Li can't be measured.
3. **Route B — silicon NOT needed (matrix + trace metals only): aqua regia.** Digest
   ~0.10–0.25 g in 5–7 mL HCl:HNO₃ (3:1), warm until the Al dissolves, then **filter
   out the Si-rich residue** to get a clear solution. *Cost:* Si (and anything locked
   in Si-rich phases) is excluded — fine for routine Cu/Fe/Mg/Mn/Zn/Ti/Cr/Ni QC.
4. **Tame the high-Al matrix with dilution.** Keep TDS < ~0.1–0.2%; consider **two
   dilutions** per digest (high-dilution for majors, lower-dilution for traces).
5. **Run the 8900 as a multi-mode MS/MS method:** He KED (mid-mass), O₂ mass-shift for
   Si (²⁸Si→²⁸Si¹⁶O⁺ at m/z 44) and Cr, NH₃ for Ti/V. Internal standards Sc/Ge/Rh/In/Bi
   at ~50–100 µg/L for drift correction.
6. **QA/QC is mandatory:** matrix-matched external calibration + internal standards,
   independent ICV, CCV every ~10 samples, method/reagent blanks, matrix spikes
   (75–125%), and a Si-bearing Al-alloy **CRM**.
7. **HBF₄ is a last resort only.** It is corrosive, hydrolyzes to HF, and needs
   HF-equivalent PPE/precautions — and it is unvalidated for AlSi10Mg. Prefer LiBO₂
   fusion before considering it.

See [`edison/artifacts/analysis_synthesis_hf_free.md`](edison/artifacts/analysis_synthesis_hf_free.md)
for the full two-route SOP outline, the consolidated isotope/mode/internal-standard
table, the HF-free safety checklist, and the open decisions the lab still needs to
make (e.g. whether Si must be quantified at all, CRM selection, and whether major
elements stay on ICP-MS or move to ICP-OES/XRF).

## XRF vs. ICP-OES vs. ICP-MS for *bulk* composition

If the goal is primarily **bulk (total) composition** across our 16-element palette
(rather than trace impurities), the technique-selection review
([`05_technique_selection.md`](edison/artifacts/05_technique_selection.md)) points to a
**two-tier, mostly digestion-free workflow** — which also dovetails with the HF-free
goal, since XRF needs no acid digestion at all:

1. **XRF is the first-line bulk tool.** It measures solid metal directly (no digestion,
   no HF), includes the Al matrix itself, and is accurate for major/minor elements at
   wt% levels when calibrated with Al-alloy CRMs. Prefer **WDXRF** for accurate lab
   quantification; **handheld/benchtop EDXRF** is great for fast screening/sorting but
   less reliable for light elements (Mg, Si) in Al — EDXRF Mg errors of ~40% relative
   have been reported.
2. **ICP-OES is the solution-based workhorse** when you need it: accurate light-element
   quantification (Mg, Na, Li, B) that XRF handles poorly, wet-chemistry verification of
   XRF, or elements below the XRF floor. It tolerates high-matrix digests well, but does
   require getting the sample into solution.
3. **ICP-MS (the Agilent 8900) is best reserved for trace/ultra-trace impurities** (ppm–ppb),
   interference-heavy elements where ICP-QQQ reaction-cell chemistry helps, and verification
   below ICP-OES limits. For bulk wt% majors it is usually overkill: the high Al/Si matrix
   forces heavy dilution, and major-element precision rarely beats ICP-OES.

**Bottom line:** XRF every sample (no digestion needed), confirm periodically with ICP-OES
on digested aliquots, and reserve the 8900 ICP-MS for trace impurities or disputed/spec
samples. This minimizes both the digestion burden and the need for HF. Full dynamic-range,
accuracy, element-coverage, cost, and scenario tables are in
[`05_technique_selection.md`](edison/artifacts/05_technique_selection.md).
