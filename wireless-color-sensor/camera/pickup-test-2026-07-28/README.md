# Housing pickup test — 2026-07-28 (slot 8, P300 GEN2, camera-confirmed)

Remote camera-guided pickup of the sensor housing, driven over the tailnet
(RPi-5 → USB-Ethernet → OT-2 HTTP API) with frames pulled from the RPi-5
side-view MJPEG stream between every move. Requested by @timothy-commins in
PR #60 ("the color sensor is in slot 8 … use the camera to confirm if it has
been picked up or not").

## Result — PICKUP CONFIRMED, and ejection works

The **P300 GEN2** nozzle (Tim swapped it in for the P20 earlier today) was
pressed ~9 mm into the housing's Ø7.5 mm swap-in tip
(`fake_tip_enclosure_bore`, printed white). On lift the press-fit **gripped
and carried the entire housing**: it rose with the gantry, traveled +34 mm
in X, and hung mid-air well clear of the deck
(`10_confirmed_hanging_midair.jpg`). The housing was then re-seated in
slot 8 and — notably — **`dropTipInPlace` ejected it cleanly**: the P300's
ejector sleeve pushes on the Ø10.5 mm crown rim, so at ~9 mm engagement the
7.5 mm interface *can* be released by the robot (the earlier "can't eject"
concern applies when the bore swallows the sleeve on a deeper press).

## Measured position (deck coordinates, left-mount P300 nozzle tip)

| quantity | value |
|---|---|
| Crown (socket) axis X | **171.0 mm** |
| Crown axis Y | **227.0 mm** |
| Crown top (mouth) Z | **≈ 99.5 mm** |
| Full-press Z used | **90.5 mm** (~9 mm engagement) |
| Eject | `dropTipInPlace` at the seated position |

**These supersede the 2026-07-27 P20 numbers (171, 233, mouth 113) for the
P300.** The robot has *no stored pipette-offset calibration for the P300*
(`GET /calibration/pipette_offset` lists only the P20), so its coordinate
frame is shifted ≈ +6 mm in Y and ≈ +13 mm in Z versus the P20-calibrated
frame; the mouth Z also reflects the new shorter swap-in tip. Running
pipette-offset calibration for the P300 in the Opentrons app would make
protocol coordinates portable again.

## Method notes

- The overhead camera was repositioned to a **side view** since yesterday —
  actually ideal for confirming a lift. In-frame comparisons (nozzle vs
  crown in the same shot) were used throughout because the camera mount
  drifts a few px between frames.
- A side view hides deck-Y (depth) errors: at the stale coordinates the
  nozzle looked aligned but slid *behind* the crown
  (`03_missed_behind_crown_z95.jpg`, crown rim occluding the nozzle).
  Y was recovered by a parallax calibration (±10 mm Y moves ≈ ∓15 px
  image-x) plus an occlusion bisection: behind at y=233, in front at y=224,
  centered at **y=227**.
- All moves were slow (2–6 mm/s) with a frame check at each step; insertion
  was verified at 3 depths before the full press, and the housing never
  shifted during entry.

## Frames

1. `01_p300_above_slot8_z160.jpg` — P300 at safe height over slot 8.
2. `02_stale_x171_looks_aligned.jpg` — stale coords *look* aligned in X…
3. `03_missed_behind_crown_z95.jpg` — …but the nozzle slides behind the
   crown (rim occludes nozzle = too far in Y).
4. `04_y224_in_front_of_crown.jpg` — over-corrected probe: nozzle in front.
5. `05_aligned_y227_at_mouth.jpg` — centered on the bore at (171, 227).
6. `06_inserted_6mm.jpg` — clean entry, white rim visible both sides.
7. `07_full_press_9mm.jpg` — full press, z = 90.5.
8. `08_lift_z115.jpg` — lift begins; crown rides the nozzle.
9. `09_sideways_carry_x205.jpg` — housing travels +34 mm in X with gantry.
10. `10_confirmed_hanging_midair.jpg` — **the confirmation shot**: housing
    dangling from the nozzle, deck empty below.
11. `11_ejected_reseated_slot8.jpg` — after reseat + `dropTipInPlace`:
    bare nozzle above, housing back in slot 8.
12. `12_final_homed.jpg` — gantry homed, deck restored.

## Follow-ups

- Repeat the press with >9 mm engagement to find the depth where the bore
  reaches the ejector sleeve and ejection starts to fail (that bounds the
  safe cyclic-loading press depth for `protocol_cyclic_housing.py`).
- Calibrate the P300 pipette offset, then re-express these coordinates.
- The pickup was of the housing Tim loaded in slot 8 (lightweight holder +
  white swap-in tip). Weigh the assembled unit to update the FEA hold margin.

## Addendum — a second, concurrent session (19:20–20:10 UTC)

Tim's "try again" comment launched a second agent session while the first
(19:05) job was still alive and mid-test — both drove the robot at the same
time, each interpreting the other's motions as a human in the lab. Two
lessons and one useful datapoint came out of it:

- **Off-center presses don't grip.** The second session pressed at the stale
  Y = 233 (6 mm behind the calibrated Y = 227 crown axis): three presses 9,
  14 and 18 mm past mouth height at 5–10 mm/s all lifted bare, and from the
  camera's blind (depth) axis each descent *looked* like a clean entry
  (`13_addendum_stale_y233_press_sequence.png`,
  `14_addendum_stale_y233_deep_press_bare_lift.png`). Together with the main
  test this brackets the press-fit's lateral tolerance: centered ⇒ grips,
  6 mm off ⇒ misses the bore entirely while looking plausible on camera.
  Always verify Y by occlusion/parallax before trusting an "insertion".
- **Only one maintenance run can exist robot-wide.** Each session silently
  deleted the other's run (`RunNotFound` mid-sequence); a stalled/obstructed
  `moveToCoordinates` still reports `succeeded` and corrupts the Z reference
  until the next home. Treat "no image change after a commanded move" as a
  stall-or-stolen-run signal, and never start a second robot session while a
  previous agent job may still be running.
