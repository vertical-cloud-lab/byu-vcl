# Lab punch list: small physical items still open

Compiled on 2026-10-20 for [#288](https://github.com/vertical-cloud-lab/byu-vcl/issues/288) from every issue, PR and doc in byu-vcl, powder-doser, caliber, robot-arms,
tensegrity-optimization, digital-alloy-lab, custom-induction-furnace, streamingLambda, structural-alloy-sdl-workshop
and .github (about 470 issues and 300 PRs). It covers things someone has to fix, mount, label, buy or move in the lab
itself. Software, papers and analysis are left out, and so is anything a later comment shows was done.

- **(check)** means the record doesn't say whether it was done. Look in the lab before acting.
- **$** means it needs a purchase. Per [#264](https://github.com/vertical-cloud-lab/byu-vcl/issues/264) (2026-10-10) the equipment line stays unspent this year, so most of
  these wait unless they can't. Most items here cost nothing.
- Owners are given where an issue names one.
- Tick an item off with a date when it's done, or delete it once its source issue closes.

The lab is CB154 unless a section says otherwise. The atomizer SOP, equipment list and manual notes cited below are
not on `main` yet. They are on [PR #276](https://github.com/vertical-cloud-lab/byu-vcl/pull/276)'s branch, linked at commit `8981f5c`.

## 1. Atomizer enclosure exit: coats, gloves, mats, strips

The #288 example. The coat hooks from [#22](https://github.com/vertical-cloud-lab/byu-vcl/issues/22) went up behind the room door on 2026-03-12, before the enclosure was
built. Nothing hangs at the enclosure yet.

- [ ] **Put hooks for the ESD coats and wrist straps *inside* the strip curtain, beside the strips but not in them.**
  There are two Portwest ESD coats from the machine's crate, plus a third Bartosz said he'd bring. Taking a coat off under
  the exhaust keeps a loaded coat from crossing the line. Branded coats hang outside, well clear of the strips
  ([#32](https://github.com/vertical-cloud-lab/byu-vcl/issues/32), 2026-09-17).
- [ ] **Add a lidded glove bin inside the strips,** so dirty gloves stay inside too ([#32](https://github.com/vertical-cloud-lab/byu-vcl/issues/32)).
- [ ] **Lay tacky mats across the strip exit, more of the mat on the inside, and keep refill pads (check).** This was
  Bartosz's one addition on the [9/17 call](meetings/2026-09-17-repowder-install/transcript.md) (15:07). The SOP lists
  the mats, but nothing confirms they're down ([#124](https://github.com/vertical-cloud-lab/byu-vcl/issues/124), [#198](https://github.com/vertical-cloud-lab/byu-vcl/issues/198)).
- [ ] **Check the strip curtain:** static-dissipative PVC (10⁶–10⁹ Ω/sq), header rail bonded to ground, about 50 %
  overlap, and strips that reach the floor. Plain clear PVC charges up every time someone pushes through, and strips
  can be swapped one at a time. $ if swapped ([#32](https://github.com/vertical-cloud-lab/byu-vcl/issues/32)).
- [ ] **Hold a tissue at the strips to check that air flows *in*.** If the enclosure isn't under negative pressure,
  parting the strips pushes powder out. It takes ten seconds ([#32](https://github.com/vertical-cloud-lab/byu-vcl/issues/32)).
- [ ] **Count wrist straps and coats.** On 2026-06-15 only one antistatic wrist band was in the crate, against two on
  the packing list. Three coats means no spare, and a Portwest AS10 is about $47. $ ([#124](https://github.com/vertical-cloud-lab/byu-vcl/issues/124), [#32](https://github.com/vertical-cloud-lab/byu-vcl/issues/32))
- [ ] **Finish the hand-wash and eye-rinse sink on the south wall, test it, and start a flush log (check).** The
  [2026-09-01 construction video](https://github.com/vertical-cloud-lab/byu-vcl/blob/8981f5c/atomizer-training/notes/groupD.md)
  shows the sinks still waiting on their plumbing. The SDS says to wash hands after powder work, and [#18](https://github.com/vertical-cloud-lab/byu-vcl/issues/18) wants the
  eye-rinse flushed monthly (weekly is better) with the area in front kept clear. Close [#18](https://github.com/vertical-cloud-lab/byu-vcl/issues/18) once it works.
  Owner: Dave Laws.

## 2. Atomizer station

- [ ] **Bolt the bench vise to a sturdy bench, or hold it down with two heavy C-clamps.** The stack is currently
  torqued while kneeling on the floor mat ([#265](https://github.com/vertical-cloud-lab/byu-vcl/issues/265)). Owner: Dave L. / Gage.
- [ ] **Keep a metric tool set at the machine, with 17 and 18 mm wrenches and metric Allen keys, and get the 18 mm
  torque-wrench tip that didn't ship.** On Oct 2, tools were borrowed from the PSC twice. Still missing from the
  manual's workshop list: a 155–230 hook wrench, a plastic or rubber hammer, metric taps with a handle, and
  penetrating oil. $
  ([SOP, lessons from Oct 2](https://github.com/vertical-cloud-lab/byu-vcl/blob/8981f5c/atomizer-training/sop.md#lessons-from-the-first-unsupervised-run-oct-2),
  [equipment](https://github.com/vertical-cloud-lab/byu-vcl/blob/8981f5c/atomizer-training/equipment.md))
- [ ] **Fix the chilled-water fitting that leaks under the atomizer, and keep cords out of the drip path.** Water was
  seen on 9/29, and the fitting leaked at the start and end of the Oct 2 run. The SOP's troubleshooting table also has
  "water dripping on a cord" ([#222](https://github.com/vertical-cloud-lab/byu-vcl/issues/222), [SOP](https://github.com/vertical-cloud-lab/byu-vcl/blob/8981f5c/atomizer-training/sop.md)).
- [ ] **Reprint the transducer cable holder stronger, with room for the cooling tubes.** The ultrasonic cable carries
  about 1000 V and has to stay off the floor. The current holder "works great", but Ronnie expects it to break
  ([#256](https://github.com/vertical-cloud-lab/byu-vcl/issues/256), [PR #257](https://github.com/vertical-cloud-lab/byu-vcl/pull/257)). Owner: Ronnie.
- [ ] **Make a set-down spot for the transducer:** a thick foam pad, caution tape on the housing, and the cover kept
  on. A repair costs about 2,000 ([#265](https://github.com/vertical-cloud-lab/byu-vcl/issues/265)).
- [ ] **Label every ultrasonic plate with its alloy and give each one a labelled slot.** The Oct 2 run began by
  searching old videos to work out which plate was which
  ([SOP](https://github.com/vertical-cloud-lab/byu-vcl/blob/8981f5c/atomizer-training/sop.md#lessons-from-the-first-unsupervised-run-oct-2)).
- [ ] **Have a grounded metal container and dry sand ready before the first HEPA change.** The HEPA is changed about
  every 2 months, and runs began on 9/29, so the first change is due around late November. A used filter can
  self-ignite. A grounded steel tray for powder work is also still unchecked on the manual's list. $
  ([manual notes](https://github.com/vertical-cloud-lab/byu-vcl/blob/8981f5c/atomizer-training/manual.md),
  [#126](https://github.com/vertical-cloud-lab/byu-vcl/issues/126), [PR #284](https://github.com/vertical-cloud-lab/byu-vcl/pull/284))
- [ ] **Post a printed operator checklist and the safety rules at the machine.** The manual requires it (8.1,
  point 15). While there, check that the light at the machine is at least 500 lux without glare, using a phone lux
  app ([manual notes](https://github.com/vertical-cloud-lab/byu-vcl/blob/8981f5c/atomizer-training/manual.md)).
- [ ] **Wall-mount the Class D extinguisher on its bracket within reach of the atomizer, and set up the inspections
  the manufacturer suggests.** [#19](https://github.com/vertical-cloud-lab/byu-vcl/issues/19) left it on the floor until a spot was chosen, and nothing records it being
  mounted. The manual also asks for an electrical-fire extinguisher within reach, so check one is nearby. Owner: Dave
  Laws.
- [ ] **Chain or rack the argon cylinder (check), and post the two-cylinder limit in the booth.** Rack options are in
  [#41](https://github.com/vertical-cloud-lab/byu-vcl/issues/41). The safety office's ruling: at most two argon or nitrogen cylinders, not manifolded, no dewar, and a
  spare counts toward the two
  ([lab safety page](https://github.com/vertical-cloud-lab/byu-vcl/blob/8981f5c/SOP/lab-safety.md), [PR #271](https://github.com/vertical-cloud-lab/byu-vcl/pull/271)).
- [ ] **Build a laser fixture that seats where the sealing pin goes and shows where the melt will land on the plate**
  ([#198](https://github.com/vertical-cloud-lab/byu-vcl/issues/198), [digital-alloy-lab#111](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/111)).
- [ ] **Mount a camera above the HMI, and put anti-glare film on the HMI and generator displays** ([#221](https://github.com/vertical-cloud-lab/byu-vcl/issues/221)).
- [ ] **Order more chest cams and phone magnet rings for recording runs.** $ ([#222](https://github.com/vertical-cloud-lab/byu-vcl/issues/222))

## 3. Enclosure air: dehumidifier, monitor, electronics

- [ ] **Check that the dehumidifier's MERV 13 filter is in, replace it around November, and keep spares.** The
  2026-09-01 video shows the unit "with the filter gone" ([#42](https://github.com/vertical-cloud-lab/byu-vcl/issues/42)). Owner: Gage.
- [ ] **Get facilities to fit the dehumidifier's on/off switch (check)** ([#42](https://github.com/vertical-cloud-lab/byu-vcl/issues/42), 9/25). Owner: Barry.
- [ ] **Confirm the condensate reaches the drain, and connect or remove the idle pump.** The pump was unplugged on
  9/29 because "the pump isn't connected to anything" ([#42](https://github.com/vertical-cloud-lab/byu-vcl/issues/42)).
- [ ] **Move the AirGradient out of the powder zone:** to the exhaust, a seam, or just outside the strips. Or have EHS
  agree to it staying inside. [#219](https://github.com/vertical-cloud-lab/byu-vcl/issues/219) recommends against an unrated, fan-driven sensor inside. It has been inside
  since 9/29, so the room itself has no reading ([PR #247](https://github.com/vertical-cloud-lab/byu-vcl/pull/247)). A second unit for the room or the lab entrance is in
  [#219](https://github.com/vertical-cloud-lab/byu-vcl/issues/219) and [#35](https://github.com/vertical-cloud-lab/byu-vcl/issues/35). $ for the second unit.
- [ ] **Ask EHS for a dust-hazard review of the enclosure.** Until then, keep power strips, phones and loose cords out
  of the powder zone ([#219](https://github.com/vertical-cloud-lab/byu-vcl/issues/219) and its
  [write-up](https://github.com/vertical-cloud-lab/byu-vcl/blob/409bf14/docs/powder-enclosure-ignition-sources.md)).

## 4. Powder storage, chemicals and waste

- [ ] **Finish turning the storage cabinet into a desiccant dry box, with small sealed jars (about 15 mL) and
  non-indicating desiccant or 3A sieve packets.** Whether silica gel can contaminate the powders is still open in
  [#230](https://github.com/vertical-cloud-lab/byu-vcl/issues/230) ([#30](https://github.com/vertical-cloud-lab/byu-vcl/issues/30), [#222](https://github.com/vertical-cloud-lab/byu-vcl/issues/222),
  [SOP](https://github.com/vertical-cloud-lab/byu-vcl/blob/8981f5c/atomizer-training/sop.md)).
- [ ] **Keep an SDS binder (or USB stick) and a chemical inventory in the lab (check).** The College plan requires both. The
  repo holds only three SDSs: AlSi10Mg, Al 1100 wire and McMaster silicon. Missing: fumed silica, Fisher silicon,
  BaCl₂, Na₂SO₄, argon, IPA, and the ammonium sulfide and lead nitrate for [#279](https://github.com/vertical-cloud-lab/byu-vcl/issues/279)
  ([CHP p. 9](../byu-engineering-lab-safety-plan-chemical-hygiene-plan-2024.pdf), [powder-doser#141](https://github.com/vertical-cloud-lab/powder-doser/issues/141)).
- [ ] **Label secondary containers (powder jars and bags) with the product name and hazards, not only the run ID (check).**
  The College plan requires it, and Risk Management has a label maker on its site
  ([CHP p. 9–10](../byu-engineering-lab-safety-plan-chemical-hygiene-plan-2024.pdf)).
- [ ] **Check that shelves holding chemicals or powders are secured to the wall, with nothing above shoulder height**
  ([CHP p. 9](../byu-engineering-lab-safety-plan-chemical-hygiene-plan-2024.pdf)).
- [ ] **Before the sulfide work in [#279](https://github.com/vertical-cloud-lab/byu-vcl/issues/279): a flammables cabinet, a spill kit, and a working eyewash.** CB154 has no
  fume hood, so stock solutions get made in the Dillon lab hood ([#195](https://github.com/vertical-cloud-lab/byu-vcl/issues/195)). $ M ([#31](https://github.com/vertical-cloud-lab/byu-vcl/issues/31), [#279](https://github.com/vertical-cloud-lab/byu-vcl/issues/279)). Owner:
  Timothy.
- [ ] **Get chemical-waste containers registered to CB154 with Risk Management.** Use separate labelled waste for lead
  and sulfide, for BaCl₂ wipes (D005), and for metal-powder wipes ([#231](https://github.com/vertical-cloud-lab/byu-vcl/issues/231), [#279](https://github.com/vertical-cloud-lab/byu-vcl/issues/279), [powder-doser#141](https://github.com/vertical-cloud-lab/powder-doser/issues/141)). Owner:
  Jarrett, Timothy.

## 5. Powder doser (back in CB154 since 2026-10-05)

- [ ] **Choose and set up the CB154 spot for loading metal and fine powders.** The [powder-doser#141](https://github.com/vertical-cloud-lab/powder-doser/issues/141) safety guidance assumed
  a fume hood, and the doser has now left both hoods ([powder-doser#144](https://github.com/vertical-cloud-lab/powder-doser/issues/144)). M
- [ ] **Merge the powder-handling safety doc and post its checklist at the doser.** It exists only on branch
  [`claude/issue-141-20260807-1840`](https://github.com/vertical-cloud-lab/powder-doser/blob/claude/issue-141-20260807-1840/docs/powder-handling-safety.md),
  with no PR ([powder-doser#141](https://github.com/vertical-cloud-lab/powder-doser/issues/141)).
- [ ] **Re-level and calibrate the A&D balance in its new spot, using PSC calibration weights.** Set `p-on` to 1, and
  power the rig from an unswitched, strain-relieved strip, because a nudged barrel jack or a switched strip silently
  drops it to standby ([powder-doser#157](https://github.com/vertical-cloud-lab/powder-doser/issues/157), [powder-doser#148](https://github.com/vertical-cloud-lab/powder-doser/issues/148), [powder-doser#138](https://github.com/vertical-cloud-lab/powder-doser/issues/138)). Owner: swcharles.
- [ ] **Replace the cardboard draft cage, now propped on a graduated cylinder, with a taller clear box that sits
  flat** ([powder-doser#141](https://github.com/vertical-cloud-lab/powder-doser/issues/141)).
- [ ] **Ground the crucible and funnel, and consider an ionizer at the balance** ([powder-doser#84](https://github.com/vertical-cloud-lab/powder-doser/issues/84), [powder-doser#117](https://github.com/vertical-cloud-lab/powder-doser/issues/117)).
- [ ] **Label every auger with an ID, its powder and its fill mass** ([powder-doser#134](https://github.com/vertical-cloud-lab/powder-doser/issues/134), [powder-doser#186](https://github.com/vertical-cloud-lab/powder-doser/issues/186)).
- [ ] **Get a desiccator and storage bags for the doser powders, and keep air-exposed powder apart from sealed stock.**
  The doser powders currently share a cabinet with the food-safe powders. Add a temperature and humidity logger at the
  doser while you're at it. $
  ([candidate powders](https://github.com/vertical-cloud-lab/powder-doser/blob/main/docs/candidate-powders.md),
  [powder-doser#116](https://github.com/vertical-cloud-lab/powder-doser/issues/116))
- [ ] **Fix the hinge screw that vibrates loose, with a locknut or a tapped hole** ([powder-doser#116](https://github.com/vertical-cloud-lab/powder-doser/issues/116)).
- [ ] **Fit a working vibration motor, which needs a new Pico W or the DRV8871 driver** ([powder-doser#142](https://github.com/vertical-cloud-lab/powder-doser/issues/142), [powder-doser#165](https://github.com/vertical-cloud-lab/powder-doser/issues/165)).
- [ ] **Once the Al 4047 cup is finished, put the salt auger back in camera view, ready for demos**
  ([powder-doser#186](https://github.com/vertical-cloud-lab/powder-doser/issues/186), [powder-doser#144](https://github.com/vertical-cloud-lab/powder-doser/issues/144)).

## 6. Cameras

- [ ] **Give the OT-2 a camera again.** `picam-ot2` has pointed at the atomizer room since 9/29–10/01, so nothing
  films the robot. The lid mount in [PR #234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234) tapes on. Fixed lighting and a colour card are still open from
  [#34](https://github.com/vertical-cloud-lab/byu-vcl/issues/34) ([#250](https://github.com/vertical-cloud-lab/byu-vcl/issues/250), [streamingLambda#4](https://github.com/vertical-cloud-lab/streamingLambda/issues/4), [stream cams](stream-cams.md)). Owner: @mcwilliams03.
- [ ] **CubXL: move the deck camera to an overhead frame mount, tie back the wires hanging in front of camera 0, and
  add light over the deck,** which is dim enough to need 50 ms exposures ([#165](https://github.com/vertical-cloud-lab/byu-vcl/issues/165)). Owner: Ben.
- [ ] **Find a new owner for the eight Pi 5s in Sterling's office and the dual-camera mount ([PR #241](https://github.com/vertical-cloud-lab/byu-vcl/pull/241)),** now
  that Seth has left. M ([#198](https://github.com/vertical-cloud-lab/byu-vcl/issues/198), [#238](https://github.com/vertical-cloud-lab/byu-vcl/issues/238), [#273](https://github.com/vertical-cloud-lab/byu-vcl/issues/273))

## 7. OT-2 and CubXL

- [ ] **Replace the OT-2 blackout of cardboard and wood with a proper panel** ([#166](https://github.com/vertical-cloud-lab/byu-vcl/issues/166),
  [OT-2 notes](../wireless-color-sensor/ot2/README.md)).
- [ ] **Plug the OT-2's Ethernet straight into the Pi's own RJ45 port, not the RTL8153 USB dongle that keeps wedging
  (check).** The `eth0` link-local profile is already set up
  ([OT-2 notes](../wireless-color-sensor/ot2/README.md), 2026-09-25). [#279](https://github.com/vertical-cloud-lab/byu-vcl/issues/279) also reports the robot's Wi-Fi as
  down.
- [ ] **CubXL Pi power: route its mains lead outside the gantry's travel, with strain relief and a service loop, and
  give the Pi its own supply, ideally a small UPS (check).** On 9/24 the gantry pulled the Pi's plug mid-run and the
  logs were lost. Later runs completed, so the routing may already be fixed. $ for the UPS
  ([wiring notes §21.7](../cubos/docs/opentrons-pipette-wiring.md)).
- [ ] **Strain-relieve the CubXL Z-limit cable, which failed three times, and the pipette's direct-wire leads (check)**
  ([#133](https://github.com/vertical-cloud-lab/byu-vcl/issues/133), [wiring notes](../cubos/docs/opentrons-pipette-wiring.md)).

## 8. PiPER arm cell (spot D in CB154, beside the atomizer's transformer)

Most of these come from the "open before the next campaign block" list on [robot-arms PR #23](https://github.com/vertical-cloud-lab/robot-arms/pull/23), which isn't merged and has no
owners or dates.

- [ ] **Buy, fit and test the plug-in E-stop (POWERTEC 71970, about $50), with only the arm's power brick on it.**
  Sterling asked for a photo on 10-16 and got no reply. $ ([robot-arms#18](https://github.com/vertical-cloud-lab/robot-arms/issues/18), [robot-arms#24](https://github.com/vertical-cloud-lab/robot-arms/issues/24)). Owner: jss265.
- [ ] **Measure the 190 mm (7.5″) clearance to the transformer, tape it off, and add a lip to the shelf on the
  transformer side** ([robot-arms#22](https://github.com/vertical-cloud-lab/robot-arms/issues/22), [robot-arms#2](https://github.com/vertical-cloud-lab/robot-arms/issues/2), [robot-arms PR #23](https://github.com/vertical-cloud-lab/robot-arms/pull/23)).
- [ ] **Cover or label the wrist (J6) teach button.** Two presses replay the last recorded path, and the arm won't stop
  for people in the way ([robot-arms#18](https://github.com/vertical-cloud-lab/robot-arms/issues/18), [robot-arms#7](https://github.com/vertical-cloud-lab/robot-arms/issues/7)).
- [ ] **Post the sign, with a name and phone number, and the one-page checklist by the arm. Then commit the sign's
  text** ([robot-arms#22](https://github.com/vertical-cloud-lab/robot-arms/issues/22), [robot-arms#24](https://github.com/vertical-cloud-lab/robot-arms/issues/24)).
- [ ] **Tape the arm's reach on the table and floor, and label the dome flap** ([robot-arms PR #23](https://github.com/vertical-cloud-lab/robot-arms/pull/23)).
- [ ] **Get everything that plugs into the wall off the wood and into open air.** That means the power brick, the Pi
  supply and the strips. Don't chain one strip into another, and check the safety-listing marks ([robot-arms#24](https://github.com/vertical-cloud-lab/robot-arms/issues/24),
  [robot-arms PR #23](https://github.com/vertical-cloud-lab/robot-arms/pull/23)).
- [ ] **Paint the plywood base with fire-retardant paint, and note where the extinguisher is.** Sterling raised the
  plywood on 10-14. $ ([robot-arms#24](https://github.com/vertical-cloud-lab/robot-arms/issues/24), [robot-arms PR #23](https://github.com/vertical-cloud-lab/robot-arms/pull/23))
- [ ] **Keep safety glasses, a brush and pan, and a glass-disposal box at the cell** ([robot-arms PR #23](https://github.com/vertical-cloud-lab/robot-arms/pull/23)).
- [ ] **Confirm the arm is bolted down and the plywood clamped to the table, and record how (check)**
  ([robot-arms#15](https://github.com/vertical-cloud-lab/robot-arms/issues/15), [robot-arms#2](https://github.com/vertical-cloud-lab/robot-arms/issues/2)).
- [ ] **Decide on the quarter-dome enclosure order ($112.72), which is waiting on approval.** Before buying, check it
  against the cut list: two drop cloths, 33 clamps, and the plywood trimmed to 47½ in. M ([robot-arms#2](https://github.com/vertical-cloud-lab/robot-arms/issues/2), 10-19). Owner:
  chris-policky.
- [ ] **Get fasteners for the wrist camera mount and assemble it** ([robot-arms#4](https://github.com/vertical-cloud-lab/robot-arms/issues/4), [robot-arms#6](https://github.com/vertical-cloud-lab/robot-arms/issues/6)). Owner: claytonblodgett.
- [ ] **Mount the side camera rigidly, since tape let it move, and add an overhead camera and a stand camera**
  ([robot-arms#24](https://github.com/vertical-cloud-lab/robot-arms/issues/24)).
- [ ] **Print the J1 parking seat after measuring the height under the upper arm (the model expects 93.5 mm)**
  ([robot-arms#25](https://github.com/vertical-cloud-lab/robot-arms/issues/25)).
- [ ] **Add a smart plug after the E-stop, defaulting to off** ([robot-arms#24](https://github.com/vertical-cloud-lab/robot-arms/issues/24)).
- [ ] **Pin the CubXL mock-up to the table, side-on beside the PiPER, where the CubXL will stand** ([#266](https://github.com/vertical-cloud-lab/byu-vcl/issues/266)).
  Owner: Chris Policky.

## 9. Printers

- [ ] **Put the H2D on a rigid surface, for example by taking the casters off its stand** ([#82](https://github.com/vertical-cloud-lab/byu-vcl/issues/82), [#108](https://github.com/vertical-cloud-lab/byu-vcl/issues/108),
  [PR #109](https://github.com/vertical-cloud-lab/byu-vcl/pull/109)).
- [ ] **Finish the H2D add-ons: mount the second AMS, the 4-in-1 adapter and the TPU spool guide, and keep TPU sealed
  with desiccant** ([#101](https://github.com/vertical-cloud-lab/byu-vcl/issues/101)). Owner: me-madsen.
- [ ] **Sweep under the H2D build platform from time to time, and log lubrication** ([#181](https://github.com/vertical-cloud-lab/byu-vcl/issues/181)).
- [ ] **Fill in the placeholders in the [3D printing SOP](../SOP/3d-printing-sop.md):** the lab location, the contact,
  where the extinguisher and E-stop are, the scrap bin, and a sign-up sheet.

## 10. SEM prep and samples (caliber)

- [ ] **Choose how to store loaded SEM stubs, then print the holders.** "We are running out of space." The 19-stub
  Petri-dish insert in [caliber PR #17](https://github.com/vertical-cloud-lab/caliber/pull/17) is ready to print ([caliber#22](https://github.com/vertical-cloud-lab/caliber/issues/22)). Owner: Ronnie.
- [ ] **Re-check the sample desiccator's vacuum and set a monthly re-pump.** The last check was 9/30. If it leaks, use
  Apiezon grease, not silicone ([caliber#16](https://github.com/vertical-cloud-lab/caliber/issues/16)).
- [ ] **Get a dedicated vacuum pump and gauge for the desiccator, about $160.** The lab still borrows the PSC's. $
  ([caliber#16](https://github.com/vertical-cloud-lab/caliber/issues/16), [#110](https://github.com/vertical-cloud-lab/byu-vcl/issues/110))
- [ ] **Confirm methanol and ethanol are in stock for polishing (check).** This was asked twice on 10-15 with no
  answer ([caliber#12](https://github.com/vertical-cloud-lab/caliber/issues/12), [#110](https://github.com/vertical-cloud-lab/byu-vcl/issues/110)).
- [ ] **Label a dedicated polishing pad "99.99 % Al std, 1 µm alumina only", and retire the pad box marked best by
  10/2026** ([caliber#12](https://github.com/vertical-cloud-lab/caliber/issues/12)).

## 11. Around the lab

- [ ] **Check that cords crossing the floor from the 20 ft power strips are taped down or run overhead.** [#51](https://github.com/vertical-cloud-lab/byu-vcl/issues/51)
  asked Dave which he'd recommend, then closed once the cords arrived.
- [ ] **Check that the Ethernet drops in the work order exist, both in the enclosure and in the lab** ([#31](https://github.com/vertical-cloud-lab/byu-vcl/issues/31)).
- [ ] **Find out what happened to the two fume hoods from the battery-manufacturer auction.** The auction charged
  for the Squidstat but not the hoods, and the thread stops on 4/30. CB154 still has no hood ([#75](https://github.com/vertical-cloud-lab/byu-vcl/issues/75), [#279](https://github.com/vertical-cloud-lab/byu-vcl/issues/279)).

## 12. Elsewhere

- [ ] **Drop tower (CB 152A, shared):** replace the broken 10,000 g base accelerometer (CH5). The tower is halted
  until then. M ([tensegrity#115](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/115))
- [ ] **Drop tower:** weigh the falling carriage and plate, measure the anvil, and record both ([tensegrity#94](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/94),
  [tensegrity#99](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/99)). Keep a spare lanyard ball-lock pin and talc for the pads ([tensegrity#92](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/92), [tensegrity#88](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/88)).
- [ ] **Find storage for the printed T3 specimens.** There are 84 IDs so far ([tensegrity#109](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/109), [tensegrity#98](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98)).
- [ ] **Induction furnace:** inventory the parts in the quotes folder, and decide whether to surplus or keep the
  abandoned CYSI heater ([custom-induction-furnace#1](https://github.com/vertical-cloud-lab/custom-induction-furnace/issues/1)). Owner: Ronnie.

## Bigger items, tracked in their own issues

These aren't small, but they shape the room: fume control, whether a canopy hood, snorkels or the Dillon hood
([#29](https://github.com/vertical-cloud-lab/byu-vcl/issues/29), [#195](https://github.com/vertical-cloud-lab/byu-vcl/issues/195), [PR #96](https://github.com/vertical-cloud-lab/byu-vcl/pull/96)); the glovebox, about $4.2k, whose cylinder would count toward the two-cylinder
limit ([#30](https://github.com/vertical-cloud-lab/byu-vcl/issues/30)); a flammables cabinet ([#31](https://github.com/vertical-cloud-lab/byu-vcl/issues/31)); drying the enclosure further, since the dehumidifier dropped the
dew point only 2–3 °C ([#42](https://github.com/vertical-cloud-lab/byu-vcl/issues/42)); a lab-owned high-speed camera for the drop tower ([tensegrity#89](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/89), [tensegrity#91](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/91)); the
three viewport cameras, about $1,218 ([#198](https://github.com/vertical-cloud-lab/byu-vcl/issues/198)); the vertical lift module ([#53](https://github.com/vertical-cloud-lab/byu-vcl/issues/53)).

## Already done, for reference

- Coat and backpack hooks behind the room door ([#22](https://github.com/vertical-cloud-lab/byu-vcl/issues/22), 2026-03-12).
- Class D extinguisher in the lab; only mounting is open ([#19](https://github.com/vertical-cloud-lab/byu-vcl/issues/19)).
- Nilfisk CFM 118EXP ATEX vacuum, tested by 9/17 ([#24](https://github.com/vertical-cloud-lab/byu-vcl/issues/24)).
- Enclosure with vinyl strips; exhaust; dehumidifier, on since 9/29; 32 A power, chilled water, compressed air and 5N
  argon for the install ([#31](https://github.com/vertical-cloud-lab/byu-vcl/issues/31), [#124](https://github.com/vertical-cloud-lab/byu-vcl/issues/124), [#42](https://github.com/vertical-cloud-lab/byu-vcl/issues/42)).
- No oxygen monitor needed within the two-cylinder rule ([PR #271](https://github.com/vertical-cloud-lab/byu-vcl/pull/271)).
- Waste route: Risk Management's Solid Material bucket, labelled metal buckets for vacuum liners, and a foot-operated
  flammable-waste bin ([#126](https://github.com/vertical-cloud-lab/byu-vcl/issues/126)).
- Bench vise with soft jaw covers, IPA and Kimwipes ([#126](https://github.com/vertical-cloud-lab/byu-vcl/issues/126)); label maker ([#50](https://github.com/vertical-cloud-lab/byu-vcl/issues/50)); extension cords
  ([#51](https://github.com/vertical-cloud-lab/byu-vcl/issues/51)); toolkit ([#37](https://github.com/vertical-cloud-lab/byu-vcl/issues/37)); caliper ([#119](https://github.com/vertical-cloud-lab/byu-vcl/issues/119)).
- Transducer cable holder printed and in use ([#256](https://github.com/vertical-cloud-lab/byu-vcl/issues/256)). OT-2 blacked out for now, and its plate re-taped after the
  10-14 lift.
- Powder doser: scale drift traced to a misaligned dust plate and fixed; locknuts; food-safe tape on augers; camera
  ([powder-doser#157](https://github.com/vertical-cloud-lab/powder-doser/issues/157), [powder-doser#132](https://github.com/vertical-cloud-lab/powder-doser/issues/132), [powder-doser#144](https://github.com/vertical-cloud-lab/powder-doser/issues/144)).
- PiPER: US power cord, practice bench and pick-up shelf ([robot-arms#7](https://github.com/vertical-cloud-lab/robot-arms/issues/7), [robot-arms#6](https://github.com/vertical-cloud-lab/robot-arms/issues/6), [robot-arms#2](https://github.com/vertical-cloud-lab/robot-arms/issues/2)). Drop tower: guide-rod pins
  replaced and interlock working; rubber pads in place of felt ([tensegrity#92](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/92), [tensegrity#88](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/88)).
- Caliber: desiccator holding vacuum; standards and carbon tape in ([caliber#16](https://github.com/vertical-cloud-lab/caliber/issues/16), [caliber#12](https://github.com/vertical-cloud-lab/caliber/issues/12)). Furnace roughing pump on
  its own cinder block ([custom-induction-furnace#7](https://github.com/vertical-cloud-lab/custom-induction-furnace/issues/7)).

Issues that look ready to close, if you agree:

- [#23](https://github.com/vertical-cloud-lab/byu-vcl/issues/23): HEPA on the enclosure exhaust dropped, since MERV 13 is enough.
- [#79](https://github.com/vertical-cloud-lab/byu-vcl/issues/79): vacuum test done before 9/17.
- [#36](https://github.com/vertical-cloud-lab/byu-vcl/issues/36): recording clamps and mounts bought, nothing left.
- [robot-arms#30](https://github.com/vertical-cloud-lab/robot-arms/issues/30): the arm moved the tape itself.
