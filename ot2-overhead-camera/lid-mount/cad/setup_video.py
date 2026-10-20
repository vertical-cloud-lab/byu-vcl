#!/usr/bin/env python3
"""Centring, zooming and focusing the lid camera, as a video to pause on and as a GIF.

    python setup_video.py            # the MP4, the GIF, the contact sheet and the chapter list
    python setup_video.py --stills   # only the frame each step ends on, to /tmp/setup_video_stills

Writes ../renders/setup_steps.mp4 (1920 x 1080, a chapter per step), ../renders/setup_steps.gif
(960 px wide, small enough to show in a GitHub comment), ../renders/setup_steps_sheet.png (where
each step ends) and ../exports/setup_steps_chapters.txt (the chapters, for a YouTube description).

Left, the OT-2 deck from above, under the top window: the slots and today's labware, the mount's
footprint, and the camera's field (the rest of the deck is shaded). Right, what the stream shows,
through coverage.py's pinhole camera, with a centre cross, the stream's timestamp and a focus
score. Orange marks what the step changes. The steps: zoom to the wide stop, focus, slide the
mount until the lens axis is over the deck centre (the middle of the rail between slots 5 and 8),
square it, then lock it and take a still. The deck is drawn flat: labware heights are ignored.

Where the camera starts comes from ../exports/lid_camera_setup.json, if it exists:

    focal_mm         effective focal length now, in coverage.py's model: the field at the plate
                     top is SENSOR x (pinhole height - 14.35 mm) / focal_mm
    axis_offset_mm   [x, y] of the lens axis from the deck centre, deck mm, x to the right and
                     y toward the back
    rotation_deg     how far the picture is turned, + clockwise on screen (rails run down to the right)
    target_focal_mm  where the zoom ends up: 8.0, the wide stop
    still_path, still_to_deck   optional: a full still (relative to the lid-mount folder), and the
                     2 x 3 affine from deck mm to its pixels. With both, the still is drawn wherever
                     it reaches and the rest of the deck is drawn; without, it is all drawn.

Without the file, the start is a rough reading of the stream frame of 2026-10-20 02:28 UTC
(../camera/frames/2026-10-20/stream_frame_0228Z.jpg, about 3.3 px/mm in its 1440 x 1080): 8.8 mm,
15 mm behind and 4.5 mm left of the deck centre, turned 1.5 deg.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import tempfile
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from coverage import INK2 as INK2_HEX, POSITIONS, SLOT_SIZE, WINDOW_TOP, slot_rect, view, wells
from lid_mount import EXPORTS, Params
from ot2_context import PLATE, PUPIL_IN_LENS, SENSOR, SLOTS
from placement import SCREWS, WINDOW, WINDOW_CENTRE_DECK

HERE = Path(__file__).resolve().parent
LID = HERE.parent
RENDERS = LID / "renders"
SETUP = EXPORTS / "lid_camera_setup.json"
FALLBACK = {"focal_mm": 8.8, "axis_offset_mm": [-4.5, 15.0], "rotation_deg": 1.5, "target_focal_mm": 8.0}

W, H, FPS = 1920, 1080, 30
VW = 1360                       # the two views; the step panel takes the rest
GIF_W, GIF_H, GIF_FPS = 960, 600, 10
GIF_MB = 8.0
CHAPTER_S = 11                  # YouTube ignores chapters shorter than 10 s
HOLD_S = 8                      # each step's end stays up this long, to read the panel
ORANGE, BLUE, GREEN, RED = (255, 120, 0), (28, 92, 171), (30, 140, 70), (210, 30, 30)
INK, GREY, PANEL, PALE = (30, 30, 32), (105, 105, 110), (244, 244, 241), (150, 150, 152)
INK2 = tuple(int(INK2_HEX[i:i + 2], 16) for i in (1, 3, 5))
FONTS = Path("/usr/share/fonts/truetype/dejavu")

P = Params()
Z_PIN = WINDOW_TOP + P.z_lens_front + PUPIL_IN_LENS       # pinhole above the deck, mm
CENTRE = POSITIONS["deck centre"][1]                      # middle of the rail between slots 5 and 8
TAB_TIP = P.base_size / 2 + P.tab_len                     # lens axis to a tape tab's tip, mm
DEFOCUS = 4.0                                             # blur after zooming, px in a 700 px wide view
FOCUS_PEAK = 41                                           # the stream's focus number when sharp, for show

# The deck as a picture, TEX_S px per mm; y runs toward the back, so up in the picture.
TEX_S = 3.0
TEX_X0, TEX_X1, TEX_Y0, TEX_Y1 = -240.0, 640.0, -190.0, 560.0
TOP_X0, TOP_X1, TOP_Y0 = -62.0, 456.0, -46.0                   # what the top view shows
TOP_Y1 = TOP_Y0 + (TOP_X1 - TOP_X0) * 512 / 600


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


def ease(u: float) -> float:
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


# --- the camera ------------------------------------------------------------------------------------

@dataclass
class Cam:
    ax: float                        # lens axis, deck mm
    ay: float
    f: float                         # effective focal length, mm
    phi: float                       # picture turned this far clockwise on screen, deg
    defocus: float = 0.0             # blur, px in a 700 px wide view
    flash: float = 0.0               # 0-1, the still's flash
    still: float = 0.0               # 0-1, the "still saved" badge
    checks: float = 0.0              # 0-1, ticks on the slots in view
    trace: list = field(default_factory=list)   # (focus ring, score) so far

    def axes(self) -> tuple[np.ndarray, np.ndarray]:
        """The picture's right and down directions, in deck coordinates."""
        c, s = math.cos(math.radians(self.phi)), math.sin(math.radians(self.phi))
        return np.array([c, s]), np.array([s, -c])

    def field(self, z: float = 0.0) -> tuple[float, float]:
        return SENSOR[0] * (Z_PIN - z) / self.f, SENSOR[1] * (Z_PIN - z) / self.f

    def corners(self, z: float = 0.0) -> np.ndarray:
        """The field's corners on the plane z, deck mm, clockwise from the picture's top left."""
        w, h = self.field(z)
        u, v = self.axes()
        c = np.array([self.ax, self.ay])
        return np.array([c + a * w / 2 * u + b * h / 2 * v for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))])

    def to_picture(self, pts, ow: int, oh: int) -> np.ndarray:
        """Deck mm (on the deck) to pixels of an ow x oh picture."""
        w, h = self.field()
        u, v = self.axes()
        d = np.atleast_2d(pts) - [self.ax, self.ay]
        return np.stack([d @ u / w * ow + ow / 2, d @ v / h * oh + oh / 2], axis=1)

    def score(self) -> float:
        return 1.0 / (1.0 + (self.defocus / 1.2) ** 2)

    def in_view(self) -> dict[int, float]:
        """The fraction of each slot's outline area that the picture shows."""
        out = {}
        for n in range(1, 13):
            x0, y0, x1, y1 = slot_rect(n)
            g = np.stack(np.meshgrid(np.linspace(x0, x1, 25), np.linspace(y0, y1, 17)), -1).reshape(-1, 2)
            q = self.to_picture(g, 1000, 750)
            out[n] = float(np.mean((q[:, 0] >= 0) & (q[:, 0] <= 1000) & (q[:, 1] >= 0) & (q[:, 1] <= 750)))
        return out


# --- the deck, drawn -------------------------------------------------------------------------------

def tex_xy(x, y, s=TEX_S) -> tuple[int, int]:
    return int(round((x - TEX_X0) * s * 16)), int(round((TEX_Y1 - y) * s * 16))


def deck_colour(start: dict) -> tuple[int, int, int]:
    """The empty deck's colour: from the still around slot 5's middle when there is one."""
    path = LID / start["still_path"] if start.get("still_path") else None
    if path is None or not path.exists() or not start.get("still_to_deck"):
        return (198, 200, 203)
    still = cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB)
    m = np.array(start["still_to_deck"], float)
    u, v = m @ [SLOTS[5][0] + 30, SLOTS[5][1] - 25, 1.0]
    patch = still[int(v) - 40:int(v) + 40, int(u) - 40:int(u) + 40].reshape(-1, 3)
    return tuple(int(c) for c in np.median(patch, axis=0))


def deck_texture(start: dict) -> np.ndarray:
    """Today's deck from straight above, TEX_S px/mm: slots, rails, engraved numbers, labware."""
    s = TEX_S
    deck = deck_colour(start)
    plate = tuple(max(0, c - 6) for c in deck)
    digit = tuple(min(255, c + 6) for c in deck)
    digit_edge = tuple(max(0, c - 34) for c in deck)
    tw, th = int((TEX_X1 - TEX_X0) * s), int((TEX_Y1 - TEX_Y0) * s)
    img = np.full((th, tw, 3), (78, 80, 84), np.uint8)
    aa, sh = cv2.LINE_AA, 4

    def box(x0, y0, x1, y1, fill, edge=None, t=0.8):
        cv2.rectangle(img, tex_xy(x0, y1), tex_xy(x1, y0), fill, -1, aa, sh)
        if edge is not None:
            cv2.rectangle(img, tex_xy(x0, y1), tex_xy(x1, y0), edge, max(1, round(t * s)), aa, sh)

    def disc(x, y, r, fill, edge=None, t=0.6):
        cv2.circle(img, tex_xy(x, y), round(r * s * 16), fill, -1, aa, sh)
        if edge is not None:
            cv2.circle(img, tex_xy(x, y), round(r * s * 16), edge, max(1, round(t * s)), aa, sh)

    box(-14, -16, 407, 373, plate)                                  # the deck plate
    rng = np.random.default_rng(7)
    x0p, y0p = (np.array(tex_xy(-14, 373)) // 16)
    x1p, y1p = (np.array(tex_xy(407, -16)) // 16)
    noise = rng.normal(0, 2.2, (y1p - y0p, x1p - x0p, 1))
    img[y0p:y1p, x0p:x1p] = np.clip(img[y0p:y1p, x0p:x1p] + noise, 0, 255).astype(np.uint8)

    for n in range(1, 13):
        x0, y0, x1, y1 = slot_rect(n)
        box(x0, y0, x1, y1, deck, tuple(max(0, c - 30) for c in deck), 0.4)
        box(x0 + 3, y0 - 3.6, x1 - 3, y0 - 0.9, (226, 227, 229), (120, 122, 126), 0.35)   # front rail
        box(x1 + 0.9, y0 + 3, x1 + 3.6, y1 - 3, (226, 227, 229), (120, 122, 126), 0.35)   # right rail
        box(x1 - 14, y0 - 4.4, x1 - 9, y0 - 0.2, (95, 96, 100))                         # clips
        box(x1 + 0.2, y0 + 9, x1 + 4.4, y0 + 14, (95, 96, 100))

    pil = Image.fromarray(img)
    d = ImageDraw.Draw(pil)
    f = font(int(40 * s), True)
    for n in range(1, 12):
        cx, cy = SLOTS[n]
        d.text(((cx - TEX_X0) * s, (TEX_Y1 - cy) * s), str(n), font=f, anchor="mm", fill=digit,
               stroke_width=2, stroke_fill=digit_edge)
    img = np.array(pil)

    # Slot 7: the 96-well plate, a few wells with paint in them.
    cx, cy = SLOTS[7]
    box(cx - PLATE[0] / 2, cy - PLATE[1] / 2, cx + PLATE[0] / 2, cy + PLATE[1] / 2, (168, 172, 178),
        (55, 56, 62), 1.2)
    paint = {(1, 6): (236, 196, 30), (4, 6): (212, 32, 42), (7, 6): (34, 42, 140), (0, 7): (236, 196, 30),
             (2, 7): (212, 32, 42), (5, 7): (24, 24, 26), (8, 7): (34, 42, 140), (10, 7): (242, 242, 240)}
    for k, (x, y) in enumerate(wells(7)):
        i, j = divmod(k, 8)
        disc(x, y, 3.43, paint.get((i, j), (150, 155, 162)), (92, 96, 104), 0.5)
    # Slot 6: tips in a rack.
    cx, cy = SLOTS[6]
    box(cx - PLATE[0] / 2, cy - PLATE[1] / 2, cx + PLATE[0] / 2, cy + PLATE[1] / 2, (48, 49, 54),
        (30, 30, 34), 1.0)
    for x, y in wells(6):
        disc(x, y, 3.0, (26, 26, 29), (128, 130, 136), 0.7)
    # Slot 10: the colour sensor's dock.
    x0, y0, x1, y1 = slot_rect(10)
    box(x0 + 2, y0 + 4, x1 - 18, y1 - 2, (236, 236, 233), (150, 150, 150), 0.8)
    box(x0 + 30, y0 + 22, x1 - 40, y1 - 14, (246, 246, 244), (170, 170, 170), 0.6)
    disc(x1 - 52, y0 + 30, 3.0, (120, 150, 230))
    # Slot 12: the trash.
    x0, y0, x1, y1 = slot_rect(12)
    box(x0 - 2, y0 - 2, x1 + 14, y1 + 20, (214, 214, 212), (150, 150, 150), 1.0)
    box(x0 + 8, y0 + 8, x1 + 6, y1 + 12, (26, 26, 30), (60, 60, 64), 1.0)
    box(x0 + 30, y1 + 4, x1 - 10, y1 + 10, (170, 40, 40))
    # Slot 3: three bottles of paint, toward the back of the slot.
    x0, y0, x1, y1 = slot_rect(3)
    for k, colour in enumerate([(40, 60, 175), (238, 214, 60), (220, 64, 78)]):
        disc(x0 + 26 + 38 * k, y0 + 46, 14.5, colour, (70, 70, 74), 0.8)
        disc(x0 + 22 + 38 * k, y0 + 50, 4.0, tuple(min(255, c + 60) for c in colour))
    # Slot 1: a reservoir, dark frame and white well.
    cx, cy = SLOTS[1]
    box(cx - PLATE[0] / 2, cy - PLATE[1] / 2, cx + PLATE[0] / 2, cy + PLATE[1] / 2, (58, 58, 64), (30, 30, 34), 1.0)
    box(cx - PLATE[0] / 2 + 8, cy - PLATE[1] / 2 + 8, cx + PLATE[0] / 2 - 10, cy + PLATE[1] / 2 - 12,
        (232, 232, 230), (150, 150, 150), 0.6)

    if start.get("still_path") and start.get("still_to_deck"):
        path = LID / start["still_path"]
        if path.exists():
            img = with_still(img, path, np.array(start["still_to_deck"], float))
    return img


def with_still(img: np.ndarray, path: Path, deck_to_still: np.ndarray) -> np.ndarray:
    """Lay a real still over the drawn deck, wherever it reaches, with a soft edge."""
    still = cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB)
    s = TEX_S
    tex_to_deck = np.array([[1 / s, 0, TEX_X0], [0, -1 / s, TEX_Y1], [0, 0, 1]])
    m = deck_to_still @ tex_to_deck
    th, tw = img.shape[:2]
    warped = cv2.warpAffine(still, m, (tw, th), flags=cv2.INTER_AREA | cv2.WARP_INVERSE_MAP)
    mask = cv2.warpAffine(np.full(still.shape[:2], 255, np.uint8), m, (tw, th),
                          flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
    mask = cv2.GaussianBlur(cv2.erode(mask, np.ones((9, 9), np.uint8)), (0, 0), 6)[..., None] / 255.0
    return (img * (1 - mask) + warped * mask).astype(np.uint8)


class Deck:
    """The deck texture at a few scales, and the camera's view of it."""

    def __init__(self, tex: np.ndarray):
        self.levels = {TEX_S: tex}
        s, t = TEX_S, tex
        for _ in range(3):
            s, t = s / 2, cv2.resize(t, (t.shape[1] // 2, t.shape[0] // 2), interpolation=cv2.INTER_AREA)
            self.levels[s] = t

    def level(self, px_per_mm: float) -> tuple[float, np.ndarray]:
        ok = [s for s in self.levels if s >= px_per_mm]
        s = min(ok) if ok else max(self.levels)
        return s, self.levels[s]

    def camera(self, cam: Cam, ow: int, oh: int) -> np.ndarray:
        """What the stream shows, ow x oh, before its overlays."""
        w, h = cam.field()
        s, tex = self.level(ow / w)
        u, v = cam.axes()
        kx, ky = w / ow, h / oh
        bx, by = (0.5 - ow / 2) * kx, (0.5 - oh / 2) * ky
        m = np.array([[s * u[0] * kx, s * v[0] * ky, s * (cam.ax + u[0] * bx + v[0] * by - TEX_X0)],
                      [-s * u[1] * kx, -s * v[1] * ky, s * (TEX_Y1 - cam.ay - u[1] * bx - v[1] * by)]])
        out = cv2.warpAffine(tex, m, (ow, oh), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(78, 80, 84))
        sigma = cam.defocus * ow / 700
        if sigma > 0.05:
            out = cv2.GaussianBlur(out, (0, 0), sigma)
        if cam.flash > 0:
            out = (out * (1 - cam.flash) + 255 * cam.flash).astype(np.uint8)
        return out

    def top(self, tw: int, th: int) -> np.ndarray:
        """The deck straight from above, with the window and the frame around it."""
        s, tex = self.level(tw / (TOP_X1 - TOP_X0))
        k = (TOP_X1 - TOP_X0) / tw
        m = np.array([[s * k, 0, s * (TOP_X0 - TEX_X0)], [0, s * k, s * (TEX_Y1 - TOP_Y1)]])
        img = cv2.warpAffine(tex, m, (tw, th), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
        return img


# --- one frame -----------------------------------------------------------------------------------------

@dataclass
class Layout:
    w: int
    h: int
    top: tuple[int, int, int, int]          # x, y, width, height of the top view
    cam: tuple[int, int, int, int]          # x, y, width, height of the stream view
    s: float                                # text scale
    gif: bool = False


MP4 = Layout(W, H, (28, 128, 600, 512), (660, 128, 680, 510), 1.0)
GIF = Layout(GIF_W, GIF_H, (10, 70, 400, 342), (424, 70, 526, 394), 0.62, gif=True)


def to_top(lay: Layout, x, y) -> tuple[float, float]:
    tx, ty, tw, th = lay.top
    k = tw / (TOP_X1 - TOP_X0)
    return tx + (x - TOP_X0) * k, ty + (TOP_Y1 - y) * k


def shade_polys(img: np.ndarray, polys: list[np.ndarray], colour, alpha: float, edge=None, t=2):
    over = img.copy()
    for poly in polys:
        cv2.fillPoly(over, [np.round(poly * 16).astype(np.int32)], colour, cv2.LINE_AA, 4)
    cv2.addWeighted(over, alpha, img, 1 - alpha, 0, img)
    if edge is not None:
        for poly in polys:
            cv2.polylines(img, [np.round(poly * 16).astype(np.int32)], True, edge, t, cv2.LINE_AA, 4)


def mount_outline(cam: Cam) -> np.ndarray:
    """The base's footprint (rounded square plus four tabs), turned with the camera, deck mm."""
    half, r, tw = P.base_size / 2, P.corner_r, P.tab_w / 2
    pts = []
    for q in range(4):                       # one side per quarter turn, starting at the front
        ang = math.radians(90 * q)
        side = [(-half + r, -half), (-tw, -half), (-tw + 2, -TAB_TIP), (tw - 2, -TAB_TIP), (tw, -half),
                (half - r, -half)]
        side += [(half - r + r * math.sin(a), -half + r - r * math.cos(a)) for a in np.linspace(0, math.pi / 2, 6)]
        for x, y in side:
            pts.append((x * math.cos(ang) - y * math.sin(ang), x * math.sin(ang) + y * math.cos(ang)))
    pts = np.array(pts)
    u, v = cam.axes()                         # turn with the picture: right = u, front = v
    return np.array([cam.ax, cam.ay]) + pts[:, :1] * u + (-pts[:, 1:]) * v


def arrow(img, a, b, colour, t):
    cv2.arrowedLine(img, tuple(np.round(np.array(a) * 16).astype(int)), tuple(np.round(np.array(b) * 16).astype(int)),
                    colour, t, cv2.LINE_AA, 4, 0.28)


def dashed_line(img, a, b, colour, t, dash=12, gap=8):
    a, b = np.array(a, float), np.array(b, float)
    n = np.linalg.norm(b - a)
    if n < 1:
        return
    u = (b - a) / n
    s = 0.0
    while s < n:
        e = min(s + dash, n)
        cv2.line(img, tuple(np.round((a + u * s) * 16).astype(int)), tuple(np.round((a + u * e) * 16).astype(int)),
                 colour, t, cv2.LINE_AA, 4)
        s = e + gap


@dataclass
class Step:
    short: str                       # chapter title and progress list entry
    title: str
    body: str
    gif: str                         # the GIF's line under the views
    watch: str = ""
    extra: list[tuple[str, list[str]]] = field(default_factory=list)
    motion: float = 3.0              # seconds of movement in the MP4; the GIF moves faster
    state: Callable[[float], Cam] | None = None
    changing: str = ""               # "field", "mount", "focus", "still": what to colour orange
    number: int = 0


class Frames:
    """Draws frames for one layout; the static parts are kept between frames."""

    def __init__(self, lay: Layout, deck: Deck, steps: list[Step], start: Cam):
        self.lay, self.deck, self.steps, self.start = lay, deck, steps, start
        tx, ty, tw, th = lay.top
        self.top_base = deck.top(tw, th)
        # Shade what lies outside the window: the OT-2's frame, under the lid's edge.
        wx, wy = WINDOW_CENTRE_DECK
        win = np.array([to_top(lay, wx + sx * WINDOW[0] / 2, wy + sy * WINDOW[1] / 2)
                        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]) - (tx, ty)
        mask = np.zeros(self.top_base.shape[:2], np.uint8)
        cv2.fillPoly(mask, [np.round(win * 16).astype(np.int32)], 255, cv2.LINE_AA, 4)
        dark = (self.top_base * 0.55 + np.array([20, 22, 26])).astype(np.uint8)
        m = mask[..., None] / 255.0
        self.top_base = (self.top_base * m + dark * (1 - m)).astype(np.uint8)
        cv2.polylines(self.top_base, [np.round(win * 16).astype(np.int32)], True, (120, 170, 220),
                      max(1, round(2 * lay.s)), cv2.LINE_AA, 4)
        for sx, sy in SCREWS:
            c = np.array(to_top(lay, wx + sx, wy + sy)) - (tx, ty)
            cv2.circle(self.top_base, tuple(np.round(c * 16).astype(int)), round(4 * lay.s * 16), (200, 205, 210),
                       -1, cv2.LINE_AA, 4)
        self.clock0 = 9 * 3600 + 30 * 60

    # -- the parts of a frame
    def top_view(self, cam: Cam, step: Step, u: float) -> Image.Image:
        lay = self.lay
        tx, ty, tw, th = lay.top
        img = self.top_base.copy()
        off = np.array([tx, ty])

        def tp(pts):
            return np.array([to_top(lay, x, y) for x, y in pts]) - off

        field_poly = tp(cam.corners())
        # Shade everything the stream doesn't show.
        mask = np.zeros(img.shape[:2], np.uint8)
        cv2.fillPoly(mask, [np.round(field_poly * 16).astype(np.int32)], 255, cv2.LINE_AA, 4)
        m = mask[..., None] / 255.0
        img = (img * (0.45 + 0.55 * m)).astype(np.uint8)
        hot = step.changing == "field"
        shade_polys(img, [field_poly], ORANGE if hot else BLUE, 0.12, ORANGE if hot else BLUE,
                    max(2, round(3 * lay.s)))
        if step.number == 0 or step.changing == "still":
            frac = cam.in_view()
            for n, fr in frac.items():
                x0, y0, x1, y1 = slot_rect(n)
                poly = tp([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
                if step.number == 0 and fr < 0.995:
                    cv2.polylines(img, [np.round(poly * 16).astype(np.int32)], True, ORANGE,
                                  max(2, round(3 * lay.s)), cv2.LINE_AA, 4)
                if step.changing == "still" and cam.checks > (n - 1) / 12 and fr >= 0.995:
                    cv2.polylines(img, [np.round(poly * 16).astype(np.int32)], True, (40, 170, 80),
                                  max(2, round(3 * lay.s)), cv2.LINE_AA, 4)
        hot = step.changing == "mount"
        shade_polys(img, [tp(mount_outline(cam))], ORANGE if hot else (34, 36, 40), 0.55 if hot else 0.6,
                    (255, 255, 255), max(1, round(1.5 * lay.s)))
        k = tw / (TOP_X1 - TOP_X0)
        ap = tp([(cam.ax, cam.ay)])[0]
        cv2.circle(img, tuple(np.round(ap * 16).astype(int)), round(P.lens_clear_ap / 2 * k * 16)
                   if hasattr(P, "lens_clear_ap") else round(20 * k * 16), (90, 90, 95), -1, cv2.LINE_AA, 4)
        c = tp([CENTRE])[0]
        arm = 12 * lay.s * 1.4
        for d in ((arm, 0), (0, arm)):
            for col, t in (((255, 255, 255), max(3, round(5 * lay.s))), ((0, 0, 0), max(1, round(2 * lay.s)))):
                cv2.line(img, tuple(np.round((c - d) * 16).astype(int)), tuple(np.round((c + d) * 16).astype(int)),
                         col, t, cv2.LINE_AA, 4)
        cv2.circle(img, tuple(np.round(ap * 16).astype(int)), round(5 * lay.s * 16), (255, 255, 255), -1, cv2.LINE_AA, 4)
        cv2.circle(img, tuple(np.round(ap * 16).astype(int)), round(3.6 * lay.s * 16), ORANGE, -1, cv2.LINE_AA, 4)

        if step.changing == "mount" and step.short.startswith("Centre"):
            d = np.array(CENTRE) - [self.start.ax, self.start.ay]
            n = np.linalg.norm(d)
            if n > 0.5:
                dirn = d / n
                base = tp([np.array([cam.ax, cam.ay]) + dirn * (TAB_TIP + 6)])[0]
                tip = base + np.array([dirn[0], -dirn[1]]) * 70 * lay.s * 1.3
                arrow(img, base, tip, ORANGE, max(3, round(5 * lay.s)))
                self.arrow_at = (base + tip) / 2
        if step.changing == "mount" and step.short.startswith("Square") and abs(self.start.phi) > 0.05:
            cc = tuple(np.round(ap * 16).astype(int))
            r = round((TAB_TIP + 22) * k * 16)
            sgn = 1 if self.start.phi > 0 else -1          # clockwise on screen to undo + phi
            a0, a1 = -60, -60 + sgn * 50
            cv2.ellipse(img, cc, (r, r), 0, a0, a1, ORANGE, max(3, round(5 * lay.s)), cv2.LINE_AA, 4)
            e = np.array(ap) + (TAB_TIP + 22) * k * np.array([math.cos(math.radians(a1)), math.sin(math.radians(a1))])
            tang = np.array([-math.sin(math.radians(a1)), math.cos(math.radians(a1))]) * sgn
            arrow(img, e - tang * 2, e + tang * 16 * lay.s * 1.4, ORANGE, max(3, round(5 * lay.s)))

        pil = Image.fromarray(img)
        d = ImageDraw.Draw(pil)
        fs = font(max(11, round(17 * lay.s)), True)
        for n in range(1, 13):
            x0, y0, x1, y1 = slot_rect(n)
            p = tp([(x0 + 4, y1 - 4)])[0]
            d.text(tuple(p), str(n), font=fs, fill=(255, 255, 255), stroke_width=max(2, round(3 * lay.s)),
                   stroke_fill=(30, 30, 32))
        fl = font(max(12, round(19 * lay.s)), True)
        bx = to_top(lay, 196.5, TOP_Y0 + 6)[0] - tx
        d.text((bx, th - 6 * lay.s), "FRONT (door)", font=fl, anchor="md", fill=(255, 255, 255))
        d.text((bx, 6 * lay.s), "BACK", font=fl, anchor="ma", fill=(255, 255, 255))
        if step.changing == "mount" and step.short.startswith("Centre"):
            dx, dy = np.array(CENTRE) - [self.start.ax, self.start.ay]
            lab = self.move_text(dx, dy, short=True)
            mid = getattr(self, "arrow_at", tp([(cam.ax, cam.ay)])[0])
            sw = max(2, round(3 * lay.s))
            bb = d.multiline_textbbox((0, 0), lab, font=fl, stroke_width=sw)
            lw_, lh_ = bb[2] - bb[0], bb[3] - bb[1]
            x = mid[0] + 22 * lay.s if mid[0] + 22 * lay.s + lw_ < tw - 6 else mid[0] - 22 * lay.s - lw_
            y = min(mid[1] - lh_ / 2, th - lh_ - 34 * lay.s)
            d.multiline_text((max(6, x), y), lab, font=fl, fill=ORANGE, stroke_width=sw, stroke_fill=(0, 0, 0),
                             align="left")
        if step.changing == "mount" and step.short.startswith("Square") and abs(self.start.phi) > 0.05:
            p = tp([np.array([cam.ax, cam.ay]) + [TAB_TIP + 18, TAB_TIP + 8]])[0]
            d.text(tuple(p), f"{abs(self.start.phi):.1f}° {self.turn_word()}", font=fl, fill=ORANGE,
                   stroke_width=max(2, round(3 * lay.s)), stroke_fill=(0, 0, 0))
        return pil

    def cam_view(self, cam: Cam, step: Step, t: float) -> Image.Image:
        lay = self.lay
        cx, cy, cw, ch = lay.cam
        img = self.deck.camera(cam, cw, ch)
        s = lay.s
        guide = step.short.startswith(("Centre", "Square", "Lock"))
        if guide:
            c = cam.to_picture([CENTRE], cw, ch)[0]
            for col, w_ in (((0, 0, 0), max(3, round(5 * s))), ((255, 255, 255), max(1, round(2 * s)))):
                cv2.circle(img, tuple(np.round(c * 16).astype(int)), round(15 * s * 16), col, w_, cv2.LINE_AA, 4)
        if step.short.startswith("Square"):
            a = cam.to_picture([(CENTRE[0] - 200, CENTRE[1]), (CENTRE[0] + 200, CENTRE[1])], cw, ch)
            mid = a.mean(axis=0)
            dashed_line(img, (0, mid[1]), (cw, mid[1]), (255, 255, 255), max(2, round(2 * s)), 14, 9)
        # The stream's own centre mark: two thin orange lines through the middle of the picture.
        t_ = max(1, round(2 * s))
        cv2.line(img, (0, round(ch / 2 * 16)), (cw * 16, round(ch / 2 * 16)), ORANGE, t_, cv2.LINE_AA, 4)
        cv2.line(img, (round(cw / 2 * 16), 0), (round(cw / 2 * 16), ch * 16), ORANGE, t_, cv2.LINE_AA, 4)
        pil = Image.fromarray(img)
        d = ImageDraw.Draw(pil, "RGBA")
        # Timestamp, top left, as the stream draws it.
        clock = self.clock0 + int(t)
        stamp = f"2026-10-20_{clock // 3600:02d}-{clock // 60 % 60:02d}-{clock % 60:02d}"
        ft = font(max(10, round(ch / 20)))
        tb = d.textbbox((10 * s, 10 * s), stamp, font=ft)
        d.rectangle([tb[0] - 4, tb[1] - 4, tb[2] + 4, tb[3] + 4], fill=(0, 0, 0, 128))
        d.text((10 * s, 10 * s), stamp, font=ft, fill=(255, 255, 255))
        now = round(FOCUS_PEAK * cam.score())
        self.history = [(t0, v) for t0, v in getattr(self, "history", []) if t - 120 <= t0 <= t] + [(t, now)]
        best = max(v for _, v in self.history)
        line = f"focus {now}  (best {best} in 2 min)"
        fy = tb[3] + 12 * s
        fb_ = font(max(9, round(ch / 26)))
        lb = d.textbbox((10 * s, fy), line, font=fb_)
        d.rectangle([lb[0] - 4, lb[1] - 4, lb[2] + 4, lb[3] + 4], fill=(0, 0, 0, 128))
        d.text((10 * s, fy), line, font=fb_, fill=(255, 255, 255))
        # LIVE, top right.
        fl = font(max(10, round(18 * s)), True)
        lw = fl.getlength("LIVE") + 38 * s
        d.rounded_rectangle([cw - lw - 12 * s, 10 * s, cw - 12 * s, 10 * s + 30 * s], radius=round(5 * s),
                            fill=(204, 0, 0, 230))
        d.ellipse([cw - lw - 2 * s, 19 * s, cw - lw + 10 * s, 31 * s], fill=(255, 255, 255))
        d.text((cw - 12 * s - 8 * s, 25 * s), "LIVE", font=fl, anchor="rm", fill=(255, 255, 255))
        # Focus score, bottom left.
        hot = step.changing == "focus"
        fs = font(max(10, round(17 * s)), True)
        bw, bh = fs.getlength("focus score (shown on the stream)  00") + 20 * s, 58 * s
        x0, y0 = 10 * s, ch - bh - 10 * s
        d.rectangle([x0, y0, x0 + bw, y0 + bh], fill=(0, 0, 0, 150))
        score = cam.score()
        d.text((x0 + 10 * s, y0 + 6 * s), "focus score (shown on the stream)", font=fs, fill=(255, 255, 255))
        d.text((x0 + bw - 10 * s, y0 + 6 * s), f"{now}", font=fs, anchor="ra",
               fill=ORANGE if hot else (255, 255, 255))
        d.rectangle([x0 + 10 * s, y0 + 34 * s, x0 + bw - 10 * s, y0 + 48 * s], fill=(255, 255, 255, 60))
        d.rectangle([x0 + 10 * s, y0 + 34 * s, x0 + 10 * s + (bw - 20 * s) * score, y0 + 48 * s],
                    fill=ORANGE if hot else (120, 200, 120))
        if guide:
            c = cam.to_picture([CENTRE], cw, ch)[0]
            if 0 < c[0] < cw and 0 < c[1] < ch:
                d.text((c[0] + 20 * s, c[1] + 16 * s), "deck centre", font=fs, fill=(255, 255, 255),
                       stroke_width=max(2, round(3 * s)), stroke_fill=(0, 0, 0))
        if cam.still > 0:
            a = int(255 * min(1.0, cam.still * 1.5))
            txt = "STILL  4056 × 3040  saved"
            fb = font(max(10, round(19 * s)), True)
            w_ = fb.getlength(txt) + 28 * s
            d.rounded_rectangle([cw - w_ - 12 * s, 50 * s, cw - 12 * s, 90 * s], radius=round(6 * s),
                                fill=(30, 140, 70, a))
            d.text((cw - 12 * s - w_ / 2, 70 * s), txt, font=fb, anchor="mm", fill=(255, 255, 255, a))
        return pil

    def move_text(self, dx: float, dy: float, short: bool = False) -> str:
        parts = []
        if abs(dy) >= 0.5:
            parts.append(f"{abs(dy):.0f} mm toward the {'door' if dy < 0 else 'back'}")
        if abs(dx) >= 0.5:
            parts.append(f"{abs(dx):.1f} mm {'right' if dx > 0 else 'left'}" if short else
                         f"{abs(dx):.1f} mm to the {'right' if dx > 0 else 'left'}")
        return ("slide " if short else "") + (",\n" if short else " and ").join(parts) if parts else "no move"

    def turn_word(self) -> str:
        return "clockwise" if self.start.phi > 0 else "anticlockwise"

    def readout(self, cam: Cam, step: Step) -> list[tuple[str, tuple]]:
        w, h = cam.field()
        dx, dy = cam.ax - CENTRE[0], cam.ay - CENTRE[1]
        zoom_hot = step.changing == "field"
        pos_hot = step.changing == "mount"
        return [(f"zoom {cam.f:.1f} mm   field {w:.0f} × {h:.0f} mm at the deck   {4056 / w:.1f} px/mm in a still",
                 ORANGE if zoom_hot else INK),
                ((f"lens axis {abs(dx):.1f} mm {'right' if dx >= 0 else 'left'}, {abs(dy):.1f} mm "
                  f"{'behind' if dy >= 0 else 'in front of'} the deck centre" if math.hypot(dx, dy) >= 0.5 else
                  "lens axis on the deck centre") + f"   turned {cam.phi:+.1f}°",
                 ORANGE if pos_hot else INK)]

    def rings(self, canvas: Image.Image, d: ImageDraw.ImageDraw, step: Step, box) -> None:
        """Which ring is which: the lens photo from camera/README.md, the step's rings in orange."""
        x0, y0, x1, y1 = (round(v) for v in box)
        if not hasattr(self, "lens_photo"):
            photo = Image.open(LID / "camera" / "frames" / "2026-10-15" / "lens_rings.jpg").crop((170, 0, 680, 720))
            k = (y1 - y0) / photo.height
            self.lens_photo = (photo.resize((round(photo.width * k), y1 - y0), Image.LANCZOS), k)
        photo, k = self.lens_photo
        canvas.paste(photo, (x0, y0))
        use = {1: {"ZOOM"}, 2: {"IRIS", "FOCUS"}, 5: {"ZOOM", "FOCUS", "IRIS"}}.get(step.number, set())
        rows = [("FOCUS", "near - far", (320, 195)), ("IRIS", "open - close", (264, 263)),
                ("ZOOM", "tele - wide", (236, 368))]
        tx = x0 + photo.width + 18
        d.text((tx, y0), "WHICH RING IS WHICH", font=font(17, True), fill=GREY)
        yy = y0 + 30
        for name, ends, (px, py) in rows:
            hot = name in use
            c = (x0 + (px - 170) * k, y0 + py * k)
            if hot:
                d.ellipse([c[0] - 11, c[1] - 11, c[0] + 11, c[1] + 11], outline=ORANGE, width=4)
            d.text((tx, yy), name, font=font(20, True), fill=ORANGE if hot else INK)
            d.text((tx + 90, yy + 2), f"({ends})", font=font(18), fill=ORANGE if hot else GREY)
            yy += 32
        d.text((tx, yy + 4), "Each ring has its own thumbscrew:\nloosen it, turn the ring, retighten.",
               font=font(17), fill=INK2, spacing=6)

    def focus_plot(self, d: ImageDraw.ImageDraw, cam: Cam, box: tuple[float, float, float, float]):
        x0, y0, x1, y1 = box
        s = self.lay.s
        d.rectangle([x0, y0, x1, y1], fill=(250, 250, 248), outline=(205, 205, 200))
        f = font(max(10, round(16 * s)))
        d.text((x0 + 8 * s, y0 + 6 * s), "focus score as the ring turns", font=f, fill=GREY)
        px0, px1, py0, py1 = x0 + 12 * s, x1 - 12 * s, y0 + 30 * s, y1 - 22 * s
        d.text((px0, y1 - 4 * s), "← nearer", font=f, anchor="ld", fill=PALE)
        d.text((px1, y1 - 4 * s), "farther →", font=f, anchor="rd", fill=PALE)

        def xy(r, sc):
            return px0 + (r + 1.1) / 1.7 * (px1 - px0), py1 - sc * (py1 - py0)
        if len(cam.trace) > 1:
            d.line([xy(r, sc) for r, sc in cam.trace], fill=ORANGE, width=max(2, round(3 * s)))
        if cam.trace:
            r, sc = cam.trace[-1]
            x, y = xy(r, sc)
            d.ellipse([x - 6 * s, y - 6 * s, x + 6 * s, y + 6 * s], fill=ORANGE, outline=(255, 255, 255))
            if max(t[1] for t in cam.trace) > 0.97 and len(cam.trace) > 3 and abs(r) < 0.02:
                xp, yp = xy(0.0, 1.0)
                d.text((xp, yp - 8 * s), "peak: stop here", font=font(max(10, round(16 * s)), True), anchor="md",
                       fill=INK)

    def side_panel(self, step: Step) -> Image.Image:
        img = Image.new("RGB", (W - VW, H), PANEL)
        d = ImageDraw.Draw(img)
        d.line([(0, 0), (0, H)], fill=(205, 205, 200), width=2)
        x, width = 40, W - VW - 76
        y = 34
        d.text((x, y), "OT-2 lid camera: centre, zoom, focus", font=font(22), fill=GREY)
        y += 48
        numbered = [s for s in self.steps if s.number]
        if step.number:
            d.text((x, y), f"Step {step.number} of {len(numbered)}", font=font(24, True), fill=ORANGE)
            y += 38
        for line in wrap(step.title, font(34, True), width):
            d.text((x, y), line, font=font(34, True), fill=INK)
            y += 44
        y += 8
        for line in wrap(step.body, font(23), width):
            d.text((x, y), line, font=font(23), fill=INK)
            y += 32
        if step.watch:
            y += 10
            for line in wrap(step.watch, font(21, True), width):
                d.text((x, y), line, font=font(21, True), fill=GREY)
                y += 29
        for heading, rows in step.extra:
            y += 22
            d.text((x, y), heading.upper(), font=font(19, True), fill=GREY)
            y += 32
            for row in rows:
                lines = wrap(row, font(21), width - 24)
                d.text((x, y), "•", font=font(21), fill=INK)
                for line in lines:
                    d.text((x + 22, y), line, font=font(21), fill=INK)
                    y += 29
                y += 4
        y = H - 34 - 31 * len(numbered)
        for s_ in numbered:
            here, done = s_.number == step.number, s_.number < step.number
            f = font(21, here)
            colour = INK if here else (GREY if done else PALE)
            if here:
                d.rectangle([x - 14, y - 2, x - 8, y + 24], fill=ORANGE)
            d.text((x, y), f"{s_.number:>2}", font=f, fill=colour)
            d.text((x + 40, y), s_.short + ("  ✓" if done else ""), font=f, fill=colour)
            y += 31
        return img

    def frame(self, cam: Cam, step: Step, u: float, t: float, panel: Image.Image | None) -> Image.Image:
        lay = self.lay
        canvas = Image.new("RGB", (lay.w, lay.h), "white")
        tx, ty, tw, th = lay.top
        cx, cy, cw, ch = lay.cam
        canvas.paste(self.top_view(cam, step, u), (tx, ty))
        canvas.paste(self.cam_view(cam, step, t), (cx, cy))
        d = ImageDraw.Draw(canvas)
        s = lay.s
        numbered = [s_ for s_ in self.steps if s_.number]
        if lay.gif:
            head = f"{step.number}/{len(numbered)}  {step.title}" if step.number else step.title
            d.text((12, 12), head, font=font(24, True), fill=INK)
            if step.number:
                d.text((12 + font(24, True).getlength(f"{step.number}/{len(numbered)}"), 12), "", font=font(24, True))
                d.text((12, 12), f"{step.number}/{len(numbered)}", font=font(24, True), fill=ORANGE)
            d.text((lay.w - 12, 18), "OT-2 lid camera", font=font(16), anchor="ra", fill=GREY)
            d.text((tx, ty - 4), "deck from above", font=font(14), anchor="ld", fill=GREY)
            d.text((cx, cy - 4), "what the stream shows", font=font(14), anchor="ld", fill=GREY)
            y = cy + ch + 8
            for text, colour in self.readout(cam, step)[:1]:
                d.text((cx, y), text, font=font(13), fill=colour)
            y = max(ty + th, cy + ch) + 32
            for line in wrap(step.gif, font(18), lay.w - 24)[:3]:
                d.text((12, y), line, font=font(18), fill=INK)
                y += 25
            # progress strip
            bw = (lay.w - 24 - 8 * (len(numbered) - 1)) / len(numbered)
            for k, s_ in enumerate(numbered):
                x0 = 12 + k * (bw + 8)
                here, done = s_.number == step.number, s_.number < step.number
                fill = ORANGE if here else ((205, 205, 200) if done else (236, 236, 232))
                d.rounded_rectangle([x0, lay.h - 30, x0 + bw, lay.h - 8], radius=4, fill=fill)
                d.text((x0 + bw / 2, lay.h - 19), f"{s_.number}. {s_.short}" + (" ✓" if done else ""),
                       font=font(13, here), anchor="mm", fill=(255, 255, 255) if here else INK)
        else:
            d.text((tx, ty - 14), "The deck from above, through the top window", font=font(22, True),
                   anchor="ld", fill=INK)
            d.text((cx, cy - 14), "What the stream shows", font=font(22, True), anchor="ld", fill=INK)
            y = cy + ch + 16
            for text, colour in self.readout(cam, step):
                d.text((cx, y), text, font=font(19), fill=colour)
                y += 28
            ly = ty + th + 14
            legend = [((34, 36, 40), "the mount's base and tabs"), (BLUE, "the camera's field"),
                      (ORANGE, "lens axis; this step's change"), ((0, 0, 0), "deck centre (5-8 rail)")]
            for k, (colour, text) in enumerate(legend):
                lx, lyy = tx + (k % 2) * 320, ly + (k // 2) * 27
                d.rectangle([lx, lyy + 4, lx + 16, lyy + 20], fill=colour)
                d.text((lx + 24, lyy), text, font=font(17), fill=INK2)
            self.rings(canvas, d, step, (tx, ly + 66, tx + tw, 1080 - 36 - 36 * 2 - 30))
            if step.changing == "focus" or (cam.trace and step.short.startswith("Focus")):
                self.focus_plot(d, cam, (cx, y + 8, cx + cw, y + 8 + 200))
            fc, lh = font(26, True), 36
            lines = wrap(step.gif, fc, VW - 2 * tx)
            if len(lines) > 2:                               # the lens photo above leaves room for two
                fc, lh = font(22, True), 26
                lines = wrap(step.gif, fc, VW - 2 * tx)[:3]
            y = lay.h - 36 - 36 * 2
            d.line([(tx, y - 18), (VW - tx, y - 18)], fill=(220, 220, 215), width=2)
            for line in lines:
                d.text((tx, y), line, font=fc, fill=INK)
                y += lh
            canvas.paste(panel, (VW, 0))
        return canvas


# --- the steps ---------------------------------------------------------------------------------------

def load_start() -> dict:
    cfg = dict(FALLBACK)
    if SETUP.exists():
        cfg.update(json.loads(SETUP.read_text()))
        cfg["source"] = str(SETUP.relative_to(LID))
    else:
        cfg["source"] = "fallback: rough reading of stream_frame_0228Z.jpg"
    return cfg


def make_steps(cfg: dict) -> tuple[list[Step], Cam]:
    f0, ft = float(cfg["focal_mm"]), float(cfg.get("target_focal_mm", 8.0))
    ox, oy = (float(v) for v in cfg["axis_offset_mm"])
    rot = float(cfg["rotation_deg"])
    s0 = Cam(CENTRE[0] + ox, CENTRE[1] + oy, f0, rot)
    w0, h0 = s0.field()
    wt, ht = replace(s0, f=ft).field()
    span = (slot_rect(3)[2] - slot_rect(1)[0], slot_rect(10)[3] - slot_rect(1)[1])     # 393 x 357.5 mm
    margin = (ht - span[1]) / 2                                                      # front and back, mm
    droop = span[0] / 2 * math.tan(math.radians(abs(rot)))
    cut = [n for n, fr in s0.in_view().items() if fr < 0.995]
    frac = s0.in_view()

    def how_cut(ns: list[int]) -> str:
        """'1–3 only 56–62 % in view, 10–12 91–99 %': each row's cut slots with their range."""
        parts = []
        for row in ([1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]):
            r = [n for n in row if n in ns]
            if r:
                lo, hi = (round(100 * min(frac[n] for n in r)), round(100 * max(frac[n] for n in r)))
                pct = f"{lo}–{hi} %" if lo != hi else f"{lo} %"
                parts.append(f"{slots_text(r)} {pct}")
        return "; ".join(parts)
    tip = TAB_TIP * math.tan(math.radians(abs(rot)))
    after_zoom = replace(s0, f=ft, defocus=DEFOCUS)
    focused = replace(after_zoom, defocus=0.0)
    centred = replace(focused, ax=CENTRE[0], ay=CENTRE[1])
    squared = replace(centred, phi=0.0)
    final_view = squared.in_view()
    all_in = [n for n, fr in final_view.items() if fr >= 0.995]

    def lerp(a: Cam, b: Cam, u: float, **kw) -> Cam:
        e = ease(u)
        return replace(a, ax=a.ax + (b.ax - a.ax) * e, ay=a.ay + (b.ay - a.ay) * e, f=a.f + (b.f - a.f) * e,
                       phi=a.phi + (b.phi - a.phi) * e, defocus=a.defocus + (b.defocus - a.defocus) * e, **kw)

    def ring(u: float) -> float:
        """The focus ring: from where the zoom left it, past the best point, then back to it."""
        return -1.0 + 1.45 * ease(u / 0.62) if u < 0.62 else 0.45 - 0.45 * ease((u - 0.62) / 0.38)

    def focus(u: float) -> Cam:
        c = replace(after_zoom, defocus=DEFOCUS * abs(ring(u)))
        c.trace = [(ring(v), replace(after_zoom, defocus=DEFOCUS * abs(ring(v))).score())
                   for v in np.linspace(0.0, u, max(2, round(120 * u)))]
        return c

    def check(u: float) -> Cam:
        flash = max(0.0, 1 - abs(u - 0.18) / 0.08) * 0.85 if 0.1 < u < 0.26 else 0.0
        return replace(squared, flash=flash, still=ease((u - 0.22) / 0.2), checks=ease((u - 0.35) / 0.6))

    dx, dy = CENTRE[0] - s0.ax, CENTRE[1] - s0.ay
    move = []
    if abs(dy) >= 0.5:
        move.append(f"{abs(dy):.0f} mm toward the {'door' if dy < 0 else 'back'}")
    if abs(dx) >= 0.5:
        move.append(f"{abs(dx):.1f} mm to the {'right' if dx > 0 else 'left'}")
    move_s = " and ".join(move) or "not at all"
    turn = "clockwise" if rot > 0 else "anticlockwise"

    def slots_text(ns: list[int]) -> str:
        rows = {1: [1, 2, 3], 4: [10, 11, 12]}
        out, rest = [], list(ns)
        for first, row in rows.items():
            if all(n in rest for n in row):
                out.append(f"{row[0]}–{row[-1]}")
                rest = [n for n in rest if n not in row]
        out += [str(n) for n in rest]
        return ", ".join(out[:-1]) + (" and " if len(out) > 1 else "") + out[-1] if out else "none"

    stream = "OT2 overhead Livestreams Playlist, youtube.com/playlist?list=PLM4VC4X_7XKQ"
    steps = [
        Step("Where it is now", "Where the camera is now",
             f"The stream shows about {w0:.0f} × {h0:.0f} mm of the deck, what the zoom gives at about "
             f"{f0:.1f} mm. The lens axis is {abs(oy):.0f} mm {'behind' if oy >= 0 else 'in front of'} and "
             f"{abs(ox):.1f} mm {'left' if ox <= 0 else 'right'} of the deck centre, and the picture is turned "
             f"{abs(rot):.1f}°. Slots partly out of view (orange): {how_cut(cut)} in view.\n"
             "Zoom first, then focus, then centre and square: zooming moves the focus, and the centre is "
             "easiest to judge once the whole deck shows.",
             f"Now: about {w0:.0f} × {h0:.0f} mm of deck, {abs(oy):.0f} mm {'behind' if oy >= 0 else 'in front of'} "
             f"and {abs(ox):.1f} mm {'left' if ox <= 0 else 'right'} of the deck centre, turned {abs(rot):.1f}°. "
             f"In view: {how_cut(cut)}.",
             extra=[("You need", [f"The stream on a phone or laptop: {stream}",
                                  "Your fingers: the lens's thumbscrews loosen by hand",
                                  "Painter's tape for the base's four tabs",
                                  "Ideally two people: one at the robot, one watching the stream"])],
             motion=0.0, state=lambda u: s0),
        Step("Zoom out", "Zoom out to the wide stop",
             f"Loosen the zoom ring's thumbscrew and turn the ring toward WIDE until it stops ({ft:g} mm). "
             f"The field grows from {w0:.0f} × {h0:.0f} to {wt:.0f} × {ht:.0f} mm at the deck. "
             "This lens is varifocal: zooming moves the focus, so the picture goes soft.",
             f"Loosen the zoom thumbscrew and turn the zoom ring to WIDE ({ft:g} mm). The view grows to "
             f"{wt:.0f} × {ht:.0f} mm and goes soft: on this lens, zoom moves focus.",
             watch="Watch for: the front and back rows coming into view.",
             motion=6.0, state=lambda u: lerp(s0, after_zoom, u), changing="field", number=1),
        Step("Focus", "Focus on the deck",
             "Open the iris fully, then turn the focus ring slowly. The focus number under the stream's "
             "timestamp rises, peaks and falls: turn back to the peak, where it matches \"best\", and "
             "tighten the focus thumbscrew. Then close the iris to about f/4, for more depth of field.",
             "Open the iris, turn the focus ring slowly: the focus number under the timestamp rises, peaks "
             "and falls. Go back to the peak and tighten the focus thumbscrew.",
             watch="The stream runs 5–20 s behind: turn a little, then wait for it to catch up.",
             motion=12.0, state=focus, changing="focus", number=2),
        Step("Centre", "Centre the mount over the deck",
             f"Slide the whole mount {move_s}, until the stream's orange cross sits on the deck centre: "
             "the middle of the rail between slots 5 and 8. Keep the base flat on the window. "
             f"At {ft:g} mm the field is only {margin:.1f} mm longer than the slots at the front and at the "
             "back, so get within about 4 mm.",
             f"Slide the mount {move_s}, until the orange cross sits on the middle of the rail between "
             f"slots 5 and 8. Get within about 4 mm: that is all the front and back margin there is.",
             watch="Moving the mount moves the picture the opposite way: slide it toward the door and the "
                   "deck moves up the screen.",
             motion=6.0, state=lambda u: lerp(focused, centred, u), changing="mount", number=3),
        Step("Square", "Square it to the deck",
             f"Turn the mount {abs(rot):.1f}° {turn}, seen from above, about the lens: a tab's tip moves "
             f"{tip:.1f} mm. Stop when the rails between the rows run level across the stream, then check "
             f"the cross again. It matters: turned {abs(rot):.1f}°, the picture's edges drop {droop:.1f} mm "
             f"from the middle to the outer slots, more than the {margin:.1f} mm margin.",
             f"Turn the mount {abs(rot):.1f}° {turn} (seen from above; a tab's tip moves {tip:.1f} mm) until the "
             f"rails between the rows are level. Left turned, the corner slots lose up to {droop:.1f} mm.",
             motion=5.0, state=lambda u: lerp(centred, squared, u), changing="mount", number=4),
        Step("Lock and check", "Lock it and take a still",
             "Tighten the zoom and focus thumbscrews and tape the base down over its four tabs. Then take a "
             "point-and-shoot still at the full 4056 × 3040 while the stream keeps running, as below. "
             + (f"All {len(all_in)} slots should be in it." if len(all_in) == 12 else
                f"Slots {slots_text([n for n in range(1, 13) if n not in all_in])} will still be cut off."),
             "Tighten the thumbscrews, tape the base down, take a 4056 × 3040 still while the stream runs "
             "(curl localhost:8081/still on the Pi, or ask @claude). "
             + ("All 12 slots in frame." if len(all_in) == 12 else ""),
             watch="If a front or back slot is clipped, slide the mount a few mm that way and check again.",
             extra=[("Take a still", ["On the Pi: ssh <pi> 'curl -s localhost:8081/still' > still.jpg",
                                      "Or comment: @claude take a still with the lid camera",
                                      "camera/measure_still.py turns a still into the mm to move"])],
             motion=5.0, state=check, changing="still", number=5),
    ]
    return steps, s0


def run(stills_only: bool) -> None:
    cfg = load_start()
    steps, s0 = make_steps(cfg)
    deck = Deck(deck_texture(cfg))
    print("start:", {k: cfg[k] for k in ("focal_mm", "axis_offset_mm", "rotation_deg", "target_focal_mm", "source")})

    mp4 = Frames(MP4, deck, steps, s0)
    gif = Frames(GIF, deck, steps, s0)
    ends: list[Image.Image] = []
    chapters: list[tuple[int, str]] = []
    gif_frames: list[np.ndarray] = []
    out = RENDERS / "setup_steps.mp4"
    tmp = out.with_suffix(".tmp.mp4")
    ff = None
    if not stills_only:
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                               "-crf", "20", "-pix_fmt", "yuv420p", "-g", str(FPS), "-movflags", "+faststart",
                               str(tmp)], stdin=subprocess.PIPE)
    n = 0
    for k, st in enumerate(steps):
        start = n
        chapters.append((start, f"{st.number}. {st.short}" if st.number else st.short))
        panel = mp4.side_panel(st)
        frames = round(st.motion * FPS)
        if not stills_only:
            for i in range(1, frames + 1):
                u = i / frames
                img = mp4.frame(st.state(u), st, u, n / FPS, panel)
                ff.stdin.write(img.tobytes())
                n += 1
        last = st.state(1.0)
        img = mp4.frame(last, st, 1.0, n / FPS, panel)
        ends.append(img)
        if stills_only:
            gif_frames.append(np.asarray(gif.frame(last, st, 1.0, n / FPS, None)))
        hold = max(HOLD_S * FPS, CHAPTER_S * FPS - (n - start)) + 4 * FPS * (k in (0, len(steps) - 1))
        if not stills_only:
            data = img.tobytes()
            for i in range(hold):
                ff.stdin.write(data)
            n += hold

        # The GIF: faster moves, shorter holds.
        if not stills_only:
            gm = round(min(st.motion * 0.5, 3.0) * GIF_FPS) if st.motion else 0
            for i in range(1, gm + 1):
                u = i / gm
                gif_frames.append(np.asarray(gif.frame(st.state(u), st, u, n / FPS, None)))
            g = np.asarray(gif.frame(st.state(1.0), st, 1.0, n / FPS, None))
            gif_frames += [g] * round((3.5 if k in (0, len(steps) - 1) else 2.5) * GIF_FPS)

    if not stills_only:
        ff.stdin.close()
        ff.wait()
        meta = Path(tempfile.mkstemp(suffix=".txt")[1])
        lines = [";FFMETADATA1", "title=OT-2 lid camera: centre, zoom, focus"]
        bounds = [c[0] for c in chapters[1:]] + [n]
        for (c0, name), c1 in zip(chapters, bounds):
            lines += ["[CHAPTER]", f"TIMEBASE=1/{FPS}", f"START={c0}", f"END={c1}", f"title={name}"]
        meta.write_text("\n".join(lines) + "\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-i", str(meta), "-map", "0",
                        "-map_metadata", "1", "-map_chapters", "1", "-c", "copy", "-movflags", "+faststart",
                        str(out)], check=True)
        tmp.unlink()
        meta.unlink()
        text = "\n".join(f"{(c // FPS) // 60}:{(c // FPS) % 60:02d} {name}" for c, name in chapters)
        (EXPORTS / "setup_steps_chapters.txt").write_text(text + "\n")
        print(f"{out.name}: {n} frames, {n / FPS:.1f} s, {out.stat().st_size / 1e6:.1f} MB")
        print(text)
        write_gif(gif_frames, RENDERS / "setup_steps.gif")

    sheet(ends, RENDERS / "setup_steps_sheet.png")
    if stills_only:
        d = Path("/tmp/setup_video_stills")
        d.mkdir(exist_ok=True)
        for k, img in enumerate(ends):
            img.save(d / f"{k}.png")
        for k, g in enumerate(gif_frames):
            Image.fromarray(g).save(d / f"gif_{k}.png")
        print("stills in", d)


def write_gif(frames: list[np.ndarray], path: Path) -> None:
    """Two passes through ffmpeg: one palette for the whole GIF, then only the changed rectangles."""
    raw = Path(tempfile.mkstemp(suffix=".rgb")[1])
    with raw.open("wb") as fh:
        for f in frames:
            fh.write(f.tobytes())
    src = ["-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{GIF_W}x{GIF_H}", "-r", str(GIF_FPS), "-i", str(raw)]
    pal = raw.with_suffix(".png")
    # The still's photo dithers into a lot of bytes; step down until the GIF is under GIF_MB.
    for colours, dither in ((256, "bayer:bayer_scale=4"), (128, "bayer:bayer_scale=5"), (96, "none")):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *src, "-vf",
                        f"palettegen=max_colors={colours}:stats_mode=diff", str(pal)], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *src, "-i", str(pal), "-lavfi",
                        f"paletteuse=dither={dither}:diff_mode=rectangle", "-loop", "0", str(path)], check=True)
        if path.stat().st_size <= GIF_MB * 1e6:
            break
    raw.unlink()
    pal.unlink()
    print(f"{path.name}: {len(frames)} frames, {len(frames) / GIF_FPS:.1f} s, {path.stat().st_size / 1e6:.1f} MB")


def sheet(ends: list[Image.Image], path: Path) -> None:
    """Where each step ends, 3 across."""
    tw, th, cols = 640, 360, 3
    rows = (len(ends) + cols - 1) // cols
    out = Image.new("RGB", (tw * cols, th * rows), "white")
    for i, img in enumerate(ends):
        out.paste(img.resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
    out.save(path, optimize=True)
    print(f"{path.name}: {len(ends)} stills")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stills", action="store_true", help="render only the frame each step ends on")
    run(ap.parse_args().stills)
