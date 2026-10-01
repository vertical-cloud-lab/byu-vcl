"""Poll PR #234 (or PR_NUMBER) every 2 s for a verification code from someone with write access,
then type it into Bambu Studio's verification dialog. The code itself is never printed."""
import json, os, re, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

REPO, PR = "vertical-cloud-lab/byu-vcl", int(os.environ.get("PR_NUMBER", "234"))
SINCE = sys.argv[1]                      # only comments created after this
SKIP_IDS = set(sys.argv[2].split(",")) if len(sys.argv) > 2 and sys.argv[2] else set()
MINUTES = float(os.environ.get("WAIT_MIN", "25"))
TOK = os.environ["GH_TOKEN"]

def get(url, etag=None):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOK}",
                                               "Accept": "application/vnd.github+json"})
    if etag:
        req.add_header("If-None-Match", etag)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.headers.get("ETag"), json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, etag, None

perm_cache = {}
def can_write(user):
    if user not in perm_cache:
        st, _, body = get(f"https://api.github.com/repos/{REPO}/collaborators/{user}/permission")
        perm_cache[user] = st == 200 and body.get("permission") in ("admin", "maintain", "write")
    return perm_cache[user]

etag, t0, n = None, time.time(), 0
while time.time() - t0 < MINUTES * 60:
    st, etag2, body = get(f"https://api.github.com/repos/{REPO}/issues/{PR}/comments?since={SINCE}&per_page=100", etag)
    n += 1
    if st == 200 and body is not None:
        etag = etag2
        for c in sorted(body, key=lambda c: c["created_at"], reverse=True):
            if c["created_at"] < SINCE or str(c["id"]) in SKIP_IDS or c["user"]["type"] == "Bot":
                continue
            m = re.search(r"(?<!\d)(\d{6})(?!\d)", c["body"])
            if m and can_write(c["user"]["login"]):
                code = m.group(1)
                env = dict(os.environ, DISPLAY=":99")
                ui = ["python3", str(Path(__file__).with_name("ui.py"))]
                subprocess.run(ui + ["click", "820", "564"], env=env)
                subprocess.run(["xdotool", "key", "ctrl+a", "BackSpace"], env=env)
                subprocess.run(["xdotool", "type", "--delay", "90", "--file", "-"], input=code, text=True, env=env)
                time.sleep(0.8)
                subprocess.run(ui + ["click", "1104", "666"], env=env)
                print(f"{time.strftime('%H:%M:%S', time.gmtime())}Z typed a {len(code)}-digit code from "
                      f"{c['user']['login']} (comment {c['id']}, created {c['created_at']}); polls: {n}")
                sys.exit(0)
    elif st not in (200, 304):
        print("poll status", st, flush=True)
    if n % 30 == 0:
        print(f"{time.strftime('%H:%M:%S', time.gmtime())}Z still waiting ({n} polls)", flush=True)
    time.sleep(2)
print("no code within", MINUTES, "min")
sys.exit(1)
