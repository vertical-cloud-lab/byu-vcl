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


# ===================================================================================================== the figures
INK, INK2, MUTED, GRID, AXIS, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
BLUE, ORANGE, AQUA, CRIT = "#2a78d6", "#eb6834", "#1baf7a", "#d03b3b"     # dataviz reference palette; CRIT is status
ARM_FRONT = [(0, -1802, 981), (0, -1631, 1569), (-175, -1092, 1378), (-175, -1212, 1378), (-175, -1212, 1262),
             (-175, -1212, 1107)]   # reach.solve at tray B (-175, -182, 253): the pose that comes nearest the strip


def _lens(spot: str, cam: dict) -> tuple:
    """Where the lens is for a bay spot: under the mount by the camera's lens drop."""
    x, y, z = BAY_SPOTS[spot][1]
    return (x, y, z - cam["lens_drop_mm"])


def bay_analysis(choice: dict, cands: dict, arm: dict | None = None) -> dict:
    """Each bay spot with its chosen camera: aim, coverage of the tray's floor and of the plane 300 mm up, the share of
    the picture that is the room, the lowest point against the band (or the strip), mm per pixel; the PTZ at both ends
    of its zoom and at each workflow seat."""
    out = {}
    for spot, key in choice.items():
        cam = cands[key]
        c = _lens(spot, cam)
        hf, vf = cam["hfov"][0], cam["vfov"][0]
        if spot == "top":
            yaw, tilt = 0.0, 90.0
            cov, cov2, room = coverage(c, 0, 90, hf, vf), coverage(c, 0, 90, hf, vf, WORK_DZ), room_share(c, 0, 90, hf, vf)
        elif spot == "back":
            yaw, tilt, cov, cov2, room = best_aim(c, hf, vf, [180.0], np.arange(30.0, 76.0, 2.5))
        else:
            yaw, tilt, cov, cov2, room = best_aim(c, hf, vf, np.arange(-60.0, 1.0, 5.0) if c[0] > 0 else
                                                  np.arange(0.0, 61.0, 5.0), np.arange(40.0, 86.0, 2.5))
        low = BAY_SPOTS[spot][1][2] - cam["hang_mm"]
        in_strip = BAY_SPOTS[spot][1][1] + cam["dia_mm"] / 2 <= TRAY_Y[0]
        r = dict(camera=key, label=BAY_SPOTS[spot][0], mount=BAY_SPOTS[spot][1], lens=tuple(round(v, 1) for v in c),
                 yaw_deg=round(yaw, 1), tilt_deg=round(tilt, 1), floor_coverage=round(cov, 3),
                 coverage_300mm_up=round(cov2, 3), room_share=round(room, 3), lowest_point_mm=round(low, 1),
                 over_goods=not in_strip, band_margin_mm=round(low - ENV_Z, 1),
                 mm_per_px_at_tray_centre=round(mm_per_px(c, (0.0, V.Y_OPEN, FLOOR_Z), hf, cam["px"][0]), 2))
        if len(cam["hfov"]) > 1:
            r["tele"] = {}
            for name, t in SEATS.items():
                d = float(np.linalg.norm(np.subtract(t, c)))
                r["tele"][name] = dict(distance_mm=round(d), mm_per_px=round(mm_per_px(c, t, cam["hfov"][1],
                                                                                        cam["px"][0]), 3),
                                       picture_width_mm=round(2 * d * math.tan(math.radians(cam["hfov"][1]) / 2)),
                                       focus_ok=None if cam.get("min_focus_tele_mm") is None
                                       else d >= cam["min_focus_tele_mm"])
        if arm is not None and spot in arm:
            r["arm"] = arm[spot]
        out[spot] = r
    return out


def fig_bay(choice: dict, cands: dict, res: dict, path: Path) -> Path:
    """out/security_cameras_bay.png: the bay in section (x = 0) with the band, the strip and the cameras; then what
    each bay camera sees of the presented tray's floor, one small plan each."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon, Rectangle
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED,
                         "ytick.color": MUTED, "font.family": "DejaVu Sans"})
    fig = plt.figure(figsize=(16, 8.6), dpi=150, facecolor=SURF)
    gs = fig.add_gridspec(2, 3, width_ratios=[1.35, 1, 1], hspace=0.42, wspace=0.16, left=0.05, right=0.985,
                          top=0.87, bottom=0.07)
    ax = fig.add_subplot(gs[:, 0])
    ax.set_facecolor(SURF)
    y0, y1 = TRAY_Y
    # the tray, the goods envelope and Kardex's clearance, the band, the roof, header, LED light, shutter, tray F1
    ax.add_patch(Rectangle((Y_PANEL, V.Z_SILL - 20), SHUTTER_Y - Y_PANEL, 20, color=AXIS, lw=0))
    ax.add_patch(Rectangle((y0, FLOOR_Z - 3), y1 - y0, 3 + V.T_RIM, fill=False, ec=INK2, lw=1.0))
    ax.add_patch(Rectangle((y0, FLOOR_Z), y1 - y0, V.MAX_GOODS_H, color=GRID, lw=0, alpha=0.7))
    ax.add_patch(Rectangle((y0, FLOOR_Z + V.MAX_GOODS_H), y1 - y0, V.GOODS_CLEAR, fill=False, hatch="////",
                           ec=MUTED, lw=0))
    ax.add_patch(Rectangle((y0, ENV_Z), SHUTTER_Y - y0, BAND, color=BLUE, alpha=0.12, lw=0))
    ax.add_patch(Rectangle((FRONT_STRIP[0], V.Z_SILL), FRONT_STRIP[1] - FRONT_STRIP[0], ROOF_Z - V.Z_SILL,
                           color=AQUA, alpha=0.12, lw=0))
    ax.plot([HEADER_Y[0], SHUTTER_Y], [ROOF_Z, ROOF_Z], color=INK, lw=1.6)
    ax.add_patch(Rectangle((HEADER_Y[0], ROOF_Z), HEADER_Y[1] - HEADER_Y[0], V.HEADER_H, color=AXIS, lw=0))
    ax.add_patch(Rectangle((LED_Y[0], ROOF_Z - 12), LED_Y[1] - LED_Y[0], 12, color=MUTED, lw=0))
    ax.add_patch(Rectangle((SHUTTER_Y, V.Z_OPEN - 10), 12, ROOF_Z + 40 - V.Z_OPEN + 10, color=MUTED, lw=0))
    ax.add_patch(Rectangle((y0, F1_Z), y1 - y0, 80, fill=False, ec=MUTED, lw=1.0, ls="--"))
    ax.plot([Y_PANEL, Y_PANEL], [V.Z_SILL - 120, ROOF_Z], color=AXIS, lw=1.0, ls=":")
    # the arm at the pose that comes nearest the front strip, its links projected onto the section
    ys = [p[1] for p in ARM_FRONT]
    zs = [p[2] for p in ARM_FRONT]
    ax.plot(ys, zs, color=INK2, lw=5, alpha=0.35, solid_capstyle="round")
    ax.plot(ys, zs, "o", color=INK2, ms=4)
    # the cameras, to scale, numbered as in the plans, and the edges of each picture in its own vertical plane,
    # projected onto the section and stopped at the tray's floor
    for n, (spot, r) in enumerate(res.items(), 1):
        cam = cands[r["camera"]]
        x, y, z = r["mount"]
        col = ORANGE if len(cam["hfov"]) > 1 else BLUE
        ax.add_patch(Rectangle((y - cam["dia_mm"] / 2, z - cam["hang_mm"]), cam["dia_mm"], cam["hang_mm"],
                               color=col, lw=0, alpha=0.9))
        ly, lz = r["lens"][1], r["lens"][2]
        cy = math.cos(math.radians(r["yaw_deg"]))
        for dv in (-cam["vfov"][0] / 2, cam["vfov"][0] / 2):
            t = math.radians(r["tilt_deg"] + dv)
            dy, dz = cy * math.cos(t), -math.sin(t)
            s_ = (FLOOR_Z - lz) / dz if dz < -1e-6 else 3000.0
            ax.plot([ly, ly + s_ * dy], [lz, lz + s_ * dz], color=col, lw=0.7, alpha=0.6)
        ax.add_patch(Circle((y + cam["dia_mm"] / 2 + 38, z - cam["hang_mm"] / 2 - 10), 26, color=INK, lw=0))
        ax.text(y + cam["dia_mm"] / 2 + 38, z - cam["hang_mm"] / 2 - 10, str(n), color=SURF, ha="center",
                va="center", fontsize=8, fontweight="bold")
    ax.set_xlim(-1900, -480)
    ax.set_ylim(780, 2080)
    ax.set_aspect("equal")
    ax.grid(color=GRID, lw=0.5)
    ax.set_xlabel("y, mm (the opening on the left, the shutter on the right)")
    ax.set_ylabel("z over the floor, mm")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    txt = dict(fontsize=8, color=INK2)
    ax.text(-1040, 1300, f"goods envelope: up to {V.MAX_GOODS_H:.1f} mm\n(the 996 mm opening's estimate, vlm.py)",
            ha="center", **txt)
    ax.text(-1040, ENV_Z + BAND / 2, f"{BAND:.1f} mm: all a roof camera may hang over the tray", ha="center",
            va="center", fontsize=8, color=INK)
    ax.text(-1040, ROOF_Z + 22, "assumed roof: the opening's clear height, 1829 mm", ha="center", fontsize=8, color=INK)
    ax.text(-1040, F1_Z + 95, "tray F1, stored over the opening (1950 mm)", ha="center", **txt)
    ax.text(FRONT_STRIP[0] - 10, 1000, "front strip: no goods\never pass under it", ha="right", **txt)
    ax.text(-1631, 1600, "UR10e elbow at its\nhighest near the strip", ha="right", va="bottom", **txt)
    ax.text(SHUTTER_Y + 18, 1350, "shutter", rotation=90, va="center", **txt)
    ax.text(-1650, 1840, "header", ha="right", **txt)
    ax.set_title("The bay in section at x = 0 (the front pair is at x = 450 and 650 mm)", loc="left", fontsize=10,
                 color=INK)
    # one plan per camera: the presented tray's floor, the picture on it (filled) and 300 mm up (dashed)
    order = ["front_wide", "front_ptz", "back", "top"]
    num = {k: n for n, k in enumerate(res, 1)}
    for i, spot in enumerate(order):
        if spot not in res:
            continue
        r = res[spot]
        cam = cands[r["camera"]]
        a = fig.add_subplot(gs[i // 2, 1 + i % 2])
        a.set_facecolor(SURF)
        a.add_patch(Rectangle((-TRAY_X, y0), 2 * TRAY_X, y1 - y0, fill=False, ec=INK2, lw=1.0))
        clip = Rectangle((-TRAY_X, y0), 2 * TRAY_X, y1 - y0, transform=a.transData)
        c = r["lens"]
        fp = footprint(c, r["yaw_deg"], r["tilt_deg"], cam["hfov"][0], cam["vfov"][0], FLOOR_Z)
        p = a.add_patch(Polygon(fp, closed=True, color=BLUE, alpha=0.22, lw=0))
        p.set_clip_path(clip)
        fp2 = footprint(c, r["yaw_deg"], r["tilt_deg"], cam["hfov"][0], cam["vfov"][0], FLOOR_Z + WORK_DZ)
        a.add_patch(Polygon(fp2, closed=True, fill=False, ec=BLUE, lw=1.0, ls="--")).set_clip_path(clip)
        a.plot([c[0]], [c[1]], marker="o", ms=7, color=ORANGE if len(cam["hfov"]) > 1 else BLUE, mec=SURF, mew=1.5,
               clip_on=False)
        if "tele" in r:
            for name, t in SEATS.items():
                yw, tl = aim(c, t)
                ft = footprint(c, yw, tl, cam["hfov"][1], cam["vfov"][1], t[2])
                a.add_patch(Polygon(ft, closed=True, color=ORANGE, alpha=0.55, lw=0))
                a.plot([t[0]], [t[1]], "+", color=INK, ms=5, mew=1)
                tr = r["tele"][name]
                off = {"vial rack (tray B)": (-60, -120), "doser shuttle fork (tray B)": (60, 40),
                       "CubXL holder seat (tray A)": (-60, 60)}.get(name, (40, 40))
                a.text(t[0] + off[0], t[1] + off[1], f"{tr['mm_per_px']:.2f} mm/px", fontsize=7, color=INK,
                       ha="right" if off[0] < 0 else "left")
        title = (f"{num[spot]}  {r['label']}: {cam['short']}\nfloor {100 * r['floor_coverage']:.0f} %, 300 mm up "
                 f"{100 * r['coverage_300mm_up']:.0f} %, room {100 * r['room_share']:.0f} % of the picture")
        a.set_title(title, loc="left", fontsize=8.5, color=INK)
        a.set_xlim(-TRAY_X - 60, TRAY_X + 60)
        a.set_ylim(y0 - 160, y1 + 60)
        a.set_aspect("equal")
        a.tick_params(labelsize=7)
        a.grid(color=GRID, lw=0.4)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        a.text(-TRAY_X, y0 - 140, "the opening", fontsize=7, color=MUTED)
    fig.suptitle("Security cameras in the bay: where they hang and what they see of the presented tray",
                 x=0.05, ha="left", fontsize=13, color=INK, y=0.975)
    fig.text(0.05, 0.925, "Section: the 95.5 mm band (blue) over the tray, under a roof at 1829 mm; the front strip "
             "(aqua), which no goods pass under; each camera to scale and the edges of its picture in the middle "
             "plane. Plans: the picture on the tray's floor (filled) and 300 mm over it (dashed); orange: the PTZ at "
             "full zoom on each workflow seat (reach.seats), mm per pixel there. Rectilinear lenses; no occlusion.",
             fontsize=8.5, color=INK2, wrap=True)
    fig.savefig(path, facecolor=SURF)
    plt.close(fig)
    return path


# ===================================================================================================== power
POE_EFF = 0.88       # PSE conversion and a short patch lead: ours (802.3 budgets 12.95 of 15.4 W for 100 m of cable)
PI_RELAY_W = (27.0, 5.0)     # a Pi 5 relaying a tray's streams: its 27 W supply (rated), ~4 W bare + the relays (ours)
SWITCH_POE_BUDGET_W, SWITCH_POE_PORTS = 52.0, 4     # the tray switch ups.py assumes: Ubiquiti USW-Lite-8-PoE


def cam_w(cam: dict) -> tuple:
    """(max, typical) W at the camera; typical is the maker's if published, else 70 % of the max (IR off): ours."""
    mx = float(cam["w_max"])
    return mx, float(cam["w_typ"]) if cam.get("w_typ") else round(0.7 * mx, 1)


def tray_power(cam: dict, pi_on_poe: bool = False) -> dict:
    """Each powered tray's UPS-backed branch with its HQ/Wide units (ups.TRAY_LOADS) and with security cameras in
    their place: the cameras on the tray's PoE switch (whose 60 W rating already covers its 52 W PoE budget), one Pi
    5 per tray on its 27 W supply (or on a PoE+ HAT from the same switch), the switch as before. The UPS stays the one
    ups.py picked; its runtime at the new typical draw is from its maker's table (ups.runtime_min)."""
    import ups
    mx, ty = cam_w(cam)
    out = {}
    for k, rows in ups.TRAY_LOADS.items():
        pis = [r for r in rows if r["key"] == "pi_unit"]
        if not pis:
            continue
        n = sum(r["qty"] for r in pis)
        ld = ups.tray_load(k)
        m = ups.unit_of(k)
        poe = n * mx + (13.0 if pi_on_poe else 0.0)          # a Pi 5 on a PoE+ HAT: about 13 W at most (ours)
        ports = n + (1 if pi_on_poe else 0)
        rated = ld["backed_rated_w"] - sum(r["rated_w"] for r in pis) + (0.0 if pi_on_poe else PI_RELAY_W[0])
        typ = ld["backed_typical_w"] - sum(r["typical_w"] for r in pis) + (n * ty + (PI_RELAY_W[1] if pi_on_poe
                                                                                   else 0.0)) / POE_EFF
        typ += 0.0 if pi_on_poe else PI_RELAY_W[1]
        out[k] = dict(cameras=n, ups=m["model"], backed_rated_now_w=ld["backed_rated_w"],
                      backed_rated_w=round(rated), backed_typical_now_w=ld["backed_typical_w"],
                      backed_typical_w=round(typ, 1), typical_change_w=round(typ - ld["backed_typical_w"], 1),
                      runtime_now_min=round(ups.runtime_min(m, ld["backed_typical_w"])),
                      runtime_min=round(ups.runtime_min(m, typ)), poe_w=round(poe, 1), poe_ports=ports,
                      poe_ok=poe <= SWITCH_POE_BUDGET_W and ports <= SWITCH_POE_PORTS,
                      ups_still_ok=m["w"] >= rated and ups.runtime_min(m, typ) >= ups.RUNTIME_MIN)
    return out
