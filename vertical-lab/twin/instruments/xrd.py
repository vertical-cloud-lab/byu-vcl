"""X-ray diffraction on a Rigaku MiniFlex (Bragg-Brentano, Cu K-alpha1/alpha2, 2theta 10-100 deg): the pattern a
powder lot or a polished part would give, and the analysis a lab runs on it.

Forward model (each term a standard one; numbers ours are marked "assumed"):

* Reflections of every phase in ``micro.phase_model`` from its structure (``micro.STRUCTURES``): kinematic structure
  factors F = sum_j f_j(s) exp(2 pi i h.r_j) with Cromer-Mann form factors (International Tables for
  Crystallography Vol. C, Table 6.1.1.4; coefficients below for every element of both spaces plus O and C), the
  anomalous terms f', f'' at Cu K-alpha (Sasaki 1989 / Henke et al. 1993, https://henke.lbl.gov/optical_constants/),
  and an isotropic Debye-Waller factor exp(-2 B s^2). Complex cells we do not carry positions for use Wilson
  statistics at the true cell's d-spacings (assumed; see micro.py).
* Intensity per reflection: scale x (w_p / rho_p) x m |F|^2 / V^2 x Lorentz-polarization (1 + cos^2 2theta) /
  (sin^2 theta cos theta) (no monochromator; MiniFlex with K-beta filter), the phase's weight fraction w_p and
  density rho_p (the mass-absorption form of the Rietveld intensity, Hill & Howard, J. Appl. Cryst. 20, 1987).
* Profiles: pseudo-Voigt (Thompson-Cox-Hastings mixing) of the instrument's Caglioti width
  H^2 = U tan^2 theta + V tan theta + W (Caglioti et al., Nucl. Instrum. 3, 1958; U, V, W assumed for a MiniFlex 600
  with D/teX Ultra, FWHM ~0.07 deg at 40 deg) and the sample's Scherrer size (K = 0.9) and microstrain (4 eps tan
  theta) broadening; K-alpha2 at 0.5 of K-alpha1 (lambda 1.540593 / 1.544414 A, Hoelzer et al., Phys. Rev. A 56,
  1997).
* Preferred orientation of parts: March-Dollase, P = (r^2 cos^2 a + sin^2 a / r)^(-3/2) about <100> along the build
  direction, the measured face being the build plane (Dollase, J. Appl. Cryst. 19, 1986); r from the columnar share
  (assumed).
* Sample-displacement shift d2theta = -2 s cos theta / R (R = 150 mm, the MiniFlex goniometer), s ~ N(0, 50 um) for
  a packed powder holder and N(0, 25 um) for a mounted part (assumed), plus a zero error ~ N(0, 0.005 deg).
* Background: a Chebyshev polynomial (air scatter at low angle, Compton, the K-beta filter's edge) plus an amorphous
  hump at 2theta ~ 21 deg from the glass/PMMA powder holder, plus a flat Fe/Mn/Cr fluorescence term under Cu
  radiation (assumed magnitudes). Poisson counts for the dwell time per step.

Analysis (what a lab runs on the pattern): background-subtracted peak search, profile fits of the FCC reflections
(pseudo-Voigt + K-alpha2), lattice parameter by least squares of a_hkl against cos^2 theta / sin theta (the
displacement correction), Williamson-Hall size and strain from the fitted widths minus the instrument's, and a
whole-pattern "Rietveld-lite": non-negative least squares of the pattern against reference patterns of the
candidate phases the chemistry allows (computed from the same structures at handbook lattice parameters, the
matrix at its refined one, with a March-Dollase r refined by grid search for parts) plus the Chebyshev background;
weight fractions from the scales (the ZMV relation), a phase reported only when its scale exceeds 3 standard errors.
Detection limits (~1-3 wt%), overlaps (L1_2 Al3X on Al, kappa on alpha) and the invisibility of nano-precipitates
emerge from the counts, not from a rule.

``solute_ss_wt``: inverse Vegard from a_fcc, assuming the solutes sit in the matrix in the design's proportions. This
is ambiguous for multi-solute alloys (Mg expands Al, Si and Cu contract it, so AlSi10Mg's 2 wt% Si and 0.3 % Mg look
like 2.3 % of "design-proportioned solute"); it is None when the solutes' effects cancel.
"""
from __future__ import annotations

import math
import time
from functools import lru_cache

import numpy as np

from twin.instruments import micro

SPEC = dict(station="xrd", hours=0.5, consumables={"zero_background_holder_use": 1},
            note="Rigaku MiniFlex 600 (assumed in house; no 'xrd' station in twin/facility.py yet): 10-100 deg at "
                 "2 deg/min (full) or 10 deg/min (lite) ~ 0.75 h with loading; parts need a polished face (prep)",
            prep=dict(station="prep", hours=0.5))

LAM1, LAM2, K21 = 1.540593, 1.544414, 0.5
R_GONIO = 150.0                                   # mm
CAGLIOTI = (0.0100, -0.0030, 0.0040)              # deg^2 (assumed, MiniFlex 600 + D/teX Ultra)
TTH = (10.0, 100.0)
FID = {"full": dict(step=0.01, speed=2.0), "lite": dict(step=0.04, speed=10.0)}
PEAK_CPS = 2.0e4                                  # Al(111) peak of pure Al powder, counts/s (assumed)

# Cromer-Mann coefficients a1..a4, b1..b4, c (International Tables Vol. C, Table 6.1.1.4). Er: Gd's coefficients
# scaled to Z = 68 (assumed: f(0) = Z, shape of the neighbouring lanthanide).
CM = {
    "Li": (1.1282, 0.7508, 0.6175, 0.4653, 3.9546, 1.0524, 85.3905, 168.261, 0.0377),
    "C": (2.3100, 1.0200, 1.5886, 0.8650, 20.8439, 10.2075, 0.5687, 51.6512, 0.2156),
    "O": (3.0485, 2.2868, 1.5463, 0.8670, 13.2771, 5.7011, 0.3239, 32.9089, 0.2508),
    "Mg": (5.4204, 2.1735, 1.2269, 2.3073, 2.8275, 79.2611, 0.3808, 7.1937, 0.8584),
    "Al": (6.4202, 1.9002, 1.5936, 1.9646, 3.0387, 0.7426, 31.5472, 85.0886, 1.1151),
    "Si": (6.2915, 3.0353, 1.9891, 1.5410, 2.4386, 32.3337, 0.6785, 81.6937, 1.1407),
    "Sc": (9.1890, 7.3679, 1.6409, 1.4680, 9.0213, 0.5729, 136.108, 51.3531, 1.3329),
    "Ti": (9.7595, 7.3558, 1.6991, 1.9021, 7.8508, 0.5000, 35.6338, 116.105, 1.2807),
    "Cr": (10.6406, 7.3537, 3.3240, 1.4922, 6.1038, 0.3920, 20.2626, 98.7399, 1.1832),
    "Mn": (11.2819, 7.3573, 3.0193, 2.2441, 5.3409, 0.3432, 17.8674, 83.7543, 1.0896),
    "Fe": (11.7695, 7.3573, 3.5222, 2.3045, 4.7611, 0.3072, 15.3535, 76.8805, 1.0369),
    "Ni": (12.8376, 7.2920, 4.4438, 2.3800, 3.8785, 0.2565, 12.1763, 66.3421, 1.0341),
    "Cu": (13.3380, 7.1676, 5.6158, 1.6735, 3.5828, 0.2470, 11.3966, 64.8126, 1.1910),
    "Zn": (14.0743, 7.0318, 5.1652, 2.4100, 3.2655, 0.2333, 10.3163, 58.7097, 1.3041),
    "Zr": (17.8765, 10.9480, 5.41732, 3.65721, 1.27618, 11.9160, 0.117622, 87.6627, 2.06929),
    "Nb": (17.6142, 12.0144, 4.04183, 3.53346, 1.18865, 11.7660, 0.204785, 69.7957, 3.75591),
    "Sn": (19.1889, 19.1005, 4.4585, 2.4663, 5.8303, 0.5031, 26.8909, 83.9571, 4.7821),
    "Ce": (21.1671, 19.7695, 11.8513, 3.33049, 2.81219, 0.226836, 17.6083, 127.113, 1.86264),
    "Er": tuple(v * 68 / 64 for v in (25.0709, 19.0798, 13.8518, 3.54545)) + (2.25341, 0.181951, 12.9331, 101.398)
    + (2.4196 * 68 / 64,),
}
# anomalous scattering at Cu K-alpha, f' and f'' (Sasaki 1989; Henke 1993; approximate)
FP = {"Li": (0.0, 0.0), "C": (0.017, 0.009), "O": (0.047, 0.032), "Mg": (0.165, 0.177), "Al": (0.204, 0.246),
      "Si": (0.244, 0.330), "Sc": (0.252, 1.519), "Ti": (0.219, 1.807), "Cr": (-0.198, 2.443),
      "Mn": (-0.568, 2.808), "Fe": (-1.179, 3.204), "Ni": (-2.956, 0.509), "Cu": (-2.019, 0.589),
      "Zn": (-1.612, 0.678), "Zr": (-0.186, 2.245), "Nb": (-0.248, 2.482), "Sn": (-0.654, 5.794),
      "Ce": (-1.0, 9.0), "Er": (-0.9, 3.8)}


def f0(el, s2):
    c = CM[el]
    return (c[0] * np.exp(-c[4] * s2) + c[1] * np.exp(-c[5] * s2) + c[2] * np.exp(-c[6] * s2)
            + c[3] * np.exp(-c[7] * s2) + c[8])


def fscat(el, s2):
    fp, fpp = FP.get(el, (0.0, 0.0))
    return f0(el, s2) + fp + 1j * fpp


# ------------------------------------------------------------------------------------------------ reflections
def _recip_metric(st, a, b, c):
    sys = st["system"]
    if sys == "hexagonal":
        return lambda h, k, l: 4.0 / 3.0 * (h * h + h * k + k * k) / a ** 2 + l * l / c ** 2
    if sys == "monoclinic":
        be = math.radians(st["beta"])
        sb = math.sin(be)
        return lambda h, k, l: (h * h / a ** 2 + k * k * sb * sb / b ** 2 + l * l / c ** 2
                                - 2 * h * l * math.cos(be) / (a * c)) / (sb * sb)
    return lambda h, k, l: h * h / a ** 2 + k * k / b ** 2 + l * l / c ** 2


def _lattice(st, a=None):
    a0 = st["a"]
    a = a or a0
    sc = a / a0
    if st["system"] == "cubic":
        return a, a, a
    return a, st["b"] * sc, st["c"] * sc


@lru_cache(maxsize=256)
def reflections(name: str, a_key: float | None = None, d_min: float = LAM1 / (2 * math.sin(math.radians(50.5)))):
    """Reflection groups of a structure (grouped by d): d (A), multiplicity, Gram matrices K[g, s, s'] of the site
    geometric factors (so |F|^2 = Re f^H K f for any site occupancy), first hkl, and for Wilson cells the drawn
    |F|^2 / <|F|^2> ratios."""
    st = micro.STRUCTURES[name]
    a, b, c = _lattice(st, a_key)
    g = _recip_metric(st, a, b, c)
    hm, km, lm = int(a / d_min) + 1, int(b / d_min) + 1, int(c / d_min) + 1
    H, K, L = np.meshgrid(np.arange(-hm, hm + 1), np.arange(-km, km + 1), np.arange(-lm, lm + 1), indexing="ij")
    H, K, L = H.ravel(), K.ravel(), L.ravel()
    q2 = g(H.astype(float), K.astype(float), L.astype(float))
    ok = (q2 > 0) & (q2 <= 1.0 / d_min ** 2)
    H, K, L, q2 = H[ok], K[ok], L[ok], q2[ok]
    if st["kind"] == "wilson":
        cen = st.get("centring", "P")
        if cen == "C":
            keep = (H + K) % 2 == 0
        elif cen == "I":
            keep = (H + K + L) % 2 == 0
        elif cen == "F":
            keep = ((H % 2) == (K % 2)) & ((K % 2) == (L % 2))
        else:
            keep = np.ones_like(H, bool)
        H, K, L, q2 = H[keep], K[keep], L[keep], q2[keep]
        d = 1 / np.sqrt(q2)
        key = np.round(d, 4)
        u, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
        r = np.random.default_rng(micro.seed_of(name))
        # Wilson: each independent reflection's |F|^2 / <|F|^2> ~ Exp(1); Friedel pairs and symmetry equivalents
        # share one draw, so a group's sum is Gamma(n_indep) (assumed: ~ half the group's count independent)
        n_ind = np.maximum(cnt / max(_n_equiv(st), 1), 1.0)
        ratio = r.gamma(n_ind, 1.0) / n_ind
        dd = _first(d, inv, len(u))
        hk = np.stack([H, K, L], 1)
        first = _first_rows(hk, inv, len(u))
        return dict(d=dd, mult=cnt.astype(float), ratio=ratio, wilson=True, hkl=first, sites=None)
    sites = list(st["sites"])
    pos = {s: np.array([p for (ss, p) in st["atoms"] if ss == s], float) for s in sites}
    hkl = np.stack([H, K, L], 1).astype(float)
    G = np.stack([np.exp(2j * np.pi * hkl @ pos[s].T).sum(1) for s in sites], 1)     # (n, n_sites)
    tot = np.abs(G).sum(1)
    nz = (np.abs(G).max(1) > 1e-6) & (tot > 1e-6)
    # drop extinct reflections (all sites' factors ~ 0)
    Gm = G[nz]
    d = 1 / np.sqrt(q2[nz])
    key = np.round(d, 5)
    u, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
    ns = len(sites)
    Kg = np.zeros((len(u), ns, ns), complex)
    np.add.at(Kg, inv, Gm[:, :, None] * np.conj(Gm[:, None, :]))
    # a group whose summed |F|^2 is zero for any occupancy is extinct
    keep = np.abs(np.einsum("gii->g", Kg)) > 1e-6
    dd = _first(d, inv, len(u))
    first = _first_rows(np.stack([H[nz], K[nz], L[nz]], 1), inv, len(u))
    return dict(d=dd[keep], mult=cnt[keep].astype(float), K=Kg[keep], wilson=False, hkl=first[keep], sites=sites)


def _n_equiv(st):
    return {"cubic": 48, "hexagonal": 24, "tetragonal": 16, "orthorhombic": 8, "monoclinic": 4}[st["system"]]


def _first(d, inv, n):
    out = np.zeros(n)
    out[inv[::-1]] = d[::-1]
    return out


def _first_rows(hkl, inv, n):
    out = np.zeros((n, 3), int)
    out[inv[::-1]] = hkl[::-1]
    return out


def _site_f(st, phase, s2):
    """Scattering factor of each site (n_sites, n_refl) for the phase's occupancy (matrix: its solid solution)."""
    sites = list(st["sites"])
    F = []
    for s in sites:
        occ = st["sites"][s]
        if phase.get("name") == "fcc":
            occ = micro.wt_to_at({e: v for e, v in phase["comp"].items()})
        tot = sum(occ.values()) or 1.0
        F.append(sum((x / tot) * fscat(e, s2) for e, x in occ.items() if e in CM))
    return np.array(F)


def intensities(phase, a=None, wl=LAM1):
    """(2theta_K-alpha1 deg, I per unit weight fraction before LP and profile, hkl) of one phase's reflection groups."""
    name = phase["name"]
    st = micro.STRUCTURES[name]
    a = a or phase.get("a") or st["a"]
    R = reflections(name, round(float(a), 5) if name == "fcc" else None)
    a0 = st["a"]
    sc = (a / a0) if name != "fcc" else 1.0
    d = R["d"] * (sc if name != "fcc" else 1.0)
    sth = wl / (2 * d)
    ok = sth < math.sin(math.radians(TTH[1] / 2 + 0.5))
    d, sth = d[ok], sth[ok]
    s2 = (sth / wl) ** 2
    B = st.get("B", 0.7)
    if R["wilson"]:
        f2 = np.zeros_like(s2)
        form = micro.structure_formula(st)
        for e, n in form.items():
            f2 += n * np.abs(fscat(e, s2)) ** 2
        F2 = f2 * R["ratio"][ok] * R["mult"][ok]
    else:
        fs = _site_f(st, phase, s2)                                       # (ns, n)
        F2 = np.real(np.einsum("in,nij,jn->n", np.conj(fs), R["K"][ok], fs))
    V = micro.cell_volume(st, a=a, c=(st["c"] * a / a0 if st["system"] != "cubic" else a))
    I = F2 * np.exp(-2 * B * s2) / V ** 2 / phase.get("density", 3.0)
    tth = 2 * np.degrees(np.arcsin(sth))
    return tth, I, R["hkl"][ok]


def lp(tth):
    t = np.radians(tth / 2)
    return (1 + np.cos(2 * t) ** 2) / (np.sin(t) ** 2 * np.cos(t))


def caglioti(tth):
    U, V, W = CAGLIOTI
    t = np.tan(np.radians(tth / 2))
    return np.sqrt(np.maximum(U * t * t + V * t + W, 1e-5))


def sample_widths(tth, cryst_nm, strain, wl=LAM1):
    """Lorentzian (size) and Gaussian (strain) FWHM, deg."""
    th = np.radians(tth / 2)
    hl = np.degrees(0.9 * wl / (cryst_nm * 10.0 * np.cos(th)))
    hg = np.degrees(4 * strain * np.tan(th))
    return hl, hg


def tch(hg, hl):
    """Thompson-Cox-Hastings pseudo-Voigt total FWHM and mixing eta."""
    H = (hg ** 5 + 2.69269 * hg ** 4 * hl + 2.42843 * hg ** 3 * hl ** 2 + 4.47163 * hg ** 2 * hl ** 3
         + 0.07842 * hg * hl ** 4 + hl ** 5) ** 0.2
    q = hl / H
    eta = 1.36603 * q - 0.47719 * q * q + 0.11116 * q ** 3
    return H, np.clip(eta, 0, 1)


def _pv_sum(x, pos, amp, H, eta, cut=10.0):
    """Sum of area-normalised pseudo-Voigts (amp = integrated intensity) on the uniform grid x (vectorized)."""
    y = np.zeros_like(x)
    if len(pos) == 0:
        return y
    pos, amp, H, eta = (np.asarray(v, float) for v in (pos, amp, H, eta))
    dx = x[1] - x[0]
    wp = int(math.ceil(2 * cut * float(H.max()) / dx)) + 2
    i0 = np.floor((pos - cut * H - x[0]) / dx).astype(int)
    I = i0[:, None] + np.arange(wp)[None, :]
    ok = (I >= 0) & (I < len(x))
    u = (x[0] + I * dx - pos[:, None]) / H[:, None]
    u2 = u * u
    prof = amp[:, None] / H[:, None] * (eta[:, None] * 0.6366198 / (1 + 4 * u2)
                                        + (1 - eta[:, None]) * 0.9394373 * np.exp(-2.7725887 * u2))
    return np.bincount(I[ok], prof[ok], minlength=len(x))[:len(x)]


def phase_pattern(x, phase, a=None, cryst=None, strain=None, r_md=1.0, shift=None):
    """Pattern (counts-per-second scale, no background) of one phase at weight fraction 1."""
    tth, I, hkl = intensities(phase, a=a)
    if len(tth) == 0:
        return np.zeros_like(x)
    cryst = cryst or phase.get("cryst_nm", 200.0)
    strain = phase.get("strain", 5e-4) if strain is None else strain
    I = I * lp(tth)
    if r_md != 1.0 and phase["name"] == "fcc":
        I = I * march_dollase(hkl, r_md)
    if len(I) > 40:                                   # drop reflections below 0.2 % of the phase's strongest
        k = I > 2e-3 * I.max()
        tth, I, hkl = tth[k], I[k], hkl[k]
    out = np.zeros_like(x)
    for wl, k in ((LAM1, 1.0), (LAM2, K21)):
        t = tth if wl == LAM1 else 2 * np.degrees(np.arcsin(np.clip(np.sin(np.radians(tth / 2)) * LAM2 / LAM1, 0, 1)))
        if shift is not None:
            t = t + shift(t)
        hl, hg = sample_widths(t, cryst, strain, wl)
        hi = caglioti(t)
        H, eta = tch(np.sqrt(hi ** 2 + hg ** 2), hl)
        eta = np.clip(eta + 0.35 * (1 - eta) * hi / H, 0, 1)            # the instrument's own Lorentzian share
        out += _pv_sum(x, t, k * I, H, eta)
    return out


_PAT_CACHE: dict = {}


def cached_pattern(x, phase, shift=None):
    """A non-matrix phase's unit pattern on grid x, cached by (phase, size, strain, grid), then shifted by
    interpolation (the displacement shift varies by less than a profile width over the window)."""
    key = (phase["name"], round(float(phase.get("cryst_nm", 200.0)), 0), round(float(phase.get("strain", 5e-4)), 5),
           round(float(phase.get("a", 0) or 0), 4), len(x), round(float(x[0]), 3), round(float(x[1] - x[0]), 4))
    y = _PAT_CACHE.get(key)
    if y is None:
        if len(_PAT_CACHE) > 600:
            _PAT_CACHE.clear()
        y = phase_pattern(x, phase)
        _PAT_CACHE[key] = y
    if shift is None:
        return y
    return np.interp(x - shift(x), x, y, left=0.0, right=0.0)


def march_dollase(hkl, r):
    """March-Dollase factor for a <100> fiber normal to the measured face (cubic), averaged over the three <100>."""
    h = np.abs(np.asarray(hkl, float))
    n = np.linalg.norm(h, axis=1)
    n[n == 0] = 1
    P = np.zeros(len(h))
    for j in range(3):
        ca = h[:, j] / n
        P += (r * r * ca * ca + (1 - ca * ca) / r) ** -1.5
    return P / 3


# ------------------------------------------------------------------------------------------------ simulation
def _r_md(pm):
    g = pm.get("grains")
    if not g:
        return 1.0
    return float(1.0 - 0.35 * (1 - g["equiaxed_frac"]))               # assumed: columnar <100> fiber -> r ~ 0.65


def _mu_mass(comp_wt):
    MU = {"Li": 0.5, "C": 4.6, "O": 11.0, "Mg": 38.6, "Al": 50.2, "Si": 63.7, "Sc": 184.0, "Ti": 202.0, "Cr": 252.0,
          "Mn": 272.0, "Fe": 304.0, "Ni": 45.7, "Cu": 52.9, "Zn": 59.5, "Zr": 136.0, "Nb": 145.0, "Sn": 256.0,
          "Ce": 352.0, "Er": 134.0}
    tot = sum(comp_wt.values()) or 1
    return sum(MU.get(e, 50.0) * w / tot for e, w in comp_wt.items())


def simulate(sample, campaign, rng, fidelity="lite", kind=None):
    kind = kind or micro.kind_of(sample)
    pm = micro.phase_model(sample, campaign, kind)
    f = FID["full" if fidelity == "full" else "lite"]
    x = np.arange(TTH[0], TTH[1] + 1e-9, f["step"])
    dwell = f["step"] / f["speed"] * 60.0                            # s per step
    disp = rng.normal(0, 0.050 if kind == "powder" else 0.025)       # mm
    zero = rng.normal(0, 0.005)
    shift = lambda t: zero + np.degrees(-2 * disp * np.cos(np.radians(t / 2)) / R_GONIO)
    r_md = _r_md(pm) if kind == "part" else 1.0
    # intensity scale: absolute through 1/mu* (mixture), normalised to pure Al powder's (111) peak at PEAK_CPS
    mu = _mu_mass(pm["composition"])
    y = np.zeros_like(x)
    ck = micro.seed_of(repr(sorted((k, round(v, 2)) for k, v in pm["composition"].items())))
    for p in pm["phases"]:
        if p["name"] == "fcc":
            y += p["wt"] * phase_pattern(x, p, r_md=r_md, shift=shift)
        else:
            # a real intermetallic's cell differs from the handbook's by its own solutes and strain: +-0.1 %
            # (assumed), fixed per sample, which the Rietveld-lite (handbook cells) does not refine
            dl = 1e-3 * np.random.default_rng(ck + micro.seed_of(p["name"])).normal()
            y += p["wt"] * cached_pattern(x, dict(p, a=round(p["a"] * (1 + dl), 4)), shift=shift)
    scale = PEAK_CPS / _al_ref_peak() * (50.2 / mu)
    y *= scale
    # background: Chebyshev (air scatter falling with angle, flat Compton), holder hump (powders), fluorescence
    u = (x - 55.0) / 45.0
    fe = sum(pm["composition"].get(e, 0.0) for e in ("Fe", "Mn", "Cr")) / 100.0
    # (assumed magnitudes: peak-to-background ~100 on Al(111), as typical MiniFlex scans of metal powders)
    bg = 250.0 * np.exp(-(x - 10) / 12.0) + 130.0 + 25.0 * u + 15.0 * (2 * u * u - 1)
    bg += 2500.0 * fe
    if kind == "powder":
        bg += 300.0 * np.exp(-0.5 * ((x - 21.5) / 4.5) ** 2)
    lam = (y + bg) * dwell
    counts = rng.poisson(np.maximum(lam, 0)).astype(float)
    return dict(x=x, counts=counts, dwell=dwell, truth_bg=bg * dwell, truth_y=y * dwell, pm=pm, disp_mm=disp,
                zero_deg=zero, r_md=r_md, kind=kind)


@lru_cache(maxsize=1)
def _al_ref_peak():
    ph = dict(name="fcc", comp={"Al": 1.0}, a=4.0496, cryst_nm=1000.0, strain=0.0, density=2.70)
    x = np.arange(37.5, 39.5, 0.005)
    return float(phase_pattern(x, ph).max())


# ------------------------------------------------------------------------------------------------ analysis
def _cheb(x, n=6):
    u = (x - x.mean()) / (0.5 * (x.max() - x.min()))
    T = [np.ones_like(u), u]
    for _ in range(2, n):
        T.append(2 * u * T[-1] - T[-2])
    return np.stack(T[:n], 1)


def _nnls_bg(A_free, A_pos, y, w):
    """min || sqrt(w) (y - A_free c - A_pos x) ||, x >= 0, via the normal equations (fast) and BVLS on the
    Cholesky factor. Returns c, x, cov(x), chi2_red."""
    from scipy.optimize import lsq_linear
    A = np.hstack([A_free, A_pos]) if A_pos.shape[1] else A_free
    Aw = A * w[:, None]
    G = A.T @ Aw
    h = Aw.T @ y
    n_f = A_free.shape[1]
    sc = np.sqrt(np.maximum(np.diag(G), 1e-30))
    Gs = G / np.outer(sc, sc) + 1e-12 * np.eye(len(G))
    hs = h / sc
    try:
        Lc = np.linalg.cholesky(Gs)
    except np.linalg.LinAlgError:
        Gs += 1e-8 * np.eye(len(G))
        Lc = np.linalg.cholesky(Gs)
    rhs = np.linalg.solve(Lc, hs)
    lb = np.r_[np.full(n_f, -np.inf), np.zeros(A.shape[1] - n_f)]
    res = lsq_linear(Lc.T, rhs, bounds=(lb, np.full(A.shape[1], np.inf)), method="bvls")
    z = res.x / sc
    r = y - A @ z
    dof = max(len(y) - A.shape[1], 1)
    chi2 = float((r * r * w).sum() / dof)
    try:
        cov = np.linalg.inv(G) * chi2
    except np.linalg.LinAlgError:
        cov = np.diag(1 / np.maximum(np.diag(G), 1e-30)) * chi2
    return z[:n_f], z[n_f:], cov[n_f:, n_f:], chi2, r


def _fit_peak(x, y, w, x0, h0):
    """Pseudo-Voigt + K-alpha2 + linear background on a window; Gauss-Newton with numerical Jacobian. Returns
    (position K-alpha1, FWHM, area, ok)."""
    sel = (x > x0 - 6 * h0) & (x < x0 + 6 * h0 + 0.4)
    xs, ys, ws = x[sel], y[sel], w[sel]
    if len(xs) < 6:
        return x0, h0, 0.0, False

    def model(p):
        pos, H, A, b0, b1 = p
        d2 = 2 * np.degrees(np.arcsin(min(np.sin(np.radians(pos / 2)) * LAM2 / LAM1, 1.0))) - pos
        out = b0 + b1 * (xs - x0)
        for c, k in ((pos, 1.0), (pos + d2, K21)):
            u = (xs - c) / H
            out = out + A * k * (0.5 * 0.6366198 / H / (1 + 4 * u * u) + 0.5 * 0.9394373 / H * np.exp(-2.7725887 * u * u))
        return out
    A0 = max((ys.max() - np.median(ys)) * h0, 1.0)
    p = np.array([x0, h0, A0, float(np.median(ys[:3])), 0.0])
    lam = 1e-3
    for _ in range(8):
        m = model(p)
        r = (ys - m) * np.sqrt(ws)
        J = np.empty((len(xs), 5))
        for j, dp in enumerate((1e-4, 1e-4, 1e-3 * abs(p[2]) + 1e-6, 1e-3 * abs(p[3]) + 1e-6, 1e-3)):
            q = p.copy()
            q[j] += dp
            J[:, j] = (model(q) - m) / dp * np.sqrt(ws)
        JTJ = J.T @ J
        step = np.linalg.solve(JTJ + lam * np.diag(np.diag(JTJ) + 1e-12), J.T @ r)
        p_new = p + step
        p_new[1] = np.clip(p_new[1], 0.02, 2.0)
        if np.sum(((ys - model(p_new)) * np.sqrt(ws)) ** 2) < np.sum(r * r):
            p, lam = p_new, lam * 0.3
        else:
            lam *= 10
        if abs(step[0]) < 2e-4 and abs(step[1]) < 2e-4:
            break
    ok = p[2] > 0 and abs(p[0] - x0) < 3 * h0
    return float(p[0]), float(p[1]), float(p[2]), bool(ok)


def candidates(campaign, design, kind):
    """The phases an analyst would try, from the design's chemistry."""
    els = {e for e, v in (design or {}).items() if v and v > 0.04}
    if campaign == "flaime_al":
        c = []
        rules = [("Si", ["Si"]), ("Cu", ["Al2Cu"]), ("Mn", ["Al6(Mn,Fe)"]), ("Fe", ["Al13Fe4"]), ("Cr", ["Al45Cr7"]),
                 ("Ni", ["Al3Ni"]), ("Ce", ["Al11Ce3"]), ("Ti", ["Al3Ti"]), ("Er", ["Al3Er"]), ("Sn", ["Sn"]),
                 ("Li", ["AlLi", "Al3Li"])]
        for e, ps in rules:
            if e in els:
                c += ps
        if "Mg" in els and "Si" in els:
            c.append("Mg2Si")
        if "Mg" in els and "Zn" in els:
            c.append("MgZn2")
        if "Sc" in els and "Zr" in els:
            c.append("Al3(Sc,Zr)")
        elif "Sc" in els:
            c.append("Al3Sc")
        elif "Zr" in els:
            c += ["Al3Zr_L12", "Al3Zr_D023"] if kind == "powder" else ["Al3Zr_L12"]
        return c
    c = []
    if "Al" in els and (design or {}).get("Al", 0) > 4:
        c += ["beta'", "kappa_II", "kappa_III"]
    if "Si" in els and "Ni" in els:
        c.append("Ni2Si")
    if "Nb" in els:
        c.append("Ni3Nb")
    if "Ti" in els and "Ni" in els:
        c.append("Ni3Ti")
    if "Cr" in els:
        c.append("Cr")
    if "Fe" in els and (design or {}).get("Al", 0) <= 4 and (design or {}).get("Fe", 0) > 1.5:
        c.append("Fe_bcc")
    return c


def _ref_phase(name, base):
    st = micro.STRUCTURES[name]
    comp = micro.stoich_wt(micro.PHASE_COMP[name]) if name in micro.PHASE_COMP else {base: 1.0}
    return dict(name=name, comp=comp, a=st["a"], b=st["b"], c=st["c"], cryst_nm=60.0 if name != "beta'" else 40.0,
                strain=1e-3 if name != "beta'" else 2e-3, density=micro.structure_density(st))


def analyze(x, counts, campaign, kind, design=None, dwell=1.0):
    """The lab's analysis of a pattern. Returns the instrument's outputs and the fit for figures."""
    base = micro.base_of(campaign)
    y = counts / dwell                                               # cps
    w = dwell / np.maximum(counts, 1.0)                              # 1 / var(cps)
    B = _cheb(x, 6)
    hump = np.exp(-0.5 * ((x - 21.5) / 4.5) ** 2)[:, None]
    Bf = np.hstack([B, hump]) if kind == "powder" else B
    # 1. background-only robust fit (iteratively clipped) for the peak search
    c, _, _, _, _ = _nnls_bg(Bf, np.zeros((len(x), 0)), y, w)
    bgy = Bf @ c
    for _ in range(3):
        keep = (y - bgy) < 2.5 * np.sqrt(np.maximum(bgy, 1) / dwell)
        c, _, _, _, _ = _nnls_bg(Bf[keep], np.zeros((keep.sum(), 0)), y[keep], w[keep])
        bgy = Bf @ c
    net = y - bgy
    sig = np.sqrt(np.maximum(y, 1) / dwell)
    # 2. FCC peaks: the analyst predicts them from the design (Vegard, all solute in solution), indexes the nearest
    #    significant peak within 0.6 deg, lowest angle first, updating the estimate as peaks are fitted
    from scipy.signal import find_peaks
    sm = np.convolve(net, np.ones(3) / 3, mode="same")
    cand_i, _ = find_peaks(sm, prominence=5 * np.median(sig) / math.sqrt(3))
    cand_i = cand_i[sm[cand_i] > 5 * sig[cand_i]]
    a_est = micro.vegard_a(base, {e: v for e, v in (design or {}).items() if e in micro.VEGARD[base] and v > 0})
    fam = [(1, 1, 1), (2, 0, 0), (2, 2, 0), (3, 1, 1), (2, 2, 2), (4, 0, 0), (3, 3, 1), (4, 2, 0)]
    pk = []
    for hkl in fam:
        n2 = sum(i * i for i in hkl)
        s_ = LAM1 * math.sqrt(n2) / (2 * a_est)
        if s_ >= math.sin(math.radians(TTH[1] / 2 - 0.3)) or len(cand_i) == 0:
            continue
        t0 = 2 * math.degrees(math.asin(s_))
        dist = np.abs(x[cand_i] - t0)
        j = int(np.argmin(dist))
        if dist[j] > (0.6 if not pk else 0.35):
            continue
        xj = float(x[cand_i[j]])
        h0 = float(caglioti(np.array([xj]))[0]) * 1.3
        pos, H, A, ok = _fit_peak(x, y, w, xj, h0)
        if ok:
            pk.append((hkl, pos, H, A))
            ah = [LAM1 / (2 * math.sin(math.radians(p[1] / 2))) * math.sqrt(sum(i * i for i in p[0])) for p in pk]
            a_est = float(np.median(ah))
    a_fcc = None
    disp_fit = 0.0
    if len(pk) >= 2:
        th = np.radians(np.array([p[1] for p in pk]) / 2)
        ahkl = np.array([LAM1 / (2 * math.sin(t)) * math.sqrt(sum(i * i for i in p[0])) for t, p in zip(th, pk)])
        f = np.cos(th) ** 2 / np.sin(th)
        if len(pk) >= 3:
            X = np.stack([np.ones_like(f), f], 1)
            coef = np.linalg.solve(X.T @ X, X.T @ ahkl)
            a_fcc, disp_fit = float(coef[0]), float(coef[1])
        else:
            a_fcc = float(np.mean(ahkl))
    elif len(pk) == 1:
        p = pk[0]
        a_fcc = LAM1 / (2 * math.sin(math.radians(p[1] / 2))) * math.sqrt(sum(i * i for i in p[0]))
    # 3. Williamson-Hall on the fitted widths minus the instrument's
    cryst, strain = None, None
    if len(pk) >= 3:
        tt = np.array([p[1] for p in pk])
        Hm = np.array([p[2] for p in pk])
        Hi = caglioti(tt)
        beta = np.radians(np.sqrt(np.maximum(Hm ** 2 - Hi ** 2, 0.0)))   # sample FWHM, rad (quadratic deconvolution)
        th = np.radians(tt / 2)
        X = np.stack([np.ones_like(th), 4 * np.sin(th)], 1)
        coef = np.linalg.solve(X.T @ X, X.T @ (beta * np.cos(th)))
        inter, slope = float(coef[0]), float(coef[1])
        strain = max(slope, 0.0)
        cryst = 0.9 * LAM1 / inter / 10.0 if inter > 1e-5 else 1000.0     # nm
        cryst = float(min(cryst, 1000.0))
    # 4. Rietveld-lite: whole-pattern NNLS against the candidates (+ the matrix at the refined a, W-H broadening)
    cand = candidates(campaign, design, kind)
    a_use = a_fcc or micro.A0[base]
    mat = dict(name="fcc", comp=_matrix_guess(base, design), a=a_use, cryst_nm=min(cryst or 300.0, 600.0),
               strain=strain if strain is not None else 5e-4, density=micro._phase_density("fcc", _matrix_guess(base, design), a_use))
    disp_shift = _disp_shift(disp_fit, a_use)
    best = None
    r_grid = [1.0] if kind == "powder" else [0.55, 0.7, 0.85, 1.0, 1.15]
    refs = []
    for nm in cand:
        refs.append(cached_pattern(x, _ref_phase(nm, base), shift=disp_shift))
    R = np.stack(refs, 1) if refs else np.zeros((len(x), 0))
    for r in r_grid:
        m = phase_pattern(x, mat, r_md=r, shift=disp_shift)[:, None]
        cc, xs, cov, chi2, res = _nnls_bg(Bf, np.hstack([m, R]), y, w)
        if best is None or chi2 < best[3]:
            best = (cc, xs, cov, chi2, res, r, m)
    cc, xs, cov, chi2, res, r_fit, m = best
    se = np.sqrt(np.maximum(np.diag(cov), 0))
    names = ["fcc"] + cand
    dens = [mat["density"]] + [_ref_phase(nm, base)["density"] for nm in cand]
    det = [i for i in range(len(names)) if xs[i] > 3 * se[i] and xs[i] > 0]
    if 0 not in det and xs[0] > 0:
        det = [0] + det
    # weight fractions: the patterns are per unit weight fraction already (1/rho folded in), so w ~ scale
    wsum = sum(xs[i] for i in det) or 1.0
    phases = {("FCC-" + base if names[i] == "fcc" else names[i]): float(xs[i] / wsum) for i in det}
    fit = dict(model=Bf @ cc + np.hstack([m, R]) @ xs, bg=Bf @ cc, comps={names[i]: (np.hstack([m, R])[:, i] * xs[i])
               for i in range(len(names)) if xs[i] > 0}, peaks=pk, r_md=r_fit, chi2=chi2, se=dict(zip(names, se)),
               scale=dict(zip(names, xs)))
    return dict(phases=phases, a_fcc_A=a_fcc, crystallite_nm=cryst, microstrain=strain, fit=fit)


def _disp_shift(slope, a):
    """2theta shift implied by the fitted a_hkl(cos^2/sin) slope: a_hkl = a (1 + (s/R) cos^2 th / sin th)."""
    s_over_R = slope / a if a else 0.0
    return lambda t: np.degrees(-2 * s_over_R * np.cos(np.radians(t / 2)))


def _matrix_guess(base, design):
    """The analyst's matrix composition for the reference pattern: the design (form factors barely care)."""
    d = {e: v for e, v in (design or {}).items() if v > 0 and e in micro.ATOM}
    d[base] = 100 - sum(d.values())
    return {e: v / 100 for e, v in d.items()}


def solute_from_a(a, campaign, design):
    """Inverse Vegard with the solutes in the design's proportions (ambiguous for multi-solute alloys; None when the
    solutes' effects cancel)."""
    if a is None:
        return None
    base = micro.base_of(campaign)
    d = {e: v for e, v in (design or {}).items() if v > 0 and e in micro.VEGARD[base]}
    if not d:
        return None
    tot = sum(d.values())
    prop = {e: v / tot for e, v in d.items()}
    da = micro.vegard_a(base, {e: p * 1.0 for e, p in prop.items()}) - micro.A0[base]   # per 1 wt% total solute
    if abs(da) < 4e-4:
        return None
    lo, hi = 0.0, 60.0 if base == "Cu" else 25.0
    f = lambda S: micro.vegard_a(base, {e: p * S for e, p in prop.items()}) - a
    if f(lo) * f(hi) > 0:
        return 0.0 if abs(f(lo)) < abs(f(hi)) else hi
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return float(0.5 * (lo + hi))


def _design(sample, campaign):
    d = sample.get("design")
    if d:
        return d
    base = micro.base_of(campaign)
    return {e: round(v, 1) for e, v in sample["composition"].items() if e != base}   # a nominal stand-in (assumed)


# ------------------------------------------------------------------------------------------------ entry points
def _lite_or_full(sample, campaign, rng, fidelity, kind, with_truth=False):
    sim = simulate(sample, campaign, rng, fidelity, kind)
    design = _design(sample, campaign)
    an = analyze(sim["x"], sim["counts"], campaign, kind, design, sim["dwell"])
    out = dict(phases=an["phases"], a_fcc_A=an["a_fcc_A"])
    if kind == "powder":
        out["solute_ss_wt"] = solute_from_a(an["a_fcc_A"], campaign, design)
        out["crystallite_nm"] = an["crystallite_nm"]
    else:
        out["microstrain"] = an["microstrain"]
        if campaign == "onr_cu":
            out["beta_prime_frac"] = float(an["phases"].get("beta'", 0.0))
    if fidelity == "full":
        out["raw"] = dict(two_theta=sim["x"], counts=sim["counts"], dwell_s=sim["dwell"], fit=an["fit"],
                          crystallite_nm=an["crystallite_nm"], microstrain=an["microstrain"])
        if with_truth:                           # the latent phases and instrument state: figures only
            out["raw"].update(true_phases={p["name"]: p["wt"] for p in sim["pm"]["phases"]},
                              true_a=sim["pm"]["matrix"]["a_A"], disp_mm=sim["disp_mm"], r_md=sim["r_md"])
    return out


def _true_state(sample, campaign, kind):
    pm = micro.phase_model(sample, campaign, kind)
    m = pm["phases"][0]
    return pm, m


def _fast(sample, campaign, rng, kind):
    """Errors sampled from the calibrated model (calib_micro.json 'xrd_powder' / 'xrd_part')."""
    key = "xrd_powder" if kind == "powder" else "xrd_part"
    P = micro.calib(key) or {}
    pm, m = _true_state(sample, campaign, kind)
    base = pm["base"]
    cb = P.get(base, {}) if P else {}
    design = _design(sample, campaign)
    a_b, a_s = cb.get("a_bias", 0.0) + cb.get("a_bias_beta", 0.0) * pm.get("beta_prime", 0.0), cb.get("a_sd", 3e-4)
    a = m["a"] + a_b + rng.normal(0, a_s)
    if rng.random() < cb.get("a_out", 0.0):                    # a misindexed peak (overlap) now and then
        a += rng.normal(0, cb.get("a_out_sd", 0.0))
    det = {}
    phc = cb.get("phase", {})
    cand = set(candidates(campaign, design, kind))
    for p in pm["phases"][1:]:
        nm = p["name"]
        if nm not in cand:
            continue
        q = phc.get(nm, phc.get("_default", dict(l50=-1.7, s=0.25, rb=-0.1, rs=0.3)))
        lw = math.log10(max(p["wt"], 1e-6))
        pd = 1 / (1 + math.exp(-(lw - q["l50"]) / max(q["s"], 0.05)))
        if rng.random() < pd:
            det[nm] = det.get(nm, 0.0) + p["wt"] * math.exp(q["rb"] + rng.normal(0, q["rs"]))
    fp = cb.get("false_pos", {})
    for nm in cand:
        if nm not in det and nm in fp and rng.random() < fp[nm]["p"]:
            det[nm] = fp[nm]["w"] * math.exp(rng.normal(0, 0.4))
    bpf = None
    if kind == "part" and campaign == "onr_cu":
        bp = pm["beta_prime"]
        bq = cb.get("beta", dict(b0=0.0, b1=1.0, s0=0.01, s1=0.05))
        # the persistent per-sample offset is seeded by the sample's composition and beta' (the same every time
        # this sample is measured); the per-measurement part comes from rng
        z_s = np.random.default_rng(micro.seed_of(repr((sorted((k, round(v_, 3)) for k, v_ in pm["composition"].items()),
                                                         round(bp, 4))))).normal()
        v = bq["b0"] + bq["b1"] * bp + bq.get("b2", 0.0) * bp * pm.get("kappa", 0.0) \
            + bq.get("between_per_bp", 0.0) * bp * z_s + rng.normal(0, bq["s0"] + bq["s1"] * bp)
        bpf = float(np.clip(v, 0.0, 1.0)) if (bp > 0.002 or v > 0.02) else 0.0
        det.pop("beta'", None)
        if bpf > 0:
            det["beta'"] = bpf                     # the same number as beta_prime_frac, as in the lite chain
    phases = {"FCC-" + base: max(1.0 - sum(det.values()), 0.0)}
    phases.update(det)
    s = sum(phases.values()) or 1.0
    phases = {k: v / s for k, v in phases.items()}
    out = dict(phases=phases, a_fcc_A=float(a))
    if kind == "powder":
        out["solute_ss_wt"] = solute_from_a(a, campaign, design)
        cr = cb.get("cryst", dict(b=0.0, s=0.25, cap=1000.0))
        c_true = m["cryst_nm"]
        bp = pm.get("beta_prime", 0.0)
        pcap = cr.get("pcap_hi", 0.0) if bp > 0.2 else cr.get("pcap_lo", 0.0)
        if rng.random() < pcap:
            c = cr.get("cap", 1000.0)
        else:
            c = c_true * math.exp(cr["b"] + cr.get("b1", 0.0) * math.log(c_true / 300.0) + rng.normal(0, cr["s"]))
        out["crystallite_nm"] = float(min(c, cr.get("cap", 1000.0)))
    else:
        st = cb.get("strain", dict(b=0.0, s=0.3, floor=1e-4, p0=0.05))
        e = m["strain"] * math.exp(st["b"] + rng.normal(0, st["s"]))
        out["microstrain"] = float(0.0 if rng.random() < st.get("p0", 0.0) else e)
        if campaign == "onr_cu":
            out["beta_prime_frac"] = float(phases.get("beta'", 0.0))
    return out


def measure_powder(sample, campaign, rng, fidelity="fast", **kw):
    if fidelity == "fast":
        return _fast(sample, campaign, rng, "powder")
    return _lite_or_full(sample, campaign, rng, fidelity, "powder", bool(kw.get("with_truth")))


def measure_part(sample, campaign, rng, fidelity="fast", **kw):
    if fidelity == "fast":
        return _fast(sample, campaign, rng, "part")
    return _lite_or_full(sample, campaign, rng, fidelity, "part", bool(kw.get("with_truth")))


# ------------------------------------------------------------------------------------------------ calibration
def calibrate(n=24, reps=3, seed=0, verbose=True):
    """Fit the fast mode on the lite chain: lattice-parameter bias and spread, per-phase detection curves (logistic in
    log10 wt) with the relative bias and spread of detected fractions, crystallite and strain ratios, and the
    beta' line, over random designs and the gallery alloys, both campaigns."""
    rng = np.random.default_rng(seed)
    out = {"xrd_powder": {}, "xrd_part": {}}
    for camp in ("flaime_al", "onr_cu"):
        base = micro.base_of(camp)
        smp = micro.random_samples(camp, n, seed=seed)
        smp += list(micro.gallery_samples()[camp].values())
        for kind, key in (("powder", "xrd_powder"), ("part", "xrd_part")):
            da, ph_rows, cr_rows, st_rows, bp_rows, fps = [], {}, [], [], [], {}
            ncand = {}
            for i_s, (lot, part) in enumerate(smp):
                s = lot if kind == "powder" else part
                pm = micro.phase_model(s, camp, kind)
                m = pm["phases"][0]
                design = _design(s, camp)
                cand = candidates(camp, design, kind)
                true = {}
                for p in pm["phases"][1:]:
                    true[p["name"]] = true.get(p["name"], 0.0) + p["wt"]
                for _ in range(reps):
                    r = (measure_powder if kind == "powder" else measure_part)(s, camp, rng, fidelity="lite")
                    if r["a_fcc_A"] is not None:
                        da.append((r["a_fcc_A"] - m["a"], pm.get("beta_prime", 0.0)))
                    for nm in cand:
                        ncand[nm] = ncand.get(nm, 0) + 1
                        wt = true.get(nm, 0.0)
                        got = r["phases"].get(nm)
                        if wt > 1e-5:
                            ph_rows.setdefault(nm, []).append((math.log10(wt), got is not None,
                                                               math.log(got / wt) if got else None))
                        elif got:
                            fps.setdefault(nm, []).append(got)
                    if kind == "powder" and r.get("crystallite_nm"):
                        cr_rows.append((m["cryst_nm"], r["crystallite_nm"], pm.get("beta_prime", 0.0)))
                    if kind == "part" and r.get("microstrain") is not None:
                        st_rows.append((m["strain"], r["microstrain"]))
                    if kind == "part" and camp == "onr_cu":
                        bp_rows.append((pm["beta_prime"], r["beta_prime_frac"], pm.get("kappa", 0.0), float(i_s)))
            da = np.array(da).reshape(-1, 2)
            # robust line in beta' (a beta'-rich Cu powder pulls the alpha peaks: overlap), constant for Al
            X = np.stack([np.ones(len(da)), da[:, 1]], 1)
            coef = np.linalg.lstsq(X, da[:, 0], rcond=None)[0] if len(da) > 3 else np.zeros(2)
            for _ in range(3):
                res = da[:, 0] - X @ coef
                mad = 1.4826 * np.median(np.abs(res)) + 1e-7
                wgt = 1 / np.maximum(1, np.abs(res) / (2.5 * mad))
                coef = np.linalg.lstsq(X * wgt[:, None], da[:, 0] * wgt, rcond=None)[0]
            res = da[:, 0] - X @ coef
            P = dict(a_bias=float(coef[0]), a_bias_beta=float(coef[1]),
                     a_sd=float(1.4826 * np.median(np.abs(res))) if len(da) else 3e-4,
                     a_out=float(np.mean(np.abs(res) > 4 * (1.4826 * np.median(np.abs(res)) + 1e-7))),
                     a_out_sd=float(np.std(res[np.abs(res) > 4 * (1.4826 * np.median(np.abs(res)) + 1e-7)]))
                     if np.any(np.abs(res) > 4 * (1.4826 * np.median(np.abs(res)) + 1e-7)) else 0.0,
                     n=len(da), phase={}, false_pos={})
            allrows = []
            for nm, rows in ph_rows.items():
                P["phase"][nm] = _fit_detect(rows)
                allrows += rows
            if allrows:
                P["phase"]["_default"] = _fit_detect(allrows)
            for nm, got in fps.items():
                P["false_pos"][nm] = dict(p=len(got) / max(ncand.get(nm, 1), 1), w=float(np.median(got)))
            if cr_rows:
                c = np.array(cr_rows)
                capped = c[:, 1] >= 999.0
                hi = c[:, 2] > 0.2
                unc = ~capped
                lr = np.log(c[unc, 1] / c[unc, 0])
                X = np.stack([np.ones(unc.sum()), np.log(c[unc, 0] / 300.0)], 1)
                coef = np.linalg.lstsq(X, lr, rcond=None)[0] if unc.sum() > 3 else np.zeros(2)
                res = lr - X @ coef
                P["cryst"] = dict(b=float(coef[0]), b1=float(coef[1]), s=float(np.std(res)) if len(res) > 2 else 0.3,
                                  cap=1000.0, pcap_hi=float(capped[hi].mean()) if hi.any() else 0.0,
                                  pcap_lo=float(capped[~hi].mean()) if (~hi).any() else 0.0)
            if st_rows:
                s_ = np.array(st_rows)
                pos = s_[:, 1] > 0
                lr = np.log(s_[pos, 1] / s_[pos, 0]) if pos.any() else np.array([0.0])
                P["strain"] = dict(b=float(np.mean(lr)), s=float(np.std(lr)), p0=float(1 - pos.mean()))
            if bp_rows:
                b = np.array(bp_rows)
                # beta' read against the true beta' (and a kappa interaction: kappa lines overlap beta'); the
                # residual splits into a persistent per-sample part (overlaps, texture: the same every time that
                # sample is measured) and a per-measurement part (counting, displacement), both growing with beta'
                X = np.stack([np.ones(len(b)), b[:, 0], b[:, 0] * b[:, 2]], 1)
                coef = np.linalg.lstsq(X, b[:, 1], rcond=None)[0]
                res = b[:, 1] - X @ coef
                ids = b[:, 3].astype(int)
                mean_r = np.array([res[ids == k].mean() for k in np.unique(ids)])
                bp_s = np.array([b[ids == k, 0].mean() for k in np.unique(ids)])
                within = res - np.array([res[ids == k].mean() for k in ids])
                n_rep = max(len(res) / max(len(mean_r), 1), 1.0)
                w_sd = float(np.sqrt(np.sum(within ** 2) / max(len(res) - len(mean_r), 1)))
                hi = bp_s > 0.05
                b_sd = float(np.sqrt(max(np.mean(mean_r[hi] ** 2) - w_sd ** 2 / n_rep, 0.0))) if hi.any() else 0.0
                bp_hi = float(np.mean(bp_s[hi])) if hi.any() else 0.3
                P["beta"] = dict(b0=float(coef[0]), b1=float(coef[1]), b2=float(coef[2]), s0=0.003,
                                 s1=float(w_sd / max(float(np.mean(b[b[:, 0] > 0.05, 0])) if (b[:, 0] > 0.05).any() else 0.3, 1e-3)),
                                 between_per_bp=float(b_sd / max(bp_hi, 1e-3)))
            out[key][base] = P
            if verbose:
                print(key, base, "a bias %.5f sd %.5f" % (P["a_bias"], P["a_sd"]),
                      {k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in P["phase"].items()},
                      P.get("cryst"), P.get("strain"), P.get("beta"), flush=True)
    return out


def _fit_detect(rows):
    """Logistic detection curve in log10 wt and the log-ratio bias/spread of detected fractions."""
    lw = np.array([r[0] for r in rows])
    y = np.array([1.0 if r[1] else 0.0 for r in rows])
    lr = np.array([r[2] for r in rows if r[1]])
    best = None
    for l50 in np.linspace(-3.5, 0.0, 71):
        for s in (0.05, 0.1, 0.15, 0.2, 0.3, 0.45, 0.7):
            p = 1 / (1 + np.exp(-(lw - l50) / s))
            p = np.clip(p, 1e-6, 1 - 1e-6)
            ll = float(np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))
            if best is None or ll > best[0]:
                best = (ll, l50, s)
    rb = float(np.median(lr)) if len(lr) else 0.0
    rs = float(1.4826 * np.median(np.abs(lr - rb))) if len(lr) > 2 else 0.3
    return dict(l50=float(best[1]), s=float(best[2]), rb=rb, rs=max(rs, 0.02), n=int(len(rows)),
                det=float(y.mean()))


# ------------------------------------------------------------------------------------------------ figures
def gallery(outdir, samples=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from pathlib import Path
    samples = samples or micro.gallery_samples()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    rows = [(c, a, lot, part) for c, d in samples.items() for a, (lot, part) in d.items()]
    fig, axes = plt.subplots(len(rows), 2, figsize=(15, 3.1 * len(rows)), gridspec_kw=dict(width_ratios=[3.2, 1]))
    for i, (camp, alloy, lot, part) in enumerate(rows):
        kind, s = ("part", part)
        rng = np.random.default_rng(100 + i)
        r = (measure_part if kind == "part" else measure_powder)(s, camp, rng, fidelity="full", with_truth=True)
        raw = r["raw"]
        ax = axes[i, 0]
        x, cts, fit = raw["two_theta"], raw["counts"], raw["fit"]
        dw = raw["dwell_s"]
        ax.plot(x, cts, color="0.15", lw=0.6, label="counts (full: 0.01 deg, %.2f s/step)" % dw)
        ax.plot(x, fit["model"] * dw, color="#d1495b", lw=0.8, alpha=0.8, label="Rietveld-lite fit")
        ax.plot(x, fit["bg"] * dw, color="#00798c", lw=0.8, ls="--", label="background")
        for nm, comp in fit["comps"].items():
            if nm != "fcc" and comp.max() * dw > 3:
                ax.plot(x, (fit["bg"] + comp) * dw, lw=0.7, label=f"{nm}")
        ax.set_yscale("log")
        ax.set_ylim(max(np.percentile(cts, 1) * 0.5, 1), cts.max() * 2)
        ax.set_xlim(*TTH)
        for (hkl, pos, H, A) in fit["peaks"]:
            ax.annotate("".join(map(str, hkl)), (pos, cts[np.argmin(np.abs(x - pos))] * 1.15), ha="center",
                        fontsize=7, color="0.3")
        ax.set_title(f"{alloy} part ({'LPBF' if camp == 'flaime_al' else 'DED'}), Cu K-alpha, MiniFlex", fontsize=10,
                     loc="left")
        ax.set_xlabel("2theta (deg)")
        ax.set_ylabel("counts")
        ax.legend(fontsize=7, ncol=3, loc="upper right")
        ax2 = axes[i, 1]
        ax2.axis("off")
        tp = raw["true_phases"]
        lines = [f"a_fcc  measured {r['a_fcc_A']:.4f} A" if r["a_fcc_A"] else "a_fcc  -",
                 f"       true     {raw['true_a']:.4f} A",
                 f"displacement {raw['disp_mm'] * 1000:.0f} um, r(MD) true {raw['r_md']:.2f} fit {fit['r_md']:.2f}",
                 f"W-H: size {raw['crystallite_nm'] or float('nan'):.0f} nm, strain {(raw['microstrain'] or 0) * 1e3:.2f}e-3",
                 "", "phase        true wt%   measured"]
        names = sorted(set(list(tp)) | set(k for k in r["phases"] if not k.startswith("FCC")), key=lambda k: -tp.get(k, 0))
        for nm in names[:9]:
            meas = r["phases"].get("FCC-" + micro.base_of(camp) if nm == "fcc" else nm)
            lines.append(f"{nm[:12]:<12} {100 * tp.get(nm, 0):7.2f}   " + (f"{100 * meas:6.2f}" if meas else "  n.d."))
        if camp == "onr_cu":
            lines.append(f"beta' frac  true {s.get('beta_prime', 0):.3f}  XRD {r.get('beta_prime_frac', 0):.3f}")
        ax2.text(0, 1, "\n".join(lines), va="top", family="monospace", fontsize=8)
    fig.suptitle("XRD (simulated MiniFlex patterns and the Rietveld-lite analysis); n.d. = below the 3-sigma detection"
                 " limit", fontsize=11)
    fig.tight_layout()
    fig.savefig(outdir / "xrd.png", dpi=110)
    plt.close(fig)


def thumbnail(path, samples=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from pathlib import Path
    samples = samples or micro.gallery_samples()
    lot, part = samples["flaime_al"]["AlSi10Mg"]
    sim = simulate(part, "flaime_al", np.random.default_rng(3), "lite", "part")
    x, y = sim["x"], sim["counts"]
    fig = plt.figure(figsize=(5.12, 5.12), dpi=100)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0.06, 0.08, 0.88, 0.84])
    ax.patch.set_alpha(0)
    yy = np.sqrt(np.maximum(y - np.percentile(y, 5), 0))
    sel = (x > 25) & (x < 85)
    from matplotlib import patheffects as pe
    halo = [pe.withStroke(linewidth=8, foreground="white", alpha=0.9)]
    ax.fill_between(x[sel], 0, yy[sel], color="#90b4e0", alpha=0.55, lw=0)
    ax.plot(x[sel], yy[sel], color="#1a365d", lw=3.2, path_effects=halo)
    ax.set_ylim(0, yy[sel].max() * 1.08)
    ax.set_xlim(25, 85)
    ax.axis("off")
    ax.text(0.97, 0.93, "XRD", transform=ax.transAxes, ha="right", va="top", fontsize=64, weight="bold",
            color="#1a365d", path_effects=halo)
    fig.savefig(Path(path), transparent=True)
    plt.close(fig)


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    t0 = time.time()
    cal = calibrate(n=n, reps=reps)
    for k, v in cal.items():
        micro.calib_write(k, v)
    print("calibrated in %.0f s" % (time.time() - t0))
