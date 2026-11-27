# Twin round 6: outputs

Round 6 of the digital twin (`vertical-lab/twin/round6.py`, `bench6.py`), stacked on round 5 (PR 405). Everything here
is simulated.

| Path | What |
|---|---|
| `market/` | the used-equipment market survey (issue 424, branch `claude/twin-used-market`): `listings.csv`, the per-station `summary.csv` the engine reads, its README |
| `runs/` | one JSON line per run, per experiment (`<experiment>.jsonl.xz`) |
| `events/` | each run's event log (`<run id>.json.xz`) |
| `checks/` | the GP determinism check's reference hashes and the smoke run's timings |
| `left.md` | runs done and left, made by `python -m twin.bench6 status` |

The grid is run in compute slices, not by the job that built the engine.
