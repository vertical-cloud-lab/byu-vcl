# Who owns popular open source, and what do the owners earn? (issue #380, round 2, part 2)

Sterling asked for "a lot more manual digging and data extraction (e.g., large-scale GitHub searches of repositories
and their parent organizations, then looking into the financial details of those parent organizations)". This
folder does that. Read [`FINDINGS.md`](FINDINGS.md) first; the hypotheses were fixed beforehand in
[`PREREGISTRATION.md`](PREREGISTRATION.md) (committed in `608d7c2` before any data was fetched).

## Pipeline

Run from this folder with the Python 3.12 venv described in [`../README.md`](../README.md), plus `beautifulsoup4` and
`lxml` for the news leads, page helper and source checks.

| Step | Script | Output |
| --- | --- | --- |
| 1. GitHub search: the 2,000 most-starred repos; the top 100 in each of 22 science topics; every owner's profile | `scripts/harvest_github.py` | `data/repos_frame_a.csv`, `data/repos_frame_b.csv`, `data/owners_github.csv`, `data/harvest_log.json` |
| 2. Wikidata: owners by GitHub username (P2037), repos by source-code URL (P1324) and their developers, and each entity's types, listings, tickers, owners and parents | `scripts/wikidata_links.py --reuse` | `data/wikidata_*.csv` |
| 3. Classify every organization (rules in [`classify_rules.md`](classify_rules.md)); merge; apply reviewed corrections | `scripts/merge_classes.py` | `data/classify_passes/`, `data/owner_class_overrides.csv`, `data/owner_classes.csv` |
| 4. FUNDING.yml links of every repo and GitHub Sponsors of every owner | `scripts/github_funding_links.py` | `data/repo_funding_links.csv`, `data/owner_sponsors.csv` |
| 5. Core companies' funding, valuations, exits and shutdowns, each with a source URL (rules in [`finance_rules.md`](finance_rules.md)). First pass: eight research agents with web search, ~49 companies each, writing through `scripts/append_finance_rows.py` | by hand (agents) | `data/finance_passes/input_*.csv`, `output_*.csv` |
| 6. The search budget ran out halfway, so for the 276 thin rows: Hacker News and TechCrunch headlines and page excerpts, then a second pass of eight agents working from them (helper: `scripts/page_text.py`), then hand corrections | `scripts/news_leads.py data/finance_passes/second_pass_targets.csv`, `scripts/second_pass_chunks.py 8` | `leads.jsonl`, `leads_*.md`, `second_*.csv`, `third_1.csv` |
| 7. SEC Form D: capital raised by US private companies, from filings (`--delta <csv>` adds names found later) | `scripts/sec_form_d.py` | `data/form_d_*.csv` |
| 8. Yahoo Finance: listed owners, parents and listed core companies | `scripts/listed_financials.py` | `data/listed_financials.csv` |
| 9. Merge the passes (second replaces first, hand corrections last), Form D and Yahoo | `scripts/build_core_financials.py` | `data/core_financials.csv` |
| 10. Check that every figure appears on the page it cites | `scripts/check_sources.py` | `data/source_checks.csv` |
| 11. Form 990s (ProPublica) for US nonprofits; Open Collective for every owner | `scripts/nonprofit_finances.py 990 oc` | `data/form990_*.csv`, `data/opencollective.csv` |
| 12. H7–H11, Edison audit agreement, and figures | `scripts/owners_analysis.py`, `scripts/owners_figures.py` | `data/h*_*.csv`, `data/class_audit_*.csv`, `data/results_summary.json`, `figures/` |

`data/cpi_u_bls.json` is the BLS CPI-U series (CUUR0000SA0) saved from the public API on 2026-11-25; October 2025
is missing from it (the federal shutdown), so 2025's average uses eleven months.

GitHub stars, Yahoo prices and Open Collective balances change daily; the harvest is dated 2026-11-25, the Yahoo
snapshot 2026-11-26. News pages change too: `leads.jsonl` keeps the excerpts as fetched on 2026-11-26.
