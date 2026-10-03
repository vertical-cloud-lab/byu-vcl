#!/usr/bin/env python3
"""Pull Onshape's own shaded views of the imported documents, as a check that the geometry
landed (and that the arm sits on its plate in the sandbox assembly). One API call per image.

    python shaded_views.py run_2026-09-26.json
    python shaded_views.py run_2026-09-27_add.json    # the tabs added with --add
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

from onshape_import import Api

HERE = Path(__file__).resolve().parent


def main() -> None:
    run = json.loads((HERE / sys.argv[1]).read_text())
    api = Api()
    shots = []
    sb = run["documents"].get("sandbox", {})
    if "added_to" in run:          # a --add record: the new equipment tabs and the new sandbox assembly
        for tab, t in run["documents"].get("equipment", {}).get("tabs", {}).items():
            if t.get("elements"):
                slug = "".join(c if c.isalnum() else "_" for c in tab.lower()).strip("_")
                shots.append((f"onshape_{slug}.png", run["documents"]["equipment"]["document"], "partstudios", t["elements"][0]))
        if sb.get("assembly"):
            shots.append(("onshape_sandbox_assembly_hr100a.png", sb["document"], "assemblies", sb["assembly"]))
    elif sb.get("assembly"):
        shots.append(("onshape_sandbox_assembly.png", sb["document"], "assemblies", sb["assembly"]))
    room = run["documents"].get("room", {})
    for tab in room.get("tabs", {}).values():
        if tab.get("elements"):
            shots.append(("onshape_cb154_room.png", room["document"], "partstudios", tab["elements"][0]))
    for name, url, kind, eid in shots:
        did, wid = url.split("/documents/")[1].split("/w/")
        out = api.call("GET", f"/{kind}/d/{did}/w/{wid}/e/{eid}/shadedviews",
                       params={"viewMatrix": "isometric", "outputHeight": 900, "outputWidth": 1400, "pixelSize": 0})
        (HERE / name).write_bytes(base64.b64decode(out["images"][0]))
        print(name)
    print(f"{api.calls} API calls")


if __name__ == "__main__":
    main()
