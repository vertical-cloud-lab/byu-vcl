# stir_only_check_20261119: Hall pulses are back, but the fan doesn't start on its own

Asked for by @benwhitney5463 on PR #348 (2026-11-19, 23:40 UTC): "run the stir test. I fixed
the wiring (I hope)". On 11-18 he had found soldered wires inside the module touching each
other once it was assembled. This repeats the stir-only check of
[11-17](../stir_only_check_20261117/README.md) and [11-18](../stir_only_check_20261118/README.md),
then adds one hands-off minute at 600 rpm.

- Protocol: [`stir_only_check.yaml`](../../configs/protocol/vcl/stir_only_check.yaml): home;
  `stir` 600 rpm for 20 s (blocking); `stir` 600 rpm, 60 s limit, `wait: false`; `pause` 15 s;
  `stir` rpm 0
- Gantry [`cub_xl_ben_3_instrument_stirrer.yaml`](../../configs/gantry/cub_xl_ben_3_instrument_stirrer.yaml),
  deck [`stir_module_trial_stirrer.yaml`](../../configs/deck/stir_module_trial_stirrer.yaml) (vial_1 at x 151)
- Code: byu-vcl `2b93a20`. CubOS `496819c` + the four earlier patches + [`stirrer-approach-1`](../../patches/stirrer-approach-1.patch)
- Record: [`run/`](run/) from `cubxl_run.py` ([`SUMMARY.md`](run/SUMMARY.md),
  [`stir_trace.json`](run/stir_trace.json)), [`hands_off_60s/`](hands_off_60s/), deck frames in
  [`frames/`](frames/), taken every 2 s by [`deck_snaps.py`](deck_snaps.py) (HTTP GETs of
  `deckcam.py`'s `/snapshot.jpg`; read-only)

## Before it ran

- The Pi: no `HOLD`, the Uno and the GRBL board's CH340 on their usual `by-id` paths, nothing
  holding either port, `throttled=0x0`.
- **USB over-current at 23:27:50 UTC today**, 13 minutes before the request: 119
  `over-current change` lines across every port in about 3 s. The CH340, the Uno and the
  Realtek USB Ethernet adapter dropped off and were back by 23:27:53. As at 11-18's event at
  23:45:28, nothing was being commanded. Nothing has been logged since, including during both
  runs below.
- Deck frame at 23:43:00 ([`frames/234300Z_deckcam_before.jpg`](frames/234300Z_deckcam_before.jpg)):
  the same layout as 11-18. The module's cable now runs up the middle of the deck, between the
  vial column and the tip rack. The head only homes in this check, from its homed corner, so
  the cable's route didn't matter.

## Run 1: the check through CubOS (23:44:53 → 23:45:52 UTC)

**CubOS 5/5 steps**, rc 0, 58.7 s. Stage 1 checks and all four gates passed, no alarms,
0 USB kernel lines during the run.

**The Uno counted Hall pulses for the first time since 11-05.** `rpm` in `31` is
30 × the falling edges in the last 2 s window, so each value repeats for two reads:

| window | `30` sent (UTC) | `rpm` at each 2 s update | duty | ended |
|---|---|---|---|---|
| 1: 600 rpm, 20 s, blocking | 23:45:14.725 | 270, 240, 270, 210, then 0 ×5 | 0.300 → 0.499, then 0.504 → 0.524 | its 20 s timer, at 23:45:34.97, one update short of the stall flag |
| 2: 600 rpm, 60 s limit, no wait | 23:45:34.980 | 0, 0, 150, 390, 390, 480, 510 | 0.300 → 0.306, then 0.381 → 0.507 | `stir` rpm 0 (step 4) at 23:45:49.99, at 15 s, still climbing |

- **Window 1** turned at 210-270 rpm for about 8 s, then counted nothing for its last 10 s.
  The duty went up 1% per update from 0.499 to 0.524, which is the firmware's stall branch:
  0.75 s off, then a 0.5 s full-power kick, every 2 s. None of the five kicks restarted it.
  The firmware sets `stalled` on the sixth such update. The 20 s timer ran out first, so
  the blocking step returned normally after 20.3 s.
- **Window 2** counted nothing for about 6 s (two stall-branch updates), then climbed from 150 to
  510 rpm. It was still speeding up when the protocol stopped it.
- **A hand was on the module during both windows** (deck frames:
  [contact sheet of the module, 23:45:11-23:45:53](frames/stir_module_crops_234511-234553Z.jpg),
  [23:45:39](frames/234539Z_deckcam.jpg)): at the bottom edge by the module at 23:45:17, 2 s
  into window 1, and on the module at 23:45:39-41, in window 2. Window 2's first pulses were
  counted in the 2 s up to 23:45:41.05, while the hand was there. At 23:45:43 the hand was
  gone, and the fan went on speeding up without it to 510 rpm
  ([23:45:49](frames/234549Z_deckcam.jpg)).

On the CubOS side, everything worked as designed. The blocking `stir` ran to the firmware's own
timer for the first time; on 11-17 and 11-18 it always ended in a stall. The non-blocking
`stir` was stopped by the protocol, and teardown sent `30,0`.

## Run 2: one hands-off minute (23:52:04 → 23:53:09 UTC)

To see what the module does with nobody touching it, 11-05's
[`stir_trial.py`](../stir_module_trial_20261105/stir/stir_trial.py) (copied unchanged, sha256
`9d16a6936063`) sent `30,600,60` straight to the Uno and read `31` every second. The gantry
did not move. The PR comment asked for hands off from 23:52.

- **Not one pulse.** The duty went 0.300 → 0.315 in the stall branch, and at 12.2 s
  (23:52:16.58) the firmware stopped the fan itself and set `stalled`. That's the same
  sequence as every window on 11-17 and 11-18
  ([`hold600.jsonl`](hands_off_60s/hold600.jsonl), [console](hands_off_60s/console.txt)).
- 34 deck frames, 23:52:02-23:53:08: nothing near the module in any of them
  ([contact sheet](hands_off_60s/stir_module_crops_235202-235308Z.jpg),
  [23:52:36](hands_off_60s/235236Z_deckcam.jpg)).
- No USB kernel lines.

## What it says

1. **The Hall fix worked.** Whenever the fan turned, the Uno counted it, at believable speeds
   (150-510 rpm), and the count dropped to zero when it stopped. On 11-17 and 11-18 not one
   edge was counted in 14 stir windows.
2. **The fan doesn't start from rest on its own, but it turns once it's going.** It never
   started when left alone (five full-power kicks in run 2). In run 1 it stopped after 8 s in
   window 1 and didn't restart. Window 2 started only after a hand had been on the module,
   then kept speeding up for 7 s after the hand was gone.

**That is what the stirrer did on 11-05 when vial 1 sat too low over the magnets.** The bar's
pull on the magnets holds them still
([`stirrer_spacer_20261105`](../stirrer_spacer_20261105/README.md)):

| under the vial (11-05) | starts from rest |
|---|---|
| spacer alone | no: 2 single pulses in 5 starts, stalled at 12-18 s every time |
| spacer + 2 washers | never stalled, but turned in bursts until the duty passed about 0.8 |
| spacer + 3 washers, **4.6 mm** (Ben measured it) | yes, on the first kick 3 of 3 times, and held 300-1200 rpm |

That stack was in place for the [11-05 trial](../stir_module_trial_20261105/README.md#the-stir-225538-utc).
After its protocol, the same stack had lost speed: 540 rpm, then bursts between 0 and
390 rpm. That record suspected the capper's decap and recap of shifting the washers. Since
then, vial 1 has been decapped and recapped ten more times (11-17 and 11-18), and the module
has been opened for the wiring fixes. So the 4.6 mm under vial 1 may no longer be there.

**Two checks, either of which settles it:**

- **Is the 4.6 mm stack (or the Ø10 × 4.6 mm spacer drawn to replace it) still under
  vial 1,** with the vial sitting on it?
- **Run a stir with vial 1 lifted out.** With no bar above it, the fan started on the first
  kick on 11-04 and held 300 rpm, then followed the ramp to 1200 rpm and settled at 1260
  ([`stirrer_spin_20261104`](../stirrer_spin_20261104/README.md)). If it does that now, the
  wiring is fine and the height is the problem. If it still won't start with the vial out,
  then either the fan isn't getting power (it won't even twitch on the kicks, every 2 s) or
  the holder catches on something (it twitches but doesn't spin up). On 11-03, turned by
  hand, it "moves jerkily, as if the magnets were catching on something".

## Changed on the Pi

- `~/byu-vcl-stir5x` fast-forwarded from `6cdc7eb` to `2b93a20` (results, and `cubxl_run.py`'s
  lab-time zone).
- New in `~/cubxl_runs/`: `stir_only_check_20261119/` and its `.console`;
  `stir_check_20261119_frames/` (the 23:43:00 frame, 59 frames from run 1, `deck_snaps.py`
  and its output);
  `stir_hold_20261119/` (the copy of `stir_trial.py`, its log and 34 frames).
- `~/cubxl_runs/HOLD` was set at 23:42:59 and removed at 23:54:05.
- Nothing else. `~/CubOS` was not touched.

`*.log` files are committed as `*.log.txt`, because the repo ignores `*.log`.
