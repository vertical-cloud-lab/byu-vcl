## Round 11: chapter 5 after Sterling's review of 2026-11-13

Two of Sterling's points on the round-10 long-form were this chapter's: "at 32:57 the arm passing through the camera /
collision" (his screenshot: the gripper and the tongs through the post of a stream camera beside the furnace on tray
F), and "Insertion / removal of the tensile bars (and the halves) have another collision. Not sure if the gripper has
enough clearance. Maybe OK if angled, otherwise needs it's own tool/end effector." The chapter's final render had never
been audited frame by frame (round 9 stopped that audit, round 10 didn't rerun it), and this round's audit is stricter
(`collide.py`, audit-a): what the gripper or a held part may touch near a grasp or release counts only up to 1.5 mm
deep, and everything else that moves is checked too (the movers check).

| | |
|---|---|
| MP4, 1280 x 720, 6 fps, 412.3 s, 2,474 frames (rendered 02:00-02:54 UTC from 86ff959, only tray F populated, Shuttles clad; section 7, frames 1766-2473, re-rendered from 5f16a3c with the test's camera raised and spliced in at the section boundary) | [`out/mp4/alloy_workflow.mp4`](../out/mp4/alloy_workflow.mp4) (21.7 MB) |
| GIF, 276 px, 2 fps, from the spliced MP4 (under the 4.9 MB budget; not used in the long-form) | [`out/alloy_workflow.gif`](../out/alloy_workflow.gif) (4.8 MB) |
| The audit of what was rendered (`ARM_AUDIT=1`, round 11's strict rules, every frame at 6 fps): 1 of 2,089 frames | [`out/collisions/alloy_workflow.json`](../out/collisions/alloy_workflow.json), the frame: [`alloy_workflow_01347.jpg`](../out/collisions/alloy_workflow_01347.jpg) |
| The same rules on round 10's code (F1 already moved): sections 1-5, sections 6-7 | [`alloy_workflow_s15.json`](../out/collisions/alloy_workflow_s15.json), [`alloy_workflow_s67.json`](../out/collisions/alloy_workflow_s67.json) |
| `PREVIEW=1` stills: the specimen fingers in their stand, a bar going into the lower grip, the halves | [`out/alloy_workflow_preview.png`](../out/alloy_workflow_preview.png) |

### What changed

1. **Camera F1 stands behind the quench tank** (`services.TRAY_CAMS["F"]`, commit 6c690a0). At 32:57 (242 s into the
   chapter) the tongs carry the rack from the furnace's front to the tank's lift basket. The tank had been moved
   behind F1's post when two streams' placements collided (`setup_lab.R8_MOVES`), so the post stood at (685, -235) on
   the tray, in the middle of the tank's front: the rack's 150 mm sweeps x 605-755 from the tray's front edge to y -35,
   and the tongs' shaft and the 2F-85 follow it. Nothing fits in front of the tank beside that path (the furnace ends
   at x 535, the disc magazine starts at 844), so the post now stands behind the tank at (680, 130), 16 mm behind it
   and 100 mm in front of the UPS (the tray's lines run along the back rim, at y 388 and over). Its head is over the
   tank's back edge and looks down into the tank at the 65 deg tilt limit: the HQ's axis meets the rim at y -95, where
   the rack goes in and comes out, and the Wide takes in the furnace's right side and top as well. Behind the tank it is
   clear of every path in chapters 5 and 6 (chapter 6 works the PX500, the press and the magazine's front). The cost:
   with the tray presented, 22 % of the Wide's picture is the room through the opening's lower part (0 % for the HQ);
   the old place saw none of the room. F0 (front left, by the press) is in no path of chapter 5; chapter 6's audit
   (audit-b) covers it. Two comments elsewhere still describe the old place (`setup_lab.R8_MOVES`, the lab's;
   `r8_prep.TRAY_PLACEMENT`, audit-b's).
2. **Specimen fingers for the 2F-85** (`ur_arm.SPEC_FINGER`, `spec_finger_meshes`; `robot.FingerSet`; the stand
   `alloy_models.FINGER_STAND`). Why a tool: after the break each half of the E8 subsize bar has 20 mm free between its
   broken end and its grip (40 mm between the jaws, broken in the middle). In a level grasp the 2F-85's fingertips are
   27 mm tall and its inner knuckles 35, so no level grasp clears both the grip and the other half; tilting the gripper
   makes it worse, because the 57 mm fingertip then reaches up or down as well. The stock fingertips also caught the
   next bar in the comb and the rack (3-12 mm) and the jar's air knife on every dip (12 mm). What automated cells do:
   ZwickRoell's roboTest C lists a pincer gripper with a 26 mm stroke whose "gripper finger (depending on specimen
   thickness) must be offered for the gripper" (articles 640332 and 010245), i.e. fingers made for the specimen; the
   Volvo/ABB cobot cell in Bosio's thesis holds the specimen in padded jaws, sets it in the lower grip first and finds
   each broken half with a distance laser to take them out separately ([`out/edison/auto_tensile/answer.md`](../out/edison/auto_tensile/answer.md)).
   Our design, after those: two aluminium caps that slip over the 2F-85's own fingertips (a spring plunger in each holds
   it on), each ending in a blade 4 mm thick and 8 mm tall that reaches 73.6 mm past the stock pad centre, its inner
   face 2 mm inside the pad's. The arm fits them from a two-slot stand on the MiR's cabinet top, behind the rack (a
   spring clip in each slot holds the blade while the fingertip draws out of the cap), and takes them off again before
   the tongs and the jar's lid, which want the stock fingertips. It wears them for the bars at the EDM (comb, jar, rack)
   and for both tensile tests. The audit checks them as real geometry: they are held parts (`FingerSet` places each on
   its fingertip every frame as the gripper opens and closes), so collide.py tests them against everything.
3. **The Instron, loaded and unloaded with real clearances** (`alloy_workflow` section 7, `r8_test.wedge_grip`).
   What collided in round 10: the bar's foot went into the lower grip on a slant, 40 mm down while 20 mm forward, so it
   cut through the grip's front before it reached the slot; the second bar went in under the upper grip, which the first
   test had left 210 mm down; and the stock fingers took each half partly inside its grip and pulled it through the
   grip's block. Now:
   - the grips have jaws: a 28 x 20 mm slot in each block with two jaws, 2 mm off each face of the specimen while open,
     that close on it (instruments.py's grip had a 6 mm slot, closed for good on the 6 mm bar);
   - the bar goes in straight down between the open jaws from 60 mm over its seat, the jaws close, the fingers open
     and draw straight back; the blades hold it 53 mm over the grip and the 2F-85 itself stays in front of the grips;
   - after the break the crosshead backs off 60 mm (20 before), so the lower half lifts 40 mm out of its jaws and the
     upper half drops 40 mm out of its own without meeting the other; the blades take each 10 mm from its broken end,
     6 mm clear of the grip and of the broken end;
   - the room-temperature halves lie in the MiR's cradle as before, which now has a relief across each channel for the
     blades; the hot test's halves drop onto the scrap chute's floor (they used to fall through it) and slide away;
   - the crosshead goes back up after each test (round 10 left it 210 mm down, so the second bar went in under it).
     Its rest height met the junction box the set-up hung on the south row's drop at the Instron (z 1720-1900, 90 mm
     into the crosshead); the lab moved the box over the frame (47219fc);
   - the chamber's door shuts against the chamber's front face; drawn inside the shell's frame, it went 50 mm into the
     shell every time it shut.
4. **The MiR stops 500 mm off the Instron, not 230.** The 3119-608's left-hinged door is 550 mm wide and opens 95 deg,
   its free edge 432 mm in front of the frame. At 230 mm it went through the MiR's cabinet, the tongs and the arm's
   base every time it opened (the movers check). At 500 mm it clears the MiR by 68 mm and the arm still reaches the load
   string. The lab moved the set-up's dock mark at the Instron to this stop (47219fc).
5. **The rest of the strict audit's findings**, section by section:
   - the plate's zero-point stud stood inside three solid parts: the printer's platform, the depowdering box's chuck and
     the EDM's receiver are bored for it now (0.5 mm round it);
   - the build cylinder is 171 mm across (the 170 mm plate rose through a 170 mm hole in the chamber's floor), the
     printer's base cabinet is cut for the cylinder and the piston's rod, and the powder cake counts as a fluid (the
     bars are buried in it);
   - the plate rides to the box 150 mm further from the row (MiR y 150, not 300): driving past the lance's post, the
     plate and the bars standing on it went through the hose where it leaves the lance's barb;
   - the box's swing clamps swing in 3 mm over the plate and close 0.1 mm over it (round 10: 1.5 mm into it);
   - leaving the box, the MiR drives 350 mm along the row before it turns: turning on the spot there, its corners swept
     over the floor pipe in front of the row;
   - the EDM's catch comb rides on a slide: the plate goes onto its receiver along the stud's axis, so its bars came in
     through the comb's front wall and teeth; the comb now waits 88 mm down in the table's window and rises under the
     bars once the plate is clamped (our design). Its ejector pins rise through holes in its floor and pads, and the
     wire head's lower guide runs 8 mm under the comb's ejector block, not 4 mm in it. Its arms reach round the
     plate 165 mm out, not 112, so the wire, which starts 150 mm left of centre, no longer crosses the left one, and
     the angle plate is 350 mm wide to take them; after the cut the head parks 125 mm right of centre, clear of the
     last bar's finger caps;
   - the closures leave 0.3 mm over each part (`ur_arm.close_for`): round 10 squeezed the lug and the tongs' handle by
     0.17 mm and the lid's knob by 0.02, which the depth limit reads as 3-6 mm (the move that frees a squeezed part is
     along the pads);
   - the tongs' jaws are 42 mm tall (at 50 they reached 3 mm into the rack's top beside its fin) and the tongs lie 90 mm
     further out on the cabinet, 325 mm off the arm's axis: at 233 mm the arm folded so far to reach the handle pointing
     down that its shoulder met its forearm. Their rest's V-blocks stand 95 mm either side of its middle: the sleeve at
     the handle, 4 mm fatter than the shaft, sat 4 mm into the left one;
   - the lid's knob is taken 4 mm under its top, not 12 (the fingertips reach 19 mm past the grasp point and were 5 mm
     into the lid), the plate's stud goes into the box's chuck straight down for its last 30 mm, the bars' last moves
     out of their troughs are planned joint moves, the box's clamps and the comb's pins as above.

### Collisions: the audit

The chapter as rendered (86ff959), every frame at 6 fps under round 11's strict rules (`ARM_AUDIT=1 ARM_AUDIT_SNAP=auto`,
02:00-02:58 UTC, in parallel with the render): **1 of 2,089 frames** in collision, and no mover's new contact deeper than
1.5 mm. The same rules on round 10's code (with F1 already moved) found 40 of 962 frames in sections 1-5 and 70 of 1,003
in sections 6-7, plus the movers listed under 3-5 above; round 10's own rules on round 6's code had 60 of 2,101.

- **The one frame** (1347, section 6): as a planned joint move swung the tongs from their rest over the rack on the MiR
  to the rack's fin, the shaft grazed the top of a specimen standing in the rack, 3 mm, between the planner's 1.5 deg
  samples ([`alloy_workflow_01347.jpg`](../out/collisions/alloy_workflow_01347.jpg)). Fixed in code after the render
  (the tongs go to 140 mm over the fin's grasp first, the jaws 66 mm over the specimens, then down in front of the fin;
  and up 140 mm again before the swing back to their rest) and not re-rendered, as the coordinator asked.
- **The MiR check** (`alloy_workflow_mir.json`, the MiRs against everything): 210 frames, all in sections 1-2, the MiR's
  skirt on the foot plate of the Aconity's target post. The post stands 650 mm behind the Aconity's dock at (6650,
  -1932) (it is backed into), at (6000, -1712), on a 300 x 300 x 12 mm foot; chapter 5's MiR stops 130 mm left of that
  dock and 150 mm further out, at (6520, -2082), because the plate has to clear the chamber's front. The skirt (z 0-30,
  20 mm inside the body) overlaps the plate by 10 x 50 mm at its rear corner: 10 mm to free, 12 on collide.depth's
  ladder. It is hidden under the body's overhang in every shot, but a real MiR's corner caster would ride onto the
  plate. The lab moved the Aconity's dock to chapter 5's stop, its post 120 mm clear (1c36cef), after the render.
- The MiR body on the floor tape, the trays against the VLM's column supports and the shutter against the bay's walls,
  which the first passes showed, are not this chapter's: audit-a's movers check ignores the floor and its tape since
  d9184d6, and the coordinator's 063b014 fixed the VLM's.

### Sources (round 11)

- ZwickRoell, roboTest C product information ([PDF](https://www.zwickroell.com/-/media/files/sharepoint/vertriebsdoku_pi/01_722_robotestc_pi_en.pdf)):
  "Feed unit with pincer gripper; Gripper stroke: 26 mm; Max. specimen thickness: 30 mm", and "An associated gripper
  finger (depending on specimen thickness) must be offered for the gripper" (articles 640332, 1.5-25 mm, and 010245,
  6-30 mm).
- Instron AT6: a Mitsubishi six-axis robot; the 100 kN configuration uses hydraulic wedge action grips
  ([Plant Automation Technology's copy of the product page](https://www.plantautomation-technology.com/products/instron/at6-6-axis-robotic-testing-system)).
  Instron's own page refused the fetch (HTTP 403); neither says how the AT6 holds or removes a specimen.
- The Volvo/ABB cobot tensile cell (Bosio 2025) and Sandia's rack-fed tester (Heckman et al. 2020), as summarised in
  [`out/edison/auto_tensile/answer.md`](../out/edison/auto_tensile/answer.md): padded robot jaws, the lower grip first,
  a distance laser to find each broken half; gas ejecting the upper half.
- The 2F-85's fingertip and knuckle sizes are measured from Robotiq's own description (`ur_arm.gripper_meshes`).

### Assumed, and left open

- The specimen fingers, their stand and the plunger that holds each cap are our design; ZwickRoell's sheet says only
  that a finger per specimen thickness comes with the gripper. Robotiq makes no automatic fingertip change for the
  2F-85: a tool changer with a second gripper would do the same job.
- The break is in the middle of the gauge here, every time. A real bar breaks anywhere along its 32 mm reduced section,
  which can leave a half only 4 mm to grip; Bosio's cell finds each half with a distance laser, and the D405 on the
  wrist would do the same here.
- The jaws close by a straight move across; a hydraulic wedge grip's jaws ride down a wedge.
- F1 behind the tank sees 22 % room in its Wide with the tray presented (see 1).
- The tongs' path fix and the Aconity's dock (above) are in code, not in the render.
- **The tensile tests were hidden in the 02:00 render.** The set-up had moved the Instron dock's AprilTag target post
  to 150 mm off the face west of the door (47219fc, an hour before), 80 mm off the line of sight of the test's camera
  (`CAM_TEST`), so its cube covered the specimen and both grips through both pulls. `CAM_TEST` now looks from 1600
  mm, not 1150, its axis 161 mm over the cube's top, and section 7 was re-rendered alone (`CH5_FROM=7`, 742 frames,
  03:43-03:58) and spliced in at frame 1766 (`/tmp/ch5/splice.py`: section 7 is 708 frames in both, the total
  2,474). The arm audit is unchanged (a camera). A run of section 7 alone starts its status panel from section 1's,
  so the splice shows "Plate: in the Aconity MIDI" through section 7 and no Bar line; the panel is set for it now
  and a second section-7 run was queued at 04:01 to fix that, if it lands in time.
- While the specimen fingers are on, the 2F-85 takes nothing else: they go on at the EDM for the bars, come off
  before the jar's lid and the tongs, and go on again at the Instron; each fitting or removal takes about 3 s.


## Round 9: chapter 5 after Sterling's review of 2026-11-05 22:56 UTC

Six points on PR #318 were this chapter's: the Aconity MIDI's door "swings the wrong way"; "28:08 that vacuuming seems
pretty clearly to have interference with the machine"; "It's not clear how that depowdering box actually gets the plate
to stay on it. Is it clamped somehow?"; tensile bars "at different orientations ... How is that going to work with the
automated EDM process? Do this, and also open a new PR focused on that"; "The angle and transparency at 32:20 is off.
Can't see the tensile test happening. Can't tell if there are collisions. Something weird with that heated box"; and
round 8's open item, six joint moves ending in a pose already in collision, the chapter never audited frame by frame.

| | |
|---|---|
| MP4, 1280 x 720, 6 fps, 385 s, 2,309 frames (rendered 06:01-06:59 UTC, only tray F populated, Shuttles clad; the planner reported no joint move starting or ending in collision, against round 8's six) | [`out/mp4/alloy_workflow.mp4`](../out/mp4/alloy_workflow.mp4) (19.4 MB) |
| GIF, 380 px, 2 fps | [`out/alloy_workflow.gif`](../out/alloy_workflow.gif) (4.7 MB) |
| `PREVIEW=1` stills: the lance, the cut with the vertical bars, a vertical bar picked and racked, the specimen loaded, the pull as a cutaway | [`out/alloy_workflow_preview.png`](../out/alloy_workflow_preview.png) |
| The separate PR: the three orientations on the EDM | branch `claude/issue-303-edm-orientations`: `edm_orientations.py`, `notes/edm_orientations.md`, `out/edm_orientations.png` |

### What changed

1. **The MIDI's door lifts** ([`alloy_models.door_T`](../alloy_models.py), `DOOR_OPEN`). Rounds 4-8 hinged it on its
   left edge and turned it +100 deg about z, which swung its free edge back into the machine, through the chamber's
   left wall. Aconity's chamber door is a flap: on Amazemet's MIDI the bar handle sits centred on the door's lower edge
   ([Amazemet](https://www.amazemet.com/aconity-midi-lpbf-system-in-amazemets-rd-facility)), and Aconity's product photo
   of the MIDI+ shows the chamber open with the flap raised, standing over the chamber on two struts, its handle at the
   top ([3Dnatives](https://www.3dnatives.com/3d-materials/en/3d-printers/aconity-midi-plus/)). It now hinges along
   its top edge at the chamber's front and swings out and up to 165 deg, leaning 15 deg forward of upright. The struts
   and the angle are our reading of that photo; that the MIDI's own flap opens the same way as the MIDI+'s is inferred
   from its handle. Chapter 3 (`alloy_print.py`) uses the same `Aconity.door`, so it opens the same way there.
2. **The lance stays clear of the machine.** The tube is 400 mm, not 300, so the gripper stays outside the chamber
   (its grasp point 12-100 mm in front of the door's plane) and only the tube passes the opening, at 1,171-1,213 mm,
   inside the 1,005-1,285 mm opening. The nozzle's centre keeps within 60 mm of the bore's axis, so its 22 mm flare stays
   inside the 170 mm cylinder (round 8's path reached 72 mm out, the flare 94 mm, over the cylinder's rim), 36 mm right
   of the lug's rows and 28 mm off the vertical bars. The hose is now collision-checked too: `DBox.hose_hits` tests the
   drawn hose against every mesh but the arm's, the lance's and its post's with collide.py's FCL as it moves (a
   `PREVIEW=1` pass: no contact). The shot is new (`CAM_LANCE`): from the front-right, low, through the open front, the
   chamber drawn opaque once its flap is up (the opening is the window), so the gripper is plainly outside and the
   tube plainly through the opening. What Sterling saw at 28:08 was round 8's view: from the left, the chamber
   see-through and the control cabinet's side opaque behind it, so the lance and its hose were drawn over the cabinet as
   if they ran through it, and the door had swung into the chamber's left wall. A check of the lance alone against the
   opened MIDI (36 poses over the sweep, FCL) found no contact.
3. **The depowdering box clamps the plate, twice over** ([`alloy_models.CLAMPS`](../alloy_models.py), `clamp_pose`).
   The plate's stud is pulled into the zero-point chuck (rounds 4-8 said so only in a caption), and three swing clamps on
   the rotor, 120 deg apart round the plate at 60, -60 and 140 deg (clear of the lug, the flat bars' ends and the
   vertical bars), rise 34 mm, turn their arms 90 deg over the rim and pull down on the plate's top face before the
   shaft turns; after, they rise, turn away and drop under the chuck's top, out of the plate's way as it comes and goes.
   Solukon's [SFM-AT200 page](https://www.solukon.de/en/products/sfm-at200/) gives the part envelope (300 x 300 x 230
   mm; 60 kg with the plate in one place on the page, 100 kg in another), a horizontal axis that swivels about 350 deg,
   a rotary table set by hand, a vibrator and inert gas, but not how the plate is clamped; its data sheet is sent on
   request. The swing clamps (a catalogue part, e.g. ROEMHELD's) are our design.
4. **Two build orientations on the chapter's plate** ([`alloy_models.ZBARS`](../alloy_models.py), `zbar_troughs`). The
   plate carries two bars printed vertical (Z) at its right, beside the four flat ones (XY), so the build is 100 mm tall.
   The lance sweeps round them, the box turns them (their tips stay inside the hopper's funnel at 180 deg), and the EDM
   cuts them in the same set-up: on edge they stand out of the plate's face, level, and the wire, which meets them
   first, cuts across their 10 x 6 mm feet (60 mm^2 each, against about 800 mm^2 along a flat bar). Each settles 0.5 mm
   into a U trough that hangs off a post on the comb's left arm, clear of the wire's plane; the upper trough stops 60 mm
   out, so the lower bar's free end is open once the upper bar is gone. The arm takes each by its free end, level,
   lifts it 2 mm, draws it straight out, turns it to hang from the gripper, rinses it and stands it in the rack's end
   slot (the rack has six slots now, 26 mm apart: [`r8_test.TRAY`](../r8_test.py)). The two tests stay on flat bars.
   Why the lab wants all three orientations, the 45 deg case, the EDM's limits and cut times are in the separate PR's
   `notes/edm_orientations.md` (branch `claude/issue-303-edm-orientations`).
5. **The tensile test as a cutaway, from the front-right** (Sterling's 32:20). Round 8's `CAM_GRIP` sat 760 mm in
   front of the frame at x 480, behind the MiR's arm, and looked at the specimen through the closed door's see-through
   window. Now the door shuts, and the chamber is drawn cut in half through the load string: its back half only
   ([`r8_test`](../r8_test.py) piece `chamber_cut`, with refractory-coloured cut faces), no front half, no door, nothing
   see-through, so the specimen, both wedge grips, the pull rods and the AVE 2 in front show while the crosshead closes,
   the chamber heats and the bar is pulled; the whole chamber comes back before the door opens. The camera is 1.6 m
   off, at the frame's right and low, past the right column's front face and the parked arm (`CAM_TEST`).
6. **What was odd about the heated box** (r8_test.instron_floor). Its shell's front wall was solid: the door was drawn
   on top of a 30 mm wall with no opening behind it, so with the door open the arm reached through the wall. The shell
   now has the door's 400 x 560 mm opening (Instron's inside size for the 3119-608). And its controller stood in the
   12.5 mm between the chamber and the right column, 24 mm into the column; it now sits on the chamber's roof, left of
   the upper pull rod. Its place on the frame (between the columns, 550 mm wide in the 575 mm gap), the door hinged on
   the left, the window and the pull rods through the ports were right and are unchanged.
7. **The six colliding poses.** Every park now goes to the first of a few variants of PARK (turned about the base by
   0, +-45, +-90 or 180 deg, or less folded) that touches nothing where the arm is (`clear_park`), so it no longer
   puts wrist 2 against the tongs or the chamber's open door. Moves that carry a bar to the rack, and the vertical bars'
   moves, go to the collision-free IK branch of their target nearest the arm's joints (`clear_q`, `go_clear`) instead of
   whichever branch the solver finds first, which is what folded the arm on itself at the rack in round 8.
8. **The IPA jar** is the lab-wide jar now (`props.jar_style`): clear glass, light grey-blue at 0.35 opacity, with a
   matte black cap (its knob too). The IPA inside stays blue.

### Collisions: what is known

Every joint move is planned round obstacles as it is rendered (`robot.py`, `collide.py`), and the planner reports any
move whose start or end pose is itself in collision. Round 8's render had six; this round's two renders (04:37-05:32 and
06:01-06:59 UTC; the second has the final shots) had **none**, and the `PREVIEW=1` pass before the fixes had five (three at the IPA jar and the rack, two at the
Instron), which is what `pick_clear`/`go_pick` and `clear_park` removed. The hose touched nothing in the `PREVIEW=1`
pass (`DBox.hose_hits`, every frame of section 2).

**The frame-by-frame audit (`ARM_AUDIT=1`) was not completed.** It started at 05:32 after the first render, in the same
runner_guard slot, and was stopped at 05:45, still in section 2, to free the slot for the six renders waiting on three
slots. So straight-line moves (the IK solved along a line, not planned) are checked only as far as the planner's start
and end poses: a link could still brush something in the middle of one. Run
`VLAB_ONLY_TRAYS=F ARM_AUDIT=1 xvfb-run -a python3 alloy_workflow.py` (about an hour) for the count.

### Left open

- The tour clips (`furnace`, `instron_floor`) were not re-rendered: the furnace's rack in them still shows four
  specimens (it has six slots now), and the 68FM-100's chamber still shows round 8's shell (no opening behind the
  door, the controller against the column). The models are fixed in `r8_test.py`; the clips need a slot.
- Chapter 3 (`alloy_print.py`, the print stream's) still prints the old plate: four flat bars and the lug. Passing
  `zbars=True` to its `Aconity(...)` prints the two vertical bars too, so the two chapters show the same build.
- The swing clamps' cylinders and the post that carries the vertical bars' troughs are our designs, as are the
  troughs; the lance's 400 mm is chosen to keep the gripper out of the chamber, not taken from a product.
- The MIDI's flap: that it lifts is read from Amazemet's photo of the MIDI (the handle centred on its lower edge) and
  Aconity's photo of the MIDI+ with its flap up; no photo of a MIDI with its door open was found.


## Round 8: chapter 5, depowder, cut, heat treat, tensile at room and elevated temperature

Sterling's review of 2026-11-05 (PR #318) asked for a catch shelf that catches, a capped IPA jar, real tensile
specimens in the heat treatment, Instron's automated loading, and an elevated-temperature test. The chapter is
re-staged as the alloy route's chapter 5 ([`alloy_workflow.py`](../alloy_workflow.py), `build_lab()` and `movie()`),
in the whole lab as the set-up movie leaves it (`setup_lab.build`: two Shuttles, every tray loaded, the floor plan), so
the VLM in its wide shots is the same one as in every other chapter. On that floor the Aconity MIDI stands in the north
row at x 6950, the wire EDM across the aisle in the south row, the 68FM-100 at the south row's west end, and the
furnace on tray F in Shuttle 1. Round 4-7's flow on the old one-Shuttle line is in git history; its `build()` stays,
because chapter 3 (`alloy_print.py`) borrows it.

| | |
|---|---|
| MP4, 1280 x 720, 6 fps, 356 s, 2,137 frames (rendered 20:12-20:58 UTC, only tray F populated, Shuttles clad) | [`out/mp4/alloy_workflow.mp4`](../out/mp4/alloy_workflow.mp4) (17.4 MB) |
| GIF, 400 px, 2 fps | [`out/alloy_workflow.gif`](../out/alloy_workflow.gif) (4.4 MB) |
| Stills: the cut over the comb, the broken bar | [`out/alloy_workflow_cut.png`](../out/alloy_workflow_cut.png), [`out/alloy_workflow_still.png`](../out/alloy_workflow_still.png) |
| Every sub-step's frames, and the numbers used | [`out/alloy_workflow.json`](../out/alloy_workflow.json) |
| Tour clips at 8 fps: the furnace with the upright rack, the 68FM-100 with its chamber, the quench tank's basket | [`furnace`](../out/mp4/instruments/furnace.mp4), [`instron_floor`](../out/mp4/instruments/instron_floor.mp4), [`quench_tank`](../out/mp4/instruments/quench_tank.mp4) |

### What changed, step by step

1. **The print, the lance, the depowdering box** (round 5's moves, on the new floor: the box and the lance's post
   stand east of the printer, as they stood beside it on the old line).
2. **The MiR250's storage is low pockets, not posts** (round 7: "no insertion gap ... positioned rather high"). The
   plate drops 12 mm into a 40 mm block bored for it and its stud; the specimen rack sits in a 20 mm frame with a 3 mm
   lead-in; the tongs lie on two V-blocks; a cradle with two channels takes the room-temperature halves
   ([`alloy_models.mir_pockets`](../alloy_models.py)). Round 4's placement "half a turn round" rolled the plate 120
   deg onto its side on its carrier; it is now a pure half turn about the vertical.
3. **Drives.** The MiR250 docks on the floor plan, turns on the spot and drives straight legs, each from rest to rest
   at its published 0.3 m/s^2 (PR #321's `props.ramp_*`, now on this branch); turning at 60 deg/s and 60 deg/s^2 is
   assumed (MiR publishes neither). The long drives to tray F and the Instron are shown at 4x, and the caption says so.
4. **A catch that catches** (Sterling: "it totally looks like they'd just bounce and fall straight off ... it should
   actually be capable of catching it in terms of distance and a taller lip"). The plate stands on edge, so each cut
   bar stands on end. Each gets its own slot in a comb under it whose floor is 0.5 mm under the bar's lower end: the
   bar settles 0.5 mm onto a urethane pad instead of falling 14 mm. The slot is walled in front (75 mm), on both sides
   (the comb's teeth) and, behind, by the plate's own face; the comb stops 1.4 mm in front of the plate, clear of the
   wire (0.15 mm off it). An ejector pin in each slot lifts its bar 65 mm, its foot still 10 mm in the slot, so the
   gripper takes the bar's upper end clear of the other three and of the plate's rim: round 6's 57 frames taking the
   bar off the shelf are gone by construction ([`alloy_models.catch_comb`](../alloy_models.py)). Our design.
5. **The IPA jar starts capped.** The arm lifts its lid off by the knob onto a rest beside it, dips each bar, and puts
   the lid back after the fourth. The jar is slim (32 mm across, IPA to 6 mm under the rim) so a bar held level by its
   upper end goes in up to the fingers; the air knife on the rim dries it on the way out. Round 5's 92 mm cup only
   let a gripper pointing down reach in. The bar's upper 25 mm, where the fingers hold it, is not dipped.
6. **Real specimens in the heat treatment** ("those aren't tensile specimens. They're just bars"). All four go
   through the jar into a stainless rack, standing on end in slots 25 mm deep ([`r8_test.TRAY`](../r8_test.py)): the
   arm carries every specimen level by its upper end, from the comb to the grips, so none is laid flat and picked up
   again. On tray F the rack gets a T6: solution treatment at 530 C, a water quench, ageing at 160 C. The schedule's
   times are assumptions until DAL sets one; the furnace tour clip's caption no longer credits EOS with it (that
   attribution had no source). The rack is always handled with **tongs** that ride on the MiR: 300 mm of steel between
   the gripper and the jaws, so the gripper stays out of the 530 C mouth (a gripper on the fin would also sit over the
   specimens). The door hinges on the furnace's right, where the quench tank is, and its free edge sweeps 472 mm in
   front, so the rack waits left of the mouth whenever the door moves and crosses to the tank in front of the closed
   door. The **quench tank has a lift basket** (r8_test.quench_tank): the rack is set on its plate just over the rim
   and dropped 150 mm into the water, about 7 s after the door opened (our figure; an aluminium alloy wants its quench
   within seconds, so check it). The door actuator, the tongs' linkage and the basket's cylinder are assumptions.
7. **The 68FM-100, loaded as in Instron's AT6 cells** (Sterling: "look at the automated tensile testing videos from
   that expensive automated module ... how they automatically load and unload the samples"). r8_test's model (round
   8, session 2) has a 3119-608 chamber round the load string on pull rods, an AVE 2 video extensometer reading
   through the door's heated window, and a scrap chute. The arm takes a specimen from the rack by its upper end, the
   chamber door opens (an actuator, assumed), the arm sets the specimen's foot in the lower wedge grip, lets go and
   backs out; the door shuts and the crosshead brings the upper grip down onto the upper end. This is the order the
   Volvo cobot cell in the Edison answer uses (lower grip first, then the upper grip approaches;
   [`out/edison/auto_tensile/answer.md`](../out/edison/auto_tensile/answer.md)).
8. **Elevated temperature** ("You're missing elevated temperature tensile tests"). The room-temperature test runs with
   the chamber cold; the second specimen is loaded cold, the door shuts, the chamber heats the grips and specimen to
   200 C and soaks 15 min, then the pull. The chamber cools before its door opens: the gripper isn't made for hot work.
   Both curves are **illustrative**: the room-temperature one through AddUp's as-built values (as round 4), the 200 C
   one assumed at about 60 % of its strength and twice its elongation. [Uzan et al.](https://cris.iucc.ac.il/en/publications/high-temperature-mechanical-properties-of-alsi10mg-specimens-fabr/)
   (Additive Manufacturing 24, 2018, 257-263) report the trend for SLM AlSi10Mg (yield falls and elongation rises above 200 C); their numbers were not
   retrieved here, so none are claimed. The room-temperature halves go to the MiR's cradle for fractography (chapter
   7's VHX), lying flat with their fracture surfaces touching nothing; the hot test's go down the scrap chute, as the
   AT6 drops them.

### Physical sense, checked in the previews and left open

- Fixed: the bars' 14 mm drop; the plate's roll on its carrier; the raised holders; the gripper reaching into a 530 C
  furnace (tongs); the furnace door swinging through the rack (it waits left of the mouth).
- Left: the jaws of the tongs are drawn fixed (the linkage that closes them is not modelled); the MiR works tray F
  350 mm further out than its dock, so its camera target (round 7's AprilTag cube) sees it from further away; the
  upper 25 mm of each bar is not rinsed; the furnace tour clip still slides its rack in from mid-air, as the tours do.

### Collisions: not audited frame by frame this round

The chapter was rewritten for round 8 and the runner's queue (two whole-floor scenes at a time) left no room for a
finished `ARM_AUDIT=1` pass before the long-form's cutoff: one ran 47 minutes and reached section 5 before a fix made
it stale. Every joint move is still planned round obstacles as it is rendered (`robot.py`, `collide.py`), so what is
known is what the planner reported in the last full preview: **six joint moves end in a pose that is itself in
collision**, which the planner cannot route round:

- section 5, twice: the arm folded on itself (shoulder against forearm, upper arm against the wrist) at a pose
  carrying a bar between the IPA jar and the rack;
- section 7, four times: the park pose the arm returns to between the Instron's steps. Folded over its base, it puts
  wrist 2 against the tongs' handle on their rest (233 mm off the arm's axis, the closest the UR10e reaches) and the
  gripper against the upper arm, and once wrist 2 against the chamber's open door.

The same six were reported while the render ran (20:12-20:58 UTC), so they are in the MP4: the arm holds each of
those poses for about a second.

Each is a few frames. The fixes are new poses: a waypoint for the bar moves, the tongs' rest further out on the cabinet
(or a different park pose while it is loaded), and a park pose that clears the door. Run
`VLAB_ONLY_TRAYS=F ARM_AUDIT=1 xvfb-run -a python3 alloy_workflow.py` (about an hour) for the frame-by-frame count.

## The alloy workflow: printer, wire EDM, tensile test (round 4)

![The alloy workflow](out/alloy_workflow.gif)

One build plate, from the Aconity MIDI to the wire EDM, then one tensile bar to the Instron. The UR10e rides its
MiR250 along the line's fronts; the rail isn't used. [`alloy_workflow.py`](alloy_workflow.py) is the scene, and
[`alloy_models.py`](alloy_models.py) has its new pieces: the Aconity opened up, the plate and bars, the EDM's fixture
and wire head, and the holders on the MiR.

| | |
|---|---|
| MP4, 1280 × 720, 10 fps, 161 s (round 6, the arm's moves collision-checked; re-render at 15 fps when the runner is free) | [`out/mp4/alloy_workflow.mp4`](out/mp4/alloy_workflow.mp4) (9.0 MB) |
| GIF, 640 × 360, 5 fps | [`out/alloy_workflow.gif`](out/alloy_workflow.gif) (5.1 MB) |
| Stills: the lance, the depowdering box | [`out/alloy_workflow_lance.png`](out/alloy_workflow_lance.png), [`out/alloy_workflow_depowder.png`](out/alloy_workflow_depowder.png) |
| Frame range of every sub-step, and the numbers used | [`out/alloy_workflow.json`](out/alloy_workflow.json) |
| Stills: the cut, the broken bar | [`out/alloy_workflow_cut.png`](out/alloy_workflow_cut.png), [`out/alloy_workflow_still.png`](out/alloy_workflow_still.png) |

![The cut, the EDM drawn see-through](out/alloy_workflow_cut.png)

![The broken bar and the curve](out/alloy_workflow_still.png)

### The steps

1. **The print is done.** Four ASTM E8 subsize bars lie flat on a 170 mm plate, still buried in powder. With them is
   a handling lug for the gripper. The process chamber is drawn see-through. An inset shows an SEM image of the
   lab's AlSi10Mg powder.
2. **Door, suction lance, platform (round 5: no person).** The chamber door opens and the MiR250 rolls up. The arm
   takes a suction lance off a post in front of the printer, right of the chamber, and vacuums the build cylinder
   at floor level, pointing 25° down, in four passes, while the platform rises out of the powder. The far pass goes
   first, and the nozzle rides just over the powder, then over the bars once they are out; the two middle passes stop
   short of the lug (round 6). The hose leaves the lance's handle from its side, past the gripper's fingers, and runs
   forward of the printer's front before it drops to the post. A pipe along the floor takes the powder to the
   depowdering box's separator. The lance goes back on its post. Loose grains are left round the bars and the lug.
3. **The arm takes the plate; the depowdering box.** The platform's clamp lets go. The arm comes in the way the
   plate will come out, level, its fingers over the lug, then down onto it, with the gripper pointing 30° down. It
   lifts the plate 32 mm, draws it out and tucks it in over the MiR's left half. Holding it, the MiR moves 1.6 m to
   the depowdering box between the printer and the 68FM-100. The box's door slides up, and the arm sets the plate's
   zero-point stud in a chuck on a horizontal shaft and backs off. The door shuts; under argon the shaft turns the
   plate over and back on a set path while a vibrator on it shakes the grains off, down a hopper into a closed
   bottle. The arm takes the clean plate out and sets it on the MiR's carrier, turned half a turn.
4. **Into the wire EDM.** The MiR drives about 3.7 m from the box to the FANUC. The tank is drained, so its door can drop. The arm
   takes the lug again, from above, and turns the plate on edge. It pushes the plate onto a zero-point receiver on
   an angle plate, bars to the front. The door goes up and the tank fills.
5. **The cut.** It is drawn see-through. The wire runs between its guides, 0.15 mm off the plate's face, and crosses
   the plate. The sparks show where it is inside a bar. Each bar drops 14 mm onto a catch shelf once it is cut
   through. The tank drains and the door drops. The arm takes the first bar by its end, dips its lower 70 mm in a
   cup of isopropanol on a stand left of the EDM (as deep as the fingers allow: their tips go into the cup, inside
   the air knife on its rim), pulls it out slowly through the air knife, and stands it in a holder on the MiR (round
   5: the rinse and dry).
6. **The tensile test.** The MiR drives to the 68FM-100, and the crosshead rises out of the way. The arm lowers the
   bar into the lower wedge grip, which closes, then lets go and backs off. The crosshead comes down until 40 mm of
   the bar is free between the jaws, and the upper grip closes. Then the pull: the stress-strain curve draws in step
   with the crosshead, to fracture at 14.8 kN. The crosshead backs off 20 mm to show the break.

Every arm move is a straight line of the grasp point solved with the UR10e's IK every frame, or a joint move between
two solved poses (`robot.py`), as in `animate.workflow()`. Since round 6 they are checked for collisions
(`collide.py`, FCL on the drawn meshes): the arm against itself, and the arm, gripper and what it holds against
everything visible. A joint move takes the nearest clear IK branch and is planned round anything in the way.

### Round 6: the arm's collisions

Sterling, on PR #318: "the robot arm didn't respect collisions with itself, at all." The audit (`ARM_AUDIT=1`, every
frame at 15 fps; [`out/collisions/alloy_workflow.json`](../out/collisions/alloy_workflow.json)) of round 5's version,
with the planner, found **539 of 2068 frames** in collision. Now: **60 of 2101**: 57 in the bar's pick at the EDM, below, and three single brushes, a fingertip and the plate's rim against the lance's hose for two frames as the arm tucks the plate in, and the wrist against the box's door for one as it shuts while the arm parks.

| Where | Frames | What it was | What was done |
| --- | --- | --- | --- |
| The lance, 2/6 | 268 | The hose left the barb on the handle's end, straight up through the gripper, which takes the handle end-on. With the hose in the way of every pose, the planner fell back to the nearest IK branch, which put the upper arm and forearm through the printer's cabinet and shell. The nozzle swept at floor + 5 mm: its 22 mm mouth was in the powder and the chamber's floor, then in the bars as the platform rose. | The barb is on the handle's side (`alloy_models.BARB`), so the hose leaves past the fingers (28 mm across) and is routed forward of the fronts before it drops. The nozzle rides 24 mm over the powder, then 26 mm over the bars; the far pass first, while it is lowest, so the gripper stays under the 280 mm chamber's roof; the middle passes stop short of the lug. |
| The plate out of the printer, 3/6 | 93 | Backed off 150 mm along its own axis, 30° down, the gripper's wrist was in the chamber's roof. | It comes in along the way the plate goes out: level, fingers over the lug, then 40 mm forward and 32 mm down onto it. |
| The drive to the box, 3/6 | 28 | Held 470 mm out of the chamber, the plate was still over the printer's cabinet, so it drove through the lance's post, its hose and the box's frame. | Tucked in over the MiR's left half first (the tuck still brushes the hose for 2 frames). |
| Into the box and out, 3/6 | 76 | The nearest IK branch reached the chuck with the upper arm and forearm through the box's frame and the printer beside it, and the plate caught the box's front on the way in and out. | The arm goes to a pose with the plate half in the door, in the branch that is clear at the chuck (`branch_q`), and the lines in and out stay in it. The door shuts as the arm parks, not as it leaves: shutting as it left, it caught the gripper (it still touches the wrist for 1 frame). |
| The rinse, 5/6 | 17 | The fingers hit the air knife on the cup's rim, and the bar "hit" the isopropanol. | The knife sits on the rim with its slot facing in, so the fingertips pass inside it; the liquid stands 17 mm under the rim. Liquids are not obstacles to the checker (`sc.fluids`, `collide.py`). |
| The bar off the EDM's catch shelf, 5/6 | 57 | The fingers between the bars and in the plate's edge; the wrist in the EDM's upper housing. | Not fixed: see below. |

**Left: taking the bar off the catch shelf (57 frames, 5/6).** Neither problem is one a pose can fix:

- **The fingers can't get between the bars.** The four bars stand on the shelf 25 mm apart, so their grip ends leave
  15 mm gaps, and a 2F-85 fingertip is about 31 mm across. The bar's back is against the plate's face, so the fingers
  can't close front to back either. Gripped by its top end, the inner finger is in the next bar and the fingertips
  are in the plate's edge.
- **There is no room to point down at the shelf.** The EDM's upper housing (`instruments.wire_edm()`) comes down to
  1230 mm from 200 mm behind the machine's front; the shelf is 390 mm in, and the bars' tops are 264 mm under the
  housing. Pointing down, the gripper and the UR's wrist need about 320 mm over the grasp point, so the wrist is in
  the housing (`inst_white`, `inst_dark`), as the audit says.

A fix, not made for lack of time: an ejector pin under the first bar's place on the shelf lifts it about 100 mm once
the tank has drained, clear of the others and of the plate's edge. The arm takes it level, as it handles the plate in
the EDM, rinses it and stands it in the holder on the MiR still level, then takes it again from above at the
holder, so that the Instron's grips are loaded as now. Printing the bars further apart would change chapter 3.

### Sources

- **Specimen:** DAL PR #169 (the Aconity MIDI set-up for the Utah build) gives a bar 100 mm long with 10 mm ends,
  a 32 mm reduced section 6 mm wide, and 6 mm thick, printed flat. That is ASTM E8/E8M's subsize sheet specimen:
  L 100, A 32, W 6, C 10, B 30, R 6, G 25 mm. The E8 table was not checked against the standard itself.
- **Plate:** 170 mm across, the MIDI's build platform (DAL PR #169). Utah's page gives "Maximum possible build
  space: Ø 170 mm x H 200 mm". Al 6061, as Utah's plate (DAL PR #169).
- **Aconity MIDI:** #199's model, `lab_models.equipment.aconity_midi()`, with its process chamber split into walls,
  a door and an inside. The chamber is that model's, 609 × 700 × 310 mm outside; with the 15 mm walls drawn here it
  is 280 mm tall inside. The build cylinder sits under the model's beam tube.
- **FANUC ROBOCUT α-C400iC:** data sheet MDS-04386 (FANUC Europe, 2022):
  - maximum workpiece 730 × 630 × 250 mm (730 × 585 × 250 with the automatic door), and 500 kg;
  - X/Y travel 400 × 300 mm, Z 255 mm;
  - wire 0.10-0.30 mm across.

  The brochure lists a "work tank automatic door" option, "that dispenses with the need to completely drain the
  water". So without it, the tank is drained before the door opens, which is what the animation does.
- **Cutting rate:** FANUC gives none for aluminium. GF's CUT AM 500, a wire EDM made for cutting parts off build
  plates, has a "maximum cutting speed of 300 mm2/m" with 0.2 mm wire (MoldMaking Technology, 14 Feb 2020). That
  figure is not specific to aluminium.
- **Instron:** the 68FM-100 and 68SC-2 are `instruments.py`'s models. Instron's 100 kN extended hydraulic wedge grips
  (CP104947) list "Fully-automatic hydraulic actuation" and "Front loading of flat specimens".
- **Stress-strain:** AddUp's AlSi10Mg data sheet, version US-10252023-0129: FormUp 350, 50 µm layers, ASTM E8,
  machined, at least 27 samples. As built, XY:
  - E 72 ± 3 GPa;
  - YS 275 ± 8 MPa;
  - UTS 412 ± 38 MPa;
  - elongation 5 ± 2 %.

  Kempen et al. 2012, Physics Procedia 39:439 (DOI 10.1016/j.phpro.2012.10.059), as built, XY:
  - E 68 ± 3 GPa;
  - UTS 391 ± 6 MPa;
  - elongation 5.55 ± 0.4 %.

  They report that "all samples were seen to break at UTS". EOS's process data sheet for the M 290 at 30 µm gives
  Rp0.2 270, Rm 461 MPa and A 10.2 % (XY), from machined round bars.
- **SEM:** DAL `figures/sem/AlSi10Mg_carbon_adhesive_SEM.png`:
  - taken on BYU's Apreo, at 500x, 5 kV, 0.10 nA, with the ETD (secondary electrons);
  - 829 µm field width, 2 April 2026;
  - posted by Gage Erickson on byu-vcl#48 (comment 4181040112, "AlSi10Mg on carbon adhesive").

  DAL's Genesis proposal captions the slurry image from the same session "stock AlSi10Mg powder (BYU)". The inset
  shows the carbon-adhesive one, because its particles are spread out and easier to see. A copy, 800 px wide, is in
  [`out/alloy_sem_AlSi10Mg_carbon_adhesive.png`](out/alloy_sem_AlSi10Mg_carbon_adhesive.png).
- **MiR250:** 800 × 580 × 300 mm (`props.py`). MiR's spec sheet (a copy at Hartfiel) gives a top speed of
  2.0 m/s and an acceleration of 0.3 m/s² at full payload.

The pages:
- [Utah's AconityMIDI page](https://aerospace.research.utah.edu/?p=67)
- [FANUC α-C400iC data sheet](https://www.fanucamerica.com/uploads/files/data-sheets/ROBOCUT-C400iC-Wire-EDM.pdf)
  and [ROBOCUT brochure](https://www.fanucamerica.com/uploads/files/data-sheets/robocut-product-brochure.pdf)
- [GF CUT AM 500, MoldMaking Technology](https://moldmakingtechnology.com/products/edm-speeds-up-additive-part-separation-preserves-part-integrity)
- [AMF clamping for additive manufacturing](https://www.amf.de/en_us/clamping-systems/additive-manufacturing)
- [Instron 100 kN extended hydraulic wedge grips](https://www.instron.com/wp-content/uploads/2024/07/100-kn-extended-hydraulic-wedge-grips.pdf)
- [AddUp AlSi10Mg data sheet](https://addupsolutions.com/wp-content/uploads/2023/10/AlSi10Mg-Material-Data-Sheet.pdf)
- [Kempen et al. 2012, open access](https://lirias.kuleuven.be/retrieve/2f46a660-a2f3-4ca3-a4eb-934fa2a0cfcb)
- [EOS AlSi10Mg, M 290, 30 µm](https://www.eos.info/metal-solutions/data-sheets/aluminium/pds-eos-aluminium-alsi10mg-eos-m-290-30um)
- [MiR250 spec sheet, Hartfiel's copy](https://www.hartfiel.com/wp-content/uploads/2024/04/MiR250-Specs.pdf)
- [The SEM images on byu-vcl#48](https://github.com/vertical-cloud-lab/byu-vcl/issues/48#issuecomment-4181040112)

### Findings

- **The gripper can't point down inside the MIDI's chamber.** The chamber is about 280 mm tall inside, taking
  15 mm walls. With the plate 18 mm proud of the floor, the grasp point on the lug is 46 mm up. Pointing down, the
  2F-85's grasp point is 155 mm below the flange (`ur_arm.TCP_MM`). The UR10e's wrist 2 axis is another 117 mm up
  (d6). That puts the axis 318 mm over the floor, 38 mm through the roof, before counting its housing. Pointing 30°
  down, the wrist 2 axis is at most 66 mm under the roof, once the plate is lifted. So the plate needs something the
  arm can take from the side: here, a lug printed with the bars.
- **The MiR has to park further out at the printer than at the VLM: 230 mm off the fronts, not 30.** To clear the
  chamber's front, the plate has to come out 435 mm. From 30 mm off, that brings the flange within 264 mm of the arm's
  base axis, and the IK has no solution there; from 230 mm off it stays 460 mm away. The MiR parks 230 mm out at
  every machine, so it drives straight along the line.
- **The bar needs the 68FM-100, not the 68SC-2.** Its 6 × 6 mm section at AddUp's 412 MPa is a 14.8 kN pull; at
  EOS's 461 MPa it is 16.6 kN. The 68SC-2's 2 kN is reached at 56 MPa on this section, below yield. On the 68SC-2, a
  bar would need a section under 4.9 mm², say 3 × 1.5 mm.
- **The cut is about 3390 mm².** That is four bars at 847 mm² each, the bar's outline. At GF's 300 mm²/min it would
  take at least 11 minutes; FANUC publishes no rate.
- **The wire EDM must take the plate on edge.** Its wire is vertical. To cut bars off at their base, the plate's face
  has to be vertical too, with the wire moving parallel to it. A 170 mm plate on edge is well within the FANUC's
  250 mm workpiece height.
- **The test is short at a fast rate.** Kempen et al. tested at 0.4 mm/mm/min. At that rate, 5.6 % strain takes
  8.4 s, about the 8 s shown.

### Caveats

- **Assumed, not documented:**
  - **The zero-point clamps:** in the MIDI's platform, on the MiR's carrier and on the EDM's angle plate. Utah's plate
    is screwed down, and the arm can't unscrew it. AMF sells zero-point pull-stud clamping for post-processing AM
    parts on CNC machines. GF's AMCarrier is reported as the workholding for the CUT AM 500, but its page wasn't
    readable.
  - **The handling lug:** 12 × 30 × 40 mm, at the plate's rim. It makes the build 40 mm tall instead of 6.
  - **The plate's 15 mm thickness.** Plate and parts come to about 1 kg; the UR10e's payload is 12.5 kg.
  - **The door:** it is hinged on the right, so it swings away from the MiR. The model's two clamps are on the left.
- **Drawn, not sourced:**
  - Aconity publishes no drawing of the chamber's inside. The supply cylinder behind the build cylinder, the
    recoater parked at the back, the piston and the powder are layout choices; only the 170 mm sizes are from DAL.
  - The wire head is drawn here. `instruments.wire_edm()`'s own head can't span a plate on edge, so it is hidden.
- **Depowdering (round 5): our design, on a commercial principle.** No source found documents automatic
  depowdering on the MIDI, and Utah's page lists the AconitySIEVE as a separate unit. So:
  - **In the chamber, the arm does what a person does** with an ATEX vacuum: a suction lance (Ø28 × 300 mm tube,
    a 12 mm handle gripped like the lug, assumed) on a post at x = 3420, in reach from the MiR's spot at the
    printer. A floor pipe along the fronts runs to the box. The lance points 25° down because the chamber is
    280 mm tall; at 30°, with a 430 mm tube, the UR10e's wrist would have had to come inside its own base's reach
    limit, so the tube was shortened.
  - **Then a depowdering box**, 420 × 620 × 1540 mm, in the 544 mm the line leaves between the Aconity (to
    x = 4486) and the 68FM-100 (from x = 5030). It works like Solukon's SFM-AT200: the plate clamped on a table
    that turns about one axis on a programmed path, shaken at a variable frequency, in nitrogen or argon. Solukon
    gives parts up to 300 × 300 × 230 mm and 60 kg ([TCT Magazine](https://www.tctmagazine.com/solukon-compact-post-processing-metal-3d-printing/));
    a later version adds ultrasonic excitation ([Metal AM](https://www.metal-am.com/?p=82324)). Solukon publishes
    no outer size, and [3devaluate](https://3devaluate.com/_files/ugd/cf3431_a1fb83966d694d8ea6f16706d573508d.pdf)
    lists its installation space as 2 × 2 × 2 m, so the commercial unit would need the line opened up by about a
    metre. Hence the narrow box: the chuck, shaft, vibrator, hopper and bottle are this model's.
  - For four flat bars the lance does most of the work; the box is what parts with channels or overhangs need.
- **Wet bars (round 5): a dip-and-blow cup.** Isopropanol in a Ø92 cup on a stand in the 410 mm between the
  68SC-2 and the EDM, with an annular air knife on the rim (assumed). No source was found on how fast wet AlSi10Mg
  stains, nor on rinsing wire-cut Al before a tensile test.
- **The depowdering takes 7 s on screen.** No cycle time is published for a plate this size; Solukon's programs
  run for minutes.
- **The curve is not a measurement.** It is a smooth curve through AddUp's four values: elastic at 72 GPa, then
  Voce hardening, s = 244 + 169 (1 - e^(-100 εp)) MPa. That puts 275 MPa at 0.2 % offset and 412 MPa at 5 %, where
  it breaks. The plot says so.
- **The SEM is the lab's stock powder.** It isn't necessarily the lot Utah printed. The inset says "the powder a
  plate like this is printed from", not "this plate's powder".
- **Too small to see:**
  - the 0.25 mm wire, which is drawn 1.6 mm thick;
  - the sparks, which are drawn on the bar's front face, while the real gap is in a 0.3 mm kerf;
  - the bar's 1.4 mm stretch over its 25 mm gauge. The crosshead moves 1.6 times that.
  - The grips' jaws aren't drawn closing: the status line says when they close.
- **The catch shelf** sits under 1 mm from the wire's path. A real cell might use a basket, or leave tabs and break
  them off.
- **The drives are about twice as fast as real.** The animation allows the MiR 1.5 m/s and no ramp: 5.5 m takes
  4.4 s. At MiR's 0.3 m/s² it never gets past 1.3 m/s on that distance, and takes about 8.5 s.
- **The chamber is still open to the air** when the arm reaches in. Whether the MIDI's chamber can be opened before
  the plate is cool, and under what gas, isn't covered here.

### Changes to the shared files I'd suggest (not made)

- `instruments.wire_edm()`: its tour cuts a flat plate with a vertical wire moving across it. That doesn't separate
  parts at their base. Standing the plate on edge, as here, would.
- `instruments.instron_small()`: its specimen is 4 × 1.5 mm = 6 mm². At about 400 MPa that is 2.4 kN, over the
  frame's 2 kN.

### Running it

```bash
xvfb-run -a python3 alloy_workflow.py            # -> out/mp4/alloy_workflow.mp4, out/alloy_workflow.gif, .json, stills
PREVIEW=1 xvfb-run -a python3 alloy_workflow.py  # the last frame of each sub-step -> /tmp/preview_alloy_workflow.png
ARM_AUDIT=1 xvfb-run -a python3 alloy_workflow.py  # every frame checked, nothing drawn -> out/collisions/alloy_workflow.json
```

The opened Aconity is tessellated once, in about 10 s, and cached in `.cache/alloy_aconity_<hash>.pkl`. The full
render took 38 minutes on the shared 4-core runner (round 6, at 10 fps: 43 minutes, with five sessions sharing it).

Round 8 (the whole lab; through `runner_guard.py` on a shared runner):

```bash
VLAB_ONLY_TRAYS=F VIZ3D_FPS=6 xvfb-run -a python3 alloy_workflow.py        # as rendered: only tray F is populated,
#                                         the Shuttles are clad (L.skin(0)), so the empty trays never show
VLAB_ONLY_TRAYS=F CH5_FROM=6 PREVIEW=1 xvfb-run -a python3 alloy_workflow.py   # stills from the heat treatment on
VLAB_ONLY_TRAYS=F ARM_AUDIT=1 xvfb-run -a python3 alloy_workflow.py        # the frame-by-frame collision count
VIZ3D_FPS=8 xvfb-run -a python3 tour.py furnace instron_floor quench_tank   # the three tour clips (r8_test.py)
```
