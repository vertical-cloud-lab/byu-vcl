# Pickup x −1 mm full cycle — SUCCESS (2026-07-28)

Requested by @timothy-commins in PR #60: *"when picking up move -1mm in the
x axis. this is in relation to the last test."*

Reference test: `../pickup-test-2026-07-28-x-offset-repeat-x2/` (pickup at
(170.05, 225.0), drop-off at (168.05, 225.0)). Applying the offset:

| parameter | last test | this test |
|---|---|---|
| Pickup XY | (170.05, 225.0) | **(169.05, 225.0)** — x −1 |
| Drop-off XY | (168.05, 225.0) | (168.05, 225.0) — unchanged |
| Drop-off (eject) Z | 96.5 | 96.5 — unchanged |

Everything else reused the proven recipe: descent ladder z 150→120→105→101→99,
straight entry z=95, press to mouth − 7 (z=91.5), lift test z=110, high lift
z=170, carry x 169.05 → 205 → 168.05 in 8.5 mm segments at 10 mm/s, mid-air
`dropTipInPlace` eject at z=96.5, post-eject clearance capped at z=128
(bare-P300 +Z rule). Driven over the tailnet (runner → Tailscale → RPi-5 →
USB-Ethernet → OT-2 HTTP API), one maintenance run, camera frame checked at
every key stage.

## Result — full cycle succeeded at the new pickup x

| stage | outcome |
|---|---|
| Descent ladder at (169.05, 225.0) | ✓ tip centred at the crown mouth |
| Straight entry z=95 | ✓ clean insertion, no housing displacement |
| Press to z=91.5 (mouth − 7) | ✓ gripped |
| Lift test z=110 | ✓ module off its base |
| High lift z=170 + carry to x=205 | ✓ module hanging, aboard the whole trip |
| Return carry to x=168.05 | ✓ still aboard |
| Descend to z=96.5 | ✓ hovering, foot ~5 mm above seat |
| Mid-air eject (`dropTipInPlace`) | ✓ clean release; module seated upright |
| Clearance z=128 → home | ✓ no +Z alarm |

Notes:

- The recipe is now **4-for-4** across three sessions with zero re-teaching.
- Pickup X has now succeeded at 171.05, 170.05 and 169.05 — a **2 mm pickup-x
  tolerance band** with no visible degradation in centring, entry or grip.
  The crown mouth chamfer + hang self-centring absorb the offset.
- Notably this pickup was 1 mm −x of where the module was last *dropped*
  (168.05): the base pocket re-centred it on drop-in well enough that the
  new coordinates worked immediately.

## Frames

1. `xm1_00_baseline.jpg` — module seated, crown up, nozzle parked.
2. `xm1_01_z99_mouth.jpg` — end of descent ladder at the new x=169.05.
3. `xm1_02_entry_z95.jpg` — straight entry, no housing shift.
4. `xm1_03_press_z91p5.jpg` — eject-capable press (mouth − 7).
5. `xm1_04_lifttest_z110.jpg` — grip confirmed, module off its base.
6. `xm1_05_highlift_z170.jpg` — hanging at carry height.
7. `xm1_06_carry_x205.jpg` — outbound end of carry, module aboard.
8. `xm1_07_return_x168.jpg` — returned over drop-off x=168.05, still aboard.
9. `xm1_08_predrop_z96p5.jpg` — hovering at the low release height.
10. `xm1_09_after_eject.jpg` — clean release; module seated, nozzle bare.
11. `xm1_10_clear_z128.jpg` — bare-nozzle clearance (no +Z alarm).
12. `xm1_11_final_homed.jpg` — gantry homed, module seated, matches baseline.

## Robot end state

Clean: gantry homed, maintenance run deleted, module seated on its base in
slot 8, crown up, nozzle bare. Status note updated in
`/tmp/OT2_STATUS_READ_ME_FIRST.txt` on the RPi-5. Camera is still mis-aimed
from the 2026-07-28 bump (side-on view) but verified every stage.
