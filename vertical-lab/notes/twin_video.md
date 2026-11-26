# The campaign video: a year of the twin, replayed

Round 2's video: the two campaigns' year in the vertical lab, replayed from the twin's own event log, with the figures
we track and what the benchmark found. **Everything in it is simulated**, except the lab design's 3-D renders (PR 318),
the lab's own atomizer footage and photos, the search spaces (the proposals) and the prices and their sources.

**On YouTube:** [Pz7hxqfODmE](https://www.youtube.com/watch?v=Pz7hxqfODmE) (public, subscribers not notified; uploaded 2026-11-26 from commit 73b155f).

**The animated cut** (PR 393, 2026-11-26): the same video with the replay's day-by-day, week-by-week and month-by-month
parts showing PR 318's 3-D lab moved by the event log, instead of station clips and lit stills. Unlisted:
[tX8Ik8oKnhk](https://www.youtube.com/watch?v=tX8Ik8oKnhk) (11:41, uploaded 2026-11-26 from commit dee5887; the public cut is untouched). Its 60 s preview, one simulated week from above: [FR3Fl1onJU0](https://www.youtube.com/watch?v=FR3Fl1onJU0) (unlisted, uploaded 2026-11-26 from commit b16bd36). See
[The animated lab](#the-animated-lab) below.

## What is on screen

| Part | What it shows | Code |
|---|---|---|
| Title | | `compose.title_frame` |
| What is simulated | The lab (the bird's-eye 3-D still) and the two search spaces as periodic-table heatmaps in DAL's style (each element's lower and upper bound) | `compose.simulated_frame`, `ptable.bounds_figure` |
| The function networks | Each campaign's network built full screen node by node, with the twin's simulated instrument data popping out at its node (SEM, EDS, EBSD, XRD, laser diffraction, tensile, PIP, corrosion), then collapsed to icons and docked in a corner | `dag_anim` |
| The figures we track | Best so far against days and against money, with dynamic axes; the state-of-the-art target; the conventional lab's curve; how the acceleration factor (X = days conventional / days automated) and the cost ratio (Y = cost automated / cost conventional) are read off; instrument utilization | `figs_anim.explain_frame` |
| The campaign year, replayed | Day 1 in 80 s of video (37 lab hours): one alloy start to finish, each step shown by PR 318's render of that station (and the lab's own melt and pour footage at the atomizer). Then day by day: the station cameras in 2 × 2 and 3 × 3 grids, each lit while a campaign uses it. Then week by week and month by month: the whole lab from above, each station lit from the event log, as the replay speeds up to about 60 lab hours a second. Throughout: the docked networks with each node lit while it is being evaluated, the compositions in flight as small periodic-table heatmaps, counters, and the live best-so-far plots | `compose.replay_frame`, `birdseye`, `ptable.multiples_panel`, `figs_anim.PlotPanel` |
| Results | The automated lab against the conventional lab for each policy both ran; how much sooner and for how much less each campaign reached the state of the art; cost per experiment; utilization and the capacity left over for outside users | `figs_anim.results_frame` |
| The takeaway | "X times faster at Y of the cost", per campaign, with what Y includes | `figs_anim.takeaway_frame` |
| Notes | What is real, what is assumed and what is simulated | `compose.notes_frame` |

**Speeding up and pulling back.** The replay covers 37 lab hours in its first 80 s, then speeds up: 1.5 lab hours per video second at 80 s, then
5, 15, 42 and finally about 60, and the camera moves from one station's render (day 1) to grids of station cameras
(days 2-23) to the whole lab from above (from about day 23 to the end of the year), as asked.

**Acceleration factor.** AF = the median days (or dollars) the conventional lab needed to first reach the target ÷
the automated lab's, with Kaplan-Meier medians when some seeds never get there and percentile-bootstrap intervals over
seeds (Rohr et al., Chem. Sci. 2020; `twin/accel.py`, `notes/twin_econ.md`). The target is the state of the art: the
best reference alloy's true utility on this synthetic truth.

## The cut

1920 × 1080 at 30 fps, 11:41, captions only (no narration), built by `python -m twin.video.compose final` in 11.6 min
on the 4-core runner (3 encoders, x264 `medium`) beside the benchmark. Chapters (the description's):

| Starts | Chapter |
|---|---|
| 0:00 | What is simulated: the lab and two search spaces |
| 0:54 | The function networks |
| 2:39 | The figures we track |
| 3:41 | The first alloy, start to finish |
| 5:01 | Day by day: station cameras |
| 6:19 | Week by week: the whole lab |
| 7:43 | Month by month, to the end of the year |
| 9:41 | Results |
| 11:11 | The takeaway |
| 11:26 | Notes: real, assumed, simulated |

![Contact sheet of the cut](../out/twin2/video/sheet.png)

- **The replayed run** is `out/twin2/events/vertical_lab_bofn_blend_s0.json`: seed 0 of the main benchmark's BOFN set B
  (plain BOFN for FLAIME, BOFN with blend screening for copper), both campaigns, one year.
- **The numbers on screen** come from `out/twin2/bench2_summary.json` (curves; the conventional lab's are its own 12
  seeds) and `out/twin2/econ/econ_summary.json` (acceleration factors, cost ratios, cost per experiment,
  utilization), through `twin/video/data.py`. The takeaway compares the vertical lab with BOFN against the
  conventional lab with the same BOFN (the lab's own contribution). Its footer and the description add the comparison
  against the conventional lab run with a metallurgist's heuristic (aluminium 1.1×, copper 2.2×), and the description
  says where BOFN doesn't win.
- **The bird's-eye stills** (`out/twin2/video/birdseye/`, four views at 2880 × 1620) are rendered once from the set-up
  movie's lab by `twin/video/birdseye_render.py` (VTK with cadquery for the tessellation, 589 s, peak RSS 3.45 GB) and
  committed, so the cut can be rebuilt without the 3-D stack. Each station's anchor is projected into the still, and
  the replay lights it from the event log.
- **Reused renders.** The station cameras and day 1's shots are PR 318's own clips; the melt and pour are the lab's
  atomizer footage (DAL #159, #219).

```bash
cd vertical-lab
python -m twin.video.compose preview      # about 57 s touching every part, veryfast
TWIN_VIDEO_WORKERS=3 python -m twin.video.compose final   # out/twin2/video/campaign.mp4, youtube_meta.json, sheet.png
python -m twin.video.upload --yes         # public, subscribers not notified; recorded in out/youtube.json
```

## Limits

Everything the video says about alloys, results and costs is simulated (`notes/twin_round2.md`, `notes/twin_econ.md`).
The DED machine has no 3-D model of its own, so its cell is a crop of the bird's-eye still. The video shows one seed's
year; the results and takeaway are over 12 seeds of each lab.

## The animated lab

Sterling, on PR 393: "I was hoping to see the lab actually move: the trays going up and down in the two Kardex towers and
out to the openings, and the MiR250 bases with their UR12e arms driving between openings and working at them." The
animated cut (`python -m twin.video.compose final3d`, `campaign_lab3d.mp4`) keeps everything else in the video and
replaces the replay's camera grids and lit stills with the set-up movie's lab, moved by the replayed run's event log.

**What moves, and why** (`twin/video/lab3d_sched.py`):

- **A booking on a tray** (the doser, Mastersizer, SEM, furnace, metallography, Vickers, PIP, CubXL, VHX and the
  machining tray: `TRAY_OF`, as `birdseye.STATION_ANCHOR` places them) brings its tray to its Shuttle's opening when it
  starts (the unit loads it) and again when it ends (the unit unloads it). In between, the instrument runs in storage
  on its dock, as in the timelapse. A booking on a floor machine (atomizer, sieving cell, MIDI, wire EDM, the Instrons,
  DED, the ICP-MS hood: `DOCK_OF`) docks a unit at its front at both ends. HPC bookings ask for nothing. Idle trays
  stay in their slots.
- **The tower's own moves:** `setup_lab.TwoLab.fetch/store`'s, step by step: the extractor at 1333 mm/s (at least
  0.6 s) to the tray's slot, the 2.2 s slide onto it, the lift to the opening, the shutter (0.7 s), the slide out, the
  shutter. Storing reverses them. One extractor per Shuttle, so one tray out of its slot at a time.
- **The units' own moves:** `warehouse.Amr.route`'s drive at 1.5 m/s, pivoting on the spot at 60°/s, along the dock's
  line to its open end, out to a lane of the aisle and in along the next dock's line, backing in where the floor plan
  says (`BACK_IN`). At the dock, the arm unfolds and passes over three poses that the arm's own IK solves
  (`timelapse.Movie.work`'s targets: over the presented tray's front, or half a metre in front of the machine), then
  folds. The pick and place take `animate.pick/place`'s 3.8 s each. A unit with nothing to do for 2.5 s of video goes
  back to its charger.
- **Two clocks.** The replay runs at 1.5 to 60 lab hours a video second. A tray change takes 8-12 s and a drive 5-15 s,
  so at the replay's speed each move would last a few thousandths of a video second, and the lab would look still. The
  moves run on a second clock instead: 8× real time at a day's pace, rising to 16× at a month's (`move_rate`). Each
  move starts when the replay's clock reaches its booking. A tray change then takes about 1.2 s of video, slow enough
  to follow its six steps.
- **When the moves can't keep up.** At 15-60 lab hours a second, Shuttle 1 is asked for 4-14 trays a video second and
  can show one every two or three seconds. When a Shuttle or a unit comes free, it takes the latest request that has
  reached the clock and drops the older ones still waiting. A request for the tray already at the opening is served
  there. A tray waits at most 2.5 s for a unit, and a machine 2 s. The panel at the bottom says how many requests were
  drawn: in the preview's week (days 120-126), 73 of 138 tray requests and 40 of 58 machine visits. So the moves show what the lab is doing, not how much. The counters,
  the lit stations and the networks still count every booking.

**How it is drawn** (`twin/video/lab3d.py`): the scene is `birdseye_render.build`'s, the set-up movie's lab with both
Shuttles see-through and every tray loaded. A frame's state goes onto it through the set-up movie's own objects: each
tray's `[y, z]` and lamp (`L.tray`, `L.where`), each Shuttle's extractor and shutter (`L.use(shuttle)`, `L.lift_z`,
`L.shutter`, `L.apply_state()`), the MiR250s (`setup_lab.Unit.set`) and the arms (`robot.Robot.set`). Nothing is
rebuilt. `kin.json` (`out/twin2/video/lab3d/`) carries what the scheduler needs from the built scene: slots, docks,
chargers, the aisle and the arm's work poses. The overlays are the replay's own (the clock, the stations lit by
`birdseye.Birdseye.frame_live` on the render's projected anchors, the docked networks, the periodic-table insets, the
live plots), plus a tag on each tray presented and each unit on the move, the moves panel, and an inset from a second
camera on the two Shuttles.

**Render budget** (measured on the 4-core runner, llvmpipe): the 589 s the bird's-eye still took was mostly building
the scene. That is 983 s the first time, for the tessellation, and 90-125 s once it is cached, at 3.0 GB. A 1920 × 1080
frame of the whole lab (3,034 actors, 7.9 M triangles) takes 0.9 s of wall time with depth peeling and 0.6 s without,
and from above the two look the same. Of the three options:

- *Keyframes per lab event and interpolate:* the scheduler already works this way. Every move is scheduled per event
  and interpolated analytically. An image can't be interpolated between keyframes without ghosting, though, so each
  frame still needs its own render.
- *A lighter level of detail:* would cost the trays the detail that shows what is on them, and the full scene is
  already cheap enough.
- *Chosen: a lower frame rate with held frames.* The 3-D lab renders at 15 fps day by day (each render held for two
  frames of the 30 fps cut) and at 10 fps from week by week on, at 15-60 lab hours a second (held for three). A render
  is reused whenever the plan's state hasn't changed (`Plan.key`), so an idle lab costs nothing. The overlays are
  drawn at 30 fps on top.

What it cost on the runner (2026-11-26):

| | 3-D frames | renders (the rest reused) | render workers | wall time |
|---|---|---|---|---|
| The preview's week: the main view, 15 fps | 900 | 850 | 3 at 1920 × 1080 | 7.5 min |
| The preview's inset, 15 fps | 720 | 709 | 1 at 960 × 540 | 7.5 min |
| The re-cut's replay: main views (15 fps day by day, then 10) | 3,231 | 3,083 | 2 at 1920 × 1080 | 30 min |
| The re-cut's replay: insets | 1,554 | 1,458 | 1 at 960 × 540 | (the same 30 min) |

Each worker builds the scene once (about 115 s), renders its batch of chunks (`lab3d_cut.run_jobs`), and holds 3.0 GB.
With llvmpipe at two threads a worker, three workers keep the four cores busy, at about 1.1 s a 1080p render. Few
renders are reused, because once the replay is past a day's pace something is nearly always moving. The overlays and
the encode come after (`compose final3d`: 6.2 min for the whole 11:41 on three workers).

In the re-cut's replay (from day 2 to the end of the year), the event log makes 2,625 tray requests and 1,576
machine requests, one at each booking's start and end. The Shuttles drew 119 presentations, serving 1,049 of the
tray requests: a request for a tray already out, or one asked for again while the Shuttle was busy, is served by the
presentation that brings it out. The units made 226 machine visits, serving 1,107 machine requests.


**Cameras** (`lab3d.VIEWS`): `towers_c` (both openings close, from the west along the aisle, under the cable tray)
and `plan` (straight down on the aisle and docks) day by day; `high` (the still's view 1.5 m to the east and a little
wider, so every booked station clears the panels), `sw` and `se` from week by week on, with a return to `towers_c`.
Cameras from the east or south-east look through the cable tray.

```bash
cd vertical-lab
VIZ3D_SIZE=1920x1080 xvfb-run -a python -m twin.video.lab3d kin      # kin.json, from the built scene
python -m twin.video.lab3d_cut preview                                # the week: out/twin2/video/lab3d_week.mp4
TWIN_VIDEO_LAB3D=1 TWIN_VIDEO_WORKERS=3 python -m twin.video.compose final3d   # campaign_lab3d.mp4, sheet_lab3d.png
python -m twin.video.upload --yes --file out/twin2/video/campaign_lab3d.mp4 \
    --meta out/twin2/video/youtube_meta_lab3d.json --privacy unlisted
python -m pytest -q twin/tests/test_lab3d_sched.py
```

**Limits of the animation.** The moves are drawn 8-16 times faster than real time but thousands of times slower than
the clock, so at the replay's speeds most requests are not drawn (see above). The units' routes ignore each other:
the two lanes keep them from meeting head on, but nothing stops them from crossing at a dock's entry. An arm's work is
the same three poses at every dock. It shows that the arm works there, not what it does. Bookings on stations without
a 3-D model of their own (the DED machine) move a unit to their reserved footprint.
