# Scaling up: a large-format printer and a repair cell (round 8, scale stream)

Sterling's review (PR #318): *"You should add an EOS or some type of large-format printer and show later on the printing
of real aerospace parts and repairs of real ship parts."*

The alloy route ends with an alloy proved gram by gram: atomized in the rePowder, printed in the Aconity MIDI, tested
and characterized. This round adds the two machines that alloy goes to next, and a chapter, `scaleup.py`, in which one
builds a real aerospace part and the other repairs a real kind of ship part.

| File | What |
|---|---|
| `r8_scale.py` | `REGISTRY` (`eos_m400`, `meltio_cell`), `FLOOR_PLACEMENT`, `FOOTPRINTS`, `SOURCES`, `ENVELOPES`, the parts (`bracket_mesh`, `tensile_bars`, `propeller_meshes`, `bead_paths`), the cell's robot (`robot_ik`, `robot_fk`) and its repair program (`repair_program`), `check_floor()` |
| `scaleup.py` | the chapter: `out/scaleup.{gif,json}`, `out/mp4/scaleup.mp4`, `out/scaleup_still.png` |
| tour clips | `out/instruments/eos_m400.{gif,png,json}`, `out/instruments/meltio_cell.{gif,png,json}`, `out/mp4/instruments/` |

## The machines

### EOS M 400-4 (laser powder-bed fusion), key `eos_m400`

- **Published:** build volume 400 x 400 x 400 mm *including the build plate*; four 400 W Yb fibre lasers, four F-theta
  lenses and four scanners, every laser over the whole 400 x 400 mm field; up to 7.0 m/s; focus about 90 µm; 3 x 50 A,
  45 kW maximum and 22 kW typical; compressed air 7 bar, 20 m³/h
  ([EOS system data sheet](https://eos.info/en-us/metal-solutions/metal-printers/data-sheets/sds-eos-m-400-4)).
- **Size:** 4181 x 1613 x 2355 mm and about 4835 kg, at least 6500 x 6000 x 3300 mm to install, as EOS's product page
  and data sheet were indexed by search on 2026-11-05. **EOS's US product page now says otherwise:** 5140 x 2490 x
  2625 mm (axes not labelled), about 4900 kg, at least 7500 x 6000 x 3300 mm
  ([eos.info, M 400-4](https://www.eos.info/en-us/metal-solutions/metal-printers/eos-m-400-4)). That is probably the
  system with its peripherals, or a later revision; I could not tell which. The model keeps 4181 x 1613 x 2355 mm, and
  the floor placement clears everything at either size.
- **Moving:** the chamber door (hinged left), the build plate going in on its path, the platform (piston), the recoater,
  the four beams, the build. The tour shows the build in five slabs; the chapter cuts the parts' meshes at the layer
  height every frame, with the powder cake drawn see-through around them.
- **Estimated (from EOS's photos, approximate):** the split into the process station (left) and the setup and unpacking
  station (right, glove ports under a window), the chamber's size, the dispenser, the recoater, where the four scanners
  sit, the plate's thickness (30 mm), the colours.

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
  for 450 nm. The robot moves four of its axes (turret, shoulder, elbow, wrist pitch), with the head kept vertical. The
  IK is analytic (`robot_ik`) and checked against the forward kinematics.
- **As modelled, 4354 x 3430 x 3160 mm** with what stands outside the enclosure: the control unit on its side wall, the
  HMI on a pedestal in front, the argon bottles and a wire drum behind, a beacon on the roof.

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
  two rows of 15 (the count is the case study's; size and layout ours).
  AlSi10Mg is one of the route's alloys, which is why this part, rather than a titanium one such as GE's bracket
  challenge, is the aerospace example.
- **The propeller**, after the WAAMpeller of Damen Shipyards, RAMLAB, Promarin, Autodesk and Bureau Veritas: three
  blades, 1350 mm across, about 400 kg, nickel aluminium bronze, printed by wire-arc DED at RAMLAB after Promarin's
  design for Damen's Stan Tug 1606, then CNC milled
  ([MarineLink](https://www.marinelink.com/amp/news/propeller-prototype429251)). **Estimated:** the blade (pitch ratio
  0.9, skew 15° at the tip, chord and thickness from a standard-series table, NACA-like sections with 1.8 % camber),
  the hub (250 x 270 mm). **Illustrative:** the damage, a notch eroded into blade 0's leading edge from 0.70 to
  0.88 R, up to 30 mm deep, and the repair: six passes of beads (each drawn about 2x a 1.2 mm wire's bead), then
  machined back to the original profile.
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
| one rePowder run, < 63 µm | 188 | DAL #219 (`alloy_atomize.K7M2Q9`: 187.973 g of 1079.886 g charged) |
| one Aconity MIDI build | 440 | the lab's planning figure (`alloy_atomize.MIDI_BUILDS`) |
| the EOS bed, 400 x 400 x 100 mm | about 22,400 | **estimate**: bulk density 1.4 g/cm³ assumed for AlSi10Mg |

So one 100 mm EOS build of this job is about 119 rePowder runs of fines. The chapter says the recipe is what the route
hands on and the powder is bought by the 100 kg (EOS sells AlSi10Mg). That is a plan, not something sourced.

## On the floor (`FLOOR_PLACEMENT`, setup_lab's floor frame)

Neither fits in a row. The free gaps are 4.17 m east of the wire EDM (beside the racking and over the EDM's MiR pivot
spot) and 4.65 m west of the Instron 68FM-100 (in front of the racking), and EOS asks for at least 6.5 x 6.0 m (or
7.5 x 6.0 m) to install the M 400-4. So both stand **south of the south row, past the racking's ends, fronts to the
north**, each with a clear strip of 2.4 m or more in front running up to the aisle's end. No MiR dock: the powder comes
by the 100 kg in EOS's containers, and a propeller by forklift or crane.

| Key | x, y (centre) | turn | Rectangle (x, y) | Least gap |
|---|---|---|---|---|
| `eos_m400` | -9450, -10700 | 180 | -11541..-7360, -11507..-9894 | 694 mm to the west racking's end (255 mm at EOS's larger 5140 x 2490) |
| `meltio_cell` | 9700, -10600 | 180 | 7675..11725, -11775..-9425 | 225 mm to the east racking's end; 643 mm south of the wire EDM |

`turn` is degrees about z, counterclockwise from above; 0 faces -y like the north row, 180 faces +y. The cell's
externals stick out beyond its published rectangle (the control unit 300 mm east, the HMI 440 mm north, the argon and
wire drum up to 640 mm south); none reaches anything. `python3 r8_scale.py` prints the check. Not yet checked with
`setup_lab.py fit` (the lab stream merges and checks the placements).

## The chapter

`VIZ3D_FPS=8 xvfb-run --server-num=<n> python3 scaleup.py`. Nine steps on a plain floor, the lab's MX-Lab beside the two
for scale: the machines; the powder (a panel of the figures above); the plate in; the build (the parts growing, four
beams on the current layer, the recoater, a layer gauge); the platform up and the plate out to a saw; the brackets cut
off the plate and lifted; the propeller on the positioner and the damaged edge (before); the positioner tilts, the robot
lays six passes; head home, the edge as deposited; machined back (after), and a panel of what each machine takes.

CHAPTER_RESULT

**Collisions.** No UR arm moves, so `ARM_AUDIT` has nothing to check. The cell's robot is checked by `check_head()`:
over the whole program, the printhead's box stays at least **75 mm** from the propeller's surface (the nozzle itself
is 12 mm over the bead it lays, by design). The arm's links are not checked against the blades; they pass well above
them (the swing between home and the blade is made at a nozzle height of 1520 mm, over the propeller's 1460 mm top).

## Open

- **EOS's two sets of figures** (4181 x 1613 x 2355 mm against 5140 x 2490 x 2625 mm): worth asking EOS which is the
  machine itself.
- **NASA's GRCop-42 chamber liners** (a copper alloy, RAMPT, built by L-PBF; NASA's slides mention EOS M 400-class
  machines) were the second aerospace part planned; not drawn, for time.
- The robot's model, the positioner's real layout and NAB wire on the blue head: to be checked with Meltio.
- The tour clips and the chapter use the same models, so a fix in `r8_scale.py` rebuilds both (`tour.load` caches on
  the file's hash).
