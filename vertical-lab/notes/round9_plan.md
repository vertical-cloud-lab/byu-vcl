# Round 9: how the work is split (PR #318 comment of 2026-11-05 22:56 UTC)

The shared brief for the round-9 sub-agents, committed so a follow-up session can see who owned what. Round 8's
brief (`notes/round8_plan.md`) still describes the code layout; this file overrides it where they differ.

## Sterling's points, and the stream that takes each

| # | Point (PR #318, 2026-11-05 22:56) | Stream |
|---|---|---|
| 1 | The multi-doser is now chain carousel v5 (powder-doser PR #185 at `353dae7`): the A&D HR-202i under the dose point, no funnel, dose falls 154 mm. Change it everywhere it appears, vial dosing and charge-cup dosing | doser |
| 2 | 8:37 (`vlm_workflow`, 41 s): the vial lies on its side, 90° off, during the dose | doser |
| 3 | The CubXL capper's magnet holds one cap at a time: where does the other cap go? A parking spot, or an empty vial kept only to park a cap, checked for interference | cubxl |
| 4 | Technicolor jars: every jar clear glass with a black lid. To point something out, a legend and a colour change that reverts | jars (+ every stream for its own jars) |
| 5 | The bay has no bottom under the tray: a real VLM has the access table there | orchestrator: done, `vlm.py` "access table" (`6e10de7`) |
| 6 | Both mobile manipulators to open the atomizer's chamber; bases heavy enough with a low centre of gravity | atomize |
| 6b | A PR to refine the rePowder model against the training and run videos (hinges, clamps) | repowder-pr (own branch) |
| 7 | Sieve-stack cleaning: the depowdering module plus ultrasonic IPA rinses? | print |
| 8 | Which containers for powder: is glass OK? | orchestrator (answer) |
| 9 | The Aconity MIDI's door swings the wrong way | tensile (owns `alloy_models.py`), print picks it up |
| 10 | Mastersizer: the view and the stacked transparency hide the laser | powder |
| 11 | 27:13 (chapter 4, 195 s, the S2 PUMA): see-through only once the cup is nearly loaded, so the internal transfer isn't seen | powder |
| 12 | 28:08 (chapter 5, 25 s): the suction lance goes into the machine | tensile |
| 13 | How does the depowdering box hold the plate? | tensile |
| 14 | Tensile bars at different build orientations through the automated EDM; and a PR focused on that | tensile (+ orchestrator opens the PR) |
| 15 | 32:20 (chapter 5, 277 s): the angle and transparency hide the tensile test; something odd with the heated chamber | tensile |
| 16 | The polishing holder doesn't hold the mount: no set screw; the machine's piston presses it down, and with the piston up it just stands in its hole | prep |

## Shared rules (as round 8, with these changes)

- **One working tree.** Everyone works in `vertical-lab/` on `claude/issue-303-20261103-1736`, except repowder-pr,
  which has its own worktree and branch. Edit only the files your stream owns. New files: prefix `r9_` or your
  stream's own names.
- **Git.** `git add <your files>` then `git commit`. Never `git add -A`, `git add .`, `git commit -a`, `git stash`,
  `git checkout`, `git reset`, `git rebase` or `git push`. If `index.lock` exists, wait and retry. The orchestrator
  pushes about every 15 minutes. Message: `vertical-lab: <what changed> (#303)`, a blank line, then
  `Co-authored-by: Sterling G. Baird <45469701+sgbaird@users.noreply.github.com>` and
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Never edit** `instruments.py`, `lab.py`, `lab_models/common.py`, `openflexure.py`, `scene.py`: every tour cache
  hashes them. To change a model there, copy its builder into your own module (`tour.MODULES`: a later module's
  `REGISTRY` key replaces an earlier one). `vlm.py` is the orchestrator's; doser may change only `COLUMNS` spans.
- **Shared modules** (`robot.py`, `collide.py`, `props.py`, `charge.py`, `animate.py`, `setup_lab.py`, `services.py`,
  `route_dag.py`, `tour.py`, `fab_tour.py`, `data_panels.py`): additive changes only, unless your stream owns the file.
- **Jars, lab-wide.** A powder jar is clear glass (light grey-blue, opacity about 0.3-0.4, so the powder shows) with
  a matte black lid. No per-jar lid colours. To point something out (which lot, which size cut, which powder), tint
  only those jars or their powder for a few seconds while a legend says what the tint means, then fade back.
- **Rendering on 4 cores and 16 GB, at most 3 heavy jobs at once.** Every 3-D job goes through `runner_guard.py`
  (its docstring has the rules): a render, a `PREVIEW=1` still, an `ARM_AUDIT=1` pass, a tour clip, `interference.py`.
  - Long jobs: `python3 runner_guard.py bg --log /tmp/<you>_<job>.log --mem <MB> --label <you>-<job> -- env ... xvfb-run --server-num=<display> -a python3 <script>`,
    then `python3 runner_guard.py wait <pid> --minutes 50 --log <log>` (repeat if it is still running).
  - Short ones (a preview): `python3 runner_guard.py slot --quick --mem <MB> --label ... -- ...`.
  - `--mem 6500` for anything on the whole two-Shuttle floor, 3000-4000 for a tour clip or a chapter built with
    `VLAB_ONLY_TRAYS`.
  - Chapters at `VIZ3D_FPS=6`, 1280 × 720; tour clips at 8. Preview first, audit (`ARM_AUDIT=1`, target 0 frames in
    collision), then render. A chapter render runs 40-70 min, so start yours as soon as the preview is right.
  - Never kill another stream's job. `python3 runner_guard.py status` shows the queue and memory.
- **Deadlines (UTC).** Code and a `PREVIEW=1` still committed by **01:30**. Final renders started by **02:15**
  at the latest. Renders committed by **03:30**: after that the orchestrator builds the long-form from what is
  committed, and an older clip stays where a new one is missing. Notes by **03:40**. If a render won't make it, commit
  the code and a still and say what is left.
- **No YouTube uploads** except the orchestrator's one long-form.
- **The Pi** (`frames.py`, `~/ytframes/` on the stream-cam Pi) is a live device carrying streams: single frames and
  storyboards only, never a whole video, one fetch at a time.
- **GitHub reads** (powder-doser, digital-alloy-lab): `GH_TOKEN=$(cat /tmp/.ghtok 2>/dev/null || echo $GH_TOKEN) gh api ...`;
  the orchestrator re-mints `/tmp/.ghtok` hourly. Never print a token or any secret.
- **Notes.** Each stream updates its own `notes/*.md`: what changed and why, sources as links, estimates marked.
  Don't edit `README.md`.
- **Report back** in under 300 words: what changed, files, rendered outputs (duration, frames in collision), sources,
  what is still open.

## Owners

| Stream | Display | Owns |
|---|---|---|
| doser | 21 | `carousel.py`, `multidoser/`, `animate.py`, `alloy_charge.py`, `charge.py`, `notes/alloy_charge.md`, `notes/multidoser.md` (new); `vlm.COLUMNS` spans; outputs `out/vlm_workflow*`, `out/alloy_charge*`, `out/mp4/vlm_workflow.mp4`, `out/mp4/alloy_charge.mp4` |
| cubxl | 22 | `cubxl_rig.py`, `r9_cubxl.py` (new; copy `instruments_lab.cubxl_corrosion` here rather than editing `instruments_lab.py`), `notes/cubxl_corrosion.md`, the `cubxl_corrosion` tour clip |
| jars | 23 | `r8_store.py`, `instruments_r7.py`, `instruments_lab.py` (packaging only), `notes/lab_r8.md` (append a round-9 section), the `storage`, `powder_store_feed`, `powder_store_lots`, `packaging` tour clips |
| atomize | 24 | `alloy_atomize.py`, `alloy_atomize_floor.py`, `notes/alloy_atomize.md`, `out/alloy_atomize*`, `out/footage/` |
| print | 25 | `alloy_print.py`, `sieve_station.py`, `notes/alloy_print.md`, `out/alloy_print*` |
| powder | 26 | `alloy_powder.py`, `r8_powder.py`, `r8_powder_data.py`, `notes/alloy_powder.md`, `out/alloy_powder*`, the `xrd`, `mastersizer`, `xrf` tour clips |
| tensile | 27 | `alloy_workflow.py`, `alloy_models.py`, `r8_test.py`, `notes/alloy_workflow.md`, `notes/edm_orientations.md` (new), `out/alloy_workflow*`, the `instron_*`, `furnace`, `wire_edm` tour clips |
| prep | 28 | `alloy_prep.py`, `r8_prep.py`, `r8_specimens.py`, `notes/alloy_prep.md`, `out/alloy_prep*`, the `polisher` tour clip |
| repowder-pr | 29 | its own branch `claude/issue-303-repowder-model`: `repowder/`, `notes/repowder_refine.md` |
| orchestrator | | `vlm.py`, `longform.py`, `alloy_route.py`, `README.md`, `youtube_upload.py`, `tour.py`'s module list, this file |

## Continuation 1 (run of 2026-11-06 03:14 UTC)

The first round-9 run stopped at 23:31 on 2026-11-05 when the account ran out of model credits. Its last push was
`dd65995` (23:17): the bay floor (`6e10de7`), this brief, and the lab-wide jar in `props.py` (`jar_style`,
`jar_meshes`/`jar_parts`, `tint_sleeve`, `TINT`/`tinted`/`pulse`, `draw_legend`/`use_legend`/`piece_legend`). Nothing
else from its sub-agents survived. No `claude/issue-303-repowder-model` branch was pushed. Everything above still
holds, except:

- **Deadlines (UTC, 2026-11-06).** The job ends at 09:14. Code and a `PREVIEW=1` still committed by **05:00**. Audit,
  then the final render started by **05:30** at the latest; earlier is better, since the three slots are the
  bottleneck. Renders committed by **07:35**: then the orchestrator builds the long-form from what is committed, and
  an older clip stays where a new one is missing. Notes by **07:45**. Report back by **07:50**.
- **Commit as you go,** at least every 30 minutes and after every piece that works. The last run lost everything its
  sub-agents hadn't committed.
- **Model credits.** Some streams run on a smaller model to spread the load. Keep tool output short (`| tail`,
  `| head`) and don't re-read long files you have already read.
- **Side branches.** repowder-pr and the EDM-orientation study each work in their own `git worktree` on their own
  branch, stacked on this one, so their PRs show only their own work. The orchestrator pushes those branches and opens
  the PRs.
- **05:15, deadlines moved.** Fourteen jobs were queued for three slots, about eight slot-hours of work, so renders
  are now due committed by **08:05**, notes by **08:10**, reports by **08:15**; the long-form is built at 08:05 from
  what is committed. A queued render runs the code on disk when its slot comes up, so an audit queued ahead of one's
  own render doesn't change it: audits go after the render, if there is time.
