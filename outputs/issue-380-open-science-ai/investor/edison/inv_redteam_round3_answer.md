# Edison job-futurehouse-data-analysis-crow-high: inv_redteam_round3

Task `964eae07-c97f-4d77-8d9a-5f021306caf8` · status success · files attached: INVESTOR_MEMO.md, BIAS_AUDIT.md, round2_review.md, round2_framing_edits.csv, h1_returns.csv, h1_summary.csv, h1_permutation.csv, fundamentals_summary.csv, cohort_listings_verified.csv

**Query.** INVESTOR_MEMO.md is a revised investor memo on the risks of investing in open-source and open-science ventures, written by an AI agent (Claude) for a university lab that favours open science. Its previous draft was reviewed by an independent analyst (round2_review.md, with suggested wording edits in round2_framing_edits.csv), who found that the draft had overcorrected toward a negative view. The revision says it applied that review. Please give a short, direct assessment (under 900 words, no long report needed): (1) Is the revised memo now balanced, or does it still lean negative, or has it tipped toward favouring openness? Quote up to five remaining sentences that are unfair in either direction, with neutral replacements. (2) Were the round-2 corrections applied correctly? Check a sample of the numbers in the memo against h1_returns.csv, h1_summary.csv, h1_permutation.csv, fundamentals_summary.csv and cohort_listings_verified.csv, and list any remaining numerical errors. (3) In two or three sentences, what is the single most important thing an investor should take from this memo?

---

## 1. Balance: largely corrected, but still mildly negative

I would no longer call this an overcorrection against openness. The revision distinguishes public benefits from investor returns, acknowledges successful open businesses and closed-company failures, and substantially improves its causal caveats. **It has not tipped toward favouring openness.** Its remaining negative tilt comes mainly from presenting selective disclosure as the preferred strategy without comparative evidence, and occasionally turning limited observations into general conclusions. A risk-focused memo need not give benefits equal space; the issue is whether its conclusions exceed its evidence.

I would change these four remaining sentences:

- **“A public-market investor in open-source software companies has not been rewarded for open-source origin as such.”**  
  Replace with: “This selected listing sample has lower unadjusted median returns for open-source-origin companies; it does not identify the return attributable to open-source origin.”
- **“The strongest case for openness is selective.”**  
  Replace with: “Selective disclosure is one possible strategy; the appropriate scope of openness depends on adoption benefits, complementary assets and financing needs.”
- **“Enabling disclosure before filing removes novelty for the claims it covers.”**  
  Replace with: “Pre-filing enabling disclosure can prevent patent protection for affected claims, depending on jurisdiction and applicable exceptions.” The memo acknowledges the US grace period elsewhere, but this sentence remains categorical.
- **“Grants and partners such as GroupGets are the right money for it.”**  
  Replace with: “The kit’s reported sales and margins do not establish a venture-scale business; grants, partnerships and commercial financing should be assessed against a credible scaling plan.”

## 2. Round-2 corrections: mostly applied correctly

All 23 originally flagged formulations have been removed or rewritten. Substantively, the revision fixes the major problems: patent grants are distinguished from openness; operating advantages from investment returns; Opentrons’ growth from causation; and Strateos’ pivot from closure. It makes H3 unresolved rather than treating a later down round as disproving an earlier billion-dollar valuation, corrects the fundamentals cohort, and adds the omitted favourable evidence and spin-out diligence priorities.

I checked all five supplied datasets and independently recomputed the primary cohort statistics, excluding JFrog as specified:

| Check | Result | Assessment |
|---|---|---|
| Relative terminal wealth versus QQQ, from `h1_returns.csv` | 0.5206 open-origin / 0.8361 closed | Correctly reported as 0.52 / 0.84; these are wealth ratios, not percentage returns |
| Annualized excess returns and nominal losses | −17.08 / −2.87 percentage points; losses 7/14 / 9/25 | Correct |
| Gaps and bootstrap intervals in `h1_summary.csv` | Offer: −14.21 points, CI −25.10 to +2.17; first close: −14.49, CI −24.36 to −0.66 | Correctly rounded in the memo |
| Primary permutation tests in `h1_permutation.csv` | Offer/QQQ 0.10270; first-close/QQQ 0.08628; offer/IGV 0.03454; relative wealth 0.19754 | Correctly reported as 0.10, 0.09, 0.03 and range 0.03–0.20 |
| `fundamentals_summary.csv`, four open-origin / 14 closed survivors | Gross margins 74.15% / 75.70%; free-cash-flow margins 23.83% / 25.22%; EV/revenue 5.068× / 6.2325×; growth 19.2% / 25.5% | All memo roundings correct; JFrog sensitivity also matches |
| `cohort_listings_verified.csv` | SUSE first close €30.00; New Relic $33.99; HashiCorp offer/exit $80/$35 | Correctly incorporated |

**Remaining numerical issue:** the listing-year-adjusted ratio reproduces at **1.1653**, but the quoted **95% interval of 0.54–2.4 remains unsupported**, as round 2 already noted. My year-fixed-effects regression gives **0.539–2.521** with HC3 heteroskedasticity-robust normal inference, or **0.521–2.607** with small-sample t inference. The memo should supply its method/output or replace the interval with a documented calculation; this is an unresolved reproducibility issue, not a proven arithmetic typo.

I found **no other numerical errors in the sampled claims**. This checks the supplied files, not the underlying web sources or every 2025–26 assertion.

## 3. The single most important investor takeaway

**Underwrite the business, not the openness label.** For an alloy-discovery spin-out, paid industrial demand, reproducible performance, cash through qualification and defensible value capture matter more than this selected software-listing comparison; openness can help or hinder those economics depending on what is released and when.

**Analytical decisions**
- I retained the memo’s primary cohort for comparability and treated survivor statistics and listing returns as descriptive, not causal.
- I separated confirmed numerical discrepancies from method-dependent uncertainty; I did not label an unreproduced interval a definite arithmetic error.

[Assessment file](assessment/memo_assessment.md)
