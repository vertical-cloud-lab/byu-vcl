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
