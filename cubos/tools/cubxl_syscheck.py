#!/usr/bin/env python3
"""Read-only systems check of the CubXL Pi, for after cables have been changed.

Run it on the CubXL Pi with CubOS's interpreter (it has pyserial). It needs no
checkout there, so it can be piped over SSH:

    ssh <user>@<cubxl-pi> '~/CubOS/.venv/bin/python - --frames /tmp/syscheck' \\
        < cubos/tools/cubxl_syscheck.py

Checks, in order: the Pi itself (power, temperature, disk, memory, Wi-Fi), the
USB devices the CubXL needs, the Tic T500, the ribbon cameras, the ``deckcam``
service, and the Arduino.

Nothing moves. The gantry's port is never opened, since opening it resets GRBL;
its CH340 is only checked for being on USB. The Arduino gets HELLO (0), plunger
STATUS (14) and the cap sensor (7) and nothing else. Opening its port resets the
board, as CubOS does; its ``setup()`` moves nothing. The Tic is only listed and
read with ``ticcmd --status``. ``--frames DIR`` adds a still from each camera,
skipped if someone is watching ``deckcam``.

Exit status: 0 nothing failed, 1 something failed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import subprocess
import time
import urllib.request
from pathlib import Path

ARDUINO = ("2341", "0043", "03535343335351018130")
CH340 = ("1a86", "7523")
TIC = ("1ffb", "00bd")
ARDUINO_BY_ID = ("/dev/serial/by-id/"
                 "usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00")
TICCMD = Path.home() / ".local/opt/pololu-tic-1.8.1-linux-rpi/ticcmd"
THROTTLE_BITS = {0: "under-voltage now", 1: "frequency capped now", 2: "throttled now",
                 3: "soft temperature limit now", 16: "under-voltage since boot",
                 17: "frequency capped since boot", 18: "throttled since boot",
                 19: "soft temperature limit since boot"}

results: list[tuple[str, str, str]] = []


def report(level: str, what: str, detail: str) -> None:
    results.append((level, what, detail))
    print(f"{level:<5} {what:<14} {detail}", flush=True)


def sh(*cmd: str, timeout: float = 20) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return -1, repr(e)


def num(x, spec: str = "g") -> str:
    return "?" if x is None else format(x, spec)


def read(path: str) -> str:
    try:
        return Path(path).read_text().strip()
    except OSError:
        return ""


def dt_u32(name: str) -> int | None:
    try:
        return int.from_bytes(Path(f"/proc/device-tree/chosen/power/{name}").read_bytes()[:4], "big")
    except OSError:
        return None


def holders(dev: str) -> list[str]:
    """PIDs with dev open, among the processes this user can see."""
    real, pids = os.path.realpath(dev), set()
    for fd in glob.glob("/proc/[0-9]*/fd/*"):
        try:
            if os.path.realpath(fd) == real:
                pids.add(fd.split("/")[2])
        except OSError:
            pass
    return sorted(pids - {str(os.getpid())})


# ------------------------------------------------------------------ the Pi
def check_pi() -> None:
    boot = dt.datetime.now() - dt.timedelta(seconds=float(read("/proc/uptime").split()[0]))
    report("INFO", "Pi", f"{read('/proc/device-tree/model').rstrip(chr(0))}, "
                         f"booted {boot:%Y-%m-%d %H:%M} local time")
    _, t = sh("vcgencmd", "get_throttled")
    bits = int(t.split("=")[1], 16) if "=" in t else None
    _, v = sh("vcgencmd", "pmic_read_adc", "EXT5V_V")
    m = re.search(r"=([\d.]+)V", v)
    volts = float(m.group(1)) if m else None
    psu, ocd = dt_u32("max_current"), dt_u32("usb_over_current_detected")
    flags = [s for b, s in THROTTLE_BITS.items() if bits is not None and bits >> b & 1]
    bad = bits is None or flags or (ocd or 0) != 0 or (volts or 0) < 4.9
    report("FAIL" if bad else "PASS", "power",
           f"{t or 'get_throttled failed'} ({', '.join(flags) or 'no under-voltage or throttling'}), "
           f"input {num(volts, '.2f')} V, power supply {psu} mA, "
           f"USB over-current {'detected' if ocd else 'none'}")
    _, temp = sh("vcgencmd", "measure_temp")
    c = float(re.sub(r"[^\d.]", "", temp) or 0)
    report("PASS" if 0 < c < 70 else "WARN", "temperature", f"{c:.1f} °C")
    st = os.statvfs("/")
    used = (st.f_blocks - st.f_bfree) / (st.f_blocks - st.f_bfree + st.f_bavail)   # as df
    report("PASS" if used < 0.9 else "WARN", "disk",
           f"{used:.0%} used, {st.f_bavail * st.f_frsize / 2**30:.1f} GiB free")
    mem = dict(re.findall(r"(\w+):\s+(\d+)", read("/proc/meminfo")))
    avail, total = int(mem.get("MemAvailable", 0)), int(mem.get("MemTotal", 1))
    report("PASS" if avail / total > 0.2 else "WARN", "memory",
           f"{avail / 1024:.0f} of {total / 1024:.0f} MiB available")
    _, link = sh("/usr/sbin/iw", "dev", "wlan0", "link")
    sig = re.search(r"signal:\s*(-?\d+)", link)
    report("PASS" if sig and int(sig.group(1)) > -75 else "WARN", "Wi-Fi",
           f"signal {sig.group(1)} dBm" if sig else f"not associated ({link[:60]})")


# ------------------------------------------------------------------ USB
def usb_devices() -> list[dict]:
    devs = []
    for d in glob.glob("/sys/bus/usb/devices/*"):
        if os.path.exists(f"{d}/idVendor"):
            devs.append({"path": os.path.basename(d), "vid": read(f"{d}/idVendor"),
                         "pid": read(f"{d}/idProduct"), "serial": read(f"{d}/serial"),
                         "product": read(f"{d}/product"),
                         "ttys": sorted({os.path.basename(t) for t in
                                         glob.glob(f"{d}/*/tty*") + glob.glob(f"{d}/*/tty/tty*")
                                         if re.fullmatch(r"tty(ACM|USB)\d+", os.path.basename(t))})})
    return devs


def check_usb() -> dict:
    devs = [x for x in usb_devices() if x["vid"] != "1d6b"]          # drop root hubs
    find = lambda vid, pid: [x for x in devs if (x["vid"], x["pid"]) == (vid, pid)]  # noqa: E731
    found = {}
    # want_tty: the port the cub_xl_ben_* gantry files name for each device
    for name, (vid, pid, *serial), want_tty in (("Arduino", ARDUINO, "ttyACM0"),
                                                 ("gantry CH340", CH340, "ttyUSB0")):
        hits = [x for x in find(vid, pid) if not serial or x["serial"] == serial[0]]
        if not hits:
            report("FAIL", name, f"{vid}:{pid} is not on USB")
            continue
        x = hits[0]
        tty = x["ttys"][0] if x["ttys"] else None
        found[name] = f"/dev/{tty}" if tty else None
        held = holders(f"/dev/{tty}") if tty else []
        level = "PASS" if tty == want_tty and not held else "FAIL"
        report(level, name, f"USB port {x['path']}, /dev/{tty}"
               + ("" if tty == want_tty else f" (the gantry files expect /dev/{want_tty})")
               + (f", held open by pid {held}" if held else ", not held open"))
    tic = find(*TIC)
    report("PASS" if tic else "FAIL", "Tic T500",
           f"USB port {tic[0]['path']}, serial {tic[0]['serial']}" if tic else
           f"{TIC[0]}:{TIC[1]} is not on USB, so its status can't be read and it can't be "
           f"energized or de-energized from the Pi")
    other = [f"{x['vid']}:{x['pid']} {x['product']}" for x in devs
             if (x["vid"], x["pid"]) not in {ARDUINO[:2], CH340, TIC}]
    if other:
        report("INFO", "other USB", "; ".join(other))
    _, klog = sh("journalctl", "-k", "-b", "--no-pager", "-o", "cat")
    errs = [ln for ln in klog.splitlines() if re.search(
        r"over-?current|error -(71|110|32)|unable to enumerate|device not accepting|"
        r"USB disconnect|cannot reset", ln, re.I)]
    report("PASS" if not errs else "WARN", "USB log",
           "no USB errors or disconnects since boot" if not errs else
           f"{len(errs)} line(s), last: {errs[-1][:120]}")
    return {"tic": bool(tic), **found}


def check_tic(present: bool) -> None:
    if not present:
        return
    _, s = sh(str(TICCMD), "--status")
    get = lambda pat: (re.search(pat, s) or [None, "?"])[1].strip()  # noqa: E731
    m = re.search(r"Errors currently stopping the motor:\s*(.*?)\n(?:Errors that|\Z)", s, re.S)
    stopping = " ".join(x.strip(" -") for x in m.group(1).splitlines() if x.strip()) if m else "?"
    vin, energized = get(r"VIN voltage:\s+([\d.]+)"), get(r"Energized:\s+(\w+)")
    report("WARN" if energized == "Yes" else "PASS", "Tic status",
           f"VIN {vin} V, energized {energized}, state {get(r'Operation state:\s+(.+)')}, "
           f"stopping errors: {stopping}"
           + (" (holding at full current; ticcmd --deenergize between runs)"
              if energized == "Yes" else ""))


# ------------------------------------------------------------------ cameras
def check_cameras(frames: Path | None) -> None:
    _, out = sh("rpicam-hello", "--list-cameras", timeout=30)
    cams = re.findall(r"^\s*(\d+) : (\S+) \[(\d+x\d+)[^\]]*\] \(([^)]+)\)", out, re.M)
    report("PASS" if len(cams) == 2 else "FAIL", "cameras",
           f"{len(cams)} detected: " + "; ".join(f"{i} {n} {r} ({p.split('/')[-2]})"
                                                 for i, n, r, p in cams))
    if frames is None or not cams:
        return
    _, busy = sh("pgrep", "-a", "rpicam")
    if busy:
        report("WARN", "stills", f"skipped, a camera is in use: {busy[:100]}")
        return
    frames.mkdir(parents=True, exist_ok=True)
    for i, *_ in cams:
        f = frames / f"cam{i}_csi{i}.jpg"
        rc, log = sh("rpicam-still", "--camera", i, "-n", "-t", "3000", "--width", "2304",
                     "--height", "1296", "--metadata", str(f.with_suffix(".json")), "-o", str(f),
                     timeout=30)
        try:
            md = json.loads(f.with_suffix(".json").read_text())
        except (OSError, ValueError):
            md = {}
        ok = rc == 0 and f.exists() and f.stat().st_size > 50_000
        report("PASS" if ok else "FAIL", f"still cam {i}",
               f"{f} {f.stat().st_size if f.exists() else 0} bytes, exposure "
               f"{md.get('ExposureTime', 0) / 1000:.1f} ms, gain {md.get('AnalogueGain', '?')}, "
               f"AfState {md.get('AfState', '?')}" if ok else f"rc={rc} {log[-150:]}")


def check_deckcam() -> None:
    _, active = sh("systemctl", "is-active", "deckcam")
    try:
        with urllib.request.urlopen("http://127.0.0.1:8743/status", timeout=5) as r:
            st = json.loads(r.read())
        detail = f"viewers {st.get('viewers')}, camera running {st.get('running')}"
    except (OSError, ValueError) as e:
        st, detail = None, f"no answer on 127.0.0.1:8743 ({e})"
    report("PASS" if active == "active" and st is not None else "FAIL", "deckcam",
           f"service {active}, {detail}")


# ------------------------------------------------------------------ Arduino
def check_arduino(present: bool) -> None:
    if not present or not os.path.exists(ARDUINO_BY_ID):
        return
    if holders(ARDUINO_BY_ID):
        report("FAIL", "Arduino serial", f"held open by pid {holders(ARDUINO_BY_ID)}, not opened")
        return
    import serial
    s = serial.Serial(ARDUINO_BY_ID, 115200, timeout=0.05)   # DTR resets the Uno
    t0, buf, ready = time.monotonic(), b"", None
    while time.monotonic() - t0 < 8.0 and (ready is None or time.monotonic() - ready < 0.5):
        buf += s.read(256)
        if ready is None and b"OK:Ready" in buf:
            ready = time.monotonic()
    replies = {}
    for code in (0, 14, 7):
        s.reset_input_buffer()
        s.write(f"{code}\n".encode())
        got, t1 = b"", time.monotonic()
        while time.monotonic() - t1 < 3.0 and not re.search(rb"(OK|ERR):[^\n]*\n", got):
            got += s.read(256)
        m = re.search(rb"((?:OK|ERR):[^\r\n]*)", got)
        replies[code] = m.group(1).decode(errors="replace") if m else None
    s.close()
    report("PASS" if ready else "FAIL", "Arduino boot",
           f"'OK:Ready' {ready - t0:.2f} s after the port opened" if ready else
           f"no 'OK:Ready' within 8 s (got {buf[-80:]!r})")
    hello, status, cap = replies[0], replies[14], replies[7]
    report("PASS" if hello and "Hello" in hello else "FAIL", "Arduino HELLO", str(hello))
    report("PASS" if status and '"max_vol":20.00' in status else "FAIL", "plunger STATUS",
           f"{status} (max_vol 20.00 = the VCL P20 GEN2 firmware)")
    report("PASS" if cap and '"value1":0' in cap.replace(" ", "") else "WARN", "cap sensor",
           f"{cap} (0 = nothing in the beam)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--frames", type=Path, default=None, help="save a still from each camera here")
    ap.add_argument("--no-arduino", action="store_true", help="don't open the Arduino's port")
    a = ap.parse_args()
    print(f"CubXL systems check, {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M:%S} UTC", flush=True)
    check_pi()
    usb = check_usb()
    check_tic(usb["tic"])
    check_cameras(a.frames)
    check_deckcam()
    if not a.no_arduino:
        check_arduino("Arduino" in usb)
    report("INFO", "gantry", "port not opened (opening it resets GRBL); "
                             "GRBL itself is checked by cubxl_run.py before a run")
    fails = [w for lvl, w, _ in results if lvl == "FAIL"]
    warns = [w for lvl, w, _ in results if lvl == "WARN"]
    print(f"\n{len(fails)} failed{': ' + ', '.join(fails) if fails else ''}; "
          f"{len(warns)} warning(s){': ' + ', '.join(warns) if warns else ''}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
