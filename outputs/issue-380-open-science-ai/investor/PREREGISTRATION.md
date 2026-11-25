# Pre-registration: the investor's view of open science and open source (issue #380, round 2)

Written 2026-11-25 at about 00:55 UTC, before any of the new data below was fetched and before any Edison answer
came back. It is committed first so the analyses can be checked against what was planned.

## The request

> try to take a less-biased approach. As an investor, what might be your major concerns with this kind of
> investment? You can use edison as a more independent rubber-duck

The first round (branch `claude/issue-380-20261123-2145`, latest `db24bf3`) asked what open science and open source
are worth. This round asks what someone putting money in should worry about. Those are different questions.
Value *created* (consumer surplus, research use, replacement cost) is the first round's main currency. An investor
only gets paid out of value *captured*.

## Why the first round may be biased

These are the reasons to distrust it, written down before looking for new evidence:

1. **Who asked.** The lab builds open-source self-driving labs and argues for open science. An agent working for
   it is pulled toward conclusions the lab will like.
2. **Who wrote it.** Claude, made by Anthropic, a company that keeps its weights closed and opens its tooling.
   Neither direction of that pull is obviously absent.
3. **Value created vs. value captured.** The headline numbers ($8.8T, PDB use value, 87% cheaper hardware) are
   social value. They say little about returns to whoever pays for the work.
4. **Interested sources.** The venture comparison (7× and 14× median exits) comes from a report co-written by a
   venture firm that invests in open source, with an open-source foundation and a trade group.
5. **Survivors.** The 179 case files cover organizations notable in 2026. Failures that nobody remembers are
   missing, and that flatters every strategy, open or closed.
6. **Conditional statistics.** Exit medians are conditional on an exit. Investors need the whole distribution,
   including the companies that returned nothing.

## Investor personas

- **A.** A venture investor looking at an open-source or open-science spin-out in the physical sciences, for
  example a company built on the lab's autonomous alloy lab (DAL, #318) or on an open SDL kit.
- **B.** A public-market investor in commercial open-source software companies.
- **C.** An institutional "investor" in the lab itself: a federal programme (DOE Genesis Mission, ONR) or an
  industry sponsor deciding whether open-by-default terms are worth funding.

## Hypotheses and what would count against them

Each is phrased as an investor's concern. The test says what result would weaken that concern.

| # | Concern | Test | Concern weakened if |
| --- | --- | --- | --- |
| H1 | Open-source origin doesn't earn public investors a premium | Every US and EU listing (IPO, direct listing or SPAC) of a company whose core product began as open source, 2014–2022, against a cohort of closed-source infrastructure-software listings from the same years chosen by rule (below). Return from offer price to the exit price or to the latest close, annualized, and in excess of QQQ over the same window | The open-source cohort's median annualized excess return beats the closed cohort's by 5 points or more |
| H2 | Openness doesn't raise value captured per dollar raised | In the first round's case files: latest value ÷ total funding, and the share acquired, taken private, or shut, by openness now and at founding, within sector | More open firms have higher value-to-funding with confidence intervals that exclude no difference |
| H3 | Open hardware doesn't reach venture scale | Edison precedent search, plus the case files: has any company whose main products are open hardware reached a valuation or exit of $1B or more? | One or more clean cases exist |
| H4 | AI weakens the funnel open-source companies monetize (documentation, community, support) and lowers the cost of copying | Published studies and dated 2025–26 company disclosures | Little or no evidence of a funnel decline, or evidence that AI raised OSS revenue |
| H5 | Selling to US academic labs is now a riskier market | US federal science budgets and obligations, FY2024–FY2026, and the tools companies' academic and government revenue | Federal research spending held flat or rose in real terms |
| H6 | Open-by-default disclosure lowers a physical-science spin-out's ability to raise money | Causal studies of patents and startup financing; novelty and grace-period rules | Evidence that patents don't matter for financing in these sectors, or that openness raises financing |

## Rules for the H1 cohorts

- **Open-source cohort:** companies whose core product began as an open-source project they lead or sponsor,
  listed 2014–2022. Planned list: Hortonworks, Talend, MuleSoft, Cloudera, MongoDB, Pivotal, Elastic, Confluent,
  SUSE, Kaltura, Couchbase, GitLab, HashiCorp, MariaDB (SPAC). JFrog is ambiguous (proprietary core with a free
  open-source edition), so it is reported both ways.
- **Closed cohort:** closed-source companies listed on a US exchange 2014–2022 in the same product categories:
  databases and data platforms, data integration and middleware, developer tools and DevOps, observability and IT
  operations, and infrastructure software. Security, business applications (CRM, HR, finance), consumer and
  hardware companies are excluded. The list is drawn from Wikipedia's and Renaissance Capital's IPO records before
  any returns are computed, and every qualifying company is kept, whatever it later did.
- **Returns:** offer price to the cash deal price on the closing date, or to the latest close for companies still
  listed. Stock-and-cash deals are valued at the announced value per share. Spin-offs and special dividends are
  included where Yahoo's adjusted prices capture them, and noted otherwise. A second version starts from the
  first-day close, which is what a public investor could actually pay.
- **Everything is reported**, including results that favour open source.

## Edison as the independent check

Edison is asked neutral questions, phrased as an investor would ask them, without the first round's conclusions
(`edison/queries.json`). One analysis job then receives the first round's brief, recommendations and dataset and
is asked to red-team them. A second analysis job will red-team this round's own memo before it is final. Edison's
answers are kept in full and reported separately from my own conclusions, including where they disagree.
