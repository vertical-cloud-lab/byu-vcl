# pipette_test_20261001

✅ **12/12 steps, protocol complete**

- **When:** 2026-10-01 21:22:19Z → 21:24:24Z (15:22:19–15:24:24 lab), **124 s** wall, run process start to end; steps themselves 106 s
- **Code:** byu-vcl `542a2b5` · CubOS `496819c` + `grbl-prompt-status-polling`, `p20-gen2-plunger-constants`, `pipette-connect-tolerate-failed-home-main`, `tipped-hover-clamp-main`
- **GRBL:** travel [391.0, 236.665, 124.0], G54 [-391.0, -236.665, -124.0], `$20=1` `$21=1`, feed F3000
- **G-code:** 47 `G01` in 55.2 s (median 0.913 s, shortest 0.056 s), F 3000; `$H` [7.9, 20.7] s
- **Tic during run:** 236 polls, VIN 9.0–11.3 V, stopping errors: none
- **Kernel:** 0 USB line(s) during the run
- **Plunger HOME check:** ended at 28.0 mm by the firmware; HOME took 12.677 s ⇒ 27.99 mm (**-0.01 mm**)

| step | command | s |
|---:|---|---:|
| 0 | home | 7.9 |
| 1 | move | 9.2 |
| 2 | decap | 6.2 |
| 3 | pick_up_tip | 7.3 |
| 4 | aspirate | 11.8 |
| 5 | move | 3.8 |
| 6 | cap | 5.7 |
| 7 | decap | 6.0 |
| 8 | blowout | 7.3 |
| 9 | drop_tip | 12.5 |
| 10 | cap | 8.0 |
| 11 | home | 20.7 |

| plunger (UTC) | command | args | s | reply |
|---|---|---|---:|---|
| 21:22:29 | STATUS |  | 0.01 | `OK:{"homed":0,"pos":0.00,"max_vol":20.00}` |
| 21:22:30 | HOME |  | 0.93 | `OK:{"msg":"Pipette homed"}` |
| 21:22:33 | MOVE_TO | 28.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved","v":[28.00]}` |
| 21:23:04 | MOVE_TO | 0.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved"}` |
| 21:23:16 | ASPIRATE | 20.0, 0.0 | 5.00 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 21:23:39 | MOVE_TO | 32.5, 0.0 | 2.86 | `OK:{"msg":"Pipette moved","v":[32.50]}` |
| 21:23:51 | MOVE_TO | 46.5, 0.0 | 4.65 | `OK:{"msg":"Pipette moved","v":[46.50]}` |
| 21:23:52 | MOVE_TO | 28.0, 0.0 | 1.70 | `OK:{"msg":"Pipette moved","v":[28.00]}` |

Files: `runner.log` (everything), `checks.json`, `gate_*.log`, `run_hardware.log`, `step_trace.json`, `plunger_trace.json`, `gantry_*.log`, `tic_*`, `arduino_*.log`, `frames/`.
