## The warehouse version, rail or mobile base, and the lab set up from scratch (round 4)

Links are relative to `vertical-lab/`, so this section can go into the README as it is.

| Scene | GIF (640 px, 5 fps) | MP4 (1280 × 720, 15 fps) | Still |
|---|---|---|---|
| **Warehouse**: the VLM and the floor machines on an open floor, two MiR250 + UR10e units driving between docks (89 s) | [`out/warehouse.gif`](out/warehouse.gif) | [`out/mp4/warehouse.mp4`](out/mp4/warehouse.mp4) | [`out/warehouse_still.png`](out/warehouse_still.png) |
| **Set up from scratch**: tape, utilities, the VLM, the machines, the arms, trays A-F, the cameras, an orbit (1 min 51 s) | [`out/setup_lab.gif`](out/setup_lab.gif) | [`out/mp4/setup_lab.mp4`](out/mp4/setup_lab.mp4) | [`out/setup_lab_still.png`](out/setup_lab_still.png) |

`out/<name>.json` gives the frame range of every sub-step, as for the other chapters.

[`out/rail_vs_amr.json`](out/rail_vs_amr.json) has the numbers in "Rail or mobile base" below, from `python3 warehouse.py sway`.

### The warehouse version

![The warehouse version](out/warehouse.gif)

[`warehouse.py`](warehouse.py) lays the lab out on a warehouse floor instead of along a rail:
- **Two rows face one aisle.** North row: the glovebox, the rePowder, the VLM, the Aconity MIDI and the wire EDM. South
  row: the two Instrons, two chargers, and space for the DED machine and the packaging station.
- **The glovebox is turned** so its automatic antechamber faces the aisle and the arm. Its glove ports face west,
  where people work.
- **Space is kept** for a DED machine and a packaging station (keys `ded` and `packaging`), and for a hot isostatic
  press (`hip`). A model takes its spot when `tour.load()` returns it. Until then the DED and packaging spots are
  labelled footprints, sized as a guess (3.0 × 2.4 m and 2.4 × 1.5 m), and the HIP's is left empty.
- **Pallet racking** stands round three walls, so it reads as a warehouse. It is typical selective racking, not a
  quote: 108 in beams, 42 in frames, 16 ft uprights, 48 × 40 in pallets.

What the movie shows:
1. The floor, labelled.
2. The aisle, the docks and the chargers.
3. Two units leave their chargers on drawn routes: unit 1 to the VLM's opening, unit 2 to the 100 kN Instron.
4. Unit 1 docks. Its wrist camera reads the target on the dock's post. Tray B comes to the opening. The arm takes a vial
   from the rack and stands it in the holder on its own cabinet. Tray B goes back.
5. Unit 1 drives to the glovebox. At the Instron, unit 2's camera finds its target.
6. At the glovebox the antechamber's outer door opens. The arm takes the vial, gripper level, and puts it into the
   antechamber.
7. Both go back to charge.

Every arm move is solved with the UR's inverse kinematics, as in the workflow. The MiR250s drive straight legs and turn
on the spot, which they can do. They are drawn at 1.5 m/s; the MiR250's top speed is 2.0 m/s.

**The floor plan, from MiR's own figures** ("MiR250 Specifications", 2023-06-28):

| | MiR's figure | In the plan |
|---|---|---|
| Corridor for one MiR250, default footprint and SICK safety set-up | 1450 mm | |
| Two MiR250s passing, default set-up | 3000 mm (2100-2450 mm with the dynamic set-ups) | **the main aisle: 3.0 m** |
| 90° turn; U-turn; pivoting | 1500; 1600; 1800 mm | all inside the aisle |
| Docking accuracy to an L-marker | ±6 mm along, ±3 mm across, ±1° yaw | |
| Docking to a VL-marker | ±3 mm, ±3 mm | |
| "Moving to position", no marker | ±60 mm, ±85 mm, ±4° yaw | |
| MiR Charge 48V: space to each side; in front | 550 mm; 2800 mm | 578 mm between the chargers; the aisle in front |
| Charging, 10 to 90 % | 52 min | |

The MiR Charge 48V is 622 × 237 × 287 mm, 487 mm deep with its charging plate (Konica Minolta's and IDEC's listings;
both are MiR distributors).

The docks sit between the aisle and the machines: a 0.84 m band on each side, taped, with a camera target on a post.
The target is a 120 mm cube with a tag on its top and on all four sides, each one different. So the wrist camera, or
a camera on the MiR, sees a tag from any side as well as from above (round 7; it was one flat tag facing up).
So a docked unit blocks nothing. From front line to front line the band is 4.68 m: 3.0 m of aisle and two dock bands.

**A unit drives into a dock along the dock's line, from the end without the post.** A docked MiR250 stands 80 mm off
the machines' fronts. A pivot on the dock line would swing its corners 0.12 m past them, along 0.66 m of the row. So a
unit can only turn onto a dock line where the row has a gap that wide, or where a machine is set back, as the glovebox
is. Most posts stand beyond the docked unit's front end, and the unit drives in forwards.

The small Instron's dock is the exception (`BACK_IN` in `warehouse.py`). The gap between the two Instrons is the only
place on that stretch of the row to turn, and the small Instron's post used to stand in it. So that dock is backed
into from the gap, and its post now stands at the dock's other end.

No unit turns at a dock. Each one backs out the way it came in.

**`ARM_AUDIT=1` checks the MiR250s too** (`warehouse.MirCheck`). It uses FCL on the drawn meshes, as `collide.py` does
for the arms. It checks the body, the cabinet, the holder and the vial in it against the posts, the machines, the VLM
and the other unit.

On the earlier routes, 134 of 1138 frames had a MiR250 inside something:
- through the glovebox's post and the small Instron's post, twice each;
- into the VLM's front, pivoting 1.2 m from its dock;
- into the 100 kN Instron, turning round at its dock.

The arms touched those posts, and the VLM's opening, in 24 frames. Now neither the units nor the arms touch anything
they shouldn't, in any of the 1120 frames checked
([`out/collisions/warehouse.json`](out/collisions/warehouse.json),
[`out/collisions/warehouse_mir.json`](out/collisions/warehouse_mir.json)).

### Rail or mobile base

Sterling's question: a rail close to the floor with a pedestal would leave the machines easier to reach when the rail
is off, but would the pedestal sway? Three options, each carrying the UR10e's base at 800 mm:

- **A. A low rail with a pedestal.** The carriage is near the floor and a steel tube lifts the arm.
- **B. The beam-height rail of round 3.** The arm bolts straight onto Vention's carriage.
- **C. A MiR250.** No rail.

![Carrying a UR10e at 800 mm, three ways](out/rail_vs_amr.png)

[`out/rail_vs_amr.png`](out/rail_vs_amr.png) is drawn by `python3 warehouse.py compare`, with the same arm pose on each.

**The loads.** UR's manual gives the loads the arm puts into whatever it stands on (UR10e user manual, software 5.26,
6.2 "Dimensioning the Stand"). Its table is the worst case multiplied by a safety factor of 2.5:
- in normal running: Mz 830 Nm, Fz 1450 N, Mxy 860 Nm, Fxy 860 N;
- in a category 0, 1 or 2 stop: Mz 990 Nm, Fz 1700 N, Mxy 1460 Nm, Fxy 1160 N.

The manual also asks for a stand whose lowest resonance is at least 45 Hz. The estimates below take the tilting
moment and the side force without the 2.5: 344 Nm and 344 N running, 584 Nm and 464 N stopping.

**A pedestal sways little.** It is drawn as a steel cantilever (E = 200 GPa), with its tilt carried out to the tool at
the arm's 1300 mm reach. Two heights:
- 436.5 mm if Vention's beam lies on the floor (its carriage top is then at 363.5 mm);
- 650 mm on a flush floor track (carriage top about 150 mm, an estimate).

| Pedestal | Height | Tool moves, running | Tool moves, stopping | First mode (estimate) |
|---|---|---|---|---|
| Round tube 219.1 × 8.0 mm | 436.5 mm | 0.047 mm | 0.077 mm | 129 Hz |
| Square tube 150 × 150 × 6.3 mm | 436.5 mm | 0.112 mm | 0.183 mm | 84 Hz |
| Square tube 200 × 200 × 10 mm | 436.5 mm | 0.031 mm | 0.050 mm | 161 Hz |
| Round tube 219.1 × 8.0 mm | 650 mm | 0.083 mm | 0.133 mm | 89 Hz |
| Square tube 150 × 150 × 6.3 mm | 650 mm | 0.196 mm | 0.315 mm | 58 Hz |
| Square tube 200 × 200 × 10 mm | 650 mm | 0.053 mm | 0.086 mm | 111 Hz |

The first mode puts 52 kg on top: the arm (33.3 kg), its payload (12.5 kg), the 2F-85 (about 0.9 kg) and a top plate
(5 kg, an estimate). That mass sits 400 mm above the flange, also an estimate.

Read the table this way:
- **A plain steel tube is stiff enough.** A Ø219 × 8 mm tube moves the tool about 0.05-0.13 mm under UR's worst cases.
  That is the order of the UR10e's own ±0.05 mm repeatability. Every tube here is above UR's 45 Hz.
- **Sway is not lost repeatability.** A still pedestal bends the same way every time for the same pose and load, so it
  repeats. What costs repeatability is moving before the sway has died away, and play in the joints. At an assumed 2 %
  damping, a 58 Hz pedestal settles to a tenth in about 0.3 s, a 129 Hz one in about 0.14 s.
- **The weak points are the joints, and no maker's figure covers them:**
  - the bolts and plate at the pedestal's foot;
  - the carriage's bearing blocks;
  - the beam's twist.
  Each 0.001° of tilt there is 0.023 mm at the tool.
- **A pedestal loads the carriage more.** The tilting moment on the carriage grows with the pedestal's height:

  | | Lever above the beam | Running | Stopping |
  |---|---|---|---|
  | Beam-height rail (B) | 116 mm | 384 Nm | 638 Nm |
  | Low rail, 436.5 mm pedestal (A) | 436.5 mm | 494 Nm | 787 Nm |
  | Flush track, 650 mm pedestal (A) | 650 mm | 568 Nm | 886 Nm |

  That is 29-48 % more moment on the same bearings.
- **The rail itself is the bigger number.** Vention's rack and pinion repeats to ±0.3 mm including backlash
  (docs.vention.com, rack and pinion actuator; 0.25 mm backlash). That is six times the arm's ±0.05 mm, and it is the
  same for A and B.

So, on these numbers, a low rail with a good steel pedestal costs little precision against the beam-height rail. What
it costs is load on the carriage and a bolted joint at the pedestal's foot that has to be stiff. It does free the
fronts of the machines for people when the rail is off.

**C. The MiR250 needs every station measured.**
- **Docking alone is too coarse for the arm.** ±3-6 mm and ±1° is 60 to 450 times the arm's ±0.05 mm. One degree of
  yaw is 23 mm at 1.3 m of reach.
- **So the arm measures each station before it works there.** Two published ways:
  - **A camera and a target.** A wrist camera reads a fiducial fixed to the station and shifts the taught frame. This is
    what the warehouse movie shows. Its accuracy depends on the camera and the target; no maker's figure was found.
  - **Touch-off.** Burger et al.'s mobile robotic chemist (Nature 583, 237 (2020), SI 1.3) used a KUKA KMR iiwa. Its
    arm touched a 100 × 100 × 50 mm cube six times at each station. Starting up to ±15 mm and ±2.5° off, it found the
    cube to ±0.12 mm and the yaw to under 0.005°. The base itself parked to about 10 mm.
- **Sway is worse on wheels, and nobody publishes it.** The whole base rocks on its wheels and suspension, which is the
  pedestal problem again, only softer. MiR's sheet gives no stiffness. A target fixes where the station is, not the
  rocking, so precise moves need the base to settle.
- **The MiR250 can tip.** UR's own manual warns that the arm's loads can tip a mobile robot. Our unit weighs about
  195 kg:
  - MiR250 97 kg (MiR);
  - UR10e 33.3 kg, its control box 12 kg, a 12.5 kg payload (UR);
  - the cabinet, 40 kg (an estimate).

  That resists at most 554 Nm about the 580 mm body's long edge; the wheels sit inside the body, so less in fact. UR's
  worst-case loads at the floor, 0.8 m below the arm's base, come to 619 Nm running and 955 Nm stopping. So **a UR10e on
  a MiR250 has to run with lower acceleration limits** (UR: lower joint accelerations reduce these loads), and its worst
  moves should be checked in URSim.
- **The arm needs its own power.** The MiR250 gives a top module 48 V at 10 A combined, 480 W. The UR10e's maximum is
  615 W (UR's data sheet), and its standard control box runs on 100-240 V AC. Ask MiR and UR how they power this pair.

| | Positioning | What recovers precision | Floor in front of the machines |
|---|---|---|---|
| A. Low rail, pedestal | ±0.3 mm along the rail (Vention), plus pedestal sway of about 0.05-0.3 mm | taught positions; a target if needed | free when the rail is off; the rail is low |
| B. Beam-height rail | ±0.3 mm (Vention) | taught positions | closed: the beam at 440-690 mm runs 120 mm in front |
| C. MiR250 | ±3-6 mm, ±1° (L-marker); ±3 mm (VL-marker) | a camera target or touch-off at every station | free; a 3.0 m aisle and 0.84 m docks |

### The lab set up from scratch

![The lab set up from scratch](out/setup_lab.gif)

[`setup_lab.py`](setup_lab.py) builds the whole lab on the warehouse floor, in order:
1. An empty bay.
2. The layout in tape: the aisle, every footprint, the docks with their targets, the charger bays, the reserved
   spaces.
3. Utilities, all layout choices:
   - cable trays over both rows, with a power and network drop to every station;
   - 208 V three-phase to the VLM (#53);
   - an argon line from a cylinder manifold to the glovebox, the rePowder, the Aconity and the DED.
4. The VLM, as round 2's assembly but shorter. It now has six trays.
5. The floor machines come in on their footprints.
6. The first unit is put together on its charger:
   - the MiR250 rolls on;
   - the cabinet goes on top;
   - the UR control box (460 × 449 × 254 mm, 12 kg) goes inside;
   - the UR10e is lowered on and bolted down: four M8 bolts at 20 Nm, two Ø8 mm pins so it goes back in the same
     place (UR's manual, 6.1);
   - the 2F-85 goes on the flange.

   Then the second unit appears on the other charger.
7. Trays A to F come to the opening one at a time and are loaded through it. People do the loading: most instruments
   weigh more than the arm's 12.5 kg.
8. The cameras go on.
9. An orbit.

What is loaded is data, so the same script renders the full lab once the other modules are merged:
- `TRAY_ITEMS` holds trays A-F: `animate.LOADS` and `line.TRAY_LOADS`.
- `ROUND4_TRAY` holds the round-4 tray instruments. They were placed after merging, from `setup_lab.py fit`:
  - the corrosion CubXL on A, in place of round 2's CubXL;
  - the VHX on C;
  - the OpenFlexure array on D, in place of the two freestanding microscopes;
  - the sieve shaker and the XRF on F.

  `REPLACED` lists what they replace.
- `warehouse.STATIONS` holds the floor (`ded`, `packaging`). The packaging station stands on a 900 mm bench
  (`warehouse.BENCH`). There is no `hip` spot: `instruments_lab.hip()` is a comparison against a tray, and the answer
  was no.
- A key that `tour.load()` doesn't return is skipped.
- `python3 setup_lab.py fit` prints every tray item's size, whether it is under Kardex's 727.5 mm and inside the tray,
  and what it overlaps. The render prints the same warnings.

**The cameras are `services.py`'s.** `services.add_cameras(sc, L)`, the function `CAMERA_HOOK` names, puts each
tray's Pi 5 units (`services.TRAY_CAMS`) and the overhead camera at the bay into the scene. Without `services.py`, the
script draws stand-ins: a camera on a post at each tray's back corner, and two domes under the north cable tray.

### Caveats

- **The figures are only as good as their conditions.** MiR's accuracies are "in controlled conditions": one robot,
  no payload, good localization, a flat clean floor. UR's loads are worst cases.
- **The pedestal numbers are first-order.** They model a clamped tube, with no plate, anchors or carriage
  compliance, and a lumped mass for the first mode. The damping is assumed.
- **The tipping check uses an estimated cabinet mass** and ignores where the wheels actually are.
- **These are layout choices, not a design:** the racking sizes, the cable trays, the argon line, the camera targets
  and the reserved footprints. The targets are drawn like AprilTag 36h11 tags, schematically: a white ring, a black
  ring and 6 x 6 data cells per face. The bits are seeded at random, not real tag IDs.
- **The collision checks cover only the drawn meshes, at the drawn speeds.** They know nothing of the MiR250's safety
  scanners. In practice those keep a moving unit farther from things than these routes do: MiR's corridor for one
  unit is 1.45 m.

### Running it

```bash
python3 warehouse.py sway                                                    # -> out/rail_vs_amr.json
xvfb-run --server-num=N -s "-screen 0 1280x720x24" python3 warehouse.py compare   # -> out/rail_vs_amr.png
xvfb-run --server-num=N -s "-screen 0 1280x720x24" python3 warehouse.py     # -> out/warehouse.gif, out/mp4/warehouse.mp4
ARM_AUDIT=1 xvfb-run -a python3 warehouse.py      # no render: -> out/collisions/warehouse.json (arms), warehouse_mir.json
python3 setup_lab.py fit                                                     # what loads where, and whether it fits
xvfb-run --server-num=N -s "-screen 0 1280x720x24" python3 setup_lab.py     # -> out/setup_lab.gif, out/mp4/setup_lab.mp4
```

### Sources

- MiR250 Specifications, 2023-06-28, Mobile Industrial Robots, hosted by the MiR distributor Hartfiel:
  <https://www.hartfiel.com/wp-content/uploads/2024/04/MiR250-Specs.pdf>
- MiR Charge 48V size and weight: Konica Minolta Australia's MiR add-on page
  (<https://www.konicaminolta.com.au/products/robotics/mir-addon/mir-charge-48v>) and IDEC's MiR pages
  (<https://en.idec-fs.com/mir/products/charge/>)
- UR10e data sheet, October 2026: <https://www.universal-robots.com/manuals/latest/en/datasheets/ur10e/>
- UR10e user manual, software 5.26, sections 6.1 and 6.2:
  <https://www.universal-robots.com/manuals/EN/PDF/SW5_26/user-manual-UR10e-PDF_online/711-039-00_UR10e_User_Manual_en_Global.pdf>
- Vention rack and pinion actuator: <https://docs.vention.com/docs/rack-and-pinon-actuator>
- B. Burger et al., "A mobile robotic chemist", Nature 583, 237-241 (2020), Supplementary Information section 1.3
- Pallet sizes: the 48 × 40 in GMA pallet, one of ISO 6780's sizes. The racking dimensions are typical, not a quote.
