# Round 8, the lab stream (#303, PR #318)

Sterling's review of 2026-11-05 00:37 UTC, the parts that are about the lab as a whole: the 9:09 clip, the service
lines, the powder jars, HF, the OpenFlexures, Modula's taller bays; and in the comment that started this run (15:29 UTC),
"renders of the entire setup might be a bit resource intensive, so keep an eye out for that". The set-up movie and the
tray plan carry every round-8 model.

## The 9:09 clip: the whole lab, not three trays

> "In 9:09, suddenly the VLM only has a few things on board"

9:09 in the long-form was round 2's `animate.py workflow` (`vlm_workflow`, "atomized powder dosed for the CubXL"). It
built its own scene: one Shuttle, trays A-C, nothing on the floor. Every scene before it in the long-form had already
shown two Shuttles with every tray loaded.

- **`animate.lab_scene()`** builds the lab as the set-up movie leaves it (`setup_lab.build`): two Shuttles, all 15
  trays (A-O) loaded with their UPSs, dock plates and camera posts, the floor machines, the utilities, both bay
  cameras, one MiR250 + UR10e docked at Shuttle 1's opening (`warehouse.dock_pose("vlm")`) and the other on its
  charger. The cladding is see-through. Tray A's static CubXL is hidden, so `cubxl_rig.CubRig` can draw the same model
  with its head moving.
- **The clip opens and closes on the whole lab** (`CAM_LAB`) and passes through both Shuttles (`CAM_LAB_VLM`) on the
  way in. The close-ups at Shuttle 1's opening are round 7's.
- **Arm collisions:** 0 of 496 frames at 6 fps (`ARM_AUDIT=1`, FCL on the drawn meshes: the arm against itself, its
  MiR and everything visible in the lab), `out/collisions/vlm_workflow.json`.
- Round 2's single Shuttle is still there as `python3 animate.py workflow_r2` (writes `vlm_workflow_r2`).

- **Rendered at 6 fps:** 586 frames, 97.7 s, `out/mp4/vlm_workflow.mp4` (7.2 MB). `out/vlm_workflow.gif` is 4.6 MB
  at 560 px and 5 fps; at the scenes' usual 720 px it came out at 8.4 MB. Round 7's two detail stills
  (`vlm_workflow_dose.png`, `vlm_workflow_vial.png`) were not re-made.

## The service lines, quieter

> "The rapid flowing of vibrant colors showing the connections/piping (e.g., liquid, gas) is a bit over the top."

- Each medium's colour is mixed 45 % towards a mid grey (`services.muted`; `services.MEDIA_VIVID` keeps round 4's).
  The lines read as a quiet tint that still tells mains, Ethernet, air, N2 and chilled water apart.
- The flow markers creep at 40 mm/s, one every 220 mm, 9 mm across, a little darker than their line and without a
  glow. Round 4's beads ran at 160 mm/s, 45 mm apart, 13 mm across, in a light pastel with a glow.
- `vlm_hookups`, `vlm_services` and `vlm_cabling` were re-rendered with them at 6 fps (bb710d2), each GIF under
  4.9 MB.

## The powder-jar store, trays N and O

> "We're going to need a ton of powder jars btw. Easily hundreds, including of different sizes."

`r8_store.py`: 581 labelled jars on two new short trays in Shuttle 2, each jar in a pocket of a white rack, picked
from above by the 2F-85. `python3 r8_store.py json` writes every seat, its size, what is in it and whether the UR10e
reaches it (`out/powder_store.json`).

| Tray | Slot | What | Jars | Sizes |
|---|---|---|---|---|
| N | 2F0 (front, low, 475 mm) | feedstock: DAL #146's elements and master alloys (Al, Si, Mg, Cu, Mn, Cr, Zr, Ti, Fe, Ni, Ce, Sc, Al-Li, Er, Zn, Sn, Al-Sc, Al-Zr), lids coloured by element | 204 | 60, 125, 250, 500 mL |
| O | 2R5 (rear, 500 mm) | atomized lots: each run's six-character ID (DAL #157: jz31op, 8rthq2, c3k0n5, ...) and its five sieve fractions (< 63 to > 250 um, as chapter 3's turntable splits them) | 377 | 30, 60, 125 mL |

The jar sizes are typical wide-mouth straight-sided jars, not a supplier's drawing (estimates). No jar is wider than
76 mm, inside the 2F-85's 85 mm stroke, and the rows leave room for its fingers.

### Round 11: full-width racks, no cameras, short slots

Sterling (PR #318, 2026-11-13, at 2:14 of the round-10 long-form): "you show cameras by the jars and possibly a UPS at
the back. That is very inefficient from a vertical space usage, since the jars are so short. Do we actual need cameras
on the jars at all times? In terms of inventory, we're going to get that with the overhead camera in the bay anyway."

**No, the jars need no cameras.** In its slot a jar tray is in the dark and nothing on it can change; it changes only at
the opening, where the bay's overhead unit looks down on it (its Wide sees 94% of a presented tray's floor) and the
arm's D405 looks at every seat it picks from. The inventory is the seat map (`out/powder_store.json`) checked against
the bay unit's picture each time the tray is presented. With the cameras gone, nothing on the tray draws power, so
the UPS, the dock plate and the tray lines go too: N and O are passive trays (`r8_store.PASSIVE_TRAYS`), as is J
(notes/tray_plan.md, "Round 11").

| Tray | Slot | Rack | Jars | Reach from the MiR at the opening's middle | ... from one of -600, 0, +600 mm |
|---|---|---|---|---|---|
| N, feedstock | 2F0, 225 mm (was 475) | 2410 x 800 mm (was 1760 x 760) | 264 (was 204): 82 x 60, 70 x 125, 58 x 250, 54 x 500 mL | 238 | all 264 |
| O, atomized lots | 2F0b, 150 mm (was 2R5, 500) | 2410 x 800 mm | 489 (was 377): 255 x 30, 164 x 60, 70 x 125 mL | 441 | all 489 |

753 jars in 375 mm of column, where round 10 had 581 in 975 mm. Both trays sit under Shuttle 2's access table, N at
300 mm and O over it at 525.

**The rack's width.** 2410 mm of the 2426 inside the rim, 8 mm spare at each end. Each end keeps 76 mm for its handle
(60 mm wide, 10-70 mm in from the end) and 6 mm between the handle and the last jar. Until round 10 a band with an odd
number of rows had its handles in line with its middle row, inside the end jars of that row; that clash was inside the
one model, so `fit` couldn't see it. The handles now stand clear of every jar.

**The rows were too close for the gripper.** Round 8 spaced rows by the jar's diameter plus 20 mm ("6 mm clear of it,
12 mm of finger, 2 mm spare") and checked only the arm's inverse kinematics. Round 11's `gripper_check()` places the
2F-85's own meshes (ur_arm, with the D405 on its wrist) open around a cap, its pads 6 mm off it (3.5 mm on a 500 mL jar,
where the gripper is fully open at 85 mm), fingers closing front to back, and checks them with FCL against the rack and
its handles, the jars near it and the tray's rim. With the 20 mm rows the fingers ran into the next row for every size
but the 30 mL jars. The reason: the 2F-85's fingertips flare as it opens. At the cap's height they reach 11 mm past the
pads around a 30 mL cap and 18 mm around a 500 mL one, and above the cap the linkage is wider still (45-62 mm from the
axis), which matters where the next row is a taller size. The rows are now spaced from those profiles with 3 mm to
spare (`r8_store.ROW_PITCH`, centre to centre: 61.5 mm for 30 mL rows up to 103 mm for 500 mL ones, and 72.5-116.5 mm
where two sizes meet), 21-41 mm between caps. The check covers both ends and the middle of every row, with the wrist
camera on either side. All clear: the closest is 1.4 mm to a neighbouring jar, 29 mm to a handle and 35 mm to the tray's
rim. The racks are 800 mm deep to fit the wider rows. This is the gripper alone, at the bottom of a straight-down
approach; the arm's links stay well above the jars there. The planned moves in a clip would still need the arm audit.

What is still assumed: the jar sizes (typical wide-mouth jars, not a supplier's drawing), the 6 mm pre-grasp
clearance (it depends on how well the D405 places each seat), and 2410 x 800 mm HDPE racks one person lifts out by
their handles. The heaviest, N's 500 mL band of 54 jars, would be about 45 kg full (up to 500 g of powder, DAL #146's
largest lot, and about 300 g of glass a jar: estimates), so it takes two people or the lift table, not one.

## No HF

> "I don't want to deal with HF in these workflows, especially not with robotics."

Round 7's ducted hood etched a polished Al coupon in Keller's reagent, which contains HF. `r8_store.fumehood()` swaps
it for **Weck's reagent** (4 g KMnO4 and 1 g NaOH in 100 mL water), an HF-free tint etch for Al alloys
(metallographic.com's page on Weck's reagent, as `r8_store.py` cites it; Springer's two-step colour etch,
[doi:10.1007/s13632-012-0033-9](https://doi.org/10.1007/s13632-012-0033-9)). ICP-MS goes out to the
[BYU Spectroscopic Facility](https://labs.chem.byu.edu/byu-spectroscopic-facility/atomic-analysis)'s Agilent 8900
(DAL's FLAIME proposal), which does its own digestion, so nothing in the lab uses HF. The tray hood drops round 7's
"acids with HF" line. Both hood clips were re-rendered (f06692d).

## The OpenFlexure array, dropped

> "I'm now not entirely sure what to use the OpenFlexures for, especially if we already have a VHX."

The six-OpenFlexure sub-tray leaves tray D (`setup_lab._items`). The Keyence VHX on tray K does the imaging. Tray D
now carries the SEM, the MiniFlex and the powder stream's prep station for XRD holders, SEM stubs and XRF cups
(`r8_powder.pxrd_prep`).

## Modula's taller bays

Sterling found the larger bay in Modula's brochure (PR #318, 2026-11-04 18:41): Modula Lift Bay S, M and XL take
695, 895 and 1,295 mm of product height. `kardex_tall.py json` (`out/tall_opening.json`, figure
`out/tall_opening_bays.png`, 77e39f8) checks the round-5 list of machines against five heights:

| Height | What it is | Fits |
|---|---|---|
| 695 mm | Modula Lift Bay S, the bay the Apr 2 Modula quote is priced with | none of them |
| 727.5 mm | Kardex's published product height | none of them |
| 856.5 mm | our estimate for the used XP 500's 996 mm opening (what the lab is drawn with) | InssTek MX-Lab, Mastrex MX100, an open Form 4 |
| 895 mm | Modula Lift Bay M | those, the Lasefinity Fusion X and the Parker Balston N2 generator |
| 1,295 mm | Modula Lift Bay XL | those, the Sharebot MetalONE, the Kings 3D DiMetal-100 and the MX-Lab's base cabinet |

Modula's trays (MC50D/MC75D/MC1000D, 2,500 x 857 mm) are rated 500, 750 and 990 kg. Only the HIP and the Aconity
MIDI are over all of them. The trays themselves are still fitted to Kardex's 2450 x 864 mm tray; re-fitting them to
Modula's, and a requote with Bay M or XL, are open.

## The tray plan and the floor (`setup_lab.py fit`)

The last run, at 18:40 UTC, took in every round-8 placement committed by then:

- **All 15 trays (A-O) fit their slots.** Everything is inside the rim and under the 856.5 mm product height, with no
  overlaps in the meshes (FCL wherever two boxes overlap).
- **All 13 MiR250 docks are clear.** Each has a way in and a pivot spot, and nothing stands in the aisle.
- **Round 6's camera clashes are gone.** Tray cameras D0, E0 and F1 no longer touch their instruments.

The outputs are `out/tray_plan.png`, `out/tray_plan_floor.png` and `out/tray_plan.json`. The JSON's `r8` key lists
every merged placement, the one move, and the machines with no dock. The slot table is in notes/tray_plan.md.

What changed in `setup_lab.merge_r8`, which takes each round-8 module's `TRAY_PLACEMENT`, `FLOOR_PLACEMENT` and
`NEW_TRAYS`:

- **The scale-up machines stand where `r8_scale` put them.** Their placements carry a setback (EOS M 400-4: 3525 mm,
  Meltio cell: 2747 mm back from the south row's fronts), which the merge ignored, so both landed in the south row.
  The Meltio cell then sat on the wire EDM's pivot spot, and the first fit of this run failed both docks ("no pivot
  spot within 4 m"). The merge now sets `warehouse.SETBACK` from them, and both stand south of the south row's ends,
  fronts to the north.
- **No MiR dock for them** (`setup_lab.NO_DOCK`): no dock tape, no target post, not in the dock check. notes/scaleup.md:
  "Neither has a MiR dock: the powder comes by the 100 kg in EOS's containers, and a propeller by forklift or crane."
- **Tray F, a clash between two streams:** the tensile stream's quench tank (x 860, y -150) stood inside the prep
  stream's disc magazine (x 1022, y -190). The magazine keeps its place in front of the UPS. The tank moves left and
  back (`setup_lab.R8_MOVES`, x 680, y -50): between the furnace's right side (25 mm) and the magazine (44 mm), 40 mm
  behind camera F1's post, out of the furnace door's swing, which opens to the front on its right-hand hinges. Chapters
  5 and 6 build on `setup_lab.build` and take the tank's rig from there, so they follow.
- **Labels:** a model called only "our design" (the powder-prep station) is labelled by its name.

## The set-up movie

`setup_lab.py` was re-rendered at 6 fps between 19:02 and 19:28 UTC: 696 frames, 116 s, `out/mp4/setup_lab.mp4`
(12.0 MB). At warehouse.py's GIF settings (640 px, 5 fps) its GIF came out at 9.1 MB, so `out/setup_lab.gif` is
made from the MP4 at 480 px and 4 fps: 4.8 MB.

What is new against round 7's render:

- **15 trays, A-O.**
  - The powder-jar store is on N and O.
  - Tray D has lost the OpenFlexure array and gained the powder-prep station.
  - Tray F has the MX400, the disc magazine and the quench tank.
  - Every instrument is drawn as the round-8 modules had it at 19:02 (`tour.load`: a later module's model replaces an
    earlier one's).
- **A step for the scale-up machines.** The EOS M 400-4 and the Meltio cell come in from outside, beyond the south
  row's ends. The floor view cut both off at the frame's edges, so the step is framed from the far south-east
  (`setup_lab.CAM_SCALE`, picked from a test of five views).
- **The camera posts on trays A and B.** Round 7's render drew two old posts inside the CubXL and the doser; it was
  made minutes before the fix. This one draws them where fit checks them.
- **The arm planner is off for this render (`ARM_NO_PLAN=1`).** The movie's only arm moves are the unit's stretch and
  park at its charger. The planner had already left both as straight joint lines (the preview's log shows no
  re-planned move), and round 6's audit of the set-up found 0 of 1376 frames in collision. Without the planner, the
  render needs no collision world (see Memory below).

### Round 11's set-up render

`ARM_NO_PLAN=1 VIZ3D_FPS=6 setup_lab.py` (as round 8 rendered it), through `runner_guard.py --mem 6500`, 00:34-00:53
UTC on 2026-11-14: 708 frames, 118.0 s, 12.0 MB; the GIF from the MP4 at 448 px, 4 fps, `--lossy=120`: 6.8 MB.

- **Trays J, N and O come in bare** (7/9): their loads only, no UPS, no camera posts, and their captions say so with
  their slot heights (325, 225 and 150 mm). N's 264 and O's 489 jars fill the tray from side to side. In O's shot, N
  shows in its slot under the access table.
- **The bay cameras** (8/9, 102-107 s; Sterling: "Can't see the overhead camera from the angle. Should change the view
  angle and temporarily make things opaque again"): Shuttle 2's unit, then Shuttle 1's, each from an operator's eyes
  at the opening (1.6 m up, 0.9 m out, 420 mm to one side, a 34° view), the cladding, bay walls and shutter solid while
  it is shown, each unit labelled; then the wide view, see-through again. 5.2 s, against 3.2 s for round 10's one wide
  shot.
- It started before the orchestrator's 063b014 (tray supports drawn only where a tray rests), so a second render
  followed: 01:17-01:36 UTC at 80c752c, 708 frames, 118.0 s, 11.8 MB, the GIF at 400 px and 3 fps (4.6 MB, under the
  4.9 MB asked for). It has 063b014's supports, the iMicro's lid-only hood (180c0f4) and chapter 5's specimen-finger
  stand on the MiR (dd81998). Not yet in it: camera E1 behind the Mastersizer, the Instron's dock on its load axis and
  its junction box over the frame (47219fc, 01:49).

## Memory: the whole lab is about 5-6 GB a process

Sterling: "renders of the entire setup might be a bit resource intensive". They are. Peak resident memory of the one
Python process, on a runner with 16 GB:

| Job | Peak |
|---|---|
| `animate.py workflow`, `PREVIEW=1`, with the arm planner | 5.85 GB |
| the same, `ARM_AUDIT=1` | 4.7 GB |
| the same, full render at 6 fps | 5.9 GB |
| `setup_lab.py`, `PREVIEW=1`, with the planner | 5.5 GB |
| the same, `PREVIEW=1 ARM_NO_PLAN=1` | 2.9 GB |
| the same, full render with `ARM_NO_PLAN=1` | 3.5 GB |

**The first workflow render was stopped by the watchdog** at 17:09 UTC. It had reached 5.7 GB while a set-up preview
(4.8 GB) and a chapter-6 preview (3.4 GB) ran beside it, and free memory was down to 868 MB. Re-run with its memory
reserved (`runner_guard.py --mem 6500`), it finished.

**Where the memory goes.** A probe built the set-up scene once and measured after each stage:

| Stage | Memory |
|---|---|
| imports | 0.5 GB |
| `lab.meshes()` | 0.5 GB |
| `load_all()`, 42 models from the caches | 0.9 GB |
| `setup_lab.build`: 2441 actors, 3.75 M points, 4.71 M triangles | 1.5 GB |
| four rendered frames | 2.0 GB |
| `collide.World` over the whole lab: 2439 FCL bodies, built in 50 s | 4.5 GB |

So about half of a whole-floor job is the arm planner's collision world. It holds one BVH for every mesh actor in the
scene, and most of them are nowhere near the arm.

- **Does memory climb during a render?** Yes, but with the lab, not from held frames. `setup_lab.build` makes its
  Scene with `gif=False`, and the GIF is made from the MP4 afterwards. Sampled every 30 s, the set-up render rose
  from 1.1 GB, through 2.75 GB at mid-movie, to a 3.48 GB peak, and ended at 3.0 GB. It rises as the lab fills up:
  each tray, instrument and machine that becomes visible is drawn, and Mesa's software renderer keeps its vertex
  buffers in RAM. That is the lab's size, not a leak.
- **What would cut it further.** The collision world could build each BVH only when an arm part's box first overlaps
  that mesh's box. `collide.Body.ensure` already does this for re-meshed actors, so the far trays and machines would
  never get one. The coordinator's `VLAB_ONLY_TRAYS` gets the chapters there another way: it leaves empty the trays
  a chapter doesn't present, which takes a scene from about 5 GB to about 1.5 GB. I didn't make the lazy-BVH change:
  collide.py is shared, and every chapter's audit was running on it.

## Physical sense

- **The 9:09 clip.** The vial goes from the rack to the doser's cup, then to the holder on the MiR's cabinet while
  the trays swap, then into the CubXL's holder. It is never let go in the air, and the audit found no frame with the
  arm, the gripper or the vial inside anything. The CubXL's P20 takes 20 uL at a time.
- **The set-up movie.**
  - People load the trays and are not drawn: instruments slide in through the opening, and floor machines slide
    along the floor onto their taped footprints, as in round 7.
  - The scale-up machines now come in from outside, south of the south row. Before, they would have slid in through
    the row's machines.
  - In the time-lapse, each tray after the first in a Shuttle cuts to the opening instead of travelling there. The
    caption says so.

## Open

- **The trays are still Kardex's.** They are fitted to Kardex's 2450 x 864 mm tray, not Modula's 2,500 x 857 mm, and
  there is no requote with Bay M or XL.
- **The lazy collision world** (above).
- **The warehouse clip** still uses round 4's one-Shuttle layout and carries a vial. It stays out of the long-form.
- **The services clips** (`vlm_hookups`, `vlm_services`, `vlm_cabling`, `bay_camera`) follow one tray each and were
  not re-rendered with the round-8 trays.
- **Two stills are round 7's:** `vlm_workflow_dose.png` and `vlm_workflow_vial.png`.

## Round 9, the jars stream (PR #318, Sterling's points 4 and 8 of 2026-11-05)

### What changed

- **Every jar in the store, the storage load and the packaging station is the lab-wide jar** (`props.jar_parts`): clear
  glass, a matte black cap, a white label, the powder showing. The lid colours by element and alloy, the amber glass of
  the lots and the milky HDPE of the packaging jar are gone. `r8_store.py`, `instruments_r7.storage` and
  `instruments_lab.packaging` changed; `props.py` is as round 9's first run left it.
- **A tint says what is special, then fades back.** Each of three clips has a `jar tint` piece (`Joint("fade")`, `props.tint_sleeve`
  sleeves, `props.piece_legend` for the legend). The clip tints for 1.6 s, holds for about 2.4 s, then fades for 1.8 s:
  - tray N (feedstock): amber for the Al master alloys (Al-Li, Al-Sc, Al-Zr), teal for Al and Si (Al 4047's elements);
  - tray O (lots): amber for the < 63 um LPBF cut, teal for the other cuts of run jz31op;
  - tray J's storage: one tint per powder in its eight sealed jars (Al 4047, Cu, Al-Ce, Ni-Al bronze: placeholders, estimates).
- The packaging station has nothing to point out, so its jars are just clear glass with a black cap. Its 61 x 131 mm size is
  still the Nalgene 2104-0008's: only the material changed (the lab's actual jar is an estimate, see below).
- `setup_lab` and the time-lapse build with these changes (import check; not re-rendered). Still: `out/jars_r9_still.png`.

### Which containers for powder: is glass OK?

**Short answer.** Glass is fine for what the lab holds now: small sealed lots of coarse (150-300 um) powder in a
dehumidified room, handled by a gripper at modest force. It is not what the standards or the powder makers prefer for
aluminium: NFPA 484 and the Aluminum Association want *conductive, grounded* containers, and glass cannot be grounded.
So keep glass for the bench-scale jars, ground what touches them (conductive racks, a grounded dosing path, no dry
pouring of fines), and put Mg, Li master alloys and anything under about 63 um in sealed metal cans or the glovebox.

**Why, by criterion.**

| | Glass (borosilicate or soda-lime, PTFE-lined cap) | HDPE / PP | Metal can (Al or steel, gasketed) |
|---|---|---|---|
| Static and dust ignition | insulating, cannot be bonded; a charged jar can discharge into fine Al or Mg | insulating, worst for charge build-up | conductive, can be bonded to ground: what NFPA 484 and TR-2 ask for |
| Moisture and O2 | best barrier (with a PTFE or foil liner) | permeable to water vapour and O2 over weeks; DAL #146's advice: not for long-term unless over-bagged | good with a gasket; over-bag for argon |
| Robot handling | breaks if dropped or squeezed; a UR10e with a 2F-85 can be force-limited, and rack pockets catch a slip | tough, light | tough, but opaque: the powder can't be seen, and a lid needs a tool |
| Visibility | powder level and caking visible, which an automated lab uses | translucent | none |
| Cleaning and contamination | inert, reusable, no extractables | scratches, plasticisers | can dent and shed coating |

- **Standards.** NFPA 484 (combustible metals) and the Aluminum Association's
  [TR-2, storage and handling of aluminum powders and paste](https://www.aluminum.org/sites/default/files/2021-11/Safe_Storage.pdf)
  ask for electrically conductive containers, bonding and grounding when powder is moved, and no plastic for handling
  aluminium powders ([NFPA 484 (2015) preview](https://www.avadocuments.com/preview/nfpa-484-2015.pdf); I read excerpts
  only, and the current edition may differ). Plastic drums don't dissipate charge
  ([Justrite's grounding guide](https://www.justrite.com/media/2019_Justrite-Guide-to-Safe-Grounding-and-Bonding-Practices.pdf)).
- **What makers ship in.** Large lots go in metal: Carpenter Additive sells a reusable stainless hopper to replace plastic
  containers ([Carpenter, transport and storage](https://www.carpenteradditive.com/news-events/metal-powder-transportation-and-storage)),
  and metal-powder packaging patents describe steel drums with earthed filling
  ([US 6,134,863](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6134863)). Small AM lots are sold in
  sealed plastic or metal containers: a reseller lists Carpenter AlSi10Mg as two sealed 5 kg containers of 20-63 um
  ([additiveplus](https://additiveplus.com/product/aluminum-alloy-powder-alsi10mg-lpbf-compatible-5-kg-11-lbs/); a
  third party, not Carpenter's own spec). I found no public packaging detail for AP&C
  ([overview](https://www.advancedpowders.com/sites/default/files/2022-06/AP&C_Overview_Bro_A4_EN_8_v3.pdf): argon
  atomization, no container named), Valimet, ECKART or Kymera: ask them when we order.
- **What the lab does now.** From
  [digital-alloy-lab #155](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/155): until there is a glovebox,
  powders from [#146](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/146) are kept in airtight supplier
  containers; #155's Edison answer advises keeping desiccant outside the powder jar, argon purging and over-bagging,
  and single-run aliquots (a published protocol used 50 g in borosilicate vials: [Grubbs 2022](https://doi.org/10.3390/met12040603)).
  #146's answer says "grounded gasketed metal cans are the best container; borosilicate glass is a fine barrier but can't be
  grounded; HDPE isn't suitable long-term unless overbagged" (an AI-written answer in the thread, not a standard). The
  alloy lab's own SOP (#129) mentions "jars" for test mixtures without naming the material. I found no issue that states
  which jars the lab bought.
- **Moisture** scales with surface area, so the 150-300 um cut asked for in #146 takes up far less than the 15-45 um
  LPBF cut that #159 aims at: fines are where glass-and-desiccant stops being enough.

**Recommendation.**
1. Keep clear glass with a black PTFE-lined cap for the working jars (30-500 mL), as the model now draws them: they let
   the robot and the people see the powder, and the powder is coarse.
2. Ground what touches them: conductive (ESD-safe) racks in place of the white HDPE ones, a grounded dosing path, argon over
   the powder where it is dosed; never pour fines in the open.
3. Fines (< 63 um Al), Mg and the Al-Li master alloy: sealed gasketed metal cans, or glovebox only.
4. Prefer shatter-resistant (polymer-coated) glass and limit the 2F-85's grip force, since a robot drops what a person
   would not.

**Does it change what the model shows?** The jar stays clear glass with a black cap. Two optional follow-ups, not done:
the racks (still drawn in white HDPE, `r8_rack`) could be drawn as conductive racks with a ground strap, and a metal can
could be added for the fines and the Mg. The grip-force limit is for whoever sets up the 2F-85.

### Open

- The jar sizes are typical wide-mouth jars, estimates. The storage tint's powder names are placeholders.
