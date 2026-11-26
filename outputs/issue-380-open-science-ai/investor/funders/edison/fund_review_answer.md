# Edison job-futurehouse-data-analysis-crow-high: fund_review

Task `b3464312-5ff5-488f-8407-8981dec34e43` · status success · files attached: FUNDERS.md, investors.csv, investor_links.csv, deals.csv, ventures.csv, programs.csv, PROTOCOL.md, source_checks_deals.csv, edison_audit_comparison.csv

**Query.** You are reviewing, as an independent and skeptical analyst, a compiled list of who has funded open-source-minded ventures (commercial open-source software, open-weight AI, open hardware and open-science companies). FUNDERS.md is the write-up; investors.csv, investor_links.csv, deals.csv, ventures.csv and programs.csv are the data it is built from; PROTOCOL.md fixed the scope before data collection; source_checks_deals.csv checks each investor name against its cited page; edison_audit_comparison.csv compares this list with an independent audit of 40 random ventures. Please check: (1) whether each claim in FUNDERS.md's bottom line and section notes is supported by the data files (recompute the key counts and rankings); (2) errors in the data that would change a conclusion (wrong investor types, duplicate funders under two names, ventures that are not open-source-minded, implausible rounds), with examples; (3) whether the write-up overstates or understates anything, including completeness and what the list implies for someone raising money for an open physical-science venture; (4) important funders or categories of funders of open-source or open-science ventures that are missing. Write review.md with numbered findings, each with evidence (file, rows, recomputed numbers) and a suggested correction, ranked by importance, and say which claims you could verify and which you could not.

---

I wrote [review.md](/workspace/review.md) with **11 numbered findings ranked by importance**, including file/row evidence, recomputed numbers, suggested corrections, and claims I could and could not verify.

**Overall:** most published rankings reproduce exactly, but I would not endorse “accurate” or “every count is a lower bound.” I found acquisitions counted as funding, duplicate ventures and funder aliases, nonprofit/non-open inclusions, and stale audit comparisons. The broad long-tail conclusion survives my conservative checks.

The [audit bundle](/workspace/review_audit_bundle.zip) includes the review, unchanged inputs, executable recomputation script, verification ledger, bibliography, and primary-source evidence.

Analytical decisions:
- I kept U1–U3 and U1–U4 denominators separate.
- I distinguished arithmetic agreement from external investment verification.
- I reported corrections as separate sensitivity checks, not a purported fully cleaned database.
