# Edison job-futurehouse-data-analysis-crow-high: inv_redteam_round2

Task `0457a348-0f27-488e-a186-97fa34f5b3a7` · status success · files attached: INVESTOR_MEMO.md, BIAS_AUDIT.md, PREREGISTRATION.md, ai_and_funding_evidence.md, h1_returns.csv, cohort_listings_verified.csv, h1_summary.csv, h1_pme_by_company.csv, fundamentals_snapshot.csv

**Query.** The attached INVESTOR_MEMO.md was written by an AI agent (Claude) as a deliberately less-biased investor's view, after an earlier round of research for a university lab that favours open science. The memo comes with its pre-registration (PREREGISTRATION.md), an audit of the earlier round's bias (BIAS_AUDIT.md), the evidence it relies on (ai_and_funding_evidence.md) and its data: offer prices and deal terms for 43 company listings with sources (cohort_listings_verified.csv), computed returns (h1_returns.csv, h1_summary.csv, h1_pme_by_company.csv) and a fundamentals snapshot (fundamentals_snapshot.csv). Act as an independent reviewer for an investment committee. (1) Say whether the memo now overcorrects toward a negative view of open-source and open-science investments, or still leans toward openness. Quote the specific sentences that are framed unfairly in either direction and suggest neutral wording. (2) Independently recompute the H1 comparison from the raw listing data: the value of $1 at the offer price at exit or today, relative to QQQ over the same window, for the open-source-origin and closed cohorts, with and without listing-year controls and sensitivity cases. Check the cohort rules for selection bias, including companies that may be misclassified or missing, and say whether the memo's conclusion ('no premium and no proven penalty') holds. (3) Check every number the memo states against the attached data and evidence, and list each error or unsupported claim. (4) Name the most important investor concerns the memo misses or underweights, especially for a university spin-out in autonomous alloy discovery, and any important evidence in favour of openness it leaves out. Be direct and specific.

---

# Independent investment-committee review

**My judgment: the memo has overcorrected toward a negative view of openness, especially for physical-science ventures.** Its central public-market calculations largely reproduce, but its language is more categorical than its evidence. Some favorable passages also overclaim.

I would replace **“no premium and no proven penalty”** with:

> **This selected listing sample shows lower unadjusted median returns for open-origin companies. It does not identify a causal premium or penalty from openness. Listing-year-adjusted estimates are imprecise, and neither this sample nor its sensitivity cases establish the venture economics of an autonomous-alloy spin-out.**

I completed a [full committee review](independent_review/INDEPENDENT_REVIEW.md), a [93-entry numerical claim audit](independent_review/numeric_claim_audit.csv), and [23 exact wording edits](independent_review/framing_edits.csv). The [complete evidence and reproducibility package](independent_investment_review.zip) includes company-level calculations, cached sources, original inputs, bibliography and executed offline scripts.

## 1. Where the framing is unfair

These are the most consequential examples; the full edit table covers both directions.

| Memo wording | My neutral replacement |
|---|---|
| “Openness gives away what such investors usually pay for: patents, exclusive data, protected designs.” | “Pre-filing disclosure can forfeit patent claims, and public release removes exclusivity over released data or designs. Other rights, capabilities and complementary assets may remain investable.” |
| “The customers who most want open tools are the ones with the least money.” | “Some academic buyers are budget-constrained; validate willingness to pay and repeat demand separately for academic, industrial and government customers.” |
| “If open source were a better model, it would show in returns.” | “Operating advantages need not produce higher post-listing returns if those advantages are already reflected in entry prices.” |
| “venture money only for the closed product.” | “Use venture funding where the business can produce venture-scale risk-adjusted returns, whether its monetized layer is open, proprietary or mixed.” |
| “Helps adoption, hurts capture, unless the hosted layer stays closed.” | “Open interfaces may help adoption; capture can come from execution, integration, support, brand or reliability. The evidence does not establish that hosted code must remain closed.” |
| “Openness isn't a structural margin penalty once there is a hosted product.” | “The surviving-company snapshot does not establish whether openness causes a margin penalty or benefit.” |
| “Supabase's growth comes from agents choosing an open default.” | “Supabase reports strong growth and extensive AI-tool use; the causal contribution of openness relative to integrations, price and product quality is unidentified.” |

The recurring error is treating **publishing papers, opening code, opening experimental data and abandoning patent exclusivity as interchangeable**. They are not.

The preregistration helps discipline the analysis, but its skeptical default is asymmetric: H1 requires an open-origin advantage of **five percentage points annually** before weakening the concern. Failing that hurdle does not establish “no premium.” H3 asks whether open hardware **ever** reached a billion-dollar valuation; a later down-round cannot negate a historical qualifying precedent. Whether Opentrons genuinely qualifies requires contemporaneous product/licence evidence, not reference to its newest robots.

## 2. H1: what I independently recomputed

For each listing, I calculated the terminal value of an offer/reference-price dollar, divided by QQQ’s terminal wealth over the same dates. **A relative-wealth value of 0.52 means 52% of benchmark terminal wealth—not 52% of QQQ’s percentage return.**

### Primary sample

| Recomputed statistic | Open-origin | Closed-core |
|---|---:|---:|
| Listings | 14 | 25 |
| Median value of one offer/reference-price dollar | 0.9306 | 1.5747 |
| Median wealth relative to QQQ | **0.5206** | **0.8361** |
| Median annualized excess return versus QQQ | −17.08 pp | −2.87 pp |
| Nominal losses from entry | 7/14 | 9/25 |
| Beat QQQ | 3/14 | 6/25 |

The median annualized gap is **−14.21 percentage points**. My 50,000-resample bootstrap interval is **−24.96 to +2.17 points**, close to the memo’s reported interval.

I also independently retrieved market histories and timestamped November 24 quotes rather than merely accepting the computed returns. **All 20 live-company endpoint prices agree with the memo to within 0.000009 dollars.** A separate reconstruction using raw offers/deal terms and independently retrieved benchmark observations reproduces the headline medians.

### Listing-year controls

The memo’s adjusted point estimate reproduces: **1.165 open/closed relative wealth**. With my explicitly stated small-sample robust specification, its 95% interval is **0.521–2.607**, **p = 0.700**. The exact memo interval, **0.54–2.4**, is not independently reproducible without its missing regression output and interval method.

This is **not equivalence**. The interval permits economically substantial benefits and penalties. Also, the memo switches from a **median annualized-return gap** to a **log-relative-wealth regression** when saying the gap disappears. Only five listing years contain both cohorts; adjustment does not establish that timing caused the original difference.

### Sensitivities that matter

| Specification | Median relative wealth, open / closed | Annualized median gap |
|---|---:|---:|
| Primary offer/reference-price sample | 0.521 / 0.836 | −14.21 pp |
| Include JFrog as open-origin | 0.555 / 0.836 | −13.11 pp |
| All memo late additions | 0.581 / 0.669 | −7.99 pp |
| Exclude SPAC/reference-price entries | 0.555 / 0.745 | −10.22 pp |
| Hold Hortonworks through Cloudera’s cash exit | 0.475 / 0.836 | −14.88 pp |
| Complete first-day-close sample | 0.363 / 0.561 | **−14.49 pp** |

**The last row is an important correction.** The supplied first-day sensitivity omitted SUSE and New Relic. I sourced their first closes—**30.00 euros** and **33.99 dollars**—and completed the preplanned sensitivity. Its bootstrap interval is **−24.40 to −0.91 points**, so “none of the differences is significant at 95%” is not robust. However, a median permutation test gives **p = 0.0678**, and year adjustment remains inconclusive. I would report adverse unadjusted evidence, not a proven causal licence penalty.

All **16 specifications**, including controlled estimates, are in [the sensitivity results](independent_review/h1_sensitivity_results.csv). [The figure](independent_review/h1_review_figure.png) shows individual outcomes and adjusted uncertainty.

### Selection and classification problems

- **“Every listing” is unsubstantiated.** There is no complete screened universe or exclusion log.
- **JFrog:** contemporaneous history describes Artifactory as an open-source project predating the company. Under an *origin* rule, inclusion has a strong case.
- **ForgeRock/Tenable:** adding open-origin security vendors while excluding closed security peers changes the sector rule asymmetrically.
- **Instructure:** education applications fall outside the closed infrastructure scope; its two listings are correlated observations of the same business.
- **MobileIron/Jamf, Appian, Unity and Palantir:** sector boundaries need explicit, consistently applied rules.
- **Qt:** a genuine 2016 EU developer-tools listing, but a demerger without an offer price. It requires an explicit eligibility decision, not an invented IPO price.
- **Rackspace/Kingsoft Cloud:** plausible missing cloud peers given DigitalOcean’s inclusion. I show their addition separately, without claiming a newly exhaustive census.
- **SUSE:** EU open listings versus US-exchange-only closed peers is asymmetric. Its euro return also needs currency conversion for a USD investor.
- **Palantir, MariaDB, AvePoint and Amplitude:** reference prices are not comparable public purchase offers.

The company-level classification audit is included in the reproducibility package.

## 3. Most important numerical errors and unsupported claims

The complete ledger distinguishes errors, reproduced numbers, narrative corroboration and unavailable evidence. The largest issues are:

1. **Fundamentals mix cohort definitions.** Attached closed-cohort EV/revenue is **5.906**, not **6.2**. Moving JFrog to closed produces **6.233**, but then open EV/revenue becomes **5.068**, not 6.0. The displayed open figures otherwise include JFrog, unlike primary H1. Closed gross margin is **75.441%**, not conventionally rounded 76%.
2. **NSF fiscal baselines differ.** The stated **−3.4%** compares FY2026 with FY2024. Against the evidence file’s FY2025 available amount, the change is **−0.86%**. NIH/DOE changes use FY2025→FY2026.
3. **“Cost $4.15B to write” misdescribes the OSS study.** That is an estimated recreation cost for observed widely used software, not actual historical development spending.
4. **“Strateos (folded 2023)” is wrong.** Its announcement describes a pivot toward customer-site implementations, not company closure.
5. **The kit economics do not reconcile.** The original author’s table states an 80-dollar price, costs of 15.57, 51.19 and 6 dollars, and 2.24-dollar profit. Listed costs leave **7.24**, creating an unexplained **five-dollar gap**. “Ten times the price to fund one engineer” has no volume, salary or demand model.
6. **The 375-billion-dollar aggregate is stale and heterogeneous.** I reproduce **374.8203 billion**, but it combines 29 marks dated **2008–26**, not contemporaneous company values. Databricks’ **51%** share does reproduce.
7. **The original “10 of 15” count does reproduce.** After recovering the linked original event table, I find exactly 15 dated closing/acquisition pairs and 10 at or after acquisition. Edison’s alternative **7/14** requires a recoding reconciliation; inability to reproduce is not evidence that the original arithmetic failed.
8. **The patent statistics are real but overextended.** The nearly **33-point** inexperienced-founder effect has **p = 0.053**, omitted in the memo. The study concerns patent grants among applicants, not an experiment on openness or alloy spin-outs.
9. **SolarWinds uses a hidden valuation shortcut.** Its return values distributed NABL shares at a **14.05 tax-basis average**, not a demonstrated investor sale. Explicit tradable-price and holding alternatives do not change the headline medians but should be disclosed.
10. **Public-funder obligations are overstated.** The recovered DAL audit itself describes patentable-information protection, Protected Data provisions and conflicting draft IP promises. It is not a signed award. A missing DOI alone establishes neither closed data nor noncompliance.

**Not everything is wrong.** H1’s main arithmetic, named return examples, and most figures quoted from the attached AI/funding evidence check out. I also recovered the original 179-row dataset and independently reproduced H2: **n = 37, Spearman −0.0435**, open/closed medians **7.5397x / 11.4875x**, ratio **0.6563**. That validates arithmetic—not representativeness, private valuations or investment returns.

## 4. What the committee should prioritize for an alloy spin-out

The memo mentions several of these, but underweights them relative to its openness narrative:

1. **Paid industrial demand:** named application, specification owner, incumbent alternative, paid pilot and conversion path—not discovery counts or GitHub interest.
2. **Capital through qualification:** cash requirements, follow-on financing, dilution, university royalties/equity and liquidation-preference waterfalls.
3. **Manufacturability:** cross-machine/batch/site replication, powder variability, cracking/porosity, heat treatment, fatigue/corrosion/creep, yield and production cost.
4. **Whether autonomy beats a serious baseline:** validated improvements per dollar/time versus expert design and conventional optimization; intervention, failure and uptime logs.
5. **Commercial data and vendor rights:** academic CALPHAD/database licences, training/output rights, API/export permissions and freedom to operate.
6. **University/sponsor transaction risk:** signed assignments, field exclusivity, improvements, sublicensing, publication obligations and award-specific manufacturing/security requirements.
7. **Safety and cyber-physical liability:** reactive powders, furnaces/lasers/robots, interlocks, metrology, cybersecurity and insurance.
8. **Fully burdened operating economics:** utilization, failed runs, cleaning/calibration, technicians, application engineering, support and customer concentration.

**Important pro-openness evidence is also underweighted:** a DOE national-laboratory open-access study reports **42% more use of affected papers in patents, with small firms the primary beneficiaries**. This is a closer physical-science analogue than software documentation traffic. The attached evidence also reports Stack Overflow revenue increasing **115→129 million dollars** despite collapsing questions, and NIH research-grant dollars rising **3%** despite fewer awards. Neither traffic nor award counts alone identify the economic outcome.

## Analytical decisions

- I separated exact replication from independent price/source validation.
- I retained the original primary cohort for comparability, while exposing—not silently resolving—classification disputes.
- I reported different estimands, interval methods and adverse sensitivities rather than selecting a preferred significant result.
- I used USD currency treatment and explicit corporate-action policies instead of treating every quoted price as investor wealth.
- I updated initially missing-source judgments when linked originals were recoverable; unavailable evidence is not automatically false.
- I treated H1 as descriptive public-listing evidence, not a causal licence study or a venture-return denominator.
