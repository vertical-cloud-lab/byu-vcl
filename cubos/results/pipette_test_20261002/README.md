# pipette_test_20261002: two attempts, neither ran the protocol

⛔ **Both attempts were stopped by Ben, and rightly.** The deck file they used
(attached to issue #169 at 19:35Z) was one Ben had edited but not saved. He said
so at 19:43:42Z, unplugged the gantry, and sent corrected files at 19:54:54Z. The
corrected files went to a new session (Actions run 37057200933). This session
(run 37055099634) never re-read the issue. It took the unplug for a USB fault and
started a retry with the stale deck file. Ben stopped that retry with the E-stop.

The corrected deck moves both vials **+21.668 mm in X** (115 → 136.668) and
−0.08 mm in Y. It also moves the tip rack's A1 to (291.332, 89) and `pickup_z`
62 → 59. The retry was heading for the stale vial_1, so its decap engage would
have landed about 22 mm off the real vial.

## Timeline (UTC; lab = UTC−6)

| UTC | |
|---|---|
| 19:35:20 | Ben attaches `ben_2vials_tiprack.yaml` + `cub_xl_ben_3_instrument.yaml` and asks for `pipette_test` |
| 19:41:13 | `checks/`: `--checks-only` passes everything, nothing moves |
| 19:42:49 | **attempt 1** starts (`attempt1_unplugged/`) |
| 19:42:59.236 | kernel: the GRBL CH340 (`ttyUSB0`) disconnects. **This was Ben unplugging the gantry.** It happened 0.32 s into the connect-time plunger `HOME`, which is a coincidence |
| 19:43:02 | step 0 `home` fails: `write failed: [Errno 5] Input/output error`. **0 G-code sent** |
| 19:43:42 | Ben: *"I just unplugged the gantry from the Pi. I realized the deck file I edited didn't save the changes."* |
| 19:54:10 | the CH340 re-enumerates (Ben plugs it back in) |
| 19:54:54 | Ben attaches corrected files: *"Stop the previous run if need be."* A new session starts |
| 19:58:23 | **attempt 2** starts (`attempt2_estopped/`) with the **stale** deck file. All checks and gates pass |
| 19:58:37–45 | step 0 `home` ✅ |
| 19:58:45–55 | step 1 `move`: capper to `park_position`, gantry (206, 25, 99) ✅ |
| 19:58:55–58 | step 2 `decap vial_1`: `Z122`, `X115`, `Y45.08` complete |
| 19:58:58.287 | `G01 Z99.0` sent. **GRBL goes silent: Ben's E-stop.** No USB event. CubOS only polls status after this |
| 19:59:07 | the new session writes `~/cubxl_runs/HOLD`: this session must start no more runs |
| 19:59:51 | Ben: *"The protocol ran with the first set of files I gave, so I used the E-stop"* |
| ~19:59:50 | first kill attempt misses (see below) |
| 20:00:07 | runner process group and CubOS child SIGKILLed |
| 20:01:33 | Tic de-energized by hand (SIGKILL skipped the runner's cleanup) |

## How the machine was left (20:02Z)

| | |
|---|---|
| head | last known gantry (115, 45.08, 122), moving down to Z 99 above the *stale* vial_1 position when the E-stop hit. Actual Z unknown. **No tip** (step 3 never ran) |
| electromagnet | never switched on (decap never reached its engage). No cap held |
| GRBL | E-stopped. Untouched since. Re-home before any motion |
| Tic | `De-energized`, VIN 12.6 V (`attempt2_estopped/tic_after_manual_deenergize.txt`) |
| Pi | `HOLD` left in place for the other session; `NOTE_from_run_37055099634.txt` (copied here) next to it |

## The one change made to Ben's gantry file

`working_volume` max 364 / 281 / 125 → **361 / 278 / 122**, i.e. max_travel minus
the 3 mm pull-off (`$27`). That matches Ben's own 2026-10-01 file. CubOS rides
every XY travel at `z_max` (`multi_tool_safe_travel_z`), and the hover-clamp
patch uses it as the tipped pipette's ceiling. After `$H`, GRBL sits at max_travel
− pull-off: the 2026-10-01 run reads WPos (388, 233.665, 121) with travel
391 / 236.665 / 124. So Z = `$132` is exactly where the Z switch tripped during
homing. With hard limits on (`$21=1` since 2026-09-30), about 13 travels per run
would end on that point, and any one that closes the switch is `ALARM:1`. With 122,
the mock's highest commanded Z is 122. **This still applies to the corrected
gantry file if its `working_volume` again equals max_travel.** The full reasoning
is in the header of `attempt*/configs/cub_xl_ben_3_instrument.yaml`.

Those configs are the only copies on this branch. They were taken out of
`cubos/configs/` so the stale deck file can't be picked up by mistake.

## What went wrong in this session, and the rule it implies

1. **It retried after an unexplained interruption without re-reading the
   issue.** A clean USB disconnect, then a replug 11 minutes later, is a person.
   The explanation was already posted on the issue. **Before any retry, re-check
   the thread** (`gh api repos/.../issues/<n>/comments`), and re-check whether
   another session holds the machine (`~/cubxl_runs/HOLD`, running
   `cubxl_run.py`).
2. **The first kill missed.** `pgrep -f "cubxl_run.py --name …"` also matched the
   `bash -c` that had launched the run, because its command line contained the
   same text. That shell's process group was tailscaled's. `kill -KILL -- -<pgid>`
   then killed only this session's own SSH processes: the session listing taken
   just before showed nothing else in it, and tailscaled runs as root. Anchor the
   match to the interpreter (`pgrep -f "^[^ ]*python[^ ]* cubos/tools/cubxl_run.py"`)
   and check that PGID == PID before killing a group.

## Files

| | |
|---|---|
| `checks/` | 19:41Z `--checks-only`: GRBL matches the file (`$130`–`$132` 364 / 281 / 125, G54 = −max_travel, `$21=1`); all four gates PASS |
| `attempt1_unplugged/` | the runner's full record, `SUMMARY.md` included. Its "CH340" kernel lines are the unplug |
| `attempt2_estopped/` | `runner.log`, `run_hardware.log` (with `@@STEP`/`@@PLUNGER` lines), `gantry_mill_control.log` sliced to 13:58:23–14:00:06 lab, `kernel_during_run.log` (empty: an E-stop is not a USB event), `tic_poll.jsonl`. No `SUMMARY.md`: SIGKILL stopped the runner before stage 5 |
| `NOTE_from_run_37055099634.txt` | the state note left on the Pi for the session holding the machine |

Hostnames in the logs are replaced with `<host>`.
