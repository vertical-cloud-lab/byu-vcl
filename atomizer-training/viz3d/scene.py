"""Scene framework for the rePowder step animations (after #239's ``piper-camera-mount/cad/animate.py``).

A Scene holds PyVista actors for the CadQuery parts, grouped so sub-assemblies move together
(groups can have parents: the ultrasonic stack rides on the door). Each ``step()`` is one
sub-step: a caption, a number of frames over which ``update(u)`` is called with an eased
u = 0 -> 1, an optional camera move, leader-line labels, then a hold. Frames are rendered once at
1280 x 720 and written two ways:

* ``out/mp4/<name>.mp4``: every frame, 15 fps, h264 yuv420p (for the narrated tutorials)
* ``out/<name>.gif``: every 1.5th frame (10 fps), 800 x 450, one palette, gifsicle -O3 --lossy

Text (title, step label, caption, gauge readouts, leader labels) is drawn with PIL on top of
each output at its own resolution, so the GIF's text is drawn at GIF size rather than shrunk.
``out/<name>.json`` records the frame range of each sub-step in the MP4, for timing narration.

For videos that add their own captions (``../ppt/``), ``VIZ3D_CLEAN=1`` drops every piece of text and writes only
``out/clean/<name>.mp4`` and ``.json``, leaving the committed GIF, still and JSON alone. ``VIZ3D_SIZE=1920x1080`` and
``VIZ3D_FPS=30`` change the frame size and rate; every move keeps its duration in seconds, so the speed is the same.

``VIZ3D_HD=1`` writes both from the same frames: ``out/hd/<name>.mp4`` with all the GIF's text, drawn at the same share
of the frame as at 1280 x 720, and the clean ``out/clean/<name>.mp4`` and ``.json``. It too leaves the GIF, still and
JSON alone. Used with ``VIZ3D_SIZE`` and ``VIZ3D_FPS`` for the MP4s in ``../ppt/videos/animations/``.
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
GIF_SIZE = (800, 450)
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
PREVIEW = bool(os.environ.get("PREVIEW"))   # render only the last frame of each sub-step, to /tmp


FLATTISH = {"cabinet", "heat_exchanger", "base_frame", "platform", "chamber", "vacuum_pump",
            "hmi", "door"}


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


def font(size, bold=False, mono=False):
    name = "DejaVuSansMono.ttf" if mono else ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    return ImageFont.truetype(str(FONT_DIR / name), int(round(size)))


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


def temp_color(t: float, cold=(0.70, 0.72, 0.75)) -> tuple:
    """Grey below ~450 C, then dull red, orange, yellow-orange: an incandescence ramp for the charge."""
    stops = [(20, cold), (450, cold), (560, (0.45, 0.16, 0.12)), (680, (0.78, 0.18, 0.06)),
             (800, (1.00, 0.42, 0.08)), (1000, (1.00, 0.68, 0.25))]
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            return mix(c0, c1, (max(t, t0) - t0) / (t1 - t0))
    return stops[-1][1]


MELT = (1.0, 0.45, 0.10)


class Scene:
    def __init__(self, name: str, title: str, size=SIZE, gif=True, mp4=True):
        self.name, self.title, self.size = name, title, size
        self.pl = pv.Plotter(off_screen=True, window_size=size, lighting="light kit")
        self.pl.set_background("white")
        self.pl.enable_anti_aliasing("ssaa")
        self.pl.enable_depth_peeling(number_of_peels=6, occlusion_ratio=0.0)
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
        if PREVIEW:
            mp4 = gif = False
        if CLEAN or HD:
            gif = False
        self.mp4_dir = OUT / ("clean" if CLEAN or HD else "mp4")
        if mp4:
            self.mp4_path = self.mp4_dir / f"{name}.mp4"
            if HD:      # the clean one is also the input of ../ppt/'s captioned clips; both are kept as delivered
                self.mp4 = encoder(self.mp4_path, size, crf=18, preset="slow")
                self.mp4_text_path = OUT / "hd" / f"{name}.mp4"
                self.mp4_text = encoder(self.mp4_text_path, size, crf=18, preset="slow")
            else:
                self.mp4 = encoder(self.mp4_path, size, crf=16 if CLEAN else 21)
        self.gif = gif
        self.intro = 1.0          # seconds of establishing view before the first sub-step's motion

    # ------------------------------------------------------------------------------- actors
    def add(self, name, poly, color, group="static", opacity=1.0, shown=True, **kw):
        if poly is None:
            return None
        style = dict(smooth_shading=True, specular=0.35, specular_power=20, ambient=0.18, diffuse=0.85)
        if name.split("#")[0].split(":")[-1] in FLATTISH:      # big flat panels: no sheen, so GIFs compress
            style.update(specular=0.08)
        if "point_size" in kw:                                  # sized for 720p: the same on screen at any VIZ3D_SIZE
            kw["point_size"] = kw["point_size"] * size_scale(self.size)
        style.update(kw)
        actor = self.pl.add_mesh(poly, color=color, opacity=opacity, **style)
        self.actors[name] = actor
        self.group_of[name] = group
        self.base_alpha[name] = opacity
        self.alpha[name] = 1.0 if shown else 0.0
        self.gmat.setdefault(group, np.eye(4))
        return actor

    def set_mesh(self, name, poly):
        self.actors[name].GetMapper().SetInputData(poly)

    def world(self, group: str) -> np.ndarray:
        m = self.gmat.get(group, np.eye(4))
        g = group
        while g in self.parent:
            g = self.parent[g]
            m = self.gmat.get(g, np.eye(4)) @ m
        return m

    def apply(self):
        cache = {}
        for name, actor in self.actors.items():
            g = self.group_of[name]
            if g not in cache:
                cache[g] = self.world(g)
            actor.SetUserMatrix(_vtk_matrix(cache[g]))
            a = self.alpha[name]
            op = self.base_alpha[name]
            role, gh = self.cutrole.get(name), self.ghost_of.get(name)
            if role or gh is not None:
                f = self.cut_f.get(g, self.cut_f.get("*", 1.0))
                if role:
                    a *= f if role == "half" else 1.0 - f
                if gh is not None:
                    op = 1.0 + (gh - 1.0) * f
            actor.SetVisibility(a > 0.02)
            actor.GetProperty().SetOpacity(min(1.0, op * a))
            if name in self.color:
                actor.GetProperty().SetColor(*self.color[name])
            if name in self.ambient:
                actor.GetProperty().SetAmbient(self.ambient[name])

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
        d = ImageDraw.Draw(img, "RGBA")
        s = max(scale, 0.80)                      # GIF text is kept larger than a straight downscale
        pad = 10 * s
        # title, top left
        ft = font(19 * s, bold=True)
        if self.title:
            tw = d.textlength(self.title, font=ft)
            d.rounded_rectangle((6 * s, 6 * s, 22 * s + tw, 36 * s), 6 * s, fill=(255, 255, 255, 215))
            d.text((14 * s, 10 * s), self.title, font=ft, fill=(20, 20, 24))
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
            lh = 24 * s
            h = len(lines) * lh + 2 * pad
            d.rectangle((0, H - h - 8 * s, W, H), fill=(255, 255, 255, 232))
            d.line([(0, H - h - 8 * s), (W, H - h - 8 * s)], fill=(30, 60, 140, 255), width=max(1, int(2 * s)))
            for i, t in enumerate(lines):
                d.text((30 * s, H - h - 8 * s + pad + i * lh), t, font=fc, fill=(15, 15, 20))
        return img

    # ------------------------------------------------------------------------------- frames
    def render_base(self) -> np.ndarray:
        self.apply()
        self.pl.camera_position = self.cam
        self.pl.camera.view_angle = self.view_angle
        self.pl.render()
        return self.pl.screenshot(return_img=True)

    def snap(self, n=1):
        base = self.render_base()
        anchors = [self.project(xyz) for _, xyz, _, _ in self.labels]
        # HD: the text keeps the share of the frame it has at 1280 x 720
        hi = self.overlay(Image.fromarray(base), size_scale(self.size) if HD else 1.0, anchors)
        if self.want_still:
            self.still = (self.n, np.asarray(hi).copy())
            self.want_still = False
        for proc, frame in ((self.mp4, base if HD else hi), (self.mp4_text, hi)):
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
                    self.snap()
            else:
                self.snap(max(1, int(round(hold * FPS))))
        self.substeps.append(dict(label=label, caption=self.caption, start_frame=start, end_frame=self.n - 1))

    # --------------------------------------------------------------------------------- save
    def save(self):
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
        (self.mp4_dir if CLEAN or HD else OUT).joinpath(f"{self.name}.json").write_text(
            json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
        if self.still is not None and not (CLEAN or HD):
            Image.fromarray(self.still[1]).convert("RGB").save(OUT / f"{self.name}_still.png", optimize=True)
        info = f"{self.name}: {self.n} frames, {self.n / FPS:.1f} s"
        if self.mp4 is not None:
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


# ------------------------------------------------------------------------------ the machine
def lighter(c, k=0.45):
    return tuple(x + (1 - x) * k for x in c)


def load_machine(sc: Scene, cut=(), hide=(), ghost: dict | None = None, pipes=True, defer=False):
    """Add every model part to the scene. Parts whose group is in `cut` (or all cuttable parts when
    cut == "all") are shown halved at y = 0 with their cut faces tinted lighter. `ghost` maps part
    names to an opacity, for see-through shells. With defer=True the machine starts closed: the halves
    and ghosts wait until set_cut() opens them (whole copies are added as "w:<part>")."""
    import model
    ms = model.meshes()
    ghost = ghost or {}
    if defer:
        sc.cut_f["*"] = 0.0
    for name, m in ms.items():
        if name in hide:
            continue
        wants = cut == "all" or m["group"] in cut or name in cut
        if wants and m.get("gone"):            # entirely in the cut-away half
            if defer:
                sc.add("w:" + name, m["whole"], m["color"], m["group"], opacity=m["opacity"])
                sc.cutrole["w:" + name] = "whole"
                sc.cut_f[m["group"]] = 0.0
            continue
        halved = m["half"] is not None and wants
        op = ghost.get(name, m["opacity"])
        if op <= 0:
            continue
        if name == "floor":
            sc.add(name, m["whole"], m["color"], m["group"], ambient=1.0, diffuse=0.0, specular=0.0,
                   smooth_shading=False)
        elif halved:
            sc.add(name, m["half"], m["color"], m["group"], opacity=op)
            if m["half_cut"] is not None:
                sc.add(name + "#cut", m["half_cut"], lighter(m["color"]), m["group"], opacity=op,
                       smooth_shading=False, ambient=0.55, diffuse=0.5, specular=0.0)
            if defer:
                sc.add("w:" + name, m["whole"], m["color"], m["group"], opacity=m["opacity"])
                sc.cutrole.update({name: "half", name + "#cut": "half", "w:" + name: "whole"})
                sc.cut_f[m["group"]] = 0.0
        elif defer and name in ghost:
            sc.add(name, m["whole"], m["color"], m["group"], opacity=1.0)
            sc.ghost_of[name] = op
        else:
            sc.add(name, m["whole"], m["color"], m["group"], opacity=op)
    if pipes:
        for name, p in model.pipe_routes().items():
            if pipes is not True and name not in pipes:
                continue
            sc.add("pipe_" + name, pv.Spline(np.array(p["pts"], float), 120).tube(radius=p["r"], n_sides=14),
                   p["color"], "pipes")
    # the stack rides on the door; the lever and the rod ride on the post's piston ("arm_base", which lifts them to pour),
    # the lever swings up about its pivot on its own ("arm"); the nozzle in its holder, the holder on the crucible
    for g in ("connector", "sonotrode", "booster", "transducer", "cover"):
        sc.parent[g] = "door"
    sc.parent["plate"] = "connector"            # the plate and the upper sonotrode are held on the connector
    sc.parent["upper"] = "connector"
    sc.parent["arm"] = "arm_base"
    sc.parent["rod"] = "arm_base"
    sc.parent["nozzle"] = "holder"
    sc.parent["holder"] = "crucible"
    sc.parent["splash"] = "container"           # the splash disc sits in the container's top flange
    return ms


def set_cut(sc: Scene, f: float, groups=None):
    """Blend deferred cutaways: 0 = the closed machine, 1 = cut open. `groups` limits it to some part groups."""
    if groups is None:
        for k in list(sc.cut_f):
            sc.cut_f[k] = f
    else:
        for g in groups:
            sc.cut_f[g] = f


def names_of(sc: Scene, group: str) -> list[str]:
    return [n for n, g in sc.group_of.items() if g == group]
