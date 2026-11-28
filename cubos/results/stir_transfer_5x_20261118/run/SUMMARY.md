# stir_transfer_5x_20261118

✅ **45/45 steps, protocol complete**

- **When:** 2026-11-18 23:32:58Z → 23:38:06Z (17:32:58–17:38:06 lab), **308 s** wall, run process start to end; steps themselves 269 s
- **Code:** byu-vcl `6cdc7eb` · CubOS `496819c` + `grbl-prompt-status-polling`, `p20-gen2-plunger-constants`, `pipette-connect-tolerate-failed-home-main`, `stirrer-approach-1`, `tipped-hover-clamp-main`
- **GRBL:** travel [364.0, 281.0, 125.0], G54 [-364.0, -281.0, -125.0], `$20=1` `$21=1`, feed F3000
- **G-code:** 172 `G01` in 173.4 s (median 0.963 s, shortest 0.409 s), F 3000; `$H` [7.9, 21.1] s
- **Kernel:** 0 USB line(s) during the run
- **Plunger HOME check:** ended at 28.0 mm by the firmware; HOME took 12.678 s ⇒ 28.0 mm (**-0.00 mm**)

| step | command | s |
|---:|---|---:|
| 0 | home | 7.9 |
| 1 | move | 9.5 |
| 2 | pick_up_tip | 7.4 |
| 3 | stir | 0.0 |
| 4 | decap | 8.6 |
| 5 | aspirate | 9.4 |
| 6 | cap | 7.8 |
| 7 | stir | 0.0 |
| 8 | decap | 6.3 |
| 9 | blowout | 6.7 |
| 10 | cap | 6.9 |
| 11 | stir | 0.0 |
| 12 | decap | 6.7 |
| 13 | aspirate | 7.2 |
| 14 | cap | 7.8 |
| 15 | stir | 0.0 |
| 16 | decap | 6.3 |
| 17 | blowout | 6.7 |
| 18 | cap | 6.9 |
| 19 | stir | 0.0 |
| 20 | decap | 6.7 |
| 21 | aspirate | 7.2 |
| 22 | cap | 7.8 |
| 23 | stir | 0.0 |
| 24 | decap | 6.3 |
| 25 | blowout | 6.7 |
| 26 | cap | 6.9 |
| 27 | stir | 0.0 |
| 28 | decap | 6.7 |
| 29 | aspirate | 7.2 |
| 30 | cap | 7.8 |
| 31 | stir | 0.0 |
| 32 | decap | 6.3 |
| 33 | blowout | 6.7 |
| 34 | cap | 6.9 |
| 35 | stir | 0.0 |
| 36 | decap | 6.7 |
| 37 | aspirate | 7.2 |
| 38 | cap | 7.8 |
| 39 | stir | 0.0 |
| 40 | decap | 6.3 |
| 41 | blowout | 6.7 |
| 42 | cap | 6.9 |
| 43 | drop_tip | 10.9 |
| 44 | home | 21.1 |

| plunger (UTC) | command | args | s | reply |
|---|---|---|---:|---|
| 23:33:08 | STATUS |  | 0.01 | `OK:{"homed":0,"pos":0.00,"max_vol":20.00}` |
| 23:33:21 | HOME |  | 12.68 | `OK:{"msg":"Pipette homed"}` |
| 23:33:23 | MOVE_TO | 28.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved","v":[28.00]}` |
| 23:33:48 | MOVE_TO | 0.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved"}` |
| 23:34:09 | ASPIRATE | 20.0, 0.0 | 5.00 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 23:34:33 | MOVE_TO | 32.5, 0.0 | 2.86 | `OK:{"msg":"Pipette moved","v":[32.50]}` |
| 23:34:56 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 23:35:17 | MOVE_TO | 32.5, 0.0 | 2.86 | `OK:{"msg":"Pipette moved","v":[32.50]}` |
| 23:35:38 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 23:35:59 | MOVE_TO | 32.5, 0.0 | 2.86 | `OK:{"msg":"Pipette moved","v":[32.50]}` |
| 23:36:20 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 23:36:41 | MOVE_TO | 32.5, 0.0 | 2.86 | `OK:{"msg":"Pipette moved","v":[32.50]}` |
| 23:37:01 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 23:37:22 | MOVE_TO | 32.5, 0.0 | 2.86 | `OK:{"msg":"Pipette moved","v":[32.50]}` |
| 23:37:40 | MOVE_TO | 46.5, 0.0 | 4.65 | `OK:{"msg":"Pipette moved","v":[46.50]}` |
| 23:37:41 | MOVE_TO | 28.0, 0.0 | 1.70 | `OK:{"msg":"Pipette moved","v":[28.00]}` |

| stir | started (UTC) | at step | stopped by | s | `31` reads | rpm max | rpm median, last 10 reads | stalled |
|---:|---|---|---|---:|---:|---:|---:|---|
| 1 | 23:33:49.986 | 3 stir | firmware (stall) | 12.1 | 12 | 0 | 0 | yes |
| 2 | 23:34:42.902 | 11 stir | firmware (stall) | 11.1 | 11 | 0 | 0 | yes |
| 3 | 23:35:24.566 | 19 stir | firmware (stall) | 11.1 | 11 | 0 | 0 | yes |
| 4 | 23:36:06.291 | 27 stir | firmware (stall) | 11.1 | 11 | 0 | 0 | yes |
| 5 | 23:36:47.959 | 35 stir | firmware (stall) | 11.1 | 11 | 0 | 0 | yes |

Files: `runner.log` (everything), `checks.json`, `gate_*.log`, `run_hardware.log`, `step_trace.json`, `plunger_trace.json`, `stir_trace.json`, `gantry_*.log`, `tic_*`, `arduino_*.log`, `frames/`.
