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
`--move` tests DIRECTION explicitly, because that is what actually broke on
this machine: it steps the plunger forward in small increments and then asks
for the same positions back, comparing the round trips. Motion on this
firmware costs a very consistent 0.673 s/mm, so a command that returns in
~0.1 s did not move regardless of what it replied.

  * forward moves scale with distance, backward moves all return ~0.1 s
        -> the stepper only turns one way. Check the DIR line from the MCU to
           the driver, the driver's direction input, and the firmware's
           retract path (a `if (target > pos)` guard or an unsigned step
           count produces exactly this). MEASURED ON THE CubXL 2026-08-31.
  * every round trip ~0.1 s whatever the distance
        -> the firmware is parsing and acking but not stepping at all. Look
           at STEP/ENABLE wiring, driver enable polarity, and motor power
           (logic power comes over USB and will happily enumerate with the
           motor supply off).
  * HOME returns in ~0.5 s from a non-zero position
        -> HOME is zeroing the counter, not seeking an endstop. A real
           retraction of N mm cannot cost less than N * 0.673 s. Also check
           the endstop switch, its pull-up, and whether the logic is inverted.
  * everything scales with distance in both directions
        -> the plunger is fine and the problem is upstream, in the mm/uL
           calibration (see the max_vol note below).

BOUNDED TRAVEL: this walks a total of +3 mm and asks for it back. It does NOT
drive the plunger further and further out -- an earlier version did, and on a
firmware that never retracts it walked the plunger ~85 mm into its mechanical
stop before anyone noticed. Keep any edit to this sequence bounded.

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
        print("Bounded to +3 mm of forward travel, then asked for it back.")
        print("This firmware moves at ~0.673 s/mm; ~0.1 s means it did not.")
        print()

        print("  -- HOME --")
        home_cold = _step(link, "HOME (cold)", CMD_HOME)

        print("  -- forward: does distance scale? --")
        f1 = _step(link, "MOVE_TO 1.0 mm", CMD_MOVE_TO, 1.0, FIRMWARE_DEFAULT_SPEED)
        _step(link, "MOVE_TO 3.0 mm", CMD_MOVE_TO, 3.0, FIRMWARE_DEFAULT_SPEED)

        print("  -- HOME from a non-zero position: does it retract? --")
        home_warm = _step(link, "HOME (from 3.0)", CMD_HOME)

        print("  -- backward: the same positions, asked for in reverse --")
        _step(link, "MOVE_TO 3.0 mm", CMD_MOVE_TO, 3.0, FIRMWARE_DEFAULT_SPEED)
        b1 = _step(link, "MOVE_TO 1.0 mm (back)", CMD_MOVE_TO, 1.0, FIRMWARE_DEFAULT_SPEED)
        b0 = _step(link, "MOVE_TO 0.0 mm (back)", CMD_MOVE_TO, 0.0, FIRMWARE_DEFAULT_SPEED)

        moved = 0.4          # s -- anything below this did not turn the motor
        fwd_ok = f1 > moved
        back_ok = max(b1, b0) > moved

        print()
        if fwd_ok and not back_ok:
            print("VERDICT: forward moves take {:.2f}s but every backward move".format(f1))
            print("  returns in ~{:.2f}s. The stepper only turns ONE WAY.".format(max(b1, b0)))
            print("  Check the DIR line to the driver and the firmware's retract")
            print("  path -- not CubOS, and not the serial link.")
        elif not fwd_ok and not back_ok:
            print("VERDICT: nothing moved in either direction (all round trips")
            print("  ~0.1 s). The firmware is acking without stepping -- look at")
            print("  STEP/ENABLE wiring, driver enable polarity, and motor power.")
        else:
            print("VERDICT: the plunger moves in both directions. If it still")
            print("  does not dispense, the problem is the mm/uL calibration or")
            print("  the mechanical coupling to the plunger.")

        if home_warm < moved < home_cold or home_warm < 0.9:
            print()
            print("ALSO: HOME returned in {:.2f}s from pos 3.0 -- too fast to".format(home_warm))
            print("  retract 3 mm at 0.673 s/mm. HOME is zeroing the counter,")
            print("  not seeking the endstop, so it is not a recovery path.")
        return 0
    finally:
        link.close()


if __name__ == "__main__":
    sys.exit(main())
