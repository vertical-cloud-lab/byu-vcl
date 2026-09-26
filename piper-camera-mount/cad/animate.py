#!/usr/bin/env python3
"""Step-by-step GIF of putting the mount together on the PiPER gripper.

    xvfb-run -a -s "-screen 0 1920x1080x24" python animate.py      # -> ../renders/assembly_steps.gif

Screws and nuts are nominal ISO models (hardware.py). The two ribbon routes are indicative:
the real cables are flat and are dressed by hand, but the lengths printed at the end (and in
the README) come from these routes.
"""
from __future__ import annotations

import math
import shutil
import subprocess
import textwrap
from pathlib import Path

import cadquery as cq
import numpy as np
import pyvista as pv
from PIL import Image

import hardware
import reference
from fiducials import tag_image, tag_quad, vec
from piper_mount import COLORS, Params, build, place_tag_wedges, station_vec, tag_poses
from render import mesh

RENDERS = Path(__file__).resolve().parent.parent / "renders"
FPS = 10
SIZE = (760, 570)
WRAP = 70
STEEL = (0.74, 0.75, 0.78)
RIBBON = (0.90, 0.78, 0.35)
OPENING = 40.0
ALU, DARK, PAD = (0.78, 0.79, 0.81), (0.20, 0.20, 0.22), (0.35, 0.35, 0.37)


def ease(u: float) -> float:
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def merged(shapes) -> pv.PolyData:
    return pv.merge([mesh(s, 0.05) for s in shapes])


class Scene:
    """Actors that move as groups, plus a caption, recorded frame by frame (after #234's animate.py)."""

    def __init__(self, title: str):
        self.pl = pv.Plotter(off_screen=True, window_size=SIZE)
        self.pl.set_background("white")
        self.pl.enable_anti_aliasing("ssaa")
        self.actors: dict[str, object] = {}
        self.pos: dict[str, np.ndarray] = {}
        self.alpha: dict[str, float] = {}
        self.base_alpha: dict[str, float] = {}
        self.groups: dict[str, set[str]] = {}
        self.group_off: dict[str, np.ndarray] = {}
        self.frames: list[Image.Image] = []
        self.pl.add_text(title, position=(14, SIZE[1] - 34), font_size=12, color="black")
        self.caption = self.pl.add_text(" ", position=(14, 14), font_size=10, color="black")
        self.step_no = self.pl.add_text(" ", position=(SIZE[0] - 90, SIZE[1] - 34), font_size=12,
                                        color=(0.35, 0.35, 0.35))
        for actor in (self.caption, self.step_no):
            prop = actor.GetTextProperty()
            prop.SetBackgroundColor(1.0, 1.0, 1.0)
            prop.SetBackgroundOpacity(0.85)
        self.caption_text = " "
        self.cam = None

    def add(self, name, poly, color=None, opacity=1.0, shown=True, **kw):
        self.actors[name] = self.pl.add_mesh(poly, color=color, opacity=opacity, smooth_shading=False,
                                             specular=0.2, **kw)
        self.pos[name] = np.zeros(3)
        self.base_alpha[name] = opacity
        self.alpha[name] = 1.0 if shown else 0.0

    def group(self, gname, members, offset=(0, 0, 0)):
        self.groups[gname] = set(members)
        self.group_off[gname] = np.array(offset, float)

    def apply(self):
        for name, actor in self.actors.items():
            p = self.pos[name].copy()
            for g, members in self.groups.items():
                if name in members:
                    p = p + self.group_off[g]
            actor.SetPosition(*p)
            a = self.alpha[name]
            actor.SetVisibility(a > 0.02)
            actor.GetProperty().SetOpacity(self.base_alpha[name] * a)

    def snap(self, n=1):
        self.apply()
        self.pl.camera_position = self.cam
        self.pl.render()
        img = Image.fromarray(self.pl.screenshot(return_img=True))
        self.frames.extend([img] * n)

    def step(self, label, caption, frames, update, hold=14, cam_to=None):
        caption = "\n".join(textwrap.fill(line, WRAP) for line in " ".join(caption.split()).split(" | "))
        self.step_no.SetInput(label)
        self.caption.SetInput(caption)
        self.caption_text = caption
        cam_from = [np.array(v, float) for v in self.cam]
        for i in range(1, frames + 1):
            u = ease(i / frames)
            update(u)
            if cam_to is not None:
                self.cam = [tuple(a + (np.array(b, float) - a) * u) for a, b in zip(cam_from, cam_to)]
            self.snap()
        self.snap(hold)

    def save(self, path: Path):
        picks = self.frames[:: max(1, len(self.frames) // 15)][:16]
        tw, th = SIZE[0] // 4, SIZE[1] // 4
        mosaic = Image.new("RGB", (tw * 4, th * 5), "white")
        for i, f in enumerate(picks):
            mosaic.paste(f.convert("RGB").resize((tw, th)), ((i % 4) * tw, (i // 4) * th))
        pal = mosaic.quantize(colors=112, method=Image.MEDIANCUT)
        frames = [f.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE) for f in self.frames]
        frames[0].save(path, save_all=True, append_images=frames[1:], duration=int(1000 / FPS), loop=0,
                       optimize=True, disposal=1)
        self.pl.close()
        if shutil.which("gifsicle"):          # lossy re-encode: about 35 % smaller, which keeps it under 5 MB
            subprocess.run(["gifsicle", "-O3", "--lossy=35", "-b", str(path)], check=True)
        print(f"{path.name}: {len(frames)} frames, {len(frames) / FPS:.0f} s, {path.stat().st_size / 1e6:.1f} MB")


def ribbon_routes(p: Params) -> dict[str, np.ndarray]:
    """Indicative centre lines of the two ribbons, from each camera's connector to the Pi 5's
    CAM/DISP connectors. Both cross the gripper in front of y = 46, clear of the jumper sockets
    in the back cover, and stay in front of the J6 flange face."""
    hq0 = vec(station_vec(p, 19.5, 2.2, 0.0))
    cm0 = vec(station_vec(p, 0.0, 0.5, p.cm_dz + p.cm_h - p.cm_lens_from_top + 0.5))
    zc = p.ax_z
    hq = [hq0, hq0 + (4, -2, -8), (-60, 52, zc - 26), (-52, 38, zc - 33), (-34, 30, zc - 42), (-8, 28, zc - 47),
          (18, 30, zc - 46), (35, 38, zc - 47), (44, 48, zc - 36), (44, 54, zc - 12), (42.5, 55, 11.4)]
    cm = [cm0, cm0 + (0, -2, 8), (-70, 40, 64), (-45, 30, 60), (-8, 28, 56), (20, 30, 53), (36, 40, 52),
          (56, 50, 47), (57, 56, 22), (48, 56, 12), (42.5, 55, 6.4)]
    return {"hq": np.array(hq, float), "cm3w": np.array(cm, float)}


def route_length(points: np.ndarray) -> float:
    spline = pv.Spline(points, 400)
    return float(np.linalg.norm(np.diff(spline.points, axis=0), axis=1).sum())


def gripper_actors(sc: Scene) -> list[str]:
    names = []
    shift = (OPENING - reference.OPENING_AS_MODELLED) / 2
    for i, s in enumerate(reference.gripper_solids()):
        if i in reference.UPPER_FINGER:
            s = s.translate(cq.Vector(0, 0, shift))
        elif i in reference.LOWER_FINGER:
            s = s.translate(cq.Vector(0, 0, -shift))
        color = PAD if i in (6, 10) else (DARK if i in (1, 5, 8, 9, 12) else ALU)
        sc.add(f"g{i}", mesh(s, 0.15), color)
        names.append(f"g{i}")
    return names


def main() -> None:
    RENDERS.mkdir(parents=True, exist_ok=True)
    p = Params()
    parts = build(p)
    hw = hardware.placed(p)
    t = math.radians(p.toe_deg)
    back = np.array([-math.sin(t), math.cos(t), 0.0])        # pod station +Y: from the camera side
    tongue_out = np.array([-math.cos(t), -math.sin(t), 0.0])  # station -X: out of the web's nut slots

    sc = Scene("AgileX PiPER wrist camera mount: assembly")
    gripper_actors(sc)
    for name in ("bracket", "carrier", "pod", "pi_spacers", "pi5", "hq_pcb", "hq_mount", "hq_lens", "cm_pcb",
                 "cm_module"):
        sc.add(name, mesh(parts[name]), COLORS[name], shown=False)
    for name, g in hw.items():
        sc.add(name, merged(g["shapes"]), STEEL, shown=False)
    wedges = place_tag_wedges(p, OPENING).val().Solids()
    for k, w in enumerate(wedges):
        sc.add(f"wedge{k}", mesh(w), COLORS["tag_wedge"], shown=False)
    for k, tp in enumerate(tag_poses(p, OPENING)):
        quad = tag_quad(vec(tp["centre"]) + vec(tp["normal"]) * 0.05, vec(tp["right"]), vec(tp["up"]), p.tag_size)
        sc.add(f"tag{k}", quad, None, shown=False, texture=pv.numpy_to_texture(tag_image(k + 1)), lighting=False)
    routes = ribbon_routes(p)
    for name, pts in routes.items():
        sc.add(f"ribbon_{name}", pv.Spline(pts, 300).tube(radius=1.2), RIBBON, shown=False)

    # Sub-assemblies that travel together.
    sc.group("bracket_sub", ["bracket", "clamp_nuts", "pod_nuts"], (-110, 0, 0))
    sc.group("carrier_sub", ["carrier", "pi_nuts"], (110, 0, 0))
    pod_members = ["pod", "hq_pcb", "hq_mount", "hq_lens", "cm_pcb", "cm_module", "hq_screws", "hq_nuts",
                   "cm_screws", "cm_nuts"]
    sc.group("pod_sub", pod_members, (-120, 60, 70))

    view = [(-420, -330, 260), (-20, 10, 5), (0, 0, 1)]
    sc.cam = [(-520, -420, 330), (-20, 10, 5), (0, 0, 1)]
    sc.caption.SetInput("AgileX PiPER gripper, fingers 40 mm apart. The mount goes on in 10 steps.")
    sc.snap(12)

    def show(names, a=1.0):
        for n in names:
            sc.alpha[n] = a

    def fly(names, vector, dist):
        """Parts arrive along `vector` over the last `dist` mm (they start at pos - vector * dist)."""
        v = np.asarray(vector, float) / np.linalg.norm(vector)
        start = {n: sc.pos[n].copy() for n in names}

        def f(u):
            for n in names:
                sc.alpha[n] = 1.0
                sc.pos[n] = start[n] - v * dist * (1 - u)
        return f

    def move_group(g, to):
        a = sc.group_off[g].copy()
        b = np.asarray(to, float)

        def f(u):
            sc.group_off[g] = a + (b - a) * u
        return f

    def both(*fs):
        def f(u):
            for g in fs:
                g(u)
        return f

    def delay(f, t0, t1=1.0):
        return lambda u: f(min(max((u - t0) / (t1 - t0), 0.0), 1.0))

    n = 16
    # 1. Nuts into the bracket, off the gripper.
    show(["bracket"])
    near_bracket = [(-380, -230, 190), (-140, 30, 5), (0, 0, 1)]
    sc.step("1 / 10", "Bracket: push 4 x M3 nuts into the pockets in its clamp ears (from the outside) | "
            "and slide 2 x M3 nuts into the side slots in its web. They hold the camera pod later.",
            n + 8, both(fly(["clamp_nuts"], (1, 0, 0), 30), delay(fly(["pod_nuts"], -tongue_out, 30), 0.3)),
            cam_to=near_bracket, hold=15)
    # 2. Bracket onto the gripper.
    sc.step("2 / 10", "Slide the bracket on from the tab side: half-collar round the O57 body, | "
            "its pad flat against the back of the tab (AgileX's reserved camera platform).",
            n + 6, move_group("bracket_sub", (0, 0, 0)), cam_to=view, hold=14)
    # 3. Tab screws.
    behind = [(-330, 320, 260), (-40, 20, 5), (0, 0, 1)]
    sc.step("3 / 10", "2 x M3 x 12 down the two hex-key channels into the tab's brass inserts | "
            "(2.5 mm key). Snug only: the inserts sit in the gripper's plastic.",
            n + 8, fly(["tab_screws"], (0, -1, 0), 60), cam_to=behind, hold=15)
    # 4. Carrier: Pi nuts in first, then onto the gripper, then the clamp screws.
    pi_side = [(420, 280, 240), (10, 25, 5), (0, 0, 1)]
    show(["carrier"])
    sc.step("4 / 10", "Carrier: 4 x M2.5 nuts into the traps on its inner face now (they're hard to | "
            "reach later), then close the collar round the body from the other side.",
            n + 10, both(fly(["pi_nuts"], (1, 0, 0), 25), delay(move_group("carrier_sub", (0, 0, 0)), 0.35)),
            cam_to=pi_side, hold=14)
    sc.step("4 / 10", "4 x M3 x 16 through the carrier's plate into the bracket's nuts: tighten evenly | "
            "until the 1 mm split closes up and the collar grips the body.",
            n + 4, fly(["clamp_screws"], (-1, 0, 0), 40), hold=14)
    # 5. Pod sub-assembly, off to the side.
    pod_at = np.array([-120, 60, 70])
    pod_view = [tuple(np.array(c) + pod_at * (i < 2)) for i, c in enumerate(
        [(-260, -250, 170), (-75, 45, 20), (0, 0, 1)])]
    show(["pod"])
    sc.step("5 / 10", "Next, the camera pod, off the gripper.", 10, lambda u: None, hold=0,
            cam_to=[(-600, -420, 520), (-110, 40, 40), (0, 0, 1)])
    sc.step("5 / 10", "Camera pod: HQ Camera on its four tall bosses, ribbon connector toward the tongue. | "
            "4 x M2.5 x 12 from the plate's front, nuts on the back of the board.",
            n + 10, both(fly(["hq_pcb", "hq_mount"], -back, 40), delay(fly(["hq_screws"], back, 25), 0.4),
                         delay(fly(["hq_nuts"], -back, 25), 0.55)), cam_to=pod_view, hold=14)
    sc.step("6 / 10", "Thread the 6 mm lens into the CS mount. Camera Module 3 Wide above it: | "
            "4 x M2 x 10 from the front, nuts behind. Plug a 300 mm Standard-Mini ribbon into each camera.",
            n + 10, both(fly(["hq_lens"], -back, 45), delay(fly(["cm_pcb", "cm_module"], -back, 30), 0.3),
                         delay(fly(["cm_screws"], back, 20), 0.55), delay(fly(["cm_nuts"], -back, 20), 0.7)),
            hold=14)
    # 7. Pod onto the web.
    sc.step("7 / 10", "Set the pod's tongue on the web and fix it with 2 x M3 x 16 into the web's nuts. | "
            "The pod can come off again without touching the collar or the tab screws.",
            n + 12, both(move_group("pod_sub", (0, 0, 0)), delay(fly(["pod_screws"], -back, 35), 0.6)),
            cam_to=[(-360, 260, 300), (-55, 30, 10), (0, 0, 1)], hold=15)
    # 8. Pi 5.
    sc.step("8 / 10", "Pi 5 with its Active Cooler: 4 printed spacers, then 4 x M2.5 x 12 from the top | "
            "into the carrier's nuts. USB-C faces the arm; feed it from a magnetic breakaway adapter.",
            n + 12, both(fly(["pi_spacers"], (-1, 0, 0), 30), delay(fly(["pi5"], (-1, 0, 0), 60), 0.25),
                         delay(fly(["pi_screws"], (-1, 0, 0), 40), 0.6)), cam_to=pi_side, hold=15)
    # 9. Ribbons.
    lens = {k: route_length(v) for k, v in routes.items()}

    def ribbons(u):
        for k in routes:
            sc.alpha[f"ribbon_{k}"] = u
    sc.step("9 / 10", f"Ribbons to CAM/DISP 0 and 1, both crossing in front of the collar's back edge, | "
            f"clear of the gripper's power/CAN jumper. Routes about {lens['hq']:.0f} mm (HQ) and "
            f"{lens['cm3w']:.0f} mm (Wide).", n, ribbons, cam_to=[(300, -380, 330), (-10, 20, 5), (0, 0, 1)],
            hold=18)
    # 10. Tag wedges.
    sc.step("10 / 10", "Print tags.pdf at 100 %, glue tag #1 and #2 onto the two wedges, and stick a wedge on | "
            "each finger's outer face, 17.5 mm behind the tip (VHB tape), tag facing the HQ Camera.",
            n + 8, both(fly(["wedge0", "wedge1"], (1, 0, 0), 40), delay(fly(["tag0", "tag1"], (1, 0, 0), 40), 0.0)),
            cam_to=[(-210, -200, 95), (-22, -58, 5), (0, 0, 1)], hold=15)
    # Done: swing round.
    sc.step("", "Assembled.", 12, lambda u: None, hold=0, cam_to=[(-420, -330, 260), (-10, 10, 5), (0, 0, 1)])
    start = np.array(sc.cam[0], float)
    focus = np.array([-10, 10, 5.0])
    r = start - focus

    def orbit(u):
        a = math.radians(-120 * u)
        rot = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
        sc.cam = [tuple(focus + rot @ r), tuple(focus), (0, 0, 1)]
    sc.cam = [tuple(start), tuple(focus), (0, 0, 1)]
    sc.step("", "Assembled: bracket, pod and carrier clamp the gripper body; nothing sits behind the J6 flange face.",
            32, orbit, hold=15)
    sc.save(RENDERS / "assembly_steps.gif")
    print({k: round(v) for k, v in lens.items()})


if __name__ == "__main__":
    main()
