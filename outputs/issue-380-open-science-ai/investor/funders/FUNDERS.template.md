# Who funds open-source-minded ventures? (issue #380, round 2, part 3)

Sterling asked for *"a list of investors, firms, philanthropists, and other VC and VC-like sources that have been
involved in funding a venture that falls into the more open-source minded of startups. Be thorough and manual."*
This folder is that list.

- **[`FUNDER_LIST.md`](FUNDER_LIST.md) lists every funder found**, grouped by type, with each venture it backed
  linked to a page that names it.
- **This file** summarises the list, says what it shows and how far to trust it.
- **[`data/`](data/) holds the tables**:
  - every round (`deals.csv`)
  - every funder–venture pair (`investor_links.csv`)
  - every funder (`investors.csv`)
  - every program-level funder (`programs.csv`)

The scope and counting rules were committed before any funding data was gathered ([`PROTOCOL.md`](PROTOCOL.md),
`448c8c2`).

## Bottom line

- **The list is long and flat.** Across the {{U1-U3.researched}} hand-researched ventures in groups U1–U3,
  {{U1-U3.with_funding}} disclosed outside funding.
  - Public sources name {{U1-U3.funders}} distinct funders across {{U1-U3.rounds}} rounds, {{U1-U3.rounds_named}}
    of which name at least one funder. A round reported by two sources counts once. Acquisitions, buyouts, IPOs and
    secondary share sales are listed but not counted, because no money went to the venture.
  - {{U1-U3.funders_1}} of those funders appear in only one venture.
  - Only {{U1-U3.funders_5plus}} backed five or more, and the ten most frequent account for
    {{U1-U3.top10_share_of_links}} of all funder–venture links.
  - There is no small club that funds open source. There is a long tail with a recognisable head.
- **The head is mostly generalist venture firms, an accelerator and chip and cloud companies:**
  - Y Combinator, by count.
  - Accel, Sequoia, Andreessen Horowitz, NEA, Index, Benchmark, Lightspeed and Insight.
  - Corporate investors, counted across all four groups with their arms rolled up to the parent:
    - Alphabet: GV, CapitalG, Gradient and Google together, {{groups.alphabet}} ventures
    - Intel Capital ({{groups.intel}}) and NVIDIA ({{groups.nvidia}})
    - Microsoft: M12, GitHub and Microsoft, {{groups.microsoft}}
    - Samsung ({{groups.samsung}}) and Salesforce Ventures ({{groups.salesforce}})
  - The firms that lead open-source rounds most often are Andreessen Horowitz, Accel, Insight, NEA, Sequoia,
    Lightspeed, Index and Benchmark.
- **The funds most associated with open source are small in this count.**
  - OSS Capital has {{focus.oss_capital}} ventures across all four groups and Uncorrelated Ventures
    {{focus.uncorrelated_ventures}}, against {{focus.bessemer_venture_partners}} for Bessemer and {{focus.gv}} for GV.
  - Runa Capital ({{focus.runa_capital}}), Heavybit ({{focus.heavybit}}), Boldstart ({{focus.boldstart_ventures}}),
    Crane ({{focus.crane_venture_partners}}) and Open Core Ventures ({{focus.open_core_ventures}}) back only a handful
    each.
  - Only two funders in the data have a dedicated open-source mandate: OSS Capital and Open Core Ventures.
    {{thesis_kinds.named_focus_or_program}} more name open source as a focus or run a program for it: Andreessen
    Horowitz, Index, Runa and Databricks Ventures. Another {{thesis_kinds.partner_remark}} have had a partner quoted
    on open source, mostly in TechCrunch's 2020 survey of investors, which shows interest rather than a mandate.
- **People are a large share of the funders.** Many of the most frequent angels founded or led open-source
  companies themselves, and now back the next ones (ventures here, all groups):
  - Guillermo Rauch of Vercel ({{focus.guillermo_rauch}}), Clem Delangue of Hugging Face ({{focus.clem_delangue}}) and
    David Cramer of Sentry ({{focus.david_cramer}})
  - Tom Preston-Werner ({{focus.tom_preston_werner}}) and Nat Friedman ({{focus.nat_friedman}}) of GitHub, Paul
    Copplestone of Supabase ({{focus.paul_copplestone}}) and Tristan Handy of dbt Labs ({{focus.tristan_handy}})
- **Open hardware, open science and lab ventures (U2) draw a wider mix.** Venture firms are still the most common
  type: {{u2_types.venture_firm.ventures}} of the {{U2.ventures}} U2 ventures have one. Alongside them:
  - Strategic corporates ({{u2_types.corporate_venture.ventures}} ventures): Bosch, Renesas, Arm, Qualcomm, Sony,
    Intel and NVIDIA.
  - Crowdfunding ({{u2_types.crowdfunding.ventures}} ventures; Kickstarter backers alone, {{u2_kickstarter}}).
  - Hardware-minded venture firms: True Ventures, Foundry Group, Spark Capital, Khosla, Eclipse and Lux.
  - Grants: SBIR, NSF, NIH, Shuttleworth, CZI, Sloan and Moore; for DeSci, crypto funds.
  - Only {{U2.funders_3plus}} funders backed three or more of the {{U2.ventures}} ventures in this group.
- **Philanthropy and government fund open source mostly at the program level**, and mostly not through companies.
  - Programs: CZI, Sloan, Moore and Schmidt Sciences; DOE's Exascale Computing Project; NSF's POSE and CSSI;
    Germany's Sovereign Tech Agency; the EU's NGI grants through NLnet.
  - Recipients are mostly projects, universities and nonprofits.
- **Read the list as a disclosed, selectively researched inventory, with omissions and some false inclusions.** Its
  counts are neither estimates for the whole population nor guaranteed lower bounds.
  - {{source_check.share_found}} of the investor names in counted rounds appear in the text of the page their round
    cites. That shows the name is on the page, not that the page shows an investment.
  - Before its rounds were merged in, Edison's blind audit of 40 random ventures found
    {{edison_audit.ours_confirmed_by_edison}} of this list's names for those ventures. It also found about
    {{edison_audit.edison_names}} funders where this list then had {{edison_audit.our_names}}, mostly smaller
    participants, angels, grants and lenders.
  - Edison's independent review of a first draft found errors that are now fixed: exits and buyouts counted as
    funding, six companies entered twice, nonprofits and closed products in the counts, and funders split across two
    names. See [Edison's review and what changed](#edisons-review-and-what-changed).
- **Nothing here says these funders made money on open source, or that they would fund a given venture.** The list
  records who put money in, as disclosed. Disclosure favours large rounds and survivors.

![Who has backed the most open-source-minded ventures](figures/top_funders.png)

## The funders that backed the most open-source-minded ventures (U1–U3)

One count per venture, however many rounds; "led" counts ventures where the funder led at least one round.
Examples list led ventures first. Full list: [`FUNDER_LIST.md`](FUNDER_LIST.md).

<!-- TABLE:top_all_u123.md:40 -->

### Young open-source startups (U4)

All 402 startups taken from the ROSS Index and Y Combinator's directory were researched. {{U4.out_of_scope}} are
out of the counts: six were the same company as another entry, five are nonprofits, and six have a main product
that is not open. Of the other {{U4.ventures}}, {{U4.with_funding}} have disclosed funding, most of it only Y
Combinator's. The funders that appear most often:

<!-- TABLE:top_u4.md:20 -->

## By kind of funder

![Who funds which kind of open venture](figures/funder_mix.png)

<!-- TABLE:type_mix.md -->

### What investors say about open source

Quoted from the firm's own page or from a public interview. The count is ventures in this data, U1–U4. The kind of
statement matters: only a dedicated mandate or a named focus or program says the firm invests in open source as
such. A partner's remark in an interview shows interest; a portfolio-company description or a mission statement
says little about the firm's own policy.

<!-- TABLE:thesis.md -->

### Corporate and strategic investors

Investment arms rolled up to their parent:

<!-- TABLE:corporate_groups.md:12 -->

Individually:

<!-- TABLE:top_corporate.md:25 -->

### Accelerators

- **Y Combinator** is the largest single source of early money for open-source startups in this data.
  - YC's own directory lists **183 companies tagged open source**, and **289 tagged or described as open source**
    ([`data/yc_open_source.csv`](data/yc_open_source.csv), from the yc-oss mirror of the directory, 2026-11-25).
  - Most of them are from 2020 on.
- **Other accelerators** appear far less often: HAX/SOSV for hardware (Opentrons, Particle, Crowd Supply), Neo,
  Antler, 500 Global, AI Grant, South Park Commons and Techstars.
- **Open Core Ventures** is a studio that builds companies around existing open-source projects.

<!-- TABLE:top_accelerators.md:12 -->

### People (angels)

<!-- TABLE:top_angels.md:30 -->

### Growth, crossover and state investors

These join later and larger rounds, mostly of AI and infrastructure companies:

<!-- TABLE:top_growth.md:20 -->

### Who joins early rounds (pre-seed, seed, angel, accelerator, Series A; U1–U4)

Counted rounds only, one count per funder per round. A Series A can be a repeat investment, so this is not a list of
first cheques.

<!-- TABLE:top_early.md:30 -->

## Open hardware, open science, lab and science-software ventures

Group U2 plus the U1 companies that part 2 found through GitHub's 22 science topics. These are the comparables for
DAL and the SDL kit. Every venture with its funders is in
[`data/tables/science_hardware_ventures.md`](data/tables/science_hardware_ventures.md).

<!-- TABLE:top_science_hardware.md:35 -->

### U2 by kind of venture

The {{U2.ventures}} U2 ventures, sorted by hand into nine kinds ([`data/u2_kinds.csv`](data/u2_kinds.csv)). Shares are
of the funder–venture links within each kind. Even within a kind, few funders recur. Lab-automation, instrument and
lab-software companies, the closest comparables for DAL and the SDL kit, are few here, with few named funders; Opentrons,
the best known, is in U1 because it came in through GitHub's science topics.

<!-- TABLE:u2_by_kind.md -->

What stands out, reading the venture table rather than the counts:

- **Few repeat backers.** Only {{U2.funders_3plus}} funders backed three or more of the {{U2.ventures}} U2 ventures; most funders
  of open hardware and science appear once. A general list of open-source investors is a weak guide here.
- **Kickstarter backers are the most frequent single funder name in U2** ({{u2_kickstarter}} ventures), but by
  type venture firms are more common: {{u2_types.venture_firm.ventures}} U2 ventures have a venture firm,
  {{u2_types.corporate_venture.ventures}} a corporate investor and {{u2_types.crowdfunding.ventures}} a crowdfunding
  campaign. Kickstarter, Crowd Supply and equity-crowdfunding campaigns funded OpenBCI, Opentrons, Pine64, Bela, OpenMV, Luxonis, Backyard Brains, Great Scott Gadgets, Printrbot,
  MicroPython, MNT Research, LimeSDR, Purism and Mycroft AI, among others.
- **Grants carry the science-software companies.**
  - SBIR/STTR grants from NSF, NIH, DOE, NASA and the Space Force funded Kitware, Enthought, re:3D, Backyard
    Brains, Hello Robot, Open Imaging and PickNik.
  - CZI funded Seqera.
  - Sloan and Moore funded Julia Computing (now JuliaHub); Moore also funded Continuum Analytics (now Anaconda).
  - The Shuttleworth Foundation seeded FarmBot.
  - EU, French, German and Spanish public money funded BCN3D, Probabl, mzio, HARFANG 3D and Pollen Robotics.
- **Large open-hardware rounds come from deep-tech venture firms and strategic corporates.** For example:
  - SiFive: Sutter Hill, Spark, Osage, Qualcomm, Intel, SK hynix, Aramco, Coatue.
  - Tenstorrent: Eclipse, Fidelity, Samsung, Hyundai, LG, Bezos Expeditions.
  - Oxide: Eclipse, USIT, Intel Capital.
  - Arduino: Bosch, Renesas, Arm, Anzu, CDP.
  - Raspberry Pi: Sony, Arm.
  - Framework: Spark.
- **Lab automation draws accelerator money, consumer and growth investors, and climate funds.**
  - Opentrons: HAX/SOSV, Kickstarter backers, Y Combinator, then Khosla Ventures, Lerer Hippeau and SoftBank's
    Vision Fund.
  - Trilobio: Initialized, Lowercarbon and others.
  - PickNik: Stellar Ventures and SBIR awards.
- **AI-for-science companies that release models or tools are funded like AI companies.**
  - EvolutionaryScale: Nat Friedman, Daniel Gross, Lux, NVIDIA, Amazon.
  - Chai Discovery: Thrive, OpenAI, Menlo, Dimension.
  - Orbital Materials: Radical, Plural, Toyota Ventures, NVIDIA.
  - Radical AI: RTX Ventures, NVIDIA, Eni, AlleyCorp.
  - Entalpic: Breega, Cathay, Felicis.
  - Boltz: Bessemer, Andreessen Horowitz, Amplify.
- **Open-science publishing and data businesses draw publishers.** Digital Science (Holtzbrinck) took stakes in
  Overleaf, Figshare and Authorea; Springer Nature bought protocols.io. Code Ocean raised from Battery, M12 and
  EBSCO. PeerJ, an open-access publisher, was backed by O'Reilly Media and OATV from its start and raised a second
  round led by SAGE and O'Reilly in 2014
  ([PeerJ](https://peerj.com/blog/post/91251985913/exciting-times-peerj-secures-next-round-of-funding-led-by-sage-and-oreilly/)).
- **DeSci draws crypto funds and a few angels.** VitaDAO, Molecule and LabDAO raised from L1 Digital, Shine, 1kx,
  Seed Club and IDTheory, from Balaji Srinivasan, and from Pfizer Ventures (VitaDAO).

### Using the list for DAL or the SDL kit

The funders closest to an open physical-science venture are in
[`data/tables/science_hardware_ventures.md`](data/tables/science_hardware_ventures.md), venture by venture, and in
the program tables below.
- To filter, use `data/investor_links.csv` with `universe` = U2, the kinds in `data/u2_kinds.csv`, or the
  ventures' `category` in `data/ventures.csv`.
- Before treating a name as a lead, check three things: what the funder backs now, whether it led or only joined,
  and how long ago.
- The early-round table above shows who joins, and who leads, open-source companies' rounds up to Series A.
- The nearest grant precedents found are Sloan's 2026 grants for an open liquid handler at Duke and for
  open-source autonomous chemistry through Renaissance Philanthropy, its open-hardware fellowships, and Tool
  Foundry's $50,000 awards for low-cost science tools (program tables below).
- The nearest public program is NSF's Programmable Cloud Laboratories test bed: $380M across 20 awardees, with up
  to $20M matched by the Astera Institute for open-science practice
  ([Astera, July 2026](https://astera.org/astera-partnering-with-the-national-science-foundation/)). The awardees
  are not named on that page, and whether companies can take part was not checked.
- A grant to a university is not evidence that the same funder would finance a company.
- The list says who has done this before. It says nothing about who would do it again, or on what terms.

## Philanthropists and foundations

Most of this money goes to projects, universities and nonprofits, not to companies. Sizes are as each source
states them, committed unless marked, over different periods; some overlap, so they can't be added up. "→ firms"
says whether for-profit companies can receive it. Full rows: [`data/programs.csv`](data/programs.csv) (passes p1–p7,
with notes on how firm each figure is and a `check_note` where two rows describe the same money).

| Funder (people behind it) | Program | Years | Size reported | → firms | Recipients, for example |
| --- | --- | --- | --- | --- | --- |
| Chan Zuckerberg Initiative (Priscilla Chan, Mark Zuckerberg); Kavli Foundation and Wellcome joined in 2024 | [Essential Open Source Software for Science](https://chanzuckerberg.com/eoss/) | 2019– | $51.8M in 193 grants over its first five cycles ([CZI's 2024 report](https://zenodo.org/records/11201216)) | no | napari, scikit-image |
| Chan Zuckerberg Initiative | [Open science grants](https://chanzuckerberg.com/science/programs-resources/open-science/grants) | 2019– | n/a | no | bioRxiv, medRxiv, protocols.io, 2i2c, The Carpentries |
| Gordon and Betty Moore Foundation | [Data-Driven Discovery](https://news.berkeley.edu/2014/10/02/funding-for-big-data-projects-in-ecology-astronomy-microscopy) | 2013–18 | $60M | no | 14 Moore Investigators |
| Gordon and Betty Moore Foundation | open-source science software and open hardware ([grants database](https://www.moore.org/grant-detail?grantId=GBMF8599); 27 grants found) | 2006– | about $30M across those 27 | sometimes | Jupyter, Julia Computing, Numba and Dask (to Continuum Analytics), Astropy, Scientific Python, Pangeo, Binder, [Open Science Hardware Foundation](https://www.moore.org/grant-detail?grantId=GBMF13637), [Public Lab](https://www.moore.org/grant-detail?grantId=GBMF7725) |
| Moore, Sloan and Helmsley foundations | [Project Jupyter](https://www.moore.org/newsroom/press-releases/2015/07/07/$6m-for-uc-berkeley-and-cal-poly-to-expand-and-enhance-open-source-software-for-scientific-computing-and-data-science) | 2015– | $6M | no | Jupyter (UC Berkeley, Cal Poly) |
| Alfred P. Sloan Foundation | [Open source in science](https://sloan.org/programs/digital-technology/open-source-in-science); [university OSPOs](https://sloan.org/programs/digital-technology/ospo-loi) | 2015– | $13.9M in 2025–26 alone ([grants database](https://sloan.org/grants-database?subprogram%5B%5D=44)) | no | NumFOCUS, JOSS, The Carpentries, Software Heritage, OSPOs at CMU, Johns Hopkins and the University of Texas; an [open liquid handler at Duke](https://sloan.org/grant-detail/g-2026-79582) ($250k) and [open-source autonomous chemistry](https://sloan.org/grant-detail/g-2026-79581) via Renaissance Philanthropy ($210k) |
| Howard Hughes Medical Institute, Wellcome, Max Planck Society | [eLife](https://en.wikipedia.org/wiki/ELife) | 2012– | $26M from HHMI (initial) | no | eLife |
| FUTO (Eron Wolf) | [microgrants](https://futo.tech/grants/) | 2023– | about $60k listed | no | Blender, KiCad, FFmpeg, GIMP, Asahi Linux |
| NumFOCUS (fiscal host, funded by its sponsors) | [Small Development Grants](https://numfocus.org/programs/small-development-grants) | 2017– | n/a | no | PyMC, GeoPandas, Julia, SciPy, pandas |
| Alfred P. Sloan Foundation with the Open Source Hardware Association | [Open Hardware Trailblazers fellowships](https://opensource.com/article/22/3/trailblazer-funding-open-hardware-academia) | 2022– | n/a | no | academic open-hardware leads |
| Schmidt Sciences (Eric and Wendy Schmidt) | [Virtual Institute for Scientific Software](https://engineering.jhu.edu/news/virtual-institute-scientific-software-johns-hopkins-schmidt-futures) | 2022–27 | $40M | no | Johns Hopkins, UW, Georgia Tech, Cambridge |
| Schmidt Futures and Ken Griffin | [Convergent Research (focused research organisations)](https://www.schmidtfutures.org/schmidt-futures-and-ken-griffin-commit-50-million-to-support-the-next-big-breakthroughs-in-science/) | 2021– | $50M | no | Forest Neurotech |
| Arnold Ventures (Laura and John Arnold) | [Center for Open Science](https://www.cos.io/about/news/center-open-science-receives-75-million-additional-funding-laura-and-john-arnold-foundation) | 2013–19 | $12.75M | no | COS, OSF |
| Arcadia Fund (Lisbet Rausing, Peter Baldwin) | OurResearch: [2021](https://blog.openalex.org/arcadia-2021-grant/), [2024](https://blog.openalex.org/?p=2066) | 2021–29 | $4.5M, then $7.5M | no | OpenAlex, Unpaywall |
| The Navigation Fund and Astera Institute (Jed McCaleb) | [open-science grants](https://blog.openalex.org/arcadia-2021-grant/); [Astera residency](https://astera.org/residency) | 2022– | n/a | sometimes | OpenAlex, 2i2c, Open Science Hardware Foundation |
| Shuttleworth Foundation (Mark Shuttleworth) | [fellowships](https://en.wikipedia.org/wiki/Shuttleworth_Foundation) | 2007–24 | n/a | no | Open Source Ecology, FarmBot (seed grant) |
| Kyutai founders: Xavier Niel (Iliad), Rodolphe Saadé (CMA CGM), Eric Schmidt | [Kyutai open-science AI lab](https://techcrunch.com/2023/11/17/kyutai-is-an-french-ai-research-lab-with-a-330-million-budget-that-will-make-everything-open-source/) | 2023– | about €300M | no | Kyutai |
| Paul G. Allen | [Allen Institute for AI](https://en.wikipedia.org/wiki/Allen_Institute_for_AI) | 2014– | n/a | no | OLMo, Semantic Scholar |
| Gil Elbaz | [Common Crawl](https://en.wikipedia.org/wiki/Common_Crawl) | 2007– | n/a | no | Common Crawl |
| Brian Armstrong | [ResearchHub](https://www.researchhub.com/about) | 2021– | $1.5M+ paid out | no | open peer review and bounties |
| Patrick Collison, Tyler Cowen and co-donors | [Fast Grants](https://en.wikipedia.org/wiki/Fast_Grants) | 2020–22 | $50M+ (about 250 grants) | no | COVID-19 research |
| Mozilla Foundation | [Mozilla Open Source Support](https://www.mozilla.org/moss) | 2015–20 | $3.5M+ | sometimes | open-source projects Mozilla relies on |
| Gates Foundation | [digital public infrastructure](https://www.biometricupdate.com/202209/gates-foundation-commits-200m-to-digital-id-and-other-public-infrastructure) | 2022– | $200M | sometimes | MOSIP, Mojaloop |
| Mellon Foundation | [open scholarly infrastructure](https://www.mellon.org/grant-details/code-for-science-and-society-inc.-20453350) | 2005– | n/a | no | Coko, Invest in Open Infrastructure, Code for Science & Society |
| Craig Newmark Philanthropies | [open-source security](https://www.memorysafety.org/blog/2026-craig-newmark/) | 2019– | n/a | no | ISRG Prossimo, Wikimedia |
| Renaissance Philanthropy with Biohub, Wellcome and Kavli | [Open Source for Science Fund](https://www.renaissancephilanthropy.org/insights/open-source-for-science-fund-launches) | 2026– | $20M | not stated | research software |
| Ford and Sloan foundations | [Digital Infrastructure Insights Fund](https://www.fordfoundation.org/the-latest/news/major-philanthropies-tackle-inequality-by-strengthening-how-open-source-code-is-developed-and-maintained/) | 2018– | $1.3M (2020 round) | no | research on open infrastructure |
| Stability AI, Hugging Face, Canva, CoreWeave and others | [EleutherAI Institute](https://techcrunch.com/2023/03/02/stability-ai-hugging-face-and-canva-back-new-ai-research-nonprofit) | 2023– | n/a | no | GPT-NeoX, The Pile |
| Gordon and Betty Moore Foundation and Schmidt Futures, through Luminary Labs | [Tool Foundry accelerator](https://www.toolfoundry.org/) for low-cost science tools | 2019 | $50,000 per team, five teams | sometimes | teams building science tools |
| Schmidt Futures, Moore Foundation and Footprint Coalition, through Experiment | [Low-Cost Tools for Science](https://experiment.com/grants/tools) challenge | | projects of about $10,000 each, crowdfunded | sometimes | dNinja open-source digital PCR, an open-source radio imager for plant health, Binomica Labs |
| Coefficient Giving | grants to [Our World in Data](https://ourworldindata.org/funding) and to the Center for Open Science's [LLM-agent benchmarking project](https://www.cos.io/benchmarking-llm-agents-on-scientific-tasks) | | n/a | no | Our World in Data, Center for Open Science |
| Thiel Foundation; Mercatus Center | [Thiel Fellowship](https://en.wikipedia.org/wiki/Thiel_Fellowship); [Emergent Ventures](https://en.wikipedia.org/wiki/Emergent_Ventures) | 2010–; 2018– | $250k per fellow; $1M launch grant | sometimes | individuals |

Philanthropy also reaches open-source companies directly, in the deal data:
- CZI granted to Seqera (Nextflow).
- Sloan granted to Julia Computing.
- Moore's grant pages name the company as the grantee: Julia Computing in 2015 and 2019
  ([GBMF4856](https://www.moore.org/grant-detail?grantId=GBMF4856), $600,000;
  [GBMF8433](https://www.moore.org/grant-detail?grantId=GBMF8433), $1,057,443) and Continuum Analytics, now
  Anaconda, for Numba and Dask in 2016 ([GBMF5423](https://www.moore.org/grant-detail?grantId=GBMF5423), $700,000).
- The Shuttleworth Foundation granted FarmBot its seed money.
- Knight Foundation co-led Authorea's 2016 round with Lux Capital.
- Jed McCaleb and Sam Altman fund Arcadia Science.

The funders of the five nonprofits that had been in U4 (Our World in Data, VotingWorks, Recidiviz, Democracy Earth
and the ARC Prize Foundation) are now in the program table, not the deal counts, as the protocol says: Wellcome, the
Gates Foundation, the Skip Foundation, Coefficient Giving and the Mohn Westlake Foundation for Our World in Data;
Democracy Fund, Schmidt Futures, the New Venture Fund, CISA, NSF and individual donors for VotingWorks; and Y
Combinator's nonprofit places for all five.

Several philanthropists also invest in open-source ventures in their own names (deal data):
- Xavier Niel: personally in Mistral AI, H Company and Odoo, and through Kima Ventures in 13 ventures, among them
  Docker, Strapi and Meilisearch.
- Eric Schmidt: H Company, Reflection AI and Stability AI, and through Innovation Endeavors.
- Bob Young, co-founder of Red Hat: AppFlowy, NocoDB, OpenBB, ResearchHub and Liquid AI.
- Mark Shuttleworth: Inktank.
- Jeff Bezos: Kong and Rescale, and through Bezos Expeditions MakerBot and Tenstorrent.
- Patrick Collison: Daytona and Logseq.

## Governments and public programs

Grants unless marked as investment. "→ firms" says whether companies can receive it.

| Government or public body | Program | Years | Size reported | → firms | Recipients, for example |
| --- | --- | --- | --- | --- | --- |
| US Department of Energy | [Exascale Computing Project](https://science.osti.gov/-/media/ascr/ascac/pdf/meetings/2024/ECP-OverviewASCACMay2024pptx.pdf) | 2016–24 | $1.8B (whole project, mostly open-source software) | no | E4S, Spack, about 70 software products |
| US National Science Foundation | [POSE (Pathways to Enable Open-Source Ecosystems)](https://www.nsf.gov/funding/opportunities/pose-pathways-enable-open-source-ecosystems) | 2022– | about $100M obligated across 146 awards (NSF awards API; approximate) | sometimes | ecosystem organisations around university projects |
| US National Science Foundation | [CSSI](https://simpler.grants.gov/opportunity/358751) (successor to SI2) | 2010– | $34M (one solicitation) | no | research software at universities |
| US National Science Foundation and NVIDIA | [Open Multimodal AI Infrastructure, led by Ai2](https://blogs.nvidia.com/blog/national-science-foundation-ai2-open-ai-models/) | 2025–30 | $152M ($75M NSF, $77M NVIDIA in kind) | no | Ai2's open models |
| NIH Office of Data Science Strategy | [Sustainable software tools for open science](https://grants.nih.gov/grants/guide/rfa-files/rfa-od-24-010.html) | 2020– | n/a | no | biomedical research software |
| NASA Science Mission Directorate | [open-source tools, frameworks and libraries; TOPS](https://science.nasa.gov/researchers/open-science/nasa-open-science-funding-opportunities) | 2020s– | $6.5M (one TOPS round) | no | open-science software |
| DARPA | [POSH open-source hardware](https://linux.com/?p=471279) and IDEA | 2018– | $35M+ (POSH) | sometimes | open-source chip-design tools |
| DARPA and ARPA-H | [AI Cyber Challenge](https://www.darpa.mil/news/2025/ai-cyber-challenge-winners-def-con-33) | 2023–25 | $8.5M in final prizes | yes | open-source cyber-reasoning systems |
| Open Technology Fund (US) | [FOSS Sustainability Fund](https://docs.opentech.fund/otf-application-guidebook/our-funds-and-fellowships/free-and-open-source-software-foss-sustainability-fund) | 2012– | n/a | sometimes | Tor, Signal |
| In-Q-Tel (US intelligence community), investment | [stakes in open-source companies](https://techcrunch.com/2012/09/18/mongodb-maker-10gen-closes-undisclosed-round-from-u-s-intelligence-investors/amp/) | 2009– | n/a | yes | 10gen (MongoDB), Lucidworks, Cloudant, D2iQ |
| US SBIR/STTR (NSF, NIH, DOE), in the deal data | small-business grants | | | yes | Kitware, Enthought, re:3D, Backyard Brains |
| Germany: Sovereign Tech Agency | [Fund, Resilience, Fellowship, Challenges](https://www.sovereign.tech/tech) | 2022– | €11.5M in its first year (Osborne et al. 2024, via Edison) | sometimes | curl, OpenSSH, systemd, PHP, conda-forge |
| Germany: Prototype Fund (research ministry) | [grants to individuals](https://prototypefund.de/en/faq) | 2016– | n/a | no | civic and open-source prototypes |
| EU: Next Generation Internet, via NLnet | [NGI Zero Entrust, Core, Commons Fund](https://nlnet.nl/NGI0/) | 2020s– | n/a | sometimes | F-Droid, Pixelfed, open-hardware projects |
| EU: European Innovation Council | [EIC Accelerator](https://eic.ec.europa.eu/news/38-start-ups-and-smes-secure-eic-support-latest-round-eic-accelerator-2026-06-15_en) (grant plus equity) | 2021– | n/a | yes | deep-tech start-ups |
| France: national AI strategy | scikit-learn and open data-science tools (Osborne et al. 2024, via Edison) | 2021– | €32M announced | not stated | scikit-learn (later Probabl) |
| France: Bpifrance, investment | [AI plan](https://www.bpifrance.com/2025/03/27/bpifrance-deploys-e10-billion-to-develop-the-ai-ecosystem-and-facilitate-the-adoption-of-artificial-intelligence-by-french-companies), stakes | 2023– | €10B plan to 2029 | yes | Mistral AI, AMI Labs, Pollen Robotics, Probabl |
| US National Science Foundation with the Astera Institute | [Programmable Cloud Laboratories test bed](https://astera.org/astera-partnering-with-the-national-science-foundation/) | 2026– | $380M from NSF across 20 awardees, plus up to $20M matched by Astera | not stated | automated, cloud-accessible lab infrastructure (awardees not named on the page) |
| UK: UKRI (EPSRC, MRC) and the Royal Society | [grants and fellowships behind the OpenFlexure microscope](https://openflexure.org/about/funding), including EPSRC's "Open Lab Instrumentation" | 2017– | n/a | no | OpenFlexure, a university-led open microscope project |
| UK: UKRI and the Software Sustainability Institute | [Research Software Maintenance Fund](https://www.software.ac.uk/research-software-maintenance-fund/round-2) | 2022– | n/a | no | research software |
| Netherlands, Australia, Canada | [eScience Center](https://www.esciencecenter.nl/about-us/), [ARDC](https://www.ardc.edu.au/about/), [CANARIE](https://www.canarie.ca/software/) | | n/a | no | research software and data |
| China: state and municipal funds, investment | [Zhipu AI and others](https://www.caixinglobal.com/2025-07-03/chinas-zhipu-ai-secures-140-million-investment-from-shanghai-state-funds-amid-ipo-push-102337464.html) | 2024– | n/a | yes | Zhipu AI, MiniMax, DeepSeek |
| Singapore: GIC and Temasek, investment | [open-weight AI and open-source companies](https://techcrunch.com/2025/10/09/reflection-raises-2b-to-be-americas-open-frontier-ai-lab-challenging-deepseek/) | 2025– | n/a | yes | Reflection AI, AMI Labs, Supabase, ClickHouse |

## Corporate open-source funds, platforms, crypto public goods and crowdfunding

| Funder | Program | Years | Size reported | → firms | Notes |
| --- | --- | --- | --- | --- | --- |
| GitHub (Microsoft) | [GitHub Sponsors](https://github.blog/open-source/maintainers/100-million-for-open-source-a-milestone-built-by-the-community/) | 2019– | $100M paid out cumulatively | sometimes | maintainers and projects |
| GitHub with M12 | [GitHub Fund and GitHub Accelerator](https://github.com/open-source/accelerator) | 2023– | GitHub reports "$130MM+ invested in open source" | yes | ToolJet, Unsloth |
| GitHub | [Accelerator, 2023 cohort](https://github.blog/2023-04-12-github-accelerator-our-first-cohort-and-whats-next/) | 2023 | $20k for each of 20 projects | sometimes | htmx, Nuxt, Datasette, tRPC, Dioxus, Formbricks |
| Andreessen Horowitz | Open Source AI Grant, batches [1](https://a16z.com/2023/08/30/supporting-the-open-source-ai-community/), [2](https://a16z.com/announcing-our-latest-open-source-ai-grants/), [3](https://a16z.com/advancing-open-source-ai-through-benchmarks-and-bold-experimentation/) | 2023– | n/a | no (equity-free) | TheBloke, Axolotl, SkyPilot, LMSYS, SGLang, Open WebUI's author |
| Nat Friedman and Daniel Gross | [AI Grant](https://aigrant.com/) | 2017– | $250k SAFE per startup in recent batches | yes | ggml, Replicate, Browserbase, Perplexity |
| OSS Capital (Joseph Jacks) | [three seed funds for commercial open source](https://techcrunch.com/2024/10/20/joseph-jacks-bets-on-open-source-startups-a-paradox-of-philanthropy-and-capitalism/) | 2018– | about $150M (three funds of about $50M) | yes | Cal.com, AppFlowy, Plane, Hoppscotch, OpenBB, W4 Games |
| Open Source Endowment | [endowment for maintainers](https://endowment.dev/) | 2026– | $0.77M | no | maintainers |
| GitHub with partners | [Secure Open Source Fund](https://techcrunch.com/2024/11/19/github-launches-1-25m-open-source-fund-with-a-focus-on-security) | 2024– | $1.25M | no | security of critical projects |
| Microsoft, Google, Amazon, Citi and others | [OpenSSF Alpha-Omega](https://openssf.org/community/alpha-omega/) | 2022– | $12.5M (2026 round) | no | security of critical projects |
| Sentry and member companies | [Open Source Pledge](https://opensourcepledge.com/) | 2024– | $9.8M pledged | no | $2,000 per developer a year to maintainers |
| Zerodha | [FLOSS/fund](https://zerodha.com/open-source/2025-report/) | 2024– | $1M a year | no | Krita, OpenSSL, FFmpeg, Blender |
| Bloomberg, Indeed, Spotify, Microsoft | FOSS contributor funds ([Bloomberg](https://www.bloomberg.com/company/stories/bloomberg-ospo-launches-foss-contributor-fund), [Indeed](https://github.com/indeedeng/FOSS-Contributor-Fund), [Spotify](https://engineering.atspotify.com/2022/4/announcing-the-spotify-foss-fund), [Microsoft](https://github.com/microsoft/foss-fund)) | 2019– | about $10,000 per award | no | projects the sponsor depends on |
| Google | [Summer of Code](https://opensource.googleblog.com/2025/08/google-summer-of-code-2025-contributor-statistics.html); [Open Source Peer Bonus](https://opensource.googleblog.com/2024/06/google-open-source-peer-bonus-program-first-group-2024-recipients.html) | 2005– | n/a | no | 1,280 contributors in 2025 |
| Meta | [Llama Impact Grants](https://ai.meta.com/blog/llama-3-1-impact-grants-call-for-applications/) | 2023–25 | $0.5M, then $2M | yes | CognitiveLab |
| Sequoia; Andreessen Horowitz | [Open Source Fellowship; Open Source AI Grant](https://techcrunch.com/2024/11/10/open-source-projects-draw-equity-free-funding-from-corporates-startups-and-even-vcs/) | 2023– | n/a | no (equity-free) | FastAPI's author, vLLM, LMSYS |
| Mozilla | [Mozilla Ventures](https://techcrunch.com/2022/11/02/mozilla-launches-35m-venture-capital-fund-for-early-stage-responsible-startups) (investment); [Builders Accelerator](https://blog.mozilla.org/en/mozilla/14-ai-projects-to-watch-mozillas-first-builders-accelerator-cohort-kicks-off/) | 2022– | $35M fund; up to $100k a project | yes | Flower, Nous Research |
| Cloudflare; Fastly; Vercel | [Vite Ecosystem Fund](https://blog.cloudflare.com/launching-vite-ecosystem-fund); [Fast Forward](https://itsfoss.com/news/fastly-open-source-initiative/); [open-source program](https://vercel.com/open-source-program) | 2022– | $1M; $50M in free services; credits | no | infrastructure for projects |
| Tidelift (now Sonar) | [paying maintainers](https://prnewswire.com/news-releases/tidelift-reaches-milestone-of-one-million-dollars-committed-to-pay-open-source-software-maintainers-300713996.html) | 2018– | $1M+ committed by 2018 | no | maintainers of packages |
| Open Collective | [Open Source Collective](https://opencollective.com/opensource) (fiscal host for 2,735 collectives); [Open Collective Foundation](https://opencollective.com/foundation/updates/announcement-we-are-dissolving-open-collective-foundation-at-the-end-of-this-year) (dissolved 2024) | 2017– | n/a | no | fiscal hosting for projects |
| Gitcoin | [Gitcoin Grants](https://www.gitcoin.co/impact) | 2019– | $60M+ distributed | sometimes | quadratic funding for open source and web3 |
| Optimism Collective | [Retro Funding](https://optimism.io/blog/850m-op-dedicated-to-the-evolution-of-retro-funding) | 2022– | paid in OP tokens | sometimes | retroactive public-goods funding |
| Ethereum Foundation | [Ecosystem Support Program](https://blog.ethereum.org/category/ecosystem-support-program) | 2019– | about $32.6M in Q1 2025 alone | sometimes | client teams, tooling, research |
| Filecoin Foundation for the Decentralized Web; Protocol Labs | [grants](https://www.businesswire.com/news/home/20210928005396/en/Filecoin-Foundation-for-the-Decentralized-Web-Supports-Free-Speech-and-Empowers-Journalists-with-Grant-to-the-Freedom-of-the-Press-Foundation) | 2020– | n/a | sometimes | Internet Archive, Freedom of the Press Foundation |
| VitaDAO; Molecule | [longevity research funding](https://www.lifespan.io/?p=118091); [IP-NFTs](https://molecule.xyz/blog/we-have-raised-12-7-million-in-seed-funding-to-build-the-future-of-decentralized-science-and-biotech) | 2021– | $3M+ funded; $12.7M seed for Molecule | sometimes | DeSci research projects |
| Kickstarter, Crowd Supply, Indiegogo backers | reward crowdfunding | 2009– | e.g. Pine64's PINE A64, [$1.7M](https://silicon.co.uk/workspace/first-15-supercomputer-kickstarter-184595) | yes | Opentrons, OpenBCI, Bela, OpenMV, Luxonis, MNT Reform, LimeSDR |
| StartEngine, Wefunder, Crowdcube investors | equity crowdfunding | | e.g. Purism [$0.2M](https://www.linux-magazine.com/Online/News/Purism-Crowdfunding-Launched) | yes | Purism, Mycroft AI, Framework |

On crowdfunding, the strongest evidence Edison found is about open source itself. Across about 28,000
Kickstarter projects, open-source projects raised about 39% more relative to their goals than comparable projects,
and patent-based ones about 33% less (Bort et al. 2024; [Edison answer](edison/fund_who_funds_open_source_answer.md)).

## How good is the list?

Six checks of different kinds, then an independent review (next section). The names the list has are mostly
supported by their sources, and a fuller search finds more. None of the checks proves that every named funder put
money into the round shown, and the review found definitional errors, now fixed. So the counts are neither complete
nor guaranteed lower bounds.

| Check | What it tests | Result |
| --- | --- | --- |
| Every investor name in a counted round against the page its round cites ([`data/source_checks_deals.csv`](data/source_checks_deals.csv)) | that the name is on the page the row cites (a name match, not proof of an investment) | Of {{source_check.fetched}} names whose page could be fetched: {{source_check.found}} ({{source_check.share_found}}) appear in the page text; {{source_check.markup_only}} more appear only in its markup, which is how company pages show investor logos; {{source_check.not_on_page}} don't appear at all. Those are mostly Chinese names recorded in English, pages that load by script, and some real errors. Two verification passes reopened {{verify.checked}} of them by hand: {{verify.confirmed}} confirmed on the cited page, {{verify.other_source}} on another page, {{verify.not_supported}} not supported (left out of the counts) and {{verify.unclear}} unclear |
| A hand check of 12 links drawn at random | that the name is a funder of that venture, in context | 9 confirmed in the cited sentence; 3 on pages that couldn't be read (a bot wall, a product page, a press release that loads by script). None was wrong |
| A second hand check, after the review: {{spot_check.links}} links drawn at random with a fixed seed, 30 from U1–U3 and 10 from U4 ([sample](data/verify/spot_check_sample.csv), [verdicts](data/verify/spot_check_verdicts.csv)) | the same, reading the passage that names the funder | Of the {{spot_check.readable}} whose page could be read, {{spot_check.confirmed}} confirmed (one only as a logo among the company's backers, one with its round unclear). One was in a round reported as not yet closed; such rounds are now left out of the counts. One name was a logo under "community supporters", with no stated role, and one could not be checked on its cited page, a 36Kr database entry (the row says the name came from a separate 36Kr article). {{spot_check.unreadable}} pages could not be read (HTTP 403 or 429) |
| Investors' own portfolio pages ([`data/portfolio/`](data/portfolio/)) | recall, from the investors' side | Of 105 portfolio pages, 77 could be read. They link to 70 ventures in this list by website. 44 of those links were already in the deal data; 24 of the other 26 were confirmed on the page and added, and 2 were false matches |
| Edison's blind audit of 40 randomly drawn ventures ([`edison/fund_deal_audit_answer.md`](edison/fund_deal_audit_answer.md), [comparison](data/edison_audit_comparison.csv)) | recall and precision, independently, with web search; measured before the audit's rounds were merged in | Edison named {{edison_audit.edison_names}} funders for the 40 ventures and this list {{edison_audit.our_names}}. **{{edison_audit.ours_confirmed_by_edison}} of this list's names are in Edison's**, but this list has only {{edison_audit.recall_vs_edison}} of Edison's. Most of Edison's extra names fall into three groups:<br>• more participants in rounds this list already has;<br>• funders of the {{edison_audit.ventures_we_missed_entirely}} audited ventures where this list found none (e.g. Coqui, Terrastruct, Bitcraze, Antmicro);<br>• angels, government grants, lenders and crowdfunding.<br>Edison also counted one project's corporate sponsors as funders. Edison found nothing for any venture where this list found funders |
| Edison's literature answer ([`edison/fund_who_funds_open_source_answer.md`](edison/fund_who_funds_open_source_answer.md), [check](data/edison_literature_check.csv)) | whether well-known funders are missing | When checked, {{edison_literature.found}} of the {{edison_literature.named}} funders it names were in the deal data or the program tables. The two then missing are now in: Indiegogo backers in the deal data, and the Footprint Coalition in the program table, as a supporter (with Moore and Schmidt Futures) of Experiment's Low-Cost Tools for Science challenge |

After the comparison, the audit's high- and medium-confidence rounds were added to the data as pass `xed`. The 40
audited ventures are now covered better than the rest, and the audit's percentages describe the list before that
merge, not now.

Two sensitivity checks, the first set by the protocol and the second asked for by Edison's review:

- **Source quality.** {{sensitivity_db.links_db_only}} of the {{sensitivity_db.links}} U1–U3 funder–venture links
  rest only on databases or Wikipedia. Dropping them leaves {{sensitivity_db.top20_overlap}} of the top 20 in place.
  Across all four groups it takes the list from {{sensitivity_db_all.funders}} funders to
  {{sensitivity_db_all.funders_strict}}.
- **Openness.** {{sensitivity_open_yes.ventures_partial_with_links}} of the U1–U3 ventures with named funders are
  only partly open (`open_ok` = partial: open core, some open-weight releases, chip firms with open instruction sets
  or software). Keeping only the {{sensitivity_open_yes.ventures_yes_with_links}} that passed outright keeps
  {{sensitivity_open_yes.top20_overlap}} of the top 20. Out go {{sensitivity_open_yes.dropped_from_top20}}; in come
  {{sensitivity_open_yes.entered_top20}}.

## Edison's review and what changed

Edison reviewed a full draft of this file and its data independently
([review](edison/fund_review_files/review.md), [summary](edison/fund_review_answer.md)). It recomputed the tables from
the CSVs (448 table cells agreed) and ranked eleven problems. What was done about each:

| Finding | What changed |
| --- | --- |
| 1. Acquisitions, buyouts, an IPO and secondary share sales were counted as funding (Cloudera's $5.3B buyout, SUSE's sales, Odoo's secondaries) | {{not_counted.exit}} such rows, plus {{not_counted.ownership_transfer}} purchases of control ([`data/round_exclusions.csv`](data/round_exclusions.csv)), stay in `deals.csv` with `counted` = no and the reason. Buyers of secondary shares, such as CapitalG and Sequoia buying Odoo shares in 2024, no longer count as funders of that round |
| 2. Nonprofits and ventures whose main product is not open were in the counts | {{out_of_scope_by_reason.nonprofit}} nonprofits and {{out_of_scope_by_reason.not_open}} closed-product ventures, all in U4, are out of the counts (`in_scope` in `ventures.csv`, reasons in [`data/out_of_scope.csv`](data/out_of_scope.csv)). The nonprofits' funders moved to the program table. Partly open ventures stay in, and the openness sensitivity above shows how much they matter |
| 3. Six companies were entered twice: Embedchain and Mem0, Danswer and Onyx, Pynecone and Reflex, ComfyUI and Comfy Org, APITable and AITable, Zinc and ZincSearch | merged ([`data/venture_aliases.csv`](data/venture_aliases.csv)) |
| 4. The count of "funding events" could not be reproduced | Rows that describe the same round now share a `round_id`; the text gives rounds, not rows |
| 5. "Accurate; every count is a lower bound" overstated the checks | reworded; the source check is described as a name match; the source-quality sensitivity is reported |
| 6. Funders were split across names (SAP Ventures and Sapphire Ventures, Partech and Partech International, LDVP and LDV Partners, spelling variants) and many types were guessed from the name | merged, with one spelling per funder and about 20 more aliases; every funder with two or more ventures, and every funder that had no type, is now typed by hand, and the one-venture funders typed by rule were read over by hand |
| 7. "Crowdfunding is the most common single source" and "first cheques" | reworded: Kickstarter backers are the most frequent single name in U2, venture firms the most common type; the early-round table is not a first-cheque table |
| 8. The audit's percentages read as current, and the missing-funder list was stale | marked as measured before the merge; both missing funders added |
| 9. Missing examples | PeerJ added to U2 (pass `h01`); Tool Foundry, Experiment's Low-Cost Tools for Science with Footprint Coalition, the Royal Society and UKRI behind OpenFlexure, Coefficient Giving, and the NSF–Astera cloud-lab test bed added to the programs (pass `p7`). CZI's EOSS total now comes from CZI's own report |
| 10. Moore's grants to companies were not shown to go to companies, and "26 funders state an open-source thesis" mixed mandates with remarks | Moore's grant pages name Julia Computing and Continuum Analytics as grantees; the three grants are now in the deal data (pass `xh1`). The thesis table now says what kind of statement each quote is |
| 11. Changes to the protocol were not logged | logged below |

One more fix came from checking the data again: a "Lux Capital" that a Hong Kong paper lists among DeepSeek's
shareholders is kept apart from the US firm of that name ([`data/contextual_aliases.csv`](data/contextual_aliases.csv)).

## How the list was made

1. **Scope first.** [`PROTOCOL.md`](PROTOCOL.md) fixed what counts as an open-source-minded venture and as a
   funder, and the counting rules, before any funding data was gathered (`448c8c2`).
2. **Four groups of ventures**, kept apart in every table:
   - **U1**: all 387 companies behind the most-starred open-source projects on GitHub, from part 2. Nobody picked
     them for their funding.
   - **U2**: 98 open hardware, open science, lab and science-software ventures, picked by hand for relevance to DAL
     and the SDL kit. PeerJ, the 98th, was added after Edison's review
     ([`scripts/late_additions.py`](scripts/late_additions.py)).
   - **U3**: 156 well-known commercial open-source and open-weight AI ventures since 1998. This group
     over-represents successes.
   - **U4**: 402 young open-source startups from two third-party lists, Runa Capital's ROSS Index (2020–26) and Y
     Combinator's directory. They were added after the first passes had started, because there was time, and
     researched more lightly.
3. **Leads without a search engine.** Every research session shares one web-search budget, which ran out in part 2
   and again here after about 15 passes. So `scripts/investor_leads.py` first collected funding sentences for every
   venture from:
   - TechCrunch, SiliconANGLE, BetaKit and TechNode (their public WordPress APIs)
   - Hacker News links, which are often the company's own announcement
   - Wikipedia and Wikidata
   - the company's own site
4. **Deal passes.** Research agents (Claude Sonnet, {{deal_passes}} passes of 13–25 ventures) read the leads and the pages they
   point to. For each round they recorded the lead and the other named investors, with a source URL. Where nothing
   was disclosed they recorded "none found". Once the search budget was spent, they searched with
   `scripts/find_pages.py`, the same open APIs.
5. **Deepening passes.** Then {{deepen_passes}} deepening passes went back to {{deepened}} ventures whose history
   came back thin:
   - well-funded ventures with few named funders
   - U1 companies where part 2 had found funding and this list had none
   - startups that Runa lists as funded
   - "none found" results the researchers themselves doubted

   They added rounds from company newsrooms, Wikipedia's cited articles, SEC prospectuses and archived press
   releases. Late passes found little that was new, a sign that these sources were exhausted.
   - A separate check confirmed 24 investor–venture links from investors' own portfolio pages; it rejected 2.
   - At the end, the U1–U3 ventures with no funding found were swept once more without search: their own home and
     about pages and the READMEs of their top GitHub repositories
     ([`data/verify/none_found_sweep.csv`](data/verify/none_found_sweep.csv)), plus part 2's matches to SEC Form D
     filings. That found funding for four of them (pass `xs1`): VoltAgent's angels, EveryApp's Y Combinator backing,
     and Form D equity sales by Agno and DoltHub, whose investors the filings do not name.
6. **Program passes.** Six passes listed the programs that fund open source and open science outside equity
   rounds: foundations (twice, the second through the Moore and Sloan grants databases), governments and public
   investors, corporate funds, crypto, accelerators, fellowships and crowdfunding. They also recorded investors
   that state an open-source thesis, in their own words. A seventh (`p7`) added the programs Edison's review named,
   each from a page fetched and read for this.
7. **Merge.** `scripts/build_funders.py` normalises names with a hand-made alias table
   ([`data/investor_aliases.csv`](data/investor_aliases.csv)) and types each funder from a hand-made table
   ([`data/investor_types.csv`](data/investor_types.csv), by the firm's own description; people count as angels).
   - A round that a source reports only as talks, a rumour or a raise in progress is kept, but its names are not
     counted (`counted` column in `deals.csv`). So are acquisitions, buyouts, IPOs, secondary share sales and
     purchases of control, which put no money into the venture.
   - Rows that describe the same round share a `round_id`: same venture and round type, and either amounts within
     5% with dates at most six months apart, or the same month where one amount is missing. Rounds are counted by
     `round_id`.
   - Ventures entered twice are merged, and nonprofits and ventures whose main product is not open are marked
     out of scope (`in_scope` in `ventures.csv`).
   - Claude Opus planned the passes, wrote the scripts, reviewed the rows and wrote this file.

### Changes to the protocol

[`PROTOCOL.md`](PROTOCOL.md) was committed before any data. These changes came later:

- **U1 has 387 companies, not 392.** The protocol counted GitHub organisations. Five of the 392 belong to companies
  already counted, so there are 387 companies: Docker (`docker`, `moby`), VoidZero (`vitejs`, `oxc-project`) and
  FIT2CLOUD (`1Panel-dev`, `halo-dev`, `jumpserver`, `dataease`). The `owners` column of `data/ventures_input.csv`
  lists each company's organisations.
- **U4 was added after the first passes had started**, because there was time. It is researched more lightly and
  reported separately.
- **The web-search budget ran out early**, so most passes used open news APIs, Wikipedia and company pages instead
  (step 3 above).
- **Edison's blind-audit rounds were merged in** (pass `xed`) after the audit had been scored.
- **After Edison's review:** exits and secondary sales were taken out of the counts, duplicate ventures merged,
  nonprofits and closed products marked out of scope, PeerJ added to U2, and Moore's grants to Julia Computing and
  Continuum Analytics added from Moore's grant pages.

## Limits

- **Disclosure is selective.** Big rounds, well-known investors and companies that survived are reported more.
  Seed angels, small funds, failures and private companies outside the US and Europe are reported less. Counts
  therefore favour large, visible firms.
- **Coverage is uneven.** The search budget ran out early, so many ventures were researched only from news APIs,
  Wikipedia and company pages.
  - Web search was available only for the program passes, all five U2 passes, three U3 passes and about four
    U1 passes; the rest relied on the open APIs and direct fetches.
  - Chinese-language sources were read for a handful of companies only.
  - U4 (young startups) was researched lightly by design: for most of it, YC's own page and a quick look at the
    company site.
- **"None found" means none found.** Of the companies behind the most-starred projects, {{U1.none_found}} have no
  disclosed outside funding in this data, and {{U2.none_found}} in U2 and {{U3.none_found}} in U3 have none either.
  Some will have raised money that was never announced or that these sources don't reach. Edison's audit found
  funders for several such ventures, so a re-check with web search, which this session could no longer do, would
  likely add some.
- **U2, U3 and U4 are not random.** U2 was picked for relevance and U3 for fame. U4 comes from lists kept by an
  accelerator (YC) and an investor (Runa), which both have an interest in the companies on them.
- **A count is not a return.** Nothing here measures whether these funders made money on open source. Edison found
  no study that does. Being on the list doesn't mean a funder would back a new open venture.
- **Names are normalised by hand.** Fund vehicles roll up to the firm, and corporate arms stay separate but roll up
  to their parent in one table. Some aliases will be missed, and a few distinct firms share a name; one known case,
  DeepSeek's "Lux Capital", is kept apart. Funders with one venture were typed by rules on their names (people as
  angels), then read over once by hand, which moved about 100 corporate arms, crypto funds, state funds and growth
  investors out of "venture firm".
- **Some ventures in the counts are only partly open**: open-core companies, AI labs that release some weights, and
  chip firms with open instruction sets or software around closed chips. VitaDAO and LabDAO (DAOs that sold tokens
  to investors) and Proton AG (whose main shareholder is the nonprofit Proton Foundation) are also kept. The
  openness sensitivity above shows how much the partly open ones matter.
- **Rounds are as sources describe them.** Labels (seed, Series A) and amounts follow the source, and sources
  sometimes disagree; the rows say so in `note`.

## Files

| Path | What it is |
| --- | --- |
| [`FUNDER_LIST.md`](FUNDER_LIST.md) | Every funder found, by type, with each venture linked to a page naming it |
| [`PROTOCOL.md`](PROTOCOL.md) | Scope and counting rules, committed before any data |
| [`deal_rules.md`](deal_rules.md), [`deepen_rules.md`](deepen_rules.md), [`program_rules.md`](program_rules.md) | The instructions each research pass followed |
| `data/ventures_input.csv` | The 1,043 ventures, their group (U1–U4) and the list each came from |
| `data/ventures.csv` | One row per venture: what is open, status, whether funding was found, whether it is in scope, part 2's funding total for U1 |
| `data/deals.csv` | One row per round as a source reports it: type, date, amount, lead and other investors (as written and normalised), source URL and kind, whether it is counted and why not, and `round_id` |
| `data/venture_aliases.csv`, `data/out_of_scope.csv`, `data/round_exclusions.csv`, `data/contextual_aliases.csv` | Hand-made corrections after Edison's review: ventures entered twice, ventures out of scope, purchases of control, and one name that means a different firm in one venture |
| `data/thesis_kinds.csv` | What kind of statement each open-source quote is |
| `data/u2_kinds.csv` | The kind of each U2 venture (devices, 3D printing, chips, robotics, lab automation and instruments, science software, AI for science, publishing, DeSci), set by hand |
| `data/verify/` | Hand checks: verdicts on doubtful names, and the random sample of 40 links read in context |
| `data/science_topic_keys.csv` | The ventures in the open hardware, science and lab tables: U2 plus the U1 companies found through GitHub's science topics |
| `data/investor_links.csv` | One row per funder–venture pair, with rounds, leads, first year and sources |
| `data/investors.csv` | One row per funder: type, ventures by group, leads, years, examples, stated open-source thesis |
| `data/programs.csv` | Program-level funders: foundations, governments, corporate funds, crypto, accelerators, crowdfunding |
| `data/investor_aliases.csv`, `data/investor_types.csv` | Hand-made name normalisation and funder types |
| `data/yc_open_source.csv`, `data/u4/ross_index.csv` | YC companies tagged or described as open source; every ROSS Index entry read |
| `data/portfolio/` | Investors' own portfolio pages, and the ventures matched on them |
| `data/source_checks_deals.csv`, `data/source_checks_programs.csv` | Whether each name or amount appears on the page it cites |
| `data/leads/` | The leads each pass started from |
| `data/deal_passes/`, `data/program_passes/` | Raw pass outputs, as written |
| `data/tables/` | The tables in this file, and the full open hardware, science and lab venture table |
| `edison/` | Edison's literature answer, blind audit and review of this file, with full trajectories |
| `scripts/` | Everything that produced the above; run order in [`README.md`](README.md) |
| `figures/` | The two charts |
