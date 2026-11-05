# Chapter 6, sample prep (`alloy_prep.py`, `r8_prep.py`, `r8_specimens.py`)

Round 8 (PR #318, Sterling's review of 2026-11-05 00:37 UTC). Chapter 7 used to start from mounted coupons; this
chapter makes them. Chapter 5's AlSi10Mg build is sectioned, and two specimens go on to characterization:

| Specimen | Made how | For | Model |
|---|---|---|---|
| Conductive hot mount | the coupon (14 x 10 x 6 mm, wire EDM) pressed face down in carbon-filled phenolic in the LECO MX400, 1.5 in (38.1 mm), 20 mm tall | SEM/EDS (the filler is the path to ground), micro-Vickers | `r8_specimens.hot_mount` |
| Steel mount | the slice (10 x 10 x 6 mm, wire EDM) faced on both sides on the Carvera to 5.6 mm, set in a 10.1 mm pocket of a 1.5 in 416-stainless puck on its steel floor, held by an M3 set screw | nanoindentation and PIP: no polymer under the sample to add compliance | `r8_specimens.steel_mount` |

Both are ground and polished together in the PX500's 6-position holder, rinsed and dried, and go to the sample store
(tray J) for chapter 7.

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
- The clip and the chapter follow the video step by step: closure off (0:44), ram up, the specimen face down on the
  ram, ram down, compound poured in (5:00-5:15), the stopper on, green end up, the closure swung back (5:20-5:30), the
  cycle at the screen's values (300, 4.2, 100, a 10:00 timer: "Heating" 5:40-5:59, "Cooling" 6:04, "Complete"
  6:09), closure off, ram up, the mount out (6:24-6:55).
- **The units are our reading**: 300 as °F (149 °C) and 4.2 as thousands of psi (29 MPa), because LECO's range is
  90-200 °C and 1200-4300 psi, curing 0-30 min, molds 1.25 in, 1.5 in, 30, 40 and 50 mm
  ([DirectIndustry's copy of the MX400 sheet](https://pdf.directindustry.com/pdf/leco/mx400/114499-936234.html)).
  The third value, 100, is not labelled in the frames.
- The ram's 75 mm stroke, the 55 mm of loose compound and the 35 mm it compresses are **estimates**.

### Sterling: "include any machining steps ... use a CNC or leverage the same wire EDM"

- **Sectioning is on the wire EDM**, the floor's FANUC that chapter 5 already uses to cut the bars off the plate. It
  cuts with no cutting force and leaves a thin recast layer, no saw burr. The Carvera's 200 W spindle with an ER11
  collet (Makera's spec, `instruments_r7.CV`) takes no slitting saw for parting aluminium, needs coolant it does not
  have, and a sawn face would need facing anyway.
- **The CNC faces the slice**, both sides: 0.2 mm a side (the EDM's recast layer, typically a few to ~20 um, and the
  cut's waviness), 6 to 5.6 mm, flat and parallel, which nanoindentation and PIP need. A 6 mm end mill, two passes a
  side (`r8_prep.cnc()`); a small vise for the 10 mm slice is ours.
- **The steel mount** (Sterling: "polish by bonding it to a metal mount (maybe with an inset in a metal mount)"):
  `r8_specimens.steel_mount`, an inset in a 416 stainless puck, held by a set screw rather than bonded, so it can be
  taken out and the puck reused. The Edison search on mounts for indentation found that what matters is whether the
  force under the indent passes through metal or polymer
  ([out/edison/mech_test_mounts/answer.md](../out/edison/mech_test_mounts/answer.md); NPL Good Practice Guide 92:
  secure the specimen "without significant added compliance or flexure").

### Sterling: "you're not showing the robot arm swapping out different grits ... this retaining ring"

`r8_prep.polisher()` refits the PX500 (copied from `instruments.polisher()`):

- **A magnetic platen and six steel discs, each pre-loaded with its paper or cloth under its own retaining ring.** The
  arm changes disc, abrasive and ring as one piece by a handle on the ring, between the platen and a six-shelf
  magazine (`disc_magazine`, front right of tray F). Each grit's handle has its own colour.
- **Why whole discs, not papers.** Changing a paper means prying the ring off, peeling the paper, laying a new one
  flat and pressing the ring back on evenly: a dexterous, two-handed job. The Edison search found no robot doing it.
  The one documented automatic route changes whole pre-loaded discs: BAM's RASI cell, a QATM QPOL 250 Bot with a
  magazine of 16 pre-loaded 250 mm discs and six fluid reservoirs (Lemiasheuski et al. 2023, in
  [out/edison/auto_polishing/answer.md](../out/edison/auto_polishing/answer.md)). Buehler's magnetic-disc patent
  ([US 6,224,474 B1](https://patents.google.com/patent/US6224474B1)) describes PSA-backed papers on removable steel
  discs over a magnetic platen, with retaining rings as the older alternative.
- **What stays manual**: re-papering the discs, between batches and off the machine. SiC paper wears fast: Buehler's
  note for its fully automatic VANGUARD says to change it after each holder (in the same Edison answer).
- The SOP's settings are kept: 320, 400, 600, 800, 1200 SiC with water at head 35 rpm, force 30, platen 150 rpm, 30 s
  each; then the cloth with 1 um alumina at force 3-5, 150 rpm, 3 min (notes/refine_polisher.md).
- **The head lifts 120 mm higher for a change (our assumption)**: with the head up as fitted to the SOP frames, the
  mounts hang 12 mm over the abrasive, too little to take a disc out under them.
- The holder takes 1.5 in mounts now (`r8_specimens.MOUNT_D`, 38.1 mm): six fit at the 52 mm radius.

### Sterling: "What did the CNC actually get used for? Was it just some random part, or was it a metal 3D printed part?"

In round 7 it was a generic part: `instruments_r7.cnc()` faced "a printed blank's as-built skin", a 100 x 40 x 30 mm
block standing in for a printed part, not tied to anything in the alloy route. Now it has the route's job: the slice
the wire EDM cut from the printed AlSi10Mg build, faced flat and parallel on both sides for the steel mount
(`r8_prep.cnc()`, chapter 6).

## Where automating this is hard, and what exists (on screen at the end of the chapter)

- **Buehler AutoMet** heads automate force, speed and time; the Burst module doses polishing suspension at timed
  intervals ([JH Technologies on the Burst module](https://jhtechnologies.com/?p=1448);
  [AutoMet](https://www.aerospacemanufacturinganddesign.com/product/buehler-semi-automatic-grinder-polishers-automet-112918)).
  A person still changes papers, and the published alloy work inspected the surface by microscope between grits.
- **Robo-Met.3D** (developed by UES; now sold by AV, [avinc.com](https://www.avinc.com/solution/robo-met-3dr/)) moves
  one mounted specimen between motorized polishing, ultrasonic cleaning and an inverted microscope for serial
  sectioning, with autofocus height closing the loop on removal (Madison 2017; Oakley et al. 2025, in the Edison
  answer). Sectioning and mounting before it are not automated.
- **Still hard here**: re-papering, judging the polish (by eye in the SOP), and loading the holder.

## What is an arm move in the chapter, and what isn't

- **Arm moves** (straight lines of the grasp point, planned joint moves, `ARM_AUDIT`): every disc change between the
  magazine and the platen (320 in full, 400 in full, the rest as a time-lapse), and the return to park.
- **Drawn with the machines' own prop joints, not the arm**: the slice into and out of the CNC's vise and its turn-over,
  the coupon onto the press's ram, the stopper and the compound, the slice into the steel mount and its set screw, the
  mounts into the holder. The gripper's pads are 38 mm long (`ur_arm._PAD`) against a 6 mm part, so those moves need
  fingertips of their own or a fixture; that is the next round's.

## Files

- `r8_prep.py`: `mount_press`, `polisher`, `cnc`, `disc_magazine`; `TRAY_PLACEMENT` puts the press at the back left
  of tray F (behind camera F0's post) and the magazine at its front right (right of camera F1's post, in front of the
  UPS and dock plate). Not yet checked with `setup_lab.py fit`.
- `alloy_prep.py`: the chapter; `out/alloy_prep.{gif,json}`, `out/mp4/alloy_prep.mp4`, `out/alloy_prep_still.png`.
- Tour clips: `out/instruments/{mount_press,polisher,cnc}.{gif,png}`, `out/mp4/instruments/...` at 8 fps.
