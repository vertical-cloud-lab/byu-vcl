# X-offset pickup + lower drop — SUCCESS (2026-07-28)

Requested by @timothy-commins in PR #60: *"try again but go -1 mm in the x
axis when picking up. go -3mm in the x when dropping off. also when dropping
off make it go -5mm in the z axis. all of this is relative to the last test
you did."*

Reference test: `../pickup-test-2026-07-28-y-minus-2-success/` (pickup/eject
at (171.05, 225.0), pre-drop hover z=101.5). Applying the offsets:

| parameter | last test | this test |
|---|---|---|
| Pickup XY | (171.05, 225.0) | **(170.05, 225.0)** — x −1 |
| Drop-off XY | (171.05, 225.0) | **(168.05, 225.0)** — x −3 |
| Drop-off (eject) Z | 101.5 (foot ~10 mm up) | **96.5** (foot ~5 mm up) — z −5 |

Everything else reused the proven recipe: descent ladder z 150→120→105→101→99,
straight entry z=95, press to mouth − 7 (z=91.5), lift test z=110, carry at
z=170 in 8.5 mm segments at 10 mm/s, mid-air `dropTipInPlace` eject. Driven
over the tailnet (runner → Tailscale → RPi-5 → USB-Ethernet → OT-2 HTTP API),
camera frame checked between stages.

## Result — full cycle succeeded with the offsets

| stage | outcome |
|---|---|
| Descent ladder at (170.05, 225.0) | ✓ tip centred over the crown mouth |
| Straight entry z=95 | ✓ clean insertion, no housing displacement |
| Press to z=91.5 (mouth − 7) | ✓ gripped |
| Lift test z=110 / high lift z=170 | ✓ module rises and hangs cleanly |
| Carry x 170.05 → 205 → 168.05, 8.5 mm segments @ 10 mm/s | ✓ module aboard the whole trip |
| Descend to z=96.5 at (168.05, 225.0) | ✓ hovering, foot ~5 mm above seat |
| Mid-air eject (`dropTipInPlace`) | ✓ clean release; module dropped into the pocket and seated upright |
| Clearance z=128 → home | ✓ **no +Z alarm this time** (kept below the bare-P300 z≈130 limit learned last session) |

Notes:

- The −1 mm pickup X did not degrade entry or grip — the tip still centred in
  the crown mouth and the press/lift behaved exactly as at 171.05.
- The drop-off landed cleanly even though the eject XY is now 2 mm −x of
  where the module was picked up; the base pocket guided it in and the module
  seated upright. The 5 mm-lower release (z=96.5) shortened the free fall.
- Post-eject clearance was deliberately capped at z=128 instead of 150,
  applying the rule from the last session's `Hard limit +Z` incident — no
  alarm occurred.

## Frames

1. `00_baseline.jpg` — module seated, crown up, nozzle parked.
2. `01_z105.jpg` / `02_z99_mouth.jpg` — descent ladder at the new x=170.05.
3. `03_entry_z95.jpg` — straight entry, no housing shift.
4. `04_press_z91p5.jpg` — the eject-capable press (mouth − 7).
5. `05_lifttest_z110.jpg` — grip confirmed, module off its base.
6. `06_highlift_z170.jpg` — hanging at the carry height.
7. `07_carry_x205.jpg` — outbound end of carry, module aboard.
8. `08_return_x168.jpg` — returned over the new drop-off x=168.05, still aboard.
9. `09_predrop_z96p5.jpg` — hovering at the new lower release height.
10. `10_after_eject.jpg` — clean release; module seated upright, nozzle bare.
11. `11_nozzle_clear_z128.jpg` — bare-nozzle clearance (no +Z alarm).
12. `12_final_homed.jpg` — gantry homed, module seated, matches baseline.

## Robot end state

Clean: gantry homed, maintenance run deleted, module seated on its base in
slot 8, crown up, nozzle bare. Status note updated in
`/tmp/OT2_STATUS_READ_ME_FIRST.txt` on the RPi-5. Camera is still mis-aimed
from the 2026-07-28 bump (side-on view, crown region low in frame) but was
sufficient to verify every stage.
