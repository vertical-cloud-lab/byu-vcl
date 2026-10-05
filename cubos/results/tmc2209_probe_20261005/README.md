# tmc2209_probe_20261005: the TMC2209 doesn't turn the plunger, so `pipette_test` was not run

Issue #169, 2026-10-05, CubXL Pi. Ben: *"run the pipette test protocol. I switched back to
the TMC2209 driver board to see if it would work."*

**`pipette_test` was not run.** First I checked, with the limit switch, that the
TMC2209 moves the plunger and in which direction. That had to come before CubOS homes the
plunger. Three probes commanded 21 mm of plunger travel in both directions, and none of it
reached the switch. The Arduino sent every step on schedule, so the fault is downstream of
its `STEP`/`DIR` pins. The gantry port was never opened.

## Why probe before the protocol

- **The firmware is unchanged:** `panda_vcl_p20gen2_tic796_fastmove_20261001.hex`,
  796 steps/mm at 1/8 step. That suits a TMC2209 too. Its setup call writes 1/8 over
  UART, and if that write never lands, the MS1/MS2 straps default to 1/8 anyway
  ([wiring doc §10.3](../../docs/opentrons-pipette-wiring.md)).
- **Only the Tic's direction has ever been proven** ([2026-09-29](../pipette_switch_search_20260929/README.md)).
  The switch stops UP moves only. The firmware's `HOME` seeks UP blind for up to
  50,000 steps (~63 mm). On a reversed motor, CubOS's connect-time `HOME` would drive the
  plunger *down* into the tip ejector.

## Where the plunger started

The 2026-10-02 run ended with a `HOME` (12.698 s, `OK`), which leaves the plunger
796 steps (~1 mm) below the switch
([`pipette_test_20261002c`](https://github.com/vertical-cloud-lab/byu-vcl/blob/d921c64/cubos/results/pipette_test_20261002c/SUMMARY.md)).
A de-energized plunger stays put. The 09-30 `HOME` from the 09-29 resting place took 0.94 s,
which is a 1 mm seek plus the back-off. The switch read closed at the start of today's
first probe, as it should.

## What the probes saw

400 microsteps/s throughout. The millimetres are firmware millimetres (796 microsteps/mm).
A "switch read" sends 2 steps UP. The firmware refuses that while D9 reads open, whichever
way the motor actually turns.

| probe | UTC | commanded | if the motor turned | seen |
|---|---|---|---|---|
| [`tmc2209_probe.py`](tmc2209_probe.py) ([log](probe.log)) | 22:01:55–22:02:02 | UP 3 mm, 0.5 mm chunks | the switch opens after ~1 mm | **no switch** |
| [`tmc2209_probe_down.py`](tmc2209_probe_down.py) ([log](probe_down.log)) | 22:03:44–22:03:58 | DOWN 6 mm, 0.25 mm chunks, switch read after each | reversed: opens after ~4 mm | **no switch** |
| [`tmc2209_probe_up12.py`](tmc2209_probe_up12.py) ([log](probe_up12.log)) | 22:05:06–22:05:31 | UP 12 mm, 0.5 mm chunks | opens within ~2 mm even at 1/64 step | **no switch** |

- **The Arduino side is fine.** Every move came back `OK` in 1.015 s against 0.995 s
  nominal per 0.5 mm, and the limit-switch input read normally.
- **`CMD 29` read `comm = 0`**: no UART reply, so the driver's own fault flags (short,
  open load, over-temperature) couldn't be read.
- **Reading.** Starting from the 10-02 position:
  - a motor turning the right way at 1/8 opens the switch within the first probe;
  - a reversed one opens it in the second;
  - any microstep setting the straps allow (1/8 to 1/64) opens it in the third.

  None did. The only case left open is that the plunger was pushed more than ~3 mm down
  by hand during the swap. That is why no longer search was tried. If the motor is
  reversed *and* the plunger is low, a long search drives it toward the ejector.

## Why the protocol was not run

With a plunger that doesn't move, CubOS's `HOME` on connect runs out its 50,000 steps
(~26 s) and fails. The patched connect carries on regardless. The run would pick up a tip,
fail to eject it, and finish with the tip stuck. That adds nothing about the driver and
leaves a tip to pull off by hand. And if the motor does turn after all, with only the
starting-position assumption wrong, a blind `HOME` is the one command that can drive the
plunger into the ejector.

## What to check on the TMC2209

From [`opentrons-pipette-wiring.md`](../../docs/opentrons-pipette-wiring.md) and the
[Tic doc](../../docs/tic-t500-pipette-setup.md), most likely first:

1. **Is it the Adafruit 6121 condemned on 2026-09-26?** Its `DIAG` stayed high through a
   power-on reset and an `ENN` reset, with a clean load (§22). Today's result is what
   that predicts: the chip re-detects a "short" at every enable and keeps its outputs off.
   With VM on, `DIAG` (header pin 7) near VDD means the fault is still there.
2. **VM: 12 V at the driver's VM/GND screw terminal.** Until today that supply fed the
   Tic's `VIN`. Without VM there is no `5VOUT`, so VREF is zero, coil current is zero,
   and the chip can't answer UART (§10.3).
3. **VDD (header pin 1) to the Arduino's 5V, GND (pin 2) to the Arduino's GND.** The Tic
   wiring left the Arduino's 5V unconnected on purpose, and the TMC2209's logic I/O needs it.
4. **`STEP` (pin 4) to A2, `DIR` (pin 3) to A3.** `EN` (pin 10) to A4 is optional,
   since the board pulls `EN` low.
5. **Coils:** 1A+1B on one winding, 2A+2B on the other. Connect the motor only with
   VM off.
6. **`UART` (pin 9) to A1, with the 10 kΩ bridge to A0 on the TX side.** This only
   affects `CMD 29` readback.

A quick test needs no meter. With VM and the Arduino both powered, a working TMC2209 holds
the plunger, and the motor resists being turned. The 6121 never did.

## State left

- **Plunger:** not homed. If the motor didn't turn, it is where 10-02 left it, ~1 mm below
  the switch. The probes netted 9 mm UP commanded (3 up, 6 down, 12 up).
- **Electromagnet:** off, `EMAG_OFF` → `OK` after each probe.
- **Gantry:** port never opened. It hasn't been homed since this boot (15:54 lab time).
- **Tic:** not on USB.
- `~/cubxl_runs/HOLD` holds the CubXL for this session (Actions run 37379090191) and is removed when it ends.

## To retry after a fix

Run [`tmc2209_probe.py`](tmc2209_probe.py) first. Once the direction is proven, it also
runs a rate ladder (1,000 / 2,500 / 10,000 steps/s, the last being the rate `MOVE_TO` and
`ASPIRATE` use) and a `HOME`. Then run `cubxl_run.py --no-tic` with the 10-02 gantry and
deck files. Without `--no-tic`, the runner's Tic check refuses to start.

```bash
cd ~/cubxl_runs/tmc2209_probe_20261005 && \
  PYTHONPATH=$HOME/CubOS/packages/core/src ~/CubOS/.venv/bin/python tmc2209_probe.py tmc2209_probe.json
```
