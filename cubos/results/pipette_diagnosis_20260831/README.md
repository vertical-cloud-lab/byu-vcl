# Why the plunger never actuated, and why `safe_z` is not the travel height

2026-08-31, after the 18/18 `pipette_test` run (campaign 33). **No motion was
commanded to the CubXL for this investigation** — every number below comes
from reading the controller, reading the Arduino's status register, and
re-reading the timestamps CubOS itself wrote during the run.

Ben's report: the head travelled roughly 10 mm below the `safe_z` he had
jogged to; the pipette tip came close to the rail; caps slid off the
electromagnet against neighbouring caps; and the pipette did not aspirate,
blow out, or drop a tip.

---

## 1. `safe_z` is a tool-point plane, not a carriage height

Measured, from `~/.cubos/logs/gantry/command.log` for campaign 33:

```
G01 Z71.065 F2000     <- every capper transit
G01 Z52.065 F2000     <- every capper engage
G01 Z87.0   F2000     <- the ONE bare-pipette hover (pick_up_tip approach)
G01 Z122.0  F2000     <- every tipped-pipette hover
```

`safe_z` is 87.0 and the capper transits at **71.065**. The gap is exactly the
capper's `depth: -15.935`: CubOS commands `gantry_z = safe_z + depth`. The jog
widget reports raw WPos with no instrument offset applied, so jogging to 87
puts the carriage 15.935 mm higher than any capper transit in the protocol —
the discrepancy Ben saw, and it is ~16 mm, not ~10.

Per-instrument, at `safe_z: 87`:

| what | gantry Z | tool point (deck Z) |
|---|---|---|
| capper transit / park | 71.065 | 87.0 (capper) |
| capper engage over a vial | 52.065 | 68.0 (capper) |
| bare pipette hover | 87.0 | 87.0 |
| pipette hover with a 35 mm tip | 122.0 | 87.0 (tip end) |

The pipette's `depth` is 0.0, so **the bare nozzle is the lowest thing on the
head and it rides at deck Z = `safe_z` − 15.935 during every capper leg.**
That is the number to compare against the rail.

### Held-cap clearance

A gripped cap's top is at the engage plane (deck 68 = rim 55 + `engage_depth_mm`
13) and its underside rests on the rim (deck 55). Lifting the tool point to
`safe_z` raises it by `safe_z − 68`, so:

```
held-cap underside  = 55 + (safe_z - 68) = safe_z - 13
neighbouring cap top= 68
clearance           = safe_z - 81
```

| `safe_z` | held-cap clearance | bare nozzle during capper legs |
|---|---|---|
| 84 (proposed) | **3 mm** | deck 68.065 |
| 87 (as run) | 6 mm | deck 71.065 |
| 89 (max unpatched) | 8 mm | deck 73.065 |
| 115 (needs the hover-clamp patch) | 34 mm | deck 99.065 |

Both reported symptoms — caps knocked off by neighbours, nozzle close to the
rail — get **worse** as `safe_z` goes down. `safe_z: 84` halves the clearance
that already failed.

The park leg is the one that matters: `decap` ends with a raw
`gantry.move(instrument, (park_x, park_y, safe_z))` (`commands/capper.py:223`),
and with `park_position: [206, 50]` on the vial column that is a pure-Y
traverse **past every lower-numbered vial while holding a cap**. Only vertical
clearance can fix it; no park XY makes the column traverse go away.

## 2. `working_volume.z_max: 129` is 5 mm outside the machine

Read live from the controller, 2026-08-31 (unchanged from 2026-08-28):

```
$20=1  $21=0  $22=1  $23=0  $130=409.000  $131=309.000  $132=124.000
<Alarm|WPos:409.000,309.000,124.000|WCO:-409.000,-309.000,-124.000>
```

`$132 = 124`, and `WCO = -max_travel`, so reachable deck-frame Z is `[0, 124]`.
`z_max: 129` is 5 mm past that, with `$20=1` — any move above 124 soft-limit
alarms. `z_max` is also what `validate_setup` bounds-checks against, so
raising it past the real travel removes the guard that would have caught it.
(`cnc.factory_z_travel_mm: 129.0` is the mechanical figure; the controller is
calibrated to 124.)

Constraint chain, unpatched:

```
tipped hover needs   safe_z + 35 <= z_max
controller allows    z_max <= 124
                 =>  safe_z <= 89
```

So **`z_max: 124`, `safe_z: 89`** is the best available without patching
CubOS, and it buys 2 mm over the run that failed. To go higher, the tipped
hover has to stop being pinned to `safe_z + 35` — that is exactly what
`patches/tipped-hover-clamp-and-ceiling-travel.patch` does (clamp the hover to
the highest reachable carriage plane instead of refusing), after which
`safe_z` can rise to ~115 and the clearance goes to 34 mm.

## 3. The plunger: commands were sent and acknowledged; absolute moves did nothing

The pipette was genuinely live. Loading the exact gantry file the run used,
without connecting:

```
instrument connect order: ['vial_capper_decapper', 'pipette']
--- pipette ---   class OpentronsPipette   _offline False   port /dev/ttyACM0
   model p20_single_gen2 | max_volume 20.0
   zero/prime/blowout/drop: 0.0 5.0 7.0 10.0
   mm_to_ul 0.025 -> 20 uL = 0.5 mm
```

`connect_instruments()` connects every instrument and the run did not abort,
so `OpentronsPipette.connect()` opened the port, got a parseable STATUS, and
returned — the Pi-to-Arduino link is fine.

### The measurement: identical gantry move, different plunger command

`aspirate` and `blowout` are each preceded by the same 47 mm descent
(Z 122 -> Z 75). From `mill_control.log`:

| step | preceding move | gap to next G-code | plunger command | attributable |
|---|---|---|---|---|
| aspirate vial_1 | Z122 -> Z75 | **8.068 s** | `12` ASPIRATE 0.5 mm (relative) | **~5.9 s** |
| blowout vial_2 | Z122 -> Z75 | **2.216 s** | `11` MOVE_TO 7.0 (absolute) | **~0.0 s** |
| pick_up_tip | Z87 -> Z60 (27 mm) | 2.215 s | `11` MOVE_TO 0.0 | ~0.1 s |
| drop_tip | Z122 -> Z95 (27 mm) | 2.324 s | `11` MOVE_TO 10.0 then 5.0 | ~0.1 s |

Same preceding motion, 5.85 s apart. **Command 12 (relative aspirate) runs the
stepper for seconds. Command 11 (absolute MOVE_TO) returns in ~0.1 s whatever
the target — 0 mm, 5 mm, 7 mm, 10 mm.** A round trip independent of commanded
distance is not a slow move; it is no move.

That accounts for the symptoms exactly: `blowout`, `drop_tip` and `pick_up_tip`
are all absolute `MOVE_TO`, so none of them did anything. `aspirate` is the one
command that did run, and at `mm_to_ul: 0.025` it commanded 0.5 mm of plunger
for a nominal 20 uL — small enough to miss.

### The plunger was never homed, and CubOS could not tell

The instrument-connect window (last `$$` before homing, to `$H`) is
**12.4 s** for both instruments:

```
11:35:15,645  $$          <- gantry setup done, connect_instruments() begins
11:35:28,050  $H          <- protocol starts
```

The capper's boot-banner wait alone is 3.80 s (measured again today) and the
pipette's `connect()` spends a fixed `sleep(2.0)` plus at least 0.6 s of
drain before its first query. That leaves under ~6 s for `home()` + `prime()`,
against the driver's own note that "full 55 mm travel at the default velocity
takes ~35 s". No homing pass happened.

CubOS cannot notice: `OpentronsPipette.home()` sets `self._is_homed = True`
unconditionally after the command returns and never re-reads the firmware's
`homed` flag. The Arduino still reports `homed: 0` today.

**This is the likely reason absolute moves no-op**: with no homing reference
the firmware has no valid absolute frame, while a relative aspirate still
steps. Confirming that needs a bench pass with the plunger visible —
`cubos/tools/pipette_bench_check.py --move`.

### `max_vol` disagrees with `pipette_model`

```
cmd 14 (plunger STATUS) -> OK:{"homed":0,"pos":0.00,"max_vol":300.00}
```

The firmware says 300 uL; the gantry YAML says `p20_single_gen2` (max 20 uL).
Every plunger constant CubOS is using for a p20 is marked `# placeholder` in
`instruments/pipette/models.py` — `prime 5.0`, `blowout 7.0`, `drop_tip 10.0`,
`mm_to_ul 0.025`. The p300 entry is marked "calibrated from PANDA-BEAR":
`prime 36.0`, `blowout 46.0`, `drop_tip 60.0`, `mm_to_ul 0.1098`.

So even once the plunger moves, `drop_tip` at 10 mm is nowhere near the 60 mm
a p300 ejector needs. Settle which pipette is mounted before any volume means
anything.

## 4. Sharing `/dev/ttyACM0` — real, but not the cause here

Upstream's own docstring for the shared link (`instruments/controllers/pawduino.py`,
landed at `1a9987f`, 2026-08-20 — **after** the Pi's `cbc33dc`):

> One Arduino serves several instruments (capper, pipette, lights) over one
> serial port, and **opening the port twice resets the board mid-session**.

The Pi's checkout has no `PawduinoLink`: each driver opens its own
`serial.Serial`, capper first then pipette, so the second open can reset the
board under the first driver and the two share one reply stream unarbitrated.
It is a real fragility and updating past `1a9987f` fixes it. It is not what
stopped the plunger — the Arduino answered every command it was given.

## Verification commands used (all read-only)

```bash
# instrument introspection: offline Gantry, connect() never called
python - <<'EOF'
from cubos.gantry.gantry import Gantry
from cubos.gantry.instrument_loader import load_instrumented_gantry_from_yaml
g = load_instrumented_gantry_from_yaml("/tmp/gantry_conv.yaml", Gantry(offline=True))
...
EOF

# controller + Arduino status, queries only
python -m cubos.tools.pipette_bench_check /dev/ttyACM0
```
