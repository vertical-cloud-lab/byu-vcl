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

On a 4-core GitHub-hosted runner, from a checkout of this branch:

```bash
cd vertical-lab
export PIP_TIMEOUT=600 PIP_RETRIES=2
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.15.0 && pip install -r out/twin6/requirements.txt
K=1                                                       # this slice's number
python -m twin.gpcheck6 --out out/twin6/slices/gpcheck-slice-$K.json      # first: exit 0 if this CPU computes what
                                                                          # the reference CPU did (about 2-5 minutes)
python -m twin.bench6 ids out/twin6/slices/slice-$K.txt --slice $K --workers 4
git add -f out/twin6/runs/*.slice-$K.jsonl out/twin6/events out/twin6/slices/gpcheck-slice-$K.json
```

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
