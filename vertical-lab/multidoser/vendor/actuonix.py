"""Actuonix P16-150-22-12-P from Actuonix's own STEP (P16_STP.zip on actuonix.com/datasheets).

Both carousels' station uses it. `fetch_actuonix.py` downloads the files through the doser
Pi; manifest_actuonix.json pins them by sha256.

Actuonix's file `p16_150mm_in.stp` (retracted): 36 (x) x 20 (y) x 70 (z) gear/motor housing
with the rear clevis tab (10 wide, 8 thick) behind it, the rear hole (dia 4.25) at
(-10.5, y, -4.5), the 12 x 12 tube, the dia 8.94 rod tube, and the rod end: a dia 8 shank and
a 9 x 6 tab with its dia 4.25 hole at z 192.9, 4 mm from the rounded tip. Hole to hole
retracted: 197.4 (datasheet: "Closed length hole to hole 197 mm", "stroke + 47").

`p16_150()` returns (body, rod) in the frame the carousels' layouts use: rear clevis hole
on the y axis at the origin, rod along +z, rod axis on x = 0 (so Actuonix's file is moved
by (+10.5, 0, +4.5)). The rod is returned fully retracted; the layout slides it.
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import step_or_none  # noqa: E402

KEY_IN = "actuonix_p16:p16_150mm_in"
SHIFT = (10.5, 0.0, 4.5)            # Actuonix's frame -> ours (rear hole to the origin, rod axis to x = 0)
ROD_ZMIN = 188.5                    # solids reaching above this (Actuonix's z) belong to the moving rod

# Datasheet (ActuonixP16Datasheet.pdf, rev B) and actuonix.com/p16-150-22-12-p, read 2026-10-27
SPEC = dict(stroke=150.0, closed_hole_to_hole=197.0, gear=22, max_force_N=50.0, backdrive_N=75.0,
            no_load_speed_mm_s=46.0, mass_g=125.0, max_side_load_N=10.0, repeatability_mm=0.6,
            stall_current_A=1.0, voltage=12.0, max_duty_cycle=0.20, backlash_mm=0.3,
            clevis_hole_d=4.25, rear_tab_t=8.0, rod_end_tab=(9.0, 6.0), tube=(12.0, 12.0),
            housing=(36.0, 20.0, 70.0), price_usd=90.0)


@lru_cache(None)
def p16_150() -> tuple[cq.Workplane, cq.Workplane] | None:
    """(body, rod) from Actuonix's STEP in the carousels' actuator frame, or None if the file isn't on disk."""
    shp = step_or_none(KEY_IN)
    if shp is None:
        return None
    body, rod = [], []
    for s in shp.Solids():
        (rod if s.BoundingBox().zmax > ROD_ZMIN else body).append(s.translate(cq.Vector(*SHIFT)))
    if len(rod) != 2:
        raise RuntimeError(f"unexpected solid split in {KEY_IN}: {len(rod)} rod solids")
    return (cq.Workplane("XY").add(cq.Compound.makeCompound(body)),
            cq.Workplane("XY").add(cq.Compound.makeCompound(rod)))


def p16_150_standin(clevis_d: float = 4.25, retracted: float = 197.4) -> tuple[cq.Workplane, cq.Workplane]:
    """The same envelope from the datasheet drawing, for when the STEP isn't on disk: 36 x 20 x 70 housing
    from z 4.5 (rod axis 10.5 mm from its +x end), rear tab 10 x 8 round the hole, 12 x 12 tube to z 192.4,
    dia 8.94 rod, rod end = 9 x 6 tab, hole 4 mm from its rounded tip."""
    housing = cq.Workplane("XY").box(36.0, 20.0, 70.0, centered=False).translate((-25.5, -10.0, 4.5))
    tab = (cq.Workplane("XZ").center(0, 0).circle(5.0).extrude(4.0, both=True)
           .union(cq.Workplane("XY").box(10.0, 8.0, 4.6, centered=(True, True, False))))
    tube = cq.Workplane("XY").box(12.0, 12.0, 169.0, centered=False).translate((-6.0, -6.0, 23.4))
    body = housing.union(tab).union(tube).cut(cq.Workplane("XZ").circle(clevis_d / 2).extrude(20, both=True))
    rod = cq.Workplane("XY").circle(4.47).extrude(165.0).translate((0, 0, retracted - 4.0 - 165.0))
    end = (cq.Workplane("XY").box(9.0, 6.0, 4.0, centered=(True, True, False)).translate((0, 0, retracted - 4.0))
           .union(cq.Workplane("XZ").center(0, retracted).circle(4.5).extrude(3.0, both=True)))
    end = end.intersect(cq.Workplane("XY").box(20, 20, 8.0, centered=(True, True, False)).translate((0, 0, retracted - 4.0)))
    rod = rod.union(end).cut(cq.Workplane("XZ").center(0, retracted).circle(clevis_d / 2).extrude(10, both=True))
    return body, rod
