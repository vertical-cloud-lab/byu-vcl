# X-offset full cycle × 2 — both SUCCEEDED back-to-back (2026-07-28)

Requested by @timothy-commins in PR #60: *"do it twice more in the same
run"* — i.e. repeat the just-proven x-offset recipe
(`../pickup-test-2026-07-28-x-offset-low-drop/`) two more times in a single
session, back-to-back, to check repeatability.

Recipe (unchanged from the reference session): pickup at **(170.05, 225.0)**,
descent ladder z 150→120→105→101→99, straight entry z=95, press to mouth − 7
(z=91.5), lift test z=110, high lift z=170, carry x 170.05 → 205 → 168.05 in
8.5 mm segments at 10 mm/s, drop-off at **(168.05, 225.0)**, descend to
**z=96.5** (foot ~5 mm above seat), mid-air `dropTipInPlace` eject,
post-eject clearance capped at z=128 (bare-P300 +Z rule). Driven over the
tailnet (runner → Tailscale → RPi-5 → USB-Ethernet → OT-2 HTTP API), one
maintenance run for both cycles, camera frame checked at every key stage.

## Result — 2 / 2 full cycles succeeded, no alarms, no intervention

| stage | cycle 1 | cycle 2 |
|---|---|---|
| Descent ladder at (170.05, 225.0) | ✓ tip centred at crown mouth | ✓ |
| Straight entry z=95 | ✓ no housing displacement | ✓ |
| Press to z=91.5 (mouth − 7) | ✓ gripped | ✓ gripped |
| Lift test z=110 | ✓ module off its base | ✓ |
| High lift z=170 + carry to x=205 | ✓ module hanging, aboard | ✓ |
| Return carry to x=168.05 | ✓ still aboard | ✓ |
| Descend to z=96.5 | ✓ hovering over pocket | ✓ |
| Mid-air eject (`dropTipInPlace`) | ✓ clean release, seated upright | ✓ |
| Clearance z=128 | ✓ no +Z alarm | ✓ no +Z alarm |

Notably, cycle 2 picked up at (170.05, 225.0) **after cycle 1 had ejected at
x=168.05** — the base pocket re-centred the module on drop-in well enough
that the unchanged pickup coordinates worked immediately. That is the
mechanism the unattended cyclic test relies on, and it just survived its
first back-to-back repeat: the recipe is now **3-for-3** across two sessions
with zero re-teaching between cycles.

## Frames

Prefix `c1_` = cycle 1, `c2_` = cycle 2 (same stage numbering in both):

1. `00_baseline.jpg` — module seated, crown up, nozzle parked.
2. `cN_01_z99_mouth.jpg` — end of descent ladder, tip at the crown mouth.
3. `cN_02_entry_z95.jpg` — straight entry, no housing shift.
4. `cN_03_press_z91p5.jpg` — eject-capable press (mouth − 7).
5. `cN_04_lifttest_z110.jpg` — grip confirmed, module off its base.
6. `cN_05_highlift_z170.jpg` — hanging at carry height.
7. `cN_06_carry_x205.jpg` — outbound end of carry, module aboard.
8. `cN_07_return_x168.jpg` — returned over drop-off x=168.05, still aboard.
9. `cN_08_predrop_z96p5.jpg` — hovering at the low release height.
10. `cN_09_after_eject.jpg` — clean release; module seated upright, nozzle bare.
11. `cN_10_clear_z128.jpg` — bare-nozzle clearance (no +Z alarm).
12. `c2_11_final_homed.jpg` — gantry homed, module seated, matches baseline.

## Robot end state

Clean: gantry homed, maintenance run deleted, module seated on its base in
slot 8, crown up, nozzle bare. Status note updated in
`/tmp/OT2_STATUS_READ_ME_FIRST.txt` on the RPi-5. Camera is still mis-aimed
from the 2026-07-28 bump (side-on view) but verified every stage.
