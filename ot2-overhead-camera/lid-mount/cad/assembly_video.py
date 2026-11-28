#!/usr/bin/env python3
"""The assembly as a video to pause on: 1920 x 1080 MP4, every part named, one step at a time.

    xvfb-run -a -s "-screen 0 1920x1080x24" python assembly_video.py            # the MP4
    xvfb-run -a -s "-screen 0 1920x1080x24" python assembly_video.py --stills   # stills only

Writes ../renders/assembly_steps.mp4 and ../renders/assembly_steps_sheet.png, a contact sheet of
where each step ends. Each step first holds with its parts laid out beside their places and a
dashed line from each one to where it goes, then moves them in and holds again. Orange marks
the parts that step adds, and the labels give each one's count, size, material and source. The
side panel repeats the step from README §2 and lists the parts, and the MP4 has a chapter per
step. The shapes, fasteners and colours are the ones animate.py uses for the GIF.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import imageio_ffmpeg
import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw, ImageFont

import hardware
from animate import TAPE, ease, merged, mesh, tape_strips
from lid_mount import COLORS, Params, box, build, corners

HERE = Path(__file__).resolve().parent
RENDERS = HERE.parent / "renders"
CACHE = HERE / ".cache" / "assembly_video"
W, H = 1920, 1080
VW = 1290                       # the 3D view; the panel takes the rest
FPS = 30
CHAPTER_S = 11                  # YouTube ignores chapters shorter than 10 s
SS = 2                          # the label layer is drawn at 2x and scaled down, for smooth lines
HL = (1.0, 0.47, 0.0)           # orange: the parts the current step adds
HL2 = (1.0, 0.76, 0.12)         # amber: the second kind of part in a step, so the two stay distinct
ORANGE = (255, 120, 0)
INK, GREY, PANEL = (30, 30, 32), (105, 105, 110), (244, 244, 241)
FONTS = Path("/usr/share/fonts/truetype/dejavu")
UP = np.array([0.0, 0.0, 1.0])
X = np.array([1.0, 0.0, 0.0])


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")), size)


def wrap(text: str, f: ImageFont.FreeTypeFont, width: float) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            trial = f"{line} {word}".strip()
            if f.getlength(trial) <= width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


# --- what each part is: label, detail line ----------------------------------------------------

PARTS = {
    "base": ("Base with 4 posts", "printed, black PLA (plate 1)"),
    "deck": ("Deck", "printed (plate 2)"),
    "m4_nuts": ("M4 hex nut", "stainless, lab drawer; phase 2 only"),
    "m3_nuts": ("M3 hex nut", "stainless, lab drawer"),
    "cam_nuts": ("M2.5 hex nut", "black nylon, COMRUN kit"),
    "pi_nuts": ("M2.5 hex nut", "black nylon, COMRUN kit"),
    "pi_standoffs": ("M2.5 standoff, 6 mm + 6 mm stud", "male-female, black nylon, COMRUN kit"),
    "camera": ("Raspberry Pi HQ Camera", "ribbon connector toward the cable slot"),
    "cam_screws": ("M2.5 x 12 pan head", "black nylon, COMRUN kit"),
    "adapter": ("C-CS adapter ring", "just one"),
    "lens": ("8-50 mm zoom lens", "C-mount; zoom to about 25 mm"),
    "m3_screws": ("M3 x 10 pan head", "stainless, lab drawer"),
    "pi5": ("Raspberry Pi 5", "power/HDMI edge toward the cable slot"),
    "pi_screws": ("M2.5 x 6 pan head", "black nylon, COMRUN kit"),
    "tape": ("Painter's tape", "one strip over each tab"),
    "slot": ("Cable slot", "the camera's ribbon connector faces it"),
    "lid": ("OT-2 top window", "5 mm, removable"),
    "m4_screws": ("M4 x 18 pan head", "stainless, lab drawer; from inside"),
    "m4_washers": ("M4 nylon washer", "4.3 x 9 mm, under each head"),
}
SWATCH = {"camera": COLORS["camera_pcb"], "tape": TAPE, "lid": COLORS["lid"], "m3_nuts": hardware.STEEL}


def swatch(key: str) -> tuple[int, int, int]:
    rgb = SWATCH.get(key) or COLORS.get(key) or hardware.color(key)
    return tuple(int(255 * c) for c in rgb)


# --- the steps -----------------------------------------------------------------------------------

@dataclass
class Move:
    names: list[str]                 # actors, or "@group"
    vec: np.ndarray                  # where they start, relative to where they end up
    t0: float = 0.0                  # the part of the step they move in
    t1: float = 1.0
    spin: float = 0.0                # turns about the lens axis on the way
    guide: list[np.ndarray] | None = None   # points for the dashed lines, if not the actors' own


@dataclass
class Label:
    key: str                         # PARTS entry
    at: tuple[float, float]          # top-left of the box, as fractions of the 3D view
    targets: list[str] = field(default_factory=list)   # actors whose instances it points at
    points: list[tuple] | None = None                   # or these points, moving with targets[0]
    qty: int = 0
    text: str | None = None


@dataclass
class Step:
    short: str                       # chapter title and progress list entry
    title: str
    body: str
    cam: list
    adds: list[tuple[int, str, int]] = field(default_factory=list)   # qty, part, which highlight
    moves: list[Move] = field(default_factory=list)
    labels: list[Label] = field(default_factory=list)
    highlight: list[str] = field(default_factory=list)
    highlight2: list[str] = field(default_factory=list)
    xray: dict[str, float] = field(default_factory=dict)
    hide: list[str] = field(default_factory=list)
    show: list[str] = field(default_factory=list)
    frames: int = 60
    custom: Callable[[float], None] | None = None
    tool: str = ""
    number: int = 0


# --- the scene -------------------------------------------------------------------------------------

def scene_meshes(p: Params) -> tuple[dict[str, pv.PolyData], dict[str, np.ndarray]]:
    """Every part as a mesh in its assembled place, plus each fastener's instance centres."""
    src = [HERE / n for n in ("lid_mount.py", "hardware.py", "animate.py", "assembly_video.py")]
    steps = sorted(hardware.MCMASTER.glob("*.step"))
    key = hashlib.sha256(b"".join(f.read_bytes() for f in src + steps)).hexdigest()[:16]
    cdir = CACHE / key
    if (cdir / "centres.json").exists():
        centres = {k: np.array(v) for k, v in json.loads((cdir / "centres.json").read_text()).items()}
        return {f.stem: pv.read(f) for f in cdir.glob("*.vtp")}, centres
    parts = build(p)
    meshes = {name: mesh(parts[name]) for name in
              ("base", "deck", "pi_standoffs", "camera_pcb", "camera_mount", "adapter", "lens", "pi5")}
    meshes["lid_plain"] = mesh(box(260, 260, p.lid_thickness, z0=-p.lid_thickness))
    meshes["lid_cut"] = mesh(parts["lid"])
    meshes["tape"] = tape_strips(p)
    shapes, sources = hardware.placed(p)
    print("fasteners:", sources)
    nuts = shapes.pop("m3_nuts")
    shapes["m3_nuts_r"] = [s for s in nuts if s.val().Center().x > 0]
    shapes["m3_nuts_l"] = [s for s in nuts if s.val().Center().x < 0]
    centres = {}
    for k, v in shapes.items():
        meshes[k] = merged(v)
        centres[k] = np.array([tuple(s.val().Center()) for s in v])
    cdir.mkdir(parents=True, exist_ok=True)
    for k, m in meshes.items():
        m.save(cdir / f"{k}.vtp")
    (cdir / "centres.json").write_text(json.dumps({k: v.tolist() for k, v in centres.items()}))
    return meshes, centres


class Video:
    def __init__(self, p: Params, out: Path | None, stills: bool):
        self.p = p
        self.pl = pv.Plotter(off_screen=True, window_size=(VW, H))
        self.pl.set_background("white")
        self.pl.enable_anti_aliasing("ssaa")
        self.pl.enable_depth_peeling()
        self.actors, self.color, self.pos, self.rot = {}, {}, {}, {}
        self.alpha, self.base_alpha, self.groups, self.group_off = {}, {}, {}, {}
        self.anchors: dict[str, np.ndarray] = {}
        self.cam = None
        self.frame_no = 0
        self.chapters: list[tuple[int, str]] = []
        self.stills: list[tuple[str, Image.Image]] = []
        self.only_stills = stills
        self.ff = None
        if out is not None and not stills:
            self.tmp = out.with_suffix(".tmp.mp4")
            self.ff = subprocess.Popen(
                [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo",
                 "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                 "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-g", str(FPS),
                 "-movflags", "+faststart", str(self.tmp)], stdin=subprocess.PIPE)

    def add(self, name, poly, color, opacity=1.0, shown=True):
        self.actors[name] = self.pl.add_mesh(poly, color=color, opacity=opacity, smooth_shading=False,
                                             specular=0.2)
        self.color[name] = color
        self.pos[name] = np.zeros(3)
        self.rot[name] = 0.0
        self.base_alpha[name] = opacity
        self.alpha[name] = 1.0 if shown else 0.0

    def offset(self, name: str) -> np.ndarray:
        off = self.pos[name].copy()
        for g, members in self.groups.items():
            if name in members:
                off = off + self.group_off[g]
        return off

    def apply(self):
        for name, actor in self.actors.items():
            actor.SetPosition(*self.offset(name))
            actor.SetOrientation(0, 0, self.rot[name])
            a = self.alpha[name]
            actor.SetVisibility(a > 0.02)
            actor.GetProperty().SetOpacity(self.base_alpha[name] * a)

    def project(self, pts) -> list[tuple[float, float]]:
        ren = self.pl.renderer
        out = []
        for x, y, z in pts:
            ren.SetWorldPoint(float(x), float(y), float(z), 1.0)
            ren.WorldToDisplay()
            dx, dy, _ = ren.GetDisplayPoint()
            out.append((dx, H - dy))
        return out

    # -- drawing -----------------------------------------------------------------------------------

    def render3d(self) -> Image.Image:
        self.apply()
        self.pl.camera_position = self.cam
        self.pl.render()
        return Image.fromarray(self.pl.screenshot(return_img=True))

    def label_points(self, lab: Label) -> list[tuple]:
        if lab.points is not None:
            off = self.offset(lab.targets[0]) if lab.targets else np.zeros(3)
            return [np.array(pt) + off for pt in lab.points]
        pts = []
        for t in lab.targets:
            pts += [c + self.offset(t) for c in self.anchors[t]]
        return pts

    def overlay(self, labels: list[Label], guides: list[tuple]) -> Image.Image:
        lay = Image.new("RGBA", (VW * SS, H * SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        for a, b in guides:
            (ax, ay), (bx, by) = self.project([a, b])
            dashed(d, (ax * SS, ay * SS), (bx * SS, by * SS), ORANGE + (235,), 3 * SS, 14 * SS, 9 * SS)
            r = 5 * SS
            d.ellipse([bx * SS - r, by * SS - r, bx * SS + r, by * SS + r], outline=ORANGE + (255,), width=2 * SS)
        f1, f2 = font(25 * SS, True), font(20 * SS)
        for lab in labels:
            if lab.targets and self.alpha[lab.targets[0]] < 0.5:     # not on screen yet
                continue
            name, sub = PARTS[lab.key]
            head = lab.text or (f"{lab.qty} x {name}" if lab.qty else name)
            tw = max(f1.getlength(head), f2.getlength(sub)) + 28 * SS
            th = 72 * SS
            x0, y0 = lab.at[0] * VW * SS, lab.at[1] * H * SS
            x1, y1 = x0 + tw, y0 + th
            for pt in self.project(self.label_points(lab)):
                px, py = pt[0] * SS, pt[1] * SS
                sx, sy = min(max(px, x0), x1), min(max(py, y0), y1)
                d.line([(sx, sy), (px, py)], fill=INK + (255,), width=2 * SS)
                r = 4.5 * SS                                # small, so it doesn't hide a nut
                d.ellipse([px - r, py - r, px + r, py + r], fill=INK + (255,), outline=(255, 255, 255, 255),
                          width=2 * SS)
            d.rounded_rectangle([x0, y0, x1, y1], radius=10 * SS, fill=(255, 255, 255, 240),
                                outline=INK + (255,), width=2 * SS)
            d.text((x0 + 14 * SS, y0 + 9 * SS), head, font=f1, fill=INK + (255,))
            d.text((x0 + 14 * SS, y0 + 41 * SS), sub, font=f2, fill=GREY + (255,))
        return lay.resize((VW, H), Image.LANCZOS)

    def compose(self, view: Image.Image, panel: Image.Image, labels, guides) -> Image.Image:
        canvas = Image.new("RGB", (W, H), "white")
        if labels or guides:
            view = Image.alpha_composite(view.convert("RGBA"), self.overlay(labels, guides)).convert("RGB")
        canvas.paste(view, (0, 0))
        canvas.paste(panel, (VW, 0))
        return canvas

    def emit(self, img: Image.Image, n: int = 1):
        if self.ff is not None:
            data = img.tobytes()
            for _ in range(n):
                self.ff.stdin.write(data)
        self.frame_no += n

    def close(self, out: Path, title: str):
        self.pl.close()
        if self.ff is None:
            return
        self.ff.stdin.close()
        self.ff.wait()
        meta = out.with_suffix(".chapters.txt")
        lines = [";FFMETADATA1", f"title={title}"]
        bounds = [c[0] for c in self.chapters[1:]] + [self.frame_no]
        for (start, name), end in zip(self.chapters, bounds):
            lines += ["[CHAPTER]", f"TIMEBASE=1/{FPS}", f"START={start}", f"END={end}", f"title={name}"]
        meta.write_text("\n".join(lines) + "\n")
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", str(self.tmp),
                        "-i", str(meta), "-map", "0", "-map_metadata", "1", "-map_chapters", "1", "-c", "copy",
                        "-movflags", "+faststart", str(out)], check=True)
        self.tmp.unlink()
        meta.unlink()
        print(f"{out.name}: {self.frame_no} frames, {self.frame_no / FPS:.1f} s, {out.stat().st_size / 1e6:.1f} MB")
        for start, name in self.chapters:
            s = start // FPS
            print(f"  {s // 60}:{s % 60:02d} {name}")


def dashed(d: ImageDraw.ImageDraw, a, b, fill, width, dash, gap):
    a, b = np.array(a, float), np.array(b, float)
    length = np.linalg.norm(b - a)
    if length < 1:
        return
    u = (b - a) / length
    s = 0.0
    while s < length:
        e = min(s + dash, length)
        d.line([tuple(a + u * s), tuple(a + u * e)], fill=fill, width=width)
        s = e + gap


# --- the side panel ------------------------------------------------------------------------------

def panel(step: Step, steps: list[Step], parts_list: list[tuple[str, list[tuple[int, str]]]] | None = None):
    img = Image.new("RGB", (W - VW, H), PANEL)
    d = ImageDraw.Draw(img)
    d.line([(0, 0), (0, H)], fill=(205, 205, 200), width=2)
    x, width = 40, W - VW - 80
    y = 34
    d.text((x, y), "OT-2 lid camera mount: assembly", font=font(22), fill=GREY)
    y += 48
    if step.number:
        d.text((x, y), f"Step {step.number} of {sum(1 for s in steps if s.number)}", font=font(24, True),
               fill=ORANGE)
        y += 38
    for line in wrap(step.title, font(34, True), width):
        d.text((x, y), line, font=font(34, True), fill=INK)
        y += 44
    y += 8
    for line in wrap(step.body, font(23), width):
        d.text((x, y), line, font=font(23), fill=INK)
        y += 32
    if step.tool:
        y += 6
        d.text((x, y), f"Tool: {step.tool}", font=font(21, True), fill=GREY)
        y += 30
    if step.adds:
        y += 22
        d.text((x, y), "THIS STEP ADDS (coloured as in the view)", font=font(19, True), fill=GREY)
        y += 34
        y = part_rows(d, x, y, step.adds, width)
    if parts_list:
        for heading, rows in parts_list:
            y += 18
            d.text((x, y), heading.upper(), font=font(19, True), fill=GREY)
            y += 32
            y = part_rows(d, x, y, rows, width, compact=True)
    if step.number:
        y = H - 34 - 31 * sum(1 for s in steps if s.number)
        for s in steps:
            if not s.number:
                continue
            here = s.number == step.number
            done = s.number < step.number
            f = font(21, here)
            colour = INK if here else (GREY if done else (150, 150, 152))
            if here:
                d.rectangle([x - 14, y - 2, x - 8, y + 24], fill=ORANGE)
            d.text((x, y), f"{s.number:>2}", font=f, fill=colour)
            d.text((x + 40, y), s.short + ("  ✓" if done else ""), font=f, fill=colour)
            y += 31
    return img


def part_rows(d, x, y, rows, width, compact=False) -> int:
    fq, fn, fs = font(23 if compact else 25, True), font(23 if compact else 25), font(19 if compact else 20)
    for qty, key, *shade in rows:
        name, sub = PARTS[key]
        sz = 22 if compact else 26
        # A step's own parts get the colour they have in the view; the full list, their real one.
        fill = tuple(int(255 * c) for c in (HL, HL2)[shade[0] - 1]) if shade else swatch(key)
        d.rounded_rectangle([x, y + 3, x + sz, y + 3 + sz], radius=5, fill=fill, outline=(90, 90, 90),
                            width=1)
        tx = x + sz + 14
        q = f"{qty} x " if qty else ""
        d.text((tx, y), q, font=fq, fill=INK)
        d.text((tx + fq.getlength(q), y), name, font=fn, fill=INK)
        if compact:
            y += 31
        else:
            d.text((tx, y + 33), sub, font=fs, fill=GREY)
            y += 68
    return y


# --- the assembly ----------------------------------------------------------------------------------

def make_steps(p: Params, v: Video) -> list[Step]:
    raised = 80.0                           # the deck sub-assembly waits this far up until step 7
    zr = p.z_deck + raised
    y_slot = -(p.cam_board / 2 + 2 + p.slot_h / 2)
    steps = [
        Step("Parts", "Parts for one mount",
             "The two printed parts, then the camera, lens and Pi 5 and their screws, in order. "
             "Steel parts come from the Prototyping Lab drawer; black ones from the nylon M2.5 kit.",
             cam=[(330, -470, 300), (0, 0, 95), (0, 0, 1)],
             labels=[Label("base", (0.05, 0.62), ["base"], points=[(-30, -52, 6)]),
                     Label("deck", (0.05, 0.10), ["deck"], points=[(-45, -50, p.z_deck + p.deck_t)])]),
        Step("M4 nuts (phase 2)", "M4 nuts into the base",
             "Drop a nut into each hex trap on the base. These are only needed for phase 2, when the "
             "base is bolted through a drilled window; for tape (phase 1) they can wait.",
             cam=[(170, -270, 210), (0, 0, 4), (0, 0, 1)], adds=[(4, "m4_nuts", 1)],
             moves=[Move(["m4_nuts"], UP * 45)], highlight=["m4_nuts"],
             labels=[Label("m4_nuts", (0.05, 0.08), ["m4_nuts"], qty=4)]),
        Step("M3 nuts into the posts", "M3 nuts into the posts",
             "Slide a nut into the side slot near the top of each post, lying flat, and push until it "
             "stops: the hex end of the slot holds it on the screw axis. The base is see-through here "
             "so the nuts show.",
             cam=[(215, -265, 175), (0, 0, 92), (0, 0, 1)], adds=[(4, "m3_nuts", 1)],
             moves=[Move(["m3_nuts_r"], X * 28), Move(["m3_nuts_l"], -X * 28)],
             highlight=["m3_nuts_r", "m3_nuts_l"], xray={"base": 0.35},
             labels=[Label("m3_nuts", (0.04, 0.08), ["m3_nuts_r", "m3_nuts_l"], qty=4)]),
        Step("Camera nuts", "Camera nuts into the deck",
             "The deck is built up on the bench and goes on the posts in step 7. Drop a nylon nut "
             "into each of the four hex traps around the lens hole on the top of the deck.",
             cam=[(120, -200, zr + 175), (0, -5, zr + 2), (0, 0, 1)], adds=[(4, "cam_nuts", 1)],
             moves=[Move(["cam_nuts"], UP * 40)], highlight=["cam_nuts"],
             hide=["base", "m4_nuts", "m3_nuts_r", "m3_nuts_l"],
             labels=[Label("cam_nuts", (0.04, 0.08), ["cam_nuts"], qty=4),
                     Label("deck", (0.60, 0.80), ["deck"], points=[(40, -50, p.z_deck + p.deck_t)])]),
        Step("Pi 5 standoffs", "Standoffs for the Pi 5",
             "Push each standoff's stud down through the deck. From underneath, start a nylon nut on "
             "it inside the trap, then turn the standoff finger tight; the trap stops the nut turning. "
             "The deck is see-through here.",
             cam=[(185, -250, zr - 95), (5, 10, zr + 3), (0, 0, 1)], adds=[(4, "pi_standoffs", 1), (4, "pi_nuts", 2)],
             moves=[Move(["pi_nuts"], -UP * 32), Move(["pi_standoffs"], UP * 40, 0.3, 1.0)],
             highlight=["pi_standoffs"], highlight2=["pi_nuts"], xray={"deck": 0.4},
             labels=[Label("pi_standoffs", (0.04, 0.06), ["pi_standoffs"], qty=4),
                     Label("pi_nuts", (0.52, 0.80), ["pi_nuts"], qty=4)]),
        Step("HQ Camera", "Hang the camera under the deck",
             "Ribbon connector toward the cable slot. Drive the four M2.5 x 12 screws up from the lens "
             "side, through the camera's corner holes and the deck, into the nuts from step 3. "
             "Snug only: nylon strips.",
             cam=[(190, -260, zr - 95), (0, 0, zr - 8), (0, 0, 1)], tool="#1 Phillips",
             adds=[(1, "camera", 1), (4, "cam_screws", 2)],
             moves=[Move(["camera_pcb", "camera_mount"], -UP * 40),
                    Move(["cam_screws"], -UP * 55, 0.35, 1.0)],
             highlight=["camera_pcb", "camera_mount"], highlight2=["cam_screws"],
             labels=[Label("camera", (0.04, 0.80), ["camera_pcb"], points=[(-19, -10, p.z_pcb_back - 1.4)]),
                     Label("cam_screws", (0.56, 0.80), ["cam_screws"], qty=4),
                     Label("slot", (0.04, 0.06), ["deck"], points=[(0, y_slot, p.z_deck)])]),
        Step("Lens", "Lens and one adapter ring",
             "Screw on the lens with ONE C-CS adapter ring between it and the camera; a second ring "
             "stops it focusing. Set the zoom to about 25 mm.",
             cam=[(280, -360, zr - 120), (0, 0, zr - 70), (0, 0, 1)], adds=[(1, "adapter", 1), (1, "lens", 2)],
             moves=[Move(["adapter"], -UP * 45), Move(["lens"], -UP * 75, 0.3, 1.0, spin=1.5)],
             highlight=["adapter"], highlight2=["lens"],
             labels=[Label("adapter", (0.60, 0.36), ["adapter"], points=[(19.0, 0, 75.3)]),
                     Label("lens", (0.58, 0.62), ["lens"], points=[(20.0, 0, 40.0)])]),
        Step("Deck onto the posts", "Deck onto the posts",
             "Lower the deck: the post tops drop 2.5 mm into the sockets underneath it. Then drive the "
             "four M3 x 10 screws down through the deck into the nuts from step 2, snug.",
             cam=[(300, -400, 330), (0, 0, 115), (0, 0, 1)], tool="#1 Phillips", adds=[(4, "m3_screws", 1)],
             moves=[Move(["@deck_sub"], UP * raised, 0.0, 0.55,
                         guide=[np.array((x, y, p.z_post_top)) for x, y in corners(p.post_c)]),
                    Move(["m3_screws"], UP * 110, 0.55, 1.0)],
             highlight=["m3_screws"], show=["base", "m4_nuts", "m3_nuts_r", "m3_nuts_l"],
             labels=[Label("m3_screws", (0.04, 0.06), ["m3_screws"], qty=4),
                     Label("base", (0.04, 0.84), ["base"], points=[(-47, -47, 60)])]),
        Step("Pi 5", "Pi 5 onto the standoffs",
             "Power/HDMI edge toward the cable slot. Fix it with four M2.5 x 6 screws into the "
             "standoffs, snug. Then plug the camera cable into either CAM/DISP port.",
             cam=[(190, -300, 330), (10, 8, 112), (0, 0, 1)], tool="#1 Phillips",
             adds=[(1, "pi5", 1), (4, "pi_screws", 2)],
             moves=[Move(["pi5"], UP * 55), Move(["pi_screws"], UP * 75, 0.4, 1.0)],
             highlight=["pi5"], highlight2=["pi_screws"],
             labels=[Label("pi5", (0.64, 0.16), ["pi5"], points=[(45, 25, 112.3)]),
                     Label("pi_screws", (0.04, 0.07), ["pi_screws"], qty=4)]),
    ]

    def phase1(u):
        v.alpha["lid_plain"] = min(1.0, u * 2)
        v.pos["lid_plain"] = -UP * 60 * (1 - min(1.0, u * 1.4))
        v.alpha["tape"] = ease(max(0.0, (u - 0.6) / 0.4))

    def phase2(u):
        v.alpha["tape"] = 1 - min(1.0, u * 3)
        v.alpha["lid_plain"] = 1 - min(1.0, u * 3)
        v.alpha["lid_cut"] = min(1.0, u * 3)

    steps += [
        Step("Phase 1: tape", "Phase 1: tape it to the window",
             "Set it on the OT-2's top window over the plate, slide it until the live preview is "
             "centred and square, then tape the four tabs. No holes.",
             cam=[(330, -440, 260), (0, 0, 45), (0, 0, 1)], adds=[(4, "tape", 1)], highlight=["tape"],
             custom=phase1, frames=70,
             labels=[Label("tape", (0.04, 0.80), ["tape"], qty=4, text="Painter's tape over each tab",
                           points=[(80, 0, 0.5), (0, -80, 0.5)]),
                     Label("lid", (0.62, 0.84), ["lid_plain"], points=[(110, -110, 0)])]),
        Step("Phase 2: bolts", "Phase 2 (optional): bolt it down",
             "Only once the window has its 2 in hole and four 5 mm holes. From inside the robot, an "
             "M4 x 18 and a nylon washer up into each M4 nut. The heads hang 3.9 mm below the window; "
             "the pipette head clears it by 9.1 mm.",
             cam=[(230, -300, -170), (0, 0, 15), (0, 0, 1)], tool="#2 Phillips",
             adds=[(4, "m4_screws", 1), (4, "m4_washers", 2)],
             moves=[Move(["m4_screws", "m4_washers"], -UP * 45, 0.35, 1.0)],
             highlight=["m4_screws"], highlight2=["m4_washers"], custom=phase2, frames=70,
             labels=[Label("m4_screws", (0.04, 0.06), ["m4_screws"], qty=4),
                     Label("m4_washers", (0.56, 0.84), ["m4_washers"], qty=4)]),
        Step("Assembled", "Assembled",
             "Every part in place, in its real colours. Pause here for the full list.",
             cam=[(330, -470, 300), (0, 0, 70), (0, 0, 1)], frames=40,
             labels=[Label("pi5", (0.60, 0.05), ["pi5"], points=[(45, 25, 112.3)]),
                     Label("m3_screws", (0.04, 0.05), ["m3_screws"], qty=4),
                     Label("deck", (0.04, 0.24), ["deck"], points=[(-25, -56, p.z_deck + 2.5)]),
                     Label("lens", (0.66, 0.50), ["lens"], points=[(14.1, -14.1, 45.0)]),
                     Label("base", (0.04, 0.62), ["base"], points=[(-47, -47, 50)]),
                     Label("m4_screws", (0.50, 0.86), ["m4_screws"], qty=4)]),
    ]
    for i, s in enumerate(steps[1:-1], 1):
        s.number = i
    return steps


def run(stills: bool) -> None:
    p = Params()
    out = RENDERS / "assembly_steps.mp4"
    v = Video(p, out, stills)
    meshes, centres = scene_meshes(p)
    v.add("lid_plain", meshes["lid_plain"], COLORS["lid"], opacity=0.35, shown=False)
    v.add("lid_cut", meshes["lid_cut"], COLORS["lid"], opacity=0.35, shown=False)
    for name in ("base", "deck", "pi_standoffs", "camera_pcb", "camera_mount", "adapter", "lens", "pi5"):
        v.add(name, meshes[name], COLORS[name])
    for name in centres:
        v.add(name, meshes[name], hardware.color(name.removesuffix("_r").removesuffix("_l")))
    v.add("tape", meshes["tape"], TAPE, shown=False)
    v.anchors = dict(centres)
    v.anchors["pi_standoffs"] = np.array([(x, y, p.z_deck + p.deck_t + p.pi_standoff_h / 2) for x, y in p.pi_holes()])
    # One point per larger part, for its dashed line: on the lens axis, or the middle of the Pi 5.
    v.anchors["camera_mount"] = np.array([(0, 0, p.z_cs_seat)])
    v.anchors["adapter"] = np.array([(0, 0, p.z_lens_flange + p.c_cs_adapter / 2)])
    v.anchors["lens"] = np.array([(0, 0, p.z_lens_front)])
    x0, x1, y0, y1 = p.pi_board_box()
    v.anchors["pi5"] = np.array([((x0 + x1) / 2, (y0 + y1) / 2, p.z_deck + p.deck_t + p.pi_standoff_h + 1.6)])
    v.groups["deck_sub"] = {"deck", "cam_nuts", "pi_nuts", "pi_standoffs", "camera_pcb", "camera_mount",
                            "cam_screws", "adapter", "lens"}
    v.group_off["deck_sub"] = UP * 80.0
    for n in ("m4_nuts", "m3_nuts_r", "m3_nuts_l", "cam_nuts", "cam_screws", "camera_pcb", "camera_mount",
              "adapter", "lens", "m3_screws", "pi_standoffs", "pi5", "pi_screws", "pi_nuts", "m4_screws",
              "m4_washers"):
        v.alpha[n] = 0.0

    steps = make_steps(p, v)
    full = [("Printed", [(1, "base"), (1, "deck")]),
            ("Bought (ME order 12704)", [(1, "camera"), (1, "adapter"), (1, "lens"), (1, "pi5")]),
            ("Black nylon, COMRUN M2.5 kit", [(4, "cam_screws"), (4, "pi_screws"), (8, "cam_nuts"),
                                              (4, "pi_standoffs")]),
            ("Stainless, Prototyping Lab drawer", [(4, "m3_screws"), (4, "m3_nuts")]),
            ("Phase 2 only", [(4, "m4_screws"), (4, "m4_nuts"), (4, "m4_washers")])]
    v.cam = steps[0].cam
    lit: list[str] = []
    for k, st in enumerate(steps):
        start = v.frame_no
        v.chapters.append((start, f"{st.number}. {st.short}" if st.number else st.short))
        pan = panel(st, steps, full if not st.number else None)
        for n in lit:                                    # last step's orange goes back to its colour
            v.actors[n].GetProperty().SetColor(*v.color[n])
        for n, a in st.xray.items():
            v.base_alpha[n] = a
        for n in st.highlight:
            v.actors[n].GetProperty().SetColor(*HL)
        for n in st.highlight2:
            v.actors[n].GetProperty().SetColor(*HL2)
        lit = st.highlight + st.highlight2
        movers = [n for m in st.moves for n in m.names if not n.startswith("@")]
        for m in st.moves:
            for n in m.names:
                if n.startswith("@"):
                    v.group_off[n[1:]] = v.group_off[n[1:]] * 0 + m.vec
                else:
                    v.pos[n] = m.vec.copy()
                    v.rot[n] = 360.0 * m.spin
        fade_in = [n for n in movers if v.alpha[n] < 1.0] + [n for n in st.show if v.alpha[n] < 1.0]
        fade_out = [n for n in st.hide if v.alpha[n] > 0.0]

        # 1. Camera to this step's view, while its parts appear beside their places.
        cam_from = [np.array(c, float) for c in v.cam]
        cam_to = [np.array(c, float) for c in st.cam]
        n_cam = 0 if k == 0 or all(np.allclose(a, b) for a, b in zip(cam_from, cam_to)) else 30
        for i in range(1, n_cam + 1):
            u = ease(i / n_cam)
            v.cam = [tuple(a + (b - a) * u) for a, b in zip(cam_from, cam_to)]
            for n in fade_in:
                v.alpha[n] = u
            for n in fade_out:
                v.alpha[n] = 1 - u
            if not stills:
                v.emit(v.compose(v.render3d(), pan, [], []))
        v.cam = [tuple(c) for c in cam_to]
        for n in fade_in:
            v.alpha[n] = 1.0
        for n in fade_out:
            v.alpha[n] = 0.0

        def guides():
            out = []
            for m in st.moves:
                for n in m.names:
                    if n.startswith("@"):
                        off_now = v.group_off[n[1:]]
                        out += [(g + off_now, g) for g in (m.guide or [])]
                    else:
                        for c in v.anchors.get(n, []):
                            out.append((c + v.offset(n), c + v.offset(n) - v.pos[n]))
            return [(a, b) for a, b in out if np.linalg.norm(a - b) > 1.0]

        # 2. Hold: the parts beside their places, with a dashed line to where each one goes.
        if st.moves:
            img = v.compose(v.render3d(), pan, st.labels, guides())
            v.stills.append((f"{st.number:02d}a", img))
            v.emit(img, 75)

        # 3. Move them in.
        if not stills:
            for i in range(1, st.frames + 1):
                u = ease(i / st.frames)
                for m in st.moves:
                    loc = ease(min(max((i / st.frames - m.t0) / (m.t1 - m.t0), 0.0), 1.0))
                    for n in m.names:
                        if n.startswith("@"):
                            v.group_off[n[1:]] = m.vec * (1 - loc)
                        else:
                            v.pos[n] = m.vec * (1 - loc)
                            v.rot[n] = 360.0 * m.spin * (1 - loc)
                if st.custom:
                    st.custom(u)
                v.emit(v.compose(v.render3d(), pan, st.labels, guides()))
        for m in st.moves:
            for n in m.names:
                if n.startswith("@"):
                    v.group_off[n[1:]] = m.vec * 0
                else:
                    v.pos[n] = np.zeros(3)
                    v.rot[n] = 0.0
        if st.custom:
            st.custom(1.0)

        # 4. Hold, in place.
        img = v.compose(v.render3d(), pan, st.labels, [])
        v.stills.append((f"{st.number:02d}b" if st.number else st.short, img))
        last = k == len(steps) - 1
        v.emit(img, max(150, (CHAPTER_S + 3 * last) * FPS - (v.frame_no - start)))
        for n, a in st.xray.items():                      # see-through only for its own step
            v.base_alpha[n] = 1.0 if n not in ("lid_plain", "lid_cut") else 0.35

    v.close(out, "OT-2 lid camera mount: assembly")
    sheet(v.stills, RENDERS / "assembly_steps_sheet.png", stills)


def sheet(stills: list[tuple[str, Image.Image]], path: Path, keep_all: bool) -> None:
    """Where each step ends, 4 across; with --stills, every still goes to /tmp as well."""
    if keep_all:
        d = Path("/tmp/assembly_video_stills")
        d.mkdir(exist_ok=True)
        for name, img in stills:
            img.save(d / f"{name.replace(' ', '_')}.png")
        print("stills in", d)
    ends = [img for name, img in stills if not name.endswith("a")]
    tw, th = 480, 270
    cols = 4
    rows = (len(ends) + cols - 1) // cols
    out = Image.new("RGB", (tw * cols, th * rows), "white")
    for i, img in enumerate(ends):
        out.paste(img.resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
    out.save(path, optimize=True)
    print(f"{path.name}: {len(ends)} stills")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stills", action="store_true", help="render only the held frames, to /tmp")
    run(ap.parse_args().stills)
