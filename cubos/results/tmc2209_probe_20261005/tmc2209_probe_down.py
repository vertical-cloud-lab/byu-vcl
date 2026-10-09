"""Second probe, 2026-10-05: is the TMC2209 turning the plunger backwards?

tmc2209_probe.py sent 3 mm UP (DIR LOW) from where the 2026-10-02 run's final
HOME left the plunger, ~1 mm below the switch, and the switch never opened.
Three explanations: the motor doesn't turn, it turns backwards (so the plunger
is now ~4 mm below the switch), or the plunger had moved since 10-02.

DOWN (DIR HIGH) moves are not gated by the switch, but a switch read is: it
sends 2 steps UP, and the firmware refuses that while D9 reads open, whichever
way the motor actually turns. So this sends DOWN in 0.25 mm chunks, at most
6 mm, and reads the switch after every chunk:

  - a reversed motor raises the plunger, and the switch opens after ~4 mm,
    overshooting it by at most one 0.25 mm chunk. Stop there.
  - a motor that turns the right way lowers it by at most 6 mm, which is
    harmless (drop_tip goes 46.5 mm down).
  - a motor that doesn't turn does nothing.

Plunger only; the gantry port is never opened. No HOME.
Exit status: 0 = the switch opened (reversed), 1 = it never did.
"""
import json
import sys
import time

from cubos.instruments.controllers.pawduino import PawduinoLink

PORT = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00"
UP, DOWN = 0, 1
SPMM = 796.0
SLOW, PROBE = 200, 400
CHUNK_MM, MAX_MM = 0.25, 6.0
OUT = sys.argv[1] if len(sys.argv) > 1 else "tmc2209_probe_down.json"
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


def switch_open():
    reply, t, dt = cmd(16, UP, 2, SLOW)
    is_open = reply.startswith("ERR")
    if not is_open and not reply.startswith("RAISED"):
        cmd(16, DOWN, 2, SLOW)
    return is_open, reply


link.connect()
say(f"connected; STATUS -> {cmd(14)[0]}")
is_open, reply = switch_open()
say(f"start: switch {'OPEN' if is_open else 'closed'}  -> {reply[:60]}")
code, sent = 1, 0.0
if not is_open:
    steps = int(round(CHUNK_MM * SPMM))
    while sent < MAX_MM - 1e-9:
        reply, t, dt = cmd(16, DOWN, steps, PROBE, timeout=steps / PROBE + 30)
        if not reply.startswith("OK"):
            say(f"DOWN chunk -> {reply[:90]}; stopping")
            break
        sent += CHUNK_MM
        is_open, r2 = switch_open()
        say(f"DOWN {sent:5.2f} mm sent (dt {dt:.3f} s): switch {'OPEN' if is_open else 'closed'}")
        if is_open:
            code = 0
            say(f"RESULT: the switch opened after {sent:.2f} mm of DOWN commands: the motor turns, "
                f"and DIR HIGH raises the plunger. The motor is REVERSED.")
            break
    else:
        say(f"RESULT: no switch within {MAX_MM} mm of DOWN commands: not reversed (from the "
            f"10-02 position), or the motor doesn't turn.")
say(f"EMAG_OFF -> {cmd(6)[0]}")
link.disconnect()
with open(OUT, "w") as fh:
    json.dump({"down_mm_sent": sent, "switch_opened": code == 0, "rows": rows}, fh, indent=2)
say(f"disconnected; exit {code}")
sys.exit(code)
