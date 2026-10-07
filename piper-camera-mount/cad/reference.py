"""AgileX's own PiPER gripper model, fetched at run time.

AgileX publishes the STEP on its CDN with no licence attached, so it is downloaded into
cad/.cache/ rather than committed (the same rule as Opentrons' OT-2 STEP in
ot2-overhead-camera/lid-mount). Every coordinate in piper_mount.py is in this file's frame.
"""
from __future__ import annotations

import hashlib
import urllib.request
from functools import lru_cache
from pathlib import Path

import cadquery as cq

CACHE = Path(__file__).resolve().parent / ".cache"
GRIPPER_URL = "https://cdn.shopify.com/s/files/1/0673/6848/5000/files/AgileX_Gripper-1-STP.STEP?v=1782224095"
GRIPPER_SHA256 = "6e6c9bb04d7e4b3c7ebcd452dd5e730a4eba2af08b1b80f1e1d2607956a5815d"  # as fetched 2026-09-26

# Solid indices in AgileX_Gripper.STEP (13 solids), as cadquery's importer returns them.
BODY = {0: "motor housing", 1: "linear rail", 2: "finger plate", 3: "back cover", 4: "flange"}
UPPER_FINGER = (5, 6, 7, 8)     # carriage, pad, finger, clamp block; the +Z finger
LOWER_FINGER = (9, 10, 11, 12)  # the -Z finger
OPENING_AS_MODELLED = 31.11 - (-27.27)   # pad to pad, mm


def fetch(url: str = GRIPPER_URL) -> Path:
    CACHE.mkdir(exist_ok=True)
    path = CACHE / "AgileX_Gripper.STEP"
    if not path.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    return path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def gripper_solids() -> tuple[cq.Solid, ...]:
    return tuple(cq.importers.importStep(str(fetch())).solids().vals())


def flange_proxy() -> cq.Solid:
    """A plain O57 x 10.5 mm cylinder where the flange is. OCC's distance and boolean
    routines treat AgileX's flange solid as touching everything (distance 0 to a part
    80 mm away), so the checks use this instead; it is solid where the real flange is
    hollow, which only makes the checks stricter. Renders use the real solid."""
    return cq.Solid.makeCylinder(28.5, 10.5, cq.Vector(-7.91, 54.48, 1.92), cq.Vector(0, 1, 0))


def gripper(opening: float | None = None, for_checks: bool = True) -> dict[str, cq.Workplane]:
    """The gripper as {'body': ..., 'fingers': ...}, with the fingers moved to `opening`
    (pad to pad, 0-100 mm). None leaves them where AgileX's model has them."""
    sol = gripper_solids()
    shift = 0.0 if opening is None else (opening - OPENING_AS_MODELLED) / 2
    body_solids = [flange_proxy() if (i == 4 and for_checks) else sol[i] for i in BODY]
    body = cq.Workplane("XY").add(cq.Compound.makeCompound(body_solids))
    up = [sol[i].translate(cq.Vector(0, 0, shift)) for i in UPPER_FINGER]
    lo = [sol[i].translate(cq.Vector(0, 0, -shift)) for i in LOWER_FINGER]
    fingers = cq.Workplane("XY").add(cq.Compound.makeCompound(up + lo))
    return {"body": body, "fingers": fingers}
