# Round 5's automated lab through the same model (issue #407)

Written by `python -m twin.worth_it run5 <dir>` from `out/worth_it/results_r5.json.xz`. Simulated: round 5's 16 two-year logs of the automated lab (PR 405: built from the day the money arrives, every route at once, decisions that wait for people as nominal, the cheap policies), its own instruments only (BYU's existing equipment, core facilities and partners are served by people, so they are left out), outside jobs from the day its first instrument opens. Days to targets are not computed: round 5's targets are its own. Medians over the logs, 10th-90th percentile in brackets.

## Timing: the twin's timing (a load and an unload a step)

| Outside load | Layout | Units busy | Busiest opening busy | Busiest tray held by a run | Internal steps end later than the twin's, mean (h) | Atomizer runs off their slot | Outside jobs served | Outside jobs a day | Outside turnaround (h) | Outside turnaround, 95th pct (h) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | 2 % (2-2) | 1 % (1-1) | 5 % (5-5) (1F) | 0.12 (0.07-0.18) | 3; 10 of 16 logs | - | - | - | - |
| 0 % | flat + 2 units | 1 % (1-1) | - | - | -0.04 (-0.04--0.03) | 0; 0 of 16 logs | - | - | - | - |
| 0 % | VLM + 2 units | 1 % (1-1) | 1 % (1-1) | 5 % (5-5) (1F) | 0.10 (0.05-0.17) | 2; 9 of 16 logs | - | - | - | - |
| 0 % | flat + 1 unit | 2 % (2-2) | - | - | -0.03 (-0.03--0.02) | 0; 1 of 16 logs | - | - | - | - |
| 30 % | VLM + 1 unit | 36 % (35-37) | 17 % (17-18) | 62 % (60-63) (1E) | 0.25 (0.18-0.37) | 44; 16 of 16 logs | 100.0 % | 111 | 2.2 (2.0-2.4) | 5.8 |
| 30 % | flat + 2 units | 19 % (18-19) | - | - | -0.02 (-0.02--0.01) | 0; 0 of 16 logs | 100.0 % | 111 | 1.4 (1.3-1.5) | 3.9 |
| 30 % | VLM + 2 units | 17 % (17-18) | 17 % (16-17) | 62 % (61-64) (1E) | 0.13 (0.07-0.19) | 4; 10 of 16 logs | 100.0 % | 111 | 2.0 (1.8-2.1) | 5.3 |
| 30 % | flat + 1 unit | 38 % (37-39) | - | - | 0.26 (0.14-0.52) | 156; 16 of 16 logs | 100.0 % | 111 | 1.6 (1.4-1.7) | 4.1 |
| 60 % | VLM + 1 unit | 59 % (58-61) | 24 % (24-25) | 70 % (68-73) (1D) | 0.78 (0.59-1.09) | 354; 16 of 16 logs | 87.9 % | 196 | 13.8 (13.6-14.1) | 31.6 |
| 60 % | flat + 2 units | 34 % (34-35) | - | - | 0.01 (0.00-0.03) | 0; 3 of 16 logs | 99.9 % | 222 | 2.4 (2.3-2.6) | 5.8 |
| 60 % | VLM + 2 units | 29 % (28-30) | 24 % (24-25) | 77 % (75-79) (1D) | 0.14 (0.08-0.21) | 4; 12 of 16 logs | 94.3 % | 210 | 8.0 (7.9-8.1) | 24.6 |
| 60 % | flat + 1 unit | 68 % (66-70) | - | - | 1.86 (1.25-4.29) | 536; 16 of 16 logs | 91.2 % | 203 | 14.3 (14.2-14.7) | 22.2 |

Handling:

| Outside load | Layout | Driving a task (s) | Waiting for the tray after arriving (s) | Request to the arm at the instrument, internal (min) | the same, outside jobs (min) | Tray presentations a day (both Shuttles) | Attended arm-hours a day |
|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | 49 | 14 | 4.8 | - | 5 | 0.0 |
| 0 % | flat + 2 units | 81 | - | 2.2 | - | - | 0.0 |
| 0 % | VLM + 2 units | 72 | 14 | 4.3 | - | 5 | 0.0 |
| 0 % | flat + 1 unit | 67 | - | 2.5 | - | - | 0.0 |
| 30 % | VLM + 1 unit | 42 | 10 | 7.3 | 67.4 | 122 | 0.0 |
| 30 % | flat + 2 units | 63 | - | 2.9 | 27.1 | - | 0.0 |
| 30 % | VLM + 2 units | 40 | 12 | 5.1 | 56.6 | 117 | 0.0 |
| 30 % | flat + 1 unit | 61 | - | 7.6 | 36.5 | - | 0.0 |
| 60 % | VLM + 1 unit | 39 | 11 | 15.1 | 752.7 | 160 | 0.0 |
| 60 % | flat + 2 units | 53 | - | 3.5 | 87.5 | - | 0.0 |
| 60 % | VLM + 2 units | 29 | 15 | 5.4 | 412.4 | 139 | 0.0 |
| 60 % | flat + 1 unit | 61 | - | 27.5 | 792.3 | - | 0.0 |

## Timing: PR 332's attended time (the arm stays for its share of each step; the powder line in a cell)

| Outside load | Layout | Units busy | Busiest opening busy | Busiest tray held by a run | Internal steps end later than the twin's, mean (h) | Atomizer runs off their slot | Outside jobs served | Outside jobs a day | Outside turnaround (h) | Outside turnaround, 95th pct (h) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | 4 % (3-4) | 2 % (2-2) | 5 % (4-5) (1F) | 0.19 (0.12-0.31) | 4; 14 of 16 logs | - | - | - | - |
| 0 % | flat + 2 units | 2 % (2-2) | - | - | -0.02 (-0.03--0.01) | 0; 2 of 16 logs | - | - | - | - |
| 0 % | VLM + 2 units | 2 % (2-2) | 2 % (2-2) | 5 % (4-5) (1F) | 0.11 (0.06-0.20) | 2; 12 of 16 logs | - | - | - | - |
| 0 % | flat + 1 unit | 4 % (3-4) | - | - | 0.01 (-0.01-0.04) | 0; 6 of 16 logs | - | - | - | - |
| 30 % | VLM + 1 unit | 72 % (70-74) | 37 % (36-38) | 40 % (39-41) (1F) | 1.56 (1.31-2.15) | 143; 16 of 16 logs | 59.2 % | 66 | 67.9 (67.2-68.3) | 85.7 |
| 30 % | flat + 2 units | 60 % (59-61) | - | - | 0.38 (0.30-0.46) | 20; 16 of 16 logs | 100.0 % | 111 | 2.4 (2.2-2.9) | 6.3 |
| 30 % | VLM + 2 units | 59 % (58-61) | 52 % (51-54) | 46 % (45-48) (1E) | 0.48 (0.38-0.61) | 19; 16 of 16 logs | 99.7 % | 111 | 4.1 (3.7-4.4) | 13.5 |
| 30 % | flat + 1 unit | 72 % (70-74) | - | - | 1.22 (1.12-1.93) | 120; 16 of 16 logs | 57.7 % | 64 | 70.4 (69.6-71.0) | 94.6 |
| 60 % | VLM + 1 unit | 72 % (70-74) | 37 % (36-38) | 47 % (46-49) (1F) | 1.57 (1.32-2.11) | 124; 16 of 16 logs | 29.7 % | 66 | 82.1 (81.4-82.8) | 99.2 |
| 60 % | flat + 2 units | 72 % (70-74) | - | - | 0.49 (0.40-0.57) | 30; 16 of 16 logs | 60.4 % | 135 | 34.4 (34.1-34.6) | 40.8 |
| 60 % | VLM + 2 units | 72 % (70-74) | 59 % (57-60) | 55 % (53-56) (1F) | 0.60 (0.50-0.78) | 33; 16 of 16 logs | 61.4 % | 137 | 33.5 (33.3-33.8) | 54.9 |
| 60 % | flat + 1 unit | 72 % (70-74) | - | - | 1.29 (1.10-1.94) | 111; 16 of 16 logs | 28.8 % | 64 | 84.8 (84.2-85.6) | 106.6 |

Handling:

| Outside load | Layout | Driving a task (s) | Waiting for the tray after arriving (s) | Request to the arm at the instrument, internal (min) | the same, outside jobs (min) | Tray presentations a day (both Shuttles) | Attended arm-hours a day |
|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 unit | 51 | 17 | 8.0 | - | 5 | 0.5 |
| 0 % | flat + 2 units | 82 | - | 3.6 | - | - | 0.5 |
| 0 % | VLM + 2 units | 63 | 16 | 6.3 | - | 5 | 0.5 |
| 0 % | flat + 1 unit | 72 | - | 4.2 | - | - | 0.5 |
| 30 % | VLM + 1 unit | 45 | 16 | 32.0 | 3,977.4 | 84 | 11.9 |
| 30 % | flat + 2 units | 53 | - | 13.7 | 80.3 | - | 20.2 |
| 30 % | VLM + 2 units | 34 | 20 | 16.1 | 175.9 | 113 | 20.2 |
| 30 % | flat + 1 unit | 71 | - | 28.7 | 4,136.1 | - | 11.6 |
| 60 % | VLM + 1 unit | 46 | 16 | 31.7 | 4,817.2 | 81 | 11.9 |
| 60 % | flat + 2 units | 60 | - | 16.2 | 1,982.7 | - | 23.8 |
| 60 % | VLM + 2 units | 40 | 20 | 18.0 | 1,926.3 | 134 | 24.0 |
| 60 % | flat + 1 unit | 73 | - | 28.8 | 4,984.4 | - | 11.6 |
