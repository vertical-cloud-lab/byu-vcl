# Round 6: runs done and left

Made by `python -m twin.bench6 status`. An arm is reported from 12 seeds; the grid has 16 for every arm. Seconds are a two-year run's CPU seconds on the runner that built the grid (its CPU is in `checks/smoke.json`), with every vCPU busy, as in a slice; how each was found is in the last column (twin/bench6.py `timings`). Core-hours are for the runs left; a runner runs four at a time.

| Tier | Experiment | Arm | Seeds done | Seeds left | s per run | Core-hours left | How |
|---|---|---|---|---|---|---|---|
| 1 | arms | `r6_vertical_parallel_fast_reorder` | 0 | 16 | 1,299 | 5.8 | measured (two years, seed 0) |
| 1 | arms | `r6_vertical_parallel_fast_lean` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 1 | arms | `r6_conventional_external_fast_reorder` | 0 | 16 | 1,187 | 5.3 | measured (two years, seed 0) |
| 1 | arms | `r6_conventional_external_fast_lean` | 0 | 16 | 1,187 | 5.3 | its arms group's two years at 64x |
| 1 | arms | `r6_vertical_parallel_bofn3_reorder` | 0 | 16 | 16,494 | 73.3 | extrapolated from day 500 of a two-year run (seed 0) on the timing runs' engine, x 0.92 (the faster trial settings) x 0.860 (64-point GP calls, measured) after day 200 (checks/batch.md): 13,727-16,494 s |
| 1 | arms | `r6_vertical_parallel_bofn3_lean` | 0 | 16 | 16,494 | 73.3 | its arms group's two years at 64x |
| 1 | arms | `r6_conventional_external_bofn3_reorder` | 0 | 16 | 1,755 | 7.8 | measured (two years, seed 0) |
| 1 | arms | `r6_conventional_external_bofn3_lean` | 0 | 16 | 1,755 | 7.8 | its arms group's two years at 64x |
| 1 | arms | `r6_vertical_parallel_pkgfn3_reorder` | 0 | 16 | 31,864 | 141.6 | extrapolated from day 480 of a two-year run (seed 0) on the timing runs' engine, x 0.92 (the faster trial settings) x 0.861 (64-point GP calls, measured) after day 200 (checks/batch.md): 17,934-31,864 s |
| 1 | arms | `r6_vertical_parallel_pkgfn3_lean` | 0 | 16 | 31,864 | 141.6 | its arms group's two years at 64x |
| 1 | arms | `r6_conventional_external_pkgfn3_reorder` | 0 | 16 | 1,882 | 8.4 | measured (two years, seed 0) |
| 1 | arms | `r6_conventional_external_pkgfn3_lean` | 0 | 16 | 1,882 | 8.4 | its arms group's two years at 64x |
| 2 | hpc | `r6_vertical_parallel_fast_reorder_hpc1` | 0 | 16 | 148 | 0.7 | its arms group's two years at 64x, the stream's cost moved to 1x (0.0250 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_fast_reorder_hpc1` | 0 | 16 | 36 | 0.2 | its arms group's two years at 64x, the stream's cost moved to 1x (0.0250 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_bofn3_reorder_hpc1` | 0 | 16 | 14,147 | 62.9 | its arms group's two years at 16x, the stream's cost moved to 1x (0.0260 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_bofn3_reorder_hpc1` | 0 | 16 | 476 | 2.1 | its arms group's two years at 64x, the stream's cost moved to 1x (0.0278 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_pkgfn3_reorder_hpc1` | 0 | 16 | 19,850 | 88.2 | its arms group's two years at 16x, the stream's cost moved to 1x (0.0260 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_pkgfn3_reorder_hpc1` | 0 | 16 | 603 | 2.7 | its arms group's two years at 64x, the stream's cost moved to 1x (0.0278 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_fast_reorder_hpc4` | 0 | 16 | 203 | 0.9 | its arms group's two years at 64x, the stream's cost moved to 4x (0.0250 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_fast_reorder_hpc4` | 0 | 16 | 91 | 0.4 | its arms group's two years at 64x, the stream's cost moved to 4x (0.0250 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_bofn3_reorder_hpc4` | 0 | 16 | 14,204 | 63.1 | its arms group's two years at 16x, the stream's cost moved to 4x (0.0260 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_bofn3_reorder_hpc4` | 0 | 16 | 537 | 2.4 | its arms group's two years at 64x, the stream's cost moved to 4x (0.0278 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_pkgfn3_reorder_hpc4` | 0 | 16 | 19,907 | 88.5 | its arms group's two years at 16x, the stream's cost moved to 4x (0.0260 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_pkgfn3_reorder_hpc4` | 0 | 16 | 664 | 3.0 | its arms group's two years at 64x, the stream's cost moved to 4x (0.0278 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_fast_reorder_hpc16` | 0 | 16 | 422 | 1.9 | its arms group's two years at 64x, the stream's cost moved to 16x (0.0250 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_fast_reorder_hpc16` | 0 | 16 | 310 | 1.4 | its arms group's two years at 64x, the stream's cost moved to 16x (0.0250 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_bofn3_reorder_hpc16` | 0 | 16 | 14,432 | 64.1 | extrapolated from day 510 of a two-year run (seed 0) on the timing runs' engine, x 0.92 (the faster trial settings) x 0.860 (64-point GP calls, measured) after day 200 (checks/batch.md): 13,779-14,432 s |
| 2 | hpc | `r6_conventional_external_bofn3_reorder_hpc16` | 0 | 16 | 781 | 3.5 | its arms group's two years at 64x, the stream's cost moved to 16x (0.0278 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_pkgfn3_reorder_hpc16` | 0 | 16 | 20,135 | 89.5 | extrapolated from day 500 of a two-year run (seed 0) on the timing runs' engine, x 0.92 (the faster trial settings) x 0.861 (64-point GP calls, measured) after day 200 (checks/batch.md): 15,174-20,135 s |
| 2 | hpc | `r6_conventional_external_pkgfn3_reorder_hpc16` | 0 | 16 | 908 | 4.0 | its arms group's two years at 64x, the stream's cost moved to 16x (0.0278 s a day per unit of scale) |
| 2 | plans | `r6_vertical_wait_fast_reorder` | 0 | 16 | 1,320 | 5.9 | its arms group's two years at 64x, its work x round 5's wait ratio (1.17) |
| 2 | plans | `r6_vertical_external_fast_reorder` | 0 | 16 | 1,274 | 5.7 | its arms group's two years at 64x, its work x round 5's external ratio (0.81) |
| 2 | plans | `r6_vertical_wait_bofn3_reorder` | 0 | 16 | 7,430 | 33.0 | its arms group's two years at 64x, its work x round 5's wait ratio (0.41) |
| 2 | plans | `r6_vertical_external_bofn3_reorder` | 0 | 16 | 10,010 | 44.5 | its arms group's two years at 64x, its work x round 5's external ratio (0.58) |
| 2 | plans | `r6_vertical_wait_pkgfn3_reorder` | 0 | 16 | 13,682 | 60.8 | its arms group's two years at 64x, its work x round 5's wait ratio (0.41) |
| 2 | plans | `r6_vertical_external_pkgfn3_reorder` | 0 | 16 | 18,858 | 83.8 | its arms group's two years at 64x, its work x round 5's external ratio (0.58) |
| 3 | crucibles_late | `r6_vertical_parallel_fast_reorder_late240` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 3 | crucibles_late | `r6_vertical_parallel_fast_lean_late240` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 3 | crucibles_late | `r6_vertical_parallel_bofn3_reorder_late240` | 0 | 16 | 16,494 | 73.3 | its arms group's two years at 64x |
| 3 | crucibles_late | `r6_vertical_parallel_bofn3_lean_late240` | 0 | 16 | 16,494 | 73.3 | its arms group's two years at 64x |
| 3 | crucibles_late | `r6_vertical_parallel_pkgfn3_reorder_late240` | 0 | 16 | 31,864 | 141.6 | its arms group's two years at 64x |
| 3 | crucibles_late | `r6_vertical_parallel_pkgfn3_lean_late240` | 0 | 16 | 31,864 | 141.6 | its arms group's two years at 64x |
| 3 | noused | `r6_vertical_parallel_fast_reorder_noused` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 3 | noused | `r6_vertical_parallel_bofn3_reorder_noused` | 0 | 16 | 16,494 | 73.3 | its arms group's two years at 64x |
| 3 | noused | `r6_vertical_parallel_pkgfn3_reorder_noused` | 0 | 16 | 31,864 | 141.6 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_fast_reorder_atom-3h` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_fast_lean_atom-3h` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_bofn3_reorder_atom-3h` | 0 | 16 | 16,494 | 73.3 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_bofn3_lean_atom-3h` | 0 | 16 | 16,494 | 73.3 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_pkgfn3_reorder_atom-3h` | 0 | 16 | 31,864 | 141.6 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_pkgfn3_lean_atom-3h` | 0 | 16 | 31,864 | 141.6 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_fast_reorder_atom-slow` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_fast_lean_atom-slow` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_bofn3_reorder_atom-slow` | 0 | 16 | 16,494 | 73.3 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_bofn3_lean_atom-slow` | 0 | 16 | 16,494 | 73.3 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_pkgfn3_reorder_atom-slow` | 0 | 16 | 31,864 | 141.6 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_pkgfn3_lean_atom-slow` | 0 | 16 | 31,864 | 141.6 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_fast_reorder_dec-none` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_fast_lean_dec-none` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_fast_reorder_dec-none` | 0 | 16 | 1,187 | 5.3 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_fast_lean_dec-none` | 0 | 16 | 1,187 | 5.3 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_bofn3_reorder_dec-none` | 0 | 16 | 16,494 | 73.3 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_bofn3_lean_dec-none` | 0 | 16 | 16,494 | 73.3 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_bofn3_reorder_dec-none` | 0 | 16 | 1,755 | 7.8 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_bofn3_lean_dec-none` | 0 | 16 | 1,755 | 7.8 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_pkgfn3_reorder_dec-none` | 0 | 16 | 31,864 | 141.6 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_pkgfn3_lean_dec-none` | 0 | 16 | 31,864 | 141.6 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_pkgfn3_reorder_dec-none` | 0 | 16 | 1,882 | 8.4 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_pkgfn3_lean_dec-none` | 0 | 16 | 1,882 | 8.4 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_fast_reorder_dec-slow` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_fast_lean_dec-slow` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_fast_reorder_dec-slow` | 0 | 16 | 1,187 | 5.3 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_fast_lean_dec-slow` | 0 | 16 | 1,187 | 5.3 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_bofn3_reorder_dec-slow` | 0 | 16 | 16,494 | 73.3 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_bofn3_lean_dec-slow` | 0 | 16 | 16,494 | 73.3 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_bofn3_reorder_dec-slow` | 0 | 16 | 1,755 | 7.8 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_bofn3_lean_dec-slow` | 0 | 16 | 1,755 | 7.8 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_pkgfn3_reorder_dec-slow` | 0 | 16 | 31,864 | 141.6 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_pkgfn3_lean_dec-slow` | 0 | 16 | 31,864 | 141.6 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_pkgfn3_reorder_dec-slow` | 0 | 16 | 1,882 | 8.4 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_pkgfn3_lean_dec-slow` | 0 | 16 | 1,882 | 8.4 | its arms group's two years at 64x |
| 5 | hpc256 | `r6_vertical_parallel_fast_reorder_hpc256` | 0 | 16 | 4,804 | 21.4 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0250 s a day per unit of scale) |
| 5 | hpc256 | `r6_conventional_external_fast_reorder_hpc256` | 0 | 16 | 4,694 | 20.9 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0250 s a day per unit of scale) |
| 5 | hpc256 | `r6_vertical_parallel_bofn3_reorder_hpc256` | 0 | 16 | 20,140 | 89.5 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0260 s a day per unit of scale) |
| 5 | hpc256 | `r6_conventional_external_bofn3_reorder_hpc256` | 0 | 16 | 5,651 | 25.1 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0278 s a day per unit of scale) |
| 5 | hpc256 | `r6_vertical_parallel_pkgfn3_reorder_hpc256` | 0 | 16 | 35,510 | 157.8 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0260 s a day per unit of scale) |
| 5 | hpc256 | `r6_conventional_external_pkgfn3_reorder_hpc256` | 0 | 16 | 5,778 | 25.7 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0278 s a day per unit of scale) |

Runs: 1392 in the grid, 1392 left.
Core-hours left by tier: tier 1: 484; tier 2: 713; tier 3: 662; tier 4: 1,851; tier 5: 340; all: 4,051, about 1,013 runner-hours at 4 runs a runner.
By experiment: atom: 883; arms: 484; dec_none: 484; dec_slow: 484; hpc: 479; crucibles_late: 441; hpc256: 340; plans: 234; noused: 221 core-hours.
