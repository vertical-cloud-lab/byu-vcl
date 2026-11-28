# Sensitivities (issue #407)

Written by `python -m twin.worth_it tables` from `out/worth_it/sensitivity.json.xz`: 4 logs (BOFN and the funnel, seeds 0-1), every layout, 30 % and 60 % outside load. Medians over the logs.

## 30 % outside load

| Case | VLM + 1 unit: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy | flat + 2 units: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy | VLM + 2 units: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy | flat + 1 unit: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy |
|---|---|---|---|---|
| base (the twin's timing) | 1.7; 100 %; 0.0; 0; 41 %; 20 % | 1.3; 100 %; -0.0; 0; 21 %; - | 1.6; 100 %; -0.0; 0; 20 %; 19 % | 1.3; 100 %; 0.0; 0; 44 %; - |
| attended time (PR 332, powder line in a cell) | 65.6; 60 %; 0.7; 5; 82 %; 43 % | 1.9; 100 %; 0.1; 0; 68 %; - | 2.7; 100 %; 0.1; 0; 67 %; 60 % | 67.9; 59 %; 0.9; 37; 82 %; - |
| attended time everywhere (PR 332; the replay loses atomizer slots) | 65.9; 56 %; 180.6; 495; 83 %; 28 % | 5.9; 96 %; 31.9; 399; 70 %; - | 12.9; 89 %; 13.7; 306; 65 %; 51 % | 75.2; 54 %; 228.7; 505; 84 %; - |
| trays may move while instruments run | 1.3; 100 %; -0.0; 0; 43 %; 22 % | 1.3; 100 %; -0.0; 0; 21 %; - | 1.3; 100 %; -0.0; 0; 21 %; 22 % | 1.3; 100 %; 0.0; 0; 44 %; - |
| attended, trays may move while instruments run | 66.0; 60 %; 0.9; 35; 82 %; 44 % | 1.9; 100 %; 0.1; 0; 68 %; - | 1.8; 100 %; 0.1; 0; 68 %; 62 % | 67.9; 59 %; 0.9; 37; 82 %; - |
| gentle trays (2.5x slower) | 1.8; 100 %; 0.0; 0; 44 %; 24 % | 1.3; 100 %; -0.0; 0; 21 %; - | 1.7; 100 %; -0.0; 0; 21 %; 23 % | 1.3; 100 %; 0.0; 0; 44 %; - |
| attended, gentle trays (2.5x slower) | 69.1; 58 %; 0.7; 4; 82 %; 46 % | 1.9; 100 %; 0.1; 0; 68 %; - | 3.2; 100 %; 0.1; 0; 70 %; 64 % | 67.9; 59 %; 0.9; 37; 82 %; - |
| no pre-fetch (the Shuttle waits for the unit) | 1.8; 100 %; 0.0; 0; 44 %; 17 % | 1.3; 100 %; -0.0; 0; 21 %; - | 1.6; 100 %; -0.0; 0; 21 %; 17 % | 1.3; 100 %; 0.0; 0; 44 %; - |
| slow handling (dock 150 s, load 120 s) | 16.3; 85 %; 26.5; 376; 66 %; 25 % | 1.4; 100 %; 0.2; 0; 40 %; - | 1.9; 100 %; 0.2; 0; 36 %; 32 % | 13.0; 94 %; 83.3; 438; 80 %; - |
| fast handling (dock 30 s, load 30 s) | 1.6; 100 %; -0.0; 0; 26 %; 14 % | 1.2; 100 %; -0.1; 0; 13 %; - | 1.5; 100 %; -0.1; 0; 13 %; 13 % | 1.2; 100 %; -0.1; 0; 27 %; - |
| driving at 0.3 m/s (Liverpool's cap) | 1.8; 100 %; 0.0; 0; 44 %; 20 % | 1.3; 100 %; 0.0; 0; 24 %; - | 1.6; 100 %; -0.0; 0; 21 %; 20 % | 2.3; 99 %; 7.0; 114; 50 %; - |
| driving at 1.5 m/s | 1.7; 100 %; 0.0; 0; 41 %; 20 % | 1.2; 100 %; -0.0; 0; 21 %; - | 1.6; 100 %; -0.0; 0; 20 %; 19 % | 1.3; 100 %; 0.0; 0; 42 %; - |
| a bare MiR250's battery (13 h a charge, 52 min to charge) | 1.7; 100 %; 0.0; 0; 41 %; 20 % | 1.3; 100 %; -0.0; 0; 21 %; - | 1.6; 100 %; -0.0; 0; 20 %; 19 % | 1.3; 100 %; 0.0; 0; 44 %; - |
| attended, a bare MiR250's battery | 52.3; 69 %; 0.3; 2; 94 %; 49 % | 1.6; 100 %; 0.0; 0; 67 %; - | 2.4; 100 %; 0.0; 0; 67 %; 60 % | 54.2; 68 %; 0.5; 5; 94 %; - |
| aisles shared (flat) | 1.7; 100 %; 0.0; 0; 41 %; 20 % | 1.2; 100 %; -0.0; 0; 22 %; - | 1.6; 100 %; -0.0; 0; 20 %; 19 % | 1.3; 100 %; 0.0; 0; 44 %; - |
| outside samples carried from packaging | 4.2; 97 %; 3.6; 84; 56 %; 26 % | 1.4; 100 %; -0.0; 0; 31 %; - | 1.8; 100 %; -0.0; 0; 28 %; 28 % | 3.7; 98 %; 17.8; 266; 62 %; - |
| outside work first come, first served (no gaps kept for internal work) | 1.6; 100 %; 1.1; 3; 41 %; 20 % | 1.2; 100 %; 0.6; 0; 22 %; - | 1.5; 100 %; 1.2; 3; 20 %; 19 % | 1.3; 100 %; 0.7; 1; 44 %; - |
| attended, outside work first come, first served | 65.4; 60 %; 1.9; 40; 82 %; 43 % | 1.8; 100 %; 0.8; 2; 68 %; - | 2.5; 100 %; 1.4; 5; 67 %; 60 % | 67.9; 59 %; 1.5; 38; 82 %; - |

## 60 % outside load

| Case | VLM + 1 unit: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy | flat + 2 units: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy | VLM + 2 units: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy | flat + 1 unit: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy |
|---|---|---|---|---|
| base (the twin's timing) | 14.1; 82 %; 12.8; 231; 63 %; 24 % | 2.0; 100 %; -0.0; 0; 40 %; - | 7.5; 94 %; -0.0; 0; 33 %; 28 % | 12.3; 89 %; 56.4; 418; 76 %; - |
| attended time (PR 332, powder line in a cell) | 79.6; 30 %; 0.7; 5; 82 %; 43 % | 33.6; 61 %; 0.2; 0; 82 %; - | 32.4; 62 %; 0.1; 0; 82 %; 67 % | 82.2; 29 %; 0.6; 4; 82 %; - |
| attended time everywhere (PR 332; the replay loses atomizer slots) | 83.7; 29 %; 174.8; 494; 83 %; 30 % | 34.8; 59 %; 45.1; 420; 83 %; - | 33.5; 59 %; 15.6; 278; 82 %; 57 % | 89.7; 27 %; 208.8; 496; 83 %; - |
| trays may move while instruments run | 12.3; 90 %; 63.0; 379; 76 %; 36 % | 2.0; 100 %; -0.0; 0; 40 %; - | 2.0; 100 %; -0.0; 0; 39 %; 39 % | 12.3; 89 %; 56.4; 418; 76 %; - |
| attended, trays may move while instruments run | 80.1; 30 %; 1.9; 22; 82 %; 43 % | 33.6; 61 %; 0.2; 0; 82 %; - | 33.2; 62 %; 0.2; 0; 82 %; 84 % | 82.2; 29 %; 0.6; 4; 82 %; - |
| gentle trays (2.5x slower) | 16.1; 77 %; 20.8; 338; 63 %; 29 % | 2.0; 100 %; -0.0; 0; 40 %; - | 7.9; 93 %; 0.0; 0; 35 %; 33 % | 12.3; 89 %; 56.4; 418; 76 %; - |
| attended, gentle trays (2.5x slower) | 82.7; 29 %; 0.9; 8; 82 %; 45 % | 33.6; 61 %; 0.2; 0; 82 %; - | 34.1; 60 %; 0.2; 0; 82 %; 71 % | 82.2; 29 %; 0.6; 4; 82 %; - |
| no pre-fetch (the Shuttle waits for the unit) | 16.3; 78 %; 16.1; 279; 65 %; 20 % | 2.0; 100 %; -0.0; 0; 40 %; - | 7.7; 94 %; -0.0; 0; 35 %; 26 % | 12.3; 89 %; 56.4; 418; 76 %; - |
| slow handling (dock 150 s, load 120 s) | 40.3; 50 %; 61.7; 418; 80 %; 26 % | 8.1; 98 %; 0.4; 1; 73 %; - | 11.2; 89 %; 0.2; 0; 58 %; 44 % | 48.1; 47 %; 77.9; 440; 83 %; - |
| fast handling (dock 30 s, load 30 s) | 7.3; 95 %; -0.0; 0; 45 %; 20 % | 1.8; 100 %; -0.1; 0; 25 %; - | 6.4; 96 %; -0.1; 0; 22 %; 20 % | 3.4; 97 %; 14.1; 256; 49 %; - |
| driving at 0.3 m/s (Liverpool's cap) | 16.4; 77 %; 19.4; 323; 64 %; 25 % | 2.2; 100 %; 0.0; 0; 45 %; - | 7.6; 94 %; -0.0; 0; 35 %; 29 % | 20.3; 79 %; 75.3; 428; 79 %; - |
| driving at 1.5 m/s | 13.6; 83 %; 9.2; 207; 63 %; 24 % | 2.0; 100 %; -0.0; 0; 38 %; - | 7.5; 94 %; -0.0; 0; 33 %; 28 % | 10.5; 91 %; 62.3; 422; 74 %; - |
| a bare MiR250's battery (13 h a charge, 52 min to charge) | 10.6; 91 %; 0.1; 0; 69 %; 29 % | 2.0; 100 %; -0.0; 0; 39 %; - | 7.5; 94 %; -0.0; 0; 33 %; 28 % | 5.2; 96 %; 15.8; 291; 80 %; - |
| attended, a bare MiR250's battery | 68.1; 35 %; 0.3; 0; 94 %; 49 % | 26.7; 70 %; 0.2; 0; 94 %; - | 26.1; 71 %; 0.1; 0; 93 %; 69 % | 70.4; 34 %; 0.3; 0; 94 %; - |
| aisles shared (flat) | 14.1; 82 %; 12.8; 231; 63 %; 24 % | 2.0; 100 %; -0.0; 0; 41 %; - | 7.5; 94 %; -0.0; 0; 33 %; 28 % | 12.3; 89 %; 56.4; 418; 76 %; - |
| outside samples carried from packaging | 24.4; 66 %; 34.8; 382; 75 %; 29 % | 3.4; 100 %; 0.0; 0; 61 %; - | 9.5; 91 %; 0.0; 0; 49 %; 41 % | 29.4; 66 %; 82.9; 414; 83 %; - |
| outside work first come, first served (no gaps kept for internal work) | 12.8; 89 %; 33.8; 366; 69 %; 28 % | 1.9; 100 %; 1.3; 23; 40 %; - | 6.9; 95 %; 1.9; 25; 33 %; 29 % | 13.2; 93 %; 61.2; 408; 79 %; - |
| attended, outside work first come, first served | 79.7; 30 %; 2.8; 32; 82 %; 43 % | 33.4; 61 %; 1.8; 4; 82 %; - | 32.4; 62 %; 4.7; 68; 82 %; 69 % | 82.3; 29 %; 1.6; 7; 82 %; - |
