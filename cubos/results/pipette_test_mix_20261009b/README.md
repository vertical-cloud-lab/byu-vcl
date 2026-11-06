# pipette_test_mix_20261009b: 12/12 with `mix` in place of `aspirate` and `blowout`

`pipette_test_mix.yaml` on the CubXL for issue #169, 2026-10-09: `pipette_test`
with step 4 (`aspirate` in vial_1) and step 8 (`blowout` in vial_2) replaced by
`mix`, 20 µL, 3 cycles, at the same height −35. Ben's 10-02 gantry and deck
files. The plunger runs on the TMC2209 (Adafruit 6121) with the 10-07
spreadCycle firmware, so the runner had `--no-tic`.

✅ **12/12 steps, protocol complete.** Campaign 124, 21:39:16 to 21:42:55Z
(15:39–15:42 lab), 218 s wall. [`SUMMARY.md`](SUMMARY.md) is the runner's own
summary, and [`runner.log`](runner.log) has everything.

This is the second attempt. The first,
[`../pipette_test_mix_20261009/`](../pipette_test_mix_20261009/README.md),
stopped at `decap vial_1` because the capper was miswired. Ben fixed the wiring
at 21:37Z, and the limit-switch probe was run again before this run
([`preflight/probe.log`](preflight/probe.log)). It passed: the switch opened
~1.01 mm UP, the ladder tripped at ~2.05 / 2.10 / 2.12 mm, and `HOME` took
1.347 s.

## Steps

The gantry, deck and every other step are the same as
[`../pipette_test_20261007/`](../pipette_test_20261007/SUMMARY.md), so that run
is the baseline.

| step | command | s | 10-07 |
|---:|---|---:|---:|
| 0 | home | 22.8 | 7.9 |
| 1 | move | 9.5 | 9.5 |
| 2 | decap vial_1 | 7.3 | 7.3 |
| 3 | pick_up_tip | 8.4 | 8.4 |
| 4 | **mix vial_1** | **46.2** | aspirate 12.8 |
| 5 | move | 5.0 | 5.0 |
| 6 | cap vial_1 | 7.0 | 7.0 |
| 7 | decap vial_2 | 5.9 | 5.9 |
| 8 | **mix vial_2** | **40.5** | blowout 7.2 |
| 9 | drop_tip | 12.8 | 12.8 |
| 10 | cap vial_2 | 7.4 | 7.4 |
| 11 | home | 22.3 | 22.3 |

Step 0 took longer because the gantry started over vial_1, where the first
attempt stopped, not in the homed corner. Both decaps caught their caps on the
first engage.

## The two mixes

**G-code** ([`gantry_command.log`](gantry_command.log)): each mix engaged at
gantry Z 56 (tip end 35 mm below the rim), then went `Z57`, `Z56` three times,
at (81.668, 34) in vial_1 and (81.668, 67) in vial_2. That's 6 more `G01` per
mix than the step it replaced, 57 in all against 45 on 10-07. Everything else
matches 10-07 command for command.

**Plunger** ([`plunger_trace.json`](plunger_trace.json)): each mix sent 6
`ASPIRATE 20` and 6 `DISPENSE 20`, alternating. CubOS's 3 cycles are 6 strokes,
because each cycle aspirates and dispenses once at each height.

| | s | plunger |
|---|---:|---|
| first `ASPIRATE` in vial_1 | 5.00 | 0.0 → 28.0 (prime) → 1.2 |
| every other `ASPIRATE` | 2.86 | 32.5 → 28.0 → 1.2 |
| every `DISPENSE` | 2.86 | 1.2 → 32.5, reply `"v":[20.00,32.50]` |

That is the firmware's behaviour, as expected from `src/Pipette.cpp`:
`ASPIRATE` always goes to prime first, and `DISPENSE` ignores its volume and
goes to the blowout plane. Two consequences:

1. **Every stroke ends with a full blowout.** That's the "displace a bit more
   air than aspirated" that Alex suggested on 10-07 for the drop left on the
   tip, but it happens on every stroke, not once at the end.
2. **From the second stroke on, each `ASPIRATE` draws ~23 µL, not 20.** It
   starts at 32.5 rather than 28.0, so the stroke is 31.3 mm. At the firmware's
   `UL_TO_MM 1.34`, that's ~23.4 µL nominal. `UL_TO_MM` is Opentrons' figure,
   not a calibration of this pipette.

As with step 4's `aspirate` in `pipette_test`, the first `ASPIRATE` in vial_1
pushed ~21 µL of air out through the tip on its way down to prime, before it
drew any liquid.

**After the run:** a plunger `HOME` of 12.669 s puts the plunger at 27.97 mm
against the firmware's 28.0 (**−0.03 mm**), so it lost no steps over 24 strokes.

## Frames

Both cameras after steps 2, 3, 4, 8, 9 and 10, in [`frames/`](frames/).
`cam1_csi1` after step 9 shows vial_2 open with red liquid in it, and vial_1
recapped. The cameras show where the head went, not liquid moving.

## State after the run (21:43Z)

| | |
|---|---|
| gantry | Homed and idle |
| magnet | Off. Cap sensor 0 |
| plunger | Homed by the post-run check. No tip: `drop_tip` ejected it over A1 |
| vials | Both capped |
| Pi | `~/cubxl_runs/HOLD` removed at 21:43:25Z. `~/byu-vcl-pipette` is on `claude/issue-169-20261009-2117` at `ef63f31`, the commit that ran |
