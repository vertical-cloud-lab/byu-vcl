## The alloy route, chapter 2: atomize (`alloy_atomize.py`)

The MiR250 brings the four charged 5N Al cups from the VLM to the rePowder. The UR10e opens the lid, loads the cups
round the sealing rod and shuts the lid. The machine, cut open at the furnace axis, washes, melts and atomizes the
charge. The arm then takes the powder container off onto the MiR. Clips and photos of the lab's own runs are cut in
where the animation reaches the same moment: the charge, the melt, the pour onto the plate, the powder and the sieved
powder.

| | |
|---|---|
| Clip | 167.3 s (156.5 s before the MiR250 kept to its 0.3 m/s², round 5's fixes), 43.6 s of it the lab's own footage; [GIF](../out/alloy_atomize.gif) (640 × 360, 5 fps, 5.5 MB), [MP4](../out/mp4/alloy_atomize.mp4), [still](../out/alloy_atomize_still.png), sub-steps in [`alloy_atomize.json`](../out/alloy_atomize.json), powder sums in [`alloy_atomize_powder.json`](../out/alloy_atomize_powder.json) |
| Starts | MiR250 at the VLM's opening (`animate.AMR_XY`), the four Al cups in `charge.carrier()`'s four pockets at `animate.BUFFER_LOCAL` on the cabinet: where chapter 1 ends |
| Ends | MiR250 at world (−3487, −2230), yaw 0: square to the container's axis, 41 mm off the view port's flange, the hand-off chapter 3 (sieve, print) starts from. The container stands in a cradle at MiR-local (280, 10), seat z = 933 mm; the arm is parked. While the arm works the MiR stands 220 mm further out (y = −2450), because at y = −2230 the lid knob and the container's handle fall inside the UR10e's unreachable cylinder over its base; it drives onto the hand-off spot at the end |
| Scene | `line.py`'s layout as `alloy_workflow.py` builds it, the rePowder loaded part by part from `repowder/model.py` (the merged copy `animate.Lab` adds is hidden) |
| Ported | `Pool`, `Powder`, `Particles`, `stream`, `film`, `shake`, the heat colours, the argon volumes, `load_machine`/`set_cut`: #124's rePowder training animations (`atomizer-training/viz3d/steps.py` and `scene.py`, branch `claude/issue-124-20261003-0335`) |
| Footage | [`out/footage/`](../out/footage/): the excerpts and photos used, small, with a [manifest](../out/footage/manifest.json) of credits |

```bash
xvfb-run -a python3 alloy_atomize.py        # render (1,693 frames, 33 min on a busy 4-core runner), then splice
python3 alloy_atomize.py splice             # only cut the footage into the last render (3-13 min, mostly the GIF)
python3 alloy_atomize.py keep               # copy the excerpts PLAN uses from /tmp/footage (FOOTAGE=...) to out/footage/
python3 alloy_atomize.py powder             # print the powder sums
```

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
- **At release the 2F-85's fingertips are 14.7 mm under the rim**
  ([`alloy_atomize_clearance.json`](../out/alloy_atomize_clearance.json), from the gripper's meshes at the movie's
  poses):
  - they pass 5.4 mm over a seated neighbour's top, which sits 19.1 mm under the rim;
  - **their outer corners run 4.2–4.9 mm into the crucible's wall.** The 2F-85's fingers are 22 mm wide and close
    along the cup's tangent, so their corners reach past the 57.1 mm bore. In the clip they pass through it, and
    round 4's did too.
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
| The pour | clip, 6 s | an Al 6063 stream on a CF plate, which **dripped rather than atomized** that day (CF plate with the 1.5:1 booster) | [dTyuZmqYxHA](https://youtu.be/dTyuZmqYxHA) at about 1:40 (Oct 8, DAL #159, PR #176) |
| The powder | 2 photos | a jar of the k7m2q9 bronze powder; the Oct 22 Al 4047 run c3k0n5, a bag of splats and a jar | DAL #219 comment 6457884447; Ronnie Guymon, DAL #159 comment 6353788099 |
| Sieved | photo | the bronze sieved: < 63 µm, 63–250 µm, flakes over 250 µm | Gage Erickson, DAL #219 comment 6509252104 |

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
- **The cradle and the cup carrier on the MiR** are this model's; chapter 1 owns the carrier.
- **The arm opens the lid by its knob** and swings it 110° (the training animation's angle). Nobody has checked
  that a UR10e can do this on the real hood, nor whether the lid's latch needs releasing first.

**Open questions the clip raises**
- **Can a robot load the cups at all? Not with the 2F-85 as it is.** Two problems:
  - The 3/4 in cup only goes past the rod's adapter tipped, and #222 calls that too close to call (−0.09 mm).
  - The 2F-85's fingers would cut 4–5 mm into the crucible's wall at release (above).

  In the clip the arm lets go once the cup is past the adapter, and the cup slides down to the floor cone. Options:
  - thin, narrow fingers that fit between the cup and the wall: with the pad faces on the cup, a 3 mm thick
    finger can be about 19 mm wide, and the 2F-85's are 22 mm;
  - a 5/8 in cup, which goes straight in (+1.83 mm);
  - ask AMAZEMET whether the adapter can be pinned on after loading.
- **Four cups leave 2.2 mm between neighbours.** A cup that lands off its place can block the next one.
- **The vent can misbehave.** #222's README warns that a Ø1/16 in hole can draw powder out during pump-down
  and wick liquid Al under the 200 mbar over-pressure.
- **Taking the container off under argon** assumes the container's own valve closes and the flange clamp opens
  with the chamber still at over-pressure. The training vents the chamber first; check the order with AMAZEMET.
- **The MiR parks 260 mm off the view port** so the arm has room to reach the lid knob: closer, the knob falls
  inside the UR10e's unreachable cylinder over its base. Check the floor space in front of the real rePowder.

**Re-rendering only the ending.** `ATOMIZE_TAIL=N` counts the frames of the first N sub-steps without drawing them,
so a changed ending renders in a minute. It writes only the tail to `out/clean/`; splice it onto the earlier render
by hand (ffmpeg trim + concat), as round 4 did.
