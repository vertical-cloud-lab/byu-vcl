# 2026-09-24 — the P20 GEN2 image is on the board; the trio was cut by a power loss

Asked for: *"run the trio. Now that the coils are working, I want to see if the
pipette works."*

**Outcome: the firmware half of this problem is finished, the plunger was
exercised 8 mm in both directions at the commanded rate, and the protocol run
itself did not complete — the Pi lost power about a minute in.**

## What was done

| | |
|---|---|
| CubOS rebuilt on the runner at the Pi's exact tree | `496819c` + all three patches, applied clean |
| `validate_setup` | **PASS**, 12 targets |
| `run_protocol --mock` | **12/12** |
| GRBL read live, read-only | `Alarm`, **no `Pn:` field**; `$20=1`, `$130/$131/$132` = 409/309/124 — matches the gantry file |
| Arduino link | healthy; `STATUS` and the capper's cap sensor both answer |
| limit switch | **CLEAR** — 14 mm of retraction ran un-gated |
| 🔑 firmware | **`panda_vcl_p20gen2_20260917.hex` flashed and verified** — 17382 bytes, matches only the GEN2 image |
| `CMD 29` with the read fix live | **still `comm = 0`** — isolates the failure to the bridge resistor |
| bench plunger window | ±4 mm balanced plus a 14 mm out-and-back, every leg at the commanded rate, **net travel zero** |
| the trio | 🔴 **cut at ~22:20 UTC by a power loss, about a minute in** |

## The flash, and why it came first

The board had been running the 2026-09-15 p20 image, confirmed again by
`avrdude -U flash:v:` against all three candidates before anything else was
done. That image carries `PRIME_POSITION 36.0` — a P300 plane — while a
P20 GEN2's bottom is **28.0**.

`MOVE_TO` is absolute millimetres, so CubOS's patched `blowout` (32.5) and
`drop_tip` (46.5) land where CubOS asks on either image. **`aspirate` does
not**: `aspirate()` is computed inside the firmware and descends to
`PRIME_POSITION` before its metered ascent. With coils that were open, that
cost nothing. With coils that now measure 4.3 Ω and 3.7 Ω it would drive the
plunger **8 mm past its mechanical bottom on every call**, stalling it against
the stop for the rest of the descent. §18.5 of the wiring doc named this a
prerequisite for running `aspirate` on a working motor, so it was done before
the trio rather than after.

Both instrument paths were re-checked on the reflashed board — the capper
shares this Arduino — and both answer. The pre-change flash backup and the
09-15 image are both committed, so this is reversible.

## `comm = 0` is now a one-line diagnosis

The GEN2 image carries `tmc2209-softwareserial-read`, without which a TMC2209
read over `SoftwareSerial` on an AVR is structurally impossible. Five reads
straight after flashing still return `comm = 0`.

That is not a disappointment, it is the isolation: with the software half
fixed, the only remaining cause is the hardware bridge. The 10 kΩ resistor is
still on the **RX** side, so the Arduino's push-pull `SoftwareSerial` TX idles
HIGH on the shared node and the driver cannot pull it down to reply. It has to
be `A1 —1 kΩ— NODE`, with `A0` **and** `PDN_UART` both directly on `NODE`.

One resistor now stands between this machine and `DRV_STATUS` — which reports
`open_load_a/b`, `s2ga/s2gb`, `s2vsa/s2vsb` and `ot` directly, i.e. the
specific bit behind `DIAG` = 5 V.

## 🔴 A tooling bug found the hard way

`CMD_MOVE_RELATIVE` (16) takes **three** varargs: `direction, steps, velocity`.
`PawduinoLink.send_command(code, *args)` is varargs, not a list. Passing
`[d, steps, rate]` as one argument serialises the list's `repr`, and the
firmware's comma tokenizer then reads `atof("[0") == 0` — so **`direction`
silently parses as 0 whatever you asked for**, and the reply's own echo shows
`v[0] = 0.00` in both cases.

The first window therefore walked **14 mm of retraction** instead of a balanced
±6 mm. It was restored with a correct `direction=1` advance in the same
session, and the subsequent ±4 mm window nets to zero — total commanded travel
for the session is zero. Retraction is the gated direction, so none of it being
refused is itself the clean confirmation that D9 reads LOW.

`cubos/tools/pipette_driver_measure.py` has the same defect from the other
side: it sends `send_command(16, steps, rate)` — two args — which this firmware
rejects outright with `ERR:{"error":"Missing relative move arguments
(direction, steps, velocity)"}`. Fixed in the same commit as this write-up.

## 🔴 The machine state is unknown

The protocol started at about 22:19 UTC. The Pi dropped off the tailnet at
**22:20:00 UTC** and had not returned 25 minutes later. The Pi shares power
with the gantry, so a supply interruption takes both — which means the run was
cut at an arbitrary point with no closing `home` and no `CMD_EMAG_OFF`.

**Before the next run, by eye:**

- **Is the capper holding a cap?** The protocol's step 2 is `decap vial_1`. If
  power was cut between there and `cap vial_1`, a cap is either on the
  electromagnet or was dropped when the coil de-energised.
- **Is a vial open?** Same window.
- **Where is the head?** GRBL's counter resets to the homed corner on port
  open regardless of where the carriage is, so `WPos` after a power cut is
  fiction. Recover by hand or by a successful `$H`; do **not** `$X` and jog —
  that is what drove Y past its stop on 2026-09-18.
- **Re-check `$20`.** It read `1` before this run, but an interrupted
  calibration leaves it at `0`, and it has been found off twice.

## Files

| | |
|---|---|
| `firmware_flash.log` | the three before-verifies, the flash, the three after-verifies, both instrument paths, the five `CMD 29` reads, and the GRBL dump |
| `bench_window.log` | both plunger windows with timestamps, the direction semantics, and the arithmetic showing net travel zero |
| `validate_runner.log`, `mock_runner.log` | the offline gates, run against `496819c` + all three patches |

No run log, plunger trace or camera frames — those were being written on the Pi
when it lost power.
