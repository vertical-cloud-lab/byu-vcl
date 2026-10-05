"""Third probe, 2026-10-05: a longer UP search, gated by the switch.

After tmc2209_probe.py (UP 3 mm, no switch) and tmc2209_probe_down.py (DOWN 6 mm,
no switch), the plunger is ~1 mm below the switch plus a net 3 mm DOWN if the
motor turns the right way at 1/8 step. A finer microstep than 1/8 (1/32 or 1/64
from MS1/MS2 straps on a different module) would also explain both misses, and
would leave it only ~1.4-1.8 mm below. So: UP in 0.5 mm chunks at 400/s, at most
12 mm (commanded). UP moves stop at the switch, so this can't overrun the top. On
a reversed motor (already excluded at 1/8 by the DOWN probe) it would go down at
most 12 mm. No HOME.

Exit status: 0 = the switch opened (the motor turns, and DIR LOW is up), 1 = it never did.
"""
import json
import sys
import time

from cubos.instruments.controllers.pawduino import PawduinoLink

PORT = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00"
UP, DOWN = 0, 1
SPMM, PROBE, CHUNK_MM, MAX_MM = 796.0, 400, 0.5, 12.0
OUT = sys.argv[1] if len(sys.argv) > 1 else "tmc2209_probe_up12.json"
rows = []


def stamp(t=None):
    t = time.time() if t is None else t
    return time.strftime("%H:%M:%S", time.gmtime(t)) + f".{int((t % 1) * 1000):03d}Z"


def say(msg):
    print(f"{stamp()}  {msg}", flush=True)


link = PawduinoLink.acquire(PORT, 115200)


def cmd(code, *args, timeout=60):
    t = time.time()
    try:
        reply = str(link.send_command(code, *args, timeout=timeout))
    except Exception as exc:                                  # noqa: BLE001
        reply = f"ERR {exc}" if "ERR:" in str(exc) else f"RAISED {exc!r}"
    dt = time.time() - t
    rows.append({"t": stamp(t), "code": code, "args": list(args), "dt_s": round(dt, 3),
                 "reply": reply})
    return reply, t, dt


link.connect()
say(f"connected; STATUS -> {cmd(14)[0]}")
steps, sent, code = int(round(CHUNK_MM * SPMM)), 0.0, 1
while sent < MAX_MM - 1e-9:
    reply, t, dt = cmd(16, UP, steps, PROBE, timeout=steps / PROBE + 30)
    if reply.startswith("ERR"):
        part = max(0.0, (dt - 0.10) * PROBE / SPMM)
        say(f"UP chunk after {sent:.1f} mm: REFUSED/STOPPED after ~{part:.2f} mm (dt {dt:.3f} s)"
            f" -> {reply[:80]}")
        say(f"RESULT: the switch opened after ~{sent + part:.2f} mm commanded UP: the motor turns, "
            f"and DIR LOW is up.")
        code = 0
        break
    if not reply.startswith("OK"):
        say(f"UP chunk -> {reply[:90]}; stopping")
        break
    sent += CHUNK_MM
    say(f"UP {sent:5.1f} mm sent (dt {dt:.3f} s): no switch")
else:
    say(f"RESULT: no switch within {MAX_MM} mm commanded UP.")
say(f"EMAG_OFF -> {cmd(6)[0]}")
link.disconnect()
with open(OUT, "w") as fh:
    json.dump({"up_mm_sent": sent, "switch_opened": code == 0, "rows": rows}, fh, indent=2)
say(f"disconnected; exit {code}")
sys.exit(code)
