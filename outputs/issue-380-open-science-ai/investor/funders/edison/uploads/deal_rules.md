# Who funded each venture: research rules for a deal pass

Part of issue #380 (see `PROTOCOL.md`). Each pass gets a list of open-source-minded ventures. For each venture, find
**every disclosed outside funding event and who put the money in**, with a source URL for each. This is about the
names of the funders, more than the amounts.

## For each venture, record

- `open_basis`: what is open and under which licence, ≤ 20 words (e.g. "Grafana, AGPLv3 since 2021"). For U1 rows
  the basis is already given; copy it. For U2/U3 rows check it; if the main product turns out not to be open, say
  so here and set `open_ok` to `no`.
- `open_url`: the repository, licence or design-files page that shows it (U2/U3 only; optional for U1).
- `country`, `founded` (year), `status` (`private`, `acquired`, `listed`, `shut_down`, `nonprofit`, `unknown`).
- `funding_found`: `yes` if any outside funding was found; `none_found` if you looked and found none;
  `bootstrapped_stated` if the company says it took no outside money (give that page as a round-less source in
  `notes_url`).
- `rounds`: one object per funding event (below). Include seed and angel rounds, accelerator cheques, grants,
  crowdfunding campaigns and token sales, not only priced VC rounds.

Each round:

| Field | What |
| --- | --- |
| `type` | One of `pre_seed`, `seed`, `series_a`, `series_b`, `series_c`, `series_d`, `series_e`, `series_f_plus`, `growth`, `venture_unspecified`, `angel`, `accelerator`, `corporate_strategic`, `convertible_note`, `grant_philanthropic`, `grant_government`, `prize`, `crowdfunding_reward`, `crowdfunding_equity`, `token_sale`, `debt`, `secondary`, `other` |
| `label` | As the source names it, e.g. "Series B extension", "YC W21", "Kickstarter" |
| `date` | YYYY-MM (or YYYY) of the announcement |
| `amount_usd` | Plain digits in USD, blank if undisclosed. Convert at the rate near the date and say so in `note` |
| `lead` | List of lead investor names (empty if none named) |
| `investors` | List of the other named participants (don't repeat the leads) |
| `source` | URL of a page that names these investors (or the amount). Required |
| `source_kind` | `company`, `investor`, `news`, `filing`, `database` (Crunchbase, Tracxn, PitchBook, CB Insights, Dealroom), `wikipedia`, `other` |
| `note` | ≤ 20 words, optional |

**How to write investor names.** Use the firm's usual name, not a fund vehicle: "Sequoia Capital", "Andreessen
Horowitz", "Index Ventures", "Y Combinator", "Intel Capital", "GV", "M12". Write people as `Full Name (person)`,
e.g. `Nat Friedman (person)`; don't attach the person's firm. A company investing directly, write as the company
("NVIDIA", "Salesforce Ventures" if the source names the venture arm). Leave out "existing investors" and
"others" without names. For crowdfunding, the funder is the platform plus "backers", e.g. `Kickstarter backers`.
For grants, the funder is the agency or foundation ("National Science Foundation (SBIR)", "Chan Zuckerberg
Initiative").

## How to work

- Use WebSearch and WebFetch. Best sources: the company's own announcement, the lead investor's post, the
  investors page of the company's site, SEC filings, TechCrunch, Reuters, Bloomberg, SiliconANGLE, VentureBeat,
  EU-Startups, Sifted, 36Kr for China. Crunchbase is often blocked: use it only if it loads; mark it `database`.
- A recent round's announcement often lists all earlier investors ("joined by existing investors A, B and C");
  record those names in a round of type `venture_unspecified` with that URL if their own rounds can't be found.
- Spend about 3–6 searches or fetches per venture; up to ~10 for large companies with many rounds. Tiny projects
  with no company funding are common: record `none_found` and move on. Absence of disclosure is itself data.
- **Never fill a name or number from memory.** If you remember an investor but can't find a page that says so,
  leave it out and add "memory: <name>" to `notes`.
- Don't skip ventures that failed or are tiny.

## Output

Append each venture as one JSON object per line through the helper, which checks the fields and writes two CSVs
(`deals_<pass>.csv`, one row per round, and `ventures_<pass>.csv`, one row per venture). Run from the
`funders/` folder:

```bash
python3 scripts/append_deals.py <pass> <<'JSON'
{"key": "grafana", "venture": "Grafana Labs", "universe": "U1", "open_basis": "...", "open_url": "", "open_ok": "yes", "country": "US", "founded": "2014", "status": "private", "funding_found": "yes", "rounds": [{"type": "series_a", "label": "Series A", "date": "2019-10", "amount_usd": "24000000", "lead": ["Lightspeed Venture Partners"], "investors": ["Lead Edge Capital"], "source": "https://...", "source_kind": "company", "note": ""}], "notes": "", "notes_url": ""}
JSON
```

Copy `key`, `venture` and `universe` exactly from your input. Send ventures in groups of 3–5 so nothing is lost if
the run stops. The helper refuses a line with a missing source URL or an unknown type; fix it and resend. A venture
sent twice keeps its last version.

When done, reply in ≤ 12 lines: ventures written, how many with no funding found, and any rows you are unsure
about. Don't repeat the data in the reply.
