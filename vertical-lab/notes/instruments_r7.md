# Round 7: the stations still missing (#303, PR #318)

Code: [`instruments_r7.py`](../instruments_r7.py), plus the VHX in [`instruments_char.py`](../instruments_char.py).
Each model is an `instruments.Instrument` with its own tour: `xvfb-run --server-num=40 python3 tour.py <key>`.
`FOOTPRINTS` at the top of the module gives each one's size, mass, product, source and whether it goes on a tray.

Limits used: 2426 x 840 mm inside a tray's rim, 856.5 mm product height (the 996 mm opening), trays of 228, 360
or 490 kg. Each tray also carries its UPS and dock plate at the back right.

| Key | What | Size W x D x H (mm) | Mass | Where |
|---|---|---|---|---|
| `glovebox_tray` | Custom N2 glovebox, purge-only, mini antechamber at the front | 1390 x 830 x 810 | about 140 kg (estimate) | tray |
| `tensile_h` | ZwickRoell zwickiLine Z5.0 TN, lying on its side | 1289 x 638 x 448 | 83 kg | tray |
| `hardness` | Mitutoyo HM-220 Type D, with its AVPAK PC | 533 x 672 x 595 | 48 kg | tray |
| `cnc` | Makera Carvera, with a lid actuator and a pneumatic vise | 610 x 535 x 540 (836 open) | about 50 kg | tray |
| `fumehood` | Labconco Protector XStream 4 ft, on a base cabinet | 1219 x 958 x 2581 | about 260 kg | floor |
| `fumehood_tray` | Sentry Air ductless hood, standard 24 in, with its blower | 1030 x 610 x 715 | about 41 kg | tray |
| `storage` | Sample storage load (our design) | 1760 x 760 x 300 | about 95 kg (estimate) | tray |
| `vhx` | VHX-7000 + EA-300, the controller turned sideways, a PiKVM | 630 x 625 x 716 | 43.4 kg | tray |

## a. A glovebox on a tray

- **No compact glovebox sold fits as it is.** Vigor's standard box is 1200 x 750 x 900 mm in the body alone. Plas-Labs'
  830-ABC is 1100 x 610 x 790 mm, but it is acrylic.
  - Vigor SG1200/750: 220 mm aluminium glove ports, a mini antechamber of 150 mm ID x 300 mm, a main one of
    370 x 600 mm, a purifier holding < 1 ppm
    ([distributor page](https://www.pharmaceutical-tech.com/products/vigor-tech-usa/standard-gloveboxes)).
  - Plas-Labs 830-ABC: 1100 x 610 x 790 mm with a 12 in transfer chamber; inside 710 x 580 x 740 mm
    ([reseller](https://spectraservices.com/product/plas-labs-830-ABC.html)).
  - Tenders ask for a mini antechamber of about 150 x 300-425 mm and ports of 200 mm or more (IIT Madras annexure).
- **So it is our design, from those parts.**
  - A stainless box 1100 x 520 x 640 mm on a 40 mm frame, with a polycarbonate front and two 220 mm ports.
  - A 150 mm mini antechamber out of the front, so the arm loads it there. Its outer door slides sideways, so it never
    leaves the tray. Its inner door slides up inside the box.
  - Inside: a shelf for the sled, a capper on a small gantry, a cradle that lifts and tips the jar, a balance with a
    storage jar. O2 and H2O sensors on the back wall, readouts on the PLC's screen.
  - On the right: the PLC, the antechamber's pump. Behind: the N2 line from the tray's dock. On top: an oil bubbler.
  - 810 mm tall with its fittings. All of these sizes are ours.
- **Purge-only, no purifier.** Why:
  - N2 already comes through the tray's dock.
  - A purifier's catalyst has to be regenerated with forming gas (H2) and a heater for hours. That doesn't belong
    inside the VLM. A purifier also adds about 100 kg, a blower's heat, and holds < 1 ppm, which this job doesn't need.
  - The cost is gas: about 7.6 box volumes (2.4 m3) to purge from air to 100 ppm O2, then a trickle.
  - **The dock's N2 can't do the first purge.** The UHPN2-1100 gives 0.5-1.1 L/min (services.md): 36 h or more.
    It needs a larger N2 supply, a dewar or a bigger generator, on the floor.
- **The job shown:** the atomizer's catch jar comes in sealed; three pump-and-refill cycles; inside, the capper takes
  its lid off, the cradle lifts and tips the powder into a storage jar on the balance, the capper closes both jars.

## b. A tensile tester on its side

- **ZwickRoell's zwickiLine can run horizontal.** Search results quote its product information: "can be operated in
  vertical or horizontal position as required, and can be swiveled 180 degrees in horizontal mode". The copy on
  DirectIndustry returned 403, so I couldn't open the page.
- **Figures** ([PI 396 1123](https://www.zwickroell.com/fileadmin/content/Files/SharePoint/user_upload/PI_EN/02_396_zwickiLine_Z0_5_up_to_Z5_0_Materials_Testing_Machine_PI_EN.pdf)):
  - Z5.0 TS, TN, TH: 789, 1289 and 1589 mm tall; 408 wide (411 with electronics); 480 deep (622 with electronics);
    70, 78 and 83 kg.
  - 5 kN; 0.0005-600 mm/min; test-area depth 105 mm.
  - **The Z5.0 TS, 789 mm tall, fits a tray standing up.**
- **Drawn: the TN on its side.** 1289 mm along the tray, 408 mm tall, plus our 40 mm base plate. The test area faces
  the opening; the arm lowers the bar between the open jaws from above.
- **5 kN can't pull the alloy route's bar.** The 6 x 6 mm bar needs 14.8 kN. Faced to 6 x 1.5 mm (an E8 sub-size bar,
  thinner), it needs 3.7 kN at 412 MPa, 74 % of the frame. The Carvera (d) can face it.
- **No motorized horizontal machine with a published size reaches 14.8 kN.**
  - Tinius Olsen sells horizontal machines from 5 to 300 kN; no size published.
  - ADMET's eXpert 5000 frames can be set up horizontal; quote only.
  - TecQuipment's SM1002 is 20 kN but hand-cranked.
  - Mark-10's horizontal stands stop at 2.2 kN. Kammrath & Weiss's 10 kN module takes specimens of 60 mm at most.
  - No Instron statement says a 68SC or 68TM can be mounted horizontally.
- The curve in the clip is illustrative and says so.

## c. A hardness tester

- **Mitutoyo HM-220 Type D**, from Mitutoyo's catalogue section K
  ([PDF](https://www.mitutoyo.com/webfoo/wp-content/uploads/K_section.pdf)):
  - main unit 315 x 671 x 595 mm, 43 kg;
  - 0.4903 mN to 19.61 N (0.05 gf to 2 kgf);
  - a motorized turret for up to 4 objectives and 2 indenters;
  - Type D: a motorized XY stage, 50 x 50 mm (100 x 100 optional), table 130 x 130 mm, 25 mm/s; motorized focus
    over 1.4 mm; a 3 MP camera; AVPAK, which measures each indent, on a PC Mitutoyo specifies.
- It is the only automatic tester whose height I found from its maker: 260 mm under the opening.
- Others: QATM's Qness 60 A+ EVO (60 kg, 150 x 150 mm XY, up to 62.5 kgf) is the stronger machine, but its height
  wasn't found. Struers' Duramin-40 and Buehler's VH3300 publish no size I could open.
- The layout (base, back column, head, camera on top) is read off Mitutoyo's photos. The PC beside it is an estimate.
- The clip: one HV0.5 indent, read by AVPAK, then a series of five. Indents are drawn 1.5 mm across and 3 mm apart;
  real ones in AlSi10Mg (about 125 HV) are 86 um. The reading on screen is illustrative.

## d. An autonomous CNC

- **Makera Carvera**, from Makera's spec
  ([its Carvera vs Carvera Air article](https://www.makera.com/blogs/article/carvera-carvera-air-which-desktop-cnc-is-right-for-you)):
  580 x 520 x 540 mm, about 50 kg, 840 mm with the lid open; work area 360 x 240 x 140 mm; a 6-tool changer with auto
  probing; 200 W spindle.
- **Why it:** the only one with a real tool changer that fits a tray, even with the lid open.
  - Roland MDX-50: 760 x 900 x 732 mm, 122 kg, a 5-tool changer. 900 mm deep, so it fits only turned, with its door
    facing along the tray.
  - Bantam Tools Desktop CNC (503 x 531 x 493 mm) and Tormach xsTECH: no tool changer.
  - DATRON neo (805 x 1290 x 1880 mm, about 700 kg, 24 tools, robot-ready): the floor.
- **What it lacks, and what we added:** its lid is lifted by hand, and it has no automation interface. The model adds a
  lid actuator and a pneumatic vise. Their sizes are estimates.
- **200 W is light for aluminium:** facing, small profiles, shallow passes. Not hogging.
- The clip: the lid opens, a printed blank goes into the vise, it clamps, the spindle takes an end mill, faces the
  as-printed skin in five passes, swaps tools, parks, and the lid opens.

## e. Fume hoods

- **On the floor: Labconco Protector XStream, 4 ft.**
  - [Labconco's page](https://www.labconco.com/p/protector-xstream-laboratory-hoods): an 18 in (457 mm) sash stop,
    a 325 mm exhaust collar.
  - 1219 x 958 x 1499 mm and about 200 kg, and 440 CFM at 0.08 in static pressure, are from Fisher's and Labrepco's
    listings. Labconco's spec PDF was blocked.
  - The base cabinet and work surface (900 + 32 mm) are estimates.
  - The clip: the sash rises to its stop, air flows in and up the collar, a polished Al coupon goes into Keller's
    reagent and then the rinse, the sash comes down.
- **On a tray: Sentry Air's ductless hood, standard 24 in.**
  - [Sentry Air's page](https://www.sentryair.com/dfhapp.htm): 24 D x 26 W x 25 H in outside (610 x 660 x 635 mm),
    23.5 x 24 x 24 in inside, about 90 lb; a separate blower, 13 x 13 x 14.5 in; 100 fpm with HEPA, 60 with carbon.
  - The 235 mm (9.25 in) front opening is the figure the page gives for its carbon-steel models.
  - It is the only ductless hood found under 856.5 mm. Air Science's Purair Basic is 889 mm tall; Erlab's Captair
    Smart 321 is 1285 mm.
  - Our layout: the filters at the back, a hose over the top to the blower beside it. 715 mm tall with the hose.
- **Two cautions.** A ductless hood returns its air to the room: on a tray, into the VLM. And carbon takes solvent
  vapours, not HF. Keller's reagent belongs in the ducted hood.

## f. Sample storage

- **Our design**, 1760 x 760 x 300 mm, so a tray's right 660 mm stays free for its UPS and dock.
- What it holds:
  - 48 cups and 48 plugs each of 5N Al (silver, in a blue anodized rack) and C10100 Cu (copper colour, in an orange
    rack). Cups and plugs are #222's (`charge.py`). The cups are in the front rows, where a level gripper takes them.
  - 54 capped 20 mL vials (`props.py`); 112 15 mL ICP-MS tubes.
  - A two-drawer cabinet: 96 SEM pin stubs (12.7 mm, carbon tabs on) in the top drawer, 32 polished 1.25 in mounts in
    the lower one. The drawers open 250 mm, over the cups.
  - 20 E8 sub-size bars (`alloy_models`), eight 250 mL powder jars with lids coloured by powder, four labelled bins.
- **`storage_seats()` lists every pocket** (base centres, in the load's frame, drawers closed) for the arm's planner.
- Tube, stub, jar and bin sizes are common ones: estimates.

## g. The Keyence VHX without its monitor

- **The interference.** The monitor was a separate piece set "aside", so it was left out of the VHX's size:
  - The fit check never saw it. On tray C (x 860 mm), the monitor's right edge reached x = 1642 mm in the tray's
    frame, 430 mm past the rim at 1213, into the VLM's side wall.
  - Its silver bar touched the stand's base skirt, about 0.5 mm deep.
  - `interference.py` also found the EA-300 drawn 20 mm into the stand's column (two built-in faults).
- **What the VHX-7000's controller is.** Keyence's
  [model page](https://www.keyence.com/products/microscope/digital-microscope/vhx-7000/models/vhx-7000/) lists it as
  625 W x 460 H x 180 D mm stored, about 12 kg, with the 27 in IPS 4K screen in its own spec table.
  - That size is a 27 in monitor's: **the controller is the monitor**.
  - Interfaces: Gigabit LAN, 6 x USB 2.0, 2 x USB 3.0, DisplayPort out, 1 TB HDD; 430 VA.
  - The head and the EA-300 cable into it, so a separate PC can't take its place.
  - Keyence's page doesn't name the operating system and documents no remote-desktop option.
  - The VHX-X1 that replaced it is the same kind of unit: 635 x 450 x 132 mm, 10.8 kg.
- **The minimum now drawn:**
  - The console is gone.
  - The controller is turned sideways beside the stand, its screen unused. The VHX is now 630 x 625 x 716 mm, not
    about 950 mm wide. Its size counts the controller.
  - A KVM-over-IP box, the PiKVM V4 Mini, sits on top: 120 x 68 x 24 mm, 0.35 kg; HDMI capture up to 1920 x 1200;
    USB keyboard and mouse emulation ([datasheet](https://docs.pikvm.org/v4/v4mini_datasheet.pdf)). It takes the
    DisplayPort output through a DP-to-HDMI adapter and plugs into a USB port. Anyone on the LAN then works the VHX
    from a browser. Nothing is installed on Keyence's controller.
  - The EA-300 now hangs 7 mm clear of the column, on an arm that rides a tilt guide on the column's face.
- **Why not a Windows x86 SBC?** It can't replace the controller. It could only be a remote-desktop client, and that
  needs Remote Desktop on the controller, which Keyence doesn't document. If Keyence will enable it, nothing extra
  is needed. Candidates if one is wanted anyway: LattePanda 3 Delta (125 x 78 x 16 mm board, ships with Windows 10),
  LattePanda Sigma (146 x 102 mm), ASRock Industrial 4X4 BOX-7840U (110 x 117.5 x 48 mm).
- **To check with Keyence:** whether the controller's DisplayPort output can be set to 1920 x 1200 or lower for the
  PiKVM, and whether Remote Desktop can be enabled.
- The `vhx` anchors for `register.py` (the monitor's corners in Keyence's video) are unchanged. They describe the
  video, not the model.

## Interference (`interference.py`, with this module added to its list)

Run on 2026-11-04 without writing `out/interference.json`:

- `vhx`: only the tilt guide and the head's arm, 1 mm, the contact `interference.py` already lists as intended.
  The two built-in faults (EA-300 in the column) are gone.
- `tensile_h`: nothing.
- `hardness`: only touching, under 0.3 mm (the indents on the face, the diamond on the coupon).
- `cnc`: one, the end mill 2 mm into the as-printed skin it is cutting off. That is the cut.
- `glovebox_tray`: only touching (the capper's pad on the lids). Fixed on the way: the outer door slid through the
  vacuum gauge, and the cradle, tipping about the jar's lip, swept through the sled and shelf. The arms now lift it
  70 mm first.
- `fumehood`, `fumehood_tray`, `storage`: checked by eye in PREVIEW stills. Only the sash, the drawers and the air
  puffs move.

`tour.FIT` still has the old 727.5 mm height, so `tour.py` reports the glovebox (810 mm) as not fitting a tray.
