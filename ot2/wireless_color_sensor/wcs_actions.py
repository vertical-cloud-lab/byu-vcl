"""Reusable Opentrons OT-2 actions for the BYU-VCL Wireless Color Sensor (WCS).

These helper functions wrap the low-level Opentrons API calls needed to
manipulate the wireless color sensor with a single-channel pipette. They are
intended to be imported by individual OT-2 protocol scripts so that the same
"internal actions" can be reused across many experiments.

The wireless color sensor is treated by the Opentrons API as a long tip that
lives in a custom "charging port" labware (a 2-well rack). Picking up the
sensor is therefore a normal ``pick_up_tip`` call, and returning it is a
``drop_tip`` call to a position above the charging well so the sensor seats
gently back into the holder.

Default assumptions (matching the issue's setup, mirrored from the
Acceleration Consortium reference):

* The charging port labware is loaded in deck slot 10.
* The sensor sits in well ``A2`` of the charging port (``A1`` is the empty
  parking well used by AC's reference setup).
* A ``p20_single_gen2`` pipette is mounted on the right.

All public functions take the protocol object, the pipette, and the
charging-port labware so they can be wired up to whatever objects the
calling protocol has loaded.
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional

# Default well in the charging port labware where the wireless color sensor
# is parked. Matches the Acceleration Consortium reference.
WCS_PARK_WELL: str = "A2"

# Default deck slot for the charging port labware. Per the issue, the WCS
# lives in slot 10.
WCS_DEFAULT_SLOT: int = 10

# Path to the bundled custom labware definition. Protocols that want to
# load the labware from disk (e.g. when running via ``opentrons.simulate``)
# can pass this constant to :func:`load_wcs_charging_port`.
LABWARE_DEFINITION_PATH: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "labware",
    "byu_color_sensor_charging_port.json",
)


def load_wcs_charging_port(
    protocol: Any,
    slot: int = WCS_DEFAULT_SLOT,
    definition_path: str = LABWARE_DEFINITION_PATH,
) -> Any:
    """Load the BYU wireless color sensor charging port labware.

    Parameters
    ----------
    protocol:
        The ``ProtocolContext`` passed into the protocol's ``run`` function.
    slot:
        Deck slot to load the labware into. Defaults to slot 10.
    definition_path:
        Path to the custom labware JSON definition.

    Returns
    -------
    The loaded labware object, which behaves as a tip rack and can be passed
    to :func:`pick_up_wcs` / :func:`return_wcs`.
    """
    with open(definition_path, encoding="utf-8") as f:
        labware_def = json.load(f)
    return protocol.load_labware_from_definition(labware_def, slot)


def pick_up_wcs(
    pipette: Any,
    charging_port: Any,
    well: str = WCS_PARK_WELL,
) -> None:
    """Pick up the wireless color sensor from its charging port.

    The Opentrons API treats the sensor as an oversized tip, so picking it
    up is just ``pipette.pick_up_tip`` targeted at the sensor's well.
    """
    pipette.pick_up_tip(charging_port[well])


def return_wcs(
    pipette: Any,
    charging_port: Any,
    well: str = WCS_PARK_WELL,
    drop_z_offset: float = -80.0,
) -> None:
    """Return the wireless color sensor to its charging port.

    A negative ``drop_z_offset`` relative to the well top is used so the
    sensor is released near the bottom of the holder rather than dropped
    from full tip height. The default of ``-80 mm`` matches the
    Acceleration Consortium reference protocol that has been validated on
    real hardware.
    """
    pipette.drop_tip(charging_port[well].top(z=drop_z_offset))


def move_wcs_to(
    pipette: Any,
    location: Any,
    speed: Optional[float] = None,
) -> None:
    """Move the (already picked up) wireless color sensor to ``location``.

    Parameters
    ----------
    pipette:
        The pipette currently holding the sensor.
    location:
        Any Opentrons ``Location`` (e.g. ``plate["A1"].top(z=-1.3)``).
    speed:
        Optional gantry speed override in mm/s. If ``None``, the pipette's
        current default speed is used.
    """
    if speed is not None:
        pipette.move_to(location, speed=speed)
    else:
        pipette.move_to(location)


def pick_up_and_return_wcs(
    pipette: Any,
    charging_port: Any,
    well: str = WCS_PARK_WELL,
) -> None:
    """Convenience: pick the sensor up and immediately put it back down.

    Used by the simplest mechanical sanity-check protocol.
    """
    pick_up_wcs(pipette, charging_port, well=well)
    return_wcs(pipette, charging_port, well=well)


def pick_up_move_and_return_wcs(
    protocol: Any,
    pipette: Any,
    charging_port: Any,
    move_location: Any,
    well: str = WCS_PARK_WELL,
    dwell_seconds: float = 1.0,
) -> None:
    """Convenience: pick up the sensor, move it, pause, and return it.

    Parameters
    ----------
    protocol:
        Protocol context, used for the dwell ``delay``.
    move_location:
        Where to take the sensor before returning it.
    dwell_seconds:
        How long to hold the sensor at ``move_location`` before returning.
    """
    pick_up_wcs(pipette, charging_port, well=well)
    move_wcs_to(pipette, move_location)
    if dwell_seconds > 0:
        protocol.delay(seconds=dwell_seconds)
    return_wcs(pipette, charging_port, well=well)
