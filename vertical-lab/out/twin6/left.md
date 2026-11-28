# Round 6: runs done and left

Made by `python -m twin.bench6 status`. An arm is reported from 12 seeds; the grid has 16 for every arm. Seconds are a two-year run's CPU seconds on the runner that built the grid (its CPU is in `checks/smoke.json`), with every vCPU busy, as in a slice; how each was found is in the last column (twin/bench6.py `timings`). Core-hours are for the runs left; a runner runs four at a time.

| Tier | Experiment | Arm | Seeds done | Seeds left | s per run | Core-hours left | How |
|---|---|---|---|---|---|---|---|
| 1 | arms | `r6_vertical_parallel_fast_reorder` | 0 | 16 | 1,299 | 5.8 | measured (two years, seed 0) |
| 1 | arms | `r6_vertical_parallel_fast_lean` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 1 | arms | `r6_conventional_external_fast_reorder` | 0 | 16 | 1,187 | 5.3 | measured (two years, seed 0) |
| 1 | arms | `r6_conventional_external_fast_lean` | 0 | 16 | 1,187 | 5.3 | its arms group's two years at 64x |
| 1 | arms | `r6_vertical_parallel_bofn3_reorder` | 0 | 16 | 20,726 | 92.1 | extrapolated from day 500 of a two-year run (seed 0): the cautious end, 17,230-20,726 s |
| 1 | arms | `r6_vertical_parallel_bofn3_lean` | 0 | 16 | 20,726 | 92.1 | its arms group's two years at 64x |
| 1 | arms | `r6_conventional_external_bofn3_reorder` | 0 | 16 | 1,755 | 7.8 | measured (two years, seed 0) |
| 1 | arms | `r6_conventional_external_bofn3_lean` | 0 | 16 | 1,755 | 7.8 | its arms group's two years at 64x |
| 1 | arms | `r6_vertical_parallel_pkgfn3_reorder` | 0 | 16 | 40,131 | 178.4 | extrapolated from day 480 of a two-year run (seed 0): the cautious end, 22,539-40,131 s |
| 1 | arms | `r6_vertical_parallel_pkgfn3_lean` | 0 | 16 | 40,131 | 178.4 | its arms group's two years at 64x |
| 1 | arms | `r6_conventional_external_pkgfn3_reorder` | 0 | 16 | 1,882 | 8.4 | measured (two years, seed 0) |
| 1 | arms | `r6_conventional_external_pkgfn3_lean` | 0 | 16 | 1,882 | 8.4 | its arms group's two years at 64x |
| 2 | hpc | `r6_vertical_parallel_fast_reorder_hpc1` | 0 | 16 | 148 | 0.7 | its arms group's two years at 64x, the stream's cost moved to 1x (0.0250 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_fast_reorder_hpc1` | 0 | 16 | 36 | 0.2 | its arms group's two years at 64x, the stream's cost moved to 1x (0.0250 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_bofn3_reorder_hpc1` | 0 | 16 | 17,910 | 79.6 | its arms group's two years at 16x, the stream's cost moved to 1x (0.0260 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_bofn3_reorder_hpc1` | 0 | 16 | 476 | 2.1 | its arms group's two years at 64x, the stream's cost moved to 1x (0.0278 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_pkgfn3_reorder_hpc1` | 0 | 16 | 25,106 | 111.6 | its arms group's two years at 16x, the stream's cost moved to 1x (0.0260 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_pkgfn3_reorder_hpc1` | 0 | 16 | 603 | 2.7 | its arms group's two years at 64x, the stream's cost moved to 1x (0.0278 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_fast_reorder_hpc4` | 0 | 16 | 203 | 0.9 | its arms group's two years at 64x, the stream's cost moved to 4x (0.0250 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_fast_reorder_hpc4` | 0 | 16 | 91 | 0.4 | its arms group's two years at 64x, the stream's cost moved to 4x (0.0250 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_bofn3_reorder_hpc4` | 0 | 16 | 17,967 | 79.9 | its arms group's two years at 16x, the stream's cost moved to 4x (0.0260 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_bofn3_reorder_hpc4` | 0 | 16 | 537 | 2.4 | its arms group's two years at 64x, the stream's cost moved to 4x (0.0278 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_pkgfn3_reorder_hpc4` | 0 | 16 | 25,163 | 111.8 | its arms group's two years at 16x, the stream's cost moved to 4x (0.0260 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_pkgfn3_reorder_hpc4` | 0 | 16 | 664 | 3.0 | its arms group's two years at 64x, the stream's cost moved to 4x (0.0278 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_fast_reorder_hpc16` | 0 | 16 | 422 | 1.9 | its arms group's two years at 64x, the stream's cost moved to 16x (0.0250 s a day per unit of scale) |
| 2 | hpc | `r6_conventional_external_fast_reorder_hpc16` | 0 | 16 | 310 | 1.4 | its arms group's two years at 64x, the stream's cost moved to 16x (0.0250 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_bofn3_reorder_hpc16` | 0 | 16 | 18,195 | 80.9 | extrapolated from day 510 of a two-year run (seed 0): the cautious end, 17,370-18,195 s |
| 2 | hpc | `r6_conventional_external_bofn3_reorder_hpc16` | 0 | 16 | 781 | 3.5 | its arms group's two years at 64x, the stream's cost moved to 16x (0.0278 s a day per unit of scale) |
| 2 | hpc | `r6_vertical_parallel_pkgfn3_reorder_hpc16` | 0 | 16 | 25,391 | 112.8 | extrapolated from day 500 of a two-year run (seed 0): the cautious end, 19,126-25,391 s |
| 2 | hpc | `r6_conventional_external_pkgfn3_reorder_hpc16` | 0 | 16 | 908 | 4.0 | its arms group's two years at 64x, the stream's cost moved to 16x (0.0278 s a day per unit of scale) |
| 2 | plans | `r6_vertical_wait_fast_reorder` | 0 | 16 | 1,320 | 5.9 | its arms group's two years at 64x, its work x round 5's wait ratio (1.17) |
| 2 | plans | `r6_vertical_external_fast_reorder` | 0 | 16 | 1,274 | 5.7 | its arms group's two years at 64x, its work x round 5's external ratio (0.81) |
| 2 | plans | `r6_vertical_wait_bofn3_reorder` | 0 | 16 | 9,152 | 40.7 | its arms group's two years at 64x, its work x round 5's wait ratio (0.41) |
| 2 | plans | `r6_vertical_external_bofn3_reorder` | 0 | 16 | 12,446 | 55.3 | its arms group's two years at 64x, its work x round 5's external ratio (0.58) |
| 2 | plans | `r6_vertical_wait_pkgfn3_reorder` | 0 | 16 | 17,045 | 75.8 | its arms group's two years at 64x, its work x round 5's wait ratio (0.41) |
| 2 | plans | `r6_vertical_external_pkgfn3_reorder` | 0 | 16 | 23,617 | 105.0 | its arms group's two years at 64x, its work x round 5's external ratio (0.58) |
| 3 | crucibles_late | `r6_vertical_parallel_fast_reorder_late240` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 3 | crucibles_late | `r6_vertical_parallel_fast_lean_late240` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 3 | crucibles_late | `r6_vertical_parallel_bofn3_reorder_late240` | 0 | 16 | 20,726 | 92.1 | its arms group's two years at 64x |
| 3 | crucibles_late | `r6_vertical_parallel_bofn3_lean_late240` | 0 | 16 | 20,726 | 92.1 | its arms group's two years at 64x |
| 3 | crucibles_late | `r6_vertical_parallel_pkgfn3_reorder_late240` | 0 | 16 | 40,131 | 178.4 | its arms group's two years at 64x |
| 3 | crucibles_late | `r6_vertical_parallel_pkgfn3_lean_late240` | 0 | 16 | 40,131 | 178.4 | its arms group's two years at 64x |
| 3 | noused | `r6_vertical_parallel_fast_reorder_noused` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 3 | noused | `r6_vertical_parallel_bofn3_reorder_noused` | 0 | 16 | 20,726 | 92.1 | its arms group's two years at 64x |
| 3 | noused | `r6_vertical_parallel_pkgfn3_reorder_noused` | 0 | 16 | 40,131 | 178.4 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_fast_reorder_atom-3h` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_fast_lean_atom-3h` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_bofn3_reorder_atom-3h` | 0 | 16 | 20,726 | 92.1 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_bofn3_lean_atom-3h` | 0 | 16 | 20,726 | 92.1 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_pkgfn3_reorder_atom-3h` | 0 | 16 | 40,131 | 178.4 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_pkgfn3_lean_atom-3h` | 0 | 16 | 40,131 | 178.4 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_fast_reorder_atom-slow` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_fast_lean_atom-slow` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_bofn3_reorder_atom-slow` | 0 | 16 | 20,726 | 92.1 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_bofn3_lean_atom-slow` | 0 | 16 | 20,726 | 92.1 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_pkgfn3_reorder_atom-slow` | 0 | 16 | 40,131 | 178.4 | its arms group's two years at 64x |
| 4 | atom | `r6_vertical_parallel_pkgfn3_lean_atom-slow` | 0 | 16 | 40,131 | 178.4 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_fast_reorder_dec-none` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_fast_lean_dec-none` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_fast_reorder_dec-none` | 0 | 16 | 1,187 | 5.3 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_fast_lean_dec-none` | 0 | 16 | 1,187 | 5.3 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_bofn3_reorder_dec-none` | 0 | 16 | 20,726 | 92.1 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_bofn3_lean_dec-none` | 0 | 16 | 20,726 | 92.1 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_bofn3_reorder_dec-none` | 0 | 16 | 1,755 | 7.8 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_bofn3_lean_dec-none` | 0 | 16 | 1,755 | 7.8 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_pkgfn3_reorder_dec-none` | 0 | 16 | 40,131 | 178.4 | its arms group's two years at 64x |
| 4 | dec_none | `r6_vertical_parallel_pkgfn3_lean_dec-none` | 0 | 16 | 40,131 | 178.4 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_pkgfn3_reorder_dec-none` | 0 | 16 | 1,882 | 8.4 | its arms group's two years at 64x |
| 4 | dec_none | `r6_conventional_external_pkgfn3_lean_dec-none` | 0 | 16 | 1,882 | 8.4 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_fast_reorder_dec-slow` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_fast_lean_dec-slow` | 0 | 16 | 1,299 | 5.8 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_fast_reorder_dec-slow` | 0 | 16 | 1,187 | 5.3 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_fast_lean_dec-slow` | 0 | 16 | 1,187 | 5.3 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_bofn3_reorder_dec-slow` | 0 | 16 | 20,726 | 92.1 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_bofn3_lean_dec-slow` | 0 | 16 | 20,726 | 92.1 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_bofn3_reorder_dec-slow` | 0 | 16 | 1,755 | 7.8 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_bofn3_lean_dec-slow` | 0 | 16 | 1,755 | 7.8 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_pkgfn3_reorder_dec-slow` | 0 | 16 | 40,131 | 178.4 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_vertical_parallel_pkgfn3_lean_dec-slow` | 0 | 16 | 40,131 | 178.4 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_pkgfn3_reorder_dec-slow` | 0 | 16 | 1,882 | 8.4 | its arms group's two years at 64x |
| 4 | dec_slow | `r6_conventional_external_pkgfn3_lean_dec-slow` | 0 | 16 | 1,882 | 8.4 | its arms group's two years at 64x |
| 5 | hpc256 | `r6_vertical_parallel_fast_reorder_hpc256` | 0 | 16 | 4,804 | 21.4 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0250 s a day per unit of scale) |
| 5 | hpc256 | `r6_conventional_external_fast_reorder_hpc256` | 0 | 16 | 4,694 | 20.9 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0250 s a day per unit of scale) |
| 5 | hpc256 | `r6_vertical_parallel_bofn3_reorder_hpc256` | 0 | 16 | 24,372 | 108.3 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0260 s a day per unit of scale) |
| 5 | hpc256 | `r6_conventional_external_bofn3_reorder_hpc256` | 0 | 16 | 5,651 | 25.1 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0278 s a day per unit of scale) |
| 5 | hpc256 | `r6_vertical_parallel_pkgfn3_reorder_hpc256` | 0 | 16 | 43,777 | 194.6 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0260 s a day per unit of scale) |
| 5 | hpc256 | `r6_conventional_external_pkgfn3_reorder_hpc256` | 0 | 16 | 5,778 | 25.7 | its arms group's two years at 64x, the stream's cost moved to 256x (0.0278 s a day per unit of scale) |

Runs: 1392 in the grid, 1392 left.
Core-hours left by tier: tier 1: 595; tier 2: 888; tier 3: 829; tier 4: 2,296; tier 5: 396; all: 5,004, about 1,251 runner-hours at 4 runs a runner.
By experiment: atom: 1,105; hpc: 600; arms: 595; dec_none: 595; dec_slow: 595; crucibles_late: 552; hpc256: 396; plans: 288; noused: 276 core-hours.
