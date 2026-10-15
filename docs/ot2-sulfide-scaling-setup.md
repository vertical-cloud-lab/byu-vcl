# Setting up the OT-2 for the sulfide-scaling experiments

Asked on [#279](https://github.com/vertical-cloud-lab/byu-vcl/issues/279) by @timothy-commins:
pull from the grant proposal for the petroleum sulfide-scaling experiments and list what has
to be done to set up for testing. Written 2026-10-15 from the written record only. Nothing on
the robot or the Pis was touched.

## Where this comes from

**The proposal itself is not in any repository this session can read.** It is most likely in
`vertical-cloud-lab/digital-wetlab-private`, which [#15](https://github.com/vertical-cloud-lab/byu-vcl/issues/15#issuecomment-3987730523)
and [#81](https://github.com/vertical-cloud-lab/byu-vcl/issues/81) both point to, and which
this session's token cannot see. The Google Doc linked from
[digital-wetlab#1](https://github.com/vertical-cloud-lab/digital-wetlab/issues/1) is a
different document: the qualitative-analysis / LLM-benchmark plan (static copy:
[`opentrons-inorganic-wet-lab-agents.txt`](https://github.com/vertical-cloud-lab/digital-wetlab/blob/bd53112/opentrons-inorganic-wet-lab-agents.txt)).

The list is built from these instead, all public:

| source | what it gives |
| --- | --- |
| [digital-wetlab#1, 2026-03-03](https://github.com/vertical-cloud-lab/digital-wetlab/issues/1#issuecomment-3993541394) | Sterling's draft of the proposal's preliminary-results paragraph, quoted below |
| [digital-wetlab PR #3](https://github.com/vertical-cloud-lab/digital-wetlab/pull/3) (open) | the experiment plans [`002-baso4-precipitation`](https://github.com/vertical-cloud-lab/digital-wetlab/blob/1c0f422/experiments/002-baso4-precipitation/README.md) and [`003-pbs-vial-tests`](https://github.com/vertical-cloud-lab/digital-wetlab/blob/1c0f422/experiments/003-pbs-vial-tests/README.md) |
| [digital-wetlab PR #8](https://github.com/vertical-cloud-lab/digital-wetlab/pull/8) (open) | the protocol that ran the BaSO₄ plate on 2026-03-05 |
| digital-wetlab [#9](https://github.com/vertical-cloud-lab/digital-wetlab/issues/9), [#11](https://github.com/vertical-cloud-lab/digital-wetlab/issues/11), [#12](https://github.com/vertical-cloud-lab/digital-wetlab/issues/12), PRs [#10](https://github.com/vertical-cloud-lab/digital-wetlab/pull/10), [#13](https://github.com/vertical-cloud-lab/digital-wetlab/pull/13) | balance, heater scheduling, the 19-parameter search space, the human part |
| this repo: [#15](https://github.com/vertical-cloud-lab/byu-vcl/issues/15), [#29](https://github.com/vertical-cloud-lab/byu-vcl/issues/29), [#195](https://github.com/vertical-cloud-lab/byu-vcl/issues/195), [#81](https://github.com/vertical-cloud-lab/byu-vcl/issues/81), [#68](https://github.com/vertical-cloud-lab/byu-vcl/issues/68), [#34](https://github.com/vertical-cloud-lab/byu-vcl/issues/34), [`wireless-color-sensor/ot2/`](../wireless-color-sensor/ot2/) | what was bought, the fume hood, the heater-shaker, the plate reader, the overhead camera, the robot's current state |
| [`byu-engineering-lab-safety-plan-chemical-hygiene-plan-2024.pdf`](../byu-engineering-lab-safety-plan-chemical-hygiene-plan-2024.pdf) | what BYU Engineering requires before hazardous work |
| the SDSs attached to [#15](https://github.com/vertical-cloud-lab/byu-vcl/issues/15#issuecomment-3991816640) | the hazards of the lead nitrate and ammonium sulfide on the shelf |

> Feasibility has been established by proof-of-concept experiments. A 96-well BaSO₄ plate with
> 80 Latin hypercube-sampled conditions varying Ba²⁺ (0.1–50 mM), SO₄²⁻ (0.1–50 mM), and NaCl
> (0–3 molal) produced the expected precipitation boundary; all supersaturated wells displayed
> visible white crystalline precipitate by 240 minutes, with imaging at 5, 15, 60, and 240
> minutes supporting subsequent computer-vision analysis. Complementary small-scale vial tests
> for PbS confirmed that black precipitates formed rapidly (<5 minutes) and were clearly visible
> at 0.5 mM Pb²⁺ in 1 molal NaCl, providing a robust visual signal and supporting the choice of
> detection optics and time points for the full platform; [...]
>
> — draft, [digital-wetlab#1](https://github.com/vertical-cloud-lab/digital-wetlab/issues/1#issuecomment-3993541394).
> Sterling added: "We also want the 8-channel light sensor data, if possible."

So the proposal commits to two things that can be tested now: a BaSO₄ plate imaged at 5, 15,
60 and 240 min, and PbS at sub-millimolar Pb²⁺ in brine. Later threads add a heater, reads at
1, 5, 15, 60 and 240 min, and a 19-parameter Ax search
([digital-wetlab#11](https://github.com/vertical-cloud-lab/digital-wetlab/issues/11)). FeS is
named as a target alongside BaSO₄ and PbS in
[#68](https://github.com/vertical-cloud-lab/byu-vcl/issues/68#issuecomment-4128277097).

## Where things stand (2026-10-15)

| | state | source |
| --- | --- | --- |
| BaSO₄ plate | **Run once, on 2026-03-05**: 80 LHS wells and 16 controls, "the lab's first 98 experiments". I found no images at the four time points and no analysis in any repo. The dry run's camera recording stopped after 1.5 h. | [digital-wetlab#1](https://github.com/vertical-cloud-lab/digital-wetlab/issues/1#issuecomment-4008876464) |
| PbS vial tests | **No record of a run.** Plan 003 is written for Na₂S·9H₂O, but the lab bought ammonium sulfide. | PR #3, #15 |
| Chemicals | Bought 03-03: AgNO₃, NaCl, Na₂SO₄, Ba(NO₃)₂ (to be returned), Pb(NO₃)₂ 500 g, (NH₄)₂S solution 500 mL. BaCl₂ was on hand by 03-05. **No Na₂S, and no iron(II) or zinc salts.** | [#15](https://github.com/vertical-cloud-lab/byu-vcl/issues/15#issuecomment-3987730523) |
| Fume hood | **None in CB154.** Facilities ruled out installing one and offered a canopy hood instead. Interim use of the Dillon lab's hood is agreed. | [#29](https://github.com/vertical-cloud-lab/byu-vcl/issues/29#issuecomment-4093457224), [#195](https://github.com/vertical-cloud-lab/byu-vcl/issues/195) |
| Pipettes | On 09-11 the only pipette attached was a **P300 single GEN2 (left)**, with no tip-length or offset calibration. The BaSO₄ run used a **P20** single GEN2. The deck calibration is from 01-27, before the robot was moved on 09-10. | [`opentrons-calibration.md`](../wireless-color-sensor/ot2/opentrons-calibration.md) |
| Opentrons App | Can't see the robot: its Wi-Fi is down and its Ethernet goes only to a Pi. | same |
| Heater-shaker | Found on 10-13 and put inside the OT-2; the temperature module went back in its box. Not yet seated or set up. | [#81](https://github.com/vertical-cloud-lab/byu-vcl/issues/81#issuecomment-6157219356) |
| Deck | The colour-sensor rig is on it: a plate taped down in slot 7 on black paper, the sensor dock in slot 10, the paint vials. | [`wireless-color-sensor/ot2/README.md`](../wireless-color-sensor/ot2/README.md) |
| Overhead camera | [#34](https://github.com/vertical-cloud-lab/byu-vcl/issues/34) is still open. Its last update (June) was a designed HQ-camera housing, with printing and assembly next. The `picam-ot2` stream has shown the atomizer room since 10-01. | #34, [`stream-cams.md`](stream-cams.md) |
| Colour sensor | Works. Its best colour error is 12%, at nozzle z 92 over black paper. | README |
| Plate reader | Byonoy Absorbance 96 quoted at $4,990; on hold for budget. | [#68](https://github.com/vertical-cloud-lab/byu-vcl/issues/68#issuecomment-4756219428) |
| Balance | The HR-100A weighs 102 g × 0.1 mg. An FX-300iWP (320 g × 1 mg) was suggested; no quote posted. | digital-wetlab #9, PR #10 |

## The checklist

### 0. Get the numbers only the proposal has

- [ ] The 19 parameters and their ranges ([digital-wetlab#11](https://github.com/vertical-cloud-lab/digital-wetlab/issues/11)).
  None of them is written down in a public repo.
- [ ] Which sulfides: PbS only, or ZnS and FeS too. FeS changes the setup the most (step 2).
- [ ] The temperature range, the pH range, and any scale inhibitors and their doses.
- [ ] Which preliminary results the proposal still needs. Is the 03-05 plate enough, and are
  the PbS vials still owed?

If a session should read the proposal itself, Sterling can put the relevant sections in
`sgbaird/agent-staging` and point the session at them (see CLAUDE.md).

### 1. Safety and paperwork, before any lead or sulfide is opened

- [ ] **Job Hazard Analysis** for the lead and sulfide work. The BYU Engineering safety plan
  requires one before work starts (§5–6).
- [ ] **A written SOP** from [`byu-engineering-sop-template.md`](../byu-engineering-sop-template.md),
  with the emergency section the plan requires (§7): H₂S release, spill, exposure, and
  what to do with the robot mid-run.
- [ ] **Training records** for everyone who will handle the chemicals, based on the JHA, the
  SOP and the SDSs (§8).
- [ ] **Treat lead nitrate as a particularly hazardous substance.** Its SDS on file (Aldrich
  Y751405) classes it Carc. 1B (H350), Repr. 1A (H360) and an oxidiser (H272). For such
  substances OSHA's lab standard,
  [29 CFR 1910.1450(e)(3)(viii)](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.1450),
  calls for a designated area, containment, and waste and decontamination procedures. Ask
  EHS how BYU wants that done in CB154. The safety plan lists College OHS (801-422-6589) and
  Risk Management (801-422-2943).
- [ ] **Store the ammonium sulfide as a flammable.** Its SDS (Sigma A1952) gives Flam. Liq. 3
  (flash point 32 °C), Skin Corr. 1B, Eye Dam. 1 and Acute Tox. 3 (oral). It also says
  "contact with acids liberates toxic gas" and asks for storage locked up, cool, and away
  from acids and oxidisers. The safety plan puts flammables in a flammable cabinet (§9).
  Keep it away from the lead nitrate, which is an oxidiser, and from any acids.
- [ ] **Decide where the sulfide work happens.** Making the sulfide stock and running the PbS
  vial tests belong in a hood, which means the Dillon lab
  ([#195](https://github.com/vertical-cloud-lab/byu-vcl/issues/195)). Check that the
  arrangement covers lead and sulfide.
- [ ] **Decide whether sulfide can run on the OT-2 at all, and under what controls.** The robot
  isn't in a hood, and CB154 can't get one
  ([#29](https://github.com/vertical-cloud-lab/byu-vcl/issues/29#issuecomment-4093457224)).
  Options to put to EHS:
  - millimolar sulfide only, kept basic and never acidified
  - a fixed H₂S monitor at the robot (plan 003 recommends a detector)
  - a canopy hood over the robot

  The project doc says the same: "H₂S requires proper ventilation (fume hood or gas
  detection)".
- [ ] **Don't count on the lab's respirators for H₂S.** The 3M half-face masks have P100
  particulate filters
  ([#15](https://github.com/vertical-cloud-lab/byu-vcl/issues/15#issuecomment-3923351840)),
  which don't stop gases.
- [ ] **Separate waste streams**, each labelled:
  - lead and sulfide liquids (never acidify them, or H₂S comes off)
  - barium liquids
  - contaminated solids: tips, plates, wipes

  Pickups go through Chemicals Management (801-422-6382).
- [ ] **A spill kit** sized for these chemicals (safety plan §9), and a working **eyewash**.
  The renovation work order includes a sink and eye rinse
  ([#31](https://github.com/vertical-cloud-lab/byu-vcl/issues/31)); check that they're in.
- [ ] **An SDS binder and inventory.** The SDSs are attached to
  [#15](https://github.com/vertical-cloud-lab/byu-vcl/issues/15#issuecomment-3991816640),
  but BaCl₂'s isn't among them. Label every secondary container with the name, hazards and
  pictograms (§9).

### 2. Chemicals and stock solutions

- [ ] **Check the ammonium sulfide bottle** before planning around it. It was bought on
  2026-03-03. Opened ammonium sulfide loses H₂S and NH₃ and turns yellow as polysulfide
  forms. Note the colour. If it's dark yellow, or the exact strength matters, buy a fresh
  bottle or standardise this one.
- [ ] **Rewrite plan 003's sulfide recipe for (NH₄)₂S,** or buy the Na₂S·9H₂O the plan
  specifies. The SDS gives 10–30 wt%, so read the exact strength off the label. At 20 wt%
  (about 3 M), the plan's 10 mM stock is about 50 µL of the bottle's solution made up to
  15 mL. Make it in the hood, fresh on the day.
- [ ] **Lead nitrate, 10 mM:** 0.0497 g in 15 mL (plan 003). Weigh it in the hood.
- [ ] **BaCl₂ 1.0 M, Na₂SO₄ 1.0 M and NaCl 5 M** (plan 002). Add 1 mM BaCl₂ and Na₂SO₄
  intermediates if the plate is to cross the precipitation boundary. PHREEQC put all 80 of
  the planned wells above saturation (SI 2.6–5.8), so the March plate mapped how much
  precipitated, not where precipitation starts (plan 002).
- [ ] **DI water** from the Chem Stores tap, stored in HDPE rather than glass
  ([#15](https://github.com/vertical-cloud-lab/byu-vcl/issues/15#issuecomment-3993989121)).
- [ ] **Weigh the solids, not the bottles.** The 0.1 mg balance tops out at 102 g
  ([digital-wetlab#9](https://github.com/vertical-cloud-lab/digital-wetlab/issues/9)).
  Weighing the solid on a boat and making it up in a volumetric flask gets round the
  limit; the FX-300iWP ([PR #10](https://github.com/vertical-cloud-lab/digital-wetlab/pull/10))
  removes it.
- [ ] **If FeS or ZnS is in scope,** buy an iron(II) or zinc salt. Fe²⁺ oxidises in air, so
  FeS also needs deoxygenated water and an inert atmosphere. There is no glovebox yet
  ([#30](https://github.com/vertical-cloud-lab/byu-vcl/issues/30)), and the argon line is
  part of the renovation ([#31](https://github.com/vertical-cloud-lab/byu-vcl/issues/31),
  [#41](https://github.com/vertical-cloud-lab/byu-vcl/issues/41)).
- [ ] **Run a saturation check on the sulfide design** before fixing its ranges, as PR #3 did
  for BaSO₄ ([`phreeqc_saturation_heatmap.py`](https://github.com/vertical-cloud-lab/digital-wetlab/blob/1c0f422/experiments/002-baso4-precipitation/phreeqc_saturation_heatmap.py)).
  PbS's Ksp (~3 × 10⁻²⁸, plan 003) is so small that any mix the robot can pipette will
  precipitate. A PbS plate therefore maps intensity and kinetics, unless pH, temperature
  or complexation is what's being varied.

### 3. The OT-2 itself

- [ ] **Clear the colour-sensor rig off the deck,** or agree a shared layout with whoever
  carries that work on ([#197](https://github.com/vertical-cloud-lab/byu-vcl/issues/197),
  [PR #202](https://github.com/vertical-cloud-lab/byu-vcl/pull/202), merged 10-15). Before any run, make
  the README's "one controller at a time" check: no other CI job, no driver running on the
  Pi, and no open maintenance run.
- [ ] **Put the P20 back on**, for example on the right mount, and keep the P300 on the left
  for the sensor and for bulk water and NaCl. With 1 M stocks, the P20's 1 µL minimum gives
  5 mM in a 200 µL well. Update the protocol's mounts to match.
- [ ] **Calibrate in order: deck, tip length, pipette offset, then Labware Position Check**
  ([`opentrons-calibration.md`](../wireless-color-sensor/ot2/opentrons-calibration.md)).
  Deck calibration clears the other two. All four are needed: the robot was moved, the P300
  has no data, and the P20 is going back on.
- [ ] **Give the OT-2 App a way to reach the robot**, or run protocols over HTTP from the Pi.
  The March runs used the App. Use the separate OT-2 App, as that doc explains.
- [ ] **Seat the heater-shaker** in slot 1, 3, 4, 6, 7 or 10, and connect its USB and power.
  On 10-14 the sensor run found a device lying across slots 1 and 2 and went round it;
  that is probably this module. From the
  [Opentrons docs](https://docs.opentrons.com/v2/modules/heater_shaker.html):
  - It heats from 37 to 95 °C and shakes at 200–3000 rpm. It can't cool; the boxed
    temperature module (4–95 °C) can.
  - No other module may sit next to it, and nothing taller than 53 mm directly to its left
    or right. The AC 15 mL tube rack is 61 mm tall.
  - The NEST 96-well 200 µL flat plate needs the 96 Flat Bottom Adapter
    (`opentrons_96_flat_bottom_adapter`). Check which adapters came with this second-hand
    unit.
  - The latch must be closed for it to shake.
- [ ] **Labware:**
  - NEST 96-well 200 µL flat plates (PR #8). Plan 002 recommends clear PS for imaging.
  - 20 µL filter tips and 300 µL tips.
  - Lids or seals for the 240-min holds and for anything heated.
  - For the vial tests, 20 mL screw-cap glass vials (some bought in #15).
- [ ] **Dry-run with water first,** as on 03-05.

### 4. Protocol changes

Start from the protocol that ran on 03-05, PR #8's
[`Experiment_1__AgCl_Precipitation_V1.py`](https://github.com/vertical-cloud-lab/digital-wetlab/blob/cded249/Experiment_1__AgCl_Precipitation_V1.py)
(the BaSO₄ plate, despite its name). Merge or close PRs #3 and #8 so there is one version.

- [ ] **Stop carrying precipitate back into the stock tubes.** That protocol uses one tip per
  reagent, and `transfer()` dispenses 1 mm above the well bottom, so the tip dips into the
  well. The Na₂SO₄ tip goes in last, touches wells that already hold Ba²⁺, then goes back
  into the Na₂SO₄ tube. That seeds the stock with BaSO₄, and seed crystals change how fast
  wells precipitate, which is what the time points measure. With sulfide, the tip would
  carry Pb²⁺ back and precipitate PbS in the sulfide tube. Dispense the last reagent from
  above the liquid (`well.top()`), or use a fresh tip for every well.
- [ ] **Log each well's own start time.** In the March dry run the water step alone took
  almost 1.5 h, because the P20 needs up to ten trips per well. The last reagent also goes
  in one well at a time, so the last well starts minutes after the first, which is
  comparable to the 5-min time point. Take each well's t = 0 from the run log, or add the
  last reagent column by column and image in the same order. Moving water and NaCl to the
  P300 shortens the run.
- [ ] **Pick one schedule:** 5, 15, 60 and 240 min (the proposal), or 1, 5, 15, 60 and 240 min
  ([digital-wetlab#11](https://github.com/vertical-cloud-lab/digital-wetlab/issues/11)).
- [ ] **Load the sulfide tube last and keep runs short.** The OT-2 can't cap tubes. An open
  sulfide stock loses strength, and gives off H₂S and NH₃, for as long as the run lasts.
- [ ] **Write the sulfide plate design.** Plan 003 is six vials mixed by hand. Use the
  saturation check from step 2, and keep the negative controls (lead only, sulfide only,
  brine only).

### 5. Measuring the plate

- [ ] **Overhead camera ([#34](https://github.com/vertical-cloud-lab/byu-vcl/issues/34)).**
  Finish the HQ-camera build and fix it above the plate. Light the plate the same way every
  time, and keep a colour card in frame (plan 002, and the reviewer's note in the project
  doc). It has to run for over 4 h; the 03-05 recording stopped at 1.5 h. Save stills at each
  time point with the time in the filename. The robot's own camera (640 × 480, through
  [`deck_photo.py`](../wireless-color-sensor/ot2/deck_photo.py)) is for checking the deck,
  not for reading wells.
- [ ] **The 8-channel sensor, "if possible".** It reads one well at a time: a reading takes
  about a second, plus the move to the next well. A pass over 96 wells takes several
  minutes and won't fit the 5-min window, so read a few sentinel wells instead. Choose the
  background on purpose: white BaSO₄ shows best over black, and black PbS best over white.
  - On the heater-shaker the plate sits on a metal adapter, so the read height and the
    background have to be found again.
  - The light panel under the plate that worked at the AC
    ([ac-dev-lab#552](https://github.com/AccelerationConsortium/ac-dev-lab/issues/552))
    can't go under a heater-shaker.
  - On 10-14 the enclosure lifted an untaped plate. The heater-shaker's latch would hold it.
- [ ] **Absorbance.** The "absorbance at 1, 5, 15, 60 and 240 minute" plan in
  [digital-wetlab#11](https://github.com/vertical-cloud-lab/digital-wetlab/issues/11)
  assumes a plate reader. That purchase is on hold
  ([#68](https://github.com/vertical-cloud-lab/byu-vcl/issues/68#issuecomment-4756219428)),
  and the OT-2 has no gripper to carry plates to one. Until then, turbidity comes from the
  camera and the sensor.

### 6. Data

- [ ] **Store results in MongoDB `digital-wetlab`.** The sensor already writes to
  `sensor-data`, and `ot2-runs` exists for runs. Record each well's conditions and start
  time, the images and their time points, a 0–3 precipitate score, and RGB/LAB values
  (plan 002, *Data Collection*).
- [ ] **Commit the design matrices and analysis** to `digital-wetlab`, or to
  `digital-wetlab-private` if they shouldn't be public before the proposal is decided.

### 7. After the first plates

- [ ] **Heater scheduling for several temperatures.**
  [digital-wetlab PR #13](https://github.com/vertical-cloud-lab/digital-wetlab/pull/13)
  recommends batching by temperature, interleaving reads, and running Ax asynchronously.
- [ ] **The human part**
  ([digital-wetlab#12](https://github.com/vertical-cloud-lab/digital-wetlab/issues/12)):
  tips, stock refills and plate swaps, since the OT-2 has no gripper. Sterling liked the
  idea of pings arriving as GitHub issues.
- [ ] **Replace the placeholder two-parameter search space** in
  [`experimentation_script.py`](https://github.com/vertical-cloud-lab/digital-wetlab/blob/bd53112/experimentation_script.py)
  (Sobol, then BoTorch) with the proposal's 19 parameters
  ([digital-wetlab#2](https://github.com/vertical-cloud-lab/digital-wetlab/issues/2)).

## Suggested order

1. **Steps 0 and 1 in parallel.** The JHA, the SOP and EHS's answers gate everything that
   involves lead or sulfide.
2. **The robot:** deck cleared, P20 back on, calibrated, heater-shaker seated, water dry run.
3. **The overhead camera,** so the next plate gets all four time points.
4. **PbS vial tests in the Dillon hood.** They are the outstanding preliminary result, and the
   first use of the new sulfide recipe.
5. **The BaSO₄ plate again,** with the protocol fixes and full imaging, if the March data
   doesn't support the proposal's paragraph.
6. **The first sulfide plate on the OT-2,** once EHS has answered step 1.
