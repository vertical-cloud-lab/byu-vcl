# Twin round 6: outputs

Round 6 of the digital twin (`vertical-lab/twin/round6.py`, `bench6.py`), stacked on round 5 (PR 405). Everything here
is simulated. The write-up is [`../../notes/twin_round6.md`](../../notes/twin_round6.md).

| Path | What |
|---|---|
| `market/` | the used-equipment market survey (issue 424, PR 429, merged): `listings.csv`, the per-station `summary.csv` the engine reads (every row records its sha256, `r6.used.file_sha256`), its README. What it changes in the build-out: `checks/used_market.md` |
| `runs/` | one JSON line per run, per experiment (`<experiment>.jsonl.xz`; a slice's own `<experiment>.slice-<k>.jsonl` until it is folded in) |
| `events/` | each run's event log (`<run id>.json.xz`) |
| `checks/` | the GP determinism check's reference (`gpcheck.json`) and its late runs' checkpoints (`late/`), what was measured to find the pin (`pin_search/`), the timing runs and BOFN's scale pilot (`timing6.*`), the batched engine's re-timing and A/B (`timing6b*`, `batch.md`), the three-day run of every group and the timings the grid plans with (`smoke.json`), each sensitivity's code path (`paths.*`), the used market in the build-out (`used_market.*`), copper's idle check (`copper_idle.*`) |
| `slices/` | the workflow's plans (`tier1.json`), what each wave's jobs left (`<plan>/`), the workflow test (`workflow_test/`): [`slices/README.md`](slices/README.md); and a hand-run slice's run list (`slice-<k>.txt`) and GP check (`gpcheck-slice-<k>.json`) |
| `left.md` | runs done and left, seconds per run and core-hours, made by `python -m twin.bench6 status` |

The grid is run in compute slices, not by the job that built the engine. **Tier 1 runs on the workflow
`ci/twin-slices.yml`** (to be moved to `.github/workflows/`), wave after wave, from the plan `slices/tier1.json`:
[`slices/README.md`](slices/README.md). The commands below are what each of its jobs runs, and how to run a slice by
hand.

## Running a compute slice

On a 4-vCPU GitHub-hosted runner (Ubuntu, x86-64) with **Python 3.14.4** (`actions/setup-python`; the wheels the
requirements pin are 3.14's), from a checkout of this branch. Everything a row depends on is pinned: the engine (the
tree hash of `twin/`), the packages (exact versions), the numerical libraries' kernels and threads (`TWIN_PIN=portable`,
which the commands set themselves) and the hash seed.

```bash
set -e
cd vertical-lab
test "$(git rev-parse HEAD:vertical-lab/twin)" = e3d828cf5b4fd49d09f06172ce20ae16321c97fb   # the engine the grid is
                                                          # planned and checked with (stop if it isn't)
export PIP_TIMEOUT=600 PIP_RETRIES=2
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.15.0 && pip install -r out/twin6/requirements.txt
K=1                                                       # this slice's number
TWIN_WORKERS=4 python -m twin.gpcheck6 --out out/twin6/slices/gpcheck-slice-$K.json   # first: exit 0 if this CPU
                                                          # computes what the reference CPU did (about 5 minutes)
python -m twin.bench6 ids out/twin6/slices/slice-$K.txt --slice $K --workers 4 --hours 5.2   # a file of run ids,
                                                          # one a line, or the ids themselves; --hours: see below
git add -f out/twin6/runs/*.slice-$K.jsonl out/twin6/events out/twin6/slices/gpcheck-slice-$K.json
git add -f out/twin6/checkpoints                          # runs stopped at the time limit, if any (next section)
```

**Runs longer than a job: checkpoints.** With `--hours H`, a run still going H hours after `ids` started stops at its
next simulated day, is saved to `out/twin6/checkpoints/<run id>.ckpt.xz` (twin/ckpt6.py: about 1 MB at day 100,
more as its GP nodes fill), and gets no row. Runs that haven't started by then aren't started. Give the next job the
same run ids, with the checkpoints in place (commit them with `git add -f`, or carry them as a workflow artifact), and
each stopped run carries on from its day, first, to the row an unbroken run gives; its row records each job's share
(`timing.segments`: the CPU, CPU seconds and days of each). `python -m twin.gpcheck6 resume` is the test that a run
carried on is the same run: the GP check's three runs stopped half way in one fresh interpreter, carried on in another,
and compared with the reference in row, event log and GP state. A slice's jobs can run on different CPUs, as long as
each passes the GP check. Set H to the job's limit less set-up, the GP check and a margin: 5.2 for a 6-hour job.

The `twin/` tree above (`e3d828c`, commit `e173728`) is the batched engine (64-point GP calls, PR 427: notes,
section 11). Its GP check reference (`checks/gpcheck.json`) was made at `3136810` on an AMD EPYC 7763 and includes two
late runs, from the committed day-300 checkpoints in `checks/late/`, which reach the network's valuation (the three
short runs end before it); the check on the tree above gives exit 0 (`checks/gpcheck_check_e173728.json`), and so does
the checkpoint-resume check (`checks/gpcheck_resume.json`). The grid's engine before the batching was `701dea1`
(`gpcheck_check_74254fe.json`; that reference is kept as `gpcheck_ref_568ab5f_9v45.json`). Change anything in `twin/`
and the checks, the timings, the plan and this hash all have to be made again.

**How long a slice takes.** A run of the automated lab with BOFN or pKGFN costs 3-6 CPU-hours on an EPYC 9V45 and
about twice that on an EPYC 7763 (`left.md`, `checks/batch.md`); with four at a time on four vCPUs, a slice's longest
run sets its length. `slices 0` keeps each
slice at or under 16 core-hours. Each row is written to the slice's file when its run ends; commit and push that file
as the slice goes, not only at the end, so a job stopped by its time limit loses only the runs still going. `ids`
skips every run whose row is already in `runs/` (slice files included), so the same list can be run again.

* `python -m twin.bench6` and `python -m twin.gpcheck6` pin themselves: with `TWIN_PIN` unset they re-execute under
  `TWIN_PIN=portable` and `PYTHONHASHSEED=0` (twin/repro.py). `ids` and `run` refuse any other pin. Don't set
  `MKL_*`, `OPENBLAS_*`, `NPY_*` or `OMP_*` yourself.
* `gpcheck6` exits 0 when every probe group and the three short runs' rows, event logs and GP states match the
  reference, 1 when anything differs, 2 when the pin isn't in force. A slice whose check doesn't exit 0 should stop and
  report it rather than make rows: those rows would not be the reference CPU's.
* `ids` skips runs already in `runs/`, runs the longest first, writes rows to `runs/<experiment>.slice-<k>.jsonl` (in
  `.gitignore`, hence `git add -f`) and event logs to `events/`, and a run that raises to
  `runs/<experiment>.slice-<k>.errors.jsonl`. Every row records its commit, the tree hash of `twin/` at the start and
  the end of the run, whether `twin/` differed from the commit at either point (`code.twin_dirty`), the CPU and the
  pin (`env`), and the sha256 of the market summary it read (`r6.used.file_sha256`).
* Pushing rows while the runs go on is fine: it doesn't change `twin/`.
* Folding the slices in: merge each slice's branch, then `python -m twin.bench6 fold` (appends each slice's rows to
  its experiment, one per run id, removes the slice files and packs), then `python -m twin.bench6 status`.

Making the lists: `python -m twin.bench6 slices 0` splits the runs left into as many lists as keep each at or under
16 core-hours (about 4 hours on 4 cores, inside a 6-hour job with set-up), longest runs first; `slices N` makes N;
`slices 0 tier1` or `slices 0 arms` only some.
