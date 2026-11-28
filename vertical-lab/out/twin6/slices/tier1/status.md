# Round 6 plan `tier1`: status after workflow run 46111337979

2 of 192 runs have rows (2 new in this wave); 40 are waiting on a checkpoint and 150 have neither. Everything is simulated.

**To carry on:** dispatch the workflow again with the same branch and plan and `resume_run_id` = `46111337979`: each job restores its checkpoints from this run's `ckpt-...` artifacts and carries those runs on first.

## Waiting on a checkpoint

| Job | Run | Stopped at day |
|---|---|---|
| 2 | `r6_vertical_parallel_pkgfn3_lean_s1` | 551 |
| 2 | `r6_vertical_parallel_pkgfn3_reorder_s1` | 579 |
| 2 | `r6_vertical_parallel_bofn3_lean_s1` | 510 |
| 2 | `r6_vertical_parallel_bofn3_reorder_s1` | 528 |
| 3 | `r6_vertical_parallel_pkgfn3_lean_s10` | 555 |
| 3 | `r6_vertical_parallel_pkgfn3_reorder_s10` | 654 |
| 3 | `r6_vertical_parallel_bofn3_lean_s10` | 519 |
| 3 | `r6_vertical_parallel_bofn3_reorder_s10` | 639 |
| 4 | `r6_vertical_parallel_pkgfn3_lean_s11` | 641 |
| 4 | `r6_vertical_parallel_pkgfn3_reorder_s11` | 640 |
| 4 | `r6_vertical_parallel_bofn3_lean_s11` | 539 |
| 4 | `r6_vertical_parallel_bofn3_reorder_s11` | 601 |
| 5 | `r6_vertical_parallel_pkgfn3_lean_s12` | 613 |
| 5 | `r6_vertical_parallel_pkgfn3_reorder_s12` | 662 |
| 5 | `r6_vertical_parallel_bofn3_lean_s12` | 555 |
| 5 | `r6_vertical_parallel_bofn3_reorder_s12` | 605 |
| 6 | `r6_vertical_parallel_pkgfn3_lean_s13` | 667 |
| 6 | `r6_vertical_parallel_pkgfn3_reorder_s13` | 671 |
| 6 | `r6_vertical_parallel_bofn3_lean_s13` | 567 |
| 6 | `r6_vertical_parallel_bofn3_reorder_s13` | 641 |
| 7 | `r6_vertical_parallel_pkgfn3_lean_s14` | 577 |
| 7 | `r6_vertical_parallel_pkgfn3_reorder_s14` | 620 |
| 7 | `r6_vertical_parallel_bofn3_lean_s14` | 523 |
| 7 | `r6_vertical_parallel_bofn3_reorder_s14` | 564 |
| 8 | `r6_vertical_parallel_pkgfn3_lean_s15` | 568 |
| 8 | `r6_vertical_parallel_pkgfn3_reorder_s15` | 552 |
| 8 | `r6_vertical_parallel_bofn3_lean_s15` | 467 |
| 8 | `r6_vertical_parallel_bofn3_reorder_s15` | 515 |
| 10 | `r6_vertical_parallel_pkgfn3_lean_s3` | 660 |
| 10 | `r6_vertical_parallel_pkgfn3_reorder_s3` | 629 |
| 10 | `r6_vertical_parallel_bofn3_lean_s3` | 548 |
| 10 | `r6_vertical_parallel_bofn3_reorder_s3` | 600 |
| 14 | `r6_vertical_parallel_pkgfn3_lean_s7` | 531 |
| 14 | `r6_vertical_parallel_pkgfn3_reorder_s7` | 550 |
| 14 | `r6_vertical_parallel_bofn3_lean_s7` | 448 |
| 14 | `r6_vertical_parallel_bofn3_reorder_s7` | 516 |
| 15 | `r6_vertical_parallel_pkgfn3_reorder_s8` | 693 |
| 15 | `r6_vertical_parallel_bofn3_lean_s8` | 567 |
| 15 | `r6_vertical_parallel_bofn3_reorder_s8` | 682 |
| 15 | `r6_conventional_external_pkgfn3_reorder_s8` | 400 |

## No row and no checkpoint

| Job | Run | Why |
|---|---|---|
| 1 | `r6_vertical_parallel_pkgfn3_lean_s0` | no row, no checkpoint |
| 1 | `r6_vertical_parallel_pkgfn3_reorder_s0` | no row, no checkpoint |
| 1 | `r6_vertical_parallel_bofn3_lean_s0` | no row, no checkpoint |
| 1 | `r6_vertical_parallel_bofn3_reorder_s0` | no row, no checkpoint |
| 1 | `r6_conventional_external_pkgfn3_lean_s0` | no row, no checkpoint |
| 1 | `r6_conventional_external_pkgfn3_reorder_s0` | no row, no checkpoint |
| 1 | `r6_conventional_external_bofn3_lean_s0` | no row, no checkpoint |
| 1 | `r6_conventional_external_bofn3_reorder_s0` | no row, no checkpoint |
| 1 | `r6_vertical_parallel_fast_lean_s0` | no row, no checkpoint |
| 1 | `r6_vertical_parallel_fast_reorder_s0` | no row, no checkpoint |
| 1 | `r6_conventional_external_fast_lean_s0` | no row, no checkpoint |
| 1 | `r6_conventional_external_fast_reorder_s0` | no row, no checkpoint |
| 2 | `r6_conventional_external_pkgfn3_lean_s1` | not started |
| 2 | `r6_conventional_external_pkgfn3_reorder_s1` | not started |
| 2 | `r6_conventional_external_bofn3_lean_s1` | not started |
| 2 | `r6_conventional_external_bofn3_reorder_s1` | not started |
| 2 | `r6_vertical_parallel_fast_lean_s1` | not started |
| 2 | `r6_vertical_parallel_fast_reorder_s1` | not started |
| 2 | `r6_conventional_external_fast_lean_s1` | not started |
| 2 | `r6_conventional_external_fast_reorder_s1` | not started |
| 3 | `r6_conventional_external_pkgfn3_lean_s10` | not started |
| 3 | `r6_conventional_external_pkgfn3_reorder_s10` | not started |
| 3 | `r6_conventional_external_bofn3_lean_s10` | not started |
| 3 | `r6_conventional_external_bofn3_reorder_s10` | not started |
| 3 | `r6_vertical_parallel_fast_lean_s10` | not started |
| 3 | `r6_vertical_parallel_fast_reorder_s10` | not started |
| 3 | `r6_conventional_external_fast_lean_s10` | not started |
| 3 | `r6_conventional_external_fast_reorder_s10` | not started |
| 4 | `r6_conventional_external_pkgfn3_lean_s11` | not started |
| 4 | `r6_conventional_external_pkgfn3_reorder_s11` | not started |
| 4 | `r6_conventional_external_bofn3_lean_s11` | not started |
| 4 | `r6_conventional_external_bofn3_reorder_s11` | not started |
| 4 | `r6_vertical_parallel_fast_lean_s11` | not started |
| 4 | `r6_vertical_parallel_fast_reorder_s11` | not started |
| 4 | `r6_conventional_external_fast_lean_s11` | not started |
| 4 | `r6_conventional_external_fast_reorder_s11` | not started |
| 5 | `r6_conventional_external_pkgfn3_lean_s12` | not started |
| 5 | `r6_conventional_external_pkgfn3_reorder_s12` | not started |
| 5 | `r6_conventional_external_bofn3_lean_s12` | not started |
| 5 | `r6_conventional_external_bofn3_reorder_s12` | not started |
| 5 | `r6_vertical_parallel_fast_lean_s12` | not started |
| 5 | `r6_vertical_parallel_fast_reorder_s12` | not started |
| 5 | `r6_conventional_external_fast_lean_s12` | not started |
| 5 | `r6_conventional_external_fast_reorder_s12` | not started |
| 6 | `r6_conventional_external_pkgfn3_lean_s13` | not started |
| 6 | `r6_conventional_external_pkgfn3_reorder_s13` | not started |
| 6 | `r6_conventional_external_bofn3_lean_s13` | not started |
| 6 | `r6_conventional_external_bofn3_reorder_s13` | not started |
| 6 | `r6_vertical_parallel_fast_lean_s13` | not started |
| 6 | `r6_vertical_parallel_fast_reorder_s13` | not started |
| 6 | `r6_conventional_external_fast_lean_s13` | not started |
| 6 | `r6_conventional_external_fast_reorder_s13` | not started |
| 7 | `r6_conventional_external_pkgfn3_lean_s14` | not started |
| 7 | `r6_conventional_external_pkgfn3_reorder_s14` | not started |
| 7 | `r6_conventional_external_bofn3_lean_s14` | not started |
| 7 | `r6_conventional_external_bofn3_reorder_s14` | not started |
| 7 | `r6_vertical_parallel_fast_lean_s14` | not started |
| 7 | `r6_vertical_parallel_fast_reorder_s14` | not started |
| 7 | `r6_conventional_external_fast_lean_s14` | not started |
| 7 | `r6_conventional_external_fast_reorder_s14` | not started |
| 8 | `r6_conventional_external_pkgfn3_lean_s15` | not started |
| 8 | `r6_conventional_external_pkgfn3_reorder_s15` | not started |
| 8 | `r6_conventional_external_bofn3_lean_s15` | not started |
| 8 | `r6_conventional_external_bofn3_reorder_s15` | not started |
| 8 | `r6_vertical_parallel_fast_lean_s15` | not started |
| 8 | `r6_vertical_parallel_fast_reorder_s15` | not started |
| 8 | `r6_conventional_external_fast_lean_s15` | not started |
| 8 | `r6_conventional_external_fast_reorder_s15` | not started |
| 9 | `r6_vertical_parallel_pkgfn3_lean_s2` | no row, no checkpoint |
| 9 | `r6_vertical_parallel_pkgfn3_reorder_s2` | no row, no checkpoint |
| 9 | `r6_vertical_parallel_bofn3_lean_s2` | no row, no checkpoint |
| 9 | `r6_vertical_parallel_bofn3_reorder_s2` | no row, no checkpoint |
| 9 | `r6_conventional_external_pkgfn3_lean_s2` | no row, no checkpoint |
| 9 | `r6_conventional_external_pkgfn3_reorder_s2` | no row, no checkpoint |
| 9 | `r6_conventional_external_bofn3_lean_s2` | no row, no checkpoint |
| 9 | `r6_conventional_external_bofn3_reorder_s2` | no row, no checkpoint |
| 9 | `r6_vertical_parallel_fast_lean_s2` | no row, no checkpoint |
| 9 | `r6_vertical_parallel_fast_reorder_s2` | no row, no checkpoint |
| 9 | `r6_conventional_external_fast_lean_s2` | no row, no checkpoint |
| 9 | `r6_conventional_external_fast_reorder_s2` | no row, no checkpoint |
| 10 | `r6_conventional_external_pkgfn3_lean_s3` | not started |
| 10 | `r6_conventional_external_pkgfn3_reorder_s3` | not started |
| 10 | `r6_conventional_external_bofn3_lean_s3` | not started |
| 10 | `r6_conventional_external_bofn3_reorder_s3` | not started |
| 10 | `r6_vertical_parallel_fast_lean_s3` | not started |
| 10 | `r6_vertical_parallel_fast_reorder_s3` | not started |
| 10 | `r6_conventional_external_fast_lean_s3` | not started |
| 10 | `r6_conventional_external_fast_reorder_s3` | not started |
| 11 | `r6_vertical_parallel_pkgfn3_lean_s4` | no row, no checkpoint |
| 11 | `r6_vertical_parallel_pkgfn3_reorder_s4` | no row, no checkpoint |
| 11 | `r6_vertical_parallel_bofn3_lean_s4` | no row, no checkpoint |
| 11 | `r6_vertical_parallel_bofn3_reorder_s4` | no row, no checkpoint |
| 11 | `r6_conventional_external_pkgfn3_lean_s4` | no row, no checkpoint |
| 11 | `r6_conventional_external_pkgfn3_reorder_s4` | no row, no checkpoint |
| 11 | `r6_conventional_external_bofn3_lean_s4` | no row, no checkpoint |
| 11 | `r6_conventional_external_bofn3_reorder_s4` | no row, no checkpoint |
| 11 | `r6_vertical_parallel_fast_lean_s4` | no row, no checkpoint |
| 11 | `r6_vertical_parallel_fast_reorder_s4` | no row, no checkpoint |
| 11 | `r6_conventional_external_fast_lean_s4` | no row, no checkpoint |
| 11 | `r6_conventional_external_fast_reorder_s4` | no row, no checkpoint |
| 12 | `r6_vertical_parallel_pkgfn3_lean_s5` | no row, no checkpoint |
| 12 | `r6_vertical_parallel_pkgfn3_reorder_s5` | no row, no checkpoint |
| 12 | `r6_vertical_parallel_bofn3_lean_s5` | no row, no checkpoint |
| 12 | `r6_vertical_parallel_bofn3_reorder_s5` | no row, no checkpoint |
| 12 | `r6_conventional_external_pkgfn3_lean_s5` | no row, no checkpoint |
| 12 | `r6_conventional_external_pkgfn3_reorder_s5` | no row, no checkpoint |
| 12 | `r6_conventional_external_bofn3_lean_s5` | no row, no checkpoint |
| 12 | `r6_conventional_external_bofn3_reorder_s5` | no row, no checkpoint |
| 12 | `r6_vertical_parallel_fast_lean_s5` | no row, no checkpoint |
| 12 | `r6_vertical_parallel_fast_reorder_s5` | no row, no checkpoint |
| 12 | `r6_conventional_external_fast_lean_s5` | no row, no checkpoint |
| 12 | `r6_conventional_external_fast_reorder_s5` | no row, no checkpoint |
| 13 | `r6_vertical_parallel_pkgfn3_lean_s6` | no row, no checkpoint |
| 13 | `r6_vertical_parallel_pkgfn3_reorder_s6` | no row, no checkpoint |
| 13 | `r6_vertical_parallel_bofn3_lean_s6` | no row, no checkpoint |
| 13 | `r6_vertical_parallel_bofn3_reorder_s6` | no row, no checkpoint |
| 13 | `r6_conventional_external_pkgfn3_lean_s6` | no row, no checkpoint |
| 13 | `r6_conventional_external_pkgfn3_reorder_s6` | no row, no checkpoint |
| 13 | `r6_conventional_external_bofn3_lean_s6` | no row, no checkpoint |
| 13 | `r6_conventional_external_bofn3_reorder_s6` | no row, no checkpoint |
| 13 | `r6_vertical_parallel_fast_lean_s6` | no row, no checkpoint |
| 13 | `r6_vertical_parallel_fast_reorder_s6` | no row, no checkpoint |
| 13 | `r6_conventional_external_fast_lean_s6` | no row, no checkpoint |
| 13 | `r6_conventional_external_fast_reorder_s6` | no row, no checkpoint |
| 14 | `r6_conventional_external_pkgfn3_lean_s7` | not started |
| 14 | `r6_conventional_external_pkgfn3_reorder_s7` | not started |
| 14 | `r6_conventional_external_bofn3_lean_s7` | not started |
| 14 | `r6_conventional_external_bofn3_reorder_s7` | not started |
| 14 | `r6_vertical_parallel_fast_lean_s7` | not started |
| 14 | `r6_vertical_parallel_fast_reorder_s7` | not started |
| 14 | `r6_conventional_external_fast_lean_s7` | not started |
| 14 | `r6_conventional_external_fast_reorder_s7` | not started |
| 15 | `r6_conventional_external_bofn3_lean_s8` | not started |
| 15 | `r6_conventional_external_bofn3_reorder_s8` | not started |
| 15 | `r6_vertical_parallel_fast_lean_s8` | not started |
| 15 | `r6_vertical_parallel_fast_reorder_s8` | not started |
| 15 | `r6_conventional_external_fast_lean_s8` | not started |
| 15 | `r6_conventional_external_fast_reorder_s8` | not started |
| 16 | `r6_vertical_parallel_pkgfn3_lean_s9` | no row, no checkpoint |
| 16 | `r6_vertical_parallel_pkgfn3_reorder_s9` | no row, no checkpoint |
| 16 | `r6_vertical_parallel_bofn3_lean_s9` | no row, no checkpoint |
| 16 | `r6_vertical_parallel_bofn3_reorder_s9` | no row, no checkpoint |
| 16 | `r6_conventional_external_pkgfn3_lean_s9` | no row, no checkpoint |
| 16 | `r6_conventional_external_pkgfn3_reorder_s9` | no row, no checkpoint |
| 16 | `r6_conventional_external_bofn3_lean_s9` | no row, no checkpoint |
| 16 | `r6_conventional_external_bofn3_reorder_s9` | no row, no checkpoint |
| 16 | `r6_vertical_parallel_fast_lean_s9` | no row, no checkpoint |
| 16 | `r6_vertical_parallel_fast_reorder_s9` | no row, no checkpoint |
| 16 | `r6_conventional_external_fast_lean_s9` | no row, no checkpoint |
| 16 | `r6_conventional_external_fast_reorder_s9` | no row, no checkpoint |

## Files

* rows-tier1-15: arms.slice-tier1-15.jsonl: 2 new rows (2 in the file)
