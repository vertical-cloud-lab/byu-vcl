# Verification log: claims used in the video and the summary

Each headline 2025–26 claim was checked against a second, independent source. The checks used the Pi
search batches ([`pi-browser/queries_batch3_verify.tsv`](pi-browser/queries_batch3_verify.tsv),
[`queries_batch4_verify.tsv`](pi-browser/queries_batch4_verify.tsv); results in
[`search_log.jsonl`](pi-browser/search_log.jsonl)), Yahoo Finance, or the primary page itself.

| Claim (as used) | Case-file source | Independent check | Status |
| --- | --- | --- | --- |
| Anthropic listed on Nasdaq (ANT) on 2026-11-19; market cap about $1.17T on 2026-11-23 | companies/C/anthropic.json (stockanalysis.com) | Yahoo Finance quote: "Anthropic, PBC Class A Common Stock", exchange NMS, first trade 2026-11-19, market cap $1.171T | Confirmed |
| NVIDIA agreed to buy Hugging Face for $12.93B (Sep 2026) | companies/B/hugging-face.json (NVIDIA blog, TechCrunch) | Pi: NVIDIA blog "NVIDIA to Acquire Hugging Face" (2026-09-03), TechCrunch, WIRED | Confirmed (agreed; closing not confirmed) |
| IBM completed its acquisition of Confluent for about $11B (2026-03-17) | companies/A/confluent.json | Pi: IBM newsroom, "IBM Completes Acquisition of Confluent" (2026-03-17) | Confirmed |
| Databricks valued at $190B (2026-08-13) | companies/B/databricks.json | Pi: CNBC and Reuters, 2026-08-13 ($5B round) | Confirmed |
| OpenAI post-money valuation of $852B (closed 2026-03-31; $122B round) | companies/C/openai.json (Wikipedia) | Pi: CNBC, 2026-03-31 | Confirmed |
| xAI valued at $250B in its SpaceX all-stock merger (2026-02-02) | companies/C/xai.json (Wikipedia) | Pi: CNBC, 2026-02-03 | Confirmed |
| DeepSeek raised at about $70B pre-money (2026) | companies/C/deepseek.json (Wikipedia) | Pi: reports of a $15–16B round at $70–74B pre-money | Roughly confirmed (range $70–74B) |
| Meta's frontier model Muse Spark shipped closed (April 2026) | companies/C/meta.json | Pi: TNW, 2026-04-08 and others | Confirmed |
| Prefect acquired Dagster Labs (2026-07-13) | companies/B/prefect.json, dagster.json | Pi: Prefect and Dagster announcements, 2026-07-13 | Confirmed |
| Supabase valued at $10B (2026) | companies/B/supabase.json | Pi: TechCrunch, "Supabase doubles valuation to $10B" | Confirmed |
| Isomorphic Labs raised about $7.7B in total (a $2.1B round, then a $5B Series C in Nov 2026) | companies/E/isomorphic-labs.json (Isomorphic press releases) | Pi: "Isomorphic Labs announces $5 Billion Series C" | Confirmed |
| Opentrons raised a $40M Series E (2026-10-29); valuation fell from $1.8B (2021) to about $162M (2025) | companies/E/opentrons.json | Pi: Opentrons press release (Series E); the 2025 valuation is a Forge estimate | Partly confirmed (the valuation is an estimate) |
| Arduino acquired by Qualcomm; terms revised 2025-10-29 | companies/D/arduino.json | Pi: Arduino blog (2025-11-21), Reddit r/hardware and r/arduino threads | Confirmed; the deal's close date is not confirmed by a primary source |
| Mistral valued at about €21B, or about $24B (Sep 2026) | companies/C/mistral-ai.json (null) | Pi: reports of a €3B Series D led by Samsung at over €21B | Confirmed as a range; left null in the case file |
| VASP's June 2026 guidelines forbid feeding its source to public AI models or training on it | companies/F/vasp.json | Primary: vasp.at/info/post (2026-07-20) | Primary source only |
| SDL-demo kit: $80 list price, $15.57 fee, $51.19 hardware, $6 labour, $2.24 stated profit | gh-mining digest | Re-read from the source comment (discussion #124, 2023-05-04). The stated items sum to $75, and the chart shows the unitemized $5 | Confirmed, with the arithmetic gap noted |
| Open-source software: $4.15B supply-side, $8.8T demand-side value; firms would spend 3.5× more; 96% of the demand-side value comes from 5% of OSS developers | Edison oss_economic_value | Primary: HBS working-paper page (Hoffmann, Nagle & Zhou 2024), fetched through the Pi on 2026-11-23 | Confirmed |
| Commercial open-source startups: median exit $1.3B vs $171M (IPO) and $482M vs $34M (M&A); 1.6× / 1.23× valuation at Series A / B; 12% exited; $26.4B across 211 deals in 2024 | LF/Serena/COSSA 2025 report | Primary: report PDF (doi:10.70828/REYQ7474), text extracted with pdftotext | Confirmed (co-authored by a VC that backs open source) |
| arXiv left Cornell on 2026-07-01; FY2025 deficit of $297k; record of 40,363 submissions in Sept 2026 | companies/G/arxiv.json | Primary: arXiv blog posts and FY26 budget PDF (cited in the file) | Primary sources |
| OSF narrowing: $4–5M a year needed; new projects stopped on 2026-11-16 | companies/G/center-for-open-science.json | Primary: COS blog (2026-08-11, 2026-08-14) and cos.io/osf-changes | Primary sources |
| Epoch, OpenAlex and price numbers | data/*.csv | Recomputed from the raw downloads by the scripts in `scripts/` | Reproducible |

Not used in the video because they couldn't be verified well enough: Creality's 2026 Hong Kong
listing, Stability AI's valuation, the date EvolutionaryScale joined Biohub, and whether Strateos and
Kebotix still operate.
