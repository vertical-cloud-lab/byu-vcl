# Programs that fund open source and open science: research rules

Part of issue #380 (see `PROTOCOL.md`). Much of the money for open source and open science goes to projects,
maintainers and nonprofits through programs rather than to companies through rounds. A program pass lists those
programs and the investors who state an open-source thesis. Every row needs a URL that states what it claims.

## One JSON object per program (or per investor thesis)

| Field | What |
| --- | --- |
| `funder` | The organisation or person who provides the money, e.g. "Chan Zuckerberg Initiative", "Alfred P. Sloan Foundation", "Sovereign Tech Agency", "OSS Capital", "Nat Friedman (person)" |
| `funder_type` | One of `foundation`, `philanthropist`, `donor_advised_or_fiscal_host`, `corporate_program`, `government_grant`, `public_investor`, `intergovernmental`, `crypto_foundation`, `dao`, `platform`, `accelerator`, `fellowship`, `venture_fund`, `angel`, `other` |
| `program` | Program name, or "open-source investment thesis" for an investor |
| `years` | e.g. "2019-2024", "2022-" |
| `committed_usd` | Total committed or disbursed in USD, plain digits, blank if unknown. Say which (committed or disbursed) in `amount_note` |
| `amount_note` | ≤ 20 words: committed vs disbursed, currency conversion, period |
| `focus` | Short list from: `science_software`, `open_hardware`, `open_science`, `open_data`, `digital_infrastructure`, `security`, `ai`, `privacy_internet_freedom`, `education`, `web3`, `general_oss`, `other` |
| `recipients` | `projects`, `individuals`, `nonprofits`, `companies`, `universities`, `mixed` |
| `funds_companies` | `yes` (for-profit companies can receive it), `no`, `sometimes`, `unknown` |
| `examples` | List of up to 8 named recipients (projects, people, ventures) |
| `access` | How money is obtained: `open_call`, `invitation`, `rolling`, `investment`, `matching`, `unknown` |
| `status` | `active`, `closed`, `paused`, `unknown` (as of the source's date) |
| `source` | URL that states the program and, where given, the amount. Required |
| `source2` | A second URL (optional) |
| `quote` | For investors: ≤ 30 words quoted from the firm's own page or post stating its open-source thesis. Otherwise optional |
| `notes` | ≤ 30 words |

## How to work

- Use WebSearch and WebFetch. Prefer the funder's own pages, annual reports, grant databases (e.g. CZI grants
  database, Sloan grants database, NSF award search, Sovereign Tech Agency investments page, NLnet project list),
  and reputable reporting.
- **Never fill a number or name from memory.** If you can't find a page that states it, leave it blank and say
  "memory: ..." in `notes`.
- Record programs that ended or failed too (e.g. a fund that closed), with their dates.
- Aim for breadth first: one row per program, then add amounts where the source gives them.

Append through the helper, 3–6 rows at a time, from the `funders/` folder:

```bash
python3 scripts/append_programs.py <pass> <<'JSON'
{"funder": "...", "funder_type": "foundation", "program": "...", "years": "...", "committed_usd": "", "amount_note": "", "focus": ["science_software"], "recipients": "projects", "funds_companies": "no", "examples": ["..."], "access": "open_call", "status": "active", "source": "https://...", "source2": "", "quote": "", "notes": ""}
JSON
```

When done, reply in ≤ 12 lines: rows written and anything you are unsure about. Don't repeat the data.
