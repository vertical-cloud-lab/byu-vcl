## The alloy workflow: printer, wire EDM, tensile test (round 4)

![The alloy workflow](out/alloy_workflow.gif)

One build plate, from the Aconity MIDI to the wire EDM, then one tensile bar to the Instron. The UR10e rides its
MiR250 along the line's fronts; the rail isn't used. [`alloy_workflow.py`](alloy_workflow.py) is the scene, and
[`alloy_models.py`](alloy_models.py) has its new pieces: the Aconity opened up, the plate and bars, the EDM's fixture
and wire head, and the holders on the MiR.

| | |
|---|---|
| MP4, 1280 × 720, 10 fps, 159 s (round 5; re-render at 15 fps when the runner is free) | [`out/mp4/alloy_workflow.mp4`](out/mp4/alloy_workflow.mp4) (8.9 MB) |
| GIF, 640 × 360, 5 fps | [`out/alloy_workflow.gif`](out/alloy_workflow.gif) (5.1 MB) |
| Stills: the lance, the depowdering box | [`out/alloy_workflow_lance.png`](out/alloy_workflow_lance.png), [`out/alloy_workflow_depowder.png`](out/alloy_workflow_depowder.png) |
| Frame range of every sub-step, and the numbers used | [`out/alloy_workflow.json`](out/alloy_workflow.json) |
| Stills: the cut, the broken bar | [`out/alloy_workflow_cut.png`](out/alloy_workflow_cut.png), [`out/alloy_workflow_still.png`](out/alloy_workflow_still.png) |

![The cut, the EDM drawn see-through](out/alloy_workflow_cut.png)

![The broken bar and the curve](out/alloy_workflow_still.png)

### The steps

1. **The print is done.** Four ASTM E8 subsize bars lie flat on a 170 mm plate, still buried in powder. With them is
   a handling lug for the gripper. The process chamber is drawn see-through. An inset shows an SEM image of the
   lab's AlSi10Mg powder.
2. **Door, suction lance, platform (round 5: no person).** The chamber door opens and the MiR250 rolls up. The arm
   takes a suction lance off a post in front of the printer, right of the chamber, and vacuums the build cylinder
   at floor level, pointing 25° down, in four passes, while the platform rises out of the powder. A pipe along the
   floor takes the powder to the depowdering box's separator. The lance goes back on its post. Loose grains are
   left round the bars and the lug.
3. **The arm takes the plate; the depowdering box.** The platform's clamp lets go. The arm takes the lug, with the
   gripper pointing 30° down, lifts the plate 32 mm and draws it out. Holding it, the MiR moves 1.6 m to the
   depowdering box between the printer and the 68FM-100. The box's door slides up, and the arm sets the plate's
   zero-point stud in a chuck on a horizontal shaft and backs off. The door shuts; under argon the shaft turns the
   plate over and back on a set path while a vibrator on it shakes the grains off, down a hopper into a closed
   bottle. The arm takes the clean plate out and sets it on the MiR's carrier, turned half a turn.
4. **Into the wire EDM.** The MiR drives about 3.7 m from the box to the FANUC. The tank is drained, so its door can drop. The arm
   takes the lug again, from above, and turns the plate on edge. It pushes the plate onto a zero-point receiver on
   an angle plate, bars to the front. The door goes up and the tank fills.
5. **The cut.** It is drawn see-through. The wire runs between its guides, 0.15 mm off the plate's face, and crosses
   the plate. The sparks show where it is inside a bar. Each bar drops 14 mm onto a catch shelf once it is cut
   through. The tank drains and the door drops. The arm takes the first bar by its end, dips it in a cup of
   isopropanol on a stand left of the EDM, pulls it out slowly through the air knife on the cup's rim, and stands it
   in a holder on the MiR (round 5: the rinse and dry).
6. **The tensile test.** The MiR drives to the 68FM-100, and the crosshead rises out of the way. The arm lowers the
   bar into the lower wedge grip, which closes, then lets go and backs off. The crosshead comes down until 40 mm of
   the bar is free between the jaws, and the upper grip closes. Then the pull: the stress-strain curve draws in step
   with the crosshead, to fracture at 14.8 kN. The crosshead backs off 20 mm to show the break.

Every arm move is a straight line of the grasp point solved with the UR10e's IK every frame, or a joint move between
two solved poses (`robot.py`), as in `animate.workflow()`. The moves are not checked for collisions with the
machines; the highest point the forearm or wrists reach is 1642 mm.

### Sources

- **Specimen:** DAL PR #169 (the Aconity MIDI set-up for the Utah build) gives a bar 100 mm long with 10 mm ends,
  a 32 mm reduced section 6 mm wide, and 6 mm thick, printed flat. That is ASTM E8/E8M's subsize sheet specimen:
  L 100, A 32, W 6, C 10, B 30, R 6, G 25 mm. The E8 table was not checked against the standard itself.
- **Plate:** 170 mm across, the MIDI's build platform (DAL PR #169). Utah's page gives "Maximum possible build
  space: Ø 170 mm x H 200 mm". Al 6061, as Utah's plate (DAL PR #169).
- **Aconity MIDI:** #199's model, `lab_models.equipment.aconity_midi()`, with its process chamber split into walls,
  a door and an inside. The chamber is that model's, 609 × 700 × 310 mm outside; with the 15 mm walls drawn here it
  is 280 mm tall inside. The build cylinder sits under the model's beam tube.
- **FANUC ROBOCUT α-C400iC:** data sheet MDS-04386 (FANUC Europe, 2022):
  - maximum workpiece 730 × 630 × 250 mm (730 × 585 × 250 with the automatic door), and 500 kg;
  - X/Y travel 400 × 300 mm, Z 255 mm;
  - wire 0.10-0.30 mm across.

  The brochure lists a "work tank automatic door" option, "that dispenses with the need to completely drain the
  water". So without it, the tank is drained before the door opens, which is what the animation does.
- **Cutting rate:** FANUC gives none for aluminium. GF's CUT AM 500, a wire EDM made for cutting parts off build
  plates, has a "maximum cutting speed of 300 mm2/m" with 0.2 mm wire (MoldMaking Technology, 14 Feb 2020). That
  figure is not specific to aluminium.
- **Instron:** the 68FM-100 and 68SC-2 are `instruments.py`'s models. Instron's 100 kN extended hydraulic wedge grips
  (CP104947) list "Fully-automatic hydraulic actuation" and "Front loading of flat specimens".
- **Stress-strain:** AddUp's AlSi10Mg data sheet, version US-10252023-0129: FormUp 350, 50 µm layers, ASTM E8,
  machined, at least 27 samples. As built, XY:
  - E 72 ± 3 GPa;
  - YS 275 ± 8 MPa;
  - UTS 412 ± 38 MPa;
  - elongation 5 ± 2 %.

  Kempen et al. 2012, Physics Procedia 39:439 (DOI 10.1016/j.phpro.2012.10.059), as built, XY:
  - E 68 ± 3 GPa;
  - UTS 391 ± 6 MPa;
  - elongation 5.55 ± 0.4 %.

  They report that "all samples were seen to break at UTS". EOS's process data sheet for the M 290 at 30 µm gives
  Rp0.2 270, Rm 461 MPa and A 10.2 % (XY), from machined round bars.
- **SEM:** DAL `figures/sem/AlSi10Mg_carbon_adhesive_SEM.png`:
  - taken on BYU's Apreo, at 500x, 5 kV, 0.10 nA, with the ETD (secondary electrons);
  - 829 µm field width, 2 April 2026;
  - posted by Gage Erickson on byu-vcl#48 (comment 4181040112, "AlSi10Mg on carbon adhesive").

  DAL's Genesis proposal captions the slurry image from the same session "stock AlSi10Mg powder (BYU)". The inset
  shows the carbon-adhesive one, because its particles are spread out and easier to see. A copy, 800 px wide, is in
  [`out/alloy_sem_AlSi10Mg_carbon_adhesive.png`](out/alloy_sem_AlSi10Mg_carbon_adhesive.png).
- **MiR250:** 800 × 580 × 300 mm (`props.py`). MiR's spec sheet (a copy at Hartfiel) gives a top speed of
  2.0 m/s and an acceleration of 0.3 m/s² at full payload.

The pages:
- [Utah's AconityMIDI page](https://aerospace.research.utah.edu/?p=67)
- [FANUC α-C400iC data sheet](https://www.fanucamerica.com/uploads/files/data-sheets/ROBOCUT-C400iC-Wire-EDM.pdf)
  and [ROBOCUT brochure](https://www.fanucamerica.com/uploads/files/data-sheets/robocut-product-brochure.pdf)
- [GF CUT AM 500, MoldMaking Technology](https://moldmakingtechnology.com/products/edm-speeds-up-additive-part-separation-preserves-part-integrity)
- [AMF clamping for additive manufacturing](https://www.amf.de/en_us/clamping-systems/additive-manufacturing)
- [Instron 100 kN extended hydraulic wedge grips](https://www.instron.com/wp-content/uploads/2024/07/100-kn-extended-hydraulic-wedge-grips.pdf)
- [AddUp AlSi10Mg data sheet](https://addupsolutions.com/wp-content/uploads/2023/10/AlSi10Mg-Material-Data-Sheet.pdf)
- [Kempen et al. 2012, open access](https://lirias.kuleuven.be/retrieve/2f46a660-a2f3-4ca3-a4eb-934fa2a0cfcb)
- [EOS AlSi10Mg, M 290, 30 µm](https://www.eos.info/metal-solutions/data-sheets/aluminium/pds-eos-aluminium-alsi10mg-eos-m-290-30um)
- [MiR250 spec sheet, Hartfiel's copy](https://www.hartfiel.com/wp-content/uploads/2024/04/MiR250-Specs.pdf)
- [The SEM images on byu-vcl#48](https://github.com/vertical-cloud-lab/byu-vcl/issues/48#issuecomment-4181040112)

### Findings

- **The gripper can't point down inside the MIDI's chamber.** The chamber is about 280 mm tall inside, taking
  15 mm walls. With the plate 18 mm proud of the floor, the grasp point on the lug is 46 mm up. Pointing down, the
  2F-85's grasp point is 155 mm below the flange (`ur_arm.TCP_MM`). The UR10e's wrist 2 axis is another 117 mm up
  (d6). That puts the axis 318 mm over the floor, 38 mm through the roof, before counting its housing. Pointing 30°
  down, the wrist 2 axis is at most 66 mm under the roof, once the plate is lifted. So the plate needs something the
  arm can take from the side: here, a lug printed with the bars.
- **The MiR has to park further out at the printer than at the VLM: 230 mm off the fronts, not 30.** To clear the
  chamber's front, the plate has to come out 435 mm. From 30 mm off, that brings the flange within 264 mm of the arm's
  base axis, and the IK has no solution there; from 230 mm off it stays 460 mm away. The MiR parks 230 mm out at
  every machine, so it drives straight along the line.
- **The bar needs the 68FM-100, not the 68SC-2.** Its 6 × 6 mm section at AddUp's 412 MPa is a 14.8 kN pull; at
  EOS's 461 MPa it is 16.6 kN. The 68SC-2's 2 kN is reached at 56 MPa on this section, below yield. On the 68SC-2, a
  bar would need a section under 4.9 mm², say 3 × 1.5 mm.
- **The cut is about 3390 mm².** That is four bars at 847 mm² each, the bar's outline. At GF's 300 mm²/min it would
  take at least 11 minutes; FANUC publishes no rate.
- **The wire EDM must take the plate on edge.** Its wire is vertical. To cut bars off at their base, the plate's face
  has to be vertical too, with the wire moving parallel to it. A 170 mm plate on edge is well within the FANUC's
  250 mm workpiece height.
- **The test is short at a fast rate.** Kempen et al. tested at 0.4 mm/mm/min. At that rate, 5.6 % strain takes
  8.4 s, about the 8 s shown.

### Caveats

- **Assumed, not documented:**
  - **The zero-point clamps:** in the MIDI's platform, on the MiR's carrier and on the EDM's angle plate. Utah's plate
    is screwed down, and the arm can't unscrew it. AMF sells zero-point pull-stud clamping for post-processing AM
    parts on CNC machines. GF's AMCarrier is reported as the workholding for the CUT AM 500, but its page wasn't
    readable.
  - **The handling lug:** 12 × 30 × 40 mm, at the plate's rim. It makes the build 40 mm tall instead of 6.
  - **The plate's 15 mm thickness.** Plate and parts come to about 1 kg; the UR10e's payload is 12.5 kg.
  - **The door:** it is hinged on the right, so it swings away from the MiR. The model's two clamps are on the left.
- **Drawn, not sourced:**
  - Aconity publishes no drawing of the chamber's inside. The supply cylinder behind the build cylinder, the
    recoater parked at the back, the piston and the powder are layout choices; only the 170 mm sizes are from DAL.
  - The wire head is drawn here. `instruments.wire_edm()`'s own head can't span a plate on edge, so it is hidden.
- **Depowdering (round 5): our design, on a commercial principle.** No source found documents automatic
  depowdering on the MIDI, and Utah's page lists the AconitySIEVE as a separate unit. So:
  - **In the chamber, the arm does what a person does** with an ATEX vacuum: a suction lance (Ø28 × 300 mm tube,
    a 12 mm handle gripped like the lug, assumed) on a post at x = 3420, in reach from the MiR's spot at the
    printer. A floor pipe along the fronts runs to the box. The lance points 25° down because the chamber is
    280 mm tall; at 30°, with a 430 mm tube, the UR10e's wrist would have had to come inside its own base's reach
    limit, so the tube was shortened.
  - **Then a depowdering box**, 420 × 620 × 1540 mm, in the 544 mm the line leaves between the Aconity (to
    x = 4486) and the 68FM-100 (from x = 5030). It works like Solukon's SFM-AT200: the plate clamped on a table
    that turns about one axis on a programmed path, shaken at a variable frequency, in nitrogen or argon. Solukon
    gives parts up to 300 × 300 × 230 mm and 60 kg ([TCT Magazine](https://www.tctmagazine.com/solukon-compact-post-processing-metal-3d-printing/));
    a later version adds ultrasonic excitation ([Metal AM](https://www.metal-am.com/?p=82324)). Solukon publishes
    no outer size, and [3devaluate](https://3devaluate.com/_files/ugd/cf3431_a1fb83966d694d8ea6f16706d573508d.pdf)
    lists its installation space as 2 × 2 × 2 m, so the commercial unit would need the line opened up by about a
    metre. Hence the narrow box: the chuck, shaft, vibrator, hopper and bottle are this model's.
  - For four flat bars the lance does most of the work; the box is what parts with channels or overhangs need.
- **Wet bars (round 5): a dip-and-blow cup.** Isopropanol in a Ø92 cup on a stand in the 410 mm between the
  68SC-2 and the EDM, with an annular air knife on the rim (assumed). No source was found on how fast wet AlSi10Mg
  stains, nor on rinsing wire-cut Al before a tensile test.
- **The depowdering takes 7 s on screen.** No cycle time is published for a plate this size; Solukon's programs
  run for minutes.
- **The curve is not a measurement.** It is a smooth curve through AddUp's four values: elastic at 72 GPa, then
  Voce hardening, s = 244 + 169 (1 - e^(-100 εp)) MPa. That puts 275 MPa at 0.2 % offset and 412 MPa at 5 %, where
  it breaks. The plot says so.
- **The SEM is the lab's stock powder.** It isn't necessarily the lot Utah printed. The inset says "the powder a
  plate like this is printed from", not "this plate's powder".
- **Too small to see:**
  - the 0.25 mm wire, which is drawn 1.6 mm thick;
  - the sparks, which are drawn on the bar's front face, while the real gap is in a 0.3 mm kerf;
  - the bar's 1.4 mm stretch over its 25 mm gauge. The crosshead moves 1.6 times that.
  - The grips' jaws aren't drawn closing: the status line says when they close.
- **The catch shelf** sits under 1 mm from the wire's path. A real cell might use a basket, or leave tabs and break
  them off.
- **The drives are about twice as fast as real.** The animation allows the MiR 1.5 m/s and no ramp: 5.5 m takes
  4.4 s. At MiR's 0.3 m/s² it never gets past 1.3 m/s on that distance, and takes about 8.5 s.
- **The chamber is still open to the air** when the arm reaches in. Whether the MIDI's chamber can be opened before
  the plate is cool, and under what gas, isn't covered here.

### Changes to the shared files I'd suggest (not made)

- `instruments.wire_edm()`: its tour cuts a flat plate with a vertical wire moving across it. That doesn't separate
  parts at their base. Standing the plate on edge, as here, would.
- `instruments.instron_small()`: its specimen is 4 × 1.5 mm = 6 mm². At about 400 MPa that is 2.4 kN, over the
  frame's 2 kN.

### Running it

```bash
xvfb-run -a python3 alloy_workflow.py            # -> out/mp4/alloy_workflow.mp4, out/alloy_workflow.gif, .json, stills
PREVIEW=1 xvfb-run -a python3 alloy_workflow.py  # the last frame of each sub-step -> /tmp/preview_alloy_workflow.png
```

The opened Aconity is tessellated once, in about 10 s, and cached in `.cache/alloy_aconity_<hash>.pkl`. The full
render took 38 minutes on the shared 4-core runner.
