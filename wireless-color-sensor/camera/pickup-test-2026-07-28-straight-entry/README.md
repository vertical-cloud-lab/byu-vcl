# Straight-in entry test — 2026-07-28 (slot 8, P300 GEN2, camera-metered)

Requested by @timothy-commins in PR #60: *"make sure that the tip fits
perfectly into the hole — every time you have gotten it in so far it has hit
the lip of the hole and slid in. We want it to go directly in."*

Driven over the tailnet (runner → Tailscale → RPi-5 → USB-Ethernet → OT-2
HTTP API), frames pulled from the RPi-5 side-view MJPEG stream between every
move. This session adds a **quantitative lateral-drag metric**: sub-pixel
phase correlation of the housing region between frames (sensitivity ≈ 0.02 mm
at 4.2–4.4 px/mm), so "hit the lip and slid in" is now a number, not a
judgement call.

## Result

| entry | alignment method | lateral drag of housing during insertion |
|---|---|---|
| first entry (Z→95.5) | camera-ray alignment on the post only | **≈ 0.95 mm** (dragged left; the wedge then gripped) |
| final entry (Z→95.7) | hang-self-centering + re-aligned X | **≈ 0.02 mm** — straight in, no lip contact |

The full cycle then completed cleanly: press at ~3 mm engagement → lift →
module carried mid-air at Z = 135 → reseat → `dropTipInPlace` release →
home. Maintenance run deleted; robot left parked and clean.

## Why entries kept hitting the lip

The side camera measures image-x, which conflates deck-X (4.23–4.40 px/mm)
with deck-Y depth (−1.49 px/mm parallax). Aligning the nozzle to the post in
the image only puts the nozzle on the **camera ray** through the bore axis —
any unknown Y error leaves a proportional X error (0.34 mm per mm of Y), and
deck-Y itself is essentially invisible (a 0.5 mm Y step moves the image
< 1 px). That residual lateral offset is what grazed the lip on every prior
session: the tapered bore then converts descent into sideways drag until the
part self-centers ("slid in").

## The fix — hang self-centering

1. Ray-align X on the post and enter once; the wedge grips (it did so at
   only ~2.9 mm engagement) and retracting **lifts the module**, which then
   hangs freely on the nozzle — at that moment the bore axis is *exactly*
   the nozzle axis, in both X and Y, with no camera involved.
2. Reseat the hanging module onto its base and eject. The bore is now at a
   known (X, Y). Re-measure the small offset the reseat/eject introduces
   (base-pocket registration shifted it 0.5 mm here) and correct X.
3. Re-enter at those coordinates. Measured drag this session: **0.02 mm**
   (48× better), i.e. the nozzle dropped straight down the bore without
   touching the lip.

## Working numbers (this session's frame, left-mount P300, no offset cal)

| quantity | value |
|---|---|
| Bore axis X / Y | **171.05 / 227.0 mm** |
| Mouth Z (fresh-measured) | ≈ 98.9 mm |
| Press Z | 95.7 mm (≈ 3.2 mm engagement — gripped and lifted the module) |
| Lift / carry Z | 135 mm |
| Eject | `dropTipInPlace` at the seated position, clean release |

Per the engagement-relative rule
(`../pickup-test-2026-07-28-repeat/README.md`), absolute Z values do not
survive re-homing — measure the mouth fresh each session. Note this grip
was achieved at only ~3 mm engagement, well short of the mouth − 7 mm
first-press rule; the press-fit at the current bore is snug enough that the
gentler press both grips and still ejects.

## Frames

1. `01_p300_above_slot8_z160.jpg` — safe approach over slot 8.
2. `02_hover_z105_above_mouth.jpg` — hover above the mouth; scale + mouth-Z measured.
3. `03_ray_aligned_x170p6.jpg` — nozzle aligned to the post on the camera ray (±0.02 mm in-image).
4. `04_first_entry_wedged_z95p5.jpg` — first entry: wedged with ~0.95 mm drag.
5. `05_diff_first_entry_drag_0p95mm.png` — difference image: every housing edge glows = the whole module moved.
6. `06_unintended_pickup_on_retract_z130.jpg` — retract lifted the module (grip at ~2.9 mm engagement).
7. `07_reseated_via_hang_centering.jpg` — hanging module lowered back onto its base.
8. `08_ejected_bare_nozzle.jpg` — released; bore now co-axial with the known nozzle position.
9. `09_recentered_x171p05.jpg` — re-aligned after the reseat's 0.5 mm registration shift.
10. `10_straight_in_full_insertion.jpg` — the verification entry, fully inserted.
11. `11_diff_straight_entry_drag_0p02mm.png` — difference image for the straight entry: housing edges quiet (bright areas are gantry + illumination change), phase-correlation drag ≈ 0.02 mm.
12. `12_grip_lift_z135_midair.jpg` — lift test: module hanging mid-air, clear of its base.
13. `13_released_bare_nozzle.jpg` — reseated and ejected; bare nozzle.
14. `14_final_homed.jpg` — gantry homed, deck restored.

## Follow-ups

- The eject clunk bumped the side-camera mount mid-session (scene shifted
  ~335 px). All measurements are in-frame relative, so nothing was lost, but
  a stiffer mount would help future sessions.
- For protocol use, the drag metric (phase correlation of the housing ROI
  between a pre-descent and post-press frame) is a cheap automatic
  "did it go in straight?" check — worth wiring into the cyclic test so a
  drifting fixture stops the run instead of grinding the lip for hours.
