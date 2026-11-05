# Round 8: how the work is split (PR #318 comment of 2026-11-05 00:37 UTC)

This file is the shared brief for the round-8 sub-agents. It is committed so a follow-up session can see how the work
was divided and what each stream owned.

## Shared rules

- **One working tree, eight agents.** Everyone works in `vertical-lab/` on branch `claude/issue-303-20261103-1736`.
  - Edit only the files your stream owns (below). New files are fine if their names start with your prefix.
  - Commit only your own files: `git add <file> ...` then `git commit`. Never `git add -A`, `git add .`,
    `git commit -a`, `git stash`, `git checkout`, `git reset` or `git rebase`. If `index.lock` exists, wait a few
    seconds and retry.
  - **Do not push.** The orchestrator pushes every 20 minutes or so.
  - Commit message: `vertical-lab: <what changed> (#303)`, then a blank line and the two trailers
    `Co-authored-by: Sterling G. Baird <45469701+sgbaird@users.noreply.github.com>` and
    `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Never edit `instruments.py`, `lab.py`, `lab_models/common.py`, `openflexure.py` or `scene.py`.** Every tour cache
  hashes the first four, so one edit makes every agent re-tessellate every model. To change a model that lives in
  `instruments.py` or `instruments_char.py`, copy its builder into your own `r8_*.py` module and change it there.
  `tour.MODULES` already lists `r8_prep`, `r8_char`, `r8_powder`, `r8_test`, `r8_store`, `r8_scale`, after the older
  modules, and `tour.load()` lets a later module's `REGISTRY` key replace an earlier one. So a `"sem"` in
  `r8_char.REGISTRY` becomes the SEM in every scene and tour clip.
- **Shared modules** (`robot.py`, `collide.py`, `props.py`, `charge.py`, `vlm.py`, `animate.py`, `setup_lab.py`,
  `services.py`, `route_dag.py`, `tour.py`, `fab_tour.py`): additive changes only (a new function, or a new keyword
  argument whose default keeps the old behaviour), unless your stream owns the file.
- **Tray and floor placements of new models.** If your module adds a model that belongs on a tray or on the floor,
  give the module `TRAY_PLACEMENT = {key: dict(tray="F", x=mm, y=mm or None, turn=deg)}` (the same convention as
  `setup_lab.ITEMS`) or `FLOOR_PLACEMENT = {key: dict(x=mm, y=mm, turn=deg)}` in `setup_lab`'s floor frame. The lab
  stream merges them into the set-up movie and the tray plan, and checks them with `setup_lab.py fit`.
- **Rendering.** The runner has 4 cores shared by eight agents.
  - Use your own X display: `xvfb-run --server-num=<yours> -a ...` (numbers below); if it is taken, add 20.
  - Check with `PREVIEW=1` stills first. Render chapters at `VIZ3D_FPS=8` (1280 × 720) unless told otherwise.
  - `ARM_AUDIT=1` before rendering any clip with arm moves. The target is 0 frames in collision; report what is left.
  - Keep each GIF under 4.9 MB (fewer frames or a smaller size).
- **Deadline.** All renders committed by **02:35 UTC**, notes committed by **02:45 UTC**. After that the orchestrator
  builds the one long-form video. If something won't make it, commit what works and write down what is left.
- **No YouTube uploads.** Sterling asked for one long video with chapters instead of many clips; the orchestrator
  uploads only that.
- **The Pi** (`frames.py`, `~/ytframes/grab.py` on the stream-cam Pi): only the prep, tensile and atomize streams use
  it, for storyboards, single frames and short excerpts. Never download a whole video. It carries live streams.
- **Notes.** Each stream writes `notes/<stream>.md`: what changed and why, every source as a link, estimates marked as
  estimates. Don't edit `README.md`; the orchestrator writes the round-8 section from your notes and report.
- **Secrets.** Never print, echo or grep environment secrets.
- **Report back** in under 300 words: what changed, files, rendered outputs (with durations and frames in
  collision), sources, and what is still open.

## The alloy route after round 8

| # | Chapter | Script | Stream |
|---|---|---|---|
| 1 | The charge cups | `alloy_charge.py` | (unchanged) |
| 2 | Melt and atomize | `alloy_atomize.py` | atomize |
| 3 | Sieve and print | `alloy_print.py` | atomize |
| 4 | The powder, checked (XRD with its prep, laser diffraction, XRF, SEM) | `alloy_powder.py` (new) | powder |
| 5 | Depowder, cut, heat treat, tensile at room and elevated temperature | `alloy_workflow.py` | tensile |
| 6 | Sample prep: section, mount, grind and polish | `alloy_prep.py` (new) | prep |
| 7 | Characterizing the build | `alloy_characterize.py` | char |
| | Scaling up: large-format printing and ship-part repair | `scaleup.py` (new) | scale |
| | Finale: the lab at speed, hour, day, week, month | `timelapse.py` (new) | timelapse |

## The specimens that pass from prep to characterization

The prep stream owns `r8_specimens.py` and commits a first version early. Others import it and never edit it.

- **Conductive hot mount**: 1.25 in (31.75 mm) across, 20 mm tall, carbon-filled conductive phenolic, the coupon's
  polished face flush on top. The filler gives the SEM its path to ground. For the micrographs, the SEM/EDS and
  micro-Vickers hardness.
- **Steel mount for the mechanical tests**: a 31.75 mm steel puck with a pocket. The wire-EDM slice (about
  10 × 10 × 6 mm), ground flat and parallel on both faces, sits on steel, not polymer, and is polished flush. For
  nanoindentation and PIP, where a soft mount under the sample would add compliance.

## Owners

| Stream | Display | Owns |
|---|---|---|
| prep | 11 | `alloy_prep.py`, `r8_prep.py`, `r8_specimens.py`, `notes/alloy_prep.md`, `out/alloy_prep*`, the `polisher`, `mount_press` and `cnc` tour clips |
| char | 12 | `alloy_characterize.py`, `r8_char.py`, `data_panels.py`, `notes/alloy_characterize.md`, `out/alloy_characterize*`, the `sem`, `vhx`, `nanoindenter`, `pip`, `hardness` tour clips |
| powder | 13 | `alloy_powder.py`, `r8_powder.py`, `notes/alloy_powder.md`, `out/alloy_powder*`, the `xrd`, `mastersizer`, `xrf` tour clips |
| tensile | 14 | `alloy_workflow.py`, `alloy_models.py`, `r8_test.py`, `notes/alloy_workflow.md`, `out/alloy_workflow*`, the `instron_*`, `furnace`, `wire_edm` tour clips |
| atomize | 15 | `alloy_atomize.py`, `alloy_print.py`, `sieve_station.py`, `out/footage/`, `notes/alloy_atomize.md`, `notes/alloy_print.md`, `out/alloy_atomize*`, `out/alloy_print*` |
| lab | 16 | `animate.py`, `services.py`, `setup_lab.py`, `instruments_r7.py`, `r8_store.py`, `kardex_tall.py`, `notes/services.md`, `notes/tray_plan.md`, `notes/lab_r8.md`, those scripts' outputs |
| scale | 17 | `scaleup.py`, `r8_scale.py`, `notes/scaleup.md`, `out/scaleup*` |
| timelapse | 18 | `timelapse.py`, `notes/timelapse.md`, `out/timelapse*` |
| orchestrator | | `longform.py`, `alloy_route.py`, `route_dag.py`, `README.md`, `youtube_upload.py`, `tour.py`'s module list, `out/edison/`, `notes/edison_r8.md` |

## Continuation, 2026-11-05 03:25 UTC (PR #318 comment "pick up from where you left off")

The first round-8 session's GitHub token expired 60 minutes in, so nothing it committed after **01:26 UTC**
(`4eac506`) was pushed, and the runner took it with it. What is on the branch from round 8 is listed under "Landed"
below; everything else starts again from there. This session re-mints the token every 40 minutes and the
orchestrator pushes every 15 minutes or so, so **commit early and often**: code as soon as a preview works, then each
render as it finishes. An unpushed commit is lost if the job ends.

**Deadlines (UTC).** Renders committed by **05:05**. Notes by **05:15**. After 05:05 the orchestrator builds the
long-form from whatever is committed; a clip that isn't there is left out, and an older version stays in its place.
If a render won't make it, commit the code and a `PREVIEW=1` still, and say what is left in your notes.

**Rendering, 4 cores for everyone.** Chapters at `VIZ3D_FPS=6` (1280 x 720), tour clips at 8. Prefix renders with
`LP_NUM_THREADS=2 nice -n 5`. Use your display number below. `ARM_AUDIT=1` before any render with arm moves; the
target is 0 frames in collision.

**Reading DAL and other repos.** `GH_TOKEN=$(cat /tmp/.ghtok) gh api repos/vertical-cloud-lab/digital-alloy-lab/...`
(the file is re-minted every 40 minutes; read it fresh on every call).

### Landed in the first session

- powder: `r8_powder.py` (MiniFlex with a see-through door and still goniometer, zero-background holder; Mastersizer
  optical bench for a cutaway; S2 PUMA grabber, port and chamber), `r8_powder_data.py` (c3k0n5 SEM count, computed
  XRD and LD, illustrative XRF) and its PNGs, the `xrd`, `mastersizer`, `xrf` tour clips at 8 fps.
  **Left:** `alloy_powder.py` (chapter 4) and `notes/alloy_powder.md`.
- scale: `r8_scale.py`, `scaleup.py`, `notes/scaleup.md` (draft). **Left:** preview, render `out/mp4/scaleup.mp4`,
  finish the notes.
- lab: `r8_store.py` (581 jars, trays N and O; fume hoods with Weck's reagent), the hood and jar-store clips,
  `setup_lab.py` merging the r8 placements and dropping the OpenFlexure array, `services.py` media colours muted and
  flow slowed (code only), `kardex_tall` Modula table. **Left:** the services clips re-rendered with the muted flow,
  `animate.py workflow` (the 9:09 clip) re-staged in the two-Shuttle lab, the set-up movie and tray plan with every
  r8 model, `notes/lab_r8.md`.
- atomize: chapter 2's footage list (the Oct 8 drip out, the MS&T 2026 stream in: `out/footage/manifest.json`,
  `mst2026_stream.mp4`). **Left:** everything else in its row of the table below.
- prep: `r8_specimens.py` (1.5 in mounts). **Left:** everything else.
- char, tensile, timelapse: nothing landed.
- orchestrator: Edison answers, DAG cards for seven chapters, `longform.py` round-8 chapter list, `alloy_route.py`.

## Continuation 2, 2026-11-05 15:50 UTC (PR #318 comment "pick up round 8, at most 3 renders at once")

Both earlier round-8 runs lost their runner to a shutdown signal (exit 143), with eight agents rendering at once on
4 cores and 16 GB, not to the token. This run has 6 hours (the job's limit is now 360 minutes) and these rules:

- **At most 3 scene jobs at once, enforced.** Every job that builds a 3-D scene (a render, a `PREVIEW=1` still, an
  `ARM_AUDIT=1` pass, a tour clip, `interference.py`) and every long ffmpeg join goes through `runner_guard.py`:
  `python3 runner_guard.py slot [--weight N] --label "<stream>: <what>" -- xvfb-run --server-num=<yours> -a python3 ...`.
  Weight 2 for the whole-lab scenes (`setup_lab.py`, `animate.py workflow`, `timelapse.py`), 1 for the rest. A job
  waits until its slots are free and there is memory for it. `runner_guard.py watch` logs memory every minute to
  `/tmp/vlab_memlog.txt` and stops the biggest slotted job if memory runs out (you'll see rc -15 / 143: just retry).
  `python3 runner_guard.py status` shows who holds the slots.
- **Long renders outlive your shell:** `pid=$(VIZ3D_FPS=6 python3 runner_guard.py bg --log /tmp/<stream>/<clip>.log
  --label "<stream>: <clip>" -- xvfb-run --server-num=<yours> -a python3 <script>.py)`, then
  `python3 runner_guard.py wait $pid --minutes 50 --log /tmp/<stream>/<clip>.log` as one foreground call with a
  long timeout (repeat it while it says STILL RUNNING). Never `sleep` in the shell.
- **The orchestrator pushes every 10 minutes and re-mints the token every 40.** Commit as each piece lands (code
  once a preview works, each render as it finishes). Don't push.
- **Frames per second:** chapters at `VIZ3D_FPS=6`, tour clips at 8, unless the stream says otherwise. GIFs under
  4.9 MB.
- **Deadlines (UTC).** Renders committed by **19:45**. Notes by **19:55**. The orchestrator builds the long-form from
  20:00 with whatever is committed.
- **Physical sense.** Sterling asked whether there are other things like the bars dropping onto a catch shelf they'd
  bounce off. Every stream checks its own clips for parts that drop, float, teleport, hang unsupported or pass
  through something, fixes what it can, and lists the rest in its notes.
- From other PRs: the lab's SEM/EDS polishing SOP is on PR #258 (`SOP/sem-eds-polishing-sop.md` on
  `claude/issue-110-20261005-1730`; step 7 is now 0.1 um diamond on the VibroMet 2). PRs #320 and #321 have no
  commits after the ones `longform.py` already pins (`5a39245`, `a34367a`), except #320's set-up re-render with trays
  G-I in one 4450 mm Shuttle, which round 7's two-Shuttle set-up replaced.

| Stream | Display | This run |
|---|---|---|
| atomize + scale | 15, 17 | render chapters 2 and 3 (code and audits done); preview and render `scaleup.py` |
| powder | 13 | write `alloy_powder.py` (chapter 4), audit, render, notes |
| tensile | 14 | rework `alloy_workflow.py` (chapter 5), audit, render; `furnace`, `wire_edm`, `instron_*` clips; notes |
| prep | 11 | preview, audit and render `alloy_prep.py` (chapter 6); `polisher`, `mount_press`, `cnc` clips; notes |
| char | 12 | rework `alloy_characterize.py` (chapter 7), audit, render; `sem`, `vhx`, `nanoindenter`, `pip`, `hardness` clips; notes |
| lab | 16 | render `animate.py workflow` and the set-up movie with every r8 model, the tray plan; `notes/lab_r8.md` |
| timelapse | 18 | write `timelapse.py` (the finale), its throughput model, render, notes |
| orchestrator | | `runner_guard.py`, pushes, the token, `longform.py`, `alloy_route.py`, README, the PR description, the one upload |

**16:45 change:** every scene job takes one slot (`--weight 1`, the default). A whole-lab scene gives `--mem 6000`
instead of `--weight 2`: weight 2 had a single-threaded whole-lab audit holding two slots for 25 minutes while three
cores and a slot sat idle behind it. Still at most 3 scene jobs at once; the memory gate and the watchdog keep the
whole-lab jobs (about 5 GB each) from running the runner out of memory.

**17:12 change:** at 17:09 two whole-lab jobs (the 9:09 clip's render, 5.7 GB, and the set-up's preview, 4.8 GB), a
chapter-6 preview (3.4 GB) and a GIF assembled in Python outside any slot took the runner to 868 MB free, and the
watchdog stopped the 9:09 render, as designed. The gate now reserves memory: a job starts only if the free memory,
less what the running jobs may still grow into (each one's `--mem` less what it already holds), covers its own `--mem`.
Declare `--mem 6500` for a whole-lab scene, leave the 3000 default for the rest, and build GIFs and other
frame-hungry post-processing inside a slot too (or stream the frames from disk through ffmpeg, not a Python list).

**17:30 change:** `--quick` for a job of a few minutes (a `PREVIEW=1` still, a tour still): it goes ahead of normal
jobs in the queue. A normal job that has waited 20 minutes counts as quick, so renders still get their turn.

**17:40 deadlines moved:** renders committed by **20:10**, notes by **20:15**; the long-form is built from 20:15
(most of its clips are already in the cache). Two whole-floor scenes at about 5.5 GB each fill the runner's memory,
so only two run at once; set-up movie last among them.
