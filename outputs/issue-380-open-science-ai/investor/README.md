# Issue #380, round 2: the investor's view

The first round (branch `claude/issue-380-20261123-2145`) asked what open science and open source are worth. This
round asks what someone paying for them gets back, as a less-biased counterweight, with Edison as an independent
check. Read [`INVESTOR_MEMO.md`](INVESTOR_MEMO.md) first.

## Reproduce

Run from this folder with a Python 3.12 venv (`edison-client` does not import on 3.14):

```bash
python3.12 -m venv /tmp/venv && /tmp/venv/bin/pip install edison-client yfinance pandas matplotlib numpy scipy requests
/tmp/venv/bin/python scripts/edison_submit.py               # submits edison/queries.json jobs not yet in _task_ids.json
/tmp/venv/bin/python scripts/edison_fetch.py --wait          # saves answers, references and full trajectories
/tmp/venv/bin/python scripts/edison_files.py inv_redteam_round1 inv_redteam_round2 inv_redteam_round3   # files the analysis jobs created
/tmp/venv/bin/python scripts/fetch_prices.py                 # Yahoo prices and fundamentals snapshot
/tmp/venv/bin/python scripts/build_cohort.py                 # verified deal terms -> data/cohort_listings.csv
/tmp/venv/bin/python scripts/h1_listing_returns.py           # H1 returns, summaries, sensitivities
/tmp/venv/bin/python scripts/h1_vintage.py                   # listing-year controls and public-market equivalents
/tmp/venv/bin/python scripts/h1_permutation.py               # permutation tests; SolarWinds valuation alternatives
/tmp/venv/bin/python scripts/h1_figure.py                    # figures/h1_listing_returns.png
/tmp/venv/bin/python scripts/value_capture_casebook.py       # H2 on the first round's case files
/tmp/venv/bin/python scripts/fundamentals_summary.py         # survivors' margins and multiples, cohorts as in H1
/tmp/venv/bin/python scripts/stackoverflow_monthly.py        # Stack Exchange API, monthly new questions 2018-26
/tmp/venv/bin/python scripts/shocks_figure.py                # figures/two_shocks.png (uses data/us_science_funding.csv)
```

`fetch_prices.py` also needs Domo's renamed ticker (HUCK) and the four sensitivity tickers, which are saved to
`data/prices_extra_*.csv`. Yahoo prices change daily, so a re-run after 2026-11-24 moves the still-listed companies.

## Contents

| Path | What it is |
| --- | --- |
| `INVESTOR_MEMO.md` | The memo: bottom line, pre-registered results, ten ranked concerns, the case for openness, an investability checklist, DAL and the SDL kit |
| `PREREGISTRATION.md` | Hypotheses H1–H6 and their tests, committed before any new data |
| `BIAS_AUDIT.md` | Where the first round's framing leaned toward openness |
| `edison/` | Every Edison job (nine neutral questions in round 1, a red team of the first round, and two reviews of this memo): `queries.json`, `_task_ids.json`, `<key>_answer.md`, `<key>_references.md`, `<key>_task.json` (full trajectory), and `<key>_files/` for analysis jobs. `uploads/` holds the files the red team received |
| `evidence/` | Dated, sourced 2025–26 evidence gathered for the memo |
| `data/` | Verified listing terms, prices, fundamentals and every results table |
| `scripts/`, `figures/` | Code and charts |
| `owners/` | Part 2: who owns the 2,000 most-starred repositories and the top science-topic ones, and what the 387 companies that sell an open project raised, were worth and became (H7–H11). Start with [`owners/FINDINGS.md`](owners/FINDINGS.md); its [`README.md`](owners/README.md) has the pipeline |
| `funders/` | Part 3: who has funded open-source-minded ventures. Every disclosed round and named funder for 1,042 ventures (the 387 companies from part 2, open hardware and science, notable COSS and open-weight AI, young open-source startups), program-level funders (foundations, governments, corporate funds, crypto, crowdfunding), checks against cited pages, investors' portfolio pages and a blind Edison audit. Start with [`funders/FUNDERS.md`](funders/FUNDERS.md); every funder is in [`funders/FUNDER_LIST.md`](funders/FUNDER_LIST.md) |
