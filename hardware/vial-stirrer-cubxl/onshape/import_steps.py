#!/usr/bin/env python3
"""Import the stir module's STEP files into the lab's Onshape folder vcl-shared > CubXL, one document per file.

Asked for by @benwhitney5463 on PR #269 (2026-11-05). Each STEP becomes its own document, named like the
folder's "Stir module spacer", holding the STEP file and the Part Studio Onshape translates it into. The
document is made in the folder directly, owned by the lab (Vertical Cloud Lab), and Onshape's volume for each
Part Studio is checked against the STEP's own (CadQuery). The record goes to import_steps_<date>.json.

    python onshape/import_steps.py              # all of FILES
    python onshape/import_steps.py --only base_compact

Needs ONSHAPE_ACCESS_KEY / ONSHAPE_SECRET_KEY with write access to the folder, plus cadquery for the check.
About 5 API calls a file. Nothing is printed about the keys.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import time

import requests

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = "https://cad.onshape.com/api/v6"
FOLDER = "a3519a23bb5dde572d2e8dbe"          # vcl-shared > CubXL
LAB = ("69eaf7207a4e49d261c433fb", 1)        # its owner, Vertical Cloud Lab (ownerType 1, a company)

# (key, STEP file under step/, document name, what it is)
FILES = [
    ("base_compact", "compact/base_compact.step", "Stir module base (compact)",
     "Compact (49 x 44 mm) base, as changed on 2026-11-04: no board stop, cable notch in the -X wall. Not printed yet; "
     "the bases printed on 2026-10-28 and 2026-10-30 still have the stop and a -Y notch."),
    ("vial_holder_compact", "compact/vial_holder_compact.step", "Stir module vial holder (compact)",
     "Compact (49 x 44 mm) vial holder, as printed on 2026-10-28 and 2026-10-30. The cup is one cup of the 9-vial holder."),
    ("magnet_carrier", "magnet_carrier.step", "Stir module magnet carrier",
     "Magnet carrier, glued on the fan hub; takes two 1/4 x 1/16 in magnets, opposite poles up. Same for both sizes."),
    ("deck_key", "deck_key.step", "Stir module deck key",
     "Deck key with the 0.05 mm press-fit nub (one dimple), picked on 2026-10-22. Two per base, either size."),
    ("base", "base.step", "Stir module base (56 x 56)", "The first, 56 x 56 mm stirrer's base (printed 2026-10-21)."),
    ("vial_holder", "vial_holder.step", "Stir module vial holder (56 x 56)",
     "The first, 56 x 56 mm stirrer's vial holder (printed 2026-10-21)."),
    ("vial_stirrer_assembly", "vial_stirrer_assembly.step", "Stir module assembly (56 x 56)",
     "The whole 56 x 56 mm stirrer in place, printed and bought parts, flattened into one Part Studio. For fit checks, not printing."),
]


class Api:
    def __init__(self):
        self.s = requests.Session()
        self.s.auth = (os.environ["ONSHAPE_ACCESS_KEY"], os.environ["ONSHAPE_SECRET_KEY"])
        self.s.headers["Accept"] = "application/json;charset=UTF-8; qs=0.09"
        self.calls = 0

    def call(self, method, path, **kw):
        for attempt in range(4):
            self.calls += 1
            r = self.s.request(method, BASE + path, timeout=300, **kw)
            if r.status_code not in (429, 502, 503, 504):
                break
            time.sleep(5 + 10 * attempt)
        if not r.ok:
            raise RuntimeError(f"{method} {path} -> HTTP {r.status_code}: {r.text[:400]}")
        return r.json() if r.content else {}


def step_volume(path: pathlib.Path) -> tuple[float, int]:
    import cadquery as cq
    shape = cq.importers.importStep(str(path))
    solids = shape.solids().vals()
    return sum(s.Volume() for s in solids), len(solids)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="*", help="keys from FILES")
    args = ap.parse_args()
    sha = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    api = Api()
    out = HERE / f"import_steps_{time.strftime('%Y-%m-%d')}.json"
    rec = json.loads(out.read_text()) if out.exists() else {"folder": "vcl-shared > CubXL", "folder_id": FOLDER, "docs": {}}
    for key, rel, name, what in FILES:
        if args.only and key not in args.only:
            continue
        path = ROOT / "step" / rel
        desc = (f"{what} Imported from hardware/vial-stirrer-cubxl/step/{rel} in vertical-cloud-lab/byu-vcl at commit {sha} "
                f"(PR #269, issue #169) by onshape/import_steps.py.")
        doc = api.call("POST", "/documents", json={"name": name, "description": desc, "isPublic": False,
                                                   "parentId": FOLDER, "ownerId": LAB[0], "ownerType": LAB[1]})
        did, wid = doc["id"], doc["defaultWorkspace"]["id"]
        d = {"name": name, "file": f"step/{rel}", "commit": sha, "did": did, "wid": wid,
             "owner": (doc.get("owner") or {}).get("name"), "parentId": doc.get("parentId")}
        with path.open("rb") as fh:
            tr = api.call("POST", f"/translations/d/{did}/w/{wid}",
                          files={"file": (path.name, fh, "application/octet-stream")},
                          data={"formatName": "", "flattenAssemblies": "true", "translate": "true",
                                "storeInDocument": "true", "allowFaultyParts": "false"})
        st = tr
        for wait in (15, 10, 10, 15, 20, 30, 30, 30):
            time.sleep(wait)
            st = api.call("GET", f"/translations/{tr['id']}")
            if st["requestState"] != "ACTIVE":
                break
        d["translation"] = {"state": st["requestState"], "elements": st.get("resultElementIds"),
                            "failure": st.get("failureReason")}
        if st["requestState"] == "DONE" and st.get("resultElementIds"):
            eid = st["resultElementIds"][0]
            mp = api.call("GET", f"/partstudios/d/{did}/w/{wid}/e/{eid}/massproperties", params={"massAsGroup": "false"})
            bodies = {k: v for k, v in (mp.get("bodies") or {}).items() if k != "-all-"}
            vol_os = sum(v["volume"][0] for v in bodies.values()) * 1e9
            vol_step, n_step = step_volume(path)
            d["check"] = {"parts_onshape": len(bodies), "solids_step": n_step, "volume_onshape_mm3": round(vol_os, 2),
                          "volume_step_mm3": round(vol_step, 2), "rel_diff": round((vol_os - vol_step) / vol_step, 6)}
            d["url"] = f"https://cad.onshape.com/documents/{did}/w/{wid}/e/{eid}"
        else:
            d["url"] = f"https://cad.onshape.com/documents/{did}/w/{wid}"
        rec["docs"][key] = d
        rec["api_calls_last_run"] = api.calls
        out.write_text(json.dumps(rec, indent=1) + "\n")
        print(json.dumps({key: d}), flush=True)
    print("api calls", api.calls)


if __name__ == "__main__":
    main()
