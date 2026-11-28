# Round 11: how the work is split (PR #318 comment of 2026-11-13 23:35 UTC)

The shared brief for round 11's sub-agents, committed so a follow-up session can see who owned what. Round 10's
brief (`notes/round10_plan.md`) and round 9's (`notes/round9_plan.md`) still describe the code layout and the rules;
this file overrides them where they differ.

## Sterling's points (2026-11-13), mapped to the round-10 long-form (aW5YoxPi0pM, `out/longform.json`)

| # | Point | Where | Stream |
|---|---|---|---|
| 1 | "At 2:14, you show cameras by the jars and possibly a UPS at the back. That is very inefficient from a vertical space usage, since the jars are so short. Do we actually need cameras on the jars at all times? In terms of inventory, we're going to get that with the overhead camera in the bay anyway." | `setup_lab.mp4` 105 s: tray N (jar racks) loaded "with its UPS and 2 camera posts"; N sits in a 475 mm slot (2F0), O in 500 mm (2R5), for jars at most 170 mm tall | lab |
| 2 | "Can't see the overhead camera from the angle. Should change the view angle and temporarily make things opaque again" | `setup_lab.mp4` 106-112 s, "The bay cameras go on, one over each opening": shot through see-through cladding from far off | lab |
| 3 | "Why isn't it the CubXL showing the corrosion workflow? Why is it the OT-2? Ah, I see. Not sure if it's necessary to try to split between the CubXL and OT-2, but fine for now." | 5:33 | orchestrator (answer only) |
| 4 | "at 32:57 the arm passing through the camera / collision" (a screenshot: the gripper and the tongs through a camera post) | `alloy_workflow.mp4` 242 s: the quench, the tongs and rack pass camera F1's post by the quench tank | ch5 |
| 5 | "Insertion / removal of the tensile bars (and the halves) have another collision. Not sure if the gripper has enough clearance. Maybe OK if angled, otherwise needs its own tool/end effector." | `alloy_workflow.py` `test_one()` | ch5 |
| 6 | "That's kind of a cringy looking human, although I don't totally dislike the idea of showing an actual person with movement." | `upkeep_clip.py` `Person` (also used by `timelapse.py`) | upkeep |
| 7 | "Also, maintenance step shows a collision. There are probably other collisions and interferences that I didn't catch from this" | `upkeep_clip.mp4`; every arm clip in the long-form | upkeep; audit-a, audit-b |

Why the audits missed 4, 5 and 7: chapter 5's final render was never audited frame by frame (round 9 stopped that
audit to free a slot; round 10 didn't rerun it). And `collide.Auditor` checks only the arms: not the person, a tray
pulled out onto a table, the MiR bodies, or anything else that moves. Its rules also let the gripper touch a part's
source and destination fixtures for 4 s around each grasp and release, however deep: fingers sunk into a grip's jaws
count as "allowed".

## Streams

| Stream | Display | Owns | Renders (priority, 1 = first) |
|---|---|---|---|
| lab | 44 | `setup_lab.py`, `r8_store.py`, `services.py` (except `TRAY_CAMS["F"]`), `vlm.COLUMNS` and the slot spans, `kardex_tall.py`, `instruments_r7.py`'s `storage` only, `notes/tray_plan.md`, `notes/lab_r8.md`, `notes/services.md`, `out/tray_plan*`, `out/setup_lab*`, `out/powder_store*` | set-up (2, `--mem 6500`); tour clips `powder_store_feed`, `powder_store_lots`, `storage` if their racks change (6) |
| ch5 | 42 | `alloy_workflow.py`, `r8_test.py`, `r8_specimens.py`, `alloy_models.py` (tongs, comb, cradles), `services.TRAY_CAMS["F"]` only, `notes/alloy_workflow.md`, `out/alloy_workflow*`, `out/collisions/alloy_workflow*`; additive changes to `ur_arm.py`/`robot.py` for a fingertip set or tool | chapter 5 (1) |
| upkeep | 45 | `upkeep_clip.py`, `timelapse.py`, new `people.py`, `notes/upkeep_clip.md`, `notes/timelapse.md`, `out/upkeep_clip*`, `out/timelapse*` | the maintenance clip (1), the finale (3, `--mem 6500`) |
| audit-a | 43 | `collide.py` (the stricter rules and the movers check: additive, but they become the default), new `audit_all.py`, `interference.py`, `out/interference*`, `notes/arm_collisions.md`, `notes/interference.md`; fixes in `alloy_charge.py`, `charge.py`, `alloy_atomize.py`, `alloy_atomize_floor.py`, `animate.py` (the 8:00 clip), `scaleup.py`, `r8_scale.py` and their notes | chapters 1, 2 and the 8:00 clip only if their audit finds something (4) |
| audit-b | 46 | fixes in `alloy_print.py`, `sieve_station.py`, `alloy_powder.py`, `r8_powder.py`, `alloy_prep.py`, `r8_prep.py`, `alloy_characterize.py`, `r8_char.py` and their notes, `out/collisions/` for those clips | chapters 3 and 7 (their round-10 fixes were never rendered) (4); 4 and 6 only if their audit finds something (5) |
| orchestrator | 40, 41 | `vlm.py` outside `COLUMNS`, `runner_guard.py`, `longform.py`, `alloy_route.py`, `README.md`, `youtube_upload.py`, `notes/feedback_ledger.md`, this file | the long-form join |

## Rules (round 10's, with these changes)

- **One working tree** (`/home/runner/work/byu-vcl/byu-vcl`, branch `claude/issue-303-20261103-1736`). Edit only the
  files you own. Shared modules (`robot.py`, `collide.py` for streams other than audit-a, `props.py`, `animate.py`,
  `setup_lab.py` for streams other than lab, `services.py`, `tour.py`, `data_panels.py`): additive changes only, and
  say so in your report. Never edit `instruments.py`, `lab.py`, `lab_models/common.py`, `openflexure.py`, `scene.py`
  (every tour cache hashes them).
- **Git.** `git add <your files>` then `git commit`. Never `git add -A`, `git add .`, `git commit -a`, `git stash`,
  `git checkout`, `git reset`, `git rebase`, `git merge` or `git push`. Never add `CLAUDE.md` (the workflow edits it).
  If `.git/index.lock` exists, wait a few seconds and retry. Commit after every piece that works and at least every
  30 minutes. Message: `vertical-lab: <what changed> (#303)`, a blank line, then
  `Co-authored-by: Sterling G. Baird <45469701+sgbaird@users.noreply.github.com>` and
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. The orchestrator pushes about every 15 minutes.
- **Rendering on 4 cores and 16 GB: at most 3 scene jobs at once, all through `runner_guard.py`** (its watchdog is
  running). A render, a `PREVIEW=1` still, an `ARM_AUDIT=1` pass, a tour clip and `interference.py` each take a slot.
  - Long jobs: `python3 runner_guard.py bg --log /tmp/<stream>_<job>.log --mem <MB> --label <stream>-<job> -- env VIZ3D_FPS=6 ... xvfb-run --server-num=<display> -a python3 <script>`,
    then `python3 runner_guard.py wait <pid> --minutes 50 --log <log>` (repeat while it runs).
  - Short ones: `python3 runner_guard.py slot --quick --mem <MB> --label ... -- ...`.
  - `--mem 6500` for the whole two-Shuttle floor, 3000-4000 for a tour clip or a chapter built with `VLAB_ONLY_TRAYS`.
  - Chapters at `VIZ3D_FPS=6`, 1280 × 720. Preview first, then `ARM_AUDIT=1` (target 0 frames in collision under the
    stricter rules), then the render. A queued render runs the code on disk when its slot comes up.
  - The caches in `.cache/` start empty on this runner: the orchestrator is warming them with `setup_lab.py fit`
    (log `/tmp/warm_fit.log`). Don't start a second whole-lab build before that finishes.
  - Never kill another stream's job. `python3 runner_guard.py status` shows the queue and memory.
- **The stricter audit (audit-a, by 00:35 UTC).** `collide.py` gets, as the default for `ARM_AUDIT=1`:
  1. a depth limit on what is "allowed": the gripper or a held part may touch a part's source and destination
     fixtures around a grasp or release only up to about 1.5 mm of penetration (FCL contacts' depth), not without
     limit;
  2. a movers check: everything that moves in a frame and isn't an arm (MiR bodies, trays, doors, people, tables,
     carried parts) against everything else that is visible, excluding its own subtree and ancestors and the
     contacts it already had when it started moving.
  audit-a writes `/tmp/r11_strict_ready` when that is committed; every stream's final audit runs after it.
- **Deadlines (UTC, 2026-11-14; the job ends at 05:35).**
  - **00:40** geometry that shows in the whole-lab scenes committed (the jar trays and their slots, camera F1's
    post); write `/tmp/r11_<stream>_geometry_done`.
  - **01:30** code and a `PREVIEW=1` still committed for the points above; the renders of chapter 5, the maintenance
    clip and the set-up queued.
  - **02:45** every other final render queued. **03:15** a render that hasn't started is dropped: say so.
  - **04:15** renders committed. The orchestrator then builds the long-form from what is committed; an older clip
    stays where a new one is missing. **04:25** notes committed and your report back.
- **Realism first.** Sterling: the point is "to simulate as realistically as possible in order to make things more
  seamless in an actual implementation". Where you assume, say so; where a real machine would do something
  differently from the model, fix the model or write it down.
- **Report back** in under 350 words: what changed, files and commits, renders (duration, frames in collision),
  sources, what is still open.
