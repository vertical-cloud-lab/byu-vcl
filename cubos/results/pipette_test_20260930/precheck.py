"""Pre-run check after flashing the 796 image: both instrument paths, then HOME.

Talks to the shared Arduino exactly as CubOS does (PawduinoLink). Plunger only;
the gantry port is never opened. Prints wall-clock UTC and lab-local times.
"""
import time, datetime as dt
from cubos.instruments.controllers.pawduino import PawduinoLink

PORT = "/dev/ttyACM0"
def now():
    t = dt.datetime.now(dt.timezone.utc)
    return f"{t:%H:%M:%S}Z / {(t - dt.timedelta(hours=6)):%H:%M:%S} lab"

def cmd(link, label, code, *args, timeout=60):
    t0 = time.monotonic()
    try:
        r = link.send_command(code, *args, timeout=timeout)
    except Exception as e:  # PawduinoLink raises on ERR replies
        r = f"RAISED {e!r}"
    print(f"{now()}  {label:<28} dt={time.monotonic()-t0:7.3f}s  {r}", flush=True)
    return r

link = PawduinoLink.acquire(PORT, 115200)
t0 = time.monotonic(); link.connect(); print(f"{now()}  connect() {time.monotonic()-t0:.2f}s", flush=True)
cmd(link, "cmd 14 pipette STATUS", 14)
cmd(link, "cmd  7 cap sensor", 7)
cmd(link, "cmd 10 HOME", 10)
cmd(link, "cmd 14 pipette STATUS", 14)
link.close()
