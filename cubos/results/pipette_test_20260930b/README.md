# 2026-09-30 (b): the trio on the Tic T500 — 12/12 steps, every plunger command executed, no steps lost

Asked for (PR #228): *"I homed the machine myself, and everything is plugged
back in. Run the trio"*, after the 2026-09-30 00:23 run
(`../pipette_test_20260930/`) stopped on a USB over-current trip that Ben traced
to the Tic's `A2` motor lead coming loose.

All times UTC; lab local is UTC−6 (the Pi's own logs are in lab time).

| | result |
|---|---|
| Pi, ports | booted ~21:52; Arduino `/dev/ttyACM0`, GRBL `/dev/ttyUSB0`, Tic on USB, as the gantry file names them; `throttled=0x0` |
| Tic | STEP/DIR, 1/8, 990 mA, energized, no errors. VIN 12.6 V de-energized → 11.0 V energized, so the coils draw current |
| firmware | `panda_vcl_p20gen2_tic796_20260930.hex` verified on the board (`avrdude -U flash:v`, read-only) |
| pre-run `HOME` | **12.687 s, OK**, from where the last run's prime left the plunger |
| GRBL | 🔴 **found factory-reset** (below). Restored the calibrated frame, no motion |
| gates on the Pi | `validate_setup` **PASS** · `--mock` **12/12** · `passive_shadow` **0** nominal, **0** tip-stuck |
| run | **12/12 steps, `Protocol complete`**, campaign 68, 22:08:13 → ~22:12:20 |
| plunger | all 8 commands `OK`, each at its commanded rate |
| post-run `HOME` | **12.680 s**, from the same firmware position: **no net step loss over the whole run** |
| USB | no over-current, no disconnects during the run (`kernel_during_run.log`) |

## 1. The controller had been factory-reset

`grbl_full_before_restore.json` against the last-known-good record
(`../pipette_test_20260926b/grbl_settings_20260926b.json`, the frame the deck
file was jog-measured in, and what the 09-30 run used):

| | 2026-09-26b | found | |
|---|---|---|---|
| `$10` status mask | 0 | 3 | gantry file: 0 |
| `$20` soft limits | 1 | **0** | gantry file: 1 |
| `$21` hard limits | 0 | **1** | not in the gantry file |
| `$122` Z accel | 150 | 300 | not in the gantry file |
| `$130/$131/$132` | 391 / 236.665 / 124 | **400 / 300 / 100** | gantry file: 391 / 236.665 / 124 |
| `G54` | −391, −236.665, −124 | **0, 0, 0** | the deck frame |

Everything else (`$0`–`$6`, `$11`–`$13`, `$22`–`$27`, `$30`–`$32`,
`$100`–`$112`, `$120`, `$121`) and the build (`[VER:1.1h.20190825:]`
`[OPT:V,15,128]`) are unchanged. 400/300/100 are the travel values in Ursa's
stock `packages/core/configs/gantry/cub_xl_panda.yaml`, and a zeroed `G54` with
round travel values is not a calibration result, so this reads as the
controller's EEPROM being reset to its build defaults (`$RST=*`, or GRBL's own
restore after an EEPROM read failure; the 09-30 USB/power interruptions are a
candidate). The cause is not known. Ben's homing was done off the Pi: its CubOS
logs end with the 09-30 run.

As found, `run_protocol` would have refused at connect (critical-settings
mismatch). With `G54` at zero the deck frame is gone from the controller.

**Restored (`grbl_restore.py`, `grbl_restore.log`, `grbl_after_restore.json`):**
only what the gantry file checks, plus the work offset:
`$10=0`, `$130=391`, `$131=236.665`, `$132=124`, `$20=1`, then `$X` (clears the
boot alarm, which blocks G-code; no motion was sent) and
`G10 L2 P1 X-391 Y-236.665 Z-124`. Read back as intended: `WCO:-391.000,-236.665,-124.000`.

**Left as found:** `$21=1` (hard limits on) and `$122=300`. Neither is checked by
CubOS; hard limits only act on a switch closing, and nothing in this protocol
reaches a switch outside homing. If they were not meant to change:
`$21=0`, `$122=150` restores the 09-26 state exactly.

The frame is the same one as before only if the switches, pull-off and steps/mm
are unchanged, and they are (`$23`, `$27`, `$100`–`$102` identical, same build,
no `Z` in `OPT` so homing leaves MPos at −pull-off). The run confirms it:
after homing, WPos read `388.000, 233.665` (max travel − 3 mm pull-off, as on
09-30), and `decap vial_1` captured the cap (frame `step02`).

## 2. Pre-run checks (`precheck_tic.log`, `precheck.log`)

```
22:00:51  energized  VIN 11.1  (x5)
22:00:55  de-energized VIN 12.6 (x5)
22:00:58  re-energized VIN 11.0 (x5)
22:01:27  cmd 14 STATUS   OK:{"homed":0,"pos":0.00,"max_vol":20.00}
22:01:40  cmd 10 HOME     12.687 s  OK:{"msg":"Pipette homed"}
```

The last run's prime (`MOVE_TO 28.0`, 22,288 steps down) completed before the
USB trip. `HOME` seeks at ~527 µs/step and backs off 796 steps (~0.41 s) plus a
100 ms debounce, so 12.687 s is ~23,110 steps of seek: the prime's 22,288 plus
the 796-step back-off it started from (23,084). The motor carried the plunger up
to the switch, which it can only do with both coils connected.

## 3. The run (`run_hardware.log`, `plunger_trace.json`, `mill_control_thisrun.log`)

Launched detached on the Pi with the camera + plunger-trace harness, the Tic
polled every ~0.4 s (`tic_poll_run.log`).

| UTC (end) | step | command | dt | what it means |
|---|---|---|---|---|
| 22:08:27.9 | connect | `HOME` | 0.934 s | already at the switch after the pre-run `HOME` |
| 22:08:37.2 | connect | prime `MOVE_TO 28.0` | 9.285 s | 22,288 steps down at 2500/s |
| 22:09:49.7 | 3 `pick_up_tip` | `MOVE_TO 0.0` | 9.286 s | 22,288 steps **up**: the gated direction runs |
| 22:10:11.9 | 4 `aspirate` | `ASPIRATE 20.0` | 5.003 s | reply `v:[20.00,1.20]`: down to prime 28.0, up 20 µL × 1.34 = 26.8 mm, lands at 1.2 |
| 22:11:08.8 | 8 `blowout` | `MOVE_TO 32.5` | 10.379 s | +31.3 mm |
| 22:11:26.6 | 9 `drop_tip` | `MOVE_TO 46.5` | 4.646 s | +14.0 mm |
| 22:11:32.7 | 9 `drop_tip` | `MOVE_TO 28.0` | 6.139 s | −18.5 mm |

The `MOVE_TO` legs fit 2500 steps/s at 796 steps/mm to within ~0.4 s of
overhead. `ASPIRATE` steps at the firmware's faster aspirate rate: 43,621 steps
in 5.0 s, about 9,600 steps/s (the same rate 1592-step builds showed in
campaigns 26/36/54). At 1/8 step that is ~6 rev/s from a standing start.

**Closed-loop check (`post_run_home_check.log`).** After the run the Tic was
re-energized for one `HOME`: **12.680 s**, against **12.687 s** before the run
from the same firmware position (28.0). The limit switch is a physical
reference, so the plunger ended within ~13 steps (~0.02 mm) of where the
firmware believed it was, after ~160,000 steps in both directions, including
the fast aspirate legs and the 46.5 mm drop-tip plane. No steps were lost, and
the plunger reached 46.5 without stalling on a stop.

Gantry: homing completed first try at both ends (22:08:57, 22:12:09); no
alarms. Every target sent, from `mill_control_thisrun.log`:

```
Z 52.0 x4   capper engage (vial z 54 + engage 15 + depth -17): 4 engages = no capture retries
Z 54.0 x2   aspirate / blowout, tip end deck 19
Z 57.0      pick_up_tip          Z 92.0  drop_tip (tip end at pickup_z 57)
Z 98.0 x9   capper transit (safe_z 115 - 17)
Z115.0      bare-nozzle hover    Z121.0 x8  tipped hover, clamped (tip end 86)
X 135 / 189 pipette / capper over the vials    X 265, Y 32.665  tip rack A1 (Ben's jog point)
```

Tic during the run: 583 polls, energized and `Normal` throughout, no errors.
VIN ranged 8.0–11.2 V; it dropped below 9.5 V only between 22:11:16 and
22:11:36, around `drop_tip`. The 12 V brick is soft (seen on 09-29 too); the
Tic runs down to 4.5 V and no steps were lost, but if the gantry shares that
brick, that would explain a dip that starts before the plunger moves.

## 4. What this does not show

- **Liquid.** Timing and the switch prove the plunger moved as commanded; they
  do not show liquid drawn or expelled, or a tip seated and ejected. That needs
  eyes (or a balance), and `UL_TO_MM 1.34` is still Opentrons' nominal figure,
  not a gravimetric calibration.
- **The scale.** 796 steps/mm assumes a 2 mm lead at 1/8 step; the ruler check
  (10 mm commanded against a rule) is still open. Every plane lands where
  Opentrons puts it only if 796 is right.
- **Frames.** The one camera rides the head and looks at the deck, not at the
  pipette, so it shows the gantry's position (`step02`: vial_1 open, vial_2
  capped) but not the plunger or tip.

## 5. How the machine was left

| | |
|---|---|
| protocol | completed, closing `home` ran |
| electromagnet | off (`CMD_EMAG_OFF` → `OK`), cap sensor `0` |
| plunger | homed (1 mm below the switch) by the post-run check |
| Tic | **de-energized** (VIN 12.6 V) so it is not holding ~4 W in the pipette. `sudo ~/.local/opt/pololu-tic-1.8.1-linux-rpi/ticcmd --energize` before the next run |
| GRBL | restored settings persist in EEPROM; the board resets on port close, so re-home before anything else |

## Files

| file | what |
|---|---|
| `run_hardware.log`, `plunger_trace.json`, `mill_control_thisrun.log` | the run |
| `frames/` | 6 in-run frames + the pre-run test shot, cam0 only (the second camera is disconnected) |
| `campaign_68_20260930_220813/` | CubOS's campaign CSVs |
| `tic_poll_run.log`, `tic_status_*.txt` | the Tic before, during, after and de-energized |
| `precheck_*`, `precheck.log`, `grbl_read.py`, `grbl_settings_20260930b.json` | the pre-run checks |
| `grbl_full_read.py`, `grbl_full_before_restore.json`, `grbl_restore.py`, `grbl_restore.log`, `grbl_after_restore.json` | the controller as found, and the restore |
| `validate_pi.log`, `mock_pi.log`, `shadow_*.log` | the gates, on the Pi's own tree (`496819c` + its 3 patches) |
| `homecheck_root.sh`, `post_run_home_check.log`, `post_arduino.py`, `post_run_arduino.log`, `deenergize.sh` | the post-run checks |
| `kernel_during_run.log` | kernel messages over the run window: camera only, no USB events |
| `launch.sh`, `tic_poll.sh` | how it was launched |

The G-code is in `mill_control_thisrun.log` (`Command sent:` lines); this
CubOS build wrote nothing to `command.log` for this run. Host and user names are
redacted to `<pi>` and `<user>`.
