#!/usr/bin/env python3
"""Put the sensor module back on its base when a release failed to let go.

``run_xscan_test.py`` ends by pressing the module into its base and firing the
pipette's tip ejector (``dropTipInPlace``). On 2026-09-10 that ejector fired
and the module stayed on the nozzle, so the gantry homed still carrying it and
the reseat-confirmation read came back 1010 counts against a seated 406 -- the
module in mid-air seeing the room, not the inside of a closed base.

That is a *recoverable* failure and a different one from 2026-09-09, when the
module came off entirely and lay on the deck. The distinction is the whole
reason this script exists:

  * module on the deck  -> its position and orientation are unknown, so
    pressing the nozzle onto it is blind. Needs hands. Do not automate.
  * module on the nozzle -> its position is exactly known, and the release
    that failed is the same one that succeeded minutes earlier at the same
    press depth. Retrying it is ordinary recovery.

Read the sensor first. Counts near the seated baseline (~400-470) mean it is
already on its base and there is nothing to do; anything above ~800 means it
is still aboard. Confirm with ``deck_photo.py`` before running this, because
the count alone cannot tell "on the nozzle" from "on the deck".

    python3 reseat_module.py --check          # read the sensor, move nothing
    python3 reseat_module.py                  # retry the release as-is
    python3 reseat_module.py --extra-press 0.5  # ... 0.5 mm deeper

A tighter press was added on 2026-09-09 to stop the module falling off
mid-run, and this is that fix's other edge: the fit that will not shed the
module in transit is also the fit that sometimes will not let go of it. If a
plain retry fails, ``--extra-press`` drives the module further into the base
so the base has more to hold while the ejector pushes.
"""
from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_xscan_test import (  # noqa: E402
    CARRY_Z, CLEAR_Z, DESCENT_SPEED, DROP_DESCENT, DROP_DX, PRESS_Z,
    BASE_DX, BASE_DY, DEFAULT_ROBOT_IP, HOME_SLOT, Robot, log,
)
import deck  # noqa: E402
from sensor_read import SensorError, SensorLink  # noqa: E402

SEATED_MAX = 800   # above this, the module is not closed on its base


def read_total(link, label, n=2):
    totals = []
    for i in range(n):
        r = link.read(label=f"{label}-{i + 1}")
        totals.append(r["total"])
        log(f"  read {i + 1}/{n}  total={totals[-1]}")
    return sum(totals) / len(totals)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--robot-ip", default=os.environ.get("OT2_IP", DEFAULT_ROBOT_IP))
    p.add_argument("--home-slot", type=int, default=HOME_SLOT)
    p.add_argument("--base-dx", type=float, default=BASE_DX)
    p.add_argument("--base-dy", type=float, default=BASE_DY)
    p.add_argument("--press-z", type=float, default=90.0,
                   help="press depth the failed run used (default: 90.0)")
    p.add_argument("--extra-press", type=float, default=0.0,
                   help="drive this many mm deeper before firing the ejector")
    p.add_argument("--check", action="store_true",
                   help="read the sensor and stop; no robot motion at all")
    args = p.parse_args(argv)

    origin = deck.slot_origin(args.home_slot)
    x = round(origin[0] + args.base_dx + DROP_DX, 2)
    y = round(origin[1] + args.base_dy, 2)
    release_z = round(DROP_DESCENT[-1] + (args.press_z - PRESS_Z) - args.extra_press, 2)

    link = SensorLink()
    link.connect()
    try:
        log("before: is the module on its base?")
        before = read_total(link, "reseat-before")
        if before <= SEATED_MAX:
            log(f"  {before:.0f} counts -- already seated. Nothing to do.")
            return 0
        log(f"  {before:.0f} counts -- NOT seated (seated reads ~400-470).")
        if args.check:
            log("--check: stopping before any motion.")
            return 1

        robot = Robot(args.robot_ip)
        robot.open()
        try:
            robot.home()
            log(f"carrying to the drop-off column ({x}, {y})")
            robot.carry_to(x, y, CARRY_Z)
            log(f"staged descent, releasing at z={release_z:g}")
            for z in [z for z in list(DROP_DESCENT[:-1]) + [release_z] if z < CARRY_Z]:
                robot.move(x, y, z, speed=DESCENT_SPEED)
                time.sleep(0.4)
            robot.drop_tip_in_place()
            robot.move(x, y, CLEAR_Z, speed=20.0)
            robot.home()
        finally:
            robot.close()

        log("after: confirming by sensor")
        after = read_total(link, "reseat-after")
        if after <= SEATED_MAX:
            log(f"  {before:.0f} -> {after:.0f}: back on its base.")
            return 0
        log(f"  {before:.0f} -> {after:.0f}: STILL NOT SEATED. "
            "Photograph the deck before trying again -- if it is now on the "
            "deck rather than on the nozzle, this script must not be re-run.")
        return 2
    except SensorError as exc:
        log(f"sensor did not answer: {exc}")
        return 3
    finally:
        link.close()


if __name__ == "__main__":
    raise SystemExit(main())
