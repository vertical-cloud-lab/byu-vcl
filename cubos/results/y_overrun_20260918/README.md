# 2026-09-18 — Y driven 33 mm past its minimum, and why nothing caught it

**What happened:** during the 2026-09-17 late session (job
`35289317552`, 18:00–18:11 lab-local) an ad-hoc motion test drove the Y axis
**33 mm past its physical minimum**. Ben stopped the run and reset the machine
by hand. No protocol was involved — this was a diagnostic script I wrote and
ran, and the fault is entirely in that script.

Nothing here is a machine fault. The limit switches, the drag chain and the
gantry are not implicated.

---

## 1. The mechanism

GRBL's `WPos` is the controller's **internal step counter**, not a
measurement. The counter and the carriage had been out of agreement since the
serial port closed at the end of campaign 50.

| moment | counter says | carriage actually at |
|---|---|---|
| 17:44:33 campaign 50's last move | (206, 27, 99.065) | (206, 27, 99.065) — in agreement |
| 17:44:35 port closed → board reset (`$22=1`) | **(409, 309, 124)** | (206, 27, 99.065) |
| 18:05 `$H` → `ALARM:9` on Z | (409, 309, 310) | (206, 27, **~124**) — Z ground to its top, X/Y never homed |
| 18:08 soft reset (`0x18`) | **(409, 309, 124)** | (206, 27, ~124) |

So at the moment the motion test started, the counter was **203 mm high on X**
and **282 mm high on Y**.

`motiontest.py` then did, in order:

```python
raw("$X", 0.6)            # unlock — clears Alarm, permits motion on an UNHOMED machine
raw("G91", 0.3)           # RELATIVE mode
raw("G01 X-60 F1000")     # counter 409 -> 349 ; carriage 206 -> 146   (safe, by luck)
raw("G01 X60  F1000")     # counter 349 -> 409 ; carriage 146 -> 206
raw("G01 Y-60 F1000")     # counter 309 -> 249 ; carriage  27 -> -33   <-- 33 mm PAST Y MIN
```

`WCO` on Y is `-309`, so machine-coordinate Y runs `[-309, 0]` and work-frame
Y runs `[0, 309]`. **Work-frame Y = 0 is the physical minimum.** The commanded
target, −33, is 33 mm beyond it.

The script writes its log only at the very end, so `/tmp/zdiag3/motiontest.log`
does not exist — the run was stopped before that point. The frames it did write
stop at `D_y_minus60`, which is the shot taken immediately after the offending
move.

## 2. Why every guard missed it

- **Soft limits (`$20=1`) validated the wrong number.** GRBL checks the target
  against its own machine position. Target MPos Y = `-309 + 249 = -60`, inside
  `[-309, 0]`, so it was accepted. Soft limits are only meaningful *after a
  successful `$H`*; on an unhomed machine they check a fiction.
- **`$X` is not a substitute for `$H`.** Unlock clears `Alarm` and lets motion
  through while leaving the position reference wrong. It is for recovering a
  machine you are about to home, not for jogging.
- **Hard limits are off (`$21=0`).** The physical Y switch was in the path and
  could not stop the move, because GRBL was not watching it.
- **X survived only by coincidence.** 206 − 60 = 146, comfortably inside
  `[0, 409]`. Had the carriage been parked below X 60 the same script would
  have crashed X instead.

## 3. The rule that follows

> **After a failed `$H`, the machine's position is unknown. Do not `$X` and
> jog — recover by hand.** Relative motion is only safe when the counter is
> known to agree with the carriage, and the only thing that establishes that
> is a *successful* homing cycle.

Recorded in `SOP/raspberry-pi-cubos-setup.md`.

This is the same class of error as the 2026-09-16/17 misdiagnosis (an
unpowered gantry read as two limit-switch faults), where the lesson written
down was *"`WPos` is a counter, not a measurement."* That lesson was about
reading the counter; this one is about **commanding against** it, and the
second half was not drawn at the time.

## 4. Motion was real — the frames confirm it

`frame_A_before_cam0.jpg` and `frame_D_after_y_minus60_cam0.jpg` show the deck
plate displaced between the start of the test and the end of the Y move, so
the stepper supply was live and the commands were executing. (Compare with
2026-09-16/17, where identical-looking `?` responses accompanied a machine
that never moved.)

## 5. State left behind

- The GRBL controller (CH340, `1a86:7523`) is **absent from the Pi's USB bus**
  — powered down as part of Ben's manual reset. `/dev/ttyUSB0` does not exist.
- The capper/pipette Arduino (`2341:0043`) is still present and free on
  `/dev/ttyACM0`.
- No CubOS protocol ran; `~/.cubos/logs/gantry/` has no entries after
  17:44:35.
- ⚠️ Z was driven against its upper stop during the 18:05 `ALARM:9` homing
  attempt (≈161 mm of steps beyond contact). That is the fifth such event
  across 09-16/17. A stepper against a hard stop skips rather than breaks, but
  the Z coupling and belt are worth an eyeball.

## 6. Open, and deliberately not answered here

Homing **succeeded** at 17:43:32 (campaign 50, `ok` in 7.0 s) and **failed**
with `ALARM:9` at 18:05 from a similar starting position. I do not have enough
evidence to say why, and the 7.0 s figure is itself hard to reconcile with an
X axis that had 203 mm to travel at `$25 = 1000 mm/min` (12.2 s minimum). Both
observations are recorded; neither is explained. Do not treat either as a
diagnosis.

## Files

| file | what |
|---|---|
| `motiontest.py` | the script that ran, exactly as executed |
| `zdiag.log` | the 18:05 Z diagnostic — every jog refused because GRBL was in `Alarm`, so nothing moved |
| `axistest.log` | the 18:06 single-axis homing attempt: `$HZ` → `error:3` (not compiled in), then `error:8` ×3 |
| `frame_A_before_cam0.jpg` | deck before the motion test |
| `frame_D_after_y_minus60_cam0.jpg` | deck immediately after the Y move |
