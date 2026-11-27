"""Heat treatment, then the tensile test: the furnace with its profile plotted as it runs, then a bar pulled to
fracture with its stress-strain curve drawn as it pulls (twin/video/exp_mech.py).

    Mech().frame(t)      0 <= t <= Mech.DURATION

What is what on screen:

* **The stress-strain curves** are the twin's simulated load records for the alloy followed (twin/instruments/
  tensile.py at full fidelity: three sub-size bars, a clip-on extensometer and a load cell with their noise), and the
  yield strength, tensile strength and elongation are that module's own analysis of them (ASTM E8).
* **The furnace profile is illustrative.** The twin books the furnace for three hours and applies "the alloy
  family's standard heat treatment" to the strength (twin/truth_al.py ``strength``); it does not model a profile. The
  one drawn is the T6 the lab's 3-D model shows on that tray (PR 318, notes/alloy_workflow.md: solution treatment at
  530 C, a water quench, ageing at 160 C), with times chosen to fill the three hours.
* **The specimen** is a schematic: its extension follows the record's strain (drawn twice life size), the neck and
  the break are drawn. **The pictures of the furnace and the load frame** are the lab's 3-D model (PR 318's renders).
"""
from __future__ import annotations

import math

import numpy as np

from . import exp_data as X
from . import exp_draw as G
from .exp_draw import Axes, Canvas, Segment, fmt, lin, ramp
from .style import CAMP, INK, INK2, mix

# the illustrative T6: (hours, degC) corner points; the quench is the vertical drop
PROFILE = [(0.0, 25.0), (0.30, 530.0), (1.30, 530.0), (1.32, 25.0), (1.45, 25.0), (1.62, 160.0), (3.20, 160.0),
           (3.50, 40.0)]
STRETCH = 2.0                    # the schematic's extension, times life size
SRC_CLIP = "alloy_workflow"      # PR 318's chapter 5: from the printer to the tensile test (out/mp4, 1280 x 720)
CROP_FURNACE = (384, 196, 775, 436)      # clear of the render's gauge table, title and caption band
CROP_FRAME = (396, 160, 424, 474)        # the load frame's column and grips, clear of the render's own inset plot


def profile_T(h: float) -> float:
    return float(np.interp(h, [p[0] for p in PROFILE], [p[1] for p in PROFILE]))


class Mech(Segment):
    key = "mech"
    title = "Heat treatment, then the tensile test"
    campaign = "flaime_al"
    nodes = ("test",)
    done = ("composition", "calphad", "powder", "print", "section", "pip")
    DURATION = 31.0
    T_FURNACE = (0.8, 8.6)       # the profile draws
    T_SWAP = (8.6, 9.8)          # furnace -> load frame
    T_PULL = (9.8, 19.6)         # the first bar, to fracture
    T_MORE = (19.9, 22.6)        # the other two bars
    T_MARK = (22.8, 26.6)        # yield, UTS, elongation marked
    T_NET = 26.8                 # what the network takes

    def __init__(self):
        super().__init__()
        a = X.alloy("flaime_al")
        self.alloy = a
        ten = a.measure("tensile")
        self.ten = ten
        self.geom = ten["raw"]["geometry"]
        self.bars = []
        for i, b in enumerate(ten["raw"]["bars"]):
            e, s = np.asarray(b["strain"]) * 100.0, np.asarray(b["stress_MPa"])
            keep = np.unique(np.concatenate([np.arange(0, len(e), max(1, len(e) // 900)), [len(e) - 1]]))
            e, s = e[keep], np.maximum(s[keep], 0.0)
            ys, uts, el, E = (ten["bars"][k][i] for k in ("ys_MPa", "uts_MPa", "el_pct", "E_GPa"))
            iu = int(np.argmax(s))
            iy = int(np.argmax((s >= ys) & (e > 0.2))) if ys else 0
            self.bars.append(dict(e=e, s=s, ys=ys, uts=uts, el=el, E=E, iu=iu, iy=iy, ef=float(e[-1]),
                                  sf=float(s[-1]), eu=float(e[iu]), n=i + 1))
        self.bars.sort(key=lambda b: b["el"])              # the bar pulled slowly is the median one in elongation
        self.bars = [self.bars[1], self.bars[0], self.bars[2]]
        emax = max(b["ef"] for b in self.bars)
        smax = max(b["uts"] for b in self.bars)
        self.ax = Axes((1068, 262, 1816, 632), (0.0, math.ceil(emax * 1.18)), (0.0, math.ceil(smax * 1.14 / 100) * 100),
                       "engineering strain, %", "engineering stress, MPa")
        self.axT = Axes((1068, 262, 1816, 632), (0.0, 3.5), (0.0, 600.0), "time in the furnace, h",
                        "temperature, °C", xticks=[0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5], yticks=[0, 100, 200, 300, 400,
                                                                                         500, 600])
        b0 = self.bars[0]                                  # the pen moves along the first bar's curve at even speed
        px_, py_ = self.ax.X(b0["e"]), self.ax.Y(b0["s"])
        seg = np.hypot(np.diff(px_), np.diff(py_))
        self.arc = np.concatenate([[0.0], np.cumsum(seg)]) / max(seg.sum(), 1e-9)
        self._clips = {}
        f = X.load_facts()["al"]["tensile"]
        self.f = f
        self.captions = [
            (0.6, 8.9, "Bars are cut by wire EDM, then heat treated. The twin books the furnace for three hours and "
                       "models the strength it leaves, not the profile: this one is illustrative."),
            (9.8, 22.4, "Then three bars are pulled to fracture. Each curve is the twin's simulated load record for "
                        "this alloy."),
            (22.8, 30.6, "Yield strength and elongation feed the tensile node. The utility scores them against the "
                         "reference alloys, and counts the mineral burden."),
        ]
        self.marks = {"mech.furnace": self.T_FURNACE[0], "mech.pull": self.T_PULL[0], "mech.fracture": self.T_PULL[1],
                      "mech.marks": self.T_MARK[0], "mech.net": self.T_NET}
        self.sources = [
            ("sim", "stress-strain curves, yield, UTS, elongation: twin/instruments/tensile.py (full fidelity, three "
                    "bars) on the alloy followed"),
            ("illus", "furnace profile: the lab model's T6 (PR 318), not modelled by the twin"),
            ("illus", "the specimen: extension follows the record, drawn twice life size"),
            ("render", "furnace and load frame: PR 318's renders (out/mp4/alloy_workflow.mp4)"),
        ]

    # ------------------------------------------------------------------------------------------ clips
    def _clip(self, which: str):
        if which not in self._clips:
            from . import assets as A
            if which == "furnace":
                self._clips[which] = G.Footage(A.src(SRC_CLIP), 1418 / 6, 1535 / 6, 800, 450, CROP_FURNACE, 2.4)
            else:
                self._clips[which] = G.Footage(A.src(SRC_CLIP), 1942 / 6, 2011 / 6, 404, 452, CROP_FRAME, 1.0)
        return self._clips[which]

    def close(self):
        for c in self._clips.values():
            c.close()
        self._clips.clear()

    # ------------------------------------------------------------------------------------------ the frame
    def static_extra(self, cv: Canvas):
        cv.card((56, 150, 900, 936), "The experiment")
        cv.card((940, 150, 1864, 936), "Its data")

    def _strain_now(self, t: float) -> tuple:
        """(strain %, stress MPa, state) of the bar on the frame at t: state 'wait', 'pull' or 'broken'."""
        b = self.bars[0]
        if t < self.T_PULL[0]:
            return 0.0, 0.0, "wait"
        u = lin(t, *self.T_PULL)
        if u >= 1.0:
            return b["ef"], 0.0, "broken"
        i = float(np.interp(u, self.arc, np.arange(len(self.arc))))
        j = int(i)
        k = min(j + 1, len(b["e"]) - 1)
        w = i - j
        return float(b["e"][j] + (b["e"][k] - b["e"][j]) * w), float(b["s"][j] + (b["s"][k] - b["s"][j]) * w), "pull"

    def _specimen(self, cv: Canvas, t: float, e_pct: float, state: str, temp_C: float | None):
        """The bar between its grips (illustrative): heated in stage 1, stretched, necked and broken in stage 2."""
        b = self.bars[0]
        y0, half0 = 800.0, 21.0
        xl = 196.0                                         # the fixed grip's inner face
        L0 = 380.0
        ext = L0 * STRETCH * e_pct / 100.0
        xr = xl + L0 + ext
        neck = 0.0
        if e_pct > b["eu"] and b["ef"] > b["eu"]:
            neck = 0.42 * ((e_pct - b["eu"]) / (b["ef"] - b["eu"])) ** 1.6
        thin = (1 + e_pct / 100.0) ** -0.5
        xn = xl + (L0 + ext) * 0.58
        xs = np.linspace(xl, xr, 90)
        sh = 54.0                                          # the shoulders' length
        hw = np.full_like(xs, half0 * thin)
        for edge, sgn in ((xl, 1), (xr, -1)):
            u = np.clip((xs - edge) * sgn / sh, 0, 1)
            hw = np.where(u < 1, half0 * thin + (38.0 - half0 * thin) * (0.5 + 0.5 * np.cos(np.pi * u)), hw)
        hw = hw - neck * half0 * np.exp(-((xs - xn) / 30.0) ** 2)
        col = (176, 182, 194)
        if temp_C is not None and temp_C > 60:
            col = mix(col, (255, 124, 56), min(0.82, 0.82 * temp_C / 530.0))
        gap = 0.0
        if state == "broken":
            gap = 9.0 + 9.0 * ramp(t, self.T_PULL[1], self.T_PULL[1] + 0.5)
        for side in (0, 1):
            if state == "broken":
                sel = xs <= xn if side == 0 else xs >= xn
                off = -gap / 2 if side == 0 else gap / 2
            else:
                if side == 1:
                    break
                sel, off = np.ones_like(xs, bool), 0.0
            px_ = xs[sel] + off
            top = [(x, y0 - h) for x, h in zip(px_, hw[sel])]
            bot = [(x, y0 + h) for x, h in zip(px_, hw[sel])]
            if state == "broken":                          # a rough fracture face
                jag = [(-3, -0.9), (4, -0.45), (-4, 0.0), (3, 0.5), (-2, 0.95)]
                h_n = float(hw[sel][-1 if side == 0 else 0])
                face = [(xn + off + dx * (1 if side == 0 else -1), y0 + dy * h_n) for dx, dy in jag]
                pts = top + face + bot[::-1] if side == 0 else face[::-1] + top + bot[::-1]
                if side == 1:
                    pts = [(xn + off + dx * -1, y0 + dy * h_n) for dx, dy in jag][::-1] + top + bot[::-1]
            else:
                pts = top + bot[::-1]
            cv.poly(pts, fill=col, outline=(232, 236, 244), width=2)
        for x0, x1 in ((xl - 96, xl + 6), (xr - 6 + (gap / 2 if state == "broken" else 0), xr + 96 +
                                          (gap / 2 if state == "broken" else 0))):
            cv.rect((x0, y0 - 56, x1, y0 + 56), fill=(52, 58, 70), outline=(110, 116, 128), width=2, radius=8)
            for k in range(5):
                yy = y0 - 40 + k * 20
                cv.line([(x0 + 10, yy), (x1 - 10, yy)], (84, 90, 102), 2)
        if state in ("pull", "broken") or (state == "wait" and t >= self.T_SWAP[0]):
            xa = xr + 104 + (gap / 2 if state == "broken" else 0)
            if state == "pull":
                cv.arrow((xa, y0), (xa + 46, y0), G.HOT, 4, 13)
        if temp_C is not None:
            cv.text(xl + L0 / 2, y0 - 84, f"{fmt(temp_C)} °C", 30, bold=True, fill=INK, anchor="mm")
        cv.tag(76, 884, "illus", "the specimen" + (f"; its extension is drawn {STRETCH:g}× life size"
                                                     if temp_C is None else ", in the furnace"))

    def draw(self, cv: Canvas, t: float):
        col = CAMP[self.campaign]
        stage2 = t >= self.T_SWAP[0] + 0.5 * (self.T_SWAP[1] - self.T_SWAP[0])
        a1 = 1.0 - ramp(t, self.T_SWAP[0], self.T_SWAP[0] + 0.55)     # the furnace's picture and plot
        a2 = ramp(t, self.T_SWAP[1] - 0.55, self.T_SWAP[1])           # the frame's
        # ------------------------------------------------ left: the experiment
        hours = 3.5 * lin(t, *self.T_FURNACE)
        temp = profile_T(hours)
        if not stage2:
            fr = self._clip("furnace").frame(max(0.0, t - 0.2))
            cv.paste(fr, 78, 196, a=a1)
            G.framed(cv, (78, 196, 878, 646), "the furnace and its quench tank (tray F)", a=a1)
            cv.tag(88, 606, "render", "the lab's 3-D model (PR 318)", a=a1)
            self._specimen(cv, t, 0.0, "wait", temp if t >= self.T_FURNACE[0] else 25.0)
        else:
            e_now, s_now, state = self._strain_now(t)
            fr = self._clip("frame").frame(max(0.0, t - self.T_SWAP[1]))
            cv.paste(fr, 78, 196, a=a2)
            G.framed(cv, (78, 196, 482, 648), "the load frame", a=a2)
            cv.tag(88, 608, "render", "the lab's 3-D model", a=a2)
            # live gauges beside the frame
            cv.rect((506, 196, 878, 648), fill=G.PLOT_FILL, outline=G.CARD_EDGE, width=2, radius=10, a=a2)
            cv.text(528, 214, "one of three bars, on the frame" if state != "wait" else "one of three bars, gripped", 19,
                    cond=True, fill=INK2, a=a2)
            cv.value(528, 262, "strain (extensometer)", fmt(e_now, 2), "%", a=a2, size=52, label_size=19)
            cv.value(528, 398, "stress (load cell)", fmt(s_now, 0) if state != "broken" else "0", "MPa", a=a2,
                     size=52, label_size=19)
            g = self.geom
            cv.text(528, 540, f"gauge {g['w']:g} × {g['t']:g} mm, L₀ {g['L0']:.0f} mm", 18, cond=True,
                    fill=INK2, a=a2)
            cv.text(528, 568, "strain control, ISO 6892-1 method A1", 18, cond=True, fill=INK2, a=a2)
            if state == "broken":
                k = ramp(t, self.T_PULL[1], self.T_PULL[1] + 0.4)
                cv.rect((528, 600, 700, 636), fill=mix(G.PLOT_FILL, G.HOT, 0.85 * k), radius=8)
                cv.text(614, 618, "fracture", 20, bold=True, fill=(20, 16, 8), anchor="mm", a=k)
            self._specimen(cv, t, e_now, state, None)
        # ------------------------------------------------ right: the data
        if a1 > 0.004:                                     # the furnace profile, drawn as it runs
            ax = self.axT
            ax.draw(cv, a1)
            cv.text(1068, 206, "Furnace temperature against time", 24, bold=True, fill=INK, a=a1)
            hs = np.linspace(0.0, 3.5, 701)
            Ts = np.array([profile_T(h) for h in hs])
            ax.line(cv, hs, Ts, (150, 156, 168), 2.0, 1.0, a1 * 0.5, dashed=True)
            pen = ax.line(cv, hs, Ts, G.HOT, 4.0, hours / 3.5, a1)
            if pen and 0 < hours < 3.5:
                cv.circle(pen[0], pen[1], 8, fill=G.HOT, outline=INK, width=2, a=a1)
            for h_, T_, s_ in ((0.80, 548, "solution treatment, 530 °C"), (2.42, 178, "ageing, 160 °C")):
                cv.text(float(ax.X(h_)), float(ax.Y(T_)) - 10, s_, 19, fill=INK, anchor="ms",
                        a=a1 * ramp(hours, h_ - 0.45, h_ - 0.2))
            cv.text(float(ax.X(1.36)), float(ax.Y(300)), "water quench", 19, fill=INK, anchor="lm",
                    a=a1 * ramp(hours, 1.3, 1.45))
            cv.tag(1068, 716, "illus", "the T6 in the lab's 3-D model (PR 318)", a=a1)
            cv.para(1068, 772, "The twin books three furnace hours and applies the strength after heat treatment. "
                               "It does not model the profile.", 20, 760, fill=INK2, a=a1, cond=True)
        if a2 > 0.004:                                     # the stress-strain curves
            ax = self.ax
            ax.draw(cv, a2)
            cv.text(1068, 206, "Stress against strain, as the bar pulls", 24, bold=True, fill=INK, a=a2)
            b0 = self.bars[0]
            u = lin(t, *self.T_PULL)
            um = lin(t, *self.T_MORE)
            for j, b in enumerate(self.bars[1:]):          # the other two bars, quicker and quieter
                uj = min(1.0, max(0.0, um * 2 - j))
                ax.line(cv, b["e"], b["s"], mix(G.PLOT_FILL, col, 0.62), 2.6, uj, a2)
            f_idx = float(np.interp(u, self.arc, np.arange(len(self.arc)))) / max(1, len(self.arc) - 1)
            pen = ax.line(cv, b0["e"], b0["s"], col, 4.2, f_idx if u < 1 else 1.0, a2)
            if pen and 0 < u < 1:
                cv.circle(pen[0], pen[1], 8, fill=G.HOT, outline=INK, width=2, a=a2)
            if u >= 1:
                X_, Y_ = ax.X(b0["ef"]), ax.Y(b0["sf"])
                k = ramp(t, self.T_PULL[1], self.T_PULL[1] + 0.35)
                cv.line([(X_ - 9, Y_ - 9), (X_ + 9, Y_ + 9)], INK, 3, a2 * k)
                cv.line([(X_ - 9, Y_ + 9), (X_ + 9, Y_ - 9)], INK, 3, a2 * k)
                cv.text(X_ + 14, Y_ + 4, "fracture", 18, fill=INK, anchor="lm", a=a2 * k * (1 - ramp(t, 22.4, 22.9)))
            # the marks on bar 1: yield (0.2 % offset), UTS, elongation after fracture
            m0, m1 = self.T_MARK
            E = b0["E"] * 1000.0 / 100.0                   # MPa per % strain
            ky = ramp(t, m0, m0 + 0.9)
            if ky > 0 and b0["ys"]:
                ey = float(b0["e"][b0["iy"]])
                x_off = ey - b0["ys"] / E
                top = min(b0["ys"] * 1.12, ax.ylim[1])
                cv.dashed([(float(ax.X(x_off)), float(ax.Y(0))),
                           (float(ax.X(x_off + top / E * ky)), float(ax.Y(top * ky)))], INK, 2, 9, 6, a2)
                kd = ramp(t, m0 + 0.7, m0 + 1.2)
                ax.dot(cv, ey, b0["ys"], G.HOT, 7, a=a2 * kd)
                cv.text(float(ax.X(ey)) + 16, float(ax.Y(b0["ys"])) + 22, "yield: where the 0.2 % offset line "
                        "meets the curve", 18, fill=INK, anchor="la", a=a2 * kd)
            ku = ramp(t, m0 + 1.5, m0 + 2.1)
            if ku > 0:
                ax.hline(cv, b0["uts"], INK2, a2 * ku, x_to=b0["eu"])
                ax.dot(cv, b0["eu"], b0["uts"], G.HOT, 7, a=a2 * ku)
                cv.text(float(ax.X(b0["eu"])), float(ax.Y(b0["uts"])) - 18, "tensile strength (UTS): the maximum",
                        18, fill=INK, anchor="ms", a=a2 * ku)
            ke = ramp(t, m0 + 2.6, m0 + 3.3)
            if ke > 0:
                x_el = b0["ef"] - b0["sf"] / E
                cv.dashed([(float(ax.X(b0["ef"])), float(ax.Y(b0["sf"]))), (float(ax.X(x_el)), float(ax.Y(0)))], INK,
                          2, 9, 6, a2 * ke)
                Y0 = float(ax.Y(0))
                cv.line([(float(ax.X(0)), Y0 - 16), (float(ax.X(x_el)), Y0 - 16)], G.HOT, 4, a2 * ke)
                for xx in (0.0, x_el):
                    cv.line([(float(ax.X(xx)), Y0 - 24), (float(ax.X(xx)), Y0 - 8)], G.HOT, 3, a2 * ke)
                cv.text(float(ax.X(x_el / 2)), Y0 - 30, "elongation after fracture", 18, fill=INK, anchor="ms",
                        a=a2 * ke)
            # the read-outs: the mean of the three bars, as the analysis reports it
            f = self.f
            for k_, (lab, val, unit, tt) in enumerate((
                    ("yield strength (0.2 %)", fmt(f["ys_MPa"]), "MPa", m0 + 0.9),
                    ("tensile strength", fmt(f["uts_MPa"]), "MPa", m0 + 1.9),
                    ("elongation", fmt(f["el_pct"], 1), "%", m0 + 3.1))):
                kk = ramp(t, tt, tt + 0.5)
                used = k_ != 1 and t >= self.T_NET
                x = 1068 + k_ * 262
                if used:
                    kn = ramp(t, self.T_NET, self.T_NET + 0.6)
                    cv.rect((x - 14, 766, x + 236, 866), fill=mix(G.CARD_FILL, col, 0.30 * kn),
                            outline=mix(G.CARD_EDGE, col, kn), width=3, radius=10, a=a2)
                cv.value(x, 778, lab, val, unit, a=a2 * kk, size=40, label_size=18)
            kn = ramp(t, self.T_NET, self.T_NET + 0.7)
            cv.text(1068, 884, "mean of three bars", 18, cond=True, fill=INK2,
                    a=a2 * ramp(t, m0 + 0.9, m0 + 1.4) * (1 - kn))
            cv.text(1068, 884, "→ the tensile node's two outputs: yield strength and elongation", 20, bold=True,
                    fill=INK, a=a2 * kn)
            cv.tag(1068, 716, "sim", "the twin's tensile test of this alloy (three bars, full fidelity)",
                   a=a2 * ramp(t, self.T_PULL[0], self.T_PULL[0] + 0.6))


if __name__ == "__main__":
    import sys
    from PIL import Image
    seg = Mech()
    for tt in [float(v) for v in sys.argv[1:]] or [3.0, 7.5, 12.0, 17.0, 20.5, 25.0, 30.0]:
        Image.fromarray(seg.frame(tt)).save(f"/tmp/vid/exp_mech_{tt:05.1f}.png")
        print("wrote", f"/tmp/vid/exp_mech_{tt:05.1f}.png")
    seg.close()
