#!/usr/bin/env python3
"""Setting the lid camera's lens (zoom, iris, focus), as a video to pause on and as a GIF.

    python lens_video.py            # the MP4, the GIF, the contact sheet and the chapter list
    python lens_video.py --stills   # only the frame each step ends on, to /tmp/lens_video_stills

Writes ../renders/lens_rings.mp4 (1920 x 1080, 30 fps, a chapter per step), ../renders/lens_rings.gif
(960 px wide), ../renders/lens_rings_sheet.png and ../exports/lens_rings_chapters.txt.

Left: the Waveshare 8-50 mm lens as it hangs under the deck, seen from the side its thumbscrews are
on, drawn after the lab's photo (../camera/frames/2026-10-15/lens_rings.jpg). From the camera down:
focus (NEAR - FAR), iris (OPEN - CLOSE) and zoom (TELE - WIDE), the big ribbed ring just above the
window. Each thumbscrew rides between the two words printed on the barrel, which read upside down
because the lens hangs front-down. Middle: what the stream shows, made from a real full-resolution
still that was sharp at about 9 mm (../camera/frames/2026-10-20/still_0358Z_lit.jpg): cropped for
the zoom, blurred for focus, dimmed for the iris until the auto exposure catches up. The blur is a
thin-lens estimate: the defocus on the sensor divided by the f-number. Where focus lands on the ring
at each zoom is made up for the picture; only the order of the steps matters.
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

HERE = Path(__file__).resolve().parent
LID = HERE.parent
RENDERS = LID / "renders"
EXPORTS = LID / "exports"
STILL = LID / "camera/frames/2026-10-20/still_0358Z_lit.jpg"
PLATE_FIT = EXPORTS / "lid_camera_plate.json"

W, H, FPS = 1920, 1080, 30
GIF_W, GIF_H, GIF_FPS, GIF_MB = 960, 540, 10, 8.0
CHAPTER_S = 11                  # YouTube ignores chapters shorter than 10 s
HOLD_S = 5                      # each step's end stays up at least this long
ORANGE, AMBER = (255, 120, 0), (240, 170, 20)
INK, GREY, PANEL, BG = (30, 30, 32), (105, 105, 110), (244, 244, 241), (250, 250, 248)
FONTS = Path("/usr/share/fonts/truetype/dejavu")

# The lens drawing: 6 px per mm, axis at LX.
S = 6.0
LX = 330
TILT = 0.16                     # ring edges bow by this x radius: seen from a little above

# The view, and the simulated optics.
VX, VY, VW, VH = 650, 118, 640, 480
F_WIDE, F_TARGET = 9.0, 27.72   # the still's own zoom (about the W stop); the plate filling the box
PIX_MM = 0.00155                # IMX477 pixel
OBJECT_MM = 600.0               # lens to the plate's top, about
FOCUS_PEAK = 41                 # the stream's focus number when sharp, for show (as in setup_video.py)
BOX = (0.927, 0.828)            # SETUP_BOX: where the plate's outline lands at F_TARGET


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


def lerp(a: float, b: float, u: float) -> float:
    return a + (b - a) * u


# --- the optics ------------------------------------------------------------------------------------

def f_number(iris: float) -> float:
    """iris 0 = CLOSE (f/16 here, darker still on the lens), 1 = OPEN (f/1.4)."""
    return 1.4 * (16 / 1.4) ** (1 - iris)


def iris_for(n: float) -> float:
    return 1 - math.log(n / 1.4) / math.log(16 / 1.4)


def travel(f: float) -> float:
    """Image-side movement from focus at infinity to the 0.20 m minimum object distance, mm."""
    return f * f / (200 - f)


def best_focus(f: float) -> float:
    """Where on the focus ring (0 FAR, 1 NEAR) the plate is sharp at zoom f. Made up: it moves
    with the zoom, which is the point."""
    return 0.55 - 0.25 * (f - F_WIDE) / (F_TARGET - F_WIDE)


def blur_px(st: "State") -> float:
    """Blur-circle diameter, px of the 640 px wide view."""
    d_mm = (st.focus - best_focus(st.zoom)) * travel(st.zoom) + 0.79 * st.unscrew
    return abs(d_mm) / f_number(st.iris) / PIX_MM * VW / 4056


def sharpness(st: "State") -> float:
    return 1 / (1 + (blur_px(st) / 2.5) ** 2)


# --- the state of the lens at one instant ----------------------------------------------------------

@dataclass
class State:
    zoom: float = 22.0           # focal length, mm
    focus: float = 0.85          # 0 FAR .. 1 NEAR
    iris: float = 0.95           # 0 CLOSE .. 1 OPEN
    exposure: float = 1.0        # brightness against what the auto exposure aims for
    loose: dict = field(default_factory=lambda: {"focus": 0.0, "iris": 0.0, "zoom": 0.0})
    spin: dict = field(default_factory=lambda: {"focus": 0.0, "iris": 0.0, "zoom": 0.0})
    hot: tuple = ()              # rings drawn orange
    arrow: tuple = ()            # (ring, +1 toward NEAR/OPEN/WIDE or -1)
    wait: float = 0.0            # 0-1: the "wait for the stream" clock
    unscrew: float = 0.0         # turns the lens body has backed out of its thread
    lens_turn: float = 0.0       # deg, the whole lens body turning (step 8)
    note: str = ""               # a line under the view


def zoom_pos(f: float) -> float:
    """0 TELE .. 1 WIDE along the zoom thumbscrew's travel."""
    return (50 - f) / (50 - 8)


# Each ring: (top y, bottom y, radius mm, colour, rib count, rib depth), thumbscrew y, travel in deg,
# words at the two ends (the low end first: FAR, CLOSE, TELE).
RINGS = {
    "focus": dict(y=(281, 359), r=19.0, colour=(26, 26, 28), ribs=0, screw_y=318, deg=(-46, 34),
                  words=("FAR", "NEAR"), name="FOCUS", ends="NEAR / FAR"),
    "iris": dict(y=(359, 425), r=19.5, colour=(24, 24, 26), ribs=120, screw_y=376, deg=(-48, 26),
                 words=("CLOSE", "OPEN"), name="IRIS", ends="OPEN / CLOSE"),
    "zoom": dict(y=(425, 611), r=20.0, colour=(22, 22, 24), ribs=26, screw_y=440, deg=(-48, 30),
                 words=("TELE", "WIDE"), name="ZOOM", ends="TELE / WIDE"),
}


def ring_value(st: State, ring: str) -> float:
    return {"focus": st.focus, "iris": st.iris, "zoom": zoom_pos(st.zoom)}[ring]


def screw_deg(st: State, ring: str) -> float:
    a, b = RINGS[ring]["deg"]
    return lerp(a, b, ring_value(st, ring)) + st.lens_turn


# --- drawing the lens ------------------------------------------------------------------------------

def shade_row(r_px: float, colour, light=-30.0, shine=0.55) -> np.ndarray:
    """One row of a lit cylinder, 2r px wide."""
    n = int(2 * r_px)
    u = (np.arange(n) + 0.5 - r_px) / r_px
    phi = np.arcsin(np.clip(u, -1, 1))
    d = np.clip(np.cos(phi - math.radians(light)), 0, 1)
    spec = np.clip(np.cos(phi - math.radians(light * 0.6)), 0, 1) ** 30 * shine
    k = 0.35 + 0.75 * d
    c = np.array(colour, float)[None, :] * k[:, None] + 255 * spec[:, None]
    return np.clip(c, 0, 255)


def band(img: np.ndarray, y0: float, y1: float, r_mm: float, colour, cx: float = LX, light=-30.0,
         shine=0.55, alpha: float = 1.0) -> None:
    """A cylinder band, its top and bottom edges bowed as seen from a little above."""
    r = r_mm * S
    row = shade_row(r, colour, light, shine)
    x0 = int(round(cx - r))
    for i in range(row.shape[0]):
        u = (i + 0.5 - r) / r
        bow = TILT * r * math.sqrt(max(0.0, 1 - u * u))
        ya, yb = int(round(y0 + bow)), int(round(y1 + bow))
        x = x0 + i
        if 0 <= x < img.shape[1] and yb > ya:
            if alpha >= 1:
                img[ya:yb, x] = row[i]
            else:
                img[ya:yb, x] = img[ya:yb, x] * (1 - alpha) + row[i] * alpha


def surface_x(r_mm: float, deg: float, cx: float = LX) -> float:
    return cx + r_mm * S * math.sin(math.radians(deg))


def bow_at(r_mm: float, deg: float) -> float:
    return TILT * r_mm * S * math.cos(math.radians(deg))


def ribs(d: ImageDraw.ImageDraw, ring: dict, rot: float, y0: float, y1: float) -> None:
    n = ring["ribs"]
    r = ring["r"]
    for k in range(n):
        a = (k * 360 / n + rot) % 360
        a = a - 360 if a > 180 else a
        c = math.cos(math.radians(a))
        if c < 0.08:
            continue
        x = surface_x(r, a)
        b = bow_at(r, a)
        lit = max(0.0, math.cos(math.radians(a + 30)))
        w = max(1, round(3.2 * c)) if n < 60 else 1
        dark = tuple(int(v) for v in (8, 8, 9))
        light = tuple(int(40 + 70 * lit) for _ in range(3))
        d.line([(x, y0 + b), (x, y1 + b)], fill=dark, width=w)
        if n < 60:
            d.line([(x + w, y0 + b), (x + w, y1 + b)], fill=light, width=1)


def printed(img: Image.Image, text: str, r_mm: float, deg: float, y: float, size: int = 15,
            colour=(235, 235, 235)) -> None:
    """A word printed on the barrel, upside down as on the hanging lens, squashed by the curve."""
    c = math.cos(math.radians(deg))
    if c < 0.25:
        return
    f = font(size, True)
    tw = int(f.getlength(text)) + 4
    tile = Image.new("RGBA", (tw, size + 6), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((2, 1), text, font=f, fill=colour + (255,))
    tile = tile.rotate(180).resize((max(4, int(tw * c)), size + 6), Image.LANCZOS)
    x = surface_x(r_mm, deg) - tile.width / 2
    img.alpha_composite(tile, (int(x), int(y + bow_at(r_mm, deg) - tile.height / 2)))


def thumbscrew(d: ImageDraw.ImageDraw, ring: dict, deg: float, loose: float, spin: float, hot: bool,
               slotted: bool) -> None:
    """A thumbscrew standing out of its ring, `loose` backs it out, `spin` turns its head."""
    s = math.sin(math.radians(deg))
    c = math.cos(math.radians(deg))
    y = ring["screw_y"] + bow_at(ring["r"], deg)
    x0 = surface_x(ring["r"], deg)
    out = (7 + 1.5 * loose) * S
    x1 = x0 + s * out
    metal, edge = (176, 178, 182), (70, 70, 74)
    if hot:
        metal, edge = (255, 170, 90), ORANGE
    d.line([(x0, y), (x1, y)], fill=(120, 120, 125), width=9)
    hw = max(9.0, 11 * abs(s) + 13 * c)        # head, seen from the side or end on
    hh = 30
    d.rounded_rectangle([x1 - hw, y - hh / 2, x1 + hw, y + hh / 2], radius=6, fill=metal, outline=edge,
                        width=3 if hot else 2)
    for k in range(7):                          # knurl, or the slot, turning with `spin`
        a = (k / 7 + spin) % 1.0
        yy = y - hh / 2 + 3 + a * (hh - 6)
        if slotted:
            if k == 0:
                d.line([(x1 - hw + 4, y - 9 + 18 * a), (x1 + hw - 4, y + 9 - 18 * a)], fill=edge, width=3)
        else:
            d.line([(x1 - hw + 3, yy), (x1 + hw - 3, yy)], fill=edge, width=1)


def curved_arrow(d: ImageDraw.ImageDraw, ring: dict, a0: float, a1: float, colour, label: str) -> None:
    """An arrow along the front of a ring, from angle a0 to a1 (deg)."""
    r = ring["r"] + 3.5
    y = ring["y"][1] + 16
    pts = []
    for k in range(25):
        a = lerp(a0, a1, k / 24)
        pts.append((surface_x(r, a), y + bow_at(r, a)))
    d.line(pts, fill=colour, width=6, joint="curve")
    (xa, ya), (xb, yb) = pts[-2], pts[-1]
    ang = math.atan2(yb - ya, xb - xa)
    tip = (xb + 10 * math.cos(ang), yb + 10 * math.sin(ang))
    l = (xb + 13 * math.cos(ang + 2.4), yb + 13 * math.sin(ang + 2.4))
    rr = (xb + 13 * math.cos(ang - 2.4), yb + 13 * math.sin(ang - 2.4))
    d.polygon([tip, l, rr], fill=colour)
    f = font(19, True)
    tx = tip[0] + 12 if xb > xa else tip[0] - 12 - f.getlength(label)
    d.rounded_rectangle([tx - 6, tip[1] - 15, tx + f.getlength(label) + 6, tip[1] + 13], radius=6,
                        fill=(255, 255, 255), outline=colour, width=2)
    d.text((tx, tip[1] - 12), label, font=f, fill=colour)


class Lens:
    """The static parts drawn once; rings, thumbscrews and words each frame."""

    TOP = 160                    # camera board's underside

    def __init__(self) -> None:
        a = np.zeros((H, 640, 3), float)
        a[:] = BG
        a[100:142, 20:620] = (32, 32, 34)                        # deck, 5 mm, seen edge on
        a[100:104, 20:620] = (70, 70, 74)
        for sx in (-15, 15):                                     # camera bosses
            x = int(LX + sx * S)
            a[142:160, x - 9:x + 9] = (40, 40, 42)
        a[160:172, int(LX - 19 * S):int(LX + 19 * S)] = (22, 110, 60)   # HQ Camera board, 2 mm
        a[160:162, int(LX - 19 * S):int(LX + 19 * S)] = (60, 160, 100)
        band(a, 172, 214, 17.5, (38, 38, 40), shine=0.35)        # camera mount, back-focus ring
        band(a, 214, 244, 16.0, (150, 152, 156), shine=0.8)      # C-CS adapter
        band(a, 244, 281, 18.0, (36, 36, 38), shine=0.45)        # lens mount end
        band(a, 271, 281, 18.6, (170, 172, 176), shine=0.9)      # its chrome ring
        self.base = a
        # The front, below the zoom ring; drawn each frame because the lens can move (step 8).
        win = np.zeros((H, 640, 3), float)
        win[:] = BG
        win[742:774, 20:620] = (205, 226, 240)                   # the window, 5 mm
        win[742:745, 20:620] = (150, 190, 220)
        win[706:742, 20:620] = (28, 28, 30)                      # the base plate
        self.below = win

    def draw(self, st: State, t: float) -> Image.Image:
        a = self.base.copy()
        drop = st.unscrew * 0.79 * S * 3                         # drawn 3x so a turn shows
        a[706:H] = self.below[706:H]
        # Rings and front, all moving down together if the lens backs out.
        for name in ("focus", "iris", "zoom"):
            ring = RINGS[name]
            band(a, ring["y"][0] + drop, ring["y"][1] + drop, ring["r"], ring["colour"])
        band(a, 611 + drop, 626 + drop, 19.6, (190, 150, 40), shine=0.9)    # gold band
        band(a, 626 + drop, 676 + drop, 19.0, (26, 26, 28))                 # front barrel
        if drop:                                                # the gap in the thread
            band(a, 281, 281 + drop, 15.0, (200, 200, 205), shine=0.3)
        # Collar around the lens front, drawn see-through in front of it.
        band(a, 622, 706, 26.0, (30, 30, 32), alpha=0.55, shine=0.2)
        img = Image.fromarray(a.astype(np.uint8)).convert("RGBA")
        d = ImageDraw.Draw(img)
        for name, ring in RINGS.items():
            if ring["ribs"]:
                y0, y1 = ring["y"]
                yy = (y0 + drop + 34, y1 + drop - 4) if name == "iris" else (y0 + drop + 26, y1 + drop - 6)
                ribs(d, ring, screw_deg(st, name) * 1.0, *yy)
        for name, ring in RINGS.items():
            lo, hi = ring["deg"]
            yw = (ring["screw_y"] + 30 if name == "zoom" else ring["screw_y"]) + drop
            printed(img, ring["words"][0], ring["r"], lo - 10 + st.lens_turn, yw, size=16)
            printed(img, ring["words"][1], ring["r"], hi + 18 + st.lens_turn, yw, size=16)
        d = ImageDraw.Draw(img)
        for name, ring in RINGS.items():
            rr = dict(ring, screw_y=ring["screw_y"] + drop)
            thumbscrew(d, rr, screw_deg(st, name), st.loose[name], st.spin[name], name in st.hot,
                       slotted=name == "focus")
        # Hot rings: an orange outline down the silhouette.
        for name in st.hot:
            ring = RINGS[name]
            r = ring["r"] * S + 6
            y0, y1 = ring["y"][0] + drop, ring["y"][1] + drop
            d.line([(LX - r, y0), (LX - r, y1)], fill=ORANGE, width=5)
            d.line([(LX + r, y0), (LX + r, y1)], fill=ORANGE, width=5)
        if st.arrow:
            name, sgn = st.arrow
            ring = dict(RINGS[name])
            ring["y"] = (ring["y"][0] + drop, ring["y"][1] + drop)
            here = screw_deg(st, name)
            word = ring["words"][1] if sgn > 0 else ring["words"][0]
            curved_arrow(d, ring, here, here + 28 * sgn, ORANGE, f"toward {word}")
        self.labels(d, st, drop)
        return img.convert("RGB")

    def labels(self, d: ImageDraw.ImageDraw, st: State, drop: float) -> None:
        fb, f = font(21, True), font(17)
        x = 470
        for name, ring in RINGS.items():
            y = ring["screw_y"] + drop - 22
            hot = name in st.hot
            colour = ORANGE if hot else INK
            xe = LX + ring["r"] * S + 4
            d.line([(xe, y + 12), (x - 8, y + 12)], fill=colour, width=2)
            d.text((x, y), ring["name"], font=fb, fill=colour)
            d.text((x, y + 25), ring["ends"], font=f, fill=GREY if not hot else colour)
        g = font(15)
        d.text((24, 156), "camera board", font=g, fill=GREY)
        d.text((24, 178), "camera's back-focus", font=g, fill=GREY)
        d.text((24, 196), "ring: leave it", font=g, fill=GREY)
        d.text((24, 222), "C-CS adapter (one)", font=g, fill=GREY)
        d.text((24, 712), "base and collar", font=g, fill=(200, 200, 204))
        d.text((24, 778), "top window", font=g, fill=GREY)
        d.text((LX - 120, 800), "plate, about 0.6 m below", font=font(17), fill=GREY)
        d.line([(LX, 826), (LX, 856)], fill=GREY, width=3)
        d.polygon([(LX - 8, 852), (LX + 8, 852), (LX, 866)], fill=GREY)


# --- what the stream shows -------------------------------------------------------------------------

class Stream:
    def __init__(self) -> None:
        img = cv2.cvtColor(cv2.imread(str(STILL)), cv2.COLOR_BGR2RGB)
        self.full = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2), interpolation=cv2.INTER_AREA)
        fit = json.loads(PLATE_FIT.read_text())
        aff = np.array(fit["plate_to_still"])
        self.plate = aff[:, 2] / 2                                  # plate centre, half-res px
        self.f0 = fit["focal_mm"]                                   # the still's zoom
        self.cache: dict = {}

    def crop(self, f: float) -> np.ndarray:
        key = round(f, 2)
        if key in self.cache:
            return self.cache[key]
        hh, ww = self.full.shape[:2]
        cw = ww * self.f0 / max(f, self.f0)
        ch = cw * VH / VW
        tw = ww * self.f0 / F_TARGET
        u = min(max((ww - cw) / (ww - tw), 0.0), 1.0)
        cx = lerp(ww / 2, self.plate[0], u)
        cy = lerp(hh / 2, self.plate[1], u)
        cx = min(max(cx, cw / 2), ww - cw / 2)
        cy = min(max(cy, ch / 2), hh - ch / 2)
        m = np.array([[VW / cw, 0, VW / 2 - cx * VW / cw], [0, VH / ch, VH / 2 - cy * VH / ch]])
        out = cv2.warpAffine(self.full, m, (VW, VH), flags=cv2.INTER_AREA if cw > VW else cv2.INTER_LINEAR)
        if len(self.cache) > 400:
            self.cache.clear()
        self.cache[key] = out
        return out

    def view(self, st: State) -> np.ndarray:
        v = self.crop(st.zoom).astype(np.float32)
        b = blur_px(st)
        if b > 0.6:
            v = cv2.GaussianBlur(v, (0, 0), b / 2.4)
        v = np.clip(v * st.exposure, 0, 255)
        return v.astype(np.uint8)


def overlay(d: ImageDraw.ImageDraw, st: State) -> None:
    """The stream's setup overlay: cross, box, focus number."""
    cx, cy = VX + VW / 2, VY + VH / 2
    d.line([(cx - 40, cy), (cx + 40, cy)], fill=ORANGE, width=2)
    d.line([(cx, cy - 40), (cx, cy + 40)], fill=ORANGE, width=2)
    bw, bh = VW * BOX[0] / 2, VH * BOX[1] / 2
    d.rectangle([cx - bw, cy - bh, cx + bw, cy + bh], outline=ORANGE, width=2)
    n = round(3 + (FOCUS_PEAK - 3) * sharpness(st) * min(1.0, st.exposure * 1.2))
    f = font(18, True)
    d.rectangle([VX + 6, VY + 6, VX + 238, VY + 58], fill=(0, 0, 0))
    d.text((VX + 12, VY + 8), "2026-10-22_15-10-00", font=f, fill=(255, 255, 255))
    d.text((VX + 12, VY + 32), f"focus {n}", font=f, fill=(255, 255, 255))


def wait_clock(d: ImageDraw.ImageDraw, u: float) -> None:
    """A stopwatch: wait about 20 s for the stream."""
    x, y, r = VX + VW - 60, VY + 60, 34
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255), outline=ORANGE, width=4)
    d.pieslice([x - r + 6, y - r + 6, x + r - 6, y + r - 6], -90, -90 + 360 * u, fill=(255, 205, 160))
    a = math.radians(-90 + 360 * u)
    d.line([(x, y), (x + (r - 8) * math.cos(a), y + (r - 8) * math.sin(a))], fill=ORANGE, width=3)
    f = font(17, True)
    label = "wait ~20 s, then look"
    tw = f.getlength(label)
    d.rectangle([x - tw - 52, y - 13, x - r - 6, y + 13], fill=(255, 255, 255))
    d.text((x - tw - 46, y - 11), label, font=f, fill=ORANGE)


# --- the steps -------------------------------------------------------------------------------------

@dataclass
class Step:
    number: int
    short: str                   # chapter title
    title: str
    text: str
    motion: float                # s of movement before the hold
    state: Callable[[float], State]


def steps() -> list[Step]:
    s0 = State()                                         # where it is now: zoomed in, out of focus
    nf = 1.4 * (16 / 1.4) ** (1 - 0.95)
    out: list[Step] = []

    def rings(u: float) -> State:
        order = ("focus", "iris", "zoom")
        k = min(int(u * 3), 2)
        return replace(s0, hot=(order[k],), note="Now: zoomed in and far out of focus")

    out.append(Step(1, "The three rings", "The three rings",
                    "From the camera down: FOCUS (NEAR / FAR), IRIS (OPEN / CLOSE) and ZOOM "
                    "(TELE / WIDE), the big ribbed ring just above the window. Each has its own "
                    "thumbscrew, which rides between the two words printed on the barrel. The words "
                    "read upside down because the lens hangs front-down.\n"
                    "Leave the camera's own back-focus ring, above the lens, alone.",
                    9.0, rings))

    def screw(u: float) -> State:
        st = replace(s0, hot=("focus",), loose=dict(s0.loose), spin=dict(s0.spin))
        if u < 0.35:
            v = ease(u / 0.35)
            st.loose["focus"], st.spin["focus"] = v, -2 * v
            st.note = "Loosen: about one turn, anticlockwise"
        elif u < 0.7:
            v = ease((u - 0.35) / 0.35)
            st.loose["focus"], st.spin["focus"] = 1.0, -2.0
            st.focus = lerp(s0.focus, s0.focus - 0.12, v)
            st.arrow = ("focus", -1)
            st.note = "Push the thumbscrew: it turns the ring"
        else:
            v = ease((u - 0.7) / 0.3)
            st.focus = s0.focus - 0.12
            st.loose["focus"], st.spin["focus"] = 1 - v, -2 + 2 * v
            st.note = "Tighten it again, finger tight"
        return st

    out.append(Step(2, "Loosen, push, retighten", "Loosen, push, retighten",
                    "Loosen a ring's thumbscrew about one turn (anticlockwise, looking at its head). "
                    "Don't take it out. Push the thumbscrew toward the word you want: that turns "
                    "the ring. Tighten it again, finger tight, once the picture is right.",
                    6.0, screw))
    s1 = replace(s0, focus=s0.focus - 0.12)

    def wide(u: float) -> State:
        v = ease(u)
        loose = {"focus": 0.0, "iris": 0.0, "zoom": min(1.0, u * 4) if u < 0.85 else (1 - u) / 0.15}
        return replace(s1, zoom=lerp(s1.zoom, F_WIDE, v), hot=("zoom",), loose=loose,
                       arrow=("zoom", 1) if u < 0.85 else (),
                       note="More of the deck, and focus is easiest to find")

    out.append(Step(3, "Zoom to the WIDE end", "Zoom to the WIDE end first",
                    "Loosen the zoom thumbscrew and push it toward WIDE until it stops. The stream "
                    "shows more of the deck. Focus is easiest to find at this end, and on 20 Oct "
                    "the camera was sharp here.",
                    5.0, wide))
    s2 = replace(s1, zoom=F_WIDE)

    half = 0.5

    def iris(u: float) -> State:
        v = ease(min(u / 0.5, 1.0))
        ia = lerp(s2.iris, half, v)
        n0 = f_number(s2.iris)
        dim = (n0 / f_number(ia)) ** 2
        rec = ease((u - 0.5) / 0.4) if u > 0.5 else 0.0
        loose = {"focus": 0.0, "iris": 1.0 if u < 0.9 else (1 - u) / 0.1, "zoom": 0.0}
        return replace(s2, iris=ia, exposure=lerp(dim, 1.0, rec), hot=("iris",), loose=loose,
                       arrow=("iris", -1) if u < 0.5 else (),
                       note="Dims, then the auto exposure brings it back")

    out.append(Step(4, "Iris about halfway", "Iris about halfway, not fully open",
                    "Set the iris about halfway between OPEN and CLOSE (about f/4). Fully open, the "
                    "sharp zone is so thin that a stream running 5-20 s behind skips right past it. "
                    "The picture dims for a moment until the camera's auto exposure catches up.",
                    5.0, iris))
    s3 = replace(s2, iris=half)

    # Focus: nudges toward FAR, past the best, back one.
    best = best_focus(F_WIDE)
    path = [s3.focus - k * 0.06 for k in range(0, 5)]
    path += [path[-1] + 0.06]
    path = [p for p in path]

    def nudges(st0: State, seq: list[float], u: float, ring="focus", key="focus") -> State:
        n = len(seq) - 1
        k = min(int(u * n), n - 1)
        w = u * n - k
        v = ease(min(w / 0.3, 1.0))
        val = lerp(seq[k], seq[k + 1], v)
        sgn = 1 if seq[k + 1] > seq[k] else -1
        st = replace(st0, hot=(ring,), loose={**st0.loose, ring: 1.0},
                     wait=(w - 0.3) / 0.7 if 0.3 < w and u < 0.985 else 0.0)
        if key == "focus":
            st.focus = val
        st.arrow = (ring, sgn) if w < 0.3 else ()
        return st

    def focus(u: float) -> State:
        if u > 0.94:
            st = nudges(s3, path, 0.9999)
            st.loose = {**st.loose, "focus": (1 - u) / 0.06}
            st.wait, st.arrow = 0.0, ()
        else:
            st = nudges(s3, path, u / 0.94)
        sh = sharpness(st)
        st.note = "Sharpest so far: stop here" if sh > 0.9 else (
            "Worse: go back one nudge" if st.focus < best - 0.03 else "Getting sharper: keep going")
        return st

    out.append(Step(5, "Focus in small nudges", "Focus in small nudges",
                    "Loosen the focus thumbscrew. Nudge it 1-2 mm toward NEAR or FAR, then wait about "
                    "20 s for the stream to catch up. Keep going while the picture gets sharper and "
                    "the focus number under the time rises. When it gets worse, go back one nudge. "
                    "Tighten.",
                    14.0, focus))
    s4 = replace(s3, focus=path[-1])

    # Zoom in toward TELE in three steps, refocusing after each.
    zs = [F_WIDE, 14.0, 20.0, F_TARGET]

    def zoom_in(u: float) -> State:
        k = min(int(u * 3), 2)
        w = u * 3 - k
        st = replace(s4)
        st.zoom = zs[k]
        st.focus = best_focus(zs[k]) if k else s4.focus
        if w < 0.3:                                                 # zoom a little
            v = ease(w / 0.3)
            st.zoom = lerp(zs[k], zs[k + 1], v)
            st.hot, st.arrow = ("zoom",), ("zoom", -1)
            st.loose = {"focus": 0.0, "iris": 0.0, "zoom": 1.0}
            st.note = "Zoom in a little: the picture goes soft"
        else:                                                       # then refocus
            st.zoom = zs[k + 1]
            p0, p1 = st.focus, best_focus(zs[k + 1])
            seq = [p0, lerp(p0, p1, 0.5), p1]
            st = nudges(st, seq, (w - 0.3) / 0.7)
            st.note = "Refocus in nudges, as in step 5"
        return st

    out.append(Step(6, "Zoom in a little, refocus, repeat", "Zoom in a little, refocus, repeat",
                    "Push the zoom thumbscrew a few millimetres toward TELE, then refocus as in step 5. "
                    "Repeat until the plate fills the orange box on the stream (about 27-28 mm). This "
                    "lens loses focus every time the zoom moves, so take it in small steps rather than "
                    "all at once.",
                    18.0, zoom_in))
    s5 = replace(s4, zoom=F_TARGET, focus=best_focus(F_TARGET))

    f8 = iris_for(8.0)

    def lock(u: float) -> State:
        st = replace(s5, hot=("iris", "focus", "zoom"))
        v = ease(min(u / 0.4, 1.0))
        st.iris = lerp(s5.iris, f8, v)
        st.exposure = lerp(1.0, (f_number(s5.iris) / f_number(st.iris)) ** 2, v) if u < 0.4 else \
            lerp((f_number(s5.iris) / 8.0) ** 2, 1.0, ease((u - 0.4) / 0.3))
        st.arrow = ("iris", -1) if u < 0.4 else ()
        t = ease((u - 0.45) / 0.45) if u > 0.45 else 0.0
        st.loose = {"focus": 1 - t, "iris": 1 - t if u > 0.4 else 1.0, "zoom": 1 - t}
        st.spin = {k: 2 * t for k in st.loose}
        st.note = "Close to about f/8, then tighten all three" if u < 0.95 else "Locked"
        return st

    out.append(Step(7, "Iris to f/8, tighten all three", "Iris to about f/8, then tighten all three",
                    "Close the iris partway, to about f/8: the sharp zone then covers the wells' rims and "
                    "the paint below them. The auto exposure makes up the light. Tighten all three "
                    "thumbscrews, finger tight, and check the stream once more.",
                    6.0, lock))
    s6 = replace(s5, iris=f8)

    def trouble(u: float) -> State:
        st = replace(s6, zoom=F_WIDE, focus=best_focus(F_WIDE), iris=half, hot=())
        if u < 0.45:                                                # backed out 1.2 turns: blurred
            st.unscrew = 1.2
            st.focus = 0.5 + 0.45 * math.sin(u / 0.45 * math.pi * 2)
            st.loose = {"focus": 1.0, "iris": 0.0, "zoom": 0.0}
            st.hot = ("focus",)
            st.note = "Lens backed out: no focus position is sharp"
        else:
            v = ease((u - 0.45) / 0.45)
            st.unscrew = 1.2 * (1 - v)
            st.lens_turn = -360 * 1.2 * (1 - v) * 0.12
            st.note = "Screw the lens body back in until snug" if v < 1 else "Back in: sharp again"
        return st

    out.append(Step(8, "Still blurry at WIDE? Check the lens", "Never sharp, even at WIDE?",
                    "Then the lens sits at the wrong distance from the sensor, and no ring setting can "
                    "make that up. Hold the camera board still and try to turn the whole lens body: "
                    "turning a stiff ring can unscrew it, 0.8 mm per turn. Screw it back in until "
                    "it's snug. Check too that the one C-CS adapter is screwed fully into the camera, "
                    "and that the camera's own back-focus ring is locked by its small screw.",
                    10.0, trouble))
    return out


# --- frames ----------------------------------------------------------------------------------------

class Frames:
    def __init__(self, all_steps: list[Step]) -> None:
        self.lens = Lens()
        self.stream = Stream()
        self.steps = all_steps

    def side_panel(self, st: Step) -> Image.Image:
        pw = W - 1310
        img = Image.new("RGB", (pw, H), PANEL)
        d = ImageDraw.Draw(img)
        x = 36
        d.text((x, 34), f"Step {st.number} of {len(self.steps)}", font=font(26, True), fill=ORANGE)
        y = 72
        for line in wrap(st.title, font(32, True), pw - 2 * x):
            d.text((x, y), line, font=font(32, True), fill=INK)
            y += 42
        y += 12
        for line in wrap(st.text, font(22), pw - 2 * x):
            d.text((x, y), line, font=font(22), fill=INK)
            y += 31
        y = max(y + 24, 640)
        d.line([(x, y - 14), (pw - x, y - 14)], fill=(210, 210, 206), width=2)
        for s in self.steps:
            done = s.number < st.number
            cur = s.number == st.number
            colour = ORANGE if cur else (GREY if done else INK)
            mark = ">" if cur else ("✓" if done else " ")
            d.text((x, y), mark, font=font(21, True), fill=colour)
            d.text((x + 28, y), f"{s.number}. {s.short}", font=font(21, cur), fill=colour)
            y += 34
        d.text((x, H - 44), "OT-2 lid camera: Waveshare 8-50 mm zoom on the HQ Camera", font=font(16), fill=GREY)
        return img

    def frame(self, st: State, step: Step, u: float, panel: Image.Image | None) -> Image.Image:
        img = Image.new("RGB", (W, H), BG)
        img.paste(self.lens.draw(st, u), (0, 0))
        d = ImageDraw.Draw(img)
        d.text((24, 22), "The lens, from the thumbscrew side", font=font(26, True), fill=INK)
        d.text((24, 58), "as it hangs under the deck", font=font(19), fill=GREY)
        d.text((VX, 22), "What the stream shows", font=font(26, True), fill=INK)
        d.text((VX, 58), "on YouTube 5-20 s later", font=font(19), fill=GREY)
        v = self.stream.view(st)
        img.paste(Image.fromarray(v), (VX, VY))
        d.rectangle([VX - 2, VY - 2, VX + VW + 1, VY + VH + 1], outline=INK, width=2)
        overlay(d, st)
        if st.wait > 0:
            wait_clock(d, min(st.wait, 1.0))
        # Sharpness bar and the numbers behind the picture.
        y = VY + VH + 26
        sh = sharpness(st)
        d.text((VX, y), "Sharpness", font=font(20, True), fill=INK)
        d.rectangle([VX + 120, y + 2, VX + VW, y + 24], fill=(226, 226, 222))
        d.rectangle([VX + 120, y + 2, VX + 120 + (VW - 120) * sh, y + 24],
                    fill=ORANGE if sh > 0.9 else (200, 200, 196) if sh < 0.3 else AMBER)
        y += 40
        d.text((VX, y), f"zoom {st.zoom:.0f} mm    iris f/{f_number(st.iris):.1f}    "
                        f"blur {blur_px(st) * 4056 / VW:,.0f} px on the sensor", font=font(19), fill=GREY)
        if st.note:
            y += 40
            for line in wrap(st.note, font(26, True), VW):
                d.text((VX, y), line, font=font(26, True), fill=ORANGE)
                y += 34
        tip = ("The stream runs 5-20 s behind the lens. Make one small move, then wait "
               "before you judge: turning while you watch sweeps straight past the sharp point.")
        ty = 860
        d.rounded_rectangle([VX, ty - 14, VX + VW, ty + 84], radius=10, fill=(255, 241, 228))
        for line in wrap(tip, font(20), VW - 30):
            d.text((VX + 15, ty), line, font=font(20), fill=INK)
            ty += 27
        d.text((VX, H - 70), "Picture: a real still from 20 Oct, cropped and blurred to show the effect. "
                             "Where focus\nlands on the ring at each zoom is only an illustration.",
               font=font(15), fill=GREY)
        if panel is not None:
            img.paste(panel, (1310, 0))
        return img


def write_gif(frames: list[np.ndarray], path: Path) -> None:
    """Two passes through ffmpeg: one palette for the whole GIF, then only the changed rectangles."""
    raw = Path(tempfile.mkstemp(suffix=".rgb")[1])
    with raw.open("wb") as fh:
        for f in frames:
            fh.write(f.tobytes())
    src = ["-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{GIF_W}x{GIF_H}", "-r", str(GIF_FPS), "-i", str(raw)]
    pal = raw.with_suffix(".png")
    for colours, dither in ((256, "bayer:bayer_scale=4"), (128, "bayer:bayer_scale=5"), (96, "none"), (64, "none")):
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
    """Where each step ends, 4 across."""
    tw, th, cols = 480, 270, 4
    rows = (len(ends) + cols - 1) // cols
    out = Image.new("RGB", (tw * cols, th * rows), "white")
    for i, img in enumerate(ends):
        out.paste(img.resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
    out.save(path, optimize=True)
    print(f"{path.name}: {len(ends)} stills")


def run(stills_only: bool) -> None:
    all_steps = steps()
    fr = Frames(all_steps)
    ends: list[Image.Image] = []
    chapters: list[tuple[int, str]] = []
    gif_frames: list[np.ndarray] = []
    out = RENDERS / "lens_rings.mp4"
    tmp = out.with_suffix(".tmp.mp4")
    ff = None
    if not stills_only:
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                               "-crf", "20", "-pix_fmt", "yuv420p", "-g", str(FPS), "-movflags", "+faststart",
                               str(tmp)], stdin=subprocess.PIPE)
    n = 0
    for k, st in enumerate(all_steps):
        start = n
        chapters.append((start, f"{st.number}. {st.short}"))
        panel = fr.side_panel(st)
        frames = round(st.motion * FPS)
        if not stills_only:
            for i in range(1, frames + 1):
                u = i / frames
                ff.stdin.write(fr.frame(st.state(u), st, u, panel).tobytes())
                n += 1
        img = fr.frame(st.state(1.0), st, 1.0, panel)
        ends.append(img)
        hold = max(HOLD_S * FPS, CHAPTER_S * FPS - (n - start)) + 3 * FPS * (k == len(all_steps) - 1)
        if not stills_only:
            data = img.tobytes()
            for _ in range(hold):
                ff.stdin.write(data)
            n += hold
            # The GIF: the same moves at 10 fps, shorter holds.
            gm = round(st.motion * 0.7 * GIF_FPS)
            for i in range(1, gm + 1):
                u = i / gm
                g = fr.frame(st.state(u), st, u, panel).resize((GIF_W, GIF_H), Image.LANCZOS)
                gif_frames.append(np.asarray(g))
            g = np.asarray(img.resize((GIF_W, GIF_H), Image.LANCZOS))
            gif_frames += [g] * round(3.0 * GIF_FPS)

    if not stills_only:
        ff.stdin.close()
        ff.wait()
        meta = Path(tempfile.mkstemp(suffix=".txt")[1])
        lines = [";FFMETADATA1", "title=OT-2 lid camera: setting the zoom, iris and focus rings"]
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
        (EXPORTS / "lens_rings_chapters.txt").write_text(text + "\n")
        print(f"{out.name}: {n} frames, {n / FPS:.1f} s, {out.stat().st_size / 1e6:.1f} MB")
        print(text)
        write_gif(gif_frames, RENDERS / "lens_rings.gif")

    sheet(ends, RENDERS / "lens_rings_sheet.png")
    if stills_only:
        d = Path("/tmp/lens_video_stills")
        d.mkdir(exist_ok=True)
        for k, img in enumerate(ends):
            img.save(d / f"{k}.png")
        print("stills in", d)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stills", action="store_true", help="render only the frame each step ends on")
    run(ap.parse_args().stills)
