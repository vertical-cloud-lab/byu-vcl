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

Tim's live feedback across today's sessions bounds the press from both sides:
first **"you need to pick it up much more"** (the 19:42 session's nozzle was
hanging in mid-air at a stale Z, never touching the crown), then — after the
takeover session pressed to z = 86, **~11.5 mm engagement** (see
`../pickup-test-2026-07-28-deep-press/`) — **"you are pushing down too
much."** The bore tapers at 1.589° half-angle, so once the nozzle wedges,
every additional commanded mm of Z converts almost entirely into downward
force on the housing, its base, and the OT-2 Z-axis.

Because the P300 has no stored offset calibration, **absolute Z values do not
survive between sessions** (the mouth measured ≈ 99.5 this morning and ≈ 97.5
after the next home — a 2 mm shift). The rule must be engagement-relative:

1. **Measure the mouth Z fresh each session** (camera-step the descent until
   the tip meets the crown; never reuse a prior session's absolute Z).
2. First press to **mouth − 7 mm** and do a lift test.
3. Only if the lift comes up bare, step **0.5–1 mm deeper at a time**, with a
   camera frame + lift test between steps.
4. **Hard floor: mouth − 9 mm** (the depth that gripped this morning) — do
   not go deeper without explicit human approval in the PR thread. The
   ~11.5 mm deep press is retired as a target; treat it only as an upper
   bound showing ejection still works there.

The OT-2 protocols' `tipOverlap` was likewise reduced 8.0 → 6.0 mm (8.0 was
the full socket depth, i.e. guaranteed bottom-out before the press increment
is even added).
</content>
</invoke>
