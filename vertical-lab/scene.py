"""Scene framework for the vertical-lab animations: atomizer-training/viz3d/scene.py from
#124's branch (after #239's ``piper-camera-mount/cad/animate.py``), with the atomizer's own
loaders taken out.

A Scene holds PyVista actors grouped so sub-assemblies move together (groups can have parents:
the equipment rides on its tray). Each ``step()`` is one sub-step: a caption, a number of frames
over which ``update(u)`` is called with an eased u = 0 -> 1, an optional camera move,
leader-line labels, then a hold. Frames are rendered once at 1280 x 720 and written two ways:

* ``out/mp4/<name>.mp4``: every frame, 15 fps, h264 yuv420p
* ``out/<name>.gif``: every 1.5th frame (10 fps), 800 x 450, one palette, gifsicle -O3 --lossy

Text (title, step label, caption, gauges, leader labels) is drawn with PIL on top of each
output at its own resolution. ``out/<name>.json`` records the frame range of each sub-step.
``VIZ3D_CLEAN=1`` drops every piece of text and writes only ``out/clean/<name>.mp4``;
``VIZ3D_SIZE=1920x1080`` and ``VIZ3D_FPS=30`` change the frame size and rate (moves keep their
duration in seconds). ``PREVIEW=1`` renders only the last frame of each sub-step, to /tmp.
"""
from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import numpy as np
import pyvista as pv
import vtk
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FPS = int(os.environ.get("VIZ3D_FPS", "15"))
GIF_FPS = 10
SIZE = tuple(int(v) for v in os.environ.get("VIZ3D_SIZE", "1280x720").split("x"))
CLEAN = bool(os.environ.get("VIZ3D_CLEAN"))     # no text at all; writes out/clean/ only (see the docstring)
HD = bool(os.environ.get("VIZ3D_HD"))           # out/hd/ with the text and out/clean/ without (see the docstring)
HD_CLEAN = os.environ.get("VIZ3D_HD_CLEAN", "1") != "0"   # VIZ3D_HD_CLEAN=0: out/hd/ only, no out/clean/ copy
INLINE_AUDIT = bool(os.environ.get("VIZ3D_AUDIT"))   # a render that also checks its own frames (collide.Auditor)
GIF_SIZE = (800, 450)
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
PREVIEW = bool(os.environ.get("PREVIEW"))   # render only the last frame of each sub-step, to /tmp
AUDIT = bool(os.environ.get("ARM_AUDIT"))   # render nothing; check the arms every frame -> out/collisions/ (collide.py)


FLATTISH = {"skin", "panel", "roof", "floor", "walls", "counter"}      # big flat parts: no sheen, so GIFs compress

# Render style (#303 review: "the amount of sheen is a bit distracting, looks like early 2000s renders").
# * Hard edges stay hard. The meshes are welded (lab._merge cleans duplicate points), so plain smooth shading averages
#   the normals across every crease: flat panels then fade from white to grey like cushions, and a disc's top and side
#   blend into a pillow. Normals are split wherever neighbouring faces meet at more than FEATURE_ANGLE.
# * Specular follows a material's 0-1 "shininess" (the fifth number in the MATERIALS tables) on a curve: paint and
#   plastic come out close to matte, metal and glass keep a small, tight highlight.
# * The key light comes from up and to the left, with a weaker headlight than VTK's default light kit, so a box reads
#   in three tones (top, front, side) instead of one flat grey. (Screen-space ambient occlusion was tried too: eight
#   times slower per frame on the runner's software renderer, for little visible difference.)
FEATURE_ANGLE = 35.0


def surface_style(shininess: float) -> dict:
    """specular and specular_power for a material's 0-1 shininess."""
    s = min(max(float(shininess), 0.0), 1.0)
    return dict(specular=0.30 * s * s, specular_power=12.0 + 68.0 * s)


def light_kit(renderer) -> None:
    kit = vtk.vtkLightKit()
    kit.SetKeyLightElevation(50.0)
    kit.SetKeyLightAzimuth(-25.0)
    kit.SetKeyLightIntensity(0.85)
    kit.SetKeyToFillRatio(2.6)
    kit.SetKeyToHeadRatio(6.0)
    kit.SetKeyToBackRatio(4.0)
    kit.AddLightsToRenderer(renderer)


def _wait_for_x(timeout=60.0):
    """Under heavy load Xvfb can still be starting when xvfb-run hands over; VTK then fails with 'bad X server
    connection'. Wait until the display accepts a connection."""
    if not os.environ.get("DISPLAY"):
        return
    import ctypes
    import time
    try:
        x11 = ctypes.cdll.LoadLibrary("libX11.so.6")
    except OSError:
        return
    x11.XOpenDisplay.restype = ctypes.c_void_p
    t0 = time.time()
    while time.time() - t0 < timeout:
        d = x11.XOpenDisplay(None)
        if d:
            x11.XCloseDisplay(ctypes.c_void_p(d))
            return
        time.sleep(0.5)


_wait_for_x()


def _quick_exit():
    """At interpreter exit, after every other atexit handler (registered first, so it runs last): flush and leave
    with os._exit. A whole-lab scene's teardown frees thousands of VTK wrappers, each a walk of VTK's ghost map, and a
    finished render sat there for minutes holding its render slot. Files are closed by then (encoders in save())."""
    import sys
    try:
        sys.stdout.flush()
        sys.stderr.flush()
    finally:
        os._exit(1 if _FAILED else 0)


_FAILED: list = []
if os.environ.get("VIZ3D_QUICK_EXIT", "1") != "0":
    import atexit
    import sys as _sys
    _hook0 = _sys.excepthook

    def _hook(t, v, tb):                     # an uncaught error still exits 1
        _FAILED.append(t)
        _hook0(t, v, tb)
    _sys.excepthook = _hook
    atexit.register(_quick_exit)


_FONTS: dict = {}
_WRAP: dict = {}

# What a frame says, where it differs from what the code says (round 14, run D). Universal Robots renamed the UR10e the
# UR12e in June 2025, for the 12.5 kg it already carried; the arm is mechanically unchanged (notes/ur12e.md). The code,
# its identifiers, the notes and the old clips keep "UR10e"; every title, status, label and caption drawn from here on
# says "UR12e". Same length and digit widths, so no layout moves.
ON_SCREEN = {"UR10e": "UR12e"}


def shown(text: str) -> str:
    """`text` with ON_SCREEN's names, as a frame shows it."""
    for a, b in ON_SCREEN.items():
        text = text.replace(a, b)
    return text


class _Shown:
    """An ImageDraw that draws and measures text through shown()."""

    def __init__(self, d):
        self._d = d

    def __getattr__(self, name):
        return getattr(self._d, name)

    def text(self, xy, text, *a, **k):
        return self._d.text(xy, shown(text), *a, **k)

    def textlength(self, text, *a, **k):
        return self._d.textlength(shown(text), *a, **k)


def _plotter(size) -> pv.Plotter:
    """pv.Plotter(off_screen=True). Round 13: on a loaded runner (three renders and the audits, load 7-12), VTK's first
    X connection in a new process failed about half the time ("bad X server connection"), and VTK fell back to OSMesa,
    which isn't installed: the render then died at its first frame, after the scene build. A second try connects, so a
    window that came up as OSMesa while DISPLAY is set is closed and made again."""
    import time
    pl = None
    for attempt in range(40):
        pl = pv.Plotter(off_screen=True, window_size=size, lighting="none")
        if not os.environ.get("DISPLAY") or pl.render_window.GetClassName() != "vtkOSOpenGLRenderWindow":
            if attempt:
                print(f"scene.py: an X window on try {attempt + 1}", flush=True)
            return pl
        pl.close()
        time.sleep(0.5 + 0.25 * min(attempt, 8))
    return pl


def font(size, bold=False, mono=False):
    """A DejaVu face, loaded once per (size, style): the overlay asks for its fonts on every frame."""
    key = (int(round(size)), bool(bold), bool(mono))
    f = _FONTS.get(key)
    if f is None:
        name = "DejaVuSansMono.ttf" if mono else ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
        f = _FONTS[key] = ImageFont.truetype(str(FONT_DIR / name), key[0])
    return f


def size_scale(size) -> float:
    """Pixel sizes (points) were chosen at 1280 x 720; this keeps them the same fraction of the frame."""
    return size[1] / 720


def ease(u: float) -> float:
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def window(u, t0, t1):
    """Re-map u so the action happens between t0 and t1 of the step (eased)."""
    return ease((u - t0) / max(t1 - t0, 1e-6))


def mix(a, b, u):
    return tuple(float(x) + (float(y) - float(x)) * u for x, y in zip(a, b))


# ------------------------------------------------------------------------------- 4x4 transforms
def T(v) -> np.ndarray:
    m = np.eye(4)
    m[:3, 3] = v
    return m


def R(axis, deg, pivot=(0, 0, 0)) -> np.ndarray:
    """Rotation by deg about `axis` through `pivot`."""
    a = np.asarray(axis, float)
    a = a / np.linalg.norm(a)
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    x, y, z = a
    rot = np.array([[c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
                    [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
                    [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)]])
    m = np.eye(4)
    m[:3, :3] = rot
    p = np.asarray(pivot, float)
    return T(p) @ m @ T(-p)


def S(scale, pivot=(0, 0, 0)) -> np.ndarray:
    m = np.eye(4)
    m[0, 0], m[1, 1], m[2, 2] = scale
    p = np.asarray(pivot, float)
    return T(p) @ m @ T(-p)


def _vtk_matrix(m: np.ndarray) -> vtk.vtkMatrix4x4:
    vm = vtk.vtkMatrix4x4()
    for i in range(4):
        for j in range(4):
            vm.SetElement(i, j, float(m[i, j]))
    return vm


class Scene:
    def __init__(self, name: str, title: str, size=SIZE, gif=True, mp4=True):
        self.name, self.title, self.size = name, title, size
        self.pl = _plotter(size)
        light_kit(self.pl.renderer)
        self.pl.set_background("white")
        # VIZ3D_AA: "fxaa" (default since round 13: a screen-space filter, enough at 1920 x 1080), "ssaa" (renders
        # oversampled: round 12's default, measured in round 13 at twice fxaa's CPU per 1080p frame, 1.82 s against
        # 0.91 s on a chapter-4 frame), "msaa" or "none"
        aa = os.environ.get("VIZ3D_AA", "fxaa")
        if aa != "none":
            self.pl.enable_anti_aliasing(aa)
        # VIZ3D_PEELS (round 13: 3, was 6): VTK's dual depth peeling costs about the same per pass whatever is
        # see-through, and peels two layers a pass. On a chapter-1 frame with 20 small translucent parts, 6 passes took
        # 1.38-1.57 s of CPU and 3 took 1.11-1.18 s (no peeling: 0.68), with 600-1000 of 2 million pixels changed by
        # more than 8 levels, all where see-through parts overlap. An occlusion ratio didn't stop the passes early.
        self.pl.enable_depth_peeling(number_of_peels=int(os.environ.get("VIZ3D_PEELS", "3")), occlusion_ratio=0.0)
        self._peel_on = True      # depth peeling is switched off for a frame with nothing see-through (render_base)
        self.actors: dict[str, vtk.vtkActor] = {}
        self.group_of: dict[str, str] = {}
        self.parent: dict[str, str] = {}
        self.gmat: dict[str, np.ndarray] = {}
        self.alpha: dict[str, float] = {}
        self.base_alpha: dict[str, float] = {}
        self.color: dict[str, tuple] = {}
        self.ambient: dict[str, float] = {}
        # deferred cutaways: parts can be added twice, whole ("whole") and halved ("half"); cut_f[group] (or cut_f["*"])
        # blends between them, so an animation can start on the closed machine and open the cutaway when it is needed.
        # Ghosted shells (ghost_of) go from opaque to their see-through opacity on the same factor.
        self.cutrole: dict[str, str] = {}
        self.ghost_of: dict[str, float] = {}
        self.cut_f: dict[str, float] = {}
        self.cam = [(3000, -3000, 2500), (0, 0, 900), (0, 0, 1)]
        self.view_angle = 30.0
        self.caption = ""
        self.label = ""
        self.gauges: list[tuple[str, str]] = []
        self.labels: list[tuple[str, tuple, tuple, float]] = []   # (text, xyz, (fx, fy), alpha)
        self.n = 0                     # frames written to the MP4
        self.substeps: list[dict] = []
        self.gif_frames: list[Image.Image] = []
        self.still: tuple[int, np.ndarray] | None = None
        self.want_still = False
        self.mp4 = self.mp4_text = None
        self.preview: list[Image.Image] = []
        if PREVIEW or AUDIT:
            mp4 = gif = False
        if CLEAN or HD:
            gif = False
        self.mp4_dir = OUT / ("clean" if CLEAN or HD else "mp4")
        if mp4:
            self.mp4_path = self.mp4_dir / f"{name}.mp4"
            if HD:      # the clean one is also the input of ../ppt/'s captioned clips; both are kept as delivered
                # round 13: crf 16 at x264's "faster" (VIZ3D_PRESET) in place of crf 18 "slow": these are intermediates
                # that longform.py encodes again, and "slow" cost the runner CPU the renders needed
                pre = os.environ.get("VIZ3D_PRESET", "faster")
                self.mp4 = encoder(self.mp4_path, size, crf=16, preset=pre) if HD_CLEAN else None
                self.mp4_text_path = OUT / "hd" / f"{name}.mp4"
                self.mp4_text = encoder(self.mp4_text_path, size, crf=16, preset=pre)
            else:
                self.mp4 = encoder(self.mp4_path, size, crf=16 if CLEAN else 21)
        self.gif = gif
        self.intro = 1.0          # seconds of establishing view before the first sub-step's motion
        self.robots: list = []    # robot.Robot instances in the scene (they register themselves)
        self.frame_hooks: list = []   # f(scene) after every frame's update, before it is drawn
        self.auditor = None
        if AUDIT:
            import collide
            self.auditor = collide.Auditor(self)
            self.frame_hooks.append(self.auditor)

    # ------------------------------------------------------------------------------- actors
    def add(self, name, poly, color, group="static", opacity=1.0, shown=True, **kw):
        if poly is None:
            return None
        style = dict(smooth_shading=True, split_sharp_edges=True, feature_angle=FEATURE_ANGLE, ambient=0.22,
                     diffuse=0.80)
        shine = kw.pop("specular", 0.35)
        if any(k in name for k in FLATTISH):
            shine = min(shine, 0.15)
        style.update(surface_style(shine))
        if "point_size" in kw:                                  # sized for 720p: the same on screen at any VIZ3D_SIZE
            kw["point_size"] = kw["point_size"] * size_scale(self.size)
        style.update(kw)
        actor = self.pl.add_mesh(poly, color=color, opacity=opacity, **style)
        self.actors[name] = actor
        self._hold(name, actor)
        self.group_of[name] = group
        self.base_alpha[name] = opacity
        self.alpha[name] = 1.0 if shown else 0.0
        self.gmat.setdefault(group, np.eye(4))
        return actor

    def set_mesh(self, name, poly):
        self.actors[name].GetMapper().SetInputData(poly)
        self._hold(name, self.actors[name])

    def _hold(self, name, actor):
        """Keep the Python wrappers of an actor's property, mapper and mesh alive for the scene's life. pyvista's are
        Python subclasses of the VTK classes, so whenever a temporary one (actor.GetProperty(), GetMapper(), GetInput())
        is dropped, VTK's wrapping keeps a "ghost" of it and walks every ghost it holds to purge dead ones: 0.5 ms a
        call with 2,600 actors, 1.4 s a frame in apply() alone and as much again in the collision checker's
        per-frame scan. A wrapper still referenced is found and returned as it is, and nothing is ghosted."""
        keep = self.__dict__.setdefault("_keep", {})
        m = actor.GetMapper()
        keep[name] = (actor.GetProperty(), m, m.GetInput() if m is not None else None)
        return keep[name]

    def world(self, group: str) -> np.ndarray:
        m = self.gmat.get(group, np.eye(4))
        g = group
        while g in self.parent:
            g = self.parent[g]
            m = self.gmat.get(g, np.eye(4)) @ m
        return m

    def apply(self):
        """Each group's world matrix and each part's visibility, opacity, colour and ambient onto its actor. Only what
        changed since the last call goes to VTK: a whole-lab scene (2,600 actors) spent 1.4 s a frame here re-sending
        all of it, twice its render time. A group's matrix is one vtkMatrix4x4 shared by its actors, new whenever the
        matrix changes; an actor touched from outside since (its or its property's MTime moved) is re-sent in full."""
        cache = {}
        mats = self.__dict__.setdefault("_gmats", {})
        sent = self.__dict__.setdefault("_sent", {})
        keep = self.__dict__.setdefault("_keep", {})
        for name, actor in self.actors.items():
            g = self.group_of[name]
            vm = cache.get(g)
            if vm is None:
                w = self.world(g)
                key = w.tobytes()
                prev = mats.get(g)
                if prev is None or prev[0] != key:
                    vm = vtk.vtkMatrix4x4()
                    vm.DeepCopy(np.asarray(w, float).ravel().tolist())
                    mats[g] = (key, vm)
                else:
                    vm = prev[1]
                cache[g] = vm
            a = self.alpha[name]
            op = self.base_alpha[name]
            role, gh = self.cutrole.get(name), self.ghost_of.get(name)
            if role or gh is not None:
                f = self.cut_f.get(g, self.cut_f.get("*", 1.0))
                if role:
                    a *= f if role == "half" else 1.0 - f
                if gh is not None:
                    op = 1.0 + (gh - 1.0) * f
            vis = a > 0.02
            opac = min(1.0, op * a)
            col = self.color.get(name)
            col = tuple(float(c) for c in col) if col is not None else None
            amb = self.ambient.get(name)
            held = keep.get(name)
            if held is None:
                held = self._hold(name, actor)
            prop = held[0]
            rec = sent.get(name)
            if rec is not None and rec[0] == actor.GetMTime() and rec[1] == prop.GetMTime():
                if rec[2] is vm and rec[3] == vis and rec[4] == opac and rec[5] == col and rec[6] == amb:
                    continue
                if rec[2] is not vm:
                    actor.SetUserMatrix(vm)
                if rec[3] != vis:
                    actor.SetVisibility(vis)
                if rec[4] != opac:
                    prop.SetOpacity(opac)
                if col is not None and rec[5] != col:
                    prop.SetColor(*col)
                if amb is not None and rec[6] != amb:
                    prop.SetAmbient(amb)
            else:
                actor.SetUserMatrix(vm)
                actor.SetVisibility(vis)
                prop.SetOpacity(opac)
                if col is not None:
                    prop.SetColor(*col)
                if amb is not None:
                    prop.SetAmbient(amb)
            sent[name] = (actor.GetMTime(), prop.GetMTime(), vm, vis, opac, col, amb)

    def show(self, names, a=1.0):
        for n in names:
            self.alpha[n] = a

    def members(self, group):
        return [n for n, g in self.group_of.items() if g == group]

    # ------------------------------------------------------------------------------ overlay
    def project(self, xyz) -> tuple[float, float]:
        ren = self.pl.renderer
        ren.SetWorldPoint(float(xyz[0]), float(xyz[1]), float(xyz[2]), 1.0)
        ren.WorldToDisplay()
        dx, dy, _ = ren.GetDisplayPoint()
        return dx / self.size[0], 1.0 - dy / self.size[1]

    def overlay(self, img: Image.Image, scale: float, anchors) -> Image.Image:
        if CLEAN:
            return img
        W, H = img.size
        d = _Shown(ImageDraw.Draw(img, "RGBA"))   # "UR10e" in the code is drawn "UR12e" (ON_SCREEN)
        s = max(scale, 0.80)                      # GIF text is kept larger than a straight downscale
        pad = 10 * s
        # title, top left; smaller (down to 70 %) or cut short if it would run under the step label
        ft = font(19 * s, bold=True)
        if self.title:
            room = W - 40 * s - (d.textlength(self.label, font=font(17 * s, bold=True)) + 2 * pad + 10 * s
                                 if self.label else 0)
            title, k = self.title, 1.0
            tw = d.textlength(title, font=ft)
            if tw > room:
                k = max(0.7, room / tw)
                ft = font(19 * s * k, bold=True)
                while d.textlength(title, font=ft) > room and len(title) > 8:
                    title = title[:-2].rstrip() + "…"
                tw = d.textlength(title, font=ft)
            d.rounded_rectangle((6 * s, 6 * s, 22 * s + tw, 6 * s + 30 * s * max(k, 0.85)), 6 * s,
                                fill=(255, 255, 255, 215))
            d.text((14 * s, 10 * s), title, font=ft, fill=(20, 20, 24))
        # step label, top right
        if self.label:
            fl = font(17 * s, bold=True)
            w = d.textlength(self.label, font=fl)
            d.rounded_rectangle((W - w - 2 * pad - 10 * s, 8 * s, W - 10 * s, 8 * s + 30 * s), 6 * s,
                                fill=(30, 60, 140, 235))
            d.text((W - w - pad - 10 * s, 12 * s), self.label, font=fl, fill=(255, 255, 255))
        # gauges, under the title
        if self.gauges:
            fg = font(15 * s, mono=True)
            y = 42 * s
            wmax = max(d.textlength(f"{k:<10}{v}", font=fg) for k, v in self.gauges)
            d.rounded_rectangle((10 * s, y - 4 * s, 10 * s + wmax + 2 * pad, y + len(self.gauges) * 21 * s + 4 * s),
                                6 * s, fill=(245, 247, 250, 225), outline=(190, 196, 204, 255))
            for k, v in self.gauges:
                d.text((10 * s + pad, y), f"{k:<10}", font=fg, fill=(90, 94, 100))
                kw = d.textlength(f"{k:<10}", font=fg)
                d.text((10 * s + pad + kw, y), v, font=fg, fill=(15, 15, 20))
                y += 21 * s
        # leader labels
        fl = font(14 * s)
        for (text, _, (fx, fy), a), (px, py) in zip(self.labels, anchors):
            if a <= 0.02:
                continue
            al = int(255 * a)
            tx, ty = fx * W, fy * H
            lines = text.split("\n")
            tw = max(d.textlength(t, font=fl) for t in lines)
            th = len(lines) * 17 * s
            left = fx < 0.5
            bx0 = tx if left else tx - tw - 12 * s
            box = (bx0, ty - th / 2 - 4 * s, bx0 + tw + 12 * s, ty + th / 2 + 4 * s)
            ex = box[2] if left else box[0]
            d.line([(ex, ty), (px * W, py * H)], fill=(60, 60, 66, al), width=max(1, int(round(1.6 * s))))
            r = 3.2 * s
            d.ellipse((px * W - r, py * H - r, px * W + r, py * H + r), fill=(40, 40, 46, al),
                      outline=(255, 255, 255, al))
            d.rounded_rectangle(box, 5 * s, fill=(255, 255, 255, int(225 * a)), outline=(120, 124, 130, al))
            for i, t in enumerate(lines):
                d.text((bx0 + 6 * s, box[1] + 4 * s + i * 17 * s), t, font=fl, fill=(20, 20, 24, al))
        # caption, bottom
        if self.caption:
            fc = font(18 * s)
            maxw = W - 60 * s
            memo = _WRAP.get((self.caption, W, s))       # round 13: wrapped once per caption, not on every frame
            if memo is None:
                paras = [p.strip() for p in self.caption.split("|")]
                lines = []
                for p in paras:
                    words, cur = p.split(), ""
                    for w_ in words:
                        t = (cur + " " + w_).strip()
                        if d.textlength(t, font=fc) > maxw and cur:
                            lines.append(cur)
                            cur = w_
                        else:
                            cur = t
                    lines.append(cur)
                memo = _WRAP[(self.caption, W, s)] = lines
            lines = memo
            lh = 24 * s
            h = len(lines) * lh + 2 * pad
            d.rectangle((0, H - h - 8 * s, W, H), fill=(255, 255, 255, 232))
            d.line([(0, H - h - 8 * s), (W, H - h - 8 * s)], fill=(30, 60, 140, 255), width=max(1, int(2 * s)))
            for i, t in enumerate(lines):
                d.text((30 * s, H - h - 8 * s + pad + i * lh), t, font=fc, fill=(15, 15, 20))
        return img

    # ------------------------------------------------------------------------------- frames
    def _needs_peeling(self) -> bool:
        """Whether this frame has anything see-through to peel. Depth peeling costs a quarter of a 1080p frame's CPU
        even when nothing is translucent (round 13: 0.91 s against 0.70 s on a chapter-4 frame), and with nothing
        translucent the picture is the same without it. Anything added to the renderer outside Scene.add keeps it on."""
        ren = self.pl.renderer
        if ren.GetActors().GetNumberOfItems() != len(self.actors) or ren.GetVolumes().GetNumberOfItems():
            return True
        for a in self.actors.values():
            if a.GetVisibility() and a.HasTranslucentPolygonalGeometry():
                return True
        return False

    def _set_camera(self):
        """The camera onto VTK. pyvista's camera_position setter resets the clipping range from every visible actor's
        bounds, a tenth of a whole-lab frame's main-thread time (round 13, py-spy on chapters 5 and 7). Here the visible
        bounds are taken every VIZ3D_CLIP_EVERY frames (8), padded by a metre for whatever moves in between, and the
        clipping range is set from those. The first frame goes through pyvista, so its camera counts as set."""
        every = int(os.environ.get("VIZ3D_CLIP_EVERY", "8"))
        n = self.__dict__.get("_clip_n", 0)
        self._clip_n = n + 1
        if every <= 1 or n == 0:
            self.pl.camera_position = self.cam
            self.pl.camera.view_angle = self.view_angle
            return
        ren = self.pl.renderer
        cam = ren.GetActiveCamera()
        cam.SetPosition(*(float(v) for v in self.cam[0]))
        cam.SetFocalPoint(*(float(v) for v in self.cam[1]))
        cam.SetViewUp(*(float(v) for v in self.cam[2]))
        cam.SetViewAngle(float(self.view_angle))
        b = self.__dict__.get("_clip_b")
        if b is None or n % every == 0:
            vb = ren.ComputeVisiblePropBounds()
            if vb[0] > vb[1]:                         # nothing visible
                b = None
            else:
                pad = 1000.0
                b = self._clip_b = (vb[0] - pad, vb[1] + pad, vb[2] - pad, vb[3] + pad, vb[4] - pad, vb[5] + pad)
        if b is not None:
            ren.ResetCameraClippingRange(*b)
        else:
            ren.ResetCameraClippingRange()

    def render_base(self) -> np.ndarray:
        self.apply()
        self._set_camera()
        if os.environ.get("VIZ3D_PEEL", "auto") == "auto":
            need = self._needs_peeling()
            if need != self.__dict__.get("_peel_on", True):
                self.pl.renderer.SetUseDepthPeeling(need)
                self._peel_on = need
        self.pl.render()
        return self.pl.screenshot(return_img=True)

    def snap(self, n=1):
        if INLINE_AUDIT and not (AUDIT or PREVIEW) and not self.__dict__.get("_inline_checked"):
            # VIZ3D_AUDIT=1: check this render's own frames, as ARM_AUDIT=1 would without rendering, unless the clip
            # attaches an auditor of its own (most chapters do); its report is written at save()
            self._inline_checked = True
            import collide
            if not any(isinstance(h, collide.Auditor) for h in self.frame_hooks):
                self.inline_auditor = collide.Auditor(self)
                self.frame_hooks.append(self.inline_auditor)
        if AUDIT:
            if self.auditor is not None and any(k in self.auditor.snap_frames for k in range(self.n, self.n + n)):
                self.auditor.picture(self)
            self.n += n
            return None
        base = self.render_base()
        anchors = [self.project(xyz) for _, xyz, _, _ in self.labels]
        # HD: the text keeps the share of the frame it has at 1280 x 720
        hi = self.overlay(Image.fromarray(base), size_scale(self.size) if HD else 1.0, anchors)
        if self.want_still:
            self.still = (self.n, np.asarray(hi).copy())
            self.want_still = False
        # HD: self.mp4 is the text-free copy, unless VIZ3D_HD_CLEAN=0 (then it is only ever a clip's own encoder, which
        # wants the frame as shown, text and all)
        for proc, frame in ((self.mp4, base if HD and HD_CLEAN else hi), (self.mp4_text, hi)):
            if proc is not None:
                buf = np.asarray(frame.convert("RGB") if isinstance(frame, Image.Image) else frame).tobytes()
                for _ in range(n):
                    proc.stdin.write(buf)
        lo = None
        for i in range(n):
            k = self.n + i
            # GIF frame j shows MP4 frame floor(j * FPS / GIF_FPS)
            if self.gif and math.floor(math.ceil(k * GIF_FPS / FPS) * FPS / GIF_FPS) == k:
                if lo is None:
                    small = Image.fromarray(base).resize(GIF_SIZE, Image.LANCZOS)
                    lo = self.overlay(small, GIF_SIZE[0] / self.size[0], anchors).convert("RGB")
                self.gif_frames.append(lo)
        self.n += n
        return hi

    def step(self, label, caption, seconds, update=None, hold=1.2, cam_to=None, labels=(), still=False,
             view_angle_to=None, live=False):
        """One sub-step: `seconds` of motion (update(u), u eased 0 -> 1, camera to `cam_to`), then `hold` s."""
        start = self.n
        self.label = label
        self.caption = " ".join(caption.split())
        if self.n == 0 and not PREVIEW:
            # a clean establishing view first (no leader labels): it shows during the tutorial's crossfade
            self.labels = []
            self.snap(int(round(self.intro * FPS)))
        frames = max(1, int(round(seconds * FPS)))
        cam_from = [np.array(v, float) for v in self.cam]
        va_from = self.view_angle
        lab_from = {t: a for t, _, _, a in self.labels}
        new = [(t, xyz, at) for t, xyz, at in labels]
        new_texts = {t for t, _, _ in new}
        for i in range(1, frames + 1):
            u = i / frames
            e = ease(u)
            if update is not None:
                update(e)
            if cam_to is not None:
                self.cam = [tuple(a + (np.array(b, float) - a) * e) for a, b in zip(cam_from, cam_to)]
            if view_angle_to is not None:
                self.view_angle = va_from + (view_angle_to - va_from) * e
            for h in self.frame_hooks:
                h(self)
            fade = min(1.0, u * 3)
            self.labels = [(t, xyz, at, fade if t not in lab_from else 1.0) for t, xyz, at in new] + \
                          [(t, xyz, at, max(0.0, 1 - u * 3)) for t, xyz, at, a in self.labels
                           if t not in new_texts and a > 0.02 and (t, xyz, at) not in new]
            self.labels = [l for l in self.labels if l[3] > 0.02 or l[0] in new_texts]
            if still and i == frames:
                self.want_still = True
            if PREVIEW and i < frames:
                self.n += 1
                continue
            img = self.snap()
            if PREVIEW:
                self.preview.append(img)
        self.labels = [(t, xyz, at, 1.0) for t, xyz, at in new]
        if hold > 0 and not PREVIEW:
            if live and update is not None:       # particles, flow and vibration keep going through the hold
                for _ in range(max(1, int(round(hold * FPS)))):
                    update(1.0)
                    for h in self.frame_hooks:
                        h(self)
                    self.snap()
            else:
                self.snap(max(1, int(round(hold * FPS))))
        self.substeps.append(dict(label=label, caption=self.caption, start_frame=start, end_frame=self.n - 1))

    # --------------------------------------------------------------------------------- save
    def save(self):
        if AUDIT:
            self.pl.close()
            return self.auditor.save()
        if PREVIEW:
            self.pl.close()
            tw, th = 640, 360
            cols = 3
            rows = (len(self.preview) + cols - 1) // cols
            sheet = Image.new("RGB", (tw * cols, th * rows), "white")
            for i, im in enumerate(self.preview):
                sheet.paste(im.convert("RGB").resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
            sheet.save(f"/tmp/preview_{self.name}.png")
            print("preview", self.name, len(self.preview))
            return
        OUT.mkdir(parents=True, exist_ok=True)
        for proc in (self.mp4, self.mp4_text):
            if proc is not None:
                proc.stdin.close()
                proc.wait()
        meta = dict(name=self.name, fps=FPS, n_frames=self.n, size=list(self.size), substeps=self.substeps)
        jpath = (self.mp4_dir if CLEAN or HD else OUT).joinpath(f"{self.name}.json")
        jpath.parent.mkdir(parents=True, exist_ok=True)          # out/clean/instruments/ when no clean MP4 made it
        jpath.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
        if self.__dict__.get("inline_auditor") is not None:      # after the video and its JSON are safe on disk
            try:
                self.inline_auditor.save()
            except Exception as e:
                print(f"{self.name}: the inline audit's report failed to save: {e!r}", flush=True)
        if self.still is not None and not (CLEAN or HD):
            Image.fromarray(self.still[1]).convert("RGB").save(OUT / f"{self.name}_still.png", optimize=True)
        info = f"{self.name}: {self.n} frames, {self.n / FPS:.1f} s"
        if self.mp4 is not None and self.mp4_path.exists():
            info += f", mp4 {self.mp4_path.stat().st_size / 1e6:.1f} MB"
        if self.mp4_text is not None:
            info += f", with text {self.mp4_text_path.stat().st_size / 1e6:.1f} MB"
        if self.gif and self.gif_frames:
            path = OUT / f"{self.name}.gif"
            write_gif(self.gif_frames, path)
            info += f", gif {len(self.gif_frames)} frames {path.stat().st_size / 1e6:.2f} MB"
        self.pl.close()
        print(info, flush=True)
        return info


def encoder(path: Path, size, crf, preset="medium") -> subprocess.Popen:
    """ffmpeg reading raw RGB frames on stdin, writing h264 yuv420p at FPS."""
    path.parent.mkdir(parents=True, exist_ok=True)
    return subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}",
         "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
         *(["-threads", os.environ["FFMPEG_THREADS"]] if os.environ.get("FFMPEG_THREADS") else []),   # runner_guard: 2
         "-movflags", "+faststart", str(path)], stdin=subprocess.PIPE)


def write_gif(frames, path: Path, colors=128, lossy=60, limit_mb=4.9):
    # palette from a 3 x 3 mosaic at half size, so small saturated parts (the yellow switch, the coil) get colours
    picks = frames[:: max(1, len(frames) // 8)][:9]
    tw, th = frames[0].width // 2, frames[0].height // 2
    mosaic = Image.new("RGB", (tw * 3, th * 3), "white")
    for i, f in enumerate(picks):
        mosaic.paste(f.resize((tw, th)), ((i % 3) * tw, (i // 3) * th))
    pal = mosaic.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=int(1000 / GIF_FPS), loop=0, optimize=False,
              disposal=1)
    if shutil.which("gifsicle"):
        # lossy re-encode; camera moves change every pixel, so step down the palette too if needed
        tries = [(lossy, None), (lossy + 50, None), (lossy + 90, 96), (lossy + 140, 64), (lossy + 190, 48)]
        for k, (lv, cols) in enumerate(tries):
            tmp = path.with_suffix(".tmp.gif")
            cmd = ["gifsicle", "-O3", f"--lossy={lv}"] + (["--colors", str(cols)] if cols else [])
            subprocess.run(cmd + ["-o", str(tmp), str(path)], check=True)
            if tmp.stat().st_size / 1e6 <= limit_mb or k == len(tries) - 1:
                tmp.replace(path)
                break
            tmp.unlink()


def lighter(c, k=0.45):
    return tuple(x + (1 - x) * k for x in c)
