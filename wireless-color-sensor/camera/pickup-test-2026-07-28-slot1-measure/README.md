# Pick up → carry to slot 1 (measure gesture) → return home — SUCCESS (2026-07-28)

Requested by @timothy-commins in PR #60: *"this test seems perfect. can you
pick up the tip, move it over to slot 1 as if it were to measure color and
then move it back to its home base?"*

This extends the proven **x −1 mm full-cycle recipe**
(`../pickup-test-2026-07-28-x-minus-1/`, 4-for-4) with a real deck traverse:
instead of the short slot-8-internal carry, the gripped module is routed all
the way to **slot 1** (front-left), held there as if taking a color reading,
then carried back to its **slot-8** home base and re-seated.

Driven over the tailnet (runner → Tailscale → RPi-5 → USB-Ethernet → OT-2
HTTP API), one maintenance run, camera frame checked at every key stage.

## Recipe

| stage | coordinates / z |
|---|---|
| Pickup XY | (169.05, 225.0) — unchanged from the x −1 recipe |
| Descent ladder | z 150 → 120 → 105 → 101 → 99 |
| Straight entry | z = 95 |
| Press (eject-capable) | z = 91.5 (mouth − 7) |
| Lift test | z = 110 |
| High lift / carry height | z = 170 |
| **Slot-1 hover target** | **(36.55, 44.0)** at z = 170 |
| Carry | 8.5 mm segments @ 10 mm/s (both directions) |
| Drop-off XY | (168.05, 225.0) |
| Drop-off (eject) Z | 96.5 (foot ~5 mm above seat) |
| Post-eject clearance | z = 128 (bare-P300 +Z rule) |

The slot-1 target is the slot-8 crown coordinate translated by the standard
OT-2 slot pitch (−132.5 mm in X for one column left, −181.0 mm in Y for two
rows forward), i.e. the module hovers roughly centered over slot 1.

## Result — full slot-8 → slot-1 → slot-8 cycle succeeded

| stage | outcome |
|---|---|
| Descent ladder at (169.05, 225.0) | ✓ tip centred at the crown mouth |
| Straight entry z=95 | ✓ clean insertion, no housing displacement |
| Press to z=91.5 (mouth − 7) | ✓ gripped |
| Lift test z=110 / high lift z=170 | ✓ module off its base, hanging cleanly |
| Carry to slot 1 (36.55, 44.0), ~224 mm incl. big −Y move | ✓ module aboard the whole way |
| Hover 3 s over slot 1 (measure gesture) | ✓ module held, no slip |
| Carry back to drop-off (168.05, 225.0) | ✓ still aboard |
| Descend z=96.5 | ✓ hovering, foot ~5 mm above seat |
| Mid-air eject (`dropTipInPlace`) | ✓ clean release; module reseated upright |
| Clearance z=128 → home | ✓ no +Z alarm |

Notes:

- **New vs every prior full cycle:** the carry now includes a large **Y**
  traverse (−181 mm) plus the −132.5 mm X, ~224 mm each way, versus the
  prior x-only ~37 mm slot-8-internal carries. The press-fit grip held the
  full round trip at 10 mm/s with no re-teaching — the recipe is now
  **5-for-5**.
- Slot 1 was reachable by the left-mount P300 at (36.55, 44.0); the
  `moveToCoordinates` commands all returned `succeeded` (no out-of-range).
- The module reseated on the base pocket exactly as in the short-carry cycles.

## Frames

1. `00_baseline.jpg` — module seated, crown up, nozzle parked.
2. `01_z99_mouth.jpg` — end of descent ladder, tip at the crown mouth.
3. `02_entry_z95.jpg` — straight entry, no housing shift.
4. `03_press_z91p5.jpg` — eject-capable press (mouth − 7).
5. `04_lifttest_z110.jpg` — grip confirmed, module off its base.
6. `05_highlift_z170.jpg` — hanging at carry height.
7. `06_over_slot1.jpg` — head departed to the front-left toward slot 1
   (the module is off the side-on camera's frame; the empty base is at
   bottom-left and the gantry column has left centre-frame).
8. `07_slot1_measuring.jpg` — held over slot 1, the "measure color" gesture.
9. `08_return_slot8.jpg` — returned over the slot-8 drop-off, still aboard.
10. `09_predrop_z96p5.jpg` — hovering at the low release height.
11. `10_after_eject.jpg` — clean release; module seated upright, nozzle bare.
12. `11_clear_z128.jpg` — bare-nozzle clearance (no +Z alarm).
13. `12_final_homed.jpg` — gantry homed, module seated, matches baseline.

## Camera caveat

The overhead camera is still mis-aimed from the 2026-07-28 bump (side-on
view of slot 8), so **slot 1 is off-frame to the front-left**. The slot-1
frames therefore show the head having left the frame rather than the module
sitting over slot 1 — expected, and consistent with a successful traverse.
Re-aiming the camera (or adding a second view of the front-left deck) would
let a future run visually confirm the module positioned over slot 1. The
robot API reported every move `succeeded`, and the pickup/return/reseat
frames confirm the grip survived the full round trip.

## Robot end state

Clean: gantry homed, maintenance run deleted, module seated on its base in
slot 8, crown up, nozzle bare. Status note updated in
`/tmp/OT2_STATUS_READ_ME_FIRST.txt` on the RPi-5.
