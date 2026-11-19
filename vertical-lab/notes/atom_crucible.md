## Changing the crucible with two arms (atom_crucible_out, atom_crucible_in)

PR #353 (#303). Sterling on PR #318: automate "changing out a crucible (lots of substeps here) ... screwing on the
graphite nut". Two clips, one script (`atom_crucible.py out|in`), tools and fixtures in `atom_crucible_tools.py`,
bill of materials in `out/atom/crucible_bom.json` (`CRUCIBLE_BOM=1 python3 atom_crucible.py`).

Starts from the lab's own plan, `notes/crucible_automation.md`, and the SOPs: DAL's detailed SOP (`178_sop.md`,
"Furnace and charge" 1-6 and 9, with video times) and DAL's checklist (`253_atomizer-sop.md`, "Loading the Furnace"
1-5, "Cooldown", "Powder Collection and Cleaning" 8). Nothing here has been tried on the machine.

### Start and end states (both clips)

- **Furnace cold.** The graphite is safe in air below about 400 C (checklist, Cooldown 1), but the nut and the
  slag wait until the furnace can be touched (Cooldown 3: "Don't touch the graphite nut under the furnace"; Powder 8:
  "Once the furnace can be touched: slag out, nozzle checked or drilled, furnace rebuilt"). The clips start below
  50 C (ours: a number for "can be touched").
- **Lid open, latch undone.** Another clip (`atom_latch.py`) works the latch; these start with it open
  (`set_joints(lid=1, latch=1, loop=1, bolt=1)`) and say so on screen. Since commit e3b1428 the lid is hinged on the
  left (DAL measured a left hinge) and stands up there when open (x -375 to -152, z 1352-1637), with the latch on the
  housing's right face. Three things below follow from that: the sealing-rod lever swings up 70 deg, not chapter 2's
  95 (at 95 the 2F-85 holding it meets the open latch lever); the nut key's handle is 500 mm out, so arm 2's wrist
  stays left of the lid; and every approach over the furnace picks an IK branch that is clear at the grasp, not only
  at the pre-grasp pose (arm 1's wrist sat in the lid while it held the crucible).
- **Door open, both clamps off** (`door=1, clamp0=1, clamp1=1`).
- **The ultrasonic stack is out, on its bench,** not drawn: "If the furnace is being rebuilt, do it before the stack
  goes in: the graphite nut under the crucible is reached through the chamber door" (checklist, Loading the
  Furnace). The plate-swap clip takes the stack out; these start after it.
- The out clip ends with the crucible in its cradle on MiR250 1. `atom_bn.py` cleans it and recoats it with BN at the
  hood. The in clip starts with it back in the cradle, clean, coated and dry, the nozzle holder standing in the
  holder fixture and the nozzle in its tray.

### Who does what

- **Arm 1**, UR10e + 2F-85 on MiR250 1 parked in front (`PARK["front"]`): everything from the top.
- **Arm 2**, UR10e + 2F-85 on MiR250 2 parked at the left by the door, 200 mm further out than `PARK["left"]`
  (x -960, y -40, yaw 90): the nut, from below, with the nut key through the open door. As the SOP says, two people make this easier (178 SOP, step 3).
- **The machine:** the SEALING ROD key, sent as a PLC input (ours; AMAZEMET would have to allow one). The other way is
  arm 1 pressing the HMI's touch key with a capacitive stylus; we did not draw it.
- **A person:** drilling a closed nozzle by hand (0.5 or 0.7 mm; SOP 2), and anything the checks below stop on.

### Out: taking the furnace apart (atom_crucible_out)

| # | Step | Who, tool | Source | Sensed |
|---|---|---|---|---|
| 1 | Thermocouple drawn straight up 100 mm by its leg, into a stand on MiR250 1 | arm 1, tweezers on the 3.8 mm sheath | SOP 1 (T1 35:49) | pull force, est. < 1 N |
| 2 | Safety pin out by its T-handle (48 mm pull) onto a rest | arm 1, pads on the handle's ends | SOP 1 (T1 36:24) | |
| 3 | Lever swung up 70 deg on its post (chapter 2: 95; the open latch lever is in the way), arm backs off straight up | arm 1, chapter 2's grasp and arc | SOP 1, T4 1:18-2:17 | |
| 4 | Sealing rod out by its brass adapter, lifted 175 mm, stood in a holder | arm 1, pads on the 21.7 mm adapter | SOP 1, 6 (T4 1:41, 1:52) | |
| 5 | Top ring out, then the side tube | arm 1, needle tool | SOP 1 (T1 37:01) | lift force |
| 6 | Key in through the door; six pins into the nut's notches, the cup under the nut and seal | arm 2, nut key | SOP 1 ("holding the graphite nut so nothing falls") | Fz up, 3 N (assumed) |
| 7 | Crucible gripper on; breakaway: crucible turned 30 deg anticlockwise, nut held; torque logged | arm 1, crucible gripper, FT 300-S | SOP 1; crucible_automation step 4 | Mz peak (logged) |
| 8 | The key spins the nut off: 6.9 more turns at 2.0 mm, the cup following it down 14 mm | arm 2's key motor; arm 1 holds the crucible | model: `NUT_Z`, `SHANK_Z0`, `NUT_PITCH` | turns (encoder) |
| 9 | Key out through the door with the nut and the lower seal in the cup, back on MiR250 2 | arm 2 | | |
| 10 | Crucible lifted 260 mm straight up (shank end clear of the deck), into its cradle | arm 1 | SOP 1 | |
| 11 | Nozzle check: cradle backlight under the nozzle, wrist camera down the bore | arm 1's D405 | SOP 2 (OCT2a 10:08); checklist 1 | light / no light |
| 12 | Bottom ring out | arm 1, needle tool | SOP 1 | |

### In: the rebuild (atom_crucible_in)

| # | Step | Who, tool | Source | Sensed |
|---|---|---|---|---|
| 1 | Bottom ring into the coil, onto the furnace floor | arm 1, needle tool | SOP 3 (T1 46:33) | |
| 2 | Nozzle: light through the bore over its tray's backlight, then into the holder's recess, white side up | arm 1, tweezers | SOP 2-3 (T1 45:54); checklist 1, 3 | camera |
| 3 | Fixture jaws close on the holder's shank; crucible taken from the cradle and set on the holder | arm 1, crucible gripper | SOP 3 (T8 1:28) | Fz -2 N |
| 4 | Thread finding: the fixture turns the holder back 45 deg until it drops 0.3 mm, then forward 1.25 turns to the torque limit; arm 1 holds the crucible and reads Mz | fixture drive, arm 1's FT 300-S | SOP 3 (T8 2:26, T1 46:08, T9 33:45) | Mz to 0.40 N m (assumed) |
| 5 | Crucible lowered straight into the coil, the shank through the bottom ring, floor and top plate; spiral search (0.7 mm) on the last 30 mm | arm 1 | SOP 3 (T1 46:33); crucible_automation step 8 | Fz limit 8 N (assumed) |
| 6 | Key in through the door with the nut and the lower seal; the seal slides onto the shank | arm 2, nut key | SOP 3 (T1 47:02) | Fz up 3 N |
| 7 | Thread finding: nut turned back 120 deg until it rises 0.5 mm onto the thread's start, then 6.5 turns up (13 mm) | key motor; arm 1 holds the crucible | crucible_automation, "compliant thread finding" | turns, Mz drag |
| 8 | Crucible turned 90 deg clockwise, the key holding the nut: its thermocouple hole to the port at the back right; the joint draws up 0.5 mm | arm 1 | SOP 3 (T1 47:02) | hole angle (known from the cradle) |
| 9 | Snug: the key turns the nut the last 54 deg to the limit | key motor; arm 1's FT 300-S | SOP 3 | Mz to 0.30 N m (assumed) |
| 10 | Key drops 16 mm off the nut and goes out; crucible gripper off | arm 2, arm 1 | | |
| 11 | Side tube down over the crucible (0.6 mm inside, 1 mm to the coil), then the top ring | arm 1, needle tool | SOP 5 (T4 0:31), checklist 4 | |
| 12 | Thermocouple down through the top ring's hole into the crucible's wall hole | arm 1, tweezers | SOP 1, 5; T1 38:06 | push force, stop at 2 N (assumed) |
| 13 | Rod stood on the nozzle (lowered until the force rises), lever down, pin in, SEALING ROD down | arm 1; PLC input | SOP 6 (T4 2:02-2:18), checklist 5 | Fz -1.5 N |

Turns, from the model: the nut is 12 mm thick (`NUT_Z` 1110-1122), the shank ends at 1108 (`SHANK_Z0`) and the pitch is
2.0 mm (`NUT_PITCH`), so from the thread's start (the nut's top at the shank's end) to snug the nut travels 14 mm:
7 turns. In: 6.5 turns by the key, 0.25 turn as the crucible is turned to the port, 0.15 turn to snug (13.8 mm; the
seal is drawn 0.2 mm short of the roof). Out: 30 deg by arm 1 (breakaway), 6.9 turns by the key. The pitch,
the thread's length and the holder-to-crucible thread are not in the SOP or the manual: model values, to measure.

### Tools and fixtures

All ours unless a maker is named; meshes in `atom_crucible_tools.py`, the BOM in `out/atom/crucible_bom.json`. Each
tool has a 28 mm handle the 2F-85 holds (pads 28 mm apart), as chapter 2's loading tong, and its own stand on MiR250 1.

- **Wrist force/torque sensor on both arms: Robotiq FT 300-S.** The UR10e's own sensor is ±10 N m with ±0.5 N m
  accuracy and ±0.2 N m precision, and ±5.5 N force accuracy (UR10e datasheet, as quoted in
  `notes/crucible_automation.md`): that is the size of the whole snug torque, so it cannot tell snug from cracked.
  The FT 300-S reads ±30 N m with 0.003 N m moment noise and a 0.01 N m contact threshold (Robotiq's sheet, same
  note). ATI's Axia80 is the alternative: 20 N m (or 8 N m in its second calibration), 0.005 N m Tz resolution,
  accuracy under 2 % of full scale ([ATI flyer](https://www.ati-ia.com/Library/documents/Axia80_Flyer.pdf)); 2 % of
  8 N m is 0.16 N m, half the snug value, so for a limit set on the bench the resolution matters more than the
  accuracy. The clips draw the arms without the sensor; it would add about 37 mm between the flange and the gripper.
- **Crucible gripper.** A plate over the rim and three jaws (4 mm aluminium, 2 mm silicone) on the top 38 mm of the
  crucible's outside, 1.5 mm of stroke, driven by the 2F-85's squeeze through a wedge. It stays inside r 46, 14 mm off
  the coil (r 60). It grips the outside, so the side tube has to be out first (out) or in last (in), and the fresh
  BN inside is not touched. With friction 0.3 (assumed, as the lab's note) on r 37.7 and three pads at the 2F-85's
  20-235 N, the grip holds 0.7-8 N m before slipping, above the 0.3-0.55 N m used here.
- **Needle tool (insulation).** Four Schmalz SNG-M 4 0.8 needle heads (10.01.29.00001: four 0.8 mm needles, 3 mm
  stroke, 30 deg, 4-6 bar; [datasheet](https://media.schmalz.com/MAM_Library/Dokumente/Datenblatt_Artikel/1/100/10012900001/eea1348ed8b8_Datasheet_Article_10.01.29.00001_en-EN.pdf))
  on a hub at r 54.5, so they land on all three pieces' top faces (top ring r 50-98, side tube r 38-59, bottom
  ring r 16-59). Why needles and not paddles: the side tube has 0.6 mm to the crucible and 1 mm to the coil, so
  nothing can get beside it; its top face is all there is. Suction does not hold porous fibre. Whether needles hold
  the vacuum-formed alumina-silica pieces without crumbling them is not known: try it on a spare piece first.
  Schmalz does not publish a holding force for these. The hub stays inside r 58 (2 mm off the coil).
- **Tweezers.** Two 1.5 mm jaws with PEEK tips, 20 mm apart at rest; a lever in the handle closes the tips 4 mm for
  each mm the 2F-85's pads close on the handle's halves (ours). For the 16 mm nozzle and the thermocouple's 3.8 mm
  sheath. The thermocouple's leg is only 10 mm over the top ring, so the 2F-85's own pads (38 mm tall) would go
  12 mm into the ring; the first version tried and the audit caught it. The tips cannot enter the nozzle's recess
  (0.2 mm clearance), so they let go 2.6 mm over its floor and the nozzle slides the rest of the way down the recess.
- **Nut key.** A 500 mm bar through the door, under the door opening's top edge (z 1103; the bar's top at 1100 when
  the nut is snug), its handle 500 mm out from the nut so arm 2's wrist stays clear of the open lid, a gear head under the nut, and a turning socket: six pins for the nut's six notches (r 30) and a
  cup whose rim stands 3 mm over the nut, so the nut and the lower seal cannot fall. A small gearmotor with an
  encoder in the bar turns the socket through a 1:1 bevel pair (to choose). The torque limit is read by arm 1's
  FT 300-S through the crucible (arm 1 holds it still), so the limit is set in one place, on the bench.
- **Holder fixture.** A block with a bore for the holder's shank, two soft jaws, and a small rotary drive under it
  (ours) that turns the holder onto the crucible while arm 1 holds the crucible still. The first version had arm 1
  turn the crucible 1.25 turns with its wrist; the IK flipped the arm on the way, and a fixture that turns is also
  how the nut is done, with the torque read in the same place.
- **On MiR250 1:** the crucible cradle (a soft seat for the base, a well for the holder and shank, a white LED under
  the nozzle), stands for the three tools, the rod holder, the thermocouple stand, the pin rest, the holder fixture,
  the nozzle tray with its own backlight. Each is on its own bearing from the arm's base, about 350 mm out, so the
  upper arm reaching one passes over no other (the first layout put the thermocouple stand between the arm and the
  cradle, and the planner found every reach to the cradle in collision).
- **Parts table beside the machine** (ours): seats for the top ring, the side tube and the bottom ring, 855 mm high,
  in front of the chamber's right end. They did not fit on the MiR with the rest.
- **Safety pin.** The model implies it; we drew one (3.2 mm shaft, T-handle) through the lever's eye. It is drawn
  without the eye's and the stub's cross holes, so the audit treats it as a soft part.

### Forces and torques

None of these torques is measured; the snug torque is a feel "Gage and Sterling got hands-on from Bartosz"
(178 SOP, step 3). Start values (ours, assumed): nut 0.30 N m, crucible onto holder 0.40 N m, an example breakaway
reading of 0.55 N m (to be logged every time, not predicted). Force limits: 2-3 N for a thread start, 8 N for the
crucible going into the coil, 2 N on the thermocouple's sheath (which "cracks normally", T1 35:49).

Bench test to set them (before anything goes near the machine):
1. With a peak-hold torque gauge and an adapter for each part, measure what hands do: snug and breakaway for the
   nut on the shank and for the crucible on the holder. Several people, ten repeats each.
2. Break a spare nut and a spare holder slowly in a fixture; record the torque. Run the robot at no more than half
   of the breaking torque, and below the hand value if that is lower.
3. On a plate with the furnace floor's and the top plate's holes (ours, BOM), run the thread finding 50 times with
   the FT 300-S: count misses and crossed starts. Start at 0.20 N m and raise in 0.05 N m steps until the furnace's
   leak check passes (it pumps to -1 bar without "Pressure crucible", T5 34:39). Then try the UR10e's own sensor
   alone, to see whether the add-on is needed at all.

### Where we left the SOP, and why

- **The bottom ring comes out after the crucible.** The SOP lists top, side, bottom insulation, then the crucible
  (T1 36:24-37:01). In the model the bottom ring (r 16-59) lies under the crucible's base (r 37.7), so it cannot be
  lifted while the crucible is in. Is the real one split, or was the SOP naming the pieces rather than ordering them?
- **The thermocouple goes in after the top ring.** The SOP does side insulation, thermocouple, top ring (SOP 5,
  checklist 4). In the model the thermocouple runs straight down through a hole in the top ring into a hole in the
  crucible's wall, and its leg lies over the ring; the SOP's thermocouple comes through the side insulation's hole
  and is bent close to the crucible. Ours follows the model and says so on screen.
- **SEALING ROD is not pressed for the strip.** The SOP presses it first (it lifts the lever and the rod), then pulls
  the pin. With the rod lifted, pulling the pin would let it drop 12 mm onto the nozzle, and graphite breaks when
  dropped (T4 1:41); a person holds the rod with the other hand, and one arm cannot do both. So the pin comes out with
  the rod seated. The rebuild ends with SEALING ROD down, shown as the piston pressing 1.5 mm (chapter 2's value).
- **The SOP's second graphite seal is not drawn.** The SOP names a second seal in the stack (T1 37:45) and a seal
  that goes in before the bottom ring (T1 46:33). The model has one, under the chamber's roof above the nut, and
  that one rides in the key's cup both ways. Where the other sits is not clear from the SOP or the model.
- **Paddles became needles** for the insulation (above).
- **Arm 2 does not turn the nut with its wrist.** The nut needs 7 turns; a UR10e's wrist 3 has a limited range, and
  the key's own motor keeps the arm still (a straight rise of 2 mm a turn).

### Checked

- **Clips** (1280 x 720): `atom_crucible_out` 1176 frames at 10 fps, 117.6 s (second render, 02:28-02:43, rendered and
  audited in one pass); `atom_crucible_in` 2201 frames at 15 fps, 146.7 s.
  MP4s in `out/mp4/`, stills `out/atom_crucible_*_still.png` (the nut spun off; the nut snug), sub-step JSONs in
  `out/`. The GIFs are resampled from the MP4s to 512 px at 3 fps (out) and 2.5 fps (in) to stay under 4.9 MB; the
  scene's own were 9.6 and 9.0 MB.
- **`ARM_AUDIT=1`, the code as rendered** (FCL on every frame; arm, gripper and held part against everything, held
  parts at most 1.5 mm into their own fixtures; movers checked): out **0 of 1027** checked frames in collision and 0
  mover contacts (second render, with the two fixes below); in **16 of 1992**, 0 mover contacts, as rendered
  (`out/collisions/atom_crucible_{out,in}.json`). The out clip's first render (15 fps) had 13 of 1520. Its causes,
  and what is left in the in clip:
  - The 2F-85's fingers graze the sealing-rod lever, 3-12 mm, at 70 deg its eye is 63 mm from the axis (out: 10
    frames, at the rod's grasp and two tool approaches; in: 3 frames, as the crucible gripper lifts off). In the in
    clip the tools now sit turned 90 deg on what they hold and the rod is taken across the lever's line (`TURN`,
    `ROD_SPIN`), which cleared it there; the out clip's second render uses the same two settings, which cleared its
    10 frames. The in clip keeps its 3.
  - The tweezers' jaws read 12 mm into MiR250 1's group for 1-2 frames as they leave or enter their stand (out 3,
    in 6), and in the in clip the nozzle holder reads 12 mm into it for 7 frames as it leaves its fixture. Found
    after the first renders: `props.mir250()`'s cabinet spans z 300-800, and this chapter put MiR250 1's fixtures on
    780 (`CAB_TOP`), so everything stood 20 mm into the cabinet top; the jaws (bottom at 788) and the holder's shank
    (end at 793) are the parts that reach it. `CAB_TOP` is now 800, which cleared the out clip's 3 frames. The in
    clip was rendered and audited with 780 (`CRUCIBLE_CAB_TOP=780` repeats it), so its 13 such frames remain in it.
- The lid moved to the left during this work (e3b1428); everything above was re-audited after it. Before that move
  the out clip was at 8 frames; the move brought it to 218 (the wrist in the lid, the fingers on the open latch
  lever) and the fixes below took it to 13.
- Clearances by construction: crucible gripper r 46 against the coil's r 60; needle hub r 58 and heads r 59 against
  r 60; the key's bar top 3 mm under the door opening's top edge, its cup rim 1 mm under the chamber's roof; nut bore
  r 12.3 and seal bore r 12.5 on the r 12 shank; holder head r 15 in the bottom ring's r 16 bore.
- **A fault in the shared model, worked round in this chapter only.** `model.py`'s furnace extension
  (`hood_parts`, part `furnace_ext`) keeps a solid 5 mm floor plate (x 0-184, z 1150-1155) right across the
  holder's shank, where the furnace floor (r 25) and the top plate (r 20) have their holes: the crucible as built
  sits 12 mm into it, and the first audit flagged every frame the crucible moved. `atom_crucible.py` cuts a 60 mm
  square out of that plate's mesh in its own scene (`Rig.__init__`); `model.py` is unchanged and should get the hole.
- Wrist 3: the turns of the crucible are pure wrist-3 rotations (the gripper's handle is on the crucible's axis),
  driven in joint space and checked against forward kinematics; the joint move before each turn picks the IK branch
  with wrist 3 inside +-170 to +-220 deg, so the turn stays inside the UR10e's +-360 deg.

### Open questions for the lab

1. Thread pitch, length of thread and turns of engagement for the nut and for the crucible-to-holder joint.
2. Is the bottom ring split, and does it really come out before the crucible?
3. Where the second graphite seal sits.
4. What SEALING ROD up does during the strip, and whether AMAZEMET would allow a PLC input for it.
5. The hand torques (bench test above), and a breaking torque from a spare nut and holder.
6. Whether needle grippers hold the insulation without crumbling it.
7. A price for a spare graphite set (crucible, holder, nozzles, nuts, seals).
