# Edison query: corroborate/refute the PXRD-for-EBSD-phase-parameters recommendation

> **Status (2026-07-06):** Submitted; awaiting response. Will integrate findings when fetched.
>
> | Task ID | Job | Submitted |
> |---|---|---|
> | `0ee4e191-7525-4449-8a87-529ffdec7469` | `LITERATURE_HIGH` (PaperQA3-high) | 2026-07-06 |

Submitted in response to [PR #95 comment 4898126487 (trigger)](https://github.com/vertical-cloud-lab/byu-vcl/pull/95#issuecomment-4898126487) asking to corroborate or refute the Claude-generated answer in [PR #95 comment 4897995353](https://github.com/vertical-cloud-lab/byu-vcl/pull/95#issuecomment-4897995353), which responded to Ronnie Guymon's question about EBSD noise / low CI on LPBF AlSi10Mg and whether PXRD is the right way to obtain phase parameters for novel Al alloy powders.

## Background

- EBSD on the FEI Apreo (EDAX TEAM) of an LPBF AlSi10Mg cross-section indexed poorly against the stock elemental Al phase (CI ≈ 0.1, substantial noise / "Christmas lights").
- A user-built custom "AlSi10Mg" phase raised CI to ≈ 0.94, but noticeable noise remained.
- The lab is moving toward novel Al alloy powder development and needs a defensible route to phase parameters for EBSD phase files; PXRD (BNSN C330, Dr. Stacey J. Smith) was proposed.

## Claims sent for point-by-point corroboration/refutation

1. Hough-based EBSD indexing needs only space group + lattice parameters + reflector list per phase (not full chemistry).
2. TEAM/OIM CI is a voting-ambiguity metric, not proof the phase model is physically correct (CI ≥ 0.1 usable, > 0.5 ideal).
3. α-Al in AlSi10Mg is FCC a ≈ 4.05 Å, so stock Al *should* index it; CI ≈ 0.1 more plausibly indicates reflector-table / Hough band-count vote splitting or pattern quality — and whether a 0.1 → 0.9 CI jump from a custom phase can be legitimate vs. an artifact.
4. Non-indexed noise largely comes from the sub-µm eutectic Si network (overlapping Al+Si patterns); adding diamond-cubic Si (a ≈ 5.43 Å) as a second phase measurably improves coverage.
5. Deformation layer must be ≲ 50 nm (vibratory polish / broad ion beam; no chemical etch) for Al-alloy EBSD.
6. PXRD + Rietveld (GSAS-II, BGMN/Profex) gives phase ID and lattice parameters to ~10⁻³–10⁻⁴ Å, phase fractions, size/strain — sufficient (with database CIFs from ICDD/ICSD/COD) to build EBSD phase files.
7. Lab PXRD detection limit ~0.5–2 wt%, so nano-Mg₂Si in as-built AlSi10Mg is NOT detected; as-built XRD shows only α-Al + Si; solid-solution lattice-parameter shift is measurable.
8. Texture in printed parts distorts relative intensities but not peak positions / refined lattice parameters; loose powder avoids the problem.
9. CALPHAD (Thermo-Calc / pycalphad) + database CIFs is a sound first step for a candidate phase list.
10. Simultaneous EDS+EBSD chemistry-assisted indexing (EDAX ChI-Scan) is established for discriminating similar phases.
11. Saved raw patterns enable NLPAR denoising and dictionary indexing (kikuchipy, PyEBSDIndex, EMsoft), documented to beat Hough indexing on noisy patterns.
12. TKD gives ~5–10 nm resolution for sub-100-nm features; TEM/SAED / 4D-STEM is the fallback for genuinely unknown structures.

Plus an overall verdict on the proposed workflow (CALPHAD/CIFs → PXRD + Rietveld → EBSD phases from refined CIFs → multi-phase EBSD with saved patterns → NLPAR + dictionary reindexing), errors/omissions, and first-time practical pitfalls.

## Next steps

1. Wait for response (typical PaperQA-high turnaround ~30–60 min).
2. Fetch via `client.get_task(uuid.UUID("0ee4e191-7525-4449-8a87-529ffdec7469"))`.
3. Add `edison-artifacts/lit-pxrd-ebsd-phase-validation__0ee4e191/{metadata.json, query.md, formatted_answer.md}` and update `edison-artifacts/README.md` index.
4. Write a short integrated summary (corroborate / qualify / refute each claim, with literature backing) for Ronnie and Gage ahead of the next session with Paul.
