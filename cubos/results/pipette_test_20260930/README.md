# 2026-09-30: the trio with the Tic T500 in circuit. Firmware moved to 796 steps/mm; the run stopped at `decap vial_1` when every USB device on the Pi dropped at once

Asked for (PR #228): *"I moved vial 1 and vial 2 back 33mm in the positive y
direction, so they should be in range now. Fix the z travel as mentioned in
[the 09-26 comment] and run the protocol. I will report what I see with the
pipette."*

All times UTC, lab local (UTC−6) in brackets where it helps.

| | result |
|---|---|
| deck | `vial_1` y 0.665 → **33.665**, `vial_2` y 33 → **66** (Ben's +33 mm) |
| protocol | `pipette_park` z and step 5 `travel_z` 87 → **86** (= `z_max` 121 − the 35 mm tip) |
| gates, runner and Pi | `validate_setup` **PASS** · `--mock` **12/12** · `passive_shadow` **0** nominal, **0** tip-stuck |
| firmware | 🔑 **`panda_vcl_p20gen2_tic796_20260930.hex` flashed and verified**: the P20 GEN2 image with `STEPS_PER_MM 796` for the Tic's 1/8 step |
| pre-run plunger check | both instrument paths answer; **`HOME` stops on the switch in 0.94 s** |
| run | homed, parked, started `decap vial_1`; **at 00:23:24 the Pi's USB ports tripped over-current and all three devices dropped.** 0 protocol steps completed by CubOS's count; the magnet was never energized |

## 1. The two config fixes

The pipette sits +12.999 mm in Y from the capper, so the lowest deck Y it can
reach is 12.999. With the vials moved, `aspirate: vial_1` commands gantry
**(135.0, 20.666, 54.0)** instead of the unreachable y −12.334 of 2026-09-26.

Ben's +33 mm was applied literally. Seat 2 had been jog-read at y 33.0 for the
old `vial_2`, so if `vial_1` now sits in that seat, 33.0 may be up to 0.665 mm
closer; that is well inside the capper's seating margin, and `decap` is sensed.

`travel_z` resolves in the moving instrument's frame, so with the 35 mm tip on,
87 named gantry 122, above `z_max` 121. 86 is also the plane the hover clamp
picks for every tipped engage.

Gates ran on byte-identical files on both machines (sha256 of the body as run;
the committed headers were edited afterwards, comments only):

```
c208431f...e7f6  cub_xl_ben_pipette_capper.yaml
daf67b43...ff0f  ben_6vials_tiprack.yaml
3018618d...8e9d  pipette_test.yaml
```

`validate_runner.log`, `mock_trace_runner.log` (12/12, with the per-move trace),
`shadow_runner.log`, `shadow_tipstuck_runner.log` are CubOS `496819c` + the Pi's
three patches rebuilt on the runner (`git diff --stat` 9 files, +154/−22, as on
the Pi). `validate_pi.log`, `shadow_pi.log`, `shadow_tipstuck_pi.log` are the
Pi's own tree.

## 2. Why the firmware changed first

The session before this one (`../pipette_switch_search_20260929/`) proved the
plunger moves on the Tic and that `HOME` stops on the switch. It also flagged
that the running image still said `STEPS_PER_MM 1592`, written for the old
board's 1/16 step. On the Tic's 1/8 step, CubOS's connect-time prime
(`MOVE_TO 28.0` = 44,576 steps) would have driven the plunger about 56 mm, past
the 46.5 mm drop-tip end of its travel.

`796` is the safe value whichever scale is right: if 796 steps/mm is right,
every plane lands where Opentrons puts it; if 1592 was right after all, every
move comes out half as long and nothing overshoots. A true scale below 796 is
ruled out by the switch search, whose 22,845 steps from rest to the switch
would then exceed the whole P20 stroke.

**Provenance.** Built on the Pi from `~/panda_fw_vcl` (the tree that built the
current image, with its cached libraries), copied to `~/panda_fw_vcl_tic796`:

- an unchanged rebuild reproduced `panda_vcl_p20gen2_20260917.hex` exactly
  (sha256 `1960c354…`);
- with `STEPS_PER_MM 1592.0 → 796.0` and `MICROSTEPPING 16 → 8`, the image
  (sha256 `2bea99ba…`, 17,382 bytes) differs from it in **5 bytes**: four
  `ldi` immediates `0xC7 → 0x47` (the second byte of the float 1592.0 =
  `0x44C70000` vs 796.0 = `0x44470000`) and one `ldi` `4 → 5` (the TMC2209
  `MRES` for 1/16 vs 1/8, which now writes to nothing).

`firmware_flash_tic796.log`: `avrdude -U flash:v` matched the GEN2 image before,
the write verified, and afterwards the board matches only the 796 image. The
script is `flash_tic796.sh`.

## 3. Pre-run check (`precheck.log`, `precheck.py`)

```
00:21:21  cmd 14 pipette STATUS  0.008 s  OK:{"homed":0,"pos":0.00,"max_vol":20.00}
00:21:21  cmd  7 cap sensor      0.004 s  OK:{"value1":0}
00:21:22  cmd 10 HOME            0.938 s  OK:{"msg":"Pipette homed"}
00:21:22  cmd 14 pipette STATUS  0.008 s  OK:{"homed":1,"pos":0.00,"max_vol":20.00}
```

The Tic had been left de-energized by the previous session; it was energized
for the run (`tic_status_before_run.txt`, `tic_status_energized.txt`: Normal, no
errors, VIN 12.1 V idle → 10.1 V holding at 990 mA).

## 4. The run (`run_hardware.log`, `plunger_trace.json`, `mill_control_thisrun.log`, `gcode_thisrun.log`)

| UTC (lab) | what |
|---|---|
| 00:22:16 (18:22:16) | launched on the Pi, detached, with the camera + plunger-trace harness |
| 00:22:30 | plunger `STATUS`: `homed:0` |
| 00:22:31 | `HOME` **0.938 s**, OK |
| 00:22:40 | prime `MOVE_TO 28.0` **9.285 s**, OK, `v:[28.00]`: 22,288 steps at 2500/s is 8.92 s, so every step went out |
| 00:22:42 → 00:23:00 | step 0 `home`: `$H`, *Homing completed*, WPos (388, 233.665, 121) |
| 00:23:00 → 00:23:17 | step 1 park: Z 98 → X 206 → Y 25 |
| 00:23:17 → 00:23:23.3 | step 2 `decap vial_1`: Z 121 → X 189 → Y 33.665, then `G01 Z98.0` sent at 00:23:23.305 |
| **00:23:24** | kernel: **`over-current change` on all four USB ports**; the Tic (`1-1`) and the Arduino (`3-1`) disconnect |
| 00:23:25 | the CH340 (`3-2`, GRBL) disconnects; all three re-enumerate within about a second. The Arduino returns as **`/dev/ttyACM1`**, because the dying CubOS still held `ttyACM0` |
| 00:23:25.492 | CubOS: `G01 Z98.0` fails, *"device reports readiness to read but returned no data"*; `decap` aborts; the safe retract fails; the failure retract then raises the known upstream `KeyError: "Unknown instrument 'PawduinoCapper'"` |

CubOS's own summary reads *"0 steps executed before exit"*, although the G-code
shows steps 0 and 1 completing. Nothing after the prime reached the plunger, and
the camera harness had not reached its first capture point (after step 2), so
there are no frames.

### What it was not

- **Not the Pi's own supply.** `vcgencmd get_throttled` = `0x0` (no
  under-voltage since boot), EXT5V 5.126 V, and the PSU negotiated 5 A, so the
  USB budget is the full 1.6 A. The Pi did not reboot.
- **Not a Tic reset.** The Tic reports *Last reset: Power-on reset*, up since
  about 17:35 lab. Its logic runs from `VIN`, so only its USB link dropped. It
  was still energized with no errors afterwards.
- **Not the electromagnet.** The capper was still descending to its approach
  height; the magnet is only switched on after the engage descent.

### What it looks like

The Pi 5 feeds all four USB ports through one current-limited switch, so a fault
on one device's `VBUS` trips all of them. It happened once, at the instant the Z
axis started down over vial_1, during the first run ever with the Tic in the
circuit; the same trio has run 12/12 without it. Candidates, cheapest check
first:

1. **The Tic's grounds and 5 V.** Only Tic `GND` → Arduino `GND` should join the
   two systems. Nothing may join Tic `5V` to Arduino `5V` (the Tic doc's
   warning), and the 12 V supply's `+` must reach only Tic `VIN`.
2. **A USB cable or connector flexing with the motion.** The Pi rides the
   gantry, and on 2026-09-24 motion pulled its power cable.
3. **Anything on the Arduino's 5 V** (the capper's sensor and driver side).

## 5. How the machine was left

| | |
|---|---|
| gantry | GRBL reset by the USB drop: `Alarm`, position reference lost. The head was last commanded to (189, 33.665, 98), above vial_1. Re-home before anything else |
| vial_1 | still capped: the decap never engaged, and the magnet was never on |
| electromagnet | off (the Arduino reset with the USB drop) |
| plunger | prime completed, so about 28 mm below home if 796 is right. The Arduino reset cleared its counter (`homed:0`) |
| Tic | **de-energized** after the run (`tic_status_after_run.txt`, VIN 12.6 V), so it is not heating the pipette at 990 mA. `ticcmd --energize` before the next run |
| Arduino port | now **`/dev/ttyACM1`**. The gantry file names `/dev/ttyACM0` for both instruments, so the next run would stop at connect (before any motion) until the Arduino is replugged or both `port` entries move to the `by-id` path |

## Files

| file | what |
|---|---|
| `run_hardware.log` | the run's full output |
| `plunger_trace.json` | the three plunger commands, timed |
| `mill_control_thisrun.log`, `gcode_thisrun.log` | the GRBL exchange and G-code from this run |
| `kernel_usb_18-22_18-30.log` | the kernel's USB events around the drop |
| `precheck.py`, `precheck.log` | the pre-run instrument and `HOME` check |
| `flash_tic796.sh`, `firmware_flash_tic796.log` | the flash, with verifies before and after |
| `tic_status_*.txt` | the Tic before, energized, and after |
| `validate_*.log`, `mock_trace_runner.log`, `shadow_*.log` | the gates, runner and Pi |

Host names and home paths in the logs are redacted to `<pi>` and `<user>`.
