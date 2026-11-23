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

## Forces and the MiRs' margins (chapter 2's `stability()`, at the rendered clip's poses)

| Load | Where | Tips at (131 kg plate / none) | Slides at (plate / none) |
| --- | --- | --- | --- |
| 100 N on the lever (200 if stiff), pulling it open | MiR250 1 at (650, -560), arm 1 on the lever | 783 / 435 N | 952 / 539 N |
| the same, pushing it shut | MiR250 1 | 690 / 398 N | 952 / 539 N |
| ~100 N press down on the lid | MiR250 2, front left | 614 / 370 N | 2087 / 1173 N |
| 58 N, the lid's weight on the knob | MiR250 2 | 1507 / 719 N | does not slide |

With the ballast plates every load has at least 3 times the stiff latch's 200 N; without them the press (370 N to tip) would
leave 1.85 times. Numbers from `out/atom/atom_latch_stability.json`.

## The container (clip `atom_container`)

**What the rendered clip shows: steps 1-5 below** (the state, the brushing, the dust settling, the valve shut), with,
since round 14, the brush's used head stripped off and a fresh one pushed on between steps 3 and 4 (the clip's own
step 4/6; "Round 14" below). Steps 6-13
are written in `atom_container.py` (`ATOM_CONTAINER_FULL=1` runs them) but their two-arm moves still collide: its audit at
01:42 found 994 frames in collision in those steps (arm 2's forearm folding onto its own MiR250 with the fork under the
container, arm 1 and arm 2 crowding the clamp). Not rendered; the next session should move MiR250 2 (the fork's arm) and
re-plan them. The view port's glass is not brushed either: from the door the long brush's grip meets the ultrasonic stack on
the open door.

| # | Step | Who | Source |
| --- | --- | --- | --- |
| 1 | Vented, cold; the door's two clamps swung off, then the door opened; paper under the opening | (done before the clip) | 178_sop After a run (T2 39:00, T5 77:17); DAL SOP Powder Collection 1 |
| 2 | An anti-static brush taken from MiR250 1's rest, by its square grip, with a fresh head on | arm 1 | AMAZEMET's set of anti-static brushes (178_manual); this long-handled one, its grip, rest and disposable heads are ours (round 14) |
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

## Round 14 (2026-11-20): the brush as a tool the gripper can't drop, one head per run

Sterling on PR #318, at the moment round 12's clip puts the brush back on its rest (24:58 in the long-form): "There's
also not much of an automation-friendly grip for the gripper. Seems like it would slip out." And: "Cross-contamination
for the anti-static brush is going to be a concern.. how to handle that? Thorough cleaning? (e.g., ultrasonic
cleaning). Disposable heads? (e.g., kind of like disposable wand attachments in other contexts)." Everything below is
ours (`atom_brush.py`), drawn to the 2F-85's own geometry (`ur_arm.py`); none of it is a catalogue part.

**Why it would slip.** Round 12/13's brush had a plain 18 mm round handle. Flat pads on a round bar hold by friction
only: the brush could turn about its own axis, and its weight (a 0.3 kg brush a few hundred mm out) twists it about the
fingers' closing line, the usual way a parallel gripper drops a long tool.

**The grip.** The 2F-85 now closes on an 18 x 18 mm square block (flat pads on flat faces: it can't turn about the
shaft) between two collars of 37 mm diameter whose inner faces stand 1 mm clear of the fingertips' sides (the
fingertips span y -14.3..13.5 mm in the TCP frame, closed on 18.8 mm). The collars stop it sliding along the fingers,
and it can't pivot about their closing line more than a few degrees before a fingertip bears on a collar: form-fit, not
friction. The collars' radius (18.5 mm) is wide enough to stop a fingertip (whose face is 9.4 mm off the axis) and
short of the inner knuckles (19.4 mm behind the grasp point). The pads close on the same 18.8 mm gap as before, so the
grasp, the brushing poses and their audit are unchanged.

**The rest.** Two V-blocks under the shaft centre it. The first has a slot that takes a 4 mm fin hanging under the
shaft by the grip: the brush lies one way only (fin down, bristles out), can't roll, and can't slide off. The slot is 59
mm long, so the fin still sits in it during the 25 mm push that puts a fresh head on.

**One head per run.** The head (bristles in a block, on an orange ferrule) goes onto a 12 x 20 mm spigot at the shaft's
end and is held by a spring ball detent (~30 N, assumed): push on, strip off, like a pipette tip. The cycle:

1. The brush waits on its rest with a fresh head on, the head sitting in the rest's open-topped pocket.
2. Taken up, it lifts the head out of the pocket; a spring-fed magazine (a pusher plate on a gas spring) slides the
   next head into the pocket.
3. After brushing, the arm drops the shaft into the slot of a stripper bar across the mouth of a waste can on MiR250 1
   and pulls back 30 mm: after 3 mm the bar holds the ferrule (the 18 mm shaft passes the 20 mm slot, the 22 mm ferrule
   doesn't), the head comes off the detent and falls into the can with the run's powder on it.
4. The headless shaft goes down onto its rest 25 mm short and pushes along its axis onto the head waiting in the
   pocket until the detent clicks; the arm lets go.

The can is steel, bonded to the MiR's frame (a ground strap is drawn), and goes to the same combustible-metal waste as
the vacuum's liners (`atom_vacuum.md`). The head's bristles are conductive (carbon or stainless fibre, as anti-static
brushes are); its size, its detent force and its cost are ours, not a product's. One head goes per run; three are drawn
in the magazine.

**Why not clean the brush between alloys.** An ultrasonic IPA wash was the other way. It was not chosen because:

- it puts reactive fine Al powder (and Mg or Al-Li, for those alloys) into a solvent bath, which is a fire load and a
  new solvent waste stream to collect, store and ship;
- the brush has to be fully dry before it touches dry powder again (wet bristles cake fines), which adds time between
  runs;
- the powder lodges at the bristles' roots, where nothing on the arm can see or test whether the brush is clean. A
  cleaned brush can't be shown free of the last alloy; a new head is free of it by construction.

The same reasoning is why the lab keeps one plate, sieve set and vacuum per alloy family; a head is cheap enough to
throw away each run.

**Audit.** Strict rules at 15 fps (`ARM_AUDIT=1 VIZ3D_FPS=15 xvfb-run -a python3 atom_container.py`): **0 of 723
frames** with an arm in collision, movers 0 (out/collisions/atom_container.json). The first pass found the falling head
3 mm into the can's wall (6 frames: the can was 90 mm across, centred on the stripping line); the can is now 88 mm
across, centred on the falling head's footprint, with 2-3 mm all round, and the stripping line moved 20 mm towards the
container's cradle to keep the can clear of the pocket's wall.

## Round 15 (2026-11-23): the MiRs off the rePowder, and the stripper past the mast

Sterling on PR #318 (2026-11-23): "Fix collisions, nonsensical parts, etc." Neither the arm audit nor the movers check
sees two parts that both stand still, so a parked MiR250 inside the machine went unreported; each parked MiR (its
Class D unit and base cameras included) was checked against the rePowder's meshes with FCL.

- MiR250 1's brushing spot `A_LEFT` is 70 mm further forward, (-700, -420, -45): at y -350 its back corner stood 18 mm
  into the vacuum pump (model x -880..-420, y 120..340). Now 52 mm clear, 116 mm at the closest as it drives off.
  From there the nearest clear IK branch at the entry ended the bowl's circle with the forearm on the MiR's cabinet;
  the entry now takes the branch that is clear down the whole path (`alloy_atomize.path_branch`, as chapter 2's tong).
- MiR250 2's `B_FRONT` is 120 mm further forward, (800, -600, 90): at y -480 its front end stood 70 mm over the
  rePowder's right base rail and its front-right foot. Now 50 mm clear. Its arm does nothing in the rendered steps.
- With the base cameras' mast back on the MiR's back-left corner (props.py, round 15), the branch picked at the
  stripper put wrist 1 into the mast as the shaft pulled back, and the first 720p render stopped at 4/6 ("end pose in
  collision"). The stripper and the rest now take the branch that is clear through the drop, the pull and the lift.
- Audit, strict, 10 fps (`ARM_AUDIT=1 VIZ3D_FPS=10 ARM_AUDIT_TAG=r15fix_atom xvfb-run -a python3 atom_container.py`):
  **0 of 481** frames with an arm in collision, movers 0 (out/collisions/atom_container_r15fix_atom.json).

The latch clip's counter now numbers the steps it shows consecutively, 1/7 to 7/7. It skipped 2/9 and 6/9: the press
(step 2) has been off since round 14, and step 6 went then. The tables below keep the procedure's own numbers.

## Round 13 (2026-11-20): the latch clip at 0 frames in collision

The fix proposed below is made (`atom_latch.py`). The final strict audit at 15 fps: **0 of 1260 checked frames** with an
arm in collision, 0 mover frames (out/collisions/atom_latch_r13fix.json; the round-12 render had 123 of 833 at 10 fps).

- **Unclamping (5/9):** arm 1 takes the loop by its legs (in and down 65 deg) and lifts it, so the lever rises to 85
  deg and the bar rides up the keeper's plate over the hook's lip; it tips the loop about 15 deg past upright, lets the
  lever down on the loop's pin onto its base, then opens its fingers and the loop falls over the lever. The gripper
  turns about 36 deg in all, not 170. One-handed, the order differs from the footage (there a second hand holds the
  lever up while the loop comes off); the caption says so.
- **Hooking on (8/9):** arm 1 closes lightly on the hanging loop's legs and keeps one hand attitude while it carries
  them round the loop's pin, so the loop turns between the pads (ours, labelled so); it raises the lever to 85 deg,
  tips the bar onto the keeper's plate and lowers it onto the hook (the lever rests at 42 deg).
- **7/9 and the lid coming down:** the knob grasp is tilted 20 deg about the model's x through the ball's centre. The
  hits were arm 2's wrist on the cabinet with the lid shut, not at the top of the swing as written below.
- **A camera at the latch's height** (front right) for 5/9 and the hook-on; from above, arm 1's wrist hid the latch.
- **The model's latch was missing.** Round 12's `alloy_atomize.load_rp` left out every `latch_*` part for every caller
  (meant for chapter 2, which draws its own), so the atomizer clips had no latch base, hold-down foot or bolt, and a
  lever and loop on no parent. load_rp now leaves them out for chapter 2 only (`own_latch=True`).

## Round 14 (2026-11-20): no arm on the lid; chapter 2 uses the same moves

Sterling (PR #318, 2026-11-20, of chapter 2 at 17:28): "holding the lid down while working the latch seems unnecessary?
It's also still missing the typical 'unlatching' step that has to happen before pulling the latch down."

- **No press.** Arm 2 no longer holds the lid down, opening or closing (steps 3/9 and the press before 9/9 are gone;
  `ATOM_LATCH_PRESS=1` brings them back). The furnace is only opened at atmosphere (the bolt goes back only then), so
  nothing pushes the lid up when the loop comes off, and a ~10 kg lid sitting on its O-ring has no stored pressure to
  let go. Closing, the latch's own over-centre draw squeezes the seal (0.6 mm at dead centre, about 100 N at the lever);
  the lid's weight keeps it on the O-ring while the loop is hooked on, and the leak check at -850 mbar is what says it
  seals. The palm on the lid in T4 5:17-5:24 is a person steadying it with a free hand.
- **The unlatching is its own step**, as it was already here: after the lever goes over centre, the loop is lifted off
  the keeper's hook and let fall over the folded lever. Chapter 2 had neither: its own round-6 latch went out and down
  in one move with the loop never unhooked. Chapter 2 now calls the same code, `atom_latch.Work` (vent, unclamp,
  open_lid, close_lid, clamp, pump), on the model's latch, so the two can't drift apart.
- **Audit, 15 fps, strict:** 0 of 1123 frames with an arm in collision, 0 mover frames
  (`out/collisions/atom_latch.json`). Re-rendered at 1080p, 15 fps (93 s, its inline audit 0).
- **The margins** (`out/atom/atom_latch_stability.json`): with the lid's 58 N on its knob MiR250 2 would tip at
  1546 N; MiR250 1 on the lever at 783 N (pulling) and 690 N (pushing), slides at 952 N.

## Audit results and what is still wrong (2026-11-19, the rendered scripts)

- **atom_latch** (the turned lid, one-armed latch; final pass 02:31, render and audit together at 10 fps, 103.1 s, 1031
  frames): **123 of 833 checked frames have an arm in collision; movers 0.** MiR250 1 now stays where it starts, (650, -560,
  0), its footprint clear of the rePowder's base frame (x 250..1050, y -850..-270). The 02:13 pass had searched six spots and
  moved it, without a drive, onto (700, -420, 50), where its corner stood in the base frame: that render had 113 arm frames
  and that mover fault. The collisions left: 5/9 and 8/9 (44 and 63 frames), arm 1's forearm and wrist in the furnace, the
  chamber, the door and the latch while it swings the loop over the lever, and there it also meets arm 2's parked forearm and
  wrist; 7/9 (16 frames), arm 2's wrist on the blue cabinet near the top of the lid's swing. The loop's grasp is the best of
  eight tried in the clip (approach in and down 40, 10, 65 or -15 deg, the tool as is or turned 180 deg about its axis): in and
  down 65 deg, 140 hits on the swing against 198 for the 40 deg one; none clears it. Holding the loop by its legs through the
  swing over the lever's top turns the gripper ~170 deg with it, and the forearm sweeps into the machine. The fix, not made
  for lack of time: lift the bar off the hook and let the loop fall onto the lever's web (what T4 5:29.5-5:35 shows: "lets
  it fall"), then fold the lever by its free end; for hooking, raise the lever with the loop on it and turn the loop over
  onto the plate with a regrasp, or by letting it tip past vertical.
- **atom_container** (the final pass at 10 fps, 50.9 s, 509 frames; it stops after the valve is shut, see above): **18 of
  384 checked frames have an arm in collision**: 12 in 3/5 (the bristles on the catch bowl's rim and the chamber, up to 12 mm,
  and arm 1's left finger up to 25 mm into the chamber at the door's edge as the brush comes out of the bowl) and 6 in 5/5 (arm
  1's right fingertip 12 mm into the chamber's outlet as it backs off the shut valve's lever). Movers: 0.

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
