import time, datetime as dt
from cubos.instruments.controllers.pawduino import PawduinoLink
link = PawduinoLink.acquire("/dev/ttyACM0", 115200); link.connect()
for label, code in (("cmd 6 EMAG_OFF", 6), ("cmd 7 cap sensor", 7), ("cmd 14 pipette STATUS", 14)):
    t0 = time.monotonic()
    try: r = link.send_command(code, timeout=10)
    except Exception as e: r = f"RAISED {e!r}"
    print(f"{dt.datetime.now(dt.timezone.utc):%H:%M:%S}Z  {label:<22} dt={time.monotonic()-t0:.3f}s  {r}", flush=True)
