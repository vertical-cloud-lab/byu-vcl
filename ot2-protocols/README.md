# OT-2 Troubleshooting / Test / Control Protocols

This folder contains a set of small Opentrons OT-2 protocols intended for
troubleshooting, testing, and basic manual-style control of the robot. The
OT-2 does not provide a button-driven jog GUI like a Bambu 3D printer, so
these short, single-purpose protocols approximate that capability by letting
you exercise one piece of robot behavior at a time.

## Common setup

Every protocol in this folder uses the same hardware configuration so that
slots and the deck layout do not need to be re-checked between tests:

| Item              | Value                                              |
|-------------------|----------------------------------------------------|
| Robot             | OT-2                                               |
| API level         | 2.15                                               |
| Left pipette      | `p20_single_gen2` (20 µL single-channel, GEN2)     |
| Tip rack          | `opentrons_96_filtertiprack_200ul` (slot 1)        |
| Labware           | `corning_96_wellplate_360ul_flat` (slot 2)         |

Slot placements are arbitrary unless a protocol notes otherwise.

## Tunable variables

Each protocol exposes a small block of constants near the top of the file
(e.g. `DISTANCE_MM = 20`, `TARGET_WELL = 'A1'`). Change those values to
adjust the behavior — the rest of the file should not need to be edited.

## Protocols

| File                                | Purpose                                                              |
|-------------------------------------|----------------------------------------------------------------------|
| `01_pick_up_and_return_tip.py`      | Pick up a tip from the tip rack and return it to the same position.  |
| `02_move_to_well_and_back.py`       | Move the pipette to a target well, pause, then return to the start.  |
| `03_move_pipette_down.py`           | Move the pipette down a configurable distance from a reference well. |
| `04_visit_plate_corners.py`         | Travel to the four corner wells of the plate (XY range-of-motion).   |
| `05_aspirate_dispense_test.py`      | Pick up a tip, aspirate then dispense a small volume, drop the tip.  |
| `06_home_and_park.py`               | Home all axes and (optionally) park above slot 5 for inspection.     |

## Running

Upload the desired `.py` file through the Opentrons App (or `opentrons_simulate`
on the command line) the same way you would any other protocol. Always run
a Labware Position Check before executing a protocol on the physical robot.

```
opentrons_simulate ot2-protocols/01_pick_up_and_return_tip.py
```
