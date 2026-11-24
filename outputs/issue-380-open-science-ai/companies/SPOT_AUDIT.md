# Citation spot-audit of the case files (issue #380)

Audited on 2026-11-24 by a Claude agent session. Scope: the 179 case files in
`companies/{A,B,C,D,E,F,G,I,J}/*.json` and their 1,354 `sources` entries. The case files were not changed.
Rows are also in [`spot_audit.csv`](spot_audit.csv).

**Question.** When a source is attached to a field through its `supports` string, does that page state the value the file gives?

**Answer.** Supported: 23/30 = 76.7% (Wilson 95% CI 59.1% to 88.2%). No sampled citation was off-topic or unreachable,
but about one in four attaches a value that the cited page does not itself state.

## Method

1. **Sampling frame.** Every (file, source) pair whose `supports` names at least one concrete schema field:
   `founded_year`, `latest_value_usd`, `funding_total_usd`, `revenue_latest_usd`, `employees_latest`, `end_year`,
   `exit_events`, `relicensing_events` or `license_history` (regex over the free-text `supports` string). A token
   followed by `(none)`, which claims that no event exists, does not count. 750 of the 1,354 sources qualify.
   Free-text fields (`risk_events`, `origin_detail`, `openness_notes`, `robustness` and so on) were not audited.
2. **Draw.** Files sorted by path, sources in file order, then `random.seed(380)` and
   `random.sample(range(750), 750)` to fix a full draw order. Draws 1-30 form the sample. Replacements are taken in
   draw order from 31 on.
3. **Claim audited.** Every concrete field the `supports` string names for that source, with the values read from
   the JSON. For list entries the audited values are: `license_history`, the licence and its year;
   `relicensing_events`, the year and the new licence, with the prior licence checked too;
   `exit_events`, the year, type, `value_usd` and counterparty, or the narrower aspect `supports` names
   (for example "market cap" or "agreement terms").
4. **Verdicts** follow the brief. *Supported*: the page states the value or it rounds to it. *Partially supported*:
   the right fact with a different or less precise number or date. A pair is also partial when some of its audited
   fields are on the page and others are not. *Not supported*: none of it is on the page. *Unreachable*: the page did
   not load.
5. **Fetching.** WebFetch only: no WebSearch, browser, proxy or Pi. WebFetch answers a prompt with a small model, so
   every prompt asked for verbatim quotes and an explicit NOT FOUND. Each "partially supported" verdict that rests on
   something being absent (draws 3, 4, 5, 13 and 28) was re-checked with a second, narrowly worded prompt. Long pages
   were read in parts using `offset` (draw 16, three reads). WebFetch fetched the GitLab FY26 PDF (draw 26) but could
   not decode it, so the text came from `pdftotext` run on the copy WebFetch saved. Separately, `curl -I` HEAD
   requests were used to read the sizes of three PDFs, only to apply the 5 MB rule.
6. **Skips and replacements.** Draw 7 (Alphabet's 2025 annual report PDF on sec.gov) returned 403 to the HEAD request.
   WebFetch then refused it as larger than its 10 MB limit, so it is a PDF over 5 MB: skipped and replaced by draw 31.
   There were no paywall URLs in draws 1-31 (the first is a bloomberg.com link at draw 45), and no unreachable pages.
   One replacement was used of the 10 allowed.
7. **Strict variant (sensitivity check).** This reclassifies as partial the 5 supported pairs where the cited page
   lacks a secondary element: the prior licence of a relicensing event (draws 2, 15 and 21), or the year of a
   licence or revenue figure (draws 12 and 31).

## Results

31 rows: the 30 audited pairs plus the skipped draw. The phrase column gives at most 20 words copied from the page;
"..." marks omitted text and [square brackets] mark my glosses.

| Draw | Group | File | Field(s) audited | Claimed value | URL | Verdict | Phrase from the page | Note |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | B | `B/databricks.json` | revenue_latest_usd | $7.0B (2026; file labels it a run-rate) | [databricks.com](https://www.databricks.com/company/newsroom/press-releases/databricks-grows-80-yoy-surpasses-7b-revenue-run-rate-scales) | supported | crossed a $7 billion revenue run-rate, delivering >80% year-over-year growth during its Q2 | Release dated 2026-08-13. |
| 2 | C | `C/mistral-ai.json` | license_history[3]; relicensing_events[1] | 2025: Mistral 3 family (Large 3 675B/41B; Ministral 3B/8B/14B) to Apache-2.0 | [mistral.ai](https://mistral.ai/news/mistral-3) | supported | All models are released under the Apache 2.0 license. | Dated 2025-12-02; sizes match. Prior research/non-production licences not named on this page. |
| 3 | G | `G/digital-science-figshare.json` | license_history[0]; exit_events[0] | 2012: proprietary platform, content CC BY / CC0; 2012 acquisition by Digital Science | [en.wikipedia.org](https://en.wikipedia.org/wiki/Figshare) | **partially supported** | supported by Digital Science since a January 2012 relaunch; CC-BY for most files and CC0 ... for datasets | Infobox owner is Digital Science, but no acquisition, date or Holtzbrinck (page says Springer Nature); platform licence not stated. Re-checked. |
| 4 | D | `D/prusa-research.json` | employees_latest | 1,144 (before 2026 cuts) | [cnews.cz](https://www.cnews.cz/clanky/prusa-poprve-propousti-ceskemu-vyrobci-3d-tiskaren-se-nedari-plnit-prodejni-cile/) | **partially supported** | Firma, která dnes zaměstnává přes 1 100 lidí | "Over 1,100 people"; the figure 1,144 does not appear (re-checked). |
| 5 | G | `G/automata.json` | funding_total_usd | $135M (as of 2026-01) | [automata.tech](https://automata.tech/company-news/automata-raises-us50-million-in-series-b-financing-to-accelerate-automation-in-life-sciences) | **partially supported** | has raised US$50 million in Series B funding | Feb 2022 round only; $135M is the sum of three rounds and no total is stated (re-checked). |
| 6 | D | `D/ultimaker.json` | founded_year; license_history[0]; employees_latest | 2011; CC BY-NC Ultimaker Original (2011); about 400 (2019) | [en.wikipedia.org](https://en.wikipedia.org/wiki/Ultimaker) | supported | founded in 2011 ... under a Creative Commons BY-NC license ... 400 (2019) |  |
| 7 | C | `C/alphabet-google.json` | revenue_latest_usd | $402.836B (2025) | [sec.gov](https://www.sec.gov/Archives/edgar/data/0001652044/000130817926000344/goog014907-ars.pdf) | **skipped** | (not fetched) | WebFetch refused: over its 10 MB limit, so a PDF over 5 MB. Replaced by draw 31. |
| 8 | G | `G/markforged.json` | revenue_latest_usd; employees_latest; license_history[1]; exit_events[1] (agreement terms) | $85.1M (2024); 270; proprietary, 71 US + 94 foreign patents, 61 pending; $5.00/share, agreement 2024-09-25 | [sec.gov](https://www.sec.gov/Archives/edgar/data/1816613/000095017025046869/mkfg-20241231.htm) | supported | revenue was $85.1 million ... 270 full-time employees ... $5.00 per share in cash | Patent counts and the 2024-09-25 agreement date also on page. |
| 9 | B | `B/suse.json` | exit_events[3] (market cap) | May 2021 Frankfurt IPO at EUR 30; market cap EUR 5.05B | [unquote.com](https://www.unquote.com/dach/official-record/3023900/eqts-suse-lists-in-eur5bn-ipo) | supported | Suse's €5.05bn market capitalisation; 37.3 million shares listed at €30 apiece |  |
| 10 | G | `G/universal-robots-mir.json` | revenue_latest_usd | $308.295M (2025) | [sec.gov](https://www.sec.gov/Archives/edgar/data/97210/000119312526059002/R138.htm) | supported | Operating Segments \| Robotics ... Revenues 308,295 [$ thousands, Dec. 31, 2025 column] | Teradyne Robotics segment (UR + MiR); page does not name the brands. |
| 11 | F | `F/openfoam.json` | employees_latest | 5 | [openfoam.org](https://openfoam.org/news/funding-2026/) | supported | CFD Direct is a company of 5 people responsible for 1.6M lines of OpenFOAM C++ code |  |
| 12 | C | `C/deepseek.json` | license_history[1] | 2024: DeepSeek Model License (weights), MIT (code), commercial use allowed | [github.com](https://github.com/deepseek-ai/DeepSeek-V3) | supported | This code repository is licensed under the MIT License ... subject to the Model License | Commercial use stated; the Dec 2024 date is not on the page. |
| 13 | E | `E/emerald-cloud-lab.json` | founded_year; license_history[0] | 2010; 2014 launch as proprietary service (SLL, Command Center, Engine) | [en.wikipedia.org](https://en.wikipedia.org/wiki/Emerald_Cloud_Lab) | **partially supported** | Emerald Therapeutics was founded in 2010 ... launched this service in 2014 | Licence not discussed (no "proprietary"/"closed"; re-checked). Founding year supported. |
| 14 | J | `J/nous-research.json` | employees_latest | ~20 | [fortune.com](https://fortune.com/crypto/2025/04/25/paradigm-nous-research-crypto-ai-venture-capital-deepseek-openai-blockchain) | supported | Nous currently has a 20-odd-person team |  |
| 15 | I | `I/chai-1.json` | license_history[1]; relicensing_events[0] | 2024-11-27: Apache-2.0 (v0.4.0/0.4.1), from non-commercial Chai Discovery Community License | [github.com](https://github.com/chaidiscovery/chai-lab/releases) | supported | v0.4.0: Apache 2.0 license (commercial use) ... Update license to Apache 2.0 | Dated 27 Nov; prior licence not named on this page. |
| 16 | J | `J/weaviate.json` | relicensing_events[0] (features moved into wl/ Sep-Nov 2026) | 2026: BSD-3 core + proprietary Weaviate License in wl/ (namespaces 09-28 ... rebalance planner 11-23) | [api.github.com](https://api.github.com/repos/weaviate/weaviate/commits?path=wl&per_page=100) | supported | Move namespacing.Prefixing into wl/namespaces under the Weaviate License ... Move RebalancePlanner into wl/ directory to gate behind enterprise | All four dated moves found (three reads with offsets). Licence file added 2026-08-26. |
| 17 | D | `D/makerbot.json` | exit_events[0]; latest_value_usd | 2013 acquisition by Stratasys, $403M (all stock) | [sec.gov](https://www.sec.gov/Archives/edgar/data/0001517396/000110465913050451/a13-15347_1ex99d1.htm) | supported | The proposed merger has an initial value of $403 million | June 19, 2013; $84.60 close; earn-out of up to 2.38M shares and $201M also on page. |
| 18 | C | `C/deepseek.json` | license_history[4] | 2026: MIT (DeepSeek-V4-Pro) | [huggingface.co](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro) | supported | This repository and the model weights are licensed under the MIT License. |  |
| 19 | G | `G/velo3d.json` | founded_year; exit_events[0]; license_history[0] | 2014; SPAC merger with JAWS Spitfire closed 2021-09-29 ($155M PIPE, 21,758,148 earn-out shares); proprietary | [sec.gov](https://www.sec.gov/Archives/edgar/data/1825079/000162828022007442/velo-20211231.htm) | supported | Since our founding in 2014 ... 'Closing Date' means September 29, 2021 ... proprietary software platform | PIPE and earn-out match; Sapphire and Flow called proprietary. |
| 20 | G | `G/center-for-open-science.json` | license_history[0] | Apache-2.0; repo created 2013-05-21 | [api.github.com](https://api.github.com/repos/CenterForOpenScience/osf.io) | supported | "created_at": "2013-05-21T15:53:37Z" ... "spdx_id": "Apache-2.0" |  |
| 21 | I | `I/gnome.json` | relicensing_events[0] | CC BY 4.0 Materials Project to non-commercial, access-controlled GNoME subset (year null) | [docs.materialsproject.org](https://docs.materialsproject.org/materials-project-data-lakehouse/access-controlled-data) | supported | opting into using the GNoME dataset for non-commercial uses | Subset under "GNoME Database License and Terms of Use"; CC BY 4.0 starting point not on this page. |
| 22 | B | `B/gitlab.json` | exit_events[0] | 2021 Nasdaq IPO (GTLB) at $77; value $11B | [about.gitlab.com](https://about.gitlab.com/press/releases/2021-10-13-gitlab-announces-pricing-of-initial-public-offering/) | **partially supported** | at a public offering price of $77.00 per share | Oct 13, 2021, 10.4M shares; no valuation, so the $11B value_usd is not on the page. |
| 23 | J | `J/unsloth.json` | license_history[0]; license_history[2] | Apache-2.0 from initial commit 2023-11-29; Apache-2.0 + AGPL-3.0 (Studio) from 2026-03-12 | [api.github.com](https://api.github.com/repos/unslothai/unsloth/commits?path=LICENSE) | **partially supported** | "Initial commit" 2023-11-29 ... "Studio (#4237)" 2026-03-12 | Dates match; commit list cannot show licence names. It also shows a same-day "Revert" of #4237. |
| 24 | G | `G/carbon.json` | founded_year | 2013 | [en.wikipedia.org](https://en.wikipedia.org/wiki/Carbon_(company)) | supported | The company was founded in 2013 |  |
| 25 | G | `G/3d-systems.json` | latest_value_usd | $254.52M (2026-11-23) | [stockanalysis.com](https://stockanalysis.com/stocks/ddd/market-cap/) | supported | market cap or net worth of $254.52 million as of November 23, 2026 |  |
| 26 | B | `B/gitlab.json` | employees_latest | 2,582 (31 Jan 2026) | [res.cloudinary.com](https://res.cloudinary.com/about-gitlab-com/image/upload/v1783451395/bpjtji8h54dcrv6atsju.pdf) | supported | Total team members ... 2,582 [FY26 column, "as of Jan 31, 2026"] | WebFetch could not decode the PDF; read with pdftotext from the copy WebFetch saved. |
| 27 | G | `G/velo3d.json` | exit_events[1] | Dec 2024 change of control: $22.4M notes + $0.4M interest for 185,151,333 shares, 95% to Arrayed | [sec.gov](https://www.sec.gov/Archives/edgar/data/1825079/000149315224051999/ex99-1.htm) | supported | the Holder will hold 95% of Velo3D's issued and outstanding common stock | December 24, 2024; $22.4M, $369K interest and 185,151,333 shares on page. |
| 28 | C | `C/amazon-aws.json` | relicensing_events[0] | 2021: Elasticsearch/Kibana Apache-2.0 to SSPL / Elastic License; AWS fork OpenSearch | [elastic.co](https://www.elastic.co/blog/why-license-change-aws) | **partially supported** | AWS's behavior has forced us to take this step and we do not do so lightly. | Jan 19, 2021 change and motive confirmed; SSPL and OpenSearch absent, Elastic License only in an update note (re-checked). |
| 29 | J | `J/chroma.json` | license_history[0] | Apache-2.0; created 2022-10-05 | [api.github.com](https://api.github.com/repos/chroma-core/chroma) | supported | "created_at": "2022-10-05T17:58:44Z" ... "spdx_id": "Apache-2.0" |  |
| 30 | D | `D/framework-computer.json` | founded_year | 2020 | [en.wikipedia.org](https://en.wikipedia.org/wiki/Framework_Computer) | supported | In January 2020, the company was founded by Nirav Patel |  |
| 31 | D | `D/formlabs.json` | revenue_latest_usd | $250M (2025) | [formlabs.com](https://formlabs.com/company/press/formlabs-board-changes-dan-riccio/) | supported | with annual revenues surpassing $250 million | Release dated 2026-08-12 gives no year; the file itself says revenue_year rests on Wikipedia. |

## Summary rates (n = 30)

| Verdict | Count | Rate | Wilson 95% CI |
| --- | ---: | ---: | --- |
| Supported | 23 | 76.7% | 59.1% to 88.2% |
| Partially supported | 7 | 23.3% | 11.8% to 40.9% |
| Not supported | 0 | 0.0% | 0.0% to 11.4% |
| Supported or partially supported | 30 | 100.0% | 88.6% to 100.0% |
| Supported, strict variant | 18 | 60.0% | 42.3% to 75.4% |
| Unreachable | 0 | 0.0% | n/a (no replacements needed) |
| Skipped (PDF over 5 MB), excluded from n | 1 | n/a | n/a |

Supported rate: **23/30 = 76.7% (Wilson 95% CI 59.1% to 88.2%)**. The strict variant gives 18/30 = 60.0% (Wilson 95% CI 42.3% to 75.4%).

The seven partial verdicts fall into four patterns:

- **Derived value, cited to one component** (draw 5). `funding_total_usd` = $135M is the sum of three rounds, and the
  cited page gives only the $50M Series B.
- **Value taken from a different source than the one cited** (draws 4 and 22). Prusa's 1,144 staff: the cited article
  says "over 1,100". GitLab's $11B IPO valuation: the cited pricing release gives $77 a share and 10.4M shares but no
  valuation.
- **Characterisation inferred rather than stated** (draws 3 and 13). Figshare's 2012 "acquisition" by Digital Science:
  Wikipedia says Digital Science has supported it since 2012 and owns it, but no acquisition is described.
  Emerald Cloud Lab's "proprietary" licence: the page never discusses licensing.
- **Page dates the event but does not name the licences** (draws 23 and 28). A commit list can show only dates. Elastic's
  2021 AWS post names neither SSPL nor OpenSearch.

Numeric scalar fields were supported in 9 of 11 pairs. Pairs involving `license_history`, `relicensing_events` or
`exit_events` were supported in 14 of 19. The partial verdicts are concentrated in values that were derived or
inferred, not in mis-transcribed numbers. Every value that was on the page matched the file exactly or to rounding:
no wrong numbers turned up.

**Limitations.** With n = 30 the interval is wide. Verdicts rest on quotes returned by WebFetch's summarising model,
so absence verdicts were re-checked and the PDF was read directly, but a summariser error in either direction remains
possible. The five lenient calls are listed under the strict variant. Free-text fields were outside the frame.

## Breakdown by group

| Group | Eligible sources in frame | Sampled | Supported | Partial | Not supported | Supported rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 113 | 0 | 0 | 0 | 0 | n/a |
| B | 106 | 4 | 3 | 1 | 0 | 3/4 |
| C | 147 | 4 | 3 | 1 | 0 | 3/4 |
| D | 88 | 5 | 4 | 1 | 0 | 4/5 |
| E | 52 | 1 | 0 | 1 | 0 | 0/1 |
| F | 46 | 1 | 1 | 0 | 0 | 1/1 |
| G | 79 | 9 | 7 | 2 | 0 | 7/9 |
| I | 8 | 2 | 2 | 0 | 0 | 2/2 |
| J | 111 | 4 | 3 | 1 | 0 | 3/4 |
| **All** | **750** | **30** | **23** | **7** | **0** | **23/30** |

Group counts are tiny and follow the uniform draw: G got 9 draws from 79 eligible sources, and A got none from 113.
Read the group rows as a description of this sample. They say nothing reliable about differences between groups.

## Recommendations

1. **Mark derived values.** Write `funding_total_usd (component: $50M Series B)` in `supports`, or add a derivation
   note giving the arithmetic, such as "sum of 2022 $50M + 2023 $40M + 2026 $45M", and cite every round.
2. **Cite the page that states the number.** Where a value came from elsewhere (GitLab's $11B, Prusa's 1,144), add
   that source for the field. Narrow the existing citation to what it shows, for example
   `exit_events[0] (price, date)`.
3. **Narrow `supports` for dating-only sources.** GitHub commit lists show dates, not licence names: use
   `license_history[0] (date)`, and pair them with the LICENSE file or the licence announcement.
4. **Label inferences.** Characterisations such as "Proprietary" or "acquisition" with no source that states them
   should say so, for example "inferred: closed commercial service; no licence statement found", instead of resting
   on a citation that does not say it.
5. **Add machine-readable alternatives for heavy sources.** WebFetch cannot read the Alphabet annual report PDF
   (over 10 MB); the 10-K HTML or an earnings release would make the value checkable. GitLab's FY26 data-table PDF
   needed local text extraction.
6. **Make `supports` structured.** Field paths in one key and qualifiers in another would make the frame exact. Now it
   has to be pulled out of free text by regex. 9 of the 750 sources in the frame say in their own `supports`
   that they were "not fetched", and should be re-verified or flagged.
7. **If group-level rates matter,** re-run stratified, for example 10 pairs per group, and audit the free-text fields
   (`risk_events`, `origin_detail`) separately. This sample does not cover them.
