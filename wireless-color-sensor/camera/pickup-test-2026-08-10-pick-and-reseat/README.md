# Pick up → set back down — SUCCESS (2026-08-10, evening)

Requested by @timothy-commins in PR #60: *"Go to the enclosure and pick it
up, and then set it back down."* A minimal cycle — the proven wire-attached
recipe from
[`../pickup-test-2026-08-10-full-cycle-sensor-read/`](../pickup-test-2026-08-10-full-cycle-sensor-read/)
minus the long carry and the sensor read (not requested this time). The
recipe is now **9-for-9 on completed reseats.**

Driven from the RPi-5 (`ssh` over tailnet → USB-Ethernet →
`http://169.254.51.252:31950` maintenance-run API), frames with
`rpicam-still` between stages.

## Sequence (recipe values unchanged)

| stage | value |
|---|---|
| Pickup XY | (169.05, 225.0) |
| Descent ladder | z 170 → 150 → 120 → 105 → 101 → 99 |
| Straight entry | z = 95 (5 mm/s) |
| Press | z = 90.5 (5 mm/s) |
| Lift test | z = 110 + 4 s dwell — **held here for a camera grip check** |
| Drop-off XY | (163.05, 225.0) — anti-tilt −6 mm offset |
| Staged descent | z 108 → 101 → 95.5 |
| Eject | dropTipInPlace, clear to z = 128, home |

Run as two phases: a phase-1 script (home → ladder → entry → press → lift
test) that left the maintenance run open holding at z = 110, a camera
verification that the module was actually hanging on the nozzle, then the
reseat leg executed by running the repo's
[`recover_reseat.py`](../../cad/recover_reseat.py) **unmodified** — the
post-lift hold state (169.05, 225, 110) is exactly the stranded-grip state
that script was written to recover from, and its savePosition pre-check
passed at 0.0 mm offset. This two-phase pattern (verify grip on camera
before committing to the blind reseat leg) avoids the failure mode where a
missed grip would send the nozzle down at the offset drop-off X beside a
still-seated crown.

## Reseat check, measured

`00_baseline_seated.jpg` vs `05_final_reseated_homed.jpg` (same camera
pose; mean abs grey-level difference at 1640 × 1232):

| region | diff |
|---|---|
| module | 3.3 |
| gantry pillar (static) | 2.5 |
| right panel (static) | 1.6 |
| deck front | 4.5 |

Module-band vertical cross-correlation: **0 px ≈ 0.0 mm** — fully seated,
module diff at static-region noise level.

## Frames

1. `00_baseline_seated.jpg` — module seated in slot 8, bare crown, before any motion.
2. `01_homed.jpg` — gantry homed, maintenance run open.
3. `02_z99_mouth.jpg` — descent ladder done, nozzle at the crown mouth.
4. `03_press_z90p5.jpg` — straight entry + press complete.
5. `04_lifttest_z110.jpg` — **grip confirmed**: module raised ~19.5 mm off its base, hanging on the nozzle.
6. `05_final_reseated_homed.jpg` — module reseated, bare crown, gantry homed.

## Robot end state

Clean: module reseated on its slot-8 base (camera + 0 px cross-correlation),
nozzle bare, gantry homed, no maintenance run left on the robot
(`/maintenance_runs/current_run` → `NoCurrentRunFound`).
