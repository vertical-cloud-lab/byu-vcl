# Swapping the atomizing plate (clip `atom_plate`, PR #353 for #303)

Files: `atom_plate.py` (the clip), `atom_plate_tools.py` (tools, fixtures, local overrides, the BOM list),
`out/atom/plate_bom.json`. Scene: `atom_base.py` (the rePowder of #327 with this PR's latch, two MiR250 + UR10e +
2F-85 + D405 units).

Sources, cited below by short name:

- **253**: DAL PR 253, `atomizer-sop.md` (Gage's checklist): "Configuring the Ultrasonic Tower" steps 8-18,
  "Powder Collection and Cleaning" step 6, "Copper Alloys" step 2, "Run Log" item 3.
- **178**: DAL PR 178, `atomizer-training/sop.md`: "Ultrasonic stack" steps 1-11 with video times (T5, T7), the
  plate table (T9 38:35), "Cleaning and maintenance" (plates), "Lessons from Oct 2 / Oct 6".
- **#164**: DAL issue 164 (plate height; the gauge plate; Sharpie lines; Bartosz's laser down the nozzle, T5 63:28).
- **#261**: byu-vcl issue 261 measurements (plate 4.71 x 0.82 in = 119.6 x 20.8 mm; upper sonotrode 0.785 x 2.23 in =
  19.9 x 56.6 mm), as built into `repowder/model.py`.
- **UR**: Universal Robots UR10e datasheet (F/T sensor at the flange: ±100 N, ±10 N m; accuracy 5.5 N, 0.5 N m) and
  UR's "max joint torques" article (wrist joints, size 2: 54 N m; elbow, size 3: 150 N m; base and shoulder, size 4:
  330 N m; "you cannot use the full value in your application").
- **Robotiq**: 2F-85 grip force 20-235 N, 85 mm stroke (already in `ur_arm.py`).

## The procedure, step by step

Who: **arm 2** = MiR 2's UR10e + 2F-85 + D405 (parked at model (-600, -720), its arm 590 mm in front of the door's
hinge line); **arm 1** = MiR 1, parked at the right, not used; **machine** = the rePowder's ultrasonic generator and
HMI; **person** = nobody in the clip (see "What a person still does").

| # | Step | Source | Who | Clip |
| --- | --- | --- | --- | --- |
| 0 | Chamber vented and cold before anything opens | 253 Safety 5; 178 After a run | machine (state) | caption, 1/12 |
| 1 | Two door bolts: knob loosened one turn (two half-turn grasps), bolt swung out of its lug | model joints `clamp0/1`; T5 27:16 | arm 2 | 2/12 |
| 2 | Door open 100 deg on its back hinge; the stack rides out on it | model `door`; 178 step 8 | arm 2 | 3/12 |
| 3 | Plate's condition: crack, dark edge spot, metal that will not lift off | 253 Cleaning 6; 178 plates (T7 50:21) | arm 2 (D405) | 4/12 |
| 4 | Upper sonotrode broken loose (counter-held) | 253 step 13 in reverse; 178 step 5 | arm 2 + stack wrench | 5/12 |
| 5 | Upper sonotrode unscrewed by hand, 7.6 turns of M8, to its tray | 178 step 2 (M8 at the plate end) | arm 2 | 6/12 |
| 6 | Old plate slid straight off the stud, into its labelled slot; logged | 178 step 9; 178 plates (OCT2a 02:24, T7 18:16) | arm 2 | 7/12 |
| 7 | New plate (W-coated CF for a Cu run) slid on; flat, gap-free contact checked | 253 steps 10-11, Copper 2 | arm 2 (D405) | 8/12 |
| 8 | Upper sonotrode on by hand | 253 step 12 | arm 2 | 9/12 |
| 9 | 50 N m, counter-held, following the arrow | 253 step 13; 178 steps 5, 9 | arm 2 + stack wrench | 10/12 |
| 10 | Plate square to the hatch | 253 step 14 | arm 2 (D405) | 11/12 |
| 11 | Height with the Mo gauge plate: between the Sharpie lines; logged | 253 step 15; #164 | arm 2 | 11/12 |
| 12 | Rescan: one peak 39.5-40.5 kHz, power higher with the plate on | 253 step 16; 178 step 10 | machine (HMI) | 11/12 |
| 13 | Wet test: a few drops of IPA, the whole plate atomizes, straight pattern | 253 step 16; 178 step 10 (T5 27:32) | arm 2 + machine | 11/12 |
| 14 | Seals wiped with IPA | 253 step 18; Cleaning 9 | arm 2 | 12/12 |
| 15 | Door shut | 253 step 18 | arm 2 | 12/12 |
| 16 | Landing check: the laser down the empty nozzle lands high and centred, clear of the upper sonotrode | 253 step 17; #164 (T5 63:28) | laser module + arm 2's view | 12/12 |
| 17 | Both bolts back, knobs tightened | as step 1 | arm 2 | 12/12 |

**Two changes of order, and why.** (a) 253 step 17 says to check the landing "with the door open", then step 18
wipes the seals and closes the hatch. In the model, as on the machine, the stack is mounted on the door, so the plate
is under the nozzle only with the door shut. The clip wipes and shuts first, then checks with the laser before the
bolts go back. Ask Gage what "with the door open" meant on the day (it came from Oct 6, when the stream hit the upper
sonotrode). (b) The laser needs the furnace open and the crucible empty, so the plate is set before the charge goes
in, which swaps the SOP's order (furnace first, stack last); #164 says this too.

## The tool: why one tool that reacts its own torque

50 N m (253 step 13; 178 step 5: 55 allowed, 50 safer) against what the arm can take:

| | Figure | Against 50 N m |
| --- | --- | --- |
| UR10e F/T sensor at the flange | ±10 N m range, 0.5 N m accuracy (UR) | 5x past the range: a protective stop, and no torque reading |
| UR10e wrist joints (size 2) | 54 N m rated, not all usable (UR) | 93 % of the rating if the reaction went through wrist 3 |
| 2F-85 friction on the Ø19.9 sonotrode | 2 x 0.3 x 235 N x 9.95 mm = 1.4 N m (μ = 0.3 assumed) | 36x short |
| A 250 mm wrench held by the arm instead | 200 N at the handle | 2x the F/T force range (±100 N); past a 141 N friction hold on the bar |

So option (b), two arms each with a crowfoot, does not work with these arms and grippers: each arm would have to take
the full 50 N m (or 200 N at a handle) through its wrist, beyond what it can measure or hold, and two grippers would
have to share the 16 mm of axis between the lower flats and the plate, through a door opening.

**Option (a), chosen (ours, to make): the stack wrench.** A C-frame that sits beside the plate's long edge
(`PT.wrench_meshes`):

- a fixed 17 mm open-end head at its lower end slides radially onto the Ti (lower) sonotrode's flats, 2 mm under the
  plate, and counter-holds them;
- at its upper end, on the stack's axis past the upper sonotrode's free end, a drive spindle slides 15 mm down the
  axis so its slotted 17 mm socket takes the upper sonotrode's end flats; a gearmotor turns it through a slip clutch
  set to 50 N m (the drive is to choose: a small DC nutrunner spindle with torque control would do the same);
- the torque goes from the socket through the upper sonotrode, the connector and the lower sonotrode back into the
  fixed head and the frame: the stack, the door and the arm see none of it. The arm carries the tool (2.8 kg, ours:
  steel head and socket, aluminium frame, gearmotor), 22 % of the UR10e's 12.5 kg payload, and only places it.
- Why the socket slides axially: a radial open-end head that turns the upper sonotrode ends at whatever angle the
  torque leaves it, and cannot slide off radially unless that angle happens to line up with the fixed head. An axial
  socket comes off at any angle. The drive turns its slot to the flats' angle (read by the D405) before it slides on.
- Loosening: the same tool in reverse; the clip shows a 58 N m peak (ours: break-loose is often a little above the
  tightening torque), then the thread runs free.
- The clutch is set and checked against the lab's own torque wrench (178 step 5).

**Other fixtures (ours, all on a 150 mm shelf over MiR 2's cabinet top, `PT.TOP` = 930 mm; on the bare cabinet top
the arm had to fold down to its own mounting plane and every IK branch put its upper arm into the cabinet):** a
per-alloy plate rack with five labelled
slots, plates standing on their hole end 52 mm apart so the 2F-85's fingers fit between them; a two-socket tray for the
upper sonotrode; the wrench's holder; the gauge plate's holder; the IPA dropper's holder; a wipe pad (lint-free wipe
over foam on a stem) and its holder. Part numbers: `out/atom/plate_bom.json`.

## Forces, turns and times

- Knob: one turn (M12 coarse assumed, 1.75 mm back off the lug) in two grasps of half a turn; the bolt then lifts out
  of the lug's slot, which is open on top (ours). The pads grip the knob's lobes 13 mm out from its middle: the
  2F-85's fingertips reach 18 mm past the grasp point and are 31 mm deep across the closing direction, so closer in
  they would sweep into the door's front edge as the wrist turns.
- The door is pulled open by the lower lug, the pads on its top and bottom faces (22 mm apart), 21 mm in front of
  the door's edge.
- Upper sonotrode by hand: the connector's outer half is 12 mm, less the 2.5 mm plate, so 9.5 mm of M8 coarse (1.25 mm
  pitch) = 7.6 turns. The 2F-85 grips it below the Sharpie lines (friction, ~1.4 N m available, ours) and turns it
  half a turn a grasp with the wrist (16 grasps each way), from 90 deg one side of centre to 90 deg the other, so
  the wrist camera never swings round into the arm's own forearm. The wrist turns about the flange's own axis, so
  `spin()` puts the turn on joint 6 alone and the thread's advance (1.25 mm a turn) on the rest of the arm.
- Before each grasp-then-move (a knob, a bolt's swing, the door, the upper sonotrode), `branch_for()` tries every IK
  branch of the grasp and follows the move from it, and the arm goes to the first branch that keeps clear (after
  chapter 2's `arc_branch`).
- Final torque: from snug to 50 N m over 20 deg (ours; the real angle depends on the joint's stiffness).
- Plate off and on: straight along the axis, 14 mm, over the 12 mm stud, so it is never forced through the 8 mm ring
  (178 step 9: one snapped at its hole's edge).
- Wet test: three drops fall 74 mm from the dropper's nozzle in 0.12 s each (free fall, drawn at that speed); the mist
  leaves the face at 20-70 mm/s (ours).
- Clip timing: every sub-step runs at `SPEED` = 0.74 of the first cut. The arm's transfers stay under 1 m/s at the TCP.
  The real robot would also need the D405 checks to run (a few seconds each), and the vibration for the wet test.

## What was checked

- Every frame with `ARM_AUDIT=1` (collide.py): the arm, its gripper and what it holds against everything, and the
  movers (the door with the stack, the bolts) against everything else. Passes: 860 of 1973 frames in collision at the
  first cut, 101 of 2146 after the branch look-ahead and the bores, **54 of 2146** (15 fps) before the final pass, with
  the movers check at 0. What was left: one fingertip grazing the upper sonotrode by 3 mm while the dropper is over
  the plate (43 frames; the dropper was then raised 25 mm), the top knob touching its lug at the 1.5 mm limit (9
  frames; the knob was then drawn 1.5 mm off), a fingertip 3 mm into the chamber's face for 2 frames. The final
  render audits itself at the same time (`PLATE_COMBINED=1`, 10 fps): **2 of 1407 frames** (a fingertip 3 mm into the chamber's face while the lower knob is tightened, 12/12), movers 0, in `out/collisions/atom_plate.json`.
- The model's own door clamps were checked with FCL before redrawing them (below).
- The wrench's clearances, by construction: the fixed head's jaws 0.3 mm off the flats, its top 2.5 mm under the
  plate (whose back face is on the sonotrode's tip face); the socket's jaws 0.3 mm off the end flats and 0.5 mm clear
  of the round part below them; the C-frame's spine 52 mm outside the plate's edge.

## Local overrides (this clip only; the shared model is untouched)

- **Door bolts.** As modelled (`repowder/model.py` `CLAMP_*`), the star knob's lobes reach 10 mm behind the chamber's
  front face (y -110 against the face at -120), so any swing along the face would pass through the chamber; and the top
  bolt's pin sits inside the viewport hood: FCL puts the top bolt 8.7 mm into the hood when shut and 37 mm at 180 deg.
  This clip hides the model's bolts and brackets (`clamp0/1`, `clamp_body0/1`) and draws its own: the rod 30 mm in
  front of the face (not 8), on a standoff bracket, through new lugs on the door's front edge (a fork open on top). The
  lower bolt swings 180 deg over the top, along the face (T5 27:16 shows the lower one swung out to the right); the top
  one swings 60 deg up, because the hood is in the way of more and the lug's path (as the door opens) rules out less,
  and its pin is 22 mm further left (x -112), clear of the hood. **To fix in the model.**
- **Air hose.** The model draws the compressed-air line to the transducer's cover as a fixed line, so the cover swung
  through it when the door opened (the audit's movers check: 25-50 mm). The hose is flexible; here its last two points
  ride on the door.
- **Upper sonotrode.** Drawn with two 17 mm flats at its free end (the SOP torques it with a 17 mm wrench; the model
  draws it round; where the real flats are is not recorded) and two Sharpie lines 36 and 42 mm from its plate face
  (#164's "optimal about 3.9 cm", with no datum given).

## Assumed (ours) and open questions for the lab

1. Where are the upper sonotrode's wrench flats? The tool's socket needs them at the free end; a radial head would
   work elsewhere only with the turn-angle problem above.
2. The door bolts' real standoff, knob size and thread; which way the top bolt swings with the hood beside it.
3. Plate IDs: engraved, or a tag? (178: "Label them: on Oct 2 nobody could tell the plates apart.") The clip's IDs
   (`CF-AL-03`, `WCF-CU-07`) and use counts are examples.
4. Does the plate keep its clocking while the upper sonotrode is torqued, or is the whole stack turned in its housing
   afterwards (step 14; 178 step 11: "loosen to turn")? The clip only checks it with the camera.
5. Which port does the gauge plate rest on (#164: "a port hole looking onto the back of the upper sonotrode")? The clip
   lays the gauge level against the upper sonotrode at the lines and reads it with the camera.
6. The angle from snug to 50 N m, and the break-loose torque (drawn 20 deg and 58 N m).
7. "With the door open" in step 17 (see the change of order above).
8. The D405's view of a crack: is it enough, or should the decision stay with a person (step 3)?

## What a person still does (not automated here)

- Puts the laser module in the sealing rod's place and takes it out before heating (#164) unless another clip's arm
  does it with the furnace open.
- Decides on a borderline plate (a dark edge spot, peeling edges: 178 plates) from the camera's pictures.
- Sets and checks the wrench's clutch against the torque wrench.
- Keeps the run log (253 Run Log item 3: plate material, size, ID, use count, booster, gauge setting).

## Not done

- The KF clamp on the door's stack housing is not touched (the stack is not turned or slid).
- Only the top and the front side of the door's seal face are wiped on screen; the chamber's own seal face is not
  shown.
- MiR 1 does nothing in this clip.
