#!/usr/bin/env python3
"""Bench-test the Pawduino plunger in isolation, away from the protocol engine.

Why this exists
---------------
On 2026-08-31 the CubXL ran `pipette_test.yaml` end to end (18/18 steps) with
the pipette configured live (`offline: false`, `/dev/ttyACM0`) -- and the
plunger did not visibly actuate. The protocol engine cannot tell you why:
every plunger call is fire-and-forget except `aspirate`, and the driver marks
itself homed without ever re-reading the firmware's own `homed` flag
(`OpentronsPipette.home()` sets `self._is_homed = True` unconditionally).

This script talks to the Arduino directly so the plunger is the only variable:
no gantry, no deck, no protocol. It separates the three things that look
identical from inside a protocol run:

  1. the link is dead              -> no reply at all
  2. the firmware acks but the      -> replies arrive, `pos` never changes,
     stepper never turns              round-trip time is independent of the
                                      commanded distance
  3. the plunger really moves       -> `pos` tracks, and round-trip time
                                      scales with distance

Usage
-----
    # READ ONLY -- queries only, never commands motion. Safe any time.
    python -m cubos.tools.pipette_bench_check /dev/ttyACM0

    # Commands real plunger motion. The pipette WILL move. Only run this
    # with the pipette in hand or on the bench, nothing loaded, tip off.
    python -m cubos.tools.pipette_bench_check /dev/ttyACM0 --move

Reading the output
------------------
`--move` walks HOME -> MOVE_TO 5 -> MOVE_TO 10 -> MOVE_TO 0 -> ASPIRATE 1.0,
printing the firmware's reported position and the wall-clock round trip for
each. Compare the `dt` column against the commanded distance:

  * dt roughly constant (~0.1 s) whatever the distance
        -> the firmware is parsing and acking but not stepping. Look at the
           STEP/DIR/ENABLE wiring, the driver's enable polarity, and motor
           power (logic power comes over USB and will happily enumerate with
           the motor supply off).
  * HOME returns in a couple of seconds
        -> a real homing pass is ~35 s of travel. A fast HOME means the
           endstop is reading already-triggered: check the switch, its
           pull-up, and whether the logic is inverted.
  * dt scales with distance and `pos` tracks
        -> the plunger is fine and the problem is upstream, in the
           mm/uL calibration (see the max_vol note below).

The `max_vol` field in the STATUS reply is the firmware's own idea of the
pipette. If it disagrees with `pipette_model` in the gantry YAML, the
plunger geometry CubOS is using (prime/blowout/drop_tip positions, mm_to_ul)
belongs to a different pipette and every commanded volume is wrong.
"""

import argparse
import json
import sys
import time

import serial

CMD_HOME = 10
CMD_MOVE_TO = 11
CMD_ASPIRATE = 12
CMD_DISPENSE = 13
CMD_STATUS = 14

# The board resets when the port opens and prints "OK:Ready". Measured on the
# lab CubXL at 3.76-3.80 s, consistently -- well past the 2.0 s that
# _ARDUINO_SETTLE_TIME allows, which is the bug the pawduino-connect-boot-banner
# patch fixes for the capper.
BANNER_TIMEOUT = 8.0
FIRMWARE_DEFAULT_SPEED = 0.0


def _open(port: str, baud: int) -> serial.Serial:
    link = serial.Serial(port, baud, timeout=8)
    start = time.monotonic()
    banner = ""
    while time.monotonic() - start < BANNER_TIMEOUT:
        if link.in_waiting:
            banner += link.read(link.in_waiting).decode(errors="replace")
            if "\n" in banner:
                break
        time.sleep(0.05)
    print(f"boot banner after {time.monotonic() - start:5.2f}s: {banner.strip()!r}")
    time.sleep(1.0)
    link.reset_input_buffer()
    return link


def _send(link: serial.Serial, code: int, *args: float, timeout: float = 130.0):
    """Send one command, return (reply, round_trip_seconds)."""
    link.reset_input_buffer()
    message = ",".join([str(code)] + [str(a) for a in args]) + "\n"
    start = time.monotonic()
    link.write(message.encode())
    link.flush()
    deadline = start + timeout
    while time.monotonic() < deadline:
        line = link.readline().decode(errors="replace").strip()
        if line:
            return line, time.monotonic() - start
    return "<no reply>", time.monotonic() - start


def _status(link: serial.Serial):
    reply, dt = _send(link, CMD_STATUS, timeout=10.0)
    parsed = None
    if reply.startswith("OK:"):
        try:
            parsed = json.loads(reply[3:])
        except json.JSONDecodeError:
            parsed = None
    return reply, dt, parsed


def _step(link: serial.Serial, label: str, code: int, *args: float):
    reply, dt = _send(link, code, *args)
    _sreply, _sdt, parsed = _status(link)
    pos = parsed.get("pos") if parsed else "?"
    homed = parsed.get("homed") if parsed else "?"
    print(f"  {label:<24} dt={dt:7.2f}s  reply={reply:<44} pos={pos} homed={homed}")
    return dt


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("port", nargs="?", default="/dev/ttyACM0")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--move", action="store_true",
                    help="Command real plunger motion (default: queries only).")
    args = ap.parse_args(argv)

    print(f"Opening {args.port} at {args.baud} baud")
    print("NOTE: opening this port resets the Arduino and de-energizes the")
    print("      capper electromagnet. Do not run while a cap is held.")
    link = _open(args.port, args.baud)
    try:
        reply, dt, parsed = _status(link)
        print(f"  {'STATUS (read-only)':<24} dt={dt:7.2f}s  reply={reply}")
        if parsed:
            print(f"      firmware max_vol = {parsed.get('max_vol')} uL "
                  f"-- must match pipette_model in the gantry YAML")

        if not args.move:
            print()
            print("Read-only pass complete. Re-run with --move to exercise the")
            print("plunger (it will physically move; tip off, nothing loaded).")
            return 0

        print()
        print("Commanding plunger motion. Watch the plunger, not the screen.")
        print("A real HOME is ~35 s of travel; a 2 s HOME means the endstop")
        print("is reading already-triggered.")
        _step(link, "HOME", CMD_HOME)
        d5 = _step(link, "MOVE_TO 5.0 mm", CMD_MOVE_TO, 5.0, FIRMWARE_DEFAULT_SPEED)
        d10 = _step(link, "MOVE_TO 10.0 mm", CMD_MOVE_TO, 10.0, FIRMWARE_DEFAULT_SPEED)
        d0 = _step(link, "MOVE_TO 0.0 mm", CMD_MOVE_TO, 0.0, FIRMWARE_DEFAULT_SPEED)
        _step(link, "ASPIRATE 1.0 mm", CMD_ASPIRATE, 1.0, FIRMWARE_DEFAULT_SPEED)
        _step(link, "DISPENSE 1.0 mm", CMD_DISPENSE, 1.0, FIRMWARE_DEFAULT_SPEED)

        print()
        spread = max(d5, d10, d0) - min(d5, d10, d0)
        if spread < 0.25:
            print(f"VERDICT: MOVE_TO round trips differ by only {spread:.2f}s across")
            print("  5 mm / 10 mm / 0 mm targets. The firmware is acking without")
            print("  stepping -- look at STEP/DIR/ENABLE wiring, driver enable")
            print("  polarity, and motor power, not at CubOS.")
        else:
            print(f"VERDICT: MOVE_TO round trips vary by {spread:.2f}s with distance,")
            print("  so the stepper is being driven. If the pipette still does not")
            print("  dispense, the problem is the mm/uL calibration or the")
            print("  mechanical coupling to the plunger.")
        return 0
    finally:
        link.close()


if __name__ == "__main__":
    sys.exit(main())
