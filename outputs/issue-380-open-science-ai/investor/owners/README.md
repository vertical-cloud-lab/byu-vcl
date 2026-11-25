# Who owns popular open source, and what do the owners earn? (issue #380, round 2, part 2)

Sterling asked for "a lot more manual digging and data extraction (e.g., large-scale GitHub searches of repositories
and their parent organizations, then looking into the financial details of those parent organizations)". This
folder does that. Read [`FINDINGS.md`](FINDINGS.md) first; the hypotheses were fixed beforehand in
[`PREREGISTRATION.md`](PREREGISTRATION.md) (committed in `608d7c2` before any data was fetched).

## Pipeline

Run from this folder with the Python 3.12 venv described in [`../README.md`](../README.md).

| Step | Script | Output |
| --- | --- | --- |
| 1. GitHub search: the 2,000 most-starred repos; the top 100 in each of 22 science topics; every owner's profile | `scripts/harvest_github.py` | `data/repos_frame_a.csv`, `data/repos_frame_b.csv`, `data/owners_github.csv`, `data/harvest_log.json` |
| 2. Wikidata: owners by GitHub username (P2037), repos by source-code URL (P1324) and their developers, and each entity's types, listings, tickers, owners and parents | `scripts/wikidata_links.py --reuse` | `data/wikidata_*.csv` |
| 3. Classify every organization (rules in [`classify_rules.md`](classify_rules.md)); merge; apply reviewed corrections | `scripts/merge_classes.py` | `data/classify_passes/`, `data/owner_class_overrides.csv`, `data/owner_classes.csv` |
| 4. FUNDING.yml links of every repo and GitHub Sponsors of every owner | `scripts/github_funding_links.py` | `data/repo_funding_links.csv`, `data/owner_sponsors.csv` |
| 5. Core companies' funding, valuations, exits and shutdowns, each with a source URL (rules in [`finance_rules.md`](finance_rules.md)) | by hand, in four passes | `data/finance_passes/`, `data/core_financials.csv` |
| 6. SEC Form D: capital raised by US private companies, from filings | `scripts/sec_form_d.py` | `data/form_d_*.csv` |
| 7. Yahoo Finance: listed owners and parents | `scripts/listed_financials.py` | `data/listed_financials.csv` |
| 8. Form 990s (ProPublica) for US nonprofits; Open Collective for every owner | `scripts/nonprofit_finances.py 990 oc` | `data/form990_*.csv`, `data/opencollective.csv` |
| 9. H7–H11 and figures | `scripts/owners_analysis.py`, `scripts/owners_figures.py` | `data/h*_*.csv`, `data/results_summary.json`, `figures/` |

`data/cpi_u_bls.json` is the BLS CPI-U series (CUUR0000SA0) saved from the public API on 2026-11-25; October 2025
is missing from it (the federal shutdown), so 2025's average uses eleven months.

GitHub stars, Yahoo prices and Open Collective balances change daily; the harvest is dated 2026-11-25.
