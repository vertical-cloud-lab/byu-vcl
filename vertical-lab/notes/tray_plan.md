# The tray plan: which tray goes in which slot, and why (#303, PR #318 rounds 7 and 8)

`vlm.COLUMNS` holds the plan, `setup_lab.TRAYS`/`ITEMS`/`CAMS` what is on each tray, and
`xvfb-run --server-num=60 python3 setup_lab.py fit` checks it. The check writes `out/tray_plan.json`, draws
`out/tray_plan.png` (every tray from above, and both Shuttles' columns) and `out/tray_plan_floor.png` (the floor
plan for MiR250 docking).

## How tall each slot is

With the 996 mm opening (`vlm.OPEN_H`), the goods may be about 856.5 mm tall over the tray floor. That figure is an
estimate (`vlm.MAX_GOODS_H`, notes/kardex_opening.md). But a slot only needs to be as tall as its own tray:

- the tray floor (3 mm, `vlm.T_FLOOR`);
- the tallest thing on the tray, measured from the meshes as drawn. That may be an instrument, the UPS (437 mm,
  so no tray is shorter than 475 mm) or a camera head (up to about 706 mm on a standard post);
- Kardex's 20 mm of clearance above it (POF order sheet);
- rounded up to the 25 mm pitch.

So a short tray, such as the storage tray, takes a short slot, and a tall one, such as the glovebox, takes a tall one.

Where the slots can be:

- **Rear column:** from 300 mm, the lowest position the extractor reaches (its carriages hang 160 mm under a tray,
  over a 140 mm base frame), up to the drive bay at 3690 mm.
- **Front column, upper part:** from 1950 mm, 120 mm over the header (1829 mm) rounded up to the pitch, to 3690 mm.
- **Front column, lower part:** from 300 mm to 793 mm, under the access table. It takes one short tray. vlm.py drew
  column walls there all along, but nothing was stored there before.

The whole unit stays at 3950 mm, under #53's 13 ft (3962 mm).

## The plan

Fourteen trays don't fit one Shuttle (fifteen since round 8). A second one, the same size, stands beside the first: x = 3630 mm, 800 mm of
floor between the claddings (`vlm.SHUTTLE_X`). The 800 mm gap is there so a MiR250 can turn on the spot between the
two units (see the floor plan below).

| Shuttle | Slot | Tray bottom (mm) | Span (mm) | Tray | What is on it | Tallest (mm) |
|---|---|---|---|---|---|---|
| 1 | R1 | 300 | 750 | D | Hitachi TM4000PlusII SEM, Rigaku MiniFlex XRD, powder prep station (round 8; the OpenFlexure array is gone) | 722 (XRD) |
| 1 | R2 | 1050 | 750 | A | CubXL corrosion set-up, Opentrons OT-2 | 703 (camera head) |
| 1 | R3 | 1800 | 775 | B | vial rack, multi-doser (chain carousel v2), Specac Autotouch vacuum press | 731 (multi-doser) |
| 1 | R4 | 2575 | 725 | E | Plastometrex PIP, KLA iMicro, Malvern Mastersizer 3000 + Aero S | 689 |
| 1 | F0 | 300 | 475 | J | sample storage: cups and plugs (Al, Cu), vials, tubes, stubs, coupons, bars, jars | 437 (UPS) |
| 1 | F1 | 1950 | 725 | C | Bambu Lab H2D, Bambu Lab A1 mini | 692 |
| 1 | F2 | 2675 | 725 | F | LECO PX500 polisher, Nabertherm NAT 15/65 furnace, LECO MX400 mounting press, disc magazine, quench tank (round 8) | 687 |
| 2 | 2R1 | 300 | 850 | K | tray glovebox (N2, purge-only), Keyence VHX-7000 | 810 (glovebox) |
| 2 | 2R2 | 1150 | 725 | L | ZwickRoell zwickiLine Z5.0 lying on its side, Mitutoyo HM-220 micro-Vickers | 693 |
| 2 | 2R3 | 1875 | 750 | M | Bruker S2 PUMA XRF, Sentry Air ductless hood, Makera Carvera CNC | 714 (hood) |
| 2 | 2R4 | 2625 | 550 | H | DDM Novastar stencil printer, Opulo LumenPnP | 516 (stencil printer) |
| 2 | 2F1 | 1950 | 725 | G | two Formlabs Form 4s, Form Wash, Form Cure | 696 |
| 2 | 2F2 | 2675 | 725 | I | two SnowX SnowPods | 686 |
| 2 | 2F0 | 300 | 475 | N | powder-jar store, feedstock: 204 jars (round 8) | 437 (UPS) |
| 2 | 2R5 | 3175 | 500 | O | powder-jar store, atomized lots: 377 jars (round 8) | 437 (UPS) |

The table is from one run of `setup_lab.py fit`; `out/tray_plan.json` has the run that matches the code. Every
camera-carrying tray needs 725-750 mm, because a camera head on a standard post reaches 690-706 mm. Trays H and J
have short posts (block at 270 mm) so their slots stay low.

What is left: Shuttle 1 has 390 mm free at the top of its rear column (3300-3690), too little for a tray with a UPS.
Its front column has 290 mm free. Shuttle 2 had 515 mm free in the rear column (one more short tray, up to a 500 mm
span), 290 mm at the top of the front and its low front slot under the access table. Round 8's two jar trays took the
rear 500 mm (2R5) and the low front slot (2F0), so Shuttle 2 now has 15 mm left in its rear column and 290 mm at the
top of its front.

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

## Every tray carries its UPS, dock plate and cameras

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
