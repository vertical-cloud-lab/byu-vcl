# Video notes: sources for every chapter, and changes after upload

Part 1: https://www.youtube.com/watch?v=Aakq7PNsFpE · Part 2: https://www.youtube.com/watch?v=uujMO9R1tMc · Part 3: https://www.youtube.com/watch?v=8P7iqUaVHyE

## Part 1

### 0:00 Intro
**Sources:** README.md

> What is open science worth in the age of AI? Over six hours, we combined nine literature reviews from Edison, a hundred and twenty-one company and project case files, Epoch AI and OpenAlex data, market prices, and nearly five thousand of our own GitHub comments. Here is what the numbers show.

### 0:21 What open-source software is worth
**Sources:** edison/oss_economic_value_answer.md; VERIFICATION.md (HBS page)

> Start with software. A Harvard Business School study estimates that rewriting the open-source code that firms use would cost about four billion dollars, but that firms would need about eight point eight trillion dollars to replace it themselves. Researchers working with U.S. national accounts put American investment in open source at thirty-six to thirty-eight billion dollars in 2019, and a European Commission study linked sixty-five to ninety-five billion euros of EU output to it. These measure different things, but they agree on one point: the value of using open code dwarfs the cost of writing it.

### 0:59 Open science: PDB, genome, open hardware
**Sources:** edison/open_science_roi_answer.md; RCSB PDB economic-impact PDF; edison/open_hardware_economics_answer.md

> Open science follows the same pattern. The Protein Data Bank costs about seven million dollars a year to run, while researchers spend an estimated five and a half billion dollars of time using it every year. It also supplied the training data for AlphaFold. When Celera restricted access to part of the human genome, later research and diagnostics on those genes fell by twenty to thirty percent. And open scientific hardware costs, on average, eighty-seven percent less than the commercial equivalent.

**Clarification:** the 87% saving for open scientific hardware is material cost only (no labour), with commercial comparators for about 45 of the 119 designs. The PDB's 800× compares operating cost with use value (researcher time), not net benefit.

### 1:33 Where the money went in commercial open source
**Sources:** companies/A, companies/B; companies_master.csv

> So who captures that value? Among about thirty commercial open-source companies with known prices, the biggest numbers belong to firms that wrap open code in a paid service. Databricks is valued at a hundred and ninety billion dollars. NVIDIA agreed to buy Hugging Face for twelve point nine billion, and IBM bought Confluent for eleven billion. Red Hat, the purest open-source subscription business, sold to IBM for thirty-four billion. MongoDB moved to a restrictive license in 2018 and is still worth about twenty-three billion. Openness alone does not set the price. Owning the service around it does.

**Update after upload:** After the video, Elastic's market cap was $8.6B (Yahoo, 2026-11-24) vs the $10.2B shown (2026-10-30), and MongoDB's $25.2B vs $23.0B shown. These are normal market moves.

### 2:13 Venture data: open vs closed startups
**Sources:** LF/Serena/COSSA 2025 report PDF (doi:10.70828/REYQ7474)

> A broader dataset points the same way in venture markets. The Linux Foundation, Serena Capital and the Commercial Open Source Startup Alliance matched more than eight hundred venture-backed open-source startups with closed-source peers. Median valuations at IPO were one point three billion dollars versus a hundred and seventy-one million, and at acquisition four hundred and eighty-two million versus thirty-four million. The open-source startups also raised at higher valuations and moved faster between rounds. One caution: the authors include a venture firm that backs open source, and only twelve percent of these startups have exited, so those medians describe the winners.

### 2:56 Licences move both ways
**Sources:** companies/events.csv

> Licenses are not fixed. In our case files, changes to license or access terms roughly doubled after 2020: thirty-one closing moves and thirty opening moves, against sixteen and eleven in the decade before. When a company closed a project that others were reselling, a fork followed: OpenSearch, OpenTofu, Valkey. Elastic and Redis later added an open-source license back. AI moved the other way, with DeepSeek's MIT release, OpenAI's first open weights since GPT-2, and Anthropic giving its Model Context Protocol to the Linux Foundation. Meanwhile, Meta's newest frontier model shipped closed.

### 3:39 Who opens, who closes
**Sources:** data/openness_by_company_kind.csv

> Across all hundred and twenty-one case files, the direction of travel depends on who you are. Companies founded since 2000, mostly venture-backed, started moderately open and became less open on average, and nearly half made at least one closing move. Firms founded before 2000 moved the other way, opening the parts they don't sell. Government, academic and foundation infrastructure started the most open and stayed there: only one of eighteen ever made a closing move.

**Update after upload:** Recomputed after the video on 143 organizations, with independent rescoring: the VC-era minus incumbent difference is −0.67 to −0.71, and both 95% CIs exclude zero.

**Correction (independent review, 2026-11-24):** this chapter overstates the effect. The 'founded before 2000' group wrongly included open infrastructure (LAMMPS among others). With infrastructure classified first, the raw gap is −0.61. Adjusted for starting openness it is −0.09 (95% CI −0.45 to +0.28). The robust pattern is convergence to the middle (open starters close, closed starters open), not that venture-backed firms close up. Infrastructure: 1 of 24 made a closing move. See data/kinds_corrected.csv.

### 4:09 Openness over time: software
**Sources:** companies/A, B

> Seen as lanes over time, the most open software firms are also among the longest-lived. Red Hat, SUSE and Canonical have each lasted more than two decades. Most of the listed open-core firms ended up owned by someone else, but their code lived on in foundations, whatever happened to the company.

### 4:30 Open-source-origin stocks vs closed peers
**Sources:** data/prices_weekly_close.csv

> Did open-source roots hurt shareholders? It depends on the company. MongoDB is up about ten-fold since listing, Elastic is roughly flat after eight years, and GitLab is down about sixty percent, while the median closed-source peer of the same vintage grew about four- to six-fold. HashiCorp, Confluent and Couchbase left the market through buyouts. With so few survivors, this is no proof of an open-source penalty, but there is no premium either.

### 4:59 Openness over time: hardware
**Sources:** companies/D

> Hardware is different. The open-hardware pioneers have lasted: Adafruit and SparkFun for about two decades, Prusa for fourteen years. But they stay small and private. The large valuations went to firms that are closed or closing. MakerBot closed its designs in 2012, sold for about four hundred million dollars, and its goodwill was written off within three years. Bambu Lab paired open slicer software with closed printers and won a large share of the market. Arduino now belongs to Qualcomm. Openness scales in hardware mainly through shared standards like RISC-V and the Open Compute Project.

### 5:38 Physical-science infrastructure
**Sources:** companies/E, F

> In the physical sciences, open infrastructure lasts. The Protein Data Bank has been open since 1971, and LAMMPS, Quantum ESPRESSO, the Materials Project and Jupyter keep growing with government and academic support. Closed codes last too: Gaussian, VASP and COMSOL have run for decades. The difference is control and capture. Ansys sold for thirty-five billion dollars, while OpenFOAM's maintainers run on about a quarter of a million euros a year. And the AI-for-science startups of 2025 and 2026 raised billions, almost all of it for closed work, often built on open public data.

### 6:20 Frontier AI: value sits with closed weights
**Sources:** companies/B, C; Yahoo Finance (ANT)

> Frontier AI shows the split most starkly. Anthropic keeps its model weights closed while opening standards like MCP, and it listed on Nasdaq four days ago at over a trillion dollars. OpenAI's last private valuation was about eight hundred and fifty billion. DeepSeek, the most prominent open-weight lab, raised at around seventy billion.

### 6:44 Big Tech and AI labs over time
**Sources:** companies/C

> Big Tech opens what it does not sell. Google gave away Kubernetes, Meta gave away PyTorch and React to foundations, and NVIDIA publishes open models that run on its closed CUDA stack. But a company's own projects can close again, as Llama did.

### 7:02 Who releases model weights
**Sources:** data/epoch_openness_by_year_sector.csv; Trisovic et al. (arXiv 2511.21739)

> Who releases model weights? In Epoch AI's database of U.S. models, academia's open-weight share rose from about one in five in 2018 and 2019 to about four in five in 2024 and 2025. Industry's stayed near forty percent and has drifted down. Joint industry and academic projects look like academia. And in science, one study found that ninety-two percent of the foundation models adopted in research papers since 2019 were open-weight.

**Update after upload:** The 92% figure comes from Edison's reading of Trisovic et al.; the paper's abstract says 'open-weight models dominate' and that science lags the frontier (6.9× by 2024).

### 7:33 The compute gap
**Sources:** data/epoch_max_compute_open_vs_closed.csv

> But the frontier is closed. In 2025, the largest open-weight training run used about one twelfth of the compute of the largest closed run, and so far in 2026 the gap has widened to roughly fifty-fold.

### 7:50 Open-access papers by sector
**Sources:** data/openalex_us_oa_by_sector.csv

> Papers tell a different story. The share of U.S. journal articles that anyone can read rose from about a quarter in 2000 to more than seventy percent today. Industry went from the least open sector to more open than academia overall. In the physical sciences, industry still trails, and government and national labs are the most open of all. Open papers and closed weights: that is the pattern of the AI era.

### 8:17 How the labs talk about open
**Sources:** language/term_rates_by_org.csv (41-document corpus at render time)

> How do the labs talk about openness? We fetched forty-one primary documents through our lab's Raspberry Pi. Meta's writing mentions open source about ten times per thousand words, mostly in its 2024 manifesto. Anthropic's and OpenAI's writing is dominated instead by safety and by science, and both now pitch AI for scientific discovery. Anthropic's new Model Hardware Standard aims to let AI agents operate lab instruments, with an open-source release planned.

**Update after upload:** The corpus later grew to 57 documents. Anthropic's rates changed (safety 5.9, science 6.5, open 1.1 per 1,000 words); see figures/language.png and README section 7.

### 8:48 In their own words
**Sources:** language/key_quotes.md

> In 2015, OpenAI promised to share its code and patents. A 2016 email from Ilya Sutskever said it was totally OK not to share the science. Its 2018 charter expected less publishing. In July 2026, Anthropic called open-weight models without dangerous capabilities a public good, and said it has never advocated a ban, while arguing that every capable model should be safety-tested.

### 9:16 Our own GitHub threads
**Sources:** gh-mining/coded_threads.csv; self-driving-lab-demo discussion #124

> Our own repositories show the same tension at small scale. We coded a hundred and eighteen threads about commercialization in the Acceleration Consortium's lab repository and in the self-driving lab demo. The most common topics were replicating open hardware, kit costs, and sustainability. The one real attempt to sell the eighty-dollar demo kit, through GroupGets group buys, left a stated profit of two dollars and twenty-four cents per kit before shipping overhead. The institutional lab bought rather than sold, and its most frequent complaint was closed commercial equipment with no API or documentation.

### 9:55 DAL and the vertical cloud lab (#318)
**Sources:** digital-alloy-lab README and proposal drafts; dal/dal_openness_audit.md

> Finally, our own lab. The Digital Alloy Lab's repository went public under the MIT license in October 2026, with budgets and letters kept private. Its proposal drafts commit to releasing the FLAIME platform as open source. On the alloy compositions themselves the drafts disagree: the latest says they will be published openly rather than licensed, while earlier drafts planned a review for selective protection. And they pair open pycalphad screening with commercial Thermo-Calc databases. The vertical cloud lab model in pull request 318 is the same pattern at lab scale: closed commercial instruments, orchestrated and documented in the open. The evidence says to keep open the layers others build on, such as drivers, schemas, data and digital twins, and to be deliberate about the rest.

**Update after upload:** The DAL card and narration were corrected before upload: the latest proposal draft says compositions will be 'published openly rather than licensed' (earlier drafts proposed a month-6 IP review).

### 10:48 Takeaways
**Sources:** README.md

> Six takeaways. Open code and data create far more value than they cost, but rarely capture it. Value goes to whoever runs the service, owns the data, or sells the hardware around the open core. Licenses are now strategic levers that move in both directions, and foundations are what keep openness durable. In hardware, openness pays in cost and longevity rather than valuation, except through open standards. AI for science runs on open public data and mostly open models, even as the frontier closes. And labs like ours add the most by opening the pieces others can build on.

### 11:29 Data and sources
**Sources:** —

> All of the data, code, case files and sources behind this video are open on GitHub, in the BYU Vertical Cloud Lab repository, issue three eighty.

## Part 2

### 0:00 Intro
**Sources:** —

> Part two. After the first video, we kept digging: twenty-two more organizations, a second verification pass, and new data on the open-science commons, on how the AI labs talk, and on our own lab. Here is what it adds.

### 0:16 Openness over time, by sector
**Sources:** data/openness_by_year_sector.csv; data/robustness_kinds_by_scope.csv

> First, openness as a function of time. Rebuilding each organization's licensing history year by year, commercial open-source software and hardware started out the most open in the mid-2000s and have declined steadily since. Big Tech and the AI labs moved the other way, opening up through the 2010s before dipping in 2026. Today every sector sits near the middle of our scale: open core, or mixed. The split between young and old firms holds up statistically: companies founded since 2000 became less open than incumbents by about two-thirds of a point, with a ninety-five percent confidence interval that excludes zero.

**Correction:** the narration's 'two-thirds of a point … interval that excludes zero' used a misclassified grouping. Corrected and adjusted for starting openness, the founding-era gap is −0.09 (95% CI −0.45 to +0.28). Also, group G (AM and instrument makers) sits near 1.1 and isn't plotted, and the physical-science line averages closed lab-automation and AI-for-science firms (0.57 in 2026) with open science infrastructure (2.70). The six-sector version is figures/openness_by_year_six_sectors.png.

### 0:57 Fifty years of open data: the PDB
**Sources:** data/pdb_released_per_year.csv

> Second, the open-science commons. The Protein Data Bank had released about a hundred and seventy-three thousand structures by 2020, the year AlphaFold 2 won the CASP14 competition, and it has grown past two hundred and sixty thousand. Decades of open, publicly funded data were the precondition for that breakthrough.

### 1:21 The open-science commons under strain
**Sources:** companies/G (arxiv, center-for-open-science, papers-with-code)

> But the commons is under strain. arXiv's submissions grew seventeen percent in 2025, and monthly submissions doubled between September 2024 and September 2026 as AI-assisted papers surged. It separated from Cornell this July and ran a deficit, before receiving a seventeen-million-dollar multiyear gift. The Center for Open Science is narrowing its Open Science Framework, because keeping it whole would cost four to five million dollars a year, about half its budget, and new projects stopped last week. And Meta shut down Papers with Code in 2025. The services that AI draws on are among the least funded.

### 2:04 From open to science: how the labs talk
**Sources:** data/language_by_year.csv; language/key_quotes.md

> Third, language. With forty-eight primary documents from the two labs, the shift is clear. Writing about science and the physical world rose roughly tenfold, from before 2024 to 2026, while Anthropic's talk of safety fell. OpenAI's open-source language spiked only in 2025, with gpt-oss. Both now court the national laboratories through the Department of Energy's Genesis Mission, with free or discounted access rather than open weights.

### 2:34 US open source: growth and licences
**Sources:** data/innovationgraph_*.csv

> Fourth, the base of U.S. open source keeps growing, and getting more permissive. U.S. developers on GitHub rose from about ten million in 2020 to thirty-five million this year, and permissive licenses like MIT and Apache grew from sixty-four to sixty-eight percent of what they push to. The relicensing fights are about a handful of vendor-controlled projects, not the commons as a whole.

### 3:00 Closed instruments, fragile makers
**Sources:** companies/G (desktop-metal, markforged, stratasys)

> Fifth, the instruments our lab buys are closed, and their makers are fragile. All thirteen additive-manufacturing and lab-automation makers we added score zero or one on our openness scale. And the 2021 wave of SPAC listings went bust. Desktop Metal went public at up to two and a half billion dollars and filed for bankruptcy in 2025. Markforged debuted at two point one billion and sold for forty-two and a half million.

### 3:28 A closer audit of DAL and #318
**Sources:** dal/dal_openness_audit.md

> Finally, a closer audit of DAL and pull request 318. Of roughly twenty instruments on the alloy route, only four have interfaces the lab can program today: the arms, the mobile robots, the OT-2 and the CubXL. The atomizer has no API, so the lab plans to read its settings with a camera. The proposal drafts disagree on whether alloy compositions will be published or protected, and the data-sharing promise lags the funder's rule of release at publication. The audit recommends MIT for code, CERN's permissive hardware license for designs, CC BY for data in Zenodo and the Materials Data Facility, one open driver per instrument, and asking vendors for API rights before buying.

### 4:16 What Part 2 adds
**Sources:** —

> So, what Part 2 adds. Every sector is converging on open core. Young, venture-backed firms close up while public infrastructure stays open. The commons that trained the AI needs funding of its own. The AI labs court science with access, not open weights. And for our lab, the highest-leverage move is to own, and open, the driver and data layer between closed instruments and AI.

**Correction:** takeaway 2 ('Young, VC-backed firms close up … CI excludes zero') is overstated, for the same reason (see the 0:16 note).

### 4:42 Data and sources
**Sources:** —

> Data, code and every source for both parts are on GitHub, in the BYU Vertical Cloud Lab repository, issue three eighty.

## Part 3

### 0:00 Intro
**Sources:** —

> Part three. In the last hours of this research run we added thirty-six more case files, six more literature reviews, and data straight from GitHub. Here is what they add.

### 0:12 Do forks survive closing moves?
**Sources:** data/fork_vs_original.csv

> First, do forks survive when a company closes its license? We counted commits over the past year for eight originals and their open forks. Every fork is alive. Where the vendor kept investing in public, like Elastic and HashiCorp, the original stayed far more active. Where the vendor's public effort faded, or it reversed course, the fork took over: Valkey now out-commits Redis, Apache Pekko out-commits Akka six to one, OpenVox carries Puppet's community, and LibreOffice dwarfs OpenOffice.

**Clarification:** 'Every fork is alive' refers to the eight well-known forks checked. Most closing moves in the case files drew no fork, and Neo4j stopped one in court.

### 0:43 AI-era open-source startups
**Sources:** companies/A, companies/J

> Second, open source in the AI era. Seventeen AI-infrastructure startups, from Ray and vLLM to LangChain, Ollama and llama.cpp, did something the database companies of the 2010s did not: none of them switched to an SSPL or BSL license. Their average openness held steady, while the earlier cohort fell by a full point. They make money from hosted and enterprise layers, and their exits were mostly acquisitions by companies that sell compute or chips, CoreWeave, Nscale, Qualcomm and Cloudflare, plus Hugging Face and Replit. There were no IPOs.

**Clarification:** this holds *so far*. These firms are young (median founding 2022), while 2010s database firms first closed at a median age of about 10.

### 1:22 AI-for-science models: licences over time
**Sources:** companies/I

> Third, AI models for science. Across nineteen releases, from AlphaFold to MatterGen and Meta's open materials datasets, openness averages about 2.8 on our scale, well above the frontier language-model companies. License changes ran eleven toward open and seven toward closed. When AlphaFold 3 launched without code, open re-implementations like Boltz and Chai-1 followed within months, and AlphaFold 3's code is now under Apache 2.0, though its weights remain gated.

### 1:53 The academic path
**Sources:** edison/academic_*_answer.md

> Fourth, the academic path. Who owns the code decides what a lab can release: contractor-run national labs can open-source under their own copyright, while code written by federal employees has no domestic copyright at all. University licensing brought in nearly three billion dollars in 2018, yet most technology-transfer offices don't cover their costs. For open lab hardware, the documented path is to publish the design and sell what publication does not supply: built and tested instruments, kits, training and support. The review literature even records Sterling Baird's light-mixing demo kit: thirty-nine units sold through two group buys.

### 2:37 Agents write our open record
**Sources:** data/byu_vcl_chars_by_month.csv

> Finally, a look in the mirror. In this lab's own repository, Claude now writes most of the public record: about six point four million characters, against one point four million from people. Agents make working in the open cheaper than ever, which makes verification, and clear human direction, more important than ever.

### 2:59 What Part 3 adds
**Sources:** —

> So, five more lessons. Forks always survived, and won when vendors stopped investing in public. AI-era open-source tools stayed permissive and sold hosted layers to the compute industry. AI-for-science models are more open than frontier chatbots, and restrictions spark open clones. Academic labs should publish designs and data openly, and earn from what publication can't supply. And with agents writing the record, openness is cheap, but checking it is essential.

**Clarification:** 'Forks always survived' means the eight checked. 'Stayed permissive' means so far, for young firms.

### 3:29 Data and sources
**Sources:** —

> All data, code and sources for the three parts are on GitHub, in the BYU Vertical Cloud Lab repository, issue three eighty.
