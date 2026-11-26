# Files from Edison's red-team analysis (`inv_redteam_round1`)

Everything the trajectory created, downloaded with `scripts/edison_files.py` (provenance API, `list_files`), mirroring
its `/workspace` paths. Start with `ic_review/investment_committee_review.md` (or the PDF), then `ic_review/analysis.py`
and the CSVs it wrote. `notebooks/*.ipynb` is the full notebook and `memory/` the agent's working memory.

Two things were left out to keep the repository small:

- **The Linux Foundation / Serena / COSSA report PDF** that Edison downloaded (`ic_review/sources/LF_COSS_2025.pdf`,
  17.7 MB, sha256 `2e4d12209c5ee4f4dedf8fbcce96a8f21aad1ac39207a7d7cd378b3cffea2fad`). It is public at
  <https://www.linuxfoundation.org/hubfs/Research%20Reports/lfr_serena_capital_report_082225b.pdf>.
- **The reproducibility zip** (`open_science_investment_review_reproducibility.zip`, 16.6 MB). It repackages the same
  `ic_review/` files plus that PDF. Its file list with checksums is in `reproducibility_bundle_manifest.sha256`.
