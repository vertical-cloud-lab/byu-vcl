# Round 5: tables

Made by `python -m twin.like5` from `out/twin5/runs/`. All simulated. Days from the day the money arrives; medians are Kaplan-Meier over seeds (a seed that never gets there counts as censored at day 730; '>730': fewer than half got there). Factors: the conventional lab's median over the automated lab's, with a 95 % paired-bootstrap interval; '>=' a lower bound where fewer than half the conventional seeds got there. Arms with fewer than 12 seeds are not reported. Targets: Aluminium T1 0.42, T2 0.64; Copper T1 0.56, T2 0.66.

## 1. Like with like, four ways (nominal decision windows, the derived atomizer cycle)

| Target | Automated lab | Conventional lab | both ordering as they go | both stocked | vertical stocked, conventional lean (round 3's pairing) | vertical lean, conventional stocked |
|---|---|---|---|---|---|---|
| Aluminium T1 | heuristic | heuristic | 1.0x (0.8-1.1); 16/16 vs 16/16 | 1.1x (0.7-1.9); 16/16 vs 16/16 | 1.6x (1.0-2.3); 16/16 vs 16/16 | 0.7x (0.5-1.2); 16/16 vs 16/16 |
| Aluminium T1 | heuristic | BOFN | 2.3x (1.6-3.0); 16/16 vs 16/16 | 2.6x (1.6-3.6); 16/16 vs 16/16 | 3.7x (2.1-4.8); 16/16 vs 16/16 | 1.6x (1.2-2.1); 16/16 vs 16/16 |
| Aluminium T1 | heuristic | pKGFN | 2.4x (1.6-3.0); 16/16 vs 15/16 | 2.7x (1.6-3.7); 16/16 vs 16/16 | 3.8x (1.9-4.7); 16/16 vs 15/16 | 1.7x (1.2-2.1); 16/16 vs 16/16 |
| Aluminium T2 | heuristic | heuristic | 1.9x (0-∞); 9/16 vs 8/16 | <= 0.8x; 7/16 vs 8/16 | <= 1.0x; 7/16 vs 8/16 | 1.5x (0-∞); 9/16 vs 8/16 |
| Aluminium T2 | heuristic | BOFN | 1.0x (0-1.5); 9/16 vs 15/16 | <= 0.3x; 7/16 vs 15/16 | <= 0.5x; 7/16 vs 15/16 | 0.6x (0-0.9); 9/16 vs 15/16 |
| Aluminium T2 | heuristic | pKGFN | 0.9x (0-1.2); 9/16 vs 15/16 | <= 0.4x; 7/16 vs 15/16 | <= 0.5x; 7/16 vs 15/16 | 0.8x (0-1.1); 9/16 vs 15/16 |
| Copper T1 | funnel | funnel | 1.6x (1.4-2.1); 15/16 vs 14/16 | 1.5x (1.2-∞); 15/16 vs 11/16 | 1.6x (1.4-2.2); 15/16 vs 14/16 | 1.6x (1.3-∞); 15/16 vs 11/16 |
| Copper T1 | funnel | BOFN | >= 2.6x; 15/16 vs 5/16 | >= 2.6x; 15/16 vs 7/16 | >= 2.6x; 15/16 vs 5/16 | >= 2.6x; 15/16 vs 7/16 |
| Copper T1 | funnel | pKGFN | 2.6x (1.7-∞); 15/16 vs 8/16 | >= 2.6x; 15/16 vs 6/16 | 2.6x (1.7-∞); 15/16 vs 8/16 | >= 2.6x; 15/16 vs 6/16 |
| Copper T2 | funnel | funnel | 1.7x (1.4-∞); 14/16 vs 11/16 | 2.1x (1.4-∞); 15/16 vs 9/16 | 1.6x (1.2-∞); 15/16 vs 11/16 | 2.2x (1.6-∞); 14/16 vs 9/16 |
| Copper T2 | funnel | BOFN | >= 2.5x; 14/16 vs 3/16 | >= 2.3x; 15/16 vs 4/16 | >= 2.3x; 15/16 vs 3/16 | >= 2.5x; 14/16 vs 4/16 |
| Copper T2 | funnel | pKGFN | >= 2.5x; 14/16 vs 3/16 | >= 2.3x; 15/16 vs 4/16 | >= 2.3x; 15/16 vs 3/16 | >= 2.5x; 14/16 vs 4/16 |

Cost on one basis (campaign spend to the target; fixed costs and equipment left out; section 3 adds them):

| Target | Automated | Conventional | both lean | both stocked |
|---|---|---|---|---|
| Aluminium T1 | heuristic | heuristic | 1.1x (0.8-1.4) | 0.9x (0.7-1.3) |
| Aluminium T1 | heuristic | BOFN | 3.4x (2.0-4.7) | 1.6x (1.4-2.3) |
| Aluminium T1 | heuristic | pKGFN | 3.5x (2.1-4.4) | 1.7x (1.4-2.2) |
| Aluminium T2 | heuristic | heuristic | 0.9x (0-∞) | <= 0.9x |
| Aluminium T2 | heuristic | BOFN | 0.3x (0-0.7) | <= 0.4x |
| Aluminium T2 | heuristic | pKGFN | 0.3x (0-0.6) | <= 0.4x |
| Copper T1 | funnel | funnel | 0.8x (0.7-1.0) | 0.8x (0.7-∞) |
| Copper T1 | funnel | BOFN | >= 1.0x | 1.0x (0.7-∞) |
| Copper T1 | funnel | pKGFN | 0.8x (0.5-∞) | >= 1.0x |
| Copper T2 | funnel | funnel | 0.8x (0.7-∞) | 0.9x (0.7-∞) |
| Copper T2 | funnel | BOFN | >= 1.0x | >= 0.9x |
| Copper T2 | funnel | pKGFN | >= 1.0x | >= 0.9x |

### The arms

| Arm | seeds | Al T1 | Al T2 | Cu T1 | Cu T2 | Al best | Cu best | money 90 % spent (median day: Al, Cu) |
|---|---|---|---|---|---|---|---|---|
| `r5_conventional_external_bofn3_lean` | 16 | 16/16; 304 | 15/16; 372 | 5/16; >730 | 3/16; >730 | 0.76 ± 0.01 | 0.54 ± 0.03 | 730, 730 |
| `r5_conventional_external_bofn3_reorder` | 16 | 16/16; 214 | 15/16; 228 | 7/16; >730 | 4/16; >730 | 0.77 ± 0.01 | 0.53 ± 0.04 | 730, 730 |
| `r5_conventional_external_fast_lean` | 16 | 16/16; 133 | 8/16; 695 | 14/16; 457 | 11/16; 495 | 0.63 ± 0.02 | 0.67 ± 0.02 | 730, 637 |
| `r5_conventional_external_fast_lean_dec-none` | 16 | 16/16; 129 | 7/16; >730 | 11/16; 454 | 9/16; 520 | 0.64 ± 0.02 | 0.61 ± 0.03 | 704, 658 |
| `r5_conventional_external_fast_lean_dec-slow` | 16 | 16/16; 151 | 7/16; >730 | 11/16; 552 | 7/16; >730 | 0.63 ± 0.02 | 0.59 ± 0.03 | 721, 651 |
| `r5_conventional_external_fast_reorder` | 16 | 16/16; 92 | 8/16; 562 | 11/16; 432 | 9/16; 647 | 0.65 ± 0.02 | 0.61 ± 0.03 | 556, 658 |
| `r5_conventional_external_fast_reorder_dec-none` | 16 | 16/16; 102 | 9/16; 474 | 12/16; 408 | 10/16; 424 | 0.65 ± 0.02 | 0.63 ± 0.03 | 536, 637 |
| `r5_conventional_external_fast_reorder_dec-slow` | 16 | 15/16; 95 | 8/16; 527 | 14/16; 416 | 10/16; 533 | 0.63 ± 0.02 | 0.65 ± 0.02 | 578, 644 |
| `r5_conventional_external_fast_reorder_hpc-add_per_day256-keep512` | 16 | 16/16; 91 | 9/16; 393 | 14/16; 406 | 10/16; 518 | 0.65 ± 0.02 | 0.66 ± 0.02 | 546, 662 |
| `r5_conventional_external_pkgfn3_lean` | 16 | 15/16; 311 | 15/16; 344 | 8/16; 717 | 3/16; >730 | 0.74 ± 0.03 | 0.56 ± 0.03 | 730, 730 |
| `r5_conventional_external_pkgfn3_reorder` | 16 | 16/16; 218 | 15/16; 292 | 6/16; >730 | 4/16; >730 | 0.76 ± 0.02 | 0.51 ± 0.05 | 730, 730 |
| `r5_vertical_external_fast_reorder` | 16 | 15/16; 82 | 10/16; 399 | 13/16; 434 | 9/16; 542 | 0.62 ± 0.04 | 0.60 ± 0.04 | 511, 644 |
| `r5_vertical_parallel_fast_lean` | 16 | 16/16; 130 | 9/16; 365 | 15/16; 278 | 14/16; 293 | 0.64 ± 0.02 | 0.69 ± 0.02 | 354, 318 |
| `r5_vertical_parallel_fast_lean_atom-3h` | 16 | 16/16; 130 | 8/16; 400 | 16/16; 275 | 16/16; 275 | 0.64 ± 0.02 | 0.71 ± 0.01 | 357, 329 |
| `r5_vertical_parallel_fast_lean_atom-slow` | 16 | 16/16; 130 | 7/16; >730 | 16/16; 282 | 15/16; 289 | 0.63 ± 0.02 | 0.71 ± 0.01 | 392, 336 |
| `r5_vertical_parallel_fast_lean_dec-none` | 16 | 16/16; 134 | 7/16; >730 | 15/16; 275 | 14/16; 283 | 0.64 ± 0.02 | 0.69 ± 0.01 | 357, 315 |
| `r5_vertical_parallel_fast_lean_dec-slow` | 16 | 16/16; 126 | 6/16; >730 | 16/16; 284 | 13/16; 291 | 0.64 ± 0.02 | 0.69 ± 0.01 | 343, 318 |
| `r5_vertical_parallel_fast_reorder` | 16 | 16/16; 81 | 7/16; >730 | 15/16; 281 | 15/16; 313 | 0.64 ± 0.02 | 0.69 ± 0.02 | 318, 312 |
| `r5_vertical_parallel_fast_reorder_atom-3h` | 16 | 16/16; 81 | 7/16; >730 | 15/16; 281 | 14/16; 313 | 0.64 ± 0.02 | 0.68 ± 0.02 | 318, 318 |
| `r5_vertical_parallel_fast_reorder_atom-slow` | 16 | 16/16; 82 | 8/16; 341 | 14/16; 289 | 13/16; 313 | 0.64 ± 0.02 | 0.67 ± 0.02 | 364, 336 |
| `r5_vertical_parallel_fast_reorder_dec-none` | 16 | 16/16; 81 | 9/16; 279 | 15/16; 281 | 13/16; 289 | 0.65 ± 0.02 | 0.68 ± 0.02 | 318, 294 |
| `r5_vertical_parallel_fast_reorder_dec-slow` | 16 | 16/16; 102 | 10/16; 324 | 14/16; 300 | 14/16; 300 | 0.66 ± 0.02 | 0.68 ± 0.02 | 318, 315 |
| `r5_vertical_parallel_fast_reorder_hpc-add_per_day256-keep512` | 16 | 16/16; 81 | 8/16; 347 | 15/16; 302 | 15/16; 304 | 0.63 ± 0.02 | 0.69 ± 0.02 | 312, 308 |
| `r5_vertical_parallel_fast_reorder_noused` | 16 | 16/16; 81 | 7/16; >730 | 14/16; 283 | 13/16; 309 | 0.63 ± 0.02 | 0.68 ± 0.02 | 312, 294 |
| `r5_vertical_wait_fast_reorder` | 16 | 16/16; 277 | 7/16; >730 | 16/16; 362 | 14/16; 380 | 0.63 ± 0.02 | 0.70 ± 0.01 | 427, 360 |

### What the stock buys within a lab (lean over stocked, same policy)

| Lab | Policy | Target | factor; seeds there (stocked vs lean) |
|---|---|---|---|
| vertical | heuristic | Aluminium T1 | 1.6x (1.0-2.4); 16/16 vs 16/16 |
| vertical | heuristic | Aluminium T2 | <= 0.5x; 7/16 vs 9/16 |
| vertical | funnel | Copper T1 | 1.0x (0.9-1.1); 15/16 vs 15/16 |
| vertical | funnel | Copper T2 | 0.9x (0.8-1.1); 15/16 vs 14/16 |
| conventional | heuristic | Aluminium T1 | 1.4x (0.9-2.0); 16/16 vs 16/16 |
| conventional | heuristic | Aluminium T2 | 1.2x (0-∞); 8/16 vs 8/16 |
| conventional | funnel | Copper T1 | 1.1x (0-1.4); 11/16 vs 14/16 |
| conventional | funnel | Copper T2 | 0.8x (0-1.2); 9/16 vs 11/16 |
| conventional | BOFN | Aluminium T1 | 1.4x (1.1-1.7); 16/16 vs 16/16 |
| conventional | BOFN | Aluminium T2 | 1.6x (1.1-2.2); 15/16 vs 15/16 |
| conventional | BOFN | Copper T1 | neither; 7/16 vs 5/16 |
| conventional | BOFN | Copper T2 | neither; 4/16 vs 3/16 |
| conventional | pKGFN | Aluminium T1 | 1.4x (1.1-1.7); 16/16 vs 15/16 |
| conventional | pKGFN | Aluminium T2 | 1.2x (0.9-1.6); 15/16 vs 15/16 |
| conventional | pKGFN | Copper T1 | <= 1.0x; 6/16 vs 8/16 |
| conventional | pKGFN | Copper T2 | neither; 4/16 vs 3/16 |

### What the optimizer buys within a lab (the heuristic or the funnel over BOFN or pKGFN, same seeds)

| Lab | Stock | Optimizer | Target | factor; seeds there (optimizer vs cheap policy) |
|---|---|---|---|---|
| conventional | stocked | BOFN | Aluminium T1 | 0.4x (0.3-0.8); 16/16 vs 16/16 |
| conventional | stocked | BOFN | Aluminium T2 | 2.5x (1.3-∞); 15/16 vs 8/16 |
| conventional | stocked | BOFN | Copper T1 | <= 0.6x; 7/16 vs 11/16 |
| conventional | stocked | BOFN | Copper T2 | <= 0.9x; 4/16 vs 9/16 |
| conventional | stocked | pKGFN | Aluminium T1 | 0.4x (0.3-0.7); 16/16 vs 16/16 |
| conventional | stocked | pKGFN | Aluminium T2 | 1.9x (1.1-∞); 15/16 vs 8/16 |
| conventional | stocked | pKGFN | Copper T1 | <= 0.6x; 6/16 vs 11/16 |
| conventional | stocked | pKGFN | Copper T2 | <= 0.9x; 4/16 vs 9/16 |
| conventional | lean | BOFN | Aluminium T1 | 0.4x (0.3-0.6); 16/16 vs 16/16 |
| conventional | lean | BOFN | Aluminium T2 | 1.9x (0.6-∞); 15/16 vs 8/16 |
| conventional | lean | BOFN | Copper T1 | <= 0.6x; 5/16 vs 14/16 |
| conventional | lean | BOFN | Copper T2 | <= 0.7x; 3/16 vs 11/16 |
| conventional | lean | pKGFN | Aluminium T1 | 0.4x (0.3-0.6); 15/16 vs 16/16 |
| conventional | lean | pKGFN | Aluminium T2 | 2.0x (0.6-∞); 15/16 vs 8/16 |
| conventional | lean | pKGFN | Copper T1 | 0.6x (0-1.0); 8/16 vs 14/16 |
| conventional | lean | pKGFN | Copper T2 | <= 0.7x; 3/16 vs 11/16 |

## Decision time: the four-way factors with no delay, the nominal windows and slow windows (cheap policies)

| Target | Pairing | no delay | nominal | slow |
|---|---|---|---|---|
| Aluminium T1 | both ordering as they go | 1.0x (0.8-1.2) | 1.0x (0.8-1.1) | 1.2x (0.8-1.7) |
| Aluminium T1 | both stocked | 1.2x (0.9-1.7) | 1.1x (0.7-1.9) | 0.9x (0.7-1.8) |
| Aluminium T1 | vertical stocked, conventional lean (round 3's pairing) | 1.6x (1.1-2.3) | 1.6x (1.0-2.3) | 1.5x (1.3-2.7) |
| Aluminium T1 | vertical lean, conventional stocked | 0.8x (0.6-1.1) | 0.7x (0.5-1.1) | 0.7x (0.6-1.0) |
| Aluminium T2 | both ordering as they go | neither | 1.9x (0-∞) | neither |
| Aluminium T2 | both stocked | 1.7x (0-∞) | <= 0.8x | 1.6x (1.1-∞) |
| Aluminium T2 | vertical stocked, conventional lean (round 3's pairing) | >= 2.6x | <= 1.0x | >= 2.3x |
| Aluminium T2 | vertical lean, conventional stocked | <= 0.6x | 1.5x (0-∞) | <= 0.7x |
| Copper T1 | both ordering as they go | 1.7x (1.4-∞) | 1.6x (1.4-2.0) | 1.9x (1.1-∞) |
| Copper T1 | both stocked | 1.4x (1.2-2.3) | 1.5x (1.2-∞) | 1.4x (1.1-1.6) |
| Copper T1 | vertical stocked, conventional lean (round 3's pairing) | 1.6x (1.3-∞) | 1.6x (1.3-2.2) | 1.8x (1.2-∞) |
| Copper T1 | vertical lean, conventional stocked | 1.5x (1.3-2.3) | 1.6x (1.3-∞) | 1.5x (1.1-1.7) |
| Copper T2 | both ordering as they go | 1.8x (1.4-∞) | 1.7x (1.4-∞) | >= 2.5x |
| Copper T2 | both stocked | 1.5x (1.1-∞) | 2.1x (1.4-∞) | 1.8x (1.3-∞) |
| Copper T2 | vertical stocked, conventional lean (round 3's pairing) | 1.8x (1.2-∞) | 1.6x (1.2-∞) | >= 2.4x |
| Copper T2 | vertical lean, conventional stocked | 1.5x (1.2-∞) | 2.2x (1.6-∞) | 1.8x (1.3-∞) |

| Arm | Target | no delay | nominal | slow |
|---|---|---|---|---|
| vertical, stocked | Aluminium T1 | 16/16; 81 | 16/16; 81 | 16/16; 102 |
| vertical, lean | Aluminium T1 | 16/16; 134 | 16/16; 130 | 16/16; 126 |
| conventional, stocked | Aluminium T1 | 16/16; 102 | 16/16; 92 | 15/16; 95 |
| conventional, lean | Aluminium T1 | 16/16; 129 | 16/16; 133 | 16/16; 151 |
| vertical, stocked | Aluminium T2 | 9/16; 279 | 7/16; >730 | 10/16; 324 |
| vertical, lean | Aluminium T2 | 7/16; >730 | 9/16; 365 | 6/16; >730 |
| conventional, stocked | Aluminium T2 | 9/16; 474 | 8/16; 562 | 8/16; 527 |
| conventional, lean | Aluminium T2 | 7/16; >730 | 8/16; 695 | 7/16; >730 |
| vertical, stocked | Copper T1 | 15/16; 281 | 15/16; 281 | 14/16; 300 |
| vertical, lean | Copper T1 | 15/16; 275 | 15/16; 278 | 16/16; 284 |
| conventional, stocked | Copper T1 | 12/16; 408 | 11/16; 432 | 14/16; 416 |
| conventional, lean | Copper T1 | 11/16; 454 | 14/16; 457 | 11/16; 552 |
| vertical, stocked | Copper T2 | 13/16; 289 | 15/16; 313 | 14/16; 300 |
| vertical, lean | Copper T2 | 14/16; 283 | 14/16; 293 | 13/16; 291 |
| conventional, stocked | Copper T2 | 10/16; 424 | 9/16; 647 | 10/16; 533 |
| conventional, lean | Copper T2 | 9/16; 520 | 11/16; 495 | 7/16; >730 |

## The automated atomizer's cycle (note 2; the automated lab, cheap policies)

| Cycle | Stock | Al T1 | Al T2 | Cu T1 | Cu T2 | atomizer runs in 2 years (Al, Cu) |
|---|---|---|---|---|---|---|
| derived | stocked | 16/16; 81 | 7/16; >730 | 15/16; 281 | 15/16; 313 | 637, 139 |
| derived | lean | 16/16; 130 | 9/16; 365 | 15/16; 278 | 14/16; 293 | 728, 137 |
| 3h | stocked | 16/16; 81 | 7/16; >730 | 15/16; 281 | 14/16; 313 | 637, 137 |
| 3h | lean | 16/16; 130 | 8/16; 400 | 16/16; 275 | 16/16; 275 | 724, 135 |
| slow | stocked | 16/16; 82 | 8/16; 341 | 14/16; 289 | 13/16; 313 | 648, 138 |
| slow | lean | 16/16; 130 | 7/16; >730 | 16/16; 282 | 15/16; 289 | 720, 134 |

## Used equipment (the automated lab, stocked, cheap policies)

| Item | bought used in | arrived faulty | days bought (median; min) | expected by the rule | $ saved (mean) |
|---|---|---|---|---|---|
| Instron 3119-608 environmental chamber (to 600 C) | 16 seeds | 2 | 30; -7 | 25 | 26,562 |
| FANUC ROBOCUT wire EDM | 16 seeds | 4 | 48; 0 | 39 | 117,875 |
| Instron 68FM-100 floor frame with grips and extensometer | 16 seeds | 1 | 27; -7 | 25 | 94,609 |
| KLA iMicro nanoindenter | 16 seeds | 7 | 15; -7 | 25 | 121,094 |

| Target | all new over with used: factor; seeds there (used vs new) |
|---|---|
| Aluminium T1 | 1.0x (1.0-1.0); 16/16 vs 16/16 |
| Aluminium T2 | neither; 7/16 vs 7/16 |
| Copper T1 | 1.0x (0.9-1.0); 15/16 vs 14/16 |
| Copper T2 | 1.0x (0.9-1.1); 15/16 vs 13/16 |

## 2. Round 4's three plans (cheap policies, stocked)

| Plan | starts (median day) | Al T1 | Al T2 | Cu T1 | Cu T2 | Al best | Cu best |
|---|---|---|---|---|---|---|---|
| wait | 247 | 16/16; 277 | 7/16; >730 | 16/16; 362 | 14/16; 380 | 0.63 ± 0.02 | 0.70 ± 0.01 |
| parallel | 0 | 16/16; 81 | 7/16; >730 | 15/16; 281 | 15/16; 313 | 0.64 ± 0.02 | 0.69 ± 0.02 |
| external | 0 | 15/16; 82 | 10/16; 399 | 13/16; 434 | 9/16; 542 | 0.62 ± 0.04 | 0.60 ± 0.04 |

| Parallel against | Target | factor (other plan's median over parallel's); parallel first / other first |
|---|---|---|
| wait | Aluminium T1 | 3.4x (2.1-4.0); 16 / 0 |
| wait | Aluminium T2 | neither; 7 / 3 |
| wait | Copper T1 | 1.3x (1.1-1.4); 15 / 1 |
| wait | Copper T2 | 1.2x (1.1-1.4); 14 / 2 |
| external | Aluminium T1 | 1.0x (0.9-1.1); 7 / 7 |
| external | Aluminium T2 | <= 0.5x; 4 / 7 |
| external | Copper T1 | 1.5x (1.2-2.6); 15 / 1 |
| external | Copper T2 | 1.7x (1.2-∞); 15 / 0 |

## 3. Economics (round 3's model; the bases are in `twin/like5.py` `economics`)

Fixed costs a year: vertical $1,184,047 (depreciation $599,907); conventional $121,470 (depreciation $63,761).

| Arm | Campaign | spend + fixed, 2 years | new alloys tested | per alloy (with fixed) | per alloy (campaign only) | to T1 with equipment (seeds) | to T2 with equipment (seeds) |
|---|---|---|---|---|---|---|---|
| `vertical|fast|reorder` | Aluminium | $1,816,274 | 150.2 | $11,994 | $1,570 | $2,097,821 (16/16) | $3,460,365 (7/16) |
| `vertical|fast|reorder` | Copper | $909,529 | 19.4 | $41,449 | $5,495 | $1,804,969 (15/16) | $1,837,325 (15/16) |
| `vertical|fast|lean` | Aluminium | $1,815,839 | 163.1 | $11,005 | $1,441 | $2,727,352 (16/16) | $3,500,547 (9/16) |
| `vertical|fast|lean` | Copper | $909,557 | 20.8 | $40,455 | $5,355 | $1,802,028 (15/16) | $1,808,691 (14/16) |
| `conventional|fast|reorder` | Aluminium | $392,785 | 74.1 | $5,352 | $3,178 | $48,842 (16/16) | $180,029 (8/16) |
| `conventional|fast|reorder` | Copper | $196,212 | 5.4 | $39,023 | $22,827 | $97,720 (11/16) | $110,151 (9/16) |
| `conventional|fast|lean` | Aluminium | $366,195 | 64.3 | $5,515 | $3,149 | $37,816 (16/16) | $77,696 (8/16) |
| `conventional|fast|lean` | Copper | $195,418 | 5.0 | $39,375 | $23,179 | $104,654 (14/16) | $104,381 (11/16) |
| `conventional|bofn3|reorder` | Aluminium | $341,628 | 33.1 | $10,469 | $5,403 | $98,293 (16/16) | $108,926 (15/16) |
| `conventional|bofn3|reorder` | Copper | $174,021 | 3.4 | $58,580 | $31,587 | $101,655 (7/16) | $118,024 (4/16) |
| `conventional|bofn3|lean` | Aluminium | $307,437 | 21.2 | $13,933 | $6,918 | $102,101 (16/16) | $117,018 (15/16) |
| `conventional|bofn3|lean` | Copper | $167,355 | 3.2 | $54,987 | $27,994 | $73,076 (5/16) | $78,859 (3/16) |
| `conventional|pkgfn3|reorder` | Aluminium | $345,470 | 37.0 | $10,113 | $5,352 | $100,096 (16/16) | $129,800 (15/16) |
| `conventional|pkgfn3|reorder` | Copper | $173,700 | 3.5 | $52,197 | $27,595 | $82,319 (6/16) | $106,751 (4/16) |
| `conventional|pkgfn3|lean` | Aluminium | $310,877 | 27.4 | $13,140 | $6,209 | $99,563 (15/16) | $112,477 (15/16) |
| `conventional|pkgfn3|lean` | Copper | $164,861 | 3.0 | $55,191 | $28,197 | $83,290 (8/16) | $85,351 (3/16) |

## Stock (mean over seeds)

| Arm | Campaign | charges | charges that waited for stock | waits after day 90 | mean wait (days) | stock bought | left at the end |
|---|---|---|---|---|---|---|---|
| `r5_conventional_external_fast_lean` | Aluminium | 293 | 99% | 255 | 43.0 | $51,347 | $1,718 |
| `r5_conventional_external_fast_lean` | Copper | 65 | 75% | 35 | 86.0 | $90,112 | $569 |
| `r5_conventional_external_fast_reorder` | Aluminium | 311 | 37% | 90 | 27.2 | $58,308 | $4,784 |
| `r5_conventional_external_fast_reorder` | Copper | 66 | 69% | 29 | 76.7 | $90,121 | $794 |
| `r5_vertical_parallel_fast_lean` | Aluminium | 648 | 100% | 609 | 40.4 | $136,144 | $2,255 |
| `r5_vertical_parallel_fast_lean` | Copper | 109 | 66% | 59 | 66.5 | $99,075 | $881 |
| `r5_vertical_parallel_fast_reorder` | Aluminium | 579 | 85% | 473 | 28.3 | $125,892 | $5,469 |
| `r5_vertical_parallel_fast_reorder` | Copper | 108 | 62% | 49 | 60.4 | $99,749 | $775 |
| `r5_conventional_external_bofn3_lean` | Aluminium | 245 | 100% | 210 | 53.0 | $68,274 | $1,530 |
| `r5_conventional_external_bofn3_lean` | Copper | 45 | 96% | 35 | 53.6 | $57,931 | $681 |
| `r5_conventional_external_bofn3_reorder` | Aluminium | 288 | 42% | 91 | 33.1 | $85,635 | $12,369 |
| `r5_conventional_external_bofn3_reorder` | Copper | 46 | 91% | 30 | 37.9 | $62,593 | $3,947 |
| `r5_conventional_external_pkgfn3_lean` | Aluminium | 246 | 100% | 210 | 53.2 | $68,419 | $1,455 |
| `r5_conventional_external_pkgfn3_lean` | Copper | 44 | 96% | 34 | 51.8 | $55,976 | $649 |
| `r5_conventional_external_pkgfn3_reorder` | Aluminium | 291 | 45% | 100 | 33.1 | $86,256 | $11,916 |
| `r5_conventional_external_pkgfn3_reorder` | Copper | 44 | 94% | 30 | 40.4 | $63,093 | $4,064 |
| `r5_vertical_external_fast_reorder` | Aluminium | 303 | 35% | 84 | 28.6 | $61,102 | $5,745 |
| `r5_vertical_external_fast_reorder` | Copper | 67 | 70% | 29 | 77.4 | $91,791 | $575 |
| `r5_vertical_wait_fast_reorder` | Aluminium | 672 | 92% | 620 | 28.1 | $151,079 | $5,194 |
| `r5_vertical_wait_fast_reorder` | Copper | 115 | 67% | 77 | 54.4 | $101,592 | $566 |
| `r5_conventional_external_fast_reorder_hpc-add_per_day256-keep512` | Aluminium | 309 | 38% | 95 | 24.5 | $58,079 | $4,815 |
| `r5_conventional_external_fast_reorder_hpc-add_per_day256-keep512` | Copper | 67 | 69% | 30 | 76.3 | $89,335 | $757 |
| `r5_vertical_parallel_fast_reorder_hpc-add_per_day256-keep512` | Aluminium | 577 | 85% | 470 | 28.6 | $124,878 | $5,343 |
| `r5_vertical_parallel_fast_reorder_hpc-add_per_day256-keep512` | Copper | 108 | 63% | 49 | 61.0 | $99,449 | $706 |

### Purchasing look-back: `r5_vertical_parallel_fast_reorder`

Each set against each seed's own weekly use, mean over seeds. An item-week short is a week that ends with more of an item used than has arrived (a charge was waiting for it). The look-back schedules order every 8 weeks, timed to arrive as each period starts (never before day 0), for the use until the next order arrives at the given quantile over seeds.

| Campaign | rule | bought | left at the end | item-weeks short |
|---|---|---|---|---|
| Aluminium | the heuristic, as it ran | $125,651 | $5,490 | 200.9 |
| Aluminium | look-back schedule, q = 0.5 | $116,146 | $4,731 | 299.2 |
| Aluminium | look-back schedule, q = 0.75 | $121,574 | $8,211 | 172.9 |
| Aluminium | look-back schedule, q = 0.9 | $130,002 | $15,484 | 91.2 |
| Copper | the heuristic, as it ran | $99,749 | $765 | 349.2 |
| Copper | look-back schedule, q = 0.5 | $98,207 | $2,473 | 390.1 |
| Copper | look-back schedule, q = 0.75 | $100,713 | $4,202 | 194.8 |
| Copper | look-back schedule, q = 0.9 | $102,888 | $6,051 | 97.7 |

Recommended buying schedule (q = 0.75), Aluminium: the 8 items with the most money (day the order is placed: quantity)

| Item | median lead (days) | orders | total | $ |
|---|---|---|---|---|
| cc_plate | 56 | d0: 20.3, d49: 66.3, d105: 32.1, d161: 5.7, d217: 1 | 125 | $43,890 |
| argon | 3 | d0: 1, d49: 1, d105: 5.06, d161: 73.7, d217: 142, d273: 32.8, d329: 14.3 ... | 279 | $25,137 |
| graphite_crucible | 49 | d0: 6.88, d56: 24.9, d112: 15.8, d168: 4, d280: 1 | 52.5 | $23,625 |
| build_plate | 14 | d0: 11.5, d35: 11.8, d91: 14.2, d147: 68, d203: 119, d259: 33.2, d315: 11.8 ... | 270 | $21,620 |
| al_bar_hp | 3 | d49: 2, d105: 5.31, d161: 48.1, d217: 22.3, d273: 4.57, d329: 2 | 84.2 | $3,368 |
| al_sc2 | 28 | d133: 0.005 | 0.005 | $1,175 |
| si_lump | 10 | d0: 0.25, d42: 0.25, d98: 0.52, d154: 4.81, d210: 2.29, d266: 0.25 | 8.38 | $1,005 |
| al_er10 | 28 | d133: 0.025 | 0.025 | $800 |

Recommended buying schedule (q = 0.75), Copper: the 8 items with the most money (day the order is placed: quantity)

| Item | median lead (days) | orders | total | $ |
|---|---|---|---|---|
| cc_plate | 56 | d0: 70, d49: 38.5, d105: 25.8, d161: 3, d217: 1, d273: 1 | 139 | $48,738 |
| bn_nozzle | 49 | d0: 70, d56: 11.8, d112: 50.2, d168: 5.25, d224: 1, d280: 1 | 139 | $16,710 |
| cu_ofe_bar | 3 | d0: 48.1, d49: 28.1, d105: 2, d161: 41.8, d217: 28.6, d273: 4.14, d329: 2 | 155 | $13,921 |
| graphite_crucible | 49 | d0: 11, d56: 1.96, d112: 8.38, d168: 1, d224: 1 | 23.3 | $10,500 |
| ded_substrate | 3 | d105: 1, d161: 2.25, d217: 13.8, d273: 9, d329: 3 | 29 | $4,350 |
| ni_pellet | 5 | d0: 1.64, d42: 0.914, d154: 1.28, d210: 0.854, d266: 0.885, d322: 0.25 | 5.82 | $2,559 |
| argon | 3 | d0: 6.06, d49: 4.83, d161: 6.89, d217: 4.61, d273: 1 | 23.4 | $2,105 |
| fe_powder | 10 | d0: 0.577, d42: 0.264, d154: 0.621, d210: 0.502, d266: 0.25 | 2.21 | $664 |

### Purchasing look-back: `r5_conventional_external_fast_reorder`

Each set against each seed's own weekly use, mean over seeds. An item-week short is a week that ends with more of an item used than has arrived (a charge was waiting for it). The look-back schedules order every 8 weeks, timed to arrive as each period starts (never before day 0), for the use until the next order arrives at the given quantile over seeds.

| Campaign | rule | bought | left at the end | item-weeks short |
|---|---|---|---|---|
| Aluminium | the heuristic, as it ran | $58,261 | $5,056 | 92.8 |
| Aluminium | look-back schedule, q = 0.5 | $50,528 | $2,865 | 184.8 |
| Aluminium | look-back schedule, q = 0.75 | $53,875 | $5,497 | 102.9 |
| Aluminium | look-back schedule, q = 0.9 | $61,601 | $12,208 | 60.8 |
| Copper | the heuristic, as it ran | $89,698 | $617 | 346.4 |
| Copper | look-back schedule, q = 0.5 | $88,214 | $1,928 | 288.7 |
| Copper | look-back schedule, q = 0.75 | $90,059 | $3,045 | 139.0 |
| Copper | look-back schedule, q = 0.9 | $91,650 | $4,424 | 70.1 |

Recommended buying schedule (q = 0.75), Aluminium: the 8 items with the most money (day the order is placed: quantity)

| Item | median lead (days) | orders | total | $ |
|---|---|---|---|---|
| cc_plate | 56 | d0: 16.9, d49: 7.1, d105: 7.6, d161: 7.8, d217: 7.4, d273: 6.9, d329: 7.2 ... | 67.6 | $23,660 |
| graphite_crucible | 49 | d0: 6.33, d56: 3.04, d112: 3, d168: 3.5, d224: 2.83, d280: 2.83, d336: 3.12 ... | 28.5 | $12,825 |
| build_plate | 14 | d0: 8.25, d35: 11.2, d91: 14.5, d147: 16.2, d203: 17, d259: 15, d315: 14.8 ... | 139 | $11,140 |
| argon | 3 | d0: 1, d49: 1, d105: 1.46, d161: 2.2, d217: 2.35, d273: 2.41, d329: 2.29 ... | 19.2 | $1,729 |
| al_bar_hp | 3 | d49: 2, d105: 3.06, d161: 4.98, d217: 5.56, d273: 5.4, d329: 4.85, d385: 4.75 ... | 41.4 | $1,655 |
| al_sc2 | 28 | d525: 0.005 | 0.005 | $1,175 |
| li_metal | 21 | d0: 1, d308: 1, d420: 1 | 3 | $600 |
| si_lump | 10 | d0: 0.25, d42: 0.25, d98: 0.25, d154: 0.512, d210: 0.539, d266: 0.388, d322: 0.393 ... | 3.85 | $463 |

Recommended buying schedule (q = 0.75), Copper: the 8 items with the most money (day the order is placed: quantity)

| Item | median lead (days) | orders | total | $ |
|---|---|---|---|---|
| cc_plate | 56 | d0: 65.5, d105: 13.5, d161: 5, d217: 3, d273: 5, d329: 17, d385: 8.75 ... | 129 | $45,150 |
| bn_nozzle | 49 | d0: 65.5, d112: 13.5, d168: 5, d224: 3, d280: 3.5, d336: 17, d392: 9.5 ... | 129 | $15,480 |
| cu_ofe_bar | 3 | d0: 48.2, d49: 21.4, d105: 2.18, d217: 14.5, d273: 7.4, d329: 2.2, d385: 6.51 ... | 142 | $12,820 |
| graphite_crucible | 49 | d0: 10.9, d112: 1.62, d168: 1, d224: 1, d336: 2.75, d392: 1.58, d448: 1 ... | 20.8 | $9,375 |
| ni_pellet | 5 | d0: 1.6, d42: 0.622, d154: 0.662, d210: 0.377, d266: 0.25, d378: 0.25, d434: 0.892 ... | 5.43 | $2,388 |
| argon | 3 | d0: 6.06, d49: 3.63, d105: 1, d217: 1.82, d273: 1, d329: 1, d385: 1 ... | 22.4 | $2,019 |
| ded_substrate | 3 | d105: 1, d217: 1, d273: 1, d329: 1, d385: 1, d497: 1, d553: 1 ... | 8 | $1,200 |
| fe_powder | 10 | d0: 0.6, d42: 0.25, d154: 0.25, d210: 0.25, d434: 0.25, d490: 0.25 | 1.85 | $555 |

### Purchasing look-back: `r5_vertical_parallel_fast_lean`

Each set against each seed's own weekly use, mean over seeds. An item-week short is a week that ends with more of an item used than has arrived (a charge was waiting for it). The look-back schedules order every 8 weeks, timed to arrive as each period starts (never before day 0), for the use until the next order arrives at the given quantile over seeds.

| Campaign | rule | bought | left at the end | item-weeks short |
|---|---|---|---|---|
| Aluminium | look-back schedule, q = 0.5 | $130,582 | $4,018 | 305.8 |
| Aluminium | look-back schedule, q = 0.75 | $135,463 | $7,550 | 189.2 |
| Aluminium | look-back schedule, q = 0.9 | $147,398 | $17,386 | 105.9 |
| Copper | look-back schedule, q = 0.5 | $95,547 | $1,723 | 394.0 |
| Copper | look-back schedule, q = 0.75 | $99,096 | $4,056 | 215.0 |
| Copper | look-back schedule, q = 0.9 | $103,306 | $7,478 | 98.5 |

Recommended buying schedule (q = 0.75), Aluminium: the 8 items with the most money (day the order is placed: quantity)

| Item | median lead (days) | orders | total | $ |
|---|---|---|---|---|
| cc_plate | 56 | d0: 19.1, d49: 78.3, d105: 33.9, d161: 7.9, d217: 1, d385: 1 | 141 | $49,420 |
| argon | 3 | d0: 1, d49: 1.2, d105: 2.63, d161: 60.1, d217: 135, d273: 75.4, d329: 31.5 ... | 311 | $28,026 |
| graphite_crucible | 49 | d0: 7.33, d56: 23.3, d112: 23.5, d168: 3.21, d224: 1 | 58.4 | $26,269 |
| build_plate | 14 | d0: 5.25, d35: 7.75, d91: 13, d147: 45.5, d203: 138, d259: 58, d315: 22 ... | 294 | $23,520 |
| al_bar_hp | 3 | d49: 2.11, d105: 4.48, d161: 52.1, d217: 25.3, d273: 6.62, d329: 2, d385: 2 | 94.6 | $3,784 |
| al_sc2 | 28 | d133: 0.005, d189: 0.005 | 0.01 | $2,350 |
| si_lump | 10 | d0: 0.25, d42: 0.25, d98: 0.54, d154: 5.96, d210: 2.38, d266: 0.299, d322: 0.25 | 9.93 | $1,191 |
| li_metal | 21 | d0: 1 | 1 | $200 |

Recommended buying schedule (q = 0.75), Copper: the 8 items with the most money (day the order is placed: quantity)

| Item | median lead (days) | orders | total | $ |
|---|---|---|---|---|
| cc_plate | 56 | d0: 43, d49: 77.2, d105: 11, d161: 4.75, d273: 1 | 137 | $47,950 |
| bn_nozzle | 49 | d0: 43, d56: 56.8, d112: 31.5, d168: 4.75, d280: 1 | 137 | $16,440 |
| cu_ofe_bar | 3 | d0: 47.3, d49: 2, d161: 81.7, d217: 13.2, d273: 4.8, d385: 2 | 151 | $13,596 |
| graphite_crucible | 49 | d0: 6.5, d56: 9.46, d112: 5.25, d168: 1 | 22.2 | $9,994 |
| ded_substrate | 3 | d49: 1, d161: 3.25, d217: 9, d273: 12.2, d329: 4.5, d441: 1 | 31 | $4,650 |
| ni_pellet | 5 | d0: 1.68, d98: 0.25, d154: 3.21, d266: 0.7 | 5.84 | $2,571 |
| argon | 3 | d0: 6.06, d161: 13.8, d217: 1.97, d273: 1 | 22.9 | $2,057 |
| fe_powder | 10 | d0: 0.534, d98: 0.25, d154: 0.761, d210: 0.25, d322: 0.25 | 2.05 | $614 |

### Purchasing look-back: `r5_conventional_external_fast_lean`

Each set against each seed's own weekly use, mean over seeds. An item-week short is a week that ends with more of an item used than has arrived (a charge was waiting for it). The look-back schedules order every 8 weeks, timed to arrive as each period starts (never before day 0), for the use until the next order arrives at the given quantile over seeds.

| Campaign | rule | bought | left at the end | item-weeks short |
|---|---|---|---|---|
| Aluminium | look-back schedule, q = 0.5 | $50,244 | $3,373 | 160.6 |
| Aluminium | look-back schedule, q = 0.75 | $51,598 | $4,252 | 107.2 |
| Aluminium | look-back schedule, q = 0.9 | $55,915 | $7,987 | 53.1 |
| Copper | look-back schedule, q = 0.5 | $86,955 | $1,160 | 250.8 |
| Copper | look-back schedule, q = 0.75 | $89,151 | $2,618 | 136.3 |
| Copper | look-back schedule, q = 0.9 | $91,306 | $4,449 | 71.8 |

Recommended buying schedule (q = 0.75), Aluminium: the 8 items with the most money (day the order is placed: quantity)

| Item | median lead (days) | orders | total | $ |
|---|---|---|---|---|
| cc_plate | 56 | d0: 16.9, d49: 5.1, d105: 5.6, d161: 4.9, d217: 5.9, d273: 5, d329: 6.2 ... | 68.1 | $23,835 |
| graphite_crucible | 49 | d0: 6.54, d56: 2.29, d112: 2.33, d168: 1.88, d224: 2.04, d280: 2.46, d336: 2.54 ... | 28 | $12,619 |
| build_plate | 14 | d0: 5.25, d35: 5.75, d91: 12.2, d147: 10, d203: 10, d259: 12.8, d315: 10 ... | 128 | $10,200 |
| argon | 3 | d0: 1, d49: 1, d105: 1.46, d161: 1.58, d217: 1.73, d273: 1.52, d329: 1.82 ... | 19.4 | $1,749 |
| al_bar_hp | 3 | d49: 2, d105: 3.05, d161: 3.6, d217: 3.97, d273: 3.48, d329: 4, d385: 3.92 ... | 41.4 | $1,657 |
| si_lump | 10 | d0: 0.25, d42: 0.25, d98: 0.265, d154: 0.355, d210: 0.43, d266: 0.36, d322: 0.338 ... | 4.09 | $491 |
| li_metal | 21 | d0: 1, d420: 1 | 2 | $400 |
| al_zr10 | 35 | d0: 0.1, d406: 0.1 | 0.2 | $180 |

Recommended buying schedule (q = 0.75), Copper: the 8 items with the most money (day the order is placed: quantity)

| Item | median lead (days) | orders | total | $ |
|---|---|---|---|---|
| cc_plate | 56 | d0: 47.5, d49: 6.75, d105: 14, d161: 18, d217: 11, d273: 2, d329: 8 ... | 127 | $44,538 |
| bn_nozzle | 49 | d0: 46.2, d56: 7, d112: 12.5, d168: 20.5, d224: 11, d280: 2, d336: 8 ... | 127 | $15,270 |
| cu_ofe_bar | 3 | d0: 47.6, d49: 2, d105: 2.88, d161: 6.75, d217: 16.2, d273: 20, d329: 12.1 ... | 141 | $12,698 |
| graphite_crucible | 49 | d0: 7.62, d56: 1, d112: 1.67, d168: 3.42, d224: 1.83, d280: 1, d336: 1 ... | 21 | $9,450 |
| ni_pellet | 5 | d0: 1.58, d42: 0.25, d154: 0.257, d210: 0.528, d266: 1.06, d322: 0.25, d434: 0.25 ... | 5.39 | $2,371 |
| argon | 3 | d0: 6.06, d49: 1, d161: 1.01, d217: 2.51, d273: 3.22, d329: 1.97, d385: 1 ... | 21.9 | $1,970 |
| ded_substrate | 3 | d105: 1, d217: 1, d273: 1, d385: 1, d441: 1, d553: 1, d609: 1 ... | 8 | $1,200 |
| fe_powder | 10 | d0: 0.576, d42: 0.25, d210: 0.25, d266: 0.25, d322: 0.25, d546: 0.25 | 1.83 | $548 |

### Shared stations: `r5_vertical_parallel_fast_reorder` (use over offered unit-hours by quarter; share by campaign)

| Station kind | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Al share | binds |
|---|---|---|---|---|---|---|---|---|---|---|
| lpbf_3dpt (jobs over its standing slots) | 12% | 32% | 10% | 1% | 3% | 2% | 2% | 2% | - |  |
| mines_x2 (jobs over its standing slots) | 0% | 11% | 39% | 25% | 32% | 0% | 7% | 21% | - |  |
| utah_midi (jobs over its standing slots) | 30% | 61% | 18% | 3% | 2% | 1% | 1% | 1% | - |  |
| utah_mxlab (jobs over its standing slots) | 6% | 66% | 60% | 64% | 47% | 35% | 43% | 39% | - |  |
| valimet (jobs over its standing slots) | 0% | 0% | 6% | 8% | 12% | 10% | 12% | 8% | - |  |
| atomizer | 44% | 79% | 48% | 28% | 7% | 1% | 0% | 0% | 74% | yes |
| operator | 15% | 33% | 41% | 22% | 4% | 1% | 1% | 1% | 78% |  |
| immersion | 0% | 0% | 7% | 15% | 7% | 1% | 0% | 2% | 0% |  |
| utah_midi | 2% | 5% | 14% | 14% | 3% | 0% | 0% | 0% | 100% |  |
| doser | 9% | 8% | 13% | 9% | 2% | 0% | 0% | 0% | 83% |  |
| shop | 7% | 12% | 13% | 9% | 2% | 0% | 0% | 0% | 82% |  |
| utah_mxlab | 0% | 0% | 8% | 6% | 2% | 0% | 0% | 0% | 0% |  |
| byu_sem | 2% | 2% | 6% | 7% | 2% | 0% | 0% | 0% | 74% |  |
| prep | 1% | 1% | 4% | 5% | 1% | 0% | 0% | 0% | 67% |  |
| sieve | 2% | 2% | 5% | 3% | 1% | 0% | 0% | 0% | 81% |  |
| robot | 0% | 0% | 3% | 4% | 1% | 0% | 0% | 0% | 82% |  |
| edm | 1% | 2% | 3% | 4% | 1% | 0% | 0% | 0% | 84% |  |
| density | 1% | 1% | 2% | 2% | 0% | 0% | 0% | 0% | 100% |  |
| furnace | 0% | 0% | 1% | 2% | 0% | 0% | 0% | 0% | 91% |  |
| psd | 1% | 0% | 2% | 1% | 0% | 0% | 0% | 0% | 86% |  |
| tensile | 1% | 0% | 1% | 2% | 0% | 0% | 0% | 0% | 92% |  |
| lpbf_3dpt | 0% | 1% | 0% | 0% | 0% | 0% | 0% | 0% | 100% |  |
| ames | 0% | 0% | 0% | 1% | 0% | 0% | 1% | 0% | 0% |  |
| hardness | 0% | 0% | 0% | 1% | 0% | 0% | 0% | 0% | 0% |  |
| cubxl | 0% | 0% | 0% | 1% | 0% | 0% | 0% | 0% | 0% |  |
| pip | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| byu_icpms | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| mines_x2 | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| valimet | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 100% |  |
| nsl | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |

### Shared stations: `r5_conventional_external_fast_reorder` (use over offered unit-hours by quarter; share by campaign)

| Station kind | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Al share | binds |
|---|---|---|---|---|---|---|---|---|---|---|
| lpbf_3dpt (jobs over its standing slots) | 8% | 36% | 47% | 49% | 42% | 28% | 24% | 12% | - |  |
| mines_x2 (jobs over its standing slots) | 0% | 21% | 43% | 61% | 82% | 68% | 71% | 86% | - | yes |
| utah_midi (jobs over its standing slots) | 24% | 61% | 71% | 64% | 57% | 45% | 46% | 21% | - | yes |
| utah_mxlab (jobs over its standing slots) | 4% | 76% | 80% | 84% | 86% | 76% | 88% | 88% | - | yes |
| valimet (jobs over its standing slots) | 2% | 0% | 0% | 12% | 4% | 10% | 12% | 8% | - |  |
| atomizer | 41% | 87% | 82% | 75% | 76% | 59% | 53% | 29% | 64% | yes |
| operator | 14% | 28% | 28% | 27% | 26% | 20% | 18% | 10% | 77% |  |
| doser | 11% | 14% | 12% | 12% | 12% | 9% | 8% | 3% | 75% |  |
| shop | 8% | 11% | 10% | 10% | 10% | 7% | 7% | 3% | 75% |  |
| sieve | 2% | 5% | 5% | 4% | 4% | 3% | 3% | 1% | 82% |  |
| byu_sem | 1% | 4% | 4% | 4% | 4% | 3% | 3% | 2% | 75% |  |
| utah_midi | 1% | 4% | 4% | 4% | 3% | 3% | 3% | 1% | 100% |  |
| edm | 1% | 3% | 3% | 3% | 3% | 2% | 2% | 1% | 90% |  |
| prep | 1% | 2% | 3% | 3% | 2% | 2% | 2% | 1% | 73% |  |
| tensile | 1% | 2% | 3% | 2% | 2% | 2% | 1% | 1% | 95% |  |
| density | 1% | 2% | 2% | 2% | 2% | 1% | 1% | 1% | 100% |  |
| immersion | 0% | 0% | 1% | 1% | 2% | 2% | 2% | 1% | 0% |  |
| furnace | 0% | 1% | 2% | 1% | 1% | 1% | 1% | 0% | 94% |  |
| psd | 1% | 2% | 2% | 1% | 1% | 1% | 1% | 0% | 82% |  |
| lpbf_3dpt | 0% | 1% | 1% | 1% | 1% | 1% | 1% | 0% | 100% |  |
| utah_mxlab | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| hardness | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| mines_x2 | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| ames | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| valimet | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 100% |  |
| pip | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| cubxl | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| byu_icpms | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| nsl | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |

### Shared stations: `r5_vertical_parallel_fast_lean` (use over offered unit-hours by quarter; share by campaign)

| Station kind | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Al share | binds |
|---|---|---|---|---|---|---|---|---|---|---|
| lpbf_3dpt (jobs over its standing slots) | 1% | 12% | 4% | 1% | 3% | 1% | 1% | 1% | - |  |
| mines_x2 (jobs over its standing slots) | 0% | 28% | 28% | 28% | 36% | 7% | 4% | 18% | - |  |
| utah_midi (jobs over its standing slots) | 11% | 35% | 8% | 3% | 1% | 1% | 1% | 0% | - |  |
| utah_mxlab (jobs over its standing slots) | 25% | 70% | 56% | 60% | 51% | 35% | 25% | 23% | - |  |
| valimet (jobs over its standing slots) | 0% | 0% | 0% | 6% | 10% | 8% | 4% | 4% | - |  |
| atomizer | 38% | 68% | 35% | 44% | 10% | 2% | 1% | 0% | 76% |  |
| operator | 9% | 24% | 32% | 33% | 7% | 1% | 1% | 0% | 77% |  |
| utah_midi | 1% | 4% | 11% | 19% | 5% | 0% | 0% | 0% | 100% |  |
| doser | 7% | 5% | 11% | 15% | 3% | 1% | 0% | 0% | 85% |  |
| immersion | 0% | 0% | 5% | 15% | 10% | 1% | 0% | 1% | 0% |  |
| shop | 5% | 8% | 10% | 13% | 3% | 1% | 0% | 0% | 84% |  |
| byu_sem | 1% | 1% | 4% | 10% | 3% | 0% | 0% | 0% | 76% |  |
| prep | 0% | 1% | 3% | 7% | 2% | 0% | 0% | 0% | 67% |  |
| utah_mxlab | 0% | 0% | 7% | 6% | 2% | 0% | 0% | 0% | 0% |  |
| robot | 0% | 0% | 3% | 6% | 1% | 0% | 0% | 0% | 84% |  |
| sieve | 2% | 2% | 4% | 5% | 1% | 0% | 0% | 0% | 84% |  |
| edm | 0% | 2% | 2% | 5% | 1% | 0% | 0% | 0% | 84% |  |
| density | 0% | 0% | 1% | 3% | 1% | 0% | 0% | 0% | 100% |  |
| furnace | 0% | 0% | 1% | 2% | 1% | 0% | 0% | 0% | 91% |  |
| tensile | 0% | 0% | 1% | 2% | 1% | 0% | 0% | 0% | 91% |  |
| psd | 0% | 0% | 1% | 2% | 0% | 0% | 0% | 0% | 88% |  |
| hardness | 0% | 0% | 0% | 1% | 0% | 0% | 0% | 0% | 0% |  |
| cubxl | 0% | 0% | 0% | 1% | 0% | 0% | 0% | 0% | 0% |  |
| ames | 0% | 0% | 0% | 1% | 1% | 0% | 0% | 0% | 0% |  |
| lpbf_3dpt | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 100% |  |
| pip | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| byu_icpms | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| mines_x2 | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| valimet | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 100% |  |
| nsl | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |

### Shared stations: `r5_conventional_external_fast_lean` (use over offered unit-hours by quarter; share by campaign)

| Station kind | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Al share | binds |
|---|---|---|---|---|---|---|---|---|---|---|
| lpbf_3dpt (jobs over its standing slots) | 2% | 12% | 24% | 25% | 30% | 25% | 33% | 31% | - |  |
| mines_x2 (jobs over its standing slots) | 0% | 21% | 57% | 43% | 68% | 82% | 61% | 75% | - | yes |
| utah_midi (jobs over its standing slots) | 10% | 35% | 47% | 50% | 50% | 46% | 51% | 50% | - |  |
| utah_mxlab (jobs over its standing slots) | 14% | 72% | 82% | 68% | 84% | 76% | 82% | 70% | - | yes |
| valimet (jobs over its standing slots) | 0% | 4% | 0% | 2% | 4% | 2% | 6% | 6% | - |  |
| atomizer | 36% | 78% | 62% | 59% | 64% | 62% | 60% | 59% | 63% | yes |
| operator | 9% | 21% | 20% | 21% | 22% | 21% | 21% | 21% | 76% |  |
| doser | 7% | 12% | 9% | 11% | 11% | 9% | 10% | 9% | 73% |  |
| shop | 5% | 10% | 7% | 9% | 9% | 8% | 8% | 8% | 74% |  |
| sieve | 2% | 4% | 3% | 3% | 3% | 4% | 3% | 3% | 81% |  |
| byu_sem | 1% | 3% | 3% | 3% | 3% | 3% | 3% | 3% | 73% |  |
| utah_midi | 1% | 2% | 3% | 3% | 3% | 3% | 3% | 3% | 100% |  |
| edm | 0% | 1% | 2% | 2% | 2% | 2% | 2% | 2% | 89% |  |
| prep | 0% | 1% | 2% | 2% | 2% | 2% | 2% | 2% | 71% |  |
| tensile | 0% | 1% | 2% | 2% | 2% | 2% | 2% | 2% | 94% |  |
| immersion | 0% | 0% | 1% | 1% | 1% | 1% | 2% | 2% | 0% |  |
| density | 0% | 1% | 1% | 1% | 1% | 1% | 1% | 1% | 100% |  |
| psd | 1% | 1% | 1% | 1% | 1% | 1% | 1% | 1% | 81% |  |
| furnace | 0% | 1% | 1% | 1% | 1% | 1% | 1% | 1% | 94% |  |
| lpbf_3dpt | 0% | 0% | 1% | 1% | 1% | 1% | 1% | 1% | 100% |  |
| utah_mxlab | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| ames | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| mines_x2 | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| hardness | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| pip | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| valimet | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 100% |  |
| cubxl | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| byu_icpms | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |
| nsl | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |  |

## Idle stretches (note 3): at least 7 days with no start at a campaign's pacing station

| Arm | Campaign, station | stretches per seed | idle days per seed | by cause (days per seed) | flagged |
|---|---|---|---|---|---|
| `r5_conventional_external_bofn3_lean` | Aluminium, atomizer | 13.1 | 273 | WIP limit (lots already waiting for the first fabrication step) 267, capacity (station busy) 6 | 0 |
| `r5_conventional_external_bofn3_lean` | Aluminium, first fabrication step | 23.6 | 544 | WIP limit (lots already waiting for the first fabrication step) 337, capacity (station busy) 207 | 0 |
| `r5_conventional_external_bofn3_lean` | Copper, atomizer | 9.8 | 505 | capacity (station busy) 482, policy waiting (results in flight) 22 | 5 |
| `r5_conventional_external_bofn3_lean` | Copper, first fabrication step | 22.6 | 699 | capacity (station busy) 661, policy waiting (results in flight) 37, decision time 2 | 14 |
| `r5_conventional_external_bofn3_reorder` | Aluminium, atomizer | 8.3 | 192 | WIP limit (lots already waiting for the first fabrication step) 179, capacity (station busy) 7, policy waiting 5, money 1 | 3 |
| `r5_conventional_external_bofn3_reorder` | Aluminium, first fabrication step | 21.9 | 485 | capacity (station busy) 274, WIP limit (lots already waiting for the first fabrication step) 203, policy waiting 7, money 1 | 2 |
| `r5_conventional_external_bofn3_reorder` | Copper, atomizer | 9.8 | 464 | capacity (station busy) 425, policy waiting (results in flight) 38, decision time 1 | 6 |
| `r5_conventional_external_bofn3_reorder` | Copper, first fabrication step | 23.8 | 698 | capacity (station busy) 655, policy waiting (results in flight) 40, decision time 2 | 14 |
| `r5_conventional_external_fast_lean` | Aluminium, atomizer | 14.7 | 277 | WIP limit (lots already waiting for the first fabrication step) 229, capacity (station busy) 44, money 4 | 0 |
| `r5_conventional_external_fast_lean` | Aluminium, first fabrication step | 23.0 | 396 | WIP limit (lots already waiting for the first fabrication step) 224, capacity (station busy) 170, money 3 | 0 |
| `r5_conventional_external_fast_lean` | Copper, atomizer | 9.2 | 290 | capacity (station busy) 218, WIP limit (lots already waiting for the first fabrication step) 71 | 0 |
| `r5_conventional_external_fast_lean` | Copper, first fabrication step | 21.2 | 699 | capacity (station busy) 619, WIP limit (lots already waiting for the first fabrication step) 80 | 0 |
| `r5_conventional_external_fast_reorder` | Aluminium, atomizer | 8.1 | 241 | WIP limit (lots already waiting for the first fabrication step) 107, money 80, money (the last few thousand dollars, held for the partners' slots) 31, capacity (station busy) 20, policy waiting (results in flight) 3 | 0 |
| `r5_conventional_external_fast_reorder` | Aluminium, first fabrication step | 18.6 | 351 | capacity (station busy) 137, WIP limit (lots already waiting for the first fabrication step) 121, money 66, money (the last few thousand dollars, held for the partners' slots) 26, policy waiting (results in flight) 2 | 0 |
| `r5_conventional_external_fast_reorder` | Copper, atomizer | 9.1 | 287 | capacity (station busy) 204, WIP limit (lots already waiting for the first fabrication step) 83 | 0 |
| `r5_conventional_external_fast_reorder` | Copper, first fabrication step | 23.2 | 697 | capacity (station busy) 584, WIP limit (lots already waiting for the first fabrication step) 113, money 0 | 0 |
| `r5_conventional_external_fast_reorder_hpc-add_per_day256-keep512` | Aluminium, atomizer | 8.2 | 236 | WIP limit (lots already waiting for the first fabrication step) 96, money 92, money (the last few thousand dollars, held for the partners' slots) 31, capacity (station busy) 17 | 0 |
| `r5_conventional_external_fast_reorder_hpc-add_per_day256-keep512` | Aluminium, first fabrication step | 20.2 | 358 | capacity (station busy) 152, WIP limit (lots already waiting for the first fabrication step) 122, money 60, money (the last few thousand dollars, held for the partners' slots) 24 | 0 |
| `r5_conventional_external_fast_reorder_hpc-add_per_day256-keep512` | Copper, atomizer | 9.2 | 288 | capacity (station busy) 203, WIP limit (lots already waiting for the first fabrication step) 85 | 0 |
| `r5_conventional_external_fast_reorder_hpc-add_per_day256-keep512` | Copper, first fabrication step | 23.4 | 696 | capacity (station busy) 582, WIP limit (lots already waiting for the first fabrication step) 114 | 0 |
| `r5_conventional_external_pkgfn3_lean` | Aluminium, atomizer | 13.6 | 268 | WIP limit (lots already waiting for the first fabrication step) 260, capacity (station busy) 8 | 0 |
| `r5_conventional_external_pkgfn3_lean` | Aluminium, first fabrication step | 23.9 | 549 | WIP limit (lots already waiting for the first fabrication step) 329, capacity (station busy) 220 | 0 |
| `r5_conventional_external_pkgfn3_lean` | Copper, atomizer | 9.2 | 504 | capacity (station busy) 481, policy waiting (results in flight) 23 | 6 |
| `r5_conventional_external_pkgfn3_lean` | Copper, first fabrication step | 22.1 | 703 | capacity (station busy) 668, policy waiting (results in flight) 33, decision time 2 | 12 |
| `r5_conventional_external_pkgfn3_reorder` | Aluminium, atomizer | 8.5 | 192 | WIP limit (lots already waiting for the first fabrication step) 184, capacity (station busy) 8 | 0 |
| `r5_conventional_external_pkgfn3_reorder` | Aluminium, first fabrication step | 22.1 | 476 | capacity (station busy) 262, WIP limit (lots already waiting for the first fabrication step) 215 | 0 |
| `r5_conventional_external_pkgfn3_reorder` | Copper, atomizer | 9.9 | 465 | capacity (station busy) 430, policy waiting (results in flight) 35 | 5 |
| `r5_conventional_external_pkgfn3_reorder` | Copper, first fabrication step | 23.2 | 697 | capacity (station busy) 662, policy waiting (results in flight) 33, decision time 2 | 11 |
| `r5_vertical_external_fast_reorder` | Aluminium, atomizer | 8.6 | 264 | money 103, WIP limit (lots already waiting for the first fabrication step) 91, money (the last few thousand dollars, held for the partners' slots) 38, capacity (station busy) 23, policy waiting 8 | 0 |
| `r5_vertical_external_fast_reorder` | Aluminium, first fabrication step | 18.9 | 360 | capacity (station busy) 138, WIP limit (lots already waiting for the first fabrication step) 106, money 68, money (the last few thousand dollars, held for the partners' slots) 40, policy waiting 4 | 0 |
| `r5_vertical_external_fast_reorder` | Copper, atomizer | 8.8 | 278 | capacity (station busy) 184, WIP limit (lots already waiting for the first fabrication step) 94 | 0 |
| `r5_vertical_external_fast_reorder` | Copper, first fabrication step | 23.0 | 700 | capacity (station busy) 584, WIP limit (lots already waiting for the first fabrication step) 116 | 0 |
| `r5_vertical_parallel_fast_lean` | Aluminium, atomizer | 13.1 | 405 | money (the last few thousand dollars, held for the partners' slots) 245, WIP limit (lots already waiting for the first fabrication step) 101, money 54, capacity (station busy) 3, policy waiting (results in flight) 1 | 0 |
| `r5_vertical_parallel_fast_lean` | Aluminium, first fabrication step | 13.8 | 454 | money (the last few thousand dollars, held for the partners' slots) 246, WIP limit (lots already waiting for the first fabrication step) 108, capacity (station busy) 56, money 44, policy waiting (results in flight) 1 | 0 |
| `r5_vertical_parallel_fast_lean` | Copper, atomizer | 14.0 | 533 | money 371, capacity (station busy) 72, WIP limit (lots already waiting for the first fabrication step) 67, money (the last few thousand dollars, held for the partners' slots) 21, sign-off 2 | 0 |
| `r5_vertical_parallel_fast_lean` | Copper, first fabrication step | 14.5 | 599 | money 331, capacity (station busy) 170, WIP limit (lots already waiting for the first fabrication step) 80, money (the last few thousand dollars, held for the partners' slots) 17, sign-off 1 | 0 |
| `r5_vertical_parallel_fast_reorder` | Aluminium, atomizer | 10.6 | 409 | money (the last few thousand dollars, held for the partners' slots) 299, WIP limit (lots already waiting for the first fabrication step) 57, money 48, capacity (station busy) 6 | 0 |
| `r5_vertical_parallel_fast_reorder` | Aluminium, first fabrication step | 10.4 | 412 | money (the last few thousand dollars, held for the partners' slots) 281, WIP limit (lots already waiting for the first fabrication step) 60, capacity (station busy) 39, money 28, policy waiting (results in flight) 3 | 0 |
| `r5_vertical_parallel_fast_reorder` | Copper, atomizer | 13.1 | 559 | money 396, WIP limit (lots already waiting for the first fabrication step) 94, capacity (station busy) 66, sign-off 3, money (the last few thousand dollars, held for the partners' slots) 1 | 0 |
| `r5_vertical_parallel_fast_reorder` | Copper, first fabrication step | 14.7 | 609 | money 358, capacity (station busy) 133, WIP limit (lots already waiting for the first fabrication step) 116, money (the last few thousand dollars, held for the partners' slots) 2, sign-off 0 | 0 |
| `r5_vertical_parallel_fast_reorder_hpc-add_per_day256-keep512` | Aluminium, atomizer | 11.1 | 415 | money (the last few thousand dollars, held for the partners' slots) 299, WIP limit (lots already waiting for the first fabrication step) 58, money 33, policy waiting 19, capacity (station busy) 6 | 0 |
| `r5_vertical_parallel_fast_reorder_hpc-add_per_day256-keep512` | Aluminium, first fabrication step | 10.6 | 421 | money (the last few thousand dollars, held for the partners' slots) 291, WIP limit (lots already waiting for the first fabrication step) 59, capacity (station busy) 40, money 15, policy waiting 14 | 1 |
| `r5_vertical_parallel_fast_reorder_hpc-add_per_day256-keep512` | Copper, atomizer | 13.2 | 565 | money 404, WIP limit (lots already waiting for the first fabrication step) 94, capacity (station busy) 66, sign-off 0 | 0 |
| `r5_vertical_parallel_fast_reorder_hpc-add_per_day256-keep512` | Copper, first fabrication step | 15.5 | 604 | money 355, capacity (station busy) 135, WIP limit (lots already waiting for the first fabrication step) 115 | 0 |
| `r5_vertical_wait_fast_reorder` | Aluminium, atomizer | 9.8 | 506 | not asked (before start) 262, money 165, policy waiting (results in flight) 30, WIP limit (lots already waiting for the first fabrication step) 27, policy waiting 11 | 0 |
| `r5_vertical_wait_fast_reorder` | Aluminium, first fabrication step | 9.5 | 492 | not asked (before start) 274, money 153, policy waiting (results in flight) 27, policy waiting 14, capacity (station busy) 14 | 0 |
| `r5_vertical_wait_fast_reorder` | Copper, atomizer | 9.9 | 635 | money 336, not asked (before start) 283, sign-off 11, capacity (station busy) 5 | 0 |
| `r5_vertical_wait_fast_reorder` | Copper, first fabrication step | 7.2 | 618 | money 329, not asked (before start) 285, sign-off 3, capacity (station busy) 1 | 0 |

## Counters (mean per run)

| Arm | Campaign | designed | lots made | alloys made | alloys printed or deposited | alloys tested | tests |
|---|---|---|---|---|---|---|---|
| `r5_conventional_external_bofn3_lean` | Aluminium | 46771 | 167 | 167 | 52 | 22 | 22 |
| `r5_conventional_external_bofn3_lean` | Copper | 43228 | 12 | 20 | 18 | 3 | 3 |
| `r5_conventional_external_bofn3_reorder` | Aluminium | 46771 | 204 | 204 | 64 | 34 | 34 |
| `r5_conventional_external_bofn3_reorder` | Copper | 43228 | 13 | 21 | 18 | 3 | 3 |
| `r5_conventional_external_fast_lean` | Aluminium | 46838 | 164 | 110 | 71 | 66 | 105 |
| `r5_conventional_external_fast_lean` | Copper | 43411 | 33 | 33 | 16 | 5 | 5 |
| `r5_conventional_external_fast_reorder` | Aluminium | 46841 | 179 | 119 | 84 | 76 | 120 |
| `r5_conventional_external_fast_reorder` | Copper | 43411 | 33 | 33 | 17 | 5 | 5 |
| `r5_conventional_external_fast_reorder_hpc-add_per_day256-keep512` | Aluminium | 186993 | 179 | 120 | 84 | 78 | 120 |
| `r5_conventional_external_fast_reorder_hpc-add_per_day256-keep512` | Copper | 164116 | 33 | 33 | 16 | 6 | 6 |
| `r5_conventional_external_pkgfn3_lean` | Aluminium | 46771 | 168 | 168 | 52 | 28 | 28 |
| `r5_conventional_external_pkgfn3_lean` | Copper | 43228 | 11 | 19 | 17 | 3 | 3 |
| `r5_conventional_external_pkgfn3_reorder` | Aluminium | 46771 | 203 | 203 | 63 | 38 | 38 |
| `r5_conventional_external_pkgfn3_reorder` | Copper | 43228 | 13 | 21 | 18 | 4 | 4 |
| `r5_vertical_external_fast_reorder` | Aluminium | 46835 | 172 | 115 | 84 | 76 | 120 |
| `r5_vertical_external_fast_reorder` | Copper | 43411 | 34 | 33 | 17 | 5 | 5 |
| `r5_vertical_parallel_fast_lean` | Aluminium | 46955 | 364 | 235 | 177 | 166 | 270 |
| `r5_vertical_parallel_fast_lean` | Copper | 43411 | 41 | 41 | 37 | 21 | 21 |
| `r5_vertical_parallel_fast_reorder` | Aluminium | 46927 | 319 | 207 | 163 | 153 | 248 |
| `r5_vertical_parallel_fast_reorder` | Copper | 43411 | 42 | 42 | 36 | 19 | 20 |
| `r5_vertical_parallel_fast_reorder_hpc-add_per_day256-keep512` | Aluminium | 187076 | 314 | 204 | 165 | 154 | 249 |
| `r5_vertical_parallel_fast_reorder_hpc-add_per_day256-keep512` | Copper | 164116 | 42 | 42 | 35 | 19 | 19 |
| `r5_vertical_wait_fast_reorder` | Aluminium | 46972 | 390 | 251 | 177 | 168 | 271 |
| `r5_vertical_wait_fast_reorder` | Copper | 43411 | 44 | 44 | 38 | 23 | 23 |

## The HPC stream (note 4)

| Arm | cores | candidates a day (allocation) | evaluated, Al | seen by the policy, Al | evaluated, Cu | seen, Cu | policies' own simulation hours (Al, Cu) |
|---|---|---|---|---|---|---|---|
| `r5_conventional_external_bofn3_lean` | 256 | 122,880 | 89,707,520 | 46,720 | 89,707,520 | 43,182 | 3, 3 |
| `r5_conventional_external_bofn3_reorder` | 256 | 122,880 | 89,707,520 | 46,720 | 89,707,520 | 43,182 | 3, 3 |
| `r5_conventional_external_fast_lean` | 256 | 122,880 | 89,707,520 | 46,720 | 89,707,520 | 43,182 | 0, 13 |
| `r5_conventional_external_fast_reorder` | 256 | 122,880 | 89,707,520 | 46,720 | 89,707,520 | 43,182 | 0, 13 |
| `r5_conventional_external_fast_reorder_hpc-add_per_day256-keep512` | 256 | 122,880 | 89,707,520 | 186,873 | 89,707,520 | 163,901 | 0, 13 |
| `r5_conventional_external_pkgfn3_lean` | 256 | 122,880 | 89,707,520 | 46,720 | 89,707,520 | 43,182 | 3, 3 |
| `r5_conventional_external_pkgfn3_reorder` | 256 | 122,880 | 89,707,520 | 46,720 | 89,707,520 | 43,182 | 3, 3 |
| `r5_vertical_external_fast_reorder` | 256 | 122,880 | 89,707,520 | 46,720 | 89,707,520 | 43,182 | 0, 13 |
| `r5_vertical_parallel_fast_lean` | 256 | 122,880 | 89,707,520 | 46,720 | 89,707,520 | 43,182 | 0, 13 |
| `r5_vertical_parallel_fast_reorder` | 256 | 122,880 | 89,707,520 | 46,720 | 89,707,520 | 43,182 | 0, 13 |
| `r5_vertical_parallel_fast_reorder_hpc-add_per_day256-keep512` | 256 | 122,880 | 89,707,520 | 186,873 | 89,707,520 | 163,901 | 0, 13 |
| `r5_vertical_wait_fast_reorder` | 256 | 122,880 | 89,707,520 | 46,720 | 89,707,520 | 43,182 | 0, 13 |

Four times the candidates the policies see (512 kept, 256 new a day) against the nominal pool (128, 64 a day): factor (nominal's median over the bigger pool's); seeds there (bigger vs nominal)

| Lab | Target | factor |
|---|---|---|
| vertical | Aluminium T1 | 1.0x (1.0-1.0); 16/16 vs 16/16 |
| vertical | Aluminium T2 | >= 2.1x; 8/16 vs 7/16 |
| vertical | Copper T1 | 0.9x (0.8-1.1); 15/16 vs 15/16 |
| vertical | Copper T2 | 1.0x (0.8-1.1); 15/16 vs 15/16 |
| conventional | Aluminium T1 | 1.0x (1.0-1.5); 16/16 vs 16/16 |
| conventional | Aluminium T2 | 1.4x (0-∞); 9/16 vs 8/16 |
| conventional | Copper T1 | 1.1x (0.9-∞); 14/16 vs 11/16 |
| conventional | Copper T2 | 1.3x (0-∞); 10/16 vs 9/16 |

## Median seed for both campaigns together (for a continuous replay)

| Arm | seed | Al T1, T2 (median) | Cu T1, T2 (median) | event log |
|---|---|---|---|---|
| `r5_conventional_external_bofn3_lean` | 12 | 339, 417 (310, 383) | 730, 730 (730, 730) | `out/twin5/events/r5_conventional_external_bofn3_lean_s12.json.xz` |
| `r5_conventional_external_bofn3_reorder` | 14 | 214, 214 (217, 241) | 730, 730 (730, 730) | `out/twin5/events/r5_conventional_external_bofn3_reorder_s14.json.xz` |
| `r5_conventional_external_fast_lean` | 12 | 115, 730 (137, 712) | 451, 451 (462, 548) | `out/twin5/events/r5_conventional_external_fast_lean_s12.json.xz` |
| `r5_conventional_external_fast_lean_dec-none` | 6 | 137, 730 (133, 730) | 614, 730 (487, 581) | `out/twin5/events/r5_conventional_external_fast_lean_s6_dec-none.json.xz` |
| `r5_conventional_external_fast_lean_dec-slow` | 3 | 149, 730 (161, 730) | 730, 730 (563, 730) | `out/twin5/events/r5_conventional_external_fast_lean_s3_dec-slow.json.xz` |
| `r5_conventional_external_fast_reorder` | 11 | 134, 730 (99, 646) | 695, 730 (540, 681) | `out/twin5/events/r5_conventional_external_fast_reorder_s11.json.xz` |
| `r5_conventional_external_fast_reorder_dec-none` | 5 | 88, 326 (108, 509) | 401, 401 (413, 428) | `out/twin5/events/r5_conventional_external_fast_reorder_s5_dec-none.json.xz` |
| `r5_conventional_external_fast_reorder_dec-slow` | 8 | 80, 730 (98, 629) | 435, 435 (418, 538) | `out/twin5/events/r5_conventional_external_fast_reorder_s8_dec-slow.json.xz` |
| `r5_conventional_external_fast_reorder_hpc-add_per_day256-keep512` | 12 | 92, 610 (92, 501) | 428, 428 (412, 545) | `out/twin5/events/r5_conventional_external_fast_reorder_s12_hpc-add_per_day256-keep512.json.xz` |
| `r5_conventional_external_pkgfn3_lean` | 8 | 319, 344 (315, 348) | 730, 730 (723, 730) | `out/twin5/events/r5_conventional_external_pkgfn3_lean_s8.json.xz` |
| `r5_conventional_external_pkgfn3_reorder` | 5 | 218, 305 (220, 295) | 730, 730 (730, 730) | `out/twin5/events/r5_conventional_external_pkgfn3_reorder_s5.json.xz` |
| `r5_vertical_external_fast_reorder` | 8 | 80, 399 (87, 422) | 475, 475 (454, 627) | `out/twin5/events/r5_vertical_external_fast_reorder_s8.json.xz` |
| `r5_vertical_parallel_fast_lean` | 12 | 122, 444 (135, 405) | 262, 262 (283, 295) | `out/twin5/events/r5_vertical_parallel_fast_lean_s12.json.xz` |
| `r5_vertical_parallel_fast_lean_atom-3h` | 12 | 122, 400 (135, 565) | 272, 272 (276, 287) | `out/twin5/events/r5_vertical_parallel_fast_lean_s12_atom-3h.json.xz` |
| `r5_vertical_parallel_fast_lean_atom-slow` | 12 | 122, 730 (135, 730) | 269, 269 (282, 293) | `out/twin5/events/r5_vertical_parallel_fast_lean_s12_atom-slow.json.xz` |
| `r5_vertical_parallel_fast_lean_dec-none` | 11 | 140, 730 (137, 730) | 281, 326 (278, 292) | `out/twin5/events/r5_vertical_parallel_fast_lean_s11_dec-none.json.xz` |
| `r5_vertical_parallel_fast_lean_dec-slow` | 4 | 115, 730 (128, 730) | 256, 257 (284, 304) | `out/twin5/events/r5_vertical_parallel_fast_lean_s4_dec-slow.json.xz` |
| `r5_vertical_parallel_fast_reorder` | 8 | 75, 730 (87, 730) | 295, 365 (288, 323) | `out/twin5/events/r5_vertical_parallel_fast_reorder_s8.json.xz` |
| `r5_vertical_parallel_fast_reorder_atom-3h` | 8 | 75, 730 (87, 730) | 295, 346 (282, 322) | `out/twin5/events/r5_vertical_parallel_fast_reorder_s8_atom-3h.json.xz` |
| `r5_vertical_parallel_fast_reorder_atom-slow` | 8 | 74, 730 (87, 535) | 303, 365 (293, 325) | `out/twin5/events/r5_vertical_parallel_fast_reorder_s8_atom-slow.json.xz` |
| `r5_vertical_parallel_fast_reorder_dec-none` | 14 | 113, 279 (87, 280) | 281, 281 (282, 311) | `out/twin5/events/r5_vertical_parallel_fast_reorder_s14_dec-none.json.xz` |
| `r5_vertical_parallel_fast_reorder_dec-slow` | 13 | 91, 91 (102, 331) | 300, 300 (300, 321) | `out/twin5/events/r5_vertical_parallel_fast_reorder_s13_dec-slow.json.xz` |
| `r5_vertical_parallel_fast_reorder_hpc-add_per_day256-keep512` | 11 | 57, 730 (86, 539) | 320, 320 (303, 312) | `out/twin5/events/r5_vertical_parallel_fast_reorder_s11_hpc-add_per_day256-keep512.json.xz` |
| `r5_vertical_parallel_fast_reorder_noused` | 8 | 75, 730 (87, 730) | 309, 351 (291, 311) | `out/twin5/events/r5_vertical_parallel_fast_reorder_s8_noused.json.xz` |
| `r5_vertical_wait_fast_reorder` | 11 | 293, 730 (280, 730) | 383, 383 (362, 382) | `out/twin5/events/r5_vertical_wait_fast_reorder_s11.json.xz` |
