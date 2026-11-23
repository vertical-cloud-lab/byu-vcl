# Edison synthesis for issue #380: the value of open science in the age of AI

Built only from the nine `<key>_answer.md` files in this folder (queries in `_task_ids.json`). Numbers are quoted as they appear there. Sources are named as Edison cited them, with "via" where Edison cited only a secondary source. **[flag]** marks a limitation Edison itself raised: an unobtainable source, an unsubstantiated figure, or a trend that is not like-for-like.

## 1. Findings by job

### `oss_economic_value`

| Finding | Number(s), units, year | Source | Caveat |
|---|---|---|---|
| Global OSS value, supply vs demand side | $4.15B to produce; $8.8T to replace; about 2,120× | Hoffmann, Nagle & Zhou 2024, via Osborne et al. 2024 | Different concepts; working paper |
| US OSS investment | $0.733B (2009) to $38.44B (2019); revised $36.2B (2019), approximately 50% of own-account software investment | Robbins et al. 2021; Santiago Calderón et al. 2022 | GitHub only; COCOMO II assumptions; possible double counting |
| EU impact, 2018 | about €1B personnel investment; €65B–€95B impact; benefit–cost above 4:1 with all costs | Blind et al. 2021 | Commission report, not peer reviewed |
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
| Savings, open vs proprietary lab hardware | 87% average (119 articles); Arduino-based 89%, 3D-printed 92%, both 94% | Pearce 2020 | Materials vs purchase price; comparable price for only 37.8% of devices |
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
| Relicensing (Elastic, HashiCorp, Redis) | Redis: 12 outside contributors in the year before, zero in six months after; Valkey fork: 29 at 10 companies (2024); no clear evidence vendors' finances improved | Foster 2024 | Cases chosen because forks occurred; [flag] the finance finding is not a controlled zero |
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
| Minimal self-driving lab | $68.61 required parts (March 2022) | Baird & Sparks 2023 | Teaching demo; [flag] the *Matter* paper was not available in full |
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
| Share of AlphaFold or ML-materials value due to open inputs | none found | Edison precedent search | No restricted-access counterfactual |
| PDB value measures (2016 activity) | $5.5B/year use value (users' time at $58.50/hour); $760M/year willingness to pay ($2,573 per user); $1.1B/year conservative R&D return | Sullivan et al. 2017 | Repository-wide; predates AlphaFold2; "cannot be attributed 100% to RCSB-PDB" |
| Materials Genome Initiative infrastructure | $123.229B–$270.047B/year potential US benefit (2013 dollars) | Scott et al. 2018 (NIST) | Prospective; nothing allocated to databases or ML |
| GNoME | 381,000 newly predicted stable materials (2023) | Merchant et al. 2023 | No dollar value |
| Openness counterfactual (genomics) | approximately 20–30% less downstream research and product development under Celera's restrictions | Williams 2013 | Not AI; not monetized |

## 2. Cross-cutting conclusions

**Value far exceeds cost; producers capture little of it.** Wherever value is set against cost the gap is wide: $8.8T against $4.15B for OSS (a "risk of underproduction", in Osborne et al.'s words); €65B–€95B from about €1B of EU contributions; PDB use value approximately 797× its operating cost. The gains spill outward. The global OSS stock raises GDP while a country's own contributions can lower its measured GDP (Blind & Schubert), and US support cuts global web-development costs about three times as much as a comparable Chinese subsidy, because firms mostly use US-built OSS (Gortmaker). Firms gain from engaging with OSS, but the evidence establishes no valuation, growth, IPO or survival premium for selling it, and relicensing shows no clear financial improvement. Hardware firms capture value through brand, expertise and speed, not design exclusivity.

**Software, hardware, physical sciences.** Evidence is deepest for software (national accounts, GDP, venture formation). Open-hardware evidence is mostly device-level savings and single-case ROI, and hardware carries manufacturing and compliance costs and weaker licence protection; Prusa has moved to layered openness. Physical-science codes run largely on public money (US DOE for LAMMPS and pymatgen, EU MaX for Quantum ESPRESSO) and foundations: free distribution "shifts the financing problem" to securing maintenance labor. Paid codes still led free ones in citations over the 2010s. Open materials data shows reach (Materials Project 600,000+ users) but, unlike Landsat imagery, no monetized return.

**Academia, government, industry over time.** The sectors moved in opposite directions. US corporations published less science over 1980–2007, yet industry came to dominate frontier AI: 96% of the largest models by 2021, and 90.2% of notable models in 2024, none from academia or government alone. Federal policy moved toward openness, from Holdren (2013) to Nelson (2022: all funders, immediate access) and NIH's 2023 data policy; national laboratories release software, but conditionally. Code-and-data sharing at AI conferences rose from 11% to 64% (2014–2024). In science, public funding is associated with open-weight use, and private funding and cloud credits with closed, API-only use (Trišović & Sivaloganathan 2026).

**Open-weight AI.** Open models are approximately 87% cheaper, near benchmark parity and 92% of foundation models adopted in science papers, yet hold less than 30% of inference usage; only 11.48% of notable 2024 models had unrestricted weights. Open releases appear to shift expected rents from compute toward software firms. For-profits are 14–18% less likely to open-source models, Big Tech approximately 20% more likely than other for-profits (Habibi 2025). NTIA (2024, via Massey 2024) chose a conditional approach over a blanket ban; Kapoor et al. (2024) find the evidence insufficient to characterize marginal risk.

## 3. Where studies disagree or measure different things

- **Five objects, not one number.** $4.15B (cost to write), $8.8T (cost to replace), $36.2B–$38.44B (US investment, 2019), €65B–€95B (modeled EU impact) and 2.2% of GDP are not rival estimates; even the US figure moved with revised data and methods.
- **Use value vs willingness to pay vs attribution.** PDB's $5.5B "use value" is time spent; its $760M willingness to pay is borrowed from EMBL-EBI; neither is attribution, and Edison says the figures "should not be added together".
- **Association vs causation.** Battelle's $141 per dollar counts associated activity; causal designs find smaller, non-dollar effects (12–27% more patent citations; 20–30% less research under Celera's restrictions). Bryan & Ozcan find no academic-citation gain, against an approximately 8% open-access citation advantage in meta-analyses.
- **Citations vs downloads.** Talirz et al.'s "at least about 90%" of atomistic references counts *source-available* code, broader than open source; testing inflates pymatgen downloads.
- **Participation vs business model.** Firm studies measure using or contributing to OSS, not selling it.
- **Price vs total cost.** Pearce calls his ROI estimates conservative; SDL authors say omitted labor can reverse a one-off build's price advantage.
- **Denominators.** Open weights: less than 30% of inference usage, 11.48% of notable models (unrestricted), 92% of science adoptions. Industry: 96% of the *largest* models (2021), 90.2% of *notable* ones (2024).

## 4. Gaps

- **AI attribution:** no study assigns dollars or a value share of AlphaFold or ML materials discovery to open data or open-source software.
- **Physical-science data:** no monetized study of the Materials Project; [flag] Landsat and 2020 EMBL-EBI costs missing from cited excerpts.
- **Open-weight AI:** no consumer-surplus figure ([flag] Nagle & Yue 2025 not obtainable); marginal misuse risk uncharacterized.
- **Firms:** no controlled comparison of OSS and proprietary vendors' valuation, growth, IPO or survival, or of relicensing's financial effect; [flag] Nagle 2019 unavailable.
- **Lab hardware and SDLs:** [flag] no Opentrons financials; SparkFun, Adafruit and Atinary claims unsubstantiated. No multi-site data on drift, downtime or failure; few independently reproduced autonomous-discovery loops.
- **Scientific software:** [flag] no financials for VASP, Gaussian, ANSYS, COMSOL or Schrödinger; no consulting-revenue figure for any open package.
- **Policy:** no measured effect yet of the Nelson memo; no denominator for national-lab software; [flag] the "at least 28%" open-access share rests on a mislinked source.
- **Coverage:** the open-science scoping review found 27 studies, concentrated in the US and UK; theorized harms of mandatory sharing lack empirical support.

## 5. US-specific numbers

- **OSS investment:** $0.733B (2009) to $38.44B (2019), revised $36.2B; real capital stock >$118B; total software investment about $492B (Robbins et al. 2021; Santiago Calderón et al. 2022).
- **Apache (2012):** $514 million to $12.8 billion replacement value; 10.5%–14% return on $400 million of NSF and DARPA Internet R&D (Greenstein & Nagle).
- **Firms:** about 133 additional ventures (2017) per 1% more commits (Wright et al. 2020); approximately 4%–5% gross margin (977 firms); at least 36% higher first-funding likelihood (160,065 startups).
- **Human Genome Project:** $3.8B federal; $796B output (1988–2010); $141 per federal dollar (Battelle).
- **Landsat:** US-user benefits $1.79 billion (2011), $2.06 billion (2017) (Straub et al. 2019).
- **PDB:** about 10,000 issued US patents mention PDB data (2022) (Berman & Burley 2025).
- **NIH mandate (2008):** about 50 percentage points more free availability; 12–27% more patent citations (Bryan & Ozcan 2021).
- **Materials Genome Initiative:** $123.229B–$270.047B/year potential (2013 dollars) (Scott et al. 2018).
- **Federal access:** 1,326,472 federally funded papers (2017–2021), about 26% closed access (2017–2020), nearly 32% (2021) (Schares 2023); Holdren threshold over $100 million R&D; NIH data policy from January 25, 2023.
- **DOE laboratories:** 2,005 public repositories; 3,760 Code.gov projects, 76% on GitHub (Barker et al. 2025; Shrivastava & Korkmaz 2024).
- **AI:** 40 notable US models in 2024, against 15 from China (Maslej et al. 2025). Edison notes Ahmed et al.'s industry shares are not US-only.
