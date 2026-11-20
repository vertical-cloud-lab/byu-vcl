"""Security cameras instead of the Pi HQ/Wide stream-camera units (#303, PR #318 follow-up): candidates, where each
would go, what it sees in the bay, whether it fits, what it draws and what it costs.

    python3 security_cams.py           # out/security_cameras.json and the two figures below (matplotlib, a few seconds)
    python3 security_cams.py arm       # the same, plus the UR10e's clearance to every bay spot (reach.py's 320 poses,
                                       # about 30 s per spot; services.bay_arm_clearance's method, our points)
    python3 security_cams.py notes     # also refill the generated tables in notes/security_cameras.md
    python3 runner_guard.py slot --mem 5000 -- xvfb-run -a python3 security_cams.py still
                                       # also out/security_cameras_3d_still.png: one 3-D still (a few minutes)

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


ROOM_MAX = 0.02      # a bay camera may show this much of the room through the opening (people): ours


def least_room(c, hfov, vfov, yaws, tilts) -> tuple:
    """As best_aim, but the aim that sees the least of the room, then the most floor."""
    best = None
    for yaw in yaws:
        for tilt in tilts:
            room = room_share(c, yaw, tilt, hfov, vfov, n=31)
            cov = coverage(c, yaw, tilt, hfov, vfov)
            key = (-round(room, 3), cov)
            if best is None or key > best[0]:
                best = (key, yaw, tilt, cov, coverage(c, yaw, tilt, hfov, vfov, dz=WORK_DZ), room)
    _, yaw, tilt, cov, cov2, room = best
    return yaw, tilt, cov, cov2, room


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


# ===================================================================================================== the candidates
# Researched 2026-11-20 (makers' datasheets where they could be opened; prices from one retailer each, on that day:
# Black Friday prices were in effect). Figures not published are None; ours are marked so.
# its length at 45 deg + half its diameter + 50 mm of bracket); h_up_mm: how far it rises over its aim pivot on a tray
# post (a turret or dome on the post's face: half its base; a bullet or box at 45 deg: as hang_mm less the bracket).
def _b(L, D):            # bullet/box at 45 degrees: (hang, h_up), ours
    up = 0.5 * L * 0.7071 + D / 2
    return round(up + 50.0, 1), round(up, 1)


FIXED = {
    "amcrest_t1179": dict(
        type="turret", maker="Amcrest (Dahua-made)", model="IP5M-T1179EW-AI-V3", short="Amcrest IP5M-T1179EW (aurora's)",
        res_txt="2960 x 1668, 20 fps", px=(2960, 1668), lens_txt="2.8 mm", hfov=(111.0,), vfov=(58.0,), zoom_txt="none",
        ir_txt="30 m", poe_txt="af, 5.0 W", w_max=5.0, w_typ=2.9, size_txt="Ø110 x 101 mm, 372 g", dia_mm=110.0,
        hang_mm=100.8, lens_drop_mm=60.0, h_up_mm=55.0, min_focus_mm=1100.0,
        onvif_txt="ONVIF; RTSP; P2P can be off", ndaa_txt="**no**: Dahua-made; out of stock",
        price=79.99, vendor="amcrest.com (out of stock)",
        price_url="https://www.amcrest.com/products/5mp-poe-camera-turret-ip5m-t1179ew-ai-v3", price_date="2026-11-20",
        price_kind="opened", src=["https://support.amcrest.com/hc/en-us/articles/22062123278733"],
        note="aurora's camera; Amcrest says it can no longer import Dahua-made products; P360/T78/R360"),
    "amlink_t5171": dict(
        type="turret", maker="AMLINK (Amcrest's new brand, FOXLINK, Taiwan)", model="AL5M-T5171EW",
        short="AMLINK AL5M-T5171EW", res_txt="2960 x 1668, 20 fps", px=(2960, 1668), lens_txt="2.8 mm",
        hfov=(111.0,), vfov=(58.0,), zoom_txt="none", ir_txt="30 m, can be off", poe_txt="af, 8.2 W (typ. 3.2)",
        w_max=8.2, w_typ=3.2, size_txt="Ø123 x 95 mm", dia_mm=123.0, hang_mm=94.9, lens_drop_mm=58.0, h_up_mm=61.5,
        min_focus_mm=1100.0, onvif_txt="S/G/T; RTSP; H.264 only", ndaa_txt="maker says yes (not verified)",
        price=94.99, vendor="amcrest.com",
        price_url="https://www.amcrest.com/products/amlink-5mp-security-ai-ip-poe-turret-camera-al5m-t5171ew",
        price_date="2026-11-20", price_kind="opened", src=["https://support.amcrest.com/hc/en-us/articles/49392408278669"],
        note="the nearest thing to aurora's turret still sold; P360/T78/R360"),
    "reolink_520a": dict(
        type="eyeball turret", maker="Reolink", model="RLC-520A (2.8 mm)", short="Reolink RLC-520A",
        res_txt="2560 x 1920, 25 fps", px=(2560, 1920), lens_txt="2.8 mm", hfov=(100.0,), vfov=(75.0,),
        zoom_txt="none", ir_txt="30 m", poe_txt="af; < 12 W (DC figure)", w_max=12.0, w_typ=None,
        size_txt="Ø105 x 95 mm, 468 g", dia_mm=105.0, hang_mm=95.0, lens_drop_mm=58.0, h_up_mm=52.5,
        min_focus_mm=None, onvif_txt="ONVIF, RTSP (enable them); P2P can be off; main stream <= 8 Mbit/s",
        ndaa_txt="yes (not a named company; Reolink's own statement)", price=59.99, vendor="reolink.com",
        price_url="https://reolink.com/us/product/rlc-520a/", price_date="2026-11-20", price_kind="opened",
        src=["https://reolink.com/us/product/rlc-520a/",
             "https://support.reolink.com/articles/900000617826-Which-Reolink-Products-Support-CGI-RTSP-ONVIF/"],
        note="a 4 mm version is 80 x 48 deg"),
    "unifi_g5turret": dict(
        type="turret", maker="Ubiquiti", model="UniFi G5 Turret Ultra", short="UniFi G5 Turret Ultra",
        res_txt="2688 x 1512, 30 fps", px=(2688, 1512), lens_txt="fixed", hfov=(102.4,), vfov=(54.9,),
        zoom_txt="none", ir_txt="30 m", poe_txt="PoE, 4 W", w_max=4.0, w_typ=None, size_txt="Ø90 x 71 mm, 330 g",
        dia_mm=90.0, hang_mm=71.2, lens_drop_mm=45.0, h_up_mm=45.0, min_focus_mm=None,
        onvif_txt="no ONVIF; RTSP only through a UniFi Protect console", ndaa_txt="yes (maker)",
        price=129.0, vendor="store.ui.com (plus a console)",
        price_url="https://store.ui.com/us/en/products/uvc-g5-turret-ultra", price_date="2026-11-20",
        price_kind="opened", src=["https://techspecs.ui.com/unifi/cameras-nvrs/uvc-g5-turret-ultra?s=us"],
        note="needs a Protect console between it and the Pi"),
    "axis_m3086v": dict(
        type="indoor mini dome", maker="Axis", model="M3086-V", short="Axis M3086-V (mini dome)",
        res_txt="2688 x 1512, 30 fps", px=(2688, 1512), lens_txt="2.4 mm", hfov=(130.0,), vfov=(93.0,),
        zoom_txt="none", ir_txt="none", poe_txt="af Class 2, 4.2 W (typ. 3.6)", w_max=4.2, w_typ=3.6,
        size_txt="Ø101 x 56 mm, 150 g", dia_mm=101.0, hang_mm=56.0, lens_drop_mm=35.0, h_up_mm=50.5,
        min_focus_mm=None, onvif_txt="G/M/S/T; local; cloud (O3C) can be off", ndaa_txt="yes (Axis)",
        price=462.99, vendor="CDW (backordered)",
        price_url="https://www.cdw.com/product/axis-m3086-v-network-surveillance-camera-dome/7058880",
        price_date="2026-11-20", price_kind="opened",
        src=["https://www.axis.com/dam/public/b2/9f/e9/datasheet-axis-m3086-v-dome-camera-en-US-555390.pdf"],
        note="P+-175/T+-80/R+-175 inside the dome; no true CBR (MBR with a fixed GOP)"),
    "hanwha_qne8011r": dict(
        type="turret", maker="Hanwha Vision", model="QNE-8011R", short="Hanwha QNE-8011R (turret)",
        res_txt="2592 x 1944, 30 fps", px=(2592, 1944), lens_txt="2.8 mm", hfov=(105.0,), vfov=(77.0,),
        zoom_txt="none", ir_txt="20 m, can be off", poe_txt="af Class 3, 7.4 W (typ. 5.5)", w_max=7.4, w_typ=5.5,
        size_txt="Ø125 x 87 mm, 645 g", dia_mm=125.0, hang_mm=87.4, lens_drop_mm=52.0, h_up_mm=62.5,
        min_focus_mm=None, onvif_txt="S/G/T; local; no P2P", ndaa_txt="yes (Hanwha)", price=388.78,
        vendor="a1securitycameras (CDW $377.99, snippet)",
        price_url="https://www.a1securitycameras.com/samsung-hanwha-qne-8011r-5mp-h-265-ir-outdoor-turret-ip-security-camera-with-2-8mm-fixed-lens.html",
        price_date="2026-11-20", price_kind="opened",
        src=["https://hvsgmpprdstorage.blob.core.windows.net/pim/QNE-8011R/DataSheet_QNE-8011R_20261116_EN_193649.pdf"],
        note="P350/T75/R360; CBR with GOV length"),
    "reolink_510a": dict(
        type="mini bullet", maker="Reolink", model="RLC-510A", short="Reolink RLC-510A (bullet)",
        res_txt="2560 x 1920, 25 fps", px=(2560, 1920), lens_txt="4 mm", hfov=(80.0,), vfov=(42.0,), zoom_txt="none",
        ir_txt="30 m", poe_txt="af; < 12 W (DC figure)", w_max=12.0, w_typ=None, size_txt="186 x Ø67 mm, 415 g",
        dia_mm=67.0, hang_mm=_b(186, 67)[0], lens_drop_mm=80.0, h_up_mm=_b(186, 67)[1], min_focus_mm=None,
        onvif_txt="ONVIF (enable it); RTSP; H.264 only", ndaa_txt="yes (as Reolink above)", price=59.99,
        vendor="reolink.com", price_url="https://reolink.com/us/product/rlc-510a/", price_date="2026-11-20",
        price_kind="opened", src=["https://reolink.com/us/product/rlc-510a/"], note=""),
    "axis_m2036le": dict(
        type="mini bullet", maker="Axis", model="M2036-LE", short="Axis M2036-LE (bullet)",
        res_txt="2688 x 1512, 30 fps", px=(2688, 1512), lens_txt="2.4 mm", hfov=(130.0,), vfov=(71.0,),
        zoom_txt="none; focuses from 0.5 m", ir_txt="20 m, can be off", poe_txt="af Class 3, 12.95 W (typ. 5)",
        w_max=12.95, w_typ=5.0, size_txt="170 x Ø101 mm, 491 g", dia_mm=101.0, hang_mm=_b(170, 101)[0],
        lens_drop_mm=90.0, h_up_mm=_b(170, 101)[1], min_focus_mm=500.0, onvif_txt="G/M/S/T; local",
        ndaa_txt="yes (Axis)", price=539.99, vendor="CDW",
        price_url="https://www.cdw.com/product/axis-m2036-le-network-surveillance-camera-bullet/6900392",
        price_date="2026-11-20", price_kind="opened",
        src=["https://www.axis.com/dam/public/bc/50/1b/datasheet-axis-m2036-le-bullet-camera-en-US-555403.pdf"],
        note="TM2001 bracket included"),
    "reolink_811a": dict(
        type="varifocal bullet", maker="Reolink", model="RLC-811A", short="Reolink RLC-811A (5x bullet)",
        res_txt="3840 x 2160, 25 fps", px=(3840, 2160), lens_txt="2.7-13.5 mm", hfov=(105.0, 31.0), vfov=(55.0, 17.0),
        zoom_txt="5x, motorized", ir_txt="30 m", poe_txt="af; < 12 W (DC figure)", w_max=12.0, w_typ=None,
        size_txt="238 x 80 x 72 mm, 838 g", dia_mm=80.0, hang_mm=_b(238, 80)[0], lens_drop_mm=90.0,
        h_up_mm=_b(238, 80)[1], min_focus_mm=None, onvif_txt="ONVIF; RTSP; its 4K main stream is H.265 only",
        ndaa_txt="yes (as Reolink above)", price=97.99, vendor="reolink.com",
        price_url="https://reolink.com/us/product/rlc-811a/", price_date="2026-11-20", price_kind="opened",
        src=["https://reolink.com/us/product/rlc-811a/"], note="4K at <= 8 Mbit/s is under YouTube's 4K minimum"),
    "amcrest_vt1289": dict(
        type="varifocal turret", maker="Amcrest (Dahua-made)", model="IP5M-VT1289EW-AI",
        short="Amcrest IP5M-VT1289EW (5x turret)", res_txt="2592 x 1944, 20 fps", px=(2592, 1944),
        lens_txt="2.7-13.5 mm", hfov=(100.0, 30.0), vfov=(72.0, 23.0), zoom_txt="5x, motorized; focuses from 0.8 m",
        ir_txt="40 m", poe_txt="af, 6.4 W", w_max=6.4, w_typ=4.2, size_txt="Ø122 x 108 mm, 685 g", dia_mm=122.0,
        hang_mm=108.3, lens_drop_mm=65.0, h_up_mm=61.0, min_focus_mm=800.0, onvif_txt="ONVIF not listed; RTSP",
        ndaa_txt="**no**: Dahua-made", price=154.99, vendor="amcrest.com (snippet)",
        price_url="https://amcrest.com/new-products/color/white.html", price_date="2026-11-20", price_kind="snippet",
        src=["https://support.amcrest.com/hc/en-us/articles/17236607643917"], note=""),
    "axis_m4216lv": dict(
        type="varifocal dome", maker="Axis", model="M4216-LV", short="Axis M4216-LV (2x dome)",
        res_txt="2304 x 1728, 30 fps", px=(2304, 1728), lens_txt="3-6 mm", hfov=(100.0, 45.0), vfov=(72.0, 34.0),
        zoom_txt="2x, remote zoom and focus", ir_txt="20 m, can be off", poe_txt="af Class 3, 9.7 W (typ. 5)",
        w_max=9.7, w_typ=5.0, size_txt="Ø121 x 71 mm, 375 g", dia_mm=121.0, hang_mm=71.0, lens_drop_mm=42.0,
        h_up_mm=60.5, min_focus_mm=None, onvif_txt="G/M/S/T; local", ndaa_txt="yes (Axis)", price=649.99,
        vendor="CDW", price_url="https://www.cdw.com/product/axis-m4216-lv-4mp-network-dome-camera/6771472",
        price_date="2026-11-20", price_kind="opened",
        src=["https://www.axis.com/dam/public/ca/74/e4/datasheet-axis-m4216-lv-dome-camera-en-US-490176.pdf"],
        note="P+-180/T-40..+65/R+-105"),
    "axis_m1137": dict(
        type="box (CS mount)", maker="Axis", model="M1137 Mk II", short="Axis M1137 Mk II (box)",
        res_txt="2592 x 1944, 30 fps", px=(2592, 1944), lens_txt="2.8-13 mm (i-CS 3.5-10 mm)", hfov=(112.0, 24.0),
        vfov=(82.0, 19.0), zoom_txt="4.6x by hand (i-CS: 2.9x, remote); focuses from 0.8 m", ir_txt="none",
        poe_txt="af Class 3, 7.2 W (typ. 4.5)", w_max=7.2, w_typ=4.5, size_txt="64 x 70 x 179 mm, 205 g",
        dia_mm=70.0, hang_mm=_b(179, 70)[0], lens_drop_mm=80.0, h_up_mm=_b(179, 70)[1], min_focus_mm=800.0,
        onvif_txt="G/M/S/T; local; 1/4-20 thread", ndaa_txt="yes (Axis)", price=657.0,
        vendor="networkdevicesinc (i-CS $803.99 at CDW)", price_url="https://networkdevicesinc.com/products/02484-001",
        price_date="2026-11-20", price_kind="opened",
        src=["https://www.axis.com/dam/public/2c/1e/98/datasheet-axis-m1137-mk-ii-box-camera-en-US-504528.pdf"],
        note="10-28 V DC too"),
    "axis_p1385": dict(
        type="box (CS mount)", maker="Axis", model="P1385", short="Axis P1385 (box)", res_txt="1920 x 1080, 60 fps",
        px=(1920, 1080), lens_txt="2.8-13 mm", hfov=(121.0, 26.0), vfov=(64.0, 15.0), zoom_txt="4.6x by hand",
        ir_txt="none", poe_txt="af Class 3, 9.3 W", w_max=9.31, w_typ=2.97, size_txt="480 g (drawing only)",
        dia_mm=75.0, hang_mm=None, lens_drop_mm=80.0, h_up_mm=None, min_focus_mm=None,
        onvif_txt="G/M/S/T; local; 1/4-20 thread", ndaa_txt="yes (Axis)", price=958.99, vendor="CDW",
        price_url="https://www.cdw.com/product/axis-p13-series-p1385-network-surveillance-camera-box/8066983",
        price_date="2026-11-20", price_kind="opened",
        src=["https://www.axis.com/dam/public/26/55/ff/datasheet-axis-p1385-box-camera-en-US-518378.pdf"], note=""),
    "axis_f2105": dict(
        type="sensor on a cable", maker="Axis", model="F9111-R Mk II + F2105-RE + 8 m cable",
        short="Axis F2105-RE sensor (F-series)", res_txt="1920 x 1080, 60 fps", px=(1920, 1080), lens_txt="3.1 mm",
        hfov=(108.0,), vfov=(58.0,), zoom_txt="none", ir_txt="none", poe_txt="at Class 4, 25.5 W (main unit)",
        w_max=25.5, w_typ=8.6, size_txt="sensor Ø30 x 46 mm, 50 g; main unit 675 g", dia_mm=30.0, hang_mm=46.0,
        lens_drop_mm=10.0, h_up_mm=15.0, min_focus_mm=None, onvif_txt="G/M/S/T; local", ndaa_txt="yes (Axis)",
        price=1033.97, vendor="CDW (main unit + sensor + cable)",
        price_url="https://www.cdw.com/product/axis-f-series-f9111-r-mk-ii-video-server-1-channels/8334770",
        price_date="2026-11-20", price_kind="opened",
        src=["https://www.axis.com/dam/public/a4/c1/17/datasheet-axis-f2105-re-standard-sensor-en-US-504514.pdf"],
        note="the main unit can live off the tray's floor, the sensor anywhere within 8 m"),
    "axis_p1275": dict(
        type="mini dome on a cable", maker="Axis", model="P1275 Mk II", short="Axis P1275 Mk II (on a cable)",
        res_txt="1920 x 1080, 30 fps", px=(1920, 1080), lens_txt="2.8-6 mm, by hand", hfov=(99.0, 53.0),
        vfov=(53.0, 30.0), zoom_txt="2x by hand; focuses from 0.1 m", ir_txt="none", poe_txt="af Class 2, 4.1 W",
        w_max=4.1, w_typ=3.4, size_txt="sensor unit 112 g (drawing only), on 8 m", dia_mm=None, hang_mm=None,
        lens_drop_mm=None, h_up_mm=None, min_focus_mm=100.0, onvif_txt="G/M/S/T; local", ndaa_txt="yes (Axis)",
        price=532.0, vendor="networkdevicesinc (backorder)", price_url="https://networkdevicesinc.com/products/02859-001",
        price_date="2026-11-20", price_kind="opened",
        src=["https://www.axis.com/dam/public/aa/f2/93/datasheet-axis-p1275-mk-ii-modular-varifocal-dome-camera-en-US-441939.pdf"],
        note="P360/T0-90/R360"),
    "axis_p1265": dict(
        type="pinhole on a cable", maker="Axis", model="P1265 Mk II", short="Axis P1265 Mk II (pinhole)",
        res_txt="1080p", px=(1920, 1080), lens_txt="3.7 mm", hfov=(91.0,), vfov=(45.0,),
        zoom_txt="none; focuses from 0.2 m", ir_txt="none", poe_txt="af Class 2", w_max=6.49, w_typ=None,
        size_txt="pinhole sensor on a cable", dia_mm=None, hang_mm=None, lens_drop_mm=None, h_up_mm=None,
        min_focus_mm=200.0, onvif_txt="G/M/S/T; local", ndaa_txt="yes (Axis)", price=499.99, vendor="CDW",
        price_url="https://www.cdw.com/", price_date="2026-11-20", price_kind="snippet", src=[], note="class 2 max"),
    "ccdcam_board": dict(
        type="IP board", maker="Shenzhen CCDCAM", model="IMA50L12 (IMX335)", short="CCDCAM IMA50L12 board",
        res_txt="2592 x 1944, 30 fps", px=(2592, 1944), lens_txt="M12, not included", hfov=(100.0,), vfov=(75.0,),
        zoom_txt="none", ir_txt="none (IR-cut only)", poe_txt="'DC12V/POE', 1.9 W", w_max=1.9, w_typ=None,
        size_txt="38 x 38 mm board", dia_mm=None, hang_mm=None, lens_drop_mm=None, h_up_mm=None, min_focus_mm=None,
        onvif_txt="'ONVIF 2.6'; RTSP; Danale P2P (firewall it)", ndaa_txt="unknown maker: get a declaration",
        price=17.05, vendor="Global Sources (snippet)",
        price_url="https://www.globalsources.com/product/network-camera-module_1200330767f.htm",
        price_date="2026-11-20", price_kind="snippet", src=["https://p.globalsources.com/IMAGES/PDT/SPEC/151/K1197603151.pdf"],
        note="the HQ Camera's 38 mm board size; a housing and lens are ours to add"),
    "mobotix_s74": dict(
        type="modular, with temperature", maker="Mobotix", model="S74 + 45° module + MultiSense",
        short="Mobotix S74 + MultiSense", res_txt="3840 x 2160, 30 fps", px=(3840, 2160), lens_txt="45° module",
        hfov=(45.0,), vfov=(25.3,), zoom_txt="none", ir_txt="optional module", poe_txt="at Class 4, 25 W", w_max=25.0,
        w_typ=None, size_txt="module Ø50 x 43 mm on 1-3 m; body 36 x 232 x 110 mm", dia_mm=50.0, hang_mm=42.5,
        lens_drop_mm=20.0, h_up_mm=25.0, min_focus_mm=None, onvif_txt="G/S/T; local",
        ndaa_txt="yes (Mobotix)", price=1628.0, vendor="a1 / VoIP Supply (parts, partly snippets)",
        price_url="https://www.a1securitycameras.com/mobotix-mx-f-msa.html", price_date="2026-11-20",
        price_kind="snippet", src=["https://www.mobotix.com/sites/default/files/2026-04/Mx_TS_S74_V2.72_EN_20260421.pdf"],
        note="temperature, not humidity; vertical angle ours (16:9)"),
}


PTZ = {
    "axis_m5075g": dict(
        type="mini PTZ", maker="Axis", model="M5075-G", short="Axis M5075-G (5x PTZ)",
        res_txt="1080p, 60 fps", px=(1920, 1080), lens_txt="2.2-11 mm", hfov=(71.0, 14.0), vfov=(40.0, 8.0),
        zoom_txt="5x, autofocus", ir_txt="none", poe_txt="af Class 3, 9.5 W (typ. 4.4)", w_max=9.5, w_typ=4.4,
        size_txt="Ø130 x 63 mm, 380 g", dia_mm=130.0, hang_mm=63.0, lens_drop_mm=40.0, h_up_mm=None,
        onvif_txt="G/M/S/T; local, cloud optional", ndaa_txt="allowed (Axis letter, 2024-12-19)",
        th_txt="no (device temperature events only)", min_focus_tele_mm=None,
        price=649.99, vendor="Newegg", price_url="https://www.newegg.com/p/N82E16881121781",
        price_date="2026-11-20", price_kind="snippet",
        src=["https://www.axis.com/dam/public/6e/44/d0/datasheet-axis-m5075-g-ptz-camera-en-US-555399.pdf",
             "https://www.axis.com/dam/public/permalink/253055/axis-ndaa-section-889-compliancepdf-en-US_253055.pdf"],
        note="indoor IP51; pan +-179 deg, tilt 90 deg, 100 deg/s; 256 presets; polygon privacy masks; microSD; "
             "AXIS M50 mounting kit included; CDW $819.99, MSRP $709 (snippets)"),
    "dahua_sd1a404": dict(
        type="mini PTZ", maker="Dahua", model="SD1A404XB-GNR (Amcrest IP4M-1066EW in the US)",
        short="Dahua SD1A404XB-GNR (4x PTZ)", res_txt="2560 x 1440, 30 fps", px=(2560, 1440), lens_txt="2.8-12 mm",
        hfov=(96.9, 31.6), vfov=(54.0, 17.8), zoom_txt="4x; focuses from 0.2-0.5 m", ir_txt="15 m",
        poe_txt="af, 8.5 W with IR (3 W without)", w_max=8.5, w_typ=3.0, size_txt="Ø128 x 65 mm, 485 g",
        dia_mm=128.0, hang_mm=65.0, lens_drop_mm=40.0, h_up_mm=None, onvif_txt="S/G/T; P2P listed",
        ndaa_txt="**not on federal funds** (Dahua)", th_txt="no", min_focus_tele_mm=500.0,
        price=289.99, vendor="Amcrest (IP4M-1066EW)",
        price_url="https://amcrest.com/4mp-poe-camera-ptz-4x-optical-zoom-ip4m-1066ew.html",
        price_date="2026-11-20", price_kind="snippet",
        src=["https://www.dahuasecurity.com/asset/upload/uploads/soft/20211015/DH-SD1A404XB-GNR_datasheet_20200605_DE_High.pdf",
             "https://ipvm.com/reports/dahua-oem"],
        note="outdoor IP66; pan 0-355, tilt 5-90; 300 presets; end of sale 2027-06-30 (eol.network, snippet); the "
             "vertical angles are 16:9 of the published horizontal ones (ours); no US price for the Dahua itself"),
    "hik_2a404": dict(
        type="mini PTZ", maker="Hikvision", model="DS-2DE2A404IW-DE3", short="Hikvision DS-2DE2A404IW-DE3 (4x PTZ)",
        res_txt="2560 x 1440, 25 fps", px=(2560, 1440), lens_txt="2.8-12 mm", hfov=(96.7, 31.6), vfov=(54.0, 17.8),
        zoom_txt="4x; focuses from 1.5 m at full zoom", ir_txt="20 m", poe_txt="af, 11.2 W with IR", w_max=11.2,
        size_txt="Ø131 x 102 mm, 530 g", dia_mm=131.0, hang_mm=102.0, lens_drop_mm=60.0, h_up_mm=None,
        onvif_txt="S/G/T", ndaa_txt="**not on federal funds** (Hikvision)", th_txt="no", min_focus_tele_mm=1500.0,
        price=242.99, vendor="IPSecurityDepot", price_url="https://ipsecuritydepot.com/Hikvision-DS-2DE2A404IW-DE3",
        price_date="2026-11-20", price_kind="snippet",
        src=["https://download.securityrussia.com/ru_datasheet_of_ds-2de2a404iw-de32.8-12mmc_v5.6.12.pdf"],
        note="marked discontinued on Hikvision's PH site (snippet)"),
    "reolink_823s2": dict(
        type="PTZ, 16x", maker="Reolink", model="RLC-823S2", short="Reolink RLC-823S2 (16x PTZ)",
        res_txt="3840 x 2160, 25 fps", px=(3840, 2160), lens_txt="5.3-86 mm", hfov=(54.2, 3.6), vfov=(30.5, 2.0),
        zoom_txt="16x; close focus not published", ir_txt="80 m", poe_txt="at, < 24 W", w_max=24.0,
        size_txt="373 x 177 x 140 mm with its mount, 2.3 kg", dia_mm=177.0, hang_mm=140.0, lens_drop_mm=90.0,
        h_up_mm=None, onvif_txt="ONVIF (profile not stated); P2P can be turned off",
        ndaa_txt="allowed (not a named company; Reolink's own statement)", th_txt="no", min_focus_tele_mm=None,
        price=339.99, vendor="Amazon (list; $230-259 on sale)", price_url="https://reolink.com/us/product/rlc-823s2/",
        price_date="2026-11-20", price_kind="snippet", src=["https://reolink.com/us/product/rlc-823s2/"],
        note="outdoor IP66; too tall for the band and too wide for the strip"),
    "reolink_trackmix": dict(
        type="dual-lens tracker", maker="Reolink", model="TrackMix PoE", short="Reolink TrackMix PoE (wide + tele)",
        res_txt="3840 x 2160, 25 fps", px=(3840, 2160), lens_txt="2.8 + 8 mm, fixed", hfov=(104.0, 38.0),
        vfov=(55.0, 21.0), zoom_txt="none (two fixed lenses, '6x hybrid')", ir_txt="30 m", poe_txt="af, < 12 W",
        w_max=12.0, size_txt="228 x 147 x 110 mm, 1.21 kg", dia_mm=147.0, hang_mm=110.0, lens_drop_mm=70.0,
        h_up_mm=None, onvif_txt="ONVIF; P2P can be turned off", ndaa_txt="allowed (as Reolink above)", th_txt="no",
        min_focus_tele_mm=None, price=199.99, vendor="Reolink store",
        price_url="https://reolink.com/us/product/reolink-trackmix-poe/", price_date="2026-11-20",
        price_kind="snippet", src=["https://reolink.com/us/product/reolink-trackmix-poe/"],
        note="the pair in one body, but with no optical zoom"),
    "axis_m5000g": dict(
        type="overview + PTZ", maker="Axis", model="M5000-G", short="Axis M5000-G (360° + 10x PTZ)",
        res_txt="PTZ 1080p; overview 3 x 5 MP", px=(1920, 1080), lens_txt="4.7-47 mm", hfov=(61.8, 6.7),
        vfov=(36.0, 3.8), zoom_txt="10x", ir_txt="none", poe_txt="at Class 4, 13.4 W", w_max=13.4,
        size_txt="Ø247 x 138 mm, 1.95 kg", dia_mm=247.0, hang_mm=138.0, lens_drop_mm=90.0, h_up_mm=None,
        onvif_txt="G/M/S/T; local", ndaa_txt="allowed (Axis letter)", th_txt="no", min_focus_tele_mm=None,
        price=1455.99, vendor="CDW",
        price_url="https://www.cdw.com/product/axis-m50-series-m5000-g-network-surveillance-panoramic-camera-dome/9030103",
        price_date="2026-11-20", price_kind="snippet",
        src=["https://www.axis.com/dam/public/d7/f5/cd/datasheet-axis-m5000-g-ptz-camera-en-US-555401.pdf"],
        note="the pair in one dome; 138 mm tall: only if the roof is higher than assumed"),
    "ptzoptics_movese20": dict(
        type="conference PTZ", maker="PTZOptics", model="Move SE 20X", short="PTZOptics Move SE 20X",
        res_txt="1080p, 60 fps", px=(1920, 1080), lens_txt="4.42-88.5 mm", hfov=(60.7, 3.4), vfov=(34.1, 1.9),
        zoom_txt="20x; close focus not published", ir_txt="none", poe_txt="af (but 'max 18 W'): plan an at port",
        w_max=18.0, size_txt="169 x 142 x 164 mm, 1.4 kg", dia_mm=169.0, hang_mm=164.0, lens_drop_mm=100.0,
        h_up_mm=None, onvif_txt="ONVIF (profile not stated); RTSP, SRT, NDI", ndaa_txt="allowed (PTZOptics' claim)",
        th_txt="no", min_focus_tele_mm=None, price=1349.0, vendor="Best Buy / Newegg",
        price_url="https://www.bestbuy.com/product/ptzoptics-move-se-20x-grey-gray/J39HLS9JC2",
        price_date="2026-11-20", price_kind="snippet", src=["https://docs.ptzoptics.com/docs/cameras/move-se/technical-specs"],
        note="a broadcast camera, not a security one; too big for the band"),
    "sony_srga12": dict(
        type="conference PTZ", maker="Sony", model="SRG-A12", short="Sony SRG-A12 (12x, AI framing)",
        res_txt="2160p30 / 1080p60", px=(3840, 2160), lens_txt="4.4-52.8 mm", hfov=(70.0, 6.7), vfov=(39.4, 3.8),
        zoom_txt="12x; focuses from 0.4 m at full zoom", ir_txt="none", poe_txt="bt Class 8, 71.3 W", w_max=71.3,
        size_txt="157 x 184 x 200 mm, 2.0 kg", dia_mm=184.0, hang_mm=200.0, lens_drop_mm=120.0, h_up_mm=None,
        onvif_txt="no ONVIF (VISCA over IP, CGI); RTSP", ndaa_txt="no statement found", th_txt="no",
        min_focus_tele_mm=400.0, price=2284.95, vendor="Newegg", price_url="https://www.newegg.com/p/34G-005N-00012",
        price_date="2026-11-20", price_kind="snippet", src=["https://www.sony.jp/products/catalog/SPC_SRG-A12.pdf"],
        note="the only PTZ found that focuses closer than 0.5 m at full zoom; 90 W PoE++ or its own adapter"),
}

CANDIDATES = {**FIXED, **PTZ}

GEAR = {   # USD, one retailer each, seen 2026-11-20; "opened": the page itself; "snippet": a search result; "ours": estimate
    "pi5_4gb": dict(what="Raspberry Pi 5, 4 GB", price=110.0, vendor="Raspberry Pi list (product brief, Nov 2026); "
                    "PiShop $110", url="https://www.pishop.us/product/raspberry-pi-5-4gb/", kind="opened"),
    "pi5_8gb": dict(what="Raspberry Pi 5, 8 GB", price=175.0, vendor="Raspberry Pi list; PiShop $175",
                    url="https://www.pishop.us/product/raspberry-pi-5-8gb/", kind="opened"),
    "psu27": dict(what="Raspberry Pi 27 W USB-C supply", price=12.95, vendor="PiShop",
                  url="https://www.pishop.us/product/raspberry-pi-27w-usb-c-power-supply-black-us/", kind="opened"),
    "cooler": dict(what="Raspberry Pi Active Cooler", price=12.95, vendor="PiShop",
                   url="https://www.pishop.us/product/raspberry-pi-active-cooler/", kind="opened"),
    "poe_hat": dict(what="Waveshare PoE HAT (H), 802.3af/at, 5 V 5 A, isolated", price=21.99, vendor="Waveshare",
                    url="https://www.waveshare.com/poe-hat-h.htm", kind="opened"),
    "sd": dict(what="microSD, 64 GB high-endurance (SanDisk)", price=29.00, vendor="Staples",
               url="https://www.staples.com/sandisk-high-endurance-64gb-microsd-memory-card-with-adapter-class-10-uhs-i-v30-sdsqqnr-064g-gn6ia/product_IM1ZS3423",
               kind="snippet"),
    "hq": dict(what="Raspberry Pi HQ Camera", price=55.00, vendor="PiShop (out of stock)",
               url="https://www.pishop.us/product/raspberry-pi-hq-camera/", kind="opened"),
    "lens16": dict(what="Raspberry Pi 16 mm C-mount lens", price=62.50, vendor="PiShop",
                   url="https://www.pishop.us/product/16mm-telephoto-lens-for-raspberry-pi-hq-camera/", kind="opened"),
    "cm3w": dict(what="Raspberry Pi Camera Module 3 Wide", price=38.50, vendor="PiShop",
                 url="https://www.pishop.us/product/raspberry-pi-camera-module-3-wide/", kind="opened"),
    "ribbon": dict(what="camera ribbon, 300 mm", price=2.45, vendor="PiShop", url="https://www.pishop.us/", kind="opened"),
    "switch": dict(what="Ubiquiti USW-Lite-8-PoE (8 ports, 4 PoE+, 52 W)", price=109.0, vendor="Ubiquiti store",
                   url="https://store.ui.com/us/en/products/usw-lite-8-poe", kind="opened"),
    "post_mount": dict(what="2020 post, printed foot and head, T-nuts (the HQ/Wide unit's)", price=15.0,
                       vendor="ours", url="", kind="ours"),
    "plate": dict(what="printed plate for a camera's base on a 2020 slot or a module, T-nuts, screws", price=4.0,
                  vendor="ours", url="", kind="ours"),
    "patch": dict(what="Cat 6 patch lead, 1-3 m", price=5.0, vendor="ours", url="", kind="ours"),
    "pi_plate": dict(what="printed plate for the Pi 5 on the tray", price=3.0, vendor="ours", url="", kind="ours"),
    "_relay": dict(what="a Pi 5 relaying a tray's or a bay's cameras",
                   items=[("pi5_4gb", 1), ("cooler", 1), ("psu27", 1), ("sd", 1), ("pi_plate", 1), ("patch", 1)]),
    "_per_camera": dict(what="what each security camera needs besides itself",
                        items=[("plate", 1), ("patch", 1), ("sd", 1)]),
    "_pi_unit": dict(what="today's HQ/Wide unit, for comparison",
                     items=[("pi5_4gb", 1), ("cooler", 1), ("psu27", 1), ("sd", 1), ("hq", 1), ("lens16", 1),
                            ("cm3w", 1), ("ribbon", 2), ("post_mount", 1), ("patch", 1)]),
}

TIERS = {   # what each tier puts where; every tier keeps the Axis M5075-G as the PTZ (no budget mini PTZ fits the band)
    "A. NDAA: Hanwha turrets on the trays, Axis in the bay": dict(
        tray="hanwha_qne8011r", bay={"back_wide": "axis_m3086v", "back_ptz": "axis_m5075g", "front": "axis_m3086v",
                                     "top": "axis_m3086v"},
        extra=[("a PoE switch for each bay set (USW-Lite-8-PoE)", 2, 109.0)]),
    "B. NDAA, smallest: Axis mini domes everywhere (no IR on the trays)": dict(
        tray="axis_m3086v", bay={"back_wide": "axis_m3086v", "back_ptz": "axis_m5075g", "front": "axis_m3086v",
                                 "top": "axis_m3086v"},
        extra=[("a PoE switch for each bay set (USW-Lite-8-PoE)", 2, 109.0)]),
    "C. Low cost: Reolink turrets on the trays and the strip, Axis on the roof": dict(
        tray="reolink_520a", bay={"back_wide": "axis_m3086v", "back_ptz": "axis_m5075g", "front": "reolink_520a",
                                  "top": "axis_m3086v"},
        extra=[("a PoE switch for each bay set (USW-Lite-8-PoE)", 2, 109.0)]),
}
CHOICE = TIERS["A. NDAA: Hanwha turrets on the trays, Axis in the bay"]["bay"]
TRAY_CHOICES = ["hanwha_qne8011r", "axis_m3086v", "reolink_520a"]
FIG_FIT_KEYS = ["axis_m3086v", "unifi_g5turret", "axis_m4216lv", "hanwha_qne8011r", "amlink_t5171", "reolink_520a",
                "amcrest_t1179", "amcrest_vt1289", "axis_f2105", "reolink_510a", "axis_m2036le", "reolink_811a",
                "axis_m1137", "axis_m5075g", "dahua_sd1a404", "hik_2a404", "reolink_trackmix", "axis_m5000g",
                "reolink_823s2", "ptzoptics_movese20", "sony_srga12"]
STILL_TRAY_CAM = "hanwha_qne8011r"
STILL_CAM = [(1650.0, -3500.0, 1430.0), (-60.0, -1000.0, 1500.0), (0, 0, 1)]   # eye, look-at, up: front right


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
        else:
            yaws = np.arange(170.0, 191.0, 5.0) if spot.startswith("back") else (
                np.arange(-40.0, 1.0, 5.0) if c[0] > 0 else np.arange(0.0, 41.0, 5.0))
            tilts = np.arange(30.0, 86.0, 2.5)
            try:     # the most floor with at most 2 % of the picture on the room (people), else the least room
                yaw, tilt, cov, cov2, room = best_aim(c, hf, vf, yaws, tilts, room_max=ROOM_MAX)
            except TypeError:
                yaw, tilt, cov, cov2, room = least_room(c, hf, vf, yaws, tilts)
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
            ax.plot([ly, ly + s_ * dy], [lz, lz + s_ * dz], color=col, lw=0.6, alpha=0.45)
        by, bz = {"back_wide": (-150.0, -150.0), "back_ptz": (-40.0, -150.0), "front": (95.0, -150.0),
                  "top": (0.0, -150.0)}.get(spot, (0.0, -150.0))
        ax.plot([y, y + by], [z - cam["hang_mm"], z + bz + 26], color=MUTED, lw=0.6)
        ax.add_patch(Circle((y + by, z + bz), 26, color=INK, lw=0, zorder=5))
        ax.text(y + by, z + bz, str(n), color=SURF, ha="center", va="center", fontsize=8, fontweight="bold",
                zorder=6)
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
    ax.annotate(f"the band (blue): {BAND:.1f} mm, all a roof camera may hang over the tray", (-1250, ENV_Z + 30),
                (-1250, 1500), fontsize=8, color=INK, ha="center",
                arrowprops=dict(arrowstyle="->", color=INK2, lw=0.8))
    ax.text(-1040, ROOF_Z + 22, "assumed roof: the opening's clear height, 1829 mm", ha="center", fontsize=8, color=INK)
    ax.text(-1040, F1_Z + 95, "tray F1, stored over the opening (1950 mm)", ha="center", **txt)
    ax.text(FRONT_STRIP[0] - 10, 1000, "front strip: no goods\never pass under it", ha="right", **txt)
    ax.text(-1631, 1600, "UR10e elbow at its\nhighest near the strip", ha="right", va="bottom", **txt)
    ax.text(SHUTTER_Y + 18, 1350, "shutter", rotation=90, va="center", **txt)
    ax.text(-1650, 1840, "header", ha="right", **txt)
    ax.set_title("The bay in section (cameras 1-2 stand at x = -120 / +120 mm, 3 at +300, 4 at 0)", loc="left",
                 fontsize=10, color=INK)
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
    """out/security_cameras_fit.png: (a) how far each candidate hangs from the bay's roof, against the 95.5 mm band;
    (b) each fixed candidate's top on a tray post at the HQ/Wide head's pivot, against the trays' slot limits."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    import services as S
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED,
                         "ytick.color": INK2, "font.family": "DejaVu Sans"})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(16, 8.4), dpi=150, facecolor=SURF,
                                 gridspec_kw=dict(width_ratios=[1.15, 1], wspace=0.55))
    fig.subplots_adjust(left=0.17, right=0.97, top=0.83, bottom=0.08)
    moving = lambda c: len(c["hfov"]) > 1
    # (a) the roof
    ks = sorted([k for k in keys if cands[k].get("hang_mm")], key=lambda k: cands[k]["hang_mm"])
    for i, k in enumerate(ks):
        c = cands[k]
        h = c["hang_mm"]
        a1.barh(i, h, height=0.62, color=ORANGE if moving(c) else BLUE, lw=0)
        spare = BAND - h
        txt = (f"fits, {spare:.0f} mm spare" if spare >= 5 else f"at the limit ({spare:.1f} mm spare)" if spare >= 0
               else "front strip only")
        a1.text(h + 4, i, f"{h:.0f} mm  {txt}", va="center", fontsize=8, color=INK if spare >= 5 else CRIT)
    a1.axvline(BAND, color=CRIT, lw=1.0, ls="--")
    a1.text(BAND + 3, len(ks) - 0.2, f"the band: {BAND:.1f} mm", fontsize=8, color=CRIT, va="bottom")
    a1.set_yticks(range(len(ks)), [cands[k]["short"] for k in ks], fontsize=8)
    a1.set_xlim(0, 290)
    a1.set_xlabel("how far it hangs below the roof, mm (published height; a bullet or box camera on a bracket: ours)")
    a1.set_title("(a) Under the bay's roof: what may hang over the tray", loc="left", fontsize=10, color=INK)
    # (b) a tray post
    piv = V.T_FLOOR + S.CAM_H + S.TILT_AXIS[2]
    kb = sorted([k for k in keys if cands[k].get("h_up_mm") is not None], key=lambda k: cands[k]["h_up_mm"])
    lims = {}
    for t, h in head.items():
        lims.setdefault(h["highest_top_same_slot_mm"], []).append(t)
    tight = min(l for l in lims if l > 600)
    for i, k in enumerate(kb):
        c = cands[k]
        top = piv + c["h_up_mm"]
        a2.barh(i, c["h_up_mm"], left=piv, height=0.62, color=ORANGE if moving(c) else BLUE, lw=0)
        a2.text(top + 2, i, f"top {top:.0f} mm", va="center", fontsize=8, color=INK if top <= tight else CRIT)
    cur = max(max(h["camera_tops_mm"]) for h in head.values())
    for lim, trays in sorted(lims.items()):
        if lim < 600 or lim > 800:
            continue
        a2.axvline(lim, color=CRIT if lim == tight else MUTED, lw=1.0, ls="--")
        a2.text(lim + 1, len(kb) - 0.2 + (0.0 if lim == tight else 0.9), f"trays {''.join(sorted(trays))}: "
                f"<= {lim:.0f}", fontsize=8, color=CRIT if lim == tight else INK2, va="bottom")
    a2.axvline(cur, color=INK2, lw=0.8, ls=":")
    a2.text(cur - 1, -1.0, f"HQ/Wide heads today: up to {cur:.0f}", fontsize=8, color=INK2, ha="right")
    a2.set_yticks(range(len(kb)), [cands[k]["short"] for k in kb], fontsize=8)
    a2.set_xlim(piv - 5, 790)
    a2.set_ylim(-1.6, len(kb) + 0.9)
    a2.set_xlabel(f"over the tray's underside, mm: from the aim pivot ({piv:.0f}, the head's tilt axis) to the top")
    a2.set_title("(b) On a tray's 2020 post, aimed down: its top against the slot", loc="left", fontsize=10,
                 color=INK)
    for ax in (a1, a2):
        ax.set_facecolor(SURF)
        ax.grid(axis="x", color=GRID, lw=0.5)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    leg = [Line2D([0], [0], color=BLUE, lw=6), Line2D([0], [0], color=ORANGE, lw=6)]
    fig.legend(leg, ["fixed lens", "motorized zoom (PTZ or varifocal)"], loc="upper right", ncol=2, frameon=False,
               bbox_to_anchor=(0.97, 0.915), fontsize=9)
    fig.suptitle("Security cameras against the room they have: the bay's roof band and the trays' slots",
                 x=0.03, ha="left", fontsize=13, color=INK, y=0.975)
    fig.text(0.03, 0.925, "(a) Over the tray a roof camera has 95.5 mm (the roof assumed at 1829 mm, the goods' "
             "top plus Kardex's 20 mm at 1733.5); taller ones can only go in the front strip. (b) A turret or dome "
             "on the post's face rises half its base over its pivot, a bullet or box camera about half its length "
             "at 45 degrees (ours); past the red line, trays C, E, G, I and L need a 25 mm taller slot unless the "
             "camera is set lower.", fontsize=8.5, color=INK2, wrap=True)
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
    """A PTZ hanging from top_c, D across and H tall: a base disc and a dome under it, its lens looking along
    `look`."""
    import pyvista as pv
    look = np.asarray(look, float) / np.linalg.norm(look)
    down = np.array([0.0, 0.0, -1.0])
    rd = min(0.70 * H, 0.45 * D)                 # the dome's radius
    t = H - rd                                   # the base disc's thickness
    base = pv.Cylinder(center=top_c + down * t / 2, direction=down, radius=D / 2, height=t, resolution=64)
    dome_c = top_c + down * t
    dome = pv.Sphere(radius=rd, center=dome_c, theta_resolution=48, phi_resolution=48, start_phi=90, end_phi=180)
    lens = pv.Cylinder(center=dome_c + look * rd * 0.92, direction=look, radius=0.12 * D, height=0.12 * D,
                       resolution=32)
    return {"sec_white": [base, dome], "sec_black": [lens]}


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
                    {"back_wide": (0.03, 0.10), "back_ptz": (0.97, 0.05), "front": (0.97, 0.16),
                     "top": (0.16, 0.20)}[spot]))
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
                    (0.10 + 0.62 * i, 0.42)))
    sc.cam = list(STILL_CAM)
    sc.step("", f"Tray {k} at the opening with a {c['short']} on each of its two camera posts, where the HQ/Wide "
            "heads were. Under a roof assumed at the opening's top (drawn see-through): the pair at the middle back "
            "(an Axis M3086-V mini dome and the M5075-G PTZ, here turned to the CubXL's holder seat), a mini dome in "
            "the strip under the header looking back, and one looking straight down. Simple shapes at each model's "
            "published size.", 0.1, None, hold=0.0, labels=lbl, still=True)
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


# ===================================================================================================== the note's tables
def _md(rows, head) -> str:
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def tables(res: dict) -> dict:
    """The generated tables of notes/security_cameras.md, by marker."""
    C = res["candidates"]
    t = {}
    for which, keep in (("FIXED_TABLE", lambda c: "PTZ" not in c["type"] and "tracker" not in c["type"]
                          and "overview" not in c["type"]),
                         ("PTZ_CANDS_TABLE", lambda c: "PTZ" in c["type"] or "tracker" in c["type"]
                          or "overview" in c["type"])):
        rows = []
        for k, c in C.items():
            if not keep(c):
                continue
            fov = "-".join(f"{h:.0f}" for h in c["hfov"]) + " x " + "-".join(f"{v:.0f}" for v in c["vfov"]) + "°"
            rows.append((c["type"], f"{c['maker']} **{c['model']}**", c["res_txt"], f"{c['lens_txt']}; {fov}",
                         c.get("zoom_txt", "none"), c.get("ir_txt", "-"), c["poe_txt"], c["size_txt"],
                         c.get("onvif_txt", "-"), c.get("ndaa_txt", "-"), f"${c['price']:,.0f}",
                         f"[{c['vendor']}]({c['price_url']})" + (" (snippet)" if c.get("price_kind") == "snippet"
                                                                 else "")))
        t[which] = _md(rows, ["Type", "Model", "Resolution", "Lens; across x up", "Zoom, focus", "IR",
                              "PoE, most it draws", "Size", "ONVIF, RTSP, local", "On federal money", "Price",
                              "Seen 2026-11-20 at"])
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
                 "not published" if v["focus_ok"] is None else ("yes" if v["focus_ok"] else "**no**"))
                for name, v in ptz["tele"].items()]
        t["PTZ_TABLE"] = _md(rows, ["The PTZ at full zoom on", "Distance", "Picture across", "mm/px",
                                    "In focus at full zoom?"])
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
                     f"{p['poe_w']:.0f} W, {p['poe_ports']} port" + ("s" if p["poe_ports"] != 1 else ""), "yes" if p["ups_still_ok"] and p["poe_ok"]
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


if __name__ == "__main__":
    words = sys.argv[1:]
    res = run(arm="arm" in words)
    if "notes" in words:
        fill_notes(json.loads((OUT / "security_cameras.json").read_text()))
    if "still" in words:
        print(still(CHOICE, CANDIDATES, res["bay"], STILL_TRAY_CAM, "A"))
    for spot, r in res["bay"].items():
        print(spot, r["camera"], f"cover {r['floor_coverage']:.2f} / {r['coverage_300mm_up']:.2f}",
              f"room {r['room_share']:.2f}", f"low {r['lowest_point_mm']}", f"band {r['band_margin_mm']}",
              r.get("arm", {}).get("smallest_gap_mm"))
    for name, c in res["cost"].items():
        print(name, c.get("total"), c.get("per_tray_point", c.get("per_point")))
