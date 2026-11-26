# Edison job-futurehouse-data-analysis-crow-high: fund_deal_audit

Task `69862258-b7d3-4950-962d-7f74445431be` · status success · files attached: funders_audit_sample.csv, deal_rules.md

**Query.** You are independently checking a research step in a pre-registered study of who funds open-source-minded ventures (companies whose main product is open-source software, open-weight AI models, open hardware or open-science tooling). funders_audit_sample.csv lists 40 ventures drawn at random with a fixed seed from the study's 640 (key, name, universe, category, website, GitHub organizations). deal_rules.md describes what the study records. For each venture, find every disclosed outside funding event (pre-seed, seed, angel, venture rounds, accelerators, corporate or strategic investment, growth rounds, grants, crowdfunding, token sales) and who put money in, using web sources: company announcements, investor posts, regulatory filings, reputable news. Do not rely on memory: every round needs a URL that names the investors or states the amount. Write funders_audit.csv with one row per funding event and these columns: key, venture, type (one of the types in deal_rules.md), label, date (YYYY-MM), amount_usd (plain digits), lead (lead investors separated by ' | '), investors (other named investors separated by ' | '), source_url, confidence (high, medium or low). For a venture with no disclosed outside funding after a reasonable search, write one row with type none_found. Write investor names as the firms' usual names (not fund vehicles), and people as 'Full Name (person)'. Also write funders_audit_notes.md with one line per venture on what you checked and anything uncertain, and say in your answer how many ventures you could not research fully.

---

I researched all **40 ventures** and produced:
- [funders_audit.csv](/workspace/funders_audit.csv) — 204 rows, including 2 `none_found` rows.
- [funders_audit_notes.md](/workspace/funders_audit_notes.md) — one line per venture with search scope and uncertainties.

**20 venture histories remain incomplete**, explicitly flagged in the notes. Low-confidence records are not confirmed cash receipts; `none_found` does not prove no outside funding.

Analytical decisions:
- I excluded unverified pledges, noncash incubation and a cancelled unpaid award, and consolidated apparent duplicate announcements.
- I distinguished secondary sales, credit commitments and ongoing donations from new equity funding.
- I documented near-date currency conversions and left unsupported dates or amounts blank.
