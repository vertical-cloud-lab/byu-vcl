# Round 6 plan `test2`: status after workflow run 999

3 of 5 runs have rows (0 new in this wave); 1 are waiting on a checkpoint and 1 have neither. Everything is simulated.

**To carry on:** dispatch the workflow again with the same branch and plan and `resume_run_id` = `999`: each job restores its checkpoints from this run's `ckpt-...` artifacts and carries those runs on first.

## Waiting on a checkpoint

| Job | Run | Stopped at day |
|---|---|---|
| 3 | `r6_vertical_parallel_pkgfn3_reorder_s9` | 311 |

## No row and no checkpoint

| Job | Run | Why |
|---|---|---|
| 4 | `r6_conventional_external_bofn3_reorder_s9` | the job left no manifest (it failed, was cancelled, or had nothing to do) |

## Files

* rows-test2-1: arms.slice-test2-1.jsonl: 0 new rows (1 in the file)
* rows-test2-2: arms.slice-test2-2.jsonl: 0 new rows (1 in the file)
* rows-test2-3: arms.slice-test2-3.jsonl: 0 new rows (1 in the file)

