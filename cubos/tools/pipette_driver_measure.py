#!/usr/bin/env python3
"""Hold the plunger stepping for a fixed window so the driver board can be probed.

Everything reachable from software has now been ruled out. The Arduino emits STEP
(§6's raw-step probe), it emits DIR with the right polarity at the right moment
(campaign 54's LED sequence, §14), the firmware executes every commanded move with
timing that matches its distance to ~1%, the limit-switch gate is open, and VM
measures 13 V at the screw terminals. What is left is the segment between the
TMC2209's input pins and the motor windings, and that segment can only be read
with a meter on the board.

This tool makes that measurable: it drives a long, slow, *bounded* plunger move in
one direction, then reverses, printing a timestamp at each transition so a reading
taken at the bench can be attributed to a known DIR state.

The pins to probe -- all broken out on the Adafruit 6121, none needing UART:

    EN     expect ~0 V. Adafruit: "Pull this pin high to disable the output to the
           motors." ~5 V here means the driver is switched off.
    DIAG   expect ~0 V. Adafruit: "driven high if there is a problem causing the
           motor driver to not be able to work properly."
    INDEX  expect it to CHANGE while stepping. Adafruit: "driven high when the
           microstep counter is in it's zero position" -- so it pulses as the chip
           consumes STEP pulses. This is the discriminator:

               STEP in + INDEX pulsing + no torque -> chip alive; the fault is the
                                                      coil path or zero current
               STEP in + INDEX dead flat           -> the chip is not processing
                                                      STEP at all

SAFETY
    Motion is bounded by --span (default 6 mm) and always returns to where it
    started, so a plunger that suddenly *does* move cannot run away. Ask the owner
    before running this: it is deliberate plunger motion on hardware somebody may
    be holding.

    Retraction only works while the pipette limit switch reads clear (D9 LOW). The
    tool measures that first and refuses the reversing window if the switch is
    asserted, because the return leg would be silently refused and the plunger
    would ratchet outward instead of coming back.
"""

from __future__ import annotations

import argparse
import sys
import time

CMD_STATUS = 14
CMD_MOVE_RELATIVE = 16
CMD_DRIVER_STATUS = 29

STEPS_PER_MM = 1592.0

# CMD_MOVE_RELATIVE takes THREE arguments -- direction, steps, velocity -- and
# PawduinoLink.send_command(code, *args) is varargs, not a list.  Passing a list
# as one argument serialises its repr, and the firmware's comma tokenizer then
# reads atof("[0") == 0, so `direction` silently parses as 0 whatever you asked
# for.  Measured on hardware 2026-09-24; it walked 14 mm one way before it showed.
DIR_RETRACT = 0  # pos decreases; this is the direction gated by the limit switch
DIR_ADVANCE = 1  # pos increases; ungated


def _send(link, code: int, *args, timeout: float = 120.0):
    t0 = time.time()
    try:
        return time.time() - t0, link.send_command(code, *args, timeout=timeout), None
    except Exception as exc:  # noqa: BLE001 - report it, never abort the window
        return time.time() - t0, None, exc


def _stamp(msg: str) -> None:
    print(f"  {time.strftime('%H:%M:%S')}  {msg}", flush=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("port", nargs="?", default="/dev/ttyACM0")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--span", type=float, default=6.0, help="mm of travel per leg (default 6)")
    ap.add_argument(
        "--rate", type=float, default=200.0, help="steps/s; lower = more torque, longer window"
    )
    ap.add_argument("--move", action="store_true", help="actually drive the plunger")
    args = ap.parse_args(argv)

    from cubos.instruments.controllers.pawduino import PawduinoLink

    link = PawduinoLink.acquire(args.port, args.baud)
    link.connect()
    try:
        _, reply, err = _send(link, CMD_STATUS, timeout=10)
        print(f"STATUS          {reply or err}")
        _, reply, err = _send(link, CMD_DRIVER_STATUS, timeout=15)
        print(f"DRIVER_STATUS   {reply or err}")
        print(
            "  NOTE: comm=0 is uninformative unless the board runs an image built with\n"
            "        cubos/patches/tmc2209-softwareserial-read.patch AND the bridge\n"
            "        resistor sits in series with A1 only (A1 -1k- NODE, with A0 and\n"
            "        PDN_UART both directly on NODE)."
        )

        # A refused retract returns almost instantly; a real one scales with distance.
        # One 1 mm probe upward says whether the return leg would actually happen.
        steps = int(round(STEPS_PER_MM))
        dt, _, err = _send(link, CMD_MOVE_RELATIVE, DIR_RETRACT, steps, args.rate, timeout=60)
        expected = steps / args.rate
        gated = dt < expected * 0.25
        print(
            f"\nlimit switch    {'ASSERTED (D9 HIGH, loop OPEN)' if gated else 'clear (D9 LOW, loop closed)'}"
            f"   [1 mm up took {dt:.2f}s vs {expected:.2f}s commanded]"
        )
        if gated:
            print(
                "\nRefusing the reversing window: the return leg would be refused and the\n"
                "plunger would ratchet outward. Fix the switch loop first (pin 6 -> GND,\n"
                "pin 7 -> D9, contact normally CLOSED)."
            )
            return 1
        _send(link, CMD_MOVE_RELATIVE, DIR_ADVANCE, steps, args.rate, timeout=60)  # undo the probe

        if not args.move:
            print("\nRead-only pass. Re-run with --move to open the measurement window.")
            return 0

        span_steps = int(round(args.span * STEPS_PER_MM))
        window = span_steps / args.rate
        print(
            f"\nMeasurement window: {args.span:.1f} mm per leg at {args.rate:.0f} steps/s"
            f"  ->  ~{window:.0f}s in each direction.\n"
            "Probe EN, DIAG and INDEX against GND while each leg runs.\n"
        )

        _stamp(f"DOWN begins  (DIR high -> RED 'B' lit)   ~{window:.0f}s")
        dt, reply, err = _send(link, CMD_MOVE_RELATIVE, DIR_ADVANCE, span_steps, args.rate, timeout=window * 3 + 60)
        _stamp(f"DOWN ends    dt={dt:.2f}s  {reply or err}")

        _stamp(f"UP begins    (DIR low -> GREEN 'F' lit)  ~{window:.0f}s")
        dt, reply, err = _send(link, CMD_MOVE_RELATIVE, DIR_RETRACT, span_steps, args.rate, timeout=window * 3 + 60)
        _stamp(f"UP ends      dt={dt:.2f}s  {reply or err}")

        _, reply, _ = _send(link, CMD_STATUS, timeout=10)
        print(f"\nSTATUS          {reply}   (should be back where it started)")
        print(
            "\nIf INDEX changed during both legs, the TMC2209 is alive and counting --\n"
            "look at the coil path (1A/1B/2A/2B screws, crimps, the FC-10P).\n"
            "If INDEX never moved, the chip is not processing STEP: check EN, then that\n"
            "STEP really lands on the driver's STEP pin, then the chip itself."
        )
        return 0
    finally:
        link.disconnect()


if __name__ == "__main__":
    sys.exit(main())
