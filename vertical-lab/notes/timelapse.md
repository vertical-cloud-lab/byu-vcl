# The finale: the whole lab at speed (`timelapse.py`)

Sterling, on PR #318 (2026-11-05 00:37 UTC): "At the very end, I want you to show the entire laboratory operating in
high-speed, starting by the hour, then day-by-day, then by weeks and months showing the total dataset sizes, including
number of unique alloys fully tested and printed."

```bash
python3 timelapse.py model                                   # the throughput model -> out/timelapse_model.json
PREVIEW=1 VIZ3D_FPS=6 xvfb-run -a python3 timelapse.py       # nine frames -> /tmp/preview_timelapse.png
VIZ3D_FPS=6 xvfb-run -a python3 timelapse.py                 # -> out/mp4/timelapse.mp4, out/timelapse.gif, still
python3 timelapse.py gif                                     # the GIF again from the MP4, under 4.9 MB
```

## The render

- **[MP4](../out/mp4/timelapse.mp4):** 525 frames at 6 fps, 87.5 s, 9.5 MB.
- **[GIF](../out/timelapse.gif):** 400 px at 3 fps, 3.8 MB.
- **[Still](../out/timelapse_still.png):** month by month.
- **Cost:** 28 min in one slot (19:11-19:40 UTC), 2.8 s a frame with every tray built.
- **Not checked:** no arm audit, since the units' poses are shown, not planned (see Caveats).

## What the clip shows

The set-up movie's lab as it ends (`setup_lab.build`: two Shuttles with all fifteen trays loaded, the floor machines,
the two MiR250 + UR10e units), seen from the south and above while the camera pans slowly, in six parts. The Shuttles
are drawn see-through, as in the set-up movie just before it. A preview with the Shuttles clad and only the eight
trays the schedule presents (A, B, D, E, F, K, L, M; `setup_lab`'s `VLAB_ONLY_TRAYS`) needed about half the memory,
but the clad Shuttles looked like different machines from the open ones a minute earlier, the inconsistency Sterling
flagged at 9:09 of the last long-form. So every tray is built (about 5.5 GB).

| Part | Lab time | Video | One second of video is |
|---|---|---|---|
| Day 1 | Monday 06:00 | 2.5 s | (the clock stands) |
| 1/4 Hour by hour | the first 24 h | 30 s | 48 min |
| 2/4 Day by day | to day 14 | 16 s | 19.5 h |
| 3/4 Week by week | to week 13 | 14 s | 5.5 days |
| 4/4 Month by month | to week 52 | 16 s | about 17 days |
| The first year | the totals | 9 s | |

- **Driven by the schedule.** Each frame asks the model what is happening at its lab time. A tray a step needs comes
  to its Shuttle's opening while a unit loads or unloads it. Each unit stands at the dock of the station it is
  carrying to, its arm over the presented tray or in front of the machine (an IK pose, not a planned move), or on its
  charger when it has nothing to carry.
- **Beacons** on the floor machines and on each Shuttle's roof show the state: green running, blue a unit at it,
  amber a person at it (the atomizer's crucible), red a run that dripped, grey idle. At the week and month scales a
  beacon is green if its machine was busy more than 15 % of the last day, since anything faster would strobe.
  **The beacons are drawn for this clip.** They aren't part of the design, though signal towers on the floor machines
  would be a sensible addition.
- **Lights out.** At the hour and day scales the room dims whenever nobody is on site (outside 08:00-16:00 on
  weekdays), and the clock panel says so. The lab keeps running.
- **Panels** (PIL, every frame): a ribbon under the title with the clock, the speed-up and the counters; what is
  running now, with the beacons' key (hours and days, bottom left); from week 2 a chart of alloys atomized, printed
  and fully tested (bottom right); the totals card at the end.
- **Cheap frames.** Frames are rendered one at a time (no `Scene.step`): every frame moves groups, re-colours beacons
  and re-draws the panels, and no mesh is rebuilt.

## The model

`simulate()` is a greedy schedule. It takes each alloy in turn, and each of its steps as soon as:
- the step's inputs are done;
- its station has a free spell as long as the step;
- one of the two units has the transfer time (6 min, assumed) free just before it.

Each station and each unit keeps a sorted list of its bookings, so a later alloy can use an earlier gap. The steps are
the route of chapters 1-7. Each step's time comes from this branch's notes or from DAL, or is marked as assumed in
`STEPS` and `PARAMS`. `out/timelapse_model.json` holds all of them with their sources (`out/timelapse.json` is the
clip's own record of its parts, as every scene's is).

**The atomizer's crucible is the one job left to people.** A person changes, cleans and coats the crucible. Sterling:
"Things related to the crucible in terms of automation are going to be very difficult", and
`notes/crucible_automation.md` says why. So a run starts only on a weekday shift:
- three run slots a day (08:00, 10:30 and 13:00), each needing its person for the first hour;
- none after noon on Fridays (maintenance, assumed);
- a ramp: one run a weekday for two weeks while the lab is commissioned, then two a weekday for two weeks.

The rest runs round the clock.

| Step | Station | h | Source |
|---|---|---|---|
| Charge: 4 cups dosed, weighed, pressed under vacuum | multi-doser, HR-202i, vacuum press (tray B) | 1.0 | chapter 1; the press's 2 min hold and 1 min program (`notes/vacuum_press.md`); 15 min a cup assumed |
| Atomize | rePowder | 2.5 | person 1.0 (assumed), a run "about 1 h with prep" (AMAZEMET training T5 21:50), cool-down about 30 min (T3 49:52), both cited in `notes/crucible_automation.md` |
| Sieve | sieving cell | 0.75 | assumed; "four passes of minutes each" (`notes/alloy_print.md`) |
| Laser diffraction, XRD (back-loaded), XRF, SEM of the powder | trays E, D, M, D | 0.25, 0.6, 0.35, 0.35 | assumed; the XRD prep from `notes/edison_r8.md` |
| Screening build, 55 mm kit | Aconity MIDI | 5.0 | the kit takes about 30 g (DAL #138); inerting, a 3 h build, cooling, unloading assumed |
| Depowder | the MIDI and chapter 5's box | 0.5 | assumed |
| Cut off the plate | wire EDM | 0.75 | at least 11 min of cutting (`notes/alloy_workflow.md`) plus fill and drain |
| Heat treat | furnace (tray F) | 3.0 | assumed |
| Tensile: 3 at room temperature, 1 hot | zwickiLine (tray L); 68FM-100 with the 3119-608 chamber | 0.6; 1.5 | assumed |
| Section, face, mount (2), polish (2) | wire EDM; Carvera (M); MX400 and PX500 (F) | 0.4, 0.3, 0.6, 0.8 | chapter 6; the MX400's 0-30 min cure (`notes/alloy_prep.md`), the SOP's 9 min a mount (`notes/alloy_characterize.md`) |
| SEM/EDS, VHX, micro-Vickers, nanoindentation, PIP | trays D, K, L, E, E | 0.5, 0.4, 0.3, 0.75, 0.25 | chapter 7's clocks: about 20 min SEM, 45 min nanoindentation (`notes/alloy_characterize.md`); the rest assumed |
| Corrosion screen, 2 spots | CubXL (tray A) | 2.2 | 67 min a spot with EIS (DAL `copper_numbers.json`, `notes/cubxl_corrosion.md`) |

**Powder.** Each run charges about 300 g of Al, in four cups as long as the Oct 27 rod pieces
(`notes/alloy_atomize.md`). Chapter 1's 2.5 in cups hold 157 g. Using the Oct 27 bronze run's yields (DAL #219):
- 91 % of it is usable;
- 17 % is under 63 µm, about 51 g. That is enough for the 55 mm kit's 30 g.

**Failures.**
- **Runs:** one run in ten drips instead of atomizing, as the Oct 8 Al 6063 run did, and is run again (assumed rate).
- **Builds:** one screening build in seven cracks, and that alloy stops at its powder data (assumed rate).

**Promotion.** One fully tested alloy in ten goes to a full plate of chapter 5's E8 subsize bars. That needs the full
cylinder's 440 g (the lab's planning figure), so eight more runs of the same composition. Then it gets an 8 h build
and two room-temperature and two hot E8 tests on the 68FM-100 (all assumed).

**"Fully tested"** means all of these:
- the atomized powder measured (laser diffraction, XRD, XRF, SEM);
- printed in the 55 mm kit and heat treated;
- tensile tested at room temperature and at temperature;
- sectioned, faced, mounted and polished;
- SEM/EDS, VHX, micro-Vickers, nanoindentation and PIP;
- a corrosion screen on the CubXL.

**Data** per step, all assumed:

| Step | GB |
|---|---|
| Atomizer run: logs and the furnace-port video | 1.5 |
| VHX 3-D reconstruction | 1.5 |
| Build SEM: 12 images, 2 EDS maps | 0.7 |
| Screening build: logs and powder-bed images | 0.35 |
| Tensile with the extensometer's record | 0.1-0.3 |

The powder data are small. Stream video: the 32 cameras the set-up puts in (30 on trays, 2 over the bays), each kept
at 1 Mbit/s, 24 h a day (assumed).

## What it gives

| By | Atomized | Printed | Fully tested | Promoted | Runs | Powder | Tensile tests | Instrument data | Video |
|---|---|---|---|---|---|---|---|---|---|
| 1 day | 1 | 1 | 1 | 0 | 1 | 0.3 kg | 4 | 4.6 GB | 0.35 TB |
| 1 week | 5 | 5 | 5 | 0 | 5 | 1.4 kg | 20 | 23 GB | 2.4 TB |
| 4 weeks | 19 | 17 | 17 | 1 | 30 | 7.4 kg | 72 | 99 GB | 9.7 TB |
| 13 weeks | 86 | 74 | 74 | 6 | 156 | 38 kg | 320 | 0.47 TB | 31 TB |
| 26 weeks | 184 | 158 | 158 | 15 | 338 | 83 kg | 692 | 1.0 TB | 63 TB |
| 52 weeks | 378 | 324 | 324 | 31 | 702 | 173 kg | 1,420 | 2.1 TB | 126 TB |

- **The atomizer is the bottleneck.** It uses every staffed run slot of the year (702 of 702). Its busy share is only
  21 %, because the slots, not the machine, set the pace.
- **The MIDI is next, at 27 %.** No downstream station is above 13 %, so a second shift on the atomizer would roughly
  double the output before anything else limits it.
- **The first alloy is fully tested 16 h after the lab starts,** at 22:00 on day 1, after one run that morning. From
  the end of a run to fully tested is a median of 12 h, at most 23 h.
- **Promoted alloys cost 248 of the 702 runs,** about a third of the atomizer, for 31 full plates. That is the
  price of the E8 bars' 440 g.
- **Stream video dwarfs everything else**, if every stream is kept: 126 TB against 2.1 TB of instrument data.

## Caveats

- **This is a model of the lab running as designed, not a measurement or a forecast.** The rates of the steps the lab
  hasn't run yet (the screening build, the automated sample prep and characterization) are guesses, marked as such.
- **The schedule is greedy, not optimised.** It has no breakdowns beyond the two failure rates and Friday afternoons,
  no holidays, and no waiting for the optimiser. A new composition is always ready. People's time beyond the crucible
  isn't counted: restocking, replacing worn discs, sieve cleaning, the crucible stock.
- **Transfers are booked only at a step's start,** for 6 min, so the units' load is understated.
- **The screening build's miniature tensile specimens are an assumption.** Chapter 5's E8 subsize bars are 100 mm
  long and need the full 170 mm plate, so a 55 mm kit build can only hold miniature specimens. Which geometry, and
  whether the zwickiLine's grips take it, is open.
- **The animation shows the schedule's state at each frame's time, not continuous motion.** At 48 min to the second,
  a MiR250's drive or a tray's trip to the opening is shorter than a frame. Units and trays therefore jump from one
  frame to the next, as they would in a real time-lapse.
- **The arm's working poses are IK solutions without the collision planner.** They're for show at this speed:
  `timelapse.py` has no arm audit.
