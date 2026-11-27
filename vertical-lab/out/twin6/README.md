# Twin round 6: outputs

Round 6 of the digital twin (`vertical-lab/twin/round6.py`, `bench6.py`), stacked on round 5 (PR 405). Everything here
is simulated. The write-up is [`../../notes/twin_round6.md`](../../notes/twin_round6.md).

| Path | What |
|---|---|
| `market/` | the used-equipment market survey (issue 424, PR 429, merged): `listings.csv`, the per-station `summary.csv` the engine reads (every row records its sha256, `r6.used.file_sha256`), its README. What it changes in the build-out: `checks/used_market.md` |
| `runs/` | one JSON line per run, per experiment (`<experiment>.jsonl.xz`; a slice's own `<experiment>.slice-<k>.jsonl` until it is folded in) |
| `events/` | each run's event log (`<run id>.json.xz`) |
| `checks/` | the GP determinism check's reference (`gpcheck.json`), what was measured to find the pin (`pin_search/`), the timing runs and BOFN's scale pilot (`timing6.*`), the three-day run of every group and the timings the grid plans with (`smoke.json`), each sensitivity's code path (`paths.*`), the used market in the build-out (`used_market.*`), copper's idle check (`copper_idle.*`) |
| `slices/` | the compute slices' run lists (`slice-<k>.txt`) and each slice's GP check (`gpcheck-slice-<k>.json`) |
| `left.md` | runs done and left, seconds per run and core-hours, made by `python -m twin.bench6 status` |

The grid is run in compute slices, not by the job that built the engine.

## Running a compute slice

On a 4-vCPU GitHub-hosted runner (Ubuntu, x86-64) with **Python 3.14.4** (`actions/setup-python`; the wheels the
requirements pin are 3.14's), from a checkout of this branch. Everything a row depends on is pinned: the engine (the
tree hash of `twin/`), the packages (exact versions), the numerical libraries' kernels and threads (`TWIN_PIN=portable`,
which the commands set themselves) and the hash seed.

```bash
set -e
cd vertical-lab
test "$(git rev-parse HEAD:vertical-lab/twin)" = 469478fe0ee785ef82279ac84b186f656ac4a5de   # the engine the grid was
                                                          # built, timed and checked with (stop if it isn't)
export PIP_TIMEOUT=600 PIP_RETRIES=2
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.15.0 && pip install -r out/twin6/requirements.txt
K=1                                                       # this slice's number
python -m twin.gpcheck6 --out out/twin6/slices/gpcheck-slice-$K.json      # first: exit 0 if this CPU computes what
                                                                          # the reference CPU did (5-15 minutes)
python -m twin.bench6 ids out/twin6/slices/slice-$K.txt --slice $K --workers 4   # a file of run ids, one a line,
                                                          # or the ids themselves: ids r6_vertical_parallel_bofn3_reorder_s0 ...
git add -f out/twin6/runs/*.slice-$K.jsonl out/twin6/events out/twin6/slices/gpcheck-slice-$K.json
```

The `twin/` tree above differs from the one the GP check's reference was made with (`aa296e7`, commit `568ab5f`) only
in the grid's planning code (`bench6.timings`, `variant_ratios`, CPU seconds in each row's `timing`), its tests and
its README: no simulation code. Change anything in `twin/` and the reference, the timings and this hash all have to be
made again.

**How long a slice takes.** A run of the automated lab with BOFN or pKGFN costs several CPU-hours (`left.md`,
`checks/timing6.md`); with four at a time on four vCPUs, a slice's longest run sets its length. `slices 0` keeps each
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
