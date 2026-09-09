"""OT-2 standard deck geometry, and the slot/offset math the X-scan test uses.

Values are the slot origins from the Opentrons deck definition
(``opentrons_shared_data/data/deck/definitions/3/ot2_standard.json``), copied
here so the geometry helpers work on a Raspberry Pi that has no ``opentrons``
package installed. ``check_geometry.py`` re-derives them from that file when
the package *is* available, so the copy cannot silently drift.
"""

from __future__ import annotations

SLOT_ORIGINS = {
    1: (0.0, 0.0),     2: (132.5, 0.0),     3: (265.0, 0.0),
    4: (0.0, 90.5),    5: (132.5, 90.5),    6: (265.0, 90.5),
    7: (0.0, 181.0),   8: (132.5, 181.0),   9: (265.0, 181.0),
    10: (0.0, 271.5), 11: (132.5, 271.5),  12: (265.0, 271.5),
}

SLOT_X_SIZE = 128.0
SLOT_Y_SIZE = 86.0

# Labware footprint inside a slot (SBS). Used for slot centres -- the slot
# itself is 128 x 86 but a plate is 127.76 x 85.48.
LABWARE_X_SIZE = 127.76
LABWARE_Y_SIZE = 85.48


def slot_origin(slot):
    try:
        return SLOT_ORIGINS[int(slot)]
    except KeyError:
        raise ValueError(f"slot must be 1-12, got {slot!r}") from None


def slot_center(slot):
    ox, oy = slot_origin(slot)
    return (ox + LABWARE_X_SIZE / 2.0, oy + LABWARE_Y_SIZE / 2.0)


def in_slot(slot, dx, dy):
    """Absolute deck (x, y) for a point ``(dx, dy)`` from the slot's front-left corner."""
    ox, oy = slot_origin(slot)
    return (ox + dx, oy + dy)


def which_slot(x, y):
    """Return the slot number containing deck point ``(x, y)``, or ``None``."""
    for slot, (ox, oy) in SLOT_ORIGINS.items():
        if ox <= x <= ox + SLOT_X_SIZE and oy <= y <= oy + SLOT_Y_SIZE:
            return slot
    return None


def slot_margin(slot, x, y):
    """Smallest distance from ``(x, y)`` to the edge of ``slot``.

    Negative means the point is outside the slot. Used as a preflight so a
    mis-typed offset is caught before the gantry carries the sensor package
    off the edge of a slot.
    """
    ox, oy = slot_origin(slot)
    return min(x - ox, ox + SLOT_X_SIZE - x, y - oy, oy + SLOT_Y_SIZE - y)
