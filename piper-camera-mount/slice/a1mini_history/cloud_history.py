#!/usr/bin/env python3
"""Print history of the lab's Bambu printers, from Bambu's cloud. Read-only.

Bambu asks for an e-mailed code on every login from a new machine, so a person has to pass it on.
`start` asks Bambu to e-mail one; `code` then checks a PR thread every 2 s for a 6-digit reply from
someone with write access and logs in with it. Ask for the reply *without* `@claude`, or it starts
a second run. A code posted 51 s after it was sent worked; one posted 10 min after was rejected.

The e-mail, password, code and token are never printed. The token (good for 90 days) is kept only
in TOKEN_FILE, mode 0600, on the machine running this; delete it when done.

    python cloud_history.py start                          # needs BAMBU_USERNAME / BAMBU_PASSWORD
    python cloud_history.py code 2026-10-08T11:47:00Z --pr 245
    python cloud_history.py tasks cloud_tasks.json         # A1 mini only; --printer H2D for the H2D
    rm -f "$TOKEN_FILE"
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API = "https://api.bambulab.com"
REPO = "vertical-cloud-lab/byu-vcl"
TOKEN_FILE = os.environ.get("TOKEN_FILE", "/tmp/.bambu_token")
HEADERS = {"User-Agent": "bambu_network_agent/01.09.05.01", "Content-Type": "application/json",
           "Accept": "application/json"}


def call(method: str, path: str, body: dict | None = None, token: str | None = None):
    hdr = dict(HEADERS, **({"Authorization": f"Bearer {token}"} if token else {}))
    req = urllib.request.Request(API + path, method=method, headers=hdr,
                                 data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, {"_raw": raw[:200].decode("utf8", "replace")}


def safe(d):
    """A login response with everything but its status fields reduced to type and length."""
    if not isinstance(d, dict):
        return d
    return {k: v if k in ("loginType", "code", "error", "message", "expiresIn") else f"<{type(v).__name__} len {len(str(v))}>"
            for k, v in d.items()}


def save_token(token: str) -> None:
    fd = os.open(TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(token)


def send_code() -> None:
    st, d = call("POST", "/v1/user-service/user/sendemail/code",
                 {"email": os.environ["BAMBU_USERNAME"], "type": "codeLogin"})
    print("code e-mailed:", st, json.dumps(safe(d)), time.strftime("%H:%M:%SZ", time.gmtime()), flush=True)


def start() -> int:
    st, d = call("POST", "/v1/user-service/user/login",
                 {"account": os.environ["BAMBU_USERNAME"], "password": os.environ["BAMBU_PASSWORD"], "apiError": ""})
    print("login:", st, json.dumps(safe(d)))
    if isinstance(d, dict) and d.get("accessToken"):
        save_token(d["accessToken"])
        print("token saved; no code needed")
        return 0
    if isinstance(d, dict) and d.get("loginType") == "verifyCode":
        send_code()
        return 10
    return 20


def github(url: str, etag: str | None = None):
    token = os.environ.get("DEFAULT_WORKFLOW_TOKEN") or os.environ["GH_TOKEN"]
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}",
                                               "Accept": "application/vnd.github+json"})
    if etag:
        req.add_header("If-None-Match", etag)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.headers.get("ETag"), json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, etag, None


def code(since: str, pr: int, minutes: float, skip: set[str]) -> int:
    writers: dict[str, bool] = {}

    def can_write(user: str) -> bool:
        if user not in writers:
            st, _, body = github(f"https://api.github.com/repos/{REPO}/collaborators/{user}/permission")
            writers[user] = st == 200 and body.get("permission") in ("admin", "maintain", "write")
        return writers[user]

    etag, t0, polls = None, time.time(), 0
    while time.time() - t0 < minutes * 60:
        st, new_etag, body = github(f"https://api.github.com/repos/{REPO}/issues/{pr}/comments?since={since}&per_page=100", etag)
        polls += 1
        if st == 200 and body is not None:
            etag = new_etag
            for c in sorted(body, key=lambda c: c["created_at"], reverse=True):
                if c["created_at"] < since or str(c["id"]) in skip or c["user"]["type"] == "Bot":
                    continue
                m = re.search(r"(?<!\d)(\d{6})(?!\d)", c["body"] or "")
                if not (m and can_write(c["user"]["login"])):
                    continue
                st, d = call("POST", "/v1/user-service/user/login", {"account": os.environ["BAMBU_USERNAME"], "code": m.group(1)})
                print(time.strftime("%H:%M:%SZ", time.gmtime()), f"code from {c['user']['login']} (comment {c['id']}, "
                      f"created {c['created_at']}), poll {polls}: login {st}", json.dumps(safe(d)), flush=True)
                if isinstance(d, dict) and d.get("accessToken"):
                    save_token(d["accessToken"])
                    print("token saved")
                    return 0
                if isinstance(d, dict) and d.get("code") == 1:   # expired: ask for a fresh one, then re-run with --skip
                    send_code()
                    return 11
                return 12
        elif st not in (200, 304):
            print("poll status", st, flush=True)
        if polls % 60 == 0:
            print(time.strftime("%H:%M:%SZ", time.gmtime()), f"still waiting ({polls} polls)", flush=True)
        time.sleep(2)
    print("no code within", minutes, "min")
    return 13


KEEP = ("title", "plateIndex", "startTime", "endTime", "costTime", "weight", "length", "status", "failedType",
        "mode", "createClientType")


def tasks(out: str, printer: str) -> int:
    token = open(TOKEN_FILE).read().strip()
    serial = os.environ[f"{printer}_SERIAL"]
    hits, offset = [], 0
    while True:
        st, d = call("GET", f"/v1/user-service/my/tasks?limit=100&offset={offset}", token=token)
        if st != 200:
            print("tasks:", st, str(d)[:200])
            return 30
        page = d.get("hits") or []
        hits += page
        if not page or len(page) < 100 or len(hits) >= d.get("total", 0):
            break
        offset += len(page)
    rows = []
    for t in sorted((h for h in hits if h.get("deviceId") == serial), key=lambda h: h["startTime"]):
        r = {k: t.get(k) for k in KEEP}
        r["outcome"] = {2: "finished", 3: "failed or stopped"}.get(t["status"], f"status {t['status']}")
        r["filament"] = [{"type": m.get("filamentType"), "colour": m.get("targetColor") or m.get("sourceColor"),
                          "ams_slot": m.get("ams")} for m in (t.get("amsDetailMapping") or [])]
        rows.append(r)
    blob = json.dumps({"source": "Bambu cloud, GET /v1/user-service/my/tasks for the lab account",
                       "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "printer": printer,
                       "count": len(rows), "tasks": rows}, indent=1)
    for secret in (serial, os.environ["BAMBU_USERNAME"]):
        blob = blob.replace(secret, "<redacted>")
    with open(out, "w") as f:
        f.write(blob + "\n")
    print(f"{len(hits)} tasks on the account, {len(rows)} on {printer}; written to {out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["start", "code", "tasks"])
    ap.add_argument("arg", nargs="?", help="code: only comments after this ISO time; tasks: output JSON")
    ap.add_argument("--pr", type=int, default=245, help="issue or PR to check for the code")
    ap.add_argument("--minutes", type=float, default=25)
    ap.add_argument("--skip", default="", help="comment ids already tried, comma-separated")
    ap.add_argument("--printer", default="A1_MINI", help="env prefix of the printer's serial: A1_MINI or H2D")
    a = ap.parse_args()
    if a.command == "start":
        return start()
    if a.command == "code":
        return code(a.arg, a.pr, a.minutes, set(filter(None, a.skip.split(","))))
    return tasks(a.arg or "cloud_tasks.json", a.printer)


if __name__ == "__main__":
    sys.exit(main())
