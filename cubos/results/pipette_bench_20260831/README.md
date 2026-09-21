# Plunger bench test — 2026-08-31

Ran `cubos/tools/pipette_bench_check.py` against the CubXL's Arduino at
@benwhitney5463's request, plus two follow-up probes the tool's own output
made necessary. **No protocol was run and no gantry motion was commanded** —
the only hardware actuated was the pipette plunger.

Also this session: `patches/tipped-hover-clamp-and-ceiling-travel.patch` was
applied to `~/CubOS` on the Pi, and the 2026-08-31 rev-2 config trio was
validated offline against it.

---

## Verdict

**The plunger stepper only ever turns one way.** The serial link is healthy,
the firmware parses every command, and the motor is genuinely driven — but
only in the direction of increasing `pos`. Every command that would retract
the plunger returns `OK` in ~0.11 s and does nothing.

This is not the wiring to the Pi, not the shared `/dev/ttyACM0`, and not
CubOS. It is the plunger's own direction handling — the DIR line, the driver's
direction input, or the firmware's sign convention.

---

## Evidence

### Pass 1 — `pipette_bench_check.py --move`

```
boot banner after  3.80s: 'OK:Ready'
  STATUS (read-only)       dt=   0.01s  reply=OK:{"homed":0,"pos":0.00,"max_vol":300.00}
  HOME                     dt=   0.52s  reply=OK:{"msg":"Pipette homed"}                    pos=0.0  homed=1
  MOVE_TO 5.0 mm           dt=   3.35s  reply=OK:{"msg":"Pipette moved","v":[5.00]}         pos=5.0  homed=1
  MOVE_TO 10.0 mm          dt=   3.35s  reply=OK:{"msg":"Pipette moved","v":[10.00]}        pos=10.0 homed=1
  MOVE_TO 0.0 mm           dt=   0.11s  reply=OK:{"msg":"Pipette moved"}                    pos=10.0 homed=1
  ASPIRATE 1.0 mm          dt=   5.02s  reply=OK:{"msg":"Pipette aspirated","v":[1.00,36.00]} pos=36.0 homed=1
  DISPENSE 1.0 mm          dt=   1.52s  reply=OK:{"msg":"Pipette dispensed","v":[1.00,44.00]} pos=44.0 homed=1
```

The tool's built-in verdict — *"round trips vary with distance, so the stepper
is being driven"* — is **right about the stepper and wrong about the
conclusion**, because it compares two moves that happen to be the same
distance (0→5 and 5→10 are both 5 mm). It also contradicts its own HOME
criterion in the same output. Both are fixed in the tool now.

### Pass 2 — is `homed` the gate? (`probe_direction.log`)

The leading hypothesis after campaign 33 was that the firmware refuses
absolute moves until homed. **Wrong** — with `homed=0`, straight off a board
reset, exactly the state campaign 33 ran in:

```
  MOVE_TO 5.0 (unhomed)      dt=  3.36s  pos=5.0  homed=0
  MOVE_TO 10.0 (unhomed)     dt=  3.35s  pos=10.0 homed=0
  ASPIRATE 1.0 (unhomed)     dt=  5.02s  pos=36.0 homed=0
```

Identical timings homed or not. `homed` gates nothing.

The same probe found what does:

```
  HOME                       dt=  0.52s  pos=0.0  homed=1
  MOVE_TO 3.0                dt=  2.02s  pos=3.0  homed=1
  MOVE_TO 0.0  <-- zero      dt=  0.11s  pos=3.0  homed=1
  MOVE_TO 0.5                dt=  0.11s  pos=3.0  homed=1     <- v:[0.50] present
  MOVE_TO 0                  dt=  0.11s  pos=3.0  homed=1
```

`MOVE_TO 0.5` was *parsed and accepted* (`"v":[0.50]` in the reply) and still
did not move. So it is not an argument-parsing bug and 0.0 is not
special-cased — **the firmware refuses any target below the current
position.**

### Pass 3 — does HOME retract? (`probe_home_retract.log`)

```
  MOVE_TO 2.0 (forward)      dt=  1.35s  pos=2.0  homed=0
  HOME (from pos 2.0)        dt=  0.52s  pos=0.0  homed=1
```

Motion in this firmware costs a very consistent **0.673 s/mm**:

| commanded | distance | dt | s/mm |
|---|---|---|---|
| MOVE_TO 2.0 from 0 | 2 mm | 1.35 s | 0.675 |
| MOVE_TO 3.0 from 0 | 3 mm | 2.02 s | 0.673 |
| MOVE_TO 5.0 from 0 | 5 mm | 3.35 s | 0.670 |
| MOVE_TO 10.0 from 5 | 5 mm | 3.35 s | 0.670 |

A 2 mm retraction should therefore cost ~1.35 s. HOME returned in 0.52 s —
the same 0.52 s it takes from `pos=0`, where there is nothing to do. **HOME
zeroes the counter without moving the plunger.** There is no recovery path in
the command set.

---

## This explains campaign 33 exactly

Timings from the 2026-08-31 run log, mapped onto the commands above:

| protocol step | plunger command | plunger pos before | result |
|---|---|---|---|
| `pick_up_tip` | MOVE_TO 0.0 | 0.0 | no-op — already there |
| `aspirate` | ASPIRATE 0.5 | 0.0 | **moved**, ~5.9 s, left pos at 36 |
| `blowout` | MOVE_TO 7.0 | 36.0 | 7 < 36 → **ignored** |
| `drop_tip` | MOVE_TO 10.0, then 5.0 | 36.0 | both < 36 → **ignored** |

So one of the four *did* actuate. `aspirate` drove the plunger ~26 mm rather
than the commanded 0.5 mm and parked it above every subsequent target;
everything after it was a retraction, and retractions do not execute.

Two further consequences worth separating out:

* **`ASPIRATE` does not honour its argument.** `ASPIRATE 1.0` moved to
  `pos 36.0`, deterministically, from `pos 10.0` in two independent runs.
  `DISPENSE 1.0` then moved to 44.0 — *further in the same direction*, not
  back. Whatever the firmware means by these, it is not what CubOS means.
* **`mm_to_ul: 0.025` was never the whole problem.** It is a real issue
  (`volume_ul: 20.0` → 0.5 mm of plunger, and it is the p20 constant while the
  firmware reports `max_vol: 300.00`), but fixing it would not have made
  blowout or drop_tip move.

---

## What to check, cheapest first

1. **The DIR line.** One direction works and the other never does. Check the
   DIR pin's continuity from the MCU to the driver, its logic level in each
   state, and the driver's direction input. If DIR is floating or stuck, this
   is exactly the signature.
2. **The firmware's retract path.** `MOVE_TO` returning in 0.11 s with a
   well-formed `v` echo means it decided not to move rather than failing to.
   A guard like `if (target > pos)` or an unsigned step count would do this.
   HOME returning 0.52 s from any position points the same way: it sets the
   counter instead of seeking an endstop.
3. **Then settle which pipette is mounted.** Firmware says `max_vol: 300.00`;
   the gantry YAML says `p20_single_gen2`. Every p20 constant in
   `instruments/pipette/models.py` is marked `# placeholder`; the p300 entry
   is calibrated from PANDA-BEAR. `drop_tip_position: 10.0` is nowhere near
   the ~60 mm a p300 ejector needs, so `drop_tip` would not eject even with
   the direction fixed.

## ⚠️ The plunger was driven ~85 mm in one direction

Cumulative forward travel commanded across the three passes, none of it
retracted: ~44 mm + ~36 mm + ~5 mm. A p300 plunger has roughly 60 mm of
travel, so it has very likely been sitting against its mechanical stop and
skipping steps for part of that (a stalled stepper still consumes the full
commanded time, so the 0.673 s/mm figures hold either way). **Worth
inspecting the plunger and its coupling before drawing conclusions from the
mechanism.** `pipette_bench_check.py` has been changed so it cannot do this
again — it now walks a bounded ±3 mm and tests direction explicitly.

---

## Hover-clamp patch — applied

`git apply` of `patches/tipped-hover-clamp-and-ceiling-travel.patch` into
`~/CubOS` succeeded cleanly. All three local patches are now live:

```
 M packages/core/src/cubos/gantry/gantry_config.py
 M packages/core/src/cubos/gantry/instrument_loader.py
 M packages/core/src/cubos/gantry/instrument_mount.py
 M packages/core/src/cubos/instruments/capper/vendors/pawduino.py
 M packages/core/src/cubos/protocol_engine/commands/capper.py
 M packages/core/src/cubos/validation/bounds.py
 M packages/core/src/cubos/validation/protocol_semantics.py
 M packages/core/tests/validation/test_pipette_tip_state.py
```

Reversible with `git apply -R`. **If it is ever reverted, `safe_z` must drop
from 115 to ≤ 89** or nothing with a tip attached will validate.

The clamp fires three times in the rev-2 trio, once per tipped engage:

```
OpentronsPipette cannot reach safe_z 115.000 (tool point rides 35.000 below
the carriage; ceiling 124.000). Hovering/traveling at 89.000 instead —
confirm this plane clears all deck contents.
```

## Offline validation of the rev-2 trio

| check | as attached | with `travel_z` 100 → 89 |
|---|---|---|
| `validate_setup` | **FAIL, 4 violations** | **PASS**, 18 steps |
| `run_protocol --mock` | aborts | 18/18 |
| `passive_shadow` | — | **0** interferences |
| `passive_shadow --tip-stuck` | — | **0** interferences |

The tip-stuck column has never been 0 before (it was 3 at `safe_z: 87`).
Raising `safe_z` to 115 plus parking at `[236, 175]` removes the passive-tip
hazard entirely rather than working around it.

Clearances at `safe_z: 115` / `engage_depth_mm: 15`, from the trace:

| | safe_z 87 | **safe_z 115** |
|---|---|---|
| nozzle height during capper legs | deck 71.065 | **deck 99.065** |
| held-cap underside vs. neighbouring cap top | 6 mm | **30 mm** |

Both of the video's symptoms map onto those two rows.

## Files

| file | what it is |
|---|---|
| `bench_move.log` | `pipette_bench_check.py --move`, verbatim |
| `probe_direction.log` | unhomed MOVE_TO, and the `MOVE_TO 0.5` test |
| `probe_home_retract.log` | HOME from a non-zero position |
| `validate_asattached.log` | the 4 violations |
| `validate_corrected.log` | PASS with `travel_z: 89` |
| `shadow_corrected_tipstuck.log` | 0 interferences, tip-stuck |
| `trace_corrected.log` | commanded gantry Z per instrument |
| `pipette_test_corrected.yaml` | the one-line fix, validated |

## Machine state — left clean

| | |
|---|---|
| Gantry motion | **none commanded** — no homing, no G-code, `/dev/ttyUSB0` never opened |
| Electromagnet | off — `CMD_EMAG_OFF`, `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held |
| Plunger | `OK:{"homed":0,"pos":0.00,"max_vol":300.00}` (counter reset by the board reset; physical position unknown — see the ~85 mm note) |
| Ports | both free |
