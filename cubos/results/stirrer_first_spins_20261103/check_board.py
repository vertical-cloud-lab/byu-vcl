"""After the flash: does the board answer the stirrer and the pipette? Nothing moves."""
import time
from datetime import datetime, timezone
from cubos.instruments.controllers.pawduino import PawduinoLink

PORT = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00"
now = lambda: datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3] + "Z"
link = PawduinoLink.acquire(PORT, 115200)
print(now(), "connect (resets the Uno)")
link.connect()
for code, label in [(31, "stirrer status"), (14, "pipette STATUS"), (29, "pipette driver status")]:
    t = time.monotonic()
    try:
        r = link.send_command(code, timeout=15)
    except Exception as e:  # report and keep going
        r = f"ERROR {type(e).__name__}: {e}"
    print(f"{now()}  {code:>2} {label:<22} {time.monotonic() - t:5.2f} s  {r}")
link.disconnect()
print(now(), "disconnected")
