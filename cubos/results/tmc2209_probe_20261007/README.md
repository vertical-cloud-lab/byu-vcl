# tmc2209_probe_20261007: with the UART wire off, the TMC2209 moves the plunger at every rate

Issue #169, [PR #260](https://github.com/vertical-cloud-lab/byu-vcl/pull/260), 2026-10-07,
CubXL Pi. Ben did the free check and test A from
[`tmc2209_probe_20261006`](../tmc2209_probe_20261006/README.md#next-two-ways-to-test-it):
*"The board and pipette were cold. I unplugged UART from pin 9. The board is getting warm."*,
then *"run tmc2209_probe.py"*.

**It moved, at every rate the firmware uses, and `HOME` worked.** `tmc2209_probe.py` exited
0. UP opened the limit switch after ~1.65 mm, every rung of the rate ladder reopened it after
its 2 mm back-off, and the firmware `HOME` returned `OK`. The same board was cold and didn't
move with the UART wire on, and is warm and moves with it off. So the board is fine, and the
firmware's UART setup was what stopped it, as 10-06 predicted.

## What the probe saw

[`tmc2209_probe.py`](../tmc2209_probe_20261005/tmc2209_probe.py), unchanged: the same sha256
(`58cb6aab…`) on the Pi as in the repo. [Log](probe.log), [rows](tmc2209_probe.json).
18:18:13–18:18:41Z. Plunger only. The GRBL port was never opened.

| step | sent | seen |
|---|---|---|
| connect | port open, which resets the Arduino | connected in 3.77 s, `STATUS` `homed 0` |
| `CMD 29` | driver status | `comm = 0`, as expected with nothing on pin 9 |
| switch read | 2 steps UP | closed (below the top) |
| UP search | 0.5 mm moves at 400 microsteps/s | moves 1–3 completed. **Move 4 opened the switch after ~0.15 mm**, ~1.65 mm in all |
| ladder @ 1000 | DOWN 2 mm at 400/s, then UP 4 mm at 1,000/s | switch reopened after ~2.05 mm |
| ladder @ 2500 | the same at 2,500/s | ~2.12 mm |
| ladder @ 10000 | the same at 10,000/s, ~8,700/s in practice: the rate `MOVE_TO` and `ASPIRATE` use | ~2.13 mm |
| `HOME` | DOWN 2 mm, then cmd 10 | `OK:{"msg":"Pipette homed"}` in 1.348 s. `homed 1`, `pos 0.00`, switch closed |
| end | `CMD 29`, `EMAG_OFF` | `comm = 0`. `OK` |

- **DIR LOW is up,** as on the Tic. The firmware's blind `HOME` seek is safe with this board
  as wired.
- **No lost steps at any rate.** Each rung backs off 1,592 microsteps and times how long it
  takes to reopen the switch. A start the motor didn't follow would show up as extra
  distance. The small rise with rate, 2.05 to 2.13 mm, comes from the timing estimate, not
  the motor. The Tic showed the same rise on 09-29
  ([`pipette_switch_search_20260929`](../pipette_switch_search_20260929/README.md), same
  method and the same raw step counts). At 2,500/s the trip took 0.774 s here and 0.770 s on
  the Tic. `HOME` from 2 mm below took 1.348 s here and 1.356 s on the Tic.
- **It started 1.65 mm below the switch, not the ~1 mm the 10-06 record expected.** Something
  moved it ~0.65 mm down after the Tic's last `HOME` on 10-06: a hand on the plunger, or the
  10-06 probes turning it part of the way. `HOME` has re-zeroed it.

## What it settles

| question | answer |
|---|---|
| did the 10-05 heat damage the board? | no. It drives the motor at every rate |
| do `STEP` and `DIR` reach it? | yes |
| which way is up? | DIR LOW, as on the Tic |
| why no motion on 10-05 and 10-06? | the firmware's UART writes. They land, and leave the chip too weak to move: cold with the wire on, warm and moving with it off |

**What it doesn't settle.**

- **Which written setting starves the motor.** That's still read from the library source
  ([10-06](../tmc2209_probe_20261006/README.md#why-it-doesnt-move-the-chip-is-asked-for-about-a-tenth-of-the-current)),
  not read back from the chip. Nothing can be read back while the 10 kΩ is on the RX side,
  and now the wire is off as well.
- **The step size.** Every figure here is a step count. 1/8 step is what `MS1`/`MS2` give with
  nothing on them (internal pull-downs, wiring doc §10.3), and it matches 796 steps/mm, but
  nothing here measures it.

## Why it's warm now

With the wire off, the firmware's writes go nowhere, and the chip runs on its own pins
(standalone mode):

- **Current from the trimmer.** VREF 0.586 V is ≈ 0.77 A rms (1.09 A peak) on a 6121's 0.05 Ω
  sense resistors. Ben hasn't confirmed the new board is a 6121.
- **StealthChop with automatic current regulation,** if the board leaves `SPREAD` on its
  internal pull-down.
- **1/8 step** from `MS1`/`MS2`.

It keeps current in the coils at rest. That's the Tic's arrangement: on 09-29 the Tic held
990 mA, about 4 W into the pipette body, with nothing running. So warm is what test A
predicted. There's no software off switch in this mode, so the 12 V switch is the way to stop
it holding when the CubXL is idle.

**Pin 9 now floats.** The [datasheet][tmc2209-ds]'s pin table gives `PDN_UART` no internal pull
(`DIO`, where `MS1`, `MS2`, `SPREAD` and `DIR` are `DI (pd)`). The 6121 notes in wiring doc
§10.3 list no board pull either. That pin decides the current at rest: low cuts it to `IHOLD`,
53% of the run current by the OTP default; high keeps the full run current. Floating, it's
whichever way the pin drifts. That's harmless, but if the wire stays off for good, give pin 9 a
level through 1–10 kΩ: to pin 2 (GND) for the cooler reduced hold, or to pin 1 (VDD) for the
Tic's full hold. The resistor keeps a stray A1 wire from shorting the Arduino pin. Rerun the
probe after.

If the pipette gets hotter than it did on the Tic, VREF 0.54 V gives 1.0 A peak, the P20's
rating. 0.586 V is 9% over it. Rerun the probe after that too.

[tmc2209-ds]: https://github.com/janelia-arduino/TMC2209/blob/main/datasheet/TMC2209_datasheet_rev1.09.pdf

## Next

1. **`pipette_test` with the wire off.** Use `cubxl_run.py --no-tic` with the 10-02 files, per
   the [10-05 order of operations](../tmc2209_probe_20261005/README.md#if-the-tmc2209-is-tried-again).
   It moves the gantry, so it waits for Ben's go-ahead.
2. **Then pick how to keep it:**
   - **Wire off for good.** This is what ran today, and it's the Tic's arrangement. Tie pin 9
     to a level as above.
   - **Fix B, wire back on.** `disableStealthChop()` in `setupMotor()`
     ([10-06](../tmc2209_probe_20261006/README.md#next-two-ways-to-test-it)). The firmware then
     sets a regulated 0.72 A rms moving and 0.21 A rms at rest, so it idles cool. It needs a
     flash of the Arduino that also runs the capper, and the probe again.

## State left

- **Plunger:** homed, 796 microsteps (1 mm) below the switch, `pos 0.00`. The next port open
  resets the Arduino and clears `homed`. CubOS re-homes on connect.
- **Electromagnet:** off, `EMAG_OFF` → `OK`.
- **Gantry:** not touched, and its port wasn't opened.
- **Driver:** TMC2209 in standalone mode, UART wire off pin 9, VREF 0.586 V, 12 V on, holding
  current at rest.
- **`~/cubxl_runs/HOLD`:** written for this session at 18:18:07Z and removed at 18:18:54Z.
- **Pi:** up 21 h, `throttled=0x0`, EXT5V 5.13 V. No kernel log entries since 10-06 22:50Z, so
  no USB drops during Ben's rewiring.
- **On the Pi:** `~/cubxl_runs/tmc2209_probe_20261007/` holds the log, the JSON and copies of
  both scripts.

To rerun:

```bash
cd ~/cubxl_runs/tmc2209_probe_20261007 && \
  PYTHONPATH=$HOME/CubOS/packages/core/src ~/CubOS/.venv/bin/python tmc2209_probe.py tmc2209_probe.json
```
