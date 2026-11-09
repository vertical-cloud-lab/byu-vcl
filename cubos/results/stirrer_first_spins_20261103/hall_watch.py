"""Fan off: read the Hall input once a second (31's rpm = 30 x falling edges per 2 s window)."""
import json, sys, time
from datetime import datetime, timezone
from cubos.instruments.controllers.pawduino import PawduinoLink
PORT = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00"
secs = float(sys.argv[1]); label = sys.argv[2]
utc = lambda: datetime.now(timezone.utc).strftime("%H:%M:%S") + "Z"
out = open(f"{label}.jsonl", "a")
link = PawduinoLink.acquire(PORT, 115200); link.connect()
print(utc(), "watching, fan off:", link.send_command(30, 0, timeout=5), flush=True)
t0 = time.monotonic(); last_print = 0; edges = 0
try:
    while time.monotonic() - t0 < secs:
        time.sleep(1.0)
        s = link.send_command(31, timeout=5)
        d = json.loads(s.split(":", 1)[1]); d["utc"] = utc()
        out.write(json.dumps(d) + "\n"); out.flush()
        if d["rpm"] > 0 or time.monotonic() - last_print > 30:
            print(d["utc"], s, flush=True); last_print = time.monotonic()
finally:
    link.disconnect()
