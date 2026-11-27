"""SEM: one beam rastering a sample, and the four detectors' signals building up side by side
(twin/video/exp_sem.py).

    SEM().frame(t)      0 <= t <= SEM.DURATION

What is what on screen:

* **The four signals are the twin's simulated raw data for the alloy followed**, from its instrument simulators at
  full fidelity (twin/instruments/sem.py, eds.py, ebsd.py through ``exp_data.Alloy.measure``): the secondary-electron
  image of the lot's powder on carbon tape, the backscattered-electron image of the polished section of the cube the
  bars are printed beside, the EDS spectrum of the powder lot, and the EBSD orientation map of the same section with
  one Kikuchi pattern. The read-outs are those modules' own analyses of that raw data (particle segmentation, pore and
  crack detection, standardless quantification, grain reconstruction). None of it is real SEM data.
* **The EDS spectrum builds as the beam dwells**: the counts after a share u of the live time are the final spectrum
  thinned binomially (mean N u, variance N u (1 - u), one fixed normal draw per channel), which is what counting
  for a shorter time gives.
* **The element maps are illustrative.** The twin simulates a spectrum, not maps. The three maps are drawn from the
  simulated powder image's particle mask and the designed wt% of the element, with counting noise, and are tagged
  so on screen.
* **The picture of the microscope is a schematic** (the column, the scanning beam and where each detector sits; not
  to scale), drawn as one scan: in the lab the powder and the section are separate scans, and the section is tilted
  70 degrees for EBSD. The small inset is the lab's 3-D model of its desktop SEM (PR 318's render), cropped clear of
  that render's own inset micrograph.
* **Which of the four the network uses** (twin/opt/policies2.py ``datasets``, ``powder_feat``, ``section_out`` and
  twin/campaign.py ``_soundness``, ``_do_powder``): the satellite share of the powder image is an input of the print
  node (with the lot's oxygen); the section's porosity and crack density are, with the Archimedes density, the print
  node's two outputs (the reported density is the lower of the two); EBSD's grain size and equiaxed share are the
  section node's two outputs, which feed the PIP and tensile nodes; EDS is measured on every lot as a composition
  check, and no node takes it as an input.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

from . import exp_data as X
from . import exp_draw as G
from . import style as St
from .exp_draw import Axes, Canvas, Segment, fmt, lin, ramp
from .style import CAMP, INK, INK2, INK3, mix

S = St.S
LEFT = (56, 150, 648, 936)
RIGHT = (680, 150, 1864, 936)
CELL_W, CELL_H = 568, 354
CELLS = {"se": (696, 198), "bse": (1280, 198), "eds": (696, 566), "ebsd": (1280, 566)}
ORDER = ("se", "bse", "eds", "ebsd")
NUM = {"se": "1", "bse": "2", "eds": "3", "ebsd": "4"}
NAME = {"se": "Secondary electrons", "bse": "Backscattered electrons", "eds": "X-rays (EDS)",
        "ebsd": "Diffraction (EBSD)"}
SAMPLE = {"se": "the powder lot", "bse": "the polished section", "eds": "the powder lot",
          "ebsd": "the same section"}
IMG = 296                        # a micrograph's side on screen
TXT_X, TXT_W = 326, 228          # the text column of a cell, from the cell's left
XC = 286                         # the column's axis in the schematic
SURF_Y = 620                     # the sample's surface
SCAN_HALF = 50                   # half the scanned width on the sample, in the schematic
FIELD = (478, 204, 132)          # the scanned field seen from above: x, y, side
ROW0, ROW_DY, NOTE_Y = 116, 24, 214          # a cell's read-out rows and its note, from the cell's top
BADGE = (316, 256, CELL_W - 8, 348)          # a cell's "which node takes this" badge, from the cell's corner
CROP_SEM = (200, 156, 484, 404)  # PR 318's render of the SEM (1280 x 720): its body, clear of the render's gauge
#                                  table (top left), its timer chip (left) and its own inset figure (right)
MAP_N = 96                       # the illustrative element maps' pixels
MAP_AL_COUNTS = 400.0            # counts in a pixel of pure aluminium (illustrative)
MAP_BG_COUNTS = 0.4              # continuum counts in any pixel (illustrative)
MAP_WORDS = ["maps drawn from the powder image and the designed wt%, with noise",      # the longest that fits
             "maps drawn from the powder image and designed wt%, with noise",
             "maps drawn from the powder image and the designed wt%",
             "maps drawn from the powder image and designed wt%",
             "maps drawn from the powder image and the design"]


def _lut2(rgb) -> np.ndarray:
    return G._lut([(0.0, (8, 9, 12)), (0.55, tuple(int(v * 0.62) for v in rgb)), (1.0, rgb)])


MAP_LUT = [G.LUT_BLUE, _lut2((255, 176, 84)), _lut2((120, 232, 160))]


class SEM(Segment):
    key = "sem"
    title = "SEM: one beam, four signals"
    campaign = "flaime_al"
    nodes = ("section",)
    done = ("composition", "calphad", "powder", "print")
    DURATION = 38.0
    T_BEAM = (2.0, 18.0)                                            # the raster
    FOCUS = {"se": 2.4, "bse": 6.4, "eds": 10.4, "ebsd": 14.4}      # each detector's four seconds
    FOCUS_S = 4.0
    T_READ = {"se": 18.6, "bse": 19.8, "eds": 21.0, "ebsd": 22.2}   # the analyses' read-outs
    T_NET = 25.2
    NET = {"se": 25.2, "bse": 26.6, "ebsd": 28.0, "eds": 29.4}      # which the network uses, the exception last
    T_NEXT = 33.5                                                   # the next node (PIP) lights in the strip

    def __init__(self):
        super().__init__()
        a = X.alloy("flaime_al")
        self.alloy = a
        self.f = X.load_facts()["al"]
        self.col = CAMP[self.campaign]
        sp, sx, ed, eb = (a.measure(n) for n in ("sem_powder", "sem_section", "eds", "ebsd"))
        self.sp, self.sx, self.ed, self.eb = sp, sx, ed, eb
        self._clip = None
        self._prep_se()
        self._prep_bse()
        self._prep_eds()
        self._prep_ebsd()
        f = self.f
        self.captions = [
            (1.0, 6.4, "One electron beam scans the sample line by line. Each detector catches a different signal "
                       "from the spot it is on."),
            (6.6, 18.2, "Secondary electrons show the surface, backscattered electrons the composition, X-rays the "
                        "elements, diffraction the crystal's orientation."),
            (18.6, 24.8, "Every image here is simulated by the twin for this alloy. The read-outs are the twin's own "
                         "analysis of those images."),
            (25.2, 33.2, "The network uses three of the four: the powder's satellites, the section's pores and "
                         "cracks, EBSD's grains."),
            (33.5, 37.7, "Sections show pores, cracks and grains; PIP reads a stress-strain curve from one indent."),
        ]
        self.marks = {"sem.raster": self.T_BEAM[0], "sem.se": self.FOCUS["se"], "sem.bse": self.FOCUS["bse"],
                      "sem.eds": self.FOCUS["eds"], "sem.ebsd": self.FOCUS["ebsd"], "sem.done": self.T_BEAM[1],
                      "sem.read": self.T_READ["se"], "sem.net": self.T_NET, "sem.next": self.T_NEXT}
        self.sources = [
            ("sim", "secondary-electron image of the powder lot and its particle analysis: twin/instruments/sem.py "
                    "measure_powder, full fidelity, the alloy followed"),
            ("sim", "backscattered-electron image of the polished section and its pore and crack analysis: "
                    "twin/instruments/sem.py measure_section, full fidelity"),
            ("sim", "EDS spectrum of the powder lot and its standardless quantification: twin/instruments/eds.py, "
                    "full fidelity; the counts shown part-way are the final spectrum thinned binomially"),
            ("sim", "EBSD orientation map, Kikuchi pattern and grain analysis: twin/instruments/ebsd.py, full "
                    "fidelity"),
            ("illus", "element maps: drawn from the simulated powder image's particles and the designed wt%, with "
                      "counting noise; the twin simulates a spectrum, not maps"),
            ("illus", "the microscope: a schematic, not to scale, drawn as one scan"),
            ("render", "the lab's desktop SEM: PR 318's render (out/mp4/alloy_characterize.mp4), cropped"),
        ]
        # the EDS numbers the panel shows (not in facts.json when this was written; see the fork's report)
        self.numbers = dict(eds=dict(comp={e: round(float(v), 2) for e, v in ed["comp"].items()},
                                     lod={e: round(float(v), 2) for e, v in ed["lod"].items()},
                                     live_s=float(ed["raw"]["live_s"]), below=self.eds_below,
                                     invisible=self.eds_invisible),
                            fov_um=dict(se=float(sp["raw"]["fov_um"]), bse=float(sx["raw"]["fov_um"]),
                                        ebsd=[float(self.ebsd_w_um), float(self.ebsd_h_um)]))

    # ------------------------------------------------------------------------------------------ preparing the data
    def _prep_se(self):
        r = self.sp["raw"]
        im = np.asarray(r["image"], float)
        lo, hi = G.stretch(im, 1.0, 99.8)
        self.im_se = G.to_image(G.colourize(im, lo, hi, G.LUT_GRAY, 0.8), IMG, IMG)
        self.se_um_per_unit = float(r["fov_um"]) / IMG
        from scipy import ndimage
        lab = np.asarray(r["labels"])
        hosts = [int(i) for i in r["sat_hosts"]]
        sl = ndimage.find_objects(lab)
        k = IMG / lab.shape[0]
        self.se_rings = []
        for i in hosts:
            s = sl[i - 1] if 0 < i <= len(sl) else None
            if s is None:
                continue
            cy_, cx_ = (s[0].start + s[0].stop) / 2, (s[1].start + s[1].stop) / 2
            rad = max(s[0].stop - s[0].start, s[1].stop - s[1].start) / 2
            self.se_rings.append((cx_ * k, cy_ * k, rad * k + 5))

    def _prep_bse(self):
        r = self.sx["raw"]
        im = np.asarray(r["image"], float)
        lvl, sg = float(r["level"]), float(r["sigma"])
        self.im_bse = G.to_image(G.colourize(im, 0.22 * lvl, 1.45 * lvl, G.LUT_GRAY, 1.0), IMG, IMG)
        self.bse_um_per_unit = float(r["fov_um"]) / IMG
        from scipy import ndimage
        lab = np.asarray(r["labels"])
        cls = np.asarray(r["cls"])
        k = IMG / lab.shape[0]
        self.bse_pores = []
        for i, s in enumerate(ndimage.find_objects(lab), start=1):
            if s is None or i >= len(cls) or cls[i] != 1:
                continue
            cy_, cx_ = (s[0].start + s[0].stop) / 2, (s[1].start + s[1].stop) / 2
            rad = max(s[0].stop - s[0].start, s[1].stop - s[1].start) / 2
            self.bse_pores.append((cx_ * k, cy_ * k, max(rad * k + 3.5, 5.0)))
        # the cracks the analysis found: drawn over the image in the accent colour (they are a pixel or two wide)
        n = max(2, int(round(IMG * S)))
        ov = Image.new("RGBA", (n, n), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        ys, xs = np.nonzero(np.asarray(r["crack_mask"]))
        kk = n / lab.shape[0]
        rr = max(1.0, 1.6 * S)
        for x_, y_ in zip(xs, ys):
            d.ellipse((x_ * kk - rr, y_ * kk - rr, x_ * kk + rr, y_ * kk + rr), fill=G.HOT + (255,))
        self.ov_cracks = ov

    def _prep_eds(self):
        a, ed = self.alloy, self.ed
        r = ed["raw"]
        E, N = np.asarray(r["E_keV"], float), np.asarray(r["counts"], float)
        sel = (E >= 0.12) & (E <= 7.0)
        self.eds_E, self.eds_N = E[sel], N[sel]
        self.eds_z = np.random.default_rng(31).standard_normal(int(sel.sum()))
        top = 10 ** math.ceil(math.log10(max(self.eds_N.max(), 10.0)) + 0.15)
        self.eds_ylim = (1.0, top)
        # the peaks to name: the base element, the additions the quantification reported, and O and C of the surface
        want = [a.base] + list(ed["comp"]) + ["O", "C"]
        best = {}
        for el, ln, kev, inten in r["lines"]:
            if el in want and 0.2 < kev < 7.0 and ln.startswith("Ka") and inten > best.get(el, (0, 0))[1]:
                best[el] = (float(kev), float(inten))
        self.eds_peaks = sorted(((kev, el) for el, (kev, _) in best.items()))
        # designed against measured
        design = dict(sorted(a.design.items(), key=lambda kv: -kv[1]))
        self.eds_rows = [(el, design[el], float(ed["comp"][el])) for el in design if el in ed["comp"]]
        self.eds_below = [el for el in design if el not in ed["comp"] and el in ed["lod"]]
        self.eds_invisible = [el for el in design if el not in ed["comp"] and el not in ed["lod"]]
        # illustrative maps: the powder image's particles, counts in proportion to the designed wt%, counting noise
        mask = np.asarray(self.sp["raw"]["mask"], np.float32)
        cov = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).resize((MAP_N, MAP_N), Image.BOX),
                         float) / 255.0
        els = [a.base] + [el for el, _, _ in self.eds_rows[:2]]
        rng = np.random.default_rng(32)
        self.maps = []
        for j, el in enumerate(els):
            lam = MAP_AL_COUNTS * cov * a.comp[el] / 100.0 + MAP_BG_COUNTS
            c = rng.poisson(lam).astype(float)
            hi = max(float(np.percentile(c, 99.5)), 2.0)
            self.maps.append((el, G.to_image(G.colourize(c, 0.0, hi, MAP_LUT[j % len(MAP_LUT)]), 88, 88,
                                             Image.NEAREST)))

    def _prep_ebsd(self):
        r = self.eb["raw"]
        ipf = np.asarray(r["ipf"])
        h, w = ipf.shape[:2]
        self.ebsd_wh = (IMG, IMG * h / w)
        self.ebsd_w_um, self.ebsd_h_um = w * float(r["step_um"]), h * float(r["step_um"])
        self.im_ipf = G.to_image(ipf, *self.ebsd_wh)
        gb = np.asarray(r["gb"])
        dark = ipf.copy()
        dark[gb] = (dark[gb] * 0.45).astype(np.uint8)
        self.im_ipf_gb = G.to_image(dark, *self.ebsd_wh)
        self.ebsd_um_per_unit = self.ebsd_w_um / IMG
        k = np.asarray(next(iter(r["kikuchi"].values())), float)
        ok = np.isfinite(k)
        lo, hi = float(np.nanmin(k)), float(np.nanmax(k))
        rgb = G.colourize(np.where(ok, k, lo), lo, hi, G.LUT_GRAY, 0.9)
        rgba = np.dstack([rgb, np.where(ok, 255, 0).astype(np.uint8)])
        self.im_kik = Image.fromarray(rgba).resize((max(2, int(round(72 * S))),) * 2, Image.LANCZOS)

    # ------------------------------------------------------------------------------------------ the render inset
    def _reader(self):
        if self._clip is None:
            from . import assets as A
            # slowed so that the shot lasts the segment without looping (the render is 6 frames a second)
            self._clip = G.Footage(A.src("alloy_characterize"), 27.5, 45.7, 222, 185, CROP_SEM,
                                   (45.7 - 27.5) / (self.DURATION + 0.5))
        return self._clip

    def close(self):
        if self._clip is not None:
            self._clip.close()
        self._clip = None

    # ------------------------------------------------------------------------------------------ what never changes
    def static_extra(self, cv: Canvas):
        cv.card(LEFT, "The experiment")
        cv.card(RIGHT, "Its data")
        cv.tag(RIGHT[2] - 18, RIGHT[1] + 10, "sim", "the twin's SEM, EDS and EBSD models of this alloy, full "
                                                    "fidelity", anchor="r")
        for key in ORDER:
            cx, cy = CELLS[key]
            cv.rect((cx, cy, cx + CELL_W, cy + CELL_H), fill=G.PLOT_FILL, outline=G.CARD_EDGE, width=2, radius=10)
            cv.text(cx + 46, cy + 11, NAME[key], 21, bold=True, fill=INK)
            cv.text(cx + CELL_W - 14, cy + 15, SAMPLE[key], 17, cond=True, fill=INK2, anchor="ra")
        # the note under the schematic
        cv.tag(322, 730, "illus", "schematic, not to scale", size=16)
        cv.para(324, 774, "Drawn as one scan. In the lab these are separate scans: the powder lot, then the polished "
                          "section, tilted 70° for EBSD.", 17, 304, fill=INK2, cond=True, lh=1.32)

    # ------------------------------------------------------------------------------------------ timing helpers
    def _focus(self, key: str, t: float) -> float:
        """How much detector ``key`` (and its panel) is the one being pointed at, 0..1."""
        w = St.window(t, self.FOCUS[key], self.FOCUS[key] + self.FOCUS_S, 0.35) if t < self.T_BEAM[1] + 0.3 else 0.0
        w = max(w, St.window(t, self.T_READ[key], self.T_READ[key] + 1.15, 0.3))
        w = max(w, St.window(t, self.NET[key], self.NET[key] + 1.35, 0.3))
        return w

    # ------------------------------------------------------------------------------------------ the schematic
    def _schematic(self, cv: Canvas, t: float, u: float, on: bool):
        steel, edge = (62, 68, 82), (128, 134, 148)
        foc = {k: self._focus(k, t) for k in ORDER}
        xf = (t * 2.3) % 1.0                                           # the fast axis: left to right, then back
        sx_ = XC - SCAN_HALF + 2 * SCAN_HALF * xf
        # the scanned field, from above
        fx, fy, fs = FIELD
        cv.rect((fx, fy, fx + fs, fy + fs), fill=(10, 12, 16), outline=G.CARD_EDGE, width=2)
        rows = fs * u
        if u > 0:
            cv.rect((fx + 1, fy + 1, fx + fs - 1, fy + max(1.0, rows)), fill=mix((10, 12, 16), G.HOT, 0.20))
            for k in range(0, int(rows), 7):
                cv.line([(fx + 2, fy + k + 1), (fx + fs - 2, fy + k + 1)], mix((10, 12, 16), G.HOT, 0.34), 1)
        if on:
            cv.line([(fx + 2, fy + rows), (fx + 2 + (fs - 4) * xf, fy + rows)], G.HOT, 2)
            cv.circle(fx + 2 + (fs - 4) * xf, fy + rows, 4.5, fill=G.HOT, outline=INK, width=1)
        cv.text(fx + fs / 2, fy + fs + 8, "the field, from above", 16, cond=True, fill=INK2, anchor="ma")
        cv.text(fx + fs / 2, fy + fs + 30, "beam off" if not on and u <= 0 else
                (f"scan {fmt(100 * u)} %" if on else "scan complete"), 17, bold=True, fill=INK, anchor="ma")
        # the column
        cv.rect((XC - 34, 198, XC + 34, 226), fill=(78, 84, 98), outline=edge, width=2, radius=6)
        cv.poly([(XC - 46, 226), (XC + 46, 226), (XC + 34, 396), (XC - 34, 396)], fill=steel, outline=edge, width=2)
        for y in (258, 326):
            for x0 in (XC - 40, XC + 12):
                cv.rect((x0, y, x0 + 28, y + 28), fill=(38, 42, 52), outline=(104, 110, 122), width=2)
                cv.line([(x0 + 4, y + 4), (x0 + 24, y + 24)], (104, 110, 122), 2)
                cv.line([(x0 + 24, y + 4), (x0 + 4, y + 24)], (104, 110, 122), 2)
        cv.poly([(XC - 34, 396), (XC + 34, 396), (XC + 16, 430), (XC - 16, 430)], fill=(92, 98, 112), outline=edge,
                width=2)
        cv.text(XC - 60, 276, "electron", 17, cond=True, fill=INK2, anchor="rm")
        cv.text(XC - 60, 298, "column", 17, cond=True, fill=INK2, anchor="rm")
        cv.text(XC - 56, 340, "lenses and", 16, cond=True, fill=INK3, anchor="rm")
        cv.text(XC - 56, 360, "scan coils", 16, cond=True, fill=INK3, anchor="rm")
        # the stage and the sample (and its pose for EBSD, dashed)
        cv.rect((XC - 92, 648, XC + 92, 670), fill=(46, 50, 60), outline=(104, 110, 122), width=2, radius=4)
        cv.rect((XC - 66, SURF_Y, XC + 66, 648), fill=(126, 138, 158), outline=(206, 212, 224), width=2)
        cv.text(XC, 678, "the sample, on its stage", 16, cond=True, fill=INK2, anchor="ma")
        ca, sa = math.cos(math.radians(-70)), math.sin(math.radians(-70))
        tilt = [(XC + x * ca - y * sa, 634 + x * sa + y * ca) for x, y in ((-66, -14), (66, -14), (66, 14), (-66, 14))]
        cv.dashed(tilt + [tilt[0]], INK3, 2, 7, 6, a=0.55 + 0.45 * foc["ebsd"])

        def chip(x, y, key, a=1.0):
            k = foc[key]
            cv.circle(x, y, 13, fill=mix((40, 44, 54), G.HOT, k), outline=mix(edge, INK, k), width=2, a=a)
            cv.text(x, y, NUM[key], 17, bold=True, fill=mix(INK, (20, 16, 8), k), anchor="mm", a=a)

        def label(x, y, key, words, sub=""):
            k = foc[key]
            chip(x + 13, y + 13, key)
            cv.text(x + 34, y + 13, words, 17, cond=True, fill=mix(INK2, INK, k), anchor="lm")
            if sub:
                cv.text(x + 34, y + 36, sub, 16, cond=True, fill=INK3, anchor="lm")

        def body(p0, p1, half, key):
            """A detector as a bar from p0 (back) to p1 (the end facing the sample)."""
            k = foc[key]
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            L = math.hypot(dx, dy)
            nx, ny = -dy / L * half, dx / L * half
            cv.poly([(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), (p1[0] - nx, p1[1] - ny),
                     (p0[0] - nx, p0[1] - ny)], fill=mix(steel, G.HOT, 0.22 * k), outline=mix(edge, G.HOT, k),
                    width=2 + (1 if k > 0.5 else 0))

        def dots(path, key, n=5, r=3.6):
            """The signal on its way: a faint path always, bright dots moving along it while in focus."""
            k = foc[key]
            cv.line(path, mix(G.CARD_FILL, INK2, 0.55), 1, a=1.0 if on else 0.5)
            if k <= 0.01 or not on:
                return
            p = np.asarray(path, float)
            seg = np.hypot(np.diff(p[:, 0]), np.diff(p[:, 1]))
            cum = np.concatenate([[0.0], np.cumsum(seg)])
            for j in range(n):
                s_ = ((t * 1.25 + j / n) % 1.0)
                d_ = s_ * cum[-1]
                x_ = float(np.interp(d_, cum, p[:, 0]))
                y_ = float(np.interp(d_, cum, p[:, 1]))
                cv.circle(x_, y_, r, fill=G.HOT, a=k * min(1.0, 4 * s_, 4 * (1 - s_)))

        spot = (sx_ if on else XC, SURF_Y)
        # 1: the secondary-electron detector at the side; slow electrons are drawn across to its cage
        p0, p1 = (92, 548), (172, 578)
        body(p0, p1, 15, "se")
        k = foc["se"]
        cv.circle(p1[0] + 12, p1[1] + 4, 17, fill=(30, 34, 42), outline=mix(edge, G.HOT, k), width=2)
        for dd in (-8, 0, 8):
            cv.line([(p1[0] + 12 + dd, p1[1] - 11), (p1[0] + 12 + dd, p1[1] + 19)], mix(edge, G.HOT, k), 1)
        for dd in (-7, 4):
            cv.line([(p1[0] - 3, p1[1] + 4 + dd), (p1[0] + 27, p1[1] + 4 + dd)], mix(edge, G.HOT, k), 1)
        label(62, 478, "se", "secondary electrons", "detector at the side")
        q = np.linspace(0, 1, 24)
        c0, c1, c2 = np.array(spot, float) + (0, -3), np.array((XC - 30, 556.0)), np.array((p1[0] + 28, p1[1] + 2.0))
        dots([tuple((1 - s_) ** 2 * c0 + 2 * s_ * (1 - s_) * c1 + s_ ** 2 * c2) for s_ in q], "se")
        # 2: the backscatter detector, a ring under the pole piece; fast electrons bounce straight back up
        k = foc["bse"]
        for x0, x1 in ((XC - 64, XC - 12), (XC + 12, XC + 64)):
            cv.rect((x0, 436, x1, 447), fill=mix(steel, G.HOT, 0.3 * k), outline=mix(edge, G.HOT, k), width=2,
                    radius=2)
        label(74, 426, "bse", "backscatter", "detector")
        dots([(spot[0], spot[1] - 3), (XC - 40, 449)], "bse", n=3)
        dots([(spot[0], spot[1] - 3), (XC + 40, 449)], "bse", n=3)
        # 3: the EDS detector, looking down at the spot; X-rays
        e0, e1 = (474, 452), (410, 498)
        body(e0, e1, 14, "eds")
        label(398, 406, "eds", "X-rays: EDS detector")
        ex, ey = e1[0] - spot[0], e1[1] - spot[1]
        L = math.hypot(ex, ey)
        wav = []
        for s_ in np.linspace(0, 1, 40):
            off = 5.0 * math.sin(s_ * 9 * math.pi - t * 9) * min(1.0, 6 * s_, 6 * (1 - s_))
            wav.append((spot[0] + ex * s_ - ey / L * off, spot[1] - 3 + (ey + 3) * s_ + ex / L * off))
        k = foc["eds"]
        cv.line(wav, mix(mix(G.CARD_FILL, INK2, 0.55), G.HOT, k if on else 0.0), 2 if k > 0.3 else 1,
                a=1.0 if on else 0.5)
        # 4: the EBSD camera, its phosphor screen facing the tilted sample
        k = foc["ebsd"]
        cv.rect((452, 556, 461, 652), fill=mix((70, 110, 80), G.HOT, 0.5 * k), outline=mix(edge, G.HOT, k), width=2)
        cv.rect((461, 574, 566, 634), fill=mix(steel, G.HOT, 0.22 * k), outline=mix(edge, G.HOT, k), width=2,
                radius=6)
        cv.text(513, 604, "camera", 16, cond=True, fill=INK2, anchor="mm")
        label(440, 660, "ebsd", "EBSD camera", "sample tilted 70°")
        for yy in (566, 604, 642):
            dots([(spot[0], spot[1] - 3), (451, yy)], "ebsd", n=3, r=3.0)
        # the beam
        if on:
            cv.line([(XC, 226), (XC, 430)], G.HOT, 2, a=0.85)
            cv.line([(XC, 430), (spot[0], spot[1])], G.HOT, 3)
            cv.circle(spot[0], spot[1], 11, fill=G.HOT + (70,))
            cv.circle(spot[0], spot[1], 4.5, fill=G.HOT, outline=INK, width=1)
            cv.line([(XC - SCAN_HALF, SURF_Y - 1), (XC + SCAN_HALF, SURF_Y - 1)], mix((126, 138, 158), G.HOT, 0.6), 2)

    # ------------------------------------------------------------------------------------------ the panels
    @staticmethod
    def _row(cv: Canvas, x, y, w, lab, val, a):
        cv.text(x, y, lab, 17, cond=True, fill=INK2, a=a)
        cv.text(x + w, y - 2, val, 19, bold=True, fill=INK, anchor="ra", a=a)

    def _badge(self, cv: Canvas, key: str, title, body_, a, used: bool, box=None):
        """Which node of the network takes this signal's numbers (tinted and edged in the campaign's colour), or
        that none does (plain)."""
        if a <= 0.004:
            return
        cx, cy = CELLS[key]
        b = box or BADGE
        box = (cx + b[0], cy + b[1], cx + b[2], cy + b[3])
        col = self.col
        cv.rect(box, fill=mix(G.PLOT_FILL, col, 0.30) if used else (32, 35, 42), outline=col if used else G.CARD_EDGE,
                width=3 if used else 2, radius=10, a=a)
        size = 18
        while size > 16 and cv.text_w(title, size, bold=True, cond=True) > box[2] - box[0] - 22:
            size -= 1
        cv.text(box[0] + 12, box[1] + 6, title, size, bold=True, cond=True, fill=INK, a=a)
        cv.para(box[0] + 12, box[1] + 29, body_, 16, box[2] - box[0] - 22, fill=INK if used else INK2, cond=True,
                a=a, lh=1.2, max_lines=3)

    def _head(self, cv: Canvas, key: str, t: float):
        cx, cy = CELLS[key]
        k = self._focus(key, t)
        cv.circle(cx + 24, cy + 23, 13, fill=mix((40, 44, 54), G.HOT, k), outline=mix((128, 134, 148), INK, k),
                  width=2)
        cv.text(cx + 24, cy + 23, NUM[key], 17, bold=True, fill=mix(INK, (20, 16, 8), k), anchor="mm")
        if k > 0.01:
            cv.rect((cx + 1, cy + 1, cx + CELL_W - 1, cy + CELL_H - 1), outline=G.HOT, width=2, radius=10, a=0.9 * k)

    def _describe(self, cv: Canvas, key: str, t: float, words: str):
        cx, cy = CELLS[key]
        a = ramp(t, self.FOCUS[key] + 0.2, self.FOCUS[key] + 0.9)
        cv.para(cx + TXT_X, cy + 46, words, 17, TXT_W, fill=INK, cond=True, a=a, lh=1.24, max_lines=3)

    def _se(self, cv: Canvas, t: float, u: float):
        cx, cy = CELLS["se"]
        f = self.f["powder"]
        x, y = cx + 14, cy + 46
        G.raster(cv, self.im_se, x, y, u)
        if u > 0.97:
            G.scale_bar(cv, x + IMG - 8, y + IMG - 8, self.se_um_per_unit)
        self._describe(cv, "se", t, "Topography. Edges and steep faces are bright.")
        a = ramp(t, self.T_READ["se"], self.T_READ["se"] + 0.6)
        for rx, ry, rr in self.se_rings:
            cv.circle(x + rx, y + ry, rr, outline=G.HOT, width=3, a=a)
        tx, ty = cx + TXT_X, cy + ROW0
        self._row(cv, tx, ty, TXT_W, "particles measured", fmt(f["particles"]), a)
        self._row(cv, tx, ty + ROW_DY, TXT_W, "sphericity", fmt(f["sphericity"], 2), a)
        self._row(cv, tx, ty + 2 * ROW_DY, TXT_W, "with satellites", f"{fmt(f['satellite_pct'], 1)} %", a)
        cv.para(tx, cy + NOTE_Y - 22, "ringed: the particles that carry satellites", 16, TXT_W, fill=INK2, cond=True,
                a=a, lh=1.22)
        self._badge(cv, "se", "→ print node: input", "the satellite share, with the lot's oxygen",
                    ramp(t, self.NET["se"], self.NET["se"] + 0.6), True)

    def _bse(self, cv: Canvas, t: float, u: float):
        cx, cy = CELLS["bse"]
        s, b = self.f["section"], self.f["best"]
        x, y = cx + 14, cy + 46
        G.raster(cv, self.im_bse, x, y, u)
        if u > 0.14:
            cv.rect((x, y, x + 150, y + 26), fill=(10, 12, 16, 225))
            cv.text(x + 8, y + 13, "↑ build direction", 16, bold=True, cond=True, fill=INK, anchor="lm")
        if u > 0.97:
            G.scale_bar(cv, x + IMG - 8, y + IMG - 8, self.bse_um_per_unit)
        self._describe(cv, "bse", t, "Composition contrast. Metal is bright; pores and cracks are dark.")
        a = ramp(t, self.T_READ["bse"], self.T_READ["bse"] + 0.6)
        for rx, ry, rr in self.bse_pores:
            if ry > 30 or rx > 154:                         # clear of the build-direction label
                cv.circle(x + rx, y + ry, rr, outline=INK, width=2, a=a * 0.9)
        if a > 0.004:
            cv.paste(self.ov_cracks, x, y, a=a)
        tx, ty = cx + TXT_X, cy + ROW0
        self._row(cv, tx, ty, TXT_W, "porosity", f"{fmt(s['porosity_pct'], 2)} %", a)
        self._row(cv, tx, ty + ROW_DY, TXT_W, "pores found (ringed)", fmt(s["pores"]), a)
        self._row(cv, tx, ty + 2 * ROW_DY, TXT_W, "largest pore", f"{fmt(s['pore_dmax_um'])} µm", a)
        self._row(cv, tx, ty + 3 * ROW_DY, TXT_W, "cracks found (marked)", fmt(s["cracks"]), a)
        a2 = ramp(t, self.T_READ["bse"] + 0.5, self.T_READ["bse"] + 1.1)
        cv.para(tx, cy + NOTE_Y, f"cracks: {fmt(s['crack_density'], 3)} mm/mm² here; the part's true value is "
                                 f"{fmt(b['true_crack'], 3)}", 16, TXT_W, fill=INK2, cond=True, a=a2, lh=1.2,
                max_lines=2)
        self._badge(cv, "bse", "→ print node: outputs",
                    "porosity and crack density, with the Archimedes density; the lower density is reported",
                    ramp(t, self.NET["bse"], self.NET["bse"] + 0.6), True)

    def _eds_axes(self) -> Axes:
        cx, cy = CELLS["eds"]
        return Axes((cx + 56, cy + 64, cx + 306, cy + 162), (0.0, 7.0), self.eds_ylim, logy=True,
                    xticks=[0, 1, 2, 3, 4, 5, 6, 7], yticks=[], xfmt="{:g}")

    def _eds_labels(self, cv: Canvas, ax: Axes) -> list:
        """Where each named peak's label goes: above its peak in the final spectrum, or beside it where that would
        leave the plot or sit on another label. [(x, y, element)], top-left corners."""
        if getattr(self, "_peak_xy", None) is None:
            x0, y0, x1, y1 = ax.box
            placed, out = [], []
            for kev, el in self.eds_peaks:
                near = (self.eds_E > kev - 0.06) & (self.eds_E < kev + 0.06)
                Xp = float(ax.X(kev))
                Yt = float(ax.Y(max(float(self.eds_N[near].max()), 1.0)))
                w, h = cv.text_w(el, 16, bold=True, cond=True), 18.0
                cands = [(Xp - w / 2, Yt - 5 - h), (Xp + 5, Yt - 3 - h), (Xp - w - 5, Yt - 3 - h),
                         (Xp - w / 2, Yt - 5 - 2 * h), (Xp + 6, Yt + 1), (Xp + 6, Yt + 1 + h)]
                box = None
                for bx, by in cands:
                    bb = (bx, by, bx + w, by + h)
                    if by < y0 + 1 or bx < x0 + 1 or bx + w > x1 - 1:
                        continue
                    if any(bb[0] < p[2] + 2 and bb[2] > p[0] - 2 and bb[1] < p[3] and bb[3] > p[1] for p in placed):
                        continue
                    box = bb
                    break
                if box is None:
                    bx, by = cands[-1]
                    box = (bx, by, bx + w, by + h)
                placed.append(box)
                out.append((box[0], box[1], el))
            self._peak_xy = out
        return self._peak_xy

    def _eds(self, cv: Canvas, t: float, u: float):
        cx, cy = CELLS["eds"]
        ax = self._eds_axes()
        ax.draw(cv, 1.0, grid=False, size=16, fill=(10, 12, 16))
        x0, y0, x1, y1 = ax.box
        dec = 1
        while 10 ** dec <= self.eds_ylim[1]:
            if dec % 2 == 1:
                Y = float(ax.Y(10.0 ** dec))
                cv.line([(x0, Y), (x1, Y)], St.GRID, 1)
                cv.text(x0 - 8, Y, "10" + {1: "", 3: "³", 5: "⁵", 7: "⁷"}.get(dec, f"^{dec}"), 16, fill=INK2,
                        anchor="rm")
            dec += 1
        cv.text(cx + 14, cy + 42, "counts per channel (log); energy, keV", 16, cond=True, fill=INK2)
        live = float(self.ed["raw"]["live_s"])
        cv.text(cx + 206, cy + 15, f"{fmt(live * u)} s of {fmt(live)} s counted", 17, cond=True, fill=INK2,
                a=1.0 if u > 0 else 0.0)
        if u > 0:
            N, z = self.eds_N, self.eds_z
            c = np.maximum(N * u + np.sqrt(np.maximum(N * u * (1 - u), 0.0)) * z, self.eds_ylim[0])
            pts = ax.pts(self.eds_E, c)
            pts[:, 1] = np.clip(pts[:, 1], y0, y1)
            cv.poly([(float(pts[0, 0]), y1)] + [tuple(p) for p in pts] + [(float(pts[-1, 0]), y1)],
                    fill=mix((10, 12, 16), self.col, 0.42))
            cv.aaline(G._thin(pts, 0.5), mix(self.col, INK, 0.25), 2.0)
            ap = ramp(u, 0.30, 0.42)                         # the peaks are named once they stand out
            for bx, by, el in self._eds_labels(cv, ax):
                cv.text(bx, by, el, 16, bold=True, cond=True, fill=INK, a=ap, stroke=2)
        # the maps (illustrative)
        my = cy + 216
        cv.text(cx + 14, cy + 194, "element maps", 16, cond=True, fill=INK2)
        for j, (el, im) in enumerate(self.maps):
            mx = cx + 14 + j * 104
            G.raster(cv, im, mx, my, u)
            cv.rect((mx - 1, my - 1, mx + 89, my + 89), outline=G.CARD_EDGE, width=2)
            cv.rect((mx, my, mx + 30, my + 22), fill=(10, 12, 16, 225))
            cv.text(mx + 15, my + 11, el, 16, bold=True, cond=True, fill=INK, anchor="mm")
        lead = cv.text_w("illustrative", 16, bold=True, cond=True) + 38
        words = next((w_ for w_ in MAP_WORDS if lead + cv.text_w(": " + w_, 16, cond=True) <= CELL_W - 24),
                     MAP_WORDS[-1])
        cv.tag(cx + 12, cy + 314, "illus", words, size=16)
        self._describe(cv, "eds", t, "Each element emits X-rays at its own energies.")
        # designed against measured
        a = ramp(t, self.T_READ["eds"], self.T_READ["eds"] + 0.6)
        tx, ty = cx + TXT_X, cy + 98
        cv.text(tx, ty, "wt%", 16, cond=True, fill=INK2, a=a)
        cv.text(tx + 150, ty, "designed", 16, cond=True, fill=INK2, anchor="ra", a=a)
        cv.text(tx + TXT_W, ty, "EDS", 16, cond=True, fill=INK2, anchor="ra", a=a)
        for i, (el, des, got) in enumerate(self.eds_rows):
            yy = ty + 22 + i * 22
            cv.text(tx, yy, el, 18, bold=True, fill=INK, a=a)
            cv.text(tx + 150, yy, fmt(des, 2), 18, fill=INK2, anchor="ra", a=a)
            cv.text(tx + TXT_W, yy, fmt(got, 2), 18, bold=True, fill=INK, anchor="ra", a=a)
        yy = ty + 22 + len(self.eds_rows) * 22 + 6
        words = ""
        if self.eds_below:
            words = ", ".join(self.eds_below) + ": under the detection limit. "
        if self.eds_invisible:
            words += ", ".join(self.eds_invisible) + ": invisible to EDS."
        cv.para(tx, yy, words.strip(), 16, TXT_W, fill=INK2, cond=True, a=a, lh=1.2, max_lines=3)
        self._badge(cv, "eds", "not a network input", "a composition check per lot",
                    ramp(t, self.NET["eds"], self.NET["eds"] + 0.6), False, box=(316, 250, CELL_W - 8, 306))

    def _ebsd(self, cv: Canvas, t: float, u: float):
        cx, cy = CELLS["ebsd"]
        f = self.f["ebsd"]
        x, y = cx + 14, cy + 46
        w, h = self.ebsd_wh
        a = ramp(t, self.T_READ["ebsd"], self.T_READ["ebsd"] + 0.6)
        G.raster(cv, self.im_ipf, x, y, u)
        if a > 0.004:
            cv.paste(self.im_ipf_gb, x, y, a=a)
        if u > 0.16:
            cv.rect((x, y, x + 150, y + 26), fill=(10, 12, 16, 225))
            cv.text(x + 8, y + 13, "↑ build direction", 16, bold=True, cond=True, fill=INK, anchor="lm")
        if u > 0.97:
            G.scale_bar(cv, x + w - 8, y + h - 8, self.ebsd_um_per_unit)
        # one diffraction pattern, and what the colours mean
        ky = cy + 274
        ak = ramp(t, self.FOCUS["ebsd"] + 0.2, self.FOCUS["ebsd"] + 0.9)
        if ak > 0.004:
            cv.circle(x + 36, ky + 36, 37, fill=(8, 9, 12), outline=G.CARD_EDGE, width=2, a=ak)
            cv.paste(self.im_kik, x, ky, a=ak)
            cv.text(x + 86, ky + 2, "left: one point's pattern", 16, cond=True, fill=INK2, a=ak)
            cv.text(x + 86, ky + 24, "colour: direction along build", 16, cond=True, fill=INK2, a=ak)
            for j, (rgb, nm) in enumerate((((255, 40, 40), "<001>"), ((40, 220, 40), "<101>"),
                                           ((60, 90, 255), "<111>"))):
                sx_ = x + 86 + j * 68
                cv.rect((sx_, ky + 51, sx_ + 15, ky + 66), fill=rgb, outline=INK, width=1, a=ak)
                cv.text(sx_ + 20, ky + 59, nm, 16, cond=True, fill=INK, anchor="lm", a=ak)
        self._describe(cv, "ebsd", t, "The pattern at each point gives the crystal's orientation.")
        tx, ty = cx + TXT_X, cy + ROW0
        self._row(cv, tx, ty, TXT_W, "grain size", f"{fmt(f['grain_um'], 1)} µm", a)
        self._row(cv, tx, ty + ROW_DY, TXT_W, "equiaxed share", f"{fmt(f['equiaxed_pct'])} %", a)
        self._row(cv, tx, ty + 2 * ROW_DY, TXT_W, "texture, × random", fmt(f["texture_mrd"], 1), a)
        self._row(cv, tx, ty + 3 * ROW_DY, TXT_W, "points indexed", f"{fmt(f['indexed_pct'])} %", a)
        cv.para(tx, cy + NOTE_Y, f"texture: <100> along the build; map step {fmt(f['step_um'], 2)} µm", 16,
                TXT_W, fill=INK2, cond=True, a=a, lh=1.2, max_lines=2)
        self._badge(cv, "ebsd", "→ section node: outputs",
                    "grain size and equiaxed share; they feed the PIP and tensile nodes",
                    ramp(t, self.NET["ebsd"], self.NET["ebsd"] + 0.6), True)

    # ------------------------------------------------------------------------------------------ the frame
    def draw(self, cv: Canvas, t: float):
        u = lin(t, *self.T_BEAM)
        on = self.T_BEAM[0] <= t < self.T_BEAM[1]
        self._schematic(cv, t, u, on)
        # the lab's own SEM, as its 3-D model has it
        fr = self._reader().frame(t)
        cv.paste(fr, 78, 728)
        G.framed(cv, (78, 728, 300, 913), "the lab's desktop SEM")
        cv.tag(84, 878, "render", "PR 318", size=16)
        for key in ORDER:
            self._head(cv, key, t)
        self._se(cv, t, u)
        self._bse(cv, t, u)
        self._eds(cv, t, u)
        self._ebsd(cv, t, u)
        # at the end the strip moves on: the section is done, PIP is next (the last caption's second half)
        k = ramp(t, self.T_NEXT, self.T_NEXT + 0.6)
        if k > 0.004:
            cv.paste(G.network_strip(self.campaign, ("pip",), G.STRIP_W, tuple(self.done) + tuple(self.nodes)),
                     St.W / S - G.MARGIN - G.STRIP_W, 36, a=k)


if __name__ == "__main__":
    import sys
    import time
    from pathlib import Path
    Path("/tmp/vid").mkdir(parents=True, exist_ok=True)
    seg = SEM()
    for tt in [float(v) for v in sys.argv[1:]] or [1.0, 4.0, 8.0, 12.0, 16.0, 19.5, 23.0, 27.0, 30.0, 35.5]:
        t0 = time.time()
        fr = seg.frame(tt)
        Image.fromarray(fr).save(f"/tmp/vid/exp_sem_{tt:05.1f}.png")
        print(f"wrote /tmp/vid/exp_sem_{tt:05.1f}.png  ({time.time() - t0:.2f} s)")
    seg.close()
