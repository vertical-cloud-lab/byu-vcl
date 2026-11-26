"""One look for every segment: canvas, fonts, colours and the small drawing helpers the segments share.

Colours (one per campaign and one per facility, the same everywhere in the video): FLAIME (Al) is blue and ONR (Cu)
orange, slots 1 and 2 of the dataviz skill's validated dark-mode palette; a campaign's own colour is always the
automated lab (PR 318's vertical lab), and the conventional baseline (the proposals' partners and core facilities) is
always grey and dashed. The state-of-the-art target is a white dotted line. Text is never drawn in a series colour.
"""
from __future__ import annotations

import functools
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = (int(v) for v in os.environ.get("TWIN_VIDEO_SIZE", "1920x1080").split("x"))
S = W / 1920.0                      # every size below is written for 1920 x 1080 and scaled by S
FPS = 30

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def hexrgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


BG = (13, 16, 21)                   # full-screen cards and the DAG
SURF = (25, 25, 25)                 # the dataviz skill's dark chart surface (#191919)
PANEL_A = 0.80                      # opacity of an overlay panel over footage
INK = hexrgb("#efefef")             # primary text
INK2 = hexrgb("#9c9c9c")            # secondary text
INK3 = (110, 112, 116)              # tertiary (axis ticks)
GRID = (52, 55, 60)
RULE = (78, 82, 88)

CAMP = {"flaime_al": hexrgb("#338ced"), "onr_cu": hexrgb("#e76624")}
CAMP_NAME = {"flaime_al": "FLAIME", "onr_cu": "ONR"}
CAMP_LONG = {"flaime_al": "FLAIME: Al alloys for laser powder bed fusion",
             "onr_cu": "ONR: Cu alloys for blown-powder DED"}
CAMP_SHORT = {"flaime_al": "Al, LPBF", "onr_cu": "Cu, DED"}
BASE = hexrgb("#9c9c9c")            # the conventional baseline, dashed
TARGET = hexrgb("#efefef")          # state of the art, dotted
GOOD = hexrgb("#0aac23")            # status: running / on (with a label, never alone)
WARN = hexrgb("#fbb315")            # status: waiting / outside


@functools.lru_cache(maxsize=256)
def font(size: float, bold: bool = False, cond: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSansMono" if mono else ("DejaVuSansCondensed" if cond else "DejaVuSans")
    if bold:
        name += "-Bold"
    return ImageFont.truetype(f"{FONT_DIR}/{name}.ttf", max(6, int(round(size * S))))


def px(v: float) -> int:
    return int(round(v * S))


def ease(u: float) -> float:
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def ease_out(u: float) -> float:
    u = min(1.0, max(0.0, u))
    return 1 - (1 - u) ** 3


def ramp(t: float, t0: float, t1: float) -> float:
    """0 before t0, 1 after t1, eased between."""
    if t1 <= t0:
        return 1.0 if t >= t0 else 0.0
    return ease((t - t0) / (t1 - t0))


def window(t: float, t0: float, t1: float, fade: float = 0.5) -> float:
    """Visible between t0 and t1, faded in and out over `fade` seconds."""
    return min(ramp(t, t0, t0 + fade), 1.0 - ramp(t, t1 - fade, t1))


def mix(a, b, u: float) -> tuple:
    return tuple(int(round(x + (y - x) * u)) for x, y in zip(a, b))


def text_w(f, s: str) -> int:
    return int(math.ceil(f.getlength(s)))


def wrap(text: str, f, width: int) -> list:
    out = []
    for para in str(text).split("\n"):
        line = ""
        for word in para.split(" "):
            cand = (line + " " + word).strip()
            if line and f.getlength(cand) > width:
                out.append(line)
                line = word
            else:
                line = cand
        out.append(line)
    return out


def rounded(size, radius, fill, alpha=1.0, outline=None, width=1) -> Image.Image:
    """An RGBA rounded rectangle (a panel)."""
    w, h = int(size[0]), int(size[1])
    im = Image.new("RGBA", (max(1, w), max(1, h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    a = int(round(255 * alpha))
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=int(radius), fill=tuple(fill[:3]) + (a,),
                        outline=None if outline is None else tuple(outline[:3]) + (255,), width=width)
    return im


def paste(base: np.ndarray, over, x: int, y: int, alpha: float = 1.0):
    """Alpha-composite an RGBA image (PIL or HxWx4 uint8 array) onto an HxWx3 uint8 frame in place, clipped."""
    if alpha <= 0.003 or over is None:
        return base
    o = np.asarray(over) if not isinstance(over, np.ndarray) else over
    h, w = o.shape[:2]
    H_, W_ = base.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W_, x + w), min(H_, y + h)
    if x1 <= x0 or y1 <= y0:
        return base
    src = o[y0 - y:y1 - y, x0 - x:x1 - x]
    dst = base[y0:y1, x0:x1]
    if src.shape[2] == 3:
        if alpha >= 0.997:
            dst[:] = src
        else:
            a = np.uint16(round(alpha * 256))
            dst[:] = ((src.astype(np.uint16) * a + dst.astype(np.uint16) * (256 - a)) >> 8).astype(np.uint8)
        return base
    a = src[:, :, 3:4].astype(np.uint16)
    if alpha < 0.997:
        a = (a * np.uint16(round(alpha * 256))) >> 8
    dst[:] = ((src[:, :, :3].astype(np.uint16) * a + dst.astype(np.uint16) * (255 - a)) // 255).astype(np.uint8)
    return base


def dim(base: np.ndarray, k: float, box=None):
    """Darken a frame (or a box of it) by factor k in place: k=0.5 halves it."""
    if box is None:
        base[:] = (base.astype(np.uint16) * np.uint16(int(k * 256)) >> 8).astype(np.uint8)
    else:
        x0, y0, x1, y1 = box
        sub = base[y0:y1, x0:x1]
        sub[:] = (sub.astype(np.uint16) * np.uint16(int(k * 256)) >> 8).astype(np.uint8)
    return base


def blank(color=BG) -> np.ndarray:
    a = np.empty((H, W, 3), np.uint8)
    a[:] = color
    return a


def layer(w=None, h=None):
    """A transparent RGBA layer and its drawer."""
    im = Image.new("RGBA", (w or W, h or H), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def shadow_text(d: ImageDraw.ImageDraw, xy, s: str, f, fill=INK, anchor="la", sw=None):
    """Text with a soft dark outline, legible over footage."""
    sw = px(2) if sw is None else sw
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0, 200))


def money(v: float) -> str:
    v = float(v)
    if abs(v) >= 1e6:
        return f"${v / 1e6:.2f}M"
    if abs(v) >= 1e4:
        return f"${v / 1e3:.0f}k"
    if abs(v) >= 1e3:
        return f"${v / 1e3:.1f}k"
    return f"${v:,.0f}"


def nice_ticks(lo: float, hi: float, n: int = 5) -> list:
    """Round tick values covering [lo, hi]."""
    span = max(hi - lo, 1e-9)
    raw = span / max(1, n)
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        step = m * mag
        if span / step <= n:
            break
    a = math.ceil(lo / step - 1e-9) * step
    out = []
    v = a
    while v <= hi + 1e-9 * step:
        out.append(round(v, 10))
        v += step
    return out


def dashed_line(d: ImageDraw.ImageDraw, pts, fill, width=2, dash=10, gap=7):
    """A polyline drawn dashed (PIL has none)."""
    carry, on = 0.0, True
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg < 1e-6:
            continue
        pos = 0.0
        while pos < seg:
            L = (dash if on else gap) - carry
            step = min(L, seg - pos)
            if on:
                u0, u1 = pos / seg, (pos + step) / seg
                d.line([(x0 + (x1 - x0) * u0, y0 + (y1 - y0) * u0), (x0 + (x1 - x0) * u1, y0 + (y1 - y0) * u1)],
                       fill=fill, width=width)
            pos += step
            if step < L:
                carry += step
            else:
                carry, on = 0.0, not on
