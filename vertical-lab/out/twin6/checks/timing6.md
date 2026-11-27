# Round 6: timing runs and BOFN's scale pilot

Made by `python out/twin6/checks/timing6.py table` from `timing6.jsonl` and `timing6_progress.jsonl`. Seed s of the stocked arm of each lab (the automated lab's parallel plan), at the scale named. **CPU seconds** are the run's own process time, what it costs a slice that runs one run per vCPU; wall seconds stretch when this runner ran more than four things at once (the load average at the end says how busy it was). Everything is simulated.

| Run | Days | CPU s | Wall s | Load at end | GP fits | Al T1 / T2 day | Cu T1 / T2 day | Al / Cu tested | Al / Cu best new | Bought used | twin/ dirty |
|---|---|---|---|---|---|---|---|---|---|---|---|
| conventional fast 64x | 730 | 1,187 | 4,211 | 12.63 | 0 | 85.358 / 134.4 | 249.1 / 499.548 | 84 / 7 | 0.7028 / 0.6915 | - | False |
| vertical fast 64x | 730 | 1,299 | 4,502 | 12.25 | 0 | 56.65 / None | 330.133 / 379.441 | 348 / 253 | 0.63 / 0.7346 | edm, instron | False |

**Not finished** (the cost so far, from the progress file, and the two years extrapolated: `low` at the latest 50 days' rate, `high` with that rate still rising at its slope over the last 100 days):

| Run | Last day reached | CPU s so far | Wall s so far | CPU s a simulated day, last 50 days | Its rise a day | Two years, low | Two years, high |
|---|---|---|---|---|---|---|---|
| conventional bofn3 64x | 600 | 1,418 | 4,763 | 2.6 | 0.006 | 1,762 | 1,816 |
| conventional pkgfn3 64x | 560 | 1,406 | 4,748 | 3.0 | 0.000 | 1,925 | 1,925 |
| pilot vertical bofn3 s0 64x | 40 | 68 | 463 | - | - | - | - |
| pilot vertical bofn3 s1 64x | 20 | 35 | 235 | - | - | - | - |
| vertical bofn3 16x | 380 | 2,252 | 4,576 | 22.8 | 0.207 | 10,217 | 22,883 |
| vertical bofn3 64x | 360 | 2,253 | 4,617 | 18.4 | 0.093 | 9,063 | 15,451 |
| vertical pkgfn3 16x | 380 | 2,288 | 4,751 | 22.4 | 0.196 | 10,130 | 22,118 |
| vertical pkgfn3 64x | 360 | 2,241 | 4,546 | 19.6 | 0.175 | 9,505 | 21,514 |

* **vertical bofn3 64x lean**: stopped at day 10 at 21:39 UTC: the automated lab's GP runs proved to take several CPU-hours each, so the CPU went to the runs asked for.
* **vertical bofn3 64x wait**: stopped at day 20 at 21:39 UTC, for the same reason.

CPU seconds by simulated day (every 100 days), all runs:

| Run | day 100 | day 200 | day 300 | day 400 | day 500 | day 600 | day 700 |
|---|---|---|---|---|---|---|---|
| conventional bofn3 64x | 171 | 405 | 660 | 904 | 1,167 | 1,418 |  |
| conventional fast 64x | 160 | 327 | 492 | 655 | 817 | 976 | 1,136 |
| conventional pkgfn3 64x | 172 | 418 | 683 | 946 | 1,224 |  |  |
| pilot vertical bofn3 s0 64x |  |  |  |  |  |  |  |
| pilot vertical bofn3 s1 64x |  |  |  |  |  |  |  |
| vertical bofn3 16x | 49 | 141 | 644 |  |  |  |  |
| vertical bofn3 64x | 170 | 421 | 1,195 |  |  |  |  |
| vertical bofn3 64x lean |  |  |  |  |  |  |  |
| vertical bofn3 64x wait |  |  |  |  |  |  |  |
| vertical fast 64x | 160 | 328 | 503 | 686 | 869 | 1,050 | 1,242 |
| vertical pkgfn3 16x | 49 | 142 | 670 |  |  |  |  |
| vertical pkgfn3 64x | 170 | 414 | 1,085 |  |  |  |  |
