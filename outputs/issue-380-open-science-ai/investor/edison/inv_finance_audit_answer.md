# Edison job-futurehouse-data-analysis-crow-high: inv_finance_audit

Task `a78745a7-1317-4f88-8b7c-b85123ddd5b2` · status success · files attached: finance_audit_sample.csv, finance_rules.md

**Query.** You are independently checking a financial-research step in a pre-registered study of companies whose main paid product is a popular open-source project they lead. finance_audit_sample.csv lists 40 such companies drawn at random (company name, GitHub organization accounts, country, website and top repositories). finance_rules.md defines the columns and the sourcing rules. For every company, research from public sources (company and investor announcements, SEC filings, reputable news) and record: status (listed, acquired, private, shut_down or unknown) with its date; acquirer; disclosed acquisition price; total disclosed equity funding with the date of the latest round counted; latest disclosed post-money valuation; the highest value ever disclosed (private valuation, first-day market cap or exit price); ever_1b (yes, no or unknown, as defined in the rules); and a source URL that states each number. Leave a number blank rather than estimate it; absence of disclosure is a valid finding, and many of these companies are small. Output a CSV named finance_audit.csv with columns github_orgs, entity, status, status_date, acquirer, exit_value_usd, exit_source, total_funding_usd, funding_asof, funding_source, last_valuation_usd, valuation_date, valuation_source, peak_value_usd, peak_value_date, peak_source, ever_1b, notes (at most 25 words), one row per input company in input order, numbers as plain USD digits. Then report counts by status and ever_1b, and the companies where public sources conflict.

---

I completed all **40 companies**, preserving input order and labels, with a public-source cutoff of **26 November 2026**.

- [finance_audit.csv](/workspace/finance_audit.csv) — exact requested 18-column schema.
- [Source discrepancies](/workspace/finance_audit_conflicts.csv) — competing figures, URLs and my resolution.
- [Evidence and methods](/workspace/finance_audit_evidence.json) — company-level evidence, funding arithmetic, limitations and validation results.

### Counts

| Status | Companies |
|---|---:|
| listed | 0 |
| acquired | 3 |
| private | 35 |
| shut_down | 2 |
| unknown | 0 |

| ever_1b | Companies |
|---|---:|
| yes | 2 |
| no | 32 |
| unknown | 6 |

The two `ever_1b=yes` companies are **DeepSeek** and **Tiger Data**. The six `unknown` companies are Qdrant, Coder Technologies, OtterMind, TileDB, Strapi and Rocket.Chat.

The acquired businesses are **Kilo Code, Anki/Ankitects and Continue**; no acquisition price was verified. **OpenBB and Textualize** announced wind-downs. Anki’s date identifies its announced paid operating-business transition, not a verified legal closing date.

### Conflicting public sources

I documented **18 discrepancies across 17 companies**:

- **Funding amounts or coverage:** Anomaly, Vectify AI, Kaleidos/Penpot, CrewAI, Continue, Coder Technologies, HeroUI, Chatwoot, TileDB and Portainer.
- **Financing scope or rounding:** Strapi, Mermaid Chart, Tiger Data and Rocket.Chat.
- **Valuation:** DeepSeek; also CrewAI and Coder Technologies.
- **Timing or terminology:** Textualize’s wind-down date and PandasAI’s seed versus pre-seed label.

These are not all direct contradictions: some reflect debt inclusion, incomplete histories, rounding, announcement versus database dates, or estimated versus disclosed valuations. The discrepancy CSV distinguishes them and records which evidence I accepted.

**Limitations:** Blank amounts mean undisclosed or unverified—not zero. Some funding totals are disclosed minimums because additional financing was confirmed without a verifiable amount. `ever_1b=no` follows the rules’ small-company criterion; it does not prove that no undisclosed billion-dollar valuation existed.

**Discretionary decisions**
- I preferred company and participating-investor disclosures over database totals, excluded debt and sponsorship, and avoided adding generic accelerator cheques.
- I used pipe-separated source URLs where a funding total required summing disclosed components; the evidence file shows the arithmetic.
- I left Tiger Data’s exact valuation blank because its official disclosure says **“over $1 billion”**; that still establishes `ever_1b=yes`.
- I left Bruno’s funding month blank because the founder supplied only an approximate relative date, and converted Vectify’s reported GBP round using a contemporaneous European Central Bank reference rate.
