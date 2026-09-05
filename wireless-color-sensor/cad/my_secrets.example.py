"""Local secrets for talking to the OT-2 over HTTP.

Copy this file to ``my_secrets.py`` and fill in your robot's IP address, then
run ``run_robot.py``.  ``my_secrets.py`` is git-ignored so the real address is
never committed.

Find the IP in the Opentrons App under *Robot Settings -> Networking*, or use
the wired self-assigned address shown on the robot.  Examples:

    ROBOT_IP = "169.254.51.252"   # USB / wired self-assigned
    ROBOT_IP = "192.168.1.42"     # Wi-Fi / LAN
"""

ROBOT_IP = "ROBOT_IP_HERE"
