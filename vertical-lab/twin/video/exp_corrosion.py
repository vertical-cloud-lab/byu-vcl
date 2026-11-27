"""Copper's corrosion: the one-hour screen with its potential drawn as the hour runs and its two scans, then the
30-day immersion with the mass loss plotted as each reading comes in (twin/video/exp_corrosion.py).

    Corrosion().frame(t)      0 <= t <= Corrosion.DURATION

What is what on screen:

* **The screen's curves and numbers** are the twin's simulated CubXL screen of the alloy followed
  (twin/instruments/corrosion.py ``measure_screen`` at full fidelity: the open-circuit potential over the hour, the
  linear polarization scan and the cyclic polarization scan, and that module's own analysis of them: polarization
  resistance, early corrosion rate, breakdown potential). The impedance spectrum it also records is named, not drawn.
* **The immersion's points** are the twin's too: the interim readings the campaign takes on days 1, 3, 7 and 14
  (twin/campaign.py ``_interim``: the coupon weighed as it is, uncleaned, so it reads low) and the day-30 result
  (``measure_immersion`` at full fidelity: the cleaned coupon's mass loss, the deepest selective attack in the
  section's SEM fields, copper and nickel in the solution by ICP-MS).
* **The deposit they are measured on** is this alloy's larger deposit, made again through the twin's truth at example
  settings (twin/instruments/micro.py ``CU_PROC``), not the replayed run's own deposits: in that run the screen ran
  on a small block on day 10 and the coupon came from a larger deposit half a year later. The strip of days is read
  from that run's event log.
* **The cell and the beaker** are schematics (illustrative); the coupon dulls with the twin's own film time constant.
  **The deck with the pipette** is the lab's 3-D model (PR 318's render of the CubXL dosing seawater).
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image

from . import data as D
from . import exp_data as X
from . import exp_draw as G
from . import style as St
from .exp_draw import Axes, Canvas, Segment, fmt, lin, ramp
from .style import CAMP, INK, INK2, mix

RENDER = ("vlm_workflow", 89.7, 95.3)              # PR 318: the CubXL's pipette dosing seawater, close up
RENDER_CROP_720 = (550, 168, 581, 327)             # in a 1280 x 720 frame: clear of the gauge table and caption band
WATER = (46, 104, 162)
BRONZE = (214, 170, 96)                            # the fresh coupon (a schematic's colour, not a measurement)
DULL = (128, 96, 70)                               # its colour under a mature film
DONE0 = ("composition", "calphad", "powder", "ded_small", "section", "pip")
TITLES = ("Copper: one hour in the screen", "Copper: thirty days in seawater")   # the header's, by half


def _alpha_text(cv: Canvas):
    """Kept for its caller: exp_draw.Canvas.text now fades a text itself (through a mask of its glyphs), which this
    module first had to do on its own."""
    return None


def run_span(alloy) -> dict:
    """{what: (first start, last end)} in days, for this design's bookings in the replayed run's own log."""
    ev = X._events(alloy.events)
    out = {}
    for e in ev["events"]:
        if e["campaign"] == alloy.campaign and e.get("design") == alloy.design_id:
            a, b = e["t0_h"] / D.HPD, e["t1_h"] / D.HPD
            lo, hi = out.get(e["what"], (a, b))
            out[e["what"]] = (min(lo, a), max(hi, b))
    return out


def _days(a: float, b: float | None = None) -> str:
    a_ = int(round(a))
    if b is None or int(round(b)) == a_:
        return f"day {a_}"
    return f"days {a_} to {int(round(b))}"


class Corrosion(Segment):
    key = "corrosion"
    title = "Copper: one hour in the screen, thirty days in seawater"
    campaign = "onr_cu"
    nodes = ("screen", "immersion")
    done = DONE0
    DURATION = 34.0
    T_OCP = (0.8, 8.0)           # the hour at rest: the potential drawn as the clock runs
    T_LPR = (8.4, 10.2)          # the linear polarization scan
    T_CP = (10.4, 13.2)          # the cyclic polarization scan, out and back
    T_OUT = 13.3                 # the screen's two outputs
    T_SWAP = (15.4, 16.6)        # screen -> immersion
    T_DAYS = (16.9, 27.0)        # day 0 to day 30
    T_NET = 29.6                 # what the network takes

    def __init__(self):
        super().__init__()
        X._twin()
        from twin.instruments import corrosion as CR
        cu = X.alloy("onr_cu")
        self.alloy = cu
        self.F = X.load_facts()["cu"]
        scr, imm = cu.measure("corrosion_screen"), cu.immersion()
        self.scr, self.imm = scr, imm
        r = scr["raw"]
        # ---- the screen
        self.ocp_t = np.asarray(r["ocp_t_s"], float) / 60.0
        self.ocp_E = np.asarray(r["ocp_E_mV"], float)
        self.minutes = float(self.ocp_t[-1])
        lo, hi = math.floor(self.ocp_E.min() / 20.0) * 20.0, math.ceil(self.ocp_E.max() / 20.0) * 20.0
        self.ax_ocp = Axes((1068, 246, 1816, 414), (0.0, self.minutes), (lo, hi), "minutes at rest",
                           "mV vs Ag/AgCl", xticks=list(range(0, int(self.minutes) + 1, 10)),
                           yticks=list(np.arange(lo, hi + 1, 20.0)), yfmt="{:.0f}")
        self.lpr_E, self.lpr_i = np.asarray(r["lpr_E_mV"], float), np.asarray(r["lpr_i_uA_cm2"], float)
        im = float(np.ceil(np.abs(self.lpr_i).max() * 10 + 1) / 10)
        e0 = float(r["lpr_Eoc_mV"])
        self.ax_lpr = Axes((1068, 572, 1372, 716), (-im, im), (e0 - 12.0, e0 + 12.0), "current, µA/cm²",
                           "potential, mV", xticks=[-0.5, 0.0, 0.5], yticks=[round(e0 - 10), round(e0), round(e0 + 10)],
                           yfmt="{:.0f}")
        self.lpr_fit = (float(r["lpr_fit"]["slope_mV_per_uA_cm2"]), float(r["lpr_fit"]["intercept_mV"]))
        self.lpr_half = float(self.lpr_E.max() - self.lpr_E.min()) / 2.0             # the scan's half-width, mV
        cpE, cpi = np.asarray(r["cp_E_mV"], float), np.asarray(r["cp_i_uA_cm2"], float)
        self.cp_E, self.cp_i = cpE, np.maximum(np.abs(cpi), 0.012)
        self.cp_turn = int(np.argmax(cpE))
        elo, ehi = math.floor(cpE.min() / 100.0) * 100.0, math.ceil(cpE.max() / 100.0) * 100.0
        self.ax_cp = Axes((1496, 572, 1816, 716), (0.01, 3000.0), (elo, ehi), "current, µA/cm² (log)", "",
                          xticks=[0.01, 1, 100], yticks=list(np.arange(elo, ehi + 1, 200.0)), yfmt="{:.0f}",
                          logx=True)
        fwd = np.arange(0, self.cp_turn + 1)
        self.cp_ib = int(fwd[np.argmax(cpE[fwd] >= scr["Eb_mV"])]) if (cpE[fwd] >= scr["Eb_mV"]).any() else None
        self.cp_minutes = len(cpE) / float(r["cp_rate_mV_s"]) / 60.0 * float(np.median(np.abs(np.diff(cpE))))
        self.area = float(r["area_cm2"])
        # ---- the immersion
        self.days = float(self.F["immersion"]["days"])
        it = imm["interim"]
        self.pts = [(float(d), float(m["mass_change_mg"]), float(m["rate_um_yr"])) for d, m in sorted(it.items())]
        fin = imm["final"]
        self.final = (self.days, float(fin["raw"]["mass_loss_mg"]), float(fin["rate30_um_yr"]))
        ymax = math.ceil(max(self.final[1], max(p[1] for p in self.pts)) * 1.12)
        self.ax_m = Axes((1068, 250, 1816, 548), (0.0, self.days + 2.0), (0.0, float(ymax)), "days in seawater",
                         "mass loss, mg", xticks=[0] + [int(p[0]) for p in self.pts] + [int(self.days)],
                         yticks=list(range(0, int(ymax) + 1)))
        self.icp_days = [float(d) for d in fin["raw"]["icp_days"]]
        self.icp_cu = [float(v) for v in fin["raw"]["icp_cu_ppb"]]
        self.fields = int(len(fin["raw"]["sem_field_max_um"]))
        self.cu_ppb, self.ni_ppb = float(fin.get("cu_ppb", 0.0)), float(fin.get("ni_ppb", 0.0))
        self.tau = float(cu.part["corrosion"]["film_days"])
        self.coupon_mm = tuple(CR.COUPON_MM)
        self.sol_mL, self.draw_mL = CR.V_SOL_L * 1000.0, CR.DRAW_L * 1000.0
        self.span = run_span(cu)
        self.proc = cu.proc
        self._clip = None
        self._bgs = [None, None]
        self._phase = 0
        self._mid = 0.5 * (self.T_SWAP[0] + self.T_SWAP[1])
        ds = [str(int(p[0])) for p in self.pts]
        read = ", ".join(ds[:-1]) + " and " + ds[-1] if len(ds) > 1 else ds[0]
        self.captions = [
            (0.6, 8.0, "A one-hour corrosion screen ranks the deposits before bars are made and tested."),
            (8.3, 15.2, "Two quick scans follow the hour at rest. The network takes the early rate and the "
                        "breakdown potential."),
            (16.7, 27.0, f"Then {fmt(self.days)} days in seawater, read on days {read} on the way, and ICP-MS of "
                         "what dissolved."),
            (27.3, 33.6, "The 30-day rate and the selective attack are the immersion node's outputs. A policy may "
                         "stop a coupon early."),
        ]
        self.marks = {"corrosion.screen": 0.6, "corrosion.ocp": self.T_OCP[0], "corrosion.scans": self.T_LPR[0],
                      "corrosion.screen_out": self.T_OUT, "corrosion.immersion": self.T_SWAP[1],
                      "corrosion.day30": self.T_DAYS[1], "corrosion.net": self.T_NET}
        for d, _, _ in self.pts:
            self.marks[f"corrosion.day{int(d)}"] = round(self._t_of_day(d), 2)
        self.sources = [
            ("sim", "open-circuit potential, linear and cyclic polarization, early rate, breakdown potential: "
                    "twin/instruments/corrosion.py measure_screen (full fidelity) on the alloy followed"),
            ("sim", "interim readings (twin/campaign.py _interim) and the day-30 result (measure_immersion, full "
                    "fidelity): mass loss, 30-day rate, selective attack, ICP-MS"),
            ("sim", "the deposit: this alloy's larger deposit made again at example settings (micro.CU_PROC), not "
                    "the replayed run's own"),
            ("illus", "the cell and the beaker; the coupon dulls with the twin's film time constant"),
            ("render", "the CubXL dosing seawater: PR 318's render (vlm_workflow)"),
        ]

    # ------------------------------------------------------------------------------------------ time
    def _day_at(self, t: float) -> float:
        """The immersion's clock: slow over the first days, when the readings come close together."""
        return self.days * lin(t, *self.T_DAYS) ** 1.6

    def _t_of_day(self, d: float) -> float:
        a, b = self.T_DAYS
        return a + (b - a) * (d / self.days) ** (1 / 1.6)

    # ------------------------------------------------------------------------------------------ the header by half
    def frame(self, t: float) -> np.ndarray:
        self._phase = 0 if t < self._mid else 1
        return super().frame(t)

    def _static(self) -> np.ndarray:
        ph = self._phase
        if self._bgs[ph] is None:
            keep = (self.nodes, self.done, self.title)
            self.title = TITLES[ph]
            self.nodes = ("screen",) if ph == 0 else ("immersion",)
            self.done = DONE0 if ph == 0 else DONE0 + ("screen", "tensile")
            self._bg = None
            self._bgs[ph] = super()._static()
            self._bg = None
            self.nodes, self.done, self.title = keep
        return self._bgs[ph]

    def static_extra(self, cv: Canvas):
        cv.card((56, 150, 900, 936), "The experiment")
        cv.card((940, 150, 1864, 936), "Its data")
        self._path(cv, self._phase)

    def _reader(self):
        if self._clip is None:
            from . import assets as A
            src = A.src(RENDER[0])
            k = A.probe(src)[0] / 1280.0
            x, y, w, h = (int(round(v * k)) for v in RENDER_CROP_720)
            self._clip = G.Footage(src, RENDER[1], RENDER[2], 520, 293, (x, y, w - w % 2, h - h % 2), 0.8)
        return self._clip

    def close(self):
        if self._clip is not None:
            self._clip.close()
        self._clip = None

    # ------------------------------------------------------------------------------------------ the run's own days
    def _path(self, cv: Canvas, phase: int):
        """This design's steps in the replayed run, with the days its own event log gives."""
        sp = self.span
        small = next((k for k in ("blend_ded", "blown_small", "preplaced") if k in sp), None)
        chips = []
        if small and "screen" in sp:
            chips.append((_days(sp[small][0]), ["DED blocks, PIP,", "the one-hour screen"], 0))
        if "charge" in sp and "atomize" in sp:
            chips.append((_days(sp["charge"][0], sp.get("powder QC", sp["atomize"])[1]), ["its powder", "atomized"],
                          None))
        if "blown_large" in sp:
            chips.append((_days(sp["blown_large"][0]), ["a larger deposit;", "bars pulled"], None))
        if "immersion" in sp:
            chips.append((_days(sp["immersion"][0], sp["immersion"][0] + self.days), ["30 days", "in seawater"], 1))
        if not chips:
            return
        col = CAMP[self.campaign]
        cv.text(78, 668, f"This alloy in the replayed run (seed {self.alloy.seed}), from its event log", 19,
                bold=True, fill=INK)
        n = len(chips)
        gap = 22.0
        w = (800.0 - (n - 1) * gap) / n
        for i, (when, lines, ph) in enumerate(chips):
            x = 78 + i * (w + gap)
            on = ph == phase
            cv.rect((x, 702, x + w, 800), fill=mix(G.CARD_FILL, col, 0.26) if on else G.PLOT_FILL,
                    outline=col if on else G.CARD_EDGE, width=3 if on else 2, radius=10)
            cv.text(x + 14, 713, when, 18, bold=True, fill=INK)
            for j, ln in enumerate(lines):
                cv.text(x + 14, 742 + j * 23, ln, 17, cond=True, fill=INK if on else INK2)
            if i < n - 1:
                cv.arrow((x + w + 3, 751), (x + w + gap - 3, 751), St.RULE, 2, 8)
        p = self.proc
        if phase == 0:
            cv.para(78, 818, "Small DED blocks come first: density, cracks and dilution at each set of settings. "
                             "The screen shown here is the twin's, on this alloy's deposit made again at example "
                             f"settings ({fmt(p['P_W'])} W, {fmt(p['v_mm_min'])} mm/min, {fmt(p['feed_g_min'])} "
                             "g/min).", 18, 800, fill=INK2, cond=True)
        else:
            cv.para(78, 818, "After any interim reading the policy may take a coupon out (round 3's rule). "
                             "Selective attack does not show in a mass: it is read on day 30, in the section.", 18,
                    800, fill=INK2, cond=True)

    # ------------------------------------------------------------------------------------------ the screen
    def _cell(self, cv: Canvas, a: float, e_now: float | None):
        """The screen's cell (illustrative): an O-ring well on the deposit, seawater, three electrodes."""
        x0, y0, x1, y1 = 616, 196, 878, 489
        cv.rect((x0, y0, x1, y1), fill=G.PLOT_FILL, outline=G.CARD_EDGE, width=2, radius=10, a=a)
        cx = (x0 + x1) / 2
        top = y1 - 96
        cv.rect((x0 + 22, top, x1 - 22, y1 - 44), fill=BRONZE, outline=(240, 214, 160), width=2, a=a)   # the deposit
        cv.text(cx, y1 - 70, "the deposit", 17, bold=True, cond=True, fill=(30, 22, 10), anchor="mm", a=a)
        wl, wr = cx - 52, cx + 52
        cv.rect((wl - 12, top - 112, wl, top), fill=(120, 126, 138), a=a)                                # the well
        cv.rect((wr, top - 112, wr + 12, top), fill=(120, 126, 138), a=a)
        cv.rect((wl, top - 96, wr, top), fill=WATER + (190,), a=a)
        for xx in (wl - 6, wr + 6):
            cv.circle(xx, top - 3, 6, fill=(18, 18, 20), outline=(90, 94, 104), width=1, a=a)            # the O-ring
        cv.rect((cx - 30, y0 + 44, cx - 22, top - 34), fill=(210, 214, 222), a=a)                        # reference
        cv.circle(cx - 26, top - 32, 5, fill=(236, 238, 244), a=a)
        cv.line([(cx + 26, y0 + 44), (cx + 26, top - 60)], (226, 228, 236), 3, a)                        # counter
        for k in range(4):
            yy = top - 58 + k * 8
            cv.line([(cx + 18, yy), (cx + 34, yy + 4)], (226, 228, 236), 2, a)
        cv.text(cx - 34, y0 + 30, "reference", 16, cond=True, fill=INK, anchor="rs", a=a)
        cv.text(cx + 34, y0 + 30, "counter", 16, cond=True, fill=INK, anchor="ls", a=a)
        cv.text(wl - 18, top - 60, "seawater", 16, cond=True, fill=INK, anchor="rm", a=a)
        cv.text(wr + 18, top - 60, "O-ring", 16, cond=True, fill=INK, anchor="lm", a=a)
        cv.text(wr + 18, top - 40, "well", 16, cond=True, fill=INK, anchor="lm", a=a)
        cv.text(cx, y1 - 22, f"wetted area {self.area:g} cm²", 16, cond=True, fill=INK2, anchor="mm", a=a)
        if e_now is not None:
            cv.rect((x0 + 10, y0 + 54, x0 + 96, y0 + 104), fill=(10, 12, 16, 230), outline=G.CARD_EDGE, radius=8, a=a)
            cv.text(x0 + 53, y0 + 70, f"{fmt(e_now)}", 22, bold=True, fill=INK, anchor="mm", a=a)
            cv.text(x0 + 53, y0 + 91, "mV", 16, cond=True, fill=INK2, anchor="mm", a=a)

    def _steps(self, cv: Canvas, t: float, a: float):
        """The screen's protocol as a bar, the step in hand lit."""
        col = CAMP[self.campaign]
        seg = [("at rest: open-circuit potential", f"{fmt(self.minutes)} min", 0.50, self.T_OCP),
               ("impedance", "not drawn", 0.14, (self.T_OCP[1], self.T_LPR[0])),
               ("linear scan", f"±{fmt(self.lpr_half)} mV", 0.15, self.T_LPR),
               ("cyclic scan", f"about {fmt(self.cp_minutes)} min", 0.21, self.T_CP)]
        x = 78.0
        for name, sub, share, (ta, tb) in seg:
            w = 800.0 * share
            on = ta <= t < tb
            was = t >= tb
            cv.rect((x + 2, 544, x + w - 2, 570), fill=mix(G.PLOT_FILL, col, 0.5 if on else (0.34 if was else 0.0)),
                    outline=col if on else G.CARD_EDGE, width=2, radius=6, a=a)
            if on:
                u = lin(t, ta, tb)
                cv.rect((x + 2, 544, x + 2 + (w - 4) * u, 570), fill=col, radius=6, a=a)
            cv.text(x + w / 2, 588, name, 16, bold=on, cond=True, fill=INK if (on or was) else INK2, anchor="mm", a=a)
            cv.text(x + w / 2, 609, sub, 16, cond=True, fill=INK2, anchor="mm", a=a)
            x += w

    def _screen(self, cv: Canvas, t: float, a: float):
        col = CAMP[self.campaign]
        F = self.F["screen"]
        # ---- left
        u = lin(t, *self.T_OCP)
        i_now = int(round(u * (len(self.ocp_E) - 1)))
        cv.paste(self._reader().frame(max(0.0, t - 0.2)), 78, 196, a=a)
        G.framed(cv, (78, 196, 598, 489), "the CubXL dosing seawater", a=a)
        cv.tag(88, 449, "render", "the lab's 3-D model (PR 318)", a=a)
        self._cell(cv, a, float(self.ocp_E[i_now]) if t < self.T_LPR[0] else None)
        cv.tag(616, 494, "illus", "the cell", a=a)
        self._steps(cv, t, a)
        # ---- right: the hour at rest
        ax = self.ax_ocp
        ax.draw(cv, a)
        cv.text(1068, 204, "The hour at rest: the open-circuit potential", 24, bold=True, fill=INK, a=a)
        pen = ax.line(cv, self.ocp_t, self.ocp_E, col, 3.6, u, a)
        if pen and 0 < u < 1:
            cv.circle(pen[0], pen[1], 8, fill=G.HOT, outline=INK, width=2, a=a)
        cv.text(1816, 208, f"{fmt(u * self.minutes)} min" if u < 1 else f"{fmt(self.minutes)} min", 24, bold=True,
                fill=INK, anchor="ra", a=a * ramp(t, self.T_OCP[0], self.T_OCP[0] + 0.4))
        cv.tag(1068, 474, "sim", "the twin's CubXL screen of this alloy's deposit (full fidelity)",
               a=a * ramp(t, self.T_OCP[0], self.T_OCP[0] + 0.6))
        # ---- the linear polarization scan
        wait = 0.34 * ramp(t, self.T_OCP[0] + 0.4, self.T_OCP[0] + 1.2)      # both scans' axes wait, dimmed
        kl = max(wait, ramp(t, self.T_LPR[0] - 0.4, self.T_LPR[0]))
        if kl > 0:
            al = self.ax_lpr
            al.draw(cv, a * kl, size=16)
            cv.text(1068, 516, "Linear scan: the slope is the", 18, bold=True, cond=True, fill=INK, a=a * kl)
            cv.text(1068, 539, "polarization resistance", 18, bold=True, cond=True, fill=INK, a=a * kl)
            ul = lin(t, *self.T_LPR)
            al.line(cv, self.lpr_i, self.lpr_E, col, 3.2, ul, a * kl)
            kf = ramp(t, self.T_LPR[1], self.T_LPR[1] + 0.4)
            if kf > 0:
                xs = np.array(al.xlim) * 0.92
                al.line(cv, xs, self.lpr_fit[0] * xs + self.lpr_fit[1], INK, 2.0, 1.0, a * kf, dashed=True)
        # ---- the cyclic polarization scan
        kc = max(wait, ramp(t, self.T_CP[0] - 0.4, self.T_CP[0]))
        if kc > 0:
            ac = self.ax_cp
            ac.draw(cv, a * kc, size=16)
            cv.text(1496, 516, "Cyclic scan: where the film", 18, bold=True, cond=True, fill=INK, a=a * kc)
            cv.text(1496, 539, "breaks down (potential, mV)", 18, bold=True, cond=True, fill=INK, a=a * kc)
            uc = lin(t, *self.T_CP)
            n = len(self.cp_E)
            k_now = uc * (n - 1)
            kt = self.cp_turn
            ac.line(cv, self.cp_i[:kt + 1], self.cp_E[:kt + 1], col, 3.2, min(1.0, k_now / kt), a * kc)
            if k_now > kt:
                ac.line(cv, self.cp_i[kt:], self.cp_E[kt:], mix(G.PLOT_FILL, col, 0.6), 2.4,
                        (k_now - kt) / max(1, n - 1 - kt), a * kc)
            if self.cp_ib is not None and k_now >= self.cp_ib:
                kb = ramp(t, self._t_cp(self.cp_ib), self._t_cp(self.cp_ib) + 0.35)
                ac.hline(cv, self.scr["Eb_mV"], INK2, a * kc * kb)
                ac.dot(cv, self.cp_i[self.cp_ib], self.cp_E[self.cp_ib], G.HOT, 6, a=a * kc * kb)
                cv.text(float(ac.X(0.012)) + 8, float(ac.Y(self.scr["Eb_mV"])) - 8, "breakdown", 16, cond=True,
                        fill=INK, anchor="ls", a=a * kc * kb)
        # ---- the read-outs
        kn = ramp(t, self.T_OUT, self.T_OUT + 0.6)
        outs = [("early corrosion rate", fmt(F["early_um_yr"]), "µm per year", self.T_LPR[1] + 0.3, True),
                ("breakdown potential", fmt(F["Eb_mV"]), "mV", self.T_CP[0] + 1.6, True),
                ("polarization resistance", fmt(F["rp_kohm_cm2"], 1), "kΩ cm²", self.T_LPR[1] + 0.3, False)]
        for k_, (lab, val, unit, tt, used) in enumerate(outs):
            kk = ramp(t, tt, tt + 0.5)
            x = 1068 + k_ * 262
            if used and kn > 0:
                cv.rect((x - 14, 780, x + 240, 874), fill=mix(G.CARD_FILL, col, 0.30 * kn),
                        outline=mix(G.CARD_EDGE, col, kn), width=3, radius=10, a=a)
            cv.value(x, 790, lab, val, unit, a=a * kk, size=38, label_size=18)
        cv.text(1068, 890, "→ these two are the screen node's outputs", 20, bold=True, fill=INK, a=a * kn)

    def _t_cp(self, i: int) -> float:
        return self.T_CP[0] + (self.T_CP[1] - self.T_CP[0]) * i / max(1, len(self.cp_E) - 1)

    # ------------------------------------------------------------------------------------------ the immersion
    @staticmethod
    def _pill(cv: Canvas, cx: float, cy: float, words: str, a: float):
        w = cv.text_w(words, 17, bold=True, cond=True) + 30
        cv.rect((cx - w / 2, cy - 16, cx + w / 2, cy + 16), fill=G.HOT, radius=16, a=a)
        cv.text(cx, cy, words, 17, bold=True, cond=True, fill=(24, 18, 8), anchor="mm", a=a)

    def _beaker(self, cv: Canvas, t: float, a: float, day: float):
        """The coupon in its beaker (illustrative), the day counter and the 30 days' events."""
        col = CAMP[self.campaign]
        x0, y0, x1, y1 = 78, 196, 468, 646
        cv.rect((x0, y0, x1, y1), fill=G.PLOT_FILL, outline=G.CARD_EDGE, width=2, radius=10, a=a)
        bl, br, bt, bb = x0 + 62, x1 - 62, y0 + 70, y1 - 74
        lvl = bt + 62
        cv.rect((bl + 3, lvl, br - 3, bb - 3), fill=WATER + (170,), a=a)
        cv.line([(bl, bt), (bl, bb - 14), (bl + 14, bb), (br - 14, bb), (br, bb - 14), (br, bt)], (176, 190, 206), 3, a)
        cv.line([(bl - 10, bt), (bl, bt)], (176, 190, 206), 3, a)
        cv.line([(br, bt), (br + 10, bt)], (176, 190, 206), 3, a)
        cx = (bl + br) / 2
        cv.line([(bl - 20, bt - 22), (br + 20, bt - 22)], (150, 156, 168), 5, a)                 # the rod it hangs from
        cv.line([(cx, bt - 22), (cx, lvl + 86)], (210, 214, 222), 2, a)
        m = 1.0 - math.exp(-day / self.tau)                                                      # the film's growth
        cw, ch = 118.0, 62.0
        cy = lvl + 86
        cv.rect((cx - cw / 2, cy, cx + cw / 2, cy + ch), fill=mix(BRONZE, DULL, m), outline=(240, 214, 160),
                width=2, radius=4, a=a)
        cv.circle(cx, cy + 9, 4, fill=G.PLOT_FILL, a=a)
        cm = self.coupon_mm
        cv.text(cx, cy + ch + 20, f"the coupon, {cm[0]:g} × {cm[1]:g} × {cm[2]:g} mm", 17, cond=True, fill=INK,
                anchor="mm", a=a)
        cv.text(cx, bb - 22, f"{fmt(self.sol_mL)} mL of artificial seawater", 17, cond=True, fill=INK, anchor="mm",
                a=a)
        cv.tag(x0 + 12, y1 - 42, "illus", "the beaker and the coupon", a=a)
        # what is happening to it now
        for d, _, _ in self.pts:
            k = St.window(t, self._t_of_day(d), self._t_of_day(d) + 1.0, 0.2)
            if k > 0:
                self._pill(cv, cx, y0 + 28, f"day {int(d)}: out, weighed, back in", a * k)
        k = ramp(t, self.T_DAYS[1], self.T_DAYS[1] + 0.4)
        if k > 0:
            self._pill(cv, cx, y0 + 28, f"day {fmt(self.days)}: out, cleaned, weighed", a * k)
        # ---- the day counter and the days' events
        px0, px1 = 490, 878
        cv.rect((px0, y0, px1, y1), fill=G.PLOT_FILL, outline=G.CARD_EDGE, width=2, radius=10, a=a)
        cv.text(px0 + 24, y0 + 22, "day", 22, cond=True, fill=INK2, a=a)
        cv.text(px0 + 24, y0 + 44, f"{int(math.floor(day + 1e-6))}", 96, bold=True, fill=INK, a=a)
        cv.text(px1 - 24, y0 + 112, f"of {fmt(self.days)}", 22, cond=True, fill=INK2, anchor="ra", a=a)
        tx0, tx1, ty = px0 + 30, px1 - 30, y0 + 214
        X_ = lambda d: tx0 + (tx1 - tx0) * d / self.days
        cv.line([(tx0, ty), (tx1, ty)], St.RULE, 3, a)
        cv.rect((tx0, ty - 3, X_(day), ty + 3), fill=col, a=a)
        cv.circle(X_(day), ty, 8, fill=G.HOT, outline=INK, width=2, a=a)
        for d, _, _ in self.pts:                                          # weighings above the line
            on = day >= d
            cv.circle(X_(d), ty - 26, 7, fill=INK if on else None, outline=INK if on else INK2, width=2, a=a)
        for j, (d, ppb) in enumerate(zip(self.icp_days, self.icp_cu)):    # solution drawn, below it
            on = day >= d - 1e-6
            xx = X_(d)
            cv.poly([(xx, ty + 18), (xx + 7, ty + 26), (xx, ty + 34), (xx - 7, ty + 26)], fill=INK if on else None,
                    outline=INK if on else INK2, width=2, a=a)
            if on:                                                        # the copper found in that draw, ppb
                last = j == len(self.icp_days) - 1
                kk = ramp(t, self._t_of_day(d), self._t_of_day(d) + 0.4)
                cv.text(xx + (8 if last else 0), ty + 42, fmt(ppb), 16, bold=last, cond=True, fill=INK,
                        anchor="ra" if last else "ma", a=a * kk)
        ly = y0 + 286
        wd = ", ".join(str(int(d)) for d, _, _ in self.pts)
        dd = ", ".join(str(int(d)) for d in self.icp_days)
        cv.circle(px0 + 34, ly + 10, 7, outline=INK, width=2, a=a)
        cv.para(px0 + 54, ly, f"weighed uncleaned: days {wd}", 17, 316, fill=INK, cond=True, a=a)
        xx, yy = px0 + 34, ly + 44
        cv.poly([(xx, yy - 8), (xx + 7, yy), (xx, yy + 8), (xx - 7, yy)], outline=INK, width=2, a=a)
        cv.para(px0 + 54, ly + 34, f"{fmt(self.draw_mL)} mL drawn for ICP-MS: days {dd}; under each, the copper "
                "found (ppb)", 17, 316, fill=INK, cond=True, a=a)
        cv.para(px0 + 24, ly + 96, f"Day {fmt(self.days)}: cleaned, weighed, then sectioned for the SEM.", 17, 340,
                fill=INK2, cond=True, a=a)

    def _immersion(self, cv: Canvas, t: float, a: float):
        col = CAMP[self.campaign]
        F = self.F["immersion"]
        day = self._day_at(t)
        self._beaker(cv, t, a, day)
        ax = self.ax_m
        ax.draw(cv, a)
        cv.text(1068, 204, "Mass loss, as each reading comes in", 24, bold=True, fill=INK, a=a)
        seen = [(0.0, 0.0)]
        rows = []
        for d, m, r in self.pts:
            k = ramp(t, self._t_of_day(d), self._t_of_day(d) + 0.4)
            if k > 0:
                seen.append((d, m))
                rows.append((f"day {int(d)}", f"{m:.2f} mg", f"{fmt(r, 1)} µm/yr", k, False))
        kf = ramp(t, self.T_DAYS[1] + 0.5, self.T_DAYS[1] + 1.1)
        if kf > 0:
            rows.append((f"day {fmt(self.final[0])}", f"{fmt(self.final[1], 1)} mg", f"{fmt(self.final[2], 1)} "
                         f"µm/yr", kf, True))
        if len(seen) > 1:
            xs, ys = [p[0] for p in seen], [p[1] for p in seen]
            ax.line(cv, xs, ys, mix(G.PLOT_FILL, col, 0.75), 2.6, 1.0, a)
        for (d, m, _r) in self.pts:
            k = ramp(t, self._t_of_day(d), self._t_of_day(d) + 0.4)
            if k > 0:
                Xp, Yp = float(ax.X(d)), float(ax.Y(m))
                cv.circle(Xp, Yp, 9, fill=G.PLOT_FILL, outline=col, width=4, a=a * k)
        if kf > 0:
            ax.line(cv, [self.pts[-1][0], self.final[0]], [self.pts[-1][1], self.final[1]], mix(G.PLOT_FILL, col, 0.75),
                    2.6, kf, a, dashed=True)
            ax.dot(cv, self.final[0], self.final[1], col, 9, a=a * kf)
            cv.text(float(ax.X(self.final[0])) - 16, float(ax.Y(self.final[1])) - 4, "cleaned", 17, cond=True,
                    fill=INK, anchor="rs", a=a * kf)
        # the table of readings, in the plot's empty corner
        tx, ty = 1484, 372
        if rows:
            cv.rect((tx - 14, ty - 10, 1808, ty + 168), fill=(12, 14, 18, 215), outline=G.CARD_EDGE, radius=8, a=a)
            cv.text(tx, ty, "reading", 16, cond=True, fill=INK2, a=a)
            cv.text(tx + 88, ty, "mass loss", 16, cond=True, fill=INK2, a=a)
            cv.text(tx + 186, ty, "rate so far", 16, cond=True, fill=INK2, a=a)
        for i, (c0, c1, c2, k, last) in enumerate(rows):
            y = ty + 26 + i * 27
            cv.text(tx, y, c0, 18, bold=last, cond=True, fill=INK, a=a * k)
            cv.text(tx + 88, y, c1, 18, bold=last, cond=True, fill=INK, a=a * k)
            cv.text(tx + 186, y, c2, 18, bold=last, cond=True, fill=INK, a=a * k)
        # the legend and the tag
        cv.circle(1080, 618, 8, fill=G.PLOT_FILL, outline=col, width=4, a=a)
        cv.text(1098, 618, "interim: the coupon weighed as it is (uncleaned, so it reads low)", 17, cond=True,
                fill=INK, anchor="lm", a=a)
        cv.circle(1080, 648, 10.5, fill=INK, a=a)
        cv.circle(1080, 648, 8, fill=col, a=a)
        cv.text(1098, 648, f"day {fmt(self.days)}: after cleaning, the mass loss the rate comes from", 17, cond=True,
                fill=INK, anchor="lm", a=a)
        cv.tag(1068, 676, "sim", "the twin's immersion of this alloy's coupon (full fidelity)",
               a=a * ramp(t, self.T_DAYS[0], self.T_DAYS[0] + 0.6))
        # the read-outs
        kn = ramp(t, self.T_NET, self.T_NET + 0.6)
        t30 = self.T_DAYS[1]
        outs = [(f"{fmt(self.days)}-day corrosion rate", fmt(F["rate30_um_yr"], 1), "µm per year", t30 + 0.9, True),
                ("selective attack, in the section", fmt(F["attack_um"], 1), "µm", t30 + 1.4, True)]
        for k_, (lab, val, unit, tt, used) in enumerate(outs):
            kk = ramp(t, tt, tt + 0.5)
            x = 1068 + k_ * 300
            if kn > 0:
                cv.rect((x - 14, 722, x + 274, 814), fill=mix(G.CARD_FILL, col, 0.30 * kn),
                        outline=mix(G.CARD_EDGE, col, kn), width=3, radius=10, a=a)
            cv.value(x, 732, lab, val, unit, a=a * kk, size=38, label_size=17)
        kk = ramp(t, t30 + 1.9, t30 + 2.4)
        cv.text(1672, 734, "dissolved, by ICP-MS", 17, cond=True, fill=INK2, a=a * kk)
        cv.text(1672, 760, f"Cu {fmt(self.cu_ppb)} ppb", 20, bold=True, fill=INK, a=a * kk)
        cv.text(1672, 788, f"Ni {fmt(self.ni_ppb)} ppb", 20, bold=True, fill=INK, a=a * kk)
        cv.text(1068, 838, "→ these two are the immersion node's outputs", 20, bold=True, fill=INK, a=a * kn)
        cv.para(1068, 870, "Its inputs: the screen's two outputs, the retained beta-prime share, and Ni, Fe and Al. "
                           "A second node predicts the 30-day rate from each interim reading.", 17, 756, fill=INK2,
                cond=True, a=a * kn, max_lines=2)

    def draw(self, cv: Canvas, t: float):
        _alpha_text(cv)
        if self._phase == 0:
            self._screen(cv, t, 1.0 - ramp(t, self.T_SWAP[0], self._mid))
        else:
            self._immersion(cv, t, ramp(t, self._mid, self.T_SWAP[1]))


if __name__ == "__main__":
    import sys
    seg = Corrosion()
    for tt in [float(v) for v in sys.argv[1:]] or [2.0, 6.0, 9.5, 12.0, 14.5, 18.5, 22.0, 26.0, 28.5, 33.0, 34.0]:
        Image.fromarray(seg.frame(tt)).save(f"/tmp/vid/exp_corrosion_{tt:05.1f}.png")
        print("wrote", f"/tmp/vid/exp_corrosion_{tt:05.1f}.png")
    seg.close()
