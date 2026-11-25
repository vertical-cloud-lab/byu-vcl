"""The whole lab from above, lit by the event log: a still rendered once (birdseye_render.py, no data in it) with a slow
Ken Burns crop, and 2-D beacons on every station the replayed run is using.

    from twin.video import data as D, birdseye as B
    be = B.Birdseye(D.Replay())
    foc = be.best_focus("high", 1.2)                         # keeps the stations out of the other panels' boxes
    img = be.frame(t_h=24 * 120, span_h=24, view="high", zoom=1.2, focus=foc)   # (1080, 1920, 3) uint8

Views (out/twin2/video/birdseye/<view>.png, 2880 x 1620, so zoom 1.5 is a 1:1 crop and zoom 1 a shrink): "high" (the
whole floor from the south, high), "sw" and "se" (obliques from the south-west and south-east), "plan" (nearly top-down;
every station clear of the other panels at zoom 1).

* A floor station busy over [t_h - span_h, t_h] gets a glowing disc in its campaign's colour (split when both
  campaigns use it), larger and brighter with its occupancy (sqrt, four levels), and a short label placed clear of the
  other labels, the beacons and the other panels' boxes (AVOID). A station the run uses but not now: a small grey dot.
* Tray stations are a column of lettered chips standing in their Shuttle's tower (lowest slot nearest the opening): a
  chip glows in the campaign colour while a station on that tray works, labelled "tray D: SEM, XRD".
* The cloud (HPC) and every outside facility (external=True in the event log) are an OFF SITE column at the left edge.
* A legend (FLAIME, ONR, idle) at the bottom centre, between the DAG and plot panels.

Station -> anchor is STATION_ANCHOR (twin/facility.py keys -> the stills' anchors); the stills' JSON also carries the
world -> clip matrix, so new anchors can be projected without another render.

    python -m twin.video.birdseye test        # test frames -> /tmp/vid/birdseye_*.png and the cost a frame
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from . import style as S

HERE = Path(__file__).resolve().parents[2]
BDIR = HERE / "out" / "twin2" / "video" / "birdseye"

# twin station key -> (anchor key(s) in <view>.json, in order of preference; short label)
STATION_ANCHOR = {
    "atomizer": (("repowder",), "atomizer"),
    "sieve": (("sieve_cell",), "sieving"),
    "utah_midi": (("aconity",), "LPBF (Aconity MIDI)"),
    "edm": (("wire_edm",), "wire EDM"),
    "tensile": (("instron_small",), "tensile"),
    "tensile_hot": (("instron_floor",), "tensile at 250 C"),
    "utah_mxlab": (("ded",), "DED (MX-Lab)"),
    "byu_icpms": (("icpms", "icp_ms", "icpms_station", "fumehood", "glovebox"), "ICP-MS"),
    "shop": (("machining", "machining_cell", "tray_M"), "machining"),     # the Carvera CNC on tray M
    "doser": (("tray_B",), "doser, press"),
    "psd": (("tray_E",), "particle size"),
    "byu_sem": (("tray_D",), "SEM"),
    "xrd": (("tray_D",), "XRD"),
    "xrf": (("tray_M",), "XRF"),
    "furnace": (("tray_F",), "furnace"),
    "prep": (("tray_F",), "section, mount, polish"),
    "hardness": (("tray_L",), "Vickers"),
    "nanoindent": (("tray_E",), "nanoindenter"),
    "pip": (("tray_E",), "PIP"),
    "cubxl": (("tray_A",), "corrosion (CubXL)"),
    "immersion": (("tray_A",), "immersion"),
    "density": (("tray_K",), "density, cracks"),
}
OFFSITE_NAME = {
    "hpc": "HPC: CALPHAD", "nsl": "NSL Analytical", "mines_x2": "Mines: FormAlloy X2", "valimet": "Valimet: gas atomize",
    "ames": "Ames Lab: gas atomize", "utah_midi": "Utah: Aconity MIDI", "utah_mxlab": "Utah: MX-Lab DED",
    "edm": "wire EDM (Provo)", "pip": "PIP service", "byu_icpms": "BYU ICP-MS", "byu_sem": "BYU SEM",
}
# screen boxes (x, y, w, h at 1920 x 1080) other panels use: no label or badge goes in them
AVOID = [(24, 20, 470, 118), (520, 24, 880, 60), (1446, 20, 450, 150), (1446, 186, 450, 300), (1296, 640, 600, 420),
         (24, 860, 820, 200)]
IDLE = (150, 152, 156)
LEVELS = 4                                             # sprite intensities


def _sprite(cols: list, radius: int, peak: float) -> Image.Image:
    """A glowing disc: a soft halo and a bright core in the campaign colour(s), split left/right for two."""
    R = radius
    n = 2 * R + 1
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1].astype(np.float32)
    r = np.sqrt(xx ** 2 + yy ** 2) / R
    halo = np.clip(1.0 - r, 0.0, 1.0) ** 1.35 * peak
    core = np.clip((0.40 - r) / 0.08, 0.0, 1.0)
    a = np.maximum(halo, core)
    rgb = np.zeros((n, n, 3), np.float32)
    c0 = np.array(cols[0], np.float32)
    c1 = np.array(cols[-1], np.float32)
    left = (xx < 0)[..., None]
    base = np.where(left, c0, c1)
    white = np.array((255, 255, 255), np.float32)
    k = np.clip((0.30 - r) / 0.30, 0.0, 1.0)[..., None] * 0.55          # a whitish centre, so it reads as lit
    rgb = base * (1 - k) + white * k
    ring = ((r > 0.40) & (r < 0.47))[..., None]                         # a dark rim round the core: reads on white
    rgb = np.where(ring, rgb * 0.45, rgb)
    a = np.where(ring[..., 0], np.maximum(a, 0.9), a)
    out = np.dstack([np.clip(rgb, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def _overlaps(a, b) -> bool:
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


class Birdseye:
    def __init__(self, replay, views=None):
        self.R = replay
        self.views = {}
        names = views or [p.stem for p in sorted(BDIR.glob("*.json"))]
        for nm in names:
            js = json.loads((BDIR / f"{nm}.json").read_text())
            im = Image.open(BDIR / f"{nm}.png").convert("RGB")
            self.views[nm] = dict(img=im, size=im.size, anchors=js["anchors"], boxes=js.get("boxes", {}),
                                  world=js.get("world", {}), bounds=js.get("bounds", {}))
        if not self.views:
            raise FileNotFoundError(f"no birds-eye stills in {BDIR}: run twin/video/birdseye_render.py")
        self._cache: dict = {}
        self._order: list = []
        self.sprites = {}
        cc = S.CAMP
        combos = {"flaime_al": [cc["flaime_al"]], "onr_cu": [cc["onr_cu"]],
                  "both": [cc["flaime_al"], cc["onr_cu"]]}
        for key, cols in combos.items():
            for lv in range(LEVELS):
                u = (lv + 1) / LEVELS
                self.sprites[(key, lv)] = _sprite(cols, S.px(24 + 22 * u), 0.70 + 0.30 * u)
        self.f_lab = S.font(18, bold=True)
        self.f_small = S.font(15)
        self.f_head = S.font(15, bold=True)
        self.f_chip = S.font(16, bold=True)
        self.avoid = [(S.px(x), S.px(y), S.px(x + w), S.px(y + h)) for x, y, w, h in AVOID]
        self.offsite = [k for k in self.R.stations if k == "hpc" or self.R.stations[k].get("external")
                        or k not in STATION_ANCHOR]
        self.offsite.sort(key=lambda k: (k != "hpc", k))
        # the trays the run uses, by Shuttle, lowest slot first (from the stills' world anchors)
        v0 = next(iter(self.views.values()))
        wd, bd = v0["world"], v0["bounds"]
        self.trays: dict = {1: [], 2: []}
        view0 = next(iter(self.views))
        used = set()
        for st in self.R.stations:
            if st in self.offsite:
                continue
            ak, _ = self.anchor_of(view0, st)
            if ak and ak.startswith("tray_"):
                used.add(ak[5:])
        for k in sorted(used):
            if f"tray_{k}" not in wd or "open1" not in wd or "open2" not in wd:
                continue
            x = wd[f"tray_{k}"][0]
            sh = 1 if abs(x - wd["open1"][0]) <= abs(x - wd["open2"][0]) else 2
            z = bd.get(f"slot_{k}", [0, 0, 0, 0, 0, 0])[4]
            self.trays[sh].append((z, k))
        for sh in self.trays:
            self.trays[sh] = [k for _, k in sorted(self.trays[sh])]

    # ------------------------------------------------------------------------------------------ the picture
    def crop(self, view: str, zoom: float, focus=(0.5, 0.5)) -> tuple:
        """(x0, y0, w, h) of the still shown at this zoom (1 = the whole still), centred on focus, kept inside."""
        sw, sh = self.views[view]["size"]
        z = max(1.0, float(zoom))
        w, h = sw / z, sh / z
        x0 = min(max(0.0, focus[0] * sw - w / 2), sw - w)
        y0 = min(max(0.0, focus[1] * sh - h / 2), sh - h)
        return x0, y0, w, h

    def base(self, view: str, zoom: float, focus=(0.5, 0.5)) -> Image.Image:
        zq = round(max(1.0, zoom) / 0.001) * 0.001
        fq = (round(focus[0], 3), round(focus[1], 3))
        key = (view, zq, fq)
        im = self._cache.get(key)
        if im is None:
            x0, y0, w, h = self.crop(view, zq, fq)
            src = self.views[view]["img"]
            if abs(w - S.W) < 0.5 and abs(h - S.H) < 0.5:
                im = src.crop((int(round(x0)), int(round(y0)), int(round(x0)) + S.W, int(round(y0)) + S.H))
            else:
                flt = Image.BOX if w > S.W else Image.BILINEAR          # an area filter when shrinking: 2x faster
                im = src.resize((S.W, S.H), flt, box=(x0, y0, x0 + w, y0 + h))
            self._cache[key] = im
            self._order.append(key)
            while len(self._order) > 6:
                self._cache.pop(self._order.pop(0), None)
        return im

    def to_screen(self, view: str, xy, crop) -> tuple:
        x0, y0, w, h = crop
        return (xy[0] - x0) * S.W / w, (xy[1] - y0) * S.H / h

    def anchor_of(self, view: str, station: str):
        if station not in STATION_ANCHOR:
            return None, None
        keys, _ = STATION_ANCHOR[station]
        A = self.views[view]["anchors"]
        for k in keys:
            if k in A:
                return k, A[k]
        return None, None

    # ------------------------------------------------------------------------------------------ one frame
    def frame(self, t_h: float, span_h: float = 1.0, view: str = "high", zoom: float = 1.0, focus=(0.5, 0.5),
              legend: bool = True, offsite: bool = True, labels: bool = True) -> np.ndarray:
        if view not in self.views:
            view = next(iter(self.views))
        crop = self.crop(view, zoom, focus)
        img = self.base(view, zoom, focus).copy()
        d = ImageDraw.Draw(img, "RGBA")
        busy = self.R.busy_stations(t_h, span_h)
        # floor stations grouped by anchor: one beacon per anchor, its label listing what runs there; tray stations
        # grouped by tray, drawn as a column of chips in their Shuttle's tower
        groups: dict = {}
        tray_g: dict = {}
        for st in self.R.stations:
            if st in self.offsite:
                continue
            ak, a = self.anchor_of(view, st)
            if a is None:
                continue
            tgt = tray_g if ak.startswith("tray_") else groups
            g = tgt.setdefault(ak, dict(xy=a, st=[], on=[], camps=set(), occ=0.0))
            g["st"].append(st)
            if st in busy:
                g["on"].append(st)
                camps, occ = busy[st]
                g["camps"] |= set(camps)
                g["occ"] = max(g["occ"], float(occ))
        placed = []
        lit = []
        for ak, g in groups.items():
            sx, sy = self.to_screen(view, g["xy"], crop)
            if not (-20 <= sx <= S.W + 20 and -20 <= sy <= S.H + 20):
                continue
            if not g["camps"]:
                r = S.px(6)
                d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=IDLE + (235,), outline=(40, 42, 46, 230),
                          width=max(1, S.px(2)))
                continue
            lit.append((ak, g, sx, sy))
        # lit beacons over the idle dots, the busiest last (on top)
        lit.sort(key=lambda x: x[1]["occ"])
        for ak, g, sx, sy in lit:
            self._beacon(img, g, sx, sy)
        chips = self._chips(img, d, view, crop, tray_g, placed)
        r = S.px(16)
        placed.extend((sx - r, sy - r, sx + r, sy + r) for _, _, sx, sy in lit)     # labels keep off the beacons
        if labels:
            for (x0, y0, x1, y1, txt, side) in chips:
                self._chip_label(d, txt, x0, y0, x1, y1, side, placed)
            blend = self._blend_now(t_h, span_h)
            for ak, g, sx, sy in sorted(lit, key=lambda x: -x[1]["occ"]):
                txt = self._label(ak, g)
                if blend and "utah_mxlab" in (g.get("on") or g["st"]):
                    txt += " · blend"                   # copper's blended-powder DED screens (what == blend_ded)
                self._place_label(d, txt, sx, sy, placed)
        if offsite and self.offsite:
            self._offsite(d, busy)
        if legend:
            self._legend(d)
        return np.asarray(img).copy()

    def _beacon(self, img, g, sx, sy, scale: float = 1.0):
        key = "both" if len(g["camps"]) > 1 else next(iter(g["camps"]))
        if key not in ("flaime_al", "onr_cu", "both"):
            key = "flaime_al"
        lv = min(LEVELS - 1, int(math.sqrt(max(0.0, g["occ"])) * LEVELS))   # 4 % busy is level 0, 30 % level 2
        sp = self.sprites[(key, lv)]
        if scale != 1.0:
            sp = sp.resize((max(3, int(sp.width * scale)), max(3, int(sp.height * scale))), Image.BILINEAR)
        img.paste(sp, (int(sx - sp.width / 2), int(sy - sp.height / 2)), sp)

    def _chips(self, img, d, view, crop, tray_g: dict, placed: list) -> list:
        """Each Shuttle's trays as a column of lettered chips standing in its tower, the lowest slot nearest the
        opening; a chip glows in its campaign's colour while a station on that tray works. -> the lit chips' boxes and
        labels, for _chip_label."""
        A = self.views[view]["anchors"]
        out = []
        f = self.f_chip
        cw, ch, gap = S.px(30), S.px(26), S.px(5)
        for sh, ks in self.trays.items():
            if not ks or f"open{sh}" not in A:
                continue
            bx, by = self.to_screen(view, A[f"open{sh}"], crop)
            n = len(ks)
            top = by - S.px(34) - n * (ch + gap)
            x0 = bx - cw / 2
            if not (0 <= bx <= S.W and 0 <= top and by <= S.H):
                continue
            d.rounded_rectangle((x0 - S.px(5), top - S.px(5), x0 + cw + S.px(5), by - S.px(34) + S.px(1)),
                                radius=S.px(7), fill=(18, 20, 24, 150))
            placed.append((x0 - S.px(5), top - S.px(5), x0 + cw + S.px(5), by - S.px(34)))
            for i, k in enumerate(ks):                   # lowest slot at the bottom of the column
                y1 = by - S.px(34) - i * (ch + gap)
                y0 = y1 - ch
                g = tray_g.get(f"tray_{k}")
                on = bool(g and g["camps"])
                if on:
                    cols = [S.CAMP[c] for c in ("flaime_al", "onr_cu") if c in g["camps"]] or [IDLE]
                    self._beacon(img, g, bx, (y0 + y1) / 2, scale=0.8)
                    d.rounded_rectangle((x0, y0, x0 + cw, y1), radius=S.px(5), fill=cols[0] + (235,),
                                        outline=(255, 255, 255, 220), width=max(1, S.px(2)))
                    if len(cols) > 1:
                        d.rounded_rectangle((x0 + cw / 2, y0, x0 + cw, y1), radius=S.px(5), fill=cols[1] + (235,))
                    d.text((bx, (y0 + y1) / 2), k, font=f, fill=(255, 255, 255, 255), anchor="mm",
                           stroke_width=max(1, S.px(1)), stroke_fill=(0, 0, 0, 160))
                    out.append((x0, y0, x0 + cw, y1, self._label(f"tray_{k}", g), "left" if sh == 1 else "right"))
                else:
                    d.rounded_rectangle((x0, y0, x0 + cw, y1), radius=S.px(5), fill=(70, 72, 78, 220))
                    d.text((bx, (y0 + y1) / 2), k, font=f, fill=S.INK2 + (255,), anchor="mm")
        return out

    def _chip_label(self, d, txt, x0, y0, x1, y1, side, placed):
        f = self.f_lab
        tw = S.text_w(f, txt)
        pad, th = S.px(7), S.px(24)
        cy = (y0 + y1) / 2
        for dy in (0, -th - 2, th + 2, -2 * th - 4, 2 * th + 4):
            if side == "left":
                box = (x0 - S.px(10) - tw - 2 * pad, cy - th / 2 + dy, x0 - S.px(10), cy + th / 2 + dy)
            else:
                box = (x1 + S.px(10), cy - th / 2 + dy, x1 + S.px(10) + tw + 2 * pad, cy + th / 2 + dy)
            if box[0] < 0 or box[2] > S.W:
                continue
            if not any(_overlaps(box, p) for p in placed):
                break
        else:
            return
        placed.append(box)
        d.rounded_rectangle(box, radius=S.px(6), fill=(18, 20, 24, 215))
        d.text((box[0] + pad, (box[1] + box[3]) / 2), txt, font=f, fill=S.INK + (255,), anchor="lm")

    def best_focus(self, view: str, zoom: float) -> tuple:
        """The focus (fx, fy) at this zoom that keeps the most stations of the run out of the other panels' boxes,
        nearest the middle among equals."""
        if zoom <= 1.0001:
            return (0.5, 0.5)
        A = self.views[view]["anchors"]
        pts = []
        for st in self.R.stations:
            ak, a = self.anchor_of(view, st)
            if a is not None and not ak.startswith("tray_"):
                pts.append(a)
        for sh in (1, 2):
            if f"open{sh}" in A:
                pts.append(A[f"open{sh}"])
        sw, sh = self.views[view]["size"]
        cx = float(np.mean([p[0] for p in pts])) / sw if pts else 0.5
        cy = float(np.mean([p[1] for p in pts])) / sh if pts else 0.5
        best, key = (0.5, 0.5), None
        for fx in np.linspace(0.3, 0.7, 17):
            for fy in np.linspace(0.35, 0.65, 13):
                c = self.crop(view, zoom, (fx, fy))
                bad = out = 0
                for p in pts:
                    sx, sy = self.to_screen(view, p, c)
                    if not (S.px(30) <= sx <= S.W - S.px(30) and S.px(30) <= sy <= S.H - S.px(30)):
                        out += 1
                    elif any(a[0] <= sx <= a[2] and a[1] <= sy <= a[3] for a in self.avoid):
                        bad += 1
                k = (out, bad, abs(fx - cx) + abs(fy - cy))
                if key is None or k < key:
                    best, key = (float(fx), float(fy)), k
        return best

    def _blend_now(self, t_h: float, span_h: float) -> bool:
        """Is a blended-powder DED screen (what == 'blend_ded') running on the DED machine over [t_h - span_h, t_h]?"""
        R = self.R
        return any(R.what[i] == "blend_ded" and R.station[i] == "utah_mxlab" for i in R.active(t_h, span_h))

    def _label(self, ak: str, g: dict) -> str:
        """What runs at this anchor now: 'tray D: SEM, XRD', 'atomizer'."""
        names = []
        for st in g.get("on") or g["st"]:
            nm = STATION_ANCHOR[st][1]
            if nm not in names:
                names.append(nm)
        if ak.startswith("tray_"):
            return f"tray {ak[5:]}: " + ", ".join(names)
        return ", ".join(names)

    def _place_label(self, d, txt: str, sx: float, sy: float, placed: list):
        f = self.f_lab
        tw = S.text_w(f, txt)
        th = S.px(24)
        pad = S.px(7)
        gap = S.px(26)
        cands = [(sx + gap, sy - gap - th), (sx - gap - tw - 2 * pad, sy - gap - th), (sx + gap, sy + gap * 0.6),
                 (sx - gap - tw - 2 * pad, sy + gap * 0.6), (sx - tw / 2 - pad, sy - 2.2 * gap - th),
                 (sx - tw / 2 - pad, sy + 1.6 * gap), (sx + 1.8 * gap, sy - th / 2), (sx - 1.8 * gap - tw - 2 * pad,
                                                                                        sy - th / 2)]
        best = None
        for (x, y) in cands:
            box = (x, y, x + tw + 2 * pad, y + th)
            if box[0] < S.px(8) or box[2] > S.W - S.px(8) or box[1] < S.px(8) or box[3] > S.H - S.px(8):
                continue
            bad = any(_overlaps(box, p) for p in placed) or any(_overlaps(box, a) for a in self.avoid)
            if not bad:
                best = box
                break
            if best is None:
                best = box if not any(_overlaps(box, p) for p in placed) else None
        if best is None:
            return
        x0, y0, x1, y1 = best
        placed.append(best)
        cx = min(max(sx, x0), x1)
        cy = min(max(sy, y0), y1)
        d.line([(sx, sy), (cx, cy)], fill=(20, 22, 26, 200), width=max(1, S.px(2)))
        d.rounded_rectangle(best, radius=S.px(6), fill=(18, 20, 24, 205))
        d.text((x0 + pad, (y0 + y1) / 2), txt, font=f, fill=S.INK + (255,), anchor="lm")

    def _offsite(self, d, busy: dict):
        """The cloud and the outside facilities: a column of badges at the left edge, under the clock."""
        x, y = S.px(24), S.px(158)
        f, fh = self.f_small, self.f_head
        w = S.px(250)
        rh = S.px(30)
        d.rounded_rectangle((x, y, x + w, y + S.px(28) + rh * len(self.offsite)), radius=S.px(8),
                            fill=(18, 20, 24, 200))
        d.text((x + S.px(12), y + S.px(15)), "OFF SITE", font=fh, fill=S.INK2 + (255,), anchor="lm")
        yy = y + S.px(28)
        for st in self.offsite:
            on = st in busy
            cy = yy + rh / 2
            r = S.px(8)
            if on:
                camps = busy[st][0]
                cols = [S.CAMP[c] for c in ("flaime_al", "onr_cu") if c in camps] or [IDLE]
                if len(cols) > 1:
                    d.pieslice((x + S.px(14), cy - r, x + S.px(14) + 2 * r, cy + r), 90, 270, fill=cols[0] + (255,))
                    d.pieslice((x + S.px(14), cy - r, x + S.px(14) + 2 * r, cy + r), 270, 90, fill=cols[1] + (255,))
                else:
                    d.ellipse((x + S.px(14), cy - r, x + S.px(14) + 2 * r, cy + r), fill=cols[0] + (255,))
                d.ellipse((x + S.px(14) - 3, cy - r - 3, x + S.px(14) + 2 * r + 3, cy + r + 3),
                          outline=(255, 255, 255, 120), width=max(1, S.px(2)))
            else:
                rr = S.px(5)
                d.ellipse((x + S.px(14) + r - rr, cy - rr, x + S.px(14) + r + rr, cy + rr), fill=IDLE + (230,))
            name = OFFSITE_NAME.get(st) or str(self.R.stations.get(st, {}).get("name", st)).split(" (")[0][:26]
            d.text((x + S.px(40), cy), name, font=f, fill=(S.INK if on else S.INK2) + (255,), anchor="lm")
            yy += rh

    def _legend(self, d):
        f = self.f_small
        items = [(S.CAMP["flaime_al"], "FLAIME (Al)"), (S.CAMP["onr_cu"], "ONR (Cu)"), (IDLE, "idle")]
        x, y = S.px(866), S.px(1016)
        w = sum(S.text_w(f, t) + S.px(40) for _, t in items) + S.px(16)
        d.rounded_rectangle((x, y, x + w, y + S.px(36)), radius=S.px(8), fill=(18, 20, 24, 200))
        xx = x + S.px(14)
        for col, t in items:
            r = S.px(7)
            cy = y + S.px(18)
            d.ellipse((xx, cy - r, xx + 2 * r, cy + r), fill=col + (255,))
            d.text((xx + 2 * r + S.px(8), cy), t, font=f, fill=S.INK + (255,), anchor="lm")
            xx += S.text_w(f, t) + S.px(40)


def _test():
    import time
    from . import data as D
    R = D.Replay()
    be = Birdseye(R)
    print("views", list(be.views), "offsite", be.offsite)
    shots = [(24 * 3 + 10, 24.0, "high", 1.5, None), (24 * 3.4, 24.0, "high", 1.15, None),
             (24 * 250, 72.0, "high", 1.0, None), (24 * 250, 24.0, "sw", 1.0, (0.5, 0.5)),
             (24 * 3.4, 48.0, "se", 1.1, None), (24 * 3.4, 72.0, "plan", 1.0, (0.5, 0.5))]
    for i, (t, span, v, z, foc) in enumerate(shots):
        if v not in be.views:
            continue
        foc = foc or be.best_focus(v, z)
        print(v, z, "focus", foc)
        t0 = time.time()
        a = be.frame(t, span, v, z, foc)
        dt = time.time() - t0
        Image.fromarray(a).save(f"/tmp/vid/birdseye_{i}_{v}.png")
        print(f"{i} {v} t={t / 24:.1f} d span={span} zoom={z}: {dt * 1000:.0f} ms", flush=True)
    # per-frame cost over a slow pull-back (new zoom every frame)
    t0 = time.time()
    n = 30
    for k in range(n):
        be.frame(24 * 100 + k * 2.0, 6.0, "high", 1.5 - 0.5 * k / n, (0.5, 0.5))
    print(f"pull-back: {(time.time() - t0) / n * 1000:.0f} ms a frame", flush=True)


if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "test":
        _test()
