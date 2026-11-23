"""Small things the workflow handles, and the robot's mobile base. PyVista primitives, millimetres, z up.

* The vial is the multi-doser's own: a 20 mL vial, 28 mm across and 61 mm tall (powder-doser
  ``cad/chain-carousel-v2/params.py``), with a powder fill and a liquid fill that the animation sets.
* The vial rack is a printed block like the CubXL's six-vial rack (``lab_models/equipment.py``), sized for 28 mm vials.
* The MiR's intermediary storage is a low block on its cabinet top, beside the arm's mounting plate, with bored and
  chamfered pockets (``pocket_block``, ``buffer_holder``; ``charge.carrier`` for the charge cups): no post.
* The mobile base is a **MiR250** (Mobile Industrial Robots, the AMR sold with UR arms): 800 x 580 x 300 mm
  (MiR250 data sheet), with a top cabinet that holds the UR control box (e-Series control box 460 x 449 x 254 mm,
  UR data sheet), so the arm's base sits at ``AMR_TOP``. The cabinet's height is a layout choice: it puts the
  arm's base 80 mm under the opening's counter, so the arm reaches over the counter and down onto the tray.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
import pyvista as pv

VIAL_R, VIAL_H = 14.0, 61.0                  # 20 mL vial (powder-doser chain-carousel-v2 params: 28 x 61 mm)
VIAL_WALL, VIAL_FLOOR = 1.2, 2.5
GLASS = (0.62, 0.78, 0.90)
POWDER = (0.33, 0.33, 0.36)                  # a grey metal powder (Al 4047, Si: the alloy lab's powders)
LIQUID = (0.25, 0.50, 0.85)
RACK_C = (0.94, 0.94, 0.92)

MIR = dict(L=800.0, W=580.0, H=300.0)        # MiR250: 800 x 580 x 300 mm
CAB_H = 480.0                                # top cabinet with the UR control box (layout choice, see above)
AMR_TOP = MIR["H"] + CAB_H + 20.0            # arm base height above the floor (20 mm mounting plate)
MIR_ACCEL = 300.0                            # mm/s^2: the MiR250 speeds up and slows down at 0.3 m/s^2 at full
#                                              payload; its top speed is 2.0 m/s (MiR250 spec sheet, Hartfiel's copy)


# ------------------------------------------------------------------------------------------------- the drives
# From PR #321 (claude/issue-303-r5-fixes, a34367a), brought over in round 8. A MiR250 drive from rest to rest: up to
# speed at MIR_ACCEL, on at vmax, down again. A trapezoid in speed, or a triangle when the drive is too short to reach
# vmax: at 0.3 m/s^2 it takes 7.5 m to reach 1.5 m/s and stop again, so along the line it never does. Scene.step eases
# its u; drive with ramp_frac(unease(u), ...) to keep this profile instead.
def unease(e: float) -> float:
    """The inverse of scene.ease: the step's own time (0-1) for the eased u that Scene.step passes, for a motion that
    keeps a profile of its own (a MiR250's drive, ramp_frac). (#321 put this in scene.py.)"""
    e = min(max(e, 0.0), 1.0)
    return 0.5 - math.sin(math.asin(1.0 - 2.0 * e) / 3.0)


def ramp_secs(dist: float, vmax: float, accel: float = MIR_ACCEL) -> float:
    """Seconds for a drive of `dist` (mm, or deg with a deg/s^2 accel) from rest to rest."""
    d = abs(dist)
    if d * accel <= vmax * vmax:
        return 2.0 * math.sqrt(d / accel)
    return d / vmax + vmax / accel


def ramp_peak(dist: float, vmax: float, accel: float = MIR_ACCEL) -> float:
    """The top speed that drive reaches: vmax, or less on a short one."""
    return min(vmax, math.sqrt(abs(dist) * accel))


def ramp_frac(u: float, dist: float, vmax: float, accel: float = MIR_ACCEL) -> float:
    """The share of that drive covered at u (0-1) of its time; spread over a longer step, it is slower all through."""
    d = abs(dist)
    if d < 1e-9:
        return 1.0
    T = ramp_secs(d, vmax, accel)
    t = min(max(u, 0.0), 1.0) * T
    v = ramp_peak(d, vmax, accel)
    ta = v / accel                                  # time to reach the top speed
    if t <= ta:
        s = 0.5 * accel * t * t
    elif t >= T - ta:
        s = d - 0.5 * accel * (T - t) ** 2
    else:
        s = 0.5 * accel * ta * ta + v * (t - ta)
    return min(1.0, max(0.0, s / d))


def s_curve(x0, y0, x1, y1, n=201):
    """A MiR250's drive from (x0, y0) to (x1, y1) that also changes lanes: x even in p, y on a smoothstep, its long axis
    on the tangent (it is differential drive, so it can't slide sideways). Returns (at, ps, s): at(p) -> (x, y, heading
    in degrees) and the path's length s at each of ps, to drive it with ramp_frac by length."""
    def at(p):
        x = x0 + (x1 - x0) * p
        y = y0 + (y1 - y0) * (3 * p * p - 2 * p ** 3)
        dydx = (y1 - y0) * (6 * p - 6 * p * p) / (x1 - x0) if abs(x1 - x0) > 1 else 0.0
        return x, y, math.degrees(math.atan(dydx))
    ps = np.linspace(0.0, 1.0, n)
    xy = np.array([at(q)[:2] for q in ps])
    return at, ps, np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(xy, axis=0), axis=1))]


def _cyl(r, h, z0=0.0, x=0.0, y=0.0, res=40):
    return pv.Cylinder(center=(x, y, z0 + h / 2), direction=(0, 0, 1), radius=r, height=h, resolution=res).triangulate()


def vial_glass() -> pv.PolyData:
    """Open 20 mL vial, base centre at the origin: a thin wall and floor, the neck's thread band."""
    outer = _cyl(VIAL_R, VIAL_H)
    neck = pv.Cylinder(center=(0, 0, VIAL_H - 5), direction=(0, 0, 1), radius=VIAL_R + 0.6, height=8,
                       resolution=40).triangulate()
    return outer.merge(neck)


def fill(level_mm: float, r: float = VIAL_R - VIAL_WALL) -> pv.PolyData:
    """A fill of unit height (the animation scales z), from the vial's floor."""
    return _cyl(r, 1.0, 0.0, res=32)


def vial_rack(n: int = 6, pitch: float = 34.0) -> tuple[pv.PolyData, list[tuple[float, float, float]]]:
    """A printed rack: n holes in a row along x, 32 mm deep. Returns the mesh and the vial seats (base centres)."""
    w = n * pitch + 16
    block = pv.Box(bounds=(-w / 2, w / 2, -26, 26, 0, 40)).triangulate()
    seats = [(-w / 2 + 8 + pitch * (i + 0.5), 0.0, 8.0) for i in range(n)]
    return block, seats


def mir250() -> dict[str, tuple[pv.PolyData, tuple]]:
    """MiR250 body, its status-light band, the top cabinet and the arm's mounting plate; origin on the floor at the
    centre of the footprint, long side along x, the arm mounted over the front (-y) half."""
    L, W, H = MIR["L"], MIR["W"], MIR["H"]
    body = pv.Box(bounds=(-L / 2, L / 2, -W / 2, W / 2, 30, H - 20)).triangulate()
    cover = pv.Box(bounds=(-L / 2 + 10, L / 2 - 10, -W / 2 + 10, W / 2 - 10, H - 20, H)).triangulate()
    band = pv.Box(bounds=(-L / 2 - 2, L / 2 + 2, -W / 2 - 2, W / 2 + 2, 60, 78)).triangulate()
    skirt = pv.Box(bounds=(-L / 2 + 20, L / 2 - 20, -W / 2 + 20, W / 2 - 20, 0, 30)).triangulate()
    cab = pv.Box(bounds=(-L / 2 + 40, L / 2 - 40, -W / 2 + 30, W / 2 - 30, H, H + CAB_H)).triangulate()
    plate = pv.Box(bounds=(-170, 170, -W / 2 + 30, W / 2 - 30, H + CAB_H, AMR_TOP)).triangulate()
    door = pv.Box(bounds=(-L / 2 + 70, L / 2 - 70, -W / 2 + 28, -W / 2 + 30, H + 40, H + CAB_H - 40)).triangulate()
    import safety
    if safety.CLASS_D_ON_MIR:      # the safety PR: the -y side carries the Class D unit, so the door is on the front end
        door = pv.Box(bounds=(L / 2 - 40, L / 2 - 38, -W / 2 + 70, W / 2 - 70, H + 40, H + CAB_H - 40)).triangulate()
    estop = pv.Cylinder(center=(L / 2 - 90, -W / 2 + 60, AMR_TOP + 15), direction=(0, 0, 1), radius=20,
                        height=30).triangulate()
    parts = {
        "amr body": (body.merge(skirt), (0.22, 0.23, 0.25)),
        "amr cover": (cover, (0.80, 0.81, 0.83)),
        "amr light band": (band, (0.55, 0.85, 1.00)),
        "amr cabinet": (cab.merge(plate), (0.86, 0.87, 0.88)),
        "amr cabinet door": (door, (0.70, 0.72, 0.75)),
        "amr e-stop": (estop, (0.85, 0.12, 0.10)),
    }
    # the safety PR (Sterling, PR #318, 2026-11-20: "a class D fire extinguisher mounted at all times to the MiR250
    # and available for use"): the Amerex B570 in an 811 vehicle bracket on the cabinet (safety.py,
    # notes/safety.md); VLAB_MIR_CLASS_D=0 leaves it off
    import safety
    if safety.CLASS_D_ON_MIR:
        parts.update({f"amr {k}": v for k, v in safety.mir_meshes().items()})
    if BASE_CAMS_ON:                 # #364: the three base cameras, so every clip that draws a MiR250 draws them
        parts.update(base_camera_parts())
    return parts


# ------------------------------------------------------------------------------------------- the base cameras (#364)
# Sterling (PR #318, 2026-11-20): "we should probably add two or three cameras to the mobile manipulator (one on either
# side, one that's situated higher up, maybe on some kind of rod or extrusion, mimicking the three cameras described in
# robot-arms PR 40)". Robot-arms PR 40's cell (docs/issue-24/camera-fixtures and camera-literature): an overhead camera
# and two side cameras raised 350-500 mm that look at the arm's work from 70-90 deg apart, each a Raspberry Pi Camera
# Module 3 Wide (102 x 67 deg) with its own Pi 5 on its 2020 post, aimed by printed parts that never move. Here, on each
# MiR250 (the arm faces +y, the station side; MiR frame as mir250()):
#   L, R  a short 2020 post clamped to each end of the cabinet, the Wide in PR 40's printed case on a wedge on top, 0.88 m
#         off the floor, turned a little in and up at the arm's work in front of the base; its Pi 5 on the cabinet's
#         end under the top, where no arm goes, on a 300 mm cable;
#   M     the mast: a 2040 extrusion clamped to the cabinet's left end at the base's back-left corner, a printed box on
#         top (the Wide in front, its Pi 5 behind) at 1.75-1.80 m (the MiR250's own 3D cameras watch up to 1.8 m),
#         looking forward and down over the arm.
# Where (posts, heights, aims) comes from base_cams_sweep.py: every arm's frames in every clip, swept in the MiR's
# frame. Nothing on an 800 x 580 base is out of a UR10e's reach, and in the clips the arm passes over every part of the
# cabinet's rim between about 1.0 and 2.0 m; these are the places it passes least (notes/base_cameras.md).
# Two chapters' moves were planned before the mast and go through where it stands (#364's audits, at 15 fps: chapter 2
# 139 -> 184 frames in collision, 45 of them the arm on a camera; chapter 4 4 -> 361, a swing round the base's back-left
# corner that the chapter's own IK-branch search can't re-plan). Until they are re-planned with the cameras in the
# scene, a run of either script leaves the cameras out unless VLAB_BASE_CAMS says otherwise; take a script off this
# list once its audit with the cameras is clean. VLAB_BASE_CAMS=0 / 1 forces them off / on for any clip.
# round 15 (PR #318, 2026-11-23: "re-render everything in a self-consistent and cohesive way"): every clip draws
# them; chapters 2 and 6 are re-planned with the cameras in the scene, so the list is empty
BASE_CAMS_OPT_OUT: set[str] = set()
BASE_CAMS_ON = os.environ.get("VLAB_BASE_CAMS", "0" if os.path.basename(sys.argv[0] if sys.argv else "") in
                              BASE_CAMS_OPT_OUT else "1") != "0"
CM3W = dict(hfov=102.0, vfov=67.0, dfov=120.0, px=(4608, 2592))           # raspberrypi.com, Camera Module 3 Wide
BOX = dict(w=68.0, h=96.0, d=46.0, lens_d=9.0, lens_out=3.0, lens_up=26.0)  # printed box, portrait: the Wide near
#   the top of its front face, the Pi 5 (85 x 56) standing behind it; w across the picture, h up it, d along the view
CASE = dict(w=49.0, h=29.5, d=8.6, lens_d=7.0, lens_out=4.0)   # robot-arms PR 40's cam_case for the Wide, 49 x 29.5 x 8.6
PI_CASE = dict(along=92.0, up=64.0, t=30.0)                    # a Pi 5 + Active Cooler in a vented printed case
CAB_X, CAB_Y = MIR["L"] / 2 - 40.0, MIR["W"] / 2 - 30.0       # the cabinet's half-length (360) and half-width (260)
CAB_TOP = MIR["H"] + CAB_H                                    # 780
BASE_CAMS = {
    # post: the extrusion's centre (x, y), its section (along x, along y) and its z range (the box sits on its top);
    # aim: the point the camera's axis passes through (MiR frame). A scan of 58 spots and heights against every
    # recorded frame of 17 clips (base_cams_sweep.py): just behind the middle of each end under 0.9 m, and the
    # back-left corner for the mast, are where the arms pass least (notes/base_cameras.md, "Where the arms go")
    # kind "case": only the camera in its case on the post's top, its Pi 5 on the cabinet's end face below the top,
    # on a 300 mm cable (#364's first audits: the arms' held parts pass where a whole camera-and-Pi box stood)
    # L at y = -60, as R: on the left end, at the case's height, chapter 2's tong sleeve (alloy_atomize.TONG_AT, y = 0)
    # and the vial holder (animate.BUFFER_LOCAL, y = -150) leave a gap only 10 mm wide between the open gripper's
    # reaches (y -70 and -80); here only the tong's grasp touches (notes/base_cameras.md)
    "L": dict(what="left side camera", post=(-(CAB_X + 11.0), -60.0), sec=(20.0, 20.0), z=(560.0, 845.0),
              aim=(-250.0, 800.0, 1000.0), kind="case"),
    "R": dict(what="right side camera", post=(CAB_X + 11.0, -60.0), sec=(20.0, 20.0), z=(560.0, 845.0),
              aim=(250.0, 800.0, 1000.0), kind="case"),
    "M": dict(what="mast camera", post=(-(MIR["L"] / 2 - 14.0), -(MIR["W"] / 2 - 24.0)), sec=(20.0, 40.0),
              z=(330.0, 1690.0), aim=(80.0, 850.0, 950.0), kind="box"),
}
CAM_COLOURS = dict(alu=(0.78, 0.79, 0.81), petg=(0.10, 0.10, 0.11), lens=(0.05, 0.07, 0.12), cable=(0.04, 0.04, 0.04))


def _cam_frame(lens, aim) -> np.ndarray:
    """4x4: the camera's frame at its lens, z along the view (from lens to aim), x to the picture's right, y down."""
    f = np.asarray(aim, float) - np.asarray(lens, float)
    f /= np.linalg.norm(f)
    r = np.cross(f, (0.0, 0.0, 1.0))
    r /= np.linalg.norm(r)
    d = np.cross(f, r)                              # the picture's down
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = r, d, f, lens
    return M


def _obox(M, x0, x1, y0, y1, z0, z1) -> pv.PolyData:
    """A box given in a frame M (4x4), as PolyData in M's parent frame."""
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1)).triangulate().transform(M, inplace=False)


def base_camera_geometry(key: str) -> dict:
    """One base camera, MiR frame: {"post", "box", "lens", "cable": PolyData, "frame": 4x4 at the lens (z the view,
    x the picture's right, y its down), "top": the highest point, "box_centre": xyz}."""
    c = BASE_CAMS[key]
    px, py = c["post"]
    sx, sy = c["sec"]
    z0, z1 = c["z"]
    side = 1.0 if px > 0 else -1.0
    post = pv.Box(bounds=(px - sx / 2, px + sx / 2, py - sy / 2, py + sy / 2, z0, z1)).triangulate()
    # two printed clamps wrap the extrusion and screw to the cabinet's end face (x = +-CAB_X)
    for zc in (z0 + 30.0, min(z1, CAB_TOP) - 40.0):
        x_in, x_out = side * (CAB_X - 2.0), px + side * (sx / 2 + 3.0)
        post = post.merge(pv.Box(bounds=(min(x_in, x_out), max(x_in, x_out), py - sy / 2 - 3, py + sy / 2 + 3,
                                         zc - 20, zc + 20)).triangulate())
    if c.get("kind") == "case":
        return _case_camera(c, post, side)
    # the camera box: a printed wedge on the post's top sets its yaw and pitch for good; the box sits on the wedge, moved
    # inboard as far as it takes to stay inside the MiR250's footprint (2 mm in), the Wide near the top of its front face
    w, h, d = BOX["w"], BOX["h"], BOX["d"]
    seat = np.array([px, py, z1 + 12.0])                      # the wedge's top, over the post's axis
    F0 = _cam_frame(seat, c["aim"])
    centre = seat - F0[:3, 1] * (h / 2 + 2.0)                 # y is the picture's down: the box stands on the wedge
    for _ in range(3):
        Fc = _cam_frame(centre, c["aim"])
        b = _obox(Fc, -w / 2, w / 2, -h / 2, h / 2, -d / 2, d / 2).bounds
        lim = (MIR["L"] / 2 - 2.0, MIR["W"] / 2 - 2.0)
        centre = centre + np.array([min(0.0, lim[0] - b[1]) + max(0.0, -lim[0] - b[0]),
                                    min(0.0, lim[1] - b[3]) + max(0.0, -lim[1] - b[2]), 0.0])
    Fc = _cam_frame(centre, c["aim"])
    up_off = -Fc[:3, 1] * (h / 2 - BOX["lens_up"])            # from the box's centre up to the lens's height
    lens = centre + up_off + Fc[:3, 2] * (d / 2 + BOX["lens_out"])
    Fr = _cam_frame(lens, c["aim"])
    box = _obox(Fc, -w / 2, w / 2, -h / 2, h / 2, -d / 2, d / 2)
    # the printed wedge: a cap on the extrusion's top and a neck from it to the middle of the box's back-bottom edge
    wedge = pv.Box(bounds=(px - sx / 2 - 3, px + sx / 2 + 3, py - sy / 2 - 3, py + sy / 2 + 3, z1, z1 + 12.0)).triangulate()
    heel = centre - Fc[:3, 2] * (d / 2 - 8.0) + Fc[:3, 1] * (h / 2 - 8.0)
    wedge = wedge.merge(pv.Line((px, py, z1 + 6.0), heel).tube(radius=9.0, n_sides=12).triangulate())
    barrel = pv.Cylinder(center=tuple(centre + up_off + Fc[:3, 2] * (d / 2 + BOX["lens_out"] / 2)),
                         direction=tuple(Fc[:3, 2]), radius=BOX["lens_d"] / 2, height=BOX["lens_out"],
                         resolution=24).triangulate()
    # its PoE lead: out of the box's back, down inside the extrusion's outboard T-slot (flush), and in through the
    # cabinet's end below its top, where no arm goes
    xo = px + side * (sx / 2 - 2.6)
    run = [centre - Fc[:3, 2] * (d / 2) + Fc[:3, 1] * (h / 2 - 10.0), (px, py, z1 + 6.0), (xo, py, z1 - 4.0),
           (xo, py, CAB_TOP - 120.0), (side * (CAB_X - 6.0), py, CAB_TOP - 120.0)]
    cable = pv.merge([pv.Line(run[i], run[i + 1]).tube(radius=2.6, n_sides=10) for i in range(len(run) - 1)]).triangulate()
    out = dict(post=post, box=box.merge(wedge), lens=barrel, cable=cable, frame=Fr, box_centre=centre)
    out["top"] = max(float(m.bounds[5]) for m in (out["post"], out["box"], out["lens"]))
    return out


def _case_camera(c: dict, post: pv.PolyData, side: float) -> dict:
    """A side camera as robot-arms PR 40 builds one: the Wide in its printed case on a wedge on the post's top, the
    wedge's faces cut to the aim; its Pi 5 on the cabinet's end face, 30 mm under the top, behind the post; the
    ribbon down the post's outboard slot to it, and the Pi's PoE lead through the end into the cabinet."""
    px, py = c["post"]
    sx, sy = c["sec"]
    z0, z1 = c["z"]
    w, h, d = CASE["w"], CASE["h"], CASE["d"]
    wedge = pv.Box(bounds=(px - 14, px + 14, py - 14, py + 14, z1, z1 + 18.0)).triangulate()
    seat = np.array([px, py, z1 + 18.0])
    F0 = _cam_frame(seat, c["aim"])
    centre = seat - F0[:3, 1] * (h / 2 + 1.0)
    Fc = _cam_frame(centre, c["aim"])
    case = _obox(Fc, -w / 2, w / 2, -h / 2, h / 2, -d / 2, d / 2)
    lens = centre + Fc[:3, 2] * (d / 2 + CASE["lens_out"])
    barrel = pv.Cylinder(center=tuple(centre + Fc[:3, 2] * (d / 2 + CASE["lens_out"] / 2)), direction=tuple(Fc[:3, 2]),
                         radius=CASE["lens_d"] / 2, height=CASE["lens_out"], resolution=24).triangulate()
    pa, pu, pt = PI_CASE["along"], PI_CASE["up"], PI_CASE["t"]
    y1 = py - sy / 2 - 8.0
    zt = CAB_TOP - 30.0
    x_in = side * CAB_X
    pi = pv.Box(bounds=(min(x_in, x_in + side * pt), max(x_in, x_in + side * pt), y1 - pa, y1, zt - pu, zt)).triangulate()
    xo = px + side * (sx / 2 - 2.6)
    run = [centre - Fc[:3, 2] * (d / 2) + Fc[:3, 1] * (h / 2 - 4.0), (xo, py, z1 + 4.0), (xo, py, zt - 20.0),
           (side * (CAB_X + pt), y1 - 12.0, zt - 20.0)]
    ribbon = pv.merge([pv.Line(run[i], run[i + 1]).tube(radius=1.6, n_sides=8) for i in range(len(run) - 1)])
    lead = pv.Line((side * (CAB_X + pt / 2), y1 - pa + 10.0, zt - pu), (side * (CAB_X + 6.0), y1 - pa + 10.0, zt - pu - 40.0))
    cable = ribbon.merge(lead.tube(radius=2.6, n_sides=10)).triangulate()
    out = dict(post=post, box=case.merge(wedge), lens=barrel, cable=cable, pi=pi, frame=_cam_frame(lens, c["aim"]),
               box_centre=centre)
    out["top"] = max(float(m.bounds[5]) for m in (out["post"], out["box"], out["lens"]))
    return out


def base_camera_parts() -> dict[str, tuple[pv.PolyData, tuple]]:
    """The three cameras' meshes for mir250(): {"amr cam L post": (mesh, rgb), ...}, MiR frame."""
    out = {}
    for k in BASE_CAMS:
        g = base_camera_geometry(k)
        out[f"amr cam {k} post"] = (g["post"], CAM_COLOURS["alu"])
        out[f"amr cam {k} box"] = (g["box"], CAM_COLOURS["petg"])
        out[f"amr cam {k} lens"] = (g["lens"], CAM_COLOURS["lens"])
        out[f"amr cam {k} cable"] = (g["cable"], CAM_COLOURS["cable"])
        if "pi" in g:
            out[f"amr cam {k} pi"] = (g["pi"], CAM_COLOURS["petg"])
    return out


def base_camera_optics(key: str, Wm=None) -> dict:
    """Camera `key`'s optics (Wm: the MiR group's world 4x4; None: the MiR frame): eye, forward, up (the picture's
    up), right, and the Wide's fields of view."""
    g = base_camera_geometry(key)
    M = g["frame"] if Wm is None else np.asarray(Wm, float) @ g["frame"]
    return dict(eye=M[:3, 3].copy(), fwd=M[:3, 2].copy(), up=-M[:3, 1], right=M[:3, 0].copy(), hfov=CM3W["hfov"],
                vfov=CM3W["vfov"])


# The MiR's intermediary storage (byu-vcl PR #318, round 7). Sterling: "There's no insertion gap for the
# intermediary storage on the MiR250. They would just fall off. Also, it's positioned rather high ... Should probably be
# much lower / flush with the base." So it is a low block standing on the cabinet top beside the arm's mounting plate,
# no post, with real bored pockets: about 1 mm radial clearance, a 45 deg lead-in at the mouth, and deep enough (over
# 40 % of a vial's or a cup's height) that nothing tips out while the MiR drives. A printed or machined block; the
# sizes are layout choices, not a product.
DECK_H = 30.0                # the pocket block's height over the cabinet top, 10 mm over the mounting plate
DECK_FLOOR = 4.0             # under the pockets: the seats are this high in the block
DECK_DEPTH = DECK_H - DECK_FLOOR      # 26 mm: 43 % of the 61 mm vial, 41 % of the 63.5 mm charge cup
POCKET_CLEAR = 1.0           # radial clearance in a pocket
POCKET_LEAD = 3.0            # 45 deg chamfer at a pocket's mouth: the lead-in that guides a part in
HOLDER_H = DECK_H            # was the vial holder's 260 mm post; kept as a name for older callers


def _cq_mesh(shape, tol: float = 0.2) -> pv.PolyData:
    verts, tris = shape.tessellate(tol, 0.25)
    pts = np.array([(v.x, v.y, v.z) for v in verts], float)
    faces = np.hstack([np.full((len(tris), 1), 3), np.asarray(tris, int)]).ravel()
    return pv.PolyData(pts, faces).clean().compute_normals(split_vertices=True, feature_angle=35.0,
                                                           auto_orient_normals=True)


_BLOCKS: dict = {}


def pocket_block(x0, x1, y0, y1, holes, h: float = DECK_H, floor: float = DECK_FLOOR,
                 lead: float = POCKET_LEAD) -> pv.PolyData:
    """A block, its bottom face at z = 0, with flat-bottomed bores [(x, y, r)] from its top down to `floor`, each with a
    45 deg chamfer `lead` deep at its mouth. CadQuery, tessellated once per shape."""
    key = (x0, x1, y0, y1, tuple(holes), h, floor, lead)
    if key not in _BLOCKS:
        import cadquery as cq
        b = cq.Workplane("XY").box(x1 - x0, y1 - y0, h, centered=False).translate((x0, y0, 0))
        for x, y, r in holes:
            bore = cq.Workplane("XY").circle(r).extrude(h - floor + 1.0).translate((x, y, floor))
            cone = cq.Solid.makeCone(r, r + lead + 0.5, lead + 0.5, pnt=cq.Vector(x, y, h - lead),
                                     dir=cq.Vector(0, 0, 1))
            b = b.cut(bore).cut(cq.Workplane("XY").add(cone))
        _BLOCKS[key] = _cq_mesh(b.val())
    return _BLOCKS[key].copy()


def buffer_holder() -> tuple[pv.PolyData, tuple[float, float, float]]:
    """A one-vial block on the cabinet top, beside the arm's mounting plate: where the vial waits while the VLM swaps
    trays. Its frame's origin is on the cabinet top; returns the mesh and the seat (the vial's base centre): a 30 mm
    bore for the 28 mm vial, 26 mm deep, with a lead-in. The gripper takes the vial 50 mm up, so its fingertips stay
    about 5 mm over the block."""
    mesh = pocket_block(-32.0, 32.0, -32.0, 32.0, [(0.0, 0.0, VIAL_R + POCKET_CLEAR)])
    return mesh, (0.0, 0.0, DECK_FLOOR)


def tcp_frame(p, approach=(0, 0, -1), spin_deg: float = 0.0) -> np.ndarray:
    """A 4x4 tool pose at point p with the tool's z along `approach` (unit vector) and its x picked by `spin_deg`.

    For an approach within 60 deg of level, spin 0 always has the tool's y pointing down (round 7). Until then it
    pointed down or up depending on the heading. That rolled the gripper 180 deg between headings, which put the wrist
    camera (ur_arm.camera_meshes, on tool0's -y side) under the gripper for some of them, and turned a part held level
    upside down between two headings. Straight-down and steep approaches are as before."""
    z = np.asarray(approach, float)
    z /= np.linalg.norm(z)
    ref = np.array([1.0, 0.0, 0.0]) if abs(z[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    x = ref - z * (ref @ z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    if y[2] > 0.5:                     # level-ish with y up: roll 180 deg about z, so y points down
        x, y = -x, -y
    a = np.radians(spin_deg)
    x, y = x * np.cos(a) + y * np.sin(a), -x * np.sin(a) + y * np.cos(a)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, p
    return M


# ------------------------------------------------------------------------------------------- powder jars (round 9)
# Sterling (PR #318, 2026-11-05 22:56): "What's with the technicolor jars? Keep them all a normal black lid with
# transparent glass, but if you want to point out something that's unique about them, use a legend and a color change
# that then reverts once the legend has been shown for a bit of time." So every powder jar in the lab is drawn the same
# way: clear glass (light grey-blue, about 35 % opaque, so the powder shows), a matte black cap, a white label. To point
# something out (which lot, which size cut, which powder), tint only those jars or their powder for a few seconds while
# a legend says what the tint means, then fade back. The helpers, for any stream's scenes:
#   jar_style()                    the colours and opacities, as a dict
#   jar_meshes(d, h, lid_h)        one jar's parts as PolyData, base centre at the origin, the label facing -y
#   jar_parts(d, h, lid_h)         the same as {part: (mesh, rgb, opacity)}, for Instrument.meshes or sc.add
#   tint_sleeve(d, h)              a tinted see-through sleeve just outside a jar's glass: fade it in to tint the jar
#   TINT, tinted(rgb, tint, k)     the highlight colours; a colour k of the way from rgb to a tint (sc.color[name])
#   pulse(t, t_on, t_off, ramp)    0 -> 1 -> 0: a tint's strength at time t, with smooth ramps
#   use_legend(sc)                 a Scene then draws sc.legend = dict(title=, items=[(rgb, text)], alpha=0-1)
#   draw_legend(img, title, items, alpha, s)   the legend box itself (PIL), top right under the step label
#   piece_legend(key, legends)     for a tour clip (tour.py): a legend shown while a fade piece of the instrument shows
JAR_GLASS = (0.76, 0.83, 0.90)               # clear glass, drawn light grey-blue so it reads on a white floor
JAR_GLASS_OPACITY = 0.35
JAR_LID = (0.07, 0.07, 0.08)                 # matte black cap (phenolic or PP; PTFE-lined: notes/lab_r8.md, "Which containers for powder")
JAR_LABEL = (0.97, 0.97, 0.95)               # a white paper label
JAR_PRINT = (0.10, 0.10, 0.11)               # the ID printed on it
JAR_POWDER = POWDER                          # grey metal powder
JAR_WALL = 2.0                               # glass wall, mm (drawn: the powder's radius is the jar's less this)
# highlight tints, one meaning each per clip; always shown with a legend, then back to the plain jar
TINT = {"amber": (0.97, 0.60, 0.08), "teal": (0.00, 0.62, 0.66), "magenta": (0.84, 0.20, 0.58),
        "blue": (0.15, 0.42, 0.92), "green": (0.30, 0.70, 0.25)}
TINT_OPACITY = 0.72                          # a tint sleeve's opacity when fully on


def jar_style() -> dict:
    """The lab-wide powder jar: {"glass": rgb, "glass_opacity": a, "lid": rgb, "label": rgb, "print": rgb,
    "powder": rgb, "wall": mm}."""
    return dict(glass=JAR_GLASS, glass_opacity=JAR_GLASS_OPACITY, lid=JAR_LID, label=JAR_LABEL, print=JAR_PRINT,
                powder=JAR_POWDER, wall=JAR_WALL)


def _arc_band(r: float, z0: float, z1: float, deg: float, res: int = 18, facing: float = -90.0) -> pv.PolyData:
    """A thin curved strip on a cylinder of radius r from z0 to z1, `deg` wide and centred on the direction `facing`
    (degrees from +x; -90 is the front, -y): a label stuck on one side of a jar."""
    th = np.radians(np.linspace(facing - deg / 2, facing + deg / 2, res + 1))
    pts = np.array([(r * np.cos(t), r * np.sin(t), z) for t in th for z in (z0, z1)], float)
    faces = []
    for i in range(res):
        a, b, c, d = 2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2
        faces += [4, a, d, c, b]
    return pv.PolyData(pts, np.array(faces)).triangulate().compute_normals(auto_orient_normals=False)


def jar_meshes(d: float, h: float, lid_h: float, fill: float = 0.62, label=(0.14, 0.52), label_deg: float = 110.0,
               res: int = 28) -> dict:
    """One powder jar, base centre at the origin, z up, its label facing -y: {"glass", "powder", "label", "print",
    "lid"} as PolyData. d and h are the glass body's outside diameter and height; the cap (lid_h tall, 2 mm wider)
    sits on top. `fill` is the powder's height as a share of the inside; `label` its band as shares of h."""
    r = d / 2
    glass = _cyl(r, h, 0.0, res=res)
    z_floor = 2.5
    powder = _cyl(r - JAR_WALL, max(0.5, fill * (h - z_floor - 4.0)), z_floor, res=res)
    lab = _arc_band(r + 0.4, label[0] * h, label[1] * h, label_deg)
    zm = (label[0] + label[1]) / 2 * h
    prt = _arc_band(r + 0.7, zm - 0.10 * h, zm + 0.02 * h, label_deg * 0.45)
    lid = _cyl(r + 1.0, lid_h, h, res=res)
    return dict(glass=glass, powder=powder, label=lab, print=prt, lid=lid)


def jar_parts(d: float, h: float, lid_h: float, **kw) -> dict:
    """jar_meshes() with the lab-wide look: {part: (mesh, rgb, opacity)}."""
    m = jar_meshes(d, h, lid_h, **kw)
    return {"glass": (m["glass"], JAR_GLASS, JAR_GLASS_OPACITY), "powder": (m["powder"], JAR_POWDER, 1.0),
            "label": (m["label"], JAR_LABEL, 1.0), "print": (m["print"], JAR_PRINT, 1.0),
            "lid": (m["lid"], JAR_LID, 1.0)}


def tint_sleeve(d: float, h: float, res: int = 28) -> pv.PolyData:
    """A see-through sleeve 1.2 mm outside a jar's glass (label included), base at z = 0: drawn in a tint at
    TINT_OPACITY and faded in, it tints the whole jar body while the cap stays black."""
    return _cyl(d / 2 + 1.2, h - 0.5, 0.25, res=res)


def tinted(rgb, tint, k: float) -> tuple:
    """A colour k (0-1) of the way from rgb to tint: for sc.color[name] in a step's update."""
    k = min(max(float(k), 0.0), 1.0)
    return tuple(float(a + (b - a) * k) for a, b in zip(rgb, tint))


def pulse(t: float, t_on: float, t_off: float, ramp: float = 0.5) -> float:
    """0 before t_on, up to 1 over `ramp` s, 1 until t_off - ramp, back to 0 at t_off (smoothstep ramps): a tint's
    and its legend's strength at time t."""
    if t <= t_on or t >= t_off:
        return 0.0
    k = min(1.0, (t - t_on) / ramp, (t_off - t) / ramp)
    return k * k * (3.0 - 2.0 * k)


def draw_legend(img, title: str, items, alpha: float = 1.0, s: float = 1.0, corner: str = "tr", top: float = 46.0):
    """A legend box on a PIL image: a bold title, then a colour swatch and a line of text per item [(rgb, text)].
    corner "tr" puts it top right under the step label, "tl" top left under the title; `top` is its top edge in
    720p pixels (scaled by s). Returns the image."""
    if alpha <= 0.02 or not items:
        return img
    from PIL import ImageDraw
    from scene import font
    d = ImageDraw.Draw(img, "RGBA")
    W, _ = img.size
    al = int(255 * min(alpha, 1.0))
    ft, fi = font(14.5 * s, bold=True), font(13.5 * s)
    pad, sw, lh = 9 * s, 15 * s, 21 * s
    tw = max([d.textlength(title, font=ft)] + [d.textlength(t, font=fi) + sw + 9 * s for _, t in items])
    w = tw + 2 * pad
    h = 2 * pad + (21 * s if title else 0) + len(items) * lh - 4 * s
    x0 = W - 10 * s - w if corner == "tr" else 10 * s
    y0 = top * s
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 6 * s, fill=(255, 255, 255, int(238 * min(alpha, 1.0))),
                        outline=(120, 124, 130, al))
    y = y0 + pad
    if title:
        d.text((x0 + pad, y - 1 * s), title, font=ft, fill=(20, 20, 24, al))
        y += 21 * s
    for rgb, text in items:
        c = tuple(int(round(255 * v)) for v in rgb[:3])
        d.rounded_rectangle((x0 + pad, y + 1.5 * s, x0 + pad + sw, y + 1.5 * s + sw), 3 * s, fill=c + (al,),
                            outline=(60, 60, 66, al))
        d.text((x0 + pad + sw + 9 * s, y), text, font=fi, fill=(20, 20, 24, al))
        y += lh
    return img


def use_legend(sc) -> None:
    """Let a Scene draw a legend: in a step's update set sc.legend = dict(title=..., items=[(rgb, text)], alpha=0-1,
    corner="tr") (None for none), and every frame shows it over the usual text. Wraps this scene's overlay only;
    calling it twice is harmless; no legend with VIZ3D_CLEAN. A tint and its legend, in a chapter script:

        P.use_legend(sc)
        def up(u):                                   # inside a step of `secs` seconds
            k = P.pulse(u * secs, 0.0, secs, ramp=0.6)
            sc.color[name] = P.tinted(P.JAR_POWDER, P.TINT["amber"], k)
            sc.legend = dict(title="Tinted for now", items=[(P.TINT["amber"], "the LPBF cut, < 63 um")], alpha=k)
    """
    if getattr(sc, "_legend_on", False):
        return
    import scene as S
    base = sc.overlay
    sc.legend = None

    def overlay(img, scale, anchors):
        img = base(img, scale, anchors)
        lg = getattr(sc, "legend", None)
        if lg and not S.CLEAN:
            draw_legend(img, lg.get("title", ""), lg.get("items", ()), lg.get("alpha", 1.0), max(scale, 0.80),
                        lg.get("corner", "tr"), lg.get("top", 46.0))
        return img
    sc.overlay = overlay
    sc._legend_on = True


def piece_legend(key: str, legends: dict, then=None, corner: str = "tr", top: float = 46.0):
    """For a tour clip (tour.py plays an Instrument): a draw(sc, img, s) for instruments_lab.PLOTS[f"instruments/{key}"]
    that shows legends[piece] = (title, [(rgb, text)]) while that piece shows, at its fade joint's value (the tint
    sleeves are such a piece: Joint("fade"), v0 = 0, faded in and out by the actions). `then`: a drawer that already
    sits in PLOTS for that clip, called first."""
    def draw(sc, img, s):
        if then is not None:
            then(sc, img, s)
        for piece, (title, items) in legends.items():
            g = f"{key}:{piece}"
            a = max((sc.alpha.get(n, 0.0) for n, gg in sc.group_of.items() if gg == g), default=0.0)
            if a > 0.02:
                draw_legend(img, title, items, min(1.0, a), s, corner, top)
    return draw
