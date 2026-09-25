#!/usr/bin/env python3
"""Read or set the OT-2's deck rail lights. No motion, one HTTP call.

The rails are the only controllable light source this rig has. The sensor
module's own LEDs are inert -- ``led_probe.py`` walked R/Y/B from 0 to 255 on
2026-09-09 and every level came back 437-439 counts -- so with the rails off
every reading is a survey of whatever the room happens to be doing, and the
room turned out to be the largest variable in the experiment.

``/robot/lights`` is a top-level endpoint: no maintenance run, no pipette, no
gantry movement. It is safe to call with the deck loaded, mid-experiment, or
with the module closed on its base.

Must be run from the Pi that holds the OT-2's USB-ethernet link -- the robot
answers only on its link-local address.

    python3 robot_lights.py            # report the current state
    python3 robot_lights.py --on
    python3 robot_lights.py --off
"""
import argparse
import os
import sys

import requests

DEFAULT_ROBOT_IP = "169.254.51.252"
HEADERS = {"Opentrons-Version": "3"}


def lights(ip, on=None, timeout=10):
    """GET the rail-light state, or POST a new one. Returns the state after."""
    url = f"http://{ip}:31950/robot/lights"
    if on is None:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
    else:
        r = requests.post(url, headers={**HEADERS, "Content-Type": "application/json"},
                          json={"on": bool(on)}, timeout=timeout)
    r.raise_for_status()
    return bool(r.json().get("on"))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--robot-ip", default=os.environ.get("OT2_IP", DEFAULT_ROBOT_IP))
    g = p.add_mutually_exclusive_group()
    g.add_argument("--on", action="store_true", help="switch the rail lights on")
    g.add_argument("--off", action="store_true", help="switch the rail lights off")
    args = p.parse_args(argv)

    want = True if args.on else (False if args.off else None)
    try:
        before = lights(args.robot_ip)
    except requests.RequestException as exc:
        print(f"could not reach the OT-2 at {args.robot_ip}: {exc}", file=sys.stderr)
        return 2

    if want is None:
        print(f"rail lights: {'ON' if before else 'off'}")
        return 0

    after = lights(args.robot_ip, on=want)
    print(f"rail lights: {'ON' if before else 'off'} -> {'ON' if after else 'off'}")
    # The robot echoes the state it actually reached, so a mismatch is a real
    # failure rather than a slow response -- report it instead of assuming.
    return 0 if after == want else 1


if __name__ == "__main__":
    raise SystemExit(main())
