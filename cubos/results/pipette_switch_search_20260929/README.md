# 2026-09-29 (evening): the plunger moves. The limit switch proves it

CubXL Pi, lab-local time (MDT, UTC−6). Plunger only: the gantry port
(`/dev/ttyUSB0`) was never opened. Driver: Pololu Tic T500 in STEP/DIR mode, 1/8
step, 990 mA. Arduino firmware: `panda_vcl_p20gen2_20260917.hex`, unchanged. It
still has `STEPS_PER_MM 1592`, so every command below is in **raw microsteps**,
and millimetres assume 796 microsteps/mm (1/8 step).

## Why this test

At 17:54 Ben reported: *"I feel the pipette vibrating."* That came after the
first moves through the Tic
([`tic_t500_first_moves_20260929`](../tic_t500_first_moves_20260929/README.md)).
Everything in that chain is open-loop. A move that returns `OK` at the commanded
rate proves the steps went out, never that the shaft turned. The plunger is
inside the pipette body, and the camera looks at the deck anyway.

The **limit switch** is the one sensor on the plunger. PANDA's `stepMotor()`
aborts an UP move (`DIR` LOW) when D9 reads HIGH, meaning the switch is open and
the plunger is at the top. `moveSteps()` then returns
`ERR:{"error":"Failed to move relative"}`. So an UP move that ends early with
that error means the plunger physically reached the switch.

This session waited for the previous one (run 36646811807) to finish before it
touched the Arduino or the Tic, so only one session drove the hardware at a
time.

## Result 1: switch search, 18:05:16 → 18:07:18 ([log](switch_search.log))

UP in 5 mm chunks (3,980 microsteps) at 200 microsteps/s:

| chunk | took | commanded | outcome |
| --- | --- | --- | --- |
| 1–5 | 20.08 s each | 19.90 s | completed. The switch stayed closed for 25 mm |
| **6** | **15.03 s** | 19.90 s | **the switch opened about 3.7 mm in** |
| 7–12 | 0.114 s each | 19.90 s | refused: 1 step plus the 100 ms debounce, the "switch open" signature |

The firmware's position counter afterwards read −14.36 mm in its own 1592/mm
units, which is 22,861 microsteps up. Taking away chunks 1–5 (19,900) and one step
each for chunks 7–12 leaves about 2,955 microsteps in chunk 6. **So the plunger
travelled about 22,855 microsteps up, 28.7 mm at 796/mm, before it opened the
switch.** That is the first time commanded motion has ever changed the switch.

⚠️ The log's closing `RESULT: NO TRIP` line is **wrong**, a bug in this script.
`PawduinoLink.send_command` raises `PawduinoLinkCommandError` on an `ERR` reply
rather than returning it, so the `reply.startswith("ERR")` test never matched.
The raw lines above are correct. Because of the bug, the back-off-and-repeat
half of the script didn't run, so it was run separately as Result 2.

## Result 2: repeat, start-rate ladder, and `HOME`, 18:08:59 → 18:10:06 ([log](switch_repeat.log))

This starts with the plunger at the switch. Every back-off is DOWN 2 mm at
200/s, and every UP is 4 mm.

| step | rate (microsteps/s) | outcome |
| --- | --- | --- |
| switch read | — | asserted, open, plunger at top |
| back off DOWN 2 mm | 200 | completed. **The switch closed again** |
| UP 4 mm | 200 | **the switch reopened after about 2.01 mm** |
| back off, then UP 4 mm | 400 | reopened after about 2.03 mm |
| back off, then UP 4 mm | 800 | reopened after about 2.04 mm |
| back off, then UP 4 mm | 1600 | reopened after about 2.07 mm |
| back off, then UP 4 mm | 2500 | reopened after about 2.11 mm |
| back off DOWN 2 mm, then firmware `HOME` (cmd 10) | about 1,900 | **`OK:{"msg":"Pipette homed"}` in 1.356 s** |
| `STATUS` | — | `homed:1, pos:0.00`, and the switch reads clear |

- **Both directions move the plunger.** Direction 0 (UP) opens the switch and
  direction 1 (DOWN) closes it again. The switch's position repeats: every
  2 mm back-off takes about 2 mm to undo.
- **The polarity is right, so no `A1`↔`A2` swap is needed.** Direction 0 is the
  way `HOME` seeks, toward the switch.
- **It doesn't stall at any rate the firmware uses, even though every move
  starts abruptly.** `stepMotor()` has no ramp, and the Tic's STEP/DIR mode
  bypasses its own acceleration limiting. Pololu warns that a motor thrown
  straight into a fast rate can *"just sit there or vibrate in place"* (Tic
  guide §4.3). Here it followed at 2,500 microsteps/s, which is `MOVE_TO`'s
  `MOVEMENT_VELOCITY`, and at about 1,900/s, which is `HOME`'s seek. A stall
  would have shown up as a 4 mm move completing without reaching the switch.
- The trip distances are computed from round-trip time with a fixed 0.10 s
  allowance for the debounce and serial overhead. Their spread (2.01 → 2.11 mm)
  is within that method's resolution. Modelling the overhead more carefully
  moves them to 1.86–1.99 mm, so read them as "2 mm, ±0.15".
- **`HOME` works for the first time on this machine.** It seeks at 10 + 500 µs
  per step: 1,592 steps (0.84 s), then the 0.10 s debounce, then its 796-step
  back-off (0.42 s), about 1.36 s in all. The measured 1.356 s matches, instead
  of the 26 s the old board spent running out its step budget. Its
  "796 = 1 mm" back-off is correct at the Tic's 1/8 step.

## The Tic throughout

[`tic_poll.log`](tic_poll.log) and
[`tic_poll_switch_repeat.log`](tic_poll_switch_repeat.log) contain 450 polls, every one
**energized, operation state Normal, no errors**. VIN held at 10.1–10.5 V
while moving. The supply is soft (12.4 V unloaded), but it didn't limit anything
here.

In those poll files, the `errors_now` field shows the *next* line of
`ticcmd --status`. When no error is present, "None" sits on the same line as its
heading, and [`tic_poll.sh`](tic_poll.sh) reads the line after it. Every line
reads "Errors that occurred since last check: None", which is the no-error case.

## What the vibration was

At 1/8 step, the 17:52 moves at 400 and 800 microsteps/s are 50 and 100 full
steps per second. Each full step is a small mechanical tick, so a stepper
running there buzzes at 50–100 Hz. You feel that through the body, and there is
nothing to see because the plunger is inside. The ladder shows the motor follows
at those rates, so the vibration was the motor turning. The 6121 never
produced it, because it never put current through the windings.

## Left as

- **Plunger homed, 796 microsteps below the switch.** The firmware's `homed`
  flag clears whenever the port reopens, since the board resets, and CubOS
  re-homes on connect.
- **Tic de-energized at 18:12** with `ticcmd --deenergize`
  ([status](tic_status_deenergized.txt)). It had been holding at 990 mA, about
  4 W into the pipette body, since about 17:40, with no test running. VIN went
  back to 12.27 V, and the settings are unchanged (1/8 step, 990 mA). **It stays
  de-energized until told otherwise. Switching the 12 V off and on does not
  clear it while USB powers the Tic's logic.** Before the next test:
  `sudo ~/.local/opt/pololu-tic-1.8.1-linux-rpi/ticcmd --energize`
- Electromagnet off (`CMD_EMAG_OFF` → OK). No gantry motion, no firmware or
  settings change.

## ⚠️ Before any protocol: the firmware's millimetres

`STEPS_PER_MM` is still 1592, written for 1/16 step. At the Tic's 1/8, each
firmware millimetre is 1,592 microsteps. If 796/mm is right, that is about 2 mm
of plunger. 796 is what PANDA's own `backOffSteps = 796; // this is equal to 1mm`
assumes, and what the setup doc's ruler check is there to confirm. The first
thing CubOS does on connect is home and then `prime`, which is
`MOVE_TO 28.0` = 44,576 microsteps, **about 56 mm**. That is past the P20 GEN2's
46.5 mm drop-tip plane, into the end of the plunger's travel. So don't connect
CubOS or run the trio until the `STEPS_PER_MM 796` image is on the board.

To settle 796 against 1592 without seeing the plunger, a raw-step gravimetric
check is safe under either assumption:
1. `HOME`
2. `16,1,15920,800`: down 20 mm if 796 is right, 10 mm if 1592 is
3. tip on, into water
4. `16,0,7960,800`: up 10 mm or 5 mm, drawing about 7.5 µL or 3.7 µL at the
   P20 GEN2's 0.746 µL/mm
5. weigh: about 7.5 mg against about 3.7 mg

## Files

- [`switch_search.py`](switch_search.py) and [`switch_repeat.py`](switch_repeat.py):
  the two tests, exactly as run. `switch_repeat.py` has the `ERR` handling fixed.
- [`run.sh`](run.sh) and [`tic_poll.sh`](tic_poll.sh): the root wrapper that polls
  the Tic while the Arduino drives. `run.sh` is shown as last used, with the
  `SCRIPT` switch. The first run used the unsuffixed log names.
- [`switch_search.log`](switch_search.log) and [`switch_repeat.log`](switch_repeat.log)
- `tic_status_before*.txt`, `tic_status_after*.txt` and
  [`tic_status_deenergized.txt`](tic_status_deenergized.txt): `ticcmd --status --full`
