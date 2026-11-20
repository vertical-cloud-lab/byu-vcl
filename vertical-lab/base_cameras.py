"""The base cameras (#364): what each of the three cameras on a MiR250 sees, parked at the VLM's opening and at the
AMAZEMET rePowder, while the arm works.

Sterling (PR #318, 2026-11-20) asked for two or three cameras on each mobile base, one on either side and one higher up
on a rod or extrusion, after robot-arms PR 40's three-camera cell. They are drawn by ``props.mir250()``
(``props.base_camera_parts``), so every clip with a MiR250 has them; this clip shows them and looks through each one.
Each view is rendered from the camera's own lens position and aim (``props.base_camera_optics``), 102 degrees across
(Raspberry Pi: Camera Module 3 Wide, 102 x 67), the frame's top and bottom blacked out to the Wide's 67 degrees.

    xvfb-run -a python3 base_cameras.py vlm          # -> out/mp4/base_cameras_vlm.mp4, out/base_cameras_vlm.json
    xvfb-run -a python3 base_cameras.py atomizer     # -> out/mp4/base_cameras_atomizer.mp4, ...
    python3 base_cameras.py join                     # -> out/mp4/base_cameras.mp4 (the two, ffmpeg -threads 2)
    python3 base_cameras.py sheet                    # -> out/base_cams/views.png: the six camera views, two rows

With ``VIZ3D_HD=1 VIZ3D_SIZE=1920x1080`` the 1080p copies go to out/hd/ (with text) and out/clean/; each camera's view
is also saved as out/base_cams/view_<site>_<camera>.png (the frame as the camera sees it, no text). ``ARM_AUDIT=1``
renders nothing and checks every frame: out/collisions/base_cameras_vlm.json and ..._atomizer.json.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import props as P                                     # noqa: E402
import scene as S                                     # noqa: E402
from scene import OUT, SIZE, T, Scene                 # noqa: E402

VIEWS = OUT / "base_cams"
COL = {"L": (0.16, 0.45, 0.85), "R": (0.93, 0.50, 0.10), "M": (0.15, 0.62, 0.30)}
NAME = {"L": "left side camera", "R": "right side camera", "M": "mast camera"}
VA = 2 * math.degrees(math.atan(math.tan(math.radians(P.CM3W["hfov"] / 2)) * SIZE[1] / SIZE[0]))   # 102 deg across
MASK_Y = (1.0 - math.tan(math.radians(P.CM3W["vfov"] / 2)) / math.tan(math.radians(VA / 2))) / 2


class CamScene(Scene):
    """A Scene that can black out the frame's edges, so a camera's own picture keeps its shape (services.py's)."""
    mask_x = 0.0
    mask_y = 0.0

    def render_base(self):
        img = super().render_base()
        if self.mask_x > 0 or self.mask_y > 0:
            img = np.array(img)
            h, w = img.shape[:2]
            mx, my = int(round(self.mask_x * w)), int(round(self.mask_y * h))
            if mx:
                img[:, :mx] = 22
                img[:, w - mx:] = 22
            if my:
                img[:my] = 22
                img[h - my:] = 22
        return img


def _tube(pts, r=3.0, n=6):
    return pv.Spline(np.asarray(pts, float), 2).tube(radius=r, n_sides=n).triangulate()


def frustum(o: dict, far: float, z_floor: float = 0.0):
    """A camera's picture as a see-through pyramid from its lens, cut at `far` mm or the floor; and its edges."""
    c, f, r, u = (np.asarray(o[k], float) for k in ("eye", "fwd", "right", "up"))
    ta, tb = math.tan(math.radians(o["hfov"] / 2)), math.tan(math.radians(o["vfov"] / 2))
    pts = [c]
    for a, b in ((1, 1), (1, -1), (-1, -1), (-1, 1)):
        d = f + a * ta * r + b * tb * u
        d /= np.linalg.norm(d)
        t = (z_floor - c[2]) / d[2] if d[2] < -1e-6 else far
        pts.append(c + d * min(t, far))
    Pp = np.array(pts)
    sides = pv.PolyData(Pp, faces=np.hstack([[3, 0, 1, 2], [3, 0, 2, 3], [3, 0, 3, 4], [3, 0, 4, 1]]))
    edges = pv.merge([_tube([Pp[0], Pp[i]]) for i in range(1, 5)] +
                     [_tube([Pp[i], Pp[1 + i % 4]]) for i in range(1, 5)])
    return sides, edges


def add_frusta(sc, Wm, far=1500.0, groups=("frusta",)):
    """The three cameras' pyramids, hidden; returns {camera: optics in the world}."""
    opt = {}
    for k in P.BASE_CAMS:
        o = P.base_camera_optics(k, Wm)
        opt[k] = o
        sides, edges = frustum(o, far)
        sc.add(f"frustum {k}", sides, COL[k], groups[0], opacity=0.14, specular=0.0, ambient=0.6)
        sc.add(f"frustum {k} edges", edges, COL[k], groups[0], ambient=0.6, specular=0.0)
    for n, g in sc.group_of.items():
        if g in groups:
            sc.alpha[n] = 0.0
    # overlays, not solids: the collision checks skip them, as they skip liquids (services.movie_bay_camera)
    sc.fluids = set(getattr(sc, "fluids", ())) | {n for n in sc.actors if sc.group_of[n] in groups}
    return opt


def show_frusta(sc, a: float, which=None):
    for n, g in sc.group_of.items():
        if g == "frusta" and (which is None or n.split()[1] in which):
            sc.alpha[n] = a


def cam_of(o: dict) -> list:
    return [tuple(o["eye"]), tuple(o["eye"] + o["fwd"] * 1000.0), tuple(o["up"])]


def into(sc, k, opt, also=None):
    """update(u): the frusta fade out as the view flies into camera k; the last stretch masks the frame to 67 deg."""
    def up(u):
        show_frusta(sc, max(0.0, 1.0 - 2.5 * u))
        sc.mask_y = MASK_Y * max(0.0, (u - 0.8) / 0.2)
        if also is not None:
            also(u)
    return up


def save_view(sc, site: str, k: str):
    """The camera's picture as it is now (no text), for the sheet."""
    if S.AUDIT or S.PREVIEW:
        return
    VIEWS.mkdir(parents=True, exist_ok=True)
    from PIL import Image
    img = Image.fromarray(np.asarray(sc.render_base()))
    img.save(VIEWS / f"view_{site}_{k}.png")


def labels_for(sc, Wm, opt, z_lift=0.0):
    out = []
    pos = {"M": (0.66, 0.16), "L": (0.10, 0.52), "R": (0.86, 0.45)}
    for k in ("M", "L", "R"):
        top = P.base_camera_geometry(k)["box_centre"]
        p = (Wm @ np.r_[top, 1.0])[:3] + (0, 0, z_lift)
        h = P.base_camera_geometry(k)["top"]
        txt = {"M": f"mast camera, {P.base_camera_optics(k)['eye'][2] / 1000:.2f} m up: Camera Module 3 Wide + Pi 5",
               "L": "left side camera, 0.88 m", "R": "right side camera, 0.88 m"}[k]
        out.append((txt, tuple(p), pos[k]))
    return out


# ================================================================================================ at the VLM
def part_vlm():
    import animate as A
    import lab
    import reach
    import services as SV
    import setup_lab
    import vlm as V
    data, idata = lab.meshes(), setup_lab.tour_load_safe()
    sc, L, live = SV.build_vlm("base_cameras_vlm", data, idata,
                               "Vertical cloud lab: the cameras on a mobile manipulator, at the VLM", robot=True,
                               scene_cls=CamScene)
    L.skin(1.0)(1.0)
    k = "B"                                              # the doser's tray, at the opening (as the bay-camera clip)
    L.tray[k] = [V.Y_OPEN, V.Z_OPEN]
    L.where[k] = "open"
    L.lift_z = V.Z_OPEN
    SV.set_dock(sc, "open", 0.0)
    SV.set_dock(sc, A.HOME[k], 1.0)
    L.apply_state()
    rb = L.robot
    Wm = sc.world("amr")
    opt = add_frusta(sc, Wm)
    L.svc_lines = [("Base", "MiR250 at Shuttle 1's opening"), (f"Tray {k}", "at the opening"),
                   ("Cameras", "3 x Camera Module 3 Wide + Pi 5")]
    L.gauges()
    # the arm's work: the bay-camera clip's vial from the rack to the doser's shuttle fork (services.movie_bay_camera),
    # the long moves planned round everything drawn (robot.joint_to), the ones in and out of a seat straight lines
    seats = reach.seats()
    rack, cup = seats["vial rack (tray B)"], seats["multi-doser shuttle fork (tray B)"]
    above_rack, above_cup = T((0, 0, 140)) @ rack, T((0, 0, 130)) @ cup
    q_park = rb.q.copy()

    def later(make):
        """A move built when its step starts (robot.joint_to and line_to plan from the arm's pose at that moment)."""
        st = {}

        def up(u):
            if "f" not in st:
                st["f"] = make()
            st["f"](u)
        return up
    fork = L.carousel.fork_group
    over = [(-2500, -4500, 2300), (0, -1650, 1100), (0, 0, 1)]
    sc.cam = over
    sc.view_angle = 30.0
    n = 5
    lbl = labels_for(sc, Wm, opt)
    sc.step(f"1/{n}", "Three cameras on the mobile base, after robot-arms PR 40's cell: one on each end of the cabinet, "
            "0.88 m up, and one on a mast at the back-left corner, 1.75 m up. Each is a Raspberry Pi Camera Module 3 Wide "
            "with its own Pi 5, aimed for good by a printed wedge; the mast's Pi rides in its camera's box, the side "
            "cameras' on the cabinet's ends.", 3.0,
            lambda u: show_frusta(sc, u), hold=2.2, labels=lbl)

    def look(key, step, caption, work, secs=3.0, view_secs=1.8, hold=0.8):
        L.svc_lines = [("Camera", NAME[key]), ("Picture", "102 x 67 deg, 16:9"), ("Base", "parked at the opening")]
        L.gauges()
        sc.step(step, caption, view_secs, into(sc, key, opt), hold=0.0, cam_to=cam_of(opt[key]), view_angle_to=VA)
        for f, s, h in work:
            sc.step(step, caption, s, f, hold=h)
        save_view(sc, "vlm", key)

    def grip(c1, then=None):
        f = rb.grip_to(c1)

        def up(u):
            f(u)
        return up
    look("M", f"2/{n}", "The mast camera, from behind and above the arm's shoulder: the whole arm, the presented tray "
         "and what the gripper holds, from outside. The wrist camera sees 7-50 cm in front of the gripper, and the bay "
         "camera only works here; this one goes to every station with the arm, with the same view every time.",
         [(later(lambda: rb.joint_to(Tw=above_rack)), 1.6, 0.1), (later(lambda: rb.line_to(rack)), 1.0, 0.1),
          (grip(A.GRIP_VIAL), 0.5, 0.2)])
    rb.grasp("vial")
    look("L", f"3/{n}", "The left side camera, low on the cabinet's end, looking forward past the arm: with the right one, "
         "a pair 0.74 m apart that sees the work in front of the arm from 50-60 degrees apart, as robot-arms PR 40's side "
         "cameras do (70 there): AprilTags on the station's face, and the gripper's fingertips, in 3-D, before and "
         "while the arm moves.",
         [(later(lambda: rb.line_to(above_rack)), 1.0, 0.0), (later(lambda: rb.joint_to(Tw=above_cup)), 1.8, 0.2)])
    look("R", f"4/{n}", "The right side camera: the other half of the pair, and the aisle on this side. All three keep "
         "recording through a protective stop: they run on the MiR250's isolated 24 V output, which stays on in an "
         "emergency or protective stop (MiR250 electrical interface).",
         [(later(lambda: rb.line_to(cup)), 1.0, 0.1), (grip(0.0), 0.5, 0.1)])
    rb.release(fork)
    L.svc_lines = [("Base", "MiR250 at Shuttle 1's opening"), ("Vial", "on the doser's shuttle fork"),
                   ("Cameras", "3, recording")]
    L.gauges()

    sc.step(f"5/{n}", "Back out: the vial is on the doser's shuttle and the arm goes home. None of the three is a "
            "safety device: the MiR250's scanners and the UR10e's own limits stay the safety functions.", 0.8,
            later(lambda: rb.line_to(above_cup)), hold=0.0)
    home = later(lambda: rb.joint_to(q1=q_park))

    def back(u):
        home(u)
        sc.mask_y = MASK_Y * max(0.0, 1.0 - 4.0 * u)
        show_frusta(sc, min(1.0, max(0.0, (u - 0.5) * 2.0)))
    sc.step(f"5/{n}", "Back out: the vial is on the doser's shuttle and the arm goes home. None of the three is a "
            "safety device: the MiR250's scanners and the UR10e's own limits stay the safety functions.", 2.6, back,
            hold=1.4, cam_to=over, view_angle_to=30.0, labels=lbl, still=True)
    return sc.save()


# ============================================================================================ at the rePowder
def part_atomizer():
    import atom_base as AB
    AB.Scene = CamScene
    sc, ma, _ = AB.build("base_cameras_atomizer",
                         "Vertical cloud lab: the cameras on a mobile manipulator, at the rePowder", mirs=1)
    rb = ma.rb
    Wm = sc.world(ma.g)
    opt = add_frusta(sc, Wm)
    M = AB.M
    vp, vn = np.asarray(M.VIEWPORT, float), np.asarray(M.VIEWPORT_N, float)
    # the arm's work: the wrist camera brought to 220 mm off the viewport's glass, looking in along its axis (checking
    # the glass for spatter before a run), then home
    q_park = rb.q.copy()
    look_T = AB.tcp(vp + vn * 220.0, -vn)
    near_T = AB.tcp(vp + vn * 150.0, -vn)
    AB.status(sc, Base="MiR250 at the rePowder's front", Cameras="3 x Camera Module 3 Wide + Pi 5")
    over = AB.cam((2300, -3300, 2300), (-80, -500, 1150))
    sc.cam = over
    sc.view_angle = 30.0
    n = 5
    lbl = labels_for(sc, Wm, opt)
    sc.step(f"1/{n}", "The same base parked at the rePowder's front: the cameras ride with it, so the views are the same "
            "relative to the arm at every station, which is what a learned policy or a calibration needs (robot-arms "
            "PR 40: a new camera position was the hardest change for policies to cope with).", 3.0,
            lambda u: show_frusta(sc, u), hold=2.2, labels=lbl)

    def look(key, step, caption, work, view_secs=1.8):
        AB.caption_rows(sc, Camera=NAME[key], Picture="102 x 67 deg, 16:9", Base="parked at the rePowder")
        sc.step(step, caption, view_secs, into(sc, key, opt), hold=0.0, cam_to=cam_of(opt[key]), view_angle_to=VA)
        for f, s, h in work:
            sc.step(step, caption, s, f, hold=h)
        save_view(sc, "atomizer", key)
    look("M", f"2/{n}", "The mast camera: the arm reaching to the chamber's viewport, the furnace and the lid above it, "
         "from outside the arm. Nothing at this station watches the arm itself: the rePowder's own cameras look at "
         "the melt and the stream.", [(rb.joint_to(Tw=look_T), 2.4, 0.2)])
    look("L", f"3/{n}", "The left side camera: the chamber's front, the latch and the viewport, and the gripper as it "
         "comes in, from low and to the left.", [(rb.line_to(near_T), 1.4, 0.4)])
    look("R", f"4/{n}", "The right side camera: the same work from the right, the base's footprint and the floor in "
         "front of the machine, where spilled powder would show.", [(rb.line_to(look_T), 1.2, 0.2)])
    AB.caption_rows(sc, Base="MiR250 at the rePowder's front", Cameras="3, recording")

    home = rb.joint_to(q1=q_park)

    def back(u):
        home(u)
        sc.mask_y = MASK_Y * max(0.0, 1.0 - 4.0 * u)
        show_frusta(sc, min(1.0, max(0.0, (u - 0.5) * 2.0)))
    sc.step(f"5/{n}", "Back out: the arm goes home. Each camera's frames are timestamped on its Pi, and every Pi is on "
            "the base's own switch, so the three pictures and the arm's log line up afterwards.", 2.6, back, hold=1.4,
            cam_to=over, view_angle_to=30.0, labels=lbl, still=True)
    return sc.save()


# =============================================================================================== join, sheet
def join():
    src = [OUT / ("hd" if S.HD else "mp4") / f"base_cameras_{p}.mp4" for p in ("vlm", "atomizer")]
    lst = Path("/tmp/base_cameras_concat.txt")
    lst.write_text("".join(f"file '{p}'\n" for p in src))
    dst = OUT / ("hd" if S.HD else "mp4") / "base_cameras.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-threads", "2", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", str(dst)], check=True)
    return dst


def sheet():
    from PIL import Image, ImageDraw
    from scene import font
    tw, th = 640, 360
    img = Image.new("RGB", (3 * tw, 2 * th + 2 * 34), (255, 255, 255))
    d = ImageDraw.Draw(img)
    for r, site in enumerate(("vlm", "atomizer")):
        for c, k in enumerate(("M", "L", "R")):
            p = VIEWS / f"view_{site}_{k}.png"
            y0 = r * (th + 34)
            d.text((c * tw + 8, y0 + 7), f"{'At the VLM' if site == 'vlm' else 'At the rePowder'}: {NAME[k]}",
                   fill=(20, 20, 24), font=font(17, bold=True))
            if p.exists():
                img.paste(Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS), (c * tw, y0 + 34))
    out = VIEWS / "views.png"
    img.save(out)
    return out


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "vlm"
    if what == "vlm":
        print(part_vlm(), flush=True)
    elif what == "atomizer":
        print(part_atomizer(), flush=True)
    elif what == "join":
        print(join(), flush=True)
    elif what == "sheet":
        print(sheet(), flush=True)
    else:
        raise SystemExit(__doc__)
