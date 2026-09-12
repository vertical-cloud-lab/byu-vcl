# Calibrating the OT-2 in the Opentrons App

Everything below was checked against this robot (`OT2CEP20210722R13`) on
2026-09-11 and against Opentrons' own docs and app source, not from memory. The
robot's state at that moment is in
[`calibration-state-2026-09-11.json`](calibration-state-2026-09-11.json), and
[`calibration_status.py`](calibration_status.py) re-derives it in one read-only
command.

## What actually needs calibrating

There are **four** calibrations, and only the last one is Labware Position
Check. They must be done in this order, because **calibrating the deck clears
the other two** — that is the Opentrons App's own wording:

> "Calibrating pipette offset before deck calibration when both are needed
> isn't suggested. Calibrating the deck clears all other calibration data."
> — `deck_calibration_modal_description`, Opentrons App localisation

| # | calibration | scope | where |
| --- | --- | --- | --- |
| 1 | **Deck** | the robot | Robot Settings → Calibration |
| 2 | **Tip length** | per pipette **× per tip-rack type** | Robot Settings → Calibration |
| 3 | **Pipette offset** | per pipette × per mount | Robot Settings → Calibration |
| 4 | **Labware Position Check** | per labware type **× per deck slot** | a protocol's Setup tab |

Steps 1–3 are "robot calibration" and live under Robot Settings. Step 4 is not
there at all — **LPC only exists inside a protocol run**, which is why it cannot
be done ahead of time or from the Devices screen.

## State of this robot, 2026-09-11

```
deck calibration        OK  last 2026-01-27  with pipette P20SV202020030408
left mount              p300_single_v2.1  P3HSV212021083111
  tip length     MISSING   (robot holds 17 entries, none for this pipette)
  pipette offset MISSING
  tiprack custom_beta/ac_color_sensor_charging_port/1  ->  MISSING
labware offsets (LPC)   0 stored
networking              limited  eth0=connected  wlan0=disconnected
```

Three things follow from that:

- **The deck calibration is stale.** It is dated 2026-01-27 and the robot was
  physically moved on 2026-09-10. The app: *"Calibrating the deck is required
  for new robots or after you relocate your robot."*
- **The attached P300 has no calibration data at all.** The robot holds 17 tip
  length calibrations and 1 pipette offset calibration, none of them for
  `P3HSV212021083111`. The app blocks a run in this state — *"Please calibrate
  all pipettes specified in loaded protocol to proceed."*
- **The app cannot see the robot.** `wlan0` is disconnected and `eth0` has a
  link-local address with no gateway, so the only machine that can reach the
  OT-2 is the stream-cam Pi it is cabled to. Calibration happens in the
  Opentrons App, which runs on a computer — so this has to be solved first.

## Step 0 — let the app reach the robot

Plug a **USB-B** cable from the OT-2's rear USB-B port into the computer running
the Opentrons App, wait a few seconds, then open the app. This is Opentrons' own
recommended path and needs no network change.

If you would rather put the robot on Wi-Fi: Devices → ⋮ → **Robot Settings** →
**Networking**. Opentrons specifically recommend doing that *while connected
over USB*, because changing Wi-Fi over Wi-Fi can strand the app.

Leave the ethernet cable to the Pi alone either way — that link is what
`run_xscan_test.py` and `deck_photo.py` use, and it is independent of the app.

## Step 1 — deck calibration

Devices → select the OT-2 → ⋮ → **Robot Settings** → **Calibration** →
**Calibrate deck**. Jog the pipette onto the etched crosses; the app walks
through the sequence.

Do this **first and once**. Everything else is downstream of it.

## Steps 2 and 3 — tip length, then pipette offset

Same screen, under **Pipette Offset Calibrations**. The flow asks you to choose
a tip rack first, then measures tip length and pipette offset in one pass.

Use `opentrons_96_tiprack_300ul` — the stock 300 µL rack the protocol uses,
which is also what the P300 is meant to be characterised on. The app is explicit
that calibrating on Opentrons tips matters.

## Step 4 — add the custom labware

Only **one** definition is custom. Left sidebar → **Labware** → **Import**, and
select the `.json` file:

| labware | load name | slot (AC protocol) | custom? |
| --- | --- | --- | --- |
| 96-well plate | `corning_96_wellplate_360ul_flat` | 1 | **no — stock, already on the robot** |
| 300 µL tip rack | `opentrons_96_tiprack_300ul` | 9 | **no — stock** |
| sensor dock | `ac_color_sensor_charging_port` | 10 | **yes** |
| paint reservoir, 6 × 15 mL tubes | `ac_6_tuberack_15000ul` | 3 | yes, *only if the robot dispenses the paint itself* |

The sensor dock is committed here as
[`protocols/ac_color_sensor_charging_port.json`](protocols/ac_color_sensor_charging_port.json)
— import *that* file, since the app's Import screen needs a standalone `.json`
and the copies embedded in the protocol scripts cannot be selected. Both custom
definitions are also upstream in
[`ac-dev-lab/src/ac_training_lab/ot-2/_scripts/`](https://github.com/AccelerationConsortium/ac-dev-lab/tree/main/src/ac_training_lab/ot-2/_scripts).

The tube rack is the **stock-solution reservoir** — six positions for 15 mL
tubes (20 mm bore, 58 mm deep), from which the P300 aspirates red, yellow and
blue out of `B1`/`B2`/`B3`. It is not a measurement target. If you pipette the
paint into the well plate by hand, you do not need it.

## Step 5 — tip length calibration for the sensor dock

**This is the step that is easy to miss.** The sensor dock is declared as a tip
rack:

```json
"parameters": { "loadName": "ac_color_sensor_charging_port",
                "isTiprack": true, "tipLength": 84 }
```

The protocol picks the module up with `p300.pick_up_tip(dock["A2"])`, so as far
as the robot is concerned the module *is* a tip — and **every tip rack a
protocol picks up from needs its own tip length calibration with the attached
pipette.** The app matches on the labware URI, here
`custom_beta/ac_color_sensor_charging_port/1`, which is why a calibration
against the 300 µL rack does not satisfy it.

Once the definition is imported it appears in the calibration flow's tip-rack
picker, under a "custom" group beneath the Opentrons racks. Re-run the pipette
calibration flow and pick it there.

## Step 6 — Labware Position Check

LPC lives inside a protocol. Import the protocol, open its **Setup** tab, expand
**Labware Offsets**, and click **Run Labware Position Check**. Jog the pipette
over each piece of labware in turn and click **Complete**.

Two properties worth knowing:

- An offset is stored against an **exact labware-type-and-slot pair**. Move the
  plate from slot 1 to slot 2 and the offset does not follow it.
- Robot software 6.0.0 and later reuses a stored offset across *different*
  protocols, as long as that labware-and-slot pair matches. So LPC is done once
  per layout, not once per protocol.

## What this does and does not reach

`run_xscan_test.py` drives the robot with `moveToCoordinates` inside a
**maintenance run**, with absolute deck numbers. No labware is loaded on that
path, so **no LPC offset is ever applied to it.** Calibrating in the app pays
off only once the motion half is ported to a real protocol that loads labware
and addresses wells by name.

That port is the point of doing this: `plate["A1"].top(z=-1.3)` is a read height
expressed relative to the well, so it survives a re-calibration or a plate swap
without a code edit — which is what the hand-tuned `--read-z` / `--drop-dx`
constants cannot do.

One more gotcha if any of this is ever run from Jupyter or `opentrons.execute`
rather than the app: **LPC offsets are not applied automatically on that path.**
Read the numbers off the app and pass them to `labware.set_offset(x, y, z)` —
and note `set_offset()` raises at protocol API 2.14–2.17, so request 2.18 or
later.

## Geometry, for the 96-well plate

Stock `corning_96_wellplate_360ul_flat`, version 2: wells 6.86 mm across,
10.67 mm deep, 360 µL, A1 at (14.38, 74.24) within the slot.

The AS7341's roughly ±20° field of view spans about 21 mm at the read heights
used so far, so a 6.86 mm well fills well under half of it. **A per-well blank
is not optional with this plate** — most of what the sensor sees is plate, not
liquid. The upside is that `.top(z=)` puts the aperture a millimetre or two off
the liquid surface with no collision risk, which is exactly what standing vials
made impossible.

## Sources

- [OT-2 robot calibration](https://docs.opentrons.com/ot-2/calibration/robot-calibration/)
- [OT-2 labware offsets](https://docs.opentrons.com/ot-2/calibration/labware-offsets/)
- [Using Labware Position Check](https://docs.opentrons.com/v2/robot_position.html#using-labware-position-check)
- [Custom labware](https://docs.opentrons.com/v2/new_labware.html#custom-labware) · [Labware Creator](https://labware.opentrons.com/create/) · [Labware Library](https://labware.opentrons.com/)
- [Connect to the OT-2 over USB](https://support.opentrons.com/s/article/Get-started-Connect-to-your-OT-2-over-USB) · [Connect over Wi-Fi](https://support.opentrons.com/s/article/Get-started-Connect-to-your-OT-2-over-Wi-Fi-optional)
- App source: [`useRunPipetteInfoByMount.ts`](https://github.com/Opentrons/opentrons/blob/edge/app/src/resources/runs/useRunPipetteInfoByMount.ts) (tip-length cal is matched per tiprack URI × pipette serial) · [`ChooseTipRack.tsx`](https://github.com/Opentrons/opentrons/blob/edge/app/src/organisms/Desktop/CalibrationPanels/ChooseTipRack.tsx) (custom tip racks are concatenated into the picker)
