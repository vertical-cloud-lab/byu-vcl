import json, os, queue, subprocess, sys, threading, time
from datetime import datetime, timezone
limit_s = float(sys.argv[1]); label = sys.argv[2]; since = sys.argv[3]
MY_ID = 6617105283
host = f'{os.environ["CUBXL_PI_USERNAME"]}@{os.environ["CUBXL_PI_HOSTNAME"]}'
cmd = ["ssh", "-o", "ConnectTimeout=20", "-o", "BatchMode=yes", host,
       f"cd ~/stir_20261103 && PYTHONPATH=$HOME/CubOS/packages/core/src ~/CubOS/.venv/bin/python hall_watch.py {limit_s} {label}"]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
q = queue.Queue()
threading.Thread(target=lambda: [q.put(l) for l in p.stdout], daemon=True).start()
seen = set(); t0 = time.monotonic(); last_gh = 0; last_edge = None; ben_said = False
def utc(): return datetime.now(timezone.utc).strftime("%H:%M:%S")
while time.monotonic() - t0 < limit_s + 10:
    try:
        line = q.get(timeout=1.0)
        print("PI ", line.rstrip(), flush=True)
        if '"rpm":' in line and '"rpm":0.0' not in line:
            last_edge = time.monotonic()
    except queue.Empty:
        pass
    if p.poll() is not None and q.empty():
        print(utc(), "pi watcher exited", p.returncode); break
    if time.monotonic() - last_gh > 15:
        last_gh = time.monotonic()
        r = subprocess.run(["gh", "api", f"repos/vertical-cloud-lab/byu-vcl/issues/269/comments?since={since}&per_page=50"],
                           capture_output=True, text=True)
        try:
            for c in json.loads(r.stdout):
                if c["id"] == MY_ID or c["id"] in seen or c["user"]["login"].endswith("[bot]"):
                    continue
                seen.add(c["id"])
                print(utc(), f"GH comment {c['id']} by {c['user']['login']} at {c['created_at']}:\n{c['body'][:1500]}\n---", flush=True)
                if c["user"]["login"] == "benwhitney5463":
                    ben_said = True
        except Exception as e:
            print(utc(), "gh poll error", (r.stderr or str(e))[:200], flush=True)
    if ben_said and (last_edge is None or time.monotonic() - last_edge > 20):
        print(utc(), "Ben replied; stopping the watch"); break
    if last_edge is not None and time.monotonic() - last_edge > 25 and not ben_said:
        print(utc(), "edges seen, then 25 s quiet; stopping the watch"); break
p.terminate()
try: p.wait(10)
except Exception: p.kill()
for l in list(q.queue): print("PI ", l.rstrip())
print(utc(), "done")
