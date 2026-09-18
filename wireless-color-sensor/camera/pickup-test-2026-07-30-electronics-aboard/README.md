# Full cycle with REAL ELECTRONICS aboard — SUCCESS (2026-07-30)

Requested by @timothy-commins in PR #60: *"pickup, move and then put back the
color sensor. note that all the electrical components inside of it are there
from the recreate wireless color git issue."*

This is the **first full pick-up → carry → put-back cycle with the fully
loaded module** — housing plus all electronics (Pico W, color-sensor board,
LiPo + shim, wiring), visibly installed (the board is on the housing's side
face in every frame). All prior full cycles ran on the lighter, empty housing.

The **proven 5-for-5 recipe was reused unchanged** — zero re-teaching. The
only addition was an extra 4-second dwell after the lift test to check for
slow grip slip under the added mass. Driven over the tailnet (runner →
Tailscale → RPi-5 → USB-Ethernet → OT-2 HTTP API), one maintenance run,
camera frame checked at every key stage.

## Recipe (unchanged from `../pickup-test-2026-07-28-slot1-measure/`)

| stage | coordinates / z |
|---|---|
| Pickup XY | (169.05, 225.0) |
| Descent ladder | z 150 → 120 → 105 → 101 → 99 |
| Straight entry | z = 95 |
| Press (eject-capable) | z = 91.5 (mouth − 7) |
| Lift test | z = 110, **+ 4 s dwell slip check (new)** |
| High lift / carry height | z = 170 |
| Carry | x 169.05 → 205 → 168.05, 8.5 mm segments @ 10 mm/s |
| Drop-off XY | (168.05, 225.0) |
| Drop-off (eject) Z | 96.5 (foot ~5 mm above seat) |
| Post-eject clearance | z = 128 (bare-P300 +Z rule) |

## Result — full cycle succeeded with the loaded module

| stage | outcome |
|---|---|
| Descent ladder at (169.05, 225.0) | ✓ tip centred at the crown mouth |
| Straight entry z=95 | ✓ clean insertion, no housing displacement |
| Press to z=91.5 (mouth − 7) | ✓ gripped |
| Lift test z=110 | ✓ loaded module off its base, base stayed |
| 4 s dwell at z=110 | ✓ **no slip** — grip static under full electronics mass |
| High lift z=170 | ✓ module hanging cleanly |
| Carry x 169.05 → 205 (10 mm/s, segments) | ✓ module aboard the whole way |
| Return carry to x=168.05 | ✓ still aboard |
| Descend to z=96.5 | ✓ hovering, foot ~5 mm above seat |
| Mid-air eject (`dropTipInPlace`) | ✓ clean release; module reseated upright |
| Clearance z=128 → home | ✓ no +Z alarm |

Notes:

- **The recipe is now 6-for-6**, and this cycle retires the biggest open
  question: the press-fit grip that held the empty housing also holds the
  full electronics payload — through pickup, a 4 s static hang, a ~37 mm
  each-way slow carry, and a clean ejector release.
- The added mass produced no visible change in behaviour: no extra housing
  drag on entry, no slip during the dwell, no detach during the carry, and
  the module dropped straight back into its base pocket on eject.
- Next logical steps: repeat with the slot-1 "measure gesture" traverse
  (~224 mm each way) with electronics aboard, then unattended multi-cycle
  runs to build the fatigue count Tim planned.

## Frames

All frames are rotated 180° to upright before committing (see camera caveat).

1. `00_baseline.jpg` — module seated, crown up, electronics board visible.
2. `01_z99_mouth.jpg` — end of descent ladder, tip at the crown mouth.
3. `02_entry_z95.jpg` — straight entry, no housing shift.
4. `03_press_z91p5.jpg` — eject-capable press (mouth − 7).
5. `04_lifttest_z110.jpg` — grip confirmed, loaded module off its base.
6. `05_lifttest_dwell.jpg` — after 4 s hang: same height, no slip.
7. `06_highlift_z170.jpg` — hanging at carry height (module's lower half at
   the top of the low-angle frame).
8. `07_carry_x205.jpg` — outbound end of carry, module aboard.
9. `08_return_x168.jpg` — returned over drop-off x=168.05, still aboard.
10. `09_predrop_z96p5.jpg` — hovering at the low release height.
11. `10_after_eject.jpg` — clean release; module seated, nozzle bare.
12. `11_clear_z128.jpg` — bare-nozzle clearance (no +Z alarm).
13. `12_final_homed.jpg` — gantry homed, module seated, matches baseline.

## Camera caveat

The overhead camera has been bumped again since the 2026-07-28 sessions and
now sits **upside-down** (raw MJPEG frames are inverted). The committed
frames are rotated 180° to upright; anyone using the live stream at
`http://rpi-5-stream-cam-2wp0:8000/stream.mjpg` should expect an inverted
image until the mount is fixed. The view is still the side-on slot-8 angle,
so carry-height frames only show the module's lower portion at the top of
the frame — its x-position tracks the commanded gantry moves exactly.

## Robot end state

Clean: gantry homed, maintenance run deleted, module (with electronics)
seated on its base in slot 8, crown up, nozzle bare. Status note updated in
`/tmp/OT2_STATUS_READ_ME_FIRST.txt` on the RPi-5.
