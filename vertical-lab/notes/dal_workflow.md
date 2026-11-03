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
| 12 | Density | Archimedes on 5 × 5 × 5 mm cubes (DAL #144) | | not modelled | a balance with a density kit |
| 13 | Metallography | mount, grind and polish with alumina | [alumina polish 1](https://www.youtube.com/watch?v=JmXvH10X9sI), [2](https://www.youtube.com/watch?v=nfnl0aPJPZc), [3](https://www.youtube.com/watch?v=eLrJxxBAcnE) | EcoMet 30 (tray F); OpenFlexure array and VHX for imaging | a mounting press |
| 14 | Mechanical testing | tensile, hardness, PIP (DAL #134), nanoindentation | | Instrons beside the VLM; PIP and iMicro on tray E | a hardness tester |
| 15 | Corrosion and electrochemistry | the CubXL with the NuVant EZstat Pro (byu-vcl #231; DAL #221, PR #177, PR #180); conductivity and spectroscopy with Dr. Porter (DAL #148) | | the CubXL, set up for corrosion (round 4) | |
| 16 | Long-term monitoring | optical monitoring of samples over time (DAL #233) | | the OpenFlexure array and the stream cameras | |
| 17 | Records | stream cameras to YouTube (DAL #147, PR #189); MongoDB | the channel | Pi 5 cameras on every tray and over the bay (round 4) | |
