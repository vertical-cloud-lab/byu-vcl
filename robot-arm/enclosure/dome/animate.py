"""Assembly GIF and a still of the finished spot D enclosure.

    xvfb-run -a python animate.py [parts] [still] [gif]

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
CLOSE = [(-0.80, -1.35, 0.16), (0.0, 0.0, 0.33), (0, 0, 1)]   # just under the raised base, steps 2 and 3
FINAL = [(-1.00, -2.90, 1.35), (0.0, -0.05, 0.50), (0, 0, 1)]  # into the open front, last step


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
            cloth = "cloth" in it.tags
            a = pl.add_mesh(pv.wrap(it.world), color=it.part.color, smooth_shading=smooth,
                            split_sharp_edges=smooth, specular=0.0 if cloth else 0.3,
                            ambient=0.35 if cloth else 0.12, diffuse=0.7 if cloth else 1.0)
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
        # camera: close on the base while the arm goes on, then out to the whole enclosure
        v = {1: 1 - ease(u), 2: 0.0, 3: ease(u)}.get(s, 1.0)
        pos, foc = [np.add(np.multiply(CLOSE[i], 1 - v), np.multiply(CAMERA[i], v)) for i in (0, 1)]
        if s == last:
            w = ease((u - 0.3) / 0.7)
            pos, foc = [np.add(np.multiply(p, 1 - w), np.multiply(FINAL[i], w)) for i, p in enumerate((pos, foc))]
        self.pl.camera_position = [tuple(pos), tuple(foc), (0, 0, 1)]
        if self.caption is not None:
            self.pl.remove_actor(self.caption)
        self.caption = self.pl.add_text(f"{s + 1}/{len(B.STEPS)}  {B.STEPS[s]}", position="upper_left",
                                        font_size=13, color=INK)

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
    sc.pl.camera_position = CAMERA
    sc.pl.enable_anti_aliasing("ssaa")
    Image.fromarray(sc.shot()).save(path)
    sc.pl.close()
    print(path.name)


def _part_shot(meshes, camera, size=(520, 440), angle=30):
    pl = pv.Plotter(off_screen=True, window_size=size, lighting="three lights")
    pl.set_background(SURFACE)
    for m, c, smooth in meshes:
        pl.add_mesh(pv.wrap(m), color=c, smooth_shading=smooth, split_sharp_edges=smooth, specular=0.3)
    pl.camera_position = camera
    pl.camera.view_angle = angle
    pl.enable_anti_aliasing("ssaa")
    img = pl.screenshot(return_img=True)
    pl.close()
    return img


def parts_sheet(path):
    """Each part on its own, with the numbers it is built from."""
    import matplotlib.pyplot as plt

    X = lambda R, t=(0, 0, 0): B.T(R, t)  # noqa: E731
    elbow, clamp, screw = P.formufit_elbow(), P.snap_clamp(), P.m5_socket_cap()
    stub = P.pvc_pipe(0.07)
    wc, pc = elbow.color, "#e9e9e5"
    em = elbow.mesh
    legs = []
    for ax, pull in ((0, 0.0), (1, 0.0), (2, 0.03)):
        d = np.eye(3)[ax]
        legs.append((stub.mesh.copy().apply_transform(X(B.rot_z_to(d), d * (P.ELBOW_STOP + pull))), pc, True))
    img1 = _part_shot([(em, wc, True), *legs], [(0.21, -0.17, 0.16), (0.035, 0.035, 0.045), (0, 0, 1)])

    pipe = P.pvc_pipe(0.16).mesh.copy().apply_transform(X(B.rot_z_to((1, 0, 0))))
    img2 = _part_shot([(pipe, pc, True)], [(0.26, -0.20, 0.10), (0.08, 0, 0), (0, 0, 1)])

    alone = clamp.mesh.copy().apply_transform(X(B.rot_z_to((1, 0, 0), (0, 0, -1))))
    img3 = _part_shot([(alone, clamp.color, True)], [(0.13, -0.11, -0.02), (0, 0, 0), (0, 0, 1)])

    sm = screw.mesh.copy().apply_transform(X(B.rot_z_to((0, 0, -1), (1, 0, 0))))
    img4 = _part_shot([(sm, screw.color, True)], [(0.05, -0.065, 0.02), (0, 0, -0.011), (0, 0, 1)])

    ply = P.plywood_base()
    under = [(ply.mesh, ply.color, False)]
    for x, y in P.hole_xy():
        under.append((screw.mesh.copy().apply_transform(X(np.eye(3), (x, y, -P.PLY["t"] + P.CBORE_H))), screw.color, True))
    img5 = _part_shot(under, [(0.075, -0.095, -0.14), (0, 0, -0.01), (0, 0, 1)])

    piper = Piper()
    arm = [(m, c, True) for _, m, c in B.arm_meshes(piper, q=B.PICK, grip=0.03, keep=None)]
    base = (ply.mesh.copy().apply_transform(B.T(t=(0, 0, P.PLY["t"]))), ply.color, False)
    img6 = _part_shot([base, *arm], [(1.05, -1.25, 0.75), (0.0, -0.18, 0.18), (0, 0, 1)])

    cards = [
        (img1, "FORMUFIT 3-way elbow", "2.250 in overall, 1.293 in OD, 1.001 in socket.\nPipe stops 15.3 mm from the corner, so\nevery pipe is cut 30.6 mm under its span."),
        (img2, "3/4 in Sch 40 PVC", "1.050 in OD, 0.113 in wall.\nCut 4 each at 1219, 1289 and 1035 mm\nfrom six 10 ft sticks."),
        (img3, "Snap clamp", "4 in long ABS, 0.90 in ID relaxed.\nSnaps over the pipe with the cloth\nunder it. 33 in all, 3 per pipe."),
        (img4, "M5 × 25 socket cap", "ISO 4762: 8.5 mm head, 4 mm hex.\nUp through the plywood, 13 mm\ninto the arm's threaded base."),
        (img5, "Plywood base, from below", "24 × 48 × 0.703 in birch panel.\n4 × Ø5.5 mm on a 70 mm square,\nØ10 mm counterbores 6 mm deep."),
        (img6, "PiPER on the base", "AgileX URDF and meshes.\n626 mm reach to the flange,\n0.77 m to the fingertips."),
    ]
    fig = plt.figure(figsize=(15, 11), dpi=110, facecolor=SURFACE)
    for i, (img, title, note) in enumerate(cards):
        x, top = 0.02 + (i % 3) * 0.33, 1 - (i // 3) * 0.5
        fig.text(x, top - 0.04, title, fontsize=15, color=INK, weight="bold")
        ax = fig.add_axes([x - 0.01, top - 0.39, 0.31, 0.33])
        ax.imshow(img)
        ax.axis("off")
        fig.text(x, top - 0.395, note, fontsize=11.5, color=INK2, va="top", linespacing=1.45)
    fig.savefig(path, facecolor=SURFACE)
    print(path.name)


if __name__ == "__main__":
    what = sys.argv[1:] or ["still", "gif", "parts"]
    if "parts" in what:
        parts_sheet(B.HERE / "dome-parts.png")
    if "still" in what:
        still(B.HERE / "dome-finished.png")
    if "gif" in what:
        gif(B.HERE / "dome-assembly.gif")
