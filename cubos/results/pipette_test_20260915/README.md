# 2026-09-15 — campaign 26, and the TMC2209 finally answered

Requested by @benwhitney5463 on PR #171: run the trio, delete the dead park
position, take pictures, then set the p20 firmware constants and stop.

Trio run, exactly as committed on this branch at `4eaf953`:

* `cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml`
* `cubos/configs/deck/ben_6vials_tiprack.yaml`
* `cubos/configs/protocol/vcl/pipette_test.yaml`

CubOS `496819c` + the two ported patches, on `rpi-5-des4`.

## The run

```
RESULT: PASS - protocol motion targets within gantry bounds
Protocol complete — 12 steps executed.
```

Campaign 26, `21:51:38 → 21:56:41` UTC. Decapped vial_1, pressed onto A1,
aspirated, parked, recapped vial_1, decapped vial_2, blew out, dropped the tip,
capped vial_2, home. No capper retries, no alarms. Both `passive_shadow` passes
reported 0 interferences.

The wall clock is ~1 min longer than campaign 77's 4m 03s purely because of the
camera timeouts below; the motion is unchanged.

## Plunger trace — identical to campaigns 77 and 83

| step | command | dt | firmware stepped? |
| --- | --- | ---: | --- |
| `connect()` | `STATUS` | 0.008 s | `homed:0, pos:0.00, max_vol:300.00` |
| `connect()` | `HOME` | 0.520 s | back-off only — limit switch reads asserted |
| `connect()` prime | `MOVE_TO 5.0` (down) | 3.354 s | yes |
| `pick_up_tip` | `MOVE_TO 0.0` (up) | 0.106 s | no — refused |
| `aspirate` | `ASPIRATE 0.5` (down) | 5.960 s | yes → pos 36.00 |
| `blowout` | `MOVE_TO 7.0` (up from 36) | 0.109 s | no — refused |
| `drop_tip` | `MOVE_TO 10.0` (up) | 0.108 s | no — refused |
| `drop_tip` | `MOVE_TO 5.0` (up) | 0.107 s | no — refused |

Motion costs ~0.673 s/mm (`MOVEMENT_VELOCITY` 2500 steps/s at `STEPS_PER_MM`
1592, plus ~23 µs/step of `digitalWrite`/`digitalRead` overhead), so a round
trip that does not scale with the commanded distance emitted no steps.

**A round trip that does scale only proves the Arduino toggled STEP.**
`stepMotor()` bit-bangs the pin and counts loop iterations — no encoder, no
current sense, no feedback of any kind.

## 🔴 The finding: the TMC2209 is not communicating

The 10 kΩ A0–A1 bridge is the right hardware change, but at the firmware as
flashed it was inert: `setupMotor()` only ever *writes* registers, and nothing
in the command set exposed driver state. The reflash below added
`CMD_PIPETTE_DRIVER_STATUS = 29`, and the answer was immediate and stable
across five consecutive reads:

```
OK:{"msg":"Driver status","v":[0.00,0.00,-1.00]}
      comm = 0    flags = 0    current_scaling = -1 (unread)
```

`comm = 0` is unambiguous. The library's chain is

```cpp
bool isCommunicating()          { return (getVersion() == VERSION); }
bool isSetupAndCommunicating()  { return serialOperationMode(); }
bool isCommunicatingButNotSetup(){ return isCommunicating() && !isSetupAndCommunicating(); }
```

so `comm = 0` means `getVersion()` returned something other than `0x21` — **no
valid reply at all**, not "replied but not configured". Every register write
`setupMotor()` makes (`setRunCurrent`, `setHoldCurrent`,
`setMicrostepsPerStep`, `enableStealthChop`, `enableCoolStep`, `enable`) has
therefore never landed, on any run, and the driver has been on power-on
defaults throughout.

That has a useful corollary: `setOperationModeToSerial()` never landed either,
so `i_scale_analog` is still 1 and **the VREF potentiometer is in circuit**.
In standalone mode a powered driver with VREF up would hold the motor.

### The two-minute discriminator

With the driver idle and powered, try to turn the plunger by hand.

| holding torque | reading |
| --- | --- |
| **none** | the driver has no coil current — VM absent at the screw terminal, VREF at zero, or the coils open. This also explains `comm = 0` if VDD is missing. |
| **present** | the driver is powered and energised, so `comm = 0` is the UART path alone — check the PDN_UART wire is on A1, and the bridge. |

Note the new `flags` word would have reported `open_load_a`/`open_load_b`
directly — but those bits require a reply, so they are only meaningful once
`comm` is non-zero.

## Cameras

`--at 2,3,4,7,8,9`, two CSI `imx708_wide`, `--vflip cam1_csi1` (that camera is
mounted rotated and faces the room; flipping it at capture time makes the deck
readable).

**7 of 12 frames.** `cam0_csi0` got all six. `cam1_csi1` timed out at the
20 s capture limit on five of six, then succeeded on the last. The design rule
held — no camera failure touched the protocol, and the run completed 12/12 —
but each timeout cost 20 s of wall clock between steps.

Not the `--vflip` flag: the same flag worked in the pre-run test shot (0.57 s)
and on the final in-run capture (0.58 s). The likely cause is contention for
CMA/camera buffers on a **1 GB** Pi 5 with two 4608×2592 sensors while CubOS is
resident — `cam0` at 0.68 s never failed, `cam1` blocked. Worth trying a lower
capture resolution, a longer `CAPTURE_TIMEOUT_S`, or one camera at a time.

The `cam1_csi1` frames committed here are **cropped** to the machine: the left
third of that camera's field is the room, with a lab member at a desk in it,
and this repository is public. The uncropped originals are on the Pi in
`/tmp/run_frames`.

## Machine state, left clean

| | |
| --- | --- |
| Protocol | completed, `home` as the final step |
| Electromagnet | off — `CMD_EMAG_OFF`, `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Caps | both returned to vials 1–2 by the protocol's own `cap` steps |
| GRBL | `Alarm` — normal, the board resets when the port closes. Re-home first. |
| `$130/$131/$132` · `$20` | 409.000 / 309.000 / 124.000 · `1` — matches the gantry file |
| Ports | `/dev/ttyUSB0` · `/dev/ttyACM0` — both free |
| Plunger | ~19 mm of one-way travel commanded (prime 5 + aspirate ~14); retraction is still refused, so none of it came back |

## Files

| | |
| --- | --- |
| `run_hardware.log` | the full run, including every `@@PLUNGER` and `@@CAM` line |
| `plunger_trace.json` | the eight plunger commands, timed |
| `validate.log`, `mock.log` | offline gates |
| `frames/` | the seven frames + `frames.json` |
