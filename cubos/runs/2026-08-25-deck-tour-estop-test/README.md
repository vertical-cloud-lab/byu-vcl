# 2026-08-25 deck-tour hardware run / live E-stop test (issue #182)

First hardware execution of `deck_tour.yaml` on the CubXL, run remotely from
GitHub Actions via the Pi (CubOS checkout `cbc33dc`, CLI
`python -m cubos.tools.run_protocol`), while the team stood at the machine and
pressed the E-stop during motion. Jarrett (23:51 UTC): "we tested the e-stop
twice, and it worked. It stopped as it should both times."

## What ran

Config trio (copies in this directory are byte-identical to what executed):

- `deck_tour.yaml` — 26-step motion-only tour (branch `claude/issue-182-20260825-2320`)
- `cub_xl_ben_pipette_capper.yaml` — gantry, 2026-08-24 calibration (PR #171 @ `43e7fd5`)
- `sterling_6vials_tiprack.yaml` — deck (PR #171 @ `43e7fd5`)

`validate_setup` PASS and full 26-step `--mock` PASS on the Pi itself before
any motion. Staged on the Pi in `~/run_20260825_deck_tour/`.

## Timeline (UTC, from the logs here)

| Attempt | Campaign | Window | Progress | Ended by |
|---|---|---|---|---|
| 1 | 15 | 23:47:40–23:48:39 | home + corner circuit (died moving to front-left) | E-stop press #1 — GRBL boot banner mid-command (`hardware_run.log`) |
| 2 | 16 | 23:49:34–~23:50 | home + corners, heading to deck center | E-stop press #2 — controller stopped answering (`hardware_run2.log`) |
| 3 | 17 | 23:55:56–23:57:49 | home + corners + center + vial hovers + vial_1 close approach | third stop/power-off — `error:9`, board rebooted to ALARM (`hardware_run3.log`) |

The `run_protocol` summary prints "0 steps executed" on every abort — that
counter is wrong on the failure path; elapsed times and the failing target
coordinates show each attempt executed real motion well into the tour.
No collisions or limit strikes; every abort was clean.

## E-stop findings

- Both human-confirmed presses match a **controller-MCU reboot** signature over
  serial (fresh `Grbl 1.1h` banner / no response, then normal again), while the
  CH341 USB-serial chip stayed enumerated (it is powered from the Pi's USB
  port, so it survives a control-box power cut). The E-stop therefore
  cuts/resets the controller rather than merely pausing G-code — it halts
  motion immediately, loses position, and latches ALARM. **Works during normal
  protocol motion (2/2).**
- The historical failure scenario — E-stop while a closed-loop stepper stalls
  past a travel end — was not tested; the team plans to test it at the next
  calibration.
- `$$` snapshot (full dump in `watchdog_interlock.log`): **`$21=0` — hard
  limits still disabled**, `$20=1` soft limits on, `$22=1` homing on,
  `$27=3.0` pull-off, `$130/$131/$132 = 389.333/235/125`, `$1=25` (steppers
  de-energize at idle — no holding torque when stopped). `$I` =
  `VER:1.1h.20190825`. Recommendation from the 2026-08-18 investigation stands:
  set `$21=1` before the past-limit E-stop test.

## Serial-connect fix discovered along the way

Every serial open was DTR-resetting the 8-bit board, so each CubOS connect
found a boot ALARM and raced the reboot. Fix applied on the Pi:

    stty -F /dev/ttyUSB0 -hupcl

DTR then stays asserted between sessions; subsequent CubOS connects found
`Idle / Alarm: clear` with homing preserved (attempt 3 connected perfectly
clean). **Transient** — reverts when the controller is unplugged or the Pi
reboots. To make it permanent, add a udev rule or run the `stty` at boot.

## Machine state at end + Pi-side changes

- Head parked near vial_1 (deck ~187, 26, Z 78–90), unpowered, controller
  ALARM-latched and unhomed → **home (`$H`) before next use**.
- Pi: created `~/run_20260825_deck_tour/` (configs, logs, an unused
  `gantry_capper_offline.yaml` experiment); set `-hupcl` as above. No
  services, cron, or repo checkouts on the Pi were modified. A second
  concurrent workflow session (duplicate trigger) held the port with a
  90-minute interlock ending ~01:30 UTC; release early with
  `touch ~/run_20260825_deck_tour/RELEASE_INTERLOCK`.

## Files

- `hardware_run.log`, `hardware_run2.log`, `hardware_run3.log` — full
  `run_protocol` output per attempt (usernames/hostnames scrubbed to
  `PIUSER`/`PIHOST`)
- `home_preflight.log` — first homing preflight
- `watchdog_interlock.log` — the concurrent session's status probes incl. the
  post-stop `$$`/`$I` dumps
- the three YAML files exactly as executed
