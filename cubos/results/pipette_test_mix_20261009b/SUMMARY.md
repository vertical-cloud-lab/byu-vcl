# pipette_test_mix_20261009b

✅ **12/12 steps, protocol complete**

- **When:** 2026-10-09 21:39:16Z → 21:42:55Z (15:39:16–15:42:55 lab), **218 s** wall, run process start to end; steps themselves 195 s
- **Code:** byu-vcl `ef63f31` · CubOS `496819c` + `grbl-prompt-status-polling`, `p20-gen2-plunger-constants`, `pipette-connect-tolerate-failed-home-main`, `tipped-hover-clamp-main`
- **GRBL:** travel [364.0, 281.0, 125.0], G54 [-364.0, -281.0, -125.0], `$20=1` `$21=1`, feed F3000
- **G-code:** 57 `G01` in 63.4 s (median 0.812 s, shortest 0.206 s), F 3000; `$H` [22.8, 22.3] s
- **Kernel:** 0 USB line(s) during the run
- **Plunger HOME check:** ended at 28.0 mm by the firmware; HOME took 12.669 s ⇒ 27.97 mm (**-0.03 mm**)

| step | command | s |
|---:|---|---:|
| 0 | home | 22.8 |
| 1 | move | 9.5 |
| 2 | decap | 7.3 |
| 3 | pick_up_tip | 8.4 |
| 4 | mix | 46.2 |
| 5 | move | 5.0 |
| 6 | cap | 7.0 |
| 7 | decap | 5.9 |
| 8 | mix | 40.5 |
| 9 | drop_tip | 12.8 |
| 10 | cap | 7.4 |
| 11 | home | 22.3 |

| plunger (UTC) | command | args | s | reply |
|---|---|---|---:|---|
| 21:39:26 | STATUS |  | 0.01 | `OK:{"homed":0,"pos":0.00,"max_vol":20.00}` |
| 21:39:27 | HOME |  | 0.94 | `OK:{"msg":"Pipette homed"}` |
| 21:39:30 | MOVE_TO | 28.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved","v":[28.00]}` |
| 21:40:19 | MOVE_TO | 0.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved"}` |
| 21:40:33 | ASPIRATE | 20.0, 0.0 | 5.00 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 21:40:36 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 21:40:39 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 21:40:42 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 21:40:45 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 21:40:48 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 21:40:51 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 21:40:54 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 21:40:57 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 21:41:00 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 21:41:03 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 21:41:06 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 21:41:33 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 21:41:36 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 21:41:39 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 21:41:42 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 21:41:45 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 21:41:48 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 21:41:51 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 21:41:54 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 21:41:57 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 21:42:00 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 21:42:03 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 21:42:06 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 21:42:18 | MOVE_TO | 46.5, 0.0 | 4.65 | `OK:{"msg":"Pipette moved","v":[46.50]}` |
| 21:42:20 | MOVE_TO | 28.0, 0.0 | 1.70 | `OK:{"msg":"Pipette moved","v":[28.00]}` |

Baseline `pipette_test_20261007`: wall 137.3 s, G01 total 60.9 s

Files: `runner.log` (everything), `checks.json`, `gate_*.log`, `run_hardware.log`, `step_trace.json`, `plunger_trace.json`, `gantry_*.log`, `tic_*`, `arduino_*.log`, `frames/`.
