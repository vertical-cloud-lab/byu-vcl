# The furnace latch, unclamped and clamped; the powder container off and on (PR #353, #303)

Sterling on PR #318 (2026-11-19): "it doesn't seem like you actually used the heat chamber latch correctly (i.e., actually
clamping it down and then unclamping it)" and "removing of the dispense container". Two clips:

| Clip | Script | What |
| --- | --- | --- |
| `atom_latch` | [`atom_latch.py`](../atom_latch.py), tools in [`atom_latch_tools.py`](../atom_latch_tools.py) | unclamping after a run, clamping before the next, the leak check |
| `atom_container` | [`atom_container.py`](../atom_container.py) | brushing the powder down, the container off onto MiR250 1, a clean one on |

Sources: DAL's SOP checklist (`253_atomizer-sop.md`), the detailed SOP with video times (`178_sop.md`), the manual notes
(`178_manual.md`), and the third pass of the model (notes/repowder_refine.md, "Third pass", T4 5:29.5-5:41). Loads and
the MiR stability sums are chapter 2's (`alloy_atomize.py`: `LATCH_F`, `PRESS_F`, `LID_KNOB_N`, `stability()`).

## What the model's latch could not do, and what the clip draws instead

FCL on the model's own meshes (`python3 atom_latch_tools.py`, bolt back) found three faults in the third-pass latch:

1. **The lever runs 14 mm above its pivot.** Opened past ~30 deg that end swings into the base plate: 48 mm deep at 90 deg,
   30 mm at 150 deg. So the 150 deg the footage shows (T4 5:32-5:34) was impossible as drawn.
2. **The loop's legs are at x = +-21.5 mm**, inside the lever's flanges and on top of the base's side flanges (+-19.5..22): they
   pass through the base's flanges and graze the pivot pin even shut.
3. **The keeper's ledge is above the cross bar** (`hook` is 2 mm under it), so the loop would pull the bar away from it. A draw
   latch pulls the lid down only if the bar bears down on a ledge under it.

The clip removes those four meshes (lever, loop, keeper, pin) and draws them again on the model's own joints, so the pivots
and the joint values are unchanged (`atom_latch_tools.latch_meshes()`; ours): the lever ends at its pivot in a rounded
knuckle and its web stops 12 mm under the pivot; its free end sits 2 mm over the hold-down foot; the loop's legs run outside
the lever's flanges (x +-30.5), their pins through the flanges; the keeper has its ledge under the bar and a 3 mm lip in
front; the pin is 53 mm long; the lever's flanges have holes for the bolt's rod, so the bolt in really locks the lever. With
these, the latch sweeps clear from shut to 150 deg with the loop riding, and from shut to 150 deg with the loop lying on the
lever (FCL, every 10 deg). The only contacts left are the loop's bar on the keeper's ledge while taut, up to the 0.6 mm draw:
the squeeze itself. model.py should take these parts.

## How the loop moves (worked out, not seen frame by frame)

The over-centre sums are the model's (`M.latch_toggle()`): the loop's pivot is 4 mm inboard of and 16 mm under the lever's,
so as the lever opens the pivot-to-hook distance first grows (dead centre at 18 deg, +0.60 mm) and then shrinks. The clip
sets the loop 0.30 mm short of the shut distance (`PRELOAD`, ours: "just tight enough to seal", 178_sop Furnace 9), so the
loop is taut from shut to 41 deg. Past that it is slack, and since a rigid loop cannot keep its bar on the hook while its
pivot comes closer, the bar rides up the keeper's plate (by 85 deg it clears the hook's 3.4 mm lip; at 150 deg it would sit
26 mm up the plate). Let back to 41.5 deg, the lever rests on the slack loop, its bar on the hook. Swung out over the lever's
top (the loop's legs run outside the lever's flanges, so it can), the loop lies over the lever's web; folded down, the lever
has the loop hanging over it, as in T4 5:08 and 5:29.5 ("it dangles, hanging down over the lever").

The pull at the lever's free end: the loop's tension taken proportional to the squeeze past its set length, times its line's
moment arm about the pivot, over the 133 mm from the pivot to where the 2F-85 holds it; scaled so its peak is chapter 2's
100 N (Kipp K0080 cover latches: 100 / 150 / 200 N for 2 / 4 / 7 kN held). It peaks a few degrees before dead centre and is
zero at it; past it the loop pulls the lever shut. That shape is geometry; the 100 N is an estimate (200 N if stiff).

## The machine as drawn now (commit e3b1428)

The lid assembly is turned 90 deg about the furnace axis: hinged on the **left** (DAL PR 189 measured it there), the knob
and the latch on the housing's **right** face, the pneumatic bolt running back into the blue cabinet. #327's back hinge swung
the lid into the cabinet: this clip's first audit found the hinge leaf 25 mm into it 5 deg after opening, and the cameras
stream found the same. The latch above is worked out in the lid's own frame (`M.latch_geom(turned=False)`, joints `JL`/`JO`
in atom_latch_tools) and carried onto the machine with `M.LID_TURN_T`; the model's own joints already answer in the turned
frame. MiR250 1 now works the latch from the right of the furnace (its spot is picked in the clip from six candidates: the
one whose arm follows the lever and the loop with the fewest collisions); MiR250 2 stays at the front left for the palm
press and the lid, which opens up and over to the left, 105 deg.

## Unclamping (clip `atom_latch`, steps 1-7)

| # | Step | Who | Source |
| --- | --- | --- | --- |
| 1 | Below 400 C: Melting Pressure off, Pressure Control off, Vent Valve | the machine (HMI) | DAL SOP Cooldown 2-3; 178_sop After a run |
| 2 | At atmosphere the pneumatic bolt goes back and frees the lever | the machine | Kalicki (install call 22:04): it locks "once you change the pressure"; the release on venting is our reading |
| 3 | Closed fingertips press the lid's top, ~100 N, so it can't jump | arm 2 | T4 5:17-5:24 (a palm on the lid); chapter 2's `press_pose`, `PRESS_AT` |
| 4 | Pads on the lever's two side flanges 133 mm under the pivot; out and up about the top pivot, through dead centre (18 deg) to 60 deg; the loop goes slack at 41 deg | arm 1 | T4 5:29.5-5:41 read backwards |
| 5 | The lever let back to 41.5 deg, where it rests on the slack loop (its bar on the hook again), and let go | arm 1 | ours: so one hand can do the rest |
| 6 | The loop taken by its two legs; lifting it raises the lever to 85 deg on the loop's pin, so the bar rides up the plate over the hook's lip; then the loop swung out over the lever's top while the lever folds down with it | arm 1 | T4 5:30-5:35 (the hand lifts the loop off), 5:08 (the loop hanging over the folded lever) |
| 7 | The lid swung up and over to the left by its knob, 105 deg about the left hinge, and let go | arm 2 | T4 5:14.5-5:16.5 (one rotation, no lift or slide); DAL PR 189 (hinge on the left) |

The footage has the lever stood up to ~150 deg (T4 5:32-5:34) before the loop comes off. With one 2F-85 per arm and the latch
now on the right face, out of arm 2's reach, the clip does it the one-handed way: the lever only goes past dead centre and the
loop's slack point, and the loop does the rest. The over-centre physics is the same.

## Clamping (clip `atom_latch`, steps 8-9)

| # | Step | Who | Source |
| --- | --- | --- | --- |
| 1 | IPA on the seal and the face it meets; the lid down by its knob | arm 2 (IPA: not shown) | DAL SOP Loading 8; 178_sop Furnace 9 (rub flakes off the lid faces, T8 11:26) |
| 2 | The loop taken by its legs and swung back over the lever's top onto the keeper's plate, raising the lever to 85 deg; lowered, the bar slides down onto the hook and the lever rests at 41.5 deg | arm 1 | T4 5:30-5:35 ("hook the loop on") |
| 3 | Closed fingertips on the lid's top again | arm 2 | T4 5:17-5:24 |
| 4 | The lever's free end swung down: through dead centre (+0.60 mm squeeze, the pull's peak) and flat onto the base | arm 1 | T4 5:37.5-5:41 |
| 5 | Vacuum Pump and Vacuum Valve: as the pressure changes the bolt comes in and locks the lever | the machine | DAL SOP Cold purge 7; Kalicki 22:04 |
| 6 | The leak check: about -850 mbar, holding, no hiss | the machine; read off the HMI | DAL SOP Loading 8 ("adjust the latch until nothing hisses"), troubleshooting ("if the furnace can't reach -0.85 bar or the lid hisses, check the sealing rod, the seals and the latch") |

**The adjuster.** "Secure the latch just tight enough to seal; if it hisses, loosen, adjust the latch and retighten" (178_sop
Furnace 9; T4 5:17, T8 9:09). Neither the model nor the footage shows how the latch is adjusted. The clip's loop has lock nuts
on its legs (ours, assumed: a threaded loop, half a turn a step) and the check the machine allows is the pump-down holding at
about -850 mbar. If it fails, the robot would vent, open the latch, turn the nuts and close it again: not animated.

**The seam inset** is a schematic of the O-ring between the lid and the body, squeezed by the preload plus the draw; the
O-ring's 5 mm section is assumed (the model's `oring` part is not measured).

## Forces and the MiRs' margins (chapter 2's `stability()`, 131 kg plates, at the clip's poses)

| Load | Where | Tips at | Slides at |
| --- | --- | --- | --- |
| 100 N (200 if stiff) on the lever, either way | MiR250 1, arm 1 at its grasp on the lever | 504 N (pulling open), 521 N (pushing shut) | 951 N |
| ~100 N press down on the lid | MiR250 2, arm 2 | 617 N | 2087 N |
| 58 N, the lid's weight on the knob | MiR250 1, arm 1 | 2401 N | does not slide |

Both have at least 2.5 times the stiff latch's 200 N. The numbers without the ballast plates are in
`out/atom/atom_latch_stability.json` (written by the render).

## The container (clip `atom_container`)

**What the rendered clip shows: steps 1-5 below** (the state, the brushing, the dust settling, the valve shut). Steps 6-13
are written in `atom_container.py` (`ATOM_CONTAINER_FULL=1` runs them) but their two-arm moves still collide: its audit at
01:42 found 994 frames in collision in those steps (arm 2's forearm folding onto its own MiR250 with the fork under the
container, arm 1 and arm 2 crowding the clamp). Not rendered; the next session should move MiR250 2 (the fork's arm) and
re-plan them. The view port's glass is not brushed either: from the door the long brush's grip meets the ultrasonic stack on
the open door.

| # | Step | Who | Source |
| --- | --- | --- | --- |
| 1 | Vented, cold; the door's two clamps swung off, then the door opened; paper under the opening | (done before the clip) | 178_sop After a run (T2 39:00, T5 77:17); DAL SOP Powder Collection 1 |
| 2 | An anti-static brush taken from MiR250 1's rest | arm 1 | AMAZEMET's set of anti-static brushes (178_manual); this long-handled one is ours |
| 3 | The cone (the 45 deg underside) brushed down to the outlet, the catch bowl brushed round in a circle, the view port's glass in a circle | arm 1 | DAL SOP Powder Collection 2; 178_sop After a run 2 (T2 43:37, T4 08:47) |
| 4 | The dust settles, 60 s (time-lapse) | | 178_sop After a run 2 (T2 50:32) |
| 5 | The container's valve shut: its lever pulled down a quarter turn | arm 1 | 178_sop After a run 3 ("pull down and move", T2 53:39); the direction is ours |
| 6 | A fork slid under the container and lifted 0.5 mm onto it: it holds the weight | arm 2 | 178_sop Chamber 1 ("one holding the weight while the other closes the clamp") |
| 7 | The flange clamp opened: 1.5 turns of its T-handle, the bolt slid out of the back lug, the front half swung open 75 deg on its hinge | arm 1 | the clamp's type is not in the footage (T5 03:44-04:48 only shows it finger-tightened): ours |
| 8 | The container lowered out of the clamp, level, carried to MiR250 1's cradle | arm 2 | |
| 9 | A blank cap on its top flange | arm 1 | ours; the shut valve keeps the argon in its bottom (178_sop After a run 3, T6 00:03) |
| 10 | A clean container, a fresh splash disc in its top flange, taken from MiR250 2's cradle and lifted under the outlet | arm 2 | 178_sop Chamber 1 (T5 02:21, 02:47) |
| 11 | The clamp swung shut, the bolt in, finger-tight | arm 1 | 178_sop Chamber 1 ("finger-tightening the flange") |
| 12 | Its valve opened | arm 1 | DAL SOP Powder Collection 10 ("reattach the cup with its valve open") |
| 13 | The fork lowered 2 mm and slid out | arm 2 | |

**Why a fork.** The container is 130 mm across and the 2F-85 opens to 85 mm. Chapter 2 carried it by the red lever on its
valve, which is the valve's handle: hanging 4-6 kg off it loads the valve's stem, and it is what step 5 turns. The fork's
prongs pass under its flat bottom; the cradles have rails it stands on and a slot the prongs pass through (ours).

**Mass.** The model's container, valve tube, lever and splash disc are 538 cm3 drawn; in stainless (7.9 g/cm3) that is about
4.3 kg empty (`out/atom/atom_container_mass.json`, written by the render). A real ball valve weighs more than the drawn tube,
so this is a floor: "it is heavier than it looks" (178_sop Chamber 1). Powder: 0.14 kg for chapter 2's four cups, about 0.5 kg
for a 225 cm3 crucible of Al as filled on Oct 27, about 1.6 kg of NAB bronze. With the fork (~0.9 kg) that is 5.3-6.8 kg: well
inside the UR10e's 12.5 kg, **but over the Robotiq 2F-85's rated payload (5 kg form-fit, 4.7-5 kg friction at a 0.3-0.4 friction coefficient; Robotiq's product page and product sheet) with a full crucible's powder**. For a heavy run
the fork would want a form-fit lock to the gripper's fingers, or both arms under it.

**Which valve.** The model has two: the chamber's (green handle, `valve_handle`, in the fixed group "chamber") and the
container's own (red lever, `container_handle`). The SOP names one, "the container valve", whose job is to keep the argon in the
container's bottom; that is the container's own, and the clip closes that one. Whether the lab also shuts the chamber's valve
before unclamping is an open question below.

**The clamp.** Drawn here as two half-rings hinged at the right and joined at the left by a T-handle bolt, replacing the
model's two halves that slid straight apart (ours, assumed). The lab should say what the real clamp is (a hinged KF/ISO clamp
with a wing nut, a chain clamp, a V-band).

## Audit results and what is still wrong (2026-11-19, the rendered scripts)

- **atom_latch** (the turned lid, one-armed latch): LATCH_AUDIT_RESULT. Before the lid was turned, the same clip with the
  latch on the front face audited at **0 of 1254 frames** in collision and 0 mover contacts (01:29). After the port the lever's
  moves are clear (its grasp now comes from above and outside: under the turned latch is the chamber's top plate), but **the
  loop's moves are not**: swinging the loop over the lever's top while holding its legs turns the gripper ~170 deg with it, and
  the forearm sweeps into the furnace body, the chamber and the blue cabinet (the clip's branch search scored 194-210 hits on
  that path at every MiR250 1 spot tried). The fix, not made for lack of time: lift the bar off the hook and let the loop fall
  onto the lever's web (what T4 5:29.5-5:35 shows: "lets it fall"), then fold the lever by its free end; for hooking, raise the
  lever with the loop on it and turn the loop over onto the plate with a regrasp, or by letting it tip past vertical.
- **atom_container**: CONTAINER_AUDIT_RESULT (the rendered clip stops after the valve is shut; see above).

## What the audit checks, and what is assumed

- `ARM_AUDIT=1` on both scripts: every frame, FCL (collide.py): the arms, the grippers and what they hold against everything,
  and every other moving part ("movers"). Results are in the PR report and `out/collisions/atom_latch.json`,
  `out/collisions/atom_container.json`.
- The grasps that move a part by its joint (the lever, the loop, the knob, the valve levers, the T-bolt) keep the pads 0.4 mm off
  the part (`close_for_gap`); the audit is told which group each grasp handles (`rb.events`), so a pad touching it counts as the
  grasp, up to 1.5 mm deep.
- Assumed: the bolt's release on venting; the loop's preload (0.30 mm); the force curve's scale (100 N); the O-ring's section;
  the adjuster; the lid's balance point; the clamp's type and its 1.5 turns; the valve lever's direction; the fork, cradles,
  brush, rests, cap and peg (all ours).

## Open questions for the lab

1. How is the furnace latch adjusted, if at all (a threaded loop, shims, a screw in the keeper)?
2. Does the lid open to a stop at ~105 deg over the left, as the turned model has it?
3. What clamp joins the container to the outlet, and how many turns free it?
4. Is the chamber's own valve (above the clamp) shut before the container comes off, or only the container's?
5. What does a full container weigh (valve included)? The model says at least 4.3 kg empty.
6. Which way does the container's valve lever turn to shut ("pull down and move")?
