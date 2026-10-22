"""Small Onshape REST client for the viewport-camera document, after #241's onshape_api.py.

Credentials come from ONSHAPE_ACCESS_KEY / ONSHAPE_SECRET_KEY in the environment, never the command line.
Every request is appended to evidence/calls.jsonl (method, path, status, time; no bodies, no keys), because the
company plan has 2,500 API calls a year (https://onshape-public.github.io/docs/auth/limits/) and only successful
calls count against it.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
API = "/api/v10"
NAME_PROPERTY = "57f3fb8efa3416c06701d60d"     # Onshape's "Name" metadata property

# The lab's shared folder and company, as used by #241 and #245.
VCL_SHARED_FOLDER = "222f47147b861ce6fc04396f"
VCL_COMPANY = "69eaf7207a4e49d261c433fb"


class Onshape:
    def __init__(self, base_url: str = "https://cad.onshape.com"):
        self.base = base_url.rstrip("/")
        self.s = requests.Session()
        self.s.auth = (os.environ["ONSHAPE_ACCESS_KEY"], os.environ["ONSHAPE_SECRET_KEY"])   # HTTP Basic
        self.s.headers["Accept"] = "application/json;charset=UTF-8; qs=0.09"
        EVIDENCE.mkdir(exist_ok=True)
        self.log = EVIDENCE / "calls.jsonl"

    def call(self, method: str, path: str, raw: bool = False, **kw):
        t = time.time()
        r = self.s.request(method, self.base + API + path, timeout=300, **kw)
        with self.log.open("a") as f:
            f.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)), "method": method,
                                "path": path, "status": r.status_code, "ok": r.ok}) + "\n")
        if not r.ok:
            raise RuntimeError(f"{method} {path} -> HTTP {r.status_code}: {r.text[:1500]}")
        if raw:
            return r
        return r.json() if r.content else {}

    def calls_ok(self) -> int:
        if not self.log.exists():
            return 0
        return sum(1 for ln in self.log.read_text().splitlines() if json.loads(ln)["ok"])
