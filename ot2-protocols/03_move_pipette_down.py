"""Move the pipette down a configurable Z distance from a reference well.

Approaches a reference well's top, then descends by ``DISTANCE_MM`` so that
plunger / Z-axis travel can be inspected in isolation. The pipette is then
raised back to the well top.

Tunable variables
-----------------
REFERENCE_WELL : Well above which the move happens.
DISTANCE_MM    : How far (in mm) to move down from the well top.
PAUSE_SEC      : Seconds to hold at the lowered position before retracting.
"""

from opentrons import protocol_api
from opentrons.types import Point

metadata = {
    'protocolName': '03 - Move Pipette Down',
    'author': 'BYU Vertical Cloud Lab',
    'description': 'Move the pipette down a configurable distance from the '
                   'top of a reference well, then move back up.',
}

requirements = {'robotType': 'OT-2', 'apiLevel': '2.15'}

# ---- Tunable variables -----------------------------------------------------
REFERENCE_WELL = 'A1'
DISTANCE_MM = 20
PAUSE_SEC = 2
# ---------------------------------------------------------------------------


def run(protocol: protocol_api.ProtocolContext) -> None:
    protocol.load_labware('opentrons_96_filtertiprack_200ul', 1)
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 2)

    pipette = protocol.load_instrument('p20_single_gen2', mount='left')

    top_location = plate[REFERENCE_WELL].top()

    protocol.comment(f'Moving to top of {REFERENCE_WELL}.')
    pipette.move_to(top_location)

    protocol.comment(f'Moving down {DISTANCE_MM} mm.')
    pipette.move_to(top_location.move(Point(z=-DISTANCE_MM)))

    protocol.delay(seconds=PAUSE_SEC)

    protocol.comment('Returning to well top.')
    pipette.move_to(top_location)
