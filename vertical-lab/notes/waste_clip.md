# The waste, animated: the bottle trip, the cabinets and the powder point (`waste_clip.py`, `powder_point.py`)

PR #371's check on #318 (2026-11-26): the chemical waste station was in the 3-D lab but no clip showed it, "nothing
about waste handling is animated: the bottle trip by MiR; the powder waste at the atomizer cell (per-family pails,
the *Solid Material* bucket, sand cans); the vacuum liners", and #369's two 118EXPs were on no floor. Sterling asked
for that check to be addressed in full. Everything shown comes from `notes/waste.md` ("Each stream", "The waste
station: where waste waits, and how the arms and MiRs move it").

```bash
python3 powder_point.py                                                     # the powder point's gaps to its neighbours
python3 runner_guard.py slot --mem 6500 --label fit -- xvfb-run -a python3 setup_lab.py fit
python3 runner_guard.py slot --mem 6500 --label waste -- env ARM_AUDIT=1 xvfb-run -a python3 waste_clip.py
python3 runner_guard.py slot --mem 6500 --quick --label waste -- env PREVIEW=1 xvfb-run -a python3 waste_clip.py
python3 runner_guard.py slot --mem 6500 --label waste -- env VIZ3D_HD=1 VIZ3D_HD_DIR=r16 VIZ3D_AUDIT=1 \
    xvfb-run -a python3 waste_clip.py                       # out/r16/waste_clip.mp4 (text), out/clean/ (none, + .json)
python3 render_r16.py queue waste                           # the same, as round 16 queues it (JOBS["waste"])
```

Without `VIZ3D_HD` it writes `out/mp4/waste_clip.mp4`, `out/waste_clip.gif` (3 fps, 512 x 288), `out/waste_clip.json`
and `out/waste_clip_still.png` (the parked arm after the swap). `VLAB_ONLY_TRAYS=""` is its default: the Shuttles
stay clad, so the trays are neither seen nor loaded, and the whole lab fits in about 6 GB.

## What it shows

1. **The bottle trip** (about 50 s). units[1] leaves charger 1 backwards, drives the aisle's south lane to the hood's
   pivot spot (x 2500), turns and drives in along the hood's dock line. On its cabinet is our PE spill tray with a
   capped 1 L bottle of sieve-wash IPA, a red band and a label in words ("IPA + Al fines / no water, no acid"). The
   sash is at its 18 in stop. The arm takes the bottle by its cap, lifts it out of the tray, goes to a stage pose
   outside the sash, moves straight in under it 70 mm above the intake tray, sets the bottle down in the empty nest and
   lets go, backs straight out, takes the front empty 1 L bottle from the rack beside the tray the same way, puts it in
   the spill tray and parks. A log line appears in the corner (bottle, station, volume), and the unit drives off.
   Captions: one class a trip and the incompatible pairs; the arm never opens, pours or combines waste; a person
   consolidates in the hood on the day shift; the delivery is logged for the pickup request to BYU Risk Management.
2. **The cabinets** (about 10 s). Close on the hood's base from the aisle, the hood fades to `waste_station.hood()`'s
   see-through drawing of the same hood with `cabinet_contents()` inside, each cabinet named in a label: the solvent
   cabinet (the sieve-wash IPA with its fines in a grounded can, the rinse IPA, the Form Wash IPA with resin, the used
   BN cans) and the acid cabinet (*Acid Aqueous* and Weck's a shelf apart, each in its own tray). Then back to the
   lab's hood.
3. **The powder point** (about 22 s). A slow camera move round it with labels: the Al-family and Cu-family 118EXPs
   (PR #377's blue and orange bands, with the words), their station post and holsters, one grounded pail per family
   ("Al family" / "Cu family", "sealed liners", "lid on, not crimped"), Risk Management's *Solid Material* bucket, the
   filter can with dry sand, the safety PR's B570 and Super D pail, the sign. Captions: Al and Cu never share a bin;
   a person seals each liner and lifts it into its family's pail, the arms don't; powder waste never rides a MiR; the
   pickup is requested from Risk Management when a pail is full.
4. **Where waste waits** (about 9 s): a high shot from the aisle's south-east with both places labelled.

**The vacuum liners, by a person** (added later in round 16, sub-steps "3/4 The vacuum liners", after the powder
point's first step; the clip is now 117.3 s, 1,759 frames). A person (`people.Person`) comes in from the aisle round
the glovebox's west end and along the corridor behind the machines, the only way in, since the fire point (680R, B570,
Super D pail) closes the point's south side. They unplug the Al-family 118EXP after its run-on and settle (vacuum SOP
4), open its clamps and lift the head off (it is set aside and not drawn: putting it on the floor needs a squat the
Person model can't make), seal the liner where it is (its mouth drawn up and twisted into a gooseneck), lift it out by
the neck over the vacuum's handle, carry it round to the Al-family pail, take the lid off, put the liner in and set
the lid back on, not crimped. Then a fresh liner, the head back on, plugged in, and out the way they came. The arms
never touch a liner (PR 80; notes/atomizer_automation.md). The day-shift beat at the hood (bottles into the cabinets)
is still a caption.

**The pails moved for it.** In the front row a person could reach the pails only through the fire point, through gaps
of 208 and 368 mm, so `powder_point.PAIL` puts them on the corridor side beside their vacuums, Al at (-6060, 330) and
Cu at (-4730, 330), with a second ground bar between the vacuums' handles, bonded to the first. The point's rectangle
is now x -6220 to -4505, y -1222 to 490. The set-up movie and the floor-clean clip were rendered again on this layout,
and `setup_lab.py fit` checked it. In the clip only, the Al pail's bail is laid down along its rim so the liner and lid
can pass; the lab model keeps it upright.

**The person's check** (`out/collisions/waste_clip_person.json`, as floor_clean_people's): no part of the body inside
any box of the scene in any frame (0 of 371), the closest 60.1 mm, to the Al pail. The hands and forearms within 250 mm
of a palm, and the vacuum's push handle the person leans over, don't count.

## Where the powder point stands, and why there

`powder_point.py` puts it **behind the rePowder's fire point**, world x -5868 to -4505, y -1222 to -60 (`RECT`):
between the 680R (x <= -5919) and the rePowder's back (x >= -4475), north of the B570's post (y >= -1273). Its
nearest neighbours as drawn: the B570's post 51 mm from its rectangle (the station's base, 43 mm from the post), the
680R 51 mm, the Super D pail 103 mm, the rePowder 30 mm (the sign), the rePowder dock's lane 688 mm, its pivot circle
484 mm, the glovebox's target post 632 mm, atom_vacuum's MIR_PARK 1.3 m (`python3 powder_point.py`).

- **Not where atom_vacuum.py stands it.** Its own floor puts the vacuum and the post in front of the rePowder's west
  end (model frame VAC_AT (-1060, -250), STN_AT (-520, -200); world = model + alloy_atomize.RP (-3775, -1700)). On
  setup_lab's floor that is the rePowder dock's approach lane (y -2520 to -1940, x -5762 to -3087), and its pail,
  extinguisher and sign at y -2460 to -3260 are in the aisle. MiR250 2 taking the wand from the holster stays
  atom_vacuum's own floor.
- **Not where floor_cleaning.VAC_STATION put it** (x -5900 to -4710, y -1980 to -340): the safety PR (#379) has since
  put its B570 at (-5150, -1400) and its Super D pail at (-5650, -1475) in that rectangle's front half. VAC_STATION is
  kept, with a comment, as the rectangle floor_cleaning's reach maps were drawn with.
- **In `setup_lab.build`**: `Floor._stations` adds it as group `powder_point`, world meshes under the rePowder's root
  ("repowder", gmat = the root's inverse) and in `F.groups["repowder"]`, so the set-up movie hides it with the empty
  bay and sets it down with the rePowder. `machine_rects` measures it on its own (`powder_point` in
  `out/tray_plan.json`), so `fit` checks every dock's lane and pivot against it; `footprints` gives it no tape (its
  rectangle's tape would run under the fire point's units). `VLAB_POWDER_POINT=0` leaves it out.
- **`fit` (07:33 UTC)**: no new hits. The rePowder and sieving-cell docks still list `repowder` and the aisle still
  has `repowder`, as before (the rePowder's floor plates, known). The rePowder dock's pivot moved from x -5362 to
  -5487 because the rePowder's own rectangle grew 110 mm west, from atom_crucible's MiR250 2 spot moved off the pump on
  2026-11-23 (its plate came back), after the last committed `fit`; the powder point is 484 mm from the new circle.

What it is, part by part (atom_nilfisk's models where they exist; the rest ours at typical sizes): the two 118EXPs
(inlets south, handles north), each with its hose drawn from its inlet along the floor and up into its wand's cuff,
its crevice tool on, its wand in a holster fork of the station post (the station's own fork for the Cu wand, the same
fork turned round for the Al wand), a family band on its bin and its cuff and a name plate on its head, a power cord
to a twin outlet box on the post's top fed down a conduit from the north cable tray (wall power); the post with its
tool rack, continuity fixture, relay box and meter (atom_nilfisk.station_meshes, turned 90 deg); the Uline S-7344
pails with their lids set on, a 25 mm family band and a label; a 5 gal HDPE *Solid Material* bucket with a liner over
its rim and a lid; a 200 x 280 mm steel can with its lid ("USED FILTERS / in dry sand"); the A-frame sign; a copper
ground bar with green-yellow bonds from both pails, the can, both vacuums' lugs and the post's lug.

## The arm's moves and the audit

Every move goes through `robot.py`: joint moves are planned (RRT-Connect when the straight joint line hits anything),
line moves are solved every frame. Before the trip, `plan_stop()` searches where the unit stops on the hood's dock
line (x 1500 to 1950, and up to 300 mm further out) and, there, every pose the arm passes through: the deck grasp and
its back-off, the nest, the pose 70 mm over it and the stage 330 mm out from it, the empty and its stage and lift,
the spill tray again with the pose over it and the back-off, each over IK branches and approach yaws, against the
scene as it stands (`collide.Checker`, the gripper open). A held bottle stays upright only if the tool keeps the
pitch it was grasped at, so each bottle has one pitch for its grasp and its place (the first audit tilted the IPA
bottle 20 deg and set it 25 mm into the intake tray). It found the stop at (1500, -5718), 150 mm out from the dock
line, with both bottles taken level (pitch 0).

**`ARM_AUDIT=1` (round 11's strict rules, the movers check on), on the final code: 0 of 1,043 checked frames with an
arm, gripper or held bottle in collision, and 0 frames with a mover's new contact** (the MiR250, its spill tray and
bottle, every frame it drives; 285 frames with something moving). The person-less first version was 1,412 frames, 94.1 s at 15 fps; with the person, the final audit is 0 of 1,399 checked frames for the arms and 0 for the movers, 590 frames with something moving, and the clip 1,759 frames, 117.3 s (the
audit checks the frames that move; holds repeat the frame before). The first audit of this file had 214 frames in collision: the arm's upper arm in the hood's posts,
the dock's target post and its own MiR250 with the unit on the dock line itself, the forearm in its own Class D unit
reaching back to the deck, and the pitch fault above.

## What is ours, and what is assumed

- The spill tray (180 x 180 x 50 mm, one nest), the 1 L narrow-mouth HDPE bottles (90 x 190 mm, a 40.5 mm cap) and
  the grasp by the cap (the 2F-85 opens to 85 mm, so it can't take the bottle's body).
- The empties are 1 L bottles now in `waste_station.work_surface()` too (they were 250 mL there), on a rack 116 mm
  wide that stays 34 mm clear of the hood's right post, so the lab's model and the clip agree.
- The volume in the log line (0.8 L) and the station are illustrative.
- The unit stops 150 mm out from the hood's dock line: from the line itself no clear pose was found for the nest
  (the upper arm met the hood's posts). The docking is ours to set; the dock's tape stays where `fit` checks it.

## Proposed narration (for `narration.json`)

- *1/4 The bottle trip*: "Liquid waste leaves a station in the capped bottle it was made in, one class a trip. At the
  fume hood the arm sets it in the intake tray, under the sash, and takes an empty back. It never opens or pours."
- *2/4 The cabinets*: "A person moves the bottles into the hood's vented cabinets each day shift: solvents on the
  left, acids on the right, a shelf apart."
- *3/4 The powder point*: "Powder waste stays by the atomizer: a vacuum and a pail for each alloy family, a bucket for
  sweepings, used filters in dry sand. A person seals and carries the liners; powder never rides a robot."
- *4/4 Where waste waits*: "Two places, across the aisle from each other, and each waste stays in the room where it
  was made."
