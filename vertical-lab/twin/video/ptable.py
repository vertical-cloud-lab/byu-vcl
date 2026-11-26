"""Periodic-table heatmaps in DAL's style, drawn with PIL alone (fast enough to call every frame).

DAL's figures (``figures/dag-thumbnails/periodic-table/render_periodic_table_bounds.py`` and ``Grant_FLAIMEplots.py``
on DAL's ``consolidation-2``; copies in /tmp/dal/ptable/): element tiles with white bold symbols, matplotlib's
"twilight" colormap truncated to [0, 0.85], and for the search space each tile split into a lower-left triangle (the
lower bound) and an upper-right one (the upper bound). Here the same on the video's dark theme, with three changes,
each for legibility at 1080p over footage: the symbols carry a thin dark outline (they sit on light and dark tiles),
every coloured tile has a light edge (twilight's middle is nearly black), and the scale is the square root of wt%,
so that 0.1-0.5 wt% additions read apart from nothing. One scale per campaign everywhere in the video: Al 0-12 wt%
(DAL's), Cu 0-30 wt% (Ni's upper bound).

    bounds_figure(campaign, w, h, reveal)            the search space, full screen ("what is simulated")
    composition_panel(campaign, comp, w, h, title)   one design in flight, a semi-transparent overlay
    multiples_panel(items, w, h)                     the batch in flight at high speed, up to 6 small tables

Bounds, balance, minimum balance and rules come from twin/spaces.py (the proposals' spaces; FLAIME's per-element
bounds are DAL's alloy_element_bounds.csv "Recommended upper bound").
"""
from __future__ import annotations

import functools
import math

import numpy as np
from PIL import Image, ImageDraw

from . import style as ST

# ------------------------------------------------------------------------------------------------- the table
# element -> (row, col), 1-indexed, as DAL's Grant_FLAIMEplots.py; rows 1-6 and the lanthanides (DAL's row 9). Row 7
# and the actinides are not drawn.
PTABLE_RC = {
    "H": (1, 1), "He": (1, 18),
    "Li": (2, 1), "Be": (2, 2), "B": (2, 13), "C": (2, 14), "N": (2, 15), "O": (2, 16), "F": (2, 17), "Ne": (2, 18),
    "Na": (3, 1), "Mg": (3, 2), "Al": (3, 13), "Si": (3, 14), "P": (3, 15), "S": (3, 16), "Cl": (3, 17), "Ar": (3, 18),
    "K": (4, 1), "Ca": (4, 2), "Sc": (4, 3), "Ti": (4, 4), "V": (4, 5), "Cr": (4, 6), "Mn": (4, 7), "Fe": (4, 8),
    "Co": (4, 9), "Ni": (4, 10), "Cu": (4, 11), "Zn": (4, 12), "Ga": (4, 13), "Ge": (4, 14), "As": (4, 15),
    "Se": (4, 16), "Br": (4, 17), "Kr": (4, 18),
    "Rb": (5, 1), "Sr": (5, 2), "Y": (5, 3), "Zr": (5, 4), "Nb": (5, 5), "Mo": (5, 6), "Tc": (5, 7), "Ru": (5, 8),
    "Rh": (5, 9), "Pd": (5, 10), "Ag": (5, 11), "Cd": (5, 12), "In": (5, 13), "Sn": (5, 14), "Sb": (5, 15),
    "Te": (5, 16), "I": (5, 17), "Xe": (5, 18),
    "Cs": (6, 1), "Ba": (6, 2), "La": (6, 3), "Hf": (6, 4), "Ta": (6, 5), "W": (6, 6), "Re": (6, 7), "Os": (6, 8),
    "Ir": (6, 9), "Pt": (6, 10), "Au": (6, 11), "Hg": (6, 12), "Tl": (6, 13), "Pb": (6, 14), "Bi": (6, 15),
    "Po": (6, 16), "At": (6, 17), "Rn": (6, 18),
    "Ce": (9, 4), "Pr": (9, 5), "Nd": (9, 6), "Pm": (9, 7), "Sm": (9, 8), "Eu": (9, 9), "Gd": (9, 10),
    "Tb": (9, 11), "Dy": (9, 12), "Ho": (9, 13), "Er": (9, 14), "Tm": (9, 15), "Yb": (9, 16), "Lu": (9, 17),
}
LAN_GAP = 0.35                      # pitches between row 6 and the lanthanide row
ROWS_H = 6 + LAN_GAP + 1            # the table's height in pitches
COLS = 18
GAP = 0.08                          # gap between tiles, as a share of the pitch (DAL: 0.08)


def _cell_xy(el: str) -> tuple:
    """(column, row) of an element's top-left corner, in pitches from the table's top-left."""
    r, c = PTABLE_RC[el]
    y = (6 + LAN_GAP) if r == 9 else (r - 1)
    return c - 1, y


# ------------------------------------------------------------------------------------------- the two spaces
_FALLBACK = {   # twin/spaces.py's values, if it cannot be imported
    "flaime_al": dict(balance="Al", min_balance=85.0, k=(2, 8), bounds={
        "Mn": (0, 5.0), "Cr": (0, 3.0), "Zr": (0, 1.0), "Mg": (0, 5.0), "Si": (0, 12.0), "Cu": (0, 4.0),
        "Ti": (0, 0.5), "Fe": (0, 0.5), "Ni": (0, 0.5), "Ce": (0, 6.0), "Sc": (0, 0.8), "Li": (0, 2.0),
        "Er": (0, 0.5), "Zn": (0, 8.0), "Sn": (0, 0.1)},
        rules=["Mg + Zn + Li <= 10", "Cu + Mg <= 5", "Sc + Zr <= 1.5"]),
    "onr_cu": dict(balance="Cu", min_balance=65.0, k=(1, 6), bounds={
        "Ni": (0, 30.0), "Al": (0, 9.5), "Fe": (0, 4.5), "Mn": (0, 4.0), "Cr": (0, 0.7), "Si": (0, 0.5),
        "Nb": (0, 0.8), "Ti": (0, 0.5)},
        rules=["Cr and Nb only where Al <= 3", "Si only where Al <= 3", "Si above 0.1 only with Nb",
               "above 7 % Al, Ni >= Fe", "below 1.5 % Al, Fe <= 2.3"]),
}
VMAX = {"flaime_al": 12.0, "onr_cu": 30.0}          # top of each campaign's colour scale, wt%
TICKS = {"flaime_al": (0, 0.1, 0.5, 1, 2, 4, 8, 12), "onr_cu": (0, 0.5, 1, 2, 5, 10, 20, 30)}
TICKS_SMALL = {"flaime_al": (0, 0.5, 2, 5, 12), "onr_cu": (0, 1, 5, 15, 30)}
NODE_SHORT = {"powder": "atomize", "print": "LPBF", "test": "tensile", "calphad": "CALPHAD", "ded_small": "DED",
              "ded_large": "DED bars", "screen": "corrosion", "immersion": "immersion", "tensile": "tensile",
              "section": "section", "pip": "PIP", "composition": "design", "utility": "utility"}


@functools.lru_cache(maxsize=4)
def space(campaign: str) -> dict:
    """{balance, min_balance, k, bounds {el: (lo, hi)}, rules [names]} from twin/spaces.py."""
    try:
        from twin import spaces as SP
        s = SP.SPACES[campaign]
        return dict(balance=s.balance, min_balance=float(s.min_balance), k=tuple(s.k_range),
                    bounds={e: (float(lo), float(hi)) for e, (lo, hi) in s.bounds.items()},
                    rules=[r[0] for r in s.rules])
    except Exception:                               # noqa: BLE001
        return _FALLBACK[campaign]


def _rule(s: str) -> str:
    return s.replace("<=", "≤").replace(">=", "≥")


# ------------------------------------------------------------------------------------------------- colours
@functools.lru_cache(maxsize=1)
def _lut() -> np.ndarray:
    """DAL's truncated twilight (matplotlib 'twilight' on [0, 0.85]) as 256 RGB rows."""
    try:
        import matplotlib
        cm = matplotlib.colormaps["twilight"]
        return (np.array([cm(u)[:3] for u in np.linspace(0.0, 0.85, 256)]) * 255 + 0.5).astype(np.uint8)
    except Exception:                               # noqa: BLE001  (no matplotlib: twilight's own anchors)
        anchors = np.array([(225, 216, 226), (165, 191, 202), (109, 144, 191), (94, 87, 176), (83, 29, 124),
                            (47, 20, 54), (99, 24, 75), (158, 59, 79), (192, 116, 93), (200, 147, 118)], float)
        u = np.linspace(0, 1, 256)
        x = np.linspace(0, 1, len(anchors))
        return np.stack([np.interp(u, x, anchors[:, i]) for i in range(3)], 1).astype(np.uint8)


def norm(campaign: str, v: float) -> float:
    """0..1 on the campaign's square-root scale."""
    return math.sqrt(min(1.0, max(0.0, float(v) / VMAX[campaign])))


def colour(campaign: str, v: float) -> tuple:
    return tuple(int(x) for x in _lut()[int(round(norm(campaign, v) * 255))])


def _lum(rgb) -> float:
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


EDGE = (214, 216, 222, 255)           # a coloured tile's edge
EMPTY_EDGE = (64, 67, 74, 255)        # an element outside the space
EMPTY_INK = (92, 95, 102, 255)
ZERO_FILL = (40, 42, 48, 255)         # in the space, not in this design
ZERO_INK = (150, 152, 158, 255)
BAL_FILL = (88, 92, 100, 255)         # the balance element
STROKE = (12, 12, 14, 230)


def _f(pixels: float, bold: bool = False, cond: bool = False):
    """A font of exactly `pixels` px (style.font scales by S, so divide it back out)."""
    return ST.font(max(6, int(round(pixels))) / ST.S, bold=bold, cond=cond)


def _hatch(d: ImageDraw.ImageDraw, x0, y0, x1, y1, fill, step):
    """Diagonal hatching clipped to a box (the balance element's tile)."""
    w, h = x1 - x0, y1 - y0
    k = -h
    while k < w:
        a = (x0 + max(k, 0), y0 + max(0, -k))
        b = (x0 + min(w, k + h), y0 + min(h, w - k))
        d.line([a, b], fill=fill, width=1)
        k += step


# ------------------------------------------------------------------------------------------ the search space
@functools.lru_cache(maxsize=64)
def _split_tile(campaign: str, el: str, cell: int) -> Image.Image:
    """One element of the space as DAL drew it: lower-left triangle the lower bound, upper-right the upper bound,
    the symbol in the middle and both bounds in their corners."""
    lo, hi = space(campaign)["bounds"][el]
    im = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    c = cell - 1
    d.polygon([(0, 0), (c, 0), (c, c)], fill=colour(campaign, hi) + (255,))       # upper-right: upper bound
    d.polygon([(0, 0), (c, c), (0, c)], fill=colour(campaign, lo) + (255,))       # lower-left: lower bound
    d.rectangle((0, 0, c, c), outline=EDGE, width=max(1, cell // 60))
    d.text((cell / 2, cell * 0.47), el, font=_f(cell * 0.36, bold=True), fill=(255, 255, 255, 255), anchor="mm",
           stroke_width=max(1, cell // 36), stroke_fill=STROKE)
    fs = _f(cell * 0.17, bold=True)
    sw = max(1, cell // 48)
    d.text((cell * 0.93, cell * 0.06), f"{hi:g}", font=fs, fill=(255, 255, 255, 255), anchor="ra",
           stroke_width=sw, stroke_fill=STROKE)
    d.text((cell * 0.07, cell * 0.95), f"{lo:g}", font=fs, fill=(255, 255, 255, 255), anchor="ld",
           stroke_width=sw, stroke_fill=STROKE)
    return im


@functools.lru_cache(maxsize=8)
def _key_tile(campaign: str, cell: int) -> Image.Image:
    """The legend's tile: an element split as the space's are, with no symbol of its own."""
    im = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    c = cell - 1
    d.polygon([(0, 0), (c, 0), (c, c)], fill=colour(campaign, VMAX[campaign] * 0.08) + (255,))
    d.polygon([(0, 0), (c, c), (0, c)], fill=colour(campaign, 0.0) + (255,))
    d.rectangle((0, 0, c, c), outline=EDGE, width=max(1, cell // 60))
    return im


@functools.lru_cache(maxsize=16)
def _balance_tile(campaign: str, cell: int, label: str = "bal.", symbol: bool = True) -> Image.Image:
    sp = space(campaign)
    im = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    c = cell - 1
    d.rectangle((0, 0, c, c), fill=BAL_FILL)
    _hatch(d, 1, 1, c - 1, c - 1, (120, 124, 132, 255), max(4, cell // 7))
    d.rectangle((0, 0, c, c), outline=ST.INK + (255,), width=max(2, cell // 30))
    if symbol:
        d.text((cell / 2, cell * 0.47), sp["balance"], font=_f(cell * 0.36, bold=True), fill=(255, 255, 255, 255),
               anchor="mm", stroke_width=max(1, cell // 36), stroke_fill=STROKE)
    if cell >= 40 and symbol:
        fs = _f(cell * 0.17, bold=True)
        d.text((cell * 0.93, cell * 0.06), f"≥{sp['min_balance']:g}", font=fs, fill=(255, 255, 255, 255),
               anchor="ra", stroke_width=max(1, cell // 48), stroke_fill=STROKE)
        d.text((cell * 0.07, cell * 0.95), label, font=fs, fill=(255, 255, 255, 255), anchor="ld",
               stroke_width=max(1, cell // 48), stroke_fill=STROKE)
    return im


def _colourbar(campaign: str, bw: int, bh: int, vertical: bool, ticks, fsize: float, title: str = "",
               tick_len: int = 5) -> tuple:
    """A colourbar with its tick labels as an RGBA image and the offset of the bar in it: (image, bar x, bar y)."""
    lut = _lut()
    f = _f(fsize)
    labels = [f"{t:g}" for t in ticks]
    if vertical:
        lw = max(ST.text_w(f, s) for s in labels) + tick_len + 6
        th = int(fsize * 1.5) if title else 0
        tw_ = ST.text_w(f, title) if title else 0
        W_ = max(bw + lw, tw_) + 2
        im = Image.new("RGBA", (W_, bh + th + int(fsize)), (0, 0, 0, 0))
        d = ImageDraw.Draw(im, "RGBA")
        y0 = th + int(fsize * 0.5)
        idx = (np.linspace(1, 0, bh) * 255).round().astype(int)
        grad = np.repeat(lut[idx][:, None, :], bw, axis=1)
        im.paste(Image.fromarray(grad, "RGB"), (0, y0))
        d.rectangle((0, y0, bw - 1, y0 + bh - 1), outline=EDGE, width=1)
        if title:
            d.text((0, 0), title, font=f, fill=ST.INK2 + (255,), anchor="la")
        for t, s in zip(ticks, labels):
            y = y0 + (1 - norm(campaign, t)) * (bh - 1)
            d.line([(bw, y), (bw + tick_len, y)], fill=ST.INK2 + (255,), width=1)
            d.text((bw + tick_len + 4, y), s, font=f, fill=ST.INK2 + (255,), anchor="lm")
        return im, 0, y0
    lh = int(fsize * 1.25) + tick_len
    im = Image.new("RGBA", (bw + int(fsize * 1.6), bh + lh + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    x0 = int(fsize * 0.8)
    idx = (np.linspace(0, 1, bw) * 255).round().astype(int)
    grad = np.repeat(lut[idx][None, :, :], bh, axis=0)
    im.paste(Image.fromarray(grad, "RGB"), (x0, 0))
    d.rectangle((x0, 0, x0 + bw - 1, bh - 1), outline=EDGE, width=1)
    for t, s in zip(ticks, labels):
        x = x0 + norm(campaign, t) * (bw - 1)
        d.line([(x, bh), (x, bh + tick_len)], fill=ST.INK2 + (255,), width=1)
        d.text((x, bh + tick_len + 1), s, font=f, fill=ST.INK2 + (255,), anchor="ma")
    return im, x0, 0


def _pill(d: ImageDraw.ImageDraw, x, y, text, f, fill, ink=ST.BG):
    """A campaign tag: the campaign colour as a mark, its name in dark text on it."""
    tw_ = ST.text_w(f, text)
    hh = f.size * 1.35
    d.rounded_rectangle((x, y, x + tw_ + f.size * 0.9, y + hh), radius=hh / 2, fill=tuple(fill) + (255,))
    d.text((x + f.size * 0.45, y + hh / 2), text, font=f, fill=tuple(ink) + (255,), anchor="lm")
    return x + tw_ + f.size * 0.9


@functools.lru_cache(maxsize=8)
def _bounds_layers(campaign: str, w: int, h: int) -> dict:
    """The parts of bounds_figure that do not animate: the empty table under the title, the legend, the colourbar,
    and where each tile goes."""
    sp = space(campaign)
    pad = int(round(h * 0.03))
    ft = _f(h * 0.048, bold=True)
    fsub = _f(h * 0.028)
    title_h = ft.size * 1.35
    # the rules, wrapped between rules rather than inside one
    toks = [f"{sp['balance']} the balance, at least {sp['min_balance']:g} wt%.  Rules: " + _rule(sp["rules"][0])] \
        + [_rule(r) for r in sp["rules"][1:]]
    sub_lines, cur = [], ""
    for tk in toks:
        cand = (cur + "  \u00b7  " + tk) if cur else tk
        if cur and ST.text_w(fsub, cand) > w - 2 * pad:
            sub_lines.append(cur)
            cur = tk
        else:
            cur = cand
    sub_lines = (sub_lines + [cur])[:3]
    lead = fsub.size * 1.3
    head_h = int(pad * 0.4 + title_h + fsub.size * 0.5 + lead * len(sub_lines))
    cbar_w = int(round(w * 0.085))
    area_w, area_h = w - 2 * pad - cbar_w, h - head_h - 2 * pad
    pitch = min(area_w / COLS, area_h / ROWS_H)
    cell = int(pitch * (1 - GAP))
    tx0 = pad + int((area_w - pitch * COLS) / 2)
    ty0 = head_h + pad
    pos = {el: (int(tx0 + c * pitch), int(ty0 + r * pitch)) for el, (c, r) in
           ((el, _cell_xy(el)) for el in PTABLE_RC)}
    base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(base, "RGBA")
    # the title: the campaign's tag, then what the space is, in text ink; the rules under it
    x = _pill(d, pad, pad * 0.4, ST.CAMP_NAME[campaign], ft, ST.CAMP[campaign])
    n = len(sp["bounds"])
    d.text((x + ft.size * 0.4, pad * 0.4 + title_h / 2),
           f"({sp['balance']}): {n} alloying elements, {sp['k'][0]}-{sp['k'][1]} at a time",
           font=ft, fill=ST.INK + (255,), anchor="lm")
    for i, line in enumerate(sub_lines):
        d.text((pad, pad * 0.4 + title_h + fsub.size * 0.5 + i * lead), line, font=fsub, fill=ST.INK2 + (255,),
               anchor="la")
    # every element, outlined; the space's own are drawn by the animation
    fe = _f(cell * 0.27)
    for el, (x0, y0) in pos.items():
        if el in sp["bounds"] or el == sp["balance"]:
            d.rectangle((x0, y0, x0 + cell - 1, y0 + cell - 1), outline=(80, 84, 92, 255), width=1)
            continue
        d.rectangle((x0, y0, x0 + cell - 1, y0 + cell - 1), outline=EMPTY_EDGE, width=1)
        d.text((x0 + cell / 2, y0 + cell / 2), el, font=fe, fill=EMPTY_INK, anchor="mm")
    # lanthanides marker: a faint bracket from La's tile to the row below
    xl, yl = pos["La"]
    d.line([(xl + cell / 2, yl + cell + 2), (xl + cell / 2, pos["Ce"][1] + cell / 2),
            (pos["Ce"][0] - 3, pos["Ce"][1] + cell / 2)], fill=(70, 73, 80, 255), width=1)
    # the legend, in the table's empty top middle (columns 3-12, rows 1-3)
    lx0, ly0 = int(tx0 + 2.4 * pitch), int(ty0 + 0.15 * pitch)
    lw_, lh_ = int(9.4 * pitch), int(2.7 * pitch)
    leg = Image.new("RGBA", (lw_, lh_), (0, 0, 0, 0))
    dl = ImageDraw.Draw(leg, "RGBA")
    kc = int(cell * 0.95)
    tile = _key_tile(campaign, kc)
    ky = int((lh_ - kc) / 2)
    leg.alpha_composite(tile, (0, ky))
    fl = _f(pitch * 0.22)
    fl2 = _f(pitch * 0.19)
    dl.line([(kc * 0.80, ky + kc * 0.18), (kc * 1.25, ky + kc * 0.18)], fill=ST.INK2 + (255,), width=1)
    dl.text((kc * 1.30, ky + kc * 0.18), "upper bound, wt%", font=fl, fill=ST.INK + (255,), anchor="lm")
    dl.line([(kc * 0.20, ky + kc * 0.84), (kc * 1.25, ky + kc * 0.84)], fill=ST.INK2 + (255,), width=1)
    dl.text((kc * 1.30, ky + kc * 0.84), "lower bound, wt%", font=fl, fill=ST.INK + (255,), anchor="lm")
    bx = int(lw_ * 0.56)
    leg.alpha_composite(_balance_tile(campaign, kc, symbol=False), (bx, ky))
    dl.text((bx + kc * 1.12, ky + kc * 0.30), f"{sp['balance']}: the balance,", font=fl, fill=ST.INK + (255,),
            anchor="lm")
    dl.text((bx + kc * 1.12, ky + kc * 0.62), f"at least {sp['min_balance']:g} wt%", font=fl,
            fill=ST.INK + (255,), anchor="lm")
    dl.text((0, lh_ - 1), "Colour: wt%, square-root scale. Grey: not in the space.", font=fl2,
            fill=ST.INK2 + (255,), anchor="ld")
    # the colourbar, right of the table
    cb, _, _ = _colourbar(campaign, int(cbar_w * 0.22), int(pitch * 5.6), True, TICKS[campaign], pitch * 0.2,
                          title="wt%")
    cbx = int(tx0 + pitch * COLS + (w - pad - (tx0 + pitch * COLS) - cb.width) / 2)
    cby = int(ty0 + pitch * 0.2)
    order = sorted(sp["bounds"], key=lambda e: (-sp["bounds"][e][1], e))
    return dict(base=base, legend=(leg, lx0, ly0), cbar=(cb, cbx, cby), pos=pos, cell=cell, order=order,
                sp=sp)


def _faded(im: Image.Image, a: float) -> Image.Image:
    if a >= 0.999:
        return im
    out = im.copy()
    out.putalpha(im.getchannel("A").point(lambda v, k=a: int(v * k)))
    return out


_FINAL: dict = {}


def bounds_figure(campaign: str, w: int = 1700, h: int = 760, reveal: float = 1.0) -> Image.Image:
    """The campaign's search space on the periodic table, w x h RGBA, transparent background. reveal 0..1: the empty
    table, then the balance element, then the alloying elements from the highest upper bound down, each popping in;
    the legend and the colourbar fade in early so the encoding is read as the tiles land."""
    reveal = float(min(1.0, max(0.0, reveal)))
    key = (campaign, w, h)
    if reveal >= 1.0 and key in _FINAL:
        return _FINAL[key].copy()
    L = _bounds_layers(campaign, w, h)
    im = L["base"].copy()
    for name, (t0, t1) in (("legend", (0.06, 0.22)), ("cbar", (0.10, 0.30))):
        lay, x, y = L[name]
        a = ST.ramp(reveal, t0, t1)
        if a > 0.003:
            im.alpha_composite(_faded(lay, a), (x, y))
    cell, pos = L["cell"], L["pos"]
    tiles = [(L["sp"]["balance"], 0.0, 0.10)]
    n = len(L["order"])
    for i, el in enumerate(L["order"]):
        s0 = 0.10 + 0.72 * i / max(1, n)
        tiles.append((el, s0, s0 + 0.18))
    for el, s0, s1 in tiles:
        u = (reveal - s0) / (s1 - s0)
        if u <= 0:
            continue
        u = min(1.0, u)
        spr = _balance_tile(campaign, cell) if el == L["sp"]["balance"] else _split_tile(campaign, el, cell)
        k = 0.55 + 0.45 * ST.ease_out(u) + 0.08 * math.sin(math.pi * u) * (1 - u)   # a small overshoot, a pop
        sz = max(2, int(round(cell * k)))
        if sz != cell:
            spr = spr.resize((sz, sz), Image.BILINEAR)
        spr = _faded(spr, min(1.0, u * 2.5))
        x0, y0 = pos[el]
        im.alpha_composite(spr, (int(x0 + (cell - sz) / 2), int(y0 + (cell - sz) / 2)))
    if reveal >= 1.0:
        _FINAL[key] = im.copy()
    return im


# --------------------------------------------------------------------------------------- one design in flight
def _table_geom(w: int, h: int, top: int, bottom: int, pad: int) -> tuple:
    pitch = min((w - 2 * pad) / COLS, (h - top - bottom) / ROWS_H)
    x0 = (w - pitch * COLS) / 2
    return pitch, x0, top


@functools.lru_cache(maxsize=32)
def _compact_base(campaign: str, w: int, h: int, alpha: float, top: int, bottom: int) -> tuple:
    """The panel with its table drawn empty: grey outlines outside the space, dark tiles for the space's elements,
    the balance element hatched, and the colourbar in the table's empty top middle."""
    sp = space(campaign)
    pad = max(6, int(round(w * 0.022)))
    pitch, x0, y0 = _table_geom(w, h, top, bottom, pad)
    cell = max(3, int(pitch * (1 - GAP)))
    im = ST.rounded((w, h), max(6, int(h * 0.035)), ST.SURF, alpha)
    d = ImageDraw.Draw(im, "RGBA")
    pos = {el: (int(x0 + c * pitch), int(y0 + r * pitch)) for el, (c, r) in
           ((el, _cell_xy(el)) for el in PTABLE_RC)}
    big = cell >= 14
    fe = _f(cell * 0.46, bold=True) if big else None
    for el, (x, y) in pos.items():
        box = (x, y, x + cell - 1, y + cell - 1)
        if el == sp["balance"]:
            d.rectangle(box, fill=BAL_FILL)
            _hatch(d, x + 1, y + 1, x + cell - 2, y + cell - 2, (122, 126, 134, 255), max(3, cell // 4))
            d.rectangle(box, outline=ST.INK + (255,), width=max(1, cell // 14))
            if big:
                d.text((x + cell / 2, y + cell / 2), el, font=fe, fill=(255, 255, 255, 255), anchor="mm",
                       stroke_width=1, stroke_fill=STROKE)
        elif el in sp["bounds"]:
            d.rectangle(box, fill=ZERO_FILL, outline=(96, 100, 108, 255), width=1)
            if big:
                d.text((x + cell / 2, y + cell / 2), el, font=fe, fill=ZERO_INK, anchor="mm")
        else:
            d.rectangle(box, outline=EMPTY_EDGE if big else (58, 61, 68, 255), width=1)
            if big:
                d.text((x + cell / 2, y + cell / 2), el, font=_f(cell * 0.40), fill=EMPTY_INK, anchor="mm")
    cb = None
    if big:   # the colourbar in the gap between columns 3 and 12, row 1
        cb, cbx0, _ = _colourbar(campaign, int(pitch * 8.6), max(5, int(pitch * 0.30)), False,
                                 TICKS_SMALL[campaign], max(9.0, pitch * 0.42))
        cx = int(x0 + 2.75 * pitch) - cbx0
        cy = int(y0 + 0.30 * pitch)
        im.alpha_composite(cb, (cx, cy))
        fl = _f(max(9.0, pitch * 0.42))
        d.text((cx + cbx0 + pitch * 8.6 / 2, cy + cb.height + pitch * 0.08),
               f"wt%, square-root scale (0-{VMAX[campaign]:g})", font=fl, fill=ST.INK2 + (255,), anchor="ma")
    return im, pos, cell, pitch, x0, y0, pad


def _tile(d: ImageDraw.ImageDraw, campaign: str, el: str, v: float, x: int, y: int, cell: int, big: bool,
          fe=None):
    rgb = colour(campaign, v)
    d.rectangle((x, y, x + cell - 1, y + cell - 1), fill=rgb + (255,), outline=EDGE, width=1)
    if cell >= 40:                      # room for the value under the symbol
        d.text((x + cell / 2, y + cell * 0.40), el, font=_f(cell * 0.36, bold=True), fill=(255, 255, 255, 255),
               anchor="mm", stroke_width=max(1, cell // 36), stroke_fill=STROKE)
        d.text((x + cell / 2, y + cell * 0.80), f"{v:.2f}" if v < 10 else f"{v:.1f}", font=_f(cell * 0.24),
               fill=(255, 255, 255, 255), anchor="mm", stroke_width=1, stroke_fill=STROKE)
    elif big and fe is not None:
        d.text((x + cell / 2, y + cell / 2), el, font=fe, fill=(255, 255, 255, 255), anchor="mm",
               stroke_width=1, stroke_fill=STROKE)


def _comp_line(campaign: str, comp: dict) -> list:
    sp = space(campaign)
    bal = sp["balance"]
    items = sorted(((e, float(v)) for e, v in comp.items() if e in PTABLE_RC and float(v) > 0 and e != bal),
                   key=lambda kv: -kv[1])
    out = []
    if bal in comp:
        out.append(f"{bal} {float(comp[bal]):.1f} bal.")
    for e, v in items:
        out.append(f"{e} {v:.2f}" if v < 10 else f"{e} {v:.1f}")
    return out


def composition_panel(campaign: str, comp: dict, w: int = 450, h: int = 300, title: str = "",
                      alpha: float = 0.82) -> Image.Image:
    """One design's composition on the compact periodic table: a semi-transparent dark panel, w x h RGBA. The
    title (default 'FLAIME alloy') beside a campaign-colour swatch; the composition in wt% under the table, largest
    first, the balance element first."""
    top = int(round(min(h * 0.115, 44)))
    bottom = int(round(min(h * 0.20, 84)))
    im, pos, cell, pitch, x0, y0, pad = _compact_base(campaign, int(w), int(h), round(float(alpha), 3), top, bottom)
    im = im.copy()
    d = ImageDraw.Draw(im, "RGBA")
    big = cell >= 14
    fe = _f(cell * 0.46, bold=True) if big else None
    sp = space(campaign)
    for el, v in comp.items():
        if el not in pos or el == sp["balance"]:
            continue
        v = float(v)
        if v <= 0:
            continue
        x, y = pos[el]
        _tile(d, campaign, el, v, x, y, cell, big, fe)
    # the title row
    ft = _f(top * 0.50, bold=True)
    sw = int(top * 0.42)
    ty = int(top * 0.55)
    d.rounded_rectangle((pad, ty - sw / 2, pad + sw, ty + sw / 2), radius=max(2, sw // 4),
                        fill=tuple(ST.CAMP[campaign]) + (255,))
    tt = title or f"{ST.CAMP_NAME[campaign]} alloy"
    while ST.text_w(ft, tt) > w - 3 * pad - sw and len(tt) > 4:
        tt = tt[:-2].rstrip() + "…" if not tt.endswith("…") else tt[:-2] + "…"
    d.text((pad + sw + pad * 0.6, ty), tt, font=ft, fill=ST.INK + (255,), anchor="lm")
    # the composition, under the table
    parts = _comp_line(campaign, comp)
    fc = _f(min(22.0, max(10.0, bottom * 0.30)))
    lines, line = [], ""
    for p in parts:
        cand = (line + "  ·  " + p) if line else p
        if line and ST.text_w(fc, cand) > w - 2 * pad:
            lines.append(line)
            line = p
        else:
            line = cand
    if line:
        lines.append(line)
    ly = y0 + pitch * ROWS_H + bottom * 0.08
    lead = fc.size * 1.25
    max_lines = max(1, int((h - ly - pad * 0.5) // lead))
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1] + "  …"
    for i, s in enumerate(lines):
        d.text((pad, ly + i * lead), s, font=fc, fill=(ST.INK if i == 0 else ST.INK) + (255,), anchor="la")
    return im


# ---------------------------------------------------------------------------------------- the batch in flight
@functools.lru_cache(maxsize=4)
def _crop(campaign: str) -> tuple:
    """The part of the table a campaign's elements span: (first row, last row, first column, last column, whether the
    lanthanide row is needed). FLAIME: rows 2-5, columns 1-14 and the lanthanides (Ce, Er); ONR: rows 3-5, 4-14."""
    sp = space(campaign)
    els = [e for e in set(sp["bounds"]) | {sp["balance"]} if e in PTABLE_RC]
    main = [PTABLE_RC[e] for e in els if PTABLE_RC[e][0] != 9]
    lan = [PTABLE_RC[e] for e in els if PTABLE_RC[e][0] == 9]
    cols = [c for _, c in main + lan]
    return (min(r for r, _ in main), max(r for r, _ in main), min(cols), max(cols), bool(lan))


MINI_LAN_GAP = 0.25


def _crop_dims(campaign: str) -> tuple:
    r0, r1, c0, c1, lan = _crop(campaign)
    return c1 - c0 + 1, (r1 - r0 + 1) + ((1 + MINI_LAN_GAP) if lan else 0)


@functools.lru_cache(maxsize=64)
def _mini_base(campaign: str, tw: int, th: int) -> tuple:
    """A small table, tw x th, cut to the rows and columns the campaign's elements span, with no panel: outlines,
    the space's elements dark, the balance hatched; symbols when the tiles are big enough to read them."""
    sp = space(campaign)
    r0, r1, c0, c1, lan = _crop(campaign)
    ncol, nrow = _crop_dims(campaign)
    pitch = min(tw / ncol, th / nrow)
    x0 = (tw - pitch * ncol) / 2
    cell = max(2, int(round(pitch * (1 - GAP))))
    im = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    pos = {}
    for el, (r, c) in PTABLE_RC.items():
        if not (c0 <= c <= c1):
            continue
        if r == 9:
            if not lan:
                continue
            yy = (r1 - r0 + 1) + MINI_LAN_GAP
        elif r0 <= r <= r1:
            yy = r - r0
        else:
            continue
        pos[el] = (int(x0 + (c - c0) * pitch), int(yy * pitch))
    sym = cell >= 13
    fe = _f(cell * 0.46, bold=True) if sym else None
    for el, (x, y) in pos.items():
        box = (x, y, x + cell - 1, y + cell - 1)
        if el == sp["balance"]:
            d.rectangle(box, fill=BAL_FILL, outline=ST.INK + (255,), width=1)
            if sym:
                d.text((x + cell / 2, y + cell / 2), el, font=fe, fill=(255, 255, 255, 255), anchor="mm",
                       stroke_width=1, stroke_fill=STROKE)
        elif el in sp["bounds"]:
            d.rectangle(box, fill=ZERO_FILL, outline=(92, 96, 104, 255), width=1)
            if sym:
                d.text((x + cell / 2, y + cell / 2), el, font=fe, fill=ZERO_INK, anchor="mm")
        else:
            d.rectangle(box, outline=(56, 59, 66, 255), width=1)
    return im, pos, cell, pitch, ncol


def _grid_for(n: int, aw: int, ah: int, head: int, ncol: float, nrow: float) -> tuple:
    """(columns, rows) for n small tables in aw x ah, each with a header of `head` px: the largest pitch wins."""
    best = (1, max(1, n), 0.0)
    for cols in (1, 2, 3):
        rows = math.ceil(n / cols)
        sw, sh = aw / cols, ah / rows
        p = min((sw - 6) / ncol, (sh - head - 6) / nrow)
        if p > best[2]:
            best = (cols, rows, p)
    return best[0], best[1]


def multiples_panel(items: list, w: int = 450, h: int = 300, alpha: float = 0.82, title: str = "") -> Image.Image:
    """Up to six designs in flight as small tables on one semi-transparent panel, w x h RGBA. items: (campaign,
    design id, composition, node) as twin.video.data.Replay.in_flight gives them (with the campaign added). Each
    table has '#id node' over it beside its campaign's swatch; one colourbar per campaign present, at the bottom."""
    items = list(items)[:6]
    w, h = int(w), int(h)
    im = ST.rounded((w, h), max(6, int(h * 0.035)), ST.SURF, alpha)
    d = ImageDraw.Draw(im, "RGBA")
    pad = max(6, int(round(w * 0.022)))
    camps = []
    for it in items:
        if it[0] not in camps:
            camps.append(it[0])
    if not camps:
        camps = ["flaime_al"]
    top = int(round(h * 0.10))
    ft = _f(top * 0.55, bold=True)
    if not title:
        who = ST.CAMP_NAME[camps[0]] if len(camps) == 1 else "Both campaigns"
        title = f"{who}: {len(items)} alloy{'s' if len(items) != 1 else ''} in flight" if items else \
            f"{who}: nothing in flight"
    sw = int(top * 0.42)
    xx = pad
    for c in camps:
        d.rounded_rectangle((xx, top * 0.55 - sw / 2, xx + sw, top * 0.55 + sw / 2), radius=max(2, sw // 4),
                            fill=tuple(ST.CAMP[c]) + (255,))
        xx += sw + 4
    d.text((xx + pad * 0.4, top * 0.55), title, font=ft, fill=ST.INK + (255,), anchor="lm")
    # colourbars at the bottom, one per campaign
    fcb = _f(max(9.0, h * 0.034))
    cb_h = max(5, int(h * 0.022))
    bot = int(cb_h + fcb.size * 1.6 + pad * 0.6)
    nb = len(camps)
    seg = (w - 2 * pad) / nb
    for i, c in enumerate(camps):
        label = f"{space(c)['balance']} alloys, wt%" if nb > 1 else "wt%, square-root scale"
        lw_ = ST.text_w(fcb, label) + 8
        bw = int(max(40, seg - lw_ - 2 * fcb.size - 10))
        cb, cbx0, _ = _colourbar(c, bw, cb_h, False, TICKS_SMALL[c], fcb.size)
        bx = int(pad + i * seg)
        by = h - bot + int(pad * 0.2)
        d.text((bx, by + cb_h / 2), label, font=fcb, fill=ST.INK2 + (255,), anchor="lm")
        im.alpha_composite(cb, (int(bx + lw_ - cbx0 + fcb.size * 0.4), by))
    # the tables
    head = max(11, int(h * 0.055))
    aw, ah = w - 2 * pad, h - top - bot - int(pad * 0.3)
    n = max(1, len(items))
    dims = [_crop_dims(c) for c in camps]
    cols, rows = _grid_for(n, aw, ah, head, max(x for x, _ in dims), max(y for _, y in dims))
    sw_, sh_ = aw / cols, ah / rows
    fh = _f(head * 0.80, bold=True)
    fh2 = _f(head * 0.74)
    for i, (camp, did, comp, node) in enumerate(items):
        cx = pad + (i % cols) * sw_
        cy = top + (i // cols) * sh_
        tw, th = int(sw_ - 6), int(sh_ - head - 6)
        base, pos, cell, pitch, ncol = _mini_base(camp, tw, th)
        tile = base.copy()
        dt = ImageDraw.Draw(tile, "RGBA")
        bal = space(camp)["balance"]
        fe = _f(cell * 0.46, bold=True) if cell >= 13 else None
        for el, v in comp.items():
            if el in pos and el != bal and float(v) > 0:
                x, y = pos[el]
                _tile(dt, camp, el, float(v), x, y, cell, cell >= 13, fe)
        ox = int(cx + 3)
        im.alpha_composite(tile, (ox, int(cy + head + 2)))
        hx = int(cx + 3 + (tw - pitch * ncol) / 2)
        ss = int(head * 0.55)
        d.rounded_rectangle((hx, cy + head / 2 - ss / 2, hx + ss, cy + head / 2 + ss / 2), radius=max(1, ss // 4),
                            fill=tuple(ST.CAMP[camp]) + (255,))
        lab = f"#{did}"
        d.text((hx + ss + 4, cy + head / 2), lab, font=fh, fill=ST.INK + (255,), anchor="lm")
        nx = hx + ss + 4 + ST.text_w(fh, lab) + 6
        d.text((nx, cy + head / 2), NODE_SHORT.get(str(node), str(node or "")), font=fh2, fill=ST.INK2 + (255,),
               anchor="lm")
    return im


# ------------------------------------------------------------------------------------------------------ test
def _demo():
    """Stills to /tmp/vid/ptable_*.png and per-call timings (python -m twin.video.ptable)."""
    import subprocess
    import time
    from pathlib import Path

    from . import data as D
    dst = Path("/tmp/vid")
    dst.mkdir(parents=True, exist_ok=True)
    for camp in ("flaime_al", "onr_cu"):
        for r in (0.0, 0.5, 1.0):
            t = time.time()
            im = bounds_figure(camp, 1700, 760, r)
            ms = (time.time() - t) * 1000
            bg = Image.new("RGBA", (1920, 1080), ST.BG + (255,))
            bg.alpha_composite(im, (110, 200))
            bg.convert("RGB").save(dst / f"ptable_bounds_{camp}_{int(r * 100):03d}.png")
            print(f"bounds_figure {camp} reveal {r}: {ms:.1f} ms (first call builds the cache)")
        t = time.time()
        for k in range(30):
            bounds_figure(camp, 1700, 760, 0.3 + 0.02 * k)
        print(f"bounds_figure {camp} animating: {(time.time() - t) / 30 * 1000:.1f} ms/call")
    R = D.Replay()
    frame = dst / "atomize_frame.png"
    src = D.HERE / "out" / "hd" / "alloy_atomize.mp4"
    if not frame.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "200", "-i", str(src), "-vframes", "1", str(frame)],
                       check=True)
    bg = np.asarray(Image.open(frame).convert("RGB")).copy()
    comp = R.designs["flaime_al"]["12"]
    composition_panel("flaime_al", comp, 450, 300, "FLAIME alloy #12, in flight: atomize")
    t = time.time()
    for k in range(50):
        p1 = composition_panel("flaime_al", comp, 450, 300, "FLAIME alloy #12, in flight: atomize")
    print(f"composition_panel: {(time.time() - t) / 50 * 1000:.1f} ms/call")
    cu = R.in_flight(24 * 120, "onr_cu", 24 * 7, 1)
    cu_id, cu_comp = (cu[0][0], cu[0][1]) if cu else next(iter(R.designs["onr_cu"].items()))
    p2 = composition_panel("onr_cu", cu_comp, 450, 300, f"ONR alloy #{cu_id}, in flight: DED blocks")
    fl = [("flaime_al",) + x for x in R.in_flight(24 * 100, "flaime_al", 24 * 7, 6)]
    multiples_panel(fl, 450, 300)
    t = time.time()
    for k in range(50):
        p3 = multiples_panel(fl, 450, 300)
    print(f"multiples_panel ({len(fl)} items): {(time.time() - t) / 50 * 1000:.1f} ms/call")
    mixed = fl[:3] + [("onr_cu",) + x for x in R.in_flight(24 * 200, "onr_cu", 24 * 10, 3)]
    p4 = multiples_panel(mixed, 520, 330)
    out = bg.copy()
    ST.paste(out, p1, 1920 - 450 - 24, 1080 - 300 - 24)
    ST.paste(out, p2, 24, 1080 - 300 - 24)
    ST.paste(out, p3, 1920 - 450 - 24, 24)
    ST.paste(out, p4, 24, 24)
    Image.fromarray(out).save(dst / "ptable_overlays.png")
    Image.fromarray(np.asarray(p1)).save(dst / "ptable_comp_panel.png")
    big = composition_panel("flaime_al", comp, 900, 600, "FLAIME alloy #12 (large)")
    out2 = bg.copy()
    ST.paste(out2, big, 40, 40)
    ST.paste(out2, multiples_panel([("onr_cu",) + x for x in R.in_flight(24 * 200, "onr_cu", 24 * 20, 6)],
                                   450, 300), 1920 - 474, 40)
    Image.fromarray(out2).save(dst / "ptable_overlays2.png")
    print("stills in", dst)


if __name__ == "__main__":
    _demo()
