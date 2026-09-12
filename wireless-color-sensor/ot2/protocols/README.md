# Opentrons protocols — colour-sensor pick-up and read height

Two protocols you run from the Opentrons App. They do no liquid handling; both
exist only to get the geometry right, one question at a time.

| file | question it answers |
| --- | --- |
| [`01_pickup_both_sides.py`](01_pickup_both_sides.py) | can the P300 use **both** sockets of the charging base? |
| [`02_read_height_over_well.py`](02_read_height_over_well.py) | how far above a 96-well plate well should the sensor sit? |
| [`ac_color_sensor_charging_port.json`](ac_color_sensor_charging_port.json) | the charging base as Opentrons labware |

Each `.py` is **self-contained** — the labware definition is embedded in it, so
drag the file into the app and it runs. The `.json` is the same definition as a
separate file, because the app's *tip-length calibration* screen can only see
labware that has been imported into its labware list.

## Running them

1. **Connect the app to the robot.** USB-B from the OT-2 to the computer. The
   ethernet cable to the Pi is a separate link and can stay as it is.
2. **Import** `ac_color_sensor_charging_port.json` — sidebar → *Labware* →
   *Import*.
3. **Calibrate**, in this order, because deck calibration wipes the other two:
   deck → tip length → pipette offset. Do the tip-length step **twice**: once on
   `opentrons_96_tiprack_300ul`, and once on the charging base, which is declared
   `"isTiprack": true` and so needs its own.
4. **Upload** the `.py` and run it. Every step pauses with a message; read the
   message, look at the machine, press *Resume*.

Settings live in an `EDIT THESE` block at the top of each file. Change one line,
re-upload, run again.

## Suggested order

```
01  MODE = "hover"    both sockets, empty nozzle, zero risk — look at the centring
01  MODE = "inplace"  SIDE = "A1"   the known-good socket
01  MODE = "inplace"  SIDE = "A2"   the new one (put the enclosure in it by hand)
01  MODE = "shuttle"  A1 → A2 → A1, all four operations in one run
02  MODE = "dry"      X/Y check over the plate, nothing picked up
02  MODE = "ladder"   step down through read heights with the enclosure on
02  MODE = "hold"     sit at the height you chose and take a reading
```

## Three things that are easy to get wrong

**Labware Position Check cannot tell A1 from A2.** It stores one offset for the
whole labware and slides both sockets together. If the nozzle is off by the same
amount over both, that is LPC's job. If it is off over one socket only, edit
`wells.A2.x` / `.y` in the JSON *and* in the embedded `DOCK_DEF` of any protocol
that uses it. `MODE = "hover"` visits both sockets in one run so you can tell
those two cases apart by eye.

**These protocols are pinned to `apiLevel` 2.13, on purpose.** On robot software
8.8.1, `pick_up_tip` from this 2-well dock fails at API 2.14 and above with
`InvalidStoredData: ... less dense than an SBS 96 standard`: the newer
tip-tracking code assumes a rack at least 12 wells wide and 8 tall and divides by
those, and a 2-well dock fails the check. 2.13 uses the older core and is
unaffected. The cost is no runtime parameters, which is why the settings are
edited in the file rather than chosen in the app. Labware Position Check still
applies its offsets to 2.13 protocols — `LegacyProtocolCore` calls
`set_calibration()` on every labware it loads, including one loaded from an
embedded definition.

**A bare nozzle cannot reach far down.** A P300 GEN2 on the left mount with no
tip bottoms out at deck z **29.45 mm**, which is about +15 mm over the rim of a
96-well plate. So `MODE = "dry"` can only rehearse the top of the ladder; it
announces and skips the rest. With the 84 mm enclosure on, the same mount reaches
84 mm lower and the whole ladder is available.

## Re-checking them

Both were simulated against `opentrons==8.8.1` — the robot's own software
version — in every mode, with no warnings. To repeat that:

```bash
python3 -m venv /tmp/otsim && /tmp/otsim/bin/pip install "opentrons==8.8.1"
/tmp/otsim/bin/opentrons_simulate 01_pickup_both_sides.py
/tmp/otsim/bin/opentrons_simulate 02_read_height_over_well.py
```

Use 8.8.1 specifically. `opentrons` 9.x refuses to simulate OT-2 protocols at
all, and older versions do not reproduce the 2.14 tip-tracking failure above.
