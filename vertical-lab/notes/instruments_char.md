## Round 4: more characterization (`instruments_char.py`)

Four more models, in [`instruments_char.py`](../instruments_char.py). `tour.py` finds them through its `REGISTRY`:
- an array of six OpenFlexure microscopes on one sub-tray;
- a Keyence digital microscope with its laser elemental analyzer;
- a desktop XRF;
- a sieve shaker for the atomizer's powder.

| Instrument | Model | What the animation shows | GIF, MP4 | Size W × D × H (mm) | Where |
|---|---|---|---|---|---|
| Six reflection microscopes on one sub-tray | OpenFlexure: 4 × v7 + 2 × Delta Stage | Slides go in, front row then back row; all six stages scan; the plate lifts out by its handles, then goes back | [GIF](../out/instruments/openflexure_array.gif), [MP4](../out/mp4/instruments/openflexure_array.mp4) | 784 × 524 × 177 as modelled; plate 700 × 510 | tray D, in place of the two freestanding ones |
| Digital microscope with laser elemental analysis (LIBS) | Keyence VHX-7000 + EA-300 on the VHX-S750E stand | A mounted coupon goes on the stage; the free-angle head tilts; the focus sweeps (depth composition); the EA-300 fires and a plasma flashes; a LIBS spectrum appears, labelled illustrative | [GIF](../out/instruments/vhx.gif), [MP4](../out/mp4/instruments/vhx.mp4) | stand and head 606 × 461 × 655 as modelled; controller 625 × 180 × 460, published | tray G, if there is a slot (below) |
| Benchtop EDXRF | Bruker S2 PUMA Series 2, XY Autochanger | The lid opens; a powder cup with prolene film goes into the 20-position tray; the lid closes; the changer takes the cup to the measuring position; the beam is drawn see-through; a spectrum appears, labelled illustrative | [GIF](../out/instruments/xrf.gif), [MP4](../out/mp4/instruments/xrf.mp4) | 670 × 710 × 610, published | tray G |
| Sieve shaker | Retsch AS 200 control, with the 8 in stack DAL bought | The rePowder's container is tipped into the No. 60; the clamping lid goes over the rods and its knobs turn; the stack shakes, see-through, and each size class falls to the cloth that stops it; the fractions are listed | [GIF](../out/instruments/sieve.gif), [MP4](../out/mp4/instruments/sieve.mp4) | 417 × 384 × 212 base, published; 567 tall with the stack and rods | beside the rePowder (below) |

### The OpenFlexure meshes, rebuilt

The runner had no OpenFlexure meshes, so `tour.load()` skipped both microscopes. They are now rebuilt with
[`openflexure/README.md`](../openflexure/README.md)'s pipeline, into `.cache/openflexure/{v7,delta}/` here and in the
main checkout. Every part's bounding box matches `openflexure/manifest.json` exactly. Four parts differ slightly in
triangle count: each motor has 4 more, the delta base 66 more, and the delta casing has 244,648 against 268,038
(its mesh isn't closed).

What the README doesn't say, and cost time:
- **The OpenSCAD AppImage needs `libEGL.so.1` and `libOpenGL.so.0`.** This Ubuntu runner has neither. Taking
  `libegl1` and `libopengl0` with `apt-get download` and `dpkg -x` into `/tmp`, and setting `LD_LIBRARY_PATH`, works
  without installing anything.
- **The v7's `rendering/librender/rendered_main_body.stl` has to be made first.** Run
  `rendered_main_body.scad` on its own. Without it, `main_body`, `main_body_full` and `xy_stage` come out empty.
- **Keep the `-D` quoting.** `delta_jobs.txt` and `helper_jobs.txt` carry `-D 'PART="casing"'`. Run them through
  `xargs` without `-d '\n'` and the quotes are eaten, so every part comes out empty.
- **Three delta exports aren't in the job lists:** `base_raspi_sangaboard.stl`, `fl_cube.stl` and
  `sample_clip_local.stl`. Each is a plain export of `base_raspi_sangaboard.scad`, `fl_cube.scad` and
  `clip_part.scad`.
- **The delta base can crash.** Run alongside other exports, OpenSCAD segfaulted after 76 s, in a CGAL Minkowski
  fallback. Run alone, it finished in 78 s.

### The OpenFlexure array

- **The mix: four v7 and two Delta Stages.**
  - The v7 is OpenFlexure's current microscope.
  - The Delta Stage keeps its optics still and moves the sample in x, y and z. Its makers say that makes it
    "particularly suited to more complex imaging (phase, reflection, fluorescence microscopy)" (the Delta Stage
    repository's `docs/index.md`).
  - Both run the same reflection optics and OpenFlexure's software. The Delta needs only the "SangaStage (Delta)"
    stage geometry setting.
  - Two Deltas let the lab compare the designs on the same coupons. Six of one kind is the choice once that's settled.
- **The sub-tray** is designed here. OpenFlexure publishes nothing for an array.
  - **Plate:** 1/4 in (6.35 mm) cast aluminium tooling plate, 700 × 510 mm. That is 5.6 kg after the pockets
    (2.70 g/cm³, from the model's volume).
  - **Pockets:** each microscope stands in a 2 mm pocket shaped to its own footprint: the convex hull of the
    underside of the v7's stand or the Delta's base, in OpenFlexure's mesh, plus 1 mm. So each goes back in the same
    place.
  - **Cabling:** one duct between the rows and one along the back edge run to a hub box with a power supply and a
    network switch. The tray's power feeds the hub. The ducts and hub are stand-ins, sized here.
  - **Handles:** one on each end. They are lift points for a person, or for the arm with a two-point lift tool.
- **What it weighs is open.** OpenFlexure publishes no mass for either microscope. The UR10e's payload is 12.5 kg,
  and the plate alone is 5.6 kg.
- **A tray carries power, not data.** The hub's uplink has to be Wi-Fi (each Pi 4 has it) or a cable at the
  opening.
- **The scan is small.** The flexure stages travel ±6 mm. At the array's scale that's a few pixels, so the clip
  shows the raster but doesn't make it obvious.

### Keyence VHX-7000 with the EA-300

Sources: Keyence's VHX-7000N brochure, KA1-1099 (©2022, pp. 34–38, mirrored by the University of Pittsburgh), and
Keyence's EA-300 model page.

| | Value | Source |
|---|---|---|
| EA-300 | 280 W × 210 D × 375 H mm with its lens stored; about 7.2 kg | EA-300 model page |
| Laser | Nd:YAG, 355 nm, Class 1; 10 µm spot (typ.) | EA-300 model page |
| Elements | H to U | EA-300 model page |
| EA-300 optics | Its own 3.19 MP camera; 300–1000× through a reflective objective, 25 mm working distance | EA-300 model page |
| EA-300 power | From the VHX controller's camera port; no box of its own | EA-300 model page |
| EA-compatible stands | VHX-S750E, S770E and S700 | Brochure, configuration diagram |
| EA-compatible lenses | VH-ZST (20–2000×) and VH-Z00R/Z00T | Brochure, configuration diagram |
| How the zoom lens attaches | The VH-ZST hangs off the EA-300 through lens joint OP-88660 | Brochure, configuration diagram |
| VHX-S750E | XYZ motorized; XY ±20 mm; θ ±90°; stage top 171 × 168 mm; focus Z 49 mm; 23.8 kg; 5 kg load | Brochure p. 38 |
| VHX-7000 controller | 625 W × 460 H × 180 D mm stored; about 12 kg | Brochure p. 38 |
| 27 in 4K screen | 596.7 × 335.7 mm | Brochure p. 38 |

What is estimated, and why:
- **The stand's base and column are scaled from photos.** Keyence does publish the S750E's outline, on the model's
  public [Dimensions tab](https://www.keyence.com/products/microscope/digital-microscope/vhx-7000/models/vhx-s750e/dimensions/) (found in round 5's fixes). The drawing gives:
  - 674 mm tall with the head upright, to the top of its cable hook;
  - 530.5 mm deep from the rear knob to the base's front, and the stage 37 mm further forward;
  - a 286 mm wide base, the head swinging 219.3 mm past it tilted 60° left and 272.5 mm tilted 90° right;
  - the stage top 258.5 mm up, 50 mm of stage Z and 49 mm of focus, a ϕ357 mm stage rotation range.

  The model is still the one fitted to Keyence's video ([refine_vhx.md](refine_vhx.md)): a 290.7 mm base (1.6 % wide
  of the drawing), its stage top at 225 mm (33.5 mm low), and its depths guessed. Refitting to the drawing is next.
- **The screen is drawn built into the controller.** That is an inference: the screen is in the controller's own
  spec table, and 625 mm fits a 27 in panel.
- **The head's tilt range is third-party.** Keyence's text gives none. Georgia Tech's facility page says −60° to
  +90° for the VHX-7000; the clip tilts 35°.
- **Where the VH-ZST sits beside the EA-300 is a guess.**

Things to know:
- **It fits a tray.** The stand and head stand 655 mm, against Kardex's 727.5 mm.
- **The clip draws the laser red and much wider than it is.** The beam is UV and its spot is 10 µm.
- **The spectrum is illustrative.** The line positions are NIST's (Mg II 279.6/280.3, Si I 288.2, Cu I 324.8/327.4,
  Fe I 372.0/373.5, Al I 394.4/396.2 nm); the intensities are made up. The panel says so.
- **The VHX-7000 is discontinued.** Keyence offers the VHX-X1 in its place, whose S700 stand is also EA-compatible.
- **DAL already counts on one.** Its proposal lists a "Keyence VHX-7000 Optical Microscope (BYU)", and its PR #52
  review asked for its specs. The EA-300 is how that microscope would add spot chemistry.

### Desktop XRF: Bruker S2 PUMA Series 2 with the XY Autochanger

Source: Bruker's S2 PUMA Series 2 specifications, via its distributor DKSH.

| | Value |
|---|---|
| Size and mass, XY Autochanger | 67 × 71 × 61 cm (W × D × H), 108 kg |
| Other versions | single-sample 37 cm tall, 87 kg; Carousel and Automation 57 cm, 130–132 kg |
| Tray | 20 removable positions; cups up to 40 mm across and 38 mm tall |
| Tube | Pd or Ag anode; 50 W; 50 kV max |
| Detector | HighSense silicon drift detector; Na to Am (C to Am for the LE version) |
| Atmosphere | Air, vacuum, He or N2; a "Helium mode with reduced pressure" for loose powder |

Why it, of the six looked at:
- **It fits a tray, closed:** 610 mm, against Kardex's 727.5 mm.
- **It takes powder cups,** in a 20-position tray.
- **It names a mode for loose powder.**
- **It has an automation version.** That is the only one of the six with a published "interface to conveyor belt or
  robot arm link-up".

The rest:
- **Rigaku NEX DE VS:** 356 × 351 × 260 mm and 27 kg. It is smaller, but its changer's number of positions isn't
  published.
- **Thermo ARL QUANT'X:** its lid opens to 915 mm.
- **Hitachi EA1000VX:** 520 × 600 × 445 mm. Those figures come from a search extract only.
- **SPECTRO XEPOS:** no official dimensions found.
- **Bruker M4 TORNADO:** a micro-XRF mapper (815 × 680 × 580 mm, 130 kg) rather than a cup analyser.

Things to know:
- **The lid's open height isn't published.** Drawn 35° open on a rear hinge, its front edge rises to about 905 mm
  (an estimate). That is above the roughly 844 mm between a presented tray's floor and the opening's header. If the
  real lid is that big, the arm can open it only once the tray is out, under full tray extraction, or on a bench.
  Ask Bruker for the open height. Round 5's fixes looked again and found none: the Series 2 brochure (DOC-B80-EXS015
  V7, 2026), the product page and the automation flyers give only the closed 670 × 710 × 610 mm, 108 kg and 600 VA.
  Bruker's manuals are behind its support portal; its brochure gives info.baxs@bruker.com.
- **The layout is from Bruker's photos and is approximate:** the sloped front, the lid over the tray, the touch screen
  on the right.
- **It measures from below,** like most benchtop EDXRF. The cup sits film side down over the window, so the film
  carries the powder.
- **The spectrum is illustrative:** real Kα energies (Mg 1.25, Al 1.49, Si 1.74, Mn 5.90, Fe 6.40, Cu 8.05,
  Zn 8.64 keV) and Ag Lα from an Ag tube, with made-up heights. The panel says so.
- **DAL's issue #102** (a TMS abstract on compositional analysis of AM powders and prints) is the use.
  - The standard S2 PUMA covers Na to Am, so it covers Mg, Al and Si in the Al alloys. Bruker lists an LE version
    from C.
  - DAL's `edison-trajectories/automated_characterization.md` notes that light elements are hard for EDS and XRF,
    and points to glow-discharge spectroscopy for C, N and O.

### Sieve shaker: Retsch AS 200 control

Source: Retsch's AS 200 control page.

| | Value |
|---|---|
| Size and mass | 417 W × 212 H × 384 D mm; about 35 kg |
| Motion | 3-D throwing motion; amplitude 0.20–3.00 mm; 1.0–15.1 g |
| Range | 20 µm to 25 mm |
| Load | up to 3 kg of sample; 6 kg of stack |
| Sieves | 100, 200 and 203 mm (8 in); up to 11 full-height fractions; stack up to 620 mm |
| Clamping lids | "standard" or "comfort" |

**The stack is the one DAL bought and ordered** (DAL PR #175, `docs/sieve-order.md`):
- **Bought** on ME Order 13553 (McMaster, 304 stainless, 8 × 2 in): cover, No. 60, No. 230 and pan.
- **On order:** No. 100, No. 140 and No. 325.
- **Geometry:** DAL's `sieving/viz3d/model.py` profiles. The frames are 203.2 mm and 2 in deep, which is also what
  each sieve adds to the stack.
- **The cover stays off.** The AS 200's own clamping lid closes the top, so McMaster's cover isn't used.

What stays on each sieve:

| Sieve | Fraction |
|---|---|
| No. 60 | > 250 µm |
| No. 100 | 150–250 µm |
| No. 140 | 106–150 µm |
| No. 230 | 63–106 µm |
| No. 325 | 45–63 µm |
| pan | < 45 µm |

What that gives each process:
- **LPBF, 20–63 µm:** the No. 325 and the pan. There is no 20 µm sieve, and DAL found under 20 µm is about 0.05 % by
  mass in the NAB lot.
- **DED, 45–105 µm** (DAL PR #220, the Mines X2's cuts): the No. 230 and No. 325, which is 45–106 µm.
- **DED, 100–200 µm:** close to the No. 140 and No. 100, which is 106–250 µm. A No. 70 (212 µm) would make it
  106–212 µm.

How much powder lands in each fraction is an example, not data. The clip and the fractions panel say so.

**No sieve shaker found is sold for robot loading.**
- None was found from Retsch, Fritsch, Haver or Gilson. That doesn't prove none exists.
- **Nearest:** Fritsch's ANALYSETTE 3 PRO, whose electric "TorqueMaster" tensions the stack, would take the
  hand-tightened knobs out of the job. SIEBTECHNIK TEMA's ASM has quick-release fasteners. I could check neither
  one's dimensions: Fritsch's came only from a distributor's search extract, and none were found for the ASM.
- **Prior art:** an IROS 2025 paper (arXiv 2509.14531) has two arms working a vibratory sieve shaker's lid.
- **What the clip shows instead:** what an arm would do with the AS 200. It tips the container, carries the lid over
  the rods and lowers it, and turns the two knobs.

**Why the AS 200 and not the Ro-Tap DAL plans to buy used:**
- **Height:** the AS 200's base is 212 mm, so with this stack and its rods it stands 567 mm, under Kardex's 727.5 mm.
- **Nothing over the stack:** the Ro-Tap RX-29 (71 × 54 × 64 cm, 180 lb, about 85 dB) swings a tapping arm over
  it.
- **DAL's reason still holds:** ASTM B214 and ISO 4497 call for a rotary-tapping shaker for the analysis itself. A
  Ro-Tap stays the reference method; the AS 200 is for the cut.

The look is estimated: the housing's proportions, the sloped panel and the lid's crossbar are from Retsch's photos.
The rePowder container is DAL's assumed Ø130 × 228 mm can. Its size hasn't been measured.

### Where they go

Tray D (R1) today is the SEM at x = −760 mm, the XRD at 60, and the v7 and Delta at 560 and 800, both at y = −150
(`line.TRAY_LOADS`).

**The array on tray D.** Put the array in place of the two freestanding microscopes: `("openflexure_array", 792.0,
-148.0)`.
- **Width:** the XRD's right edge is at x = 370 and the rim at 1213, leaving 843 mm. The array is 784 mm wide, so it
  leaves about 30 mm each side.
- **Depth:** the array is 524 mm deep, so it spans y −410 to 114, inside the rim's ±420.
- **Reach:** the front row is at the opening edge. The back row is about 550 mm in, inside the UR10e's 800 mm. The
  far right end may be at the edge of the 83 % of the tray `reach.json` covers.

**A seventh tray, G, for composition, if the Shuttle has a free slot.** Round 2 used R1, R4 and F2 for D–F, and I
don't know whether Kardex's configuration leaves another.
- **What goes on it:** the VHX with its controller, and the S2 PUMA.
- **Width:** the VHX's stand and head are 606 mm wide, the controller behind them 625 mm, and the XRF 670 mm. With
  gaps that is about 1.4 m of the 2.43 m.
- **Height:** all are under 727.5 mm.
- **Mass:** the XRF is 108 kg, the stand 23.8 kg, the EA-300 7.2 kg and the controller 12 kg. That is about 150 kg,
  under the light tray's 502 lb (228 kg).

**If there's no free slot:**
- **The VHX** fits the right of tray F: 678 × 840 mm is free there, with the stand in front and the controller
  behind it. But F carries the polisher and the 650 °C furnace, and neither is a good neighbour for a microscope.
- **The XRF** would then stand on a bench at the line. It needs no services but power.

**The sieve shaker beside the rePowder, not in the VLM.** It fits a tray (567 mm), but:
- **The dust:** Al powder from 2 to 63 µm is among the most ignitable metal dusts. DAL's sieve note asks for bonding,
  grounding and local extraction, or an inert glovebox. A VLM tray is an enclosed, ungrounded-by-design space for
  that.
- **The route:** the powder's route is atomizer → sieve → jar. All three are left of the VLM, beside the glovebox.
- **Inside the glovebox?** The box is 928 mm tall, so the shaker fits inside. But it would be loaded through the
  gloves, since the arm stays outside. The 381 mm antechamber passes 8 in sieves but not the 417 × 384 mm shaker, so
  it would go in once, through the box.

### Caveats

- **The spectra are illustrative.** Both the LIBS and the XRF spectra are; the line positions are real and the
  heights made up. Each panel says so on screen.
- **The panels are each instrument's `Instrument.overlay`** (round 5's fixes), which `tour.tour_one` draws over
  every frame of that instrument's clip, at the opacity of its `readout` piece. Until round 5 this module wrapped
  `scene.Scene.overlay` on import instead, keyed on the scene's name. The three clips render pixel-identical either way.
- **`CharInstrument` subclasses `Instrument`.** Its `aside` pieces stay out of the size and the framing, but
  keep their place in the hero still. They are the container, the VHX controller and the readouts.
- **Display trouble.** Under the load of five agents, `xvfb-run` on this runner sometimes gave VTK a "bad X server
  connection". That happened on several display numbers, not just 101. A retry fixed it each time.
- **Placing them in `line.py`.** Outside the tour, a `tour.Rig` starts every joint at `v0`. The slides, cups and
  powder then hang at the start of their paths, as the XRD's holder does today. Put the props in place first, as
  the tour's hero still does: `rig.move({k: (None, 1.0) for k in inst.props})(1.0)`.
