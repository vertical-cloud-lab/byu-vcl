## The alloy workflow, step by step: what DAL does by hand, and where it goes in the vertical lab

Each step the lab runs today, from the [digital-alloy-lab](https://github.com/vertical-cloud-lab/digital-alloy-lab) (DAL)
issues, PRs and SOPs and from the lab's own videos on the BYU Vertical Cloud Lab channel. The table gives the station
it would use in the vertical lab and what is still missing. The "Real footage" column is the lab doing that step,
by hand.

| # | Step | What the lab does now (DAL) | Real footage | Station in the vertical lab | What is still missing |
|---|---|---|---|---|---|
| 1 | Pick a composition | BO / BOFN over a CALPHAD-screened space (DAL #3, #91, #121); the FLAIME 15-element palette (DAL PR #88) | | software | |
| 2 | Weigh the charge | Al wire or rod and Si / master-alloy powders weighed by hand (byu-vcl #16; DAL PR #187's SOP); Al cups and press-fit plugs hold the charge (DAL PR #179, #152) | [powder dispensing SOP](https://youtu.be/WTrs3JU2HF0) | the multi-doser on tray B (round 2) | a station that fills a cup and presses its plug; cutting wire or rod to mass |
| 3 | Coat the crucible | boron nitride sprayed onto the graphite crucible (DAL PR #220) | [coating](https://www.youtube.com/watch?v=GF2Bo60-4z4), [recoating](https://www.youtube.com/watch?v=gZdjcXo7nx0), [results](https://www.youtube.com/watch?v=Sh-nYiggiek) | by hand, under extraction | stays manual: an aerosol job |
| 4 | Atomize | AMAZEMET rePowder: charge, pump down and back-fill with argon, induction melt, ultrasonic atomization (DAL PR #178's SOP; runs in #182, #230) | [630 bronze run](https://www.youtube.com/watch?v=NZWmk5PqQhg), [Cu70/Ni30 run](https://www.youtube.com/watch?v=Ha7lIHP9X9g) | beside the VLM | charging by the arm; computer control of the rePowder (DAL #151) |
| 5 | Recover and sieve the powder | clean the chamber with the explosion-proof vacuum (DAL #128, PR #186); sieve through 8 in stainless sieves: No. 60 (250 µm) scalp, No. 230 and pan bought, No. 100, 140 and 325 on order (DAL PR #175's `docs/sieve-order.md`); 20–63 µm for LPBF, 45–105 and 100–200 µm for DED (DAL PR #220) | [cleaning and sieving 1](https://www.youtube.com/watch?v=7pqPt9xbV8E), [2](https://www.youtube.com/watch?v=sN0xzUjTDKE), [3](https://www.youtube.com/watch?v=Dni35K9VWck) | Retsch AS 200 control sieve shaker, beside the rePowder (round 4) | moving powder between atomizer, sieve and jar without air exposure (the glovebox, DAL #130) |
| 6 | Store | dry storage at about 25 % RH (DAL #131, PR #188); whether desiccant contaminates the powder (DAL #155) | | jars in the glovebox, or a dry cabinet | a dry cabinet on a tray |
| 7 | Characterize the powder | SEM and EDS on carbon tape or as a slurry (DAL PR #181's SOP); size and shape from the SEM images (DAL #225); composition (DAL #102) | [SEM samples](https://www.youtube.com/watch?v=_LnkM2GqiCI), [SEM and EDX](https://www.youtube.com/watch?v=SHlhp0VHKsY), [particle analysis](https://www.youtube.com/watch?v=IGZ0saVgkzw) | SEM, Mastersizer (round 3); XRF, VHX with LIBS (round 4) | a stub-prep station: carbon tape, powder, blow-off |
| 8 | Ship powder out | samples went to Amazemet by post; MSE Supplies confirmed them non-hazardous per IATA (DAL `alloy-workflow-review.md`) | | packaging station (round 4) | a dangerous-goods check per powder |
| 9 | Print | LPBF on the Aconity MIDI at the U of Utah (DAL #138, PR #169); copper by DED (DAL PR #117, #213) | | Aconity MIDI and the DED machine, beside the VLM | depowdering and build-plate handling |
| 10 | Cut parts off the plate | wire EDM | | FANUC ROBOCUT, beside the VLM | |
| 11 | Heat treat | solution treatment and ageing | | Nabertherm NAT 15/65, tray F (round 3) | |
| 12 | Density | Archimedes on 5 × 5 × 5 mm cubes (DAL #144) | | not modelled | open: a balance with a density kit |
| 13 | Metallography | mount, grind and polish with alumina | [alumina polish 1](https://www.youtube.com/watch?v=JmXvH10X9sI), [2](https://www.youtube.com/watch?v=nfnl0aPJPZc), [3](https://www.youtube.com/watch?v=eLrJxxBAcnE) | EcoMet 30 (tray F); OpenFlexure array and VHX for imaging | a mounting press |
| 14 | Mechanical testing | tensile, hardness, PIP (DAL #134), nanoindentation | | Instrons beside the VLM; PIP and iMicro on tray E | a hardness tester |
| 15 | Corrosion and electrochemistry | the CubXL with the NuVant EZstat Pro (byu-vcl #231; DAL #221, PR #177, PR #180); conductivity and spectroscopy with Dr. Porter (DAL #148) | | the CubXL, set up for corrosion (round 4) | |
| 16 | Long-term monitoring | optical monitoring of samples over time (DAL #233) | | the OpenFlexure array and the stream cameras | |
| 17 | Records | stream cameras to YouTube (DAL #147, PR #189); MongoDB | the channel | Pi 5 cameras on every tray and over the bay (round 4) | |

## Round 14 (run D): what this design does with each step

Sterling on round 12's card (PR #318, 2026-11-20): '11:43 "most by hand" is dissatisfying and misleading. For example,
coating the crucible is being explored as automated in another PR'. The table above is round 4's, and its last column
is out of date (the mounting press, the hardness tester and the BN recoat all have stations now). The long-form's card
(`longform.DAL_STEPS`, drawn as [`out/dal_workflow_table.png`](../out/dal_workflow_table.png)) now says, per step,
whether this design automates it and shows it, or has no station yet, and what inside the step is still by hand, in
progress, or open:

| # | Step | In this design | Status | By hand, in progress, or open |
|---|---|---|---|---|
| 1 | Pick a composition | Bayesian optimization over a CALPHAD-screened space | automated | |
| 2 | Weigh the charge | multi-doser + HR-202i, vacuum press, tray B (ch. 1) | automated | in progress: machining the cups and plugs (a separate PR); by hand until then |
| 3 | Coat the crucible (BN) | scraped and sprayed by the arm in a fume hood (`atom_bn`, #353) | automated | |
| 4 | Atomize | the rePowder, loaded, opened, cleaned and rebuilt by two arms (ch. 2, the turnaround clips) | automated | by hand: booster swaps and argon cylinders; the arm presses the HMI's keys until AMAZEMET opens an interface (DAL #151; `notes/atomizer_automation.md`) |
| 5 | Recover and sieve | the explosion-proof Nilfisk (`atom_vacuum`); the sieving cell with its wash module (ch. 3) | automated | |
| 6 | Store | the 753-jar store on trays N and O | automated | open: dry storage at about 25 % RH (DAL #131) |
| 7 | Characterize the powder | laser diffraction, XRD with its prep, XRF, SEM with stub prep (ch. 4) | automated | in progress: composition by ICP-MS, the new station (`notes/icpms.md`), shown in the corrosion chapter, not yet in the route |
| 8 | Ship powder out | the packaging station | automated | by hand: the dangerous-goods call for each powder |
| 9 | Print | the Aconity MIDI, fed by the arm; the depowdering box (ch. 3, 5) | automated | |
| 10 | Cut parts off the plate | the wire EDM, bars caught in a comb (ch. 5; #328's orientations) | automated | |
| 11 | Heat treat | the Nabertherm furnace on tray F (ch. 5) | automated | open: the schedule, DAL's to set |
| 12 | Density (Archimedes) | no station | no station yet | open: a balance with a density kit |
| 13 | Metallography | EDM sections, MX400 hot mounting, the PX500 with pre-loaded discs (ch. 6) | automated | by hand: re-papering the discs |
| 14 | Mechanical testing | tensile at 20 and 200 C (ch. 5); micro-Vickers, nanoindenter, PIP (ch. 7) | automated | by hand: the nanoindenter's tip change (the maintenance clip) |
| 15 | Corrosion | the CubXL and the OT-2 on tray A | automated | in progress: impedance (a potentiostat requested); the ICP-MS station, until which the samples go to BYU's facility |
| 16 | Long-term monitoring | the stream cameras only | no station yet | open: repeat imaging of stored samples (the OpenFlexure array was dropped in round 8) |
| 17 | Records | Pi 5 cameras on every powered tray and over each bay; MongoDB | automated | |

"Automated" means automated in this design and shown in the video; all of it is a design, not yet built. The
narration over the card now says so ("fifteen are automated and shown in this video, two have no station yet, and the
last column says what is still by hand, in progress, or open"), and the BN line in the turnaround chapter no longer
refers to the old card. In the last column, "by hand" is still a person's, "in progress" is being designed (in a PR or
this round), and "open" has no design yet.
