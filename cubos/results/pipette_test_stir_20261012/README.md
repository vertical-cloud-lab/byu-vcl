# pipette_test_stir_20261012: 74/74 with the tip stirring vial_2 in place of `mix`

`pipette_test_stir.yaml` on the CubXL, 2026-10-12, for @benwhitney5463 on PR #269. It is
`pipette_test_mix` with step 8's `mix` in vial_2 replaced by gantry moves that stir with the
tip. Ben's question was whether the machine can move fast enough, safely, to mix. The vial
ID is 21 mm and the tip starts at the centre. Ben's 10-02 gantry and deck files and the
TMC2209 plunger, so `--no-tic`, as in the 10-09 mix runs.

✅ **74/74 steps, protocol complete.** Campaign 132, 18:43:44Z to 18:47:01Z (12:43–12:47
lab), 197 s wall. [`SUMMARY.md`](SUMMARY.md) is the runner's own summary, and
[`runner.log`](runner.log) has everything. There were no alarms beyond the usual one at
connect and no USB events. The post-run plunger `HOME` came out at +0.01 mm.

## The stir

[`stir_moves.py`](../../tools/stir_moves.py) generates it
(`--x 136.668 --y 78 --z 21 --r-max 5`). The entry move puts the tip end at deck Z 21 at
vial_2's centre, gantry (81.668, 67, 56), with the same `Z122 / X81.668 / Y67.0 / Z56.0`
the 10-09 mix's engage sent. Then:

1. 5 square laps counter-clockwise, then 5 clockwise. The corners are at (±3.5, ±3.5) mm,
   so each side is 7 mm.
2. 4 round trips of ±5 mm along X through the centre, then 4 along Y.
3. Back to the centre, then straight up to gantry Z 122.

Every step changes one axis, so each is exactly one `G01`. In
[`gantry_command.log`](gantry_command.log), the 61 `G01`s between the entry and the lift
are all at Z 56. The farthest is 5.000 mm from the centre, which leaves 5.5 mm from the
tip's axis to the glass of a 21 mm ID.

## How fast it went

These times come from [`gantry_mill_control.log`](gantry_mill_control.log): from sending each
`G01` to GRBL reporting Idle.

| move | n | s each | mean speed | motion alone | top speed |
|---|---:|---:|---:|---:|---:|
| 7 mm square side | 40 | 0.408 | 17 mm/s | 0.31 s | 46 mm/s |
| 10 mm stroke | 14 | 0.459 | 22 mm/s | 0.37 s | 50 mm/s |
| 3.5, 5 and 8.5 mm (into and out of each pattern) | 7 | 0.31–0.46 | | | |

"Motion alone" and "top speed" are the trapezoidal profile at GRBL's 300 mm/s² and F3000.
After each move there is another ~0.05 s before the next `G01` is sent.

- **The 61 moves took 28.3 s for 454 mm of path, 16 mm/s on average.** One square lap took
  1.84 s, about 33 laps a minute. One stroke took 0.51 s, about 2 a second. Steps 8–70 (in,
  stir, out) took 34.2 s, against 40.5 s for the 10-09 `mix` they replace.
- **The tip reaches 46–50 mm/s, but only for an instant.** CubOS waits for Idle after every
  `G01`, so each move starts and ends at rest. At 300 mm/s² a 7 mm side tops out at 46 mm/s,
  below F3000, and a 10 mm stroke covers only its middle 1.7 mm at 50 mm/s. So the
  acceleration sets the speed here, not the feed rate. F5000 would save under 0.01 s a stroke.
- **About a quarter of every move is overhead.** The measured times are ~0.1 s longer than
  the motion profile, in 0.05 s steps because CubOS polls status every 50 ms. The ~0.05 s
  between moves comes on top of that.

## Did it mix?

The cameras can't answer this on their own:

- After `drop_tip` (step 71), the head camera looks into the open vial_2 from the same pose
  as step 9 on 10-09. After the 10-09 `mix` there was a darker patch in the middle. Today the
  liquid looks evenly red ([side by side](frames/vial2_after_mix_20261009_vs_after_stir_20261012.jpg)).
  But three days separate the two frames, and nothing looked into the open vial_2 before
  today's stir, so the change can't be put down to the stir.
- The overhead camera, before the run and after it (vials capped, head homed), sees vial_2's
  side through the glass. It is evenly red in both
  ([side by side](frames/vials_overhead_before_vs_after.jpg)).
- The frames after the entry (step 8) and the lift (step 70) show the head over the vial,
  not the liquid.

Looking at the vial in person is the better check.

## Making it faster

- **Queue the moves instead of waiting for Idle.** If the stir's segments went into GRBL's
  planner together, or as `G2`/`G3` arcs, GRBL would blend them without stopping. On a
  5 mm-radius circle the 300 mm/s² limit allows about √(300 × 5) ≈ 39 mm/s, which is 0.8 s
  a turn (~75 rpm) with no stops. That is more than twice today's lap rate. It needs a CubOS
  command (a `stir`, say) or a patch, because YAML `move`s can't queue.
- **Raise `$120`/`$121` (acceleration).** At 1000 mm/s² a 10 mm stroke needs ~0.25 s of
  motion instead of 0.37 s. It is a machine-wide setting, so it needs its own test for missed
  steps. The gantry file and `cubxl_run.py`'s GRBL check would change with it.
- **Raising the feed rate alone barely helps** at these lengths, as above.

## Steps

The gantry, deck and every step outside vial_2 are the same as
[`../pipette_test_mix_20261009b/`](../pipette_test_mix_20261009b/README.md), which is the
baseline.

| step | command | s | 10-09b |
|---:|---|---:|---:|
| 0 | home | 7.9 | 22.8 |
| 1 | move | 9.5 | 9.5 |
| 2 | decap vial_1 | 7.3 | 7.3 |
| 3 | pick_up_tip | 8.4 | 8.4 |
| 4 | mix vial_1 | 46.1 | 46.2 |
| 5 | move | 5.0 | 5.0 |
| 6 | cap vial_1 | 7.1 | 7.0 |
| 7 | decap vial_2 | 5.9 | 5.9 |
| 8 | **move into vial_2** | 4.3 | mix vial_2: 40.5 |
| 9–69 | **61 stir moves** | 28.3 (0.36–0.51 each) | |
| 70 | **move up out of vial_2** | 1.7 | |
| 71 | drop_tip | 11.2 | 12.8 |
| 72 | cap vial_2 | 7.4 | 7.4 |
| 73 | home | 22.3 | 22.3 |

Step 0 was shorter because the gantry started in the homed corner. On 10-09 it had started
over vial_1. `drop_tip` was 1.6 s shorter because step 70 had already lifted the head to
Z 122.

**Plunger** ([`plunger_trace.json`](plunger_trace.json)): step 4 sent the same 6 `ASPIRATE`
and 6 `DISPENSE` as on 10-09, with the same timings. The plunger stayed at 32.5 mm (blowout)
through the stir, so the tip carried nothing into or out of vial_2.

## State after the run (18:47Z)

| | |
|---|---|
| gantry | Homed and idle |
| magnet | Off. Cap sensor 0 |
| plunger | Homed by the post-run check. No tip: `drop_tip` ejected it over A1 |
| vials | Both capped |
| Pi | `~/cubxl_runs/HOLD` removed at 18:47:38Z. `~/byu-vcl-pipette` is on `claude/issue-169-20261009-2151` at `f4ef516`, the commit that ran |

The two overhead stills `frames/pre_run_1836Z__cam0_csi0.jpg` and
`frames/post_run_1849Z__cam0_csi0.jpg` were taken by hand with `rpicam-still`, outside the
runner. The Pi's hostname is redacted in [`kernel_during_run.log`](kernel_during_run.log).
