#!/usr/bin/env python3
"""Report which OT-2 calibrations are present and which are missing.

Read-only: every call is a GET, nothing moves. Run it from the Pi that holds the
OT-2's ethernet link (see README) -- the robot answers only on its link-local
address.

    python3 calibration_status.py
    python3 calibration_status.py --labware ac_color_sensor_charging_port.json

The three robot calibrations must be done in order -- deck, tip length, pipette
offset -- because calibrating the deck clears the other two. Labware Position
Check comes last and is part of a protocol run, not of Robot Settings.

Any labware with "isTiprack": true needs its OWN tip length calibration with the
attached pipette, custom definitions included. The sensor dock is defined as a
tiprack, so it counts. Pass --labware to check a definition's URI against what
the robot has stored.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

DEFAULT_HOST = "http://169.254.51.252:31950"
HEADERS = {"Opentrons-Version": "3"}


def get(host: str, path: str, timeout: float = 15.0) -> dict:
    req = urllib.request.Request(host.rstrip("/") + path, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def labware_uri(definition: dict) -> str:
    """Reproduce Opentrons' getLabwareDefURI: namespace/loadName/version."""
    return "{}/{}/{}".format(
        definition.get("namespace", "custom_beta"),
        definition["parameters"]["loadName"],
        definition.get("version", 1),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default=DEFAULT_HOST,
                        help="robot base URL (default: the link-local address)")
    parser.add_argument("--labware", action="append", default=[], metavar="FILE",
                        help="labware definition JSON to check; repeatable")
    parser.add_argument("--json", action="store_true", help="emit the raw findings as JSON")
    args = parser.parse_args()

    try:
        health = get(args.host, "/health")
        pipettes = get(args.host, "/pipettes")
        status = get(args.host, "/calibration/status")
        tip_length = get(args.host, "/calibration/tip_length").get("data", [])
        offsets = get(args.host, "/calibration/pipette_offset").get("data", [])
        networking = get(args.host, "/networking/status")
    except (urllib.error.URLError, OSError) as exc:
        print(f"cannot reach the robot at {args.host}: {exc}", file=sys.stderr)
        print("check /sys/class/net/eth1/carrier on the Pi -- 0 means the cable is out",
              file=sys.stderr)
        return 2

    # /labwareOffsets rejects a pageLength parameter on this robot software; ask bare.
    try:
        stored_offsets = get(args.host, "/labwareOffsets").get("data", [])
    except (urllib.error.URLError, OSError):
        stored_offsets = []

    problems: list[str] = []
    print(f"robot   {health.get('name')}  API {health.get('api_version')}  "
          f"system {health.get('system_version')}")

    deck = status.get("deckCalibration", {})
    deck_data = deck.get("data") or {}
    print(f"\ndeck calibration        {deck.get('status')}  "
          f"last {str(deck_data.get('lastModified'))[:10]}  "
          f"with pipette {deck_data.get('pipetteCalibratedWith')}")
    if deck.get("status") != "OK":
        problems.append("deck calibration is not OK -- do it first, it clears the others")

    for mount in ("left", "right"):
        pipette = pipettes.get(mount) or {}
        serial = pipette.get("id")
        if not serial:
            continue
        print(f"\n{mount} mount            {pipette.get('model')}  {serial}")

        if deck_data.get("pipetteCalibratedWith") not in (None, serial):
            print("  note: the deck was calibrated with a different pipette "
                  "(fine -- deck calibration is robot-level, not per-pipette)")

        mine = [d for d in tip_length if d["pipette"] == serial]
        if mine:
            for d in mine:
                print(f"  tip length     OK   {d['uri']}  "
                      f"{d['tipLength']:.2f} mm  last {d['lastModified'][:10]}")
        else:
            print(f"  tip length     MISSING   (robot holds {len(tip_length)} entries, "
                  "none for this pipette)")
            problems.append(f"tip length calibration missing for {mount} pipette {serial}")

        my_offsets = [d for d in offsets if d["pipette"] == serial]
        if my_offsets:
            for d in my_offsets:
                print(f"  pipette offset OK   {[round(v, 2) for v in d['offset']]}  "
                      f"last {d['lastModified'][:10]}")
        else:
            print("  pipette offset MISSING")
            problems.append(f"pipette offset calibration missing for {mount} pipette {serial}")

        for path in args.labware:
            with open(path) as handle:
                definition = json.load(handle)
            if not definition["parameters"].get("isTiprack"):
                print(f"  {definition['parameters']['loadName']}: not a tiprack, "
                      "no tip length calibration needed")
                continue
            uri = labware_uri(definition)
            have = any(d["pipette"] == serial and d["uri"] == uri for d in tip_length)
            print(f"  tiprack {uri}  ->  {'OK' if have else 'MISSING'}")
            if not have:
                problems.append(f"tip length calibration missing for {uri} on {serial}")

    print(f"\nlabware offsets (LPC)   {len(stored_offsets)} stored")
    if not stored_offsets:
        problems.append("no Labware Position Check has been run -- it is per labware AND slot")

    interfaces = networking.get("interfaces") or {}
    reachable_off_pi = any(
        iface.get("state") == "connected" and iface.get("gatewayAddress")
        for iface in interfaces.values()
    )
    print(f"networking              {networking.get('status')}  " + "  ".join(
        f"{name}={iface.get('state')}" for name, iface in sorted(interfaces.items())))
    if not reachable_off_pi:
        problems.append("no routable network: the Opentrons App cannot reach the robot. "
                        "Connect a USB-B cable to the computer running the app, or put "
                        "the robot on the lab network")

    print()
    if problems:
        print(f"{len(problems)} thing(s) to fix, in this order:")
        for i, problem in enumerate(problems, 1):
            print(f"  {i}. {problem}")
    else:
        print("everything the app checks before a run is present")

    if args.json:
        print(json.dumps({"problems": problems}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
