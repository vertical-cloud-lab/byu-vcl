"""Fasteners for the renders: the parts the lab is actually using (2026-10-03).

- Steel: M3 x 10 and M4 x 18 stainless Phillips pan heads and their nuts, from the ME
  Prototyping Lab's drawer (see ../shopping-list.md). These are drawn from McMaster-Carr's STEP
  models of the same parts where we have them, and from ISO nominal sizes where not.
- Nylon: every M2.5 part is black nylon from the lab's COMRUN 350-piece M2.5 kit (Amazon
  B0CKBWQSNY; ../hardware/amazon/README.md): Phillips pan heads, hex nuts, and the 6 + 6 mm
  male-female standoffs the Pi 5 sits on (those are drawn in lid_mount.py). COMRUN publishes no
  CAD, so these are nominal shapes. The M4 washers are white nylon, McMaster 95610A550.

Every screw comes back in one pose: axis on Z, the underside of the head at Z = 0, the head
below it (Z < 0) and the shank running up +Z. Nuts and washers sit on Z = 0 and rise +Z.
Callers flip or translate them into place.

The McMaster files go in ../hardware/mcmaster/<part number>.step. They aren't committed;
../hardware/README.md says how to fetch them. If a file is missing, the ISO dimensions below
stand in for it, so the renders never depend on the download.
"""
from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq
import numpy as np

MCMASTER = Path(__file__).resolve().parent.parent / "hardware" / "mcmaster"

# The McMaster part standing in for each steel fastener in the build (18-8 stainless unless noted).
ROLES = {
    "m4_screw": "92000A227",    # M4 x 18 Phillips pan head: the drawer's M4 x 18 (phase 2)
    "m4_nut": "91828A231",      # M4 hex nut
    "m4_washer": "95610A550",   # nylon washer, 4.3 mm ID x 9 mm OD
    "m3_screw": "92000A120",    # M3 x 10 Phillips pan head: the drawer's M3 x 10
    "m3_nut": "91828A211",      # M3 hex nut, in the posts' side slots
}

# What each group in the build is, for captions and the parts list.
BUILD = {
    "m4_screws": "M4 x 18 Phillips pan head, stainless (lab drawer)",
    "m4_nuts": "M4 hex nut, stainless (lab drawer)",
    "m4_washers": "M4 nylon washer, 4.3 x 9 mm",
    "m3_screws": "M3 x 10 Phillips pan head, stainless (lab drawer)",
    "m3_nuts": "M3 hex nut, stainless (lab drawer)",
    "cam_screws": "M2.5 x 12 Phillips pan head, black nylon (COMRUN kit)",
    "cam_nuts": "M2.5 hex nut, black nylon (COMRUN kit)",
    "pi_screws": "M2.5 x 6 Phillips pan head, black nylon (COMRUN kit)",
    "pi_nuts": "M2.5 hex nut, black nylon (COMRUN kit)",
}
CAM_SCREW_LEN = 12.0    # the kit's longest M2.5; just reaches through the nut (fastener_fit.py)
PI_SCREW_LEN = 6.0      # through the 1.6 mm board, 4.4 mm into the standoff
STEEL = (0.74, 0.75, 0.78)
NYLON = (0.96, 0.95, 0.90)          # the white M4 washers
BLACK_NYLON = (0.20, 0.20, 0.22)    # the COMRUN kit


def color(group: str) -> tuple[float, float, float]:
    if group == "m4_washers":
        return NYLON
    return BLACK_NYLON if "black nylon" in BUILD.get(group, "") else STEEL

# Nominal ISO dimensions (mm): head diameter, head height, hex socket, nut across flats / height.
ISO7380 = {"M4": (7.6, 2.2, 2.5), "M3": (5.7, 1.65, 2.0), "M2.5": (4.7, 1.5, 1.5)}   # button head
ISO4762 = {"M4": (7.0, 4.0, 3.0), "M3": (5.5, 3.0, 2.5), "M2.5": (4.5, 2.5, 2.0)}   # socket head cap
ISO4032 = {"M4": (7.0, 3.2), "M3": (5.5, 2.4), "M2.5": (5.0, 2.0)}                  # hex nut
ISO7045 = {"M4": (8.0, 3.1), "M3": (5.6, 2.4), "M2.5": (5.0, 2.1)}                  # Phillips pan head
MAJOR = {"M4": 4.0, "M3": 3.0, "M2.5": 2.5}


def _hex_socket(af: float, depth: float) -> cq.Workplane:
    return cq.Workplane("XY").polygon(6, af / math.cos(math.pi / 6)).extrude(depth)


def button_head(size: str, length: float) -> cq.Workplane:
    dk, k, s = ISO7380[size]
    head = (cq.Workplane("XY").circle(dk / 2).extrude(k).translate((0, 0, -k))
            .faces("<Z").edges().fillet(k * 0.6))
    head = head.cut(_hex_socket(s, k * 0.6).translate((0, 0, -k - 0.01)))
    shank = cq.Workplane("XY").circle(MAJOR[size] / 2).extrude(length)
    return head.union(shank)


def socket_head(size: str, length: float) -> cq.Workplane:
    dk, k, s = ISO4762[size]
    head = cq.Workplane("XY").circle(dk / 2).extrude(k).translate((0, 0, -k)).faces("<Z").chamfer(0.3)
    head = head.cut(_hex_socket(s, k * 0.6).translate((0, 0, -k - 0.01)))
    shank = cq.Workplane("XY").circle(MAJOR[size] / 2).extrude(length)
    return head.union(shank)


def pan_head(size: str, length: float) -> cq.Workplane:
    """Phillips pan head (ISO 7045): a rounded cylinder with a cross recess."""
    dk, k = ISO7045[size]
    head = (cq.Workplane("XY").circle(dk / 2).extrude(k).translate((0, 0, -k))
            .faces("<Z").edges().fillet(k * 0.45))
    w, depth = dk * 0.13, k * 0.55
    for ang in (0, 90):
        slot = cq.Workplane("XY").box(dk * 0.55, w, depth + 0.01, centered=(True, True, False))
        head = head.cut(slot.rotate((0, 0, 0), (0, 0, 1), ang).translate((0, 0, -k - 0.01)))
    shank = cq.Workplane("XY").circle(MAJOR[size] / 2).extrude(length)
    return head.union(shank)


def hex_nut(size: str) -> cq.Workplane:
    af, m = ISO4032[size]
    nut = cq.Workplane("XY").polygon(6, af / math.cos(math.pi / 6)).extrude(m)
    return nut.cut(cq.Workplane("XY").circle(MAJOR[size] * 0.42).extrude(m + 1).translate((0, 0, -0.5)))


def washer(od: float, id_: float, t: float) -> cq.Workplane:
    return cq.Workplane("XY").circle(od / 2).circle(id_ / 2).extrude(t)


def _verts(shape: cq.Workplane) -> np.ndarray:
    """Tessellated vertices: tight bounds, unlike the B-spline control box that BoundingBox() uses."""
    verts, _ = shape.val().tessellate(0.02, 0.2)
    return np.array([(v.x, v.y, v.z) for v in verts])


def _normalise(shape: cq.Workplane, kind: str, major: float = 0.0) -> cq.Workplane:
    """Rotate a vendor model into the pose described in the module docstring."""
    v = _verts(shape)
    ext = v.max(axis=0) - v.min(axis=0)
    # Screws: the long axis is the screw axis. Nuts and washers: the short one is.
    axis = int(np.argmax(ext)) if kind == "screw" else int(np.argmin(ext))
    if axis == 0:
        shape = shape.rotate((0, 0, 0), (0, 1, 0), 90)
    elif axis == 1:
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 90)
    v = _verts(shape)
    # Centre on the axis: the middle of the widest end (the head, or the whole nut).
    lo, hi = v[:, 2].min(), v[:, 2].max()
    end_lo, end_hi = v[v[:, 2] < lo + 0.3], v[v[:, 2] > hi - 0.3]
    def spread(e):
        return (e[:, :2].max(axis=0) - e[:, :2].min(axis=0)).max()
    head = end_lo if spread(end_lo) >= spread(end_hi) else end_hi
    c = (head[:, :2].max(axis=0) + head[:, :2].min(axis=0)) / 2
    shape = shape.translate((-c[0], -c[1], -lo))
    if kind != "screw":
        return shape
    if head is end_hi:   # head on top: turn it over so it sits at the bottom
        zc = (hi - lo) / 2
        shape = shape.rotate((0, 0, zc), (1, 0, zc), 180)
    v = _verts(shape)
    # The underside of the head is the highest point that still lies outside the thread.
    r = np.hypot(v[:, 0], v[:, 1])
    underside = v[r > major / 2 + 0.4, 2].max()
    return shape.translate((0, 0, -underside))


def mcmaster(pn: str, kind: str, major: float = 0.0) -> cq.Workplane | None:
    path = MCMASTER / f"{pn}.step"
    if not path.exists():
        return None
    return _normalise(cq.importers.importStep(str(path)), kind, major)


def fasteners() -> dict[str, tuple[cq.Workplane, str]]:
    """Each fastener in the build, as (shape, where it came from)."""
    def pick(role: str, kind: str, fallback, major: float = 0.0):
        pn = ROLES.get(role)
        shape = mcmaster(pn, kind, major) if pn else None
        if shape is not None:
            return shape, f"McMaster-Carr {pn}"
        return fallback, "ISO nominal (no McMaster file)"

    kit = "nominal sizes (COMRUN publishes no CAD)"
    return {
        "m4_screw": pick("m4_screw", "screw", pan_head("M4", 18), MAJOR["M4"]),
        "m4_nut": pick("m4_nut", "nut", hex_nut("M4")),
        "m4_washer": pick("m4_washer", "nut", washer(9.0, 4.3, 0.8)),
        "m3_screw": pick("m3_screw", "screw", pan_head("M3", 10), MAJOR["M3"]),
        "m3_nut": pick("m3_nut", "nut", hex_nut("M3")),
        "m25_cam_screw": (pan_head("M2.5", CAM_SCREW_LEN), kit),
        "m25_pi_screw": (pan_head("M2.5", PI_SCREW_LEN), kit),
        "m25_nut": (hex_nut("M2.5"), kit),
    }


def _place(shape, xys, z, flip=False):
    """Copies of a screw or nut at each (x, y); `flip` points a screw's shank down."""
    s = shape.rotate((0, 0, 0), (1, 0, 0), 180) if flip else shape
    return [s.translate((x, y, z)) for x, y in xys]


def placed(p) -> tuple[dict[str, list[cq.Workplane]], dict[str, str]]:
    """Every fastener in its assembled position (phase 2, bolted), and where each model came from."""
    from lid_mount import corners

    f = fasteners()
    z_top_deck = p.z_deck + p.deck_t
    z_cam_front = p.z_pcb_back - p.cam_pcb_t
    z_pi_top = z_top_deck + p.pi_standoff_h + 1.6
    washer_t = f["m4_washer"][0].val().BoundingBox().zlen
    m3_nut_h = f["m3_nut"][0].val().BoundingBox().zlen
    shapes = {
        # Base: M4 nuts at the bottom of their traps; pan heads + washers from inside the robot.
        "m4_nuts": _place(f["m4_nut"][0], corners(p.bolt_xy), p.base_t - p.m4_nut_h),
        "m4_screws": _place(f["m4_screw"][0], corners(p.bolt_xy), -p.lid_thickness - washer_t),
        "m4_washers": _place(f["m4_washer"][0], corners(p.bolt_xy), -p.lid_thickness - washer_t),
        # Camera: M2.5 up through the PCB and bosses, nuts in the deck's top traps.
        "cam_screws": _place(f["m25_cam_screw"][0], corners(p.cam_hole_pitch / 2), z_cam_front),
        "cam_nuts": _place(f["m25_nut"][0], corners(p.cam_hole_pitch / 2), z_top_deck - p.m25_nut_h),
        # Deck to posts: M3 down through the deck into nuts in the posts' side slots, which the
        # screws pull up against the slot roofs.
        "m3_screws": _place(f["m3_screw"][0], corners(p.post_c), z_top_deck, flip=True),
        "m3_nuts": _place(f["m3_nut"][0], corners(p.post_c), p.z_m3_slot + p.m3_nut_slot_h - m3_nut_h),
        # Pi 5: M2.5 down through the board into the standoffs (lid_mount.place_pi_standoffs),
        # whose studs go through the deck into nuts pulled up against the roofs of its underside traps.
        "pi_screws": _place(f["m25_pi_screw"][0], p.pi_holes(), z_pi_top, flip=True),
        "pi_nuts": _place(f["m25_nut"][0], p.pi_holes(), p.z_deck + p.m25_nut_h - ISO4032["M2.5"][1]),
    }
    return shapes, {k: v[1] for k, v in f.items()}
