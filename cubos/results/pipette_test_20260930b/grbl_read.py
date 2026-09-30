"""Read-only GRBL snapshot: $$, $#, ?. Opening the port resets the board (as
CubOS's own connect does); nothing is written except the three queries."""
import json, re, sys, time, serial
EXPECT = {"$3": 1, "$10": 0, "$20": 1, "$22": 1, "$23": 0, "$27": 3.0,
          "$100": 400.0, "$101": 400.0, "$102": 400.0,
          "$130": 391.0, "$131": 236.665, "$132": 124.0}
s = serial.Serial("/dev/ttyUSB0", 115200, timeout=0.2)
time.sleep(2.5); banner = s.read(4096).decode(errors="replace").strip()
def q(cmd, until=b"ok", wait=3.0):
    s.reset_input_buffer(); s.write(cmd); buf = b""; t = time.time()
    while time.time() - t < wait:
        buf += s.read(4096)
        if until in buf: break
    return buf.decode(errors="replace").strip()
dd = q(b"$$\n"); off = q(b"$#\n"); st = q(b"?", until=b">", wait=1.5)
s.close()
vals = dict(re.findall(r"^(\$\d+)=([-\d.]+)", dd, re.M))
print("banner:", banner.replace("\r", " ").replace("\n", " | "))
print("status:", st)
print("offsets:", " ".join(l for l in off.splitlines() if l.startswith("[G54") or l.startswith("[G28")))
bad = []
for k, v in EXPECT.items():
    got = vals.get(k); ok = got is not None and abs(float(got) - float(v)) <= 0.001
    print(f"  {k:>5} = {got:>10}   gantry file {v}   {'ok' if ok else 'MISMATCH'}")
    if not ok: bad.append(k)
print("RESULT:", "all match" if not bad else f"MISMATCH {bad}")
json.dump({"banner": banner, "settings": vals, "offsets": off, "status": st},
          open("/tmp/run_20260930b/grbl_settings_20260930b.json", "w"), indent=2)
