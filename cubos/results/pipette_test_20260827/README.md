# pipette_test, 2026-08-27 — first hardware run with a tip inside a vial

@benwhitney5463 attached a revised `pipette_test.yaml` to PR #171 ("I changed
the protocol so the pipette tip actually enters the vial") and asked for a
hardware run. Steps 0–5 ran and completed. Steps 6–18 were not run: `drop_tip`
cannot return the tip to the rack, and every step after it is planned as if the
nozzle were bare.

## What ran

`pipette_test_partA.yaml` — steps 0–5 of the attachment, verbatim — against
`sterling_6vials_tiprack.yaml` and the attached gantry file with the capper's
`park_position` set to `[187.0, 50.0]`.

```
RESULT: PASS - protocol motion targets within gantry bounds
Protocol complete — 6 steps executed.
```

Campaign 25, `2026-08-27 23:50:49 → 23:52:30` UTC, status `completed`. No
warnings, no capture retries, no alarms. `decap` confirmed cap capture on the
first attempt.

| step | action | gantry commanded |
|---|---|---|
| 0 | `home` | — |
| 1 | capper → park_position | (187, 170, 64.065) |
| 2 | `decap vial_1` | approach 71.065 · engage **52.065** · retract 71.065 · park (187, 50) |
| 3 | `pick_up_tip tip_rack.A1` | hover (265, 1, 87) · press **(265, 1, 60)** |
| 4 | `mix vial_1 height=-15` | hover (135, 14, **122**) · engage (135, 14, **75**) |
| 5 | pipette → park_position | (135, 158, 115) |

Step 4 is the change under test. `mix` engages by descending the tool point to
`coord.z + height`; with the rim at deck 55 and a 35 mm tip that is tip-end
deck Z **40.0**, gantry Z **75.0** — 15 mm inside the vial, nozzle still 20 mm
above the rim. The tipped hover at gantry 122 is exactly `working_volume.z_max`,
which is what `safe_z: 87` buys (87 + 35 = 122).

## Machine state afterwards

| | |
|---|---|
| GRBL | `Alarm`, WPos at max — the board resets when the port closes. **Re-home before the next run.** |
| `$20` | **1** (restored, see below) · `$21=0` · `$22=1` · `$130/$131/$132` = 389.333 / 235.0 / 125.0 |
| Electromagnet | off — `CMD_EMAG_OFF` sent explicitly, `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| **vial_1** | **open** |
| **vial_1's cap** | **loose on the deck.** The protocol ends holding it; closing the port resets the Arduino and de-energizes the magnet, so it was released at the final pose — capper tool point deck ≈ (135, 158). Put it back by hand. |
| Pipette tip | **probably still on the nozzle.** `pick_up_tip` is a friction press with no sensor, and no camera looks at this deck. Confirm by eye and pull it off before any further capper motion. |

## `$20=0` — soft limits were disabled on the controller

Read live before running: `$20=0`, `$21=0`. `$20` is in
`Gantry._validate_grbl_settings`' critical set and the gantry file's
`soft_limits: true` maps to `$20=1` (`gantry/grbl_settings.py:43`), so **any**
run would have aborted at connect with *"Critical GRBL settings mismatch"*.

The cause is in `configure_soft_limits_from_spans`
(`gantry/gantry.py:618-632`): it writes `$20=0`, then `$130/$131/$132`, then
`$20=1`. Interrupted between the first and last write — an E-stop during
calibration does exactly this, and issue #182 was testing E-stops during
calibration — it leaves the machine with no software limit protection and no
sign of it. `session.py:903` has a matching error string ("Soft-limit restore
did not verify $20=1 on the controller"), so the failure mode is known
upstream. Restored to `$20=1` and verified. Worth re-checking after any
interrupted calibration.

The `$130/$131/$132` mismatch flagged on 2026-08-26 is gone; the controller now
matches the config exactly.

## Why steps 6–18 did not run

`drop_tip: tip_rack.A1` fails three independent ways:

1. **It ejects 35 mm in the air.** `drop_tip` engages like any pipette command:
   the tool point — the tip end, with a tip on — descends to the rack's
   `pickup_z: 60.0`, i.e. gantry Z 95.0 (traced). A tip seated in A1 has its end
   at deck Z 25 (nozzle at 60, tip 35 long).
2. **The eject position is a placeholder.** `instruments/pipette/models.py`,
   `p20_single_gen2`: `drop_tip_position=10.0,  # placeholder`.
3. **Nothing checks the outcome.** `commands/pipette.py` calls
   `pipette.clear_attached_tip_extension()` unconditionally after
   `pipette.drop_tip(speed)` returns.

If the tip is still on at step 7, the capper legs at gantry 71.065 carry the tip
end at deck Z **36.065** — 19 mm below the vial rims, 32 mm below the cap tops —
across the vial column, ~20 times. The real fix is a `tip_disposal` deck entry
(drop_tip's intended target, ejecting at that entry's own `location.z`) plus a
measured `drop_tip_position`.

## Other findings

**The shared `/dev/ttyACM0` works.** Probed the Arduino directly: it answers the
capper's command 7 *and* the pipette's command 14 from the same firmware —

```
cmd 7  (capper line-break)  -> OK:{"value1":0}
cmd 14 (pipette STATUS)     -> OK:{"homed":0,"pos":0.00,"max_vol":300.00}
```

so the two drivers are talking to one board that understands both. The
arbitration concern stands (`PawduinoLink` does not exist at the Pi's `cbc33dc`;
`opentrons.py:132` opens its own `serial.Serial`, and its own comment notes
"Opening the port resets the Arduino"), but the run was clean, and the boot
banner still lands at 3.76 s as it did on 2026-08-03.

**`max_vol` says 300, the config says p20.** The firmware reports
`max_vol: 300.00`; the gantry file declares `pipette_model: p20_single_gen2`.
Check which pipette is mounted. `mm_to_ul: 0.025` is the p20 number either way,
so `volume_ul` is not yet microlitres (20 µL → 0.5 mm of plunger).

**Capper park geometry.** `[125, 50]` is off the vial column, so at `safe_z: 87`
each decap/cap leg walks the bare nozzle across the cap tops at deck 71.065 vs.
~68 — about 3 mm, closest pass 0.9 mm from vial_2's axis. `[187.0, 50.0]` makes
every leg a pure-Y move at deck X 187 with the nozzle held at deck X 239, over
ground the engages already sweep at deck Z 52.065. That is what this run used.

## Runner ↔ Pi connectivity

The `Connect to Tailscale` step is still missing from `.github/workflows/claude.yml`
on `main` (removed in `429fe34`), so the runner starts with no tailnet. This
session joined manually using the `TS_OAUTH_CLIENT_ID` / `TS_OAUTH_SECRET`
secrets the job already carries, with `tag:stream-cam-test`. Restoring the
workflow step is the durable fix; the GitHub App cannot edit workflow files.

## Files

| | |
|---|---|
| `run_hardware_partA.log` | the hardware run |
| `partA_validate.log` | `validate_setup` for the run |
| `partA_trace.log` | every commanded gantry coordinate, Part A |
| `validate_setup.log` | `validate_setup` for the full 19-step attachment (PASS) |
| `trace.log` | every commanded gantry coordinate, full 19 steps — the `drop_tip` numbers above come from here |
