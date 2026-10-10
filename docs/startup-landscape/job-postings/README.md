# Job postings: the actual roles and descriptions

Historical job postings survive, mostly with their full descriptions. This folder holds **811 postings from 23 companies, 757 of them with the full description**. They run from March 2014 to 10 October 2026; 318 had closed by then, 264 of those with their description intact.

The first version of this folder covered 15 companies and found only careers-page captures, or nothing, for the other ten. A second pass found postings for eight of those ten: it followed each careers page to the board behind it, and it checked the job boards that universities and investors run. [The ten companies the first pass missed](#the-ten-companies-the-first-pass-missed) covers how, and what those postings show. Only Mattiq and Intrepid Labs still have none.

Each company has a page listing its postings by first-seen date. Underneath are the role-specific parts of each description: responsibilities, requirements and pay. The cross-company tables are in [summary.md](summary.md), the role-by-role reading is in [roles.md](roles.md), and the full text is in [`../data/job_postings.jsonl`](../data/job_postings.jsonl).

![Job postings by first-seen date and function](../figures/postings_timeline_by_function.png)

The previous pass said Periodic's launch-day postings were unrecoverable "JavaScript shells". That was a decoding mistake. The Wayback Machine returns those pages gzip-encoded as originally sent, and each one embeds the posting as JSON: title, team, location, pay and description. Greenhouse, Rippling and Personio pages carry the same data in their own formats.

## What the postings show

### 1. A company's first postings are its build plan, and they go up before the announcement

**[Periodic Labs](periodic-labs.md)** published its first 14 roles between 18 and 24 September 2025. That was a week or more before its $300M seed was announced on 30 September. Eight of the 14 were lab hardware and facilities:
- [Automation Engineer](periodic-labs.md#automation-engineer-2025-09-22)
- [Controls Engineer](periodic-labs.md#controls-engineer-2025-09-22)
- [Mechanical Engineer](periodic-labs.md#mechanical-engineer-2025-09-22)
- [Reliability Engineer](periodic-labs.md#reliability-engineer-2025-09-22)
- [Robotics Engineer](periodic-labs.md#robotics-engineer-2025-09-22)
- [Systems Engineer](periodic-labs.md#systems-engineer-2025-09-22)
- [Facilities Manager](periodic-labs.md#facilities-manager-2025-09-22)
- [Research Engineer, Lab Automation](periodic-labs.md#research-engineer-lab-automation-2025-09-22)

Of the other six, one was a [materials-characterization scientist](periodic-labs.md#research-scientist-materials-characterization-2025-09-22). The other five built the model side: CUDA kernels, distributed training, inference, supercompute and mid-training. By the board's next capture in February 2026, the robotics, reliability, facilities and CUDA roles were gone. Thin films, powder processing, process safety, EHS and technician roles followed through 2026.

**[Lila Sciences](lila-sciences.md)**' Greenhouse board was first archived on 6 October 2025, three weeks after its $235M Series A. It listed 29 roles in its first two weeks, including:
- ML scientists and engineers for interatomic potentials, scientific reasoning, distributed training and the AI platform;
- research scientists for porous materials, statistical mechanics, functional materials and in-silico discovery;
- electron-microscopy and electroanalytical internships;
- a mechatronics engineer and a robotics systems architect;
- two staff forward-deployed engineers, one for life sciences and one for physical sciences.

**[Medra](medra.md)**'s first roles (September–October 2025, around its $11M seed) were these:
- robotics software, full-stack and mechanical engineers;
- a [forward-deployed robotics engineer](medra.md#forward-deployed-robotics-engineer-2025-10-23);
- intern versions of each for winter and summer 2026.

Scientists came later: protein engineering in December 2025, then biology research associates through 2026.

**[Atinary](atinary.md)** posted a [Synthetic Chemist, Self-Driving Lab (Boston, MA)](atinary.md#synthetic-chemist-self-driving-lab-boston-ma-2025-09-24) and a Lead AI Scientist in September 2025. That was half a year before its Boston self-driving lab opened. A "Head of lab" was posted in November 2024.

### 2. Pivots and strategy shifts show up in the postings first

**[Orbital Materials](orbital-materials.md)**' postings turned to hardware well before it renamed itself Orbital Industries in 2026:
- **October 2024:** generative-model and LLM researchers and a full-stack engineer.
- **December 2024:** a [Mechanical Engineer, Data Center Cooling Design](orbital-materials.md#mechanical-engineer-data-center-cooling-design-2024-12-02), a [Process Engineering, Data Center Cooling](orbital-materials.md#process-engineering-data-center-cooling-2024-12-18) role and two [Pilot Plant Design Engineers: Carbon Removal](orbital-materials.md#pilot-plant-design-engineer-carbon-removal-2024-12-02).
- **2025:** electrical, quality and senior mechanical engineers in Canada, a CFO and sales directors.
- **2026:** prototype researchers, test engineers and forward-deployed engineers.

**[CuspAI](cuspai.md)** hired ML researchers and application scientists through its Series A. After its $450M Series B in July 2026, 8 of its 10 new postings were in partnerships, an "AI Materials Foundry" ecosystem manager, developer relations, technical programme management, talent and data leadership.

**[Chemify](chemify.md)** posted 21 roles in 2026Q3. Nine were hardware and lab roles for its Glasgow Chemifarm: an automation scientist; mechanical, mechatronics, firmware and manufacturing engineers; an engineering project manager; a laboratory coordinator; and a health and safety advisor.

### 3. What the jobs are

290 of the first pass's postings with descriptions were sorted by hand into seven archetypes (nine rows, since the scientists split three ways). The reading behind each row is in [roles.md](roles.md): what the job involves, which instruments and tools, required and preferred degrees, pay, and verbatim quotes. The coding is in [`../data/job_postings_roles.csv`](../data/job_postings_roles.csv).

| Archetype | Postings (n) | Companies | Degree asked for most often | Median min. years | US posted pay (n) | Example |
|---|---|---|---|---|---|---|
| 1. Lab automation, robotics | 43 | 5 | bachelor's (20 of 40) | 3 (n=20) | $75.6K–$304K (23) | [Robotics Engineer](periodic-labs.md#robotics-engineer-2025-09-22) |
| 2. Associates, technicians, operators | 36 | 6 | bachelor's (12 of 33) | 1.5 (n=12) | $72K–$225K (13) | [Laboratory Technician](periodic-labs.md#laboratory-technician-2026-07-16) |
| 3. Materials and chemistry scientists | 27 | 6 | PhD (18 of 25) | 5 (n=18) | $108K–$350K (21) | [Research Scientist, Thin Films](periodic-labs.md#research-scientist-thin-films-2025-10-31) |
| 3b. Biology scientists | 8 | 2 | PhD (5 of 8) | 4 (n=6) | $88K–$256K (6) | [Lead Scientist, Protein Engineering](medra.md#lead-scientist-protein-engineering-2025-12-11) |
| 3c. Computational scientists | 17 | 7 | PhD (14 of 16) | 4 (n=4) | $140.8K–$350K (7) | [Research Scientist, Condensed Matter Theory](periodic-labs.md#research-scientist-condensed-matter-theory-2025-11-12) |
| 4. ML researchers, engineers | 79 | 11 | PhD (21 of 63) | 4.5 (n=20) | $144K–$570K (33) | [Research Scientist, Scaling RL](periodic-labs.md#research-scientist-scaling-rl-2026-10-01) |
| 5. Lab-software engineers | 38 | 7 | bachelor's / none stated (16 each of 35) | 5 (n=27) | $108K–$390K (20) | [Software Engineer I, Instrument Software](lila-sciences-lab-automation.md#software-engineer-i-instrument-software-2026-03-20) |
| 6. Forward-deployed, application | 20 | 10 | none stated (7 of 17) | 3 (n=3) | $140K–$400K (5) | [Forward Deployed Engineer](orbital-materials.md#forward-deployed-engineer-2026-08-25) |
| 7. Lab operations, facilities, EHS | 22 | 7 | none stated (9 of 19) | 5 (n=11) | $68K–$325K (11) | [Lab Operations Specialist](lila-sciences-lab-automation.md#lab-operations-specialist-2026-09-28) |

Some points from that reading:
- **Lab automation rarely asks for a PhD; the scientists who specify it do.** 6 of 40 lab-automation postings name a PhD, against 23 of 25 experimental materials and chemistry scientists and 15 of 16 computational scientists. The PhD lab-automation roles are mostly "translators" who turn experiments into automation specifications, plus two Lila robotics research scientists.
- **Technicians run shifts.** 11 technician postings require nights, weekends, off-hours or on-call work, and many are contracts: 4 of Periodic's 5 technician postings and 6 Lila lab roles.
- **Software engineers need lab experience only as a bonus.** Just 1 of 35 software postings requires hands-on hardware experience: Chemify's robotics architect, which asks for 8+ years of safety-critical C/C++. 26 list it as a bonus. 13 require hands-on use of AI coding assistants.
- **Pay depends more on the company than on the role.** Lila posts Scientist I/II at $108–170K against $160–350K for Periodic's research scientists, and Engineer I at $75.6–100.8K against $100–130K for Periodic's Laboratory Technician.

### 4. What the descriptions ask for

These figures cover the 502 English-language postings with a description. DP Technology's postings are in Chinese and are left out, because the skill keywords are English. The full table is in [summary.md](summary.md#what-the-descriptions-ask-for-by-function).

**Who needs a PhD.** It is the norm for materials scientists but not for the people who build the lab:

| Function | Name a PhD | Name a bachelor's | Median "N+ years" |
|---|---|---|---|
| Materials science | 70% | 30% | 3 |
| ML research | 46% | 22% | 4 |
| Lab automation | 19% | 41% | 3 |
| Software | 10% | 33% | 5 |

"Name" means the degree appears anywhere in the text, required or preferred.

**What lab-automation postings ask for.** Robots come up in 57%, safety (EHS) in 46%, CAD and mechanical design in 27%, and PLC and controls in 23%.

**Software engineers are asked about the lab.** 41% of software postings mention robots, usually as a bonus. Lila's software postings, for example, add "experience with laboratory devices, robotics, or hardware drivers".

**Posted pay.** For US postings that publish a range, the median range midpoint by function:

| Function | Median midpoint |
|---|---|
| ML research | $291K |
| Software | $224K |
| Lab automation | $163K |
| Materials science | $162K |
| Business and operations | $156K |

Lab automation was $177K in the first version. The second pass added lower-paid lab roles: Radical AI's [Automation Technician](radical-ai.md#automation-technician-2026-08-21) ($66–103K) and [Laboratory Operations Specialist](radical-ai.md#laboratory-operations-specialist-2026-06-04) ($87–120K), and Emerald Cloud Lab's [Laboratory Operations Shift Manager](emerald-cloud-lab.md#laboratory-operations-shift-manager-2024-01-04) ($70–90K). Materials science comes out low because most of those ranges are Lila's, for its Scientist I/II and research-associate levels. Periodic posts $250–350K for research scientists, $200–250K for its [Automation Engineer](periodic-labs.md#automation-engineer-2025-09-22) and $100–130K for its [Laboratory Technician](periodic-labs.md#laboratory-technician-2026-07-16). Lila posts $75.6–100.8K for an [Engineer I, Research Operations](lila-sciences-lab-automation.md#engineer-i-research-operations-2nd-shift-2026-09-08) on its second shift.

### 5. How long a posting stays up depends on the company more than the role

For closed postings, the time between first and last sighting varies mostly by company:

| Company | Lab automation (median days) | ML (median days) |
|---|---|---|
| Lila | 26 | 33 |
| Periodic | 134 | 133 |
| Orbital (hardware postings) | 251 | |

These spans follow the archive's crawl dates, so they are rough. [roles.md](roles.md#what-the-closed-postings-add) has more on what the closed postings show.

## The ten companies the first pass missed

The first pass searched the archive for each company's careers-page URL, and it probed the usual ATS vendors by company name. It missed three things:
- the links and embeds on those careers pages, which lead to the boards behind them;
- ATS vendors outside its short list;
- the job boards that universities and investors run for their companies.

Fixing those found postings for eight of the ten:

| Company | Postings (with description) | First seen to last | Where they were |
|---|---|---|---|
| [Emerald Cloud Lab](emerald-cloud-lab.md) | 43 (28) | 2014–2026 | Lever, first under its old name `emeraldtherapeutics` and then as `emeraldcloudlab`; BambooHR since 2024. Role names on its 2015–16 careers page |
| [DP Technology](dp-technology.md) | 248 (248), all open | 2022–2026 | the JSON API behind its Feishu board, which issues a token to every visitor |
| [Radical AI](radical-ai.md) | 31 (31) | 2024–2026 | Lever (`RadicalAI`: the token is case-sensitive), then Nodi; closed Lever postings on AlleyCorp's portfolio board |
| [Deep Principle](deep-principle.md) | 7 (7) | 2025–2026 | inline on its own join pages, in Chinese and English |
| [Polymerize](polymerize.md) | 7 (0) | 2023–2025 | titles of its careers pages, which load their text client-side |
| [Altrove](altrove.md) | 6 (6) | 2025–2026 | Entrepreneurs First's and Contrarian Ventures' portfolio boards |
| [Kebotix](kebotix.md) | 2 (2) | 2018–2019 | its Google Hire board |
| [Telescope Innovations](telescope-innovations.md) | 2 (2) | 2024 | the MaRS tech-jobs board |
| Mattiq | none | | its careers button links only to LinkedIn |
| Intrepid Labs | none | | no careers page or ATS; its university and investor board pages listed no jobs |

What they add:

**Emerald Cloud Lab's postings are a cloud lab's staffing record.**
- **Lab operators:** a [Laboratory Operator](emerald-cloud-lab.md#laboratory-operator-2014-03-26) posting was open almost continuously, on Lever from 2014 to 2021. It was posted again in Austin in 2023 and has been on BambooHR [since 2024](emerald-cloud-lab.md#laboratory-operator-i-ii-iii-2024-05-06), at $20–26 an hour.
- **Locations:** the postings move from South San Francisco (to 2021) to Austin (from 2023). In 2024 they add Pittsburgh, for the Carnegie Mellon cloud lab: a [shift manager](emerald-cloud-lab.md#laboratory-operations-shift-manager-2024-01-04) ($70–90K), a [laboratory development engineer](emerald-cloud-lab.md#laboratory-development-engineer-i-2024-03-06), a [scientific operations](emerald-cloud-lab.md#scientific-operations-2024-01-09) role ($105–115K) and lab operators.
- **Pay:** these are the lowest salaries posted anywhere in the survey.

**DP Technology is building wet labs.**
- **The board as a whole:** most of its 248 open postings are software, product, sales and operations for its AI-for-science platforms, and 95 are internships.
- **2026 adds lab roles.** From January there are battery and electrolyte roles in Yibin, a battery-industry city.
- **5 August 2026:** a batch of lab roles went up in Beijing:
  - [ADME](dp-technology-materials-science.md#adme-engineer-2026-08-05), [analytical and separation](dp-technology-materials-science.md#analytical-and-separation-scientist-2026-08-05) and [chemical-analysis](dp-technology-materials-science.md#chemical-analysis-engineer-2026-08-05) scientists;
  - an [automation-equipment engineer](dp-technology-lab-automation.md#automation-equipment-development-engineer-2026-08-05) and a [lab-automation application developer](dp-technology-lab-automation.md#lab-automation-application-developer-2026-08-05);
  - a [facilities engineer](dp-technology-lab-automation.md#facilities-engineer-2026-08-05).
- **By early September** came an [instrument-automation engineer](dp-technology-lab-automation.md#instrument-automation-engineer-2026-09-01) and an [EHS manager](dp-technology-lab-automation.md#ehs-manager-2026-09-03).
- **The pattern:** that is the build-out Periodic posted at its launch (automation, facilities, safety). DP posted it eight months after its ~$114M Series C.

**Radical AI hired scientists and lab engineers first.**
- **August 2024:** its first postings were AI research scientists for [GNN and foundation models](radical-ai.md#ai-research-scientist-gnn-foundation-models-2024-08-22) and [generative models](radical-ai.md#ai-research-scientist-generative-models-2024-08-22), a [materials scientist](radical-ai.md#material-scientist-2024-08-22), and [mechanical](radical-ai.md#mechanical-engineer-2024-08-22) and [mechatronics](radical-ai.md#mechatronics-engineer-2024-08-22) engineers.
- **Spring 2026:** computational chemists and materials scientists for metal alloys, robotics, and a [lab operations specialist](radical-ai.md#laboratory-operations-specialist-2026-06-04).
- **Since August 2026, on Nodi:** an [automation technician](radical-ai.md#automation-technician-2026-08-21) ($66–103K), a [design mechanical engineer](radical-ai.md#mechanical-engineering-design-2026-08-21) ($140–185K), an [ML research engineer](radical-ai.md#ml-research-engineer-2026-09-17) ($235–295K) and software engineers ($165–295K).
- **Context:** in January 2026 it committed to New York State to add 115 jobs.

**Smaller companies hire one of each.**
- **Altrove,** right after its $10M seed (October 2025): a [laboratory technician](altrove.md#laboratory-technician-advanced-materials-2025-10-03), an [inorganic-materials engineer for manufacturing and process design](altrove.md#inorganic-materials-engineer-manufacturing-and-process-design-2025-10-18) and a business-development associate. An ML engineer and a CTO associate followed in 2026.
- **Telescope,** in August 2024: a [mechatronics engineer](telescope-innovations.md#mechatronics-engineer-automated-chemistry-technology-2024-08-16) (CAD 85–125K) and a [software engineer](telescope-innovations.md#software-engineer-automated-chemistry-technology-2024-08-20) (CAD 85–120K) for its automated chemistry technology.
- **Deep Principle,** in 2025: a [Head of AI](deep-principle.md#head-of-artificial-intellgence-2025-06-17) and a [Head of Laboratory for high-throughput experimentation](deep-principle.md#head-of-laboratory-hte-2025-06-17). Both were gone from its page by December.

## Coverage and gaps

Twenty-three companies have postings here. Two have none:
- **Mattiq.** Its careers page has one button, which links to its LinkedIn jobs tab. This survey does not read LinkedIn. Under its earlier name, Stoicheia, it had a one-page site, and no ATS board was ever archived under either name.
- **Intrepid Labs.** It has no careers page and no ATS. Its pages on the University of Toronto and Radical Ventures job boards were archived in January and June 2026 with no jobs listed, and showed none on 9 October. A search snippet shows a "Director of Operations" posting on an aggregator, which was not read.

**Thin coverage:**
- **Citrine:** only from 2025 on. Its 2019–22 openings sat in a Greenhouse embed that was never captured.
- **Kebotix:** two 2019 postings. Its 2020 Indeed widget and its 2021 Greenhouse board were never archived, under any form of their URLs.
- **Emerald Cloud Lab:** nothing from 2017–19. Its 2015–16 roles have titles but no text, because their Lever pages were not archived.
- **DP Technology:** only postings still open, dated by when they were published. Closed postings leave its board, and its posting pages were never archived.
- **Polymerize:** seven titles with dates and no text. Its careers pages load their text client-side, and the archive never captured that data.
- **Mitra Chem:** one 2021 posting plus today's.
- **Materials Nexus:** two postings from 2022.
- **Matlantis:** two postings from 2023–24.
- **Telescope:** two 2024 postings.
- **Entalpic:** its 2025 Notion role pages survive only as titles in their URLs.
- **Tetsuwan:** two current postings.

## For the VCL

These are the parts that bear on #155, the question of whom an academic self-driving lab should hire and when.

**The first hire is a scientist-engineer, not an ML researcher.** Periodic posted its [Research Engineer, Lab Automation](periodic-labs.md#research-engineer-lab-automation-2025-09-22) at launch, and again in August 2026 at $200–250K. The role:
- asks for a PhD in materials science "or equivalent experience";
- turns scientific goals into an automation roadmap and user requirements;
- runs proof-of-concept experiments;
- works with the mechanical, robotics and controls engineers and the vendors who build the system.

Its partner is the bachelor's-level [Automation Engineer](periodic-labs.md#automation-engineer-2025-09-22), also $200–250K. That role develops "instrument drivers that automate lab workflows" and connects instruments and robots to lab information systems such as a LIMS.

**Technicians come next, and they are where the companies differ most.**

| Role | Posted pay | Notes |
|---|---|---|
| Lila, [Engineer I, Research Operations](lila-sciences-lab-automation.md#engineer-i-research-operations-2nd-shift-2026-09-08) | $75.6–100.8K | shift work |
| Periodic, [Laboratory Technician](periodic-labs.md#laboratory-technician-2026-07-16) | $100–130K | |
| Medra, [Research Associate, Foundry](medra.md#research-associate-foundry-2026-04-09) | not posted | "Our robots don't sleep, so this role includes regular night and/or weekend shifts." |

A university lab that runs unattended overnight will face the same staffing question.

**A cloud lab runs on hourly operators.** Emerald Cloud Lab is the closest commercial analogue to a university cloud lab. It has had a Laboratory Operator posting open for most of a decade, now at $20–26 an hour in Austin. When it set up Carnegie Mellon's cloud lab in 2024, it hired in Pittsburgh:
- lab operators;
- a [shift manager](emerald-cloud-lab.md#laboratory-operations-shift-manager-2024-01-04) ($70–90K);
- a [laboratory development engineer](emerald-cloud-lab.md#laboratory-development-engineer-i-2024-03-06);
- a [scientific operations](emerald-cloud-lab.md#scientific-operations-2024-01-09) role ($105–115K);
- a junior IT administrator ($60–70K).

That is the nearest thing in this survey to a staffing plan for an academic cloud lab.

**For software, hire software engineers and teach them the lab.** 41% of software postings mention robots, but nearly always as a bonus rather than a requirement.

**The descriptions work as templates.** When the VCL writes its own postings, the role-specific sections linked from each company page give concrete responsibilities and requirements at each level. They also show how the same title is scoped at a $300M startup and at a $10M one.

## Method

**Current postings** come from each company's public job-board API, the same JSON its careers page renders from:

| Company | Board |
|---|---|
| Periodic Labs, CuspAI, Medra, Orbital, Tetsuwan | Ashby posting API |
| Lila Sciences | Greenhouse board API |
| Citrine Informatics | Rippling board pages |
| Dunia Innovations | Personio XML feed and job pages |
| Chemify | PeopleHR openings, with titles and post dates from chemify.io/careers |
| Aionics | the WordPress REST API of its own site, which still serves postings from 2021–24 |
| Mitra Chem | TriNet Hire pages linked from its careers page |
| Entalpic | Notion's public page API |
| Emerald Cloud Lab | BambooHR's careers API (`/careers/list` and `/careers/<id>/detail`) |
| Radical AI | Lever's postings API (token `RadicalAI`) and Nodi's public job-offer endpoint |
| DP Technology | the API behind its Feishu (Lark) Hire board, `POST /api/v1/search/job/posts`, with the token the board issues to every visitor |
| Telescope, Altrove, Radical AI (closed postings) | posting pages on Getro boards run by MaRS, Entrepreneurs First and AlleyCorp, which keep a posting's page after it closes |

The previous pass said Entalpic's Notion page could not be read without a browser. That was wrong: Notion's page API returns the hiring database as JSON.

**Past postings** come from Wayback Machine captures of the same boards, plus the older boards the companies have since left. Two kinds of capture are read:
- **Every archived posting URL** under each board. Its first and last capture give the dates.
- **The board page itself, once a quarter.** It lists postings that were never captured on their own.

Most applicant-tracking systems embed the posting in the page as JSON:
- Ashby: `window.__appData`
- Greenhouse: its Remix context
- Rippling and Getro: `__NEXT_DATA__`
- schema.org `JobPosting` on others (Lever, Google Hire)

Others need their own readers:
- **Lever board pages** list every opening with its team and location.
- **BambooHR** keeps the title in `og:title`, and its archived `/careers/list` JSON lists the openings.
- **Deep Principle** writes each posting into its join page's HTML.

So one archived page yields the title, team, location, pay and full description, even where the page looks like an empty JavaScript app in a browser. The archive serves these pages gzip-encoded as originally sent, and [`fetch.get`](../../../scripts/startup_landscape/fetch.py) decodes them. The earlier note that Periodic's launch-day postings "could not be recovered" came from reading the undecoded bytes.

**Fetching through the Pi.** From the GitHub runner, the Wayback Machine refused connections twice:
- first after four parallel index queries;
- then after about six requests in a minute, well under its usual limit of about 15.

GitHub-hosted runners share outbound IP addresses, so other jobs' traffic counts against the same limit. The archive crawl was therefore run from the CubXL Raspberry Pi over Tailscale SSH:
- from a scratch directory, `~/jd-fetch`;
- as one client, 6 s between requests, reads capped at 150 KB/s, at `nice 10`.

The Pi was idle (load 0.00), and its camera script kept running throughout. The scratch directory was deleted afterwards and nothing else on the Pi was changed.

The second pass (10 October 2026) was refused by the archive after about 16 requests from the runner. It then sent its archive requests through the same Pi, using an `ssh -D` tunnel over Tailscale, with `$SL_SOCKS` pointing [`fetch.get`](../../../scripts/startup_landscape/fetch.py) at it.
- The requests left from the Pi's address, but nothing ran or was stored on the Pi.
- It was one client, 6 s between requests, reads capped at 150 KB/s: about 170 requests over 40 minutes.

Both passes read the live job-board APIs from the runner.

**What was not read.** Nothing logged in anywhere. No LinkedIn, Indeed, Glassdoor or Wellfound page was read, live or archived.

**Getro boards.** Investors and universities run these boards to advertise their portfolio companies' jobs.
- **Telescope** entered its own postings.
- **Altrove's** reached the boards from its LinkedIn jobs tab, so their text is Getro's copy of Altrove's LinkedIn ad.
- **Radical AI:** 13 of its 17 pages on AlleyCorp's board are also in the archive. The other 4 were found by checking the IDs next to the one the board still lists, because Getro numbers postings consecutively.

**Building the tables.** [`scripts/startup_landscape/jobs_report.py`](../../../scripts/startup_landscape/jobs_report.py) does the following:
- **Merges** the two sources by posting ID.
- **Dedupes by title.** Two postings with the same title whose date spans overlap or come within 45 days are one posting. A board listing and its own page can carry different IDs, and Ashby re-issues IDs when a posting is edited. A title that comes back after a longer gap is kept as a re-posting.
- **Classifies** each posting into the survey's six functions by its title. It uses the rules in `analyze.py`, plus a few for automated-systems, firmware, recruiting and founding roles. A generic "engineer" on a lab or hardware team counts as lab automation.
- **Reads requirements from the role-specific text only.** It drops lines that recur in at least 40% of one company's postings (the company pitch, perks, legal text) and sections headed "About us", "Benefits", "Equal opportunity" and the like. This keeps a pitch such as "we combine AI and robotics" from making every role look like a robotics role.
- **Records three requirement fields** from what is left: the degrees named, the smallest "N+ years" figure, and a fixed list of skills.

**Dates.** `first_seen` is the earliest of the board's publish date and the first Wayback capture. `last_seen` is the latest capture, or "open" if the posting was live on 10 October 2026. On a Getro board, `first_seen` is when the board first listed the posting, which can be later than the company posted it, and `last_seen` is when the board deactivated it. These are bounds from the inside: a posting was open at least that long.

**Privacy and text.** Descriptions are the companies' own published wording. They are kept for research, and each one links to its source capture or live page. Email addresses and phone numbers are removed. A scan for people named in the descriptions found only executives, in line with the survey's leadership-only rule.

## Caveats

- **Wayback coverage is uneven.** A role that was never crawled is missing, and a closed role whose page was never captured on its own has a title and dates but no description.
- **Date spans are lower bounds.** Postings live on 10 October 2026 carry the board's publish date, which some boards reset when a posting is edited.
- **The function labels come from titles.** "Research Scientist, Data" and "Forward Deployed Engineer, Physics & Simulation" could each sit in two places.
- **The requirement fields are keyword reads.** "Degree named" counts any mention, so "PhD or equivalent experience" and "PhD preferred" both count as naming a PhD.
