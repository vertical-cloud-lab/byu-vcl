"""Release the enclosure over its own pocket, from a stopped run. Used once, 2026-09-29.

enclosure_height_cal.py was stopped (SIGTERM, no motion) with the enclosure
hanging just above its seat in socket A2, at (92.8, 316.5, 94.0), after it
failed the in-pocket grip test. Its 10-minute timeout would have lifted it to
z 130 and moved it. This is the script's back_out() done by hand: rise to
press_z + 5 = 95, eject, rise to 110, photograph. It refuses to move unless
the nozzle is where that run left it.

    python3 release_in_place.py <maintenance-run-id>

The script's own ``release-here`` command now does the same from inside a run,
and its timeout does too when the enclosure is still inside the pocket.
"""
import subprocess, sys, time, os
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_xscan_test import Robot, HEADERS

IP = "169.254.51.252"
r = Robot(IP)
r.run_id = sys.argv[1]
r.pipette_id = requests.get(f"http://{IP}:31950/maintenance_runs/{r.run_id}", headers=HEADERS,
                            timeout=10).json()["data"]["pipettes"][0]["id"]
FF = os.path.expanduser("~/ytframes/bin/ffmpeg")

def photo(name):
    raw = name + "_raw.jpg"
    p = requests.post(f"http://{IP}:31950/camera/picture", headers=HEADERS, timeout=30)
    p.raise_for_status()
    open(raw, "wb").write(p.content)
    subprocess.run([FF, "-loglevel", "error", "-y", "-i", raw, "-vf", "hflip,vflip", "-q:v", "3",
                    name + "_robot.jpg"], check=True)
    os.remove(raw)
    print("photo", name + "_robot.jpg", flush=True)

pos = r.position()
print("position", pos, flush=True)
if abs(pos["x"] - 92.8) > 0.05 or abs(pos["y"] - 316.5) > 0.05 or not 93.5 <= pos["z"] <= 95.0:
    sys.exit("not where expected; stopping without motion")
step = sys.argv[2] if len(sys.argv) > 2 else "eject"
if step == "eject":
    r.move(92.8, 316.5, 95.0, 5.0)
    time.sleep(0.5)
    photo("12_release_pose_z95")
    r.drop_tip_in_place()
    time.sleep(0.5)
    r.move(92.8, 316.5, 110.0, 10.0)
    time.sleep(1.0)
    photo("13_after_eject_z110")
