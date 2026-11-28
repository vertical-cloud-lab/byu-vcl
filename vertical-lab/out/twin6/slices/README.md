# Round 6: the grid's compute slices on GitHub Actions

Everything here is simulated. The workflow is [`../../../ci/twin-slices.yml`](../../../ci/twin-slices.yml) (to be
moved to `.github/workflows/` by a person: the Claude app can't write there), its helper
[`../../../ci/twin_slices.py`](../../../ci/twin_slices.py) (standard library only), and the plan it runs is a JSON
file here, made by `python -m twin.bench6 plan`.

| Path | What |
|---|---|
| `tier1.json` | tier 1's plan: the 12 `arms` groups x 16 seeds (192 runs) in jobs, made by `bench6 plan` (below) |
| `<plan>/job-<k>/` | what each job of the latest wave left: its GP check (`gpcheck.json`), its `ids` log, its `manifest.json` (each run: a row, a checkpoint and the day it stopped at, not started, or neither) |
| `<plan>/status.md` | after each wave: runs with rows, runs waiting on a checkpoint, runs with neither, and how to carry on |
| `workflow_test/` | the workflow's steps run on two short runs, and its fold on fabricated artifacts (`ci/test_twin_slices.sh`) |

## Running a plan

1. **Install the workflow** (once): `git mv vertical-lab/ci/twin-slices.yml .github/workflows/twin-slices.yml`.
2. **Wave 1**: Actions -> *twin round 6 slices* -> *Run workflow*, with the branch (`claude/twin-round6`), the plan
   (`out/twin6/slices/tier1.json`) and `resume_run_id` empty. Every job of the plan gets a runner (or at most
   `max_parallel` at once).
3. **When it ends**, its last job has committed the rows to the branch (`out/twin6/runs/arms.slice-tier1-<k>.jsonl`,
   one file per job, the same file in every wave) with the event logs, each job's GP check and manifest, and
   `out/twin6/slices/tier1/status.md`, also on the run's summary page: the runs still waiting on a checkpoint.
4. **Wave 2, 3 ...**: run it again with the same branch and plan and `resume_run_id` set to the previous wave's run id
   (the number in its URL). Only the jobs with runs left start; each restores its checkpoints from the previous
   wave's `ckpt-tier1-<k>` artifact and carries those runs on first. Repeat until the status lists nothing.
5. **Fold** when the plan is done: `python -m twin.bench6 fold` (appends the slice files to `runs/arms.jsonl`, one row
   per run id, removes them and packs), then `python -m twin.bench6 status`.

A job that fails can be re-run from the run's page (*Re-run failed jobs*): it restores the same checkpoints, skips
the runs that already have rows on the branch, and the fold job runs again and merges what is new. Artifacts are
kept 90 days.

**What each job checks before it makes a row.** That `vertical-lab/twin` at the branch's head is the tree the plan was
made for (`twin_tree` in the plan: its time estimates and the GP check's reference belong to that engine), and that
this runner computes what the reference runner did: `python -m twin.gpcheck6` reruns the committed GP rows (the kernel
probe, the three short BOFN and pKGFN runs, and the two late runs from the committed day-300 checkpoints of the main
arm, `../checks/late/`) and the job stops on any difference. All of them run at once on the four vCPUs.

**The pin is `portable`, not `avx2`.** `TWIN_PIN=portable` is round 6's pin: `avx2`'s AVX2 kernels plus numpy's own
kernels capped at AVX2, MKL's CPU-independent branch and OpenBLAS's blocking fixed (twin/repro.py). `bench6 ids`
refuses any other pin, and under `avx2` alone round 5's rows differed between an EPYC 7763 and an EPYC 9V45, both CPUs
GitHub gives its 4-vCPU runners. The GP check on the engine before the batching matched the 9V45's reference on this
EPYC 7763 in every part (`../checks/gpcheck_7763_vs_ref_701dea1.json`).

## The plan

`python -m twin.bench6 plan tier1 --name tier1 --speed 9V45=1 --speed 7763=2.1` packs the runs left in tier 1 into jobs
by LPT (longest processing time first: each run, the longest first, to the job with the least estimated work so far)
on their estimated CPU seconds (`status`'s, `../left.md`), then simulates each job as `ids --hours 5.2` works through
it: four runs at a time, those carried over from a checkpoint first and then the longest first, a run still going at
5.2 hours carried on by the next wave, a run not started by then waiting for it. It takes the number of jobs (up to
20, a free organization's concurrent jobs, so that a wave runs at once) with the fewest waves at both speeds, then the
least wall-clock, then the fewest jobs. `--jobs N` sets the number instead.

The seconds are CPU seconds on the EPYC 9V45 that timed round 6. GitHub's 4-vCPU runners are not all the same CPU:
this job ran on an EPYC 7763, about 2.1 times slower per run for the same code (`../checks/batch.md`). A wave's jobs
can land on either, and a run carried over to the next wave may change CPU, which the check allows (every CPU that
passes it computes the same rows). The plan gives the waves and wall-clock for both.

**`tier1.json`**: 192 runs, 484 CPU-hours on a 9V45, in 16 jobs of 12 runs (2 of the automated lab's pKGFN at 8.9 h,
2 of its BOFN at 4.6 h, and 8 cheap runs: 30.3 CPU-hours a job).

| | On 9V45s | On 7763s (2.1x) |
|---|---|---|
| Waves | 2 | 4 |
| Wall-clock (each wave's jobs at once, 0.25 h of set-up and check a job) | 9.3 h | 19.6 h |
| Runner-hours | 150 | 313 |

Plus the time between a wave's end and the next dispatch. Expect something between the two columns. The plan's
`alternatives` give the same for 1-20 jobs: 13 jobs need the same waves and 0.7-1.4 h more; more than 16 gain nothing.
