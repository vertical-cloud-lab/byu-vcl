# 2026-08-26 XY-square hardware run / E-stop test #2 (issue #182)

First hardware execution of `xy_square.yaml` on the CubXL, run remotely from
GitHub Actions via the Pi (CubOS checkout `cbc33dc`, CLI
`python -m cubos.tools.run_protocol`). Requested by @jarrettshupe: "a simple
protocol to have the gantry only move in the X and Y directions ... a small
square around the center of the deck ... I would like to keep testing the
estop."

Two runs were started; **both were halted mid-motion by an E-stop press**,
one on a `+Y` edge and one on a `+X` edge. Combined with the two
human-confirmed presses on 2026-08-25, the E-stop is now **4 for 4 during
normal protocol motion**.

## What ran

Config trio (copies here are byte-identical to what executed, modulo the
serial-port line noted below):

- `xy_square.yaml` — 55 steps: home, one descent to Z 111, 10 laps of an
  80 x 80 mm square centred on deck (245, 128), park at centre, home
- `cub_xl_ben_pipette_capper.yaml` — gantry, 2026-08-24 calibration
- `sterling_6vials_tiprack.yaml` — deck (unchanged from 2026-08-25)

`validate_setup` PASS (84 motion targets) and a full 55-step `--mock` PASS on
the Pi before any motion.

## Why the run is X/Y only

CubOS's mill driver never interpolates diagonally: `_build_direct_move` and
`_build_transit_move` (`gantry/gantry_driver/driver.py`) emit one `G01` per
*changed* axis in X -> Y -> Z order and prune any axis already at its target.
Every waypoint in `xy_square.yaml` sits at Z 111.0 and every move carries
`travel_z: 111.0`, so after the initial descent **no Z word is emitted at
all**, and because consecutive square corners differ in exactly one axis,
each edge is a single pure single-axis move at F2000 (33 mm/s, ~2.4 s per
80 mm edge).

The only Z motion in the protocol is the 11 mm descent from the post-home
Z 122.0 to the Z 111.0 working plane, executed once at the home corner
before any XY travel, plus the closing `home`. `travel_z` is specified
rather than omitted so that a *lift* to 111 is always the first command if
the driver's position read fails and it must emit the un-pruned sequence.

## Timeline (UTC)

| Run | Campaign | Window | Elapsed | Ended by |
|---|---|---|---|---|
| 1 | 19 | 23:05:05–23:06:10 | 65 s (~3 laps) | E-stop press — died on `G01 Y156.0 F2000` (`hardware_run1.log`) |
| 2 | 20 | 23:08:24–23:09:46 | 83 s (~4–5 laps) | E-stop press — died on `G01 X233.0 F2000` (`hardware_run2.log`) |

Both aborts read `Command execution timed out after 5 seconds: Grbl 1.1h
['$' for help]` — a fresh GRBL boot banner arriving where the `ok` for the
in-flight move should have been.

As on 2026-08-25, `run_protocol` prints "0 steps executed" on the abort path;
that counter is wrong on failure. Elapsed time and the failing G-code show
each run executed several complete laps.

## E-stop findings

- **Controller-MCU reboot signature, twice more.** The boot banner mid-command,
  with `dmesg` showing the CH341 USB-serial converter **never disconnecting**
  (it is powered from the Pi's USB port, so it survives a control-box power
  cut). The stop therefore cuts/resets the control box rather than pausing
  G-code — the good class of E-stop behaviour.
- **Verified stopped, not coasting.** Read-only probes after each abort:
  `<Alarm|WPos:389.333,235.000,125.000|FS:0,0>` — feed 0, position frame
  reset to the post-boot default, identical across three probes 3 s apart.
- **Axis coverage:** run 1 was stopped during a `+Y` move, run 2 during a
  `+X` move. The previous session's two presses were during multi-axis
  transits.
- `$21=0` — **hard limits are still disabled** on the flashed controller
  (`$20=1` soft limits on, `$22=1` homing on). Unchanged from 2026-08-25 and
  deliberately not modified by this session. The untested scenario from the
  2026-08-18 investigation — E-stop while a closed-loop stepper stalls past
  a travel end — still stands, and setting `$21=1` first is still the
  recommendation before attempting it.

## Serial port changed: use the by-id symlink

The control box was power-cycled between 2026-08-25 and this run
(`dmesg`: `ttyUSB0` disconnected, re-enumerated as **`ttyUSB1`**), so the
repo's `serial_port: /dev/ttyUSB0` no longer pointed at the gantry. The
Pi-side copy of the gantry YAML in this directory therefore reads:

    serial_port: /dev/serial/by-id/usb-1a86_USB_Serial-if00-port0

That symlink is stable across replugs and renumbering. Worth adopting in the
repo's gantry YAML, or pinning with a udev rule.

`stty -F <port> -hupcl` was re-applied before connecting (it reverts on
unplug — the same transient fix documented in the 2026-08-25 run record);
both runs then connected without racing a DTR-triggered reboot.

## Machine state as left

- Physically parked somewhere on the square perimeter — gantry x 153–233,
  y 76–156, Z 111 — clear of every piece of labware. Motors de-energised
  (`$1=25`, no holding torque at idle).
- Controller alive, **ALARM-latched and unhomed, position lost** →
  **home (`$H`) before next use.**
- Serial port free: no process holds it, no `run_protocol` is alive, and no
  interlock was installed this session (the 2026-08-25 operator-stop
  interlock had already expired and removed itself).
- Pi-side: created `~/run_20260826_xy_square/` (configs + logs) and cleared
  `hupcl` on the gantry port. No services, cron, or repo checkouts modified.

## Run policy used

Up to three runs were queued, with the rule that **a non-zero exit stops the
sequence — no blind retry**. Run 1's abort halted the queue; run 2 was
started only after announcing it in the issue comment, and no run 3 was
attempted. This is a direct response to the 2026-08-25 incident, where an
agent re-running the protocol after each press made a working E-stop look
like a machine that would not stop.

## Files

- the protocol itself lives at `cubos/configs/protocol/vcl/xy_square.yaml`
- `validate_setup.log`, `mock_run.log` — offline preflight
- `hardware_run1.log`, `hardware_run2.log` — full `run_protocol` output
- `campaigns_19_20.csv` — CubOS campaign rows for both runs
- `cub_xl_ben_pipette_capper.yaml`, `sterling_6vials_tiprack.yaml` — exact
  configs as executed (usernames/hostnames scrubbed to `PIUSER`/`PIHOST`)
