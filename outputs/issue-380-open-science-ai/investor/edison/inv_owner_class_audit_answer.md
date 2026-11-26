# Edison job-futurehouse-data-analysis-crow-high: inv_owner_class_audit

Task `a881386a-ac1a-461a-a6d1-493965779dd3` · status success · files attached: audit_sample.csv, classify_rules.md

**Query.** You are auditing a classification step in a pre-registered study of who owns popular open-source software. audit_sample.csv lists 120 GitHub organization accounts (60 drawn at random from the 300 with the most stars, 60 from the rest), with each account's name, website, e-mail domain, location, creation year, description and top repositories. classify_rules.md gives the classes (core, complement, nonprofit, academic, government, community, unknown) and the tie-breakers. Classify every account independently by those rules, checking the organization's website or repository where you are unsure. Do not use any financial outcome (funding, valuation, revenue, acquisition price, shutdown) to decide a class. Output a CSV named owner_class_audit.csv with columns owner, cls, entity, parent, basis (at most 15 words), judgment (1 if a judgment call), source_url, one row per input account in input order, and report the counts by class and the accounts you found hardest to classify, with reasons.

---

I wrote **[owner_class_audit.csv](/workspace/owner_class_audit.csv)** with all **120 accounts**, in input order, using exactly the seven requested columns. I checked a primary website or repository for every account and did not use financial outcomes to choose classes.

| Class | Count |
|---|---:|
| core | 36 |
| complement | 19 |
| nonprofit | 9 |
| academic | 10 |
| government | 1 |
| community | 45 |
| unknown | 0 |
| **Total** | **120** |

I marked **36 judgment calls**. [Review notes](/workspace/owner_class_audit_notes.md) explain every flagged account, with source links and limitations. These are unweighted sample counts, not population estimates.

### Hardest classifications

- **`Spooky-Manufacturing` → core:** Its manufacturer description and computer designs suggest a product-focused hardware developer, but legal-entity and paid-offering evidence remain incomplete.
- **`OpenMontageInc` → core:** The repository links to its Studio product; treating it as a commercial project company requires inference because a paid tier was not established.
- **`labmlai` → community:** The checked pages establish open tutorials and self-hosted tools, but not an owning company or paid offering.
- **`micro` → core:** The hosted assistant and open framework suggest one product ecosystem, but their precise commercial relationship is insufficiently explicit.
- **`K-Dense-AI` → complement:** I distinguish its free skills/local assistant from its paid hosted agents. Whether these constitute variants of the same project is genuinely debatable.
- **`Textualize` → complement:** Its current homepage presents separate writing applications alongside the framework; I did not establish a current paid framework edition.
- **`php` → community:** A supporting foundation does not, by itself, establish ownership or control of the PHP organization account.
- **`spacetelescope` → academic:** I apply the research-institute rule to the AURA-operated institute; operating NASA missions does not make it a government agency.
- **`mixOmics-org` → academic:** I interpret the stated University of Melbourne lab leadership as an academic account, despite worldwide contributors.

### Analytical decisions

- I distinguished ownership and stewardship from contributor employment, sponsorship, and fiscal hosting.
- I applied the maintainer-company tie-breaker and flagged borderline product relationships rather than treating every project-branded account as community-owned.
- Where ownership was identifiable but the class remained uncertain, I chose the more likely class and set `judgment=1`. **Zero unknowns does not mean every account’s legal ownership was conclusively verified.**
