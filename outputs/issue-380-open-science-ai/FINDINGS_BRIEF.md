# Findings brief: the value of open science in the age of AI (issue #380)

This two-page version of [`README.md`](README.md) gives every number with its source file.

**Videos:** [Part 1](https://www.youtube.com/watch?v=Aakq7PNsFpE) (11:41), [Part 2](https://www.youtube.com/watch?v=uujMO9R1tMc) (4:53) and [Part 3](https://www.youtube.com/watch?v=8P7iqUaVHyE) (3:40). **Playbook:** [`RECOMMENDATIONS.md`](RECOMMENDATIONS.md).

## Twelve numbers

1. **$4.15B vs. $8.8T.** Open-source software would cost $4.15B to rewrite, but firms would need $8.8T to
   replace it themselves. 96% of that value comes from 5% of developers (Hoffmann, Nagle & Zhou 2024;
   [verified](VERIFICATION.md)).
2. **About 800×.** The Protein Data Bank costs $6.9M a year to run and generates $5.5B a year of research
   use. It held 172,801 open structures by 2020, the year AlphaFold 2 won CASP14
   ([PDB data](data/pdb_released_per_year.csv)).
3. **12–27% more patent citations** to NIH-funded research after its 2008 open-access mandate, a causal
   estimate ([Edison](edison/open_science_roi_answer.md)).
4. **87% cheaper.** That is the average saving from open scientific hardware over 119 designs (Pearce
   2020). Open SDL hardware costs $100–2,000, vs. about $10k for general-purpose commercial systems and
   about $1M for specialized ones.
5. **$375B vs. $8.8T.** The value captured by about 30 commercial open-source companies is a sliver of the
   value created. Databricks ($190B), Red Hat ($34B) and MongoDB ($23B) top the list
   ([case files](companies/companies_master.csv)).
6. **7× and 14×.** Median IPO and M&A exit values for VC-backed open-source startups vs. matched closed
   peers ($1.3B vs. $171M; $482M vs. $34M). The source is the LF/Serena/COSSA 2025 report, co-written by
   a VC that backs open source.
7. **16 → 31 closing moves, 11 → 30 opening moves.** Licence changes in the 2010s vs. 2020–26. Forks
   survived every closing move. Valkey, Pekko, OpenVox and LibreOffice now out-commit the originals
   ([fork data](data/fork_vs_original.csv)).
8. **−0.67 (95% CI −1.04 to −0.31).** Companies founded since 2000 became less open over their lives
   than incumbents did. Government, academic and foundation infrastructure almost never closed: 1 of 18
   ([robustness](data/robustness_kinds_by_scope.csv)).
9. **21% → 81% vs. ~40%.** Academia's open-weight share of US AI models (2018–19 → 2024–25), against
   industry's, which stayed near 40%. The largest closed training run is now about 50× the largest open
   one (Epoch AI).
10. **76% vs. 72%.** In 2024 US industry papers were more often open access than academic ones overall,
    but not in the physical sciences (OpenAlex). The pattern is open papers and closed weights.
11. **2.8 vs. 1.6.** AI-for-science model releases average 2.8 on the 0–4 openness scale, against 1.6 for
    frontier-LLM companies. 14 of 17 trained on public data
    ([group I](companies/I/_summary.md)).
12. **$2.24 a kit.** That was the stated profit on the $80 SDL-demo kit sold through GroupGets. The
    institutional lab bought equipment rather than selling any, and closed vendor equipment was its most
    frequent complaint ([digest](gh-mining/commercialization_digest.md)).

## Five patterns

- **Openness creates value; the service, the data and the hardware capture it.** Every sector is
  converging on "open core / mixed" (about 2 on the 0–4 scale in 2026).
- **Hardware is not software.** Open hardware buys cost savings and longevity, not valuations. Clones,
  bills of materials and liability are real costs, and open *standards* (RISC-V, OCP) are where hardware
  openness scales.
- **The physical sciences run on public open infrastructure.** PDB, the Materials Project, LAMMPS, DOE's
  code (93.6% open source) and arXiv are cheap and heavily used. They are also thinly funded: arXiv left
  Cornell and ran a deficit, and OSF stopped new projects in November 2026.
- **The AI labs now talk about science, not openness.** Anthropic's and OpenAI's science language rose
  about 10× into 2026. Both court the national labs with access and credits, and open their *tooling*
  (MCP, skills, SDKs) rather than their weights. Anthropic calls safe open-weight models "a public good"
  and has never advocated a ban.
- **DAL and #318 already fit the winning pattern: open orchestration on closed instruments.** The open
  questions are whether compositions are published or protected (the drafts disagree) and how to open the
  driver and data layer between closed instruments and AI ([audit](dal/dal_openness_audit.md)).

![Openness over time](figures/openness_by_year_sector.png)
