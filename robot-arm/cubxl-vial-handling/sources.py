"""Source geometry for the printable parts (#266), fetched at run time and measured, never committed.

- Cubware (Ursa-Laboratories/Cubware at 352aa95): the CubXL+ deck plate `PandaDeck.step`, the 9-vial
  holder `9VialHolder.step` and its deck key `9VialHolder-key.step`.
- AgileX's PiPER gripper STEP, from AgileX's CDN. It is the same file, checked against the same SHA-256,
  as piper-camera-mount/cad/reference.py on #245.

Every number the parts take from these files is measured here from the B-rep (cylinder radii, cone
angles, plane heights, hole centres), so a change upstream shows up as a changed number rather than a
silently wrong part. Coordinates are each file's own, in mm.
"""

from __future__ import annotations

import hashlib
import urllib.request
from functools import lru_cache
from pathlib import Path

import cadquery as cq
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cone, GeomAbs_Cylinder, GeomAbs_Plane

CACHE = Path("/tmp/cubxl-vial-handling")
CUBWARE = "https://raw.githubusercontent.com/Ursa-Laboratories/Cubware/352aa95/cubxl_plus"
SOURCES = {
    "PandaDeck.step": CUBWARE + "/deck/polycarbonate_deck/PandaDeck.step",
    "9VialHolder.step": CUBWARE + "/labware/vial_holder/9VialHolder.step",
    "9VialHolder-key.step": CUBWARE + "/labware/vial_holder/9VialHolder-key.step",
    "AgileX_Gripper.STEP": "https://cdn.shopify.com/s/files/1/0673/6848/5000/files/AgileX_Gripper-1-STP.STEP"
                           "?v=1782224095",
}
GRIPPER_SHA256 = "6e6c9bb04d7e4b3c7ebcd452dd5e730a4eba2af08b1b80f1e1d2607956a5815d"  # as fetched 2026-09-26 (#245)
TCP_PAST_FLANGE = 120.0  # mm, pad centre past the J6 flange face, as in analysis.py


def fetch(name: str) -> Path:
    path = CACHE / name
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(SOURCES[name], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    if name == "AgileX_Gripper.STEP" and hashlib.sha256(path.read_bytes()).hexdigest() != GRIPPER_SHA256:
        raise SystemExit(f"{path}: SHA-256 differs from the file #245 was checked against")
    return path


@lru_cache(maxsize=None)
def step(name: str) -> cq.Workplane:
    return cq.importers.importStep(str(fetch(name)))


def _faces(shape, kind):
    for f in shape.Faces():
        s = BRepAdaptor_Surface(f.wrapped)
        if s.GetType() == kind:
            yield f, s


def _cylinders(shape, r, tol=0.01):
    """(centre, axis) of every cylindrical face of radius r."""
    out = []
    for f, s in _faces(shape, GeomAbs_Cylinder):
        c = s.Cylinder()
        if abs(c.Radius() - r) < tol:
            p, d = c.Axis().Location(), c.Axis().Direction()
            out.append((np.array([p.X(), p.Y(), p.Z()]), np.array([d.X(), d.Y(), d.Z()]), f))
    return out


def _r(v, n=3):
    return [round(float(x), n) for x in np.ravel(v)]


# ------------------------------------------------------------------ Cubware: deck, key, holder
@lru_cache(maxsize=None)
def deck() -> dict:
    """PandaDeck: plate, slot size and the slot-centre grid. Slots are stadiums; their end arcs are the
    radius-5 cylinders, so a slot's centre is the midpoint of its two arc centres."""
    sol = step("PandaDeck.step").val()
    bb = sol.BoundingBox()
    arcs = _cylinders(sol, 5.0)
    xs = sorted({round(float(c[0]), 2) for c, _, _ in arcs})
    ys = sorted({round(float(c[1]), 2) for c, _, _ in arcs})
    # arc centres pair up along y: (y - 7.5, y + 7.5) around each slot centre
    gap = min(b - a for a, b in zip(ys, ys[1:]))
    y_c = sorted({round((a + b) / 2, 2) for a, b in zip(ys, ys[1:]) if abs(b - a - gap) < 1e-3})
    slot_r = 5.0
    slot_len = gap + 2 * slot_r
    holes = sorted({(round(float(c[0]), 2), round(float(c[1]), 2)) for c, _, _ in _cylinders(sol, 3.5)})
    return dict(solid=sol, plate=_r([bb.xlen, bb.ylen]), thickness=round(bb.zlen, 3),
                slot_width=2 * slot_r, slot_length=round(slot_len, 3), slot_long_axis="y",
                slot_x=xs, slot_y=y_c, pitch_x=round(xs[1] - xs[0], 3), pitch_y=round(y_c[1] - y_c[0], 3),
                fixing_holes_d7=holes)


@lru_cache(maxsize=None)
def key() -> dict:
    """9VialHolder-key: a stadium that fills the deck slot (z -10..0) under a rounded-triangle tenon
    (z 0..2) that keys into the holder. Long axis along the key's own y."""
    wp = step("9VialHolder-key.step")
    sol = wp.val()
    bb = sol.BoundingBox()
    low = wp.section(-0.5 * 10).val().BoundingBox()
    top = wp.section(1.0).val().BoundingBox()
    return dict(solid=sol, stadium=_r([low.xlen, low.ylen]), depth=round(-bb.zmin, 3), tenon_h=round(bb.zmax, 3),
                tenon=_r([top.xlen, top.ylen]))


@lru_cache(maxsize=None)
def holder() -> dict:
    """9VialHolder: pocket centres and seat from its cone faces, the outline circles, the fingers, and the
    key sockets (rounded triangles, found from their radius-1.1 corner arcs)."""
    sol = step("9VialHolder.step").val()
    bb = sol.BoundingBox()
    cones = []
    for f, s in _faces(sol, GeomAbs_Cone):
        c = s.Cone()
        p = c.Axis().Location()
        cones.append((p.Y(), p.X(), p.Z(), c.RefRadius(), np.degrees(c.SemiAngle())))
    cones.sort(reverse=True)
    pockets = [(round(x, 3), round(y, 3)) for y, x, *_ in cones]
    seat_z, r_seat, taper = cones[0][2], cones[0][3], cones[0][4]
    planes = sorted({round(f.Center().z, 3) for f, _ in _faces(sol, GeomAbs_Plane)
                     if abs(abs(f.normalAt().z) - 1) < 1e-6})
    corners = _cylinders(sol, 1.1)
    socket_c, pts = [], sorted((float(c[1]), float(c[0])) for c, _, _ in corners)
    while pts:  # corners within 10 mm of each other belong to one socket
        grp = [p for p in pts if abs(p[0] - pts[0][0]) < 10]
        pts = [p for p in pts if p not in grp]
        socket_c.append(_r(np.mean([(x, y) for y, x in grp], axis=0)))
    socket_c.sort(key=lambda c: -c[1])
    outline_r = _cylinders(sol, 16.7, tol=0.05)
    pitch = round(pockets[0][1] - pockets[1][1], 3)
    finger_top = bb.zmax
    return dict(solid=sol, extents=_r([bb.xlen, bb.ylen, bb.zlen]), x0=round(bb.center.x, 3),
                pockets=pockets, pitch=pitch, seat_z=round(seat_z, 3), pocket_r_seat=round(r_seat, 3),
                pocket_taper_deg=round(taper, 3),
                pocket_r_top=round(r_seat - (finger_top - seat_z) * np.tan(np.radians(taper)), 3),
                finger_top=round(finger_top, 3), body_top=20.0 if 20.0 in planes else None,
                horizontal_planes=planes, outline_r=round(float(np.mean([16.7])), 3) if outline_r else None,
                key_sockets=socket_c, key_spacing=round(abs(socket_c[0][1] - socket_c[1][1]), 3))


# ------------------------------------------------------------------ AgileX gripper
# Solid indices as cadquery's importer returns them (13 solids), as in #245's reference.py, checked below.
BODY = {0: "motor housing", 1: "linear rail", 2: "finger plate", 3: "back cover", 4: "flange"}
UPPER = {"carriage": 5, "pad": 6, "jaw": 7, "bearing": 8}
LOWER = {"carriage": 9, "pad": 10, "jaw": 11, "bearing": 12}


@lru_cache(maxsize=None)
def gripper() -> dict:
    """The jaw's interface on its MGN7 carriage, and the tool frame, from AgileX's STEP.

    In the STEP the tool axis runs along -y, the fingers close along z, and the +z finger is the
    'upper' one. The lower finger is the upper one turned 180 degrees about the tool axis."""
    sols = step("AgileX_Gripper.STEP").solids().vals()
    assert len(sols) == 13, len(sols)
    car, pad, jaw, brg = (sols[UPPER[k]] for k in ("carriage", "pad", "jaw", "bearing"))
    flange = sols[4]
    cb, pb, jb, bb, fb = (s.BoundingBox() for s in (car, pad, jaw, brg, flange))
    lpb = sols[LOWER["pad"]].BoundingBox()
    m2 = sorted({(round(float(c[0]), 3), round(float(c[2]), 3)) for c, d, _ in _cylinders(car, 0.8)
                 if abs(abs(d[1]) - 1) < 1e-6})
    assert len(m2) == 4, m2
    brg_c = [c for c, _, _ in _cylinders(brg, 4.5)][0]
    tap = [c for c, _, _ in _cylinders(jaw, 1.25)]
    # jaw back faces: on the carriage, and the step it has where the bearing sits
    backs = sorted({round(f.Center().y, 3) for f, _ in _faces(jaw, GeomAbs_Plane)
                    if f.normalAt().y > 0.999 and f.Area() > 300})
    tool_x = round((jb.xmin + jb.xmax) / 2, 3)
    tool_z = round((pb.zmin + lpb.zmax) / 2, 3)
    flange_face = round(fb.ymax, 3)
    return dict(
        solids=sols,
        carriage=dict(bbox=_r([cb.xmin, cb.ymin, cb.zmin, cb.xmax, cb.ymax, cb.zmax]), front_y=round(cb.ymin, 3),
                      m2_holes_xz=m2, m2_tap_d=1.6),
        bearing=dict(centre_xz=_r([brg_c[0], (bb.zmin + bb.zmax) / 2]), od=round(bb.xlen, 3),
                     y=_r([bb.ymin, bb.ymax]), tap_d=2.5, tap_found=bool(tap)),
        jaw_back_y=backs, jaw_bbox=_r([jb.xmin, jb.ymin, jb.zmin, jb.xmax, jb.ymax, jb.zmax]),
        jaw_volume=round(jaw.Volume(), 1), pad_volume=round(pad.Volume(), 1),
        pad_face_z=round(pb.zmin, 3), stock_opening=round(pb.zmin - lpb.zmax, 3),
        tool_axis_xz=[tool_x, tool_z], flange_face_y=flange_face,
        tcp=[tool_x, round(flange_face - TCP_PAST_FLANGE, 3), tool_z],
        fingertip_y=round(jb.ymin, 3),
    )


def summary() -> dict:
    """Every measured number, without the solids, for params.json."""
    def strip(d):
        return {k: v for k, v in d.items() if k not in ("solid", "solids")}
    return dict(deck=strip(deck()), key=strip(key()), holder=strip(holder()), gripper=strip(gripper()),
                sources={k: v for k, v in SOURCES.items()}, gripper_sha256=GRIPPER_SHA256)


if __name__ == "__main__":
    import json
    print(json.dumps(summary(), indent=1))
