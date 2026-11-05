# Scaling up: a large-format printer and a repair cell (round 8, scale stream)

Sterling's review (PR #318, 2026-11-05 00:37 UTC): *"You should add an EOS or some type of large-format printer and show
later on the printing of real aerospace parts and repairs of real ship parts."*

The alloy route ends with an alloy proved gram by gram: atomized in the rePowder, printed in the Aconity MIDI, tested
and characterized. This round adds the two machines that alloy goes to next, and a chapter, `scaleup.py`, in which one
builds a real aerospace part and the other repairs a real kind of ship part.

| File | What |
|---|---|
| `r8_scale.py` | `REGISTRY` (`eos_m400`, `meltio_cell`), `FLOOR_PLACEMENT`, `FOOTPRINTS`, `BBOX`, `SOURCES`, `ENVELOPES`, the parts (`bracket_mesh`, `tensile_bars`, `propeller_meshes`, `bead_paths`), the cell's robot (`robot_ik`, `robot_fk`) and its repair program (`repair_program`), `check_floor()`. `python3 r8_scale.py` prints the floor check and the program's figures |
| `scaleup.py` | the chapter: `out/scaleup.{gif,json}`, `out/mp4/scaleup.mp4`, `out/scaleup_still.png` |

No tour clips of the two machines were rendered (`tour.py eos_m400` and `tour.py meltio_cell` would make them; the
models carry their own `actions` for it).

## The chapter

`VIZ3D_FPS=8 LP_NUM_THREADS=2 nice -n 5 xvfb-run --server-num=17 -a python3 scaleup.py` (render in progress when these notes were first committed; its figures follow in the next commit).

Nine steps on a plain floor, the lab's InssTek MX-Lab beside the two for scale:

1. **The machines.** The EOS M 400-4, the Meltio Robot Cell and the MX-Lab, labelled.
2. **The powder.** A panel: one rePowder run against one Aconity MIDI build against one EOS bed (the table below).
3. **The plate in.** The chamber door opens, the 400 mm build plate goes onto the platform, the door shuts, and the
   machine is drawn see-through.
4. **The build.** The parts grow, cut from their meshes at the layer height every frame, inside a see-through powder
   cake. The four beams go from the four scanners to points on the layer being melted. The recoater sweeps, and a gauge
   counts layers (1667 at 60 µm) and height.
5. **Out.** The platform lifts the plate out of the powder, the door opens, and the plate goes out to a saw table.
6. **Off the plate.** A band saw (drawn as its blade) parts the brackets, and they lift off; the 30 tensile bars stay.
7. **The cell.** The cell's doors slide open on a nickel aluminium bronze propeller on the positioner, then shut, and
   the cell is drawn see-through. The positioner tilts the propeller 72° so that the damaged leading edge faces up.
   Close-up: the notch.
8. **The repair.** The robot brings the head down, and six passes of beads fill the notch, each bead appearing as the
   head lays it. The blue light and melt pool show only while a bead is being laid. Head up, robot home, and the edge
   stands proud as deposited.
9. **After.** The edge is machined back to the profile (the patch replaces the beads), the positioner levels the
   propeller, and the wide view returns with a panel of what size of part each machine takes.

**Checks.** No UR arm moves, so `ARM_AUDIT` (which checks `robot.Robot` arms) has nothing to check. The cell's robot
is checked numerically instead, over the whole repair program sampled 400-600 times:

- the printhead's box (262 x 272 mm, from 90 mm over the nozzle tip to the flange) stays at least **75 mm** from the
  propeller (`scaleup.check_head()`, printed when the chapter runs). The nozzle itself is 12 mm over the bead it lays,
  by design;
- the arm's links, drawn as capsules (lower and upper arm 100 mm radius, the shoulder housing 125 mm), stay at least
  **334 mm** from it. This check was run once for these notes and isn't in the code.

The swing between home and the blade is made at a nozzle height of 1520 mm, over the tilted propeller's top at
1400 mm.

### Fixed after the first preview (this session)

- **The propeller is drawn left-handed** (`r8_scale._wrap`). Right-handed, it needed −72° of tilt to turn the damaged
  edge up, which turned its back, and the positioner, towards every front camera: the propeller sat behind the
  faceplate. Left-handed, it tilts +72° and faces the front. Either hand is plausible: Damen lists the Stan Tug 1606,
  whose propeller the WAAMpeller was designed after, with twin-screw propulsion
  ([Damen, Stan Tug 1606](https://damen.com/vessels/tugs/stan-tugs/stan-tug-1606)), so the tug carries one of each
  hand. Which hand the WAAMpeller was isn't stated.
- **The cell's doorway is clear.** The front had a centre post and a rail at 900 mm across the sliding doors' opening.
  Both are gone from between the doors. They hid the propeller in step 7 and would block loading a 400 kg part.
- **The blue light follows the bead.** The light and the melt pool were on from the first bead to the last, so they
  hung 40 mm in the air while the head moved between passes. They now fade with the program's `pool` state.
- **The powder panel lines up.** It uses a monospaced font, with the figures in one column.
- **Cameras.** The chamber close-up is square on, so the touchscreen sits at the edge of the frame instead of filling
  its top right. The cell's opening shot looks in through the open doors. The tilt and deposit close-ups keep the robot's
  base out of the way.

## The machines

### EOS M 400-4 (laser powder-bed fusion), key `eos_m400`

- **Published:** build volume 400 x 400 x 400 mm *including the build plate*; four 400 W Yb fibre lasers, four F-theta
  lenses and four scanners, every laser over the whole 400 x 400 mm field; up to 7.0 m/s; focus about 90 µm; 3 x 50 A,
  45 kW maximum and 22 kW typical; compressed air 7 bar, 20 m³/h
  ([EOS system data sheet](https://eos.info/en-us/metal-solutions/metal-printers/data-sheets/sds-eos-m-400-4)).
- **Size:** 4181 x 1613 x 2355 mm and about 4835 kg, at least 6500 x 6000 x 3300 mm to install, as EOS's product page
  ([eos.info, EOS M 400-4](https://eos.info/en/industrial-3d-printer/metal/eos-m-400-4)) and data sheet were indexed by
  search on 2026-11-05. **EOS's US product page now says otherwise:** 5140 x 2490 x 2625 mm (axes not labelled), about
  4900 kg, at least 7500 x 6000 x 3300 mm
  ([eos.info, M 400-4, US](https://www.eos.info/en-us/metal-solutions/metal-printers/eos-m-400-4)). That is probably
  the system with its peripherals, or a later revision; I could not tell which. The model keeps 4181 x 1613 x 2355 mm,
  and the floor placement clears everything at either size.
- **Moving:** the chamber door (hinged left), the build plate going in on its path, the platform (piston), the recoater,
  the four beams, the build. In the tour the build grows in five slabs; in the chapter the parts' meshes are cut at the
  layer height every frame, with the powder cake drawn see-through around them.
- **Estimated (from EOS's photos, approximate):** the split into the process station (left) and the setup and unpacking
  station (right, glove ports under a window), the chamber's size, the dispenser, the recoater, where the four scanners
  sit, the touchscreen on its arm, the plate's thickness (30 mm), the colours.

### Meltio Robot Cell with the Blue Laser Engine (wire-laser DED), key `meltio_cell`

- **Published** ([Meltio Robot Cell](https://meltio3d.com/metal-3d-printers/meltio-robot-cell)): 4050 x 2350 x 3000 mm;
  8 axes: an ABB robot with SafeMove and a two-axis positioner, 500 kg standard; print envelope 1000 mm diameter x
  1200 mm with the positioner interpolating, 2000 x 1000 x 1000 mm without it; 300 x 400 mm actively cooled build plate;
  Class 1 enclosure with interlocks and active laser windows; three 50 L argon bottles; external feeders for spools and
  drums over 100 kg; 400 V three-phase, 20 kW peak, 7 kW average. **Blue Laser Engine:** 1000 W from nine 450 nm direct
  diodes, a robot-mounted head 262 x 272 x 572 mm (20.5-23 kg), wire 0.8-1.2 mm, a wall-mounted control unit
  600 x 300 x 800 mm. Materials listed: steels, nickel alloys, titanium, **copper alloys**. Nickel aluminium bronze is not
  named. The 2025 data sheet gives 4000 kg as indexed by search; the page itself gives no mass.
- **Estimated:** the robot (Meltio names ABB, not the model): drawn after an IRB 2600, shoulder 445 mm up and 150 mm
  forward, lower arm 700 mm, upper arm to the wrist 795 mm, on a 550 mm riser. The positioner's layout (a pedestal on
  one side, the tilt axis 800 mm up, a 650 mm faceplate). The enclosure's posts, doors, panels and the amber glazing
  for 450 nm are our reading of Meltio's photos. The robot moves four of its axes (turret, shoulder, elbow, wrist
  pitch), with the head kept vertical. The IK is analytic (`robot_ik`) and checked against the forward kinematics.
- **As modelled, 4354 x 3430 x 3160 mm** (`BBOX`) with what stands outside the enclosure: the control unit on its side
  wall, the HMI on a pedestal in front, the argon bottles and a wire drum behind, a beacon on the roof.

### What size of part each takes (`r8_scale.ENVELOPES`)

| Machine | Takes |
|---|---|
| InssTek MX-Lab (DED, in the lab) | 150 x 150 x 150 mm stroke on a 175 x 175 mm table (`instruments_lab.DED`) |
| Aconity MIDI (LPBF, in the lab) | 170 mm diameter x 200 mm (`lab_models/equipment.py`, `ACONITY`) |
| EOS M 400-4 (LPBF) | 400 x 400 x 400 mm, the plate included |
| Meltio Robot Cell (DED) | 1000 mm dia. x 1200 mm with the positioner turning; 2000 x 1000 x 1000 mm robot only; 500 kg |

The MX-Lab cannot take a propeller blade: a 150 mm stroke repairs coupons and blade-edge test pieces. The 1350 mm,
400 kg propeller is within the cell's 500 kg but past its 1000 mm envelope for printing with the positioner turning,
so the chapter repairs one blade at a time: the positioner tilts the blade's damaged edge face up and holds it, and the
robot alone lays the beads within its 2000 x 1000 x 1000 mm. That is our reading of Meltio's figures, not a Meltio
statement.

## The parts

- **Sentinel-1 antenna bracket**, after RUAG Space, Altair and EOS. About 40 cm long, aluminium, printed on an EOS M 400
  ([develop3d, 2014](https://www.develop3d.com/blog/2014/11/collaborative-project-between-ruag-space-altair-and-eos-to-be-unveiled-at-e)).
  The [EOS case study](https://uk.eos.info/01_parts-and-applications/case_studies_applications_parts/_case_studies_pdf/en_cases/cs_m_aerospace_ruag_en.pdf)
  (as indexed by search; the PDF did not open here) adds: EOS Aluminium AlSi10Mg, 60 µm layers, printed by citim GmbH;
  one build held two antenna brackets, 30 tensile specimens and other test items, in about 80 h; stiffness more than
  30 % over its minimum; qualified for flight. Weight saving: 40 % in the case study, 1.6 kg to 1.2 kg after the first
  optimization loop in [RUAG's Altair talk](https://speakerdeck.com/altairhyperworks/additive-manufacturing-for-space-application-franck-mouriaux-ruag-space).
  **The shape here is ours**: RUAG's geometry is not public, so the bracket is a schematic topology-optimized truss,
  380 x 110 x 100 mm, lying on its feet so that two fit on the 400 mm plate. The tensile bars are 10 x 62 mm blanks in
  two rows of 15 (the count is the case study's; size and layout ours). The case study's build was on the one-laser
  M 400; the chapter puts it in the four-laser M 400-4 and says so.
  AlSi10Mg is one of the route's alloys, which is why this part, rather than a titanium one such as GE's bracket
  challenge, is the aerospace example.
- **The propeller**, after the WAAMpeller of Damen Shipyards, RAMLAB, Promarin, Autodesk and Bureau Veritas: three
  blades, 1350 mm across, about 400 kg, nickel aluminium bronze, printed by wire-arc DED at RAMLAB after Promarin's
  design for Damen's Stan Tug 1606, then CNC milled
  ([MarineLink](https://www.marinelink.com/amp/news/propeller-prototype429251)). **Estimated:** the blade (pitch ratio
  0.9, skew 15° at the tip, chord and thickness from a standard-series table, NACA-like sections with 1.8 % camber),
  the hub (250 x 270 mm), and the hand (left: see above). **Illustrative:** the damage, a notch eroded into blade 0's
  leading edge from 0.70 to 0.88 R, up to 30 mm deep, and the repair: six passes of beads (each drawn about 2x a
  1.2 mm wire's bead), then machined back to the original profile. The machining is shown as the patch replacing the
  beads; the caption says it is done on a mill or by hand, not in the cell.
- **Navy context, in the captions:** AML3D's ARCEMY wire-arc cells print nickel aluminium bronze and copper-nickel parts
  for the US Navy's submarine industrial base ([metal-am.com](https://www.metal-am.com/aml3d-expands-us-navy-submarine-additive-manufacturing-with-nickel-aluminium-bronze-prototype-order/),
  [Defence Connect](https://www.defenceconnect.com.au/naval/18883-aml3d-signs-initial-production-parts-order-for-us-navy-submarines)).
  The ARCEMY's outer size isn't published, so it is not the modelled cell.
- **Not checked here:** that copper alloys absorb 450 nm light far better than the ~1 µm of fibre lasers is widely
  stated by blue-laser makers; I did not look up a figure. **Assumed:** NAB filler wire (AWS ERCuNiAl class) on
  Meltio's blue head: Meltio lists copper alloys, not NAB.

## Powder: why the recipe scales, not the powder

| | g | Source |
|---|---|---|
| one rePowder run, < 63 µm | 188 | [DAL #219](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/219#issuecomment-6509252104) (`alloy_atomize.K7M2Q9`: 187.973 g of 1079.886 g charged) |
| one Aconity MIDI build | 440 | the lab's planning figure (`alloy_atomize.MIDI_BUILDS`: powder-doser `design/brainstorming.md`, section 3) |
| the EOS bed, 400 x 400 x 100 mm | about 22,400 | **estimate**: bulk density 1.4 g/cm³ assumed for AlSi10Mg |

So one 100 mm EOS build of this job takes as much powder as about 119 rePowder runs make under 63 µm. The chapter
says the recipe is what the route hands on, and that the powder is bought by the 100 kg (EOS sells AlSi10Mg). That is
a plan, not something sourced.

## On the floor (`FLOOR_PLACEMENT`, setup_lab's floor frame)

Neither machine fits in a row. The free gaps in the south row are 4.17 m east of the wire EDM (beside the racking,
over the EDM's MiR pivot spot) and 4.65 m west of the Instron 68FM-100 (in front of the racking). The EOS is 4.18 m wide
and the cell 4.35 m with its control unit, and EOS asks for at least 6.5 x 6.0 m (or 7.5 x 6.0 m) to install the
M 400-4. So both stand **south of the south row, past the racking's ends, fronts to the north**. Each has a clear strip
in front, 4.17 m or wider, running north to the aisle's end. Neither has a MiR dock: the powder comes by the 100 kg in
EOS's containers, and a propeller by forklift or crane. Both stay on `warehouse.py`'s floor plane, which runs to
y = -14000.

**The placements are written in `setup_lab.merge_r8`'s terms, which are `warehouse.place`'s.** `y` only picks the row
("S" here). `x` is the centre of the model's whole bounding box (`BBOX`, the externals included). `turn` is relative
to the row: 0 puts the front to the aisle, which for the south row is north. The front stands on the south row's face
(y = -6238), moved back by `warehouse.SETBACK[key]`. The first draft had `turn=180`, read as absolute, which the merge
would have turned to face south; it is now 0.

| Key | x (box centre) | y (enclosure centre) | turn | setback | Enclosure (x, y) | Least gap: box / footprint |
|---|---|---|---|---|---|---|
| `eos_m400` | -9450 | -10700 | 0 | 3525 | -11540..-7360, -11506..-9894 | 563 / 694 mm, to the west racking's end (255 mm at EOS's larger 5140 x 2490) |
| `meltio_cell` | 9602 | -10600 | 0 | 2747 | 7425..11475, -11775..-9425 | 54 / 358 mm, to the east racking |

The cell's 54 mm is only its bounding box's corner, which takes its east edge from the control unit and its north edge
from the HMI. The control unit stands 54 mm short of the racking's line but 1.1 m south of its end, and the HMI, beside
the racking's end, is 650 mm from it. Checked by
`r8_scale.check_floor()` against `setup_lab fit`'s rectangles of 2026-11-04 (`out/tray_plan.json`). No other round-8
module places anything on the floor.

**For the lab stream (`merge_r8`), two things:**

1. `merge_r8` does not set `warehouse.SETBACK`, so as written it puts both machines *in* the south row: the EOS in the
   west gap (it fits, 172 mm from the Instron 68FM-100), and the cell overlapping the wire EDM by 235 mm
   (`r8_scale.check_floor(setback=0)`). One line in its loop would place them as intended:
   `W.SETBACK[key] = float(p.get("setback", 0.0))`.
2. `merge_r8` gives every floor key a dock on the south dock line at `dock_x` (= `x`), and `check_floor` gives it a
   target post 150 mm off the row's face, at (x - 650, -6088). Neither machine is served by a MiR, so those should be
   skipped for these two keys.

## Open

- **EOS's two sets of figures** (4181 x 1613 x 2355 mm against 5140 x 2490 x 2625 mm): worth asking EOS which is the
  machine itself.
- **NASA's GRCop-42 chamber liners** (a copper alloy, RAMPT, built by L-PBF; NASA's slides mention EOS M 400-class
  machines) were the second aerospace part planned; not drawn, for time.
- The robot's model, the positioner's real layout, the doors, and NAB wire on the blue head: to be checked with Meltio.
- The set-up movie needs `merge_r8` to apply the setbacks (above); not checked with `setup_lab.py fit`.
- The tour clips (`tour.py eos_m400`, `tour.py meltio_cell`) were not rendered. The tour and the chapter use the same
  models, so a fix in `r8_scale.py` rebuilds both (`tour.load` caches on the file's hash).
