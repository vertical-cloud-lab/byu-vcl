# Dated evidence: AI and the open-source funnel, US federal science funding, investor sentiment

Gathered 2026-11-25 by a research sub-agent for the investor memo, with instructions to include evidence against each
concern as well as for it. **[confirmed]** means the number was seen in the opened source (page, PDF, or the GitHub,
Stack Exchange or npm API); **[unconfirmed]** means it was seen only in a search snippet or secondary write-up. The
session's web-search budget ran out partway through section C, so C1 is thin.

## A. AI and the open-source business funnel

### A1. Tailwind Labs
- Adam Wathan, GitHub comment 2026-01-07: "75% of the people on our engineering team lost their jobs here yesterday because of the brutal impact AI has had on our business." (https://github.com/tailwindlabs/tailwindcss.com/pull/2388#issuecomment-3717222957) [confirmed]
- Same comment: "Traffic to our docs is down about 40% from early 2023 despite Tailwind being more popular than ever. The docs are the only way people find out about our commercial products." [confirmed]
- Same comment: "Tailwind is growing faster than it ever has and is bigger than it ever has been, and our revenue is down close to 80%." [confirmed]
- He closed the PR that would have added LLM-friendly docs (/llms.txt): "I'm nervous to offer them without solving that problem first." [confirmed]
- Runway, quoted by DevClass 2026-01-08: "if nothing changed, then in about six months we would no longer be able to meet payroll obligations." (https://www.devclass.com/ai-ml/2026/01/08/tailwind-labs-lays-off-75-percent-of-its-engineers-thanks-to-brutal-impact-of-ai/4079571) [confirmed]
- Podcast 2026-02-18: the cuts were "three of the four engineers"; the company is bootstrapped; after the layoffs "we added a lot of partner program revenue", which he calls "charity as a business"; he calls AI "the most transformative thing I've used for building things." (https://tighten.com/insights/pragmatic-ai-ep2-adam-wathan-ai-impact-on-open-source-funding/) [confirmed]
- New sponsors after the layoffs (amounts undisclosed): Vercel, Google AI Studio, Lovable, Supabase, Gumroad. (https://analyticsindiamag.com/ai-features/tailwind-was-crushed-by-ai-now-ai-companies-are-rescuing-it, 2026-01-24) [confirmed; secondary]
- npm monthly downloads of `tailwindcss`: 19.9M (Jan 2023), 49.9M (Jan 2025), 122.3M (Dec 2025), 631.9M (Oct 2026). (https://api.npmjs.org/downloads/point/2026-10-01:2026-10-31/tailwindcss) [confirmed]. Caveat: `react` went from 119M to 887M a month and `next` from 34M to 320M over the same span; automated and agent installs inflate downloads, so they don't measure users.

### A2. Stack Overflow
- del Rio-Chanona, Laurentsyeva & Wachs, *PNAS Nexus* 3(9), 2024-09-11: posting fell about 25% within six months of ChatGPT relative to Russian- and Chinese-language counterparts and maths forums; a lower bound; larger for the most widely used languages. (https://academic.oup.com/pnasnexus/article/3/9/pgae400/7754871) [confirmed]
- Burtch, Lee & Chen, *Scientific Reports* (May 2024): visits and questions fell, most on topics where ChatGPT does well; Reddit communities showed no decline; the loss was concentrated among newer users. (https://www.nature.com/articles/s41598-024-61221-0) [unconfirmed]
- Monthly questions, Stack Exchange API (excludes deleted questions; queried 2026-11-25): Mar 2014 207,169; Nov 2022 109,119; Dec 2023 42,280; Dec 2024 17,913; Dec 2025 4,114; Oct 2026 843 (−99.2% vs Nov 2022). Annual: 2022 1,334,585; 2023 787,547; 2024 398,312; 2025 108,909; Jan–Oct 2026 19,571. The decline began before ChatGPT: −47% from Mar 2014 to Nov 2022. [confirmed]
- Prosus FY2026 results (year to 2026-03-31): Stack Overflow revenue rose from $115M to $129M (+12%), adjusted EBITDA from −$9M to +$12M; the group took $482M of impairments "primarily related to Stack Overflow and GoodHabitz", "following the disruption caused by generative AI." (https://www.prosus.com/~/media/Files/P/prosus-corp-v2/results-reports-and-events-archive/annual-report/2026/prosus-financial-results-fy26-booklet.pdf) [confirmed]
- Earlier Stack Overflow impairments: $246M, $560M and $372M (2023–24), about $1.178B, 68% of the $1.742B purchase price. (https://www.citizen.co.za/business/how-ai-decimated-this-prosus-company/, 2026-02-05) [confirmed; secondary]

### A3. Other traffic that funds open projects
- Wikipedia human pageviews down about 8% for Mar–Aug 2025 vs 2024 after reclassifying evasive bots; Wikimedia blames AI answers in search and social video and warns of fewer volunteers and donors. (https://diff.wikimedia.org/2025/10/17/new-user-trends-on-wikipedia/) [confirmed]
- Mintlify (docs host, vendor data): AI coding agents 45.3% of docs requests vs browsers 45.8% over 30 days (https://www.mintlify.com/blog/state-of-ai, 2026-04-03); in August 2026, 257M agent requests vs 131M human page loads (https://www.mintlify.com/blog/the-state-of-knowledge-2026-highlights, 2026-09-16). [confirmed]
- Koren, Békés, Hinz & Lohmann, "Vibe Coding Kills Open Source" (preprint, 2026-01-21): when maintainers are paid through user engagement, more vibe coding lowers the creation and sharing of OSS (a model, not a measurement). (https://arxiv.org/abs/2601.15494) [confirmed]
- No company other than Tailwind was found publishing a numeric AI-driven docs-traffic loss. [unconfirmed beyond Tailwind]

### A4. AI crawler load on open infrastructure
- Wikimedia 2025-04-01: multimedia download bandwidth +50% since Jan 2024; bots about 35% of pageviews but at least 65% of the most expensive traffic. (https://diff.wikimedia.org/2025/04/01/how-crawlers-impact-the-operations-of-the-wikimedia-projects/) [confirmed]
- Wikimedia AI licensing deals with Amazon, Meta, Microsoft, Mistral and Perplexity, 2026-01-15, terms undisclosed. (https://ny1.com/nyc/all-boroughs/ap-top-news/2026/01/15/wikipedia-unveils-new-ai-licensing-deals-as-it-marks-25th-birthday) [confirmed]
- SourceHut, 2025-03-17: "anywhere from 20-100% of my time in any given week mitigating hyper-aggressive LLM crawlers"; "dozens of brief outages per week". (https://drewdevault.com/blog/Stop-externalizing-your-costs-on-me/) [confirmed]
- GNOME GitLab: about 3% of about 81–84k requests passed the Anubis proof-of-work check. (https://thelibre.news/foss-infrastructure-is-under-attack-by-ai-companies/; https://tech.slashdot.org/story/25/03/26/016244/) [confirmed]
- Fedora's Pagure, 2025-03-15: "in desperation, I blocked .br entirely." (https://www.scrye.com/blogs/nirik/posts/2025/03/15/mid-march-infra-bits-2025/) [confirmed]
- Read the Docs, 2024-07-25: one crawler downloaded 73 TB in May 2024 (over $5,000 of bandwidth); blocking AI crawlers cut download bandwidth 75%. (https://about.readthedocs.com/blog/2024/07/ai-crawlers-abuse/) [confirmed]

### A5. Low-quality AI bug reports and pull requests
- curl, 2025-07-14: about 20% of 2025 bug-bounty submissions were AI slop and about 5% genuine. (https://daniel.haxx.se/blog/2025/07/14/death-by-a-thousand-slops/) [confirmed]
- curl ended its bug bounty 2026-01-31 (announced 2026-01-26): 87 confirmed vulnerabilities and over $100K paid since 2019; confirmed rate above 15% in earlier years, below 5% in 2025. (https://daniel.haxx.se/blog/2026/01/26/the-end-of-the-curl-bug-bounty/) [confirmed]
- curl back on HackerOne without rewards, 2026-04-22: "The slop situation is not a problem anymore"; "Almost every security report now uses AI"; confirmed rate back to 15–16%. (https://daniel.haxx.se/blog/2026/04/22/high-quality-chaos/) [confirmed]
- curl report volume "4-5 times higher than it was in 2024", 2026-05-26. (https://daniel.haxx.se/blog/2026/05/26/the-pressure/) [confirmed]
- Ghostty (2026-01-22): drive-by AI PRs closed; Mitchell Hashimoto: AI "increased the 'bad' count by 10x if not more." (https://github.com/ghostty-org/ghostty/pull/10412) [confirmed]
- tldraw (2026-01-17) auto-closes external PRs. (https://tldraw.dev/blog/stay-away-from-my-trash) [confirmed]
- GitHub (2026-02-12) lets maintainers limit or turn off PRs. (https://github.blog/open-source/maintainers/welcome-to-the-eternal-september-of-open-source-heres-what-we-plan-to-do-for-maintainers/) [confirmed]
- Godot's Rémi Verschelde, 2026-02-18: AI slop PRs are "draining and demoralizing". (https://www.theregister.com/2026/02/18/godot_maintainers_struggle_with_draining/) [confirmed]

### A6. AI lowering the cost of reimplementation
- Cloudflare "vinext", 2026-02-24: one engineer, under a week, about $1,100 of Claude API tokens, 94% of the Next.js 16 API. (https://blog.cloudflare.com/vinext/) [confirmed]
- Gergely Orosz, 2026-03-05: "AI is bringing the value of existing commercial open source moats into question." (https://blog.pragmaticengineer.com/the-pulse-cloudflare-rewrites-next-js-as-ai-rewrites-commercial-open-source/) [confirmed]
- Anthropic's agent-built C compiler, 2026-02-05: 16 agents, about $20K, two weeks, builds Linux 6.9; stated limits include inefficient code and reliance on GCC for parts. (https://www.anthropic.com/engineering/building-c-compiler) [confirmed]
- chardet 7.0.0 (March 2026): an AI-assisted rewrite moved it from LGPL to MIT; the original author called it "an explicit violation of the LGPL." (https://simonwillison.net/2026/mar/5/chardet) [confirmed]
- Song, Agarwal & Wen (arXiv v4, 2026-08-13): Copilot raises project-level OSS contributions 5.9% and coordination time 8%. (https://arxiv.org/abs/2410.02091) [confirmed]
- Yeverechyahu, Mayya & Oestreicher-Singer (arXiv v4, 2026-05-24): Copilot raised OSS contributions 28–40%, mostly incremental. (https://arxiv.org/abs/2409.08379) [confirmed]
- METR randomized trial, 2025-07-10: 16 experienced OSS developers, 246 tasks, 19% slower with AI while believing they were 20% faster; 2026-02-24 follow-up estimates are unreliable by METR's own account. (https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/; https://metr.org/blog/2026-02-24-uplift-update/) [confirmed]

### A7. Counter-evidence: AI raising OSS usage, contributions or revenue
- GitHub Octoverse 2025: 1.12B contributions to public and open-source projects (+13%), 518.7M PRs merged (+29%), 1.1M+ public repos using an LLM SDK (+178%). (https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/) [confirmed]
- Supabase raised $100M at $5B pre-money (2025-10-03) and $500M at $10B pre-money (2026-06-04); "More than 60% of new databases are launched by some sort of AI tool." (https://supabase.com/blog/supabase-series-e; https://supabase.com/blog/supabase-series-f) [confirmed]
- Anthropic acquired Bun, which "will remain open source and MIT-licensed", 2025-12-03. (https://www.anthropic.com/news/anthropic-acquires-bun-as-claude-code-reaches-usd1b-milestone) [confirmed]
- OpenAI agreed to acquire Astral (uv, Ruff), 2026-03-19. (https://simonwillison.net/2026/mar/19/openai-acquiring-astral/) [confirmed]

## B. US federal science funding

### B1. Appropriations vs requests
- **NSF:** FY2024 enacted $9.06B; FY2025 $8.826B available under the full-year CR; FY2026 request $3.903B, enacted $8.75B (−3.4%), research account flat, STEM education $938M (−20%); FY2027 request $3.963B (−54.7%); FY2027 bills: House $7B (−20%), Senate $8.83B (+0.9%). (https://nsf-gov-resources.nsf.gov/files/FY-2027-NSF-Budget-Request-to-Congress.pdf; https://www.aip.org/fyi/congress-set-to-finalize-science-budgets-rejecting-trump-cuts; https://www.aip.org/fyi/senate-science-funding-proposals-revealed) [confirmed]
- **NIH:** FY2025 $47.035B program level (−0.6%); FY2026 request $27.915B (−40.6%); FY2026 enacted $47.493B (+1.0%), signed 2026-02-03; FY2027 request $41.471B (−10.8% comparable), competing research grants from 9,712 to 5,145 and success rate from 14.9% to 7.8%, again proposing a 15% indirect-cost cap; Senate FY2027 bill $49B (+$500M). (https://www.everycrsreport.com/files/2026-05-18_R43341_6d77dd2bbd94600af3f1daf86e55b0efd27b39a1.pdf; https://officeofbudget.od.nih.gov/pdfs/FY27/br/Overview%20of%20FY%202027%20Budget%20Executive%20Summary.pdf; https://www.appropriations.senate.gov/download/lhhs-fy27-bill-summary&download=1) [confirmed]
- **DOE Office of Science:** FY2025 $8.24B [unconfirmed]; FY2026 request $7.092B (−13.9%) [unconfirmed]; FY2026 enacted $8.25B + $150M = $8.4B (+1.9%) (https://www.aip.org/fyi/the-week-of-jan-5-2026) [confirmed]; FY2027 request $7.14B with $1.2B moved to a new Office of AI and Quantum; House $8.53B, Senate $8.52B. [confirmed]
- FY2027 status: a stopgap (P.L. 119-103, signed 2026-09-02) funds agencies through 2026-12-11. (https://www.asme.org/government-relations/policy-impact/congress-prevents-government-shutdown-and-delays-omb-rule) [confirmed]

### B2. Awards, terminations and the 15% indirect-cost cap
- NSF awards: FY2024 10,937; FY2025 8,647 ($8.3B obligated); FY2026 6,218 ($6.4B obligated), −43% in count vs FY2024, with more than $1B unobligated at year end. (https://www.aip.org/fyi/the-week-of-october-5-2026, citing Grant Witness) [confirmed]
- NIH FY2024→FY2025: competing research project grants −20.5% (10,265 → 8,161); success rate 18.5% → 13.0%; total research-grant dollars +3.0% to $26.503B, partly from funding grants up front. (https://www.grants.nih.gov/news-events/nih-extramural-nexus-news/2026/03/fiscal-year-2025-by-the-numbers-extramural-grant-investments-in-research) [confirmed]
- JAMA study: 694 NIH grants worth about $1.8B terminated in about a month in spring 2025. (https://www.statnews.com/2025/05/08/trump-nih-cuts-jama-study-analyzes-1-point-8-billion-in-grant-cancellations/) [confirmed]
- CRS: as of 2026-04-10, 1,392 NIH awards terminated ($539M unspent obligations), many later reinstated; fewer than 6 midstream terminations 2012–Jan 2025. (https://www.everycrsreport.com/files/2026-04-17_IF13131_c620ea761ed58004260034c2b14c614accfa0b17.pdf) [confirmed]
- 15% cap: NIH's permanently blocked (injunction 2025-04-04, affirmed 2026-01-05, no Supreme Court petition); DOE rescinded its caps effective 2026-01-23; NSF's vacated 2025-06-20 [unconfirmed]; FY2026 laws bar changes to NIH indirect-cost policy. OMB's proposed Uniform Guidance rewrite (2026-05-29) has no cap but prefers "institutions with lower indirect cost rates". (https://www.aamc.org/about-us/biomedical-research/science-policy-hub/federal-research-related-litigation; https://www.asme.org/government-relations/policy-impact/energy-department-rescinds-implementation-of-indirect-cost-policy; https://www.gtlaw.com/en/insights/2026/7/omb-proposes-significant-revisions-to-the-uniform-guidance-for-grants-and-agreements) [confirmed]

### B3. Tools companies' academic and government exposure
- **Bruker:** US academia and government "about 8% of our revenue", NIH-funded "only 3% to 4%" (2025-03-12); FY2025 revenue $3.44B, −3.7% organic, citing "headwinds from academic funding"; the FY2025 10-K calls the cuts "a material adverse effect" on its US academic business; it sold 2 GHz-class NMR systems in 2025 vs 4 in 2024; in Q3 2026 it saw demand strengthening "in Q3 also in the US academic market". (https://ir.bruker.com/press-releases/press-release-details/2026/Bruker-Reports-Fourth-Quarter-and-Full-Year-2025-Financial-Results/default.aspx; https://s22.q4cdn.com/617463959/files/doc_downloads/2026/03/BRKR_10K_123125.pdf; https://finviz.com/news/415261/bruker-reports-third-quarter-2026-financial-results) [confirmed]
- **Thermo Fisher:** academic and government "declined in the low single digits" in Q4 and full-year 2025; 2026 guidance assumes "similar conditions". (https://www.fool.com/earnings/call-transcripts/2026/01/29/thermo-fisher-tmo-q4-2025-earnings-transcript/) [confirmed]
- **Danaher:** direct NIH sales under 1% of revenue, total academic exposure under 5%. [confirmed]
- **Agilent:** academia and government is its smallest end market; −8% in fiscal Q1 2026 and −5% in Q2; US labs are "using available funding to keep their labs running as opposed to investing in new capital equipment". (https://s24.q4cdn.com/305549747/files/doc_earnings/2026/q1/transcript/Q1-26-Prepared-Remarks-Final.pdf) [confirmed]
- **Waters:** academic and government flat for FY2025 (−1% constant currency). [confirmed]
- **Revvity:** academia about 5% of revenue, NIH about 1%. [confirmed]
- **Bio-Techne:** academic customers about 21% of revenue, US institutions about 12%. [confirmed]
- **Illumina:** CEO 2026-01-14: "we still think 2026 will be muted on the research in [the] academic environment." [confirmed]

## C. Investor sentiment and relicensing, 2024–2026
- Prosus wrote down Stack Overflow for "the disruption caused by generative AI" (results dated 2026-06-27). [confirmed]
- Menlo Ventures: open-source share of enterprise AI model use fell "from 19% last year to 11% today" (2025-12-09). (https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/) [confirmed]
- Accel on Supabase: "We haven't seen a company grow at this pace, certainly in the database layer, ever before" (2026-06-04). [confirmed]
- Heather Meeker, 2026-04-09: "copyleft is moribund"; "maintaining a fork is almost always more expensive and difficult than complying." (https://heathermeeker.com/tag/lgpl/) [confirmed]
- Redis added AGPL for Redis 8 (2025-05-01); its CEO said the 2024 switch "hurt our relationship with the Redis community" and that "AWS and Google now maintain their own fork." (https://redis.io/blog/agplv3/) [confirmed]
- Elastic added AGPL (2024-08-29). (https://www.elastic.co/blog/elasticsearch-is-open-source-again) [confirmed]
- Liquibase 5.0 moved from Apache 2.0 to the source-available Functional Source License (2025-09-30). [confirmed]
- MinIO wound down its open-source community edition: source-only releases (2025-10-15), maintenance mode (2025-12-03), repository archived (2026-02-12). (https://github.com/minio/minio) [confirmed]
- OpenAI released Apache-2.0 open-weight gpt-oss models (2025-08-05). [confirmed]
- Gaps: no direct 2024–26 statements from Sequoia, Redpoint, Bessemer or OSS Capital were found before the search budget ran out; no stock-price reactions to 2025–26 relicensings (the companies are private).
