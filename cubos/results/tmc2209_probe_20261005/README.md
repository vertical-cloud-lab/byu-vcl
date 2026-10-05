# tmc2209_probe_20261005: the TMC2209 doesn't drive the plunger, so `pipette_test` was not run

Issue #169, 2026-10-05, CubXL Pi. Ben: *"run the pipette test protocol. I switched back to
the TMC2209 driver board to see if it would work."*

**It doesn't work, and `pipette_test` was not run.** Before CubOS homes the plunger, I
checked with the limit switch that the TMC2209 moves it and in which direction. With the
board plugged in, 9 mm of commanded travel in both directions never reached the switch.
A 30 s buzz at 100 full steps/s was then sent while Ben stood at the pipette, and he
reported *"nothing is happening with the pipette. No buzzing."* The Arduino sent every
step on schedule, so the fault is downstream of its `STEP`/`DIR` pins. Ben is putting the
pipette back on the Tic T500. The gantry never moved.

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
which is a 1 mm seek plus the back-off. The switch read closed at the start of every
probe today, as it should.

## What the probes saw

400 microsteps/s unless stated. The millimetres are firmware millimetres
(796 microsteps/mm). A "switch read" sends 2 steps UP. The firmware refuses that while D9
reads open, whichever way the motor actually turns.

**Round 1, 22:01–22:05Z. The driver board was unplugged.** Ben had unplugged it because it
was heating up (his 22:10Z comment). So this round only shows that the Arduino side works.

| probe | UTC | commanded | seen |
|---|---|---|---|
| [`tmc2209_probe.py`](tmc2209_probe.py) ([log](probe.log)) | 22:01:55 | UP 3 mm, 0.5 mm chunks | no switch |
| [`tmc2209_probe_down.py`](tmc2209_probe_down.py) ([log](probe_down.log)) | 22:03:44 | DOWN 6 mm, 0.25 mm chunks, switch read after each | no switch |
| [`tmc2209_probe_up12.py`](tmc2209_probe_up12.py) ([log](probe_up12.log)) | 22:05:06 | UP 12 mm, 0.5 mm chunks | no switch |

**Round 2, 22:11–22:16Z. The board was plugged back in, and Ben reported it no longer
heating.**

| probe | UTC | commanded | if the motor turned | seen |
|---|---|---|---|---|
| `tmc2209_probe.py` ([log](probe2.log)) | 22:11:40 | UP 3 mm | the switch opens after ~1 mm | **no switch** |
| `tmc2209_probe_down.py` ([log](probe2_down.log)) | 22:12:00 | DOWN 6 mm, switch read every 0.25 mm | reversed: opens after ~4 mm | **no switch** |
| [`tmc2209_buzz.py`](tmc2209_buzz.py) ([log](buzz.log)) | 22:15:30–22:16:00 | 30 × (UP 0.5 mm, DOWN 0.5 mm) at 800/s = 100 full steps/s | a hum you can feel (Ben felt the Tic at these rates on 09-29) | **Ben: "No buzzing"** |

- **The Arduino side is fine.** Every move came back `OK` on schedule (1.015 s against
  0.995 s nominal per 0.5 mm), and the limit-switch input read normally.
- **`CMD 29` read `comm = 0` in both rounds.** There was no UART reply, so the driver's own
  fault flags (short, open load, over-temperature) couldn't be read.
- **The buzz settles it.** The switch probes alone leave one case open: a plunger moved
  more than ~3 mm down by hand. A person at the pipette closes it. 100 full steps/s
  for 30 s produced nothing Ben could feel or hear, so the board isn't driving the
  motor.
- **Heat.** Ben saw the board heat up while it was connected before round 1, then stay cool
  once re-plugged. Neither state turned the motor. Heat without coil drive fits the
  damaged output stage described in §22 of the wiring doc, but that is an inference from
  his report, not a measurement.

## Why the protocol was not run

With a plunger that doesn't move, CubOS's `HOME` on connect runs out its 50,000 steps
(~26 s) and fails. The patched connect carries on regardless. The run would pick up a tip,
fail to eject it, and finish with the tip stuck. That adds nothing about the driver and
leaves a tip to pull off by hand. Until the switch has proven the direction, a blind `HOME`
is also the one command that can drive a reversed plunger into the ejector.

Everything else was ready. A checks-only pass of `cubxl_run.py` at 22:08Z
(`~/cubxl_runs/checks_20261005/` on the Pi) used Ben's 10-02 files
(`cub_xl_ben_3_instrument.yaml`, `ben_2vials_tiprack.yaml`) and found:

- GRBL matches the gantry file: travel 364 / 281 / 125, `G54` = −travel, `$20=1`, `$21=1`.
- The Arduino answers, the cap sensor reads 0, and the magnet is off.
- The validate, mock and both collision-shadow gates pass.

Nothing moved. Opening the GRBL port resets the controller into `Alarm`, as every run does,
and the protocol's step 0 `home` clears it.

## If the TMC2209 is tried again

From [`opentrons-pipette-wiring.md`](../../docs/opentrons-pipette-wiring.md) and the
[Tic doc](../../docs/tic-t500-pipette-setup.md), most likely first:

1. **Is it the Adafruit 6121 condemned on 2026-09-26?** Its `DIAG` stayed high through a
   power-on reset and an `ENN` reset, with a clean load (§22). With VM on, `DIAG` (header
   pin 7) near VDD means the fault is still there.
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

**Quick test, no meter needed.** With VM and the Arduino both powered, a working TMC2209
holds the motor, so it resists being turned by hand.

**Order of operations.** Run [`tmc2209_probe.py`](tmc2209_probe.py) first. Once the
switch proves the direction, it also runs a rate ladder (1,000 / 2,500 / 10,000 steps/s,
the last being the rate `MOVE_TO` and `ASPIRATE` use) and a `HOME`. After that, run
`cubxl_run.py --no-tic` with the 10-02 files. Without `--no-tic`, the runner's Tic check
refuses to start.

```bash
cd ~/cubxl_runs/tmc2209_probe_20261005 && \
  PYTHONPATH=$HOME/CubOS/packages/core/src ~/CubOS/.venv/bin/python tmc2209_probe.py tmc2209_probe.json
```

## State left

- **Plunger:** not homed. Nothing turned it today, so it should still be where 10-02 left
  it, ~1 mm below the switch.
- **Electromagnet:** off, `EMAG_OFF` → `OK` after every probe.
- **Gantry:** not moved. It hasn't been homed since the 15:54 lab-time boot. GRBL is in
  `Alarm` from the checks-only port open.
- **Driver:** Ben is putting the pipette back on the Tic T500. The runner's Tic path,
  without `--no-tic`, re-checks the Tic's settings and energizes it before a run, as on 10-02.
- **Pi:** dropped off the tailnet at ~22:17Z, presumably powered down for the swap, and
  was still offline at 22:36Z.
- **⚠️ `~/cubxl_runs/HOLD` is still on the Pi.** It held the CubXL for this session
  (Actions run 37379090191), and the Pi went offline before the session could remove
  it. That run has ended, so delete the file (`rm ~/cubxl_runs/HOLD`). Until then,
  `cubxl_run.py` refuses to start and prints the file's text.
- The round-2 and buzz logs here were copied from the session's terminal, since the Pi was
  offline at write-up. The matching `*.json` row files, and `runner.log` / `gate_*.log` for
  the checks-only pass, are on the Pi under `~/cubxl_runs/`.
