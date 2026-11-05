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
