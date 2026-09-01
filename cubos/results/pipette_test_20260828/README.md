# pipette_test.yaml, 2026-08-28 revision — offline audit, no hardware run

Requested on PR #171 by @benwhitney5463: run the attached trio, with the
protocol changed to aspirate in vial_1, recap vial_1, decap vial_2, blow out
in vial_2, then drop the tip. Ben's note: *"don't worry about ensuring the
tip has been dropped. I am watching the machine, and will manually remove
the tip mid-run if needed."*

**Nothing was sent to the CubXL.** The Pi was off the tailnet for the whole
session (`Online: false`, last seen `2026-08-28T00:26:57Z`, ~35 minutes
before the request). The runner reached the tailnet fine — this was the Pi,
not the workflow.

That turned out not to be the limiting factor: **the trio as attached drives
the attached tip into vial_1**, and both offline gates say it is fine.

## Result summary

| configuration | validate_setup | `--mock` | `passive_shadow` | `--tip-stuck` |
|---|---|---|---|---|
| as attached (`safe_z 87`, park `[125, 50]`, stock CubOS) | PASS | 19/19 | **4 interferences** | **25** |
| `cub_xl_ben_pipette_capper_tipsafe.yaml` (`safe_z 122`, park `[206, 50]`) + hover-clamp patch | PASS | 19/19 | **0** | **0** |

Deck and protocol files are identical between the two rows. The whole
difference is two values in the gantry file plus one patch on the Pi.

## The failure

`validate_setup` and `run_protocol --mock` only ever check the instrument a
command *names*. The CubXL carries two rigidly coupled tools, so the other
one is dragged through the deck on every move and nothing upstream models
it. Sweeping it explicitly (`cubos/tools/passive_shadow.py`, added in this
commit) against the attached config:

```
step  5 cap       moving=PawduinoCapper   passive=pipette (tip=on)
     -> vial_1: 0.0 mm from its axis, tool point down to Z 36.065 vs obstacle top 55.0
     (206.0, 27.0, 36.06) -> (258.0, 27.0, 36.06)
step  5 cap       moving=PawduinoCapper   passive=pipette (tip=on)
     -> vial_1: 12.0 mm from its axis, tool point down to Z 36.065 vs obstacle top 68.0
     (258.0, 39.0, 36.06) -> (177.0, 39.0, 36.06)
step  6 decap     moving=PawduinoCapper   passive=pipette (tip=on)
     -> vial_2: 2.0 mm from its axis, tool point down to Z 36.065 vs obstacle top 68.0
     (177.0, 62.0, 36.06) -> (258.0, 62.0, 36.06)
step  6 decap     moving=PawduinoCapper   passive=pipette (tip=on)
     -> vial_2: 12.0 mm from its axis, tool point down to Z 36.065 vs obstacle top 55.0
     (258.0, 72.0, 36.06) -> (177.0, 72.0, 36.06)
```

The first is the one that ends the run. After `aspirate` the tip is 15 mm
inside vial_1 at deck Z 40. `cap`'s approach is `move_to_labware`, which
lowers to the **capper's** travel plane at the **current XY** — gantry
71.065, tip end 36.06, i.e. *deeper* — and only then translates X. The tip
is dragged sideways through the vial neck 19 mm below the rim. The other
three sweep the tip 32 mm below the cap tops.

### Correction to earlier notes in this repo

Comments on 2026-08-26 and 2026-08-27 described capper legs as diagonals and
gave lateral clearances computed that way (e.g. "0.9 mm from vial_2's
centre"). Motion is **axis-by-axis, never diagonal** —
`gantry_driver/driver.py::_build_direct_move` emits one G01 per changed axis
in X→Y→Z order, `_build_transit_move` does lift→X→Y→descend, and the
docstring states the reason ("the mill never commands simultaneous
multi-axis motion"). The vertical clearances in those notes were right; the
path shape and the lateral numbers were not. Under the correct model the
passive nozzle passes **12 mm** from the axis of the vial the capper is
working on — inside its 14 mm radius — which is why the interference is
real, just not where it was previously said to be.

## Why no config value fixes it

`safe_z` is a single number shared by both tools and applied at each tool's
own point. A 35 mm tip puts the pipette's tool point 50.935 mm below the
capper's (35 mm tip + the capper's `depth: -15.935`):

| requirement | constraint |
|---|---|
| `aspirate`/`blowout`/`drop_tip` hover: gantry = `safe_z` + 35 ≤ `z_max` 122 | `safe_z` ≤ 87 |
| capper legs clear the cap tops (deck 68) with the tip on: `safe_z` − 50.935 ≥ 68 | `safe_z` ≥ 119 |

Empty by 32 mm. `safe_z: 87` is correct for the half it was chosen for and is
exactly what makes capper motion lethal to an attached tip. Raising it is not
available either — `GantryYamlSchema` rejects `safe_z` above `z_max`:

```
Value error, cnc.safe_z (130.0) must be within [0.0, 122.0]
```

## The fix that was verified

`cubos/configs/gantry/cub_xl_ben_pipette_capper_tipsafe.yaml` — `safe_z:
122.0`, capper `park_position: [206, 50]` — **plus**
`cubos/patches/tipped-hover-clamp-and-ceiling-travel.patch` applied to the
Pi's CubOS. Neither half works without the other.

* The patch decouples the tipped hover from `safe_z` (clamping it to the
  highest carriage-reachable plane) and rides XY travel at the
  working-volume ceiling, so capper transits carry the tip end at deck 87 —
  19 mm over the caps — while a tipped engage still clamps to gantry 122,
  the plane Ben verified by eye on 2026-08-25.
* Park on the vial column turns every capper leg into a pure-Y move holding
  the passive nozzle at deck X 258: 38 mm clear of the vials (edge 220), 22
  mm clear of the rack body (~280). The park leg is a *raw* move, so it does
  not get the patch's ceiling travel — this is what covers it.

The `--tip-stuck` row is the one that matters for Ben's instruction not to
gate the run on the tip actually coming off. Under this configuration that
is genuinely safe. Under `safe_z: 87` a stuck tip is 25 interferences,
including dragging through the tip rack on step 9's approach.

## `drop_z: 60` — no motion effect, and it shrinks the rack's model

At `cbc33dc` and on current CubOS `main`, `drop_z` is read in exactly one
place, `deck/labware/tip_rack.py:158-160`, and it is not a motion target:

```python
if pickup_z is not None and drop_z is not None:
    data["height"] = max(round(abs(pickup_z - drop_z), 3), 1.0)
```

With `pickup_z: 60` and `drop_z: 60` that is `abs(0)` → clamped to **1.0 mm**,
overriding the explicit `height: 22` and collapsing the rack's modeled
bounding box. `drop_tip` engages the **tip end** to the rack's `location.z`
60 (gantry 95); a seated tip has its end at deck 25, so the ejector fires one
full tip-length above the slot. Recommendation: revert to `drop_z: null` and
add a `tip_disposal` entry, which is what `drop_tip` is designed to target.

## Still unverified — needs eyes on the machine

* **Deck strip x ≈ 240–275, y ≈ 15–205, clear from deck Z ≈ 17 up.** During
  every capper engage the passive pipette descends to gantry 52.065; with a
  tip on that is a tip end at deck Z 17.065 at `(258, vial_y + 12)`. Vial
  holders, brackets and cabling are not in the deck file, so no offline
  check — including `passive_shadow` — can see them.
* `pickup_z: 60.0` is still the 2026-08-06 number, never re-jogged.
* The capper Arduino reports `max_vol 300` while the config says
  `p20_single_gen2` (`mm_to_ul: 0.025`), so `volume_ul: 20.0` commands 0.5 mm
  of plunger travel, not 20 µL.
* GRBL `$20` (soft limits) was found disabled on 2026-08-27 after an
  interrupted calibration and restored to 1. Re-check it before any run.

## Files

| | |
|---|---|
| `validate_recommended.log` | `validate_setup` on the recommended trio — PASS, 19 steps |
| `mock_recommended.log` | `run_protocol --mock` — 19/19 |
| `shadow_recommended.log` / `shadow_recommended_tipstuck.log` | 0 interferences, both modes |
| `shadow_asattached.log` / `shadow_asattached_tipstuck.log` | 4 and 25 interferences |
| `validate_asattached.log` | PASS — the gate that misses all of it |

Reproduce (CubOS `cbc33dc` + the three patches in `cubos/patches/`):

```bash
C=~/byu-vcl/cubos/configs
python -m cubos.tools.validate_setup       $C/gantry/cub_xl_ben_pipette_capper_tipsafe.yaml $C/deck/ben_6vials_tiprack.yaml $C/protocol/vcl/pipette_test.yaml
python -m cubos.tools.run_protocol --mock  $C/gantry/cub_xl_ben_pipette_capper_tipsafe.yaml $C/deck/ben_6vials_tiprack.yaml $C/protocol/vcl/pipette_test.yaml
python -m cubos.tools.passive_shadow       $C/gantry/cub_xl_ben_pipette_capper_tipsafe.yaml $C/deck/ben_6vials_tiprack.yaml $C/protocol/vcl/pipette_test.yaml --tip-stuck
```

## Second blocker, found on the machine: the controller's travel extents moved

The Pi came back on the tailnet at 01:19 UTC. Before commanding anything I
read the controller (`grbl_settings_20260828.json`, full `$$` dump). Every
setting in `grbl_settings` matches **except the three travel extents**, and
all three are in `_validate_grbl_settings`' critical set, so `run_protocol`
would abort at connect with *"Critical GRBL settings mismatch — motion would
be wrong"* before any motion:

| | config | controller | delta |
|---|---|---|---|
| `$130` `max_travel_x` | 389.333 | **409.000** | +19.667 |
| `$131` `max_travel_y` | 235.000 | **309.000** | +74.000 |
| `$132` `max_travel_z` | 125.000 | **124.000** | −1.000 |

```
<Alarm|WPos:409.000,309.000,124.000|FS:0,0|WCO:-409.000,-309.000,-124.000>
$20=1  $21=0  $22=1  $23=0  $27=3  $100=$101=$102=400
```

`to_machine_coordinates` is a pass-through (`gantry/coordinate_translator.py`
— it normalises, it does not translate), so the deck frame is defined
entirely by the controller's WCO, and the WCO is `-max_travel` on each axis.
**Changing `$131` from 235 to 309 therefore moved the deck's Y origin by
74 mm**: the same physical point now reads 74 mm higher in WPos than it did
before the recalibration.

That is consistent with the X axis and *not* with the Y axis of the new deck
file:

* `$130` moved **+19.667** and every vial's `location.x` moved **187 → 206
  (+19)**. That is the same holder re-read in the new frame. Consistent.
* `$131` moved **+74** but every vial's `location.y` moved only **+1**
  (26/59/92/125/158/191 → 27/60/93/126/159/192).

So either the holder was physically moved ~73 mm in −Y at the same time, or
the Y column was not re-measured in the new frame. If it is the latter, the
vials are physically at deck Y ≈ 100/133/166/199/232/265 and every `decap`
would descend 73 mm short of its vial — and vial_6 at 265 would be outside
the config's `working_volume.y_max: 232` entirely.

Not something to resolve by running it. **No motion was commanded.**

Whatever the answer, `grbl_settings.max_travel_x/y/z` in the gantry file has
to be updated to 409.0 / 309.0 / 124.0 before anything can connect. Note that
`$132: 124` also means the reachable deck-frame Z is `[0, 124]`, so
`working_volume.z_max: 122.0` still has 2 mm of headroom and the tipped hover
at gantry 122 remains reachable.

### Machine state — untouched

| | |
|---|---|
| Motion | none commanded; no homing, no protocol run |
| GRBL | `Alarm` (the board resets when the port is opened) — re-home before any run |
| `$20` soft limits | `1` — still set, unlike 2026-08-27 |
| Electromagnet / cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Pipette plunger | `OK:{"homed":0,"pos":0.00,"max_vol":300.00}` — reports 300 µL, config says `p20_single_gen2` |
| Ports | `/dev/ttyUSB0` CH340 → gantry · `/dev/ttyACM0` Arduino Uno → capper+pipette; both free |
| `~/CubOS` | `cbc33dc`, both Pi patches still applied; hover-clamp patch **not** applied |
| Pi uptime | booted 2026-08-27 06:11 — the 00:26–01:19 dropout was the network, not a reboot |

## Where the branch's trio stands now (rev 2 + both corrections)

Re-verified independently against the Pi's exact CubOS after the rev-2
corrections landed:

| gantry config | CubOS | validate | mock | shadow | `--tip-stuck` |
|---|---|---|---|---|---|
| `cub_xl_ben_pipette_capper.yaml` (`safe_z 87`, park `[206, 50]`) | Pi's, stock | PASS | 20/20 | **0** | **3** |
| `cub_xl_ben_pipette_capper_tipsafe.yaml` (`safe_z 122`, park `[206, 50]`) | + hover-clamp patch | PASS | 20/20 | **0** | **0** |

The 3 residual ones are all step 10 (`cap vial_2`) against `tip_rack.A1`/`A2`:
`drop_tip` clears the modeled tip extension unconditionally, so if the tip did
not physically leave, the following capper approach drags it through the rack
at deck Z 36.065 against tips topping out at 60. There is no config fix for
that at `safe_z: 87`; the hover-clamp route removes it because capper
transits then ride the ceiling.

That matters here specifically because Ben asked not to gate the run on
confirming the tip came off.

### Why `grbl_settings` was deliberately left stale

Updating `max_travel_x/y/z` to 409/309/124 is the one-line change that lets a
run connect — and it is exactly the guard that is currently stopping a run
whose deck Y frame is unresolved. Left as-is on purpose. Update it *after*
the Y question above is settled, not before.
