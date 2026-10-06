# tmc2209_probe_20261006: no motion again, and the firmware's driver setup is the likely cause

Issue #169, [PR #260](https://github.com/vertical-cloud-lab/byu-vcl/pull/260), 2026-10-06,
CubXL Pi. Ben worked through the checklist in
[`tmc2209_probe_20261005`](../tmc2209_probe_20261005/README.md#if-the-tmc2209-is-tried-again),
then: *"run tmc2209_probe.py"*.

**The plunger didn't move in either direction, so there was no `HOME`.** Reading the
firmware's TMC2209 library and the datasheet turned up a likely cause, and it isn't the
board. The library switches off the chip's automatic current control, and the firmware never
switches it back on. That leaves the coils with about **0.1 A** when they should get 1 A
([below](#why-it-doesnt-move-the-chip-is-asked-for-about-a-tenth-of-the-current)). This is a
reading of the source, not yet a measurement. [Next](#next-two-ways-to-test-it) gives two ways
to test it.

## What the probes saw

Both scripts are the 10-05 ones, unchanged: the same sha256 on the Pi and in
[`../tmc2209_probe_20261005/`](../tmc2209_probe_20261005/). Plunger only. The GRBL port was
never opened.

| probe | UTC | commanded | seen |
|---|---|---|---|
| [`tmc2209_probe.py`](../tmc2209_probe_20261005/tmc2209_probe.py) ([log](probe.log), [json](tmc2209_probe.json)) | 22:46:14 | UP 3 mm in 0.5 mm chunks at 400 microsteps/s | **no switch**, exit 1, no `HOME` |
| [`tmc2209_probe_down.py`](../tmc2209_probe_20261005/tmc2209_probe_down.py) ([log](probe_down.log), [json](tmc2209_probe_down.json)) | 22:52:01 | DOWN 6 mm in 0.25 mm chunks, switch read after each | **no switch**, so the motor isn't running backwards |

- **The Arduino side is normal.** Every move came back `OK` on schedule (1.015–1.016 s per
  0.5 mm against 0.995 s nominal). The switch read closed (below the top) at the start.
  `EMAG_OFF` → `OK`.
- **`CMD 29` read `comm = 0`.** The 10 kΩ is still on the RX side, so there's no readback.
- **No USB events** during either probe.
- **The plunger should still be ~1 mm below the switch.** On 10-05, with this board plugged
  in, it was sent DOWN 6 mm, a direction the switch doesn't stop. Yet the 10-06 Tic run's
  connect `HOME` took 0.94 s, a 1 mm seek, so that move turned nothing either. The 10-06 run's
  own closing `HOME` left the plunger 1 mm below the switch.

## Ben's readings, steps 1–12

| step | reading | verdict |
|---|---|---|
| 1 look | normal | ✅ |
| 2 VM terminals, ohms | rises as the capacitor charges | ✅ no short |
| 3 coils | 1A–1B and 2A–2B 3.4 Ω, cross pairs very high | ✅ (4.3 / 3.7 Ω on 09-23) |
| 4 diode test | ~1.5 V on each, *"the same both ways around"* | ❓ below |
| 7 VM | 12.4 V | ✅ |
| 8 VDD | 5 V | ✅ |
| 9 VREF | 0.586 V | ✅ `5VOUT` alive; 1.09 A peak on a 6121, *in standalone mode only* (below) |
| 10 DIAG, EN high | 0 V | ✅ |
| 12 DIAG, EN back on A4 | 0 V | ✅ **the go/no-go the 09-26 board failed** |

Steps 5, 6, 11 and 13 weren't reported. Step 6 must have been done, since step 12 moved EN back.

**The diode test isn't the expected result, but it doesn't change the next step.** A healthy
output reads 0.4–0.6 V one way round. 1.5 V both ways round was also what the 09-26 board gave
(wiring doc §22.1). Two cheap explanations come before a fault:

- The probes were on the lifted wire ends. Ben wrote *"on each motor wire"*. The wire ends are
  open circuit. The board's `1A`/`1B`/`2A`/`2B` terminals are what to test.
- The meter shows about 1.5 V for an open circuit in diode mode. Check this with the probes
  touching nothing.

DIAG staying at 0 V once enabled is the stronger evidence. The chip checks every output MOSFET
it switches on, and the old board failed exactly that check.

## Why it doesn't move: the chip is asked for about a tenth of the current

The flashed image is `panda_vcl_p20gen2_tic796_fastmove_20261001.hex`. Its source is
`~/panda_fw_vcl_tic796_fast` on the Pi, built against
[janelia-arduino/TMC2209](https://github.com/janelia-arduino/TMC2209) **10.1.1**.
`setupMotor()` runs on every Arduino reset:

```
stepperDriver.setup(softSerial)  -> TMC2209::initialize():
    setOperationModeToSerial()           GCONF: i_scale_analog 0 (trimmer out of circuit),
                                                pdn_disable 1, mstep_reg_select 1
    setRegistersToDefaults()             PWMCONF = 0xC10D0024: PWM_OFS 36, PWM_GRAD 0,
                                                pwm_autoscale 1, pwm_autograd 1
    clearDriveError(); minimizeMotorCurrent(); disable()
    disableAutomaticCurrentScaling()     PWMCONF.pwm_autoscale = 0   <- never undone
    disableAutomaticGradientAdaptation() PWMCONF.pwm_autograd  = 0
setRunCurrent(20)                        IRUN 6
setHoldCurrent(5)                        IHOLD 1
setMicrostepsPerStep(8)                  MRES 1/8
enableStealthChop()                      en_SpreadCycle 0; TPWMTHRS is 0, so StealthChop at every speed
enableCoolStep()                         inert: TCOOLTHRS is 0
enable()                                 CHOPCONF.toff 3
```

The [datasheet][tmc2209-ds]'s PWMCONF table explains what `pwm_autoscale = 0` does:
*"User defined feed forward PWM amplitude. The current settings IRUN and IHOLD are not enforced
by regulation but scale the PWM amplitude, only! The resulting PWM amplitude (limited to
0…255) is: PWM_OFS * ((CS_ACTUAL+1) / 32) + PWM_GRAD * 256 / TSTEP"*.

So the chip doesn't regulate the current at all. It applies a fixed fraction of VM:

| | CS | PWM amplitude, of 255 | coil current at 12.4 V, 3.4 Ω |
|---|---|---|---|
| moving | IRUN 6 | 36 × 7/32 ≈ 7.9 | **≈ 0.08 A rms (0.11 A peak)** |
| at rest | IHOLD 1 | 36 × 2/32 ≈ 2.3 | **≈ 0.02 A rms (0.03 A peak)** |
| what `RUN_CURRENT_PERCENT 20` was meant to give | IRUN 6 | would need ≈ 74 | 0.72 A rms (1.02 A peak) |
| the Tic, which moves this plunger at every rate | | regulated | 0.99 A limit |

The currents come from the datasheet's own formula for this mode (§6.4, p. 43):
`I_rms = VM × PWM_SCALE / (374 × R_coil)`. Back-EMF in motion lowers them further. A tenth of
the rated current gives about a tenth of the torque. That's too little to drive the plunger past
its seals, and it's silent and cold while it fails.

**It fits everything seen so far:**

| observation | explanation |
|---|---|
| 10-05: the board was hot before the session first opened the port | no UART writes had landed: standalone mode, where StealthChop's automatic scaling *does* regulate, to the trimmer's current |
| 10-05: cool after the port opens, and ever since | the writes landed: ~0.03 A at rest |
| no motion either way on 10-05 or today; no buzz at 100 full steps/s | ~0.1 A while moving |
| DIAG low when enabled | nothing is wrong with the output stage. It just isn't asked for current |
| every move `OK` on schedule | the Arduino side was never at fault |

It applies to every image this TMC2209 path has run. Upstream's `RUN_CURRENT_PERCENT 50`
(CS 15) gives 36 × 16/32 = 18, about 0.23 A, and the 09-15 image's 17 (CS 5) about 0.09 A. The
09-26 board still had a fault of its own (DIAG high once enabled).

**Corrections to the 10-05 record and wiring doc §22.** These all assumed the firmware's
settings drive their nominal current. They don't, in this mode:

- *"the same settings drive 0.72 A rms during a move"*
- the 0.21 A rms hold current
- §22.4–§22.5b: *"the two agree within 7%, so it stops mattering"*

Once the writes land, the trimmer is out of circuit and the current is ~0.1 A, whatever VREF
says.

**Not yet shown.** All of this depends on the UART writes landing. The 10-05 hot-then-cool
sequence suggests they do, but `comm = 0` can't confirm it. If they don't, the chip is in
standalone mode, the trimmer governs, and something else stops the motion. The most likely
culprit is then `STEP` not reaching header pin 4. Test A below separates the two.

[tmc2209-ds]: https://github.com/janelia-arduino/TMC2209/blob/main/datasheet/TMC2209_datasheet_rev1.09.pdf

## Next: two ways to test it

**Free check first.** With the 12 V on and nothing moving for a few minutes, the chip and
pipette should be **cold** if this is right, since the hold current is ~0.03 A. If they're
**warm**, the chip is in standalone mode holding the trimmer's ~0.77 A rms, so the writes
aren't landing and the cause is elsewhere.

**A. No firmware change: take the UART wire off.** Takes about two minutes at the bench.

1. Switch off the 12 V. Take the UART wire (A1) off header pin 9 and leave everything else.
2. Switch on the 12 V. The firmware's writes now go nowhere, and the chip runs in standalone
   mode: StealthChop with automatic scaling, the trimmer's current (VREF 0.586 V ≈ 0.77 A rms
   on a 6121), and 1/8 step from MS1/MS2, which matches 796 steps/mm. After a minute, it and
   the pipette should be warm.
3. Comment `@claude run tmc2209_probe.py`.

| result | meaning |
|---|---|
| direction proven, `HOME` ok | the firmware setup was the fault. Standalone mode can stay: it's the Tic's arrangement, full current at rest, set by the trimmer. Or put the wire back after fix B |
| no motion, board warm | current flows but `STEP` doesn't arrive: beep A2 → pin 4 |
| no motion, board cold | no coil current even in standalone mode: back to the board |

**B. Fix the firmware.** No hands needed, but it needs Ben's go-ahead, because the same Arduino
runs the capper. In `src/Pipette.cpp`, `setupMotor()`:

```diff
-    stepperDriver.enableStealthChop();
+    stepperDriver.disableStealthChop();   // [VCL] SpreadCycle: IRUN/IHOLD regulated
```

SpreadCycle regulates the coil current every chopper cycle against the sense resistors, like
the Tic. IRUN 6 then means 0.72 A rms (1.02 A peak) and IHOLD 1 means 0.21 A rms, on a 6121's
0.05 Ω. It also tolerates the firmware's step changes in speed: `stepMotor()` starts at up to
~8,700 microsteps/s with no ramp, and StealthChop's automatic tuning expects ramped moves. Staying in
StealthChop and calling `enableAutomaticCurrentScaling()` and
`enableAutomaticGradientAdaptation()` is quieter, but needs tuning moves. With the Tic in
circuit the writes reach nothing, so B doesn't change the Tic path. Build it, flash it with
`avrdude -U flash:v` before and after, as in the [firmware README](../../firmware/README.md),
then run `tmc2209_probe.py`.

Whichever way it moves, run the probe before any protocol, and use `cubxl_run.py --no-tic`.

## The USB over-current at 16:35 lab time

The Pi's kernel log had nothing to do with the probes, but it's worth knowing about:

| UTC | |
|---|---|
| 22:15:07 | the Tic unplugged (the swap) |
| 22:26:07, 22:33:42, 22:34:33, 22:34:57 | the GRBL board's CH340 drops off USB and comes back, with no over-current |
| **22:35:04–09** | **over-current on every USB port at once**, ~96 events. The Arduino and the CH340 both drop and come back |
| **22:35:31–32** | again, 23 events, and both drop and come back again |

Nothing since: `throttled=0x0`, EXT5V 5.13 V. The timing matches the bench work. The likely
cause is the Arduino's `5V` header pin, which sits between `3.3V` and `GND`. A jumper or probe
that slips there during step 6 or step 12 shorts the USB 5 V, and the Pi switches off every
port. A run on 09-30 was stopped the same way. It's harmless if brief, but every drop resets the
Arduino (dropping the capper's magnet) and GRBL (so it needs homing).

## State left

- **Plunger:** not homed, and most likely still ~1 mm below the switch, since nothing turned.
- **Electromagnet:** off, `EMAG_OFF` → `OK` after each probe.
- **Gantry:** not touched, and its port wasn't opened. GRBL was reset by the 16:35 USB drops,
  so it needs homing before a run, as always.
- **`~/cubxl_runs/HOLD`:** written for this session at 22:46Z and removed at 22:53Z.
- **On the Pi:** `~/cubxl_runs/tmc2209_probe_20261006/` holds these logs and copies of the
  two scripts.
