# Independent investment review: reproducibility package

Start with `INDEPENDENT_REVIEW.md` for the committee review. The full numeric claim audit is `numeric_claim_audit.csv`; exact quote edits are in `framing_edits.csv`; company classification checks are in `cohort_rule_audit.csv`.

## Reproduce

Requirements: Python 3, numpy, pandas, scipy, statsmodels.

```
python reproduce_h1.py --output rerun
python reproduce_supplementary_h2.py
```

The H1 script uses the supplied raw listing offers/deal terms and cached observations. It distinguishes snapshot reconstruction from independently retrieved timestamped November 24 quotes and a November 23 complete-daily-bar sensitivity. The independent timestamped reconstruction does not take endpoint prices or benchmark ratios from the supplied computed returns. All 16 scenario summaries and their fixed-seed bootstrap intervals have been executed and checked against published values.

`h1_independent_timestamped_company.csv` has the raw-only independent memo-date analysis; `h1_replication_company.csv` reproduces the original cohort; `h1_sensitivity_results.csv` contains all scenarios and interval definitions. `h1_all_scenarios_company.csv` provides company-level inspection. `market_observations.csv` and `timestamped_quotes.csv` preserve price inputs. Historical corporate actions use explicitly documented liquidation choices; these are not a universal reinvested portfolio return.

`inputs/` preserves the supplied nine files. `input_sha256.json` records their hashes. `source_cache/` contains retrieved vendor responses, linked original first-round evidence and relevant original-source text. The source cache is evidence, not independently certified truth. Source statuses and limits are stated in the review and ledger.

The merged `references.bib` contains full citations saved for sources used during the review; the report lists the sources it cites. Numbers repeated only in AI-authored case descriptions are distinguished from primary observations and independently recomputed values.

## Important cautions

This is not an exhaustive newly certified IPO universe or a causal estimate of licence effects. Public listing returns do not establish pre-IPO venture returns. All legal points require transaction-specific counsel. Completed first-day-close sensitivity has adverse unadjusted bootstrap evidence but is not robust across inference methods or year adjustment. Missing or unverified evidence is not automatically false.
