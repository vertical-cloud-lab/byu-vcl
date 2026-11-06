# The multi-doser in the lab: chain carousel v5 on an A&D HR-202i (round 9)

[`carousel.py`](../carousel.py) runs powder-doser's own CAD for the multi-doser: byte-for-byte copies of
[`cad/chain-carousel-v5/`](https://github.com/vertical-cloud-lab/powder-doser/tree/353dae78829ef8fffaa1bd584876a157145a0b76/cad/chain-carousel-v5)
at `353dae7` (PR #185's head, 2026-11-05) and the vendor helpers it imports, in [`../multidoser/`](../multidoser/)
(file list and SHA-256s in its README). It appears in two clips: the 8:37 one (`animate.py workflow`, a vial dosed for
the CubXL) and chapter 1 (`alloy_charge.py`, the atomizer's charge cups), and stands on tray B in every whole-lab
scene (`setup_lab.py`). Sterling's two points of 2026-11-05 22:56 on PR #318 that this answers:

1. "we have an updated version of the multi-doser [powder-doser PR #185 comment]. You'll need to make changes across a
   couple places (both vial dosing and charge cup dosing) ... Noting also that you'll be putting the balance
   underneath."
2. "during the dispensing at 8:37 or so the vial ... is still oriented 90 degrees the wrong way (laying flat instead of
   the top towards the top)."

## What v5 is

From the [v5 comment](https://github.com/vertical-cloud-lab/powder-doser/pull/185#issuecomment-6638969198) and v5's
[README](https://github.com/vertical-cloud-lab/powder-doser/blob/353dae7/cad/chain-carousel-v5/README.md); numbers
marked (computed) are ours, from the copied `layout.py`:

- **v4 with the station rebuilt round an A&D HR-202i** (220 g × 0.1 mg, plus a 51 g × 0.01 mg fine range; RS-232C
  only). It stands on the bench under the dose point, inside the U-shaped base, touching nothing of the doser.
- **The electronics carriage (EC) rides an 8 mm lift bar carried by two Actuonix P16s**, one each side of the balance
  (P16 axes at y ±146 mm), with guided shoes in slots on two station posts that leave their slots as the EC seats. It
  rises 28 mm from park to dock (`PARK_DROP`), docks under the station module and tilts it to 30° (40° at most: past
  about 41° the bar meets the neighbouring modules).
- **The carousel is 80 mm higher** (top rail 831 mm) so the parked EC (328 mm) and the NEMA 34 (332.5 mm) clear the
  316 mm balance. The front base rail and both station rails are gone; the latch rail hangs from a 2020 beam.
- **No funnel and no load cell.** A 25 mL beaker on a printed riser (rim at 282 mm) goes in through the balance's -y
  side door; the top door slides back 205 mm; the dose falls 154 mm into the beaker; `chain_rig.py dose-to` doses by
  weight in quarter auger turns, reading the balance over RS-232 (`Q`, 2400 7E1) after each. The exit stays on the
  hinge axis, 435.8 mm over the bench (computed), at every tilt.
- **Front hatch 300 × 330 mm**, open down to the bench: a hand reaches the side doors through it. The doors are opened
  by hand: v5 says a robot-served station needs an actuator.
- **HR-202i model**: checked against A&D's [HR-i manual](https://www.aandd.jp/products/manual/balances/hr-i.pdf)
  p.59-60 and A&D's 1:1 DXF: 200 × 428 × 310 mm body, pan Ø90 with its top 50 mm up, chamber 183 × 164.5 × 250 mm,
  side doors 148.5 × 251 mm whose opening's top is 291 mm up, doors sliding back 205 mm. A&D has discontinued it
  (MNM Scales: $2,989, out of stock, "replaced by GH-202").
- **Interference** (v5's own OCC checks): 0 at home over all 843 instances, 0 parts in the balance's way, 0 over the
  rise and tilts to 40°, 0 on a chain sweep. **BoM** $2,361.63 ($2,220.24 without test gear), the balance at $0.
- **Not done in v5**: the MuJoCo station model and the swap check re-run; the vibration through the bench (T8a); the
  154 mm fall's strays for fine powders (T8b); the two P16s tracking within 2 mm (T6).

## How it is run here

- `carousel.CL = layout`, `carousel.CP = params` (the copies). `layout.placements(State(...))` gives every part
  instance for a chain shift, the EC's lift (`ext`, 0 parked to 28 docked) and tilt, an auger turn, the solenoid and
  the balance's doors (`top_door`, `side_door`, 0-205 mm). The animation eases those numbers; every frame is the rig's
  own kinematics.
- **Vendor STEPs**: McMaster's, Actuonix's and StepperOnline's files can't be redistributed, so they are not fetched.
  With no `cad/vendor/files/`, the copied builders draw their own parametric stand-ins, exactly as powder-doser does on
  a checkout without them. Sam's plate and EC, the auger and its cap are fetched from v4's `reference/` (the same three
  files round 8 used for v2) and hash-checked.
- **One import quirk**: v5's vendor helpers import `common`, and so does the lab (`lab_models/common.py`, via `vlm.py`).
  `carousel._import_v5` swaps the lab's out for the import and puts it back, and takes `vendor/` off `sys.path` after.
- 841 instances, 96 unique parts, 499k triangles placed (68k tessellated), 13 ms per `placements` call; actors whose
  instances didn't move keep their meshes (and `collide.py` keeps their collision trees).
- Round 8's v2 copies are removed: nothing runs v2 any more.

## What is ours (drawn in the lab's PETG teal)

**Why a shuttle: no gripper reaches v5's pan.** The way to the balance's -y side door passes between the frame's front
post (x ≤ -36.4 mm, rig frame) and the -y station post that carries the P16 (x ≥ 81 mm): 117 mm. The Robotiq 2F-85's
knuckles span 127-138 mm whatever it grips (`ur_arm.gripper_fk`, closure 0.55-1.0), so a 2F-85 carrying a vial or a cup
cannot pass. An FCL sweep of the gripper along that line (`/tmp` check, round 9) hit the front post, the station post
and the P16 from 60 mm out onward. v5's front hatch is for a hand. So:

- **Vessel shuttle**: a fork (36 mm wide, 180 mm long, 4 mm thick, a 13 mm × 30 mm slot at its tip) on a carriage
  that runs on a rail along y, x = 33.4 mm (the pan's centre), the rail 110-130 mm up from y -110 to -470 mm, held by a
  bracket on the -y base rail and a leg on the tray. The arm sets the vessel on the fork at y -270 mm, 71 mm outside
  the -y acrylic panel; the shuttle carries it 254.8 mm in, through the open side door, 6 mm over the pedestal, and
  drops 10 mm: 6 mm sets the vessel down, 4 mm leaves the fork clear under it, and the fork backs out round the
  pedestal through its slot. To take it out, the reverse. Only the vessel's foot touches the balance (on the pedestal).
- **Pedestal riser**: v5's riser (80 mm foot, 44 mm tube) with an 11 mm neck 20 mm tall on top, so the vessel stands
  at 219 mm: the vial's rim at 280 mm (a 155.8 mm fall), a charge cup's at 282.5 mm (153.3 mm), both against v5's 282
  mm and 154 mm. Lifted 6 mm on the fork, the cup's rim (288.5 mm) still passes under the door opening's 291 mm top.
  The neck centres a cup's 12.7 mm bore under the 8 mm stream to within the fork's placement.
- **A port** 67 × 200 mm in the -y acrylic panel (x 0-67, z 100-300 mm) for the shuttle.
- **Door pushers**: v5's doors are slid by hand. Two belt slides on the bench inside the base, 14 mm off the
  balance's sides, whose fingers take a door's grip only while they move it, so nothing touches the balance while it
  weighs: one for the -y side door, one reaching over to the top door's front grip.
- **On tray B the top panel lies on the top rails** (its 6 mm standoffs go into the rails): the rig is 854 mm tall,
  under the Shuttle's 856.5 mm product height (`vlm.MAX_GOODS_H`, our estimate for a 996 mm opening). As powder-doser
  draws it, 860 mm would not pass the opening.

Checked (FCL, rig frame, side door open): the fork at both heights, the vial and a cup, at 41 positions along the
travel, against every part of the rig, the pushers, the rail and the pedestal: **no contact**. With the EC docked and
tilted to 30° and the top door open, the vial and a cup on the pedestal: **no contact**. Designs, not built; their
dimensions are ours and estimates.

## On tray B

- **The rig is no longer turned.** Round 8 stood v2 turned 90° on the tray. v5 stands as powder-doser draws it, its
  -y side (side door, port, shuttle) toward the opening and the arm, at (150, 50) on the tray (`animate.LOADS`): the
  rig spans x 20-540, y -149 to 270 mm, the shuttle's leg reaches y -415. The electronics board lies flat left of the
  rig, behind the vial rack (x -380 to -80, y -310 to 110).
- **Tray B's slot is taller**: `vlm.COLUMNS` R3 from 775 to 900 mm (854 mm of rig, 3 mm of tray floor and 20 mm clear,
  on the 25 mm pitch). Shuttle 1's rear column then fills 3,125 of its 3,390 mm; tray E (R4) moves up 125 mm.
- `services.py`'s fixed box for the carousel (560 mm tall) and `reach.py`'s seat for the doser's cup are round 8's;
  neither is ours to edit.

## The vial (Sterling's point 2)

Round 8's vial lay on its side at 8:37 because it was taken from the rack from above (gripper pointing down) and set in
the doser's cup with the gripper level: the vial turned with the gripper. Now the gripper takes it from above and sets
it down from above, upright, on the shuttle's fork, and the shuttle carries it in and out; it takes it from the fork
from above again for the MiR's holder. It never leaves the vertical.

## Rendered (2026-11-06)

| Clip | Length | Frames (6 fps, 1280 × 720) | Arm audit (same pass) | Files |
|---|---|---|---|---|
| 8:37, `animate.py workflow` (the whole lab, Shuttles see-through) | 111.8 s | 671 | **0 of 574** checked frames in collision | [MP4](../out/mp4/vlm_workflow.mp4) (7.9 MB), [GIF](../out/vlm_workflow.gif) (4.6 MB, made from the MP4 at 4 fps, 560 px: `lab_scene` writes none), stills `out/vlm_workflow_{dose,vial,still}.png`, [audit](../out/collisions/vlm_workflow.json) |
| Chapter 1, `alloy_charge.py` | 254.3 s | 1526 | **0 of 1145** | see [`alloy_charge.md`](alloy_charge.md) |

![8:37: the vial upright on our pedestal on the HR-202i's pan while module 6 doses into it](../out/vlm_workflow_dose.png)

Two things found on the way, both fixed: v5 swaps the station module's outlet-door spring for its compressed mesh as
the EC docks (`door_spring` / `door_spring_open`), so `Carousel.set` allows that one key to change; and the first
chapter-1 render died at its first frame because its X display (:32) never came up ("bad X server connection"), not
because of the scene; re-queued on another display, it ran.

The CubXL half of the 8:37 clip opens one cap only (the seawater stock), so it needs no parking spot for a second cap
(the cubxl stream's note in [`cubxl_corrosion.md`](cubxl_corrosion.md), round 9).

## Open

- **Which balance the lab has.** v5 found no record that the lab owns an HR-202i; the documented 0.1 mg balance is
  the HR-100A (102 g), which fits the station with the hatch door's edge raised. A Cu charge cup reads 135.7 g, over
  the HR-100A's 102 g.
- **The shuttle, the pedestal and the pushers are ours**, not powder-doser's: worth a powder-doser issue if the station
  is to be robot-served. Strays from a 153-156 mm fall, the pedestal's centring of a cup's bore, and whether the
  fork's drop disturbs a reading are untested.
- **The 2F-85's knuckles** are the binding number: a narrower gripper (or a v5 station post moved) would let the arm
  reach the pan itself.
