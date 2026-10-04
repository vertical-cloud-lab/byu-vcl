#!/usr/bin/env python3
"""Show the mount on AgileX's gripper in the lab's Onshape document, in about a dozen calls.

The first import (onshape_import.py) brought in exports/assembly.step, which holds only our
parts, so the document had the mount floating on its own plus Onshape's two default tabs,
both empty. This adds the gripper next to it:

    1. import AgileX's gripper STEP (cad/reference.py fetches it and checks its SHA-256) as a
       second Part Studio. Both STEPs share one frame, so nothing needs placing,
    2. insert both Part Studios, whole, into the empty default assembly, at the origin,
    3. name the tabs for what they hold, and try to delete the empty default Part Studio (the
       lab's API key can't delete: 403, so that one is left for the web app),
    4. save a shaded view of the assembly.

The document is private (isPublic false). Keep it that way: AgileX publishes the STEP with
no licence, which is why the repo fetches it at run time instead of committing it.

    python onshape/add_gripper.py --doc 93ef145982c24192bfd160be --ws e3d08fcb2dcad7c92e183721
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "cad"))
from reference import GRIPPER_SHA256, fetch, sha256  # noqa: E402

BASE = "https://cad.onshape.com/api/v10"
NAME_PROPERTY = "57f3fb8efa3416c06701d60d"      # Onshape's "Name" metadata property
# 3 x 4 view matrix, row-major (screen right, screen up, towards the viewer): the same view as
# renders/assembly.png (camera at (-250, -520, 420) looking at the origin, +Z up).
VIEW = "0.9013,-0.4333,0,0,0.255,0.5304,0.8085,0,-0.3503,-0.7286,0.5885,0"
TABS = {"assembly": "Mount parts (exports/assembly.step)",
        "gripper": "AgileX gripper (reference, do not share)",
        "Assembly 1": "Mount on gripper"}


class Api:
    def __init__(self):
        self.s = requests.Session()
        self.s.auth = (os.environ["ONSHAPE_ACCESS_KEY"], os.environ["ONSHAPE_SECRET_KEY"])
        self.s.headers["Accept"] = "application/json;charset=UTF-8; qs=0.09"
        self.calls = 0

    def call(self, method, path, **kw):
        self.calls += 1
        r = self.s.request(method, BASE + path, timeout=180, **kw)
        if not r.ok:
            raise RuntimeError(f"{method} {path} -> HTTP {r.status_code}: {r.text[:600]}")
        return r.json() if r.content else {}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doc", required=True)
    ap.add_argument("--ws", required=True)
    args = ap.parse_args()
    did, wid = args.doc, args.ws
    step = fetch()
    if sha256(step) != GRIPPER_SHA256:
        raise SystemExit("AgileX's gripper STEP has changed since it was checked; look before importing")
    api = Api()
    rec: dict = {"date": time.strftime("%Y-%m-%d"), "document": f"https://cad.onshape.com/documents/{did}/w/{wid}"}

    doc = api.call("GET", f"/documents/{did}")
    if doc.get("public") or doc.get("isPublic"):
        raise SystemExit("the document is public; AgileX's STEP should not go into it")
    els = {e["name"]: e for e in api.call("GET", f"/documents/d/{did}/w/{wid}/elements")}
    rec["tabs_before"] = {n: e["elementType"] for n, e in els.items()}
    mount, asm, empty = els["assembly"]["id"], els["Assembly 1"]["id"], els.get("Part Studio 1", {}).get("id")

    with step.open("rb") as fh:
        tr = api.call("POST", f"/translations/d/{did}/w/{wid}",
                      files={"file": ("AgileX_Gripper.STEP", fh, "application/octet-stream")},
                      data={"formatName": "", "flattenAssemblies": "true", "translate": "true"})
    for _ in range(12):
        time.sleep(10)
        st = api.call("GET", f"/translations/{tr['id']}")
        if st["requestState"] != "ACTIVE":
            break
    rec["import"] = {"file": step.name, "sha256": GRIPPER_SHA256, "state": st["requestState"],
                     "elements": st.get("resultElementIds")}
    if st["requestState"] != "DONE":
        raise SystemExit(json.dumps(rec, indent=2))
    gripper = st["resultElementIds"][0]

    for eid in (mount, gripper):
        api.call("POST", f"/assemblies/d/{did}/w/{wid}/e/{asm}/instances",
                 json={"documentId": did, "elementId": eid, "isWholePartStudio": True, "isAssembly": False})
    for key, eid in (("assembly", mount), ("gripper", gripper), ("Assembly 1", asm)):
        api.call("POST", f"/metadata/d/{did}/w/{wid}/e/{eid}",
                 json={"properties": [{"propertyId": NAME_PROPERTY, "value": TABS[key]}]})
    rec["deleted"] = None
    if empty:
        try:       # the lab's API key has no delete scope (HTTP 403 "Invalid API key state")
            api.call("DELETE", f"/elements/d/{did}/w/{wid}/e/{empty}")
            rec["deleted"] = "Part Studio 1 (empty default)"
        except RuntimeError as err:
            rec["deleted"] = f"not deleted: {str(err).split(' -> ')[1][:40]}; delete Part Studio 1 in the web app"
    rec["tabs_after"] = {TABS["Assembly 1"]: "ASSEMBLY: both Part Studios, whole, at the origin",
                         TABS["assembly"]: "PARTSTUDIO", TABS["gripper"]: "PARTSTUDIO"}

    r = api.call("GET", f"/assemblies/d/{did}/w/{wid}/e/{asm}/shadedviews",
                 params={"viewMatrix": VIEW, "outputWidth": 1400, "outputHeight": 900, "pixelSize": 0,
                         "edges": "show", "useAntiAliasing": "true"})
    img = (r.get("images") or [None])[0]
    if img:
        (HERE / "onshape_on_gripper.png").write_bytes(base64.b64decode(img))
        rec["shaded_view"] = "onshape_on_gripper.png"
    rec["api_calls_used"] = api.calls
    (HERE / f"run_{rec['date']}_gripper.json").write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
