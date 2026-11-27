# Round 6: runs done and left

Made by `python -m twin.bench6 status`. An arm is reported from 12 seeds; the grid has 16 for every arm. Seconds are a two-year run's CPU seconds on the runner that built the grid (its CPU is in `checks/smoke.json`), with every vCPU busy, as in a slice; how each was found is in the last column (twin/bench6.py `timings`). Core-hours are for the runs left; a runner runs four at a time.

| Tier | Experiment | Arm | Seeds done | Seeds left | s per run | Core-hours left | How |
|---|---|---|---|---|---|---|---|
| 1 | arms | `r6_vertical_parallel_fast_reorder` | 0 | 16 | 1,299 | 5.8 | measured (two years, seed 0) |
| 1 | arms | `r6_vertical_parallel_fast_lean` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 1 | arms | `r6_conventional_external_fast_reorder` | 0 | 16 | 1,187 | 5.3 | measured (two years, seed 0) |
| 1 | arms | `r6_conventional_external_fast_lean` | 0 | 16 | 1,187 | 5.3 | its arms group's two years at 64x |
| 1 | arms | `r6_vertical_parallel_bofn3_reorder` | 0 | 16 | 18,829 | 83.7 | extrapolated from day 390 of a two-year run (seed 0): the cautious end, 10,543-18,829 s |
| 1 | arms | `r6_vertical_parallel_bofn3_lean` | 0 | 16 | 18,829 | 83.7 | its arms group's two years at 64x |
| 1 | arms | `r6_conventional_external_bofn3_reorder` | 0 | 16 | 1,755 | 7.8 | measured (two years, seed 0) |
| 1 | arms | `r6_conventional_external_bofn3_lean` | 0 | 16 | 1,755 | 7.8 | its arms group's two years at 64x |
| 1 | arms | `r6_vertical_parallel_pkgfn3_reorder` | 0 | 16 | 19,380 | 86.1 | extrapolated from day 390 of a two-year run (seed 0): the cautious end, 11,049-19,380 s |
| 1 | arms | `r6_vertical_parallel_pkgfn3_lean` | 0 | 16 | 19,380 | 86.1 | its arms group's two years at 64x |
| 1 | arms | `r6_conventional_external_pkgfn3_reorder` | 0 | 16 | 1,882 | 8.4 | measured (two years, seed 0) |
| 1 | arms | `r6_conventional_external_pkgfn3_lean` | 0 | 16 | 1,882 | 8.4 | its arms group's two years at 64x |
| 2 | hpc | `r6_vertical_parallel_fast_reorder_hpc1` | 0 | 16 | 146 | 0.6 | its arms group's two years at 64x, the stream's cost moved to 1x (0.0251 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_fast_reorder_hpc1` | 0 | 16 | 32 | 0.1 | its arms group's two years at 64x, the stream's cost moved to 1x (0.0251 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_bofn3_reorder_hpc1` | 0 | 16 | 24,710 | 109.8 | its arms group's two years at 16x, the stream's cost moved to 1x (0.0268 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_bofn3_reorder_hpc1` | 0 | 16 | 478 | 2.1 | its arms group's two years at 64x, the stream's cost moved to 1x (0.0278 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_pkgfn3_reorder_hpc1` | 0 | 16 | 25,054 | 111.3 | its arms group's two years at 16x, the stream's cost moved to 1x (0.0268 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_pkgfn3_reorder_hpc1` | 0 | 16 | 605 | 2.7 | its arms group's two years at 64x, the stream's cost moved to 1x (0.0278 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_fast_reorder_hpc4` | 0 | 16 | 201 | 0.9 | its arms group's two years at 64x, the stream's cost moved to 4x (0.0251 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_fast_reorder_hpc4` | 0 | 16 | 87 | 0.4 | its arms group's two years at 64x, the stream's cost moved to 4x (0.0251 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_bofn3_reorder_hpc4` | 0 | 16 | 24,768 | 110.1 | its arms group's two years at 16x, the stream's cost moved to 4x (0.0268 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_bofn3_reorder_hpc4` | 0 | 16 | 539 | 2.4 | its arms group's two years at 64x, the stream's cost moved to 4x (0.0278 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_pkgfn3_reorder_hpc4` | 0 | 16 | 25,112 | 111.6 | its arms group's two years at 16x, the stream's cost moved to 4x (0.0268 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_pkgfn3_reorder_hpc4` | 0 | 16 | 666 | 3.0 | its arms group's two years at 64x, the stream's cost moved to 4x (0.0278 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_fast_reorder_hpc16` | 0 | 16 | 421 | 1.9 | its arms group's two years at 64x, the stream's cost moved to 16x (0.0251 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_fast_reorder_hpc16` | 0 | 16 | 307 | 1.4 | its arms group's two years at 64x, the stream's cost moved to 16x (0.0251 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_bofn3_reorder_hpc16` | 0 | 16 | 25,003 | 111.1 | extrapolated from day 400 of a two-year run (seed 0): the cautious end, 12,277-25,003 s |
| 2 | hpc | `r6_conventional_external_bofn3_reorder_hpc16` | 0 | 16 | 782 | 3.5 | its arms group's two years at 64x, the stream's cost moved to 16x (0.0278 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_pkgfn3_reorder_hpc16` | 0 | 16 | 25,347 | 112.7 | extrapolated from day 400 of a two-year run (seed 0): the cautious end, 12,289-25,347 s |
| 2 | hpc | `r6_conventional_external_pkgfn3_reorder_hpc16` | 0 | 16 | 909 | 4.0 | its arms group's two years at 64x, the stream's cost moved to 16x (0.0278 s a day per unit of scale) |
| 2 | plans | `r6_vertical_wait_fast_reorder` | 0 | 16 | 1,320 | 5.9 | its arms group's two years at 64x, its work x round 5's wait ratio (1.17) |
| 2 | plans | `r6_vertical_external_fast_reorder` | 0 | 16 | 1,275 | 5.7 | its arms group's two years at 64x, its work x round 5's external ratio (0.81) |
| 2 | plans | `r6_vertical_wait_bofn3_reorder` | 0 | 16 | 8,402 | 37.3 | its arms group's two years at 64x, its work x round 5's wait ratio (0.41) |
| 2 | plans | `r6_vertical_external_bofn3_reorder` | 0 | 16 | 11,370 | 50.5 | its arms group's two years at 64x, its work x round 5's external ratio (0.58) |
| 2 | plans | `r6_vertical_wait_pkgfn3_reorder` | 0 | 16 | 8,626 | 38.3 | its arms group's two years at 64x, its work x round 5's wait ratio (0.41) |
| 2 | plans | `r6_vertical_external_pkgfn3_reorder` | 0 | 16 | 11,687 | 51.9 | its arms group's two years at 64x, its work x round 5's external ratio (0.58) |
| 3 | crucibles_late | `r6_vertical_parallel_fast_reorder_late240` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 3 | crucibles_late | `r6_vertical_parallel_fast_lean_late240` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 3 | crucibles_late | `r6_vertical_parallel_bofn3_reorder_late240` | 0 | 16 | 18,829 | 83.7 | its arms group's two years at 64x |
| 3 | crucibles_late | `r6_vertical_parallel_bofn3_lean_late240` | 0 | 16 | 18,829 | 83.7 | its arms group's two years at 64x |
| 3 | crucibles_late | `r6_vertical_parallel_pkgfn3_reorder_late240` | 0 | 16 | 19,380 | 86.1 | its arms group's two years at 64x |
| 3 | crucibles_late | `r6_vertical_parallel_pkgfn3_lean_late240` | 0 | 16 | 19,380 | 86.1 | its arms group's two years at 64x |
| 3 | noused | `r6_vertical_parallel_fast_reorder_noused` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 3 | noused | `r6_vertical_parallel_bofn3_reorder_noused` | 0 | 16 | 18,829 | 83.7 | its arms group's two years at 64x |
| 3 | noused | `r6_vertical_parallel_pkgfn3_reorder_noused` | 0 | 16 | 19,380 | 86.1 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_fast_reorder_atom-3h` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_fast_lean_atom-3h` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_bofn3_reorder_atom-3h` | 0 | 16 | 18,829 | 83.7 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_bofn3_lean_atom-3h` | 0 | 16 | 18,829 | 83.7 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_pkgfn3_reorder_atom-3h` | 0 | 16 | 19,380 | 86.1 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_pkgfn3_lean_atom-3h` | 0 | 16 | 19,380 | 86.1 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_fast_reorder_atom-slow` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_fast_lean_atom-slow` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_bofn3_reorder_atom-slow` | 0 | 16 | 18,829 | 83.7 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_bofn3_lean_atom-slow` | 0 | 16 | 18,829 | 83.7 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_pkgfn3_reorder_atom-slow` | 0 | 16 | 19,380 | 86.1 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_pkgfn3_lean_atom-slow` | 0 | 16 | 19,380 | 86.1 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_fast_reorder_dec-none` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_fast_lean_dec-none` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_fast_reorder_dec-none` | 0 | 16 | 1,187 | 5.3 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_fast_lean_dec-none` | 0 | 16 | 1,187 | 5.3 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_bofn3_reorder_dec-none` | 0 | 16 | 18,829 | 83.7 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_bofn3_lean_dec-none` | 0 | 16 | 18,829 | 83.7 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_bofn3_reorder_dec-none` | 0 | 16 | 1,755 | 7.8 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_bofn3_lean_dec-none` | 0 | 16 | 1,755 | 7.8 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_pkgfn3_reorder_dec-none` | 0 | 16 | 19,380 | 86.1 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_pkgfn3_lean_dec-none` | 0 | 16 | 19,380 | 86.1 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_pkgfn3_reorder_dec-none` | 0 | 16 | 1,882 | 8.4 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_pkgfn3_lean_dec-none` | 0 | 16 | 1,882 | 8.4 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_fast_reorder_dec-slow` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_fast_lean_dec-slow` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_fast_reorder_dec-slow` | 0 | 16 | 1,187 | 5.3 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_fast_lean_dec-slow` | 0 | 16 | 1,187 | 5.3 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_bofn3_reorder_dec-slow` | 0 | 16 | 18,829 | 83.7 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_bofn3_lean_dec-slow` | 0 | 16 | 18,829 | 83.7 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_bofn3_reorder_dec-slow` | 0 | 16 | 1,755 | 7.8 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_bofn3_lean_dec-slow` | 0 | 16 | 1,755 | 7.8 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_pkgfn3_reorder_dec-slow` | 0 | 16 | 19,380 | 86.1 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_pkgfn3_lean_dec-slow` | 0 | 16 | 19,380 | 86.1 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_pkgfn3_reorder_dec-slow` | 0 | 16 | 1,882 | 8.4 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_pkgfn3_lean_dec-slow` | 0 | 16 | 1,882 | 8.4 | its arms group's two years at 64x |
| 5 | hpc256 | `r6_vertical_parallel_fast_reorder_hpc256` | 0 | 16 | 4,811 | 21.4 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0251 s a day per unit of scale) |
| 5 | hpc256 | `r6_conventional_external_fast_reorder_hpc256` | 0 | 16 | 4,707 | 20.9 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0251 s a day per unit of scale) |
| 5 | hpc256 | `r6_vertical_parallel_bofn3_reorder_hpc256` | 0 | 16 | 22,584 | 100.4 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0268 s a day per unit of scale) |
| 5 | hpc256 | `r6_conventional_external_bofn3_reorder_hpc256` | 0 | 16 | 5,646 | 25.1 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0278 s a day per unit of scale) |
| 5 | hpc256 | `r6_vertical_parallel_pkgfn3_reorder_hpc256` | 0 | 16 | 23,135 | 102.8 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0268 s a day per unit of scale) |
| 5 | hpc256 | `r6_conventional_external_pkgfn3_reorder_hpc256` | 0 | 16 | 5,772 | 25.7 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0278 s a day per unit of scale) |

Runs: 1392 in the grid, 1392 left.
Core-hours left by tier: tier 1: 394; tier 2: 879; tier 3: 527; tier 4: 1,490; tier 5: 296; all: 3,587, about 897 runner-hours at 4 runs a runner.
By experiment: atom: 702; hpc: 690; arms: 394; dec_none: 394; dec_slow: 394; crucibles_late: 351; hpc256: 296; plans: 190; noused: 176 core-hours.
