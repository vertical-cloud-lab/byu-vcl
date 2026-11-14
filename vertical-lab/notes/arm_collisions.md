# The arm's collisions: what was wrong, the check, the planner

Sterling, on PR #318 (2026-11-04): "the robot arm didn't respect collisions with itself, at all. Passed through the
MiR250 and collided with the vial holder."

## What was wrong

`robot.py` moves the UR10e in two ways:

- **`line_to`**: a straight line of the grasp point, with IK solved every frame;
- **`joint_to`**: a straight line in joint space between two solved poses.

Nothing checked either kind of move against anything. Two things went wrong:

1. **A joint move goes where its joints take it.** From a pose over the tray to one over the MiR's own cabinet, the
   elbow and wrists swing through whatever lies between: the cabinet, the holder on its post, the VLM's front panel,
   and the arm's own links.
2. **The IK took the nearest solution every time.** The UR's closed-form IK has up to eight solutions for a pose:
   shoulder left or right, elbow up or down, wrist flipped or not. `ur_arm.ik` returns the one nearest the current
   joints. For the level reach into the multi-doser, the nearest one has the elbow down, through the MiR's cabinet
   and the VLM's front panel under the opening. The line moves that follow are seeded from it, so they stay in that
   branch all the way in and out. Over the holder, the nearest solution puts the upper arm through the holder.

## The check (`collide.py`)

- **FCL** (the Flexible Collision Library, the checker MoveIt uses by default), through `python-fcl`, on the meshes
  as drawn: triangle-mesh BVHs (OBB-RSS), so a holder on a post or an open machine counts as drawn, not as its
  convex hull. The arm's links are decimated to 8000 triangles for the check, and the drawn meshes are untouched.
- **Self-collision.** Every pair of arm links that aren't adjacent in the chain, plus the gripper (all its parts)
  as one body on the flange. Pairs that touch in over 90 % of 400 random poses (the joints' own housings) are left
  out, as MoveIt's setup assistant does it for UR's SRDF.
- **Everything else that is visible:**
  - the MiR the arm rides on, its cabinet, holders and carriers;
  - trays, machines, the VLM and the other arm.

  A cutaway machine counts whole, since only the camera's view is cut.
- **What may touch:**
  - the arm's base and the cabinet it's bolted to;
  - the gripper and the part it is picking up or putting down, or that part's fixture, within 4 s of the grasp or
    release;
  - a held part, and the fixtures it touches when it is taken and when it is let go.

## The planner (`robot.Robot.joint_to`)

1. **Every IK branch, nearest first.** The first one whose pose is clear is taken.
2. **The straight joint line, if it is clear.** Most moves are unchanged.
3. **Otherwise RRT-Connect** (Kuffner and LaValle, 2000) in joint space:
   - every edge checked at 1.5° steps;
   - then shortcut, and each remaining via pose dropped if it can be.

   The move takes the same time as before and ends in the same place.

`ARM_NO_PLAN=1` gives the old straight joint lines. `ARM_AUDIT=1` runs a clip without rendering and checks every
frame, line moves too: `out/collisions/<clip>.json`, with the sub-step, the frames and the pair. `ARM_AUDIT_SNAP=f1,f2`
also draws those frames with the parts in collision in red.

## What the audit found

Every frame of each clip, checked after its update (`ARM_AUDIT=1`). "Before" is `ARM_NO_PLAN=1`, the straight joint
lines; "after" is with the planner. The JSONs are in [`out/collisions/`](../out/collisions/).

| Clip | Before | After | What was left, and what was done about it |
| --- | --- | --- | --- |
| Round 2 workflow | 130 of 1140 | **0** | Before: the vial into the holder on the MiR (4/6) and out again (5/6). The upper arm and forearm went through the cabinet, the holder, the VLM's front panel and the bay; the forearm hit the gripper and the vial. The planner's IK-branch choice cleared all of it. Re-rendered. |
| Warehouse | 216 of 1138 | 24, then **0** of 1120 | The planner left two things that no joint path could fix. The MiRs' routes crossed the 900 mm camera-target posts, and a parked wrist swept the VLM's bay while its MiR pivoted. A sub-agent moved one post and changed three routes, and added a check of the MiR bodies themselves (0 of 1120, `warehouse_mir.json`; 134 frames before). Re-rendered. |
| Lab set up from scratch | | 0 of 1376 | Its two joint moves were clear. Not re-rendered, but its floor shares the warehouse's moved post, so its committed render shows the old one. |
| Alloy route 1, vacuum-press version (`alloy_charge.py`) | | **0** of 2752 | Rebuilt round the vacuum press (`alloy_press.py`). Four things were needed beyond the planner. The plug goes into the cup at the rack, low down. The punch is handled level. Level grasps are aimed along a direction the checker finds clear (`aim()`), nearest the line from the arm's base: square to the tray, the rack cups nearest the base, the carrier's second pocket and the press off to the side all folded the arm into itself. Detours may not lift the arm more than 150 mm over the move's higher end: one RRT sample had sent it up to 2.2 m. Rendered as `out/alloy_charge_vacuum.*`. |
| Alloy route 1, round 5's doser version (`alloy_charge_doser.py`) | | 59 of 1875 | Rendered by round 5 before the check. Left: the arm in the press and in the rack's back cups (4/8). |
| Alloy route 2, atomize (round 5) | | 257 of 1421 | Rendered by round 5 before the check. Left: the gripper in the rePowder's hood (2/5), the arm in the MiR (5/5). |
| Alloy route 3, sieve and print (round 5) | | 543 of 2372 | Rendered by round 5 before the check. Left: the arm in the sieves of the stack (2/5), in the Aconity's cabinet (4/5). The planner's branch choice made one of its line moves flip the wrist; `line_to` now falls back to a planned joint move rather than stopping the render. |
| Alloy route 4, cut and test (round 5) | | 539 of 2068 | Rendered by round 5 before the check. Left: the gripper in the depowdering lance's hose (2/6), the arm in the Aconity and the shaker box (3/6). |

The round-4 versions of chapters 3 and 4, before round 5 rewrote them, went from 717 to 227 of 1310 frames and from
331 to 77 of 1466 with the planner.

## Limits

- **The audit trusts the meshes.** A part drawn as a solid box, such as a rack with its pockets as rims on top, is
  solid to the check. So the rules let a held part touch its fixtures at pick and place.
- **Contact, not depth** (until round 11). FCL reports contact between meshes. A brush of 1 mm and a pass straight
  through counted the same, so a run of frames was the measure. Round 11 measures depth (below).
- **Moving obstacles are planned against as they stand.** A move planned while a door is open doesn't know the door
  closes during it. The audit catches that.
- **Only the arms (and the warehouse's MiRs) are checked** (until round 11, which adds the movers check below).
  Instruments' own moving parts are `interference.py`'s job (round 5's MuJoCo sweep).

## Round 11: the stricter audit (the default for `ARM_AUDIT=1`)

Sterling, after the round-10 long-form (2026-11-13): the arm through a stream-camera post in chapter 5, collisions
loading and unloading the tensile bars and in the maintenance clip, and "There are probably other collisions and
interferences that I didn't catch from this". The audit missed them for two reasons besides chapter 5 never being
audited frame by frame:

- **What it allowed had no depth.** The gripper could touch anything in the subtree of a grasp's or release's groups
  within 4 s of the event, and a held part whatever it touched in its first and last frames held, however deep.
  Fingers sunk into a grip's jaws counted as "allowed".
- **It checked only the arms.** A person, a tray pulled out onto a table, a MiR's body or a door could pass through
  anything.

### Rule 1: what may touch, only up to 1.5 mm deep

The allowances stay (the gripper and the part it handles and that part's fixtures around a grasp or release; a held
part and where it came from and where it goes), but each contact is allowed only up to `ARM_AUDIT_DEPTH_MM` (1.5 mm)
deep. Anything else an arm, its gripper or what it holds touches is still a collision at any depth. The 4 s window is
now 4 s at the clip's own frame rate (it was 60 frames, which is 10 s at the 6 fps the chapters are audited at).

**FCL's own depth is not a depth for meshes.** `CollisionRequest(num_max_contacts=..., enable_contact=True)` gives
contacts with a `penetration_depth`, but for two triangle meshes (BVH-BVH) it is computed per pair of triangles: how
far one triangle reaches behind the other's plane inside the other's prism, the smaller of the two ways round. On a
coarse mesh that is the depth; on a fine one it is capped by the triangle size. Tested on known cases (a 20 x 20 mm
"finger" sunk into a 100 mm block; "fine" = the box subdivided to about 5 mm triangles):

| Sunk | coarse block, coarse finger | coarse block, fine finger | fine block, coarse finger | fine block, fine finger |
| --- | --- | --- | --- | --- |
| 0.3 mm | 0.3 | 0.3 | 0.3 | 0.3 |
| 3 mm | 3.0 | 3.0 | 2.86 | 2.86 |
| 10 mm | 10.0 | **1.11** | **2.86** | **1.11** |
| 25 mm | 25.0 | **2.78** | **2.86** | **2.78** |

A sphere sunk 8 mm read 0.5 mm, and a fine rod through a fine block 2.6 mm. So it can't tell fingers sunk 10 mm from
fingers brushing.

**The depth used instead: `collide.depth()`, a sampled translational penetration depth**, the standard definition (the
shortest move that separates two bodies). One body is moved by 1.5, 3, 6, 12, 25 and 50 mm along each of 26
directions (to a cube's faces, edges and corners, nearest the line between the two boxes' centres first) and the
answer is the first step at which some direction frees it, so "1.5" means "under 1.5 mm" and "12" means "6 to 12 mm"
(999: nothing up to 50 mm frees it). It needs only FCL's yes/no test, so it behaves the same on any mesh:

| Case (`python3 audit_all.py selftest` re-runs these) | coarse/coarse | coarse/fine | fine/coarse | fine/fine |
| --- | --- | --- | --- | --- |
| finger sunk 0.3 mm | 1.5 | 1.5 | 1.5 | 1.5 |
| finger sunk 1.0 mm | 1.5 | 1.5 | 1.5 | 1.5 |
| finger sunk 2 mm | 3 | 3 | 3 | 3 |
| finger sunk 3 mm | 6 | 6 | 6 | 6 |
| finger sunk 10 mm | 12 | 12 | 12 | 12 |
| finger sunk 25 mm | 25 | 25 | 25 | 25 |

A sphere sunk 0.5, 1, 3 and 8 mm reads 1.5, 1.5, 6 and 12; a 10 mm rod straight through the block 50; a finger
0.2 mm clear 0 (no contact). (These are before the shrink below: with it, a finger sunk 3 mm reads 3.) A depth exactly on a step reads the next step up, since a face-to-face touch still counts
as contact. It costs 0.1 ms for a shallow pair and about 1.2 ms for a deep one (26 tests per step).

**Fits.** A translational depth reads a peg in a bore as deep as it is inserted, since the shortest move that frees it
is pulling it out. Many parts here are drawn with zero clearance: a plug of the bore's own diameter, a punch's nose in
its guide ring. So `depth()` first shrinks the moving part by `TOUCH_MM` (0.3 mm) along its vertex normals (each
connected piece by the sign of its own enclosed volume, since `charge.lathe`'s faces wind whichever way the profile
runs): if the shrunk part clears the other, the two only touch, and the answer is 0.3. That is what `interference.py`
does with its 0.6 mm `TOUCH_MM`, for the tessellation's chord error. Then, for a 20 mm peg 20 mm into a ring
(`charge.lathe` parts, both windings): a bore of its own size reads 0.3 (touching), 0.3 mm clearance reads 0, and a
bore 0.6 mm too small reads 25. That last is an interference fit drawn where a real part would need a slip fit, so it
is reported. (An earlier version of this test put the ring off the peg's axis, since `pv.Cylinder` points along x by
default, and read 25 for every case.) A finger sunk 3 mm now reads 3 rather than 6: the shrink takes 0.17-0.3 mm off.

### Rule 2: the movers check

`collide.Movers`, run every audited frame after the arms:

1. **What moves.** Every group whose world matrix changed since the last audited frame (by more than 1e-6), except the
   arms' links and grippers and what each arm holds (the arm checks cover those): MiRs, trays, the extractor, doors,
   tables, people, parts riding on any of them.
2. **Rigid clusters.** Groups that moved by the same rigid motion (a MiR with its cabinet, holders and the parts on
   them) are one cluster and aren't checked against each other: their relative poses didn't change, so no new
   contact can appear between them. Two moving clusters are checked against each other once.
3. **Against what.** Every other visible body, except the group's own subtree and ancestors, the arms and what they
   hold, liquids, and **the floor and its markings**: anything whose top is within 6 mm of z = 0 (`FLOOR_MM`), the slab,
   the aisle and dock tape, the taped footprints. Tape is paint, and `props.mir250`'s skirt is drawn down to z = 0
   (the real MiR250 stands on its wheels with the body clear of the floor), so without this every drive read as the
   MiR's body 3 mm into the tape (audit-b's chapter 7 and the chapter-5 validation below, 7-22 frames a leg). The
   900 mm camera-target posts in the same `docks` group are solid and still checked. World boxes first, for every actor at once, filtered by each cluster's union box; then FCL on
   the meshes of the pairs whose boxes overlap, with BVHs built only for those (or taken from the arm checks' World).
4. **What counts.** The contacts a group had at its last pose before it started moving are its baseline and are left
   out while it keeps moving, until that pair comes apart (a MiR's wheels on the floor, a tray on its supports, a
   door on its hinge). A new contact counts if `depth()` puts it deeper than 1.5 mm, so a tray set down on a table or
   a MiR rolling onto a floor plate isn't reported.
5. **Scaled groups.** FCL takes only rigid transforms: a scaled matrix is read as a rotation and the scale dropped (a
   box stretched to plus or minus 6 didn't touch a probe at 4). A group drawn with a scale (the VLM's belts, a level)
   is checked as its vertices moved into the world instead, cached per matrix. (The arm checks still pass such
   matrices to FCL: nothing an arm handles is drawn scaled except a vial's contents, which are liquids or inside the
   vial.)

The results go in the same JSON, in a `"movers"` section grouped into runs (the moving group, the two bodies, the depth
per pair), and are printed after the arm's. The top-level `frames_with_collisions` is still the arm's count;
`frames_with_collisions_all` is either; `hits_allowed_before_but_too_deep` counts the contacts round 10's rules allowed
and the depth limit no longer does.

**Soft parts and hidden meshes.** `sc.soft` (a set of actor names, like `sc.fluids`) marks parts that are meant to
deform where they are drawn overlapping: an O-ring in its bore (chapter 1's punch: a 2.4 mm section squeezed 0.55 mm a
side), a pipette tip pressed onto its cone. The checks leave them out as they do liquids. A held part's hidden meshes
(alpha 0, such as chapter 3's legend sleeve on the LPBF jar) are left out too, as the world's always were (audit-b's
find).

### Switches

| | |
| --- | --- |
| `ARM_AUDIT_RULES=old` | round 10's rules: no depth limit, no movers check (for before/after numbers) |
| `ARM_AUDIT_MOVERS=0` | the depth limit without the movers check |
| `ARM_AUDIT_DEPTH_MM=2` | another limit (1.5 by default) |
| `ARM_AUDIT_SNAP=auto` (`auto:N`) | the first frame of each new run of collisions drawn (up to N, 24), aimed at the contact, the parts in red, to `ARM_AUDIT_SNAP_DIR` (`/tmp/r11_snaps`) with an index |
| `python3 audit_all.py run ch1 ch2 ...` | audit-a's clips one slot at a time; `summary` writes `out/collisions/round11_summary.json`, `sheet` the worst frames |

### Validation

- **Scenes with known answers** (`python3 audit_all.py selftest`, which runs them under `ARM_AUDIT=1`): a cart that
  stands 0.5 mm into the floor, rolls over a 0.8 mm plate and ends 20 mm into a wall; a lift sinking into its own cart;
  a door swinging through a post; a belt drawn with a scale growing 20 mm into a ceiling. Reported: the cart into the
  wall (25 mm), the door into the post (50 mm), the belt into the ceiling. Not reported: the floor (baseline), the plate
  (1.3 mm, under the limit), the lift (its own subtree). An arm holding a 30 mm cube and pushing it 10 mm into the
  fixture it is put down on: 4 frames, 12 mm, under the new rules; 0 under round 10's (`hits_allowed_before_but_too_deep`
  4).
- **Round 10's chapter 5, the quench** (Sterling's "at 32:57 the arm passing through the camera"): `alloy_workflow.py`
  as committed in round 10, section 6 alone (`CH5_FROM=6`, stopped after it, `VLAB_ONLY_TRAYS=F`), under the new
  rules. With camera F1 where round 10 had it (in front of the quench tank, put back for the test only): **the tongs
  through F1's post, 25 mm, frames 333-370 (28 frames)**, and the tongs 6 mm into the MiR's cabinet at their rest
  (frames 548-551), which round 10's rules allowed
  ([JSON](../out/collisions/round11_validation/ch5_section6_round10_camera_F1.json),
  [frame 333](../out/collisions/round11_validation/ch5_section6_round10_camera_F1_frame333.jpg)). With F1 behind the
  tank (the ch5 stream's 6c690a0) the post is clear; that run found the arm folding into itself (shoulder on forearm,
  upper arm on wrist 1, 6 frames) and the tongs 3 mm into the rack in four single frames, which the planner routed
  differently once the post had moved ([JSON](../out/collisions/round11_validation/ch5_section6_camera_F1_moved.json)).
  Chapter 5 is the ch5 stream's; these went to them.
- **Shared faults the movers check found first** (through audit-b's chapters and this validation), fixed by the
  orchestrator in `vlm.py` (063b014): stored trays, with their plates and service lines, went into the drawn column
  supports as they were stored (tray F, 50 mm, in the validation's first run); the safety shutter went 12 mm into the
  bay's side walls as it moved. The supports are now drawn only where a tray rests inside a slot, per Shuttle, and the
  walls stop 1 mm short of the shutter's path. And the MiR's body 3 mm into the floor tape on every drive, which is
  why the floor and its markings are left out (rule 2, point 3).

### Each clip, before and after (audit-a's clips)

Frames in collision, at the 6 fps the clips are rendered at. "Round 10's rules" is the committed JSON as round 11
started (d6eeeb7); "round 11" is the same code under the new rules; "after" is after this round's fixes. Arm / movers /
either. `python3 audit_all.py summary` gathers them into
[`out/collisions/round11_summary.json`](../out/collisions/round11_summary.json).

| Clip | Round 10's rules | Round 11, before | After | What it was |
| --- | --- | --- | --- | --- |
| Chapter 1, `alloy_charge.py` (re-rendered, 26e6a13) | 0 of 1145 | 29 / 11 / **40** | **0 / 0 / 0** | Fixtures drawn as solid blocks with their pockets only drawn as rims (the charge rack, the punch's rest), the pads 3 mm into the rack round a plug, cups let go 1 mm over their seats (so they rode 2 mm high into the press), the punch's O-ring squeezed in its bore. [Notes](alloy_charge.md#round-11-the-stricter-collision-audit-0-of-1145-frames-from-40) |
| Chapter 2, `alloy_atomize.py` (re-rendered, 7d93845) | 0 of 920 | 5 / 6 / **11** | **0 / 0 / 0** | The tong holder's tab filling half its bore, the latch loop's rods through the keeper's lip, the locking bolt sliding into a solid cylinder. [Notes](alloy_atomize.md#round-11-pr-318-2026-11-14-the-stricter-collision-audit) |
| Chapter 5's section 6 as round 10 had it (the validation, camera F1 put back) | never audited | 31 / 0 / **31** | (ch5's: F1 moved, 6c690a0) | The tongs through F1's post, 25 mm, 28 frames, and the tongs 6 mm into the MiR's cabinet: Sterling's catch, caught. [JSON](../out/collisions/round11_validation/ch5_section6_round10_camera_F1.json) |
| The 8:00 clip, `animate.py workflow` | 0 of 574 | 6 / 5 / **11** | 5 / 0 / **5** (not re-rendered: the fixes don't show) | The vial in tray B's solid rack; the vial in Ben's 9-vial TightFit holder in the CubXL (a grip by design: its lips are 25.9 mm across for a 27.5 mm vial, and the clip's vial is 28 mm); the CubXL's tip on its P20 cone and the liquid in the tip |

### What round 11's audit still can't see

- **Surfaces, not volumes.** FCL tests triangles against triangles. A part wholly inside another (a pin sunk out of
  sight in a block) crosses no surface and isn't a contact. Moving parts cross a surface on the way in, so the movers
  check and the arm checks see them arrive. Something drawn inside something else from the start, and never moved,
  isn't seen.
- **A baseline contact that deepens.** A mover's contacts at its last pose before it moved are left out until that pair
  comes apart. A pair that touches at the start and then goes deeper without parting (a tray sliding along a rail into
  a cross-member of the same mesh) isn't reported.
- **Soft parts and liquids are taken on trust.** `sc.soft` and `sc.fluids` leave whole actors out. Only seals, tips
  and liquids are marked; anything marked can't be checked.
- **Designed grips are reported, not hidden.** The 8:00 clip's vial in Ben's 9-vial "TightFit" holder in the CubXL is
  an interference by design: the holder's lips are 25.92 mm across, against the CubXL's own 27.5 mm stock vials and
  the clip's 28 mm vial. The rigid meshes overlap 0.6-1.0 mm a side, which reads as the vial's insertion depth. The
  holder is merged with other dark-PETG parts of the CubXL's body, so marking it soft would hide those too. It is left
  reported.
- **The depth is sampled.** 26 directions and the steps 1.5, 3, 6, 12, 25 and 50 mm: a contact reads "under 1.5" or
  "3 to 6", never 2.2. The shrink takes 0.17-0.3 mm off (vertex normals at a box's corners point diagonally).
- **ARM_AUDIT_SNAP=auto's aim** points the clip's own view direction at the contact from 0.8-3.5 m. Behind a machine
  housing the frame comes out dark (chapter 2's latch, frame 632). The JSON is unaffected.
- **FCL drops scale.** The movers check bakes scaled groups into the world; the arm checks still pass their matrices to
  FCL, and nothing an arm handles is drawn scaled except liquids.
