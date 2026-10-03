"""Vendor CAD, downloaded into .cache/ at run time and never committed.

Opentrons publishes the OT-2 model in github.com/Opentrons/ot2 for "our community to modify
their OT-2 robots however they choose"; AgileX publishes the PiPER STEP on its store CDN with
no licence attached. Neither is redistributed here: fetch() downloads each file and checks the
SHA-256 it was built against.

Both STEP files are Y-up; load() turns them Z-up with the front facing -y, like everything
else in this folder.
"""
from __future__ import annotations

import hashlib
import io
import urllib.request
import zipfile
from pathlib import Path

import cadquery as cq

from common import CACHE, Model

FILES = {
    "ot2": dict(
        url="https://raw.githubusercontent.com/Opentrons/ot2/ef9ede131ed1d64daf9a0df5b2140a0a8e56b632/"
            "reference-model/STEP/OT-2%20Reference%20Model%20Detailed.STEP",
        name="OT-2 Reference Model Detailed.STEP",
        sha256="f8bf145b878683337ec0f89b74668bd7e350d674777762fab9befbcd014b42d4"),
    "piper": dict(
        url="https://cdn.shopify.com/s/files/1/0673/6848/5000/files/AgileX_PiPER_with_Gripper-1-STP.zip?v=1782225359",
        member="AgileX PiPER with Gripper-1-STP.STEP",
        name="AgileX PiPER with Gripper-1-STP.STEP",
        sha256="91a23674f202c7736183a2134ec0144067d8c447212a7f0881680172196e6919"),
}


def fetch(key: str) -> Path:
    f = FILES[key]
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f["name"]
    if not path.exists():
        req = urllib.request.Request(f["url"], headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=600).read()
        if "member" in f:
            data = zipfile.ZipFile(io.BytesIO(data)).read(f["member"])
        path.write_bytes(data)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != f["sha256"]:
        print(f"warning: {path.name} has sha256 {digest}, built against {f['sha256']}")
    return path


def _solids(key: str) -> list[cq.Solid]:
    """Z-up solids, cached as BREP next to the STEP (a 42 MB STEP takes ~50 s to parse)."""
    brep = CACHE / f"{key}_zup.brep"
    if brep.exists():
        return list(cq.Shape.importBrep(str(brep)).Solids())
    sols = cq.importers.importStep(str(fetch(key))).solids().vals()
    rot = cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90)     # Y-up -> Z-up
    sols = [s.moved(rot) for s in sols]
    comp = cq.Compound.makeCompound(sols)
    bb = comp.BoundingBox()
    if key == "piper":     # centre on the base (the solids in the bottom 40 mm), not the whole arm
        low = [s for s in sols if s.BoundingBox().zmax < bb.zmin + 40]
        c = cq.Compound.makeCompound(low).BoundingBox().center
        shift = cq.Location(cq.Vector(-c.x, -c.y, -bb.zmin))
    else:
        shift = cq.Location(cq.Vector(-bb.center.x, -bb.center.y, -bb.zmin))
    sols = [s.moved(shift) for s in sols]
    cq.Compound.makeCompound(sols).exportBrep(str(brep))
    return sols


def ot2() -> Model:
    m = Model("opentrons_ot2", "Opentrons OT-2", source="Opentrons reference STEP (github.com/Opentrons/ot2)")
    for i, s in enumerate(_solids("ot2")):
        bb = s.BoundingBox()
        # windows are the thin panels; the rest is the white frame/chassis
        thin = min(bb.xlen, bb.ylen, bb.zlen) < 7 and max(bb.xlen, bb.ylen, bb.zlen) > 150
        m.add(f"solid {i + 1}", s, "acrylic" if thin else "printer_white")
    bb = m.bbox()
    m.notes = {"envelope_mm": [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]}
    return m


def piper() -> Model:
    m = Model("agilex_piper", "AgileX PiPER with gripper", source="AgileX STEP (AgileX store CDN)")
    for i, s in enumerate(_solids("piper")):
        m.add(f"solid {i + 1}", s, "printer_white" if s.Volume() > 20000 else "printer_black")
    bb = m.bbox()
    m.notes = {"envelope_as_delivered_mm": [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]}
    return m
