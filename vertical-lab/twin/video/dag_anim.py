"""The two function networks: built full screen node by node, with real figures popping out at their nodes, then
collapsed to icons and docked into a corner as the overlay the campaign replay lights up (twin/video/dag_anim.py).

    dag = Dag()
    dag.intro_frame(t)          # 0 <= t <= dag.DURATION: one 1920 x 1080 RGB frame (numpy uint8) of the intro
    dag.overlay(lit, alpha, t)  # the docked mini-DAG, 820 x 200 RGBA, for (x, y) = Dag.DOCK[:2]; lit[(campaign, node)]
                                # = 0..1 (Dag.intensity(count) turns Replay.lit counts into that)
    dag.captions                # [(t0, t1, text)]: the intro's captions, drawn by intro_frame; also its chapter marks

The nodes and edges are data.network(campaign) (twin/opt/network.py when it lands, else the brief's). Figures: the
twin's simulated instrument images (out/twin2/instruments/*.png) when they exist, matched to a node by the instrument
names in INSTR, else a few of PR 318's real or illustrative figures (FIG_FALLBACK), each labelled with its source.
Icons are drawn here (pictogram()); a thumb from out/twin2/thumbs/ matching a node shows on its card.

``python -m twin.video.dag_anim`` saves stills to /tmp/vid/dag_*.png and times a frame.
"""
from __future__ import annotations

import math
import sys
import time
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import data as D
from . import style as St
from .style import BG, CAMP, INK, INK2, RULE, H, W, ease, ease_out, font, mix, px

OUT = D.HERE / "out"
INSTR_DIR = D.OUT2 / "instruments"
THUMB_DIR = D.OUT2 / "thumbs"

CARD_FILL = (24, 28, 35)
CARD_EDGE = (66, 70, 78)
ICON_FILL = (32, 36, 44)
ICON_EDGE = (84, 88, 96)
PANEL_FILL = (22, 24, 28)
WARN = St.WARN

SHORT = {"composition": "comp.", "calphad": "CALPHAD", "powder": "atomize", "print": "LPBF", "section": "section",
         "pip": "PIP", "test": "tensile", "utility": "utility", "ded_small": "DED", "ded": "DED",
         "screen": "corrosion", "tensile": "tensile", "immersion": "immersion"}
KIND_TAG = {"input": "input", "sim": "simulation, HPC", "lab": "in the lab", "out": "outside facility",
            "output": "output"}
# which pictogram a node gets: by key, else by a word in its title
ICON_OF = {"composition": "tile", "calphad": "phase", "powder": "droplets", "print": "laser", "section": "cube",
           "pip": "indent", "test": "dogbone", "tensile": "dogbone", "ded_small": "nozzle", "ded": "nozzle",
           "ded_large": "nozzle", "screen": "beaker", "immersion": "vial", "utility": "target"}
ICON_WORDS = [("composit", "tile"), ("calphad", "phase"), ("atomiz", "droplets"), ("powder", "droplets"),
              ("lpbf", "laser"), ("print", "laser"), ("ded", "nozzle"), ("section", "cube"), ("pip", "indent"),
              ("tensile", "dogbone"), ("corros", "beaker"), ("immers", "vial"), ("utility", "target")]
# instruments (twin/instruments INSTRUMENTS names) whose images belong at a node, best first
INSTR = {"powder": ["sem_powder", "psd", "xrd_powder", "xrf", "eds", "yield", "atomize", "powder"],
         "print": ["density", "lpbf", "print", "build"], "ded_small": ["density", "ded", "deposit"],
         "section": ["sem_section", "ebsd", "xrd_part", "vickers", "nanoindent", "section"], "pip": ["pip"],
         "test": ["tensile_hot", "tensile", "test"], "tensile": ["tensile"],
         "screen": ["corrosion_screen", "screen", "eis", "lpr", "ocp", "corrosion"],
         "immersion": ["immersion", "icpms"], "calphad": ["calphad", "scheil", "thermo"],
         "composition": ["composition", "ptable"], "utility": ["utility"]}
# PR 318's own figures, until the twin's instrument images exist: (path, what it is)
FIG_FALLBACK = {
    ("flaime_al", "powder"): [("out/alloy_powder_sem.png", "real data: SEM of the lab's own atomized Al 4047 (DAL #157)")],
    ("flaime_al", "section"): [("out/alloy_characterize_panel_sem.png",
                                "illustrative section, real inset (PR 318, chapter 7)")],
    ("flaime_al", "pip"): [("out/alloy_characterize_panel_pip.png", "illustrative PIP curve (PR 318, chapter 7)")],
    ("flaime_al", "test"): [("out/alloy_characterize_panel_vhx.png",
                             "illustrative fracture surface (PR 318, chapter 7)")],
    ("onr_cu", "powder"): [("out/alloy_atomize_footage_pour.png",
                            "real footage: 630 bronze atomizing, Oct 27 2026 (DAL #219)")],
    ("onr_cu", "immersion"): [("out/icpms_still.png", "the ICP-MS station, a 3-D render (PR 318)")],
}
POP_PRIORITY = {"flaime_al": ["powder", "section", "pip", "test", "print", "calphad"],
                "onr_cu": ["powder", "screen", "immersion", "ded_small", "section", "tensile", "pip"]}
MAX_POPS = 4
# the brief's stations of a node that a conventional lab sends outside (twin/facility.py PROPOSED, external=True)
OUTSIDE_BASELINE = {("flaime_al", "print"), ("flaime_al", "pip"), ("flaime_al", "test"), ("onr_cu", "powder"),
                    ("onr_cu", "ded_small"), ("onr_cu", "pip"), ("onr_cu", "tensile")}

# ------------------------------------------------------------------------------------------------- geometry
MARGIN = 60
LANE = {"flaime_al": dict(label_y=98, top=138, h=204), "onr_cu": dict(label_y=716, top=752, h=196)}  # set by _layout
ONR_BOTTOM = 944                         # ONR's cards end here; its skip arcs hang 16 px below
CAP_Y = 994                              # captions: the bottom band (one line)
_BG_FRAME = None


def _bg() -> np.ndarray:
    global _BG_FRAME
    if _BG_FRAME is None:
        _BG_FRAME = St.blank(BG)
    return _BG_FRAME.copy()
DOCK = (24, 860, 820, 200)               # (x, y, w, h) of the overlay on the replay
FULL_ICON_RECT = (60, 322, 1800, 439)    # the same mini-DAG at full screen (820 x 200 scaled by 1800/820)
OV_ROW_Y = {"flaime_al": 50, "onr_cu": 140}
OV_X0, OV_X1, OV_R = 134, 794, 18


def _nbsp(s: str) -> str:
    """A number and its unit (250 C, 30 %) kept on one line."""
    import re
    return re.sub(r"(\d) (C|K|%|h|wt%)\b", "\\1\u00a0\\2", str(s))


def _short(n: dict) -> str:
    return SHORT.get(n["key"]) or n["title"].split(" ")[0][:10]


def _icon_kind(n: dict) -> str:
    if n["key"] in ICON_OF:
        return ICON_OF[n["key"]]
    t = (n["title"] + " " + n["key"]).lower()
    for w, k in ICON_WORDS:
        if w in t:
            return k
    return "dot"


# ------------------------------------------------------------------------------------------------- pictograms
def pictogram(kind: str, size: int, color=INK2, base_el: str = "Al") -> Image.Image:
    """A simple line pictogram, size x size RGBA, drawn at 4x and reduced (so its lines are smooth)."""
    return _pictogram(kind, int(size), tuple(color[:3]), base_el).copy()


@lru_cache(maxsize=512)
def _pictogram(kind, size, color, base_el):
    k = 4
    S_ = size * k
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = color + (255,)
    lw = max(2, int(S_ * 0.075))
    u = S_ / 100.0                        # draw in a 100 x 100 box

    def P(x, y):
        return (x * u, y * u)

    def line(pts, w=lw):
        d.line([P(*p) for p in pts], fill=c, width=w, joint="curve")
        for p in (pts[0], pts[-1]):
            r = w / 2
            d.ellipse((p[0] * u - r, p[1] * u - r, p[0] * u + r, p[1] * u + r), fill=c)

    if kind == "tile":
        d.rounded_rectangle((*P(16, 16), *P(84, 84)), radius=int(10 * u), outline=c, width=lw)
        f = font(1, bold=True)
        f = f.font_variant(size=int(34 * u))
        d.text(P(50, 54), base_el, font=f, fill=c, anchor="mm")
    elif kind == "phase":                 # a binary phase diagram: axes, liquidus and solidus lens
        line([(16, 14), (16, 86), (88, 86)])
        pts_l = [(16 + 72 * s, 26 + 40 * (s - 0.5) ** 2 * 2 + 10 * s) for s in np.linspace(0, 1, 24)]
        pts_s = [(16 + 72 * s, 26 + 58 * math.sin(math.pi * s) * 0.9 + 10 * s) for s in np.linspace(0, 1, 24)]
        line(pts_l, max(2, lw - 1))
        line(pts_s, max(2, lw - 1))
    elif kind == "droplets":
        for (x, y, r) in ((34, 34, 13), (66, 46, 9), (42, 70, 10), (70, 74, 6), (60, 22, 5)):
            d.ellipse((*P(x - r, y - r), *P(x + r, y + r)), outline=c, width=max(2, lw - 1))
    elif kind == "laser":                 # a beam onto a stack of layers, a spark where it lands
        line([(50, 8), (50, 50)])
        for i, y in enumerate((60, 72, 84)):
            line([(16, y), (84, y)], max(2, lw - 1))
        for a in range(0, 360, 60):
            x2, y2 = 50 + 11 * math.cos(math.radians(a)), 52 + 8 * math.sin(math.radians(a))
            line([(50, 52), (x2, y2)], max(2, lw // 2))
    elif kind == "nozzle":                # a DED nozzle over a bead
        d.polygon([P(32, 12), P(68, 12), P(58, 46), P(42, 46)], outline=c, width=lw)
        line([(50, 50), (50, 60)], max(2, lw // 2))
        d.chord((*P(26, 62), *P(74, 92)), 180, 360, outline=c, width=max(2, lw - 1))
        line([(12, 78), (88, 78)], max(2, lw - 1))
    elif kind == "cube":                  # a block with a cut face
        d.polygon([P(18, 34), P(52, 18), P(84, 34), P(84, 72), P(50, 88), P(18, 72)], outline=c, width=lw)
        line([(18, 34), (50, 50), (84, 34)], max(2, lw - 1))
        line([(50, 50), (50, 88)], max(2, lw - 1))
        for i in range(3):
            y = 58 + i * 9
            line([(22, y - 6 + i * 2), (44, y + 4 + i * 2)], max(2, lw // 2))
    elif kind == "indent":                # an indenter over a dented surface
        d.polygon([P(36, 10), P(64, 10), P(50, 46)], outline=c, width=lw)
        line([(10, 62), (34, 62)])
        d.arc((*P(32, 44), *P(68, 80)), 0, 180, fill=c, width=lw)
        line([(66, 62), (90, 62)])
    elif kind == "dogbone":               # a tensile bar, pulled
        pts = [(26, 16), (74, 16), (74, 34), (60, 40), (60, 60), (74, 66), (74, 84), (26, 84), (26, 66), (40, 60),
               (40, 40), (26, 34), (26, 16)]
        d.line([P(*p) for p in pts], fill=c, width=lw, joint="curve")
        line([(50, 4), (50, 12)], max(2, lw // 2))
        line([(50, 88), (50, 96)], max(2, lw // 2))
    elif kind == "beaker":                # a beaker of seawater
        line([(22, 14), (26, 18), (26, 84), (74, 84), (74, 18), (78, 14)])
        pts = [(28 + s * 44, 46 + 5 * math.sin(s * 3 * math.pi)) for s in np.linspace(0, 1, 30)]
        line(pts, max(2, lw - 1))
        pts = [(28 + s * 44, 62 + 5 * math.sin(s * 3 * math.pi + 1.4)) for s in np.linspace(0, 1, 30)]
        line(pts, max(2, lw // 2))
    elif kind == "vial":                  # a capped vial, liquid in it
        d.rounded_rectangle((*P(36, 6), *P(64, 22)), radius=int(3 * u), outline=c, width=lw)
        d.rounded_rectangle((*P(34, 22), *P(66, 92)), radius=int(12 * u), outline=c, width=lw)
        line([(38, 56), (62, 56)], max(2, lw - 1))
        for y in (66, 78):
            line([(42, y), (58, y)], max(2, lw // 2))
    elif kind == "target":
        for r in (40, 26, 12):
            d.ellipse((*P(50 - r, 50 - r), *P(50 + r, 50 + r)), outline=c, width=max(2, lw - 1))
        d.ellipse((*P(46, 46), *P(54, 54)), fill=c)
    else:
        d.ellipse((*P(30, 30), *P(70, 70)), outline=c, width=lw)
    return im.resize((size, size), Image.LANCZOS)


# --------------------------------------------------------------------------------------------- figure lookup
def _tokens(stem: str) -> str:
    return "_" + "".join(ch if ch.isalnum() else "_" for ch in stem.lower()) + "_"


def _camp_of(stem: str):
    t = _tokens(stem)
    if "_flaime" in t or "_al_" in t or "flaime_al" in t:
        return "flaime_al"
    if "_onr" in t or "_cu_" in t or "onr_cu" in t:
        return "onr_cu"
    return None


def figures_for(campaign: str, node: str) -> list:
    """[(path, label)] for a node: the twin's instrument images matching its instruments (this campaign's or
    unmarked), else FIG_FALLBACK. Re-globbed on every call (other streams write them while this one runs)."""
    names = INSTR.get(node, [node])
    found = []
    if INSTR_DIR.exists():
        for p in sorted(INSTR_DIR.glob("*.png")):
            t = _tokens(p.stem)
            camp = _camp_of(p.stem)
            if camp not in (None, campaign):
                continue
            for rank, nm in enumerate(names):
                if f"_{nm}_" in t:
                    found.append((rank, 0 if camp == campaign else 1, p))
                    break
    found.sort(key=lambda r: (r[0], r[1], r[2].name))
    out = []
    for rank, _, p in found:
        nm = names[rank].replace("_", " ")
        try:
            rel = p.relative_to(D.HERE)
        except ValueError:
            rel = p
        out.append((p, f"simulated instrument data: {nm} ({rel})"))
    if not out:
        for rel, what in FIG_FALLBACK.get((campaign, node), []):
            p = D.HERE / rel
            if p.exists():
                out.append((p, f"{what}  [{rel}]"))
    return out


def thumb_for(campaign: str, node: str):
    """A thumb from out/twin2/thumbs/ named for the node (its key, short name, pictogram or instruments; this
    campaign's or unmarked), else None."""
    if not THUMB_DIR.exists():
        return None
    names = [node, SHORT.get(node, node).lower().rstrip("."), ICON_OF.get(node, node)] + INSTR.get(node, [])
    best, best_rank = None, None
    for p in sorted(THUMB_DIR.glob("*.png")):
        t = _tokens(p.stem)
        camp = _camp_of(p.stem)
        if camp not in (None, campaign):
            continue
        hit = [i for i, nm in enumerate(names) if f"_{nm}_" in t]
        if not hit:
            continue
        rank = (hit[0], 0 if camp == campaign else 1)
        if best_rank is None or rank < best_rank:
            best, best_rank = p, rank
    return best


# --------------------------------------------------------------------------------------------- the class
class Dag:
    DOCK = DOCK
    DURATION = 105.0

    def __init__(self, duration: float = 105.0):
        self.nets = {c: D.network(c) for c in D.CAMPAIGNS}
        self.nodes = {c: self.nets[c]["nodes"] for c in D.CAMPAIGNS}
        self.idx = {c: {n["key"]: i for i, n in enumerate(self.nodes[c])} for c in D.CAMPAIGNS}
        self.edges = {c: [(a, b) for a, b in self.nets[c]["edges"] if a in self.idx[c] and b in self.idx[c]]
                      for c in D.CAMPAIGNS}
        try:
            sys.path.insert(0, str(D.HERE))
            from twin import spaces as SP
            self.n_el = {c: len(SP.SPACES[c].bounds) for c in D.CAMPAIGNS}
            self.base_el = {c: SP.SPACES[c].balance for c in D.CAMPAIGNS}
        except Exception:                                    # noqa: BLE001
            self.n_el = {"flaime_al": 15, "onr_cu": 8}
            self.base_el = {"flaime_al": "Al", "onr_cu": "Cu"}
        self._layout()
        self._figs()
        self._timeline(duration)
        self._cache: dict = {}
        self._ov_base: dict = {}
        self._sprites: dict = {}
        self._full_icons = None

    # ------------------------------------------------------------------------------------------ layout
    def _title_font(self, w, title):
        """The largest bold size (22 down to 17) at which every word of the title fits the card."""
        size = 22
        while size > 17 and max(St.text_w(font(size, bold=True), wd) for wd in title.split()) > w - 24:
            size -= 1
        return font(size, bold=True), size

    def _tag_lines(self, c, n, w):
        tag = [(KIND_TAG.get(n["kind"], n["kind"]), None)]
        if (c, n["key"]) in OUTSIDE_BASELINE and n["kind"] in ("lab", "out"):
            for ln in St.wrap("outside in a conventional lab", font(14, cond=True), w - 24 - 13):
                tag.append((ln, WARN))
        return tag

    def _meas_font(self, w):
        return font(19 if w < 180 else 20)

    def _need_h(self, c, i, w):
        n = self.nodes[c][i]
        fb, size = self._title_font(w, n["title"])
        yy = 16 + 22 + 19 * (len(self._tag_lines(c, n, w)) - 1)
        yy += (size + 5) * len(St.wrap(n["title"], fb, w - 24)[:3]) + 4
        yy += 24 * len(St.wrap(_nbsp(n["meas"]), self._meas_font(w), w - 24)) + 10
        return yy

    def _layout(self):
        self.card = {}
        for c in D.CAMPAIGNS:
            n = len(self.nodes[c])
            gap = 34 if n <= 8 else 22
            w = (W - 2 * MARGIN - (n - 1) * gap) / n
            h = int(min(248, max(170, max(self._need_h(c, i, w) for i in range(n)))))
            if c == "flaime_al":
                LANE[c] = dict(label_y=98, top=138, h=h)
            else:
                LANE[c] = dict(label_y=ONR_BOTTOM - h - 38, top=ONR_BOTTOM - h, h=h)
            L = LANE[c]
            self.card[c] = [(MARGIN + i * (w + gap), L["top"], w, L["h"]) for i in range(n)]
        f_bot = LANE["flaime_al"]["top"] + LANE["flaime_al"]["h"]
        # FLAIME's pops hang below its lane (ONR's lane is not drawn yet); ONR's sit between the lanes
        self.pop_box = {"flaime_al": (f_bot + 52, CAP_Y - 18), "onr_cu": (f_bot + 14, LANE["onr_cu"]["label_y"] - 10)}
        # the icon geometry (one function for the overlay and the full-screen icons)
        self.icon_unit = {}
        for c in D.CAMPAIGNS:
            n = len(self.nodes[c])
            xs = [OV_X0 + (OV_X1 - OV_X0) * i / max(1, n - 1) for i in range(n)]
            self.icon_unit[c] = [(x, OV_ROW_Y[c]) for x in xs]

    def icon_at(self, c: str, i: int, rect) -> tuple:
        """(cx, cy, r) of icon i of campaign c when the mini-DAG fills rect (x, y, w, h)."""
        x, y, w, h = rect
        k = w / DOCK[2]
        ux, uy = self.icon_unit[c][i]
        return (x + ux * k, y + uy * k, OV_R * k)

    # ------------------------------------------------------------------------------------------ figures
    def _figs(self):
        self.pops = {c: [] for c in D.CAMPAIGNS}
        for c in D.CAMPAIGNS:
            for key in POP_PRIORITY[c]:
                if key not in self.idx[c] or len(self.pops[c]) >= MAX_POPS:
                    continue
                figs = figures_for(c, key)
                if figs:
                    self.pops[c].append((key, figs[0]))
        self.pop_img = {}
        for c in D.CAMPAIGNS:
            for key, (path, label) in self.pops[c]:
                self.pop_img[(c, key)] = self._pop_card(c, path, label)
        self.thumbs = {(c, n["key"]): thumb_for(c, n["key"]) for c in D.CAMPAIGNS for n in self.nodes[c]}

    def _pop_card(self, c, path, label) -> Image.Image:
        """A popped figure: the image on a dark card with a campaign-coloured edge, its source under it."""
        im = Image.open(path).convert("RGB")
        top, bot = self.pop_box[c]
        mw, mh = (820 if c == "flaime_al" else 640), (bot - top) - 64
        k = min(mw / im.width, mh / im.height)
        im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
        f = font(16, cond=True)
        lines = St.wrap(label, f, max(im.width, 360))[:2]
        pad = 8
        tw = max([im.width] + [St.text_w(f, s) for s in lines])
        cw, ch = tw + 2 * pad, im.height + 2 * pad + 6 + 21 * len(lines)
        card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=10, fill=CARD_FILL + (255,), outline=CAMP[c] + (255,),
                            width=3)
        card.paste(im, (pad + (tw - im.width) // 2, pad))
        y = pad + im.height + 4
        for s in lines:
            d.text((pad, y), s, font=f, fill=INK2 + (255,))
            y += 21
        return card

    # ------------------------------------------------------------------------------------------ timeline
    def _caption_plan(self) -> dict:
        """The captions of each lane, anchored on a node (None: the lane's lead-in, before its first card)."""
        f, o = self.n_el["flaime_al"], self.n_el["onr_cu"]
        return {
            "flaime_al": [
                (None, f"FLAIME: aluminium alloys for laser powder bed fusion. A design is Al plus up to {f} "
                       f"alloying elements."),
                ("calphad", "CALPHAD runs on the BYU HPC: pycalphad on open databases, Thermo-Calc as an interface."),
                ("powder", "The lab makes its own powder: it doses and presses the charge, atomizes it and checks "
                           "the powder."),
                ("print", "Each powder is printed at several laser settings; every build is checked for density "
                          "and cracks."),
                ("section", "Sections show pores, cracks and grains; PIP reads a stress-strain curve from one "
                            "indent."),
                ("test", "Then bars are cut by wire EDM, heat treated and pulled, at room temperature and at 250 C."),
                ("utility", "The utility scores strength and ductility against the reference alloys, and counts the "
                            "mineral burden."),
            ],
            "onr_cu": [
                (None, f"ONR: copper alloys designed as powders for blown-powder DED. A design is Cu plus up to {o} "
                       f"elements."),
                ("ded_small", "Small DED blocks first: density, cracks and dilution at each set of settings."),
                ("screen", "A one-hour corrosion screen ranks the deposits before bars are made and tested."),
                ("immersion", "Then 30 days in seawater, read on days 1, 3, 7 and 14 on the way, and ICP-MS of "
                              "what dissolved." if D.ROUND == 3 else
                 "Then 30 days in seawater, and ICP-MS of what dissolved. The utility counts nickel "
                 "and the corrosion rate."),
            ]}

    def _lay_lanes(self, t, stretch, POP=4.2):
        """Node and pop times from t, with a lead-in per lane and at least CAP_MIN seconds for each caption."""
        CAP_MIN, LEAD = 4.8, 2.2
        base_step = {"flaime_al": 2.0, "onr_cu": 1.7}
        plan = self._caption_plan()
        node_t, pop_t, lanes, caps = {}, {}, {}, []
        for c in D.CAMPAIGNS:
            start = t
            anchors = {k: txt for k, txt in plan[c] if k is not None and k in self.idx[c]}
            lead = [txt for k, txt in plan[c] if k is None]
            last_cap = None
            if lead:
                caps.append([t, None, lead[0]])
                last_cap = t
            t += LEAD
            popkeys = {k for k, _ in self.pops[c]}
            for n in self.nodes[c]:
                if n["key"] in anchors:
                    if last_cap is not None and t - last_cap < CAP_MIN:
                        t = last_cap + CAP_MIN
                    caps.append([t, None, anchors[n["key"]]])
                    last_cap = t
                node_t[(c, n["key"])] = t
                t += base_step[c] + stretch
                if n["key"] in popkeys:
                    pop_t[(c, n["key"])] = (t - 0.9, t - 0.9 + POP)
                    t += POP
            if last_cap is not None and t - last_cap < CAP_MIN:
                t = last_cap + CAP_MIN
            lanes[c] = (start, t)
            t += 0.6
        return t, node_t, pop_t, lanes, caps

    def _timeline(self, duration: float):
        T = {"title": (0.0, 5.5)}
        n_nodes = sum(len(self.nodes[c]) for c in D.CAMPAIGNS)
        tail = 0.6 + 11.0 + 7.0 + 2.5 + 4.0           # between lanes, both, collapse, icons, dock
        n_pops = sum(len(self.pops[c]) for c in D.CAMPAIGNS)
        pop = 4.2
        for _ in range(3):                              # many figures: shorter pops (not under 3.2 s) to keep time
            over = self._lay_lanes(5.5, 0.0, pop)[0] + tail - 3.0 - duration
            if over <= 0.05 or not n_pops or pop <= 3.2:
                break
            pop = max(3.2, pop - over / n_pops)
        t_end0 = self._lay_lanes(5.5, 0.0, pop)[0]
        extra = max(0.0, duration - (t_end0 + tail))
        stretch = min(extra, 0.8 * n_nodes) / max(1, n_nodes)
        for _ in range(3):                              # the caption minimum makes the stretch nonlinear: settle
            t_end = self._lay_lanes(5.5, stretch, pop)[0]
            over = t_end + tail - duration
            if abs(over) < 0.05 or (over < 0 and stretch >= 0.8):
                break
            stretch = max(0.0, min(0.8, stretch - over / max(1, n_nodes)))
        t, self.node_t, self.pop_t, lanes, lane_caps = self._lay_lanes(5.5, stretch, pop)
        T.update(lanes)
        t += 0.6
        both = max(8.0, duration - (t + 7.0 + 2.5 + 4.0))
        T["both"] = (t, t + both)
        t += both
        T["collapse"] = (t, t + 7.0)
        t += 7.0
        T["icons"] = (t, t + 2.5)
        t += 2.5
        T["dock"] = (t, t + 4.0)
        t += 4.0
        self.T = T
        self.DURATION = t
        cap = [[0.0, 5.5, "Two campaigns, one lab: the function networks"]]
        for row in lane_caps:
            cap.append(row)
        b0, b1 = T["both"]
        self._mid_caps = {"Both campaigns run at once in one lab, sharing its atomizer, SEM, outside facilities, "
                          "market and calendar."}
        cap.append([b0, b0 + (b1 - b0) * 0.5, next(iter(self._mid_caps))])
        cap.append([b0 + (b1 - b0) * 0.5, b1, "A node lights up while the lab is running that step."])
        cap.append([T["collapse"][0], T["icons"][1], "From here on each node is an icon, lit while its step runs."])
        cap.sort(key=lambda r: r[0])
        lane_end = {c: T[c][1] for c in D.CAMPAIGNS}
        out = []
        for j, (a_, b_, s_) in enumerate(cap):
            if b_ is None:                               # a lane caption runs to the next caption or its lane's end
                nxt = cap[j + 1][0] if j + 1 < len(cap) else self.DURATION
                lane = "flaime_al" if a_ < T["onr_cu"][0] else "onr_cu"
                b_ = min(nxt, lane_end[lane] + 0.3)
            elif j > 0 and j + 1 < len(cap):
                b_ = min(b_, cap[j + 1][0])
            out.append((round(a_, 2), round(b_, 2), s_))
        self.captions = out
        self._cap_img = {}

    # ------------------------------------------------------------------------------------------ cards
    @lru_cache(maxsize=64)
    def _card_img(self, c: str, i: int, lit: bool = False) -> Image.Image:
        n = self.nodes[c][i]
        x, y, w, h = self.card[c][i]
        w, h = int(round(w)), int(round(h))
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        col = CAMP[c]
        edge = col if lit else CARD_EDGE
        fill = mix(CARD_FILL, col, 0.16) if lit else CARD_FILL
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=12, fill=fill + (255,), outline=edge + (255,),
                            width=3 if lit else 2)
        d.rounded_rectangle((0, 0, w - 1, 10), radius=6, fill=col + (255,))
        d.rectangle((0, 6, w - 1, 9), fill=fill + (255,))
        d.line((2, 6, w - 3, 6), fill=col + (255,), width=1)
        pad = 12
        yy = 16
        for j, (ln, dot) in enumerate(self._tag_lines(c, n, w)):
            if j == 0:
                d.text((pad, yy), ln, font=font(16, cond=True), fill=INK2 + (255,))
                yy += 22
            else:
                if j == 1:
                    d.ellipse((pad, yy + 5, pad + 8, yy + 13), fill=dot + (255,))
                d.text((pad + 13, yy), ln, font=font(14, cond=True), fill=INK2 + (255,))
                yy += 19
        th = self.thumbs.get((c, n["key"]))
        fb, size = self._title_font(w, n["title"])
        for s in St.wrap(n["title"], fb, w - 2 * pad)[:3]:
            d.text((pad, yy), s, font=fb, fill=INK + (255,))
            yy += size + 5
        yy += 4
        fm = self._meas_font(w)
        lines = St.wrap(_nbsp(n["meas"]), fm, w - 2 * pad)
        room = int((h - yy - 8) // 24)
        if len(lines) > room:
            lines = lines[:max(1, room)]
            lines[-1] = lines[-1].rstrip(",;") + "..."
        for s in lines:
            d.text((pad, yy), s, font=fm, fill=INK2 + (255,))
            yy += 24
        if th is not None and yy < h - 40:
            try:
                ti = Image.open(th).convert("RGBA")
                ti.thumbnail((w - 2 * pad, h - yy - 10), Image.LANCZOS)
                im.alpha_composite(ti, (pad + (w - 2 * pad - ti.width) // 2, h - ti.height - 8))
            except Exception:                                # noqa: BLE001
                pass
        return im

    def _arrow(self, d, p0, p1, col, width=3, head=True):
        d.line([p0, p1], fill=col, width=width)
        if head:
            ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
            L, a = 11, math.radians(28)
            pts = [p1, (p1[0] - L * math.cos(ang - a), p1[1] - L * math.sin(ang - a)),
                   (p1[0] - L * math.cos(ang + a), p1[1] - L * math.sin(ang + a))]
            d.polygon(pts, fill=col)

    def _edge_pts(self, c, a, b):
        """The straight edge between adjacent cards a -> b (indices), right edge to left edge at mid-height."""
        xa, ya, wa, ha = self.card[c][a]
        xb, yb, wb, hb = self.card[c][b]
        return (xa + wa + 2, ya + ha / 2), (xb - 3, yb + hb / 2)

    def _skip_pts(self, c, a, b, n=40):
        xa, ya, wa, ha = self.card[c][a]
        xb, yb, wb, hb = self.card[c][b]
        x0, x1 = xa + wa / 2, xb + wb / 2
        y0 = ya + ha + 2
        sag = 30 if c == "flaime_al" else 16
        return [(x0 + (x1 - x0) * s, y0 + sag * math.sin(math.pi * s)) for s in np.linspace(0, 1, n)]

    # ------------------------------------------------------------------------------------------ static layers
    def _header(self, d, alpha=1.0):
        f = font(34, bold=True)
        d.text((MARGIN, 30), "Two campaigns, one lab: the function networks", font=f, fill=mix(BG, INK, alpha))

    def _lane_label(self, d, c, a=1.0):
        L = LANE[c]
        y = L["label_y"]
        d.rounded_rectangle((MARGIN, y + 3, MARGIN + 8, y + 31), radius=3, fill=mix(BG, CAMP[c], a))
        d.text((MARGIN + 20, y), St.CAMP_NAME[c], font=font(26, bold=True), fill=mix(BG, INK, a))
        w0 = St.text_w(font(26, bold=True), St.CAMP_NAME[c])
        d.text((MARGIN + 34 + w0, y + 5), St.CAMP_LONG[c].split(": ", 1)[-1], font=font(21), fill=mix(BG, INK2, a))

    def _static(self, n_done: dict, lit_cards=frozenset()) -> np.ndarray:
        """The build's background: header, lane labels, the cards built so far and their edges."""
        key = ("static", n_done["flaime_al"], n_done["onr_cu"], lit_cards)
        if key in self._cache:
            return self._cache[key]
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        self._header(d)
        for c in D.CAMPAIGNS:
            k = n_done[c]
            if k <= 0:
                continue
            self._lane_label(d, c)
            for a, b in self.edges[c]:
                ia, ib = self.idx[c][a], self.idx[c][b]
                if ia >= k or ib >= k:
                    continue
                if abs(ib - ia) == 1:
                    p0, p1 = self._edge_pts(c, ia, ib)
                    self._arrow(d, p0, p1, RULE)
                else:
                    St.dashed_line(d, self._skip_pts(c, ia, ib), RULE, width=2, dash=9, gap=7)
            for i in range(k):
                x, y, w, h = self.card[c][i]
                im.paste(self._card_img(c, i, (c, i) in lit_cards), (int(round(x)), int(round(y))),
                         self._card_img(c, i, (c, i) in lit_cards))
        arr = np.asarray(im).copy()
        if len(self._cache) > 24:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = arr
        return arr

    def _caption_img(self, s: str) -> Image.Image:
        if s not in self._cap_img:
            f = font(27)
            lines = St.wrap(s, f, W - 2 * MARGIN - 40)[:2]
            hh = 36 * len(lines) + 8
            im = Image.new("RGBA", (W, hh), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            for j, ln in enumerate(lines):
                d.text((W // 2, 4 + 36 * j), ln, font=f, fill=INK + (255,), anchor="ma")
            self._cap_img[s] = im
        return self._cap_img[s]

    def _draw_captions(self, frame: np.ndarray, t: float):
        for t0, t1, s in self.captions:
            if t0 <= t <= t1 and s != self.captions[0][2] and s not in self._mid_caps:
                a = St.window(t, t0, t1, 0.45)
                img = self._caption_img(s)
                y = CAP_Y if img.height < 50 else CAP_Y - 18
                St.paste(frame, img, 0, y, a)

    # ------------------------------------------------------------------------------------------ the intro
    def intro_frame(self, t: float) -> np.ndarray:
        T = self.T
        t = max(0.0, min(t, self.DURATION))
        if t < T["title"][1]:
            return self._title(t)
        if t < T["both"][0]:
            fr = self._build(t)
        elif t < T["both"][1]:
            fr = self._both(t)
        elif t < T["collapse"][1]:
            fr = self._collapse(t)
        elif t < T["icons"][1]:
            fr = self._icons(t)
        else:
            return self._dock(t)
        self._draw_captions(fr, t)
        return fr

    def _title(self, t):
        T0, T1 = self.T["title"]
        fr = _bg()
        im = Image.fromarray(fr)
        d = ImageDraw.Draw(im)
        a = St.ramp(t, 0.2, 1.2)
        mv = St.ramp(t, T1 - 1.3, T1 - 0.1)              # the title rises into the header
        f_big = font(56 + (34 - 56) * mv, bold=True)
        s = "Two campaigns, one lab: the function networks"
        tw = St.text_w(f_big, s)
        x = (W - tw) / 2 + ((MARGIN) - (W - tw) / 2) * mv
        y = 440 + (30 - 440) * mv
        d.text((x, y), s, font=f_big, fill=mix(BG, INK, a))
        sub = "Each campaign is a network of models and measurements. Each node is a step the lab runs."
        a2 = St.ramp(t, 1.0, 2.0) * (1 - St.ramp(t, T1 - 1.6, T1 - 0.9))
        f2 = font(28)
        d.text(((W - St.text_w(f2, sub)) / 2, 540), sub, font=f2, fill=mix(BG, INK2, a2))
        return np.asarray(im).copy()

    def _build(self, t):
        nt = self.node_t
        n_done = {}
        cur = {}
        for c in D.CAMPAIGNS:
            k = 0
            for i, n in enumerate(self.nodes[c]):
                t0 = nt[(c, n["key"])]
                if t >= t0 + 0.75:
                    k = i + 1
                elif t >= t0:
                    cur[c] = (i, (t - t0) / 0.75)
            n_done[c] = k
        fr = self._static(n_done).copy()
        im = None
        for c in D.CAMPAIGNS:
            l0 = self.T[c][0]
            if n_done[c] == 0 and t >= l0:
                im = im or Image.fromarray(fr)
                self._lane_label(ImageDraw.Draw(im), c, ease((t - l0) / 0.8))
        for c, (i, u) in cur.items():
            # the lane label fades in with the first card; the edge from the card before it draws in first
            im = im or Image.fromarray(fr)
            d = ImageDraw.Draw(im)
            pass
            key = self.nodes[c][i]["key"]
            for a, b in self.edges[c]:
                ia, ib = self.idx[c][a], self.idx[c][b]
                if max(ia, ib) != i or min(ia, ib) >= n_done[c] + (0 if min(ia, ib) < i else 1):
                    continue
                ue = ease(min(1.0, u / 0.45))
                if abs(ib - ia) == 1:
                    p0, p1 = self._edge_pts(c, min(ia, ib), max(ia, ib))
                    p1u = (p0[0] + (p1[0] - p0[0]) * ue, p0[1] + (p1[1] - p0[1]) * ue)
                    self._arrow(d, p0, p1u, RULE, head=ue > 0.95)
                else:
                    pts = self._skip_pts(c, min(ia, ib), max(ia, ib))
                    St.dashed_line(d, pts[:max(2, int(len(pts) * ue))], RULE, width=2, dash=9, gap=7)
            ua = ease_out(max(0.0, (u - 0.3) / 0.7))
            if ua > 0:
                card = self._card_img(c, i)
                x, y, w, h = self.card[c][i]
                sc = 0.86 + 0.14 * ua
                cw, ch = max(1, int(card.width * sc)), max(1, int(card.height * sc))
                cs = card.resize((cw, ch), Image.BILINEAR)
                if ua < 0.999:
                    a = cs.getchannel("A").point(lambda v, k=ua: int(v * k))
                    cs.putalpha(a)
                im.paste(cs, (int(x + (card.width - cw) / 2), int(y + (card.height - ch) / 2)), cs)
        if im is not None:
            fr = np.asarray(im).copy()
        # pops
        for (c, key), (p0, p1) in self.pop_t.items():
            if p0 <= t <= p1:
                self._draw_pop(fr, c, key, t, p0, p1)
        return fr

    def _pop_place(self, c, key, img):
        i = self.idx[c][key]
        x, y, w, h = self.card[c][i]
        cx = x + w / 2
        px_ = int(min(max(cx - img.width / 2, MARGIN), W - MARGIN - img.width))
        top, bot = self.pop_box[c]
        if c == "flaime_al":
            py = top
            anchor = (cx, y + h + 2)
            tip = (cx if px_ <= cx <= px_ + img.width else px_ + img.width / 2, py)
        else:
            py = bot - img.height
            anchor = (cx, y - 2)
            tip = (cx if px_ <= cx <= px_ + img.width else px_ + img.width / 2, py + img.height)
        return px_, py, anchor, tip

    def _draw_pop(self, fr, c, key, t, p0, p1):
        img = self.pop_img[(c, key)]
        px_, py, anchor, tip = self._pop_place(c, key, img)
        grow = ease_out((t - p0) / 0.45)
        shrink = ease(max(0.0, (t - (p1 - 0.45)) / 0.45))
        s = max(0.04, grow * (1 - shrink))
        a = min(1.0, grow * 1.5) * (1 - shrink)
        # leader line, then the card scaled about its anchor end
        im = Image.fromarray(fr)
        d = ImageDraw.Draw(im)
        lt = (anchor[0] + (tip[0] - anchor[0]) * min(1, grow * 1.3), anchor[1] + (tip[1] - anchor[1]) * min(1, grow * 1.3))
        d.line([anchor, lt], fill=mix(BG, CAMP[c], a), width=3)
        d.ellipse((anchor[0] - 5, anchor[1] - 5, anchor[0] + 5, anchor[1] + 5), fill=mix(BG, CAMP[c], a))
        cw, ch = max(2, int(img.width * s)), max(2, int(img.height * s))
        sm = img.resize((cw, ch), Image.BILINEAR) if s < 0.999 else img
        # the card grows out of its leader's tip
        cx = tip[0] + (px_ + img.width / 2 - tip[0]) * s
        cy = py + img.height / 2
        cy = tip[1] + (cy - tip[1]) * s
        if a < 0.999:
            al = sm.getchannel("A").point(lambda v, k=a: int(v * k))
            sm = sm.copy()
            sm.putalpha(al)
        im.paste(sm, (int(cx - cw / 2), int(cy - ch / 2)), sm)
        fr[:] = np.asarray(im)

    def _both(self, t):
        """Both lanes; the stations they share in between; then a pulse runs along each network to show what
        'lit' will mean."""
        b0, b1 = self.T["both"]
        n_all = {c: len(self.nodes[c]) for c in D.CAMPAIGNS}
        u = (t - b0) / max(1e-6, b1 - b0)
        lit = set()
        if u > 0.5:
            v = (u - 0.5) / 0.5
            for c in D.CAMPAIGNS:
                pos = v * (n_all[c] + 1.5) - 0.5
                for i in range(n_all[c]):
                    if abs(pos - i) < 0.75:
                        lit.add((c, i))
        fr = self._static(n_all, frozenset(lit)).copy()
        a = St.window(t, b0, b0 + (b1 - b0) * 0.5, 0.6)
        if a > 0.01:
            St.paste(fr, self._shared_layer(), 0, 0, a)
        return fr

    SHARED = [("one atomizer", "powder", "powder"), ("one SEM", "section", "section")]

    def _shared_layer(self):
        """Mid-screen: 'both at once, one lab', and chips for the stations the two networks share, joined to the
        nodes that use them in each."""
        if "shared" in self._cache:
            return self._cache["shared"]
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        f_bot = LANE["flaime_al"]["top"] + LANE["flaime_al"]["h"]
        o_top = LANE["onr_cu"]["top"]
        mid = (f_bot + LANE["onr_cu"]["label_y"]) / 2
        fs = font(34, bold=True)
        s1 = "Both campaigns run at once, in one lab"
        xs = W - MARGIN - St.text_w(fs, s1)
        d.text((xs, mid - 46), s1, font=fs, fill=INK + (255,))
        fc = font(23)
        line_c = (118, 122, 130, 255)
        for label, kf, ko in self.SHARED:
            if kf not in self.idx["flaime_al"] or ko not in self.idx["onr_cu"]:
                continue
            xf, yf, wf, hf = self.card["flaime_al"][self.idx["flaime_al"][kf]]
            xo, yo, wo, ho = self.card["onr_cu"][self.idx["onr_cu"][ko]]
            cxf, cxo = xf + wf / 2, xo + wo / 2
            cx = (cxf + cxo) / 2
            tw = St.text_w(fc, label)
            bx0, by0, bx1, by1 = cx - tw / 2 - 16, mid - 4, cx + tw / 2 + 16, mid + 36
            for (x0, y0, x1, y1) in (((cxf, f_bot + 4, cx, by0)), ((cx, by1, cxo, o_top - 4))):
                St.dashed_line(d, [(x0, y0), (x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2), (x1, y1)], line_c, width=2,
                               dash=8, gap=6)
            d.rounded_rectangle((bx0, by0, bx1, by1), radius=18, fill=(30, 34, 42, 255), outline=(150, 154, 160, 255),
                                width=2)
            d.text((cx, by0 + 7), label, font=fc, fill=INK + (255,), anchor="ma")
        for j, s2 in enumerate(("They share the atomizer and the SEM, and also the outside",
                                "facilities, the feedstock market and the calendar.")):
            d.text((xs, mid + 8 + 32 * j), s2, font=font(23), fill=INK2 + (255,))
        self._cache["shared"] = np.asarray(im).copy()
        return self._cache["shared"]

    # ------------------------------------------------------------------------------------------ icons
    def _icon_sprite(self, c, i, r, lit=0.0, label=True, phase=0):
        """An icon (circle + pictogram) of radius r: unlit, or lit at intensity `lit` (quantized), with a ring."""
        q = int(round(lit * 4))
        key = (c, i, int(round(r * 4)), q, phase)
        if key in self._sprites:
            return self._sprites[key]
        n = self.nodes[c][i]
        pad = int(r * 0.6) + 4
        size = int(2 * (r + pad))
        k = 3
        big = Image.new("RGBA", (size * k, size * k), (0, 0, 0, 0))
        d = ImageDraw.Draw(big)
        cc = size * k / 2
        R = r * k
        col = CAMP[c]
        if q > 0:
            I = q / 4
            glow = Image.new("RGBA", big.size, (0, 0, 0, 0))
            dg = ImageDraw.Draw(glow)
            gr = R * (1.35 + 0.08 * phase)
            dg.ellipse((cc - gr, cc - gr, cc + gr, cc + gr), fill=col + (int(150 * I),))
            glow = glow.filter(ImageFilter.GaussianBlur(R * 0.22))
            big.alpha_composite(glow)
            rr = R * (1.18 + 0.06 * phase)
            d.ellipse((cc - rr, cc - rr, cc + rr, cc + rr), outline=col + (int(255 * I),), width=max(2, int(k * r / 9)))
            fill = mix(ICON_FILL, col, 0.35 + 0.65 * I)
            d.ellipse((cc - R, cc - R, cc + R, cc + R), fill=fill + (255,), outline=col + (255,), width=max(2, k * 2))
            pc = INK
        else:
            d.ellipse((cc - R, cc - R, cc + R, cc + R), fill=ICON_FILL + (255,), outline=ICON_EDGE + (255,),
                      width=max(2, int(k * 1.5)))
            pc = INK2
        sp = big.resize((size, size), Image.LANCZOS)
        pg = pictogram(_icon_kind(n), int(r * 1.25), pc, self.base_el[c])
        sp.alpha_composite(pg, ((size - pg.width) // 2, (size - pg.height) // 2))
        self._sprites[key] = (sp, pad)
        return self._sprites[key]

    def _icon_layer(self, rect, panel_alpha=0.0, labels=1.0) -> Image.Image:
        """The mini-DAG drawn to fill rect (x, y, w, h), as an RGBA image of rect's size, unlit."""
        x0, y0, w, h = rect
        k = w / DOCK[2]
        im = Image.new("RGBA", (int(round(w)), int(round(h))), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if panel_alpha > 0:
            d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=int(12 * k),
                                fill=PANEL_FILL + (int(255 * panel_alpha),), outline=(70, 74, 82, int(255 * panel_alpha)),
                                width=max(1, int(round(k))))
        for c in D.CAMPAIGNS:
            cy = OV_ROW_Y[c] * k
            d.rounded_rectangle((14 * k, cy - 26 * k, 20 * k, cy + 26 * k), radius=int(3 * k), fill=CAMP[c] + (255,))
            d.text((28 * k, cy - 22 * k), St.CAMP_NAME[c], font=font(17 * k, bold=True), fill=INK + (255,))
            d.text((28 * k, cy + 1 * k), St.CAMP_SHORT[c], font=font(14 * k, cond=True), fill=INK2 + (255,))
            pts = [self.icon_at(c, i, (0, 0, w, h)) for i in range(len(self.nodes[c]))]
            for a, b in self.edges[c]:
                ia, ib = self.idx[c][a], self.idx[c][b]
                if abs(ia - ib) != 1:
                    continue
                (xa, ya, r), (xb, yb, _) = pts[min(ia, ib)], pts[max(ia, ib)]
                d.line([(xa + r + 3 * k, ya), (xb - r - 3 * k, yb)], fill=(96, 100, 108, 255), width=max(1, int(round(1.6 * k))))
            for i, (cx, cy_, r) in enumerate(pts):
                sp, pad = self._icon_sprite(c, i, r)
                im.alpha_composite(sp, (int(round(cx - r - pad)), int(round(cy_ - r - pad))))
                if labels > 0:
                    s = _short(self.nodes[c][i])
                    fs = 14 * k
                    room = (OV_X1 - OV_X0) / max(1, len(pts) - 1) * k - 4 * k
                    f = font(fs / St.S, cond=True)
                    while St.text_w(f, s) > room and fs > 13 * k:
                        fs -= 0.5
                        f = font(fs / St.S, cond=True)
                    d.text((cx, cy_ + r + 3 * k), s, font=f, fill=INK2 + (int(255 * labels),), anchor="ma")
        return im

    def overlay_base(self, alpha: float = 0.82) -> Image.Image:
        key = round(alpha, 3)
        if key not in self._ov_base:
            self._ov_base[key] = self._icon_layer((0, 0, DOCK[2], DOCK[3]), panel_alpha=alpha)
        return self._ov_base[key]

    @staticmethod
    def intensity(count) -> float:
        """A node's glow from Replay.lit's count of its events running."""
        return 0.0 if not count else min(1.0, 0.45 + 0.55 * min(1.0, count / 3.0))

    def overlay(self, lit: dict | None = None, alpha: float = 0.82, t: float | None = None) -> Image.Image:
        """The docked mini-DAG (820 x 200 RGBA) with lit[(campaign, node)] (0..1, or a count) glowing."""
        base = self.overlay_base(alpha)
        if not lit:
            return base
        im = base.copy()
        phase = 0 if t is None else int((t * 5) % 6)
        phase = min(phase, 6 - phase) if phase else 0
        d = None
        for (c, key), v in lit.items():
            c, key = str(c), str(key)
            if c not in self.idx or key not in self.idx[c]:
                continue
            v = float(v)
            if v > 1.0:
                v = self.intensity(v)
            if v <= 0.05:
                continue
            i = self.idx[c][key]
            cx, cy, r = self.icon_at(c, i, (0, 0, DOCK[2], DOCK[3]))
            sp, pad = self._icon_sprite(c, i, r, v, phase=phase)
            im.alpha_composite(sp, (int(round(cx - r - pad)), int(round(cy - r - pad))))
            d = d or ImageDraw.Draw(im)
            n = len(self.nodes[c])
            s = _short(self.nodes[c][i])
            fs = 14.0
            room = (OV_X1 - OV_X0) / max(1, n - 1) - 4
            f = font(fs, cond=True)
            while St.text_w(f, s) > room and fs > 13:
                fs -= 0.5
                f = font(fs, cond=True)
            d.text((cx, cy + r + 3), s, font=f, fill=INK + (255,), anchor="ma")
        return im

    def _full_icon_img(self):
        if self._full_icons is None:
            self._full_icons = self._icon_layer(FULL_ICON_RECT, panel_alpha=0.0)
        return self._full_icons

    def _collapse(self, t):
        c0, c1 = self.T["collapse"]
        u = (t - c0) / (c1 - c0)
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im)
        self._header(d)
        for c in D.CAMPAIGNS:
            self._lane_label(d, c, 1 - ease(u / 0.35))
        rects = {}
        n_all = {c: len(self.nodes[c]) for c in D.CAMPAIGNS}
        for c in D.CAMPAIGNS:
            for i in range(n_all[c]):
                stag = 0.0
                m = ease((u - 0.25 - stag) / 0.45)
                x, y, w, h = self.card[c][i]
                cx, cy, r = self.icon_at(c, i, FULL_ICON_RECT)
                tx, ty, tw_, th_ = cx - r, cy - r, 2 * r, 2 * r
                rects[(c, i)] = (x + (tx - x) * m, y + (ty - y) * m, w + (tw_ - w) * m, h + (th_ - h) * m, m, r)
        # edges between the shapes' current centres
        for c in D.CAMPAIGNS:
            for a, b in self.edges[c]:
                ia, ib = self.idx[c][a], self.idx[c][b]
                if abs(ia - ib) != 1:
                    continue
                ia, ib = min(ia, ib), max(ia, ib)
                xa, ya, wa, ha, ma, _ = rects[(c, ia)]
                xb, yb, wb, hb, mb, _ = rects[(c, ib)]
                p0 = (xa + wa + 2, ya + ha / 2)
                p1 = (xb - 3, yb + hb / 2)
                self._arrow(d, p0, p1, RULE if max(ma, mb) < 0.9 else (96, 100, 108), width=3 if ma < 0.5 else 2,
                            head=ma < 0.5)
        for c in D.CAMPAIGNS:
            for i in range(n_all[c]):
                x, y, w, h, m, r = rects[(c, i)]
                text_a = 1 - ease(u / 0.3)
                if text_a > 0.01 and m < 0.02:
                    card = self._card_img(c, i)
                    if text_a < 0.999:
                        card = card.copy()
                        card.putalpha(card.getchannel("A").point(lambda v, k=text_a: int(v * k)))
                    # the bare card under the fading text
                    d.rounded_rectangle((x, y, x + w, y + h), radius=12, fill=CARD_FILL, outline=CARD_EDGE, width=2)
                    im.paste(card, (int(round(x)), int(round(y))), card)
                else:
                    rad = 12 + (min(w, h) / 2 - 12) * m
                    fill = mix(CARD_FILL, ICON_FILL, m)
                    edge = mix(CARD_EDGE, ICON_EDGE, m)
                    d.rounded_rectangle((x, y, x + w, y + h), radius=max(2, rad), fill=fill, outline=edge,
                                        width=2)
                    if m < 0.15:
                        d.rounded_rectangle((x, y, x + w, y + min(10, h / 4)), radius=max(2, min(6, rad)),
                                            fill=mix(CAMP[c], fill, m / 0.15))
                pa = ease((m - 0.6) / 0.4)
                if pa > 0.01:
                    pg = pictogram(_icon_kind(self.nodes[c][i]), int(r * 1.25), INK2, self.base_el[c])
                    if pa < 0.999:
                        pg.putalpha(pg.getchannel("A").point(lambda v, k=pa: int(v * k)))
                    cx, cy = x + w / 2, y + h / 2
                    im.paste(pg, (int(round(cx - pg.width / 2)), int(round(cy - pg.height / 2))), pg)
        # the row labels and node labels of the icon view fade in at the end
        la = ease((u - 0.8) / 0.2)
        fr = np.asarray(im).copy()
        if la > 0.01:
            full = self._full_icon_img()
            # only its text and row bars: paste the whole layer faded (its icons sit where the shapes have arrived)
            St.paste(fr, np.asarray(full), FULL_ICON_RECT[0], FULL_ICON_RECT[1], la)
        return fr

    def _icons(self, t):
        fr = self._header_frame().copy()
        St.paste(fr, np.asarray(self._full_icon_img()), FULL_ICON_RECT[0], FULL_ICON_RECT[1])
        return fr

    def _header_frame(self):
        if "header" not in self._cache:
            im = Image.new("RGB", (W, H), BG)
            self._header(ImageDraw.Draw(im))
            self._cache["header"] = np.asarray(im).copy()
        return self._cache["header"]

    def _header_layer(self):
        if "header_rgba" not in self._cache:
            im = Image.new("RGBA", (1200, 80), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.text((MARGIN, 30), "Two campaigns, one lab: the function networks", font=font(34, bold=True),
                   fill=INK + (255,))
            self._cache["header_rgba"] = np.asarray(im).copy()
        return self._cache["header_rgba"]

    def _dock(self, t):
        d0, d1 = self.T["dock"]
        u = ease((t - d0) / (d1 - d0))
        fx, fy, fw, fh = FULL_ICON_RECT
        dx, dy, dw, dh = DOCK
        x, y, w, h = fx + (dx - fx) * u, fy + (dy - fy) * u, fw + (dw - fw) * u, fh + (dh - fh) * u
        fr = _bg()
        ha = 1 - ease(min(1.0, (t - d0) / 1.2))
        if ha > 0.01:
            St.paste(fr, self._header_layer(), 0, 0, ha)
        iw, ih = max(2, int(round(w))), max(2, int(round(h)))
        xx, yy = int(round(x)), int(round(y))
        if t >= d1 - 1e-6:
            St.paste(fr, np.asarray(self.overlay_base()), dx, dy)
            return fr
        full = self._full_icon_img()
        # the full-screen icons, shrinking; the overlay itself (panel and all) fades in over the last 40 %
        xf = ease((u - 0.6) / 0.4)
        if xf < 0.999:
            sm = full.resize((iw, ih), Image.BILINEAR)
            St.paste(fr, np.asarray(sm), xx, yy, 1 - xf)
        if xf > 0.001:
            ov = self.overlay_base()
            om = ov if (iw, ih) == ov.size else ov.resize((iw, ih), Image.BILINEAR)
            St.paste(fr, np.asarray(om), xx, yy, xf)
        return fr


# ------------------------------------------------------------------------------------------------- self-test
def _stills():
    import subprocess
    out = Path("/tmp/vid")
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    dag = Dag()
    print(f"Dag() {time.time() - t0:.2f} s; DURATION {dag.DURATION:.1f} s; pops "
          f"{ {c: [k for k, _ in dag.pops[c]] for c in D.CAMPAIGNS} }")
    for c0, c1, s in dag.captions:
        print(f"  {c0:6.1f}-{c1:6.1f}  {s}")
    T = dag.T
    picks = {"a_title": 1.5, "b_title_move": T["title"][1] - 0.4}
    fl = [k for k, _ in dag.pops["flaime_al"]]
    if fl:
        p0, p1 = dag.pop_t[("flaime_al", fl[0])]
        picks["c_flaime_pop"] = p0 + 2.0
    picks["d_flaime_done"] = T["flaime_al"][1] - 0.2
    on = [k for k, _ in dag.pops["onr_cu"]]
    if on:
        p0, p1 = dag.pop_t[("onr_cu", on[0])]
        picks["e_onr_pop"] = p0 + 2.0
    picks["f_onr_mid"] = dag.node_t[("onr_cu", dag.nodes["onr_cu"][5]["key"])] + 0.4
    picks["g_both"] = T["both"][0] + 0.8 * (T["both"][1] - T["both"][0])
    picks["h_collapse"] = T["collapse"][0] + 0.55 * (T["collapse"][1] - T["collapse"][0])
    picks["i_icons"] = T["icons"][0] + 1.0
    picks["j_dock"] = T["dock"][0] + 2.0
    picks["k_end"] = dag.DURATION
    times = []
    for name, tt in picks.items():
        a = time.time()
        fr = dag.intro_frame(tt)
        times.append(time.time() - a)
        Image.fromarray(fr).save(out / f"dag_{name}.png")
    print("first-frame times (s):", [round(x, 3) for x in times])
    # steady-state timing over a second of the build and of the collapse
    for name, (a_, b_) in (("build", (T["flaime_al"][0] + 3, T["flaime_al"][0] + 5)),
                           ("collapse", (T["collapse"][0] + 2, T["collapse"][0] + 4)),
                           ("dock", (T["dock"][0], T["dock"][1]))):
        ts = np.arange(a_, b_, 1 / 30)
        a = time.time()
        for tt in ts:
            dag.intro_frame(tt)
        print(f"{name}: {1000 * (time.time() - a) / len(ts):.1f} ms a frame")
    # the overlay on footage
    src = D.HERE / "out" / "hd" / "alloy_atomize.mp4"
    bg = out / "dag_bg_atomize.png"
    if not bg.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "60", "-i", str(src), "-vframes", "1", str(bg)],
                       check=True)
    R = D.Replay()
    lit = R.lit(24 * 30, 24)
    lit2 = {k: Dag.intensity(v) for k, v in lit.items()}
    lit2[("onr_cu", "screen")] = 0.6
    lit2[("flaime_al", "print")] = 1.0
    a = time.time()
    for k in range(60):
        ov = dag.overlay(lit2, t=k / 30)
    print(f"overlay: {1000 * (time.time() - a) / 60:.2f} ms a call; lit {lit}")
    fr = np.asarray(Image.open(bg).convert("RGB")).copy()
    St.paste(fr, np.asarray(ov), DOCK[0], DOCK[1])
    Image.fromarray(fr).save(out / "dag_overlay_on_footage.png")
    big = dag.overlay(lit2, t=0.2).resize((DOCK[2] * 2, DOCK[3] * 2), Image.NEAREST)
    canvas = Image.new("RGB", big.size, (60, 60, 60))
    canvas.paste(big, (0, 0), big)
    canvas.save(out / "dag_overlay_zoom.png")
    # the dock's last frame against overlay() on BG: identical?
    end = dag.intro_frame(dag.DURATION)
    ref = St.blank(BG)
    St.paste(ref, np.asarray(dag.overlay({})), DOCK[0], DOCK[1])
    print("dock end == overlay on BG:", bool((end == ref).all()))


if __name__ == "__main__":
    _stills()
