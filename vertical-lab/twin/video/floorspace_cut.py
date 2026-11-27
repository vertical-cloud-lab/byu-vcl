"""The floor-space segment, cut: the 3-D renders (floorspace3d.py) with their overlays, the footprints side by side
(2-D, at one scale: the four layouts of today's equipment, then the Shuttles' capacity laid out flat, with the floor
machines' block apart), the narration (floorspace_voice.py), and the preview's record, contact sheet, subtitles and
YouTube metadata.

    cd vertical-lab
    python -m twin.video.floorspace_cut stills 3 27 40 48 58 70 80 90 100 112    # overlay stills -> /tmp/fscut/
    python -m twin.video.floorspace_cut final       # out/floorspace/floorspace_preview.mp4 (needs /tmp/fs3d/lab3d.mp4)
    python -m twin.video.floorspace_cut sheet       # out/floorspace/sheet.png
    python -m twin.video.floorspace_cut meta        # out/floorspace/youtube_meta.json

Reusable in a longer cut: Cut().frame(t, base) draws any moment of the segment onto a 1920 x 1080 frame (base: the 3-D
render at t, or None in the plans phase); Cut.T is its length in seconds and Cut.lines its narration with their times.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from . import floorspace as FS
from . import floorspace_story as FSS
from . import style as ST

HERE = Path(__file__).resolve().parents[2]
OUTD = HERE / "out" / "floorspace"
FPS = 30
F3D = Path(os.environ.get("FS3D_DIR", "/tmp/fs3d")) / "lab3d.mp4"
PH = FSS.PH
INK, INK2 = ST.INK, ST.INK2
DARK = (24, 26, 30)                  # ink on the light plans
DARK2 = (88, 92, 99)
PLAN_BG = (229, 229, 226)            # the 3-D ground's colour, so the cross-fade doesn't flash
COL = dict(floor_conv=(201, 207, 214), floor_vert=(209, 220, 204), wall=(58, 60, 64), corridor=(184, 192, 205),
           aisle=(240, 233, 205), mir=(244, 228, 160), bench=(190, 172, 146), shelf=(150, 156, 164),
           machine=(110, 140, 176), inst=(222, 118, 88), vlm=(74, 86, 104), dock=(30, 140, 70), charger=(120, 84, 160),
           arm=(235, 170, 40), mir1=(238, 214, 120), free=(236, 226, 210), store=(150, 156, 164))
BAR = {"floor machines": (110, 140, 176), "benches, shelves and Shuttles": (190, 152, 100),
       "service clearance": (150, 196, 160), "aisles and corridor": (236, 206, 110), "walls": (58, 60, 64),
       "other floor": (200, 200, 198)}
STAGE = {"conv": "1   Conventional lab", "flat": "2   Automated, same floor plan", "vert": "3   Vertical lab",
         "plans": "Side by side"}
ROW_A = ("conventional", "flat", "robots", "vertical")
TITLES = {"conventional": "Conventional lab", "flat": "Automated, same floor plan",
          "robots": "Automated, laid out for robots", "vertical": "Vertical lab"}


def fmt(v: float) -> str:
    return f"{v:,.0f}"


class Cut:
    T = PH["end"]

    def __init__(self):
        self.S = FSS.Story()
        js = json.loads((OUTD / "layouts.json").read_text())
        self.js = js
        self.rows = {r["name"]: r for r in js["summary"]["rows"]}
        self.counts = js["summary"]["counts"]
        sc = json.loads((Path(__file__).with_name("narration_floorspace.json")).read_text())
        rec = json.loads((OUTD / "narration" / "lines.json").read_text())["lines"]
        self.lines = [dict(ln, t0=PH[ln["phase"]] + ln["at"], t1=PH[ln["phase"]] + ln["at"] + rec[ln["id"]]["seconds"])
                      for ln in sc["lines"]]
        for a, b in zip(self.lines[:-1], self.lines[1:]):
            if b["t0"] < a["t1"] + 0.3:
                print(f"floorspace_cut: line {b['id']} starts {a['t1'] - b['t0']:.2f} s before {a['id']} ends",
                      flush=True)
        self._plan_cache: dict = {}
        self.cap = js["capacity"]
        self.rob = FS.robots(self.S.inv)
        self.capf = FS.capacity_flat(self.S.inv, self.cap["trays"]["trays"])
        self.lays = {"conventional": self.S.conv, "flat": self.S.flat, "robots": self.rob, "vertical": self.S.vert,
                     "capacity": self.capf}
        self.top = self.S.camera(PH["plans"])
        q = FSS.project(self.top, [(self.S.vert.envelope[0], self.S.vert.envelope[3], 0.0),
                                   (self.S.vert.envelope[2], self.S.vert.envelope[1], 0.0)])
        self.k_top = (q[1, 0] - q[0, 0]) / (self.S.vert.envelope[2] - self.S.vert.envelope[0])
        self.o_top = (q[0, 0], q[0, 1])

    # ------------------------------------------------------------------------------------------------ helpers
    def phase(self, t: float) -> str:
        for p in ("plans", "vert", "flat"):
            if t >= PH[p]:
                return p
        return "conv"

    @staticmethod
    def panel(d, box, a=1.0, fill=(14, 17, 22), radius=12, outline=None):
        x0, y0, x1, y1 = box
        d.rounded_rectangle(box, ST.px(radius), fill=(*fill, int(205 * a)),
                            outline=(*outline, int(255 * a)) if outline else None, width=2)

    @staticmethod
    def text(d, xy, s, f, fill=INK, a=1.0, anchor="la"):
        d.text(xy, s, font=f, fill=(*fill, int(255 * a)), anchor=anchor)

    def area_now(self, t: float) -> tuple:
        """(sq ft, m2, length m, width m, label) shown in the area panel at t: the conventional plan's until the vertical
        floor grows, then counting down to the vertical lab's as it does."""
        c, v = self.rows["conventional"], self.rows["vertical"]
        g = self.S.grow(t)
        if g <= 0:
            return c["area_sqft"], c["area_m2"], c["length_m"], c["width_m"], 0.0
        sq = c["area_sqft"] + (v["area_sqft"] - c["area_sqft"]) * g
        m2 = c["area_m2"] + (v["area_m2"] - c["area_m2"]) * g
        if g >= 1:
            return v["area_sqft"], v["area_m2"], v["length_m"], v["width_m"], 1.0
        return sq, m2, None, None, g

    # ------------------------------------------------------------------------------------------------ 3-D overlays
    def overlay(self, base: np.ndarray, t: float) -> np.ndarray:
        img = Image.fromarray(base).convert("RGBA")
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        ph = self.phase(t)
        S = self.S
        # the title
        ft, fs = ST.font(31, bold=True), ST.font(19)
        title = "Floor space: the same 43 instruments, three ways"
        tw = max(d.textlength(title, font=ft), d.textlength("Design layouts, not built labs  ·  equipment from PR "
                                                              "318's 3-D lab", font=fs))
        self.panel(d, (ST.px(24), ST.px(20), ST.px(24) + tw + ST.px(38), ST.px(20 + 86)))
        self.text(d, (ST.px(42), ST.px(30)), title, ft)
        self.text(d, (ST.px(42), ST.px(72)), "Design layouts, not built labs  ·  equipment from PR 318's 3-D lab", fs,
                  fill=INK2)
        # the stage
        fb = ST.font(26, bold=True)
        lab = STAGE[ph]
        w = d.textlength(lab, font=fb)
        x1 = ST.px(1896)
        self.panel(d, (x1 - w - ST.px(40), ST.px(20), x1, ST.px(20 + 56)), fill=(30, 60, 140))
        self.text(d, (x1 - w - ST.px(20), ST.px(33)), lab, fb)
        # the area panel
        a_area = ST.ramp(t, 2.0, 3.0)
        if a_area > 0:
            sq, m2, L, Wd, g = self.area_now(t)
            ox, oy = ST.px(1896 - 470), ST.px(92)
            self.panel(d, (ox, oy, ST.px(1896), oy + ST.px(150)), a_area)
            big = ST.font(46, bold=True)
            self.text(d, (ox + ST.px(20), oy + ST.px(12)), f"{fmt(sq)} sq ft", big, a=a_area)
            dims = f"{m2:,.0f} m²" + (f"  ·  {L:.1f} × {Wd:.1f} m" if L else "")
            self.text(d, (ox + ST.px(20), oy + ST.px(70)), dims, ST.font(21), a=a_area)
            n = self.counts["instruments"]
            per = n / sq * 1000
            self.text(d, (ox + ST.px(20), oy + ST.px(104)), f"{n} instruments  ·  {per:.1f} per 1,000 sq ft",
                      ST.font(21), fill=INK2, a=a_area)
            if ph == "flat":
                tag = "unchanged"
                a2 = ST.window(t, PH["flat"] + 11.0, PH["vert"], 0.6)
                if a2 > 0:
                    fw = ST.font(20, bold=True)
                    tw = d.textlength(tag, font=fw)
                    d.rounded_rectangle((ST.px(1896) - tw - ST.px(44), oy + ST.px(18), ST.px(1896) - ST.px(16),
                                         oy + ST.px(50)), ST.px(8), fill=(10, 172, 35, int(230 * a2)))
                    self.text(d, (ST.px(1896) - tw - ST.px(30), oy + ST.px(22)), tag, fw, a=a2)
            if ph == "vert" and g >= 1:
                c = self.rows["conventional"]["area_sqft"]
                v = self.rows["vertical"]["area_sqft"]
                tag = f"−{(1 - v / c) * 100:.0f} %"
                fw = ST.font(24, bold=True)
                tw = d.textlength(tag, font=fw)
                d.rounded_rectangle((ST.px(1896) - tw - ST.px(44), oy + ST.px(16), ST.px(1896) - ST.px(16),
                                     oy + ST.px(52)), ST.px(8), fill=(10, 172, 35, 235))
                self.text(d, (ST.px(1896) - tw - ST.px(30), oy + ST.px(20)), tag, fw)
        # the rules: the conventional plan's from f3, the vertical lab's from f7
        f3 = next(ln for ln in self.lines if ln["id"] == "f3")["t0"]
        f7 = next(ln for ln in self.lines if ln["id"] == "f7")["t0"]
        rules_c = ["How the area is measured: design rules, the same in every layout",
                   "Benches 30 in (0.76 m) deep, 36 in for deeper instruments; 150 mm between instruments",
                   "Aisles 5 ft (1.52 m), from NIH's lab module; a 6 ft (1.83 m) corridor",
                   "Service space 0.6 m beside and behind every floor machine",
                   "Walls 150 mm; no room narrower than one 11 ft module; area to the walls' outer faces"]
        rules_v = ["The vertical lab, by the same rules",
                   "Two Kardex Shuttle XP 500s, 9.15 m tall, hold the benchtop instruments",
                   "One MiR aisle, 3.0 m: two MiR250s pass (MiR250 spec sheet)",
                   "Service space 0.6 m beside and behind every floor machine",
                   "Area to the walls' outer faces"]
        f6_ = next(ln for ln in self.lines if ln["id"] == "f6")["t0"]
        for rules, a, top in ((rules_c, ST.window(t, f3, f6_ + 0.2, 0.6), False),
                              (rules_v, ST.window(t, f7, PH["plans"] + 0.5, 0.6), True)):
            if a <= 0:
                continue
            f1, f2 = ST.font(19, bold=True), ST.font(18)
            wmax = max(d.textlength(rules[0], font=f1), *(d.textlength("•  " + r, font=f2) for r in rules[1:]))
            hh = ST.px(36 + 27 * (len(rules) - 1) + 10)
            x0, y1b = ST.px(24), (ST.px(120) + hh if top else ST.px(1060))
            self.panel(d, (x0, y1b - hh, x0 + wmax + ST.px(36), y1b), a)
            self.text(d, (x0 + ST.px(18), y1b - hh + ST.px(12)), rules[0], f1, a=a)
            for i, r in enumerate(rules[1:]):
                self.text(d, (x0 + ST.px(18), y1b - hh + ST.px(44 + 27 * i)), "•  " + r, f2, fill=(214, 216, 220),
                          a=a)
        # room labels on the conventional plan
        a_rooms = min(ST.ramp(t, 7.0, 8.0), 1.0 - ST.ramp(t, PH["vert"] + 11.0, PH["vert"] + 12.2))
        if a_rooms > 0:
            cam = S.camera(t)
            fr = ST.font(17, bold=True)
            placed = []
            for r in S.conv.rooms:
                x0, y0, x1, y1 = r["rect"]
                q = FSS.project(cam, [((x0 + x1) / 2, (y0 + y1) / 2, 1250.0)])[0]
                s = r["name"]
                w = d.textlength(s, font=fr)
                bx = [q[0] - w / 2 - ST.px(9), q[1] - ST.px(15), q[0] + w / 2 + ST.px(9), q[1] + ST.px(15)]
                for p in placed:
                    if bx[0] < p[2] and p[0] < bx[2] and bx[1] < p[3] and p[1] < bx[3]:
                        bx[1] += ST.px(34)
                        bx[3] += ST.px(34)
                placed.append(bx)
                d.rounded_rectangle(bx, ST.px(7), fill=(14, 17, 22, int(190 * a_rooms)))
                self.text(d, (bx[0] + ST.px(9), bx[1] + ST.px(5)), s, fr, a=a_rooms)
        # the automation added (flat)
        a_auto = ST.window(t, PH["flat"] + 1.0, PH["vert"] + 1.0, 0.6)
        if a_auto > 0:
            fl = self.rows["flat"]
            items = [f"{FS.FLAT_UNITS} MiR250 + UR12e mobile manipulators",
                     f"{fl['docks']} docking targets: one per floor machine and bench",
                     f"{fl['arms']} fixed arms with sample racks, where a bench has room",
                     f"{fl['chargers']} chargers"]
            f1, f2 = ST.font(20, bold=True), ST.font(18)
            wmax = max(d.textlength("+  " + s_, font=f2) for s_ in items)
            ox, oy = ST.px(1896) - wmax - ST.px(36), ST.px(256)
            self.panel(d, (ox, oy, ST.px(1896), oy + ST.px(48 + 28 * len(items))), a_auto)
            self.text(d, (ox + ST.px(18), oy + ST.px(12)), "Automation added", f1, a=a_auto)
            for i, s in enumerate(items):
                self.text(d, (ox + ST.px(18), oy + ST.px(44 + 28 * i)), "+  " + s, f2, fill=(214, 216, 220),
                          a=a_auto)
        f5 = next(ln for ln in self.lines if ln["id"] == "f5")["t0"]
        a_aisle = ST.window(t, f5 + 2.5, PH["vert"] + 0.5, 0.6)
        if a_aisle > 0:
            s1 = "A MiR250 docked in a 5 ft (1.52 m) aisle leaves 0.94 m beside it;"
            s2 = "one needs 1.45 m to drive by (MiR250 spec sheet), so the others wait."
            f2 = ST.font(20)
            w = max(d.textlength(s1, font=f2), d.textlength(s2, font=f2))
            cx = ST.px(960)
            self.panel(d, (cx - w / 2 - ST.px(22), ST.px(1060 - 82), cx + w / 2 + ST.px(22), ST.px(1060)), a_aisle,
                       fill=(60, 44, 10))
            self.text(d, (cx, ST.px(1060 - 70)), s1, f2, a=a_aisle, anchor="ma")
            self.text(d, (cx, ST.px(1060 - 40)), s2, f2, a=a_aisle, anchor="ma")
        # the Shuttles come in
        f6 = next(ln for ln in self.lines if ln["id"] == "f6")["t0"]
        a_sh = ST.window(t, f6, PH["vert"] + 13.0, 0.6)
        if a_sh > 0:
            n_trays = len(self.S.tp["trays"])
            n_bench = self.counts["benchtop"]
            n_store = sum(1 for it in self.S.inv.values() if it.tray is not None and not it.instrument)
            s1 = "Two Kardex Shuttle XP 500s, 9.15 m tall, come in"
            s2 = (f"{n_bench} benchtop instruments and {n_store} other items (stores, racks, accessories) go onto "
                  f"their {n_trays} trays")
            f1, f2 = ST.font(22, bold=True), ST.font(20)
            w = max(d.textlength(s1, font=f1), d.textlength(s2, font=f2))
            cx = ST.px(960)
            self.panel(d, (cx - w / 2 - ST.px(22), ST.px(1060 - 86), cx + w / 2 + ST.px(22), ST.px(1060)), a_sh)
            self.text(d, (cx, ST.px(1060 - 74)), s1, f1, a=a_sh, anchor="ma")
            self.text(d, (cx, ST.px(1060 - 42)), s2, f2, a=a_sh, anchor="ma")
        # the two footprints, labelled, once the vertical floor is down
        a_fp = ST.window(t, PH["vert"] + 19.0, PH["plans"] + 0.2, 0.6)
        if a_fp > 0:
            cam = S.camera(t)
            cx0, cy0, cx1, cy1 = S.conv.envelope
            vx0, vy0, vx1, vy1 = S.vert.envelope
            fr = ST.font(19, bold=True)
            cands = {"the conventional lab's footprint": [(cx1 - 2600.0, vy0 - 1400.0, 0.0),
                                                          (cx1 - 2600.0, (cy0 + vy0) / 2, 0.0),
                                                          ((cx0 + cx1) / 2, vy0 - 1600.0, 0.0)],
                     "the vertical lab": [(vx0 + 3800.0, vy0 + 700.0, 0.0), ((vx0 + vx1) / 2 - 3000.0, vy0 + 700.0, 0.0)]}
            for s, col in (("the conventional lab's footprint", (120, 70, 56)), ("the vertical lab", (16, 96, 52))):
                q = None
                for p in cands[s]:
                    qq = FSS.project(cam, [p])[0]
                    if 250 < qq[0] < 1670 and 140 < qq[1] < 1000:
                        q = qq
                        break
                if q is None:
                    continue
                w = d.textlength(s, font=fr)
                bx = (q[0] - w / 2 - ST.px(10), q[1] - ST.px(16), q[0] + w / 2 + ST.px(10), q[1] + ST.px(16))
                d.rounded_rectangle(bx, ST.px(8), fill=(*col, int(225 * a_fp)))
                self.text(d, (q[0], q[1] - ST.px(12)), s, fr, a=a_fp, anchor="ma")
        img.alpha_composite(lay)
        return np.asarray(img.convert("RGB"))

    # ------------------------------------------------------------------------------------------------ the plans
    def plan_layer(self, name: str, k: float) -> Image.Image:
        """A layout drawn in plan at k px/mm, north up, on a transparent layer sized to its envelope."""
        key = (name, round(k, 6))
        if key in self._plan_cache:
            return self._plan_cache[key]
        S = self.S
        lay = self.lays[name]
        inv = S.inv
        x0, y0, x1, y1 = lay.envelope
        W_, H_ = int(math.ceil((x1 - x0) * k)) + 2, int(math.ceil((y1 - y0) * k)) + 2
        im = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)

        def R(r):
            return ((r[0] - x0) * k, (y1 - r[3]) * k, (r[2] - x0) * k, (y1 - r[1]) * k)
        d.rectangle(R(lay.envelope), fill=COL["floor_vert" if name == "vertical" else "floor_conv"])
        for a in lay.aisles:
            col = {"corridor": COL["corridor"], "aisle": COL["aisle"], "mir": COL["mir"], "dock": COL["aisle"],
                   "mir1": COL["mir1"]}
            d.rectangle(R(a["rect"]), fill=col.get(a["kind"], COL["aisle"]))
        for b in lay.benches:
            if b.get("free"):
                d.rectangle(R(b["rect"]), fill=COL["free"], outline=(170, 160, 146), width=1)
            else:
                d.rectangle(R(b["rect"]), fill=COL["bench" if b["kind"] == "bench" else "shelf"],
                            outline=(150, 134, 112) if "tray" in b else None, width=1)
        for kk, p in lay.places.items():
            if kk in FS.VLM_KEYS:
                r = (p.x - FS.VLM["w"] / 2, p.y - FS.VLM["d"] / 2, p.x + FS.VLM["w"] / 2, p.y + FS.VLM["d"] / 2)
                d.rectangle(R(r), fill=COL["vlm"], outline=(30, 34, 40), width=max(1, int(k * 40)))
                continue
            if p.on is not None and p.on.startswith("tray"):
                continue
            if math.isnan(p.x):
                continue
            r = p.rect(inv[kk])
            if p.on is None:
                d.rectangle(R(r), fill=COL["machine"], outline=(60, 80, 104), width=max(1, int(k * 30)))
            elif p.on == "bench":
                d.rectangle(R(r), fill=COL["inst"] if inv[kk].instrument else COL["store"])
        for c in lay.chargers:
            d.rectangle(R((c[0] - 300, c[1] - 300, c[0] + 300, c[1] + 300)), fill=COL["charger"])
        for a in lay.arms:
            rr = max(2, 230 * k)
            q = R((a["x"], a["y"], a["x"], a["y"]))
            d.ellipse((q[0] - rr, q[1] - rr, q[0] + rr, q[1] + rr), fill=COL["arm"], outline=(90, 60, 10))
        for dk in lay.docks:
            q = R((dk["x"], dk["y"], dk["x"], dk["y"]))
            rr = max(2.5, 220 * k)
            d.polygon([(q[0], q[1] - rr), (q[0] - rr, q[1] + rr * 0.8), (q[0] + rr, q[1] + rr * 0.8)],
                      fill=COL["dock"])
        for w in lay.walls:
            d.rectangle(R(w), fill=COL["wall"])
        d.rectangle(R(lay.envelope), outline=(20, 22, 26), width=max(2, int(k * 120)))
        self._plan_cache[key] = im
        return im

    def plans_geometry(self):
        """Where each plan sits at the end, all at one scale, north up: today's equipment in the first row (the
        conventional lab, the same plan automated, laid out for robots, the vertical lab) and the same capacity in the
        second (the Shuttles' trays laid out flat, the vertical lab again). -> (k px/mm, {name: (x, y)}, the rows'
        heights in px)."""
        env = {n: l.envelope for n, l in self.lays.items()}
        wid = {n: e[2] - e[0] for n, e in env.items()}
        hei = {n: e[3] - e[1] for n, e in env.items()}
        gap = 1800.0
        k = (1920 - 2 * 46) / (sum(wid[n] for n in ROW_A) + 3 * gap)
        pos, x = {}, 46.0
        for n in ROW_A:
            pos[n] = (x, 192.0)
            x += (wid[n] + gap) * k
        pos["capacity"] = (46.0, 584.0)
        pos["vertical2"] = (46.0 + (wid["capacity"] + gap) * k, 584.0)
        return k, pos, max(hei[n] for n in ROW_A) * k, max(hei["capacity"], hei["vertical"]) * k

    def t0(self, lid: str) -> float:
        return next(ln for ln in self.lines if ln["id"] == lid)["t0"]

    def _fade_in(self, img, name, k, xy, a):
        if a <= 0:
            return
        L = self.plan_layer(name, k)
        if a < 1:
            L = L.copy()
            L.putalpha(L.getchannel("A").point(lambda v: int(v * a)))
        img.alpha_composite(L, (int(round(xy[0] - (1 - a) * 160)), int(round(xy[1]))))

    def _badge(self, d, x, y, s, a, size=24):
        fw = ST.font(size, bold=True)
        w = d.textlength(s, font=fw)
        d.rounded_rectangle((x, y, x + w + 24, y + size + 14), 9, fill=(10, 140, 35, int(240 * a)))
        self.text(d, (x + 12, y + 5), s, fw, fill=(255, 255, 255), a=a)
        return x + w + 24

    def plans(self, t: float) -> np.ndarray:
        S = self.S
        img = Image.new("RGBA", (1920, 1080), (*PLAN_BG, 255))
        k1, pos, hA, hB = self.plans_geometry()
        u = ST.ramp(t, PH["plans"] + 2.6, PH["plans"] + 5.4)
        # the vertical lab: from the top view's scale and place to its slot in the first row
        kv = self.k_top + (k1 - self.k_top) * u
        ox = self.o_top[0] + (pos["vertical"][0] - self.o_top[0]) * u
        oy = self.o_top[1] + (pos["vertical"][1] - self.o_top[1]) * u
        img.alpha_composite(self.plan_layer("vertical", kv), (int(round(ox)), int(round(oy))))
        for i, n in enumerate(("conventional", "flat", "robots")):
            self._fade_in(img, n, k1, pos[n], ST.ramp(t, PH["plans"] + 3.8 + 0.4 * i, PH["plans"] + 5.6 + 0.4 * i))
        f8, f11, f9, f10 = (self.t0(x) for x in ("f8", "f11", "f9", "f10"))
        f11b = f11 + 7.6                                   # "And by capacity, ..."
        aB = ST.ramp(t, f11b - 1.2, f11b)
        self._fade_in(img, "capacity", k1, pos["capacity"], aB)
        self._fade_in(img, "vertical", k1, pos["vertical2"], aB)
        d = ImageDraw.Draw(img)
        rows, cp = self.rows, self.cap
        a_txt = ST.ramp(t, PH["plans"] + 5.2, PH["plans"] + 6.2)
        green = (10, 110, 30)
        if a_txt > 0:
            self.text(d, (46, 24), "Floor space, compared two ways", ST.font(34, bold=True), fill=DARK, a=a_txt)
            self.text(d, (46, 72), "At one scale, north up. Design layouts, not built labs.", ST.font(20), fill=DARK2,
                      a=a_txt)
            self.text(d, (46, 116), "Same equipment: today's 43 instruments", ST.font(24, bold=True), fill=DARK,
                      a=a_txt)
            extra = {"flat": (f"+ {FS.FLAT_UNITS} robots, {rows['flat']['arms']} fixed arms, {rows['flat']['docks']} "
                              "docks", "a docked robot leaves 0.94 m of a 5 ft aisle", False),
                     "robots": (f"{rows['robots']['positions']} tray-sized positions, a dock lane each",
                                "one-way 1.45 m robot aisles; floor machines as in the vertical lab", False),
                     "vertical": ("Shuttles 9.15 m tall: it needs a high bay", "", True), "conventional": ("", "", False)}
            yl = 192 + hA + 8
            for n in ROW_A:
                r = rows[n]
                x, y = pos[n]
                self.text(d, (x, 162), TITLES[n], ST.font(19, bold=True), fill=DARK, a=a_txt)
                self.text(d, (x, yl), f"{fmt(r['area_sqft'])} sq ft", ST.font(27, bold=True), fill=DARK, a=a_txt)
                self.text(d, (x, yl + 36), f"{r['length_m']:.1f} × {r['width_m']:.1f} m · {r['area_m2']:.0f} m² · "
                                           f"{r['per_1000_sqft']:.1f} instruments / 1,000 sq ft", ST.font(14),
                          fill=DARK2, a=a_txt)
                e1, e2, bold = extra[n]
                self.text(d, (x, yl + 56), e1, ST.font(14, bold=bold), fill=(150, 60, 20) if bold else DARK2, a=a_txt)
                self.text(d, (x, yl + 74), e2, ST.font(14), fill=DARK2, a=a_txt)
            # what the plans' marks are
            lx, ly = 46, 872
            marks = [("floor machine", "rect", COL["machine"]), ("benchtop instrument", "rect", COL["inst"]),
                     ("store", "rect", COL["store"]), ("bench", "rect", COL["bench"]),
                     ("free tray position", "rect", COL["free"]), ("Shuttle", "rect", COL["vlm"]),
                     ("aisle, dock lane", "rect", COL["aisle"]), ("MiR aisle", "rect", COL["mir"]),
                     ("one-way MiR aisle", "rect", COL["mir1"]), ("docking target", "tri", COL["dock"]),
                     ("fixed arm", "dot", COL["arm"]), ("charger", "rect", COL["charger"])]
            fl = ST.font(15)
            for lab_, kind, col in marks:
                if kind == "rect":
                    d.rectangle((lx, ly + 3, lx + 16, ly + 18), fill=(*col, int(255 * a_txt)))
                elif kind == "tri":
                    d.polygon([(lx + 8, ly + 2), (lx, ly + 18), (lx + 16, ly + 18)], fill=(*col, int(255 * a_txt)))
                else:
                    d.ellipse((lx + 1, ly + 3, lx + 15, ly + 18), fill=(*col, int(255 * a_txt)))
                self.text(d, (lx + 21, ly), lab_, fl, fill=DARK2, a=a_txt)
                lx += 21 + d.textlength(lab_, font=fl) + 18
        # the first comparison (f8), and the layout for robots (f11's first sentence)
        a8 = min(ST.ramp(t, f8, f8 + 0.8), a_txt)          # with the labels it sits by
        xv = pos["vertical"][0]
        yl = 192 + hA + 8
        fh = ST.font(24, bold=True)
        xh = 46 + d.textlength("Same equipment: today's 43 instruments", font=fh) + 28
        c, v, rb = rows["conventional"], rows["vertical"], rows["robots"]
        pc = cp["percent"]
        if a8 > 0:
            wv = d.textlength(f"{fmt(v['area_sqft'])} sq ft", font=ST.font(27, bold=True))
            xb = self._badge(d, xv + wv + 14, yl - 2, f"−{pc['vertical_vs_conventional']} %", a8, 22)
            self.text(d, (xh, 120), f"The vertical lab: {pc['vertical_vs_conventional']} % less floor than the "
                                    f"conventional lab ({v['per_1000_sqft']:.1f} against {c['per_1000_sqft']:.1f} "
                                    "instruments per 1,000 sq ft)", ST.font(18, bold=True), fill=green, a=a8)
        a11 = ST.ramp(t, f11, f11 + 0.8)
        if a11 > 0:
            xr = pos["robots"][0]
            wr = d.textlength(f"{fmt(rb['area_sqft'])} sq ft", font=ST.font(27, bold=True))
            d.rounded_rectangle((xr - 8, yl - 4, xr + wr + 10, yl + 34), 8, outline=(*green, int(255 * a11)),
                                width=3)
            self.text(d, (xh, 143), f"and {pc['vertical_vs_robots']} % less than the flat lab laid out for robots "
                                    f"({fmt(v['area_sqft'])} against {fmt(rb['area_sqft'])} sq ft)",
                      ST.font(18, bold=True), fill=green, a=a11)
        # the second row: the same capacity
        if aB > 0:
            tr = cp["trays"]
            fl_, vv = cp["same_capacity"]["flat"], cp["same_capacity"]["vertical"]
            self.text(d, (46, 508), f"Same capacity: the Shuttles' {tr['trays']} trays as bench positions",
                      ST.font(24, bold=True), fill=DARK, a=aB)
            self.text(d, (46, 540), f"{tr['in_use']} trays in use today, {tr['added']} more at the tray plan's "
                                    f"{tr['span_mm']:.0f} mm; each 2.45 × 0.86 m ({tr['tray_m2']:.1f} m²): "
                                    f"{fmt(tr['surface_m2'])} m² of tray surface in all", ST.font(16), fill=DARK2, a=aB)
            yb = 584 + hB + 8
            labs = {"capacity": (f"Automated, {fl_['positions']} tray positions laid out flat",
                                 f"{fl_['length_m']:.1f} × {fl_['width_m']:.1f} m  ·  {fl_['area_m2']:.0f} m²  ·  "
                                 f"{fl_['positions_per_1000_sqft']:.1f} positions / 1,000 sq ft",
                                 f"{tr['added']} free positions, light; the same rules as the layout for robots",
                                 fl_["area_sqft"]),
                    "vertical2": (f"Vertical lab: {vv['positions']} trays in two Shuttles",
                                  f"{v['length_m']:.1f} × {v['width_m']:.1f} m  ·  {v['area_m2']:.0f} m²  ·  "
                                  f"{vv['positions_per_1000_sqft']:.1f} positions / 1,000 sq ft",
                                  "", vv["area_sqft"])}
            for n, (ti, l2, l3, sq) in labs.items():
                x, _ = pos[n]
                self.text(d, (x, yb), f"{fmt(sq)} sq ft", ST.font(27, bold=True), fill=DARK, a=aB)
                self.text(d, (x, yb + 36), l2, ST.font(14), fill=DARK2, a=aB)
                self.text(d, (x, yb + 56), l3, ST.font(14), fill=DARK2, a=aB)
            # plan titles for the second row sit over the plans, in the plans' own gap
            for n, (ti, _, _, _) in labs.items():
                x, _ = pos[n]
                self.text(d, (x, 584 - 24), ti, ST.font(17, bold=True), fill=DARK, a=aB)
        aB2 = ST.ramp(t, f11b + 2.0, f11b + 2.8)
        if aB2 > 0:
            vv = cp["same_capacity"]["vertical"]
            fl_ = cp["same_capacity"]["flat"]
            wv = d.textlength(f"{fmt(vv['area_sqft'])} sq ft", font=ST.font(27, bold=True))
            yb = 584 + hB + 8
            self._badge(d, pos["vertical2"][0] + wv + 14, yb - 2, f"−{pc['vertical_vs_flat_capacity']} %", aB2, 22)
            fh2 = ST.font(24, bold=True)
            xh2 = 46 + d.textlength(f"Same capacity: the Shuttles' {cp['trays']['trays']} trays as bench positions",
                                    font=fh2) + 28
            self.text(d, (xh2, 512), f"{vv['positions_per_1000_sqft']:.1f} against {fl_['positions_per_1000_sqft']:.1f}"
                                     " tray positions per 1,000 sq ft", ST.font(18, bold=True), fill=green, a=aB2)
        # where the floor goes, the floor machines apart (f9)
        a9 = ST.ramp(t, f9, f9 + 0.8)
        if a9 > 0:
            ve = self.lays["vertical"].envelope
            x0 = pos["vertical2"][0] + (ve[2] - ve[0]) * k1 + 64
            y0 = 552
            mbm = cp["machine_block"]["area_m2"]
            self.text(d, (x0, y0), "Where the floor goes (m²)", ST.font(19, bold=True), fill=DARK, a=a9)
            bars = [("Conventional lab: rooms mix machines and benches", None, c["area_m2"]),
                    ("Vertical lab: + the two Shuttles", mbm, v["area_m2"] - mbm),
                    ("Laid out for robots: + 18 tray positions", mbm, rb["area_m2"] - mbm),
                    (f"{cp['same_capacity']['flat']['positions']} tray positions, flat", mbm,
                     cp["same_capacity"]["flat"]["area_m2"] - mbm)]
            sc = (1880 - x0) / 600.0
            yy = y0 + 34
            for lab_, m_, rest in bars:
                self.text(d, (x0, yy), lab_, ST.font(14), fill=DARK2, a=a9)
                yy += 19
                xx = x0
                if m_ is not None:
                    w = m_ * sc
                    d.rectangle((xx, yy, xx + w, yy + 24), fill=(*COL["machine"], int(255 * a9)))
                    self.text(d, (xx + w / 2, yy + 4), f"{m_:.0f}", ST.font(14, bold=True), fill=(255, 255, 255),
                              a=a9, anchor="ma")
                    xx += w
                    w = rest * sc
                    d.rectangle((xx, yy, xx + w, yy + 24), fill=(*BAR["benches, shelves and Shuttles"], int(255 * a9)))
                    self.text(d, (xx + w + 6, yy + 4), f"+ {rest:.0f}", ST.font(14, bold=True), fill=DARK, a=a9)
                else:
                    w = rest * sc
                    d.rectangle((xx, yy, xx + w, yy + 24), fill=(*BAR["other floor"], int(255 * a9)))
                    self.text(d, (xx + w + 6, yy + 4), f"{rest:.0f}", ST.font(14, bold=True), fill=DARK, a=a9)
                yy += 34
            self.text(d, (x0, yy + 2), f"Blue: the floor machines' block ({mbm:.0f} m²): the 12 machines, their 0.6 m",
                      ST.font(14), fill=DARK2, a=a9)
            self.text(d, (x0, yy + 20), "service space and the 3.0 m robot aisle, the same in all three",
                      ST.font(14), fill=DARK2, a=a9)
        # Emerald Cloud Lab (f10)
        a10 = ST.ramp(t, f10, f10 + 0.8)
        if a10 > 0:
            e = FS.ECL
            per = 100 / e["ssf"]["sqft"] * 1000
            y = 912
            d.rounded_rectangle((36, y, 1884, y + 136), 12, fill=(255, 255, 255, int(225 * a10)),
                                outline=(150, 154, 160, int(255 * a10)), width=2)
            self.text(d, (56, y + 14), "For scale: Emerald Cloud Lab, built labs, as published", ST.font(21, bold=True),
                      fill=DARK, a=a10)
            self.text(d, (56, y + 50), f"South San Francisco: about {fmt(e['ssf']['sqft'])} sq ft ({fmt(e['ssf']['m2'])}"
                                       f" m²), more than 100 items of equipment: more than {per:.1f} per 1,000 sq ft "
                                       "(The Guardian, 2022)", ST.font(19), fill=DARK2, a=a10)
            self.text(d, (56, y + 80), f"Austin: {fmt(e['austin']['sqft'])} sq ft for over 230 instrument types (ECL press "
                                       "release, 2023): types, not instruments, so no per-area figure", ST.font(19),
                      fill=DARK2, a=a10)
            self.text(d, (56, y + 108), "Life-science instruments on benches with people loading them: a scale "
                                        "reference, not like for like.", ST.font(17), fill=DARK2, a=a10)
        return np.asarray(img.convert("RGB"))

    # ------------------------------------------------------------------------------------------------ a frame
    def frame(self, t: float, base: np.ndarray | None) -> np.ndarray:
        if t < PH["plans"] or base is not None and t < FSS.T3D_END:
            over = self.overlay(base, t) if base is not None else None
        else:
            over = None
        if t < PH["plans"]:
            return over
        p = self.plans(t)
        a = ST.ramp(t, PH["plans"] + 0.2, PH["plans"] + 2.4)
        if over is None or a >= 1:
            return p
        return (over.astype(np.float32) * (1 - a) + p.astype(np.float32) * a).astype(np.uint8)


# ============================================================================================ build
def frames_3d():
    """The 3-D renders, decoded once, frame by frame (rgb24)."""
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(F3D), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                            stdout=subprocess.PIPE)
    n = 1920 * 1080 * 3
    while True:
        b = proc.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(1080, 1920, 3)
    proc.wait()


def audio(cut: Cut, path: Path) -> Path:
    """The narration track: each line levelled to -19 dBFS RMS at its time, 48 kHz, then one gain to -16 LUFS."""
    import soundfile as sf
    from scipy.signal import resample_poly
    sr = 48000
    n = int(math.ceil(cut.T * sr))
    track = np.zeros(n, np.float32)
    for ln in cut.lines:
        y, r = sf.read(str(OUTD / "narration" / f"{ln['id']}.flac"), dtype="float32")
        y = resample_poly(y, sr, r).astype(np.float32)
        rms = float(np.sqrt(np.mean(y ** 2)) + 1e-9)
        y *= 10 ** (-19.0 / 20) / rms
        pk = float(np.abs(y).max())
        if pk > 10 ** (-1.5 / 20):
            y *= 10 ** (-1.5 / 20) / pk
        i0 = int(ln["t0"] * sr)
        track[i0:i0 + len(y)] += y[:max(0, n - i0)]
    raw = path.with_suffix(".raw.wav")
    sf.write(str(raw), track, sr, subtype="PCM_16")
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:"
                           "print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    js = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    # the second pass: one linear gain when the true peak allows it (loudnorm's linear mode), as the campaign video
    af = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:"
          "linear=true:print_format=json")
    out = subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(raw), "-af", af, "-ar", str(sr), str(path)],
                         capture_output=True, text=True).stderr
    js2 = json.loads(out[out.rindex("{"):out.rindex("}") + 1])
    print(f"audio: {js['input_i']} LUFS -> {js2['output_i']} LUFS, true peak {js2['output_tp']} dBTP, "
          f"{js2['normalization_type']}", flush=True)
    raw.unlink()
    return path


def remux():
    """The narration mixed again and muxed onto the encoded picture (/tmp/fscut/video.mp4), the picture copied."""
    cut = Cut()
    tmp = Path("/tmp/fscut")
    wav = audio(cut, tmp / "narration.wav")
    out = OUTD / "floorspace_preview.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "video.mp4"), "-i", str(wav), "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    print("wrote", out, flush=True)


def srt(cut: Cut, path: Path):
    def ts(t):
        h, m = int(t // 3600), int(t % 3600 // 60)
        s = t % 60
        return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"
    out = []
    for i, ln in enumerate(cut.lines, 1):
        out.append(f"{i}\n{ts(ln['t0'])} --> {ts(ln['t1'])}\n{ln['text']}\n")
    path.write_text("\n".join(out))


def final():
    cut = Cut()
    OUTD.mkdir(parents=True, exist_ok=True)
    tmp = Path("/tmp/fscut")
    tmp.mkdir(parents=True, exist_ok=True)
    vid = tmp / "video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080",
                            "-framerate", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf",
                            "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(vid)], stdin=subprocess.PIPE)
    src = frames_3d()
    cur, cur_i = None, -1
    n = int(round(cut.T * FPS))
    import time
    t0 = time.time()
    for i in range(n):
        t = i / FPS
        base = None
        if t < FSS.T3D_END:
            want = int(t * 15 + 1e-6)
            while cur_i < want:
                try:
                    cur = next(src)
                    cur_i += 1
                except StopIteration:
                    break
            base = cur
        img = cut.frame(t, base)
        enc.stdin.write(np.ascontiguousarray(img).tobytes())
        if (i + 1) % 300 == 0:
            print(f"cut: {i + 1}/{n} frames, {time.time() - t0:.0f} s", flush=True)
    enc.stdin.close()
    enc.wait()
    wav = audio(cut, tmp / "narration.wav")
    out = OUTD / "floorspace_preview.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-i", str(wav), "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    srt(cut, OUTD / "floorspace_preview.srt")
    rec = dict(file=out.name, seconds=cut.T, fps=FPS, size=[1920, 1080], render_fps_3d=15,
               lines=[dict(id=ln["id"], t0=round(ln["t0"], 2), t1=round(ln["t1"], 2), text=ln["text"])
                      for ln in cut.lines], phases=PH, rows=cut.rows,
               capacity=dict(trays=cut.cap["trays"]["trays"], in_use=cut.cap["trays"]["in_use"],
                             machine_block_m2=cut.cap["machine_block"]["area_m2"],
                             same_capacity={k: {kk: v[kk] for kk in ("area_m2", "area_sqft", "benchtop_m2",
                                                                     "positions_per_1000_sqft")}
                                            for k, v in cut.cap["same_capacity"].items()},
                             percent=cut.cap["percent"]))
    (OUTD / "floorspace_preview.json").write_text(json.dumps(rec, indent=1) + "\n")
    print("wrote", out, flush=True)


def stills(ts):
    cut = Cut()
    tmp = Path("/tmp/fscut")
    tmp.mkdir(parents=True, exist_ok=True)
    want = {int(t * 15 + 1e-6): t for t in ts if t < FSS.T3D_END}
    got = {}
    if want and F3D.exists():
        for i, fr in enumerate(frames_3d()):
            if i in want:
                got[want[i]] = fr.copy()
            if i > max(want):
                break
    for t in ts:
        base = got.get(t)
        if base is None and t < PH["plans"]:
            base = np.full((1080, 1920, 3), 200, np.uint8)
        img = cut.frame(t, base)
        Image.fromarray(img).save(tmp / f"still_{t:05.1f}.png")
        print("still", t, flush=True)


SHEET_T = (2.0, 10.0, 24.0, 33.0, 40.0, 47.0, 53.0, 57.0, 61.0, 64.5, 68.0, 73.0, 79.0, 92.0, 108.0, 125.0)


def sheet():
    """Sixteen moments of the preview in a 4 x 4 grid, each with its time."""
    out = OUTD / "floorspace_preview.mp4"
    tiles = []
    for t in SHEET_T:
        b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(out), "-frames:v", "1", "-f",
                            "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        im = Image.frombytes("RGB", (1920, 1080), b[:1920 * 1080 * 3]).resize((480, 270), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        s = f"{int(t // 60)}:{t % 60:04.1f}"
        d.rectangle((0, 0, 70, 22), fill=(0, 0, 0))
        d.text((6, 3), s, fill=(255, 255, 255), font=ST.font(15))
        tiles.append(im)
    sh = Image.new("RGB", (1920, 1080), (0, 0, 0))
    for i, im in enumerate(tiles):
        sh.paste(im, ((i % 4) * 480, (i // 4) * 270))
    sh.save(OUTD / "sheet.png")
    print("wrote", OUTD / "sheet.png")


def meta(commit: str):
    cut = Cut()
    c, f, r, v = (cut.rows[n] for n in ("conventional", "flat", "robots", "vertical"))
    cp = cut.cap
    tr, fl, vv, pc = cp["trays"], cp["same_capacity"]["flat"], cp["same_capacity"]["vertical"], cp["percent"]
    desc = f"""A preview segment for review (unlisted): the vertical lab's equipment laid out four ways, the floor area each layout takes, and the Shuttles' tray capacity laid out flat. Design layouts, not built labs.

Same equipment: today's 43 instruments (31 benchtop, 12 floor machines), from the 3-D lab of PR 318:
1. Conventional materials lab, grouped by workflow: {c['length_m']:.1f} x {c['width_m']:.1f} m, {c['area_m2']:.0f} m2 ({c['area_sqft']:,} sq ft), {c['per_1000_sqft']:.1f} instruments per 1,000 sq ft.
2. The same plan automated ({FS.FLAT_UNITS} MiR250 + UR12e mobile manipulators, {f['docks']} docking targets, {f['arms']} fixed arms with sample racks, {f['chargers']} chargers): the same {f['area_sqft']:,} sq ft, but a docked robot leaves 0.94 m of a 5 ft aisle, under the 1.45 m another needs to pass.
3. Automated, laid out for robots: the {r['positions']} trays in use as tray-sized bench positions (864 mm benches, a dock lane in front of each row, one-way 1.45 m MiR aisles in loops), the floor machines as in the vertical lab: {r['length_m']:.1f} x {r['width_m']:.1f} m, {r['area_m2']:.0f} m2 ({r['area_sqft']:,} sq ft).
4. Vertical lab (two Kardex Shuttle XP 500s, 9.15 m tall, with the benchtop instruments on their trays; the floor machines along one 3.0 m MiR aisle): {v['length_m']:.1f} x {v['width_m']:.1f} m, {v['area_m2']:.0f} m2 ({v['area_sqft']:,} sq ft), {v['per_1000_sqft']:.1f} instruments per 1,000 sq ft: {pc['vertical_vs_conventional']} % less floor than the conventional lab and {pc['vertical_vs_robots']} % less than the layout for robots, but it needs a high bay.

Same capacity: the two Shuttles hold {tr['trays']} trays at 9.15 m with the tray plan's slot spans ({tr['in_use']} in use, {tr['added']} more at {tr['span_mm']:.0f} mm), {tr['surface_m2']:.0f} m2 of tray. Laid out flat by the same rules, they need {fl['area_m2']:.0f} m2 ({fl['area_sqft']:,} sq ft) against the vertical lab's {vv['area_m2']:.0f} m2: {vv['positions_per_1000_sqft']:.1f} tray positions per 1,000 sq ft against {fl['positions_per_1000_sqft']:.1f}. The floor machines' block ({cp['machine_block']['area_m2']:.0f} m2) is the same in the vertical lab and both layouts for robots.

Rules: benches 30 in deep (36 in for deeper instruments), aisles 5 ft (NIH Office of Research Facilities, Lab Module Design Considerations, 2013), a 6 ft corridor, 0.6 m service space beside and behind every floor machine, 150 mm walls, no room narrower than one 11 ft module; for robots, the trays' own 2,450 x 864 mm per position, an 838 mm dock lane, MiR aisles of 1.45 m one way and 3.0 m to pass (MiR250 spec sheet); area to the walls' outer faces.

For scale: Emerald Cloud Lab's South San Francisco lab, about 15,000 sq ft with more than 100 items of equipment (The Guardian, 11 September 2022); its Austin facility, 105,000 sq ft for over 230 instrument types (Emerald Cloud Lab press release, 28 February 2023).

Narration: Kokoro v1.0 (open weights), voice af_heart. Code and notes: https://github.com/vertical-cloud-lab/byu-vcl/tree/{commit}/vertical-lab (twin/video/floorspace*.py, notes/twin_floorspace.md)."""
    js = dict(title="Floor space: four labs, the same equipment, and the same capacity (preview)", description=desc,
              tags=["vertical lab", "self-driving lab", "lab automation", "floor space", "Kardex", "MiR250"],
              categoryId="28", privacy="unlisted", commit=commit)
    (OUTD / "youtube_meta.json").write_text(json.dumps(js, indent=1) + "\n")
    print("wrote", OUTD / "youtube_meta.json")


if __name__ == "__main__":
    cmd = sys.argv[1] if sys.argv[1:] else "final"
    if cmd == "final":
        final()
    elif cmd == "stills":
        stills([float(v) for v in sys.argv[2:]])
    elif cmd == "sheet":
        sheet()
    elif cmd == "remux":
        remux()
    elif cmd == "meta":
        meta(sys.argv[2] if sys.argv[2:] else "HEAD")
    else:
        raise SystemExit(__doc__)
