# Round 6: what the grid costs

Made by `python out/twin6/checks/grid_hours.py` from `smoke.json`. CPU-hours of two-year runs on the runner that timed them (an AMD EPYC 9V45, every vCPU busy, as in a slice); a runner runs four at a time. **High** prices each extrapolated run with its cost a day still rising as it was (what `status` and `slices` use), **low** with its latest cost a day held. The cost a day has risen in every stretch measured so far, and copper's GP nodes were still filling at day ~400 (checks/profile/profile.md), so low is more likely to be short than high is to be long. Everything is simulated.

| Lab | Policies | Runs | CPU-hours a run, low-high (mean) | Longest run, high (h) | Core-hours, low | Core-hours, high |
|---|---|---|---|---|---|---|
| conventional | BOFN and pKGFN | 320 | 0.5-0.5 | 1.6 | 165 | 165 |
| conventional | heuristic and funnel | 160 | 0.3-0.3 | 1.3 | 54 | 54 |
| automated | BOFN and pKGFN | 608 | 3.3-5.5 | 7.0 | 2,027 | 3,358 |
| automated | heuristic and funnel | 304 | 0.4-0.4 | 1.3 | 111 | 111 |
| all | | 1,392 | | | 2,358 | 3,689 |

**Runner-hours at four runs a runner: 590 (low) to 922 (high).**

Extrapolated two-year runs:

* `r6_vertical_parallel_bofn3_reorder`: day 410 reached at 3,622 CPU s, 27.38 CPU s a day over the last 50 days, rising 0.1759 a day: two years 12,384-21,391 CPU s (3.4-5.9 h)
* `r6_vertical_parallel_bofn3_reorder_hpc16`: day 420 reached at 3,590 CPU s, 32.32 CPU s a day over the last 50 days, rising 0.187 a day: two years 13,609-22,596 CPU s (3.8-6.3 h)
* `r6_vertical_parallel_pkgfn3_reorder`: day 410 reached at 3,565 CPU s, 26.48 CPU s a day over the last 50 days, rising 0.136 a day: two years 12,037-19,000 CPU s (3.3-5.3 h)
* `r6_vertical_parallel_pkgfn3_reorder_hpc16`: day 410 reached at 3,359 CPU s, 31.51 CPU s a day over the last 50 days, rising 0.2164 a day: two years 13,444-24,524 CPU s (3.7-6.8 h)
