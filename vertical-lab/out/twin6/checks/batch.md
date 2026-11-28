# Round 6: batched GP predictions, what they save, and this runner's speed

Made by `python out/twin6/checks/batch_merge.py` from `timing6b_ab.jsonl`, `timing6b_progress.jsonl`, `timing6b_calib.jsonl` and round 6's timing runs (`timing6_progress.jsonl`). Everything is simulated.

**The saving on identical work** (the same saved state carried on with 64-point GP calls and without, side by side on this runner):

| Policy | From day | Days | CPU s, 64-point calls | CPU s, one call | Ratio | Load at the arms' ends |
|---|---|---|---|---|---|---|
| bofn3 | 300 | 10 | 158 | 231 | 0.684 | 14.35 / 9.84 |
| bofn3 | 300 | 10 | 153 | 203 | 0.757 | 5.67 / 4.03 |
| bofn3 | 350 | 10 | 226 | 294 | 0.767 | 11.72 / 9.83 |
| bofn3 | 400 | 10 | 348 | 405 | 0.860 | 2.84 / 1.77 |
| pkgfn3 | 300 | 10 | 181 | 303 | 0.596 | 13.86 / 8.76 |
| pkgfn3 | 300 | 10 | 171 | 249 | 0.686 | 5.3 / 2.62 |
| pkgfn3 | 350 | 10 | 276 | 365 | 0.756 | 10.74 / 7.71 |
| pkgfn3 | 400 | 10 | 360 | 418 | 0.861 | 6.19 / 4.5 |

**The grid's seconds** (`smoke.json`, two-year CPU seconds on the 9V45, which `status` and `plan` read): `new = pre + (old - pre) x 0.92 x r`: `old` the extrapolation of round 6's timing run on the engine it used (568ab5f), `pre` its CPU seconds at day 200, 0.92 the faster trial settings (74254fe, notes section 10), `r` the batching's ratio for the policy at the latest day measured (the larger, if measured twice): the saving shrinks as a run goes on, and most of a run's cost comes after day 400.

| Group | r | The timing runs' engine (568ab5f), low-high | Batched, low-high |
|---|---|---|---|
| `r6_vertical_parallel_bofn3_reorder` | 0.860 | 17,230-20,726 | 13,727-16,494 |
| `r6_vertical_parallel_pkgfn3_reorder` | 0.861 | 22,539-40,131 | 17,934-31,864 |
| `r6_vertical_parallel_bofn3_reorder_hpc16` | 0.860 | 17,370-18,195 | 13,779-14,432 |
| `r6_vertical_parallel_pkgfn3_reorder_hpc16` | 0.861 | 19,126-25,391 | 15,174-20,135 |

**This runner's speed against the 9V45** (CPU seconds here over CPU seconds there for the same code and simulated days, every vCPU busy on both; above 1 is slower):

| Runs | day 50 | day 100 | day 150 | day 200 | day 250 | day 300 | day 350 | day 400 | day 450 | day 500 | day 550 | day 600 | day 650 | day 700 | day 750 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| vertical bofn3 64x unbatched | 2.26 | 2.15 | 2.09 | 1.99 | 1.86 | 1.75 | 1.74 |  |  |  |  |  |  |  |  |
| vertical pkgfn3 64x unbatched | 2.25 | 2.15 | 2.09 | 2.00 | 1.90 | 1.80 | 1.75 |  |  |  |  |  |  |  |  |
| vertical fast 64x calib | 2.19 | 2.16 | 2.10 | 2.09 |  |  |  |  |  |  |  |  |  |  |  |

Median from day 100 on: **2.00**.
