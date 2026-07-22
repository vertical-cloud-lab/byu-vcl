"""OT-2 protocol: repeated pickup/drop cycles with the ACTUAL sensor housing.

Companion to ``protocol_cyclic_loading.py`` (which fatigue-tests the small
press-fit tips in the deck-plate pockets). This one cycles the **real
enclosure** — ``stl/real_enclosure_p20_tip.stl``, the printed sensor housing
with its fake tip swapped for the tested best P20 tip (3.40 mm bore, 6
spring-finger slits) — through pick-up -> lift/transport -> drop, to measure
how the full-size, full-weight package behaves over many cycles.

Setup:

1. Stand the housing upright on its foot in ``HOUSING_SLOT`` (or seat it in
   the charging dock from PR #116 if you have it — then add the dock's seat
   height to ``SOCKET_MOUTH_Z`` below).
2. Position it so the **socket** (the post) is at the slot centre. The post
   is offset ~10 mm from the body centre, so align the *post*, not the body.
   The protocol pauses with the nozzle hovering over the target before the
   first cycle so you can slide the housing into alignment.
3. Because the housing stands free (no pocket walls to catch it like the
   test-array plate has), the drop is released **low** — with the foot
   ~``DROP_RELEASE_Z`` mm off the deck — so it settles back in place. A tape
   outline or printed fence around the foot adds margin for long runs.

Upload with ``run_robot.py protocol_cyclic_housing.py``.
"""

import json

# --- Cyclic-test configuration (edit these) -------------------------------
# Deck slot the housing stands in.
HOUSING_SLOT = 8

# Height of the SOCKET MOUTH above the deck, in mm. The housing
# (real_enclosure_p20_tip) is 90.5 mm tall standing on its foot: foot bottom
# at z = -5 mm and socket mouth at z = +85.5 mm in part coordinates. If the
# housing sits in the PR #116 charging dock instead of directly on the deck,
# ADD the dock's seat height here.
SOCKET_MOUTH_Z = 90.5

# Where the socket axis sits within the slot (mm from the slot's front-left
# corner). Default: slot centre. Remember to centre the POST, not the body.
SOCKET_X = 127.76 / 2
SOCKET_Y = 85.48 / 2

# How many pick-up/drop cycles to run. Start small (e.g. 10) to confirm the
# housing lands back on its foot reliably, then raise into the hundreds.
NUM_CYCLES = 500

# Print a progress comment every N cycles (0 disables).
COMMENT_EVERY = 10

# Pause for a physical inspection every N cycles (0 disables): check the
# socket for whitening/cracks at the slit roots and that the housing still
# sits square on its alignment mark.
PAUSE_EVERY = 50

# Lateral transport during each cycle (mm). Loads the press-fit joint
# sideways like a real move; 0 for a pure axial insert/remove test.
TRANSPORT_DX = 40.0
# Lift above the socket mouth during transport (mm). Kept modest because the
# gantry carries the full 90.5 mm housing below the nozzle.
TRANSPORT_DZ = 20.0

# Release height of the housing's FOOT above the deck at drop, in mm. Low
# release (the drop-off fix from PR #60) so the housing barely falls and
# lands back on its footprint instead of toppling.
DROP_RELEASE_Z = 2.0
# --------------------------------------------------------------------------

metadata = {
    "protocolName": "WCS Real Housing P20 Cyclic Pickup",
    "author": "BYU Vertical Cloud Lab",
    "description": (
        "Repeat pick-up/transport/drop of the actual sensor housing "
        "(real_enclosure_p20_tip, 3.40 mm slitted socket) to test the "
        "press-fit joint at full package size and weight."
    ),
    "apiLevel": "2.12",
}

# Single-position "tip rack": the housing itself is the tip (same modelling
# as the byu_color_sensor_charging_port labware from PR #116, which used
# tipLength: 84 for the original 84 mm package; this housing is 90.5 mm).
HOUSING_LABWARE = {
    "ordering": [["A1"]],
    "brand": {"brand": "BYU-VCL", "brandId": []},
    "metadata": {
        "displayName": "BYU WCS real housing (P20 tip)",
        "displayCategory": "tipRack",
        "displayVolumeUnits": "µL",
        "tags": [],
    },
    "dimensions": {"xDimension": 127.76, "yDimension": 85.48,
                   "zDimension": SOCKET_MOUTH_Z},
    "wells": {
        "A1": {
            "depth": SOCKET_MOUTH_Z,
            "totalLiquidVolume": 20,
            "shape": "circular",
            "diameter": 10.0,   # tip flange OD; only the centre matters
            "x": round(SOCKET_X, 2),
            "y": round(SOCKET_Y, 2),
            "z": 0.0,           # foot stands on the deck
        }
    },
    "groups": [{"metadata": {}, "wells": ["A1"]}],
    "parameters": {
        "format": "irregular",
        "quirks": ["touchTipDisabled"],
        "isTiprack": True,
        "tipLength": SOCKET_MOUTH_Z,
        "tipOverlap": 8.0,      # socket engagement depth, like the arrays
        "isMagneticModuleCompatible": False,
        "loadName": "byu_wcs_real_housing_p20",
    },
    "namespace": "custom_beta",
    "version": 1,
    "schemaVersion": 2,
    "cornerOffsetFromSlot": {"x": 0, "y": 0, "z": 0},
}


def point(x, y, z):
    """Local import wrapper so the module imports without opentrons present."""
    from opentrons.types import Point
    return Point(x, y, z)


def run(protocol):
    housing = protocol.load_labware_from_definition(
        HOUSING_LABWARE, HOUSING_SLOT
    )
    pipette = protocol.load_instrument(
        instrument_name="p20_single_gen2",
        mount="left",
        tip_racks=[housing],
    )
    well = housing["A1"]

    # alignment check: hover the bare nozzle over the socket so the housing
    # can be slid into position before any pressing happens
    pipette.move_to(well.top(z=15))
    protocol.pause(
        "ALIGN: slide the housing so its socket is centred directly under "
        "the nozzle (the post, not the body centre), then resume."
    )

    protocol.comment(
        f"=== Housing cyclic test: {NUM_CYCLES} pick-up/drop cycles ==="
    )
    for cycle in range(1, NUM_CYCLES + 1):
        pipette.pick_up_tip(well)
        # lift and transport like a real move (inertia + lateral load)
        pipette.move_to(well.top(z=TRANSPORT_DZ))
        if TRANSPORT_DX:
            pipette.move_to(
                well.top(z=TRANSPORT_DZ).move(point(TRANSPORT_DX, 0, 0))
            )
            pipette.move_to(well.top(z=TRANSPORT_DZ))
        # release low so the housing settles back onto its footprint
        pipette.drop_tip(well.bottom(z=DROP_RELEASE_Z))

        if COMMENT_EVERY and cycle % COMMENT_EVERY == 0:
            protocol.comment(f"  housing: {cycle}/{NUM_CYCLES} cycles done")
        if PAUSE_EVERY and cycle % PAUSE_EVERY == 0 and cycle < NUM_CYCLES:
            protocol.pause(
                f"Housing at {cycle} cycles. Inspect the socket for "
                "whitening/cracks at the slit roots, check the housing sits "
                "square on its mark, record, then resume."
            )
    protocol.comment(f"=== Housing finished {NUM_CYCLES} cycles ===")


if __name__ == "__main__":
    print(json.dumps(HOUSING_LABWARE, indent=2))
