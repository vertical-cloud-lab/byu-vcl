"""Pick up a single tip and return it to the same position in the rack.

This is the simplest possible "did the robot move and grab a tip?" check.
It does not aspirate, dispense, or visit the plate.

Tunable variables
-----------------
TIP_WELL        : Which well of the tip rack to pick up from / return to.
"""

from opentrons import protocol_api

metadata = {
    'protocolName': '01 - Pick Up and Return Tip',
    'author': 'BYU Vertical Cloud Lab',
    'description': 'Pick up one tip from the filter tip rack and return it '
                   'to the same position.',
}

requirements = {'robotType': 'OT-2', 'apiLevel': '2.15'}

# ---- Tunable variables -----------------------------------------------------
TIP_WELL = 'A1'
# ---------------------------------------------------------------------------


def run(protocol: protocol_api.ProtocolContext) -> None:
    tiprack = protocol.load_labware('opentrons_96_filtertiprack_20ul', 1)
    # Plate is loaded so the deck layout matches the other test protocols,
    # even though this protocol does not touch it.
    protocol.load_labware('corning_96_wellplate_360ul_flat', 2)

    pipette = protocol.load_instrument(
        'p20_single_gen2', mount='left', tip_racks=[tiprack]
    )

    protocol.comment(f'Picking up tip from {TIP_WELL}.')
    pipette.pick_up_tip(tiprack[TIP_WELL])

    protocol.comment(f'Returning tip to {TIP_WELL}.')
    pipette.return_tip()
