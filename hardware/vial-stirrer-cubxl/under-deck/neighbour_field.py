#!/usr/bin/env python3
"""Side by side: how much field a neighbouring stirrer puts on this one's Hall sensor, and on its bar.

The same magpylib model as ../analysis/field_check.py and coupling_through_deck.py: two 1/4 x 1/16 in
N52 discs, and the 15 x 6 mm bar with the strongest of the four guessed cores, its axis where it sits
under a 9 mm deck. Each neighbour turns through a full revolution; the table gives the largest |Bz|
that neighbour puts on the Hall element, against the US1881's worst-case trip points of +-9.5 mT, and
the largest horizontal field it puts at this module's bar, against the drive's own at the bar.

    python under-deck/neighbour_field.py > under-deck/neighbour_field_output.txt    # from hardware/vial-stirrer-cubxl
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
from field_check import MM, bar, drive  # noqa: E402

HALL = (-11.70, 0.0, 22.655)                  # the Hall element, stirrer frame, mm (field_check.py's spot)
GAP = 1.185 + 9.0                             # magnets to vial bottom under a 9 mm deck
BAR_Z = 22.645 + GAP + 1.6 + 3.0              # bar axis: vial's outside bottom + 1.6 mm glass + 3 mm (half the bar)
CORE = (1.0, 4, 12)                           # strongest of the four guessed cores (coupling_through_deck.py)
ANGS = np.arange(0.0, 360.0, 6.0)


def source(ang, dx, dy):
    """A neighbour's drive magnets and bar, turned to ang, moved to (dx, dy) mm."""
    objs = list(drive(ang).children) + [bar(ang, *CORE, BAR_Z)]
    for o in objs:
        o.move((dx * MM, dy * MM, 0))
    return objs


def peak(dx, dy, point, comp):
    vals = []
    for a in ANGS:
        b = sum(o.getB(np.array(point) * MM) for o in source(a, dx, dy)) / MM      # T -> mT
        vals.append(abs(b[2]) if comp == "z" else float(np.hypot(b[0], b[1])))
    return max(vals)


def main():
    own_at_bar = min(float(np.hypot(*drive(a).getB((0, 0, BAR_Z * MM))[:2])) / MM for a in (0.0, 45.0, 90.0))
    print(f"Hall element at {HALL[:2]} mm from the axis; bar axis {BAR_Z:.2f} mm (stirrer frame), core {CORE}")
    print(f"This module's own drive at its bar, horizontal: {own_at_bar:.1f} mT\n")
    print("neighbour at (mm)     max |Bz| at the Hall   max horizontal at the bar")
    total = 0.0
    for dx, dy in [(50, 0), (-50, 0), (0, 45), (0, -45), (50, 45), (-50, 45), (50, -45), (-50, -45), (75, 0), (-75, 0)]:
        h = peak(dx, dy, HALL, "z")
        b = peak(dx, dy, (0.0, 0.0, BAR_Z), "xy")
        if abs(dx) <= 50:
            total += h
        print(f"  ({dx:4d}, {dy:4d})          {h:6.3f} mT            {b:6.3f} mT ({100 * b / own_at_bar:4.2f} % of its own)")
    print(f"\nAll eight neighbours at 50 x 45, each at its worst angle at once: {total:.2f} mT at the Hall, "
          f"against 9.5 to trip it")


if __name__ == "__main__":
    main()
