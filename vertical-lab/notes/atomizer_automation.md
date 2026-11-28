# Automating the atomizer: every step of a run, by robot (#353, for #303)

Sterling on #318 (2026-11-19): automate "all aspects of the process": the plate swap, the crucible change, cleaning
the crucible, recoating it with BN, screwing on the graphite nut, the explosion-proof vacuum with the lab's safety
workflow (it was missing from the BoM and the visualizations), the arm vacuuming the inside of the chamber, removing
the dispense container, the furnace latch actually clamped and unclamped, and DAL's melt-chamber and melt-stream
cameras with their displays.

This note is the map. It takes every line of the lab's own run checklist and says who does it in the automated cell,
with what, and what is sensed, and which clip shows it. The clips' own notes (`atom_*.md`) have the details.

**Sources.** Unless a line says otherwise, the procedure is the lab's, not ours:

- DAL's current SOP checklist, Gage's notes checked against the training videos and the runs from Oct 2 to Nov 5
  ([digital-alloy-lab PR 253](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/253), `SOP/atomizer-sop.md`).
- The detailed SOP with a video timestamp for every step
  ([digital-alloy-lab PR 178](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/178),
  `atomizer-training/sop.md`, with `manual.md` and `equipment.md`). Video codes below (T1-T9, TA, SP, OCT2a/b) are that
  SOP's.
- The 630 bronze run plan's crucible coating section
  ([digital-alloy-lab PR 220](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/220)).
- The viewport cameras ([digital-alloy-lab PR 189](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/189)) and
  the display bench test ([PR 258](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/258)).
- The Nilfisk CFM 118EXP operating and disposal SOPs ([byu-vcl PR 80](https://github.com/vertical-cloud-lab/byu-vcl/pull/80),
  moved to [digital-alloy-lab PR 186](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/186)).
- This repo's [`crucible_automation.md`](crucible_automation.md) (round 7) and
  [`repowder_refine.md`](repowder_refine.md) (the model, #327).

## The cell

- **Two MiR250 + UR10e units**, the same as chapter 2's: each a UR10e with a Robotiq 2F-85 and a RealSense D405 on the
  wrist, on a MiR250 with a 131 kg steel ballast plate under its cabinet (round 9; `alloy_atomize.stability()` checks
  tipping and sliding). Arm 1 works from the front (the furnace, the lid, the container); arm 2 from the left, beside
  the chamber's door (the stack, the plate, the nut under the crucible, the inside of the chamber). Many steps need
  both at once, as they need two hands now: one holds, the other turns (the crucible and its nut, the plate's two
  wrench flats), or one supports while the other clamps (the container).
- **Tools the 2F-85 holds by a handle**, as chapter 2's loading tong does, each with its own holder: the vacuum wand,
  brushes, a scraper, tweezer fingers, insulation paddles, a crucible gripper, a nut key, a torque-limited stack wrench,
  a gauge plate, a BN spray-can tool. Where a tool has to deliver or react a torque the gripper can't (50 N·m on the
  plate), the reaction is closed inside the tool and the arm only positions it ([`atom_plate.md`](atom_plate.md)).
- **The machine's own program** does the gas washes, the heating, the melt, the pour and the venting, as it does for
  people now. What a person does with the HMI is pressing keys at the right moment (DAL SOP, "Atomizer Trial", steps
  1-35). An arm can press a Weintek touchscreen with a stylus, but the sound route is an interface AMAZEMET supplies or
  allows. The HMI is a Weintek cMT2166X; AMAZEMET's newer units have an "Advanced Control Cabinet" with a PLC and an API
  for remote process control ([DAL issue 151](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/151)).
  Whether ours can have one is the first question for AMAZEMET. Until then, the clips have the arm press the keys and
  say so.
- **The cameras** of DAL PR 189 watch the melt (through the lid window) and the stream on the plate (through the front
  view port and the door's sight glass), each with its own display by the machine. In the automated cell they are also
  the robot's checks: the plate's position before closing, the landing during the pour, the plate's state after it.

## Every step of a run, and who does it

"Arm" steps are animated in the clips named; "machine" steps are the rePowder's own program; "person" steps stay with
a person, with the reason.

### Start-up (DAL SOP "Start Up"; PR 178 "Operator checklist" and "Utilities")

| Step (SOP) | In the cell | How, and what is sensed |
| --- | --- | --- |
| Recording cameras on | machine | The viewport cameras and the room camera stream all day ([`atom_cameras.md`](atom_cameras.md)) |
| Gloves, lab coat; ground wire checked | arm / sensor | The arms need no PPE. The ground wire's continuity is a measurement, so a fixed milliohm check on the machine's bonding point, logged each start (ours) |
| Leaks, damaged wires, clean inside and out | camera + person | The viewport cameras and the wrist D405 see the inside; a person's daily walk-round stays, as the manual asks |
| Vacuum-pump oil in the sight glass | camera | A fixed camera on the sight glass (ours); the pump's oil change stays a person's job (DAL "Maintenance") |
| Heat-exchanger water level | sensor | A level switch, or a camera on its marks (ours) |
| Argon: cylinder pressure noted, regulator at 8 bar | sensor + person | A pressure transducer on the cylinder side (ours); the cylinder swap is a person's (two cylinders at most in the booth, none manifolded: the industrial hygienist's rule) |
| Chilled water opened about 20 deg | valve | A motorised valve (ours) instead of a hand valve, set once against the "water too cold" alarm |
| Compressed air on, ~4 bar | valve | A solenoid valve (ours) |
| The big red switch; HMI login; program; 10 s wait | arm or interface | The red switch is a rotary isolator: a person turns it on in the morning (it is the machine's safety isolator, so it stays manual). Login and program by interface, or the arm with a stylus |

### The ultrasonic tower (DAL SOP "Configuring the Ultrasonic Tower")

| Step | In the cell | How |
| --- | --- | --- |
| Booster chosen and oriented; housing on its O-ring, 4 bolts | person | Only on a booster change, rare: the transducer is "very expensive, don't drop it" (DAL issue 161: one slip $5-10k), and only trained people handle it |
| Threads cleaned with IPA; transducer-booster 65 N·m, booster-sonotrode 60 N·m in the soft-jawed vise | person | The same reason. A bench fixture with a torque tool could do it, not in this PR |
| Cover bolted on, cable locked, air on, cable on its holder | person | Ditto |
| Frequency scan on the bench | machine | |
| Protective plate inside; seal; stack into the housing; clamp | person | Done with the stack, rarely |
| Connector into the lower sonotrode; **plate on; upper sonotrode on; 50 N·m; oriented; height set with the gauge plate; rescan; wet test; landing checked; seals wiped; hatch closed** | **arm 2** | [`atom_plate.md`](atom_plate.md), clip `atom_plate`: every run that changes alloy or finds the plate cracked |

### Loading the furnace (DAL SOP "Loading the Furnace")

| Step | In the cell | How |
| --- | --- | --- |
| Nozzle: light through the bore; globs off with tweezers; drill if closed | arm 1 | Tweezer fingers; the D405 (or a fixed backlit camera) looks for light through the bore; drilling by hand stays a person's (a 0.5-0.7 mm drill in graphite) |
| Crucible BN-coated the night before, dry | **arm 1** | [`atom_bn.md`](atom_bn.md), clip `atom_bn` |
| Rebuild: nozzle in holder white side up; crucible snug, never forced; seal, bottom insulation, crucible into the coil, **graphite nut on from below**; the TC hole lined up with the thermocouple | **arms 1 and 2** | [`atom_crucible.md`](atom_crucible.md), clip `atom_crucible_in` |
| Side insulation's hole on the TC port; TC bent close; top insulation pushed in | arm 1 | Same clip |
| Sealing rod: tip clean; stood on the nozzle; lever down; safety pin; SEALING ROD | arm 1 | Same clip, and chapter 2 |
| Splash disc in the container's flange; container clamped with its valve open; catch bowl in | **arms 1 and 2** | [`atom_latch_container.md`](atom_latch_container.md), clip `atom_container` |
| Charge cleaned and weighed (250-300 g Al) | arm 1 | Chapter 1 makes the charge cups; chapter 2 loads them with the tong |
| Furnace seal wiped with IPA; **lid closed; latch adjusted until nothing hisses** | **arms 1 and 2** | Clip `atom_latch`, and chapter 2 with the same moves (`atom_latch.Work`): arm 2 the lid by its knob, arm 1 the loop and the lever; since round 14 no arm presses on the lid |

### The run (DAL SOP "Atomizer Trial", "End of run")

The cold purge, the 250 °C and 500 °C washes, the melt, the 2 min hold, the scan, the amplitude, Ultrasonic Start,
Graining Pressure and Sealing Rod, the turbo pulses, and the end-of-run sequence are all keys on the HMI and are the
machine's (by interface, or the arm pressing keys). What needs eyes is the pour: "Watch the plate the whole pour"
(step 30). In the cell that is the front and left viewport cameras, whose pictures also go to their displays; a person
still watches the first runs. The O₂ reading (the low 20s ppm ideal, above 29 ppm wash again) and the generator's
display (a trip freezes the nozzle, Nov 5) are read off the HMI and the generator: an interface, or a camera on each
(DAL issue 151's comment: "a camera positioned above the HMI is probably the quickest way").

**Steering the plate during the pour (round 14, ours; chapter 2).** Sterling (PR #318, 2026-11-20): "we can probably
have the two arms working together to adjust the position of the plate in real-time during the several minutes of
atomization". A two-axis landing stage between the chamber's door and the stack's housing, sealed by an edge-welded
bellows, moves the stack under argon: one axis slides it along its axis (the stream lands nearer to or further from the
plate's hole; the lab sets it at 75 mm, #261), the other moves it across, under the stream. Each is a lead screw, 8 mm a
turn, with a braked hex knob on top; arm 2 (left of the door) holds one knob and arm 1 (front left) the other through
the pour. The melt-stream cameras above give the landing along and across the plate in mm, and the cell turns a knob
an eighth or a quarter of a turn when it is more than 1 mm off. To check with AMAZEMET: the stack's seal at the door,
the transducer's cable and cooling air, and whether the plate may move while it vibrates. Details in
[`alloy_atomize.md`](alloy_atomize.md#steering-the-plate-in-the-pour-ours).

### Cooldown and shut-down (DAL SOP "Cooldown and Shut Down")

| Step | In the cell | How |
| --- | --- | --- |
| Wait to ~400 °C | machine | Graphite is safe in air below it |
| Melting Pressure off; Pressure Control off; **Vent Valve**; open | machine, then arms | The chamber door locks off atmosphere (T5 44:19) and the latch's bolt locks the lid; the arms open both only after the HMI reads atmosphere |
| Argon cylinder closed | valve | A solenoid on the regulator's outlet (ours); "a cylinder left open leaks empty" |
| ~100 °C: heat exchanger off, chilled water, compressed air, power | valves, person | |
| Lid closed against dust | arms 1 and 2 | Clip `atom_latch` |

### Powder collection and cleaning (DAL SOP "Powder Collection and Cleaning")

| Step | In the cell | How |
| --- | --- | --- |
| Paper under the opening | arm | A tray on the MiR under the door (ours) |
| Powder brushed from the plate, cone, view port and bowl into the cup; dust settles | **arm 2** | Clip `atom_container`. Round 14: the brush has a square grip between two collars and a V-rest with a fin slot, and **one disposable head per run** from a magazine on its rest, stripped into a grounded can after (`atom_brush.py`; ultrasonic IPA cleaning rejected, [`atom_latch_container.md`](atom_latch_container.md)) |
| **Cup's valve closed; cup removed**; powder into a jar; cup cleaned | **arms 1 and 2** | Clip `atom_container`; the jar and its 6-character ID go on through chapter 3 |
| Splashes, bowl metal and leftovers weighed separately | arm | On chapter 1's balance |
| Door, sonotrode and plate cleaned; **plate off if cracked**; never ground; one alloy per plate; condition logged | arm 2 | Clip `atom_plate` |
| Chamber, view port, crucible stand, splash plate and cone cleaned: **vacuumed with the ATEX vacuum**, then wiped; never compressed air | **arm 2** | [`atom_vacuum.md`](atom_vacuum.md), clip `atom_vacuum` |
| Once cool: slag out, nozzle checked, **furnace rebuilt** | **arms 1 and 2** | Clips `atom_crucible_out`, `atom_bn`, `atom_crucible_in` |
| Every seal and its face wiped with IPA before closing | arms | A wipe tool (pre-saturated 70 % IPA wipes: the vacuum SOP's choice, no spray bottle near powder) |
| Cup back on, valve open | arms 1 and 2 | Clip `atom_container` |
| Screens and handles wiped | arm | |
| Floor swept outside the yellow lines; sweepings and full liners to their buckets; pickup request | person | The vacuum's liner is sealed by a gooseneck twist and carried to the grounded pail: a person's job here ([`atom_vacuum.md`](atom_vacuum.md)) |
| Jar and leftovers to the closet; videos to YouTube | arm / software | |

### Maintenance (DAL SOP "Maintenance")

Daily looks (coolant, leaks, seals) by camera; weekly pump oil, KF clamps and cabinet, every 20 h the safety filter,
flapper seals and pump filter, the HEPA into sand every two months, the hinges quarterly, and the yearly work stay with a
person or AMAZEMET. `upkeep.py` already books these into the lab's year.

## Safety, in the cell

The lab's rules, and what each becomes when an arm does the work:

- **Never open the chamber above atmosphere: vent first.** The machine locks the door and, through the latch's bolt,
  the lid. The arms' programs read atmosphere on the HMI before reaching for a clamp or the latch.
- **Never compressed air once powder has been in the machine.** No tool in the cell uses it; cleaning is brush,
  vacuum and dry wipe, as the SOP says.
- **Combustible metal dust: bonding and grounding.** The vacuum's ground chain is checked before every use, joint by
  joint, to 0.1 Ω (UL 1213 par. 22 via Nilfisk's manual; byu-vcl PR 80); the arm does this on a fixture
  ([`atom_vacuum.md`](atom_vacuum.md)). Every tool that touches powder (the wand, the brushes, the scraper) is metal or
  conductive and bonded through the arm's flange to the MiR's ground and the building's. Round 14 (ours, to be checked
  by EHS; `atom_ground.py`, [`atom_vacuum.md`](atom_vacuum.md)): a stainless plate set flush in the floor at every spot
  a MiR250 parks to work at the atomizer, its leads in a floor channel to the area's ground bar; each MiR250 lowers two
  sprung copper-graphite shoes onto it when parked, and no arm moves near the powder until shoe to shoe and plate to bar
  both read 1 ohm or less (the MiR's bond lamp turns green). Nothing to clip on, nothing trailing. Shown in the vacuum
  clip and on both units in chapter 2. The vacuum SOP's isolated-conductor sweep covers the MiRs and their carried
  parts: every metal object near the powder bonded or out of the zone.
- **A Class D extinguisher at the station**, never water, CO₂ or ABC. The two units stay outside the yellow lines
  while powder is out unless they are working.
- **Hearing protection while the ultrasonics or induction run**, the full-face P3 respirator before the chamber
  opens: these are for people, and in the automated cell a person stays out of the enclosure while the arms work and
  the dust settles (the SOP's 60 s settle, the vacuum SOP's 60 s after switching off).
- **The transducer and the stack:** the arms don't take the stack apart (above). The plate swap stays on the door.
- **Hot graphite:** nothing is touched above 400 °C (open) and the graphite only once it can be touched; the arms
  read the furnace temperature before reaching in.
- **Alloy families are kept apart** (Al with copper oxide is a thermite pair): per-alloy plates, crucible, nozzle,
  sealing rod and sieves, and, for the vacuum, one unit per family ([`atom_vacuum.md`](atom_vacuum.md)).
- **Powder stays at the atomizer, not on the arms.** The units go on to other workflows, so for the powder phase each
  arm wears a dissipative, bonded sleeve that ends in the atomizer's own gripper on a tool changer, put on and taken
  off at a stand on the tape line, one set per family ([`atom_sleeve.md`](atom_sleeve.md), with how far up the arm the
  powder reaches in each clip).

## What stays a person's job, and why

- The stack's booster, transducer and its 65 / 60 N·m joints: rare, and a slip costs $5-10k (DAL issue 161).
- Sealing the vacuum's liner (a gooseneck twist and conductive tape or two steel ties) and carrying it to the pail.
- Turning the machine's main isolator on and off; swapping argon cylinders; the pump's oil and filters; the HEPA into
  sand.
- Drilling out a closed graphite nozzle.
- The first "snug" on new graphite: the torque limits the arms use are set from bench trials with spare graphite, by a
  person who has the feel Bartosz taught (DAL SOP: "have someone show you the first time").
- Watching the first automated pours, and every pour of a new alloy family.

## Questions for AMAZEMET

1. Can our rePowder take the Advanced Control Cabinet's API, or any remote interface to the HMI's keys (the Weintek
   cMT2166X's own remote options), so a cell controller can run the program? Which signals are allowed (SEALING ROD,
   Vent Valve, the pressures, the temperature, O₂, the generator's state)?
2. The latch: what is its adjustment ("adjust the latch until nothing hisses"), and what does the pneumatic bolt
   engage? The model's over-centre geometry is ours ([`repowder_refine.md`](repowder_refine.md), third pass).
3. The crucible's and the nut's thread: pitch, and a torque figure for "snug" on new and on used graphite.
4. The chamber door's opening angle, and whether anything may be fixed to the door (the left camera unit rides on it).
5. The container: its mass empty, and whether a second container can be bought, so one is cleaned while the other is on.

## The model, corrected on the way

- **The lid is hinged on the left.** #327 had it hinged at the back, where it opened into the blue cabinet. DAL PR 189
  measured it on the left, with the window on the front facet and the knob to its right. The latch is on the housing's
  right face, and its bolt runs back into the cabinet ([`repowder_refine.md`](repowder_refine.md), fifth pass).
- **The latch is built as the footage shows it:** the lever pivots at its top, and the loop has its own pivot and
  hooks a keeper on the lid. The latch clip found three faults in the parts and draws corrected ones
  ([`atom_latch_container.md`](atom_latch_container.md)).

## The clips

| Clip | What it shows | Notes |
| --- | --- | --- |
| `atom_cameras` | DAL PR 189's three viewport cameras, each with its live view on its own display; the top arm parked and back | [`atom_cameras.md`](atom_cameras.md) |
| `atom_latch` | The latch unclamped (bolt back, lever through dead centre, loop off) and clamped; the lid about its left hinge | [`atom_latch_container.md`](atom_latch_container.md) |
| `atom_container` | Powder brushed into the container, the dust settled, the valve shut (the removal is written but not rendered) | [`atom_latch_container.md`](atom_latch_container.md) |
| `atom_vacuum` | The Nilfisk CFM 118EXP: continuity check, equalization touch, slow passes inside the chamber, run-on, settle | [`atom_vacuum.md`](atom_vacuum.md) |
| `atom_plate` | The plate swapped through the open door, 50 N·m with the stack wrench, gauge plate, wet test | [`atom_plate.md`](atom_plate.md) |
| `atom_crucible_out` | Thermocouple, rod, insulation; the crucible off its graphite nut, held from below | [`atom_crucible.md`](atom_crucible.md) |
| `atom_bn` | The crucible cleaned and its BN coat touched up in the hood; dried overnight; checked | [`atom_bn.md`](atom_bn.md) |
| `atom_crucible_in` | The rebuild; the nut threaded on from below while the crucible is held; snug; the thermocouple hole lined up | [`atom_crucible.md`](atom_crucible.md) |

The audit numbers, the reel and the merged bill of materials (`out/atom/bom.md`) are in PR #353's description.
`atom_timeline.py` draws the turnaround as a timeline (`out/atom/turnaround.png`); its arm times are estimates.
