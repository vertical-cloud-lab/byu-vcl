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

## Round 9 (#303, Sterling's point 16 of 2026-11-05 22:56)

**The PX500's holder holds nothing.** Round 8 drew a plain 6-hole disc with a handling tab and said "clips (ours) keep
the mounts in". Sterling's reading (and the lab's, from its SOP videos, [refine_polisher.md](refine_polisher.md): part 2
at 6:28 shows an individual-force holder with pistons) is that there is no set screw or clamp: with the head down, each
mount stands on the disc, and the machine's piston comes down onto its back to press it; with the piston up the mount is
freestanding in its hole. What changed:

- **No clamping anywhere on the holder.** The "clips" caption is gone. (The set screw that remains is the *steel puck's*
  ball plunger and screw in `r8_specimens.steel_mount`, a different part, before the holder.)
- **The pistons are modelled.** `r8_prep.polisher()` has a `pistons` piece (six rods 26 mm across with 29 mm feet, a
  stainless carrier plate above them, sizes ours) on a slide joint under the spinning `holder`. In every grind the head
  comes down, the pistons come down 5 mm onto the mounts' backs, the platen and holder turn, then "Pistons up: the mounts
  just stand in their holes", then the head lifts. A close-up camera at the holder shows it. The polisher tour clip
  (`inst.actions`) has the same.
- **Stepped bores.** Each hole is the mount's diameter (38.1 + 0.4 mm) for the mount's 20 mm less its 13 mm that stands
  proud, i.e. 7 mm, then a 5 mm ledge with a 30 mm aperture the piston passes through. A mount rests against that ledge
  when the holder is carried face up, and the piston reaches it through the aperture. Sizes are ours.

**What stops the mounts falling when the holder is lifted and turned over (open, decided here).** LECO publishes nothing
about how its holder keeps a mount in hand: its pages say only that the individual holder's wheel indexes slowly "to
make loading and removing mounts easier" ([LECO PX series](https://www.leco.com/instrument/px-series-grinder-polishers/),
[PX400/PX500 catalogue](https://pdf.directindustry.com/pdf/leco/px400-px500-grinder-polisher-series/114499-791543.html)),
so a ledge alone cannot be what holds a mount once the holder is turned face down. Three options:

1. a ledge: holds only while the holder is face up (the mount rests on its back), fails the moment it is turned over;
2. the holder stays on the machine and the arm loads and unloads mounts one at a time, with the head up; that is what the
   indexing wheel suggests, but then the mount needs a hold while the arm lets go;
3. a light friction grip in the bore (an O-ring), which is what this chapter shows: the mount is loaded face up against
   the ledge, the holder is turned over, and the O-ring keeps the mount from dropping while the holder is handled. **This is
   an assumption**, not a LECO feature, and it is the first thing to check with LECO or on the lab's machine. If the real
   holder stays on the head, the chapter's holder transfers (steps 3 and 6) become mount-by-mount transfers instead.

Estimates and assumptions: piston and aperture sizes, the 5 mm piston gap and press travel, the O-ring.

**Round 9 outputs.** Whole chapter rendered (`VLAB_ONLY_TRAYS=FM VIZ3D_FPS=6`, 1280x720): 1816 frames, 302.7 s (5:03),
mp4 14.0 MB, GIF 4.62 MB (606 frames), commit `c0828e5`. It ends at the holder back on its rest and the SOP card, not at
the first grind as in round 8. **Arm audit (`VLAB_ONLY_TRAYS=FM ARM_AUDIT=1`): 456 of 3539 frames in collision, 90 runs
(`out/collisions/alloy_prep.json`), not the target 0.** Mount step: 51 frames, the wrist camera against the press body.
Polish: 405 frames, mostly the forearm into the gripper (270) and wrist 3 (45) and the upper arm into the bay (114) and the
MiR's cabinet (57), plus a held 320/400 disc against the polisher body (25). They cluster in the move that fits the holder
onto the head (the planner logs "line move would flip the arm... end pose in collision") and in the disc changes. Not fixed:
the queue left no time to re-plan and re-render. The close-up camera on the pistons (`cam_pist`) was added after the
only preview and was not previewed; the render is its first sight. The polisher tour clip was not re-rendered.

## Round 10 (#303, 2026-11-07): the arm's moves made physically possible

Round 9's audit (`ARM_AUDIT=1`) had **456 of 3,539 frames in collision**. Every one was traced, with a pose
server (`PREP_SERVE=mount,polish`, below) that holds the built scene and tests IK branches and straight tool lines
against it in seconds instead of a rebuild:

| Where | What hit what (round 9) | Why | Fix |
|---|---|---|---|
| MX400, the coupon onto the ram, the stopper in and out, the mount off the ram (51 frames) | the wrist camera against the press's body | the D405 rides on one side of the coupling; with the gripper at spin 0 over the mold it ran into the press in **all 4** IK branches | the gripper turned 180 deg over the mold (`SPIN_MOLD`): 4 of 4 branches clear (45-270 deg all are) |
| PX500, every disc lifted off or onto the platen (the held disc against the body) | the held disc against `F0_polisher:body` | **the head's column stood inside the bowl**, 95 mm behind its centre (the model's `cy = hy + head_back - 40`), from the deck up to the head. A 300 mm disc lifted above the deck ran into it; below the deck the bowl's lip stops a level slide. As modelled, no disc could come or go under the head at any height. | the column moved behind the bowl's lip (268 mm behind the bowl's centre, still inside the PX500's footprint); the head reaches it by an arm and slides on it (a slide drawn with the head, so the column stays below the head when it lifts). **Assumed**: a grinder-polisher's power head is carried from behind the wheel; the column is hidden behind the head in the SOP frames the model was fitted to. |
| PX500, the holder onto and off the head | the held holder against the pistons | the pistons, "up", hung 4 mm into the holder's apertures, so the holder could not slide onto the coupling under them | the pistons' up gap 5 -> 12 mm (`r8_prep.PIST_GAP`): their feet clear the holder's back by 3 mm; pressed is where it was |
| PX500, the disc changes (most of Polish's 405 frames) | the forearm into the gripper (270), the upper arm through the bay's frame (114) and into the MiR's cabinet (57), wrist 3 | each move followed the IK branch the last one left the arm in, and the transfer was one 2-metre straight line of the gripper from the magazine (tray F's right end) to the platen (its left), through the furnace's corner and the bay's frame | every approach is now a joint move into an IK branch from which the straight lines that follow are all clear and don't flip: in, the lift, out with the disc held, and the retreat after letting go (`clear_branch`, after `alloy_charge.py`'s `pre()`). The transfer between magazine and platen is a planned joint move with the disc held, not a straight line. The holder's moves onto and off the head use the same. |
| the magazine (1+2 frames) | a held disc against the disc above or below | lifted 8 mm off its rails, a disc's handle (92 mm tall) met the ring of the disc 100 mm above | lifted 4 mm (`LIFT_MAG`); off the platen 70 mm (`LIFT_POL`, was 62): over the bowl's lip (51 mm) and under the lifted holder's mounts (128 mm) |

What the probe found at the MiR's stop for the PX500 (Shuttle 1's dock, x = 0), the arm's base 1.09 m from the
magazine's handles and 0.63 m from the platen's handle (horizontally): the magazine's shelves have 2 to 5 clear IK
branches of 8 for the whole in-lift-out sequence (the bottom shelf 2); the platen's level approach from the front (470
mm out, 70 mm up) had **none** while the column stood in the bowl and has 2 without it. The preview (`PREVIEW=1`) then
ran with no "no IK branch" note and no joint move left unplanned. The magazine, the MiR's stops and the chapter's
content and captions are as in round 9.

**The audit is now part of the render.** A full render of the chapter also runs `collide.Auditor` on its own frames
(`PREP_AUDIT_RENDER=0` to skip) and writes `out/collisions/alloy_prep.json`, so the numbers are for the very frames of
the MP4 and need no second pass through the chapter (round 10 had three render slots for six streams).

**The pose server, for the next session.** `PREP_SERVE=mount,polish ARM_AUDIT=1 VIZ3D_FPS=1 VLAB_ONLY_TRAYS=FM
xvfb-run -a python3 alloy_prep.py` runs the movie quickly to the start of the MX400 or the PX500 and then executes each
new `/tmp/prep_srv/*.py` in the movie's namespace (output to `*.out`) until `/tmp/prep_srv/next` exists. It is how the
column was found: the held disc hit `F0_polisher:body/inst_grey1` (the bowl and the column, one mesh) at every lift.

**Round 10 outputs.** Whole chapter re-rendered on the code above (commit `32d05e4`; `VLAB_ONLY_TRAYS=FM VIZ3D_FPS=6`,
1280 x 720), 23:09-00:18 UTC: 1816 frames, 302.7 s (5:03), mp4 14.0 MB, GIF 4.62 MB (606 frames), still
`out/alloy_prep_still.png`, preview still of the changed steps `out/alloy_prep_preview.png`. **Its audit, of its own
frames: 0 of 1,423 checked frames in collision, 0 runs** (`out/collisions/alloy_prep.json`; the auditor runs on every
frame that moves, and the 393 others are holds, copies of the frame before). Round 9's 456 of 3,539 were counted on a
separate `ARM_AUDIT=1` pass at a higher frame rate, so the frame totals differ; the rules for what may touch are the
same. The chapter's length, steps and captions are as in round 9.

Still assumed or simplified: the column behind the bowl and the head's arm to it (above); the pre-loaded discs, the
magazine and the magnetic platen (round 8); pressing the slice and the stopper home as the closed fingers moving at a
steady speed, which a real cell would do under force control. A clear audit means the drawn meshes never interpenetrate;
it doesn't check clearances a real cell would want (a few mm here and there, such as the pistons' 3 mm over the holder).

Not re-rendered: the polisher's tour clip (`out/instruments/polisher.*`) still shows the column in the bowl and the
pistons' old gap.

## Round 11 (2026-11-14): the stricter audit

Sterling, on the round-10 long-form: "There are probably other collisions and interferences that I didn't catch from
this." Round 11's `collide.py` (audit-a) lets the gripper and a held part touch what they handle only up to 1.5 mm deep
and checks everything else that moves (trays, doors, the MiR, the press, the PX500's head and platen, the Carvera's lid
and vise) against everything else. Camera F1 on tray F moved behind the quench tank (chapter 5's stream, `6c690a0`),
away from the front of the tray where the arm works; the comment in `r8_prep.TRAY_PLACEMENT` now says so.

| Audit (`VLAB_ONLY_TRAYS=FM`, 6 fps) | Code | Arm | Movers | All |
|---|---|---|---|---|
| [`alloy_prep_r11a.json`](../out/collisions/alloy_prep_r11a.json), round 10's rules, F1 at its old place | round 10's | 0 of 1423 | | **0** |
| [`alloy_prep.json`](../out/collisions/alloy_prep.json), stricter rules, F1 at its new place | round 10's | 1 of 1423 | 55 | **56** |

Not re-rendered this round (the coordinator: chapters 4 and 6 audit only, all four render slots taken); the committed
MP4 is round 10's.

Seen in the other chapters and true here too, but not changed: the MiR's caddy (`CADDY`, x -130 to 95) stands on the
cabinet's 780 mm inside the arm's 20 mm mounting plate (`props.mir250` draws the plate, |x| < 170 mm, as part of the
cabinet), so only its top 10 mm shows; its seats are at 810 mm, over the plate's top, so the parts on it don't touch
the plate. The holder's rest reaches 20 mm over the plate's edge in the same way.

What the stricter audit found (none of it fixed this round; the arm itself is clear but for one frame):
- **Camera F1's new place is clear of the arm**: 213 mm at the closest (a held disc, in the disc changes). F0, 12.2 mm
  (the wrist camera at the press), and the bay unit, 247 mm. Nothing touches.
- **The arm: 1 frame**, the hot mount set into the holder's pocket deeper than 1.5 mm (`Mount`).
- **The movers check, 55 frames, mostly the machines' own processes drawn as solids:**
  - the Carvera's end mill passes 25 mm into the steel puck while it faces the slice (15 frames). The cut should
    take 0.4 mm off the slice's face only, so the tool's path in `r8_prep.cnc` needs to stop at the puck's face;
  - the PX500's pistons press 14 frames into the holder (they press the mounts, by design; the holder's apertures or
    the pistons' stroke need the 1.5 mm to be met, or the pistons drawn as pressing the mounts, not the holder);
  - the MX400's compound (granules), the finished mount and the doser against the coupon, the stopper and the closure
    (22 frames): the compound fills round the coupon by design, so it is a non-solid until it cures; not registered in
    time;
  - **the Carvera's lid, at our actuator's 65 deg, rises 999 mm "into" tray H (the tray stored over Shuttle 2's
    opening) and 50 mm into the bay's overhead camera** (4 frames). At Makera's 40 deg no arm pose reached the vise
    (round 8's probe), so the lid needs another way to open (a sliding cover) or the slot over the opening needs the
    room; a real interference, open for the lab stream (the slots) and this chapter.
- **The PX500's tour clip** (`out/instruments/polisher.*`, not this chapter's audit): audit-a's `interference.py` finds
  the disc handles passing 12-13 mm through each other and through the head's housing while discs are swapped
  (frames 199-202, 314-317, 335 of the tour). Open.


