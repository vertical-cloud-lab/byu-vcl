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
| 30 % | VLM + 1 unit | 41 % (41-41) | 20 % (20-20) | 70 % (69-70) (1E) | 0.00 (-0.01-0.07) | 0; 0 of 24 logs | 100.0 % | 127 | 1.7 (1.7-1.8) | 5.2 |
| 30 % | flat + 2 units | 21 % (21-22) | - | - | -0.03 (-0.03--0.02) | 0; 0 of 24 logs | 100.0 % | 127 | 1.3 (1.2-1.3) | 3.8 |
| 30 % | VLM + 2 units | 20 % (20-20) | 19 % (19-19) | 70 % (70-71) (1E) | -0.03 (-0.04-0.02) | 0; 0 of 24 logs | 100.0 % | 127 | 1.6 (1.6-1.7) | 4.9 |
| 30 % | flat + 1 unit | 43 % (43-44) | - | - | 0.02 (0.01-0.04) | 0; 0 of 24 logs | 100.0 % | 127 | 1.3 (1.3-1.3) | 3.8 |
| 60 % | VLM + 1 unit | 68 % (67-70) | 28 % (27-29) | 85 % (84-87) (1D) | 0.06 (0.04-0.16) | 0; 0 of 24 logs | 90.5 % | 230 | 10.5 (10.2-10.9) | 29.5 |
| 60 % | flat + 2 units | 39 % (39-39) | - | - | -0.02 (-0.02--0.01) | 0; 0 of 24 logs | 100.0 % | 255 | 2.0 (2.0-2.1) | 5.6 |
| 60 % | VLM + 2 units | 33 % (33-33) | 28 % (28-28) | 89 % (88-89) (1D) | -0.02 (-0.03-0.03) | 0; 0 of 24 logs | 94.0 % | 240 | 7.6 (7.4-7.7) | 24.7 |
| 60 % | flat + 1 unit | 74 % (73-75) | - | - | 572.25 (326.06-929.24) | 446; 24 of 24 logs | 90.5 % | 231 | 7.9 (7.3-8.2) | 15.6 |

Days to the twin's targets, later than the twin's own day:

| Outside load | Layout | Al SOTA: days later (median, max) | Al halfway: days later (median, max) | Cu SOTA: days later (median, max) | Cu halfway: days later (median, max) |
|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | -0.00 (0.15; n=18) | -0.00 (0.02; n=12) | 0.00 (0.00; n=19) | -0.00 (0.00; n=15) |
| 0 % | flat + 2 units | -0.00 (0.00; n=18) | -0.00 (0.00; n=12) | -0.00 (0.00; n=19) | -0.00 (0.00; n=15) |
| 0 % | VLM + 2 units | -0.00 (0.02; n=18) | -0.00 (0.01; n=12) | -0.00 (-0.00; n=19) | -0.00 (-0.00; n=15) |
| 0 % | flat + 1 unit | -0.00 (0.00; n=18) | -0.00 (0.01; n=12) | 0.00 (0.00; n=19) | -0.00 (0.00; n=15) |
| 30 % | VLM + 1 unit | 0.00 (0.13; n=18) | 0.00 (0.01; n=12) | 0.00 (0.01; n=19) | 0.00 (0.01; n=15) |
| 30 % | flat + 2 units | -0.00 (0.00; n=18) | -0.00 (0.00; n=12) | -0.00 (0.00; n=19) | -0.00 (0.00; n=15) |
| 30 % | VLM + 2 units | -0.00 (0.02; n=18) | 0.00 (0.02; n=12) | -0.00 (0.01; n=19) | -0.00 (0.04; n=15) |
| 30 % | flat + 1 unit | 0.00 (0.02; n=18) | 0.00 (0.01; n=12) | 0.00 (0.02; n=19) | 0.00 (0.02; n=15) |
| 60 % | VLM + 1 unit | 0.01 (0.13; n=18) | 0.01 (0.01; n=12) | 0.00 (0.08; n=19) | 0.01 (0.05; n=15) |
| 60 % | flat + 2 units | 0.00 (0.01; n=18) | 0.00 (0.01; n=12) | -0.00 (0.01; n=19) | -0.00 (0.01; n=15) |
| 60 % | VLM + 2 units | 0.00 (0.14; n=18) | 0.00 (0.02; n=12) | -0.00 (0.06; n=19) | -0.00 (0.05; n=15) |
| 60 % | flat + 1 unit | 0.06 (94.00; n=18) | 6.95 (94.00; n=12) | 19.81 (73.65; n=19) | 19.81 (90.42; n=15) |

Handling:

| Outside load | Layout | Driving a task (s) | Waiting for the tray after arriving (s) | Request to the arm at the instrument, internal (min) | the same, outside jobs (min) | Tray presentations a day (both Shuttles) | Attended arm-hours a day |
|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | 43 | 16 | 1.9 | - | 6 | 0.0 |
| 0 % | flat + 2 units | 81 | - | 2.2 | - | - | 0.0 |
| 0 % | VLM + 2 units | 61 | 15 | 1.7 | - | 6 | 0.0 |
| 0 % | flat + 1 unit | 58 | - | 2.3 | - | - | 0.0 |
| 30 % | VLM + 1 unit | 42 | 10 | 3.6 | 41.3 | 140 | 0.0 |
| 30 % | flat + 2 units | 63 | - | 2.8 | 17.8 | - | 0.0 |
| 30 % | VLM + 2 units | 40 | 12 | 2.4 | 35.9 | 134 | 0.0 |
| 30 % | flat + 1 unit | 60 | - | 4.3 | 20.0 | - | 0.0 |
| 60 % | VLM + 1 unit | 37 | 11 | 4.9 | 560.5 | 185 | 0.0 |
| 60 % | flat + 2 units | 53 | - | 3.2 | 63.1 | - | 0.0 |
| 60 % | VLM + 2 units | 29 | 15 | 2.7 | 385.9 | 159 | 0.0 |
| 60 % | flat + 1 unit | 55 | - | 3,527.6 | 414.0 | - | 0.0 |

## Timing: PR 332's attended time (the arm stays for its share of each step; the powder line in a cell)

| Outside load | Layout | Units busy | Busiest opening busy | Busiest tray held by a run | Internal steps end later than the twin's, mean (h) | Atomizer runs off their slot | Outside jobs served | Outside jobs a day | Outside turnaround (h) | Outside turnaround, 95th pct (h) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | 2 % (2-3) | 1 % (1-2) | 2 % (2-3) (1D) | -0.06 (-0.07-0.03) | 0; 0 of 24 logs | - | - | - | - |
| 0 % | flat + 2 units | 1 % (1-2) | - | - | -0.06 (-0.07--0.05) | 0; 0 of 24 logs | - | - | - | - |
| 0 % | VLM + 2 units | 1 % (1-2) | 1 % (1-2) | 2 % (2-3) (1D) | -0.07 (-0.07-0.01) | 0; 0 of 24 logs | - | - | - | - |
| 0 % | flat + 1 unit | 2 % (2-3) | - | - | -0.06 (-0.07--0.04) | 0; 0 of 24 logs | - | - | - | - |
| 30 % | VLM + 1 unit | 82 % (81-82) | 41 % (26-43) | 44 % (38-51) (1F) | 13.33 (0.33-791.11) | 24; 16 of 24 logs | 60.6 % | 77 | 57.0 (47.3-65.1) | 78.9 |
| 30 % | flat + 2 units | 68 % (67-68) | - | - | 0.07 (0.03-0.18) | 0; 2 of 24 logs | 100.0 % | 127 | 1.7 (1.6-1.8) | 4.6 |
| 30 % | VLM + 2 units | 67 % (66-67) | 60 % (59-60) | 53 % (52-53) (1E) | 0.03 (0.01-0.21) | 0; 2 of 24 logs | 100.0 % | 127 | 2.5 (2.3-2.8) | 7.8 |
| 30 % | flat + 1 unit | 82 % (82-82) | - | - | 1.36 (0.37-514.65) | 8; 19 of 24 logs | 59.3 % | 76 | 59.2 (49.3-67.3) | 81.1 |
| 60 % | VLM + 1 unit | 82 % (82-83) | 31 % (20-43) | 62 % (52-70) (1F) | 38.82 (0.39-641.62) | 109; 18 of 24 logs | 30.6 % | 78 | 72.6 (64.7-79.4) | 141.7 |
| 60 % | flat + 2 units | 82 % (82-82) | - | - | 0.30 (0.13-260.33) | 0; 8 of 24 logs | 61.2 % | 156 | 29.8 (25.0-33.2) | 39.9 |
| 60 % | VLM + 2 units | 82 % (82-82) | 63 % (59-68) | 65 % (63-76) (1F) | 0.27 (0.11-1.11) | 0; 8 of 24 logs | 62.8 % | 160 | 28.2 (23.6-31.7) | 53.7 |
| 60 % | flat + 1 unit | 82 % (82-82) | - | - | 42.38 (0.37-686.88) | 124; 19 of 24 logs | 29.7 % | 76 | 76.0 (67.3-82.0) | 132.5 |

Days to the twin's targets, later than the twin's own day:

| Outside load | Layout | Al SOTA: days later (median, max) | Al halfway: days later (median, max) | Cu SOTA: days later (median, max) | Cu halfway: days later (median, max) |
|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | -0.00 (0.14; n=18) | -0.00 (0.02; n=12) | -0.00 (0.01; n=19) | -0.00 (0.01; n=15) |
| 0 % | flat + 2 units | -0.00 (0.01; n=18) | -0.00 (0.00; n=12) | -0.00 (0.01; n=19) | -0.00 (0.01; n=15) |
| 0 % | VLM + 2 units | -0.00 (0.15; n=18) | -0.00 (0.02; n=12) | -0.00 (0.01; n=19) | -0.00 (-0.00; n=15) |
| 0 % | flat + 1 unit | -0.00 (0.02; n=18) | -0.00 (0.02; n=12) | -0.00 (0.01; n=19) | -0.00 (0.01; n=15) |
| 30 % | VLM + 1 unit | 0.16 (28.97; n=18) | 0.25 (15.50; n=12) | 0.06 (80.95; n=19) | 0.04 (72.75; n=15) |
| 30 % | flat + 2 units | 0.02 (0.15; n=18) | 0.02 (0.12; n=12) | 0.00 (14.77; n=19) | 0.01 (20.00; n=15) |
| 30 % | VLM + 2 units | 0.01 (0.15; n=18) | 0.02 (0.14; n=12) | 0.01 (0.09; n=19) | 0.01 (0.09; n=15) |
| 30 % | flat + 1 unit | 0.18 (28.59; n=18) | 0.18 (15.58; n=12) | 0.08 (52.84; n=19) | 0.10 (72.86; n=15) |
| 60 % | VLM + 1 unit | 0.20 (29.22; n=18) | 0.30 (15.56; n=12) | 0.10 (55.87; n=19) | 0.14 (59.00; n=15) |
| 60 % | flat + 2 units | 0.05 (74.96; n=18) | 0.11 (74.96; n=12) | 0.04 (80.73; n=19) | 0.04 (80.11; n=15) |
| 60 % | VLM + 2 units | 0.04 (0.28; n=18) | 0.04 (0.36; n=12) | 0.02 (14.82; n=19) | 0.04 (20.11; n=15) |
| 60 % | flat + 1 unit | 0.20 (74.96; n=18) | 0.30 (74.96; n=12) | 0.14 (56.22; n=19) | 0.14 (77.19; n=15) |

Handling:

| Outside load | Layout | Driving a task (s) | Waiting for the tray after arriving (s) | Request to the arm at the instrument, internal (min) | the same, outside jobs (min) | Tray presentations a day (both Shuttles) | Attended arm-hours a day |
|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | 36 | 22 | 2.3 | - | 4 | 0.3 |
| 0 % | flat + 2 units | 69 | - | 2.4 | - | - | 0.3 |
| 0 % | VLM + 2 units | 47 | 21 | 1.7 | - | 4 | 0.3 |
| 0 % | flat + 1 unit | 53 | - | 2.5 | - | - | 0.3 |
| 30 % | VLM + 1 unit | 44 | 17 | 24.4 | 3,319.0 | 93 | 13.6 |
| 30 % | flat + 2 units | 51 | - | 8.7 | 40.5 | - | 22.9 |
| 30 % | VLM + 2 units | 32 | 21 | 7.4 | 83.6 | 128 | 22.9 |
| 30 % | flat + 1 unit | 68 | - | 25.2 | 3,459.6 | - | 13.3 |
| 60 % | VLM + 1 unit | 44 | 15 | 28.7 | 4,227.0 | 76 | 13.6 |
| 60 % | flat + 2 units | 57 | - | 15.1 | 1,707.4 | - | 27.3 |
| 60 % | VLM + 2 units | 38 | 21 | 13.8 | 1,607.8 | 149 | 27.5 |
| 60 % | flat + 1 unit | 67 | - | 32.2 | 4,440.2 | - | 13.3 |
