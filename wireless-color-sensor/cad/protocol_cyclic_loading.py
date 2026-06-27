"""OT-2 protocol: cyclic (fatigue) loading of the P20 fake-tip survivors.

Companion to ``protocol_fake_tip_test.py`` (the single-pass sweep). Where that
script visits every pocket once to find which bore sizes grip, this one repeats
pick-up -> transport -> drop **many times** on just the tips that already
passed, to measure how many insert/remove cycles each socket survives before it
loosens, whitens, or cracks at a slit root.

Per @timothy-commins' first round
(https://github.com/vertical-cloud-lab/byu-vcl/pull/60#issuecomment-4792616426):

* **solid** bores 3.40-3.50 mm picked up and held,
* **slitted** only 3.40 mm held,

so by default this runs the union of those wells. Edit ``CYCLE_WELLS`` and
``NUM_CYCLES`` to match whatever your print actually passed, then upload with
``run_robot.py``.

Each cycle picks the tip up, lifts it, moves across the deck and back to load
the socket the way a real transfer would (inertia + a small lateral nudge),
returns over the pocket, and ejects. Progress is printed every
``COMMENT_EVERY`` cycles so you can follow along in the app/run log, and the
robot pauses at fixed checkpoints (``PAUSE_EVERY``) so you can inspect the
socket for wear and record it.

The labware definition is identical to ``protocol_test_array.py`` so the same
printed deck plate and tips are reused.
"""

import json

# --- Cyclic-test configuration (edit these) -------------------------------
# Bores that survived round 1; only these get fatigue-tested. Map of
# well name -> bore ID label (mm), in the engraved A1..B5 layout.
CYCLE_WELLS = {
    "A1": 3.40,
    "A2": 3.45,
    "A3": 3.50,
}

# How many pick-up/drop cycles to run on EACH well. The goal is thousands;
# start smaller (e.g. 50) to confirm motion, then raise. At ~6 s/cycle,
# 1000 cycles per tip is ~1.7 h, so budget run time accordingly.
NUM_CYCLES = 1000

# Print a progress comment every N cycles (0 disables).
COMMENT_EVERY = 25

# Pause for a physical wear inspection every N cycles (0 disables). Use this
# to eyeball/caliper the socket and note any whitening or cracks; the run log
# records the cycle number so failures are timestamped.
PAUSE_EVERY = 250

# Lateral transport during each cycle (mm). A non-zero nudge loads the joint
# sideways like a real move; set to 0 for a pure axial insert/remove test.
TRANSPORT_DX = 40.0
TRANSPORT_DZ = 60.0

# Eject height above the seated (pocket-bottom) position, in mm. The tip is
# released LOW in its pocket so the walls guide it back into the seat and it
# barely falls -- essential for unattended cycling where no human repositions
# missed tips. (Releasing above the pocket rim, e.g. well.top(z=2), dropped the
# tip ~22 mm and it often missed the hole; see PR #60 testing videos.)
DROP_RELEASE_Z = 2.0
# --------------------------------------------------------------------------

metadata = {
    "protocolName": "WCS P20 Fake-Tip Cyclic (Fatigue) Loading",
    "author": "BYU Vertical Cloud Lab",
    "description": (
        "Repeat pick-up/transport/drop many times on the surviving press-fit "
        "tips to measure insert/remove cycle life (PETG fatigue)."
    ),
    "apiLevel": "2.12",
}

ARRAY_SLOT = 8

# Geometry from cad/cad_model.py: plate 24 mm tall, pocket depth 12.2 mm,
# so a tip seats with its bottom at z = 11.8 mm; tip is 20 mm tall ->
# socket entry (well top) at 31.8 mm. Matches protocol_test_array.py.
TIP_SEAT_Z = 11.8
TIP_HEIGHT = 20.0

_PITCH = 18.0
_CX, _CY = 127.76 / 2, 85.48 / 2

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


def point(x, y, z):
    """Local import wrapper so the module imports without opentrons present."""
    from opentrons.types import Point
    return Point(x, y, z)


def run(protocol):
    array = protocol.load_labware_from_definition(
        TEST_ARRAY_LABWARE, ARRAY_SLOT
    )
    pipette = protocol.load_instrument(
        instrument_name="p20_single_gen2",
        mount="left",
        tip_racks=[array],
    )

    for well_name, bore in CYCLE_WELLS.items():
        well = array[well_name]
        protocol.comment(
            f"=== Cyclic test: tip {well_name} (bore {bore:.2f} mm), "
            f"{NUM_CYCLES} cycles ==="
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
            # return over the pocket and eject low so the walls catch the tip
            pipette.drop_tip(well.bottom(z=DROP_RELEASE_Z))

            if COMMENT_EVERY and cycle % COMMENT_EVERY == 0:
                protocol.comment(
                    f"  tip {well_name}: {cycle}/{NUM_CYCLES} cycles done"
                )
            if PAUSE_EVERY and cycle % PAUSE_EVERY == 0 and cycle < NUM_CYCLES:
                protocol.pause(
                    f"Tip {well_name} (bore {bore:.2f} mm) at {cycle} cycles. "
                    "Inspect the socket for whitening/cracks/loosening, record "
                    "it, then resume."
                )
        protocol.comment(
            f"=== Tip {well_name} finished {NUM_CYCLES} cycles ==="
        )


if __name__ == "__main__":
    print(json.dumps(TEST_ARRAY_LABWARE, indent=2))
