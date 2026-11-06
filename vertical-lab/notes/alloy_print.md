## The alloy route, chapter 3: sieve and print (`alloy_print.py`, `sieve_station.py`)

The atomized powder goes through a sieving cell, into the Aconity MIDI's powder supply, and the MIDI prints the
plate that chapter 4 ([`alloy_workflow.py`](../alloy_workflow.py)) takes out.
[GIF](../out/alloy_print.gif), [MP4](../out/mp4/alloy_print.mp4), [still](../out/alloy_print_still.png),
[steps](../out/alloy_print.json), stills of the [cell](../out/alloy_print_cell.png) and the
[tipper](../out/alloy_print_tipper.png). 198 s at 1280 × 720 and 10 fps (round 6, with the arm's collisions planned
round, below; 10 fps to fit the session; re-render at 15 fps when the runner is free); the GIF is 640 × 360 at 5 fps.

### Round 9 (PR #318, 2026-11-06): cleaning the sieves without a person, clear-glass jars with a legend

Sterling's review of 2026-11-05 22:56 UTC, verbatim: "Do we have some automation in place for cleaning the sieve stack? I
guess we could use that depowdering module in combination with ultrasonic IPA rinses?"; "Aconity MIDI door swings the
wrong way."; and, for every jar in the lab, "What's with the technicolor jars? Keep them all a normal black lid with
transparent glass, but if you want to point out something that's unique about them, use a legend and a color change that
then reverts once the legend has been shown for a bit of time."

| Point | Before | Now |
|---|---|---|
| Sieve cleaning | The stack went back on the stand with "between alloys it would go to an ultrasonic bath" in a caption | A wash module on a 450 mm extension of the bench, left of the tipper (`sieve_station.wash_parts`, own hood and duct). The No. 325, the finest cloth, is drawn through the whole cycle: (1) back in the tipper, turned over the funnel, vibrated 3 s (the Solukon-style depowdering, in small); (2) the arm sets it on a basket ring, a lift lowers it into an ultrasonic IPA tank (sped up from minutes), the liquid shimmers; (3) the lift raises it into a warm-air knife (a slot nozzle above and one below, travelling along the cloth); (4) the arm puts it back in the cradle and the MiR rolls back to the stand. The other five go through the same cycle but are not drawn (a repeat of 25 s each would add about 2.5 min) |
| Jars | white, lid off, 50 % | `props.jar_parts` style: clear glass (opacity 0.35), white label; the powder stays grey. Lids are off while a jar is under the funnel (not drawn; the black lid is `sieve_station.jar_lid`). After the sieving, each jar is tinted by its size cut for 6 s with a legend (`props.use_legend`, `pulse`), then fades back to plain |
| MIDI door | | The door is `alloy_models.py`'s (tensile stream's fix); this render picks up whatever is committed there |

**Is that a sound way to clean test sieves?** Mostly yes, with three cautions.

* *Ultrasonics.* Retsch says sieves with meshes finer than 500 µm should be cleaned in an ultrasonic bath, usually 2-3 min
  (3-5 min in the DAL #234 summary); its UR 1 takes one 8 in × 2 in sieve (the lab's size), UR range
  [data sheet](https://www.retsch.com/files/452777/product-data-sheet-ur.pdf). Retsch's cleaning agent is water with a
  surfactant ([white paper](https://www.retsch.com/files/17682/white-paper-different-sieving-methods-for-a-variety-of-applications.pdf)).
  An Advantech manual asks for at most 150 W, at room temperature, short runs, the sieve suspended and off the tank floor
  (DAL #234 summary, [comment](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/234)). The basket ring here
  holds the sieve off the floor. For a 45 µm cloth that is accepted practice; I found no source for sonicating 20 µm or
  electroformed micromesh, so do not extend the cycle to those without the maker's say.
* *Drying.* Retsch: dry below 80 °C, sieves upright, never hotter, since the fine wire mesh can warp and lose tension
  ([AS 200 manual, drying](https://www.manualslib.com/manual/1922097/Retsch-As-200-Tap.html?page=37)). Warm air at about
  60 °C through slot nozzles is inside that; remove rubber or plastic seal rings first (none on this stack). The air knife
  is a fixed low-pressure slot, not a hand-held compressed-air jet, which DAL #234 and Advantech warn distorts openings.
* *Why IPA for aluminium.* Fine Al in water makes hydrogen (DAL #234), and the lab's set is aluminium-only, so a solvent
  rinse is sensible. But DAL #234's own advice is not to put IPA or other flammables in an ordinary ultrasonic cleaner.
  Hence the module's shape: sonicate indirectly (IPA in a closed stainless vessel inside a water jacket; the drawing's tank
  is that vessel), at most a few hundred mL, under extraction, grounded, away from ignition sources, an
  explosion-proof or ATEX-rated unit if a direct bath is ever used (IPA flash point about 12 °C, and ultrasonic heating
  raises it). Remove the powder dry first (the vibration step does that): that cuts the IPA's metal-fines load, and the
  rinse slurry is hazardous waste, kept wet. Al fines under 63 µm are an ignitable dust, so the dry stages stay inside the
  downdraft enclosure; the module's own hood is drawn for that.
* *Standards.* ASTM E11 sets the wire cloth and frame tolerances; I did not find cleaning limits in it, and DAL #234's two
  Edison runs found no standard that gives a cleaning recipe or a "clean sieve" test either. A cleaned sieve should still
  be re-inspected (a calibrated-sample check or a microscope look at the cloth) per the lab's own schedule.

**Render (round 9).** 1816 frames, 302.7 s at 6 fps, 1280 x 720 (`VLAB_ONLY_TRAYS=F`, Shuttles clad); MP4 11.6 MB; the GIF
is every second frame at 640 x 360, `gifsicle --lossy=140 --colors 48`, 4.8 MB. **Collisions: not yet 0.** The last full audit
(before the render, same code) found 7 of 3402 frames: 1 in chapter 3 (the gripper's right fingertip against the
enclosure, frame 3063, not yet located: the audit's step log never got a slot) and 6 in chapter 4 (the forearm against the
Aconity's door twice, 3 frames each, going into and out of the chamber): the door as `alloy_models.door_T` now has it lifting
to 165 degrees above the front, where round 8's door swung inward, so the fill approach needs re-planning against it. The
render was started before that was fixed; re-run `PRINT_STEPS=1 ARM_AUDIT=1` (prints each step's first frame) and adjust.
The wash module's own moves were in that audit and produced no collision. Only the No. 325 is drawn through the wash cycle.

*Time (estimate).* Vibrate 2 min, ultrasonic IPA 3-5 min, warm-air dry 3-5 min, three transfers by the arm about 2 min: some
12-15 min per sieve, about 75-90 min for the six one after another with one module. Alternatives: a second module or a
bath that takes the whole stack (one UR 1 takes only one sieve, bigger UR baths several); one disposable or dedicated set
per alloy family, as DAL #234 advises (what the stand already assumes), which makes cleaning a between-campaign job
rather than a between-run one; a Retsch-style ultrasonic sieve cleaner, or none at all for a dedicated Al set (dry
recovery, frame tap, no wash) with the wash reserved for an alloy change. The module's sizes (tank 330 × 350 mm, hood,
lift, nozzles) are assumptions, not a product.

### Round 8 (PR #318, 2026-11-05): grey powder, the lab's real sieved jars, two Shuttles, 0 collisions

Sterling's review of 2026-11-05 00:37 UTC, the two points for this chapter, verbatim:

> The already sieved bronze powders are shown right after pulling it out, you should show the unsieved jar first,
> then show the sieved results after you actually do the sieving. See DAL for the issues and PRs related to sieving

> The powder that gets put into the sieve looks like multi-colored candy... keep it all gray at first, and only change
> the color after it's all settled and then you show the legend. After you show the legend, you should change it back
> to all gray.

| What | Round 7 | Round 8 | Why |
| --- | --- | --- | --- |
| The powder's colour | Each fraction its own colour from the moment it was poured (`instruments_char.sieve()`'s clusters), in the sieves and in the jars | Grey (`alloy_models.POWDER`, the container's powder) while it is poured, shaken and settles; then 0.8 s to the fraction colours with the legend ("What stays on each sieve") for 3.4 s, labelled *Coloured now only to tell them apart*; then 0.8 s back to grey, *it is all the same powder, only sorted by size*. The jars fill grey | Sterling, above |
| The lab's sieved result | In chapter 2, straight after the container came off the rePowder | Here, after the arm has done the sieving and every fraction is in its jar: Gage Erickson's photo of the Oct 27 bronze (lot k7m2q9) in three jars, < 63 µm (188 g), 63-250 µm (827 g) and > 250 µm (182 g), of 1,938 g melted in two runs, 5 s full frame, badged **REAL PHOTO · 630 bronze (NAB) · Oct 29 2026 · Gage Erickson, DAL #219** ([DAL #219 comment 6509252104](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/219#issuecomment-6509252104)). Chapter 2 now shows the unsieved powder (the k7m2q9 jar on the day of the run and the c3k0n5 bag and jar) | Sterling, above |
| The sieve set | The 8 in stack, No. 60 to the pan | The same six pieces, now named in the cell's caption: No. 60, 100, 140, 230, 325 and the pan, which is the lab's own stack since the No. 100, 140 and 325 arrived on Nov 4 ([DAL PR #175 comment 6642949111](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/175#issuecomment-6642949111): McMaster 7969T42, T43, T48, 304 stainless, 8 × 2 in) | DAL |
| The floor | `line.py`'s one-Shuttle line: the Aconity at x = 3250, where the second Shuttle now stands | `setup_lab.py`'s floor plan: the second Shuttle at x = 3630, the Aconity at 6950, the glovebox at −7300 turned to the aisle, the Instrons and the wire EDM on the south row ([`alloy_atomize_floor.py`](../alloy_atomize_floor.py), shared with chapter 2). The MiR drives 8.7 m from the cell to the Aconity, past both Shuttles. Chapter 5's depowdering box, lance post and rinse cup, which `alloy_workflow.build()` places round the old Aconity and which would stand in front of Shuttle 2, are left out of this chapter | the brief for round 8 |
| The MiR's cabinet | Chapter 4's plate carrier and bar holder, and two cups on 140 mm posts for the container and the jar | As chapter 2 leaves it: chapter 1's low cup carrier (empty: the cups went into the crucible) and the container in chapter 2's low cradle (a ring 37 mm tall), handle to the front; the LPBF jar rides in a pocket block like the carrier's (`props.pocket_block`, 26 mm deep, a lead-in) | round 7's low pocketed carrier (`alloy_charge.py`, `props.py`) |
| The jar into the MIDI | 97 frames in collision: the planner found no joint path through the 280 mm door, and its fallback put the forearm in the base cabinet's top | To the door in the IK branch that is clear at the supply cylinder (`alloy_workflow.branch_q`), then a straight line in and the same line out. A probe of 36 combinations (the MiR 250, 400 or 550 mm further off; the jar's grasp 60, 90 or 120 mm over the chamber floor; level or 12° down; on the cylinder's axis or 60 mm short) found four clear, all 250 mm off and level, with the grasp 60 or 90 mm up, on the axis or 60 mm short of it. Taken: 90 mm (the jar's foot 32 mm over the floor), 60 mm short, as before | the brief: collisions to 0 |
| The MiR250's drives (continuation 2) | `Mir2.drive`: the y leg first, as a sideways slide, then along x, on the old smoothstep ease (about twice the MiR250's published acceleration) | PR #321's `Mir2`, brought over: an S-curve with the MiR's long axis on the tangent (`props.s_curve`), from rest to rest at 0.3 m/s², up to 1.5 m/s (`props.ramp_frac`, `props.ramp_secs`) | a MiR250 is differential drive: it can't slide sideways; #321's published acceleration |
| Up to the bench for the LPBF jar (continuation 2) | the MiR slid 300 mm sideways, from 300 mm off the bench onto its usual line | 900 mm forward along an S-curve onto the line (at most 27° off it), then straight back the 900 mm, each from rest to rest | Sterling asked for anything else that couldn't happen as drawn |
| The last caption (continuation 2) | "chapter 4 takes the plate from here" | "Chapter 4 checks the sieved powder; chapter 5 takes the plate from here": round 8's seven chapters | round 8's route |

**Rendered (continuation 2, 2026-11-05 17:03 UTC):** 253.7 s at 6 fps, 1522 frames (`out/mp4/alloy_print.mp4`, 9.8 MB), the lab's sieved jars at frames 1040-1071. Arm audit at 6 fps: **0 of 1112 frames in collision** (`out/collisions/alloy_print.json`). Chapter 5's `alloy_workflow.py` and `alloy_models.py`, whose `build()` this chapter's scene is, were being rewritten by the tensile stream at the time, so this render (and its audit) ran with both pinned at commit `60dc682` (round 7's chapter-4 scene): the wire EDM and the Instrons in the background are as they were, without chapter 5's new catch comb. The GIF the scene wrote was 6.8 MB, so `out/alloy_print.gif` was remade from the MP4 at 3 fps and 512 x 288 (4.6 MB). The first try at this render died at its start with Xvfb's "Render window is not current" and was simply run again.

**What the lab does now, from DAL.**
- [DAL PR #175](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/175), *Sieve order for atomized powder:
  No. 60 scalp + 20–63 µm LPBF cut*: the lab's 8 in, 2 in deep, 304 stainless McMaster sieves. The Oct 28 review
  there ([comment 6479961909](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/175#issuecomment-6479961909)):
  the powder has too little under 20 µm for a lower cut to matter; hand sieving is fine at 63 µm for now; a used
  Ro-Tap (about $1.5–2.3k) before 45 µm cuts become routine. On grounding for the bronze
  ([comment 6480413613](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/175#issuecomment-6480413613)):
  the ignition risk of copper-alloy dust is far lower than aluminium's, but clip the lead on every time, since the
  same sieves and hood are used for Al.
- [DAL #234](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/234), *What is standard practice for
  cleaning sieves?*: Gage, Nov 3: "we used our 63um and 250um sieves on the bronze powder. Now we want to run aluminum
  through them". Its Edison answer is the cleaning paragraph below; on Nov 4 Gage asked whether to clean them or order
  another set. That question is open, and it is why the cell keeps a set per alloy family.
- [DAL #219 comment 6509252104](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/219#issuecomment-6509252104)
  (Gage, Oct 29): the photos of the sieved bronze, "Far left jar is <63um 630 Bronze powder", and the weights.
- Gage Erickson's three videos of 29 Oct 2026 (below): sieving by hand over a funnel into glass jars.

So the lab sieves by hand with two sieves (63 and 250 µm) today; the cell here, with six pieces, a shaker and a
tipper, is our design for doing the same without a person, and is marked as such.

**Round 5 (PR #318): no person.** Sterling, on "a person still takes the sieve stack apart": "The idea would be to
have the robot take care of this, or to use something more automated. ... some kind of clamping mechanism or clever
hardware-centric design." The arm now builds the stack, takes it apart, tips each sieve into its own jar and puts
the set back, with no second arm. What it takes is in [`sieve_station.py`](../sieve_station.py).

```bash
xvfb-run -a python3 alloy_print.py            # 40+ min on the 4-core runner when other renders share it
PREVIEW=1 xvfb-run -a python3 alloy_print.py  # last frame of each sub-step -> /tmp/preview_alloy_print.png
```

| Step | What happens | Who does it |
|---|---|---|
| 1 | MiR250 from the rePowder to the sieving cell | MiR |
| 2 | The stack built on the AS 200 from the Al set's stand, pan first (the pan in full, the rest sped up); the container from the MiR, tipped into the No. 60, back on the MiR; the lid from the tipper's roof, over the rods; both knobs turned; the stack shakes, see-through; the fractions panel | arm, then the AS 200 |
| 3 | Knobs back, lid back on the tipper's roof; each sieve, top down, into the tipper's cradle, which clamps it, turns it over the funnel and knocks the frame; the turntable puts the right jar under the funnel; the sieve back on the stand; the LPBF jar into a cup on the MiR | arm, tipper |
| 4 | MiR to the Aconity; door opens; supply piston drops; the arm carries the jar in, level, and pours; jar back on the MiR; door shuts | arm |
| 5 | The print as a time-lapse, cut open; MiR back to x = 1400 | the MIDI |

### The cell

| Part | What it is | Why |
|---|---|---|
| **Handling tab** on each sieve and the pan | 12 mm stainless tab at the front of the frame, 40 mm out, gripped like the plate's 12 mm lug (2F-85 at 0.88), fingers closing vertically; the pan's tab is held by its sides, 28 mm across (0.69), and every tab is approached with the gripper half open (0.5) | The 2F-85 opens 85 mm and a sieve is 207 mm across. Nested sieves leave only the top one's rim free, and a tab 50.8 mm above the next one leaves room for the fingers. The pan is the bottom piece on the shaker: fingers above and below its tab put the lower one and its knuckle in the shaker's housing |
| **The Al set's stand** | A 120 mm pedestal with a lip that takes a skirt, right of the shaker. The set waits nested in reverse: No. 60 at the bottom, pan on top (the pan sits on the No. 325's rim) | Off the stand top first, the pieces go onto the shaker pan first. Off the shaker top first, they go back in storage order, ready for the next run. No rack, no second arm. On round 5's 20 mm plate the No. 60's tab was so low that the gripper's lower knuckle reached into the bench |
| **Tipper** | A C-shaped cradle on a horizontal shaft (pneumatic rotary actuator), open at the front for the tab and the fingers; three pads clamp the frame; a pneumatic knocker taps the frame | The lab tips each sieve over a funnel by hand (below) |
| **Funnel and jars** | A Ø252 funnel over a turntable with five 250 mL jars, labelled: > 250, 150–250, 106–150, 63–106 and < 63 µm (LPBF). The No. 325 and the pan share the LPBF jar | Each fraction in its own jar |
| **Lid park** | The AS 200's clamping lid rests on the tipper's roof | The arm turns the two knobs, as before |
| **Enclosure** | Downdraft enclosure on the bench, 1150 mm tall, open at the front, extraction through the roof; a ground bar on the back panel and green-yellow straps to the shaker, tipper, stand | Al under 63 µm is among the most ignitable metal dusts (DAL's sieve note); Sterling asked for the grounding to be shown on DAL #175. At round 5's 950 mm the roof and the front rail left the arm no room over the tipper's roof and the knobs |

**Cleaning between alloys, from DAL #234's Edison answer** (Nov 3): use a separate sieve set per alloy family
("cleaning lowers carryover but can't prove there is none"), so the Cu-alloy set lives on its own stand. Recover
powder dry by tapping the frame, not the mesh; brush only No. 100 and coarser, lightly, from the underside; never a
wire brush or an air jet on the cloth; sonicate finer meshes 3–5 min in water with a mild detergent, then rinse and
dry upright. The tipper's knocker does the first. The clip doesn't show a brush or a bath: Retsch's UR 1 bath takes
one 200 × 50 mm sieve at a time (5.7 L, 35 kHz, timer 0–15 min, Retsch data sheet), so a bath step would be one
more station on the bench.

**Passes.** DIN 66165 allows at most 26 cm³ on a 200 mm, 63 µm sieve, about 35–40 g of powder at 1.3–1.5 g/cm³
(Retsch's table, via DAL PR #175). Four cups charge 157 g, so a run is about four passes; one is shown.

**What the lab does now** (Gage Erickson's videos "10/29/2026 Atomizer 630 Bronze cleaning and sieving", Videos
1–3, unlisted on the lab's channel, fetched at 144p by the parent session): the 8 in sieve shaken by hand over its
pan, the retained powder tipped out over a white plastic funnel into glass jars, the jars labelled on a P-touch and
weighed, the sieves brushed and wiped with Kimwipes. The NAB result is three jars (< 63 µm, 64–250 µm and
> 251 µm: 188 g, 827 g and 182 g of 1,938 g melted over two runs, DAL #219).

**Hand-offs.**
- **Start (round 8):** the MiR at x = −3487, y = −2230, arm parked, as chapter 2 leaves it
  (`alloy_atomize.END_POSE`): chapter 1's cup carrier, empty, and the container in chapter 2's low cradle at
  MiR-local (280, 10), handle to the front. Round 7 started on chapter 4's MiR (plate carrier and bar holder) with
  the container in a cup on a post; chapter 2 now also sets the container down handle to the front
  (`alloy_atomize.CRADLE_TURN`), so the two chapters meet in the same state.
- **End:** the MiR at x = 1400, `MIR_Y`, between the two Shuttles, arm parked; the Aconity closed and opaque; the
  plate under a 30 mm powder cake. On the MiR: the empty container in its cradle and the empty jar in its pocket.
- **Where the cell stands:** the bench is 1065 × 600 × 700 mm (assumed), x from −2515 to −1450, between the
  rePowder's heat exchanger and the VLM. Tipper at x = −2350, AS 200 at −1971, stand at −1623. Since round 7
  `setup_lab.py`'s floor plan has the same cell at the same place (`FLOOR_PLAN["sieve_cell"]`, `SIEVE_BENCH`), with a
  MiR dock 300 mm off it, as here.

### The arm's collisions (round 6)

Sterling, on PR #318: the arm "didn't respect collisions with itself, at all. Passed through the MiR250 and collided
with the vial holder." Round 5 of this chapter was rendered before `collide.py` landed. Checked with the planner
(`ARM_AUDIT=1`, every frame at 15 fps, [`notes/arm_collisions.md`](arm_collisions.md)), it had **543 of 2372**
frames in collision: the arm folded into itself, and its lower finger in the shaker and the bench, at the sieves'
tabs (2/5, 3/5); the container through the tipper and the parked lid; the forearm through the enclosure, the tipper
and the stack over the lid and the knobs; the forearm and wrist in the Aconity's base cabinet and chamber (4/5).
Now, as rendered: **97 of 2426**, every one of them in the Aconity (4/5); the sieving cell (2/5, 3/5) is clear
([`out/collisions/alloy_print.json`](../out/collisions/alloy_print.json)). Nothing was hidden or left out of the
check; `robot.py`, `collide.py` and the other shared modules are unchanged.

| What collided (round 5) | What changed | Why |
| --- | --- | --- |
| The arm in itself (shoulder and forearm, upper arm and wrists) and in the MiR's cabinet, at the tabs | The MiR parks 300 mm further off the bench than off the line (`CELL_DY`) | From the line's spot the tabs are 520 mm in front of the arm's base, and a level gripper there folds the arm with its elbow over the shoulder. From 820 mm it reaches them stretched out, and the self-collisions are gone |
| The lower finger and its knuckle in the shaker's housing (placing the pan) and in the bench (the No. 60 on its stand) | The pan's tab is held by its sides; every tab is approached with the gripper half open; the stand is a 120 mm pedestal | Fingers above and below a tab put the lower one about 40 mm under it when wide open (85 mm), and its knuckle lower still |
| The container through the tipper, the lid parked on it, and the sieves' tabs | It waits 260 mm in front of the stack, tips part way there, then goes in over the No. 60 as it tips the rest of the way, towards the stand | Beside the stack on the left it stood in the tipper; tipped in one move from upright its foot swept through the tabs |
| The lid through a rod on its way down | It is lowered from straight over its seat | `lid_grasp(2/3)` was still on the rig's way across (its path runs by arc length), so the line down cut the corner |
| The forearm in the enclosure's roof and front rail, over the tipper and the knobs | The enclosure is 1150 mm tall, not 950 | The lid and the knobs are taken from above: the wrist stands 300 mm over them |
| The fingertips on the knobs they turn | A grasp and a release are recorded for the knob the gripper turns | The rules let the gripper touch what it takes, within 4 s; the knob is taken and turned, just not lifted off its rod |
| The forearm in the bench's front edge, reaching under the funnel for the LPBF jar | The MiR rolls back up to its usual line first | From 300 mm further out the reach down to the jar was too long and low |
| The forearm and wrist in the Aconity's base cabinet and chamber, carrying the jar in | The MiR stops 250 mm further off the Aconity (`ACO_DY`); the jar goes in 20 mm lower and is poured 60 mm short of the supply's axis; door to cylinder and back are planned joint moves | The chamber's opening is 280 mm tall and the cylinder 540 mm behind the door. From the usual spot the forearm comes down into the cabinet's top. From further back both ends of the move are clear, but the move between them is not yet: see below |

**What is left: the jar into the Aconity (97 frames).** Each end of the move is clear (a grid search found IK
branches with the jar's foot 17 mm over the chamber floor, 60 mm short of the supply's axis, from 250 mm further
off), but the planner finds no joint path between the door and the cylinder in 2500 iterations: the opening is 280 mm tall and
the cylinder 540 mm behind the door. It then falls back to the straight joint line to the nearest solution, which
puts the forearm and the wrist in the base cabinet's top and the chamber's wall (91 frames going in, tipping and
pouring; 6 coming out). The next thing to try is a straight line of the gripper from the door to the cylinder in
the branch that is clear at the cylinder (solve the line backwards from there and start the move at the door in
that branch); if no branch is clear all the way, the pour needs a different reach: a funnel or chute at the
door, or the supply filled from outside the chamber. The highest point of the elbow and the wrists in the clip is
2.15 m.

Along the way: round 5, 543 frames; 159 after the MiR's spot at the cell, the tabs, the pedestal and the taller
enclosure; 140 after the knobs, the MiR rolling up for the jar, the container tipped towards the stand and the
MiR's spot at the Aconity; 97 after the lid straight down the rods, the container tipped in two moves and the
planned moves through the door, which took the cell to 0.

### Sources and assumptions

| Item | Value | Status |
|---|---|---|
| Shaker, lid, knobs, the fractions' colours | `instruments_char.sieve()`: Retsch AS 200 control | published |
| Sieves | DAL's 8 in, 2 in deep, 304 stainless McMaster stack (DAL PR #175), profiles from DAL's sieving model; here each its own group with a tab | DAL; the tab is ours |
| Stand, tipper, funnel, turntable, jars, enclosure, straps | `sieve_station.py` | **assumed, our design** |
| LPBF cut | No. 325 + pan, 20–63 µm; under 20 µm about 0.05 % (DAL) | from `instruments_char.md` |
| Powder in each jar | drawn heights, an example | **not data** |
| Supply fill caption | full MIDI cylinder about 440 g, its 55 mm reduction kit about 30 g (DAL #138); 1,080 g of 630 bronze in one run of the 225 cm³ crucible (DAL #219) | DAL |
| Gripper closures | 12 mm tab and handle 0.88, 36 mm crossbar 0.59, 54 mm knob 0.36, 70 mm jar 0.18 | approximate |

### Open questions and simplifications

- **Can the 2F-85 hold a loaded sieve by one tab?** About 0.7 kg 100 mm from the tab is about 0.7 N·m on the
  fingers. That is well inside the gripper's rating, but the tab has to be stiff and the pads must not slip.
- **The cradle's pads clamp a 0.6 mm wall.** A real cradle might clamp the rim lip instead, or take the sieve in a
  collet. Not checked against a real sieve.
- **Knocking the frame isn't brushing.** Fines left in the 45 µm cloth stay there until the set is cleaned; DAL
  #234 says that is the reason for a set per alloy family.
- **The jars are open.** A capped jar would need a decapper, or the jar goes to the MIDI open, as here.
- **The bench's sieving takes about 2 min on screen.** A real run is four passes of minutes each.
- **The lid is put back by the arm**; Fritsch's ANALYSETTE 3 PRO, with motor-tensioned clamping, would take the
  knobs out of the job.
- **The arm pours into the MIDI's supply through the door**, as before; in practice the MIDI's supply is filled by
  hand.
