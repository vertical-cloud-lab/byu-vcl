"""TMC2209 bring-up probe, run before pipette_test on 2026-10-05 (issue #169).

Ben swapped the plunger driver from the Tic T500 back to a TMC2209 board. The
Arduino firmware is unchanged (panda_vcl_p20gen2_tic796_fastmove_20261001.hex:
796 steps/mm, 1/8 step). Only the Tic's direction was ever proven on this
machine, and the firmware's HOME seeks blind with DIR LOW for up to 50,000
steps (~63 mm). On a reversed motor that drives the plunger down into the tip
ejector instead of up to the switch, and CubOS homes on connect. So this runs
first. Plunger only: the gantry port is never opened.

The limit switch is the only sensor on the plunger. stepMotor() refuses an UP
move (DIR LOW) while D9 reads the switch open, so an UP move that comes back
ERR means the plunger is at the top. Same method as
../pipette_switch_search_20260929/switch_repeat.py.

  1. connect (resets the Arduino; setup() rewrites the TMC2209 over UART)
  2. STATUS, and CMD 29 (TMC2209 driver status over UART)
  3. switch read: 2 steps UP; refused = switch open (plunger at the top).
     If open: DOWN 0.5 mm and read again. Still open = stop.
  4. UP in 0.5 mm chunks at 400 microsteps/s, at most 3 mm, stopping at the
     first refusal. A refusal proves the motor turns and that DIR LOW is up.
     No refusal within 3 mm: stop with nothing else moved, and no HOME.
  5. only if 4 tripped: DOWN 2 mm at 400/s, then UP 4 mm at 1000, 2500 and
     10000 (the 100 us floor, ~8,700/s, the rate MOVE_TO and ASPIRATE use).
     A trip after ~2 mm means the driver followed an abrupt start at that
     rate. Stops at the first rate that doesn't trip.
  6. only if 4 tripped: DOWN 2 mm, firmware HOME (cmd 10), STATUS, switch read
  7. CMD 29 again, EMAG_OFF

Exit status: 0 = direction proven and HOME ok, 1 = not proven (don't run CubOS).
"""
import json
import re
import sys
import time

from cubos.instruments.controllers.pawduino import PawduinoLink

PORT = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00"
UP, DOWN = 0, 1
SPMM = 796.0          # microsteps per mm at 1/8 step, 2 mm lead
SLOW = 200
PROBE = 400
LADDER = (1000, 2500, 10000)
FLOOR = 8700          # stepMotor()'s 100 us floor plus loop overhead, measured 2026-10-01
FLAGS = ["ot_warning", "ot_shutdown", "short_gnd_a", "short_gnd_b", "low_side_a",
         "low_side_b", "open_load_a", "open_load_b", "ot_120c", "ot_143c", "ot_150c",
         "ot_157c", "stealthchop", "standstill", "hw_disabled"]
OUT = sys.argv[1] if len(sys.argv) > 1 else "tmc2209_probe.json"
rows, result = [], {"proven": False, "home_ok": False, "ladder": {}}


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


def driver_status(label):
    reply, t, dt = cmd(29, timeout=15)
    m = re.search(r'"v":\[([^\]]*)\]', reply)
    v = [float(x) for x in m.group(1).split(",")] if m else []
    if len(v) >= 3:
        bits = int(v[1])
        names = [n for i, n in enumerate(FLAGS) if bits & (1 << i)]
        comm = {0: "0 (no UART reply)", 1: "1 (talking, setup lost)", 2: "2 (talking, set up)"}
        say(f"CMD 29 {label}: comm={comm.get(int(v[0]), v[0])} flags={bits} {names} CS={int(v[2])}")
        result[f"driver_{label}"] = {"comm": int(v[0]), "flags": bits, "flag_names": names,
                                     "cs": int(v[2])}
    else:
        say(f"CMD 29 {label} -> {reply}")
        result[f"driver_{label}"] = {"reply": reply}


def move(direction, mm, rate, label):
    steps = int(round(mm * SPMM))
    reply, t, dt = cmd(16, direction, steps, rate, timeout=steps / rate + 30)
    tripped = reply.startswith("ERR")
    raised = reply.startswith("RAISED")
    eff = min(rate, FLOOR)
    done = max(0.0, (dt - 0.10) * eff / SPMM) if tripped else mm
    what = ("RAISED" if raised else "SWITCH OPENED after ~%.2f mm" % done if tripped
            else "completed")
    say(f"{label:<26} {'UP  ' if direction == UP else 'DOWN'} {mm:4.1f} mm @ {rate:>5}/s  "
        f"dt={dt:6.3f} s (full move {steps / eff:6.3f} s)  {what}  -> {reply[:90]}")
    return tripped, raised, done


def switch_open(label):
    reply, t, dt = cmd(16, UP, 2, SLOW)
    is_open = reply.startswith("ERR")
    if not is_open and not reply.startswith("RAISED"):
        cmd(16, DOWN, 2, SLOW)
    say(f"{label:<26} switch {'OPEN (plunger at the top)' if is_open else 'closed (below the top)'}"
        f"  dt={dt:.3f} s  -> {reply[:60]}")
    return is_open


def finish(code):
    say(f"EMAG_OFF -> {cmd(6)[0]}")
    link.disconnect()
    say(f"disconnected; exit {code}")
    result["exit"] = code
    with open(OUT, "w") as fh:
        json.dump({"result": result, "rows": rows}, fh, indent=2)
    sys.exit(code)


t0 = time.time()
link.connect()
say(f"connected in {time.time() - t0:.2f} s (the port open reset the Arduino)")
say(f"STATUS -> {cmd(14)[0]}")
driver_status("before")

if switch_open("start"):
    move(DOWN, 0.5, PROBE, "off the switch")
    if switch_open("after DOWN 0.5 mm"):
        say("RESULT: the switch is still open after DOWN 0.5 mm: no motion, or DOWN is up. "
            "Stopping; no HOME.")
        finish(1)

for i in range(6):
    tripped, raised, _ = move(UP, 0.5, PROBE, f"UP search {i + 1}/6")
    if raised:
        say("RESULT: a move raised; stopping, no HOME.")
        finish(1)
    if tripped:
        result["proven"] = True
        result["search_mm"] = round(0.5 * i + _, 2)
        break
if not result["proven"]:
    say("RESULT: no switch within 3 mm UP. Either the motor doesn't turn, DIR LOW is down "
        "(the plunger went 3 mm down, which is harmless), or it sat lower than expected. "
        "Stopping with no HOME, since a reversed HOME would drive ~63 mm down.")
    finish(1)
say(f"DIRECTION PROVEN: UP opened the switch after ~{result['search_mm']} mm")

for rate in LADDER:
    _, raised, _ = move(DOWN, 2.0, PROBE, "back off")
    if raised:
        finish(1)
    tripped, raised, d = move(UP, 4.0, rate, f"ladder @ {rate}")
    result["ladder"][rate] = round(d, 2) if tripped else None
    if raised:
        finish(1)
    if not tripped:
        say(f"LADDER: no trip within 4 mm at {rate}/s: stalled or lost steps; stopping the ladder")
        break

move(DOWN, 2.0, PROBE, "back off before HOME")
reply, t, dt = cmd(10, timeout=90)
result["home"] = {"reply": reply, "dt_s": round(dt, 3)}
result["home_ok"] = reply.startswith("OK")
say(f"firmware HOME (cmd 10)  dt={dt:6.3f} s  -> {reply}")
say(f"STATUS -> {cmd(14)[0]}")
switch_open("after HOME")
driver_status("after")
finish(0 if result["home_ok"] else 1)
