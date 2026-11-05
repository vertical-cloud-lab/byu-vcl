## The alloy route, chapter 2: atomize (`alloy_atomize.py`)

The MiR250 brings the four charged 5N Al cups from the VLM to the rePowder. The UR10e opens the lid, swings the
sealing rod's lever up, loads the cups round the rod, lowers the lever and shuts the lid. The machine, cut open at the furnace axis, washes, melts and atomizes the
charge. The arm then takes the powder container off onto the MiR. Clips and photos of the lab's own runs are cut in
where the animation reaches the same moment: the charge, the melt, the pour onto the plate and the powder as it comes out,
not yet sieved (the sieved jars are chapter 3's since round 8).

| | |
|---|---|
| Clip | 197.4 s at 10 fps (round 6), 35.1 s of it the lab's own footage, the melt at 2×; [GIF](../out/alloy_atomize.gif) (560 × 315, 4 fps, 5.8 MB: over the 4.9 MB budget), [MP4](../out/mp4/alloy_atomize.mp4), [still](../out/alloy_atomize_still.png), sub-steps in [`alloy_atomize.json`](../out/alloy_atomize.json), powder sums in [`alloy_atomize_powder.json`](../out/alloy_atomize_powder.json) |
| Starts | MiR250 at the VLM's opening (`animate.AMR_XY`), the four Al cups in `charge.carrier()`'s four pockets at `animate.BUFFER_LOCAL` on the cabinet: where chapter 1 ends |
| Ends | MiR250 at world (−3487, −2230), yaw 0: square to the container's axis, 41 mm off the view port's flange, the hand-off chapter 3 (sieve, print) starts from. The container stands in a cradle at MiR-local (280, 10), a low ring on the cabinet top, seat z = 783 mm (round 6; it was 933 on a post); the loading tong hangs in its sleeve on the cabinet's −x end; the arm is parked. While the arm works the MiR stands further out: 220 mm (y = −2450) for the lid and the cups, because at y = −2230 the lid knob falls inside the UR10e's unreachable cylinder over its base; 420 mm (y = −2650) for the container, because closer the forearm comes down through the MiR's own cabinet to the handle, 275 mm off the floor. It drives onto the hand-off spot at the end |
| Scene | `line.py`'s layout as `alloy_workflow.py` builds it, the rePowder loaded part by part from `repowder/model.py` (the merged copy `animate.Lab` adds is hidden) |
| Ported | `Pool`, `Powder`, `Particles`, `stream`, `film`, `shake`, the heat colours, the argon volumes, `load_machine`/`set_cut`: #124's rePowder training animations (`atomizer-training/viz3d/steps.py` and `scene.py`, branch `claude/issue-124-20261003-0335`) |
| Footage | [`out/footage/`](../out/footage/): the excerpts and photos used, small, with a [manifest](../out/footage/manifest.json) of credits |

```bash
xvfb-run -a python3 alloy_atomize.py        # render (round 6: 1,623 frames, 40 min on a very busy 4-core runner), then splice (15 min)
python3 alloy_atomize.py splice             # only cut the footage into the last render (3-13 min, mostly the GIF)
python3 alloy_atomize.py keep               # copy the excerpts PLAN uses from /tmp/footage (FOOTAGE=...) to out/footage/
python3 alloy_atomize.py powder             # print the powder sums
```

### Round 8 (PR #318, 2026-11-05): the MS&T stream, the unsieved powder, two Shuttles

Sterling's review of 2026-11-05 00:37 UTC, verbatim:

> That Al6063 melt stream video that you found is a dud. Bad. You could find the stream from a recent youtube video
> from me probably, and it is probably on our youtube somewhere.

> The already sieved bronze powders are shown right after pulling it out, you should show the unsieved jar first,
> then show the sieved results after you actually do the sieving. See DAL for the issues and PRs related to sieving

| What | Round 7 | Round 8 |
| --- | --- | --- |
| The pour's footage | the lab's Oct 27 bronze jet, then an Oct 8 Al 6063 stream that dripped | a melt stream atomizing on the plate from Sterling's MS&T 2026 talk ([YmvaeqOQAU4](https://youtu.be/YmvaeqOQAU4?t=298), 4:58-5:05, after the slide "Ultrasonic atomization enables chemical whitespace AM alloy discovery"), cropped to the video and shown beside the model, badged REAL FOOTAGE · Sterling Baird's MS&T 2026 talk; then the Oct 27 bronze jet. The Oct 8 clip is out. The talk doesn't say which alloy or run it is, and the caption says so |
| After the pour | the unsieved jar, the c3k0n5 bag and jar, then the three sieved jars | the unsieved powder only: the k7m2q9 jar on the day of the run ("not yet sieved; it is sieved in chapter 3") and the c3k0n5 bag and jar "as collected that day". The sieved jars are chapter 3's, after the arm's sieving ([`alloy_print.md`](alloy_print.md)) |
| The floor | `line.py`'s one-Shuttle line, the Aconity at x = 3250 | `setup_lab.py`'s floor ([`alloy_atomize_floor.py`](../alloy_atomize_floor.py)): the second Shuttle at x = 3630, the Aconity at 6950, the glovebox at −7300 turned to the aisle |
| The container in its cradle | turned half round, the handle to the arm | the handle to the front, as it came out of the rePowder: chapter 3 takes it from there, level from the front, so the two chapters now meet in the same state (`CRADLE_TURN`) |
| Framing | the latch steps seen from the close-up; the camera through the machine for a few frames (fixed in code in round 7, not rendered) | rendered |
| The MiR250's drives | the old smoothstep ease: about twice the MiR250's published acceleration | from rest to rest at its published 0.3 m/s², up to 1.5 m/s, along the same S-curves (`props.ramp_frac`, `props.ramp_secs`, `props.s_curve`: PR #321's ramps, brought over in round 8). The drives take longer: the arm audit's count at 6 fps went from 800 frames to 866 |
| The latch | base, lever, loop and keeper all the furnace's light grey, so the latch all but vanished in its close-ups | the base and the keeper on the lid dark (0.36-0.41 grey), the lever and the loop bright stainless, so the over-centre motion reads |
| The pull on the latch | a "ballast plate, 95 kg" label whose leader ran in from off screen (the plate is under the MiR's cabinet, out of the latch's close-up) | no label; the caption names the plate |

**Rendered (continuation 2, 2026-11-05 16:22 UTC):** 210.5 s at 6 fps, 1263 frames: 178.5 s of 3-D and 32.0 s of the lab's footage in 8 pieces (the charge photo, three melt excerpts at 2x, the MS&T stream, the bronze jet, the k7m2q9 jar, the c3k0n5 bag and jar). Arm audit at 6 fps: **0 of 866 frames in collision** (`out/collisions/alloy_atomize.json`). The GIF the splice wrote was 5.9 MB, over the 4.9 MB budget even at its 4 fps fallback, so `out/alloy_atomize.gif` was remade from the MP4 at 3 fps and 512 x 288 (4.8 MB).

### Round 6 (PR #318, 2026-11-04): the lid's latch, the base, a loading tong, the crucible

Sterling's notes on the round-5 render, and what changed.

#### The lid shuts with one draw latch

> "That lid for the atomizer; check the videos, but I'm pretty sure it's a clamp of sorts that would require a fair
> bit of pressure to undo."

**What the footage shows.** Three frames of the lab's training video T4
([`1F9_4ccwhss`](https://youtu.be/1F9_4ccwhss?t=308)), kept small in [`refs/repowder_lid/`](../refs/repowder_lid/):
- **5:08, lid up** ([frame](../refs/repowder_lid/t4_0508_lid_open_latch.jpg)). A stainless over-centre draw latch
  (a toggle latch) sits on a flat on the furnace body's front right. Its lever stands up, its loop on top.
- **5:17, lid down** ([frame](../refs/repowder_lid/t4_0517_latch_and_keeper.jpg)). The keeper is on the lid above it:
  a plate with a lip and two screws. A horizontal bolt comes out of the machine's blue cabinet right beside the latch.
- **5:23** ([frame](../refs/repowder_lid/t4_0523_closing.jpg)). One hand presses the lid down; the other works the
  latch.

**What the lab's notes say.**
- The SOP (`atomizer-training/sop.md`, #124 branch): "Close the furnace lid and secure the latch just tight enough to
  seal; if it hisses, loosen, adjust the latch and retighten" (T4 5:17). So the loop is threaded to set the draw.
- Bartosz Kalicki (AMAZEMET) at the install call
  ([`rePowder-BYU-Installation-Details.txt`](../../rePowder-BYU-Installation-Details.txt), 20:21 and 21:51-22:11):
  "on the right you have the lock", and "once you close the furnace and you change the pressure in the furnace, it
  automatically locks; there is like a bolt coming and locking the furnace".
- T8 9:09's "how tight?" is the chamber door's star-knob swing bolts (frame checked), not the lid.

So the lid has **one latch, opened by pulling its lever over centre, and a pneumatic bolt that blocks the lever
whenever the furnace is off atmosphere.** No screws to undo.

**In the chapter.** The latch, its keeper and the bolt are drawn in `alloy_atomize.py` (`latch_meshes`), so the
rePowder model's mesh cache is untouched. The arm takes the lever by a pull tab from above and swings it out 105°;
the loop comes off the keeper. It then opens the lid by its knob, as before. At the end it shuts the lid and swings
the lever back up over centre. When the first pump-down starts, the bolt comes out in front of the lever; when the
chamber is vented at the end, it goes back.
- **The pull tab is an addition.** The real lever ends in a plain plate with a hole. The tab ends in a T, so the
  2F-85's pads sit inside its head and the pull is taken by shape. A friction grip would hold about 2 × 235 N × 0.3 =
  141 N (Robotiq's own friction figure), under the 200 N design load below.
- **The hinge is probably wrong.** At 5:08 the open lid stands up behind the crucible with its inside to the camera,
  so it likely hinges at the back. The model hinges it on the left (#124's guess). Not changed: the arm's whole lid
  move depends on it.

**How hard to undo: not measured; an estimate.** An over-centre latch holds its preload with the loop's pull a few
mm past the lever's pivot. To open it, the lever has to come back over centre against that. Kipp publishes the hand
force for its K0080 cover latches: **100, 150 and 200 N for 2, 4 and 7 kN held**
([K0080 sheet](https://www.marek.eu/data/katalogove-listy/kipp/K0080.pdf)). DESTACO's stainless latches hold 1.6-8.9 kN
and give no lever force. The lid's seal sets the preload: a 6 mm O-ring cord about 790 mm round, at 10 % squeeze,
takes 1.3-3.6 N/mm ([Parker O-Ring Handbook](https://nfc.arizona.edu/sites/default/files/2022-02/parker_o-ring_handbook.pdf),
Fig. 2-8, 0.275 in section), so 1-2.8 kN, about half of it on the latch and half on the hinge. So the sums below take
**100 N expected and 200 N for a stiff one**. Under pressure it can't be opened at all: the bolt blocks it, and at
+150 to +350 mbar the lid carries 750-1,750 N (π · 126² mm² × the over-pressure).

#### Will the MiR tip? No, with margin; a ballast plate adds more

> "I'm also a bit worried about whether the base is heavy enough to be able to compensate for a lot of load from
> being exerted via the arm. This is where a rail would more or less address that, but a heavy enough base that's
> low enough to the ground could be fine, too."

`stability()` sums it at the pose the chapter uses: the arm on the pull tab, the MiR where it stands for the lid.
Results in [`out/alloy_atomize_stability.json`](../out/alloy_atomize_stability.json).

| | Mass, CoG height | Tips at | Slides at | 100 N latch (expected) | 200 N latch (stiff) |
|---|---|---|---|---|---|
| MiR250, cabinet, control box, UR10e, 2F-85 | 172 kg, 442 mm | 466 N | 505 N | 4.7× tipping, 5.1× sliding | 2.3×, 2.5× |
| the same with the 95 kg ballast plate (as drawn) | 267 kg, 397 mm | 730 N | 785 N | 7.3×, 7.9× | 3.7×, 3.9× |

Closing the latch pushes the other way: it would tip the MiR at 483 N (746 N with the plate).

- **The force** acts at the tab, 1,331 mm up and 664 mm out from the MiR's centre, toward the furnace (the lever pulls
  back on the arm). Closing the latch pushes the other way.
- **The masses:** MiR250 97 kg ([2023 spec sheet](https://www.hartfiel.com/wp-content/uploads/2024/04/MiR250-Specs.pdf);
  MiR's page now says 94), UR10e 33.3 kg and its control box 12 kg
  ([datasheet](https://www.universal-robots.com/manuals/latest/en/datasheets/ur10e/)). The cabinet's frame (25 kg) and
  the gripper with its camera (1.2 kg) are estimates. The arm's links are placed by its forward kinematics at the pose,
  with UR's published link masses.
- **The support:** MiR250 has two drive wheels at mid-length and four corner casters (spec sheet). Their positions
  aren't published; the sums take the casters at ±325 × ±225 mm (estimate).
- **Sliding:** the drive wheels carry half the weight (estimate); μ = 0.6, the low end of the 0.6-0.8 floor friction
  MiR's user guide asks for (§16). The casters roll.
- **The arm's own limits.** Its joints give 330 N·m (base, shoulder), 150 N·m (elbow) and 54 N·m (wrists)
  ([UR](https://www.universal-robots.com/articles/ur/robot-care-maintenance/max-joint-torques-cb3-and-e-series/)); its
  rated payload is 12.5 kg. At the tab the wrists are the limit, about 0.2 m from the pull: 200 N is 40 N·m.

**So the base is heavy enough for this latch: it holds more than twice a stiff one, unballasted.** Sterling's rail
or a floor-anchored dock would be the answer for jobs that push harder. The chapter still draws a **95 kg steel
plate, 32 mm thick, under the cabinet** (the dark band at its foot): cheap margin, within the MiR250's 250 kg
payload (cabinet, control box, arm, gripper and plate come to about 170 kg). A dock at this spot would stand where
chapter 3's hand-off pose puts the MiR.

#### A loading tong: no drop, nothing near the rod

> "It almost looks like there's some interference between the gripper and the sealing rod when adding the charges
> into the melting chamber. I also don't like that it's just getting dropped inside from a high height. This also
> seems like something where a custom end effector might help."

Round 5 let go of each cup with its foot 13-15 mm into the bore (cup 2: 19 mm over the rim), and the cup slid the
rest of the way. Now the 2F-85 picks up a **loading tong** from a sleeve on the MiR's cabinet end (`tong_meshes`):
- two spring-steel jaws, 1.2 mm thick and 8 mm wide, take the cup's top 12 mm on the two sides square to the
  crucible's radius;
- a 6 × 8 mm stem runs up to a handle 185 mm over the jaws, where the 2F-85 clamps it;
- closing the 2F-85 the last 3 mm shuts the jaws; opening it 3 mm opens them (custom fingertip blocks pinned into the
  handle's two halves). Opening it fully leaves the tong in its sleeve. A design, not built;
- below the gripper nothing is wider than the cup or the stem.

The tong carries each cup all the way (`tong_path`): over the crucible; down #222's descent (beside the adapter, tipped
4.1° with the foot over the bore's lip, down the line until the top passes under the adapter); upright as it goes on
down, its outer side 0.3 mm inside the bore at the rim; in to its place; onto the floor cone. Only then do the jaws
open, and the tong comes straight up.

**Clearances** ([`alloy_atomize_clearance.json`](../out/alloy_atomize_clearance.json)), by FCL on the meshes, the
least along each cup's whole path:

| Least clearance, mm | Sealing rod | Rod adapter | Crucible bore | Filling cone | Thermocouple | Cups already in |
|---|---|---|---|---|---|---|
| Jaws (all four cups) | 10.2 | 7.6 | 3.3 | 3.3 | 4.4 (cup 2) | 1.3 |
| Stem and bridge | 7.1 | **2.6** | 3.2 | 3.1 | 3.5 (cup 2) | 4.2 |
| The cup it carries | −0.3 to −0.4 | −0.5 to −0.9 | +0.2 | +0.1 to +0.2 | ≥ 3 | 1.1 |

- **The gripper's lowest point stays 136 mm over the rim** (the cup seated, its top 19.1 mm under the rim). Nothing
  of the 2F-85 comes near the rod, the adapter's stub, the raised lever or the filling cone.
- **The tightest spots** are the stem passing the adapter's rim as the cup goes upright (2.6 mm), and a jaw passing a
  cup already seated (1.3 mm; neighbours stand 2.2 mm apart).

- **The cup's own squeeze is unchanged.** A 3/4 in cup only passes the adapter tipped, at #222's −0.09 mm. In the
  model the cup overlaps the adapter by 0.5-0.9 mm and the rod by 0.3-0.4 mm at the tight spot. These are FCL's
  contact depths, which are rough, and the meshes' facets cost up to 0.2 mm of the bore. No tool changes this; a
  5/8 in cup goes straight in (+1.83 mm, #222).
- **The audit's bookkeeping.** Down the bore, the arm "holds" the cup (the tong riding on it) as far as the tight spot,
  then the tong (with the cup in it). A held part may touch where it came from and where it goes. So the cup's squeeze
  past the adapter, the rod and the rim is allowed, as the old release point allowed it. The tong's own parts are
  checked like everything else.

#### The crucible stack, as it would have to be automated

> "Things related to the crucible in terms of automation are going to be very difficult. Fragile graphite materials
> that are getting screwed onto other graphite materials. Custom end effector attachments, high-sensitivity force
> sensing (torque for example), are all things that would be very important for trying to do this automation."

Step 3 now stops on the cut-open stack for a few seconds: the crucible, its threaded shank, the graphite seal and the
thin graphite nut that goes on from below, through the chamber's door. The nut turns, and the caption gives the force
sensing it would take: the UR10e's own sensor is good to ±5.5 N and ±0.5 N·m; a Robotiq FT 300-S resolves 0.1 N and
0.005 N·m, an ATI Mini45 1/16 N and 1/752 N·m. The plan, the hard parts and the risks are in
[`crucible_automation.md`](crucible_automation.md).

#### The rest

- **The wrist camera** (the round's shared foundation) shows in the close-up of the tong being picked up.
- **The melt footage runs at 2×** (`MELT_SPEED`): the three 2brsz-90seg excerpts, 16.5 s of real time in 7.8 s,
  badged `2× SPEED`. Only the kept excerpts exist (`out/footage/`); longer windows at 3× would need a fresh fetch.
- **One camera move came after the render.** In the committed round-6 render the lid's knob and the lever are seen
  from the latch's close-up, and the camera passes through the machine for a few frames on its way to the tong. The
  knob step now moves the camera back out (`cam_to=CAM_LOAD`); the next render picks it up.
- **The container's cradle is a low ring on the cabinet top**, where it was a ring on a 150 mm post that the upper arm
  crossed.
- **Collisions: 0 of 1,339 frames** at 10 fps (`ARM_AUDIT=1`, [`out/collisions/alloy_atomize.json`](../out/collisions/alloy_atomize.json); round 5: 10 of 1,586 at 15 fps). On the way: the wrist camera in the hood on the latch grasp (the grasp turned 180° so the camera rides outboard), a fingertip on the bolt's cylinder (the gripper opens only to 0.72 round the tab), the tong's handle grazing the open lid's edge for one frame (a staging pose in front of the furnace), and the arm's upper arm through the cradle on its post (now a low ring).

**The render and the footage are kept apart.** The render writes the 3-D chapter to `out/clean/` (git-ignored):
`alloy_atomize_3d.mp4`, its GIF frames and a JSON with a marker wherever footage goes. With each marker it keeps the
view at that moment without its text. `splice` then fits each piece in `PLAN` to the frame and draws the chapter's
title, step label and caption on it, plus a red badge, `REAL FOOTAGE` or `REAL PHOTO`, with the alloy and the date.
It writes the final MP4, GIF and JSON with every sub-step moved on by the footage before it. Portrait clips and photos
stand beside the model's view of the same moment; landscape ones fill the frame. Changing the footage needs no
re-render.

### Four cups a run

Sterling (PR #318): *"We load multiple charges into the crucible (4), and potentially much more if we upgrade to the
400 cm³ crucible."* The Oct 27 bronze run (k7m2q9, DAL #219 and PR #230) went in as 4 rod pieces, 1,079.886 g.

**Where the four cups go: #222's four places round the rod**, the model's `SLUG_ANGLES` (70°, 145°, 220°, 295°):
- **75° apart, clear of the sealing-rod lever**, which lies over the crucible along +x. A set with one cup on the cut
  plane (as round 4 had, at 110° and 180°) doesn't fit four cups: the lever leaves a 225° arc, and 3 × 75° fills it.
- **Neighbours stand 2.2 mm apart** on the 17.4 mm circle halfway between the rod and the wall. A cup has 3.2 mm
  between the rod and the wall.
- **Getting past the adapter is the same for each cup:** straight down misses by 1.35 mm; tipped in, −0.09 mm (#222).
- **The 2F-85's fingers don't fit the bore, so the arm lets go higher** (below, "Checked for collisions"). Round 5
  let go at #222's tight spot with the fingertips 14.7 mm under the rim and their outer corners 4.2–4.9 mm into the
  crucible's wall: the fingers are 22 mm wide and close along the cup's tangent, so their corners stand 31 mm out
  from the axis, past the 57.1 mm bore. Round 4's clip did the same.
- **The cutaway.** The two back cups (145°, 70°) stay in it and are drawn cut through their own axes, a stepped
  section 10 and 16 mm behind the cut plane, so their powder, plug and vent show. The two front cups go with the half
  that is cut away.

**The melt:** 156.7 g at 2.37 g/cm³ (liquid Al, assumed for Al-10Si) is 66.1 cm³. In the model's crucible round the
rod that stands 21.6 mm above the floor cone's rim (it was 7.6 mm for round 4's 78 g). **The powder:** 143 g at
1.40 g/cm³ loose (assumed) is a heap 15 mm deep at the container's wall.

### How much powder a run makes

The yields are the Oct 27 bronze run's, the lab's best so far. Gage sieved both bronze runs together (DAL #219,
comments 6509252104 and 6509485831):
- under 63 µm, 188.0 g;
- 64–250 µm, 827.1 g;
- over 251 µm, 181.9 g;
- left in the crucible, 732.0 g.

He put 97 % of the usable powder down to the first run. For that run, that is **91 % usable (under 250 µm)** and
**17 % of the charge under 63 µm**, the MIDI's cut.

| Charge | Al in | Usable, < 250 µm | 20–63 µm | Runs for a 440 g build | Runs for a 30 mm build (1.0 kg) |
|---|---|---|---|---|---|
| 4 cups, this chapter (`out/alloy_recipe.json`) | 157 g | 143 g | 26 g | 17 | 39 |
| 225 cm³ crucible filled as on Oct 27 (142.5 cm³ of metal, 63 %) | 385 g | 351 g | 65 g | 7 | 16 |
| 400 cm³ crucible, the same fill (assumed) | 684 g | 624 g | 116 g | 4 | 9 |

- **The MIDI's powder per build, two figures:**
  - the lab's planning figure is **440 g a build** (powder-doser `design/brainstorming.md` §3, from Sterling's
    PR-thread comment);
  - chapter 3's 30 mm build in the full Ø170 mm cylinder takes about **1.0 kg** in the bed (π/4 · 170² · 30 mm at
    1.5 g/cm³).

  They differ in build height, not method. 440 g is 293 cm³, a 12.9 mm layer of the full cylinder, so 440 g is a
  short build or a smaller cylinder. Both are the bed alone; the supply's excess comes on top.
- **Al atomizes coarser than bronze** at the same 40 kHz. The capillary wavelength goes as (surface tension /
  density)^(1/3), about 1.3× for Al against Cu alloys (textbook values, assumed). So 17 % under 63 µm is an upper
  estimate for Al. The lab's Al 4047 powders looked coarse under the SEM: "around 40–60 µm for the smaller
  particles" (DAL #159).
- **The coarse powder isn't lost.** The 63–250 µm and the flakes can go back into a later run, with more oxygen each
  time. That saves metal, not runs: each run still makes the same share of fines.
- **The cups, not the crucible, limit a cup charge.** Four 2.5 in cups hold 59 cm³ of metal, a quarter of the 225 cm³.
  The Oct 27 rod pieces were about 125 mm long (270 g each of 3/4 in bronze rod). Cups that long would about double
  the charge, to about 300 g.
- **For DED the sums are kinder.** About 70 % of the k7m2q9 powder by volume fell in 50–200 µm (DAL #219).

### The lab's own footage, cut in

Every piece is the lab's, credited on screen. None of it is Al-10Si: each caption says what it is.

| Beat | Piece | What it shows | Source |
|---|---|---|---|
| Four cups in | photo | the Oct 27 charge: four 630 bronze rod pieces, 1,079.886 g on the balance | Gage Erickson, DAL #219 comment 6457884447 |
| The melt | 3 clips, 5 + 7 + 4.5 s | through the furnace port: the bronze pieces round the sealing rod glowing, sinking into their own melt, then fully molten | [2brsz-90seg](https://youtu.be/2brsz-90seg) at about 1:02, 4:36 and 5:28 (k7m2q9, Oct 27) |
| The pour | clip, 7.5 s | through the view port: the bronze jet on the tip of the W-coated CF plate, atomizing | [2brsz-90seg](https://youtu.be/2brsz-90seg) at about 8:17 |
| The pour (round 8) | clip, 7 s, cropped to the video (the talk's black bar and webcam inset off), beside the model | a melt stream, a line of drops, onto the tip of the vibrating plate, breaking up into a spray; the talk names neither the alloy nor the run | Sterling Baird's MS&T 2026 talk, [YmvaeqOQAU4](https://youtu.be/YmvaeqOQAU4?t=298) at 4:58-5:05 |
| The powder | 2 photos | the k7m2q9 bronze powder in a jar on the day of the run, not yet sieved; the Oct 22 Al 4047 run c3k0n5 as collected, a bag of splats and a jar | DAL #219 comment 6457884447; Ronnie Guymon, DAL #159 comment 6353788099 |

Round 8 took out the Oct 8 Al 6063 clip ([dTyuZmqYxHA](https://youtu.be/dTyuZmqYxHA), which dripped rather than
atomized: "a dud", Sterling) and moved the sieved-jars photo to chapter 3, after its sieving.

The clips were fetched through a lab Pi (YouTube refuses the runner) and cut at keyframes. `out/footage/` keeps only
the windows used, at 720 px tall with no sound, and the photos at 1600 px: 2.4 MB in all.

**What the footage shows that the model doesn't:** the Oct 27 rod pieces stand up past the crucible's rim, their cut
ends level with the rod's adapter, where the four cups sit 19 mm under it. Rod pieces that long are the "about 125 mm"
above, and the reason a cup charge is so much smaller than a rod charge.

### What the clip says, and where it comes from

| On screen | Value | Source |
|---|---|---|
| Charge | 4 cups, 156.7 g, Al-10Si (3.92 g of Si powder 27.7 mm up each bore) | `out/alloy_recipe.json` (charge.py: #222's cup and plug, tapped Si 1.10 g/cm³) |
| Four cups a run | how the lab loads the crucible; the lab's own Al runs were 169–180 g | PR #318; DAL #159 (Oct 6: 180 g of 6063; Oct 21 and 22: 169 g of 4047) |
| Loading order | rod fitted and seated first, then the metal round it | GU500 manual pp. 15, 47–51, via #222 |
| Getting past the rod's adapter | straight down misses by 1.35 mm; tipped in, −0.09 mm (−2.1 to +0.5) | #222 README, `loading_margin()` |
| Gas wash | 3 cycles, pump to 4 × 10⁻¹ mbar, back-fill with 5N Ar, O₂ under 50 ppm | Ge et al. 2025; Ukabhai et al. 2025; GU500 pp. 18, 36, via #222 |
| Vent | Ø1/16 in through the plug: the air under it leaves on pump-down | #104, #222 |
| Coil | 10 kW, 7 kHz | GU500 p. 18, via #222 |
| Thermocouple | Type N in the crucible wall, to 1300 °C; the metal lags the reading | GU500 pp. 18, 36, via #222 |
| Pour | 200 mbar Ar over-pressure on the furnace; the melt's own head is ~7 mbar | Ge et al. 2025, via #222; #222's 2γ/r working |
| Nozzle | 0.7 mm for Al alloys, 0.5 mm standard; ours not identified | AMAZEMET training (#124 step 2a.2); #222 |
| Ultrasound | 40 kHz | #124 (the training's scan: one wide peak a little over 40 kHz) |
| Powder, 91 % usable, 17 % under 63 µm | the Oct 27 bronze run | DAL #219 |

**Assumed, not measured**
- **The 750 °C hold.** Al-10Si is liquid above about 595 °C. The training holds 4047 (Al-12Si) at about 800 °C; 750 is
  a choice.
- **The melt's density**, 2.37 g/cm³, which sets the pool's level, and **the loose powder's**, 1.40 g/cm³, which sets
  the heap.
- **The 400 cm³ crucible's fill**, taken as the Oct 27 run's 63 %. Its shape isn't known here.
- **The furnace/chamber gauges** (+150 mbar during the melt, +350/+150 at the pour) are the training's style of
  reading with #222's 200 mbar difference. They are not a recipe.
- **The cradle, the tong's sleeve and the ballast plate on the MiR** are this model's; chapter 1 owns the carrier.
- **The arm opens the lid by its knob** and swings it 110° (the training animation's angle) about a hinge on the left,
  after it has undone the latch (round 6). The footage suggests the real lid hinges at the back. Nobody has checked
  that a UR10e can lift the real hood.
- **The latch's force** (100 N, 200 N stiff) is Kipp's published hand force for cover latches of this kind, not a
  measurement on our lid. A spring scale on the lever would settle it.
- **The loading tong** is a design, not a part: the jaws' spring, the fingertip blocks that work them and a ceramic
  lining against hot Al are all assumed.
- **The arm swings the sealing-rod lever up** on its pivot to load, and back down over the adapter after. Nobody has
  checked that it can pull the eye's safety pin, nor that the rod stays seated with the lever up.

**Open questions the clip raises**
- **Can a robot load the cups? With the tong, yes, but a 3/4 in cup still squeezes past the adapter** (#222's
  −0.09 mm, too close to call). Round 5's problem, the 2F-85's fingers not fitting the bore, is gone: the tong
  carries the cup to the floor (round 6, above). What is left:
  - a 5/8 in cup, which goes straight in (+1.83 mm);
  - or ask AMAZEMET whether the adapter can be pinned on after loading.
- **Four cups leave 2.2 mm between neighbours.** A cup that lands off its place can block the next one.
- **The vent can misbehave.** #222's README warns that a Ø1/16 in hole can draw powder out during pump-down
  and wick liquid Al under the 200 mbar over-pressure.
- **Taking the container off under argon** assumes the container's own valve closes and the flange clamp opens
  with the chamber still at over-pressure. The training vents the chamber first; check the order with AMAZEMET.
- **The MiR parks 260 mm off the view port** so the arm has room to reach the lid knob, and 460 mm off it for the
  container: closer, the knob falls inside the UR10e's unreachable cylinder over its base, and the forearm comes down
  through the MiR's cabinet to the container's handle. Check the floor space in front of the real rePowder.

### Checked for collisions, and the cups let go higher (PR #318, 2026-11-04)

*Round 5. Round 6 replaced the release over the bore with the loading tong, and the cradle on a post with a low
ring; see above. Kept for the record.*

Sterling: "the robot arm didn't respect collisions with itself, at all. Passed through the MiR250 and collided with
the vial holder." Round 5 rendered this chapter before the arm was checked. `ARM_AUDIT=1` (`collide.py`, FCL on the
drawn meshes; [`notes/arm_collisions.md`](arm_collisions.md)) found **257 of 1421 checked frames** with the arm,
the gripper or what it held in something, with the planner on. Now: **10 of 1586**
([`out/collisions/alloy_atomize.json`](../out/collisions/alloy_atomize.json); the chapter is 165 frames longer, for
the lever). Both counts are at 15 fps. The committed render is at 10 fps, to fit the session (`VIZ3D_FPS=10`).

**What is left: two joint moves the planner can't route** in its 2500 RRT-Connect iterations, both with the upper arm
through the container's cradle on the MiR's own cabinet (MiR-local (280, 10), 300 mm from the arm's base). The
straight joint line is used instead:
- cup 4's move from the carrier to over the crucible, 6 frames;
- the move from the lid's pose to the raised lever, to lower it, 4 frames (one with the fingertip on the lever).

Moving the cradle out of the upper arm's sweep should clear both. The container's placement checks out at
(300, −170) on the cabinet as well, turned 0°, 90° or 270° (a probe of the planner's IK branches); chapter 3 doesn't
read the cradle's place. Not done: there was no time left to re-render.

| Where | What was wrong | What changed |
|---|---|---|
| The lid's knob (2/5), 117 frames | The knob is a 28 mm ball whose centre stands 12.7 mm off the hood's front-right face. The level grasp from the front put the right finger, its knuckles and its tip through the face for the whole swing, open and shut. | The pads go either side of the ball along the face, the fingers pointing down its slope, their width square to it, 3 mm out from the ball's centre (`knob_grasp`). The arm takes the IK branch from which the whole 110° swing and the approach are clear (`arc_branch`). The knob is its own scene group, so the audit lets the pads touch it and nothing else of the hood. |
| The cups (2/5), 60 frames | The forearm and wrist 1 in the rePowder's cabinet behind the furnace for the back pair; the gripper in the filling cone, the crucible, the sealing-rod lever and the wall thermocouple; the cup through the rod's adapter on the way in. Most of the gripper's contacts weren't even counted: the cup was let go into the whole rePowder, so for 4 s round each release the audit forgave the gripper touching any part of the machine. | Below. The cups are now let go into the crucible, so only the crucible's own parts are forgiven. |
| The sealing-rod lever | Down, its bar lies over the places of the cups at 70° and 295°. The 2F-85's fingers reach 40 mm along the cup's tangent and would straddle it. | The arm swings the lever up on its pivot before the cups, and back down over the adapter after them: `model.py` has it swing up 95° "to clear the opening" (training video T4, 1:18-2:17), "clear of everything that goes into the furnace". It takes the bar from above, 40 mm from the rod. The rod stays seated. |
| The container (5/5), 80 frames | Every IK solution for the level grasp of the handle, 275 mm off the floor, had the forearm or the wrists in the MiR's own cabinet and body; the fingertip in the open flange clamp; then the container through the chamber's bottom on the way up, and the arm folded into its own base over the cradle. | The MiR stands 200 mm further out for this step (y = −2650). The handle is taken at its outer end (x = 356 in the model, clear of the open clamp's front half, which is over its inner 40 mm), level from the front and 15° from the right. The fingers open only to 19 mm for the 12 mm bar: wide open, the upper one reaches the chamber valve's handle, 27 mm over it. The container comes 230 mm out (was 170) before it goes up. The cradle stays where it was. |

**The fingertip clearance: the arm lets go higher.** Round 5 let go of each cup at #222's tight spot, the cup's top just
under the adapter, with the 2F-85's fingertips 14.7 mm under the rim and their outer corners 4.2-4.9 mm into the
crucible's wall. The fingers' corners stand 31 mm out from the axis there, and the bore is 28.55 mm, so nothing short
of other fingers gets them into it. Of the three options (let go higher, grip higher, fit the adapter after loading),
this chapter now **lets go higher**:
- the 2F-85 holds the cup 8 mm under its top (was 13), so its fingertips stay 5 mm higher and still overlap 27 mm of
  the cup;
- it carries the cup down a fixed path (`descent`): beside the adapter; tipped 4.1°, the foot over the bore's lip; the
  foot at the rim by the rod; then down the bore on a line 0.3 mm inside the bore at the rim (`LINE_R`);
- it goes down that path only as far as the checker finds the gripper and the arm clear of everything (`release_at`),
  and lets go there. The rest of the way, past the adapter and onto the floor cone, the cup slides on its own;
- where it lets go, per cup ([`alloy_atomize_clearance.json`](../out/alloy_atomize_clearance.json)):

  | Cup | Place | Foot | Fingers' lowest point | Fingers to the filling cone |
  |---|---|---|---|---|
  | 1 | 145° | 13.4 mm in the bore | 22.3 mm over the rim | 3.9 mm |
  | 2 | 70° | 19.1 mm over the rim | 55.0 mm over the rim | clear of it |
  | 3, 4 | 220°, 295° | 14.7 mm in the bore | 21.0 mm over the rim | 3.9 mm |

  None of them reaches past the bore. Cup 2 is let go highest because the wall thermocouple stands 38 mm proud in the
  filling cone at 40°: lower, a finger meets its sheath. Cup 2 drops 19 mm before its foot reaches the bore;
- the gripper lets go by opening to 0.70 (its pads 4.5 mm off the cup), not all the way: wide open, the fingers
  swing out into the filling cone. It opens fully on its way back to the carrier.

**#222's −0.09 mm is still there.** On that line the cup's inner side meets the adapter by about 0.3 mm in the model
(the meshes' facets cost 0.2 mm of the bore). That is #222's "too close to call" squeeze, drawn: the held cup's one
contact, which the audit allows as the place it is let go. Whether a real 3/4 in cup slides past the adapter on its
own is the same open question as before; a 5/8 in cup (+1.83 mm) goes straight in.

**The lever up is assumed.** The lever's eye drops over the adapter's top stub with a safety pin through it (implied
in the model). Nobody has checked that a UR10e can pull the pin and swing the lever, nor that the rod stays seated
without it. Ask AMAZEMET alongside the lid's latch.

**Re-rendering only the ending.** `ATOMIZE_TAIL=N` counts the frames of the first N sub-steps without drawing them,
so a changed ending renders in a minute. It writes only the tail to `out/clean/`; splice it onto the earlier render
by hand (ffmpeg trim + concat), as round 4 did. `ATOMIZE_PART=a:b` draws only sub-steps a to b−1, into
`out/clean/*_part<a>*`, so the chapter can be rendered in parts side by side on a machine with the room for it;
`python3 alloy_atomize.py merge` joins them and splices the footage in.
