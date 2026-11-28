# Round 6: what the grid costs

Made by `python out/twin6/checks/grid_hours.py` from `smoke.json`. CPU-hours of two-year runs on the runner that timed them (an AMD EPYC 9V45, every vCPU busy, as in a slice); a runner runs four at a time. **High** prices each extrapolated run with its cost a day still rising as it was (what `status` and `slices` use), **low** with its latest cost a day held. The cost a day has risen in every stretch measured so far, and copper's GP nodes were still filling at day ~400 (checks/profile/profile.md), so low is more likely to be short than high is to be long. Everything is simulated.

| Lab | Policies | Runs | CPU-hours a run, low-high (mean) | Longest run, high (h) | Core-hours, low | Core-hours, high |
|---|---|---|---|---|---|---|
| conventional | BOFN and pKGFN | 320 | 0.5-0.5 | 1.6 | 165 | 165 |
| conventional | heuristic and funnel | 160 | 0.3-0.3 | 1.3 | 54 | 54 |
| automated | BOFN and pKGFN | 608 | 5.2-7.7 | 12.2 | 3,174 | 4,672 |
| automated | heuristic and funnel | 304 | 0.4-0.4 | 1.3 | 111 | 111 |
| all | | 1,392 | | | 3,505 | 5,004 |

**Runner-hours at four runs a runner: 876 (low) to 1,251 (high)** with the engine the timing runs used (568ab5f); **813 to 1,157 with this engine** (the automated lab's BOFN and pKGFN at 0.92 of their time: 4.8-7.1 CPU-hours a run on average). Core-hours: 3,251 to 4,630.

**In 6-hour jobs** (`ids --hours 5.2`, four runs at a time, a run still going at 5.2 hours carried on by the next job from a checkpoint): about 21 CPU-hours of runs a job, so 156 to 223 jobs for the grid with this engine. A job's CPU-hours are worth 40 of the conventional lab's BOFN and pKGFN runs; 61 of the conventional lab's heuristic and funnel runs; 2.9-4.3 of the automated lab's BOFN and pKGFN runs; 57 of the automated lab's heuristic and funnel runs (on average; a run longer than 5.2 CPU-hours always spans two jobs).

Extrapolated two-year runs:

* `r6_vertical_parallel_bofn3_reorder`: day 500 reached at 7,343 CPU s, 42.99 CPU s a day over the last 50 days, rising 0.1322 a day: two years 17,230-20,726 CPU s (4.8-5.8 h)
* `r6_vertical_parallel_bofn3_reorder_hpc16`: day 510 reached at 7,691 CPU s, 43.99 CPU s a day over the last 50 days, rising 0.0341 a day: two years 17,370-18,195 CPU s (4.8-5.1 h)
* `r6_vertical_parallel_pkgfn3_reorder`: day 480 reached at 7,356 CPU s, 60.73 CPU s a day over the last 50 days, rising 0.563 a day: two years 22,539-40,131 CPU s (6.3-11.1 h)
* `r6_vertical_parallel_pkgfn3_reorder_hpc16`: day 500 reached at 7,487 CPU s, 50.6 CPU s a day over the last 50 days, rising 0.2369 a day: two years 19,126-25,391 CPU s (5.3-7.1 h)
