# Round 6 plan `tier1`: status after workflow run 46121467370

6 of 192 runs have rows (4 new in this wave); 24 are waiting on a checkpoint and 162 have neither. Everything is simulated.

**To carry on:** dispatch the workflow again with the same branch and plan and `resume_run_id` = `46121467370`: each job restores its checkpoints from this run's `ckpt-...` artifacts and carries those runs on first.

## Waiting on a checkpoint

| Job | Run | Stopped at day |
|---|---|---|
| 1 | `r6_vertical_parallel_pkgfn3_lean_s0` | 698 |
| 1 | `r6_vertical_parallel_pkgfn3_reorder_s0` | 648 |
| 1 | `r6_vertical_parallel_bofn3_lean_s0` | 593 |
| 1 | `r6_vertical_parallel_bofn3_reorder_s0` | 660 |
| 9 | `r6_vertical_parallel_pkgfn3_lean_s2` | 701 |
| 9 | `r6_vertical_parallel_bofn3_lean_s2` | 597 |
| 9 | `r6_vertical_parallel_bofn3_reorder_s2` | 678 |
| 9 | `r6_conventional_external_bofn3_lean_s2` | 118 |
| 11 | `r6_vertical_parallel_pkgfn3_lean_s4` | 499 |
| 11 | `r6_vertical_parallel_pkgfn3_reorder_s4` | 528 |
| 11 | `r6_vertical_parallel_bofn3_lean_s4` | 445 |
| 11 | `r6_vertical_parallel_bofn3_reorder_s4` | 526 |
| 12 | `r6_vertical_parallel_pkgfn3_lean_s5` | 602 |
| 12 | `r6_vertical_parallel_pkgfn3_reorder_s5` | 639 |
| 12 | `r6_vertical_parallel_bofn3_lean_s5` | 536 |
| 12 | `r6_vertical_parallel_bofn3_reorder_s5` | 565 |
| 13 | `r6_vertical_parallel_pkgfn3_lean_s6` | 697 |
| 13 | `r6_vertical_parallel_pkgfn3_reorder_s6` | 725 |
| 13 | `r6_vertical_parallel_bofn3_lean_s6` | 649 |
| 13 | `r6_vertical_parallel_bofn3_reorder_s6` | 702 |
| 16 | `r6_vertical_parallel_pkgfn3_lean_s9` | 651 |
| 16 | `r6_vertical_parallel_bofn3_lean_s9` | 567 |
| 16 | `r6_vertical_parallel_bofn3_reorder_s9` | 696 |
| 16 | `r6_conventional_external_pkgfn3_lean_s9` | 504 |

## No row and no checkpoint

| Job | Run | Why |
|---|---|---|
| 1 | `r6_conventional_external_pkgfn3_lean_s0` | not started |
| 1 | `r6_conventional_external_pkgfn3_reorder_s0` | not started |
| 1 | `r6_conventional_external_bofn3_lean_s0` | not started |
| 1 | `r6_conventional_external_bofn3_reorder_s0` | not started |
| 1 | `r6_vertical_parallel_fast_lean_s0` | not started |
| 1 | `r6_vertical_parallel_fast_reorder_s0` | not started |
| 1 | `r6_conventional_external_fast_lean_s0` | not started |
| 1 | `r6_conventional_external_fast_reorder_s0` | not started |
| 2 | `r6_vertical_parallel_pkgfn3_lean_s1` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 2 | `r6_vertical_parallel_pkgfn3_reorder_s1` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 2 | `r6_vertical_parallel_bofn3_lean_s1` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 2 | `r6_vertical_parallel_bofn3_reorder_s1` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 2 | `r6_conventional_external_pkgfn3_lean_s1` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 2 | `r6_conventional_external_pkgfn3_reorder_s1` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 2 | `r6_conventional_external_bofn3_lean_s1` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 2 | `r6_conventional_external_bofn3_reorder_s1` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 2 | `r6_vertical_parallel_fast_lean_s1` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 2 | `r6_vertical_parallel_fast_reorder_s1` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 2 | `r6_conventional_external_fast_lean_s1` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 2 | `r6_conventional_external_fast_reorder_s1` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 3 | `r6_vertical_parallel_pkgfn3_lean_s10` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 3 | `r6_vertical_parallel_pkgfn3_reorder_s10` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 3 | `r6_vertical_parallel_bofn3_lean_s10` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 3 | `r6_vertical_parallel_bofn3_reorder_s10` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 3 | `r6_conventional_external_pkgfn3_lean_s10` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 3 | `r6_conventional_external_pkgfn3_reorder_s10` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 3 | `r6_conventional_external_bofn3_lean_s10` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 3 | `r6_conventional_external_bofn3_reorder_s10` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 3 | `r6_vertical_parallel_fast_lean_s10` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 3 | `r6_vertical_parallel_fast_reorder_s10` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 3 | `r6_conventional_external_fast_lean_s10` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 3 | `r6_conventional_external_fast_reorder_s10` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 4 | `r6_vertical_parallel_pkgfn3_lean_s11` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 4 | `r6_vertical_parallel_pkgfn3_reorder_s11` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 4 | `r6_vertical_parallel_bofn3_lean_s11` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 4 | `r6_vertical_parallel_bofn3_reorder_s11` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 4 | `r6_conventional_external_pkgfn3_lean_s11` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 4 | `r6_conventional_external_pkgfn3_reorder_s11` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 4 | `r6_conventional_external_bofn3_lean_s11` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 4 | `r6_conventional_external_bofn3_reorder_s11` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 4 | `r6_vertical_parallel_fast_lean_s11` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 4 | `r6_vertical_parallel_fast_reorder_s11` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 4 | `r6_conventional_external_fast_lean_s11` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 4 | `r6_conventional_external_fast_reorder_s11` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 5 | `r6_vertical_parallel_pkgfn3_lean_s12` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 5 | `r6_vertical_parallel_pkgfn3_reorder_s12` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 5 | `r6_vertical_parallel_bofn3_lean_s12` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 5 | `r6_vertical_parallel_bofn3_reorder_s12` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 5 | `r6_conventional_external_pkgfn3_lean_s12` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 5 | `r6_conventional_external_pkgfn3_reorder_s12` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 5 | `r6_conventional_external_bofn3_lean_s12` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 5 | `r6_conventional_external_bofn3_reorder_s12` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 5 | `r6_vertical_parallel_fast_lean_s12` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 5 | `r6_vertical_parallel_fast_reorder_s12` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 5 | `r6_conventional_external_fast_lean_s12` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 5 | `r6_conventional_external_fast_reorder_s12` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 6 | `r6_vertical_parallel_pkgfn3_lean_s13` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 6 | `r6_vertical_parallel_pkgfn3_reorder_s13` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 6 | `r6_vertical_parallel_bofn3_lean_s13` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 6 | `r6_vertical_parallel_bofn3_reorder_s13` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 6 | `r6_conventional_external_pkgfn3_lean_s13` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 6 | `r6_conventional_external_pkgfn3_reorder_s13` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 6 | `r6_conventional_external_bofn3_lean_s13` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 6 | `r6_conventional_external_bofn3_reorder_s13` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 6 | `r6_vertical_parallel_fast_lean_s13` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 6 | `r6_vertical_parallel_fast_reorder_s13` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 6 | `r6_conventional_external_fast_lean_s13` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 6 | `r6_conventional_external_fast_reorder_s13` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 7 | `r6_vertical_parallel_pkgfn3_lean_s14` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 7 | `r6_vertical_parallel_pkgfn3_reorder_s14` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 7 | `r6_vertical_parallel_bofn3_lean_s14` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 7 | `r6_vertical_parallel_bofn3_reorder_s14` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 7 | `r6_conventional_external_pkgfn3_lean_s14` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 7 | `r6_conventional_external_pkgfn3_reorder_s14` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 7 | `r6_conventional_external_bofn3_lean_s14` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 7 | `r6_conventional_external_bofn3_reorder_s14` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 7 | `r6_vertical_parallel_fast_lean_s14` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 7 | `r6_vertical_parallel_fast_reorder_s14` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 7 | `r6_conventional_external_fast_lean_s14` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 7 | `r6_conventional_external_fast_reorder_s14` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 8 | `r6_vertical_parallel_pkgfn3_lean_s15` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 8 | `r6_vertical_parallel_pkgfn3_reorder_s15` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 8 | `r6_vertical_parallel_bofn3_lean_s15` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 8 | `r6_vertical_parallel_bofn3_reorder_s15` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 8 | `r6_conventional_external_pkgfn3_lean_s15` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 8 | `r6_conventional_external_pkgfn3_reorder_s15` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 8 | `r6_conventional_external_bofn3_lean_s15` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 8 | `r6_conventional_external_bofn3_reorder_s15` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 8 | `r6_vertical_parallel_fast_lean_s15` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 8 | `r6_vertical_parallel_fast_reorder_s15` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 8 | `r6_conventional_external_fast_lean_s15` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 8 | `r6_conventional_external_fast_reorder_s15` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 9 | `r6_conventional_external_bofn3_reorder_s2` | not started |
| 9 | `r6_vertical_parallel_fast_lean_s2` | not started |
| 9 | `r6_vertical_parallel_fast_reorder_s2` | not started |
| 9 | `r6_conventional_external_fast_lean_s2` | not started |
| 9 | `r6_conventional_external_fast_reorder_s2` | not started |
| 10 | `r6_vertical_parallel_pkgfn3_lean_s3` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 10 | `r6_vertical_parallel_pkgfn3_reorder_s3` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 10 | `r6_vertical_parallel_bofn3_lean_s3` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 10 | `r6_vertical_parallel_bofn3_reorder_s3` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 10 | `r6_conventional_external_pkgfn3_lean_s3` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 10 | `r6_conventional_external_pkgfn3_reorder_s3` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 10 | `r6_conventional_external_bofn3_lean_s3` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 10 | `r6_conventional_external_bofn3_reorder_s3` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 10 | `r6_vertical_parallel_fast_lean_s3` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 10 | `r6_vertical_parallel_fast_reorder_s3` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 10 | `r6_conventional_external_fast_lean_s3` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 10 | `r6_conventional_external_fast_reorder_s3` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 11 | `r6_conventional_external_pkgfn3_lean_s4` | not started |
| 11 | `r6_conventional_external_pkgfn3_reorder_s4` | not started |
| 11 | `r6_conventional_external_bofn3_lean_s4` | not started |
| 11 | `r6_conventional_external_bofn3_reorder_s4` | not started |
| 11 | `r6_vertical_parallel_fast_lean_s4` | not started |
| 11 | `r6_vertical_parallel_fast_reorder_s4` | not started |
| 11 | `r6_conventional_external_fast_lean_s4` | not started |
| 11 | `r6_conventional_external_fast_reorder_s4` | not started |
| 12 | `r6_conventional_external_pkgfn3_lean_s5` | not started |
| 12 | `r6_conventional_external_pkgfn3_reorder_s5` | not started |
| 12 | `r6_conventional_external_bofn3_lean_s5` | not started |
| 12 | `r6_conventional_external_bofn3_reorder_s5` | not started |
| 12 | `r6_vertical_parallel_fast_lean_s5` | not started |
| 12 | `r6_vertical_parallel_fast_reorder_s5` | not started |
| 12 | `r6_conventional_external_fast_lean_s5` | not started |
| 12 | `r6_conventional_external_fast_reorder_s5` | not started |
| 13 | `r6_conventional_external_pkgfn3_lean_s6` | not started |
| 13 | `r6_conventional_external_pkgfn3_reorder_s6` | not started |
| 13 | `r6_conventional_external_bofn3_lean_s6` | not started |
| 13 | `r6_conventional_external_bofn3_reorder_s6` | not started |
| 13 | `r6_vertical_parallel_fast_lean_s6` | not started |
| 13 | `r6_vertical_parallel_fast_reorder_s6` | not started |
| 13 | `r6_conventional_external_fast_lean_s6` | not started |
| 13 | `r6_conventional_external_fast_reorder_s6` | not started |
| 14 | `r6_vertical_parallel_pkgfn3_lean_s7` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 14 | `r6_vertical_parallel_pkgfn3_reorder_s7` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 14 | `r6_vertical_parallel_bofn3_lean_s7` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 14 | `r6_vertical_parallel_bofn3_reorder_s7` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 14 | `r6_conventional_external_pkgfn3_lean_s7` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 14 | `r6_conventional_external_pkgfn3_reorder_s7` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 14 | `r6_conventional_external_bofn3_lean_s7` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 14 | `r6_conventional_external_bofn3_reorder_s7` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 14 | `r6_vertical_parallel_fast_lean_s7` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 14 | `r6_vertical_parallel_fast_reorder_s7` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 14 | `r6_conventional_external_fast_lean_s7` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 14 | `r6_conventional_external_fast_reorder_s7` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 15 | `r6_vertical_parallel_pkgfn3_reorder_s8` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 15 | `r6_vertical_parallel_bofn3_lean_s8` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 15 | `r6_vertical_parallel_bofn3_reorder_s8` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 15 | `r6_conventional_external_pkgfn3_reorder_s8` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 15 | `r6_conventional_external_bofn3_lean_s8` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 15 | `r6_conventional_external_bofn3_reorder_s8` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 15 | `r6_vertical_parallel_fast_lean_s8` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 15 | `r6_vertical_parallel_fast_reorder_s8` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 15 | `r6_conventional_external_fast_lean_s8` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 15 | `r6_conventional_external_fast_reorder_s8` | the job left no manifest (it failed, was cancelled, or had nothing to do) |
| 16 | `r6_conventional_external_pkgfn3_reorder_s9` | not started |
| 16 | `r6_conventional_external_bofn3_lean_s9` | not started |
| 16 | `r6_conventional_external_bofn3_reorder_s9` | not started |
| 16 | `r6_vertical_parallel_fast_lean_s9` | not started |
| 16 | `r6_vertical_parallel_fast_reorder_s9` | not started |
| 16 | `r6_conventional_external_fast_lean_s9` | not started |
| 16 | `r6_conventional_external_fast_reorder_s9` | not started |

## Files

* rows-tier1-16: arms.slice-tier1-16.jsonl: 1 new rows (1 in the file)
* rows-tier1-9: arms.slice-tier1-9.jsonl: 3 new rows (3 in the file)
