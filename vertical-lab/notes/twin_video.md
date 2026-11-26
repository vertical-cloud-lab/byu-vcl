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
seeds (after Rohr et al., Chem. Sci. 2020, whose factor is a ratio of numbers of experiments, sequential
learning against random selection; here it is applied to days and dollars between two labs: `twin/accel.py`,
`notes/twin_econ.md`). The target is the state of the art: the
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
  utilization), through `twin/video/data.py`. The takeaway compares the stocked vertical lab running BOFN
  (with blend screening for copper) against the conventional lab ordering as it goes and running plain BOFN (DAL's
  audit, digital-alloy-lab PR 293, §4: not "the lab's own contribution", as this said before). Its footer and the description add the comparison
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

## The narrated cut

Sterling asked for narration "at least at the strategic places", on top of the animated re-cut
([PR 393](https://github.com/vertical-cloud-lab/byu-vcl/pull/393#issuecomment-7180846741)): what is simulated and what is
real, the function networks as each is built, how to read the best-so-far plots and the acceleration factor, the first
alloy, the switch to the whole lab, the results, the takeaway with what "Y of the cost" includes, and the closing
notes. Elsewhere the captions and the pictures carry it: 25 lines, 5.5 min of speech in 12:50. It is
built on the animated cut ([The animated lab](#the-animated-lab)), so the replay is PR 318's 3-D lab moved by the event
log.

**On YouTube:** being built (unlisted when uploaded) (unlisted; uploaded 2026-11-26 from commit (pending)), and its 60 s preview (being uploaded)
(unlisted): the opening, then the 3-D lab taking over on day 2 and the first view of the whole lab from above. The
public cut (Pz7hxqfODmE) and the animated re-cut's upload are left as they are.

**The voice** is Kokoro v1.0 (82 M parameters, Apache-2.0 open weights), run on the runner's CPU through kokoro-onnx
0.6.1, with its stock voice `af_heart` at 0.96 speed: no reference audio, nobody's voice cloned or imitated. It is the
same model and voice as the long-form video's narration (`longform.py`). Each line is spoken from phonemes:
`narration.SAY` respells what the voice would misread (FLAIME said as "flame"; ONR, BOFN, DED, LPBF, SEM letter by
letter; "aluminium" as the American "aluminum", since the voice is American), and `narration.IPA` gives CALPHAD
("KAL-fad"), Kardex, Sobol and "doser" their phonemes.

**Heard back.** Every line was transcribed by faster-whisper (base.en and small.en) and compared word by word with what
it should say: 0.55 % (small.en) and 2.0 % (base.en, which twice repeats a phrase that was said once) word error over 910 words. The differences are spellings ("grey"/"gray") and "CALPHAD", a
word the recognizers don't know (`out/twin2/video/narration/check.json`; `lines.ogg` has every line in a row, to listen
to).

**Every spoken number** is on screen while it is said, and comes from `econ_summary.json` or `bench2_summary.json` at
the commit the cut was built from. Each line's `src` in `twin/video/narration.json` says where. Where a number wasn't
on screen, the caption was changed to show it (below). "Simulated" is said wherever it applies, and the copper result is
given as it is: tiered CALPHAD screening finished ahead.

**Captions in step.** These change on the narrated cut only, so the cuts without narration build exactly as before:

- the results' first caption names the leaders the voice names: in the automated lab, BOFN finished highest on
  aluminium; on copper, tiered CALPHAD screening finished ahead of BOFN with blend screening (0.69 against 0.67),
  computed from `bench2_summary.json` (`figs_anim._leaders`);
- the takeaway's footnote says what the operating cost includes: materials, outside fees, labour, service contracts,
  utilities and space, without the equipment's capital cost;
- the notes frame names the voice instead of "Captions only, no narration";
- the takeaway (15 to 51 s) and the notes (15 to 19 s) are longer, to fit their lines.

**Where the lines sit.** Each line is anchored on a segment (`seg`, `at`) or on a named moment inside one (`mark`:
each network card's arrival, day 1's steps, the 3-D lab taking over, the first view from above;
`narration.marks`), so it follows the cut when segments are re-timed. `python -m twin.video.narration plan` prints
each line's time and the caption on screen meanwhile; a line that would overlap the one before, or run past its
segment, is reported. The two lines about the animated lab (`needs: lab3d`) are placed only on the animated cut.

**Rebuilding it.** The audio sources are committed: each line's FLAC (24 kHz, 16-bit) in
`out/twin2/video/narration/`, with its text, phonemes, voice and speed in `lines.json`, so the cut rebuilds without the
speech model. A line is spoken again only when its text changes, which needs `/tmp/kokoro/kokoro-v1.0.onnx` and
`voices-v1.0.bin` from kokoro-onnx's `model-files-v1.0` release (their sha256 in `lines.json`). The track is mixed at
48 kHz, each line levelled to -19 dBFS RMS, and muxed in as AAC; the subtitles are `narration/narration.srt` (the upload
token can't add a caption track, so they aren't on YouTube).

```bash
cd vertical-lab
python -m twin.video.narration plan      # each line's time in the narrated cut, and the caption on screen meanwhile
python -m twin.video.narration tts       # speak the lines whose text changed (Kokoro), into out/twin2/video/narration/
python -m twin.video.narration check     # heard back by faster-whisper
# the 3-D lab needs the set-up movie's stack (VTK, cadquery: twin/video/lab3d.py), so run these with that Python
TWIN_VIDEO_LAB3D=1 TWIN_VIDEO_NARRATION=1 TWIN_VIDEO_WORKERS=3 python -m twin.video.compose final3d
TWIN_VIDEO_LAB3D=1 TWIN_VIDEO_NARRATION=1 python -m twin.video.compose npreview   # out/twin2/video/preview_narrated.mp4
python -m twin.video.upload --yes --file out/twin2/video/campaign_lab3d_narrated.mp4 \
    --meta out/twin2/video/youtube_meta_lab3d_narrated.json --privacy unlisted
```

### The script, with its times in the cut

| Time | Part | Line |
|---|---|---|
| 0:00-0:09 | Opening | This is a simulated benchmark: two alloy discovery campaigns, replayed for a whole year in a digital twin of our planned automated lab. |
| 0:10-0:26 | Opening | Some of it comes from real sources: the lab's design and its 3-D model, footage from our own atomizer, the search spaces in the two proposals, and published prices. Everything else is simulated: every alloy, every measurement, and every result. |
| 0:54-1:07 | The function networks | Each campaign is a function network: a chain of steps, where each step's results feed the next. BOFN, Bayesian optimization over function networks, models every step, not just the final score. |
| 1:09-1:15 | The function networks | For aluminium, the lab makes each alloy's powder itself, then prints it and checks every build. |
| 2:02-2:10 | The function networks | For copper, a one-hour corrosion screen ranks the DED deposits, and thirty days in seawater come before a utility is known. |
| 2:25-2:31 | The function networks | Both campaigns share one lab. From here on, each step is an icon that lights up while it runs. |
| 2:39-2:58 | Reading the figures | Best so far is the highest utility of any alloy tested yet. The dotted line is the target: the best reference alloy's score on the twin's synthetic alloy model. One random design in twelve beats it, so reaching it shows how fast a lab tests its first alloys, not a discovery. |
| 2:58-3:10 | Reading the figures | Against money, the same curve shows what the progress cost. The grey dashed curve is the conventional lab: the same optimizer through partner and core facilities, ordering its metal as it goes. |
| 3:15-3:28 | Reading the figures | Where each first reaches the target, the median over the runs, gives the acceleration factor: here 220 days over 116, or 1.9 times. Money gives the cost ratio the same way. |
| 3:41-3:53 | The campaign year | Day one follows a single simulated aluminium alloy from start to finish. Its cup is machined, its metals are dosed and pressed under vacuum, then melted and atomized into powder. |
| 3:55-3:59 | The campaign year | The melt and the pour are real footage, from the lab's own atomizer. |
| 4:17-4:24 | The campaign year | After sieving and powder checks, it's printed by laser powder bed fusion, then inspected, sectioned and indented. |
| 4:51-4:58 | The campaign year | Wire EDM cuts its bars, and a tensile test scores it, about a day and a half after its cup was machined. |
| 5:01-5:14 | The campaign year | From day two, the event log moves the lab's 3-D model: each booking brings its tray to a Shuttle's opening and back, and a mobile arm drives over to serve it. Trays nobody has booked stay in their slots. |
| 5:35-5:46 | The campaign year | Now the whole lab from above, with the two Shuttles up close from a second camera. The moves run on a clock of their own, so you can follow them; the panel at the bottom counts how many were drawn. |
| 6:20-6:29 | The campaign year | This replay is one seed of twelve, and aluminium's luckiest: it reaches the target on day 20, where the median seed takes 116 days. |
| 9:41-10:05 | Results | Each panel is one policy: twelve one-year runs in the automated lab, twelve three-year runs in the conventional one. BOFN finished highest on aluminium. On copper, tiered CALPHAD screening finished ahead of BOFN with blend screening, 0.68 against 0.58 over 24 seeds, and plain BOFN did no better than random. |
| 10:07-10:29 | Results | Against a conventional lab that orders metal as it goes and runs plain BOFN, the stocked automated lab reached the target 1.9 times sooner on aluminium, and at least 3.7 times sooner on copper, where the conventional lab got there in 6 of its 12 runs. With both labs ordering as they go, aluminium's factor is 1.2. |
| 10:31-10:43 | Results | Per demonstrated alloy, the automated lab costs more while the two campaigns carry its equipment alone. It costs less only if outside users fill it to sixty percent, which the model assumes. |
| 10:47-11:04 | Results | The two campaigns use 5.8 percent of the lab's hours, weighted by capital cost. With an assumed ten hours a week of outside work per instrument, the spare hours would net about 1.2 million dollars a year, 2.1 times the lab's depreciation. |
| 11:12-11:31 | The takeaway | So: in this simulated benchmark, a stocked automated lab reached an alloy better than the reference alloy sooner than a conventional lab that orders metal as it goes: aluminium in 116 days against 220, and copper in 225 days against at least 840. |
| 11:32-11:43 | The takeaway | Most of aluminium's gain is the stock: with both labs ordering as they go, it's 1.2 times. And for copper, the automated lab also screens powder blends first. |
| 11:44-12:08 | The takeaway | To get there, with the equipment included, the automated lab cost 2.0 times as much for aluminium, and 1.15 times for copper; counting only what the campaigns spent, 0.6 and 0.4 times. With the equipment, it costs less only for copper, and only if outside users rent its idle hours, which this model assumes and does not show. |
| 12:09-12:22 | The takeaway | Against a conventional lab run by a metallurgist's rules of thumb, the automated lab is no faster on aluminium, at 2.6 times the operating cost, and 2.2 times faster on copper. |
| 12:24-12:48 | Closing notes | Everything here is simulated: the alloys, the results, and every measurement, with modelled noise not yet calibrated on the lab's instruments. Station times, fees and schedules, the stock on the shelf, the atomizer's failure rate and yield, and who staffs the lab are assumptions. It shows how the lab's design and its optimizer interact in a model, not what the real lab will find. |

### DAL's audit, and what the narrated cut takes from it

DAL audited the first cut's claims while this was being written
([digital-alloy-lab PR 293](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/293),
`audits/twin-round2-video/README.md`). Its verdict: the arithmetic reproduces, but the two headline factors are not a
measure of what automation does, and the takeaway's "84 %" means two different things. The narrated cut follows its
suggested rewording (§4), in the voice and on screen:

- **The takeaway card and the description's two bullets** (§4, first item). The narrated card says what was compared:
  "a stocked automated lab reached an alloy better than the reference alloy sooner than a conventional lab that orders
  metal as it goes", aluminium in 116 days against 220 (1.9×, 95 % CI 1.1 to 3.4) and copper in 225 days against at
  least 840 (≥ 3.7×; the conventional lab got there in 6 of 12 three-year runs). It adds "both labs ordering metal as
  they go: 1.2× (0.7 to 1.7)" for aluminium, and that copper's automated lab also screens powder blends first. Voice:
  `take1`, `take1b`, `res2`. The results' ratio panel shows "≥ 3.7x" and "at least 840 d (6 of 12 runs got there)".
- **Cost** (§4). There is one basis for both campaigns, led by the one with the equipment: 2.0× and 1.15× the
  conventional lab's cost, and 0.6× and 0.4× counting only the campaigns' spending. The voice adds "with the equipment,
  it costs less only for copper, and only if outside users rent its idle hours, which this model assumes and does not
  show". This replaces the card's "84 %", which meant operating cost with outside users for aluminium and operating
  cost without the equipment for copper. Voice: `take2`, and `res3` ("only if outside users fill it to sixty percent,
  which the model assumes").
- **"State of the art"** (§4). The target is "the best reference alloy's score on the twin's synthetic alloy model. One
  random design in 12 beats it, so reaching it shows how fast a lab tests its first alloys, not a discovery". This is in
  the explainer's target caption and the takeaway. Voice: `fig1`.
- **The heuristic line** (§4). "No faster on aluminium (1.05×, 0.7 to 2.2) at 2.6× the operating cost, and 2.2× faster
  on copper (1.7 to 2.6)", on the card and in the description. Voice: `take3`.
- **Copper in "Where BOFN doesn't win"** (§4). "0.68 against 0.58 over 24 seeds (0.69 against 0.67 in the first 12);
  plain BOFN did no better than random (0.33 against 0.35)", in the results caption and the description. Voice: `res1`.
- **The replay** (§4). A badge for its whole length: "One seed of 12: here aluminium reaches the target on day 20; the
  median seed takes 116 days". Voice: `seed1`, which also says it is aluminium's luckiest seed (the audit's §1, row 9).
- **Run counts** (§4). "12 one-year automated and 12 three-year conventional runs per policy" replaces "twin-years" in
  the results caption, the ratio panels' footnotes and the takeaway's footer. Voice: `res1`.
- **The notes frame** (§4). "Assumed" gains "the automated lab's feedstock stock on day 0; the atomizer's failure rate and
  yield; who staffs the automated lab". "Every measurement, with noise" becomes "Every measurement, with modelled noise
  not yet calibrated on the lab's instruments". Voice: `note1`.
- **This file's account of the takeaway's comparison** (§4, last item). It is reworded in [The cut](#the-cut).
- Also from the audit's claims table, not its §4: the explainer's grey curve says the conventional lab orders its metal
  as it goes (rows 1 and 15; voice `fig2`). The acceleration factor's definition below now says how Rohr et al.'s
  differs (row 16). The narrated description drops "the same campaigns run the conventional way", and says the
  conventional lab is the proposals' plan (row 14).

Not taken: §5's experiments, which would settle the open claims rather than reword them (stocking the conventional lab,
the same copper method in both labs, more seeds, one horizon, the logged atomizer). They need new benchmark runs.

Every number those use is read from this commit's data: aluminium with both labs ordering as they go is recomputed with
`twin.accel` (as `econ_summary.json` computes the headline) from `bench2_summary.json`'s `stock` runs against the
conventional lab, 1.16 (0.73 to 1.67), against the audit's 1.16 (0.72 to 1.66) from 20,000 resamples. Copper over 24
seeds is `main` plus `cu_seeds`, and "one random design in 12" is `oracle.json`'s `frac_above_sota` (0.082, both spaces).
Where the audit's own bootstrap and `econ_summary.json` differ in the last digit, the video uses `econ_summary.json`:
copper against the heuristic is 2.2× (1.7 to 2.6) there, 1.8 to 2.6 in the audit.
