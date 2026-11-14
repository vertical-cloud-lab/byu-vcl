# Chapter 4: the powder, checked (`alloy_powder.py`, round 8)

Sterling, on PR #318 (2026-11-05 00:37 UTC), about the round-7 long-form:

> The laser diffractometer demo was really quick and not very informative. [...] you should be showing the
> characteristic data that comes from each of these techniques [...] The rigaku miniflex has kind of a poor angle, or
> you should make the door more transparent from the beginning. The goniometer is already moving by the time the door
> is opening. [...] why isn't this inline with the rest of the animation [...] (i.e., why isn't a tray coming and then
> the robot is putting something in there). Also, for powder XRD, you didn't show anything related to the sample prep
> for it, which is actually kind of an art. [...] For the XRF, it's not clear how the sample is making it somewhere
> else. [...] Instead of the stock AlSi10Mg powder, you should pull SEM images from the Al powder we actually atomized.

This chapter answers those in one run, in the whole two-Shuttle lab as the set-up movie leaves it
(`setup_lab.build`), so every tray is loaded whenever the VLM shows (the 9:09 complaint: "suddenly the VLM only has a
few things on board").

## What happens

| # | Where | What |
|---|---|---|
| 1 | Shuttle 1 | While the plate prints (chapter 3), the MiR250 + UR10e brings a retained sample of the sieved 20-63 µm cut, about 15 g in a vial with a mesh cap, to Shuttle 1's dock. |
| 2 | Tray D, prep station | The arm takes the vial by its side and, turning it over and shaking it, sifts the powder onto a zero-background holder, dusts an SEM stub and fills an XRF cup. A blade strikes the holder's powder off flush with its reference plane, the excess into a trough. Nothing is ground or pressed. |
| 3 | Tray D, Rigaku MiniFlex | The door, drawn see-through from the start, opens to 80 deg; the goniometer stands still. The arm carries the holder in by its fin and sets it on the stage. Door shut and locked, X-ray lamp on, then the goniometer moves: theta 5 deg / 2theta 10 deg to 45 / 90 deg, the holder spinning. The pattern (computed). |
| 4 | Tray D, Hitachi TM4000PlusII | The stub, on a 1.5 in carrier, goes into the SEM's mount cup (r8_char's, with the spring plunger), door in, pump-down; the lab's real images of the same powder, and the particle count. The XRF cup goes onto the MiR. |
| 5 | Tray E, Mastersizer 3000 + Aero S | About 5 g poured into the Aero S. The optical bench in cutaway: the background, the feeder running, large particles scattering narrow onto the focal-plane arcs and small ones wide onto the large-angle detectors; then the size distribution. |
| 6 | Tray M (Shuttle 2), Bruker S2 PUMA | The MiR drives to Shuttle 2 at its 0.3 m/s² (props.ramp_frac, from PR #321). A hatch in the hood's top slides back, the port opens and the chamber's lift ring rises 60 mm through it; the arm sets the cup on the ring, which lowers it over the tube and the detector under helium; the spectrum (illustrative). |
| 7 | | The record: size, phases, shape and composition, each tray brought to an opening only when needed. |

## Real, computed, illustrative

- **SEM images: REAL.** The lab's own Al 4047, ultrasonically atomized on the rePowder on 22 Oct 2026, run c3k0n5
  ([DAL #159](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/159)), imaged on BYU's Apreo at 5 kV
  by Ronnie Guymon on 26 Oct 2026 ([DAL #157](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/157)).
  They replace the stock AlSi10Mg image. The caption says they come from a floor SEM, not the TM4000 shown.
- **Particle count: measured from those images** (`r8_powder_data.py`): 972 particles, Dn50 67 µm and Dv50 101 µm as
  imaged, which is the powder before it was sieved.
- **Laser diffraction: COMPUTED.** No Mastersizer result for this powder exists. The curve is the SEM count by volume
  put through a soft-edged 20-63 µm sieve: Dv10 44, Dv50 58, Dv90 72 µm. The panel is badged so.
- **XRD: COMPUTED.** Al-12Si (Al 4047) from Bragg's law, structure factors, Lorentz-polarization and Cu Kα1/Kα2
  (`r8_powder_data.py`). The panel is badged COMPUTED, NOT MEASURED.
- **XRF: ILLUSTRATIVE.** Real line energies and the Aluminum Association's 4047 limits; the heights and the result
  column are made up. Badged ILLUSTRATIVE.

## The XRD prep, and why this way

From Edison's literature answer ([`../out/edison/auto_pxrd_prep/answer.md`](../out/edison/auto_pxrd_prep/answer.md),
summarized in [`edison_r8.md`](edison_r8.md)):

- **Don't grind ductile metal powder.** Milling gas-atomized Al-Cu turned the spheres into larger flakes by cold
  welding, which creates the preferred orientation grinding is meant to cure. So the powder goes on as sieved.
- **Fill evenly with minimal pressure, flush with the holder's reference plane.** Brush or sift fine powder on rather
  than forcing it in. Whitfield, Huq and Kaduk, *Specimen preparation*, International Tables for Crystallography H
  (2019), [doi:10.1107/97809553602060000945](https://doi.org/10.1107/97809553602060000945).
- **Back-loading** fills the inverted holder from behind and helps platy or needle-like powders. These are spheres,
  so sifting on and striking off is enough; the caption doesn't claim back-loading.
- **The automated way:** A-Lab's UR5e pours powder into a vial with a steel-mesh lid and inverts it over the holder
  (Szymanski, *Automating the synthesis and characterization of inorganic materials*, 2024). Our vial's mesh cap is
  that idea; the shaking is ours.
- **Height is the check:** 0.1 mm too high moves Al 111 by -0.072 deg 2theta on the MiniFlex's 150 mm goniometer
  (`r8_powder_data.height_shift`). 0.2 mm of powder is "infinitely thick" to 99 % at 2theta = 90 deg, so the 0.5 mm well
  is enough (`thick_enough`).
- **Spin the holder.** It samples more crystallites; it doesn't remove orientation. Drawn here; whether this MiniFlex
  has a spinner is an assumption.
- **The diffractometer's door by an actuator:** Yotsumoto et al., *Autonomous robotic experimentation system for powder
  X-ray diffraction*, Digital Discovery 3, 2523 (2024),
  [doi:10.1039/d4dd00190g](https://doi.org/10.1039/d4dd00190g), drove theirs with one. Ours is drawn on the hinge.

## Our designs and assumptions (every size an estimate)

- **The prep station** (`r8_powder.pxrd_prep`, on tray D where the OpenFlexure array stood, `TRAY_PLACEMENT`, so the
  set-up movie and `setup_lab.py fit` include it): a 380 × 220 × 100 mm pedestal, the holder's nest at its front edge,
  a 1.5 in stub carrier, an XRF cup, a blade on a small linear axis, a trough.
- **The holder's fin** (14 × 8 × 30 mm, on a tab 30 mm in front of the well): the gripper closes across it, so its
  fingers never reach under the carrier and nothing of the gripper is near the beam's plane.
- **The stub carrier**: a 38.1 mm aluminium disc 25 mm tall with a pin stub, so the SEM's 1.5 in mount cup and its
  spring plunger (r8_char) hold and ground it like a mount; it stands 13 mm proud of the cup's rim for the fingers.
- **The XRF hatch.** At the VLM's opening the S2 PUMA's hood can't open far enough for an arm to reach under it: its
  front corner reaches the 856.5 mm goods height at about 20 deg. Bruker's brochure says the Automation version takes
  samples "into the sample chamber directly or via buffer positions"; drawn here as a hatch in the hood's top that
  slides back over the chamber's port. The real mechanism is a question for Bruker.
- **The XRF seat** used in the tour is now the front-right one (`XRF_SEAT`), nearest the arm.
- **The MiR at Shuttle 2** stops 450 mm left of the dock's centre, in front of the XRF's end of tray M.
- **The holder goes onto the stage turned 25 deg about its axis.** Square to the door, the arm's wrist and forearm
  went into the door (open to 80 deg) and tray D's camera post on the hinge side (`ARM_AUDIT`); turned, the arm comes in
  from the left of the doorway. The spinner takes the holder any way round.
- **The S2 PUMA's lift ring rises 60 mm through the open port** to take the cup, then lowers it into the chamber. Set
  down at deck level, the arm's forearm went into the hood round the hatch (`ARM_AUDIT`). The ring's travel is ours.
- **The XRD door opens to 80 deg, not the tour's 100:** tray D's middle camera post (`services.TRAY_CAMS["D"]`, its
  mast 140 mm in front of the door's hinge) is in the way past about 85 deg.
- **The Aero S cover** lifts off by an actuator (by hand in Malvern's videos), as in round 7.

## Physical sense: what was checked

- Nothing floats: the holder, the stub carrier and both cups are in the arm's gripper, in a nest, or in an
  instrument's own part (the XRD stage, the SEM door's cup, the XRF's lift ring) at every frame.
- The vial's powder moves to the mesh cap when it is upside down and back when it is righted.
- The excess struck off the holder lands in the trough, where it stays.
- The XRF cup stays in the S2 PUMA, and the holder and the stub stay in the MiniFlex and the SEM, until the next
  sample: the trays go back with them inside, doors shut.
- **Left as drawn:** the falling powder is a few dozen points; the dusting on the stub and the fills are simple solids;
  the holder spins on a stage with no spinner drawn.

## As rendered (2026-11-05)

- **`out/mp4/alloy_powder.mp4`: 1275 frames at 6 fps, 3 min 33 s**, 1280 × 720; `out/alloy_powder.gif` at 480 px and
  3 fps (4.9 MB); `out/alloy_powder.json` (the sub-steps); `out/alloy_powder_still.png`.
- **Built with `VLAB_ONLY_TRAYS=DEMKLH`, the Shuttles clad.** My call, after checking the previews: with only some
  trays built, the chapter draws both Shuttles clad (opaque, as a real Kardex), so wide shots show white cabinets, and
  the only trays seen are the one at an opening and the rear columns behind it: D, A, B and E behind Shuttle 1's
  opening, K, L, M and H behind Shuttle 2's (A-C are always built). Every tray that could show is loaded.
- **Arm collisions (`ARM_AUDIT=1`, at 6 fps on trays D, E and M):**
  - audit 1, the first version: 24 of 994 frames;
  - audit 2, after the first fixes: 27 of 996, in three places: the gripper's right finger brushing the holder while
    the vial rolls over it (6 frames); the upper arm through the MiniFlex's open door (21 frames: open, the door
    stands between the arm and the prep station, so reaching for the holder swept through it); the forearm and
    wrist against the door and tray D's camera post going in (3 frames). The XRF's 8 were gone (the rising ring);
  - **audit 3, the rendered version** (the holder taken with the door shut, the arm waiting outside the door's swing
    while it opens): **23 of 1002 frames** ([`../out/collisions/alloy_powder.json`](../out/collisions/alloy_powder.json)).
    The upper arm no longer sweeps through the open door. What is left, all in the render:
    - **the arm's way back to its park pose after setting the holder in the MiniFlex: 16 frames, about 3 s**, its upper
      arm and forearm through the SEM's and the MiniFlex's housings and tray D's left camera post (`cam_D0`). The fix is
      a via pose straight back out of the doorway before the park move, or parking in front of tray D instead of over
      the MiR;
    - the gripper's right finger brushing the holder while the vial rolls over it, 6 frames (about 1 s);
    - the holder touching the open door's edge on the way in, 1 frame.
- **Not fixed in time** (the render was due at 20:45 and finished at 20:55): those 23 frames.

## Running it

```bash
PREVIEW=1 python3 runner_guard.py bg --quick --mem 6500 --log /tmp/p.log -- xvfb-run -a python3 alloy_powder.py
ARM_AUDIT=1 python3 runner_guard.py bg --mem 6500 --log /tmp/a.log -- xvfb-run -a python3 alloy_powder.py
VIZ3D_FPS=6 python3 runner_guard.py bg --mem 6500 --log /tmp/r.log -- xvfb-run -a python3 alloy_powder.py
```

## Round 9 (2026-11-06): Sterling's points 10 and 11 on the round-8 long-form, and the collision frames

- **Mastersizer view and transparency (point 10).** Round 8 ghosted the whole bench body at 18 % opacity, so the cover,
  the cell cassette, the Aero S and the deck stacked over the laser. Now `r8_powder.mastersizer()` moves the outer covers
  (bench shell, plinth, end cap, deck, bay plates, lid, handle, swoosh, status light) into their own piece `shell`, a fade
  joint that goes fully out (not 18 %) for the measurement, leaving the optics bare on a dark base plate; the cell
  cassette is sectioned in half along the beam so its pocket and windows show. No `~body` ghost is used any more (the
  tour clip's actions were changed the same way). The chapter camera (`CAM_BENCH`) is high and in front, from the
  laser's end, so the whole axis (laser, beam expander, lens, cell, detector arcs) is in one frame. Still:
  `out/alloy_powder_preview_mastersizer.png` (the preview before the camera was pulled back a further 25 %).
- **S2 PUMA (point 11).** The hood and body now go see-through in the first step (hatch and port opening), before the
  cup is picked up, and stay so until the measurement is over. The lowering takes 3.6 s (was 2.4), with a held low camera
  (`CAM_XRFI`, from the right so the parked arm is out of the picture) and labels on the lift ring and the tube/detector.
- **Collisions.** Round 8 had 23 of 1002 frames. Fixes: a via pose up over the MiR after the holder is set in the
  MiniFlex (instead of the joint-space move straight to park, which swept the SEM and MiniFlex housings and the camera
  post); the vial held 48 mm over the holder (was 26) while sifting, for the finger brushing the holder. First audit
  after the first pair of fixes: 19 of 1025 frames; the result of the second is in
  `out/collisions/alloy_powder.json` once the audit has run.

### Round 9 outcome (2026-11-06)

- Rendered: `out/mp4/alloy_powder.mp4`, 1309 frames, 218.2 s at 6 fps, 1280x720 (commit `50a8e08`); GIF shrunk with
  `gifsicle --lossy=150 --colors 80 --scale 0.75` to 4.7 MB (the native-size GIF was 7.9 MB).
- **The final render's audit** (run by the orchestrator at 07:20-07:50 in a free slot, `VLAB_ONLY_TRAYS=DEM
  ARM_AUDIT=1`): **19 of 1028 frames in collision, 14 runs**, the same places as the audit before the last two fixes,
  so the via pose over the MiR and the 48 mm sift gap did not clear them:
  - the right finger brushing the zero-background holder while the vial sifts (2 frames);
  - the held holder touching the MiniFlex's door going in (1 frame);
  - the upper arm and forearm sweeping the SEM's and the MiniFlex's housings and tray D's camera post on the move
    away from the MiniFlex after the XRD load (16 frames, in 11 runs).

  `out/collisions/alloy_powder.json` is this audit. The fix is still a waypoint straight out of the MiniFlex's doorway
  before the arm turns for the MiR.
- Not done: re-rendering the `xrd`, `mastersizer` and `xrf` tour clips (their instrument models changed: the
  Mastersizer's `shell` piece), no slot was free. The tour cache is keyed on the sources, so they rebuild on next run.

## Round 10 (2026-11-07): the arm's collisions to 0

- **Audit: 0 of 1028 frames in collision** (`VLAB_ONLY_TRAYS=DEM ARM_AUDIT=1 VIZ3D_FPS=6`, 13 min;
  [`../out/collisions/alloy_powder.json`](../out/collisions/alloy_powder.json), code `b0ec92c`). Round 9 left 19 of
  1028 in 14 runs.
- **The 16-frame sweep was on the way in, not on the way back out.** Round 9's notes put it on the move to park after
  the holder was set on the stage, and added a via pose over the MiR there; that move was clear all along. Built once
  and stopped at each move (a scratch workbench: the scene under `ARM_AUDIT=1`, the movie run to a chosen move, then
  candidate moves tried and checked frame by frame), the hits came on the three straight lines from the wait pose
  into the MiniFlex. The wait pose was a joint move to the IK solution nearest the prep station, with the shoulder pan
  at -169 deg where the branch that is clear on the stage has -71 deg, and the straight line in from that branch swung
  the upper arm and forearm through the SEM, the MiniFlex's housing, tray D's camera post and its slide, and the tray.
  **Fix:** the
  wait pose is taken in the branch that is clear with the holder on the stage (`branch_q`, judged with the door open,
  as it will be), so the line in stays in one branch.
- **The opening door met the holder (1 frame).** The arm waits for the door with the holder 380 mm back along the way
  in, which put the holder's far edge about 372 mm from the door's right-hand hinge, inside its 398 mm swing; the door
  brushed it as it opened. It now waits 480 mm back (about 430 mm from the hinge).
- **The finger at the holder (2 frames).** The vial turns over on its way down to the holder and back upright on its
  way up; at the half-turn the right finger, pointing down, swept the holder's carrier. The mesh now stops 60 mm over
  the holder (it was 48 mm). Tried in the workbench: 60 mm, 0 frames; 30 deg to the left of square at 48 mm, also 0;
  a 150 deg turn instead of 165, 3 frames; 30 deg to the right, 3 frames. *Assumed:* sifting from 12 mm higher doesn't
  change the layer the holder gets (not measured).
- **The collision world** is now kept to what the arm can reach (`fast_collisions`, as chapter 7's): the trays the
  chapter presents (D, E, M) and whatever stands within 2.8 m of the arm's base anywhere on its way, 667 of the 1420
  actors with `VLAB_ONLY_TRAYS=DEM`. The planner and the audit see the same world, and the audit took 13 min (30 in
  round 9).
- **Re-rendered with the fixes** (2026-11-07 23:24-23:59 UTC, `409e723`): `out/mp4/alloy_powder.mp4`, 1309 frames,
  218.2 s at 6 fps, 1280 x 720, `VLAB_ONLY_TRAYS=DEMKLH` (Shuttles clad, as round 9), MP4 11.1 MB;
  `out/alloy_powder.gif` remade with `gifsicle -O3 --lossy=150 --colors 80 --scale 0.75` to 4.7 MB (the script's was
  7.9 MB). `out/alloy_powder.json` (the sub-steps) and `out/alloy_powder_still.png` came out identical to round 9's.
  [`../out/alloy_powder_r10_xrd_load.png`](../out/alloy_powder_r10_xrd_load.png): frames 352 and 370, the arm waiting
  outside the door's swing as it opens, then in through the doorway in the new branch.
- **The render is the audited version.** The audit ran with `VLAB_ONLY_TRAYS=DEM`, the render with `DEMKLH`; both
  collision worlds held the same 667 actors (trays K, L and H stay in their slots and are left out), and the planner
  reported the same twelve joint moves, via poses and IK branches in both, so the render's moves are the audit's.

## Round 11 (2026-11-14): the stricter audit

Sterling, on the round-10 long-form: "There are probably other collisions and interferences that I didn't catch from
this." Round 11's `collide.py` (audit-a) lets the gripper and a held part touch what they handle only up to 1.5 mm deep
and checks everything else that moves (trays, doors, the MiR, the instruments' own parts) against everything else.

| Audit (`VLAB_ONLY_TRAYS=DEM`, 6 fps) | Code | Arm | Movers | All |
|---|---|---|---|---|
| [`alloy_powder_r11a.json`](../out/collisions/alloy_powder_r11a.json), round 10's rules | round 10's | 0 of 1028 | | **0** |
| [`alloy_powder_r11s0.json`](../out/collisions/alloy_powder_r11s0.json), stricter rules | round 10's, the XRF block on the plate | 14 of 1028 | 78 | **92** |
| [`alloy_powder_r11s1.json`](../out/collisions/alloy_powder_r11s1.json), light as non-solid, the cover 55 % open, the door to 70 deg | | 39 of 1028 | 12 | **51** |
| [`alloy_powder.json`](../out/collisions/alloy_powder.json): the committed code, light as non-solid, the cover and the door as in round 10 | `e54631f` | 14 of 1028 | 16 | **30** |

Changed this round, from what the stricter audit found in the other chapters (not re-rendered: the committed MP4 is
round 10's, rendered before these):
- **The XRF cup's block stands on the arm's mounting plate.** `props.mir250` draws the arm's 20 mm plate (|x| < 170 mm,
  top at 800 mm) as part of the cabinet, and the block at MiR (60, -185) was placed at the cabinet's 780 mm, 20 mm down
  in the plate: its pocket's floor was 2 mm under the plate's top, so the cup was set down into the plate. It now
  stands on the plate.
- **The SEM's cup** (`r8_char.sem`, shared with chapter 7): its spring plunger's ball stood 1.6 mm into a seated 1.5 in
  mount or stub carrier; set back to 0.45 mm (chapter 7's notes).
- **Tray E's camera E1** moved behind the Mastersizer (lab, `47219fc`); **the iMicro's lid** lifts without its front
  panel (chapter 7's notes). This chapter only passes them.

What the stricter audit found in this chapter (`alloy_powder_r11s0.json`), and what was done (in code only: the
coordinator kept chapter 4 to an audit this round, so the committed MP4 is round 10's):
- **Light counted as solid (64 frames of the movers check).** The MiniFlex's incident and diffracted beams, the
  Mastersizer's laser, its scattered light and the grains crossing it are drawn as meshes; they are now registered as
  non-solids (`sc.fluids`), as the IPA and the laser are in chapter 3.
- **The Mastersizer's cover swings into the iMicro beside it** (6 frames, 50 mm): `instruments.mastersizer`'s full swing
  reaches past tray E's iMicro. Opened only 55 %, the cover was in the arm's way (25 frames, `r11s1`), so it opens fully
  again (`MS_LID`). **Open:** the cover's hinge or the two instruments' places on tray E (`line.TRAY_LOADS`, not mine).
- **The MiniFlex's door meets camera D1** (7 frames; its head and pan at 80 deg). At 70 deg it still did (`r11s1`), so the
  door opens to 80 deg as before (`XRD_DOOR`). **Open:** camera D1 (lab's `services.TRAY_CAMS["D"]`) needs to stand out
  of the door's swing; requested in `/tmp/r11_post_requests.txt`.
- **Still open, not traced in time:** the zero-background holder set on the MiniFlex's stage 3 mm deep (4 frames); the
  stub carrier reading 12 mm into the SEM's drawer as it is set in the cup (4 frames: the cup's depth, so the carrier is
  touching the cup or its plunger all round; chapter 7's hot mount, the same 38.1 mm, now seats clean in the same cup);
  the forearm against the gripper and the wrist against Shuttle 2's bay at the S2 PUMA (6 frames, new since round 10's
  audit: the bay's model changed this round, `063b014`, and the XRF cup's block is 20 mm higher); the goniometer's
  detector against the holder (1 frame).
- **The camera posts against the arm's paths** (FCL distance): closest to D1 11.3 mm (wrist 2, going into the
  MiniFlex), D0 35.5 mm, E0 41.7 mm, M0 506 mm; E1's new place is out of reach.


