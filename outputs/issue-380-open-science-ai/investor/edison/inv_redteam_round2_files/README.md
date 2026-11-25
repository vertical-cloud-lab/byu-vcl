# Files from Edison's review of the investor memo (`inv_redteam_round2`)

Everything the trajectory created, downloaded with `scripts/edison_files.py`. The trajectory's files arrived as one
zipped collection, unpacked here as `0457a348-0f27-488e-a186-97fa34f5b3a7_trajectory_files.zip.d/`. Start with
`independent_review/INDEPENDENT_REVIEW.md`. Then see `framing_edits.csv` (23 suggested wording changes),
`numeric_claim_audit.csv` (93 checked claims), `h1_sensitivity_results.csv` and `reproduce_h1.py`.
`source_cache/` holds the sources it fetched.

Two things were left out:

- **`independent_investment_review.zip`** (5.2 MB), which repackages the same `independent_review/` files. Its file
  list with checksums is in `independent_investment_review_manifest.sha256`.
- **`source_cache/patent_lottery.pdf`**, a copy of Farre-Mensa, Hegde & Ljungqvist's paper (sha256 `950203fd3ef493867f09721346a345dddbcc96ad7d0843704da3b7a1445b3108`). It is
  published as doi:10.1111/jofi.12867 and is not redistributed here.
