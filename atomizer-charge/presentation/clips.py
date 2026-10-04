"""Presentation versions of the three machining clips from PR #232, for #248.

The #232 clips (machining_cup.gif, machining_plug.gif, fill_and_vent.gif) carry a title, a step counter, a note,
a caption line and leader-line callouts, and most steps are on screen for one to three and a half seconds. These
are for a slide instead:

  * text in one place only: one caption at a time, centred in a band under the picture
  * at most six words per caption and no numbers, so nothing on screen can go out of date
  * every caption stays up for at least MIN_CAPTION_S seconds; save() refuses to write a clip that breaks either rule
  * 1280x720, each clip as a looping GIF (drops straight into Google Slides) and an H.264 MP4 (PowerPoint, Keynote)

The motion is re-rendered from the same build123d model, with more frames per step, using machining.py's geometry
and drawing helpers, rather than stretched from the old GIFs.

    xvfb-run -a python clips.py              # all three -> out/{cup,plug,fill}.{gif,mp4}
    xvfb-run -a python clips.py plug         # one of them
    xvfb-run -a python clips.py --preview    # two frames per move -> out/preview_<clip>.png, to check framing

Needs build123d, pyvista, matplotlib, pillow, numpy, and ffmpeg (on PATH, or from the imageio-ffmpeg wheel).
machining.py, charge_cad.py and render.py come from ../cad/ once #232 is merged, and from its commit until then.
"""

from __future__ import annotations

import math
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CHARGE = os.path.dirname(HERE)  # atomizer-charge/
REPO = os.path.dirname(CHARGE)
PR232_COMMIT = "323adba"  # head of PR #232 when these were built
CACHE = os.environ.get("CLIPS_CACHE", "/tmp/al/pr232-cad")
OUT = os.path.join(HERE, "out")

W, H = 1280, 720
BAND = 104  # caption band along the bottom; the picture is everything above it
VIEW_H = H - BAND
FONT_PX = 44
INK = (11, 11, 11)
FRAME_S = 0.1  # 10 fps while anything moves
MIN_CAPTION_S = 5.0
MAX_WORDS = 6
FPS_MP4 = 30
PREVIEW = "--preview" in sys.argv


def cad_dir():
    """Directory holding PR #232's machining.py and the two modules it imports."""
    names = ("machining.py", "charge_cad.py", "render.py")
    local = os.path.join(CHARGE, "cad")
    if all(os.path.exists(os.path.join(local, n)) for n in names):
        return local
    os.makedirs(CACHE, exist_ok=True)
    for n in names:
        dst = os.path.join(CACHE, n)
        if not os.path.exists(dst):
            blob = subprocess.run(["git", "-C", REPO, "show", f"{PR232_COMMIT}:atomizer-charge/cad/{n}"],
                                  check=True, capture_output=True).stdout
            with open(dst, "wb") as f:
                f.write(blob)
    return CACHE


sys.path.insert(0, cad_dir())
import machining as m  # noqa: E402

cad, pv, rr = m.cad, m.pv, m.rr

# Draw CAD edges on top of the faces they bound. Without this, half of every circular edge z-fights with its own
# surface and comes out dashed, which is what #232's clips show.
from vtkmodules.vtkRenderingCore import vtkMapper  # noqa: E402

vtkMapper.SetResolveCoincidentTopologyToPolygonOffset()
vtkMapper.SetResolveCoincidentTopologyPolygonOffsetParameters(1.0, 2.0)

PARTS ={k: v for k, v in cad.build().items() if k in ("std_cup", "std_plug")}
AL = rr.MAT["al"]
SPIN = m.RPM * 0.5  # #232 turns the spindle 33 deg a frame at 5 fps; same speed at 10 fps

# Re-framed for 16:9 with nothing to keep clear at the top, and centred now there are no callouts to the right
CUP_CAM = dict(focal=(33.0, -1.5, 4.0), scale=41.0)
PLUG_CAM = dict(focal=(21.0, 0.0, -1.0), scale=33.5)
CUP_PART_CAM = ((0.0, 0.0, m.CUP_L / 2), (0.55, -1.0, 0.42), 39.0)
PLUG_PART_CAM = ((0.0, 0.0, cad.PLUG_L / 2 - 0.6), (0.55, -1.0, 0.78), 9.5)
FILL_CAM = ((0.0, 0.0, m.CUP_L / 2 + 12.0), (0.42, -1.0, 0.30), 49.0)


def font_path():
    from matplotlib import font_manager

    return font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold"))


def steps(n):
    """n eased values 0..1 for one move; just the two ends in --preview."""
    return [0.0, 1.0] if PREVIEW else [m.ease(i, n) for i in range(n)]


def turn_about_z(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a), v[2])


class Clip(m.Scene):
    """machining.Scene, but each frame is (picture, caption, seconds) and the only text is the caption band."""

    def __init__(self, name):
        self.name = name
        self.w, self.h = W, VIEW_H
        self.pl = pv.Plotter(off_screen=True, window_size=(W * m.SS, VIEW_H * m.SS), lighting="light_kit")
        self.pl.set_background("white")
        self.pl.enable_parallel_projection()
        self.frames: list[list] = []
        self.font = ImageFont.truetype(font_path(), FONT_PX)

    def picture(self):
        self.pl.render()  # screenshot() alone keeps the previous camera, which shows on the first frame after a cut
        return Image.fromarray(self.pl.screenshot(return_img=True)).resize((W, VIEW_H), Image.LANCZOS)

    def add(self, pic, caption, seconds=FRAME_S):
        frame = Image.new("RGB", (W, H), "white")
        frame.paste(pic, (0, 0))
        ImageDraw.Draw(frame).text((W / 2, VIEW_H + BAND / 2), caption, font=self.font, fill=INK, anchor="mm")
        self.frames.append([frame, caption, seconds])

    def grab(self, caption, **_):
        """Called by machining.lathe_frame; titles, notes, callouts and dimensions are never drawn."""
        self.add(self.picture(), caption)

    def linger(self, seconds):
        self.frames[-1][2] = round(self.frames[-1][2] + seconds, 2)

    def dissolve(self, caption, n=5):
        """Cross-fade from the last frame's picture to whatever the plotter holds now."""
        start, end = self.frames[-1][0].crop((0, 0, W, VIEW_H)), self.picture()
        for k in range(1, 1 if PREVIEW else n):
            self.add(Image.blend(start, end, k / n), caption)
        self.add(end, caption)

    def runs(self):
        """[(caption, seconds on screen)] in order."""
        out = []
        for _, caption, seconds in self.frames:
            if out and out[-1][0] == caption:
                out[-1][1] += seconds
            else:
                out.append([caption, seconds])
        return [(c, round(s, 2)) for c, s in out]

    def save(self):
        self.pl.close()
        os.makedirs(OUT, exist_ok=True)
        if PREVIEW:
            return self.contact_sheet()
        for caption, seconds in self.runs():
            words = len(caption.split())
            assert words <= MAX_WORDS, f"{self.name}: {caption!r} is {words} words"
            assert seconds >= MIN_CAPTION_S, f"{self.name}: {caption!r} is up for only {seconds} s"
        self.write_gif()
        self.write_mp4()
        total = sum(s for _, _, s in self.frames)
        print(f"{self.name}: {len(self.frames)} frames, {total:.1f} s")
        t = 0.0
        for caption, seconds in self.runs():
            print(f"  {t:5.1f}-{t + seconds:5.1f} s  {caption}")
            t += seconds

    def write_gif(self, colours=256):
        imgs = [f for f, _, _ in self.frames]
        sample = Image.fromarray(np.vstack([np.asarray(im) for im in imgs[:: max(1, len(imgs) // 24)]]))
        pal = sample.quantize(colors=colours, method=Image.Quantize.MEDIANCUT)
        q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in imgs]
        # Median cut averages each box, so the background comes out (252, 252, 252): a grey rectangle on a white
        # slide. Adding a pure white entry doesn't help, as Pillow's palette lookup is approximate and still picks
        # the grey one, so turn whichever entry the background landed on white. The band's corner is always background.
        bg = q[0].getpixel((2, H - 2))
        p = pal.getpalette()[: 3 * colours]
        p[3 * bg: 3 * bg + 3] = [255, 255, 255]
        for im in q:
            im.putpalette(p)
        ms = [int(round(s * 1000)) for _, _, s in self.frames]
        path = os.path.join(OUT, f"{self.name}.gif")
        q[0].save(path, save_all=True, append_images=q[1:], duration=ms, loop=0, disposal=1)
        print(f"wrote out/{self.name}.gif  {os.path.getsize(path) / 1e6:.1f} MB")

    def write_mp4(self):
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg is None:
            import imageio_ffmpeg

            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        path = os.path.join(OUT, f"{self.name}.mp4")
        enc = subprocess.Popen([ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS_MP4), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                                "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", path],
                               stdin=subprocess.PIPE)
        for frame, _, seconds in self.frames:
            enc.stdin.write(frame.tobytes() * int(round(seconds * FPS_MP4)))
        enc.stdin.close()
        assert enc.wait() == 0, "ffmpeg failed"
        print(f"wrote out/{self.name}.mp4  {os.path.getsize(path) / 1e6:.1f} MB")

    def contact_sheet(self):
        tiles = [f.resize((W // 4, H // 4)) for f, _, _ in self.frames]
        cols = 4
        sheet = Image.new("RGB", (cols * W // 4, -(-len(tiles) // cols) * H // 4), (200, 200, 200))
        for k, t in enumerate(tiles):
            sheet.paste(t, ((k % cols) * W // 4, (k // cols) * H // 4))
        sheet.save(os.path.join(OUT, f"preview_{self.name}.png"))
        if os.environ.get("PREVIEW_FRAMES"):  # every frame full size too, for a closer look
            os.makedirs(os.environ["PREVIEW_FRAMES"], exist_ok=True)
            for k, (f, _, _) in enumerate(self.frames):
                f.save(os.path.join(os.environ["PREVIEW_FRAMES"], f"{self.name}_{k:02d}.png"))
        print(f"wrote out/preview_{self.name}.png  ({len(tiles)} frames)")


class Lathe:
    """Spindle state for one clip: every frame advances the spin, as in #232."""

    def __init__(self, clip, stick, cam):
        self.c, self.stick, self.cam, self.spin = clip, stick, cam, 0.0

    def frame(self, profile, caption, tools=(), cut=False, stripe_to=None, cam=None):
        m.lathe_frame(self.c, profile, self.spin, tools=tools, cut=cut, stick=self.stick, stripe_to=stripe_to,
                      caption=caption, **(cam or self.cam))
        self.spin += SPIN

    def stage(self, profile, tools=(), cut=False, stripe_to=None, cam=None):
        """Set up a frame without keeping it, so dissolve() can fade to it."""
        pl = self.c.pl
        pl.clear()
        m.show(pl, m.cached("chuck", m.chuck_body), m.CHUCK_C, lw=0.7, spin=self.spin)
        m.show(pl, m.cached("jaws", m.chuck_jaws), m.JAW_C, lw=0.7, spin=self.spin)
        m.show(pl, m.tessellate(m.lay(m.turned(profile)), cut=cut), AL, lw=1.1)
        marks = m.stripes(2.0, stripe_to if stripe_to is not None else self.stick, self.spin, front_only=cut)
        if marks is not None:
            pl.add_mesh(marks, color=m.STRIPE, line_width=2.0 * m.SS)
        for trio, mat, move in tools:
            m.show(pl, trio, mat, lw=0.8, move=move)
        cam = cam or self.cam
        self.c.camera(cam["focal"], m.CAM_DIR, cam["scale"])

    def comes_free(self, stub, part, caption, start, drop, stripe_to):
        """The parted-off piece drops away from the stub left in the chuck."""
        for t in steps(12):
            pl = self.c.pl
            pl.clear()
            m.show(pl, m.cached("chuck", m.chuck_body), m.CHUCK_C, lw=0.7, spin=self.spin)
            m.show(pl, m.cached("jaws", m.chuck_jaws), m.JAW_C, lw=0.7, spin=self.spin)
            m.show(pl, m.tessellate(m.lay(m.turned(stub))), AL, lw=1.1)
            m.show(pl, part, AL, lw=1.1, move=(start + drop[0] * t, 0, -drop[1] * t * t))
            marks = m.stripes(2.0, stripe_to, self.spin)
            if marks is not None:
                pl.add_mesh(marks, color=m.STRIPE, line_width=2.0 * m.SS)
            self.c.camera(self.cam["focal"], m.CAM_DIR, self.cam["scale"])
            self.c.grab(caption)
            self.spin += SPIN


def finished_part(c, solid, cam, caption):
    """Fade in on the finished part, swing round to the section view, then fade the near half away."""
    focal, view, scale = cam
    whole, half = m.tessellate(solid), m.tessellate(solid, cut=True)

    def put(trio, deg):
        c.pl.clear()
        m.show(c.pl, trio, AL, lw=1.2)
        c.camera(focal, turn_about_z(view, deg), scale)

    put(whole, -35)
    c.dissolve(caption)
    for t in steps(20):
        put(whole, -35 * (1 - t))
        c.grab(caption)
    c.linger(0.4)
    put(half, 0)
    c.dissolve(caption, n=8)
    c.linger(2.0)


def reamer():
    """Straight reamer, a hair under size like machining.drill(): chamfered nose, flutes, then a thinner shank."""
    r = cad.CUP_BORE_D / 2 * 0.94
    return m.lay(m.turned([(0, 0), (r - 0.8, 0), (r, 0.8), (r, 52), (r * 0.72, 52), (r * 0.72, 80), (0, 80)]))


# ---------------------------------------------------------------------------
# 1. The cup
# ---------------------------------------------------------------------------
def cup():
    c = Clip("cup")
    S, R, face, depth = m.STICK, m.R, 0.6, cad.CUP_BORE_DEPTH
    end = S - face
    lathe = Lathe(c, S, CUP_CAM)
    bit = m.cached("bit_long", lambda: m.drill(cad.CUP_BORE_D, 75))  # long enough to stick out at full depth
    ream = m.cached("reamer", reamer)
    blade = m.cached("blade", m.parting_blade)

    cap = "Face the end flat"
    for t in steps(10):  # tool in, clear of the bar
        lathe.frame(m.bar_profile(), cap, tools=m.cutter(S + 1.4, -(R + 9 - 8.4 * t), 0))
    for t in steps(30):  # across the end, from the outside to the centre
        fr = R * (1 - t)
        lathe.frame(m.bar_profile(face=face, face_r=fr), cap, stripe_to=end, tools=m.cutter(end, -fr, 0))
    for t in steps(8):  # back off
        lathe.frame(m.bar_profile(face=face), cap, stripe_to=end, tools=m.cutter(end + 3 * t, -(R + 9) * t, 0))
    c.linger(0.4)

    cap = "Drill the pocket"
    lathe.stage(m.bar_profile(face=face), tools=[(bit, m.STEEL, (end + 8, 0, 0))], cut=True, stripe_to=end)
    c.dissolve(cap)
    for t in steps(6):
        lathe.frame(m.bar_profile(face=face), cap, tools=[(bit, m.STEEL, (end + 8 * (1 - t), 0, 0))], cut=True,
                    stripe_to=end)
    for t in steps(30):
        d = depth * t
        lathe.frame(m.bar_profile(face=face, bore=d), cap, tools=[(bit, m.STEEL, (end - d, 0, 0))], cut=True,
                    stripe_to=end)
    c.linger(0.3)
    for t in steps(8):
        lathe.frame(m.bar_profile(face=face, bore=depth), cap, tools=[(bit, m.STEEL, (end - depth + (depth + 8) * t,
                                                                                      0, 0))], cut=True, stripe_to=end)

    cap = "Ream it smooth"
    lathe.stage(m.bar_profile(face=face, bore=depth), tools=[(ream, m.STEEL, (end + 8, 0, 0))], cut=True,
                stripe_to=end)
    c.dissolve(cap, n=4)
    for t in steps(32):  # to the bottom of the straight part of the hole, short of the drill point
        lathe.frame(m.bar_profile(face=face, bore=depth), cap, cut=True, stripe_to=end,
                    tools=[(ream, m.STEEL, (end + 8 - (8 + depth - 0.4) * t, 0, 0))])
    c.linger(0.3)
    for t in steps(12):
        lathe.frame(m.bar_profile(face=face, bore=depth), cap,
                    tools=[(ream, m.STEEL, (end - depth + 0.4 + (depth + 7.6) * t, 0, 0))], cut=True, stripe_to=end)

    cap = "Cut the cup off"
    gz = m.Z_PART - m.GROOVE_W / 2  # blade on the scrap side of the cup
    lathe.stage(m.bar_profile(face=face, bore=depth), tools=[(blade, m.TOOL, (gz, -(R + 10), 0))], stripe_to=end)
    c.dissolve(cap)
    for t in steps(8):
        lathe.frame(m.bar_profile(face=face, bore=depth), cap, stripe_to=end,
                    tools=[(blade, m.TOOL, (gz, -(R + 10 - 10 * t), 0))])
    for t in steps(26):
        r = max(R - (R + 0.4) * t, 0.2)
        lathe.frame(m.bar_profile(face=face, bore=depth, groove_z=gz, groove_r=r), cap, stripe_to=end,
                    tools=[(blade, m.TOOL, (gz, -r, 0))])
    cup_lathe = m.cached("cup_lathe", lambda: m.lay(PARTS["std_cup"]))
    lathe.comes_free(m.bar_profile(stick=m.Z_PART - m.GROOVE_W), cup_lathe, cap, m.Z_PART, (14, 18),
                     stripe_to=m.Z_PART - m.GROOVE_W - 0.4)
    c.linger(0.3)

    finished_part(c, PARTS["std_cup"], CUP_PART_CAM, "The finished cup")
    c.save()


# ---------------------------------------------------------------------------
# 2. The plug
# ---------------------------------------------------------------------------
def plug():
    c = Clip("plug")
    S, R, RB = m.STICK_PLUG, m.R, m.RB
    lathe = Lathe(c, S, PLUG_CAM)
    blade = m.cached("blade", m.parting_blade)
    vent_bit = m.cached("vent", lambda: m.drill(cad.VENT_D, 30, flute=13))
    z_step = S - 16.0  # turned length
    z_cut = S - cad.PLUG_L  # the plug's top face
    gz = z_cut - m.GROOVE_W / 2
    lead_l, lead_tan = cad.PLUG_LEADIN_L, math.tan(math.radians(15))
    turned = dict(step_z=z_step, step_r=RB)
    led = dict(turned, lead=lead_l)
    vented = dict(led, bore_d=cad.VENT_D, bore=14.0)

    cap = "Turn it to fit its cup"
    for t in steps(8):
        lathe.frame(m.bar_profile(S), cap, stripe_to=S, tools=m.cutter(S + 1.0, -(R + 8 - (R + 8 - RB) * t), 0))
    for t in steps(30):  # feed toward the chuck; the step follows the tool
        zt = S - 16.0 * t
        lathe.frame(m.bar_profile(S, step_z=zt, step_r=RB), cap, stripe_to=zt, tools=m.cutter(zt, -RB, 0))
    c.linger(1.4)

    cap = "Taper the end that goes in"
    path = [(z_step, -RB), (z_step + 1.0, -(RB + 4)), (S + 1.0, -(RB + 4)), (S, -RB)]
    for (x0, y0), (x1, y1), n in zip(path, path[1:], (6, 8, 6)):  # out, along, back in at the nose
        for t in steps(n):
            lathe.frame(m.bar_profile(S, **turned), cap, stripe_to=z_step,
                        tools=m.cutter(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, 0))
    for t in steps(16):
        lead = lead_l * t
        lathe.frame(m.bar_profile(S, **turned, lead=lead), cap, stripe_to=z_step,
                    tools=m.cutter(S - lead / 2, -(RB - lead * lead_tan / 2), 0))
    for t in steps(8):
        x0, y0 = S - lead_l / 2, -(RB - lead_l * lead_tan / 2)
        lathe.frame(m.bar_profile(S, **led), cap, stripe_to=z_step,
                    tools=m.cutter(x0 + (S + 4 - x0) * t, y0 + (-(RB + 8) - y0) * t, 0))
    c.linger(0.8)

    cap = "Drill the air hole"
    lathe.stage(m.bar_profile(S, **led), tools=[(vent_bit, m.STEEL, (S + 6, 0, 0))], cut=True, stripe_to=z_step)
    c.dissolve(cap)
    for t in steps(6):
        lathe.frame(m.bar_profile(S, **led), cap, tools=[(vent_bit, m.STEEL, (S + 6 * (1 - t), 0, 0))], cut=True,
                    stripe_to=z_step)
    for t in steps(30):
        d = 14.0 * t
        lathe.frame(m.bar_profile(S, **led, bore_d=cad.VENT_D, bore=d), cap, cut=True, stripe_to=z_step,
                    tools=[(vent_bit, m.STEEL, (S - d, 0, 0))])
    c.linger(0.3)
    for t in steps(10):
        lathe.frame(m.bar_profile(S, **vented), cap, cut=True, stripe_to=z_step,
                    tools=[(vent_bit, m.STEEL, (S - 14.0 + 20.0 * t, 0, 0))])
    c.linger(0.3)

    # The break is 0.4 mm, nothing at the wide view, so zoom in on it. No tool in shot, as in #232: at this zoom
    # the tip is wider than the whole feature and would sit right on top of it.
    cap = "Chamfer the top edge"
    wide, close = PLUG_CAM, dict(focal=(z_cut + 1.0, 0.0, 0.0), scale=10.0)

    def zoom(t):
        f = [a + (b - a) * t for a, b in zip(wide["focal"], close["focal"])]
        return dict(focal=tuple(f), scale=wide["scale"] * (close["scale"] / wide["scale"]) ** t)

    lathe.stage(m.bar_profile(S, **vented), stripe_to=z_step)
    c.dissolve(cap)
    for t in steps(12):
        lathe.frame(m.bar_profile(S, **vented), cap, stripe_to=z_step, cam=zoom(t))
    for t in steps(16):
        ch = cad.PLUG_TOP_CHAMFER * max(0.0, 1.35 * t - 0.35)
        lathe.frame(m.bar_profile(S, **vented, chamf_z=z_cut, chamf=ch), cap, stripe_to=z_step, cam=close)
    c.linger(0.6)
    chamfered = dict(vented, chamf_z=z_cut, chamf=cad.PLUG_TOP_CHAMFER)
    for t in steps(12):
        lathe.frame(m.bar_profile(S, **chamfered), cap, stripe_to=z_step, cam=zoom(1 - t))

    cap = "Cut the plug off"
    r0 = RB - cad.PLUG_TOP_CHAMFER
    for t in steps(8):
        lathe.frame(m.bar_profile(S, **chamfered), cap, stripe_to=z_step,
                    tools=[(blade, m.TOOL, (gz, -(RB + 4 - (4 + cad.PLUG_TOP_CHAMFER) * t), 0))])
    for t in steps(26):
        r = max(r0 * (1 - t), 0.2)
        lathe.frame(m.bar_profile(S, **chamfered, groove_z=gz, groove_r=r), cap, stripe_to=z_step,
                    tools=[(blade, m.TOOL, (gz, -r, 0))])
    plug_lathe = m.cached("plug_lathe", lambda: m.lay_rev(PARTS["std_plug"]))  # nose still toward the tailstock
    stub = m.bar_profile(S, step_z=z_step, step_r=RB, bore_d=cad.VENT_D, bore=14.0, face=cad.PLUG_L + m.GROOVE_W)
    lathe.comes_free(stub, plug_lathe, cap, S, (8, 11), stripe_to=z_step)
    c.linger(0.6)

    finished_part(c, PARTS["std_plug"], PLUG_PART_CAM, "The finished plug")
    c.save()


# ---------------------------------------------------------------------------
# 3. Fill it, close it, pump the chamber down
# ---------------------------------------------------------------------------
def fill():
    c = Clip("fill")
    cup_solid, plug_solid = PARTS["std_cup"], PARTS["std_plug"]
    floor = m.CUP_L - cad.CUP_BORE_DEPTH
    z_top = m.CUP_L - cad.PLUG_L
    focal, view, scale = FILL_CAM
    cup_mesh = m.tessellate(cup_solid, cut=True)
    plug_mesh = m.tessellate(plug_solid, cut=True)
    colour = rr.POWDER["AlSi10Mg"]

    rng = np.random.default_rng(7)  # same grains as #232
    grains = rng.uniform(-1, 1, (30, 2)) * m.RB * 0.6
    ga = rng.uniform(0, 2 * math.pi, 14)
    gr = m.RB * np.sqrt(rng.uniform(0, 0.8, 14))
    surface_grains = list(zip(gr * np.cos(ga), gr * np.sin(ga), rng.uniform(0.35, 0.7, 14)))

    def scene(frac, plug_z=None):
        pl = c.pl
        pl.clear()
        m.show(pl, cup_mesh, AL, lw=1.2)
        if frac >= 0.01:
            top = floor + (z_top - floor) * frac
            col = cad.turned(cad.powder_profile(cad.CUP_BORE_D, floor, top, point=True))
            m.show(pl, m.tessellate(col, cut=True, tol=0.05), colour, lw=0.5, powder=True)
            for gx, gy, g in surface_grains:
                if gy >= 0.5:
                    pl.add_mesh(pv.Sphere(radius=g, center=(gx, gy, top + g * 0.4)), color=colour, **rr.BODY)
        if plug_z is not None:
            m.show(pl, plug_mesh, AL, lw=1.2, move=(0, 0, plug_z))
        c.camera(focal, view, scale)

    cap = "Fill with weighed powder"
    n = 2 if PREVIEW else 40
    for i in range(n):
        frac = i / (n - 1)
        scene(frac)
        if i < n - 1:  # grains still falling
            for k, (gx, gy) in enumerate(grains):
                z = z_top + 30 - ((i * 3.8 + k * 3.7) % 34)
                if gy < 0.6 or z < floor + (z_top - floor) * frac:
                    continue
                c.pl.add_mesh(pv.Sphere(radius=0.7, center=(gx, gy, z)), color=colour, **rr.BODY)
        c.grab(cap)
    c.linger(1.2)

    cap = "Close it with its own plug"
    for t in steps(36):
        scene(1.0, plug_z=z_top + 22 * (1 - t))
        c.grab(cap)
    c.linger(1.6)

    cap = "Vacuum pulls air out the hole"
    n = 2 if PREVIEW else 52
    for i in range(n):
        scene(1.0, plug_z=z_top)
        for k in range(3):
            z = m.CUP_L + 1 + ((i * 1.05 + k * 4.7) % 14)
            fade = max(0.0, 1 - (z - m.CUP_L - 1) / 14)
            c.pl.add_mesh(pv.Arrow(start=(0, 0, z), direction=(0, 0, 1), tip_length=0.42, tip_radius=0.32,
                                   shaft_radius=0.13, scale=7.0), color=m.AIR, opacity=0.25 + 0.65 * fade, **rr.BODY)
        c.grab(cap)
    c.linger(0.8)
    c.save()


CLIPS = {"cup": cup, "plug": plug, "fill": fill}

if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(CLIPS)
    for name in names:
        CLIPS[name]()
