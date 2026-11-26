# Pre-registration: who owns popular open source, and what do the owners earn? (issue #380, round 2, part 2)

Written 2026-11-25 at about 21:25 UTC and committed before any of the data below was fetched. The only GitHub call
made beforehand was a three-row test query to check API access (the top three repositories by stars).

## The request

> I think you can do a lot more manual digging and data extraction (e.g., large-scale GitHub searches of
> repositories and their parent organizations, then looking into the financial details of those parent
> organizations).

The first part of this round worked from 39 listings and the first round's case files, both chosen by people
looking for notable companies. This part starts from the other end: the open-source work itself. It takes the
most-starred repositories on GitHub, finds who owns them, and then finds what those owners earn, raise and are
worth. Starting from the repositories rather than from the companies means that the owners which made no money are
counted.

## Frames (fixed before fetching)

- **Frame A, popular open source.** The 2,000 most-starred public, non-fork repositories on GitHub on 2026-11-25,
  from the search API (`stars:>N`, sorted by stars, paged through star ranges because one query returns at most
  1,000 rows).
- **Frame B, open science.** For each of these 22 topics, the 100 most-starred repositories carrying the topic with
  at least 10 stars, pooled and de-duplicated: `chemistry`, `computational-chemistry`, `cheminformatics`,
  `materials-science`, `materials-informatics`, `bioinformatics`, `genomics`, `drug-discovery`,
  `molecular-dynamics`, `quantum-chemistry`, `protein-structure`, `lab-automation`, `laboratory-automation`,
  `self-driving-lab`, `autonomous-experimentation`, `open-hardware`, `open-source-hardware`,
  `scientific-computing`, `physics`, `astronomy`, `neuroscience`, `microscopy`.
- **Content repositories** (lists, books, courses, interview preparation) are flagged by rule and reported
  separately: no primary language, or a topic among `awesome`, `awesome-list`, `list`, `lists`, `resources`,
  `tutorial`, `tutorials`, `book`, `books`, `interview`, `interview-questions`, `roadmap`, `cheatsheet`, `learning`,
  `education`, `course`, `courses`, or a name containing `awesome`, `interview`, `roadmap`, `cheatsheet`,
  `tutorial`, `book`, `course`. The main results use the remaining software repositories.

## Owner classes

Each organization account is assigned one class, by me, from its GitHub profile, its website, Wikidata (property
P2037, GitHub username) and, where needed, its own pages. Classification is done before any financial figure is
pulled, so the class cannot be chosen to fit an outcome.

| Class | Rule |
| --- | --- |
| **Core company** | A company whose main paid product is the project itself in another form: a hosted service, an open-core or enterprise edition, support subscriptions, or hardware it sells. Example: Elastic and `elastic/elasticsearch` |
| **Complement company** | A company that publishes the project but earns most of its revenue from other products. Example: Meta and `facebook/react` |
| **Nonprofit** | A foundation or other nonprofit that owns or stewards the project. Example: the Python Software Foundation and `python/cpython` |
| **Academic** | A university, university lab or academic research institute |
| **Government** | A government agency or national laboratory |
| **Community** | A project with no owning legal entity, or one that only uses a fiscal host such as Open Collective |
| **Individual** | A repository owned by a personal account rather than an organization. Not investigated further |
| **Unknown** | Not identifiable from public sources |

## Financial details (fixed before fetching)

| Owner | What is collected | Source |
| --- | --- | --- |
| Listed company | Market cap, revenue, margins, R&D | Yahoo Finance; SEC XBRL company facts for US filers |
| Private company | Disclosed total funding and latest disclosed valuation; for US companies, the total amount sold across Form D filings | Company and investor press releases; SEC EDGAR Form D |
| Acquired or shut down | Acquirer, date, disclosed price, or date of shutdown | Press releases, filings |
| US nonprofit | Total revenue, expenses and net assets, latest year and FY2019 | IRS Form 990 via ProPublica Nonprofit Explorer |
| Community project | Total raised and last-12-months income | Open Collective |

Every figure keeps its source URL. Figures that can't be sourced are left blank rather than estimated.

## Hypotheses

Numbering continues from the first part ([`../PREREGISTRATION.md`](../PREREGISTRATION.md)). Each is phrased as an
investor's concern, with the result that would weaken it.

| # | Concern | Test | Concern weakened if |
| --- | --- | --- | --- |
| H7 | Most popular open source is paid for by organizations that don't sell it, so a company that does sell it competes with free work funded by others | Share of Frame A software stars by owner class | Core companies hold at least half the stars held by all companies (core + complement) |
| H8 | Popularity converts poorly into money | Among core companies in Frames A and B with a disclosed latest value (market cap on 2026-11-24, exit price, or latest private valuation): Spearman ρ between the organization's stars in the frame and its latest value, with a 5,000-resample bootstrap 95% CI. The same for disclosed capital raised. The spread of value per star (75th ÷ 25th percentile) | ρ(stars, value) ≥ 0.4 and its CI excludes 0 |
| H9 | Outcomes for companies built on popular open source are worse than the famous examples suggest | For every core company in Frame A: status on 2026-11-25 (listed, acquired, private and operating, shut down, project handed to a foundation), whether it ever reached $1B in value (private mark, market cap at its first close, or exit price), and for acquisitions with a disclosed price, whether the price exceeded capital raised | At least 25% reached $1B and at most 10% shut down. (For comparison, published cohort studies put the share of companies raising a Series A that later reach $1B in the low single digits, but those companies were not selected on traction, as these are) |
| H10 | Open science software and hardware attracts little private capital (persona A) | Share of Frame B software stars by owner class; every company owner in Frame B with its disclosed financing and outcome | Companies hold at least 30% of Frame B software stars, or at least 10 core companies in Frame B have each raised $10M or more |
| H11 | The organizations that keep the commons running have thin, flat budgets (memo concern 10) | Latest Form 990 revenue of US nonprofits owning repositories in either frame, against FY2019 deflated by CPI-U; Open Collective income of community projects; revenue per 1,000 stars | The median nonprofit owner had at least $10M of revenue in its latest year, and at least two-thirds grew in real terms since FY2019 |

## What will be reported

All of it: the repository and owner tables, every classification with its basis, every financial figure with its
source, and every hypothesis result, including those that favour openness. Classifications that are judgment calls
are marked as such. Where I deviate from this plan, the deviation is listed with its reason.

## Known weaknesses, stated in advance

- Stars measure attention, not use or revenue, and they accumulate over time, so old projects are favoured.
- The frames are still survivors in one sense: a project has to be popular to be counted. They are not selected
  on financial success, which is the bias this part tries to remove.
- Form D covers only US securities offerings that rely on Regulation D, and companies sometimes file under other
  entity names. It understates capital raised; it does not overstate it.
- Private valuations are marks, not returns, and many are undisclosed.
- I classify the owners myself. To make that checkable, each class comes with its basis, and the judgment calls
  are flagged.
