# Interference check in MuJoCo (`collide.py`)

Asked on PR #318: "For all those collisions and interferences, couldn't you use something like MuJoCo to simulate
this?" Yes. [`collide.py`](../collide.py) loads every animated model into MuJoCo and plays its tour through it:
every frame at the tour's 15 fps, with the same easing `tour.Rig` uses. It reports every place where two pieces
overlap.

The last review found its faults by rendering poses between keyframes and looking at them. This check computes
them at every frame instead. Two of that review's finds, put back into the furnace, are found again (see
[Does it find what the review found by eye?](#does-it-find-what-the-review-found-by-eye)).

| | |
|---|---|
| Run | `python3 collide.py` (every model), `python3 collide.py furnace xrd` (some), `xvfb-run -a python3 collide.py sheet` (the picture), `python3 collide.py mjcf furnace` (the MuJoCo model as MJCF, for `python3 -m mujoco.viewer`) |
| Output | [`out/collisions.json`](../out/collisions.json), every finding with its pieces, depth, volume, tour frames and position; [`out/collisions_sheet.png`](../out/collisions_sheet.png), the 12 deepest moving overlaps |
| Models | RUN_MODELS |
| Not checked | the OpenFlexure v7, Delta and the six-microscope array: their meshes need OpenSCAD's nightly build and OpenFlexure's repositories ([`openflexure/README.md`](../openflexure/README.md)), which this run didn't build |
| Runtime | RUN_TIME |
| Needs | `pip install mujoco coacd python-fcl manifold3d rtree` (MuJoCo 3.17 here) |

## How it works

1. **Geometry.** Every CadQuery part is tessellated at 0.4 mm chord and 0.2 rad, a little finer than the tours.
2. **Convex pieces.** MuJoCo collides convex shapes only: a mesh geom stands for its convex hull. A cabinet, a
   chamber or a door frame would then look solid and touch everything near it. So each part is tested first. A part
   whose volume is under 97 % of its hull's is split into convex pieces with CoACD (Wei et al., SIGGRAPH 2022,
   concavity threshold 0.04). NONCONVEX
3. **The MuJoCo model.** It is built with `MjSpec`, one body per moving piece, nested as the pieces ride on each other
   (`Joint.parent`):
   - `slide` is a slide joint;
   - `hinge`, `spin` and `turn` are a hinge through the pivot;
   - `path` and `track` are three slides;
   - `fade` pieces are welded to their parent;
   - OpenFlexure's `follow` flexures would be three slides and a ball, at the nearest rotation.

   Each frame's joint values become `qpos`, taken from each joint's own matrix. MuJoCo's body poses then match the
   tours' to within 10⁻¹² mm on every model.
4. **Sweep.** At every frame, MuJoCo's collision pipeline (broad phase, then convex-convex narrow phase) lists the
   penetrating contacts between two different pieces. Parent-child pairs are checked too (`filterparent` off).
5. **Exact check.** A contact counts only if the two parts' own triangle meshes overlap at that frame. FCL
   (`python-fcl`) tests the surfaces for a crossing, and a point-in-mesh test catches one part wholly inside another.
   manifold3d then intersects the two solids for the overlap's volume and thickness: its thinnest extent, along its
   principal axes. The hulls cover the parts they stand for, so MuJoCo can't miss an overlap the meshes have. The
   exact check removes what the hulls add.
6. **Sorting.** By thickness:
   - under 0.6 mm is **touching**, within the tessellation's own error;
   - 0.6 to 2 mm is **minor**;
   - 2 mm or more is a **fault**.

   By kind:
   - **motion:** it appears as something moves;
   - **built in:** the pieces overlap as modelled, before anything moves;
   - **guide:** a piece drawn solid through the rail or column it rides on, the same overlap at every frame.

   Contacts a model is meant to have are listed in `INTENDED`, each with its reason, and reported as intended
   rather than dropped. Examples: a specimen in its grips, a plug in its bore, the EDM wire through the bars it cuts,
   DED beads fused to each other.
7. **Coming loose.** At rest and at the end of every action, the least distance from each moving machine piece to
   the rest of the machine. A piece more than 10 mm away has come loose. That is the other half of what the last
   review found, parts floating: a frame 90 mm above its columns, a motor with no pinion.

Liquids, powders, glows, beams and overlays are not solids and are left out, by material and by piece (`VISUAL`,
`VISUAL_PIECES`).

## Does it find what the review found by eye?

Two of the round-3 review's furnace faults, put back for a test (not committed):

| Seeded fault | Found |
|---|---|
| The door hinged to swing inwards (`deg=-100`, the round-3 bug) | door through the housing, 83.6 mm deep, from frame 10 (2 frames into the swing) to 117 |
| The coupon tray waiting in front, inside the door's swing | door through the tray, 8.3 mm, frames 16-25, and through each coupon |

With the round-4 fixes in place, the furnace is clean: the tray touches the chamber floor, nothing more.

## What it found

FINDINGS

## The four open items from the last review

| Item | What the check says |
|---|---|
| The rail's cable chain doesn't follow the carriage | **Not an overlap, a missing link.** Nothing on the rail overlaps at any frame. The chain is a fixed box in the rail's body, from x = −1900 to 0 mm. At full travel (1600 mm) the carriage's trailing edge is at x = 1387 mm, so the chain stops 1387 mm short of it. It needs a moving end on the carriage: a bend that rides at half the carriage's speed and an upper run that goes with it. That is fork 6's (the rail is theirs). |
| The cut bars stay on the EDM plate | **Not an overlap either.** The wire runs through each bar's base (2.0 mm, the wire's own diameter: the cut, listed as intended), and the bars stay where they are. They are parts of the plate's piece (`load`), so no joint can part them. To show them dropping into the tank they need a piece of their own, faded in or carried on a short path once the wire is past. |
| The Meltio head's arm runs into its Z column | **Confirmed: 30 mm deep, tour frames 116-230**, whenever the head goes round the far side of the wall. On the near side the arm pulls 30 mm clear of the column, so the head floats (the coming-loose check sees that too). The arm is fixed to the head, and the head moves in y with nothing behind it to slide on. A real fix is a kinematics choice, so it isn't made here. Either the bed carries the wall in x and y under a head that only moves in z, or the arm slides through a carriage on the column. |
| The v7's brass nut doesn't ride with its column | **Not checked.** The OpenFlexure meshes aren't built in this run: they need OpenSCAD's nightly build and the two OpenFlexure repositories, about an hour of setup ([`openflexure/README.md`](../openflexure/README.md)). Once `.cache/openflexure/` is there, `python3 collide.py openflexure_v7` checks it. The flexures' `follow` joints are small affine motions; MuJoCo gets their nearest rigid motion. |

## What it fixed

Clear, small faults only. Each was re-checked after the change.

| Model | Fault | Fix | After |
|---|---|---|---|
| XRD, `instruments.py` | The door ran 3.05 mm into the left post as it opened (frames 10-246). A door set in its frame and hinged at its front edge swings its back corner out by hypot(w, t) − w: 4.1 mm for this 397 × 57 mm door, against 1 mm of clearance | 6 mm clearance on the free side | FIX_XRD |
| Wire EDM, `instruments.py` | The tank door dropped 490 mm into a solid base: 30 mm deep, with its window and warning label | A slot in the base for it to drop into | FIX_EDM |
| XRF, `instruments_char.py` | The powder cup clipped the open lid's front edge on its way in: 10.1 mm, frame 67 | It comes in 80 mm higher, over the edge, then down | FIX_XRF |
| MPRINT, `fab_metal.py` (shared with the MetalONE and SnowPod) | The 150 mm build plate came in from the side and clipped the door frame: 11.7 mm, frames 132-134 and 410-411 | It lines up square to the door first | FIX_MPRINT |
| Meltio M450, `fab_metal.py` | The substrate plate clipped the front frame on its way in: 7.95 mm, frame 49 | The same: square to the opening first | FIX_MELTIO |
| LumenPnP, `fab_pcb.py` | The board lifted off while the head was still over it, through the nozzle, the ring light and the top camera: 1.6 mm, frames 426-430 | The head parks first, then the board leaves | FIX_PNP |

Each one needs its tour re-rendered: `xvfb-run -a python3 tour.py xrd wire_edm xrf`, then
`xvfb-run -a python3 fab_tour.py mprint metalone snowpod meltio_m450 lumenpnp`. The MetalONE and SnowPod share the
MPRINT's plate path, so their tours change too. After that come the joined tours and galleries:
`python3 tour.py gallery join` and `python3 fab_tour.py gallery join`.

## Limits

- **Sampled, not continuous.** Every tour frame is checked, and nothing in between. A part that moves farther than
  its own thickness in one frame can pass through a thin one unseen. The EDM's 2 mm wire moves about 7.5 mm a frame
  and still shows in every bar it crosses, because the bars are 12 mm wide. FCL's continuous collision
  (`fcl.continuousCollide`) would close the gap.
- **Kinematic only.** No forces, no gravity. A prop carried by an unseen hand floats, and nothing falls.
- **The arm is not in the instrument models.** The UR10e's own moves are checked against the lab by `reach.py`'s IK
  study, not here.
- **Thin parts.** Overlaps under 0.6 mm are reported as touching: the tessellation's chord error is 0.4 mm.
- **The intended list is judgement.** Each entry has its reason in `INTENDED`.
- **Not checked:** the OpenFlexure models, the VLM itself (`vlm.py`), and the chapter scenes (`animate.py`,
  `alloy_*.py`, `setup_lab.py`), whose motion is scripted per frame rather than by `Instrument` joints. The charge
  press is the exception, re-driven from `alloy_charge.py`'s sequence.

## MuJoCo, FCL, or both

- **MuJoCo** has a fast collision pipeline. It checks all pairs at once, broad phase then narrow phase, in about
  MJ_MS ms a frame here. The same model can later run physics:
  - gripper contact with friction: a charge cup in the 2F-85's pads, the build plate lifted by its lug;
  - parts that drop: the EDM's cut bars into the tank;
  - the press-fit plug's force.

  Its limit is convex shapes only, hence CoACD. It also models powder poorly: granular flow is a job for DEM codes
  (LIGGGHTS, Yade), not MuJoCo.
- **FCL** works on the exact meshes, with no decomposition, and gives distances. It is better for a plain yes or no,
  and for gaps. It has no dynamics.
- **Here** MuJoCo finds the candidates, then FCL and manifold3d confirm and measure them.
