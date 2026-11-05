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
