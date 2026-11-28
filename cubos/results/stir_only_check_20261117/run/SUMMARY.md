# stir_only_check_20261117

✅ **5/5 steps, protocol complete**

- **When:** 2026-11-17 22:42:32Z → 22:43:22Z (16:42:32–16:43:22 lab), **51 s** wall, run process start to end; steps themselves 35 s
- **Code:** byu-vcl `650f68c` · CubOS `496819c` + `grbl-prompt-status-polling`, `p20-gen2-plunger-constants`, `pipette-connect-tolerate-failed-home-main`, `stirrer-approach-1`, `tipped-hover-clamp-main`
- **GRBL:** travel [364.0, 281.0, 125.0], G54 [-364.0, -281.0, -125.0], `$20=1` `$21=1`, feed F3000
- **G-code:** 0 `G01` in 0 s (median None s, shortest None s), F ; `$H` [7.9] s
- **Kernel:** 0 USB line(s) during the run

| step | command | s |
|---:|---|---:|
| 0 | home | 7.9 |
| 1 | stir | 12.2 |
| 2 | stir | 0.0 |
| 3 | pause | 15.0 |
| 4 | stir | 0.0 |

| plunger (UTC) | command | args | s | reply |
|---|---|---|---:|---|
| 22:42:41 | STATUS |  | 0.01 | `OK:{"homed":0,"pos":0.00,"max_vol":20.00}` |
| 22:42:42 | HOME |  | 0.94 | `OK:{"msg":"Pipette homed"}` |
| 22:42:45 | MOVE_TO | 28.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved","v":[28.00]}` |

| stir | started (UTC) | at step | stopped at step | s | `31` reads | rpm max | rpm median, last 10 s | stalled |
|---:|---|---|---|---:|---:|---:|---:|---|
| 1 | 22:42:53.324 | 1 stir | (teardown) | ? | 25 | 0 | 0 | yes |
| 2 | 22:43:05.485 | 3 pause | 4 stir | 15.0 | 12 | 0 | 0 | yes |

Files: `runner.log` (everything), `checks.json`, `gate_*.log`, `run_hardware.log`, `step_trace.json`, `plunger_trace.json`, `stir_trace.json`, `gantry_*.log`, `tic_*`, `arduino_*.log`, `frames/`.
