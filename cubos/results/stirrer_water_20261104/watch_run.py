"""Runner side of the 11-04 water stir: run stir_video.py on the CubXL Pi over SSH, print
its output, and read PR #269 every 15 s. A comment from a person asking to stop or wait
puts a STOP file on the Pi, which ends the sequence with 30,0.

usage: watch_run.py <since-ISO-UTC> <label> <rpm> <seconds> [<rpm> <seconds> ...]
"""
import json, os, queue, re, subprocess, sys, threading, time
from datetime import datetime, timezone

since, label, steps = sys.argv[1], sys.argv[2], " ".join(sys.argv[3:])
MY_ID = 6644627356
host = f'{os.environ["CUBXL_PI_USERNAME"]}@{os.environ["CUBXL_PI_HOSTNAME"]}'
ssh = ["ssh", "-o", "ConnectTimeout=20", "-o", "BatchMode=yes", host]
p = subprocess.Popen(ssh + [f"cd ~/stir_20261104b && PYTHONPATH=$HOME/CubOS/packages/core/src "
                            f"~/CubOS/.venv/bin/python stir_video.py {label} {steps}"],
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
q = queue.Queue()
threading.Thread(target=lambda: [q.put(l) for l in p.stdout], daemon=True).start()
utc = lambda: datetime.now(timezone.utc).strftime("%H:%M:%S")
seen, last_gh, stopped = set(), 0.0, False
while True:
    try:
        print("PI ", q.get(timeout=1.0).rstrip(), flush=True)
    except queue.Empty:
        pass
    if p.poll() is not None and q.empty():
        print(utc(), "pi script exited", p.returncode, flush=True)
        break
    if time.monotonic() - last_gh > 15:
        last_gh = time.monotonic()
        r = subprocess.run(["gh", "api", f"repos/vertical-cloud-lab/byu-vcl/issues/269/comments"
                            f"?since={since}&per_page=100"], capture_output=True, text=True)
        try:
            for c in json.loads(r.stdout):
                if c["id"] == MY_ID or c["id"] in seen or c["user"]["login"].endswith("[bot]"):
                    continue
                seen.add(c["id"])
                print(utc(), f"GH comment {c['id']} by {c['user']['login']} at {c['created_at']}:"
                      f"\n{c['body'][:1500]}\n---", flush=True)
                if not stopped and re.search(r"\b(stop|wait|hold|pause|halt)\b", c["body"], re.I):
                    subprocess.run(ssh + ["touch ~/stir_20261104b/STOP"], timeout=60)
                    stopped = True
                    print(utc(), "asked to stop: STOP file written on the Pi", flush=True)
        except Exception as e:
            print(utc(), "gh poll error", (r.stderr or str(e))[:200], flush=True)
print(utc(), "done", flush=True)
