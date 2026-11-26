# The campaign video: a year of the twin, replayed

Round 2's video: the two campaigns' year in the vertical lab, replayed from the twin's own event log, with the figures
we track and what the benchmark found. **Everything in it is simulated**, except the lab design's 3-D renders (PR 318),
the lab's own atomizer footage and photos, the search spaces (the proposals) and the prices and their sources.

**On YouTube:** VIDEO_URL (public, subscribers not notified).

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
