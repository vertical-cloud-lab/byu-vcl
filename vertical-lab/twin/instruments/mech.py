"""Shared mechanics for the twin's mechanical instruments: elastic modulus, the Voce constitutive law, texture
anisotropy and the defect-controlled (weakest-link) fracture model. ``tensile.py``, ``pip.py`` and ``hardness.py``
all read the same hidden state through this module, so their readings are correlated the way a real lab's are.

**Elastic modulus.** Hill's average of the Voigt and Reuss bounds over the elements' polycrystalline Young's moduli,
weighted by volume fraction (elemental E and densities: CRC Handbook / Kaye & Laby,
https://www.kayelaby.npl.co.uk/general_physics/2_2/2_2_2.html; Si 162 GPa, Hopcroft et al., J. MEMS 19, 2010,
https://doi.org/10.1109/JMEMS.2009.2039697). Checks: AlSi10Mg 77 GPa (datasheets 70-75), 70-30 Cu-Ni 150 GPa
(C71500 datasheet 152), NAB 115 GPa (C95800: 110-117). Porosity: Mackenzie's dilute spherical-pore result
E = E0 (1 - 1.9 p + 0.9 p^2) (Proc. Phys. Soc. B 63, 1950, https://doi.org/10.1088/0370-1301/63/1/302). Temperature:
-4.8e-4 /K for Al, -3.8e-4 /K for Cu (linear fits to Kaye & Laby's E(T), assumed linear to 250 degC).

**Voce law** (Voce, J. Inst. Met. 74, 1948): true stress against true plastic strain,
sigma(e) = s_y + (s_s - s_y)(1 - exp(-theta0 e / (s_s - s_y))). Three conditions fix it: the 0.2 % offset stress, the
engineering UTS at Considere's point (d sigma / d e = sigma), and the uniform strain there. Two laws per part:

* ``bar_law``: the gauge section's effective law, matched to the truth's ``strength`` (ys_MPa, uts_MPa; the truth's
  porosity and crack knock-downs are already in them); uniform elongation e_u = f_u * el with
  f_u = 0.62 + 0.38 exp(-el / 4) (assumed: about 0.75 of the total for ductile metals, about all of it for brittle
  ones, which fail before or at the neck).
* ``matrix_law``: the sound material between the pores, what an indentation into ~1 mm^3 sees: ys_sound_MPa, with
  the truth's own UTS/YS ratio evaluated at the sound ductility (the truth's porosity and crack knock-downs undone).

**Anisotropy** (assumed, after Tang et al., Materialia 15, 2021, https://doi.org/10.1016/j.mtla.2021.101017: AM
superalloy with columnar <001> grains stiffer and stronger transverse to the build direction than along it). The
truth's strength is taken to be the horizontal (XY) bar's. Columnar share: 1 - ``equiaxed`` for Al (the truth's
nucleant share), 0.7 for DED Cu (assumed). Flow stress along the build direction (Z) is lower by 9 % x columnar
(Taylor factor of a <001> fibre, M = 2.45, against 3.06 random, diluted to 30 %: assumed), elongation in Z lower by
25 % x columnar (inter-layer defects; assumed).

**Fracture.** The weakest-link draw of the largest defect in the gauge volume: each pore population (gas, keyhole,
lack of fusion, cracks) has a volume fraction from the truth's ``pores`` and an assumed lognormal size distribution;
N = f V / <v> defects in the gauge volume, and the largest one has P(d_max <= d) = exp(-N (1 - F(d))) (Poisson
extreme value; Murakami's sqrt(area) parameter, Metal Fatigue, 2002). Its projected area removes a share ``a`` of the
weakest section, and the bar is an imperfect tensile bar (the Marciniak-Kuczynski / Hutchinson-Neale imperfection
argument): the defect section carries the same load on (1 - a) of the area, so it reaches its local fracture strain
e_loc while the bulk has strained only to e_b, where sigma(e_b) exp(-e_b) = (1 - a) sigma(min(e_loc, e_u)) exp(...).
If that load is below the bulk's yield, the bar breaks elastically (crack-dominated parts can fail before 0.2 %
offset). Elongation at fracture (plastic) = exp(e_b) - 1 + (e_loc - e_b) l_neck / L_gauge. e_loc is solved per part
so the mean over specimens equals the truth's ``el_pct`` (stratified quantiles of the extreme-value draw), so the
truth's mean holds while the scatter, and the chance of a premature break, grow with the size and number of defects.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np

from twin import physics as ph

_CALIB = None
CALIB_PATH = Path(__file__).resolve().parent / "calib_mech.json"


def calib(name: str) -> dict:
    """The fast-mode parameters ``calibrate_mech.py`` fitted for instrument ``name`` ({} before calibration)."""
    global _CALIB
    if _CALIB is None:
        try:
            _CALIB = json.loads(CALIB_PATH.read_text())
        except (OSError, ValueError):
            _CALIB = {}
    return _CALIB.get(name, {})


def reload_calib():
    global _CALIB
    _CALIB = None
    _TL_CACHE.clear()


# ---------------------------------------------------------------------------------------------- elastic constants
E_GPA = dict(Al=70.0, Cu=130.0, Ni=200.0, Fe=211.0, Mn=198.0, Cr=279.0, Si=162.0, Nb=105.0, Ti=116.0, Zr=88.0,
             Mg=45.0, Zn=108.0, Sc=74.0, Ce=34.0, Li=4.9, Sn=50.0, Er=70.0)
NU = dict(Al=0.33, Cu=0.34)
DE_DT = dict(Al=-4.8e-4, Cu=-3.8e-4)          # 1/K, fractional change of E with temperature (assumed linear)


def base_of(sample_or_campaign) -> str:
    c = sample_or_campaign if isinstance(sample_or_campaign, str) else sample_or_campaign.get("campaign", "")
    return "Al" if c == "flaime_al" else "Cu"


def modulus_GPa(comp: dict, porosity: float = 0.0, temp_C: float = 25.0, base: str | None = None) -> float:
    """Hill average of Voigt and Reuss over volume fractions, Mackenzie's porosity correction, linear in T."""
    vol = {e: w / ph.RHO[e] for e, w in comp.items() if w > 0 and e in ph.RHO}
    tot = sum(vol.values())
    if tot <= 0:
        return 70.0
    voigt = sum(v / tot * E_GPA.get(e, 100.0) for e, v in vol.items())
    reuss = 1.0 / sum(v / tot / E_GPA.get(e, 100.0) for e, v in vol.items())
    E = 0.5 * (voigt + reuss)
    p = min(max(porosity, 0.0), 0.5)
    E *= 1 - 1.9 * p + 0.9 * p * p
    b = base or max(comp, key=comp.get)
    E *= 1 + DE_DT.get(b, -4e-4) * (temp_C - 25.0)
    return float(E)


def poisson(base: str) -> float:
    return NU.get(base, 0.33)


# ---------------------------------------------------------------------------------------------- the Voce law
def voce(eps, law):
    sy, ss, th = law["s_y"], law["s_s"], law["theta0"]
    d = ss - sy
    return sy + d * (1.0 - np.exp(-th * np.asarray(eps) / d))


def voce_slope(eps, law):
    d = law["s_s"] - law["s_y"]
    return law["theta0"] * np.exp(-law["theta0"] * np.asarray(eps) / d)


def _solve_voce(ys, uts, eu):
    for _ in range(40):
        su = uts * math.exp(eu)                       # true stress at the neck
        if su > ys and ys - su * (1 - eu + 0.002) < 0:
            break
        eu *= 0.85                                    # a Voce law cannot reach this neck: bring it in
        if eu < 0.006:
            eu = 0.006
            break
    su = uts * math.exp(eu)
    a = 0.002 / eu

    def g(x):
        return -su * eu * (x ** a - x) / (x * math.log(x)) - (su - ys)

    lo, hi = 1e-12, 1 - 1e-9
    if g(lo) * g(hi) > 0:                             # degenerate (uts ~ ys): nearly flat law
        d = max(su - ys, 0.5)
        return dict(s_y=ys - 0.1, s_s=ys - 0.1 + d * 1.5, theta0=su * 1.5, eu=eu)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if g(mid) > 0:
            lo = mid
        else:
            hi = mid
    x = 0.5 * (lo + hi)
    D = -su * eu / (x * math.log(x))
    s_s = su + D * x
    return dict(s_y=s_s - D, s_s=s_s, theta0=su / x, eu=eu)


@lru_cache(maxsize=20000)
def _voce_fit(ys, uts, e_u):
    """Voce parameters with sigma(0.002) = ys (true), engineering UTS = uts at Considere's strain ln(1 + e_u). A bar
    too brittle to neck (the knee such a law would need is sharper than a metal's elastic-plastic transition, i.e.
    s_y below 0.6 ys) gets its neck moved out until the law is physical: it breaks before reaching it."""
    ys, uts = float(ys), float(uts)
    eu = math.log1p(max(e_u, 0.006))
    law = _solve_voce(ys, uts, eu)
    for _ in range(25):
        if law["s_y"] >= 0.6 * ys or law["eu"] > 0.08:
            break
        eu = law["eu"] * 1.25
        law = _solve_voce(ys, uts, eu)
    return law


def voce_fit(ys, uts, e_u):
    law = dict(_voce_fit(round(float(ys), 3), round(float(uts), 3), round(float(e_u), 5)))
    return law


def eng_curve(law, eps_p):
    """Engineering stress (MPa) along true plastic strain eps_p (elastic strain neglected in the area change)."""
    return voce(eps_p, law) * np.exp(-np.asarray(eps_p))


def uniform_fraction(el_pct: float) -> float:
    return 0.62 + 0.38 * math.exp(-max(el_pct, 0.0) / 4.0)


def _ratio(campaign: str, el: float) -> float:
    """The truth's UTS/YS ratio at elongation el (truth_al / truth_cu ``strength``)."""
    if campaign == "flaime_al":
        return 1.1 + 0.6 * el / (el + 10.0)
    return 1.3 + 0.9 * el / (el + 20.0)


def _strength(sample: dict, hot: bool):
    st = sample.get("strength_hot") if hot else sample.get("strength")
    if st is None:
        st = sample["strength"]
    return st


def bar_law(sample: dict, hot: bool = False) -> dict:
    st = _strength(sample, hot)
    el = max(st["el_pct"], 0.05)
    law = voce_fit(st["ys_MPa"], st["uts_MPa"], uniform_fraction(el) * el / 100.0)
    law["el_pct"] = el
    return law


def sound_ductility(sample: dict, hot: bool = False) -> float:
    """The truth's elongation with its porosity and crack knock-downs undone (what the matrix could do)."""
    st = _strength(sample, hot)
    al = sample.get("campaign") == "flaime_al"
    cf = min(sample.get("crack_density", 0.0) / (2.0 if al else 1.5), 1.0)
    fac = (1 - 6 * sample.get("porosity", 0.0)) * (1 - 0.9 * cf)
    return float(min(max(st["el_pct"] / max(fac, 0.1), st["el_pct"]), 60.0))


def matrix_law(sample: dict, hot: bool = False) -> dict:
    st = _strength(sample, hot)
    el_s = sound_ductility(sample, hot)
    ys = st["ys_sound_MPa"] if "ys_sound_MPa" in st else st["ys_MPa"]
    if hot and "ys_sound_MPa" not in st:
        ys = st["ys_MPa"] / max((1 - 1.5 * sample.get("porosity", 0.0)), 0.3)
    uts = ys * _ratio(sample.get("campaign", "flaime_al"), el_s)
    law = voce_fit(ys, uts, uniform_fraction(el_s) * el_s / 100.0)
    law["el_pct"] = el_s
    return law


# ---------------------------------------------------------------------------------------------- texture
def anisotropy(sample: dict) -> dict:
    if sample.get("campaign") == "flaime_al":
        col = 1.0 - float(sample.get("equiaxed", 0.0))
    else:
        col = 0.7 if sample.get("mode", "blown_large") != "preplaced" else 0.5
    return dict(columnar=col, r_z=1.0 - 0.09 * col, el_z=1.0 - 0.25 * col)


# ---------------------------------------------------------------------------------------------- defects
# (median equivalent diameter um, log sd, projected-area factor) per pore type, assumed: LPBF Al gas pores 5-50 um,
# keyholes 30-100 um, lack-of-fusion voids irregular and flat (projected area larger than a sphere's of equal
# volume); DED pores larger (mm-scale melt pools). Cracks: hot-crack traces 100-500 um (LPBF 7075, Martin 2017).
PORE_SIZES = {
    "Al": dict(gas=(15.0, 0.45, 1.0), keyhole=(55.0, 0.40, 1.0), lof=(110.0, 0.55, 1.8), crack=(220.0, 0.55, 1.0)),
    "Cu": dict(gas=(30.0, 0.45, 1.0), keyhole=(90.0, 0.40, 1.0), lof=(220.0, 0.55, 1.8), crack=(350.0, 0.55, 1.0)),
}
CRACK_OPENING_UM = 3.0     # mean crack opening, so a crack network's volume share is S_V * opening (assumed)


def defect_populations(sample: dict) -> list:
    """[(name, number density per mm^3, ln-median d (um), log sd, area factor)] from the truth's pore shares."""
    base = base_of(sample)
    sizes = PORE_SIZES[base]
    pores = dict(sample.get("pores") or {})
    if not pores:
        pores = dict(gas=sample.get("porosity", 0.0))
    out = []
    for k in ("gas", "keyhole", "lof"):
        f = float(pores.get(k, 0.0))
        if f <= 0:
            continue
        d50, s, af = sizes[k]
        v_mean = math.pi / 6 * (d50 * 1e-3) ** 3 * math.exp(4.5 * s * s)     # mm^3
        out.append((k, f / v_mean, math.log(d50), s, af))
    cd = float(sample.get("crack_density", 0.0))
    if cd > 1e-4:
        d50, s, af = sizes["crack"]
        sv = 4.0 / math.pi * cd                        # crack area per volume, mm^2/mm^3 (stereology, S_V = 4 L_A / pi)
        a_mean = math.pi / 4 * (d50 * 1e-3) ** 2 * math.exp(2 * s * s)
        out.append(("crack", sv / a_mean, math.log(d50), s, af))
    return out


def largest_defect_share(pops: list, volume_mm3: float, area_mm2: float, u):
    """Projected-area share of the weakest section taken by the largest defect, for uniform draws u (array, one
    per population per specimen: shape (n, len(pops))); 0 where a population has no defect in the volume."""
    from scipy.special import ndtri
    u = np.atleast_2d(u)
    a = np.zeros(u.shape[0])
    dmax = np.zeros(u.shape[0])
    for j, (name, n_v, mu, s, af) in enumerate(pops):
        N = n_v * volume_mm3
        if N <= 0:
            continue
        q = 1.0 + np.log(np.clip(u[:, j], 1e-300, 1.0)) / N          # F(d_max) for this draw
        has = q > 0
        d = np.where(has, np.exp(mu + s * ndtri(np.clip(q, 1e-12, 1 - 1e-12))), 0.0)   # um
        area = af * math.pi / 4 * (d * 1e-3) ** 2 / area_mm2
        if name == "crack":
            area = area * 0.64                        # mean |cos| of a random crack plane against the load (assumed)
            # the fracture links the cracks within a band about one crack size thick around the weakest section:
            # projected share 0.64 S_V d_mean * 0.5 (linking efficiency, assumed), fluctuating with the draw
            sv = n_v * math.pi / 4 * math.exp(2 * mu + 2 * s * s) * 1e-6
            d_mean = math.exp(mu + 0.5 * s * s) * 1e-3
            z = ndtri(np.clip(u[:, j], 1e-9, 1 - 1e-9))
            net = 0.64 * sv * d_mean * 0.5 * np.exp(0.35 * z)
            area = 1 - (1 - np.minimum(area, 0.9)) * (1 - np.minimum(net, 0.9))
        better = area > a
        a = np.where(better, area, a)
        dmax = np.where(better, d, dmax)
    return np.clip(a, 0.0, 0.95), dmax


def _branch(law, n=160):
    e = np.linspace(0.0, law["eu"], n)
    return e, eng_curve(law, e)


def fracture_strain(law: dict, a, eps_loc: float, k_neck: float, E_MPa: float, a_mean: float = 0.0):
    """Plastic engineering elongation at fracture (fraction) and the fracture mode, for defect shares a (array).
    The truth's YS and UTS already carry the mean section loss, so the defect section carries (1 - a) / (1 - a_mean)
    of the bar law's capacity: a typical bar reaches the truth's UTS, a bad draw breaks early."""
    a = np.asarray(a, float)
    eb_grid, sb_grid = _branch(law)
    peak = sb_grid[-1]
    rel = np.minimum((1 - a) / (1 - a_mean), 1.0)    # a stronger section than typical: the neck goes elsewhere
    cap = rel * float(eng_curve(law, min(eps_loc, law["eu"])))         # what the defect section can carry
    elastic = cap < sb_grid[0]
    eb = np.interp(np.minimum(cap, peak), sb_grid, eb_grid)
    eb = np.where(elastic, 0.0, eb)
    e_pl = np.expm1(eb) + np.maximum(eps_loc - eb, 0.0) * k_neck * rel
    e_pl = np.where(elastic, 0.0, e_pl)
    return e_pl, elastic, cap


_EL_CACHE: dict = {}


def eps_loc_for(sample: dict, law: dict, geom: dict, hot: bool = False, el_target: float | None = None,
                K: int = 24):
    """(e_loc, a_mean): the matrix's local fracture strain that makes the mean elongation over specimens equal the
    truth's, and the mean defect share over the stratified draws."""
    st = _strength(sample, hot)
    el = (st["el_pct"] if el_target is None else el_target) / 100.0
    key = (round(law["s_y"], 2), round(law["s_s"], 2), round(law["theta0"], 1), round(el, 6),
           tuple(round(x[1], 6) for x in defect_populations(sample)), geom["V"], geom["A"], geom["k_neck"])
    if key in _EL_CACHE:
        return _EL_CACHE[key]
    pops = defect_populations(sample)
    if pops:
        rr = np.random.default_rng(12345)               # fixed stratified quantiles, not the caller's rng
        u = (np.arange(K)[:, None] + rr.random((K, len(pops)))) / K
        for j in range(1, len(pops)):
            rr.shuffle(u[:, j])
        a, _ = largest_defect_share(pops, geom["V"], geom["A"], u)
    else:
        a = np.zeros(1)
    a_mean = float(np.mean(a))
    E = 1e3 * modulus_GPa(sample["composition"], sample.get("porosity", 0.0))
    lo, hi = 1e-5, 4.0
    for _ in range(50):
        mid = math.sqrt(lo * hi)
        m = float(np.mean(fracture_strain(law, a, mid, geom["k_neck"], E, a_mean)[0]))
        if m < el:
            lo = mid
        else:
            hi = mid
    out = (math.sqrt(lo * hi), a_mean)
    if len(_EL_CACHE) > 50000:
        _EL_CACHE.clear()
    _EL_CACHE[key] = out
    return out


def specimen_fractures(sample: dict, law: dict, geom: dict, rng, n: int, hot: bool = False, el_target=None):
    """n specimens: (plastic elongation at fracture, elastic-break flags, load capacity MPa, defect share, d_max)."""
    pops = defect_populations(sample)
    eps_loc, a_mean = eps_loc_for(sample, law, geom, hot, el_target)
    if pops:
        u = rng.random((n, len(pops)))
        a, dmax = largest_defect_share(pops, geom["V"], geom["A"], u)
    else:
        a, dmax = np.zeros(n), np.zeros(n)
    # specimen-to-specimen variation of the matrix ductility itself (microstructure; 8 %, assumed)
    loc = eps_loc * np.exp(rng.normal(0, 0.08, n))
    E = 1e3 * modulus_GPa(sample["composition"], sample.get("porosity", 0.0))
    out = [fracture_strain(law, a[i:i + 1], loc[i], geom["k_neck"], E, a_mean) for i in range(n)]
    e_pl = np.array([o[0][0] for o in out])
    el_flag = np.array([bool(o[1][0]) for o in out])
    cap = np.array([o[2][0] for o in out])
    return dict(e_pl=e_pl, elastic=el_flag, cap=cap, a=a, dmax_um=dmax, eps_loc=loc, a_mean=a_mean)


_U_STRAT: dict = {}


def defect_stats(sample: dict, geom: dict, K: int = 12) -> tuple:
    """Mean and sd of the largest-defect share over stratified draws (cheap; the fast modes' scatter feature)."""
    pops = defect_populations(sample)
    if not pops:
        return 0.0, 0.0
    key = (K, len(pops))
    if key not in _U_STRAT:
        q = (np.arange(K) + 0.5) / K
        _U_STRAT[key] = np.column_stack([np.roll(q, 5 * j) for j in range(len(pops))])
    a, _ = largest_defect_share(pops, geom["V"], geom["A"], _U_STRAT[key])
    return float(a.mean()), float(a.std())


def hardening(sample: dict) -> float:
    """log(UTS / YS) of the matrix law: the work-hardening capacity the indentation sees."""
    law = matrix_law(sample)
    return float(math.log(max(eng_curve(law, law["eu"]), 1.0) / max(float(voce(0.002, law)), 1.0)))


_TL_CACHE: dict = {}


def two_level(p: dict, x, h: float = 0.2, k: int = 6) -> tuple:
    """(mean, sd) of a log ratio from ``calibrate_mech.fit_two_level`` at features x: the linear mean plus the
    kernel-weighted residuals of the k nearest calibration samples (shrunk toward 0 when none is close)."""
    key = id(p)
    if key not in _TL_CACHE:
        _TL_CACHE[key] = (np.asarray(p["Z"], float), np.asarray(p["eg"], float), np.asarray(p["esw"], float),
                          np.asarray(p["xm"], float), np.asarray(p["xs"], float), np.asarray(p["mu"], float),
                          np.asarray(p["lsw"], float))
    Zg, eg, esw, xm, xs, mu, lsw = _TL_CACHE[key]
    z = (np.asarray(x, float) - xm) / xs
    m = mu[0] + float(mu[1:] @ z)
    ls = lsw[0] + float(lsw[1:] @ z)
    if len(eg):
        d2 = ((Zg - z) ** 2).sum(axis=1) / len(z)
        idx = np.argpartition(d2, min(k, len(d2) - 1))[:k] if len(d2) > k else np.arange(len(d2))
        w = np.exp(-d2[idx] / (2 * h * h))
        sw = float(w.sum())
        shrink = sw / (sw + 0.1)
        if sw > 1e-12:
            m += shrink * float(w @ eg[idx]) / sw
            ls += shrink * float(w @ esw[idx]) / sw
    return m, math.exp(min(ls, 3.0))


def ln_mean_sd(p: dict, x) -> tuple:
    """Mean and sd of a calibrated normal (``calibrate_mech.fit_mean_sd``) at state features x."""
    z = (np.asarray(x, float) - np.asarray(p["xm"])) / np.asarray(p["xs"])
    mu = p["mu"][0] + float(np.dot(p["mu"][1:], z))
    sd = math.exp(min(p["lsd"][0] + float(np.dot(p["lsd"][1:], z)), 3.0))
    return mu, sd


def features(sample: dict) -> dict:
    """State features the fast modes' calibrated biases depend on."""
    pores = sample.get("pores") or {}
    return dict(por=float(sample.get("porosity", 0.0)), lof=float(pores.get("lof", 0.0)),
                gas=float(pores.get("gas", 0.0)), crack=float(sample.get("crack_density", 0.0)),
                col=anisotropy(sample)["columnar"], beta=float(sample.get("beta_prime", 0.0)))
