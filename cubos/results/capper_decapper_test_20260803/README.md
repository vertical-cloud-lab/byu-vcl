# capper_decapper_test on the CubXL — 2026-08-03

Three hardware attempts at `cubos/configs/protocol/vcl/capper_decapper_test.yaml`
against the lab CubXL. The last two were aborted by the capper's capture
interlock at `decap` of `vial_holder.vial_2`.

| attempt | time (UTC) | gantry config | outcome |
|---|---|---|---|
| 1 | 19:29 | `safe_z: 105.0` | died at capper connect — Pawduino boot-banner bug (fixed, see `cubos/patches/`); 0 steps, no motion |
| 2 | 19:31 | `safe_z: 105.0`, `travel_z: 105.0` | homed, parked, approached vial_2, `decap` aborted — sensor did not confirm capture. Pipette nozzle brushed the cap tops during capper transit |
| 3 | 19:47 | `safe_z: 115.0`, `travel_z: 111.0` | transit clearance fixed; `decap` aborted identically — sensor did not confirm capture |

`run_hardware_attempt3.log` is attempt 3's full stdout/stderr. (It is
force-added: the repo `.gitignore` has a blanket `*.log` rule, which is why
the attempt-2 log referenced in commit `86ebf48` never actually landed.)

## Root cause of the decap failure: the engage plane is ~38 mm too low

`decap` descends to `vial.location.z + capper.engage_depth_mm`
(`protocol_engine/commands/capper.py:204`). With this deck and gantry that is:

```
vial_holder.location.z                       39.0   (deck YAML)
+ labware_seat_height_from_bottom            18.0   (ursa_vial_holder/9VialHolder.yaml)
= Vial.location.z  (resolve_coordinate)      57.0
+ engage_depth_mm                           -15.0
= capper tool-plane target                   42.0   -> gantry Z 17.0
```

The gantry Z is 25 mm lower than the capper tool plane because the capper is
configured `depth: -25.0`, i.e. its socket sits 25 mm **above** the gantry
datum. The pipette is `depth: 0.0`, so the pipette nozzle *is* the gantry
datum and hangs 25 mm below the capper socket — which is why the pipette, not
the capper, was the part that fouled the caps during capper transit.

That gives an independent measurement of the cap height. On attempt 2
(`safe_z: 105.0`) the capper transited at gantry Z 80, putting the pipette
nozzle at deck Z 80, and the nozzle **brushed the cap tops**. At `safe_z:
115.0` (gantry Z 90) it cleared. So the cap tops sit at roughly deck Z 80,
while `decap` is driving the capper socket to deck Z 42 — about 38 mm past
them.

`engage_depth_mm: -15.0` is not a measured value. It is
`CAPPER_ENGAGE_DEPTH_MM`, the placeholder in
`tools/panda_bear_import/constants.py`, whose own comment reads "never
measured against real PANDA hardware; confirm/recalibrate before trusting
physical motion." Same provenance as the `[-10.0, -10.0]` park position.

### The knob

```
capper socket target Z = vial_holder.location.z + 18.0 + engage_depth_mm
gantry Z               = capper socket target Z - 25.0
```

Changing `engage_depth_mm` alone is the minimal fix and leaves the deck file
describing physical geometry. To put the socket at deck Z *S*:

```
engage_depth_mm = S - 57.0
```

e.g. `S = 78.0` (2 mm onto a cap topping out near 80) gives
`engage_depth_mm: +21.0`. The sign flip is expected: a magnet-on-top capper
engages *above* the vial rim, not below it, so a negative depth can never be
right for this head. The exact number needs the measured cap-top height.

## Z ceiling: `safe_z: 115.0` is 1 mm outside the machine's travel

Read off the controller on 2026-08-03:

```
$20=1 (soft limits on)   $21=0   $23=0 (home to max)   $132=114.000
<Alarm|WPos:383.000,238.000,114.000|WCO:-383.000,-238.000,-114.000>
```

`WPos = MPos + 114`, and GRBL's reachable `MPos` Z is `[-114, 0]`, so the
reachable deck-frame Z is **`[0, 114]`**. `working_volume.z_max: 115.0` and
`cnc.safe_z: 115.0` are both above that.

This protocol still runs because every `safe_z` move belongs to the capper
(`depth: -25.0` → gantry Z 90) and the pipette moves use an explicit
`travel_z: 111.0`. The highest gantry Z actually commanded is 111.0. But:

* any `move` of the **pipette** at `safe_z` (a deck-target `move`, `measure`,
  `aspirate`, `scan` — anything routed through `move_to_labware`) commands
  gantry Z 115 and will trip a soft-limit alarm;
* `working_volume.z_max: 115.0` is what `validate_setup` bounds-checks
  against, so it no longer catches that;
* the post-failure retract in `protocol_engine/setup.py:377` would do exactly
  that if the `PawduinoCapper` name bug noted in `cubos/patches/README.md`
  were ever fixed.

Setting `z_max` and `safe_z` to `114.0` restores the guard and costs 1 mm of
capper transit clearance.

## Machine state after the run

| | |
|---|---|
| Capper head | retracted to `safe_z` — last pose `(162.0, 39.0, 115.0)` → gantry `(162.0, 39.0, 90.0)` |
| Electromagnet | off — `CMD_EMAG_OFF` sent, `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held |
| GRBL | `Alarm` (board resets when the port closes); re-home before the next run |
| Ports | `/dev/ttyUSB0` CH340 → gantry · `/dev/ttyACM0` Arduino Uno → capper |

The Pawduino boot-banner patch (`cubos/patches/`) is still applied to
`~/CubOS` on the Pi (CubOS `cbc33dc`); the capper connected cleanly on both
runs.
