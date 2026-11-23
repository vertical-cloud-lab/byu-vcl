# Group G: AM, lab automation, CALPHAD and publishing infrastructure (Nov 2026)

Openness is initial→current on the 0–4 scale. All 21 entries used WebFetch only, because the search budget was exhausted.

| Name | Open | Origin | Founded | Outcome | Value or scale (date) |
|---|---|---|---|---|---|
| Thermo-Calc (SE) | 0→0 | Academic (KTH) | 1997 | Foundation-owned | n/a |
| pycalphad | 3→3 | Academic | 2014 | Active | 50k downloads/month (2026-11) |
| OpenCalphad | 3→3 | Academic | 2013 | Active | n/a |
| Aconity3D (DE) | 0→0 | Founder | n/a | Private | n/a |
| EOS (DE) | 0→0 | Founder | 1989 | Private, family | €360M revenue (2022) |
| Desktop Metal | 0→0 | Founder | 2015 | Chapter 11 (2025) | ≤$2.5B at SPAC (2020) |
| Markforged | 0→0 | Founder | 2013 | Sold to Stratasys | $42.5M (2026-05) |
| Velo3D | 0→0 | Founder | 2014 | Creditor-controlled | $109M cap (2026-11-23) |
| 3D Systems | 0→0 | Founder | 1986 | Public | $255M cap (2026-11-23) |
| Stratasys | 0→0 | Founder | 1989 | Public | $469M cap (2026-11-23) |
| Carbon | 0→0 | Founder | 2013 | Private VC | ~$2.5B (2019-12) |
| Hamilton | 0→0 | Founder | 1950 | Private, family | ~3,000 staff |
| Tecan (CH) | 0→0 | Founder | 1980 | Public | $3.61B cap (2026-11-23) |
| Automata (UK) | 0→0 | Founder | n/a | Private VC | ≥$135M raised |
| Kardex (CH) | 0→0 | Corporate | 1977 | Public | $2.05B cap (2026-11-23) |
| UR + MiR (DK) | 0→1 | Academic | 2005 | Teradyne (2015) | $308M revenue (2025) |
| COS / OSF | 4→4 | Academic | 2013 | OSF narrowed (2026) | $10.2M revenue (2024) |
| arXiv | 4→4 | Government | 1991 | Independent (2026) | $6.4M revenue (FY2025) |
| OurResearch | 4→4 | Nonprofit | 2011 | Nonprofit | $4.3M revenue (FY2025) |
| Digital Science / Figshare | 1→1 | Founder | 2011 | Holtzbrinck-owned | n/a |
| Papers with Code | 3→3 | n/a | 2018 | Shut by Meta (2025) | n/a |

## Observations

1. **The instrument makers are closed, and outsiders supply the openness.** All 8 AM firms, Hamilton, Tecan, Automata and Kardex score 0. UR+MiR reaches 1 only through a BSD-3 ROS 2 driver. PyLabRobot (MIT) drives Hamilton and Tecan robots, and pycalphad and OpenCalphad read Thermo-Calc's TDB files. Patents protect the AM firms: 3D Systems sued EOS and Formlabs, and Stratasys sued Bambu Lab (2024).
2. **The SPAC boom became a bust.**
   - Desktop Metal listed at up to $2.5B (2020), was bought by Nano Dimension (April 2025) and filed for Chapter 11 three months later.
   - Markforged fell from ~$2.1B (2021) to a $42.5M sale (2026).
   - A creditor took 95% of Velo3D.

   3D Systems (−97%) and Stratasys (−93%) sank from their 2013 peaks. Family-owned EOS stayed independent.
3. **Lab automation had a COVID boom and bust.** Tecan's market cap fell 77% (2021–25). Teradyne Robotics' revenue fell from $375M to $308M (2023–25), and about 400 jobs were cut in 2025.
4. **Open-science infrastructure runs on small nonprofit budgets.**
   - arXiv serves 2.9M papers with 28 staff and $6.7M of expenses (FY2025). It left Cornell in July 2026, and three philanthropies pledged $17.2M in September.
   - OurResearch ran OpenAlex on $4.3M (FY2025, 56% grants).
   - COS raised ~$69M in grants (2013–24), yet it stopped new OSF projects in November 2026 because it could not raise $4–5M a year.
5. **Open licences outlive their hosts, but services do not.** Meta let Papers with Code decay into a Hugging Face redirect (2025), and its CC BY-SA dumps let the community archive it. Figshare's code is closed and owned by Holtzbrinck.
6. **AI now costs open infrastructure money.** arXiv's monthly submissions doubled in two years (40,363 in September 2026), which forced rate limits. OpenAlex now charges for heavy API use.
7. **For a lab that buys closed instruments:**
   - Buy for access to parameters and APIs (Aconity3D exposes every scan vector).
   - Script instruments with open drivers (PyLabRobot, UR's ROS 2 driver).
   - Publish CALPHAD assessments as TDB files for pycalphad.
   - Deposit data with DOIs on durable repositories (Zenodo, arXiv), and keep local copies.

   A vendor (Desktop Metal) and a free service (OSF) each failed or narrowed within a year.
