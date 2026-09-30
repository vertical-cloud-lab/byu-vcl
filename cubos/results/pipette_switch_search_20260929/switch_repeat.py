"""Follow-up to switch_search.py: repeatability, a start-rate ladder, and HOME.

switch_search.py found the switch after ~28.7 mm of upward travel at
200 microsteps/s, but its ERR check missed the trip: PawduinoLink raises
PawduinoLinkCommandError on an ERR reply instead of returning it. This script
treats an exception carrying "ERR:" as a trip.

The plunger starts parked AT the switch (switch asserted).

  1. DOWN 2 mm @ 200/s; the switch must close again (reads clear)
  2. UP 4 mm @ 200/s; the switch must reopen after ~2 mm
  3. start-rate ladder: for each rate, DOWN 2 mm @ 200/s, then UP 4 mm at the
     rate. A trip after ~2 mm means the motor started and followed at that rate
     with no ramp, which is how PANDA always steps. A completed 4 mm with no
     trip means it stalled ("vibrate in place", Tic guide sec. 4.3). The ladder
     stops at the first stall.
  4. DOWN 2 mm @ 200/s, then the firmware's own HOME (cmd 10): seeks up at
     ~1900 microsteps/s, backs off 796 microsteps, zeroes the counter.
"""
import time

from cubos.instruments.controllers.pawduino import PawduinoLink

PORT = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00"
UP, DOWN = 0, 1
SPMM = 796.0          # microsteps per mm at 1/8 step, 2 mm lead
SLOW = 200
LADDER = (400, 800, 1600, 2500)


def stamp(t=None):
    t = time.time() if t is None else t
    return time.strftime("%H:%M:%S", time.localtime(t)) + f".{int((t % 1) * 1000):03d}"


def say(msg):
    print(f"{stamp()}  {msg}", flush=True)


link = PawduinoLink.acquire(PORT, 115200)


def cmd(code, *args, timeout=60):
    t = time.time()
    try:
        reply = str(link.send_command(code, *args, timeout=timeout))
    except Exception as exc:
        reply = f"ERR {exc}" if "ERR:" in str(exc) else f"RAISED {exc!r}"
    return reply, t, time.time() - t


def move(direction, mm, rate, label):
    steps = int(round(mm * SPMM))
    reply, t, dt = cmd(16, direction, steps, rate, timeout=steps / rate + 30)
    tripped = reply.startswith("ERR")
    done_mm = max(0.0, (dt - 0.10) * rate / SPMM) if tripped else mm
    print(f"{stamp(t)}  {label:<28} {'UP  ' if direction == UP else 'DOWN'} {mm:4.1f} mm @ {rate:>4}/s  "
          f"dt={dt:6.3f} s (full move {steps / rate:6.3f} s)  "
          f"{'SWITCH OPENED after ~%.2f mm' % done_mm if tripped else 'completed'}  -> {reply}", flush=True)
    return tripped, done_mm


def switch_asserted(label):
    reply, t, dt = cmd(16, UP, 2, SLOW)
    asserted = reply.startswith("ERR")
    if not asserted:
        cmd(16, DOWN, 2, SLOW)
    print(f"{stamp(t)}  {label:<28} switch {'ASSERTED (open, plunger at top)' if asserted else 'clear (closed)'}"
          f"  dt={dt:.3f} s", flush=True)
    return asserted


t0 = time.time()
link.connect()
say(f"connected in {time.time() - t0:.2f} s; STATUS -> {cmd(14)[0]}")
time.sleep(1.0)
switch_asserted("start")

move(DOWN, 2.0, SLOW, "back off")
if switch_asserted("after back-off"):
    move(DOWN, 2.0, SLOW, "back off more")
    switch_asserted("after 4 mm back-off")
tripped, d = move(UP, 4.0, SLOW, "repeat @ 200")
say(f"REPEAT: {'switch reopened after ~%.2f mm' % d if tripped else 'NO trip within 4 mm'}")

for rate in LADDER:
    move(DOWN, 2.0, SLOW, "back off")
    tripped, d = move(UP, 4.0, rate, f"ladder @ {rate}")
    if not tripped:
        say(f"LADDER: stalled or lost steps at {rate}/s (no trip within 4 mm); stopping the ladder")
        break

move(DOWN, 2.0, SLOW, "back off before HOME")
switch_asserted("before HOME")
reply, t, dt = cmd(10, timeout=90)
print(f"{stamp(t)}  {'firmware HOME (cmd 10)':<28} dt={dt:6.3f} s  -> {reply}", flush=True)
say(f"STATUS -> {cmd(14)[0]}")
switch_asserted("after HOME")
say(f"EMAG_OFF -> {cmd(6)[0]}")
link.disconnect()
say("disconnected")
