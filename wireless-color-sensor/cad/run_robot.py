"""Upload an OT-2 protocol over HTTP and start the run.

Reads the robot address from ``my_secrets.py`` (copy ``my_secrets.example.py``
first and set ``ROBOT_IP``). This is the same upload path @timothy-commins used
in PR #60, with the hard-coded IP and protocol path factored out so nothing
secret is committed.

Usage::

    python run_robot.py                         # uploads protocol_cyclic_loading.py
    python run_robot.py protocol_fake_tip_test.py
    python run_robot.py path/to/any_protocol.py

Type ``cancel`` + Enter at any time to stop the robot.
"""

import os
import sys
import threading

import requests

try:
    from my_secrets import ROBOT_IP
except ImportError:  # pragma: no cover - guidance for first-time users
    sys.exit(
        "Missing my_secrets.py. Copy my_secrets.example.py to my_secrets.py "
        "and set ROBOT_IP to your OT-2's address."
    )

if not ROBOT_IP or ROBOT_IP == "ROBOT_IP_HERE":
    sys.exit("Set ROBOT_IP in my_secrets.py to your OT-2's address first.")

BASE_URL = f"http://{ROBOT_IP}:31950"
HEADERS = {"Opentrons-Version": "3"}

DEFAULT_PROTOCOL = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "protocol_cyclic_loading.py"
)

run_id = None


def cancel_run():
    if run_id is None:
        print("No active run to cancel.")
        return
    response = requests.post(
        f"{BASE_URL}/runs/{run_id}/actions",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"data": {"actionType": "stop"}},
    )
    if response.ok:
        print(f"Run {run_id} cancelled successfully.")
    else:
        print(f"Failed to cancel: {response.status_code} {response.text}")


def listen_for_cancel():
    while True:
        try:
            cmd = input()
        except EOFError:
            return
        if cmd.strip().lower() == "cancel":
            print("Cancelling run...")
            cancel_run()
            return


def run_protocol(protocol_path):
    global run_id

    print(f"Uploading {protocol_path} to {BASE_URL} ...")
    with open(protocol_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/protocols", headers=HEADERS, files={"files": f}
        )
    response.raise_for_status()
    protocol_id = response.json()["data"]["id"]
    print(f"Protocol uploaded. ID: {protocol_id}")

    print("Creating run...")
    response = requests.post(
        f"{BASE_URL}/runs",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"data": {"protocolId": protocol_id}},
    )
    response.raise_for_status()
    run_id = response.json()["data"]["id"]
    print(f"Run created. ID: {run_id}")

    listener = threading.Thread(target=listen_for_cancel, daemon=True)
    listener.start()
    print(">> Type 'cancel' + Enter at any time to stop the robot.")

    print("Starting run...")
    response = requests.post(
        f"{BASE_URL}/runs/{run_id}/actions",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"data": {"actionType": "play"}},
    )
    response.raise_for_status()
    print("Protocol is now running on the OT-2!")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROTOCOL
    if not os.path.isfile(path):
        sys.exit(f"Protocol file not found: {path}")
    run_protocol(path)
