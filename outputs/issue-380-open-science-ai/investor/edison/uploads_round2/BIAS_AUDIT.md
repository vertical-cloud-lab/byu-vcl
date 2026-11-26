# Where the first round leaned toward openness

An audit of the first round's [`FINDINGS_BRIEF.md`](edison/uploads/FINDINGS_BRIEF.md),
[`RECOMMENDATIONS.md`](edison/uploads/RECOMMENDATIONS.md) and `README.md` (branch `claude/issue-380-20261123-2145`,
commit `db24bf3`), read as an investor would read them. The first round's own independent review
(`REVIEW_FINDINGS.md`, 39 issues) checked whether numbers were right. This audit asks a different question:
which way did the framing lean? An independent check of the same files by Edison is in
[`edison/inv_redteam_round1_answer.md`](edison/inv_redteam_round1_answer.md).

## Who asked, who answered

- The lab that asked builds open-source self-driving labs and argues for open science.
- The agent that answered is Claude. Anthropic keeps its model weights closed and opens its tooling, so its pull
  could run either way. The pull toward the requester's views is the better-documented one.
- None of the first round's eight recommendations says "keep this closed". The one exception it allows is a
  provisional patent on an alloy composition that has a named licensee.

## Seven places the framing favoured openness

1. **Value created came first; value captured came second.** Short answer 1 leads with "create far more value
   than they cost" ($8.8T, the PDB's $5.5B of research use, 87% cheaper hardware). Those are social values. An
   investor is paid only from what a company captures, which the same sentence says is rare. The headline and
   the caveat should swap places for this audience.

2. **The examples were winners.** Short answer 2 illustrates "who captures the value" with Databricks, the
   Hugging Face deal, Confluent, Red Hat and MongoDB. It doesn't put next to them the open-source companies
   whose public investors lost money or broke even: MariaDB, HashiCorp, SUSE, Couchbase, Cloudera and
   Hortonworks. Nor does it mention Docker, whose software became an industry standard and whose company was
   recapitalized. Picking cases by outcome flatters whatever strategy the winners used. H1 in
   [`INVESTOR_MEMO.md`](INVESTOR_MEMO.md) replaces the examples with every listing in a defined window.

3. **"Venture data agrees" rests on an interested source, and one of its numbers cuts the other way.** The
   7× and 14× exit medians come from a report co-written by a venture firm that invests in open source, a
   foundation and a trade group. The first round disclosed this but still led with the numbers. Exit medians
   are also conditional on an exit, and only 12% of the sample had one. The same report's 1.6× higher Series A
   valuation was presented as a strength. For an investor buying in, a higher entry price is a cost: it lowers
   the multiple unless exits are higher by more.

4. **"Foundations keep openness durable" is a commons argument, not an investment one.** Moving code to a
   neutral foundation (recommendation 2) is what keeps it open, and that is the point. It also gives up the
   control a company would need in order to relicense, bundle or exclude a competitor. Confluent could not
   relicense Kafka, and Kubernetes' largest earners are the clouds that host it.

5. **The report saw the investor's logic and recommended against it without weighing it.** Recommendation 3
   notes that "the 2025–26 AI-for-materials startups protect *data and compositions*" and that failed runs are
   "the signal closed players hoard". It then recommends releasing all data, failed runs included, within 12
   months. That can be the right call for a publicly funded lab. A spin-out would be giving away the asset
   its funders are paying for. The trade-off should be stated, not resolved by default.

6. **"Sell services around the open core" borrowed evidence from a different business.** Recommendation 4
   supports services with Databricks, Confluent and MongoDB Atlas, which are hosted software with software
   margins. Lab services, such as cloud-lab time, setup and integration, are a different business. Their
   track record in the case files is Strateos closing its hosted cloud lab in 2023, after about $80M or more
   in funding, and Emerald Cloud Lab, whose biggest win was a $40M cloud lab built for Carnegie Mellon.

7. **The dataset couldn't answer the investor's question, and that went unsaid.** The 179 case files were
   built to describe openness. Only 37 for-profit organizations have both a funding total and a value, almost
   none of them closed software companies, and organizations that failed mostly have no value recorded. Tested
   here (H2), openness shows no relationship with value per dollar raised (Spearman ρ −0.04, 95% CI −0.39 to
   0.31, n = 37). Neither side should claim the casebook as evidence.

## What was missing for an investor

- **Base rates.** Most venture-backed companies return less than the capital invested, open or closed. A
  strategy is judged by its whole distribution, including the companies nobody remembers.
- **Entry price and time.** Multiples on capital, internal rates of return and holding periods, not latest
  valuations. Private marks are not realized returns.
- **The customer's budget.** Open lab tools sell mostly to academic labs. US academic research is 55%
  federally funded ($64.6B of $117.7B in FY2024, NSF HERD), and federal science funding was cut and disrupted
  in 2025–26 (see the memo's H5).
- **Who else profits.** Open data and open models feed the largest firms first: the PDB trained AlphaFold, and
  Isomorphic Labs commercializes its successor, whose weights are not open for commercial use. The first round recorded this as a fact about the commons; for an
  investor it is the central risk.
- **The lab's own purchases.** By the first round's audit, the lab's alloy route runs on about 20 instruments,
  of which about 4 can be programmed. Its printers are closed Bambu Lab machines and its CALPHAD route uses
  proprietary Thermo-Calc. A lab that argues for openness still buys closed tools when they work better, which
  is exactly the willingness-to-pay question an investor would ask about an open product.

## What the first round got right, from an investor's chair

The audit is one-sided by design, so for balance:

- It said plainly that value goes "to whoever runs the service, owns the data or sells the hardware", that
  open hardware "pays in cost and longevity, not in valuation", and that the SDL-demo kit made $2.24 a kit.
- It disclosed the venture report's conflict of interest and the 12% exit rate.
- It corrected its own overstatements after review, in a public fourth video.
