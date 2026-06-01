"""Travel to each corner of the 96-well plate to exercise XY range of motion.

The pipette visits A1, A12, H12, then H1 (clockwise from the top-left) and
returns home. No tip is picked up. Useful for confirming that the gantry
can reach the extremes of the plate without collisions.

Tunable variables
-----------------
PAUSE_SEC : Seconds to hover above each corner before moving on.
CORNERS   : Tuple of well names to visit in order. Defaults to the four
            corners of a 96-well plate, traversed clockwise from A1.
"""

from opentrons import protocol_api

metadata = {
    'protocolName': '04 - Visit Plate Corners',
    'author': 'BYU Vertical Cloud Lab',
    'description': 'Move the pipette to each of the four corner wells of '
                   'the 96-well plate, pausing briefly above each.',
}

requirements = {'robotType': 'OT-2', 'apiLevel': '2.15'}

# ---- Tunable variables -----------------------------------------------------
PAUSE_SEC = 2
CORNERS = ('A1', 'A12', 'H12', 'H1')
# ---------------------------------------------------------------------------


def run(protocol: protocol_api.ProtocolContext) -> None:
    protocol.load_labware('opentrons_96_filtertiprack_20ul', 1)
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 2)

    pipette = protocol.load_instrument('p20_single_gen2', mount='left')

    for well in CORNERS:
        protocol.comment(f'Moving to corner well {well}.')
        pipette.move_to(plate[well].top())
        protocol.delay(seconds=PAUSE_SEC)

    protocol.comment('Homing the gantry.')
    protocol.home()
