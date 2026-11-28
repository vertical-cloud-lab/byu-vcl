# HPC pilot (round 6)

Made by `python out/twin6/checks/hpc_pilot_table.py` from `hpc_pilot.jsonl`. Everything is simulated.

| Policy | Days | Lab | Scale | Seeds | Al T1 | Al T2 | Al best | Al tested | Cu T1 | Cu T2 | Cu best | Cu tested | CPU s per run | extra CPU s a day |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bofn3 | 300 | conventional | 1x | 1 | - (0/1) | - (0/1) | 0.0 | 5 | 209.2 (1/1) | 209.2 (1/1) | 0.6937 | 2 | 75.8 |  |
| bofn3 | 300 | vertical | 1x | 1 | 151.7 (1/1) | 185.7 (1/1) | 0.7493 | 18 | - (0/1) | - (0/1) | 0.3948 | 2 | 544.5 |  |
| bofn3 | 300 | vertical | 4x | 1 | 231.4 (1/1) | 245.7 (1/1) | 0.7431 | 41 | - (0/1) | - (0/1) | 0.0 | 1 | 607.3 | 0.21 |
| bofn3 | 300 | vertical | 16x | 2 | 214.0 (2/2) | 214.0 (2/2) | 0.8077 | 52.5 | - (1/2) | - (0/2) | 0.5073 | 2.0 | 1244.4 | 2.33 |
| bofn3 | 300 | vertical | 64x | 2 | 212.6 (2/2) | 215.3 (2/2) | 0.7805 | 26.5 | - (1/2) | - (1/2) | 0.5308 | 3.0 | 1369.2 | 2.75 |
| fast | 300 | conventional | 1x | 1 | 81.7 (1/1) | 130.4 (1/1) | 0.7028 | 35 | - (0/1) | - (0/1) | 0.354 | 2 | 15.2 |  |
| fast | 300 | vertical | 1x | 1 | 56.6 (1/1) | - (0/1) | 0.5453 | 110 | - (0/1) | - (0/1) | 0.4134 | 2 | 25.2 |  |

Medians over the seeds; a target's cell is the median day (a seed that doesn't reach it counts as later than the horizon) and the seeds that reached it. 'extra s a day': the run's seconds over the same policy's and lab's at 1x, per simulated day (CPU seconds). Seeds are paired across scales (the same truths, build-outs and draws), but a run's path parts as soon as one decision differs, so with a few seeds only large changes show.
