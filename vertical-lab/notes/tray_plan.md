# The tray plan: which tray goes in which slot, and why (#303, PR #318 rounds 7, 8 and 11)

`vlm.COLUMNS` holds the plan, `setup_lab.TRAYS`/`ITEMS`/`CAMS` what is on each tray, and
`xvfb-run --server-num=60 python3 setup_lab.py fit` checks it. The check writes `out/tray_plan.json`, draws
`out/tray_plan.png` (every tray from above, and both Shuttles' columns) and `out/tray_plan_floor.png` (the floor
plan for MiR250 docking).

## How tall each slot is

With the 996 mm opening (`vlm.OPEN_H`), the goods may be about 856.5 mm tall over the tray floor. That figure is an
estimate (`vlm.MAX_GOODS_H`, notes/kardex_opening.md). But a slot only needs to be as tall as its own tray:

- the tray floor (3 mm, `vlm.T_FLOOR`);
- the tallest thing on the tray, measured from the meshes as drawn. That may be an instrument, the UPS (437 mm,
  so no tray that has one is shorter than 475 mm) or a camera head (up to about 706 mm on a standard post). Since
  round 11 the three storage trays (J, N, O) have no UPS and no cameras, so their own load sets their height;
- Kardex's 20 mm of clearance above it (POF order sheet);
- rounded up to the 25 mm pitch.

So a short tray, such as the storage tray, takes a short slot, and a tall one, such as the glovebox, takes a tall one.

Where the slots can be:

- **Rear column:** from 300 mm, the lowest position the extractor reaches (its carriages hang 160 mm under a tray,
  over a 140 mm base frame), up to the drive bay at 3690 mm.
- **Front column, upper part:** from 1950 mm, 120 mm over the header (1829 mm) rounded up to the pitch, to 3690 mm.
- **Front column, lower part:** from 300 mm to 793 mm, under the access table. It takes short trays: tray J in
  Shuttle 1, trays N and O in Shuttle 2 (round 11). vlm.py drew column walls there all along, but nothing was stored
  there before round 7.

The whole unit stays at 3950 mm, under #53's 13 ft (3962 mm).

**The supports between slots: a question for Kardex.** Kardex's columns carry tray-support profiles every 25 mm, so any
slot height can be set. Our slots are fixed, and a tray's rim, its dock plate and its tray lines stand over the 20 mm
the profiles reach in, so on a real Shuttle the profiles above a tray's own rest profile would be in its way. Since
round 11 (063b014, `vlm.support_parts`) the model draws a support only where a tray rests, per Shuttle, and leaves the
others out. Whether Kardex can supply columns with the profiles fitted only at our slot heights, or profiles that clear
a plate and lines on the tray's right, is to be asked.

## The plan

Fourteen trays don't fit one Shuttle (fifteen since round 8). A second one, the same size, stands beside the first: x = 3630 mm, 800 mm of
floor between the claddings (`vlm.SHUTTLE_X`). The 800 mm gap is there so a MiR250 can turn on the spot between the
two units (see the floor plan below).

| Shuttle | Slot | Tray bottom (mm) | Span (mm) | Tray | What is on it | Tallest (mm) |
|---|---|---|---|---|---|---|
| 1 | R1 | 300 | 750 | D | Hitachi TM4000PlusII SEM, Rigaku MiniFlex XRD, powder prep station (round 8; the OpenFlexure array is gone) | 722 (XRD) |
| 1 | R2 | 1050 | 750 | A | CubXL corrosion set-up, Opentrons OT-2 | 702 (camera head) |
| 1 | R3 | 1800 | 900 | B | vial rack, multi-doser v5 (chain carousel on an HR-202i, 13 powders), Specac Autotouch vacuum press | 854 (multi-doser) |
| 1 | R4 | 2700 | 725 | E | Plastometrex PLX-Benchtop, KLA iMicro, Malvern Mastersizer 3000 + Aero S | 700 (camera E1's head, behind the Mastersizer since round 11) |
| 1 | F0 | 300 | 325 | J | sample storage, passive: cups and plugs (Al, Cu), vials, tubes, stubs, coupons, bars, jars | 300 (drawer cabinet) |
| 1 | F1 | 1950 | 725 | C | Bambu Lab H2D, Bambu Lab A1 mini | 692 (camera head) |
| 1 | F2 | 2675 | 750 | F | LECO PX500 polisher, Nabertherm NAT 15/65 furnace, LECO MX400 mounting press, disc magazine, quench tank | 703 (camera F1's head) |
| 2 | 2R1 | 300 | 850 | K | tray glovebox (N2, purge-only), Keyence VHX-7000 | 810 (glovebox) |
| 2 | 2R2 | 1150 | 725 | L | ZwickRoell zwickiLine Z5.0 lying on its side, Mitutoyo HM-220 micro-Vickers | 693 (camera head) |
| 2 | 2R3 | 1875 | 750 | M | Bruker S2 PUMA XRF, Sentry Air ductless hood, Makera Carvera CNC | 714 (hood) |
| 2 | 2R4 | 2625 | 550 | H | DDM Novastar stencil printer, Opulo LumenPnP, Puhui T-962A reflow oven | 516 (stencil printer) |
| 2 | 2F0 | 300 | 225 | N | powder-jar store, feedstock, passive: 264 jars (round 11) | 182 (500 mL jars) |
| 2 | 2F0b | 525 | 150 | O | powder-jar store, atomized lots, passive: 489 jars (round 11) | 104 (125 mL jars) |
| 2 | 2F1 | 1950 | 725 | G | two Formlabs Form 4s, Form Wash, Form Cure | 696 (camera head) |
| 2 | 2F2 | 2675 | 725 | I | two SnowX SnowPods | 686 (camera head) |

The table is from round 11's runs of `setup_lab.py fit` (00:20 and 01:48 UTC, 2026-11-14); `out/tray_plan.json` has the run
that matches the code. Every camera-carrying tray needs 725-750 mm, because a camera head on a standard post reaches
690-706 mm. Tray H has short posts (block at 270 mm) so its slot stays low.

What is left (round 11; `out/tray_plan.png` draws it dashed): Shuttle 1 has 265 mm at the top of its rear column, 265
at the top of its front and 168 under the access table. Shuttle 2 has 515 mm at the top of its rear column (one more
tray of up to 500 mm, with a UPS if it needs one), 290 at the top of its front and 118 under the access table. In all,
1621 mm of column is free, against 896 mm before round 11.

## Round 8

`setup_lab.merge_r8` takes each round-8 module's `TRAY_PLACEMENT`, `FLOOR_PLACEMENT`, `NEW_TRAYS` and `NEW_SLOTS`
into the plan, and `fit` checks the result (18:40 UTC run: all 15 trays and all 13 docks clear). notes/lab_r8.md has
the details.

- **Two new short trays in Shuttle 2** (`r8_store`): N in 2F0, the front column's low slot under the access table
  (475 mm), and O in 2R5, the rear column's last 500 mm (the room round 7 left). Each carries a powder-jar store and
  its UPS, dock plate and two short camera posts.
- **Tray D:** the OpenFlexure array is gone; the powder stream's prep station (XRD holders, SEM stubs, XRF cups;
  `r8_powder.pxrd_prep`) stands at the front right, 147 mm tall.
- **Tray F:** the MX400 mounting press at the back left and the disc magazine at the front right (`r8_prep`), the
  quench tank with its lift basket (`r8_test`). The tank's own placement (x 860, y -150) stood inside the magazine,
  so the plan moves it to x 680, y -50 (`setup_lab.R8_MOVES`): 25 mm from the furnace, 44 mm from the magazine, 21 mm
  behind camera F1's post, out of the furnace door's swing.
- **On the floor:** the EOS M 400-4 and the Meltio robot cell (`r8_scale`) stand south of the south row's ends, set
  back 3525 and 2747 mm (their `setback`, which the merge now applies), with no MiR dock or target (`NO_DOCK`).
- **Round 6's camera clashes** (D0, E0 and F1 touching their instruments' boxes) are gone: every camera rig is clear.

## Round 11: the storage trays are passive

Sterling (PR #318, 2026-11-13, on the round-10 long-form at 2:14): "you show cameras by the jars and possibly a UPS at
the back. That is very inefficient from a vertical space usage, since the jars are so short. Do we actual need cameras
on the jars at all times? In terms of inventory, we're going to get that with the overhead camera in the bay anyway."

**Do we need cameras on the jars? No.** Nothing on a storage tray moves, heats, runs or draws power. In its slot the
tray sits in the dark inside the Shuttle and nothing on it can change; it changes only at the opening, where the arm
takes or puts back a jar or a sample. There the bay's overhead unit looks down on it (its Wide sees 94% of a presented
tray's floor, `services.json` `cameras.bay_view`; what it misses is at the back corners, nearest the unit) and the D405
on the arm's wrist looks at every seat the arm picks from. A stream camera on the tray would film a closed slot. So
the seat map (`out/powder_store.json`, `instruments_r7.storage_seats()`) plus a picture from the bay unit at every
presentation is the inventory, and the UPS that kept the cameras alive in transit goes with them. This holds for J too.

**What changed** (`setup_lab.PASSIVE`, `r8_store.PASSIVE_TRAYS`):

- J, N and O carry no UPS, no dock plate or tray lines, no socket, power strip or power lamp, and no stream cameras.
  Their slots mate with nothing, so they get no dock either: a real build leaves out three CombiTac docks. Nothing had
  to be removed from the scenes for that: services.py's clips draw docks only at trays A-F's slots and the bay, and the
  set-up movie never drew slot docks. The service risers stay. Each runs its column's whole height and feeds the
  powered trays' docks in it: C's and F's over J in Shuttle 1's front column, G's and I's over N and O in Shuttle 2's.
- `setup_lab.CAMS` loses tray J's two short posts; a new tray from a module gets them (`SHORT_CAMS`) only if it isn't
  passive.
- N's and O's racks run the tray's full width, 2410 mm of the 2426 inside the rim (they were 1760, left of the UPS),
  and 800 mm deep (was 760: a passive tray has no power strip along its back). Their rows are spaced for the gripper:
  see notes/lab_r8.md. Tray J's storage load stays 1760 mm wide, centred: its racks are laid out by hand around its
  drawer cabinet, and the 333 mm left at each end is room for more.
- Each slot is its own load's height: the tray floor, the tallest thing on the tray, Kardex's 20 mm, up to the 25 mm
  pitch.

| Tray | Before: slot, span, tallest | After: slot, span, tallest | Jars |
|---|---|---|---|
| J, sample storage | F0, 475 mm, 437 (the UPS) | F0, 325 mm, 300 (drawer cabinet) | 8 (and its cups, vials, tubes) |
| N, feedstock | 2F0, 475 mm, 437 (the UPS) | 2F0, 225 mm, 182 (500 mL jars on their rack) | 204 -> 264 |
| O, atomized lots | 2R5 (top of Shuttle 2's rear column), 500 mm, 437 (the UPS) | 2F0b (under Shuttle 2's access table, over N), 150 mm, 104 (125 mL jars) | 377 -> 489 |

The three slots took 1450 mm of column; they take 700 now, and 750 mm is free. Both jar trays now sit under Shuttle 2's
access table (300-675 mm), so 2R5 is gone and Shuttle 2's rear column has 515 mm free at its top. 753 jars, against
581, in 375 mm of column against 975.

**Tray F's slot grows 725 -> 750 mm.** The ch5 stream moved camera F1 behind the quench tank, looking down into it
(commit 6c690a0, Sterling's point 4 of 2026-11-13); its head now stands 703 mm over the tray floor, and 703 + 3 + 20
rounds up to 750. F2 is the top slot of Shuttle 1's front column, so nothing else moves.

## What moved in round 7, and why

- **Tray B gets the vacuum press.** The Specac Atlas Autotouch 15T is loaded onto tray B in the set-up movie, at
  `alloy_press.PRESS_AT`, where the alloy route uses it. It is stored with its guard down (640 mm). The multi-doser is
  731 mm tall, so tray B's slot is 775 mm.
- **The sieve shaker leaves tray F.** The alloy route sieves in the sieving cell on the bench between the rePowder and
  the VLM (`sieve_station.py`, `alloy_print.BENCH`). The set-up movie now builds that cell on the floor.
- **The XRF leaves tray F.** Tray F had four instruments, and the UPS took the back right corner. The Bruker S2 PUMA
  went to tray M.
- **The Keyence VHX leaves tray C.** As modelled it is 624 mm deep. In front of the dock plate and the UPS there are
  595 mm, and the rest of tray C is the two printers and the camera posts. So it went to tray K, beside the tray
  glovebox, in front of the UPS.
- **Tray L:** the micro-Vickers at the left, and the zwickiLine (on its side, 638 mm deep) in front of the UPS.
  The HM-220 is 767 mm deep as modelled, too deep to stand there.
- **Small moves** (`line.TRAY_LOADS`, `animate.LOADS`, `fab_trays.LOADS`): the Mastersizer 60 mm forward, clear of
  the UPS and the tray's lines; the OT-2 10 mm forward of the lines; the LumenPnP 70 mm forward of the UPS.
- **New trays:** J (storage), K (glovebox), L (sideways tensile and hardness), M (XRF, ductless hood and CNC). Their
  models are `instruments_r7.py`'s, placed from the meshes, which run larger than `FOOTPRINTS` in places: the
  glovebox is 826 mm deep and 813 mm tall, the hood 1030 mm wide and 717 mm tall. If a model isn't built,
  `setup_lab.load_all` stands in a box of its `FOOTPRINTS` size, and the item's name says "stand-in box".
- **Considered and not moved onto a tray:**
  - The InssTek MX-Lab (835 mm without its base cabinet) would pass a 996 mm opening. It stays on the floor. It needs
    argon, and the tray coupling carries N2. It needs an exhaust and its base cabinet, whose contents aren't published.
    Its 250 kg on 0.47 m2 is 2.3 times a strong tray's rating per area (kardex_tall.py).
  - A Form 4 with its cover open (844 mm) now fits under the opening. It opens only there, so tray G's slot is set by
    the closed printer.

## Every tray with instruments carries its UPS, dock plate and cameras

The storage trays J, N and O don't (round 11, above).


`fit` measures each of these from its meshes, as an axis-aligned box in the tray's frame:

- every instrument;
- the UPS (`services.UPS_AT`);
- the dock plate with its bracket and the tray's lines (`services.PLATE_*`);
- each camera rig, in two parts: the post on its foot, and the yoke and head.

Where two boxes overlap, FCL checks the meshes themselves, so a head leaning over an instrument's low corner isn't
counted as a clash. The checks are: no overlaps, everything inside the rim (a camera head may lean over the rim but
not past the tray's edge), the opening's product height, and the slot's span. Trays A-F use `services.TRAY_CAMS`.
G-M use `setup_lab.CAMS`: posts at the back between instruments, looking down at them. The services.py search
(`unit_view`) hasn't placed those yet.

Found and left to services.py, which owns these parts:

- The tray's lines run through the UPS's box (x 939-1060, y 254-326, z 113-128): the lines start at the plate and run
  inwards along the back rim, where the UPS stands.
- `services.TRAY_CAMS` (round 7, front positions):
  - A0's post at (-680, -270) stands inside the CubXL corrosion set-up's frame;
  - B1's post at (685, -340) stands inside the multi-doser's footprint.

  Both clash in the meshes. The search seems to have used older footprints (round 2's CubXL, a smaller doser).

## The floor: MiR250 docking, no rail

`setup_lab.FLOOR_PLAN` is the floor in `warehouse.STATIONS`'s form. `setup_lab.use_floor_plan()` points warehouse.py
at it for the set-up movie and the check. warehouse.py's own `STATIONS` is unchanged: other chapters drive their MiRs
on it.

- **North row** (fronts at y = -1562, facing the aisle): the glovebox, the rePowder, the sieving cell, the two
  Shuttles, the Aconity MIDI (moved from x = 3700 to 6950), and the packaging station (moved across the aisle).
- **South row** (fronts at y = -6238): the 100 kN and the tabletop Instron, the two chargers, the ducted fume hood
  (Labconco XStream, new), the DED (InssTek MX-Lab) and the wire EDM (moved across the aisle).

A MiR250 docks alongside a station, 80 mm off its front, with an AprilTag target on a post beyond one end. A MiR turns
on the spot, sweeping a circle of 494 mm radius, so it can't turn in front of a row. It turns at a gap and drives along
the dock line into the dock. `fit` checks, with 30 mm to spare:

- the docked MiR;
- its way in from the nearest pivot spot at its open end;
- the pivot circle;
- every target post's foot, against every machine's plan rectangle;
- the aisle, against all of them.

As placed, every dock is clear and no machine stands in the aisle.

- **The rePowder sticks out 337 mm past the row's fronts.** It is fixed where `animate.REPOWDER_AT` puts it, and the
  atomize chapter's arm moves depend on that. So its dock is 298 mm further out, at y = -2230, as the alloy route's
  chapters already park there (`alloy_atomize.END_POSE`). Its target post stands 180 mm in front of it. It is entered
  from the west, along y = -2230, which clears the rePowder's front by 41 mm. A MiR docked there reaches 120 mm into
  the aisle's 3.0 m.
- **The 100 kN Instron's dock moved out (round 11).** Chapter 5's MiR stops 500 mm off the row at the 68FM-100, on
  its load axis (x -6187.5), 68 mm clear of the 3119-608 chamber's 550 mm door, which swings 432 mm out in front of
  the frame. The tape was 80 mm off the row and 412 mm west, so `DOCK_Y` and the station's dock x now match the stop
  (y -5448). Its target post stays 150 mm off the face, 650 mm beyond the MiR's front end (`TARGET_AT`). A MiR docked
  there reaches 242 mm into the aisle's 3.0 m. The junction box on the south row's drop there hung at 1720-1900 mm,
  inside the frame's crosshead (1610-1810 at rest), so it now hangs over the frame's top, at 2350-2530 mm.
- **The VLMs' targets stand outside the opening's width** (x = -1330, and 3630 + 1330), so a tray pulled out to the
  front passes them. The first unit backs into its dock from the gap between the Shuttles; the second drives forwards
  into its dock from the same gap.

## Sources

- Kardex Shuttle POF order sheet (StoreMoreStore option 1): 727.5 mm of product height, 20 mm clearance, 25 mm pitch,
  833 mm access table.
- The 996 mm opening: a used XP 500, lagersysteme-paternoster.de Pos. 89 (vlm.py).
- #53: under 13 ft; tray ratings.
- MiR250 Specifications, 2023-06-28: 800 x 580 mm, 3.0 m for two robots passing (warehouse.py).
- Instrument sizes: each model's own source (out/instruments.json, out/fabrication.json, instruments_r7.FOOTPRINTS).
- Everything else here is a layout choice.
