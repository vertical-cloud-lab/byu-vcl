"""Closed-loop proof of plunger motion: drive UP until the limit switch opens.

Run on the CubXL Pi with ~/CubOS/.venv/bin/python. Plunger only: the gantry
port is never opened.

Why this test: the Arduino and the Tic are both open-loop. A move that returns
OK at the commanded rate proves the steps were emitted, never that the shaft
turned, and the camera cannot see inside the pipette. The limit switch is the
one sensor on the plunger. PANDA's stepMotor() aborts an UP move (DIR LOW) the
moment D9 reads HIGH (switch open = plunger at the top), and moveSteps() then
returns ERR "Failed to move relative". So an UP move that stops early with ERR
means the plunger physically travelled up to the switch.

Sequence:
  1. read the switch (2 steps up, 2 back: 2 is the smallest move that can
     report the abort, since stepMotor() steps before it tests the pin)
  2. UP in 5 mm chunks, slowly, until ERR or MAX_CHUNKS (60 mm, more than the
     P20 GEN2's whole plunger stroke)
  3. if it tripped: DOWN 2 mm, re-read the switch (must be clear again), then
     UP 4 mm, which must trip after ~2 mm. A switch that opens and closes at a
     repeatable plunger position cannot be explained by anything but motion.
  4. leave the plunger 2 mm below the switch

Units: 1/8 step on the Tic, ~796 microsteps per mm (PANDA's 1592 at 1/16).
PawduinoLink.send_command takes separate varargs, never a list (2026-09-24).
"""
import sys
import time

from cubos.instruments.controllers.pawduino import PawduinoLink

PORT = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00"
UP, DOWN = 0, 1
STEPS_PER_MM = 796.0
RATE = int(sys.argv[1]) if len(sys.argv) > 1 else 200      # microsteps/s
CHUNK_MM = 5.0
MAX_CHUNKS = int(sys.argv[2]) if len(sys.argv) > 2 else 12


def stamp(t=None):
    t = time.time() if t is None else t
    return time.strftime("%H:%M:%S", time.localtime(t)) + f".{int((t % 1) * 1000):03d}"


def say(msg):
    print(f"{stamp()}  {msg}", flush=True)


link = PawduinoLink.acquire(PORT, 115200)


def move(direction, steps, label):
    t = time.time()
    try:
        reply = link.send_command(16, direction, steps, RATE, timeout=steps / RATE + 30)
    except Exception as exc:
        reply = f"RAISED {exc!r}"
    dt = time.time() - t
    commanded = steps / RATE
    print(f"{stamp(t)}  {label:<26} {'UP  ' if direction == UP else 'DOWN'} {steps:>5} steps "
          f"({steps / STEPS_PER_MM:5.2f} mm) @ {RATE}/s  dt={dt:6.3f} s  commanded={commanded:6.3f} s  -> {reply}",
          flush=True)
    return str(reply), dt


def switch_asserted(label):
    reply, _ = move(UP, 2, label)
    if reply.startswith("OK"):
        move(DOWN, 2, label + " (put back)")
        return False
    return True


t0 = time.time()
link.connect()
say(f"connected in {time.time() - t0:.2f} s; STATUS -> {link.send_command(14)}")
time.sleep(1.0)

if switch_asserted("switch read, before"):
    say("RESULT: switch reads ASSERTED before any travel -- plunger already at the top, or the loop is open. Stopping.")
else:
    say("switch reads clear; starting the upward search")
    chunk = int(round(CHUNK_MM * STEPS_PER_MM))
    travelled_mm, tripped = 0.0, False
    for i in range(1, MAX_CHUNKS + 1):
        reply, dt = move(UP, chunk, f"search chunk {i}/{MAX_CHUNKS}")
        if reply.startswith("ERR"):
            partial = max(0.0, (dt - 0.10) * RATE / STEPS_PER_MM)   # 100 ms debounce
            travelled_mm += partial
            tripped = True
            say(f"SWITCH OPENED during chunk {i}: ~{partial:.2f} mm into it, "
                f"~{travelled_mm:.1f} mm of upward travel in total")
            break
        travelled_mm += CHUNK_MM
        time.sleep(0.5)
    if not tripped:
        say(f"RESULT: NO TRIP after {travelled_mm:.0f} mm commanded UP. Either the shaft is not "
            "turning, it is turning DOWN (then the plunger is now at its bottom stop and the tip "
            "ejector is extended), or the switch cannot be reached.")
    else:
        time.sleep(1.0)
        move(DOWN, int(2 * STEPS_PER_MM), "back off 2 mm")
        time.sleep(0.5)
        clear = not switch_asserted("switch read, backed off")
        say(f"after backing off 2 mm the switch reads {'CLEAR (it closed again)' if clear else 'STILL ASSERTED'}")
        time.sleep(0.5)
        reply, dt = move(UP, int(4 * STEPS_PER_MM), "repeat: up 4 mm")
        if reply.startswith("ERR"):
            again = max(0.0, (dt - 0.10) * RATE / STEPS_PER_MM)
            say(f"REPEAT: switch opened again after ~{again:.2f} mm (expected ~2 mm)")
        else:
            say("REPEAT: 4 mm up completed WITHOUT reopening the switch")
        time.sleep(0.5)
        move(DOWN, int(2 * STEPS_PER_MM), "park 2 mm below switch")
        say("RESULT: TRIPPED" if clear else "RESULT: TRIPPED, but the switch did not re-close on back-off")

say(f"STATUS -> {link.send_command(14)}")
say(f"EMAG_OFF -> {link.send_command(6)}")
link.disconnect()
say("disconnected")
