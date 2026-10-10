"""Host-side driver: read the color sensor over the Pico W's USB serial REPL.

Run this on whatever machine the Pico W is plugged into (a laptop, or the
RPi-5 ``rpi-5-stream-cam-2wp0`` so the read can be triggered over the tailnet).
It needs no WiFi and no MQTT broker -- just the USB cable.

    pip install pyserial
    python collect_over_serial.py --n 10 --period 1.0 --out reading.json

What it does:

1. finds the Pico's serial port (VID 0x2E8A, or pass ``--port``),
2. enters the MicroPython **raw REPL**,
3. uploads ``pico_read_intensity_flicker.py`` into RAM and executes it,
4. parses the ``#WCS#``-prefixed JSON lines it prints,
5. writes JSON (and optionally CSV) and prints a human-readable summary.

Nothing is written to the Pico's filesystem, so this cannot disturb the demo
firmware already on the board -- but note that ``main.py`` will be running on
boot, so the script sends Ctrl-C first to interrupt it. Power-cycling the Pico
restores normal MQTT operation.
"""

import argparse
import csv
import json
import os
import sys
import time

try:
    import serial
    from serial.tools import list_ports
except ImportError:  # pragma: no cover - dependency hint
    sys.exit("pyserial is required:  pip install pyserial")

HERE = os.path.dirname(os.path.abspath(__file__))
PICO_SCRIPT = os.path.join(HERE, "pico_read_intensity_flicker.py")

RP2040_VID = 0x2E8A  # Raspberry Pi (Pico / Pico W) USB vendor ID
PREFIX = "#WCS#"


def find_port():
    """Return the first serial port that looks like a Pico W."""
    candidates = [p for p in list_ports.comports() if p.vid == RP2040_VID]
    if not candidates:
        # Fall back to any CDC-ACM device; on a Pi this is usually right.
        candidates = [p for p in list_ports.comports() if "ACM" in p.device]
    if not candidates:
        ports = ", ".join(p.device for p in list_ports.comports()) or "none"
        raise SystemExit(
            "No Pico W serial port found (ports seen: %s). "
            "Pass --port explicitly." % ports
        )
    return candidates[0].device


class RawRepl:
    """Minimal MicroPython raw-REPL client (paste-free, no mpremote needed)."""

    def __init__(self, port, baud=115200, timeout=5.0):
        self.ser = serial.Serial(port, baud, timeout=timeout)
        # Residual bytes read past a token; a single read() often returns the
        # whole "OK<stdout>\x04<stderr>\x04>" frame at once, so anything after
        # the token has to be carried over to the next _read_until call.
        self._buf = b""
        time.sleep(0.2)

    def close(self):
        try:
            self.ser.write(b"\x02")  # Ctrl-B: back to the friendly REPL
            time.sleep(0.1)
        finally:
            self.ser.close()

    def _read_until(self, token, timeout=10.0):
        """Read up to and including ``token``; return everything before it."""
        deadline = time.time() + timeout
        while True:
            index = self._buf.find(token)
            if index != -1:
                head, self._buf = self._buf[:index], self._buf[index + len(token):]
                return head
            if time.time() >= deadline:
                break
            chunk = self.ser.read(1024)
            if chunk:
                self._buf += chunk
            else:
                time.sleep(0.01)
        raise TimeoutError(
            "timed out waiting for %r; got: %r" % (token, self._buf[-400:])
        )

    def enter(self):
        self.ser.write(b"\r\x03\x03")  # Ctrl-C twice: stop main.py
        time.sleep(0.3)
        self.ser.reset_input_buffer()
        self._buf = b""
        self.ser.write(b"\r\x01")  # Ctrl-A: raw REPL
        self._read_until(b"raw REPL; CTRL-B to exit\r\n>")

    def exec_(self, code, timeout=120.0):
        """Execute ``code`` on the board; return (stdout, stderr) as str."""
        self.ser.write(code.encode())
        self.ser.write(b"\x04")  # Ctrl-D: run it
        # The board answers "OK<stdout>\x04<stderr>\x04>". Wait for the "OK"
        # through the same buffer rather than a fixed-size read, so a stray
        # byte before it does not desynchronise the framing.
        self._read_until(b"OK", timeout=timeout)
        out = self._read_until(b"\x04", timeout=timeout)
        err = self._read_until(b"\x04", timeout=timeout)
        return out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


def collect(port, n, period, led_ma, timeout):
    with open(PICO_SCRIPT) as fh:
        pico_source = fh.read()

    repl = RawRepl(port)
    try:
        repl.enter()
        # Define the module in RAM, then call it. Split into two execs so a
        # syntax error in the module is reported separately from a run error.
        repl.exec_(pico_source.replace('if __name__ == "__main__":\n    run(n=1)\n', ""))
        out, err = repl.exec_(
            "run(n=%d, period_s=%r, led_ma=%d)\n" % (n, period, led_ma),
            timeout=timeout,
        )
    finally:
        repl.close()

    if err.strip():
        print("--- board stderr ---\n%s" % err.strip(), file=sys.stderr)

    readings = []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith(PREFIX):
            readings.append(json.loads(line[len(PREFIX):].strip()))
    if not readings:
        raise SystemExit(
            "No readings parsed. Raw board output was:\n%s" % out
        )
    return readings


def summarise(readings):
    channels = [
        "ch410", "ch440", "ch470", "ch510",
        "ch550", "ch583", "ch620", "ch670",
    ]
    print("\n%-6s %-8s %-8s %-9s %s" % ("idx", "clear", "nir", "flicker", "spectral counts"))
    for r in readings:
        spectral = " ".join("%5d" % r[c] for c in channels)
        flag = "  SATURATED" if r.get("saturated") else ""
        print(
            "%-6s %-8d %-8d %-9s %s%s"
            % (
                r.get("index", "-"),
                r["clear"],
                r["nir"],
                "%d Hz" % r["flicker_hz"] if r["flicker_hz"] else "none",
                spectral,
                flag,
            )
        )
    print("\nchannel order: %s (nm)" % ", ".join(c[2:] for c in channels))


def write_csv(readings, path):
    channels = [
        "ch410", "ch440", "ch470", "ch510",
        "ch550", "ch583", "ch620", "ch670",
    ]
    cols = ["index"] + channels + ["clear", "nir", "flicker_hz", "saturated"]
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        for r in readings:
            writer.writerow(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", help="serial port (default: autodetect the Pico W)")
    ap.add_argument("--n", type=int, default=1, help="number of readings")
    ap.add_argument("--period", type=float, default=1.0, help="seconds between readings")
    ap.add_argument(
        "--led-ma",
        type=int,
        default=0,
        help="onboard LED current in mA (0 = off/ambient; 4..20 even values)",
    )
    ap.add_argument("--out", help="write readings as JSON to this path")
    ap.add_argument("--csv", help="also write a flat CSV to this path")
    ap.add_argument("--timeout", type=float, default=300.0, help="board exec timeout (s)")
    args = ap.parse_args()

    port = args.port or find_port()
    print("Using serial port: %s" % port)

    readings = collect(port, args.n, args.period, args.led_ma, args.timeout)
    summarise(readings)

    if args.out:
        with open(args.out, "w") as fh:
            json.dump(readings, fh, indent=2)
        print("\nwrote %s" % args.out)
    if args.csv:
        write_csv(readings, args.csv)
        print("wrote %s" % args.csv)


if __name__ == "__main__":
    main()
