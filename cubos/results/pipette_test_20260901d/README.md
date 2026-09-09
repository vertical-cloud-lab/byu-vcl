# pipette_test on the CubXL — 2026-09-01, run 4 (campaign 73)

**Result: 12/12 steps, `completed`, 19:23:23 → 19:28:39 UTC (5m 16s).** Gantry and
capper clean. The plunger did not move — reported by Ben, who was watching: no
motion, and no buzzing.

Configs run, unchanged from `d901754`:

- gantry `cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml`
- deck `cubos/configs/deck/ben_6vials_tiprack.yaml`
- protocol `cubos/configs/protocol/vcl/pipette_test.yaml`

Offline gates on the Pi's CubOS (`cbc33dc` + all four local patches):

```
validate_setup                PASS — 12 steps
run_protocol --mock           12/12
passive_shadow                0 interferences
passive_shadow --tip-stuck    0 interferences
```

## The plunger trace

Every `OpentronsPipette._send_command` timed via `cubos/tools/run_with_plunger_trace.py`.
Full JSON in `plunger_trace.json`.

| step | command | counter | dt | s/mm | firmware stepped? |
|---|---|---|---|---|---|
| `connect()` | `STATUS` | — | 0.007 s | — | — |
| `connect()` | `HOME` | — | 26.345 s | — | seek ran, switch never asserted |
| `connect()` | `HOME` (retry) | — | 26.348 s | — | same |
| `pick_up_tip` | `MOVE_TO 0.0` | 0.00 mm | 0.008 s | — | correct no-op, already at 0 |
| `aspirate` | `ASPIRATE 0.5` | 0 → 35.45 | 6.671 s | — | yes |
| `blowout` | `MOVE_TO 7.0` | −28.45 mm | 18.863 s | 0.663 | yes |
| `drop_tip` | `MOVE_TO 10.0` | +3.00 mm | 1.998 s | 0.666 | yes |
| `drop_tip` | `MOVE_TO 5.0` | −5.00 mm | 3.321 s | 0.664 | yes |

Identical to campaign 69. Both directions scale at ~0.665 s/mm.

### What that does and does not establish

`stepMotor()` in the PANDA firmware bit-bangs the STEP pin and counts loop
iterations. There is no encoder, no current sense, **no feedback of any kind**.
So a round trip at the expected rate proves the *Arduino emitted the steps* and
nothing more. Ben's eyes are the only motion sensor in this loop, and they say the
plunger is stationary and silent.

That splits the fault cleanly: **everything upstream of the STEP/DIR pins is
working; the TMC2209 is not driving the coils.** Total silence — no buzz, no
holding torque — means no coil current at all (a mixed-up coil pair buzzes
instead).

Earlier write-ups in this directory (`pipette_test_20260901`, `..._20260901c`) read
these timings as "the plunger moved". That inference was wrong in the safe
direction — a flat ~0.1 s does prove no steps were emitted — but the converse
does not hold. Both tools have been corrected.

### Where the numbers come from

Reading the firmware source resolved several open questions at once, all recorded
in `cubos/docs/opentrons-pipette-wiring.md`:

- `ASPIRATE 0.5` → `35.45` is exact arithmetic, not a bug in transit: `aspirate()`
  primes to `PRIME_POSITION 36.0`, clamps the argument to `MIN_VOLUME 5.0` µL, and
  targets `36.0 − 5×0.1098 = 35.45`.
- 0.673 s/mm is `MOVEMENT_VELOCITY 2500` → 400 µs/step × `STEPS_PER_MM 1592`.
- `HOME`'s 26.35 s is the `stepsCount > 50000` budget in `homePipette()`, not the
  60 s timeout — so the seek ran to completion and D9 never went HIGH.
- `max_vol: 300.00` is `MAX_VOLUME 300.0`: the firmware is built for a P300.

## Gantry — same geometry as campaign 69

From `gantry_command.log`:

```
  8 x  Z99.065    capper transit / park       (safe_z 115 + depth -15.935)
  8 x  Z124.0     tipped hover, CLAMPED by the hover-clamp patch
  4 x  Z54.065    capper engage               (rim 55 + engage_depth 15)
  2 x  Z55.0      aspirate / blowout          (tip end deck 20, nozzle at rim)
  1 x  Z92.0      drop_tip
  1 x  Z84.065    step 1, capper park at travel_z 100
  1 x  Z57.0      pick_up_tip
  1 x  Z122.0     step 5, pipette_park at travel_z 87
  1 x  Z115.0     bare-nozzle hover at safe_z
```

Distinct X: 154.0 (vial column, pipette frame), 206.0 (capper over the vials),
236.0 (capper park), 284.0 (tip rack). Controller read live before the run:
`$130/$131/$132` = 409.000 / 309.000 / 124.000, matching the gantry file; `$20=1`.

## Machine state after the run

| | |
|---|---|
| Protocol | completed, `home` as the final step |
| Electromagnet | off — `CMD_EMAG_OFF`, `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Caps | both returned to vials 1–2 by the protocol's own `cap` steps |
| GRBL | `Alarm` — normal, the board resets when the port closes. Re-home first. |
| Plunger | counter reset by the port-open board reset; physically unmoved |
| Ports | `/dev/ttyUSB0` · `/dev/ttyACM0` — both free |
| `~/CubOS` | `cbc33dc` + all four patches |

No physical plunger travel accumulated this session: the motor never turned.

## Files

| file | |
|---|---|
| `run_hardware.log` | the full run |
| `plunger_trace.json` | every plunger command, timed |
| `gantry_command.log` | the run's G-code |
| `validate.log`, `mock.log`, `shadow.log`, `shadow_tipstuck.log` | offline gates |
| `firmware_Pipette.h.txt` | the firmware pin map, as fetched |

Campaign CSVs in `../campaign_73_20260901_192323/`.
