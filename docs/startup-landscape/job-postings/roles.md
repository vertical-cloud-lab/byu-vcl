# What AI-for-materials and self-driving-lab startups hire for: role archetypes

Back to [the job-postings overview](README.md). The hand-coded archetype and degree for each posting are in [`../data/job_postings_roles.csv`](../data/job_postings_roles.csv).

*Source: [`job_postings.jsonl`](../data/job_postings.jsonl), 465 postings from 15 companies, general applications excluded (snapshot 2026-10-10 07:22 UTC), 237 of them closed. 290 were sorted by hand into seven archetypes; Orbital's 10 postings for its own cooling hardware are left out. Degrees are coded from requirement text (88 of 191 postings naming one accept equivalent experience); blurbs and stubs count but are not coded. Pay is posted base salary.*

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

## 1. Lab-automation and robotics engineers (43: Lila 19, Periodic 12, Chemify 6, Medra 5, Dunia 1)

[Robotics Engineer](periodic-labs.md#robotics-engineer-2025-09-22), [Senior Automated Systems Engineer](lila-sciences-lab-automation.md#senior-automated-systems-engineer-2026-01-23), [Senior Firmware Engineer](chemify.md#senior-firmware-engineer-2026-07-15).

**Work.** Periodic's engineers specify workcells, oversee the integrators who build them and commission them (PLC/SCADA, labware "hotels", mobile robots, LIMS drivers). Lila's sustain workcells and test mobile manipulators (ROS2, Isaac Sim); its robotics scientists do motion planning and robot learning. Chemify builds its own robots, firmware included; Medra adapts arms to "biology tools designed for humans".

**Requirements.** Of 40 with requirement text, 20 ask for a bachelor's, 2 for an unspecified degree and 12 for none. The 6 naming a PhD are 4 translator roles that turn experiments into automation specifications ([Periodic's Research Engineer, Lab Automation](periodic-labs.md#research-engineer-lab-automation-2026-08-15), [Lila's Platform Scientist roles](lila-sciences-lab-automation.md#platform-scientist-i-ii-functional-materials-instrumentation-2026-10-05)) and 2 Lila robotics research scientists. CAD appears in 18, Python in 19.

**Pay.** Lila $75.6K–$304K; Periodic $175K–$300K; Medra $110K–$200K.

> “Own the robotics architecture for new cells: end effector strategy, labware plan (nests, racks, hotels), and material flow.” (Periodic, Robotics Engineer)

## 2. Research associates, technicians and robot operators (36: Lila 15, Chemify 7, Medra 6, Periodic 6, Dunia 1, Mitra Chem 1)

[Research Associate - Foundry](medra.md#research-associate-foundry-2026-04-09), [Associate / Engineer I, ResOps, Synthesis](lila-sciences-materials-science.md#associate-engineer-i-resops-synthesis-2026-05-19), [Process Technician, Thin Films](periodic-labs.md#process-technician-thin-films-2026-08-18).

**Work.** They load and monitor automated runs, prepare reagents, and clear routine errors on liquid handlers and workstations (Hamilton, Lynx, Echo, KingFisher, Chemspeed). They calibrate, follow SOPs (named in 16 of 33), log to ELN/LIMS and hand off between shifts. Materials variants add synthesis, deposition and XRD/SEM; Lila's robot operators need ROS2.

**Requirements.** Of 33 with requirement text, 12 ask for a bachelor's, 6 for vocational training (HNC/HND, NVQ, CTA), 3 for school-level only, 5 for none, and 5 are internships or co-ops. 2 require a PhD: Periodic's 12-month [Research Associate - Thin Films (Fixed Term)](periodic-labs.md#research-associate-thin-films-fixed-term-2026-03-10) ($180K–$225K) and Chemify's [Synthetic Chemist](chemify.md#synthetic-chemist-2026-09-25), who reviews NMR and UPLC-MS data on evening and weekend shifts. 11 require nights, weekends, off-hours or on-call work (as do 2 operations postings). 4 of Periodic's 5 technician postings and 6 Lila lab roles are contracts.

**Pay.** Lila $72K–$217.9K; Periodic technicians $100K–$165K; hourly: Mitra Chem Lab Technician $30–45/h; Periodic Process Technician, Thin Films $45–65/h.

> “Our robots don't sleep, so this role includes regular night and/or weekend shifts.” (Medra, Research Associate - Foundry)

## 3. Experimental materials and chemistry scientists (27: Lila 18, Periodic 5, Atinary 1, Chemify 1, Dunia 1, Mitra Chem 1)

[Research Scientist, Thin Films](periodic-labs.md#research-scientist-thin-films-2025-10-31), [Scientist I/II, X-ray Diffraction Characterization](lila-sciences-materials-science.md#scientist-i-ii-x-ray-diffraction-characterization-2026-09-14), [Research Scientist, Thermocatalysis](dunia-innovations.md#research-scientist-thermocatalysis-2026-02-04).

**Work.** Most own one synthesis or measurement method (PVD/PLD/MBE films, solid-state growth, organic and process chemistry, cryogenic transport, XRD, XRF/EDS, electron diffraction). They make it high-throughput, set its calibration and QC, and specify what the engineers automate. Lila's characterization scientists also own "machine-readable" output and analysis code.

**Requirements.** 23 of 25 name a PhD (4 also accept an MS; 1 only prefers one); the exceptions are Lila's Microfabrication Scientist I/II (bachelor's) and Periodic's Research Engineer, Semiconductor (master's). Yet 6 Periodic research postings asking for a PhD set a formal minimum of a bachelor's or equivalent. 15 of 16 computational postings with requirement text (DFT, CADD, simulation) name a PhD.

**Pay.** Lila $108K–$198K (Scientist I to Senior); Periodic $160K–$350K.

> “The ideal candidate is credible at both the instrument and the keyboard” (Lila, Scientist I/II, Characterization and Composition Analysis)

## 4. ML researchers and engineers (79: Lila 32, Periodic 13, CuspAI 7, Orbital 6, 21 at seven others)

[Research Scientist, Scaling RL](periodic-labs.md#research-scientist-scaling-rl-2026-10-01), [ML Scientist I/II, AI for Protein Engineering](lila-sciences-ml-research.md#ml-scientist-i-ii-ai-for-protein-engineering-2026-09-15), [ML Engineer, Agents & Reasoning](dunia-innovations.md#ml-engineer-agents-reasoning-2026-02-06).

**Work.** Some train or post-train LLMs (Periodic, Medra, Lila). Others build domain models: protein and cell-biology models at Lila, generative chemistry and robot-camera vision at Chemify, agents at Dunia and CuspAI. Their lab link is choosing experiments: 15 of 63 mention active learning, Bayesian optimization or DOE.

**Requirements.** 35 of 63 name a PhD, 21 as the headline requirement. Periodic's 10 frontier-model postings set no degree bar above a bachelor's or equivalent, asking instead for experience such as "training LLMs on curated mixes of trillions of tokens".

**Pay.** Lila $144K–$570K; Periodic $225K–$350K.

> “agents must reason about messy reality: experiments that fail, data that contradicts itself, and physical systems that don’t reset cleanly.” (Dunia, ML Engineer, Agents & Reasoning)

## 5. Software engineers building lab software (38: Lila 17, Chemify 10, Medra 5, Atinary 2, Periodic 2, Orbital 1, Tetsuwan 1)

[Senior Software Engineer I/II, Back-end/Data, Robotics](lila-sciences-software-eng.md#senior-software-engineer-i-ii-back-end-data-robotics-2026-08-10), [Principal Architect – Robotics & Hardware Abstraction](chemify.md#principal-architect-robotics-hardware-abstraction-2026-03-03), [Software Engineer](tetsuwan-scientific.md#software-engineer-2026-06-03).

**Work.** They build lab systems of record that track what was planned and what actually ran, schedulers for instruments and robots (Temporal, Flyte), instrument drivers, data pipelines, hardware-in-the-loop tests and digital twins. At Tetsuwan, an OCaml compiler turns protocols into robot instructions.

**Requirements.** 31 of 35 name Python. Only 1 of 35 requires hands-on hardware experience: Chemify's architect role asks for "8+ years of C/C++ in safety-critical or physically consequential domains such as robotics, automotive, aerospace, or industrial automation". 2 require adjacent experience (industrial telemetry; a hardware-in-the-loop "mindset"), 26 list hardware or lab experience as a bonus and 6 omit it. 13 require hands-on use of AI coding assistants.

**Pay.** Lila $108K–$390K; Periodic $250K–$350K; Medra $170K–$210K; Tetsuwan $140K–$180K.

> “the code you ship has physical consequences in the lab” (Chemify, Senior Full Stack SW Engineer)

## 6. Forward-deployed engineers and application scientists (20, 10 companies)

[Staff Forward Deployed Engineer, Physical Sciences](lila-sciences-materials-science.md#staff-forward-deployed-engineer-physical-sciences-level-flexible-2025-10-06), [Application Scientist (AI Materials Science), Singapore](cuspai.md#application-scientist-ai-materials-science-singapore-2026-03-16), [Scientist, Biology](medra.md#scientist-biology-2026-02-17).

**Work.** FDEs wire the platform into customer systems: PLCs and MES/SCADA (Lila), instruments and test rigs (Orbital), robots (Medra), LLMs in fabs (Periodic). Application scientists (CuspAI, Citrine, Medra, Matlantis) turn platform output into experiment or simulation plans, train users and install instruments.

**Requirements.** 5 of 17 with requirement text name a PhD and 7 name no degree. Orbital wants "no prior chemistry, materials, or engineering experience".

**Pay.** Lila $192K–$256K; Periodic $250K–$400K; Medra $140K–$175K; Citrine €70K–€100K.

> “Serve as CuspAI’s "eyes and ears" in the lab” (CuspAI, Application Scientist, AI Materials Science)

## 7. Lab operations, facilities and EHS (22: Lila 10, Chemify 4, Periodic 4, Atinary 1, Dunia 1, Medra 1, Orbital 1)

[Lab Operations Specialist](lila-sciences-lab-automation.md#lab-operations-specialist-2026-09-28), [Lab Operations & Procurement Manager](dunia-innovations.md#lab-operations-procurement-manager-2026-02-04), [Process Safety Engineer](periodic-labs.md#process-safety-engineer-2026-10-07).

**Work.** They run maintenance, calibration, inventory, gases, vendors and procurement; Dunia's manager negotiates "multi-million euro" equipment contracts, and Lila's include facilities directors and a factory-layout engineer. Periodic's EHS postings cover permits, HAZOP reviews and change management for labs running unattended overnight; both senior ones include helping train an LLM to reason about process hazards.

**Requirements.** 8 of 19 ask for a bachelor's (2 via Periodic's form line), 2 for a certificate or associate degree and 9 for none. NEBOSH and CSP/CIH certificates appear.

**Pay.** Lila $68K–$228K; Periodic $96K–$124K (EHS Technician) to $250K–$325K (Head of EHS).

> “not a compliance function bolted on after the fact” (Periodic, Head of Environmental Health & Safety)

## What the closed postings add

The 237 closed postings come from archived board captures. They cannot show whether a role was filled or withdrawn, and their last dates are only last captures: 60 of Lila's 91 closed postings were last seen in June 2026, when most captures of its board were made. Still, lab roles turned over more than software roles. Of Lila's postings first seen by 12 June 2026, 37 of 42 lab-side roles have closed, against 18 of 23 ML and computational roles and 4 of 13 lab-software roles. The median observed span was much the same for lab and ML roles (35 and 36 days), so closing more often was not closing faster. None of the 4 chemistry scientist roles Lila opened on 25 March 2026 is still open. Periodic has closed 7 of the 8 lab-engineering and facilities roles it posted at launch: the Automation Engineer is still open, and the Research Engineer, Lab Automation was re-posted in August 2026. Overall, 9 of its 16 lab and 7 of 11 ML postings from before mid-June have closed.

## Cross-cutting observations

- **Lab roles differ by company.** Periodic is building a materials lab through vendors: 8 of its first 19 postings were lab engineering or facilities, most technicians are contractors, and pay is highest. Lila runs a larger, shift-based operation for less: Scientist I/II at $108K–$170K against $160K–$350K for Periodic's Research Scientists; Engineer I at $75.6K–$100.8K against $100K–$130K for Periodic's Laboratory Technician. Medra runs night shifts and embeds scientists at customers. Chemify builds its own robot fleet and staffs it with vocationally trained shift technicians. Dunia ties its scientist to customer proofs of concept.
- **Requirements diverge.** 1 of 35 software postings requires hardware experience. A PhD is asked for in 6 of 40 lab-automation postings, against 23 of 25 experimental-scientist, 15 of 16 computational, 2 of 33 technician and 0 of 19 operations postings.
- **What an academic SDL would need first.** The closest matches are a PhD research engineer who turns experiments into automation requirements and Python workflows (Periodic's Research Engineer, Lab Automation, $200K–$250K) and a bachelor's-level [Automation Engineer](periodic-labs.md#automation-engineer-2025-09-22) who writes instrument drivers and connects them to a LIMS. Next come a technician to keep the platform calibrated, stocked and documented, and someone to review the hazards of unattended runs. Periodic's thin-film postings also value university shared-cleanroom experience, down to "tool reservation systems".
