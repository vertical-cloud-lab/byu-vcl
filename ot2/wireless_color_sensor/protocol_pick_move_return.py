"""OT-2 protocol: Pick up the wireless color sensor, move it, and return it.

Self-contained second mechanical test for the BYU-VCL wireless color
sensor (WCS): pick the sensor up from its charging port, traverse the
gantry over a destination well on a 96-well plate, dwell briefly (as if
taking a reading), and then return the sensor to the charging port.

This file is a single, self-contained OT-2 protocol -- the custom labware
definition is embedded inline so the file can be uploaded directly via the
Opentrons App with no separate custom-labware setup required.

The same logic is also available as importable helpers in ``wcs_actions``
(see this folder's README), for users who want to compose more complex
protocols from the packaged actions.

Deck layout
-----------
* Slot 1:  Corning 96-well flat plate (``corning_96_wellplate_360ul_flat``)
* Slot 10: BYU wireless color sensor charging port (custom labware)

Pipette
-------
* Right mount: ``p20_single_gen2``
"""

import json

metadata = {
    "protocolName": "WCS Test 2: Pick Up, Move, and Return",
    "author": "BYU Vertical Cloud Lab",
    "description": (
        "Pick the wireless color sensor up from its charging port "
        "(slot 10, well A2), move it over a destination well on a "
        "96-well plate in slot 1, dwell briefly, and return the "
        "sensor to its charging port."
    ),
    "apiLevel": "2.12",
}

# Deck slot for the wireless color sensor charging port.
WCS_SLOT = 10

# Well in the charging port labware where the sensor is parked.
WCS_PARK_WELL = "A2"

# Vertical offset (mm, relative to the well top) at which the sensor is
# released back into the charging port. Matches the value validated on
# real hardware by the Acceleration Consortium reference setup.
WCS_RETURN_Z_OFFSET = -80.0

# Destination well on the 96-well plate to "measure" above.
MEASUREMENT_WELL = "A1"

# Vertical offset (mm, relative to the destination well top) at which the
# sensor is held during the dwell. Matches the AC reference setup.
MEASUREMENT_Z_OFFSET = -1.3

# How long (s) to hold the sensor above the destination well.
DWELL_SECONDS = 2.0

# Inline custom labware definition for the BYU wireless color sensor
# charging port (same JSON as in ``labware/`` and ``protocol_pick_and_place.py``).
WCS_CHARGING_PORT_LABWARE = json.loads(
    """{
    "ordering": [["A1"], ["A2"]],
    "brand": {"brand": "BYU-VCL", "brandId": []},
    "metadata": {
        "displayName": "BYU wireless color sensor charging port",
        "displayCategory": "tipRack",
        "displayVolumeUnits": "\u00b5L",
        "tags": []
    },
    "dimensions": {"xDimension": 128, "yDimension": 86, "zDimension": 100},
    "wells": {
        "A1": {"depth": 84, "totalLiquidVolume": 1000, "shape": "circular",
                "diameter": 66, "x": 36,    "y": 43, "z": 16},
        "A2": {"depth": 84, "totalLiquidVolume": 1000, "shape": "circular",
                "diameter": 66, "x": 91.95, "y": 43, "z": 16}
    },
    "groups": [{"metadata": {}, "wells": ["A1", "A2"]}],
    "parameters": {
        "format": "irregular",
        "quirks": ["centerMultichannelOnWells", "touchTipDisabled"],
        "isTiprack": true,
        "tipLength": 84,
        "tipOverlap": 0,
        "isMagneticModuleCompatible": false,
        "loadName": "byu_color_sensor_charging_port"
    },
    "namespace": "custom_beta",
    "version": 1,
    "schemaVersion": 2,
    "cornerOffsetFromSlot": {"x": 0, "y": 0, "z": 0}
}"""
)


def run(protocol):
    # Standard 96-well flat plate in slot 1.
    plate = protocol.load_labware(
        "corning_96_wellplate_360ul_flat", location=1
    )

    # Custom labware: WCS charging port in slot 10.
    charging_port = protocol.load_labware_from_definition(
        WCS_CHARGING_PORT_LABWARE, WCS_SLOT
    )

    # p20 single-channel Gen2 pipette on the left mount, bound to the
    # charging port so the WCS is picked up as if it were a tip.
    pipette = protocol.load_instrument(
        instrument_name="p20_single_gen2",
        mount="left",
        tip_racks=[charging_port],
    )

    # ---- Mechanical test: pick up, move, dwell, return ----
    pipette.pick_up_tip(charging_port[WCS_PARK_WELL])
    pipette.move_to(plate[MEASUREMENT_WELL].top(z=MEASUREMENT_Z_OFFSET))
    protocol.delay(seconds=DWELL_SECONDS)
    pipette.drop_tip(charging_port[WCS_PARK_WELL].top(z=WCS_RETURN_Z_OFFSET))
