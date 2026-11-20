"""Security cameras instead of the Pi HQ/Wide stream-camera units (#303, PR #318 follow-up): candidates, where each
would go, what it sees in the bay, whether it fits, what it draws and what it costs.

    python3 security_cams.py           # out/security_cameras.json and the two figures below (matplotlib, a few seconds)
    python3 security_cams.py arm       # the same, plus the UR10e's clearance to every bay spot (reach.py's 320 poses,
                                       # about 30 s per spot; services.bay_arm_clearance's method, our points)

Figures: out/security_cameras_bay.png (the bay in section and what each bay camera sees of the presented tray) and
out/security_cameras_fit.png (each candidate to scale against the bay's roof band and the trays' slot headroom).

Sterling (PR #318, 2026-11-20): "Considering a swap to mostly or all security cameras ... with a Pi 5 handling the
streaming and control (similar to borysgroup/aurora-cloud-infra PR 35 ...), and I also need an approximate cost".
notes/security_cameras.md is the write-up. Nothing here changes the Pi camera units in services.py or the animations.

Frames as in vlm.py: x to the right and y away from you facing the opening, z up from the floor, mm; Shuttle 1's bay.
Every figure with a source is in CANDIDATES / GEAR (each entry's `src`); estimates say so.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

import vlm as V

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

# ===================================================================================================== the bay
# The presented tray and the room over it (vlm.py). Sterling (PR #318, 2026-11-20): "In real kardex systems, I'm
# pretty sure there's a 'roof' to the bay". The model draws the bay open up to tray F1 (1950 mm); a roof is assumed
# here at the opening's clear height, the header's underside, where the bay's side walls and the LED light already
# stop. Kardex hasn't said where it is (open question 1 in the notes).
FLOOR_Z = V.Z_OPEN + V.T_FLOOR                                  # the presented tray's floor: 857
ENV_Z = FLOOR_Z + V.MAX_GOODS_H + V.GOODS_CLEAR                 # top of the goods envelope with Kardex's 20 mm: 1733.5
ROOF_Z = V.Z_OPEN_TOP                                           # the assumed roof's underside: 1829
BAND = ROOF_Z - ENV_Z                                           # what a ceiling camera may hang over the tray: 95.5
F1_Z = V.SLOTS["F1"][1]                                         # tray F1's underside, stored over the opening: 1950
TRAY_X = V.TRAY_W / 2                                           # 1225
TRAY_Y = (V.Y_OPEN - V.TRAY_D / 2, V.Y_OPEN + V.TRAY_D / 2)     # the presented tray front to back: -1462, -598
Y_PANEL = -V.UNIT_D / 2 - V.SKIN                                # the front panel's outer face: -1562
HEADER_Y = (Y_PANEL - 20.0, Y_PANEL + 40.0)                     # the header band: -1582 .. -1522 (vlm.opening)
LED_Y = (Y_PANEL - 10.0, Y_PANEL + 160.0)                       # the LED light under it: -1572 .. -1402, 12 mm deep
SHUTTER_Y = V.Y_SHUTTER - 6.0                                   # the shutter's front face: -569; it slides up there
SIDE_X = V.OPEN_W / 2                                           # the bay's side walls: +-1250
WORK_DZ = 300.0                                                 # a second plane for coverage: 300 mm over the floor
# The goods only ever pass under y >= TRAY_Y[0]: a tray slides in from the shaft and stops with its front edge at
# -1462, so the strip from there to the header is never swept by anything on a tray. A camera hung there is limited by
# the arm and the operator, not by Kardex's product height. Everywhere else over the tray it must stay inside BAND.
FRONT_STRIP = (LED_Y[0], TRAY_Y[0])                             # -1572 .. -1462: 110 mm deep


def basis(yaw: float, tilt: float):
    """Camera axes, world: forward, right, up. yaw: heading in degrees from +y towards +x (0 looks at the shutter, 180
    out through the opening); tilt: degrees below level."""
    a, t = math.radians(yaw), math.radians(tilt)
    f = np.array([math.sin(a) * math.cos(t), math.cos(a) * math.cos(t), -math.sin(t)])
    r = np.array([math.cos(a), -math.sin(a), 0.0])
    u = np.cross(r, f)
    return f, r, u


def aim(c, target) -> tuple:
    """(yaw, tilt) that point a camera at c onto target."""
    d = np.asarray(target, float) - np.asarray(c, float)
    return math.degrees(math.atan2(d[0], d[1])), math.degrees(math.atan2(-d[2], math.hypot(d[0], d[1])))


def in_view(P, c, yaw, tilt, hfov, vfov) -> np.ndarray:
    """Which points P (n, 3) a rectilinear camera at c with the given full angles sees (no occlusion)."""
    f, r, u = basis(yaw, tilt)
    v = np.asarray(P, float) - np.asarray(c, float)
    zc = v @ f
    with np.errstate(divide="ignore", invalid="ignore"):
        ok = (zc > 1.0) & (np.abs(v @ r) <= zc * math.tan(math.radians(hfov) / 2)) & \
             (np.abs(v @ u) <= zc * math.tan(math.radians(vfov) / 2))
    return ok


def tray_grid(dz=0.0, step=25.0) -> np.ndarray:
    xs = np.arange(-TRAY_X + step / 2, TRAY_X, step)
    ys = np.arange(TRAY_Y[0] + step / 2, TRAY_Y[1], step)
    X, Y = np.meshgrid(xs, ys)
    return np.c_[X.ravel(), Y.ravel(), np.full(X.size, FLOOR_Z + dz)]


def coverage(c, yaw, tilt, hfov, vfov, dz=0.0) -> float:
    """Share of the presented tray's floor (or of the plane dz over it) inside the picture."""
    return float(in_view(tray_grid(dz), c, yaw, tilt, hfov, vfov).mean())


def footprint(c, yaw, tilt, hfov, vfov, z, n=48, far=6000.0) -> np.ndarray:
    """The picture's outline where it meets the plane z, (m, 2): the image border cast as rays; rays that don't come
    down to z within `far` stop there (so the outline stays finite)."""
    f, r, u = basis(yaw, tilt)
    th, tv = math.tan(math.radians(hfov) / 2), math.tan(math.radians(vfov) / 2)
    s = np.linspace(-1, 1, n)
    border = [(a, -1) for a in s] + [(1, b) for b in s] + [(a, 1) for a in s[::-1]] + [(-1, b) for b in s[::-1]]
    pts = []
    for a, b in border:
        d = f + a * th * r + b * tv * u
        d /= np.linalg.norm(d)
        t = (z - c[2]) / d[2] if d[2] < -1e-9 else far
        t = min(t, far)
        pts.append(np.asarray(c)[:2] + t * d[:2])
    return np.array(pts)


def mm_per_px(c, target, hfov, width_px) -> float:
    """Across the picture, at the target, with the camera aimed at it."""
    d = float(np.linalg.norm(np.asarray(target, float) - np.asarray(c, float)))
    return 2.0 * d * math.tan(math.radians(hfov) / 2) / width_px


def cyl_points(c, dia, h, n=24, rings=4) -> np.ndarray:
    """Points on a vertical cylinder hanging from c (its top centre), for the arm check and the band check."""
    out = []
    for z in np.linspace(0.0, -h, rings):
        for a in np.linspace(0, 2 * math.pi, n, endpoint=False):
            out.append((c[0] + dia / 2 * math.cos(a), c[1] + dia / 2 * math.sin(a), c[2] + z))
    out.append((c[0], c[1], c[2] - h))
    return np.array(out)


def arm_clearance(points: np.ndarray) -> dict:
    """services.bay_arm_clearance (reach.py's 320 poses: the workflow's seats and the presented tray on a 100 mm grid,
    gripper down, 100 and 250 mm over its floor; the UR10e as 75 mm capsules from the shoulder to the TCP) against
    our points instead of the HQ/Wide bay unit's."""
    import services as S
    keep = S.bay_points
    S.bay_points = lambda: np.asarray(points, float)
    try:
        return S.bay_arm_clearance()
    finally:
        S.bay_points = keep


def room_share(c, yaw, tilt, hfov, vfov, n=61) -> float:
    """Share of the picture that looks out through the opening into the room (people, faces) rather than at the tray
    or the bay: a ray counts if it reaches the front panel's plane inside the opening before it meets the tray's floor
    or the roof. As services.unit_view, nothing else counts as cover."""
    f, r, u = basis(yaw, tilt)
    th, tv = math.tan(math.radians(hfov) / 2), math.tan(math.radians(vfov) / 2)
    hits = 0
    for a in np.linspace(-1, 1, n):
        for b in np.linspace(-1, 1, n):
            d = f + a * th * r + b * tv * u
            t_panel = (Y_PANEL - c[1]) / d[1] if d[1] < -1e-9 else math.inf
            t_floor = (FLOOR_Z - c[2]) / d[2] if d[2] < -1e-9 else math.inf
            t_roof = (ROOF_Z - c[2]) / d[2] if d[2] > 1e-9 else math.inf
            if t_panel < min(t_floor, t_roof):
                p = np.asarray(c) + t_panel * d
                if abs(p[0]) <= SIDE_X and V.Z_SILL <= p[2] <= ROOF_Z:
                    hits += 1
    return hits / n ** 2


def best_aim(c, hfov, vfov, yaws, tilts, room_max=None) -> tuple:
    """(yaw, tilt, floor coverage, coverage 300 mm up, room share): the aim that sees the most of the tray's floor
    (then the most of the plane 300 mm over it), seeing at most room_max of the room."""
    best = None
    for yaw in yaws:
        for tilt in tilts:
            cov = coverage(c, yaw, tilt, hfov, vfov)
            room = room_share(c, yaw, tilt, hfov, vfov, n=31)
            if room_max is not None and room > room_max:
                continue
            key = (round(cov, 3), coverage(c, yaw, tilt, hfov, vfov, dz=WORK_DZ), -room)
            if best is None or key > best[0]:
                best = (key, yaw, tilt, room)
    (cov, cov2, _), yaw, tilt, room = best
    return yaw, tilt, cov, cov2, room


# ===================================================================================================== the spots
# The bay, per Shuttle. Sterling (PR #318, 2026-11-20): "maybe we could have two side-by-side, one focused on wide
# capture and another that could point closely at whatever workflow is happening ... We can also have multiple overhead
# cameras in the bay to get different angles (e.g., ceiling middle back, ceiling middle front)".
# * The pair goes in the front strip, under the header, where nothing on a tray ever passes (FRONT_STRIP), so the PTZ
#   may hang lower than the 95.5 mm band. Off-centre to the right: in the middle of the strip a 180 mm PTZ comes
#   within 17 mm of the UR10e's capsules (x 0) or 31 mm (x 170) when the arm reaches the tray's front half with its
#   elbow up at 1.56-1.57 m; at x 450 / 650 the gaps are 171 / 137 mm (arm_clearance, out/security_cameras.json).
# * The middle back camera hangs from the roof 70 mm in front of the shutter's path, over the tray's back strip, so it
#   must stay inside the band; it looks forward and down, as the HQ/Wide bay unit does now.
# * The top-down camera hangs from the roof over the tray's centre: one wide picture of the whole floor, square to it
#   (inventory, and a plain homography for registering a tray's layout).
BAY_SPOTS = {     # key: (label, mount point on the roof (x, y, z), how it is placed)
    "front_wide": ("front pair: wide", (450.0, -1517.0, ROOF_Z), "under the header, in the front strip"),
    "front_ptz": ("front pair: PTZ", (650.0, -1517.0, ROOF_Z), "under the header, in the front strip"),
    "back": ("ceiling, middle back", (0.0, -645.0, ROOF_Z), "on the roof, 76 mm in front of the shutter's face"),
    "top": ("ceiling, middle, straight down", (0.0, -1030.0, ROOF_Z), "on the roof over the tray's centre"),
}
SEATS = {        # reach.seats(), world (Shuttle 1's bay): where the arm works in the workflow; the PTZ's close-ups
    "vial rack (tray B)": (-165.0, -1402.0, 915.0),
    "doser shuttle fork (tray B)": (183.0, -1250.0, 1132.0),
    "CubXL holder seat (tray A)": (-156.0, -1342.0, 987.0),
    "tray's back left, 150 mm up": (-1000.0, -700.0, FLOOR_Z + 150.0),
}


def tray_spots() -> list:
    """Every tray camera as drawn in PR #318 (services.TRAY_CAMS for trays A-F, setup_lab.CAMS for G-M): (tray, unit,
    pivot (x, y, z) in the tray's frame, aim point, distance pivot -> aim). The pivot is the HQ/Wide head's tilt axis
    (its post's offset of 67-80 mm ignored)."""
    import services as S
    import setup_lab as SL
    out = []
    lay = {k: (v, S.CAM_H) for k, v in S.TRAY_CAMS.items()}
    lay.update({k: (v[0], v[1] if v[1] is not None else S.CAM_H) for k, v in SL.CAMS.items()})
    for tray, (units, h) in lay.items():
        for i, (x, y, ax, ay, az, *_) in enumerate(units):
            piv = (x, y, V.T_FLOOR + h + S.TILT_AXIS[2])
            d = float(np.linalg.norm(np.subtract((ax, ay, az), piv)))
            out.append(dict(tray=tray, unit=f"{tray}{i}", pivot=piv, aim=(ax, ay, az), dist_mm=round(d)))
    return out


def tray_headroom() -> dict:
    """Per tray, from setup_lab.py fit (out/tray_plan.json): the slot, the tallest thing that isn't a camera, the
    camera heads' tops, the highest top that keeps the slot as it is (span - 20 mm), and the slot the tray would need
    with no camera above its tallest instrument."""
    d = json.loads((OUT / "tray_plan.json").read_text())
    out = {}
    for k, r in d["trays"].items():
        non = [it for it in r["items"] if not it["item"].startswith("cam_")]
        heads = [it["box_mm"][5] for it in r["items"] if it["item"].startswith("cam_") and "head" in it["item"]]
        if not heads:
            continue
        tall = max(non, key=lambda it: it["box_mm"][5])
        top_ok = r["span_mm"] - V.GOODS_CLEAR
        need = lambda top: V.PITCH * math.ceil((top + V.GOODS_CLEAR) / V.PITCH - 1e-9)
        out[k] = dict(slot=r["slot"], span_mm=r["span_mm"], tallest_other=tall["item"],
                      tallest_other_mm=round(tall["box_mm"][5], 1), camera_tops_mm=[round(h, 1) for h in heads],
                      cameras_set_the_slot=max(heads) > tall["box_mm"][5], highest_top_same_slot_mm=top_ok,
                      span_if_cameras_below_mm=need(tall["box_mm"][5]))
    return out
