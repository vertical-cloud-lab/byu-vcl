# Financial details of companies built on popular open-source projects

Part of a pre-registered study (issue #380). The companies in your input were already classified as `core`: their
main paid product is an open-source project they lead, in another form (hosted service, open-core or enterprise
edition, paid licences or support, or hardware). Your job is to find what each company raised, what it was or is
worth, and what happened to it, **with a source URL for every number**.

## Input

A CSV with one row per company: `owner` (GitHub login), `entity` (company name from the classification),
`parent` (current owner if acquired, when known), `country`, `basis`, `status_hint`, `stars` (the org's stars in
the frame) and the top repositories. Rows with `h9_addition=1` are companies that built the project and later
handed it to a foundation (e.g. Anyscale and Ray); research the company named in `entity`, not the foundation.
Several GitHub orgs can belong to one company (e.g. Docker Inc. owns `docker` and `moby`); fill each row anyway.

## For each company, find

| Column | What | Rules |
| --- | --- | --- |
| `status` | One of `listed`, `acquired`, `private`, `shut_down`, `unknown` | `listed` = its own shares trade today. `acquired` = bought by another company (even if it still operates as a subsidiary, or was later taken private by PE: use `acquired` and say so in notes). `shut_down` = ceased operating, wound down, or sold only its assets/IP in distress. `private` = independent and operating |
| `status_date` | YYYY or YYYY-MM of the listing, acquisition or shutdown | |
| `ticker` | Yahoo Finance ticker if listed (e.g. `ESTC`, `MDB`, `9988.HK`) | |
| `acquirer` | Buyer if acquired | |
| `exit_value_usd` | Disclosed acquisition price (equity or enterprise value as reported), in USD | Blank if undisclosed. Don't use "reportedly" figures unless no official figure exists; then say "reported" in notes |
| `exit_source` | URL | |
| `total_funding_usd` | Total disclosed equity funding raised before listing/exit or to date, in USD | From the company's or investors' announcements, or a reputable news report summing them. Exclude debt where you can tell |
| `funding_asof` | YYYY-MM of the latest round counted | |
| `funding_source` | URL | |
| `last_valuation_usd` | Latest disclosed post-money valuation if private; blank otherwise | |
| `valuation_date` | YYYY-MM | |
| `valuation_source` | URL | |
| `peak_value_usd` | Highest value ever disclosed: any private post-money valuation, the market cap at the close of its first trading day, or exit value | |
| `peak_value_date` | YYYY-MM | |
| `peak_source` | URL | |
| `ever_1b` | `yes` if any disclosed value reached USD 1B (private mark, first-day market cap, or exit price); `no` if the company's disclosed values are all below 1B or it never disclosed one and is clearly small; `unknown` otherwise | |
| `legal_name` | The US legal entity name if the company is (or was) US-incorporated, e.g. "Grafana Labs, Inc." or "Raintank, Inc." (the name it would use on an SEC Form D). Several names separated by `|` | |
| `notes` | ≤ 25 words: anything an investor should know (down round, relicensing, acqui-hire, crypto token, numbers that conflict between sources) | |

## How to work

- Use WebSearch and WebFetch. Good sources: company press releases and blogs, investor (VC) announcements, SEC
  filings (EDGAR), Reuters, TechCrunch, Bloomberg, The Information (summaries), Wikipedia only for its cited
  sources. Crunchbase pages are often blocked; don't rely on them.
- **Every number needs a URL that states it.** If you know a figure from memory but can't find a page stating it,
  leave the number blank and put "memory: ~$XM" in notes.
- Spend about 3–5 searches or fetches per company at most. Small companies with no disclosed rounds are common:
  record `status` and leave the numbers blank. Absence of disclosure is itself data.
- Convert non-USD amounts at the rate near the announcement date and say so in notes.
- Don't skip companies that failed or that are tiny. Those rows matter most.

## Output

Write a CSV with a header to the path in your task, one row per input company, in input order, with columns:

`owner,entity,status,status_date,ticker,acquirer,exit_value_usd,exit_source,total_funding_usd,funding_asof,funding_source,last_valuation_usd,valuation_date,valuation_source,peak_value_usd,peak_value_date,peak_source,ever_1b,legal_name,notes`

Numbers as plain digits in USD (e.g. 6400000000), no "$", "B" or commas. Quote fields containing commas. Save
progress after every ~10 companies. When done, reply with the row count, counts by status, and any rows you are
unsure about.
