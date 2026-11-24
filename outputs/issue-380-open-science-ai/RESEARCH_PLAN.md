# Research plan for issue #380, and what became of it

The plan below was posted to the tracking comment at 21:49 UTC on 2026-11-23, before the work began. The comment was
overwritten by later progress updates, so it is preserved here verbatim (unchecked boxes as posted). The outcome
of each section follows it.

## The plan as posted (21:49 UTC)

**A. Starting the long-running jobs (21:45–22:30)**
- [x] Set up the runner: ffmpeg, xdotool and Chromium installed; tailnet up, CubXL Pi visible
- [ ] Edison: about 8 literature and precedent queries, polled in the foreground. Topics:
  - the economic value of open-source software
  - the return on open science and open data (PDB to AlphaFold, the Materials Project, Landsat, the Human Genome Project)
  - the economics of open-source hardware (Pearce and others)
  - outcomes of open-source business models and relicensing
  - open-weight AI and its economic effects
  - openness in academia vs. national labs vs. industry over time
  - open-source self-driving labs and lab automation
  - US policy: the Nelson memo, the NTIA open-weights report, the AI Action Plan, the Genesis Mission
- [ ] Use `gh api` to dump every issue, PR and discussion, with every comment and review comment, from `AccelerationConsortium/ac-dev-lab` and `sparks-baird/self-driving-lab-demo`. Then classify the threads on open-source commercialization.

**B. Searching through the Pi (22:15 onward, ongoing)**
- [ ] A visible (headed) Chromium on a virtual display whose traffic exits through the Pi over an SSH SOCKS tunnel, using the repo's existing tunnel setup script. I'll use mouse automation for search engines, Reddit, YouTube, Hacker News, blogs and forums, and save screenshots and extracted text as evidence.

**C. Company and project case studies (22:30–01:30)**
- [ ] A structured dataset of about 80 or more organizations. Each record gets:
  - openness level (0–4) and license history with dates
  - origin (academic, government, corporate or community)
  - founding year, funding and outcome (IPO, acquired, private or dead)
  - market value over time
  - forks and relicensing events (as a measure of robustness), and longevity and risk
  
  Every claim gets a source URL. Coverage:
  - software (MongoDB, Elastic, Redis, HashiCorp, Confluent, Red Hat, GitLab, Databricks, Prefect, Astronomer/Airflow, Grafana and more)
  - Big Tech (Meta, Google, Microsoft)
  - AI labs
  - open hardware (Arduino, Raspberry Pi, Prusa, MakerBot, Adafruit, SparkFun, Opentrons, LulzBot, SiFive and more)
  - physical-science and AI-for-science companies (Schrödinger, Citrine, Emerald Cloud Lab, Strateos, Periodic Labs, Lila and more)
  
  Several hundred searches in total, split across parallel research agents and checked one by one.
- [ ] Market numbers: the HBS estimate of OSS value ($8.8T demand side), the EU estimate, BEA/NSF OSS investment, how the open-source IPO cohort has performed, and acquisition values over time

**D. Quantitative trends (00:00–02:00)**
- [ ] Epoch AI's notable-models data: openness of AI models by sector (academia, government, industry), year and country, with a US focus
- [ ] OpenAlex: open-access share by institution type over time (academia, government/national labs, industry), for all fields and for the Physical Sciences domain
- [ ] Software vs. hardware vs. physical science, compared over time

**E. Language of the AI labs (00:30–01:30)**
- [ ] Collect Anthropic and OpenAI texts on open source, open weights, open science and science or physical sciences: charters, policy submissions, blogs, gpt-oss, MCP and so on. Add Meta, Google DeepMind and DeepSeek for contrast. Count terms and pull key quotes.

**F. DAL and #318 (01:30–02:00)**
- [ ] Read DAL and #318 and analyze them in open-source and open-science terms

**G. Visualizations and video (01:45–03:00)**
- [ ] Animated figures (matplotlib), narrated with an offline TTS engine, assembled with ffmpeg and uploaded to YouTube as **public with notifySubscribers=False**

**H. Write-up (ongoing; final by 03:20)**
- [ ] A report under `research/open-science-ai/` with the data, scripts, sources and figures, pushed every hour

**Backlog for any spare time:** more company deep dives, more Pi searches (Reddit and YouTube talks), cross-checking numbers against a second source, and sensitivity analyses.

## What became of it

| Section | Planned | Done |
| --- | --- | --- |
| A. Edison | about 8 queries | 15 jobs (literature, high-effort literature and precedent), all fetched with trajectories; [`edison/SYNTHESIS.md`](edison/SYNTHESIS.md) |
| A. GitHub mining | every issue, PR, discussion and comment in two repos | 4,928 records in 816 threads, 118 coded for commercialization; [`gh-mining/`](gh-mining/) |
| B. Pi browser | headed Chromium through the Pi, mouse automation | 150 searches, 84 page fetches, 7 YouTube transcript sessions for 6 videos; [`pi-browser/`](pi-browser/), [`voices/`](voices/) |
| C. Case studies | about 80 organizations | 179 case files in groups A–J with 1,354 cited sources, calibration, a spot audit and verification passes; [`companies/`](companies/) |
| C. Market numbers | OSS value, investment, IPO cohort, acquisitions | README §1–3, [`data/`](data/) |
| D. Trends | Epoch AI, OpenAlex, software vs. hardware vs. science over time | README §2, §5–6; plus the GitHub Innovation Graph, PDB, DOE code.json and OpenAlex topic counts |
| E. Language | Anthropic and OpenAI texts, with contrast labs | 57 documents, term rates and quotes; [`language/`](language/) |
| F. DAL and #318 | analysis in open-source terms | [`dal/dal_openness_audit.md`](dal/dal_openness_audit.md) and [`dal/suggested_proposal_language.md`](dal/suggested_proposal_language.md) |
| G. Video | animated, narrated, public without notifying subscribers | four videos (11:41, 4:53, 3:40 and a 2:18 corrections video) |
| H. Write-up | `research/open-science-ai/` | written to `outputs/issue-380-open-science-ai/` instead, with a brief, a playbook, a figure index and video notes |
| Backlog | deep dives, more Pi searches, second-source checks, sensitivity analyses | groups G, I and J; verification passes 2 and 3; an independent review (39 issues, all resolved); robustness, fork and event-study analyses |

One planned item changed: the WebSearch budget ran out about 15 minutes in, so the case-study agents used fetches of
known pages rather than "several hundred searches"; see README, Method.
