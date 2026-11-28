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
| pilot conventional bofn3 s0 1x | 300 | 76 | 238 | 11.15 | 37 | None / None | 209.171 / 209.171 | 5 / 2 | 0.0 / 0.6937 | - | False |
| pilot conventional fast s0 1x | 300 | 15 | 72 | 10.54 | 0 | 81.656 / 130.4 | None / None | 35 / 2 | 0.7028 / 0.354 | - | False |
| pilot vertical bofn3 s0 64x | 300 | 1,054 | 4,847 | 11.33 | 72 | 245.454 / 245.454 | None / None | 33 / 1 | 0.7687 / 0.3926 | edm, instron | False |
| pilot vertical bofn3 s1 64x | 300 | 1,685 | 7,252 | 11.41 | 141 | 179.728 / 185.053 | 289.282 / 289.282 | 20 / 5 | 0.7922 / 0.669 | edm, instron | False |
| pilot vertical bofn3 s0 16x | 300 | 742 | 3,174 | 9.67 | 78 | 245.4 / 245.4 | None / None | 43 / 2 | 0.807 / 0.4117 | edm, instron | False |
| pilot vertical bofn3 s1 16x | 300 | 1,747 | 7,126 | 7.49 | 152 | 182.525 / 182.525 | 239.414 / None | 62 / 2 | 0.8085 / 0.603 | edm, instron | False |
| pilot vertical bofn3 s0 4x | 300 | 607 | 2,691 | 8.49 | 79 | 231.4 / 245.688 | None / None | 41 / 1 | 0.7431 / 0.0 | edm, instron | False |
| pilot vertical bofn3 s0 1x | 300 | 544 | 2,250 | 6.5 | 63 | 151.65 / 185.65 | None / None | 18 / 2 | 0.7493 / 0.3948 | edm, instron | False |
| pilot vertical fast s0 1x | 300 | 25 | 120 | 11.74 | 0 | 56.65 / None | None / None | 110 / 2 | 0.5453 / 0.4134 | edm, instron | False |

**Not finished** (the cost so far, from the progress file, and the two years extrapolated: `low` at the latest 50 days' rate, `high` with that rate still rising at its slope over the last 100 days):

| Run | Last day reached | CPU s so far | Wall s so far | CPU s a simulated day, last 50 days | Its rise a day | Two years, low | Two years, high |
|---|---|---|---|---|---|---|---|
| vertical bofn3 16x | 510 | 7,691 | 13,592 | 44.0 | 0.034 | 17,370 | 18,195 |
| vertical bofn3 64x | 500 | 7,343 | 13,163 | 43.0 | 0.132 | 17,230 | 20,726 |
| vertical pkgfn3 16x | 500 | 7,487 | 13,432 | 50.6 | 0.237 | 19,126 | 25,391 |
| vertical pkgfn3 64x | 480 | 7,356 | 13,274 | 60.7 | 0.563 | 22,539 | 40,131 |

* **vertical bofn3 64x lean**: stopped at day 10 at 21:39 UTC: the automated lab's GP runs proved to take several CPU-hours each, so the CPU went to the runs asked for.
* **vertical bofn3 64x wait**: stopped at day 20 at 21:39 UTC, for the same reason.
* **vertical bofn3 64x**: stopped at day 500 at 00:48 UTC on 2026-11-28, when the job that timed it had to finish; its two years are extrapolated from its cost curve.
* **vertical pkgfn3 64x**: stopped at day 480 at 00:48 UTC on 2026-11-28, when the job that timed it had to finish; its two years are extrapolated from its cost curve.
* **vertical bofn3 16x**: stopped at day 510 at 00:48 UTC on 2026-11-28, when the job that timed it had to finish; its two years are extrapolated from its cost curve.
* **vertical pkgfn3 16x**: stopped at day 500 at 00:48 UTC on 2026-11-28, when the job that timed it had to finish; its two years are extrapolated from its cost curve.
* **pilot vertical bofn3 s1 1x**: stopped at day 250 at 00:48 UTC on 2026-11-28, when the job that timed it had to finish; the pilot's other runs finished.

CPU seconds by simulated day (every 100 days), all runs:

| Run | day 100 | day 200 | day 300 | day 400 | day 500 | day 600 | day 700 |
|---|---|---|---|---|---|---|---|
| conventional bofn3 64x | 171 | 405 | 660 | 904 | 1,167 | 1,418 | 1,680 |
| conventional fast 64x | 160 | 327 | 492 | 655 | 817 | 976 | 1,136 |
| conventional pkgfn3 64x | 172 | 418 | 683 | 946 | 1,224 | 1,523 | 1,794 |
| pilot conventional bofn3 s0 1x | 7 | 32 | 77 |  |  |  |  |
| pilot conventional fast s0 1x | 6 | 11 | 16 |  |  |  |  |
| pilot vertical bofn3 s0 16x | 56 | 159 | 743 |  |  |  |  |
| pilot vertical bofn3 s0 1x | 19 | 110 | 546 |  |  |  |  |
| pilot vertical bofn3 s0 4x | 24 | 104 | 608 |  |  |  |  |
| pilot vertical bofn3 s0 64x | 184 | 441 | 1,055 |  |  |  |  |
| pilot vertical bofn3 s1 16x | 50 | 287 | 1,747 |  |  |  |  |
| pilot vertical bofn3 s1 1x | 11 | 205 |  |  |  |  |  |
| pilot vertical bofn3 s1 64x | 175 | 512 | 1,686 |  |  |  |  |
| pilot vertical fast s0 1x | 6 | 12 | 26 |  |  |  |  |
| pre conventional bofn3 s0 1x | 7 |  |  |  |  |  |  |
| pre conventional fast s0 1x | 5 |  |  |  |  |  |  |
| pre conventional pkgfn3 s0 1x | 8 |  |  |  |  |  |  |
| pre vertical fast s0 1x | 6 |  |  |  |  |  |  |
| vertical bofn3 16x | 49 | 141 | 644 | 2,946 | 7,244 |  |  |
| vertical bofn3 64x | 170 | 421 | 1,195 | 3,295 | 7,343 |  |  |
| vertical bofn3 64x lean |  |  |  |  |  |  |  |
| vertical bofn3 64x wait |  |  |  |  |  |  |  |
| vertical fast 64x | 160 | 328 | 503 | 686 | 869 | 1,050 | 1,242 |
| vertical pkgfn3 16x | 49 | 142 | 670 | 2,993 | 7,487 |  |  |
| vertical pkgfn3 64x | 170 | 414 | 1,085 | 3,315 |  |  |  |
