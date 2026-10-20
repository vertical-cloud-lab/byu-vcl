# pipette_test_20261020

✅ **12/12 steps, protocol complete**

- **When:** 2026-10-20 22:10:48Z → 22:13:04Z (16:10:48–16:13:04 lab), **135 s** wall, run process start to end; steps themselves 114 s
- **Code:** byu-vcl `ed84bba` · CubOS `496819c` + `grbl-prompt-status-polling`, `p20-gen2-plunger-constants`, `pipette-connect-tolerate-failed-home-main`, `tipped-hover-clamp-main`
- **GRBL:** travel [364.0, 281.0, 125.0], G54 [-364.0, -281.0, -125.0], `$20=1` `$21=1`, feed F3000
- **G-code:** 45 `G01` in 60.9 s (median 1.165 s, shortest 0.207 s), F 3000; `$H` [7.9, 22.3] s
- **Kernel:** 0 USB line(s) during the run
- **Plunger HOME check:** ended at 28.0 mm by the firmware; HOME took 12.681 s ⇒ 28.0 mm (**+0.00 mm**)

| step | command | s |
|---:|---|---:|
| 0 | home | 7.9 |
| 1 | move | 9.5 |
| 2 | decap | 7.3 |
| 3 | pick_up_tip | 8.4 |
| 4 | aspirate | 12.8 |
| 5 | move | 5.0 |
| 6 | cap | 7.0 |
| 7 | decap | 5.9 |
| 8 | blowout | 7.2 |
| 9 | drop_tip | 12.8 |
| 10 | cap | 7.4 |
| 11 | home | 22.3 |

| plunger (UTC) | command | args | s | reply |
|---|---|---|---:|---|
| 22:10:58 | STATUS |  | 0.01 | `OK:{"homed":0,"pos":0.00,"max_vol":20.00}` |
| 22:10:59 | HOME |  | 0.95 | `OK:{"msg":"Pipette homed"}` |
| 22:11:02 | MOVE_TO | 28.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved","v":[28.00]}` |
| 22:11:36 | MOVE_TO | 0.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved"}` |
| 22:11:50 | ASPIRATE | 20.0, 0.0 | 5.00 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 22:12:17 | MOVE_TO | 32.5, 0.0 | 2.86 | `OK:{"msg":"Pipette moved","v":[32.50]}` |
| 22:12:29 | MOVE_TO | 46.5, 0.0 | 4.65 | `OK:{"msg":"Pipette moved","v":[46.50]}` |
| 22:12:31 | MOVE_TO | 28.0, 0.0 | 1.70 | `OK:{"msg":"Pipette moved","v":[28.00]}` |

Baseline `pipette_test_20261007`: wall 137.3 s, G01 total 60.9 s

Files: `runner.log` (everything), `checks.json`, `gate_*.log`, `run_hardware.log`, `step_trace.json`, `plunger_trace.json`, `gantry_*.log`, `tic_*`, `arduino_*.log`, `frames/`.
