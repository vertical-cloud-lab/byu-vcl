"""Home all axes and (optionally) park the pipette above an empty slot.

Use this when the robot has stopped in an awkward position and you want a
known, safe starting state. After homing, the pipette can optionally be
moved to a parking position above a chosen deck slot for easier inspection
or maintenance access.

Tunable variables
-----------------
PARK_AFTER_HOME : If True, move above PARK_SLOT after homing.
PARK_SLOT       : Deck slot (1-11) to park above.
"""

from opentrons import protocol_api

metadata = {
    'protocolName': '06 - Home and Park',
    'author': 'BYU Vertical Cloud Lab',
    'description': 'Home all axes and optionally park the pipette above a '
                   'chosen deck slot for inspection.',
}

requirements = {'robotType': 'OT-2', 'apiLevel': '2.15'}

# ---- Tunable variables -----------------------------------------------------
PARK_AFTER_HOME = True
PARK_SLOT = 5
# ---------------------------------------------------------------------------


def run(protocol: protocol_api.ProtocolContext) -> None:
    protocol.load_labware('opentrons_96_filtertiprack_20ul', 1)
    protocol.load_labware('corning_96_wellplate_360ul_flat', 2)

    pipette = protocol.load_instrument('p20_single_gen2', mount='left')

    protocol.comment('Homing all axes.')
    protocol.home()

    if PARK_AFTER_HOME:
        # Load a temporary labware in the park slot just to get a clean
        # reference Location for move_to. It is not interacted with.
        park_labware = protocol.load_labware(
            'corning_96_wellplate_360ul_flat', PARK_SLOT
        )
        protocol.comment(f'Parking above slot {PARK_SLOT}.')
        pipette.move_to(park_labware['A1'].top(z=20))
