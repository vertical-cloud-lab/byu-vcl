# Job postings: the actual roles and descriptions

Historical job postings survive, mostly with their full descriptions. This folder holds **465 postings from 15 companies, 433 of them with the full description**. They run from July 2021 to 10 October 2026; 237 had closed by then, 205 of those with their description intact.

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

290 of the postings with descriptions were sorted by hand into seven archetypes (nine rows, since the scientists split three ways). The reading behind each row is in [roles.md](roles.md): what the job involves, which instruments and tools, required and preferred degrees, pay, and verbatim quotes. The coding is in [`../data/job_postings_roles.csv`](../data/job_postings_roles.csv).

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

These figures cover the 433 postings with a description. The full table is in [summary.md](summary.md#what-the-descriptions-ask-for-by-function).

**Who needs a PhD.** It is the norm for materials scientists but not for the people who build the lab:

| Function | Name a PhD | Name a bachelor's | Median "N+ years" |
|---|---|---|---|
| Materials science | 72% | 32% | 3 |
| ML research | 43% | 18% | 5 |
| Lab automation | 21% | 38% | 4 |
| Software | 11% | 35% | 5 |

"Name" means the degree appears anywhere in the text, required or preferred.

**What lab-automation postings ask for.** Robots come up in 57%, safety (EHS) in 45%, CAD and mechanical design in 26%, and PLC and controls in 21%.

**Software engineers are asked about the lab.** 43% of software postings mention robots or lab hardware, usually as a bonus. Lila's software postings, for example, add "experience with laboratory devices, robotics, or hardware drivers".

**Posted pay.** For US postings that publish a range, the median range midpoint by function:

| Function | Median midpoint |
|---|---|
| ML research | $294K |
| Software | $218K |
| Lab automation | $177K |
| Materials science | $162K |
| Business and operations | $156K |

Materials science comes out low because most of those ranges are Lila's, for its Scientist I/II and research-associate levels. Periodic posts $250–350K for research scientists, $200–250K for its [Automation Engineer](periodic-labs.md#automation-engineer-2025-09-22) and $100–130K for its [Laboratory Technician](periodic-labs.md#laboratory-technician-2026-07-16). Lila posts $75.6–100.8K for an [Engineer I, Research Operations](lila-sciences-lab-automation.md#engineer-i-research-operations-2nd-shift-2026-09-08) on its second shift.

### 5. How long a posting stays up depends on the company more than the role

For closed postings, the time between first and last sighting varies mostly by company:

| Company | Lab automation (median days) | ML (median days) |
|---|---|---|
| Lila | 26 | 33 |
| Periodic | 134 | 133 |
| Orbital (hardware postings) | 251 | |

These spans follow the archive's crawl dates, so they are rough. [roles.md](roles.md#what-the-closed-postings-add) has more on what the closed postings show.

## Coverage and gaps

Fifteen companies have postings here. Five more have only careers-page captures, and five have nothing.

**Careers-page captures only:** Kebotix, Emerald Cloud Lab, Mattiq, Polymerize and Deep Principle. Their careers pages list jobs through embedded widgets that the archive did not capture, such as Greenhouse iframes, or they link out without naming the roles. So Kebotix's board (2019–21) and Emerald Cloud Lab's (2015–26) are lost apart from the page captures, which are linked from their pages here.

**Nothing found:**
- **Radical AI:** no public careers page or board.
- **Telescope Innovations:** no careers pages in the archive.
- **Intrepid Labs:** hires through the University of Toronto's entrepreneurship job board.
- **DP Technology:** a Feishu job board that renders client-side, in Chinese.
- **Altrove:** no public board.

**Thin coverage:**
- **Citrine:** only from 2025 on. Its 2019–22 openings sat in a Greenhouse embed that was never captured.
- **Mitra Chem:** one 2021 posting plus today's.
- **Materials Nexus:** two postings from 2022.
- **Matlantis:** two postings from 2023–24.
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

**For software, hire software engineers and teach them the lab.** 43% of software postings mention robots or lab hardware, but nearly always as a bonus rather than a requirement.

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

The previous pass said Entalpic's Notion page could not be read without a browser. That was wrong: Notion's page API returns the hiring database as JSON.

**Past postings** come from Wayback Machine captures of the same boards, plus the older boards the companies have since left. Two kinds of capture are read:
- **Every archived posting URL** under each board. Its first and last capture give the dates.
- **The board page itself, once a quarter.** It lists postings that were never captured on their own.

Most applicant-tracking systems embed the posting in the page as JSON:
- Ashby: `window.__appData`
- Greenhouse: its Remix context
- Rippling: `__NEXT_DATA__`
- schema.org `JobPosting` on others

So one archived page yields the title, team, location, pay and full description, even where the page looks like an empty JavaScript app in a browser. The archive serves these pages gzip-encoded as originally sent, and [`fetch.get`](../../../scripts/startup_landscape/fetch.py) decodes them. The earlier note that Periodic's launch-day postings "could not be recovered" came from reading the undecoded bytes.

**Fetching through the Pi.** From the GitHub runner, the Wayback Machine refused connections twice:
- first after four parallel index queries;
- then after about six requests in a minute, well under its usual limit of about 15.

GitHub-hosted runners share outbound IP addresses, so other jobs' traffic counts against the same limit. The archive crawl was therefore run from the CubXL Raspberry Pi over Tailscale SSH:
- from a scratch directory, `~/jd-fetch`;
- as one client, 6 s between requests, reads capped at 150 KB/s, at `nice 10`.

The Pi was idle (load 0.00), and its camera script kept running throughout. The scratch directory was deleted afterwards and nothing else on the Pi was changed. The live job-board APIs were read from the runner. Nothing logged in anywhere, and no job aggregator was read: no LinkedIn, Indeed, Glassdoor or Wellfound.

**Building the tables.** [`scripts/startup_landscape/jobs_report.py`](../../../scripts/startup_landscape/jobs_report.py) does the following:
- **Merges** the two sources by posting ID.
- **Dedupes by title.** Two postings with the same title whose date spans overlap or come within 45 days are one posting. A board listing and its own page can carry different IDs, and Ashby re-issues IDs when a posting is edited. A title that comes back after a longer gap is kept as a re-posting.
- **Classifies** each posting into the survey's six functions by its title. It uses the rules in `analyze.py`, plus a few for automated-systems, firmware, recruiting and founding roles. A generic "engineer" on a lab or hardware team counts as lab automation.
- **Reads requirements from the role-specific text only.** It drops lines that recur in at least 40% of one company's postings (the company pitch, perks, legal text) and sections headed "About us", "Benefits", "Equal opportunity" and the like. This keeps a pitch such as "we combine AI and robotics" from making every role look like a robotics role.
- **Records three requirement fields** from what is left: the degrees named, the smallest "N+ years" figure, and a fixed list of skills.

**Dates.** `first_seen` is the earliest of the board's publish date and the first Wayback capture. `last_seen` is the latest capture, or "open" if the posting was live on 10 October 2026. These are bounds from the inside: a posting was open at least that long.

**Privacy and text.** Descriptions are the companies' own published wording. They are kept for research, and each one links to its source capture or live page. Email addresses and phone numbers are removed. A scan for people named in the descriptions found only executives, in line with the survey's leadership-only rule.

## Caveats

- **Wayback coverage is uneven.** A role that was never crawled is missing, and a closed role whose page was never captured on its own has a title and dates but no description.
- **Date spans are lower bounds.** Postings live on 10 October 2026 carry the board's publish date, which some boards reset when a posting is edited.
- **The function labels come from titles.** "Research Scientist, Data" and "Forward Deployed Engineer, Physics & Simulation" could each sit in two places.
- **The requirement fields are keyword reads.** "Degree named" counts any mention, so "PhD or equivalent experience" and "PhD preferred" both count as naming a PhD.
