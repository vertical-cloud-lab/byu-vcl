# Sensitivities (issue #407)

Written by `python -m twin.worth_it tables` from `out/worth_it/sensitivity.json.xz`: 4 logs (BOFN and the funnel, seeds 0-1), every layout, 30 % and 60 % outside load. Medians over the logs.

## 30 % outside load

| Case | VLM + 1 unit: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy | flat + 2 units: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy | VLM + 2 units: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy | flat + 1 unit: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy |
|---|---|---|---|---|
| base (the twin's timing) | 1.7; 100 %; 0.0; 0; 41 %; 20 % | 1.3; 100 %; -0.0; 0; 21 %; - | 1.6; 100 %; -0.0; 0; 20 %; 19 % | 1.3; 100 %; 0.0; 0; 43 %; - |
| attended time (PR 332, powder line in a cell) | 57.6; 61 %; 87.4; 166; 82 %; 36 % | 1.7; 100 %; 0.1; 0; 68 %; - | 2.5; 100 %; 0.1; 0; 67 %; 60 % | 62.3; 59 %; 0.8; 8; 82 %; - |
| attended time everywhere (PR 332; the replay loses atomizer slots) | 58.9; 57 %; 1,116.6; 514; 83 %; 25 % | 8.3; 93 %; 703.8; 495; 67 %; - | 21.0; 78 %; 612.6; 473; 56 %; 35 % | 66.4; 57 %; 1,422.0; 520; 84 %; - |
| trays may move while instruments run | 1.3; 100 %; -0.0; 0; 43 %; 22 % | 1.3; 100 %; -0.0; 0; 21 %; - | 1.3; 100 %; -0.0; 0; 21 %; 22 % | 1.3; 100 %; 0.0; 0; 43 %; - |
| attended, trays may move while instruments run | 60.7; 60 %; 6.3; 30; 82 %; 43 % | 1.7; 100 %; 0.1; 0; 68 %; - | 1.7; 100 %; 0.1; 0; 68 %; 61 % | 62.3; 59 %; 0.8; 8; 82 %; - |
| gentle trays (2.5x slower) | 1.8; 100 %; 0.0; 0; 44 %; 24 % | 1.3; 100 %; -0.0; 0; 21 %; - | 1.7; 100 %; -0.0; 0; 21 %; 23 % | 1.3; 100 %; 0.0; 0; 43 %; - |
| attended, gentle trays (2.5x slower) | 61.8; 59 %; 72.1; 102; 82 %; 40 % | 1.7; 100 %; 0.1; 0; 68 %; - | 2.9; 100 %; 0.1; 0; 69 %; 64 % | 62.3; 59 %; 0.8; 8; 82 %; - |
| no pre-fetch (the Shuttle waits for the unit) | 1.8; 100 %; 0.0; 0; 44 %; 17 % | 1.3; 100 %; -0.0; 0; 21 %; - | 1.6; 100 %; -0.0; 0; 21 %; 17 % | 1.3; 100 %; 0.0; 0; 43 %; - |
| slow handling (dock 150 s, load 120 s) | 19.4; 79 %; 473.7; 438; 61 %; 24 % | 1.4; 100 %; 0.2; 0; 40 %; - | 1.9; 100 %; 0.2; 0; 36 %; 32 % | 12.6; 92 %; 795.7; 486; 77 %; - |
| fast handling (dock 30 s, load 30 s) | 1.6; 100 %; -0.0; 0; 26 %; 14 % | 1.2; 100 %; -0.1; 0; 13 %; - | 1.5; 100 %; -0.1; 0; 13 %; 13 % | 1.2; 100 %; -0.1; 0; 27 %; - |
| driving at 0.3 m/s (Liverpool's cap) | 1.8; 100 %; 0.0; 0; 43 %; 20 % | 1.3; 100 %; 0.0; 0; 24 %; - | 1.6; 100 %; -0.0; 0; 21 %; 20 % | 1.3; 100 %; 0.1; 0; 50 %; - |
| driving at 1.5 m/s | 1.7; 100 %; 0.0; 0; 41 %; 20 % | 1.2; 100 %; -0.0; 0; 21 %; - | 1.6; 100 %; -0.0; 0; 20 %; 19 % | 1.3; 100 %; 0.0; 0; 42 %; - |
| a bare MiR250's battery (13 h a charge, 52 min to charge) | 1.7; 100 %; 0.0; 0; 41 %; 20 % | 1.3; 100 %; -0.0; 0; 21 %; - | 1.6; 100 %; -0.0; 0; 20 %; 19 % | 1.3; 100 %; 0.0; 0; 43 %; - |
| attended, a bare MiR250's battery | 47.9; 69 %; 0.5; 3; 94 %; 48 % | 1.6; 100 %; 0.0; 0; 67 %; - | 2.4; 100 %; 0.1; 0; 67 %; 60 % | 49.4; 68 %; 0.7; 6; 94 %; - |
| aisles shared (flat) | 1.7; 100 %; 0.0; 0; 41 %; 20 % | 1.2; 100 %; -0.0; 0; 22 %; - | 1.6; 100 %; -0.0; 0; 20 %; 19 % | 1.3; 100 %; 0.0; 0; 43 %; - |
| outside samples carried from packaging | 2.0; 100 %; 0.0; 0; 57 %; 28 % | 1.3; 100 %; -0.0; 0; 31 %; - | 1.8; 100 %; -0.0; 0; 28 %; 28 % | 1.5; 100 %; 0.1; 0; 63 %; - |
| outside work first come, first served (no gaps kept for internal work) | 1.6; 100 %; 1.2; 3; 41 %; 20 % | 1.2; 100 %; 0.6; 0; 22 %; - | 1.5; 100 %; 1.2; 3; 20 %; 19 % | 1.3; 100 %; 0.7; 0; 44 %; - |
| attended, outside work first come, first served | 59.6; 60 %; 336.3; 225; 82 %; 43 % | 1.7; 100 %; 0.8; 0; 68 %; - | 2.3; 100 %; 1.4; 6; 67 %; 60 % | 61.6; 59 %; 449.1; 324; 82 %; - |

## 60 % outside load

| Case | VLM + 1 unit: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy | flat + 2 units: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy | VLM + 2 units: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy | flat + 1 unit: turnaround h; served; step delay h; atomizer runs off slot; units busy; opening busy |
|---|---|---|---|---|
| base (the twin's timing) | 10.5; 90 %; 0.1; 0; 69 %; 28 % | 2.0; 100 %; -0.0; 0; 39 %; - | 7.5; 94 %; -0.0; 0; 33 %; 28 % | 8.1; 90 %; 641.3; 472; 75 %; - |
| attended time (PR 332, powder line in a cell) | 75.4; 30 %; 11.6; 50; 82 %; 39 % | 30.8; 61 %; 0.2; 0; 82 %; - | 28.9; 63 %; 0.2; 0; 82 %; 65 % | 79.5; 28 %; 0.8; 4; 82 %; - |
| attended time everywhere (PR 332; the replay loses atomizer slots) | 77.8; 30 %; 1,400.6; 520; 83 %; 24 % | 32.3; 60 %; 842.4; 504; 83 %; - | 30.2; 58 %; 809.3; 496; 80 %; 47 % | 84.4; 28 %; 1,186.1; 520; 84 %; - |
| trays may move while instruments run | 8.4; 90 %; 656.6; 464; 75 %; 35 % | 2.0; 100 %; -0.0; 0; 39 %; - | 2.0; 100 %; -0.0; 0; 39 %; 39 % | 8.1; 90 %; 641.3; 472; 75 %; - |
| attended, trays may move while instruments run | 77.5; 29 %; 24.0; 88; 82 %; 41 % | 30.8; 61 %; 0.2; 0; 82 %; - | 30.5; 61 %; 0.2; 0; 82 %; 82 % | 79.5; 28 %; 0.8; 4; 82 %; - |
| gentle trays (2.5x slower) | 11.8; 89 %; 0.1; 0; 71 %; 33 % | 2.0; 100 %; -0.0; 0; 39 %; - | 7.9; 93 %; 0.0; 0; 35 %; 32 % | 8.1; 90 %; 641.3; 472; 75 %; - |
| attended, gentle trays (2.5x slower) | 74.6; 30 %; 448.0; 324; 82 %; 30 % | 30.8; 61 %; 0.2; 0; 82 %; - | 30.6; 61 %; 0.2; 0; 82 %; 69 % | 79.5; 28 %; 0.8; 4; 82 %; - |
| no pre-fetch (the Shuttle waits for the unit) | 11.6; 89 %; 0.1; 0; 73 %; 24 % | 2.0; 100 %; -0.0; 0; 39 %; - | 7.6; 94 %; -0.0; 0; 35 %; 25 % | 8.1; 90 %; 641.3; 472; 75 %; - |
| slow handling (dock 150 s, load 120 s) | 36.6; 52 %; 752.4; 493; 80 %; 28 % | 4.4; 100 %; 0.3; 0; 73 %; - | 10.7; 89 %; 0.2; 0; 58 %; 43 % | 44.0; 49 %; 891.7; 504; 83 %; - |
| fast handling (dock 30 s, load 30 s) | 7.4; 94 %; -0.0; 0; 44 %; 20 % | 1.8; 100 %; -0.1; 0; 25 %; - | 6.5; 96 %; -0.1; 0; 22 %; 20 % | 1.9; 100 %; -0.0; 0; 51 %; - |
| driving at 0.3 m/s (Liverpool's cap) | 11.5; 89 %; 0.1; 0; 73 %; 29 % | 2.1; 100 %; 0.0; 0; 44 %; - | 7.6; 94 %; -0.0; 0; 35 %; 29 % | 15.2; 83 %; 698.4; 488; 81 %; - |
| driving at 1.5 m/s | 10.4; 90 %; 0.1; 0; 68 %; 28 % | 2.0; 100 %; -0.0; 0; 38 %; - | 7.5; 94 %; -0.0; 0; 33 %; 28 % | 6.3; 92 %; 551.4; 389; 74 %; - |
| a bare MiR250's battery (13 h a charge, 52 min to charge) | 10.5; 90 %; 0.1; 0; 69 %; 28 % | 2.0; 100 %; -0.0; 0; 39 %; - | 7.5; 94 %; -0.0; 0; 33 %; 28 % | 3.1; 100 %; 0.1; 0; 83 %; - |
| attended, a bare MiR250's battery | 63.6; 35 %; 0.7; 7; 94 %; 46 % | 24.5; 71 %; 0.2; 0; 94 %; - | 23.2; 71 %; 0.1; 0; 94 %; 68 % | 67.0; 33 %; 0.7; 8; 94 %; - |
| aisles shared (flat) | 10.5; 90 %; 0.1; 0; 69 %; 28 % | 2.0; 100 %; -0.0; 0; 40 %; - | 7.5; 94 %; -0.0; 0; 33 %; 28 % | 8.1; 90 %; 641.3; 472; 75 %; - |
| outside samples carried from packaging | 23.3; 65 %; 543.7; 448; 73 %; 30 % | 3.0; 100 %; -0.0; 0; 61 %; - | 9.5; 90 %; 0.0; 0; 49 %; 41 % | 27.7; 67 %; 976.6; 498; 83 %; - |
| outside work first come, first served (no gaps kept for internal work) | 10.0; 91 %; 353.4; 284; 69 %; 29 % | 1.9; 100 %; 19.2; 68; 39 %; - | 7.0; 95 %; 397.4; 285; 33 %; 28 % | 6.8; 99 %; 881.3; 469; 82 %; - |
| attended, outside work first come, first served | 75.4; 29 %; 546.9; 443; 82 %; 41 % | 30.5; 61 %; 2.1; 4; 82 %; - | 29.0; 63 %; 552.7; 442; 82 %; 67 % | 78.8; 28 %; 451.8; 388; 82 %; - |
