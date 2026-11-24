"""spin.py (11-03) plus deck-camera frames: polls 31 every second while stirring.

2026-11-05 copy for stir_module_trial (PR #269): a file named STOP in the working
directory ends the sequence early (30,0 at once). Otherwise unchanged from
cubos/results/stirrer_spin_20261104/spin_frames.py.

usage: spin_frames.py <label> <rpm> <seconds> [<rpm> <seconds> ...]
One connection for the whole sequence (opening the port resets the Uno). Each step sends
30,<rpm>,<seconds> and polls 31 until the run has ended, then 4 s more. Writes <label>.jsonl,
and a deck-camera snapshot every 2 s into frames_<label>/ while it runs.
"""
import json, sys, threading, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from cubos.instruments.controllers.pawduino import PawduinoLink

PORT = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00"
label, rest = sys.argv[1], [int(a) for a in sys.argv[2:]]
steps = list(zip(rest[0::2], rest[1::2]))
utc = lambda: datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-4] + "Z"
out = open(f"{label}.jsonl", "a")
frames = Path(f"frames_{label}"); frames.mkdir(exist_ok=True)
done = threading.Event()

def grab():
    while not done.is_set():
        try:
            data = urllib.request.urlopen("http://127.0.0.1:8743/snapshot.jpg", timeout=10).read()
            (frames / (datetime.now(timezone.utc).strftime("%H%M%S") + "Z.jpg")).write_bytes(data)
        except Exception as e:
            print(utc(), "frame error", type(e).__name__, flush=True)
        done.wait(2.0)

threading.Thread(target=grab, daemon=True).start()
link = PawduinoLink.acquire(PORT, 115200)
link.connect()
try:
    pre = link.send_command(31, timeout=5)
    print(utc(), "before:", pre, flush=True)
    for rpm, secs in steps:
        if Path("STOP").exists():
            break
        r = link.send_command(30, rpm, secs, timeout=5)
        t0 = time.monotonic()
        print(f"{utc()} 30,{rpm},{secs} -> {r}", flush=True)
        out.write(json.dumps({"utc": utc(), "t": 0.0, "cmd": f"30,{rpm},{secs}", "reply": r}) + "\n")
        while time.monotonic() - t0 < secs + 4:
            time.sleep(1.0)
            if Path("STOP").exists():
                print(utc(), "STOP file: stopping", flush=True)
                break
            s = link.send_command(31, timeout=5)
            t = time.monotonic() - t0
            print(f"{utc()} {t:5.1f} s  {s}", flush=True)
            rec = {"utc": utc(), "t": round(t, 2), "rpm_cmd": rpm, "reply": s}
            try:
                rec.update(json.loads(s.split(":", 1)[1]))
            except Exception:
                pass
            out.write(json.dumps(rec) + "\n"); out.flush()
finally:
    print(utc(), "stop:", link.send_command(30, 0, timeout=5), flush=True)
    print(utc(), "after:", link.send_command(31, timeout=5), flush=True)
    link.disconnect()
    done.set()
