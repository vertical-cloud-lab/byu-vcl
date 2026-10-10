# pipette_test_mix_20261009

❌ **stopped after 0/12 steps**: `decap failed for 'vial_1': CapperError: decap: sensor did not confirm cap capture after 3 attempt(s) (last reading: cap_present=False, expected True).. Tool ret`

- **When:** 2026-10-09 21:27:16Z → 21:28:04Z (15:27:16–15:28:04 lab), **48 s** wall, run process start to end; steps themselves 32 s
- **Code:** byu-vcl `ef63f31` · CubOS `496819c` + `grbl-prompt-status-polling`, `p20-gen2-plunger-constants`, `pipette-connect-tolerate-failed-home-main`, `tipped-hover-clamp-main`
- **GRBL:** travel [364.0, 281.0, 125.0], G54 [-364.0, -281.0, -125.0], `$20=1` `$21=1`, feed F3000
- **G-code:** 13 `G01` in 20.2 s (median 1.165 s, shortest 0.661 s), F 3000; `$H` [7.9] s
- **Kernel:** 0 USB line(s) during the run
- **Plunger HOME check:** ended at 28.0 mm by the firmware; HOME took 12.681 s ⇒ 28.0 mm (**+0.00 mm**)

| step | command | s |
|---:|---|---:|
| 0 | home | 7.9 |
| 1 | move | 9.5 |
| 2 | decap ❌ | 14.5 |

| plunger (UTC) | command | args | s | reply |
|---|---|---|---:|---|
| 21:27:26 | STATUS |  | 0.01 | `OK:{"homed":0,"pos":0.00,"max_vol":20.00}` |
| 21:27:27 | HOME |  | 0.94 | `OK:{"msg":"Pipette homed"}` |
| 21:27:30 | MOVE_TO | 28.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved","v":[28.00]}` |

Baseline `pipette_test_20261007`: wall 137.3 s, G01 total 60.9 s

Files: `runner.log` (everything), `checks.json`, `gate_*.log`, `run_hardware.log`, `step_trace.json`, `plunger_trace.json`, `gantry_*.log`, `tic_*`, `arduino_*.log`, `frames/`.
