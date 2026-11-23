# Group G: AM, lab automation, CALPHAD and publishing infrastructure (Nov 2026)

Openness is initial→current on the 0–4 scale. All 21 entries used WebFetch only, because the search budget was exhausted. The last column shows revenue where no market value exists.

| Name | Open | Origin | Founded | Outcome | Value or scale (date) |
|---|---|---|---|---|---|
| Thermo-Calc (SE) | 0→0 | Academic (KTH) | 1997 | Foundation-owned | n/a |
| pycalphad | 3→3 | Academic (Penn State) | 2014 | 2 maintainers | 50k downloads/month (2026-11) |
| OpenCalphad | 3→3 | Academic (ICAMS) | 2013 | Informal collaboration | n/a |
| Aconity3D (DE) | 0→0 | Founder | n/a | Private | n/a |
| EOS (DE) | 0→0 | Founder, family | 1989 | Private | €360M revenue (2022) |
| Desktop Metal | 0→0 | Founder (MIT) | 2015 | SPAC → Nano → Ch. 11 (2025) | up to $2.5B SPAC (2020) |
| Markforged | 0→0 | Founder | 2013 | SPAC → Nano → Stratasys | $42.5M sale (2026-05) |
| Velo3D | 0→0 | Founder | 2014 | SPAC; creditor-controlled | $109M cap (2026-11-23) |
| 3D Systems | 0→0 | Founder | 1986 | Public | $255M cap (2026-11-23) |
| Stratasys | 0→0 | Founder | 1989 | Public, consolidator | $469M cap (2026-11-23) |
| Carbon | 0→0 | Founder (academic) | 2013 | Private VC | ~$2.5B (2019-12) |
| Hamilton | 0→0 | Founder, family | 1950 | Private | ~3,000 staff |
| Tecan (CH) | 0→0 | Founder | 1980 | Public | $3.61B cap (2026-11-23) |
| Automata (UK) | 0→0 | Founder | n/a | Private VC | ≥$135M raised (2026-01) |
| Kardex (CH) | 0→0 | Corporate | 1977 | Public | $2.05B cap (2026-11-23) |
| UR + MiR (DK) | 0→1 | Academic (SDU) | 2005 | Teradyne ($285M, 2015) | $308M revenue (2025) |
| COS / OSF | 4→4 | Academic (UVA) | 2013 | Nonprofit; OSF narrowed | $10.2M revenue (2024) |
| arXiv | 4→4 | Government (LANL) | 1991 | Independent nonprofit (2026) | $6.4M revenue (FY2025) |
| OurResearch / OpenAlex | 4→4 | Nonprofit | 2011 | Nonprofit | $4.3M revenue (FY2025) |
| Digital Science / Figshare | 1→1 | Founder | 2011 | Holtzbrinck-owned | n/a |
| Papers with Code | 3→3 | n/a | 2018 | Meta; shut 2025 | n/a |

## Observations

1. **Every instrument maker here is closed, and openness comes from outside.** All 8 AM firms, Hamilton, Tecan, Automata and Kardex score 0. UR+MiR reaches 1 only through a BSD-3 ROS 2 driver. PyLabRobot (MIT) drives Hamilton STARs and Tecan EVOs without either vendor among its supporters, and pycalphad and OpenCalphad read Thermo-Calc's TDB files. Aconity3D's LPBF machines are the only ones exposing every parameter and scan vector, but they carry no open licence. Patents are the AM moat:
   - 3D Systems sued EOS (cross-licensed 2004) and Formlabs (2012).
   - Stratasys (~2,700 patents) sued Bambu Lab in 2024.
2. **The SPAC boom became a bust.**
   - Desktop Metal listed at up to $2.5B (2020), was bought by Nano Dimension (April 2025) and filed Chapter 11 three months later.
   - Markforged went from ~$2.1B (2021) to $116M (2025) to $42.5M (Stratasys, 2026), about 2% of its listing value.
   - A creditor took 95% of Velo3D for $22.4M of notes.

   The incumbents 3D Systems (−97%) and Stratasys (−93%) also sank from their 2013 peaks. Family-owned EOS, with no outside investors, stayed independent.
3. **Lab automation had its own COVID boom and bust.** Tecan's market cap fell 77% (end-2021 to end-2025) as sales dropped from CHF 1.14B to CHF 883M. Teradyne Robotics' revenue fell from $375M to $308M (2023–25), with pre-tax losses reaching $99M and about 400 jobs cut. Automata calls itself "open by design" but publishes no open licence.
4. **Open-science infrastructure runs on small nonprofit budgets.**
   - arXiv serves 2.9M papers and 6B downloads with 28 staff and $6.7M of expenses (FY2025). It left Cornell in July 2026 with $17.2M of multiyear pledges.
   - OurResearch built OpenAlex on $4.3M of revenue (FY2025, 56% grants), after negative net assets in FY2024.
   - COS raised about $69M in grants (2013–24), mostly from one foundation, yet it stopped new OSF projects on 16 November 2026 because it could not raise $4–5M a year.
5. **Open licences outlive their hosts, but services don't.** Meta let Papers with Code decay and redirected it to Hugging Face (2025), and its CC BY-SA dumps let the community archive it. OSF's public content stays readable with DOIs. Figshare's code is closed, and it belongs to Holtzbrinck, which also owns 53% of Springer Nature.
6. **AI now costs open infrastructure money.** arXiv's monthly submissions doubled in two years (40,363 in September 2026), with cs.AI up sixfold, forcing rate limits and bans. OpenAlex now charges for heavy API use. 21% of Thermo-Calc users surveyed already use LLMs with it.
7. **For a lab that buys closed instruments:**
   - Choose vendors for access to parameters and interfaces (Aconity3D-style), and script them from open code (PyLabRobot, UR's ROS 2 driver).
   - Publish CALPHAD assessments as TDB files that pycalphad can use.
   - Deposit data and code with DOIs on durable repositories (Zenodo, arXiv) and keep local copies. A vendor (Desktop Metal) and a free service (OSF) each failed or narrowed within a year.
