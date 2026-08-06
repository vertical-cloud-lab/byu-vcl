#!/usr/bin/env python3
"""Mirror the ``dummy pipette`` Onshape document into this folder.

The document lives on BYU's Onshape enterprise instance and is shared by link
with anonymous read access:

    https://byudesign.onshape.com/documents/7998140a612dc87389384e77/w/fb057218e57432289e21cd0b/e/b6dcdab4f2c49c67192f6f3a

Anonymous link access covers *read* endpoints (document metadata, element list,
the Part Studio feature tree, thumbnails, shaded views) but **not** the export /
translation endpoints -- ``/stl``, ``/parasolid``, ``/gltf`` and
``POST /translations`` all return ``401``, and ``/export`` returns ``403``.
That means this script cannot produce a mesh or a B-rep; see README.md for how
to unblock a real STEP/STL commit.

Usage::

    python fetch_onshape.py            # refresh onshape/ and img/
    python fetch_onshape.py --report   # also print the dimension report

No credentials required. If Onshape API keys are ever added, set
ONSHAPE_ACCESS_KEY / ONSHAPE_SECRET_KEY and the export endpoints become
reachable (not implemented here).
"""

from __future__ import annotations

import argparse
import base64
import json
import pathlib
import re
import urllib.parse
import urllib.request

BASE = "https://byudesign.onshape.com/api/v6"
DID = "7998140a612dc87389384e77"
WID = "fb057218e57432289e21cd0b"
PARTSTUDIO_EID = "b6dcdab4f2c49c67192f6f3a"

HERE = pathlib.Path(__file__).parent
ONSHAPE_DIR = HERE / "onshape"
IMG_DIR = HERE / "img"

HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

# Shaded views Onshape accepts by name for an anonymous read.
VIEWS = ("isometric", "trimetric", "front", "right", "top")


def _get(path: str, params: dict | None = None) -> bytes:
    url = f"{BASE}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS)) as r:
        return r.read()


def _write_json(name: str, raw: bytes) -> dict | list:
    parsed = json.loads(raw)
    (ONSHAPE_DIR / name).write_text(json.dumps(parsed, indent=1) + "\n")
    return parsed


def fetch() -> None:
    ONSHAPE_DIR.mkdir(parents=True, exist_ok=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    _write_json("document.json", _get(f"documents/{DID}"))
    _write_json("elements.json", _get(f"documents/d/{DID}/w/{WID}/elements"))
    _write_json("features.json", _get(f"partstudios/d/{DID}/w/{WID}/e/{PARTSTUDIO_EID}/features"))

    thumb = urllib.request.Request(
        f"https://byudesign.onshape.com/api/thumbnails/d/{DID}/w/{WID}/s/600x340",
        headers={"User-Agent": HEADERS["User-Agent"], "Accept": "image/png"},
    )
    with urllib.request.urlopen(thumb) as r:
        (IMG_DIR / "thumbnail.png").write_bytes(r.read())

    for view in VIEWS:
        raw = _get(
            f"partstudios/d/{DID}/w/{WID}/e/{PARTSTUDIO_EID}/shadedviews",
            {"viewMatrix": view, "outputHeight": 700, "outputWidth": 900, "pixelSize": 0},
        )
        img = base64.b64decode(json.loads(raw)["images"][0])
        (IMG_DIR / f"view_{view}.png").write_bytes(img)


# --------------------------------------------------------------------------- #
# Dimension report
# --------------------------------------------------------------------------- #

# Parameters worth surfacing per feature type; everything else (tolerance
# bounds, unused bound styles, ...) is noise in the raw feature list.
INTERESTING = {
    "extrude": ("operationType", "endBound", "depth", "oppositeDirection", "symmetric"),
    "revolve": ("operationType", "fullRevolve", "angle"),
    "fillet": ("radius",),
    "chamfer": ("chamferType", "width", "angle"),
    "draft": ("angle",),
    "hole": ("style", "holeDiameterV3", "holeDepthV3", "endStyleV2", "locationSignatures"),
}


def _param(feature: dict, pid: str):
    for p in feature.get("parameters", []):
        if p.get("parameterId") == pid:
            return p.get("expression") or p.get("value")
    return None


def _hole_origins(raw: str) -> str:
    """Hole centres, mm. ``locationSignatures`` is JSON-ish but carries bare
    ``0.0165 meter`` literals, so it has to be scraped rather than parsed."""
    out = []
    for block in re.findall(r'"origin"\s*:\s*\[([^\]]*)\]', raw):
        coords = re.findall(r"(-?[\d.eE+-]+)\s*meter", block)
        out.append("(" + ", ".join(f"{float(c) * 1000:.1f}" for c in coords) + ")")
    return "; ".join(out)


def _sketch_extent(feature: dict) -> str:
    """Bounding box of a sketch's non-construction geometry, in mm."""
    xs, ys = [], []
    for e in feature.get("entities", []):
        g = e.get("geometry") or {}
        if e.get("isConstruction"):
            continue
        if "pntX" in g:
            xs.append(g["pntX"])
            ys.append(g["pntY"])
        if "xCenter" in g:
            r = g.get("radius", 0.0)
            xs += [g["xCenter"] - r, g["xCenter"] + r]
            ys += [g["yCenter"] - r, g["yCenter"] + r]
    if not xs:
        return "(no placed geometry)"
    return (
        f"x {min(xs) * 1000:.2f}..{max(xs) * 1000:.2f} mm, "
        f"y {min(ys) * 1000:.2f}..{max(ys) * 1000:.2f} mm"
    )


def report() -> str:
    features = json.loads((ONSHAPE_DIR / "features.json").read_text())["features"]
    lines = []
    for i, f in enumerate(features):
        ftype = f.get("featureType") or f.get("btType")
        name = f.get("name")
        if ftype == "newSketch":
            n = len([e for e in f.get("entities", []) if not e.get("isConstruction")])
            lines.append(f"{i:>3}  {name:<12} sketch    {n} entities; extent {_sketch_extent(f)}")
            continue
        bits = []
        for pid in INTERESTING.get(ftype, ()):
            v = _param(f, pid)
            if v not in (None, "", False):
                if pid == "locationSignatures":
                    v = _hole_origins(v)
                bits.append(f"{pid}={v}")
        lines.append(f"{i:>3}  {str(name):<12} {ftype:<9} " + ", ".join(bits))
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true", help="print the dimension report")
    ap.add_argument("--no-fetch", action="store_true", help="report from the committed files")
    args = ap.parse_args()
    if not args.no_fetch:
        fetch()
    if args.report:
        print(report())
