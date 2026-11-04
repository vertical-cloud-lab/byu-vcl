# The tray plan: which tray goes in which slot, and why (#303, PR #318 round 7)

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

Fourteen trays don't fit one Shuttle. A second one, the same size, stands beside the first: x = 3630 mm, 800 mm of
floor between the claddings (`vlm.SHUTTLE_X`). The 800 mm gap is there so a MiR250 can turn on the spot between the
two units (see the floor plan below).

| Shuttle | Slot | Tray bottom (mm) | Span (mm) | Tray | What is on it | Tallest (mm) |
|---|---|---|---|---|---|---|
| 1 | R1 | 300 | 750 | D | Hitachi TM4000PlusII SEM, Rigaku MiniFlex XRD, OpenFlexure array | 722 (XRD) |
| 1 | R2 | 1050 | 750 | A | CubXL corrosion set-up, Opentrons OT-2 | 703 (camera head) |
| 1 | R3 | 1800 | 775 | B | vial rack, multi-doser (chain carousel v2), Specac Autotouch vacuum press | 731 (multi-doser) |
| 1 | R4 | 2575 | 725 | E | Plastometrex PIP, KLA iMicro, Malvern Mastersizer 3000 + Aero S | 689 |
| 1 | F0 | 300 | 475 | J | sample storage: cups and plugs (Al, Cu), vials, tubes, stubs, coupons, bars, jars | 437 (UPS) |
| 1 | F1 | 1950 | 725 | C | Bambu Lab H2D, Bambu Lab A1 mini | 692 |
| 1 | F2 | 2675 | 725 | F | LECO PX500 polisher, Nabertherm NAT 15/65 furnace | 687 |
| 2 | 2R1 | 300 | 800 | K | tray glovebox (N2, purge-only), Keyence VHX-7000 | 760 (glovebox) |
| 2 | 2R2 | 1100 | 725 | L | ZwickRoell zwickiLine Z5.0 lying on its side, Mitutoyo HM-220 micro-Vickers | 689 |
| 2 | 2R3 | 1825 | 725 | M | Bruker S2 PUMA XRF, Sentry Air ductless hood, Makera Carvera CNC | 688 |
| 2 | 2R4 | 2550 | 550 | H | DDM Novastar stencil printer, Opulo LumenPnP | 516 (stencil printer) |
| 2 | 2F1 | 1950 | 725 | G | two Formlabs Form 4s, Form Wash, Form Cure | 696 |
| 2 | 2F2 | 2675 | 725 | I | two SnowX SnowPods | 686 |

The table is from one run of `setup_lab.py fit`; `out/tray_plan.json` has the run that matches the code. Every
camera-carrying tray needs 725-750 mm, because a camera head on a standard post reaches 690-706 mm. Trays H and J
have short posts (block at 270 mm) so their slots stay low.

What is left: Shuttle 1 has 390 mm free at the top of its rear column (3300-3690), too little for a tray with a UPS.
Its front column has 290 mm free. Shuttle 2 has 590 mm free in the rear column (one more short tray, up to a 575 mm
span) and 290 mm in the front.

## What moved, and why

- **Tray B gets the vacuum press.** The Specac Atlas Autotouch 15T is loaded onto tray B in the set-up movie, at
  `alloy_press.PRESS_AT`, where the alloy route uses it. It is stored with its guard down (640 mm). The multi-doser is
  731 mm tall, so tray B's slot is 775 mm.
- **The sieve shaker leaves tray F.** The alloy route sieves in the sieving cell on the bench between the rePowder and
  the VLM (`sieve_station.py`, `alloy_print.BENCH`). The set-up movie now builds that cell on the floor.
- **The XRF leaves tray F.** Tray F had four instruments, and the UPS took the back right corner. The Bruker S2 PUMA
  went to tray M.
- **The Keyence VHX leaves tray C.** With its controller beside it, it is 948 mm wide. That doesn't fit beside the
  A1 mini and in front of the UPS, so it went to tray K, beside the tray glovebox.
- **Small moves** (`line.TRAY_LOADS`, `animate.LOADS`, `fab_trays.LOADS`): the Mastersizer 60 mm forward, clear of
  the UPS and the tray's lines; the OT-2 10 mm forward of the lines; the LumenPnP 70 mm forward of the UPS.
- **New trays:** J (storage), K (glovebox), L (sideways tensile and hardness), M (XRF, ductless hood and CNC). Their
  models are `instruments_r7.py`'s. Until a model is built, `setup_lab.load_all` stands in a box of its
  `FOOTPRINTS` size, and the item's name says "stand-in box".
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
