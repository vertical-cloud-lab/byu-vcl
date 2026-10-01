# Tic T500: first plunger moves, 2026-09-29

Bring-up steps 3 and 5 of [`tic-t500-pipette-setup.md`](../../docs/tic-t500-pipette-setup.md),
at Ben's request once the Tic was wired in STEP/DIR mode (Figure 1) and on 12 V.
He had tried the moves from an Arduino IDE serial monitor and seen nothing.

Plunger only. The gantry port (`/dev/ttyUSB0`) was never opened. All times are
lab local (UTC−6).

**Result: everything the Pi can see works.** The Arduino emits the steps, the
Tic energizes the motor with no errors, the coils carry the current the Tic sets,
and the Tic can step the motor on its own. None of that proves the shaft turned:
there is no encoder, and the pipette was out of the camera's view during the
moves. **Whether the plunger moved in test B, test C, both or neither is Ben's
observation, and it decides the next step (see the end).**

## Starting state (17:47)

[`tic_status_before.txt`](tic_status_before.txt): energized, operation state
Normal, **no errors stopping the motor**, 1/8 step, 990 mA, VIN 10.05 V. The Tic
had been powered since about 17:36. Its USB joined the Pi at 17:40:57 and the
Arduino's at 17:42:12, which fits the serial-monitor attempt having been made
from another computer. Nothing else had either serial port open.

## B. Through the Arduino (17:52)

PANDA `CMD 16` (raw steps, `direction,steps,rate`), via `PawduinoLink` exactly as
CubOS sends it. 796 microsteps = 1 mm at 1/8 step. Log:
[`b_arduino_moves.log`](b_arduino_moves.log).

| time | command | reply | dt | commanded |
| --- | --- | --- | --- | --- |
| 17:52:04 | `16,1,796,400` (direction 1) | `OK` Moved relative | 2.022 s | 1.99 s |
| 17:52:08 | `16,0,796,400` (direction 0) | `OK` Moved relative | 2.022 s | 1.99 s |
| 17:52:12 | `16,1,3980,800` | `OK` Moved relative | 5.070 s | 4.97 s |
| 17:52:19 | `16,0,3980,800` | `OK` Moved relative | 5.070 s | 4.97 s |

- Every move took its commanded time, so the Arduino emitted every step.
- Direction 0 is the one the firmware gates on D9. Neither direction-0 move was
  refused, so **the limit switch reads clear**.
- The Tic stayed energized with no errors throughout
  ([`b_tic_poll_during_arduino_moves.log`](b_tic_poll_during_arduino_moves.log)).
  In STEP/DIR mode the pulses go straight to the MP6500, so the Tic cannot count
  them.
- No camera frames: `run_moves.sh` created its output directory as root, so the
  camera loop (running as the user) could not write. Fixed in the committed copy.

## D. Is current reaching the coils? (17:54–17:56, no motion)

The Tic has no current sensor, but VIN sags with load. At each temporary current
limit (read back each time) VIN was averaged over 12 samples
([`d2_current_sweep.log`](d2_current_sweep.log)):

| driver | VIN mean | sag |
| --- | --- | --- |
| de-energized | 12.40 V | — |
| 174 mA | 12.03 V | 0.37 V |
| 343 mA | 11.66 V | 0.74 V |
| 634 mA | 11.11 V | 1.29 V |
| 990 mA | 10.50 V | 1.90 V |
| de-energized | 12.50 V | — |

**The sag tracks the setting, so the driver is regulating real current into an
inductive load.** A dead short would have tripped the MP6500's over-current
protection (no driver error was recorded), and an open coil would draw nothing.
That is the opposite of the 6121, which never showed a sign of driving the coils.

An earlier, cruder run ([`d1_energize_toggle.log`](d1_energize_toggle.log))
did not separate 343 from 990 mA, and its de-energized baseline was 12.0 V
rather than 12.4 V. The supply wanders: VIN at 990 mA ranged 10.05–11.1 V over
ten minutes. The sweep ran in 20 s with the limit read back, so it is the one to
trust.

**The 12 V supply is soft.** It drops about 2 V at a 990 mA hold, which is under
0.5 A from the supply. A regulated 12 V / 2 A brick should hardly move at that
load. The MP6500 runs from 4.5 V, so this doesn't block anything, but check the
supply and its wiring if VIN keeps falling under load.

## C. The Tic stepping the motor itself (17:57)

To take the Arduino's STEP/DIR wires out of the question, the Tic was switched
to Serial / I²C / USB mode with the command timeout disabled
([`c_settings_temp_serial.txt`](c_settings_temp_serial.txt); those two lines are
the only difference). It then stepped the motor itself at 800 microsteps/s
(~1 mm/s) ([`c_tic_usb_moves.log`](c_tic_usb_moves.log)):

| time | target | reached |
| --- | --- | --- |
| 17:57:37.5 | +796 (1 mm) | 1.1 s |
| 17:57:40.7 | 0 | 1.1 s |
| 17:57:43.8 | +3980 (5 mm) | 5.2 s |
| 17:57:51.1 | 0 | 5.3 s |

- No errors at any point; VIN held at 10.4–10.7 V.
- Safe start had to be exited after the mode change, as expected.
- **Afterwards the saved settings were reloaded and read back byte-identical.**
  [`final_settings_readback.txt`](final_settings_readback.txt) equals
  [`cubos/docs/tic_p20.txt`](../../docs/tic_p20.txt), and
  [`tic_status_after.txt`](tic_status_after.txt) shows energized, 1/8 step,
  990 mA, no errors. The Tic is back in STEP/DIR mode, as Ben left it.
- The camera took 45 stills, but the pipette was no longer under it (compare
  [`frames/cam0_1750_pipette_in_view.jpg`](frames/cam0_1750_pipette_in_view.jpg)
  with [`frames/cam0_175748_during_tic_move.jpg`](frames/cam0_175748_during_tic_move.jpg)).
  The frame-to-frame changes during the moves are glare shifts on the deck, not
  the pipette.

## What Ben's observation decides

| B (Arduino, 17:52) | C (Tic alone, 17:57) | meaning |
| --- | --- | --- |
| moved | moved | It works. The serial-monitor attempt failed for another reason. |
| no | moved | The Tic and motor are good. The fault is in the Arduino → Tic `STEP`/`DIR`/`GND` wires. |
| no | no, but it buzzed | Current flows but the coil pairs are split across `A` and `B`. |
| no | no, silent, holds firmly | Mechanical: the motor has torque but the plunger can't move. |
| no | no, silent, no holding torque | Contradicts test D. Measure `A1`–`A2` and `B1`–`B2` at the Tic's terminals, power off. |

## Scripts

[`scripts/`](scripts/) holds everything as run on the Pi (the root parts via
`sudo`). The one exception is the output-directory fix in `run_moves.sh`.
