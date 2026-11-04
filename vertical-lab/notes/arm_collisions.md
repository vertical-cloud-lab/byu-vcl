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
| Alloy route 1, the charge | | **0** of 2752 | Rebuilt round the vacuum press (`alloy_press.py`). Four things were needed beyond the planner. The plug goes into the cup at the rack, low down. The punch is handled level. Level grasps are aimed along a direction the checker finds clear (`aim()`), nearest the line from the arm's base: square to the tray, the rack cups nearest the base, the carrier's second pocket and the press off to the side all folded the arm into itself. Detours may not lift the arm more than 150 mm over the move's higher end: one RRT sample had sent it up to 2.2 m. Re-rendered. |
| Alloy route 3, sieve and print | 717 of 1310 | 227 | Every IK solution for standing the jar in the cup on the MiR's own cabinet has the upper arm in the cabinet (3/5). The fingertips also touch the sieve knobs. Needs new poses or a new place for the cup. Not re-rendered: another session was rewriting this chapter. |
| Alloy route 4, cut and test | 331 of 1466 | 77 | The wrist enters the Aconity's shell to take the plate (3/6), and the forearm and wrists enter the wire EDM's body while the plate is cut and the bar taken (5/6). Needs new poses. Not re-rendered, for the same reason. |
| Alloy route 2, atomize | | | Doesn't run: `alloy_atomize.py` still reads `charge.RUNS` in its pre-round-5 form. |

## Limits

- **The audit trusts the meshes.** A part drawn as a solid box, such as a rack with its pockets as rims on top, is
  solid to the check. So the rules let a held part touch its fixtures at pick and place.
- **Contact, not depth.** FCL reports contact between meshes. A brush of 1 mm and a pass straight through count the
  same, so a run of frames is the measure.
- **Moving obstacles are planned against as they stand.** A move planned while a door is open doesn't know the door
  closes during it. The audit catches that.
- **Only the arms (and the warehouse's MiRs) are checked.** Instruments' own moving parts are `interference.py`'s
  job (round 5's MuJoCo sweep).
