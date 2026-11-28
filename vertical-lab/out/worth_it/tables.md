# Is the vertical lab worth it? The queue model's tables (issue #407)

Written by `python -m twin.worth_it tables` from `out/worth_it/results.json.xz`. Simulated: the twin's round-3 event logs (24: 12 seeds of time-aware BOFN, 12 of the funnel, the vertical lab, one year) replayed through a transport layer with stand-in handling times (`twin/worth_it.py`, `Params`). Medians over the logs, 10th-90th percentile in brackets. An internal step's delay is against the twin's own end; the twin's 6 min transfer is credited back, so it can be negative. 'Atomizer runs off their slot': runs that started more than 30 min after their slot in the twin (median over logs; how many logs had any). A replay keeps the twin's order, so one lost slot moves every later run: those rows are the cases to read as 'this many units can't carry it'.

The twin's own days to its targets in these logs: Al SOTA: reached in 18 of 24 logs, median day 90; Al halfway: reached in 12 of 24 logs, median day 95; Cu SOTA: reached in 19 of 24 logs, median day 177; Cu halfway: reached in 15 of 24 logs, median day 191.

## Timing: the twin's timing (a load and an unload a step)

| Outside load | Layout | Units busy | Busiest opening busy | Busiest tray held by a run | Internal steps end later than the twin's, mean (h) | Atomizer runs off their slot | Outside jobs served | Outside jobs a day | Outside turnaround (h) | Outside turnaround, 95th pct (h) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | 2 % (2-2) | 1 % (1-1) | 6 % (5-7) (1B) | -0.04 (-0.05-0.01) | 0; 0 of 24 logs | - | - | - | - |
| 0 % | flat + 2 units | 1 % (1-1) | - | - | -0.04 (-0.05--0.04) | 0; 0 of 24 logs | - | - | - | - |
| 0 % | VLM + 2 units | 1 % (1-1) | 1 % (1-1) | 6 % (5-7) (1B) | -0.05 (-0.05--0.01) | 0; 0 of 24 logs | - | - | - | - |
| 0 % | flat + 1 unit | 2 % (2-2) | - | - | -0.04 (-0.04--0.03) | 0; 0 of 24 logs | - | - | - | - |
| 30 % | VLM + 1 unit | 41 % (41-41) | 20 % (20-20) | 71 % (70-71) (1E) | 0.00 (-0.01-0.07) | 0; 0 of 24 logs | 100.0 % | 127 | 1.7 (1.7-1.8) | 5.1 |
| 30 % | flat + 2 units | 21 % (21-22) | - | - | -0.03 (-0.03--0.02) | 0; 0 of 24 logs | 100.0 % | 127 | 1.3 (1.2-1.3) | 3.8 |
| 30 % | VLM + 2 units | 20 % (20-20) | 19 % (19-19) | 71 % (71-72) (1E) | -0.03 (-0.04-0.01) | 0; 0 of 24 logs | 100.0 % | 127 | 1.6 (1.6-1.7) | 4.9 |
| 30 % | flat + 1 unit | 44 % (43-44) | - | - | 0.02 (0.01-1.43) | 0; 6 of 24 logs | 100.0 % | 127 | 1.3 (1.3-1.7) | 3.9 |
| 60 % | VLM + 1 unit | 62 % (60-64) | 24 % (24-25) | 75 % (73-82) (2L) | 14.90 (9.01-24.69) | 280; 24 of 24 logs | 80.8 % | 206 | 14.3 (13.9-14.7) | 38.2 |
| 60 % | flat + 2 units | 39 % (39-40) | - | - | -0.01 (-0.02--0.01) | 0; 0 of 24 logs | 100.0 % | 255 | 2.1 (2.0-2.1) | 5.7 |
| 60 % | VLM + 2 units | 33 % (33-33) | 28 % (28-28) | 89 % (88-89) (1D) | -0.02 (-0.03-0.04) | 0; 0 of 24 logs | 94.2 % | 240 | 7.6 (7.4-7.7) | 24.5 |
| 60 % | flat + 1 unit | 76 % (75-76) | - | - | 60.86 (36.23-92.90) | 396; 24 of 24 logs | 89.4 % | 228 | 12.3 (11.8-13.3) | 19.9 |

Days to the twin's targets, later than the twin's own day:

| Outside load | Layout | Al SOTA: days later (median, max) | Al halfway: days later (median, max) | Cu SOTA: days later (median, max) | Cu halfway: days later (median, max) |
|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | -0.00 (0.15; n=18) | -0.00 (0.02; n=12) | 0.00 (0.00; n=19) | -0.00 (0.00; n=15) |
| 0 % | flat + 2 units | -0.00 (0.00; n=18) | -0.00 (0.00; n=12) | -0.00 (0.00; n=19) | -0.00 (0.00; n=15) |
| 0 % | VLM + 2 units | -0.00 (0.02; n=18) | -0.00 (0.01; n=12) | -0.00 (-0.00; n=19) | -0.00 (-0.00; n=15) |
| 0 % | flat + 1 unit | -0.00 (0.00; n=18) | -0.00 (0.01; n=12) | 0.00 (0.00; n=19) | 0.00 (0.00; n=15) |
| 30 % | VLM + 1 unit | 0.00 (0.13; n=18) | 0.00 (0.01; n=12) | 0.00 (0.01; n=19) | 0.00 (0.04; n=15) |
| 30 % | flat + 2 units | -0.00 (0.00; n=18) | -0.00 (0.00; n=12) | -0.00 (0.00; n=19) | -0.00 (0.00; n=15) |
| 30 % | VLM + 2 units | -0.00 (0.02; n=18) | -0.00 (0.02; n=12) | -0.00 (0.01; n=19) | -0.00 (0.04; n=15) |
| 30 % | flat + 1 unit | 0.00 (0.01; n=18) | 0.00 (0.02; n=12) | 0.00 (0.02; n=19) | 0.00 (0.02; n=15) |
| 60 % | VLM + 1 unit | 0.00 (2.66; n=18) | 0.00 (2.66; n=12) | 0.01 (3.77; n=19) | 0.01 (0.09; n=15) |
| 60 % | flat + 2 units | 0.00 (0.01; n=18) | 0.00 (0.01; n=12) | 0.00 (0.01; n=19) | 0.00 (0.00; n=15) |
| 60 % | VLM + 2 units | -0.00 (0.15; n=18) | -0.00 (0.00; n=12) | -0.00 (0.06; n=19) | -0.00 (0.06; n=15) |
| 60 % | flat + 1 unit | 0.03 (2.92; n=18) | 0.04 (2.27; n=12) | 0.01 (4.87; n=19) | 0.02 (4.87; n=15) |

Handling:

| Outside load | Layout | Driving a task (s) | Waiting for the tray after arriving (s) | Request to the arm at the instrument, internal (min) | the same, outside jobs (min) | Tray presentations a day (both Shuttles) | Attended arm-hours a day |
|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | 43 | 16 | 1.9 | - | 6 | 0.0 |
| 0 % | flat + 2 units | 81 | - | 2.2 | - | - | 0.0 |
| 0 % | VLM + 2 units | 61 | 15 | 1.7 | - | 6 | 0.0 |
| 0 % | flat + 1 unit | 58 | - | 2.3 | - | - | 0.0 |
| 30 % | VLM + 1 unit | 42 | 10 | 3.6 | 42.1 | 141 | 0.0 |
| 30 % | flat + 2 units | 63 | - | 2.8 | 17.8 | - | 0.0 |
| 30 % | VLM + 2 units | 40 | 12 | 2.4 | 36.5 | 134 | 0.0 |
| 30 % | flat + 1 unit | 61 | - | 4.3 | 20.3 | - | 0.0 |
| 60 % | VLM + 1 unit | 39 | 11 | 208.3 | 783.7 | 164 | 0.0 |
| 60 % | flat + 2 units | 53 | - | 3.3 | 64.8 | - | 0.0 |
| 60 % | VLM + 2 units | 29 | 15 | 2.7 | 385.3 | 160 | 0.0 |
| 60 % | flat + 1 unit | 60 | - | 734.9 | 673.7 | - | 0.0 |

## Timing: PR 332's attended time (the arm stays for its share of each step; the powder line in a cell)

| Outside load | Layout | Units busy | Busiest opening busy | Busiest tray held by a run | Internal steps end later than the twin's, mean (h) | Atomizer runs off their slot | Outside jobs served | Outside jobs a day | Outside turnaround (h) | Outside turnaround, 95th pct (h) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | 2 % (2-3) | 1 % (1-2) | 2 % (2-3) (1D) | -0.06 (-0.07-0.03) | 0; 0 of 24 logs | - | - | - | - |
| 0 % | flat + 2 units | 1 % (1-2) | - | - | -0.06 (-0.07--0.05) | 0; 0 of 24 logs | - | - | - | - |
| 0 % | VLM + 2 units | 1 % (1-2) | 1 % (1-2) | 2 % (2-3) (1D) | -0.07 (-0.07-0.01) | 0; 0 of 24 logs | - | - | - | - |
| 0 % | flat + 1 unit | 2 % (2-3) | - | - | -0.06 (-0.07--0.04) | 0; 0 of 24 logs | - | - | - | - |
| 30 % | VLM + 1 unit | 82 % (82-82) | 43 % (42-43) | 45 % (44-51) (1F) | 0.72 (0.33-1.66) | 5; 19 of 24 logs | 60.4 % | 77 | 65.2 (64.6-66.3) | 74.8 |
| 30 % | flat + 2 units | 68 % (67-68) | - | - | 0.08 (0.04-0.15) | 0; 2 of 24 logs | 100.0 % | 127 | 1.9 (1.8-1.9) | 4.8 |
| 30 % | VLM + 2 units | 67 % (67-68) | 60 % (59-61) | 53 % (53-54) (1E) | 0.05 (0.02-0.19) | 0; 0 of 24 logs | 100.0 % | 127 | 2.8 (2.6-3.0) | 8.7 |
| 30 % | flat + 1 unit | 82 % (82-82) | - | - | 0.77 (0.37-2.81) | 6; 18 of 24 logs | 58.9 % | 75 | 67.5 (66.9-68.8) | 76.9 |
| 60 % | VLM + 1 unit | 82 % (82-82) | 43 % (42-43) | 55 % (54-70) (1F) | 0.61 (0.34-1.45) | 2; 16 of 24 logs | 30.4 % | 78 | 79.7 (79.0-80.6) | 91.4 |
| 60 % | flat + 2 units | 82 % (82-82) | - | - | 0.18 (0.12-0.29) | 0; 1 of 24 logs | 61.0 % | 155 | 33.4 (33.2-33.8) | 39.4 |
| 60 % | VLM + 2 units | 82 % (82-82) | 67 % (66-68) | 64 % (62-77) (1F) | 0.14 (0.10-0.31) | 0; 2 of 24 logs | 62.2 % | 158 | 32.5 (31.8-32.9) | 54.1 |
| 60 % | flat + 1 unit | 82 % (82-82) | - | - | 0.66 (0.37-8.31) | 4; 18 of 24 logs | 29.5 % | 75 | 82.2 (81.4-83.4) | 91.7 |

Days to the twin's targets, later than the twin's own day:

| Outside load | Layout | Al SOTA: days later (median, max) | Al halfway: days later (median, max) | Cu SOTA: days later (median, max) | Cu halfway: days later (median, max) |
|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | -0.00 (0.14; n=18) | -0.00 (0.02; n=12) | -0.00 (0.01; n=19) | -0.00 (0.01; n=15) |
| 0 % | flat + 2 units | -0.00 (0.01; n=18) | -0.00 (0.00; n=12) | -0.00 (0.01; n=19) | -0.00 (0.01; n=15) |
| 0 % | VLM + 2 units | -0.00 (0.15; n=18) | -0.00 (0.02; n=12) | -0.00 (0.01; n=19) | -0.00 (-0.00; n=15) |
| 0 % | flat + 1 unit | -0.00 (0.02; n=18) | -0.00 (0.02; n=12) | -0.00 (0.01; n=19) | -0.00 (0.01; n=15) |
| 30 % | VLM + 1 unit | 0.11 (0.30; n=18) | 0.18 (0.28; n=12) | 0.05 (0.17; n=19) | 0.05 (0.17; n=15) |
| 30 % | flat + 2 units | 0.02 (0.16; n=18) | 0.02 (0.16; n=12) | 0.00 (0.05; n=19) | 0.00 (0.05; n=15) |
| 30 % | VLM + 2 units | 0.01 (0.29; n=18) | 0.02 (0.17; n=12) | 0.01 (0.05; n=19) | 0.01 (0.05; n=15) |
| 30 % | flat + 1 unit | 0.11 (0.33; n=18) | 0.11 (0.42; n=12) | 0.04 (0.18; n=19) | 0.04 (0.18; n=15) |
| 60 % | VLM + 1 unit | 0.07 (0.44; n=18) | 0.13 (0.44; n=12) | 0.04 (0.13; n=19) | 0.04 (0.13; n=15) |
| 60 % | flat + 2 units | 0.03 (0.28; n=18) | 0.02 (0.15; n=12) | 0.01 (0.08; n=19) | 0.01 (0.08; n=15) |
| 60 % | VLM + 2 units | 0.02 (0.39; n=18) | 0.03 (0.15; n=12) | 0.02 (0.09; n=19) | 0.02 (0.08; n=15) |
| 60 % | flat + 1 unit | 0.06 (0.32; n=18) | 0.07 (0.32; n=12) | 0.06 (0.16; n=19) | 0.06 (0.18; n=15) |

Handling:

| Outside load | Layout | Driving a task (s) | Waiting for the tray after arriving (s) | Request to the arm at the instrument, internal (min) | the same, outside jobs (min) | Tray presentations a day (both Shuttles) | Attended arm-hours a day |
|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | 36 | 22 | 2.3 | - | 4 | 0.3 |
| 0 % | flat + 2 units | 69 | - | 2.4 | - | - | 0.3 |
| 0 % | VLM + 2 units | 47 | 21 | 1.7 | - | 4 | 0.3 |
| 0 % | flat + 1 unit | 53 | - | 2.5 | - | - | 0.3 |
| 30 % | VLM + 1 unit | 44 | 17 | 19.7 | 3,815.9 | 97 | 13.6 |
| 30 % | flat + 2 units | 52 | - | 9.0 | 48.6 | - | 22.9 |
| 30 % | VLM + 2 units | 33 | 20 | 8.0 | 97.5 | 129 | 22.9 |
| 30 % | flat + 1 unit | 70 | - | 20.6 | 3,963.3 | - | 13.3 |
| 60 % | VLM + 1 unit | 44 | 17 | 20.0 | 4,667.5 | 93 | 13.6 |
| 60 % | flat + 2 units | 59 | - | 12.5 | 1,924.6 | - | 27.2 |
| 60 % | VLM + 2 units | 39 | 21 | 11.3 | 1,863.1 | 154 | 27.5 |
| 60 % | flat + 1 unit | 72 | - | 20.2 | 4,824.6 | - | 13.2 |
