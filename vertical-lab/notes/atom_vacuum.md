# The explosion-proof vacuum, and the arm vacuuming the inside of the chamber (PR #353, #303)

Sterling, on PR #318 (2026-11-19): "using an explosion-proof vacuum and the same sort of safety workflows as described
here and in DAL (see e.g., nilfisk from #80) (note: you may have missed adding this to the BoM and to the visualizations
with a faithful reconstruction - you should add this in, potentially multiple depending on needs), having the arm grab
the vacuum attachment and doing an actual vacuuming of the inside of the chamber".

| File | What |
| --- | --- |
| [`atom_nilfisk.py`](../atom_nilfisk.py) | The models: the Nilfisk CFM 118EXP, the hose (a relaxed chain), the wand, cuff, crevice tool and dust brush, the steel pail, the Class D extinguisher on its stand, the area sign, and our station |
| [`atom_vacuum.py`](../atom_vacuum.py) | The clip `atom_vacuum` |
| [`atom_ground.py`](../atom_ground.py) | Ground within reach (ours): the bonded floor plates at every spot a MiR250 works at the atomizer, their channels and the ground bar; the MiR250's two sprung shoes and its bond lamp |
| [`out/atom/vacuum_bom.json`](../out/atom/vacuum_bom.json) | The bill of materials, with the vacuum count |
| `out/atom_vacuum.{gif,json}`, `out/mp4/atom_vacuum.mp4`, `out/atom_vacuum_still.png` | The render |
| `out/collisions/atom_vacuum.json`, `out/collisions/atom_vacuum_hose.json` | The arm audit and the hose check |

## Sources

- **Vacuum SOP**: byu-vcl PR 80, `vacuum-operating-sop.md` (Rev 1, 2026-09-04), cited as "SOP section".
- **Accessories doc**: byu-vcl PR 80, `vacuum-accessories-options.md`: part numbers, prices, the bin's size, the OEM
  manual's accessory BOM 01760495 and its continuity rule (sections 11, 15).
- **DAL atomizer SOP** (`253_atomizer-sop.md`), "Powder Collection and Cleaning" step 7: "Clean the chamber, view port,
  crucible and crucible stand, and the splash plate and cone down to the cup. Vacuum with the ATEX vacuum, then wipe.
  Never compressed air." "Copper Alloys" step 1: "Keep copper and Al residues apart (Al with copper oxide is a thermite
  pair)."
- **DAL detailed SOP** (`178_sop.md`), "Cleaning and maintenance": vacuum first, then wipe; the only crevices are the pump
  port and the view port (T4 6:51, T7 1:14); the cone swings out, take it down and vacuum its seal from below (T4 8:08);
  material change: vacuum everything, about 1 h (T5 67:38). `178_equipment.md`: the ATEX vacuum in hand is a Nilfisk
  CFM 118EXP; full liners go in a labelled metal bucket (Risk Management, 2026-07-20).
- **Nilfisk 118 EXP/EXPW brochure**, as quoted by a web search on 2026-11-19 (Nilfisk's spec page and PDF returned
  403/429 to the fetch): 6.6 gal tank, 20 x 24 x 45 in (L x W x H), 57 lb, CSA Class I Group D, Class II Groups E, F, G;
  304 stainless container, filter chamber and trolley.

## The model (`atom_nilfisk.py`) and where each size comes from

| Part | Size | Source |
| --- | --- | --- |
| Overall | 508 x 610 x 1143 mm (20 x 24 x 45 in), 25.9 kg | brochure |
| Bin | 320 mm ID, 311 mm deep (6.6 gal at that ID), 406 mm over the rim gasket | accessories doc 9.5, 10.4 (12.5 in ID), 10.7 ("about 16 in" with gasket); depth computed |
| Main filter | 360 mm antistatic sleeve, 40000460 (not drawn: inside the housing) | accessories doc 2a |
| Inlet | 38 mm (1.5 in) stub on the bin's side, z 410 | accessories doc header; height estimated from photos, +-40 mm |
| Filter chamber, motor head, downstream HEPA housing | z 440-700, 700-905, 905-965 | estimated from photos, +-50 mm |
| Trolley | 440 mm wheelbase, 50 mm castors | estimated inside the brochure's envelope, +-40 mm |
| Switch | sealed box with a rocker on the motor head | estimated from photos |
| Electrics | 120 V, 10 A, 1000 W; 130 CFM; 69 in water lift | accessories doc header (a used listing says 95 CFM, 85 in: not used) |
| Wand 01768601 | 508 mm (20 in), 38 mm OD | **length assumed** (+-150 mm): no source gives it. Measure the lab's |
| Cuff 4072000343 | 52 OD x 90 | estimated |
| Crevice tool 01768900 | 279 mm (11 in), flattening to a 34 x 11 mm slot cut at about 45 deg | length from the accessories doc 3b; slot estimated |
| Dust brush 01719401 | 76 mm (3 in) head, 28 mm conductive bristles, 120 mm long | estimated (the Ruwac kit's brush is 3 in) |
| Hose | 3048 mm (10 ft), 50 mm OD | 107413543 / 01769218, accessories doc 1; OD estimated |
| Pail Uline S-7344 | 340 mm (13.4 in) tall, 298 mm top OD, 273 mm bottom OD | Uline's S-20030BL figures (Hydrobuilder listing), a proxy: S-7344's own sizes were not found |
| Class D extinguisher Amerex B570 | 13 x 8 x 35 in, 30 lb NaCl | Airgas listing |

The tools share one collar design (a 17.4 mm spigot into the wand's 35 mm bore, a 44 mm collar ring, a 38 mm neck), so
the rack can hold any of them. The spigot and collar sizes are estimates.

**The hose** is a chain of 50 links (62 mm each) relaxed every frame by position-based dynamics: gravity, fixed link lengths, a bend
limit (no kink tighter than about a link in radius), the floor with friction (nodes resting on it don't slide),
and obstacles (the MiR250 and its cabinet, the vacuum, the station, the chamber, the open door and stack, the pump, the
pail, the arm's links as capsules, the wand). Each end leaves along its fitting's axis. Its drawn length stays within
about 3 % of 3048 mm (the links stretch a little under gravity).

## Who does what

| # | Step | Who | Source |
| --- | --- | --- | --- |
| 0 | After the run: cold, vented, door open; powder brushed into the container, the container's valve closed and the container taken off | a person (other clips) | DAL SOP collection steps 1-3 |
| 1 | Area checks: the vacuum's ground cable to the ground bar, the station and the pail bonded, extinguisher and pail staged, sign up | a person at the start of the day; the clip shows the result | SOP 2.2, 2.3 |
| 2 | MiR250 2 parks in front of our station, on its bonded floor plate; it lowers its two shoes, the two bond readings pass and its lamp turns green before the arm moves | MiR250 2 + the station's monitor | ours (below, "Ground within reach"); NFPA 484 (2015, 8.5.2) via `atom_sleeve.md` |
| 3 | Take the wand (crevice tool fitted) from the holster by its fin | arm 2 | ours |
| 4 | Continuity: the tool tip on the bonded spring pad, three spring probes on the joints, a relay box switches the 4-wire meter; each joint <= 0.1 ohm, the hose <= 1e4 ohm, the body < 1 ohm to ground, or the run stops | arm 2 + our fixture | OEM manual (UL 1213 par. 22, accessories doc 15.1), SOP 1.1 |
| 5 | Equalization touch on the bonded ground button, away from the powder | arm 2 | SOP 3.1 |
| 6 | Vacuum ON before the powder (a switched outlet, ours) | the cell | SOP 3.2 |
| 7 | Passes through the door: round the inside of the view port; down the 45 deg floor towards the outlet in two lanes (the floor is the funnel to the outlet); along the front corner where the floor meets the front wall | arm 2 | DAL SOP step 7; 178 SOP T4 6:51; SOP 3.3-3.5 (slow, nozzle close, never blow) |
| 8 | Tool change: the crevice tool into pocket A (its collar between two slotted plates), the wand pulled off it, the wand pushed onto the brush in pocket B, out to the front | arm 2 + our rack | ours |
| 9 | Brush-and-capture: the brush on the plate (on the open door), then along the door's sealing face (its free edge and top) | arm 2 | SOP 3 (brush), DAL SOP step 6 (door, plate) |
| 10 | Lift clear; run-on 20 s in clean air; OFF; wait >= 60 s; liner check <= 25 % | arm 2 + the cell | SOP 4.1-4.3 |
| 11 | Wand back in the holster | arm 2 | ours |
| 12 | Liner sealing (gooseneck, 2-3 turns, ESD tape or two steel ties), lifting it into the pail, lid set on, a fresh liner; wiping the tools (dry, then a barely damp 70 % IPA wipe), the session log | **a person** | SOP 4.4, 5, 10 |
| 13 | The catch bowl and the round end, the cone taken down and its seal vacuumed from below, the view port taken out with the hook wrench | **a person** | 178 SOP T4 7:49, 8:08 |

The arm stays outside the chamber: only the wand and the tool go through the door. The tool never touches what it
cleans except the brush's bristles (a soft part in the audit) and the two spring contacts.

## What is ours, and why

- **The wand's clamp collar and fin.** The OEM manual: "Any alteration to this equipment by a third party will nullify
  its certification" (accessories doc 15.1). So the collar clamps on (54 mm OD, 60 long) and nothing is drilled. The fin
  is 30 mm thick, so the 2F-85 closes to 0.68 (`ur_arm.close_for(30.3)`). The 6 mm pin under the collar drops into a
  hole in the holster's fork, so the wand always hangs in the same roll and the arm's grasp repeats. Open question: the
  collar must be conductive and bonded to the wand (an isolated conductor is the hazard the SOP hunts for, 2.3), or
  non-conductive and small; ask Nilfisk and EHS which.
- **The station** (two: one per vacuum station): a bonded steel post with the holster, the tool rack (two keyhole
  pockets: the lower plate carries a tool by its collar, the upper plate holds it down while the wand pulls off), the
  continuity fixture (a spring pad, three spring probes on a column, a relay box) and the ground button, and the meter on
  a shelf under the rack. The spring parts (pad, probes, button) are soft parts in the audit, as plungers are. The
  vacuum stands to the station's left with its inlet turned to the back, so the hose runs behind the station's base and
  rises behind its post to the holster.
- **The automated continuity check.** The SOP's meter (EXTECH 380560 class, resolves 0.01 ohm) reads 4-wire through a
  relay box that switches its leads between the probe pairs: tool tip (pad) to the wand above the tool joint; the wand
  under the collar to the cuff; the cuff to the vacuum's inlet; the body to the ground bar. The readings on screen
  (0.04, 0.02, 0.03, 4.1 and 0.2 ohm) are illustrative. **The lab's own crevice tool read open (megohms) on 2026-08-19
  (SOP gate 0.1)**: until the SOP's remediation ladder (1.4) clears it, the fixture would stop this run, and the SOP's
  fallback is the dust brush alone.
- **The liner fill** is shown from an assumed load cell under the trolley; the SOP checks it by eye when the head comes
  off. **The vacuum's switch**: a switched outlet controlled by the cell, not a change to the vacuum; to clear with
  Nilfisk and EHS.

## Forces and timing

- Tool push-on and pull-off: about 30 N, assumed (a slip fit; not measured). The UR10e's 12.5 kg payload and the 2F-85's
  20-235 N grip are far above the wand set's weight (aluminium wand and tools, under 1 kg, plus part of the hose's
  weight, assumed under 1.5 kg).
- Passes at about 30 mm/s (SOP 3.3: "slow, deliberate"); the view port ring (240 mm) in 9 s, each 250 mm floor lane
  in 8 s, the bowl in 7 s.
- The run-on (20 s) and the settle (60 s) are shown as time-lapses with a timer gauge.
- The whole clip is about 2 minutes of screen time; at real speed the session would take about 5 minutes plus the
  person's liner work.

## How many vacuums: three

1. **Atomizer, Al family** (AlSi10Mg, Si, 4047, 6063): the 118EXP the lab has.
2. **Atomizer, Cu family** (NAB, 630 bronze): a second 118EXP with its own hose, wand, tools, filters and pail, all
   labelled. DAL's SOP keeps Cu and Al residues apart (Al with copper oxide is a thermite pair), and the vacuum SOP
   (section 6) says a switch between the families needs the main filter and both HEPA filters replaced, a full IPA clean
   of the bin, hose, wand and tools, a fresh liner and a fresh pail. At the accessories doc's lowest quotes the filters
   alone are about $1,200 a switch ($353 + $243 + $603), plus about an hour of cleaning (178 SOP T5 67:38). The lab ran
   copper on Oct 27, Oct 28 and Nov 5 between Al runs, so a second unit pays for itself in a few switches, and no
   thermite residue ever shares a bin.
3. **The printer line, Al family**: the Aconity MIDI's depowdering lance (notes/alloy_workflow.md, round 5: the arm
   vacuums the build cylinder with a lance on a post) needs an ATEX suction source at the printer, and the sieve station's
   bench (notes/alloy_print.md: a downdraft enclosure with its own extraction) needs a vacuum for spills. One 118EXP on
   that line serves both; wheeling vacuum 1 across the floor with its hose would mean a hose crossing the MiRs' paths.

**Cost** (the BoM): the vacuums themselves have no published price (quote needed). For vacuums 2 and 3 the priced items
are two hoses ($1,292), two wands ($350), two crevice tools ($106), three main filters ($1,059), three upstream HEPAs
($729), two downstream HEPA kits ($1,206), two cases of liners ($410), two pails ($48) and bonding hardware ($15):
**about $5,200**, plus two dust brushes (about $20-40 each, estimated), two Class D extinguishers (Amerex B570, quote) and
our two stations.

## The render and what was checked

**2026-11-20 (this round).** The clip with the sign fitted, the floor plates, the bond step and the tool rack approached
from a pose clear of the station.

- **The render.** 149.3 s, 2240 frames at 15 fps, 1920 x 1080 (`VIZ3D_HD=1`), rendered and audited in one pass.
  - `out/hd/atom_vacuum.mp4` with its text-free copy in `out/clean/` (both git-ignored; the 1080p file is
    force-added);
  - the 720p copy `out/mp4/atom_vacuum.mp4`;
  - `out/atom_vacuum.gif`, from the 720p copy at 3 fps and 448 px to stay under 5 MB;
  - `out/atom_vacuum_still.png`, the first floor lane at 74 s;
  - `out/atom/atom_vacuum_bond.png` (the lamp green) and `out/atom/atom_vacuum_sign.png`.
- **Arm audit** (strict, round 11 rules, 15 fps): **0 of 1836 checked frames**; movers 0. Round 13 left 1 frame: the
  crevice tool 1.5 mm into the station during the joint move to the tool rack. The move now goes by way of a pose
  150 mm further out and 180 mm higher, then down in a straight line.
- **The hose check** (`out/collisions/atom_vacuum_hose.json`) stays as before in kind. The hose rests on and against our
  station in every frame, its drawn tube 3-6 mm into the station's base, post and lug where it bends over them.
  - It lies in the gripper's left finger and fingertip in about 50 of 1836 frames, holding the wand by the fin with the
    hose hanging from the cuff just above.
  - With the gripper's knuckles and fingers added to the hose's obstacles, that fell to 41 frames, but the hose then lay
    in the rePowder's vacuum pump in 140 frames instead of 16, so they were left out.
  - A finer chain (the links are 62 mm) is the fix.

**Round 12 (2026-11-19).**

- **The clip**: `atom_vacuum`, 142 s, 1420 frames at 10 fps (`VIZ3D_FPS=10`: the render queue was full), 1280 x 720;
  `out/mp4/atom_vacuum.mp4` (8.0 MB); `out/atom_vacuum.gif` re-encoded to 512 px with every other frame (3.5 MB: the
  scene's own GIF was 8.7 MB); `out/atom_vacuum_still.png` is the first floor lane (taken from the MP4 at 68 s).
- **Arm audit** (rendered and audited in one pass, round 11 rules): **11 of 1184 motion frames in collision**, all in the
  last holster steps: the UR10e's upper arm against the vacuum's body (frames 1346-1350, the joint move from the clear
  pose to above the holster) and against its own wrist 2 (frames 1399-1404, the final back-off). Not fixed: there was no
  time for another render. The fix is to back off upwards first and park the arm by a planned joint move, and to keep
  the arm's elbow on the station's side, away from the vacuum. Everything before that (taking the wand, the
  continuity check, the equalization touch, the passes inside the chamber, the tool change, the brush) is clear. The
  movers check: 0 frames.
- Earlier audits on the way, and what each fix was: 788 frames (the tool through the meter shelf at the fixture, the
  crevice slot's edges in the floor and the wall, the tool in the outlet's cone); 232 (the gripper and wrist at the
  door during the catch bowl); 259 and 56 (the wand and tool through the station's post on the way to the rack, from a
  "clear" pose I had picked inside the post; the probes on the fixture); then 11.
- The hose: its own FCL check every audited frame against everything but the wand, its tools, the vacuum's inlet, the
  floor's markings and the ground cables (`out/collisions/atom_vacuum_hose.json`), with `collide.depth` for how deep.
  Result: it never enters the vacuum, the chamber, the MiR or the arm's links, but it **rests on and against our
  station** in every frame, and the drawn tube sinks 3-6 mm into the station's 14 mm base plate (890 frames), its post
  (736) and tool rack (129), the station's ground lug (246) and the vacuum pump's casing (87); it touches the gripper's
  fingertips in 7 frames. The links are 62 mm and the tube is drawn through a spline, which cuts the corners where the
  hose bends over an edge. A finer chain or a route that keeps the hose off the station is the fix.
- The tool's reach through the door: with the crevice tool the grasp point is 648 mm behind the tip. For the floor's
  lanes down to x = 212 the gripper stays outside the door; the catch bowl (its near rim at x = 232, 290 mm past the
  door at the floor's foot) put the gripper and the wrist into the door's front edge and the swung clamps in the audit
  (it is about 650 mm from the tip to the door), so the arm does not do it: a person does, or a second wand section
  would (not modelled).
- The crevice tool's slot (34 x 11 mm) has a wide side: it is fitted turned 90 deg on the wand, so with the fin towards
  the arm the slot lies across the floor's lanes; for the view port the wand is rolled so the fin is up (the gripper
  above the wand) and the slot lies flat to the front wall. Each roll was chosen after the audit found the slot's edge
  in the floor and the wall.
- The dust brush cannot meet the 45 deg floor square from the door (the floor faces up and away from the door, so the
  brush would meet it at about 17 deg and its head would scrape): the floor is done with the crevice tool, which drags
  at that angle as it is meant to, and the brush is used on the plate and the door's sealing face, which face the arm.

## Ground within reach (2026-11-20)

Sterling, on PR #318 (2026-11-20, at 25:53 of round 12's long-form): "Nice on having a ground cable and ground bar or
similar. I wonder about trying to have a mobile ground bar of sorts (overhead), or maybe better, just making sure ground
is available within close reach pretty much anywhere nearby machines or where the mobile manipulator would be."

**Why a MiR250 needs it.** [`atom_sleeve.md`](atom_sleeve.md) has the rule: NFPA 484 (2015, 8.5.2) wants mobile metal
equipment bonded or grounded before use. A MiR250 on its tyres is an isolated conductor, and the arm, its sleeve and the
tools it holds near the powder bond through it. The vacuum's own chain (tool, wand, hose, body) is a separate matter: it
is bonded through the vacuum's ground cable and checked joint by joint (UL 1213's 0.1 ohm, above).

**The options**

| Option | For | Against |
| --- | --- | --- |
| An overhead bonded rail with a trolley and a retractable lead | reaches anywhere under the rail; one connection to the building's ground | a lead hanging in two arms' workspace and over the MiRs' paths; the trolley's sliding contact is one more joint to check; an arm has to clip and unclip a clamp at every stop; a ceiling rail to put up and inspect |
| A bonding reel on each MiR250, its lead clipped by the arm to a stud | works wherever there is a stud | an extra grasp, and a spring clamp a 2F-85 must open, at every stop; a cable on the floor while the MiR works; an interlock so it never drives off clipped on |
| Ground studs on each machine, leads clipped by a person | what the lab does now: the vacuum's cable to the bar | a person at every MiR stop |
| **Bonded plates in the floor where the MiRs park, two sprung shoes on each MiR250 (chosen)** | automatic on parking; nothing to clip, nothing trailing, nothing overhead; read every time | floor work at each spot; parking has to land the shoes on the plate; powder on a plate can raise the contact resistance (the reading catches that, and the plates are inside the vacuumed area) |

**The design (ours, [`atom_ground.py`](../atom_ground.py))**

- **Plates.** 304 stainless, set flush (2 mm proud, a stepped edge), wherever a MiR250 parks to work. Each spot's plate
  spans +-148 mm along the MiR and +-214 mm across it, round the two shoes. That covers the MiR's +-60-85 mm without a
  marker (MiR's figure, quoted in round 4), the shoes' +-70 mm spread and a margin.
  - The atomizer's 16 spots are the clips' and chapters' (`ATOMIZER_SPOTS`). Where plates overlap, they are joined and
    laid side by side (`plate_rects`).
  - The lab's floor gets 13 of them: 5 joined areas, 1.16 m² of plate. The other three spots put a MiR250 where the
    machine's vacuum pump or chapter 3's wash module stands (`NOT_IN_LAB`). That is a layout fault in those clips, below.
  - Each joined area has a recessed terminal and two leads in a flush floor channel to the area's ground bar, the bar the
    vacuum's cable already goes to.
- **Shoes.** Two copper-graphite blocks, 46 x 38 mm, 140 mm apart, each on a spring, under a crossbar.
  - A 24 V actuator lowers them 15 mm once the MiR has parked and lifts them before it drives, so they don't drag dust
    or wear on the floor.
  - Everything hangs on a bracket from the top module's ballast plate at the MiR's front end. Nothing is drilled into the
    MiR250 itself.
  - The shoes' leads go to the top module's ground, which the arm's sleeve and tool changer bond to
    ([`atom_sleeve.md`](atom_sleeve.md)).
- **Two readings before the arm may reach for powder or a tool.** A failed reading stops the step.
  1. The MiR's own 4-wire meter: shoe A, through the plate, to shoe B, at most 1 ohm. This shows both shoes are on metal.
  2. The station's monitor: the plate, through its two leads, to the bar, at most 1 ohm. This shows the plate is still
     bonded.
- **The lamp** is on the cabinet's front face: amber until both readings pass, green once bonded.
- **The 1 ohm limit is ours**, deliberately tighter than the published figures for a static ground:
  - NFPA 77 calls a bonding resistance of 10 ohm or less with copper wire (25 ohm with stainless or other metals)
    typical in practice, and a higher one a sign that the metal path isn't continuous (Annex A.3.3.2, 7.3.1.6.1).
  - ESIG's guide asks for a temporary earth of 10 ohm or less for a vehicle on pneumatic tyres standing on a dry floor
    (3.3.5.1).

  Both are as summarised by Newson Gale's page on the standards
  ([industry standards and guidelines](https://newson-gale.com/static-electricity/industry-standards-guidelines/),
  read 2026-11-20); the standards themselves weren't open to read. The readings on screen (0.12 and 0.05 ohm) are
  illustrative.
- **What it doesn't replace.**
  - The vacuum's ground cable to the bar, which a person checks at the start of the day (SOP 2.2).
  - The pail's bonding wire and the station's lug.
  - People's own grounding. If EHS wants static-dissipative footwear (NFPA 484 for dusts under 100 mJ, see
    [`atom_sleeve.md`](atom_sleeve.md)), that needs a dissipative floor where people stand. The plates are only where
    the MiRs park.
- **For EHS and MiR to sign off:** the plates, the shoes and the 1 ohm limits. Also whether a ground path from a top
  module's bracket to the MiR250's chassis is allowed (MiR), and whether the lab's floor can take recessed plates and
  channels.

**On screen.** In `atom_vacuum` (step 3/10, "Bond"), MiR250 2 parks on its plate, lowers its shoes, both readings pass
and its lamp turns green. Only then does the arm reach for the wand. MiR250 1, parked at the right since before the
clip, is already bonded. In the lab's scenes, `lab._repowder()` draws the 13 spots' plates, their channels and the bar
(below).

**Found on the way, not fixed (other clips' files):**

- `atom_crucible`'s MiR250 2 (`MIR2_AT`, -960, -40, turned 90 deg) and `atom_base.PARK["left"]` put the MiR's body over
  the model's vacuum pump (x -880..-420, y 120..340, on the floor).
- `atom_container`'s MiR250 2 (`B_FRONT`) stands where chapter 3 puts the sieve wash module's stand.

The audits miss both: collide.py checks a MiR against the machine only while it moves, and these are parked.

## The area sign (2026-11-20)

The sign's text ran off both edges of its board (25:53 in round 12's long-form): "COMBUSTIBLE METAL" was set 44 mm tall
on one line, about 530 mm wide on a 460 mm board. `atom_nilfisk.fit_text` now measures every line and sets one scale
for the whole block, so the widest line fits inside a 34 mm margin and a 12 mm black border. The warning is in three
lines (COMBUSTIBLE / METAL POWDER / IN USE) and the rules in three smaller ones (Authorized personnel only / NO water /
NO compressed air), with the wording of SOP 2.3. The widest line is now 368 mm on the 460 mm board, and every line sits
inside the margins (checked in code, `sign_meshes.info`). It was the only text board in the atomizer clips.

## Where the atomizer's fixtures now appear (2026-11-20)

Sterling (21:12 in round 12's long-form): "the atomizer is missing the new renders in other spots across the video".
Every lab scene draws the rePowder from `lab._repowder()`, which tessellates `repowder/model.py`, so they already had the
turned lid and #353's latch wherever they were rendered after #353 merged. #353's fixtures were only in its own clips.
`lab._repowder()` now adds:

- DAL PR 189's three viewport camera units with their displays (front, left and top), as `atom_cams` places them: the
  door shut, the top arm in its working dimple over the lid window. DAL's port nut and glass replace the model's port
  flange and glass, as in the clips.
- The bonded floor plates at the atomizer's working spots, their channels and the ground bar (above).

The scenes that draw the merged rePowder, and so show these once re-rendered:

- the set-up movie (`setup_lab.py`);
- chapter 3, the sieving cell beside the rePowder (`alloy_print.py`, through `alloy_workflow.build`);
- chapters 1, 4, 5, 6 and 7 in their wide shots (`alloy_charge.py`, `alloy_powder.py`, `alloy_workflow.py`,
  `alloy_prep.py`, `alloy_characterize.py`);
- the finale (`timelapse.py`);
- the maintenance clip (`upkeep_clip.py`);
- the services clips (`services.py`, `ups.py`);
- the older `animate.py`, `line.py`, `warehouse.py` and `reach.py`.

Chapter 2 (`alloy_atomize.py`) hides the merged copy and loads the model part by part. It shows the camera units only if
it calls `atom_cams.add_units(sc)`, which works on its scene, and the plates only if it adds
`atom_ground.plate_meshes(...)`. Changing `lab.py` changes the key of all three of `lab.meshes()`'s caches, so each
scene re-tessellates once (about 10 s here).

Not checked by a render:

- The front unit stands out to y = -355 in the model frame, at z 918 and up, above a docked MiR's cabinet (z 800). A
  chapter 3 or set-up arm that sweeps past the chamber's front at that height would meet it, and the audit of their
  next render will show it.
- In the set-up movie the plates, being part of the merged rePowder, arrive with the machine when it is set down.

## Not done, or assumed

- The wand's length (20 in), the tools' spigot and collar, the hose's OD and the trolley are estimates; measure the lab's.
- The door's seal is not in the rePowder model, so the brush pass follows the band where the door meets the chamber's
  face (6-12 mm in from the door's edge), along the free edge and the top only (the stack's port is in the way lower down).
- The chamber's own valve is taken as closed with the container off (the airlock), so nothing falls out of the outlet.
- The meter readings are illustrative; the load cell and the switched outlet are assumptions to clear with EHS.
- The person's steps (liner, wiping, the far side of the bowl, the cone from below) are captions, not animated.
- Open questions for the lab: the wand's length; whether the collar should be conductive (bonded) or insulating; whether
  EHS accepts a robot-switched outlet for the vacuum; Nilfisk's written clearance on the crevice tool (SOP gate 0.4);
  whether one extinguisher can serve both atomizer vacuums (they are side by side).
