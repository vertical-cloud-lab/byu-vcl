#!/usr/bin/env python3
"""Remote OT-2 pipette offset + tip length calibration, guided by a person in a GitHub thread.

Written for byu-vcl#349 (2026-11-17). It drives the same ``/sessions`` calibration flow the
Opentrons App uses (``pipetteOffsetCalibration``, robot software 8.8.1). Step 1 (bare nozzle
on the trash) worked; the person stopped the run before the tip pick-up, so nothing was
saved. See ``opentrons-calibration.md`` ("Driving the App's calibration from the Pi").

The robot is reached through an SSH port-forward from the runner, through the Pi that holds
the robot's cable:

    ssh -f -N -o ExitOnForwardFailure=yes -L 127.0.0.1:31950:169.254.51.252:31950 "$USER@$PI"

The person at the robot replies in the issue thread with short commands (``down 1``,
``left 0.5``, ``ok``, ``stop``); only CAL_OPERATOR's replies move anything. Each reply gets a
reaction: +1 when done, confused when refused (the reason goes on the tracking comment's
``**Now:**`` line). Every move is capped (5 mm per move, and a total per step), and every
manual command first checks the thread for an unread ``stop``.

    remote_pipette_cal.py init   --since ISO          only replies after this time count
    remote_pipette_cal.py start                       create the session (HOMES the robot) + loadLabware
    remote_pipette_cal.py wait   --phase NAME         wait for ok/ready/no/stop (no motion)
    remote_pipette_cal.py jog    --phase NAME --session ID [--down MM --xy MM]
    remote_pipette_cal.py cmd    --session ID calibration.<command> [JSON]
    remote_pipette_cal.py photo  NAME                 the OT-2's own camera, 640x480
    remote_pipette_cal.py status [--session ID]

Set CAL_REPO, CAL_ISSUE, CAL_COMMENT_ID and CAL_OPERATOR for another thread. Waits are
Python-side (time.sleep), so run each as one foreground call: the shell ``sleep`` is blocked
in agent sessions, and a background process dies with the runner.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import requests

ROBOT = "http://127.0.0.1:31950"
RH = {"Opentrons-Version": "3"}
REPO = os.environ.get("CAL_REPO", "vertical-cloud-lab/byu-vcl")
ISSUE = int(os.environ.get("CAL_ISSUE", "349"))
COMMENT_ID = int(os.environ.get("CAL_COMMENT_ID", "6935654281"))   # the tracking comment
OPERATOR = os.environ.get("CAL_OPERATOR", "timothy-commins")       # only this login moves the robot
STOPPERS = {"OWNER", "MEMBER", "COLLABORATOR"}
STATE = os.environ.get("CAL_STATE", "/tmp/cal/state.json")
LOG = os.environ.get("CAL_LOG", "/tmp/cal/log.jsonl")
PHOTOS = os.environ.get("CAL_PHOTOS", "/tmp/cal/photos")

MAX_STEP = 5.0                   # mm per move
DIRS = {
    "up": (0, 0, 1), "down": (0, 0, -1),
    "left": (-1, 0, 0), "right": (1, 0, 0),
    "back": (0, 1, 0), "backward": (0, 1, 0), "backwards": (0, 1, 0), "away": (0, 1, 0),
    "forward": (0, -1, 0), "forwards": (0, -1, 0), "front": (0, -1, 0), "toward": (0, -1, 0),
    "towards": (0, -1, 0),
}
CONFIRM = {"ok", "okay", "k", "good", "yes", "y", "done", "touching", "ready", "go", "confirmed",
           "looks good", "it's good", "its good", "perfect"}
STOP = {"stop", "abort", "cancel", "halt", "estop", "e-stop"}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(**kw) -> None:
    kw["t"] = now()
    with open(LOG, "a") as f:
        f.write(json.dumps(kw) + "\n")


def load_state() -> dict:
    try:
        return json.load(open(STATE))
    except FileNotFoundError:
        return {"seen": [], "since": None}


def save_state(st: dict) -> None:
    tmp = STATE + ".tmp"
    json.dump(st, open(tmp, "w"))
    os.replace(tmp, STATE)


# ---------------------------------------------------------------- GitHub
def gh_token() -> str:
    if os.path.exists("/tmp/.ghtok"):
        return open("/tmp/.ghtok").read().strip()
    return os.environ["GITHUB_TOKEN"]


def gh(method: str, path: str, **kw):
    h = {"Authorization": f"Bearer {gh_token()}", "Accept": "application/vnd.github+json",
         "X-GitHub-Api-Version": "2022-11-28"}
    r = requests.request(method, "https://api.github.com" + path, headers=h, timeout=20, **kw)
    return r


def new_comments(since: str, seen: set) -> list:
    r = gh("GET", f"/repos/{REPO}/issues/{ISSUE}/comments", params={"since": since, "per_page": 100})
    if r.status_code != 200:
        log(ev="gh_poll_error", status=r.status_code)
        return []
    out = []
    for c in r.json():
        if c["id"] in seen or c["id"] == COMMENT_ID:
            continue
        if c["created_at"] < since:
            continue
        out.append(c)
    out.sort(key=lambda c: c["created_at"])
    return out


def react(cid: int, content: str) -> None:
    r = gh("POST", f"/repos/{REPO}/issues/comments/{cid}/reactions", json={"content": content})
    if r.status_code not in (200, 201):
        log(ev="react_error", status=r.status_code, cid=cid)


def base_status(text: str) -> None:
    st = load_state(); st["base"] = text; save_state(st)
    set_status(text)


def note_status(note: str) -> None:
    base = load_state().get("base", "")
    set_status(f"{base} <br>*{note}*")


def set_status(text: str) -> None:
    """Replace the **Now:** line in the tracking comment."""
    r = gh("GET", f"/repos/{REPO}/issues/comments/{COMMENT_ID}")
    if r.status_code != 200:
        log(ev="status_get_error", status=r.status_code)
        return
    body = r.json()["body"]
    new = re.sub(r"^\*\*Now:\*\* .*$", lambda m: f"**Now:** {text}", body, count=1, flags=re.M)
    if new != body:
        r = gh("PATCH", f"/repos/{REPO}/issues/comments/{COMMENT_ID}", json={"body": new})
        if r.status_code != 200:
            log(ev="status_patch_error", status=r.status_code)


# ---------------------------------------------------------------- parsing
def clean(body: str) -> str:
    lines = [ln for ln in body.splitlines() if not ln.lstrip().startswith(">")]
    text = " ".join(lines).lower()
    text = re.sub(r"[`*_]", "", text)
    text = text.replace("toward me", "toward").replace("towards me", "towards")
    text = text.replace("@claude", "")
    return text.strip()


NUM = r"([0-9]*\.?[0-9]+)"
DIRW = "|".join(sorted(DIRS, key=len, reverse=True))
P1 = re.compile(rf"^(?:move\s+|go\s+|jog\s+)?({DIRW})\s*(?:by\s+)?{NUM}\s*(?:mm|millimeters?)?$")
P2 = re.compile(rf"^(?:move\s+|go\s+|jog\s+)?{NUM}\s*(?:mm|millimeters?)?\s*({DIRW})$")


def parse(body: str):
    """Return ('confirm'|'stop'|'moves'|'unknown', payload)."""
    text = clean(body)
    bare = text.strip(" .!")
    if any(re.search(rf"\b{re.escape(w)}\b", bare) for w in STOP):
        return "stop", None
    if bare in {"no", "nope", "not straight", "crooked", "bad", "no it's crooked", "no, crooked"}:
        return "no", bare
    if bare in CONFIRM or bare.rstrip(".!") in CONFIRM:
        return "confirm", bare
    parts = [p.strip(" .!") for p in re.split(r",|;|\band then\b|\bthen\b|\band\b|\n", text) if p.strip(" .!")]
    moves, other = [], []
    for p in parts:
        m = P1.match(p)
        if m:
            d, v = m.group(1), float(m.group(2))
        else:
            m = P2.match(p)
            if not m:
                other.append(p)
                continue
            v, d = float(m.group(1)), m.group(2)
        ux, uy, uz = DIRS[d]
        moves.append((ux * v, uy * v, uz * v, f"{d} {v:g}"))
    if moves and not other:
        return "moves", moves
    if moves and other:
        return "unknown", bare            # mixed moves and words: too easy to misread
    first = re.split(r"[\s,.!]+", bare)[0] if bare else ""
    if first in {"ok", "okay", "ready", "good", "yes", "done", "touching", "perfect"}:
        return "confirm", bare
    return "unknown", bare


def pending_stop():
    """A not-yet-processed `stop` in the thread, without consuming other replies."""
    st = load_state()
    for c in new_comments(st["since"], set(st["seen"])):
        kind, _ = parse(c["body"] or "")
        if kind == "stop" and (c["user"]["login"] == OPERATOR or c.get("author_association") in STOPPERS):
            return c
    return None


# ---------------------------------------------------------------- robot
def rget(path: str):
    r = requests.get(ROBOT + path, headers=RH, timeout=30)
    return r.status_code, r.json()


def session_cmd(sid: str, name: str, data: dict | None = None, timeout: float = 180):
    body = {"data": {"command": name, "data": data or {}}}
    r = requests.post(f"{ROBOT}/sessions/{sid}/commands/execute", headers=RH, json=body, timeout=timeout)
    try:
        js = r.json()
    except Exception:
        js = {"raw": r.text[:500]}
    log(ev="session_cmd", name=name, data=data, status=r.status_code)
    return r.status_code, js


def session_step(sid: str) -> str:
    code, js = rget(f"/sessions/{sid}")
    return js.get("data", {}).get("details", {}).get("currentStep", f"?{code}")


def photo(name: str) -> str:
    os.makedirs(PHOTOS, exist_ok=True)
    r = requests.post(ROBOT + "/camera/picture", headers=RH, timeout=60)
    path = os.path.join(PHOTOS, name + ".jpg")
    if r.status_code == 200:
        open(path, "wb").write(r.content)
        return path
    return f"error {r.status_code}"


# ---------------------------------------------------------------- loops
def loop(phase: str, sid: str | None, timeout: float, lim: dict) -> dict:
    st = load_state()
    seen = set(st["seen"])
    since = st["since"]
    total = [0.0, 0.0, 0.0]
    t_last = time.time()
    while True:
        if time.time() - t_last > timeout:
            log(ev="timeout", phase=phase)
            return {"result": "timeout", "phase": phase, "total": total}
        try:
            cs = new_comments(since, seen)
        except Exception as e:  # network hiccup
            log(ev="poll_exception", err=str(e)[:200])
            cs = []
        for c in cs:
            seen.add(c["id"])
            st["seen"] = sorted(seen)
            save_state(st)
            login = c["user"]["login"]
            kind, payload = parse(c["body"] or "")
            log(ev="reply", phase=phase, cid=c["id"], login=login, kind=kind,
                payload=payload if kind != "moves" else [m[3] for m in payload])
            if kind == "stop" and (login == OPERATOR or c.get("author_association") in STOPPERS):
                react(c["id"], "+1")
                return {"result": "stop", "phase": phase, "by": login, "cid": c["id"], "total": total}
            if login != OPERATOR:
                continue  # only the operator moves the robot; ignore everyone else
            t_last = time.time()
            if kind == "confirm":
                react(c["id"], "+1")
                return {"result": "ok", "phase": phase, "cid": c["id"], "text": payload, "total": total}
            if kind == "no":
                react(c["id"], "eyes")
                return {"result": "no", "phase": phase, "cid": c["id"], "text": payload, "total": total}
            if kind == "unknown" or (kind == "moves" and sid is None):
                react(c["id"], "confused")
                why = ("I couldn't read" if kind == "unknown" else "No moves yet, I'm waiting for `ready`:")
                note_status(f"Your {c['created_at'][11:16]} reply: {why} "
                            f"`{(payload if isinstance(payload, str) else '')[:60]}`. Nothing moved.")
                continue
            # moves: check every limit before moving anything
            bad = None
            t2 = list(total)
            for dx, dy, dz, label in payload:
                if max(abs(dx), abs(dy), abs(dz)) > MAX_STEP:
                    bad = f"`{label}` is more than {MAX_STEP:g} mm"
                    break
                t2 = [t2[0] + dx, t2[1] + dy, t2[2] + dz]
                if abs(t2[0]) > lim["xy"] or abs(t2[1]) > lim["xy"]:
                    bad = f"`{label}` would take it more than {lim['xy']:g} mm sideways from where this step started"
                    break
                if t2[2] < -lim["down"]:
                    bad = f"`{label}` would take it more than {lim['down']:g} mm below where this step started"
                    break
                if t2[2] > lim["up"]:
                    bad = f"`{label}` would take it more than {lim['up']:g} mm above where this step started"
                    break
            if bad:
                react(c["id"], "confused")
                note_status(f"Your {c['created_at'][11:16]} reply: refused, {bad}. Nothing moved.")
                continue
            ok = True
            for dx, dy, dz, label in payload:
                code, js = session_cmd(sid, "calibration.jog", {"vector": [dx, dy, dz]})
                if code >= 300:
                    ok = False
                    log(ev="jog_error", code=code, js=str(js)[:500])
                    react(c["id"], "confused")
                    note_status(f"Your {c['created_at'][11:16]} reply: the robot refused `{label}` "
                                f"(HTTP {code}). It stopped there.")
                    return {"result": "error", "phase": phase, "cid": c["id"], "code": code,
                            "detail": str(js)[:800], "total": total}
                total = [total[0] + dx, total[1] + dy, total[2] + dz]
            if ok:
                react(c["id"], "+1")
                log(ev="jogged", phase=phase, total=total)
        time.sleep(3)


def start_session() -> int:
    """Create the pipetteOffsetCalibration session (this HOMES the robot, lights on), load labware."""
    code, js = rget("/sessions")
    if js.get("data"):
        print("a session already exists:", json.dumps(js)[:800]); return 1
    code, js = rget("/maintenance_runs/current_run")
    if code == 200:
        print("a maintenance run is active; not starting"); return 1
    if pending_stop():
        print("STOP pending in the thread; not starting"); return 3
    body = {"data": {"sessionType": "pipetteOffsetCalibration",
                     "createParams": {"mount": "left", "shouldRecalibrateTipLength": True,
                                      "hasCalibrationBlock": False, "tipRackDefinition": None}}}
    r = requests.post(ROBOT + "/sessions", headers=RH, json=body, timeout=180)
    log(ev="session_create", status=r.status_code)
    js = r.json()
    if r.status_code >= 300:
        print(r.status_code, json.dumps(js)[:1500]); return 1
    d = js["data"]
    det = d["details"]
    print("session", d["id"])
    print("step", det["currentStep"], "| shouldPerformTipLength", det["shouldPerformTipLength"])
    print("labware", [(l.get("slot"), l.get("loadName"), l.get("version")) for l in det["labware"]])
    code, js = session_cmd(d["id"], "calibration.loadLabware", {})
    print("loadLabware", code, "step:", session_step(d["id"]))
    return 0 if code < 300 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("wait"); w.add_argument("--phase", required=True); w.add_argument("--timeout", type=float, default=600)
    j = sub.add_parser("jog"); j.add_argument("--phase", required=True); j.add_argument("--session", required=True)
    j.add_argument("--timeout", type=float, default=600); j.add_argument("--xy", type=float, default=15)
    j.add_argument("--down", type=float, default=20); j.add_argument("--up", type=float, default=30)
    c = sub.add_parser("cmd"); c.add_argument("--session", required=True); c.add_argument("name"); c.add_argument("data", nargs="?")
    p = sub.add_parser("photo"); p.add_argument("name")
    s = sub.add_parser("status"); s.add_argument("--session")
    i = sub.add_parser("init"); i.add_argument("--since", required=True)
    t = sub.add_parser("parse"); t.add_argument("text")
    sub.add_parser("start")
    a = ap.parse_args()

    if a.cmd == "init":
        st = load_state(); st["since"] = a.since; save_state(st); print(st); return 0
    if a.cmd == "start":
        return start_session()
    if a.cmd == "parse":
        print(parse(a.text)); return 0
    if a.cmd == "wait":
        print(json.dumps(loop(a.phase, None, a.timeout, {"xy": 0, "down": 0, "up": 0}))); return 0
    if a.cmd == "jog":
        print(json.dumps(loop(a.phase, a.session, a.timeout, {"xy": a.xy, "down": a.down, "up": a.up}))); return 0
    if a.cmd == "cmd":
        data = json.loads(a.data) if a.data else {}
        if a.name not in ("calibration.exitSession", "calibration.saveOffset"):
            c = pending_stop()
            if c:
                print(f"STOP pending (comment {c['id']} at {c['created_at']}); not sending {a.name}")
                return 3
        code, js = session_cmd(a.session, a.name, data)
        print(code, json.dumps(js)[:1500])
        if code < 300:
            print("step:", session_step(a.session))
        return 0 if code < 300 else 1
    if a.cmd == "photo":
        print(photo(a.name)); return 0
    if a.cmd == "status":
        if a.session:
            code, js = rget(f"/sessions/{a.session}")
            d = js.get("data", {})
            print(code, json.dumps({k: d.get(k) for k in ("id", "createParams")}),
                  json.dumps({k: d.get("details", {}).get(k) for k in ("currentStep", "shouldPerformTipLength", "supportedCommands")}))
        for path in ("/calibration/pipette_offset", "/calibration/tip_length"):
            code, js = rget(path)
            rows = [r for r in js.get("data", []) if r.get("pipette") == "P3HSV212021083111"]
            print(path, code, json.dumps(rows)[:1500])
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
