## Files Ready for Analysis

| File | Description | Format | Size |
|---|---|---|---:|
| `financial_disclosures.csv` | Analysis-ready rows in the exact requested schema | CSV | 2,499 bytes |
| `evidence.json` | Supporting source extracts, search results, currency data, and caveats | JSON | 1,089,057 bytes |
| `sources.bib` | Complete supporting bibliography | BibTeX | 5,325 bytes |
| `provenance.json` | Supporting source and file manifest | JSON | 9,700 bytes |
| `retrieve.py` | Reproduction script with the reviewed snapshot embedded | Python | 13,283 bytes |

**Completed: 10 rows. Status counts: 9 private, 1 acquired, 0 listed, 0 shut down, 0 unknown.** Research cutoff: **2026-11-26**. The complete CSV and bibliography are reproduced below; no filesystem access is required to use this answer.

### Saved-file provenance

- `/workspace/downloads/oss_financial_disclosures/financial_disclosures.csv`: The ten reviewed company rows. Sources are the company-specific URLs below. Transformations include manual entity resolution, one GBP-to-USD conversion, and an explicitly approximate Bruno funding month. Version: reviewed 2026-11-26 snapshot.
- `/workspace/downloads/oss_financial_disclosures/evidence.json`: Source text from the URLs below, web-search queries and results, direct Anki HTML extraction, and the exchange-rate response. Searches requested five results per query. Source text was consolidated without discarding the intermediate evidence. Version: 2026-11-26 snapshot.
- `/workspace/downloads/oss_financial_disclosures/sources.bib`: Citation metadata for the 24 sources below, with access date 2026-11-26. No financial transformations.
- `/workspace/downloads/oss_financial_disclosures/provenance.json`: Locally generated manifest identifying source URLs, retrieval parameters, transformations, file sizes, and checksums. Version: 2026-11-26 snapshot.
- `/workspace/downloads/oss_financial_disclosures/retrieve.py`: Locally authored reproduction script using `e14c.web` and `httpx.AsyncClient`. It repeats the recorded queries and fetches and writes the manually reviewed CSV; it does not automatically reinterpret later disclosures.
- `/workspace/citations/default_project/ddd0f559-7ce3-4b14-bb21-d0beeb9bf66a.bib`: Citation-library copy saved through `save_citation`, containing the same source metadata. Size: 5,326 bytes.

## Full CSV

```csv
github_orgs,entity,status,status_date,acquirer,exit_value_usd,exit_source,total_funding_usd,funding_asof,funding_source,last_valuation_usd,valuation_date,valuation_source,peak_value_usd,peak_value_date,peak_source,ever_1b,notes
datalab-org,datalab industries ltd,private,,,,,,,,,,,,,,no,Active UK consultancy and managed-hosting company. No disclosed equity financing or valuation located.
ankitects,"Anki Software, LLC (Ankitects)",acquired,2026-02,AnkiHub,,https://forums.ankiweb.net/t/regarding-recent-events/74723,,,,,,,,,,no,AnkiHub took over operations; founder confirms installment payments. Price undisclosed; transaction structure and legal-entity scope unverified. Previously self-funded.
notable,Notable (Fabio Spampinato),private,,,,,,,,,,,,,,no,Founder-led app remains available. No disclosed financing located. UK legal-entity linkage and recent development activity remain unverified.
sinaptik-ai,Sinaptik (PandasAI),private,,,,,1100000,2023-09,https://blog.pandas-ai.com/pandasai-raised-a-1-1m-round-led-by-runa-capital/,,,,,,,no,Confirmed disclosed minimum; additional Y Combinator investment unquantified in company-specific sources. Company calls round seed; news calls it pre-seed.
VectifyAI,Vectify AI,private,,,,,1421750,2025-03,https://www.thebaehq.com/news/vectify-ai-raises-1-1m-to-automate-document-and-financial-data-analysis,,,,,,,no,Reported £1.1m; USD conversion uses ECB 2025-03-21 GBP/USD 1.2925. Later aggregator rounds excluded; no primary amount verified.
usebruno,Bruno Software Inc,private,,,,,3000000,2025-08,https://blog.usebruno.com/the-funding-announcement-we-never-made,,,,,,,no,Funding announced August 2026; round dated approximately August 2025 from 'about a year ago.' Valuation undisclosed.
marmelab,marmelab,private,,,,,,,,,,,,,,no,"Company explicitly described itself as self-funded, with no investors or debt. Disclosed react-admin revenue is not financing or valuation."
BruceDevices,Bruce Devices,private,,,,,,,,,,,,,,no,Active firmware project selling branded hardware. Formal incorporation and ownership unverified; no disclosed funding or valuation located.
go-gitea,Gitea Ltd / CommitGo,private,,,,,,,,,,,,,,no,"Commercial operator CommitGo, Inc.; Gitea Limited received founder-held trademarks, not an external acquisition. No verified funding amount located."
GrapesJS,GrapesJS,private,,,,,,,,,,,,,,no,"Commercial company is Grapes Studio Inc., backed by Open Core Ventures. Investment confirmed, amount undisclosed; no valuation located."
```

### Interpretation and uncertainty

Blank financial fields mean **no qualifying amount was verified**, not zero. No qualifying valuation was found for any company. The `ever_1b=no` entries use the study's allowance for clearly small companies without disclosed valuations; they are not claims that a comprehensive valuation history exists.

The principal uncertainties are **Anki's legal transaction structure and closing date; Notable's recent development and corporate linkage; PandasAI's complete funding total; Vectify's secondary-source funding report; Bruno's approximate round month; and Bruce's formal incorporation**.

## Company evidence, exact excerpts, and conflicts

### 1. datalab-org — datalab industries ltd

**Status: private and operating.** The [company website](https://datalab.industries/) describes itself as “The open source scientific software and data consultancy” and offers “Managed hosting of datalab instances.” [Companies House](https://find-and-update.company-information.service.gov.uk/company/15704476) identifies DATALAB INDUSTRIES LTD as “Active” and a “Private limited Company.”

No qualifying equity-funding or valuation disclosure was located. Academic project support and consultancy income were not treated as equity financing.

### 2. ankitects — Anki Software, LLC (Ankitects)

**Status: acquired by AnkiHub; the business remains operating.** The [February 2, 2026 announcement](https://forums.ankiweb.net/t/ankis-growing-up/68610) states:

> “I ended up suggesting to them that we look into gradually transitioning business operations and open source stewardship over”

The same discussion states:

> “Both Anki and AnkiHub are entirely self-funded.”

Crucially, the founder's [November 25, 2026 update](https://forums.ankiweb.net/t/regarding-recent-events/74723) confirms a paid arrangement:

> “the deal I made with AnkiHub requires them to pay me over time.”

It also refers to “instalments to me.” No acquisition consideration is disclosed. `2026-02` is the public transition-announcement month, **not a verified legal closing date**. The evidence supports a paid operating-business transfer but does not establish whether shares, assets, or another contractual structure were used, nor whether the input LLC name precisely identifies the transferred entity.

### 3. notable — Notable (Fabio Spampinato)

**Status: provisionally private and operating.** The [official website](https://notable.app/) continues to provide desktop downloads and describes its commercial plans:

> “The web app will require paying for a subscription to use”

The [Companies House record for NOTABLE TECHNOLOGIES LTD](https://find-and-update.company-information.service.gov.uk/company/12371038) says “Active” and “Private limited Company.” However, the official app page inspected did not establish its legal connection to that entity. Its continuing availability is stronger evidence than its undated statements about future development; recent development activity remains unverified.

No qualifying financing or valuation disclosure was located. Unrelated companies named Notable were excluded.

### 4. sinaptik-ai — Sinaptik (PandasAI)

**Status: private and operating.** The [Y Combinator company profile](https://www.ycombinator.com/companies/pandasai) labels PandasAI “Active” and identifies its batch as “Winter 2024.”

The [company funding announcement](https://blog.pandas-ai.com/pandasai-raised-a-1-1m-round-led-by-runa-capital/) states:

> “PandasAI has raised $1.1 million in seed funding led by Runa Capital!”

[Tech.eu, September 29, 2023](https://tech.eu/2023/09/29/pandasai-raises-11m-in-pre-seed-round-for-ai-powered-data-analysis), reports:

> “has raised $1.1 million in a Pre-Seed funding round.”

Thus, **1100000 is a confirmed disclosed minimum**, not a verified complete lifetime total. The company blog is dated October 7, but contemporaneous reporting establishes September as the announcement month. The company calls the round seed, whereas Tech.eu calls it pre-seed.

An [August 2024 founder interview](https://www.future-of-computing.com/pandasai-shaping-the-future-of-conversational-data-analysis/) repeats the earlier financing and confirms participation in Y Combinator. No company-specific amount for that additional investment was verified. I did not infer funding or valuation from standard accelerator terms or conflicting aggregator totals.

### 5. VectifyAI — Vectify AI

**Status: private and operating.** The [official PageIndex company page](https://pageindex.ai/about) states:

> “PageIndex is built and operated by Vectify AI.”

It identifies the operator as Vectify AI Limited, registered in England and Wales.

[Bae HQ, March 21, 2025](https://www.thebaehq.com/news/vectify-ai-raises-1-1m-to-automate-document-and-financial-data-analysis), reports:

> “Vectify AI has raised £1.1 million”

**This is lower-confidence, reported funding, not a verified company or investor announcement.** Bae HQ cites Crunchbase as its underlying source. The [Dealroom page](https://app.dealroom.co/companies/pageindex) instead lists “Mar 2025*” at “£1.2m” and “Jul 2025*” at “£300k.” Those conflicting aggregator entries and associated valuations were not adopted or added.

The [Frankfurter response restricted to the European Central Bank provider](https://api.frankfurter.dev/v2/rates?date=2025-03-21&base=GBP&quotes=USD&providers=ecb&expand=providers) returns:

> `"date":"2025-03-21","base":"GBP","quote":"USD","rate":1.2925`

Conversion: **GBP 1,100,000 × 1.2925 = USD 1,421,750**. The provider filter and historical-date parameters follow the [documented API](https://frankfurter.dev/). This is the converted reported round, not a verified complete funding history.

### 6. usebruno — Bruno Software Inc

**Status: private and operating.** The founder's [August 11, 2026 announcement](https://blog.usebruno.com/the-funding-announcement-we-never-made) states:

> “About a year ago, Bruno raised $3M, and we didn't announce it at the time.”

It names Silverton Partners and describes continued team and product investment. The page footer identifies Bruno Software Inc.

The CSV records **3000000**. `funding_asof=2025-08` is **approximate**, inferred from “about a year ago”; it is not an independently verified closing month. No valuation or additional disclosed round was verified.

### 7. marmelab — marmelab

**Status: private and operating.** In [its November 2023 account](https://marmelab.com/blog/2023/11/08/open-source-profit-1.html), the company states:

> “We've never sought investors. We're self-funded and we have no debt.”

It also says:

> “We've generated almost €1M with react-admin”

That figure is **revenue, not financing or company valuation**, and was excluded. The [official blog](https://marmelab.com/blog) contains a November 25, 2026 publication, providing recent operating evidence. The historical self-funding statement was not converted into a claim that every subsequent financing event has been ruled out.

### 8. BruceDevices — Bruce Devices

**Status: provisionally private and operating as an independent commercial project.** The [official website](https://bruce.computer/) advertises:

> “Buy our Board HERE”

The [hardware page](https://bruce.computer/boards) describes:

> “Official and community hardware designed for Bruce firmware”

These support continuing firmware and hardware activity. They do **not** establish a separately incorporated company or a verified ownership structure. No qualifying funding, acquisition, shutdown, or valuation disclosure was located.

### 9. go-gitea — Gitea Ltd / CommitGo

**Status: private and operating.** The [official Gitea Cloud announcement](https://blog.gitea.com/gitea-cloud/) states:

> “Gitea Cloud is offered by ‘CommitGo, Inc.’, a Delaware company which is behind Gitea to offer services, support, and training”

The [2022 founder statement](https://blog.gitea.com/a-message-from-lunny-on-gitea-ltd.-and-the-gitea-project/) explains:

> “I have also transferred both the domains and trademarked name to Gitea Ltd. so that they are no longer personally owned by me”

This founder-to-company transfer is **not evidence of an external acquisition**. No qualifying equity-funding amount or valuation was verified. Donations, merchandise sales, and paid commercial contributions described by the founder were not counted as equity financing.

### 10. GrapesJS — GrapesJS

**Status: private and operating through Grapes Studio Inc.** The [June 28, 2024 investor announcement](https://opencoreventures.com/insights/grapesjs-creator-founds-grapes-studio-inc-to-bring-the-open-source-multi-project-no-code-website-editor-mainstream/) states:

> “With funding from OCV, Artur aims to build a better alternative”

Its title identifies the company as **Grapes Studio Inc.** The [current commercial website](https://grapesjs.com/) markets an “AI visual editor for SaaS” with pricing, sign-in, and product documentation.

Investment is confirmed, but its amount and any valuation are not disclosed in the investor announcement. No amount was inferred from Open Core Ventures' general investment model or aggregator profiles. Venture backing was not classified as an acquisition.

## Full BibTeX

```bibtex
@misc{datalab_site,
  author = {{datalab industries ltd.}},
  title = {datalab industries ltd.},
  url = {https://datalab.industries/},
  urldate = {2026-11-26}
}

@misc{datalab_registry,
  author = {{Companies House}},
  title = {DATALAB INDUSTRIES LTD: Company overview},
  url = {https://find-and-update.company-information.service.gov.uk/company/15704476},
  urldate = {2026-11-26}
}

@misc{anki_transition,
  author = {{dae and AnkiHub}},
  title = {Anki's Growing Up},
  url = {https://forums.ankiweb.net/t/ankis-growing-up/68610},
  urldate = {2026-11-26},
  date = {2026-02-02}
}

@misc{anki_recent,
  author = {{dae}},
  title = {Regarding recent events},
  url = {https://forums.ankiweb.net/t/regarding-recent-events/74723},
  urldate = {2026-11-26},
  date = {2026-11-25}
}

@misc{notable_site,
  author = {{Notable}},
  title = {Notable: The Markdown-based note-taking app that does not suck},
  url = {https://notable.app/},
  urldate = {2026-11-26}
}

@misc{notable_registry,
  author = {{Companies House}},
  title = {NOTABLE TECHNOLOGIES LTD: Company overview},
  url = {https://find-and-update.company-information.service.gov.uk/company/12371038},
  urldate = {2026-11-26}
}

@misc{pandasai_funding,
  author = {{PandasAI}},
  title = {PandasAI raised a \$1.1M round led by Runa Capital},
  url = {https://blog.pandas-ai.com/pandasai-raised-a-1-1m-round-led-by-runa-capital/},
  urldate = {2026-11-26},
  date = {2023-10-07}
}

@misc{pandasai_news,
  author = {{Dan Taylor}},
  title = {PandasAI raises \$1.1M in Pre-Seed round for AI-powered data analysis},
  url = {https://tech.eu/2023/09/29/pandasai-raises-11m-in-pre-seed-round-for-ai-powered-data-analysis},
  urldate = {2026-11-26},
  date = {2023-09-29}
}

@misc{pandasai_yc,
  author = {{Y Combinator}},
  title = {PandasAI: Winter 2024 company profile},
  url = {https://www.ycombinator.com/companies/pandasai},
  urldate = {2026-11-26}
}

@misc{pandasai_interview,
  author = {{Benjamin Wolba}},
  title = {PandasAI: Shaping the Future of Conversational Data Analysis},
  url = {https://www.future-of-computing.com/pandasai-shaping-the-future-of-conversational-data-analysis/},
  urldate = {2026-11-26},
  date = {2024-08-06}
}

@misc{vectify_about,
  author = {{Vectify AI}},
  title = {About PageIndex},
  url = {https://pageindex.ai/about},
  urldate = {2026-11-26}
}

@misc{vectify_funding,
  author = {{Bae HQ}},
  title = {Vectify AI Raises £1.1M to Automate Document and Financial Data Analysis},
  url = {https://www.thebaehq.com/news/vectify-ai-raises-1-1m-to-automate-document-and-financial-data-analysis},
  urldate = {2026-11-26},
  date = {2025-03-21}
}

@misc{vectify_conflict,
  author = {{Dealroom}},
  title = {PageIndex company information, funding and investors},
  url = {https://app.dealroom.co/companies/pageindex},
  urldate = {2026-11-26}
}

@misc{gbp_usd,
  author = {{Frankfurter and European Central Bank}},
  title = {GBP/USD reference exchange rate, 21 March 2025, ECB provider},
  url = {https://api.frankfurter.dev/v2/rates?date=2025-03-21&base=GBP&quotes=USD&providers=ecb&expand=providers},
  urldate = {2026-11-26},
  date = {2025-03-21}
}

@misc{fx_documentation,
  author = {{Frankfurter}},
  title = {Frankfurter exchange-rate API documentation},
  url = {https://frankfurter.dev/},
  urldate = {2026-11-26}
}

@misc{bruno_funding,
  author = {{Anoop MD}},
  title = {The Funding Announcement We Never Made},
  url = {https://blog.usebruno.com/the-funding-announcement-we-never-made},
  urldate = {2026-11-26},
  date = {2026-08-11}
}

@misc{marmelab_funding,
  author = {{Jérémie Grossetete and François Zaninotto}},
  title = {Turning Open-Source Into Profit: Our Journey},
  url = {https://marmelab.com/blog/2023/11/08/open-source-profit-1.html},
  urldate = {2026-11-26},
  date = {2023-11-08}
}

@misc{marmelab_current,
  author = {{Marmelab}},
  title = {Latest Posts},
  url = {https://marmelab.com/blog},
  urldate = {2026-11-26}
}

@misc{bruce_site,
  author = {{Bruce Devices}},
  title = {Bruce Firmware},
  url = {https://bruce.computer/},
  urldate = {2026-11-26}
}

@misc{bruce_boards,
  author = {{Bruce Devices}},
  title = {Bruce Hardware},
  url = {https://bruce.computer/boards},
  urldate = {2026-11-26}
}

@misc{gitea_corporate,
  author = {{Lunny Xiao}},
  title = {A message from Lunny on Gitea Ltd. and the Gitea project},
  url = {https://blog.gitea.com/a-message-from-lunny-on-gitea-ltd.-and-the-gitea-project/},
  urldate = {2026-11-26},
  date = {2022-10-30}
}

@misc{gitea_cloud,
  author = {{Gitea}},
  title = {Gitea Cloud: A brand new platform for managed Gitea Instances},
  url = {https://blog.gitea.com/gitea-cloud/},
  urldate = {2026-11-26},
  date = {2023-11-27}
}

@misc{grapesjs_investor,
  author = {{Erica Lindberg}},
  title = {GrapesJS creator founds Grapes Studio Inc. to bring the open-source, multi-project, no-code website editor mainstream},
  url = {https://opencoreventures.com/insights/grapesjs-creator-founds-grapes-studio-inc-to-bring-the-open-source-multi-project-no-code-website-editor-mainstream/},
  urldate = {2026-11-26},
  date = {2024-06-28}
}

@misc{grapesjs_current,
  author = {{Grapes Studio}},
  title = {Embed a Visual Editor for Emails, Landing Pages, Websites and Documents},
  url = {https://grapesjs.com/},
  urldate = {2026-11-26}
}
```