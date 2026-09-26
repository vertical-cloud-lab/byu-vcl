# Same full cycle, now with a wire attached to the sensor — FAILED at the high lift (2026-07-31)

Requested by @timothy-commins in PR #60: *"I have now attached a wire to the
color sensor. Can you run the exact same test to see if the enclosure returns
back to its housing unit?"*

Answer: **no — it never got that far.** The grip and the 4 s hang were fine,
but the module came off the nozzle during the lift from z = 110 to the
z = 170 carry height, before the carry even started. Every stage after that
ran with a bare nozzle, so there was nothing to put back.

The recipe was reused **verbatim** from the 7-for-7 run in
[`pickup-test-2026-07-31-drop-xminus5`](../pickup-test-2026-07-31-drop-xminus5/README.md)
— no coordinate, height, speed, or press depth was changed. The only
difference between the two sessions is the wire.

## Recipe (unchanged from the 7-for-7 run)

| stage | coordinates / z |
|---|---|
| Pickup XY | (169.05, 225.0) |
| Descent ladder | z 150 → 120 → 105 → 101 → 99 |
| Straight entry | z = 95 |
| Press (eject-capable) | z = 91.5 (mouth − 7) |
| Lift test | z = 110, + 4 s dwell slip check |
| High lift / carry height | z = 170 |
| Carry | x 169.05 → 205 → 163.05, 8.5 mm segments @ 10 mm/s |
| Drop-off XY | (163.05, 225.0) — the −5 mm anti-tilt offset |
| Drop-off (eject) Z | 96.5 |

## Result

| stage | outcome |
|---|---|
| Descent ladder at (169.05, 225.0) | ✓ tip centred on the crown mouth (`02_z99_mouth.jpg`) |
| Straight entry z = 95 | ✓ clean insertion, no housing displacement |
| Press to z = 91.5 | ✓ gripped |
| Lift test z = 110 | ✓ module off its base, hanging (`05_lifttest_z110.jpg`) |
| 4 s dwell | ✓ **no slip** — the socket held the loaded module (`06_dwell_gripped.jpg`) |
| **High lift z = 110 → 170** | ✗ **module detached** (`07_highlift_z170_DETACHED.jpg`) |
| Carry x → 205 → 163.05 | — ran with a bare nozzle |
| Staged descent + eject | — nothing to release |
| Reseat | ✗ **module did not return to its housing; the pocket is empty** |

The run was ended cleanly: gantry homed, maintenance run deleted, nozzle bare.

## Where the failure happened, quantitatively

Two image regions were tracked across every frame, against the pre-run
baseline (mean absolute grey-level difference):

| frame | module pocket (slot 8) | lower-left deck |
|---|---|---|
| `03_entry_z95` | 2.7 | 12.9 |
| `04_press_z91p5` | 3.8 | 13.0 |
| `05_lifttest_z110` | 27.3 (module lifted off base) | 13.2 |
| `06_dwell_gripped` | 27.0 (still hanging) | 12.9 |
| **`07_highlift_z170`** | **40.3** | **42.1** |
| `08_carry_x205` | 40.5 | 41.9 |
| `11_final_homed` | 42.1 | 39.0 |

Both regions change in the **same** frame transition, 06 → 07, i.e. during the
single 60 mm Z move from the dwell position to carry height: the module
disappears from the nozzle *and* a thick black cable plus a white object
appear in the lower-left of the scene at the same instant.

**This is not a camera artefact.** Cross-correlating the static background
between frames 06 and 07 gives a shift of exactly **(0, 0) px**, and the
static regions match to under 2 grey levels (gantry pillar 0.7, base back
wall 1.8, deck front 1.1, panel corner 1.2). The camera did not move; the
scene did.

## Interpretation — the wire is a tether, and it pulled the module off

The press-fit itself is not the thing that failed. The socket gripped, took
the full loaded mass, and survived a 4 s static hang — exactly as in the
successful run. It let go only once the gantry started climbing, and the wire
appeared in frame in the very same move.

The most consistent reading of the frames is that the wire went **taut**
somewhere between z ≈ 110 and z ≈ 170 and stripped the module off the nozzle.
Supporting evidence:

* The failure is Z-triggered, not carry-triggered — it happened before any X
  motion, in a pure vertical move, which is exactly the direction a tether
  anchored below the module pulls against.
* A thick black cable (≈ 4–5 mm across at the deck scale) enters the frame in
  the same transition and is still lying diagonally across the lower-left deck
  in every later frame, including the final homed one.
* Nothing else in the cycle changed. The identical motion with the same loaded
  module and no wire succeeded seven times in a row.

`14_fallen_module_and_wire_closeup.png` shows the white object and the wire
that arrived in the lower-left, close to the lens and out of focus.

## What is needed before another attempt

The module is off its base and cannot be reseated remotely — **someone needs
to physically put the module back on its dock in slot 8** before this test can
be repeated. Please also check it for damage; it dropped from somewhere
between 20 and 80 mm above the deck with the electronics aboard.

Suggestions for the wire itself, in rough order of how cheap they are:

1. **Give it a service loop.** The nozzle lifts the module ~80 mm above the
   seated position (z 91.5 → 170). The wire needs at least that much slack,
   plus the 42 mm of X travel, measured *from where it is anchored*, before
   the gantry starts moving.
2. **Anchor it high, not low.** If the wire can be routed up and over — clipped
   to the gantry rail or to the tower near the pipette, so it travels *with*
   the head — the module never has to drag it. This is how the pipette's own
   cable is managed.
3. **Add strain relief on the enclosure.** A wire pulling on the module body
   applies a moment about the socket, which is the worst load case for a
   press-fit; the socket is only designed to resist axial pull-off (~2.2 N
   required, ~2.3 N predicted at bore 3.40 mm — very little margin against a
   sideways tug).
4. **Drop the carry height while a wire is attached.** z = 170 was chosen for
   clearance with no tether. If the wire has to stay anchored at deck level,
   the lowest carry height that still clears the base would reduce how far the
   tether has to stretch.

Worth saying plainly: the FEA margin on this socket is thin by design — 3.40 mm
was picked as the bore that *just* holds the 50 g package while still being
ejectable. It has essentially no reserve for a tether load. If the wire has to
stay attached during transport, that changes the requirement and the bore
should be re-chosen against the new (tether-inclusive) pull-off force rather
than against package weight alone.

## Frames

1. `00_baseline_seated.jpg` — before any motion; module seated on its base in slot 8, electronics aboard.
2. `01_hover_z170.jpg` — nozzle hovering over the pickup point.
3. `02_z99_mouth.jpg` — end of the descent ladder, tip centred on the crown mouth.
4. `03_entry_z95.jpg` — straight entry.
5. `04_press_z91p5.jpg` — eject-capable press (mouth − 7).
6. `05_lifttest_z110.jpg` — grip confirmed, module off its base.
7. `06_dwell_gripped.jpg` — after the 4 s hang: still gripped, no slip.
8. `07_highlift_z170_DETACHED.jpg` — **the failure frame**: nozzle bare, module gone, wire now across the lower-left.
9. `08_carry_x205_bare.jpg` — outbound carry, nothing aboard.
10. `09_return_x163_bare.jpg` — returned over the drop-off x, still bare.
11. `10_survey_z200.jpg` — gantry raised clear; slot-8 pocket empty.
12. `11_final_homed.jpg` — gantry homed, pocket still empty, run deleted.
13. `12_pocket_before_after.png` — slot-8 pocket, before vs after.
14. `13_detach_dwell_vs_highlift.png` — the 06 → 07 transition, the moment it let go.
15. `14_fallen_module_and_wire_closeup.png` — close-up of what arrived in the lower-left.

## Robot end state

Clean: gantry homed, maintenance run deleted, nozzle bare, no error state.
**The deck is not clean** — the module is off its dock somewhere front-left of
slot 8 with its wire across the deck, and needs a human to reset it.
