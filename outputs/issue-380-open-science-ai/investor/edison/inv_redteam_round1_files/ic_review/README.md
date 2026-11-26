# Reproducibility bundle: open science investment committee review

## Contents and limits

The report is my skeptical review of the six supplied Claude-generated research attachments. It recomputes their exports; it is not an independent audit of all financing or source records. The snapshot convention is 2026-11-23, and the assessment date is 2026-11-25. All amounts are nominal USD. The dataset is a selected casebook, not a representative sample.

## Reproduce

From this extracted directory, use Python 3 and install `requirements.txt`, then run:

```bash
python analysis.py
MPLBACKEND=Agg python make_figure.py
```

`analysis.py` writes CSVs into this directory and loads only the input CSVs from `inputs/`. The bootstrap uses seed 3802026 and 12,000 replicates. `make_figure.py` reads those outputs and writes `figures/investment_evidence.png` and `.pdf`.

The report PDF is built from `latex/investment_committee_review.tex`, the filled-in fetched report template, with `tectonic`. Its style file is unchanged. Body tables have compatibility edits for Pandoc-generated LaTeX. The build succeeds with the template's bundled BibTeX engine diagnostics; all nine bibliography entries and all citations were checked in the rendered PDF. No input values were changed to make results look favorable.

## Tables

- `companies_analysis.csv`: all 179 source rows plus eligibility, admissible-value, multiple, event flags, parsed-value dates and analysis fields. `latest_value_usd` is the original field; `value_usd` is the admissible valuation subset. Do not use `latest_value_usd` indiscriminately.
- `openness_summary.csv`: current and initial score-level summaries for all rows, primary commercial and expanded commercial samples. Values are raw USD, rates are fractions. Missing score has its own row. Primary commercial has no current level4 row because no entity qualifies.
- `sector_summary.csv`: primary commercial sector distributions and historical event prevalence, including confidence intervals.
- `sector_openness_summary.csv`: full sector-by-score financial distributions and event-rate intervals, for current and initial scores.
- `contrasts_sensitivity.csv`: predeclared-style exploratory contrasts, score2+ vs0-1 and score3+ vs0-2; medians/ratios and bootstrap intervals, Cliff delta/Mann-Whitney tests for financial outcomes; event rate differences with Newcombe-Wilson intervals and Fisher tests. Includes within-sector, mark-type, recency, confidence and terminal-loss sensitivities. Single-case financial CIs are blank, not falsely precise.
- `regression_results.csv`: exploratory OLS and linear-probability models, HC3 uncertainty. Log10 financial outcomes are converted to percent effects per one score point. No causal or population inference is warranted. Rare-failure models are only technical sensitivities.
- `missingness_bounds.csv`: observation fractions and an intentionally extreme all-missing-values-failed scenario, not an estimated failure correction.
- `omitted_failure_sensitivity.csv`: count of omitted failures required to reach hypothetical10/25/50% failure rates, assuming no omitted successes. These are scenarios, not estimates of missing firms.
- `concentration.csv`: concentration of aggregate reported values, not comparable equity proceeds.
- `events_audit.csv`: source events joined to organizational eligibility and openness.
- `closing_event_audit.csv`: dated closing rows compared with the first recorded acquisition/take-private year. Same-calendar-year ordering is not known. Missing year is not counted as after acquisition.
- `audit_metadata.json`: inclusion counts, input SHA-256 hashes, non-valuation exclusions, seed and snapshot convention.
- `package_versions.json` and `requirements.txt`: numerical environment used.

Event flags count a unit once per kind and allow overlap; they are recorded historical prevalence, not annual rates, success rates or a survival estimate. No missing funding is imputed as zero. Zero funding does not create an infinite multiple. Only the explicitly labeled bankruptcy zero-recovery scenario assigns a zero multiple. Levels0-4 are not treated as equally spaced except in the clearly labeled trend-regression sensitivity.

## Sources

`inputs/` preserves the exact six attachments. `sources/` preserves the primary venture-study PDF and two primary-source page extracts; `web_search_evidence.json` preserves the searches used to locate primary works. `references.bib` contains the complete merged entries. External sources are separately distinguished from claims that can only be checked against the supplied documents. The primary-study PDF in `sources/` is unmodified.

Execution95ddb5a0-c3c5-438f-8083-cacf439a71f0. Project URL metadata was not available; no project link has been invented.
