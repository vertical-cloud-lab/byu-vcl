# Edison synthesis for issue #380: the value of open science in the age of AI

Built only from the 13 `<key>_answer.md` files in this folder, nine from the first round and four from the second (queries in `_task_ids.json`). Numbers are quoted as they appear there. Sources are named as Edison cited them, with "via" where Edison cited only a secondary source. **[flag]** marks a limitation Edison itself raised: an unobtainable source, an unsubstantiated figure, or a trend or comparison that is not like-for-like.

## 1. Findings by job

### `oss_economic_value`

| Finding | Number(s), units, year | Source | Caveat |
|---|---|---|---|
| Global OSS value, supply vs demand side | $4.15B to produce; $8.8T to replace; about 2,120× | Hoffmann, Nagle & Zhou 2024, via Osborne et al. 2024 | Different concepts; working paper |
| US OSS investment | $0.733B (2009) to $38.44B (2019); revised $36.2B (2019), approximately 50% of own-account software investment | Robbins et al. 2021; Santiago Calderón et al. 2022 | GitHub only; model-sensitive; may double-count |
| EU impact, 2018 | about €1B personnel investment; €65B–€95B impact; benefit–cost above 4:1 with broader costs | Blind et al. 2021 | Commission report, not peer reviewed |
| GDP with no OSS, 32 countries, 2000–2018 | about 2.2% lower, long run | Blind & Schubert 2023 | Own contributions can lower a country's measured GDP |
| Entrepreneurship, 207 countries, 2000–2016 | +1% commits: 0.2%–0.4% more IT ventures; 0.4%–0.8% greater venture-financing value | Wright, Nagle & Greenstein 2020 | Elasticities; reverse causality possible |

### `open_science_roi`

| Finding | Number(s), units, year | Source | Caveat |
|---|---|---|---|
| Protein Data Bank | $5.5B/year use value, $760M/year contingent value vs about $6.9M/year cost (2016): approximately 797× and 110× | Sullivan et al. 2017 | Modeled, not realized returns |
| Human Genome Project | $3.8B federal; $796B US output (1988–2010); $141 per federal dollar | Battelle 2011, via Carr 2012 | Associated activity, not causal |
| Landsat free data (end of 2008) | benefits $2.19B (2011), $3.45B (2017); downloads roughly 20× by 2017 | Straub et al. 2019; Zhu et al. 2019 | [flag] program cost not in cited excerpts |
| NIH Public Access Mandate (2008) | patents cite funded papers 12–27% more; no measurable rise in academic citations | Bryan & Ozcan 2021 | Knowledge flow, not product value |
| AlphaFold, trained on PDB | 16–25% relative increase in research on proteins lacking experimental structures | Hill & Stein 2026 | Publications, not dollars |

### `open_hardware_economics`

| Finding | Number(s), units, year | Source | Caveat |
|---|---|---|---|
| Savings, open vs proprietary lab hardware | 87% average (119 articles); Arduino-based 89%, 3D-printed 92%, both 94% | Pearce 2020 | Materials vs purchase price; comparable prices for only 37.8% |
| Return on public development funding | approximately $30,000 cost; more than $2.5 million value within a year; ROI 460% to more than 8,300% | Pearce 2016 | One syringe-pump library |
| Arduino | 200 boards (2005) to more than 150,000 (Q1 2010); trademark fees 10% of revenue (2013) | Thompson 2011; Li & Seering 2019 | Value captured by brand, not designs |
| MakerBot (went closed) vs Aleph Objects (stayed open) | MakerBot acquired for $403 million (2013), then declined; Aleph $5.8 million Q2 2016 revenue, 2,782% three-year growth | Pearce 2017 | Not causally conclusive; [flag] claimed 2019 Aleph bankruptcy undocumented |
| Prusa Research | about CZK 6.6 billion (roughly USD $280 million) combined revenue (2024); more than 1,000 people | Guhathakurta & Nag 2026 | Openness now layered |

### `oss_business_outcomes`

| Finding | Number(s), units, year | Source | Caveat |
|---|---|---|---|
| Gross margin after adopting open development | approximately 4%–5% above nonadopters; 977 US high-tech firms, 2001–2025 | Singh et al. 2026 | A practice, not OSS vendors |
| First funding | at least 36% more likely, relative to the mean; 160,065 US startups | Conti, Peukert & Roche 2021 | Working paper; probability, not valuation |
| Acquisition | higher hazard if active in OSS; 67,794 firms, 2,639 acquired, 111 IPOs | Vetter 2021 | Association; licence type not significant |
| Relicensing (Elastic, HashiCorp, Redis) | Redis: 12 outside contributors the year before, zero in six months after; Valkey: 29 at 10 companies (2024); no clear evidence vendors' finances improved | Foster 2024 | Cases chosen because forks occurred; [flag] the finance finding is not a controlled zero |
| OSS use and firm productivity | positive, conditional on IT capability; no coefficient | Nagle 2019, as reported by others | [flag] full text unavailable |

### `open_weights_ai_impact`

| Finding | Number(s), units, year | Source | Caveat |
|---|---|---|---|
| Inference market | approximately 87% cheaper conditional on model intelligence; less than 30% share | Demirer et al. 2025 | Buyers also value capability and support |
| Capability gap, closed minus open | MMLU 15.9 points (late 2023) to 0.1 point (end 2024); Chatbot Arena 8.0% (Jan 2024) to 1.7% (Feb 2025) | Maslej et al. 2025 (AI Index) | Benchmarks miss some production needs |
| Release mix, notable models, 2024 | API 32.8%; restricted open weights 18.03%; unrestricted 11.48%; noncommercial 9.84% | Maslej et al. 2025 | A spectrum, not open vs closed |
| Use in science | 92% of adopted foundation models open-weight since 2019; customized 42% vs 23% (closed); Chinese families 61% of open-weight selections (2026) | Trišović et al. 2025; Dunivin 2026 | Preprints |
| Who gains: event study, 39 releases | open: +2.20% software-minus-compute spread; closed: −2.30% (p = 0.004) | Huang, Liu & Liu 2026 | Expected rents, not realized value |

### `sector_openness_trends`

| Finding | Number(s), units, year | Source | Caveat |
|---|---|---|---|
| Corporate science publishing | fell at publicly traded US firms, 1980–2007, while patenting rose | Arora, Belenzon & Patacconi 2015 | Edison reports no magnitude |
| Industry in AI research | industry-coauthored papers 22% (2000) to 38% (2020); largest models 11% (2010) to 96% (2021) | Ahmed, Wahed & Thompson 2023 | Output, not openness; not US-only |
| Code and data sharing, AI conferences | 11% (2014) to 64% (2024), 56,800 papers | Coakley et al. 2026 | All sectors mixed; documented, not rerun |
| Foundation Model Transparency Index | 37/100 (2023), 58/100 (2024), about 40/100 (2025) | Bommasani et al. 2024; Wan et al. 2026 | [flag] 2025 not like-for-like |
| Closed access, US federally funded papers | about 26% (2017–2020), nearly 32% (2021) | Schares 2023 | Before the 2022 Nelson memo |

### `open_sdl_lab_automation`

| Finding | Number(s), units, year | Source | Caveat |
|---|---|---|---|
| Minimal self-driving lab | $68.61 required parts (March 2022) | Baird & Sparks 2023 | Teaching demo; [flag] *Matter* paper unavailable in full |
| Hardware cost classes | open roughly $100–$2,000; commercial roughly $10,000 (general-purpose) to roughly $1 million (special-purpose) | Tom et al. 2024 | Open price excludes labor |
| Hidden engineering | hundreds to thousands of development hours; more than 70% of 58 respondents willing to publish | Pelkie et al. 2025 | Workshop; willingness, not adoption |
| OT-2 in industry (Roche) | approximately $7,500 starting price; ICC 0.998 vs manual; 30 minutes less hands-on time per assay | Lo et al. 2023; Thieme et al. 2024 | Commercial, not fully open; automation, not an SDL |
| AI-for-materials funding | approximately $1.98–$2.29 billion disclosed, Sept 2025 to July 2026; Periodic, CuspAI, Lila 86–88% | Shen et al. 2026 | Not peer reviewed; includes unconfirmed rounds |

### `physsci_software_sustainability`

| Finding | Number(s), units, year | Source | Caveat |
|---|---|---|---|
| Citations, atomistic codes | paid codes led free ones over the 2010s; Gaussian and VASP more than half of 23 commercial codes' citations; open engines up more than 300% since 2010 | Talirz, Ghiringhelli & Smit 2021 | Citations, not executions |
| Licence cost and code choice | Quantum ESPRESSO 67% vs VASP 47% of DFT users (Philippines, 2020) | Arevalo 2020 | 16 respondents |
| Quantum ESPRESSO reach | more than 4,000 downloads per release; 15,000 citations since 2009 (as of 2019) | Giannozzi 2019 | Not unique users |
| pymatgen reach | 23,239,954 PyPI downloads (Aug 2018–Dec 2025); 2,713 dependent repositories | George et al. 2026 | Testing inflates downloads |
| Project survival | 18,247 repositories: longer life with dependents, infrastructure status, government participation | Thakur et al. 2025 | Association |

### `precedent_open_data_to_ai`

| Finding | Number(s), units, year | Source | Caveat |
|---|---|---|---|
| Open inputs' share of AlphaFold or ML-materials value | none found | Edison precedent search | No restricted-access counterfactual |
| PDB value measures (2016 activity) | $5.5B/year use value (users' time at $58.50/hour); $760M/year willingness to pay ($2,573 per user); $1.1B/year conservative R&D return | Sullivan et al. 2017 | Repository-wide; predates AlphaFold2; "cannot be attributed 100% to RCSB-PDB" |
| Materials Genome Initiative | $123.229B–$270.047B/year potential US benefit (2013 dollars) | Scott et al. 2018 (NIST) | Prospective; nothing allocated to databases or ML |
| GNoME | 381,000 newly predicted stable materials (2023) | Merchant et al. 2023 | No dollar value |
| Openness counterfactual (genomics) | approximately 20–30% less downstream research and product development under Celera's restrictions | Williams 2013 | Not AI; not monetized |

### `materials_open_data_value`

| Finding | Number(s), units, year | Source | Caveat |
|---|---|---|---|
| Materials Project reach | 178,627 materials; more than 600,000 registered users; more than 145,000 material-data DOIs since 2015 (2025 account) | Horton et al. 2025 | Different measures; a downloaded record is not a person or a publication |
| Database scale | OQMD more than one million computed compounds (July 2022); AFLOW over 3.5 million entries (2024); NOMAD over 50 million total-energy calculations (March 2018), over 13 million repository entries (2024) | Shen et al. 2022; Toher & Curtarolo 2024; Draxl & Scheffler 2019; Bauer et al. 2024 | Compounds, entries and calculations differ; no user totals; [flag] NOMAD's two counts are not a time series |
| AI-scale datasets | Alexandria 5.8 million DFT structures; 119 million generated candidates gave 1.3 million DFT-validated compounds, 74,000 newly predicted stable (2026); OMat24 over 110 million DFT calculations, stability F1 greater than 0.9 (2026) | Cavignac et al. 2026; Barros-Luque et al. 2026 | DFT-validated is not synthesized; a calculation is not a material |
| Laboratory-tested results | MP search of 21,576 Li-containing materials led to a Li₃OCl interlayer (cell kept 76.36% capacity after 1,000 cycles); AFLOW descriptor: eight borides synthesized (2024); OQMD screening: two mixed perovskites synthesized and cycled | Horton et al. 2025; Divilov et al. 2024; Shen et al. 2022 | Database-supported, not database-alone discovery; [flag] perovskite formulas not named |
| Benchmarks | JARVIS-Leaderboard 1,281 contributions to 274 benchmarks (2024); NOMAD ML competition 883 submitted solutions | Choudhary et al. 2024; Draxl & Scheffler 2019 | Predictions, not discoveries; [flag] no platform-wide JARVIS discovery count |
| Citations per platform paper | JARVIS 2020: 712; MP 2025: 616; NOMAD 2019: 585; OMat24 2026: 560; OQMD 2022: 75; Alexandria 2026: 39 | Edison bibliographic records | [flag] no common method or date; not database-wide totals |
| Licences | OQMD CC BY 4.0; NOMAD raw calculations CC BY 3.0, embargo up to three years; OMat24 dataset CC BY; 2025 MP paper CC BY-NC 4.0 | Shen et al. 2022; Draxl & Scheffler 2019; Barros-Luque et al. 2026; Horton et al. 2025 | A paper's licence is not its data's; [flag] date and scope of any database-wide change not established |
| Funding and return | budgets generally not disclosed; tens of millions of dollars saved, returns up to 7:1 (computational materials engineering, 2016); approximately 3:1–9:1 (molecular modelling) | Jain, Persson & Ceder 2016; Goldbeck 2012 | Not database-specific; [flag] no defensible database-specific benefit, benefit–cost ratio or ROI |

### `lab_automation_business`

| Finding | Number(s), units, year | Source | Caveat |
|---|---|---|---|
| Clinical total laboratory automation market | $5.57–6.1 billion (2023); North America 38%; Siemens, Roche, Beckman Coulter 34%, 31%, 25% | Nam & Park 2025, citing QYResearch and Precedence Research | Clinical, not SDLs; [flag] no verifiable forecast or CAGR in accessible excerpts |
| SDL research and cloud-lab counts | 352 SDL papers, 2004–2023, rising after 2019; 15 example cloud labs worldwide (2025) | Jung et al. 2025; Zilgalvis 2025 | Activity, not revenue; the cloud-lab list is not a census |
| Emerald Cloud Lab and Strateos | ECL Austin 105,000 ft², more than 230 instruments; ECL minimum commitment more than $250,000 (2025 review); Strateos 14,000-ft² facility, approximately 200 instruments (2019 entry) | Zilgalvis 2025; Doloi et al. 2025 | [flag] facility data largely company statements; commitment figure unverified |
| Opentrons OT-2 prices | approximately $7,500 starting (2024 review); approximately $10,000 entry-level (2025 review); approximately $20,000–30,000 configured (2024) | Lo et al. 2024; Doloi et al. 2025; Norton-Baker et al. 2024 | Date and configuration differ; not Opentrons sales or profit |
| Industrial payback (Roche, OT-2 with AutoLab) | approximately half the labor cost per sample; labor saving did not fully offset hardware use within five years (2024) | Thieme et al. 2024 | One assay volume; sharing it across workflows might improve payback |
| Open build vs commercial liquid handlers | FINDUS under $400 to build, pipetting error below 0.3% (2025 review); commercial more than $60,000, some more than $150,000 | Doloi et al. 2025; Norton-Baker et al. 2024 | Build cost excludes labor, calibration and maintenance; [flag] not like-for-like |
| Open software on a cloud lab (DARPA SD2 Round Trip) | nearly 100 experiments on Strateos by 2022; design and analysis roughly two orders of magnitude faster; approximately ten versus three people | Bryce et al. 2022 | Combined software-and-lab workflow; not a Strateos-only effect |
| Company outcomes | no verified revenue, customer counts, profitability, valuation or exit for ECL, Strateos or Opentrons | Edison search; Zilgalvis 2025 | [flag] not in the retrieved evidence; facility size is no proxy |

### `industry_publication_norms`

| Finding | Number(s), units, year | Source | Caveat |
|---|---|---|---|
| Generative-AI papers, January 2020–March 2025 | Google DeepMind 969; Meta 64; OpenAI 64; Anthropic 62 (fractional counts); broad decline from 2023 to 2024, particularly at Google DeepMind | Strauss et al. 2025 | One corpus, not total output; [flag] Meta may be undercounted |
| Papers vs models | industry-only papers among the 100 most-cited: 17 (2021), 19 (2022), 7 (2023); industry 55 notable models, 90.2% (2024); academia 84.9% of AI publications (2023) | Maslej et al. 2025 (AI Index) | A highly cited subset, not all industry papers |
| Staged and gated releases | GPT-2's 1.5-billion-parameter model initially withheld (2019); LLaMA to approved researchers, non-commercial (2023); Llama 2 commercial use (2023); Llama 3.1 405B weights public (2024) | Stoltz et al. 2026; Touvron et al. 2023; Grattafiori et al. 2024 | Access widened but stayed licensed |
| Closed flagships, open smaller models | GPT-4 report omitted size, architecture, compute and dataset construction (2023); 2025 Index flagships o3, Gemini 2.5, Claude 4 by API, Llama 4 open-weight; gpt-oss (2025) and Gemma 2B and 7B (2024) open | OpenAI 2023; Wan et al. 2026; Gemma Team 2024 | Llama 4 and Gemma 3: training data and code private (Nobel et al. 2026) |
| FMTI, four firms, 2024 → 2025 | Anthropic 51 → 46; Google 47 → 41; Meta 60 → 31; OpenAI 49 → 35; mean 40.69/100 (2025), 13 developers | Wan et al. 2026 | [flag] indicators, sample and scoring changed; six firms, including Anthropic, scored from public information |
| FMTI training-data disclosure | training-data-properties indicators averaged 15% (2025); eight companies scored zero | Wan et al. 2026 | Measures disclosure, not publication or open weights |
| Funding and model choice in science | 104,226 papers, 2018–2025: industry cloud credits associated with closed/API models, public funding with open weights | Trišović & Sivaloganathan 2026 | Association, not causation |
| AI-conference code and data | 56,800 papers: code and data 11% (2014) to 64% (2024); code alone 13% to 69%; estimated reproducibility 28% to 64% | Coakley et al. 2026 | No systematic academia–industry difference; [flag] reproducibility inferred, not rerun |

### `open_infrastructure_sustainability`

| Finding | Number(s), units, year | Source | Caveat |
|---|---|---|---|
| arXiv | approximately $550,000 projected for 2012 (six full-time-equivalent staff, servers, networking); Cornell $75,000 annually plus indirect expenses; membership tiers $1,500–3,000, aimed at roughly 200 libraries and laboratories; later goal at least $300,000 per year | Rieger 2012; Reinsfelder & Pike 2018 | Historical projection, not a current budget |
| PDB, US RCSB node, 2023 | about $7.5 million: $2.8 million curation, $2.2 million preservation, $2.5 million dissemination; $420 per newly processed structure; $10.30 per archived structure per year; preservation about 1% of structure-determination costs | Berman & Burley 2025 | RCSB activity budgets, not the worldwide PDB's accounts |
| Zenodo, modeled | CHF 11 million discounted costs and CHF 2.8 billion potential discounted benefit, 2028–2057 | Crespo Garrido et al. 2024 | A comparable future platform, not Zenodo's budget or a realized return; [flag] no verified current annual cost |
| Center for Open Science (OSF) | $7 million annual operating budget (2019), about $3 million on product and engineering; $229,225 for 26 OSF Preprints services, 33,650 papers, $6.81 per paper (2020); planned 2021 mix 51% grants, 39% philanthropy, 10% earned revenue | Nosek et al. 2019; Schroeder et al. (CZI proposal, undated) | Proposal figures, not audited; $7 million is all of COS, not OSF |
| OpenAlex | $7.5 million Arcadia grant announced 2024, over five years; CC0 data plus paid premium tiers; usage-based API pricing (2026) | Torres-Salinas & Arroyo-Machado 2026; Borrego & Urbano 2025; Domenighetti 2026 | A grant total, not an annual cost; [flag] no audited annual budget |
| Grant loss | Tranche and Peptidome closed after NIH support ceased, with partial loss of data; NIAID ended VEuPathDB support covering approximately 60% of operating costs (September 2024) | ProteomeXchange, via Imker 2025; Imker 2025 | Preprint; VEuPathDB continued on stopgap support while developing tiered subscriptions |
| Hosted preprint servers | 14 of 29 listed servers ceased publishing or were no longer hosted by COS/OSF (2024) | 2024 examination, via Domenighetti 2026 | Individual services, not an OSF shutdown; annual service charges a possible contributor |
| Machine traffic | PRIDE: 159.3 million downloads (2021–2025); 48.2% automated bots; bot traffic up sixteenfold | Hewapathirana et al. 2026 | [flag] bots not shown to be generative-AI crawlers; bandwidth cost not quantified |

## 2. Cross-cutting conclusions

**Value far exceeds cost; producers capture little of it.** Wherever value is set against cost the gap is wide: $8.8T against $4.15B for OSS (a "risk of underproduction", per Osborne et al.); €65B–€95B from about €1B of EU contributions; PDB use value approximately 797× its operating cost. Gains spill outward: the global OSS stock raises GDP while a country's own contributions can lower its measured GDP (Blind & Schubert). Firms gain from engaging with OSS, but no premium for selling it is established, and relicensing shows no clear financial improvement. Hardware firms capture value through brand, expertise and speed, not design exclusivity; Emerald Cloud Lab, Strateos and Opentrons finances are unverified.

**Software, hardware, physical sciences.** Evidence is deepest for software (national accounts, GDP, venture formation). Open-hardware evidence is mostly device-level savings and single-case ROI; hardware also carries manufacturing and compliance costs and weaker licence protection, and price is not cost per result: Roche's OT-2 cut labor cost per sample to approximately half, yet did not fully offset its hardware within five years. Physical-science codes rely on public money (US DOE, EU MaX), foundations, institutions and industry: free distribution "shifts the financing problem" to maintenance labor. Open materials databases supply AI-scale training data (OMat24: over 110 million DFT calculations) and several laboratory-tested discoveries but no monetized return; the only ratios (up to 7:1; approximately 3:1–9:1) are not database-specific.

**Academia, government, industry over time.** US corporations published less science over 1980–2007, yet industry came to dominate frontier AI: 96% of the largest models by 2021 and 90.2% of notable models in 2024, though academia produced 84.9% of AI publications (2023). Industry disclosure became layered, with papers, API access and weights released separately; Google DeepMind's generative-AI papers fell from 2023 to 2024; and Anthropic, Google, Meta and OpenAI all scored lower on the Transparency Index in 2025 (Meta 60 → 31; [flag] method changed). Federal policy moved toward openness, from Holdren (2013) to Nelson (2022: all funders, immediate access) and NIH's 2023 data policy. AI-conference code-and-data sharing rose from 11% to 64% (2014–2024).

**Open-weight AI.** Open models are approximately 87% cheaper, near benchmark parity and 92% of foundation models adopted in science papers, yet hold less than 30% of inference usage; only 11.48% of notable 2024 models had unrestricted weights, and weights need not come with training data or code. For-profits are 14–18% less likely to open-source models, Big Tech approximately 20% more likely than other for-profits (Habibi 2025). NTIA (2024, via Massey 2024) chose a conditional approach over a blanket ban; Kapoor et al. (2024) find the evidence insufficient to characterize marginal risk.

**Shared infrastructure is cheap to run but easy to lose.** US RCSB PDB's 2023 activity budgets total about $7.5 million, and preservation costs about 1% of structure determination; a Zenodo-like platform is modeled at CHF 2.8 billion in potential benefit against CHF 11 million in costs (2028–2057). Yet grants are usually time-limited: Tranche and Peptidome closed after NIH support ceased, losing some data, and VEuPathDB lost support covering approximately 60% of operating costs in 2024. AI can add machine load: bots made 48.2% of PRIDE downloads ([flag] not shown to be AI crawlers). Unproven proposals: fund recurring work, pool beneficiaries' contributions (AI firms' included), and charge for high-capacity service, not data, as OpenAlex does.

## 3. Where studies disagree or measure different things

- **Five objects, not one number.** $4.15B (cost to write), $8.8T (cost to replace), $36.2B–$38.44B (US investment, 2019), €65B–€95B (modeled EU impact) and 2.2% of GDP are not rival estimates.
- **Use value vs willingness to pay.** PDB's $5.5B "use value" is time spent; its $760M willingness to pay is borrowed from EMBL-EBI; neither is attribution, and Edison says they "should not be added together".
- **Budgets, grants and models.** RCSB's 2023 budgets (about $7.5 million) cover three activities, not the worldwide PDB; COS's $7 million (2019) is the whole organization, not OSF; OpenAlex's $7.5 million is a five-year grant; Zenodo's CHF figures model a comparable future platform.
- **Association vs causation.** Battelle's $141 per federal dollar counts associated activity; causal designs find smaller, non-dollar effects (12–27% more patent citations; approximately 20–30% less downstream research under Celera's restrictions). Bryan & Ozcan find no academic-citation gain, against an approximately 8% open-access citation advantage in meta-analyses. The link between industry cloud credits and closed models (104,226 papers) is also only an association.
- **Citations vs downloads.** Talirz et al.'s "at least about 90%" counts *source-available* code, not only open source; testing inflates pymatgen downloads, and bots made 48.2% of PRIDE downloads. Materials-database citation counts attach to single papers, with no common date.
- **Computed vs made.** OQMD counts compounds, AFLOW entries, NOMAD and OMat24 calculations, Alexandria structures. Alexandria's 74,000 newly predicted stable materials are DFT results, not syntheses like AFLOW's eight borides.
- **Market vs activity.** Clinical laboratory automation ($5.57–6.1 billion, 2023), 352 SDL papers and 15 example cloud labs measure different things; none is an SDL market size.
- **Participation vs business model.** Firm studies measure using or contributing to OSS, not selling it.
- **Price vs total cost.** Pearce calls his ROI conservative; SDL authors say omitted labor can reverse a one-off build's price advantage. OT-2 quotes run from approximately $7,500 (starting) to approximately $20,000–30,000 (configured). Emerald Cloud Lab's $24,000 per month for three concurrent experiments (Arnold 2022) and its more than $250,000 minimum commitment (Doloi et al. 2025; [flag] unverified) are different price bases.
- **Publication vs disclosure.** The Transparency Index scores disclosure, not papers or open weights. The AI Index's industry-only counts (17, 19, 7 for 2021–2023) cover only the 100 most-cited papers, and Google DeepMind's 2023–2024 fall is within one generative-AI corpus.
- **Denominators.** Open weights: less than 30% of inference usage, 11.48% of notable models (unrestricted), 92% of science adoptions. Industry: 96% of the *largest* models (2021), 90.2% of *notable* ones (2024); academia: 84.9% of AI *publications* (2023).

## 4. Gaps

- **AI attribution:** Edison found no study that credibly assigns dollars or a value share of AlphaFold or ML materials discovery to open data or open-source software, and [flag] no database-specific benefit, benefit–cost ratio or ROI for the Materials Project, OQMD, AFLOW, NOMAD, JARVIS, Alexandria or OMat24.
- **Physical-science data:** no monetized Materials Project study; [flag] budgets for the seven materials databases generally undisclosed; [flag] date and scope of any database-wide licence change unestablished (the 2025 Materials Project paper is CC BY-NC 4.0); [flag] no platform-wide count of JARVIS-enabled syntheses; [flag] Landsat and 2020 EMBL-EBI costs missing from cited excerpts.
- **Open-weight AI:** no consumer-surplus figure ([flag] Nagle & Yue 2025 not obtainable); marginal misuse risk uncharacterized.
- **Industry publishing:** no annual 2018–2026 series of industry AI papers; [flag] Meta may be undercounted in the generative-AI paper count; [flag] Transparency Index changes are not like-for-like.
- **Firms:** no controlled OSS-vs-proprietary comparison of valuation, growth, IPO or survival, or of relicensing's financial effect; [flag] Nagle 2019 unavailable.
- **Lab hardware and SDLs:** [flag] no verified revenue, customer counts, profitability, valuation or exit for Emerald Cloud Lab, Strateos or Opentrons; [flag] no SDL market size or growth rate (the only market figure is for clinical automation); SparkFun, Adafruit and Atinary claims unsubstantiated; no multi-site drift, downtime or failure data; few independently reproduced autonomous-discovery loops.
- **Scientific software:** [flag] no financials for VASP, Gaussian, ANSYS, COMSOL or Schrödinger; no consulting-revenue figure for any named open package.
- **Infrastructure:** [flag] no verified current annual budget for Zenodo or OpenAlex, and arXiv's cost figure is a 2012 projection; [flag] no measure of AI crawlers' share of repository traffic or its bandwidth cost; financing proposals (pooled beneficiary funds, high-volume service charges) unproven.
- **Policy:** no measure here of the Nelson memo's effect; no denominator for national-lab software; [flag] the headline open-access share (at least 28%) rests on a mislinked source.
- **Coverage:** the open-science scoping review found 27 studies, concentrated in the US and UK; theorized harms of mandatory sharing lack empirical support.

## 5. US-specific numbers

Sources are as in the tables unless named.

- **OSS investment:** $0.733B (2009) to $38.44B (2019), revised $36.2B; real capital stock >$118B; total software investment about $492B (2019).
- **Apache (2012):** $514 million to $12.8 billion replacement value; 10.5%–14% return on $400 million of NSF and DARPA Internet R&D (Greenstein & Nagle 2013/2014).
- **Firms:** about 133 additional ventures (2017) per 1% more commits; approximately 4%–5% higher gross margin (977 firms); at least 36% higher first-funding likelihood (160,065 startups).
- **OSS subsidies:** US support cuts global web-development costs about three times as much as a comparable Chinese subsidy, because firms mostly use US-built OSS (Gortmaker, 2026 draft).
- **Human Genome Project:** $3.8B federal; $796B output (1988–2010); $141 per federal dollar.
- **Landsat:** US-user benefits $1.79 billion (2011), $2.06 billion (2017).
- **PDB:** RCSB's 2023 federal budgets (NSF, NIH and DOE) about $7.5 million: $2.8 million curation, $2.2 million preservation, $2.5 million dissemination; about 10,000 issued US patents mention PDB data (2022) (Berman & Burley 2025).
- **NIH mandate (2008):** about 50 percentage points more free availability; 12–27% more patent citations.
- **Federal support withdrawn:** Tranche and Peptidome closed after NIH support ceased; NIAID ended VEuPathDB support, approximately 60% of its operating costs, in September 2024 (Imker 2025).
- **Materials Genome Initiative:** $123.229B–$270.047B/year potential (2013 dollars).
- **Materials Project (a DOE resource):** 178,627 materials and more than 600,000 registered users (2025); [flag] budget not disclosed.
- **DARPA SD2 Round Trip:** nearly 100 experiments on Strateos's cloud lab by 2022; design and analysis roughly two orders of magnitude faster.
- **Federal access:** 1,326,472 federally funded papers (2017–2021), about 26% closed access (2017–2020), nearly 32% (2021); Holdren threshold over $100 million R&D; NIH data policy from January 25, 2023 (Bulock 2023; Spector-Bagdady et al. 2024).
- **DOE laboratories:** 2,005 public repositories; 3,760 Code.gov projects, 76% on GitHub (Barker et al. 2025; Shrivastava & Korkmaz 2024).
- **AI:** 40 notable US models in 2024, against 15 from China.
