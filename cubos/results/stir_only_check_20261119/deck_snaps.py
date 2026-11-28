#!/usr/bin/env python3
"""Save a deckcam still every PERIOD s, at most N of them (bounded; read-only HTTP GETs)."""
import datetime as dt, sys, time, urllib.request
from pathlib import Path
out = Path(sys.argv[1]); n = int(sys.argv[2]); period = float(sys.argv[3])
for i in range(n):
    t0 = time.monotonic()
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%H%M%S.%f")[:-4]
    try:
        data = urllib.request.urlopen("http://127.0.0.1:8743/snapshot.jpg", timeout=3).read()
        (out / f"{stamp}Z_deckcam.jpg").write_bytes(data)
    except Exception as e:
        print("snap failed", stamp, e, flush=True)
    time.sleep(max(0.0, period - (time.monotonic() - t0)))
