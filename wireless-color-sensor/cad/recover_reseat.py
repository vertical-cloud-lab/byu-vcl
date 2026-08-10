"""Finish the interrupted 2026-08-10 cycle: reseat the module left gripped at z=110.

The 2026-08-10 session (camera/pickup-test-2026-08-10-sensor-read-midair/) ended
with the sensor module still gripped on the P300 nozzle at (169.05, 225.0, 110)
over slot 8, because the RPi-5 network bridge went down before the return leg.
This script completes the proven recipe's remaining steps — and nothing else:

1. sanity-check the nozzle is still where the last session left it (savePosition),
2. lateral shift to the anti-tilt drop x (163.05) at z = 110,
3. staged slow descent z 108 -> 101 -> 95.5,
4. dropTipInPlace (module reseats on its slot-8 base),
5. straight-up clearance to z = 128, then home, then delete the maintenance run.

It deliberately does NOT start with `home` — a home would traverse the gantry at
full speed with the module and its overhead wire still aboard.

Run it from whichever machine currently has the OT-2's USB-Ethernet link
(the RPi-5, or the Windows box if the USB cable was moved there):

    python recover_reseat.py            # uses ROBOT_IP from my_secrets.py if present
    python recover_reseat.py 169.254.51.252
    python recover_reseat.py 169.254.51.252 --force   # skip the position check

If the position check fails (nozzle not near x=169, z=110), the robot has most
likely been restarted or moved and the module may already have fallen — stop and
look inside the robot before using --force.
"""

import sys
import time

import requests

# Proven coordinates from the 2026-08-10 session (wire-attached recipe)
HOLD_X, HOLD_Y, HOLD_Z = 169.05, 225.0, 110.0   # where the module was left gripped
DROP_X = 163.05                                  # anti-tilt drop x (pickup x - 6)
DESCENT_STAGES = [108.0, 101.0, 95.5]            # slow staged descent to release height
CLEAR_Z = 128.0                                  # straight-up retreat after release
POSITION_TOL_MM = 3.0                            # abort if nozzle further than this from HOLD_*

PIPETTE = {"pipetteName": "p300_single_gen2", "mount": "left"}


def get_robot_ip(argv):
    for a in argv[1:]:
        if not a.startswith("-"):
            return a
    try:
        from my_secrets import ROBOT_IP
        return ROBOT_IP
    except ImportError:
        return "169.254.51.252"


ROBOT_IP = get_robot_ip(sys.argv)
FORCE = "--force" in sys.argv
BASE = f"http://{ROBOT_IP}:31950"
HEADERS = {"Opentrons-Version": "3"}


def command(run_id, command_type, params, timeout=60):
    r = requests.post(
        f"{BASE}/maintenance_runs/{run_id}/commands",
        headers={**HEADERS, "Content-Type": "application/json"},
        params={"waitUntilComplete": "true"},
        json={"data": {"commandType": command_type, "params": params}},
        timeout=timeout,
    )
    r.raise_for_status()
    data = r.json()["data"]
    if data["status"] != "succeeded":
        raise RuntimeError(f"{command_type} failed: {data.get('error')}")
    return data.get("result") or {}


def main():
    health = requests.get(f"{BASE}/health", headers=HEADERS, timeout=10).json()
    print(f"robot: {health['name']} ({health['robot_model']})")

    print("creating maintenance run (supersedes any stale one)...")
    r = requests.post(f"{BASE}/maintenance_runs", headers=HEADERS,
                      json={"data": {}}, timeout=10)
    r.raise_for_status()
    run_id = r.json()["data"]["id"]
    print(f"maintenance run: {run_id}")

    try:
        pip = command(run_id, "loadPipette", PIPETTE)  # does not move the gantry
        pid = pip["pipetteId"]

        pos = command(run_id, "savePosition", {"pipetteId": pid})["position"]
        print(f"current nozzle position: x={pos['x']:.2f} y={pos['y']:.2f} z={pos['z']:.2f}")
        off = max(abs(pos["x"] - HOLD_X), abs(pos["y"] - HOLD_Y), abs(pos["z"] - HOLD_Z))
        if off > POSITION_TOL_MM and not FORCE:
            raise SystemExit(
                f"ABORT: nozzle is {off:.1f} mm from the expected hold position "
                f"({HOLD_X}, {HOLD_Y}, {HOLD_Z}) — the robot was likely restarted or "
                "moved and the module may have fallen. Inspect before using --force."
            )

        def move(x, y, z, speed):
            command(run_id, "moveToCoordinates", {
                "pipetteId": pid,
                "coordinates": {"x": x, "y": y, "z": z},
                "speed": speed,
                "forceDirect": True,
            }, timeout=120)
            print(f"  at ({x:.2f}, {y:.2f}, {z:.2f})")

        print(f"lateral shift to drop x={DROP_X} at z={HOLD_Z}...")
        move(DROP_X, HOLD_Y, HOLD_Z, speed=25)

        print("staged descent...")
        for z in DESCENT_STAGES:
            move(DROP_X, HOLD_Y, z, speed=10)
            time.sleep(0.5)

        print("releasing (dropTipInPlace)...")
        command(run_id, "dropTipInPlace", {"pipetteId": pid})

        print(f"clearance retreat to z={CLEAR_Z}...")
        move(DROP_X, HOLD_Y, CLEAR_Z, speed=20)

        print("homing...")
        command(run_id, "home", {}, timeout=120)
    finally:
        requests.delete(f"{BASE}/maintenance_runs/{run_id}", headers=HEADERS, timeout=10)
        print("maintenance run deleted.")

    print("DONE — module should be reseated on its slot-8 base. Verify visually.")


if __name__ == "__main__":
    main()
