"""Read-only: full $$, $#, $I, $N, and ? from GRBL (opening the port resets it)."""
import json, time, serial
s = serial.Serial("/dev/ttyUSB0", 115200, timeout=0.2)
time.sleep(2.5); banner = s.read(4096).decode(errors="replace")
def q(cmd, until=b"ok", wait=3.0):
    s.reset_input_buffer(); s.write(cmd); buf = b""; t = time.time()
    while time.time() - t < wait:
        buf += s.read(4096)
        if until in buf: break
    return buf.decode(errors="replace")
out = {"t_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "banner": banner,
       "settings_raw": q(b"$$\n"), "offsets_raw": q(b"$#\n"), "build_raw": q(b"$I\n"),
       "startup_raw": q(b"$N\n"), "status": q(b"?", until=b">", wait=1.5)}
s.close()
json.dump(out, open("/tmp/run_20260930b/grbl_full_before_restore.json", "w"), indent=2)
for k in ("banner", "build_raw", "startup_raw", "status", "offsets_raw", "settings_raw"):
    print(f"--- {k}\n{out[k].strip()}")
