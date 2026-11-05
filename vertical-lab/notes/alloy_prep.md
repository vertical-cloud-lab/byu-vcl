# Chapter 6, sample prep (`alloy_prep.py`, `r8_prep.py`, `r8_specimens.py`)

Round 8 (PR #318, Sterling's review of 2026-11-05 00:37 UTC). Chapter 7 used to start from mounted coupons; this
chapter makes them. Chapter 5's AlSi10Mg build is sectioned, and two specimens go on to characterization:

| Specimen | Made how | For | Model |
|---|---|---|---|
| Conductive hot mount | the coupon (14 x 10 x 6 mm, wire EDM) pressed face down in carbon-filled phenolic in the LECO MX400, 1.5 in (38.1 mm), 20 mm tall | SEM/EDS (the filler is the path to ground), micro-Vickers | `r8_specimens.hot_mount` |
| Steel mount | the slice (10 x 10 x 6 mm, wire EDM) pressed into a 10.1 mm, 5.6 mm deep pocket of a 1.5 in 416-stainless puck, on its steel floor, held by a ball plunger; faced flush (0.4 mm off) on the Carvera | nanoindentation and PIP: no polymer under the sample to add compliance | `r8_specimens.steel_mount` |

Both are ground and polished together in the PX500's 6-position holder. The chapter ends with the holder face up on
the MiR's rest, both mounts in it, for chapter 7.

## The chapter, step by step

**Every transfer is the arm's** (Sterling, round 8: parts must not drop, float or teleport). The only things that
move on their own are what a machine moves itself: the press's closure, ram and doser, the Carvera's lid, vise and
spindle, the PX500's head and platen, the VLM's trays.

1. **Sectioning, on the wire EDM** on the floor (chapter 5's machine): a coupon and a slice. Shown as a look at the
   EDM with the reasons, not as an animation of the cut (chapter 5 animates the EDM). The pieces then ride the MiR's
   caddy (ours) with a steel puck and the press's stopper.
2. **The steel mount, on the caddy.** The slice is let go in the pocket's mouth (the pads' tips stop 1 mm over the
   puck's top) and pressed home by the closed fingers, 5.6 mm. It ends 0.4 mm proud.
3. **The Carvera, tray M at Shuttle 2.** The MiR stops 420 mm right of Shuttle 2's dock, with the Carvera at tray M's
   right end in reach. The lid opens; the arm sets the puck on two short parallels in a pneumatic vise (ours) whose
   jaws close along y while the fingers close along x; the vise clamps, the lid shuts, a 6 mm end mill faces the slice
   flush with the puck in three passes, the lid opens, the vise lets go.
4. **Into the holder, face up, then the holder over.** The steel mount goes into a pocket of the face-up holder on the
   MiR's rest. The arm then lifts the holder by its tab, turns it over (wrist 3, 180 degrees about the tab's axis) and
   sets it back face down, so the steel mount's face points down as the polisher needs.
5. **The MX400, tray F at Shuttle 1.** The MiR drives 4.8 m along the dock line at the MiR250's 0.3 m/s^2
   (`props.ramp_frac`, from PR #321) and stops 720 mm left of Shuttle 1's dock, the press at tray F's left end in reach.
   The lab's video, step by step: closure off, ram up, the coupon set face down on the ram, ram down, compound from the
   doser, the stopper set in the mold's mouth and pressed down onto the compound by the closed fingers, closure back,
   heat and pressure, cooling, closure off, the ram pushing the mount up with the stopper on it, the stopper back to
   the caddy, the mount into the holder face down.
6. **The PX500, tray F.** The MiR moves to Shuttle 1's dock. The head lifts (our extra lift); the arm fits the holder
   onto the spindle's coupling from under it (assumed, as in round 7). Then the disc changes, as before: 320 out of the
   magazine onto the magnetic platen, grind, a rinse, 400 back and 600 on, and so on to the cloth, with 1 um alumina.
7. The holder back on the MiR's rest, turned face up on the way: both polished faces up. Captions for the SOP's steps
   6 and 7 and for what is hard; tray F goes back.

## What changed, and why

### Sterling: "You jumped straight to the mounted coupons ... model and add that mount maker (some kind of hot press)"

`r8_prep.mount_press()` is the lab's **LECO MX400**, modelled from the lab's own video,
[Making Bakelite Polishing Puck](https://www.youtube.com/watch?v=9m_hdgmu2Jw) (storyboard and three frames fetched
through the stream-cam Pi with `frames.py`; nothing else downloaded):

- A slim light-grey cabinet. LECO gives the width only: "a slim, 8-inch wide profile"
  ([LECO MX400/MX500](https://eu.leco.com/product/mx400-500)). **Depth 460 mm and height 480 mm to the deck are
  estimates**, read off the video against that width.
- The touchscreen low on the vertical front, "MX400" under it; the LECO badge and a vent grille on the sloped upper
  front; on top, the 1.5 in mold ("Mold Size 1.50\"" on its screen, 6:20) under a stainless swing-arm closure with a
  knob at each end, and a label: "ALWAYS PLACE STOPPER ON TOP GREEN MARBLE END UP".
- The chapter follows the video and the lab's SOP (step 2, PR #258): the specimen face down on the ram, "3/4 scoop" of
  compound, the cap "with metal facing down and green marble facing up and flush with the top of the machine. It
  should be an airtight fit", the lock bar, the cycle, "use the up arrow to push the piece out of the chamber".
- **The cycle at the screen's values** (300, 4.2, 100, a 10:00 timer: "Heating" 5:40-5:59, "Cooling" 6:04,
  "Complete" 6:09). **The units are our reading**: 300 as °F (149 °C) and 4.2 as thousands of psi (29 MPa), because
  LECO's range is 90-200 °C and 1200-4300 psi, curing 0-30 min, molds 1.25 in, 1.5 in, 30, 40 and 50 mm
  ([DirectIndustry's copy of the MX400 sheet](https://pdf.directindustry.com/pdf/leco/mx400/114499-936234.html)).
  The third value, 100, is not labelled in the frames.
- **What we added for the arm**:
  - **A compound doser** on the deck behind the mold: a hopper with a chute that swings over the mold and back. The
    video pours by hand. Struers sells such a unit for its own presses, the CitoDoser, "an optional automatic dosing
    system" that dispenses a preset amount of resin
    ([Struers, CitoPress](https://www.struers.com/en/Products/Mounting/Hot-mounting/CitoPress)). Its size and place
    are ours.
  - **The stopper is pressed down by the closed fingers.** The fingers can't follow a 38 mm stopper into a 38.6 mm
    bore, so the arm lets it go in the mold's mouth and pushes it 20 mm down onto the compound with the pads' tips,
    as a person pushes the "airtight" cap in.
- The ram's 75 mm stroke, the 55 mm of loose compound and the 35 mm it compresses are **estimates**.

### Sterling: "include any machining steps ... use a CNC or leverage the same wire EDM"

- **Sectioning is on the wire EDM**, the floor's FANUC that chapter 5 uses to cut the bars off the plate. It cuts with
  no cutting force and leaves a thin recast layer, no saw burr. The Carvera's 200 W spindle with an ER11 collet
  (Makera's spec, `instruments_r7.CV`) takes no slitting saw for parting aluminium, and a sawn face would need facing
  anyway. The lab's own SOP sections with a diamond saw (step 1); the EDM replaces it here.
- **The CNC faces the steel mount** (`r8_prep.cnc()`): the slice goes into the puck as cut, 0.4 mm proud, and a 6 mm
  end mill takes it flush with the puck's top. That removes the EDM's recast layer (a few to ~20 um) and the cut's
  waviness, and makes the face parallel to the puck's base, which nanoindentation and PIP need. The first version
  faced the bare slice on both sides; the arm can't turn a 10 mm slice over with a two-finger gripper without a
  regrasp station, so the slice is faced in its mount instead, one side, no turn-over.
- **The steel mount** (Sterling: "polish by bonding it to a metal mount (maybe with an inset in a metal mount)"): an
  inset in a 416 stainless puck. It is held by a ball plunger in the pocket wall rather than bonded or screwed, so the
  arm needs no driver and the puck can be reused. The Edison search on mounts for indentation found that what matters
  is whether the force under the indent passes through metal or polymer
  ([out/edison/mech_test_mounts/answer.md](../out/edison/mech_test_mounts/answer.md); NPL Good Practice Guide 92:
  secure the specimen "without significant added compliance or flexure").

### Sterling: "you're not showing the robot arm swapping out different grits ... this retaining ring"

`r8_prep.polisher()` refits the PX500 (copied from `instruments.polisher()`):

- **A magnetic platen and six steel discs, each pre-loaded with its paper or cloth under its own retaining ring.** The
  arm changes disc, abrasive and ring as one piece by a handle on the ring, between the platen and a six-shelf
  magazine (`disc_magazine`, front right of tray F). Each grit's handle has its own colour.
- **Why whole discs, not papers.** The lab's SOP (step 4) changes a paper by taking "off the splash guard ring and
  metal sand paper holding ring", placing the paper and replacing "the two rings": a dexterous, two-handed job. The
  Edison search found no robot doing it. The one documented automatic route changes whole pre-loaded discs: BAM's
  RASI cell, a QATM QPOL 250 Bot with a magazine of 16 pre-loaded 250 mm discs and six fluid reservoirs
  (Lemiasheuski et al. 2023, in [out/edison/auto_polishing/answer.md](../out/edison/auto_polishing/answer.md)).
  Buehler's magnetic-disc patent ([US 6,224,474 B1](https://patents.google.com/patent/US6224474B1)) describes
  PSA-backed papers on removable steel discs over a magnetic platen, with retaining rings as the older alternative.
- **What stays manual**: re-papering the discs, between batches and off the machine. The SOP: "All sand paper pads are
  single use".
- **The holder** is the PX500's 6-position holder with a handling tab and fingertip slots at the two pockets we use
  (ours), as round 7's chapter 7 had it; it goes onto the head's coupling from under the lifted head (assumed: LECO
  publishes no quick-change coupling) and comes back to a rest on the MiR (three pins on a base, ours).
- **The head lifts 120 mm higher for a change (our assumption)**: with the head up as fitted to the SOP frames, the
  mounts hang 12 mm over the abrasive, too little to take a disc out under them.

### The lab's SOP, from PR #258 (`SOP/sem-eds-polishing-sop.md` on `claude/issue-110-20261005-1730`)

What the chapter takes from it, step by step:

| SOP step | The SOP | Here |
|---|---|---|
| 1 | diamond saw, ~1 cm sample | the wire EDM (above) |
| 2 | hot mounting: face down, 3/4 scoop, the cap green end up, the lock bar, "push the piece out" | the MX400 sequence, with the doser and the arm |
| 3 | belt sander until the sample is exposed | the 320 disc takes the compound's 0.6 mm skin off |
| 4 | 320, 400, 600, 800, 1200 SiC with water at the "gentle settings ... 35, 30, 150", 30 s; clean everything with water "between every grit change" | the same sequence and settings; a rinse under the spigot after each grit; the captions say "35, 30, 150" without naming which is force and which speed, since the SOP lists that as an open question |
| 5 | a pad with 1 um alumina, no water, 3 min, re-applied | the cloth disc, alumina from the PX500's dispenser |
| 6 | ethanol, methanol, ultrasonic | a caption: not modelled |
| 7 | 0.1 um diamond on a Buehler VibroMet 2, 1-2 h, checked every 30 min | a caption: not modelled (below) |

**The VibroMet 2 (step 7) is not modelled.** It is a vibratory bowl with its own holders and weights, run for 1-2
hours; it would need a tray place and its own handling, and there was no time in this round. Gage's videos of the
lab's machine are [setup](https://youtu.be/OvVvYESOxqw) and [removal and cleaning](https://youtu.be/kcyESipwU8Y).

### Sterling: "What did the CNC actually get used for? Was it just some random part, or was it a metal 3D printed part?"

In round 7 it was a generic part: `instruments_r7.cnc()` faced "a printed blank's as-built skin", a 100 x 40 x 30 mm
block standing in for a printed part, not tied to anything in the alloy route. Now it has the route's job: the slice
the wire EDM cut from the printed AlSi10Mg build, faced flush in its steel mount (`r8_prep.cnc()`, chapter 6).

## Where automating this is hard, and what exists (on screen at the end of the chapter)

- **Buehler AutoMet** heads automate force, speed and time; the Burst module doses polishing suspension at timed
  intervals ([JH Technologies on the Burst module](https://jhtechnologies.com/?p=1448);
  [AutoMet](https://www.aerospacemanufacturinganddesign.com/product/buehler-semi-automatic-grinder-polishers-automet-112918)).
  A person still changes papers, and the published alloy work inspected the surface by microscope between grits.
- **Robo-Met.3D** (developed by UES; now sold by AV, [avinc.com](https://www.avinc.com/solution/robo-met-3dr/)) moves
  one mounted specimen between motorized polishing, ultrasonic cleaning and an inverted microscope for serial
  sectioning, with autofocus height closing the loop on removal (Madison 2017; Oakley et al. 2025, in the Edison
  answer). Sectioning and mounting before it are not automated.
- **Still hard here**: re-papering, judging the polish (by eye in the SOP), the holder's clips and coupling.

## Physical sense: what was checked, what is left

Sterling asked whether other things, like the bars dropping onto a catch shelf, would not work as drawn. In this
chapter:

- **Fixed: parts moving on their own.** The first version (28905c5) moved the slice into the CNC's vise, the coupon
  onto the press's ram, the stopper, the slice into the steel puck and its set screw along the machines' own prop
  paths, with nothing carrying them, and the two mounts appeared in the polisher's holder. Now the arm carries every
  one of them, and a part is only ever let go where something holds it: a flat seat, the ram's face, a pocket's mouth
  (then pressed home), the vise's parallels, the holder's pocket.
- **Fixed: the slice turned over by the vise.** The first version faced both sides of the bare slice and turned it
  over between them by a joint of the vise, which no gripper can do with a 10 mm part without a regrasp station.
- **Fixed: the PX500 tour's parked discs swung round with the platen** (they were children of the spinning platen,
  so a disc waiting in the magazine orbited the machine during grinding). A disc now spins only while it is on the
  platen.
- **Fixed: the holder's tab ended up at the back.** The holder turned a fraction of a turn per grind, so after six
  grinds its tab faced away from the arm. Each grind now turns it whole turns.
- **Fixed: the Carvera's lid was in the way.** At Makera's 40 degrees no arm pose reached the vise (`PREP_PROBE=1`
  found 0 of 8 IK branches clear); our actuator opens it to 65 degrees (2 of 8 clear), 957 mm tall, still under the
  996 mm opening.
- **Simplified: the pushes.** Pressing the slice into a 0.05 mm-clearance pocket and the stopper into its "airtight"
  bore are drawn as the closed fingers pushing the part down at a steady speed; a real cell would need force control
  (the UR10e's own force-torque sensing) and might still jam a tilted slice.
- **Assumed: the holder's coupling and clips.** LECO publishes no quick-change coupling for the PX500's holder, and
  nothing holds a mount in a pocket of the stock holder when it is turned over.
- **The tour clips** move their samples on paths, with no arm, as every tour clip does; the chapter is where the arm
  does it.
- **The arm audit**: see Outputs below.
- **Left, from the last preview's planner log**: three joint moves in the disc changes start from a pose where the
  forearm touches the gripper (a straight line before them ends there), and five straight moves would have flipped
  the wrist, so the planner replaced them with planned joint moves. The disc changes need their own audit and poses.

## How the arm's stops were chosen

`PREP_PROBE=1 PREVIEW=1 xvfb-run -a python3 alloy_prep.py` builds the scene and, instead of the movie, prints for every
grasp (the caddy's seats, the holder's pockets and tab on its rest, the Carvera's vise, the press's mold, the PX500's
platen, the six magazine shelves and the holder on the head) how many of the UR10e's 8 IK branches are clear, at
several MiR stops, gripper spins and lid angles. The chapter's stops come from it: the MiR stops at x = -800 mm for the
press (at -720 a quarter of the spins hit camera F0's head; at -860 its tail would reach the VLM's target post), 560 mm
right of Shuttle 2's centre for the Carvera, and at Shuttle 1's dock for the PX500.

## Our designs, at assumed sizes

The caddy and the holder's rest on the MiR, the holder's tab, fingertip slots and clips, the press's doser, the
Carvera's vise and lid actuator, the disc magazine and the pre-loaded discs, the magnetic platen, the head's extra
lift, the ball plunger in the steel puck.

## Outputs (round 8)

- **`out/mp4/alloy_prep.mp4`: 195 s, 1172 frames at 6 fps, 1280 x 720, every tray built.** It is cut short. At about
  2.9 s a frame, with two other whole-floor renders on the runner, the whole chapter (about 1630 frames, 272 s) would
  have ended near 21:02 UTC, after the long-form's 20:45 cutoff. So the render was stopped at frame 1142, in the first
  (320-grit) grind. ffmpeg closed the file cleanly, and a 5 s card summarises the rest: the other grits, the holder back
  on the MiR face up, the SOP's steps 6 and 7. It shows everything up to the first grind: sectioning, the steel mount,
  the Carvera facing it, the holder turned over, the MX400 procedure, the holder onto the PX500 and the first disc
  change.
- `out/alloy_prep.gif`: 3.7 MB, 2 fps, 480 x 270, made from the MP4 with ffmpeg and gifsicle. `out/alloy_prep_still.png`
  is frame 1110: the arm laying the 320 disc on the platen.
- `out/alloy_prep.json` notes the cut. The per-step frame ranges were not written, because the run stopped before
  `Scene.save()`.
- **To render the whole chapter:** `VIZ3D_FPS=6 python3 runner_guard.py bg --mem 7000 --log ... -- xvfb-run -a python3
  alloy_prep.py`, about 80 min at today's load. The script runs to the end: preview v3 reached its last step.
- **The arm audit** (`VLAB_ONLY_TRAYS=FM ARM_AUDIT=1 xvfb-run -a python3 alloy_prep.py`, trays F and M are the only ones
  the arm works at) was queued after the render and had not run when these notes were written. The render does
  **not** rest on a clean audit.

## Files

- `r8_prep.py`: `mount_press` (with the doser), `polisher`, `cnc` (the steel mount's job), `disc_magazine`;
  `TRAY_PLACEMENT` puts the press at the back left of tray F (behind camera F0's post) and the magazine at its front
  right.
- `r8_specimens.py`: the two specimens; `steel_mount("seated")` is now the slice as cut, 0.4 mm proud.
- `alloy_prep.py`: the chapter; `out/alloy_prep.{gif,json}`, `out/mp4/alloy_prep.mp4`, `out/alloy_prep_still.png`;
  the arm audit in `out/collisions/alloy_prep.json`.
- Tour clips: `out/instruments/{mount_press,polisher,cnc}.{gif,png}`, `out/mp4/instruments/...` at 8 fps.
