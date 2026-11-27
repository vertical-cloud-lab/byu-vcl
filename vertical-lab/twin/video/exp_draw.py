"""What the experiment segments share: a canvas in design units, live plots, image reveals, provenance tags, the network
strip and the segment's frame (twin/video/exp_draw.py).

Every coordinate and size a segment gives is in the 1920 x 1080 design; ``Canvas`` scales by style.S, so the same
segment renders at TWIN_VIDEO_SIZE=960x540 for a quick look. A segment (``Segment``) is one experiment shown beside
the data it makes: ``frame(t)`` for 0 <= t <= DURATION, ``captions`` [(t0, t1, text)], ``marks`` {name: t} for the
narration to anchor on, and ``sources`` (what on screen is simulated, computed, illustrative or real).

Provenance is said the same way everywhere (``tag``): a small chip with a coloured dot and words.

    sim      simulated by the twin for this alloy (its truth and its instrument models)
    calc     computed with an open CALPHAD tool on an open database
    illus    an illustrative schematic: drawn to explain, not computed for this alloy
    real     real footage or a real photograph from the lab
    render   the lab's 3-D model, rendered (PR 318): the station as designed, not a recording
"""
from __future__ import annotations

import math
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from . import data as D
from . import style as St
from .style import BG, CAMP, GRID, INK, INK2, INK3, RULE, H, W, font, mix, px

S = St.S
CARD_FILL = (24, 28, 35)
CARD_EDGE = (66, 70, 78)
PLOT_FILL = (18, 21, 27)
KIND = {  # provenance: (dot colour, lead word)
    "sim": ((92, 158, 255), "simulated"),
    "calc": ((186, 148, 255), "computed"),
    "illus": (St.WARN, "illustrative"),
    "real": (St.GOOD, "real"),
    "render": ((150, 156, 168), "3-D model"),
}
HOT = (255, 196, 92)            # the laser, the melt, a scan line: one accent for "this is happening now"
SOLID = (148, 176, 214)         # solid metal in the schematics
LIQUID = (255, 150, 60)         # liquid metal in the schematics


# ------------------------------------------------------------------------------------------------- colour maps
def _lut(stops) -> np.ndarray:
    xs = np.array([s[0] for s in stops])
    cs = np.array([s[1] for s in stops], float)
    u = np.linspace(0, 1, 256)
    return np.stack([np.interp(u, xs, cs[:, i]) for i in range(3)], 1).astype(np.uint8)


lut = _lut                       # public name: other modules make their own tables
LUT_HEAT = _lut([(0.0, (14, 12, 28)), (0.18, (70, 16, 92)), (0.38, (158, 36, 98)), (0.58, (226, 78, 52)),
                 (0.78, (250, 150, 34)), (0.92, (252, 224, 96)), (1.0, (255, 252, 226))])
LUT_GRAY = _lut([(0.0, (6, 7, 9)), (1.0, (238, 240, 244))])
LUT_BLUE = _lut([(0.0, (10, 14, 24)), (0.5, (38, 96, 190)), (1.0, (196, 226, 255))])


def colourize(a: np.ndarray, lo: float, hi: float, lut: np.ndarray = LUT_GRAY, gamma: float = 1.0) -> np.ndarray:
    """A 2-D array as RGB through a 256-entry colour table."""
    u = np.clip((np.asarray(a, float) - lo) / max(hi - lo, 1e-12), 0.0, 1.0)
    if gamma != 1.0:
        u = u ** gamma
    return lut[(u * 255).astype(np.uint8)]


def stretch(a: np.ndarray, p_lo: float = 1.0, p_hi: float = 99.7) -> tuple:
    """Display limits of a micrograph: percentiles, as an operator sets brightness and contrast."""
    return float(np.percentile(a, p_lo)), float(np.percentile(a, p_hi))


# ------------------------------------------------------------------------------------------------- the canvas
class Canvas:
    """A frame being drawn, in design units."""

    def __init__(self, base=None):
        if base is None:
            self.im = Image.new("RGB", (W, H), BG)
        elif isinstance(base, Image.Image):
            self.im = base.copy()
        else:
            self.im = Image.fromarray(base)
        self.d = ImageDraw.Draw(self.im, "RGBA")

    # ---- primitives
    @staticmethod
    def _c(fill, a=1.0):
        if fill is None:
            return None
        f = tuple(int(v) for v in fill)
        al = f[3] if len(f) > 3 else 255
        return f[:3] + (int(round(al * max(0.0, min(1.0, a)))),)

    def text(self, x, y, s, size=24, bold=False, fill=INK, anchor="la", cond=False, mono=False, a=1.0, stroke=0):
        """Text at (x, y), faded by ``a``. A faded text is drawn through a mask of its glyphs: on this Pillow an RGBA
        fill on an RGB image blends for shapes but comes out opaque for text, so a fade would pop."""
        if a <= 0.004 or not s:
            return
        s = str(s)
        f = font(size, bold=bold, cond=cond, mono=mono)
        col = tuple(int(v) for v in fill[:3])
        al = (fill[3] / 255.0 if len(fill) > 3 else 1.0) * max(0.0, min(1.0, a))
        sw = px(stroke) if stroke else 0
        X, Y = x * S, y * S
        if al >= 0.996:
            if sw:
                self.d.text((X, Y), s, font=f, fill=col + (255,), anchor=anchor, stroke_width=sw,
                            stroke_fill=(0, 0, 0, 255))
            else:
                self.d.text((X, Y), s, font=f, fill=col + (255,), anchor=anchor)
            return
        x0, y0, x1, y1 = self.d.textbbox((X, Y), s, font=f, anchor=anchor, stroke_width=sw)
        x0, y0 = max(0, int(x0) - 2), max(0, int(y0) - 2)
        x1, y1 = min(self.im.width, int(x1) + 3), min(self.im.height, int(y1) + 3)
        if x1 <= x0 or y1 <= y0:
            return
        if sw:                                              # the dark outline first, at the same fade
            m = Image.new("L", (x1 - x0, y1 - y0), 0)
            ImageDraw.Draw(m).text((X - x0, Y - y0), s, font=f, fill=int(round(255 * al)), anchor=anchor,
                                   stroke_width=sw, stroke_fill=int(round(255 * al)))
            self.im.paste(Image.new("RGB", m.size, (0, 0, 0)), (x0, y0), m)
        m = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(m).text((X - x0, Y - y0), s, font=f, fill=int(round(255 * al)), anchor=anchor)
        self.im.paste(Image.new("RGB", m.size, col), (x0, y0), m)

    def text_w(self, s, size=24, bold=False, cond=False, mono=False) -> float:
        return St.text_w(font(size, bold=bold, cond=cond, mono=mono), str(s)) / S

    def wrap(self, s, size, width, bold=False, cond=False) -> list:
        return St.wrap(s, font(size, bold=bold, cond=cond), int(width * S))

    def para(self, x, y, s, size=24, width=800, fill=INK, lh=1.36, bold=False, cond=False, a=1.0, anchor="la",
             max_lines=None) -> float:
        """Wrapped text; returns the y under the last line."""
        lines = self.wrap(s, size, width, bold, cond)
        if max_lines:
            lines = lines[:max_lines]
        for i, ln in enumerate(lines):
            self.text(x, y + i * size * lh, ln, size, bold=bold, fill=fill, cond=cond, a=a, anchor=anchor)
        return y + len(lines) * size * lh

    def rect(self, box, fill=None, outline=None, width=1, radius=0, a=1.0):
        if a <= 0.004:
            return
        x0, y0, x1, y1 = (v * S for v in box)
        if x1 < x0 or y1 < y0:
            return
        kw = dict(fill=self._c(fill, a), outline=self._c(outline, a), width=max(1, px(width)))
        if radius:
            self.d.rounded_rectangle((x0, y0, x1, y1), radius=px(radius), **kw)
        else:
            self.d.rectangle((x0, y0, x1, y1), **kw)

    def line(self, pts, fill, width=2, a=1.0, closed=False):
        if a <= 0.004 or len(pts) < 2:
            return
        p = [(x * S, y * S) for x, y in pts]
        if closed:
            p.append(p[0])
        self.d.line(p, fill=self._c(fill, a), width=max(1, px(width)), joint="curve")

    def dashed(self, pts, fill, width=2, dash=10, gap=7, a=1.0):
        if a <= 0.004 or len(pts) < 2:
            return
        St.dashed_line(self.d, [(x * S, y * S) for x, y in pts], self._c(fill, a), width=max(1, px(width)),
                       dash=max(2, px(dash)), gap=max(2, px(gap)))

    def circle(self, x, y, r, fill=None, outline=None, width=1, a=1.0):
        if a <= 0.004:
            return
        self.d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=self._c(fill, a),
                       outline=self._c(outline, a), width=max(1, px(width)))

    def poly(self, pts, fill=None, outline=None, width=1, a=1.0):
        if a <= 0.004 or len(pts) < 3:
            return
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=self._c(fill, a), outline=self._c(outline, a),
                       width=max(1, px(width)))

    def arrow(self, p0, p1, fill, width=3, head=12, a=1.0):
        self.line([p0, p1], fill, width, a)
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        b = math.radians(27)
        self.poly([p1, (p1[0] - head * math.cos(ang - b), p1[1] - head * math.sin(ang - b)),
                   (p1[0] - head * math.cos(ang + b), p1[1] - head * math.sin(ang + b))], fill=fill, a=a)

    def aaline(self, pts, fill, width=3.0, a=1.0, k=3):
        """A smooth polyline: drawn k times larger on its own layer and reduced."""
        if a <= 0.004 or len(pts) < 2:
            return
        p = np.asarray(pts, float) * S
        pad = width * S + 3
        x0, y0 = np.floor(p.min(0) - pad).astype(int)
        x1, y1 = np.ceil(p.max(0) + pad).astype(int)
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
        if x1 <= x0 or y1 <= y0:
            return
        lay = Image.new("L", ((x1 - x0) * k, (y1 - y0) * k), 0)
        dl = ImageDraw.Draw(lay)
        q = [((x - x0) * k, (y - y0) * k) for x, y in p]
        wd = max(1, int(round(width * S * k)))
        dl.line(q, fill=255, width=wd, joint="curve")
        r = wd / 2.0
        for x, y in (q[0], q[-1]):
            dl.ellipse((x - r, y - r, x + r, y + r), fill=255)
        m = lay.resize((x1 - x0, y1 - y0), Image.LANCZOS)
        if a < 0.996:
            m = m.point(lambda v, a=a: int(v * a))
        self.im.paste(Image.new("RGB", m.size, tuple(fill[:3])), (x0, y0), m)

    def paste(self, img, x, y, w=None, h=None, a=1.0, resample=Image.BILINEAR):
        """An image (numpy or PIL, RGB or RGBA) with its top left at (x, y); (w, h) in design units resizes it."""
        if a <= 0.004 or img is None:
            return
        im = img if isinstance(img, Image.Image) else Image.fromarray(np.ascontiguousarray(img))
        if w is not None:
            size = (max(1, int(round(w * S))), max(1, int(round(h * S))))
            if im.size != size:
                im = im.resize(size, resample)
        X, Y = int(round(x * S)), int(round(y * S))
        if im.mode == "RGBA":
            if a < 0.996:
                im = im.copy()
                im.putalpha(im.getchannel("A").point(lambda v, a=a: int(v * a)))
            self.im.paste(im, (X, Y), im)
        elif a < 0.996:
            self.im.paste(im, (X, Y), Image.new("L", im.size, int(255 * a)))
        else:
            self.im.paste(im, (X, Y))

    def frame(self) -> np.ndarray:
        return np.asarray(self.im).copy()

    # ---- compounds
    def card(self, box, title: str = "", fill=CARD_FILL, edge=CARD_EDGE, a=1.0, radius=14, title_size=22):
        self.rect(box, fill=fill, outline=edge, width=2, radius=radius, a=a)
        if title:
            self.text(box[0] + 20, box[1] + 14, title, title_size, bold=True, fill=INK, a=a)

    def tag(self, x, y, kind: str, words: str, a=1.0, size=17, anchor="l") -> float:
        """A provenance chip; returns its width. anchor 'l': (x, y) is its top left; 'r': its top right."""
        col, lead = KIND[kind]
        s1, s2 = lead, (": " + words if words else "")
        w = self.text_w(s1, size, bold=True, cond=True) + self.text_w(s2, size, cond=True) + 38
        h = size * 1.75
        if anchor == "r":
            x -= w
        self.rect((x, y, x + w, y + h), fill=(12, 14, 18, 235), outline=(70, 74, 84), width=1, radius=h / 2, a=a)
        self.circle(x + 15, y + h / 2, 5.5, fill=col, a=a)
        self.text(x + 27, y + h / 2, s1, size, bold=True, cond=True, fill=INK, anchor="lm", a=a)
        self.text(x + 27 + self.text_w(s1, size, bold=True, cond=True), y + h / 2, s2, size, cond=True, fill=INK2,
                  anchor="lm", a=a)
        return w

    def value(self, x, y, label: str, val: str, unit: str = "", a=1.0, size=30, label_size=17, w=None,
              fill=INK) -> None:
        """A read-out: a small label over a number with its unit."""
        self.text(x, y, label, label_size, cond=True, fill=INK2, a=a)
        self.text(x, y + label_size * 1.45, val, size, bold=True, fill=fill, a=a)
        if unit:
            self.text(x + self.text_w(val, size, bold=True) + 7, y + label_size * 1.45 + size * 0.34, unit,
                      size * 0.58, fill=INK2, a=a)


# ------------------------------------------------------------------------------------------------- plots
class Axes:
    """A plot area in design units. box = (x0, y0, x1, y1) of the data rectangle."""

    def __init__(self, box, xlim, ylim, xlabel="", ylabel="", xticks=None, yticks=None, xfmt="{:g}", yfmt="{:g}",
                 logx=False, logy=False):
        self.box, self.xlim, self.ylim = tuple(box), tuple(xlim), tuple(ylim)
        self.xlabel, self.ylabel, self.xfmt, self.yfmt = xlabel, ylabel, xfmt, yfmt
        self.logx, self.logy = logx, logy
        self.xticks = xticks if xticks is not None else St.nice_ticks(min(xlim), max(xlim), 6)
        self.yticks = yticks if yticks is not None else St.nice_ticks(min(ylim), max(ylim), 5)

    def _u(self, v, lim, log):
        v = np.asarray(v, float)
        if log:
            return (np.log10(np.maximum(v, 1e-300)) - math.log10(lim[0])) / (math.log10(lim[1]) - math.log10(lim[0]))
        return (v - lim[0]) / (lim[1] - lim[0])

    def X(self, v):
        x0, _, x1, _ = self.box
        return x0 + self._u(v, self.xlim, self.logx) * (x1 - x0)

    def Y(self, v):
        _, y0, _, y1 = self.box
        return y1 - self._u(v, self.ylim, self.logy) * (y1 - y0)

    def draw(self, cv: Canvas, a=1.0, grid=True, size=17, fill=PLOT_FILL, frame=True):
        x0, y0, x1, y1 = self.box
        if fill is not None:
            cv.rect((x0, y0, x1, y1), fill=fill, a=a)
        for v in self.xticks:
            X = float(self.X(v))
            if x0 - 0.5 <= X <= x1 + 0.5:
                if grid:
                    cv.line([(X, y0), (X, y1)], GRID, 1, a)
                cv.line([(X, y1), (X, y1 + 6)], RULE, 2, a)
                cv.text(X, y1 + 11, self.xfmt.format(v), size, fill=INK2, anchor="ma", a=a)
        for v in self.yticks:
            Y = float(self.Y(v))
            if y0 - 0.5 <= Y <= y1 + 0.5:
                if grid:
                    cv.line([(x0, Y), (x1, Y)], GRID, 1, a)
                cv.line([(x0 - 6, Y), (x0, Y)], RULE, 2, a)
                cv.text(x0 - 11, Y, self.yfmt.format(v), size, fill=INK2, anchor="rm", a=a)
        if frame:
            cv.line([(x0, y0), (x0, y1), (x1, y1)], RULE, 2, a)
        if self.xlabel:
            cv.text((x0 + x1) / 2, y1 + 11 + size * 1.5, self.xlabel, size + 2, fill=INK, anchor="ma", a=a)
        if self.ylabel:
            self._ylabel(cv, a, size + 2)

    def _ylabel(self, cv, a, size):
        f = font(size)
        w, h = St.text_w(f, self.ylabel) + 4, int(size * S * 1.5) + 4
        lab = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(lab).text((2, h / 2), self.ylabel, font=f, fill=INK + (int(255 * a),), anchor="lm")
        lab = lab.rotate(90, expand=True)
        x0, y0, _, y1 = self.box
        wid = max(St.text_w(font(17), self.yfmt.format(v)) for v in self.yticks) / S if self.yticks else 30
        cv.im.paste(lab, (int((x0 - 22 - wid) * S - lab.width), int((y0 + y1) / 2 * S - lab.height / 2)), lab)

    def pts(self, xs, ys) -> np.ndarray:
        return np.stack([self.X(xs), self.Y(ys)], 1)

    def line(self, cv: Canvas, xs, ys, fill, width=3.5, upto=1.0, a=1.0, dashed=False, clip=True):
        """The curve up to a share ``upto`` of its points (the last piece interpolated), so it can be drawn live.
        Returns the pen's position in design units (or None)."""
        xs, ys = np.asarray(xs, float), np.asarray(ys, float)
        n = len(xs)
        if n < 2 or upto <= 0:
            return None
        f = min(1.0, upto) * (n - 1)
        i = int(math.floor(f))
        X, Y = self.X(xs[:i + 1]), self.Y(ys[:i + 1])
        if i < n - 1:
            u = f - i
            X = np.append(X, self.X(xs[i] + (xs[i + 1] - xs[i]) * u) if not self.logx else
                          self.X(xs[i] * (xs[i + 1] / xs[i]) ** u))
            Y = np.append(Y, self.Y(ys[i] + (ys[i + 1] - ys[i]) * u))
        if clip:
            x0, y0, x1, y1 = self.box
            X, Y = np.clip(X, x0, x1), np.clip(Y, y0, y1)
        p = thin(np.stack([X, Y], 1))
        if len(p) < 2:
            return tuple(p[-1]) if len(p) else None
        if dashed:
            cv.dashed([tuple(q) for q in p], fill, width, a=a)
        else:
            cv.aaline(p, fill, width, a)
        return float(p[-1][0]), float(p[-1][1])

    def dot(self, cv: Canvas, x, y, fill, r=7, ring=INK, a=1.0):
        X, Y = float(self.X(x)), float(self.Y(y))
        cv.circle(X, Y, r + 2.5, fill=ring, a=a)
        cv.circle(X, Y, r, fill=fill, a=a)
        return X, Y

    def hline(self, cv, y, fill=INK2, a=1.0, label="", size=17, x_from=None, x_to=None, side="r"):
        x0, _, x1, _ = self.box
        xa = x0 if x_from is None else float(self.X(x_from))
        xb = x1 if x_to is None else float(self.X(x_to))
        Y = float(self.Y(y))
        cv.dashed([(xa, Y), (xb, Y)], fill, 2, 9, 6, a)
        if label:
            cv.text(xb - 8 if side == "r" else xa + 8, Y - 6, label, size, fill=INK, anchor="rs" if side == "r"
                    else "ls", a=a)

    def vline(self, cv, x, fill=INK2, a=1.0, label="", size=17, y_from=None, y_to=None, side="t"):
        _, y0, _, y1 = self.box
        ya = y1 if y_from is None else float(self.Y(y_from))
        yb = y0 if y_to is None else float(self.Y(y_to))
        X = float(self.X(x))
        cv.dashed([(X, ya), (X, yb)], fill, 2, 9, 6, a)
        if label:
            cv.text(X + 8, yb + 6 if side == "t" else ya - 6, label, size, fill=INK, anchor="la" if side == "t"
                    else "ls", a=a)


def thin(p: np.ndarray, tol: float = 0.35) -> np.ndarray:
    """Drop points closer than tol design units to the one kept before (long records: thousands of points)."""
    if len(p) < 3:
        return p
    keep = [0]
    last = p[0]
    for i in range(1, len(p) - 1):
        if abs(p[i][0] - last[0]) + abs(p[i][1] - last[1]) >= tol:
            keep.append(i)
            last = p[i]
    keep.append(len(p) - 1)
    return p[keep]


# ------------------------------------------------------------------------------------------------- images
def to_image(rgb: np.ndarray, w: float, h: float, resample=Image.LANCZOS) -> Image.Image:
    """An RGB array as a PIL image of w x h design units."""
    return Image.fromarray(np.ascontiguousarray(rgb)).resize((max(1, int(round(w * S))), max(1, int(round(h * S)))),
                                                             resample)


def raster(cv: Canvas, im: Image.Image, x: float, y: float, u: float, a: float = 1.0, line=HOT, ghost: float = 0.0,
           label_rows: bool = False):
    """An image appearing as a beam rasters it: the rows above the scan line are in, the rest dark (or a faint
    ``ghost`` of it). u in 0..1; at 1 the scan line is gone."""
    if a <= 0.004:
        return
    w, h = im.size
    X, Y = int(round(x * S)), int(round(y * S))
    u = max(0.0, min(1.0, u))
    rows = int(round(h * u))
    if ghost > 0 and rows < h:
        g = Image.eval(im, lambda v, k=ghost: int(v * k))
        cv.im.paste(g, (X, Y))
    elif rows < h:
        cv.d.rectangle((X, Y, X + w - 1, Y + h - 1), fill=(8, 9, 12, 255))
    if rows > 0:
        cv.im.paste(im.crop((0, 0, w, rows)), (X, Y))
    if 0 < rows < h:
        cv.d.rectangle((X, Y + rows - max(1, px(2)), X + w - 1, Y + rows), fill=tuple(line) + (255,))
        cv.d.rectangle((X, Y + rows, X + w - 1, Y + rows + px(10)), fill=tuple(line) + (46,))


def framed(cv: Canvas, box, label: str = "", a=1.0, edge=CARD_EDGE, size=17):
    """A thin frame round an image, with a label on a dark strip at its top left."""
    x0, y0, x1, y1 = box
    cv.rect((x0 - 1, y0 - 1, x1 + 1, y1 + 1), outline=edge, width=2, a=a)
    if label:
        w = cv.text_w(label, size, bold=True, cond=True) + 18
        cv.rect((x0, y0, x0 + w, y0 + size * 1.7), fill=(10, 12, 16, 225), a=a)
        cv.text(x0 + 9, y0 + size * 0.85, label, size, bold=True, cond=True, fill=INK, anchor="lm", a=a)


def scale_bar(cv: Canvas, x1: float, y1: float, um_per_unit: float, a=1.0, want=(10, 20, 50, 100, 200, 500, 1000)):
    """A micron bar ending at (x1, y1), its length chosen from ``want`` to be near 120 design units."""
    um = min(want, key=lambda v: abs(v / um_per_unit - 120))
    L = um / um_per_unit
    cv.rect((x1 - L - 12, y1 - 38, x1 + 6, y1 + 4), fill=(8, 9, 12, 215), a=a)
    cv.rect((x1 - L - 3, y1 - 8, x1 - 3, y1 - 3), fill=INK, a=a)
    cv.text(x1 - 3 - L / 2, y1 - 12, f"{um:g} µm" if um < 1000 else f"{um / 1000:g} mm", 16, bold=True, fill=INK,
            anchor="ms", a=a)


# ------------------------------------------------------------------------------------------------- footage
class Footage:
    """Frames of [t0, t1] of a video file, cropped (x, y, w, h in its pixels) and scaled to (w, h) design units,
    read in order from one ffmpeg process and looped (as assets.Reader, for a file that is not one of its clips)."""

    def __init__(self, path, t0: float, t1: float, w: float, h: float, crop=None, speed: float = 1.0, fps=30.0):
        self.path, self.t0, self.t1, self.speed, self.fps = Path(path), t0, t1, speed, fps
        self.w, self.h = max(2, int(round(w * S))), max(2, int(round(h * S)))
        self.crop = crop
        self.p, self.pos, self.last = None, None, None
        self.span = max(0.3, (t1 - t0) / speed)

    def _start(self, k: int):
        self.close()
        off = (k / self.fps) * self.speed
        vf = ""
        if self.crop:
            x, y, w, h = self.crop
            vf = f"crop={w}:{h}:{x}:{y},"
        vf += f"setpts=(PTS-STARTPTS)/{self.speed},fps={self.fps},scale={self.w}:{self.h}:flags=bicubic"
        self.p = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-threads", "1", "-ss", f"{self.t0 + off:.3f}", "-i", str(self.path), "-t",
             f"{max(0.2, self.t1 - self.t0 - off):.3f}", "-an", "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=self.w * self.h * 3 * 2)
        self.pos = k

    def frame(self, t: float) -> np.ndarray:
        k = int((max(0.0, t) % self.span) * self.fps + 1e-6)
        if self.last is not None and self.pos is not None and k == self.pos - 1:
            return self.last                            # the same frame again (a held last frame): no new seek
        if self.p is None or self.pos is None or k < self.pos or k > self.pos + 90:
            self._start(k)
        n = self.w * self.h * 3
        while self.pos <= k:
            buf = self.p.stdout.read(n) if self.p else b""
            if len(buf) < n:
                if self.last is None:
                    self.last = np.zeros((self.h, self.w, 3), np.uint8)
                self.pos = k + 1
                break
            self.last = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 3)
            self.pos += 1
        return self.last

    def close(self):
        if self.p is not None:
            try:
                self.p.stdout.close()
                self.p.kill()
                self.p.wait(timeout=2)
            except Exception:                           # noqa: BLE001
                pass
        self.p = None


def lab_clip(clip: str, t0: float, t1: float, w: float, h: float, speed: float = 1.0):
    """A shot of one of PR 318's renders (assets.SHOTS seconds), cropped clear of its title and caption band."""
    from . import assets as A
    return A.Reader(clip, t0, t1, max(2, int(round(w * S))), max(2, int(round(h * S))), speed)


# ------------------------------------------------------------------------------------------------- the network strip
SHORT = {"composition": "composition", "calphad": "CALPHAD", "powder": "atomize", "print": "print", "section": "section",
         "pip": "PIP", "test": "tensile", "utility": "utility", "ded_small": "DED", "screen": "screen",
         "tensile": "tensile", "immersion": "immersion"}
STRIP_W = 1010       # the network strip's width in the header


@lru_cache(maxsize=64)
def network_strip(campaign: str, lit: tuple = (), width: int = 1010, done: tuple = ()) -> Image.Image:
    """The campaign's function network as one row of small tiles (pictogram and short name), the node(s) the
    segment is about lit in the campaign's colour, nodes already shown ticked off in a quieter tone."""
    from .dag_anim import ICON_OF, pictogram
    nodes = D.network(campaign)["nodes"]
    n = len(nodes)
    col = CAMP[campaign]
    hh = 76
    im = Image.new("RGBA", (int(width * S), int(hh * S)), (0, 0, 0, 0))
    cv = Canvas(Image.new("RGB", im.size, BG))
    gap = 12.0
    tw = (width - (n - 1) * gap) / n
    base_el = "Al" if campaign == "flaime_al" else "Cu"
    for i, nd in enumerate(nodes):
        x = i * (tw + gap)
        on, was = nd["key"] in lit, nd["key"] in done
        fill = mix(CARD_FILL, col, 0.30) if on else CARD_FILL
        edge = col if on else (mix(CARD_EDGE, col, 0.45) if was else CARD_EDGE)
        cv.rect((x, 2, x + tw, hh - 2), fill=fill, outline=edge, width=3 if on else 2, radius=10)
        ink = INK if on else (INK2 if was else INK3)
        pic = pictogram(ICON_OF.get(nd["key"], "dot"), int(30 * S), ink, base_el)
        cv.im.paste(pic, (int((x + tw / 2) * S - pic.width / 2), int(9 * S)), pic)
        name = SHORT.get(nd["key"], nd["key"])
        size = 15
        while size > 11 and cv.text_w(name, size, cond=True, bold=on) > tw - 8:
            size -= 1
        cv.text(x + tw / 2, hh - 12, name, size, bold=on, cond=True, fill=ink, anchor="ms")
        if i < n - 1:
            cv.line([(x + tw + 1, hh / 2), (x + tw + gap - 1, hh / 2)], RULE, 2)
    return cv.im


# ------------------------------------------------------------------------------------------------- a segment
CHAPTER = "The function networks: what each step is"
TOP = 150            # the first y a segment draws at
BOTTOM = 936         # the last (the caption band is below)
MARGIN = 56


class Segment:
    """One experiment beside its data. Subclasses set key, title, campaign, nodes (the network nodes it is), DURATION,
    captions [(t0, t1, text)] and marks {name: t}, and draw in ``draw(cv, t)`` between y = TOP and y = BOTTOM."""
    key = "segment"
    title = ""
    campaign = "flaime_al"
    nodes: tuple = ()
    done: tuple = ()
    DURATION = 20.0
    FADE = 0.45

    def __init__(self):
        self.captions: list = []
        self.marks: dict = {}
        self.sources: list = []       # [(kind, words)]: what the segment shows and where it comes from (the record)
        self._bg = None

    # the header (chapter, title, the network strip) is the same for every frame of a segment
    def _static(self) -> np.ndarray:
        if self._bg is None:
            cv = Canvas()
            col = CAMP[self.campaign]
            sw = STRIP_W
            x0 = W / S - MARGIN - sw
            xl = x0 - 150                                   # the campaign's name, left of its strip
            cv.text(MARGIN, 26, CHAPTER, 19, fill=INK2, cond=True)
            size = 38
            while size > 24 and cv.text_w(self.title, size, bold=True) > xl - 26 - MARGIN:
                size -= 1
            cv.text(MARGIN, 54 + (38 - size) * 0.6, self.title, size, bold=True, fill=INK)
            cv.rect((xl, 40, xl + 6, 110), fill=col, radius=3)
            cv.text(xl + 16, 46, St.CAMP_NAME[self.campaign], 22, bold=True, fill=INK)
            cv.text(xl + 16, 76, "aluminium" if self.campaign == "flaime_al" else "copper", 17, fill=INK2, cond=True)
            cv.text(xl + 16, 96, "LPBF" if self.campaign == "flaime_al" else "DED", 17, fill=INK2, cond=True)
            cv.paste(network_strip(self.campaign, tuple(self.nodes), sw, tuple(self.done)), x0, 36)
            cv.line([(MARGIN, 128), (W / S - MARGIN, 128)], (40, 44, 52), 2)
            self.static_extra(cv)
            self._bg = cv.frame()
        return self._bg

    def static_extra(self, cv: Canvas):
        """What else never changes during the segment (panels' cards, axes)."""

    def caption_at(self, t: float):
        for t0, t1, s in self.captions:
            if t0 <= t < t1:
                return s, St.window(t, t0, t1, 0.4)
        return None, 0.0

    def frame(self, t: float) -> np.ndarray:
        t = max(0.0, min(float(t), self.DURATION))
        cv = Canvas(self._static())
        self.draw(cv, t)
        s, a = self.caption_at(t)
        if s:
            lines = cv.wrap(s, 28, W / S - 2 * MARGIN - 80)[:2]
            y = 1004 - (len(lines) - 1) * 19
            for i, ln in enumerate(lines):
                cv.text(W / S / 2, y + i * 38, ln, 28, fill=INK, anchor="mm", a=a)
        return cv.frame()

    def draw(self, cv: Canvas, t: float):
        raise NotImplementedError

    def close(self):
        """Release readers (ffmpeg processes)."""


def ramp(t, t0, t1):
    return St.ramp(t, t0, t1)


def lin(t, t0, t1):
    """0 before t0, 1 after t1, linear between (a pen moving at constant speed)."""
    if t1 <= t0:
        return 1.0 if t >= t0 else 0.0
    return max(0.0, min(1.0, (t - t0) / (t1 - t0)))


def fmt(v, n=0) -> str:
    """A number as the chapter writes it: fixed decimals, a thin thousands separator from 10,000."""
    s = f"{v:,.{n}f}"
    return s if abs(v) >= 10000 else s.replace(",", "")


_thin = thin                     # the names the first segments were written against
