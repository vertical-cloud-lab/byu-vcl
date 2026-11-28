# Round 6: what the grid costs

Made by `python out/twin6/checks/grid_hours.py` from `smoke.json`. CPU-hours of two-year runs on the runner that timed them (an AMD EPYC 9V45, every vCPU busy, as in a slice); a runner runs four at a time. **High** prices each extrapolated run with its cost a day still rising as it was (what `status` and `slices` use), **low** with its latest cost a day held. The cost a day has risen in every stretch measured so far, and copper's GP nodes were still filling at day ~400 (checks/profile/profile.md), so low is more likely to be short than high is to be long. Everything is simulated.

| Lab | Policies | Runs | CPU-hours a run, low-high (mean) | Longest run, high (h) | Core-hours, low | Core-hours, high |
|---|---|---|---|---|---|---|
| conventional | BOFN and pKGFN | 320 | 0.5-0.5 | 1.6 | 165 | 165 |
| conventional | heuristic and funnel | 160 | 0.3-0.3 | 1.3 | 54 | 54 |
| automated | BOFN and pKGFN | 608 | 4.2-6.1 | 9.9 | 2,533 | 3,720 |
| automated | heuristic and funnel | 304 | 0.4-0.4 | 1.3 | 111 | 111 |
| all | | 1,392 | | | 2,864 | 4,051 |

**Runner-hours at four runs a runner: 716 (low) to 1,013 (high)** with this engine (the faster trial settings and 64-point GP calls, measured: checks/batch.md; the automated lab's BOFN and pKGFN at 4.2-6.1 CPU-hours a run on average), on the 9V45. Core-hours: 2,864 to 4,051.

**In 6-hour jobs** (`ids --hours 5.2`, four runs at a time, a run still going at 5.2 hours carried on by the next job from a checkpoint): about 21 CPU-hours of runs a job, so 138 to 195 jobs for the grid on 9V45s, about twice as many on EPYC 7763s (checks/batch.md). A job's CPU-hours are worth 40 of the conventional lab's BOFN and pKGFN runs; 61 of the conventional lab's heuristic and funnel runs; 3.4-5.0 of the automated lab's BOFN and pKGFN runs; 57 of the automated lab's heuristic and funnel runs on a 9V45 (on average; a run longer than 5.2 CPU-hours spans two jobs or more).

Extrapolated two-year runs:

* `r6_vertical_parallel_bofn3_reorder`: day 500 reached at 7,343 CPU s on the timing runs' engine, 42.99 CPU s a day over the last 50 days, rising 0.1322 a day: two years 17,230-20,726 CPU s there; batched 13,727-16,494 (3.8-4.6 h)
* `r6_vertical_parallel_bofn3_reorder_hpc16`: day 510 reached at 7,691 CPU s on the timing runs' engine, 43.99 CPU s a day over the last 50 days, rising 0.0341 a day: two years 17,370-18,195 CPU s there; batched 13,779-14,432 (3.8-4.0 h)
* `r6_vertical_parallel_pkgfn3_reorder`: day 480 reached at 7,356 CPU s on the timing runs' engine, 60.73 CPU s a day over the last 50 days, rising 0.563 a day: two years 22,539-40,131 CPU s there; batched 17,934-31,864 (5.0-8.9 h)
* `r6_vertical_parallel_pkgfn3_reorder_hpc16`: day 500 reached at 7,487 CPU s on the timing runs' engine, 50.6 CPU s a day over the last 50 days, rising 0.2369 a day: two years 19,126-25,391 CPU s there; batched 15,174-20,135 (4.2-5.6 h)
