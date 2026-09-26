# Edison query: validate WDXRF/EDXRF standards discussion + broad Al-alloy composition space with no direct standard

> **Status (2026-07-14):** Submitted; awaiting response. Will integrate findings when fetched.
>
> | Task ID | Job | Submitted |
> |---|---|---|
> | `068a5ac1-9deb-4174-8e99-cd99aed604e8` | `LITERATURE_HIGH` (PaperQA3-high) | 2026-07-14 |

Submitted in response to [PR #95 trigger comment](https://github.com/vertical-cloud-lab/byu-vcl/pull/95#issuecomment-4972304019) asking for validation and review of the WDXRF/EDXRF discussion — Ronnie's report of the conversation with Kevin Rey (WDXRF accurate but ~3–4 weeks to build new standards since his current calibrations are geological; EDXRF quick test on the AlSi10Mg powder sample already left with him; ICP-MS/OES fallback) and the Claude-generated answer on XRF standards ([comment 4966986994](https://github.com/vertical-cloud-lab/byu-vcl/pull/95#issuecomment-4966986994)) — plus a forward-looking question: **how do you set up quantitative composition measurement when exploring a broad Al-alloy composition space for which no grade-matched standard exists?**

## Query structure

### Part 1 — point-by-point corroborate/qualify/refute (with citations)

Facility-manager statements:

- 1a. WDXRF accurate but ~3–4 weeks to develop new (non-geological) standards for Al-alloy powder.
- 1b. What accuracy is realistically achievable for Mg at 0.2–0.45 wt% by quick standardless-FP EDXRF on loose/cupped powder (Mg Kα fluorescence yield, matrix absorption, particle-size effects, detection limits)?
- 1c. ICP-MS or ICP-OES as a "not super complicated, very consistent" fallback.

AI-assistant claims under review:

- 2a. XRF standards are matrix-matched multi-element alloy disks, not one-per-element; curves per element line, suites per matrix.
- 2b. New analyte usually ≠ new suite (if certified in existing disks); new alloy family generally = new suite.
- 2c. Alloy 360 ≈ AlSi10Mg; commercial CRMs exist (Arconic KA/KB/KC/SS-360, ARMI|MBH EN AC-43000/43100, NIST SRM 87a, A356/413 range extenders).
- 2d. Standardless FP ~5–10 % relative on majors; FP + type standardization collapses a multi-week empirical build to ~a day or two.
- 2e. Pure standardless FP is marginal for Mg at 0.2–0.45 wt%; a grade-matched anchor materially helps.
- 2f. Solid-disk calibrations don't transfer directly to powder; particle/packing bias worst for Mg Kα.
- 2g. Three prep routes: powder cup/pellet + FP-type-standard → pellet-vs-pellet calibration → lithium-borate fusion beads (synthetic oxide standards possible; geology facility's home turf).
- 2h. Fusion caveats: destructive, ~10× dilution, metallic Al attacks Pt crucibles without pre-oxidation, exothermic-oxidation safety.
- 2i. Advice: buy 2–3 disks of the 360 family + type-standardized FP; keep ICP-MS/MS (or OES) as the Mg accuracy anchor.

### Part 2 — additional considerations to flag

Combustible-dust safety for fine Al powder; XRF sampling depth vs ~20–63 µm particle size and MgO surface-film enrichment on gas-atomized powder; He vs vacuum path; Al Kα tailing / sum peaks near Mg in EDXRF; cup-film (Mylar/PP) absorption of Mg Kα; minimum sample mass; relevant standards (ASTM E1621, B215 riffling, ISO 12677, ISO/ASTM 52907); powder-lot homogeneity; anything else.

### Part 3 — broad compositional space with no direct standard

- 3a. ICP-OES/MS with elemental solution calibration as the composition-space-agnostic primary/referee method (+ role certifying in-house solids); ASTM E3061/E1479/E2371, ISO 17025.
- 3b. XRF across arbitrary Al alloys: FP + wide-range influence coefficients (Lachance–Traill, Claisse–Quintin, de Jongh); region-spanning designed standard sets; synthetic fusion-bead standards from pure oxides.
- 3c. In-house RMs: arc-melt/cast buttons of candidate compositions, homogeneity verification, ICP certification; ISO Guide 35 / ISO 17034 concepts scaled to a research lab; pitfalls (macrosegregation, Mg/Zn evaporative loss, oxide inclusions).
- 3d. EPMA/WDS with pure-element standards + φ(ρz) corrections as the standard-flexible microanalysis route; accuracy for Mg in Al.
- 3e. What combinatorial/high-throughput alloy work actually uses (micro-XRF, EPMA grids, LIBS, standards-based EDS) and at what accuracy.
- 3f. Gravimetric blending of elemental powders as calibration blends — sound for XRF given particle-size/mineralogy mismatch vs pre-alloyed powder?
- 3g. Concrete tiered workflow: accuracy anchor, routine screening tool, standards acquisition/fabrication strategy as the space grows, traceability documentation for grants/publications.

## Next steps

1. Wait for response (PaperQA-high turnaround typically ~30–60 min; can be longer).
2. Fetch via `client.get_task(uuid.UUID("068a5ac1-9deb-4174-8e99-cd99aed604e8"))`.
3. Add `edison-artifacts/lit-wdxrf-standards-broad-composition__068a5ac1/{metadata.json, query.md, formatted_answer.md}` and update `edison-artifacts/README.md` index.
4. Write an integrated summary (per-claim verdicts, watch-list, and the no-standard workflow) for Ronnie/Gage ahead of the follow-up with Kevin Rey.

> Note: tasks `a5c9d1c7` (ICP-MS/MS Mg validation) and `0ee4e191` (PXRD/EBSD corroboration) also remain unfetched — all three can be integrated in one pass.
