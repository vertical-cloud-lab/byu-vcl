"""Restore the calibrated frame the deck file was measured in (2026-09-26b, and
what every run since used). Writes ONLY what the gantry file checks plus the G54
offset; leaves everything else as found. No motion: $X clears the boot alarm so
GRBL accepts the G10 offset write, and nothing else is sent.
Before-state: grbl_full_before_restore.json."""
import json, time, serial
WRITES = ["$10=0", "$130=391.000", "$131=236.665", "$132=124.000", "$20=1"]
s = serial.Serial("/dev/ttyUSB0", 115200, timeout=0.2)
time.sleep(2.5); s.read(4096)
def q(cmd, until=b"ok", wait=3.0):
    s.reset_input_buffer(); s.write(cmd); buf = b""; t = time.time()
    while time.time() - t < wait:
        buf += s.read(4096)
        if until in buf or b"error" in buf: break
    return buf.decode(errors="replace").strip()
log = []
for w in WRITES:
    r = q((w + "\n").encode()); log.append((w, r)); print(f"{w:<16} -> {r}")
r = q(b"$X\n"); log.append(("$X", r)); print(f"{'$X':<16} -> {r.replace(chr(13),' ').replace(chr(10),' | ')}")
g = "G10 L2 P1 X-391.000 Y-236.665 Z-124.000"
r = q((g + "\n").encode()); log.append((g, r)); print(f"{g} -> {r}")
dd = q(b"$$\n"); off = q(b"$#\n"); st = q(b"?", until=b">", wait=1.5)
s.close()
json.dump({"t_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "writes": log,
           "settings_raw": dd, "offsets_raw": off, "status": st},
          open("/tmp/run_20260930b/grbl_after_restore.json", "w"), indent=2)
print("status after:", st)
print("G54 after   :", [l for l in off.splitlines() if l.startswith("[G54")])
want = {"$3":"1","$10":"0","$20":"1","$21":"1","$22":"1","$23":"0","$27":"3.000","$100":"400.000",
        "$101":"400.000","$102":"400.000","$122":"300.000","$130":"391.000","$131":"236.665","$132":"124.000"}
got = dict(l.split("=", 1) for l in dd.splitlines() if l.startswith("$") and "=" in l)
bad = {k: (got.get(k), v) for k, v in want.items() if got.get(k) != v}
print("readback:", "as intended" if not bad else f"DIFFERS {bad}")
