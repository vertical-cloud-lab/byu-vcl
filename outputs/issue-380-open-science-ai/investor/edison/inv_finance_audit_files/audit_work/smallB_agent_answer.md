## Files Ready for Analysis

| File | Description | Format | Size |
|---|---|---|---:|
| `financial_disclosures.csv` | Analysis-ready data: 11 companies, exact requested columns | CSV | 2,801 bytes |
| `evidence.json` | Supporting search results, fetched pages, queries, URLs and source metadata | JSON | 871,909 bytes |
| `sources.bib` | Supporting bibliography: 29 sources | BibTeX | 7,233 bytes |
| `methodology.json` | Supporting definitions, uncertainties and validation results | JSON | 2,796 bytes |
| `reproduce_retrieval.py` | Supporting script to repeat the recorded searches and fetches | Python | 999 bytes |

**Completed: 11 rows. Status counts: 10 private; 1 shut_down; 0 acquired, listed or unknown.** Research cutoff: **2026-11-26**. Each company received three to five searches or fetches. Nothing was uploaded.

Blank financial fields mean undisclosed or unverified, not zero. `ever_1b=no` follows your small-company screening rule; it does not establish a historical valuation ceiling. OtterMind remains `unknown` on that measure because its corporate perimeter is unresolved.

```csv
github_orgs,entity,status,status_date,acquirer,exit_value_usd,exit_source,total_funding_usd,funding_asof,funding_source,last_valuation_usd,valuation_date,valuation_source,peak_value_usd,peak_value_date,peak_source,ever_1b,notes
Textualize,Textualize,shut_down,2025-05,,,,,,https://www.willmcgugan.com/blog/tech/post/weeknotes/,,,,,,,no,Wind-down announced May 2025; date reflects announcement. Rich and Textual continue as community projects. Funding amount undisclosed.
OtterMind,OtterMind,private,,,,,,,,,,,,,,unknown,Active Singapore company. Chat2DB-linked Chinese financing cannot be securely attributed to OtterMind; amounts undisclosed or imprecise.
heroui-inc,HeroUI Inc.,private,,,,,,,https://blog.epakon.com/uncovering-opportunities-a-look-back-and-ahead-at-a-thrilling-year-in-vc-ac7b1d446fda,,,,,,,no,Formerly NextUI; active YC S24 company. Epakon confirms pre-seed investment without amount; conflicting database totals excluded.
chatwoot,Chatwoot,private,,,,,1600000,2021-08,https://www.chatwoot.com/hc/handbook/articles/investors-27,,,,,,,no,Company discloses one seed round including Y Combinator; database totals conflict. No later disclosed equity round found.
typst,Typst GmbH,private,,,,,,,https://www.ewor.com/startups/typst,,,,,,,no,"Active, financially sustainable company. EWOR affiliation has no disclosed investment amount; engineer sponsorship is not equity funding."
nanocoai,NanoCo,private,,,,,12000000,2026-05,https://www.linkedin.com/posts/nanoclaw-ai_today-were-announcing-nanoco-creators-of-activity-7462949209873235969-gMOs,,,,,,,no,Seed announced May 2026. Rejected acquisition offer is neither an exit nor a disclosed post-money valuation.
usablica,usablica (Intro.js),private,,,,,,,,,,,,,,no,Commercial licences remain available under Usablica branding. Corporate incorporation and ownership structure unverified; no disclosed equity financing found.
LiteFold,LiteFold,private,,,,,,,https://yourstory.com/2026/05/litefold-biotech-startup-using-proprietary-ai-speed-up-drug-discovery,,,,,,,no,Offscript-led funding amount undisclosed; approximately USD 23000 grants excluded. News inconsistently describes private and friends-and-family rounds; product shifted proprietary.
aipoch,AIPOCH,private,,,,,,,,,,,,,,no,"Singapore research-software company; public product launch October 2026. No disclosed equity amount, valuation, acquisition, or shutdown found."
meshpro,MeshPro,private,,,,,,,,,,,,,,no,"MeshPro is a Monday Tech product, not a verified separate corporation. Paid licences active; no financing or acquisition disclosure found."
borneo-iot,Yunnan BinaryStars Technologies,private,,,,,,,,,,,,,,no,Operating aquarium hardware/software business; company site and March 2026 app terms identify operator. No disclosed financing or valuation found.
```

## Company evidence, exact excerpts and conflicts

### 1. Textualize

**Status: shut_down.** The founder's [May 2025 announcement](https://textual.textualize.io/blog/2025/05/07/the-future-of-textualize/) states: “we weren't able to find a shared problem or pain-point to build a viable business around. Which is why Textualize, the company, will be wrapping up in the next few weeks.” It separately states: “Textual will live on as an Open Source project.” Continuing repository activity therefore does not establish continuing company operations.

**Financing:** The founder's [Weeknotes](https://www.willmcgugan.com/blog/tech/post/weeknotes/) states: “The investment for Textualize landed at the end of last year, just before Christmas.” No amount is supplied, so funding remains blank.

**Date conflict:** [PitchBook](https://pitchbook.com/profiles/company/510364-36) dates its “Out of Business” event to February 2026. The CSV instead uses the founder's operational wind-down announcement month. The exact completion date and legal dissolution date were not established.

### 2. OtterMind

**Status: private, operating; corporate attribution requires caution.** The [GitHub organization](https://github.com/ottermind) connects OtterMind with Chat2DB and the OtterMind website. The company's [About page](https://ottermind.ai/about) states: “Ottermind is operated by the Singapore-registered company listed here,” identifying **OTTERMIND PTE. LTD.** Its current site markets an operating AI-agent workspace.

**Financing conflict:** The [36Kr Chat2DB profile](https://pitchhub.36kr.com/project/3173327576230918) instead identifies the Chinese legal entity **爱獭科技（杭州）有限公司**, translated there as Love Otter Technology (Hangzhou) Co., Ltd. Its financing table lists angel, Series A and Series A+ events, with the latest in May 2026, but the amount field is **“未透露”**, meaning “undisclosed.” I did not establish whether these financings belong to the Singapore entity, an affiliate, or another corporate perimeter. No amount or valuation was transferred into OtterMind's row.

### 3. HeroUI Inc.

**Status: private, operating.** [Y Combinator's company page](https://www.ycombinator.com/companies/heroui) says “Status: Active” and identifies Junior Garcia as “Founder and CEO of HeroUI (formerly NextUI).”

**Verified investment, undisclosed amount:** Investor Epakon's [annual review](https://blog.epakon.com/uncovering-opportunities-a-look-back-and-ahead-at-a-thrilling-year-in-vc-ac7b1d446fda) states: “In 2023, Epakon led NextUI’s pre-seed round.” It does not give the investment amount.

**Excluded conflicting figures:** The search-index financial panel associated with the [LinkedIn profile](https://linkedin.com/company/heroui) says “Total Funding: USD 425,000,” whereas [aVenture](https://aventure.vc/companies/heroui-san-francisco-ca-us/fundraising) says “Disclosed Funding$500,000.” Neither was established as an authoritative company-specific funding announcement. I also did not substitute Y Combinator's generic investment terms. Total funding remains blank.

### 4. Chatwoot

**Status: private, operating.** Its [current commercial website](https://www.chatwoot.com/) offers the hosted customer-support product and enterprise services.

**Accepted funding: USD 1,600,000.** The company's [investor handbook](https://www.chatwoot.com/hc/handbook/articles/investors-27) states: “We raised a $1.6M seed round from Goat Capital, Uncorrelated Ventures & YCombinator.” [VentureBeat's announcement](https://venturebeat.com/business/chatwoot-challenges-zendesk-with-open-source-customer-engagement-platform), dated August 2021, independently says Chatwoot “today announced it has raised $1.6 million in seed funding.” This establishes `funding_asof=2021-08`.

**Conflict:** [PitchBook](https://pitchbook.com/profiles/company/227991-43) says: “Chatwoot has raised $1.91M,” and lists a different seed-round amount. I preferred the company's explicit disclosure. The CSV total represents the disclosed company-backed round, not independently audited lifetime proceeds. No generic accelerator cheque was added separately because the company already includes Y Combinator among the round's investors.

### 5. Typst GmbH

**Status: private, operating.** Its [current About page](https://typst.app/about/) describes the company and commercial platform. Founder Martin Haug's [company update](https://typst.app/blog/2025/future/) states: “As a company, we have grown financially sustainable over the past two years.”

**Financing:** [EWOR's Typst profile](https://www.ewor.com/startups/typst) identifies Martin Haug as a fellow and describes the business, but discloses no investment amount. Typst's [statement about Posit](https://www.linkedin.com/posts/typst_posit-and-typst-posit-activity-7342823256472584192-pyUB) says: “Their commitment to funding one of our full-time engineers means the world to us.” That establishes development sponsorship, not a disclosed equity round or valuation. No numerical equity total was verified.

### 6. NanoCo

**Status: private, operating, not acquired.** The [current company website](https://www.nanoco.ai/) offers enterprise AI assistants and early access.

**Accepted funding: USD 12,000,000.** The [company's announcement](https://www.linkedin.com/posts/nanoclaw-ai_today-were-announcing-nanoco-creators-of-activity-7462949209873235969-gMOs) states: “Today we're announcing NanoCo (creators of NanoClaw), our enterprise offering from the team behind NanoClaw, and a $12M seed round led by Valley Capital Partners.” [TechCrunch](https://techcrunch.com/2026/05/20/nanoclaw-creator-turns-down-20m-buyout-offer-raises-12m-seed-instead/), dated May 2026, confirms an “oversubscribed $12 million seed round.”

**Important exclusion:** TechCrunch reports “a roughly $20 million acquisition offer” that the founders “declined.” An unconsummated offer, reportedly including employment arrangements, is neither an exit value nor a disclosed post-money financing valuation. All valuation and exit fields remain blank.

### 7. usablica (Intro.js)

**Status: private commercial operation, with legal-entity uncertainty.** The [official website](https://introjs.com/) states: “Free for open-source projects. A once-off payment for commercial ones.” Its footer identifies Usablica. This supports continuing paid licensing rather than shutdown.

No equity amount, valuation or acquisition announcement was located. The incorporation jurisdiction and exact legal entity behind the brand were not independently established; `private` describes the continuing independent commercial operation, not a verified corporate-registration finding.

### 8. LiteFold

**Status: private, operating.** The [current website](https://www.litefold.ai/) identifies “LiteFold Inc., a Delaware C-Corporation” and markets its private AI platform.

**Undisclosed equity; grants excluded.** [YourStory](https://yourstory.com/2026/05/litefold-biotech-startup-using-proprietary-ai-speed-up-drug-discovery) states: “The startup recently raised an undisclosed amount in a private funding round led by Offscript VC.” It continues: “It has also secured about $23,000 in grants from Emergent Ventures, Dr Aniruddha Malpani’s 3F VC, and also an undisclosed friends and family round from the Boston-based OffScript VC.”

The wording does not clearly establish whether the private and friends-and-family descriptions refer to separate transactions. I did not double-count them or enter grants as equity. The same article states: “Sannigrahi later shifted it into a proprietary platform after recognising the commercial potential of the technology,” which is relevant to the supplied open-source classification.

### 9. AIPOCH

**Status: private, operating.** Its [company-issued PR Newswire release](https://www.prnewswire.com/news-releases/aipoch-launches-open-science-making-research-easier-to-follow-learn-from-and-share-with-science-packages-302908207.html), dated October 2026 and issued from Singapore, states: “AIPOCH today announced the formal public release of AIPOCH Open-Science.”

The release establishes recent operations but discloses no equity financing, valuation or acquisition price. No such financial disclosure was located in the bounded search.

### 10. MeshPro

**Status: private commercial operation; supplied entity is a product name.** [Monday Tech's official documentation](https://mondaytech.com/meshpro/getting-started/) states: “MeshPro is a collection of Python libraries and command-line tools for mesh I/O and mesh manipulation.” It adds: “Full access to all MeshPro functionality requires a license.”

The [optimesh repository](https://github.com/meshpro/optimesh) directs commercial users to **support@mondaytech.com**. This supports ongoing commercialization under Monday Tech, but not a separately incorporated company called MeshPro or a completed acquisition. No funding amount or valuation was located. I retained the supplied entity label and flagged the identity issue rather than inventing a buyer or acquisition event.

### 11. Yunnan BinaryStars Technologies

**Status: private, operating.** The company's [About page](https://www.binarystarstech.com/en/about/) describes its integrated hardware and software engineering business and links the Borneo-IoT product line. The [Borneo-IoT app terms](https://www.borneoiot.com/app/tos/), updated March 2026, identify the service as “operated by Yunnan BinaryStars Technologies, Co., Ltd.”

No disclosed equity amount, valuation or acquisition price was found. The terms retain some unfilled template placeholders elsewhere; I used only their explicit operator identification, corroborated by the company website.

## Uncertain rows and interpretation

The principal uncertainties are **OtterMind**'s corporate relationship to the Chinese Chat2DB business; **HeroUI**'s conflicting unsupported funding totals; **Usablica**'s and **MeshPro**'s legal-entity identities; **LiteFold**'s ambiguous round descriptions; and **Textualize**'s exact cessation date. Chatwoot's reported database total also conflicts with its own disclosure. None of these uncertainties was resolved by inventing a number.

No qualifying post-money valuation, completed acquisition price, or first-day public-market capitalization was verified for these companies. Consequently, every valuation and exit-value field is blank. No currency conversion was necessary for the accepted funding figures.

## Saved files and reproduction

All files below concern the public-disclosure snapshot as of 2026-11-26; genome builds and scientific dataset releases are not applicable.

- `/workspace/downloads/oss_financial_disclosures/financial_disclosures.csv`: Analysis-ready curated data. Sources are the company, investor and news URLs above. Transformations were entity matching, status classification, exclusion of grants and uncompleted offers, and conversion of explicit USD million amounts into integer USD digits. Validated for 11 rows, exact columns, integer-or-blank financial fields and notes of at most 25 words.
- `/workspace/downloads/oss_financial_disclosures/evidence.json`: Supporting original tool-returned search and fetched-page text, all retrieval queries and URLs, and used-source metadata. Retrieval used `e14c.web.web_search` with five results per query and `e14c.web.fetch_parsed_page` on the recorded HTTPS URLs. Results were serialized without financial estimation.
- `/workspace/downloads/oss_financial_disclosures/sources.bib`: Supporting hand-curated bibliographic metadata for the 29 sources cited below. Source URLs and publication dates are retained when available.
- `/workspace/downloads/oss_financial_disclosures/methodology.json`: Supporting research parameters, screening definitions, conflicts, call counts and validation findings. Derived from the saved evidence and curation decisions.
- `/workspace/downloads/oss_financial_disclosures/reproduce_retrieval.py`: Repeats the exact retrieval calls recorded in `evidence.json`; run with `python /workspace/downloads/oss_financial_disclosures/reproduce_retrieval.py`. It does not substitute automated extraction for the documented manual financial judgments.

The same bibliography was also saved through `save_citation` to `/workspace/citations/default_project/08d1321c-1746-402b-bad9-7f630a43bf59.bib`. Complete bibliography follows so the caller does not need filesystem access.

## Full BibTeX

```bibtex
@misc{textualize_shutdown,
  author = {McGugan, Will},
  title = {{The future of Textualize}},
  organization = {Textual},
  date = {2025-05-07},
  url = {https://textual.textualize.io/blog/2025/05/07/the-future-of-textualize/},
  urldate = {2026-11-26}
}
@misc{textualize_funding,
  author = {McGugan, Will},
  title = {{Weeknotes}},
  date = {2022-01-14},
  url = {https://www.willmcgugan.com/blog/tech/post/weeknotes/},
  urldate = {2026-11-26}
}
@misc{textualize_database,
  author = {{PitchBook}},
  title = {{Textualize 2026 Company Profile: Valuation, Funding and Investors}},
  url = {https://pitchbook.com/profiles/company/510364-36},
  urldate = {2026-11-26}
}
@misc{ottermind_github,
  author = {{OtterMind}},
  title = {{OtterMind GitHub organization}},
  organization = {GitHub},
  url = {https://github.com/ottermind},
  urldate = {2026-11-26}
}
@misc{ottermind_about,
  author = {{Ottermind}},
  title = {{About Ottermind}},
  url = {https://ottermind.ai/about},
  urldate = {2026-11-26}
}
@misc{chat2db_financing,
  author = {{36Kr}},
  title = {{Chat2DB project profile}},
  url = {https://pitchhub.36kr.com/project/3173327576230918},
  urldate = {2026-11-26}
}
@misc{heroui_yc,
  author = {{Y Combinator}},
  title = {{HeroUI: The UI framework for AI agents and developers to build beautiful apps}},
  url = {https://www.ycombinator.com/companies/heroui},
  urldate = {2026-11-26}
}
@misc{heroui_epakon,
  author = {Salas, Diego},
  title = {{Uncovering Opportunities: A Look Back (and Ahead) at a Thrilling Year in VC}},
  organization = {Epakon Capital},
  date = {2024-01-22},
  url = {https://blog.epakon.com/uncovering-opportunities-a-look-back-and-ahead-at-a-thrilling-year-in-vc-ac7b1d446fda},
  urldate = {2026-11-26}
}
@misc{heroui_linkedin,
  author = {{HeroUI}},
  title = {{HeroUI (YC S24) company profile; search-index financial panel}},
  organization = {LinkedIn},
  note = {Indexed financial figures were not verified as a company announcement and were excluded},
  url = {https://linkedin.com/company/heroui},
  urldate = {2026-11-26}
}
@misc{heroui_database,
  author = {{aVenture}},
  title = {{HeroUI fundraising history}},
  note = {Database amount excluded from accepted funding total},
  url = {https://aventure.vc/companies/heroui-san-francisco-ca-us/fundraising},
  urldate = {2026-11-26}
}
@misc{chatwoot_investors,
  author = {{Chatwoot}},
  title = {{Investors}},
  date = {2024-05-21},
  note = {Page last-updated date},
  url = {https://www.chatwoot.com/hc/handbook/articles/investors-27},
  urldate = {2026-11-26}
}
@misc{chatwoot_seed,
  author = {Sawers, Paul},
  title = {{Chatwoot challenges Zendesk with open source customer engagement platform}},
  organization = {VentureBeat},
  date = {2021-08-09},
  url = {https://venturebeat.com/business/chatwoot-challenges-zendesk-with-open-source-customer-engagement-platform},
  urldate = {2026-11-26}
}
@misc{chatwoot_current,
  author = {{Chatwoot}},
  title = {{Chatwoot official website}},
  url = {https://www.chatwoot.com/},
  urldate = {2026-11-26}
}
@misc{chatwoot_database,
  author = {{PitchBook}},
  title = {{Chatwoot 2026 Company Profile: Valuation, Funding and Investors}},
  note = {Database total conflicts with company disclosure and was excluded},
  url = {https://pitchbook.com/profiles/company/227991-43},
  urldate = {2026-11-26}
}
@misc{typst_current,
  author = {{Typst}},
  title = {{About Typst}},
  url = {https://typst.app/about/},
  urldate = {2026-11-26}
}
@misc{typst_sustainable,
  author = {Haug, Martin},
  title = {{Two years and counting: How we are building the future of technical writing}},
  organization = {Typst},
  date = {2025-08-20},
  url = {https://typst.app/blog/2025/future/},
  urldate = {2026-11-26}
}
@misc{typst_ewor,
  author = {{EWOR}},
  title = {{EWOR Startup - Typst}},
  url = {https://www.ewor.com/startups/typst},
  urldate = {2026-11-26}
}
@misc{typst_sponsorship,
  author = {{Typst}},
  title = {{We are grateful to Posit for their continued support of Typst}},
  organization = {LinkedIn},
  date = {2025-06-23},
  url = {https://www.linkedin.com/posts/typst_posit-and-typst-posit-activity-7342823256472584192-pyUB},
  urldate = {2026-11-26}
}
@misc{nanoco_seed,
  author = {{NanoClaw}},
  title = {{Today we are announcing NanoCo and a 12M dollar seed round}},
  organization = {LinkedIn},
  date = {2026-05-20},
  url = {https://www.linkedin.com/posts/nanoclaw-ai_today-were-announcing-nanoco-creators-of-activity-7462949209873235969-gMOs},
  urldate = {2026-11-26}
}
@misc{nanoco_offer,
  author = {Bort, Julie},
  title = {{NanoClaw creator turns down 20M dollar buyout offer, raises 12M dollar seed instead}},
  organization = {TechCrunch},
  date = {2026-05-20},
  url = {https://techcrunch.com/2026/05/20/nanoclaw-creator-turns-down-20m-buyout-offer-raises-12m-seed-instead/},
  urldate = {2026-11-26}
}
@misc{nanoco_current,
  author = {{NanoCo}},
  title = {{NanoCo: The AI assistant for work}},
  url = {https://www.nanoco.ai/},
  urldate = {2026-11-26}
}
@misc{introjs_current,
  author = {{Usablica}},
  title = {{User Onboarding and Product Walkthrough Library - Intro.js}},
  url = {https://introjs.com/},
  urldate = {2026-11-26}
}
@misc{litefold_funding,
  author = {Biswas, Tunir},
  title = {{Meet LiteFold, a biotech startup using proprietary AI to speed up drug discovery}},
  organization = {YourStory},
  date = {2026-05-13},
  url = {https://yourstory.com/2026/05/litefold-biotech-startup-using-proprietary-ai-speed-up-drug-discovery},
  urldate = {2026-11-26}
}
@misc{litefold_current,
  author = {{LiteFold}},
  title = {{LiteFold: Private AI for Drug Discovery and Scientific R and D}},
  url = {https://www.litefold.ai/},
  urldate = {2026-11-26}
}
@misc{aipoch_launch,
  author = {{AIPOCH}},
  title = {{AIPOCH Launches Open-Science, Making Research Easier to Follow, Learn From, and Share with .science Packages}},
  organization = {PR Newswire},
  date = {2026-10-14},
  url = {https://www.prnewswire.com/news-releases/aipoch-launches-open-science-making-research-easier-to-follow-learn-from-and-share-with-science-packages-302908207.html},
  urldate = {2026-11-26}
}
@misc{meshpro_project,
  author = {{MeshPro}},
  title = {{meshpro/optimesh}},
  organization = {GitHub},
  url = {https://github.com/meshpro/optimesh},
  urldate = {2026-11-26}
}
@misc{meshpro_product,
  author = {{Monday Tech}},
  title = {{MeshPro: Getting started}},
  url = {https://mondaytech.com/meshpro/getting-started/},
  urldate = {2026-11-26}
}
@misc{binarystars_about,
  author = {{Yunnan BinaryStars Technologies}},
  title = {{About BinaryStars}},
  url = {https://www.binarystarstech.com/en/about/},
  urldate = {2026-11-26}
}
@misc{borneo_terms,
  author = {{Yunnan BinaryStars Technologies}},
  title = {{Borneo-IoT Aqua Pro Terms of Service}},
  date = {2026-03-01},
  note = {Terms last-updated date},
  url = {https://www.borneoiot.com/app/tos/},
  urldate = {2026-11-26}
}
```