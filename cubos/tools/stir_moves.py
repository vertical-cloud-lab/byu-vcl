#!/usr/bin/env python3
"""Print the YAML `move` steps that stir a vial with the pipette tip.

CubOS has no stir command, but a raw ``move`` whose ``travel_z`` equals its own
target Z keeps the tip at that depth and only moves XY. The driver
(``_build_transit_move`` at CubOS 496819c) sends one ``G01`` per changed axis,
X then Y, never a diagonal, and waits for Idle before the next. So a step that
changes both X and Y really goes X first, then Y, through a corner that is not
on the straight line. Every step this prints changes ONE axis, so the path that
runs is exactly the path written, and its farthest point is checked against
``--r-max``.

The path, all at one depth, from the vial centre and back to it:

  1. ``--laps`` square laps counter-clockwise, then the same clockwise.
     Corners at (+-a, +-a), a = r_max / sqrt(2) rounded down to 0.1 mm, so
     the corners sit just inside r_max.
  2. ``--strokes`` round trips along X through the centre, +-r_max.
  3. The same along Y.

    python cubos/tools/stir_moves.py --x 136.668 --y 78 --z 21 --r-max 5

Coordinates are the tipped pipette's frame (deck XY, tip-end Z), as in any raw
``move`` with ``instrument: pipette``.
"""
from __future__ import annotations

import argparse
import math


def path(r_max: float, laps: int, strokes: int) -> list[tuple[str, float, float]]:
    """(label, dx, dy) for each step after the tip is at the centre."""
    a = math.floor(r_max / math.sqrt(2) * 10) / 10
    pts = [("square entry", a, 0.0), ("square entry", a, a)]
    for _ in range(laps):                       # counter-clockwise from (a, a)
        pts += [("square ccw", -a, a), ("square ccw", -a, -a),
                ("square ccw", a, -a), ("square ccw", a, a)]
    for _ in range(laps):                       # clockwise from (a, a)
        pts += [("square cw", a, -a), ("square cw", -a, -a),
                ("square cw", -a, a), ("square cw", a, a)]
    pts.append(("to x axis", a, 0.0))
    for _ in range(strokes):
        pts += [("x stroke", -r_max, 0.0), ("x stroke", r_max, 0.0)]
    pts.append(("centre", 0.0, 0.0))
    for _ in range(strokes):
        pts += [("y stroke", 0.0, -r_max), ("y stroke", 0.0, r_max)]
    pts.append(("centre", 0.0, 0.0))
    return pts


def check(pts, r_max: float) -> None:
    prev = (0.0, 0.0)
    for label, dx, dy in pts:
        changed = (dx != prev[0]) + (dy != prev[1])
        assert changed == 1, f"{label} ({dx}, {dy}) changes {changed} axes from {prev}"
        assert math.hypot(dx, dy) <= r_max + 1e-9, f"{label} ({dx}, {dy}) is past r_max"
        prev = (dx, dy)
    assert prev == (0.0, 0.0), "the path must end at the centre"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--x", type=float, required=True, help="vial centre X, deck")
    ap.add_argument("--y", type=float, required=True, help="vial centre Y, deck")
    ap.add_argument("--z", type=float, required=True, help="tip-end Z to stir at, deck")
    ap.add_argument("--r-max", type=float, default=5.0,
                    help="farthest the tip axis goes from the centre, mm")
    ap.add_argument("--laps", type=int, default=5)
    ap.add_argument("--strokes", type=int, default=4)
    ap.add_argument("--instrument", default="pipette")
    a = ap.parse_args()
    pts = path(a.r_max, a.laps, a.strokes)
    check(pts, a.r_max)
    last = None
    for label, dx, dy in pts:
        if label != last:
            print(f"  # {label}")
            last = label
        x, y = round(a.x + dx, 3), round(a.y + dy, 3)
        print(f"  - move: {{instrument: {a.instrument}, position: [{x}, {y}, {a.z}], "
              f"travel_z: {a.z}}}")


if __name__ == "__main__":
    main()
