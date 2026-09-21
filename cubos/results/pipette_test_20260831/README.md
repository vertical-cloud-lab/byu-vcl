# pipette_test on the CubXL — 2026-08-31 — 18/18 steps, PASS

Requested by @benwhitney5463 on PR #171. **First run in which the pipette's own
`aspirate` / `blowout` / `drop_tip` commands executed on hardware**, and the run
that resolved the deck-frame ambiguity left open on 2026-08-28.

| | |
|---|---|
| Campaign | 33 — `campaign_33_20260831_173506` |
| Window | 2026-08-31 17:35:06 → 17:39:45 UTC (**4m 39s**) |
| Status | `completed`, 18/18 steps |
| Retries / warnings / alarms | none (only the routine "GRBL is in Alarm state after connect" pair) |
| CubOS | `~/CubOS` @ `cbc33dc` + `pawduino-connect-boot-banner` + `cap-release-confirm-after-retract`. Hover-clamp patch **not** applied and not needed. |

Sequence: `home` → capper to park → decap vial_1 → `pick_up_tip` A1 → `aspirate`
in vial_1 → pipette retract → cap vial_1 → decap vial_2 → `blowout` in vial_2 →
`drop_tip` → cap vial_2 → decap+cap vials 3, 4, 5 → `home`.

## The question this run answered

On 2026-08-28 the deck file's vial Y column could not be reconciled with the
controller. The recalibration moved `$131` (`max_travel_y`) 235 → 309, and
`to_machine_coordinates` is a pass-through — it normalises, it does not
translate (`coordinate_translator.py:54`) — so the deck frame *is* the
controller's work frame and `WCO = -max_travel` on every axis. Shifting `$131`
by 74 mm shifts the deck Y origin by 74 mm:

| | old deck | + frame shift → *predicted* | Ben's deck | |
|---|---|---|---|---|
| vial x | 187 | 206.7 | **206** | consistent |
| vial y | 26, 59, 92, 125, 158, 191 | 100, 133, … , 265 | **27, 60, … , 192** | 73 mm apart |
| vial z | 55 | 54 | **55** | 1 mm apart |

Either the holder had physically moved or the Y column was stale. That is not
resolvable remotely — there is no camera on the CubXL deck — but it *is*
resolvable by the machine, because `decap` is an interlocked probe:

* If the column were stale, `decap vial_1` would descend over bare deck at
  (206, 27) — gantry Z 52.065, ~52 mm above the deck surface, with the passive
  nozzle at deck (258, 39) also clear — fire the magnet in air, read
  `cap_present=False`, retry 3× and abort with the tool retracted to `safe_z`.
  A clean, bounded, self-diagnosing failure.
* If the column were current, it would capture and the run would continue.

**It captured on the first attempt, and all five vials decapped and capped with
zero retries.** The deck file describes the machine. The `z: 55` / 1 mm question
is not separately resolved — 1 mm is inside the capper's seating margin — but it
is no longer load-bearing.

## What had to change to run at all

`$130/$131/$132` are in `Gantry._validate_grbl_settings`' critical set, compared
at 0.001 mm. The gantry config still carried the pre-recalibration
389.333 / 235.0 / 125.0 while the controller reports 409 / 309 / 124 (read live
twice, 2026-08-28 and 2026-08-31, identical — see `grbl_settings_20260831.json`),
so **every** run aborted at connect with *"Critical GRBL settings mismatch —
motion would be wrong"* before a single G-code. Synced in the committed gantry
file. `working_volume` was deliberately left tighter (386.333 / 232 / 122) — it
is the envelope all the protocol geometry was validated against.

## The tip-rack anchor conversion

Ben measured the anchor with the **pipette tip** hovering over the corner tip,
but the jog display always reports the **reference instrument** — the capper,
offsets 0/0 — so `(284, 25.5)` is a raw work-coordinate reading. Deck
coordinates are instrument-independent (`gantry = deck - offset`), so:

```
(284 + 52.0, 25.5 + 12.0) = (336.0, 37.5)
```

Verified through the loader, not asserted — with the converted anchor,
`pick_up_tip: tip_rack.A1` commands the gantry to exactly **(284.0, 25.5, 60.0)**,
reproducing the measured point. Left unconverted it commands (232.0, 13.5):
52 mm and 12 mm short, which puts the *capper* over the rack and presses the
pipette into bare deck.

**`validate_setup` PASSES either way** (`validate_asattached.log`) — it only asks
whether a coordinate is reachable, never whether it is the right one.

## Verification matrix

| check | as attached (unconverted rack, stale GRBL) | as run (converted + synced) |
|---|---|---|
| `validate_setup` | PASS (12 targets) — but aims at the wrong point | **PASS** (12 targets) |
| `run_protocol --mock` | 18/18 | **18/18** |
| `passive_shadow` (nominal) | 0 | **0** |
| `passive_shadow --tip-stuck` | 3 | **3** (all step 10, into the tip rack) |
| hardware connect | **aborts** — critical GRBL mismatch | **ran, 18/18** |

## Commanded gantry coordinates (mock trace, reproduced on hardware)

```
capper transit / park      z  71.065     (safe_z 87 + depth -15.935)
capper engage over a vial  z  52.065     (rim 55 + engage_depth_mm 13, -15.935)
pick_up_tip tip_rack.A1    (284.000,  25.500,  60.000)   <- Ben's measured jog
tipped hover               z 122.000     (safe_z 87 + tip 35 = z_max exactly)
aspirate vial_1            (154.000,  15.000,  75.000)   tip end 15 mm in
blowout  vial_2            (154.000,  48.000,  75.000)   tip end 15 mm in
drop_tip tip_rack.A1       (284.000,  25.500,  95.000)   <- 35 mm above the slot
every capper pose          x = 206.000  (pure-Y legs; pipette held at deck 258)
```

`safe_z: 87` is what makes the tipped engage commands legal: they hover at
`safe_z` measured **at the tool point**, so with a 35 mm tip the carriage needs
`safe_z + 35` = 122, exactly `z_max`. At the old 114 that would be 149.

## Still open

* **`drop_tip` releases the tip 35 mm above the slot.** It descends the *tip end*
  to the rack's `location.z` 60 (gantry 95); a seated tip's end is at deck 25. It
  will not seat back in A1, and `commands/pipette.py` calls
  `clear_attached_tip_extension()` unconditionally, so from step 10 on CubOS
  plans bare-nozzle whatever happened. Ben's standing instruction is not to gate
  the run on this. Real fix: a `tip_disposal` deck entry plus a measured
  `drop_tip_position` (`models.py` has `10.0  # placeholder`).
* **`pickup_z: 60`** was not re-measured with the new anchor, and `$132` moved
  125 → 124, so a physically unmoved rack would now read 59. `pick_up_tip` is a
  friction press with no sensor — it cannot report a miss.
* **The plunger reports `max_vol: 300.00`** while the config says
  `p20_single_gen2`. `mm_to_ul: 0.025` is the p20 number, so `volume_ul: 20.0` is
  0.5 mm of plunger travel, not 20 µL. Worth settling which pipette is mounted.
* **`/dev/ttyACM0` is shared** by the capper and pipette drivers with no
  arbitration at `cbc33dc` (no `PawduinoLink`). Works in practice — three
  hardware runs now — but updating the Pi past upstream `1a9987f` fixes it.
* The capper parks over vial_2's footprint at deck Z 87; holding a ~13 mm cap its
  underside is ~6 mm above vial_2's cap top. Unmeasured. `[206, 5]` or
  `[206, 220]` clears every footprint and still sweeps clean.

## Machine state, left clean

| | |
|---|---|
| Protocol | completed, `home` as the final step |
| Electromagnet | off — `CMD_EMAG_OFF`, `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Caps | all five returned to vials 1–5 by the protocol's own `cap` steps |
| Plunger | `OK:{"homed":0,"pos":0.00,"max_vol":300.00}` (resets when the port re-opens) |
| GRBL | `Alarm` — normal, the board resets when the port closes. Re-home before the next run. |
| `$20` soft limits | `1` |
| Ports | `/dev/ttyUSB0` CH340 → gantry · `/dev/ttyACM0` Arduino → capper + pipette; both free |

No visual confirmation of the dropped tip or of cap seating — there is no camera
on this deck. Those need eyes.

## Files

| file | what it is |
|---|---|
| `run_hardware_20260831.log` | the hardware run, 18/18 |
| `validate_setup.log` / `mock.log` / `trace.log` | offline gates + commanded-gantry trace, as run |
| `shadow_nominal.log` / `shadow_tipstuck.log` | passive-instrument sweep, 0 and 3 |
| `validate_asattached.log` | the attachments unconverted — PASSES, aiming at the wrong point |
| `grbl_settings_20260831.json` | full `$$` dump read after the run |
| `../campaign_33_20260831_173506/` | campaign CSVs |
