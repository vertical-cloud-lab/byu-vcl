"""The data the powder chapter shows (#303, round 8): what is measured, what is computed and what is illustrative.

    python3 r8_powder_data.py        # -> out/alloy_powder_{sem,psd,xrd,xrf}.png, out/alloy_powder_data.json,
                                     #    out/alloy_powder_sem_detect.png (the particles the count found)

* **SEM (measured, real data).** The lab's own atomized Al 4047, run c3k0n5 (rePowder, 22 Oct 2026, DAL #159), imaged on
  BYU's Apreo at 5 kV (ETD) by Ronnie Guymon on 26 Oct 2026 (DAL #157): ``out/footage/sem_c3k0n5_{1,2,3}.png``.
* **Particle count (measured from those images).** Each 137x frame (HFW 3.03 mm over 1536 px, 1.97 um per pixel) is
  thresholded (Otsu), the grey particle interiors are filled (not the dark gaps between touching particles), and every
  particle is taken as the largest circle inscribed in it (the peaks of the distance transform, largest first, a
  peak inside an accepted circle dropped). Only the evenly lit middle of each frame is counted (an ellipse 600 x 560
  px about the centre), and nothing under 12 um (6 px). That is a number-weighted, projected-diameter distribution of
  the powder *as imaged*, which is not yet the sieved cut (the frames show particles up to about 0.27 mm).
* **Laser diffraction (computed, not measured).** No Mastersizer result for this powder exists. The curve labelled as
  the Mastersizer's is the SEM count converted to volume (d^3) and passed through a 20-63 um sieve with soft edges
  (a log-normal cut of width 0.08 in ln d), which is what a laser-diffraction result of the cut would look like if the
  count were the whole powder. Laser diffraction reports volume-weighted equivalent-sphere diameters.
* **XRD (computed, not measured).** Al 4047 is about Al-12Si. Peak positions from the lattice parameters and Cu
  K-alpha (Bragg's law), intensities from the structure factors (International Tables form factors), multiplicity,
  Lorentz-polarization and a Debye-Waller factor, with the two phases weighted by mass fraction / density / cell
  volume squared; pseudo-Voigt peaks with K-alpha2.
* **XRF (illustrative).** Real line energies; the heights and the "result" column are made up for the picture.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FOOT = OUT / "footage"
SEM_FILES = [FOOT / f"sem_c3k0n5_{i}.png" for i in (1, 2, 3)]
UM_PX = 3030.0 / 1536.0               # 137x: HFW 3.03 mm across the 1536 px frame (the data bar's HFW)
D_MIN = 12.0                           # um: smaller than 6 px is not counted
SIEVE = (20.0, 63.0)                   # the cut, um

# colours (the dataviz reference palette, light mode)
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"
SURFACE = "#fcfcfb"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"     # blue, orange, aqua

SEM_CREDIT = ("c3k0n5: the lab's own Al 4047, ultrasonically atomized on the rePowder, 22 Oct 2026 (DAL #159). "
              "SEM: BYU's Apreo, 5 kV, ETD, 137x and 1000x, Ronnie Guymon, 26 Oct 2026 (DAL #157).")


# ================================================================================================= the particle count
def _count(path: Path, show: Path | None = None) -> np.ndarray:
    import cv2
    from scipy import ndimage as ndi
    g = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)[:1012]          # above the data bar
    b = cv2.GaussianBlur(g, (3, 3), 0)
    _, bw = cv2.threshold(b, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    bw = bw > 0
    holes = ndi.binary_fill_holes(bw) & ~bw
    lab, n = ndi.label(holes)
    if n:                                   # fill the grey particle interiors, not the dark gaps between particles
        mean = ndi.mean(b, lab, index=np.arange(1, n + 1))
        bw = bw | np.isin(lab, np.flatnonzero(np.asarray(mean) > 30) + 1)
    bw = ndi.binary_opening(bw, iterations=1)
    dist = cv2.distanceTransform(bw.astype(np.uint8), cv2.DIST_L2, 5)
    peak = (dist == ndi.maximum_filter(dist, size=5)) & (dist >= D_MIN / UM_PX / 2)
    cand = np.argwhere(peak)
    vals = dist[cand[:, 0], cand[:, 1]]
    acc = []
    for i in np.argsort(-vals):
        y, x = cand[i]
        r = float(vals[i])
        if any((ay - y) ** 2 + (ax - x) ** 2 < (0.85 * ar) ** 2 for ay, ax, ar in acc):
            continue
        k = max(1, int(0.5 * r))
        if b[max(0, y - k):y + k + 1, max(0, x - k):x + k + 1].mean() < 38:    # a dark gap, not a particle
            continue
        acc.append((int(y), int(x), r))
    H, W = bw.shape
    keep = [(y, x, r) for y, x, r in acc
            if ((x - W / 2) / 600) ** 2 + ((y - H / 2) / 560) ** 2 < 1 and y - r > 2 and y + r < H - 2]
    if show is not None:
        c = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
        cv2.ellipse(c, (W // 2, H // 2), (600, 560), 0, 0, 360, (214, 120, 42), 3)
        for y, x, r in keep:
            cv2.circle(c, (x, y), int(round(r)), (52, 104, 235), 2)
        cv2.imwrite(str(show), cv2.resize(c, (768, 506), interpolation=cv2.INTER_AREA))
    return np.array([2 * r * UM_PX for _, _, r in keep])


def sem_count() -> dict:
    """The c3k0n5 particle count from the two 137x frames, cached in out/alloy_powder_data.json."""
    cache = OUT / "alloy_powder_data.json"
    if cache.exists():
        d = json.loads(cache.read_text())
        if "sem_count" in d:
            return d["sem_count"]
    ds = [_count(SEM_FILES[0], OUT / "alloy_powder_sem_detect.png"), _count(SEM_FILES[1])]
    d = np.sort(np.concatenate(ds))
    v = d ** 3
    cv = np.cumsum(v) / v.sum()
    cn = np.arange(1, len(d) + 1) / len(d)
    inside = (d >= SIEVE[0]) & (d <= SIEVE[1])
    out = dict(images=[p.name for p in SEM_FILES[:2]], um_per_px=UM_PX, d_min_um=D_MIN, n=int(len(d)),
               per_image=[int(len(x)) for x in ds],
               Dn10=float(np.interp(0.1, cn, d)), Dn50=float(np.interp(0.5, cn, d)), Dn90=float(np.interp(0.9, cn, d)),
               Dv10=float(np.interp(0.1, cv, d)), Dv50=float(np.interp(0.5, cv, d)), Dv90=float(np.interp(0.9, cv, d)),
               number_frac_cut=float(inside.mean()), volume_frac_cut=float(v[inside].sum() / v.sum()),
               d_um=[round(float(x), 2) for x in d])
    return out


def _phi(z):
    from scipy.special import ndtr
    return ndtr(z)


def psd_curves(cnt: dict):
    """Log-spaced bins: the number % per bin, the volume % per bin (both from the count), and the computed laser-
    diffraction result of the 20-63 um cut (volume % per bin), smoothed in ln d."""
    d = np.asarray(cnt["d_um"])
    edges = np.geomspace(8, 400, 46)
    mids = np.sqrt(edges[1:] * edges[:-1])
    num = np.histogram(d, edges)[0].astype(float)
    vol = np.histogram(d, edges, weights=d ** 3)[0]
    # the cut: the volume distribution through a 20-63 um sieve with soft edges, smoothed (kernel 0.12 in ln d)
    lx = np.log(mids)
    t = _phi((np.log(d) - math.log(SIEVE[0])) / 0.08) * (1 - _phi((np.log(d) - math.log(SIEVE[1])) / 0.08))
    w = d ** 3 * t
    k = np.exp(-0.5 * ((lx[:, None] - np.log(d)[None, :]) / 0.12) ** 2)
    cut = (k * w[None, :]).sum(1)
    # its Dv10/50/90 from a fine grid
    fine = np.geomspace(8, 400, 2000)
    kf = np.exp(-0.5 * ((np.log(fine)[:, None] - np.log(d)[None, :]) / 0.12) ** 2)
    cf = np.cumsum((kf * w[None, :]).sum(1))
    cf /= cf[-1]
    dv = {q: float(np.interp(q, cf, fine)) for q in (0.1, 0.5, 0.9)}
    return mids, edges, 100 * num / num.sum(), 100 * vol / vol.sum(), 100 * cut / cut.sum(), dv


# ================================================================================================= XRD, computed
WL = (1.5405929, 1.5444274)            # Cu K-alpha1, K-alpha2 (A); K-alpha2 at half the intensity
A_AL, A_SI = 4.0495, 5.4311            # A, room temperature: Al (fcc), Si (diamond; NIST SRM 640e)
CM = {  # International Tables Vol. C, Table 6.1.1.4: a1 b1 a2 b2 a3 b3 a4 b4 c
    "Al": (6.4202, 3.0387, 1.9002, 0.7426, 1.5936, 31.5472, 1.9646, 85.0886, 1.1151),
    "Si": (6.2915, 2.4386, 3.0353, 32.3337, 1.9891, 0.6785, 1.5410, 81.6937, 1.1407),
}
B_ISO = {"Al": 0.85, "Si": 0.46}       # A^2, room temperature (approximate)
PHASES = {"Al": dict(a=A_AL, rho=2.70, w=0.88), "Si": dict(a=A_SI, rho=2.33, w=0.12)}   # Al-12Si, all Si as Si


def _f(el, s):
    a = CM[el]
    return sum(a[2 * i] * math.exp(-a[2 * i + 1] * s * s) for i in range(4)) + a[8]


def _families(maxh=6):
    fam = {}
    for h in range(maxh + 1):
        for k in range(h + 1):
            for l in range(k + 1):
                if h == k == l == 0:
                    continue
                n = h * h + k * k + l * l
                # multiplicity of {hkl} in m-3m
                perms = set()
                import itertools
                for p in itertools.permutations((h, k, l)):
                    for sg in itertools.product((1, -1), repeat=3):
                        perms.add(tuple(a * b for a, b in zip(p, sg)))
                fam.setdefault(n, []).append(((h, k, l), len(perms)))
    return fam


def xrd_peaks(tt_max=90.0) -> list[dict]:
    """[{phase, hkl, two_theta, d, I}] for Cu K-alpha1, I relative to the strongest = 100."""
    out = []
    for ph, p in PHASES.items():
        a = p["a"]
        V = a ** 3
        for n, lst in sorted(_families().items()):
            for (h, k, l), m in lst:
                par = {x % 2 for x in (h, k, l)}
                if len(par) > 1:                                   # fcc: unmixed only
                    continue
                if ph == "Si" and par == {0} and (h + k + l) % 4 != 0:     # diamond: h+k+l = 4n when all even
                    continue
                d = a / math.sqrt(n)
                x = WL[0] / (2 * d)
                if x >= 1:
                    continue
                th = math.asin(x)
                tt = math.degrees(2 * th)
                if tt > tt_max or tt < 5:
                    continue
                s = x / WL[0]                                       # sin(theta) / lambda
                f = _f(ph, s)
                F2 = 16 * f * f if ph == "Al" else (64 * f * f if par == {0} else 32 * f * f)
                lp = (1 + math.cos(2 * th) ** 2) / (math.sin(th) ** 2 * math.cos(th))
                dw = math.exp(-2 * B_ISO[ph] * s * s)
                I = p["w"] / p["rho"] / V ** 2 * F2 * m * lp * dw
                out.append(dict(phase=ph, hkl=f"{h}{k}{l}", two_theta=round(tt, 3), d=round(d, 4), I=I))
    top = max(o["I"] for o in out)
    for o in out:
        o["I"] = round(100 * o["I"] / top, 2)
    return sorted(out, key=lambda o: o["two_theta"])


def xrd_pattern(peaks, lo=10.0, hi=90.0, n=4000):
    x = np.linspace(lo, hi, n)
    y = 0.6 + 2.0 * np.exp(-(x - lo) / 6.0)                     # air scatter at low angle; the Si plate adds nothing
    for p in peaks:
        for wl, k in zip(WL, (1.0, 0.5)):
            th = math.asin(min(0.999, wl / (2 * p["d"])))
            c = math.degrees(2 * th)
            fw = 0.075 + 0.05 * math.tan(th)                        # FWHM, deg (a benchtop, estimate)
            g = np.exp(-4 * math.log(2) * ((x - c) / fw) ** 2)
            lo_ = 1.0 / (1 + 4 * ((x - c) / fw) ** 2)
            y = y + k * p["I"] * (0.5 * g + 0.5 * lo_)
    return x, 100 * y / y.max()


def height_shift(s_mm=0.1, R=150.0, two_theta=38.47) -> float:
    """Peak shift (deg 2theta) for a sample surface s mm above the goniometer axis: -2 s cos(theta) / R."""
    th = math.radians(two_theta / 2)
    return -math.degrees(2 * s_mm * math.cos(th) / R)


def thick_enough(two_theta=90.0, packing=0.6) -> float:
    """The depth (mm) that gives 99 % of the intensity an infinitely thick Al-12Si powder would, at two_theta:
    t = 2.3 sin(theta) / mu, with mu = (mu/rho) * rho_packed. Mass attenuation for Cu K-alpha: Al 50.3, Si 60.6
    cm^2/g (NIST XCOM, 8.05 keV)."""
    mu_rho = 0.88 * 50.3 + 0.12 * 60.6
    mu = mu_rho * 2.66 * packing                       # 1/cm
    return 10 * 2.3 * math.sin(math.radians(two_theta / 2)) / mu


# ================================================================================================= XRF, illustrative
XRF_LINES = [(1.254, 0.02, "Mg Ka"), (1.487, 1.00, "Al Ka"), (1.740, 0.62, "Si Ka"), (2.838, 0.10, "Pd La"),
             (3.072, 0.04, ""), (5.899, 0.015, "Mn Ka"), (6.404, 0.11, "Fe Ka"), (7.058, 0.017, ""),
             (8.048, 0.03, "Cu Ka"), (8.639, 0.02, "Zn Ka")]
AL4047 = [("Si", "11.0-13.0", "12.1"), ("Fe", "0.8 max", "0.21"), ("Cu", "0.30 max", "0.03"),
          ("Mn", "0.15 max", "0.02"), ("Mg", "0.10 max", "<0.05"), ("Zn", "0.20 max", "0.02"),
          ("Al", "balance", "87.6")]


# ================================================================================================= the panels
def _mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "axes.edgecolor": "#c9c8c2",
                         "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.8,
                         "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE})
    return plt


def _badge(fig, text, color):
    fig.text(0.985, 0.955, text, ha="right", va="center", fontsize=9, fontweight="bold", color="white",
             bbox=dict(boxstyle="round,pad=0.3", fc=color, ec="none"))


def panel_psd(cnt: dict, path: Path):
    plt = _mpl()
    mids, edges, num, vol, cut, dv = psd_curves(cnt)
    fig, ax = plt.subplots(figsize=(6.0, 3.7), dpi=110)
    ax.axvspan(*SIEVE, color="#e8f3ee", lw=0, zorder=0)
    ax.text(math.sqrt(SIEVE[0] * SIEVE[1]), 0.50, "the cut,\n20-63 µm", transform=ax.get_xaxis_transform(),
            ha="center", va="center", fontsize=8.6, color="#1d7a55")
    ax.step(mids, num, where="mid", color=C1, lw=2, label=f"SEM count, by number (measured, n = {cnt['n']})")
    ax.step(mids, vol, where="mid", color=C2, lw=2, label="the same count, by volume (computed)")
    ax.fill_between(mids, cut, color=C3, alpha=0.25, lw=0)
    ax.plot(mids, cut, color=C3, lw=2, label="laser diffraction of the cut (computed, not measured)")
    ax.set_xscale("log")
    ax.set_xlim(8, 400)
    ax.set_xticks([10, 20, 45, 63, 100, 200, 400])
    ax.set_xticklabels(["10", "20", "45", "63", "100", "200", "400"])
    ax.set_xlabel("particle size (µm)")
    ax.set_ylabel("% per size class")
    ax.set_ylim(0, max(cut.max(), num.max(), vol.max()) * 1.32)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(loc="upper right", fontsize=8.6, frameon=False, labelcolor=INK)
    fig.text(0.015, 0.955, "Particle size, c3k0n5 Al 4047", ha="left", va="center", fontsize=12, color=INK,
             fontweight="bold")
    fig.text(0.015, 0.035, f"The cut, computed: Dv10 {dv[0.1]:.0f}, Dv50 {dv[0.5]:.0f}, Dv90 {dv[0.9]:.0f} µm. The powder as "
             f"imaged: Dv50 {cnt['Dv50']:.0f} µm,\n{100 * cnt['volume_frac_cut']:.0f} % of its volume in the cut. "
             "Laser diffraction reports volume; the SEM count, number.", fontsize=8.4, color=INK2)
    _badge(fig, "SEM COUNT MEASURED, LD COMPUTED", "#1d7a55")
    fig.subplots_adjust(left=0.10, right=0.98, top=0.88, bottom=0.27)
    fig.savefig(path)
    plt.close(fig)
    return dv


def panel_xrd(peaks, path: Path):
    plt = _mpl()
    x, y = xrd_pattern(peaks)
    fig, ax = plt.subplots(figsize=(6.0, 3.7), dpi=110)
    ax.plot(x, y, color=C1, lw=1.4)
    ax.set_xlim(10, 90)
    ax.set_ylim(0, 118)
    ax.set_xlabel("2θ (degrees), Cu Kα")
    ax.set_ylabel("intensity (relative)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    shown = [p for p in peaks if p["I"] > 1.2]
    for p in shown:
        c = C1 if p["phase"] == "Al" else C2
        ax.annotate(f"{p['phase']} {p['hkl']}", (p["two_theta"], min(p["I"], 100) + 2), ha="center", va="bottom",
                    fontsize=8.2, color=INK if p["phase"] == "Al" else "#a8431c", rotation=90 if p["I"] < 60 else 0)
        ax.plot([p["two_theta"]] * 2, [-2, 1.5], color=c, lw=2, clip_on=False)
    fig.text(0.015, 0.955, "Powder XRD, Al-12Si (Al 4047)", ha="left", va="center", fontsize=12, color=INK,
             fontweight="bold")
    sh = height_shift()
    fig.text(0.015, 0.035, f"Al (fcc) a = {A_AL} Å, Si (diamond) a = {A_SI} Å, Cu Kα1 {WL[0]:.4f} Å: Bragg's law, "
             f"structure factors,\nLorentz-polarization. A surface 0.1 mm too high shifts Al 111 by {sh:.2f}° (R = 150 mm).",
             fontsize=8.4, color=INK2)
    _badge(fig, "COMPUTED, NOT MEASURED", "#8a5a00")
    fig.subplots_adjust(left=0.10, right=0.98, top=0.88, bottom=0.27)
    fig.savefig(path)
    plt.close(fig)


def panel_xrf(path: Path):
    plt = _mpl()
    x = np.linspace(0.6, 10.0, 1600)
    y = 0.012 + 0.03 * np.exp(-((x - 7.5) / 3.5) ** 2) * (x > 2.0)          # the scattered tube continuum
    for mu, h, _ in XRF_LINES:
        y = y + h * np.exp(-0.5 * ((x - mu) / (0.040 + 0.011 * mu)) ** 2)
    fig = plt.figure(figsize=(6.0, 3.7), dpi=110)
    ax = fig.add_axes((0.09, 0.27, 0.56, 0.61))
    ax.semilogy(x, y, color=C1, lw=1.4)
    ax.set_ylim(0.008, 2.5)
    ax.set_xlim(0.6, 10)
    ax.set_xlabel("energy (keV)")
    ax.set_ylabel("counts (log)")
    ax.set_yticks([])
    ax.minorticks_off()
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for mu, h, lab in XRF_LINES:
        if lab:
            yy = h * 1.25 + 0.012
            dx = {"Al Ka": -0.32, "Si Ka": 0.34}.get(lab, 0.0)
            ax.text(mu + dx, yy, lab, ha="center", va="bottom", fontsize=8, color=INK, rotation=90 if h < 0.5 else 0)
    ax.set_title("EDXRF, He, 50 kV (illustrative)", loc="left", fontsize=11.5, color=INK, fontweight="bold")
    tx = fig.add_axes((0.67, 0.27, 0.32, 0.61))
    tx.axis("off")
    rows = [("", "AA spec", "result*")] + AL4047
    for i, (el, spec, res) in enumerate(rows):
        yy = 0.97 - i * 0.118
        w = "bold" if i == 0 else "normal"
        tx.text(0.02, yy, el, fontsize=9.2, fontweight=w, color=INK, va="top")
        tx.text(0.20, yy, spec, fontsize=9.2, fontweight=w, color=INK2, va="top")
        tx.text(0.80, yy, res, fontsize=9.2, fontweight=w, color=INK, va="top", ha="right")
    tx.text(0.02, 0.0, "wt %, Al 4047", fontsize=8.4, color=INK2)
    fig.text(0.01, 0.06, "*Illustrative: real line energies and the Aluminum Association's 4047 limits; the heights "
             "and the\nresult column are made up. The S2 PUMA measures loose powder under helium.", fontsize=8.2,
             color=INK2)
    fig.text(0.985, 0.955, "ILLUSTRATIVE", ha="right", fontsize=9, fontweight="bold", color="white",
             bbox=dict(boxstyle="round,pad=0.3", fc="#8a5a00", ec="none"))
    fig.savefig(path)
    plt.close(fig)


def panel_sem(path: Path):
    """The 137x and 1000x frames side by side under a REAL DATA badge, with the credit."""
    from PIL import Image, ImageDraw
    from scene import font
    W, H = 660, 400
    im = Image.new("RGB", (W, H), SURFACE)
    d = ImageDraw.Draw(im)
    a = Image.open(SEM_FILES[0]).convert("RGB")
    c = Image.open(SEM_FILES[2]).convert("RGB")
    tw = 318
    th = int(tw * a.height / a.width)
    im.paste(a.resize((tw, th), Image.LANCZOS), (8, 40))
    im.paste(c.resize((tw, th), Image.LANCZOS), (W - tw - 8, 40))
    d.text((10, 9), "SEM of the powder, c3k0n5", font=font(17, bold=True), fill=INK)
    bw = d.textlength("REAL DATA", font=font(13, bold=True)) + 16
    d.rounded_rectangle((W - bw - 8, 8, W - 8, 32), 5, fill="#1d7a55")
    d.text((W - bw, 12), "REAL DATA", font=font(13, bold=True), fill="white")
    d.text((10, 42 + th), "137x, HFW 3.03 mm", font=font(12), fill=INK2)
    d.text((W - tw - 6, 42 + th), "1000x, HFW 414 µm", font=font(12), fill=INK2)
    import textwrap
    for i, line in enumerate(textwrap.wrap(SEM_CREDIT, 92)):
        d.text((10, 62 + th + i * 16), line, font=font(11.5), fill=INK2)
    im.save(path, optimize=True)


def build_all() -> dict:
    cnt = sem_count()
    peaks = xrd_peaks()
    dv = panel_psd(cnt, OUT / "alloy_powder_psd.png")
    panel_xrd(peaks, OUT / "alloy_powder_xrd.png")
    panel_xrf(OUT / "alloy_powder_xrf.png")
    panel_sem(OUT / "alloy_powder_sem.png")
    data = dict(sem_count=cnt, laser_diffraction_cut_computed={f"Dv{int(q * 100)}": round(v, 1) for q, v in dv.items()},
                xrd_peaks_computed=peaks, xrd_height_shift_deg_per_0p1mm_at_Al111=round(height_shift(), 3),
                xrd_depth_for_99pct_mm={str(t): round(thick_enough(t), 3) for t in (40, 90, 140)},
                xrf_lines_keV=[(e, lab) for e, _, lab in XRF_LINES if lab], al4047_spec_wt_pct=AL4047)
    (OUT / "alloy_powder_data.json").write_text(json.dumps(data, indent=1) + "\n")
    return data


PANELS = {k: OUT / f"alloy_powder_{k}.png" for k in ("sem", "psd", "xrd", "xrf")}


def panel(key: str):
    """The panel image (PIL RGB), built first if it isn't there."""
    from PIL import Image
    p = PANELS[key]
    if not p.exists():
        build_all()
    return Image.open(p).convert("RGB")


if __name__ == "__main__":
    d = build_all()
    c = d["sem_count"]
    print({k: v for k, v in c.items() if k != "d_um"})
    print("cut (computed):", d["laser_diffraction_cut_computed"])
    for p in d["xrd_peaks_computed"]:
        print(p)
    print("height shift", d["xrd_height_shift_deg_per_0p1mm_at_Al111"], "depth 99 %", d["xrd_depth_for_99pct_mm"])
