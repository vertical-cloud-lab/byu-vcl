
**main**

| setting | n | FLAIME best new (± SE) | hit T1 | median days to T1 | median $ to T1 | ONR best new (± SE) | hit T1 | median days to T1 | median $ to T1 | s/run |
|---|---|---|---|---|---|---|---|---|---|---|
| vertical_lab_bofn_blend | 12 | 0.687 ± 0.015 | 100% | 116 | $39k | 0.674 ± 0.009 | 100% | 225 | $50k | 231 |
| vertical_lab_bofn | 12 | 0.650 ± 0.034 | 92% | 123 | $40k | 0.327 ± 0.086 | 25% | 141 | $39k | 116 |
| vertical_lab_gpbo | 12 | 0.455 ± 0.066 | 83% | 185 | $44k | 0.529 ± 0.056 | 67% | 184 | $50k | 17 |
| vertical_lab_cost_aware | 12 | 0.552 ± 0.076 | 83% | 48 | $22k | 0.633 ± 0.015 | 92% | 74 | $31k | 19 |
| vertical_lab_random | 12 | 0.102 ± 0.060 | 8% | 61 | $24k | 0.347 ± 0.083 | 33% | 91 | $38k | 2 |
| vertical_lab_sobol | 12 | 0.105 ± 0.049 | 8% | 11 | $15k | 0.447 ± 0.054 | 25% | 134 | $42k | 2 |
| vertical_lab_heuristic | 12 | 0.605 ± 0.017 | 100% | 37 | $20k | 0.585 ± 0.023 | 58% | 127 | $43k | 4 |
| vertical_lab_tiered | 12 | 0.338 ± 0.090 | 58% | 60 | $17k | 0.686 ± 0.016 | 92% | 88 | $32k | 2 |

**conventional**

| setting | n | FLAIME best new (± SE) | hit T1 | median days to T1 | median $ to T1 | ONR best new (± SE) | hit T1 | median days to T1 | median $ to T1 | s/run |
|---|---|---|---|---|---|---|---|---|---|---|
| proposed_bofn_stock-lean | 12 | 0.743 ± 0.008 | 100% | 220 | $61k | 0.546 ± 0.029 | 50% | 484 | $69k | 336 |
| proposed_gpbo_stock-lean | 12 | 0.520 ± 0.077 | 75% | 334 | $83k | 0.642 ± 0.021 | 92% | 692 | $88k | 37 |
| proposed_random_stock-lean | 12 | 0.389 ± 0.085 | 67% | 425 | $102k | 0.617 ± 0.028 | 75% | 551 | $88k | 4 |
| proposed_sobol_stock-lean | 12 | 0.272 ± 0.070 | 25% | 436 | $99k | 0.567 ± 0.020 | 58% | 397 | $62k | 4 |
| proposed_heuristic_stock-lean | 12 | 0.675 ± 0.014 | 100% | 123 | $32k | 0.642 ± 0.012 | 100% | 490 | $64k | 9 |
| proposed_tiered_stock-lean | 12 | 0.338 ± 0.090 | 58% | 163 | $23k | 0.706 ± 0.010 | 100% | 334 | $46k | 4 |

**lite**

| setting | n | FLAIME best new (± SE) | hit T1 | median days to T1 | median $ to T1 | ONR best new (± SE) | hit T1 | median days to T1 | median $ to T1 | s/run |
|---|---|---|---|---|---|---|---|---|---|---|
| vertical_lab_bofn_fidelity-lite | 3 | 0.665 ± 0.048 | 100% | 136 | $44k | 0.363 ± 0.197 | 33% | 167 | $50k | 320 |
| vertical_lab_heuristic_fidelity-lite | 3 | 0.546 ± 0.037 | 100% | 50 | $21k | 0.545 ± 0.062 | 33% | 128 | $38k | 26 |

**cu_hidden**

| setting | n | FLAIME best new (± SE) | hit T1 | median days to T1 | median $ to T1 | ONR best new (± SE) | hit T1 | median days to T1 | median $ to T1 | s/run |
|---|---|---|---|---|---|---|---|---|---|---|
| vertical_lab_bofn_blend_cu_hidden-1.0 | 12 | 0.695 ± 0.017 | 100% | 107 | $35k | 0.552 ± 0.077 | 75% | 226 | $51k | 359 |
| vertical_lab_bofn_cu_hidden-1.0 | 12 | 0.665 ± 0.035 | 92% | 123 | $40k | 0.291 ± 0.089 | 25% | 141 | $39k | 207 |
| vertical_lab_gpbo_cu_hidden-1.0 | 12 | 0.455 ± 0.066 | 83% | 185 | $44k | 0.529 ± 0.056 | 67% | 184 | $50k | 20 |
| vertical_lab_cost_aware_cu_hidden-1.0 | 12 | 0.552 ± 0.076 | 83% | 48 | $22k | 0.633 ± 0.015 | 92% | 74 | $31k | 20 |
| vertical_lab_random_cu_hidden-1.0 | 12 | 0.102 ± 0.060 | 8% | 61 | $24k | 0.347 ± 0.083 | 33% | 91 | $38k | 2 |
| vertical_lab_tiered_cu_hidden-1.0 | 12 | 0.338 ± 0.090 | 58% | 60 | $17k | 0.686 ± 0.016 | 92% | 88 | $32k | 2 |
| vertical_lab_heuristic_cu_hidden-1.0 | 12 | 0.605 ± 0.017 | 100% | 37 | $20k | 0.585 ± 0.023 | 58% | 127 | $43k | 4 |

**cu_proxy**

| setting | n | FLAIME best new (± SE) | hit T1 | median days to T1 | median $ to T1 | ONR best new (± SE) | hit T1 | median days to T1 | median $ to T1 | s/run |
|---|---|---|---|---|---|---|---|---|---|---|
| vertical_lab_tiered_mis | 12 | 0.302 ± 0.093 | 50% | 39 | $14k | 0.707 ± 0.011 | 100% | 69 | $30k | 2 |
| vertical_lab_tiered_mis_cu_hidden-1.0 | 12 | 0.302 ± 0.093 | 50% | 39 | $14k | 0.707 ± 0.011 | 100% | 69 | $30k | 2 |