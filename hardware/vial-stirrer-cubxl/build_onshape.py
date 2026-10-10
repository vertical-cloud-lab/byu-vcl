#!/usr/bin/env python3
"""Rebuild the single-vial stirrer in Onshape from ``onshape/vial_stirrer.fs``
and pull the renders and printable meshes back into this folder.

The whole model is one FeatureScript feature, so the Onshape document is
disposable: this script uploads the FeatureScript to the document's Feature
Studio, puts one instance of the feature in the Part Studio, renders every
assembly step with Onshape's own renderer, and exports the printed parts.

Needs an Onshape API key pair with write access to the document, in
``ONSHAPE_ACCESS_KEY`` / ``ONSHAPE_SECRET_KEY`` (cad.onshape.com). Nothing is
printed about the keys.

    python build_onshape.py                # upload, render all steps, export STLs
    python build_onshape.py --no-render    # upload and rebuild only
    python build_onshape.py --new          # make a fresh document first
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import os
import pathlib
import time

import requests

HERE = pathlib.Path(__file__).parent
FS_FILE = HERE / "onshape" / "vial_stirrer.fs"
DOC_FILE = HERE / "onshape" / "document.json"
STEPS_FILE = HERE / "onshape" / "render_steps.json"
IMG = HERE / "img"
STL = HERE / "stl"

BASE = "https://cad.onshape.com/api/v6"
HEADERS = {"Accept": "application/json;charset=UTF-8; qs=0.09", "Content-Type": "application/json"}
# Printed parts to export, by part-name prefix. Only one deck key is exported (two are printed).
PRINTED = {"Base (printed": "base", "Vial holder (printed": "vial_holder",
           "Magnet carrier (printed": "magnet_carrier", "Deck key (printed": "deck_key"}


class Onshape:
    def __init__(self) -> None:
        self.auth = (os.environ["ONSHAPE_ACCESS_KEY"], os.environ["ONSHAPE_SECRET_KEY"])

    def req(self, method: str, path: str, **kw):
        url = path if path.startswith("http") else f"{BASE}/{path.lstrip('/')}"
        headers = {**HEADERS, **kw.pop("headers", {})}
        for attempt in range(5):
            r = requests.request(method, url, auth=self.auth, headers=headers, timeout=180, **kw)
            if r.status_code not in (429, 502, 503, 504):
                return r
            time.sleep(3 + 5 * attempt)
        return r

    def get(self, path, **kw):
        return self.req("GET", path, **kw)

    def post(self, path, **kw):
        return self.req("POST", path, **kw)

    def delete(self, path, **kw):
        return self.req("DELETE", path, **kw)


def new_document(api: Onshape) -> dict:
    r = api.post("documents", json={"name": "single-vial-stirrer-cubxl (byu-vcl #169)", "isPublic": False})
    r.raise_for_status()
    d = r.json()
    did, wid = d["id"], d["defaultWorkspace"]["id"]
    els = api.get(f"documents/d/{did}/w/{wid}/elements").json()
    ps = next(e["id"] for e in els if e["elementType"] == "PARTSTUDIO")
    fs = api.post(f"featurestudios/d/{did}/w/{wid}", json={"name": "vial_stirrer.fs"}).json()["id"]
    asm = next(e["id"] for e in els if e["elementType"] == "ASSEMBLY")
    # the whole Part Studio as one assembly instance, so Onshape's BOM element lists every part
    api.post(f"assemblies/d/{did}/w/{wid}/e/{asm}/instances",
             json={"documentId": did, "elementId": ps, "isWholePartStudio": True, "includePartTypes": ["PARTS"]}).raise_for_status()
    doc = {"did": did, "wid": wid, "partstudio": ps, "featurestudio": fs, "assembly": asm,
           "url": f"https://cad.onshape.com/documents/{did}/w/{wid}/e/{ps}"}
    DOC_FILE.write_text(json.dumps(doc, indent=1) + "\n")
    return doc


def upload(api: Onshape, doc: dict) -> dict:
    did, wid, fs = doc["did"], doc["wid"], doc["featurestudio"]
    cur = api.get(f"featurestudios/d/{did}/w/{wid}/e/{fs}").json()
    r = api.post(f"featurestudios/d/{did}/w/{wid}/e/{fs}", json={
        "contents": FS_FILE.read_text(), "serializationVersion": cur["serializationVersion"],
        "sourceMicroversion": cur["sourceMicroversion"], "rejectMicroversionSkew": False})
    r.raise_for_status()
    specs = api.get(f"featurestudios/d/{did}/w/{wid}/e/{fs}/featurespecs").json()["featureSpecs"]
    if not specs:
        raise SystemExit("FeatureScript did not compile (no feature specs); open the Feature Studio in Onshape to see the error")
    return specs[0]


def params(step: int, exploded: bool = False, section: bool = False) -> list:
    return [
        {"btType": "BTMParameterQuantity-147", "isInteger": True, "value": step, "units": "", "expression": str(step), "parameterId": "step"},
        {"btType": "BTMParameterBoolean-144", "value": exploded, "parameterId": "exploded"},
        {"btType": "BTMParameterBoolean-144", "value": section, "parameterId": "section"},
    ]


def set_feature(api: Onshape, doc: dict, spec: dict, step: int = 0, exploded: bool = False, section: bool = False) -> None:
    did, wid, ps = doc["did"], doc["wid"], doc["partstudio"]
    feat = {"btType": "BTMFeature-134", "featureType": spec["featureType"], "name": "Single-vial stirrer",
            "namespace": spec["namespace"], "parameters": params(step, exploded, section)}
    feats = api.get(f"partstudios/d/{did}/w/{wid}/e/{ps}/features").json()["features"]
    mine = [f for f in feats if f.get("featureType") == spec["featureType"]]
    if mine:
        feat["featureId"] = mine[0]["featureId"]
        r = api.post(f"partstudios/d/{did}/w/{wid}/e/{ps}/features/featureid/{feat['featureId']}", json={"feature": feat})
    else:
        r = api.post(f"partstudios/d/{did}/w/{wid}/e/{ps}/features", json={"feature": feat})
    r.raise_for_status()
    state = r.json().get("featureState", {}).get("featureStatus")
    if state != "OK":
        raise SystemExit(f"feature rebuilt with status {state} (step {step}, exploded {exploded}, section {section})")


def view_matrix(az_deg: float, el_deg: float, ty: float = 0.0) -> str:
    """Onshape 3x4 view matrix. az: degrees from the -Y (front) view toward +X; el: degrees up."""
    az, el = math.radians(az_deg), math.radians(el_deg)
    d = (math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))
    n = math.hypot(d[0], d[1])
    r = (-d[1] / n, d[0] / n, 0.0)
    u = (d[1] * r[2] - d[2] * r[1], d[2] * r[0] - d[0] * r[2], d[0] * r[1] - d[1] * r[0])
    return ",".join(f"{v:.6f}" for v in (*r, 0.0, *u, ty, *d, 0.0))


def shaded(api: Onshape, doc: dict, view: str, w: int, h: int, pixel: float) -> bytes:
    did, wid, ps = doc["did"], doc["wid"], doc["partstudio"]
    r = api.get(f"partstudios/d/{did}/w/{wid}/e/{ps}/shadedviews",
                params={"viewMatrix": view, "outputHeight": h, "outputWidth": w, "pixelSize": pixel, "edges": "show"})
    r.raise_for_status()
    return base64.b64decode(r.json()["images"][0])


def render(api: Onshape, doc: dict, spec: dict, only: set | None = None) -> None:
    from io import BytesIO

    from PIL import Image, ImageDraw, ImageFont

    def font(size, bold=False):
        try:
            return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf", size)
        except OSError:
            return ImageFont.load_default()

    cfg = json.loads(STEPS_FILE.read_text())
    w, h, cap = cfg["width"], cfg["height"], cfg["caption_px"]
    IMG.mkdir(exist_ok=True)
    seq = []
    for s in cfg["frames"]:
        if only and s["key"] not in only:
            continue
        w, h = s.get("width", cfg["width"]), s.get("height", cfg["height"])
        set_feature(api, doc, spec, s["step"], s.get("exploded", False), s.get("section", False))
        v = {**cfg["view"], **s.get("view", {})}
        raw = shaded(api, doc, v["named"] if "named" in v else view_matrix(v["az"], v["el"], v["ty"]), w, h, v["px"])
        im = Image.open(BytesIO(raw)).convert("RGBA")
        canvas = Image.new("RGBA", (w, h + cap), "white")
        canvas.alpha_composite(im, (0, cap))
        d = ImageDraw.Draw(canvas)
        d.rectangle([0, 0, w, cap - 4], fill=(240, 243, 247))
        d.text((18, 12), s["title"], fill=(20, 30, 45), font=font(26, True))
        for i, line in enumerate(s["caption"].split("\n")):
            d.text((18, 50 + 21 * i), line, fill=(60, 70, 85), font=font(17))
        out = IMG / f"{s['key']}.png"
        canvas.convert("RGB").save(out, optimize=True)
        if s.get("sequence", False):
            seq.append(out)
        print("rendered", out.name, flush=True)
    set_feature(api, doc, spec, 0)
    if only:
        return
    # contact sheet and GIF of the numbered steps
    cols = cfg.get("sheet_cols", 4)
    tw, th = cfg["width"] // 2, (cfg["height"] + cap) // 2
    rows = (len(seq) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), "white")
    for i, f in enumerate(seq):
        sheet.paste(Image.open(f).resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
    sheet.save(IMG / "assembly_steps.png", optimize=True)
    frames = [Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS).convert("P", palette=Image.ADAPTIVE, colors=160) for f in seq]
    frames[0].save(IMG / "assembly_steps.gif", save_all=True, append_images=frames[1:], duration=1800, loop=0, optimize=True)


def export_stl(api: Onshape, doc: dict) -> None:
    did, wid, ps = doc["did"], doc["wid"], doc["partstudio"]
    STL.mkdir(exist_ok=True)
    parts = api.get(f"parts/d/{did}/w/{wid}/e/{ps}").json()
    done = set()
    for p in parts:
        stem = next((v for k, v in PRINTED.items() if p["name"].startswith(k)), None)
        if not stem or stem in done:
            continue
        done.add(stem)
        r = api.get(f"parts/d/{did}/w/{wid}/e/{ps}/partid/{p['partId']}/stl",
                    params={"mode": "binary", "units": "millimeter", "angleTolerance": 0.04, "chordTolerance": 0.02},
                    headers={"Accept": "application/vnd.onshape.v1+octet-stream"}, allow_redirects=False)
        if r.status_code in (302, 307):
            r = api.get(r.headers["Location"], headers={"Accept": "application/vnd.onshape.v1+octet-stream"})
        r.raise_for_status()
        (STL / f"{stem}.stl").write_bytes(r.content)
        print("exported", f"{stem}.stl", len(r.content), "bytes", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--new", action="store_true", help="create a fresh Onshape document first")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--no-stl", action="store_true")
    ap.add_argument("--only", default="", help="comma-separated frame keys to re-render (skips the sheet and GIF)")
    a = ap.parse_args()
    api = Onshape()
    doc = new_document(api) if a.new else json.loads(DOC_FILE.read_text())
    spec = upload(api, doc)
    set_feature(api, doc, spec, 0)
    if not a.no_stl:
        export_stl(api, doc)
    if not a.no_render:
        render(api, doc, spec, set(filter(None, a.only.split(","))) or None)
    print("document:", doc["url"])
