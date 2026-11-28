"""Vendor CAD for the purchased parts that are not McMaster or Actuonix, placed in the same local frame as the
design's stand-in builder (parts.py), or None when the file is not on disk (the builder then uses its stand-in).

Which vendors publish CAD without an account (checked 2026-10-27 through the Pi, cad/vendor/AUDIT_other.md):
  * StepperOnline: the STEP of every motor now sits behind "Log in to download" (not used). The NEMA 34's STEP that
    PR #115 brought in (cad/paternoster/reference/34HS59-6004D-E1000.step) is StepperOnline's own file: nema34()
    serves it to chain-carousel-v2 too.
  * KHK: 3D CAD needs a registered account; its 2D sales drawing is public (used for the pinion's numbers).
  * 80/20: the 'CAD Files' tab did not open for the Pi's browser; the profile drawing is in the gallery (used).
  * Adafruit (github.com/adafruit/Adafruit_CAD_Parts): no model for 3872, 412 or 158.
  * Surplus Center (sprockets, flange bearings): page behind a Cloudflare check; makers' tables used instead.
So everything else is built from the vendor's drawing or table in parts.py.
"""
from __future__ import annotations

import hashlib
from functools import lru_cache
from pathlib import Path

VENDOR = Path(__file__).resolve().parent
CAD = VENDOR.parent
NEMA34_STEP = CAD / "paternoster" / "reference" / "34HS59-6004D-E1000.step"
NEMA34_SHA256 = "9ece1214eed103be2a2693d9e94db0b3cd2ceddab030c7f25f7230916346b804"   # the file PR #115 committed


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


@lru_cache(None)
def _nema34_raw():
    import cadquery as cq
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader

    if not NEMA34_STEP.exists() or _sha256(NEMA34_STEP) != NEMA34_SHA256:
        return None
    rd = STEPControl_Reader()
    if rd.ReadFile(str(NEMA34_STEP)) != IFSelect_RetDone:
        return None
    rd.TransferRoots()
    return cq.Shape.cast(rd.OneShape())


def nema34_cached() -> bool:
    """True when the cropped NEMA 34 is already on disk (then nema34() takes seconds, not minutes)."""
    return (VENDOR / "files" / "stepperonline" / f"34HS59-6004D-E1000.cropped.{NEMA34_SHA256[:12]}.brep").exists()


@lru_cache(None)
def nema34(cable: str = "+x"):
    """StepperOnline's 34HS59-6004D-E1000 STEP in the stand-in's frame: mounting face at z = 0, shaft up (+z), body
    down to z -169 (encoder included). The file's encoder lead and plug hang 150 mm out of the body on its -y side;
    they are cut off 2 mm out of the body (a flexible lead, routed on the bench) and the motor is turned so the lead leaves on
    `cable` ('+x' as chain-carousel-v2's stand-in gland, '-y' as the file). None if the file is missing or changed."""
    import cadquery as cq

    if not NEMA34_STEP.exists() or _sha256(NEMA34_STEP) != NEMA34_SHA256:
        return None
    # the boolean crop takes about 5 min on a shared 4-CPU runner, so its result is kept as a BREP next to the other
    # vendor files (git-ignored) and reused while the STEP's hash is unchanged
    cache = VENDOR / "files" / "stepperonline" / f"34HS59-6004D-E1000.cropped.{NEMA34_SHA256[:12]}.brep"
    if cache.exists():
        s = cq.Shape.importBrep(str(cache))
    else:
        s = _nema34_raw()
        if s is None:
            return None
        keep = cq.Solid.makeBox(110.0, 100.0, 220.0, pnt=cq.Vector(-55.0, -45.0, -180.0))
        s = s.intersect(keep)
        cache.parent.mkdir(parents=True, exist_ok=True)
        s.exportBrep(str(cache))
    if cable == "+x":
        s = s.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), 90.0)
    return s
