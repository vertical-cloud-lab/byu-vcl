#!/usr/bin/env python3
"""Check every coordinate the X-scan test will visit against the OT-2 simulator.

``run_xscan_test.py --simulate`` prints the motion plan; this takes that plan
and pushes each point through ``opentrons.simulate`` so the robot's own axis
limits get a vote. It exists because an out-of-range move fails *mid-carry*,
with the sensor package hanging on the nozzle -- much better to find it here.

The simulator only *logs* "Out of bounds move" rather than raising, so this
installs a log handler and treats any such record as a failure.

    pip install opentrons
    python3 check_reachability.py
    python3 check_reachability.py --home-slot 10 --scan-slot 8

Also re-derives the slot origins in ``deck.py`` from the packaged Opentrons
deck definition, so the hard-coded copy cannot drift from upstream.
"""

from __future__ import annotations

import glob
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deck  # noqa: E402
import run_xscan_test as xs  # noqa: E402


class BoundsCatcher(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.violations = []

    def emit(self, record):
        msg = record.getMessage()
        if "Out of bounds move" in msg:
            self.violations.append(msg)


def check_deck_table():
    """Compare deck.SLOT_ORIGINS against the packaged Opentrons definition."""
    import opentrons_shared_data as osd

    base = os.path.dirname(osd.__file__)
    hits = sorted(glob.glob(
        os.path.join(base, "**", "deck", "definitions", "3", "ot2_standard.json"),
        recursive=True))
    if not hits:
        print("  deck definition not found in opentrons_shared_data; skipping")
        return True
    upstream = json.load(open(hits[0]))
    ok = True
    for slot in upstream["locations"]["orderedSlots"]:
        num = int(slot["id"])
        want = (round(slot["position"][0], 2), round(slot["position"][1], 2))
        got = tuple(round(v, 2) for v in deck.SLOT_ORIGINS[num])
        if want != got:
            print(f"  MISMATCH slot {num}: deck.py has {got}, upstream has {want}")
            ok = False
    print(f"  slot origins match the packaged deck definition: "
          f"{'PASS' if ok else 'FAIL'}")
    return ok


def plan_points(args):
    """Every (x, y, z) the real run will command, in order."""
    plan = xs.build_plan(args)
    px, py = plan["pickup"]["x"], plan["pickup"]["y"]
    dx, dy = plan["drop_off"]["x"], plan["drop_off"]["y"]
    pts = [("descent-ladder", px, py, z) for z in xs.DESCENT_LADDER]
    pts.append(("entry", px, py, xs.ENTRY_Z))
    pts.append(("press", px, py, xs.PRESS_Z))
    pts.append(("lift-test", px, py, xs.LIFT_Z))
    pts += [("high-lift", px, py, z) for z in xs.high_lift_stages(args.carry_z)]
    for pos in plan["positions"]:
        pts.append((f"carry-to-pos{pos['index']}", pos["x"], pos["y"], args.carry_z))
        pts.append((f"read-pos{pos['index']}", pos["x"], pos["y"], pos["z"]))
        pts.append((f"lift-pos{pos['index']}", pos["x"], pos["y"], args.carry_z))
    pts.append(("return-carry", dx, dy, args.carry_z))
    pts += [("drop-descent", dx, dy, z) for z in xs.DROP_DESCENT]
    pts.append(("clearance", dx, dy, xs.CLEAR_Z))
    return plan, pts


def main(argv=None):
    args = xs.parse_args(argv or sys.argv[1:])
    plan, pts = plan_points(args)

    print(f"\n=== reachability check: slot {args.home_slot} -> slot {args.scan_slot} ===\n")
    print("  geometry")
    geometry_ok = check_deck_table()
    for pos in plan["positions"]:
        print(f"  read {pos['index']} at ({pos['x']}, {pos['y']}) is "
              f"{pos['slot_margin_mm']} mm inside slot {args.scan_slot}")

    from opentrons.simulate import get_protocol_api
    from opentrons.types import Location, Point

    catcher = BoundsCatcher()
    logging.getLogger().addHandler(catcher)
    logging.getLogger().setLevel(logging.DEBUG)

    protocol = get_protocol_api("2.13")
    pipette = protocol.load_instrument(xs.PIPETTE["pipetteName"], xs.PIPETTE["mount"])
    protocol.home()

    print(f"\n  simulator ({xs.PIPETTE['pipetteName']}, {xs.PIPETTE['mount']} mount)")
    failures = []
    for stage, x, y, z in pts:
        before = len(catcher.violations)
        pipette.move_to(Location(Point(x, y, z), None), force_direct=True)
        if len(catcher.violations) > before:
            failures.append((stage, x, y, z, catcher.violations[-1]))
    print(f"    {len(pts)} points checked, {len(failures)} out of bounds")
    for stage, x, y, z, msg in failures:
        print(f"      FAIL {stage} ({x}, {y}, {z}): {msg}")

    ok = geometry_ok and not failures
    print(f"\n  RESULT: {'PASS' if ok else 'FAIL'}\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
