# Round 6: timing runs and BOFN's scale pilot

Made by `python out/twin6/checks/timing6.py table` from `timing6.jsonl` and `timing6_progress.jsonl`. Seed s of the stocked arm of each lab (the automated lab's parallel plan), at the scale named. **CPU seconds** are the run's own process time, what it costs a slice that runs one run per vCPU; wall seconds stretch when this runner ran more than four things at once (the load average at the end says how busy it was). Everything is simulated.

| Run | Days | CPU s | Wall s | Load at end | GP fits | Al T1 / T2 day | Cu T1 / T2 day | Al / Cu tested | Al / Cu best new | Bought used | twin/ dirty |
|---|---|---|---|---|---|---|---|---|---|---|---|
| conventional bofn3 64x | 730 | 1,755 | 5,377 | 10.5 | 65 | 234.4 / 273.4 | 250.004 / 250.004 | 18 / 3 | 0.7228 / 0.682 | - | False |
| pre conventional bofn3 s0 1x | 160 | 20 | 41 | 12.35 | 16 | None / None | None / None | 1 / 0 | 0.0 / 0.0 | - | False |
| conventional fast 64x | 730 | 1,187 | 4,211 | 12.63 | 0 | 85.358 / 134.4 | 249.1 / 499.548 | 84 / 7 | 0.7028 / 0.6915 | - | False |
| pre conventional fast s0 1x | 160 | 6 | 15 | 11.47 | 0 | 81.656 / 130.4 | None / None | 16 / 0 | 0.7028 / 0.0 | - | False |
| conventional pkgfn3 64x | 730 | 1,882 | 5,582 | 10.28 | 71 | 213.525 / 213.525 | 251.033 / 251.033 | 29 / 2 | 0.7726 / 0.682 | - | False |
| pre conventional pkgfn3 s0 1x | 160 | 20 | 46 | 12.17 | 16 | None / None | None / None | 1 / 0 | 0.0 / 0.0 | - | False |
| vertical fast 64x | 730 | 1,299 | 4,502 | 12.25 | 0 | 56.65 / None | 330.133 / 379.441 | 348 / 253 | 0.63 / 0.7346 | edm, instron | False |
| pre vertical fast s0 1x | 160 | 7 | 20 | 11.91 | 0 | 56.65 / None | None / None | 16 / 0 | 0.4245 / 0.0 | edm, instron | False |

**Not finished** (the cost so far, from the progress file, and the two years extrapolated: `low` at the latest 50 days' rate, `high` with that rate still rising at its slope over the last 100 days):

| Run | Last day reached | CPU s so far | Wall s so far | CPU s a simulated day, last 50 days | Its rise a day | Two years, low | Two years, high |
|---|---|---|---|---|---|---|---|
| pilot vertical bofn3 s0 16x | 250 | 357 | 1,519 | 4.0 | 0.062 | 2,254 | 9,410 |
| pilot vertical bofn3 s0 64x | 230 | 564 | 2,750 | 3.7 | 0.027 | 2,407 | 5,833 |
| pilot vertical bofn3 s1 16x | 210 | 325 | 1,387 | 4.4 | 0.057 | 2,602 | 10,278 |
| pilot vertical bofn3 s1 64x | 200 | 512 | 2,400 | 4.4 | 0.037 | 2,840 | 8,050 |
| vertical bofn3 16x | 420 | 3,590 | 6,730 | 32.3 | 0.187 | 13,609 | 22,596 |
| vertical bofn3 64x | 410 | 3,622 | 6,778 | 27.4 | 0.176 | 12,384 | 21,391 |
| vertical pkgfn3 16x | 420 | 3,807 | 7,092 | 36.1 | 0.260 | 14,999 | 27,477 |
| vertical pkgfn3 64x | 410 | 3,565 | 6,689 | 26.5 | 0.136 | 12,037 | 19,000 |

* **vertical bofn3 64x lean**: stopped at day 10 at 21:39 UTC: the automated lab's GP runs proved to take several CPU-hours each, so the CPU went to the runs asked for.
* **vertical bofn3 64x wait**: stopped at day 20 at 21:39 UTC, for the same reason.

CPU seconds by simulated day (every 100 days), all runs:

| Run | day 100 | day 200 | day 300 | day 400 | day 500 | day 600 | day 700 |
|---|---|---|---|---|---|---|---|
| conventional bofn3 64x | 171 | 405 | 660 | 904 | 1,167 | 1,418 | 1,680 |
| conventional fast 64x | 160 | 327 | 492 | 655 | 817 | 976 | 1,136 |
| conventional pkgfn3 64x | 172 | 418 | 683 | 946 | 1,224 | 1,523 | 1,794 |
| pilot vertical bofn3 s0 16x | 56 | 159 |  |  |  |  |  |
| pilot vertical bofn3 s0 64x | 184 | 441 |  |  |  |  |  |
| pilot vertical bofn3 s1 16x | 50 | 287 |  |  |  |  |  |
| pilot vertical bofn3 s1 64x | 175 | 512 |  |  |  |  |  |
| pre conventional bofn3 s0 1x | 7 |  |  |  |  |  |  |
| pre conventional fast s0 1x | 5 |  |  |  |  |  |  |
| pre conventional pkgfn3 s0 1x | 8 |  |  |  |  |  |  |
| pre vertical fast s0 1x | 6 |  |  |  |  |  |  |
| vertical bofn3 16x | 49 | 141 | 644 | 2,946 |  |  |  |
| vertical bofn3 64x | 170 | 421 | 1,195 | 3,295 |  |  |  |
| vertical bofn3 64x lean |  |  |  |  |  |  |  |
| vertical bofn3 64x wait |  |  |  |  |  |  |  |
| vertical fast 64x | 160 | 328 | 503 | 686 | 869 | 1,050 | 1,242 |
| vertical pkgfn3 16x | 49 | 142 | 670 | 2,993 |  |  |  |
| vertical pkgfn3 64x | 170 | 414 | 1,085 | 3,315 |  |  |  |
