#!/usr/bin/env python3
"""Export the Part Studio from Onshape (STEP, one file, parts named) and save shaded views.

    python export.py step                 # ../exports/onshape_partstudio.step   (about 4 API calls)
    python export.py views                # evidence/view_*.png                 (1 API call per view)
"""
from __future__ import annotations

import base64
import json
import sys
import time
from pathlib import Path

from client import Onshape

HERE = Path(__file__).resolve().parent
EXPORTS = HERE.parent / "exports"
# 3 x 4 view matrices, row-major (screen right, screen up, towards the viewer)
VIEWS = {
    "front_left": "0.707,-0.707,0,0,0.408,0.408,0.816,0,-0.577,-0.577,0.577,0",
    "front": "1,0,0,0,0,0,1,0,0,-1,0,0",
}


def main() -> None:
    api = Onshape()
    st = json.loads((HERE / "state.json").read_text())
    did, wid, eid = st["did"], st["wid"], st["elements"]["Viewport cameras"]["id"]
    what = sys.argv[1:] or ["step"]
    if "step" in what:
        tr = api.call("POST", f"/partstudios/d/{did}/w/{wid}/e/{eid}/translations",
                      json={"formatName": "STEP", "storeInDocument": False, "flattenAssemblies": False,
                            "yAxisIsUp": False, "includeExportIds": False})
        tid = tr["id"]
        for _ in range(60):
            time.sleep(4)
            s = api.call("GET", f"/translations/{tid}")
            if s["requestState"] in ("DONE", "FAILED"):
                break
        if s["requestState"] != "DONE":
            raise SystemExit(f"translation {s['requestState']}: {s.get('failureReason')}")
        ext = s["resultExternalDataIds"][0]
        r = api.call("GET", f"/documents/d/{did}/externaldata/{ext}", raw=True)
        EXPORTS.mkdir(exist_ok=True)
        (EXPORTS / "onshape_partstudio.step").write_bytes(r.content)
        print("STEP", len(r.content), "bytes")
    for v in [w for w in what if w.startswith("view")]:
        name = v.split(":", 1)[1] if ":" in v else "front_left"
        r = api.call("GET", f"/partstudios/d/{did}/w/{wid}/e/{eid}/shadedviews",
                     params={"viewMatrix": VIEWS[name], "outputWidth": 1400, "outputHeight": 1000, "pixelSize": 0,
                             "edges": "show"})
        out = HERE / "evidence" / f"view_{name}.png"
        out.write_bytes(base64.b64decode(r["images"][0]))
        print("view", out.name)
    print("API calls so far (successful):", api.calls_ok())


if __name__ == "__main__":
    main()
