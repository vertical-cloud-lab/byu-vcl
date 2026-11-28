# Round 6: each sensitivity's code path, checked

Made by `python out/twin6/checks/paths.py table` from `paths.jsonl`: seed 0, the automated lab stocked unless named, the heuristic and the funnel unless named, at 1x round 5's candidates, shortened. Days are from t = 0. Everything is simulated.

| Case | Days run | Work starts | Cell | Atomizer cycle | Atomizer runs a day after the cell | Derived cycle starts | Runs that waited for a crucible (Al / Cu) | Bought used | Capital new / used ($M) | Results held for a person (Al / Cu) | Al T1 / T2 | Cu T1 / T2 | s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| main | 330 | 0.0 | 211.5 | {'flaime_al': None, 'onr_cu': None, 'changeover_h': 1.5} | 5.72 | 211.52 | 1 / 0 | 2 | 4.16 / 0.07 | 240 / 0 | 56.6 / None | None / None | 72.6 |
| lean | 330 | 0.0 | 211.5 | {'flaime_al': None, 'onr_cu': None, 'changeover_h': 1.5} | 10.78 | 211.52 | 8 / 0 | 2 | 4.16 / 0.07 | 230 / 0 | 112.7 / None | None / None | 64.5 |
| plan: wait for the cell | 330 | 312.9 | 211.5 | {'flaime_al': None, 'onr_cu': None, 'changeover_h': 1.5} | 0.35 | 211.52 | 0 / 0 | 2 | 4.16 / 0.07 | 0 / 0 | None / None | None / None | 18.9 |
| plan: external routes only | 330 | 0.0 | None | {'flaime_al': None, 'onr_cu': None, 'changeover_h': 1.5} | None | None | 1 / 0 | 0 | 0.00 / 0.00 | 70 / 0 | 56.6 / None | None / None | 35.6 |
| decisions: none | 330 | 0.0 | 211.5 | {'flaime_al': None, 'onr_cu': None, 'changeover_h': 1.5} | 8.23 | 211.52 | 1 / 0 | 2 | 4.16 / 0.07 | 0 / 0 | 56.6 / None | None / None | 58.9 |
| decisions: slow | 330 | 0.0 | 211.5 | {'flaime_al': None, 'onr_cu': None, 'changeover_h': 1.5} | 7.12 | 211.52 | 2 / 0 | 2 | 4.16 / 0.07 | 267 / 0 | 154.6 / None | None / None | 67.0 |
| atomizer: 3 h | 330 | 0.0 | 211.5 | {'flaime_al': 3.0, 'onr_cu': 3.0, 'changeover_h': 1.5} | 5.15 | 211.52 | 1 / 1 | 2 | 4.16 / 0.07 | 249 / 0 | 56.6 / None | None / None | 67.8 |
| atomizer: slow | 330 | 0.0 | 211.5 | {'flaime_al': 5.5, 'onr_cu': 6.5, 'changeover_h': 2.0} | 4.01 | 211.52 | 1 / 0 | 2 | 4.16 / 0.07 | 146 / 0 | 56.6 / None | None / None | 53.7 |
| crucibles: late | 400 | 0.0 | 211.5 | {'flaime_al': None, 'onr_cu': None, 'changeover_h': 1.5} | 5.73 | 282.86 | 107 / 44 | 2 | 4.16 / 0.07 | 215 / 0 | 267.4 / None | 368.9 / 397.7 | 83.4 |
| crucibles: late, BOFN | 400 | 0.0 | 211.5 | {'flaime_al': None, 'onr_cu': None, 'changeover_h': 1.5} | 6.02 | 282.86 | 118 / 15 | 2 | 4.16 / 0.07 | 0 / 0 | 316.7 / 323.4 | 311.2 / 374.4 | 3673.3 |
| all-new equipment | 330 | 0.0 | 211.5 | {'flaime_al': None, 'onr_cu': None, 'changeover_h': 1.5} | 7.6 | 211.52 | 1 / 0 | 0 | 4.56 / 0.00 | 238 / 0 | 56.6 / None | None / None | 56.2 |
| conventional lab | 330 | 0.0 | None | {'flaime_al': None, 'onr_cu': None, 'changeover_h': 1.5} | None | None | 2 / 0 | 0 | 0.00 / 0.00 | 216 / 316 | 81.7 / 130.4 | None / None | 27.6 |

Marked `twin_dirty` (twin/ changed while the run went): crucibles: late, BOFN (ended at 4ee6b1b, started at twin/ tree aa296e7). `git diff` between the run's start and end shows what changed under twin/.
