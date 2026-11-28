# stir_only_check_20261118: after the fan-ground fix, still 0 rpm

Run on PR #348 before repeating the 5× transfer protocol
([`stir_transfer_5x_20261118`](../stir_transfer_5x_20261118/README.md)). Ben had found the
fan's ground lead disconnected and soldered it (23:23 UTC). This repeats
[`stir_only_check_20261117`](../stir_only_check_20261117/README.md) exactly. The head only
homed, from its homed corner, so nothing went near a vial.

- Protocol: [`stir_only_check.yaml`](../../configs/protocol/vcl/stir_only_check.yaml): home;
  `stir` 600 rpm for 20 s (blocking); `stir` 600 rpm, 60 s limit, `wait: false`; `pause` 15 s;
  `stir` rpm 0
- Gantry [`cub_xl_ben_3_instrument_stirrer.yaml`](../../configs/gantry/cub_xl_ben_3_instrument_stirrer.yaml),
  deck [`stir_module_trial_stirrer.yaml`](../../configs/deck/stir_module_trial_stirrer.yaml) (vial_1 at x 151)
- Code: byu-vcl `6cdc7eb`. CubOS `496819c` + the four earlier patches + `stirrer-approach-1`
- Record: [`run/`](run/) ([`SUMMARY.md`](run/SUMMARY.md), [`stir_trace.json`](run/stir_trace.json))

## Result

**CubOS: 5/5 steps, 23:28:31 → 23:29:22 UTC.** Checks and gates passed, no alarms, 0 USB
kernel lines.

**The stirrer didn't turn:**

| stir | started (UTC) | stopped by | s | `31` reads | rpm max | stalled |
|---:|---|---|---:|---:|---:|---|
| 1, step 1 (20 s, blocking) | 23:28:53.282 | firmware (stall) | 12.1 | 13 | 0 | yes |
| 2, step 2 (60 s limit, no wait) | 23:29:05.440 | firmware (stall) | 12.1 | 12 | 0 | yes |

The replies match 11-17's: setpoint 100 → 600 rpm, duty 0.300 → 0.315 in the stall branch,
then `stalled` after five updates with no Hall edge. Step 1 returned after 12.2 s instead of
20, with CubOS's warning that the stirrer stalled and stopped itself. The repair didn't
change what the Uno sees. Possible causes, and the hand-turn check that followed, are in
[`stir_transfer_5x_20261118`](../stir_transfer_5x_20261118/README.md#what-the-zero-says).

`*.log` files are committed as `*.log.txt`, because the repo ignores `*.log`.
