# pipette_test_mix_20261009: stopped at step 2, the capper never caught vial_1's cap

**Cause: the capper was wired incorrectly.** Ben found and fixed it at 21:37Z,
and the re-run,
[`../pipette_test_mix_20261009b/`](../pipette_test_mix_20261009b/README.md),
completed 12/12 with both decaps catching on the first engage.

`pipette_test_mix.yaml` (`pipette_test` with `mix` in place of `aspirate` and
`blowout`) on the CubXL for issue #169, 2026-10-09. Ben's 10-02 gantry and deck
files. The plunger runs on the TMC2209 (Adafruit 6121) with the 10-07
spreadCycle firmware, so the runner had `--no-tic`.

❌ **Stopped after 2/12 steps.** `decap vial_1` engaged three times
(`capture_retries: 2`), and after each retract the cap sensor read no cap:

```
decap failed for 'vial_1': CapperError: decap: sensor did not confirm cap
capture after 3 attempt(s) (last reading: cap_present=False, expected True).
```

No mix ran, no tip was picked up, and the pipette never went over a vial.

## Before the run

| UTC | what | result |
|---|---|---|
| 21:20 | Pi, read-only | Idle, no `HOLD`. Arduino and CH340 on their usual `by-id` paths, no Tic on USB. Up since 10-08 21:51Z |
| 21:23 | `~/cubxl_runs/HOLD` | Written for this run |
| 21:24 | Offline gates ([`offline_gates/`](offline_gates/)) | validate PASS, mock 12/12, both collision shadows clear |
| 21:25:43 | Limit-switch probe ([`preflight/probe.log`](preflight/probe.log)), script [`../tmc2209_probe_20261005/tmc2209_probe.py`](../tmc2209_probe_20261005/tmc2209_probe.py) | The switch opened ~1.01 mm UP, so `DIR LOW` is up. The ladder tripped at ~2.05 / 2.12 / 2.13 mm, with no lost steps up to the `MOVE_TO` rate. `HOME` took 1.348 s. Same as 10-07 and 10-08 |

The offline trace puts each mix at gantry Z 56 over the vial (tip end 35 mm
below the rim at deck Z 56), cycling up to Z 57 and back three times.

## The run

[`SUMMARY.md`](SUMMARY.md), [`runner.log`](runner.log). It ran 21:27:16 to
21:28:04Z (15:27–15:28 lab). Checks and gates passed again inside the runner.

| step | command | s | |
|---:|---|---:|---|
| 0 | home | 7.9 | |
| 1 | move | 9.5 | capper to park (206, 25) |
| 2 | decap vial_1 | 14.5 | ❌ |

The G-code ([`gantry_command.log`](gantry_command.log)) is what the 10-06 and
10-07 runs sent for step 2: Z 122, then `X136.668`, `Y45.0`, `Z99.0`. It then
engaged at `Z55.0` and retracted to `Z99.0`, three times. On 10-07 the first
engage caught the cap. On 10-06 the second did.

The plunger did what it should: `HOME`, prime to 28.0, and after the run a
`HOME` of 12.681 s, which puts the plunger at 28.00 mm (+0.00 mm).

## State after the stop (21:28Z)

| | |
|---|---|
| gantry | Homed and idle, capper at gantry (136.668, 45.0, 99.0) over vial_1 |
| magnet | Off (`EMAG_OFF` after the run). Cap sensor 0 |
| plunger | Homed by the post-run check. No tip |
| vial_1 | Looks capped in the close-up camera, [`after_stop/after_stop_cam1.jpg`](after_stop/after_stop_cam1.jpg) |

The photos in [`after_stop/`](after_stop/) were taken from the stopped
position. Compared with the 10-07 frames, the close-up camera now sits
differently on the head: the capper and its red-wired board sit about 190 px
further right in the frame. So the photos can't show whether vial_1 moved
relative to the capper.

## What was considered before Ben found the wiring

Written before his reply, most likely first. Ben's fix was to the capper's
wiring:

1. **The cap sits differently on vial_1**, for example pressed on harder after a
   refill. On 10-06 the first engage already missed, so vial_1's decap has been
   marginal.
2. **The vial holder or vial_1 moved** relative to the capper since 10-07.
3. **The magnet isn't pulling**, from its supply or wiring. The plunger's 12 V
   is fine: the probe and both `HOME`s were normal.

## A CubOS bug the stop exposed

After the failed decap, CubOS's protocol-level failure retract raised
`Unknown instrument 'PawduinoCapper'. Available: camera_3, pipette,
vial_capper_decapper` ([`run_hardware.log`](run_hardware.log)).
`last_commanded_pose` records the instrument's `name`, which defaults to its
class name when the gantry file gives none, and the retract looks that up among
the gantry file's keys (`protocol_engine/setup.py`, `_best_effort_retract_to_safe_z`,
at CubOS `496819c`). It did no harm here, because the decap
command had already retracted the capper to Z 99. A failure that leaves a tool
low would not get this second retract.
