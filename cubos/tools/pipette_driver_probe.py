#!/usr/bin/env python3
"""Probe the plunger's limit switch and stepper driver with raw steps.

Why this exists
---------------
`pipette_bench_check.py` works in millimetres through `MOVE_TO`/`HOME`, which
means every reading it takes is filtered through two things that have been
broken on this machine at different times: the firmware's position counter and
its limit-switch gate. This tool goes underneath both, using the firmware's
`CMD_MOVE_RELATIVE` (code 16), which takes **raw steps** and a velocity in
steps/second and hands them straight to `moveSteps()`.

Two things make that command the right probe:

  * `moveSteps()` returns `stepsCompleted == abs(steps)`, and the Interface
    handler turns a False into `ERR:{"error":"Failed to move relative"}`. So an
    aborted move is reported **explicitly** rather than having to be inferred
    from a round-trip time.
  * the limit-switch gate in `stepMotor()` only fires when DIR is LOW (UP), so
    the DOWN direction is completely ungated. A DOWN move exercises the driver
    and the motor with the switch entirely out of the picture.

Modes
-----
    # Read the limit switch, once. Commands 2 steps up (0.0013 mm) and puts
    # them back. Effectively motionless.
    python pipette_driver_probe.py /dev/ttyACM0 --switch

    # Same read, repeated, so you can wiggle the connector and watch it flip.
    python pipette_driver_probe.py /dev/ttyACM0 --switch-monitor 60

    # Drive the plunger DOWN a bounded distance, slowly, so it is easy to see
    # and hear. Ungated, so it works even with the switch stuck asserted.
    python pipette_driver_probe.py /dev/ttyACM0 --motor-test

Why 2 steps and not 1: `stepMotor()` emits the step *before* it tests the
switch, so a 1-step up move completes its one step and returns success even
when the gate is asserted. 2 steps is the smallest move that can report the
abort.

The `--motor-test` default velocity is 400 steps/s, well below the firmware's
MOVEMENT_VELOCITY of 2500, because a stepper makes the most torque and the most
noise slowly. If it is silent at 400 steps/s it is not a speed problem.
"""

import argparse
import json
import sys
import time

import serial

CMD_MOVE_RELATIVE = 16
CMD_STATUS = 14

DIR_UP = 0
DIR_DOWN = 1

STEPS_PER_MM = 1592.0  # PANDA_Arduino include/Pipette.h
BOOT_WAIT = 5.0


def send(ser, code, *args, timeout=40.0):
    line = ",".join([str(code)] + [str(a) for a in args]) + "\n"
    ser.reset_input_buffer()
    t0 = time.time()
    ser.write(line.encode())
    while time.time() - t0 < timeout:
        reply = ser.readline().decode(errors="replace").strip()
        if reply.startswith(("OK:", "ERR:")):
            return reply, time.time() - t0
    return "(timeout)", time.time() - t0


def status(ser):
    reply, _ = send(ser, CMD_STATUS)
    try:
        return json.loads(reply.split(":", 1)[1])
    except Exception:
        return {}


def read_switch(ser, steps=2, velocity=400):
    """Return (asserted, reply, dt). Nets out to zero travel."""
    up_reply, dt = send(ser, CMD_MOVE_RELATIVE, DIR_UP, steps, velocity)
    asserted = up_reply.startswith("ERR:")
    if not asserted:
        # the up move succeeded, so put those steps back
        send(ser, CMD_MOVE_RELATIVE, DIR_DOWN, steps, velocity)
    return asserted, up_reply, dt


def open_port(port):
    ser = serial.Serial(port, 115200, timeout=2)
    print(f"Opening {port} at 115200 baud")
    print("NOTE: opening this port resets the Arduino and de-energizes the")
    print("      capper electromagnet. Do not run while a cap is held.")
    t0 = time.time()
    while time.time() - t0 < BOOT_WAIT:
        line = ser.readline().decode(errors="replace").strip()
        if line.startswith("OK:"):
            print(f"boot banner after {time.time() - t0:6.2f}s: {line!r}")
            break
    ser.reset_input_buffer()
    return ser


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("port", nargs="?", default="/dev/ttyACM0")
    ap.add_argument("--switch", action="store_true",
                    help="read the limit switch once (effectively motionless)")
    ap.add_argument("--switch-monitor", type=float, metavar="SECONDS",
                    help="read the limit switch repeatedly for SECONDS")
    ap.add_argument("--motor-test", action="store_true",
                    help="drive the plunger DOWN, slowly, ungated by the switch")
    ap.add_argument("--mm", type=float, default=1.0,
                    help="--motor-test distance in mm (default 1.0)")
    ap.add_argument("--velocity", type=int, default=400,
                    help="steps/second (default 400; firmware normal is 2500)")
    args = ap.parse_args()

    if not (args.switch or args.switch_monitor or args.motor_test):
        args.switch = True

    ser = open_port(args.port)
    try:
        st = status(ser)
        print(f"  STATUS  homed={st.get('homed')} pos={st.get('pos')} "
              f"max_vol={st.get('max_vol')}")

        if args.switch or args.switch_monitor:
            print()
            print("  -- limit switch (pipette pin 7 -> D9, return pin 6 -> GND) --")
            print("  D9 is INPUT_PULLUP and HIGH means 'at the limit', so an OPEN")
            print("  switch loop reads ASSERTED. At rest a healthy normally-closed")
            print("  contact holds it CLEAR.")
            deadline = time.time() + (args.switch_monitor or 0)
            first = True
            while first or time.time() < deadline:
                first = False
                asserted, reply, dt = read_switch(ser, velocity=args.velocity)
                state = "ASSERTED (D9 HIGH, loop OPEN)" if asserted else "CLEAR (D9 LOW, loop CLOSED)"
                print(f"  {time.strftime('%H:%M:%S')}  {state:34s} dt={dt:5.2f}s  {reply}")
                if args.switch_monitor:
                    time.sleep(0.5)

        if args.motor_test:
            steps = int(round(args.mm * STEPS_PER_MM))
            secs = steps / float(args.velocity)
            print()
            print("  -- motor test: DOWN only, which the switch gate never blocks --")
            print(f"  {steps} steps = {args.mm} mm at {args.velocity} steps/s "
                  f"-> about {secs:.1f}s of travel.")
            print("  WATCH AND LISTEN TO THE PLUNGER. The firmware bit-bangs STEP")
            print("  and counts loop iterations, so a clean reply proves only that")
            print("  the Arduino emitted the pulses -- not that the motor turned.")
            before = status(ser)
            reply, dt = send(ser, CMD_MOVE_RELATIVE, DIR_DOWN, steps, args.velocity,
                             timeout=secs + 30)
            after = status(ser)
            print(f"  DOWN {args.mm} mm   dt={dt:6.2f}s  expected~{secs:.1f}s  {reply}")
            print(f"  counter {before.get('pos')} -> {after.get('pos')}")
            print()
            if abs(dt - secs) > max(1.0, 0.4 * secs):
                print("  The round trip did not match the commanded distance -- the")
                print("  firmware did not emit the steps it was asked for.")
            else:
                print("  The Arduino emitted every step it was asked for, at the")
                print("  commanded rate. If the plunger was silent and still, the")
                print("  fault is downstream of the Arduino:")
                print("    1. no motor supply on the driver's +/- (VM) terminal, or")
                print("       coils not actually reaching the motor. Open coils are")
                print("       SILENT; a swapped coil PAIR buzzes instead.")
                print("    2. EN not held LOW at the driver pin (firmware pin A4).")
                print("    3. current set to zero -- the VREF pot in standalone mode,")
                print("       or a UART config that left the driver minimized.")
                print("  Grab the plunger with the driver idle: energized coils")
                print("  resist. No resistance at all means no coil current.")
    finally:
        ser.close()


if __name__ == "__main__":
    sys.exit(main())
