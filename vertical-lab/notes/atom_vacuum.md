# The explosion-proof vacuum, and the arm vacuuming the inside of the chamber (PR #353, #303)

Sterling, on PR #318 (2026-11-19): "using an explosion-proof vacuum and the same sort of safety workflows as described
here and in DAL (see e.g., nilfisk from #80) (note: you may have missed adding this to the BoM and to the visualizations
with a faithful reconstruction - you should add this in, potentially multiple depending on needs), having the arm grab
the vacuum attachment and doing an actual vacuuming of the inside of the chamber".

| File | What |
| --- | --- |
| [`atom_nilfisk.py`](../atom_nilfisk.py) | The models: the Nilfisk CFM 118EXP, the hose (a relaxed chain), the wand, cuff, crevice tool and dust brush, the steel pail, the Class D extinguisher on its stand, the area sign, and our station |
| [`atom_vacuum.py`](../atom_vacuum.py) | The clip `atom_vacuum` |
| [`out/atom/vacuum_bom.json`](../out/atom/vacuum_bom.json) | The bill of materials, with the vacuum count |
| `out/atom_vacuum.{gif,json}`, `out/mp4/atom_vacuum.mp4`, `out/atom_vacuum_still.png` | The render |
| `out/collisions/atom_vacuum.json`, `out/collisions/atom_vacuum_hose.json` | The arm audit and the hose check |

## Sources

- **Vacuum SOP**: byu-vcl PR 80, `vacuum-operating-sop.md` (Rev 1, 2026-09-04), cited as "SOP section".
- **Accessories doc**: byu-vcl PR 80, `vacuum-accessories-options.md`: part numbers, prices, the bin's size, the OEM
  manual's accessory BOM 01760495 and its continuity rule (sections 11, 15).
- **DAL atomizer SOP** (`253_atomizer-sop.md`), "Powder Collection and Cleaning" step 7: "Clean the chamber, view port,
  crucible and crucible stand, and the splash plate and cone down to the cup. Vacuum with the ATEX vacuum, then wipe.
  Never compressed air." "Copper Alloys" step 1: "Keep copper and Al residues apart (Al with copper oxide is a thermite
  pair)."
- **DAL detailed SOP** (`178_sop.md`), "Cleaning and maintenance": vacuum first, then wipe; the only crevices are the pump
  port and the view port (T4 6:51, T7 1:14); the cone swings out, take it down and vacuum its seal from below (T4 8:08);
  material change: vacuum everything, about 1 h (T5 67:38). `178_equipment.md`: the ATEX vacuum in hand is a Nilfisk
  CFM 118EXP; full liners go in a labelled metal bucket (Risk Management, 2026-07-20).
- **Nilfisk 118 EXP/EXPW brochure**, as quoted by a web search on 2026-11-19 (Nilfisk's spec page and PDF returned
  403/429 to the fetch): 6.6 gal tank, 20 x 24 x 45 in (L x W x H), 57 lb, CSA Class I Group D, Class II Groups E, F, G;
  304 stainless container, filter chamber and trolley.

## The model (`atom_nilfisk.py`) and where each size comes from

| Part | Size | Source |
| --- | --- | --- |
| Overall | 508 x 610 x 1143 mm (20 x 24 x 45 in), 25.9 kg | brochure |
| Bin | 320 mm ID, 311 mm deep (6.6 gal at that ID), 406 mm over the rim gasket | accessories doc 9.5, 10.4 (12.5 in ID), 10.7 ("about 16 in" with gasket); depth computed |
| Main filter | 360 mm antistatic sleeve, 40000460 (not drawn: inside the housing) | accessories doc 2a |
| Inlet | 38 mm (1.5 in) stub on the bin's side, z 410 | accessories doc header; height estimated from photos, +-40 mm |
| Filter chamber, motor head, downstream HEPA housing | z 440-700, 700-905, 905-965 | estimated from photos, +-50 mm |
| Trolley | 440 mm wheelbase, 50 mm castors | estimated inside the brochure's envelope, +-40 mm |
| Switch | sealed box with a rocker on the motor head | estimated from photos |
| Electrics | 120 V, 10 A, 1000 W; 130 CFM; 69 in water lift | accessories doc header (a used listing says 95 CFM, 85 in: not used) |
| Wand 01768601 | 508 mm (20 in), 38 mm OD | **length assumed** (+-150 mm): no source gives it. Measure the lab's |
| Cuff 4072000343 | 52 OD x 90 | estimated |
| Crevice tool 01768900 | 279 mm (11 in), flattening to a 34 x 11 mm slot cut at about 45 deg | length from the accessories doc 3b; slot estimated |
| Dust brush 01719401 | 76 mm (3 in) head, 28 mm conductive bristles, 120 mm long | estimated (the Ruwac kit's brush is 3 in) |
| Hose | 3048 mm (10 ft), 50 mm OD | 107413543 / 01769218, accessories doc 1; OD estimated |
| Pail Uline S-7344 | 340 mm (13.4 in) tall, 298 mm top OD, 273 mm bottom OD | Uline's S-20030BL figures (Hydrobuilder listing), a proxy: S-7344's own sizes were not found |
| Class D extinguisher Amerex B570 | 13 x 8 x 35 in, 30 lb NaCl | Airgas listing |

The tools share one collar design (a 17.4 mm spigot into the wand's 35 mm bore, a 44 mm collar ring, a 38 mm neck), so
the rack can hold any of them. The spigot and collar sizes are estimates.

**The hose** is a chain of 36 links relaxed every frame by position-based dynamics: gravity, fixed link lengths, a bend
limit (no kink tighter than about a link, 87 mm, in radius), the floor with friction (nodes resting on it don't slide),
and obstacles (the MiR250 and its cabinet, the vacuum, the station, the chamber, the open door and stack, the pump, the
pail, the arm's links as capsules, the wand). Each end leaves along its fitting's axis. Its drawn length stays within
about 3 % of 3048 mm (the links stretch a little under gravity).

## Who does what

| # | Step | Who | Source |
| --- | --- | --- | --- |
| 0 | After the run: cold, vented, door open; powder brushed into the container, the container's valve closed and the container taken off | a person (other clips) | DAL SOP collection steps 1-3 |
| 1 | Area checks: the vacuum's ground cable to the ground bar, the station and the pail bonded, extinguisher and pail staged, sign up | a person at the start of the day; the clip shows the result | SOP 2.2, 2.3 |
| 2 | MiR250 2 parks in front of our station | MiR250 2 | ours |
| 3 | Take the wand (crevice tool fitted) from the holster by its fin | arm 2 | ours |
| 4 | Continuity: the tool tip on the bonded spring pad, three spring probes on the joints, a relay box switches the 4-wire meter; each joint <= 0.1 ohm, the hose <= 1e4 ohm, the body < 1 ohm to ground, or the run stops | arm 2 + our fixture | OEM manual (UL 1213 par. 22, accessories doc 15.1), SOP 1.1 |
| 5 | Equalization touch on the bonded ground button, away from the powder | arm 2 | SOP 3.1 |
| 6 | Vacuum ON before the powder (a switched outlet, ours) | the cell | SOP 3.2 |
| 7 | Passes through the door: round the inside of the view port; down the 45 deg floor towards the outlet in two lanes; round the catch bowl's near side and into the outlet's mouth; along the front corner where the floor meets the front wall | arm 2 | DAL SOP step 7; 178 SOP T4 6:51; SOP 3.3-3.5 (slow, nozzle close, never blow) |
| 8 | Tool change: the crevice tool into pocket A (its collar between two slotted plates), the wand pulled off it, the wand pushed onto the brush in pocket B, out to the front | arm 2 + our rack | ours |
| 9 | Brush-and-capture: the brush on the plate (on the open door), then along the door's sealing face (its free edge and top) | arm 2 | SOP 3 (brush), DAL SOP step 6 (door, plate) |
| 10 | Lift clear; run-on 20 s in clean air; OFF; wait >= 60 s; liner check <= 25 % | arm 2 + the cell | SOP 4.1-4.3 |
| 11 | Wand back in the holster | arm 2 | ours |
| 12 | Liner sealing (gooseneck, 2-3 turns, ESD tape or two steel ties), lifting it into the pail, lid set on, a fresh liner; wiping the tools (dry, then a barely damp 70 % IPA wipe), the session log | **a person** | SOP 4.4, 5, 10 |
| 13 | The far side of the catch bowl and the round end, the cone taken down and its seal vacuumed from below, the view port taken out with the hook wrench | **a person** | 178 SOP T4 7:49, 8:08 |

The arm stays outside the chamber: only the wand and the tool go through the door. The tool never touches what it
cleans except the brush's bristles (a soft part in the audit) and the two spring contacts.

## What is ours, and why

- **The wand's clamp collar and fin.** The OEM manual: "Any alteration to this equipment by a third party will nullify
  its certification" (accessories doc 15.1). So the collar clamps on (54 mm OD, 60 long) and nothing is drilled. The fin
  is 30 mm thick, so the 2F-85 closes to 0.68 (`ur_arm.close_for(30.3)`). The 6 mm pin under the collar drops into a
  hole in the holster's fork, so the wand always hangs in the same roll and the arm's grasp repeats. Open question: the
  collar must be conductive and bonded to the wand (an isolated conductor is the hazard the SOP hunts for, 2.3), or
  non-conductive and small; ask Nilfisk and EHS which.
- **The station** (two: one per vacuum station): a bonded steel post with the holster, the tool rack (two keyhole
  pockets: the lower plate carries a tool by its collar, the upper plate holds it down while the wand pulls off), the
  continuity fixture and the ground button.
- **The automated continuity check.** The SOP's meter (EXTECH 380560 class, resolves 0.01 ohm) reads 4-wire through a
  relay box that switches its leads between the probe pairs: tool tip (pad) to the wand above the tool joint; the wand
  under the collar to the cuff; the cuff to the vacuum's inlet; the body to the ground bar. The readings on screen
  (0.04, 0.02, 0.03, 4.1 and 0.2 ohm) are illustrative. **The lab's own crevice tool read open (megohms) on 2026-08-19
  (SOP gate 0.1)**: until the SOP's remediation ladder (1.4) clears it, the fixture would stop this run, and the SOP's
  fallback is the dust brush alone.
- **The liner fill** is shown from an assumed load cell under the trolley; the SOP checks it by eye when the head comes
  off. **The vacuum's switch**: a switched outlet controlled by the cell, not a change to the vacuum; to clear with
  Nilfisk and EHS.

## Forces and timing

- Tool push-on and pull-off: about 30 N, assumed (a slip fit; not measured). The UR10e's 12.5 kg payload and the 2F-85's
  20-235 N grip are far above the wand set's weight (aluminium wand and tools, under 1 kg, plus part of the hose's
  weight, assumed under 1.5 kg).
- Passes at about 30 mm/s (SOP 3.3: "slow, deliberate"); the view port ring (240 mm) in 9 s, each 250 mm floor lane
  in 8 s, the bowl in 7 s.
- The run-on (20 s) and the settle (60 s) are shown as time-lapses with a timer gauge.
- The whole clip is about 2 minutes of screen time; at real speed the session would take about 5 minutes plus the
  person's liner work.

## How many vacuums: three

1. **Atomizer, Al family** (AlSi10Mg, Si, 4047, 6063): the 118EXP the lab has.
2. **Atomizer, Cu family** (NAB, 630 bronze): a second 118EXP with its own hose, wand, tools, filters and pail, all
   labelled. DAL's SOP keeps Cu and Al residues apart (Al with copper oxide is a thermite pair), and the vacuum SOP
   (section 6) says a switch between the families needs the main filter and both HEPA filters replaced, a full IPA clean
   of the bin, hose, wand and tools, a fresh liner and a fresh pail. At the accessories doc's lowest quotes the filters
   alone are about $1,200 a switch ($353 + $243 + $603), plus about an hour of cleaning (178 SOP T5 67:38). The lab ran
   copper on Oct 27, Oct 28 and Nov 5 between Al runs, so a second unit pays for itself in a few switches, and no
   thermite residue ever shares a bin.
3. **The printer line, Al family**: the Aconity MIDI's depowdering lance (notes/alloy_workflow.md, round 5: the arm
   vacuums the build cylinder with a lance on a post) needs an ATEX suction source at the printer, and the sieve station's
   bench (notes/alloy_print.md: a downdraft enclosure with its own extraction) needs a vacuum for spills. One 118EXP on
   that line serves both; wheeling vacuum 1 across the floor with its hose would mean a hose crossing the MiRs' paths.

**Cost** (the BoM): the vacuums themselves have no published price (quote needed). For vacuums 2 and 3 the priced items
are two hoses ($1,292), two wands ($350), two crevice tools ($106), three main filters ($1,059), three upstream HEPAs
($729), two downstream HEPA kits ($1,206), two cases of liners ($410), two pails ($48) and bonding hardware ($15):
**about $5,200**, plus two dust brushes (about $20-40 each, estimated), two Class D extinguishers (Amerex B570, quote) and
our two stations.

## What was checked

- `ARM_AUDIT=1`: see the result below.
- The hose: its own FCL check every audited frame against everything but the wand, its tools, the vacuum's inlet and the
  floor's markings (`out/collisions/atom_vacuum_hose.json`).
- The tool's reach through the door: with the crevice tool the grasp point is 648 mm behind the tip, so the gripper stays
  outside the door for the near side of the bowl and the floor; the far side of the bowl (x > 300) would put the gripper
  in the door, so it is left to a person (or to a second wand section, not modelled).
- The dust brush cannot meet the 45 deg floor square from the door (the floor faces up and away from the door, so the
  brush would meet it at about 17 deg and its head would scrape): the floor is done with the crevice tool, which drags
  at that angle as it is meant to, and the brush is used on the plate and the door's sealing face, which face the arm.

## Not done, or assumed

- The wand's length (20 in), the tools' spigot and collar, the hose's OD and the trolley are estimates; measure the lab's.
- The door's seal is not in the rePowder model, so the brush pass follows the band where the door meets the chamber's
  face (6-12 mm in from the door's edge), along the free edge and the top only (the stack's port is in the way lower down).
- The chamber's own valve is taken as closed with the container off (the airlock), so nothing falls out of the outlet.
- The meter readings are illustrative; the load cell and the switched outlet are assumptions to clear with EHS.
- The person's steps (liner, wiping, the far side of the bowl, the cone from below) are captions, not animated.
- Open questions for the lab: the wand's length; whether the collar should be conductive (bonded) or insulating; whether
  EHS accepts a robot-switched outlet for the vacuum; Nilfisk's written clearance on the crevice tool (SOP gate 0.4);
  whether one extinguisher can serve both atomizer vacuums (they are side by side).
