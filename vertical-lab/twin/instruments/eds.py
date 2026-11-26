"""Desktop-SEM EDS (Hitachi TM4000 + a 30 mm2 SDD, 15 kV): the spectrum a lot or a polished part gives, and the
standardless quantification a lab runs on it.

Forward model (what the detector records), per measurement:

* **Generation.** Characteristic ionizations per electron from Bethe's cross-section integrated along the electron's
  slowing down, Q(E) = 6.51e-20 n_s b_s ln(c_s U) / (U E_c^2) cm2, dE/drho s from Bethe with Joy & Luo's low-energy
  J* (Joy & Luo, Scanning 11, 1989), times the fluorescence yield (Krause, J. Phys. Chem. Ref. Data 8, 1979) and the
  line's share of its family, times the backscatter loss R (Myklebust's fit). Bremsstrahlung by Kramers' law,
  N(E) dE = k Z (E0 - E)/E dE (Kramers, Phil. Mag. 46, 1923).
* **Absorption on the way out**: a Packwood-Brown Gaussian phi(rho z) (Packwood & Brown, X-Ray Spectrom. 10, 1981)
  integrated numerically, with the X-ray range of Anderson & Hasler, at a 35 deg take-off angle (assumed); mass
  absorption coefficients from a Z^3.66 E^-2.8 law with K/L/M jump ratios (assumed; within ~10 % of NIST XCOM for
  the metals at 1.5-9 keV: https://physics.nist.gov/PhysRefData/Xcom/html/xcom1.html), and a fixed per-pair
  perturbation (5 % above 2 keV, 12 % below 1 keV) for the tables' own uncertainty, which the quantification does
  not know (assumed). Secondary fluorescence K-K by Reed's formula (Reed, Br. J. Appl. Phys. 16, 1965).
* **Surfaces**: a carbon contamination film and the native oxide (powder: the oxide shell that the lot's oxygen
  implies for its particle size; parts: 3 nm); they emit O and C and absorb soft X-rays. **Powder geometry**: take-off
  angles spread over the particles' curvature and soft X-rays shadowed by neighbours (assumed), so light elements
  read low; the field samples a few hundred particles from the lot's atomizer runs (Dirichlet mixing).
* **Detector**: Moxtek AP3.3-like polymer window on a Si grid (77 % open), 30 nm Si dead layer, 450 um Si
  (assumed); FWHM^2 = noise^2 + 2.355^2 F eps E with F = 0.115 (Fano factor of Si), eps = 3.71 eV, noise set so
  that Mn K-alpha is 129 eV; Si escape peaks (Reed & Ware, J. Phys. E 5, 1972); a 0.5 % incomplete-charge tail;
  pile-up sum peaks (self-convolution, pulse-pair resolution 0.4 us); paralyzable dead time 4 us (real time from live
  time); gain/offset drift; Poisson counts. Line energies: Bearden, Rev. Mod. Phys. 39 (1967) 78 and NIST SRD 128
  (https://physics.nist.gov/PhysRefData/XrayTrans/Html/search.html).

Analysis on that spectrum (what AZtec/Esprit-like software does, simplified): weighted linear least squares of
the whole spectrum against a Kramers background (absorbed and window-corrected, three terms), one Gaussian family per
element and shell (fixed in-family weights, escape peaks included), a pile-up term; net intensities; standardless
k-ratios against computed pure-element intensities; a ZAF-lite (Philibert-Duncumb-Heinrich absorption, the same
Z and F) iterated to convergence; metals normalized to 100 %; 3-sigma detection limits from the fit covariance.
The overlaps that matter are real ones: Er M / Al K, Mg K / Al K, Mn K-beta / Fe K-alpha, Cr K-beta / Mn K-alpha,
Ni K-beta / Cu K-alpha, Cu K-beta / Zn K-alpha, Ti K-beta / Ce L-alpha, Sc K-beta / Ti K-alpha, Zr L / Nb L, O K /
Cr L. Li is invisible (window and yield). Because the forward model and the quantification differ the way the real
specimen and the software's model differ, the biases come out of the chain rather than being imposed.

Fidelity: 'full' 10 eV channels (2000), 'lite' 20 eV (1000), same counting statistics; 'fast' draws errors from
distributions fitted to the lite chain (``calibrate``; parameters in calib_micro.json under 'eds').
"""
from __future__ import annotations

import math
import zlib

import numpy as np

from twin.instruments import micro

SPEC = dict(station="byu_sem", hours=0.15, consumables={"carbon_tape": 1, "stub": 1},
            note="area spectrum, 60 s live at 15 kV, about 1 nA; a polished part needs the 'prep' station first")

E0 = 15.0                       # keV
TOA_DEG = 35.0                  # take-off angle (assumed)
LIVE_S = 60.0                   # live time (assumed)
BEAM_NA = 1.0                   # beam current (assumed)
OMEGA_SR = 0.03                 # 30 mm2 SDD at ~32 mm (assumed)
TAU_DEAD = 4e-6                 # s, paralyzable (assumed)
TAU_PPR = 0.4e-6                # s, pulse-pair resolution (assumed)
FANO, EPS_PAIR = 0.115, 3.71e-3
NOISE2 = 0.129 ** 2 - 2.3548 ** 2 * FANO * EPS_PAIR * 5.8987
ESC_E = 1.7398                  # Si K-alpha escape
KRAMERS_K = 2.0e-6 / (4 * math.pi)  # Kramers' constant, photons per electron per keV per sr per unit Z (Lifshin's
                                    # ~2e-9 per eV into 4 pi; Goldstein et al. 2018, ch. 4)
AL_SPACE = micro.AL_ELEMENTS
CU_SPACE = micro.CU_ELEMENTS

# characteristic lines: element -> [(family, line, E keV, weight within family)]; Bearden 1967 / NIST SRD 128.
# In-family weights: K-beta/K-alpha from Scofield's ratios (about 0.13 for Sc-Zn, smaller for light elements);
# L and M family weights approximate (assumed).
LINES = {
    "Li": [("K", "Ka", 0.0543, 1.0)],
    "C": [("K", "Ka", 0.2770, 1.0)],
    "O": [("K", "Ka", 0.5249, 1.0)],
    "Mg": [("K", "Ka", 1.2536, 1.0), ("K", "Kb", 1.3022, 0.013)],
    "Al": [("K", "Ka", 1.4865, 1.0), ("K", "Kb", 1.5575, 0.026)],
    "Si": [("K", "Ka", 1.7398, 1.0), ("K", "Kb", 1.8359, 0.035)],
    "Sc": [("K", "Ka", 4.0906, 1.0), ("K", "Kb", 4.4605, 0.120), ("L", "La", 0.3952, 1.0)],
    "Ti": [("K", "Ka", 4.5108, 1.0), ("K", "Kb", 4.9318, 0.125), ("L", "La", 0.4522, 1.0)],
    "Cr": [("K", "Ka", 5.4147, 1.0), ("K", "Kb", 5.9467, 0.134), ("L", "La", 0.5728, 1.0)],
    "Mn": [("K", "Ka", 5.8987, 1.0), ("K", "Kb", 6.4904, 0.135), ("L", "La", 0.6374, 1.0)],
    "Fe": [("K", "Ka", 6.4038, 1.0), ("K", "Kb", 7.0580, 0.135), ("L", "La", 0.7050, 1.0)],
    "Ni": [("K", "Ka", 7.4782, 1.0), ("K", "Kb", 8.2647, 0.136), ("L", "La", 0.8515, 1.0)],
    "Cu": [("K", "Ka", 8.0478, 1.0), ("K", "Kb", 8.9053, 0.137), ("L", "La", 0.9297, 1.0)],
    "Zn": [("K", "Ka", 8.6389, 1.0), ("K", "Kb", 9.5720, 0.138), ("L", "La", 1.0117, 1.0)],
    "Zr": [("L", "La", 2.0424, 1.0), ("L", "Lb1", 2.1244, 0.55), ("L", "Lb2", 2.2194, 0.10), ("L", "Lg1", 2.3027, 0.04)],
    "Nb": [("L", "La", 2.1659, 1.0), ("L", "Lb1", 2.2574, 0.56), ("L", "Lb2", 2.3670, 0.11), ("L", "Lg1", 2.4618, 0.05)],
    "Sn": [("L", "La", 3.4440, 1.0), ("L", "Lb1", 3.6628, 0.60), ("L", "Lb2", 3.9049, 0.18), ("L", "Lg1", 4.1311, 0.07)],
    "Ce": [("L", "La", 4.8402, 1.0), ("L", "Lb1", 5.2622, 0.62), ("L", "Lb2", 5.6134, 0.20), ("L", "Lg1", 6.0520, 0.08),
           ("M", "Ma", 0.8830, 1.0), ("M", "Mb", 0.9050, 0.55)],
    "Er": [("L", "La", 6.9487, 1.0), ("L", "Lb1", 7.8109, 0.62), ("L", "Lb2", 7.9374, 0.22), ("L", "Lg1", 9.0890, 0.09),
           ("M", "Ma", 1.4060, 1.0), ("M", "Mb", 1.4530, 0.60)],
}
# absorption edges (keV): K, L3, M5 (Bearden & Burr 1967; NIST SRD 128)
EDGES = {
    "Li": dict(K=0.0548), "C": dict(K=0.2838), "O": dict(K=0.5317), "Mg": dict(K=1.3050, L=0.0496),
    "Al": dict(K=1.5596, L=0.0726), "Si": dict(K=1.8389, L=0.0999), "Sc": dict(K=4.4928, L=0.4022),
    "Ti": dict(K=4.9664, L=0.4555), "Cr": dict(K=5.9892, L=0.5745), "Mn": dict(K=6.5390, L=0.6387),
    "Fe": dict(K=7.1120, L=0.7067), "Ni": dict(K=8.3328, L=0.8547), "Cu": dict(K=8.9789, L=0.9311),
    "Zn": dict(K=9.6586, L=1.0197), "Zr": dict(K=17.998, L=2.2223, M=0.1786), "Nb": dict(K=18.986, L=2.3705, M=0.2024),
    "Sn": dict(K=29.200, L=3.9288, M=0.4848), "Ce": dict(K=40.443, L=5.7232, M=0.8838),
    "Er": dict(K=57.486, L=8.3579, M=1.4093),
}
# fluorescence yields (Krause 1979): K shell; L3 shell for Zr, Nb, Sn, Ce, Er; M shell (assumed, ~1e-2); L of the 3d
# metals (Krause: about 0.002-0.01)
OMEGA = {
    ("C", "K"): 0.0028, ("O", "K"): 0.0083, ("Li", "K"): 0.00029, ("Mg", "K"): 0.030, ("Al", "K"): 0.039,
    ("Si", "K"): 0.050, ("Sc", "K"): 0.190, ("Ti", "K"): 0.219, ("Cr", "K"): 0.275, ("Mn", "K"): 0.303,
    ("Fe", "K"): 0.347, ("Ni", "K"): 0.414, ("Cu", "K"): 0.445, ("Zn", "K"): 0.479,
    ("Zr", "L"): 0.036, ("Nb", "L"): 0.042, ("Sn", "L"): 0.083, ("Ce", "L"): 0.118, ("Er", "L"): 0.178,
    ("Ce", "M"): 0.010, ("Er", "M"): 0.015,
    ("Sc", "L"): 0.0015, ("Ti", "L"): 0.0020, ("Cr", "L"): 0.0030, ("Mn", "L"): 0.0035, ("Fe", "L"): 0.0040,
    ("Ni", "L"): 0.0055, ("Cu", "L"): 0.0060, ("Zn", "L"): 0.0070,
}
SHELL = dict(K=(2, 0.35, 1.0), L=(4, 0.25, 1.0), M=(6, 0.25, 1.0))     # n_s, b_s, c_s (assumed, Powell-like)
PRINCIPAL = {e: ("L" if e in ("Zr", "Nb", "Sn", "Ce", "Er") else "K") for e in LINES}
# overlap partners used as fast-mode features (the spectral overlaps above)
OVERLAP = {"Al": ("Er", "Mg"), "Mg": ("Al",), "Mn": ("Cr", "Fe"), "Fe": ("Mn",), "Cr": ("Mn",), "Cu": ("Ni", "Zn"),
           "Ni": ("Cu",), "Zn": ("Cu",), "Ti": ("Sc", "Ce"), "Ce": ("Ti",), "Sc": ("Ti",), "Zr": ("Nb",),
           "Nb": ("Zr",), "Er": ("Al", "Fe")}


# ------------------------------------------------------------------------------------------------ physics helpers
def r_jump(el, shell="K"):
    z = micro.Z(el)
    if shell == "K":
        return 125.0 / z + 3.5          # K jump ratio (approximation after Poehn et al. 1985; assumed)
    if shell == "L":
        return 3.0
    return 2.0


def mac(E, el):
    """Mass absorption coefficient of element ``el`` at photon energy E (keV), cm2/g; vectorized in E. A
    Z^3.66 / A E^-2.8 law with jump ratios at the K, L3 and M5 edges (assumed; see the module docstring)."""
    E = np.asarray(E, float)
    z, a = micro.Z(el), micro.M(el)
    mu = 38.5 * z ** 3.66 / a * np.power(np.maximum(E, 0.02), -2.8)
    ed = EDGES.get(el, {})
    for sh in ("K", "L", "M"):
        if sh in ed:
            mu = np.where(E < ed[sh], mu / r_jump(el, sh), mu)
    return mu


def mac_mix(E, wf: dict):
    return sum(w * mac(E, e) for e, w in wf.items() if w > 0)


def fwhm(E):
    return np.sqrt(NOISE2 + 2.3548 ** 2 * FANO * EPS_PAIR * np.maximum(E, 0.0))


def det_eff(E):
    """Window (polymer ~300 nm, Al 40 nm, Si grid 77 % open), 30 nm Si dead layer, 450 um Si (assumed)."""
    E = np.asarray(E, float)
    t_poly = np.exp(-(0.75 * mac(E, "C") + 0.25 * mac(E, "O")) * 1.42 * 300e-7)
    t_al = np.exp(-mac(E, "Al") * 2.70 * 40e-7)
    t_dead = np.exp(-mac(E, "Si") * 2.33 * 30e-7)
    absorb = 1.0 - np.exp(-mac(E, "Si") * 2.33 * 0.045)
    grid = 0.77 + 0.23 * np.exp(-mac(E, "Si") * 2.33 * 0.038)
    return t_poly * t_al * t_dead * absorb * grid


def escape_frac(E):
    """Si K escape probability (Reed & Ware 1972)."""
    E = np.asarray(E, float)
    musi = mac(ESC_E, "Si")
    mu = mac(E, "Si")
    r = r_jump("Si")
    f = 0.5 * OMEGA[("Si", "K")] * (1 - 1 / r) * (1 - musi / mu * np.log1p(mu / musi))
    return np.where(E > EDGES["Si"]["K"], np.clip(f, 0, 0.05), 0.0)


def _J(z):
    return (9.76 * z + 58.5 * z ** -0.19) * 1e-3     # keV, Berger-Seltzer mean ionization potential


_UG = np.linspace(0.0, 1.0, 24)


def gen_integral(Ec, n_s, b_s, c_s, wf: dict, idx=None):
    """Ionizations per electron per (atom/g): integral of Q/S from Ec to E0 (Bethe Q, Bethe-Joy-Luo S); arrays of
    lines (Ec etc. arrays) for one matrix. With ``idx`` (catalogue line indices) the per-line grids and the
    elements' stopping logarithms come from a table built once."""
    if idx is not None:
        _gen_table()
        els = [e for e, w in wf.items() if w > 0]
        cols = np.array([_GT["el"].index(e) for e in els])
        wza = np.array([wf[e] * micro.Z(e) / micro.M(e) for e in els])
        S = 78500.0 * np.maximum(np.einsum("j,ijk->ik", wza, _GT["logJ"][idx][:, cols, :]), 1e-6) / _GT["E"][idx]
        return np.trapezoid(_GT["QE"][idx] / S, _GT["lnE"][idx], axis=1)
    Ec = np.asarray(Ec, float)[:, None]
    lnU0 = np.log(E0 / Ec)
    E = Ec * np.exp(lnU0 * (1e-3 + (1 - 1e-3) * _UG[None, :]))          # log grid from ~Ec to E0
    U = E / Ec
    Q = 6.51e-20 * np.asarray(n_s)[:, None] * np.asarray(b_s)[:, None] * np.log(np.asarray(c_s)[:, None] * U) \
        / (U * Ec ** 2)
    S = 0.0
    for el, w in wf.items():
        if w <= 0:
            continue
        z, a = micro.Z(el), micro.M(el)
        J = _J(z)
        k = 0.731 + 0.0688 * math.log10(z)
        Js = J / (1 + k * J / E)
        S = S + w * z / a * np.log(1.166 * E / Js)
    S = 78500.0 * np.maximum(S, 1e-6) / E
    integ = Q / S * E                                                  # dE = E dlnE
    return np.trapezoid(integ, lnU0 * _UG[None, :], axis=1)


_GT = {}


def _gen_table():
    if _GT:
        return
    Ec = CAT_EC[:, None]
    lnU0 = np.log(E0 / Ec)
    E = Ec * np.exp(lnU0 * (1e-3 + (1 - 1e-3) * _UG[None, :]))
    U = E / Ec
    Q = 6.51e-20 * CAT_SH[:, 0:1] * CAT_SH[:, 1:2] * np.log(CAT_SH[:, 2:3] * U) / (U * Ec ** 2)
    els = list(micro.ATOM)
    logJ = np.zeros((len(CAT), len(els), len(_UG)))
    for j, el in enumerate(els):
        z = micro.Z(el)
        J = _J(z)
        k = 0.731 + 0.0688 * math.log10(z)
        logJ[:, j, :] = np.log(1.166 * E / (J / (1 + k * J / E)))
    _GT.update(el=els, logJ=logJ, E=E, QE=Q * E, lnE=lnU0 * _UG[None, :])


def backscatter_R(zbar, U):
    """Backscatter loss factor (Myklebust 1984 fit)."""
    U = np.asarray(U, float)
    return np.clip(1 - 0.0081517 * zbar + 3.613279e-5 * zbar ** 2 + 0.009583 * zbar * np.exp(-U) + 0.001141 * E0,
                   0.5, 1.0)


def eta_bse(zbar):
    return -0.0254 + 0.016 * zbar - 1.86e-4 * zbar ** 2 + 8.3e-7 * zbar ** 3


_DEPTH = np.linspace(0.0, 1.6, 36)


def f_chi_phirhoz(chi, Ec, wf, rho):
    """Packwood-Brown Gaussian phi(rho z), integrated numerically (forward model)."""
    chi = np.asarray(chi, float)
    Ec = np.asarray(Ec, float)
    zbar = sum(w * micro.Z(e) for e, w in wf.items())
    U = E0 / Ec
    rR = 0.064e-4 * (E0 ** 1.68 - Ec ** 1.68)                         # g/cm2, Anderson-Hasler
    alpha = 2.2 / rR
    eta = eta_bse(zbar)
    phi0 = 1 + 2.8 * (1 - 0.9 / U) * eta
    lnU = np.log(U)
    g0 = 5 * math.pi * U / ((U - 1) * lnU) * (lnU - 5 + 5 * U ** -0.2)
    g0 = np.maximum(g0, phi0 + 0.2)
    beta = 0.4 * alpha * zbar ** 0.6
    rz = _DEPTH[None, :] * rR[:, None]
    a2 = (alpha ** 2)[:, None]
    phi = g0[:, None] * np.exp(-a2 * rz ** 2) - (g0 - phi0)[:, None] * np.exp(-a2 * rz ** 2 - beta[:, None] * rz)
    phi = np.maximum(phi, 0.0)
    if chi.ndim == 1:
        num = np.trapezoid(phi * np.exp(-chi[:, None] * rz), rz, axis=1)
        return num / np.maximum(np.trapezoid(phi, rz, axis=1), 1e-30)
    num = np.trapezoid(phi[:, None, :] * np.exp(-chi[:, :, None] * rz[:, None, :]), rz[:, None, :], axis=2)
    return num / np.maximum(np.trapezoid(phi, rz, axis=1), 1e-30)[:, None]


def f_chi_pdh(chi, Ec, wf):
    """Philibert-Duncumb-Heinrich absorption factor (the quantification's model)."""
    zbar = sum(w * micro.Z(e) for e, w in wf.items())
    abar = sum(w * micro.M(e) for e, w in wf.items())
    h = 1.2 * abar / zbar ** 2
    sig = 4.5e5 / (E0 ** 1.65 - np.asarray(Ec) ** 1.65)
    x = np.asarray(chi) / sig
    return 1.0 / ((1 + x) * (1 + h / (1 + h) * x))


def _pert(el_line, absorber, E):
    """Fixed relative error of the 'true' MAC table for this emitter line and absorber (assumed)."""
    s = 0.12 if E < 1.0 else (0.08 if E < 2.0 else 0.05)
    u = (zlib.crc32(f"{el_line}|{absorber}".encode()) % 100000) / 100000.0
    from statistics import NormalDist
    return math.exp(s * NormalDist().inv_cdf(min(max(u, 1e-4), 1 - 1e-4)))


# line catalogue as arrays (built once)
def _catalogue():
    rows = []
    for el, ls in LINES.items():
        for fam, ln, E, w in ls:
            ed = EDGES[el].get(fam if fam != "M" else "M")
            if ed is None or ed >= E0:
                continue
            rows.append(dict(el=el, fam=fam, line=ln, E=E, w=w, Ec=ed))
    return rows


CAT = _catalogue()
CAT_E = np.array([r["E"] for r in CAT])
CAT_EC = np.array([r["Ec"] for r in CAT])
CAT_W = np.array([r["w"] for r in CAT])
CAT_OM = np.array([OMEGA.get((r["el"], r["fam"]), 0.0) for r in CAT])
CAT_SH = np.array([SHELL[r["fam"]] for r in CAT])
CAT_EL = [r["el"] for r in CAT]
CAT_FAM = [r["fam"] for r in CAT]
_FAMW = {}
for _r in CAT:
    _FAMW[(_r["el"], _r["fam"])] = _FAMW.get((_r["el"], _r["fam"]), 0.0) + _r["w"]
# share of the family's emission in each line
CAT_P = np.array([r["w"] / _FAMW[(r["el"], r["fam"])] for r in CAT])
CAT_RJK = np.array([r_jump(e) for e in CAT_EL])
CAT_ECK = np.array([EDGES[e].get("K", 99.0) for e in CAT_EL])
CAT_A = np.array([micro.M(e) for e in CAT_EL])
CAT_OMK = np.array([OMEGA.get((e, "K"), 0.0) for e in CAT_EL])
CAT_ISK = np.array([f == "K" for f in CAT_FAM])
_MAC_TAB = {}


def _mac_lines(idx, absorbers, perturb):
    """MAC of each absorber at each catalogue line (n_lines x n_abs), optionally the 'true' perturbed table."""
    key = (tuple(idx), tuple(absorbers), perturb)
    if key in _MAC_TAB:
        return _MAC_TAB[key]
    E = CAT_E[idx]
    M = np.stack([mac(E, a) for a in absorbers], axis=1)
    if perturb:
        P = np.array([[_pert(CAT_EL[i] + CAT[i]["line"], a, CAT_E[i]) for a in absorbers] for i in idx])
        M = M * P
    if len(_MAC_TAB) > 5000:
        _MAC_TAB.clear()
    _MAC_TAB[key] = M
    return M


# ------------------------------------------------------------------------------------------------ forward model
def emitted_lines(wf: dict, rho: float, truth: bool, toa_deg=TOA_DEG, layers=None, toa_spread=0.0, shadow=0.0,
                  fluor=True, principal_only=False):
    """Photons per electron per sr leaving the specimen towards the detector, for every catalogue line of the
    elements present (before the detector). Returns (line indices, intensities)."""
    els = [e for e, w in wf.items() if w > 0]
    idx = [i for i, e in enumerate(CAT_EL) if e in wf and wf[e] > 0
           and (not principal_only or CAT_FAM[i] == PRINCIPAL[e])]
    if not idx:
        return np.array([], int), np.array([])
    idx_a = np.array(idx)
    w_arr = np.array([wf[CAT_EL[i]] for i in idx])
    zbar = sum(wf[e] * micro.Z(e) for e in els)
    Ec = CAT_EC[idx_a]
    sh = CAT_SH[idx_a]
    gen = gen_integral(Ec, sh[:, 0], sh[:, 1], sh[:, 2], wf, idx=idx_a)
    A = np.array([micro.M(CAT_EL[i]) for i in idx])
    R = backscatter_R(zbar, E0 / Ec)
    n_ion = micro.NA * w_arr / A * gen * R
    emit = n_ion * CAT_OM[idx_a] * CAT_P[idx_a] / (4 * math.pi)
    M = _mac_lines(idx, els, truth)
    mu = M @ np.array([wf[e] for e in els])                         # specimen MAC at each line
    if truth:
        if toa_spread > 0:
            # take-off angles over particle curvature: Gauss-Hermite average (assumed spread)
            xs, ws = np.polynomial.hermite_e.hermegauss(5)
            ang = np.clip(toa_deg + toa_spread * xs, 5.0, 85.0)
            chi = mu[:, None] / np.sin(np.radians(ang))[None, :]
            f = f_chi_phirhoz(chi, Ec, wf, rho) @ (ws / ws.sum())
        else:
            f = f_chi_phirhoz(mu / math.sin(math.radians(toa_deg)), Ec, wf, rho)
    else:
        f = f_chi_pdh(mu / math.sin(math.radians(toa_deg)), Ec, wf)
    emit = emit * f
    if fluor:
        emit = emit * (1 + _fluor(idx_a, wf, mu, M, els, toa_deg))
    if truth and shadow > 0:      # neighbours in a powder bed shadow soft X-rays (path ~2 um through edges, assumed)
        emit = emit * (1 - shadow * (1 - np.exp(-mu * rho * 1e-4)))
    if layers:
        att = np.ones_like(emit)
        for lw, lrho_t in layers:                      # (mass fractions, mass thickness g/cm2)
            mul = sum(w * mac(CAT_E[idx_a], e) for e, w in lw.items())
            att *= np.exp(-mul * lrho_t / math.sin(math.radians(toa_deg)))
        emit = emit * att
    return idx_a, emit


def _fluor(idx_a, wf, mu_line, M, els, toa_deg):
    """Reed's K-K secondary fluorescence enhancement of each line (ratio to its primary intensity), vectorized
    over (fluoresced line, exciting line) pairs."""
    n = len(idx_a)
    isK = CAT_ISK[idx_a]
    if isK.sum() < 2:
        return np.zeros(n)
    elA = [CAT_EL[i] for i in idx_a]
    EcK = CAT_ECK[idx_a]
    E = CAT_E[idx_a]
    UA = E0 / EcK
    UB = E0 / CAT_EC[idx_a]
    col = {e: k for k, e in enumerate(els)}
    ci = np.array([col[e] for e in elA])
    mu_ab = M[:, ci].T                                              # [j, ib]: MAC of j's element at line ib
    same = ci[:, None] == ci[None, :]
    ok = isK[:, None] & isK[None, :] & ~same & (E[None, :] > EcK[:, None]) & (UA[:, None] > 1) & (UB[None, :] > 1)
    if not ok.any():
        return np.zeros(n)
    rA = CAT_RJK[idx_a]
    wB = np.array([wf[e] for e in elA])
    omB = CAT_OMK[idx_a]
    AA = CAT_A[idx_a]
    mu_b = mu_line[None, :]
    u = mu_line[:, None] / math.sin(math.radians(toa_deg)) / mu_b
    v = (4.5e5 / (E0 ** 1.65 - CAT_EC[idx_a] ** 1.65))[None, :] / mu_b
    with np.errstate(divide="ignore", invalid="ignore"):
        term = 0.5 * (wB * omB * CAT_P[idx_a])[None, :] * ((rA - 1) / rA)[:, None] * (AA[:, None] / AA[None, :]) \
            * (np.clip(UB[None, :] - 1, 0, None) / np.clip(UA[:, None] - 1, 1e-6, None)) ** 1.67 * mu_ab / mu_b \
            * (np.log1p(u) / u + np.log1p(v) / v)
    return np.where(ok, np.nan_to_num(term), 0.0).sum(1)


def continuum(E, wf, rho, truth, toa_deg=TOA_DEG):
    """Kramers continuum per electron per sr per keV leaving the specimen (absorbed as if generated like a line
    with E_c = E)."""
    E = np.asarray(E, float)
    zbar = sum(w * micro.Z(e) for e, w in wf.items())
    k = KRAMERS_K                                  # photons / (e keV sr) per unit Z
    n = k * zbar * np.clip(E0 - E, 0, None) / np.maximum(E, 0.05)
    mu = mac_mix(E, wf)
    Ec = np.clip(E, 0.05, E0 - 0.05)
    chi = mu / math.sin(math.radians(toa_deg))
    f = f_chi_phirhoz(chi, Ec, wf, rho) if truth else f_chi_pdh(chi, Ec, wf)
    return n * f


def _gauss_cols(E_axis, centers, amps, width):
    """sum_j amps_j * Gaussian(E; centers_j, FWHM) * channel width."""
    dE = E_axis[1] - E_axis[0]
    s = fwhm(centers) / 2.3548
    z = (E_axis[None, :] - centers[:, None]) / s[:, None]
    g = np.exp(-0.5 * z * z) / (s[:, None] * math.sqrt(2 * math.pi)) * dE
    return amps @ g if amps.ndim == 1 else amps @ g


def _profiles(E_axis, centers, sig_cut=5.0):
    dE = E_axis[1] - E_axis[0]
    s = fwhm(centers) / 2.3548
    z = (E_axis[None, :] - centers[:, None]) / s[:, None]
    g = np.where(np.abs(z) < sig_cut, np.exp(-0.5 * z * z), 0.0) / (s[:, None] * math.sqrt(2 * math.pi)) * dE
    return g


def true_composition(sample, campaign, rng, kind):
    """Composition in the analysed volume (mass fractions): lot = run mixture of a few hundred particles plus
    entrained intermetallic; part = the part's."""
    pm = micro.phase_model(sample, campaign, kind)
    base = pm["base"]
    comp = dict(pm["composition"])
    if kind == "powder":
        runs = [r for r in sample.get("runs", []) if not r.get("failed")]
        if len(runs) > 1:
            w = np.array([max(r.get("usable_frac", .9) * r.get("cut_frac", .3), 1e-6) for r in runs])
            w = w / w.sum()
            mix = rng.dirichlet(w * 120.0 + 1e-3)     # ~120 particles' worth of volume in the field (assumed)
            comp = {}
            for wi, r in zip(mix, runs):
                for e, v in r["composition"].items():
                    comp[e] = comp.get(e, 0.0) + wi * v
        for e, x in (pm.get("extra") or {}).items():
            comp[e] = comp.get(e, 0.0) + x * rng.gamma(2.0, 0.5)    # entrained particles: few, clumpy
    tot = sum(v for e, v in comp.items() if e != base)
    comp[base] = max(100.0 - tot, 50.0)
    s = sum(comp.values())
    return {e: v / s for e, v in comp.items() if v > 0}, pm


def simulate(sample, campaign, rng, fidelity="lite"):
    """The recorded spectrum and everything the figure needs (truth side)."""
    kind = micro.kind_of(sample)
    wf, pm = true_composition(sample, campaign, rng, kind)
    base = pm["base"]
    rho = sum(p["vol"] * p["density"] for p in pm["phases"])
    # surface layers: carbon contamination and native oxide (O is part of the measured surface, not the alloy)
    ox_frac = {"Al": {"Al": 0.529, "O": 0.471}, "Cu": {"Cu": 0.888, "O": 0.112}}[base]
    ox_rho = 3.95 if base == "Al" else 6.0
    if kind == "powder":
        d50 = sum(c["w"] * c["d50"] for c in pm["powder"]["components"])
        o_ppm = pm.get("oxygen_ppm") or (700.0 if base == "Al" else 400.0)
        if not np.isfinite(o_ppm):
            o_ppm = 700.0
        w_ox = 0.5 * o_ppm * 1e-6 / ox_frac["O"]          # half of the lot's oxygen in the surface shell (assumed)
        t_ox = float(np.clip(w_ox * rho * d50 * 1e-4 / (6 * ox_rho), 2e-7, 2e-6)) * rng.lognormal(0, 0.15)  # cm
        t_c = 8e-7 * rng.lognormal(0, 0.3)
        toa_spread, shadow = 14.0 * rng.uniform(0.8, 1.2), rng.uniform(0.05, 0.20)
    else:
        t_ox, t_c = 3e-7 * rng.lognormal(0, 0.2), 5e-7 * rng.lognormal(0, 0.3)
        toa_spread, shadow = 0.0, 0.0
    layers = [({"C": 1.0}, 2.0 * t_c), (ox_frac, ox_rho * t_ox)]
    idx, emit = emitted_lines(wf, rho, True, layers=layers, toa_spread=toa_spread, shadow=shadow)
    # emission of the layers themselves (thin films at the surface: phi0 ~ 1 + backscatter)
    zbar = sum(w * micro.Z(e) for e, w in wf.items())
    phi0 = 1 + 2.8 * eta_bse(zbar) * 0.9
    film = []
    for lw, mt in layers:
        for e, w in lw.items():
            if e not in ("O", "C"):
                continue
            i = [k for k, r in enumerate(CAT) if r["el"] == e][0]
            Ec = CAT_EC[i]
            U = E0 / Ec
            Q = 6.51e-20 * 2 * 0.35 * math.log(U) / (U * Ec ** 2)
            film.append((i, micro.NA * w * mt / micro.M(e) * Q * phi0 * OMEGA[(e, "K")] / (4 * math.pi)))
    if film:
        idx = np.concatenate([idx, [f[0] for f in film]])
        emit = np.concatenate([emit, [f[1] for f in film]])
    dE = 0.01 if fidelity == "full" else 0.02
    E_axis = np.arange(dE / 2, 20.0, dE)
    electrons = BEAM_NA * 1e-9 / 1.602e-19 * LIVE_S
    # detector response: drift, efficiency, escape, Gaussian, tail
    off, gain = rng.normal(0, 0.002), rng.normal(0, 4e-4)
    Ec_lines = CAT_E[idx]
    n_det = emit * OMEGA_SR * electrons * det_eff(Ec_lines)
    esc = escape_frac(Ec_lines)
    centers = Ec_lines * (1 + gain) + off
    peaks = _gauss_cols(E_axis, centers, n_det * (1 - esc), None)
    peaks = peaks + _gauss_cols(E_axis, np.maximum(centers - ESC_E, 0.05), n_det * esc, None)
    # incomplete charge collection: a flat shelf below each peak, 0.5 % of its counts (assumed)
    tail = np.zeros_like(E_axis)
    for c, n in zip(centers, n_det * (1 - esc)):
        m = E_axis < c
        if m.any():
            tail[m] += 0.005 * n / m.sum()
    cont = continuum(E_axis, wf, rho, True) * dE * OMEGA_SR * electrons * det_eff(E_axis)
    cont = _smear(E_axis, cont)
    spec = peaks + tail + cont
    R_in = spec.sum() / LIVE_S
    p_pu = 1 - math.exp(-R_in * TAU_PPR)
    pu = _pileup(spec, dE) * p_pu
    spec = spec * (1 - p_pu) + pu
    counts = rng.poisson(np.maximum(spec, 0)).astype(float)
    real_time = LIVE_S / math.exp(-R_in * TAU_DEAD)
    return dict(E=E_axis, counts=counts, expected=spec, wf=wf, base=base, kind=kind, rho=rho, R_in=R_in,
                real_s=real_time, dead_frac=1 - LIVE_S / real_time, pileup_frac=p_pu, drift=(off, gain),
                lines=[(CAT_EL[i], CAT[i]["line"], float(CAT_E[i]), float(n)) for i, n in zip(idx, n_det)],
                layers_nm=(t_ox * 1e7, t_c * 1e7), pm=pm)


def _smear(E_axis, y):
    """Continuum through the detector response (Gaussian, width at mid-spectrum): cheap convolution."""
    dE = E_axis[1] - E_axis[0]
    s = 0.06 / dE
    k = np.arange(-int(4 * s) - 1, int(4 * s) + 2)
    g = np.exp(-0.5 * (k / s) ** 2)
    return np.convolve(y, g / g.sum(), mode="same")


def _pileup(spec, dE):
    """Normalized self-convolution: the energy of two coincident events (channel i + channel j)."""
    n = len(spec)
    p = spec / max(spec.sum(), 1.0)
    L = 1 << int(math.ceil(math.log2(2 * n)))
    f = np.fft.rfft(p, L)
    c = np.fft.irfft(f * f, L)[:n]
    # E_i + E_j with E = (k + 1/2) dE: shift by half a channel ~ one channel
    c = np.concatenate([[0.0], c[:-1]])
    return np.maximum(c, 0.0) * spec.sum()


# ------------------------------------------------------------------------------------------------ analysis
def quantify(E, counts, campaign, live_s=LIVE_S, return_fit=False):
    """Standardless quantification of a spectrum (the analysis a lab runs)."""
    base = micro.base_of(campaign)
    space = AL_SPACE if base == "Al" else CU_SPACE
    cand = [base] + [e for e in space if e != "Li"] + ["O", "C"]
    dE = E[1] - E[0]
    sel = (E > 0.33) & (E < E0 - 0.3)
    Es, ys = E[sel], counts[sel]
    ck = (campaign, len(E), round(float(dE), 6))
    if ck not in _QCACHE:
        _QCACHE[ck] = _columns(Es, cand)
    cols, keys, eff_s, macs = _QCACHE[ck]
    nel = len(cols)
    # first-pass composition for the background's absorption: nominal (alloy base only)
    wf = {base: 0.95, "O": 0.01}
    for _ in range(2):
        bk = []
        brem = np.clip(E0 - Es, 0, None) / Es * eff_s
        mu_s = sum(w * macs[e] for e, w in wf.items() if e in macs)
        fa = f_chi_pdh(mu_s / math.sin(math.radians(TOA_DEG)), np.clip(Es, 0.05, E0 - 0.05), wf)
        for t in (brem, brem * (E0 - Es) / E0, brem * Es / E0, brem * (Es / E0) ** 2, brem * (Es / E0) ** 3,
                  brem / np.maximum(Es, 0.3)):
            bk.append(_smear(Es, t * fa))
        pu = _pileup(np.where(sel, counts, 0.0), dE)[sel]
        A = np.stack(cols + bk + [pu / max(pu.sum(), 1.0)], axis=1)
        w = 1.0 / np.sqrt(np.maximum(ys, 4.0))
        Aw = A * w[:, None]
        # normal equations, column-scaled (LAPACK's lstsq/QR are ~100 ms here under thread contention)
        sc = np.sqrt((Aw * Aw).sum(0)) + 1e-30
        An = Aw / sc
        G = An.T @ An + 1e-10 * np.eye(An.shape[1])
        Ginv = np.linalg.inv(G)
        coef = (Ginv @ (An.T @ (ys * w))) / sc
        res = (ys - A @ coef) * w
        chi2 = float(res @ res) / max(len(ys) - A.shape[1], 1)
        sig = np.sqrt(np.maximum(np.diag(Ginv), 0.0)) / sc * math.sqrt(max(chi2, 1.0))
        # ZAF-lite iteration on the principal families
        I = {k[0]: (coef[j], sig[j]) for j, k in enumerate(keys) if k[1] == PRINCIPAL[k[0]]}
        conc = {e: max(v[0], 0.0) for e, v in I.items() if e != "C"}
        wf = _zaf(conc, I, base, n_iter=2 if _ == 0 else 3)
    return _report(I, wf, base, return_fit, Es, A, coef, bk, cols, keys, sig, nel, chi2)


_QCACHE = {}


def _columns(Es, cand):
    """One column per (element, family) in the catalogue: its lines at fixed in-family weights through the
    detector (efficiency, escape), for a given energy axis."""
    cols, keys = [], []
    for el in cand:
        fams = sorted({CAT_FAM[i] for i, e in enumerate(CAT_EL) if e == el})
        for fam in fams:
            ii = np.array([i for i, (e, f) in enumerate(zip(CAT_EL, CAT_FAM)) if e == el and f == fam])
            Ei = CAT_E[ii]
            amp = CAT_P[ii] * det_eff(Ei)
            esc = escape_frac(Ei)
            g = _profiles(Es, Ei) * (amp * (1 - esc))[:, None]
            g = g.sum(0) + (_profiles(Es, np.maximum(Ei - ESC_E, 0.05)) * (amp * esc)[:, None]).sum(0)
            cols.append(g)
            keys.append((el, fam))
    macs = {e: mac(Es, e) for e in cand}
    return cols, keys, det_eff(Es), macs


def _report(I, wf, base, return_fit, Es, A, coef, bk, cols, keys, sig, nel, chi2):
    out = {}
    lod = {}
    P = _pred(wf, list(I))
    norm = sum(max(I[e][0], 0.0) / P[e] for e in I if e not in ("C", "O")) or 1.0
    for e, (c, s) in I.items():
        if e in ("C", "O", base):
            continue
        cw = 100.0 * max(c, 0.0) / P[e] / norm
        lw = 100.0 * 3.0 * s / P[e] / norm
        lod[e] = float(lw)
        if c > 3.0 * s and cw > 0:
            out[e] = float(cw)
    res = dict(comp=out, lod=lod)
    if return_fit:
        res["fit"] = dict(E=Es, model=A @ coef, background=sum(coef[nel + i] * bk[i] for i in range(len(bk))),
                          components={f"{k[0]} {k[1]}": coef[j] * cols[j] for j, k in enumerate(keys) if coef[j] > 3 * sig[j]},
                          pileup=coef[-1] * A[:, -1], chi2=chi2,
                          O_wt=100.0 * max(I["O"][0], 0) / P["O"] / norm if "O" in I else None)
    return res


def _pred(wf, els):
    """Quantification model's emitted principal-family intensity per unit mass fraction, by element."""
    wfn = {e: max(wf.get(e, 0.0), 1e-6) for e in set(wf) | set(els) if e != "C"}
    idx, emit = emitted_lines(wfn, 3.0, False, principal_only=True)
    tot = {}
    for i, v in zip(idx, emit):
        if CAT_FAM[i] == PRINCIPAL[CAT_EL[i]]:
            tot[CAT_EL[i]] = tot.get(CAT_EL[i], 0.0) + v
    out = {e: max(tot.get(e, 0.0) / wfn[e], 1e-30) for e in els if e != "C"}
    if "C" in els:
        out["C"] = 1.0
    return out


def _zaf(conc, I, base, n_iter=4):
    """Iterate C_i = I_i / P_i(C), normalized over everything but carbon."""
    wf = {e: max(v, 0.0) for e, v in conc.items()}
    s = sum(wf.values()) or 1.0
    wf = {e: v / s for e, v in wf.items()}
    wf.setdefault(base, 0.9)
    for _ in range(n_iter):
        P = _pred(wf, list(wf))
        new = {e: max(I[e][0], 0.0) / P[e] for e in wf if e in I}
        s = sum(new.values()) or 1.0
        wf = {e: v / s for e, v in new.items() if v > 0}
        wf.setdefault(base, 0.5)
    return wf


# ------------------------------------------------------------------------------------------------ fast mode
def fit_near_lod(pts):
    """pts: [(c, lod_med, measured or None)] with 0 < c < 3 lod. Logistic detection curve in q = ln(c/lod),
    P = 1/(1 + exp(-(q - q0)/w)) by grid maximum likelihood, and the measured/true ratio when detected."""
    if len(pts) < 6:
        return None
    q = np.array([math.log(c / l) for c, l, m in pts])
    d = np.array([m is not None for c, l, m in pts], float)
    best = (-1e18, 0.0, 0.3)
    for q0 in np.linspace(-2.0, 1.5, 36):
        for w in (0.05, 0.1, 0.15, 0.2, 0.3, 0.45, 0.6, 0.8):
            P = np.clip(1 / (1 + np.exp(-(q - q0) / w)), 1e-4, 1 - 1e-4)
            ll = float((d * np.log(P) + (1 - d) * np.log(1 - P)).sum())
            if ll > best[0]:
                best = (ll, float(q0), float(w))
    lr = [math.log(m / c) for c, l, m in pts if m is not None]
    return dict(q0=best[1], w=best[2], nl_b=float(np.mean(lr)) if lr else 0.0,
                nl_sd=float(np.std(lr)) if len(lr) > 2 else 0.25, n=len(pts))


def fast_value(c, lod_med, p, rng, x_feats):
    """One fast-mode draw for an element present at c (wt%): near the LOD the calibrated detection curve and the
    conditional ratio; above it the bias/spread regression. None: not detected."""
    nl = p.get("near")
    if nl and c < 3 * lod_med:
        q = math.log(max(c, 1e-6) / lod_med)
        P = 1 / (1 + math.exp(-(q - nl["q0"]) / nl["w"]))
        if rng.random() > P:
            return None
        return c * math.exp(nl["nl_b"] + nl["nl_sd"] * rng.normal())
    b = p.get("b", [0.0] * len(x_feats))
    s = p.get("s", [-3.0] + [0.0] * (len(x_feats) - 1))
    bias = sum(bi * xi for bi, xi in zip(b, x_feats))
    lsd = math.exp(sum(si * xi for si, xi in zip(s, x_feats)))
    m = c * math.exp(bias + lsd * rng.normal())
    if not nl and c < 3 * lod_med:
        m += rng.normal(0, lod_med / 3.0)
        if m < lod_med:
            return None
    return m


def false_positive(p, lod, rng):
    r = p.get("fp_rate", 0.0)
    if r > 0 and rng.random() < r:
        return lod * p.get("fp_val", 1.2) * math.exp(0.15 * rng.normal())
    return None


def _features(el, comp_true, kind, base):
    c = max(comp_true.get(el, 0.0), 1e-4)
    ov = sum(comp_true.get(p, 0.0) for p in OVERLAP.get(el, ())) / c
    return math.log10(c), math.log10(1 + ov), 1.0 if kind == "powder" else 0.0


def matrix_features(comp, base):
    """Two descriptors of the matrix the fast mode's bias depends on (absorption and fluorescence): Al alloys:
    heavy solutes and light solutes (wt%/10); Cu alloys: Ni/30 and Al/9.5."""
    if base == "Al":
        heavy = sum(comp.get(e, 0.0) for e in ("Cu", "Zn", "Fe", "Ni", "Mn", "Cr", "Ce", "Er", "Zr", "Sn"))
        light = sum(comp.get(e, 0.0) for e in ("Si", "Mg", "Li"))
        return heavy / 10.0, light / 10.0
    return comp.get("Ni", 0.0) / 30.0, comp.get("Al", 0.0) / 9.5


def fit_grouped(groups, lam=1e-2):
    """groups: [(features list, [log ratios of the repeats])]. Bias regression on the group means, within-sample
    log-spread regression on the group SDs (what one sample's repeats scatter by)."""
    X = np.array([g[0] for g in groups])
    ym = np.array([np.mean(g[1]) for g in groups])
    L = np.diag([1e-6] + [lam] * (X.shape[1] - 1))
    b = np.linalg.solve(X.T @ X + L, X.T @ ym)
    sd = np.array([np.std(g[1], ddof=1) if len(g[1]) > 1 else np.nan for g in groups])
    ok = np.isfinite(sd)
    ls = np.log(np.maximum(sd[ok], 1e-4))
    Xs = X[ok]
    s = np.linalg.solve(Xs.T @ Xs + L, Xs.T @ ls) if ok.sum() >= X.shape[1] else np.array([-3.0] + [0.0] * (X.shape[1] - 1))
    res = ym - X @ b
    return [float(v) for v in b], [float(v) for v in s], float(np.std(res)), float(np.median(sd[ok])) if ok.any() else 0.0


DEFAULT = dict(eds={})


def _fast(sample, campaign, rng):
    kind = micro.kind_of(sample)
    pm = micro.phase_model(sample, campaign, kind)
    base = pm["base"]
    comp = {e: v for e, v in pm["composition"].items() if e != base and v > 0}
    for e, x in (pm.get("extra") or {}).items():
        comp[e] = comp.get(e, 0.0) + x
    cal = micro.calib("eds").get(campaign, {})
    out, lod = {}, {}
    space = AL_SPACE if base == "Al" else CU_SPACE
    for el in space:
        if el == "Li":
            continue
        p = cal.get(f"{el}|{kind}") or cal.get(el) or {}
        lod_med = p.get("lod_med", 0.08 if el in ("Mg", "Al", "Si") else 0.15)
        l = lod_med * math.exp(rng.normal(0, p.get("lod_sd", 0.15)))
        lod[el] = float(l)
        c = comp.get(el, 0.0)
        if c <= 0:
            v = false_positive(p, l, rng)
            if v is not None:
                out[el] = float(v)
            continue
        x, ov, pw = _features(el, comp, kind, base)
        m1, m2 = matrix_features(comp, base)
        m = fast_value(c, lod_med, p, rng, (1.0, x, ov, m1, m2))
        if m is not None:
            out[el] = float(m)
    return dict(comp=out, lod=lod)


def measure(sample, campaign, rng, fidelity="fast", **kw):
    if fidelity == "fast":
        return _fast(sample, campaign, rng)
    sim = simulate(sample, campaign, rng, fidelity)
    q = quantify(sim["E"], sim["counts"], campaign, return_fit=(fidelity == "full"))
    out = dict(comp=q["comp"], lod=q["lod"])
    if fidelity == "full":
        out["raw"] = dict(E_keV=sim["E"], counts=sim["counts"], fit=q["fit"],
                          lines=sim["lines"], real_s=sim["real_s"], live_s=LIVE_S, dead_frac=sim["dead_frac"],
                          pileup_frac=sim["pileup_frac"], R_in_cps=sim["R_in"])
        if kw.get("with_truth"):                 # the noise-free spectrum and the true composition: figures only
            out["raw"].update(expected=sim["expected"], layers_nm=sim["layers_nm"],
                              true_wt={e: 100 * v for e, v in sim["wf"].items()})
    return out


# ------------------------------------------------------------------------------------------------ calibration
def calibrate(n=36, reps=3, seed=0, verbose=True):
    """Fit the fast-mode error model on the lite chain (per campaign, element and sample kind): bias regressed on
    concentration, overlap load and two matrix descriptors over sample means; within-sample spread on the repeats'
    SDs; a detection curve near the LOD; false-positive rate and size for absent elements."""
    import time
    t0 = time.time()
    rng = np.random.default_rng(seed)
    params = {}
    table = []
    for camp in ("flaime_al", "onr_cu"):
        pairs = micro.random_samples(camp, n, seed=seed + 3) + list(micro.gallery_samples()[camp].values())
        rows = []                     # (el, kind, sample id, feats, logratio or None, lod, c, m)
        sid = 0
        for lot, part in pairs:
            for s in (lot, part):
                sid += 1
                kind = micro.kind_of(s)
                pm = micro.phase_model(s, camp, kind)
                base = pm["base"]
                comp = {e: v for e, v in pm["composition"].items() if e != base and v > 0}
                for e, x_ in (pm.get("extra") or {}).items():
                    comp[e] = comp.get(e, 0.0) + x_
                m1, m2 = matrix_features(comp, base)
                for _ in range(reps):
                    r = measure(s, camp, rng, fidelity="lite")
                    for el, l in r["lod"].items():
                        c = comp.get(el, 0.0)
                        x, ov, pw = _features(el, comp, kind, base)
                        m = r["comp"].get(el)
                        rows.append((el, kind, sid, (1.0, x, ov, m1, m2),
                                     None if (m is None or c <= 0) else math.log(m / c), l, c, m))
        cp = {}
        for el in sorted({r[0] for r in rows}):
            for kind in ("powder", "part"):
                R = [r for r in rows if r[0] == el and r[1] == kind]
                if not R:
                    continue
                lods = np.array([r[5] for r in R])
                ent = dict(lod_med=float(np.median(lods)), lod_sd=float(np.std(np.log(lods))))
                groups = {}
                for r in R:
                    if r[6] > 3 * ent["lod_med"] and r[4] is not None:
                        groups.setdefault(r[2], (r[3], []))[1].append(r[4])
                G = list(groups.values())
                if len(G) >= 6:
                    b, sv, between, within = fit_grouped(G)
                    allr = [v for g in G for v in g[1]]
                    ent.update(b=b, s=sv, n=len(allr), n_samples=len(G), between_sd=between, within_sd=within)
                    table.append((camp, el, kind, len(G), float(np.mean(allr)), between, within, ent["lod_med"]))
                near = fit_near_lod([(r[6], ent["lod_med"], r[7]) for r in R if 0 < r[6] < 3 * ent["lod_med"]])
                if near:
                    ent["near"] = near
                Z0 = [r for r in R if r[6] <= 0]
                fp = [r for r in Z0 if r[7] is not None]
                ent["fp_rate"] = len(fp) / max(len(Z0), 1)
                ent["fp_val"] = float(np.median([r[7] / r[5] for r in fp])) if fp else 1.2
                cp[f"{el}|{kind}"] = ent
        params[camp] = cp
    if verbose:
        print(f"eds calibration: {time.time() - t0:.0f} s")
        print("campaign  el  kind   samples  mean log(meas/true)  between-sample sd  within sd  LOD wt%")
        for row in table:
            print("%-9s %-3s %-6s %3d %+.3f %.3f %.3f %.3f" % row)
    params["_table"] = [list(r) for r in table]
    return params


# ------------------------------------------------------------------------------------------------ figures
def gallery(outdir, samples):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from pathlib import Path
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(14, 9.5))
    gs = fig.add_gridspec(3, 2, height_ratios=[1.2, 1.2, 1.0])
    show = [("flaime_al", "AlSi10Mg"), ("onr_cu", "NAB")]
    for k, (camp, nm) in enumerate(show):
        lot, part = samples[camp][nm]
        r = measure(part, camp, np.random.default_rng(1), fidelity="full", with_truth=True)
        raw = r["raw"]
        ax = fig.add_subplot(gs[k, :])
        E, y = raw["E_keV"], raw["counts"]
        ax.semilogy(E, np.maximum(y, 0.5), color="0.35", lw=0.6, label="counts (60 s live)")
        fit = raw["fit"]
        ax.semilogy(fit["E"], np.maximum(fit["model"], 0.5), color="C3", lw=0.9, label="fit")
        ax.semilogy(fit["E"], np.maximum(fit["background"], 0.5), color="C0", lw=0.9, ls="--", label="Kramers background")
        ax.semilogy(fit["E"], np.maximum(fit["pileup"], 0.5), color="C2", lw=0.8, ls=":", label="pile-up")
        lab = {}
        for el, ln, Eline, n in raw["lines"]:
            if n < 300 or Eline > 14.5:
                continue
            key = (el, ln[:2])
            if key in lab:
                continue
            lab[key] = 1
            iy = np.argmin(abs(E - Eline))
            ax.annotate(f"{el} {ln}", (Eline, max(y[max(iy - 2, 0):iy + 3].max(), 1) * 1.4), fontsize=7, ha="center",
                        rotation=90, va="bottom")
            if Eline > 1.84:
                ax.annotate(f"esc", (Eline - ESC_E, max(y[np.argmin(abs(E - (Eline - ESC_E)))], 1) * 1.3), fontsize=6,
                            color="C1", ha="center", rotation=90)
        ax.set_xlim(0, 15)
        ax.set_ylim(0.5, y.max() * 8)
        ax.set_xlabel("energy (keV)")
        ax.set_ylabel("counts per 10 eV")
        ax.set_title(f"{nm} part, 15 kV: input {raw['R_in_cps'] / 1e3:.1f} kcps, dead time {100 * raw['dead_frac']:.0f} %, "
                     f"pile-up {100 * raw['pileup_frac']:.1f} %; measured " +
                     ", ".join(f"{e} {v:.2f}" for e, v in sorted(r["comp"].items(), key=lambda t: -t[1])[:6]) + " wt%",
                     fontsize=9)
        ax.legend(fontsize=7, loc="upper right")
    ax = fig.add_subplot(gs[2, :])
    names, true, meas, err = [], [], [], []
    rng = np.random.default_rng(5)
    for camp, d in samples.items():
        for nm, (lot, part) in d.items():
            pm = micro.phase_model(part, camp, "part")
            base = pm["base"]
            reps = [measure(part, camp, rng, fidelity="lite") for _ in range(4)]
            for el, v in sorted(pm["composition"].items(), key=lambda t: -t[1]):
                if el == base or v < 0.05 or el == "Li":
                    continue
                ms = [q["comp"].get(el, 0.0) for q in reps]
                names.append(f"{nm}\n{el}")
                true.append(v)
                meas.append(np.mean(ms))
                err.append(np.std(ms))
    x = np.arange(len(names))
    ax.bar(x - 0.2, true, 0.4, label="true (part)", color="0.6")
    ax.bar(x + 0.2, meas, 0.4, yerr=err, label="EDS lite, mean of 4", color="C3")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=7)
    ax.set_ylabel("wt%")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / "eds.png", dpi=130)
    plt.close(fig)


def thumbnail(path, samples):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import patheffects as pe
    halo = [pe.withStroke(linewidth=8, foreground="white", alpha=0.9)]
    lot, part = samples["onr_cu"]["NAB"]
    r = measure(part, "onr_cu", np.random.default_rng(2), fidelity="full")
    E, y = r["raw"]["E_keV"], r["raw"]["counts"]
    k = 6
    n = len(E) // k * k
    E2, y2 = E[:n].reshape(-1, k).mean(1), y[:n].reshape(-1, k).sum(1)
    fig = plt.figure(figsize=(5.12, 5.12), dpi=100)
    ax = fig.add_axes([0.06, 0.08, 0.9, 0.86])
    ax.fill_between(E2, 0, np.sqrt(np.maximum(y2, 0)), color="#9ec5ee", alpha=0.55, lw=0)
    ax.plot(E2, np.sqrt(np.maximum(y2, 0)), color="#1f4e8c", lw=3.2, path_effects=halo)
    ax.set_xlim(0.2, 10.5)
    ax.set_ylim(0, np.sqrt(y2.max()) * 1.05)
    ax.axis("off")
    ax.text(0.97, 0.9, "EDS", transform=ax.transAxes, ha="right", va="top", fontsize=64, color="#1f4e8c", path_effects=halo,
            fontweight="bold")
    fig.savefig(path, transparent=True)
    plt.close(fig)


if __name__ == "__main__":
    micro.calib_write("eds", calibrate())
