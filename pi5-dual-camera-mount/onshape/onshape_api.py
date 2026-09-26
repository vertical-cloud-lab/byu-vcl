#!/usr/bin/env python3
"""Put the Pi 5 dual-camera mount and its C-mount collar into Onshape over the REST API.

Creates a new Onshape document, then

  1. builds the mount and the collar as native Onshape features (features.py): ordinary
     sketches and extrudes on the Top, Front and Right planes, which stay editable there,
  2. checks each one against CadQuery with Onshape's own mass properties and bounding box,
  3. imports the STEP exports (both printed parts and both colour assemblies), and
  4. saves shaded views of the result in evidence/.

It follows the OT-2 lid mount's onshape_api.py (PR #234), which found that the translation
endpoint accepts only the fields of Onshape's documented example.

Credentials come from the environment, never the command line:

    ONSHAPE_ACCESS_KEY, ONSHAPE_SECRET_KEY   API keys (My Account > Developer > API keys) with
                                             the Read and Write scopes
    ONSHAPE_BASE_URL                         optional, default https://cad.onshape.com

    python onshape_api.py --dry-run                     # no network; every request goes to dry_run.json
    python onshape_api.py                               # a new document in your own Onshape home
    python onshape_api.py --parent FOLDER --owner-id ID --owner-type 1   # ...in a company folder
    python onshape_api.py --document URL --skip-native --step collar     # one more STEP, existing document

A full run is about 60 API calls. Only successful calls count, and an EDU Educator plan gets
2,500 a year for the whole company (https://onshape-public.github.io/docs/auth/limits/).
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import features as F  # noqa: E402

API = "/api/v10"
PLANE_IDS = {"Front": "JCC", "Top": "JDC", "Right": "JEC"}   # deterministic ids of the default planes
M = 0.001                      # sketch geometry is in metres
STEPS = ("mount", "collar", "assembly_hq_cm3", "assembly_2x_cm3")   # files in ../exports, .step
# The native part studios: tab name, key in features.check(), part name, shaded views to save.
NATIVE = (("Mount (native features)", "mount", "Pi 5 dual-camera mount", ("front_left", "rear_right")),
          ("C-mount collar (native features)", "collar", "C-mount collar", ("top_iso",)))
NAME_PROPERTY = "57f3fb8efa3416c06701d60d"                          # Onshape's "Name" metadata property
# 3 x 4 view matrices, row-major (screen right, screen up, towards the viewer).
VIEWS = {
    "front_left": "0.707,-0.707,0,0,0.408,0.408,0.816,0,-0.577,-0.577,0.577,0",
    "rear_right": "-0.707,0.707,0,0,-0.408,-0.408,0.816,0,0.577,0.577,0.577,0",
    "top_iso": "0.707,0.707,0,0,-0.408,0.408,0.816,0,0.577,-0.577,0.577,0",
}


class Onshape:
    def __init__(self, base_url: str, access: str, secret: str):
        self.base = base_url.rstrip("/")
        self.s = requests.Session()
        self.s.auth = (access, secret)              # Onshape accepts API keys as HTTP Basic auth
        self.s.headers["Accept"] = "application/json;charset=UTF-8; qs=0.09"
        self.n = 0

    def call(self, method: str, path: str, **kw) -> dict:
        r = self.s.request(method, self.base + API + path, timeout=180, **kw)
        if not r.ok:
            raise RuntimeError(f"{method} {path} -> HTTP {r.status_code}: {r.text[:800]}")
        self.n += 1                                  # only successful calls count against the quota
        return r.json() if r.content else {}

    # --- documents -----------------------------------------------------------------
    def whoami(self) -> dict:
        return self.call("GET", "/users/sessioninfo")

    def create_document(self, name: str, parent: str | None, owner_id: str | None, owner_type: int | None) -> tuple[str, str]:
        body = {"name": name, "isPublic": False}
        if parent:
            body["parentId"] = parent
        if owner_id:
            body.update({"ownerId": owner_id, "ownerType": owner_type})
        doc = self.call("POST", "/documents", json=body)
        return doc["id"], doc["defaultWorkspace"]["id"]

    def elements(self, did: str, wid: str) -> list[dict]:
        return self.call("GET", f"/documents/d/{did}/w/{wid}/elements")

    def create_part_studio(self, did: str, wid: str, name: str) -> str:
        return self.call("POST", f"/partstudios/d/{did}/w/{wid}", json={"name": name})["id"]

    def name_element(self, did: str, wid: str, eid: str, name: str) -> None:
        self.call("POST", f"/metadata/d/{did}/w/{wid}/e/{eid}",
                  json={"properties": [{"propertyId": NAME_PROPERTY, "value": name}]})

    # --- features ------------------------------------------------------------------
    def add_feature(self, did: str, wid: str, eid: str, feature: dict) -> str:
        body = {"btType": "BTFeatureDefinitionCall-1406", "feature": feature}
        out = self.call("POST", f"/partstudios/d/{did}/w/{wid}/e/{eid}/features", json=body)
        state = out.get("featureState", {}).get("featureStatus", "?")
        print(f"  + {feature['name']:<44} {state}")
        if state not in ("OK", "INFO"):
            raise RuntimeError(f"feature {feature['name']!r} regenerated with status {state}")
        return out["feature"]["featureId"]

    def mass_properties(self, did: str, wid: str, eid: str) -> dict:
        return self.call("GET", f"/partstudios/d/{did}/w/{wid}/e/{eid}/massproperties")

    def bounding_box(self, did: str, wid: str, eid: str) -> dict:
        return self.call("GET", f"/partstudios/d/{did}/w/{wid}/e/{eid}/boundingboxes")

    def parts(self, did: str, wid: str, eid: str) -> list[dict]:
        return self.call("GET", f"/parts/d/{did}/w/{wid}/e/{eid}")

    def name_part(self, did: str, wid: str, eid: str, pid: str, name: str) -> None:
        self.call("POST", f"/metadata/d/{did}/w/{wid}/e/{eid}/p/{pid}",
                  json={"properties": [{"propertyId": NAME_PROPERTY, "value": name}]})

    # --- assembly ------------------------------------------------------------------
    def create_assembly(self, did: str, wid: str, name: str) -> str:
        return self.call("POST", f"/assemblies/d/{did}/w/{wid}", json={"name": name})["id"]

    def insert_part(self, did: str, wid: str, asm: str, part_studio: str, pid: str) -> None:
        self.call("POST", f"/assemblies/d/{did}/w/{wid}/e/{asm}/instances", json={
            "documentId": did, "elementId": part_studio, "partId": pid, "isAssembly": False,
            "isWholePartStudio": False})

    def instances(self, did: str, wid: str, asm: str) -> list[dict]:
        return self.call("GET", f"/assemblies/d/{did}/w/{wid}/e/{asm}")["rootAssembly"]["instances"]

    def place(self, did: str, wid: str, asm: str, instance: str, matrix: list[float]) -> None:
        self.call("POST", f"/assemblies/d/{did}/w/{wid}/e/{asm}/occurrencetransforms", json={
            "isRelative": False, "occurrences": [{"path": [instance]}], "transform": matrix})

    def shaded_view(self, did: str, wid: str, eid: str, view: str, out: Path, w: int = 1000, h: int = 700,
                    kind: str = "partstudios") -> None:
        r = self.call("GET", f"/{kind}/d/{did}/w/{wid}/e/{eid}/shadedviews", params={
            "viewMatrix": VIEWS[view], "outputWidth": w, "outputHeight": h, "pixelSize": 0,
            "edges": "show", "showAllParts": "true", "useAntiAliasing": "true"})
        images = r.get("images") or []
        img = images[0] if images and isinstance(images[0], str) else (images[0][0] if images else None)
        if not img:
            raise RuntimeError("no image in the shaded view response")
        out.write_bytes(base64.b64decode(img))

    # --- import --------------------------------------------------------------------
    def import_step(self, did: str, wid: str, path: Path) -> list[str]:
        before = {e["id"] for e in self.elements(did, wid)}
        with path.open("rb") as fh:
            tr = self.call("POST", f"/translations/d/{did}/w/{wid}", files={
                "file": (path.name, fh, "application/octet-stream"),
            }, data={
                # Exactly the fields of Onshape's documented example; PR #234 found that adding
                # storeInDocument or yAxisIsUp gets HTTP 400 "illegal argument".
                "formatName": "", "flattenAssemblies": "true", "translate": "true",
            })
        tid = tr["id"]
        for _ in range(40):                     # every poll counts against the yearly limit
            time.sleep(8)
            st = self.call("GET", f"/translations/{tid}")
            if st["requestState"] == "DONE":
                return st.get("resultElementIds") or sorted({e["id"] for e in self.elements(did, wid)} - before)
            if st["requestState"] == "FAILED":
                raise RuntimeError(f"import of {path.name} failed: {st.get('failureReason')}")
        raise TimeoutError(f"import of {path.name} still running after 5 minutes")


class DryRun(Onshape):
    """Stands in for the API: records every request and answers with placeholders, so the
    whole flow can be exercised and its payloads reviewed without keys."""

    def __init__(self):
        self.base = "https://cad.onshape.com"
        self.log: list[dict] = []
        self.n = 0
        self.inserted: list[str] = []

    def call(self, method: str, path: str, **kw) -> dict:
        self.n += 1
        body = kw.get("json")
        if body is None and "data" in kw:
            body = {"form": kw["data"], "file": kw["files"]["file"][0]}
        self.log.append({"method": method, "path": API + path, "params": kw.get("params"), "body": body})
        if path == "/users/sessioninfo":
            return {"name": "dry run"}
        if path == "/documents":
            return {"id": "DID", "defaultWorkspace": {"id": "WID"}}
        if path.endswith("/features"):
            return {"feature": {"featureId": f"F{self.n}"}, "featureState": {"featureStatus": "OK"}}
        if path.endswith("/massproperties"):
            return {"bodies": {"-all-": {"volume": [0.0, 0.0, 0.0]}}}
        if path.endswith("/boundingboxes"):
            return {k: 0.0 for k in ("lowX", "lowY", "lowZ", "highX", "highY", "highZ")}
        if path.endswith("/shadedviews"):
            return {"images": [base64.b64encode(b"").decode() or "AA=="]}
        if path.startswith("/parts/"):
            return [{"partId": "JHD", "name": "Part 1"}]
        if path.startswith("/partstudios/"):
            return {"id": f"EID{self.n}"}
        if path.startswith("/translations/d/"):
            return {"id": f"TID{self.n}"}
        if path.startswith("/translations/"):
            return {"requestState": "DONE", "resultElementIds": [f"E{self.n}"]}
        if path.endswith("/elements"):
            return [{"id": "DEFAULT", "name": "Part Studio 1", "elementType": "PARTSTUDIO"},
                    {"id": "ASSEMBLY", "name": "Assembly 1", "elementType": "ASSEMBLY"}]
        if path.endswith("/instances"):
            self.inserted.append(body["elementId"])
        if path.startswith("/assemblies/") and method == "POST" and path.count("/") == 5:
            return {"id": "ASM"}
        return {}

    def shaded_view(self, did, wid, eid, view, out, w=1000, h=700, kind="partstudios") -> None:
        self.call("GET", f"/{kind}/d/{did}/w/{wid}/e/{eid}/shadedviews", params={"viewMatrix": VIEWS[view]})

    def instances(self, did, wid, asm) -> list[dict]:
        self.call("GET", f"/assemblies/d/{did}/w/{wid}/e/{asm}")
        return [{"id": f"I{i}", "elementId": e} for i, e in enumerate(self.inserted)]


# --- feature JSON ---------------------------------------------------------------------

def quantity(pid: str, mm: float) -> dict:
    return {"btType": "BTMParameterQuantity-147", "parameterId": pid, "expression": f"{round(mm, 6):g} mm",
            "isInteger": False}


def enum(pid: str, enum_name: str, value: str) -> dict:
    return {"btType": "BTMParameterEnum-145", "parameterId": pid, "enumName": enum_name, "value": value}


def boolean(pid: str, value: bool) -> dict:
    return {"btType": "BTMParameterBoolean-144", "parameterId": pid, "value": value}


def entities(e, eid: str) -> list[dict]:
    """One sketch entity as Onshape JSON. Arcs run counter-clockwise with their parameters (radians
    from the sketch's x direction) kept within 0..2 pi, so an arc across that direction is sent as
    two arcs that meet on it."""
    if isinstance(e, F.Circle):
        return [{"btType": "BTMSketchCurve-4", "entityId": eid, "centerId": f"{eid}.center",
                 "geometry": {"btType": "BTCurveGeometryCircle-115", "radius": e.r * M, "xCenter": e.cx * M,
                              "yCenter": e.cy * M, "xDir": 1.0, "yDir": 0.0, "clockwise": False}}]
    if isinstance(e, F.Line):
        dx, dy = e.x1 - e.x0, e.y1 - e.y0
        length = math.hypot(dx, dy)
        return [{"btType": "BTMSketchCurveSegment-155", "entityId": eid, "startPointId": f"{eid}.start",
                 "endPointId": f"{eid}.end", "startParam": 0.0, "endParam": length * M,
                 "geometry": {"btType": "BTCurveGeometryLine-117", "pntX": e.x0 * M, "pntY": e.y0 * M,
                              "dirX": dx / length, "dirY": dy / length}}]
    tau = 2 * math.pi
    a0 = e.a0 % tau
    a1 = a0 + (e.a1 - e.a0)
    spans = [(a0, min(a1, tau))] if a1 <= tau + 1e-9 else [(a0, tau), (0.0, a1 - tau)]
    out = []
    for i, (s, t) in enumerate(spans):
        sid = eid if len(spans) == 1 else f"{eid}{'ab'[i]}"
        out.append({"btType": "BTMSketchCurveSegment-155", "entityId": sid, "startPointId": f"{sid}.start",
                    "endPointId": f"{sid}.end", "centerId": f"{sid}.center", "startParam": s, "endParam": t,
                    "geometry": {"btType": "BTCurveGeometryCircle-115", "radius": e.r * M, "xCenter": e.cx * M,
                                 "yCenter": e.cy * M, "xDir": 1.0, "yDir": 0.0, "clockwise": False}})
    return out


def sketch_json(s: F.Sketch) -> dict:
    ents = [j for i, loop in enumerate(s.loops) for k, e in enumerate(loop) for j in entities(e, f"l{i}e{k}")]
    return {
        "btType": "BTMSketch-151", "featureType": "newSketch", "name": s.name,
        "parameters": [{"btType": "BTMParameterQueryList-148", "parameterId": "sketchPlane",
                        "queries": [{"btType": "BTMIndividualQuery-138", "deterministicIds": [PLANE_IDS[s.plane]]}]}],
        "entities": ents, "constraints": [],
    }


def extrude_json(x: F.Extrude, sketch_id: str) -> dict:
    params = [
        enum("bodyType", "ExtendedToolBodyType", "SOLID"),
        enum("operationType", "NewBodyOperationType", x.op),
        {"btType": "BTMParameterQueryList-148", "parameterId": "entities",
         "queries": [{"btType": "BTMIndividualSketchRegionQuery-140", "featureId": sketch_id}]},
        enum("endBound", "BoundingType", "THROUGH_ALL" if x.depth is None else "BLIND"),
        boolean("oppositeDirection", x.opposite),
        boolean("symmetric", x.symmetric),
    ]
    if x.depth is not None:
        params.append(quantity("depth", x.depth))
    if x.start_offset:
        params += [boolean("startOffset", True), enum("startOffsetBound", "StartOffsetType", "BLIND"),
                   quantity("startOffsetDistance", x.start_offset),
                   boolean("startOffsetOppositeDirection", x.start_opposite)]
    if x.op != "NEW":
        params.append(boolean("defaultScope", True))
    return {"btType": "BTMFeature-134", "featureType": "extrude", "name": x.name, "parameters": params}


def collar_placement(p) -> list[float]:
    """4 x 4 transform, row-major and in metres, from the collar's print frame (front face on
    the Top plane, legs up +Z) to its place on the left station, in the mount's frame."""
    y_front = F.m.hq_front_y(p) - p.collar_front
    return [1, 0, 0, p.stations[0] * M,
            0, 0, 1, y_front * M,
            0, -1, 0, p.axis_z * M,
            0, 0, 0, 1]


def assemble(api: Onshape, did: str, wid: str, asm: str, mount_eid: str, collar_eid: str, evidence: Path) -> dict:
    """The two native parts in an assembly, the collar where it sits on an HQ Camera."""
    for eid in (mount_eid, collar_eid):
        api.insert_part(did, wid, asm, eid, api.parts(did, wid, eid)[0]["partId"])
    by_element = {i["elementId"]: i["id"] for i in api.instances(did, wid, asm)}
    api.place(did, wid, asm, by_element[collar_eid], collar_placement(F.m.Params()))
    out = evidence / "api-assembly-native.png"
    api.shaded_view(did, wid, asm, "front_left", out, 1200, 800, kind="assemblies")
    return {"element": asm, "instances": 2, "shaded_view": out.name}


def build(api: Onshape, did: str, wid: str, eid: str, features: list) -> None:
    ids: dict[str, str] = {}
    for f in features:
        if isinstance(f, F.Sketch):
            ids[f.name] = api.add_feature(did, wid, eid, sketch_json(f))
        else:
            api.add_feature(did, wid, eid, extrude_json(f, ids[f.sketch]))


def measure(api: Onshape, did: str, wid: str, eid: str) -> dict:
    mp = api.mass_properties(did, wid, eid)
    bb = api.bounding_box(did, wid, eid)
    return {"volume_mm3": round(mp["bodies"]["-all-"]["volume"][0] * 1e9, 3),
            "bbox_mm": {k: round(v * 1000, 3) for k, v in bb.items() if k[:3] in ("low", "hig")}}


def git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True,
                              cwd=HERE, check=True).stdout.strip()
    except Exception:
        return "local"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", default=f"Pi 5 dual-camera mount ({git_sha()})")
    ap.add_argument("--parent", metavar="FOLDER_ID", help="folder for the new document")
    ap.add_argument("--owner-id", help="company or team that owns it (with --owner-type)")
    ap.add_argument("--owner-type", type=int, help="0 user, 1 company, 2 team")
    ap.add_argument("--document", metavar="URL", help="work in an existing document instead of creating one")
    ap.add_argument("--skip-native", action="store_true", help="only import the STEP files")
    ap.add_argument("--skip-import", action="store_true", help="only build the native features")
    ap.add_argument("--skip-assembly", action="store_true", help="no assembly of the two native parts")
    ap.add_argument("--step", action="append", choices=STEPS, metavar="NAME",
                    help=f"import only this STEP file (repeatable; default all of: {', '.join(STEPS)})")
    ap.add_argument("--dry-run", action="store_true",
                    help="no network: run the whole flow against a stub and save every request to dry_run.json")
    args = ap.parse_args()

    if args.dry_run:
        api = DryRun()
        time.sleep = lambda _s: None             # noqa: E731  (no waiting on a stub)
    else:
        access, secret = os.environ.get("ONSHAPE_ACCESS_KEY"), os.environ.get("ONSHAPE_SECRET_KEY")
        if not (access and secret):
            raise SystemExit("ONSHAPE_ACCESS_KEY and ONSHAPE_SECRET_KEY must be set (see the README).")
        api = Onshape(os.environ.get("ONSHAPE_BASE_URL", "https://cad.onshape.com"), access, secret)
    print("signed in as", api.whoami().get("name", "?"))

    if args.document:
        mt = re.search(r"/documents/(\w+)/w/(\w+)", args.document)
        if not mt:
            raise SystemExit(f"not a workspace URL: {args.document}")
        did, wid = mt.groups()
        default = []
        assemblies = [e["id"] for e in api.elements(did, wid)
                      if e.get("elementType") == "ASSEMBLY" and re.fullmatch(r"Assembly \d+", e.get("name", ""))]
    else:
        did, wid = api.create_document(args.name, args.parent, args.owner_id, args.owner_type)
        els = api.elements(did, wid)
        default = [e["id"] for e in els if e.get("elementType") == "PARTSTUDIO"]
        assemblies = [e["id"] for e in els if e.get("elementType") == "ASSEMBLY"]
    url = f"{api.base}/documents/{did}/w/{wid}"
    print("document:", url)
    summary: dict = {"document": url, "name": args.name, "part_studios": {}, "imports": {}, "failures": []}
    evidence = HERE / "evidence"
    evidence.mkdir(exist_ok=True)
    reference = F.check()                        # CadQuery: the same features, and mount.py
    p = F.m.Params()
    feats = {"mount": F.mount_features(p), "collar": F.collar_features(p)}
    tabs = {e["name"]: e["id"] for e in api.elements(did, wid)} if args.document else {}
    for label, key, part_name, views in NATIVE:
        rec = {"features": len(feats[key]), "cadquery_volume_mm3": reference[key]["volume_mount_py_mm3"]}
        try:
            if args.skip_native:                 # re-measure tabs an earlier run built
                eid = tabs.get(label)
                if eid is None:
                    continue
            else:
                eid = None
                if default:                      # a new document's empty "Part Studio 1": reuse it
                    try:
                        api.name_element(did, wid, default[0], label)
                        eid = default.pop(0)
                    except RuntimeError as exc:
                        print("  (could not rename the default part studio, adding a tab instead:", str(exc)[:120], ")")
                        default.clear()
                eid = eid or api.create_part_studio(did, wid, label)
                print(f"building {label!r}")
                build(api, did, wid, eid, feats[key])
            rec["element"] = eid
            summary["part_studios"][label] = rec
            rec.update(measure(api, did, wid, eid))
            rec["volume_difference_mm3"] = round(rec["volume_mm3"] - rec["cadquery_volume_mm3"], 3)
            if not args.skip_native:
                parts = api.parts(did, wid, eid)
                if len(parts) == 1:
                    api.name_part(did, wid, eid, parts[0]["partId"], part_name)
                rec["parts"] = len(parts)
            for view in views:
                out = evidence / f"api-{key}-{view.replace('_', '-')}.png"
                if not args.skip_native or not out.exists():
                    api.shaded_view(did, wid, eid, view, out)
                rec.setdefault("shaded_views", []).append(out.name)
        except Exception as exc:                  # keep going: the STEP imports still give a full model
            summary["failures"].append(f"{label}: {exc}")
            print("  !", exc)
    studios = {k: v["element"] for k, v in summary["part_studios"].items() if "element" in v}
    if not args.skip_assembly and len(studios) == 2:
        label = "Mount + C-mount collar (native parts)"
        try:
            asm = assemblies[0] if assemblies else api.create_assembly(did, wid, label)
            if assemblies:                       # a new document's empty "Assembly 1": reuse it
                try:
                    api.name_element(did, wid, asm, label)
                except RuntimeError as exc:
                    print("  (could not rename the assembly:", str(exc)[:120], ")")
            print(f"assembling {label!r}")
            summary["assembly"] = assemble(api, did, wid, asm, studios[NATIVE[0][0]], studios[NATIVE[1][0]], evidence)
        except Exception as exc:
            summary["failures"].append(f"assembly: {exc}")
            print("  !", exc)
    if not args.skip_import:
        exports = HERE.parent / "exports"
        for name in args.step or STEPS:
            try:
                ids = api.import_step(did, wid, exports / f"{name}.step")
                summary["imports"][f"{name}.step"] = ids
                print(f"imported {name}.step -> elements {ids}")
            except Exception as exc:
                summary["failures"].append(f"import {name}.step: {exc}")
                print("  !", exc)
        hq = summary["imports"].get("assembly_hq_cm3.step")
        if hq and not args.dry_run:
            try:
                api.shaded_view(did, wid, hq[0], "front_left", evidence / "api-assembly-hq-cm3.png", 1200, 800)
            except Exception as exc:
                summary["failures"].append(f"assembly view: {exc}")
    summary["api_calls"] = api.n
    if args.dry_run:
        (HERE / "dry_run.json").write_text(json.dumps(api.log, indent=1) + "\n")
    else:
        (HERE / "last_run.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    if summary["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
