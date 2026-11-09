# pipette_test_20261002

❌ **stopped after 0/12 steps**: `write failed: [Errno 5] Input/output error`

- **When:** 2026-10-02 19:42:49Z → 19:43:04Z (13:42:49–13:43:04 lab), **16 s** wall, run process start to end
- **Code:** byu-vcl `0e6076a` · CubOS `496819c` + `grbl-prompt-status-polling`, `p20-gen2-plunger-constants`, `pipette-connect-tolerate-failed-home-main`, `tipped-hover-clamp-main`
- **GRBL:** travel [364.0, 281.0, 125.0], G54 [-364.0, -281.0, -125.0], `$20=1` `$21=1`, feed F3000
- **G-code:** 0 `G01` in 0 s (median None s, shortest None s), F ; `$H` [] s
- **Tic during run:** 30 polls, VIN 10.7–11.3 V, stopping errors: none
- **Kernel:** 3 USB line(s) during the run — first: `2026-10-02T13:42:59-06:00 <host> kernel: usb 3-2: USB disconnect, device number 8`
- **Plunger HOME check:** ended at 28.0 mm by the firmware; HOME took 12.678 s ⇒ 28.0 mm (**-0.00 mm**)

| plunger (UTC) | command | args | s | reply |
|---|---|---|---:|---|
| 19:42:58 | STATUS |  | 0.01 | `OK:{"homed":0,"pos":0.00,"max_vol":20.00}` |
| 19:42:59 | HOME |  | 0.95 | `OK:{"msg":"Pipette homed"}` |
| 19:43:02 | MOVE_TO | 28.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved","v":[28.00]}` |

Files: `runner.log` (everything), `checks.json`, `gate_*.log`, `run_hardware.log`, `step_trace.json`, `plunger_trace.json`, `gantry_*.log`, `tic_*`, `arduino_*.log`, `frames/`.
