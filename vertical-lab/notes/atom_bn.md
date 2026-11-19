# Cleaning the crucible and recoating it with boron nitride, by robot (`atom_bn`, PR #353)

Clip: `atom_bn.py` (stations, tools and the crucible's coat in `atom_bn_station.py`); bill of materials:
`out/atom/bn_bom.json`. The clip starts where `atom_crucible.py` ends (the used crucible out of the furnace, holder
and nozzle off, the skull inside, in a cradle on MiR 1) and ends with the crucible coated, dried, checked and back on
MiR 1, ready to go back into the furnace.

Sources, short names used below:

- **Bronze plan**: DAL PR 220, `220_bronze-plan.md`, "Coating and recoating the crucible" (Oct 30 - Nov 2 2026, the
  lab's own experience) and "The day before" steps 2-3.
- **SOP 253**: DAL PR 253, the atomizer SOP checklist ("Crucible boron-nitride coated: a thin coat, sprayed the night
  before, dry"; for copper, "cure it empty under argon before the run (a fresh coat smoked at 500 C)").
- **SOP 178**: DAL PR 178, the detailed SOP, "Cleaning and maintenance" ("Crucible: slag always remains at the bottom;
  peel it off; re-coat with BN when the coating is gone", T5 76:16, SP 11:37, T1 42:23; "Unpoured silicon cracks the
  crucible on cooling", T5 12:39) and "After a run" ("Un-atomized metal is feedstock, not waste").
- **Vacuum SOP**: byu-vcl PR 80, `vacuum-operating-sop.md` (dry-wipe first; never IPA on visible powder; no compressed
  air; every metal joint <= 0.1 ohm; the crevice tool 01768900 out of service until it passes).
- **Can**: Momentive Boron Nitride Spray II, 13 oz, McMaster 10515K35, its directions as quoted in the bronze plan
  (6-8 in, successive light coats, 4 s upside down to clear the valve). Dried BN rated to 1,800 C inert, 850 C in air.

## The layout (ours)

All in the rePowder's model frame (x right, y back, z up, mm), to the right of the atomizer's taped area:

- **Cleaning bench** 680 x 600 mm, top at 900 mm, x 1700-2380, its front at y = -229.
- **Fume hood**: the Labconco Protector XStream 4 ft as `instruments_r7.fumehood()` draws it (1219 x 958 mm, work
  surface at 932 mm, sash stop at 18 in = 457 mm), its centre at (3000, 250), so its front is in line with the bench's.
  Its etch beakers and coupon are left out. The sash is at its 18 in working stop the whole time: the opening is
  960-1417 mm high over the airfoil, 1019 mm wide; 840 mm from the sash to the baffle.
- **MiR 1 parks at two spots**: the bench spot (2150, -850) and the hood spot (2850, -1130), the arm's base 771 mm in
  front of the hood. Both were checked offline for reach (UR10e IK) on every pose before the scene was built: from
  closer spots, the level grasps fall inside the UR10e's inner singular cylinder.

### Can a UR10e on a MiR reach into the hood under a working sash? Yes, with three choices

1. **Level approach.** The gripper comes in level (props.tcp_frame, y down), so the arm's elbow and forearm stay
   outside the hood and only the 2F-85 and what it holds pass under the sash. The arm's base stays 771 mm back; the
   elbow is then outside the sash, and the wrist passes the sash plane at 1100-1300 mm, under its 1417 mm edge.
2. **Work near the front.** The box's front is 213 mm (8.4 in) behind the sash, more than the 6 in the bronze plan asks;
   everything the arm touches is within 380 mm of the sash (the plug's holster, the box, the rack, the spray tool's
   cradle).
3. **A lift under the turntable** (ours, 152 mm). The crucible is handed over with its top 82 mm above the box's rim,
   so the gripper never goes into the box; the box can then be as narrow as still air needs (130 x 150 mm inside).

The gripper's top (with the D405 riding on it) reaches about 1340 mm. A sash below about 15.7 in (400 mm) over the
airfoil would not clear it: if the lab's hood is marked lower, this layout doesn't fit, and a level wrist without the
camera on top, or a bench-top enclosure, would be needed. A ductless (carbon) hood is not a substitute: carbon does not
hold propane or butane, and its blower would sit in the vapour.

## The procedure, step by step

| # | Step (clip label) | Who / what | Source |
|---|---|---|---|
| 1 | MiR 1 brings the used crucible from the rePowder to the bench (1/10). | MiR 1 | atom_crucible.py hands it over |
| 2 | The arm lifts it out of MiR 1's cradle (top grasp) and stands it in the positioner's chuck; the soft jaws close on the outside (2/10). | arm, positioner | ours; never grip the bore |
| 3 | The positioner turns it mouth down 20 mm over the dark tray and jolts it (a 5 deg flick and a hard stop: the robot's tap); the skull falls out (free fall, 0.18 s) (3/10). | positioner | bronze plan step 1 (take out the skull); SOP 178 (slag at the bottom; un-atomized metal is feedstock) |
| 4 | A soft nylon bore brush loosens what is left while the chuck turns (4/10). | arm (brush tool) | bronze plan step 1 (brush out anything loose) |
| 5 | An acetal scraper takes off only what is cracked or lifted or has metal stuck to it, down to the thin grey layer; never the seat round the hole (5/10). | arm (scraper), positioner turns | bronze plan step 2 |
| 6 | Mouth down and tapped again (the flakes fall on the dark tray); then the crevice tool of the Nilfisk 118EXP vacuums the bore and floor, slow and close; no compressed air; IPA only if something oily touched it (not this time) (6/10). | positioner, arm (vacuum tool) | bronze plan step 3; vacuum SOP |
| 7 | To the hood. The arm takes the crucible from the chuck with a level grasp; MiR 1 drives 0.8 m to the hood spot; the arm sets the crucible on the raised turntable; the lift lowers it (7/10). | arm, MiR 1, lift | bronze plan "Why the box" |
| 8 | The seat plug: the arm holds the PTFE plug still over the crucible and the lift raises the crucible onto it; the arm lets go; the lift lowers the crucible to the spraying height, its rim 70 mm under the box's rim (7/10). | arm, lift | bronze plan ("keep the spray out of the nozzle seat and bore") |
| 9 | The arm takes the spray tool from its cradle, draws it out of the hood and shakes it: about 2.5 Hz, +-20 mm along the can's axis, 90 s (3 s shown) (8/10). | arm (spray tool) | bronze plan ("at least a minute after the ball starts to rattle") |
| 10 | Pass 1: short bursts (0.35 s) from 175 mm at the upper wall and 200 mm at the lower wall, aimed at the walls, the turntable turning the next scraped sector to the can between bursts; only scraped sectors get a burst (8/10). | arm, turntable, air pusher | bronze plan ("short, quick bursts, turning the crucible between them"; "aim at the walls"; "on a touch-up, one or two light passes over the repaired spots") |
| 11 | About 5 min wait (time-lapse); pass 2 the same (8/10). | - | bronze plan ("about 5 min between passes, longer if still wet") |
| 12 | The can upside down for 4 s to clear the valve, aimed at the hood's back (8/10); the tool goes back in its cradle. | arm | can directions (bronze plan) |
| 13 | The lift raises the crucible; the arm takes the plug off it (the lift lowers the crucible away from the plug) and puts it in its holster; the arm takes the crucible, turns it over in the air (a 180 deg wrist roll) and stands it upside down on the rack's three pins (9/10). | arm, lift | bronze plan ("dry overnight in the running hood, in the box or upside down") |
| 14 | Overnight in the running hood (time-lapse with a clock, 18:30 to 07:30); the coat goes from wet to matte white (9/10). | hood | bronze plan; SOP 253 ("sprayed the night before, dry"); "never pour onto a wet coat" |
| 15 | Morning: the arm takes it off the rack, turns it upright outside the hood, MiR 1 drives back to the bench, the arm stands it in the chuck (10/10). | arm, MiR 1 | ours |
| 16 | The check: side light on; the arm holds still where it backed off, the positioner tilts the mouth 50 deg toward it, and the D405 on the level gripper looks 18 deg off the bore's axis, about 270 mm from the floor, while the chuck turns (10/10). | arm (camera), light, positioner | bronze plan ("look at the floor and the floor-wall corner under a strong side light for cracks, lifted edges or bare graphite") |
| 17 | Mouth down over the dark tray and tapped once more: nothing falls (10/10). Ready; back to MiR 1 for atom_crucible. | positioner | bronze plan ("turn the crucible over a dark sheet and tap it... nothing loose near the hole") |
| 18 | For copper runs: cure it empty under argon in the furnace before the run (a fresh coat smokes at 500 C). Caption only. | furnace | SOP 253, copper section and troubleshooting |

**What the vision check looks for** (ours, on the D405's colour image, needs calibrating on photos of real coats):
dark pixels on the floor and the floor-wall corner (black graphite showing through: spot spray and dry again, bronze
plan); thin dark lines (cracks: tolerated if stuck down and white or grey underneath, fixed at the next touch-up);
a bright edge with a shadow beside it under the low side light (a lifted flake: brushed and tapped out). The D405's
depth image can't resolve a 0.1 mm lifted edge at 250 mm; the shadow can. The tap over the dark tray is the check
that settles it: what falls out would have come off in the furnace and could reach the 0.5 mm nozzle.

**A touch-up, not a full coat.** The clip does the lab's routine between runs (bronze plan, "Between runs: touch up,
don't strip"): only the floor and five wall patches were scraped back to the grey bonded layer, and only those sectors
get bursts. On bare graphite (a new crucible) the same moves fire at every sector, two or three light passes; on a
touch-up one or two. Stop when the sprayed spots are matte white once dry; a spot still shiny or grey gets one more
light pass.

## The spray geometry, and what it can't reach

The can's actuator sprays square to the can's axis. To spray 40 deg off vertical into the crucible the can is tilted
50 deg from upright, its top toward the back of the hood (tilted "only as far as needed": past horizontal it sputters).
The can's body slopes down toward the sash, so its whole length has to clear the box's front wall: the deepest the
beam's centre can land on the far wall is about 61 mm under the rim (at 200 mm), 20 mm above the floor-wall corner. The
burst's lower edge reaches lower, and the floor also catches the mist that settles, which the bronze plan says builds up
fastest there; the clip gives the floor sectors 45% of each lower burst. If the floor-wall corner stays grey at the
morning check, the answer is a third light pass, not a steeper can. Placing the crucible 10 mm behind the box's centre
(47 mm in front of it, 27 mm behind) is what lets the beam clear the front wall at all.

## Tools and fixtures

Ours vs bought, with part numbers and sources, are in `out/atom/bn_bom.json`. In short: bought: the BN spray
(10515K35), the hood, the Nilfisk 118EXP with its conductive hose, cuff and the 11 in crevice tool 01768900, the
D405 on the arm. Ours: the positioner (3-jaw chuck with acetal soft jaws on a trunnion; flip and spin; an air
the tap as a 5 deg jolt of its flip axis), the dark tray, the holsters, the brush on our handle, the acetal scraper, the vacuum's grip clamp, the box,
the air-driven turntable and lift, the PTFE seat plug, the spray tool (cradle, clamp bands, a 10 mm air cylinder on the
actuator), the drying rack, the side light, MiR 1's crucible cradle. Every tool has the same 20 mm handle for the
2F-85.

**Nothing in the hood may spark.** The propellant (propane and butane) and solvents (ethanol, acetone) are heavier
than air and pool at the bottom of the box (bronze plan). So the turntable, the lift and the can's pusher are air-driven
with their valves outside the hood (ours), not motors under the box. The can is stored in the flammables cabinet; a
person loads it into the spray tool for the session (assumed).

**The vacuum's nozzle.** The crevice tool 01768900 is out of service until it reads <= 0.1 ohm tool to wand (vacuum
SOP 0.1: it read open on 2026-08-19). Until then, the brush and the tap over the dark tray do the job, or the dust
brush 01719401 (0.03 ohm, passes) at the mouth. Our grip clamp must keep the chain bonded (aluminium, no paint at the
joints). The Nilfisk is drawn from `atom_nilfisk.py`'s `vacuum_meshes()`; the crevice tool on its cuff and our clamp is
drawn here (a flat nozzle tapering to a 30 x 10 mm slot), not with that module's wand.

## Forces, masses and their basis

- The crucible: about 0.52 kg (288 cm3 of graphite at 1.8 g/cm3, from the model's dimensions; density assumed). The
  2F-85 at its lowest force, 20 N (Robotiq's range 20-235 N), with a friction coefficient of 0.3 assumed, holds
  2 x 20 x 0.3 = 12 N against 5.1 N. Graphite is brittle (SOP 178: "snug, never forced"), so no more.
- The 2F-85 opens to 85 mm; the crucible is 75.3 mm across: 4.9 mm each side on the way down. The chuck's jaws open
  5 mm.
- The scraper: a light scrape, 5-10 N normal at the edge, under the UR10e's force mode (assumed, to set on a scrap
  crucible). The drawn blade stops 0.2-1.4 mm off the wall (16 mm wide, straight edge).
- The can's actuator: about 20-40 N to press (assumed); a 10 mm bore cylinder gives 47 N at 6 bar.
- The shake: +-20 mm at 2.5 Hz is a peak acceleration of 4.9 m/s2 with about 0.6 kg in the tool (assumed): within a
  UR10e's tool speed (1 m/s) and comfortable for its payload (12.5 kg).
- The skull's fall: 0.18 s from inside the inverted crucible to the tray (h = g t^2 / 2 on the drawn heights).

## Timing (the real job, estimated; the clip compresses it)

About 25 min of work plus the overnight dry: arrive and chuck 1 min; skull out 30 s; brush 1 min; scrape 3-5 min; tip
out and vacuum 2 min; to the hood and the plug 2 min; shake 90 s; two passes about 1 min each with 5 min between;
valve clear 4 s; plug out and onto the rack 1.5 min; overnight about 12 h; morning check and tap 3 min.

## What was checked

- Reach: every pose of the clip solved with the UR10e's IK from both MiR spots before building the scene.
- Collisions: `ARM_AUDIT=1` (FCL on every frame; the arm, gripper and held parts against everything, held parts
  allowed 1.5 mm into their own fixtures; the movers check on everything else that moves). Seven audit passes took it
  from 518 frames in collision to the result in `out/collisions/atom_bn.json`: **112 of 2234 checked frames in collision, one run, all in the last sub-step (10/10)**: after the arm sets the
  crucible back in the chuck and backs 170 mm away along -y, its forearm dips into MiR 1's cabinet and stays there
  through the check and the tap (the last 8 s of the clip). Sub-steps 1/10 to 9/10: 0 frames. Movers: 0 contacts. What the passes found
  and fixed: the vacuum tool's cuff in the gripper (the tool redesigned: gripped 130 mm from its tip, its cuff 75 mm
  to the side, turned away from the wrist); a holster against the hood's post; the scraper's straight blade wider
  than the bore allows (now 16 mm); the crucible carried into the box below its rim (it now comes in 15 mm over the
  rim and goes down); the IK branch with the wrist over the tool, whose forearm hit the sash's edge (the hood moves
  now pick the elbow-up branch whose wrist passes inside the opening's band, 1040-1340 mm, and enter on straight lines
  from poses outside the sash); the plug's holster too close to the sash; the crucible turned over inside the hood
  (now a pure roll of the last joint, outside); the lift's column through the work surface (now four nested 61 mm
  stages that fold into the plinth); the skull landing inside the positioner's plate; a knocker that sat in the
  trunnion's sweep (dropped: the positioner jolts instead); MiR drives that dragged the held crucible into the bench.
- Under the sash: the elbow stays outside the hood in every hood pose; the forearm passes the sash plane under its
  1417 mm edge.
- Clearances drawn: the brush (50 mm) in the 57.1 mm bore (3.5 mm each side; a real brush is larger and its bristles
  bend against the wall); the scraper's edge 0.2-1.4 mm off the wall (its contact is the change of colour, scraped
  sector by sector); the vacuum tool 8 mm above the floor.

## Not done

- **The 10/10 fault above is not fixed in the rendered clip.** The fix was found but there was no render slot left
  before the deadline: back off only 60 mm (enough to free the fingers), then a planned move (`Clip.low`, elbow up)
  to a look pose pitched 30 deg down, 110 mm from the mouth, with the positioner tilting the mouth 60 deg. Audit pass 6
  ran exactly that look pose and found it, and everything after it, clean; the 170 mm back-off before it was the only
  fault. The next render should make that change.
- The clip is 153.9 s (2308 frames at 15 fps), 4 s over the 150 s asked; the GIF is resampled to 5 fps (330 frames,
  3.4 MB) to stay under 4.9 MB.
- The spray's mist is a cone drawn for each burst; the overspray onto the plug and the rim and the mist settling on
  the floor are in the coat colours, not drawn as particles.
- The coat is shown by zone (12 sectors of the upper wall, the lower wall and the floor), not as a texture.

## Assumed (and why)

- The can's size, 68 x 230 mm with its actuator: a standard 211 can (most 12-16 oz aerosols); the actuator's
  spray square to the axis (a standard actuator).
- The positions of everything on the floor, the bench, the box's size inside the bronze plan's rules, the lift's
  stroke, the plug's shape: ours.
- Which spots are damaged (the floor and five wall patches): an example, after the bronze plan's note that the Oct 30
  coat and the Nov 2 touch-up cracked on the floor.
- The skull comes out with a tap. If it sticks, the scraper peels it (SOP 178: "peel it off"); unpoured silicon can
  crack the crucible (SOP 178), which the check would find.

## Open questions for the lab

1. Which hood is it, and where is its sash's working-height mark? This layout needs at least 400 mm (15.7 in) open.
2. Is a robot reaching in under the sash acceptable under the lab's hood policy, if only the gripper and the tool go in?
3. The wall thermocouple hole opens at the rim: should it be masked too (a pin plug), or does a little overspray there
   not matter?
4. Weighing the dry crucible after each recoat shows build-up (bronze plan: 1 g over about 200 cm2 is about 50 um): a
   balance at the bench would make "strip it all" a measured decision. Worth it?
5. The crevice tool's continuity (vacuum SOP 0.1): fixed yet? Until it is, the vacuum step uses the dust brush.
6. For copper, is the cure under argon done right after the morning check, or the next day before the run?
