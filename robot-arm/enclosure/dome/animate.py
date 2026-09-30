"""Assembly GIF and a still of the finished spot D enclosure.

    xvfb-run -a python animate.py [still] [gif]

The GIF is kept light on purpose: 640 x 480, about 100 frames, one fixed camera and a shared
palette, so only the moving parts change from frame to frame. It renders in a minute or two.
"""

import sys
import time

import numpy as np
import pyvista as pv
from PIL import Image

import build as B
import parts as P
from piper_fk import Piper

SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
MOVE, LAST = 8, 18                  # frames per step, frames for the last step
MOVE_MS, HOLD_MS = 70, 1500
CAMERA = [(-2.35, -3.35, 2.05), (0.0, -0.05, 0.43), (0, 0, 1)]


def ease(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def translate(v):
    M = np.eye(4)
    M[:3, 3] = v
    return M


class Scene:
    def __init__(self, size, arm_keep=0.35):
        self.pl = pl = pv.Plotter(off_screen=True, window_size=size, lighting="three lights")
        pl.set_background(SURFACE)
        tx, ty, tt = B.TABLE["x"] / 2, B.TABLE["y"] / 2, B.TABLE["t"]
        for y0, y1 in ((-ty, -0.0015), (0.0015, ty)):
            pl.add_mesh(pv.Box((-tx, tx, y0, y1, -tt, 0)), color="#26272a", ambient=0.2)

        self.items = B.layout()
        self.actors = []
        for it in self.items:
            smooth = not it.part.name.startswith("plywood")
            a = pl.add_mesh(pv.wrap(it.world), color=it.part.color, smooth_shading=smooth,
                            split_sharp_edges=smooth, specular=0.3 if "cloth" not in it.tags else 0.0,
                            ambient=0.12)
            self.actors.append(a)
        self.flap = next(a for a, it in zip(self.actors, self.items) if "flap" in it.tags)
        roll = B.flap_roll()
        self.roll = pl.add_mesh(pv.wrap(roll), color=P.canvas_panel(1, 1).color, smooth_shading=True)
        self.roll_origin = roll.centroid

        self.piper = Piper()
        self.arm = []
        for link, m, c in B.arm_meshes(self.piper, keep=arm_keep, world=False):
            a = pl.add_mesh(pv.wrap(m), color=c, smooth_shading=True, specular=0.25)
            self.arm.append((link, a))
        base = next(it for it in self.items if "base" in it.tags)
        self.arm_item = B.Item(base.part, np.eye(4), 2, (0, 0, 0.5), (0, 0.5), lift=base.lift)
        self.caption = None
        pl.camera_position = CAMERA
        pl.camera.view_angle = 28

    def offset(self, it, s, u):
        """Displacement of an item from its place at step s, fraction u; None if not there yet."""
        if s < it.step:
            return None
        off = np.zeros(3)
        if s == it.step:
            a, b = it.window
            if u < a:
                return None
            off += np.asarray(it.entry, float) * (1 - ease((u - a) / (b - a)))
        if it.lift:
            vec, s_low = it.lift
            if s < s_low:
                off += vec
            elif s == s_low:
                off += np.asarray(vec, float) * (1 - ease(u))
        return off

    def pose(self, s, u, q=B.REST):
        for it, a in zip(self.items, self.actors):
            off = self.offset(it, s, u)
            a.visibility = off is not None
            if off is not None:
                a.position = off
        off = self.offset(self.arm_item, s, u)
        poses = self.piper.fk(q, grip=0.01)
        base = B.arm_base()
        for link, a in self.arm:
            a.visibility = off is not None
            if off is not None:
                a.user_matrix = translate(off) @ base @ poses[link]
        # last step: roll the flap up under its rail
        last = len(B.STEPS) - 1
        roll_u = ease(u / 0.35) if s == last else 0.0
        top = np.array([0, self.flap.center[1], B.Z0 + B.SPAN["z"]])
        self.flap.origin = top
        self.flap.scale = (1, 1, max(1 - roll_u, 1e-3))
        self.flap.visibility = bool(self.flap.visibility and roll_u < 0.97)
        self.roll.visibility = bool(s == last and roll_u > 0.3)
        if self.caption is not None:
            self.pl.remove_actor(self.caption)
        self.caption = self.pl.add_text(f"{s + 1}/{len(B.STEPS)}   {B.STEPS[s]}", position="upper_left",
                                        font_size=10, color=INK)

    def shot(self):
        self.pl.render()
        return self.pl.screenshot(return_img=True)


def gif(path, size=(640, 480)):
    t0 = time.time()
    sc = Scene(size)
    sc.pl.enable_anti_aliasing("fxaa")
    frames, ms = [], []
    last = len(B.STEPS) - 1
    for s in range(len(B.STEPS)):
        n = 1 if s == 0 else (LAST if s == last else MOVE)
        for k in range(n):
            u = (k + 1) / n
            q = B.REST
            if s == last:
                q = B.REST + (B.PICK - B.REST) * ease((u - 0.4) / 0.6)
            sc.pose(s, u, q)
            frames.append(Image.fromarray(sc.shot()))
            ms.append(HOLD_MS if k == n - 1 else MOVE_MS)
    ms[-1] = 3000
    sc.pl.close()
    # one palette for every frame, so unchanged pixels stay identical and compress away
    pal = frames[-1].quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=ms, loop=0, optimize=False, disposal=1)
    print(f"{path.name}: {len(frames)} frames, {path.stat().st_size / 1e6:.2f} MB, {time.time() - t0:.0f} s")


def still(path, size=(1400, 1050)):
    sc = Scene(size, arm_keep=None)
    last = len(B.STEPS) - 1
    sc.pose(last, 1.0, B.PICK)
    sc.pl.remove_actor(sc.caption)
    sc.pl.enable_anti_aliasing("ssaa")
    Image.fromarray(sc.shot()).save(path)
    sc.pl.close()
    print(path.name)


if __name__ == "__main__":
    what = sys.argv[1:] or ["still", "gif"]
    if "still" in what:
        still(B.HERE / "dome-finished.png")
    if "gif" in what:
        gif(B.HERE / "dome-assembly.gif")
