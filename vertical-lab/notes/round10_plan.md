# Round 10: how the work is split (PR #318 comment of 2026-11-07 03:36 UTC)

The shared brief for round 10's sub-agents, committed so a follow-up session can see who owned what. Round 9's brief
(`notes/round9_plan.md`) still describes the code layout and the rules; this file overrides it where they differ.

## Sterling's points (2026-11-07)

1. "How goes it? Did you finish? You probably still have a lot to do if you carefully comb through all my feedback
   here and do some careful thinking, considering that this is meant to help us simulate as realistically as possible
   in order to make things more seamless in an actual implementation." -> the orchestrator's ledger of every point
   (`notes/feedback_ledger.md`), and the streams below for what it finds open.
2. "Open a separate PR focused on finding (using the Pi) all the contact information, specs, requests, etc. for the
   individual parts that go into this entire workflow. Include specific emails and answer the typical questions people
   would be asking us in order for them to give a budgetary quote or answer certain questions." -> vendors-a/b/c, on
   their own branch `claude/issue-303-vendors-rfq` (worktree `/tmp/wt-vendors`), stacked on this one.
3. "Something that's been on my mind is maintenance over long-term and how that gets handled in workflows." ->
   upkeep-model and upkeep-clip.
4. "Did you get latest multi-doser with the scale? Note the comment about raising the cup on a platform of sorts so
   that the nozzle is closer, but we might end up needing to use a funnel anyway." -> doser. powder-doser PR #185's
   head is still `353dae7` (v5, the HR-202i under the dose point), which round 9 vendored. The comment is
   Sterling's of 2026-11-05 17:52 on that PR: "if we have a shorter scale or want to get it closer to the dispense
   point, we just raise the scale up on some kind of block (e.g., granite block)".

## Streams

| Stream | Display | Owns | Renders (priority) |
|---|---|---|---|
| doser | 41 | `carousel.py`, `animate.py`, `alloy_charge.py`, `charge.py`, `notes/multidoser.md`, `notes/alloy_charge.md`, new `r10_doser*.py`; `vlm.COLUMNS` spans only if a slot must grow (say so in your report) | ch1 `alloy_charge` (2), 8:37 `animate.py workflow` (5) |
| prep | 42 | `alloy_prep.py`, `r8_prep.py`, `r8_specimens.py`, `notes/alloy_prep.md` | ch6 `alloy_prep` (1) |
| checks | 43 | `alloy_powder.py`, `r8_powder.py`, `r8_powder_data.py`, `alloy_characterize.py`, `r8_char.py`, `alloy_print.py`, `sieve_station.py`, `alloy_workflow.py` (audit fixes only), `alloy_models.py` (only `Aconity(zbars=...)` use), their notes; may copy #321's `audit_mir.py` | ch4 `alloy_powder` (3); ch7, ch3 only if a slot is free after 06:30 |
| lab | 44 | `setup_lab.py`, `services.py`, `reach.py`, `kardex_tall.py`, `notes/services.md`, `notes/tray_plan.md`, `notes/lab_r8.md` | `services.py hookups baycam` (4), `setup_lab.py` (4, after 05:15), `services.py services cabling` (6) |
| upkeep-model | 45 | `timelapse.py`, new `upkeep.py`, `notes/upkeep.md` (new), `notes/timelapse.md`, `out/upkeep*`, `out/timelapse*` | the finale `timelapse.py` (4, after 06:00) |
| upkeep-clip | 46 | new `upkeep_clip.py`, `notes/upkeep_clip.md`, `out/upkeep_clip*`, `out/mp4/upkeep_clip.mp4` | the new maintenance clip (3) |
| repowder | 47 | its own worktree `/tmp/wt-repowder` on `claude/issue-303-repowder-model` (PR #327): `repowder/`, `instruments_repowder.py`, `refs/repowder/`, `notes/repowder_refine.md` | stills only |
| vendors-a, -b, -c | none | `/tmp/wt-vendors`, `vertical-lab/procurement/` only, each its own files | none |
| orchestrator | | `vlm.py`, `runner_guard.py`, `longform.py`, `alloy_route.py`, `README.md`, `youtube_upload.py`, `tour.py`'s module list, `notes/feedback_ledger.md`, this file | the long-form join |

Lower number = more important. When slots are short, the lowest-priority render waits or is dropped.

## Rules (round 9's, with these changes)

- **One working tree** (`/home/runner/work/byu-vcl/byu-vcl`) for every stream except repowder and vendors. Edit only
  the files you own. Shared modules (`robot.py`, `collide.py`, `props.py`, `animate.py` for non-doser streams,
  `setup_lab.py` for non-lab streams, `services.py`, `route_dag.py`, `tour.py`, `data_panels.py`): additive changes
  only, and say so in your report. Never edit `instruments.py`, `lab.py`, `lab_models/common.py`, `openflexure.py`,
  `scene.py` (every tour cache hashes them).
- **Git.** `git add <your files>` then `git commit`. Never `git add -A`, `git add .`, `git commit -a`, `git stash`,
  `git checkout`, `git reset`, `git rebase`, `git merge` or `git push`. If `.git/index.lock` exists, wait a few
  seconds and retry. Commit after every piece that works and at least every 30 minutes. Message:
  `vertical-lab: <what changed> (#303)`, a blank line, then
  `Co-authored-by: Sterling G. Baird <45469701+sgbaird@users.noreply.github.com>` and
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. The orchestrator pushes about every 15 minutes.
- **Rendering on 4 cores and 16 GB: at most 3 scene jobs at once, all through `runner_guard.py`.** A render, a
  `PREVIEW=1` still, an `ARM_AUDIT=1` pass, a tour clip, `interference.py` each take a slot.
  - Long jobs: `python3 runner_guard.py bg --log /tmp/<stream>_<job>.log --mem <MB> --label <stream>-<job> -- env VIZ3D_FPS=6 ... xvfb-run --server-num=<display> -a python3 <script>`,
    then `python3 runner_guard.py wait <pid> --minutes 50 --log <log>` (repeat while it runs).
  - Short ones: `python3 runner_guard.py slot --quick --mem <MB> --label ... -- ...`.
  - `--mem 6500` for the whole two-Shuttle floor, 3000-4000 for a tour clip or a chapter built with `VLAB_ONLY_TRAYS`.
  - New this round: a waiter held up only by memory no longer blocks smaller jobs behind it (backfill), and
    `runner_guard.py status` lists the waiters.
  - Chapters at `VIZ3D_FPS=6`, 1280 × 720. Preview first, then `ARM_AUDIT=1` (target 0 frames in collision), then the
    render. A queued render runs the code on disk when its slot comes up.
  - Never kill another stream's job.
- **Deadlines (UTC, 2026-11-07; the job ends at 09:37).**
  - Geometry that shows in the whole-lab scenes (tray B's station, anything on a tray or the floor) committed by
    **05:15**, so the set-up movie and the finale pick it up. Write `/tmp/r10_<stream>_geometry_done` when it is.
  - Code and a `PREVIEW=1` still committed by **05:45**. Final renders queued by **06:15** at the latest.
  - Renders committed by **08:05**: then the orchestrator builds the long-form from what is committed, and an older
    clip stays where a new one is missing. Notes by **08:15**. Report back by **08:20**.
- **Jars, lab-wide** (round 9): clear glass, a matte black cap; a tint and a legend for a few seconds where something
  is pointed out, then back.
- **The Pi** (stream-cam Pi, `RPI_STREAM_CAM_USERNAME@RPI_STREAM_CAM_HOSTNAME` over Tailscale SSH, already in
  known_hosts) is a live device carrying a stream: single frames, single pages, one fetch at a time, `curl
  --limit-rate 300k`; nothing left on its disk. Never print its hostname or any credential.
- **GitHub reads** (powder-doser, digital-alloy-lab, robot-arms, ac-dev-lab):
  `GH_TOKEN=$(cat /tmp/.ghtok 2>/dev/null || echo $GH_TOKEN) gh api ...`. Never print a token or any secret.
- **Notes.** Each stream updates its own `notes/*.md`: what changed and why, sources as links, estimates marked.
  Don't edit `README.md`.
- **Realism first.** Sterling: the point is "to simulate as realistically as possible in order to make things more
  seamless in an actual implementation". Where you assume, say so; where a real machine would do something
  differently from the model, fix the model or write it down.
- **Report back** in under 350 words: what changed, files and commits, renders (duration, frames in collision),
  sources, what is still open.
