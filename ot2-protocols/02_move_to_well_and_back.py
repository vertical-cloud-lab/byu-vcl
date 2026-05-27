"""Move the pipette to a target well, pause, and then return to the start.

Useful for confirming XY travel and for visually checking alignment over a
specific well without performing any liquid handling.

Tunable variables
-----------------
START_WELL  : Well to begin (and return) above.
TARGET_WELL : Well to travel to.
PAUSE_SEC   : Seconds to hover above the target well before returning.
"""

from opentrons import protocol_api

metadata = {
    'protocolName': '02 - Move to Well and Back',
    'author': 'BYU Vertical Cloud Lab',
    'description': 'Move the pipette to a target well, pause, then return '
                   'to the starting well. No tip is picked up.',
}

requirements = {'robotType': 'OT-2', 'apiLevel': '2.15'}

# ---- Tunable variables -----------------------------------------------------
START_WELL = 'A1'
TARGET_WELL = 'H12'
PAUSE_SEC = 3
# ---------------------------------------------------------------------------


def run(protocol: protocol_api.ProtocolContext) -> None:
    # Tip rack is loaded so the deck layout is consistent across tests.
    protocol.load_labware('opentrons_96_filtertiprack_200ul', 1)
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 2)

    pipette = protocol.load_instrument('p20_single_gen2', mount='left')

    protocol.comment(f'Moving to start well {START_WELL}.')
    pipette.move_to(plate[START_WELL].top())

    protocol.comment(f'Moving to target well {TARGET_WELL}.')
    pipette.move_to(plate[TARGET_WELL].top())

    protocol.delay(seconds=PAUSE_SEC)

    protocol.comment(f'Returning to start well {START_WELL}.')
    pipette.move_to(plate[START_WELL].top())
