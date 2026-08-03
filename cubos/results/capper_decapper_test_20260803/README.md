# capper_decapper_test on the CubXL — 2026-08-03

Seven hardware attempts at `cubos/configs/protocol/vcl/capper_decapper_test.yaml`
against the lab CubXL. **Attempts 6 and 7 completed all 27 steps**: six vials
each decapped, entered with the pipette, and recapped.

| attempt | time (UTC) | change | outcome |
|---|---|---|---|
| 1 | 19:29 | `safe_z: 105.0` | died at capper connect — Pawduino boot-banner bug (patched, see `cubos/patches/`); 0 steps, no motion |
| 2 | 19:31 | `travel_z: 105.0` | homed, parked, approached vial_2, `decap` aborted — capture not confirmed. Pipette nozzle brushed the cap tops during capper transit |
| 3 | 19:47 | `safe_z: 115.0`, `travel_z: 111.0` | transit clearance fixed; `decap` aborted identically |
| 4 | 20:11 | `engage_depth_mm: -15.0 → +28.0` | `decap` aborted identically — the head stopped 12 mm short |
| — | 20:15 | `probe_cap_plane.py` | **measured** the engage plane with the head's own sensor: beam broke at gantry Z 48.0 |
| 5 | 20:18 | `engage_depth_mm: +15.0` | **`decap` succeeded**, pipette entered vial_2 and retracted, `cap` aborted — release not confirmed |
| 6 | 20:21 | `cap-release-confirm-after-retract.patch` | **PASS — 27/27 steps, vials 2–7 decapped, entered, recapped** |
| 7 | 20:50 | Ben's re-measured deck Y, `safe_z`/`z_max` 114.0, `engage_depth_mm: 13.0`, `park_position: [125, 50]`, insert Z 40.0 | **PASS — 27/27 steps, 6m 51s, campaign 13 `completed`** |

Logs: `run_hardware_attempt{3,4,5,6,7}.log` and `probe_cap_plane.log`. All
force-added — the repo `.gitignore` has a blanket `*.log` rule. Campaign CSVs
are in `cubos/results/campaign_11_20260803_202120/` (attempt 6) and
`cubos/results/campaign_13_20260803_205035/` (attempt 7).

## What was actually wrong: the engage plane, and it could not be derived

`decap`/`cap` descend to `vial.location.z + capper.engage_depth_mm`
(`protocol_engine/commands/capper.py:204`). Both terms were wrong, in a way
that no amount of reading configs could resolve:

```
vial_holder.location.z                       39.0   (deck YAML)
+ labware_seat_height_from_bottom            18.0   (ursa_vial_holder/9VialHolder.yaml)
= Vial.location.z  (resolve_coordinate)      57.0   <- CubOS calls this "the vial rim"
+ engage_depth_mm                           -15.0
= capper tool-plane target                   42.0   -> gantry Z 17.0
```

* **57.0 is not the rim.** Ben measured the vial tops at deck Z **85**, ~28 mm
  higher. The deck YAML's Z column does not describe this machine.
* **`depth: -25.0` is not the socket height either.** The sensor probe put the
  seated cap at capper deck Z 73.0, i.e. gantry Z 48.0 — so the physical socket
  face is ~12 mm *above* where `depth` says the tool point is.

Because the two errors add, an estimate built from either number alone misses.
Attempt 4 used Ben's 85 mm directly (`engage_depth_mm: +28.0`, gantry Z 60) and
still failed, 12 mm short.

### The measurement that settled it

`cubos/tools/probe_cap_plane.py` steps the head down over one vial in 1 mm
increments with **the magnet off**, polling the line-break sensor, and stops at
the first beam break. That finds the plane at which a cap is seated in the head
directly — independent of both `depth` and the deck YAML:

```
  gantry Z   49.0  (capper deck Z   74.0)  cap_present=False
  gantry Z   48.0  (capper deck Z   73.0)  cap_present=True

BEAM BROKE at gantry Z 48.0 (capper deck Z 73.0).
  engage_depth_mm = 73.0 - 57.0 = 16.0
```

`engage_depth_mm: 15.0` is that minus 1 mm of seating margin. The descent was
bounded at gantry Z 17.0 — the lowest this machine had already been driven to
over a vial, on attempts 2 and 3 — so the sweep stayed inside territory the
machine had already traversed.

The sign flip off the `-15.0` placeholder is expected: a magnet-on-top head
engages *above* the vial, so a negative depth can never be right for it.
`-15.0` is `CAPPER_ENGAGE_DEPTH_MM` from `tools/panda_bear_import/constants.py`,
whose own comment reads "never measured against real PANDA hardware".

## Second blocker: `cap` could never confirm a release

With the engage plane right, `decap` worked on the first try and the pipette
entered vial_2 — then `cap` aborted with `cap_present=True, expected False`.
The cap had in fact been placed back correctly: reading the sensor by hand with
the head parked at `safe_z` returned `False`, nothing held.

`_run_capper_sequence()` confirms **before** retracting, for both directions.
The line-break sensor reports a cap anywhere in the beam, held or not — the
probe proved that by tripping it on a cap merely *resting* on a vial — so at
the engage plane a just-released cap is still in the beam and `cap` can never
pass. Patched locally
(`cubos/patches/cap-release-confirm-after-retract.patch`); details there.

## Resolved in attempt 7: `safe_z: 115.0` was 1 mm outside the machine's travel

Read off the controller:

```
$20=1 (soft limits on)   $23=0 (home to max)   $132=114.000
<Alarm|WPos:383.000,238.000,114.000|WCO:-383.000,-238.000,-114.000>
```

`WPos = MPos + 114` and GRBL's reachable `MPos` Z is `[-114, 0]`, so the
reachable deck-frame Z is `[0, 114]`. `working_volume.z_max: 115.0` and
`cnc.safe_z: 115.0` are both above it.

This protocol runs anyway because every `safe_z` move belongs to the capper
(`depth: -25.0` → gantry Z 90) and the pipette moves carry an explicit
`travel_z: 111.0`; the highest gantry Z commanded in the successful run is
111.0. But any *pipette* move at `safe_z` — a deck-target `move`, `measure`,
`aspirate`, `scan` — would command gantry Z 115 and trip a soft-limit alarm,
and `z_max: 115.0` is what `validate_setup` bounds-checks against, so it can no
longer catch that. Setting both to `114.0` restores the guard at the cost of
1 mm of capper transit clearance.

Ben set both to `114.0` before attempt 7, which ran clean. The capper now
transits with its tool point at deck Z 114 — see the next section for what
that means for the pipette.

## The pipette shadow — why the probe dragged the nozzle on the X rail

Reported by Ben after attempt 6: `probe_cap_plane.py` dragged the pipette along
the X rail. The cause is not specific to the probe. The two instruments are
rigidly coupled on one head:

| | `offset_x` | `offset_y` | `depth` |
|---|---|---|---|
| `vial_capper_decapper` | 0.0 | 0.0 | −25.0 |
| `pipette` | +135.0 | +20.0 | 0.0 |

`gantry = deck − offset` in XY and `gantry_z = deck_z + depth`, so whenever the
capper's tool point is commanded to deck `(x, y, z)`, the pipette nozzle is at
deck:

```
(x + 135, y + 20, z - 25)
```

The nozzle is the lowest thing on the head and it hangs 135 mm to +X of the
capper. Every capper move therefore sweeps the nozzle through a plane 25 mm
below the capper's own, a third of the bed away in X:

| capper action | capper tool point | nozzle deck position |
|---|---|---|
| transit at `safe_z: 114.0` | Z 114 | Z **89** |
| engage at `engage_depth_mm: 13.0` over vial_N (deck X 162) | Z 70 | (297, y+20, **45**) |
| probe's deepest step (attempt 6) | Z 73 | (297, 56, **48**) |

So the probe's lowest nozzle plane was Z 48, and **the protocol's own
`decap`/`cap` steps go to Z 45 — 3 mm lower — twelve times per run.** Whatever
the nozzle contacted during the probe, it contacts during a normal run too; the
probe only made it visible by descending in 1 mm steps with a sensor poll (and
a visible pause) at each one.

Nothing offline models this. `validate_setup` bounds-checks the *commanded*
instrument against the working volume and checks the built-in Cub XL rail
boxes, but it has no model of a second instrument's swept volume, and deck
X 297 is nowhere near the modeled `X[480, 540]` right-rail box.

If deck X ≈ 297 is where the rail sits, the options are to raise
`engage_depth_mm` (each +1 mm lifts the nozzle 1 mm), shorten the pipette's
`offset_x`, or shim the pipette up so its `depth` is no longer 0.0 — the last
being the only one that buys clearance without moving the engage plane.

## Machine state after attempt 7

| | |
|---|---|
| Protocol | completed, `home` as the final step |
| Electromagnet | off — `release_cap()` sent explicitly after the run |
| Cap sensor | `cap_present=False` — nothing held |
| Caps | all six returned to vials 2–7 by the protocol's own `cap` steps |
| GRBL | resets to `Alarm` when the port closes; `run_protocol` clears it and homes at startup |
| Ports | `/dev/ttyUSB0` CH340 → gantry · `/dev/ttyACM0` Arduino Uno → capper |

Both patches in `cubos/patches/` are applied to `~/CubOS` on the Pi (CubOS
`cbc33dc`). Neither is upstreamed yet.
