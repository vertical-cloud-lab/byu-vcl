# `pipette_test.yaml` on hardware — 2026-09-08, campaign 83

**12/12 steps, 4m 3s, `completed`.** Gantry and capper clean: no capper retries,
no GRBL alarms, no warnings beyond the routine "GRBL is in Alarm state after
connect" and the three expected tipped-hover clamp notices.

Ran the trio exactly as committed at `a0ccbb7` — no config edit was needed, the
serial ports came back on the same names after the CubXL was replugged.

```
validate_setup                PASS  (12 protocol targets)
run_protocol --mock           12/12
passive_shadow                0 interferences (28 poses, 36 obstacles)
passive_shadow --tip-stuck    0 interferences
```

## Ports after the replug — unchanged

| device | port | USB ID | by-id |
| --- | --- | --- | --- |
| GRBL gantry | `/dev/ttyUSB0` | `1a86:7523` CH340 | `usb-1a86_USB_Serial-if00-port0` |
| capper + pipette Arduino | `/dev/ttyACM0` | `2341:0043` Uno R3 | `usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00` |

Both enumerated at 15:14 local. Prefer the `by-id` paths over `ttyACM0`/`ttyUSB0`
if a third device is ever added — the CH340 and the Uno land on different
subsystems today, but the number is assignment order, not identity.

Controller read live before the run, matching the gantry file exactly:

```
$20=1  $21=0  $22=1  $23=0  $130=409.000  $131=309.000  $132=124.000
<Alarm|WPos:409.000,309.000,124.000|WCO:-409.000,-309.000,-124.000>
```

## Gantry geometry commanded

From this run's own G-code (`gantry_command_thisrun.log`):

```
  9 x  Z99.065    capper transit / park     (safe_z 115 + depth -15.935)
  8 x  Z124.0     tipped hover, CLAMPED by the hover-clamp patch
  4 x  Z54.065    capper engage             (rim 55 + engage_depth 15)
  2 x  Z55.0      aspirate / blowout        (tip end deck 20, nozzle at rim)
  1 x  Z115.0     bare-nozzle hover at safe_z
  1 x  Z122.0     step 5, pipette_park at travel_z 87
  1 x  Z92.0      drop_tip
  1 x  Z57.0      pick_up_tip
```

Distinct X: 154.0 (vial column in the pipette frame), 206.0 (capper over the
vials), 236.0 (capper park), 284.0 (tip rack — the measured jog point,
reproduced for the fourth consecutive run).

## Plunger trace

Motion costs 0.673 s/mm — see "where 0.673 comes from" below. A round trip that
does not scale with the commanded distance emitted no steps.

| step | command | dt | firmware stepped? |
| --- | --- | --- | --- |
| `connect()` | `STATUS` | 0.007 s | — (`homed:0, pos:0.00, max_vol:300.00`) |
| `connect()` | `HOME` | 0.520 s | no — back-off only, switch asserted |
| `connect()` prime | `MOVE_TO 5.0` (down) | 3.354 s | **yes** |
| `pick_up_tip` | `MOVE_TO 0.0` (up) | 0.106 s | no — refused |
| `aspirate` | `ASPIRATE 0.5` (down) | 5.961 s | **yes** → pos 36.00 |
| `blowout` | `MOVE_TO 7.0` (up from 36) | 0.106 s | no — refused |
| `drop_tip` | `MOVE_TO 10.0` (up from 36) | 0.109 s | no — refused |
| `drop_tip` | `MOVE_TO 5.0` (up) | 0.107 s | no — refused |

Byte-for-byte the shape of campaign 77. Two forward moves: ~3.4 s at startup
before the gantry homed, ~6 s down in vial_1 during the aspirate.

## New this session: a raw-step probe underneath the counter and the gate

`cubos/tools/pipette_driver_probe.py` uses `CMD_MOVE_RELATIVE` (code 16), which
takes raw steps and a velocity in steps/second and hands them to `moveSteps()`.
Two properties make it the right instrument:

* `moveSteps()` returns `stepsCompleted == abs(steps)`, and the Interface
  handler turns a False into `ERR:{"error":"Failed to move relative"}`. An
  aborted move is reported **explicitly**, so the switch state no longer has to
  be inferred from a round-trip time.
* the gate in `stepMotor()` only fires when DIR is LOW (UP), so **DOWN is
  completely ungated** — it exercises the driver and motor with the switch out
  of the picture.

Caveat that applies to any move: `stepMotor()` emits the step *before* it tests
the switch, so a 1-step up move completes and returns success even when the gate
is asserted. 2 steps is the smallest move that can report the abort.

### Limit switch — open loop, confirmed rather than inferred

```
15:32:00  ASSERTED (D9 HIGH, loop OPEN)  dt= 0.11s  ERR:{"error":"Failed to move relative"}
```

`PIPETTE_LIMIT_PIN` (D9) is `INPUT_PULLUP` and the firmware treats HIGH as "at
the limit", so an **open** switch loop reads asserted. At rest a healthy
normally-closed contact holds it clear.

### Motor — the Arduino's STEP output is perfect

```
DOWN 1.0 mm   dt=  4.04s  expected~4.0s  OK:{"msg":"Moved relative","v":[1.00,1592.00,400.00]}
counter 0.0 -> 1.0
```

1592 steps at 400 steps/s, ungated, deliberately slow so the motor makes its
maximum torque and noise. 4.04 s measured against 4.00 s commanded — every step
was emitted at the commanded rate. `stepMotor()` bit-bangs STEP and counts loop
iterations with no feedback of any kind, so this proves the **Arduino** did its
job and says nothing about whether the motor turned.

## Three firmware readings that close open questions

Read out of `BU-KABlab/PANDA_Arduino` (`src/Pipette.cpp`, `include/Pipette.h`)
and `janelia-arduino/TMC2209` v10.1.1.

### `ASPIRATE`'s odd landing positions are the two-leg move plus the gate

`aspirate()` clamps the volume to `MIN_VOLUME 5.0`, moves **down to
`PRIME_POSITION 36.0` first**, and only then moves up to
`36.0 - volume * UL_TO_MM`:

```c
volume = constrain(volume, MIN_VOLUME, MAX_VOLUME);
if (!moveTo(PRIME_POSITION, velocity)) return false;
float targetPosition = PRIME_POSITION - volume * UL_TO_MM;
return moveTo(targetPosition, velocity);
```

So `ASPIRATE 0.5` is really "go to 36.0, then go to 35.451". The second leg is
**upward**, so it is subject to the gate:

* switch clear (campaign 69) → both legs run → reported 35.45
* switch asserted (campaigns 77, 83) → second leg refused → reported 36.00

That accounts for every value seen and closes the "ASPIRATE doesn't honour its
argument / has a second counter" item. It does honour it; the second leg just
cannot execute. It is also why aspirate is *never* a small move: it always
drives to 36.0 first, whatever volume is asked for. (`dispense()` ignores its
volume argument entirely and moves to `BLOWOUT_POSITION 44.0`.)

### Where 0.673 s/mm comes from

`stepMotor()` computes `stepDelay = 1000000 / velocity`, clamped to
[100, 10000] µs. The effective velocity is `MOVEMENT_VELOCITY = 2500` steps/s →
400 µs, plus ~23 µs of `digitalWrite`/`digitalRead`/loop overhead → ~423 µs per
step. At `STEPS_PER_MM 1592` that is **0.673 s/mm**, matching every measurement
taken since 2026-08-31. The constant is not a fit; it is arithmetic.

### The TMC2209 library defaults are *not* the problem

Two hypotheses ruled out by reading the pinned library rather than assuming:

* **SoftwareSerial baud.** The `setup(SoftwareSerial&)` overload defaults to
  **9600**, not the 115200 the `HardwareSerial` overloads use. 9600 on an
  ATmega328P is comfortable. `stepperDriver.setup(softSerial)` passes no baud,
  so 9600 is what runs.
* **`enable()` writing a zero.** `toff_` is initialised to `TOFF_DEFAULT = 3`
  (`TMC2209.h:508-510`), so `enable()` writes a live chopper config, not another
  disable.

`initialize()` does still run `minimizeMotorCurrent()` and `disable()` before
`setupMotor()` re-enables — that path is real, and it is UART-only because
`setHardwareEnablePin()` is never called. But it only strands the driver if the
register writes **partially** land, which is a narrower failure than a plain
"UART is misrouted". See `cubos/docs/opentrons-pipette-wiring.md`.

## ⚠️ While the switch reads asserted, the plunger is a one-way ratchet

Every upward command is refused, `HOME` only zeroes the counter, and there is no
other retract path in the command set. So each run that reaches `aspirate`
drives the plunger further out and nothing brings it back. This session
commanded roughly +6 mm (bench), +13.9 mm (prime + aspirate) and +1 mm (motor
test). Commanded, not necessarily physical — a plunger against its stop just
skips steps.

Practical consequence for diagnosis: `--motor-test` cannot distinguish "no coil
current" from "already at the mechanical stop". **Holding torque can** — grab the
plunger with the driver idle; energized coils resist. That test is independent
of both the stop and the counter.

## Machine state, left clean

| | |
| --- | --- |
| Protocol | completed, `home` as the final step |
| Electromagnet | off — `CMD_EMAG_OFF`, `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Caps | both returned to vials 1–2 by the protocol's own `cap` steps |
| GRBL | `Alarm` — normal, the board resets when the port closes. Re-home before the next run. |
| Ports | `/dev/ttyUSB0` · `/dev/ttyACM0` — both free |
| `~/CubOS` | `cbc33dc` + all four patches |

## Files

| file | what it is |
| --- | --- |
| `run_hardware.log` | the full hardware run, including the `@@PLUNGER` trace lines |
| `plunger_trace.json` | the 8 plunger commands with timings |
| `gantry_command_thisrun.log` | this run's G-code, sliced out of the appended log |
| `probe_switch.log` | the raw-step limit-switch read |
| `probe_motor.log` | the slow ungated 1 mm motor test |
| `bench_move.log` | `pipette_bench_check.py --move`, run before anything was sent |
| `validate.log`, `mock.log`, `shadow_*.log` | the offline gates |

Campaign CSVs: `../campaign_83_20260908_212252/`.
