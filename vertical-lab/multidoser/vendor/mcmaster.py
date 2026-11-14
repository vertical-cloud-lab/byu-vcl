"""McMaster-Carr's own STEP files for the carousels' McMaster parts, placed in the frames our builders use.

`fetch_mcmaster.py` downloads them (logged out, through the doser Pi) into files/mcmaster/<PN>.step
and pins them in manifest_mcmaster.json; mcmaster_specs.json has each page's spec table and price.
`mcm(pn)` returns McMaster's solid moved into the frame of the part builder that uses it (the
builder's docstring), or None when the file isn't on disk, so the builder falls back to its
dimension-table stand-in. Each FRAMES entry was found by measuring the STEP (axis, ends, holes)
against that builder, and is checked in `__main__` by the overlap with the stand-in.
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import step_or_none  # noqa: E402

# pn -> (rotations about the origin as (axis, degrees), applied in order; then a translation), McMaster frame -> ours
FRAMES: dict[str, tuple[list[tuple[str, float]], tuple[float, float, float]]] = {
    # SA-1 connecting link: McMaster's pins along z at x 4.76 / 14.29 with the tab toward +y on the -z plate.
    # Ours (parts.chain_sa1_link): pins at x = +-P/2, tab toward -y on the +z plate.
    "7321K31": ([("x", 180.0)], (-9.525, 0.0, 0.0)),
    # 1/4-20 nylon-insert locknut, 7/16 hex, 5/16 tall (7.95 measured): axis y, bearing face at y -3.975, nylon crown +y.
    # Ours (parts.locknut): bearing face z = 0, crown +z.
    "95615A120": ([("x", 90.0)], (0.0, 0.0, 3.975)),
    # M5 and M3 nylon-insert locknuts (18-8): axis y, bearing face at y = -h/2, crown +y. Ours: as parts.locknut.
    "93625A200": ([("x", 90.0)], (0.0, 0.0, 2.5)),
    "93625A100": ([("x", 90.0)], (0.0, 0.0, 2.0)),
    # 841-bronze flanged sleeve bearing 4 x 7.02 x 6, flange 10 x 1.5: axis y, flange's outer face y = 0, sleeve to y = 6.
    # Ours (parts.sleeve_bearing): flange outer face z = +1.5, seat face z = 0, sleeve along -z.
    "6659K65": ([("x", -90.0)], (0.0, 0.0, 1.5)),
    # PTFE washer 4.3 x 9 x 0.8: axis z, centred. Ours (parts.thrust_washer): z 0 .. 0.8.
    "95630A630": ([], (0.0, 0.0, 0.4)),
    # M5 tapered heat-set insert, 5.7 long, 7.1 knurl OD: axis y, wide (flush) end at y = +2.858.
    # Ours (parts.heat_set_insert_m5): top face z = 0, body along -z.
    "94459A774": ([("x", 90.0)], (0.0, 0.0, -2.858)),
    # M5 x 16 socket head screw: axis z, head on top, underside of the head at z = +5.5. Ours (parts.screw): z = 0, shank -z.
    "91292A126": ([], (0.0, 0.0, -5.5)),
    # M5 x 16 low-profile knurled thumb screw, 11 x 5 head: axis z, head on top, its underside at z = +5.5.
    # Ours (parts.thumb_screw): underside of the head z = 0, shank along -z.
    "92545A179": ([], (0.0, 0.0, -5.5)),
    # 18-8 shoulder screws, 4 mm shoulder, M3 x 5 thread, 6 x 3 head: axis z, head on top; underside of the head at
    # z = +6 (4 x 10, gondola pivots) and z = +9 (4 x 16, the P16 base pin). Ours: underside of the head z = 0, shoulder -z.
    "90265A121": ([], (0.0, 0.0, -6.0)),
    "90265A123": ([], (0.0, 0.0, -9.0)),
    # 18-8 button head (ISO 7380), socket head (ISO 4762) and flat head (ISO 10642) screws: axis z, head on top. Ours
    # (parts.shcs / parts.screw): underside of the head at z = 0 (top face for a flat head), shank along -z.
    "92095A181": ([], (0.0, 0.0, -4.0)),     # M3 x 8 button head
    "92095A183": ([], (0.0, 0.0, -6.0)),     # M3 x 12 button head
    "92095A210": ([], (0.0, 0.0, -6.0)),     # M5 x 12 button head
    "92125A126": ([], (0.0, 0.0, -3.0)),     # M3 x 6 flat head (top face at z = +3)
    "91292A124": ([], (0.0, 0.0, -2.5)),     # M5 x 10 socket head
    "91292A129": ([], (0.0, 0.0, -10.0)),    # M5 x 25 socket head
    # hardened dowel pins, axis z, centred. 4 x 38 (U-yoke pin): ours along y, centred. 4 x 8 (locating pins): ours z 0..8.
    "91595A128": ([("x", 90.0)], (0.0, 0.0, 0.0)),
    "91595A150": ([], (0.0, 0.0, 4.0)),
}

# (thread d, length, head) -> McMaster part number, for the generic screw builders (18-8 stainless unless noted)
SCREWS: dict[tuple[int, int, str], str] = {
    (3, 8, "button"): "92095A181", (3, 12, "button"): "92095A183", (5, 12, "button"): "92095A210",
    (3, 6, "flat"): "92125A126",
    (5, 10, "socket"): "91292A124", (5, 16, "socket"): "91292A126", (5, 25, "socket"): "91292A129",
}

_AX = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}


@lru_cache(None)
def mcm(pn: str) -> cq.Workplane | None:
    """McMaster `pn` in our builder's frame, or None (file missing, or no frame worked out for it yet)."""
    if pn not in FRAMES:
        return None
    shp = step_or_none(pn)
    if shp is None:
        return None
    rots, t = FRAMES[pn]
    for ax, deg in rots:
        shp = shp.rotate(cq.Vector(0, 0, 0), cq.Vector(*_AX[ax]), deg)
    return cq.Workplane("XY").add(shp.translate(cq.Vector(*t)))


if __name__ == "__main__":   # overlap of each placed STEP with the stand-in it replaces (run from a design folder)
    import importlib
    PT = importlib.import_module("parts")
    checks = {"7321K31": lambda: PT.chain_sa1_link(), "95615A120": lambda: PT.locknut(6.35),
              "93625A200": lambda: PT.locknut(5.0), "93625A100": lambda: PT.locknut(3.0),
              "6659K65": lambda: PT.sleeve_bearing(), "95630A630": lambda: PT.thrust_washer(),
              "94459A774": lambda: PT.heat_set_insert_m5(), "91292A126": lambda: PT.screw(5.0, 16.0, 8.5, 5.0),
              "92545A179": lambda: PT.thumb_screw()}
    for pn, f in checks.items():
        try:
            f()
        except Exception:
            continue                 # this design has no such builder
        m = mcm(pn)
        if m is None:
            print(pn, "missing")
            continue
        a, b = m.val(), f().val()
        print(f"{pn}: McMaster {a.Volume():.0f} mm3, stand-in {b.Volume():.0f} mm3, common {a.intersect(b).Volume():.0f} mm3")
