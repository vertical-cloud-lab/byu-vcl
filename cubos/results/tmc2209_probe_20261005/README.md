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
His *"I'm unplugging the 12V"* comment came at 22:02:27Z, 25 s after the first probe ended,
so that probe may have run with the board still powered. It settles nothing either way.

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
- **Heat.** Ben saw the board heat up before round 1, then stay cool once re-plugged. The
  pipette was warm too, so the hot board was driving coil current. See
  [Why it got hot](#why-it-got-hot-2026-10-06). *(Corrected 2026-10-06. This bullet first
  read the heat as heat without coil drive, from a damaged output stage. The warm pipette
  rules that out for the hot period.)*

## Why it got hot (2026-10-06)

Ben's follow-up on [PR #260](https://github.com/vertical-cloud-lab/byu-vcl/pull/260): why did the
board get so hot and then stop, did that break something, and did this session stop it? The
times come from his comments on #169, the logs here, and the file times on the Pi.

| UTC | |
|---|---|
| ~21:54 | The Pi boots (`Pi up 14 minutes` at 22:08:24). The Arduino is powered from its USB |
| 21:57:26 | Ben: the board is *"really warm (even with a heat sink on)"*, and the pipette is warm |
| 22:01:52 | The session's first contact with the Arduino: `tmc2209_probe.py` opens the port |
| 22:02:27 | Ben: *"I'm unplugging the 12V from the board"* |
| 22:08:28 | The checks-only pass opens the port |
| 22:10:30 | Ben: plugged in again and *"not heating up"* |
| 22:11:36–22:16:00 | Round 2 and the buzz: no motion |

**The session didn't cause the heat, and didn't set out to stop it.** The board was hot four
minutes before the session first opened the Arduino's port. After that it sent the Arduino only
`STATUS` (14), a cap-sensor read, `CMD 29` (a read), `CMD 16` moves and `EMAG_OFF` (6). None of
them sets the driver's current or switches it off. Pulling the 12 V at 22:02 is what stopped the
heat.

**The session may have kept it from coming back, though.** Each port open resets the Arduino, and
`setupPipette()` then re-sends the TMC2209's settings over UART. Those take the trimmer out of
circuit and set run current CS 6 (0.72 A rms on a 6121) and hold current CS 1 (0.21 A rms). That
happened seven times: 22:01:52, 22:03:41, 22:05:02, 22:08:28, 22:11:36, 22:11:56 and 22:15:26.
If the UART wire was connected and the 12 V was back on for one of them, the board idled at
0.21 A rms from then on and stayed cool. That can't explain the missing motion, since the same
settings drive 0.72 A rms during a move.

*Corrected 2026-10-06: they don't, and it can.* The library switches off StealthChop's automatic
current scaling, and the firmware never switches it back on. So CS 6 and CS 1 scale a fixed PWM
amplitude, about 0.1 A while moving and 0.03 A at rest, rather than setting a regulated current.
Cool, no motion and no buzz all follow from that one cause. See
[`tmc2209_probe_20261006`](../tmc2209_probe_20261006/README.md) and wiring doc §24.

**Why it got hot: it held the motor at a current nobody had set.**

- The driver is on whenever it has 12 V. The firmware drives A4 (`EN`) low, and the 6121 pulls
  `EN` down with 20 kΩ as well, so the coils carry current with nothing moving. The warm pipette
  shows they did.
- The firmware's settings reach the chip only when the Arduino resets with the 12 V already up.
  Before 22:01:52 the last reset was at ~21:54 or earlier. If the 12 V came on after it, the chip
  was in standalone mode, and the trimmer set the current: up to ~1.5 A rms (2.2 A peak) at full
  clockwise on a 6121 (wiring doc §22.5a), against the P20's 1.0 A peak.
- In standalone mode it also held that full current at rest. The chip drops to its hold current
  only while `PDN_UART` is low ([datasheet][tmc2209-ds] §3.4), and the UART line from A1 idles
  high. So the hold current was the run current.

Nobody has measured where the new board's trimmer sits, so the current isn't known. For
scale, the datasheet's typical dissipation is 1.4 W at 1.0 A rms and 2.8 W at 1.4 A rms
(datasheet §20.3). Near the top of that range a small breakout gets too hot to touch, heat
sink or not, and the motor takes up to about five times the Tic's 4 W.

**Why it then stayed cool:** either the settings landed (above) and something else stops the
motion, or no coil current has flowed since the re-plug. The second covers "cool", "no motion"
and "no buzz" with one cause: no 12 V at the VM terminals, no VDD, or a driver that no longer
drives.

**Whether it broke:** unknown until it is measured (the checklist below). Heat alone is the
less likely culprit. The chip switches its outputs off at 143 °C and back on below 120 °C
(datasheet §15.1). At the trimmer's top end (~1.5 A rms) it runs just past its 1.4 A rms
continuous rating (datasheet §20.1), the kind of slow overload that cutoff is for. More likely
ways to break it are how the 12 V went back in (see *Every step* below) and a motor wire moving
while powered. The motor came through: on 2026-10-06 the same pipette ran `pipette_test` 12/12
on the Tic with no lost steps.

[tmc2209-ds]: https://github.com/janelia-arduino/TMC2209/blob/main/datasheet/TMC2209_datasheet_rev1.09.pdf

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

*Rewritten 2026-10-06 as a troubleshooting checklist, at Ben's request.* The first version
asked whether this was the 6121 condemned on 2026-09-26. Ben said at 22:06Z that it is a new
board. It also said the UART wire only mattered for readback, which is wrong: it carries the
firmware's current settings.

*2026-10-06: Ben's run through steps 1–12 and the probe's result are in
[`tmc2209_probe_20261006`](../tmc2209_probe_20261006/README.md).* The board passed. Step 13's
"0.21 A rms hold current" below is wrong for the reason given there. Once the firmware's writes
land, the chip holds ~0.03 A and should feel cold. The last two rows of the table now lead to
that record's tests A and B.

Section numbers are from [`opentrons-pipette-wiring.md`](../../docs/opentrons-pipette-wiring.md).
The figures assume an Adafruit 6121 like the 09-26 board: 0.05 Ω sense resistors, VREF at most
~1.16 V. Header pins (§10.3): 1 VDD, 2 GND, 3 DIR, 4 STEP, 7 DIAG, 9 UART, 10 EN. The pipette
works on the Tic, so steps 1–13 can also be done on the bench with a spare stepper, which
leaves the CubXL alone.

**Every step:** switch the 12 V on and off at the wall (or the supply's own switch), with its
DC lead already connected to the board. The datasheet wants VS to rise slower than 1 V/µs:
*"failure to do so could result in destructive currents via the charge pump capacitor"*
([datasheet][tmc2209-ds] §3.1). Pushing a live lead in can be far faster. Touch motor wires
only with the 12 V off.

**Power off**

1. Look the board over: discolouration or a crack near the chip, a burnt smell, and the heat
   sink on the chip only.
2. Resistance across the VM terminals, red probe on `+`, black on `−`. It should climb as the
   22 µF capacitor charges. Steady under ~10 Ω means a shorted chip or capacitor: replace the
   board.
3. Coils at the board's terminals: 1A–1B and 2A–2B about 4 Ω (4.3 / 3.7 Ω on 09-23). 1A–2A and
   1B–2B open.
4. Lift the four motor wires. Diode-test each of 1A, 1B, 2A and 2B against GND and against VM+,
   both ways round (§22.7): about 0.4–0.6 V one way, alike on all four. ~0.00 V is a shorted
   output, and open is a dead one. Reconnect the wires.
5. Beep out the wiring from the Arduino to the header: 5V–1, GND–2, A3–3 (DIR), A2–4 (STEP),
   A1–9 (UART, with the 10 kΩ to A0), A4–10 (EN), and the 12 V supply to the VM block. The swaps
   to the Tic and back are where a wire is most likely to have gone astray.
6. Take EN (pin 10) off A4 and jumper it to the Arduino's 5V. Then the chip passes no coil
   current, whatever its trimmer says (§22.8 step 4).

**12 V on, EN high.** Black probe on GND.

7. VM at the screw heads: 11.4–12.6 V. 0 V means it isn't connected, and −12 V means it is
   reversed.
8. VDD (pin 1): about 5 V, never 12 V. Without it the chip is held in reset (datasheet
   §20.2). The green LED also needs VDD: it lights while DIR is low.
9. VREF at the trimmer wiper (§19.4). Anything above 0 V means the chip's internal 5 V regulator
   is alive. About 0 V with VM present means a dead chip: replace the board. Set it to
   0.55–0.59 V, about 1.0 A peak, the same current the firmware asks for (§22.4).
10. DIAG (pin 7): about 0 V.
11. After a minute, the chip should still be at room temperature. If it warms with EN high, stop.

**Enable it**

12. Move EN back to A4. DIAG should stay near 0 V. If it jumps to ~5 V, switch off and stop: the
    output stage is failing its own short check, as the 09-26 board did (§22.2).
13. With nothing commanded, the chip and the pipette get warm, not hot. At VREF 0.55 V it holds
    ~0.72 A rms at rest, about the Tic's 4 W in the motor, until an Arduino reset lands the
    firmware's 0.21 A rms hold current. A gently pushed plunger should resist (§22.7).
14. Run [`tmc2209_probe.py`](tmc2209_probe.py) (below). Its port open is that reset. It proves
    the direction with the limit switch before any `HOME`.
15. Optional: move the 10 kΩ to the TX side (§22.8 step 2). Then `CMD 29` reads the chip's own
    flags (short, open load, over-temperature) instead of `comm = 0`.

| finding | meaning |
|---|---|
| VM wrong (7) | fix the 12 V wiring and start again |
| VDD missing (8) | connect the Arduino's 5V to pin 1 and start again |
| VREF ~0 V with VM present (9) | dead chip: replace the board |
| DIAG high once enabled (12) | damaged output stage: replace the board |
| holds at 13, but the probe sees no motion | take the UART wire off pin 9 and run the probe again. If it moves now, the UART writes leave the driver off (§4). If not, STEP isn't reaching pin 4 |
| the probe proves the direction | the 10-05 fault was the wiring or the 12 V connection |

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
  *(2026-10-06: done. `pipette_test` ran 12/12 on the Tic.)*
- **Pi:** dropped off the tailnet at ~22:17Z, presumably powered down for the swap, and
  was still offline at 22:36Z.
- **`~/cubxl_runs/HOLD` was left on the Pi.** It held the CubXL for this session
  (Actions run 37379090191), and the Pi went offline before the session could remove
  it. *(2026-10-06: the next run session replaced it with its own and then removed that.
  There was no `HOLD` on the Pi at 21:53Z.)*
- The round-2 and buzz logs here were copied from the session's terminal, since the Pi was
  offline at write-up. The matching `*.json` row files, and `runner.log` / `gate_*.log` for
  the checks-only pass, are on the Pi under `~/cubxl_runs/`.
