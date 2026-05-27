"""Smallest end-to-end liquid-handling sanity check.

Picks up a tip, aspirates a small volume from a source well, dispenses it
into a destination well, and drops the tip in the trash. Intended to verify
that the plunger, tip pickup, and Z motion all cooperate.

NOTE: For a true dry run, leave the wells empty and watch the motion. To
actually move liquid, pre-fill the source well with water (or whatever you
are testing with) before starting.

Tunable variables
-----------------
SOURCE_WELL : Well to aspirate from.
DEST_WELL   : Well to dispense into.
VOLUME_UL   : Volume in microliters (must be within the p20 range, 1-20 µL).
"""

from opentrons import protocol_api

metadata = {
    'protocolName': '05 - Aspirate / Dispense Test',
    'author': 'BYU Vertical Cloud Lab',
    'description': 'Pick up a tip, aspirate a small volume from one well, '
                   'dispense it into another, then trash the tip.',
}

requirements = {'robotType': 'OT-2', 'apiLevel': '2.15'}

# ---- Tunable variables -----------------------------------------------------
SOURCE_WELL = 'A1'
DEST_WELL = 'B1'
VOLUME_UL = 10
# ---------------------------------------------------------------------------


def run(protocol: protocol_api.ProtocolContext) -> None:
    tiprack = protocol.load_labware('opentrons_96_filtertiprack_200ul', 1)
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 2)

    pipette = protocol.load_instrument(
        'p20_single_gen2', mount='left', tip_racks=[tiprack]
    )

    pipette.pick_up_tip()
    protocol.comment(f'Aspirating {VOLUME_UL} uL from {SOURCE_WELL}.')
    pipette.aspirate(VOLUME_UL, plate[SOURCE_WELL])
    protocol.comment(f'Dispensing {VOLUME_UL} uL into {DEST_WELL}.')
    pipette.dispense(VOLUME_UL, plate[DEST_WELL])
    pipette.drop_tip()
