# Interference check in MuJoCo (`interference.py`)

Not to be confused with [`collide.py`](../collide.py), a separate check of the UR arm's own moves against the lab
(FCL, with RRT-Connect planning round obstacles).

Asked on PR #318: "For all those collisions and interferences, couldn't you use something like MuJoCo to simulate
this?" Yes. [`interference.py`](../interference.py) loads every animated model into MuJoCo and plays its tour through it:
every frame at the tour's 15 fps, with the same easing `tour.Rig` uses. It reports every place where two pieces
overlap.

The last review found its faults by rendering poses between keyframes and looking at them. This check computes
them at every frame instead. Two of that review's finds, put back into the furnace, are found again (see
[Does it find what the review found by eye?](#does-it-find-what-the-review-found-by-eye)).

| | |
|---|---|
| Run | `python3 interference.py` (every model), `python3 interference.py furnace xrd` (some), `xvfb-run -a python3 interference.py sheet` (the picture), `python3 interference.py mjcf furnace` (the MuJoCo model as MJCF, for `python3 -m mujoco.viewer`) |
| Output | [`out/interference.json`](../out/interference.json), every finding with its pieces, depth, volume, tour frames and position; [`out/interference_sheet.png`](../out/interference_sheet.png), the 12 deepest moving overlaps |
| Models | 31 in all. They are the 12 round-3 instruments, the 9 round-4 models, the 9 fabrication machines and the alloy route's plug press (`charge.py`, re-driven the way `alloy_charge.py` drives it). Ten were refitted by the other session (8fc52ed) and are checked as refitted |
| Not checked | the OpenFlexure v7, Delta and the six-microscope array: their meshes need OpenSCAD's nightly build and OpenFlexure's repositories ([`openflexure/README.md`](../openflexure/README.md)), which this run didn't build |
| Runtime | About 7 min the first time on the shared 4-core runner, almost all of it CoACD. After that, 2.5 min, with every part's convex pieces cached (`.cache/interference/hulls.pkl`), most of it the DED's 72 fused beads. MuJoCo's kinematics and collision take 0.1-0.5 ms a frame |
| Needs | `pip install mujoco coacd python-fcl manifold3d rtree` (MuJoCo 3.17 here) |

## How it works

1. **Geometry.** Every CadQuery part is tessellated at 0.4 mm chord and 0.2 rad, a little finer than the tours.
2. **Convex pieces.** MuJoCo collides convex shapes only: a mesh geom stands for its convex hull. A cabinet, a
   chamber or a door frame would then look solid and touch everything near it. So each part is tested first. A part
   whose volume is under 97 % of its hull's is split into convex pieces with CoACD (Wei et al., SIGGRAPH 2022,
   concavity threshold 0.04). Here 270 of the 1,334 parts are not convex. With them, the 31 models make 3,580 MuJoCo geoms.
3. **The MuJoCo model.** It is built with `MjSpec`, one body per moving piece, nested as the pieces ride on each other
   (`Joint.parent`):
   - `slide` is a slide joint;
   - `hinge`, `spin` and `turn` are a hinge through the pivot;
   - `path` and `track` are three slides;
   - `fade` pieces are welded to their parent;
   - a `follow` joint is three slides and a ball, at the nearest rotation;
   - a piece whose joint stretches is left out and listed, since no rigid body can follow it. These are the rebuilt
     LumenPnP's cable chains, whose runs lengthen with the carriage.

   Each frame's joint values become `qpos`, taken from each joint's own matrix. MuJoCo's body poses then match the
   tours' to within 10⁻¹² mm on every model.
4. **Sweep.** At every frame, MuJoCo's collision pipeline (broad phase, then convex-convex narrow phase) lists the
   penetrating contacts between two different pieces. Parent-child pairs are checked too (`filterparent` off).
5. **Exact check.** A contact counts only if the two parts' own triangle meshes overlap at that frame. FCL
   (`python-fcl`) tests the surfaces for a crossing, and a point-in-mesh test catches one part wholly inside another.
   manifold3d then intersects the two solids for the overlap's volume and thickness: its thinnest extent, along its
   principal axes, capped at 4 V / A so that a U-shaped overlap reads as its walls' depth. The hulls cover the parts
   they stand for, so MuJoCo can't miss an overlap the meshes have. The exact check removes what the hulls add:
   3,233 of MuJoCo's 78,338 candidate contacts here. Intended pairs are re-checked every 10th frame only, since
   the DED's beads alone make 58,000.
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

With those two taken out, the round-4 furnace was clean: its tray rests on the chamber floor, nothing more. (The refitted furnace adds its own door touching its hinge knuckles, 1.5 mm: see below.)

## What it found

After the fixes below, 28 pairs of parts still overlap by 2 mm or more as something moves. They come from 13 pairs of
pieces in 10 models. The other 21 models have none. Each is drawn at its worst frame in
[`out/interference_sheet.png`](../out/interference_sheet.png): the two pieces in colour, the rest faint, the overlap in
red.

| Model | What runs into what | Deepest | Tour frames | Reading |
|---|---|---|---|---|
| Meltio M450 | the head's carriage into the Z column | 30.0 mm | 116-230 | the open item below |
| Plug press (`charge.py`) | the ejector pin through the press's base and rail | 7.6 mm | 12-163 | The base needs a slot for the pin as the nest slides; drawn solid |
| Form 4 (refit) | the cover, swinging up, through the cartridge cap, the resin tank and the deck | 6.7 mm | 62-180 | The cover's arc or its hinge needs to move |
| PLX-Benchtop PIP (refit) | the indenter's tip and cylinder into the sample | 6.0 mm | 35-202 | It should stop at the sample's face, plus the indent |
| Packaging | the bagged jar into the foam pocket's floor and walls, and the lid's foam down onto it | 6.0 mm | 219-432 | The bag is drawn as a rigid 84 mm box round the 61 mm jar, and the pocket is 80 mm wide. Widen the pocket, or draw the bag as film |
| CubXL corrosion | the capper through tip racks 1 and 2 at travel height, and into tip A2 | 4.6 mm | 82-455 | The travel height is CubOS's own (z 122). Either the capper or the racks are drawn too tall, or the real head would hit them too: worth checking on the machine |
| LumenPnP (refit) | the head's Z motor into the right nozzle's back plate | 4.0 mm | 256-571 | As nozzle 1 goes down, nozzle 2 rises into the motor |
| PX500 polisher (refit) | mounts 4-6 through the column as the holder turns | 4.0 mm | 80-269 | The holder turns too close to the column |
| Packaging | the AP380's pressure roller and arm into the jar | 3.6 mm | 113-192 | The roller should stop on the jar |
| VHX + EA-300 (refit) | the EA-300's side panel into the arch as the head tilts | 3.2 mm | 65-135 | |
| Mastersizer (refit) | the vial through the clear cover as it lifts | 2.0 mm | 34-59 | |

**Built in and guide overlaps are mostly modelling shortcuts.** 25 pairs overlap by 2 mm or more as modelled, and
37 more are guides. Each is a part drawn solid where the real one is bored or slotted:
- a crosshead through its columns (both Instrons, the PIP);
- a ram retracted into a solid head (the plug press);
- carriages on their rails (the CubXL, the LumenPnP);
- LPBF pistons in solid housings;
- the DED head's carriage and powder lines in the cabinet's top.

They don't show in the renders, but a cutaway would show them. All are in the JSON.

**Minor overlaps, 0.6 to 2 mm: 34 moving pairs.** One is the furnace's refitted door, which touches its own hinge
knuckles (1.5 mm).

**Coming loose: 16 pieces.**
- **Doors and lids hang off their hinges.** No hinge is drawn, so when open they stand 10-59 mm off the machine: the
  Form Wash's lid 59 mm, the XRF's hood 42 mm, the DED's door 34 mm.
- **The AP380's pressure arm floats 25 mm off the labeller as modelled.**
- **The Meltio head comes 30 mm off its column** (the open item below).
- **Some are meant to.** The Mastersizer's vial and the sieve's container are props carried by an unseen hand, and
  the dock's tray is meant to leave.

**Left out: pieces no rigid body can follow.** The rebuilt LumenPnP's four cable-chain pieces stretch (`follow`
joints), so they are left out of its check.

## The four open items from the last review

| Item | What the check says |
|---|---|
| The rail's cable chain doesn't follow the carriage | **Not an overlap, a missing link.** Nothing on the rail overlaps at any frame. The chain is a fixed box in the rail's body, from x = −1900 to 0 mm. At full travel (1600 mm) the carriage's trailing edge is at x = 1387 mm, so the chain stops 1387 mm short of it. It needs a moving end on the carriage: a bend that rides at half the carriage's speed and an upper run that goes with it. The rail is being reworked separately this round, so it isn't changed here. |
| The cut bars stay on the EDM plate | **Not an overlap either.** The wire runs through each bar's base (2.0 mm, the wire's own diameter: the cut, listed as intended), and the bars stay where they are. They are parts of the plate's piece (`load`), so no joint can part them. To show them dropping into the tank they need a piece of their own, faded in or carried on a short path once the wire is past. |
| The Meltio head's arm runs into its Z column | **Confirmed: 30 mm deep, tour frames 116-230**, whenever the head goes round the far side of the wall. On the near side the arm pulls 30 mm clear of the column, so the head floats (the coming-loose check sees that too). The arm is fixed to the head, and the head moves in y with nothing behind it to slide on. A real fix is a kinematics choice, so it isn't made here. Either the bed carries the wall in x and y under a head that only moves in z, or the arm slides through a carriage on the column. |
| The v7's brass nut doesn't ride with its column | **Not checked.** The OpenFlexure meshes aren't built in this run: they need OpenSCAD's nightly build and the two OpenFlexure repositories, about an hour of setup ([`openflexure/README.md`](../openflexure/README.md)). Once `.cache/openflexure/` is there, `python3 interference.py openflexure_v7` checks it. The flexures' `follow` joints are small affine motions; MuJoCo gets their nearest rigid motion. |

## What it fixed

Clear, small faults only. Each was re-checked after the change, and again after merging the other session's ten
refits (8fc52ed).

| Model | Fault | Fix | After |
|---|---|---|---|
| Wire EDM, `instruments.py` | The tank door dropped 490 mm through a solid base: 30 mm deep, with its window and warning label | A slot in the base for it to drop into | Clear |
| XRF, `instruments_char.py` | The powder cup clipped the open lid's front edge on its way in: 10.1 mm at frame 67, and 8.4 mm at frame 62 on the refitted hood | It comes down in front of the lid, then in under its front edge (the lid opens only 35°), then down into the seat | Clear |
| MPRINT, `fab_metal.py` | The 150 mm build plate came in from the side and clipped the door frame: 11.7 mm, frames 132-134 and 410-411. Lined up first, it then met the door, which opened while the plate moved | The plate lines up square to the door, and the door is open before the plate moves. The path is shared with the MetalONE and SnowPod | Clear |
| Meltio M450, `fab_metal.py` | The substrate plate clipped the front frame on its way in: 7.95 mm, frame 49 | The same: square to the opening first | Clear |
| LumenPnP, `fab_pcb.py` (Opulo's CAD) | The board lifted out while the head was still over it: through the nozzle holder, the camera mask, the Z motor and the board mount, 1.6-2.0 mm, frames 587-591. The rebuilt model had the same move as the old one | The head goes home first, then the board leaves | Clear |
| CubXL, `instruments_lab.py` | The two used tips landed in the same spot in the waste: 5.2 mm, frames 483-531 | The second lands 8.5 mm beside the first | Clear |
| Packaging, `instruments_lab.py` | The jar went through the next jar waiting in the nest: 18.1 mm, frames 20-22 | It comes in over the next jar's cap, then down | Clear |
| XRD, `instruments.py` | The door ran 3.05 mm into the left post as it opened. A door set in its frame and hinged at its front edge swings its back corner out by hypot(w, t) − w, 4.1 mm against 1 mm of clearance | 6 mm on the free side; dropped in the merge, because the refitted door hinges elsewhere and is clear | Clear (the refit) |

They need their tours re-rendered:
- `xvfb-run -a python3 tour.py wire_edm xrf cubxl_corrosion packaging`;
- `xvfb-run -a python3 fab_tour.py mprint metalone snowpod meltio_m450 lumenpnp`.

The MetalONE and SnowPod share the MPRINT's plate path, so their tours change too. After that come the joined
tours and galleries: `python3 tour.py gallery join` and `python3 fab_tour.py gallery join`.

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
  0.1-0.5 ms a frame here. The same model can later run physics:
  - gripper contact with friction: a charge cup in the 2F-85's pads, the build plate lifted by its lug;
  - parts that drop: the EDM's cut bars into the tank;
  - the press-fit plug's force.

  Its limit is convex shapes only, hence CoACD. It also models powder poorly: granular flow is a job for DEM codes
  (LIGGGHTS, Yade), not MuJoCo.
- **FCL** works on the exact meshes, with no decomposition, and gives distances. It is better for a plain yes or no,
  and for gaps. It has no dynamics.
- **Here** MuJoCo finds the candidates, then FCL and manifold3d confirm and measure them.
