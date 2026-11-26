# Who funds open-source-minded ventures? Scope and method (issue #380, round 2, part 3)

Sterling asked (PR #386, 2026-11-26): *"compile a list of investors, firms, philanthropists, and other VC and VC-like
sources that have been involved in funding a venture that falls into the more open-source minded of startups. Be
thorough and manual."* This file fixes the scope and the counting rules before any funding data is collected, so
that the list is not shaped by what turns up.

## What counts as an open-source-minded venture

A company (or a venture-like project that took outside money) whose main product is something it created or leads
and releases openly:

| Kind | Test |
| --- | --- |
| Commercial open source (COSS) | Its main paid product is an open-source project it leads, in another form: hosted service, open core, enterprise edition, licences, support. Projects later relicensed to source-available or fair-code licences stay in, flagged |
| Open-weight AI | Releases the weights of its main models for download (any licence; non-commercial licences flagged) |
| Open hardware | Publishes the design files of its main products under an open licence, or did so when it raised money |
| Open science | Its business is open-access publishing, open data, open protocols or open research tooling, even where its own code is closed (flagged) |
| Open-source platforms | Businesses whose product exists to host, fund or secure open source (GitHub, Tidelift, npm) — flagged; counted separately |

Corporate labs (Meta, Google, Microsoft) are not ventures and are out. Nonprofits are out of the deal list but their
funders are in the program list below.

## The ventures (three universes, each kept separate in the data)

- **U1, the systematic sample.** All 392 `core` companies from part 2's GitHub harvest (the 2,000 most-starred repos
  and the top 100 in each of 22 science topics; `../owners/data/finance_passes/input_all.csv`). Nobody picked these
  for their funding; they are in because their projects are popular on GitHub. Their classification was frozen in
  `efd5a76`, before this question was asked.
- **U2, open hardware, open science and science software.** Hand-picked: the first round's open hardware, lab and
  science companies (`../edison/inv_redteam_round1_files/ic_review/companies_analysis.csv`), plus open robotics,
  open instruments, lab automation, open-science publishing and tools, DeSci. Chosen for relevance to DAL and the
  SDL kit, so it is not a random sample.
- **U3, notable COSS and open-weight AI ventures not in U1.** The open-source listings from the H1 cohort
  (`../data/cohort_listings_verified.csv`), the first round's for-profit open-source companies, and well-known COSS
  exits, failures and AI labs from 1998 on. Chosen because they are known, which over-represents successes.

Every venture carries `universe` and `source_list` columns, so any count can be restricted to U1.

## What counts as a funder

Anyone who put money in, named in a public source: lead and participating investors in equity rounds, angels,
accelerators, corporate and strategic investors, crowdfunding (reward and equity), token sales (flagged),
philanthropic and government grants and prizes, venture debt where named. Acquirers and IPO buyers are not funders.
"Existing investors" without names are not counted.

Separately, a **program list** records philanthropic, government, corporate, crypto and community programs that fund
open source or open science at the program level (who, what program, years, amount, what it funds, whether it
funds companies), because much of that money goes to projects and nonprofits rather than to ventures.

## Counting rules

- One venture counts once per investor however many rounds the investor joined; rounds and leads are counted too.
- Investor names are normalised by an alias table kept in `data/investor_aliases.csv` (e.g. a16z = Andreessen
  Horowitz; GV = Google Ventures). Fund vehicles roll up to the firm. People are kept separate from their firms.
- Investor type is assigned centrally, by hand, after collection: venture firm, corporate venture or strategic,
  angel or person, accelerator or incubator, growth/PE/hedge/crossover, sovereign or public investor, philanthropy,
  government grant, crowdfunding, crypto fund or DAO, bank or debt, other.
- Every round needs a URL that states the investors or the amount. Database pages (Crunchbase, Tracxn, PitchBook
  profiles) are allowed but marked, and counted separately in a sensitivity check.
- Absence is recorded: a venture with no disclosed outside funding gets a row saying so.

## What the list cannot show

Disclosure is selective: big rounds and successful companies are reported more; small angels and failed companies
are not. U2 and U3 are hand-picked. A count of open-source deals says what an investor has done, not whether it
made money or will do it again, and nothing here is advice to approach anyone.
