# Full-cycle attempt — 2026-07-28 (pickup ✓, lift ✓, carry ✗: module detached)

Continuation of the straight-entry work
(`../pickup-test-2026-07-28-straight-entry/`), requested by
@timothy-commins in PR #60: *"continue on your progress in picking up the
tip, moving it, then putting it back."* Driven over the tailnet (runner →
Tailscale → RPi-5 → USB-Ethernet → OT-2 HTTP API), side-view camera frame
checked between every move.

## Result

| stage | outcome |
|---|---|
| Straight entry at (171.05, 227.0) | ✓ **0.001 mm housing drag** at z=97 and z=95 — the stored hang-centered coordinates reproduced session-to-session with no re-alignment |
| Gentle press, z=94.7 (mouth − 4 mm) | ✓ gripped — no deep press needed |
| Lift test z=110 | ✓ crown rose ~79 px with the nozzle; base stayed (0 px) |
| High lift z=150 | ✓ module hanging cleanly mid-air |
| Sideways carry x=171 → 205 @ 30 mm/s | ✗ **module detached in transit** — nozzle bare on arrival |
| Reseat / eject | not reached |

The robot was homed, the maintenance run deleted, and the nozzle verified
bare on camera. **The module is off its base and needs a manual reseat**
before any further robot work near slot 8.

## Session numbers (left-mount P300, uncalibrated, this session's frame)

| quantity | value |
|---|---|
| Image scale (fresh cal, 20 mm X move) | 4.30 px/mm horizontal, 4.5 px/mm vertical |
| Mouth Z (fresh-measured per the engagement-relative rule) | **≈ 98.7 mm** (98.9 last session — 0.2 mm session drift) |
| Entry drag (phase correlation, housing ROI) | 0.001 mm at z=97; 0.001 mm at z=95 |
| Press | z=94.7 ≈ **4.0 mm engagement** — gripped on first try |
| Detach | between frames at x=171.05 and x=205, z=150, 30 mm/s commanded speed |

## Where the module went

The side camera cannot see most of the deck around slot 8 (the base
assembly occludes it). Differencing the baseline against the post-detach
deck survey (`11_change_overlay_vs_baseline.png`) shows (a) the module
cleanly gone from its seat, and (b) a new white mass appearing at image
columns ~1280–1420 — on the camera ray ≈ 55–60 mm right of the bore axis,
i.e. near deck x ≈ 205–230, y unknown. **No crown post is visible on top of
it, so the module is most likely tilted or on its side** — not
re-grabbable, and a blind approach risked crashing the nozzle into it, so
the session was ended cleanly instead (a person was visible in the
enclosure-glass reflection at the end of the session, so a manual reseat
was imminent anyway).

## Why it probably let go

- **The hold margin at this bore is thin by design.** The measured-OD FEA
  puts the 3.40 mm slitted socket at ~2.3 N axial hold vs ~2.2 N required
  (SF 3, static). A 34 mm point-to-point move at default gantry
  acceleration adds a lateral inertial jerk at both ends of the move that
  the static margin does not cover.
- **Engagement was the gentlest yet.** 4.0 mm (mouth − 4) grips for a
  vertical lift, but prior successful carries ran deeper: ~9 mm
  (2026-07-28 repeat) and ~11.5 mm (deep-press). The straight-entry
  session's carry at ~3.2 mm engagement survived, but only barely
  different, and this socket has now been through dozens of insert/eject
  cycles across sessions — PETG spring fingers relax with wear, so
  yesterday's marginal grip can be today's drop.

## Rules to add for future carry attempts

1. **Vertical lift test ≠ carry-worthiness.** After the mouth − 4 lift
   test, re-press to **mouth − 6 or − 7** (still above the mouth − 9
   floor) before any lateral transport.
2. **Slow the carry**: ≤ 10 mm/s laterally with the module aboard, and
   break long traverses into short segments with a camera frame between —
   the drop is then detected within seconds and localized to a ~10 mm
   window instead of a 34 mm one.
3. **Grip-presence check is cheap**: one frame + the crown-top row test
   (white crown at the nozzle tip vs bare black taper) after every
   segment.
4. When the wear question comes up (@timothy-commins): caliper the crown
   bore mouth and compare against the printed 3.40 mm — dozens of cycles
   on this one socket may have opened it up; the round-2 3.38–3.44 mm
   sweep parts would restore a fresh grip surface.

## Frames

1. `01_baseline_module_seated_slot8.jpg` — module + crown seated on its base.
2. `02_descent_z105.jpg` — approach; scale calibrated (86 px per 20 mm).
3. `03_z101_mouth_measured_98p7.jpg` — tip 2.3 mm above crown → mouth ≈ 98.7.
4. `04_straight_entry_z95_drag_0p00mm.jpg` — inserted, rim both sides, zero drag.
5. `05_gentle_press_z94p7_mouth_minus_4.jpg` — the 4 mm-engagement press.
6. `06_lifttest_z110_grip_confirmed.jpg` — crown follows the nozzle up.
7. `07_highlift_z150_module_hanging.jpg` — module dangling mid-air, clear of base.
8. `08_carry_x205_nozzle_bare_module_fell.jpg` — arrival at x=205: bare nozzle.
9. `09_return_x171_still_bare.jpg` — return leg, still bare.
10. `10_deck_survey_module_not_visible.jpg` — gantry moved clear; module occluded.
11. `11_change_overlay_vs_baseline.png` — red = changed vs baseline: module gone
    from seat; new white mass right of the base.
12. `12_slot8_before_after.png` — top: baseline; bottom: after (module missing).
13. `13_final_homed_camera_bumped.jpg` — homed and parked; the side camera was
    physically bumped/moved near session end (view shifted), and a person is
    visible in reflection — deck state after this frame is unknown.

Robot left clean: gantry homed, maintenance run deleted, status note updated in
`/tmp/OT2_STATUS_READ_ME_FIRST.txt` on the RPi-5 warning the next session not
to descend below z=150 near slot 8/9 until the module is reseated.
