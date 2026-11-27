# Round 5's automated lab through the same model (issue #407)

Written by `python -m twin.worth_it run5 <dir>` from `out/worth_it/results_r5.json.xz`. Simulated: round 5's 16 two-year logs of the automated lab (PR 405: built from the day the money arrives, every route at once, decisions that wait for people as nominal, the cheap policies), its own instruments only (BYU's existing equipment, core facilities and partners are served by people, so they are left out), outside jobs from the day its first instrument opens. Days to targets are not computed: round 5's targets are its own. Medians over the logs, 10th-90th percentile in brackets.

## Timing: the twin's timing (a load and an unload a step)

| Outside load | Layout | Units busy | Busiest opening busy | Busiest tray held by a run | Internal steps end later than the twin's, mean (h) | Atomizer runs off their slot | Outside jobs served | Outside jobs a day | Outside turnaround (h) | Outside turnaround, 95th pct (h) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | 2 % (2-2) | 1 % (1-1) | 5 % (4-5) (1F) | 0.11 (0.06-0.17) | 3; 10 of 16 logs | - | - | - | - |
| 0 % | flat + 2 units | 1 % (1-1) | - | - | -0.04 (-0.04--0.03) | 0; 0 of 16 logs | - | - | - | - |
| 0 % | VLM + 2 units | 1 % (1-1) | 1 % (1-1) | 5 % (4-5) (1F) | 0.10 (0.05-0.16) | 2; 8 of 16 logs | - | - | - | - |
| 0 % | flat + 1 unit | 2 % (2-2) | - | - | -0.03 (-0.03--0.02) | 0; 1 of 16 logs | - | - | - | - |
| 30 % | VLM + 1 unit | 35 % (35-36) | 17 % (17-18) | 61 % (59-63) (1E) | 0.30 (0.19-0.48) | 81; 16 of 16 logs | 99.9 % | 111 | 2.3 (2.1-2.4) | 6.2 |
| 30 % | flat + 2 units | 19 % (18-19) | - | - | -0.02 (-0.02--0.01) | 0; 0 of 16 logs | 100.0 % | 111 | 1.4 (1.3-1.6) | 3.9 |
| 30 % | VLM + 2 units | 17 % (17-18) | 17 % (16-17) | 61 % (60-63) (1E) | 0.13 (0.07-0.19) | 1; 8 of 16 logs | 100.0 % | 111 | 2.0 (1.8-2.1) | 5.4 |
| 30 % | flat + 1 unit | 38 % (37-39) | - | - | 0.14 (0.08-0.32) | 114; 16 of 16 logs | 100.0 % | 111 | 1.5 (1.4-1.6) | 4.0 |
| 60 % | VLM + 1 unit | 57 % (55-58) | 24 % (23-24) | 75 % (73-77) (1D) | 0.47 (0.33-0.76) | 176; 16 of 16 logs | 86.3 % | 194 | 11.9 (11.1-12.2) | 32.0 |
| 60 % | flat + 2 units | 34 % (34-35) | - | - | 0.00 (-0.01-0.01) | 0; 0 of 16 logs | 99.9 % | 222 | 2.4 (2.3-2.5) | 5.8 |
| 60 % | VLM + 2 units | 29 % (28-29) | 24 % (24-25) | 77 % (76-80) (1D) | 0.15 (0.09-0.23) | 11; 13 of 16 logs | 93.5 % | 208 | 8.2 (8.1-8.4) | 25.3 |
| 60 % | flat + 1 unit | 69 % (69-72) | - | - | 1.34 (1.03-3.07) | 460; 16 of 16 logs | 98.0 % | 219 | 5.6 (5.2-6.5) | 17.0 |

Handling:

| Outside load | Layout | Driving a task (s) | Waiting for the tray after arriving (s) | Request to the arm at the instrument, internal (min) | the same, outside jobs (min) | Tray presentations a day (both Shuttles) | Attended arm-hours a day |
|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | 49 | 14 | 4.7 | - | 5 | 0.0 |
| 0 % | flat + 2 units | 81 | - | 2.2 | - | - | 0.0 |
| 0 % | VLM + 2 units | 72 | 14 | 4.2 | - | 5 | 0.0 |
| 0 % | flat + 1 unit | 67 | - | 2.5 | - | - | 0.0 |
| 30 % | VLM + 1 unit | 41 | 10 | 7.9 | 74.2 | 121 | 0.0 |
| 30 % | flat + 2 units | 63 | - | 2.9 | 27.0 | - | 0.0 |
| 30 % | VLM + 2 units | 40 | 12 | 5.0 | 54.4 | 117 | 0.0 |
| 30 % | flat + 1 unit | 60 | - | 5.9 | 32.1 | - | 0.0 |
| 60 % | VLM + 1 unit | 35 | 11 | 10.2 | 639.8 | 152 | 0.0 |
| 60 % | flat + 2 units | 52 | - | 3.3 | 85.1 | - | 0.0 |
| 60 % | VLM + 2 units | 29 | 14 | 5.7 | 423.1 | 136 | 0.0 |
| 60 % | flat + 1 unit | 55 | - | 22.2 | 276.8 | - | 0.0 |

## Timing: PR 332's attended time (the arm stays for its share of each step; the powder line in a cell)

| Outside load | Layout | Units busy | Busiest opening busy | Busiest tray held by a run | Internal steps end later than the twin's, mean (h) | Atomizer runs off their slot | Outside jobs served | Outside jobs a day | Outside turnaround (h) | Outside turnaround, 95th pct (h) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | 4 % (3-4) | 2 % (2-2) | 4 % (4-5) (1F) | 0.19 (0.12-0.31) | 4; 14 of 16 logs | - | - | - | - |
| 0 % | flat + 2 units | 2 % (2-2) | - | - | -0.02 (-0.03--0.01) | 0; 2 of 16 logs | - | - | - | - |
| 0 % | VLM + 2 units | 2 % (2-2) | 2 % (2-2) | 5 % (4-5) (1F) | 0.10 (0.06-0.19) | 2; 12 of 16 logs | - | - | - | - |
| 0 % | flat + 1 unit | 4 % (3-4) | - | - | 0.01 (-0.01-0.04) | 0; 6 of 16 logs | - | - | - | - |
| 30 % | VLM + 1 unit | 72 % (71-74) | 22 % (21-36) | 38 % (37-39) (1F) | 6.49 (2.13-9.80) | 350; 16 of 16 logs | 49.7 % | 56 | 70.4 (56.5-72.9) | 214.0 |
| 30 % | flat + 2 units | 59 % (58-61) | - | - | 0.51 (0.38-0.69) | 39; 16 of 16 logs | 100.0 % | 111 | 2.3 (2.0-2.7) | 6.1 |
| 30 % | VLM + 2 units | 59 % (58-61) | 52 % (51-54) | 45 % (44-48) (1E) | 0.51 (0.40-0.66) | 28; 16 of 16 logs | 99.6 % | 111 | 3.6 (3.4-4.1) | 12.4 |
| 30 % | flat + 1 unit | 72 % (70-74) | - | - | 6.94 (1.89-10.71) | 366; 16 of 16 logs | 49.1 % | 56 | 71.0 (58.7-74.1) | 230.5 |
| 60 % | VLM + 1 unit | 73 % (71-75) | 21 % (20-33) | 47 % (44-52) (1F) | 25.55 (2.40-112.64) | 474; 16 of 16 logs | 22.8 % | 52 | 102.0 (75.4-108.8) | 163.1 |
| 60 % | flat + 2 units | 72 % (71-74) | - | - | 2.07 (0.84-2.63) | 187; 16 of 16 logs | 51.3 % | 116 | 35.5 (29.3-36.4) | 134.3 |
| 60 % | VLM + 2 units | 72 % (71-74) | 41 % (40-55) | 55 % (54-57) (1F) | 1.53 (0.79-2.08) | 167; 16 of 16 logs | 53.3 % | 120 | 34.2 (27.3-35.0) | 91.4 |
| 60 % | flat + 1 unit | 73 % (71-75) | - | - | 38.02 (2.42-164.32) | 470; 16 of 16 logs | 22.9 % | 52 | 100.4 (78.6-106.8) | 154.9 |

Handling:

| Outside load | Layout | Driving a task (s) | Waiting for the tray after arriving (s) | Request to the arm at the instrument, internal (min) | the same, outside jobs (min) | Tray presentations a day (both Shuttles) | Attended arm-hours a day |
|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | 51 | 17 | 7.8 | - | 5 | 0.5 |
| 0 % | flat + 2 units | 82 | - | 3.6 | - | - | 0.5 |
| 0 % | VLM + 2 units | 63 | 16 | 6.0 | - | 5 | 0.5 |
| 0 % | flat + 1 unit | 72 | - | 4.2 | - | - | 0.5 |
| 30 % | VLM + 1 unit | 50 | 10 | 85.1 | 4,086.8 | 55 | 12.6 |
| 30 % | flat + 2 units | 51 | - | 16.4 | 70.4 | - | 20.2 |
| 30 % | VLM + 2 units | 33 | 20 | 16.1 | 147.1 | 110 | 20.1 |
| 30 % | flat + 1 unit | 61 | - | 86.5 | 4,129.2 | - | 12.6 |
| 60 % | VLM + 1 unit | 40 | 5 | 259.3 | 5,959.3 | 31 | 13.6 |
| 60 % | flat + 2 units | 45 | - | 41.3 | 2,032.7 | - | 26.1 |
| 60 % | VLM + 2 units | 39 | 15 | 33.4 | 1,950.9 | 92 | 25.5 |
| 60 % | flat + 1 unit | 46 | - | 334.9 | 5,871.3 | - | 13.5 |
