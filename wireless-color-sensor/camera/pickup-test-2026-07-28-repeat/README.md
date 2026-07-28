# Housing pickup test — 2026-07-28 (repeat, slot 8, P300 GEN2, camera-confirmed)

Second camera-guided pickup of the sensor housing, requested by
@timothy-commins in PR #60 ("you can continue but if the tip runs into
something stop pushing. it will break the ot-2."). Driven over the tailnet
(runner → Tailscale → RPi-5 → USB-Ethernet → OT-2 HTTP API), frames pulled
from the RPi-5 side-view MJPEG stream between every move.

## Method — small steps, hard Z floor

To honor the "stop pushing if it hits something" constraint, every descent was
done in small increments (160 → 105 → 97 → 93 → 90.5 mm) with a camera frame
checked after each move, watching for any housing shift that would signal a
rim collision. A hard **Z floor of 90.5 mm** (the 2026-07-28 full-press depth,
~9 mm engagement) was enforced in the control helper so the nozzle could never
press deeper than the previously-verified safe depth.

Coordinates reused from 2026-07-28: crown/socket axis **X = 171**, **Y = 227**
(deck coords, left-mount P300 nozzle tip); mouth Z ≈ 99.5.

## Result — PICKUP + CARRY CONFIRMED, then paused for human intervention

- Entry into the socket was clean at Z = 97 and 93 with **zero housing shift**.
- At the Z = 90.5 full press (~9 mm engagement) and lift to Z = 150, the
  press-fit **gripped and lifted the entire enclosure clear of its base**
  (`06_lift_gripped_z150.jpg`).
- A sideways carry to X = 205 (+34 mm) kept the enclosure **hanging from the
  nozzle, clear of the base** (`07_sideways_carry_x205_hanging.jpg`) —
  reproducing the 2026-07-28 pickup.
- During the return/reseat, **a person's hand entered the workspace and
  removed the base holder** (`08_base_removed_by_hand_paused.jpg`). All robot
  motion was stopped at that point: the housing was left gripped and the robot
  held position rather than ejecting the part onto a bare deck or moving while
  someone was reaching in.
- The person then **pulled the housing off the nozzle by hand and reset the
  whole assembly back into slot 8**. With the nozzle confirmed bare and the
  deck restored, the gantry was homed and the maintenance run deleted, leaving
  the robot in a clean parked state (`09_final_homed_deck_restored.jpg`).

## Frames

1. `01_p300_safe_over_slot8_z160.jpg` — P300 at safe height over the socket.
2. `02_aligned_over_socket_z105.jpg` — nozzle centered on the white socket mouth.
3. `03_clean_entry_z97.jpg` — clean entry, ~2.5 mm engaged, housing steady.
4. `04_inserted_z93.jpg` — ~6.5 mm engaged, housing steady.
5. `05_full_press_z90p5.jpg` — full press at the Z = 90.5 floor (~9 mm).
6. `06_lift_gripped_z150.jpg` — lift: enclosure rides the nozzle, off its base.
7. `07_sideways_carry_x205_hanging.jpg` — enclosure carried +34 mm, hanging.
8. `08_base_removed_by_hand_paused.jpg` — hand removed the base; motion stopped.
9. `09_final_homed_deck_restored.jpg` — bare nozzle homed, housing back in slot 8.

## Notes / follow-ups

- The P300 still has **no stored pipette-offset calibration** (only the P20 is
  calibrated), so these X/Y/Z are in the P300's uncalibrated frame — the same
  frame as the 2026-07-28 numbers, and they reproduced exactly.
- Ejection was **not** exercised this run because the base was removed
  mid-cycle; the 2026-07-28 run already confirmed `dropTipInPlace` releases the
  housing cleanly at this ~9 mm engagement.
- The robot was left holding the gripped housing at (171, 227, 90.5) pending
  direction on whether to eject, reseat (base back in slot 8), or park/home.

## Press-depth correction (2026-07-28, @timothy-commins)

Tim's feedback after these runs: **"you are pushing down too much."** The
Z = 90.5 "full press" (~9 mm engagement) used here and on 2026-07-28 — and
carried between sessions as the verified-safe floor — is **too deep** and must
not be reused. The bore tapers at 1.589° half-angle, so once the nozzle wedges,
every additional commanded mm of Z converts almost entirely into downward force
on the housing, its base, and the OT-2 Z-axis.

New rule for any future camera-guided press (P300 frame, mouth Z ≈ 99.5):

1. Press first to **Z = 93.5 (~6 mm engagement)** and do a lift test.
2. Only if the lift comes up bare, step **0.5 mm deeper at a time**, with a
   camera frame + lift test between steps.
3. **Hard floor Z = 92.0 (~7.5 mm)** — do not go deeper without explicit human
   approval in the PR thread. Z = 90.5 is retired.

The array protocols' `tipOverlap` was likewise reduced 8.0 → 6.0 mm (8.0 was
the full socket depth, i.e. guaranteed bottom-out before the press increment
is even added).
</content>
</invoke>
