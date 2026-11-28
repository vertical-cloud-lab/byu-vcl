"""Chapter 7's data panels (#303, round 8): what characterizing the lab's printed AlSi10Mg would show, and what of it
is real, computed or illustrative.

    python3 data_panels.py      # -> out/alloy_characterize_panel_{sem,eds,hv,nano,pip,vhx}.png and
                                #    out/alloy_characterize_data.json (every number shown, its status, its source)

    from data_panels import panel
    panel("hv")                 # PIL RGB, the PNG built first if it isn't there

The specimen is a coupon of the lab's LPBF AlSi10Mg build. **Nothing here has been measured on it yet.** No image
of a polished section of the lab's prints was found (searched 5 Nov 2026: the main tree of
vertical-cloud-lab/digital-alloy-lab, whose only micrographs are of the powder, and byu-vcl's ``vertical-lab/out/``
and ``docs/``); the only real image used is of the powder, and it is labelled so.

* **sem (illustrative; the inset is real).** A BSE-like section computed with numpy: melt pools 105-140 um wide and
  42-58 um deep in 30 um layers at a 110 um hatch, the later pools remelting the earlier, so that their lower edges
  make the "fish scales" of LPBF AlSi10Mg (Thijs et al. 2013, https://doi.org/10.1016/j.actamat.2012.11.052); the
  boundaries a little brighter (coarser Si), a faint cellular texture, six round gas pores (6-30 um) and one
  lack-of-fusion void with an unmelted particle in it. The inset is real but is the powder: the lab's own
  atomized Al 4047, run c3k0n5 (rePowder, 22 Oct 2026, https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/159),
  BYU's Apreo, 1000x, 5 kV, Ronnie Guymon, 26 Oct 2026 (https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/157).
  Round 7 used a stock AlSi10Mg powder here; Sterling asked for the powder the lab atomized (PR #318, 5 Nov 2026).
* **eds (illustrative).** Real line energies (X-ray Data Booklet, https://xdb.lbl.gov/Section1/Table_1-2.pdf):
  C K 0.277 keV (the conductive carbon-filled mount), O K 0.525, Mg K 1.254, Al K 1.486, Si K 1.740, Fe K-alpha 6.404.
  The heights are made up, in keeping with AlSi10Mg's composition: Si 9-11, Mg 0.20-0.45, Fe <= 0.55 wt % (EOS's
  data sheet, https://www.eos.info/en-us/metal-solutions/metal-materials/data-sheets/mds-eos-aluminium-alsi10mg;
  EN AC-43000 in EN 1706). A Kramers continuum at 15 kV through a detector efficiency, with the Al K edge; peak
  widths for an SDD with 129 eV at Mn K-alpha. The element maps reuse the sem panel's melt-pool geometry, Si along
  the boundaries, as Poisson counts. Hitachi TM4000PlusII at 15 kV (its EDS runs at 5, 10, 15 or 20 kV), AZtecOne
  (Oxford Instruments).
* **hv (illustrative).** HV = 1.8544 F / d^2 (F in kgf, d the mean diagonal in mm) at F = 0.1 kgf (HV0.1). The values,
  119-128 HV, are typical of as-built LPBF AlSi10Mg: Thijs et al. 2013 report 127 +- 3 HV0.5 without any
  precipitation hardening (https://doi.org/10.1016/j.actamat.2012.11.052; the figure read from the KU Leuven
  postprint, https://lirias.kuleuven.be/bitstream/123456789/369343/3/Thijs%20et%20al%202012_fine-structured%20aluminium%20products%20with%20controllable%20texture%20by%20SLM%20of%20AlSi10Mg%20powder_postprint.pdf);
  the diagonals are chosen to give them and the indent is drawn to scale. Mitutoyo HM-220.
* **nano (computed).** H = 1.80 GPa and E = 77 GPa, chosen as typical literature values for LPBF AlSi10Mg (not taken
  from one paper). 25 load-displacement curves (a 5 x 5 grid at a 20 um pitch, a few % scatter, softer next to a
  melt-pool boundary) are generated to 500 nm and analysed back by Oliver and Pharr
  (https://doi.org/10.1557/JMR.1992.1564): loading P = C h^2; unloading P = alpha (h - h_f)^m, m = 1.4; S = dP/dh at
  the peak; h_c = h_max - 0.75 P/S; A = 24.5 h_c^2; H = P/A; E_r = sqrt(pi) S / (2 sqrt(A)); 1/E_r = (1 - nu^2)/E +
  (1 - nu_i^2)/E_i with the diamond's E_i = 1141 GPa, nu_i = 0.07 and nu = 0.33. Noise is added and the back analysis
  fits the power law to the unloading curve above 20 % of the peak load. KLA iMicro, Berkovich tip. The slice is on
  steel in a steel mount (no polymer underneath).
* **pip (illustrative).** A Voce law, sigma = sigma_s - (sigma_s - sigma_0) exp(-eps_p / eps_0), E = 70 GPa, its three
  parameters solved to give Rp0.2 = 250 MPa, UTS = 400 MPa and 4.5 % uniform elongation, in keeping with EOS's as-built
  values (EOS M 400-4, 30 um layers, horizontal: yield 250 MPa, UTS 400 MPa, 5 % elongation; vertical: 230, 430, 3 %;
  https://www.eos.info/metal-solutions/data-sheets/aluminium/pds-eos-aluminium-alsi10mg-eos-m-400-4-30um). The
  residual indent's profile: a 1 mm radius ball, about 0.8 mm across and 78 um deep below a 7 um pile-up. PIP gets
  the curve by fitting an FEM model to that profile (Plastometrex PLX-Benchtop, https://www.plastometrex.com/).
* **vhx (illustrative, computed).** A height map of a 6 x 4 mm gauge section's fracture surface: roughly flat, finely
  dimpled (bowls ~0.1 mm), a shear lip round the edge and one gas pore, and a profile along A-B through the pore. As
  the Keyence VHX would reconstruct it from a tilt series of the free-angle head (-60 to +90 deg) and one flip of the
  bar.
"""
from __future__ import annotations

import json
import math
import os
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
KEYS = ("sem", "eds", "hv", "nano", "pip", "vhx")
PANELS = {k: OUT / f"alloy_characterize_panel_{k}.png" for k in KEYS}
DATA = OUT / "alloy_characterize_data.json"
POWDER_SEM = OUT / "footage" / "sem_c3k0n5_3.png"       # the lab's own atomized Al 4047 (r8_powder_data.SEM_FILES)

# colours (the dataviz reference palette, light mode), as in r8_powder_data.py
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"
SURFACE = "#fcfcfb"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"     # blue, orange, aqua
REAL, NOT_REAL = "#1d7a55", "#8a5a00"           # badge colours: measured / computed or illustrative
C2_TEXT = "#b8471a"                              # the orange, dark enough for text

FIGSIZE, DPI = (9.0, 6.3), 110                  # 990 x 693 px

SRC = dict(
    byu_vcl_48="https://github.com/vertical-cloud-lab/byu-vcl/issues/48",
    dal_157="https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/157",
    dal_159="https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/159",
    thijs2013="https://doi.org/10.1016/j.actamat.2012.11.052",
    xray_data_booklet="https://xdb.lbl.gov/Section1/Table_1-2.pdf",
    eos_alsi10mg_mds="https://www.eos.info/en-us/metal-solutions/metal-materials/data-sheets/mds-eos-aluminium-alsi10mg",
    eos_alsi10mg_m400="https://www.eos.info/metal-solutions/data-sheets/aluminium/pds-eos-aluminium-alsi10mg-eos-m-400-4-30um",
    thijs2013_postprint="https://lirias.kuleuven.be/bitstream/123456789/369343/3/Thijs%20et%20al%202012_fine-structured"
                        "%20aluminium%20products%20with%20controllable%20texture%20by%20SLM%20of%20AlSi10Mg%20powder_postprint.pdf",
    oliver_pharr1992="https://doi.org/10.1557/JMR.1992.1564",
    plastometrex="https://www.plastometrex.com/",
)


# ================================================================================================= helpers
def _mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 14, "axes.edgecolor": "#c9c8c2",
                         "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.8,
                         "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE})
    return plt


def _badge(fig, text, color, size=14):
    fig.text(0.985, 0.955, text, ha="right", va="center", fontsize=size, fontweight="bold", color="white",
             bbox=dict(boxstyle="round,pad=0.3", fc=color, ec="none"))


def _fig(title, badge, foot, color=NOT_REAL):
    plt = _mpl()
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    fig.text(0.02, 0.955, title, ha="left", va="center", fontsize=20, color=INK, fontweight="bold")
    _badge(fig, badge, color)
    fig.text(0.02, 0.02, foot, ha="left", va="bottom", fontsize=12, color=INK2, linespacing=1.3)
    return plt, fig


def _save(plt, fig, path: Path):
    """Written atomically (a temporary name, then a rename), as RGB, so parallel renders never read half a file."""
    from PIL import Image
    tmp = path.with_name(f".{path.stem}.{os.getpid()}.tmp.png")
    fig.savefig(tmp)
    plt.close(fig)
    Image.open(tmp).convert("RGB").save(tmp, optimize=True)
    os.replace(tmp, path)


def _stroke(w=3, c="black"):
    import matplotlib.patheffects as pe
    return [pe.withStroke(linewidth=w, foreground=c)]


def _edges(L):
    e = np.zeros(L.shape, bool)
    d = L[:, 1:] != L[:, :-1]
    e[:, 1:] |= d
    e[:, :-1] |= d
    d = L[1:, :] != L[:-1, :]
    e[1:, :] |= d
    e[:-1, :] |= d
    return e


def _cells(H, W, size, rng):
    """Voronoi cell walls (bool) of random seeds about `size` px apart."""
    import cv2
    n = int(H * W / size ** 2)
    seeds = np.ones((H, W), np.uint8)
    seeds[rng.integers(0, H, n), rng.integers(0, W, n)] = 0
    _, lab = cv2.distanceTransformWithLabels(seeds, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    return _edges(lab)


# ================================================================================================= sem
def melt_pools(W, H, um_px, seed=7, layer=30.0, hatch=110.0):
    """A label image of the melt pools in a section along the build direction (up the image): each layer's tracks are
    half-ellipses hanging below the layer's top, 105-140 um wide and 42-58 um deep; later pools overwrite (remelt)
    earlier ones. Some layers are cut obliquely (the scan rotates layer to layer) and look wider."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W]
    X = xx * um_px
    Y = (H - 1 - yy) * um_px
    L = np.full((H, W), -1, np.int32)
    nid = 0
    for k in range(-2, int(H * um_px / layer) + 3):
        top = k * layer
        widen = float(rng.choice([1.0, 1.0, 1.0, 1.25, 1.6]))
        x = -rng.uniform(0, hatch * widen)
        while x < W * um_px + hatch * widen:
            a = 0.5 * rng.uniform(105, 140) * widen
            b = rng.uniform(42, 58)
            xc = x + rng.normal(0, 5)
            x += hatch * widen
            c0, c1 = max(0, int((xc - a) / um_px)), min(W, int((xc + a) / um_px) + 2)
            r0, r1 = max(0, int(H - 1 - top / um_px)), min(H, int(H - 1 - (top - b) / um_px) + 2)
            if c0 >= c1 or r0 >= r1:
                nid += 1
                continue
            sx, sy = X[r0:r1, c0:c1], Y[r0:r1, c0:c1]
            m = (((sx - xc) / a) ** 2 + ((sy - top) / b) ** 2 <= 1) & (sy <= top)
            L[r0:r1, c0:c1][m] = nid
            nid += 1
    return L


SEM_FIELD = dict(W=900, H=640, um_px=0.75)
SEM_PORES = [(0.15, 0.25, 30), (0.47, 0.13, 14), (0.86, 0.36, 20), (0.36, 0.64, 9), (0.80, 0.72, 7),
             (0.07, 0.56, 12)]                    # (x, y as fractions of the field, diameter um)
SEM_LOF = (0.57, 0.45)                             # the lack-of-fusion void's centre, fractions of the field


def section_image(seed=7):
    from scipy import ndimage as ndi
    W, H, um = SEM_FIELD["W"], SEM_FIELD["H"], SEM_FIELD["um_px"]
    rng = np.random.default_rng(seed)
    L = melt_pools(W, H, um, seed)
    edges = _edges(L)
    band = ndi.gaussian_filter(edges.astype(float), 1.8)
    band = np.clip(band / band.max() * 2.2, 0, 1)
    cell = ndi.gaussian_filter(_cells(H, W, 4.0, rng).astype(float), 0.7)
    lf = ndi.gaussian_filter(rng.normal(size=(H, W)), 30)
    lf /= lf.std()
    img = 0.50 + 0.13 * band + 0.05 * cell + 0.015 * lf
    yy, xx = np.mgrid[0:H, 0:W]
    # the lack-of-fusion void: an irregular flat gap along a layer, an unmelted particle at its end
    cx, cy = SEM_LOF[0] * W, SEM_LOF[1] * H
    f = np.zeros((H, W))
    for i in range(7):
        ex = cx + (i - 3) * 16 + rng.uniform(-5, 5)
        ey = cy + rng.uniform(-6, 6)
        a, b = rng.uniform(16, 26), rng.uniform(6, 12)
        f += np.exp(-((xx - ex) / a) ** 2 - ((yy - ey) / b) ** 2)
    nz = ndi.gaussian_filter(rng.normal(size=(H, W)), 3)
    f += 2.5 * nz
    lof = f > 0.75
    lab, n = ndi.label(lof)
    if n > 1:                                          # keep the biggest piece
        sizes = ndi.sum(lof, lab, range(1, n + 1))
        lof = lab == (1 + int(np.argmax(sizes)))
    rr_lof = np.hypot(xx - (cx + 62), yy - (cy + 2))
    part = rr_lof < 12                                 # a 18 um unmelted particle, half in the void
    img[lof] = 0.06 + 0.04 * rng.random(int(lof.sum()))
    img[part] = 0.47 + 0.06 * (1 - rr_lof[part] / 12)
    img[(rr_lof >= 12) & (rr_lof < 13.5) & lof] = 0.62
    lof_box = np.argwhere(lof | part)
    lof_size = ((np.ptp(lof_box[:, 1]) + 1) * um, (np.ptp(lof_box[:, 0]) + 1) * um)
    # gas pores: round, dark, a bright rim where the beam meets the edge
    for fx, fy, d in SEM_PORES:
        r = d / 2 / um
        rr = np.hypot(xx - fx * W, yy - fy * H)
        inside = rr <= r
        img[inside] = 0.05 + 0.07 * (rr[inside] / r) ** 2
        rim = (rr > r) & (rr < r + 1.6)
        img[rim] += 0.14
    img += rng.normal(0, 0.03, (H, W))
    img = ndi.gaussian_filter(img, 0.6)
    return np.clip(img, 0, 1), edges, dict(lack_of_fusion_um=[round(lof_size[0]), round(lof_size[1])],
                                           unmelted_particle_um=18)


def panel_sem(path: Path) -> dict:
    from matplotlib.patches import Rectangle
    from PIL import Image
    W, H, um = SEM_FIELD["W"], SEM_FIELD["H"], SEM_FIELD["um_px"]
    img, edges, info = section_image()
    foot = ("No micrograph of this section exists yet. Computed: melt pools ~120 µm wide, ~50 µm deep in\n"
            "30 µm layers; gas pores 6-30 µm; a lack-of-fusion void. The inset is real, but it is the powder.")
    plt, fig = _fig("Polished section, BSE (as it would look)", "ILLUSTRATIVE", foot)
    ax = fig.add_axes((0.015, 0.15, 0.63, 0.755))
    ax.imshow(img, cmap="gray", vmin=0, vmax=1, interpolation="lanczos")
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_axis_off()
    # the scale bar
    sb = 100 / um
    x1, yb = W - 28, H - 34
    ax.add_patch(Rectangle((x1 - sb, yb), sb, 10, fc="white", ec=INK, lw=0.8))
    ax.text(x1 - sb / 2, yb - 8, "100 µm", color="white", ha="center", va="bottom", fontsize=16, fontweight="bold",
            path_effects=_stroke())
    # the build direction
    ax.annotate("", xy=(W - 30, 0.30 * H), xytext=(W - 30, 0.62 * H),
                arrowprops=dict(arrowstyle="-|>", color="white", lw=2.5, mutation_scale=22))
    ax.text(W - 48, 0.46 * H, "build", color="white", ha="center", va="center", rotation=90, fontsize=15,
            fontweight="bold", path_effects=_stroke())
    # labels
    pts = np.argwhere(edges)

    def near_edge(fx, fy):
        i = np.argmin((pts[:, 1] - fx * W) ** 2 + (pts[:, 0] - fy * H) ** 2)
        return pts[i, 1], pts[i, 0]

    kw = dict(color="white", fontsize=16, fontweight="bold", path_effects=_stroke(),
              arrowprops=dict(arrowstyle="-|>", color="white", lw=2.2, mutation_scale=18))
    ax.annotate("melt-pool\nboundaries", xy=near_edge(0.19, 0.69), xytext=(0.03 * W, 0.97 * H), va="bottom",
                ha="left", **kw)
    p = SEM_PORES[0]
    ax.annotate("gas pore", xy=(p[0] * W + 0.6 * p[2] / um, p[1] * H - 0.6 * p[2] / um), xytext=(0.27 * W, 0.08 * H),
                va="center", ha="left", **kw)
    ax.annotate("lack of fusion", xy=(SEM_LOF[0] * W, SEM_LOF[1] * H + 14), xytext=(0.43 * W, 0.72 * H),
                va="top", ha="center", **kw)
    # the inset: the real powder image
    pw = np.asarray(Image.open(POWDER_SEM).convert("L"))
    h_frac = 0.32 * 990 * pw.shape[0] / pw.shape[1] / 693
    ax2 = fig.add_axes((0.665, 0.42, 0.32, h_frac))
    ax2.imshow(pw, cmap="gray", vmin=0, vmax=255, interpolation="lanczos")
    ax2.set_axis_off()
    top = 0.42 + h_frac
    fig.text(0.665, top + 0.035, "REAL DATA", ha="left", va="center", fontsize=13, fontweight="bold", color="white",
             bbox=dict(boxstyle="round,pad=0.3", fc=REAL, ec="none"))
    fig.text(0.665, 0.405, "The powder, not the section:\nthe lab's atomized Al 4047,\nrun c3k0n5 (DAL #159).\n"
             "BYU Apreo, 1000x, 5 kV,\nR. Guymon, 26 Oct 2026\n(DAL #157)", ha="left", va="top", fontsize=13, color=INK,
             linespacing=1.35)
    _save(plt, fig, path)
    return dict(status="illustrative", what="a computed BSE-like section; no micrograph of the printed section exists",
                field_um=[W * um, H * um], um_per_px=um, layer_um=30, hatch_um=110, melt_pool_width_um=[105, 140],
                melt_pool_depth_um=[42, 58], gas_pore_diameters_um=[p[2] for p in SEM_PORES], **info,
                scale_bar_um=100, source=SRC["thijs2013"],
                inset=dict(status="real", file=f"footage/{POWDER_SEM.name}", what="the lab's own atomized Al 4047, "
                           "run c3k0n5 (rePowder, 22 Oct 2026, DAL #159), not the section; replaces round 7's stock "
                           "AlSi10Mg powder image (PR #318 review)", instrument="BYU Apreo, ETD", mag="1000x", kV=5,
                           by="Ronnie Guymon", date="2026-10-26", source=SRC["dal_157"], run=SRC["dal_159"]),
                real_section_image_found=False)


# ================================================================================================= eds
EDS_KV = 15.0
EDS_LINES = [(0.277, 0.060, "C K"), (0.525, 0.035, "O K"), (1.254, 0.011, "Mg K"), (1.486, 1.0, "Al K"),
             (1.557, 0.018, ""), (1.740, 0.115, "Si K"), (1.836, 0.003, ""), (6.404, 0.0045, "Fe Kα"),
             (7.058, 0.0007, "")]                  # keV (X-ray Data Booklet), height relative to Al K (made up)
ALSI10MG = dict(Si="9.0-11.0", Mg="0.20-0.45", Fe="0.55 max", Al="balance")      # wt %, EOS data sheet / EN 1706


def _fwhm(e_kev):
    """An SDD's FWHM (keV): 129 eV at Mn K-alpha, Fano 0.115, 3.8 eV per pair."""
    return math.sqrt(129.0 ** 2 - 2.42 * 5895 + 2.42 * e_kev * 1000) / 1000


def eds_spectrum(seed=11):
    rng = np.random.default_rng(seed)
    e = np.arange(0.05, 10.0, 0.01)                    # keV, 10 eV channels
    eff = np.exp(-(0.42 / e) ** 3)                     # the window and dead layer at low energy (approximate)
    cont = 0.0016 * np.clip(EDS_KV - e, 0, None) / e * eff                 # Kramers
    cont = cont * np.where(e > 1.559, 0.75 + 0.25 * (1 - np.exp(-(e - 1.559) / 2.0)), 1.0)   # the Al K edge
    y = cont.copy()
    for mu, h, _ in EDS_LINES:
        y = y + h * np.exp(-4 * math.log(2) * ((e - mu) / _fwhm(mu)) ** 2)
    counts = rng.poisson(y * 30000).astype(float)
    return e, counts, cont * 30000


def eds_maps(N=150, seed=5):
    from scipy import ndimage as ndi
    rng = np.random.default_rng(seed)
    L = melt_pools(N, N, SEM_FIELD["um_px"], seed=seed + 1)
    band = ndi.gaussian_filter(_edges(L).astype(float), 1.2)
    band = np.clip(band / band.max() * 2, 0, 1)
    cell = ndi.gaussian_filter(_cells(N, N, 3.0, rng).astype(float), 0.6)
    yy, xx = np.mgrid[0:N, 0:N]
    pore = np.hypot(xx - 0.68 * N, yy - 0.35 * N) < 9
    si = 0.5 + 1.8 * band + 0.6 * cell
    al = 1.0 - 0.12 * band - 0.05 * cell
    mg = 1.0 + 0.4 * band
    out = {}
    for name, m, k in (("Al K", al, 14.0), ("Si K", si, 2.2), ("Mg K", mg, 0.35)):
        m = m.copy()
        m[pore] = 0.02
        out[name] = ndi.gaussian_filter(rng.poisson(m * k).astype(float), 0.7)
    return out


def panel_eds(path: Path) -> dict:
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Rectangle
    e, counts, cont = eds_spectrum()
    foot = ("Real line energies; heights made up to match AlSi10Mg (Si 9-11, Mg 0.20-0.45, Fe ≤ 0.55 wt %,\n"
            "EOS data sheet, EN AC-43000). TM4000PlusII at 15 kV, AZtecOne (Oxford Instruments).")
    plt, fig = _fig("EDS of the polished section", "ILLUSTRATIVE", foot)
    ax = fig.add_axes((0.085, 0.20, 0.58, 0.68))
    ax.fill_between(e, 1, counts + 1, color=C1, alpha=0.18, lw=0)
    ax.semilogy(e, counts + 1, color=C1, lw=1.3)
    ax.semilogy(e, cont + 1, color=MUTED, lw=1.2, ls="--")
    ax.set_xlim(0, 8)
    ax.set_ylim(3, 2.5e5)
    ax.set_yticks([])
    ax.minorticks_off()
    ax.set_xlabel("energy (keV)")
    ax.set_ylabel("counts (log)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    lk = dict(fontsize=15, color=INK, fontweight="bold", arrowprops=dict(arrowstyle="-", color=INK2, lw=1.0))
    ax.annotate("C K\n(mount)", xy=(0.277, 2300), xytext=(0.04, 1.3e4), ha="left", va="bottom", **lk)
    ax.annotate("O K", xy=(0.525, 1300), xytext=(0.66, 3.3e3), ha="left", va="bottom", **lk)
    ax.annotate("Mg K", xy=(1.254, 420), xytext=(1.0, 90), ha="center", va="top", **lk)
    ax.text(1.60, 3.2e4, "Al K", ha="left", va="bottom", fontsize=15, color=INK, fontweight="bold")
    ax.text(1.85, 4.6e3, "Si K", ha="left", va="bottom", fontsize=15, color=INK, fontweight="bold")
    ax.text(6.404, 330, "Fe Kα", ha="center", va="bottom", fontsize=15, color=INK, fontweight="bold")
    ax.text(3.3, 280, "continuum,\nE₀ = 15 kV", fontsize=13.5, color=INK2, ha="left", va="bottom")
    maps = eds_maps()
    cols = {"Al K": C1, "Si K": C2, "Mg K": C3}
    fig.text(0.755, 0.905, "maps, one field", ha="left", va="center", fontsize=14, color=INK2)
    for i, (name, m) in enumerate(maps.items()):
        b = 0.15 + (2 - i) * 0.248
        mx = fig.add_axes((0.76, b, 0.16, 0.228))
        cm = LinearSegmentedColormap.from_list(name, ["#000000", cols[name], "#ffffff"])
        mx.imshow(m, cmap=cm, vmin=0, vmax=np.percentile(m, 99.7) * 1.15, interpolation="nearest")
        mx.set_axis_off()
        fig.text(0.75, b + 0.114, name, ha="right", va="center", fontsize=16, fontweight="bold",
                 color={"Al K": C1, "Si K": C2_TEXT, "Mg K": "#14805a"}[name])
        if i == 2:
            n = m.shape[0]
            sb = 50 / SEM_FIELD["um_px"]
            mx.add_patch(Rectangle((n - 8 - sb, n - 14), sb, 5, fc="white", ec="none"))
            mx.text(n - 8 - sb / 2, n - 17, "50 µm", color="white", ha="center", va="bottom", fontsize=12,
                    fontweight="bold")
    _save(plt, fig, path)
    return dict(status="illustrative", kV=EDS_KV, analyser="AZtecOne (Oxford Instruments)", sem="Hitachi TM4000PlusII",
                lines_keV={lab: mu for mu, _, lab in EDS_LINES if lab}, lines_source=SRC["xray_data_booklet"],
                heights_relative_to_Al_K_made_up={lab: h for _, h, lab in EDS_LINES if lab},
                detector_fwhm_eV_at_MnKa=129, composition_wt_pct=ALSI10MG,
                composition_source=[SRC["eos_alsi10mg_mds"], "EN 1706, EN AC-43000 (AlSi10Mg(a))"],
                maps="the sem panel's melt-pool geometry, Si along the boundaries, Poisson counts (illustrative)")


# ================================================================================================= hv
HV_F = 0.1                                          # kgf (HV0.1, 100 gf)
HV_D = [(38.3, 38.7), (38.8, 39.2), (37.9, 38.3), (38.6, 39.0), (39.2, 39.6)]   # um: d1, d2 of five indents


def hv_of(d1, d2, F=HV_F):
    d = (d1 + d2) / 2 / 1000.0                      # mm
    return 1.8544 * F / d ** 2


def vickers_image(d1, d2, N=520, field=70.0, seed=3):
    """Bright-field top view of a Vickers indent in a polished face: the four faces dark (they tilt the light out of
    the objective), the ridges along the diagonals, a dark rim; field x field um."""
    from scipy import ndimage as ndi
    rng = np.random.default_rng(seed)
    um = field / N
    yy, xx = np.mgrid[0:N, 0:N]
    X = (xx - (N - 1) / 2) * um
    Y = ((N - 1) / 2 - yy) * um
    lf = ndi.gaussian_filter(rng.normal(size=(N, N)), N / 25)
    lf /= lf.std()
    img = 0.80 + 0.02 * lf + 0.012 * rng.normal(size=(N, N))
    for _ in range(3):                                   # fine polishing scratches
        ang, off = rng.uniform(0, np.pi), rng.uniform(-0.4, 0.4) * field
        dist = np.abs(X * math.sin(ang) - Y * math.cos(ang) - off)
        img -= 0.05 * np.exp(-(dist / (0.2 + 0.0 * field)) ** 2)
    for _ in range(4):                                   # a few dark specks (fine pores)
        sx, sy = rng.uniform(-0.45, 0.45, 2) * field
        if abs(sx) / (d1 / 2) + abs(sy) / (d2 / 2) < 1.3:
            continue
        img[np.hypot(X - sx, Y - sy) < rng.uniform(0.3, 0.8)] = 0.25
    u = np.abs(X) / (d1 / 2) + np.abs(Y) / (d2 / 2)
    inside = u <= 1
    q = (X >= 0).astype(int) + 2 * (Y >= 0).astype(int)
    shade = np.array([0.20, 0.13, 0.25, 0.17])[q] * (0.7 + 0.3 * u)
    img = np.where(inside, shade, img)
    ridge = inside & ((np.abs(X) < 2 * um) | (np.abs(Y) < 2 * um))
    img[ridge] += 0.09
    halo = (u > 1) & (u < 1.10)
    img[halo] -= 0.10 * (1 - (u[halo] - 1) / 0.10)
    img = ndi.gaussian_filter(img, 0.9 * N / 520)
    return np.clip(img, 0, 1), um


def panel_hv(path: Path) -> dict:
    from matplotlib.patches import Rectangle
    vals = [hv_of(*d) for d in HV_D]
    mean, sd = float(np.mean(vals)), float(np.std(vals, ddof=1))
    d1, d2 = HV_D[0]
    foot = ("A typical value for as-built LPBF AlSi10Mg (Thijs et al. 2013: 127 ± 3 HV0.5);\n"
            "the diagonals are computed from it and the indent drawn to scale. Mitutoyo HM-220, 100 gf.")
    plt, fig = _fig("Micro-Vickers, polished face", "ILLUSTRATIVE", foot)
    img, um = vickers_image(d1, d2)
    N = img.shape[0]
    ax = fig.add_axes((0.02, 0.14, 0.52, 0.76))
    ax.imshow(img, cmap="gray", vmin=0, vmax=1, interpolation="lanczos")
    ax.set_xlim(0, N)
    ax.set_ylim(N, 0)
    ax.set_axis_off()
    c = (N - 1) / 2
    xl, xr = c - d1 / 2 / um, c + d1 / 2 / um
    yt, yb = c - d2 / 2 / um, c + d2 / 2 / um
    for x in (xl, xr):
        ax.axvline(x, color=C1, lw=1.6)
    for y in (yt, yb):
        ax.axhline(y, color=C2, lw=1.6)
    ya = yb + 45
    ax.annotate("", xy=(xl, ya), xytext=(xr, ya), arrowprops=dict(arrowstyle="<|-|>", color=C1, lw=2,
                                                                   mutation_scale=16))
    ax.text(c, ya + 10, f"d₁ = {d1:.1f} µm", color=C1, ha="center", va="top", fontsize=17, fontweight="bold",
            path_effects=_stroke(4, "white"))
    xa = xr + 45
    ax.annotate("", xy=(xa, yt), xytext=(xa, yb), arrowprops=dict(arrowstyle="<|-|>", color=C2, lw=2,
                                                                   mutation_scale=16))
    ax.text(xa + 12, c, f"d₂ = {d2:.1f} µm", color=C2_TEXT, ha="left", va="center", rotation=90, fontsize=17,
            fontweight="bold", path_effects=_stroke(4, "white"))
    sb = 10 / um
    ax.add_patch(Rectangle((22, N - 30), sb, 7, fc=INK, ec="none"))
    ax.text(22 + sb / 2, N - 36, "10 µm", color=INK, ha="center", va="bottom", fontsize=14, fontweight="bold",
            path_effects=_stroke(3, "white"))
    # the result
    hv0 = vals[0]
    fig.text(0.575, 0.835, "HV0.1", ha="left", va="center", fontsize=22, color=INK2, fontweight="bold")
    fig.text(0.575, 0.71, f"{hv0:.0f}", ha="left", va="center", fontsize=66, color=INK, fontweight="bold")
    fig.text(0.575, 0.585, "HV = 1.8544 F / d²", ha="left", va="center", fontsize=18, color=INK)
    fig.text(0.575, 0.525, f"F = 0.1 kgf,  d = {(d1 + d2) / 2:.1f} µm", ha="left", va="center", fontsize=15,
             color=INK2)
    # five indents
    fig.text(0.575, 0.44, "five indents", ha="left", va="center", fontsize=14, color=INK2)
    for i, (a, b) in enumerate(HV_D):
        t, _ = vickers_image(a, b, N=130, seed=10 + i)
        tx = fig.add_axes((0.575 + i * 0.083, 0.245, 0.074, 0.074 * 990 / 693 * 1.0))
        tx.imshow(t, cmap="gray", vmin=0, vmax=1)
        tx.set_axis_off()
        fig.text(0.575 + i * 0.083 + 0.037, 0.225, f"{vals[i]:.0f}", ha="center", va="top", fontsize=15,
                 color=INK, fontweight="bold")
    fig.text(0.575, 0.145, f"{mean:.0f} ± {sd:.0f} HV0.1 (n = 5)", ha="left", va="center", fontsize=17,
             color=INK, fontweight="bold")
    _save(plt, fig, path)
    return dict(status="illustrative", instrument="Mitutoyo HM-220", load_kgf=HV_F, formula="HV = 1.8544 F / d^2",
                indents=[dict(d1_um=a, d2_um=b, HV=round(v, 1)) for (a, b), v in zip(HV_D, vals)],
                mean_HV=round(mean, 1), sd_HV=round(sd, 1),
                literature="as-built LPBF (SLM) AlSi10Mg: 127 +- 3 HV0.5, no precipitation hardening (Thijs et al. "
                           "2013, Acta Materialia 61, 1809-1819)",
                source=[SRC["thijs2013"], SRC["thijs2013_postprint"]])


# ================================================================================================= nano
NU_I, E_I, NU_S = 0.07, 1141.0, 0.33
H_SET, E_SET = 1.80, 77.0                          # GPa: typical literature values for LPBF AlSi10Mg
H_MAX, M_UNL = 500.0, 1.4                          # nm; the unloading exponent
PITCH = 20.0                                        # um


def _er(E):
    return 1.0 / ((1 - NU_S ** 2) / E + (1 - NU_I ** 2) / E_I)


def _e_from_er(er):
    return (1 - NU_S ** 2) / (1.0 / er - (1 - NU_I ** 2) / E_I)


def op_forward(H, E, hmax=H_MAX, m=M_UNL):
    """The peak load (mN), stiffness (mN/nm), h_c, A (nm^2) and h_f that make a curve to hmax give H and E exactly."""
    er = _er(E)
    hc = hmax / (1 + 0.75 * H * math.sqrt(24.5 * math.pi) / (2 * er))
    A = 24.5 * hc ** 2
    P = H * A * 1e-6                                   # GPa nm^2 -> mN
    S = 2 * er * math.sqrt(A) / math.sqrt(math.pi) * 1e-6
    return dict(P=P, S=S, hc=hc, A=A, hf=hmax - m * P / S)


def op_curves(H, E, rng, n=140):
    f = op_forward(H, E)
    hl = np.linspace(0, H_MAX, n)
    pl = f["P"] * (hl / H_MAX) ** 2
    hu = np.linspace(H_MAX, f["hf"], n)
    pu = f["P"] * ((hu - f["hf"]) / (H_MAX - f["hf"])) ** M_UNL
    pl, pu = pl + rng.normal(0, 0.006, n), pu + rng.normal(0, 0.006, n)
    hl, hu = hl + rng.normal(0, 0.25, n), hu + rng.normal(0, 0.25, n)
    pl[0], hl[0] = 0.0, 0.0
    return hl, pl, hu, pu, f


def op_analyse(hu, pu):
    """Oliver-Pharr from the unloading curve: fit P = alpha (h - h_f)^m above 20 % of the peak, S at h_max."""
    from scipy.optimize import curve_fit
    pmax, hmax = float(pu[0]), float(hu[0])
    sel = pu > 0.2 * pmax

    def law(h, alpha, hf, m):
        return alpha * np.clip(h - hf, 1e-9, None) ** m

    hf0 = hmax - M_UNL * pmax / 0.2
    p0 = (pmax / (hmax - hf0) ** M_UNL, hf0, M_UNL)
    (alpha, hf, m), _ = curve_fit(law, hu[sel], pu[sel], p0=p0,
                                  bounds=((0, 0.5 * hmax, 1.0), (np.inf, hmax - 5, 2.2)), maxfev=20000)
    S = alpha * m * (hmax - hf) ** (m - 1)
    hc = hmax - 0.75 * pmax / S
    A = 24.5 * hc ** 2
    er = math.sqrt(math.pi) * S / (2 * math.sqrt(A)) * 1e6
    return dict(P_mN=pmax, S_mN_per_nm=S, h_c_nm=hc, A_nm2=A, m=m, h_f_nm=hf, H_GPa=pmax / A * 1e6,
                Er_GPa=er, E_GPa=_e_from_er(er))


def nano_grid(seed=21):
    rng = np.random.default_rng(seed)
    xs = np.arange(5) * PITCH
    X, Y = np.meshgrid(xs, xs)
    arc_c, arc_r = (-50.0, -35.0), math.hypot(40 + 50, 40 + 35)      # a melt-pool boundary through (40, 40)
    dist = np.abs(np.hypot(X - arc_c[0], Y - arc_c[1]) - arc_r)
    H = H_SET * (1 + rng.normal(0, 0.025, X.shape)) - 0.15 * np.exp(-(dist / 3.0) ** 2)
    E = E_SET * (1 + rng.normal(0, 0.015, X.shape))
    rows = []
    for i in range(5):
        for j in range(5):
            hl, pl, hu, pu, f = op_curves(float(H[i, j]), float(E[i, j]), rng)
            r = op_analyse(hu, pu)
            rows.append(dict(x_um=float(X[i, j]), y_um=float(Y[i, j]), H_set=float(H[i, j]), E_set=float(E[i, j]),
                             curve=(hl, pl, hu, pu), **r))
    return rows, (arc_c, arc_r)


def panel_nano(path: Path) -> dict:
    from matplotlib.colors import LinearSegmentedColormap
    rows, (arc_c, arc_r) = nano_grid()
    Hs = np.array([r["H_GPa"] for r in rows])
    Es = np.array([r["E_GPa"] for r in rows])
    soft = int(np.argmin(Hs))
    typical = [i for i in (2, 7, 13, 21, 24) if i != soft][:4]
    foot = ("Curves generated from H 1.80 GPa, E 77 GPa (typical literature values), then Oliver-Pharr back:\n"
            "A = 24.5 h_c², diamond 1141 GPa, ν 0.33. The slice is on steel in a steel mount, no polymer.")
    plt, fig = _fig("Nanoindentation, KLA iMicro (Berkovich)", "COMPUTED", foot)
    ax = fig.add_axes((0.085, 0.20, 0.47, 0.68))
    for k, i in enumerate(typical):
        hl, pl, hu, pu = rows[i]["curve"]
        ax.plot(hl, pl, color=C1, lw=1.6, alpha=0.85, label="typical" if k == 0 else None)
        ax.plot(hu, pu, color=C1, lw=1.6, alpha=0.85)
    hl, pl, hu, pu = rows[soft]["curve"]
    ax.plot(hl, pl, color=C2, lw=2.2, label="on a melt-pool boundary")
    ax.plot(hu, pu, color=C2, lw=2.2)
    r = rows[typical[0]]
    hh = np.linspace(H_MAX - 95, H_MAX + 8, 10)
    ax.plot(hh, r["P_mN"] + r["S_mN_per_nm"] * (hh - H_MAX), color=INK, lw=1.4, ls="--")
    ax.annotate("S = dP/dh", xy=(468, 2.8), xytext=(420, 1.0), ha="right", va="center", fontsize=15, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=1.0))
    ax.set_xlim(0, 540)
    ax.set_ylim(0, 11.8)
    ax.set_xticks([0, 100, 200, 300, 400, 500])
    ax.set_xlabel("depth h (nm)")
    ax.set_ylabel("load P (mN)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(loc="upper left", fontsize=13.5, frameon=False, labelcolor=INK)
    # the grid map
    mx = fig.add_axes((0.635, 0.44, 0.25, 0.25 * 990 / 693))
    cm = LinearSegmentedColormap.from_list("seq", ["#d3e3f7", C1, "#0c2f5e"])
    t = np.linspace(0, 2 * np.pi, 800)
    ax_x, ax_y = arc_c[0] + arc_r * np.cos(t), arc_c[1] + arc_r * np.sin(t)
    mx.plot(ax_x, ax_y, color=MUTED, lw=6, alpha=0.35, solid_capstyle="round")
    sc = mx.scatter([r["x_um"] for r in rows], [r["y_um"] for r in rows], c=Hs, cmap=cm, s=420, marker="s",
                    vmin=round(Hs.min() - 0.05, 1), vmax=round(Hs.max() + 0.05, 1), edgecolors="white", lw=1.0)
    mx.scatter([rows[soft]["x_um"]], [rows[soft]["y_um"]], s=420, marker="s", facecolors="none", edgecolors=C2,
               lw=3.0)
    mx.set_xlim(-12, 92)
    mx.set_ylim(-12, 92)
    mx.set_aspect("equal")
    mx.set_xticks([0, 40, 80])
    mx.set_yticks([0, 40, 80])
    mx.tick_params(labelsize=12)
    mx.set_xlabel("µm", fontsize=12, labelpad=1)
    for s in ("top", "right"):
        mx.spines[s].set_visible(False)
    cb = fig.colorbar(sc, cax=fig.add_axes((0.905, 0.46, 0.014, 0.30)))
    cb.set_label("H (GPa)", fontsize=13, color=INK2)
    cb.ax.tick_params(labelsize=12)
    cb.outline.set_visible(False)
    fig.text(0.625, 0.315, f"H = {Hs.mean():.2f} ± {Hs.std(ddof=1):.2f} GPa", fontsize=19, color=INK,
             fontweight="bold", ha="left", va="center")
    fig.text(0.625, 0.245, f"E = {Es.mean():.0f} ± {Es.std(ddof=1):.0f} GPa", fontsize=19, color=INK,
             fontweight="bold", ha="left", va="center")
    fig.text(0.625, 0.18, "25 indents, 500 nm deep", fontsize=13, color=INK2, ha="left", va="center")
    _save(plt, fig, path)
    return dict(status="computed", instrument="KLA iMicro, Berkovich", H_set_GPa=H_SET, E_set_GPa=E_SET,
                H_E_source="typical literature values for LPBF AlSi10Mg (not taken from one paper)",
                method=SRC["oliver_pharr1992"], h_max_nm=H_MAX, unloading_m=M_UNL, area="A = 24.5 h_c^2",
                tip_E_GPa=E_I, tip_nu=NU_I, sample_nu=NU_S, grid="5 x 5", pitch_um=PITCH,
                H_mean_GPa=round(float(Hs.mean()), 3), H_sd_GPa=round(float(Hs.std(ddof=1)), 3),
                E_mean_GPa=round(float(Es.mean()), 2), E_sd_GPa=round(float(Es.std(ddof=1)), 2),
                softest=dict(x_um=rows[soft]["x_um"], y_um=rows[soft]["y_um"], H_GPa=round(float(Hs[soft]), 3)),
                indents=[{k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k != "curve"}
                         for r in rows],
                mount="the slice is on steel in a steel mount (no polymer underneath)")


# ================================================================================================= pip
E_MOD = 70000.0                                     # MPa
PIP_TARGET = dict(Rp02_MPa=250.0, UTS_MPa=400.0, uniform_elongation=0.045)


def voce(ep, s0, ss, e0):
    return ss - (ss - s0) * np.exp(-np.asarray(ep) / e0)


def voce_points(s0, ss, e0):
    """Rp0.2, the nominal UTS and the uniform elongation (nominal, elastic included) of a Voce law; necking where
    d(nominal stress)/d(plastic strain) = 0, i.e. (ss - st) / e0 = st E / (E - st)."""
    b = ss + E_MOD * (1 + e0)
    stu = (b - math.sqrt(b * b - 4 * ss * E_MOD)) / 2
    epu = -e0 * math.log((ss - stu) / (ss - s0))
    eu = math.expm1(epu + stu / E_MOD)
    sp = float(voce(0.002, s0, ss, e0))
    return sp / (1 + math.expm1(0.002 + sp / E_MOD)), stu / (1 + eu), eu, stu, epu


def fit_voce():
    from scipy.optimize import fsolve
    t = PIP_TARGET

    def res(p):
        rp, uts, eu, _, _ = voce_points(*p)
        return [rp - t["Rp02_MPa"], uts - t["UTS_MPa"], 100 * (eu - t["uniform_elongation"])]

    return [float(v) for v in fsolve(res, [225.0, 425.0, 0.012])]


def pip_profile(R=1.05, a=0.40, pile=8.0, w=0.12):
    """The residual indent's profile (mm, um): a spherical cap (the ball's 1 mm radius, a little larger after elastic
    recovery) of contact radius a, a pile-up of height `pile` decaying outward over w."""
    from scipy import ndimage as ndi
    r = np.linspace(-1.2, 1.2, 961)
    ar = np.abs(r)
    cap = (R - np.sqrt(R ** 2 - np.minimum(ar, a) ** 2)) * 1000
    capa = (R - math.sqrt(R ** 2 - a ** 2)) * 1000
    z = np.where(ar <= a, cap - capa + pile, pile * np.exp(-(ar - a) / w))
    z = ndi.gaussian_filter1d(z, 6)
    return r, z


def panel_pip(path: Path) -> dict:
    s0, ss, e0 = fit_voce()
    rp, uts, eu, stu, epu = voce_points(s0, ss, e0)
    foot = ("A Voce law chosen to match EOS's as-built AlSi10Mg (horizontal: yield 250 MPa, UTS 400 MPa,\n"
            "5 % elongation). PIP gets the curve by fitting an FEM model to the indent's profile.")
    plt, fig = _fig("PIP, Plastometrex PLX-Benchtop", "ILLUSTRATIVE", foot)
    ax = fig.add_axes((0.10, 0.20, 0.55, 0.68))
    ep = np.linspace(0, epu, 400)
    st = voce(ep, s0, ss, e0)
    et = ep + st / E_MOD
    en = np.expm1(et)
    sn = st / (1 + en)
    ee = s0 / E_MOD
    ax.plot(np.r_[0, 100 * np.expm1(ee), 100 * en], np.r_[0, s0 / (1 + np.expm1(ee)), sn], color=C1, lw=2.6,
            label="nominal (engineering)")
    ep2 = np.linspace(0, 0.14, 400)
    st2 = voce(ep2, s0, ss, e0)
    et2 = ep2 + st2 / E_MOD
    u = ep2 <= epu
    ax.plot(np.r_[0, 100 * et2[u]], np.r_[0, st2[u]], color=C2, lw=2.6, label="true")
    ax.plot(100 * et2[~u], st2[~u], color=C2, lw=2.0, ls="--")
    ax.plot([100 * eu], [uts], "o", color=C1, ms=9)
    ax.annotate(f"UTS {uts:.0f} MPa", (100 * eu, uts), xytext=(100 * eu + 0.6, uts - 70), fontsize=16,
                color=INK, fontweight="bold", arrowprops=dict(arrowstyle="-", color=INK2, lw=1.2))
    ey = 0.002 + rp / E_MOD
    ax.plot([100 * ey], [rp], "o", color=C1, ms=9)
    ax.annotate(f"yield {rp:.0f} MPa", (100 * ey, rp), xytext=(1.6, 150), fontsize=16, color=INK,
                fontweight="bold", arrowprops=dict(arrowstyle="-", color=INK2, lw=1.2))
    ax.annotate("", xy=(100 * eu, 30), xytext=(0, 30), arrowprops=dict(arrowstyle="<|-|>", color=INK2, lw=1.4))
    ax.text(100 * eu / 2, 42, f"uniform {100 * eu:.1f} %", ha="center", va="bottom", fontsize=14, color=INK2)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 520)
    ax.set_xlabel("strain (%)")
    ax.set_ylabel("stress (MPa)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(loc="lower right", fontsize=14, frameon=False, labelcolor=INK)
    # the profile
    r, z = pip_profile()
    px = fig.add_axes((0.735, 0.50, 0.245, 0.30))
    px.plot(r, z, color=C2, lw=2.2, label="FEM fit")
    rng = np.random.default_rng(4)
    k = slice(0, None, 24)
    px.plot(r[k], z[k] + rng.normal(0, 1.2, len(r[k])), "o", color=C1, ms=4.5, label="profile")
    px.set_xlim(-1.2, 1.2)
    px.set_ylim(-85, 25)
    px.set_xticks([-1, 0, 1])
    px.set_yticks([-80, -40, 0])
    px.tick_params(labelsize=12)
    px.set_xlabel("radius (mm)", fontsize=12.5, labelpad=1)
    px.set_ylabel("height (µm)", fontsize=12.5, labelpad=1)
    for s in ("top", "right"):
        px.spines[s].set_visible(False)
    px.legend(loc="lower right", fontsize=11.5, frameon=False, labelcolor=INK, handlelength=1.2, borderpad=0.1)
    fig.text(0.735, 0.845, "the indent's profile", fontsize=15, color=INK, fontweight="bold", ha="left",
             va="center")
    depth = float(z.max() - z.min())
    fig.text(0.735, 0.33, f"1 mm-radius ball\n0.8 mm across\n{depth:.0f} µm deep\n{z.max():.0f} µm pile-up",
             fontsize=14, color=INK2, ha="left", va="center", linespacing=1.35)
    _save(plt, fig, path)
    return dict(status="illustrative", instrument="Plastometrex PLX-Benchtop", source_pip=SRC["plastometrex"],
                law="Voce: sigma = sigma_s - (sigma_s - sigma_0) exp(-eps_p / eps_0)", E_MPa=E_MOD,
                voce=dict(sigma_0_MPa=round(s0, 1), sigma_s_MPa=round(ss, 1), eps_0=round(e0, 5)),
                targets=PIP_TARGET, Rp02_MPa=round(rp, 1), UTS_MPa=round(uts, 1), uniform_elongation_pct=round(100 * eu, 2),
                true_stress_at_necking_MPa=round(stu, 1),
                eos_as_built=dict(horizontal=dict(yield_MPa=250, UTS_MPa=400, elongation_pct=5),
                                  vertical=dict(yield_MPa=230, UTS_MPa=430, elongation_pct=3),
                                  source=SRC["eos_alsi10mg_m400"]),
                profile=dict(ball_radius_mm=1.0, contact_radius_mm=0.40, depth_below_pileup_um=round(depth, 1),
                             pileup_um=round(float(z.max()), 1)))


# ================================================================================================= vhx
VHX_SECTION = (6.0, 4.0)                            # mm, the gauge section
VHX_PORE = (1.3, -0.7, 0.16, 120.0)                 # x, y, radius (mm), depth (um)


def fracture_map(nx=300, ny=200, seed=9):
    import cv2
    from scipy import ndimage as ndi
    rng = np.random.default_rng(seed)
    w, h = VHX_SECTION
    x = np.linspace(-w / 2, w / 2, nx)
    y = np.linspace(-h / 2, h / 2, ny)
    X, Y = np.meshgrid(x, y)
    z = 40 * X / 3 - 25 * Y / 2                          # a slight tilt, um
    lf = ndi.gaussian_filter(rng.normal(size=(ny, nx)), 16)
    z += 28 * lf / lf.std()
    seeds = np.ones((ny, nx), np.uint8)
    n = int(nx * ny / 25)
    seeds[rng.integers(0, ny, n), rng.integers(0, nx, n)] = 0
    dist = cv2.distanceTransform(seeds, cv2.DIST_L2, 5)
    z += 16 * (np.minimum(dist, 4.0) / 4.0) ** 2          # dimples: shallow bowls ~0.1 mm
    z += ndi.gaussian_filter(rng.normal(0, 3, (ny, nx)), 0.7)
    de = np.minimum(w / 2 - np.abs(X), h / 2 - np.abs(Y))
    lipw = 0.33 + 0.08 * ndi.gaussian_filter(rng.normal(size=(ny, nx)), 25) / 0.01
    lipw = np.clip(lipw, 0.22, 0.45)
    z += 300 * np.clip(1 - de / lipw, 0, 1)              # the shear lip, ~45 deg
    px, py, pr, pd = VHX_PORE
    rr = np.hypot(X - px, Y - py)
    z -= pd * np.sqrt(np.clip(1 - (rr / pr) ** 2, 0, None))
    z -= z.min()
    return x, y, z


def panel_vhx(path: Path) -> dict:
    from matplotlib import cm as mcm
    from matplotlib.colors import Normalize
    x, y, z = fracture_map()
    w, h = VHX_SECTION
    foot = ("Computed: a 6 x 4 mm gauge section, flat and finely dimpled, a shear lip, one gas pore. As the VHX\n"
            "would build it from a tilt series of the free-angle head (−60 to +90°) and one flip of the bar.")
    plt, fig = _fig("Fracture surface, Keyence VHX 3-D", "ILLUSTRATIVE (COMPUTED)", foot)
    vmax = float(np.percentile(z, 99.5))
    norm = Normalize(0, vmax)
    ax = fig.add_axes((0.03, 0.42, 0.44, 0.46))
    im = ax.imshow(z, extent=(-w / 2, w / 2, -h / 2, h / 2), origin="lower", cmap="turbo", norm=norm,
                   interpolation="bilinear")
    ax.set_axis_off()
    py_ = VHX_PORE[1]
    ax.plot([-w / 2 + 0.05, w / 2 - 0.05], [py_, py_], color="white", lw=2, ls="--")
    for xx, t in ((-w / 2 - 0.05, "A"), (w / 2 + 0.05, "B")):
        ax.text(xx, py_, t, ha="right" if t == "A" else "left", va="center", fontsize=16, fontweight="bold",
                color=INK)
    kw = dict(color="white", fontsize=15, fontweight="bold", path_effects=_stroke(),
              arrowprops=dict(arrowstyle="-|>", color="white", lw=2, mutation_scale=16))
    ax.annotate("shear lip", xy=(-1.0, h / 2 - 0.12), xytext=(-2.3, 0.9), ha="left", va="center", **kw)
    ax.annotate("pore", xy=(VHX_PORE[0] + 0.1, py_ + 0.12), xytext=(1.6, 0.55), ha="left", va="center", **kw)
    ax.set_xlim(-w / 2 - 0.35, w / 2 + 0.35)
    ax.set_ylim(-h / 2, h / 2)
    cax = fig.add_axes((0.485, 0.45, 0.015, 0.40))
    cb = fig.colorbar(im, cax=cax)
    cb.set_label("height (µm)", fontsize=13, color=INK2)
    cb.ax.tick_params(labelsize=12)
    cb.outline.set_visible(False)
    # the 3-D view
    a3 = fig.add_axes((0.57, 0.36, 0.43, 0.56), projection="3d")
    s = 2
    Xg, Yg = np.meshgrid(x[::s], y[::s])
    Zg = z[::s, ::s]
    a3.plot_surface(Xg, Yg, Zg, facecolors=mcm.turbo(norm(Zg)), rstride=1, cstride=1, linewidth=0,
                    antialiased=False, shade=False)
    a3.set_box_aspect((w, h, 1.5))
    a3.view_init(elev=34, azim=-58)
    a3.set_axis_off()
    a3.set_facecolor((0, 0, 0, 0))
    fig.text(0.785, 0.40, "3-D view, height exaggerated", ha="center", va="center", fontsize=13, color=INK2)
    # the profile A-B
    j = int(np.argmin(np.abs(y - py_)))
    pa = fig.add_axes((0.09, 0.165, 0.88, 0.165))
    pa.plot(x - x[0], z[j], color=C1, lw=1.8)
    pa.fill_between(x - x[0], 0, z[j], color=C1, alpha=0.12, lw=0)
    pa.set_xlim(0, w)
    pa.set_ylim(0, max(380.0, float(z[j].max()) * 1.08))
    pa.set_xlabel("along A-B (mm)", fontsize=13, labelpad=1)
    pa.set_ylabel("µm", fontsize=13)
    pa.tick_params(labelsize=12)
    for sp in ("top", "right"):
        pa.spines[sp].set_visible(False)
    pa.text(0.02, 0.98, "A", transform=pa.transAxes, fontsize=14, fontweight="bold", va="top", color=INK)
    pa.text(0.98, 0.98, "B", transform=pa.transAxes, fontsize=14, fontweight="bold", va="top", ha="right", color=INK)
    _save(plt, fig, path)
    return dict(status="illustrative (computed)", instrument="Keyence VHX, free-angle head",
                section_mm=list(VHX_SECTION), height_range_um=[0.0, round(float(z.max()), 1)],
                shear_lip="~0.22-0.45 mm wide, rising ~300 um at the edge", dimples_mm=0.1,
                pore=dict(x_mm=VHX_PORE[0], y_mm=VHX_PORE[1], radius_mm=VHX_PORE[2], depth_um=VHX_PORE[3]),
                reconstruction="a tilt series of the free-angle head (-60 to +90 deg) and one flip of the bar")


# ================================================================================================= the API
BUILD = dict(sem=panel_sem, eds=panel_eds, hv=panel_hv, nano=panel_nano, pip=panel_pip, vhx=panel_vhx)


def build_all() -> dict:
    data = dict(specimen="a coupon of the lab's LPBF AlSi10Mg build, polished; nothing here measured on it yet",
                real_section_image_found=False,
                searched=["vertical-cloud-lab/digital-alloy-lab main tree (figures/sem: powder only)",
                          "byu-vcl vertical-lab/out/, docs/"],
                sources=SRC)
    for k in KEYS:
        data[k] = BUILD[k](PANELS[k])
    tmp = DATA.with_name(f".{DATA.stem}.{os.getpid()}.tmp.json")
    tmp.write_text(json.dumps(data, indent=1, default=float) + "\n")
    os.replace(tmp, DATA)
    return data


@lru_cache(maxsize=None)
def panel(key: str):
    """The panel image (PIL RGB) for key in sem, eds, hv, nano, pip, vhx; its PNG built first if it isn't there."""
    from PIL import Image
    p = PANELS[key]
    if not p.exists():
        BUILD[key](p)
    return Image.open(p).convert("RGB")


if __name__ == "__main__":
    d = build_all()
    for k in KEYS:
        print(k, PANELS[k].name, d[k]["status"])
    print("hv", d["hv"]["mean_HV"], "+-", d["hv"]["sd_HV"], "| nano H", d["nano"]["H_mean_GPa"], "E",
          d["nano"]["E_mean_GPa"], "| pip", d["pip"]["Rp02_MPa"], d["pip"]["UTS_MPa"], d["pip"]["uniform_elongation_pct"])
