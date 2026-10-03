#!/usr/bin/env python3
"""Put the lab models into Onshape, one document per group, in few API calls.

For each document in DOCS:

    1. create the document straight into the target folder, owned by the lab's team
       (ownerType 1 + ownerId), so nothing is left behind in the API key owner's account,
    2. import each STEP as its own tab (Onshape flattens each file into one Part Studio),
    3. wait once, then poll each import until it is done (tabs keep the STEP file names: the
       public API can't rename an element),
    4. for the sandbox, add an assembly with AgileX's arm placed on the layout.

The folder itself was made over the API too (`make_folder`): POST /folders works for API keys
when the body carries the owner (`ownerId`, `ownerType`); without them it is HTTP 400. Moving
a document between folders is still web-app only (#234).

Every successful call counts against the plan's 2,500 a year (4xx and 5xx responses don't), so
the script waits before its first poll instead of polling fast. A dry run (--dry-run) prints the plan and makes no calls.

Credentials come from the environment: ONSHAPE_ACCESS_KEY, ONSHAPE_SECRET_KEY.

    python onshape_import.py --folder FOLDER_ID            # all documents
    python onshape_import.py --folder FOLDER_ID --only equipment
    python onshape_import.py --make-folder "Lab Models"    # once: a new folder in vcl-shared
    python onshape_import.py --add equipment sandbox       # the latest batch of new tabs, into the existing documents
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
CACHE = HERE.parent / "cad" / ".cache"
BASE = "https://cad.onshape.com/api/v10"
VCL_SHARED = "222f47147b861ce6fc04396f"        # vcl-shared, owned by the Vertical Cloud Lab team
LAB_TEAM = "69eaf7207a4e49d261c433fb"          # owner id of that team (ownerType 1)
LAB_MODELS = "4213db40f9a2525e7c715685"        # vcl-shared > Lab Models, made 2026-09-26 by make_folder

# document key -> (title, [(tab name, STEP path)])
DOCS = {
    "sandbox": ("Sandbox objects", [
        ("Labware lineup", EXPORTS / "labware_lineup.step"),
        ("Sandbox layout (spot D)", EXPORTS / "sandbox_layout.step"),
        ("AgileX PiPER with gripper (AgileX STEP)", CACHE / "AgileX PiPER with Gripper-1-STP.STEP"),
    ]),
    "equipment": ("Lab equipment", [
        ("Bambu A1 mini", EXPORTS / "bambu_a1_mini.step"),
        ("Bambu H2D", EXPORTS / "bambu_h2d.step"),
        ("Opentrons OT-2 (Opentrons STEP)", CACHE / "OT-2 Reference Model Detailed.STEP"),
        ("AgileX PiPER with gripper (AgileX STEP)", CACHE / "AgileX PiPER with Gripper-1-STP.STEP"),
        ("CubXL", EXPORTS / "cubxl.step"),
        ("Lansmont M23 drop tower", EXPORTS / "lansmont_m23_drop_tower.step"),
        ("AMAZEMET rePowder atomizer", EXPORTS / "amazemet_repowder.step"),
    ]),
    "room": ("CB154 room", [
        ("CB154 with equipment", EXPORTS / "onshape" / "cb154_room.step"),
    ]),
}

# Tabs added later to documents that already exist (ids in the run record), one batch per session.
# The key can't delete, so a model that changes goes in as a new tab and the one it replaces stays
# behind; a replacement is uploaded under a new file name, since the tab takes the file's name.
BATCHES = {
    "2026-09-27": {
        "equipment": [
            ("A&D HR-100A with breeze break", EXPORTS / "labware" / "balance_hr100a.step", None),
            ("Labconco glove box", EXPORTS / "labconco_glovebox.step", None),
            ("Aconity MIDI", EXPORTS / "aconity_midi.step", None),
        ],
        "sandbox": [
            ("A&D HR-100A with breeze break", EXPORTS / "labware" / "balance_hr100a.step", None),
            ("Sandbox layout (spot D), real HR-100A", EXPORTS / "sandbox_layout.step", "sandbox_layout_hr100a.step"),
        ],
    },
    "2026-10-03": {
        "equipment": [
            ("HR-100A, AutoTrickler V4 lid", EXPORTS / "labware" / "balance_hr100a.step", "balance_hr100a_autotrickler_lid.step"),
            ("HR-100A, A&D stock lid", EXPORTS / "labware" / "balance_hr100a_stock_lid.step", None),
            ("MSE PRO acrylic glove box", EXPORTS / "mse_pro_glovebox.step", None),
            ("Aconity MIDI, reworked", EXPORTS / "aconity_midi.step", "aconity_midi_v2.step"),
        ],
        "sandbox": [
            ("HR-100A, AutoTrickler V4 lid", EXPORTS / "labware" / "balance_hr100a.step", "balance_hr100a_autotrickler_lid.step"),
            ("AutoTrickler V4 lid", EXPORTS / "labware" / "lid_autotrickler_v4.step", None),
            ("FXi-10 stock lid", EXPORTS / "labware" / "lid_fxi10_stock.step", None),
        ],
    },
}
LATEST = max(BATCHES)


class Api:
    def __init__(self):
        self.s = requests.Session()
        self.s.auth = (os.environ["ONSHAPE_ACCESS_KEY"], os.environ["ONSHAPE_SECRET_KEY"])
        self.s.headers["Accept"] = "application/json;charset=UTF-8; qs=0.09"
        self.calls = 0

    def call(self, method, path, **kw):
        self.calls += 1
        r = self.s.request(method, BASE + path, timeout=600, **kw)
        if not r.ok:
            raise RuntimeError(f"{method} {path} -> HTTP {r.status_code}: {r.text[:600]}")
        return r.json() if r.content else {}


def upload(api: Api, did: str, wid: str, path: Path, name: str | None = None) -> str:
    with path.open("rb") as fh:
        # Exactly the fields of Onshape's documented example; storeInDocument/yAxisIsUp give HTTP 400 (#234).
        tr = api.call("POST", f"/translations/d/{did}/w/{wid}", files={"file": (name or path.name, fh, "application/octet-stream")},
                      data={"formatName": "", "flattenAssemblies": "true", "translate": "true"})
    return tr["id"]


def poll(api: Api, pending: dict[str, str], first_wait: float) -> dict:
    """Wait once, then poll each translation until it is done."""
    time.sleep(first_wait)
    tabs = {}
    for tab, tid in pending.items():
        for _ in range(20):
            st = api.call("GET", f"/translations/{tid}")
            if st["requestState"] != "ACTIVE":
                break
            time.sleep(30)
        tabs[tab] = {"state": st["requestState"], "elements": st.get("resultElementIds"),
                     "failure": st.get("failureReason")}
        print(f"  {tab}: {st['requestState']}", flush=True)
    return tabs


def add_tabs(api: Api, base: dict, keys: list[str], first_wait: float, batch: dict) -> dict:
    """Import a batch's STEP files as new tabs of the documents in an earlier run record."""
    out = {}
    for k in keys:
        doc = base["documents"][k]
        did, wid = doc["document"].split("/documents/")[1].split("/w/")
        pending = {}
        for tab, path, name in batch[k]:
            pending[tab] = upload(api, did, wid, path, name)
            print(f"  uploaded {path.name} ({path.stat().st_size / 1e6:.1f} MB) into {doc['name']!r} as {tab!r}", flush=True)
        rec = {"document": doc["document"], "tabs": poll(api, pending, first_wait)}
        if k == "sandbox" and any(t.startswith("Sandbox layout") for t, _, _ in batch[k]):
            # a new assembly on the new layout, with the arm tab already there
            layout = next((t["elements"][0] for n, t in rec["tabs"].items() if n.startswith("Sandbox layout") and t["elements"]), None)
            arm = next((t["elements"][0] for n, t in doc["tabs"].items() if "PiPER" in n and t.get("elements")), None)
            if layout and arm:
                try:
                    rec["assembly"] = sandbox_assembly(api, did, wid, layout, arm, "Sandbox with PiPER (HR-100A)")
                except RuntimeError as exc:
                    rec["assembly_error"] = str(exc)[:300]
        out[k] = rec
        print(json.dumps(rec, indent=2), flush=True)
    return out


# AgileX's STEP (Y-up, as imported) -> the sandbox layout: turn it Z-up (+90 deg about x), shift
# its base onto the origin (vendor.py measures (0, 9.2, 4.0) mm), yaw it -90 deg to the URDF's
# zero, and lift it onto the 12 mm arm plate. Row-major, metres.
PIPER_IN_SANDBOX = [0, 0, -1, 0.0092,
                    -1, 0, 0, 0.0,
                    0, 1, 0, 0.016,
                    0, 0, 0, 1]


def sandbox_assembly(api: Api, did: str, wid: str, layout_eid: str, piper_eid: str,
                     name: str = "Sandbox with PiPER") -> str:
    """One assembly tab: the layout Part Studio, and AgileX's arm placed on its plate (5 calls)."""
    eid = api.call("POST", f"/assemblies/d/{did}/w/{wid}", json={"name": name})["id"]
    for ps in (layout_eid, piper_eid):
        api.call("POST", f"/assemblies/d/{did}/w/{wid}/e/{eid}/instances",
                 json={"documentId": did, "elementId": ps, "isWholePartStudio": True})
    asm = api.call("GET", f"/assemblies/d/{did}/w/{wid}/e/{eid}")
    # A whole-Part-Studio insert makes one instance per part (74 for AgileX's arm), so move them all
    arm = [i["id"] for i in asm["rootAssembly"]["instances"] if i.get("elementId") == piper_eid]
    api.call("POST", f"/assemblies/d/{did}/w/{wid}/e/{eid}/occurrencetransforms",
             json={"occurrences": [{"path": [a]} for a in arm], "transform": PIPER_IN_SANDBOX, "isRelative": False})
    return eid


def make_folder(api: Api, name: str, parent: str = VCL_SHARED, owner: str = LAB_TEAM) -> str:
    d = api.call("POST", "/folders", json={"name": name, "parentId": parent, "ownerId": owner, "ownerType": 1})
    return d["id"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", default=LAB_MODELS, help="id of the target folder (from its URL)")
    ap.add_argument("--make-folder", metavar="NAME", help="create a folder in vcl-shared and print its id")
    ap.add_argument("--only", nargs="*", choices=list(DOCS), help="just these documents")
    ap.add_argument("--first-wait", type=float, default=90.0, help="seconds before the first poll")
    ap.add_argument("--add", nargs="+", choices=["equipment", "sandbox"], help="add a batch's tabs to these existing documents")
    ap.add_argument("--batch", default=LATEST, choices=list(BATCHES), help="which batch of tabs (default: the latest)")
    ap.add_argument("--record", default="run_2026-09-26.json", help="run record holding the existing documents")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.make_folder:
        api = Api()
        print(make_folder(api, args.make_folder))
        return
    if args.add:
        batch = BATCHES[args.batch]
        tabs = [(t, p) for k in args.add for t, p, _ in batch.get(k, [])]
        for _, p in tabs:
            if not p.exists():
                raise SystemExit(f"missing {p}: run cad/build.py first")
        if args.dry_run:
            print("\n".join(f"{t} [{p.stat().st_size / 1e6:.1f} MB]" for t, p in tabs))
            print(f"about {2 * len(tabs)} calls, plus 4 if the batch has a new sandbox layout")
            return
        api = Api()
        base = json.loads((HERE / args.record).read_text())
        record = {"date": time.strftime("%Y-%m-%d"), "batch": args.batch, "added_to": args.record,
                  "documents": add_tabs(api, base, [k for k in args.add if k in batch], args.first_wait, batch)}
        record["api_calls_used"] = api.calls
        out = HERE / f"run_{record['date']}_add.json"
        out.write_text(json.dumps(record, indent=2) + "\n")
        print(f"{api.calls} API calls; record in {out.name}")
        return
    sha = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()
    keys = args.only or list(DOCS)
    for k in keys:
        for _, p in DOCS[k][1]:
            if not p.exists():
                raise SystemExit(f"missing {p}: run cad/build.py first (and cad/vendor.py for vendor STEP)")
    if args.dry_run:
        for k in keys:
            title, tabs = DOCS[k]
            print(f"{title} ({sha}): " + ", ".join(f"{t} [{p.stat().st_size / 1e6:.1f} MB]" for t, p in tabs))
        n = sum(len(DOCS[k][1]) for k in keys)
        print(f"about {len(keys) + 2 * n + 5} calls (create, then upload and poll per tab, plus the sandbox assembly)")
        return
    api = Api()
    record = {"date": time.strftime("%Y-%m-%d"), "commit": sha, "folder": args.folder, "documents": {}}
    for k in keys:
        title, tabs = DOCS[k]
        name = f"{title} ({sha})"
        doc = api.call("POST", "/documents", json={"name": name, "isPublic": False, "parentId": args.folder,
                                                   "ownerId": LAB_TEAM, "ownerType": 1})
        did, wid = doc["id"], doc["defaultWorkspace"]["id"]
        rec = {"name": name, "document": f"https://cad.onshape.com/documents/{did}/w/{wid}",
               "parentId": doc.get("parentId"), "owner": (doc.get("owner") or {}).get("name"), "tabs": {}}
        pending = {}
        for tab, path in tabs:
            pending[tab] = upload(api, did, wid, path)
            print(f"  uploaded {path.name} ({path.stat().st_size / 1e6:.1f} MB) as {tab!r}", flush=True)
        rec["tabs"] = poll(api, pending, args.first_wait)
        # Tabs keep their STEP file names: the public API has no element rename (POST /elements/...
        # is HTTP 405, tried 2026-09-26), so the files are named for what they hold instead.
        if k == "sandbox":
            els = {t: (i.get("elements") or [None])[0] for t, i in rec["tabs"].items()}
            layout = next((e for t, e in els.items() if t.startswith("Sandbox layout")), None)
            arm = next((e for t, e in els.items() if "PiPER" in t), None)
            if layout and arm:
                try:
                    rec["assembly"] = sandbox_assembly(api, did, wid, layout, arm)
                except RuntimeError as exc:
                    rec["assembly_error"] = str(exc)[:300]
        record["documents"][k] = rec
        print(json.dumps(rec, indent=2), flush=True)
    record["api_calls_used"] = api.calls
    out = HERE / f"run_{record['date']}.json"
    out.write_text(json.dumps(record, indent=2) + "\n")
    print(f"{api.calls} API calls; record in {out.name}")


if __name__ == "__main__":
    main()
