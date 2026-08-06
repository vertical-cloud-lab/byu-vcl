# CubXL — limit switches, soft limits, and getting un-stuck

Written up from the 2026-08-05 calibration failures in
[#133](https://github.com/vertical-cloud-lab/byu-vcl/issues/133) (Ben and Jarrett:
gantry runs into a limit, locks up, needs a power cycle plus `$20=0` to jog off).

Everything below is checked against CubOS `main` @ `v0.1.69` and the official
SainSmart docs for the base machine.

## The base machine

The CubXL gantry is a **SainSmart Genmitsu PROVerXL 4030 V2** — CubOS says so
directly in
[`packages/core/configs/gantry/cub_xl_panda.yaml`](https://github.com/Ursa-Laboratories/CubOS/blob/main/packages/core/configs/gantry/cub_xl_panda.yaml#L6)
("Estimated work volume from the Cub XL / Genmitsu PROVerXL 4030 V2 setup").
It runs stock **GRBL 1.1** over USB-B.

Factory GRBL defaults for that machine:

| Setting | Default | Meaning |
| --- | --- | --- |
| `$5` | `0` | Limit pins **not** inverted → switches are **normally open** |
| `$20` | `0` | Soft limits **off** |
| `$21` | `1` | Hard limits **on** |
| `$22` | `1` | Homing cycle enabled |
| `$23` | `0` | Homing direction mask |
| `$27` | `3.000` | Homing pull-off (mm) |
| `$110/$111/$112` | `2000` | Max rate, mm/min |
| `$120/$121/$122` | `300` | Acceleration, mm/s² |
| `$130/$131/$132` | `420 / 310 / 110` | Max travel, mm |

Two consequences matter here:

- **`$20` requires homing and correct `$130–$132`.** SainSmart's own reference
  spells it out: `$20` is "Enable, Hard limits and homing Required". After a
  hard-limit trip GRBL has *lost* its machine position, so a soft-limit check
  against that position is meaningless — GRBL rejects the jog with `error:15`
  (*travel exceeded*). That is exactly why `$20=0` is needed to jog off.
- **`$5=0` means an unplugged limit switch reads as "never triggered."** The
  Z-limit wire that keeps pulling out has no fail-safe: with normally-open
  wiring, a disconnected switch silently removes hard-limit protection on that
  axis rather than faulting. See [Z-limit wire](#z-limit-wire) below.

## Recovery procedure (do this at the machine)

SainSmart's official procedure for a triggered limit switch is: **unlock → set
jog step to 10 → jog away from the switch → re-home.** With GRBL 1.1 on a
hard-limit trip there is one extra step *before* the unlock, and one after:

1. **Soft-reset first — `Ctrl-X` (`0x18`), not just `$X`.** A hard limit is a
   *critical* GRBL event: GRBL enters an alarm loop that ignores everything
   except a soft reset. Pressing "Unlock" alone (UGS's unlock button sends only
   `$X`) does nothing, which is what makes it look like the controller needs a
   power cycle. In the Operator UI this is **Advanced → Reset and unlock**
   (`POST /gantry/reset-unlock`), not **Unlock (`$X`)**.
2. **`$X`** to clear the alarm lock (the reset-and-unlock button does both).
3. **`$20=0`** — disable soft limits. Required because machine position is lost
   after the trip; leave this off only for the pull-off.
4. **Jog off the switch**, 10 mm at a time, away from the limit.
5. **`$20=1`** to re-enable soft limits.
6. **`$H` to re-home.** Position is not trustworthy until you do. Do not resume
   calibration or a protocol on an un-homed machine.

A power cycle also works for steps 1–2, but note GRBL boots straight back into
Alarm when `$22=1`, so you still need `$X` and `$20=0` afterward — which matches
what Jarrett saw.

## Why it happens: three findings in CubOS

### 1. During calibration, *every* travel guard is off simultaneously

Ben's read — "soft limits are off automatically when we entered calibration…
the machine was taking any inputs we sent it and not limiting us in any way" —
is correct, and it is deliberate. Starting calibration turns off three separate
guards at once:

| Guard | Where it is disabled |
| --- | --- |
| GRBL soft limits (`$20=0`) | [`session.py:459-462`](https://github.com/Ursa-Laboratories/CubOS/blob/main/packages/core/src/cubos/gantry/session.py#L459-L462) — `prepare_calibration_origin` |
| Server-side working-volume check | [`session.py:818-819`](https://github.com/Ursa-Laboratories/CubOS/blob/main/packages/core/src/cubos/gantry/session.py#L818-L819) — `_calibration_jog_bypass_working_volume` short-circuits `_validate_jog_target_locked` |
| Client-side predicted-position check | absent in [`CalibrationWizard.tsx:704`](https://github.com/Ursa-Laboratories/CubOS/blob/main/apps/operator-web/src/components/gantry/CalibrationWizard.tsx#L704) — the normal jog panel *does* have one ([`GantryPositionWidget.tsx:150-166`](https://github.com/Ursa-Laboratories/CubOS/blob/main/apps/operator-web/src/components/gantry/GantryPositionWidget.tsx#L150-L166)) |

The rationale is sound — pre-calibration `$130–$132` are stale, so soft limits
would reject the very jogs calibration needs. But the result is that during
calibration the **physical limit switches are the only thing left**, and hitting
one is a hard-limit alarm, not a graceful stop. There is no "slow down near the
edge" layer in between.

Turning `$20` back on mid-calibration (what Ben and Jarrett tried) makes it
*worse*, not better: it re-imposes the stale factory envelope on top of a
half-calibrated origin.

### 2. `$20` is written back to `1` on disconnect, so the trap re-arms

`$` settings live in GRBL's EEPROM and survive a power cycle. On disconnect (or
an errored teardown) CubOS restores `$20=1`
([`session.py:900-903`](https://github.com/Ursa-Laboratories/CubOS/blob/main/packages/core/src/cubos/gantry/session.py#L900-L903)).
So the sequence is: trip a limit → session tears down → `$20=1` written → next
connect finds the machine parked on a switch with an unknown position and soft
limits on → every jog is refused with `error:15` → operator concludes the
machine is bricked and power-cycles. That is the loop they were in.

The Operator UI does expose the escape hatch: the **"Calibration interrupted —
soft limits are disabled / Restore soft limits"** banner and the Advanced GRBL
settings box (type `$20`, value `0`, Apply).

### 3. Holding a jog button queues more motion than a release can cancel

This is Jarrett's "if we hold the button for too long, the gantry will keep
moving and not stop until it hits the limit," and it is a real race, not
operator error.

- The UI re-fires a jog every **150 ms** while a button is held
  ([`CalibrationWizard.tsx:46`](https://github.com/Ursa-Laboratories/CubOS/blob/main/apps/operator-web/src/components/gantry/CalibrationWizard.tsx#L46),
  same constant in `GantryPositionWidget.tsx`).
- Each jog is a separate `POST /gantry/jog` at the default **F2000**.
- At the stock 300 mm/s² acceleration, one jog step actually takes:

  | Step | Execution time | vs. 150 ms issue interval |
  | --- | --- | --- |
  | 0.5 mm (UI default) | ~58 ms | drains fine |
  | 5 mm | ~260 ms | queue grows ~1.7× |
  | 10 mm | ~410 ms | queue grows ~2.7× |

  Z is worse wherever `$112` is set below `$110`/`$111`.

  5–10 mm is not an exotic setting — it is exactly what
  [the CubOS UI docs recommend](https://github.com/Ursa-Laboratories/CubOS/blob/main/docs/operator-ui.md)
  for "long moves across the deck," i.e. precisely the moves that head toward a
  limit.

- Releasing the button sends `POST /gantry/jog-cancel`, which reaches GRBL as a
  jog-cancel (`0x85`) and flushes the planner. But:
  - `/gantry/jog-cancel` takes the same session lock as `jog`
    ([`session.py:302-305`](https://github.com/Ursa-Laboratories/CubOS/blob/main/packages/core/src/cubos/gantry/session.py#L302-L305)),
    so it queues **behind** every jog request still in flight — each of which can
    hold the lock for up to the 2 s serial read timeout when GRBL's planner is
    full and stops acking.
  - Worse, there is no cancel epoch: the jog requests that were already queued
    **re-issue `$J=` after** the cancel lands. The flush is undone by the
    backlog.
  - A non-blocking path already exists — `session.jog_cancel_interrupt()`
    ([`session.py:307-309`](https://github.com/Ursa-Laboratories/CubOS/blob/main/packages/core/src/cubos/gantry/session.py#L307-L309))
    and `request_jog_cancel_interrupt()`
    ([`routers/gantry.py:686`](https://github.com/Ursa-Laboratories/CubOS/blob/main/services/api/src/cubos_api/routers/gantry.py#L686))
    — but **no HTTP route is wired to it**; the only exposed route is the
    locking one.

### Bonus: auto-recovery exists, but only in the calibration wizard

CubOS *does* have automatic limit recovery — jog-cancel → `Ctrl-X` → `$X` →
pull-off jog opposite the failed direction, up to 5 attempts
([`limit_recovery.py`](https://github.com/Ursa-Laboratories/CubOS/blob/main/packages/core/src/cubos/gantry/limit_recovery.py)).
It is wired into the CLI calibration tool and into the Operator UI's
**Calibration Wizard** (which watches the status poll for `ALARM` and fires
recovery using the last jog delta). It is **not** wired into the ordinary jog
panel — there, an alarm just greys out the jog buttons and you are on your own
with the Advanced panel.

Also, `session.jog()` never probes controller status after a jog. GRBL acks a
`$J=` as soon as it is *queued*, so the jog that trips the limit usually returns
HTTP 200 and the alarm only surfaces on the next status poll. The CLI path calls
`probe_for_limit_status_after_jog()` for exactly this reason; the API path does
not.

## Settings to verify on our machine

Connect, then **Advanced → Read GRBL settings** in the UI (or `$$` in a serial
terminal) and check:

```
$5    should be 0    (normally-open switches — confirm against actual wiring)
$20   should be 1    (except mid-calibration)
$21   should be 1    (hard limits ON — nothing in any shipped CubOS gantry YAML
                      sets this, so it is whatever the controller happens to hold)
$22   should be 1
$23                  (must match the physical corner the switches sit in)
$27   3.000          (pull-off; CubOS forces a >= 5 mm pull-off during recovery)
$130/$131/$132       (must match the *calibrated* envelope, not the 420/310/110
                      factory numbers, or soft limits guard the wrong box)
```

`$21` is worth checking first. **No CubOS gantry config in the repo sets
`hard_limits`** — `cub_xl_sterling.yaml` sets `soft_limits: true` and stops
there — so if `$21` ever got written to `0`, hitting a switch does nothing at
all and the axis just grinds into its mechanical stop.

## Z-limit wire

The Z-limit switch pulling out of its connector has now happened three times
(2026-06-29, 2026-07-22, 2026-08-05). With `$5=0` / normally-open wiring, a
disconnected switch does not fault — it silently reports "not triggered," so Z
loses hard-limit protection without any warning. Worth (a) adding strain relief
/ a service loop so the wire cannot reach tension over full Z travel, and (b)
raising the cable length with Ursa as a hardware fix, since it is not
lab-specific.

## Upstream

Existing CubOS issues that overlap:

- [Ursa-Laboratories/CubOS#245](https://github.com/Ursa-Laboratories/CubOS/issues/245)
  — *Clear GRBL alarms/errors gracefully* (open). Alex hit the same thing on the
  4040: "CubOS hangs and errors out upon receiving an alarm from the gantry
  reaching a limit switch outside of a homing step."
- [Ursa-Laboratories/CubOS#211](https://github.com/Ursa-Laboratories/CubOS/issues/211)
  — *Guard against GRBL settings drift on connect* (open) — covers the `$20`/`$21`
  verification gap.

Not yet filed, and worth filing separately:

1. **Jog-cancel cannot win against a held-button backlog** — wire a route to
   `request_jog_cancel_interrupt()` (lock-free) and add a cancel generation
   counter so in-flight jog requests issued before the cancel are dropped
   instead of re-issued. Optionally make the UI's repeat interval adapt to step
   size, or use a single long continuous jog plus `0x85` on release rather than
   a 150 ms drip of discrete jogs.
2. **Limit-alarm auto-recovery in the ordinary jog panel**, not just the
   calibration wizard — plus a post-jog status probe in `session.jog()` so the
   alarm is caught at the jog that caused it.
3. **`$20=1` restored onto a machine parked on a limit switch** — restore soft
   limits only after a successful re-home, or surface a one-click "clear alarm,
   pull off, re-home" recovery that handles `$20` itself.
4. **`hard_limits` absent from every shipped gantry YAML** — `$21` should be
   asserted on connect, not inherited from EEPROM.
