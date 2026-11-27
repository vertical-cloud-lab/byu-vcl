# Round 6: timing runs and BOFN's scale pilot

Made by `python out/twin6/checks/timing6.py table` from `timing6.jsonl` and `timing6_progress.jsonl`. Seed s of the stocked arm of each lab (the automated lab's parallel plan), at the scale named. **CPU seconds** are the run's own process time, what it costs a slice that runs one run per vCPU; wall seconds stretch when this runner ran more than four things at once (the load average at the end says how busy it was). Everything is simulated.

| Run | Days | CPU s | Wall s | Load at end | GP fits | Al T1 / T2 day | Cu T1 / T2 day | Al / Cu tested | Al / Cu best new | Bought used | twin/ dirty |
|---|---|---|---|---|---|---|---|---|---|---|---|

**Not finished** (the cost so far, from the progress file, and the two years extrapolated: `low` at the latest 50 days' rate, `high` with that rate still rising at its slope over the last 100 days):

| Run | Last day reached | CPU s so far | Wall s so far | CPU s a simulated day, last 50 days | Its rise a day | Two years, low | Two years, high |
|---|---|---|---|---|---|---|---|
| conventional bofn3 64x | 290 | 638 | 2,914 | 2.4 | 0.000 | 1,708 | 1,708 |
| conventional fast 64x | 400 | 655 | 2,947 | 1.6 | 0.000 | 1,196 | 1,212 |
| conventional pkgfn3 64x | 290 | 657 | 2,966 | 2.6 | 0.000 | 1,818 | 1,818 |
| vertical bofn3 16x | 350 | 1,532 | 2,872 | 17.8 | 0.221 | 8,281 | 24,262 |
| vertical bofn3 64x | 320 | 1,499 | 2,813 | 14.0 | 0.142 | 7,231 | 19,132 |
| vertical fast 64x | 380 | 648 | 2,944 | 1.9 | 0.001 | 1,311 | 1,385 |
| vertical pkgfn3 16x | 340 | 1,351 | 2,508 | 15.7 | 0.192 | 7,455 | 22,046 |
| vertical pkgfn3 64x | 320 | 1,415 | 2,569 | 12.3 | 0.141 | 6,456 | 18,321 |

* **vertical bofn3 64x lean**: stopped at day 10 at 21:39 UTC: the automated lab's GP runs proved to take several CPU-hours each, so the CPU went to the runs asked for.
* **vertical bofn3 64x wait**: stopped at day 20 at 21:39 UTC, for the same reason.

CPU seconds by simulated day (every 100 days), all runs:

| Run | day 100 | day 200 | day 300 | day 400 | day 500 | day 600 | day 700 |
|---|---|---|---|---|---|---|---|
| conventional bofn3 64x | 171 | 405 |  |  |  |  |  |
| conventional fast 64x | 160 | 327 | 492 | 655 |  |  |  |
| conventional pkgfn3 64x | 172 | 418 |  |  |  |  |  |
| vertical bofn3 16x | 49 | 141 | 644 |  |  |  |  |
| vertical bofn3 64x | 170 | 421 | 1,195 |  |  |  |  |
| vertical bofn3 64x lean |  |  |  |  |  |  |  |
| vertical bofn3 64x wait |  |  |  |  |  |  |  |
| vertical fast 64x | 160 | 328 | 503 |  |  |  |  |
| vertical pkgfn3 16x | 49 | 142 | 670 |  |  |  |  |
| vertical pkgfn3 64x | 170 | 414 | 1,085 |  |  |  |  |
