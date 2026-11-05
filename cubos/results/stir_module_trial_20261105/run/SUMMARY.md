# stir_module_trial_20261105

✅ **11/11 steps, protocol complete**

- **When:** 2026-11-05 22:52:46Z → 22:55:09Z (16:52:46–16:55:09 lab), **142 s** wall, run process start to end; steps themselves 106 s
- **Code:** byu-vcl `d28c733` · CubOS `496819c` + `grbl-prompt-status-polling`, `p20-gen2-plunger-constants`, `pipette-connect-tolerate-failed-home-main`, `tipped-hover-clamp-main`
- **GRBL:** travel [364.0, 281.0, 125.0], G54 [-364.0, -281.0, -125.0], `$20=1` `$21=1`, feed F3000
- **G-code:** 43 `G01` in 54.1 s (median 0.964 s, shortest 0.408 s), F 3000; `$H` [7.9, 21.1] s
- **Kernel:** 0 USB line(s) during the run
- **Plunger HOME check:** ended at 28.0 mm by the firmware; HOME took 12.678 s ⇒ 28.0 mm (**-0.00 mm**)

| step | command | s |
|---:|---|---:|
| 0 | home | 7.9 |
| 1 | move | 9.5 |
| 2 | decap | 8.2 |
| 3 | pick_up_tip | 8.0 |
| 4 | aspirate | 11.7 |
| 5 | cap | 7.8 |
| 6 | decap | 6.3 |
| 7 | blowout | 6.7 |
| 8 | cap | 6.9 |
| 9 | drop_tip | 11.4 |
| 10 | home | 21.1 |

| plunger (UTC) | command | args | s | reply |
|---|---|---|---:|---|
| 22:52:56 | STATUS |  | 0.01 | `OK:{"homed":0,"pos":0.00,"max_vol":20.00}` |
| 22:53:09 | HOME |  | 12.68 | `OK:{"msg":"Pipette homed"}` |
| 22:53:11 | MOVE_TO | 28.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved","v":[28.00]}` |
| 22:53:46 | MOVE_TO | 0.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved"}` |
| 22:53:59 | ASPIRATE | 20.0, 0.0 | 5.00 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 22:54:24 | MOVE_TO | 32.5, 0.0 | 2.86 | `OK:{"msg":"Pipette moved","v":[32.50]}` |
| 22:54:43 | MOVE_TO | 46.5, 0.0 | 4.65 | `OK:{"msg":"Pipette moved","v":[46.50]}` |
| 22:54:44 | MOVE_TO | 28.0, 0.0 | 1.69 | `OK:{"msg":"Pipette moved","v":[28.00]}` |

Files: `runner.log` (everything), `checks.json`, `gate_*.log`, `run_hardware.log`, `step_trace.json`, `plunger_trace.json`, `gantry_*.log`, `tic_*`, `arduino_*.log`, `frames/`.
