# stir_only_check_20261124

✅ **5/5 steps, protocol complete**

- **When:** 2026-11-24 23:18:23Z → 23:19:33Z (16:18:23 MST–16:19:33 MST lab), **70 s** wall, run process start to end; steps themselves 43 s
- **Code:** byu-vcl `87e97d5` · CubOS `496819c` + `grbl-prompt-status-polling`, `p20-gen2-plunger-constants`, `pipette-connect-tolerate-failed-home-main`, `stirrer-approach-1`, `tipped-hover-clamp-main`
- **GRBL:** travel [364.0, 281.0, 125.0], G54 [-364.0, -281.0, -125.0], `$20=1` `$21=1`, feed F3000
- **G-code:** 0 `G01` in 0 s (median None s, shortest None s), F ; `$H` [7.9] s
- **Kernel:** 0 USB line(s) during the run

| step | command | s |
|---:|---|---:|
| 0 | home | 7.9 |
| 1 | stir | 20.3 |
| 2 | stir | 0.0 |
| 3 | pause | 15.0 |
| 4 | stir | 0.0 |

| plunger (UTC) | command | args | s | reply |
|---|---|---|---:|---|
| 23:18:32 | STATUS |  | 0.01 | `OK:{"homed":0,"pos":0.00,"max_vol":20.00}` |
| 23:18:45 | HOME |  | 12.68 | `OK:{"msg":"Pipette homed"}` |
| 23:18:48 | MOVE_TO | 28.0, 0.0 | 2.56 | `OK:{"msg":"Pipette moved","v":[28.00]}` |

| stir | started (UTC) | at step | stopped by | s | `31` reads | rpm max | rpm median, last 10 reads | stalled |
|---:|---|---|---|---:|---:|---:|---:|---|
| 1 | 23:18:56.041 | 1 stir | firmware (its timer) | 20.2 | 21 | 630 | 600 | no |
| 2 | 23:19:16.293 | 2 stir | step 4 stir | 15.0 | 14 | 630 | 210 | no |

Files: `runner.log` (everything), `checks.json`, `gate_*.log`, `run_hardware.log`, `step_trace.json`, `plunger_trace.json`, `stir_trace.json`, `gantry_*.log`, `tic_*`, `arduino_*.log`, `frames/`.
