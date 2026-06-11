"""OT-2 protocol: cycle through the P20 fake-tip test array.

Based on the working template from
https://github.com/vertical-cloud-lab/byu-vcl/pull/116#issuecomment-4665074566
(protocol_pick_and_place.py by @timothy-commins) — upload with run_robot.py
or via the Opentrons app.

The 3D-printed deck plate (cad/stl/deck_plate_base.stl) sits in DECK SLOT 8
with its engraved "A1" marker at the BACK-LEFT.  Each pocket holds one test
tip from cad/stl/fake_tip_test_array.stl (bore IDs engraved on the plate and
on the underside of each tip).

For every pocket the robot: picks the tip up, raises it, pauses so you can
check retention (tug gently / observe), then ejects it back over its pocket.
Record pass/fail per the evaluation criteria in p20-fake-tip-design.md.
"""

import json

metadata = {
    "protocolName": "WCS P20 Fake-Tip Test Array Sweep",
    "author": "BYU Vertical Cloud Lab",
    "description": (
        "Pick up and eject each of the 10 press-fit test tips "
        "(bore ID 3.40-3.85 mm) to find the optimal P20 socket size."
    ),
    "apiLevel": "2.12",
}

ARRAY_SLOT = 8

# Geometry from cad/cad_model.py: plate 24 mm tall, pocket depth 12.2 mm,
# so a tip seats with its bottom at z = 11.8 mm; tip is 20 mm tall ->
# socket entry (well top) at 31.8 mm.  This keeps the P20 pickup press
# (which travels ~tipLength + 4.5 mm below the well top) above the deck.
TIP_SEAT_Z = 11.8
TIP_HEIGHT = 20.0

# Pocket grid: 2 rows x 5 cols, 18 mm pitch, centered on the SLAS footprint
# (127.76 x 85.48 mm).  Labware coords measure from the front-left corner.
_PITCH = 18.0
_CX, _CY = 127.76 / 2, 85.48 / 2
_BORES = [3.40, 3.45, 3.50, 3.55, 3.60, 3.65, 3.70, 3.75, 3.80, 3.85]

_wells = {}
_ordering = []
for col in range(5):
    col_names = []
    for row in range(2):  # A = back (+y), B = front
        name = f"{'AB'[row]}{col + 1}"
        _wells[name] = {
            "depth": TIP_HEIGHT,
            "totalLiquidVolume": 20,
            "shape": "circular",
            "diameter": 10.8,
            "x": round(_CX + (col - 2) * _PITCH, 2),
            "y": round(_CY + (0.5 - row) * _PITCH, 2),
            "z": TIP_SEAT_Z,
        }
        col_names.append(name)
    _ordering.append(col_names)

TEST_ARRAY_LABWARE = {
    "ordering": _ordering,
    "brand": {"brand": "BYU-VCL", "brandId": []},
    "metadata": {
        "displayName": "BYU P20 fake-tip test array",
        "displayCategory": "tipRack",
        "displayVolumeUnits": "µL",
        "tags": [],
    },
    "dimensions": {"xDimension": 127.76, "yDimension": 85.48,
                   "zDimension": TIP_SEAT_Z + TIP_HEIGHT},
    "wells": _wells,
    "groups": [{"metadata": {}, "wells": sorted(_wells)}],
    "parameters": {
        "format": "irregular",
        "quirks": ["touchTipDisabled"],
        "isTiprack": True,
        "tipLength": TIP_HEIGHT,
        "tipOverlap": 8.0,
        "isMagneticModuleCompatible": False,
        "loadName": "byu_p20_fake_tip_test_array",
    },
    "namespace": "custom_beta",
    "version": 1,
    "schemaVersion": 2,
    "cornerOffsetFromSlot": {"x": 0, "y": 0, "z": 0},
}

# Well order matches the engraved bore labels: A1..A5 = 3.40-3.60,
# B1..B5 = 3.65-3.85.
WELL_SEQUENCE = [f"A{i}" for i in range(1, 6)] + [f"B{i}" for i in range(1, 6)]


def run(protocol):
    array = protocol.load_labware_from_definition(
        TEST_ARRAY_LABWARE, ARRAY_SLOT
    )
    pipette = protocol.load_instrument(
        instrument_name="p20_single_gen2",
        mount="left",
        tip_racks=[array],
    )
    for well_name, bore in zip(WELL_SEQUENCE, _BORES):
        well = array[well_name]
        protocol.comment(f"--- Test tip {well_name}: bore ID {bore:.2f} mm ---")
        pipette.pick_up_tip(well)
        pipette.move_to(well.top(z=60))
        protocol.pause(
            f"Tip {well_name} (bore {bore:.2f} mm) lifted. Check retention "
            "(gently tug), then resume to eject it back into its pocket."
        )
        # eject just above the pocket so the tip drops back in
        pipette.drop_tip(well.top(z=2))
        protocol.pause(
            f"Did tip {well_name} eject cleanly and land in its pocket? "
            "Record the result, then resume."
        )


if __name__ == "__main__":
    # print the labware definition for use with other scripts
    print(json.dumps(TEST_ARRAY_LABWARE, indent=2))
