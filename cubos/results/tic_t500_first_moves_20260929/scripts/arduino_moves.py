"""Small plunger moves through the Arduino (PANDA CMD 16, raw steps).

Run on the CubXL Pi with ~/CubOS/.venv/bin/python. Plunger only: the gantry
port is never opened. Args to send_command are separate varargs
(direction, steps, velocity), never a list (see 2026-09-24).
At 1/8 step on the Tic, 796 microsteps = 1 mm of plunger.
"""
import sys
import time

from cubos.instruments.controllers.pawduino import PawduinoLink

PORT = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00"
PLAN = [(14,)] + [tuple(int(x) for x in a.split(",")) for a in sys.argv[1:]] + [(14,)]


def stamp(t):
    return time.strftime("%H:%M:%S", time.localtime(t)) + f".{int((t % 1) * 1000):03d}"


link = PawduinoLink.acquire(PORT, 115200)
t0 = time.time()
link.connect()
print(f"{stamp(time.time())}  connected in {time.time() - t0:.2f} s", flush=True)
for step in PLAN:
    code, *args = step
    t = time.time()
    try:
        reply = link.send_command(code, *args, timeout=90)
    except Exception as exc:  # report, keep going
        reply = f"RAISED {exc!r}"
    dt = time.time() - t
    expect = ""
    if code == 16:
        expect = f"  (commanded {args[1] / args[2]:.2f} s = {args[1] / 796:.2f} mm at 1/8 step)"
    print(f"{stamp(t)}  cmd {code} {tuple(args)}  dt={dt:.3f} s{expect}  -> {reply}", flush=True)
    time.sleep(2.0)
link.disconnect()
print(f"{stamp(time.time())}  disconnected", flush=True)
