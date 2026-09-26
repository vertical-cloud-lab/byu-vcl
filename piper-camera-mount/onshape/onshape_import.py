#!/usr/bin/env python3
"""Put the PiPER camera mount into Onshape over the REST API, in few calls.

    1. create a document (it lands in the API key owner's account),
    2. import exports/assembly.step (bracket, carrier, Pi 5 spacers, cameras and Pi 5
       envelopes; flattened into one Part Studio),
    3. copy the workspace into a lab folder in vcl-shared with the documented
       copyWorkspace call, which makes the copy lab-owned. (Moving a document between
       folders is not available to API keys: the web app's endpoint returns 403.)

Credentials come from the environment: ONSHAPE_ACCESS_KEY, ONSHAPE_SECRET_KEY.
A run costs about 8-10 of the plan's 2,500 yearly calls; the record goes to last_run.json.

    python onshape_import.py --folder-of DOC_ID --folder-name "6DOF Robot Arm"
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
EXPORTS = HERE.parent / "exports"
BASE = "https://cad.onshape.com/api/v10"


class Api:
    def __init__(self):
        self.s = requests.Session()
        self.s.auth = (os.environ["ONSHAPE_ACCESS_KEY"], os.environ["ONSHAPE_SECRET_KEY"])
        self.s.headers["Accept"] = "application/json;charset=UTF-8; qs=0.09"
        self.calls = 0

    def call(self, method, path, **kw):
        self.calls += 1
        r = self.s.request(method, BASE + path, timeout=120, **kw)
        if not r.ok:
            raise RuntimeError(f"{method} {path} -> HTTP {r.status_code}: {r.text[:600]}")
        return r.json() if r.content else {}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder-of", required=True, help="a document already in vcl-shared (to find the folder tree)")
    ap.add_argument("--folder-name", default="6DOF Robot Arm", help="sibling folder in vcl-shared to copy into")
    ap.add_argument("--step", default="assembly", help="file in ../exports, without .step")
    args = ap.parse_args()
    sha = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True).stdout.strip()
    name = f"PiPER wrist camera mount ({sha})"
    api = Api()
    rec: dict = {"date": time.strftime("%Y-%m-%d"), "name": name}

    # Find the target folder: the reference document's folder, its parent (vcl-shared), then the sibling.
    ref = api.call("GET", f"/documents/{args.folder_of}")
    ref_folder = ref["parentId"]
    folder = api.call("GET", f"/folders/{ref_folder}")
    shared = folder["parentId"]
    listing = api.call("GET", f"/globaltreenodes/folder/{shared}")
    items = listing.get("items", [])
    target = next((i for i in items if i.get("name") == args.folder_name and i.get("jsonType") == "folder"), None)
    if target is None:
        raise SystemExit(f"no folder {args.folder_name!r} in vcl-shared; found {[i.get('name') for i in items]}")
    rec["folder"] = {"vcl-shared": shared, args.folder_name: target["id"]}

    doc = api.call("POST", "/documents", json={"name": name, "isPublic": False})
    did, wid = doc["id"], doc["defaultWorkspace"]["id"]
    rec["source_document"] = f"https://cad.onshape.com/documents/{did}/w/{wid}"
    path = EXPORTS / f"{args.step}.step"
    with path.open("rb") as fh:
        tr = api.call("POST", f"/translations/d/{did}/w/{wid}", files={"file": (path.name, fh, "application/octet-stream")},
                      data={"formatName": "", "flattenAssemblies": "true", "translate": "true"})
    for _ in range(12):
        time.sleep(10)
        st = api.call("GET", f"/translations/{tr['id']}")
        if st["requestState"] != "ACTIVE":
            break
    rec["import"] = {"file": path.name, "state": st["requestState"], "elements": st.get("resultElementIds")}
    if st["requestState"] != "DONE":
        raise SystemExit(json.dumps(rec, indent=2))

    copy = api.call("POST", f"/documents/{did}/workspaces/{wid}/copy",
                    json={"newName": name, "isPublic": False, "parentId": target["id"]})
    cdid = copy.get("newDocumentId") or copy.get("id")
    cwid = copy.get("newWorkspaceId") or (copy.get("defaultWorkspace") or {}).get("id")
    rec["lab_copy"] = f"https://cad.onshape.com/documents/{cdid}/w/{cwid}"
    rec["api_calls_used"] = api.calls
    (HERE / "last_run.json").write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
