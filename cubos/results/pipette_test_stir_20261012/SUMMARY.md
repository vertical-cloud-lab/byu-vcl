# pipette_test_stir_20261012

✅ **74/74 steps, protocol complete**

- **When:** 2026-10-12 18:43:44Z → 18:47:01Z (12:43:44–12:47:01 lab), **197 s** wall, run process start to end; steps themselves 172 s
- **Code:** byu-vcl `f4ef516` · CubOS `496819c` + `grbl-prompt-status-polling`, `p20-gen2-plunger-constants`, `pipette-connect-tolerate-failed-home-main`, `tipped-hover-clamp-main`
- **GRBL:** travel [364.0, 281.0, 125.0], G54 [-364.0, -281.0, -125.0], `$20=1` `$21=1`, feed F3000
- **G-code:** 112 `G01` in 87.3 s (median 0.459 s, shortest 0.207 s), F 3000; `$H` [7.9, 22.3] s
- **Kernel:** 0 USB line(s) during the run
- **Plunger HOME check:** ended at 28.0 mm by the firmware; HOME took 12.685 s ⇒ 28.01 mm (**+0.01 mm**)

| step | command | s |
|---:|---|---:|
| 0 | home | 7.9 |
| 1 | move | 9.5 |
| 2 | decap | 7.3 |
| 3 | pick_up_tip | 8.4 |
| 4 | mix | 46.1 |
| 5 | move | 5.0 |
| 6 | cap | 7.1 |
| 7 | decap | 5.9 |
| 8 | move | 4.3 |
| 9 | move | 0.4 |
| 10 | move | 0.4 |
| 11 | move | 0.5 |
| 12 | move | 0.5 |
| 13 | move | 0.5 |
| 14 | move | 0.5 |
| 15 | move | 0.5 |
| 16 | move | 0.5 |
| 17 | move | 0.5 |
| 18 | move | 0.5 |
| 19 | move | 0.5 |
| 20 | move | 0.5 |
| 21 | move | 0.5 |
| 22 | move | 0.5 |
| 23 | move | 0.5 |
| 24 | move | 0.5 |
| 25 | move | 0.5 |
| 26 | move | 0.5 |
| 27 | move | 0.5 |
| 28 | move | 0.5 |
| 29 | move | 0.5 |
| 30 | move | 0.5 |
| 31 | move | 0.5 |
| 32 | move | 0.5 |
| 33 | move | 0.5 |
| 34 | move | 0.5 |
| 35 | move | 0.5 |
| 36 | move | 0.5 |
| 37 | move | 0.5 |
| 38 | move | 0.5 |
| 39 | move | 0.5 |
| 40 | move | 0.5 |
| 41 | move | 0.5 |
| 42 | move | 0.5 |
| 43 | move | 0.5 |
| 44 | move | 0.5 |
| 45 | move | 0.5 |
| 46 | move | 0.5 |
| 47 | move | 0.5 |
| 48 | move | 0.5 |
| 49 | move | 0.5 |
| 50 | move | 0.5 |
| 51 | move | 0.4 |
| 52 | move | 0.5 |
| 53 | move | 0.5 |
| 54 | move | 0.5 |
| 55 | move | 0.5 |
| 56 | move | 0.5 |
| 57 | move | 0.5 |
| 58 | move | 0.5 |
| 59 | move | 0.5 |
| 60 | move | 0.4 |
| 61 | move | 0.4 |
| 62 | move | 0.5 |
| 63 | move | 0.5 |
| 64 | move | 0.5 |
| 65 | move | 0.5 |
| 66 | move | 0.5 |
| 67 | move | 0.5 |
| 68 | move | 0.5 |
| 69 | move | 0.4 |
| 70 | move | 1.7 |
| 71 | drop_tip | 11.2 |
| 72 | cap | 7.4 |
| 73 | home | 22.3 |

| plunger (UTC) | command | args | s | reply |
|---|---|---|---:|---|
| 18:43:54 | STATUS |  | 0.01 | `OK:{"homed":0,"pos":0.00,"max_vol":20.00}` |
| 18:43:55 | HOME |  | 0.95 | `OK:{"msg":"Pipette homed"}` |
| 18:43:57 | MOVE_TO | 28.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved","v":[28.00]}` |
| 18:44:32 | MOVE_TO | 0.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved"}` |
| 18:44:46 | ASPIRATE | 20.0, 0.0 | 5.00 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 18:44:49 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 18:44:52 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 18:44:55 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 18:44:58 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 18:45:01 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 18:45:04 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 18:45:07 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 18:45:10 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 18:45:13 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 18:45:16 | ASPIRATE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette aspirated","v":[20.00,1.20]}` |
| 18:45:19 | DISPENSE | 20.0, 0.0 | 2.86 | `OK:{"msg":"Pipette dispensed","v":[20.00,32.50]}` |
| 18:46:25 | MOVE_TO | 46.5, 0.0 | 4.65 | `OK:{"msg":"Pipette moved","v":[46.50]}` |
| 18:46:26 | MOVE_TO | 28.0, 0.0 | 1.70 | `OK:{"msg":"Pipette moved","v":[28.00]}` |

Baseline `pipette_test_mix_20261009b`: wall 218.5 s, G01 total 63.4 s

Files: `runner.log` (everything), `checks.json`, `gate_*.log`, `run_hardware.log`, `step_trace.json`, `plunger_trace.json`, `gantry_*.log`, `tic_*`, `arduino_*.log`, `frames/`.
