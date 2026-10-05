"""Buzz test, 2026-10-05: something Ben can feel or hear at the pipette.

The limit-switch probes can't tell a motor that doesn't turn from one whose plunger
sits lower than expected. A person with a finger on the pipette can. This sends
0.5 mm UP then 0.5 mm DOWN, repeated for ~30 s at 800 microsteps/s, which is 100 full
steps/s and a hum Ben felt on the Tic on 2026-09-29. Net travel is zero.

UP goes first, and UP moves stop at the switch. So a motor turning the right way
can't overrun the top, and a reversed one only ever goes below where it started.
An UP refused partway (the switch opened) proves the motor turns and that DIR LOW
is up; the buzz stops there. Plunger only; the gantry port is never opened. No HOME.
"""
import json
import sys
import time

from cubos.instruments.controllers.pawduino import PawduinoLink

PORT = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00"
UP, DOWN = 0, 1
SPMM, RATE, LEG_MM, SECONDS = 796.0, 800, 0.5, 30.0
OUT = sys.argv[1] if len(sys.argv) > 1 else "tmc2209_buzz.json"
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
steps = int(round(LEG_MM * SPMM))
t_end, cycles, tripped = time.time() + SECONDS, 0, False
say(f"BUZZ START: {LEG_MM} mm UP / {LEG_MM} mm DOWN at {RATE}/s for {SECONDS:.0f} s")
while time.time() < t_end:
    reply, t, dt = cmd(16, UP, steps, RATE, timeout=steps / RATE + 30)
    if not reply.startswith("OK"):
        tripped = reply.startswith("ERR")
        say(f"UP leg {cycles + 1}: {reply[:90]} (dt {dt:.3f} s)")
        if tripped:
            say("RESULT: the switch opened during an UP leg: the motor turns, and DIR LOW is up.")
        break
    reply, t, dt = cmd(16, DOWN, steps, RATE, timeout=steps / RATE + 30)
    if not reply.startswith("OK"):
        say(f"DOWN leg {cycles + 1}: {reply[:90]}")
        break
    cycles += 1
say(f"BUZZ END: {cycles} full cycles")
say(f"EMAG_OFF -> {cmd(6)[0]}")
link.disconnect()
with open(OUT, "w") as fh:
    json.dump({"cycles": cycles, "switch_opened": tripped, "rows": rows}, fh, indent=2)
say("disconnected")
