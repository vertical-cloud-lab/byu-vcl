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
FRONT_STRIP = (HEADER_Y[0], TRAY_Y[0])                          # -1582 .. -1462: 120 mm deep (the LED light, 12 mm
                                                                # under the header, has to be split where a camera is)


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
# * The pair hangs from the roof at the middle back, 76 mm in front of the shutter's face, where the HQ/Wide bay unit
#   is now: a fixed wide turret and a PTZ side by side, 240 mm apart. Both must stay inside the 95.5 mm band, which a
#   mini PTZ like the Axis M5075-G (63 mm tall) does. From there they face the arm's work, so the arm doesn't hide the
#   gripper, and the wrist's D405 sees it from the other side. UR10e clearance 286 / 313 mm (arm_clearance).
# * The middle front camera hangs in the front strip, 300 mm right of the middle, and looks back: the whole tray, the
#   arm from behind, and none of the room. In the middle of the strip it keeps 105 mm from the arm's capsules (the
#   elbow rises to 1.57 m reaching the tray's front half); 300 mm right, 146 mm. A taller camera may hang there, since
#   no goods pass under the strip, but the arm's elbow comes within 17 mm of a 180 mm PTZ in the middle.
# * The top-down camera hangs from the roof over the tray's centre: one wide picture of the whole floor, square to it
#   (inventory, and a plain homography for registering a tray's layout). 242 mm from the arm.
BAY_SPOTS = {     # key: (label, mount point on the roof (x, y, z), how it is placed)
    "back_wide": ("middle back: wide", (-120.0, -645.0, ROOF_Z), "on the roof, 76 mm in front of the shutter's face"),
    "back_ptz": ("middle back: PTZ", (120.0, -645.0, ROOF_Z), "on the roof, beside the wide one"),
    "front": ("middle front", (300.0, -1522.0, ROOF_Z), "under the header, in the front strip, looking back"),
    "top": ("middle, straight down", (0.0, -1030.0, ROOF_Z), "on the roof over the tray's centre"),
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
        elif spot.startswith("back"):
            yaw, tilt, cov, cov2, room = best_aim(c, hf, vf, np.arange(170.0, 191.0, 5.0), np.arange(30.0, 81.0, 2.5))
        else:
            yaw, tilt, cov, cov2, room = best_aim(c, hf, vf, np.arange(-40.0, 1.0, 5.0) if c[0] > 0 else
                                                  np.arange(0.0, 41.0, 5.0), np.arange(40.0, 86.0, 2.5))
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
    ax.set_title("The bay in section, every camera drawn at x = 0 (the back pair is at x = -120 and +120 mm, the "
                 "front one at +300)", loc="left", fontsize=10, color=INK)
    # one plan per camera: the presented tray's floor, the picture on it (filled) and 300 mm up (dashed)
    order = ["back_wide", "back_ptz", "front", "top"]
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


def post_fit(cands: dict, head: dict) -> dict:
    """Each candidate on a tray's 2020 post in place of an HQ/Wide head, its aim pivot where the head's tilt axis is
    (643 mm over the tray's underside on the standard post): its top (pivot + h_up_mm, our estimate from the maker's
    dimensions) against each tray's highest top that keeps its slot (span - 20 mm). -> {candidate: {trays that fit,
    trays whose slot would grow by a 25 mm step, the top}}."""
    import services as S
    piv = V.T_FLOOR + S.CAM_H + S.TILT_AXIS[2]
    out = {}
    for key, c in cands.items():
        if c.get("h_up_mm") is None:
            continue
        top = piv + c["h_up_mm"]
        fits, grows = [], {}
        for k, h in head.items():
            p = piv if k != "H" else V.T_FLOOR + 270.0 + S.TILT_AXIS[2]
            t = p + c["h_up_mm"]
            if t <= h["highest_top_same_slot_mm"]:
                fits.append(k)
            else:
                grows[k] = V.PITCH * math.ceil((max(t, h["tallest_other_mm"]) + V.GOODS_CLEAR) / V.PITCH - 1e-9) - \
                    h["span_mm"]
        out[key] = dict(top_mm=round(top, 1), fits=fits, slot_grows_mm=grows)
    return out


def fig_fit(cands: dict, keys: list, head: dict, path: Path) -> Path:
    """out/security_cameras_fit.png: each candidate to scale, (a) hung from the bay's roof against the 95.5 mm band,
    (b) on a tray post at the HQ/Wide head's pivot against the trays' headroom."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle
    import services as S
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED,
                         "ytick.color": MUTED, "font.family": "DejaVu Sans"})
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(16, 9.2), dpi=150, facecolor=SURF,
                                 gridspec_kw=dict(height_ratios=[1, 1.15], hspace=0.55))
    fig.subplots_adjust(left=0.06, right=0.985, top=0.88, bottom=0.08)
    gap = 60.0
    xs, x = [], 0.0
    for k in keys:
        w = max(cands[k]["dia_mm"], 60.0)
        xs.append(x + w / 2)
        x += w + gap + 90.0
    # (a) the roof
    a1.set_facecolor(SURF)
    a1.axhline(ROOF_Z, color=INK, lw=1.6)
    a1.axhline(ENV_Z, color=CRIT, lw=1.0, ls="--")
    a1.add_patch(Rectangle((-200, ENV_Z), x + 400, BAND, color=BLUE, alpha=0.10, lw=0))
    a1.text(-150, ROOF_Z + 8, "the bay's roof (assumed at 1829 mm)", fontsize=8, color=INK)
    a1.text(-150, ENV_Z - 22, "top of the goods + Kardex's 20 mm (1733.5 mm): over the tray, nothing hangs lower; "
            "the front strip has no such limit", fontsize=8, color=INK2)
    for k, cx in zip(keys, xs):
        c = cands[k]
        d, h = c["dia_mm"], c["hang_mm"]
        col = ORANGE if len(c["hfov"]) > 1 else BLUE
        a1.add_patch(FancyBboxPatch((cx - d / 2, ROOF_Z - h), d, h, boxstyle="round,pad=0,rounding_size=8",
                                    color=col, lw=0, alpha=0.85))
        low = ROOF_Z - h
        ok = low >= ENV_Z
        a1.text(cx, low - 18, ("fits the band, " if ok else "strip only, ") + f"{abs(low - ENV_Z):.0f} mm "
                + ("spare" if ok else "below the band"), ha="center", va="top", fontsize=7.5,
                color=INK if ok else CRIT)
        a1.text(cx, ROOF_Z + 40, c["short"], ha="center", va="bottom", fontsize=7.5, color=INK, rotation=0, wrap=True)
    a1.set_xlim(-200, x + 200)
    a1.set_ylim(ROOF_Z - 260, ROOF_Z + 110)
    a1.set_aspect("equal")
    a1.set_xticks([])
    a1.set_ylabel("z, mm")
    for s in ("top", "right", "bottom"):
        a1.spines[s].set_visible(False)
    a1.set_title("(a) Hung from the bay's roof, to scale (published height; a bullet or box camera on its ceiling "
                 "bracket)", loc="left", fontsize=10, color=INK)
    # (b) a tray post
    a2.set_facecolor(SURF)
    piv = V.T_FLOOR + S.CAM_H + S.TILT_AXIS[2]
    lims = sorted({h["highest_top_same_slot_mm"] for h in head.values() if h["highest_top_same_slot_mm"] < 800})
    a2.axhline(piv, color=MUTED, lw=0.8, ls=":")
    a2.text(-150, piv - 4, "aim pivot: the HQ/Wide head's tilt axis, 643 mm", fontsize=7.5, color=INK2, va="top")
    for lim in lims:
        trays = "".join(sorted(k for k, h in head.items() if h["highest_top_same_slot_mm"] == lim))
        a2.axhline(lim, color=CRIT if lim == min(lims) else AXIS, lw=0.9, ls="--")
        a2.text(x + 180, lim + 2, f"trays {trays}: top <= {lim:.0f} mm keeps the slot", fontsize=7.5, ha="right",
                va="bottom", color=INK2)
    cur = max(max(h["camera_tops_mm"]) for h in head.values())
    for k, cx in zip(keys, xs):
        c = cands[k]
        if c.get("h_up_mm") is None:
            continue
        d = c["dia_mm"]
        top = piv + c["h_up_mm"]
        bot = piv - c.get("h_down_mm", c["h_up_mm"])
        col = ORANGE if len(c["hfov"]) > 1 else BLUE
        a2.add_patch(FancyBboxPatch((cx - d / 2, bot), d, top - bot, boxstyle="round,pad=0,rounding_size=8",
                                    color=col, lw=0, alpha=0.85))
        a2.add_patch(Rectangle((cx - d / 2 - 22, piv - 300), 20, 300 + 60, color=AXIS, lw=0))   # the 2020 post
        a2.text(cx, top + 10, f"top {top:.0f}", ha="center", va="bottom", fontsize=7.5,
                color=INK if top <= min(lims) else CRIT)
        a2.text(cx, piv - 320, c["short"], ha="center", va="top", fontsize=7.5, color=INK)
    a2.set_xlim(-200, x + 200)
    a2.set_ylim(piv - 380, max(lims) + 70)
    a2.set_aspect("equal")
    a2.set_xticks([])
    a2.set_ylabel("z over the tray's underside, mm")
    for s in ("top", "right", "bottom"):
        a2.spines[s].set_visible(False)
    a2.set_title(f"(b) On a tray's 2020 post in place of the HQ/Wide head (its top today: up to {cur:.0f} mm), aimed "
                 "down; the box is what the camera sweeps as it is aimed (our estimate from the maker's dimensions)",
                 loc="left", fontsize=10, color=INK)
    fig.suptitle("Security cameras to scale: under the bay's roof, and on the trays' camera posts", x=0.06,
                 ha="left", fontsize=13, color=INK, y=0.975)
    fig.text(0.06, 0.925, "Blue: fixed cameras; orange: motorized zoom (PTZ or varifocal). A red label: outside the "
             "band, or a top that would make the tightest trays' slots taller by a 25 mm step.", fontsize=8.5,
             color=INK2)
    fig.savefig(path, facecolor=SURF)
    plt.close(fig)
    return path


PI_UNIT = {     # the HQ/Wide unit's two pictures, for comparison (services.SOURCES: cm3_wide, hq_sensor)
    "wide": dict(hfov=102.0, px=4608, what="Camera Module 3 Wide"),
    "hq": dict(hfov=22.2, px=4056, what="HQ Camera, 16 mm lens"),
}


def tray_detail(cands: dict, keys: list) -> dict:
    """At each tray camera's aim point, the picture's width and mm per pixel: the HQ/Wide unit's two pictures, then
    each candidate's widest and (for a zoom) narrowest. -> {unit: {...}} and the medians."""
    spots = tray_spots()
    rows = {}
    for s in spots:
        d = s["dist_mm"]
        r = {"dist_mm": d}
        for k, p in PI_UNIT.items():
            r[f"pi_{k}"] = round(2 * d * math.tan(math.radians(p["hfov"]) / 2) / p["px"], 3)
        for k in keys:
            c = cands[k]
            r[f"{k}_wide"] = round(2 * d * math.tan(math.radians(c["hfov"][0]) / 2) / c["px"][0], 3)
            if len(c["hfov"]) > 1:
                r[f"{k}_tele"] = round(2 * d * math.tan(math.radians(c["hfov"][1]) / 2) / c["px"][0], 3)
                r[f"{k}_tele_focus_ok"] = None if c.get("min_focus_tele_mm") is None else d >= c["min_focus_tele_mm"]
        rows[s["unit"]] = r
    med = {k: round(float(np.median([r[k] for r in rows.values()])), 3) for k in next(iter(rows.values()))
           if not k.endswith("_ok")}
    return dict(per_unit=rows, median=med)


# ===================================================================================================== the 3-D still
# Our simple shapes, at the recommended places, in PR #318's VLM scene (services.build_vlm with cams=False): a turret
# is a base disc, an eyeball and a lens; a PTZ a mount, a body, a dome and a lens. Sizes are each model's published
# outline. Nothing here is used by the animations.
SEC_MATS = {"sec_white": (0.92, 0.92, 0.90, 1.0, 0.35), "sec_black": (0.06, 0.06, 0.07, 1.0, 0.8),
            "sec_roof": (0.70, 0.72, 0.75, 0.30, 0.1), "sec_plate": (0.27, 0.28, 0.30, 1.0, 0.25)}


def _turret_meshes(base_c, n, D, H, look) -> dict:
    """A turret whose base disc is centred at base_c with its outward normal n (into the room), D across and H from
    the base to the eyeball's far side, looking along `look`. {material: [PolyData]}."""
    import pyvista as pv
    n = np.asarray(n, float) / np.linalg.norm(n)
    look = np.asarray(look, float) / np.linalg.norm(look)
    t = 0.18 * H
    base = pv.Cylinder(center=base_c + n * t / 2, direction=n, radius=D / 2, height=t, resolution=48)
    rb = 0.40 * D
    ball_c = base_c + n * (H - rb)
    ball = pv.Sphere(radius=rb, center=ball_c, theta_resolution=40, phi_resolution=40)
    hood = pv.Cylinder(center=ball_c + look * (rb * 0.92), direction=look, radius=0.17 * D, height=0.16 * D,
                       resolution=32)
    return {"sec_white": [base, ball], "sec_black": [hood]}


def _ptz_meshes(top_c, D, H, look) -> dict:
    """A PTZ hanging from top_c: a mount ring, a body and a dome, looking along `look`."""
    import pyvista as pv
    look = np.asarray(look, float) / np.linalg.norm(look)
    down = np.array([0.0, 0.0, -1.0])
    ring = pv.Cylinder(center=top_c + down * 0.06 * H, direction=down, radius=0.42 * D, height=0.12 * H,
                       resolution=48)
    body = pv.Cylinder(center=top_c + down * 0.36 * H, direction=down, radius=D / 2, height=0.48 * H, resolution=48)
    dome_c = top_c + down * (H - D / 2)
    dome = pv.Sphere(radius=0.47 * D, center=dome_c, theta_resolution=40, phi_resolution=40)
    lens = pv.Cylinder(center=dome_c + look * 0.40 * D, direction=look, radius=0.13 * D, height=0.16 * D,
                       resolution=32)
    return {"sec_white": [ring, body, dome], "sec_black": [lens]}


def _add_mesh_group(sc, g, by_mat, parent=None):
    import lab
    import services as S
    M = dict(S.mats())
    M.update(SEC_MATS)
    for mat, meshes in by_mat.items():
        r, gg, b, a, spec = M[mat]
        sc.add(f"{g}/{mat}", lab._merge(meshes) if len(meshes) > 1 else meshes[0], (r, gg, b), g, opacity=a,
               specular=spec)
    sc.gmat[g] = np.eye(4)
    if parent:
        sc.parent[g] = parent


def still(choice: dict, cands: dict, res: dict, tray_cam: str, k: str = "A") -> str:
    """out/security_cameras_3d_still.png: tray k presented, its camera posts with a turret each where the HQ/Wide heads
    were, and the bay's set under an assumed roof (drawn see-through)."""
    import animate as A
    import lab
    import services as S
    import setup_lab
    data, idata = lab.meshes(), setup_lab.tour_load_safe()
    sc, L, live = S.build_vlm("security_cameras_3d", data, idata, "Security cameras: the bay's set and tray "
                              f"{k}'s", cams=False, mp4=False)
    L.skin(1.0)(1.0)
    L.tray[k] = [V.Y_OPEN, V.Z_OPEN]
    L.where[k] = "open"
    L.lift_z = V.Z_OPEN
    S.set_dock(sc, "open", 0.0)
    S.set_dock(sc, S.HOME[k], 1.0)
    L.apply_state()
    import pyvista as pv
    roof = pv.Box(bounds=(-SIDE_X, SIDE_X, HEADER_Y[1], SHUTTER_Y - 2, ROOF_Z, ROOF_Z + 3))
    _add_mesh_group(sc, "sec_roof", {"sec_roof": [roof]})
    lbl = []
    # the bay's set
    for spot, r in res.items():
        cam = cands[r["camera"]]
        top = np.array(r["mount"], float)
        f, _, _ = basis(r["yaw_deg"], r["tilt_deg"])
        if spot == "back_ptz":
            seat = SEATS["CubXL holder seat (tray A)"]
            f = np.subtract(seat, r["lens"])
            by = _ptz_meshes(top, cam["dia_mm"], cam["hang_mm"], f)
        else:
            by = _turret_meshes(top, (0, 0, -1), cam["dia_mm"], cam["hang_mm"], f)
        _add_mesh_group(sc, f"secbay_{spot}", by)
        lbl.append((f"{r['label']}: {cam['short']}", tuple(top - (0, 0, cam["hang_mm"])),
                    {"back_wide": (0.30, 0.06), "back_ptz": (0.62, 0.06), "front": (0.80, 0.14),
                     "top": (0.12, 0.10)}[spot]))
    # tray k's posts, each with a turret where the head's tilt axis was, looking at the head's aim point
    c = cands[tray_cam]
    mast = S.meshes_of(f"mast{S.POST_H}True", lambda: S.mast_parts(S.POST_H, True), 0.5)
    for i, (x, y, ax, ay, az, *fixed) in enumerate(S.TRAY_CAMS[k]):
        post, pan, tilt = S.rig_pose(x, y, (ax, ay, az), S.CAM_H, post=fixed[0] if fixed else None)
        g = f"seccam_{k}{i}"
        S.add_meshes(sc, g, mast, g)
        sc.gmat[g] = I_T((x, y, V.T_FLOOR)) @ I_R((0, 0, 1), post)
        sc.parent[g] = f"tray_{k}"
        a = math.radians(post)
        n = np.array([math.sin(a), -math.cos(a), 0.0])        # the post's front face, outward (rig -y, turned)
        zc = V.T_FLOOR + S.CAM_H + S.TILT_AXIS[2]
        base_c = np.array([x, y, zc]) + n * 16.0
        plate = pv.Cylinder(center=np.array([x, y, zc]) + n * 13.0, direction=n, radius=c["dia_mm"] / 2 + 4,
                            height=6.0, resolution=48)
        look = np.subtract((ax, ay, az), base_c + n * (c["hang_mm"] - 0.4 * c["dia_mm"]))
        by = _turret_meshes(base_c, n, c["dia_mm"], c["hang_mm"], look)
        by.setdefault("sec_plate", []).append(plate)
        _add_mesh_group(sc, f"sectur_{k}{i}", by, parent=f"tray_{k}")
        lbl.append((f"{c['short']} on a tray post", tuple(A.tray_world(k, (x, y, zc + 60.0))),
                    (0.10 + 0.55 * i, 0.30)))
    sc.cam = [(1650.0, -3350.0, 1640.0), (150.0, -1050.0, 1380.0), (0, 0, 1)]
    sc.step("", f"Tray {k} at the opening with a {c['short']} on each of its two camera posts, where the HQ/Wide "
            "heads were; under a roof assumed at the opening's top (drawn see-through), the front pair under the "
            "header (a wide turret and a PTZ, here on the CubXL's holder seat), a turret at the middle back and one "
            "looking straight down.", 0.1, None, hold=0.0, labels=lbl, still=True)
    return sc.save()


def I_T(v):
    import instruments as I
    return I._T(v)


def I_R(axis, deg):
    import instruments as I
    return I._R(axis, deg)


# ===================================================================================================== cost
def bom(cands: dict, gear: dict, tiers: dict) -> dict:
    """The bill of materials per tier: every powered tray's cameras (as many as it has HQ/Wide units today) on its
    existing PoE switch with one Pi 5, and each Shuttle's bay set with its own Pi 5; against today's HQ/Wide units
    (one Pi 5 each). tiers: {name: {"tray": key, "tray_zoom": key or None, "zoom_units": [unit, ...],
    "bay": {spot: key}}}. Prices are each item's `price` (USD, one retailer, the date in its entry)."""
    import ups
    n_tray = {k: sum(r["qty"] for r in rows if r["key"] == "pi_unit") for k, rows in ups.TRAY_LOADS.items()}
    n_tray = {k: v for k, v in n_tray.items() if v}
    units = [s["unit"] for s in tray_spots()]
    n_cams = sum(n_tray.values())
    n_bays = len(V.SHUTTLE_X)
    relay = sum(gear[g]["price"] * q for g, q in gear["_relay"]["items"])
    per_point_extra = sum(gear[g]["price"] * q for g, q in gear["_per_camera"]["items"])
    out = {}
    for name, t in tiers.items():
        zoom = set(t.get("zoom_units") or [])
        lines = []
        cam_cost = 0.0
        for u in units:
            key = t["tray_zoom"] if (u in zoom and t.get("tray_zoom")) else t["tray"]
            cam_cost += cands[key]["price"]
        lines.append(("tray cameras", n_cams, round(cam_cost, 2)))
        lines.append(("mount, lead and card per tray camera", n_cams, round(n_cams * per_point_extra, 2)))
        lines.append(("Pi 5 relays, one per powered tray", len(n_tray), round(len(n_tray) * relay, 2)))
        bay_cams = sum(cands[k]["price"] + per_point_extra for k in t["bay"].values())
        lines.append(("bay sets (cameras, mounts, leads), one per Shuttle", n_bays, round(n_bays * bay_cams, 2)))
        lines.append(("Pi 5 relays, one per bay", n_bays, round(n_bays * relay, 2)))
        extra = t.get("extra", [])
        for what, q, each in extra:
            lines.append((what, q, round(q * each, 2)))
        total = sum(c for _, _, c in lines)
        per_tray_point = (cam_cost + n_cams * per_point_extra + len(n_tray) * relay) / n_cams
        out[name] = dict(lines=lines, total=round(total), tray_points=n_cams, bay_points=n_bays * len(t["bay"]),
                         per_tray_point=round(per_tray_point), per_bay_set=round(bay_cams + relay),
                         pi5_count=len(n_tray) + n_bays)
    today = gear["_pi_unit"]
    unit = sum(gear[g]["price"] * q for g, q in today["items"])
    out["today"] = dict(per_point=round(unit), points=n_cams + n_bays, total=round(unit * (n_cams + n_bays)),
                        pi5_count=n_cams + n_bays)
    return out


# ===================================================================================================== main
def run(arm: bool = False) -> dict:
    """Everything but the 3-D still: out/security_cameras.json and the two figures."""
    head = tray_headroom()
    arm_res = None
    if arm:
        arm_res = {}
        for spot, key in CHOICE.items():
            c = CANDIDATES[key]
            arm_res[spot] = arm_clearance(cyl_points(BAY_SPOTS[spot][1], c["dia_mm"], c["hang_mm"]))
    bay = bay_analysis(CHOICE, CANDIDATES, arm_res)
    if not arm:
        old = OUT / "security_cameras.json"
        if old.exists():                                     # keep the last arm check if this run skipped it
            prev = json.loads(old.read_text()).get("bay", {})
            for spot, r in bay.items():
                if "arm" in prev.get(spot, {}) and prev[spot].get("camera") == r["camera"] and \
                        tuple(prev[spot].get("mount", ())) == tuple(r["mount"]):
                    r["arm"] = prev[spot]["arm"]
    fits = post_fit(CANDIDATES, head)
    detail = tray_detail(CANDIDATES, [k for k in FIG_FIT_KEYS if CANDIDATES[k].get("h_up_mm") is not None])
    power = {k: tray_power(CANDIDATES[k]) for k in TRAY_CHOICES}
    power_poe_pi = tray_power(CANDIDATES[TRAY_CHOICES[0]], pi_on_poe=True)
    cost = bom(CANDIDATES, GEAR, TIERS)
    out = dict(
        geometry=dict(floor_z=FLOOR_Z, goods_top_with_clearance_z=ENV_Z, roof_z_assumed=ROOF_Z, band_mm=BAND,
                      tray_y=TRAY_Y, front_strip_y=FRONT_STRIP, header_y=HEADER_Y, shutter_face_y=SHUTTER_Y,
                      f1_underside_z=F1_Z, note="the roof is assumed at the opening's clear height (1829 mm); "
                                                "the goods envelope is the 996 mm opening's estimate (vlm.py)"),
        bay=bay, choice=CHOICE, tray_headroom=head, post_fit=fits, tray_detail=detail, tray_power=power,
        tray_power_pi_on_poe=power_poe_pi, cost=cost, tiers=TIERS,
        candidates=CANDIDATES, gear={k: v for k, v in GEAR.items() if not k.startswith("_")},
        kits={k: v for k, v in GEAR.items() if k.startswith("_")})
    (OUT / "security_cameras.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    fig_bay(CHOICE, CANDIDATES, bay, OUT / "security_cameras_bay.png")
    fig_fit(CANDIDATES, FIG_FIT_KEYS, head, OUT / "security_cameras_fit.png")
    return out


if __name__ == "__main__":
    words = sys.argv[1:]
    res = run(arm="arm" in words)
    if "still" in words:
        print(still(CHOICE, CANDIDATES, res["bay"], STILL_TRAY_CAM, "A"))
    for spot, r in res["bay"].items():
        print(spot, r["camera"], f"cover {r['floor_coverage']:.2f} / {r['coverage_300mm_up']:.2f}",
              f"room {r['room_share']:.2f}", f"low {r['lowest_point_mm']}", f"band {r['band_margin_mm']}",
              r.get("arm", {}).get("smallest_gap_mm"))
    for name, c in res["cost"].items():
        print(name, c.get("total"), c.get("per_tray_point", c.get("per_point")))


# ===================================================================================================== the note's tables
def _md(rows, head) -> str:
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def tables(res: dict) -> dict:
    """The generated tables of notes/security_cameras.md, by marker."""
    C = res["candidates"]
    t = {}
    rows = []
    for k, c in C.items():
        fov = "/".join(f"{h:.0f}" for h in c["hfov"]) + "°"
        rows.append((c["type"], f"{c['maker']} {c['model']}", c["res_txt"], f"{c['lens_txt']}, {fov}",
                     c.get("zoom_txt", "none"), c.get("ir_txt", "-"), c["poe_txt"], c["size_txt"],
                     c.get("onvif_txt", "-"), c.get("ndaa_txt", "-"), f"${c['price']:,.0f}",
                     f"[{c['vendor']}]({c['price_url']}), {c['price_date']}" + (" (snippet)" if c.get("price_kind")
                                                                                == "snippet" else "")))
    t["CANDIDATES"] = _md(rows, ["Type", "Model", "Resolution", "Lens, across", "Optical zoom", "IR",
                                 "PoE, max", "Size", "ONVIF / local", "Federal funds", "Price", "Seen at"])
    rows = []
    for spot, r in res["bay"].items():
        c = C[r["camera"]]
        arm = r.get("arm", {}).get("smallest_gap_mm")
        low = (f"{r['lowest_point_mm']:.0f} mm, {r['band_margin_mm']:+.0f} mm to the band" if r["over_goods"]
               else f"{r['lowest_point_mm']:.0f} mm, in the strip")
        rows.append((r["label"], c["short"], f"({r['mount'][0]:.0f}, {r['mount'][1]:.0f})",
                     f"{r['yaw_deg']:.0f} / {r['tilt_deg']:.0f}", f"{100 * r['floor_coverage']:.0f} %",
                     f"{100 * r['coverage_300mm_up']:.0f} %", f"{100 * r['room_share']:.0f} %", low,
                     "-" if arm is None else f"{arm} mm", f"{r['mm_per_px_at_tray_centre']:.2f}"))
    t["BAY_TABLE"] = _md(rows, ["Spot", "Camera", "Mount (x, y)", "Heading / tilt, °", "Tray floor seen",
                                "300 mm up", "Room in the picture", "Lowest point", "Nearest the arm",
                                "mm/px at the tray's centre"])
    ptz = next((r for r in res["bay"].values() if "tele" in r), None)
    if ptz:
        c = C[ptz["camera"]]
        rows = [(name, f"{v['distance_mm']} mm", f"{v['picture_width_mm']} mm", f"{v['mm_per_px']:.2f}",
                 "-" if v["focus_ok"] is None else ("yes" if v["focus_ok"] else "**no**"))
                for name, v in ptz["tele"].items()]
        t["PTZ_TABLE"] = _md(rows, ["The PTZ at full zoom on", "Distance", "Picture across", "mm/px",
                                    f"In focus (closer than {c.get('min_focus_tele_mm') or '?'} mm is not)"])
    rows = []
    for k, h in res["tray_headroom"].items():
        rows.append((k, h["slot"], f"{h['span_mm']:.0f}", f"{h['tallest_other']} ({h['tallest_other_mm']:.0f})",
                     f"{max(h['camera_tops_mm']):.0f}", f"{h['highest_top_same_slot_mm']:.0f}",
                     f"{h['span_if_cameras_below_mm']:.0f}"))
    t["HEADROOM_TABLE"] = _md(rows, ["Tray", "Slot", "Span", "Tallest other thing (top)", "Camera heads' top",
                                     "Highest top for the same slot", "Span with no camera above it"])
    rows = []
    for k, f in res["post_fit"].items():
        c = C[k]
        grow = ", ".join(f"{t_} +{v:.0f}" for t_, v in f["slot_grows_mm"].items()) or "none"
        rows.append((c["short"], f"{c['h_up_mm']:.0f}", f"{f['top_mm']:.0f}", "".join(sorted(f["fits"])), grow))
    t["POSTFIT_TABLE"] = _md(rows, ["On a tray post", "Over the pivot", "Top", "Trays it fits as they are",
                                    "Slots that grow (mm)"])
    key0 = next(iter(res["tray_power"]))
    rows = []
    for k, p in res["tray_power"][key0].items():
        rows.append((k, p["cameras"], p["ups"].replace("Liebert ", ""), f"{p['backed_rated_now_w']} -> "
                     f"{p['backed_rated_w']}", f"{p['backed_typical_now_w']} -> {p['backed_typical_w']:.0f}",
                     f"{p['typical_change_w']:+.0f}", f"{p['runtime_now_min']} -> {p['runtime_min']}",
                     f"{p['poe_w']:.0f} W, {p['poe_ports']} ports", "yes" if p["ups_still_ok"] and p["poe_ok"]
                     else "**no**"))
    t["POWER_TABLE"] = _md(rows, ["Tray", "Cameras", "UPS", "Backed, rated W", "Backed, typical W", "Change",
                                  "Runtime, min", "PoE from the switch", "Still fits"])
    rows = []
    for name, cst in res["cost"].items():
        if name == "today":
            continue
        rows.append((name, f"${cst['per_tray_point']:,}", f"${cst['per_bay_set']:,}", cst["pi5_count"],
                     f"**${cst['total']:,}**"))
    td = res["cost"]["today"]
    rows.append(("today: HQ + Wide units (for comparison)", f"${td['per_point']:,}", "-", td["pi5_count"],
                 f"${td['total']:,}"))
    t["COST_TABLE"] = _md(rows, ["Tier", "Per tray point (camera, mount, lead, card, its share of the Pi 5)",
                                 "Per bay set (with its Pi 5)", "Pi 5s", "Whole lab"])
    return t


def fill_notes(res: dict, path: Path = HERE / "notes" / "security_cameras.md") -> None:
    """Write the generated tables between <!-- BEGIN:X --> and <!-- END:X --> in the note."""
    s = path.read_text()
    for k, md in tables(res).items():
        a, b = f"<!-- BEGIN:{k} -->", f"<!-- END:{k} -->"
        if a in s and b in s:
            i, j = s.index(a) + len(a), s.index(b)
            s = s[:i] + "\n" + md + "\n" + s[j:]
    path.write_text(s)
